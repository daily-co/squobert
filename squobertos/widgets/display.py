"""
Layered Display Widget for SquobertOS
"""

from pathlib import Path
from textual.widgets import Static


class LayeredDisplay(Static):
    """Widget to display circuit background with squobert overlay"""

    def render(self) -> str:
        """Render the layered display with circuit and squobert"""
        # Load the circuit background from file
        circuit_file = Path(__file__).parent.parent / "assets/circuit.txt"
        squobert_file = Path(__file__).parent.parent / "assets/face.txt"

        TARGET_WIDTH = 113
        TARGET_HEIGHT = 31

        try:
            with open(circuit_file, "r", encoding="utf-8") as f:
                circuit_lines = f.read().splitlines()

            with open(squobert_file, "r", encoding="utf-8") as f:
                squobert_lines = f.read().splitlines()

            # Pad to target height if needed
            while len(circuit_lines) < TARGET_HEIGHT:
                circuit_lines.append("")
            while len(squobert_lines) < TARGET_HEIGHT:
                squobert_lines.append("")

            # Overlay squobert on circuit
            result_lines = []
            for i in range(TARGET_HEIGHT):
                circuit_line = circuit_lines[i] if i < len(circuit_lines) else ""
                squobert_line = squobert_lines[i] if i < len(squobert_lines) else ""

                # Pad to target width
                circuit_line = circuit_line.ljust(TARGET_WIDTH)
                squobert_line = squobert_line.ljust(TARGET_WIDTH)

                # Overlay: use squobert character if non-space, otherwise use circuit
                overlay_line = ""
                for j in range(TARGET_WIDTH):
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
