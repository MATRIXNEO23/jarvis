# Jarvis — gestione add-on locali con registro GPT sincronizzato

**Stato:** ramo sperimentale `feature/trusted-addon-lifecycle-gpt` (PR draft #28), da provare sul Pavilion prima di adottarlo. Dipende dal registro live della PR #27 e dai moduli Telegram della PR #26. Le vecchie installazioni e i dati Telegram non vengono modificati.

## Utilizzo nell'interfaccia
1. Aprire **Impostazioni → Add-on → Gestisci add-on**.
2. Premere **Installa / aggiorna...** e scegliere un file `.jaddon`. Un pacchetto dimostrativo facoltativo si trova in `examples/addons/DiagnosticaSistema.jaddon`. Nessun file di esempio si installa da solo.
3. Il pacchetto viene controllato e salvato in `%LOCALAPPDATA%\\Jarvis\\addons`; per sicurezza nasce **SPENTO**. Anche un aggiornamento a una versione maggiore spegne il vecchio add-on e revoca l'autorizzazione, finché l'utente non lo riattiva.
4. Selezionare l'add-on nella lista e premere **Attiva / Disattiva**; confermare la sua attivazione. Le modifiche hanno effetto alla prossima richiesta a GPT, senza riconnettere l'account Sign in with ChatGPT e senza reinstallare un modello locale.
5. **Rimuovi** elimina la registrazione dell'add-on scelto, dopo conferma. **Ricarica** verifica lo stato dei file. La disattivazione non cancella il pacchetto.
6. In modalità conversazione GPT, oppure in console testuale con richieste brevi, Jarvis comunica le capacità attive al GPT. Il modello può suggerire l'ID approvato; soltanto il dispatcher locale lo traduce nel comando realmente autorizzato.

## Formato `.jaddon` v1
È un singolo file JSON UTF-8, **non uno script o uno ZIP eseguibile**. Schema esatto: `schema_version: 1`, `id`, `name`, `version: X.Y.Z`, `description`, `actions`; ogni azione ha `id`, `description`, `example`, `core_action`.

L'ID azione deve essere `addon.<id>.<azione>`. Il manifesto non può dichiarare percorsi, shell, comandi Windows, binari, `module`, URL esterni, API, permessi arbitrari o codice. Un file oltre 12 KB, manomesso o con chiavi sconosciute viene rifiutato. Massimo 20 add-on e 32 azioni complessive.

**Esecuzione v1 volutamente limitata a tre azioni già implementate, approvate e di sola lettura:** `system.status`, `downloads.list`, `history.list`. Servono per collaudare il ciclo di vita e il dispatcher senza regalare privilegi a un file installato. Il pacchetto demo si limita a `system.status`; non attiva nuove capacità hardware o servizi.

## Cosa succede quando un add-on cambia
- **Installa:** validazione del file, salvataggio atomico, registrazione disattivata.
- **Attiva:** consenso dell'utente, registrazione live, promozione nel catalogo visibile al GPT esterno, abilitazione del dispatcher.
- **Disattiva / rimuovi:** l'azione non può essere proposta da nuove richieste, né eseguita dopo la revoca.
- **Aggiorna:** versione incrementata, autorizzazione revocata, registrazione aggiornata e nuovo consenso per riattivare.
- **Riavvia Jarvis:** lo stato autorizzato è ricostruito dai file JSON locali; mai da memoria GPT o messaggi di chat.
- **Modifica manuale / file corrotto:** il file viene ignorato se la sua integrità interna non coincide con quella registrata; non si esegue codice proveniente da esso. Se l'archivio non è leggibile, l'elenco eseguibile va considerato non disponibile.
- **GPT restituisce una vecchia capacità:** il parser, il dispatcher e il worker la controllano nuovamente. Una proposta obsoleta viene respinta senza esecuzione.

## Confini di fiducia e componenti
`addon_manager.py` è la fonte locale della registrazione e dei controlli. `addon_ui.py` gestisce la finestra Tkinter. `live_capabilities.py` osserva gli stati e il loro hash di versione. `conversation_router.py` costruisce il catalogo compatto per il bridge ufficiale con limite 5.000 caratteri e valida le proposte JSON. `jarvis.py` gestisce l'esecuzione locale senza delegarla al GPT.

Il modello esterno **non riceve** nomi o numeri Telegram, credenziali, file personali, o i file degli add-on. Riceve soltanto un elenco limitato di ID di azioni attive e una sintesi di stato, a ogni nuova richiesta. Non si eseguono richieste di rete e non si installano dipendenze con questa funzione.

**Limite importante:** un nuovo add-on con funzioni davvero inedite (es. controllo di una nuova app) richiede un **handler Python sottoposto a revisione e inserito in una release attendibile di Jarvis**, con controlli di autorizzazione propri. Il file descrittivo `.jaddon` non concede, da solo, un esecutore generico per nuovi programmi. Questo è intenzionale per non eseguire software non verificato semplicemente perché viene copiato nella cartella degli add-on. Un futuro catalogo di provider firmati può essere sviluppato e collaudato separatamente.

## Collaudo
`tests/test_addon_lifecycle.py` prova installazione, persistency, aggiornamento che disattiva, revoca, rimozione, manifest sospetti, JSON manomessi, funzionamento del dispatcher read-only e prompt lungo entro 5K. I test GitHub Actions sono senza rete, non eseguono realmente Telegram, programmi esterni o codice di terze parti.

Collaudo Windows manuale ancora necessario sul Pavilion: installare il pacchetto demo in cartella separata, verificare che resti spento, attivarlo, interrogare il GPT esterno, disattivarlo, ritentare e verificare che sia rifiutato; aggiornare e confermare che torni spento; rimuovere e verificare che sparisca. Prima di testare fare backup di `%LOCALAPPDATA%\\Jarvis`. Non disattivare Defender se segnala un pacchetto.
