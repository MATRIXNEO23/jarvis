# 8. Manutenzione delle guide e ordine del repository
Queste istruzioni riguardano lo sviluppo; l'utente non deve programmare.

## A ogni nuova funzione o add-on
- Aggiornare questa cartella nello stesso lavoro: componente/versione, dipendenze, fonte, installazione, configurazione, profilo dati, comandi, prova ed errori.
- Allineare la diagnostica ai prerequisiti veri; aggiornare test propri e integrazione prima della consegna.
- Tenere nel pacchetto finale questa cartella e, per la navigazione proposta, la cartella separata Estensione-Edge quando sarà implementata.
- Aggiornare piano, stato attività e handoff prima/dopo il lavoro e dopo le verifiche.
- Chiedere all'utente su ambiguità che cambiano risultato, perdita di dati, costi o comportamento; non inventare. Risolvere autonomamente dettagli tecnici ordinari già compresi nell'obiettivo.

## Riordino a ogni aggiunta
Verificare import, riferimenti, launcher, workflow, manifest del pacchetto, test e guide prima di considerare un file inutilizzato. Un file vecchio può ancora servire al recupero o alla compatibilità.
Il contenuto attivo deve offrire un percorso unico e chiaro. Per un documento superato, indicare il sostituto oppure archiviarlo fuori dal percorso operativo; mantenere in Git la storia utile. Per codice/asset veramente superflui, dimostrare assenza d'uso e verificare la rimozione col pacchetto e i test pertinenti.
Non eliminare in blocco sorgenti, dati utente, prove diagnostiche o pacchetti che le regole richiedono di conservare. Non unificare rami né cambiare il programma sorgente autorevole senza una scelta motivata.
Se la funzione di un file resta dubbia, registrare il dubbio e chiedere sul comportamento desiderato; non cancellarlo solo per il nome.

## Contraddizioni osservate, non ancora corrette nel programma
| File del ramo evoluto | Problema | Fonte attuale |
|---|---|---|
| README.md | Mescola fasi e rami, include avvio microfono ON | Codice jarvis.py/handOff corretto: standby |
| docs/VOCE_OFFLINE.md | Nota ON e paragrafi OFF nello stesso testo | Codice del riferimento 5e61e53 |
| LEGGIMI_PROVA_TELEGRAM_50.txt | Alcune istruzioni dicono microfono ON | preparatore Trial e runtime: standby |
| avvia_jarvis.bat | Echo ON superato, launcher però conserva profilo Trial | Codice effettivo e questa guida |
| docs/ADDON_LIFECYCLE.md e guide Telegram | Riferimenti a vecchie PR/posizioni UI | Moduli del riferimento fissato |

Questa fase ha creato guide chiare e identificato i punti superati; non ha cancellato quei file né modificato il launcher. Il riordino del codice e delle guide storiche richiede verifica mirata, senza presentare la sola età come prova d'inutilità.

## Evidenze di questa edizione
Riferimento sorgenti: 5e61e53fbb58ccb5d95b85671604cc5f365d6e04. Letti script di installazione/avvio, configurazione Telegram, settings.py, codice delle dipendenze voce/GPT/Telegram e UI. Inventariati import dei 60 moduli Python non-test.
Non eseguiti in questa fase: installazione Windows, nuovi test runtime, login, invii, audio, misura RAM o confezionamento di una nuova build. La CI precedente resta documentata nell'handoff, non va attribuita a una nuova installazione.
Fonti esterne consultate: procedura API ID Telegram e sito Python; build FFmpeg Gyan. La pagina ffmpeg.org/download.html non è stata recuperata dal servizio di ricerca, quindi il dettaglio Windows è verificato direttamente sul sito del fornitore delle build.
