"""On-demand local view; no services are started or probed by this window."""
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText


class ServiceDiagnosticsWindow:
    def __init__(self, parent, *, get_report):
        self.get_report = get_report
        self.window = tk.Toplevel(parent)
        self.window.title('Jarvis // Diagnostica servizi')
        self.window.geometry('780x580')
        self.window.minsize(540, 360)
        frame = ttk.Frame(self.window, padding=12)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Stato osservato e ultimi eventi',
                  font=('Segoe UI', 12, 'bold')).pack(anchor='w')
        ttk.Label(frame,text='Aggiornamento a richiesta. Non modifica servizi, account o impostazioni.',
                  wraplength=700).pack(anchor='w',pady=6)
        self.text = ScrolledText(frame,wrap='word',height=20)
        self.text.pack(fill='both',expand=True)
        buttons=ttk.Frame(frame);buttons.pack(fill='x',pady=8)
        ttk.Button(buttons,text='Aggiorna',command=self.refresh).pack(side='left')
        ttk.Button(buttons,text='Copia rapporto',command=self.copy_report).pack(side='left',padx=8)
        ttk.Button(buttons,text='Chiudi',command=self.window.destroy).pack(side='right')
        self.window.bind('<Escape>',lambda _:self.window.destroy())
        self.refresh()

    def refresh(self):
        try:
            report=self.get_report()
            if not isinstance(report,str):
                raise ValueError('invalid diagnostic report')
        except Exception:
            report='Diagnostica non disponibile. Nessun servizio è stato modificato. Riprova con Aggiorna.'
        self.text.configure(state='normal')
        self.text.delete('1.0','end');self.text.insert('1.0',report)
        self.text.configure(state='disabled')

    def copy_report(self):
        self.window.clipboard_clear()
        self.window.clipboard_append(self.text.get('1.0','end-1c'))
