"""
Settings Screen for SquobertOS
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.screen import Screen
from textual.binding import Binding


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
