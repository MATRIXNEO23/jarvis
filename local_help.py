"""Local, read-only help using the existing command catalogs and Tk widgets."""
import tkinter as tk
import weakref
from tkinter import ttk


def help_sections(engine):
    files = getattr(engine, 'file_access', None)
    apps = getattr(engine, 'program_apps', None)
    enabled = False
    details = []
    for service in (files, apps):
        if service is None:
            continue
        try:
            if service is files:
                enabled = bool(service.available())
            commands = service.commands()
            if commands:
                details.append(commands)
        except (OSError, ValueError, RuntimeError):
            details.append('Catalogo del componente non disponibile: controlla le impostazioni.')
    return {
        'Inizia qui':
            'Scrivi nella casella e premi Invio oppure il pulsante di invio.\n'
            'Comandi con parole tue: Impostazioni > Personalizzazione comandi (comandi di base) '
            'e Gestisci add-on > sezione dell’add-on (comandi dell’add-on).\n'
            'Diagnostica servizi apre il rapporto locale, anche da voce con Lumi. Lo trovi anche in Impostazioni > Progetti e servizi. Aggiorna e Copia rapporto non inviano messaggi o richieste ai modelli.\n'
            'Scrivi aiuto, help o comandi per riaprire questa guida. Funziona anche con Gemma o GPT attivi.\n\n'
            'F1 apre la guida. Ctrl+L porta il cursore nella casella. Ctrl+, apre le impostazioni.\n'
            'La guida non invia richieste ai modelli e non esegue i comandi mostrati.\n'
            'Le sezioni spiegano esempi e prerequisiti; le funzioni opzionali richiedono attivazione e permessi.',
        'Comandi locali':
            'Scrivi e premi Invio/Invia: i comandi riconosciuti vengono eseguiti prima di Gemma o GPT. '
            'Esegui locale resta una scelta facoltativa.\n\n'
            'apri / avvia / lancia la calcolatrice\n'
            'apri / avvia / lancia il browser predefinito\n'
            'stato sistema / mostrami lo stato del sistema / controlla la RAM\n'
            'apri / mostra Download — apre la cartella in Esplora file\n'
            'elenca Download — elenco esplicitamente richiesto\n\n'
            'Apri browser usa il browser predefinito di Windows e non richiede Programmi e app. '
            'Apri Chrome o apri Edge usa invece il modulo Programmi e app e i suoi permessi.\n\n'
            + engine.available_commands(files_enabled=enabled),
        'Timer e sveglia':
            'imposta timer sei minuti\navvia un timer da 6 minuti\ntimer 45 secondi\n'
            'pausa timer\nriprendi timer\nquanto manca al timer\nferma timer\nreset timer\n\n'
            'Un timer con durata parte subito. Scrivere solo timer apre la regolazione manuale.\n\n'
            'metti sveglia alle sette e trenta di mattina\nimposta sveglia alle 07:30\n'
            'ferma la sveglia\nche ore sono\n\n'
            'La sveglia richiede la relativa add-on attiva. Se l’orario è passato, vale per domani. '
            'Per evitare ambiguità puoi usare il formato 24 ore. Gli elenchi di questa guida non vengono letti a voce.',
        'Controllo PC':
            'Add-on Controllo PC (spento finché non lo attivi in Gestisci add-on). Tutto offline.\n\n'
            'finestre aperte\ncosa c’è aperto\npassa a Chrome\nvai su Blocco note\npassa alla 2\n'
            'chiudi la finestra Blocco note\nclicca su Cerca\ndoppio clic su Foto\n'
            'scrivi ciao nel campo Cerca\ndigita buongiorno\npremi Ctrl più C\npremi invio\n'
            'scorri giù\nscorri su di 5\ncosa posso cliccare\nchiama questa finestra lavoro\n\n'
            'Le prime volte chiede «sì», poi ricorda; le azioni delicate (Invia, Elimina, '
            'Non salvare, Alt+F4, Invio…) chiedono sempre. Nomi tuoi per le finestre: '
            'Gestisci add-on > Controllo PC > Configura.',
        'Musica':
            'metti Bohemian Rhapsody\nsuona la canzone Imagine\nfammi sentire Vasco Rossi\n\n'
            'Lettore:\n'
            'play / riprendi\npausa / metti in pausa\nstop / ferma la musica\n'
            'avanti / prossima / brano successivo\nindietro / torna indietro / brano precedente\n'
            'alza il volume della musica\nabbassa il volume della musica\n\n'
            'Coda e playlist:\n'
            'aggiungi in coda Imagine / metti in coda Imagine\nmetti la playlist Viaggio\n\n'
            'Indietro: oltre 3 secondi ricomincia il brano, altrimenti va al precedente. '
            'Il pulsante ☰ della barra apre l’elenco dei brani per cartelle e playlist: doppio clic per '
            'ascoltare, «+ Coda», «+ Playlist...» per crearne o riempirne una, «Togli» e «Rinomina» per le '
            'playlist (anche più playlist con nome, anche con video YouTube). Il pulsante Coda mostra la coda: sposta, togli, cerca e aggiungi, salva come playlist. Con YouTube (chiave API) finito un video parte il risultato successivo; mentre va YouTube «aggiungi in coda …» cerca su YouTube e lo mette dopo il video in corso.\n\n'
            'Richiede l’add-on Musica attivo. Cerca prima nelle cartelle musica scelte in '
            'Gestisci add-on > Musica > Configura; se il brano non c’è apre la ricerca su YouTube '
            'nel browser (con la chiave API facoltativa apre subito il primo video).',
        'Voce':
            'Standby: microfono fermo. Premi per parlare: usa il pulsante dedicato.\n'
            'Ascolto continuo: accetta le richieste direttamente; può interpretare anche parlato ambientale.\n'
            'Hey Lumi: inizia OGNI richiesta con Lumi, per esempio Lumi, imposta timer sei minuti. '
            'Il solo nome Lumi non abilita la frase successiva.\n\n'
            'Il pulsante MIC mantiene il controllo manuale. Il riconoscimento offline richiede Vosk e il modello vocale. '
            'Per installazione e problemi usa docs/VOCE_OFFLINE.md distribuita con Lumi.',
        'Modelli e GPT':
            'GPT ON seleziona GPT per voce (anche Premi per parlare), chat e Telegram; GPT OFF seleziona Gemma. '
            'I comandi locali riconosciuti vengono intercettati nella console prima dei modelli; file e app seguono i rispettivi controlli.\n\n'
            'Al primo invio conversazionale a GPT confermi il consenso per la sessione, condiviso fra voce e chat. Un errore di connessione non seleziona Gemma. Torna a Gemma quando lo scegli tu. '
            'Le altre formulazioni possono essere interpretate da Gemma come azioni del catalogo: '
            'il motore le valida ed esegue, oppure chiede un chiarimento. '
            'Risposte non valide o annullate non eseguono azioni. '
            'Se il catalogo non entra nel contesto configurato, compare un avviso: '
            'restano disponibili chat e comandi diretti, senza cambiare automaticamente le impostazioni. '
            'Passa a GPT / torna a Gemma / usa GPT / attiva Gemma / avvia GPT cambiano lo stesso interruttore, anche a voce. In Hey Lumi anteponi Lumi. Telegram mantiene autorizzazione e consenso specifici. Prova Gemma locale resta una prova esplicita del modello.\n\n'
            'GPT richiede abilitazione, collegamento e permesso della funzione. '
            'Mai: nessun invio per quella funzione. Chiedi autorizzazione: domanda prima dell’invio. '
            'Autorizzato: evita quella richiesta ripetuta, ma non autorizza automaticamente le azioni.\n'
            'Pianifica attività propone un piano da approvare. L’autodiagnosi locale è distinta dalla valutazione esterna. '
            'Le voci Web nei permessi non equivalgono a un navigatore autonomo completo.',
        'File e app':
            '\n\n'.join(details) + '\n\n'
            'Configura Accesso file e Programmi e app nelle impostazioni: scegli cartelle, applicazioni e permessi. '
            'Con Accesso file attivo e Download autorizzata: apri Download, poi apri Foto (nome di una sottocartella), '
            'poi torna indietro di una cartella. La vista Explorer deve essere identificabile senza ambiguità. '
            'Un esempio non concede accesso. Gli alias personali dipendono dal catalogo attivo. '
            'L’indice autonomo di Lumi non è implementato: ricerca tramite Windows Search e scansione limitata. '
            'Guide del pacchetto: file_access/LEGGIMI.md e program_apps/LEGGIMI.md.',
        'Progetti e Telegram':
            'crea progetto Casa\napri progetto Casa\nelenca progetti\ntorna alla conversazione generale\n\n'
            'I progetti mantengono contesti separati. Le preferenze memoria controllano il recupero dei ricordi.\n\n'
            'Telegram richiede attivazione, account collegato e contatti autorizzati. '
            'Gestisci contatti, cronologia e consensi dalle impostazioni Telegram. '
            'Non avviare due istanze Telegram contemporaneamente. I messaggi non letti compaiono negli indicatori; '
            'aprire una conversazione marca solo i messaggi visualizzati. Gli invii restano soggetti ai controlli previsti.',
        'Tastiera':
            'F1 — Apri o richiama questa guida.\n'
            'Ctrl+L — Metti il cursore nella casella di comando, senza inviare nulla.\n'
            'Invio — Invia il testo nella casella di comando.\n'
            'Ctrl+, — Apri le impostazioni (scorciatoia già esistente).\n'
            'Ctrl+Tab / Ctrl+Shift+Tab — Cambia sezione della guida.\n'
            'Tab — Passa tra i controlli.\n'
            'Esc nella guida — Chiudi solo la guida.\n\n'
            'Per problemi: usa Autodiagnosi Lumi. Un rapporto locale non invia nulla a GPT da solo.',
    }


