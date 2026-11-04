## Correzione architetturale dell’utente — 4 novembre 2026

Requisito prevalente: incorporare nell’add-on di Jarvis il motore e le funzioni utili che consentono a KoboldCpp di eseguire Gemma, senza installazione/configurazione esterna di KoboldCpp. Stessa console, controllo CPU/RAM/thread/contesto, modello residente. L’utente descrive il lavoro come reverse engineering: prima analisi e riuso dei sorgenti pubblici e delle librerie, non reimplementazione cieca degli algoritmi. Prestazioni pari a Kobo sono un obiettivo da misurare sul Pavilion, non un risultato garantito.

L’adattatore subprocess che richiede un koboldcpp.exe scelto dall’utente NON soddisfa questo requisito e non va distribuito come soluzione finale. local_model/runtime.py e client.py operativi sono bozze locali non pubblicate né verificate; remoto a83f533 contiene soltanto lo stub del contratto configurazione. Broker con nove test Windows rimane riutilizzabile; i test command-line sul vecchio approccio non attestano il nuovo motore incorporato.

Fonti primarie consultate: https://github.com/LostRuins/koboldcpp (sorgenti e componenti/licenze), https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md e ggml/CMakeLists.txt (librerie native e configurazione CPU). Valutare libreria interna KoboldCpp contro llama.cpp nativo riusabile tramite binding, preservando formato Gemma2, cache e opzioni effettive. Non scegliere dal solo nome della libreria. Verificare AVX senza AVX2/FMA/F16C e altre istruzioni non disponibili sullo i3-2100; compilazione Windows e prova di caricamento/inferenza necessarie. Non affermare parità di prestazioni dal riuso dello stesso antenato del motore.

Prossimo passo: inventario funzioni necessarie e confronto tecnico dei due riusi, versione sorgente e licenze fissate, piccola prova Windows del backend incorporabile prima del raccordo GUI. Non proseguire il wrapper HTTP/Kobold esterno come consegna finale. Nessun motore nuovo già integrato, nessuna006. Le sezioni precedenti sono storia e sono superate dove incompatibili.

# Gemma locale principale Implementation Plan

> **For agentic workers:** Execute task-by-task through the authorized native project workflow. No delegation requested. Steps use checkboxes.

**Goal:** collegare Gemma alle funzioni esistenti di Jarvis e rendere ogni inferenza online facoltativa e confermata.

**Architecture:** adattatore CPU e processo KoboldCpp in local_model/, broker unico compatibile con GPTClient.call. Riutilizzo router, parser, esecutori e console attuali; il broker è usato anche da Telegram e planner.

**Tech Stack:** Python 3.11/3.12 standard library, Tkinter, KoboldCpp v1.121 già disponibile, Gemma GGUF locale, CI Windows2022.

**Spec:** docs/GEMMA-LOCALE-SPEC-20261104.md

## Global Constraints

- Zero costi aggiuntivi e nessuna API a consumo.
- Target: Windows10 x64, i3-2100 AVX senza AVX2, 10GB RAM.
- Nuova funzione .jaddon, console esistente, nessuna chat separata.
- Preservare dati/preferenze/microfono e pacchetti001–005; nuova consegna006 solo verificata.
- Test funzionali e pacchetto soltanto Windows; nessun test Linux.

## Review Focus

- Server già sulla porta: non riusarlo o terminarlo implicitamente.
- Consenso vecchio/doppio o disattivazione durante l’attesa: zero inferenze online.
- Risposta tardiva dopo revoca/chiusura: nessuna azione.
- Catalogo troppo lungo per2048 token: errore chiaro, mai troncamento cieco della richiesta.
- Telegram non può autorizzare GPT o comandi PC.

### Task1: configurazione, processo e client locale

Files: local_model/config.py, runtime.py, client.py, __init__.py; tests/test_local_model.py.
Interfaces: LocalConfig.load/save(path), LocalRuntime.start/stop/is_running; LocalClient.ask(prompt, timeout)->dict con text/provider.
- [ ] Scrivere test comportamento su config persistente, argomenti CPU-only/noavx2, loopback, proprietà processo, contesto/timeout, formato Gemma e input invariato.
- [ ] Red Windows usando stub che rifiuta generazione e non avvia processi: deve mancare il risultato atteso, non errori import.
- [ ] Implementare protocollo /api/v1/generate, /api/extra/tokencount e caricamento finito, richieste serializzate, proxy/redirect disabilitati.
- [ ] Green Windows e checkpoint con prove/limiti.

### Task2: broker unico e consenso online

Files: local_model/service.py, consent.py; tests/test_model_routing.py.
Interfaces: ModelService.call(action,timeout,**arguments), events, stop; ConsentGate.request(reason,origin,timeout), respond(id,approved), revoke.
- [ ] Red Windows: locale riesce→zero chiamate online; locale fallisce→nessuna inferenza senza consenso; login non basta; Telegram ha origine distinta.
- [ ] Implementare online OFF, consenso monouso per ask/plan; scadenza/revoca/spegnimento e serializzazione; fallback non muta preferenze.
- [ ] Green: rifiuto/scadenza/risposta duplicata, conferma di una sola richiesta, switch OFF durante attesa, locale non avviabile, nessuna ripetizione azioni.

### Task3: add-on, impostazioni e console esistenti

Files: local_model/ModelloLocale.jaddon, ui.py; addon_manager.py, addon_ui.py, jarvis.py, settings.py; tests/test_local_model_integration.py.
Interfaces: manager.local_model_enabled(); ModelSettings(parent,service,on_change); broker usato come unico service in console/planner/Telegram.
- [ ] Registrare manifest speciale allowlisted senza introdurre azione eseguibile da chat per cambiare modello/consenso.
- [ ] UI semplice: exe/GGUF, thread/batch/context/output, CPU AVX, avvia/arresta/default; configurazioni nel profilo addon-data/modello_locale.
- [ ] Separare interruttore online dalla disponibilità locale, consenso non modale con voce/testo/pulsanti; status caricamento nella console.
- [ ] Testare callback reali voce/testo, Telegram e parser con trasporti controllati, revoca/disabilitazione e apertura immediata su richiesta esplicita e chiarimento sulle proposte indirette.
- [ ] Green Windows suite regressione; aggiornare catalogo e mappa prima della consegna.

### Task4: consegna e recupero

Files: tools/build_file_access.py, check_file_access_package.py, .github/workflows/tests.yml; Prima-installazione/Modello-locale.md, local_model/LEGGIMI.md, docs/GEMMA-LOCALE-HANDOFF-20261104.md e indici.
- [ ] Preparare candidato006 con cartella local_model inclusa e nessun binario/peso duplicato.
- [ ] Suite Windows, estrazione ZIP, import, bootstrap/chiusura UI, manifest/hash/riproducibilità.
- [ ] Pubblicare solo se controlli richiesti verdi; verificare HTTP/byte/hash/posizione in cima e preservare005.
- [ ] Misure definitive Pavilion: stessa base senza add-on/disattiva/attiva inattiva/inferenza/dopo; sommare Jarvis+KoboldCpp, RAM/CPU e latenza. Nessuna inferenza su account personale durante CI. Se impossibile completare, salvare checkpoint remoto e descrivere blocco concreto.

Self-review: coperti requisiti console unica, CPU/RAM, consenso e capability reuse; incognita residua: accuratezza Gemma reale e RAM/latency con catalogo completo. Le prove API simulate non risolvono questa incognita; chiarimento sulle aperture indirette; aperture esplicite immediate secondo la precisazione utente.
