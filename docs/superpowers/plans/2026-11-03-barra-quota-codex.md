# Barra quota Codex Implementation Plan

> **For agentic workers:** Execute this plan task-by-task using the user's authorized project workflow. Steps use checkbox syntax. Implementation authorized in the following user turn. Task1 boundary/no-account protocol verified; personal-account gate remains open. No release authorized.

**Goal:** Mostrare il residuo Codex reale vicino a Interfaccia neurale,con lettura alla connessione,ogni60s e al clic,senza turni del modello.
**Architecture:** Add-on codex_quota con provider di sola lettura e snapshot inRAM; riuso di gestore,bridge/IPC e header esistenti. Il collegamento alla fonte reale è un gate di fattibilità: la004 non espone quote. Non migrare la conversazione per ottenere una barra.
**Tech Stack:** Python3.11/3.12,Tk,Node22.12 già previsti,Windows10x64; protocollo ufficiale account/rateLimits/read se compatibile.
**Spec:** ../../BARRA-QUOTA-CODEX-20261103.md.

## Global Constraints
- Automatico alla connessione e ogni60s dopo il termine del tentativo; clic manuale immediato se non già occupato.
- Nessun prompt,streamResponse,turn/start,acquisto o riscatto crediti per controllare la quota.
- Timeout10s; oltre75s dall’ultimo successo dato non aggiornato.
- Una lettura e un timer alla volta; risultati invalidati a cambio account/disconnessione/revoca/chiusura.
- Zero costi aggiuntivi; HP Pavilion i3-2100/10GB/Windows10x64; niente test funzionali Linux.
- Cartella add-on .jaddon separata; installazione OFF; preservare004,profilo e modalità voce.
- Nessuna percentuale ipotizzata o identitàQuotaCodex sostituita da quotaSiwC/header API.
- Nessuna build005 autorizzata dal progetto.

## Review Focus
1. Vecchio account risponde dopo il cambio: nessuna percentuale del vecchio account visibile (Task3).
2. Clic ripetuti durante il timeout: una sola chiamata e nessun blocco Tk (Task3/4).
3. Più finestre o un bucket diverso: etichette corrette,nessuna somma o falsa quotaCodex (Task2).
4. AutenticazioneSiwC adatta all’inferenza ma non ai servizi account: restituire indisponibile,mai avviare un turno di prova (Task1).
5. Header stretto/DPI/chiusura con worker attivo: controlliMIC/GPT/MEMORIA accessibili e callback tardivi ignorati (Task4).

### Task1 — dimostrare la fonte senza inferenza
**Files:** Create tools/probe_codex_quota.py,tests/test_codex_quota_provider.py,codex_quota/provider.py.
**Interfaces:** Provider.read_limits(*,timeout:float)->dict; Provider.available()->bool; QuotaUnavailable come errore distinto. Il provider è associato a una session_key opaca,niente segreti restituiti.
- [x] Preparare test del trasporto con sola richiesta account/rateLimits/read e trappole su turn/start,/responses,streamResponse e login automatico:0 chiamate a questi percorsi.
- [x] Eseguire Red su Windows: python -m unittest discover -s tests -p test_codex_quota_provider.py -v; il test deve fallire per lettura non collegata,non per import casuale.
- [x] Implementare il probe --protocol-only senza account e validare la richiesta/snapshot campione. Non usare il campione per dichiarare quota live.
- [ ] Verificare il protocollo disponibile su Windows; se esiste una sessione esplicitamente collegata al modulo,una lettura autenticata --read-account può produrre soltanto stato,metodo,bucket,finestre e tempi. Niente token,headers,email o contenuti chat nei log.
- [ ] **Gate:** provare autenticazione appropriata e bucketcodex reale. Se SDKSiwC attuale non lo consente,documentare accesso non disponibile e confronto della soluzione minima con costo/processi/RAM; non installare app-server o introdurre login diversi senza aver reso concreta quella scelta. Non procedere alla presentazione come quota live.
- [x] Green delle trappole e checkpoint con ambiente,fonte,risultato e limiti; nessun tempo/consumo inventato.

### Task2 — normalizzare gli snapshot reali
**Files:** Create codex_quota/service.py,tests/test_codex_quota_service.py.
**Interfaces:** QuotaWindow(used_percent:float,window_minutes:int|None,resets_at:int|None); QuotaSnapshot(session_key:str,limit_id:str,windows:tuple,checked_at:float,received_monotonic:float). normalize_limits(payload:dict,session_key:str,now:float,monotonic:float)->QuotaSnapshot.
- [ ] Red Windows per0/100,una/due finestre,NaN/inf/fuori0–100,campi assenti,bucket diverso e reset passato. residues0→100,100→0;0non valeNone.
- [ ] Normalizzare soltanto snapshot del bucketrichiesto; preferire rateLimitsByLimitId.codex quando presente e coerente. Rifiutare valori invalidi; assenza resta indisponibile. Più finestre: principale=max used_percent,con durata indicata.
- [ ] Eseguire suite del Task2 su Windows; verifica che nessun valore sia derivato da token locali,orologio/reset presunto o altri bucket.
- [ ] Checkpoint con errori/correzioni e nessuna quota personale nei log.

