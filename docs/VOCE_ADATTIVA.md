# Lia — riconoscimento vocale adattivo senza caricare altri modelli

**Stato:** prototipo sperimentale nel branch `feature/adaptive-offline-voice`, PR draft #5. Vosk italiano resta il motore acustico offline. Nessun nuovo modello Whisper, servizio remoto, token API, training GPU o processo sempre attivo.

## Che cosa fa veramente

Vosk non modifica i suoi pesi e non impara da solo la voce. Una correzione approvata dall'utente viene salvata nel dizionario personale locale e applicata **al testo appena trascritto**, prima del catalogo dei comandi o di GPT. Questo può correggere nomi di programmi, parole o termini ricorrenti. **Non** corregge errori fonetici mai incontrati, mancanza di audio, microfoni difettosi o incomprensioni semantiche di GPT.

Esempio:
1. Nel test Vosk riconosce «apri blocco moto», ma l'utente aveva detto «apri blocco note».
2. Nella finestra di Jarvis si preme **«Correggi voce...»**; la finestra mostra l'ultima frase riconosciuta.
3. L'utente corregge la frase con «apri blocco note» e preme **«Conferma correzione»**.
4. Il programma estrae la porzione sicura «blocco moto» → «blocco note» e la salva in SQLite. La correzione è persistente tra riavvii.
5. Alla successiva trascrizione «Ehi Jarvis apri blocco moto» Lia passerà al router «Ehi Jarvis apri blocco note», e soltanto l'esecutore autorizzato potrà aprire Blocco note.

Non occorre usare le stesse parole di comando per forza in modalità GPT: il catalogo delle capacità e il Second Brain conversazionale restano indipendenti.

## Controllo e sicurezza

- Le correzioni sono salvate soltanto dopo la pressione esplicita di **«Conferma correzione»**; GPT e Vosk non possono aggiungerle automaticamente.
- Per una correzione persistente occorre attivare manualmente **«Second Brain locale»**; questo è disattivato per impostazione predefinita, e non viene attivato automaticamente dall'apprendimento vocale.
- Sono vietate correzioni che cambiano **wake word, negazioni, verbi di comando, salvataggi o conferme**. Un esempio non consentito è «non salvare» → «salva». Se la frase completa ha un verbo diverso, l'apprendimento è rifiutato.
- Massimo 80 correzioni brevi di 1-4 parole. Solo parole alfabetiche; niente percorsi, script, numeri di telefono, password o testo da eseguire. È possibile azzerare soltanto il dizionario nel popup, lasciando intatte le altre memorie.
- Il dizionario usa la cache RAM e una sola passata per frase, senza leggere il disco a ogni riconoscimento. Nessun buffer audio o file WAV è conservato.
- Il database è lo stesso `%LOCALAPPDATA%\\Jarvis\\second_brain.sqlite3`, non cifrato, nel profilo utente. **«Cancella memoria salvata»** elimina anche il dizionario delle correzioni. Disattivare la memoria ne sospende l'applicazione ma non elimina il database.
- Le correzioni sono eseguite anche nella dettatura manuale; non scavalcano il controllo wake word in Ascolto continuo e non alterano la scelta manuale della modalità microfono.
- Nessun requisito aggiuntivo: restano sufficienti i componenti Vosk e GPT già installati per le funzionalità rispettive.

## Verifiche richieste prima dell'adozione

**Test automatici:** persistenza dopo riavvio, differenza tra frasi complete, corretto instradamento locale, confini delle parole, nessuna propagazione a cascata, limite 80 correzioni, divieto di modificare wake word/comandi/negazioni, cancellazione e assenza di nuovi strumenti o modelli.

**Test reale sul Pavilion:** estrarre la ZIP sperimentale in un'altra cartella, lasciare il programma inizialmente in Standby, attivare Second Brain, attivare manualmente la modalità di ascolto preferita, provocare una trascrizione errata innocua, correggerla via popup, ripetere la frase e verificare il risultato dopo riavvio. Misurare eventuale rallentamento e confrontare con la versione precedente. Non usare test con eliminazione o sovrascrittura di dati reali.

## Eventuale seconda fase, non ancora implementata

Se i test dimostrano che il dizionario non basta, valutare un filtro audio opzionale a basso costo CPU, impostazioni microfono e un eventuale riconoscitore alternativo solo su frasi incerte. **Non** attivare Whisper o un secondo modello permanente senza misurazioni sull'i3-2100 e decisione separata di adozione.
