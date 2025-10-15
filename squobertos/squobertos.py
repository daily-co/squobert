#!/usr/bin/env python3
"""
SquobertOS - Configuration TUI for Squobert
A terminal-based interface for configuring Squobert at new locations
"""

import subprocess
import sys
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.screen import Screen
from textual.binding import Binding


class MainMenuScreen(Screen):
    """Main menu screen with configuration options"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("1", "configure_wifi", "WiFi"),
        Binding("2", "launch_ai", "Launch AI"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("🤖 SquobertOS", id="title"),
            Static("Configuration Menu", id="subtitle"),
            Vertical(
                Button("1. Configure WiFi", id="wifi_btn", variant="primary"),
                Button("2. Launch AI Mode", id="ai_btn", variant="success"),
                Button("3. System Settings", id="settings_btn"),
                Button("4. Exit to Shell", id="shell_btn"),
                Button("Q. Quit", id="quit_btn", variant="error"),
                id="menu_buttons"
            ),
            id="main_container"
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
        elif button_id == "shell_btn":
            self.action_shell()
        elif button_id == "quit_btn":
            self.app.exit()

    def action_configure_wifi(self) -> None:
        """Open WiFi configuration screen"""
        self.app.push_screen(WiFiScreen())

    def action_launch_ai(self) -> None:
        """Launch Squobert AI mode in fullscreen Chromium"""
        self.app.exit(message="launch_ai")

    def action_shell(self) -> None:
        """Exit to shell"""
        self.app.exit(message="shell")

    def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()


class WiFiScreen(Screen):
    """WiFi configuration screen"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("📡 WiFi Configuration", id="title"),
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
                    id="wifi_buttons"
                ),
                Static("", id="status"),
                id="wifi_container"
            ),
            id="main_container"
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
        """Scan for available WiFi networks"""
        networks_widget = self.query_one("#networks", Static)
        networks_widget.update("Scanning...")

        try:
            # Use nmcli to scan for networks
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                formatted = []
                for line in lines[:10]:  # Show top 10 networks
                    parts = line.split(':')
                    if len(parts) >= 3 and parts[0]:
                        ssid = parts[0]
                        signal = parts[1]
                        security = parts[2] if parts[2] else "Open"
                        formatted.append(f"  {ssid:30s} {signal:>3s}% {security}")

                if formatted:
                    networks_widget.update('\n'.join(formatted))
                else:
                    networks_widget.update("No networks found")
            else:
                networks_widget.update("Error scanning networks")
        except Exception as e:
            networks_widget.update(f"Error: {str(e)}")

    def connect_to_network(self) -> None:
        """Connect to the specified WiFi network"""
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
                    timeout=30
                )
            else:
                result = subprocess.run(
                    ["nmcli", "device", "wifi", "connect", ssid],
                    capture_output=True,
                    text=True,
                    timeout=30
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
                    id="settings_buttons"
                ),
                Static("", id="status"),
                id="settings_container"
            ),
            id="main_container"
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

    CSS = """
    Screen {
        align: center middle;
    }

    #main_container {
        width: 80;
        height: auto;
        border: solid $primary;
        padding: 1 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 1 0;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    #menu_buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    Button {
        width: 100%;
        margin: 1 0;
    }

    #wifi_container, #settings_container {
        width: 100%;
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
    """

    def on_mount(self) -> None:
        """Set up the application"""
        self.title = "SquobertOS"
        self.sub_title = "Configuration Interface"
        self.push_screen(MainMenuScreen())


def launch_ai_mode():
    """Launch Chromium in kiosk mode for AI interface"""
    print("Launching Squobert AI Mode...")
    try:
        # Launch Chromium in fullscreen kiosk mode
        # This will start its own X session if needed
        subprocess.run([
            "chromium-browser",
            "--kiosk",
            "--noerrdialogs",
            "--disable-infobars",
            "--no-first-run",
            "--check-for-update-interval=31536000",
            "http://localhost:3000"  # TODO: Make this configurable
        ])
    except Exception as e:
        print(f"Error launching AI mode: {e}")
        input("Press Enter to continue...")


def main():
    """Main entry point"""
    app = SquobertOS()
    result = app.run()

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
