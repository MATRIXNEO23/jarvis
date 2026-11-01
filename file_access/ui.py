"""On-demand folder checkboxes and a read-only viewer, using existing Tk."""
from __future__ import annotations
import os
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from .policy import contains
from .windows import drives, known_folder, long_path


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
        try:
            path = long_path(path)
        except OSError:
            pass
        matches = [(Path(p), allow) for p, allow in self.rules.items() if contains(Path(p), path)]
        allowed = max(matches, key=lambda item: len(item[0].parts))[1] if matches else False
        children = [a for p, a in self.rules.items() if Path(p) != path and contains(path, Path(p))]
        if any(a != allowed for a in children):
            return '◩'
        return '☑' if allowed else '☐'

    def insert(self, parent, path):
        try:
            path = long_path(path)
        except OSError:
            pass
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
        matches = [(Path(p), allow) for p, allow in self.rules.items() if contains(Path(p), path)]
        current = max(matches, key=lambda item: len(item[0].parts))[1] if matches else False
        self.rules[str(path)] = not current
        self.update_labels()

    def remove_rule(self):
        selection = self.tree.selection()
        if selection and selection[0] in self.paths:
            self.rules.pop(str(self.paths[selection[0]]), None)
            self.update_labels()

    def add_folder(self):
        value = filedialog.askdirectory(parent=self.window, title='Scegli una cartella da consentire')
        if value:
            path = long_path(Path(value))
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


class ResultWindow:
    """One bounded, nonmodal result view; all actions return to the existing worker."""
    def __init__(self,parent,listing,on_open,on_select):
        self.window=tk.Toplevel(parent)
        self.window.title('Jarvis — risultati file e cartelle')
        self.window.geometry('900x460')
        box=ttk.Frame(self.window,padding=10)
        box.pack(fill='both',expand=True)
        self.status=tk.StringVar()
        ttk.Label(box,textvariable=self.status,wraplength=860).pack(fill='x',pady=(0,8))
        table=ttk.Frame(box)
        table.pack(fill='both',expand=True)
        self.tree=ttk.Treeview(table,columns=('number','kind','name','path'),show='headings',selectmode='browse')
        for key,label,width in (('number','N.',45),('kind','Tipo',80),('name','Nome',210),('path','Percorso',500)):
            self.tree.heading(key,text=label)
            self.tree.column(key,width=width,minwidth=40,stretch=key=='path')
        vertical=ttk.Scrollbar(table,orient='vertical',command=self.tree.yview)
        horizontal=ttk.Scrollbar(table,orient='horizontal',command=self.tree.xview)
        self.tree.configure(yscrollcommand=vertical.set,xscrollcommand=horizontal.set)
        self.tree.grid(row=0,column=0,sticky='nsew')
        vertical.grid(row=0,column=1,sticky='ns')
        horizontal.grid(row=1,column=0,sticky='ew')
        table.rowconfigure(0,weight=1); table.columnconfigure(0,weight=1)
        ttk.Label(box,text='Scegli una riga o indica il numero a voce. Doppio clic / Invio: apri o continua la richiesta.',wraplength=860).pack(fill='x',pady=8)
        self.open_button=ttk.Button(box,text='Apri / continua',command=self.open_selected)
        self.open_button.pack(side='left')
        ttk.Button(box,text='Chiudi',command=self.window.destroy).pack(side='right')
        self.tree.bind('<<TreeviewSelect>>',self.select)
        self.tree.bind('<Double-1>',self.open_selected)
        self.tree.bind('<Return>',self.open_selected)
        self.update(listing,on_open,on_select)

    def update(self,listing,on_open,on_select):
        self.listing=listing
        self.on_open=on_open; self.on_select=on_select
        self.tree.delete(*self.tree.get_children())
        for number,item in enumerate(listing['items'],1):
            self.tree.insert('', 'end',iid=str(number),values=(number,*item))
        self.status.set(listing['summary'])
        self.open_button.configure(state='disabled')
        self.window.update_idletasks()
        if not self.on_select(None,listing['token'],self.window.winfo_id()):
            self.status.set('Elenco scaduto o sostituito: ripeti la ricerca o aggiorna l’elenco.')
        elif len(listing['items'])==1:
            self.tree.selection_set('1')
            self.select()

    def select(self,_event=None):
        selected=self.tree.selection()
        number=int(selected[0]) if selected else None
        valid=self.on_select(number,self.listing['token'],self.window.winfo_id())
        self.open_button.configure(state='normal' if selected and valid else 'disabled')
        if not valid:
            self.status.set('Elenco scaduto o sostituito: ripeti la ricerca o aggiorna l’elenco.')

    def open_selected(self,_event=None):
        self.select()
        selected=self.tree.selection()
        if selected and str(self.open_button.cget('state'))!='disabled':
            self.on_open(int(selected[0]),self.listing['token'])
        return 'break'


def show_results(parent,listing,on_open,on_select):
    view=getattr(parent,'_jarvis_file_results',None)
    if view is None or not view.window.winfo_exists():
        view=ResultWindow(parent,listing,on_open,on_select)
        parent._jarvis_file_results=view
    else:
        view.update(listing,on_open,on_select)
    view.window.deiconify()
    view.window.lift()
    return view


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
