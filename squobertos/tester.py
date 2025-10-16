#!/usr/bin/env python3
"""
Tester app for experimenting with Squobert face design
"""

from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Static
from textual.containers import Container


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

            # Ensure both have the same number of lines (37)
            while len(circuit_lines) < 37:
                circuit_lines.append(" " * 128)
            while len(squobert_lines) < 37:
                squobert_lines.append(" " * 128)

            # Overlay squobert on circuit
            result_lines = []
            for i in range(37):
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


class TesterApp(App):
    """Test app for layered display"""

    CSS = """
    Screen {
        align: center middle;
    }

    LayeredDisplay {
        width: 128;
        height: 37;
        border: solid green;
    }
    """

    def compose(self) -> ComposeResult:
        yield LayeredDisplay()


if __name__ == "__main__":
    app = TesterApp()
    app.run()
