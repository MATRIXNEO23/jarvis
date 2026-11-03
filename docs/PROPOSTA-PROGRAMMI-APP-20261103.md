# Proposta — add-on Programmi e app, 3 novembre 2026

Stato: soluzione proposta in risposta alla richiesta dell'utente; nessun codice prodotto, test Windows o build nuova. La003 resta il download corrente. L'utente riferisce «i tasti funzionano»: conferma limitata ai nuovi pulsanti della003, non a tutte le funzioni o prestazioni.

## Obiettivo e soluzione consigliata

Avviare dalla voce o dal testo le applicazioni Windows scelte nelle impostazioni: programmi classici ovunque installati e app Store dell'utente corrente. L'utente delega la scelta tecnica all'assistente e richiede review. Riutilizzare l'architettura Jarvis, cartella autonoma `program_apps`, manifest .jaddon descrittivo e adattatore locale verificato; nessuna dipendenza a pagamento, modello locale o processo residente aggiuntivo.

Un solo elenco in Impostazioni > Gestisci add-on > Programmi e app > Configura, con ricerca per nome, spunta «Consenti avvio», nome leggibile, tipo (classica/Store), stato e dettaglio destinazione. Pulsanti Aggiorna elenco, Aggiungi programma, Prova avvio e Salva. Prova avvio usa il normale controllo dei permessi salvati; non abilita implicitamente la riga. Il primo elenco richiede aggiornamento su richiesta; aggiornamenti successivi conservano selezioni e nomi personali.
Tutte le app nuove non selezionate; applicare Salva per rendere effettive le modifiche. Mostrare stato vuoto, caricamento annullabile, risultato incompleto/errori fonte e stato non disponibile senza bloccare Tk. Nessun taglio a20 app: elenco scorrevole con eventuale caricamento progressivo, conteggio totale e copertura dichiarata. Timeout di fonte produce errore/incompletezza visibile e non cancella app o consensi precedenti.
Nomi personali facoltativi, es. «posta» per Thunderbird. Non chiedere all'utente di conoscere percorsi/ID per le app rilevate.

## Alternative considerate e scelta tecnica proposta

1. Consigliata: catalogo Windows dell'utente + collegamenti Start/Desktop + App Paths e integrazione manuale. Copre classiche/Store e installazioni personalizzate senza scandire tutti gli eseguibili; conserva identità di avvio, non solo directory.
2. Soli percorsi aggiunti manualmente: semplice ma costringe a trovare ogni programma e non risolve da solo lo Store. Resta integrazione facoltativa.
3. Scansione ricorsiva di Program Files/dischi: non identifica sempre il lanciatore corretto fra helper/disinstallatori e non è adatta all'attivazione Store; costo HDD e falsi candidati maggiori. Non scelta per l'inventario iniziale.

La scelta1 è proposta dall'assistente sulla base del requisito; non è ancora approvazione dell'utente di questa nuova implementazione.

## Fonti Windows e avvio

- Get-StartApps e namespace AppsFolder: nomi/identità visibili all'utente corrente; Get-StartApps non elenca app assenti da Start.
- Collegamenti .lnk Start/Desktop utente e comuni e App Paths HKCU/HKLM, viste32/64 bit: integrazione classiche anche fuori Program Files. Le entry di disinstallazione possono offrire indizi, mai un comando di avvio direttamente.
- Store: pacchetti e manifest dell'utente corrente, soltanto applicazioni realmente avviabili; escludere framework, risorse, voci senza launcher. AUMID indipendente dal percorso; attivazione nativa ApplicationActivationManager per le app compatibili.
- Classiche: identità Shell/collegamento Windows valido, oppure eseguibile locale selezionato e verificato. ShellExecuteEx per il target registrato; niente stringa di comando generata dal GPT. Gli argomenti necessari di un collegamento locale selezionato sono dati della sua identità di avvio e vanno preservati, non inventati; validazione/policy prima dell'esecuzione.
- Aggiungi programma accetta scelta locale di .exe/.lnk con nome leggibile; programmi portatili e installazioni senza registrazioni restano coperti manualmente. Nessun percorso Store da inseguire in WindowsApps e nessun cambio ACL/privilegi.
- Refresh rilegge metadati soltanto; avvio solo dopo una richiesta esplicita o pulsante Prova avvio. Nuove app non ereditano la selezione di un omonimo; target manuale sostituito o cambiato significativamente richiede nuova scelta. App disinstallata conserva riga non disponibile e preferenza, senza lancio di altra app.

Fonti Microsoft verificate in questa sessione:
https://learn.microsoft.com/en-us/windows/configuration/store/find-aumid
https://learn.microsoft.com/en-us/windows/win32/shell/app-registration
https://learn.microsoft.com/en-us/windows/win32/shell/launch
https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nf-shobjidl_core-iapplicationactivationmanager-activateapplication

Queste fonti documentano API disponibili; non provano ancora la loro integrazione nella nuova add-on o il funzionamento delle app sul Pavilion.

## Dialogo, autorizzazione e contesto

