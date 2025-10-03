#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import os
import random

import aiohttp
from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    LLMMessagesFrame,
    LLMRunFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
)
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi import (
    RTVIConfig,
    RTVIObserver,
    RTVIProcessor,
    RTVIServerMessageFrame,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams
from pipecat.transports.services.daily import DailyTransport
from pipecatcloud.agent import DailySessionArguments
from pipecat_tail.runner import TailRunner

emotions = ["resting", "laughing", "kawaii", "nervous"]


# Load environment variables
load_dotenv(override=True)


# TODO: This could probably be an observer?
class BotFaceProcessor(FrameProcessor):
    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, UserStartedSpeakingFrame):
            msg_frame = RTVIServerMessageFrame(data={"event": "user_started_speaking"})
            logger.info("SERVER MESSAGE: User started speaking")
            await self.push_frame(msg_frame)
        elif isinstance(frame, UserStoppedSpeakingFrame):
            msg_frame = RTVIServerMessageFrame(data={"event": "user_stopped_speaking"})
            logger.info("SERVER MESSAGE: User stopped speaking")
            await self.push_frame(msg_frame)
        elif isinstance(frame, BotStartedSpeakingFrame):
            msg_frame = RTVIServerMessageFrame(data={"event": "bot_started_speaking"})
            logger.info("SERVER MESSAGE: Bot started speaking")
            await self.push_frame(msg_frame)
        elif isinstance(frame, BotStoppedSpeakingFrame):
            msg_frame = RTVIServerMessageFrame(data={"event": "bot_stopped_speaking"})
            logger.info("SERVER MESSAGE: Bot stopped speaking")
            await self.push_frame(msg_frame)
            emotion_frame = RTVIServerMessageFrame(
                data={
                    "event": "expression_change",
                    "data": {"expression": random.choice(emotions)},
                }  # random.choice(emotions)
            )
            await self.push_frame(emotion_frame)
            # INFO: The bot also suports hide_text,
            # text_frame = RTVIServerMessageFrame(
            #     data={
            #         "event": "show_text",
            #         "data": {"text": "test text", "duration": 3},
            #     }
            # )
            # await self.push_frame(text_frame)

        await self.push_frame(frame, direction)


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info("Starting bot")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="32b3f3c5-7171-46aa-abe7-b598964aa793",
    )

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")

    messages = [
        {
            "role": "system",
            "content": "You are Squabert, a small, cute, furry bigfoot stuffed animal. Your goal is to demonstrate your capabilities in a succinct way. The user is speaking to you using their voice. If they ask if you can hear them, tell them you hear them loud and clear. Your output will be converted to audio so don't include special characters in your answers. Respond to what the user said in a creative and helpful way. You don't need to explain your appearance, because the user can see you.",
        },
    ]

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)
    bot_face = BotFaceProcessor()

    pipeline = Pipeline(
        [
            transport.input(),
            rtvi,
            stt,
            context_aggregator.user(),
            llm,
            tts,
            bot_face,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
            report_only_initial_ttfb=True,
            observers=[RTVIObserver(rtvi)],
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected")
        # Kick off the conversation.
        await task.queue_frames(
            [
                RTVIServerMessageFrame(data={"event": "client connected"}),
                RTVIServerMessageFrame(
                    data={
                        "event": "expression_change",
                        "data": {"expression": "resting"},
                    }
                ),
            ]
        )
        messages.append(
            {
                "role": "system",
                "content": "Start with a one-sentence introduction, including your name.",
            }
        )
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_participant_left(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    # runner = TailRunner(handle_sigint=runner_args.handle_sigint)

    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for the bot starter."""

    transport_params = {
        "daily": lambda: DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            turn_analyzer=LocalSmartTurnAnalyzerV3(),
        ),
    }

    transport = await create_transport(runner_args, transport_params)

    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
