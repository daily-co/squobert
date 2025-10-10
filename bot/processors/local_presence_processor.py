#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import asyncio
import time
import cv2
import numpy as np
import copy

from loguru import logger

from pipecat.frames.frames import (
    Frame,
    StartFrame,
    EndFrame,
    CancelFrame,
    LLMMessagesUpdateFrame
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

from .presence_frame import PresenceFrame
from .session_frames import StartSessionFrame, StopSessionFrame


class LocalPresenceProcessor(FrameProcessor):
    """
    Monitors local webcam for face detection.
    Runs its own camera capture loop and emits a PresenceFrame when the face count changes.
    Emits StartSessionFrame after sustained presence (5s) and StopSessionFrame after sustained absence (10s).
    Starts capturing on StartFrame, stops on EndFrame or CancelFrame.
    """

    def __init__(
        self,
        messages,
        camera_index: int = 0,
        check_interval: float = 1.0,
        start_session_delay: float = 5.0,
        stop_session_delay: float = 20.0,
    ):
        """
        Initialize the local presence processor.

        Args:
            camera_index: Camera device index (default: 0)
            check_interval: Time in seconds between face detection checks (default: 1.0)
            start_session_delay: Seconds of sustained presence before starting session (default: 5.0)
            stop_session_delay: Seconds of sustained absence before stopping session (default: 10.0)
        """
        super().__init__()
        # Save messages for when we need to reset the context
        self._messages = copy.deepcopy(messages)
        self._camera_index = camera_index
        self._check_interval = check_interval
        self._start_session_delay = start_session_delay
        self._stop_session_delay = stop_session_delay
        self._last_face_count = 0

        # Session tracking
        self._session_active = False
        self._presence_start_time = None  # When faces were first detected
        self._absence_start_time = None   # When faces were last seen

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

        logger.info(
            f"LocalPresenceProcessor initialized "
            f"(camera: {camera_index}, interval: {check_interval}s, "
            f"start_delay: {start_session_delay}s, stop_delay: {stop_session_delay}s)"
        )

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

                    # Track presence/absence for session management
                    has_faces = face_count > 0

                    if has_faces:
                        # Reset absence timer
                        self._absence_start_time = None

                        # Start tracking presence if not already
                        if self._presence_start_time is None:
                            self._presence_start_time = current_time
                            logger.debug("Started tracking presence")

                        # Check if we should start a session
                        if not self._session_active:
                            presence_duration = current_time - self._presence_start_time
                            if presence_duration >= self._start_session_delay:
                                logger.info(f"Starting session after {presence_duration:.1f}s of presence")
                                await self._start_session()
                    else:
                        # Reset presence timer
                        self._presence_start_time = None

                        # Start tracking absence if session is active
                        if self._session_active:
                            if self._absence_start_time is None:
                                self._absence_start_time = current_time
                                logger.debug("Started tracking absence")

                            # Check if we should stop the session
                            absence_duration = current_time - self._absence_start_time
                            if absence_duration >= self._stop_session_delay:
                                logger.info(f"Stopping session after {absence_duration:.1f}s of absence")
                                self._absence_start_time = None
                                await self._stop_session()
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

        # Reset session state
        self._session_active = False
        self._presence_start_time = None
        self._absence_start_time = None

        logger.info("Camera capture stopped")

    async def _start_session(self):
        self._session_active = True
        await self.push_frame(StartSessionFrame())

    async def _stop_session(self):
        self._session_active = False
        await self.push_frame(StopSessionFrame())
        await self.push_frame(LLMMessagesUpdateFrame(messages=self._messages))

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

        # Always push system frames
        if isinstance(frame, SystemFrame):
            await self.push_frame(frame, direction)

        else:
            # Only push other frames if we're in an active session
            if self._session_active:
                await self.push_frame(frame, direction)

    async def cleanup(self):
        """Cleanup method called when processor is being destroyed."""
        await self._stop_capture()
        await super().cleanup()
