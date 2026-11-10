## Build 030 PROVA — add-on Musica

[Scarica Lumi-030-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-030-PROVA.zip)

Come la 029, più l'add-on Musica (installato spento: attivalo in Impostazioni > Gestisci add-on > Musica, poi Configura per scegliere la cartella). «Lumi, metti …» cerca il brano nella cartella musica e lo suona dentro Lumi; se non c'è apre la ricerca su YouTube nel browser (con la chiave API YouTube facoltativa apre subito il primo video). Pausa, riprendi, prossima, ferma la musica, volume, anche a voce; barra sotto il nucleo. Con l'add-on spento Lumi resta com'era. Verificati in CI Windows: 1217 test, voce inclusa sul pacchetto estratto, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42843310028). SHA-256: `663fff0d8a5cdc7b419e64635add0a1ee4d650c2e18783202ef567f06c6380b1`.

## Build 029 PROVA — finestra Modello locale: Salva e Prova di nuovo visibili

[Scarica Lumi-029-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-029-PROVA.zip)

Come la 028, più: nella configurazione del modello locale i pulsanti Salva, Prova generazione e Chiudi restano sempre in fondo alla finestra, il resto scorre, e l'altezza si adatta allo schermo (sulla 026-028, con uno schermo da 768 px, i pulsanti finivano fuori e non si poteva salvare il nuovo GGUF). Nient'altro cambiato. Verificati in CI Windows: test della finestra su schermo piccolo, 1206 test, voce inclusa sul pacchetto estratto, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42817896454). SHA-256: `4a24902e0e76a6fd1711f53aabe34ff2c96535c0a99d0732eb7bacd877343286`.

## Build 028 PROVA — Telegram: avviso con nome e ID del mittente ignorato

[Scarica Lumi-028-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-028-PROVA.zip)

Come la 027, più: quando arriva un messaggio da un account che non è tra i contatti spuntati, Lumi lo scrive in chat una volta per mittente («messaggio da Nome [ID numero] ignorato»), invece di scartarlo in silenzio. Confronta quell'ID con quello mostrato in Gestisci contatti. Nient'altro cambiato. Verificati in CI Windows: 1205 test, ascolto Telegram simulato, voce inclusa sul pacchetto estratto, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42805702663). SHA-256: `bce0b7a73babfdec1c013b3be948048854c66518c36a6b1223c3bf92a7a27b3d`.

## Build 027 PROVA — Telegram: messaggi ricevuti elaborati di nuovo

[Scarica Lumi-027-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-027-PROVA.zip)

Come la 026, più: i messaggi Telegram che arrivavano a Lumi ma non venivano elaborati (diagnostica: «nuovo messaggio osservato» ma 0 messaggi autorizzati) ora vengono recuperati direttamente da Telegram dopo 2 secondi e ricevono risposta una sola volta. Gli errori interni del gestore messaggi ora compaiono in Lumi invece di sparire. Nient'altro cambiato. Verificati in CI Windows: 1205 test, ascolto Telegram simulato, voce inclusa sul pacchetto estratto, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42801282254). SHA-256: `e61e00dcba3fdb78152eebcc7e6cdedad2f30ab463f4efc81037cb23e7d498cf`.

## Build 026 PROVA — fast forwarding, carattere di Lumi, lunghezza delle risposte

[Scarica Lumi-026-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-026-PROVA.zip)

Come la 025, più: prompt riordinato (parti fisse in cima, regola di lunghezza vicino alla domanda) per sfruttare il fast forwarding di KoboldCpp, con interruttore in Modello locale (cambiarlo richiede il riavvio). In CI la seconda domanda con lo stesso inizio: 3,4 s invece di 14,8 s. Nuovi menu Carattere principale e Tocco in più, Lunghezza risposte (Nessuno, Breve scegli tu, 1-5 frasi), frasi per le spiegazioni (spiegami, come funziona, approfondisci, in dettaglio, descrivimi, consigliami) e Note su di te. Impostazioni precedenti mantenute, Telegram invariato. Verificati in CI Windows: 1204 test, voce inclusa sul pacchetto estratto, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42786913579). SHA-256: `5cdafd4300694965113e4f2b93e754bbca752c5920135299d43d24c15ad96841`.

## Build 025 PROVA — velocità, tonalità e volume della voce; configurazione Telegram corretta

[Scarica Lumi-025-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-025-PROVA.zip)

Come la 024, più: in Impostazioni > Voce i cursori Velocità, Tonalità e Volume, validi per Paola/Serena, voci Edge, voci Windows e note vocali Telegram; l'effetto digitale ora viene salvato. Configurazione Telegram: i campi sbagliati si possono reinserire, numero e hash vengono ripuliti (+39, spazi), e una nuova configurazione non cancella più i contatti spuntati (era il motivo per cui i messaggi non arrivavano più): se hai già riconfigurato con la 024, rispunta i contatti una volta. Verificati in CI Windows: 1197 test, voce inclusa sul pacchetto estratto, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42733173977). SHA-256: `a9b197099421526596c7c438fe3d7fac7ed55adb17e4cc84f50fb4c378c63037`.

## Build 024 PROVA — note vocali Telegram con la voce scelta, labiale agganciato all'audio

[Scarica Lumi-024-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-024-PROVA.zip)

Come la 023, più: le note vocali Telegram usano la voce scelta in Lumi (Edge, Paola/Serena o Windows) e, se non funziona, la voce Windows predefinita invece di non rispondere. La bocca dell'avatar segue la posizione reale dell'audio e parte solo quando parte il suono, con tutte le voci. configura_telegram.bat salva nello stesso profilo di avvia_lumi.bat e ricontrolla le credenziali. Verificati in CI Windows: 1191 test, voce inclusa sul pacchetto estratto, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42726221570). SHA-256: `bf12b5f8f7623a35678c120d7761c1c59248a47002cb64940680940c542b0cd2`.

## Build 023 PROVA — Telegram corretto, voci Edge, labiale anche con voce Windows

[Scarica Lumi-023-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-023-PROVA.zip)

Come la 022, più: Telegram legge di nuovo le credenziali già salvate (errore «Formato credenziali non riconosciuto» introdotto dalla rinomina). Streaming anche per richieste come «consigliami dei film». La voce non legge emoji e asterischi; nelle frasi lunghe parte alla virgola. Bocca che si muove anche con le voci Windows. Avatar più grande e più fluido (13 posizioni della testa, 8 aperture della bocca, 25 fotogrammi al secondo). Voci Microsoft Edge facoltative (Isabella, Elsa, Diego, Giuseppe): gratuite ma online, si attivano con installa_voce_edge.bat. Verificati in CI Windows: 1185 test, voce inclusa sul pacchetto estratto, labiale voce Windows, voce Edge reale, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42719345419). SHA-256: `a6e44f0c838d3942cf46ce609d619cba9634a9b9f246404dabf0613083c17370`.

## Build 022 PROVA — voce inclusa senza installazioni, avatar più naturale

[Scarica Lumi-022-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-022-PROVA.zip)

Come la 021, più: motore voce Piper incluso in Lumi (cartella voce_engine, solo italiano, senza installare nulla e senza numpy): basta premere «Scarica Paola» o «Scarica Serena». Avatar: la testa ruota piano a destra e sinistra (niente tremolio), le ciocche seguono il movimento e si assestano, respiro lento di spalle e petto, bocca a 5 aperture più morbida. Prompt un po' più leggero (cronologia 200 token, ultimo scambio sempre intero). Stesso profilo dati. Verificati in CI Windows: 1176 test, voce con il motore incluso sul pacchetto estratto (seconda frase 0,19 s), streaming, avvio UI e risposta del motore. Pavilion da collaudare (voce senza AVX2, resa dell'avatar).

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42708117898). SHA-256: `612e173dfb5717500be18fce7efe53f291f63ad4eae2103ea472fd897957c3e8`.

## Build 021 PROVA — avatar a figura intera, risposta in streaming, voce naturale veloce

[Scarica Lumi-021-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-021-PROVA.zip)

Come la 020, più: LUMI a figura intera (capelli e busto escono dal cerchio) con testa che oscilla piano; la bocca si muove solo quando l'audio suona davvero. La risposta compare mentre il modello la scrive e la voce parte dalla prima frase completa. Voce Paola/Serena: modello caricato una sola volta e frase successiva preparata mentre suona la precedente (in CI 0,17 s per frase invece di 5,5 s). Stesso profilo dati. Verificati in CI Windows: 1171 test, streaming reale di Gemma, ZIP estratto, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42701561517). SHA-256: `e89bbdf8f25fe8c1baa56f5583e6b6c955cb1ba61e6daf7fca97dc52fa588927`.

## Build 020 PROVA — avatar LUMI animato, voci naturali in un file ZIP ciascuna

[Scarica Lumi-020-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-020-PROVA.zip)

Come la 019, più: il volto di LUMI (la tua immagine, invariata) sostituisce la scritta nel cerchio centrale, con battito di ciglia, sguardo che si muove e bocca che segue la voce. Quando riduci a icona, il mini avatar resta in basso a destra sopra la barra; doppio clic per riaprire. Voci: «Scarica Paola» / «Scarica Serena» scaricano un unico ZIP verificato (Voce-Paola.zip, Voce-Serena.zip). Stesso profilo dati. Verificati in CI Windows: 1161 test, ZIP estratto, avvio UI e risposta del motore. Pavilion da collaudare (resa dell'avatar e consumo CPU).

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42693084765). SHA-256: `b1d2f57ecad420bd65667b0e075ea10a602190e855b3f77583173933272ab9ba`.

## Build 019 PROVA — l'assistente diventa LUMI, voci naturali Paola e Serena

[Scarica Lumi-019-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Lumi-019-PROVA.zip)

Come la 018, più: l'assistente si chiama Lumi ovunque (interfaccia, voce, Telegram) e la parola di attivazione è «Lumi» / «Ehi Lumi»; launcher avvia_lumi.bat. Voci naturali offline Piper: esegui installa_voce_naturale.bat, poi in Impostazioni > Voce premi «Scarica Paola» o «Scarica Serena» (dal repository, con verifica), scegli la voce e regola l'«Effetto digitale». Se il motore non gira su questo PC si torna alla voce di Windows. Stesso profilo dati (impostazioni, chat e memoria restano). L'avatar arriva nella prossima build. Verificati in CI Windows: 1153 test, voce Paola generata dal repository, ZIP estratto, avvio UI e risposta del motore. Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42678806394). SHA-256: `4239473ab934499fb2932673b4aa3a1ab5b60b1cac84f0814762da72004007ad`.

## Build 018 PROVA — tasto riduci a icona e conversazioni Telegram più fluide

[Scarica Jarvis-018-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-018-PROVA.zip)

Come la 017, più: il tasto «–» riduce Jarvis a icona nella barra delle applicazioni invece di farlo sparire; su Telegram il modello locale ricorda gli ultimi 3 scambi con ogni contatto come vera conversazione e risponde in massimo 2-3 frasi, con istruzioni più corte. Estrai in una cartella NUOVA; 014 resta la stabile. Verificati in CI Windows: test unitari (incluso il tasto riduci a icona), ZIP estratto, avvio UI e risposta del motore incluso. Telegram reale e Pavilion da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42665758452). SHA-256: `d9167de4a9ef834bdbd77c10aa0ae500ad0ccb326ed5b2e66d09fb60b6bd8762`.

## Build 017 PROVA — risposte Telegram locali corrette

[Scarica Jarvis-017-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-017-PROVA.zip)

Come la 016, più la correzione Telegram: il prompt della risposta automatica era misurato in caratteri invece che in token, e con contesto piccolo Jarvis rinunciava prima di chiamare il modello (ValueError: Contesto Gemma insufficiente). Ora usa il tokenizer reale del modello. Estrai in una cartella NUOVA; 014 resta la stabile. Verificati in CI Windows: test unitari, ZIP estratto, avvio UI e risposta del motore incluso. Telegram reale da collaudare sul Pavilion.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42655550438). SHA-256: `0325874986b00d2f7a228a1d53a0883245e808f8e275d938f94b605b204fa514`.

## Build 016 PROVA — chat stile ChatGPT, cronologia completa, prompt più leggero

[Scarica Jarvis-016-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-016-PROVA.zip)

Build di prova sopra la 015 (014 resta la stabile). Chat locali con elenco a sinistra apribile/chiudibile (☰), Nuova chat, titolo automatico dalla prima domanda e cronologia completa visibile anche dopo il riavvio. Le domande scritte risultano tue (TU) e non più Gemma. Il catalogo azioni arriva al modello solo se la frase sembra un comando: chat semplice con prompt più corto. Corretti: cronologia di una chat ridotta dopo l'uso di un'altra, salvataggio chat fallito ora ritentato, cattura Diagnostica prompt non persa su errore. Telegram: se la risposta locale fallisce la console mostra la causa esatta. Stesso profilo dati, estrai in una cartella NUOVA, cambio modello/contesto/thread con riavvio. Verificati in CI Windows: 1141 test, ZIP estratto, avvio UI e risposta del motore incluso. Pavilion, voce e Telegram reale da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42645704397). SHA-256: `1b68e8c0f64bf7659dc5648255acb6a3fb349e373d3306ef2a87a2cb046e88da`.

## Build 015 PROVA — motore KoboldCpp integrato (Gemma 2, Qwen2.5, Qwen3)

[Scarica Jarvis-015-PROVA.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-015-PROVA.zip)

Build di prova, non stabile: 014 resta la versione di riferimento. Nuovo motore KoboldCpp 6d2fedf no-AVX2 compilato con w64devkit, caricato dentro Jarvis senza server. La famiglia del modello (Gemma 2, Qwen2.5, Qwen3) è riconosciuta dal GGUF. Cambio di modello, contesto o thread: salva e riavvia Jarvis. Stesso profilo dati della 014 (impostazioni, chat e memoria conservate). Estrai in una cartella NUOVA. Verificati in CI Windows: ZIP estratto, avvio/chiusura UI, risposta Gemma dal motore incluso; prove Gemma/Qwen2.5/Qwen3 sul bundle. Velocità, RAM, voce e account sul Pavilion ancora da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42625213859). SHA-256: `c4c04198ce70486dd96f2e3e953e132c68424301211a3e24026a9763a960dbff`.

