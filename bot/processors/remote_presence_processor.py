#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import time
import cv2
import numpy as np

from loguru import logger

from pipecat.frames.frames import (
    Frame,
    InputImageRawFrame,
    UserAudioRawFrame
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from .presence_frame import PresenceFrame


class RemotePresenceProcessor(FrameProcessor):
    """
    Monitors InputImageRawFrame objects from remote participants for face detection.
    Checks for faces every second and emits a PresenceFrame when the count changes.
    """

    def __init__(self):
        super().__init__()
        self._last_check_time = 0
        self._check_interval = 1.0  # Check every 1 second
        self._last_face_count = 0

        # Load the Haar Cascade for face detection
        self._face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        if self._face_cascade.empty():
            logger.error("Failed to load face detection cascade")
            raise RuntimeError("Could not load face detection cascade")

        logger.info("RemotePresenceProcessor initialized with face detection")

    def _detect_faces(self, frame: InputImageRawFrame) -> int:
        """
        Detect faces in the given image frame.

        Args:
            frame: InputImageRawFrame containing image data

        Returns:
            Number of faces detected
        """
        try:
            image_bytes = frame.image
            size = frame.size
            format_str = frame.format

            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)

            # Try to decode as encoded image (JPEG, PNG, etc.)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # If decoding failed, assume it's raw pixel data
            if img is None:
                width, height = size

                # Determine the format and reshape accordingly
                # Most common formats: RGB24, BGR24, RGBA, BGRA
                if format_str and 'RGB' in format_str.upper():
                    # RGB format - need to determine if it has alpha channel
                    if 'RGBA' in format_str.upper() or len(image_bytes) == width * height * 4:
                        img = np.frombuffer(image_bytes, dtype=np.uint8).reshape((height, width, 4))
                        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
                    else:
                        img = np.frombuffer(image_bytes, dtype=np.uint8).reshape((height, width, 3))
                        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                else:
                    # Assume BGR format (OpenCV default)
                    bytes_per_pixel = len(image_bytes) // (width * height)
                    if bytes_per_pixel == 4:
                        img = np.frombuffer(image_bytes, dtype=np.uint8).reshape((height, width, 4))
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    else:
                        img = np.frombuffer(image_bytes, dtype=np.uint8).reshape((height, width, 3))

            if img is None:
                logger.warning("Failed to process image")
                return 0

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self._face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            return len(faces)

        except Exception as e:
            logger.error(f"Error detecting faces: {e}", exc_info=True)
            return 0

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        if not isinstance(frame, UserAudioRawFrame):
            logger.debug(f"Got frame: {frame}")

        if isinstance(frame, InputImageRawFrame):
            logger.info(f"Got Input Image Raw Frame: size={frame.size}, format={frame.format}")
            current_time = time.time()

            # Check if enough time has passed since last check
            if current_time - self._last_check_time >= self._check_interval:
                self._last_check_time = current_time

                # Detect faces in the image
                face_count = self._detect_faces(frame)

                # If face count changed, emit a PresenceFrame
                if face_count != self._last_face_count:
                    logger.info(f"Face count changed: {self._last_face_count} -> {face_count}")
                    self._last_face_count = face_count
                    presence_frame = PresenceFrame(face_count=face_count)
                    logger.info(f"Emitting presence frame: {presence_frame}")
                    await self.push_frame(presence_frame)

        else:
            # Put this in an 'else' for now so we eat image frames and don't pass them to the model
            await self.push_frame(frame, direction)
