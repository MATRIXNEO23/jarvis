# Audit prestazioni Gemma — 8 novembre 2026

## Ambito e stato finale
Richiesta: verificare se la memoria comprime il contesto durante la generazione e perché la latenza segnalata è salita da circa30 a105secondi. Audit della012, sorgente e79eac854844a84944c05c914ab0dc125d86832c (runtime e29bc749). Nessuna modifica al prodotto, nessuna build o nuovo ZIP autorizzato da questo audit.

Foto diagnostica: input701/768token, output riservato128, margine128,3scambi interi,0estratti/omessi/ripristinati. Il128 non è il numero di token effettivamente generati. La foto del terminale non consente una ripartizione affidabile dei tempi.

## Piano finito prima della prova
1. Ricostruire percorso chat, sincronizzazione, caricamenti, conteggi e richiamo archivio; confronto indipendente in sola lettura concluso.
2. Aggiungere soltanto uno strumento di audit e workflow Windows che riusano sessione/adattatore/DLL reali e modello pubblico Gemma2 2B IT Q4_K_M verificato. Fixture sintetiche, nessun account o dato personale.
3. Separare tempo totale prepare_turn, caricamento, conteggi, selezione, callback memoria e inferenza; contare generazioni e caricamenti. Confrontare catalogo+3scambi, ripetizione identica,1scambio, controllo senza catalogo, richiamo archivio stabile/variabile e ultima risposta lunga. Non sommare tempi annidati.
4. Salvare esiti/limiti e proposta minima. Runner Windows diverso dal Pavilion: non estrapolare secondi o miglioramenti garantiti. Coda Telegram, DB/fsync, UI e voce del PC restano fuori dalla prova nativa.

## Fatti già verificati sul sorgente
- Nessun riassunto generativo nella chat: CompactContext e IdleMemoryGate non hanno chiamanti nel runtime. select_recent_pairs seleziona/taglia testo prima dell’unica chiamata al modello. Nella foto non è stato necessario estrarre testo.
- Una sola upstream.generate per richiesta. Sessione, provider e bridge serializzano le operazioni; Telegram può attendere o far attendere la chat, non comprime parallelamente.
- Riutilizzo del modello a configurazione equivalente; prova esplicita nelle impostazioni o cambi modello/DLL/thread/contesto possono ricaricare.
- Cache locale dei conteggi presente, ma adapter.call riconta il prompt finale già contato; viene misurato anche un prefisso di ricordi inutilizzato quando non c’è callback/spazio.
- Catalogo delle azioni inviato anche alle domande di conversazione. Cronologia+richiamo limitati a600token reali nel percorso con tokenizer; il budget effettivo non usa prompt_max_tokens configurabile. Il cambio da limite prudenziale in caratteri a token può aver aumentato il testo storico ammesso: da verificare quantitativamente, non causa unica dimostrata.
- I ricordi variabili sono aggiunti all’inizio del primo messaggio utente. Possono alterare il prefisso comune e ridurre il riuso della cache nativa: impatto da misurare.
- SecondBrain può cercare3000ricevute e1500episodi e allegare recenti già presenti nella chat. Il salvataggio precede la visualizzazione e nei progetti include fsync/snapshot. Impatto HDD non misurato.

## File da aggiungere; prossimo controllo
Strumento tools/probe_native_prompt_performance.py, workflow .github/workflows/native-prompt-performance.yml, questo rapporto e checkpoint nei documenti di stato/handoff/lezioni. Prima controllo sintassi statico, poi esecuzione Windows e rilettura dei risultati. Nessun test funzionale Linux. Esito inizialmente pendente; completato come riportato sotto.

## Prima prova Windows: checkpoint e controllo aggiuntivo
Run42464366606, sorgente88baf15:SUCCESS,8richieste/8generazioni,1load. Sette conteggi con3scambi: circa7ms; selezione con estrazione circa5ms. Prompt419token: primo totale25,985s (load2,548s), identico1,830s; ricordo A297token1,789s alla ripetizione identica contro6,649s per ricordo B297token (output12/14token). Sono prove sintetiche, non spiegazione dei105s sul PC.
Scoperto un limite della telemetria upstream: media per token moltiplicata per input completo riporta52,794s di process quando generate dura1,822s. Non usare backend.process_seconds come durata reale con riuso cache; walltime affidabile. Strumento aggiornato per conservare medie grezze, senza questa moltiplicazione. Aggiunti2casi vicini ai701token reali della foto. Importazione/creazione provider escluse dal caso cold; misurato il load nativo. Entrambe le deviazioni della review preventiva corrette (checkout SHA e unica sessione persistente). Nuova verifica Windows giustificata da questi rilievi, non nuova revisione globale. Nessun runtime cambiato, nessuna build.

