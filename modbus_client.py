import threading
import time
from pymodbus.client.sync import ModbusTcpClient

class ModbusPoller(threading.Thread):
    def __init__(self, host='192.168.0.100', port=502, poll_interval=1.0, unit=1):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.poll_interval = poll_interval
        self.unit = unit
        self._client = ModbusTcpClient(host, port=port)
        self._stop = threading.Event()
        self.lock = threading.Lock()
        self.data = {}

    def run(self):
        if not self._client.connect():
            # keep trying
            while not self._stop.is_set():
                if self._client.connect():
                    break
                time.sleep(5)

        while not self._stop.is_set():
            try:
                # example: read 10 holding registers starting at 0
                rr = self._client.read_holding_registers(0, 10, unit=self.unit)
                if not rr.isError():
                    with self.lock:
                        self.data = {'regs': list(rr.registers)}
            except Exception:
                pass
            time.sleep(self.poll_interval)

    def stop(self):
        self._stop.set()
        try:
            self._client.close()
        except Exception:
            pass

    def get_data(self):
        with self.lock:
            return dict(self.data)