## Build 014 — Gemma: conversazione naturale e comandi protetti

[Scarica Jarvis-014.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-014.zip)

Domande informative risolte in chat naturale senza catalogo azioni e senza JSON obbligatorio. Il sistema conserva le verifiche rigorose dei comandi e riconosce direttamente sinonimi sicuri di stato sistema. Distinto il raggiungimento di Max Output dai JSON malformati. Suite 1013 test sullo ZIP estratto e prova con GGUF reale su Windows, senza promettere gli stessi tempi sul Pavilion. Estrai in una cartella nuova, conservando 013, progetti, cronologia e profilo. Test microfono e Telegram reali ancora pendenti.

[Verifiche Windows/GGUF](https://github.com/MATRIXNEO23/jarvis/actions/runs/42516477567). SHA-256: `f9c9cd92d1443774e48be89674ce04d9897f47d003df0ad11972ab7815d671c0`.

## Build 013 — Contesto Gemma leggero e configurabile

[Scarica Jarvis-013.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-013.zip)

Nel pannello Memoria e inattività, Token cronologia e ricordi (Gemma):250 iniziali, regolabili da128 a600. Ultimo riferimento preservato con estrazione locale se necessario; scambi esclusi dal solo prompt, senza cancellare gli archivi. Ricordi variabili vicini alla domanda per favorire il riuso del contesto. Impostazioni legacy compatibili, nessun riassuntore generativo o aumento automatico della finestra del modello. Include le funzioni della012. Due job Windows e1006test sullo ZIP estratto superati. Estrai in una cartella nuova e conserva012 e profilo; prestazioni sul Pavilion e account Telegram reale ancora da collaudare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42501645142). SHA-256: `1926bb5b65d98bb78d1c829cd9143b1e39773c8c14581f6f63a8d0d9454ed781`.

## Build 012 — Diagnostica servizi e Telegram

[Scarica Jarvis-012.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-012.zip)

Impostazioni > Progetti e servizi > Apri diagnostica servizi, oppure comando vocale e scritto diagnostica servizi. Rapporto aggiornabile e copiabile con stato dei componenti e fasi Telegram, prima dei filtri fino al modello, sintesi e invio. Registro RAM limitato senza contenuti dei messaggi, nomi o credenziali; nessun invio di prova o avvio dei modelli. Include le correzioni della011. Due job Windows e 999 test sullo ZIP estratto superati. Estrai in una cartella nuova; collaudo sul Pavilion e causa della mancata ricezione sull’account reale ancora da verificare con il rapporto.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42457722089). SHA-256: `57c8fa161d36020207a46e2a6eee45f5fec8f0987546ae601e3abe1b6881c680`.

## Build 011 — Contesto Gemma e ricezione Telegram

[Scarica Jarvis-011.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-011.zip)

Conteggio nativo dei token, ultimo scambio protetto e recupero dei recenti dopo riavvio con Memoria attiva. Correzione del listener Telegram che poteva restare falsamente attivo dopo una disconnessione definitiva. Nessun riassunto generativo aggiuntivo. Due job Windows e 987 test sullo ZIP estratto superati. Estrai in una cartella nuova senza sovrascrivere la precedente. Collaudo Pavilion, microfono, account Telegram e GGUF reale pendente: la causa sul PC della mancata ricezione resta da confermare.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42455562664). SHA-256: `8d388afe774b62d034c4fc8b7a836493654fa7baee201b4b004df37c39815250`.

## Build 010 — Risposte conversazionali Gemma

[Scarica Jarvis-010.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-010.zip)

Correzione delle risposte Gemma in testo libero: chat mostrata, pronunciata e conservata; azioni ancora soggette alla validazione e messaggi locali attribuiti a Gemma. Include le correzioni della009; nessun nuovo sistema di riassunto. Due job Windows e 966 test sullo ZIP estratto superati. Estrai in una cartella nuova senza sovrascrivere la precedente. Collaudo Pavilion, microfono, account e GGUF reale pendente.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42447357900). SHA-256: `c71c4442969ded771bf7db4fe823196814e742b65ceec3b092949b46d0b98aae`.

## Build 009 — GPT e contesto Gemma

[Scarica Jarvis-009.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-009.zip)

Scelta GPT per voce/chat/PTT/Telegram, consenso conversazionale per la sessione, comandi di cambio modello e cronologia Gemma2 IT con turni separati. Due job Windows e 962 test sullo ZIP estratto superati. Estrai in una cartella nuova senza sovrascrivere la precedente. Collaudo Pavilion, microfono, account e GGUF reale pendente.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42440862650). SHA-256: `c17224c0de53c92942e6e2b79d76d02fb9bd9f3592ad9fb185634d1e0afa5a45`.

## Build 008 — Comandi interni e Gemma

[Scarica Jarvis-008.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-008.zip)

Comandi interni con sinonimi, browser predefinito, help aggiornato e interpretazioni Gemma collegate agli esecutori esistenti. Due job Windows e 946 test sullo ZIP estratto superati. Estrai in una cartella nuova; collaudo Pavilion, microfono e GGUF reale pendente.

[Verifiche Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/42431542519). SHA-256: `63c1d46e4402229a20a0849c0d91266ce81e7075d74cba65160c10f08bfceea4`.

# Jarvis007 — timer scritto e guida locale

**[Scarica Jarvis-007.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-007.zip)**

«Imposta timer sei minuti» avvia360secondi dalla chat. «Aiuto», «help» o «comandi», il pulsante **?** e **F1** aprono la guida locale a sezioni. **Ctrl+L** torna alla casella di comando anche dalla guida/impostazioni. **Ctrl+,** apre le impostazioni. Nessun cambio alla scelta Gemma/GPT: i comandi base del catalogo indicano quando usare **⋯ → Esegui locale**.

Estrai in una cartella NUOVA e avvia `Jarvis-Gemma/avvia_jarvis.bat`. Profilo Gemma-Trial invariato rispetto alla006, nessuna cancellazione o migrazione dati. GGUF e account non inclusi; Python3.11/3.12 x64 e dipendenze devono essere predisposti.

[Verifiche Windows e runtime estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42420559553):922test per versione Python nei sorgenti e922 sull’estratto con supporti di test separati, non distribuiti. Verificati manifest/hash/guide/import/DLL e avvio/chiusura UI. Collaudo Windows10/i3/audio/account/GGUF reali ancora da fare: candidata, non certificazione del PC.

[Sorgenti esatti](https://github.com/MATRIXNEO23/jarvis/tree/9f8c5f582b98a4ac131c41a4170b194c98abc3fa) · [Consegna](../docs/CONSEGNA-JARVIS-007-20261107.md) · [Handoff](../docs/HANDOFF-JARVIS-007-20261107.md) · [Versioni precedenti](REGISTRO-VERSIONI.md).

SHA256 `a5a24f35b410a45bed3dd08ed2180563d429e82cbe0a878045f4e7157182408f` — 8138643 byte, 119 file.

---

# Jarvis 006 — Gemma e correzioni audit

**[Scarica Jarvis-006.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-006.zip)**

Correzioni a permessi GPT, separazione dei progetti, memoria locale, documenti, voce, concorrenza Gemma/add-on, timeout, HUD, impostazioni e risorse. Guide operative incluse. Nessun nuovo indice autonomo; causa del timeout intermittente CI ancora da chiarire.

Estrai in una cartella NUOVA, senza sovrascrivere la precedente, e avvia solo `avvia_jarvis.bat` nella cartella `Jarvis-Gemma`. Il launcher conserva il profilo `Jarvis-Gemma-Trial` delle candidate Gemma. Non cancellare i vecchi dati. Python3.11/3.12 x64 e dipendenze devono essere gia predisposti; GGUF e account non inclusi. Se provieni dalla005, il profilo Gemma e distinto: non cancellare o migrare a mano il profilo precedente.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42384228753):911 test per versione Python nei sorgenti e911 sul runtime estratto; import/DLL/avvio/chiusura in profilo temporaneo verificati. La suite completa dell’estratto usa supporti di sviluppo separati, non distribuiti. Windows10/i3-2100, GGUF, audio e account reali restano da collaudare: candidata, non versione PC certificata.

[Sorgenti esatti](https://github.com/MATRIXNEO23/jarvis/tree/3e2cc05b0b08fdc5b47054b19593cf3151aff75a) · [Consegna e limiti](../docs/CONSEGNA-JARVIS-006-20261107.md) · [Versioni precedenti](REGISTRO-VERSIONI.md).

SHA-256: `066c6f0cb0af78a9e064119d1a9a39a9317f7524456e14c1716555d9d08f103a` — 8134642 byte, 118 file.

---

> **Indice autorevole:** [versioni, commit sorgenti, workflow e hash](REGISTRO-VERSIONI.md). I link sotto conservano la cronologia. Le correzioni audit in bozza non sono automaticamente contenute negli ZIP pubblicati.

# Jarvis Gemma — carattere e stile del modello locale

**[Scarica la candidata Windows](./Jarvis-Gemma-Carattere-e-Stile-61a95f8.zip)**

In Impostazioni → GPT e memoria → Configura Gemma locale, il campo Carattere e stile accetta istruzioni personalizzate fino a 240 caratteri.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42270285346). Collaudo con Telegram e Gemma sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: c38806cf12574e7ae142a8eef2cebe2afec6244c92db0a195c507d6bade6041a

---

# Jarvis Gemma — consenso GPT per la sessione Telegram

**[Scarica la candidata Windows](./Jarvis-Gemma-Telegram-Consenso-GPT-Sessione-c233bb4.zip)**

In Impostazioni → Telegram → Consenso GPT online puoi scegliere Consenti per questa sessione per i contatti spuntati. Chiedi ogni volta resta il valore iniziale.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42251845994). Collaudo con Telegram e Gemma sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: 59f3acd524c7f39b3bcb7846ca13ecd614f7537040220b2d9843522ca42a34e2

---

# Jarvis Gemma — notifiche Telegram nel HUD

**[Scarica la candidata Windows](./Jarvis-Gemma-Telegram-Notifiche-HUD-bf6bce9.zip)**

Il pallino del contatto lampeggia finché ci sono messaggi Telegram da vedere. Aprendo la conversazione dal pallino, i messaggi mostrati vengono segnati come visti in Jarvis.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42222733895). Collaudo con Telegram e Gemma sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: 30f1226a76c4723d5d756faa51bd10306a90ddaaff96a889517c39250be30cc3

---

# Jarvis Gemma — contesto per contatto Telegram

**[Scarica la candidata Windows](./Jarvis-Gemma-Telegram-Contesto-Contatti-0055607.zip)**

In Impostazioni Telegram → Contatti puoi salvare un contesto separato per ogni contatto autorizzato. Il profilo è usato da Gemma locale nelle risposte Telegram.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42211351973). Collaudo con Telegram e Gemma sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: 6e718b5f1576bfc86a8b68d56a015eea29d38ed966027eff8d180d0f03df7a48

---

# Jarvis Gemma — ascolto continuo

**[Scarica la candidata Windows](./Jarvis-Gemma-Ascolto-Continuo-b62d8a7.zip)**

In Ascolto continuo puoi parlare direttamente. In modalità Hey Jarvis serve il richiamo. Entrambe provano prima il motore locale e usano Gemma per le richieste non gestite localmente.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42170295267). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: a27885b2e085f9aad47054f53acec5599f5558367d26b49d3858559ea87e8b26

---

# Jarvis Gemma — voce in console

**[Scarica la candidata Windows](./Jarvis-Gemma-Voce-Console-53460ce.zip)**

Ripristina la ricerca del modello vocale italiano nel profilo sorgente e mostra in console gli errori del microfono.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42165467735). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: e2101e7523f424256dea9fbca3eb401500b401c7cbf332c3fdc80c7e93e1f094

---

# Jarvis Gemma — risposte Telegram

**[Scarica la candidata Windows](./Jarvis-Gemma-Telegram-9adc86e.zip)**

Gemma può rispondere su Telegram quando GPT è disattivato. Il collaudo con Telegram e Gemma sul Pavilion è ancora da fare.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42163091184). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: 7df6c330da85c6bf49353e657e5d0f3c8a5fd2076f8c257bdb71e27ed9e8cdbd

---

# Jarvis Gemma — comandi in chat e finestre senza cornice

**[Scarica la candidata Windows](./Jarvis-Gemma-Comandi-e-Interfaccia-f387779.zip)**

In **Impostazioni → Interfaccia** puoi attivare **Tieni acceso il PC con Jarvis massimizzato in primo piano**. La preferenza è disattivata di default.

Le risposte di dialogo restano in chat. Una richiesta di apertura con un riferimento recente e univoco può diventare una proposta da confermare. Include «con Gemma» anche per testo e i tre pulsanti integrati, senza barra del titolo aggiuntiva. Trascina vicino al bordo superiore per spostare ogni finestra. Jarvis cerca la finestra del programma avviato e verifica il passaggio in primo piano. Include l’orologio nell’interfaccia, il comando «che ore sono?» e l’add-on Sveglia.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42160047720). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: b97e3c3883f106bd761144067a0aad47bdec51fe78a9df7e6a8f93d59b1f7f6b

---

# Jarvis Gemma — comandi in chat e finestre senza cornice

**[Scarica la candidata Windows](./Jarvis-Gemma-Comandi-e-Interfaccia-c1ac14f.zip)**

Le risposte di dialogo restano in chat. Una richiesta di apertura con un riferimento recente e univoco può diventare una proposta da confermare. Include «con Gemma» anche per testo e i tre pulsanti integrati, senza barra del titolo aggiuntiva. Trascina vicino al bordo superiore per spostare ogni finestra. Jarvis cerca la finestra del programma avviato e verifica il passaggio in primo piano. Include l’orologio nell’interfaccia, il comando «che ore sono?» e l’add-on Sveglia.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42157188141). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: ee25da511c82c2bae178aa1126a9fb5babf5f2ee428ec9fd8398de59e3413276

---

# Jarvis Gemma — comandi in chat e finestre senza cornice

**[Scarica la candidata Windows](./Jarvis-Gemma-Comandi-e-Interfaccia-43b2045.zip)**

