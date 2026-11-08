## Esito finale — fix mirato verificato
Sorgente24b3ef7509e84ecf60e023763671a303b0230633. Suite completa run42454285936 SUCCESS:987 test OK su ciascuna versione Python3.11/3.12 Windows; job128649889463181.021s, job128649889593150.959s. Test listener run42454285903 SUCCESS:4 test,0.800s. Prova nativa Gemma di regressione42454285900 SUCCESS. Build/pubblicazione saltate;010 invariata.

Conferma utente ulteriore: il messaggio arriva da un altro account, contatto spuntato, non da se stesso. Rimane non dimostrato che la disconnessione terminale sia l'unica causa sul PC: nessun accesso a log/sessione reale. Il fix elimina il listener falsamente attivo e segnala l'uscita quando i retry interni Telethon terminano; non introduce riavvio automatico o recupero retroattivo dei messaggi persi. Per ripartire da una disconnessione terminale si riattivano le risposte automatiche.

Revisione indipendente: corretti anche identità del Future Telethon (property restituisce shield, va catturato una volta) ed eccezioni terminali da consumare senza divulgarne i dettagli. Recheck finale: nessun importante difetto residuo confermato. Test coprono Future shield, chiusura normale, errore terminale senza warning, flag enabled/thread, handler contatto autorizzato, esclusione uscenti/non autorizzati e duplicati. Audio e rete controllati, archivio reale temporaneo. Nessun test funzionale Linux o messaggio reale inviato.

Modifiche runtime limitate a telegram_bridge.py (+20 righe circa); nessun cambiamento a modello, invio manuale, credenziali, contatti o dati storici. L'invio manuale è coperto anche dalla suite completa esistente.

[Suite Windows finale](https://github.com/MATRIXNEO23/jarvis/actions/runs/42454285936) · [Test listener](https://github.com/MATRIXNEO23/jarvis/actions/runs/42454285903) · [Commit verificato](https://github.com/MATRIXNEO23/jarvis/commit/24b3ef7509e84ecf60e023763671a303b0230633)

Segue indagine storica e piano iniziale. I GREEN indicati sopra sostituiscono lo stato pendente riportato nel checkpoint iniziale.

# Telegram: listener inattivo dopo disconnessione terminale

Sintomo utente: invio manuale funziona, messaggi in ingresso non producono nemmeno «Ricevuto». Causa sul PC non ancora provata: nessun account/log live accessibile.

Difetto dimostrato nel codice: _run attende solo _shutdown; il Future Telethon client.disconnected non viene osservato. Quando termina la riconnessione gestita da Telethon, il thread rimane bloccato e il flag enabled resta True, dando l'apparenza di ricezione attiva.

Piano mirato autorizzato da richiesta utente: osservare insieme stop e disconnessione; allo stop esplicito uscita normale, a disconnessione terminale errore breve, disconnect/finally esistenti liberano risorse e disattivano UI. Non cancellare il Future posseduto da Telethon. Non aggiungere riconnessioni concorrenti o replay di messaggi: Telethon gestisce già i retry. Nessun cambiamento a invio manuale, filtri contatti, Gemma/GPT, credenziali o archivio.

Alternative scartate: riavvio automatico del bridge o polling della cronologia introdurrebbero nuove politiche di retry/replay e rischi duplicati senza prova della causa sul PC. Non modificare il modello perché l'assenza di evento ricevuto precede l'inferenza.

RED: sorgente0fa82a6, run42454038692, job128649131802: percorso handler selezionato→archivio→risposta→audio controllato passa; il test della disconnessione fallisce perché il listener resta in attesa dello Stop. Fix limitato al lifecycle in telegram_bridge.py; aggiunta prova completa del wrapper thread/flag/stato. Verifica GREEN Windows e review ancora pendenti. Nessun test Linux, account reale, messaggio reale o build.

Riferimenti primari: https://docs.telethon.dev/en/stable/modules/client.html (disconnected, auto_reconnect), https://core.telegram.org/api/updates (meccanismo ricezione). Queste fonti spiegano l'API; la prova del difetto è il test Windows del codice Jarvis.
