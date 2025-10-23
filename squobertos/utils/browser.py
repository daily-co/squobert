"""Browser launcher utility for SquobertOS"""

import subprocess


def launch_url_in_kiosk(url: str) -> tuple[bool, str]:
    """
    Launch a URL in Chromium kiosk mode.

    Args:
        url: The URL to open

    Returns:
        A tuple of (success: bool, message: str)
    """
    try:
        subprocess.Popen(
            ["chromium", "--kiosk", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # Detach from parent process
        )
        return True, f"Opened {url} in kiosk mode"
    except Exception as e:
        return False, f"Error opening URL: {e}"