## Causa tecnica e proposta, prima del risultato finale
Il sorgente pinned upstream `model_adapter.cpp`, funzione ContextFastForward, riusa i token iniziali identici fino alla prima divergenza. Nei log nativi della prima prova il ricordo A identico richiede di processare1token/0,18s; cambiando solo A→B nello stesso JSON e mantenendo297token totali, il backend processa92token/4,75s. La generazione di output passa da12a14token (1,60/1,89s). È un costo di cache/prefill dimostrato sulla fixture, non una seconda generazione di riassunto né una prova completa della regressione PC. Il controllo senza catalogo riduce278→107token (171token di differenza in questa configurazione), ma non è una proposta di eliminare i controlli o le capacità.
Il backend segnala SWA attivo e context shifting disabilitato per questo modello; non forzare opzioni incompatibili per ottimizzare. Il riuso del prefisso continua a funzionare.
Proposta minima da concordare dopo audit: budget cronologia/ricordi configurabile, inizialmente più contenuto (200–250token come candidato da collaudare), ultima coppia protetta dall’estrattore esistente; istruzioni stabili all’inizio e dati richiamati variabili vicini alla domanda attuale; evitare duplicazione dei recenti nell’archivio e misure inutili soltanto se preservati i controlli di sicurezza. Nessun riassuntore generativo nuovo e nessun aumento automatico del contesto. Non promettere ritorno a30s: mancano confronto a parità di output e misure Pavilion di coda/load/prefill/generazione/salvataggio/UI/TTS.

## Esito finale Windows — audit concluso
[Run42464609069](https://github.com/MATRIXNEO23/jarvis/actions/runs/42464609069) SUCCESS sul sorgente43b719bff81930120860101cecb7b8f238b637b7, con checkout esplicito di quello SHA; PR59 draft, base fix/service-diagnostics-20261108.10richieste,10generazioni,1caricamento,0selezioni durante generate, nessun riassunto generativo. Tutti i conteggi corrispondono ai token di input del backend, budget1024−128−128=768rispettato,3scambi interi anche nel caso705token. Solo test Windows.

| Caso sintetico | Input | Output effettivo | Token realmente processati (log nativo) | Prefill (s) | Output (s) | prepare_turn totale (s) |
|---|---:|---:|---:|---:|---:|---:|
|3coppie, primo load|419|13|419|25,88|2,09|31,761|
|Stesso prompt identico|419|13|1|0,18|2,14|2,322|
|3coppie, vicino alla foto|705|13|451|28,04|2,41|30,466|
|Stesso705identico|705|13|1|0,20|2,58|2,800|
|Solo ultima coppia +catalogo|278|17|89|5,58|2,60|8,193|
|Controllo senza catalogo|107|13|102|6,34|1,33|7,677|
|Ricordo A, ripetizione identica|297|12|1|0,19|1,71|1,899|
|Ricordo B, unica lettera cambiata|297|14|92|5,43|2,02|7,452|
|Ultima risposta lunga, estratta|346|12|157|9,76|1,77|11,542|

Nel caso705token i7conteggi durano8,37ms totali; la selezione include alcuni di essi, quindi non sommare tempi annidati. Nel caso estratto la selezione dura8,21ms (valore esatto nel JSON). Il costo significativo della fixture è prefill nativo, non la compressione testuale. Ripetizione identica è un controllo artificiale della cache, NON la velocità promessa di un dialogo reale: domanda/risposta successiva e finestra scorrevole cambiano il prompt. Il confronto fra casi in ordine fisso non misura un risparmio lineare per token, anche gli output differiscono.

Le due esecuzioni hanno velocità diverse: prima prova circa20token/s di prefill, seconda circa16. I loro secondi non vanno mescolati per stimare accelerazioni. Il modello pubblico verificato è Gemma2 2B IT Q4_K_M, SHA256e0aee85060f168f0f2d8473d7ea41ce2f3230c1bc1374847505ea599288a7787; identità del file personale non verificata. DLL pinned SHA256ac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba.

Evidenze persistenti: [prima prova annotata](evidence/gemma-performance-first-20261108.json), [prova finale](evidence/gemma-performance-final-20261108.json). I JSON conservano conteggi/tempi e provenance, non testi o dati personali. La prima prova conserva i valori derivati errati della telemetria con avviso esplicito; per durate usare walltime/log console. La prova finale conserva soltanto medie backend grezze e log process/generate correttamente associati ai10casi.

## Conclusione e prossimo passo
L’ipotesi di compressione generativa concorrente è esclusa nel percorso verificato. Sono dimostrati il costo del prefill per testo non riutilizzato, la sensibilità al cambiamento dei ricordi in testa al prompt e i conteggi ridondanti (minori in CI). Confermato il limite storia/ricordi600token fisso, indipendente dal vecchio parametro configurabile in caratteri. Questo non prova che da solo spieghi tutti i75secondi in più sul Pavilion.
Nessuna modifica runtime, nessun nuovo ZIP o pubblicazione Download.012 immutata. Proposta tecnica sopra, non implementata: budget più contenuto/configurabile, ultimo scambio preservato, dati variabili vicino alla domanda e riuso prefisso; niente nuovo riassuntore. Richiesti per attribuzione completa del caso PC tempi di attesa/caricamento/preparazione/generazione/salvataggio/visualizzazione a parità di modello, output effettivo e impostazioni. Non aggiungere altri servizi, scansioni o framework per questo scopo.

## Controlli accessori al checkpoint finale
Run42464609139:999test OK su Windows/Python3.11 (job128681093568), diagnosi/Tk12prove job128681093609SUCCESS. Python3.12 job128681093373 ancora in corso al checkpoint; non dichiarato superato. Build/pubblicazione non richieste e saltate. Nessuna modifica del codice runtime richiede nuova candidata per questo audit.
