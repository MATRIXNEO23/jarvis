# ARCH-01 F3 — diagnostica prompt, provenienza e misurazioni, senza ottimizzare il modello

**Data apertura:** 8 novembre 2026 · **Stato:** START; non distribuita.
**Base esatta:** F2 source `566db0b8e2583d07c499f4db455ca3ffcde65ae4`, [PR #63](https://github.com/MATRIXNEO23/jarvis/pull/63), [CI 42532269337](https://github.com/MATRIXNEO23/jarvis/actions/runs/42532269337) SUCCESS 1030 test per job, [nativo 42532269371](https://github.com/MATRIXNEO23/jarvis/actions/runs/42532269371) SUCCESS. Baseline per rollback completo: ZIP Jarvis-014 immutabile, source `88c2934cbd6081f94fb33fba5f87f1800b07ebc0`.
**Diagnostica sorgente:** [PR #61](https://github.com/MATRIXNEO23/jarvis/pull/61), branch `fix/jarvis015-prompt-diagnostics-20261108` certificato su Windows, da trasferire nella F3 in modo trasparente e verificabile. Nessun merge implicito della PR: copiare solo i file esplicitamente verificati e documentare il confronto.

## Obiettivo
Capire con dati reali perché Gemma su Jarvis elabora 400–500 token con Second Brain e se i messaggi vengono ripetuti, con sorgenti per istruzioni, personalità, storia, Second Brain/archivio e richiesta corrente. Non tagliare nessuna istruzione o memoria prima della prova; non passare a server KoboldCpp durante F3.

## Piccoli passi
- F3.0: congelare source F2 e aprire branch isolato e PR draft; questo checkpoint prima di modificare codice.
- F3.1: trasferire la funzione PR#61 **manuale e opzionale**: in Impostazioni Gemma > Diagnostica prompt... > Acquisisci prossima domanda > Aggiorna > Scarta. Capture **solo RAM**, non log, nessun invio online, non entra nel Second Brain, nessuna generazione aggiuntiva. Mostra modalità, provenienza dei segmenti, token totali nativi, peso indicativo sezioni, e stringa Gemma esatta. Revoca cattura in corso se Scarta.
- F3.2: verificare che l'interfaccia dalla nuova scheda Chat locali (F2) apra lo stesso pannello, senza far partire il modello, e che una cattura per chat non includa prompt/ricordi delle altre chat. Cattura differenzia istanza F2 vs Console legacy.
- F3.3: test Windows Python 3.11/3.12 e prova tokenizer nativo, controlli privacy, azioni JSON/allowlist e continuità F2; confronto del diff (non deve cambiare `jarvis.py`, GGUF, memoria né provider in questa fase).
- F3.4: guida per benchmark comparativo **da eseguire realmente sul Pavilion**, non dichiarato verificato via CI. Condizioni fisse: stesso modello/quantizzazione, context_size=1024, max_output=256, history_max_tokens=250, thread 2/BLAS 2, domande uguali e memoria on/off. Raccogliere testo di output redatto/oscurato, Processed/token/s, Generated/token/s, latenza e RAM. Confrontare Jarvis Console, Chat F2 e KoboldCpp originale. Per privacy non condividere prompt interi senza anonimizzarli.

## Gate e rollback
Le modifiche PR#61 erano additive a `local_model/native_conversation_session.py` e `local_model/native_ui.py`, con nuovo formatter e test; F2 non aveva modificato questi file, quindi il trasferimento preserva il codice F2. Test RED/Green su branch separato; se una suite fallisce, correggere solo cause identificate e rieseguire. Nessuna build o ZIP nuova finché non richiesta, nessun controllo sul PC utente senza installazione. Il diff e i link CI vengono registrati qui e nel registro main.

**Rollback:** ignorare branch F3 e tornare alla F2 (`566db0b8...`) senza toccare profili/DB; per utilizzo stabile ZIP014 invariato. Non cancellare `jarvis_chat_sessions.sqlite3` o Second Brain. Nessun account/API o chiave richiesta.
