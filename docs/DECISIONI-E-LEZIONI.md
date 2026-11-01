# Decisioni e lezioni — Jarvis

## Regola del registro
Conservare le soluzioni riuscite come riferimenti entro il loro ambito verificato. Scartare quelle fallite dalle raccomandazioni, conservando la spiegazione tecnica del fallimento. Ogni nuova scheda indica data, stato (verificato, scartato, ipotesi o proposto), problema, decisione/motivazione, prove, commit/workflow e limiti. Gli stati non si confondono: la CI verde non dimostra la qualità del dialogo GPT.

## 2026-10-31 — CI dialogo: verificato
**Problema:** run 41230403859 e 41230414187 fallite. Tutti gli 8 log mostrano l'unico fallimento test_second_brain.py:26: 16 non è <=8.

**Decisione e motivo:** mantenere l'ampliamento intenzionale a 16 scambi e aggiornare il test al contratto nuovo. Tornare a 8 avrebbe annullato l'obiettivo della modifica; disabilitare il test avrebbe nascosto il problema. La regressione ora verifica anche contenuto, ordine, espulsione e budget, non soltanto la dimensione.

**Prove:** prima della patch 373 test locali, un fallimento identico alla CI; dopo 373 OK (5 Windows saltati in Linux). Commit faba67363e07ea478241fbe549c45474aab5144a sul ramo feature/timer-settings-ui-20261031. Run https://github.com/MATRIXNEO23/jarvis/actions/runs/41232983494 SUCCESS: quattro job Linux/Windows, Python 3.11/3.12, 373 test ciascuno; Windows nessuno skip, Linux 5 skip. Sintassi e parser PowerShell PASS.

**Limite:** non risolve i difetti della pipeline di memoria e non prova il dialogo reale con GPT. Nessun pacchetto pubblicato.

## 2026-10-31 — Aumento dei limiti come soluzione sufficiente: scartato
**Errore da evitare:** considerare 16 turni RAM/2400 caratteri come prova di continuità migliore.

**Causa:** jarvis.py richiede solo 860 caratteri, poi il router riduce fino a 850 o allo spazio residuo; la capacità di archivio non è il contenuto consegnato al modello. Cinque turni medi si riducono a due nella riproduzione locale. Il percorso permanente.recent non è letto dal compattatore finale.

**Lezione applicabile:** verificare il payload finale del client e il recupero dopo riavvio. Non aumentare indiscriminatamente i limiti e non considerare i test dei singoli moduli una prova dell'intero flusso. Correzione del nucleo proposta, ancora da approvare.

## 2026-10-31 — Archify: verificato parzialmente
**Decisione:** usarlo da main contro checkout separato dei sorgenti evoluti 1f7310f; così la mappa rappresenta il codice effettivamente esaminato.

**Prove:** docs/architecture-20261031/jarvis.html e candidato/ricevuta su main. Validate, deliver e check PASS. Browser-check saltato perché Chrome/Chromium assente; finalize codice 2. Non dichiarare riuscita completa o ispezione visiva.

**Lezione:** distinguere integrità/fonti dell'artefatto, controllo browser e collaudo dell'app. Nessuna dipendenza Archify aggiunta al runtime.

## 2026-10-31 — Nucleo dialogo: soluzione verificata automaticamente
**Autorizzazione:** piano approvato con «Sì». Commit a86c2c932af988b23916e8d4495025de5ee0a730 sul ramo evoluto, nessun add-on o API aggiuntiva.

**Scelta e motivo:** raccolta locale senza tagli intermedi, recupero recenti SQLite, domanda pendente preservata e una sola selezione nel prompt finale. Le prove dimostravano che la capacità RAM non equivale al contesto ricevuto dal modello. Limite invariato 5000 unità UTF-16; cataloghi opzionali subordinati alla memoria. Timeout testo breve allineato alla voce. Standby all'avvio senza cambiare le modalità manuali e senza riscrivere preferenze salvate.

**Prove:** 386 test per ognuno dei quattro job Windows/Linux, Python 3.11/3.12 nella run 41236238213 SUCCESS (Linux 5 skip Windows-only, Windows nessuno). Smoke reale bridge/SDK Windows senza login run 41236238208 SUCCESS. Le 13 nuove regressioni coprono riavvio, dieci turni, payload effettivo dei callback voce/testo, cataloghi, Unicode, isolamento e assenza replay.

