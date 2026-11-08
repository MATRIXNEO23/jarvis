# Dialogo Gemma: contesto recente protetto e budget reale
Data ricerca:8 novembre2026. Stato: proposta sottoposta a revisione, NON implementata. Baseline ispezionata091e73cc2a7939a1145a2e7d5666512e3ac15c07; pacchetto010 resta immutabile.

## Obiettivo e vincoli
Mantenere riferimenti e argomento del dialogo quando la cronologia cresce, evitando che un solo scambio lungo azzeri la storia inviata. PC i3-2100 AVX/10GB/Windows10, Gemma2 2B IT Q4_K_M via DLL KoboldCpp fissata. Zero servizi/API a consumo, nessun modello aggiuntivo, nessun cambiamento automatico del contesto1024/2048 o del max output. Questa fase produce ricerca/spec/piano, non autorizza una nuova build o nuove scritture di conversazioni.
Riscontri utente:009 risponde discretamente su scambi brevi; il riferimento a una parola usata dalla precedente risposta lunga si perde; dopo riapertura la continuità è insufficiente. Non dimostrano da soli che ogni errore sia memoria o che la qualità del modello sia risolta.

## As-is verificato nel repository
1. native_conversation_session.prepare_turn misura len(format_gemma_messages(...)), cioè caratteri. MemoryPreferences.available_prompt_tokens limita quel numero con valori derivati da token. Il limite600 predefinito non corrisponde a600 token effettivamente usati.
2. Inserisce istruzioni/catalogo prima della storia. Per le coppie in ordine recente, se una non entra esegue break: può restare zero storia. Sostituire semplicemente break con continue terrebbe eventualmente scambi vecchi perdendo proprio quello cui l'utente si riferisce.
3. Il messaggio «Contesto insufficiente per interpretare azioni» nasce quando il catalogo non entra; non misura il numero di scambi inviati e non significa «memoria vuota».
4. SecondBrain conserva user320/reply350 caratteri e reinserisce recenti ancora più corti; non è un riassunto. RAM:16 scambi globali, risposta limitata a2000 caratteri. Tagli su disco, selezione RAM, archivio e prompt effettivo sono fenomeni distinti.
5. Upstream koboldcpp.py al pin7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759, blob7805cd49cd1f7a8f0101aba52721af7a771067af: tokenize_ids(countprompt,tcaddspecial) usa handle.token_count con lock e copia ID. È disponibile una base nativa per il conteggio senza generare testo. Integrazione nel lifecycle Jarvis e latenza reale non provate.
6. Gemma2/3 IT usa user/model e delimitatori di turno, istruzioni nel primo user; non copiare genericamente un turno system da esempi di altre librerie.

## Ricerca: fonti primarie e applicazione limitata
- Google Gemma prompt structure: https://ai.google.dev/gemma/docs/core/prompt-structure — ruoli e delimitatori. Applicabile a Gemma2 IT; non confondere col formato Gemma4.
- HuggingFace chat templates: https://huggingface.co/docs/transformers/main/chat_templating — formattare prima della tokenizzazione, evitare duplicazione BOS/EOS. Principio utile, non proposta di installare Transformers.
- LangChain trim_messages: https://reference.langchain.com/python/langchain-core/messages/utils/trim_messages — taglio per budget, messaggi recenti, coerenza dei ruoli e opzione parziale. La politica last con coppie indivisibili può comunque lasciare soltanto l'ultima domanda: non adottare il default come soluzione automatica al nostro caso.
- Anthropic context engineering: https://www.anthropic.com/research/effective-context-engineering-for-ai-agents — selezione, note e compattazione sono strumenti differenti; comprimere aggressivamente perde dettagli. Principi, non chiamate al servizio o soglie copiate.
- Anthropic compaction threshold: https://platform.claude.com/docs/en/build-with-claude/compaction-threshold — esempio che protegge scambio precedente e domanda attuale. Le API e le soglie di modelli enormi non si applicano a Gemma2 locale.
- Lost in the Middle, autori: https://arxiv.org/abs/2307.03172 — posizione/rilevanza contano; un contesto più grande non garantisce uso migliore. Non è un benchmark di Gemma2 sul Pavilion.
- LongMemEval, autori: https://arxiv.org/abs/2410.10813 — separa recupero, lettura, aggiornamenti temporali e astensione; ispira casi di test, non richiede integrare il framework.
- HF cache explanation: https://huggingface.co/docs/transformers/main/cache_explanation — contesto maggiore ha costi di memoria/elaborazione; comportamento preciso del backend fissato da misurare.
- Issue39261 nel repo LangChain: https://github.com/langchain-ai/langchain/issues/39261 — segnalazione riproducibile di perdita storia con finestra senza messaggio umano, chiusa not planned; indizio di classe di errore, non prova eseguita da noi né giudizio generale sulla libreria.

