# Quota Codex — esito della prova di fattibilità, 3 novembre2026

**Stato:** confine di lettura e protocollo verificati su Windows,quota personale non letta. Il gate di autenticazione reale non è superato; nessuna barra/add-on installabile o nuova build.
**Sorgenti:** [897b95b98fba166957cb17c4ebcd911969925d0f](https://github.com/MATRIXNEO23/jarvis/tree/897b95b98fba166957cb17c4ebcd911969925d0f),ramo feature/codex-quota-20261103.
**Run finale:** [41728307013](https://github.com/MATRIXNEO23/jarvis/actions/runs/41728307013),SUCCESS.
**Progetto:** [barra quota](BARRA-QUOTA-CODEX-20261103.md);[piano](superpowers/plans/2026-11-03-barra-quota-codex.md).

## Fatti dimostrati
- SDK Sign in with ChatGPT fissato della004 e main upstream coincidono a0a36fefeb913055c8c7a1a29b63d82b96b2e841a. Interfaccia pubblica senza lettura quote;streamResponse restituisce testo,non quota.
- Codex ufficiale documenta account/rateLimits/read. Sorgente app-server account_processor.rs a3abe09d017c0f68df363bcbd19d49fa0278c3588 richiede autenticazione per backendCodex; un provider inferenzaResponses è un’altra configurazione.
- BinarioWindows x64 ufficiale rust-v0.166.0 scaricato soltanto nel runner:ZIP92228613byte, SHA256edbdd3d5c74ea5437eb13254131de56d855a95a6bc18c139ecce7e95338e4d63. Hash e dimensioni verificati prima dell’esecuzione.
- Initialize e lettura stato/quota eseguiti realmente suWindows2022 con archivio credenziali inRAM,sia senza account sia con provider della formaSiwC e valore fittizio destinato al serverloopback.
- In entrambi i casi account/rateLimits/read restituisce autenticazione richiesta. Il providerJarvis traduce l’esito in QuotaUnavailable,non0% o100%.
- Metodi inviati:initialize,account/read,account/rateLimits/read. Nessun thread/start,turn/start,streamResponse,login,riscatto o acquisto. TrappolaHTTPloopback:0richieste. Non sono state usate o lette credenziali personali.
- Il provider non avvia processi o rete finché non riceve un trasporto esplicitamente collegato. Accetta soltanto laRPC quota,timeout≤10s,nessun retry;errori tecnici/credenziali non esposti. Zero turni generati per il controllo.

## Prove e correzione
| Prova | Risultato |
| --- | --- |
| Red source3293a8b/run41727385004 | Due job falliti;log126235625936:7test,1fallimento/6errori sul provider placeholder,nessun import mancante |
| Primo Green source238f9c5/run41727784400 | 7test per Python3.11/3.12 e probe realeWindows PASS |
| Ricontrollo finale source897b95b/run41728307013 | 9test per Python3.11/job126238767708 (0.175s),9 perPython3.12/job126238767242 (0.208s),zero fallimenti/errori/skip |
| Probe finale job126238910473 | PASS,no-auth e formaSiwC rifiutati,0turni e0richieste loopback |

Nel ricontrollo statico individuata la possibilità che notifiche estranee prolungassero il ciclo di lettura: aggiunto controllo del termine a ogni iterazione e conversione queue.Empty→TimeoutError. Due prove dedicate verificano il lettore reale con clock/coda controllati,senza sleep; incluse nei9test finali. Il Red iniziale riguarda i primi7,non attribuire un cicloRed separato alle ultime2prove.

## Peso osservato e limiti
| Voce | Misura |
| --- | --- |
| Download aggiuntivo della soluzione app-server provata | 92.23MB decimali compressi |
| Solo eseguibile su disco | 283894064byte,circa283.9MB decimali |
| WorkingSet processo senza auth | 35020800byte,circa35.0MB decimali |
| WorkingSet formaSiwC fittizia | 34263040byte,circa34.3MB decimali |
| Memoria privata rispettiva | 14950400 e14667776byte |
| Tempo processo→fineletture rispettivo | 1.172s e0.047s nel runner |

Sono campioni puntuali di un processo non autenticato suWindowsServer2022,non picchi,misure residenti/di inferenza,confrontoJarvisOFF/ON o prestazioni del Pavilion/Windows10. Secondo avvio può beneficiare della cache; nessuna promessa di quei tempi sul discoHDD dell’utente.
Nessun binario aggiunto alla004 o al pacchettoJarvis. Codice nuovo limitato a codex_quota/provider.py,LEGGIMI,probe/test e workflow dedicato; nessunHUD,manifestinstallabile,backendconversazione o credenziale modificati.

## Cosa questa prova non dimostra
Nessuna quota personale autentica ottenuta. Il probe con formaSiwC usa un valore fittizio e non prova che un tokenSiwC autentico venga respinto da un endpoint remoto; dimostra che configurare soltanto il providerResponses non crea la sessione accountCodex richiesta. Non usare questo esito come prova assoluta d’impossibilità di ogni integrazione futura.
Non è stata eseguita alcuna richiestaOAuth,lettura dei fileaccount personali,login o inferenza a pagamento. La compatibilità delle credenziali attuali con i serviziquota non è stata verificata e il SDK non espone tale metodo.

## Scelta concreta prima del passo successivo
La strada ufficiale provata richiede un componenteCodex e una sessioneCodex esplicitamente collegata; l’account della conversazioneJarvis resta separato. Prima riusare un’eventuale installazione compatibile già scelta dall’utente; altrimenti il componente supplementare avrebbe il peso sopra misurato. Accesso via browser richiesto soltanto da un gesto esplicito,nessun login automatico durante refresh. Nessun nuovo piano/acquisto è parte della proposta; le letture non inviano turni al modello.
Un’alternativa più semplice è un controllo che apre la pagina ufficialeUso,senza percentuale automatica nelHUD. Il dettaglio del perimetro visibile dalla pagina dipende dal servizio/account.
Occorre ora decidere se accettare componente e collegamentoCodex dedicati per proseguire con lettura personale; non installarli sulla macchina dell’utente o rimpiazzare il motore per ottenere una barra. Dopo quella scelta e una rispostaquota reale,procedere agli altri task. Nessuna005 autorizzata.

## Evidenze e fonti
[evidenza strutturata](evidence/quota-feasibility-20261103.json).
Fonti: https://learn.chatgpt.com/docs/app-server ; https://developers.openai.com/siwc/token-sharing-open-source/codex-app-server ; openai/codex account_processor.rs e tests/suite/v2/rate_limits.rs (revisioni sopra); openai/sign-in-with-chatgpt-devkit packages/local/src/types.ts e index.ts (revisione fissata).
