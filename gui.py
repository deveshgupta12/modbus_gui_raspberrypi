import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import os
import time
from modbus_client import ModbusPoller
from wifi_manager import scan_wifi, connect
from keyboard import OnScreenKeyboard

try:
    import RPi.GPIO as GPIO
except Exception:
    GPIO = None

SPLASH_IMAGE = 'splash.png'  # place your image here

class HMIApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('HMI')
        self.root.geometry('800x480')
        self.modbus = ModbusPoller()
        self.modbus.start()
        self.gpio_pin = 17
        if GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio_pin, GPIO.OUT)

        self._build_splash()
        self.root.after(3000, self._build_main)

    def _build_splash(self):
        if os.path.exists(SPLASH_IMAGE):
            img = Image.open(SPLASH_IMAGE)
            img = img.resize((800, 480))
            self.splash_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(self.root, image=self.splash_img)
            lbl.place(x=0,y=0)
        else:
            lbl = tk.Label(self.root, text='Starting...', font=('Helvetica',24))
            lbl.pack(expand=True)

    def _build_main(self):
        for w in self.root.winfo_children():
            w.destroy()

        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.param_var = tk.StringVar(value='No data')
        ttk.Label(frame, text='Modbus Registers:').grid(row=0, column=0, sticky='w')
        ttk.Label(frame, textvariable=self.param_var).grid(row=0, column=1, sticky='w')

        self.gpio_state = tk.BooleanVar(value=False)
        btn = ttk.Checkbutton(frame, text='GPIO ON/OFF', variable=self.gpio_state, command=self._toggle_gpio)
        btn.grid(row=1, column=0, sticky='w')

        settings_btn = ttk.Button(frame, text='Settings', command=self._open_settings)
        settings_btn.grid(row=1, column=1, sticky='e')

        self._update_loop()

    def _update_loop(self):
        data = self.modbus.get_data()
        self.param_var.set(str(data.get('regs', 'empty')))
        self.root.after(1000, self._update_loop)

    def _toggle_gpio(self):
        val = self.gpio_state.get()
        if GPIO:
            GPIO.output(self.gpio_pin, GPIO.HIGH if val else GPIO.LOW)
        else:
            print('GPIO toggle:', val)

    def _open_settings(self):
        s = tk.Toplevel(self.root)
        s.title('Settings')
        ttk.Label(s, text='WiFi Networks:').pack(anchor='w')
        listbox = tk.Listbox(s, height=8)
        listbox.pack(fill='x')

        def scan():
            listbox.delete(0,'end')
            nets = scan_wifi()
            for n in nets:
                listbox.insert('end', n.get('ssid') or '')

        scan_btn = ttk.Button(s, text='Scan', command=scan)
        scan_btn.pack()

        pw_entry = ttk.Entry(s, show='*')
        pw_entry.pack(fill='x')

        def show_kb():
            OnScreenKeyboard(self.root, pw_entry)

        kb_btn = ttk.Button(s, text='Keyboard', command=show_kb)
        kb_btn.pack()

        def connect_selected():
            sel = listbox.curselection()
            if not sel:
                messagebox.showinfo('Info','Select network')
                return
            ssid = listbox.get(sel[0])
            pw = pw_entry.get()
            ok = connect(ssid, pw)
            messagebox.showinfo('Result', 'Connected' if ok else 'Failed')

        connect_btn = ttk.Button(s, text='Connect', command=connect_selected)
        connect_btn.pack()

    def run(self):
        self.root.mainloop()
