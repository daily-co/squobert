"""
Face detection module for presence detection service.

This module provides async-friendly face detection using OpenCV's Haar Cascade classifier.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Optional

import cv2


class FaceDetector:
    """
    Async-friendly face detector that continuously monitors a camera feed.
    """

    def __init__(self, camera_index: int = 0, interval: float = 1.0):
        """
        Initialize the face detector.

        Args:
            camera_index: Camera device index (default: 0)
            interval: Interval between detections in seconds (default: 1.0)
        """
        self.camera_index = camera_index
        self.interval = interval

        self._cap: Optional[cv2.VideoCapture] = None
        self._face_cascade: Optional[cv2.CascadeClassifier] = None
        self._running = False
        self._task: Optional[asyncio.Task] = None

        # Current state
        self._present = False
        self._face_count = 0
        self._last_update = None
        self._error = None

    def _detect_faces(self, frame):
        """
        Detect faces in the given frame.

        Args:
            frame: Image frame from webcam

        Returns:
            List of face rectangles (x, y, w, h)
        """
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        return faces

    def _capture_and_detect(self) -> tuple[bool, int, Optional[str]]:
        """
        Capture a frame and detect faces.

        Returns:
            Tuple of (success, face_count, error_message)
        """
        if not self._cap or not self._face_cascade:
            return False, 0, "Detector not initialized"

        ret, frame = self._cap.read()
        if not ret:
            return False, 0, "Failed to capture frame"

        try:
            faces = self._detect_faces(frame)
            return True, len(faces), None
        except Exception as e:
            return False, 0, str(e)

    async def start(self):
        """Start the face detection loop."""
        if self._running:
            return

        # Initialize the webcam
        self._cap = cv2.VideoCapture(self.camera_index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Could not open camera {self.camera_index}")

        # Load the Haar Cascade for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self._face_cascade = cv2.CascadeClassifier(cascade_path)

        if self._face_cascade.empty():
            self._cap.release()
            self._cap = None
            raise RuntimeError("Could not load face detection cascade")

        self._running = True
        self._task = asyncio.create_task(self._detection_loop())

    async def stop(self):
        """Stop the face detection loop and release resources."""
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        if self._cap:
            self._cap.release()
            self._cap = None

        self._face_cascade = None

    async def _detection_loop(self):
        """Main detection loop that runs continuously."""
        loop = asyncio.get_running_loop()

        while self._running:
            start_time = time.time()

            # Run detection in thread pool to avoid blocking
            success, face_count, error = await loop.run_in_executor(
                None, self._capture_and_detect
            )

            # Update state
            if success:
                self._present = face_count > 0
                self._face_count = face_count
                self._error = None
            else:
                self._error = error

            self._last_update = datetime.now(timezone.utc)

            # Sleep for remaining interval time
            elapsed = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

    def get_status(self) -> dict:
        """
        Get current detection status.

        Returns:
            Dictionary with current presence status
        """
        return {
            "present": self._present,
            "face_count": self._face_count,
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "error": self._error,
            "camera_index": self.camera_index,
        }
