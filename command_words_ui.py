"""«Le mie parole»: accanto a ogni comando esistente, la casella per le tue frasi.

Usato da Impostazioni > Personalizzazione comandi (comandi di base) e da
Gestisci add-on (comandi di ciascun add-on). F1 resta solo una guida.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import command_aliases


class AliasPanel(ttk.Frame):
    """Una riga per comando: comando | le mie parole (più frasi separate da «;»)."""

    def __init__(self, parent, section, engine=None, height=220):
        super().__init__(parent, padding=(8, 4))
        self.section = section
        self.engine = engine
        ttk.Label(self, text='Le mie parole: scrivi accanto al comando come vuoi dirlo '
                             '(più frasi separate da ;). Dove c’è «…» scrivi solo l’inizio. '
                             'Il comando standard resta valido.',
                  wraplength=700).pack(anchor='w')
        holder = ttk.Frame(self)
        holder.pack(fill='both', expand=True, pady=(4, 4))
        self.canvas = tk.Canvas(holder, height=height, highlightthickness=0)
        scroll = ttk.Scrollbar(holder, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.grid_frame = ttk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.grid_frame, anchor='nw')
        self.grid_frame.bind('<Configure>', lambda _e: self.canvas.configure(
            scrollregion=self.canvas.bbox('all')))
        row = ttk.Frame(self)
        row.pack(fill='x')
        ttk.Button(row, text='Salva le mie parole', command=self.save).pack(side='left')
        self.status = tk.StringVar()
        ttk.Label(row, textvariable=self.status, wraplength=520).pack(side='left', padx=8)
        self.entries = {}
        self.fill()

    def fill(self):
        for child in self.grid_frame.winfo_children():
            child.destroy()
        self.entries = {}
        commands = command_aliases.catalog(self.engine).get(self.section, [])
        if not commands:
            ttk.Label(self.grid_frame, text='Nessun comando ancora: configura prima '
                                            'questo componente.').grid(row=0, column=0, sticky='w')
            return
        ttk.Label(self.grid_frame, text='Comando', font=('Segoe UI', 9, 'bold')
                  ).grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Label(self.grid_frame, text='Le mie parole', font=('Segoe UI', 9, 'bold')
                  ).grid(row=0, column=1, sticky='w')
        for index, (command, mine) in enumerate(
                command_aliases.section_rows(self.section, commands), start=1):
            ttk.Label(self.grid_frame, text=command.replace('{testo}', '…')
                      ).grid(row=index, column=0, sticky='w', padx=(0, 10), pady=1)
            value = tk.StringVar(value=mine.replace(' {testo}', '').replace('{testo}', '…'))
            ttk.Entry(self.grid_frame, textvariable=value, width=40
                      ).grid(row=index, column=1, sticky='w', pady=1)
            self.entries[command] = value

    def save(self):
        values = {command: var.get().replace('…', '{testo}')
                  for command, var in self.entries.items()}
        wanted = sum(1 for v in values.values() for p in v.split(';') if p.strip())
        items = command_aliases.replace_section(self.section, values)
        try:
            command_aliases.save(items)
        except OSError as exc:
            self.status.set('Non salvato: ' + str(exc)[:80])
            return
        mine = sum(1 for i in items if i['command'] in values)
        lost = wanted - mine
        self.status.set(f'Salvato: {mine} frasi, valgono per voce e testo.' +
                        (f' {lost} già usate per un altro comando: non aggiunte.' if lost > 0 else ''))
        self.fill()


class CommandWordsWindow:
    """Impostazioni > Personalizzazione comandi: solo i comandi di base."""

    def __init__(self, parent, engine=None):
        self.window = tk.Toplevel(parent)
        self.window.title('LUMI // Personalizzazione comandi')
        self.window.geometry('780x560')
        frame = ttk.Frame(self.window, padding=10)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, wraplength=740, text=(
            'Comandi di base di Lumi. I comandi degli add-on (Musica, Controllo PC, '
            'Programmi e app…) si personalizzano in Gestisci add-on, nella sezione di '
            'ciascun add-on.')).pack(anchor='w', pady=(0, 6))
        tabs = ttk.Notebook(frame)
        tabs.pack(fill='both', expand=True)
        for section in command_aliases.BASE_SECTIONS:
            tab = ttk.Frame(tabs)
            tabs.add(tab, text=section)
            AliasPanel(tab, section, engine, height=330).pack(fill='both', expand=True)
        tab = ttk.Frame(tabs)
        tabs.add(tab, text='Sinonimi')
        SynonymsPanel(tab).pack(fill='both', expand=True)
        ttk.Button(frame, text='Chiudi', command=self.window.destroy).pack(anchor='e', pady=(6, 0))

    def exists(self):
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False

    def focus(self):
        self.window.deiconify()
        self.window.lift()


class SynonymsPanel(ttk.Frame):
    """Parole tue che valgono come un verbo che Lumi conosce (es. «spara» = «imposta»).
    Si usano prima del modello per capire i comandi detti in modo diverso."""

    def __init__(self, parent):
        super().__init__(parent, padding=8)
        import intent_normalizer
        self.normalizer = intent_normalizer
        ttk.Label(self, wraplength=700, text=(
            'Lumi capisce già molti sinonimi (attiva/avvia/metti = imposta, stoppa/spegni = '
            'ferma, aumenta = alza…). Qui aggiungi i tuoi: scrivi la parola e scegli il verbo '
            'che deve valere.')).pack(anchor='w')
        self.tree = ttk.Treeview(self, columns=('word', 'base'), show='headings', height=10)
        self.tree.heading('word', text='Quando dico')
        self.tree.heading('base', text='Vale come')
        self.tree.pack(fill='both', expand=True, pady=6)
        row = ttk.Frame(self)
        row.pack(fill='x')
        self.word = tk.StringVar()
        self.base = tk.StringVar(value='imposta')
        ttk.Entry(row, textvariable=self.word, width=24).pack(side='left')
        ttk.Label(row, text=' = ').pack(side='left')
        ttk.Combobox(row, textvariable=self.base, width=14, state='readonly',
                     values=sorted(intent_normalizer.SYNONYMS)).pack(side='left')
        ttk.Button(row, text='Aggiungi', command=self.add).pack(side='left', padx=6)
        ttk.Button(row, text='Togli', command=self.remove).pack(side='left')
        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status).pack(anchor='w', pady=(4, 0))
        self.fill()

    def fill(self):
        self.tree.delete(*self.tree.get_children())
        for word, base in sorted(self.normalizer.load_extra().items()):
            self.tree.insert('', 'end', values=(word, base))

    def _save(self, extra, message):
        try:
            self.normalizer.save_extra(extra)
        except OSError as exc:
            self.status.set('Non salvato: ' + str(exc)[:80])
            return
        self.status.set(message)
        self.fill()

    def add(self):
        word = ' '.join(self.word.get().lower().split())
        if not word:
            self.status.set('Scrivi la parola.')
            return
        extra = dict(self.normalizer.load_extra())
        extra[word] = self.base.get()
        self.word.set('')
        self._save(extra, f'«{word}» ora vale come «{self.base.get()}».')

    def remove(self):
        selected = self.tree.selection()
        if not selected:
            self.status.set('Scegli una riga.')
            return
        word = self.tree.item(selected[0], 'values')[0]
        extra = {k: v for k, v in self.normalizer.load_extra().items() if k != word}
        self._save(extra, 'Tolto.')
