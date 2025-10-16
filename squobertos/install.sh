#!/bin/bash
# SquobertOS Installation Script

set -e

echo "🤖 Installing SquobertOS..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  echo "❌ Please do not run this script as root. Run as your normal user."
  exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install Python dependencies using uv
echo "📦 Installing Python dependencies with uv..."
cd "$SCRIPT_DIR"
uv sync

# Make the main script executable
echo "🔧 Making squobertos.py executable..."
chmod +x "$SCRIPT_DIR/squobertos.py"

# Configure auto-login to TTY1
echo "🔑 Configuring auto-login to TTY1..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d/
sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf >/dev/null <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin $USER --noclear %I \$TERM
EOF

# Add auto-start to .bashrc for TTY1 only
echo "🚀 Configuring auto-start in .bashrc..."
if ! grep -q "# SquobertOS auto-start" ~/.bashrc; then
  cat >>~/.bashrc <<EOF

# SquobertOS auto-start
if [ "$(tty)" = "/dev/tty1" ] || [ "$(tty)" = "/dev/pts/0" ]; then
    cd $HOME/Code/squobert/squobertos
    uv run python squobertos.py
fi
EOF
fi

# Disable graphical target (desktop environment)
echo "🖥️  Disabling desktop environment..."
sudo systemctl set-default multi-user.target

echo ""
echo "✅ SquobertOS installation complete!"
echo ""
echo "On next boot, your Pi will:"
echo "  1. Boot to TTY1 (no desktop)"
echo "  2. Auto-login as $USER"
echo "  3. Launch the SquobertOS TUI"
echo ""
echo "To test now without rebooting, run:"
echo "  cd $SCRIPT_DIR && uv run python squobertos.py"
echo ""
echo "To revert and re-enable desktop:"
echo "  sudo systemctl set-default graphical.target"
echo ""
