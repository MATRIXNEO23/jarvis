# ARCH-01 F2 — implementazione incrementale UI chat + sicurezza del contesto
**Stato:** F2 IMPLEMENTATA E WINDOWS CI VERIFICATA; nessuna build o release.
**Baseline F1 verificata:** modulo chat SHA `2f3c8d207ab1aff41d578fca6e48d606f7cd00d3`, ramo checkpoint `a5149e0eed1238821b5c2c184426e6e44079d699`, [PR #62](https://github.com/MATRIXNEO23/jarvis/pull/62), Windows 1022 test/job [42529275925](https://github.com/MATRIXNEO23/jarvis/actions/runs/42529275925); 014 originale `88c2934cbd6081f94fb33fba5f87f1800b07ebc0` sempre disponibile. Branch **F2** `feature/jarvis-kobold-chat-f2-20261108` (separato da F1 e diagnostica PR#61).

## Contratto e gate
1. UI `Chat locali` + `Console` nella zona sinistra `hud.console_host`: non togliere `tk.Text output` né `hud.attach_console`. Chat con selezione istanza, nuova chat, rinomina, testo cronologico, impostazioni Gemma attuali, stato sintetico. Tk standard library, nessun browser/WebView2 aggiunto.
2. Salvataggio chat esclusivo al nuovo `ChatSessionStore` per risposte locali **accettate**. I messaggi generati a scopo d'azione (JSON + validazione) NON finiscono in chat se non diventano una risposta `chat` validata; nessuna azione può aggirare il parser/allowlist.
3. F2 isola la cronologia di Gemma per `chat_id` (32 hex, già consentito dal `NativeConversationSession.prepare_turn`) anche dopo il riavvio. La `memory_context.recent_pairs` riceve solo coppie dallo store della chat selezionata; `memory_context(room)` ritorna `""`: **nessun Second Brain globale o progetto aggiunto automaticamente a chat nuove**. La memoria generale legacy conserva il suo percorso quando si usa la scheda `Console`.
4. Voce Gemma e messaggi digitati possono usare la chat attiva. Le altre funzioni (comandi diretti, GPT online, Telegram) rimangono sul vecchio dispatch; se GPT è attivo in `Chat locali`, informare che in F2 le chat isolate supportano Gemma locale senza inviare a GPT inconsapevolmente. F8 provider API programmati in seguito, senza credenziali in F2.
5. Cambio chat e cambio progetto impediti mentre si genera o ci sono richieste/azioni pendenti; risposta stale scartata con `conversation_epoch`, ID chat e progetto; la nuova chat non eredita il topic precedente. Nessuna cancellazione o migrazione dei dati legacy.
6. Archivio lazy: file `default_path().with_name("jarvis_chat_sessions.sqlite3")` creato solo alla prima apertura deliberata della scheda chat. L'app 014 originale non lo apre.
7. Test RED/GREEN Windows 3.11/3.12, unit/Tk, isolamento M2, fallback console, restrizioni azioni, speaker/voice, project-switch, restart DB, vecchio codice/core invariato dove possibile. Sempre rollback via source 014 o F1; dati nuovi non cancellati.

## Avanzamento
| Sottofase | Stato | Evidenza |
|---|---|---|
| F2-0 revisione punti di integrazione e piano | FATTO | punti di routing e modalità native/legacy verificati |
| F2-1 test e modulo UI locale | FATTO | chat_ui.py e tests/test_chat_ui.py, Tk Windows |
| F2-2 routing chat + isolamento Gemma | FATTO | context_id=chat_id, reader scoped, console preservata |
| F2-3 suite Windows, compare e review | FATTO | [42532269337](https://github.com/MATRIXNEO23/jarvis/actions/runs/42532269337), 1030 test/job |
| F2-4 checkpoint/piano aggiornato | FATTO | questo documento + main RECUPERO/registro/piano |

## Rischi particolari
- `NativeConversationSession.prepare_turn` accetta `context_id` solo come ID hex 32, quindi **usare l'ID della chat come partizione nativa**, non stringhe speciali.
- `native_memory_request` generale e progetto possono recuperare conversazioni precedenti: non collegarlo alla chat F2; serve un reader solo della chat selezionata. Le chat legacy non vanno migrate automaticamente.
- La pagina `Console` rimane quella dell'app per le azioni; se la UI chat è fallita o disabilitata, la console deve ancora funzionare.
- Il parser di output JSON dei comandi e le autorizzazioni Windows non sono modificati. Un'azione rifiutata non viene salvata come risposta valida.
- Nuove API online richieste dall'utente: registrate come F8 nel piano principale, **nessuna API/chiave integra in F2**.


## Implementazione e correzioni eseguite — checkpoint di sicurezza
**Codice F2:** `jarvis.py` (solo innesti UI/dispatch chat), nuovi `local_model/chat_ui.py`, `local_model/chat_context.py`, test `tests/test_chat_ui.py`; nessuna modifica al provider GGUF `native_bridge.py`, `native_provider.py`, `second_brain.py` o `workspace_memory.py`. HEAD codice più recente `026f150953962bffe39404fb62312e1ec5dc8239`.
- Notebook nella vecchia area console: schede `Chat locali` e `Console`. Il vecchio `output` e `hud.attach_console(output)` sono **conservati**. La pagina Chat è solo Tk (niente WebView/browser, server o modello extra), con nuova/sele­ziona/rinomina, impostazioni Gemma legacy e transcript di ultimi 32 scambi; tutti gli scambi sono persistenti nel DB, nessun limite di retention distruttiva.
- Creazione sidecar ritardata fino all'apertura esplicita della chat; store `%LOCALAPPDATA%/Jarvis/jarvis_chat_sessions.sqlite3` oppure `JARVIS_TRIAL_HOME/jarvis_chat_sessions.sqlite3`.
- Domande chat Gemma `NativeConversationSession.prepare_turn` per `context_id=chat_id` già validato 32hex; reader `make_chat_history_reader` con soli `recent_pairs` della chat corrente, richiamo ricordi generali ritorna stringa vuota: nuova chat non eredita automaticamente Second Brain né scambi di altre istanze; legacy Console mantiene routing storico e recupero Second Brain.
- Risposta accettata in chat: prima validazione JSON/azioni invariata, poi `NativeChatTurn.commit`, poi persistenza `ChatSessionStore.append_exchange`; azioni non-accettate, JSON malformato e comandi eseguiti non si fingono risposte chat. Voce e testo Gemma nel tab Chat puntano allo stesso chat_id; switching interdetto se modello occupato.
- Nessuna spedizione accidentale a GPT online dal tab Chat: verifica per invio digitato, pulsante `Chiedi a GPT` e conversazione vocale. GPT e Telegram legacy restano disponibili dalla Console senza modifica trasporti.
- Conservazione lavoro pendente: tab/chat non cambia durante generazione o presenza di follow-up già in coda; non li cancella. Il cambio progetto legacy nella Console mantiene la revoca tramite epoch che i test esistenti si aspettano.
- Impostazioni KoboldCpp avanzate, Qwen e altri GGUF sono F5; provider con chiavi API gratuite/eventuali F8; diagnostica prompt PR #61 è ramo separato.

### RED e regressioni intermediate
- [42531259734](https://github.com/MATRIXNEO23/jarvis/actions/runs/42531259734): 58 ERROR Windows per riferimenti non protetti ai nuovi widget in test legacy che estraggono i gestori senza costruire tutta la UI. Corretto con `try/except NameError` nei soli accessi opzionali; non alterati dispatch legacy o source dei test.
- [42531814491](https://github.com/MATRIXNEO23/jarvis/actions/runs/42531814491): 2 errori Windows per l'iniziale blocco globale di cambio progetto mentre Gemma era attiva; ripristinata la semantica originale Console, mantenuto blocco solo per chat F2. Non ignorare questi RED: sono registrati per motivare la correzione.
- [42532269371](https://github.com/MATRIXNEO23/jarvis/actions/runs/42532269371): Native tokenizer/owner SUCCESS su sorgente F2 `026f15095`.
- [42532269337](https://github.com/MATRIXNEO23/jarvis/actions/runs/42532269337): suite Windows completa dell'ultimo HEAD F2 **SUCCESS**, 1030 test PASS su ciascuno dei due job Windows (Python 3.11 e 3.12), inclusi test di chat Tk, voce/conversazione, parser comandi e servizi. Log 243.0s e 262.3s rispettivamente. Pubblicazione SKIPPED. Stato F2: GREEN sui sorgenti CI, non collaudo PC.
- Nessun test Windows10/Pavilion reale, nessun avvio dell'app sul PC dell'utente e nessun ZIP creato/pubblicato.

## Gate finale F2 e ripristino
**GREEN documentato:** [CI Windows unità/GUI/protocolli 42532269337](https://github.com/MATRIXNEO23/jarvis/actions/runs/42532269337) SUCCESS, 1030 test per job Windows 3.11/3.12 e diagnostica servizi PASS. [KoboldCpp tokenizer/owner 42532269371](https://github.com/MATRIXNEO23/jarvis/actions/runs/42532269371) SUCCESS. **Fonte esatta verificata:** `026f150953962bffe39404fb62312e1ec5dc8239`; successivi commit solo documentazione e [skip ci]. Delta vs F1: `jarvis.py`, nuovi `local_model/chat_context.py`, `local_model/chat_ui.py`, `tests/test_chat_ui.py` e documenti, niente modifiche a `second_brain.py`, `workspace_memory.py`, `native_provider.py`, `native_bridge.py`, `telegram_bridge.py` o DLL.
**Residui:** confronto grafico con KoboldAI Lite sul display reale non fatto, nessuna prova Pavilion di audio/mic/TTS/UI/prestazioni, vecchi messaggi possono essere presenti nell'archivio legacy ma NON migrati nella nuova chat, il tasto mostra solo gli ultimi 32 scambi (i più vecchi rimangono nel DB), profilo singolo Gemma soltanto. PR #61 diagnostica non fusa, Qwen e adapter multi-provider API non ancora implementati.
**Rollback:** chiudere nuova build sperimentale (non pubblicata) e usare fonte F1 per riprendere i lavori oppure estrarre/avviare ZIP014 immutabile. Non cancellare `jarvis_chat_sessions.sqlite3`, Second Brain, progetti o profili. Nessun file del PC utente è stato toccato. **Nessun ZIP/numero versione consumato**.
**Prossimo gate:** integrazione collaudo visivo e diagnostica prompt F3, poi scegliere in base a dati comparabili se conservare ABI o introdurre KoboldCpp server opzionale. F8 provider API future con credenziali personali è solo pianificata.