**Errori scartati:** primo conteggio con len Python insufficiente per emoji/escaping, corretto con unità UTF-16; prima conservazione della domanda finale produceva un prefisso residuo, corretto il separatore. Entrambi restano nei test per evitare ricadute. Non promuovere tentativi precedenti a riferimenti.

**Limiti:** collaudo GPT/Pavilion non eseguito, nessun pacchetto distribuito. Archify aggiornato: tre gate PASS, browser-check assente per Chrome mancante. Il dedup confronta solo prefissi disponibili nei vecchi archivi; i dati già troncati non si ricostruiscono. Dettagli e piano di collaudo in CORREZIONE-NUCLEO-DIALOGO-20261031.md.


## 2026-11-01 — Dialogo reale: riscontro positivo riferito dall'utente
**Prova disponibile:** Alberto riferisce durante uso reale che Jarvis «mantiene abbastanza il contesto» ed è «molto migliorato».

**Decisione e motivo:** registrare un miglioramento percepito nell'uso reale, distinguendolo dai test automatici e da un collaudo completo. Il feedback aggiorna la precedente mancanza di riscontri pratici; non prova da solo tutte le regressioni.

**Limiti:** versione/SHA sul PC non verificato, nessuna misura del numero di turni o ispezione dei prompt. Non attribuire automaticamente il risultato al commit a86c2c9; riavvio, progetti, salvataggi e microfono restano da collaudare. Nessun nuovo test o pacchetto in questa fase. Dettagli nel handoff, sezione 2026-11-01.

## 2026-11-01 — Add-on web e memoria di sviluppo: piano, non implementazione
**Richieste:** navigazione vocale autonoma con GPT esterno e motore locale, solo su richiesta, minimo carico sul Pavilion; add-on separate, UI semplice, reset configurazione e ritorno di versione; diagnostica leggibile e verifiche integrate. Prima di creare, discutere e pianificare per fasi.

**Prove:** letti addon_manager.py, addon_ui.py, self_diagnostics.py, diagnostic_session.py, runtime_diagnostics.py, diagnostic_handoff.py e punti diagnostici di jarvis.py nel ramo evoluto. Il gestore .jaddon ammette azioni descrittive limitate: l'esecuzione web richiede un adattatore revisionato. La diagnostica runtime attuale è passiva e non esegue test funzionali. Blob e limiti sono nel piano.

**Decisione e motivo:** proposta estensione Edge + add-on, per usare il browser esistente; non è ancora provata come soluzione più leggera o affidabile. Separare osservazioni passive, test locali con pagina controllata e collaudo reale GPT/browser. Non riutilizzare il precedente budget 1–2 GB come misura reale.

**Memoria persistente:** AGENTS.md ora impone lettura di handoff, registro e piano più verifica del codice prima delle modifiche; checkpoint di fase con fatti, motivazioni tecniche sintetiche, test/esiti e prossimo passo. Regola commit cf19eff734c7b85e81fa296f73b7b258d3aafc1c. Gli approcci falliti restano esclusi dai riferimenti raccomandati, con causa/lezione conservate.

**Risultato:** piano docs/PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md creato nel commit 04c8bf86c3f39158f6dd14b8cd9cb1125a541d3a e aggiornato con checkpoint. Nessuna implementazione, nuovo workflow, prova funzionale o misura prestazionale. Conservare distinzione tra proposta e verifica.

## 2026-11-01 — Responsabilità nello sviluppo
**Richiesta e scelta:** l'utente non programma e vuole occuparsi delle decisioni di prodotto. L'assistente assume pianificazione, scelte tecniche motivate, realizzazione autorizzata, test e continuità; interventi manuali inevitabili sul PC guidati un passo alla volta. Regola aggiunta ad AGENTS.md e al piano web. Il piano è documentato, l'implementazione resta non avviata. Nessun nuovo test o workflow.

