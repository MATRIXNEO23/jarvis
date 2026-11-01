# Indice dei sorgenti Jarvis

## Base operativa confermata e verificata
- Pacchetto: Jarvis-Timer-Audio-Fix2-20261031.zip in Download, confermato dall'utente come ultima build funzionante nell'uso attuale.
- Sorgenti esatti: b936879a431370d206152be7b089baf587d15499. Tutti i 155 file del pacchetto corrispondono al tree; ZIP ricreato identico, SHA-256 c37270265918c63ddb3a9cf6a2c0982d468dd1af83a1af330c5af1dfb20f9352.
- Test dello ZIP: 373 OK, 5 skip Windows su Linux; CI Windows/Linux storica riletta e file coincidenti col merge testato.
- [Rapporto/prove](VERIFICA-CONCRETA-BASE-20261101.md), [registro e ripristino](../Download/REGISTRO-VERSIONI.md).
- Le prossime aggiunte partono da questa base. Il codice successivo qui sotto è distinto: conversation_context.py e la nuova suite pipeline sono soltanto nel ramo successivo, non nella base.

## Fotografia separata del ramo successivo
Verificato il 2026-11-01 con inventario Git ricorsivo non troncato: 167 voci, 160 file versionati. Questo è un indice di disponibilità dei file, non una prova di build o di completezza di tutte le dipendenze.

## Riferimento del ramo successivo, non del pacchetto PC
- Repository: MATRIXNEO23/jarvis.
- Ramo sorgenti evoluti: feature/timer-settings-ui-20261031.
- Riferimento verificato coerente con l'handoff: 5e61e53fbb58ccb5d95b85671604cc5f365d6e04; contiene le modifiche del nucleo a86c2c9 e successiva documentazione.
- Main: catalogo/distribuzione e documentazione aggiornata; sorgenti alla radice storici. Non trattare la radice main come app evoluta e non sovrascriverla con una copia massiva.
- Prima di ogni lavoro verificare nuovamente ramo/SHA, diff e codice; prima di rilasciare collegare il pacchetto a un commit preciso dei sorgenti.

## Punti d'ingresso già presenti
Per l'accesso file sulla base b936879: [inventario mirato e proposta semplice](implementabili/ACCESSO-FILE-CONTRATTO.md), con collegamenti immutabili ai punti del codice e [integrità dei 14 file](evidence/accesso-file-20261101/source-integrity.json). La cartella del componente e la divisione dei file sono da realizzare secondo necessità effettiva; nessun nuovo schema/framework o numero di moduli prescritto. Prova nativa Windows da eseguire prima di promuovere il collegamento a soluzione verificata.

| Area | File da leggere sul ramo evoluto |
|---|---|
| Applicazione e integrazione UI | jarvis.py, settings.py |
| GPT esterno e protocollo | gpt_client.py, gpt_bridge.mjs, conversation_router.py |
| Contesto e memoria | conversation_memory.py, second_brain.py, workspace_memory.py; conversation_context.py solo nel ramo successivo |
| Voce e risposta | voice_control.py, offline_tts.py, adaptive_voice.py |
| Capacità ed esecuzione locale | capability_registry.py, live_capabilities.py, local_engine.py |
| Add-on e impostazioni | addon_manager.py, addon_ui.py, docs/ADDON_LIFECYCLE.md |
| Diagnostica | self_diagnostics.py, runtime_diagnostics.py, diagnostic_session.py, diagnostic_handoff.py |
| Esempi comandi | jarvis_commands.json, docs/CATALOGO_COMANDI.md |
| Verifiche | tests/, .github/workflows/tests.yml, .github/workflows/gpt-smoke.yml |
| Avvio e predisposizione | avvia_jarvis.bat, installa_gpt.ps1, installa_voce.bat, installa_telegram.bat |

Altre funzionalità presenti (documenti, progetti, Telegram, timer, HUD) non vanno rimosse o ricreate alla cieca. Consultare inventario, test e documentazione pertinente prima di intervenire.

## Architettura e ripresa
- [RECUPERO.md](../RECUPERO.md) e [stato attività](STATO-ATTIVITA.md): procedura e checkpoint attuali.
- [Handoff](HANDOFF-CODEX-ARCHIFY-20261031.md): risultati, versioni e limiti.
- Mappa Archify già prodotta: docs/architecture-core-20261031/jarvis-core.html su main, riferita al nucleo a86c2c9; controlli strutturali documentati, verifica browser non eseguita. La mappa non sostituisce il codice e va aggiornata quando cambiano struttura e collegamenti.
- [Piano web](PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md): proposta, non codice implementato.

## Regola di manutenzione
Conservare nel repository sorgenti completi delle modifiche, test, file necessari al pacchetto e istruzioni/dipendenze riproducibili; non limitarsi a ZIP o eseguibili. Non versionare credenziali o dati personali. Un rilascio deve permettere di risalire alla versione sorgente e alle prove eseguite.
Aggiornare questo indice e la mappa pertinente quando cambiano punti d'ingresso, moduli o rami autorevoli. Ripartire dalla struttura salvata, leggendo e verificando i soli punti interessati; non ridisegnare da zero Jarvis né assumere che una mappa vecchia sia sempre valida.

