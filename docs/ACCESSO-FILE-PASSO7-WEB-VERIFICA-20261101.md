# Fonti web via Sign in with ChatGPT — verifica di fattibilità, 1 novembre 2026

## Obiettivo e ambito
Dopo «Possiamo procedere?» verificare come il GPT già collegato possa usare fonti web per precisare una ricerca locale. Non è l'implementazione del progetto browser/Edge e non richiede un secondo indice del PC. Rimangono locale per primo, risultato verificato sul PC e zero costi aggiuntivi.
Runtime Jarvis di riferimento: a279a4ee944c23a93545835ada740793055418fe; checkpoint 93343fa. Questo incremento modifica soltanto strumenti di sviluppo, raccordo CI e documenti; gpt_bridge.mjs e l'installazione sul PC non ricevono una nuova capacità web.

## Fatti verificati nei sorgenti
installa_gpt.ps1 fissa il DevKit ufficiale al commit 0a36fefeb913055c8c7a1a29b63d82b96b2e841a. Il bridge chiama sdk.streamResponse con model/input e riceve text.
| Sorgente upstream | Blob letto | Riscontro |
|---|---|---|
| packages/local/src/types.ts | e80f3d2fd6c7bb976b2c83469c4453bf57b16e07 | StreamResponseOptions espone model/input/instructions/signal/onDelta; nessun tools |
| packages/local/src/responses.ts | dd9f6f6a5229e6b42f8e6328b5a2e48587d09bbf | Costruisce la richiesta senza tools/include; raccoglie delta testuali, richiede response.completed e restituisce soltanto text |
| packages/local/src/index.ts | commit fissato sopra | Inoltra options al modulo responses dentro il percorso di autenticazione esistente; credenziali e refresh restano interni |

I due blob types/responses letti anche dal ramo upstream corrente coincidono con quelli fissati. Il solo aggiornamento del DevKit, al controllo, non aggiunge gli strumenti. Il confronto è dei due file interessati, non una verifica completa di tutte le versioni SDK.

## Fonti ufficiali consultate
- [Limitazioni Sign in with ChatGPT](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations): la ricerca web dipende da modello/account/policy; store:false e stream:true. max_tool_calls è fra i parametri non ammessi su questa route: non promettere di limitarla con un campo non supportato.
- [Guida web search](https://developers.openai.com/api/docs/guides/tools-web-search): configurazione tools, eventi di ricerca, annotazioni e fonti; l'integrazione richiede citazioni visibili/cliccabili.
- [SDK e uso del piano](https://developers.openai.com/cookbook/articles/sign-in-with-chatgpt): il client usa OAuth e il piano autorizzato, non richiede una chiave API personale; una sessione collegata da sola non prova inferenza o capacità specifiche.
- [Account e limiti](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions) e [linee guida uso piano](https://developers.openai.com/siwc/ui-ux-guidelines): richieste idonee usano piano o saldo crediti; limiti gestiti dalle impostazioni ChatGPT. Questi documenti non dimostrano inclusione/costo della ricerca web per l'account specifico di Alberto.

Non trasferire la tariffazione dell'API Platform a consumo alla route SIWC senza evidenza specifica, né promettere uso gratuito illimitato. Non sono stati consultati dati account, acquistati crediti o eseguite richieste live.

## Prova isolata Windows
tools/probe_siwc_web_contract.mjs, source 0af4305227145f777de4aabc8a5869fc214fa33a, collegato al workflow GPT smoke già esistente. Il runner installa/compila il DevKit fissato come già previsto; il probe controlla i blob sorgenti prima dell'adattamento, importa il modulo SDK vero e intercetta integralmente fetch.
Baseline: opzioni web aggiunte alla chiamata non vengono inoltrate e le fonti non tornano al chiamante. Candidato di prova: modulo temporaneo accanto all'originale, senza sovrascriverlo, che inoltra solo web_search quando richiesto e conserva fonti deduplicate dal completamento. Mantiene il client e i controlli SDK esistenti, inclusi store/stream, errori, completamento e cancellazione.
Trasporto simulato, token fittizio, nessun login o inferenza live. Non sono fonti trovate online: sono fixture controllate. Qualunque destinazione di rete inattesa fa fallire il probe; niente fallback. Il candidato viene eliminato in finally, senza modificare i file originali. La guard richiede Windows, GITHUB_ACTIONS e --ci-only.

Criteri: limite upstream osservato; tools/include inoltrati; fonti duplicate consolidate; richieste normali prive di strumenti/fonti; risposta senza ricerca non dichiarata ricerca; URL non adatti rifiutati; rifiuto del server, stream incompleto e cancel mantengono l'errore. [SDK smoke 41346741167](https://github.com/MATRIXNEO23/jarvis/actions/runs/41346741167) SUCCESS, job 124968075832: 8 controlli PASS. [Suite 41346741184](https://github.com/MATRIXNEO23/jarvis/actions/runs/41346741184) SUCCESS: 455 test per job Windows Python 3.11/3.12; sintassi/probe/Windows Search live PASS, build/ZIP/publisher skipped. [Evidenza completa](evidence/siwc-web-contract-20261101.json).

## Alternative e scelta
| Opzione | Esito |
|---|---|
| Aggiungere «cerca online» al prompt | Insufficiente: non abilita il tool nel payload |
| Passare tools al DevKit invariato | Scartata dalla lettura del payload; verificata nella baseline della prova |
| Aggiornare soltanto il DevKit | I due file interessati sono ancora identici al pin al momento del controllo |
| Estendere soltanto trasporto/parser esistenti | Candidato minimo verificabile nella prova; non ancora adattamento distribuito |
| Avviare ora un browser/estensione/servizio parallelo | Non necessario per provare il tool ospitato; progetto browser completo resta distinto |

## Ripresa precisa
1. Acquisire i risultati CI del probe e della suite e conservarli.
2. Prima dell'attivazione operativa, verificare per l'account/modello scelti sia il supporto reale sia che l'uso rispetti il vincolo piano incluso senza acquisti/credito extra. La prova simulata non lo dimostra.
3. Se queste condizioni sono soddisfatte, preparare l'estensione minima del SDK con sorgenti/versione/ripristino conservativi e integrarla soltanto nel raffinamento file richiesto; mantenere percorso normale senza web.
4. Trasportare fonti strutturate fino alla chat con link verificabili; pagine/fonti sono dati e non autorizzano nuove azioni. La proposta resta soggetta al controllo di stesso obiettivo/scope/tipo e alla verifica del percorso locale. Non rimuovere oggi la frase «web non disponibile» dal prompt attuale.
5. Verificare installazione/aggiornamento, fonti vere, rifiuto tool, quota, timeout e revoca sul percorso completo. Nessuna build automatica e nessuna nuova add-on dichiarata consegnata per il solo probe.

Il passo corrente chiude una prova del contratto SDK. Non abilita una ricerca reale, non prova il microfono/account personale, non misura RAM sul Pavilion e non sostituisce la prova di un pacchetto estratto.
