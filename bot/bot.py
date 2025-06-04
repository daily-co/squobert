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
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    LLMMessagesFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi import (
    RTVIConfig,
    RTVIObserver,
    RTVIProcessor,
    RTVIServerMessageFrame,
)
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecatcloud.agent import DailySessionArguments

emotions = ["resting", "laughing", "kawaii", "nervous"]

# Check if we're in local development mode
LOCAL_RUN = os.getenv("LOCAL_RUN")
if LOCAL_RUN:
    import asyncio
    import webbrowser

    try:
        from local_runner import configure
    except ImportError:
        logger.error(
            "Could not import local_runner module. Local development mode may not work."
        )

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


async def main(room_url: str, token: str):
    """Main pipeline setup and execution function.

    Args:
        room_url: The Daily room URL
        token: The Daily room token
    """
    logger.debug("Starting bot in room: {}", room_url)

    transport = DailyTransport(
        room_url,
        token,
        "bot",
        DailyParams(
            audio_out_enabled=True,
            transcription_enabled=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="32b3f3c5-7171-46aa-abe7-b598964aa793",
    )

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")

    messages = [
        {
            "role": "system",
            "content": "You are Squabert, a small, cute, furry bigfoot stuffed animal. Your goal is to demonstrate your capabilities in a succinct way. Your output will be converted to audio so don't include special characters in your answers. Respond to what the user said in a creative and helpful way. You don't need to explain your appearance, because the user can see you.",
        },
    ]

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)
    bot_face = BotFaceProcessor()

    pipeline = Pipeline(
        [
            transport.input(),
            rtvi,
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

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        logger.info("First participant joined: {}", participant["id"])
        await transport.capture_participant_transcription(participant["id"])
        # Kick off the conversation.
        await task.queue_frames(
            [
                context_aggregator.user().get_context_frame(),
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
        await task.queue_frames([LLMMessagesFrame(messages)])

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        logger.info("Participant left: {}", participant)
        await task.cancel()

    runner = PipelineRunner()

    await runner.run(task)


async def bot(args: DailySessionArguments):
    """Main bot entry point compatible with the FastAPI route handler.

    Args:
        room_url: The Daily room URL
        token: The Daily room token
        body: The configuration object from the request body
        session_id: The session ID for logging
    """
    logger.info(f"Bot process initialized {args.room_url} {args.token}")

    try:
        await main(args.room_url, args.token)
        logger.info("Bot process completed")
    except Exception as e:
        logger.exception(f"Error in bot process: {str(e)}")
        raise


# Local development functions
async def local_main():
    """Function for local development testing."""
    try:
        async with aiohttp.ClientSession() as session:
            (room_url, token) = await configure(session)
            logger.warning("_")
            logger.warning("_")
            logger.warning(f"Talk to your voice agent here: {room_url}")
            logger.warning("_")
            logger.warning("_")
            webbrowser.open(room_url)
            await main(room_url, token)
    except Exception as e:
        logger.exception(f"Error in local development mode: {e}")


# Local development entry point
if LOCAL_RUN and __name__ == "__main__":
    try:
        asyncio.run(local_main())
    except Exception as e:
        logger.exception(f"Failed to run in local mode: {e}")