## File presenti nel riferimento esaminato
L'elenco è una fotografia del riferimento sopra, non un elenco di file tutti letti o testati in questa fase.
- .github/workflows/gpt-smoke.yml
- .github/workflows/publish-audit-zip.yml
- .github/workflows/tests.yml
- AGENTS.md
- Download/README.md
- LEGGIMI_PROVA_TELEGRAM_50.txt
- README.md
- ROADMAP.md
- action_planner.py
- adaptive_voice.py
- addon_manager.py
- addon_ui.py
- animated_hud.py
- avvia_jarvis.bat
- capability_registry.py
- configura_telegram.bat
- configura_telegram.py
- conversation_context.py
- conversation_memory.py
- conversation_router.py
- desktop_dictation.py
- diagnostic_handoff.py
- diagnostic_session.py
- dialogue_focus.py
- dialogue_style.py
- docs/ADDON_LIFECYCLE.md
- docs/AUDIT_COMPLETO_20261031.md
- docs/AUTODIAGNOSI_E_CONSIGLI.md
- docs/AUTODIAGNOSI_IBRIDA_LOCALE_GPT.md
- docs/AUTO_PROJECT_CONTINUITY.md
- docs/CATALOGO_COMANDI.md
- docs/CONTESTO_DIALOGO_V1.md
- docs/CONVERSAZIONE_GPT_DOCUMENTI.md
- docs/CORREZIONE-NUCLEO-DIALOGO-20261031.md
- docs/CORREZIONE_INTENTO_AUTODIAGNOSI.md
- docs/DECISIONI-E-LEZIONI.md
- docs/DETTATURA_BROWSER.md
- docs/DIAGNOSTICA_RUNTIME_SIGN_IN_GPT.md
- docs/DIAGNOSTICA_VISIBILE_E_RECUPERO.md
- docs/DIALOGO_CONTINUO.md
- docs/GPT_SETUP.md
- docs/HUD_ANIMATO.md
- docs/HUD_CINEMATIC_BACKGROUND.md
- docs/HUD_HIGH_FIDELITY.md
- docs/HUD_REFERENCE_V2.md
- docs/HUD_RIFERIMENTO_20261031.md
- docs/HUD_VOICE_ACTIVITY.md
- docs/MEMORIA_AFFIDABILE_V1.md
- docs/PROJECT_MAINTENANCE_AND_SELF_AUDIT.md
- docs/PROJECT_MEMORY_TELEGRAM.md
- docs/QUALITA_CONVERSAZIONE_V1.md
- docs/RECUPERO_BLOCCO_NOTE_CHIUSO.md
- docs/REGISTRO_CAPACITA_LIVE_GPT.md
- docs/SECOND_BRAIN.md
- docs/TELEGRAM_CONTATTI_INVIO_VOCALI.md
- docs/TELEGRAM_CRONOLOGIA_50.md
- docs/TIMER_E_IMPOSTAZIONI_20261031.md
- docs/VOCE_ADATTIVA.md
- docs/VOCE_OFFLINE.md
- docs/VOCE_RISPOSTE.md
- docs/VOICE_PROJECT_DOCUMENTS.md
- document_dialog.py
- document_execution.py
- document_language.py
- document_recovery.py
- document_store.py
- examples/addons/DiagnosticaSistema.jaddon
- gpt_bridge.mjs
- gpt_client.py
- hud_backdrop.py
- hud_orbits.py
- hud_raster.py
- hud_reference.py
- installa_gpt.bat
- installa_gpt.ps1
- installa_modello_voce.py
- installa_telegram.bat
- installa_voce.bat
- jarvis.py
- jarvis_commands.json
- jarvis_persona.py
- jarvis_timer.py
- live_capabilities.py
- local_engine.py
- managed_documents.py
- memory_boundaries.py
- network_telemetry.py
- notepad_controller.py
- offline_tts.py
- plan_runner.py
- planner_ui.py
- preference_voice.py
- prepara_test_telegram50.py
- project_documents.py
- project_voice.py
- runtime_diagnostics.py
- second_brain.py
- self_diagnostics.py
- settings.py
- source_review.py
- speech_activity.py
- startup_greeting.py
- telegram_bridge.py
- telegram_commands.py
- telegram_directory.py
- telegram_outbound_flow.py
- telegram_secret_dialog.py
- telegram_security.py
- telegram_ui.py
- telegram_voice.py
- tests/smoke_gpt_bridge.mjs
- tests/test_action_planner.py
- tests/test_adaptive_voice.py
- tests/test_addon_lifecycle.py
- tests/test_animated_hud.py
- tests/test_auto_project_continuity.py
- tests/test_capability_registry.py
- tests/test_conversation_pipeline.py
- tests/test_conversation_router.py
- tests/test_desktop_dictation.py
- tests/test_diagnostic_handoff.py
- tests/test_diagnostic_recovery.py
- tests/test_dialogue_focus.py
- tests/test_dialogue_style.py
- tests/test_document_dialog.py
- tests/test_document_execution.py
- tests/test_document_language.py
- tests/test_gpt_client.py
- tests/test_hud_backdrop.py
- tests/test_hud_raster.py
- tests/test_hud_ui_regressions.py
- tests/test_jarvis_persona.py
- tests/test_jarvis_timer.py
- tests/test_live_capabilities.py
- tests/test_local_engine.py
- tests/test_managed_documents.py
- tests/test_memory_boundaries.py
- tests/test_network_telemetry.py
- tests/test_offline_tts.py
- tests/test_plan_runner.py
- tests/test_project_maintenance.py
- tests/test_project_orbits_telegram.py
- tests/test_runtime_diagnostics.py
- tests/test_second_brain.py
- tests/test_self_review.py
- tests/test_settings.py
- tests/test_speech_activity.py
- tests/test_telegram_bounded_history.py
- tests/test_telegram_commands.py
- tests/test_telegram_multi_contacts.py
- tests/test_telegram_no_network.py
- tests/test_telegram_secret_dialog.py
- tests/test_telegram_trial_launcher.py
- tests/test_voice_control.py
- tests/test_voice_installer.py
- tests/test_voice_project_documents.py
- tests/test_workspace_memory.py
- voice_control.py
- workspace_gui.py
- workspace_memory.py