## 2026-11-01 — Continuità fra attività
L'utente richiede recupero dei progetti precedenti anche dopo un cambio di argomento. Creato docs/STATO-ATTIVITA.md nel commit d074634e96b584c1a1f339176ea22962108a357b, con fonti e punti di ripresa per web, dialogo e metodo. Regola in AGENTS.md: recuperare dati confermati, distinguere proposte/autorizzazioni/esecuzione, aggiornare checkpoint prima di sospendere. Solo documentazione: nessuna nuova funzione runtime o test.

## 2026-11-01 — Recupero iniziale e aggiornamento a ogni modifica
**Decisione:** RECUPERO.md come ingresso unico, creato nel commit aa1bce7e0f56ce4ede2258fe5e6742f14ded4186; AGENTS.md ne impone la lettura all'avvio e collega indice/handoff/lezioni/piano. Aggiornare continuità per ogni modifica e prima di sospendere, raggruppando edit correlati in checkpoint coerenti.
**Motivo:** recuperare fatti e autorizzazioni senza dipendere dal contesto della chat e senza ripetere lavoro o errori. Se una richiesta è incompatibile, proporre alternative motivate invece di seguirla alla cieca.
**Limite:** regole documentali verificate per presenza, non un test con una nuova istanza; la sessione deve avere accesso al repository. Nessun caricamento automatico garantito in chat esterna; nessun nuovo test runtime o implementazione web.

## 2026-11-01 — Handoff continuo, non a richiesta
Precisazione dell'utente: recupero necessario anche se la sessione termina all'improvviso. Regola in AGENTS.md e RECUPERO.md: checkpoint prima di ogni modifica coerente, subito dopo e dopo le verifiche. Stato «in corso» recuperabile confrontando codice/diff/commit. Non limitarsi al salvataggio di fine turno e non promettere che scritture interrotte siano persistite. Modifica solo documentale, nessun test runtime.

## 2026-11-01 — Prevenzione degli errori con revisione limitata
**Problema:** individuare incompatibilità solo alla build finale, oppure ripetere controlli senza un criterio di arresto.
**Decisione:** progetto basato su fonti reali, consultazione delle lezioni pertinenti, una revisione iniziale e un ricontrollo mirato delle correzioni. Una criticità bloccante residua richiede scelta o prova di fattibilità limitata; il numero di revisioni non autorizza a ignorarla. Dopo approvazione provare subito un percorso minimo completo e poi ampliare.
**Apprendimento operativo:** errore riprodotto → evidenza/causa o ipotesi → rimedio verificato → lezione preventiva e test di regressione quando utile. Riutilizzare solo nel contesto pertinente, senza ripetere tutte le verifiche del progetto.
**Ambito:** procedura salvata in AGENTS.md e piano web; non dimostra efficacia empirica o assenza di bug. Nessuna implementazione, nuova build o test runtime in questa fase.

## 2026-11-01 — Ogni add-on con test propri nel repository
**Decisione:** ogni nuova add-on include test automatici propri e prove d'integrazione prima della consegna, più regressioni pertinenti di Jarvis e verifica del pacchetto. I test delle parti reali non sono sostituibili da sole simulazioni; controlli obbligatori non eseguiti bloccano la dichiarazione di prontezza.
**Motivo:** individuare in sviluppo errori riproducibili di interfaccia, collegamento, configurazione e recupero, senza farli scoprire all'utente nell'installazione. Sul PC rimangono account, dispositivi, prestazioni e ambiente reale.
**Stato:** salvato in AGENTS.md e piano web. Nessun nuovo test implementato/eseguito in questa fase documentale. Non attribuire retroattivamente copertura alle add-on esistenti senza inventario.

## 2026-11-01 — Nessuna aggiunta a sorpresa, add-on completa anche nella voce
**Richiesta:** rispettare l'obiettivo; suggerire prima eventuali extra. Includere comandi vocali e tutti i collegamenti, per evitare una funzione implementata ma non riconosciuta da Jarvis.
**Decisione:** contratto completo frase/trascrizione → GPT esterno/stato → capacità registrata → azione locale → verifica → risposta. Test delle vie voce/testo e disponibilità attivo/disattivo; catalogo capacità, esempi e UI aggiornati insieme. Distinguere simulazioni da audio/microfono reali.
**Stato:** regola e piano aggiornati, nessuna nuova funzione, test o build. Non dichiarare risolto un bug vocale senza una riproduzione e prova della correzione.

