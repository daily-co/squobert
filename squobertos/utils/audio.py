"""
Audio device management for SquobertOS using wpctl
"""

import subprocess
import re
from typing import Optional, Tuple


def get_default_audio_devices() -> Tuple[
    Optional[str], Optional[str], Optional[str], Optional[str]
]:
    """
    Get the default audio input and output devices using wpctl.

    Returns:
        Tuple of (input_id, input_name, output_id, output_name)
    """
    try:
        # Get wpctl status
        result = subprocess.run(
            ["wpctl", "status"], capture_output=True, text=True, check=True
        )

        output = result.stdout
        input_id = None
        input_name = None
        output_id = None
        output_name = None

        # Parse the output to find default devices
        # Look for lines like: "* 123. Device Name [vol: 0.50]"
        # The asterisk indicates the default device

        lines = output.split("\n")
        in_audio_section = False
        in_sinks_section = False
        in_sources_section = False

        for line in lines:
            # Check for section headers
            if "Audio" in line:
                in_audio_section = True
                continue
            elif "Video" in line or "Settings" in line:
                in_audio_section = False
                in_sinks_section = False
                in_sources_section = False
                continue

            if in_audio_section:
                if "Sinks:" in line:
                    in_sinks_section = True
                    in_sources_section = False
                    continue
                elif "Sources:" in line:
                    in_sources_section = True
                    in_sinks_section = False
                    continue
                elif "Sink endpoints:" in line or "Source endpoints:" in line:
                    in_sinks_section = False
                    in_sources_section = False
                    continue

                # Look for default device (marked with *)
                if in_sinks_section and "*" in line:
                    # Parse output device
                    match = re.search(r"\*\s+(\d+)\.\s+(.+?)(?:\s+\[|$)", line)
                    if match:
                        output_id = match.group(1)
                        output_name = match.group(2).strip()

                elif in_sources_section and "*" in line:
                    # Parse input device
                    match = re.search(r"\*\s+(\d+)\.\s+(.+?)(?:\s+\[|$)", line)
                    if match:
                        input_id = match.group(1)
                        input_name = match.group(2).strip()

        return input_id, input_name, output_id, output_name

    except subprocess.CalledProcessError:
        return None, None, None, None
    except Exception:
        return None, None, None, None


def set_default_audio_devices(
    input_id: Optional[str] = None, output_id: Optional[str] = None
) -> bool:
    """
    Set the default audio input and/or output devices using wpctl.

    Args:
        input_id: The ID of the input device to set as default
        output_id: The ID of the output device to set as default

    Returns:
        True if successful, False otherwise
    """
    success = True

    try:
        if output_id:
            subprocess.run(
                ["wpctl", "set-default", output_id], check=True, capture_output=True
            )

        if input_id:
            subprocess.run(
                ["wpctl", "set-default", input_id], check=True, capture_output=True
            )

        return success

    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False


def get_device_display_name(device_name: Optional[str]) -> str:
    """
    Convert a device name to a user-friendly display name.

    Args:
        device_name: The raw device name from wpctl

    Returns:
        A user-friendly device name
    """
    if not device_name:
        return "None"

    # Clean up common device name patterns
    # Remove common suffixes and prefixes
    name = device_name

    # Remove "Built-in Audio" prefix if present
    name = re.sub(r"^Built-in Audio\s*", "", name)

    # Simplify common patterns
    replacements = {
        "Analog Stereo": "",
        "Digital Stereo (IEC958)": "Digital",
        "Pro Audio": "",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    # Clean up extra whitespace
    name = " ".join(name.split())

    # Truncate if too long
    if len(name) > 40:
        name = name[:37] + "..."

    return name if name else "Unknown Device"
