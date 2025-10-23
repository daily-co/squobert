"""
Network utilities for SquobertOS
"""

import subprocess
import re
from typing import Optional, Tuple


def get_wifi_info() -> Tuple[Optional[str], Optional[str]]:
    """
    Get the current WiFi network name (SSID) and IP address.

    Returns:
        Tuple of (ssid, ip_address)
    """
    ssid = get_wifi_ssid()
    ip = get_ip_address()
    return ssid, ip


def get_wifi_ssid() -> Optional[str]:
    """
    Get the current WiFi network SSID.

    Returns:
        The SSID of the connected WiFi network, or None if not connected
    """
    try:
        # Try using iwgetid first (most reliable for WiFi)
        result = subprocess.run(
            ["iwgetid", "-r"], capture_output=True, text=True, check=False
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()

        # Fallback: try nmcli
        result = subprocess.run(
            ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("yes:"):
                    ssid = line.split(":", 1)[1].strip()
                    if ssid:
                        return ssid

        return None

    except Exception:
        return None


def get_ip_address() -> Optional[str]:
    """
    Get the current IP address of the default network interface.

    Returns:
        The IP address, or None if not available
    """
    try:
        # Use hostname -I to get all IP addresses, take the first one
        result = subprocess.run(
            ["hostname", "-I"], capture_output=True, text=True, check=False
        )

        if result.returncode == 0 and result.stdout.strip():
            # Get the first IP address
            ips = result.stdout.strip().split()
            if ips:
                # Filter out IPv6 addresses (contain colons)
                ipv4_addresses = [ip for ip in ips if ":" not in ip]
                if ipv4_addresses:
                    return ipv4_addresses[0]

        # Fallback: try ip command
        result = subprocess.run(
            ["ip", "-4", "addr", "show"], capture_output=True, text=True, check=False
        )

        if result.returncode == 0:
            # Look for inet addresses that are not loopback
            for line in result.stdout.split("\n"):
                if "inet " in line and "127.0.0.1" not in line:
                    match = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", line)
                    if match:
                        return match.group(1)

        return None

    except Exception:
        return None


def format_network_status(ssid: Optional[str], ip: Optional[str]) -> str:
    """
    Format network status for display.

    Args:
        ssid: The WiFi SSID
        ip: The IP address

    Returns:
        Formatted status string
    """
    if not ssid and not ip:
        return "◉ Network: Not connected"

    parts = []

    if ssid:
        # Truncate SSID if too long
        display_ssid = ssid if len(ssid) <= 20 else ssid[:17] + "..."
        parts.append(f"◉ WiFi: {display_ssid}")
    else:
        parts.append("◉ WiFi: Not connected")

    if ip:
        parts.append(f"IP: {ip}")

    return " | ".join(parts)
