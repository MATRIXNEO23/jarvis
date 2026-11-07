## JRV-AUD-007 — correzione autorizzata in preparazione, 2026-11-07

Dopo spiegazione semplice l'utente dà «ok»: applicare007, un solo passo. Basec9d1d29 (bozza40), ramo fix/jrv-aud-007-voice-generation-20261107. Specifica docs/superpowers/specs/2026-11-07-jrv-aud-007-design.md e piano docs/superpowers/plans/2026-11-07-jrv-aud-007-fix.md. Red già valido2632321/run42340988254,723 test/job,9 fallimenti e0 errori. Aggiunti6 test di confine (effetti vecchi, misti, malformed, close, stato nuovo); runtime ancora invariato, nuovo Red da acquisire prima del fix. Scelta minima: numero sessione nell'evento, check nel consumer prima degli effetti; nessuna coda parallela/svuotamento globale. Nessun build/merge/dato utente/test funzionale Linux.022/023 aperti. Prossimo: Windows Red ampliato, poi implementazione e Green.

## 7 novembre 2026 — JRV-AUD-007 confermato, sola verifica

[Bozza40](https://github.com/MATRIXNEO23/jarvis/pull/40), base7920c4d (001–006 conservate), source2632321c258d9a20d44a7e6cbba8538476505412. [Rapporto](VERIFICA-JRV-AUD-007-20261107.md), [evidenza](evidence/jrv-aud-007-20261107.json), [run42340988254](https://github.com/MATRIXNEO23/jarvis/actions/runs/42340988254): Windows3.11.9/job128308391527 e3.12.10/job128308391854,723 test ciascuno,9 fallimenti comportamentali e0 errori,153.353s/148.019s. Suite rossa attesa:007 CONFERMATO/ALTO, non corretto. Quattro nuovi metodi falliscono (9 sottocasi); tre controlli passano; nessun altro fallimento.

Causa: `_report` verifica generazione prima della coda ma manda solo(kind,value); `poll` usa modo corrente. OFF→ON permette a testo vecchio di arrivare a comando/modello e a status vecchio di sostituire stato nuovo; frase senza hotword GPT diventa locale passando a continuo. Controlli: standby blocca; produttore vecchio non accoda; comando/modello corrente passa una volta. Producer/Queue/callback/loop dispatch reali, audio/azioni/modello controllati; nessun programma o account usato per007.

Errore iniziale della fixture (mock refresh_buttons assente) registrato e superato; aggiunti controlli positivi modello/hotword dopo review indipendente, senza ulteriori rilievi. Nessuna modifica runtime, configurazione/dato utente, merge, build/ZIP/release o test funzionale Linux. Sintassi Python/JS passata; PowerShell/probe file saltati dopo Red; Search live3.12 passata con servizio/fixture ripristinati. Windows10/i3/HDD, microfono/Vosk e modello reale non verificati.022/023 aperti, non riprodotti in questo run.

Prossimo passo soltanto dopo via utente: identità di sessione nell'evento e controllo al consumo prima di qualunque effetto; preservare altri eventi/mode/consensi, rendere verdi i test e rieseguire Windows. Non svuotare tutta la coda condivisa. Checkpoint finale soltanto documentale.

## JRV-AUD-007 — verifica in corso, 2026-11-07

Richiesta «ok verifica»: soltanto test/documentazione. Base `7920c4d9c32049d49f848aef3af0006a037dfedf`, ramo `verify/jrv-aud-007-voice-queue-20261107`, dipendente dalla bozza39. Ipotesi: evento vocale già in coda reinterpretato dopo cambio modalità/standby. Piano: `docs/superpowers/plans/2026-11-07-jrv-aud-007-verification.md`; test `tests/test_voice_queue_generation.py`. Nessuna correzione runtime applicata. Prova Windows ancora da eseguire; nessun test funzionale Linux, microfono, GPT reale, build o merge. Prossimo passo: Windows CI e confronto tra eventi vecchi e controlli nuovi. 022/023 restano aperti.

## 7 novembre 2026 — JRV-AUD-006: recupero dipendenza verificato, nessuna build

Sourcec0007689154efa574917ddb2ce23279ddf36c5f8, [PR draft39](https://github.com/MATRIXNEO23/jarvis/pull/39) dipendente dalla38. [Run42339214356](https://github.com/MATRIXNEO23/jarvis/actions/runs/42339214356) SUCCESS: Python3.11.9/job128302928559,716 test/122.394s; Python3.12.10/job128302928433,716 test/131.725s. [Evidenza](evidence/jrv-aud-006-20261107.json), [mappa/provenienza](NATIVE-ENGINE-REFERENCE.md). Red709 test/un fallimento per job per capacità autonoma assente, senza fingere una build attualmente fallita: vecchio artifact ancora valido fino al18 novembre.

Quattro consumer ora recuperano lo stesso componente da archivio Git fissatof147b1a; SHA archivio/DLL e source ABI controllati, estrazione selettiva, staging senza sovrascrittura divergente, riuso identico e archivio locale facoltativo. Source checkout pin, controlli hash esistenti e guardie build/publisher preservati. Runtime Jarvis, vecchi artifact/ZIP, configurazioni e dati non modificati; nessun binario nuovo in Git.

Otto nuove prove Windows passate: recupero pubblico reale senza artifact, sorgente upstream fissato reale, probe DLL caricamento/export con7 simboli e token iniziali0, corruzione/dimensioni/hash, membro mancante/duplicato, download errato, conservazione/idempotenza e LF/CRLF. Review indipendente senza blocchi dopo ricontrollo dei gap; archivio e DLL anche verificati dal revisore, otto blob uguali ai remoti. Sintassi/probe e Windows Search live passati, servizio/fixture ripristinati; package/publisher skipped.

Limiti: non eseguiti action checkout/full workflow di inferenza/build completa, GGUF o target Windows10/i3/HDD. Non è compilazione C++ bit-per-bit; è recupero dei medesimi byte senza scadenza Actions, con dipendenza dal repository GitHub o copia locale verificata. Nessuna nuova build, ZIP applicativo, release, merge o test funzionale Linux.022/023 restano aperti. Checkpoint successivo solo documentale; prossimo JRV-AUD-007: verificare e riprodurre trascrizioni vocali vecchie in coda dopo spegnimento/riattivazione o cambio modalità.

## 7 novembre 2026 — JRV-AUD-006, candidata di preparazione build in verifica

Red2da23de / run42338424815/job128300496475:709 test/un fallimento senza errori per capacità autonoma assente, non una build dichiarata fallita oggi. Implementati tools/native_model/restore_engine.py e manifest: archivio Git f147b1a, streaming limitato/hash archivio e DLL, membro unico, staging senza sovrascrivere file diversi, archivio locale identico facoltativo. Quattro consumer ora usano il helper dopo setup Python; pin upstream e hash esistenti conservati, guardie build/publisher invariate. Trigger suite estesi a manifest e workflow. Runtime Jarvis invariato.

Review indipendente iniziale senza blocchi: archivio e DLL verificati anche dal revisore. Gap minore coperto estendendo il recupero reale al sorgente upstream fissato, oltre alle fixture; source normalizzato identico al blob Git7805cd49. Otto prove preparate: download reale senza artifact, probe DLL/export senza GGUF, ZIP sintetici corrotti/duplicati/dimensione/hash, file preesistenti/idempotenza, source ABI e download troncato. Nuova mappa docs/NATIVE-ENGINE-REFERENCE.md. AST/JSON/diff controllati; Green Windows ancora pendente. Nessuna compilazione/build/ZIP applicativo, release, esecuzione modello o test funzionale Linux;022/023 aperti.

## 7 novembre 2026 — JRV-AUD-006, recupero dipendenza in preparazione

Base649d1a0 con001–005 conservate; ramo fix/jrv-aud-006-native-reference-20261107. Artifact13339099748/run41860087656 non ancora scaduto, scadenza verificata18 novembre2026 ore15:49:03UTC. Quattro workflow lo consumano. Identica DLL già presente nello ZIP61a95f8 in Git al commitf147b1a, hashac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba; nessun binario nuovo necessario.

Piano tools/native_model/restore_engine.py con manifest immutabile, recupero pubblico/hash/extraction selettiva, consumer aggiornati. Test Red della capacità di recuperare da checkout vuota senza artifact (baseline manca il helper): non si finge che la build attuale sia già fallita, non si cancella artifact. Dopo recupero il test userà il probe DLL esistente, senza modello/GGUF/build. Runtime/workflow ancora invariati, nessun test funzionale Linux, nuova build/ZIP, release o dato personale.

## 7 novembre 2026 — JRV-AUD-005 verificata in CI con ABI controllata, non distribuita

Checkpoint357c65122bb0faa0b07871c8b59cb65692831b93, runtimee20e4b88451541d650d0a9160f536290a6daaa25, [PR draft38](https://github.com/MATRIXNEO23/jarvis/pull/38) dipendente dalla37. [Run42337129314](https://github.com/MATRIXNEO23/jarvis/actions/runs/42337129314) SUCCESS: Python3.11.9/job128296467283,708 test/114.337s; Python3.12.10/job128296467507,708 test/106.014s. [Evidenza](evidence/jrv-aud-005-20261107.json).

Red700 test/tre fallimenti per job ha dimostrato chat+trial e due pannelli con picco2 generazioni, reload e abort concorrenti al confine ABI controllato. Il builder aggiungeva un proprietario separato alla UI del pacchetto. Ora il getter condiviso passa al pannello senza attivazione automatica; prova, chat e Telegram usano lo stesso proprietario/lock. Reload esplicito e generazione isolata nella sessione, storico invariato, nessuno stop finale del proprietario condiviso. Adapter.prepare riceve snapshot validato; richieste obsolete in coda rifiutate, ulteriori salvataggi non cambiano il modello già acquisito.

Dieci nuove prove, callback apertura reale, trasformazione UI effettiva su copia temporanea senza ZIP. Review indipendente senza blocchi; lacuna getter/lock corretta con osservatore del tentativo reale e ricontrollata, confronti DOS/canonici corretti con samefile senza rimuovere verifiche modello/parametri. CI intermedie706/708 fallite solo per quelle fixture, conservate nei riferimenti. Sette blob runtime/test recensiti uguali ai remoti. Sintassi/probe nativi e Windows Search live passati, servizio/fixture ripristinati; package/publisher skipped.

Non è una prova di crash risolto con C/DLL/GGUF reali: nessun modello reale, target Windows10/i3-2100/HDD, account Telegram o microfono collaudato; nessuna build, ZIP, merge, chiamata GPT o modifica dati/configurazioni personali.022/023 restano aperti. Il checkpoint seguente cambia solo documentazione. Prossimo JRV-AUD-006: dipendenza da artifact nativo in scadenza il18 novembre, da risolvere prima di quella data senza build automatica.

## 7 novembre 2026 — JRV-AUD-005, correzione della fixture percorsi Windows

Run42336668228 sul runtimee20e4b8:706 test per Python3.11/3.12, un fallimento della nuova prova per confronto testuale fra percorso DOS RUNNER~1 e nome completo runneradmin del medesimo GGUF. Difetto della fixture, non del runtime. Corretti solo confronti con numero di load e os.path.samefile, mantenendo verifiche modello/parametri. La lezione sui nomi Windows era già presente e va applicata anche alle prove nuove.

Review finale runtime senza blocchi; gap queued-settings ora coperto da osservatore sul tentativo reale del RLock (non solo getter), ricontrollato indipendentemente. Anche prova snapshot→prepare aggiunta. Nessuna ulteriore modifica runtime; prossimo controllo:708 test Windows sul checkpoint di test corretto. Nessuna build/ZIP/merge, prova DLL/GGUF reale o test funzionale Linux.022/023 restano aperti.

## 7 novembre 2026 — JRV-AUD-005, review e due nuove prove mirate

Candidata runtimee20e4b8 recensita indipendentemente: nessun difetto bloccante. Rilievo minore: manca prova del cambio configurazione durante attesa del lock. Aggiunti test deterministici del callback trial mentre chat è bloccata, poi salvataggio; e dello snapshot letto prima di un ulteriore salvataggio, verificando modello/parametri effettivi e file nuovo preservato. Runtime invariato; le nuove prove richiedono CI Windows aggiornata. Nessun test funzionale Linux, DLL/GGUF reale, build, ZIP o merge.

## 7 novembre 2026 — JRV-AUD-005 confermata al confine ABI, candidata in verifica

Red728ef2d / run42336282687/job128293840609:700 test/tre fallimenti senza errori. Trial generato dal builder insieme alla chat o a un altro pannello: ABI controllata registra picco2 generazioni, ricaricamento e abort sovrapposti; callback apertura senza owner. Dimostrato il difetto di ownership, non un crash C/DLL reale.

Candidata: get_gemma_session trasmesso al pannello senza invocarlo; test_model generato chiama test_generation sul proprietario app esistente, senza stop finale. La sessione attende il lock, valida snapshot/configurazione, esegue reload esplicito e prova isolata, lascia backend pronto a chat/Telegram senza cambiare lo storico. NativeChatAdapter.prepare accetta lo snapshot per impedire cambi di modello fra validazione e caricamento. Nuove prove per stile/storia, modello/parametri appena salvati, configurazione obsoleta, errore, Telegram concorrente e pannello senza owner. AST/diff controllati; Green Windows e review indipendente pendenti. Nessun test funzionale Linux, DLL/GGUF/Pavilion reale, build/ZIP, merge o dati personali.022/023 restano aperti.

## 7 novembre 2026 — JRV-AUD-005, riproduzione in corso

Basefa4eec2 con001–004 conservate; ramo fix/jrv-aud-005-native-owner-20261107, piano dedicato. La root UI non ha Prova generazione: il builder la aggiunge nel pacchetto creando una seconda sessione, mentre chat/Telegram già condividono get_gemma_session. Test Windows preparati: stessa trasformazione UI su copia temporanea (nessun ZIP), callback generato e factory/bridge/adapter/session reali con ABI controllata; chat+prova e due pannelli, reload/abort durante altra generazione. Ingresso impostazioni reale verificato senza attivazione automatica. Runtime invariato, Red da eseguire; nessun crash DLL/GGUF reale dichiarato, test funzionale Linux, build, merge o dato personale. Proposta: riusare il proprietario esistente e una prova isolata con reload serializzato.

## 7 novembre 2026 — JRV-AUD-004 verificata nei sorgenti, non distribuita

Runtime8557ddb9b23c34c11aaee7a1b65bf57470dfd7f5, [PR draft37](https://github.com/MATRIXNEO23/jarvis/pull/37), dipendente dalla36. [Run42332441469](https://github.com/MATRIXNEO23/jarvis/actions/runs/42332441469) SUCCESS dopo un retry del solo job3.12: Python3.11.9/job128281773601,698 test/90.906s; Python3.12.10/job128282998223,698 test/113.115s. [Evidenza completa](evidence/jrv-aud-004-20261107.json).

Confermati quattro incastri lifecycle/richiesta file in Red692 test per job. Review ha trovato un rischio della candidata1, poi riprodotto con Red2 Python3.11/698 test/tre fallimenti: vecchi pending/selezioni potevano rivivere. Candidata2 serializza lifecycle e invalidazione con RLock separato, conserva i permessi transazionali, rilascia manager-lock prima di file.reset e completa reset prima della riattivazione. Refresh iniziale completo invalida anche revoche esterne prima della riapprovazione. Runtime modificato solo addon_manager.py; FileAccessService, schemi, autorizzazioni e dati conservati. Sette nuove prove reali verificano incastro, reenable con/senza nuova richiesta, vera selezione, ledger mancante, permessi durante transazione, limiti/copie e refresh attivo. Review finale senza blocchi residui; blob locali/remote uguali.

Limiti CI conservati:022 crash Tcl_AsyncDelete nel Red2/job3.12, senza conteggio completo;023 timeout15s nel vecchio harness PowerShell al primo Green/job3.12 (698 test/un errore), passato al retry sullo stesso codice. Le cause di022/023 restano da investigare: il successivo verde non costituisce correzione di quei problemi. [022](evidence/jrv-aud-022-20261107.json), [023](evidence/jrv-aud-023-20261107.json). Sintassi/probe nativi e Windows Search live passati, servizio ripristinato/fixture rimossa, package/publisher skipped. Nessun test funzionale Linux, PC Windows10/i3/HDD, nuova build, ZIP, merge o dato/configurazione personale modificato. Checkpoint successivo solo documentale. Prossimo JRV-AUD-005: verificare proprietà e concorrenza del backend nativo prima di correggere;022/023 aperti per affidabilità del collaudo prima della distribuzione.

## 7 novembre 2026 — JRV-AUD-004, seconda candidata; nuovo limite CI tracciato022

Red2 dc1e4f2 / run42332104260: nel job128280722034 Python3.12 i nuovi casi no-fresh pending/selezione e ledger sono falliti; il vecchio incastro invece non si riproduceva più. Questo conferma la regressione della candidata1 rilevata dalla review. La suite del job si interrompe poi per Tcl_AsyncDelete/Variable.__del__: nessun conteggio finale disponibile, non è un collaudo completo. JRV-AUD-022: crash confermato della suite Tkinter, causa da verificare (finalizzazione di oggetti Tk da thread diverso nel test003 Win32); priorità media per affidabilità CI, non ancora corretto.

Candidata2: RLock separato serializza lifecycle, reset e riattivazione; callback permessi mantengono solo manager-lock. Refresh iniziale completo prima della transazione invalida revoche esterne; metadati sotto manager-lock, reset file fuori manager-lock prima del rilascio lifecycle-lock. ProgramService.reset nella posizione originale, FileAccessService ripristinato identico alla base. Test reenable richiede attesa del reset e conserva la nuova richiesta; altri test no-fresh e ledger invariati. Design riesaminato indipendentemente senza ciclo bloccante individuato. AST/diff controllati; Green e review sul codice finale ancora pendenti, nessuna build/merge/dato personale.

## 7 novembre 2026 — JRV-AUD-004, rilievo bloccante della review e nuova riproduzione

La prima candidata elimina il ciclo ma il reset condizionale può saltare una revoca se la riattivazione arriva prima del reset: vecchi pending/risultati/selezione tornano validi. Caso anche sequenziale: ledger rimosso e subito set_enabled(True), che osserva inattivo nel refresh iniziale e attivo alla fine senza invalidare. Rilievo statico importante del revisore; non dichiarato ancora riprodotto su Windows. Aggiunte prove con risultati/selezione reali, reenable senza nuova richiesta e ledger mancante. La candidata corrente è pubblicata solo per ottenere Red2, non è pronta. Prossima correzione proposta: serializzare i lifecycle separatamente dai permessi, completare reset fuori dal lock manager prima della riattivazione e fare refresh iniziale completo prima della transazione. Nessuna nuova build o merge.

## 7 novembre 2026 — JRV-AUD-004 confermata, candidata in verifica

Red baa9317 / run42331515560, job128278876066 Python3.11.9:692 test/quattro fallimenti senza errori. Nei quattro lifecycle reader e changer restano bloccati dopo join, con entrambi i confini raggiunti e lock reali. Causa: manager→file.reset e pending→manager.files_enabled. Candidata: guardia comune per refresh/install/set_enabled/remove; refresh record separato da reset file, eseguito dopo rilascio del lock esterno anche su return/eccezione. Reset condizionale ricontrolla attivazione sotto lock file per non cancellare richieste successive alla riattivazione.

Scartata prima di implementarla la proposta iniziale di callback senza lock: potrebbe leggere il vecchio enabled=True durante una revoca ancora in I/O. I callback mantengono il lock transazionale; ProgramService.reset non bloccante conservato nella posizione originale. Nuove prove: revoca durante transazione, reset ritardato dopo reenable, limiti per operazione/copie dei descrittori, refresh attivo che conserva il chiarimento e policy. AST/diff verificati; Green Windows e review indipendente pendenti. Nessun test funzionale Linux, build, merge o dato/configurazione personale.

## 7 novembre 2026 — JRV-AUD-004, riproduzione in corso

Base386fcd1, ramo separato fix/jrv-aud-004-addon-locks-20261107,001/002/003 conservate. Piano docs/superpowers/plans/2026-11-07-jrv-aud-004-addon-locks.md. Test Windows con manager/servizio/lock e file temporanei reali, eventi ai confini enabled/reset e processo isolato: chiarimento pendente insieme a disable/remove/upgrade/revoca ledger. Runtime invariato; inversione dei lock ancora ipotesi statica fino al Red. Proposta minima: leggere lo snapshot già pubblicato nei callback file senza lock inverso, mantenendo reset/revoca sincroni. Nessun test funzionale Linux, build, merge o dato personale.

## 7 novembre 2026 — JRV-AUD-003 verificata su Windows, non distribuita

Correzione4dabf48fd71e433d43a6b97ae1a057730b1ee3b8, [PR draft36](https://github.com/MATRIXNEO23/jarvis/pull/36), dipendente dalla35. [Run42330792141](https://github.com/MATRIXNEO23/jarvis/actions/runs/42330792141) SUCCESS:691 test per Python3.11.9/3.12.10; nove test nuovi con Edit Windows nativo e file temporanei. Red precedente684 test/due asserzioni fallite senza errori per ciascun job. [Evidenza](evidence/jrv-aud-003-20261107.json).

Salva e chiudi ora distingue snapshot salvato e scarto esplicito. La chiusura verifica il testo sotto blocco temporaneo della digitazione; modifiche sopraggiunte lasciano aperti editor/sessione e copia salvata. Ripristino dirty/stile originale anche dopo lock parzialmente applicato, lettura/PostMessage/timeout e cambio titolo. close_clean confronta la copia su disco; save_only, scarto autorizzato e versioni immutabili conservati. Review indipendente senza difetti bloccanti, lacune iniziali titolo/documentazione risolte e ricontrollate; cinque blob runtime/test identici ai remoti.

Sintassi/probe nativi e Windows Search live passati, servizio ripristinato/fixture rimossa; package/publisher skipped. Nessun test funzionale Linux, Notepad installato/Windows10/Pavilion, nuova build, ZIP, merge o modifica dati/configurazioni utente. Il parent nascosto di test non replica il dialogo Save di Notepad. Readonly tutela la digitazione, non scritture programmatiche di automazioni estranee; un processo bloccato può impedire anche il tentativo di ripristino. Checkpoint successivo solo documentale. Prossimo JRV-AUD-004: riprodurre la possibile inversione dei lock add-on/file con barriere, ancora da confermare.

## 7 novembre 2026 — JRV-AUD-003 confermata, candidata in verifica

Red f92eef2 / run42330339439:684 test per Python3.11/3.12, due fallimenti comportamentali senza errori. La finestra Edit reale accetta digitazione dopo dirty-clear; modifica durante I/O chiusa e scartata. Candidata: salva e chiudi passa lo snapshot salvato anziché consenso allo scarto; bridge protegge Edit in sola lettura dal confronto finale alla chiusura, ripristina dirty/stile originale in errore. close_clean richiede copia salvata corrispondente. Scarto esplicito e save_only preservati. Test aggiunti per lock rifiutato/timeout dopo applicazione, lettura, PostMessage, chiusura non confermata, stile iniziale readonly, titolo rinominato, versioni immutabili e identità estranea. AST/diff controllati, Green Windows e review indipendente pendenti; nessun test funzionale Linux, Notepad/Pavilion personale, build o merge.

## 7 novembre 2026 — JRV-AUD-003, riproduzione in corso

Base784edad, ramo isolato fix/jrv-aud-003-save-close-20261107 con001/002 conservate. Piano docs/superpowers/plans/2026-11-07-jrv-aud-003-save-close.md. Test Windows: worker/orchestratore/bridge reali, file temporanei e controllo Edit nativo nascosto del solo test; modifica durante I/O e digitazione tra dirty-clear/WM_CLOSE. Runtime ancora invariato, rischio non ancora riprodotto. Prossimo passo Red Windows; poi confronto del testo con blocco temporaneo della digitazione e ripristino in errore. Nessun Notepad personale, test Linux, build o merge.

## 7 novembre 2026 — JRV-AUD-002 verificata su Windows, non distribuita

Correzione `05926bdc34516624eb3c5ef21321b801cb466586`, [PR draft35](https://github.com/MATRIXNEO23/jarvis/pull/35), dipendente dalla34. [Run42329422636](https://github.com/MATRIXNEO23/jarvis/actions/runs/42329422636) SUCCESS:682 test per Python3.11.9/3.12.10, sintassi/probe nativi e indice Windows live passati; servizio e fixture ripristinati. Red precedente675 test/cinque asserzioni fallite senza errori fixture. [Evidenza](evidence/jrv-aud-002-20261107.json).

Un solo backend, buffer globale di16 scambi partizionati per progetto/generale, nessuna persistenza aggiunta. Solo turni accettati nel poll con epoca/progetto validi entrano nella memoria e nel follow-up app. Verificati ritorno al progetto, revoca voce/testo, contesto catturato prima del worker, budget globale, commit idempotente, poll non bloccato dall'inferenza, isolamento Telegram/picker e conservazione dei ricordi su disco. Review indipendente senza difetti bloccanti; coperte anche le lacune iniziali follow-up/poll concorrente. I blob runtime/test condivisi coincidono col commit remoto. Nessun test account/microfono/GGUF/Pavilion, nuova build, ZIP o merge. Il checkpoint successivo cambia solo documentazione. Prossimo ID003: riprodurre la modifica manuale durante salva e chiudi prima di correggere; il rischio resta da confermare.

## 7 novembre 2026 — JRV-AUD-002, candidata in verifica

Red Windows run42328846716 / job128270410711 su a988b63:675 test, cinque fallimenti comportamentali, nessun errore fixture. Riprodotti contaminazione A→generale/B, turni vocali/scritti revocati ancora ricordati e contesto errato del worker. Piano invariato: un backend,32 messaggi globali, nessun archivio persistente modificato.

Candidata: buffer di16 scambi etichettati per contesto; prepare_turn produce una proposta, il poll UI la accetta solo se epoca/progetto sono correnti. Commit idempotente con lock breve distinto dall'inferenza; follow-up app aggiornato soltanto dopo accettazione. API ask sincrona e chat isolata Telegram/picker conservate. Nuove prove di budget, commit differito/idempotente, metadati non bloccati dall'inferenza e contesto invalido. AST/diff controllati; Green Windows e review indipendente ancora da completare. Nessun test funzionale Linux, GGUF/account reale, build o merge. PR35 dipende da PR34.

## 7 novembre 2026 — JRV-AUD-002, riproduzione in corso

Base53717eb con001 conservata; ramo separato fix/jrv-aud-002-gemma-history-20261107. Piano docs/superpowers/plans/2026-11-07-jrv-aud-002-history.md. Test nuovi dei callback reali con NativeConversationSession e WorkspaceMemory temporanei: progetti/generale, risultato revocato prima del poll, cambio contesto durante inferenza e prima dell'avvio worker, conservazione dati persistenti. Backend controllato senza DLL/GGUF/account. Runtime invariato. Prossimo passo: Red Windows, poi partizionare un buffer globale limitato e inserire nella memoria soltanto risposte accettate dalla UI. Nessun test funzionale Linux, build, ZIP o merge.

## 7 novembre 2026 — JRV-AUD-001 verificata su Windows, non distribuita

Correzione runtime `daa7a6a8760688f6081bca95ee6c9d6df6ac8ce8`, [PR draft34](https://github.com/MATRIXNEO23/jarvis/pull/34). [Run42327319575](https://github.com/MATRIXNEO23/jarvis/actions/runs/42327319575) SUCCESS: 670 test per Python3.11.9 e3.12.10, sintassi/probe nativi e Windows Search live passati; servizio e fixture ripristinati. I14 test aggiunti coprono policy, revoca, file, diagnosi e planner. Red precedente659 test/cinque asserzioni fallite conservato. Review indipendente in sola lettura: nessun difetto bloccante; lacune iniziali file/diagnosi coperte dai test aggiunti. [Evidenza](evidence/jrv-aud-001-20261107.json).

Mai prevale su consenso precedente e sessione Telegram; ask conserva la conferma; allowed evita la richiesta ripetuta; il grant viene ricontrollato prima della pipe. File assente/danneggiato nega; nessuna preferenza migrata o riscritta. Login e autorizzazioni alle azioni restano separati. Nessuna nuova build, ZIP, merge, modifica ai dati o prova di account/microfono/Pavilion. La005 e le candidate Gemma distribuite restano invariate. Il checkpoint seguente cambia solo documentazione, non i blob runtime/test verificati. Prossimo passo JRV-AUD-002: isolamento dello storico Gemma tra progetti/generale, senza scaricare il backend caricato; riproduzione Windows prima del fix.

## 7 novembre 2026 — JRV-AUD-001, correzione candidata in verifica

Red Windows run42326631728 / job128263321901 sul commit4b21693: 659 test, cinque asserzioni fallite nei tre nuovi test di integrazione, nessun errore fixture. Riprodotti il bypass di Mai (tre azioni console e sessione Telegram) e il dialogo superfluo per allowed. Ramo correttivo isolato; PR draft34. Nessun pacchetto o pubblicazione Download.

La candidata introduce grant di richiesta per funzione, riletto prima dell'invio: never nega, ask richiede conferma, allowed evita il dialogo. Integra console, raffinamento e spiegazione file, planner, diagnosi e Telegram; il consenso di sessione non supera Mai. UI estesa ai permessi effettivi di spiegazione file, planner e diagnosi. Configurazioni mancanti/danneggiate restano negate; nessun file utente scritto. Fixture storiche aggiornate con permessi ask espliciti solo in profili temporanei. Verifica statica AST/diff eseguita; Green Windows e review in corso, nessuna dichiarazione di fix verificato. Prossimo controllo: matrice completa Windows 3.11/3.12 e regressioni.

## 7 novembre 2026 — JRV-AUD-001, riproduzione in corso

Autorizzate le correzioni dell'audit con spiegazioni sintetiche. Base evoluta61a95f8, ramo isolato fix/jrv-aud-001-permissions-20261107. Prima unità: permessi GPT per funzione. Aggiunti piano docs/superpowers/plans/2026-11-07-jrv-aud-001-permissions.md e tests/test_online_permissions_integration.py: Mai nella console anche dopo conferma, allowed senza dialogo e revoca prima del worker, Mai Telegram prevale sul consenso di sessione. Solo callback reali con confini controllati e profilo temporaneo; nessun account/dispositivo. Runtime ancora invariato. Prossimo controllo: Red Windows; nessun test funzionale Linux, nuova build, ZIP, merge o modifica ai dati.

# JARVIS — handoff tecnico, mappa architetturale e checkpoint (2026-11-05)

## 6 novembre 2026 — Carattere di Gemma locale

La configurazione del modello include istruzioni facoltative di stile (240 caratteri). Il valore è locale e compatibile con i profili precedenti. Si applica alle nuove risposte della conversazione Gemma e a Prova generazione, senza richiedere un ricaricamento per il solo cambio di stile. Si preserva la domanda se il budget è stretto. Le risposte Telegram continuano a usare il contesto del contatto. La prima run 42268657858 ha rilevato un'asserzione UI eseguita dopo Ripristina anziché dopo Salva. Sul commit correttivo `3c71ca4` le due suite Windows e la verifica dello ZIP estratto sono passate nella [run 42269297921](https://github.com/MATRIXNEO23/jarvis/actions/runs/42269297921). Resta il collaudo con il GGUF sul Pavilion.

## 6 novembre 2026 — Consenso GPT per Telegram durante la sessione

La modalità predefinita resta la conferma per messaggio. L'opzione esplicita in Impostazioni → Telegram autorizza l'invio dei messaggi e del contesto recente dei soli contatti selezionati. Il consenso è solo in RAM e si azzera disattivando o disconnettendo GPT oppure chiudendo Jarvis. Il trasporto ricontrolla token, epoca e bridge prima dell'invio e scarta risposte obsolete. Console e planner mantengono i propri controlli. Le due suite Windows e la verifica dello ZIP estratto sono passate nella [run 42246973814](https://github.com/MATRIXNEO23/jarvis/actions/runs/42246973814). I test simulano conferma, rifiuto, sessione e revoca. Resta il collaudo con l'account reale sul Pavilion.

## 6 novembre 2026 — Indicatore Telegram dei messaggi da vedere

Base `0055607`. Il pallino del contatto riusa il conteggio dei messaggi in arrivo non ancora visti. L'animazione HUD esistente alterna due tonalità viola per i nuovi messaggi e mantiene una tonalità tenue e fissa dopo l'apertura della cronologia. Il clic registra solo gli ID in arrivo mostrati, così un messaggio concorrente resta da vedere. Nessuna modifica alle ricevute di Telegram. Le due suite Windows e la verifica dello ZIP estratto sono passate nella [run 42221709872](https://github.com/MATRIXNEO23/jarvis/actions/runs/42221709872) sul commit `addc19e`. Resta la prova visiva sul Pavilion. Nessuna pubblicazione in Download.

## Telegram con Gemma locale

Il bridge mantiene contatti autorizzati, contesto recente della singola chat, presentazione, sintesi e invio dei vocali. Se GPT è attivo e connesso, resta il consenso per richiesta. Se GPT non è disponibile, Gemma riusa il modello caricato senza accedere alla cronologia della console o dei progetti. Il collaudo con account Telegram e modello reali resta separato dalla CI Windows.

## 6 novembre 2026 — rimossa la barra sostitutiva

La candidata `Download/Jarvis-Gemma-Comandi-e-Interfaccia-6e73e3b.zip` è pubblicata su main `14967a4`. Il commit `6e73e3b` mantiene solo i tre pulsanti, integrati nell'intestazione HUD esistente o raggruppati in alto a destra nelle finestre secondarie. Eliminata la fascia aggiuntiva con il titolo. I dialoghi nativi Windows mantengono l'aspetto di sistema. [Suite Windows, archivio estratto e pubblicazione](https://github.com/MATRIXNEO23/jarvis/actions/runs/42147766728) riusciti.

## Segnalazione Pavilion — dialogo Gemma e apertura app

La foto mostra «Apri Netflix» come risposta della chat. Il percorso scritto di Gemma non condivideva la selezione app del percorso vocale. Ora «con Gemma» può essere scritto oppure pronunciato. Dopo uno scambio recente che identifica una sola app autorizzata, una richiesta esplicita come «me lo apri?» passa al motore come proposta da confermare. Il testo del dialogo continua ad andare in chat. Scambio valido per 120 secondi e solo nella stessa epoca di conversazione. [Matrice Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42145643937) superati sul commit `0d99357`. Nessuna pubblicazione in Download.

## Finestre Windows con comandi integrati

Le finestre Tk di Jarvis usano una barra interna scura con riduci, massimizza/ripristina e chiudi. La rimozione della cornice avviene sul wrapper Win32 e mantiene i protocolli di chiusura Tk. La barra si applica anche alle finestre secondarie mappate dopo l’avvio e alla finestra separata di configurazione segreti Telegram. Le finestre native di sistema seguono l'aspetto Windows. La run [42144862058](https://github.com/MATRIXNEO23/jarvis/actions/runs/42144862058) sul commit `72af40e` ha superato 639 test per versione Python, compresa la prova Windows della barra su finestra principale e secondaria. Il pacchetto CI è stato generato e verificato dopo estrazione. Nessuna pubblicazione in `Download` per questa modifica.

## 6 novembre 2026 — candidata Gemma pubblicata

La [run Windows 42142495567](https://github.com/MATRIXNEO23/jarvis/actions/runs/42142495567) sul commit `5d554c8` ha superato la matrice Windows, i 26 test mirati dal pacchetto estratto e il caricamento della DLL inclusa. Il commit `7088b95` su main ha pubblicato `Download/Jarvis-Gemma-Avvio-Programmi-5d554c8.zip` e aggiornato `Download/README.md`. Archivio: 8.093.345 byte, SHA-256 `e54912b4e3de94c06dc654cd2fc4f64b698f0f2f2249ff67dab6e091022b8944`. Candidata per il collaudo su Pavilion. Voce, Gemma e app reali restano da provare.

## 6 novembre 2026 — avvio app con varianti locali e prova Gemma

I commit `9c08935` e `56fd9e4` riusano il catalogo e le autorizzazioni di Programmi e app. Una selezione abilita i verbi comuni. Frase senza nome, risposta successiva con nome esatto e suggerimenti per somiglianza sono stati verificati con launcher controllato. Il suggerimento Gemma richiede il prefisso vocale «con Gemma» in modalità conversazione e una conferma della scelta. La prova del selettore usa un modello simulato e verifica una generazione e l'esclusione della cronologia.

La [run Windows 42139706373](https://github.com/MATRIXNEO23/jarvis/actions/runs/42139706373) su `56fd9e4` ha superato 638 test per versione di Python. Restano il collaudo con voce, Gemma e app reali sul Pavilion, e il gate di rilascio. Nessuna nuova build pubblicata.

## Apertura locale e prova Gemma su richiesta

Programmi e app riconosce anche aprimi, avviami, lanciami, esegui, fai partire e metti in esecuzione. Una frase senza nome apre un chiarimento locale. I nomi simili suggeriscono un'app autorizzata e attendono una scelta. La prova vocale esplicita «Jarvis, con Gemma, mi serve qualcosa per vedere un film» seleziona una proposta fra 1–12 app abilitate e disponibili, senza cronologia nel prompt. Il motore chiede conferma e applica i permessi correnti. Gemma usa una sola generazione con il modello già caricato se disponibile. Prova Windows CI e collaudo Pavilion da registrare.

## 6 novembre 2026 — JRV-004, verifica Windows

La [run 42129127625](https://github.com/MATRIXNEO23/jarvis/actions/runs/42129127625) sul commit `e51c269` ha superato 635 test per job con Python 3.11 e 3.12. È passata anche la prova live Windows Search sul job previsto. Copertura mirata nei log: rifiuto e revoca dei callback, Telegram simulato, disconnessione immediata, revoca durante avvio del bridge e toggle HUD.

`dea28e6`: consenso console e planner. `4dd0e1f`: consenso Telegram e generazione di revoca del planner. `43d29e4`: ripristina il guard esplicito di rifiuto dell'autodiagnosi, mantenendo il controllo dell'epoca. `36d549e`: verifica nel trasporto prima dell'invio e scarto dei piani di un contesto superato. `e51c269`: inizializza lo stato Telegram nella fixture del pannello rapido dopo il fallimento della run 42129015218. Il risultato è simulato per account GPT e Telegram. Restano la configurazione persistente per funzionalità, le prove con account reale e il gate di rilascio. Una revoca dopo l'invio può scartare la risposta in Telegram, mentre i dati già trasmessi restano fuori dal controllo di Jarvis.

Prossimo intervento: JRV-005, isolare la cronologia Gemma tra progetto e contesto generale conservando il modello caricato e gli archivi persistenti. Verificare anche la configurazione applicata al provider quando si modificano contesto massimo e output.

## JRV-004 — Telegram e revoca durante la conferma

Il worker Telegram attende fino a 30 secondi una decisione monouso della console prima di inviare messaggio e contesto recente a GPT. Il collegamento Telegram e il recapito dei messaggi approvati dal proprietario restano separati. Una richiesta scaduta o riferita a un bridge disattivato viene scartata. Il pianificatore usa lo stesso dialogo e conserva la generazione di consenso fino al worker. La disattivazione o la perdita del collegamento GPT revoca l'accesso del worker Telegram. Verifica Windows e collaudo con account reale distinti.

Il trasporto ricontrolla il consenso dopo l’avvio del bridge e prima di scrivere la richiesta. La disconnessione revoca subito planner e Telegram. Telegram scarta le risposte arrivate dopo la revoca. Un piano ricevuto o confermato dopo un cambio di contesto viene scartato prima dell’esecuzione.

## 6 novembre 2026 — JRV-004, consenso per richiesta dalla console

Il percorso `run_gpt` richiede il consenso prima di avviare un worker di inferenza e ricontrolla connessione, stato ed epoca dopo il dialogo. Login, stato e disconnessione seguono il loro percorso. Il raffinamento chiede prima di consumare il token, la spiegazione distingue il testo dell'anteprima, il chiarimento progetto conserva il riepilogo locale e l'autodiagnosi riusa il consenso specifico già esistente. I comandi locali precedono il dialogo del pulsante GPT. Il pianificatore separa il consenso a inviare la richiesta dall'approvazione del piano. Aggiornati i test Windows dei callback. Verifica CI sul nuovo commit in attesa. Restano il worker Telegram, la policy persistente per funzionalità e il collaudo con account reale.

## Verifica Windows e blocchi di rilascio

`db0b3a4`: [run 42113303954](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113303954) verde su entrambi i job, 628 test per job. Il test di finestra Tk reale e i casi di accettazione, PID e finestra sono passati. Nessuna prova di apertura Netflix sul Pavilion.

`09c5e95`: [run 42113573907](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113573907) ha riprodotto un errore della nuova fixture, che non passava `queue` all'esecuzione isolata del poll. `75bef3a` ripristina la dipendenza mantenendo le asserzioni. Nella [run 42113970995](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113970995) i test unitari risultano verdi in entrambe le versioni Python. I job 127548563547 e 127548564393 hanno registrato 629 test ciascuno e hanno superato la nuova prova sulla risposta vocale obsoleta. La prova live di Windows Search è passata nel job Python 3.12 previsto. L'intera matrice è conclusa con successo.

Prossimo intervento JRV-004: trattare separatamente login e inferenza. Il pulsante GPT verifica un consenso condizionato alla presenza della configurazione Gemma prima di instradare azioni locali. Il chiarimento progetto, il raffinamento file e la spiegazione del file arrivano a `run_gpt`. Telegram chiama direttamente `service.call` dal worker e il pianificatore riceve lo stesso servizio. L'autodiagnosi ha un dialogo già dedicato. Per ogni percorso verificare esplicita autorizzazione, rifiuto, revoca e assenza di invio di contenuti altrimenti. Conservare il percorso locale e il consenso alle azioni come controlli distinti.

Per JRV-011 resta da collegare il pacchetto a una dipendenza esplicita dalla matrice Windows sullo stesso SHA, mantenendo separata la verifica dell'archivio estratto. La DLL no-AVX2 deve restare disponibile e verificabile per una ricostruzione futura. Il rilascio pubblico dipende anche dai collaudi obbligatori sul Pavilion, ancora aperti. Nessuna build pubblicata nel checkpoint.

## Voce Gemma: risposta in corso e cambi di contesto

La run [42112965273](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112965273) su `cfa0e19` ha concluso la matrice Windows con successo. `db0b3a4` ha introdotto l'osservazione del PID e della finestra, run [42113303954](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113303954). Il controllo osserva una finestra Win32 con titolo dello stesso PID, non minimizzata e non nascosta da DWM. Può rilevare una finestra già esistente o coperta. L'app Store può usare un altro processo per la finestra.

JRV-001/002: `jarvis.py` descrive Gemma locale quando si attiva la modalità conversazione. Il risultato vocale, compreso l'errore, ora appartiene alla generazione di contesto che ha avviato la richiesta: il poll scarta la risposta quando nel frattempo sono cambiati modalità, progetto o stato GPT. La risposta scritta mantiene il percorso esistente. La nuova prova esegue il callback reale su eventi controllati. Restano microfono e TTS reali, oltre all'isolamento della cronologia interna della sessione Gemma (JRV-005).

## Checkpoint Windows e osservazione avvio programmi

La matrice Windows della run [42112346657](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112346657) su `57c3dd1` ha completato 626 test per job con esito OK. La revisione ha trovato il conflitto app/progetti nel ramo generico del parser. `c8c697c` ha riservato il ramo progetti esplicito, ma la run [42112742159](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112742159) ha riprodotto un errore del nuovo test: Accesso file, ancora attivo nella fixture, consumava «apri Netflix». `cfa0e19` isola il test del ramo di riserva nella run [42112965273](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112965273). Resta da verificare la precedenza app/file con i due componenti configurati insieme, mantenendo l'apertura implicita nella cartella Explorer.

JRV-003: `program_apps/native.py` conserva il PID fornito da Windows per l'attivazione Store o ricavato dall'handle ShellExecute. Il messaggio distingue accettazione, PID disponibile e osservazione immediata di una finestra Win32 visibile con lo stesso PID. App con finestra ospitata da un processo differente e finestre che appaiono più tardi richiedono verifica ulteriore. `tests/test_program_apps_native.py` copre i tre esiti e la prova Win32 su una finestra Tk controllata. Restano CI Windows sul commit, Netflix reale e affidabilità della corrispondenza finestra/app Store.

Altri blocchi registrati: il workflow ZIP scarica la DLL da un artefatto CI con scadenza 18 novembre 2026 e riscrive parti del runtime durante il packaging. La sessione Gemma conserva in RAM il dialogo anche quando cambia progetto e il provider già caricato conserva la configurazione precedente dopo un cambio delle impostazioni. Da verificare isolamento, aggiornamento della configurazione, consenso GPT, collaudi Pavilion e gate di rilascio.

## Riesame integrazione e programma di verifica

La run 42112126088 ha confermato la correzione del raffinamento file e del contesto in attesa. Il job 127542105108 ha chiuso con 2 fallimenti e 11 errori residui su 626 test. Il successivo checkpoint `57c3dd1` è in verifica nella run 42112346657. La revisione indipendente ha rilevato che anticipare il gestore progetti senza filtro avrebbe classificato «apri Netflix» come progetto quando l'add-on è spento. Il checkpoint successivo riserva i comandi che nominano esplicitamente un progetto e aggiunge il caso Netflix al test del callback di console.

| Sequenza | Integrazione | Prova richiesta |
| --- | --- | --- |
| 1 | File, voce, autodiagnosi, app e progetti | Callback reali con trascrizione e servizi controllati, suite Windows 3.11/3.12 |
| 2 | Gemma, TTS e hotword (JRV-001/002) | Output pulito nei due ingressi, ascolto automatico con hotword e standby manuale, collaudo Vosk/TTS sul Pavilion |
| 3 | Programmi e add-on (JRV-003/007) | Verificare precedenze, alias, revoca, accettazione Windows, PID osservabile e finestra associata. Collaudare Netflix con add-on attivo e app autorizzata |
| 4 | GPT e Telegram (JRV-004/008) | Inventario chiamate, consenso monouso prima dell'invio, rifiuto e nessun fallback implicito, collaudo account separato |
| 5 | Memoria, file e progetti (JRV-005/006/009) | Isolamento tra contesti, revoca permessi, conservazione dati esistenti, Windows Search e fallback su più unità |
| 6 | Risorse e rilascio (JRV-010/011) | Confronto con Kobold sul Pavilion, stessa configurazione. ZIP dallo stesso SHA collaudato, avvio da estrazione pulita e gate automatico senza dipendenza dal workflow assente su main |

Blocchi individuati da verificare: raffinamento file, spiegazione file e chiarimento progetto chiamano `run_gpt` senza passare dalla policy per funzionalità. Il launcher Store dispone di un PID ma lo scarta. L'attuale workflow Gemma manca su main e il percorso manuale può arrivare alla pubblicazione indipendentemente dalla suite. Lo ZIP modifica anche file Python in fase di assemblaggio, quindi i sorgenti della suite e quelli effettivamente distribuiti richiedono un controllo separato.

## 5 novembre 2026 — suite Windows del ramo Gemma

La run [42106340408](https://github.com/MATRIXNEO23/jarvis/actions/runs/42106340408) ha riprodotto 8 fallimenti e 13 errori su 626 test. `7ff60e2` collega il vero `ChatTransport` al servizio simulato in `tests/test_file_refinement.py`, usato anche da `tests/test_pending_file_context.py`. La relativa [run 42112126088](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112126088) è stata avviata sul commit esatto.

Il checkpoint corrente applica lo stesso cablaggio a `tests/test_activity_status.py`. La fixture in `tests/test_voice_corrections_review.py` riproduce il contenitore `[False]` usato dal callback. `tests/test_gpt_voice_addressing.py` verifica che Gemma occupata rifiuti solo la richiesta indirizzata e che il parlato ambientale non venga inviato o accodato. `tests/test_self_review.py` controlla la precedenza della diagnosi rispetto al percorso Gemma della voce e al percorso GPT del testo. In `jarvis.py` i progetti espliciti tornano a precedere il filtro generico di avvio app, dopo la gestione dei file.

Gate aperto: verificare test mirati e matrice Windows 3.11/3.12 sul checkpoint, quindi analizzare eventuali fallimenti residui. JRV-001 e JRV-002 richiedono ancora collaudo reale. JRV-003 non ha conferma di apertura Netflix. Il rilascio resta subordinato alle prove obbligatorie.

## Fonte di verità e stato
Repository: `MATRIXNEO23/jarvis`. Ramo di integrazione Gemma: `feature/gemma-local-20261104`. Pubblicazione ZIP su `main/Download/Jarvis-Gemma-PROVA-CORRETTA.zip`; pagina `main/Download/README.md`. Il ramo `main` contiene anche pubblicazioni automatiche: NON assumere che il codice applicativo su main coincida con il ramo Gemma. Verificare sempre ref/commit, ZIP e workflow prima di dichiarare un rilascio.

Checkpoint verificato: il modello Gemma risponde nella chat principale (test visivo dell'utente); la sintesi vocale è stata collegata via `speak_result` (commit `5481310272c474de9a8f210dd8d196cf39698627`), build Windows riuscita run `42081191577`. Il guardrail per richieste esplicite di avvio senza esecuzione è nel commit `950acac1ed3d33d0bae8f4428ed1be4e6350a99f`, build riuscita run `42081766861`, ZIP pubblicata su main. Non equivale a test reale del PC.

Problema Netflix: prima Gemma rispondeva «Ti aiuterò a avviare Netflix» senza prova dell'avvio; poi la console mostrava «PROGRAMMI > Non ho avviato il programma. Attiva Programmi e app...». L'utente ha confermato che Netflix era già spuntato ma l'add-on **Programmi e app era disattivato**. È la causa operativa individuata; l'utente deve ancora confermare un avvio riuscito dopo attivazione. NON registrare «Netflix funziona» come collaudato.

## Mappa di esecuzione (codice verificato sul ramo Gemma)
```text
Utente: tastiera / microfono (Vosk e controlli voce)
                 |
                 v
          jarvis.py (GUI, eventi, stato, console)
                 |
       +---------+---------------------+
       |                               |
  comandi espliciti                conversazione
  try_file_command                 send_console_input
       |                               |
  try_program_command             configurazione GGUF valida?
       |                            /             \
  ProgramService.parse_command    sì             no
       |                           |               |
  addon_manager.is_active       submit_gemma_trial  GPT solo secondo
       |                           |                impostazioni/permessi
  submit_local / LocalEngine       | 
       |                       NativeConversationSession
  execute_program                 -> NativeChatAdapter
       |                          -> NativeLocalProvider
  ProgramService.execute          -> NativeGemmaBridge
       |                          -> DLL KoboldCpp no-AVX2 / GGUF
  allowlist app, consenso,           |
  identità e disponibilità       poll_gemma_trial
       |                          -> write_line + speak_result
  program_apps/native.py
  avvio Windows EXE/LNK/Store
       |
  risultato reale in console / voce
```
Il modello non esegue programmi autonomamente: il testo libero generato non è un comando sicuro. Il servizio ProgramService verifica app consentita, identità, catalogo, disponibilità, ambiguità, revoca e permesso add-on. Evitare shell arbitraria e bypass delle spunte.

## File chiave
- `jarvis.py`: punto di composizione GUI, eventi voce/chat, `send_console_input`, `try_file_command`, `try_program_command`, `submit_local`, `submit_gpt`, `submit_gemma_trial`, `poll_gemma_trial`, `speak_result`. Attenzione ai rami di risposta e alle priorità di routing.
- `local_engine.py`: motore deterministico e TaskResult, delega alle capacità approvate; nessun codice generato eseguito.
- `addon_manager.py` / `addon_ui.py`: installazione, attivazione e permessi separati. Manifest `.jaddon` dichiarativi, nessun codice eseguibile nell'installazione.
- `program_apps/ProgrammiApp.jaddon`: azione `addon.programmi_app.avvia` -> `apps.launch`; **OFF iniziale**.
- `program_apps/service.py`: `launch_query`, `protected`, `blocked`, `parse_command`, `execute`, `save_preferences`, `refresh_catalog`. `available()` dipende da `enabled()`; la spunta della singola app NON abilita l'add-on. `programs.json` salva elenco, disponibilità, preferenze e alias. L'esecuzione richiede `enabled=True` per l'app e add-on attivo.
- `program_apps/native.py`, `windows_apps.ps1`: enumerazione e avvio app Windows (classiche/Store); `program_apps/ui.py`: selezione, alias, aggiornamento, test avvio.
- `local_model/native_config.py`, `native_settings.py`, `native_ui.py`: GGUF, DLL, threads, context_size, max_output, sampling; impostazioni configurabili.
- `local_model/native_conversation_session.py`: storico locale limitato, costruzione prompt con budget; esplicitamente nessuna azione desktop né fallback online.
- `local_model/native_chat_adapter.py`, `native_factory.py`, `native_initializer.py`, `native_provider.py`, `native_bridge.py`: trasporto e inferenza KoboldCpp in processo, senza servizio HTTP; errore nativo con status/stopreason.
- `local_model/online_permissions.py`: controlli permessi online; verificare TUTTI i percorsi prima di affermare che nessuna chiamata online parte senza consenso.
- `file_access/`: accesso file e ricerca; `project_voice.py`, `workspace_memory.py`, `conversation_memory.py`: progetti e continuità; `voice_control.py`, `speech_activity.py`: comandi e stato voce.
- `.github/workflows/gemma-windows-test-package.yml`: build prova Windows da ramo Gemma; scarica DLL no-AVX2 pinned, esegue test e pubblica ZIP su main. Trigger push include `jarvis.py`, `local_model/**`, build script e workflow; **modifiche solo a `program_apps/**` non attivano necessariamente questa build**.
- `tools/build_gemma_clean_trial.py`: creazione ZIP. `Download/README.md`: indice download. `docs/PROGRAMMI-APP-IMPLEMENTAZIONE-20261103.md`: design, controlli e prove precedenti.

## Vincoli e decisioni permanenti
Windows 10 x64, HP Pavilion i3-2100 (AVX, NO AVX2), 10 GB RAM, Radeon HD6450 1GB; zero costi extra, nessuna API a consumo. Preferire CPU no-AVX2 e mini-LLM locale; online solo con consenso esplicito. Gemma deve usare la chat principale e TTS esistente, non una chat separata. Tutte le nuove capacità preferibilmente add-on `.jaddon`, core solo per collegamenti tecnici motivati. Non migrare indiscriminatamente le vecchie funzioni. App Store e desktop devono essere supportate, ma solo se selezionate. Sinonimi e alias vocali; non eseguire comandi senza autorizzazione. Microfono in standby/spento all'avvio, poi controllo manuale e wake word «Jarvis»; evitare consumo token a microfono acceso. Preservare preferenze, memoria, progetti, salvataggi e rollback. Non dichiarare un successo basandosi sulla sola risposta testuale del modello.

## Rischi / opportunità di miglioramento
1. Diagnostica specifica di `try_program_command`: distinguere add-on OFF, app non selezionata, catalogo obsoleto, parser non riconosce, ambiguità, permesso revocato, avvio Windows fallito. Il guardrail del commit `950acac` usa ancora un messaggio generico; non è una riparazione del launcher.
2. Allineare messaggi TTS/console all'esito `ProgramResult`, non al testo del modello. Eseguire prove reali per EXE/LNK e Store (Netflix) su Windows.
3. Testare input sia scritto sia vocale (wake word, varianti «apri», «avvia», alias) e tutte le combinazioni: add-on OFF/ON, app non spuntata/spuntata, app assente, due match, modifica/revoca consenso.
4. Verificare che la sintesi vocale non blocchi la UI e rispetti mute e preferenze; testare risposte Gemma e errori.
5. Verificare l'integrazione tra modello locale e azioni: le richieste non parseabili non devono diventare «ho fatto» fittizi; proporre eventualmente un intent strutturato validato, senza dare al modello privilegi di esecuzione.
6. Audit di tutti i percorsi online (chat, voce, fallback, comandi GPT) per conferma esplicita e zero traffico non autorizzato.
7. Test regressione, benchmark reali su CPU AVX-only (RAM, latenza, TTFT), timeout e recupero errori; nessuna garanzia di prestazioni senza misure.

## Ripresa operativa per un nuovo agente / programma
1. Aprire questo file e `docs/PROGRAMMI-APP-IMPLEMENTAZIONE-20261103.md`; verificare SHA corrente di main e ramo Gemma.
2. Leggere `jarvis.py` (funzioni nominate sopra), `addon_manager.py`, `program_apps/service.py`, `program_apps/native.py`, `local_engine.py`, `local_model/native_conversation_session.py`.
3. Chiedere soltanto l'esito mancante: «Dopo aver attivato l'add-on, Netflix si apre?». Non assumere fallimento o successo.
4. Se fallisce, riprodurre con app spuntata e add-on ON, aggiungere test mirato e diagnostica, correggere causa minima, preservare permessi e percorsi esistenti.
5. Eseguire test Windows, compilare ZIP, verificare workflow e artefatto pubblicato, aggiornare `Download/README.md` con nome chiaro, commit e stato di collaudo. Evitare di dire «pubblicato» prima di controllare.
6. Aggiornare questo handoff dopo ogni modifica: data, ref, commit, test, ZIP, risultati reali, problemi aperti. Nessun lavoro in background presunto.

## Riferimenti release
- Gemma chat/voce: `5481310`, run `42081191577`.
- Guardrail programmi: `950acac`, run `42081766861`.
- README Download aggiornato: `7e1cfad8113205a266d63785c374dc967116f7a9`.
- URL ZIP: `https://github.com/MATRIXNEO23/jarvis/raw/refs/heads/main/Download/Jarvis-Gemma-PROVA-CORRETTA.zip`.
- **Non ancora collaudato**: Netflix dopo riattivazione add-on; TTS reale su Pavilion.

## JRV-002 — console senza trascrizione vocale, 6 novembre 2026

Confronto tra le candidate `f387779` e `9adc86e`: il percorso da `voice_text` alla riga `TU` non è cambiato con Telegram. Riprodotti due difetti: il profilo Gemma ignorava un modello Vosk presente solo nel profilo sorgente del launcher e lo stato generico di microfono spento sostituiva il messaggio di errore.

Jarvis ora cerca il modello anche nel profilo sorgente e conserva l'errore di avvio del microfono, visibile anche in console. Restano il controllo della hotword e la modalità selezionata. Le due regressioni riprodotte falliscono prima del fix e passano dopo. Suite Windows e prova acustica sul Pavilion da verificare.

## JRV-002 — Ascolto continuo senza parola di richiamo

Il richiamo è richiesto in modalità Hey Jarvis. Ascolto continuo accetta la trascrizione direttamente. Entrambe mostrano sotto TU le richieste riconosciute, provano prima i gestori locali e usano Gemma per le richieste rimaste senza risposta. Durante la dettatura manuale le frasi libere vanno al campo di destinazione e il comando esplicito di arresto funziona anche senza prefisso. Il collaudo acustico sul Pavilion resta da fare.