«Apri Thunderbird» e «avvia Netflix» sono esempi, non formule obbligatorie. Comando preciso con nome/alias univoco: risoluzione locale e avvio senza GPT. Parafrasi non riconosciuta: GPT già abilitato/collegato può proporre la capacità con nome richiesto; il locale risolve esclusivamente fra app consentite e convalida l'identità. GPT non fornisce eseguibili, AUMID o comandi liberi.
Più candidati: domanda breve «Quale?» e finestra dedicata; risposta nome/numero completa la stessa richiesta una volta sola. Non recitare l'elenco. Conservare richiesta e candidati con identità/revisione; nuovo argomento, annulla, scadenza, disattivazione o revoca impediscono un avvio vecchio.
App non selezionata: risposta «abilitala nelle impostazioni», nessuna domanda ripetuta per app già autorizzata. App assente o guasta: messaggio specifico; non aprire il sito web come sostituzione.
Esito nativo accettato distinto da finestra osservata: non affermare che il contenuto è visibile senza prova. Una app già aperta segue il comportamento del proprio launcher (nuova istanza o attivazione), senza promettere riuso universale.
Aiuto/«cosa puoi fare?» e descrizione al GPT aggiornati da medesime capacità e selezioni. Non inserire tutto l'inventario/percorso privato nel prompt: risoluzione locale su richiesta e chiarimenti circoscritti, preservando il budget della conversazione.

## Integrazione verificata nei sorgenti003

Source2d52ba540aad1f9989f588e45b7a0b0973d49e67:
- local_engine.py avvia poche app fisse con Popen: manca catalogo configurabile generale. Raccordo comune voce/testo e risultati TaskResult da riusare.
- file_access/windows.py e windows_shell.ps1 leggono già Get-StartApps, pacchetti, App Paths e .lnk per trovare directory. Non equivalgono a inventario completo di launcher; attuali limiti40/2000 e risposta64KB non vanno copiati come troncamento silenzioso della nuova lista.
- addon_ui.py configure è oggi specifico accesso_file. Serve piccolo dispatch esplicito per le configurazioni fidate.
- addon_manager.py accetta soltanto target di base/file e cinque azioni per manifest: aggiungere adattatore programmi autorizzato, non codice eseguibile importato dal manifest. Una capacità parametrica di avvio, non un'azione .jaddon per ogni applicazione.
- capability_registry/live_capabilities e raccordi jarvis/conversation_router richiedono percorso definito fino all'esecutore; non basta il menu. Va verificata precedenza fra avvio app, apertura cartella e dialoghi documenti già presenti; non sottrarre Blocco note al flusso documenti.
- Dati selezioni/catalogo nel profilo esistente, addon-data/programmi_app, separati dai sorgenti. Salvataggio atomico, rollback visibile se fallisce, revisioni coerenti e compatibilità di003 al ritorno (dati additivi separati).
- Riusare utility Windows appropriate senza spostamenti massivi di Accesso file. Revisione del raccordo finale basata sul diff; struttura dei moduli per responsabilità, nomi file lasciati al piano.
- Disattivare/rimuovere add-on invalida richieste ed esclude avvio; dati/preferenze conservati secondo ciclo di vita esistente.

## Confine di questo incremento

Solo inventario/selezione/avvio. Chiusura programmi è requisito già registrato separatamente (anche app aperte manualmente, chiusura normale senza perdita dati); non implementarla o chiedere di nuovo tale scelta qui. Controllo interno app, installazione/disinstallazione, automazioni browser e correzioni ricerca20/Programmi Explorer restano attività separate. Non disabilitare servizi o cambiare modalità microfono per risparmiare risorse.

## Fasi e prove previste, non ancora eseguite

1. Prova nativa Windows isolata di inventario e avvio classica + app pacchettizzata disponibile, con verifica API/esito e pulizia. Se il runner non offre Store interattivo, dichiarare lacuna e definire prova Windows adeguata, non sostituire tutto con simulazioni.
2. Percorso minimo completo: selezione/salvataggio → richiesta voce/testo → app consentita → avvio → esito. Test per directory con spazi/non standard, collegamento con argomenti, app Store/AUMID, duplicati/alias e selezione a più turni; fonti incomplete, revoca/stale, disinstallazione e salvataggio fallito. Nessun avvio durante inventario o se add-on spenta/app non scelta.
3. Regressioni Windows3.11/3.12 e catalogo/aiuto/GPT simulato, chiarezza fra API accettata e finestra osservata, budget prompt e memoria, UI non bloccata. Microfono/account reali distinti.
4. Review indipendente del diff e prove; solo dopo richiesta di build, candidata004 con ZIP estratto/UI/download verificati,003/002/001 conservate. Nessuna nuova build da questa proposta.
Misure consumo: niente polling/scansione residente; rilevamento on-demand, processi temporanei chiusi, dati minimi caricati a richiesta. CPU/RAM/usabilità effettive sul Pavilion da misurare, nessun numero promesso.

## Esito della revisione preventiva

Review indipendente in sola lettura del documento45b15baa092d7ae74c67d1fcf43fc7c031f3c332: nessuna questione sostanziale mancante per preparare il piano. Confermata distinzione inventario/launcher, fallback manuale, integrazione fidata e revoca delle richieste pendenti. Precedenza dialoghi, validazione launcher e copertura nativa Windows sono verifiche già richieste, non prove eseguite. Scelta tecnica rimane proposta dell'assistente; nessuna implementazione o nuova build avviata.