## Opzioni considerate
| Opzione | Beneficio | Costo/limite | Scelta proposta |
| --- | --- | --- | --- |
| A: conteggio nativo, scambi recenti protetti, espulsione vecchi | Affronta i difetti verificati senza altra inferenza | Più storia realmente utilizzata può rallentare la risposta; integrazione tokenizer da provare | Prima milestone |
| B: estratto locale dell'ultimo scambio sovradimensionato | Conserva riferimenti senza generazione aggiuntiva | Selezione lessicale non comprende tutta la semantica; omissioni esplicite | Fallback di A |
| C: riassunto generativo ricorrente | Può sintetizzare relazioni più ricche | Un'altra generazione, contesa CPU, possibili distorsioni | Rimandato, opzionale dopo misure |
| Nuovo modello/embedding/framework/contesto aumentato automaticamente | Non necessario per dimostrare la correzione | RAM/dipendenze e rischio allargamento | Escluso da questa fase |

## Politica proposta prima di ogni invio
Il motore costruisce una vista della cronologia; rimuovere un turno da quella vista non cancella l'originale conservato. Non promettere conservazione integrale oltre i limiti oggi esistenti.
Budget effettivo: token(prompt completo) + max_output + margine <= context_size scelto. Il prompt completo include istruzioni, catalogo, dati archivio, delimitatori e prefisso di generazione. Contare con gli stessi flag special/BOS del backend; confronto reale prima di attivarlo. Non fare una generazione per contare.
Priorità: domanda attuale e istruzioni essenziali; ultimo scambio pertinente al seguito; altri scambi recenti; ricordi più lontani solo se pertinenti e c'è spazio. Non eliminare controlli/permessi per far entrare storia. Se descrizioni opzionali del catalogo vanno ridotte, invalidare coerentemente l'interpretazione azioni non descritta; i comandi diretti locali restano separati. Prima versione può lasciare il catalogo invariato e guadagnare spazio correggendo unità e selezione.
Se manca spazio, espellere prima le coppie più vecchie. Inserire la coppia recente protetta prima di tentare le altre: non lasciarla come ultima cosa a cui destinare gli avanzi.
Se la coppia protetta da sola non entra: ricavare estratti dei suoi testi originali, mantenendo domanda/risposta e ordine. Preferire la frase citata dalla nuova domanda con frasi vicine, il tema della domanda precedente e inizio/fine utili. Non una semplice coda di testo arbitraria. Etichettare estratto/omissioni; non inventare fatti né trasformare parole di Gemma in opinioni dell'utente o verità verificate. Ricontare il risultato finale.
Se non c'è un termine di richiamo chiaro: un estratto può mantenere il tema, ma non garantisce il referente; il modello deve poter chiedere chiarimento. Nessun falso «riassunto completo».
Se persino domanda e base obbligatoria non entrano: errore specifico sulla richiesta attuale prima di generare; non troncare silenziosamente la domanda o aumentare RAM. Se restano zero token per qualunque prova storica, dichiarare la limitazione reale: non promettere un riferimento impossibile.
Formato sempre user/model valido, nessun assistant orfano. Le citazioni archiviate restano dati e non autorizzano azioni. Epoch, stop, modello selezionato, contesti progetto e Telegram invariati.

## Esempio di accettazione
L'utente chiede una spiegazione storica; Gemma produce risposta lunga contenente la parola X; domanda successiva «perché X?». La vista deve contenere la domanda originaria e il passaggio di Gemma con X (o segnalare che non è disponibile). Non imporre a Gemma di approvare o ripetere errori storici.
Niente sostituzione con un vecchio argomento solo perché il turno vecchio è più corto.

