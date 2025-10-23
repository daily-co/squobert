"""
Main Menu Screen for SquobertOS
"""

import subprocess
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Button, Static
from textual.screen import Screen
from textual.binding import Binding

from widgets.display import LayeredDisplay
from utils.config import get_config
from utils import launch_url_in_kiosk
from utils.audio import get_default_audio_devices, get_device_display_name
from utils.network import get_wifi_info, format_network_status


class MainMenuScreen(Screen):
    """Main menu screen with configuration options"""

    BINDINGS = [
        Binding("u", "launch_ui", "Squobert UI"),
        Binding("s", "settings", "Settings"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            LayeredDisplay(id="squobert_face"),
            Container(
                Static("● Presence: Starting...", id="presence_status"),
                Static("♪ Input: Loading... | ♫ Output: Loading...", id="audio_status"),
                Static("◉ Network: Loading...", id="network_status"),
                id="status_lines",
            ),
            Horizontal(
                Button("Squobert [u]U[/u]I", id="ui_btn", variant="success"),
                Button(
                    "[u]S[/u]ettings",
                    id="settings_btn",
                ),
                Button("[u]Q[/u]uit", id="quit_btn"),
                id="bottom_buttons",
            ),
            id="main_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen"""
        # Load initial status displays
        self.update_audio_status()
        self.update_network_status()
        # Set up 5-second refresh for network status
        self.set_interval(5.0, self.update_network_status)

    def on_screen_resume(self) -> None:
        """Called when returning to this screen from another screen"""
        # Refresh status displays when returning from settings
        self.update_audio_status()
        self.update_network_status()

    def update_audio_status(self) -> None:
        """Update the audio device status display"""
        try:
            input_id, input_name, output_id, output_name = get_default_audio_devices()

            # Check if both devices are Jabra SPEAK 410
            if "Jabra SPEAK 410" in input_name and "Jabra SPEAK 410" in output_name:
                status_text = "♪ Audio: Jabra SPEAK 410"
                status_color = "green"
            else:
                # Get user-friendly names
                input_display = get_device_display_name(input_name)
                output_display = get_device_display_name(output_name)
                status_text = f"♪ Input: {input_display} | ♫ Output: {output_display}"
                status_color = "orange"

            audio_status = self.query_one("#audio_status", Static)
            audio_status.update(f"[{status_color}]{status_text}[/{status_color}]")
        except Exception:
            # If we can't get audio status, show error
            try:
                audio_status = self.query_one("#audio_status", Static)
                audio_status.update(
                    "[orange]♪ Input: Unknown | ♫ Output: Unknown[/orange]"
                )
            except Exception:
                pass

    def update_network_status(self) -> None:
        """Update the network status display"""
        try:
            ssid, ip = get_wifi_info()
            status_text = format_network_status(ssid, ip)

            # Green if WiFi is connected and has an IP, orange otherwise
            if ssid and ip:
                status_color = "green"
            else:
                status_color = "orange"

            network_status = self.query_one("#network_status", Static)
            network_status.update(f"[{status_color}]{status_text}[/{status_color}]")
        except Exception:
            # If we can't get network status, show error
            try:
                network_status = self.query_one("#network_status", Static)
                network_status.update("[orange]◉ Network: Unknown[/orange]")
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "settings_btn":
            self.action_settings()
        elif button_id == "ui_btn":
            self.action_launch_ui()
        elif button_id == "quit_btn":
            self.app.exit()

    def action_launch_ui(self) -> None:
        """Launch Chromium in kiosk mode for AI interface"""
        try:
            # Get URL from config
            config = get_config()
            url = config.get("squobert_ui.url", "https://squobert.vercel.app")

            # Launch URL in kiosk mode
            launch_url_in_kiosk(url)
        except Exception as e:
            # Show error in a way that's visible in the TUI
            from textual.widgets import Label

            error_label = Label(f"Error: {e}")
            self.mount(error_label)

    def action_settings(self) -> None:
        """Open Settings screen"""
        # Import here to avoid circular import
        from screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())

    def action_quit(self) -> None:
        """Quit the application"""
        self.app.exit()
