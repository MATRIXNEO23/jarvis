# Jarvis: browser, ricerca e dettatura (versione di prova)

Queste funzioni aggiungono capacità alla versione già collaudata sul Pavilion.
Non serve reinstallare Vosk o scaricare un altro modello italiano: si usa la
stessa installazione vocale esistente.

## Browser predefinito

Con **Premi per parlare** o **Ascolto continuo**, pronuncia:

- **"Jarvis, apri il browser"**: apre Google nel browser predefinito di Windows.
- **"Jarvis, cerca nel browser Colosseo di Roma"**: apre una ricerca Google.
- **"Jarvis, cerca su internet mod Minecraft"**: stessa funzione.

Anche il campo dei comandi locali accetta `apri browser` e
`cerca nel browser TESTO`. Sono operazioni esplicite: non vengono eseguite
ricerche quando Jarvis riconosce una frase qualsiasi.
Il browser usa Internet per le pagine e per le ricerche; il riconoscimento
vocale resta **offline**. Questa versione usa Google come motore di ricerca
per le ricerche; l'impostazione personalizzabile è prevista successivamente.

Nel pianificatore GPT, l'apertura del browser e la ricerca richiedono
l'approvazione del piano, come le altre azioni pianificate.

## Dettatura nelle altre finestre

1. Avvia Jarvis: il microfono è sempre **spento**.
2. Seleziona manualmente **Ascolto continuo**. Jarvis non cambia modalità da
   solo, neanche quando apri Minecraft.
3. Apri Blocco note, Word o un campo di testo nel browser, e **clicca nel campo
   in cui vuoi scrivere**.
4. Senza tornare a cliccare su Jarvis, pronuncia **"Ehi Jarvis, attiva dettatura"**.
   Si può anche dire **"Ehi Jarvis"** e, entro 10 secondi, **"attiva dettatura"**.
   Se preferisci, premi **Attiva dettatura** nell'interfaccia, poi torna nel
   campo di testo dell'altra finestra.
5. Parla normalmente. Jarvis prova a digitare il testo riconosciuto in quel
   campo tramite gli eventi Unicode di Windows. Di' **"a capo"** per andare
   alla riga successiva.
6. Per terminare, pronuncia **"Ehi Jarvis, disattiva dettatura"** oppure
   **"Ehi Jarvis, interrompi dettatura"**. Funzionano anche mentre sei
   nel campo di testo: non vengono scritte nella pagina. Il pulsante
   **Disattiva dettatura** resta disponibile come alternativa.

I comandi di attivazione e disattivazione sono **vocali** e richiedono
**Ehi Jarvis** in ascolto continuo, come tutti i comandi. La dettatura,
una volta attivata, scrive il parlato normale senza dover ripetere il nome.

La dettatura e l'ascolto sono due impostazioni diverse. Spegnere la dettatura
**non** mette il microfono in standby. Per spegnere il microfono scegli
**Standby** manualmente. Scegliendo Standby, la dettatura viene interrotta.
La dettatura è disattivata a ogni riavvio di Jarvis e richiede ascolto
continuo, perché con Premi per parlare il pulsante di Jarvis prenderebbe
il focus dalla finestra in cui vuoi scrivere.

### Sicurezza e limiti della versione alpha

- La dettatura **non è attiva per impostazione predefinita** e non scrive
  nella finestra di Jarvis.
- Se passa a un'altra finestra o controllo, Jarvis non scrive il testo
  riconosciuto e chiede di disattivare e riattivare la dettatura.
- I campi password di Windows tradizionali vengono esclusi, ma i campi
  delle pagine web e le app personalizzate **non sono sempre riconoscibili**.
  **Non usare la dettatura per password, dati bancari o altri segreti.**
- Non usa la clipboard né modifica file direttamente; il testo viene
  inviato come tasti al programma in primo piano. Alcuni programmi, giochi
  o campi protetti potrebbero ignorarli.
- Jarvis non invia testo dettato a GPT e non registra l'audio; tuttavia il
  programma in cui detti (ad es. un documento cloud) può sincronizzare i dati
  secondo le proprie regole.
- Sul Pavilion il primo collaudo ha rilevato un errore di inserimento:
  Vosk riconosceva le parole ma Windows rifiutava i tasti per una struttura
  `SendInput` di dimensione errata (32 byte invece di 40 su Windows x64).
  La correzione usa ora la struttura completa e mostra il codice di errore
  Win32 in caso di nuovo rifiuto. **Correzione da confermare sul Pavilion**.
- Il messaggio «Testo inviato a Windows» significa che Windows ha accettato
  gli eventi di tastiera, **non garantisce** che l'applicazione li abbia
  effettivamente visualizzati.
- La versione corrente non dispone ancora di punteggiatura avanzata,
  correzione testo o selezione intelligente dei campi. Prima di usarla
  in documenti importanti verifica sempre il testo.

## Verifica su Pavilion

La precedente versione vocale di Jarvis è già stata provata con successo:
apertura Blocco note e altri comandi vocali. Queste **nuove funzioni** di
browser e dettatura sono ancora da collaudare sul Pavilion.

Prove: avvio in standby; browser; ricerca con frase; dettatura in Blocco
note; cambio finestra durante dettatura (nessun testo nella nuova finestra);
arresto dettatura; standby e riavvio; prova CPU/RAM con Minecraft aperto.
