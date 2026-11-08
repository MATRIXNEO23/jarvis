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

# Registro autorevole — versioni, sorgenti e pacchetti

Aggiornamento documentale del 7 novembre 2026. Questo è l'ingresso per scegliere una versione: la radice di main è storica e non coincide con il runtime Gemma. Le sezioni successive conservano la cronologia. 001–005 appartengono alla serie precedente.006 prosegue la numerazione includendo il runtime Gemma e le correzioni audit; il profilo resta Gemma-Trial.

| Riferimento | Sorgenti esatti | Verifica disponibile | Pacchetto/stato |
|---|---|---|---|
| **Ultima candidata:007** | [9f8c5f582b98a4ac131c41a4170b194c98abc3fa](https://github.com/MATRIXNEO23/jarvis/tree/9f8c5f582b98a4ac131c41a4170b194c98abc3fa) | [Windows e runtime estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42420559553), SUCCESS | [Jarvis-007.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-007.zip); collaudo PC pendente; [handoff](../docs/HANDOFF-JARVIS-007-20261107.md) |
| Precedente candidata006 | [3e2cc05b0b08fdc5b47054b19593cf3151aff75a](https://github.com/MATRIXNEO23/jarvis/tree/3e2cc05b0b08fdc5b47054b19593cf3151aff75a) | [Windows e runtime estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42384228753), SUCCESS | [Jarvis-006.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-006.zip); collaudo PC pendente; [scheda](../docs/CONSEGNA-JARVIS-006-20261107.md) |
| Precedente candidata Gemma | [61a95f8c78f0d429ede21acee25c87a77f91d712](https://github.com/MATRIXNEO23/jarvis/tree/61a95f8c78f0d429ede21acee25c87a77f91d712) | [Windows e ZIP estratto 42270285346](https://github.com/MATRIXNEO23/jarvis/actions/runs/42270285346), SUCCESS | [Jarvis-Gemma-Carattere-e-Stile-61a95f8.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/f147b1a5faa977e8e4aefe21c9799465a7a8e990/Download/Jarvis-Gemma-Carattere-e-Stile-61a95f8.zip); collaudo PC ancora pendente |
| Precedente numerata005 | [b202181d435cf4ee13ffb355265e1f1a9f995963](https://github.com/MATRIXNEO23/jarvis/tree/b202181d435cf4ee13ffb355265e1f1a9f995963) | [Windows/estrazione 41749364482](https://github.com/MATRIXNEO23/jarvis/actions/runs/41749364482), SUCCESS | [Jarvis-005.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/f147b1a5faa977e8e4aefe21c9799465a7a8e990/Download/Jarvis-005.zip); candidata storica, collaudo PC pendente |
| Base storicamente confermata | [b936879a431370d206152be7b089baf587d15499](https://github.com/MATRIXNEO23/jarvis/tree/b936879a431370d206152be7b089baf587d15499) | [Pubblicazione 41229495866](https://github.com/MATRIXNEO23/jarvis/actions/runs/41229495866), [test 41229501460](https://github.com/MATRIXNEO23/jarvis/actions/runs/41229501460), [verifica dei byte](../docs/VERIFICA-CONCRETA-BASE-20261101.md) | [Timer-Audio-Fix2](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/f147b1a5faa977e8e4aefe21c9799465a7a8e990/Download/Jarvis-Timer-Audio-Fix2-20261031.zip); non identifica automaticamente l'installazione attuale dell'utente |
| Audit — checkpoint prima di006 | [970bcb17e15b9c197ec4fa5766eac6a6519058a6](https://github.com/MATRIXNEO23/jarvis/tree/970bcb17e15b9c197ec4fa5766eac6a6519058a6) | [Windows 42378831525](https://github.com/MATRIXNEO23/jarvis/actions/runs/42378831525): 911 test per versione Python; [correzioni in bozza, PR53](https://github.com/MATRIXNEO23/jarvis/pull/53) | Le correzioni sono ora incluse nella006; questo rimane il riferimento prima della build |

Hash SHA256:006 verificata dal nuovo workflow; archivi precedenti ricontrollati e conservati senza ricostruzione:

| Archivio | Byte | SHA256 |
|---|---:|---|
| 007 | 8138643 | `a5a24f35b410a45bed3dd08ed2180563d429e82cbe0a878045f4e7157182408f` |
| 006 | 8134642 | `066c6f0cb0af78a9e064119d1a9a39a9317f7524456e14c1716555d9d08f103a` |
| Gemma 61a95f8 | 8103631 | `c38806cf12574e7ae142a8eef2cebe2afec6244c92db0a195c507d6bade6041a` |
| 005 | 283598 | `583bd55d1ef416b3781f6183d8ea6365f0b8761c6cf1fd614d652db832285728` |
| Timer-Audio-Fix2 | 406653 | `c37270265918c63ddb3a9cf6a2c0982d468dd1af83a1af330c5af1dfb20f9352` |

Per sviluppare o verificare il codice, aprire il commit scelto della tabella, leggere AGENTS/RECUPERO e usare i test Windows previsti. Il vecchio builder Gemma trasformava alcuni Python: il commit della release identifica anche quella ricetta. La correzione 012 elimina tale differenza nei sorgenti della006; gli archivi precedenti restano invariati.

Il [registro numerico JSON](BUILD-NUMBERS.json) conserva i metadata 001–007; gli altri pacchetti e dati storici restano sotto. Non promuovere una bozza a versione PC confermata dal solo CI e non associare i test nuovi al vecchio ZIP. Nessuna nuova build è autorizzata da questo indice.

---

Rapporti: [audit iniziale](../docs/AUDIT-JARVIS-INIZIALE-20261107.md) e [stato finale delle correzioni](../docs/RAPPORTO-FINALE-AUDIT-CORREZIONI-20261107.md). I report di sviluppo restano nella repository, fuori dal pacchetto operativo.

## Cronologia conservata

# Build numerate Jarvis

Da questa consegna i file hanno numeri progressivi. Ogni versione pubblicata resta disponibile; la prossima sarà008.

| Build | Pacchetto | Stato | Descrizione |
| --- | --- | --- | --- |
| 005 | [Jarvis-005.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-005.zip) | Candidata, collaudo PC pendente | Richiamo Jarvis obbligatorio e prompt senza memoria vuota |
| 004 | [Jarvis-004.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-004.zip) | Candidata, collaudo PC pendente | Avvio programmi e app con comandi personali |
| 003 | [Jarvis-003.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-003.zip) | Candidata, collaudo PC pendente | Interruttori rapidi MIC, GPT e MEMORIA |
| 002 | [Jarvis-002.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-002.zip) | Candidata, collaudo PC pendente | Contesto della cartella indicata in conversazione |
| 001 | [Jarvis-001.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-001.zip) | Candidata, collaudo PC pendente | Continuità e ricerca; stessi byte della precedente candidata cec4536 |

Registro tecnico: [BUILD-NUMBERS.json](BUILD-NUMBERS.json). I pacchetti storici senza numero restano elencati sotto.

## Candidata Gemma — carattere e stile del modello locale, 61a95f8

[Jarvis-Gemma-Carattere-e-Stile-61a95f8.zip](./Jarvis-Gemma-Carattere-e-Stile-61a95f8.zip) — Istruzioni personalizzate per il tono di Gemma, applicabili dalla risposta successiva. [Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42270285346) superate. Collaudo sul Pavilion pendente.

## Candidata Gemma — consenso GPT per la sessione Telegram, c233bb4

[Jarvis-Gemma-Telegram-Consenso-GPT-Sessione-c233bb4.zip](./Jarvis-Gemma-Telegram-Consenso-GPT-Sessione-c233bb4.zip) — Consenso GPT online per la sessione Telegram, con conferma per messaggio come modalità predefinita. [Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42251845994) superate. Collaudo sul Pavilion pendente.

## Candidata Gemma — notifiche Telegram nel HUD, bf6bce9

[Jarvis-Gemma-Telegram-Notifiche-HUD-bf6bce9.zip](./Jarvis-Gemma-Telegram-Notifiche-HUD-bf6bce9.zip) — Pallino Telegram lampeggiante per i messaggi da vedere e viola tenue dopo la lettura. [Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42222733895) superate. Collaudo sul Pavilion pendente.

## Candidata Gemma — contesto per contatto Telegram, 0055607

[Jarvis-Gemma-Telegram-Contesto-Contatti-0055607.zip](./Jarvis-Gemma-Telegram-Contesto-Contatti-0055607.zip) — Profilo modificabile per singolo contatto, usato da Gemma locale. [Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42211351973) superate. Collaudo sul Pavilion pendente.

## Candidata Gemma — ascolto continuo, b62d8a7

[Jarvis-Gemma-Ascolto-Continuo-b62d8a7.zip](./Jarvis-Gemma-Ascolto-Continuo-b62d8a7.zip) — Ascolto continuo senza richiamo, modalità Hey Jarvis con richiamo e priorità al motore locale. [Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42170295267) superate. Collaudo sul Pavilion pendente.

## Candidata Gemma — voce in console, 53460ce

[Jarvis-Gemma-Voce-Console-53460ce.zip](./Jarvis-Gemma-Voce-Console-53460ce.zip) — Ripristina la ricerca del modello vocale italiano nel profilo sorgente e mostra gli errori del microfono in console. [Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42165467735) superate. Collaudo sul Pavilion pendente.

## Candidata Gemma per Telegram — 9adc86e

[Jarvis-Gemma-Telegram-9adc86e.zip](./Jarvis-Gemma-Telegram-9adc86e.zip) — Gemma può rispondere su Telegram quando GPT è disattivato. [Verifiche Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42163091184) superate. Collaudo sul Pavilion pendente.

## Riscontro successivo — correzioni nei sorgenti, 2 novembre 2026
Dopo il candidato d06e233 proposto in chat: foto ricerca parziale e blocco locale del contesto GPT; segnalati apertura browser su ricerca senza ambito, risposta solo Download e perdita di azione al chiarimento. La foto non identifica autonomamente nome ZIP/richiesta iniziale; nessuna promozione a base PC. Source correttivo 806685275947cea4b933d20aa0317658d13b853c, ramo feature/fix-file-search-20261102, 471 test per job Windows PASS (run 41367835278). [Scheda](../docs/RICERCA-DIALOGO-CORREZIONI-20261102.md). Non pubblicato un nuovo pacchetto: i file Download e la base b936879 sono preservati, d06e233 non contiene queste correzioni. Nuova build solo su richiesta esplicita.

# Registro versioni e punti di ripristino Jarvis
Aggiornato il 2026-11-01. Questo è l'indice diretto per recuperare una versione senza analizzare tutta la cronologia o cercare artifact.

## Ultimo candidato consegnato — d06e233 (collaudo PC pendente)
[Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip), source d06e233a98e4ea5b4e99a9d296b9570ce0c92d86. [Scheda e prove](../docs/CONSEGNA-ACCESSO-FILE-20261101-d06e233.md). Windows CI 41350638557 SUCCESS: 466 test per versione Python, 93 estratti, UI/manifest/launcher unico e download HTTP/hash PASS. 266689 byte; SHA-256 ac130883d32518b430737f8f3d767a16a56e3cad9b3ae32f37d8f20799f42699. BASE-UTENTE sotto conservata; nessun riscontro PC attribuito al candidato.

## Riferimento funzionante confermato
**BASE-UTENTE-20261101 — Jarvis-Timer-Audio-Fix2-20261031.zip.**
Il 2026-11-01 l’utente ha identificato come funzionante Timer Audio Fix2, allora in cima a Download/README.md. Nome e file sono verificati: non serve ripetere la domanda. I candidati aggiunti successivamente in cima al catalogo non ereditano quella conferma PC.

| Campo | Valore verificato |
|---|---|
| Pacchetto completo | [Jarvis-Timer-Audio-Fix2-20261031.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Fix2-20261031.zip) |
| Commit sorgente esatto | [b936879a431370d206152be7b089baf587d15499](https://github.com/MATRIXNEO23/jarvis/tree/b936879a431370d206152be7b089baf587d15499) |
| Dimensione e integrità | 406653 byte; Git blob SHA-1 6aa9e6f9eb040dc7390b4edb55c9ae175bd4e512 |
| SHA-256 | c37270265918c63ddb3a9cf6a2c0982d468dd1af83a1af330c5af1dfb20f9352 |
| Provenienza | Tutti i 155 file identici al tree sorgente; ZIP ricostruito byte-identico; log publisher coerente |
| Test locali audit | 373 raccolti: 368 eseguiti con successo, 5 Windows/Tk saltati; zero fallimenti/errori. Python 3.12.14 Linux; sintassi Python/Node PASS |
| Download diretto | HTTP 200, 406653 byte, confronto integrale con il pacchetto versionato PASS |
| CI storica | Run 41229501460 Windows/Linux 3.11/3.12: 373 per job; file identici al merge testato |
| Pubblicazione | Run 41229495866, log con sorgente/hash uguali alla copia scaricata |
| Prova PC | Conferma esplicita di Alberto del 2026-11-01: build attualmente usata funziona bene; ambito riferito, non prova diretta dell'agente di tutte le funzioni |
| Dati | Launcher profilo Trial separato; backup/profilo compatibile prima di ogni ritorno; credenziali cifrate non portabili liberamente |
| Avvio microfono | Nella base dipende da auto_listen, inizialmente attivo nel profilo Trial; non attribuirle lo standby del ramo successivo |
| Evidenze complete | [Rapporto e log](../docs/VERIFICA-CONCRETA-BASE-20261101.md) |

Questa è la base da preservare e usare per le aggiunte successive. Non sovrascrivere il pacchetto.
Il ramo 5e61e53/a86c2c9 contiene successive modifiche al nucleo e 386 test, ma non è il contenuto di questa ZIP: valutarlo separatamente, senza attribuire il miglioramento riferito a codice assente. L'audit non ha sostituito il programma sul PC.
Il ripristino è ora identificabile direttamente da ZIP, commit e checksum, con i limiti di compatibilità dati descritti sotto.

## Scheda obbligatoria per ogni punto di ripristino
Compilare una scheda compatta prima della promozione:
- ID leggibile/versione e data; stato: candidato, test automatici superati, collaudato sul PC nell'ambito indicato, oppure superato/non consigliato.
- Commit esatto dei sorgenti e riferimento immutabile recuperabile; nome/versione delle add-on.
- Percorso ZIP completo versionato in Download, commit che lo conserva, dimensione e SHA-256 del pacchetto. Il Git blob SHA è un identificatore diverso: non chiamarlo SHA-256.
- Link diretto nel README Download, verifica di download ed estrazione, contenuto/manifest del pacchetto, istruzioni di installazione e dipendenze/versioni.
- Test automatici: comando, ambiente, esito, commit e workflow; distinguere simulazioni da componenti reali.
- Prova dell'utente: data, pacchetto identificato, funzioni effettivamente provate, esito e limiti. «Funziona» non equivale a ogni funzione collaudata al cento per cento.
- Compatibilità del profilo/schema dati, backup privato necessario e procedura per tornare indietro senza perdere dati o usare database incompatibili. Nessuna credenziale o backup personale in repository.
- Motivo della scelta e link alla scheda decisione/errore, problemi noti e riferimento funzionante precedente.

Dopo il collaudo PC, aggiornare il puntatore in cima a questo file con il nome esatto. Non sovrascrivere lo ZIP di una versione funzionante con contenuti diversi. I rilasci nuovi usano nomi univoci, per esempio Jarvis-VERSIONE-SHA.zip.
Gli artifact CI sono prove o copie ausiliarie: il pacchetto di recupero deve essere conservato in Download nel repository, non soltanto in un artifact che può scadere. Conservare anche i sorgenti corrispondenti.

## Quando l'utente dice «riprendi da lì» o «torniamo a quella»
1. Aprire questo registro e la scheda identificata dal contesto. Se il riferimento è ambiguo, chiedere soltanto quale delle versioni nominate intende; non scegliere in silenzio.
2. Distinguere ripresa dello sviluppo da ripristino del programma sul PC. Individuare subito commit, ZIP e compatibilità dati dalla scheda.
3. Verificare presenza e integrità del pacchetto esatto; usare il riferimento immutabile se main si è spostato.
4. Per sviluppo: recuperare i sorgenti in un checkout/ramo separato o proporre un ripristino tracciato, conservando la cronologia. Nessun reset distruttivo o force-push implicito.
5. Per il PC: chiudere Jarvis, conservare profilo e pacchetto correnti, estrarre quello scelto in cartella separata e usare un profilo compatibile. Non cancellare dati né aprire un database nuovo con codice vecchio senza verifica.
6. Registrare l'operazione e le verifiche essenziali in piano/handoff. I test già documentati non vanno rifatti tutti senza un motivo; verificare soltanto integrità, ambiente cambiato e aspetti irrisolti.

La procedura consente recupero diretto dei riferimenti registrati. Richiede accesso al repository e file ancora conservati; non garantisce scritture mai completate o file rimossi. Nessun ripristino è stato eseguito creando questo registro.

## Inventario dei pacchetti già versionati
Fotografia del commit bb94afa1865fe0315021f783736be3cb77c4af84. Presenza, dimensioni e Git blob SHA verificati via API GitHub; non sono test di download, estrazione o funzionamento PC. I link fissati al commit evitano che un cambiamento di main confonda il riferimento.
| ZIP | Byte | Git blob SHA |
|---|---:|---|
| [Jarvis-AddOn-Registro-GPT-Test.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-AddOn-Registro-GPT-Test.zip) | 369432 | ea1fb192dc257be6defeae01ff3d39e905b776f3 |
| [Jarvis-Autodiagnosi-Ibrida-GPT.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Autodiagnosi-Ibrida-GPT.zip) | 313324 | d73a4bb98f75c5417e5af73afff9bf4eba49d0f9 |
| [Jarvis-Autodiagnosi-e-Miglioramenti.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Autodiagnosi-e-Miglioramenti.zip) | 300368 | 49b36bab7fe6522a749576909820c31c1268690f |
| [Jarvis-Contesto-e-Risposte-Brevi.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Contesto-e-Risposte-Brevi.zip) | 262463 | 14fa07cf4e3484fc4fb60f430b22bdd71584e965 |
| [Jarvis-Conversazione-Naturale.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Conversazione-Naturale.zip) | 290170 | b0d6ce6b042d35401646b7a68dc78a4eec27f8c8 |
| [Jarvis-Diagnostica-Runtime-GPT.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Diagnostica-Runtime-GPT.zip) | 330999 | a34d8a62bca7168fbf108c14025d8310273f068b |
| [Jarvis-Fix-Autodiagnosi-Vocale.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Fix-Autodiagnosi-Vocale.zip) | 304402 | f806bfe7f4680369c10d6721b57c4bdd87bea53b |
| [Jarvis-Fix-Diagnostica-Visibile.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Fix-Diagnostica-Visibile.zip) | 321915 | ad9c7b4a2b41229ccccd085d95739024eeb0a4f2 |
| [Jarvis-Full-Audit-Telegram50-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Full-Audit-Telegram50-20261031.zip) | 394717 | 68c0cd7e9b699c161fc5945453eb4984a3b7b559 |
| [Jarvis-Gestione-Progetti-e-Diagnostica.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Gestione-Progetti-e-Diagnostica.zip) | 256542 | bbe95ce13823042461b71068ba7b4f14e26e529d |
| [Jarvis-HUD-Riferimento-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-HUD-Riferimento-20261031.zip) | 394707 | 0c716780755ec9a4ae4b5f6bfa4c5e0db10755c2 |
| [Jarvis-Memoria-Affidabile.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Memoria-Affidabile.zip) | 282608 | 209b027df98c0177fa0af8465a33fd78a240cd02 |
| [Jarvis-Memoria-Automatica.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Memoria-Automatica.zip) | 234564 | 90ee4e0b5ebb850994d15fea757ad74e0244767d |
| [Jarvis-Progetti-Vocali-e-Salvataggio.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Progetti-Vocali-e-Salvataggio.zip) | 244349 | 16634118983f39d337ba6856b5fb9eb0892cb244 |
| [Jarvis-Recupero-Documenti.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Recupero-Documenti.zip) | 293782 | 84c550f6a45cf9d1f61702f3570f5c54e3ac119b |
| [Jarvis-Telegram-Contatti-Vocali-Test.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Telegram-Contatti-Vocali-Test.zip) | 345603 | 6d96e5bbd63f21b216a07895ea0d7099386b32e2 |
| [Jarvis-Timer-Audio-Corretto-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Corretto-20261031.zip) | 407889 | 5019a79d91b5fcbfe28fc9a65155c5fc47f25fb8 |
| [Jarvis-Timer-Audio-Fix2-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Fix2-20261031.zip) | 406653 | 6aa9e6f9eb040dc7390b4edb55c9ae175bd4e512 |
| [Jarvis-Timer-Impostazioni-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Impostazioni-20261031.zip) | 405091 | d6335a69325d02edf061603a2e4707ecf92e9c16 |
| [Jarvis-Timer-Vocale-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Vocale-20261031.zip) | 407868 | 5d10f8ab35cb6e31ccc89921b0aecefab760530c |

## Fonti rapide
[Handoff](../docs/HANDOFF-CODEX-ARCHIFY-20261031.md), [decisioni e lezioni](../docs/DECISIONI-E-LEZIONI.md), [stato attività](../docs/STATO-ATTIVITA.md), [sorgenti](../docs/INDICE-SORGENTI.md), [installazione e dati](../Prima-installazione/06-Reinstallazione-e-dati.md).

## Candidato Accesso file 63bfd04 — 2026-11-01

- ZIP persistente: Download/Jarvis-Accesso-File-0.1.0-20261101-63bfd04.zip
- Sorgenti: 63bfd048032f51ff5d52f87a14060f27fad720c0
- SHA-256: 43867ec86094eac5c7e9ef6f03674d9c5ad19cd6736f3594638eadfb85d6db0e
- Windows CI: run 41321679044, due job 3.11/3.12, pacchetto estratto e avvio UI.
- Collaudo PC: pendente. La base confermata BASE-UTENTE-20261101 b936879 resta invariata.
- Recupero: usare la cartella precedente Timer Audio Fix2; non cancellare profili o dati.

## Candidato Accesso file 7298fb6 — 2026-11-01

- ZIP persistente: Download/Jarvis-Accesso-File-0.1.0-20261101-7298fb6.zip
- Sorgenti: 7298fb632cd9b72386fd7a30f469b307ce7e6fa5
- SHA-256: 72c6d57a9a258fe7c875cfdc8646bc4ddf5b75417aa748bb5d4d4b7ef3e96755
- Windows CI: run 41322290359, due job 3.11/3.12, pacchetto estratto e avvio UI.
- Collaudo PC: pendente. La base confermata BASE-UTENTE-20261101 b936879 resta invariata.
- Recupero: usare la cartella precedente Timer Audio Fix2; non cancellare profili o dati.

### Esito dettagliato del candidato 7298fb6
393 test Windows per job Python 3.11/3.12 senza skip; 20 test dall’archivio estratto, import e avvio/chiusura/rilascio directory PASS, run 41322290359. Scaricamento raggiungibile HTTP 200, 249396 byte e tipo application/zip. Git blob ZIP 09e3ef994a0ca38475844f0fd8e22334e8dba4c4. [Rapporto](../docs/ACCESSO-FILE-RAPPORTO-20261101.md). Prova PC ancora pendente; preservare BASE-UTENTE b936879.

## Candidato Accesso file 755f988 — 2026-11-01

- ZIP persistente: Download/Jarvis-Accesso-File-0.1.0-20261101-755f988.zip
- Sorgenti: 755f988437b214c035c23c7db5f73f6c38c2ffde
- SHA-256: 98c8ccaaa7ac133e24b0f40860e5ec470893ecedb3978660f36cefed1ae53de9
- Windows CI: run 41330559676, due job 3.11/3.12, pacchetto estratto e avvio UI.
- Collaudo PC: pendente. La base confermata BASE-UTENTE-20261101 b936879 resta invariata.
- Recupero: usare la cartella precedente Timer Audio Fix2; non cancellare profili o dati.

## Candidato Accesso file 950f655 — 2026-11-01

- ZIP persistente: Download/Jarvis-Accesso-File-0.1.0-20261101-950f655.zip
- Sorgenti: 950f655a6fc0db25f2eb4c66d47507cf9b0d3038
- SHA-256: 85c7879346824198e1a54939b0b44faae7d0813b004b152e95b788e79160539f
- Windows CI: run 41330921134, due job 3.11/3.12, pacchetto estratto e avvio UI.
- Collaudo PC: pendente. La base confermata BASE-UTENTE-20261101 b936879 resta invariata.
- Recupero: usare la cartella precedente Timer Audio Fix2; non cancellare profili o dati.

## Candidato Accesso file d06e233 — 2026-11-01

- ZIP persistente: Download/Jarvis-Accesso-File-0.1.0-20261101-d06e233.zip
- Sorgenti: d06e233a98e4ea5b4e99a9d296b9570ce0c92d86
- SHA-256: ac130883d32518b430737f8f3d767a16a56e3cad9b3ae32f37d8f20799f42699
- Windows CI: run 41350638557, due job 3.11/3.12, pacchetto estratto e avvio UI.
- Collaudo PC: pendente. La base confermata BASE-UTENTE-20261101 b936879 resta invariata.
- Recupero: usare la cartella precedente Timer Audio Fix2; non cancellare profili o dati.

## Candidato Continuità cec4536 — 2026-11-03

- ZIP persistente: Download/Jarvis-Continuita-20261103-cec4536.zip
- Sorgenti: cec4536b0f5991cb900680ed05295245f4e04acb
- SHA-256: d96e90657ad67399893ef5d89a7e250da5369b64a833fd596e4d718ad3687f07
- Windows CI: run 41614085149, due job 3.11/3.12, pacchetto estratto e avvio UI.
- Collaudo PC: pendente. La base confermata BASE-UTENTE-20261101 b936879 resta invariata.
- Recupero: usare la cartella precedente Timer Audio Fix2; non cancellare profili o dati.
