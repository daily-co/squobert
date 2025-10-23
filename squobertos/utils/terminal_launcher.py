"""
Terminal launcher utility for SquobertOS

Launches CLI tools in separate terminal windows without blocking the main application.
"""

import subprocess
import os
from pathlib import Path
from typing import Union


def launch_in_terminal(*command: str) -> tuple[bool, str]:
    """
    Launch a CLI command in a new terminal window.

    This function attempts to launch the specified command in a new terminal window
    using various terminal emulators available on the system. It tries multiple
    common terminal emulators in order of preference.

    Args:
        *command: The CLI command to run in the terminal. Can be a single string
                  or multiple arguments (e.g., "wiremix" or "ffplay", "/dev/video0")

    Returns:
        A tuple of (success: bool, message: str) indicating whether the launch
        succeeded and a status message

    Example:
        >>> success, message = launch_in_terminal("impala")
        >>> if success:
        ...     print(message)  # "✓ Launched command successfully"
        >>>
        >>> success, message = launch_in_terminal("ffplay", "/dev/video0")
        >>> if success:
        ...     print(message)  # "✓ Launched command successfully"
    """
    # Convert command args to a list
    cmd_args = list(command)

    # Create a display string for logging/messages
    cmd_display = " ".join(cmd_args)

    # Create log directory in the same directory as this file
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Create log files for stdout and stderr
    stdout_log = log_dir / "terminal_launcher_stdout.log"
    stderr_log = log_dir / "terminal_launcher_stderr.log"

    # Open log files in write mode (will overwrite each time)
    stdout_file = open(stdout_log, "w")
    stderr_file = open(stderr_log, "w")

    # List of terminal emulators to try, in order of preference
    # Each terminal gets the command args appended after its -e flag
    terminal_emulators = [
        [
            "alacritty",
            "-o",
            'window.decorations="None"',
            "-o",
            "window.dimensions.columns=80",
            "-o",
            "window.dimensions.lines=22",
            "-e",
        ]
        + cmd_args,
        ["ghostty", "-e"] + cmd_args,  # selfish, for Chad
        # And some fallbacks
        ["xterm", "-e"] + cmd_args,
        ["x-terminal-emulator", "-e"] + cmd_args,
        ["gnome-terminal", "--"] + cmd_args,
        ["konsole", "-e"] + cmd_args,
        ["xfce4-terminal", "-e"] + cmd_args,
    ]

    for terminal_cmd in terminal_emulators:
        try:
            # Launch the command in a new terminal window
            # start_new_session=True ensures it doesn't block the parent process
            subprocess.Popen(
                terminal_cmd,
                start_new_session=True,
                stdout=stdout_file,
                stderr=stderr_file,
            )
            return True, f"✓ Launched {cmd_display} successfully (logs: {log_dir})"
        except FileNotFoundError:
            # This terminal emulator is not available, try the next one
            continue
        except Exception as e:
            # Unexpected error occurred
            stdout_file.close()
            stderr_file.close()
            return False, f"✗ Error launching {cmd_display}: {e}"

    # None of the terminal emulators were found
    stdout_file.close()
    stderr_file.close()
    return False, f"✗ Could not find a terminal emulator to launch {cmd_display}"
