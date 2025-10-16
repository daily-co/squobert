# SquobertOS

A terminal-based configuration interface for Squobert, designed to boot directly without a desktop environment.

## Hardware

- Raspberry Pi 5 running Raspberry Pi OS
- Jabra 410 speakerphone (speaker + microphone)
- Logitech C925 webcam
- 7-inch HDMI touchscreen

## Features

- **WiFi Configuration**: Scan and connect to wireless networks
- **AI Mode Launcher**: Launch fullscreen Chromium in kiosk mode for the AI interface
- **System Settings**: Configure hostname and server URLs
- **Shell Access**: Drop to a shell when needed
- Clean TUI interface that works around the obscured edges of the display

## Installation

```bash
cd /home/chad/Code/squobert/squobertos
./install.sh
```

This will:
1. Install Python dependencies (textual)
2. Configure auto-login to TTY1
3. Set up auto-start of the TUI on login
4. Disable the desktop environment (switch to multi-user.target)

After installation, reboot to see SquobertOS launch automatically.

## Testing Without Rebooting

```bash
python3 squobertos.py
```

## Usage

### Main Menu
- **1. Configure WiFi**: Scan for networks and connect
- **2. Launch AI Mode**: Start Chromium in fullscreen kiosk mode
- **3. System Settings**: Edit hostname and AI server URL
- **4. Exit to Shell**: Drop to bash shell (type `exit` to return to TUI)
- **Q. Quit**: Exit the TUI

### Keyboard Shortcuts
- `1-4`: Quick access to menu items
- `q`: Quit
- `Escape`: Go back to previous screen

## Launching AI Mode

When you select "Launch AI Mode", SquobertOS will launch Chromium in fullscreen kiosk mode without requiring a desktop environment. It will:
- Start Chromium in kiosk mode (`--kiosk`)
- Disable error dialogs and info bars
- Connect to http://localhost:3000 (configurable in settings)

## Reverting to Desktop Mode

If you need to re-enable the desktop environment:

```bash
sudo systemctl set-default graphical.target
sudo reboot
```

## Accessing TTY

- TTY1: SquobertOS (auto-login)
- TTY2-6: Available via Ctrl+Alt+F2 through F6
- TTY7: Desktop (if graphical.target is enabled)

## Troubleshooting

### TUI doesn't start on boot
Check if auto-login is configured:
```bash
cat /etc/systemd/system/getty@tty1.service.d/autologin.conf
```

Check if .bashrc has the auto-start code:
```bash
grep -A5 "SquobertOS auto-start" ~/.bashrc
```

### WiFi scanning not working
Ensure NetworkManager is installed:
```bash
sudo apt install network-manager
```

### Chromium won't launch
Ensure Chromium is installed:
```bash
sudo apt install chromium-browser
```

## Development

The TUI is built with [Textual](https://textual.textualize.io/), a modern Python framework for terminal applications.

To modify the interface, edit `squobertos.py` and test with:
```bash
python3 squobertos.py
```

## File Structure

```
squobertos/
├── squobertos.py      # Main TUI application
├── requirements.txt   # Python dependencies
├── install.sh        # Installation script
├── squobertos.service # Systemd service (alternative approach)
└── README.md         # This file
```
