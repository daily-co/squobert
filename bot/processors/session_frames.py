#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

from pipecat.frames.frames import Frame
from dataclasses import dataclass


@dataclass
class StartSessionFrame(Frame):
    """Frame that indicates a session should start due to sustained presence."""

    def __post_init__(self):
        super().__post_init__()


@dataclass
class StopSessionFrame(Frame):
    """Frame that indicates a session should stop due to sustained absence."""

    def __post_init__(self):
        super().__post_init__()
