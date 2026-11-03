# Richiamo vocale e controllo consumi — 3 novembre 2026

L’utente conferma parlato ambientale raccolto involontariamente durante la notte con microfono lasciato acceso e quota esaurita. Richiede il nome all’inizio di ogni richiesta: «Jarvis, attivami questo». Non è autorizzata una finestra di conversazione libera dopo il solo richiamo. Richiede inoltre un controllo approfondito dei prompt per individuare risparmi; NON autorizza ancora a snellirli.

Base corretta: build 004, ramo build/jarvis-004, checkpoint 765b5024650bf763f3869e222e14e38ae346f43a. Correzione isolata in fix/gpt-voice-addressing-20261103, senza esperimento quota/App Server.

Causa nel codice: il tasto MIC seleziona GPT_CONVERSATION, il cui ingresso voice_text non usa WakeWordGate. Ogni frase irrisolta passa al modello o alla coda, anche senza comandi. Il filtro locale esiste in CONTINUOUS ma non protegge il normale MIC GPT. Non sono disponibili log/contatori dell’episodio: causa del percorso verificata, consumo personale non misurato.

Piano autorizzato: riproduzione Windows con trascrizioni controllate; richiamo sul testo grezzo prima di correzioni, log, azioni e coda; nome in ogni richiesta in modalità conversazione GPT; nessun cambio automatico microfono né cancellazione memoria. Il solo «Jarvis» non autorizza la frase seguente. Testo digitato e pressione manuale restano intenzionali. Riutilizzare WakeWordGate senza servizi/modelli aggiuntivi. Aggiornare istruzioni UI; regressione Windows 3.11/3.12. Nessuna build/pubblicazione automatica.

Audit prompt separato: seguire voce→router→client→bridge, misurare sezioni con dati sintetici e senza chiamate modello; distinguere unità UTF-16/token reali/quota; controllare memoria, catalogo, richieste successive, output e retry. Documentare risparmi possibili, rischi e priorità prima di qualunque riduzione runtime.

Stato: test di riproduzione preparati; nessuna correzione runtime ancora verificata. Prossimo passo: esito Red Windows, correzione minima e Green completo. Barra quota/App Server in pausa, nessun componente installato.
