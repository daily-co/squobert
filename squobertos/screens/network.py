"""
Network Configuration Screen for SquobertOS
"""

import subprocess
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Label, Input, Static
from textual.screen import Screen
from textual.binding import Binding


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
