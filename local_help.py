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
            'Add-on Controllo PC (spento finché non lo attivi in Gestisci add-on). Tutto offline, '
            'pensato per usare il PC solo con la voce.\n\n'
            'FINESTRE\nfinestre aperte\npassa a Chrome / passa alla 2 / passa a lavoro (nome tuo)\n'
            'minimizza / ingrandisci / ripristina (la finestra in uso o con il nome)\n'
            'chiudi la finestra / chiudi la finestra Blocco note\n\n'
            'SCEGLIERE SENZA DIRE IL NOME\nmostra i numeri → poi «il 3», «clicca il 3», «vai al 3»\n'
            'seleziona il primo / apri il terzo / l’ultima cartella / la prima immagine\n'
            'giù / su: la selezione si sposta di uno e Lumi dice il nome\n'
            'aprilo / apri questo / doppio clic: apre l’elemento selezionato\n'
            'apri (da solo): con un elemento selezionato Lumi chiede «Apro …?»\n\n'
            'ESPLORA FILE\nvai su Download / vai su Disco C / vai su Utenti\n'
            'indietro / avanti / su di un livello\nvai alla barra degli indirizzi (poi detta il percorso)\n\n'
            'CAMPI E TASTI\nclicca su Cerca\nscrivi gatti nel campo cerca (sostituisce il testo)\n'
            'aggiungi neri nel campo cerca (scrive dopo)\npulisci la ricerca\ndigita buongiorno\n'
            'premi Ctrl più C / premi invio\nscorri giù / scorri su di 5\n\n'
            'NETFLIX E PROGRAMMI SENZA ELEMENTI\nmostra i numeri: se il programma non dichiara i pulsanti '
            'Lumi legge le scritte sullo schermo (OCR di Windows, offline)\n'
            'riproduci / play: scritta «Riproduci», poi pulsante tondo col triangolo, altrimenti Invio\n'
            'file successivo / file precedente: un elemento (a destra nelle copertine)\n'
            'riga successiva / riga precedente: una riga sotto o sopra\n'
            'scorri a destra / scorri a sinistra / riga avanti / riga indietro: frecce della riga\n\n'
            'SCHERMO INTERO\nschermo intero / metti lo schermo intero\n'
            'esci / esci dallo schermo intero / togli lo schermo intero\n'
            'Il tasto dipende dal programma davanti: F per Netflix e YouTube, F11 per browser ed '
            'Esplora file, Esc per uscire. «esci» da solo vale solo se qualcosa è a schermo intero '
            '(il video della musica di Lumi per primo).\n\n'
            'VIDEO (Netflix, YouTube…)\nplay / riproduci, pausa, indietro (pagina precedente), torna alla home\n'
            'mostra i comandi / nascondi i comandi: striscia con i comandi della finestra davanti\n'
            'clicca Deep Impact: trova il titolo anche se il microfono lo capisce un po\' storto\n\n'
            'MOUSE PRECISO\ngriglia → dici solo il numero (cinque, sei…, anche senza «Lumi») → «clicca», '
            '«doppio clic» o «invio»\n'
            'indietro: torna alla griglia più grande; chiudi griglia\n'
            'mouse a destra / sinistra / su / giù (circa 50 pixel); mouse di poco a destra (10 pixel)\n'
            'ancora: ripete lo spostamento; clicca / clic destro: dove si trova il puntatore\n\n'
            'PROGRAMMI BLOCCATI\napri gestione attività\nchiudi forzatamente Chrome (chiede sempre; '
            'mai Lumi)\n\n'
            'AIUTO\ncosa posso fare qui → poi «altri»\nchiama questa finestra lavoro\n\n'
            'Le parole corte (giù, su, indietro, avanti, apri, il 3) valgono come comando solo '
            'mentre stai usando il Controllo PC (2 minuti dall’ultimo comando): altrimenti vanno '
            'agli altri comandi e al modello. Il puntatore si muove sempre in modo visibile. '
            'Lumi è nell’elenco finestre: chiuderla o ridurla da qui chiede sempre conferma. '
            'Scorrere, giù/su e i numeri non chiedono mai. I clic per nome le prime volte chiedono «sì» '
            'per programma, poi ricorda; le azioni delicate (Invia, Elimina, '
            'Non salvare, Alt+F4, Invio…) chiedono sempre. Nomi tuoi per le finestre: '
            'Gestisci add-on > Controllo PC > Configura.',
        'Lumi':
            'Comandi su Lumi stessa, anche con Lumi ridotta a icona:\n'
            'riduci a icona / minimizza Lumi → resta il mini avatar\n'
            'Lumi, nascondi → anche l’avatar sparisce, finché non dici «Lumi, sveglia»\n'
            'Lumi, sveglia / svegliati → riapre l’interfaccia a schermo intero\n'
            'chiudi Lumi / spegni Lumi → chiude con un saluto\n'
            'riavvia Lumi → chiede conferma, dice il messaggio per intero e si riapre da sola\n'
            'attiva / spegni cervello locale (anche «cervello locale on/off»): il modello sul PC; '
            'l\'add-on «Modello locale» in Gestisci add-on lo spegne del tutto (non si carica)\n'
            'attiva / spegni cervello online (anche «cervello online on/off»): GPT\n'
            'spegni il PC → solo detto così, chiede conferma; «annulla lo spegnimento» lo ferma\n\n'
            '«Lumi» da solo non fa ricomparire niente: aspetta il comando per qualche secondo. '
            '«sveglia» o «Lumi, sveglia» riapre sempre Lumi; la sveglia si imposta con '
            '«imposta/metti la sveglia alle …».\n'
            'Quando Lumi fa una domanda, «sì» o «no» valgono senza dire «Lumi» (anche se '
            'il microfono capisce «s» o «se»), per qualche secondo dopo la domanda.\n'
            'Mini avatar: trascinalo dove vuoi; tasto destro → «Nascondi avatar». Col mouse fermo '
            'per 30 secondi avatar e mini lettore diventano trasparenti e tornano muovendo il mouse '
            '(Impostazioni > Integrazioni > Mini avatar).\n'
            'Video della musica a schermo intero: solo il video; «esci» o Esc per tornare.\n'
            'Frasi di Lumi (saluti, risposte, «Intendevi…?»): Impostazioni > Personalizzazione '
            'comandi > Frasi di Lumi.',
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
            'MODELLO ON/OFF (in alto, accanto a GPT): con OFF nessuna richiesta va a Gemma o a GPT, '
            'funzionano solo i comandi interni; serve a provare il motore interno. A ogni avvio torna ON.\n'
            'Prima del modello Lumi prova a capire da sola: toglie le parole di cortesia e usa i sinonimi '
            '(attiva/avvia/metti = imposta, stoppa/spegni = ferma…). Se la frase diventa un comando lo esegue '
            '(in console «CAPITO COME > …»). Con MODELLO OFF, se la frase somiglia a un comando chiede '
            '«Intendevi …?»: rispondi sì o no. Sinonimi tuoi: Impostazioni > Personalizzazione comandi > Sinonimi.\n\n'
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
            'Telegram è un add-on: attivalo in Gestisci add-on > Telegram, dove trovi account '
            '(ID, hash, numero e codice in un pop-up), contatti, cronologia e consensi. '
            'Non avviare due istanze Telegram contemporaneamente. I messaggi non letti compaiono negli indicatori; '
            'aprire una conversazione marca solo i messaggi visualizzati. Gli invii restano soggetti ai controlli previsti.',
        'Chiavi API':
            'Alcuni add-on usano chiavi o dati d’accesso gratuiti. Si inseriscono nella sezione '
            'dell’add-on in Gestisci add-on; lì c’è anche il pulsante «Crea la chiave».\n\n'
            'CHIAVE YOUTUBE (add-on Musica, video nel riquadro)\n'
            '1. Apri https://console.cloud.google.com/ e accedi con il tuo account Google.\n'
            '2. In alto scegli «Seleziona un progetto» > «Nuovo progetto», dai un nome (es. Lumi) e crea.\n'
            '3. Apri https://console.cloud.google.com/apis/library/youtube.googleapis.com e premi «Abilita».\n'
            '4. Vai su https://console.cloud.google.com/apis/credentials > «Crea credenziali» > «Chiave API».\n'
            '5. Copia la chiave e incollala in Gestisci add-on > Musica > Configura, poi Salva.\n'
            'È gratuita (quota giornaliera: circa 100 ricerche). Non serve carta di credito per questa API. '
            'Consigliato: in «Limita chiave» scegli solo «YouTube Data API v3».\n\n'
            'API ID E API HASH DI TELEGRAM (add-on Telegram)\n'
            '1. Apri https://my.telegram.org e accedi con il tuo numero (il codice arriva nell’app Telegram).\n'
            '2. Scegli «API development tools».\n'
            '3. Compila App title (es. Lumi) e Short name (es. lumi), piattaforma Desktop, e crea.\n'
            '4. Copia «App api_id» (numero) e «App api_hash» (32 caratteri).\n'
            '5. In Lumi: Gestisci add-on > Telegram > «Configura account», scrivi ID, hash e numero, '
            'poi «Collegati» e inserisci il codice nel pop-up.\n'
            'Non condividere mai API hash, codici o sessione con nessuno.\n\n'
            'Se un link cambia, nella sezione dell’add-on puoi scrivere quello nuovo e premere «Salva link».',
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


