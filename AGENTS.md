# Istruzioni persistenti — Jarvis

## Decisioni, risultati ed errori
Dopo ogni fase significativa aggiornare docs/DECISIONI-E-LEZIONI.md e il documento di handoff con problema, decisione, motivazione tecnica sintetica, prove osservabili, commit, workflow, risultato e questioni aperte.

Promuovere a riferimento soltanto soluzioni verificate, indicando ambito e limiti del collaudo. Un test locale non prova il funzionamento del modello esterno o dell'hardware Windows.

Un approccio fallito va scartato dalle soluzioni raccomandate: indicare causa, prova del fallimento e condizione necessaria per rivalutarlo. Conservare una scheda diagnostica minima per non ripetere l'errore; non cancellare log utili, cronologia, pacchetti precedenti o dati utente. Una nuova prova può correggere una conclusione precedente: registrare il superamento senza riscrivere i fatti.

Non limitarsi a un elenco di comandi: spiegare il nesso tecnico tra problema, scelta e risultato con evidenze riproducibili. Distinguere fatti dimostrati, ipotesi e attività non eseguite. Non salvare credenziali o conversazioni personali nei registri.

## Vincoli
- Zero costi aggiuntivi e nessuna API a consumo.
- Archify è uno strumento di sviluppo, mai componente di Jarvis.
- Continuità conversazionale nel nucleo; nuove funzionalità come add-on salvo necessità motivate.
- Preservare impostazioni, salvataggi e controllo manuale microfono; standby all'avvio secondo handoff.
- Non pubblicare pacchetti difettosi o dichiarare test senza prove.
- Le modifiche del nucleo conversazionale proposte nel rapporto del 31 ottobre richiedono l'approvazione del piano già richiesta dall'utente. Il fix CI faba673 è autorizzato e verificato.

## Sorgenti e continuità
Main contiene il catalogo Download e sorgenti storici alla radice. Il ramo feature/timer-settings-ui-20261031 contiene l'app evoluta: verificare sempre SHA, ramo, diff e workflow prima di intervenire. Non sostituire in blocco la radice main per correggere un test.

Handoff autorevole: docs/HANDOFF-CODEX-ARCHIFY-20261031.md su main. Rapporto: docs/DIAGNOSI-ARCHIFY-DIALOGO-20261031.md su main.
