"""
FastAPI server that provides presence detection over WebSocket.

This service monitors a camera feed for faces and broadcasts presence updates
to connected WebSocket clients.
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from loguru import logger

from detector import FaceDetector

# Configuration from environment variables
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
DETECTION_INTERVAL = float(os.getenv("DETECTION_INTERVAL", "1.0"))
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8765"))

# Global detector instance
detector: FaceDetector = None
connected_clients: Set[WebSocket] = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler for startup and shutdown."""
    global detector

    # Startup
    logger.info(
        f"Starting presence detector (camera={CAMERA_INDEX}, interval={DETECTION_INTERVAL}s)"
    )
    detector = FaceDetector(camera_index=CAMERA_INDEX, interval=DETECTION_INTERVAL)

    try:
        await detector.start()
        logger.info("Presence detector started successfully")
    except Exception as e:
        logger.error(f"Failed to start detector: {e}")
        raise

    # Background task to broadcast updates
    broadcast_task = asyncio.create_task(broadcast_presence_updates())

    yield

    # Shutdown
    logger.info("Shutting down presence detector")
    broadcast_task.cancel()
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass

    await detector.stop()
    logger.info("Presence detector stopped")


app = FastAPI(
    title="Presence Detection Service",
    description="Real-time face presence detection over WebSocket",
    version="1.0.0",
    lifespan=lifespan,
)


async def broadcast_presence_updates():
    """Background task that broadcasts presence updates to all connected clients."""
    last_status = None

    while True:
        try:
            await asyncio.sleep(0.1)  # Check for updates frequently

            if not connected_clients:
                continue

            current_status = detector.get_status()

            # Only broadcast if status has changed
            if current_status != last_status:
                last_status = current_status.copy()

                # Broadcast to all connected clients
                disconnected = set()
                for client in connected_clients:
                    try:
                        await client.send_json(current_status)
                    except Exception as e:
                        logger.warning(f"Failed to send to client: {e}")
                        disconnected.add(client)

                # Remove disconnected clients
                for client in disconnected:
                    connected_clients.discard(client)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in broadcast loop: {e}")
            await asyncio.sleep(1)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Presence Detection Service",
        "version": "1.0.0",
        "endpoints": {"status": "/status", "websocket": "/ws"},
    }


@app.get("/status")
async def get_status():
    """Get current presence status."""
    if not detector:
        return JSONResponse(
            status_code=503, content={"error": "Detector not initialized"}
        )

    status = detector.get_status()
    logger.debug(f"status: {status}")
    if status.get("error"):
        return JSONResponse(status_code=500, content=status)

    return status


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time presence updates."""
    await websocket.accept()
    connected_clients.add(websocket)

    logger.info(f"Client connected. Total clients: {len(connected_clients)}")

    try:
        # Send initial status
        initial_status = detector.get_status()
        logger.debug(f"Sending initial status: {initial_status}")
        await websocket.send_json(initial_status)

        # Keep connection alive and handle incoming messages
        while True:
            # Wait for client messages (mostly to detect disconnection)
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        connected_clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not detector or detector._error:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": detector._error if detector else "Not initialized",
            },
        )

    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {HOST}:{PORT}")
    uvicorn.run("server:app", host=HOST, port=PORT, log_level="info")