## 2026-11-01 — Interpretazione naturale e catalogo veritiero
Richiesta: non dover usare parole esatte e ricevere un elenco aggiornato quando si chiede cosa Jarvis può fare. Decisione: interpretazione GPT esterna basata su significato e contesto, esempi non vincolanti, chiarimenti sui dati mancanti; registro delle capacità come fonte per azioni e descrizione di ciò che è realmente disponibile. Test previsti per parafrasi e ciclo attiva/disattiva/rimuovi. Solo regole e piano aggiornati; nessuna prova funzionale o modifica runtime.

## 2026-11-01 — Sorgenti versionati e indice di integrazione
**Richiesta:** codice intero disponibile nel repository, nuove add-on costruite su ciò che esiste. Verificato inventario Git del ramo feature/timer-settings-ui-20261031: 167 voci non troncate, moduli/bridge/test/workflow presenti; riferimento evoluto 5e61e53. Main mantiene sorgenti storici alla radice. Creato docs/INDICE-SORGENTI.md con punti d'ingresso e fotografia dei file; collegato da AGENTS/RECUPERO. Non è una build o verifica di tutte le dipendenze.
**Decisione:** versionare sorgenti completi, test e istruzioni; collegare pacchetti a SHA e prove; aggiornare indice/mappa quando cambiano. Riutilizzare la struttura esistente verificando i punti interessati. Nessuna copia massiva su main, merge o modifica runtime. Nessun nuovo test.

## 2026-11-01 — Installazione completa, ordine e consegna scaricabile
**Richieste:** cartella per installazione/configurazione di tutti i moduli e reinstallazione; rilevazione componenti mancanti; valutazione dei file superati a ogni aggiunta; domande specifiche sui dubbi sostanziali; annuncio di una nuova funzione soltanto dopo download effettivamente disponibile in Download/README.md.
**Prove:** consultati import di 60 moduli non-test e script/configurazioni del riferimento 5e61e53. Individuate contraddizioni documentali sul microfono ON rispetto al runtime in standby e la distinzione tra profilo Trial e SDK/account/modello condivisi.
**Intervento:** nove guide in Prima-installazione, collegamento dall'ingresso README, regole e piano aggiornati. Controlli dipendenze esistenti distinti da unificazione in chat ancora da implementare. Fonti Telegram/Python e Gyan consultate per istruzioni esterne. Guide iniziali create da 949ce9d6bde5cd14d8ffef3ace1fb23b8eb16b6f a 238be19be7ee0f1036b42aa7863219fc7962c71b, con correzione testuale successiva.
**Limiti:** nessuna installazione Windows o nuova suite runtime, nessun pacchetto/merge; nessun file sorgente eliminato. Il controllo dei collegamenti documentali non prova l'installazione. Non trasformare vecchi echo o documenti in descrizione di comportamento corrente.

## 2026-11-01 — Consumi di ogni add-on sul PC target
Richiesta: ogni add-on progettata per occupare poca RAM sul Pavilion i3-2100/10 GB. Regola: valutare dipendenze/processi e caricamento su richiesta, misurare RAM incrementale in condizioni comparabili e a fine attività, preservando affidabilità e controllo manuale. Nessun benchmark o tetto numerico dichiarato in questa fase; soltanto requisito e metodo aggiornati.

## 2026-11-01 — Percorso ibrido confermato dall'utente
**Evidenza:** nel riferimento letto, voce in Conversazione GPT prova gestori locali e speech_to_local_command prima del modello; nelle altre modalità il testo non riconosciuto può fermarsi nel campo di input. Questo è comportamento del codice, non prova di ogni errore sul PC.
**Scelta:** mantenere comando preciso locale senza GPT. Ricorrere al modello esterno per formulazioni non risolte o ambigue, entro modalità/connessione consentite; il motore riceve l'azione validata. Chiedere quando resta dubbio e collegare «sì» all'attività pendente.
**Lezione:** non confondere priorità locale con difetto da eliminare né trasformare interpretazione naturale in obbligo di chiamare sempre GPT. Nuove prove devono verificare entrambi i percorsi. Solo documentazione aggiornata, nessuna correzione runtime o nuovo test.

