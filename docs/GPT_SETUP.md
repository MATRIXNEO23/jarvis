# Collegare Jarvis a ChatGPT (Windows 10 x64)

Questa integrazione usa **solo** il kit ufficiale [Sign in with ChatGPT DevKit](https://github.com/openai/sign-in-with-chatgpt-devkit). Il runtime Node viene installato **su richiesta** e usato da Jarvis come processo figlio; non richiede API key, account API a consumo, servizi in avvio automatico o un grande modello AI sul PC.

## Installazione sul Pavilion

1. Installa **Python 3.11 x64** e **Node.js 22.12 o successivo** dagli **siti ufficiali**; Node include npm. Windows 10 rimane il sistema operativo previsto.
2. Scarica la repository `MATRIXNEO23/jarvis` (ZIP GitHub o git clone), estraila in una cartella del computer.
3. Fai doppio clic su **`installa_gpt.bat`**. Lo script PowerShell scarica il sorgente ufficiale OpenAI bloccato sul commit `0a36fefeb913055c8c7a1a29b63d82b96b2e841a`, installa le dipendenze del solo SDK locale usando npm e lo compila in `%LOCALAPPDATA%\Jarvis\runtime\siwc`.
4. Fai doppio clic su **`avvia_jarvis.bat`**. L'opzione GPT è accesa per impostazione predefinita. L'indicazione **«GPT abilitato» non significa «connesso»**.
5. Premi **Connetti ChatGPT**. Si apre il browser di sistema verso `https://auth.openai.com` per login e consenso esplicito all'utilizzo del piano, se disponibili per l'account.
6. Dopo il collegamento, inserisci una domanda e premi **Chiedi a GPT**. Il pulsante **Esegui locale** continua a usare soltanto i comandi offline.

## Privacy, costi e sicurezza

- OAuth e richieste AI avvengono mediante `@siwc/local`; **nessun login tramite browser automatizzato** e nessuna chiave API a consumo.
- Le credenziali ChatGPT vengono cifrate su Windows tramite **DPAPI CurrentUser**, salvate in `%LOCALAPPDATA%\Jarvis\gpt_account`, mai inserite nella repo o passate a Python.
- Jarvis e il bridge Node comunicano tramite **pipe stdin/stdout**, non una porta server aperta; il provider OAuth apre temporaneamente una callback di loopback solo quando necessaria.
- Il microfono resta **spento** all'avvio: il collegamento GPT non abilita automaticamente l'ascolto vocale.
- Attivazione GPT di default, disattivazione e riattivazione **manuali**. Senza timeout automatico di inattività; non vengono fatte richieste GPT da sole.
- **Nessuna API a consumo**: se il permesso `chatgpt.tokens.use.direct`, la quota o il modello non sono disponibili, Jarvis mostra l'errore e rimane operativo offline.
- Usa **Scollega account** per revocare la connessione locale. Spegnere l'interruttore GPT arresta il processo ma non revoca i permessi OAuth: la revoca è un'azione separata.
- Non inserire password o dati sensibili nelle domande a GPT. Le richieste testuali inviate con **Chiedi a GPT** raggiungono i server OpenAI.

## Diagnostica

- Se vedi «SDK non installato», ripeti `installa_gpt.bat`. Non cancellare la cartella `gpt_account`: conserva le credenziali cifrate.
- Se Node non viene trovato, riapri il terminale/Windows dopo averlo installato. Controlla `node --version`.
- Se il login non concede uso del piano, consulta le impostazioni del tuo account ChatGPT. Non esiste fallback a pagamento.
- Il kit è stato progettato da OpenAI per app locali; il codice Jarvis è un adattamento **Windows sperimentale**. Test automatizzati di sintassi e protocollo **non equivalgono a login e inferenza collaudati** sul tuo account e sul tuo Pavilion.

## Per sviluppatori

- `gpt_client.py` avvia il figlio solo quando GPT è abilitato.
- `gpt_bridge.mjs` usa il DevKit ufficiale, i flussi OAuth inclusi e la libreria streaming Responses. Non interpreta comandi di Windows.
- `local_engine.py` esegue soltanto le azioni allowlisted; le risposte GPT **non sono mai eseguite automaticamente**.
- Per accedere al motore di pianificazione GPT -> task locale occorreranno schema dei piani, validazione, permessi, backup, rollback e test end-to-end.

## Timeout e annullamento — correzione011 verificata nei sorgenti

Le richieste GPT vocali e scritte usano lo stesso limite di attesa di180secondi
dopo l'avvio del collegamento. Login600secondi e controlli40secondi mantengono
i limiti precedenti. Non sono minuti garantiti per l'intero avvio/installazione.

Se una domanda scade, Jarvis chiede di annullare quella singola richiesta al
collegamento già aperto e ignora eventuali risposte tardive. Il messaggio
distingue comando di annullamento inviato o non inviato; non conferma che il
server abbia già smesso. Nessun nuovo invio automatico, login o scollegamento
dell'account per riprovare. Token già consumati non vengono restituiti.

Si riusa AbortSignal del DevKit già fissato, senza aggiornare SDK o dipendenze.
Client Python e bridge Node devono provenire dalla stessa versione del codice.
Verifica Windows2022:811test per Python3.11/3.12, run42352732284,
inclusi19nuovi controlli con SDK simulato. Nessuna nuova build o collaudo account.
