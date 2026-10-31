# Jarvis — qualità della conversazione, revisione 1

Obiettivo circoscritto: italiano naturale, risposte concise nella conversazione e complete nelle procedure, ironia e sarcasmo intelligente e **irriverenza** quando pertinenti.

**Correzione esplicita dell'utente:** «Irriverenza no deferenza». Non si deve ricercare deferenza, riverenza, servilismo, adulazione o appellativi cerimoniosi. L'irriverenza è una sfumatura asciutta e spiritosa, non scortesia, insulto o derisione.

## Comportamento atteso

- **Conversazione quotidiana**: di norma 1–3 frasi pertinenti, spontanee e scorrevoli; senza spiegazioni o saluti ripetitivi.
- **Istruzioni richieste**: procedura completa con prerequisiti, passaggi, verifiche e rischi pertinenti, senza tagli arbitrari per sembrare breve.
- **Battute, sarcasmo e irriverenza**: contestuali, occasionali e coerenti con il registro dell'utente; nessun obbligo di fare battute.
- **Situazioni delicate**: niente battute su problemi medici, crisi, perdite di dati, sicurezza, credenziali o minacce informatiche. Qui prevalgono precisione e tatto.
- **Documenti e testi richiesti**: non imporre ironia, sarcasmo o irriverenza al contenuto di un documento senza che l'utente lo chieda.

## Implementazione isolata

- `dialogue_style.py`: seleziona un suggerimento breve basato sulla frase corrente; non conferisce autorizzazioni operative né richiama API.
- `jarvis_persona.py`: stesso tono base per chat scritta e voce.
- `conversation_router.py`: modalità conversazionale con limite aumentato per risposte testuali, senza allentare lo schema delle azioni, e con supporto a più righe solo per chat.
- `offline_tts.py`: risposte vocali più lunghe suddivise in blocchi ordinati anziché tagliate dopo 600 caratteri; numero massimo di caratteri sempre limitato.
- `tests/test_dialogue_style.py`: copertura automatica di stile, priorità alla sensibilità, procedura lunga, limiti di prompt, TTS e assenza di comandi impliciti.

I test unitari controllano la scelta delle istruzioni e gli invarianti di formato, **non** misurano se il modello genererà sempre un'ironia appropriata. La qualità naturale va valutata nel collaudo reale rinviato dall'utente. Non modificare dati dei progetti né le preferenze archiviate durante il collaudo.

## Sicurezza e distribuzione

La segnalazione Microsoft Defender `Trojan:Script/Wacatac.B!ml` sul precedente pacchetto non è stata risolta. I test automatici non certificano l'assenza di malware: non disabilitare antivirus o autorizzare un rilevamento per eseguire la build. Backup completo di `%LOCALAPPDATA%\Jarvis` prima di ogni successivo collaudo.
