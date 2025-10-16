"""
Squobert processors package
"""

from .script_processor import ScriptProcessor
from .bot_face_processor import BotFaceProcessor
from .remote_presence_processor import RemotePresenceProcessor
from .local_presence_processor import LocalPresenceProcessor
from .presence_frame import PresenceFrame
from .session_frames import StartSessionFrame, StopSessionFrame

__all__ = [
    "ScriptProcessor",
    "BotFaceProcessor",
    "RemotePresenceProcessor",
    "LocalPresenceProcessor",
    "PresenceFrame",
    "StartSessionFrame",
    "StopSessionFrame",
]
