# JRV-AUD-022 — ownership degli oggetti Tk nelle fixture Windows

Stato: riproduzione controllata da acquisire, causa ancora probabile. Nessuna nuova build.
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
