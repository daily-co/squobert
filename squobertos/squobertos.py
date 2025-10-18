#!/usr/bin/env python3
"""
SquobertOS - Configuration TUI for Squobert
A terminal-based interface for configuring Squobert at new locations
"""

import subprocess
import sys
import threading
import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.screen import Screen
from textual.binding import Binding

# Import presence detection server
import os

sys.path.insert(0, str(Path(__file__).parent.parent / "presence"))
from server import app as presence_app
import uvicorn


class LayeredDisplay(Static):
    """Widget to display circuit background with squobert overlay"""

    def render(self) -> str:
        """Render the layered display with circuit and squobert"""
        # Load the circuit background from file
        circuit_file = Path(__file__).parent / "assets/circuit.txt"
        squobert_file = Path(__file__).parent / "assets/face.txt"

        try:
            with open(circuit_file, "r", encoding="utf-8") as f:
                circuit_lines = f.read().splitlines()

            with open(squobert_file, "r", encoding="utf-8") as f:
                squobert_lines = f.read().splitlines()

            # Ensure both have the same number of lines (35)
            while len(circuit_lines) < 35:
                circuit_lines.append(" " * 128)
            while len(squobert_lines) < 35:
                squobert_lines.append(" " * 128)

            # Overlay squobert on circuit
            result_lines = []
            for i in range(35):
                circuit_line = circuit_lines[i] if i < len(circuit_lines) else " " * 128
                squobert_line = (
                    squobert_lines[i] if i < len(squobert_lines) else " " * 128
                )

                # Ensure lines are padded to at least 128 characters
                circuit_line = circuit_line.ljust(128)
                squobert_line = squobert_line.ljust(128)

                # Overlay: use squobert character if non-space, otherwise use circuit
                overlay_line = ""
                max_len = max(len(circuit_line), len(squobert_line))
                for j in range(max_len):
                    c_char = circuit_line[j] if j < len(circuit_line) else " "
                    s_char = squobert_line[j] if j < len(squobert_line) else " "

                    if s_char != " ":
                        # Light green for squobert
                        overlay_line += f"[#00ff00]{s_char}[/]"
                    elif c_char != " ":
                        # Dark green for circuit
                        overlay_line += f"[#004900]{c_char}[/]"
                    else:
                        overlay_line += " "

                result_lines.append(overlay_line)

            return "\n".join(result_lines)

        except FileNotFoundError as e:
            return f"File not found: {e}"


