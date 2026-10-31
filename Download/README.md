# Scarica Jarvis per Windows 10 — HP Pavilion

## NUOVA PROVA — AUTODIAGNOSI CON EVIDENZE RUNTIME E GPT ESTERNO (31/10/2026)

**[Scarica il ramo sperimentale Jarvis-Diagnostica-Runtime-GPT (ZIP da GitHub)](https://github.com/MATRIXNEO23/jarvis/archive/refs/heads/feature/diagnostic-runtime-evidence-external-gpt.zip)**

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
