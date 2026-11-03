# Prompt e consumi Jarvis — controllo senza modificare i prompt

Richiesta: controllare approfonditamente che cosa si può ridurre, senza snellire ancora. Analizzati i sorgenti della 004 e la correzione voce in `fix/gpt-voice-addressing-20261103`. **Nessuna modifica ai prompt, alla memoria, al modello o al SDK. Nessuna inferenza durante l’audit.**

## Esito

Il primo spreco dimostrato è il numero di richieste ambientali involontarie. La seconda opportunità è il testo fisso: anche una domanda di nove lettere porta migliaia di caratteri di istruzioni e catalogo. C’è spazio per ridurre il testo, ma non è corretto promettere una percentuale di quota recuperata.

La memoria è già limitata: non viene allegato tutto l’archivio e non esiste un riassunto periodico fatto dal modello. Ridurla indiscriminatamente rischia di peggiorare la continuità e provocare più chiarimenti. Con catalogo attivo e richiesta lunga, un caso misurato perde già tutta la memoria del prompt.

## Metodo ed evidenza

[Misura Windows 41733308539](https://github.com/MATRIXNEO23/jarvis/actions/runs/41733308539), source `a91aff9ef2013fd3fae0e9e87c41fa80843f7783`, Python 3.12.10: costruttori reali, manifest delle due add-on distribuite, memoria sintetica, zero accessi a microfono, profilo, credenziali o modello. Procedura ripetibile in `.github/workflows/prompt-audit.yml`; risultati in `docs/evidence/prompt-payload-audit-20261103.json`.

L’unità è la lunghezza UTF-16 usata dal bridge. **Non sono token del modello, usage fatturato o quota personale.** Non abbiamo log dell’episodio, modello effettivo o metriche usage dell’account. Il bridge/SDK restituisce testo e nome modello, non propaga contatori di token. Nessuna conversione arbitraria caratteri/4 o quota in percentuale.

## Che cosa parte quando si parla

1. Vosk e correzioni approvate lavorano localmente. Il nuovo richiamo controlla il grezzo prima di correzioni, log, gestori o coda. Nessun modello per riconoscere «Jarvis».
2. Programmi consentiti, timer, diagnostica locale, file riconosciuti e dialoghi locali hanno precedenza. Quando bastano, nessun prompt parte.
3. Il resto entra in `start_conversation_gpt` → `build_conversation_prompt` → `run_gpt` → `GPTClient.call("ask")` → bridge `sdk.streamResponse`. Una normale conversazione usa il modello anche se non esegue operazioni sul PC.
4. Una chiamata riceve un unico prompt ricostruito: identità/stile, regole del router, catalogo consentito, stato runtime, add-on, memoria compatta e frase corrente. Non viene passato un identificatore di conversazione remota; la continuità si riporta nel testo locale.
5. Il SDK fissato converte la stringa in un messaggio `user` e usa `store:false`. Il bridge non invia `instructions`, strumenti o un secondo elenco di messaggi. Non emerge dal codice un secondo invio automatico identico per ogni frase.

Sorgenti principali: `jarvis.py` (`recent_memory_for_gpt`, `start_conversation_gpt`, `run_gpt`, `start_file_refinement`); `conversation_router.py`; `jarvis_persona.py`; `conversation_memory.py`; `workspace_memory.py`; `second_brain.py`; `live_capabilities.py`; `capability_registry.py`; `gpt_client.py`; `gpt_bridge.mjs`.

## Misure dei prompt effettivamente costruiti

| Scenario sintetico | Unità UTF-16 |
| --- | ---: |
| «come stai», senza contesto/stato (riferimento minimo del builder) | 3.336 |
| Stessa frase, stato runtime, memoria vuota del percorso normale | 3.815 |
| Stato runtime e tre scambi recenti, senza add-on | 4.077 |
| Add-on programmi e tre scambi recenti | 4.595 |
| Programmi + file e tre scambi recenti | 4.913 |
| Richiesta lunga, memoria ampia e due add-on | 4.849; memoria esclusa |
| Raffinamento ricerca file, due add-on e memoria | 3.807 |
| Spiegazione di estratto file di 1.800 caratteri | 1.952 |
| Telegram, messaggio breve senza/con 1.000 caratteri di contesto | 1.164 / 2.164 |

Nel caso da 4.077: identità 952, catalogo core 737, stato con etichetta 253, memoria con intestazione 488, stile 144, frase con etichetta 57, altre regole 1.446. Quindi la sola frase incide poco. Il massimo 5.000 è un limite di testo, non un budget di token o una misura di consumo già avvenuto.

## Opportunità ordinate per prudenza

| Possibile intervento | Evidenza e beneficio | Rischio / prova necessaria |
| --- | --- | --- |
| Saltare il blocco memoria quando è semanticamente vuoto | Nel caso misurato occupa 226 unità; eliminarlo porterebbe 3.815→3.589, circa 5,9% del testo, non della quota | Verificare prima che siano vuoti anche focus, preferenze, risultati e prove; non eliminare memoria salvata |
| Unificare le istruzioni di stile | Identità 952 più guida dinamica 112–172 circa; brevità, italiano, ironia e chiarimenti si sovrappongono | Conservare carattere Jarvis, precisione, contenuti richiesti e casi delicati; confronto di qualità ancora da fare. Non approvato rimuovere la personalità |
| Compattare le regole senza cambiare il contratto delle azioni | Altre regole base 1.446, con sezioni specifiche anche per funzioni non disponibili | Mantenere JSON, campi, limiti, conferme, intenzione attuale e separazione dati/permessi. Non cancellare i controlli locali |
| Ridurre doppie descrizioni di capacità/add-on | Con la sola app lo stato include una descrizione e segue anche catalogo/grammatica. Stato app 415 contro 253 senza descrizione | Verificare che il modello sappia ancora che cosa può fare; quando lo stato completo supera 850 il codice elimina già le descrizioni add-on, quindi il risparmio non si somma in tutti i casi |
| Deduplicare gli scambi di progetto prima della compattazione | `earlier + short` combina archivio e RAM senza deduplica. Caso sintetico senza add-on: 6 record, 3 unici arrivano nel prompt | Conservare cronologia e veri scambi ripetuti; non promettere meno caratteri quando lo spazio liberato viene usato per altro contesto utile |
| Valutare un percorso chat più piccolo solo quando la scelta locale è certa | Il builder chat puro costruisce 2.268 unità nella prova breve, contro 3.815 del router con memoria vuota | NON sostituire automaticamente il router per frasi ambigue: perderebbe capacità operative e potrebbe ripresentare i vecchi falsi «non posso». Nessun secondo classificatore GPT per scegliere il percorso |

Per stile/regole/catalogo non è ancora misurato un risparmio ottenibile mantenendo la qualità: servono una proposta concreta e prove mirate, non una percentuale inventata. Non sommare i massimi dei vari casi: catalogo e memoria competono per lo stesso limite.

## Memoria: limiti e possibili duplicati

`ConversationMemory` conserva al massimo 8 scambi in RAM; il richiamo usa un budget di 860 caratteri. La ricerca nella memoria persistente usa 530; il progetto combina recenti, avanzamento e riassunto controllati. `compact_memory` porta il contesto finale fino a 850 unità circa, ulteriormente ridotte se non c’è spazio; preferisce domanda corrente/progetto e ultimi scambi. Non è una cronologia remota che cresce senza limite.

La duplicazione progetto è possibile perché ogni scambio viene salvato e mantenuto anche in RAM. La misura con contesto di progetto e catalogo pieno contiene invece solo due record unici: la pressione sul limite nasconde il duplicato. In una richiesta lunga con catalogo, il blocco memoria viene omesso completamente. Priorità: liberare istruzioni ridondanti, prima di tagliare ancora il contesto utile.

## Numero di chiamate: non confonderlo con la lunghezza

| Percorso | Inferenze dal codice |
| --- | --- |
| Parlato senza richiamo nel normale MIC, dopo correzione | 0 |
| Comando locale risolto | 0 |
| Chat o interpretazione richiesta non locale | Normalmente 1 |
| Ricerca locale senza risultati utili | Può aggiungere 1 raffinamento; un chiarimento esplicito può richiedere un turno ulteriore |
| Azione file prima interpretata dal modello, poi raffinata | Può arrivare a 2; non è un retry identico |
| Spiegazione file richiesta dall’utente | 1 per la spiegazione; eventuale interpretazione precedente è distinta |
| Revisione diagnostica esterna autorizzata | 1; diagnostica locale senza modello |
| Telegram automatico attivo e contatto autorizzato | Può generare risposte indipendenti dal MIC; note già approvate riferite senza modello |
| Stato account/lista modelli | Non sono turni di generazione; eventuale traffico di autenticazione/metadati è distinto |

La coda voce è limitata a tre frasi ma prima poteva essere riempita dal parlato ambientale e riavviarsi continuamente. Adesso accetta solo frasi indirizzate. Il limite della coda non è un tetto di consumo nel tempo. Non emerge un retry automatico nel client Python; il SDK fissato imposta `maxRetries:0` per le risposte. Il raffinamento non si riattiva da solo sul proprio esito negativo, ma una risposta dell’utente al chiarimento è un nuovo turno.

## Risposte, modello e misurazione mancante

Le istruzioni chiedono normalmente 1–3 frasi, ma consentono procedure complete. `MAX_REPLY=2600`, massimo JSON, taglio a 30.000 nel bridge e limite di testo del SDK agiscono dopo o durante la ricezione; **non costituiscono un tetto di generazione comunicato al server**. Tagliare localmente la risposta o pronunciarne meno non recupera token già generati.

Il bridge chiama `streamResponse` solo con `model` e `input`. L’interfaccia del SDK fissato non espone un parametro per massimo output o livello di ragionamento: non basta aggiungere un’impostazione fittizia alla UI. Occorre una verifica separata del contratto supportato prima di proporre un limite reale; nessun componente aggiuntivo approvato qui.

Nei percorsi riletti Jarvis non passa una scelta di modello; il bridge prende il primo disponibile quando manca una scelta valida. Non sappiamo quale fosse nell’episodio: non assumere che sia il più economico o proporre un modello non disponibile nel piano. La risposta restituisce il nome; per attribuire risparmi reali servirebbe una misura autorizzata delle richieste/usage, senza registrare conversazioni o credenziali e senza inferenze di prova automatiche. Non sono implementati contatori, nuova telemetria o cambio modello.

Fonti del SDK ufficiale alla revisione effettivamente fissata, consultate in sola lettura: [responses.ts](https://github.com/openai/sign-in-with-chatgpt-devkit/blob/0a36fefeb913055c8c7a1a29b63d82b96b2e841a/packages/local/src/responses.ts) e [types.ts](https://github.com/openai/sign-in-with-chatgpt-devkit/blob/0a36fefeb913055c8c7a1a29b63d82b96b2e841a/packages/local/src/types.ts). Non si presume che una versione diversa sia già installata o compatibile.

## Prossimo passo consigliato

Terminare prima la protezione dal parlato ambientale. Per una futura riduzione autorizzata dei prompt: cominciare dal blocco memoria realmente vuoto e dalle ripetizioni di stile, poi compattare le regole preservando il contratto e verificando qualità/continuità/azioni su Windows. Nessuna promessa di risparmio percentuale sulla quota. Non cancellare ricordi, non introdurre classificatori online, login dedicati, acquisti o App Server per questa ottimizzazione.
