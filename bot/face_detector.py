#!/usr/bin/env python3
"""
Webcam Face Detection Script

Captures images from the webcam periodically and detects faces.
Run with: python face_detector.py [--interval SECONDS]
"""

import cv2
import argparse
import time
import sys
from datetime import datetime


def detect_faces(frame, face_cascade):
    """
    Detect faces in the given frame.

    Args:
        frame: Image frame from webcam
        face_cascade: Haar cascade classifier for face detection

    Returns:
        List of face rectangles (x, y, w, h)
    """
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    return faces


def main():
    parser = argparse.ArgumentParser(description='Detect faces from webcam periodically')
    parser.add_argument(
        '--interval',
        type=float,
        default=1.0,
        help='Interval between captures in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='Camera device index (default: 0)'
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Show the camera feed with face boxes'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Show live webcam view in a debug window'
    )

    args = parser.parse_args()

    # Initialize the webcam
    print(f"Initializing camera {args.camera}...")
    cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        print(f"Error: Could not open camera {args.camera}", file=sys.stderr)
        return 1

    # Load the Haar Cascade for face detection
    # This uses OpenCV's pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    if face_cascade.empty():
        print("Error: Could not load face detection cascade", file=sys.stderr)
        cap.release()
        return 1

    print(f"Face detection started. Checking every {args.interval} seconds.")
    if args.show or args.debug:
        print("Press 'q' to quit the window, or Ctrl+C to stop.")
    else:
        print("Press Ctrl+C to stop.")

    try:
        last_capture_time = 0

        while True:
            current_time = time.time()

            # Read frame from webcam
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to capture frame", file=sys.stderr)
                break

            # Check if it's time to process
            if current_time - last_capture_time >= args.interval:
                last_capture_time = current_time

                # Detect faces
                faces = detect_faces(frame, face_cascade)

                # Print results
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if len(faces) > 0:
                    print(f"[{timestamp}] ✓ Detected {len(faces)} face(s)")
                else:
                    print(f"[{timestamp}] - No faces detected")

                # Draw rectangles around faces if showing
                if args.show:
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Display the frame if requested
            if args.show or args.debug:
                # For debug mode, show raw feed; for show mode, faces are already drawn above
                display_frame = frame.copy()

                # Add debug info overlay if in debug mode
                if args.debug:
                    cv2.putText(
                        display_frame,
                        f"Camera {args.camera} - Press 'q' to quit",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

                window_title = 'Debug View' if args.debug else 'Face Detection'
                cv2.imshow(window_title, display_frame)

                # Break on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopping...")
                    break
            else:
                # Small sleep to prevent CPU spinning
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\nStopping...")

    finally:
        # Clean up
        cap.release()
        if args.show or args.debug:
            cv2.destroyAllWindows()
        print("Camera released.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
