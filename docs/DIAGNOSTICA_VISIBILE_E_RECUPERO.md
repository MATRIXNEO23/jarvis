# Jarvis — Diagnostica visibile, recupero da blocchi e comandi vocali

## Segnalazione reale (31 ottobre 2026)

Durante il collaudo della build Jarvis-Autodiagnosi-Ibrida-GPT.zip:
- premendo «Autodiagnosi Jarvis», il programma risponde che l'analisi è già in corso;
- nessun indicatore conferma l'avanzamento e non arriva un rapporto;
- il comando vocale non avvia la diagnosi.

La causa esatta del blocco sul Pavilion non è ancora determinata, perché
non abbiamo un log del worker. Tuttavia il codice aveva tre difetti
verificabili: la variabile diagnostic_busy poteva restare True se
inspect_jarvis terminava con un'eccezione imprevista, non c'erano
progressi né timeout, e una richiesta vocale poteva essere intercettata
prima da un dialogo di documento pendente. Un errore nel polling GUI
poteva inoltre interrompere i successivi cicli di ricezione.

## Correzioni

- diagnostic_session.py: identificatore incrementale per ogni scansione;
  stato in memoria, file esaminati e fase; rifiuto delle risposte in ritardo.
- self_diagnostics.py e source_review.py: progressione reale in 4 fasi
  (inventario, sintassi, consigli statici, completamento).
- jarvis.py: stato «Autodiagnosi: fase X/Y (secondi)» e barra di avanzamento
  visibili anche quando il menu secondario «...» è chiuso. Il pulsante
  «Annulla» interrompe l'attesa nella GUI; non uccide forzatamente
  il thread che sta leggendo, e ignora gli eventuali risultati tardivi.
- Errori del worker: vengono riportati con il solo nome del tipo eccezione
  nella console; la sessione viene dichiarata fallita e si può riprovare.
- Dopo 12 secondi senza progressi: avviso esplicito; dopo 120 secondi
  complessivi: rilascio del blocco UI, avviso e risultato tardivo ignorato.
  Al massimo due vecchi worker ancora attivi possono coesistere: se entrambi
  non terminano, Jarvis non avvia un terzo ed esplicita di dover essere
  riavviato. Il limite non implica una terminazione forzata dei thread.
- Watchdog separato dal polling generale della console, che ora
  programma il prossimo ciclo prima di elaborare gli eventi; un errore
  di interfaccia non sopprime per sempre il ricevimento dei risultati.
- Comandi vocali: normalizzazione di «auto diagnosi», «auto-diagnosi»,
  «l'autodiagnosi», riconoscimento locale prioritario prima di dialoghi
  documenti e richieste GPT. Il riconoscitore Vosk può comunque sbagliare
  la trascrizione: controllare la riga «TU >» o l'ultima frase riconosciuta.

## Collaudo futuro sul Pavilion

1. Chiudere tutte le istanze precedenti di Jarvis (i thread di quella
   versione non possono essere corretti a caldo).
2. Fare backup completo di %LOCALAPPDATA%\Jarvis prima di avviare
   una build sperimentale; decomprimere in una nuova cartella.
3. Premere «... > Autodiagnosi Jarvis». Verificare che si veda
   «Autodiagnosi: inventario/sintassi/consigli» e il conteggio Y/Z;
   attendere un rapporto con priorità e file/riga, oppure un errore
   specifico anziché il vecchio blocco indefinito.
4. Provare «Annulla» durante un controllo. Lo stato deve diventare
   «annullata» e il pulsante tornare disponibile. Non confondere
   annullamento dell'attesa con terminazione immediata del worker.
5. Riprovare un controllo e verificare che il vecchio risultato non
   sovrascriva quello nuovo.
6. Attivare manualmente la modalità voce desiderata e dire
   «Jarvis, fai un'autodiagnosi» (in ascolto continuo non-GPT,
   usare la frase di attivazione «Ehi Jarvis»). La riga «TU >»
   deve mostrare la frase davvero riconosciuta.
7. Solo dopo aver verificato il rapporto locale, usare «valuta
   la diagnosi con GPT»; l'invio richiede consenso e non concede
   permessi di modifica del programma.

Nessuna nuova API a pagamento, esecuzione di sorgenti o automodifica.
Lo scanner statico non verifica il funzionamento del programma nel suo
insieme e non è uno scanner antivirus.

## Sicurezza

Il precedente rilevamento Defender
Trojan:Script/Wacatac.B!ml non è stato chiarito. Una build pubblicata
o CI verde non garantiscono che il file sia sicuro. Non disattivare
Defender, non creare esclusioni né autorizzare un file segnalato.