class MainMenuScreen(Screen):
    """Main menu screen with configuration options"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "chat_mode", "Chat Mode"),
        Binding("2", "eval_mode", "Eval Mode"),
        Binding("3", "configure_wifi", "Network"),
        Binding("4", "configure_audio", "Audio"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            LayeredDisplay(id="squobert_face"),
            Horizontal(
                Static("🔴 Presence: Starting...", id="presence_status"),
                id="top_buttons",
            ),
            Horizontal(
                Button("1: Launch", id="ai_btn", variant="success"),
                Button(
                    "2: Settings",
                    id="wifi_btn",
                ),
                Button("q: Quit", id="quit_btn"),
                id="bottom_buttons",
            ),
            id="main_container",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "wifi_btn":
            self.action_configure_wifi()
        elif button_id == "ai_btn":
            self.action_launch_ai()
        elif button_id == "settings_btn":
            self.app.push_screen(SettingsScreen())
        elif button_id == "audio_btn":
            self.action_audio()
        elif button_id == "quit_btn":
            self.app.exit()

    def action_configure_wifi(self) -> None:
        """Open Network configuration screen"""
        self.app.push_screen(NetworkScreen())

    def action_launch_ai(self) -> None:
        """Launch Squobert AI mode in fullscreen Chromium"""
        self.app.exit(message="launch_ai")

    def action_audio(self) -> None:
        """Configure audio"""
        self.app.exit(message="shell")

    def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()


class NetworkScreen(Screen):
    """Network configuration screen"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("📡 Network Configuration", id="title"),
            Vertical(
                Label("Available Networks:"),
                Static("Scanning...", id="networks"),
                Label("Connect to Network:"),
                Input(placeholder="SSID", id="ssid_input"),
                Input(placeholder="Password", password=True, id="password_input"),
                Horizontal(
                    Button("Scan Networks", id="scan_btn", variant="primary"),
                    Button("Connect", id="connect_btn", variant="success"),
                    Button("Back", id="back_btn"),
                    id="wifi_buttons",
                ),
                Static("", id="status"),
                id="wifi_container",
            ),
            id="main_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Scan for networks on mount"""
        self.scan_networks()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "scan_btn":
            self.scan_networks()
        elif button_id == "connect_btn":
            self.connect_to_network()
        elif button_id == "back_btn":
            self.app.pop_screen()

    def scan_networks(self) -> None:
        """Scan for available Network networks"""
        networks_widget = self.query_one("#networks", Static)
        networks_widget.update("Scanning...")

        try:
            # Use nmcli to scan for networks
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                formatted = []
                for line in lines[:10]:  # Show top 10 networks
                    parts = line.split(":")
                    if len(parts) >= 3 and parts[0]:
                        ssid = parts[0]
                        signal = parts[1]
                        security = parts[2] if parts[2] else "Open"
                        formatted.append(f"  {ssid:30s} {signal:>3s}% {security}")

                if formatted:
                    networks_widget.update("\n".join(formatted))
                else:
                    networks_widget.update("No networks found")
            else:
                networks_widget.update("Error scanning networks")
        except Exception as e:
            networks_widget.update(f"Error: {str(e)}")

    def connect_to_network(self) -> None:
        """Connect to the specified network(s)"""
        ssid_input = self.query_one("#ssid_input", Input)
        password_input = self.query_one("#password_input", Input)
        status_widget = self.query_one("#status", Static)

        ssid = ssid_input.value.strip()
        password = password_input.value

        if not ssid:
            status_widget.update("❌ Please enter an SSID")
            return

        status_widget.update(f"Connecting to {ssid}...")

        try:
            # Use nmcli to connect to the network
            if password:
                result = subprocess.run(
                    ["nmcli", "device", "wifi", "connect", ssid, "password", password],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            else:
                result = subprocess.run(
                    ["nmcli", "device", "wifi", "connect", ssid],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            if result.returncode == 0:
                status_widget.update(f"✅ Connected to {ssid}")
                password_input.value = ""
            else:
                status_widget.update(f"❌ Connection failed: {result.stderr.strip()}")
        except Exception as e:
            status_widget.update(f"❌ Error: {str(e)}")


class SettingsScreen(Screen):
    """System settings screen"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("⚙️  System Settings", id="title"),
            Vertical(
                Label("Hostname:"),
                Input(placeholder="squobert", id="hostname_input"),
                Label("AI Server URL:"),
                Input(placeholder="http://localhost:3000", id="server_input"),
                Horizontal(
                    Button("Save", id="save_btn", variant="success"),
                    Button("Back", id="back_btn"),
                    id="settings_buttons",
                ),
                Static("", id="status"),
                id="settings_container",
            ),
            id="main_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load current settings"""
        # TODO: Load settings from config file
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "save_btn":
            self.save_settings()
        elif button_id == "back_btn":
            self.app.pop_screen()

    def save_settings(self) -> None:
        """Save settings to config file"""
        status_widget = self.query_one("#status", Static)
        # TODO: Implement settings save
        status_widget.update("✅ Settings saved")


class SquobertOS(App):
    """SquobertOS Configuration TUI"""

    # Presence server thread
    presence_server_thread = None
    presence_server_running = False

    CSS = """
    Screen {
        align: center middle;
    }

    #main_container {
        width: 128;
        height: 33;
        align: center middle;
    }

    #squobert_face {
        width: 128;
        height: 33;
    }

    #title {
        layer: overlay;
        dock: top;
        width: 100%;
        height: 1;
        text-align: center;
        text-style: bold;
        color: $accent;
        background: $background 50%;
    }

    #top_buttons {
        layer: overlay;
        offset: 0 -4;
        width: 80;
        height: 5;
    }

    #bottom_buttons {
        layer: overlay;
        offset: 0 7;
        width: 80;
        height: 5;
    }

    #top_buttons Button, #bottom_buttons Button {
        width: 1fr;
        height: 5;
        min-height: 1;
        margin: 0 2;
    }

    #wifi_container, #settings_container {
        width: 80%;
        height: auto;
    }

    #networks {
        height: 12;
        border: solid $primary;
        padding: 1;
        margin: 1 0;
        overflow-y: scroll;
    }

    Input {
        width: 100%;
        margin: 1 0;
    }

    #wifi_buttons, #settings_buttons {
        width: 100%;
        height: auto;
        margin-top: 2;
    }

    #wifi_buttons Button, #settings_buttons Button {
        width: 1fr;
        margin: 0 1;
    }

    #status {
        margin-top: 1;
        text-align: center;
        color: $accent;
    }

    #presence_status {
        width: 100%;
        height: auto;
        text-align: center;
        color: $accent;
        background: $background 80%;
        padding: 0 1;
    }
    """

    def on_mount(self) -> None:
        """Set up the application"""
        self.title = "SquobertOS"
        self.sub_title = "Configuration Interface"
        self.start_presence_server()
        self.push_screen(MainMenuScreen())
        # Set up periodic presence status check
        self.set_interval(2.0, self.update_presence_status)

    def update_presence_status(self) -> None:
        """Update the presence status indicator"""
        import requests

        try:
            response = requests.get("http://localhost:8765/status", timeout=1)
            if response.status_code == 200:
                data = response.json()
                present = data.get("present", False)
                face_count = data.get("face_count", 0)
                if present:
                    status_text = f"🟢 Presence: Active ({face_count} face{'s' if face_count != 1 else ''})"
                else:
                    status_text = "🟡 Presence: No faces detected"
            else:
                status_text = "🔴 Presence: Error"
        except Exception:
            status_text = "🔴 Presence: Starting..."

        # Update the status widget if it exists and we're on the main screen
        try:
            if hasattr(self.screen, "query_one"):
                status_widget = self.screen.query_one("#presence_status", Static)
                status_widget.update(status_text)
        except Exception:
            pass  # Widget not found or screen changed

    def start_presence_server(self) -> None:
        """Start the presence detection server in a background thread"""
        if self.presence_server_running:
            return

        def run_server():
            """Run uvicorn server in this thread"""
            # Redirect uvicorn logs to /dev/null to prevent them from displaying over the UI
            import logging

            logging.getLogger("uvicorn").setLevel(logging.CRITICAL)
            logging.getLogger("uvicorn.access").setLevel(logging.CRITICAL)
            logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)

            config = uvicorn.Config(
                presence_app,
                host="0.0.0.0",
                port=8765,
                log_level="critical",
                loop="asyncio",
            )
            server = uvicorn.Server(config)
            asyncio.run(server.serve())

        self.presence_server_thread = threading.Thread(target=run_server, daemon=True)
        self.presence_server_thread.start()
        self.presence_server_running = True

    def stop_presence_server(self) -> None:
        """Stop the presence detection server"""
        # The daemon thread will be automatically cleaned up when the app exits
        self.presence_server_running = False


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
                "--no-first-run",
                "--check-for-update-interval=31536000",
                "http://localhost:3000",  # TODO: Make this configurable
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
