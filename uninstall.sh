#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "This uninstaller must be run as root: sudo ./uninstall.sh"
  exit 1
fi

SERVICE_NAME=hmi.service
SERVICE_PATH=/etc/systemd/system/${SERVICE_NAME}
INSTALL_DIR=/opt/hmi

echo "Stopping and disabling ${SERVICE_NAME} if present..."
if systemctl list-unit-files | grep -q "^${SERVICE_NAME}"; then
  if systemctl is-active --quiet ${SERVICE_NAME}; then
    systemctl stop ${SERVICE_NAME} || true
  fi
  if systemctl is-enabled --quiet ${SERVICE_NAME}; then
    systemctl disable ${SERVICE_NAME} || true
  fi
fi

if [ -f "${SERVICE_PATH}" ]; then
  echo "Removing service unit ${SERVICE_PATH}"
  rm -f "${SERVICE_PATH}"
fi

echo "Reloading systemd daemon"
systemctl daemon-reload
systemctl reset-failed || true

if [ -d "${INSTALL_DIR}" ]; then
  echo "Removing installation directory ${INSTALL_DIR}"
  rm -rf "${INSTALL_DIR}"
fi

echo "Uninstall complete. You may review logs with:"
echo "  journalctl -u ${SERVICE_NAME} --no-pager"
echo "To remove journal logs for the unit, run as root (optional):"
echo "  journalctl --vacuum-time=1s"

exit 0
