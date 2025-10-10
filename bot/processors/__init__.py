"""
Squobert processors package
"""

from .script_processor import ScriptProcessor
from .bot_face_processor import BotFaceProcessor
from .presence_processor import PresenceProcessor
from .presence_frame import PresenceFrame

__all__ = ["ScriptProcessor", "BotFaceProcessor", "PresenceProcessor", "PresenceFrame"]
