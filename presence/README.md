# Presence Detection Service

A FastAPI-based service that detects face presence using a webcam and streams updates over WebSocket.

## Features

- Real-time face detection using OpenCV's Haar Cascade classifier
- WebSocket streaming for live presence updates
- REST API for polling current status
- Configurable camera selection and detection interval
- Async/await for efficient concurrent connections
- Structured logging with Loguru for better debugging

## Installation

1. Create a virtual environment:
```bash
cd presence
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

Basic usage (uses camera 0, checks every 1 second):
```bash
python main.py
```

With custom configuration:
```bash
PRESENCE_CAMERA_INDEX=0 PRESENCE_INTERVAL_SECONDS=0.5 PRESENCE_PORT=8765 python main.py
```

### Environment Variables

- `PRESENCE_CAMERA_INDEX`: Camera device index (default: 0)
- `PRESENCE_INTERVAL_SECONDS`: Seconds between detection checks (default: 1.0)
- `PRESENCE_HOST`: Server host (default: 0.0.0.0)
- `PRESENCE_PORT`: Server port (default: 8000)

## API Endpoints

### GET /

Service information and available endpoints.

### GET /status

Returns the current presence status:
```json
{
  "type": "presence",
  "timestamp": "2025-10-17T12:34:56.789Z",
  "present": true,
  "faces": 1,
  "processing_ms": 45.2,
  "camera": 0
}
```

### WebSocket /ws

Real-time presence updates. Connect and receive JSON messages whenever presence status changes.

## WebSocket Example

### Python Client

```python
import asyncio
import websockets
import json

async def monitor_presence():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Present: {data['present']}, Faces: {data['faces']}")

asyncio.run(monitor_presence())
```

### JavaScript Client

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Present: ${data.present}, Faces: ${data.faces}`);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

## Architecture

- **detector.py**: Face detection logic using OpenCV
  - `PresenceDetector` class manages camera and detection loop
  - Runs detection in thread pool to avoid blocking async loop
  - Broadcasts updates to registered listener queues

- **main.py**: FastAPI application
  - WebSocket endpoint at `/ws` streams presence updates
  - REST endpoint `/status` for polling current state
  - Lifespan handler manages detector startup/shutdown

## Troubleshooting

### Camera Not Found

If you get "Could not open camera" error:
- Check available cameras: `ls /dev/video*` (Linux)
- Try different `PRESENCE_CAMERA_INDEX` values (0, 1, 2, etc.)
- Ensure camera is not in use by another application

### Permission Denied

On Linux, you may need to add your user to the video group:
```bash
sudo usermod -a -G video $USER
```

Then log out and back in.

## Development

Run with auto-reload for development:
```bash
PRESENCE_RELOAD=true python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

## License

Part of the Squobert project.
