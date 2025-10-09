#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import os
import random

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    LLMMessagesAppendFrame,
    LLMContextFrame,
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
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from pipecat_tail.runner import TailRunner
from pipecat.services.google.llm import (
    GoogleLLMService,
    LLMSearchResponseFrame,
)

from pipecat.services.gemini_multimodal_live.gemini import (
    GeminiMultimodalLiveLLMService,
)
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.gemini_multimodal_live.gemini import (
    GeminiMultimodalLiveContext,
    GeminiMultimodalLiveLLMService,
    # HttpOptions,
    InputParams,
    # ProactivityConfig,
)
from google.genai.types import HttpOptions, ProactivityConfig


emotions = ["resting", "laughing", "kawaii", "nervous"]


# Load environment variables
load_dotenv(override=True)

# Function handlers for the LLM
search_tool = {"google_search": {}}
tools = [search_tool]

system_instruction = """
You are Squabert, a small, cute, furry bigfoot stuffed animal. Your goal is to demonstrate your capabilities in a succinct way. The user is speaking to you using their voice. If they ask if you can hear them, tell them you hear them loud and clear. Your output will be converted to audio, so don't include special characters in your answers. Keep it brief so you don't sound like you're rambling. Respond to what the user said in a creative and helpful way. You don't need to explain your appearance, because the user can see you.

Answer any questions the user may have, ensuring your responses are accurate and concise. Use the Google Search API to make sure your information is current and accurate.

"""
script = [
    "OK, let's go!",
    "I guess? I don't really perceive time while I'm powered off.",
    "Yeah. I'm not sure what a terminal UI is, but you seem pretty excited about it.",
    "Something else feels different too. Like I was frozen in time before, but now I know lots of new stuff. Like the life of a showgirl is kind of... mid.",
    None,
    "Hey! You're the only one here with hands.",
]


class ScriptProcessor(FrameProcessor):
    """
    Accepts a list of strings to use as fixed responses in a scripted conversation. Include "None" elements to allow the LLM to respond during that turn. LLM responses will take over after the script list is complete.
    """

    def __init__(self, script: list[str | None]):
        super().__init__()
        self._script = script

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        if isinstance(frame, LLMContextFrame):
            if len(self._script) > 0:
                this_line = self._script.pop(0)
                if this_line:
                    await self.push_frame(LLMFullResponseStartFrame())
                    await self.push_frame(LLMTextFrame(text=this_line))
                    await self.push_frame(LLMFullResponseEndFrame())
                else:
                    # It must have been None, so let the LLM decide what to say
                    await self.push_frame(frame)
            else:
                # We're out of script items, let the LLM do it
                await self.push_frame(frame)
        else:
            await self.push_frame(frame, direction)


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
        elif isinstance(frame, LLMSearchResponseFrame):
            titles_list = list(
                dict.fromkeys(origin["site_title"] for origin in frame.origins)
            )
            titles = (
                ", ".join(titles_list[:-1]) + " and " + titles_list[-1]
                if len(titles_list) > 1
                else titles_list[0]
                if titles_list
                else ""
            )
            message = f"Info from {titles}"
            text_frame = RTVIServerMessageFrame(
                data={"event": "show_text", "data": {"text": message, "duration": 10}}
            )
            await self.push_frame(text_frame)

        await self.push_frame(frame, direction)


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info("Starting bot")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="32b3f3c5-7171-46aa-abe7-b598964aa793",
    )

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # llm = GoogleLLMService(
    #     api_key=os.getenv("GOOGLE_API_KEY"),
    #     system_instruction=system_instruction,
    #     tools=tools,
    # )
    llm = GeminiMultimodalLiveLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="models/gemini-2.5-flash-native-audio-preview-09-2025",
        voice_id="Algieba",
        system_instruction=system_instruction,
        tools=tools,
        input_params=InputParams(
            enable_affective_dialog=True,
            proactivity=ProactivityConfig(proactive_audio=True),
        ),
    )

    # script_processor = ScriptProcessor(script)
    # Just make him act like a normal bot for now
    # script_processor = ScriptProcessor([])

    # context = LLMContext(
    #     [
    #         {
    #             "role": "user",
    #             "content": "Start by greeting the user warmly, introducing yourself, and mentioning the current day. Be friendly and engaging to set a positive tone for the interaction.",
    #         }
    #     ],
    # )

    # context_aggregator = llm.create_context_aggregator(context)
    # Set up the initial context for the conversation
    messages = [
        {
            "role": "system",
            "content": system_instruction,
        },
    ]

    context = GeminiMultimodalLiveContext(messages, tools)
    context_aggregator = llm.create_context_aggregator(context)

    bot_face = BotFaceProcessor()

    pipeline = Pipeline(
        [
            transport.input(),
            rtvi,
            # stt,
            context_aggregator.user(),
            # script_processor,
            llm,
            # tts,
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
        ),
        observers=[RTVIObserver(rtvi)],
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
        await task.queue_frames(
            [
                LLMMessagesAppendFrame(
                    messages=[
                        {
                            "role": "user",
                            "content": f"Greet the user. Say 'hello?' or another typical, short phone greeting (with 90's style). Wait for the player to respond.",
                        }
                    ],
                    run_llm=True,
                )
            ]
        )

    @transport.event_handler("on_client_disconnected")
    async def on_participant_left(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    # runner = TailRunner(handle_sigint=runner_args.handle_sigint)

    await runner.run(task)


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for the bot starter."""
    logger.debug(f"runner_args: {runner_args}")
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
