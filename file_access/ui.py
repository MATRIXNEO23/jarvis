"""On-demand folder checkboxes and a read-only viewer, using existing Tk."""
from __future__ import annotations
import os
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from .policy import contains
from .windows import drives, known_folder


class FolderSettings:
    def __init__(self, parent, service, on_change=lambda: None):
        self.service = service
        self.on_change = on_change
        self.rules = {str(Path(r['path'])): r['allow'] for r in service.policy.rules()}
        self.paths = {}
        self.loaded = set()
        self.loading = set()
        self.events = queue.Queue()
        self.alive = True
        self.window = tk.Toplevel(parent)
        self.window.title('Jarvis — Accesso file / cartelle consentite')
        self.window.geometry('780x540')
        box = ttk.Frame(self.window, padding=12)
        box.pack(fill='both', expand=True)
        ttk.Label(box, text='Scegli dischi o cartelle. Sottocartelle incluse; togli solo le eccezioni.',
                  wraplength=740).pack(anchor='w')
        ttk.Label(box, text='Solo lettura. Le spunte non cambiano i permessi di Windows.').pack(anchor='w', pady=5)
        self.tree = ttk.Treeview(box, show='tree', selectmode='browse')
        self.tree.pack(fill='both', expand=True)
        self.status = tk.StringVar(value=service.policy.error or '')
        ttk.Label(box, textvariable=self.status, wraplength=740).pack(fill='x', pady=6)
        controls = ttk.Frame(box)
        controls.pack(fill='x')
        for title, command in (('Aggiungi cartella…', self.add_folder),
                               ('Spunta / Escludi', self.toggle),
                               ('Togli regola', self.remove_rule),
                               ('Salva', self.save)):
            ttk.Button(controls, text=title, command=command).pack(side='left', padx=(0, 5))
        ttk.Button(controls, text='Chiudi', command=self.close).pack(side='right')
        roots = list(drives())
        for name in ('profilo', 'documenti', 'download', 'desktop'):
            try:
                path = known_folder(name)
                if path not in roots:
                    roots.append(path)
            except OSError:
                pass
        for name in self.rules:
            if Path(name) not in roots:
                roots.append(Path(name))
        for root in roots:
            self.insert('', root)
        self.tree.bind('<<TreeviewOpen>>', self.expand)
        self.tree.bind('<Double-1>', lambda _event: self.toggle())
        self.tree.bind('<space>', lambda _event: self.toggle())
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.window.after(100, self.poll)
        self.update_labels()

    def mark(self, path):
        matches = [(Path(p), allow) for p, allow in self.rules.items() if contains(Path(p), path)]
        allowed = max(matches, key=lambda item: len(item[0].parts))[1] if matches else False
        children = [a for p, a in self.rules.items() if Path(p) != path and contains(path, Path(p))]
        if any(a != allowed for a in children):
            return '◩'
        return '☑' if allowed else '☐'

    def insert(self, parent, path):
        ident = self.tree.insert(parent, 'end', text='')
        self.paths[ident] = path
        self.tree.item(ident, text=self.mark(path)+' '+(str(path) if not parent else path.name))
        # Child data is read only when the user expands, not during setup.
        self.tree.insert(ident, 'end', text='Espandi per caricare…')
        return ident

    def update_labels(self):
        for ident, path in self.paths.items():
            parent = self.tree.parent(ident)
            self.tree.item(ident, text=self.mark(path)+' '+(str(path) if not parent else path.name))
        allowed = sum(v for v in self.rules.values())
        excluded = len(self.rules)-allowed
        self.status.set(f'{allowed} cartelle/dischi inclusi, {excluded} eccezioni. Solo lettura. Premi Salva per applicare.')

    def toggle(self):
        selection = self.tree.selection()
        if not selection or selection[0] not in self.paths:
            return
        path = self.paths[selection[0]]
        # Toggling parent updates inherited state, preserving explicit exceptions.
        current = self.mark(path)
        self.rules[str(path)] = current != '☑'
        self.update_labels()

    def remove_rule(self):
        selection = self.tree.selection()
        if selection and selection[0] in self.paths:
            self.rules.pop(str(self.paths[selection[0]]), None)
            self.update_labels()

    def add_folder(self):
        value = filedialog.askdirectory(parent=self.window, title='Scegli una cartella da consentire')
        if value:
            path = Path(value)
            self.rules[str(path)] = True
            self.insert('', path)
            self.update_labels()

    def expand(self, _event=None):
        ident = self.tree.focus()
        if ident not in self.paths or ident in self.loaded or ident in self.loading:
            return
        self.loading.add(ident)
        path = self.paths[ident]
        def worker():
            result, error = [], ''
            try:
                with os.scandir(path) as entries:
                    for entry in entries:
                        if entry.is_dir(follow_symlinks=False):
                            result.append(Path(entry.path))
                            if len(result) >= 200:
                                error = 'Mostrate le prime 200 cartelle: usa Aggiungi cartella per selezionarne un’altra.'
                                break
            except OSError as exc:
                error = 'Cartella non leggibile: '+str(exc)[:120]
            self.events.put((ident, sorted(result, key=lambda p: p.name.casefold()), error))
        threading.Thread(target=worker, daemon=True, name='jarvis-folder-list').start()

    def poll(self):
        if not self.alive:
            return
        try:
            while True:
                ident, paths, error = self.events.get_nowait()
                self.loading.discard(ident)
                self.loaded.add(ident)
                for child in self.tree.get_children(ident):
                    self.tree.delete(child)
                for path in paths:
                    self.insert(ident, path)
                if error:
                    self.status.set(error)
        except queue.Empty:
            pass
        self.window.after(100, self.poll)

    def save(self):
        try:
            self.service.policy.configure(list(self.rules.items()))
            self.service.reset(self.service._context)
            self.on_change()
            self.status.set('Scelte salvate. Accesso in sola lettura; attiva l’add-on nel pannello se è spento.')
        except (OSError, ValueError) as exc:
            messagebox.showerror('Accesso file', str(exc), parent=self.window)

    def close(self):
        self.alive = False
        self.window.destroy()


def show_preview(parent, path, text):
    window = tk.Toplevel(parent)
    window.title('Jarvis — lettura senza modifica: '+Path(path).name)
    window.geometry('780x550')
    ttk.Label(window, text=path, wraplength=750).pack(fill='x', padx=10, pady=8)
    area = tk.Text(window, wrap='word')
    area.insert('1.0', text)
    area.configure(state='disabled')
    area.pack(fill='both', expand=True, padx=10)
    ttk.Button(window, text='Chiudi', command=window.destroy).pack(pady=8)
    return window
