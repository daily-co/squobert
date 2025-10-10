#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import time
import cv2
import numpy as np

from loguru import logger

from pipecat.frames.frames import (
    Frame,
    StartFrame,
    EndFrame,
    CancelFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from .presence_frame import PresenceFrame


class LocalPresenceProcessor(FrameProcessor):
    """
    Monitors local webcam for face detection.
    Runs its own camera capture loop and emits a PresenceFrame when the face count changes.
    Starts capturing on StartFrame, stops on EndFrame or CancelFrame.
    """

    def __init__(self, camera_index: int = 0, check_interval: float = 1.0):
        """
        Initialize the local presence processor.

        Args:
            camera_index: Camera device index (default: 0)
            check_interval: Time in seconds between face detection checks (default: 1.0)
        """
        super().__init__()
        self._camera_index = camera_index
        self._check_interval = check_interval
        self._last_face_count = 0

        # Camera and task management
        self._capture = None
        self._capture_task = None
        self._running = False

        # Load the Haar Cascade for face detection
        self._face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        if self._face_cascade.empty():
            logger.error("Failed to load face detection cascade")
            raise RuntimeError("Could not load face detection cascade")

        logger.info(f"LocalPresenceProcessor initialized (camera: {camera_index}, interval: {check_interval}s)")

    def _detect_faces(self, frame: np.ndarray) -> int:
        """
        Detect faces in the given image frame.

        Args:
            frame: OpenCV image frame (numpy array)

        Returns:
            Number of faces detected
        """
        try:
            if frame is None:
                return 0

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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

    async def _camera_capture_loop(self):
        """
        Background task that continuously captures frames from the camera
        and performs face detection at regular intervals.
        """
        logger.info("Starting camera capture loop")

        # Initialize the webcam
        self._capture = cv2.VideoCapture(self._camera_index)

        if not self._capture.isOpened():
            logger.error(f"Failed to open camera {self._camera_index}")
            return

        last_check_time = 0

        try:
            while self._running:
                # Read frame from webcam
                ret, frame = self._capture.read()

                if not ret:
                    logger.warning("Failed to capture frame from camera")
                    await asyncio.sleep(0.1)
                    continue

                current_time = time.time()

                # Check if it's time to process
                if current_time - last_check_time >= self._check_interval:
                    last_check_time = current_time

                    # Detect faces
                    face_count = self._detect_faces(frame)

                    # If face count changed, emit a PresenceFrame
                    if face_count != self._last_face_count:
                        logger.info(f"Local face count changed: {self._last_face_count} -> {face_count}")
                        self._last_face_count = face_count
                        presence_frame = PresenceFrame(face_count=face_count)
                        await self.push_frame(presence_frame)

                # Small sleep to prevent CPU spinning
                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            logger.info("Camera capture loop cancelled")
        except Exception as e:
            logger.error(f"Error in camera capture loop: {e}", exc_info=True)
        finally:
            if self._capture:
                self._capture.release()
                self._capture = None
            logger.info("Camera capture loop stopped")

    async def _start_capture(self):
        """Start the camera capture task."""
        if self._running:
            logger.warning("Camera capture already running")
            return

        self._running = True
        self._capture_task = asyncio.create_task(self._camera_capture_loop())
        logger.info("Camera capture started")

    async def _stop_capture(self):
        """Stop the camera capture task."""
        if not self._running:
            return

        self._running = False

        if self._capture_task:
            self._capture_task.cancel()
            try:
                await self._capture_task
            except asyncio.CancelledError:
                pass
            self._capture_task = None

        if self._capture:
            self._capture.release()
            self._capture = None

        logger.info("Camera capture stopped")

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)

        # Start camera capture on StartFrame
        if isinstance(frame, StartFrame):
            logger.info("Received StartFrame, starting camera capture")
            await self._start_capture()

        # Stop camera capture on EndFrame or CancelFrame
        elif isinstance(frame, (EndFrame, CancelFrame)):
            logger.info(f"Received {frame.__class__.__name__}, stopping camera capture")
            await self._stop_capture()

        # Always push the original frame through
        await self.push_frame(frame, direction)

    async def cleanup(self):
        """Cleanup method called when processor is being destroyed."""
        await self._stop_capture()
        await super().cleanup()