# Nomi interi delle sezioni nel menu verticale (le chiavi restano corte).
FULL_TITLES = {
    'Inizia qui': 'Inizia qui',
    'Comandi locali': 'Comandi locali di base',
    'Timer e sveglia': 'Timer e sveglia',
    'Controllo PC': 'Controllo PC (finestre, mouse, tasti)',
    'Lumi': 'Lumi: finestra, avatar, chiusura',
    'Musica': 'Musica e video',
    'Voce': 'Voce e microfono',
    'Modelli e GPT': 'Modelli locali e GPT',
    'File e app': 'File, cartelle e programmi',
    'Progetti e Telegram': 'Progetti e Telegram',
    'Chiavi API': 'Chiavi API (come crearle)',
    'Tastiera': 'Scorciatoie da tastiera',
}

_LINK = __import__('re').compile(r'https://[^\s)»"]+')


def _fill_text(text, content):
    """Inserisce il testo e rende cliccabili i link https:// (si aprono nel browser)."""
    import webbrowser
    text.configure(state='normal')
    text.delete('1.0', 'end')
    text.insert('1.0', content)
    text.tag_configure('link', foreground='#5fd0ff', underline=True)
    for index, match in enumerate(_LINK.finditer(content)):
        tag = f'link{index}'
        start, end = f'1.0+{match.start()}c', f'1.0+{match.end()}c'
        text.tag_add('link', start, end)
        text.tag_add(tag, start, end)
        text.tag_bind(tag, '<Button-1>', lambda _e, url=match.group(0): webbrowser.open(url))
        text.tag_bind(tag, '<Enter>', lambda _e: text.configure(cursor='hand2'))
        text.tag_bind(tag, '<Leave>', lambda _e: text.configure(cursor=''))
    text.configure(state='disabled')


