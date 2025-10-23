#!/usr/bin/env python3
"""
Simple test script for terminal launcher
"""

from utils.terminal_launcher import launch_in_terminal

print("Testing terminal launcher...")
success, message = launch_in_terminal("wiremix")
print(f"Success: {success}")
print(f"Message: {message}")