## 2026-11-01 — Allineamento finale e fermo prima del codice
Riconciliate le formulazioni generiche GPT con la decisione ibrida finale; corretta la clausola storica che sembrava lasciare in attesa il nucleo già approvato/corretto. Esplicitata ricerca web e confronto riuso/adattamento/sviluppo. STATO-ATTIVITA e RECUPERO ora riportano il medesimo arresto: metodo allineato, revisione tecnica web fase 1 pendente, fasi 2–8 non avviate. L'utente richiede stop prima dell'implementazione. Controlli soltanto documentali, nessun codice, nuovo test runtime, misura RAM, merge o pacchetto. Prossimo passo alla ripresa: completare revisione tecnica, poi presentare risultato prima del via al codice.

## 2026-11-01 — Registro di recupero persistente e tracciabilità
Creato Download/REGISTRO-VERSIONI.md con schema delle prove e inventario di 20 ZIP già presenti al commit bb94afa1865fe0315021f783736be3cb77c4af84. Esistenza/dimensione/Git blob SHA verificati, non download o collaudo PC dei contenuti. Nessuno promosso a stabile per supposizione. Il feedback sul dialogo non identifica ancora lo ZIP installato; a86c2c9 non ha nuovo pacchetto consegnato in questa fase. Per le versioni future collegare motivazione tecnica, commit, SHA-256 del pacchetto, test, collaudo PC e dati compatibili. Recupero diretto dalla scheda invece di scansione della storia. Solo documentazione, nessun ripristino o build.

## 2026-11-01 — L'utente sceglie la build attuale come base funzionante
Riscontro esplicito: l'ultima build usata funziona bene per il momento; conservarla e partire da quella per le prossime aggiunte. Creato riferimento BASE-UTENTE-20261101 nel registro. Nome ZIP/commit installato ancora da confermare; candidato in cima a Download è Jarvis-Timer-Audio-Fix2-20261031.zip, non automaticamente associato al PC. Preservare pacchetto e codice identificati prima di intervenire. Nessuna nuova build, prova runtime o ripristino.

## 2026-11-01 — Audit reale: il pacchetto confermato precede la correzione nucleo
**Prova:** ZIP prelevato e hash calcolato sui byte; 155 file coincidono con b936879a431370d206152be7b089baf587d15499 e ZIP ricreato identico. Log publisher e merge CI coincidono. Sullo ZIP estratto 373 test OK (5 Windows saltati), compileall e sintassi Node PASS; log remoti Windows/Linux 373 per job riletti.
**Scostamento:** rispetto a 5e61e53 ci sono 10 file diversi e 5 aggiunti. Il pacchetto non contiene il nucleo a86c2c9 né la sua nuova suite; il suo avvio segue auto_listen, il ramo successivo impone standby.
**Errore documentale corretto:** la prima guida aveva preso come riferimento il ramo successivo, quindi classificava come superati testi ON che sono coerenti con la base pubblicata. Corretto il riferimento, mantenendo entrambe le versioni esplicite.
**Scelta:** preservare b936879 e lo ZIP confermato come base delle aggiunte; valutare separatamente eventuali correzioni successive. Registro con sorgente, checksum, log e dati di recupero. Rapporto docs/VERIFICA-CONCRETA-BASE-20261101.md.
**Lezione:** verificare il contenuto consegnato, non dedurre versione dalla punta del ramo o da una CI più recente. Una suite diversa non è copertura del pacchetto installato. L'audit non prova dispositivi/account reali o prestazioni del Pavilion.

## 2026-11-01 — Chiusura della ripresa concreta
Verificati anche download diretto, integrità dei 20 ZIP conservati, copertura add-on esistente e DDL dei due archivi. Checkpoint incompleto chiuso con indice/handoff aggiornati; modifiche documentali arrivate nel frattempo riconciliate preservandole, senza duplicare manifest e log. Dettagli nel rapporto e package-checks.json. La prova del metodo è questa ripresa con accesso al repository, non una garanzia per ogni chat. Nessuna funzione aggiunta e nessuna dichiarazione di nuova build pronta.


