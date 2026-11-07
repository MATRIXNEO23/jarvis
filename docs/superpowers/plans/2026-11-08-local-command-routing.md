# Comandi interni e Gemma — requisiti confermati e piano

Conferma esplicita dell'utente nella chiamata del 8 novembre 2026, dopo lettura dei nove punti. Base: Jarvis007, source `9f8c5f582b98a4ac131c41a4170b194c98abc3fa`. Ramo isolato `fix/local-command-routing-20261108`. Nessuna nuova build autorizzata da questa sola conferma.

## Requisiti di accettazione

1. Invio normale della chat: comandi interni riconosciuti prima del modello, senza obbligo di Esegui locale.
2. Sinonimi e frasi naturali per i comandi INTERNI (non soltanto per Programmi e app). Un riconoscimento condiviso voce/chat, una sola azione per funzione. Nessuna esecuzione per frasi negate o semplici menzioni.
3. Richieste non risolte localmente: Gemma interpreta e propone una capacità già esistente; il motore valida ed esegue. Dati mancanti/ambiguità: chiarimento. Mai confermare un effetto dalla sola risposta del modello.
4. Apri browser: browser predefinito Windows, anche senza Programmi e app attivo. Apri Chrome/Edge: modulo Programmi e app, permessi invariati.
5. Conservare navigazione Explorer: apri Download → sottocartella per nome → cartella superiore, nella vista corretta e con policy invariata.
6. Mostra Download: aprire la cartella, non limitarsi a elencarne il contenuto in chat. Elenchi esplicitamente richiesti restano distinti.
7. Help aggiornato a comportamento effettivo, sinonimi e prerequisiti. Non documentare capacità non verificate.
8. Nessuna aggiunta estranea o duplicazione; conservare Netflix, programmi, timer, documenti, progetti, impostazioni e dati.
9. Step brevi, stato persistente e test Windows prima delle conclusioni. Nessun test funzionale Linux; niente promessa di assenza universale di regressioni.

## Fatti e limiti

- Utente: stato sistema con Esegui locale funziona, con Invio passa a Gemma; apri browser non funziona nell'invio normale; apri Netflix già intercettato localmente.
- Rettifica utente: apri Download funziona dopo abilitazione Accesso file. Non trattarlo come difetto di apertura riprodotto con add-on attivo.
- Codice: `send_console_input` intercetta file/app/timer, ma i comandi base raggiungono `submit_local` solo dopo la scelta Gemma/GPT. Il guard generico di avvio può respingere anche un comando base non intercettato.
- `speech_to_local_command` contiene già il riconoscimento base; `LocalEngine` gli esecutori; `capability_registry` e `parse_conversation_intent` validano le proposte del modello. Riutilizzarli.
- `file_access/service.py` implementa già navigazione figlio/superiore e verifica vista/policy. Non ricrearla.
- La sessione Gemma ordinaria prepara testo, non intenzioni eseguibili. Il budget prompt predefinito è limitato a 600 caratteri dalla policy esistente: non incollare indiscriminatamente il prompt GPT completo o modificare preferenze senza verifica.

## Approccio

Riutilizzare il riconoscimento locale e il protocollo di capacità esistente. Scartate duplicazione del modulo Programmi e app e nuova lista di esecutori: aumenterebbero incoerenze. La richiesta dell'utente di usare lo stesso metodo riguarda riconoscimento → validazione → esecutore, non trasformare cartelle o browser predefinito in app da spuntare.

## Passi e prove

- [ ] Riproduzione Windows su callback console reale (fixture AST già usata dal progetto), LocalEngine e registro SQLite reali, solo apertura programmi/browser sostituita. Stato/browser/sinonimi non devono chiamare Gemma; Netflix e dialoghi pendenti mantengono priorità. Registrare Red prima del codice.
- [ ] Modifica mirata a `voice_control.py`, `jarvis.py`, eventuale normalizzazione in `local_engine.py`: riconoscimento condiviso, sinonimi, protezioni. `mostra Download` allineato anche nel servizio file, senza cambiare elenca/lista espliciti.
- [ ] Raccordo Gemma al validatore/esecutori: prima prova del contratto e del budget con sessione reale e adattatore controllato. Mantenere contesto, cancellazione/epoch, permessi e memoria; nessun fallback online implicito. Precisare separatamente ciò che non è provato sul GGUF reale.
- [ ] Aggiornamento `local_help.py`, catalogo e guide pertinenti. Verificare corrispondenza con l'esecuzione e navigazione esistente.
- [ ] Windows mirati e suite 3.11/3.12, review del diff; riportare esiti e limiti. Build/package solo su richiesta esplicita e dopo controlli del runtime estratto.

## Recupero

007 e profili restano invariati. Il ramo isolato non viene fuso né pubblicato come pacchetto automaticamente. A ogni pausa leggere questo documento, stato attività e diff; distinguere test scritti, avviati e conclusi. Non attribuire alla nuova modifica i 922 test storici della007.

## Stato corrente

Requisiti confermati, analisi sorgenti svolta. Nessuna modifica runtime, nessun test nuovo eseguito, nessun pacchetto creato. Prossimo passo: regressione Windows del percorso console.

Aggiornamenti successivi: [verifiche, source, review e prossimo passo](../../COMANDI-INTERNI-VERIFICA-20261108.md). Lo stato iniziale sopra è storico; leggere questo registro prima di proseguire.
