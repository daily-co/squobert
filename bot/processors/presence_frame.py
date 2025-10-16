#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

from pipecat.frames.frames import Frame
from dataclasses import dataclass


@dataclass
class PresenceFrame(Frame):
    """Frame that indicates the number of faces detected in the video stream."""

    face_count: int = 0

    def __post_init__(self):
        super().__post_init__()
