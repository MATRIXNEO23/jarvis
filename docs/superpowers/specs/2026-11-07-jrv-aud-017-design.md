# JRV-AUD-017 — indicatore della sessione Gemma condivisa

Base015 verificata `558135173a13ca7bdaddfc543c63897730633353`. L'utente autorizza correzioni conservative; niente build/nuove risposte del modello o cambi di avvio/microfono.

## Difetto e soluzione minima

Il provider HUD in jarvis.main non legge l'attività Gemma: thinking usa solo busy_gpt/busy_local/document_busy e reasoning solo richieste GPT. Il flag della chat/prova manuale non copre Telegram e la prova nelle impostazioni: queste usano la sessione condivisa senza settare gemma_trial_busy.

Aggiungere alla NativeConversationSession un contatore protetto dal lock breve dei metadati, bilanciato da finally nell'operazione già esistente. Proprietà is_busy senza lock d'inferenza, caricamento, accesso a disco o creazione di sessione. Contare anche richieste già in coda; ask/prepare_turn annidati non devono portare a uno stato idle prematuro. Errori di configurazione, prompt, adapter, timeout e revisione devono sempre scaricare il contatore. Stop/close non dichiarano inattivo un backend non cooperativo finché l'operazione non esce davvero.

HUD reasoning/thinking includono l'owner esistente e il flag del lavoro chat in attesa del poll UI, indipendentemente dall'abilitazione GPT. Mantenere speaking/listening/searching e precedenze visuali. Nessun getter che crei/carichi Gemma per leggere l'indicatore, nessun nuovo thread/poller/timer. Stato generico di elaborazione: non inventare fasi dettagliate di caricamento/inferenza che il backend non espone alla UI.

## Prove e limiti

Test Windows con sessione/factory/bridge e callback HUD/Telegram reali, ABI controllata già presente. Generazione bloccata con Event, osservatore bounded per dimostrare che il provider non aspetta l'inferenza. Chat, turno differito, Telegram, prova impostazioni generata dal builder (sola trasformazione UI, nessuna build), suggerimento programmi, coda, annullamento/timeout/close, errori e ritorno idle. Verificare metadati senza I/O/nuova sessione e preservazione delle priorità HUD/Tk già testate.

Non prova GGUF/DLL reali, account Telegram, Windows10/i3/HDD o pacchetto estratto. Nessun test funzionale Linux.022/023 restano separati. Ritorno reversibile alla015 nel ramo senza toccare dati e pacchetti precedenti.