Le risposte di dialogo restano in chat. Una richiesta di apertura con un riferimento recente e univoco può diventare una proposta da confermare. Include «con Gemma» anche per testo e i tre pulsanti integrati, senza barra del titolo aggiuntiva. Trascina vicino al bordo superiore per spostare ogni finestra. Jarvis cerca la finestra del programma avviato e verifica il passaggio in primo piano. Include l’orologio nell’interfaccia, il comando «che ore sono?» e l’add-on Sveglia.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42157045926). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: 3e65c7244a0515c0c727b2443021e09011c7c225b84e71027fe97bfce60d5a52

---

# Jarvis Gemma — comandi in chat e finestre senza cornice

**[Scarica la candidata Windows](./Jarvis-Gemma-Comandi-e-Interfaccia-b96a0d6.zip)**

Le risposte di dialogo restano in chat. Una richiesta di apertura con un riferimento recente e univoco può diventare una proposta da confermare. Include «con Gemma» anche per testo e i tre pulsanti integrati, senza barra del titolo aggiuntiva. Trascina vicino al bordo superiore per spostare ogni finestra. Jarvis cerca la finestra del programma avviato e verifica il passaggio in primo piano.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42152839696). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: 2c81cd8f80f45d9270eb6db74320f83278f478d9b8c8853bd7c7a61dbcf9813c

---

# Jarvis Gemma — comandi in chat e finestre senza cornice

**[Scarica la candidata Windows](./Jarvis-Gemma-Comandi-e-Interfaccia-bd8d832.zip)**

Le risposte di dialogo restano in chat. Una richiesta di apertura con un riferimento recente e univoco può diventare una proposta da confermare. Include «con Gemma» anche per testo e i tre pulsanti integrati, senza barra del titolo aggiuntiva. Trascina vicino al bordo superiore per spostare ogni finestra.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42150179430). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: 7fac1c28d51978e2a180328b0dc0ca19d3e74d38430b5d3263529ff7245e7c26

---

# Jarvis Gemma — comandi in chat e finestre senza cornice

**[Scarica la candidata Windows](./Jarvis-Gemma-Comandi-e-Interfaccia-a4dce52.zip)**

Le risposte di dialogo restano in chat. Una richiesta di apertura con un riferimento recente e univoco può diventare una proposta da confermare. Include «con Gemma» anche per testo e i tre pulsanti integrati, senza barra del titolo aggiuntiva.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42149101326). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: f22f5500a2f67d7e6143a0d750d48083ca64b9434c79d898d17f49c04c41a083

---

# Jarvis Gemma — comandi in chat e finestre senza cornice

**[Scarica la candidata Windows](./Jarvis-Gemma-Comandi-e-Interfaccia-0c3117b.zip)**

Le risposte di dialogo restano in chat. Una richiesta di apertura con un riferimento recente e univoco può diventare una proposta da confermare. Include «con Gemma» anche per testo e i tre pulsanti integrati, senza barra del titolo aggiuntiva.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42149002686). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: 83c189783d9d88c2c03c0ed8d6f07d4b3d43c86cbcc3c6493a1a07674c3ad6c6

---

# Jarvis Gemma — comandi in chat e finestre senza cornice

**[Scarica la candidata Windows](./Jarvis-Gemma-Comandi-e-Interfaccia-6e73e3b.zip)**

Le risposte di dialogo restano in chat. Una richiesta di apertura con un riferimento recente e univoco può diventare una proposta da confermare. Include «con Gemma» anche per testo e i tre pulsanti integrati, senza barra del titolo aggiuntiva.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42147766728). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: 9bcd0cb8d83ea035db4855ddb6a1e02be04acf7cbd1aff1518817c69d851ff41

---

# Jarvis Gemma — comandi in chat e finestre senza cornice

**[Scarica la candidata Windows](./Jarvis-Gemma-Comandi-e-Interfaccia-1b5d647.zip)**

Le risposte di dialogo restano in chat. Una richiesta di apertura con un riferimento recente e univoco può diventare una proposta da confermare. Include «con Gemma» anche per testo e i pulsanti integrati nelle finestre di Jarvis.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42146452342). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: b1bf964bb0682f64f7aa8643eb128cfa9283d9bfc59e7b9753f9572e62064aec

---

# Jarvis Gemma — avvio programmi e varianti vocali

**[Scarica la candidata Windows](./Jarvis-Gemma-Avvio-Programmi-5d554c8.zip)**

Include apri, aprimi, avvia, avviami e altre varianti. Se il nome è incompleto o simile, Jarvis chiede di precisare. «Con Gemma» è una prova facoltativa con conferma.

[Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42142495567). Collaudo di voce, Gemma e app reali sul Pavilion ancora da fare. Estrai la candidata in una cartella separata.

SHA-256: e54912b4e3de94c06dc654cd2fc4f64b698f0f2f2249ff67dab6e091022b8944

---

# Jarvis Gemma — chat vocale e avvio programmi (05/11/2026)

**[SCARICA JARVIS GEMMA — CHAT, VOCE E AVVIO PROGRAMMI](./Jarvis-Gemma-PROVA-CORRETTA.zip)**

