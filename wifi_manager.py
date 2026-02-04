import subprocess
import shlex

def scan_wifi():
    """Try `nmcli` first, then fallback to `iwlist` parsing. Returns list of dicts with ssid and signal."""
    try:
        out = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SIGNAL', 'device', 'wifi', 'list'], stderr=subprocess.DEVNULL, text=True)
        networks = []
        for line in out.splitlines():
            if not line.strip():
                continue
            parts = line.split(':')
            ssid = parts[0]
            sig = parts[1] if len(parts) > 1 else ''
            networks.append({'ssid': ssid, 'signal': sig})
        return networks
    except Exception:
        pass

    # fallback to iwlist
    try:
        out = subprocess.check_output(['sudo', 'iwlist', 'wlan0', 'scan'], stderr=subprocess.DEVNULL, text=True)
        networks = []
        current = {}
        for line in out.splitlines():
            line = line.strip()
            if line.startswith('ESSID:'):
                essid = line.split(':',1)[1].strip().strip('"')
                current['ssid'] = essid
                networks.append(dict(current))
                current = {}
            if 'Signal level' in line:
                # crude parse
                try:
                    sl = line.split('Signal level=')[-1]
                    current['signal'] = sl
                except Exception:
                    pass
        return networks
    except Exception:
        return []

def connect_nmcli(ssid, password):
    try:
        subprocess.check_call(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', password])
        return True
    except Exception:
        return False

def connect_wpa(ssid, password):
    # Write a basic wpa_supplicant entry and reconfigure
    conf = f'network={{\n    ssid="{ssid}"\n    psk="{password}"\n}}\n'
    try:
        with open('/etc/wpa_supplicant/wpa_supplicant.conf','a') as f:
            f.write(conf)
        subprocess.check_call(['sudo','wpa_cli','-i','wlan0','reconfigure'])
        return True
    except Exception:
        return False

def connect(ssid, password):
    if connect_nmcli(ssid, password):
        return True
    return connect_wpa(ssid, password)
