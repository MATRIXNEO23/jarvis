# Jarvis005 — preparazione e consegna, 4 novembre 2026

Alla richiesta «prosegui», dopo l’implementazione verificata e l’avviso che la004 non è aggiornata, si procede alla fase di preparazione, verifica Windows e pubblicazione della nuova candidata. Questa prosecuzione riguarda la005; non abilita build future su push ordinari.

Base: 14eeffc44055eb1a9dba936c57e10b6be155aa1f, derivata dai fix richiamoJarvis e memoria vuota verificati (558 test per Windows3.11/3.12). Ramo di confezione build/jarvis-005, nessun nuovo runtime o ulteriore snellimento prompt. Build immutabile progressiva005,004 e precedenti conservate; nessun componente Codex App Server o quotaHUD.

Confezione: aggiornati numero/versione/timestamp deterministico, identità nel verificatore e guida effettiva (riportava ancora003). Prove dal cwd ZIP estratto estese ai 12 casi richiamo, 4 casi memoria vuota e regressioni persona/router, senza import dal checkout del prodotto. Manifest/hash, solo file operativi, launcher unico, import e avvio/chiusura UI, riproducibilità con clock diverso. Suite Windows completa e probe prima della build; nessun test funzionale Linux.

Il collegamento GitHub non espone dispatch: si usa per questa consegna il trigger push del solo ramo build/jarvis-005. Publisher dipende dal successo di entrambi i job Windows, conserva le versioni, inserisce005 in cima a Download e riscarica il file pubblico controllando hash/byte e tutti i pacchetti001–004. Dopo la consegna disabilitare di nuovo trigger dedicato e publisher. Nessuna scrittura concorrente su main durante il publisher.

Stato: preparazione; pacchetto non ancora costruito, verificato o pubblicato. Prossimo passo: esito completo Windows→ZIP estratto→publisher→download HTTP verificato, poi salvare metadati, handoff e link. Non dichiarare consegnato un semplice artifact o solo il verde unit. Il collaudo reale su microfono/account/desktop/Pavilion resta da fare nella nuova cartella005, dati e impostazioni conservati.
