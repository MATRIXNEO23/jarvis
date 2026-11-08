# Continuità Gemma — M1 e M2 completate

Autorizzazione: «Fai entrambi prima uno poi l'altro», seguita da «Continua». Eseguita M1 prima di M2. Sorgente verificato: a81bf4f2541cf6d8f3ca4f0c78ebc0b0ae031f91. Ramo fix/model-selection-session-20261108, PR57 draft. Nessun merge, build o nuovo ZIP. La010 pubblicata rimane immutabile.

## Risultato
- M1: prompt completo conteggiato con tokenize_ids(prompt,True) della DLL già usata per generare; budget C-max_output-128. Ruoli user/model, delimitatori e prefisso di generazione inclusi. Domanda attuale non troncata silenziosamente.
- Ultima coppia dello stesso contesto protetta. Se troppo lunga, estratto locale con citazione/termine richiamato e attribuzione originale, massimo12 riduzioni; altre coppie vecchie intere soltanto se entrano. Storia/ricordi insieme al massimo600 token aggiunti alla base, entro il budget fisico. Nessuna generazione per riassumere o contare.
- Profilo legacy e valori numerici conservati senza conversione silenziosa: prompt_max_tokens resta il limite in caratteri dei percorsi legacy. La nuova politica600 token è indipendente e dichiarata nelle impostazioni, con dettagli di input/riserva/scambi. La010 può leggere ancora il profilo. Nessun aumento automatico del contesto o dell'output.
- M2: originali recenti separati dai record storici brevi; massimo16 coppie per partizione,16384 caratteri per testo. Pruning transazionale, trigger di cancellazione anche per una versione precedente che cancelli soltanto la tabella originale. Colonne/ricerche/snapshot storici preservati, nessun duplicato Telegram, filtri sensibili applicati prima della scrittura.
- Recupero quando la RAM di quel contesto è vuota; ruoli originali nello stesso selettore M1. Idratazione RAM soltanto all'accettazione della risposta. Non si fonde a ogni turno una cronologia disco potenzialmente concorrente con una sessione già attiva.
- Second Brain generale OFF impedisce letture successive e nuova idratazione da un owner revocato. Il dialogo RAM già accettato resta, come prima. Cancellazione esplicita revoca letture/risposte pendenti e svuota la RAM generale. Memoria dei progetti espliciti resta indipendente dall'interruttore generale; progetti nel cestino esclusi. Epoch, azioni consentite, selezione GPT/Gemma e Telegram conservati.

## Prove osservate
| Fase | Sorgente/run | Esito |
| --- | --- | --- |
| M1 RED |311a62d /42451445590|970 test;3 failure e1 error esclusivamente nelle4 nuove regressioni: perdita storia, falsa soglia caratteri, contatore ignorato|
| Tokenizer reale |42451445591|conteggio e prompt_tokens coincidono15/25, Unicode e delimitatori inclusi|
| M1 GREEN |7992049 /42451932114|974 test passati per Python3.11 e3.12 su Windows; controlli nativi/PowerShell/WindowsSearch applicabili riusciti|
| Owner/DLL M1 |42451932310|1 caricamento,2 richieste/2 generazioni; input29/47 token uguali al backend; scambio precedente nel secondo prompt|
| M2 RED |af1cf1f /42452312804|978 test;3 failure attese: dettaglio tardivo perso dopo riapertura generale/progetto e recupero recenti|
| M1+M2 GREEN |a81bf4f /42452818179|983 test per Python3.11 e3.12, entrambi OK; intero workflow SUCCESS. PowerShell, accesso file nativo, osservazione Search e integrazione live CI applicabile riusciti. Build e pubblicazione saltate intenzionalmente|
| Owner/DLL con recupero |a81bf4f /42452818064|SUCCESS;1 caricamento,3 richieste/3 generazioni; token29/47/82 coincidenti con il backend. Terza richiesta recupera SQLite riaperto, conserva domanda storica e passaggio tardivo con un estratto. Nessuna inferenza supplementare per memoria|

Log finali: job128645470840,983 test in143.514s; job128645470974,983 test in178.367s. I tempi sono dell'intera suite CI, non della generazione sul Pavilion.
CI eseguita sul merge tecnico ecdcb7f4c5dc50cfa6e4d46fc493dff56b910000: tree1c71ead7b7e32dca61394fadfd65dad2c2651b41 identico al tree del sorgente a81bf4f. Nessuna differenza di codice fra sorgente indicato e checkout verificato.

- [Suite Windows finale](https://github.com/MATRIXNEO23/jarvis/actions/runs/42452818179)
- [Prova modello/DLL finale](https://github.com/MATRIXNEO23/jarvis/actions/runs/42452818064)
- [Modifiche nel ramo di lavoro](https://github.com/MATRIXNEO23/jarvis/commit/a81bf4f2541cf6d8f3ca4f0c78ebc0b0ae031f91)

Revisione indipendente M1: due rilievi importanti risolti (riferimento tardivo durante estrazione, budget combinato storia/archivio), aggiunti test per citazioni/Unicode e conservazione profilo. Recheck: nessun importante nuovo difetto. Rifiniti successivamente gli offset Unicode mantenendo le posizioni originali.
Revisione indipendente M2: nessun difetto bloccante confermato; ampliati test per limiti e cancellazione progetti, OFF prima dell'accettazione e clear durante lettura. Recheck mirato senza nuovi problemi importanti. Limite minore: il test dei più recenti4–19 verifica l'API pubblica con fallback legacy; non ispeziona separatamente ogni ID del payload recente. Il codice SQL di pruning è stato ispezionato. Nessun test funzionale eseguito su Linux.

## Limiti e prossimo passo
Il modello CI è bartowski/gemma-2-2b-it-GGUF/gemma-2-2b-it-Q4_K_M.gguf, verificato con SHA256 del publisher. Non è stato confrontato l'hash del file sul PC dell'utente. Non è una versione abliterated.
Non sono stati misurati latenza/RAM/qualità sul Pavilion. Conteggio e selezione non fanno altre generazioni, ma un prompt più ricco può aumentare prefill e tempo totale. L'estrazione lessicale non è un riassunto semantico e non garantisce ogni referente ambiguo; un singolo scambio o un riferimento oltre i limiti conservati può restare indisponibile. Testare risposte vere sul PC è ancora necessario. Il testo già perso dai vecchi record troncati non si ricostruisce retroattivamente.
La cronologia breve legacy resta per ricerca/compatibilità; gli originali estesi sono soltanto i recenti. Non vengono importati documenti o corpi file per creare memoria. Nessun riassunto generativo automatico, nuovo modello, embedding o servizio a pagamento.
Prossimo passo: eventuale nuova candidata solo su richiesta di build/pubblicazione, poi collaudo sul Pavilion con stessi C/O/modello e dialoghi.010/009 disponibili per rollback. Questo checkpoint documentale non modifica il runtime verificato.
