#!/usr/bin/env python3
"""
SquobertOS - Configuration TUI for Squobert
A terminal-based interface for configuring Squobert at new locations
"""

import os
import sys
import subprocess
from textual.app import App
from textual.widgets import Static

# Suppress GStreamer and OpenCV warnings before any imports
os.environ["OPENCV_LOG_LEVEL"] = "OFF"
os.environ["OPENCV_VIDEOIO_DEBUG"] = "0"
os.environ["GST_DEBUG"] = "0"
os.environ["GSTREAMER_DEBUG"] = "0"

# Redirect stderr to suppress C-level warnings
import warnings

warnings.filterwarnings("ignore")

from styles import SQUOBERTOS_CSS
from screens.main_menu import MainMenuScreen
from services.presence import PresenceService


class SquobertOS(App):
    """SquobertOS Configuration TUI"""

    CSS = SQUOBERTOS_CSS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.presence_service = PresenceService()

    def on_mount(self) -> None:
        """Set up the application"""
        from utils.config import get_config

        self.title = "SquobertOS"
        self.sub_title = "Configuration Interface"

        # Only start presence service if enabled in config
        config = get_config()
        enabled = config.get("presence.enabled", True)
        if enabled:
            self.presence_service.start()

        self.push_screen(MainMenuScreen())
        # Set up periodic presence status check
        self.set_interval(2.0, self.update_presence_status)

    def update_presence_status(self) -> None:
        """Update the presence status indicator"""
        import requests
        from utils.config import get_config

        status_text = ""
        status_color = "red"  # Default to red

        # Check if presence detector is enabled in config
        config = get_config()
        enabled = config.get("presence.enabled", True)

        if not enabled:
            status_text = "● Presence: Disabled"
            status_color = "gray"
        else:
            try:
                response = requests.get("http://localhost:8765/status", timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    available = data.get("available", True)

                    if not available:
                        status_text = "● Presence: Unavailable (OpenCV not installed)"
                        status_color = "red"
                    else:
                        present = data.get("present", False)
                        face_count = data.get("face_count", 0)
                        if present:
                            status_text = f"● Presence: Active ({face_count} face{'s' if face_count != 1 else ''})"
                            status_color = "green"
                        else:
                            status_text = "● Presence: No faces detected"
                            status_color = "orange"
                else:
                    status_text = "● Presence: Error"
                    status_color = "red"
            except Exception:
                status_text = "● Presence: Starting..."
                status_color = "orange"

        # Update the status widget if it exists and we're on the main screen
        try:
            if hasattr(self.screen, "query_one"):
                status_widget = self.screen.query_one("#presence_status", Static)
                status_widget.update(f"[{status_color}]{status_text}[/{status_color}]")
        except Exception:
            pass  # Widget not found or screen changed


def launch_ai_mode():
    """Launch Chromium in kiosk mode for AI interface"""
    print("Launching Squobert AI Mode...")
    try:
        # Launch Chromium in fullscreen kiosk mode
        # This will start its own X session if needed
        subprocess.run(
            [
                "chromium-browser",
                "--kiosk",
                "--noerrdialogs",
                "--disable-infobars",
                "--yes-first-run",
                "--check-for-update-interval=31535999",
                "https://squobert.vercel.app",  # TODO: Make this configurable
            ]
        )
    except Exception as e:
        print(f"Error launching AI mode: {e}")
        input("Press Enter to continue...")


def main():
    """Main entry point"""
    app = SquobertOS()
    result = app.run()

    # Clear screen after TUI exits
    subprocess.run(["clear"])

    # Handle exit actions
    if result == "launch_ai":
        launch_ai_mode()
    elif result == "shell":
        print("Exiting to shell...")
        subprocess.run(["/bin/bash"])
        # After shell exits, restart the TUI
        main()


if __name__ == "__main__":
    main()
