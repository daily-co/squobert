"""
CSS Styles for SquobertOS TUI
"""

SQUOBERTOS_CSS = """
Screen {
    align: center middle;
}

#main_container {
    width: 113;
    height: 30;
    align: center middle;
}

#squobert_face {
    width: 113;
    height: 30;
}

#title {
    layer: overlay;
    dock: top;
    width: 100%;
    height: 1;
    text-align: center;
    text-style: bold;
    color: $accent;
    background: $background 50%;
}

#status_lines {
    layer: overlay;
    offset: 0 -4;
    width: 80;
    height: auto;
}

#status_lines Static {
    width: 100%;
    height: auto;
    text-align: left;
    color: $accent;
}

#bottom_buttons {
    layer: overlay;
    offset: 0 7;
    width: 80;
    height: 5;
}

#bottom_buttons Button {
    width: 1fr;
    height: 5;
    min-height: 1;
    margin: 0 2;
}

#wifi_container, #settings_container {
    width: 80%;
    height: auto;
}

#networks {
    height: 12;
    border: solid $primary;
    padding: 1;
    margin: 1 0;
    overflow-y: scroll;
}

Input {
    width: 100%;
    margin: 1 0;
}

#wifi_buttons, #settings_buttons {
    width: 100%;
    height: auto;
    margin-top: 2;
}

#wifi_buttons Button, #settings_buttons Button {
    width: 1fr;
    margin: 0 1;
}

#status {
    margin-top: 1;
    text-align: center;
    color: $accent;
}
"""
