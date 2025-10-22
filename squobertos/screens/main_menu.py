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


class MainMenuScreen(Screen):
    """Main menu screen with configuration options"""

    BINDINGS = [
        Binding("u", "launch_ui", "Squobert UI"),
        Binding("s", "settings", "Settings"),
        Binding("q", "quit", "Quit"),
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
            # Launch Chromium in the background without blocking
            # Using Popen instead of run so it doesn't wait for the browser to close
            subprocess.Popen(
                [
                    "chromium",
                    "--kiosk",
                    "https://squobert.vercel.app",  # TODO: Make this configurable
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # Detach from parent process
            )
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
