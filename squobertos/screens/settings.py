"""
Settings Screen for SquobertOS
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.screen import Screen
from textual.binding import Binding

from utils import launch_in_terminal, launch_url_in_kiosk
from utils.config import get_config
from widgets.display import CircuitBackground

import subprocess


class ServerInputScreen(Screen):
    """Screen for configuring URLs"""

    BINDINGS = [
        Binding("b", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static("◉ URL Configuration", id="title"),
            Vertical(
                Label("Squobert UI URL:"),
                Input(placeholder="http://localhost:3000", id="server_input"),
                Label("Network Test URL:", classes="url_label"),
                Input(placeholder="http://192.168.1.1", id="network_test_input"),
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
        """Load current URLs"""
        config = get_config()

        # Load Squobert UI URL
        current_url = config.get("squobert_ui.url", "https://squobert.vercel.app")
        input_widget = self.query_one("#server_input", Input)
        input_widget.value = current_url

        # Load Network Test URL
        network_test_url = config.get(
            "network_test.url", "https://network-test-v2.daily.co"
        )
        network_test_widget = self.query_one("#network_test_input", Input)
        network_test_widget.value = network_test_url

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "save_btn":
            self.save_settings()
        elif button_id == "back_btn":
            self.app.pop_screen()

    def save_settings(self) -> None:
        """Save URLs to config file"""
        input_widget = self.query_one("#server_input", Input)
        network_test_widget = self.query_one("#network_test_input", Input)
        status_widget = self.query_one("#status", Static)

        url = input_widget.value.strip()
        if not url:
            status_widget.update("✗ Squobert UI URL cannot be empty")
            return

        network_test_url = network_test_widget.value.strip()

        config = get_config()
        config.set("squobert_ui.url", url)
        if network_test_url:
            config.set("network_test.url", network_test_url)
        status_widget.update("✓ URLs saved")


class SettingsScreen(Screen):
    """System settings screen"""

    BINDINGS = [
        Binding("w", "wifi", "Wifi"),
        Binding("a", "audio", "Audio"),
        Binding("u", "squobert_ui", "URLs"),
        Binding("n", "network_test", "Network Test"),
        Binding("t", "terminal", "Terminal"),
        Binding("r", "update_and_reboot", "Update and Reboot"),
        Binding("b", "back", "Back"),
        Binding("q", "back", "Back"),
        Binding("escape", "back", "Back"),
    ]

    CSS = """
    CircuitBackground {
        layer: background;
    }

    #main_container {
        align: center middle;
        layer: overlay;
    }

    #button_grid {
        width: 80;
        height: 15;
        layer: overlay;
        grid-size: 3 2;
        grid-gutter: 1 2;
    }

    #button_grid Button {
        width: 100%;
        height: 100%;
    }

    #status {
        text-align: center;
        margin-top: 15;
    }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            CircuitBackground(),
            Grid(
                Button("[u]W[/u]ifi", id="wifi_btn", variant="primary"),
                Button("[u]A[/u]udio", id="audio_btn", variant="primary"),
                Button("[u]U[/u]RLs", id="squobert_ui_btn", variant="primary"),
                Button("[u]N[/u]etwork Test", id="network_test_btn", variant="warning"),
                Button("[u]T[/u]erminal", id="terminal_btn", variant="error"),
                Button("[u]B[/u]ack", id="back_btn"),
                id="button_grid",
            ),
            Static("", id="status"),
            id="main_container",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "wifi_btn":
            self.action_wifi()
        elif button_id == "audio_btn":
            self.action_audio()
        elif button_id == "squobert_ui_btn":
            self.action_squobert_ui()
        elif button_id == "network_test_btn":
            self.action_network_test()
        elif button_id == "terminal_btn":
            self.action_terminal()
        elif button_id == "back_btn":
            self.action_back()

    def action_wifi(self) -> None:
        """Launch the impala wifi configuration tool in a new terminal"""
        try:
            success, message = launch_in_terminal("impala")
            status_widget = self.query_one("#status", Static)
            status_widget.update(message)
        except Exception as e:
            # Log error but don't crash
            import sys

            print(f"Error in action_wifi: {e}", file=sys.stderr)

    def action_audio(self) -> None:
        """Launch the wiremix audio configuration tool in a new terminal"""
        try:
            success, message = launch_in_terminal("wiremix")
            status_widget = self.query_one("#status", Static)
            status_widget.update(message)
        except Exception as e:
            # Log error but don't crash
            import sys

            print(f"Error in action_audio: {e}", file=sys.stderr)

    def action_squobert_ui(self) -> None:
        """Open URL configuration screen"""
        self.app.push_screen(ServerInputScreen())

    def action_network_test(self) -> None:
        """Launch network test URL in kiosk mode"""
        try:
            config = get_config()
            url = config.get("network_test.url", "")

            if not url:
                status_widget = self.query_one("#status", Static)
                status_widget.update("✗ Network Test URL not configured")
                return

            success, message = launch_url_in_kiosk(url)
            status_widget = self.query_one("#status", Static)
            status_widget.update(message)
        except Exception as e:
            # Log error but don't crash
            import sys

            print(f"Error in action_network_test: {e}", file=sys.stderr)

    def action_terminal(self) -> None:
        """Launch a new terminal"""
        try:
            success, message = launch_in_terminal("bash")
            status_widget = self.query_one("#status", Static)
            status_widget.update(message)
        except Exception as e:
            # Log error but don't crash
            import sys

            print(f"Error in action_terminal: {e}", file=sys.stderr)

    def action_update_and_reboot(self) -> None:
        """Update code from git and reboot the system"""
        try:
            success, message = launch_in_terminal(
                "bash -c 'cd ~/Code/squobert && git pull && reboot'"
            )
            status_widget = self.query_one("#status", Static)
            status_widget.update(message if success else "✗ Failed to launch update")
        except Exception as e:
            # Log error but don't crash
            import sys

            print(f"Error in action_update_and_reboot: {e}", file=sys.stderr)

    def action_back(self) -> None:
        """Go back to previous screen"""
        self.app.pop_screen()
