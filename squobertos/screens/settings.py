"""
Settings Screen for SquobertOS
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.screen import Screen
from textual.binding import Binding

from utils import launch_in_terminal

import subprocess


class ServerInputScreen(Screen):
    """Screen for configuring Squobert UI server URL"""

    BINDINGS = [
        Binding("b", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("🌐 Squobert UI Configuration", id="title"),
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
        # TODO: Load settings from config file
        #
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "save_btn":
            self.save_settings()
        elif button_id == "back_btn":
            self.app.pop_screen()

    def save_settings(self) -> None:
        """Save server URL to config file"""
        status_widget = self.query_one("#status", Static)
        # TODO: Implement settings save
        status_widget.update("✅ Server URL saved")


class SettingsScreen(Screen):
    """System settings screen"""

    BINDINGS = [
        Binding("w", "wifi", "Wifi"),
        Binding("a", "audio", "Audio"),
        Binding("u", "squobert_ui", "Squobert UI"),
        Binding("b", "back", "Back"),
        Binding("escape", "back", "Back"),
    ]

    CSS = """
    #button_grid {
        width: 50%;
        height: 50%;
        grid-size: 2 2;
        grid-gutter: 1 2;
        align: center middle;
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
        yield Header()
        yield Container(
            Grid(
                Button("[u]W[/u]ifi", id="wifi_btn", variant="primary"),
                Button("[u]A[/u]udio", id="audio_btn", variant="primary"),
                Button(
                    "3: Squobert [u]U[/u]I", id="squobert_ui_btn", variant="primary"
                ),
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
        elif button_id == "back_btn":
            self.action_back()

    def action_wifi(self) -> None:
        """Launch the impala wifi configuration tool in a new terminal"""
        status_widget = self.query_one("#status", Static)
        success, message = launch_in_terminal("impala")
        status_widget.update(message)

    def action_audio(self) -> None:
        """Launch the wiremix audio configuration tool in a new terminal"""
        status_widget = self.query_one("#status", Static)
        success, message = launch_in_terminal("wiremix")
        status_widget.update(message)

    def action_squobert_ui(self) -> None:
        """Open Squobert UI configuration screen"""
        self.app.push_screen(ServerInputScreen())

    def action_back(self) -> None:
        """Go back to previous screen"""
        self.app.pop_screen()
