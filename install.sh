#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "This installer must be run as root: sudo ./install.sh"
  exit 1
fi

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR=/opt/hmi

echo "Installing HMI to $DEST_DIR"
rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"
cp -a "$SRC_DIR"/* "$DEST_DIR/"

# Install python requirements
if command -v python3 >/dev/null 2>&1; then
  python3 -m pip install -r "$DEST_DIR/requirements.txt"
else
  echo "python3 not found - please install Python 3"
  exit 1
fi

# Install systemd service
if [ -f "$DEST_DIR/hmi.service" ]; then
  cp "$DEST_DIR/hmi.service" /etc/systemd/system/hmi.service
  systemctl daemon-reload
  systemctl enable hmi.service
  systemctl restart hmi.service || systemctl start hmi.service
  echo "Service hmi.service installed and started."
else
  echo "hmi.service not found in $DEST_DIR, skipping service installation."
fi

chown -R pi:pi "$DEST_DIR"

echo "Installation complete. To view logs: journalctl -u hmi.service -f"
