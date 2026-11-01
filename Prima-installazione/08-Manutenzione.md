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

## Distinzioni di versione accertate dall'audit
| File/area | Base pubblicata b936879 | Ramo successivo a86c2c9/5e61e53 |
|---|---|---|
| jarvis.py e preparatore Trial | Avvio secondo auto_listen; inizialmente attivo nel Trial | Avvio in standby |
| LEGGIMI ed echo launcher | Indicazione ON coerente con la base | Indicazione ON non allineata al runtime successivo |
| installa_voce.bat | Echo finale OFF non descrive necessariamente l'avvio auto_listen della base | Echo OFF coerente con standby |
| conversation_context.py | Assente | Presente nella correzione successiva |
| Test inclusi | 373 | 386 |
| README e guide storiche | Mescolano fasi; identificare sempre il pacchetto | Non usare paragrafi di altre fasi come specifica attuale |

La prima ricognizione aveva definito superati alcuni testi ON usando soltanto il ramo successivo: l'audit dello ZIP dimostra che per la base pubblicata non lo sono. Correggere l'etichetta/versione della documentazione, non il runtime funzionante per deduzione.
Nessun sorgente o launcher è stato cancellato in questo audit. Il riordino effettivo richiede riferimenti e test mirati.

## Evidenze di questa edizione
Riferimento sorgenti: 5e61e53fbb58ccb5d95b85671604cc5f365d6e04. Letti script di installazione/avvio, configurazione Telegram, settings.py, codice delle dipendenze voce/GPT/Telegram e UI. Inventariati import dei 60 moduli Python non-test.
Non eseguiti in questa fase: installazione Windows, nuovi test runtime, login, invii, audio, misura RAM o confezionamento di una nuova build. La CI precedente resta documentata nell'handoff, non va attribuita a una nuova installazione.
Fonti esterne consultate: procedura API ID Telegram e sito Python; build FFmpeg Gyan. La pagina ffmpeg.org/download.html non è stata recuperata dal servizio di ricerca, quindi il dettaglio Windows è verificato direttamente sul sito del fornitore delle build.

## Audit concreto successivo
Base b936879 verificata sui byte: 155 file coincidenti e ZIP ricreato identico, 373 test locali OK con 5 skip Windows; log CI Windows/Linux riletti. Rapporto ../docs/VERIFICA-CONCRETA-BASE-20261101.md. Queste sono prove nuove rispetto alla prima ricognizione; non includono nuova installazione o uso di dispositivi reali.
