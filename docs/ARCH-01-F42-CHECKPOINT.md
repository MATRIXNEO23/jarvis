# ARCH-01 F4.2 — Benchmark ripetibile KoboldCpp vs Jarvis, sicurezza e rollback

**Data:** 9 novembre 2026. **Stato:** F4.2 avviata su branch isolato, nessun test reale sul Pavilion.
**Baseline sorgente:** F4.1 `0d7e0105c35fd94dba1f64a4f3d137c650745a97` ([PR #65](https://github.com/MATRIXNEO23/jarvis/pull/65)), con codice F4.1 Windows-green `ce5dfd07bd51229ac3f251c57af2ae3e74da8183`, [Windows CI 42534821947](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534821947) 1051 test/job, [nativo 42534821971](https://github.com/MATRIXNEO23/jarvis/actions/runs/42534821971) SUCCESS.
**Rollback completo:** source Jarvis014 `88c2934cbd6081f94fb33fba5f87f1800b07ebc0`, ZIP immutabile `Download/Jarvis-014.zip`; F3 `b8828f0facca6fb916ccd341e313670627e67a1d`.

## Decisione
La F4.2 serve a raccogliere dati comparabili; non conferisce autorizzazione a sostituire l'ABI DLL, avviare server in Jarvis, usare un secondo GGUF o comprimere Second Brain. Il PC dell'utente non è raggiungibile da GitHub Actions. **Strumentazione e protocolli possono essere testati in CI**, le prestazioni sul Pavilion NON possono essere misurate finché il test non viene eseguito localmente.

## Piano prima del codice
1. Nuovo strumento opzionale **solo laboratorio** in `tools/f42_benchmark.py`, non importato da Jarvis. Due modalità: `template` stampa schema per annotare prove Jarvis/KoboldCpp senza prompt privati; `compare` legge un file JSON fornito volontariamente, compara latenza e contesto e segnala prove non confrontabili. `server` esegue un singolo piccolo prompt sintetico Gemma tramite il canary localhost F4.1, soltanto con flag esplicito `--allow-generation`, mai automaticamente.
2. Misurare il tempo client end-to-end e leggere `/api/extra/perf`: `last_process`, `last_eval` in secondi e `last_token_count` **come contatore grezzo non classificato** (non presumerlo processed o generated in assenza di evidenza). Se `total_gens` o la coda suggeriscono interferenze, segnalare contaminazione. Niente stampa, log o salvataggio di testo del prompt/risposta; nessun file scritto senza `--output` esplicito.
3. Tempi reali da Jarvis Console Brain on/off e Chat F2/F3: inserirli manualmente dal log e dalla diagnostica prompt. Non leggere file/profili reali automaticamente. Nessuna dipendenza esterna.
4. Test unitari RED prima del codice, poi GREEN su Windows 3.11/3.12 e prova nativa. Test input malformati, auto-no-network, flag esplicito, nessuna fuga prompt, contesto non confrontabile, costo per output token, errori e privacy.
5. Aggiornare `RECUPERO.md`, piano e registro con SHA, run e rollback. **Nessun ZIP pubblicato** salvo autorizzazione esplicita.

## Gate
- Confronti efficaci soltanto per stesso GGUF/quantizzazione, context 1024, max_output 256, threads e sampler equivalenti, stesso numero di domande e stesso prompt serializzato per confrontare la cache. Tempi piccoli senza output tokens e contesto di input non rappresentativo NON dimostrano superiorità.
- Evitare due GGUF aperti su CPU i3-2100/10GB. Il server deve già essere avviato manualmente su `127.0.0.1`, senza password/endpoint online forniti al report.
- Non stampare né salvare chat, ricordi, token API o prompt integrali. Nessun invio a GPT online.

**Stato test iniziale:** da creare. **F4.2 benchmark Pavilion:** NON ESEGUITO. **Migrazione DLL → server:** NON APPROVATA.
