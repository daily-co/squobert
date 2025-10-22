"""
Presence Detection Service for SquobertOS
"""

import sys
import threading
import asyncio
from pathlib import Path

# Import presence detection server
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "presence"))
from server import app as presence_app
import uvicorn


class PresenceService:
    """Manages the presence detection server in a background thread"""

    def __init__(self):
        self.server_thread = None
        self.running = False

    def start(self) -> None:
        """Start the presence detection server in a background thread"""
        if self.running:
            return

        def run_server():
            """Run uvicorn server in this thread"""
            # Redirect uvicorn logs to /dev/null to prevent them from displaying over the UI
            import logging
            from loguru import logger

            # Disable all uvicorn logging
            logging.getLogger("uvicorn").setLevel(logging.CRITICAL)
            logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)
            logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)

            # Disable loguru logger used by presence server
            logger.remove()  # Remove all handlers
            logger.add(lambda _: None)  # Add a no-op handler

            config = uvicorn.Config(
                presence_app,
                host="0.0.0.0",
                port=8765,
                log_level="critical",
                loop="asyncio",
            )
            server = uvicorn.Server(config)
            asyncio.run(server.serve())

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True

    def stop(self) -> None:
        """Stop the presence detection server"""
        # The daemon thread will be automatically cleaned up when the app exits
        self.running = False

    def is_running(self) -> bool:
        """Check if the presence server is running"""
        return self.running
