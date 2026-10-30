# Jarvis — risposte vocali offline e attivazione con «Ehi Jarvis»

Questa funzionalità è **sperimentale**: il codice e i test automatici non sostituiscono una prova sul Pavilion. Non altera la versione vocale precedentemente verificata.

## Risposta vocale, senza costi

Jarvis usa **Windows SAPI / System.Speech** tramite Windows PowerShell già presente su Windows 10. Non richiede chiavi API, servizi a consumo o nuovi modelli linguistici. Le risposte vocali sono **spente per impostazione predefinita** e possono essere attivate separatamente dal microfono.

Nella finestra di Jarvis:
1. Cerca la sezione **Risposte vocali offline — voci di Windows**.
2. Clicca **Aggiorna voci** per ottenere le voci locali effettivamente installate.
3. Seleziona la voce nell'elenco (oppure **Predefinita di Windows**).
4. Clicca **Prova voce** per ascoltare un esempio senza avviare il microfono.
5. Attiva **Jarvis risponde a voce** per fargli leggere i risultati dei comandi locali completati e le risposte GPT. Le preferenze vengono salvate senza modificare l'opzione GPT.

Le voci installate variano a seconda dell'installazione Windows; una voce maschile profonda o italiana **non è garantita**. Non è implementata la clonazione della voce dell'attore cinematografico. Se Windows non espone alcuna voce SAPI, Jarvis rimane utilizzabile in modalità testuale.

La risposta vocale legge fino a 600 caratteri per messaggio, senza rallentare l'interfaccia durante la riproduzione. Il processo di sintesi riceve il testo come JSON sullo standard input, non come comando. Le voci sono locali; nessun testo viene inviato a un servizio TTS online.

## «Ehi Jarvis» in ascolto continuo

Il microfono parte **sempre in standby**. Se l'utente seleziona manualmente **Ascolto continuo**, Jarvis mantiene attiva quella modalità anche quando altre applicazioni sono pesanti.

Nell'ascolto continuo:
- Un comando come «Apri Blocco note» **senza chiamare Jarvis** non viene eseguito.
- «**Ehi Jarvis, apri Blocco note**» viene interpretato come comando.
- «**Ehi Jarvis**» da solo arma **un solo comando successivo**, per 10 secondi; il timeout **non cambia lo stato del microfono**.
- Una frase dopo il comando viene ignorata finché non si chiama nuovamente Jarvis.
- In **Premi per parlare** restano validi i comandi senza nome, dato che il pulsante richiede già un'azione manuale.
- In **Dettatura attivata manualmente**, il parlato ordinario rimane testo. «Ehi Jarvis, disattiva dettatura» resta un comando esplicito.

Durante la riproduzione della propria voce Jarvis ignora l'audio captato dal microfono, per evitare che si risponda da solo. **Non spegne il microfono e non cambia modalità**. Per brevi istanti non accetta nuovi comandi mentre sta parlando.

## Prove necessarie sul Pavilion

Dopo un CI completamente verde, provare: elenco delle voci; prova vocale; interruttore e salvataggio; avvio con microfono spento; ascolto continuo con frase senza nome (non deve eseguire); «Ehi Jarvis» seguito da comando; apertura browser; ricerca; dettatura e suo arresto; soppressione dell'eco quando Jarvis risponde; cambio modalità solo manuale; funzionamento con Minecraft aperto.

Non reinstallare Vosk se è già installato e funzionante. Il browser e la ricerca web possono richiedere Internet, ma il riconoscimento e la sintesi vocale sono locali.
