# PROMEMORIA — Promemoria locali
## Ripresa rapida
2026-11-01: proposta dell'assistente da discutere; nessuna implementazione autorizzata. Complessità preliminare media per scadenze persistenti e riavvii.

## Idea e decisioni aperte
Memorizzare una richiesta come «ricordami alle 18 di ...» e avvisare all'orario concordato. Prima decidere comportamento con Jarvis chiuso/PC spento e avvisi scaduti al riavvio. Non promettere avvisi a computer spento; ricorrenze e notifiche Telegram non sono incluse né approvate.

## Verifiche prima del progetto
Inventariare timer, memoria e capacità già presenti sulla base confermata. Definire salvataggio, orario/fuso, eventuali dipendenze e carico senza introdurre processi continui superflui. Nessuna fattibilità runtime verificata in questa attività.

## Prove e recupero da pianificare
Persistenza, riavvio, scadenza superata, modifica/cancellazione, nessun doppio avviso, voce/testo e dati preservati. Nessun nuovo test eseguito. Pacchetto e ritorno versione nel registro solo dopo realizzazione e prove.

## Prossimo passo
Valutare utilità rispetto alle altre idee e concordare il comportamento a Jarvis chiuso; poi piano tecnico mirato.

## Regole comuni
Proposta da discutere, non autorizzazione al codice. Base conservata: b936879; [prove](../VERIFICA-CONCRETA-BASE-20261101.md). Zero costi aggiuntivi; Pavilion i3-2100/10 GB/Windows 10. Nuove funzioni come .jaddon salvo necessità tecnica motivata; prima inventariare ciò che esiste. Comandi precisi locali senza GPT; interpretazione esterna quando serve e consentita. Preservare dati, impostazioni e controllo microfono.
