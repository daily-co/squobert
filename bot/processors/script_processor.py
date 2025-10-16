#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

from pipecat.frames.frames import (
    Frame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    LLMContextFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor


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
