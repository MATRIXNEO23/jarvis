# JARVIS — continuità automatica dei progetti (prototipo isolato)

**Branch:** feature/automatic-project-continuity (deriva dal ramo di fix Telegram, non da main).
**Stato:** codice e test automatici da collaudare sul Pavilion; nessuna migrazione distruttiva, nessun merge autorizzato.

## Obiettivo

La memoria deve crescere **mentre JARVIS svolge un lavoro**, non solo quando l'utente
preme "Salva". Il database SQLite locale è la fonte canonica. I file leggibili si
rigenerano dal database e sono disponibili anche dopo la chiusura di JARVIS.

## File creati per ogni progetto

Directory: %LOCALAPPDATA%\Jarvis\projects\<UUID> (UUID invariabile).

- CONTINUITA.md: stato fornito dall'utente, passi recenti classificati per esito,
  file verificati e ultimi scambi. Ricostruito automaticamente e dotato di
  CONTINUITA.previous.md come copia della generazione precedente.
- STATO.json: stato strutturato del progetto, conteggi, attività incompiute,
  ultimi risultati verificati, identificatori di aggiornamento.
- PASSI.md: elenco recente dei passi, con stati planned/running/completed/failed/interrupted.
- EVENTI.jsonl: estratto cronologico delle ultime 100 transizioni tracciate;
  lo storico completo è nel database SQLite, non in questa proiezione limitata.
- ARTIFATTI.md: riferimenti a file realmente verificati come esistenti.
- files/: directory per futuri risultati generati all'interno del progetto.
  Non sposta né copia di nascosto documenti da altre cartelle.

## Eventi realmente registrati

1. Creazione progetto: immediata creazione dei file locali.
2. Chat in un progetto: persistenza automatica del turno concluso, anche
   quando il Second Brain generale è OFF. Le chat generali restano soggette
   all'interruttore esistente. Stringhe che sembrano contenere credenziali
   vengono escluse.
3. Comando locale in un progetto: passo running **prima** dell'esecuzione;
   completed solo dopo il risultato effettivo con task_id; failed se respinto
   o non riuscito.
4. Documento gestito da JARVIS: passo running e risultato effettivo.
   Se un salvataggio crea un file individuabile, registrazione del riferimento
   SOLO dopo verifica dell'esistenza.
5. Pianificatore con approvazione esplicita: i passi diventano planned solo
   dopo l'approvazione; il completamento dipende dai messaggi del motore e
   dalle ricevute dei singoli comandi. Alla terminazione anticipata i passi
   restanti sono interrupted, mai completed.
6. Progetto corrente: all’apertura di un progetto (o ritorno al generale)
   viene salvato il contesto, ripristinato al prossimo avvio.
7. Riavvio: ogni passo rimasto planned/running viene marcato interrupted;
   non viene rieseguito automaticamente. I file di proiezione assenti o non
   allineati vengono ricostruiti dalle righe persistite in SQLite.

L'obiettivo è distinguere chiaramente intenzione, risultato e incertezza.
Non si considera riuscita una compilazione perché l'assistente dice "fatto".
Per una compilazione reale servirà una capacità autorizzata che esegua e
verifichi concretamente il comando: la memoria non inventa la ricevuta.

## Vincoli di sicurezza e prestazioni

- Nessuna API a consumo, IA locale pesante o servizio resident aggiuntivo.
- Registrazione di esiti in transazioni SQLite; proiezioni testuali scritte con
  file temporanei e sostituzione atomica, serializzate per ridurre conflitti.
- Nessun passo distruttivo viene autorizzato automaticamente dalla memoria.
- Nessuna sincronizzazione automatica con GitHub o con altri contatti Telegram;
  contesti e segreti restano isolati.
- La nuova memoria di progetto è richiesta esplicitamente dall'utente. Il
  Second Brain generale resta opt-in finché non verrà ridefinito separatamente.
- Alla caduta dell'alimentazione un file proiezione può essere precedente al
  database, ma il recupero controlla gli ID e lo rigenera; l'esito di un
  passo non verificato rimane interrotto anziché inventato.

## Prove richieste prima di proporre l'adozione

- Unit test su Windows/Linux (project state, receipts, doppioni, crash recovery,
  isolamento, errori, segreti, file verificati).
- Test reale su Pavilion: crea progetto, avvia almeno 3 azioni, verifica che
  CONTINUITA.md e STATO.json cambino passo dopo passo, spegni JARVIS durante
  un'attività innocua e riaprilo, verifica "interrupted" e ripresa manuale.
- Carico CPU/RAM/HDD con Minecraft aperto; assicurarsi che l'operazione del
  journal non congeli la GUI e non sovrascriva file preesistenti.
- Test regressione Telegram, Second Brain e tutti i comandi precedenti.

**Non ancora incluso in questo prototipo:** creazione/apertura/archiviazione
dei progetti tramite voce naturale; monitoraggio dei programmi esterni
indipendenti da JARVIS; controllo generalizzato del desktop; sintesi AI
periodica delle chat; registrazione automatica di ogni file modificato
manualmente dall'utente. Questi restano obiettivi separati del progetto.
