# Raspberry Pi HMI (Tkinter)

This project is a minimal HMI (GUI) for Raspberry Pi OS Lite.

Features
- Splash screen on startup (place `splash.png` next to `main.py`).
- Polls Modbus TCP registers and displays them.
- Settings screen: scan WiFi, connect using `nmcli` or fallback.
- On-screen keyboard for password entry.
- On-screen GPIO ON/OFF button (controls BCM 17).

Setup
1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Place a splash image named `splash.png` (800x480 recommended) next to `main.py`.

3. Run as root for GPIO and network access if needed:

```bash
sudo python3 main.py
```

Notes
- WiFi functions try `nmcli` first. Ensure `NetworkManager` is installed or the fallback `iwlist` and `wpa_cli` are available.
- Adjust Modbus host/port in `modbus_client.ModbusPoller` or extend UI to change settings.
