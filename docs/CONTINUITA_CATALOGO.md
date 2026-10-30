# Jarvis — continuità catalogo azioni

Data: 30 ottobre 2026. Questa nota integra `docs/CONTINUITA_JARVIS.md` e contiene lo stato della nuova architettura per interpretare comandi non espressi con frasi prefissate.

## Richiesta dell'utente

Jarvis deve conoscere un elenco verificato di capacità delle applicazioni e usare GPT, quando la modalità Conversazione GPT è attiva, per tradurre espressioni come «mi chiudi Blocco note?» nell'azione `notepad.close`. La frase non deve corrispondere esattamente a una lista di parole. Un file descrive ciò che può fare, ma il modello non deve poter inventare codice o comandi.

## Implementato e isolato

Branch sperimentale `feature/gpt-conversazione-documenti`, PR draft #3, nessun merge verso main.

- `jarvis_commands.json`: catalogo leggibile con nome, applicazione, descrizione, esempi e rischio delle **sole azioni già implementate**.
- `capability_registry.py`: carica il catalogo, ne verifica lo schema, applica una whitelist immutabile di azioni associate a implementazioni Python e delega i comandi locali al pianificatore esistente. Blocca azioni sconosciute, argomenti imprevisti, path arbitrari e chiusura di Blocco note senza un documento identificato.
- `conversation_router.py`: mostra il catalogo a GPT; accetta `{"kind":"capability","action_id":"...","arguments":{}}` con schema rigoroso, senza possibilità di inventare comandi arbitrari. I formati precedenti restano accettati per retrocompatibilità.
- `jarvis.py`: instrada l'azione canonica verso l'esecutore locale già controllato, oppure verso il gestore di un solo Blocco note aperto da Jarvis. Richieste di chiusura passano ancora dalla scelta di salvataggio, senza `taskkill`.
- `action_planner.py`, `local_engine.py`, `voice_control.py`: aggiunta la capacità fissa `explorer.drive_c` per aprire C in Esplora file senza shell e senza consentire percorsi arbitrari; disponibile anche come comando vocale offline preciso.
- Test `tests/test_capability_registry.py` e ampliamenti ai test per GPT, planner, motore locale e Vosk.

**Ultima CI del ramo con documentazione:** [Windows/Linux SUCCESS, run 41137979952](https://github.com/MATRIXNEO23/jarvis/actions/runs/41137979952). Prima di ulteriori modifiche verificare nuovamente HEAD e CI.

## Condizioni di collaudo

L'utente ha già provato sul Pavilion che la versione precedente può creare documenti, ma non ha ancora provato questa nuova interpretazione per applicazione. La prova pratica su Windows deve verificare frasi diverse per aprire/chiudere lo stesso Blocco note, richiesta di salvataggio, apertura disco C, domande ordinarie che non provocano azioni e nessuna chiusura di finestre aperte manualmente.

Non dichiarare che Jarvis conosce tutti i comandi di Windows: l'elenco è estendibile ma ogni nuova applicazione richiede un adattatore sicuro, test e decisione di adozione. Il JSON **non è un file di comandi eseguibili**.

Requisiti invariati: microfono sempre spento ad ogni avvio, scelta manuale delle modalità, nessun timeout che cambia la modalità, nessuna nuova API a pagamento, DevKit GPT già configurato, versione già funzionante da conservare in cartella separata, nessun merge automatico.


**Ottimizzazione successiva:** il catalogo inviato a GPT è compatto, mentre il file JSON locale conserva tutte le descrizioni. Il test verifica che anche con una frase vocale lunga il prompt resti entro il limite di 5.000 caratteri del DevKit già installato. Commit verificato: `98bd7a2c18d4afdb6deacbd7dd1daa1922a775eb`.
