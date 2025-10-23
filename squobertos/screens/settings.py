"""
Settings Screen for SquobertOS
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.screen import Screen
from textual.binding import Binding

from utils import launch_in_terminal
from utils.config import get_config
from widgets.display import CircuitBackground

import subprocess


class ServerInputScreen(Screen):
    """Screen for configuring Squobert UI server URL"""

    BINDINGS = [
        Binding("b", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Static("◉ Squobert UI Configuration", id="title"),
            Vertical(
                Label("Squobert UI URL:"),
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
        """Load current server URL"""
        config = get_config()
        current_url = config.get("squobert_ui.url", "https://squobert.vercel.app")
        input_widget = self.query_one("#server_input", Input)
        input_widget.value = current_url

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "save_btn":
            self.save_settings()
        elif button_id == "back_btn":
            self.app.pop_screen()

    def save_settings(self) -> None:
        """Save server URL to config file"""
        input_widget = self.query_one("#server_input", Input)
        status_widget = self.query_one("#status", Static)

        url = input_widget.value.strip()
        if not url:
            status_widget.update("✗ URL cannot be empty")
            return

        config = get_config()
        config.set("squobert_ui.url", url)
        status_widget.update("✓ Server URL saved")


class SettingsScreen(Screen):
    """System settings screen"""

    BINDINGS = [
        Binding("w", "wifi", "Wifi"),
        Binding("a", "audio", "Audio"),
        Binding("u", "squobert_ui", "Squobert UI"),
        Binding("t", "terminal", "Terminal"),
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
        height: 7;
        layer: overlay;
        grid-size: 5 1;
        grid-gutter: 1 2;
    }

    #button_grid Button {
        width: 100%;
        height: 100%;
    }

    #status {
        text-align: center;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            CircuitBackground(),
            Grid(
                Button("[u]W[/u]ifi", id="wifi_btn", variant="primary"),
                Button("[u]A[/u]udio", id="audio_btn", variant="primary"),
                Button("Squobert [u]U[/u]I", id="squobert_ui_btn", variant="primary"),
                Button("[u]T[/u]erminal", id="terminal_btn", variant="warning"),
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
        """Open Squobert UI configuration screen"""
        self.app.push_screen(ServerInputScreen())

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

    def action_back(self) -> None:
        """Go back to previous screen"""
        self.app.pop_screen()
