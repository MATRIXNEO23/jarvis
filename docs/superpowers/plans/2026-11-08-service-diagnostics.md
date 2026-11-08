# Service diagnostics Implementation Plan
> Execute task-by-task within the user's authorized workflow.
Goal: vedere dove si ferma Telegram e lo stato osservato dei servizi senza effetti collaterali.
Architecture: runtime_diagnostics.py per journal limitato a codici, telemetry bridge passiva, runtime_diagnostics_ui.py vista Tk a richiesta; riuso snapshot e autodiagnosi del main.
Tech Stack: Python standard library, Tk, Telethon già richiesto, Windows CI.
Spec: docs/superpowers/specs/2026-11-08-service-diagnostics-design.md.
Constraints: nessuna nuova dipendenza, nessun messaggio automatico di prova, nessun salvataggio log privato; nuove build soltanto012 autorizzata.
Review focus: callback Telegram deve filtrare come prima; lettura UI non attiva modello/rete; osservazioni stale separate; chiusura/copia senza cambiare servizi; errori di un componente non devono impedire il rapporto degli altri.

Task1: tests/test_service_diagnostics.py + nuove prove nel listener; RED su Windows, nessun runtime cambiato. Verifica fasi, esclusione, errore e zero dati privati/nessuna risposta ai contatti esclusi.
Task2: runtime_diagnostics.py ServiceEventLog/format_service_report, telegram_bridge.py diagnostic_snapshot e osservazioni passive; fix solo se riprodotto. GREEN mirato e suite completa.
Task3: runtime_diagnostics_ui.py ServiceDiagnosticsWindow(parent, get_report) con refresh/copy/close, main snapshot_services_report/open_service_diagnostics e pulsante Progetti e servizi. Comando locale diagnostica servizi da voce/chat. tests/test_service_diagnostics_ui.py: vera Tk e callback reali, nessun modello o rete.
Task4: aggiornare help/guida installazione esistente, stato/handoff/lezioni; review diff e test Windows. Poi012 con987+nuovi test (conteggio osservato, non presunto), verifica ZIP estratto, pubblicazione e stop.011 immutabile; rollback precedente e nessun cambio dati/impostazioni.
