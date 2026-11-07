# JRV-AUD-017 — attività Gemma nel HUD

Stato: verificata nei sorgenti in bozza; nessuna nuova build. Sourceverde `d5a58c901f5c7c283ca6369fd6af405592e1996c`.
Base015 `558135173a13ca7bdaddfc543c63897730633353`, [bozza49](https://github.com/MATRIXNEO23/jarvis/pull/49).
[Specifica](superpowers/specs/2026-11-07-jrv-aud-017-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-017-fix.md).

## Causa dimostrata e correzione

Il provider HUD non legge l'owner Gemma. Thinking usa GPT, azioni locali e documento; reasoning soltanto richieste GPT. Telegram e prova nelle impostazioni condividono la sessione nativa ma non settano il flag del lavoro chat: aggiungere quel flag da solo non risolverebbe il difetto.

Riusare il context manager delle operazioni nella sessione: contatore su lock breve dei metadati, incremento prima della coda d'inferenza, decremento in finally anche su eccezioni. Property is_busy senza I/O, caricamento o attesa del lock d'inferenza. Ask annidato in prepare_turn resta occupato fino al commit esterno. Stop/close non azzerano artificialmente un'operazione non ancora uscita. Il provider usa l'owner già esistente e il flag della chat in attesa del poll UI; nessun getter che crei o carichi il modello.

Le animazioni riusano reasoning/thinking, senza aggiungere un poller o alterare comandi/risposte. Lo stato indica elaborazione generica, non fasi dettagliate del backend non esposte alla UI. Speaking/listening e priorità visuali restano invariati.

## Prove ed esiti

Red source `5ac6e9d1e90f4c6ebc02d7d60d37161a4d1d2b5f`, [run42360223737](https://github.com/MATRIXNEO23/jarvis/actions/runs/42360223737),14nuovi/883totali attesi. Runtime ancora015, fixture del provider con owner inattivo per conservare test GPT precedenti. Esito FALLITO:883test per job,18failure0errori tutti nel nuovo017 (inclusi subtest). Python3.11.9 job128366829486118.761s; Python3.12.10 job128366829253132.637s. Manca propertyBoolean e la veraUI mostra MICROFONO SPENTO anziché JARVIS STA RAGIONANDO durante generazione nativa. Tutti i test precedenti passano; nessun022/023 osservato. Searchlive3.12 passato con servizio e fixture ripristinati.

Review preventiva readonly: nessun bug confermato nella specifica/test; chiesti due rafforzamenti. Snapshot idle ora intercetta anche config_loader/memory_loader, per vietare I/O implicito. Nuovo metodo stop con abort ignorato verifica che lo stato resti occupato finché il backend non esce davvero.15nuovi/884attesi nella candidata; modifiche dopo il primo sourceRed senza rivendicare ulterioreRed. Cleanup Tk rafforzato per chiudere la finestra anche se un worker non termina nei tempi del test.

Usati callback/provider HUD/Telegram reali e fixture sessione/factory/bridge con ABI controllata. La prova impostazioni applica solo la trasformazione UI del builder a un file temporaneo: non crea ZIP/DLL. Osservatore bounded verifica che lo status non aspetti l'inferenza. Una prova mostra il testo nella vera UI Tk Windows e controlla priorità voce.

## Limiti e recupero

Modello/DLL/account Telegram/microfono reali non utilizzati. Nessuna misura CPU/RAM su Windows10/i3/HDD né pacchetto estratto.022/023 restano distinti, non corretti per assenza di riproduzione. Nessuna esecuzione funzionale Linux, dipendenza o dato/profilo personale. Nessuna build/merge/release; ramo isolato `fix/jrv-aud-017-native-hud-20261107`, ritorno alla015 reversibile senza cancellare dati o pacchetti precedenti.

Review runtime indipendente readonly senza rilievi bloccanti: contatore bilanciato, lock breve, nessuna creazione di sessione/statusIO, stop/close non azzerano prematuramente attività. Entrambi i gap recepiti. Green Windows ancora necessario; la review non è un test eseguito.

## Prima candidata: fixture header incompleta, non un Green

Source `0419b5b7d31ca320a1fae9c48becd1f8efad5819`, run42360619718 FALLITO.884test/job,0failure/3errori: Python3.11.9 job128368034045157.873s; Python3.12.10 job128368034166121.567s. Tutti15nuovi metodi017 passano, ma tre test header eseguono il provider estratto viaAST con un ambiente che non inizializza gemma_trial_busy/gemma_session: NameError nella lambda. L'app reale inizializza entrambi prima della registrazione del provider. Non è022/023 e non è una prova che i pulsanti runtime siano guasti.

Corretta solo la fixture test_hud_quick_toggles.wire: owner=None/flagFalse, come nella vera inizializzazione e nella fixture ActivityStatus già aggiornata. Tutti gli assert di clic, salvataggio/rollback e conservazione memoria restano identici; runtime della candidata invariato. Il primo fallimento è conservato, niente retry cieco. Serve nuova verifica Windows del source con la fixture completa; nessun Green dichiarato.

## Green2 Windows e checkpoint

[Run42360995994](https://github.com/MATRIXNEO23/jarvis/actions/runs/42360995994) SUCCESS, source `d5a58c901f5c7c283ca6369fd6af405592e1996c`, prima verifica di questo source con fixture completa. Python3.11.9 job128369166220:884test in122.925s; Python3.12.10 job128369166047:884test in130.016s. Zero failure/errori/skip, tutti15nuovi017 passati, compresa veraUI Tk e callback Telegram con generazione controllata. Tutti i test dei pulsanti tornati verdi senza cambiare gli assert. Runtime identico alla prima candidata0419b5b7: hash dei due moduli confrontati sulle API Git.

Sintassi Python/JavaScript/PowerShell e probe nativo passati. Searchlive3.12 passato, servizio ripristinato e fixture rimossa. Build, estrazione, artifact e publisher saltati. Nessun test funzionale Linux.022/023 non osservati, restano aperti senza una riproduzione causale risolta.

[JSON evidenza](evidence/jrv-aud-017-fix-20261107.json) conserva Red, prima candidata fallita, causa fixture e Green2. Checkpoint finale solo documenti/evidenza; runtime/test da confrontare col source verde prima di dichiarare conservazione remota. Prossimo019: chiarire unità del budget memoria senza cambiare valori/salvataggi o introdurre un tokenizer.
