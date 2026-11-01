# Recupero del lavoro Jarvis
Questo è il punto d'ingresso per una nuova sessione di sviluppo con accesso al repository MATRIXNEO23/jarvis. Non è memoria runtime di Jarvis e non concede autorizzazioni nuove.

## Procedura di avvio
1. Leggere integralmente AGENTS.md.
2. Leggere docs/STATO-ATTIVITA.md e docs/HANDOFF-CODEX-ARCHIFY-20261031.md, compresi gli aggiornamenti finali.
3. Leggere docs/DECISIONI-E-LEZIONI.md e il piano collegato all'attività da riprendere.
4. Verificare ramo, SHA, diff, file correnti e prove prima di assumere che uno stato descritto sia ancora valido. Main contiene catalogo e documentazione; verificare dove si trovano i sorgenti effettivi.
5. Riprendere dal prossimo passo non risolto, mantenendo decisioni e autorizzazioni documentate. Non rieseguire installazioni, migrazioni, pubblicazioni o test già conclusi senza motivo. Non confondere la richiesta di ripresa con approvazione di una proposta rimasta in attesa.
6. Dopo ogni modifica aggiornare nello stesso insieme di lavoro handoff e stato dell'attività; documentare nel registro scelte, motivazioni tecniche, prove ed errori. Ogni commit significativo di codice/configurazione deve avere continuità aggiornata; una breve serie di edit può avere un checkpoint unico prima del commit. Se le API producono commit distinti per file, completarli in sequenza e collegarli nel checkpoint. Prima di pausa/fine turno registrare il prossimo passo preciso. Il registro Git fornisce lo SHA del commit che contiene l'aggiornamento: non inseguire aggiornamenti ricorsivi per registrare il proprio SHA.
7. Se una richiesta contrasta con architettura o vincoli, spiegare il problema con evidenze e proporre un'alternativa concreta che preservi l'obiettivo. Le scelte di prodotto restano all'utente; i dettagli tecnici ordinari spettano all'assistente.

## Stato orientativo al 2026-11-01
- Navigazione web: piano docs/PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md salvato; implementazione non avviata, da discutere prima di creare.
- Continuità dialogo: CI precedente documentata e riscontro positivo dell'utente; versione installata e collaudi rimanenti da verificare.
- Metodo di sviluppo: memoria nel repository, lavoro per fasi, prove osservabili, UI semplice e recupero delle add-on. L'utente decide risultati e compromessi, non deve programmare.

L'indice e gli aggiornamenti nell'handoff sono la fonte per lo stato più recente: questa sintesi non li sostituisce. Le istruzioni hanno effetto solo quando la nuova istanza ha accesso al repository e le legge; nessun meccanismo di questa documentazione può attribuire accesso automatico a una chat esterna.

## Ripresa dopo interruzione improvvisa
L'handoff viene salvato durante il lavoro, prima della modifica (in corso), subito dopo (eseguita, verifiche pendenti) e dopo i test (esito osservato). Non richiede una richiesta dell'utente a fine sessione. Un checkpoint rimasto in corso può indicare un'interruzione: controllare commit, diff e file effettivi; non trattarlo come successo o assumere che nulla sia cambiato. Resta inevitabile una possibile differenza tra ultimo checkpoint salvato e operazioni interrotte prima del salvataggio.

## Sorgenti e architettura esistenti
Consultare docs/INDICE-SORGENTI.md: identifica il ramo del programma evoluto, i moduli, gli script, i test e la mappa Archify già disponibile. Non confondere la radice main storica con i sorgenti evoluti; verificare SHA e codice pertinente, senza ricreare da zero l'architettura. Aggiornare i riferimenti quando cambiano struttura o versione autorevole.

## Installazione e consegna
Guide aggiornate in Prima-installazione/README.md; distinguono codice di riferimento, profilo Trial e dipendenze. Aggiornarle a ogni modulo nuovo. Prima di annunciare una funzione installabile verificare pacchetto e link effettivo in Download/README.md. La sola documentazione non è una nuova build. Per il riordino verificare uso reale dei file e chiedere su ambiguità che cambiano il risultato.
