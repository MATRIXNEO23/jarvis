# JRV-AUD-001 — piano di correzione

Goal: rendere effettivi i permessi GPT per funzione, conservando autorizzazioni alle azioni e sessione Telegram.
Base: 61a95f8c78f0d429ede21acee25c87a77f91d712. Richiesta del 7 novembre: procedere alle correzioni con spiegazioni brevissime.

Architettura: riusare OnlinePermissionPolicy e i callback esistenti. Mai nega anche con conferma/sessione; Chiedi consuma il consenso per richiesta; Autorizzato evita il dialogo. Ricontrollo prima della pipe e su risposta Telegram. Nessuna migrazione di impostazioni o nuovo servizio.

- [x] Riprodurre su Windows il bypass di Mai nella console e Telegram e la richiesta superflua per allowed. Test reali dei callback con profili temporanei e confine pipe controllato.
- [ ] Aggiungere un grant di richiesta revocabile in local_model/online_permissions.py; integrare chat, file, planner, diagnosi e Telegram senza cambiare le azioni locali.
- [ ] Esporre in online_permissions_ui gli identificatori effettivamente utilizzati; default Mai invariato. Nessuna configurazione utente riscritta.
- [ ] Verificare rifiuto, allowed, revoca durante conferma/startup, file corrotto, azioni locali e login separato. Adeguare le fixture storiche con permessi espliciti solo nei profili sintetici.
- [ ] Suite Windows 3.11/3.12. Nessun test funzionale Linux. Nessuna build, pubblicazione ZIP o merge.

Rischi: bloccare involontariamente GPT quando manca il file policy (il default documentato è Mai); ricontrollo mancante nel worker; consenso globale che amplia un permesso specifico; fixture che mascherano il diniego.
Recupero: ramo correttivo isolato, nessuna modifica al ramo sorgente o main. Le versioni distribuite restano intatte.
Stato: test di riproduzione preparati; non ancora eseguiti. Runtime non modificato.

Red Windows: run42326631728, commit4b21693, cinque fallimenti comportamentali nei tre test aggiunti. Candidata runtime e ulteriori prove di revoca/scoping/planner preparate; Green non ancora eseguito.