### Task3 — timer,concorrenza e ciclo add-on
**Files:** Modify codex_quota/service.py,addon_manager.py,capability_registry.py; Create codex_quota/QuotaCodex.jaddon,tests/test_codex_quota_schedule.py,tests/test_codex_quota_addon.py.
**Interfaces:** QuotaService(provider,clock,wall_clock,emit); set_session(key:str|None,connected:bool)->None; set_enabled(enabled:bool)->None; request_refresh()->bool; tick()->None; close()->None. emit(event:dict) invia quota_state con revisione/sessione al poll UI,senza segreti.
- [ ] Red con clock/trasporto controllati:connessione→1lettura,59s→0,60s→1;manuale riprogramma;100clic durante lavoro→1totale;timeout10s→errore,nuovo tentativo non prima60s;checked_at non avanza dopo errore.
- [ ] Red per disconnessione,cambio account,add-onOFF/rimozione e chiusura durante lettura:risultato tardivo scartato e timer fermo.
- [ ] Aggiungere l’azione fidata di sola lettura account.quota.read associata esclusivamente a quota_codex/ addon.quota_codex.aggiorna,senza argomenti o target liberi; gestore attuale richiede azioni non vuote. Riutilizzare consenso/digest/revoca,senza manifest eseguibili.
- [ ] Implementare scheduler con worker e un solo in-flight; timer/clic invocano il servizio locale direttamente. Non inviare automaticamente la quota a GPT e non usare il modello per aggiornare la UI.
- [ ] Green Windows di servizio/gestore,con trappola sul client inferenza anche durante installazione/attivazione/reset. StatoOFF non invia rete.
- [ ] Checkpoint; se adattamento gestore interferisce con altre add-on,fermare le fasi dipendenti e correggere la regressione.

### Task4 — barra e raccordo al programma
**Files:** Create codex_quota/ui.py,tests/test_codex_quota_ui.py; Modify animated_hud.py,jarvis.py,gpt_bridge.mjs,gpt_client.py,addon_ui.py.
**Interfaces:** QuotaBar(parent,on_refresh); update(state:dict)->None; close()->None. JarvisHUD.set_quota_state(state:dict),set_quota_refresh_handler(callback). IPC read_quota aggiunto al bridge solo quando Task1 prova il trasporto; GPTClient.call resta il canaleesistente.
- [ ] Red Tk reale su Windows:barra nel header,timestamp e residuo corretti,più finestre nel dettaglio,clic/Invio/Spazio richiamano servizio senza run_gpt.
- [ ] Implementare barra a fianco della scritta e prima dei controlli rapidi,senza nuove librerie grafiche; aggiornamento via poll output_queue esistente,nessun thread tocca Tk.
- [ ] Mostrare dati non aggiornati dopo75s,disconnessione e ultimoerrore; preservare vecchio valore soltanto etichettato. La chiusura rimuove timer/callback.
- [ ] Raccordare gli eventi dell’account realmente usato dal provider,non assumere che sessioneGPT equivalga a sessioneCodex. Un account non compatibile resta indisponibile.
- [ ] Green Tk1024×768 e1280×720,UIbootstrap/chiusura e controlliMIC/GPT/MEMORIA invariati; provaPavilion/DPI resta separata.
- [ ] Checkpoint e review mirata del diff; regressioni appropriate e0 chiamate inferenza per refresh.

### Task5 — guide,verifiche e consegna futura
**Files:** Create codex_quota/LEGGIMI.md,Prima-installazione/Quota-Codex.md; Modify Prima-installazione/README.md,tools/build_file_access.py,tools/check_file_access_package.py,docs/INDICE-SORGENTI.md e documenti di continuità pertinenti.
- [ ] Documentare attivazione,lettura60s/clic,timestamp,account e stati; indicare dipendenze effettive emerse dal Task1 e rimedi precisi per componente mancante.
- [ ] Dopo singolo Green pertinente,eseguire regressioniWindows3.11/3.12 e sintassiPython/Node/PowerShell applicabile. Non ripetere audit globali senza motivo.
- [ ] Misurare confrontoOFF/inattivo/lettura/dopo lettura con processi figli; distinguere runner da Pavilion e non dichiarare RAM/CPU target dalla sola CI.
- [ ] Alla successiva richiesta esplicita di build,leggere Download/BUILD-NUMBERS.json corrente,adeguare numero e verificare ZIP estratto includendo moduli/manifest/risorse e provequota; pubblicare soltanto dopo esiti obbligatori verdi.
- [ ] Aggiornare handoff/evidenze/registro/capacità e verificare contenuti remoti;004 e dati conservati.

## Self-review del progetto
Coperti tempi60/75/10,clic concorrenti,quota reale,più finestre,revoca/account,accessibilità e prove0inferenza. Nessuna API quota del SDKSiwC inventata; IPC e API del modulo sopra sono proposte,non funzioni esistenti. Task1 condiziona la scelta del trasporto prima dei raccordi. Protocollo/account reale non verificati e nessuna garanzia di quota disponibile al solo termine del progetto.
Prossimo passo: eventuale implementazione autorizzata comincia esclusivamente dal Task1; non iniziare una barra con percentuali simulate per poi cercare la fonte.

## Esito Task1 — prima fase,3novembre2026
9test per Python3.11/3.12 e probe ufficialeWindows PASS,run41728307013/source897b95b. Nessun turno del modello; nessunaquota autentica ottenuta. Passo protocollo senza account verificato,passo con sessione personale non eseguito; il gate resta aperto. [Misure,limiti e scelta del collegamento dedicato](../../QUOTA-CODEX-FATTIBILITA-20261103.md). Non spuntare gli altri task o iniziareHUD finché la fonte personale non è dimostrata.
