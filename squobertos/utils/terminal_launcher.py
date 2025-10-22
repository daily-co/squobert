"""
Terminal launcher utility for SquobertOS

Launches CLI tools in separate terminal windows without blocking the main application.
"""

import subprocess
from typing import Optional


def launch_in_terminal(command: str) -> tuple[bool, str]:
    """
    Launch a CLI command in a new terminal window.

    This function attempts to launch the specified command in a new terminal window
    using various terminal emulators available on the system. It tries multiple
    common terminal emulators in order of preference.

    Args:
        command: The CLI command to run in the terminal

    Returns:
        A tuple of (success: bool, message: str) indicating whether the launch
        succeeded and a status message

    Example:
        >>> success, message = launch_in_terminal("impala")
        >>> if success:
        ...     print(message)  # "✅ Launched command successfully"
    """
    # List of terminal emulators to try, in order of preference
    terminal_emulators = [
        ["xterm", "-e", command],  # the Pi
        ["ghostty", "-e", command],  # selfish, for Chad
        # And some fallbacks
        ["x-terminal-emulator", "-e", command],
        ["gnome-terminal", "--", command],
        ["konsole", "-e", command],
        ["xfce4-terminal", "-e", command],
    ]

    for terminal_cmd in terminal_emulators:
        try:
            # Launch the command in a new terminal window
            # start_new_session=True ensures it doesn't block the parent process
            subprocess.Popen(
                terminal_cmd,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True, f"✅ Launched {command} successfully"
        except FileNotFoundError:
            # This terminal emulator is not available, try the next one
            continue
        except Exception as e:
            # Unexpected error occurred
            return False, f"❌ Error launching {command}: {e}"

    # None of the terminal emulators were found
    return False, f"❌ Could not find a terminal emulator to launch {command}"
