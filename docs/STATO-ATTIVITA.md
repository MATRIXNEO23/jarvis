# Stato attività Jarvis
Aggiornato il 2026-11-01 dopo «Continua»: audit concreto chiuso, metodo e riferimenti allineati; fermo prima dell'implementazione della nuova add-on. Download diretto e integrità dei 20 ZIP confermati; prove nel rapporto.

## Punto di partenza certo
**BASE-UTENTE-20261101:** Jarvis-Timer-Audio-Fix2-20261031.zip, sorgenti b936879a431370d206152be7b089baf587d15499. L'utente conferma la build attualmente usata; l'audit ha verificato ZIP reale, 155 file contro sorgenti, riproduzione byte-identica e test inclusi.
[Registro con download/checksum](../Download/REGISTRO-VERSIONI.md) · [rapporto e log](VERIFICA-CONCRETA-BASE-20261101.md).

| Attività | Stato reale | Prova e prossimo passo |
|---|---|---|
| Audit della base | Completato | 373 test locali OK, 5 skip Windows; sintassi PASS; CI storica Windows/Linux riletta e codice coincidente |
| Identificazione sorgenti | Completata | Tutti i 155 file uguali a b936879; non al ramo successivo 5e61e53 |
| Guide e riferimenti | Allineamento alla base b936879 | [Prima-installazione](../Prima-installazione/README.md); separati avvio auto_listen della base e standby del ramo successivo |
| Metodo e recupero | Regole e checkpoint salvati | [AGENTS](../AGENTS.md), [RECUPERO](../RECUPERO.md), [handoff](HANDOFF-CODEX-ARCHIFY-20261031.md) |
| Ramo successivo a86c2c9/5e61e53 | Separato, non adottato automaticamente | Correzione nucleo e 386 test documentati, assenti dalla ZIP base |
| Add-on web: requisiti | Raccolti | [Piano](PIANO-ADDON-WEB-E-DIAGNOSTICA-20261101.md), voce naturale, ricerca e azione nel sito |
| Add-on web: progetto tecnico | Da completare sulla base b936879 | Contratto, ricerca/riuso, permessi, integrazione e revisione finita prima del codice |
| Add-on web: codice/test nuovi/pacchetto | Non iniziati | Nessuna nuova distribuzione |
| Diagnostica nuova/reset/ritorno versione/UI | Requisiti pianificati | Non confondere con funzioni già presenti nella base |
| Riordino operativo | Candidati e contraddizioni individuati | Nessun sorgente, launcher, pacchetto o dato cancellato |
| RAM/CPU target, nuovi login/audio/Windows | Non misurati/eseguiti dall'audit | Riscontro utente e CI hanno ambiti distinti |

## Decisioni preservate
Comando preciso locale senza GPT; interpretazione esterna quando necessaria e consentita; chiarimenti contestuali. Nessuna funzione extra non concordata. Utente decide risultati e non programma; assistente realizza il lavoro tecnico autorizzato. Add-on per Pavilion i3-2100/10 GB/Windows 10, caricamento a richiesta e test propri. Dati, compatibilità e controllo manuale microfono preservati. Consegna soltanto con pacchetto verificato e link funzionante in Download.

## Aggiornamento vigente — schede dei progetti
[Catalogo implementabili](IMPLEMENTABILI.md) e schede in implementabili/ creati per recuperare caratteristiche, decisioni, prove, dubbi e prossimo passo di ciascun progetto. Browser sospeso; discutere altre funzioni e concordare priorità prima del codice. Cronometro e promemoria sono proposte dell'assistente, non richieste approvate. Ritirata la proposta appunti vocali nata da un fraintendimento: l'utente chiedeva appunti di sviluppo nella repository. Nessuna modifica runtime, nuova build o test dell'app.

