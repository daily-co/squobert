"""
Presence Detection Service for SquobertOS
"""

import sys
import threading
import asyncio
from pathlib import Path
import time

# Import presence detection server
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "presence"))
from server import app as presence_app
import uvicorn


class PresenceService:
    """Manages the presence detection server in a background thread"""

    def __init__(self):
        self.server_thread = None
        self.server = None
        self.running = False
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the presence detection server in a background thread"""
        if self.running:
            return

        self._stop_event.clear()

        def run_server():
            """Run uvicorn server in this thread"""
            # Create log directory and file
            log_dir = Path(__file__).parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "presence_detector.log"

            # Open log file in write mode (overwrite each time)
            with open(log_file, "w") as log:
                # Redirect stdout and stderr to log file
                import sys as pysys

                old_stdout = pysys.stdout
                old_stderr = pysys.stderr
                pysys.stdout = log
                pysys.stderr = log

                try:
                    # Redirect uvicorn logs to the log file
                    import logging
                    from loguru import logger

                    # Configure uvicorn logging to use the log file
                    logging.basicConfig(
                        stream=log,
                        level=logging.INFO,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    )

                    # Configure loguru logger to use the log file
                    logger.remove()  # Remove all handlers
                    logger.add(log, level="INFO")

                    config = uvicorn.Config(
                        presence_app,
                        host="0.0.0.0",
                        port=8765,
                        log_level="info",
                        loop="asyncio",
                    )
                    self.server = uvicorn.Server(config)

                    # Run the server
                    asyncio.run(self.server.serve())
                finally:
                    # Restore stdout and stderr
                    pysys.stdout = old_stdout
                    pysys.stderr = old_stderr

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.running = True

        # Give the server a moment to start
        time.sleep(0.5)

    def stop(self) -> None:
        """Stop the presence detection server"""
        if not self.running:
            return

        self.running = False

        # Signal the server to stop
        if self.server:
            self.server.should_exit = True

        self._stop_event.set()

        # Give it a moment to shut down gracefully
        time.sleep(1)

    def is_running(self) -> bool:
        """Check if the presence server is running"""
        return self.running
