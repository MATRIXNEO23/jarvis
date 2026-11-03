# R02 — conservare la domanda durante il chiarimento

## Problema e correzione
Il parser locale può non riconoscere risposte naturali come «Non ricordo il nome preciso». Prima del fallback GPT, try_file_command azzerava la domanda ancora pendente e i risultati della scelta. La presenza di un chiarimento non va decisa soltanto cercando alcune parole nella frase.

Il servizio esistente espone ora pending_clarification: controlla domanda effettivamente pendente, abilitazione, radici consentite, revisione della policy e scadenza. Il callback conserva la domanda per il normale prompt; se la domanda appartiene a un raffinamento, riusa il percorso già vincolato a quella ricerca. La parafrasi non esegue un'azione locale e non rinnova la durata dello stato.

Modificati solo jarvis.py e file_access/service.py; nessun nuovo add-on, indice, modello o comportamento di apertura file.

## Prove Windows
- Base: 870fa27a68bc95c6e30944ecc93e144e454290e7, runtime ricerca 9df2229 preservato.
- Red: 3a8d368168491a69e13a2e980cdde4fc01a12b52, [run41612249231](https://github.com/MATRIXNEO23/jarvis/actions/runs/41612249231). Python3.11.9/job125836779004 e Python3.12.10/job125836778566: tre fallimenti nuovi, zero errori. Cambia il token della richiesta; scompare la domanda di scelta; risposta naturale al raffinamento restituisce False anziché riusare la domanda.
- Il Red esegue512 prove perché un import di classe fa scoprire due volte7 test esistenti. Corretto soltanto l'import del nuovo file, senza cambiare le asserzioni del Red.
- Green: [runtime1265360](https://github.com/MATRIXNEO23/jarvis/tree/126536015968429b8c71d14497731b448050bb67), [run41612658412](https://github.com/MATRIXNEO23/jarvis/actions/runs/41612658412). Python3.11.9/job125838180245:505 test OK,56.642s; Python3.12.10/job125838180871:505 test OK,79.073s. Cinque nuove prove in tests/test_pending_file_context.py.
- Sintassi Python/Node/PowerShell e probe nativo PASS; integrazione Windows Search PASS nel job3.12. Build, verifica ZIP e publisher SKIPPED.

I test mantengono filesystem temporaneo Windows, policy, servizio, callback e prompt reali. Trasporto modello e scheduling dei worker sono controllati. Coprono richiesta senza nome → parafrasi → domanda presente nel prompt → risposta col nome → ricerca effettiva; scelta tra due risultati con parafrasi; raffinamento che conserva richiesta/domanda/risposta. Controllano annullamento, scadenza, revoca, disattivazione, cambio progetto e sostituzione con nuova ricerca precisa.

## Ambito e limiti
Questa è una correzione della domanda pendente, non della continuità universale. Risultati senza domanda locale pendente e lavori GPT già in corso mantengono il comportamento precedente. Non è stata modificata l'interpretazione di nuove conversazioni né aggiunta una classificazione semantica parallela. Le due modifiche runtime sono state ricontrollate nel diff remoto; nessuna revisione indipendente nuova svolta in questa unità.

Nessuna chiamata al modello/account, prova microfono o prestazione sul Pavilion. Nessun test funzionale Linux. Nessuna nuova build/ZIP o modifica del PC utente; il Download resta d06e233 e la base b936879 è preservata.

## Ripresa
Restare sul problema iniziale: dialogo completo con chiarimenti e risultato locale coerente. Non passare a nuove capacità di ricerca/apertura finché il percorso conversazionale in esame non è verificato. R03 (conferme non legate all'esito locale) e gli altri casi della review restano aperti, senza attribuirli a questa correzione. Piano: superpowers/plans/2026-11-03-pending-context-r02.md.