## Attività attuale — Windows, file e programmi
Requisiti dell'utente in [scheda WINDOWS](implementabili/WINDOWS.md): accesso/cartelle, ricerca/apertura file e programmi selezionabili nelle impostazioni, interpretazione naturale e catalogo aggiornato. Riusare Windows/codice esistente quando sufficiente; non è un divieto assoluto di dipendenze nuove, la scelta deve essere motivata da requisiti, consumo e affidabilità. Lettura sorgenti b936879 e documentazione Microsoft svolta, nessun test Windows/benchmark o implementazione. Chiarito dall'utente: ricerca/apertura e lettura/spiegazione entrambe richieste, con nomi parziali e ricerca per indizi/scopo (esempio cartella installazione Minecraft). Non basta cercare una cartella chiamata Minecraft; verificare fonti locali e distinguere candidati. Ambito cartelle e formati iniziali ancora da definire; nessun nuovo test/implementazione. Guida semplice, un punto/domanda alla volta.

## Piano Windows e vincolo contro i duplicati
Piano per fasi salvato nella scheda WINDOWS: inventario con responsabilità → prova minima Windows → miglioramento percorso completo → estensione ricerca/lettura esistenti → verifiche/consegna/recupero. Funzioni già presenti da migliorare nel loro componente, nessun doppione o nuova add-on automatica. Piano/documentazione soltanto; prove d'integrazione, codice e pacchetto non iniziati. Prossimo passo: discussione guidata del piano con esempio concreto, poi delimitare incrementi e autorizzazione.

## Organizzazione manualmente leggibile
Richiesta: nuove add-on/moduli con propria cartella dal nome chiaro e LEGGIMI che orienti fra codice, risorse, test, configurazione e dati reali. Pianificare/verificare compatibilità col gestore esistente; niente duplicati o spostamenti automatici dei moduli attuali. Requisito salvato in AGENTS e scheda WINDOWS; nessun file runtime riordinato.

## Metodo per le riprese e ZIP essenziale
AGENTS/RECUPERO aggiornati: ogni istanza con accesso repo deve leggere il metodo e la scheda, senza farlo ripetere all'utente. Nessuna garanzia di accesso automatico per chat esterne. Prossimi ZIP con soli file operativi/installazione/configurazione/istruzioni essenziali, inclusi sorgenti direttamente eseguiti. Test/handoff/CI e altro sviluppo restano repo; inclusioni motivate e test su ZIP estratto. Publisher b936879 esaminato: oggi include quasi tutto il Git, quindi selezione runtime ancora da implementare. Base/pacchetto confermati invariati.

## Componenti mancanti e istruzioni nella consegna
Richiesti avvisi nella console con nome esatto di add-on/file/dipendenza, funzione interessata e rimedio/script o nome/link verificato per scaricarla. File interni: percorso e pacchetto corretto. Rilevatori Telegram/FFmpeg/Vosk e installa_telegram.bat letti sulla base, da riusare; unificazione console/link non implementata o collaudata ora. Requisito in AGENTS e scheda WINDOWS; ZIP operativo con istruzioni essenziali, base invariata.

## Primo incremento scelto: applicazioni classiche e Store
L'utente sceglie avvio programmi: rilevamento Windows di classici e Store, spunte nelle impostazioni, frase naturale e apertura dell'app corretta (esempio Netflix). Specifica e fonti Microsoft nella scheda WINDOWS; rilevata distinta da avvio collaudato. No sostituzione silenziosa col sito web o promessa di trovare qualunque programma. Nessun codice o prova Windows eseguiti. Prossimo passo specifico: spiegare elenco/spunte/prova apertura e completare contratto/revisione sul gestore esistente prima dell'implementazione.

## Prossimo passo corrente
Discutere con l'utente quali funzioni desidera; salvare nella scheda soltanto le caratteristiche concordate, distinguendo dubbi e proposte. Alla ripresa leggere indice e scheda, verificare i riferimenti; nessuna autorizzazione automatica al codice o al web.

## Prossimo passo precedente, subordinato alla scelta delle priorità
Attendere il successivo via dell'utente; poi leggere questi riferimenti e completare la revisione tecnica dell'add-on sulla base b936879 preservata. La revisione tecnica resta da completare, senza implementare finché non arriva il successivo via dell'utente. Non ripetere la ricerca della base o attribuire alla ZIP i 386 test successivi. Per ripristino usare il registro, non scansionare tutti i commit/artifact.
