# Richiamo vocale e controllo consumi — 3 novembre 2026

L’utente conferma parlato ambientale raccolto involontariamente durante la notte con microfono lasciato acceso e quota esaurita. Richiede il nome all’inizio di ogni richiesta: «Jarvis, attivami questo». Non è autorizzata una finestra di conversazione libera dopo il solo richiamo. Richiede inoltre un controllo approfondito dei prompt per individuare risparmi; NON autorizza ancora a snellirli.

Base corretta: build 004, ramo build/jarvis-004, checkpoint 765b5024650bf763f3869e222e14e38ae346f43a. Correzione isolata in fix/gpt-voice-addressing-20261103, senza esperimento quota/App Server.

Causa nel codice: il tasto MIC seleziona GPT_CONVERSATION, il cui ingresso voice_text non usa WakeWordGate. Ogni frase irrisolta passa al modello o alla coda, anche senza comandi. Il filtro locale esiste in CONTINUOUS ma non protegge il normale MIC GPT. Non sono disponibili log/contatori dell’episodio: causa del percorso verificata, consumo personale non misurato.

Piano autorizzato: riproduzione Windows con trascrizioni controllate; richiamo sul testo grezzo prima di correzioni, log, azioni e coda; nome in ogni richiesta sia in conversazione GPT sia in Ascolto continuo; nessun cambio automatico microfono né cancellazione memoria. Il solo «Jarvis» non autorizza la frase seguente. Testo digitato e pressione manuale restano intenzionali. Riutilizzare WakeWordGate senza servizi/modelli aggiuntivi. Aggiornare istruzioni UI; regressione Windows 3.11/3.12. Nessuna build/pubblicazione automatica.

Audit prompt separato: seguire voce→router→client→bridge, misurare sezioni con dati sintetici e senza chiamate modello; distinguere unità UTF-16/token reali/quota; controllare memoria, catalogo, richieste successive, output e retry. Documentare risparmi possibili, rischi e priorità prima di qualunque riduzione runtime.

Red Windows osservato: source 6c0b1a6, run 41732555641, 8 test eseguiti, 11 asserzioni fallite per il comportamento atteso (nessun errore di fixture). 50 frasi ambientali avviano 50 richieste al confine GPT; altre frasi entrano nella coda. Trasporto modello sostituito, nessuna inferenza reale. Correzione minima applicata nei sorgenti: require_name=True nel gate esistente, controllo sul grezzo, feedback e guida aggiornati. Vecchie prove intenzionali ora pronunciano esplicitamente Jarvis. Prossimo passo: Green completo Windows 3.11/3.12; non dichiarare ancora verificata la correzione. Barra quota/App Server in pausa, nessun componente installato.


## Regola estesa a ogni modalità di ascolto passivo

Il requisito utente vale anche per Ascolto continuo: rimosse le eccezioni per risposte a dialoghi Telegram, app e selezioni file; anche queste richiedono Jarvis iniziale. Dettatura avviata manualmente e pressione per parlare restano intenzionali. Nuova riproduzione valida Windows f35a970/run41733931696: 12 test, 3 fallimenti comportamentali per vecchio Ascolto continuo (richiamo isolato arma la frase seguente, dialogo pendente scavalca richiamo, correzione agisce prima del filtro); nessun errore. La prima estensione del fixture in72bf818 mancava di dictation_voice_action, corretta prima della riproduzione valida.

Prima correzione normale MIC: a91aff9/run41733308463 SUCCESS, 550 test per Python3.11/3.12, sintassi/probe nativi e indice Windows live verificati; nessuna build. Ora in verifica la regola comune a entrambe le modalità. Prompt invariati: audit offline Windows41733308539 SUCCESS, zero inferenze, rapporto AUDIT-PROMPT-CONSUMI-20261103.md e misure docs/evidence/prompt-payload-audit-20261103.json. Non promettere quota risparmiata dalle misure di caratteri.
