# CRONOMETRO — Cronometro locale
## Ripresa rapida
2026-11-01: proposta dell'assistente per la discussione; nessuna implementazione autorizzata. Complessità potenzialmente bassa rispetto al web, ancora da verificare.

## Idea e decisioni aperte
Contare il tempo trascorso con avvio, pausa e azzeramento, usando voce e controlli visibili. È un esempio di funzione locale circoscritta; non sono concordati interfaccia, salvataggio o comportamento alla chiusura. Non aggiungere giri/intertempi o altre opzioni senza discuterli.

## Verifiche prima del progetto
Esiste già il timer: [indice sorgenti](../INDICE-SORGENTI.md), jarvis_timer.py e relativa suite sulla base esatta. Inventariare capacità e riuso prima di duplicare logica o proporre migrazione del timer. Nessun codice di cronometro inventariato in questa attività.

## Prove e recupero da pianificare
Tempo monotono, pausa/ripresa/reset, voce/testo, disattivazione e nessuna regressione del timer. Non è stato eseguito alcun nuovo test. Collegare eventuale pacchetto futuro al registro versioni e preservare dati.

## Prossimo passo
Discutere se è utile e definire il comportamento minimo; poi valutazione tecnica mirata, senza partire col codice.

## Regole comuni
Proposta da discutere, non autorizzazione al codice. Base conservata: b936879; [prove](../VERIFICA-CONCRETA-BASE-20261101.md). Zero costi aggiuntivi; Pavilion i3-2100/10 GB/Windows 10. Nuove funzioni come .jaddon salvo necessità tecnica motivata; prima inventariare ciò che esiste. Comandi precisi locali senza GPT; interpretazione esterna quando serve e consentita. Preservare dati, impostazioni e controllo microfono.
