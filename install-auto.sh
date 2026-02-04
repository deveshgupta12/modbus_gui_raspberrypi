#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "This installer must be run as root: sudo ./install.sh"
  exit 1
fi

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR=/opt/hmi

echo "========================================="
echo "HMI Installation Script"
echo "========================================="
echo ""

echo "Installing HMI to $DEST_DIR"
rm -rf "$DEST_DIR"
mkdir -p "$DEST_DIR"
cp -a "$SRC_DIR"/* "$DEST_DIR/"

# Install python requirements
if command -v python3 >/dev/null 2>&1; then
  echo "Checking for pip..."
  if python3 -m pip --version >/dev/null 2>&1; then
    echo "pip is available"
  else
    echo "pip not found, attempting to bootstrap with ensurepip..."
    if python3 -m ensurepip --upgrade >/dev/null 2>&1; then
      echo "ensurepip succeeded"
    else
      echo "ensurepip failed, installing python3-pip via apt"
      apt-get update
      DEBIAN_FRONTEND=noninteractive apt-get install -y python3-pip
    fi

    if ! python3 -m pip --version >/dev/null 2>&1; then
      echo "pip installation failed; please install pip manually and re-run the installer"
      exit 1
    fi
  fi

  echo "Installing Python requirements..."
  VENV_DIR="$DEST_DIR/venv"
  echo "Creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR" || {
    echo "python3-venv not available, installing..."
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv
    python3 -m venv "$VENV_DIR"
  }

  echo "Upgrading pip inside venv and installing requirements"
  "$VENV_DIR/bin/python3" -m pip install --upgrade pip setuptools
  "$VENV_DIR/bin/pip" install -r "$DEST_DIR/requirements.txt"
else
  echo "python3 not found - please install Python 3"
  exit 1
fi

echo ""
echo "========================================="
echo "Detecting display environment..."
echo "========================================="

HAS_DISPLAY_MANAGER=0

if systemctl is-enabled display-manager.service >/dev/null 2>&1 || \
   systemctl is-enabled lightdm.service >/dev/null 2>&1 || \
   systemctl is-enabled xdm.service >/dev/null 2>&1 || \
   systemctl is-enabled slim.service >/dev/null 2>&1 || \
   systemctl is-enabled gdm.service >/dev/null 2>&1 || \
   systemctl is-enabled sddm.service >/dev/null 2>&1; then
  HAS_DISPLAY_MANAGER=1
  echo "Display manager detected"
else
  echo "CLI-only system detected"
  echo "Installing minimal X environment (xserver-xorg, xinit, openbox)..."
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y xserver-xorg xinit openbox
  echo "X environment installed"
fi

echo ""
echo "========================================="
echo "Installing systemd service..."
echo "========================================="

if [ "$HAS_DISPLAY_MANAGER" -eq 1 ]; then
  SERVICE_FILE="hmi.service"
  echo "Using standard GUI service (hmi.service)"
else
  SERVICE_FILE="hmi-x.service"
  echo "Using CLI X service (hmi-x.service) with xinit"
fi

if [ -f "$DEST_DIR/$SERVICE_FILE" ]; then
  cp "$DEST_DIR/$SERVICE_FILE" "/etc/systemd/system/$SERVICE_FILE"
  systemctl daemon-reload
  systemctl enable "$SERVICE_FILE"
  
  if systemctl start "$SERVICE_FILE" 2>/dev/null; then
    echo "Service $SERVICE_FILE started successfully"
  else
    echo "Failed to start $SERVICE_FILE immediately (normal on first install)"
    echo "The service will start at next reboot or manually:"
    echo "sudo systemctl start $SERVICE_FILE"
  fi
  
  echo "Service $SERVICE_FILE installed and enabled for auto-start"
else
  echo "$SERVICE_FILE not found in $DEST_DIR, skipping service installation."
  exit 1
fi

chown -R pi:pi "$DEST_DIR"

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "Service: $SERVICE_FILE"
echo "Status: sudo systemctl status $SERVICE_FILE"
echo "Logs: journalctl -u $SERVICE_FILE -f"
echo "Stop: sudo systemctl stop $SERVICE_FILE"
echo "Restart: sudo systemctl restart $SERVICE_FILE"
echo ""
echo "To uninstall, run: sudo ./uninstall.sh"
echo ""