## 2026-11-01 — Scheda per progetto e correzione del fraintendimento sugli appunti
**Richiesta:** discutere alternative prima del browser, salvare nella repository caratteristiche/decisioni per riprenderle dal file. **Scelta:** indice docs/IMPLEMENTABILI.md, modello e schede autonome; piano web esistente collegato senza duplicarlo. Stato e autorizzazioni separati dai requisiti.
**Errore:** l'assistente ha suggerito «appunti vocali» come funzione; l'utente chiarisce che parlava degli appunti presi dall'assistente nella repository. Proposta ritirata, scheda rimossa dall'indice e dal percorso corrente, storia Git conservata. Non confondere istruzioni sul metodo di sviluppo con requisiti del prodotto. Cronometro/promemoria restano solo idee da discutere.
**Ambito:** modifica esclusivamente documentale; nessuna implementazione, test runtime, build o modifica alla base b936879. Verifica prevista: rilettura dei file pubblicati e dei riferimenti. **Prossimo passo:** discutere funzioni desiderate e aggiornare le rispettive schede, nessuna priorità automatica al web.


## 2026-11-01 — Usare Windows quando soddisfa il requisito
**Richiesta:** file/cartelle e avvio programmi scelti nelle impostazioni, linguaggio naturale e catalogo aggiornato. **Precisazione:** minimo peso sul PC, prima riuso del codice e delle funzioni Windows; non un divieto ideologico di nuove dipendenze. Valutare necessità/vantaggio, consumo, affidabilità e manutenzione, senza scaricare scelte tecniche sull'utente.
**Evidenze:** local_engine della base b936879 ha aperture fisse e ricerca limitata a Download; settings non contiene elenco programmi scelti. Registro capacità già presente, con binding espliciti e lista locale anche statica. Fonti Microsoft confermano ShellExecute, Get-StartApps e interrogazione Windows Search con copertura limitata. Fonti e limiti nella scheda implementabili/WINDOWS.md.
**Stato:** requisiti/fattibilità preliminare documentati; dettagli di «verificare file», cartelle e integrazione da discutere. Nessun codice, nuova suite, pacchetto o benchmark. Le fonti Windows non provano il collegamento in Jarvis né installazioni app sul PC. Add-on logica non implica dipendenza esterna aggiuntiva.


## 2026-11-01 — Cercare per indizi, non soltanto per nome
**Riscontro utente:** vuole sia trovare/aprire sia leggere/spiegare file. Nome parziale/prefisso o descrizione senza nome esatto; esempio «cartella d'installazione di Minecraft». **Proposta:** interpretazione GPT dove necessaria e consentita, recupero locale con strumenti esistenti, indizi da collegamenti/configurazione e verifica percorso/ruolo. Distinguere programma, dati e salvataggi, più installazioni e candidati. Non assumere un percorso Minecraft né installazione del launcher dalla chat. Windows Search non dimostra da solo ricerca semantica universale; senza indizi sufficienti chiarire. **Limiti:** proposta documentata in implementabili/WINDOWS.md, nessuna nuova integrazione/test/benchmark; formati da definire. Non ripetere la domanda già risolta «solo apertura oppure anche lettura?». Guida semplice, un punto e una domanda alla volta.


## 2026-11-01 — Piano con prove e miglioramenti senza doppioni
**Decisione dell'utente:** prima un piano verificabile; se una funzione è già presente, migliorarla invece di crearne una nuova parallela. **Applicazione:** piano in cinque fasi nella scheda WINDOWS con inventario responsabilità/limite/modifica/test, prova Windows minima, percorso completo, estensioni progressive e consegna/recupero. Riusare gestori e lettori esistenti dopo inventario, mantenere coerenti catalogo e disponibilità. Regola persistente in AGENTS; add-on per capacità nuove non autorizza duplicazioni o migrazioni automatiche. **Prove attuali:** letture sorgenti/fonti già documentate e salvataggi documentali; nessun nuovo test di integrazione, codice, pacchetto o benchmark. Collegamento concreto Windows/Python da provare, non dato per eseguito. **Prossimo passo:** spiegare/discutere piano e ambito prima del via al codice.
