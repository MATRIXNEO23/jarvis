# JRV-AUD-022 — ownership degli oggetti Tk nelle fixture Windows

Stato: difetto delle quattro fixture corretto e verificato in Windows. Nessuna nuova build. Sourceverde `3cd88a04b3a645257bc77c24bfcc9cd5fe5770b4`.
Compagna della021 nella [bozza51](https://github.com/MATRIXNEO23/jarvis/pull/51), per dipendenza del collaudo; runtimeTTS invariato dalla candidata `6504abffe0553461a2f44c07c9833d67a2abf2e1`.
[Specifica](superpowers/specs/2026-11-07-jrv-aud-022-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-022-fix.md).

## Sintomo storico e ricorrenza

L'[evidenza originale](evidence/jrv-aud-022-20261107.json) conserva source dc1e4f2/run42332104260/job128280722034 Python3.12.10: Variable.__del__/Image.__del__ su thread errato eTcl_AsyncDelete, senza riepilogo completo. Il test attivo DocumentSaveRace usa un worker Win32 senza Tk; non prova che il documento sia responsabile degli oggetti Tk precedenti.

Ricorrenza source0216504abffe/run42363252951/job128375837908 Python3.12.10: stesso sintomo durante test_clean_close_requires_current_text_to_match_saved_copy, prima dei nuovi021. Nessun conteggio finale inventato. Python3.11.9 job128375837812 dello stesso source passa900test in172.068s, tutti16nuoviTTS; Searchlive3.12 passa con servizio e fixture ripristinati. Green completo021 non dichiarato, nessun retry cieco.

## Ipotesi e regressione prima della correzione

Fixture HUD già chiuse possono lasciare cicli di variabili/immagini Tk, poi raccolti dal GC su un worker non proprietario. Nuovo tests/test_aa_tk_lifetime.py: un metodo e quattro subtest in figli separati, senza creare Tk nel processo padre. Ogni figlio esegue una fixture reale con il suo teardown (ActivityStatus, AnimatedHUD, header o HUD nativo), richiede successo reale senza skip e poi forza gc.collect da worker. GC automatico spento soltanto nel figlio per rendere osservabile quel passaggio, senza sopprimere errori/finalizer. Poller di rete isolato, nessun audio/account/profilo reale.

Diagnostica immediata con stadio e ID thread, stderr del figlio e timeout45s; un eventuale fatal rimane nel figlio e viene letto dal padre.901test attesi se la suite completa. Nessuna modifica ai teardown o al GC dell'app prima dell'evidenza. Review preventiva readonly da acquisire; successivo intervento limitato alle fixture dimostrate, poi Green completo Windows3.11/3.12 con021.

## Limiti

La riproduzione proposta riguarda ownership delle fixture, non certifica ogni possibile ciclo del runtime Tk. Non attribuisce a priori tutte le vecchie interruzioni a un unico oggetto. Non cambia comandi, dati, microfono, modelli o stato Windows dell'utente. Nessuna esecuzione funzionale Linux, build/ZIP/merge/release, disabilitazione test o nuova dipendenza.023 distinto e aperto.

## Red controllato e correzione delle fixture

Source `5991813f4c2add224e50f375ea36b8838fd1823b`, run42363972403. Python3.11.9 job128378016116:901test in171.384s,4failure0errori, tutti i quattro subtest di finalizzazione. Python3.12.10 job128378016392 stampa gli stessi quattro figli falliti, poi il padre abortisce di nuovo durante DocumentSaveRace: nessun riepilogo finale attribuito. Tutti gli8figli completano prima la fixture con successo e poi abortiscono (2147483651) sul worker GC, con Variable.__del__/Tcl_AsyncDelete; AnimatedHUD mostra anche Image.__del__ reale su entrambe le versioni. [Evidenza controllata](evidence/jrv-aud-022-controlled-red-20261107.json). Difetto dei quattro grafi confermato; non viene identificata retroattivamente l'identità di ogni oggetto del vecchio aborto.

Correzione limitata a quattro file test. ActivityStatus/AnimatedHUD/NativeHud raccolgono nel teardown sul thread principale, dopo che i riferimenti locali del metodo sono usciti. Header ha anche il ciclo self/env/callback e campi self.hud/root: chiude HUD, sostituisce provider, svuota env, distrugge root e ritira i riferimenti prima della raccolta. Tutte le asserzioni originali rimangono; nessuna modifica al GC globale dell'app o al runtime grafico.

Review preventiva rafforza diagnosticaTimeout e copertura Image: il probe finale assegna una PhotoImage reale1x1 come foglia al HUD, osservata soltanto con WeakSet/contatore, senza aggiungere cicli o trattenere il proprietario. Richiede creazione e assenza dopoGC. È una prova deterministica di risorsa Image, non della prontezza del renderer raster asincrono. Questi rafforzamenti seguono il primo sourceRed, senza rivendicare un altroRed. RuntimeTTS SHA c02a4a4ebb339b93a1eade0cc37b054d19c385e2 invariato da6504. Green completo021/022 ancora necessario.

Review correttiva indipendente readonly completata: log Red letti, cleanup sul thread principale e rilascio dei riferimenti header giudicati coerenti, nessun blocco rilevato. Nessun test eseguito dal reviewer; Green ancora necessario.

## Green Windows e ambito della risoluzione

Run42364574425 SUCCESS,901test per Python3.11.9 (job128379821296,180.165s) e3.12.10 (job128379821451,208.118s),0failure/errori/skip. Tutti gli8figli del probe passano la fixture, creano una vera immagine e ne osservano0residui prima della raccolta dal worker; completano conreturncode0 e stderr vuoto. Nessuna eccezione di finalizer nascosta e nessun fatal nel padre. I16nuovi controlliTTS passano su entrambe le versioni; il suo runtime non cambia per022.

L'evidenza conferma la correzione dei quattro grafi riprodotti e la nuova suite completa. Il sintomo storico è coerente con questa causa, ma non vengono identificati singolarmente gli oggetti di ogni vecchio aborto né garantita ogni altra finestra runtime. Nessun GC dell'app modificato. [Evidenza021/022](evidence/jrv-aud-021-fix-20261107.json); storia e Red022 preservati nell'evidenza originale/controllata. Sintassi/probe passati, Searchlive3.12 con ripristino servizio/fixture; nessun build/estrazione/pubblicazione o test funzionale Linux.023 distinto aperto.
