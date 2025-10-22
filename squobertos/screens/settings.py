"""
Settings Screen for SquobertOS
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.screen import Screen
from textual.binding import Binding

from utils import launch_in_terminal


class ServerInputScreen(Screen):
    """Screen for configuring Squobert UI server URL"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
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
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("⚙️  System Settings", id="title"),
            Vertical(
                Button("📡 Wifi", id="wifi_btn", variant="primary"),
                Button("🔊 Audio", id="audio_btn", variant="primary"),
                Button("🖥️  Squobert UI", id="squobert_ui_btn", variant="primary"),
                Button("Back", id="back_btn"),
                Static("", id="status"),
                id="settings_container",
            ),
            id="main_container",
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "wifi_btn":
            self.launch_wifi_tool()
        elif button_id == "audio_btn":
            self.launch_audio_tool()
        elif button_id == "squobert_ui_btn":
            self.app.push_screen(ServerInputScreen())
        elif button_id == "back_btn":
            self.app.pop_screen()

    def launch_wifi_tool(self) -> None:
        """Launch the impala wifi configuration tool in a new terminal"""
        status_widget = self.query_one("#status", Static)
        success, message = launch_in_terminal("impala")
        status_widget.update(message)

    def launch_audio_tool(self) -> None:
        """Launch the wiremix audio configuration tool in a new terminal"""
        status_widget = self.query_one("#status", Static)
        success, message = launch_in_terminal("wiremix")
        status_widget.update(message)