## Avvisi coerenti, senza spam
- Storia ridotta ma presente: «Cronologia alleggerita: conservati gli scambi più recenti».
- Estratto dell'ultima risposta: indicazione discreta/diagnostica che è stato usato un estratto.
- Catalogo non disponibile: stato specifico dell'interpretazione comandi, distinto dalla conversazione, solo quando cambia.
- Storia realmente assente: dichiararlo soltanto quando lo è.
Nel pannello diagnostico esistente: conteggio input/output riservato, scambi interi/estratti/omessi e motivo, senza nuovi log persistenti di dati sensibili. Le metriche aiutano anche a distinguere un errore di recupero da un errore di Gemma.

## Due milestone, entrambe da approvare prima del runtime
M1 — budget e continuità nella sessione: native_bridge/provider/adapter/session e test esistenti. Riutilizzare DLL e tokenizer; preflight validazione senza side effect inutili, conteggio quando il modello è caricato, lock/lifecycle unici. Cache solo conteggi di input immutabili con limite; controllo finale dell'intero prompt. Nessun secondo modello/load, chiamata online o riassunto automatico. Migrazione esplicita delle vecchie impostazioni: non reinterpretare silenziosamente600 caratteri come600 token; chiarire unità nel pannello e preservare profilo/rollback. Prima patch correggere dropout e conteggio, niente archivio nuovo.
M2 — continuità dopo riavvio: SecondBrain/workspace e reader. Separata da M1: definire retention e dimensioni per originali recenti prima di salvare più dati, rispettando Memoria on/off, filtri/cancellazione e isolamento. Recupero recente prima di ricordi vecchi correlati per un seguito breve. Una porzione già perduta nel record troncato non si ricostruisce da quel record. Nessuna nuova persistenza completa per implicazione.
Riassunto con modello: solo eventuale M3 dopo confronto sul PC; gate idle già presente da riusare, proteggere conversazione e abort, salvataggio atomico e conservazione originali, mai cancellare storia se il riassunto fallisce.

## Requisiti e prove
| ID | Contratto | Verifica prevista |
| --- | --- | --- |
| R1 | Budget token completo e riserva risposta | Tokenizer nativo, Unicode/italiano/separatori/BOS; confronto con backend e nessun reload |
| R2 | Non azzerare storia per una risposta lunga | Caso X, molte coppie brevi, ultimo turno sovradimensionato, argomenti alternati; ispezione input reale |
| R3 | Ruoli/attribuzioni e autorizzazioni invariati | Gemma user/model validi, citazioni/errori modello come dati, JSON azioni/permessi e Telegram isolati |
| R4 | Nessuna inferenza supplementare nel percorso A/B | Contatore invocazioni e lock/stop/concorrenza; nessuna seconda generazione |
| R5 | UI distingue taglio, assenza e catalogo | Avviso corretto, nessun messaggio di memoria vuota con scambi effettivamente allegati |
| R6 | Persistenza controllata in M2 | Riavvio, on/off, cancellazione, retention e dimensioni limitate, progetti separati |
Baseline:010 pubblicata;966 test sul sorgente e ZIP estratto. Nessuno di quei test prova questa proposta non implementata. Nuove regressioni Red prima della patch, Windows3.11/3.12 e revisione prima di una futura build richiesta.
PC: confrontare stesse impostazioni/modello e stessi dialoghi, tempi tokenizer/prefill/generazione, RAM e qualità dei riferimenti. Latenza/RAM aggiuntive NON MISURATE. Zero generazioni supplementari non significa tempo totale invariato: usare più token può richiedere più elaborazione.
Rollback: feature/policy precedente selezionabile durante collaudo, versioni010/009 intatte e dati non sovrascritti; nuova build solo con richiesta separata.

## Decisioni tecniche dopo revisione della proposta
Revisione indipendente del design c7a2994: nessuna contraddizione dimostrata, quattro contratti da precisare. Le seguenti sono scelte proposte dal progettista, non preferenze già approvate dall'utente.

D1 — limiti e migrazione: C=context_size scelto, O=max_output scelto, R=margine128 token già usato numericamente oggi; B=C-O-R. Tutto il prompt formattato deve stare in B. Dopo base obbligatoria e domanda attuale, storia/ricordi ricevono al massimo H=min(S, spazio residuo effettivo), con S nuovo budget della storia in token, proposta iniziale600. S non autorizza mai a superare B e non limita/tronca la domanda attuale; se la sola base+domanda supera B, richiesta respinta con spiegazione precisa. La domanda non viene silenziosamente tagliata.
Il vecchio prompt_max_tokens non deve essere rietichettato e reinterpretato di nascosto: mantenere il valore legacy per rollback; introdurre una versione di impostazioni leggibile insieme al vecchio schema e mostrare il nuovo budget600 token chiaramente. Attivare la nuova politica solo nella candidata approvata, con nota di migrazione e possibilità di mantenere la010. Il valore600 è una proposta iniziale da verificare, non un benchmark ottimale. Gli override storici e il profilo non vengono cancellati/reset. C e O non cambiano automaticamente. La prova R1 include esplicitamente migrazione da schema precedente.

