# Richiamo vocale e controllo consumi — 3 novembre 2026

L’utente conferma che Jarvis raccoglieva discorsi ambientali non rivolti a lui, con cuffie appoggiate e microfono dimenticato acceso; riferisce quota esaurita durante la notte. Richiede «Jarvis» all’inizio di ogni richiesta, senza necessità di «Ehi». Richiede inoltre un controllo approfondito dei prompt: NON chiede ancora di snellirli.

## Modifica e confini

Base build004, checkpoint 765b5024650bf763f3869e222e14e38ae346f43a. Ramo correttivo fix/gpt-voice-addressing-20261103; source finale d76efd46d233f914b4a8a8f69535c9f82ace053d. Nessun esperimento quota/App Server incluso.

Il normale MIC selezionava GPT_CONVERSATION, che ignorava il WakeWordGate. Ogni frase non risolta localmente poteva partire verso GPT o riempire la coda di tre frasi. Correzione nel componente esistente: WakeWordGate con require_name, applicato alla trascrizione grezza prima di correzioni apprese, log, campione voce, azioni locali e coda. Regola identica anche in CONTINUOUS, eliminando le eccezioni per risposte a dialoghi Telegram/app/file.

«Jarvis, apri Netflix» e «Jarvis, dimmi…» sono richieste; «Ehi Jarvis» resta facoltativo. Il solo nome non autorizza una frase successiva. Anche «Jarvis, sì», «Jarvis, confermo» e «Jarvis, il secondo» richiedono il nome. Il nome citato nel mezzo di una conversazione non attiva comandi. Testo digitato, pressione per parlare e dettatura intenzionalmente attivata mantengono i loro usi. Nessun cambio automatico di modalità microfono, cancellazione memoria, nuovo processo, dipendenza o modello per il filtro.

La trascrizione Vosk resta locale; il filtro non chiama un modello. Una frase indirizzata che richiede GPT continua naturalmente a consumare quota. Un riconoscimento acustico errato come «Jarvis…» può ancora essere accettato: le prove sintetiche non certificano falsi risvegli o prestazioni Pavilion.

## Prove e limiti

Red iniziale: 6c0b1a6/run41732555641, 8 test, 11 asserzioni fallite, zero errori di fixture. Cinquanta frasi ambientali raggiungevano cinquanta volte il confine GPT; altre riempivano la coda. Trasporto sostituito: zero inferenze reali. Prima correzione MIC: a91aff9/run41733308463 SUCCESS, 550 test per Python3.11/3.12.

Estensione CONTINUOUS: il primo fixture72bf818 mancava del callback dictation_voice_action; corretto, senza considerare quegli errori una riproduzione. Red valido f35a970/run41733931696: 12 test, 3 fallimenti comportamentali attesi (finestra dopo solo nome, dialogo pendente senza richiamo, correzioni prima del controllo grezzo).

Green finale: d76efd46d233f914b4a8a8f69535c9f82ace053d, [run41734087987](https://github.com/MATRIXNEO23/jarvis/actions/runs/41734087987) SUCCESS. Python3.11.9/job126258644816: 554 test OK in68.883s; Python3.12.10/job126258645656: 554 test OK in72.519s. Sintassi Python/Node/PowerShell, probe file nativo e indiceWindows live PASS (servizio/fixture ripristinati). Build, controlloZIP, artifact installabile e publisher SKIPPED.

Dodici prove mirate: cento frasi ambientali con GPT libero/occupato, richiamo iniziale per ogni richiesta, nome isolato, correzioni che non possono inventare autorizzazione, coda, comandi locali, audio TTS, varianti/punteggiatura, vecchio ascolto continuo e dettatura intenzionale. Usati callback Jarvis reali, Tk e memoria temporanea; confine modello/azioni esterne controllato. Non usati microfono, accountGPT o desktop personali. Nessun test funzionale Linux.

## Audit prompt separato

[Rapporto](AUDIT-PROMPT-CONSUMI-20261103.md), [misure](evidence/prompt-payload-audit-20261103.json). Source a91aff9/run41733308539 SUCCESS: costruttori reali, Windows3.12, dati sintetici, zero inferenze. Prompt e memoria runtime NON modificati. Dimensioni UTF-16, non token o quota: domanda breve 3815; con recenti4077; programmi4595; programmi+file4913. Memoria semanticamente vuota226; sovrapposizioni stile, duplicati progetto e limiti post-generazione documentati. Nessuna promessa percentuale sulla quota, nessun cambio modello o nuovo contatore.

## Consegna e ripresa

Solo sorgenti corretti e prove; nessuna nuova build, ZIP o pubblicazione. La 004 installata non è aggiornata automaticamente: finché non sarà distribuita una nuova versione, spegnere MIC o GPT quando non serve per evitare il vecchio comportamento. Build soltanto su nuova richiesta esplicita e verifica del pacchetto estratto.

Prossimo passo: eventuale build autorizzata con collaudo acustico sul PC; eventuale proposta di riduzione prompt da approvare separatamente partendo da blocco vuoto/stile, senza tagliare i ricordi. Barra quota/App Server restano in pausa; nessun componente installato.
