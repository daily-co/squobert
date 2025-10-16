#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
)
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
from pipecat.services.google.llm import GoogleLLMService

from processors import (
    ScriptProcessor,
    BotFaceProcessor,
    RemotePresenceProcessor,
    LocalPresenceProcessor,
)


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


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info("Starting bot")

    stt = DeepgramSTTService(api_key=os.getenv("DEEPGRAM_API_KEY"))

    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        voice_id="32b3f3c5-7171-46aa-abe7-b598964aa793",
    )

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    llm = GoogleLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        system_instruction=system_instruction,
        tools=tools,
    )
    # script_processor = ScriptProcessor(script)
    # Just make him act like a normal bot for now
    script_processor = ScriptProcessor([])

    messages = [
        {
            "role": "user",
            "content": "Start by greeting the user warmly, introducing yourself, and mentioning the current day. Be friendly and engaging to set a positive tone for the interaction.",
        }
    ]
    context = LLMContext(messages)

    context_aggregator = LLMContextAggregatorPair(context)
    bot_face = BotFaceProcessor()
    remote_presence = RemotePresenceProcessor()
    local_presence = LocalPresenceProcessor(messages=messages)

    pipeline = Pipeline(
        [
            transport.input(),
            # remote_presence,
            local_presence,
            rtvi,
            stt,
            context_aggregator.user(),
            script_processor,
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
        ),
        observers=[RTVIObserver(rtvi)],
    )

    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        logger.info("!!! on client ready")
        await rtvi.set_bot_ready()
        await task.queue_frames(
            [
                RTVIServerMessageFrame(
                    data={
                        "event": "expression_change",
                        "data": {"expression": "resting"},
                    }
                ),
            ]
        )
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("!!! Client connected")
        # TODO-CB: Send camera to transport
        # await maybe_capture_participant_camera(transport, client)
        # Kick off the conversation.
        await rtvi.set_bot_ready()
        await task.queue_frames(
            [
                RTVIServerMessageFrame(
                    data={
                        "event": "expression_change",
                        "data": {"expression": "resting"},
                    }
                ),
            ]
        )
        await task.queue_frames([LLMRunFrame()])
        logger.info("!!! sent starting stuff")

    @transport.event_handler("on_client_disconnected")
    async def on_participant_left(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    # runner = TailRunner(handle_sigint=runner_args.handle_sigint)

    await runner.run(task)


async def maybe_capture_participant_camera(
    transport: BaseTransport, client: any, framerate: int = 0
):
    """Capture participant camera video if transport supports it.

    Args:
        transport: The transport instance.
        client: Transport-specific client object.
        framerate: Video capture framerate. Defaults to 0 (auto).
    """
    try:
        from pipecat.transports.daily.transport import DailyTransport

        if isinstance(transport, DailyTransport):
            await transport.capture_participant_video(
                client["id"], framerate=1, video_source="camera"
            )
            logger.info(f"Capturing camera for participant {client}")
    except ImportError:
        pass


async def bot(runner_args: RunnerArguments):
    """Main bot entry point for the bot starter."""

    transport_params = {
        "daily": lambda: DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            # TODO-CB: Send camera to transport
            video_in_enabled=False,
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
