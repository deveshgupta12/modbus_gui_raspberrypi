import tkinter as tk

class OnScreenKeyboard(tk.Toplevel):
    def __init__(self, master, entry_widget, **kwargs):
        super().__init__(master, **kwargs)
        self.title('Keyboard')
        self.entry = entry_widget
        keys = [
            list('1234567890'),
            list('qwertyuiop'),
            list('asdfghjkl'),
            list('zxcvbnm'),
        ]
        for r, row in enumerate(keys):
            for c, ch in enumerate(row):
                b = tk.Button(self, text=ch, width=3, command=lambda ch=ch: self._press(ch))
                b.grid(row=r, column=c)
        tk.Button(self, text='Space', width=10, command=lambda: self._press(' ')).grid(row=4, column=0, columnspan=5)
        tk.Button(self, text='Back', width=5, command=self._back).grid(row=4, column=5)

    def _press(self, ch):
        self.entry.insert('end', ch)

    def _back(self):
        s = self.entry.get()
        self.entry.delete(0, 'end')
        self.entry.insert(0, s[:-1])