class HelpWindow(tk.Toplevel):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.title('Lumi — Aiuto e comandi')
        self.geometry('800x550')
        self.minsize(560, 360)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        self.notebook.enable_traversal()
        self.pages = {}
        for title, content in help_sections(engine).items():
            frame = ttk.Frame(self.notebook)
            text = tk.Text(frame, wrap='word', font=('Segoe UI', 11),
                           bg='#061421', fg='#d7f6ff', padx=12, pady=12)
            scroll = ttk.Scrollbar(frame, command=text.yview)
            text.configure(yscrollcommand=scroll.set)
            scroll.pack(side='right', fill='y')
            text.pack(fill='both', expand=True)
            text.insert('1.0', content)
            text.configure(state='disabled')
            self.pages[title] = text
            self.notebook.add(frame, text=title)
        ttk.Button(self, text='Chiudi (Esc)', command=self.destroy).pack(pady=(0, 10))
        self.bind('<Escape>', self.close)
        self.bind('<Control-l>', self.focus_command)
        self.bind('<Destroy>', lambda event: self._forget(parent, event), add='+')

    def _forget(self, parent, event):
        if event.widget is self and getattr(parent, '_jarvis_help_window', None) is self:
            parent._jarvis_help_window = None

    def close(self, event=None):
        self.destroy()
        return 'break'

    def focus_command(self, event=None):
        reference = getattr(self.master, '_jarvis_focus_command', None)
        callback = reference() if reference is not None else None
        if callback is not None:
            callback(event)
        return 'break'

    def refresh(self, engine):
        for title, content in help_sections(engine).items():
            text = self.pages[title]
            text.configure(state='normal')
            text.delete('1.0', 'end')
            text.insert('1.0', content)
            text.configure(state='disabled')


def open_help(parent, engine):
    window = getattr(parent, '_jarvis_help_window', None)
    if window is not None and window.winfo_exists():
        window.refresh(engine)
        window.deiconify()
        window.lift()
    else:
        window = HelpWindow(parent, engine)
        parent._jarvis_help_window = window
    window.focus_force()
    return window


def bind_help_shortcuts(root, settings_window, show_help, focus_command):
    root._jarvis_focus_command = weakref.ref(focus_command)
    root.bind('<F1>', show_help, add='+')
    settings_window.bind('<F1>', show_help, add='+')
    settings_window.bind('<Control-l>', focus_command, add='+')
    root.bind('<Control-l>', focus_command, add='+')
