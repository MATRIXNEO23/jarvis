"""Native Tk configuration; discovery runs only while explicitly requested."""
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog


class ProgramSettings:
    def __init__(self, parent, service, on_change=lambda: None):
        self.service, self.on_change = service, on_change
        self.window = tk.Toplevel(parent)
        self.window.title('Lumi — Programmi e app')
        self.window.geometry('850x560')
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.cancelled = threading.Event()
        self.events = queue.Queue()
        self._working = False
        self._dirty = False
        self._selected = None
        self._after = None
        self.rows = {}
        self.filter = tk.StringVar()
        self.phrase = tk.StringVar()
        self.status = tk.StringVar()
        self.detail = tk.StringVar()
        body = ttk.Frame(self.window, padding=12)
        body.pack(fill='both', expand=True)
        ttk.Label(body,text='Spunta le app da consentire; Salva prima di provarne l’avvio.').pack(anchor='w')
        ttk.Label(body,text='Cerca nell’elenco:').pack(anchor='w',pady=(8,0))
        self.filter_entry=ttk.Entry(body,textvariable=self.filter)
        self.filter_entry.pack(fill='x')
        table_frame = ttk.Frame(body)
        table_frame.pack(fill='both',expand=True,pady=8)
        self.table = ttk.Treeview(table_frame,columns=('enabled','name','kind','state'),show='headings',selectmode='browse')
        for key,title,width in [('enabled','Consenti avvio',95),('name','Programma',330),('kind','Tipo',90),('state','Stato',135)]:
            self.table.heading(key,text=title)
            self.table.column(key,width=width)
        scroll = ttk.Scrollbar(table_frame,orient='vertical',command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side='left',fill='both',expand=True)
        scroll.pack(side='right',fill='y')
        self.table.bind('<<TreeviewSelect>>',self.select)
        self.table.bind('<Button-1>',self.click)
        self.table.bind('<space>',self.toggle_selected)
        ttk.Label(body,textvariable=self.detail,wraplength=800).pack(anchor='w')
        ttk.Label(body,text='Comando vocale personalizzato (facoltativo):').pack(anchor='w',pady=(8,0))
        self.phrase_entry = ttk.Entry(body,textvariable=self.phrase)
        self.phrase_entry.pack(fill='x')
        self.phrase_entry.bind('<KeyRelease>',lambda event:self.changed())
        ttk.Label(body,text='Esempio: «apri la posta». Funzionano anche «avvia la posta» e il nome originale.').pack(anchor='w')
        controls = ttk.Frame(body)
        controls.pack(fill='x',pady=10)
        self.refresh_button = ttk.Button(controls,text='Aggiorna elenco',command=self.refresh)
        self.refresh_button.pack(side='left')
        ttk.Button(controls,text='Annulla aggiornamento',command=self.cancelled.set).pack(side='left',padx=4)
        self.add_button=ttk.Button(controls,text='Aggiungi programma',command=self.add)
        self.add_button.pack(side='left',padx=4)
        self.try_button=ttk.Button(controls,text='Prova avvio',command=self.try_launch)
        self.try_button.pack(side='left',padx=4)
        self.save_button=ttk.Button(controls,text='Salva',command=self.save)
        self.save_button.pack(side='right')
        ttk.Button(controls,text='Chiudi',command=self.close).pack(side='right',padx=4)
        ttk.Label(body,textvariable=self.status,wraplength=800).pack(anchor='w')
        self.filter.trace_add('write',lambda *args:self.render())
        self.reload()

    def changed(self):
        self._dirty = True

    def capture(self):
        if self._selected in self.rows:
            value = self.phrase.get().strip()
            if value != self.rows[self._selected]['phrase']:
                self._dirty = True
            self.rows[self._selected]['phrase'] = value

    def reload(self):
        self.rows = {row['id']:dict(row) for row in self.service.entries()}
        self._selected = None
        self.phrase.set('')
        self._dirty = False
        self.render()
        warnings = ' '.join(self.service.warnings)
        self.status.set(f'{len(self.rows)} applicazioni. '+(warnings or 'Premi Aggiorna elenco per rilevare le app di Windows.'))

    def render(self):
        self.capture()
        selected = self._selected
        self.table.delete(*self.table.get_children())
        query = self.filter.get().casefold().strip()
        for ident,row in self.rows.items():
            if query and query not in (row['name']+' '+row['phrase']).casefold():
                continue
            self.table.insert('', 'end',iid=ident,values=('☑' if row['enabled'] else '☐',
                row['name'],'Store' if row['kind']=='store' else 'Classica',
                'Disponibile' if row['available'] else 'Non disponibile'))
        if selected and self.table.exists(selected):
            self.table.selection_set(selected)

    def select(self,event=None):
        if self._working:
            return 'break'
        self.capture()
        selected = self.table.selection()
        self._selected = selected[0] if selected else None
        row = self.rows.get(self._selected)
        self.phrase.set(row['phrase'] if row else '')
        self.detail.set(row['target'] if row else '')

    def click(self,event):
        if self._working:
            return 'break'
        if self.table.identify_column(event.x)=='#1':
            ident = self.table.identify_row(event.y)
            if ident:
                self.table.selection_set(ident)
                self.select()
                self.toggle_selected()
                return 'break'

    def toggle_selected(self,event=None):
        if self._working:
            return 'break'
        if self._selected in self.rows:
            self.rows[self._selected]['enabled'] = not self.rows[self._selected]['enabled']
            self._dirty = True
            self.render()
        return 'break'

    def save(self):
        if self._working:
            self.status.set('Attendi il completamento o annulla l’aggiornamento.')
            return False
        self.capture()
        try:
            self.service.save_preferences({key:dict(enabled=row['enabled'],phrase=row['phrase'])
                                           for key,row in self.rows.items()})
            self._dirty = False
            self.on_change()
            self.status.set('Selezioni e comandi salvati. Le app nuove restano non consentite.')
            return True
        except (OSError,ValueError) as exc:
            self.status.set('Non salvato: '+str(exc))
            return False

    def _start(self, work):
        self.capture()
        if self._dirty:
            self.status.set('Salva prima le modifiche alla selezione e ai comandi.')
            return
        if self._working:
            self.status.set('Operazione già in corso.')
            return
        self.cancelled.clear()
        self._working = True
        self._controls_state('disabled')
        self.status.set('Operazione in corso…')
        def worker():
            try:
                self.events.put(('ok',work()))
            except (OSError,ValueError) as exc:
                self.events.put(('error',str(exc)))
        threading.Thread(target=worker,daemon=True).start()
        self._after = self.window.after(50,self._poll)

    def _poll(self):
        self._after = None
        try:
            kind,value = self.events.get_nowait()
        except queue.Empty:
            self._after = self.window.after(50,self._poll)
            return
        self._working = False
        self._controls_state('normal')
        if kind=='ok':
            self.reload()
            if isinstance(value,str):
                self.status.set(value)
        else:
            self.status.set('Operazione non completata: '+value)

    def _controls_state(self,state):
        for control in (self.refresh_button,self.add_button,self.try_button,self.save_button,
                        self.phrase_entry,self.filter_entry):
            control.configure(state=state)

    def refresh(self):
        self._start(lambda:self.service.refresh_catalog(self.cancelled))

    def add(self):
        if self._working:
            return
        path = filedialog.askopenfilename(parent=self.window,title='Scegli programma o collegamento',
                                         filetypes=[('Programma Windows','*.exe *.lnk')])
        if path:
            self._start(lambda:self.service.add_manual(path) and 'Programma aggiunto, ancora non consentito. Spunta e salva.')

    def try_launch(self):
        ident = self._selected
        if ident is None:
            self.status.set('Seleziona un programma.')
            return
        def launch_and_report():
            result = self.service.execute('launch_id', {'query':ident})
            if result.status != 'completed':
                return 'Avvio non riuscito: ' + result.message
            return result.message
        self._start(launch_and_report)

    def close(self):
        self.cancelled.set()
        if self._after is not None:
            self.window.after_cancel(self._after)
        self.window.destroy()


def show_choices(parent, listing, on_select):
    previous = getattr(parent,'_program_choices',None)
    if previous is not None and previous.winfo_exists():
        previous.destroy()
    window = tk.Toplevel(parent)
    parent._program_choices = window
    window.title('Lumi — Scegli programma da avviare')
    window.geometry('760x350')
    table = ttk.Treeview(window,columns=('number','name','target'),show='headings')
    for key,title in [('number','N.'),('name','Programma'),('target','Destinazione')]:
        table.heading(key,text=title)
    table.column('number',width=45,stretch=False)
    table.pack(side='left',fill='both',expand=True)
    scroll = ttk.Scrollbar(window,orient='vertical',command=table.yview)
    scroll.pack(side='right',fill='y')
    table.configure(yscrollcommand=scroll.set)
    for row in listing['rows']:
        table.insert('','end',iid=str(row['number']),values=(row['number'],row['name'],row['target']))
    def choose(event=None):
        selection = table.selection()
        if selection:
            on_select(selection[0],listing['token'])
            window.destroy()
    table.bind('<Double-1>',choose)
    table.bind('<Return>',choose)
    ttk.Button(window,text='Avvia selezionato',command=choose).pack(side='bottom')
