# ARCH-01 F4.0 — Canary KoboldCpp server locale: protocollo e rollback

**Data:** 9 novembre 2026 · **Stato:** F4.1 CANARY GREEN nei test Windows, nessun server avviato e nessun release/merge.
**Sorgente congelata F3:** `b8828f0facca6fb916ccd341e313670627e67a1d` da [PR #64](https://github.com/MATRIXNEO23/jarvis/pull/64); F3 testata al runtime commit `0c3247b69ac7033ec3d8194fbe1f6583d78108c0` in [42533254766](https://github.com/MATRIXNEO23/jarvis/actions/runs/42533254766) 1040 PASS per job Windows e [42533254794](https://github.com/MATRIXNEO23/jarvis/actions/runs/42533254794) nativo SUCCESS. Base installabile da ripristinare: ZIP014 source `88c2934cbd6081f94fb33fba5f87f1800b07ebc0`.
**Gate precedente non soddisfatto sul Pavilion:** il benchmark F3 Jarvis vs KoboldCpp originale con stessi prompt/config e Second Brain on/off NON è ancora stato eseguito. Perciò questa F4 è **solo una prova tecnica opzionale, senza modificare l'architettura di Jarvis**: niente switch automatico al server, niente seconda copia di GGUF, niente avvio del processo, niente collegamento alla UI.
**Documentazione KoboldCpp:** https://koboldcpp.net/docs/api/endpoints/ (GET `/api/v1/model`, POST `/api/v1/generate`, GET `/api/extra/perf`); https://koboldcpp.net/docs/api/overview/ ; https://github.com/LostRuins/koboldcpp/wiki/ (payload generazione con `prompt`, `max_context_length`, `max_length`, `stop_sequence`).

## Sottofasi
- **F4.0:** branch isolato, test di contratto scritti prima dell'implementazione, documentazione di protocollo, revisione sicurezza.
- **F4.1:** modulo nuovo `local_model/kobold_server_canary.py` con **chiamata esplicita** a KoboldCpp *già avviato separatamente* su `http://127.0.0.1:<porta>`; `probe()` read-only, `generate(...)` solo su chiamata manuale, `perf()` read-only. Solo urllib/std library, nessun import nel programma Jarvis.
- **Sicurezza:** host esattamente IP 127.0.0.1 (no DNS, LAN, HTTPS, router/admin); disabilitare proxy ambiente e redirect; timeout e massimo corpo di risposta; validazione tipi/campi, nessuna stampa prompt in errori, nessun download di modelli, credenziali locali in memoria solo se fornite dal chiamante; blocco su mismatch del modello prima di inviare testo, no retry implicito.
- **Test:** URL esterni/SSRF e redirect rifiutati, niente connessioni alla costruzione, probe parser, model mismatch senza POST, generazione raw esatta/limiti/stop, risposta malformata, errore/timeout, proxy isolato. Fake opener/HTTP local mock: nessun GGUF, rete o credenziale reale in CI.
- **Integrazione:** vietato modificare `jarvis.py`, `native_bridge.py`, `native_provider.py`, `chat_sessions.py`, `second_brain.py` o profili. F4 GUI e selezione backend sono una decisione successiva, condizionata a benchmark sulla macchina utente e consenso. Un solo GGUF caricato per il confronto pratico.
- **Rollback:** abbandonare branch/PR F4 e tornare a F3 `b8828f...`; nessun DB, memoria o profilo modificato, ZIP014 resta la versione installabile; nessun nuovo pacchetto/numero consumato.

## Registro verifiche
| Checkpoint | Stato | Evidenza |
|---|---|---|
| F4.0 preparazione | FATTO | questo documento, branch source F3 |
| F4.1 test RED | FATTO | [42534308393](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534308393), ModuleNotFoundError atteso |
| F4.1 modulo opzionale | FATTO | kobold_server_canary.py, nessun import nel runtime |
| F4.1 GREEN CI Windows | FATTO | [42534821947](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534821947), 1051 test/job PASS, [nativo 42534821971](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534821971) SUCCESS |
| F4.2 confronto Pavilion | NON ESEGUITO | protocollo F3 e prova utente |
| Migrazione DLL→server | NON APPROVATA | richiede dati e gate separato |


## Implementazione F4.1 e difetti intercettati dai test (9 novembre 2026)
- **RED** [42534308393](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534308393): test prima del modulo, errore atteso di import per `local_model.kobold_server_canary` mancante. Nessun file Jarvis modificato.
- Primo candidato `0f590c0dbe025ff244e86988c2397490fd7c255e`: modulo opt-in senza wiring, primo test [42534398145](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534398145) ha segnalato due problematiche **di test/formulazione**, non un trasferimento reale del prompt: errore case-sensitive nel messaggio «modello» e presenza supposta del `ProxyHandler({})` nella lista degli handler. Python può omettere handler vuoti: la sicurezza si verifica accertando che **nessun proxy attivo** sia configurato.
- Correzioni mirate: `2fe2562b...` messaggio safe, `dacddf7c...` server protetto deve bloccare il tentativo prima di POST, `782f5563...` relativo test, `ce5dfd07bd51229ac3f251c57af2ae3e74da8183` asserzione sul mancato uso dei proxy. Nessun cambio a prompt/formati/route della 014/F3, né altra funzione.
- **Ultima prova da accertare:** [42534821947](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534821947) suite Windows 3.11/3.12, **SUCCESS 1051 test/job** su source `ce5dfd07bd51229ac3f251c57af2ae3e74da8183`; [42534821971](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534821971) tokenizer nativo SUCCESS. Successivi commit sul ramo solo documentazione [skip ci].
- **Uso previsto solo in laboratorio:** Jarvis/embedded GGUF non deve essere in esecuzione assieme al server standalone su Pavilion; l'app corrente non carica né collega il canary. Avviare manualmente KoboldCpp su `127.0.0.1:5001`, poi richiedere solo `probe()`/lettura `perf()`; una `generate` invia il **prompt raw letterale** solo dopo confronto esatto del nome modello e chiamata esplicita. Non usare testo privato nella prova; il client non salva il contenuto ma il server può stampare output in console.
- Limite tecnico: test mock dell'interfaccia HTTP non equivalgono al benchmark umano sul PC, né dimostrano che la DLL embedded sia più lenta del server; nessun percorso di rollback degli archivi viene attivato dalla sola importazione del canary.


## Protocollo di prova manuale (non eseguito)
**Prerequisito:** prima misurare prompt/tempi con la F3 sul Pavilion, poi eventualmente confrontare con il canary senza tenere due GGUF caricati. Eseguire KoboldCpp originale standalone con **un solo GGUF** sulla porta 5001, bind 127.0.0.1, stesso Context Size/Max Output/threads e modello. Non aprire contemporaneamente la modalità Gemma embedded di Jarvis.
```python
from local_model.kobold_server_canary import KoboldServerCanary
canary = KoboldServerCanary("http://127.0.0.1:5001")
model = canary.probe()  # solo identità GGUF, NON genera
stats_before = canary.perf()  # opzionale; campi dipendono dalla versione
# Solo con prompt sintetico e non privato, e solo se autorizzato:
answer = canary.generate(
    "<start_of_turn>user\\nCos'è un buco nero?<end_of_turn>\\n<start_of_turn>model\\n".replace("\\n", "\n"),
    expected_model=model,
    max_context_length=1024,
    max_length=256,
    stop_sequence=("<end_of_turn>",),
)
stats_after = canary.perf()
```
`generate` non interpreta gli output come azioni Jarvis e non salva cronologia; questo snippet è un esempio per i testatori, NON una feature con pulsante disponibile nella 014. Durante i test CI viene simulato un server e **non** parte alcuna generazione GGUF, LAN, provider API o servizio online. Se non è possibile attestare che il server ha il modello corretto, nessun invio prompt.


## Esito F4.1 — canary verificato sui sorgenti Windows
**GREEN:** [Windows 42534821947](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534821947) SUCCESS, **1051 test PASS per job** (Python Windows 3.11: 150.254s; 3.12: 201.17s), diagnostica servizi SUCCESS; [nativo/tokenizer 42534821971](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534821971) SUCCESS. **Commit codice testato** `ce5dfd07bd51229ac3f251c57af2ae3e74da8183`, dopo solo aggiornamenti documentali. RED attestato e correzioni mirate nel blocco precedente.
**Diff vs F3:** *soltanto* il nuovo modulo `local_model/kobold_server_canary.py`, test `tests/test_kobold_server_canary.py` e questo checkpoint. Non sono stati toccati `jarvis.py`, provider DLL, UI, salvataggi chat, Second Brain, profili, Telegram o capacità Windows. Il canary viene invocato unicamente con import/chiamata esplicita da test o developer.
**Confine dell'accettazione:** F4.1 è verificata per mock protocollo/validazione e non regressioni; **F4.2 benchmark Pavilion è ancora NON ESEGUITO**. Non promettere speed-up, non avviare un server dentro Jarvis, non caricare due GGUF contemporaneamente. La versione pubblicata resta 014; **nessun ZIP/numero nuovo consumato**.
**Rollback:** F4 branch/PR ignorabili, F3 `b8828f...` disponibile; per utente ZIP014 originale. Nessun file storico eliminato o migrato.
