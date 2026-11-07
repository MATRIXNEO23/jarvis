# JRV-AUD-010 — annullamento cooperativo Gemma

Stato: progetto della correzione autorizzata, non ancora verificata. Base009 `6e6b0813789adc87435995a663cabaa4d0d48f6b`; conservare001–009.

L'utente riferisce che Jarvis funzionava nei suoi limiti e autorizza «procedi con le correzioni senza rompere niente». Versione/pacchetto di quel riscontro non identificati: nessuna nuova attribuzione di collaudo. Obiettivo: intervenire solo su timeout/arresto, preservando flussi, dati, impostazioni e memoria. Nessuna garanzia assoluta di assenza di regressioni.

## Evidenza e riuso

`NativeGemmaBridge.generate` controlla il timeout soltanto dopo `upstream.generate`; `NativeConversationSession.stop` prende il lock occupato dall'inferenza prima di chiamare abort. `jarvis.close` non ferma il proprietario nativo e il getter può crearlo dopo la chiusura.

Riutilizzare `handle.abort_generate`, già esposto dalla DLL e usato nell'upstream KoboldCpp fissato a `7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759` (`koboldcpp.py`, init_library/endpoint `/api/extra/abort` e gestione streaming). Fonte: https://github.com/LostRuins/koboldcpp/blob/7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759/koboldcpp.py . Questo dimostra il percorso cooperativo, non garantisce che qualunque fase della DLL risponda prontamente.

## Contratto minimo

- Un Timer standard per generazione richiede abort alla scadenza; viene cancellato e congiunto prima di liberare il lock nativo. Callback terminata o revocata non può interrompere la richiesta successiva. Nessun polling residente, nuova dipendenza o processo.
- Timeout distinto da stop manuale. Risultato tardivo o errore ABI successivo all'annullamento non entra nella storia. Il timeout riguarda la generazione, non un termine massimo garantito per load/C non cooperativo.
- Stop richiede prima abort e poi attende il lock solo per completare il reset. Close terminale revoca attive/in coda e richiede abort senza attendere il lock di inferenza. Non scaricare/ricaricare la DLL mentre una chiamata C è attiva. Se C ignora abort, il lavoro resta serializzato; niente terminazione forzata di thread.
- Durante load: marcare annullamento, senza chiamare abort sull'ABI in inizializzazione; controllare prima/dopo inizializzazione e caricamento e non generare dopo chiusura.
- Revisione della sessione revoca richieste già in coda e NativeChatTurn non accettati. Storia già accettata conservata; stop consente recupero, close è definitivo. La prova esplicita conserva il reload serializzato005 senza invalidare se stessa.
- Getter GUI rifiuta nuove sessioni quando closing; close usa solo l'owner già esistente e continua la chiusura se abort fallisce, con avviso sintetico.

## Rischi e limiti

Concorrenza/lifecycle: rischio regressione alto, test specifici oltre alla suite. Non modificare instradamento locale/GPT, consenso, microfono, Telegram o politica della memoria. Non attivare fallback online o retry di inferenza. Non cancellare cronologie né cambiare configurazioni utente.

Solo test Windows2022/Python3.11 e3.12. Inferenza ABI controllata per sincronizzazione deterministica; reale GGUF, latenza abort/load e Windows10/i3-2100/HDD restano da collaudare. Nessun test funzionale Linux, build, ZIP, merge o pubblicazione pacchetti.022/023 distinti.