class HelpWindow(tk.Toplevel):
    def __init__(self, parent, engine):
        super().__init__(parent)
        self.title('Lumi — Aiuto e comandi')
        self.geometry('800x550')
        self.minsize(560, 360)
        # Menu verticale a sinistra con i nomi interi, testo della sezione a destra.
        body = ttk.Frame(self)
        body.pack(fill='both', expand=True, padx=10, pady=10)
        self.menu = tk.Listbox(body, width=30, activestyle='none', exportselection=False,
                               font=('Segoe UI', 11), bg='#031522', fg='#d7f6ff',
                               selectbackground='#1b6f8f', highlightthickness=0)
        self.menu.pack(side='left', fill='y', padx=(0, 8))
        self.content = ttk.Frame(body)
        self.content.pack(side='left', fill='both', expand=True)
        self.pages = {}
        self.frames = {}
        self.order = []
        for title, content in help_sections(engine).items():
            frame = ttk.Frame(self.content)
            text = tk.Text(frame, wrap='word', font=('Segoe UI', 11),
                           bg='#061421', fg='#d7f6ff', padx=12, pady=12)
            scroll = ttk.Scrollbar(frame, command=text.yview)
            text.configure(yscrollcommand=scroll.set)
            scroll.pack(side='right', fill='y')
            text.pack(fill='both', expand=True)
            _fill_text(text, content)
            self.pages[title] = text
            self.frames[title] = frame
            self.order.append(title)
            self.menu.insert('end', ' ' + FULL_TITLES.get(title, title))
        self.menu.bind('<<ListboxSelect>>', lambda _e: self.show_page())
        self.menu.selection_set(0)
        self.show_page()
        ttk.Button(self, text='Chiudi (Esc)', command=self.destroy).pack(pady=(0, 10))
        self.bind('<Escape>', self.close)
        self.bind('<Control-l>', self.focus_command)
        self.bind('<Destroy>', lambda event: self._forget(parent, event), add='+')

    def show_page(self, title=None):
        if title is None:
            chosen = self.menu.curselection()
            title = self.order[chosen[0]] if chosen else self.order[0]
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[title].pack(fill='both', expand=True)

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
            _fill_text(self.pages[title], content)


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
