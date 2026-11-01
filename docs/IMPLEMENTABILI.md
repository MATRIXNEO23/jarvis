# Cose implementabili — Jarvis
Aggiornato: 2026-11-01. **Stato: discussione delle alternative prima dell'implementazione.** Il browser non è una priorità obbligata. Nessuna delle nuove proposte qui sotto è approvata per il codice.

## Indice delle schede
| ID | Funzione | Stato | Complessità preliminare | Prossimo passo |
|---|---|---|---|---|
| WINDOWS | [File, cartelle e programmi](implementabili/WINDOWS.md) | Requisiti utente in discussione; lettura codice/fonti svolta | Avvio programmi più circoscritto; ricerca generale da progettare | Riuso Windows prima di nuove dipendenze; chiarire verifiche sui file |
| CRONOMETRO | [Cronometro](implementabili/CRONOMETRO.md) | Proposta dell'assistente da discutere | Potenzialmente bassa; da verificare col timer esistente | Chiarire utilità e funzioni minime |
| PROMEMORIA | [Promemoria locali](implementabili/PROMEMORIA.md) | Proposta dell'assistente da discutere | Media per persistenza, riavvio e scadenze | Concordare comportamento a PC spento |
| WEB | [Navigazione browser](implementabili/WEB.md) | Requisiti raccolti; revisione tecnica sospesa | Alta rispetto a un modulo locale senza servizi esterni | Discutere prima le alternative; nessuna precedenza automatica |

Le difficoltà sono stime di pianificazione, non misure o esiti di fattibilità. Le prime due idee sono suggerimenti dell'assistente, non richieste già approvate dall'utente. Non fissare ordine di sviluppo finché la discussione non lo definisce. Un miglioramento di funzione esistente non richiede necessariamente una nuova add-on.

## Come riprendere
Per «riprendiamo il cronometro» aprire la relativa scheda: obiettivo, stato/autorizzazioni, decisioni, prove, dubbi e prossimo passo. Leggere i riferimenti puntuali e verificare i soli componenti coinvolti; non ricostruire ogni volta tutti i commit/artifact. Per tornare a una build usare [registro versioni](../Download/REGISTRO-VERSIONI.md).

Una scheda per ogni add-on/attività distinta, ricavata dal [modello](implementabili/MODELLO.md). Aggiungerla all'indice senza trasformare un'idea in un impegno. Gli aspetti condivisi rimangono in [AGENTS](../AGENTS.md), i requisiti dettagliati in un unico piano collegato: evitare copie che divergono.

## Stati e completamento
Separare: proposta → requisiti discussi → progetto revisionato → implementazione autorizzata → codice in corso → verifiche → pacchetto consegnato → riscontro PC. Sospesa, bloccata e scartata hanno motivazione esplicita. Test automatici e prova sul PC vanno registrati separatamente con ambito e limiti. Solo la versione identificata e confermata diventa riferimento per l'ambito collaudato; nessuna garanzia universale.

Base di sviluppo preservata: Timer Audio Fix2, b936879; [audit](VERIFICA-CONCRETA-BASE-20261101.md). Creazione di questo catalogo: solo documentazione, nessuna modifica al programma.

## Precisazione dell'utente
«Prendere appunti» significa che l'assistente documenta nella repository caratteristiche e decisioni dei progetti da riprendere; non è una richiesta di funzione appunti in Jarvis. La proposta APPUNTI inserita per fraintendimento è stata ritirata. Cronometro e promemoria restano soltanto suggerimenti dell'assistente da discutere, non requisiti concordati.