Build di prova aggiornata: chat collegata a Gemma locale, risposte vocali tramite la sintesi di Jarvis e gestione dei comandi di avvio attraverso il modulo autorizzato **Programmi e app**. Se un programma non può essere avviato, Jarvis deve segnalarlo anziché dichiarare falsamente di averlo aperto. Compilazione Windows [riuscita](https://github.com/MATRIXNEO23/jarvis/actions/runs/42081766861). **L'avvio effettivo dei programmi e la voce sul PC dell'utente sono ancora da collaudare.** Estrai in una cartella separata, senza sostituire la versione stabile.

---

# Jarvis Gemma — pulsante di prova ripristinato (05/11/2026)

**[SCARICA JARVIS GEMMA — PROVA TEST RIPRISTINATO](./Jarvis-Gemma-PROVA-TEST-RIPRISTINATO.zip)**

Deriva dalla precedente PROVA-CORRETTA, preserva il pulsante Prova generazione e aggiunge dettagli di errore dal bridge. Test di regressione del pulsante e integrità ZIP eseguiti in CI Windows. Generazione effettiva sul Pavilion ancora da verificare; non sostituire la versione stabile.

---

# Jarvis Gemma — diagnostica generazione (05/11/2026)

**[SCARICA JARVIS GEMMA DIAGNOSTICA](./Jarvis-Gemma-DIAGNOSTICA-20261105.zip)**

Versione diagnostica: espone lo stato e i dettagli restituiti dal motore nativo. Non risolve ancora il problema di generazione, non collaudata sul Pavilion. Estrarre in cartella separata senza sostituire la versione stabile.

---

# Jarvis Gemma — prova corretta (05/11/2026)

**[SCARICA JARVIS GEMMA — PROVA CORRETTA](./Jarvis-Gemma-PROVA-CORRETTA.zip)**

[Download diretto ZIP](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Gemma-PROVA-CORRETTA.zip) · [Workflow Windows riuscito](https://github.com/MATRIXNEO23/jarvis/actions/runs/42056417329)

Pacchetto sperimentale isolato e alleggerito, con DLL KoboldCpp CPU no-AVX2 inclusa e pulsante **Prova generazione** per visualizzare risposta o errore. Estrai in una cartella nuova, avvia `avvia_jarvis.bat`, scegli il GGUF nelle impostazioni Gemma e premi **Prova generazione**. Il GGUF non è incluso. **FunctionGemma 270M non è ancora stato collaudato sul PC Pavilion**; non sostituire la versione stabile.

---

# Jarvis Gemma - test Windows (05/11/2026)

**[SCARICA ZIP GEMMA WINDOWS DI PROVA](./Jarvis-Gemma-Windows-TEST-cc52c20.zip)**

Versione sperimentale isolata, con DLL nativa KoboldCpp no-AVX2 verificata.
Modello GGUF non incluso: selezionarlo nelle impostazioni Gemma insieme alla DLL.
Non sostituire la versione stabile; test prestazioni su Pavilion non ancora eseguito.
Pacchetto compilato e testato su Windows CI.

---
> **Recupero e versioni:** [registro](REGISTRO-VERSIONI.md). Ultima candidata **005**, verificata su Windows; collaudo PC pendente. Build001/002/003/004 e base PC b936879 conservate.

## Build 005 — Richiamo Jarvis e consumi

[Scarica Jarvis-005.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-005.zip)

Ogni richiesta vocale inizia con Jarvis: il parlato senza richiamo iniziale viene ignorato prima di azioni e GPT. Il solo nome non abilita la frase seguente. Estrai in una cartella nuova e avvia avvia_jarvis.bat. Omissione della memoria vuota nei prompt, dati e impostazioni conservati. Nessun nuovo componente quota. Test Windows, pacchetto estratto e avvio/chiusura UI verificati; GPT/account/microfono/Pavilion da collaudare. Limite20 risultati e altri rilievi ancora aperti; nessuna nuova capacità di apertura file.

Sorgenti: [b202181](https://github.com/MATRIXNEO23/jarvis/tree/b202181d435cf4ee13ffb355265e1f1a9f995963). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41749364482). SHA-256: `583bd55d1ef416b3781f6183d8ea6365f0b8761c6cf1fd614d652db832285728`.


## Build 004 — Programmi e app

[Scarica Jarvis-004.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-004.zip)

Nuova add-on Programmi e app: scegli le app consentite e un comando vocale personale; apri/avvia/lancia usano la stessa selezione. Estrai in una cartella nuova e avvia avvia_jarvis.bat; poi Impostazioni > Gestisci add-on > Programmi e app > Configura. Aggiorna elenco, spunta Consenti avvio, Salva e attiva l’add-on. Profilo e impostazioni esistenti conservati. Test Windows, pacchetto estratto e avvio/chiusura UI verificati; GPT/account/microfono/Pavilion da collaudare. Limite20 risultati e altri rilievi ancora aperti; nessuna nuova capacità di apertura file.

Sorgenti: [a1b93f3](https://github.com/MATRIXNEO23/jarvis/tree/a1b93f34ff25bd9a972ed971a432af4984366f28). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41694455705). SHA-256: `8589a789fecafd7918bdcf85cb81534ebd079b3531321a3e66042c0ff0a3c980`.


## Build 003 — Interruttori rapidi

[Scarica Jarvis-003.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-003.zip)

MIC, GPT e MEMORIA in alto a destra sono ora cliccabili e sincronizzati con le impostazioni. Estrai in una cartella nuova e avvia avvia_jarvis.bat; profilo di prova e impostazioni esistenti conservati. Test Windows, pacchetto estratto e avvio/chiusura UI verificati; GPT/account/microfono/Pavilion da collaudare. Limite20 risultati e altri rilievi ancora aperti; nessuna nuova capacità di apertura file.

Sorgenti: [2d52ba5](https://github.com/MATRIXNEO23/jarvis/tree/2d52ba540aad1f9989f588e45b7a0b0973d49e67). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41675960102). SHA-256: `9554fd5bdde7b9f8c387bfa2fed66167abb90c5c98e691f74ad5ffb6bcf119fb`.


## Build 002 — Contesto nella conversazione

[Scarica Jarvis-002.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-002.zip)

Include la correzione del contesto quando indichi una cartella nel dialogo e rispondi alla domanda successiva. Estrai in una cartella nuova e avvia avvia_jarvis.bat; profilo di prova e impostazioni esistenti conservati. Test Windows, pacchetto estratto e avvio/chiusura UI verificati; GPT/account/microfono/Pavilion da collaudare. Limite20 risultati e altri rilievi ancora aperti; nessuna nuova capacità di apertura file.

Sorgenti: [6f48ad1](https://github.com/MATRIXNEO23/jarvis/tree/6f48ad1c0c2d0d55363fb8ec5b7b1ced2ad37e5f). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41650952370). SHA-256: `43cc2258c684c8b6470263ffa43c13b5111e938ffbcbcffc59ef3c9f23617cb6`.


## Build 001 — Continuità e ricerca

[Scarica Jarvis-001.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-001.zip)

Correzioni di continuità della domanda e dei risultati nel passaggio a GPT; ricerca Windows prima del fallback e nomi naturali. Candidata per il collaudo del dialogo e della ricerca, senza nuove capacità di apertura file. Estrai in una cartella nuova e avvia avvia_jarvis.bat; poi Impostazioni > Gestisci add-on > Accesso file > Configura, Salva e Attiva. Profilo di prova separato, precedente installazione preservata. Test automatici solo Windows, archivio estratto e avvio UI verificati. Collaudo Pavilion/account/microfono reali ancora da fare; indice Windows reale e fallback verificati in CI. Nessuna ricerca web attivata da questo pacchetto.

Sorgenti: [cec4536](https://github.com/MATRIXNEO23/jarvis/tree/cec4536b0f5991cb900680ed05295245f4e04acb). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41614085149). SHA-256: `d96e90657ad67399893ef5d89a7e250da5369b64a833fd596e4d718ad3687f07`.


## Accesso file 0.1.0 — build candidata Windows (d06e233)

[Scarica Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip](https://github.com/MATRIXNEO23/jarvis/raw/main/Download/Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip)

Cartelle dei programmi da registrazioni/collegamenti Windows, percorsi del profilo corrente, ricerca locale con aiuto GPT quando necessario. Risultati nella finestra dedicata e scelte vocali. Estrai in una cartella nuova e avvia avvia_jarvis.bat; poi Impostazioni > Gestisci add-on > Accesso file > Configura, Salva e Attiva. Profilo di prova separato, precedente installazione preservata. Test automatici solo Windows, archivio estratto e avvio UI verificati. Collaudo Pavilion/account/microfono reali ancora da fare; indice Windows reale e fallback verificati in CI. Nessuna ricerca web attivata da questo pacchetto.

Sorgenti: [d06e233](https://github.com/MATRIXNEO23/jarvis/tree/d06e233a98e4ea5b4e99a9d296b9570ce0c92d86). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41350638557). SHA-256: `ac130883d32518b430737f8f3d767a16a56e3cad9b3ae32f37d8f20799f42699`.


## Accesso file 0.1.0 — build candidata Windows (950f655)

[Scarica Jarvis-Accesso-File-0.1.0-20261101-950f655.zip](https://github.com/MATRIXNEO23/jarvis/raw/main/Download/Jarvis-Accesso-File-0.1.0-20261101-950f655.zip)

Ricerca, cartelle consentite con spunte, lettura senza modifica e integrazione voce/testo/GPT. Elenchi solo in chat e conferme vocali brevi. Estrai in una cartella nuova e avvia avvia_jarvis.bat; poi Impostazioni > Gestisci add-on > Accesso file > Configura, Salva e Attiva. Profilo di prova separato, precedente installazione preservata. Test automatici solo Windows, archivio estratto e avvio UI verificati. Collaudo PC/account/microfono reali ancora da fare; indice Windows non disponibile nel runner, fallback verificato.

Sorgenti: [950f655](https://github.com/MATRIXNEO23/jarvis/tree/950f655a6fc0db25f2eb4c66d47507cf9b0d3038). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41330921134). SHA-256: `85c7879346824198e1a54939b0b44faae7d0813b004b152e95b788e79160539f`.


## Accesso file 0.1.0 — build candidata Windows (755f988)

[Scarica Jarvis-Accesso-File-0.1.0-20261101-755f988.zip](https://github.com/MATRIXNEO23/jarvis/raw/main/Download/Jarvis-Accesso-File-0.1.0-20261101-755f988.zip)

Ricerca, cartelle consentite con spunte, lettura senza modifica e integrazione voce/testo/GPT. Elenchi solo in chat e conferme vocali brevi. Estrai in una cartella nuova e avvia avvia_jarvis.bat; poi Impostazioni > Gestisci add-on > Accesso file > Configura, Salva e Attiva. Profilo di prova separato, precedente installazione preservata. Test automatici solo Windows, archivio estratto e avvio UI verificati. Collaudo PC/account/microfono reali ancora da fare; indice Windows non disponibile nel runner, fallback verificato.

Sorgenti: [755f988](https://github.com/MATRIXNEO23/jarvis/tree/755f988437b214c035c23c7db5f73f6c38c2ffde). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41330559676). SHA-256: `98c8ccaaa7ac133e24b0f40860e5ec470893ecedb3978660f36cefed1ae53de9`.


## Accesso file 0.1.0 — build candidata Windows (7298fb6)

[Scarica Jarvis-Accesso-File-0.1.0-20261101-7298fb6.zip](https://github.com/MATRIXNEO23/jarvis/raw/main/Download/Jarvis-Accesso-File-0.1.0-20261101-7298fb6.zip)

Ricerca, cartelle consentite con spunte, lettura senza modifica e integrazione voce/testo/GPT. Estrai in una cartella nuova e avvia avvia_jarvis.bat; poi Impostazioni > Gestisci add-on > Accesso file > Configura, Salva e Attiva. Profilo di prova separato, precedente installazione preservata. Test automatici solo Windows, archivio estratto e avvio UI verificati. Collaudo PC/account/microfono reali ancora da fare; indice Windows non disponibile nel runner, fallback verificato.

Sorgenti: [7298fb6](https://github.com/MATRIXNEO23/jarvis/tree/7298fb632cd9b72386fd7a30f469b307ce7e6fa5). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41322290359). SHA-256: `72c6d57a9a258fe7c875cfdc8646bc4ddf5b75417aa748bb5d4d4b7ef3e96755`.


## Accesso file 0.1.0 — build candidata Windows (63bfd04)

[Scarica Jarvis-Accesso-File-0.1.0-20261101-63bfd04.zip](https://github.com/MATRIXNEO23/jarvis/raw/main/Download/Jarvis-Accesso-File-0.1.0-20261101-63bfd04.zip)

Ricerca, cartelle consentite con spunte, lettura senza modifica e integrazione voce/testo/GPT. Estrai in una cartella nuova e avvia avvia_jarvis.bat; poi Impostazioni > Gestisci add-on > Accesso file > Configura, Salva e Attiva. Profilo di prova separato, precedente installazione preservata. Test automatici solo Windows, archivio estratto e avvio UI verificati. Collaudo PC/account/microfono reali ancora da fare; indice Windows non disponibile nel runner, fallback verificato.

Sorgenti: [63bfd04](https://github.com/MATRIXNEO23/jarvis/tree/63bfd048032f51ff5d52f87a14060f27fad720c0). [Prove Windows](https://github.com/MATRIXNEO23/jarvis/actions/runs/41321679044). SHA-256: `43867ec86094eac5c7e9ef6f03674d9c5ad19cd6736f3594638eadfb85d6db0e`.


# Jarvis: Timer audio Fix 2 - 31/10/2026

**[SCARICA JARVIS COMPLETO CON FIX AUDIO TIMER](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Fix2-20261031.zip)**

Versione completa per Windows 10 con un solo launcher `avvia_jarvis.bat`. Il timer e' una finestra indipendente con cifre digitali, START, PAUSA, STOP, RESET e durata modificabile. Comandi locali e vocali: 'timer 10 minuti', 'pausa timer', 'riprendi timer', 'stop timer' e 'quanto manca al timer'. Cinque suonerie offline con anteprima, volume e ripetizione nelle impostazioni gia' esistenti, ora organizzate per categorie. **Fix 2 audio:** corretta costante SND_SYNC inesistente; riproduzione WAV da file con ripiego in memoria, bip alternativo Windows selezionabile e messaggi di stato visibili sia nel tasto Prova che alla scadenza del timer. I comandi originali, Telegram, memoria, progetti, microfono, add-on e GPT esterno non sono stati rimossi.

Estrai in una cartella nuova e avvia `avvia_jarvis.bat`. I dati del profilo di prova restano isolati. I test automatici Windows/Linux sono superati; il collaudo reale del timer e dei dispositivi audio sul Pavilion e' ancora necessario. Sorgente e modifiche nella PR #32.

---

# Jarvis: Timer con audio corretto - 31/10/2026

**[SCARICA JARVIS COMPLETO CON FIX AUDIO TIMER](./Jarvis-Timer-Audio-Corretto-20261031.zip)**

Versione completa per Windows 10 con un solo launcher `avvia_jarvis.bat`. Il timer e' una finestra indipendente con cifre digitali, START, PAUSA, STOP, RESET e durata modificabile. Comandi locali e vocali: 'timer 10 minuti', 'pausa timer', 'riprendi timer', 'stop timer' e 'quanto manca al timer'. Cinque suonerie offline con anteprima, volume e ripetizione nelle impostazioni gia' esistenti, ora organizzate per categorie. **Fix audio:** riproduzione WAV da file con ripiego in memoria, bip alternativo Windows selezionabile e messaggi di stato visibili sia nel tasto Prova che alla scadenza del timer. I comandi originali, Telegram, memoria, progetti, microfono, add-on e GPT esterno non sono stati rimossi.

Estrai in una cartella nuova e avvia `avvia_jarvis.bat`. I dati del profilo di prova restano isolati. I test automatici Windows/Linux sono superati; il collaudo reale del timer e dei dispositivi audio sul Pavilion e' ancora necessario. Sorgente e modifiche nella PR #32.

---

# Jarvis: Timer vocale e Impostazioni - 31/10/2026

**[SCARICA JARVIS CON TIMER E IMPOSTAZIONI RIORDINATE](./Jarvis-Timer-Impostazioni-20261031.zip)**

Versione completa per Windows 10 con un solo launcher `avvia_jarvis.bat`. Il timer e' una finestra indipendente con cifre digitali, START, PAUSA, STOP, RESET e durata modificabile. Comandi locali e vocali: 'timer 10 minuti', 'pausa timer', 'riprendi timer', 'stop timer' e 'quanto manca al timer'. Cinque suonerie offline con anteprima, volume e ripetizione nelle impostazioni gia' esistenti, ora organizzate per categorie. I comandi originali, Telegram, memoria, progetti, microfono, add-on e GPT esterno non sono stati rimossi.

Estrai in una cartella nuova e avvia `avvia_jarvis.bat`. I dati del profilo di prova restano isolati. I test automatici Windows/Linux sono superati; il collaudo reale del timer e dei dispositivi audio sul Pavilion e' ancora necessario. Sorgente e modifiche nella PR #32.

---

# Ultima build Jarvis — timer vocale e impostazioni (31/10/2026)

**[SCARICA JARVIS COMPLETO — TIMER VOCALE + HUD](./Jarvis-Timer-Vocale-20261031.zip)**

**File esatto:** `Jarvis-Timer-Vocale-20261031.zip`. Versione completa di prova Windows 10 in ZIP di sorgenti Python (non .exe); un solo `avvia_jarvis.bat`. Contiene il Jarvis HUD corretto, GPT esterno, voce, documenti, memoria, progetti, Telegram, add-on e tutti i controlli precedenti.

**Nuovo:** timer locale apribile dicendo «timer» e avviabile con «timer dieci minuti». Popup digitale separato con Start, Pausa, Stop, Reset e regolazione manuale ore/minuti/secondi. Quattro suonerie offline con prova, volume e ripetizione **dentro le impostazioni esistenti**, ora più navigabili senza rimuovere alcuna funzione.

Estrarre in **cartella nuova** e avviare `avvia_jarvis.bat`. Profilo dati sperimentale separato, account GPT e Telegram reali quando connessi. Test automatici Windows e Ubuntu 4/4 PASS; collaudo di microfono e suoni sul Pavilion ancora necessario. Codice su PR #33 separata dal ramo main.

[Documentazione timer](https://github.com/MATRIXNEO23/jarvis/blob/feature/timer-popup-settings-20261031/docs/TIMER_POPUP_E_SUONERIE.md)

---

# Download — ultima build completa di Jarvis (31/10/2026)

## Jarvis HUD Riferimento — interfaccia corretta

**Nome esatto del file:** `Jarvis-HUD-Riferimento-20261031.zip`

**[Scarica Jarvis-HUD-Riferimento-20261031.zip](./Jarvis-HUD-Riferimento-20261031.zip)**  
[Visualizza il file nella cartella Download](./Jarvis-HUD-Riferimento-20261031.zip) · [Revisione grafica PR #31](https://github.com/MATRIXNEO23/jarvis/pull/31)

Questa è la **versione completa di prova** per Windows 10 (sorgenti Python e script di avvio, non un file `.exe`). Comprende il programma Jarvis con GPT esterno, riconoscimento vocale, documenti, progetti, add-on e Telegram.

**Correzioni rispetto alla build precedente:**
- Interfaccia scura blu/ciano ispirata alla seconda immagine di riferimento.
- Autodiagnosi nascosta quando inattiva; durante il controllo compare una barra scura discreta con annullamento.
- Riquadri **CPU, RAM, Disco C e Rete** con larghezze e allineamenti uniformi.
- Colori che indicano ascolto e parlato **solo nel nucleo centrale**; gli anelli esterni mantengono il blu/ciano.
- **Un solo launcher:** `avvia_jarvis.bat`. Nessun doppio launcher di prova.
- Telegram conserva massimo **50 messaggi locali per contatto** e passa al GPT solo i **4 messaggi precedenti**, senza riassunti.

**Come provarla:** chiudi Jarvis, estrai la ZIP in una cartella nuova senza sovrascrivere la precedente e avvia `avvia_jarvis.bat`. Il profilo di prova mantiene i dati separati; il microfono è predisposto attivo all'avvio se modello vocale e dispositivo sono disponibili. Telegram, quando abilitato, usa l'account reale.

**Verifiche:** test automatici Windows e Ubuntu superati. Il collaudo grafico e funzionale sul Pavilion resta da effettuare. La PR #31 non è stata integrata nel codice `main`: nella cartella `Download` è pubblicata la ZIP già assemblata.

---

# Scarica Jarvis per Windows 10 — HP Pavilion

## NOVITÀ SPERIMENTALE — GESTIONE ADD-ON E CATALOGO GPT (31/10/2026)

**[Scarica Jarvis-AddOn-Registro-GPT-Test.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-AddOn-Registro-GPT-Test.zip)**

Questa build di prova comprende tutte le funzioni dei rami Telegram (selezione contatti, invio OGG/Opus manuale e con conferma vocale) e del registro delle capacità GPT esterno, più un vero **pannello Gestisci add-on** con installazione, aggiornamento, attivazione, disattivazione, rimozione, approvazioni persistenti e aggiornamento del catalogo a ogni richiesta. Anche il campo testuale di Jarvis usa ora il dispatcher autorizzato per le richieste operative brevi.

Gli add-on `.jaddon` sono **file dichiarativi senza codice eseguibile**, limitati per ora a tre azioni locali in sola lettura già approvate: `system.status`, `downloads.list` e `history.list`. Le future capacità che richiedono esecuzione di nuovo codice dovranno essere implementate come handler revisionati; un file add-on da solo non può introdurre processi o permessi. L'archivio include `examples/addons/DiagnosticaSistema.jaddon` **non installato né abilitato automaticamente**.

Codice e test sul [ramo di sviluppo separato](https://github.com/MATRIXNEO23/jarvis/tree/feature/trusted-addon-lifecycle-gpt), [PR draft #28](https://github.com/MATRIXNEO23/jarvis/pull/28). [Guida e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/trusted-addon-lifecycle-gpt/docs/ADDON_LIFECYCLE.md).

Test Python/Node automatici [4/4 PASS su Windows e Ubuntu](https://github.com/MATRIXNEO23/jarvis/actions/runs/41200751953). ZIP pubblicato dal commit sperimentale `dc77a7c256466688dc13d93ed290a6d7dd6f7e63`, dopo un secondo recheck della suite, e verificato con manifest SHA-256. **Non collaudato realmente sul Pavilion né con invii Telegram reali**. La pubblicazione non aggiorna l'installazione principale e non sostituisce le vecchie build. Prima di provarla, chiudi Jarvis, salva una copia di `%LOCALAPPDATA%\\Jarvis`, estrai in una cartella diversa; se Defender rileva una minaccia, non bypassare i controlli.

---

## NOVITÀ DI PROVA — TELEGRAM MULTI-CONTATTO E MESSAGGI VOCALI (31/10/2026)

**[Scarica Jarvis-Telegram-Contatti-Vocali-Test.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Telegram-Contatti-Vocali-Test.zip)**

Include selezione dei contatti reali tramite **spunte**, risposte automatiche per i soli contatti autorizzati, pulsante **Invia messaggio vocale** (destinatario e testo + conferma), e comando «Jarvis, manda un messaggio a Nico» con dettatura del contenuto e conferma. Testo scritto o dettato viene trasformato localmente in OGG/Opus (Windows SAPI e FFmpeg) e inviato come nota vocale Telegram. Nessun modello locale aggiuntivo, nessuna API GPT nuova.

Codice nel [ramo isolato](https://github.com/MATRIXNEO23/jarvis/tree/feature/telegram-multicontact-voice-outbound), [PR draft #26](https://github.com/MATRIXNEO23/jarvis/pull/26); non integrato nel programma principale. Archivio separato dalle versioni precedenti. [Istruzioni e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/telegram-multicontact-voice-outbound/docs/TELEGRAM_CONTATTI_INVIO_VOCALI.md).

Il pacchetto è stato creato da una revisione fissata dopo controllo dei test automatici (senza invii reali) e verifica del contenuto SHA-256. **Non è ancora collaudato sul tuo Pavilion con un destinatario Telegram reale.** Prima di provarlo, chiudi Jarvis, salva una copia di `%LOCALAPPDATA%\\Jarvis` ed estrailo in una cartella distinta. Se Windows Defender lo segnala, interrompi la prova, senza disattivare la protezione e senza creare esclusioni. Le credenziali Telegram e gli archivi esistenti non vanno cancellati.

---

## NUOVA PROVA — AUTODIAGNOSI CON EVIDENZE RUNTIME E GPT ESTERNO (31/10/2026)

**[Scarica Jarvis-Diagnostica-Runtime-GPT.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Diagnostica-Runtime-GPT.zip)** — archivio pubblicato e verificato in `Download`, senza sostituire le versioni precedenti.

Questa è una versione di prova isolata, basata sulla diagnostica visibile precedente; il codice **non** è integrato automaticamente in `main`. [Modifiche e PR draft #25](https://github.com/MATRIXNEO23/jarvis/pull/25). [CI Windows/Linux 4/4 SUCCESS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41192534100) sui sorgenti `d6578989459326bed6ddba590f0c21d1d0e75702`.

**Architettura reale:** nessun modello locale, GPT esterno tramite Sign in with ChatGPT. Il piccolo motore Windows analizza i sorgenti e raccoglie stati passivi verificabili: bridge/SDK GPT, stream microfono, motore locale, archivio progetti, conteggi anonimi degli errori osservati nell'istanza. Mostra il rapporto anche offline. Solo con consenso trasmette al modello esterno un riepilogo ristretto e categoriale, per consigli tecnici; nessuna patch né comando eseguito automaticamente. Presenza di un componente NON significa collaudo funzionale.

**Collaudo sul Pavilion ancora da svolgere.** Conservare la vecchia installazione, fare backup di `%LOCALAPPDATA%\\Jarvis` e provare la ZIP in una cartella distinta, con una sola istanza aperta. Premere `⋯ → Autodiagnosi Jarvis`, controllare la sezione `Stato locale osservato`; poi chiedere «Jarvis, valuta la diagnosi con GPT» e verificare il consenso prima dell'invio. [Guida dettagliata sul ramo](https://github.com/MATRIXNEO23/jarvis/blob/feature/diagnostic-runtime-evidence-external-gpt/docs/DIAGNOSTICA_RUNTIME_SIGN_IN_GPT.md).

**Avviso antivirus invariato:** precedente segnalazione Defender `Trojan:Script/Wacatac.B!ml` non risolta; CI verde non certifica sicurezza della ZIP. Se Defender blocca, interrompere e non creare esclusioni, non disattivare la protezione.

---

## NUOVA BUILD DI TEST — DIAGNOSTICA VISIBILE, RECUPERO E VOCE (31/10/2026)

**[SCARICA Jarvis-Fix-Diagnostica-Visibile.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Fix-Diagnostica-Visibile.zip)**

Pacchetto verificato nella cartella `Download` (321915 byte), sorgenti `fa372c2ffdf9210642c9febd973068c9bac0af9b` sul ramo `fix/diagnostic-visible-progress-recovery-voice`, PR draft [#24](https://github.com/MATRIXNEO23/jarvis/pull/24). Include `SOURCE-COMMIT.txt` e SHA-256 di ogni sorgente nello ZIP. [Test automatici Windows e Ubuntu](https://github.com/MATRIXNEO23/jarvis/actions/runs/41190775816). Il ramo di codice resta separato da `main` e le ZIP precedenti sono intatte.

**Bug reale segnalato sul Pavilion:** il pulsante Autodiagnosi riportava «sta già eseguendo» ma senza progressi visibili né risultato; a voce non partiva. Dal codice erano assenti timeout e progressi; un'eccezione non prevista nel worker poteva lasciare il blocco permanente. Una conferma di documento poteva inoltre avere priorità sul comando vocale. Il ciclo eventi GUI poteva smettere di programmare i successivi controlli se un gestore generava un errore.

**Correzioni:** progresso visibile sul pannello principale `Autodiagnosi: inventario/sintassi/consigli X/Y (secondi)`, barra di completamento e pulsante **Annulla**. Il rapporto rimane in console. Dopo 12 secondi senza avanzamento compare avviso, dopo 120 secondi viene liberata la GUI, con risultati tardivi ignorati; il vecchio worker non è forzatamente terminato. Errori imprevisti mostrano il tipo di errore e sbloccano il controllo. Il watchdog è indipendente dal ciclo generale. Comandi vocali più robusti per `auto diagnosi`, `auto-diagnosi`, `l'autodiagnosi`; autodiagnosi locale prioritaria rispetto a GPT e alle vecchie conferme documenti. Una nuova scansione invalida il vecchio rapporto prima di valutare suggerimenti col modello esterno.

**Prova locale:** chiudere tutte le vecchie istanze; backup di tutto `%LOCALAPPDATA%\Jarvis`; estrarre nella nuova cartella e avviare una sola versione. Premere `⋯ → Autodiagnosi Jarvis`; devono apparire i progressi e poi il rapporto o un errore preciso. Provare `Annulla`. A voce dire «Jarvis, fai un'autodiagnosi» e controllare nella console il testo realmente trascritto. Il collaudo fisico della build nuova NON è ancora stato eseguito.

**Avviso antivirus ancora irrisolto:** una ZIP precedente è stata segnalata da Defender come `Trojan:Script/Wacatac.B!ml`. Nessuna verifica antivirus indipendente è stata effettuata sulla ZIP nuova: una CI verde e un manifest non dimostrano assenza di malware. Non creare esclusioni, non disattivare Defender, non consentire rilevazioni per eseguire il programma. Se Defender blocca il file, sospendere il collaudo.

---

## NUOVA VERSIONE — AUTODIAGNOSI IBRIDA: MOTORE LOCALE + GPT ESTERNO (31/10/2026)

**[SCARICA Jarvis-Autodiagnosi-Ibrida-GPT.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Autodiagnosi-Ibrida-GPT.zip)**

Pacchetto realmente presente nella cartella `Download` (313324 byte), creato da sorgente pin `0a8d9769e6858f7f571d480d0261aba16924b4a4` sul ramo `feature/local-audit-external-gpt-review` e completo di manifest SHA-256. [CI Windows/Linux: 4/4 SUCCESS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41189465744); [pubblicazione ZIP SUCCESS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41189529881). [PR #23 sperimentale](https://github.com/MATRIXNEO23/jarvis/pull/23), codice non integrato nel ramo main. Versioni precedenti conservate.

**Perché:** Jarvis ha un piccolo motore Python sul PC ma ragiona con un GPT esterno. Non è GPT a poter leggere il disco di Windows: è il motore locale che analizza il proprio codice in sola lettura e produce un rapporto. Una volta disponibile, l'utente può chiedere **«Jarvis, valuta la diagnosi con GPT»** oppure **«Jarvis, fai un'autodiagnosi del tuo funzionamento e proponi eventuali fix»**; dopo una domanda di consenso, Jarvis invia al collegamento GPT già autorizzato **solo** dati tecnici ridotti (massimo 6 segnali AST, file relativi, righe, verifiche da eseguire, e conteggi anonimi fino alle ultime 20 operazioni). GPT produce suggerimenti senza autorizzazioni operative. Rifiutando il consenso, niente viene inviato, il rapporto locale rimane.

**Limiti:** non è un modello locale; non introduce API a consumo, modelli nuovi o servizi a pagamento. Non invia codice sorgente integrale, percorsi personali, log, credenziali, file privati, messaggi Telegram o contenuti dei progetti. Gli indicatori disponibili e i conteggi non attestano che le funzioni lavorino correttamente; GPT non può testare il PC e non è autorizzato a modificare file. I log di runtime NON sono ancora analizzati. Guida nel ramo: `docs/AUTODIAGNOSI_IBRIDA_LOCALE_GPT.md`.

**Collaudo reale sul Pavilion ancora da svolgere.** Prima backup completo di `%LOCALAPPDATA%\Jarvis`; decomprimere in nuova cartella, chiudere la versione precedente e avviare una sola istanza.

**Avviso antivirus irrisolto:** un precedente ZIP è stato segnalato da Microsoft Defender come `Trojan:Script/Wacatac.B!ml`. La nuova ZIP non ha verifica antivirus indipendente; CI e manifest non certificano assenza di malware. Se Defender la blocca, NON disattivare l'antivirus né autorizzarne l'esecuzione.

---

## FIX AUTODIAGNOSI — RICHIESTE VOCALI E PULSANTE DEDICATO (31/10/2026)

**[SCARICA Jarvis-Fix-Autodiagnosi-Vocale.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Fix-Autodiagnosi-Vocale.zip)**

Pacchetto verificato nella cartella `Download` (304402 byte), revision `4154746df5e160c9ad906864d23239463a1c1d64` del ramo `fix/self-diagnostic-intent-route-and-button`. [PR #22](https://github.com/MATRIXNEO23/jarvis/pull/22) ancora isolata, senza merge su `main`. [Test CI Windows/Linux 4/4 SUCCESS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41186793779); [workflow di pubblicazione SUCCESS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41186849663).

**Problema corretto dopo foto dell'utente:** chiedendo «Jarvis, fai un'autodiagnosi del tuo funzionamento e proponi eventuali fix» Jarvis rispondeva con testo generico del GPT che diceva di non poter accedere al codice o ai log. Invece la diagnosi deve avvenire localmente, prima di chiedere a GPT: ora vengono riconosciute le frasi composte e anche il pulsante «Chiedi a GPT» passa prima dal controllo diagnostico. In più è disponibile il pulsante **Autodiagnosi Jarvis** sotto il menu secondario `⋯`, per evitare ambiguità della voce. Il rapporto indica file, righe, priorità e prove da eseguire. I vecchi comandi, tra cui «analizza il tuo codice», sono preservati.

**Limite reale:** il modulo legge i sorgenti Python installati e dà possibili consigli di manutenzione; non legge i log runtime, non esegue i sorgenti o test e non può garantire da solo il corretto funzionamento. Rimane in sola lettura e non modifica il programma. Il collaudo reale sul Pavilion resta da fare.

**Avviso sicurezza ancora aperto:** un precedente ZIP è stato segnalato da Windows Defender come `Trojan:Script/Wacatac.B!ml`. Non è stata verificata con uno scanner indipendente l'assenza di malware nel nuovo pacchetto. Se Defender lo blocca, non disattivarlo né forzare l'esecuzione. Fare backup di `%LOCALAPPDATA%\Jarvis`, estrarre la nuova build in una cartella distinta e avviare una sola istanza alla volta.

---

## NUOVA BUILD DI TEST — AUTODIAGNOSI E CONSIGLI DI MIGLIORAMENTO (31/10/2026)

**[SCARICA Jarvis-Autodiagnosi-e-Miglioramenti.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Autodiagnosi-e-Miglioramenti.zip)**

Pacchetto realmente presente in `Download` (300368 byte), completo di sorgenti e manifest SHA-256; commit `aeb87d25dbad6559d903ac46754d51ddfcae9cd3` nel ramo `feature/self-diagnostic-improvement-advice`, [PR #21 sperimentale](https://github.com/MATRIXNEO23/jarvis/pull/21), senza merge del codice su `main`. [Test automatici Windows/Linux superati](https://github.com/MATRIXNEO23/jarvis/actions/runs/41185960295) sul codice della nuova autodiagnosi; [pubblicazione ZIP riuscita](https://github.com/MATRIXNEO23/jarvis/actions/runs/41186056668).

**Novità:** «Jarvis, fai un'autodiagnosi», «Jarvis, come potresti migliorarti?», «Jarvis, suggerisci miglioramenti al tuo codice», «Jarvis, analizza self_diagnostics.py». La scansione di sorgenti Python in sola lettura, senza eseguirli, aggiunge fino a 8 proposte concrete con priorità, file, riga, osservazione e test da fare. Valuta funzioni molto lunghe o complicate, gestione eccezioni silenziosa, moduli estesi e uso di shell=True. Leggi e copia il rapporto dalla cronologia di Jarvis; la voce pronuncia il primo suggerimento. Le segnalazioni **non sono bug dimostrati**, e la diagnosi non garantisce che le funzioni lavorino correttamente. Nessuna automodifica o accesso a dati personali, account, credenziali o Internet.

**Collaudo reale sul Pavilion ancora da effettuare**, come concordato. Prima fare backup completo di `%LOCALAPPDATA%\Jarvis`, estrarre in una cartella distinta e usare una sola versione per volta. Le ZIP precedenti e i dati del PC non sono stati toccati.

**Avviso antivirus ancora aperto:** un precedente pacchetto è stato segnalato da Defender come `Trojan:Script/Wacatac.B!ml`. Il nuovo ZIP non ha una scansione antivirus indipendente; test e manifest non ne certificano l'innocuità. Se Defender lo blocca, non forzare l'esecuzione o disattivare la protezione.

---

## NUOVA BUILD DI TEST — RECUPERO DOCUMENTI BLOCCO NOTE (31/10/2026)

**[SCARICA Jarvis-Recupero-Documenti.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Recupero-Documenti.zip)**

Pacchetto confermato presente nella cartella `Download` (293782 byte), sorgente nel commit `9fb43205c2c395e4fd6ed2fada089b13e523be12` sul ramo `fix/notepad-stale-session-recovery`, [PR draft #20](https://github.com/MATRIXNEO23/jarvis/pull/20) non unita a `main`. [Test automatici Windows e Linux](https://github.com/MATRIXNEO23/jarvis/actions/runs/41185338882) superati per i nuovi controlli; la documentazione successiva non cambia il codice.

**Correzione mirata:** quando un documento Blocco note controllato da Jarvis è stato davvero chiuso manualmente, Jarvis riconosce la scomparsa del processo/finestra, dimentica il suo vecchio identificatore e le conferme di salvataggio rimaste in sospeso, e consente un nuovo documento di testo. Se la finestra è **ancora aperta** o Windows non può accertarne lo stato, non dimentica la sessione né rischia il testo non salvato. Vecchi file non cancellati né sovrascritti. Il controllo è ora eseguito prima dei comandi voce/chat e durante il polling leggero. Documentazione: `docs/RECUPERO_BLOCCO_NOTE_CHIUSO.md`.

**Collaudo fisico sul Pavilion non eseguito; da effettuare quando l'utente proverà la build.** Prima fare backup completo di `%LOCALAPPDATA%\Jarvis`, estrarre in una cartella nuova e non eseguire due versioni contemporaneamente.

**Avviso antivirus NON risolto:** un precedente ZIP di Jarvis è stato segnalato da Microsoft Defender come `Trojan:Script/Wacatac.B!ml`. Questa build non è stata certificata antivirus. La CI e il manifest dei sorgenti non costituiscono prova di assenza di malware. Se Defender blocca il download, NON disattivarlo né forzare l'esecuzione.

---

## NUOVA BUILD DI TEST — ITALIANO NATURALE E IRRIVERENZA (31/10/2026)

**[SCARICA Jarvis-Conversazione-Naturale.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Conversazione-Naturale.zip)**

Pacchetto effettivamente presente in `Download`, sorgente `fa4b03472dc47107af8dd69d29a3693ccd5988d4`, codice testato nelle [CI Windows e Linux 4/4 SUCCESS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41183303442). [PR #19 sperimentale](https://github.com/MATRIXNEO23/jarvis/pull/19), non integrata in `main`. Sono conservate le ZIP precedenti.

**Richiesta esatta:** italiano naturale, risposte sintetiche in conversazione, procedure complete quando richieste, ironia/sarcasmo intelligente e **IRRIVERENZA**, non deferenza/riverenza. Battute solo quando pertinenti, non su problemi delicati. Il tono non altera contenuti di documenti o autorizzazioni a eseguire azioni. Risposte GPT procedurali più lunghe e sintesi vocale a blocchi per non tagliarle dopo 600 caratteri. Documentazione nel ramo: `docs/QUALITA_CONVERSAZIONE_V1.md`.

**Colllaudo reale sul Pavilion rimandato su richiesta dell'utente.** Fare prima backup completo di `%LOCALAPPDATA%\Jarvis`, estrarre in cartella nuova e non avviare contemporaneamente due versioni.

**AVVERTENZA ANTIVIRUS:** il precedente rilevamento Defender `Trojan:Script/Wacatac.B!ml` non è stato risolto; il nuovo ZIP non ha certificazione antivirus. I test CI e il manifest SHA-256 verificano la riproducibilità, non la sicurezza malware. Se Defender lo blocca, non disabilitare la protezione né forzarne l'esecuzione.

---

## NUOVA VERSIONE — MEMORIA AFFIDABILE E STORICO VERIFICABILE (31/10/2026)

**[SCARICA Jarvis-Memoria-Affidabile.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Memoria-Affidabile.zip)**

Il pacchetto ZIP è realmente disponibile in `Download`; include tutti i file di programma e test (sorgente Python con `avvia_jarvis.bat`, non EXE compilato), il commit sorgente e un manifest SHA-256 per ogni file incluso. Deriva dal commit testato `15658a1ad140c60247502052d634173f3ad184c5` nel ramo `feature/memory-provenance-and-separation`. [CI Windows e Linux: 4/4 SUCCESS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41182354475). [PR #18 in sola prova](https://github.com/MATRIXNEO23/jarvis/pull/18), senza merge in main.

**Modifiche mirate alla memoria:**
- Preferenze in `%LOCALAPPDATA%\Jarvis\jarvis_preferences.sqlite3`, SOLO dopo conferma esplicita; non dedotte dalle conversazioni. «Jarvis, ricorda che preferisco risposte brevi» richiede «confermo».
- Progetti, file, continuità e passi nel loro database `jarvis_workspaces.sqlite3` e cartelle `projects\<UUID>`, intatti e separati.
- Conversazione Second Brain nel precedente `second_brain.sqlite3`; i ricordi NON vengono eseguiti come comandi.
- Nuova cronologia `jarvis_actions.sqlite3`: requested, running, reported, verified, failed, interrupted, uncertain. Successi riferiti da processi lanciati non equivalgono alla prova che una finestra funziona; TXT salvati verificati solo quando esistono sul disco. In caso di arresto le operazioni in sospeso diventano interrupted senza replay.
- Vecchi record e receipt conservati; le azioni pregresse senza prova classificabile diventano **legacy_unassessed / reported_action**, non verified. Snapshot dei progetti aggiornati alla versione 2 in modo additivo, senza cancellazione dati.
- Guida: [MEMORIA_AFFIDABILE_V1.md](https://github.com/MATRIXNEO23/jarvis/blob/feature/memory-provenance-and-separation/docs/MEMORIA_AFFIDABILE_V1.md).

**Collaudo fisico rimandato su richiesta dell'utente.** Prima di avviare una versione nuova, fare backup COMPLETO di `%LOCALAPPDATA%\Jarvis`, chiudere ogni istanza precedente ed estrarre lo ZIP in una cartella diversa. La memoria del PC non è stata modificata dalla pubblicazione.

**AVVERTENZA ANTIVIRUS ANCORA APERTA:** un pacchetto Jarvis precedente è stato segnalato da Defender come `Trojan:Script/Wacatac.B!ml`. Questa ZIP non è stata certificata da una scansione antivirus indipendente; test CI e manifest non provano l'assenza di malware. Non disattivare Defender né forzare l'esecuzione di un file segnalato. Se il download è bloccato, interrompere il collaudo. Le ZIP precedenti sono state conservate.

---

## NUOVA VERSIONE DI TEST — COMPRENSIONE DEL CONTESTO (31/10/2026)

**[SCARICA Jarvis-Contesto-e-Risposte-Brevi.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Contesto-e-Risposte-Brevi.zip)**

Pacchetto presente fisicamente nella cartella `Download` della repository, tratto dal commit `eaae39fbb21fa75294221a1363300cda250c34da` su `feature/contextual-followups-and-project-references`. [4/4 test automatici Windows e Linux superati](https://github.com/MATRIXNEO23/jarvis/actions/runs/41181339526). [PR isolata #17](https://github.com/MATRIXNEO23/jarvis/pull/17), non integrata nel branch main.

**Solo miglioramento del contesto:** risposte brevi associate alla domanda precedente, niente «sì/no» trattati come nomi di progetto, riferimento «questo progetto» al solo progetto selezionato, un unico chiarimento concreto quando il riferimento è mancante, limiti alle azioni proposte da GPT dopo un «sì» isolato. Conservate le funzioni precedenti (progetti, memoria automatica, Telegram, diagnostica in sola lettura).

**Sicurezza:** il precedente ZIP di Jarvis è stato segnalato da Microsoft Defender come `Trojan:Script/Wacatac.B!ml`. Questa nuova ZIP **non è stata certificata antivirus**; la segnalazione precedente non è stata risolta. Non disattivare Defender, non creare esclusioni e non autorizzare file segnalati per eseguirli. La pubblicazione in GitHub non garantisce sicurezza.

**Installazione prudente solo dopo verifica antivirus:** chiudi Jarvis; salva un backup completo di `%LOCALAPPDATA%\Jarvis`; estrai in una cartella nuova senza sostituire le precedenti; avvia una sola versione per volta. Test sulla voce reale e GPT collegato ancora da eseguire sul Pavilion.

---

## NUOVO PACCHETTO SPERIMENTALE — PROGETTI E DIAGNOSTICA (31/10/2026)

**[ZIP: Jarvis-Gestione-Progetti-e-Diagnostica.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Gestione-Progetti-e-Diagnostica.zip)**

Pacchetto pubblicato su richiesta dell'utente nella cartella `Download` e verificato come file presente. Basato sul commit `468ff31f0253bb7de7929076febaa71e6329dc68` del ramo `fix/project-rename-and-discovery`. [Test automatici Windows e Linux superati](https://github.com/MATRIXNEO23/jarvis/actions/runs/41179416762). Il ramo rimane separato da `main`, nessun merge.

**Funzioni incluse:** rinomina del progetto corrente o nominato a voce e da interfaccia, senza alterare UUID e memoria; «elimina il progetto» soltanto verso un cestino logico ripristinabile e previa conferma; «ripristina il progetto ...»; elenco dei progetti salvati, incluso il cestino; autodiagnostica statica offline dei file del programma, senza leggere credenziali o modificare il codice. La diagnosi non esegue test runtime e non certifica la correttezza di ogni funzione.

**AVVISO DI SICUREZZA NON RISOLTO:** Microsoft Defender sul PC dell'utente ha segnalato il pacchetto ZIP precedente come `Trojan:Script/Wacatac.B!ml`. Non è stata effettuata una verifica antivirus indipendente sul nuovo ZIP, quindi **non è possibile dichiararlo sicuro o un falso positivo**. Non disattivare Defender, non autorizzare una rilevazione e non creare esclusioni per eseguirlo. Se viene nuovamente bloccato, conservare l'installazione precedente e fermare il collaudo. La disponibilità in download **non significa approvazione antivirus**.

Prima di ogni futuro collaudo sul Pavilion: chiudere Jarvis, backup di tutta la cartella `%LOCALAPPDATA%\Jarvis`, estrarre in una cartella nuova e non avviare insieme le due versioni.

---

## SOSPESO PER VERIFICA ANTIVIRUS — PROGETTI A VOCE E FILE SALVATI NEL PROGETTO (31 OTTOBRE 2026)

**ATTENZIONE: un utente ha segnalato un blocco «virus rilevato» durante il download. Non forzare il download, non autorizzare il file in Defender e non aggiungere esclusioni fino alla verifica del nome della minaccia. Il pacchetto resta disponibile in archivio per analisi, ma il collaudo sul Pavilion è sospeso.**

**[ARCHIVIO IN VERIFICA — NON SCARICARE PER ORA](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Progetti-Vocali-e-Salvataggio.zip)**

Questa versione è stata inserita **fisicamente** in `Download/Jarvis-Progetti-Vocali-e-Salvataggio.zip`; include le funzioni Telegram precedenti, la memoria automatica per progetti e ora il riconoscimento di comandi vocali locali come «Jarvis, crea un progetto chiamato Minecraft», «apri il progetto Minecraft», «quali progetti sono attivi» e «apri la cartella del progetto».

**Percorsi dei dati:** `%LOCALAPPDATA%\Jarvis\projects\<UUID>\` per ogni progetto; la sottocartella `files\` ospita i TXT. `PROGETTO.txt` descrive il progetto, `CONTINUITA.md` e gli altri file registrano lo stato e i passi. La directory UUID esistente non cambia, dunque non si migra né si cancella la memoria precedente.

**Documenti:** quando il progetto è attivo e il Blocco note è gestito da Jarvis, la frase «salva» crea una copia `.txt` nella sua cartella `files` con un nome basato sulla richiesta originale; il programma rimane aperto. Un secondo salvataggio dopo modifiche crea una nuova versione, non sovrascrive quella precedente. «Salva e chiudi» continua a essere distinto. Senza progetto è ancora necessario indicare cartella e nome.

**Prima prova:** chiudi Jarvis, **fai il backup di tutta `%LOCALAPPDATA%\Jarvis`**, estrai lo ZIP in **una cartella nuova** e avvia `avvia_jarvis.bat` con lo stesso account Windows. Non tenere aperta anche la versione vecchia, perché il database è condiviso.

**Verifiche:** [test Windows e Ubuntu superati](https://github.com/MATRIXNEO23/jarvis/actions/runs/41177638619); collaudo fisico su Pavilion (microfono, Blocco note, velocità HDD) ancora necessario. [PR isolata #15](https://github.com/MATRIXNEO23/jarvis/pull/15) e [guida delle funzioni](https://github.com/MATRIXNEO23/jarvis/blob/feature/voice-project-folder-documents/docs/VOICE_PROJECT_DOCUMENTS.md). Nessun merge in main.

---

## VERSIONE AGGIORNATA — MEMORIA AUTOMATICA DEI PROGETTI (31/10/2026)

**[SCARICA JARVIS CON MEMORIA AUTOMATICA — ZIP NELLA CARTELLA DOWNLOAD](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Memoria-Automatica.zip)**

**File presente nella repository:** [Download/Jarvis-Memoria-Automatica.zip](https://github.com/MATRIXNEO23/jarvis/blob/main/Download/Jarvis-Memoria-Automatica.zip) — pacchetto ZIP completo dell'HEAD testato `9ae0c269e3acd497b0310cc0a6b483a89474eaea` del ramo `feature/automatic-project-continuity`, pubblicato senza integrare il ramo in `main`. Contiene anche i fix già presenti per l'inserimento dell'API hash di Telegram.

**Novità:** ogni progetto aggiorna automaticamente `CONTINUITA.md`, `STATO.json`, `PASSI.md`, `EVENTI.jsonl` e `ARTIFATTI.md`, con avanzamenti e ricevute delle azioni; al riavvio viene recuperato il progetto selezionato e le attività non verificate risultano interrotte. La gestione completamente vocale dei progetti NON è ancora implementata.

**Installazione prudente:** chiudi Jarvis; fai prima una copia di `%LOCALAPPDATA%\Jarvis` (database, memorie, Telegram); estrai lo ZIP in una **cartella nuova**, senza sovrascrivere quella funzionante; avvia `avvia_jarvis.bat` con lo stesso utente Windows. **Non eseguire contemporaneamente la nuova versione e quella vecchia:** condividono i dati in `%LOCALAPPDATA%\Jarvis`.

**Stato:** [test automatici Windows/Linux PASS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41175634069); mancano ancora collaudo e verifica della conservazione della memoria sul Pavilion. [Dettagli tecnici nella PR #14](https://github.com/MATRIXNEO23/jarvis/pull/14).

---

## FIX TELEGRAM — INCOLLA API HASH NELLA FINESTRA PROTETTA

**[SCARICA JARVIS CON CORREZIONE API HASH TELEGRAM — ZIP](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/fix/telegram-secret-paste-dialog.zip)**

Questa versione corregge la difficoltà segnalata sul Pavilion: dopo avere inserito `API ID` in `configura_telegram.bat`, il precedente `getpass` in console non permetteva di incollare facilmente `API hash`. Ora compare una **finestra grafica con campo mascherato (asterischi)**, pulsante **Incolla**, **Cancella** e **Conferma**, con supporto a Ctrl+V. La stessa finestra viene usata per il codice di accesso e l'eventuale password in due passaggi.

**Procedura:** chiudi la configurazione precedente, estrai la nuova ZIP in una cartella diversa, lancia `configura_telegram.bat`, inserisci l'API ID nella console e premi Invio; nella nuova finestra incolla l'API hash da `my.telegram.org`, controlla che siano comparsi gli asterischi e premi Conferma. **Non condividere la credenziale in chat.** Le risposte automatiche restano **OFF** dopo la configurazione e non viene inviato nessun messaggio di prova.

Questa ZIP contiene anche l'ultima versione sperimentale con memoria per progetti, pallini orbitanti e Telegram vocale; nessun merge nella versione stabile. [Correzione isolata PR #13](https://github.com/MATRIXNEO23/jarvis/pull/13).

## ULTIMO PROTOTIPO — PROGETTI, PALLINI ORBITANTI E TELEGRAM VOCALE

**[SCARICA JARVIS CON MEMORIA PER PROGETTO E TELEGRAM — ZIP](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/project-memory-orbits-telegram.zip)**

Questa prova include la precedente grafica high fidelity con sfondo cinematico e aggiunge le funzioni approvate:

- **Un contesto per ogni progetto**: cronologia separata, ricerca indicizzata SQLite FTS5, file `CONTINUITA.md` per ogni progetto, stato modificabile esplicitamente, archivio dei progetti inattivi. Attiva **Second Brain locale** da ⚙ per salvare anche le conversazioni.
- **Pallini che orbitano attorno al reattore**: ciano per progetti attivi con nome al passaggio del mouse e apertura al clic, viola per Telegram (ricevuti/risposte), ambra per comunicazioni da riferire.
- **Telegram personale (MTProto)**: configurazione facoltativa per **un solo contatto privato**, risposte **vocali** automatiche con voce Windows SAPI in OGG/Opus, registro degli esiti ricevuto/risposto, istruzioni esplicite del tipo «Jarvis, riferisci alla mia amica che ...». Interruttore **OFF di default**, quindi nessun messaggio automatico durante i test. Sessione salvata cifrata DPAPI sul PC.
- **JARVIS più sintetico e ironico**: 1–3 frasi normalmente, approfondimenti quando li chiedi.

**Prima prova sul Pavilion:** estrai lo ZIP in **una cartella nuova**, avvia `avvia_jarvis.bat`, prova i pallini, la memoria e i file di continuità. Nessuna configurazione Telegram è obbligatoria per le funzioni locali. Per Telegram sono necessari, solo se decidi di attivarlo, il pacchetto gratuito Telethon (`installa_telegram.bat`), FFmpeg gratuito nel PATH e il tuo `api_id`/`api_hash` gratuiti da Telegram. Segui `configura_telegram.bat` per scegliere l'unico contatto, poi torna in ⚙ e attiva le risposte. **Nessun messaggio Telegram reale è stato inviato nei test automatici.**

**Attenzione:** l'integrazione Telegram richiede un collaudo controllato e consenso/informazione del contatto. Con l'opzione OFF l'app non legge né invia nuovi messaggi Telegram; la memoria di Telegram è distinta da quella privata dei progetti. Il computer deve rimanere acceso con JARVIS in esecuzione perché risponda.

[Guida completa](https://github.com/MATRIXNEO23/jarvis/blob/feature/project-memory-orbits-telegram/docs/PROJECT_MEMORY_TELEGRAM.md) · [PR sperimentale #12](https://github.com/MATRIXNEO23/jarvis/pull/12). **La versione precedente rimane disponibile. Nessun merge automatico.**

## ULTIMA PROVA — SFONDO NERO CINEMATICO COME NEL CONCEPT

**[SCARICA JARVIS CON SFONDO SCURO E CIRCUITI LUMINOSI — ZIP](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/high-fidelity-cinematic-background.zip)**

Dopo il test reale del precedente HUD High Fidelity sul Pavilion, l'utente ha mostrato una fotografia e chiesto anche lo **sfondo molto più simile al preview originale**. Questa nuova revisione sostituisce la **griglia quadrata blu diffusa** dietro al reattore e alla Terra con un fondo **quasi nero**, sottili piste elettroniche, dettagli angolari e piccoli nodi ciano. Anche i pannelli e la console sono leggermente più scuri.

**Restano invariati:** reattore JARVIS e globo animati, nucleo ciano con microfono silenzioso, arancione mentre parli e verde durante la voce, ascolto automatico all'apertura dell'app con opt-out ⚙, saluto, dialogo GPT, Second Brain, file e comandi. I circuiti sono disegnati solo alla creazione/ridimensionamento della finestra, non a ogni fotogramma. **Nessuna nuova dipendenza o costo.**

**COME PROVARE:** chiudi il vecchio Jarvis, estrai questa ZIP in **una cartella nuova** e avvia `avvia_jarvis.bat`. Non reinstallare nulla se Vosk/ChatGPT già funzionano, non cancellare `%LOCALAPPDATA%\\Jarvis` né la versione precedente. Confronta il colore dello sfondo e la ricchezza dei dettagli con il concept originario, poi verifica se ascolto e animazioni restano fluidi.

[Guida e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/high-fidelity-cinematic-background/docs/HUD_CINEMATIC_BACKGROUND.md) · [PR sperimentale #11](https://github.com/MATRIXNEO23/jarvis/pull/11).

**Il design va ancora confrontato visivamente sul Pavilion; i test CI non garantiscono la somiglianza al pixel con il concept.**

## ULTIMA VERSIONE SPERIMENTALE — HUD HIGH FIDELITY

**[SCARICA JARVIS CON INTERFACCIA PIÙ VICINA AL PREVIEW — ZIP](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/high-fidelity-reference-hud.zip)**

Questa è la revisione richiesta per avvicinare **molto di più** l'interfaccia al concept: nucleo **JARVIS più luminoso e stratificato**, Terra con ombreggiatura, continenti e luci su immagini raster generate localmente, orbite animate, cornici tecnologiche e console/chat Segoe UI con campo di inserimento, pulsante microfono e freccia di invio. I vecchi comandi locali e il pianificatore sono sempre disponibili premendo **⋯**.

La grafica è più ricca e leggermente più pesante, ma **le texture vengono calcolate una sola volta in un thread separato**, senza bloccare i comandi né usare GPU, filmati o librerie aggiuntive. Finché non sono pronte si vede il precedente reattore vettoriale. In basso trovi **CPU / RAM / DISCO C / RETE**, con dati reali o **--**, non i numeri fittizi del concept.

Restano tutte le funzioni precedenti: microfono in **Conversazione continua GPT già all'apertura dell'app** (disattivabile da ⚙), saluto iniziale secondo l'orario, conversazione continuativa, Second Brain, dettatura e comandi. Il nucleo rimane **ciano nel silenzio**, pulsa **arancione mentre parli** e **verde quando JARVIS risponde a voce**.

**COME PROVARLA:** chiudi il Jarvis vecchio, scarica questo ZIP, estrailo in **una cartella nuova** e apri `avvia_jarvis.bat`. Non reinstallare Vosk/ChatGPT se funzionano già e non cancellare la versione precedente o `%LOCALAPPDATA%\\Jarvis`. Controlla soprattutto se il risultato è visivamente più vicino al tuo preview e se sul Pavilion il carico CPU rimane accettabile. **Non è ancora collaudata fisicamente sul Pavilion**.

[Guida tecnica e criteri di prova](https://github.com/MATRIXNEO23/jarvis/blob/feature/high-fidelity-reference-hud/docs/HUD_HIGH_FIDELITY.md) · [Sviluppo isolato PR #10](https://github.com/MATRIXNEO23/jarvis/pull/10) · [Test automatici Windows/Linux](https://github.com/MATRIXNEO23/jarvis/actions/runs/41153729061).

## ULTIMA PROVA — MICROFONO SEMPRE ATTIVO E CENTRO REATTIVO ALLA VOCE

**[SCARICA JARVIS CON ASCOLTO AUTOMATICO E SALUTO VOCALE (ZIP)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/hud-speech-activity-auto-start.zip)**

Questa nuova versione sperimentale contiene tutte le funzioni del ramo precedente (dialogo continuo, personalità, Second Brain, correzioni Vosk, HUD vicino al preview) e modifica tre comportamenti richiesti:

- **Il centro resta CIANO** quando il microfono è acceso ma non stai parlando.
- **Lampeggia ARANCIONE** quando rileva la tua voce nel microfono; poi torna ciano quando smetti.
- **Lampeggia VERDE** mentre la voce Windows di JARVIS parla; il verde ha sempre la precedenza.
- **Aprendo l'applicazione** il microfono parte automaticamente in **Conversazione continua GPT**, senza «Ehi Jarvis» e senza dover premere l'ascolto. **Non** abbiamo aggiunto JARVIS all'avvio automatico di Windows.
- All'apertura, JARVIS saluta con la voce locale in base all'orario («Buongiorno», «Buonasera» o «Buonanotte, signore. Come posso esserle utile?»). Il saluto è anche visibile nella console.
- Nelle impostazioni ⚙ puoi disattivare **«Avvia Jarvis già in Conversazione continua GPT»** per i prossimi avvii; durante l'uso puoi ancora selezionare manualmente Standby o altre modalità. Nessun cambio automatico verso Standby quando apri programmi pesanti.

**Test Pavilion:** chiudi la precedente istanza di JARVIS, scarica lo ZIP, estrailo in **una cartella nuova** ed esegui `avvia_jarvis.bat`. Se Vosk e ChatGPT sono già installati e connessi, non devi aggiungere componenti. Controlla il saluto verde, il silenzio ciano, il parlato arancione e il ritorno al ciano. Poi verifica da ⚙ che Standby spenga davvero il microfono. Il rilevamento arancione usa un semplice segnale di attività: rumori forti possono occasionalmente attivarlo.

**[Test automatici Windows/Linux PASS](https://github.com/MATRIXNEO23/jarvis/actions/runs/41151683977)** · [Guida tecnica e privacy](https://github.com/MATRIXNEO23/jarvis/blob/feature/hud-speech-activity-auto-start/docs/HUD_VOICE_ACTIVITY.md) · [PR sperimentale #9](https://github.com/MATRIXNEO23/jarvis/pull/9).

**Versione non ancora collaudata fisicamente sul Pavilion.** Non sovrascrivere la versione funzionante, il modello Vosk o `%LOCALAPPDATA%\\Jarvis`. Le versioni più vecchie sotto seguono le loro precedenti impostazioni di avvio.

## NUOVA PROVA — JARVIS CONVERSA E MANTIENE IL FILO DEL DISCORSO

**[SCARICA JARVIS CON DIALOGO CONTINUO, PERSONALITÀ E HUD RINNOVATO (ZIP)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/dialogue-continuity-personality.zip)**

Questa versione sperimentale mantiene l'**interfaccia più simile al preview**, il globo animato e il nucleo ciano/arancione/verde, ma migliora anche le conversazioni: JARVIS tiene in RAM più scambi recenti, interpreta risposte che completano la domanda precedente e non perde subito le frasi pronunciate mentre GPT sta elaborando (fino a 3 in attesa). Ha inoltre un tono più naturale, professionale e discretamente ironico, ispirato all'assistente JARVIS.

**Per il test sul Pavilion:** chiudi il Jarvis attuale, scarica lo ZIP e decomprimilo in **una cartella nuova**; avvia `avvia_jarvis.bat` e seleziona manualmente **Conversazione continua GPT**. Verifica con un semplice scambio: «Scrivimi un racconto», poi alla sua richiesta di chiarimento rispondi solo «Breve e malinconico». JARVIS dovrebbe collegare le due frasi senza ripartire da zero.

**Niente nuove installazioni**, se Vosk e ChatGPT funzionano già. Memoria breve utilizzabile anche con Second Brain persistente disattivato. Microfono spento all'avvio; le azioni locali e le conferme dei file restano controllate. **Non cancellare il vecchio Jarvis o `%LOCALAPPDATA%\\Jarvis`**.

Questa versione va ancora verificata nel dialogo reale sul Pavilion. Le risposte possono comunque richiedere chiarimenti, e JARVIS non è full-duplex durante la propria voce SAPI. [Guida del dialogo e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/dialogue-continuity-personality/docs/DIALOGO_CONTINUO.md) · [PR di prova #8](https://github.com/MATRIXNEO23/jarvis/pull/8).

## ULTIMA PROVA — INTERFACCIA JARVIS COME NEL PREVIEW

**[SCARICA JARVIS HUD CON GLOBO DETTAGLIATO E REATTORE CIANO/ARANCIONE/VERDE (ZIP)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/hud-reference-redesign.zip)**

Questa è la **revisione del design richiesta dopo il confronto fotografico** tra la precedente build sul Pavilion e l'immagine concept. Il nuovo layout avvicina la schermata al preview: console/chat con schede **Console / Attività / Sistema** a sinistra, **cerchio JARVIS più ricco di anelli e luci** al centro, **Terra con continenti, luci e orbite rotanti** a destra e quattro strumenti di monitoraggio reali in basso.

**Codice colore del centro:** ciano quando Jarvis è inattivo; **arancione lampeggiante** soltanto se il microfono Vosk è realmente aperto; **verde lampeggiante** quando la sintesi vocale Windows sta parlando, con precedenza sullo stato di ascolto. Il nome **JARVIS** non cambia; nessuna scritta «ASCOLTO» nel nucleo.

**Installazione per il test:** chiudi la vecchia istanza, scarica questa ZIP, estraila in **un'altra cartella** e avvia `avvia_jarvis.bat`. Nessun nuovo modello o costo API. Il microfono rimane **in Standby all'avvio**: scegli la modalità manualmente da ⚙. Confronta i colori, la rotazione terrestre e la leggibilità sul Pavilion. **Non cancellare il Jarvis precedente, la cartella Vosk né `%LOCALAPPDATA%\\Jarvis`.**

I test automatici Windows/Linux sono verdi; manca **il collaudo visivo e prestazionale direttamente sul Pavilion**. Le versioni precedenti rimangono negli altri collegamenti sotto. [Dettagli e test da fare](https://github.com/MATRIXNEO23/jarvis/blob/feature/hud-reference-redesign/docs/HUD_REFERENCE_V2.md) · [PR #7 di prova](https://github.com/MATRIXNEO23/jarvis/pull/7).

## NOVITÀ — JARVIS HUD ANIMATO (PROVA SEPARATA)

**[SCARICA LA NUOVA INTERFACCIA JARVIS ANIMATA — ZIP](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/animated-hud-interface.zip)**

L'interfaccia approvata dall'utente è ora nel ramo di prova: **console dei comandi e risposte sulla sinistra**, **reattore JARVIS animato al centro**, **globo olografico che ruota a destra**. Il centro passa leggermente dal **blu al turchese mentre Jarvis sta parlando**, poi torna blu. In alto trovi l'**ingranaggio ⚙**: tutte le impostazioni già esistenti sono spostate lì e non riempiono più la schermata principale. I pulsanti per salvare/annullare un documento restano visibili accanto alla chat quando servono.

**Per provare sul Pavilion:** chiudi la vecchia finestra di Jarvis, scarica lo ZIP e decomprimilo in una **cartella nuova**, poi apri `avvia_jarvis.bat`. Il microfono resta **in standby all'avvio**, da attivare solo manualmente tramite ⚙. Per vedere il bagliore del centro in azione, attiva la voce di Windows e chiedi a Jarvis di rispondere; il globo gira da solo. **Non reinstallare Vosk/GPT se già funzionanti; non cancellare la cartella vecchia né `%LOCALAPPDATA%\\Jarvis`.**

È un'implementazione grafica leggera in Tkinter, senza video o componenti aggiuntivi; **l'effetto deve ancora essere verificato fisicamente sul Pavilion**. I test automatici non sostituiscono il collaudo della finestra reale. [Guida e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/animated-hud-interface/docs/HUD_ANIMATO.md) · [Sviluppo isolato PR #6](https://github.com/MATRIXNEO23/jarvis/pull/6).

## ULTIMA VERSIONE SPERIMENTALE — LIA IMPARA LE CORREZIONI VOCALI

**[SCARICA JARVIS CON VOCE ADATTIVA E SECOND BRAIN (ZIP)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/adaptive-offline-voice.zip)**

Questa versione mantiene **Vosk italiano offline, Conversazione continua GPT, Second Brain e i comandi precedenti**, aggiungendo il pulsante **«Correggi voce...»**. Quando Vosk sbaglia il nome di un'applicazione, puoi correggere la frase: Lia ne memorizza la correzione e la applica alle successive trascrizioni. Non si scarica nessun nuovo modello e non si usa una nuova API a pagamento.

**Prova sul Pavilion:** chiudi Jarvis; scarica lo ZIP ed estrailo in una **cartella nuova**; esegui `avvia_jarvis.bat`. Attiva manualmente **Second Brain locale** per consentire il salvataggio delle correzioni. Seleziona una modalità microfono, pronuncia una frase semplice, premi **«Correggi voce...»**, modifica la frase come l'avevi pronunciata e seleziona **«Conferma correzione»**. Ripeti la frase e verifica che venga riconosciuta correttamente. Le parole «chiudi», «salva», «non» e «Jarvis» non possono essere cambiate da questo dizionario.

**Non reinstallare Vosk né eliminare `%LOCALAPPDATA%\\Jarvis`.** Il microfono parte sempre in Standby. L'apprendimento riguarda il testo trascritto, non un riaddestramento automatico di Vosk. La versione va collaudata sul PC prima di integrarla nella versione stabile.

[Funzioni e limiti dell'adattamento vocale](https://github.com/MATRIXNEO23/jarvis/blob/feature/adaptive-offline-voice/docs/VOCE_ADATTIVA.md) · [PR sperimentale #5](https://github.com/MATRIXNEO23/jarvis/pull/5).

## NUOVA PROVA SEPARATA — SECOND BRAIN DI LIA

**[SCARICA JARVIS CON SECOND BRAIN (ZIP SPERIMENTALE)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/conversation-short-memory.zip)**

Questa variante aggiunge **memoria conversazionale breve** (capisce meglio i riferimenti alle frasi precedenti) e un **archivio persistente SQLite locale** per scambi e azioni realmente confermate, consultabile anche dopo aver riavviato Windows. Funziona sia nella conversazione vocale GPT sia nel campo «Chiedi a GPT». Mantiene catalogo comandi, dettatura e Blocco note della versione sperimentale precedente.

**Attivazione:** scarica lo ZIP di questa sezione, estrailo in una **nuova cartella** e avvia `avvia_jarvis.bat`. Nell'interfaccia seleziona **«Second Brain locale»** per consentire il salvataggio permanente (inizialmente disattivato). Puoi successivamente disattivarlo e cancellare i ricordi archiviati tramite pulsante dedicato. Il microfono resta sempre **spento all'avvio**. Non cancellare la tua vecchia cartella né `%LOCALAPPDATA%\\Jarvis`.

**Privacy:** gli scambi selezionati e le ricevute delle attività restano nel database del profilo Windows, non crittografato; brevi estratti pertinenti vengono comunque inviati al modello ChatGPT quando chiedi di utilizzarli per la conversazione. Non salvare password o dati riservati. **Lettura e invio reali delle email non sono ancora funzioni di questa versione:** il Second Brain è soltanto predisposto a registrarne in futuro le ricevute quando un modulo email avrà confermato l'invio.

[Guida completa al Second Brain e limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/conversation-short-memory/docs/SECOND_BRAIN.md) · [Ramo separato di sviluppo PR #4](https://github.com/MATRIXNEO23/jarvis/pull/4). **Versione non ancora collaudata sul Pavilion:** verificare con conversazioni fittizie prima di sostituire qualsiasi installazione.

## NOVITÀ — CATALOGO DEI COMANDI PER APPLICAZIONE

La versione **Conversazione GPT e documenti** include ora `jarvis_commands.json`, un catalogo delle azioni che Jarvis sa realmente eseguire. GPT può collegare frasi diverse alla stessa azione, per esempio **«Chiudimi Blocco note»** → `notepad.close`, senza imporre parole identiche. Aggiunta anche l'apertura del **disco locale C**. Sono supportate soltanto le funzioni con un esecutore verificato; non viene dato a GPT accesso libero ai programmi, ai file o alla shell. [Leggi il catalogo e i limiti](https://github.com/MATRIXNEO23/jarvis/blob/feature/gpt-conversazione-documenti/docs/CATALOGO_COMANDI.md).

Per provare l'aggiornamento, scarica la ZIP desiderata qui sopra e tieni separata la versione che già funziona. Il catalogo richiede ancora la prova reale sul Pavilion; il microfono parte sempre spento.

## NUOVA PROVA ISOLATA — CONVERSAZIONE GPT E DOCUMENTI

**[SCARICA LO ZIP SPERIMENTALE CON GPT CONVERSAZIONALE E BLOCCO NOTE](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/gpt-conversazione-documenti.zip)**

Questa versione aggiunge **Conversazione continua GPT** (senza ripetere «Ehi Jarvis»), risposte vocali e gestione assistita di **nuovi documenti in Blocco note classico**: GPT prepara il testo, Jarvis tenta di inserirlo, chiede se salvare e chiudere, non salvare oppure annullare, e accetta la scelta a voce. Permette un nuovo file `.txt` sul Desktop, in Documenti o Download, per esempio **«sul desktop come poesia di Venezia»**. I file esistenti non vengono mai sovrascritti. La versione è **solo di prova: i test automatici non verificano la reale automazione di Blocco note sul Pavilion**. [Funzioni, limiti e prove necessarie](https://github.com/MATRIXNEO23/jarvis/blob/feature/gpt-conversazione-documenti/docs/CONVERSAZIONE_GPT_DOCUMENTI.md).

**Installazione sul PC:** chiudi Jarvis; estrai lo ZIP in **un'altra cartella**, senza sostituire la precedente, avvia `avvia_jarvis.bat`. Non reinstallare Vosk né il DevKit GPT se sono già presenti. Non cancellare `%LOCALAPPDATA%\\Jarvis`. Il microfono rimane sempre **spento all'avvio**: per provare seleziona manualmente «Conversazione continua GPT», con ChatGPT collegato, e usa documenti di prova non importanti.

**Mantieni anche la versione vocale precedente funzionante:** è ancora disponibile nei link sottostanti. Nessun merge automatico nella versione principale.

**[NUOVA PROVA — JARVIS CON BROWSER, DETTATURA, «EHI JARVIS» E RISPOSTE A VOCE](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/voice-browser-dictation.zip)**

**AGGIORNAMENTO DETTATURA (30/10/2026):** il primo test reale sul Pavilion ha mostrato che Jarvis riconosceva le parole ma Windows rifiutava l'inserimento. La correzione modifica la struttura `SendInput` per Windows 64 bit e aggiunge test specifici: [CI Windows/Linux superata](https://github.com/MATRIXNEO23/jarvis/actions/runs/41129730526). **Da confermare nuovamente sul Pavilion.**

**Per avviare e fermare la dettatura completamente a voce:** seleziona **Ascolto continuo**, clicca nel campo di testo di Blocco note, quindi pronuncia **«Ehi Jarvis, attiva dettatura»**. Per interrompere di' **«Ehi Jarvis, disattiva dettatura»**. Una volta attiva, il parlato comune diventa testo senza ripetere «Jarvis». La modalità del microfono non cambia da sola.

**Per riprovare la correzione:** scarica di nuovo lo ZIP del **primo link**, estrailo in una **cartella nuova**, chiudi il Jarvis precedente e apri il nuovo `avvia_jarvis.bat`. **Non reinstallare Vosk** se già funziona. Non cancellare o sostituire le cartelle precedenti né `%LOCALAPPDATA%\\Jarvis`.

Il ramo di prova consente di aprire/cercare nel browser, dettare in un campo esterno, chiamare Jarvis con «Ehi Jarvis» durante l'ascolto continuo e **scegliere una voce Windows per le risposte parlate offline**. [Test automatici Windows/Linux superati](https://github.com/MATRIXNEO23/jarvis/actions/runs/41126671637); **collaudo reale sul Pavilion ancora necessario**. Non sostituisce per ora la versione vocale precedente. [Istruzioni risposte vocali](https://github.com/MATRIXNEO23/jarvis/blob/feature/voice-browser-dictation/docs/VOCE_RISPOSTE.md) · [Dettatura e browser](https://github.com/MATRIXNEO23/jarvis/blob/feature/voice-browser-dictation/docs/DETTATURA_BROWSER.md).

## SCARICA JARVIS — ZIP COMPLETO AGGIORNATO CON VOCE OFFLINE (VERSIONE DI PROVA)

**[PREMI QUI PER SCARICARE JARVIS CON LA VOCE](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/offline-voice-pavilion.zip)**

Questo link scarica lo ZIP del branch `feature/offline-voice-pavilion` con il comando vocale offline italiano e i file di installazione. **Non scaricare lo ZIP `main` se vuoi provare la voce.**

Il microfono **rimane spento a ogni avvio**. Puoi scegliere manualmente Standby, Premi per parlare e Ascolto continuo. Nessun passaggio automatico a standby per Minecraft o altri programmi.

### Installazione della versione con voce sul Pavilion

1. **Chiudi Jarvis** se e' aperto. Scarica lo ZIP dal pulsante qui sopra.
2. In Download di Windows, clic destro sullo ZIP e scegli **Estrai tutto** in **una cartella nuova**. Non cancellare o sovrascrivere la precedente cartella Jarvis.
3. Apri la cartella estratta `jarvis-feature-offline-voice-pavilion` (il nome puo' variare).
4. Fai doppio clic su **`installa_voce.bat`**: installa i moduli Vosk e SoundDevice e scarica il piccolo modello italiano ufficiale. Serve Internet soltanto per questa installazione; segui il testo nella finestra fino al completamento.
5. Fai doppio clic su **`avvia_jarvis.bat`**. Il microfono parte **spento**. Per la prima prova seleziona **Premi per parlare**, tieni premuto il pulsante e pronuncia «Jarvis, apri la calcolatrice».

Non devi reinstallare il collegamento GPT gia' installato nella cartella dei dati utente. Se l'installazione voce fallisce, il normale input testuale di Jarvis rimane utilizzabile. **Non cancellare i dati in `%LOCALAPPDATA%\Jarvis`.**

**Stato di verifica:** i test automatici Python/Node per Windows e Linux sono superati ([CI](https://github.com/MATRIXNEO23/jarvis/actions/runs/41099757267)). Il microfono fisico e le prestazioni sul tuo Pavilion non sono ancora collaudati; questa non e' una versione definitiva.

[Guida completa alla voce offline](https://github.com/MATRIXNEO23/jarvis/blob/feature/offline-voice-pavilion/docs/VOCE_OFFLINE.md) · [Codice e avanzamento della voce](https://github.com/MATRIXNEO23/jarvis/pull/1)

## Versione precedente senza voce

**[SCARICA JARVIS — ZIP PRINCIPALE (MAIN, SENZA VOCE)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/main.zip)**

Questa e' la versione gia' utilizzata per il pianificatore e i comandi testuali sul Pavilion. Mantienila finche' la prova del microfono non e' completata.

[Pagina principale del progetto](../README.md)
