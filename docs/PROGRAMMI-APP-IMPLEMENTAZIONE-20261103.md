# Programmi e app — consegna004, 3 novembre 2026

**Stato corrente:** inclusa nella [build004 pubblicata](CONSEGNA-BUILD-004-20261103.md), source di confezione a1b93f3, run41694455705:542 test per versione Python e167 dal pacchetto estratto. Download pubblico e001/002/003 preservate verificati. Alla ripresa l’utente ha richiesto di continuare dal punto prima della build; eseguita una consegna una tantum, senza futuri automatismi. Le prove di implementazione sotto rimangono riferite al source67ca39c precedente alla confezione. Collaudo PC004 pendente.

[Source completo67ca39c4af21c91a12a6306b1ed967f6d83bbedd](https://github.com/MATRIXNEO23/jarvis/tree/67ca39c4af21c91a12a6306b1ed967f6d83bbedd) · [ramo feature/program-apps-20261103](https://github.com/MATRIXNEO23/jarvis/tree/feature/program-apps-20261103) · [run Windows41690560916](https://github.com/MATRIXNEO23/jarvis/actions/runs/41690560916).

## Comportamento nel codice

- Nuova add-on descrittiva Programmi e app, installata OFF; nessuna app viene consentita dall'installazione.
- Configura nel gestore esistente: elenco filtrabile, Consenti avvio, frase personale, Aggiorna elenco annullabile, Aggiungi programma locale, Prova avvio e Salva. Nessun limite a20 righe. Durante worker i controlli di modifica sono disabilitati, evitando perdita di edit al completamento.
- Fonti Windows dell'utente corrente: Start, collegamenti Desktop/Start, App Paths32/64 e manifest di app pacchettizzate. Framework/risorse/app senza launcher esclusi. Errori di fonte dichiarano copertura incompleta e preservano catalogo/consensi precedenti.
- Frase «apri la posta» associa il richiamo posta alla stessa app: apri/avvia/lancia, formule cortesi, nome originale e frase libera configurata. Precisazione locale senza chiamata al modello.
- Se il locale non comprende, resta il modello già collegato attraverso il flusso conversazionale esistente; in ConversazioneGPT e consoleGPT il fallback è automatico, senza cambiare le altre modalità voce/dettatura. Il modello propone un nome tramite addon.programmi_app.avvia/arguments.query, mai eseguibili/AUMID/comandi liberi.
- Identità e permesso risolti dal servizio locale; app esatta non consentita non viene sostituita con una app simile. Selezioni parziali/ambigue producono domanda breve e finestra, risposta nome/numero per la stessa richiesta una volta sola, con token/revisione/scadenza/contesto.
- Richieste documento, dettatura, timer, progetti espliciti, Telegram e preferenze conservano precedenza. Negazioni/domande informative non avviano app. Frasi riservate e conflitti sono rifiutati prima di salvare; controlli ribaditi al routing.
- Dati separati nel profilo attivo, addon-data/programmi_app/programs.json, salvataggio atomico; errore non sostituisce configurazione precedente. Nuove app OFF; cambi significativi di collegamento/programma manuale richiedono nuova selezione. Disattivazione/rimozione revocano richieste pendenti senza cancellare programmi o preferenze.
- ShellExecuteEx per classiche/.lnk con argomenti originali; ActivationManager/AUMID per app pacchettizzate. Esito Windows accettato distinto da finestra/contenuto osservati.

## Moduli e raccordi

program_apps/native.py e windows_apps.ps1: catalogo e API; service.py: profilo, frasi, autorizzazioni e richieste; ui.py: Tk; ProgrammiApp.jaddon: manifest; LEGGIMI.md: guida.
Raccordi limitati in addon_manager.py, addon_ui.py, local_engine.py, conversation_router.py e jarvis.py. ResolvedCapability.target esistente trasporta soltanto il nome richiesto; nessun nuovo backend/modello o dipendenza. tools/build_file_access.py include i nuovi operativi nella futura selezione; numero/publisher non attivati per un rilascio.
Main conserva sorgenti storici e Download003; il runtime nuovo è nel ramo indicato, senza merge massivo.

## Prove Windows

Comando: python -m unittest discover -s tests -v, Windows2022, source67ca39c4af21c91a12a6306b1ed967f6d83bbedd. Run41690560916 SUCCESS; nessun test funzionale Linux.

| Ambiente | Esito |
| --- | --- |
| Python3.11.9/job126107699337 | 542 test OK,115.061s,zero skip/fallimenti/errori |
| Python3.12.10/job126107699773 | 542 test OK,86.623s,zero skip/fallimenti/errori |
| Sintassi | Python/Node/PowerShell (incluso windows_apps.ps1) PASS |
| Probe Windows | Percorsi nativi e Windows Search live PASS; fixture/servizio ripristinati |
| UI app completa | Bootstrap, chiusura normale e manifest bundled OFF, profilo temporaneo/servizi live spenti PASS |
| Catalogo reale | 389 voci,2 AUMID di sistema,nessun avviso nel runner; non misura il catalogo del Pavilion |
| Lancio classico reale | .lnk temporaneo con argomenti esegue cmd di prova e crea marker; .lnk modificato rifiutato PASS |
| Attivazione pacchettizzata reale | Impostazioni/AUMID Windows, API accetta e restituisce PID3600/4396; visibilità finestra non osservata |
| Build/artifact/pubblicazione | SKIPPED; nessuna004 generata |

31 nuove prove oltre alle511 della003, senza contare fixture importate come suite duplicate. Servizio/manager/engine/JSON/Tk/callback/provider/binding reali; trasporto GPT e acquisizione microfono controllati. Lancio nativo intercettato nelle prove di servizio, reale nelle prove native isolate. Dispatcher vocale reale con trascrizioni controllate in ConversazioneGPT/PTT/Continuo; caso non compreso in ConversazioneGPT inoltrato al client esistente una volta.
Provati persistenza/rollback, app nuova/disattivata/non scelta, oltre20 risultati, errori fonte/annullamento, omonimi/scelte vecchie, revoca/scadenza/progetto, conflitti, app parziale e nessuna sostituzione da app esatta non consentita.

## Errori, review e correzioni conservate

- Red1fd8f4d/run41685538437:512 test,un fallimento gateway previsto (manifest apps.launch rifiutato). Non import mancante.
- Primo candidato5723db2/run41687523191:556 test per job;5 NameError engine in fixture storiche, nuovi casi passano. Aggiunti riferimenti reali alle fixture, senza allentare asserzioni. Rimossa duplicazione involontaria delle classi di test importate.
- Review indipendente del diff ae4eca2…5723db2 identifica frasi salva/dettatura che intercettano la voce e UI che perde modifiche durante refresh. Red87e82e4/run41688626086/job126100966340:535 test,5 fallimenti attesi,0 errori; dispatcher salva nei3 modi e controlli Tk.
- Fix7e0f25f/run41689112486: riserva progetti troppo ampia,21 errori setup. La grammatica progetti accetta anche apriX; corretta distinzione esplicito/generico e gestione ValueError in413c26d. Ricontrollo mirato senza blocchi statici.
- Run41689631152/source87a7d0c:541 test,1 conflitto contestuale e2 NameError dictation_voice_action nella nuova fixture. Riservate anche scelte contestuali save/discard/cancel, fornita funzione reale alla fixture; subTest nominano la frase. Review3c06c717 senza rilievi bloccanti.
- Green3c06c717/run41690362646:541 test per Python,0 skip/errori. Ultimo source67ca39c4af21c91a12a6306b1ed967f6d83bbedd aggiunge soltanto il test di bootstrap UI:542 PASS come sopra.
- Le verifiche di WindowsSearch girano anche dopo un errore della suite: il loro avvio non prova che unittest sia passata. Usare conclusione del passo e log Ran/OK, mai la sola fase corrente.

## Limiti e prossimo passo

Qualità STT/microfono/account/GPT reali, app Store terze (Netflix ecc.), layout/DPI e prestazioni Pavilion richiedono collaudo PC del pacchetto esatto. Le identità di launcher diverse non sono fuse per il solo nome: collegamenti/eseguibili registrati separatamente possono apparire come scelte distinte. Nessuna promessa di inventario universale o di equivalenza fra tutti i launcher.
Avvio di un'app non ne controlla le funzioni interne. Chiusura app, installazione/disinstallazione, limite20 della ricerca file, caso Programmi Explorer e rischio salva/chiudi precedente restano attività separate.
Passaggio di consegna004 completato: numero/registro aggiornati, nuove suite incluse nei167 test dello ZIP estratto, UI/manifest/download verificati e001/002/003 preservate. Prossimo passo: collaudo PC004, una app consentita e una frase personale. Nessun bisogno di ripetere progettazione o test verdi senza modifica o dubbio concreto.
