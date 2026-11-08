# Jarvis 015 — Diagnostica dei prompt (proposta implementata in ramo isolato)

Data: 8 novembre 2026. **Nessuna build 015 generata o pubblicata.** Baseline operativa immutabile: Jarvis 014, source SHA `88c2934cbd6081f94fb33fba5f87f1800b07ebc0`; sviluppo PR #61 (`fix/jarvis015-prompt-diagnostics-20261108`).

## Obiettivo concordato

Analizzare **il prompt effettivo** che Jarvis invia a Gemma, con fonte, costruttore e token delle singole componenti. Niente modifiche strutturali, sintesi o riduzione del prompt: la 014 mantiene coerenza e memoria e non va alterata senza dati reali.

## Integrazione

In `Impostazioni → Modello locale Gemma`, pulsante **Diagnostica prompt...**. Nella finestra:
1. **Acquisisci prossima domanda**: abilita solo la prossima richiesta nella sessione conversazionale Gemma, compresa quella interpretata come azione strutturata, ma non la prova generazione isolata, Telegram o i comandi gestiti internamente senza Gemma.
2. Fai una normale domanda scritta o vocale a Gemma. Poi **Aggiorna** per leggere il report.
3. Rapporto: percorso `jarvis.submit_gemma_voice → conversation_router.native_intent_context_for_request → NativeConversationSession.prepare_turn → native_provider.format_gemma_messages → NativeChatAdapter.call`. Modalità chat/JSON, sorgente delle istruzioni, personalità applicata, domande e risposte storiche effettivamente incluse (RAM o archivio ripristinato), memoria recuperata, domanda attuale, avvisi di esclusione della cronologia, totale token del prompt, valori Context Size/Max Output e limite cronologia, **stringa integrale del prompt post-template**.
4. **Scarta** rimuove il report dalla RAM e disarma la cattura. **Copia con conferma** avvisa che possono esservi conversazioni e ricordi privati prima di usare gli appunti Windows.

Token isolati: stime con il tokenizer nativo per ogni sezione, **non sommabili** perché subword e delimitatori possono cambiare ai confini. Il totale prompt deriva dal conteggio nativo già usato per la verifica budget (se disponibile). Se non c'è tokenizer, viene indicata l'unità in caratteri, non spacciata per token.

## Confini e sicurezza

- Capture **off per impostazione predefinita**: nessun contenuto registrato, nessun I/O e nessuna nuova tokenizzazione nel percorso normale.
- Su cattura manuale, il report è elaborato **dopo l'inferenza**: misure prefill non alterate, nessuna nuova generazione o invio rete; solo costi di tokenizzazione per leggere le sezioni, limitati all'attivazione esplicita.
- La stringa è solo RAM della sessione, non inserita nella cronologia, Second Brain, archivi, log o file; stop e chiusura sessione la azzerano.
- Il report può contenere materiale privato: non copiarlo o condividerlo integralmente con terzi. Per condividere una diagnosi, oscurare ricordi, nomi e testi sensibili.
- Nessun cambiamento ai prompt, catalogo azioni, parse JSON, memoria, parametri del GGUF, profilo o comportamenti della build 014.

## Verifiche e gate

- Tests `tests/test_native_prompt_diagnostics.py`: non attivato per default, cattura esatta del prompt dopo chiamata al modello, provenienza e totali, sorgente JSON, recupero ricordi, cancellazione in RAM, stop/close, nessuna interferenza con richieste isolate.
- CI Windows Python 3.11 e 3.12 richiesta via PR #61; controllo UI Tk con simulazioni, senza microfono/GGUF reale. La qualità dei risultati e la velocità su Pavilion non dipendono da questa aggiunta perché non cambia il prompt.
- Nessuna build/publishing fino alla successiva autorizzazione esplicita dell'utente. In caso di regressione, annullare branch; la 014 e profili utente rimangono intatti.

## Prossima decisione

Dopo un campione reale raccolto dalla finestra, decidere **se** e **quali** componenti siano superflui. Non sintetizzare o tagliare automaticamente i ricordi per il solo fatto che un prompt supera 400 token.