D2 — scambio protetto: M1 protegge per default la coppia completa immediatamente precedente nello STESSO contesto, anche se i temi cambiano. La parola «pertinente» non autorizza a sostituirla scegliendo arbitrariamente un turno più vecchio e corto. Un riferimento più vecchio può essere aggiunto come prova secondaria quando c'è spazio; sostituire la coppia protetta richiede un riferimento esplicito e non ambiguo al turno (citazione/identificativo verificabile), non il solo punteggio lessicale. Se ambiguo, non cambiare referente in silenzio. M2 specificherà il recupero tra sessioni; non blocca il primo rimedio nella sessione attuale.

D3 — estrazione limitata: non più di una coppia viene trasformata nel fallback M1. Dopo aver riservato etichette/separatori, assegnare inizialmente circa25% del contenuto alla vecchia domanda (tetto64 token), il resto alla risposta; spazio non usato torna alla risposta. Conservare almeno testo non vuoto con parole complete di entrambi, senza riempire artificialmente frammenti brevi. Includere prima l'eventuale citazione esatta presente nella nuova domanda, poi frasi con termini non banali in comune, poi elementi di inizio/fine; massimo5 frasi candidate con contesto vicino e ordine originale. Se ci sono più corrispondenze, mantenere la più recente nello stesso turno e non inventare una disambiguazione.
Dimensionare su testi disponibili e limiti di input esistenti, non scansioni illimitate. Tokenizzare/ricontare il prompt intero dopo assemblaggio, perché i conteggi di pezzi non sono una prova additiva esatta. Riduzioni iterative con target decrescente (dimezzamento), massimo12 tentativi: evitare cicli senza limite. Se un frammento minimo con riferimento non entra, allegare solo ciò che entra e dichiarare la limitazione reale; non dire «riferimento conservato» se la citazione è stata omessa. Se i delimitatori e due frammenti non vuoti non entrano, storia esclusa per spazio effettivamente insufficiente, non per il break su una coppia grande. Il modello non deve fingere di avere un antecedente mancante.
Queste allocazioni/limiti sono parametri di implementazione proposti e testabili, non garanzie semantiche. Il risultato è un estratto, mai etichettato come riassunto esaustivo. La storia originale rimane nel suo archivio nei limiti già esistenti; M1 non amplia la persistenza.

D4 — disponibilità tokenizer: prima una prova tecnica sul provider/pin reale. Il conteggio avviene sul worker, usando lo stesso provider/modello già caricato per la richiesta; alla prima richiesta valida il caricamento ordinario può essere necessario, ma non viene creato un secondo owner né eseguita una seconda generazione. Validazioni rapide dei tipi, controlli e dimensioni assolute precedono ogni load. Prima di attivare M1 verificare simboli/flag special/BOS e concordanza con input del backend; mismatch blocca l'attivazione della nuova politica.
Una volta attiva, errore del contatore non porta a un invio con budget dichiarato esatto ma solo stimato: interrompere quella richiesta con errore diagnostico e lasciare la010/politica precedente come rollback esplicito. La modalità legacy non viene presentata come conteggio esatto. Caricamento/contatore devono partecipare agli stessi controlli revision/stop/lock; nessuna chiamata DLL sul thread UI e nessun riavvio del modello sopra un'inferenza ancora attiva. Questa fattibilità resta da provare su Windows e modello reale prima del codice operativo.

## Stato conclusivo della ricerca
Ricerca e proposta completate; nessuna prova nuova di runtime/qualità/prestazioni eseguita e nessuna build creata per questa fase. Decisioni D1-D4 da recepire nel piano soltanto dopo approvazione della proposta. Non presentare questi dettagli come comportamento della010 già installabile.

Revisione finale indipendente sulla versione7f4fa101: D1-D4 sufficienti per pianificare M1, nessuna contraddizione concreta; fattibilità tokenizer reale resta primo gate. Nessun test o modifica eseguito dal revisore. Conferma utente ancora da ottenere prima del runtime.
