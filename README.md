# Raspberry Pi HMI (Tkinter)

A complete HMI (Human Machine Interface) application for Raspberry Pi OS Lite with Modbus TCP support, WiFi management, and GPIO control.

## Features

- **Splash Screen**: Displays a boot image on startup
- **Modbus TCP Polling**: Reads and displays holding registers from Modbus devices
- **WiFi Management**: Scan available networks, connect with on-screen keyboard
- **GPIO Control**: ON/OFF button to control GPIO pin 17 (customizable)
- **Auto-start**: Systemd service runs at boot as the `pi` user
- **Display Manager Support**: Waits for X11 display manager to be ready

## Project Structure

```
├── main.py              # Application entrypoint
├── gui.py               # Tkinter GUI/HMI implementation
├── modbus_client.py     # Modbus TCP polling thread
├── wifi_manager.py      # WiFi scanning and connection
├── keyboard.py          # On-screen keyboard widget
├── hmi.service          # Systemd service unit
├── install.sh           # Installation script
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Installation

### Quick Install (Recommended)

1. Clone or download the repository to your Raspberry Pi:
```bash
cd ~/hmi
```

2. Run the installation script as root:
```bash
chmod +x install.sh
sudo ./install.sh
```

This will:
- Copy files to `/opt/hmi`
- Install Python dependencies inside a virtual environment at `/opt/hmi/venv`
- Install and enable the systemd service `hmi.service`
- Start the service immediately

### Manual Setup

If you prefer manual setup:

1. Install dependencies:
```bash
# Create a virtualenv and install here (recommended):
python3 -m venv venv
venv/bin/python -m pip install --upgrade pip setuptools
venv/bin/pip install -r requirements.txt
```

2. Place a splash image named `splash.png` (800x480 recommended) in the same directory as `main.py`.

3. Run the application:
```bash
python3 main.py
```

## Configuration

### Modbus Settings

Edit `modbus_client.py` to change:
- Host IP: `host='192.168.0.100'`
- Port: `port=502`
- Poll interval: `poll_interval=1.0`

### GPIO Pin

Edit `gui.py` to change the GPIO pin used (default: BCM 17):
```python
self.gpio_pin = 17
```

### Service Management

After installation, manage the service with:

```bash
# View status
systemctl status hmi.service

# View logs
journalctl -u hmi.service -f

# Stop service
sudo systemctl stop hmi.service

# Restart service
sudo systemctl restart hmi.service

# Disable auto-start
sudo systemctl disable hmi.service
```

## Requirements

- Raspberry Pi OS Lite with GUI (`raspi-config` > System > Boot > Desktop)
- Python 3.7+
- X11 display server running
- NetworkManager or alternative WiFi tools (`iwlist`, `wpa_cli`)

### CLI-only systems (no display manager)

If your Raspberry Pi is running the CLI only (no display manager), you can start the HMI by installing a minimal X environment and enabling the provided `hmi-x.service`:

1. Install minimal X and a session launcher:

```bash
sudo apt update
sudo apt install -y xserver-xorg xinit openbox
```

2. Install the project (if not already) and enable the X service:

```bash
sudo ./install.sh
sudo cp /opt/hmi/hmi-x.service /etc/systemd/system/hmi-x.service
sudo systemctl daemon-reload
sudo systemctl enable hmi-x.service
sudo systemctl start hmi-x.service
```

This will start a minimal X session on `tty1` and run the HMI; logs are available via `journalctl -u hmi-x.service -f`.

## WiFi Connection

The application supports two methods:

1. **nmcli** (NetworkManager) - Primary method
2. **iwlist + wpa_supplicant** - Fallback method

Ensure at least one is available on your system.

## Notes

- The service runs as the `pi` user with access to GPIO via `/dev/gpiomem`
- Adjust Modbus IP/port and GPIO pins in source files before deployment
- X11 must be running; the service waits for `graphical.target`
- For headless mode, consider using a framebuffer or virtual display
