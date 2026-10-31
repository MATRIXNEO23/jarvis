# JARVIS — comprensione del contesto, fase 1

Questa è una modifica circoscritta alla **comprensione dei riferimenti conversazionali**.
Non introduce nuovi poteri di modifica, accesso a programmi, Telegram, database
personali, connessioni a servizi a pagamento o esecuzione di azioni implicite.

## Dialogo breve

- Quando Jarvis ha appena posto una domanda concreta, una risposta breve
  ("sì", "no", "quello", "la seconda", un nome) viene associata a **quella
  precisa domanda**, non scambiata per un nuovo argomento.
- La domanda precedente viene passata al modello come **dato non affidabile**,
  non come autorizzazione: un "sì" ambiguo non può da solo far eseguire un
  comando o completare una modifica.
- Dopo "Come vuoi chiamare il nuovo progetto?", "sì" non è un nome valido;
  la domanda rimane aperta. L'utente può rispondere "Minecraft".
- Se manca qualsiasi domanda recente e l'utente dice soltanto "sì" o "quello",
  Jarvis chiede UNA cosa: "A quale domanda ti riferisci?".
- Un comando nuovo ed esplicito sostituisce un vecchio chiarimento non concluso.

## Progetto corrente

- "Questo progetto" significa **soltanto il progetto effettivamente
  selezionato** nel registro di Jarvis.
- La memoria breve e i documenti del progetto vengono mantenuti separati:
  cambiare progetto resetta il riferimento breve.
- Se non è selezionato nessun progetto e l'utente chiede "Come procede
  questo progetto?", Jarvis domanda: "Quale progetto salvato vuoi aprire per
  risponderti?" e attende un nome esatto.
- Se l'utente risponde "Minecraft", Jarvis verifica il nome contro il database
  reale. Non sceglie un progetto solo perché ha un nome somigliante. Dopo la
  selezione, riprende la domanda precedente **in modalità chat testuale senza
  possibilità di eseguire azioni**, non tramite il pianificatore.
- "Rinomina questo progetto" e "Elimina questo progetto" sono riferimenti
  al progetto selezionato, ma seguono ancora le autorizzazioni e le conferme
  della gestione progetti.

## Una sola precisazione

Le risposte di chiarimento del modello vengono ridotte a una singola
domanda concreta. Il limite dei 5000 caratteri per il bridge GPT è
rispettato dando priorità alla domanda pendente e al progetto realmente
selezionato; la cronologia rimane informazione non attendibile.

## Collaudo manuale sul Pavilion (dopo sicurezza antivirus)

1. Crea un progetto, chiedi la rinomina senza specificare il nuovo nome,
   rispondi "sì": Jarvis deve richiedere il nome **senza rinominarlo**.
2. Rispondi "Colosseo": deve rinominare lo stesso UUID.
3. Avvia una conversazione e verifica risposta breve "quello" dopo una
   domanda precisa: Jarvis deve conservarne il riferimento.
4. Passa a conversazione generale; "Come procede questo progetto?" deve
   chiedere UN nome, non inventare un progetto.
5. Dì il nome di un progetto salvato: Jarvis deve identificarlo senza creare
   copie e, se ChatGPT è disponibile, rispondere alla domanda iniziale.
6. Chiedi di parlare di un altro progetto: la domanda precedente non deve
   trasferirsi al nuovo.
7. Prova "sì" isolato dopo un commento senza domanda: non deve eseguire
   alcuna azione.

CI e unit test provano i componenti, ma non sostituiscono il microfono e
il modello collegato sul PC dell'utente.

**Sicurezza:** lo ZIP precedente è stato rilevato da Defender come
Trojan:Script/Wacatac.B!ml. I test unitari non risolvono la segnalazione
antivirus. Non forzare il download né disattivare Defender.
