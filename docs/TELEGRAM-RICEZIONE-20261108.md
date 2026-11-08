# Telegram: listener inattivo dopo disconnessione terminale

Sintomo utente: invio manuale funziona, messaggi in ingresso non producono nemmeno «Ricevuto». Causa sul PC non ancora provata: nessun account/log live accessibile.

Difetto dimostrato nel codice: _run attende solo _shutdown; il Future Telethon client.disconnected non viene osservato. Quando termina la riconnessione gestita da Telethon, il thread rimane bloccato e il flag enabled resta True, dando l'apparenza di ricezione attiva.

Piano mirato autorizzato da richiesta utente: osservare insieme stop e disconnessione; allo stop esplicito uscita normale, a disconnessione terminale errore breve, disconnect/finally esistenti liberano risorse e disattivano UI. Non cancellare il Future posseduto da Telethon. Non aggiungere riconnessioni concorrenti o replay di messaggi: Telethon gestisce già i retry. Nessun cambiamento a invio manuale, filtri contatti, Gemma/GPT, credenziali o archivio.

Alternative scartate: riavvio automatico del bridge o polling della cronologia introdurrebbero nuove politiche di retry/replay e rischi duplicati senza prova della causa sul PC. Non modificare il modello perché l'assenza di evento ricevuto precede l'inferenza.

RED: sorgente0fa82a6, run42454038692, job128649131802: percorso handler selezionato→archivio→risposta→audio controllato passa; il test della disconnessione fallisce perché il listener resta in attesa dello Stop. Fix limitato al lifecycle in telegram_bridge.py; aggiunta prova completa del wrapper thread/flag/stato. Verifica GREEN Windows e review ancora pendenti. Nessun test Linux, account reale, messaggio reale o build.

Riferimenti primari: https://docs.telethon.dev/en/stable/modules/client.html (disconnected, auto_reconnect), https://core.telegram.org/api/updates (meccanismo ricezione). Queste fonti spiegano l'API; la prova del difetto è il test Windows del codice Jarvis.
