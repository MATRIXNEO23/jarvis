"""«Le mie parole»: accanto a ogni comando esistente, la casella per le tue frasi.

Usato da Impostazioni > Personalizzazione comandi (comandi di base) e da
Gestisci add-on (comandi di ciascun add-on). F1 resta solo una guida.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import command_aliases


class AliasPanel(ttk.Frame):
    """Una riga per comando: comando, cosa fa, le tue frasi, «Aggiungi» e «Gestisci».
    Le tue frasi si sommano al comando standard, che funziona sempre."""

    def __init__(self, parent, section, engine=None, height=220):
        super().__init__(parent, padding=(8, 4))
        self.section = section
        self.engine = engine
        ttk.Label(self, text='Le mie parole: «Aggiungi» un altro modo di dire il comando; '
                             '«Gestisci» per vedere, modificare o eliminare le tue frasi una alla '
                             'volta. Il comando standard resta sempre valido. «…» = parte variabile.',
                  wraplength=720).pack(anchor='w')
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
        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status, wraplength=700).pack(anchor='w')
        self.fill()

    def fill(self):
        for child in self.grid_frame.winfo_children():
            child.destroy()
        commands = command_aliases.catalog(self.engine).get(self.section, [])
        if not commands:
            ttk.Label(self.grid_frame, text='Nessun comando ancora: configura prima '
                                            'questo componente.').grid(row=0, column=0, sticky='w')
            return
        for col, title in enumerate(('Comando', 'Cosa fa', 'Le mie parole')):
            ttk.Label(self.grid_frame, text=title, font=('Segoe UI', 9, 'bold')).grid(
                row=0, column=col, sticky='w', padx=(0, 10))
        items = command_aliases.load()
        for row, command in enumerate(commands, start=1):
            mine = [p.replace(' {testo}', ' …').replace('{testo}', '…')
                    for p in command_aliases.phrases_for(command, items)]
            ttk.Label(self.grid_frame, text=command.replace('{testo}', '…')).grid(
                row=row, column=0, sticky='w', padx=(0, 10), pady=1)
            ttk.Label(self.grid_frame, text=command_aliases.describe(command), wraplength=230,
                      foreground='#7fb8cc').grid(row=row, column=1, sticky='w', padx=(0, 10))
            summary = '; '.join(mine) if mine else '—'
            ttk.Label(self.grid_frame, text=summary[:60] + ('…' if len(summary) > 60 else ''),
                      wraplength=220).grid(row=row, column=2, sticky='w', padx=(0, 6))
            ttk.Button(self.grid_frame, text='Aggiungi', width=9,
                       command=lambda c=command: self.add(c)).grid(row=row, column=3, padx=2)
            manage = ttk.Button(self.grid_frame, text='Gestisci', width=9,
                                command=lambda c=command: self.manage(c))
            manage.grid(row=row, column=4, padx=2)
            if not mine:
                manage.state(['disabled'])

    def _ask_text(self, title, prompt, initial=''):
        from tkinter import simpledialog
        return simpledialog.askstring(title, prompt, initialvalue=initial, parent=self)

    def add(self, command):
        text = self._ask_text('Aggiungi un modo di dirlo',
                              f'Nuova frase per «{command.replace("{testo}", "…")}»'
                              + (' (la parte variabile va in fondo da sola)' if '{testo}' in command else '')
                              + ':')
        if text:
            try:
                self.status.set(command_aliases.add_phrase(self.section, command,
                                                           text.replace('…', '{testo}')))
            except OSError as exc:
                self.status.set('Non salvato: ' + str(exc)[:80])
            self.fill()

    def manage(self, command):
        dialog = tk.Toplevel(self)
        dialog.title('Le mie frasi')
        dialog.transient(self.winfo_toplevel())
        body = ttk.Frame(dialog, padding=10)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text=f'Comando: «{command.replace("{testo}", "…")}» (predefinito, sempre valido)'
                  ).pack(anchor='w')
        listbox = tk.Listbox(body, height=8, width=50)
        listbox.pack(fill='both', expand=True, pady=6)

        def refill():
            listbox.delete(0, 'end')
            for phrase in command_aliases.phrases_for(command):
                listbox.insert('end', phrase.replace('{testo}', '…') + '   (tua)')
        refill()

        def chosen():
            sel = listbox.curselection()
            phrases = command_aliases.phrases_for(command)
            return phrases[sel[0]] if sel and sel[0] < len(phrases) else None

        def edit():
            old = chosen()
            if old is None:
                return
            new = self._ask_text('Modifica', 'Nuova frase:', old.replace('{testo}', '…'))
            if new:
                self.status.set(command_aliases.edit_phrase(old, new.replace('…', '{testo}')))
                refill()
                self.fill()

        def delete():
            old = chosen()
            if old is None:
                return
            self.status.set(command_aliases.remove_phrase(old))
            refill()
            self.fill()
        row = ttk.Frame(body)
        row.pack(fill='x')
        ttk.Button(row, text='Modifica', command=edit).pack(side='left')
        ttk.Button(row, text='Elimina', command=delete).pack(side='left', padx=6)
        ttk.Button(row, text='Chiudi', command=dialog.destroy).pack(side='right')


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
