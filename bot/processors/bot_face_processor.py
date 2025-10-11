#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import random

from loguru import logger

from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    Frame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.processors.frameworks.rtvi import RTVIServerMessageFrame
from pipecat.services.google.llm import LLMSearchResponseFrame
from .session_frames import StartSessionFrame, StopSessionFrame


# also "sleeping" but we don't want that one randomly
emotions = ["resting", "laughing", "kawaii", "nervous"]


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
        elif isinstance(frame, StartSessionFrame):
            emotion_frame = RTVIServerMessageFrame(
                data={
                    "event": "expression_change",
                    "data": {"expression": "kawaii"},
                }  # random.choice(emotions)
            )
            await self.push_frame(emotion_frame)
        elif isinstance(frame, StopSessionFrame):
            emotion_frame = RTVIServerMessageFrame(
                data={
                    "event": "expression_change",
                    "data": {"expression": "sleeping"},
                }  # random.choice(emotions)
            )
            await self.push_frame(emotion_frame)
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
