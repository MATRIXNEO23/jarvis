# Audit prestazioni Gemma — 8 novembre 2026

## Ambito e stato
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
Strumento tools/probe_native_prompt_performance.py, workflow .github/workflows/native-prompt-performance.yml, questo rapporto e checkpoint nei documenti di stato/handoff/lezioni. Prima controllo sintassi statico, poi esecuzione Windows e rilettura dei risultati. Nessun test funzionale Linux. Esito ancora pendente.
