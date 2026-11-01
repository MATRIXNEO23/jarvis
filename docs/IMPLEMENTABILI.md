# Cose implementabili — Jarvis

## Aggiornamento vigente — Accesso file 0.1.0 candidato disponibile
Primo incremento generale in sola lettura realizzato e consegnato: [Download](../Download/README.md), [rapporto](ACCESSO-FILE-RAPPORTO-20261101.md), sorgenti 7298fb632cd9b72386fd7a30f469b307ce7e6fa5. Solo test Windows: 393 per versione Python e 20 estratti, avvio/chiusura/rilascio cartella PASS. Prova PC pendente. Applicazioni classiche/Store complete, formati oltre il testo e scritture/cancellazioni restano fasi future; browser sospeso. Le proposte non diventano realizzate per il solo nome della scheda.

Aggiornato: 2026-11-01. **Stato: accesso file prioritario, inventario/contratto e revisione iniziale completati; prova Windows e codice runtime ancora da eseguire.** Il browser resta sospeso. Requisiti approvati, prove e implementazione sono distinti nelle schede.

## Indice delle schede
| ID | Funzione | Stato | Complessità preliminare | Prossimo passo |
|---|---|---|---|---|
| WINDOWS | [File, cartelle e programmi](implementabili/WINDOWS.md) | Primo incremento Accesso file consegnato come candidato Windows | [Implementazione/prove](ACCESSO-FILE-RAPPORTO-20261101.md), sorgenti 7298fb6 | Collaudo del pacchetto esatto sul Pavilion; altre fasi da discutere |
| CRONOMETRO | [Cronometro](implementabili/CRONOMETRO.md) | Proposta dell'assistente da discutere | Potenzialmente bassa; da verificare col timer esistente | Chiarire utilità e funzioni minime |
| PROMEMORIA | [Promemoria locali](implementabili/PROMEMORIA.md) | Proposta dell'assistente da discutere | Media per persistenza, riavvio e scadenze | Concordare comportamento a PC spento |
| WEB | [Navigazione browser](implementabili/WEB.md) | Requisiti raccolti; revisione tecnica sospesa | Alta rispetto a un modulo locale senza servizi esterni | Discutere prima le alternative; nessuna precedenza automatica |

Le difficoltà sono stime di pianificazione, non misure o esiti di fattibilità. Cronometro e promemoria sono suggerimenti dell'assistente, non richieste già approvate dall'utente. L'utente ha scelto l'accesso file come priorità; non cambiare l'ordine senza una nuova indicazione. Un miglioramento di funzione esistente non richiede necessariamente una nuova add-on.

## Come riprendere
Per «riprendiamo il cronometro» aprire la relativa scheda: obiettivo, stato/autorizzazioni, decisioni, prove, dubbi e prossimo passo. Leggere i riferimenti puntuali e verificare i soli componenti coinvolti; non ricostruire ogni volta tutti i commit/artifact. Per tornare a una build usare [registro versioni](../Download/REGISTRO-VERSIONI.md).

Una scheda per ogni add-on/attività distinta, ricavata dal [modello](implementabili/MODELLO.md). Aggiungerla all'indice senza trasformare un'idea in un impegno. Gli aspetti condivisi rimangono in [AGENTS](../AGENTS.md), i requisiti dettagliati in un unico piano collegato: evitare copie che divergono.

## Stati e completamento
Separare: proposta → requisiti discussi → progetto revisionato → implementazione autorizzata → codice in corso → verifiche → pacchetto consegnato → riscontro PC. Sospesa, bloccata e scartata hanno motivazione esplicita. Test automatici e prova sul PC vanno registrati separatamente con ambito e limiti. Solo la versione identificata e confermata diventa riferimento per l'ambito collaudato; nessuna garanzia universale.

Base di sviluppo preservata: Timer Audio Fix2, b936879; [audit](VERIFICA-CONCRETA-BASE-20261101.md). Creazione di questo catalogo: solo documentazione, nessuna modifica al programma.

## Precisazione dell'utente
«Prendere appunti» significa che l'assistente documenta nella repository caratteristiche e decisioni dei progetti da riprendere; non è una richiesta di funzione appunti in Jarvis. La proposta APPUNTI inserita per fraintendimento è stata ritirata. Cronometro e promemoria restano soltanto suggerimenti dell'assistente da discutere, non requisiti concordati.
