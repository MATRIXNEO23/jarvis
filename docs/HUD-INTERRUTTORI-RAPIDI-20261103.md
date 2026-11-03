# HUD — interruttori rapidi microfono, GPT e memoria

## Richiesta e comportamento
I tre indicatori in alto a destra diventano pulsanti cliccabili ON/OFF, mantenendo posizione e stile ciano. Servono gli stessi controlli delle impostazioni:
- MIC richiama il pulsante microfono rapido esistente (standby/ConversazioneGPT come già previsto da quel controllo).
- GPT invoca la checkbutton esistente, con salvataggio e arresto del collegamento; non inventa una seconda configurazione.
- MEMORIA invoca la checkbutton SecondBrain della conversazione generale. OFF conserva ricordi salvati, progetti e memoria breve RAM; non è un comando di cancellazione.

Il provider resta la fonte dello stato. GPT abilitato ma non collegato mostra NON CONNESSO. Microfono configurato senza stream mostra NON ATTIVO, oppure PTT se in quella modalità. La cache evita riconfigurazioni dei widget quando nulla cambia. Nessuna nuova dipendenza, servizio, modello, add-on o modifica alle funzioni di ricerca. Le modalità/manualità e l'avvio restano invariati.

## Sorgenti
Base066e7d97e3b43c981ed933d4f6478e379799421b, branch feature/hud-quick-toggles-20261103.
Runtime [2dba1d3](https://github.com/MATRIXNEO23/jarvis/tree/2dba1d36d5e019db2e3bc91b03713315ed752d22): animated_hud.py e jarvis.py.
Sorgente completo verificato [0eafb12c143f0a90d64c91b9fc6c38ab34301945](https://github.com/MATRIXNEO23/jarvis/tree/0eafb12c143f0a90d64c91b9fc6c38ab34301945) comprende la correzione della fixture.

## Prove
Red:1d54841bd99359bd596938cba9f1c005fc3c3d6b, run41668984791,511 test e3 fallimenti nei nuovi casi per assenza dei controlli cliccabili, nessun errore di import/fixture.

Primo candidato2dba/run41669378541: tre nuove prove native passano, ma10 errori NameError nelle regressioni attività. Il provider reale ora usa STANDBY/PUSH_TO_TALK e la vecchia fixture forniva soltanto GPT_CONVERSATION. Corretto tests/test_activity_status.py con le costanti reali; nessuna asserzione rimossa o alleggerita.

[Run finale41669810415](https://github.com/MATRIXNEO23/jarvis/actions/runs/41669810415) SUCCESS:
- Python3.11.9/job126034842798:511 test OK,86.351s.
- Python3.12.10/job126034842324:511 test OK,74.465s.
- Tre nuove prove tests/test_hud_quick_toggles.py: pulsanti Tk reali; callback/provider/binding app reali; salvataggio JSON e SecondBrain SQLite temporanei reali. Click singolo, stato condiviso con impostazioni, assenza di falsa connessione/ascolto, rollback su errore di salvataggio e conservazione dei ricordi/RAM.
- Sintassi Python/Node/PowerShell, probe nativo e Windows Search live PASS; build/ZIP/publisher SKIPPED. Nessun test funzionale Linux.

Trasporto GPT, dispositivo microfono e scheduling sono controllati. Non sono prove di account o acquisizione live, stop/riattivazione molto rapidi, layout visibile/DPI o prestazioni Pavilion.

## Revisione e consegna
Revisione indipendente in sola lettura sul diff066e7d9…2dba1d3: un blocco di verifica sulla fixture, risolto in0eafb12 e ricontrollato; nessun altro blocco runtime concreto. Il revisore non ha eseguito test, Green Windows letto separatamente.

002 resta il download corrente e non contiene gli interruttori. Nessuna003 generata. Per la prossima candidata autorizzata usare questo source, verificare anche dallo ZIP il nuovo test e le regressioni attività, e seguire numerazione/cautele della confezione002. Il collaudo del contesto002 e il caso dei nomi Programmi restano separati.
