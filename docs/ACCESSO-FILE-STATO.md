# Accesso file — checkpoint di sviluppo

2026-11-01: utente autorizza «Procediamo passo passo fino all’implementazione e build testabile». Base b936879, ramo feature/file-access-20261101. Regole correnti main ad13e63 recuperate; nessuna migrazione delle correzioni successive del nucleo o del microfono.

Fase 1 in corso: prova Windows nativa con cartelle note, identità volume/percorso e Windows Search, file temporanei controllati. Prima di dipendere da questo esito pubblicare/eseguire il probe su Windows CI. Nessun file utente modificato.
Fasi successive autorizzate: integrare un solo servizio con comandi/voce/GPT/gestore add-on e configurazione spunte; test automatici propri e regressioni, CI Windows e pacchetto operativo estratto. Build candidata persistente separata dalla base PC confermata; consumo e microfono/GPT reali sul Pavilion distinti dai test simulati.
Proposta semplice: usare funzioni Windows e moduli già presenti, nuova logica nella cartella file_access, file separati per responsabilità. Nessun nuovo framework, modello o indicizzatore residente. Lettura soltanto per i dati cercati; salvataggio della configurazione Jarvis necessario e distinto.

Aggiornamento utente: test solo Windows; matrice CI Windows Server 2022/Python 3.11 e 3.12. Nessuna nuova suite Linux eseguita. Adattatori nativi e probe preparati, esito Windows ancora da acquisire prima dell’integrazione.
