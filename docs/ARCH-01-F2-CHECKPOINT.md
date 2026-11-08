# ARCH-01 F2 — implementazione incrementale UI chat + sicurezza del contesto
**Stato:** START / implementazione isolata; nessuna release.
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
| F2-0 revisione punti di integrazione e piano | IN CORSO | jarvis.py linee console/speech/Gemma/Second Brain lette |
| F2-1 test e modulo UI locale | DA FARE | — |
| F2-2 routing chat + isolamento Gemma | DA FARE | — |
| F2-3 suite Windows, compare e review | DA FARE | — |
| F2-4 checkpoint/piano aggiornato | DA FARE | — |

## Rischi particolari
- `NativeConversationSession.prepare_turn` accetta `context_id` solo come ID hex 32, quindi **usare l'ID della chat come partizione nativa**, non stringhe speciali.
- `native_memory_request` generale e progetto possono recuperare conversazioni precedenti: non collegarlo alla chat F2; serve un reader solo della chat selezionata. Le chat legacy non vanno migrate automaticamente.
- La pagina `Console` rimane quella dell'app per le azioni; se la UI chat è fallita o disabilitata, la console deve ancora funzionare.
- Il parser di output JSON dei comandi e le autorizzazioni Windows non sono modificati. Un'azione rifiutata non viene salvata come risposta valida.
- Nuove API online richieste dall'utente: registrate come F8 nel piano principale, **nessuna API/chiave integra in F2**.
