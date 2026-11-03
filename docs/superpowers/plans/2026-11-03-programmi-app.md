# Programmi e app Implementation Plan

> **For agentic workers:** Execute this plan task-by-task using the user's authorized project workflow. Steps use checkbox syntax; implementation native in this session, independent read-only review at the end.

**Goal:** Avviare programmi classici e Store scelti dall'utente, con frasi personalizzate e varianti naturali, locale prima del GPT.
**Architecture:** Add-on descrittivo programmi_app e adattatore fidato nella cartella program_apps; catalogo Windows dell'utente, selezioni atomiche nel profilo, stesso esecutore per voce/testo/GPT. UI Tk esistente estesa senza duplicare ricerca file.
**Tech Stack:** Python3.11/3.12 stdlib, Tk/ttk, Windows PowerShell5.1 e API Windows; nessun acquisto o processo residente.
**Spec:** docs/PROPOSTA-PROGRAMMI-APP-20261103.md (main0e6469a4, approvata dall'utente «procediamo con progettazione e implementazione»).

## Global Constraints
- Solo Windows/CI Windows per test funzionali; niente test Linux.
- HP Pavilion i3-2100,10GB,Windows10 x64; zero costi aggiuntivi.
- Preservare003, dati, impostazioni, manualità microfono e runtime storico main.
- Sorgenti separati feature/program-apps-20261103 dalla003/ae4eca2; nessuna build o pubblicazione004 senza richiesta.
- .jaddon descrittivo, provider locale verificato, nessuna esecuzione arbitraria dal GPT/manifest.
- Chiusura app e controllo interno app restano esclusi da questo incremento.

## Review Focus
- Nome difficile/parziale o due app omonime: scelta una sola volta, nessun lancio casuale (Task2/4).
- Negazione/domanda, conflitto con documenti/cartelle e frase personalizzata: non rubare comandi esistenti (Task2/4).
- Target collegamento modificato, revoca durante worker/modello: consenso riletto prima dell'avvio (Task2/4).
- Fonte Windows lenta o incompleta: Tk reattivo, dati precedenti conservati e avviso esplicito (Task1/3).
- Store non disponibile nel runner o API accettata senza finestra: prova distinta dal desktop personale e nessuna falsa conferma (Task1/4).

## Task1 — inventario e avvio nativo
**Files:** program_apps/native.py,program_apps/windows_apps.ps1,program_apps/__init__.py; tests/test_program_apps_native.py.
**Interfaces:** AppEntry(id,name,kind,target,fingerprint,manual=False); discover(cancelled=None)->(list[AppEntry],list[str]); manual_entry(path)->AppEntry; launch(entry)->str.
- [ ] Scrivere test Windows con .exe e .lnk temporanei/reali, inventario utente corrente, dati spazi/Unicode, fonte fallita e annullamento; per attivazione Store distinguere API/payload controllato e app disponibile nel runner.
- [ ] Eseguire Red comportamentale del gateway con il test Task2 prima di aggiungere la capacità.
- [ ] Implementare metadati Start/AppsFolder, .lnk Start/Desktop e App Paths; identità Store AUMID e classiche .lnk/.exe o Shell ID verificato. Nessun limite20/copertura taciuta; errori fonti espliciti. Lancio via ShellExecuteEx/ActivationManager su target locale, senza comando generato.
- [ ] Eseguire probe/test Windows e registrare limiti; nessuna azione su desktop/account personali.

## Task2 — servizio, permessi, lingua e contesto
**Files:** program_apps/service.py,program_apps/ProgrammiApp.jaddon; addon_manager.py,capability_registry.py,local_engine.py; tests/test_program_apps.py.
**Interfaces:** ProgramService(folder,enabled); refresh_catalog(cancelled=None); entries(); save_preferences(preferences); add_manual(path); parse_command(text); execute(operation,arguments)->ProgramResult(status,message,listing=None); reset(context=None); context_hint(); available(); commands().
**Boundary:** manifest addon.programmi_app.avvia→apps.launch, argomento GPT query soltanto; ResolvedCapability handler program_apps,target=query. Service risolve identità e permessi correnti; nessuna identità nativa dal modello.
- [ ] Test Red sul manager reale: manifest app installabile OFF, attivazione e azione consentita; comandi locali raggiungono lo stesso servizio e solo app spuntata.
- [ ] Implementare persistenza atomica catalogo/preferenze in addon-data/programmi_app; errori non azzerano i dati precedenti, nuove app OFF, identità distinta dagli omonimi; modifiche significative target manuale revocano selezione.
- [ ] Parser locale: negazioni/annulla prima di shortcut/grammatica; apri/avvia/lancia e forme cortesi, alias derivato da frase personale; customphrase non toglie nome ufficiale. Collisioni con alias/frasi e comandi esistenti segnalate prima del salvataggio; omonimi ufficiali permessi ma richiedono scelta.
- [ ] Pending con token/revisione/contesto/scadenza, consumato una sola volta; nome/numero nella stessa richiesta, reset su nuovo argomento/progetto/disattivazione/revoca.
- [ ] Test Windows: persistenza, rollback, >20 app, incompleto, alias e varianti, negazione/domanda, duplicati, timeout/scelta stale e revoca; esecutore nativo controllato soltanto dove serve evitare avvii reali ripetuti.
- [ ] Verificare Green/regressioni Windows e checkpoint.

## Task3 — configurazione
**Files:** program_apps/ui.py,program_apps/LEGGIMI.md,addon_ui.py; tests/test_program_apps_ui.py.
**Interfaces:** ProgramSettings(parent,service,on_change); show_choices(parent,listing,on_select).
- [ ] Test Tk con servizio/profilo temporanei reali: selezione+riga comando+Salva, errore collisione senza perdita dati, filtro e >20 app, revoca.
- [ ] Implementare lista filtrabile Consenti avvio/nome/tipo/stato, dettaglio e comando personalizzato; Aggiorna/Aggiungi/Prova/Salva. Prova usa solo selezioni già salvate.
- [ ] Aggiornamento cancellabile fuori thread Tk, risultati via coda e after solo mentre in corso; nessun polling residente. Salva finale atomico, errore visibile, righe non disponibili conservate.
- [ ] Aggancio configure esplicito del gestore; .jaddon auto installato OFF se bundled.
- [ ] Green Tk Windows e checkpoint.

## Task4 — raccordi voce/testo/GPT, regressioni e review
**Files:** jarvis.py,conversation_router.py,live_capabilities.py se necessario,tools/build_file_access.py; tests/test_program_apps_integration.py.
- [ ] Test callback reale estratto come fixture esistenti: frase locale senza GPT, varianti/alias, selezione a due turni, worker con revoca; prompt/risposta GPT simulati con gateway reale e target non inventabile.
- [ ] try_program_command(message) dopo controlli dialoghi protetti e prima fallback GPT; instradare engine.execute_program operation,args dal worker locale e dal capability handler. Conservare wake/PTT, dictation, documenti, progetti e salvataggi; reset richieste su cambio contesto/chiusura.
- [ ] Prompt capacità avvia con arguments.query, nessun inventario intero nel prompt; context_hint piccolo per domanda pendente e richiesta originale. Aiuto dinamico coerente e varianti non riconosciute al modello già connesso, senza nuovo backend/account.
- [ ] Configurare CI push del solo ramo per test, publisher003 disabilitato. Aggiungere operativi program_apps al selettore ZIP per futura build senza crearla.
- [ ] Eseguire suite Windows3.11/3.12, sintassi Python/Node/PowerShell e probe nativi; leggere conti/errori, correggere soltanto cause dimostrate.
- [ ] Review indipendente read-only del diff completo e ricontrollo dei fix necessari, verifiche applicabili prima della chiusura. Documentare source/run/prove e limiti microfono/account/Pavilion.
- [ ] Pubblicare checkpoint main e ramo, con source completo e prove. Comunicare stato sorgenti verificati, non download004; nuova build soltanto su richiesta.

## Metodo esecutivo e recupero
Scelta tecnica ordinaria: implementazione nativa in questa sessione, review indipendente finale; l'utente ha delegato le scelte e autorizzato il lavoro. Non richiedere una nuova approvazione del piano per ripetere decisioni risolte. Se emerge scelta di prodotto sostanziale, porre una domanda mirata e proseguire solo il lavoro indipendente.
Ogni Red/Green/errore ha checkpoint remoto con source/run, causa dimostrata, limiti e prossimo passo. Main conserva documentazione/catalogo003, mai merge massivo dei sorgenti. Profilo003 non migrato; i nuovi dati sono additivi separati.
