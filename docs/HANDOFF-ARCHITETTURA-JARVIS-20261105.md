## 7 novembre2026 — correzione timer scritto autorizzata

Utente conferma: dalla casella «imposta timer 6 minuti» finisce a Gemma. Source0063e2cc05: send_console_input controlla try_timer_command solo se parse_alarm è non-None, quindi i timer saltano il gate; il percorso voce già lo chiama direttamente. parse_timer_command riconosce solo cifre. Richiesti anche «sei minuti» e sveglia «sette e trenta di mattina». Piano minimo: riprodurre con callback reali viaAST e confini timer/modello controllati su Windows; togliere solo il filtro sveglia nel gate timer comune; riusare mappa numeri italiana esistente e qualificatore mattina limitato; conservare precedenze documenti/file/consensi, durata e controlli. Test Windows Red/Green e review indipendente prima di dichiarare corretto. Nessuna nuova build autorizzata da questo passo,006 e dati utente preservati.

## 7 novembre2026 — build006, errore della fixture smoke riprodotto

Run42383777615/source9c6061acc78f6c584232b86a135ed90fb9d605d8:911test verdi per3.11/3.12 (190.426s/133.011s), package fallisce nel controllo positivo. Causa dimostrata dal traceback window_chrome.py:158: il nuovo smoke sostituiva tk.Tk con una funzione, rendendo invalido isinstance(...,(tk.Tk,tk.Toplevel)). La nuova raccolta errori ha rifiutato correttamente l'avvio; prima di essa il vecchio smoke avrebbe potuto dichiarare successo. Correzione solo della fixture: sottoclasse SmokeTk mantiene l'identità di tipo; negative probe/callback gate preservati. AST del codice principale e dei due script smoke valido, nessuna esecuzione Linux. Runtime Jarvis invariato. Review mirata e nuovo dispatch richiesti; nessun artefatto pubblicato dal tentativo fallito.

Nei log della suite emerge lo stesso TypeError solo nella fixture test_telegram_secret_dialog, che patcha tk.Tk con Mock; i911 test risultano comunque OK. Avvisi conservati, non equivalgono a un errore dell'app installata; la fixture storica non viene cambiata in questo passo di build.

## 7 novembre2026 — review build006, controllo callback Tk

Review indipendente build-only: Node del package ora fissato22.12 come la matrice. Individuato limite del nuovo smoke: Tk stampa le eccezioni callback e può uscire0 dopo la chiusura programmata. Verificato sul sorgente tkinter.CallWrapper/report_callback_exception (sola lettura): non rilancia. Il verificatore raccoglie gli errori callback e rifiuta lo smoke al ritorno da main; normale WM_DELETE e timeout preservati. Non è prova di un guasto runtime di Jarvis. Primo dispatch42383621234/source dcd35a81919cd8fe98dcc7ac3e064418184ba96a annullato per sostituire il gate prima della pubblicazione, nessun risultato completo attribuito. Nuovo dispatch necessario dopo salvataggio e ricontrollo. Runtime invariato; nessun test funzionale Linux o dato reale.

## 7 novembre2026 — build006 esplicitamente richiesta, preparazione

Richiesta: «allora pubblicami la build in download». Build/pubblicazione autorizzate per questa consegna, nessuna nuova feature. Base f9458557074b528d2a480c124f54e3efe7ff9e05 (runtime verde970bcb17,911test Windows per Python). Ramo build/jarvis-006-audit-20261107, separato da main. [Spec](superpowers/specs/2026-11-07-build-006-design.md), [piano](superpowers/plans/2026-11-07-build-006-plan.md). Riutilizzare Gemma builder/DLL pinned, profilo invariato, nuova candidata006 con manifest, verifiche estratto e review prima di pubblicare. Vecchi ZIP e dati personali preservati. Nessuna esecuzione funzionale Linux; hardware/audio/account/GGUF reali ancora da verificare.016/023 restano dichiarati.

## 7 novembre 2026 — JRV-AUD-013 verificata nei sorgenti in bozza

Quattro guide operative incluse e obbligatorie, sviluppo/handoff/test/upstream esclusi. Guida voce e messaggi installer coerenti con modalità/preferenze reali, link tecnico online immutabile. Nessun comportamento assistente o profilo cambiato. Fixture012 conserva guard nativi e ZIP vietato.

Source970bcb17e15b9c197ec4fa5766eac6a6519058a6, bozza53, run42378831525 SUCCESS tentativo1:911test su3.11.9 (job128421936403,129.771s) e3.12.10 (job128421936166,151.451s),0failure/errori/skip,3nuovi passati. Red1ed02006/run42378209746:911test/job5failure0errori guide/rimedio;3.11job128420097593139.441s,3.12job128420097746192.454s. Review e ricontrollo indipendenti senza blocchi dopo rettifica dei testi; sintassi/probe/Searchlive3.12 passati con ripristino. Rapporti/evidenza013 preservati.

Nessun build/ZIP/estrazione/installer/download, main/merge/release, test funzionale Linux o dato reale. Verifica guide dall'archivio ancora da fare quando autorizzato; Windows10/hardware/audio/account non provati. Codice/test/guide da confrontare col sourceverde nel checkpoint finale. Stack001–015 salvo016,017–019,021 e022 nel loro ambito conservato;023 aperto. Prossimo020 solo indice documentale da main e riepilogo finale, senza portare lì il runtime.016 indice autonomo resta funzione distinta da progettare, non correzione automatica.

## JRV-AUD-013 — ricontrollo completato, candidata per Green

Nessun blocco statico residuo dopo rettifica dei testi voce; selezione/esclusioni e obbligatorietà corrette, helper012 valido.911test Windows attesi, nessun archivio costruito o installer eseguito. Prossimo esiti/evidenza e verifica remota.

## JRV-AUD-013 — rilievi documentali corretti

Review verifica allowlist/obbligatorietà/esclusioni e segnala due testi da allineare: UI reale HeyJarvis richiede nome a ogni frase, Ascolto continuo accetta richieste dirette senza dettatura; corrette le descrizioni. Corretto anche il print dell'installer modello richiamato dalBAT, mantenendo invariati installazione e preferenze. AST/diff passano, nessun installer eseguito. Assert/fixture012 preservati e rafforzati. Ricontrollo mirato e Green Windows necessari,911attesi; nessun build/ZIP/merge/test funzionale Linux o dato reale.

## JRV-AUD-013 — Red acquisito e candidata minima

Red1ed02006/run42378209746:911test per versione,5failure0errori guide/rimedio esclusi;3.11job128420097593139.441s,3.12job128420097746192.454s. Candidata allowlist esatta quattro guide anche obbligatorie, esclusioni generali conservate. Guida voce aggiornata a preferenze/modalità reali e soloechoBAT corretto; riferimento tecnico Accesso file online immutabile. Fixture012 riceve guide e guard boundary nativi, nessun assert indebolito/ZIP. Review mirata richiesta, Green necessario. Nessun comportamento assistente, dato, installer/download, build/merge o test funzionale Linux.022 passa,023 aperto, futuro pacchetto non verificato.

## 7 novembre 2026 — JRV-AUD-013 avviata: guide operative

Base012605c7056 verificata remota14file/7codice-test-workflow uguali al sourceverde, main pulito f147b1a. Ramo013 isolato. Selettore esclude guide richiamate dall'installer: allowlist esatta delle quattro guide operative, obbligatorie; niente docs di sviluppo/handoff. Aggiornare testo voce storico contraddittorio e rimedi, senza cambiare avvio o impostazioni. Spec/piano prima del runtime, tre regressioni pronte sul selettore reale/percorsi locali,911test attesi. Nessun builder eseguito, ZIP, installer/download, merge, dato reale o test funzionale Linux. ProssimoRed Windows, fix minimo e review.

## 7 novembre 2026 — JRV-AUD-012 verificata nei sorgenti in bozza

Stesso Python già generato ora nei moduli; builder non lo riscrive più dopo i test. Launcher/profili invariati, helper diretti con assert precedenti conservati. Workflow futuro rifiuta modifiche PY/MJS/PS1 e si ferma al primo comando Python fallito. Parità statica con il vecchio codice generato verificata.

Sourceverde a95cbd2884afe1079774419bedabf2f324d1a611, bozza52. Run42377581328 SUCCESS tentativo1:908test su3.11.9 (job128418236381,119.730s) e3.12.10 (job128418236628,137.421s),0failure/errori/skip, tutti7nuovi passati. Red1af0f654/run42377060724:907test/job4failure1errore solo012;3.11job128416727551170.282s,3.12job128416727411157.150s. Review indipendente senza blocchi; un metodo/rafforzamenti aggiunti dopoRed, nessun extraRed rivendicato. Rapporti/evidenza012 preservano confini e risultati.

Sintassi/probe passati, Searchlive3.12 con ripristino. Nessuna build/ZIP/estrazione/DLL reale, publish, merge, test funzionale Linux o dato utente modificato. Writer ZIP vietato e python stub nei test del futuro workflow.022 passa,023 aperto; build vera/Windows10/hardware restano da verificare. Checkpoint finale solo documenti/evidenza con hash da confermare; prossimo013 guide operative nel futuro pacchetto, poi020 indice.016 funzione distinta non implementata.

## JRV-AUD-012 — candidata revisionata pronta per Windows

Red1af0f654/run42377060724:907test per versione,4failure1errore tutti nuovo012;3.11job128416727551170.282s,3.12job128416727411157.150s. Fallback DLL realmente assente nei sorgenti, UI e gate parità mancanti;022 passa,023 non osservato,Searchlive3.12 ripristinato. Candidata sposta esatto Python già generato nei moduli e rimuove riscritture, profili/launcher sorgente invariati. Parità del testo verificata staticamente. Workflow futuro con hash e fail-fast; helper test diretti e assert conservati. Review indipendente readonly senza rilievi bloccanti, rafforzamenti preventivi recepiti.7nuovi/908attesi, un metodo dopoRed senza extraRed rivendicato.

Nessun build/ZIP dell'app, DLL reale o test funzionale Linux. I test del workflow eseguono stub innocuo al posto di python; builder fermato prima di ZIP con writer vietato. Green Windows necessario, estrazione/build vera ancora da autorizzare. Prossimo esiti/checkpoint, poi013.

## JRV-AUD-012 — review preventiva recepita

Rafforzato il test pre-ZIP: deve raggiungere git ls-files, evitando il falso verde dell'assert iniziale dopo spostamento della UI. Il blocco workflow viene ora verificato con pwsh come in CI, su PY/MJS/PS1 e con fallimento py_compile oltre al builder.7nuovi/908attesi, un metodo e questi rafforzamenti dopo il sourceRed1af0f654/run42377060724 (6nuovi/907attesi), nessun ulterioreRed rivendicato. Runtime ancora021/022, nessun build/ZIP/test funzionale Linux; prossimi logRed, spostamento minimo e review finale.

## 7 novembre 2026 — JRV-AUD-012 avviata: parità sorgenti/pacchetto

Base021/0228626d193 verificata remota19file/7runtime-test uguali al sourceverde; main pulito f147b1a. Ramo012 isolato. Il builder riscrive due moduli Python dopo la suite: portare nei sorgenti lo stesso comportamento già presente nel pacchetto, conservando profilo isolato del launcher. Nel workflow futuro hash prima/dopo e stop sul primo comando fallito. Spec/piano salvati prima del runtime.

Sei nuove regressioni pronte: builder reale fermato prima dello ZIP con assets nativi assenti/writer vietato, vero blocco PowerShell in Git temporaneo con pythonstub innocuo, prova UI/fallback DLL dai sorgenti con ABI controllata.907test attesi, runtime ancora021/022. Nessuna build/ZIP prodotto, DLL caricata, test funzionale Linux, merge o dato reale. ProssimoRed Windows/review; verifica del vero pacchetto resterà pendente fino a richiesta esplicita.

## 7 novembre 2026 — JRV-AUD-021 e022 verificate nei sorgenti in bozza

La voce possiede il solo helper avviato dal runner predefinito: close richiede termine senza aspettare sulla UI, scarta la coda e rifiuta il testo quando la pubblicazione arriva dopo chiusura. Custom runner, lista voci, JSON/cwd, chunk e anti-eco conservati. Se Windows nega la terminazione il worker può aspettare l'uscita effettiva, senza mascherare l'errore primario. Nessun altro processo controllato.

022: quattro grafi di fixture Tk riprodotti in otto figli, ognuno con successo UI prima del fatal su worker GC. Pulizia sul thread principale e rilascio dei riferimenti header corretti nei soli test, assert originali e GC dell'app invariati. Il probe finale conferma immagine reale creata e0residui prima del worker, otto returncode0/stderr vuoto. La risoluzione è limitata alle fixture dimostrate; non certifica ogni possibile ciclo Tk del runtime.

Sourceverde3cd88a04b3a645257bc77c24bfcc9cd5fe5770b4, [bozza51](https://github.com/MATRIXNEO23/jarvis/pull/51). [Run42364574425](https://github.com/MATRIXNEO23/jarvis/actions/runs/42364574425) SUCCESS tentativo1:901test per Python3.11.9 (job128379821296,180.165s) e3.12.10 (job128379821451,208.118s),0failure/errori/skip, tutti16nuoviTTS passati. Sintassi/probe e Searchlive3.12 passati, servizio/fixture ripristinati. Rapporti021/022 ed [evidenza](evidence/jrv-aud-021-fix-20261107.json);022 conserva storia e Red controllato separato.

RedTTS556a4b44/run42362426651:897test/job6failure0errori. Candidata6504/run42363252951:3.11 passa900test/172.068s,3.12 abortisce022 prima deiTTS, nessun conto completo. RedTk5991813f/run42363972403:3.11 completa901test/4failure0errori in171.384s;3.12 stampa quattro figli falliti e poi abortisce ancora, nessun riepilogo assegnato. Fallimenti conservati, nessun retry cieco. Tre metodiTTS e rafforzamenti del probe aggiunti dopo i rispettiviRed, nessun extraRed rivendicato. Review indipendenti senza blocchi residui; hash runtimeTTS invariato dalla6504.

Checkpoint finale solo documenti/evidenze, runtime/test da confrontare col sourceverde prima della conservazione remota. Nessun build/ZIP/merge/release, test funzionale Linux, dipendenza, audio/account/microfono o dato/profilo reale. Windows10/i3/HDD e pacchetto estratto non verificati. Conservate001–011,018,014,015,017,019,021 e022 nel suo ambito. Restano012/013 distribuzione,020 indice,016 funzione separata non implementata e023 timeoutCI non risolto. Prossimo012: eliminare differenze Python introdotte dal builder dopo i test e preparare verifiche del futuro pacchetto; nessuna build automatica.

## JRV-AUD-021/022 — candidata con cleanup delle fixture revisionato

Review indipendente readonly ha verificato i log Red e il fix delle quattro fixture: nessun blocco rilevato, assert originali conservati, GC dell'app immutato e runtime TTS identico a6504. Activity/Animated/NativeHUD raccolgono sul thread principale dopo il metodo; header ritira anche i riferimenti persistenti prima della raccolta. Il probe controlla anche una vera immagine come foglia, con osservatore debole, e conserva diagnostica di timeout. Rafforzamenti del probe successivi al primo Red, nessun ulteriore Red rivendicato.

Prossimo: Green completo Windows3.11/3.12,901test attesi con16nuoviTTS e1metodo/4subtestTk. Non dichiarare completata021 o022 finché entrambe le suite non terminano. Rapporti/evidenze conservano il primo blocco e la riproduzione; nessun build/merge/test funzionale Linux/dato reale,023 distinto aperto.

## JRV-AUD-022 — causa delle fixture riprodotta, pulizia candidata

Red5991813f4c2add224e50f375ea36b8838fd1823b/run42363972403:3.11job128378016116901test171.384s4failure0errori tutti subtestGC;3.12job128378016392 stampa4figli falliti poiabortaancoraDocumentSaveRace, nessuncontofinale. Tutti8figli passanoprimalafixture, poiVariable.__del__/Tcl_AsyncDelete suworker conthreadIDdiverso eexit2147483651. AnimatedHUDincludeImage.__del__realesuentrambeversioni. Confermatodifettodiownershipdei4grafi, nonidentificatioggettisingolidiogniabortostorico. EvidenzacontrollataJSON evecchiorapportopreservati.

Candidata solo4fixturetest: Activity/Animated/NativeHud gc.collect nelteardownmain dopo metodoritornato; header spezzacicloenv/callbackeritiraself.env/hud/root dopodestroyprimaGC. Assertoriginaliinvariati, GCappnonmodificato. Reviewpreventiva rafforza diagnosticaTimeout eImageleafreale/WeakSet nonritentiva, nessunextraRedrivendicato. TTSruntime SHA c02a4a4e invariato6504. Green021/022901testattesi ancoranecessario, reviewmiratarichiesta. Nessunbuild/merge/testfunzionaleLinux/audio/account/datoreale.023 distintoaperto.

## 7 novembre 2026 — JRV-AUD-022 ricomparsa, blocca il Green completo021

Candidata0216504abffe0553461a2f44c07c9833d67a2abf2e1/run42363252951:Python3.11.9 job128375837812 SUCCESS900test in172.068s, tutti16nuovi021 passati. Python3.12.10 job128375837908 abortisce durante DocumentSaveRace prima dei021:Variable.__del__/Image.__del__ RuntimeError main thread is not in main loop, poiTcl_AsyncDelete, nessun riepilogo completo assegnato. Search live3.12 passato con servizio/fixture ripristinati; nessun retry cieco o Green dichiarato per021.

022 viene investigata come correzione distinta nella bozza51 perché dipendenza del collaudo021. Ipotesi: fixture HUD precedenti lasciano cicli Tk chiusi, raccolti poi da workerWin32 senzaTk. Nuovo tests/test_aa_tk_lifetime.py prima di editare teardown: un metodo/quattro figli isolati con fixture vere Activity/Animated/header/nativeHUD, GC automatico disabilitato solo nel figlio e raccolta esplicita da worker dopo fixture, nessun error suppression/skip. Diagnostica stampata prima degli assert per conservarla anche se il resto suite abortisce. Poller di rete intercettato, account/audio/profili reali assenti.901attesi se la suite completa; nessuna conta inventata su abort.

Specifica/piano022 salvati, runtimeTTS invariato6504. ProssimoRed022 e review; cleanup Tk sul mainthread solo se la riproduzione lo dimostra. Nessuna modifica GC globale dell'app, build/merge/test funzionale Linux o dati reali.

## JRV-AUD-021 — Red acquisito, candidata revisionata pronta per Windows

Red556a4b4460287fb41f0bf7e7c1d080c6b81ec993/run42362426651 FALLITO:897test/job6failure0errori nel nuovo021.3.11job128373412696144.361s,3.12job128373412895196.734s. Confermati helper/worker vivi dopo close e invio possibile dopo creazione concorrente; baseline precedente passa. Nessun022/023;Searchlive3.12 passato con servizio/fixture ripristinati.

Candidata solo offline_tts.py: Popen posseduto dal default, attach/close/detach per identità sotto lock breve, terminate fuori lock, payload non inviato se pubblicazione rifiutata, pipe/context cleanup prima del detach. Customrunner2arg/listvoices/JSON/cwd/chunk/anti-eco preservati. Review preventiva rafforza close bounded, terminateOSError, cleanupperrisorsa/markeratomico; reviewruntime richiede conservareerrore primario conkillfallita, corretto connota diagnostica e due subtest.16nuovi/900attesi,3metodi dopoRed senza extraRed rivendicato. Ultimo ricontrollo readonly senza blocchi rilevati.

Green Windows ancora necessario, AST/diff locali soltanto. SeOSnega terminate/kill, worker puòaspettare uscitaeffettiva, UIclose nonattende; nessuna promessa di harddeadline nel cleanup. Nessun audio/SAPI/account/profilo reale, nuova dipendenza, build/merge o test funzionale Linux. Rapporto/spec aggiornati, prossimo collaudo Windows e checkpoint remoto.

## JRV-AUD-021 — review preventiva: chiusura bounded e cleanup rafforzati

Review readonly segnala gap di latenza/erroreterminate e rischio di marker parziale. Tutte le close nei test ora chiamate da osservatore bounded, aggiunti worker trattenuto dopo communicate per provare ritorno prima del rilascio e erroreterminate controllato senza interrompere shutdown. Cleanup rilascia barriere, ritira tutti i figli prima di close e prosegue per risorsa raccogliendo errori. Marker pubblicato conrename atomico dopo JSON completo.15nuovi/899attesi, dopo sourceRed556a4b44/run42362426651 (13nuovi/897attesi), nessun extraRed rivendicato. Runtime ancora019, prime prove Windows in corso; nessun test funzionale Linux/build/merge/audio/account/profilo reale.

## JRV-AUD-021 — tredici prove pronte prima del runtime

Nuovo tests/test_tts_process_lifecycle.py: Popen/pipe/figliWindows reali, eseguibile sostituito solo alla frontiera con helperPython silenzioso temporaneo. Copertura close attivo, chunk/coda scartati, close prima di pubblicazione/testo non inviato, doppio close/figlio già uscito, processo estraneo preservato, JSON/argv/cwd, timeout/exitnonzero/avviofallito, customrunner2arg/anti-eco e lista voci. Cleanup ritira sempre anche figli del Red senza orphan.13nuovi/897attesi, runtime ancora019. Review preventiva indipendente avviata; prossima bozza RedWindows. Nessun audio/SAPI/account/profilo reale, build/merge o test funzionale Linux.

## 7 novembre 2026 — JRV-AUD-021 avviata: processo vocale in chiusura

Base019 e059883a1e446ca71452a2358920b4af02001b69, remoto verificato11file/3moduli uguali al sourceverde; main pulito f147b1a. Ramo021 isolato. Il codice close svuota la coda ma non interrompe subprocess.run attivo: il chunk può continuare fino al termine/timeout90s. Conservare e ritirare solo il Popen creato dal runner vocale, sincronizzando pubblicazione/close senza attese sotto lock. Compatibilità runnercustom2arg, lista voci, JSON/cwd e anti-eco preservati. Nessun taskkill o gestione di app estranee, nessun nuovo mute/microfono. Specifica/piano prima del runtime; prossime prove RedWindows con figli temporanei reali, senza audio/account. Nessuna build/merge/test funzionale Linux/dato reale.

## 7 novembre 2026 — JRV-AUD-019 verificata nei sorgenti in bozza

Corrette soltanto etichette/testo e docstring: il pannello memoria indica caratteri nel prompt (spazi inclusi), Context Size/Max Output Gemma indicano token, sintesi automatica e suo limite dichiarati non collegati. Nessun tokenizer, attivazione di sintesi o migrazione. ConfrontoAST con la base conferma defaults/schema, budget/validate/save e callbacksave UI identici. Valori e algoritmo non cambiano.

Base017 530fad08, sourceverde190cac1e1080134de06e64ed241079ba07a7a369, [bozza50](https://github.com/MATRIXNEO23/jarvis/pull/50). [Run42361597736](https://github.com/MATRIXNEO23/jarvis/actions/runs/42361597736) SUCCESS tentativo1:884test per Python3.11.9 (job128370965405,139.336s) e3.12.10 (job128370965635,137.486s),0failure/errori/skip. Sintassi/probe passati, Searchlive3.12 con servizio/fixture ripristinati. [Rapporto](CORREZIONE-JRV-AUD-019-20261107.md), [evidenza](evidence/jrv-aud-019-fix-20261107.json). Nessun nuovo test speculare delle stringhe o Red runtime rivendicato per questa correzione di testo; nessuna review indipendente rivendicata.

Checkpoint finale solo documenti/evidenza, tre moduli da confrontare col sourceverde prima di dichiarare conservazione remota. Nessuna build/ZIP/merge/release, test funzionale Linux, dipendenza o dato/profilo reale. Budget caratteri non è tokenizzazione GGUF né garanzia per ogni Unicode; layout PC, Windows10/i3/HDD e pacchetto estratto non verificati.022/023 non osservati, restano aperti. Conservate001–011,018,014,015,017,019. Prossimo021: annullamento del processo vocale posseduto in chiusura, mantenendo runner personalizzati e anti-eco. Distribuzione012/013 e indice020 separati;016 nuova funzione da valutare, non implementata automaticamente. Build solo su richiesta esplicita.

## JRV-AUD-019 — etichette/docstring corrette, verifica Windows necessaria

Pannello memoria chiarisce caratteri/spazi inclusi e sintesi non collegata; summary_max_tokens non presentato come limite attivo. Pannello Gemma indica token per Context Size/Max Output. Docstring del metodo legacy spiega che budget in caratteri non è tokenizzazione. ConfrontoAST statico con base: algoritmo budget/defaults/schema e callbacksave identici, nessuna modifica a dati o valori. Nessun nuovo test speculare di stringhe né Red runtime rivendicato. Guida e rapporto aggiornati, suite/probe Windows esistenti da acquisire; nessun test funzionale Linux/build/merge/tokenizer/dipendenza. Layout PC reale/tokenizzazioneGGUF non verificati;022/023 restano aperti. Prossimo: CI e checkpoint remoto, poi021.

## 7 novembre 2026 — JRV-AUD-019 avviata: chiarire caratteri e token

Base017 530fad08935f29b2909a6ae2481a19cf77dcefc8, remoto verificato12file e5runtime/test uguali al source verde; main pulito f147b1a. Ramo019 isolato. Il budget prompt600 è applicato conlen(str), non tokenizer. Context Size/Max Output sono token del backend; summary_max_tokens soltanto validato e non usato da sintesi collegata. Correzione di etichette/testo/docstring: schema JSON/API/valori/algoritmo invariati, nessuna sintesi attivata o dipendenza. Specifica/piano salvati prima dell'edit. Suite Windows esistente da eseguire per regressioni, nessun nuovo test speculare di etichette o Red runtime rivendicato. Nessuna build/merge/test funzionale Linux/dato reale.

## 7 novembre 2026 — JRV-AUD-017 verificata nei sorgenti in bozza

HUD thinking/reasoning include attività dell'owner Gemma già esistente e flag chat pendente, anche con GPT spento e da Telegram/prova impostazioni. La sessione conta operazioni attive/in coda, con finally e metadata lock breve; nessun caricamento/I/O/attesa del lock d'inferenza per leggere is_busy. Nessun nuovo poller o fase dettagliata inventata. Stop/close non dichiarano idle prima dell'uscita effettiva, errori e annidamento scaricano il contatore. Risposte, permessi, memoria e priorità voce preservati.

Base015 55813517, sourceverde d5a58c901f5c7c283ca6369fd6af405592e1996c, [bozza49](https://github.com/MATRIXNEO23/jarvis/pull/49). [Run42360995994](https://github.com/MATRIXNEO23/jarvis/actions/runs/42360995994) SUCCESS prima verifica del source con fixture completa:884test per Python3.11.9 (job128369166220,122.925s) e3.12.10 (job128369166047,130.016s),0failure/errori/skip, tutti15nuovi metodi passati. Sintassi/probe passati; Search live3.12 con servizio/fixture ripristinati. [Rapporto](CORREZIONE-JRV-AUD-017-20261107.md), [evidenza](evidence/jrv-aud-017-fix-20261107.json).

Red5ac6e9d1/run42360223737:883test/job,18failure0errori solo nuovo017/subtest;3.11job128366829486118.761s,3.12job128366829253132.637s. Review rafforza loader spies e stop non cooperativo:1nuovo metodo dopoRed, nessun extraRed rivendicato. Candidata0419b5b7/run42360619718 fallita884test/job0failure3errori nella fixture header: envAST privo di owner/flag, mentre15nuovi017 passano. Completata fixture con stati inattivi, tuttiassert preservati, diagnosi ricontrollata readonly e runtimehash identici prima/dopo. Nessun retry cieco; review runtime senza blocchi rilevati.022/023 non osservati, restano aperti.

Checkpoint finale solo documenti/evidenze, runtime/test da confrontare con il sourceverde prima di dichiarare conservazione remota. Nessuna build/ZIP/merge/release, test funzionale Linux, dipendenza o dato/profilo reale modificato. ABI controllata con componenti veri e UI Tk Windows, non modello/DLL/account/microfono, Windows10/i3/HDD o pacchetto estratto. Conservate001–011,018,014,015,017. Prossimo019: rendere chiare le unità del contesto memoria, mantenendo schema JSON/valori/budget; nessun tokenizer nuovo o sintesi automatica attivata. Build solo su richiesta esplicita.

## JRV-AUD-017 — fixture header ricontrollata, seconda verifica Windows necessaria

Review indipendente readonly conferma diagnosi NameError e modifica di soli due contenitori inattivi nella fixture HeaderQuickControlTests.wire; nessuna asserzione o callback attenuata. Runtime invariato rispetto0419b5b7 e hash da confrontare col prossimo source. Fallimento Green1 conservato, Green2 da acquisire;884test attesi. Nessuna build/merge/test funzionale Linux/dato reale. Prossimo: collaudo e checkpoint remoto.

## JRV-AUD-017 — prima candidata fallita: fixture header da completare

Source0419b5b7d31ca320a1fae9c48becd1f8efad5819/run42360619718 FALLITO:884test per job,0failure3errori.3.11job128368034045157.873s,3.12job128368034166121.567s. Tutti15nuovi metodi017 passano. Tre test header estraggono il provider HUD viaAST con env parziale: NameError gemma_trial_busy (manca anche owner). Nell'app reale entrambi sono inizializzati prima di registrare il provider. Causa fixture dimostrata, non022/023; Search live3.12 passato e stato/fixture ripristinati.

Aggiunti soltanto owner=None eflagFalse a tests/test_hud_quick_toggles.py:wire; tutti gli assert esistenti di clic/persistenza/rollback/memoria conservati, runtime identico alla candidata. Nessun retry cieco o test indebolito. Review mirata su fixture da richiedere e nuova verifica Windows necessaria;884attesi. Nessun build/merge/test funzionale Linux/dato reale. Fallimento conservato nel rapporto017.

## JRV-AUD-017 — Red acquisito e candidata revisionata pronta per Windows

Red source5ac6e9d1e90f4c6ebc02d7d60d37161a4d1d2b5f/run42360223737:883test per job,18failure0errori tutti nel nuovo017 (subtest inclusi);3.11job128366829486118.761s e3.12job128366829253132.637s. Manca lo snapshotBoolean e la veraUI Tk mostra MICROFONO SPENTO durante generazione nativa. Baseline precedente passa, nessun022/023 osservato; Search live3.12 passato con servizio/fixture ripristinati. Nessun retry cieco.

Candidata nei due componenti esistenti: contatore finally e propertyis_busy sul metadata lock nella sessione, provider HUD legge owner già creato e flag chat pendente indipendentemente da GPT. Nessun caricamento/I/O/attesa inference per status, né nuovo poller. Review runtime indipendente readonly senza blocchi rilevati; gap test recepiti,15nuovi/884attesi,1metodo e loader spies aggiunti dopoRed senza rivendicare altroRed. Green Windows ancora necessario; AST/diff locali soltanto. Nessuna build/merge/test funzionale Linux/profilo reale modificato. Prossimo: suite Windows e checkpoint evidenze.

## JRV-AUD-017 — review preventiva recepita nei test

Review readonly senza difetti confermati nella specifica/test; rafforzati due gap: config_loader/memory_loader intercettati negli snapshot idle per vietare I/O implicito, nuovo stop con abort ignorato che resta busy fino all'uscita reale del backend.15nuovi/884attesi; modifiche successive al sourceRed5ac6e9d1/run42360223737 (14nuovi/883attesi), senza rivendicare un ulterioreRed. Cleanup della UI Tk garantito anche se il worker tarda. Runtime ancora015, Green non eseguito. Rapporto017 avviato con limiti; nessun build/merge/test funzionale Linux/dato reale. Prossimo: log Red e correzione minima.

## JRV-AUD-017 — quattordici prove pronte prima del runtime

Nuovo tests/test_native_hud_activity.py riusa fixture factory/bridge/sessione e ABI controllata; provider HUD e callback Telegram reali, UI impostazioni generata solo in temporaneo senzaZIP. Copertura chat/turno differito/Telegram/prova/programmi, preparazione, ask annidato in commit, attesa lock, abort ignorato/timeout e stop, errori/configurazione/close, nessun caricamento da idle, flag GPT/local/documento e stato Tk reale con priorità voce. Osservatore bounded evita blocco se status prendesse inference lock.14nuovi/883attesi; runtime ancora015, fixture ActivityStatus aggiunge solo owner/flag inattivi. Review indipendente preventiva avviata. Prossimo Red Windows, nessun test funzionale Linux/build/merge/dato reale.

## 7 novembre 2026 — JRV-AUD-017 avviata: attività Gemma nel HUD

Base015 558135173a13ca7bdaddfc543c63897730633353, remoto verificato10file e runtime/test uguali al source verde; main pulito f147b1a. Ramo017 isolato. Il provider HUD ignora l'owner nativo condiviso: correggere l'indicatore con metadati della sessione, senza getter che crei o carichi il modello. Contatore delle operazioni attive/in coda con finally, lettura su lock breve e niente I/O; reasoning/thinking includono attività nativa e flag chat pendente. Nessuna nuova fase inventata o poller; priorità voce/GPT/ricerca preservate. Specifica/piano017 salvati prima del runtime. Fixture ActivityStatus aggiunge solo owner/flag inattivi. Prossimo: test Red Windows e review. Nessuna build/merge/test funzionale Linux o dato reale modificato.

## 7 novembre 2026 — JRV-AUD-015 verificata nei sorgenti in bozza

La ricerca ora condivide una deadline tra indice Windows e scansione: timeout min(8s,residuo), nessun nuovo budget per il fallback. Risultati validi conservati con copertura parziale time_limit, annullamento/revoca prevalgono, callback legacy a due argomenti senza retry TypeError. Radici e reinclusioni non rimosse,20risultati/5000voci e spunte invariati. Nessun nuovo indice016 o dipendenza.

Base014 4f436630, source verificato bd722353fce33a38647e102778eb585579cb428e, [bozza48](https://github.com/MATRIXNEO23/jarvis/pull/48). [Run42359421674](https://github.com/MATRIXNEO23/jarvis/actions/runs/42359421674) SUCCESS prima candidata runtime:869test per Python3.11.9 (job128364417473,126.668s) e3.12.10 (job128364417195,130.805s),0failure/errori/skip, tutti17nuovi metodi passati. Sintassi/probe passati; Search live3.12 con servizio e fixture ripristinati. [Rapporto](CORREZIONE-JRV-AUD-015-20261107.md), [evidenza](evidence/jrv-aud-015-fix-20261107.json).

Red82379bfe/run42358971980:867test/job,10failure0errori nel nuovo015;3.11job128363078992192.808s e3.12job128363079143181.795s. Causa dimostrata, nessun retry cieco. Review preventiva rafforza TypeError interno e risultato fallback selezionabile dopo scadenza:2metodi aggiunti dopoRed, senza rivendicare altroRed. Review runtime indipendente readonly senza blocchi rilevati.022/023 non osservati, restano aperti.

Checkpoint finale solo documenti/evidenza, runtime/test da confrontare con il source verde prima di dichiarare conservazione remota. Nessuna build/ZIP/merge/release, test funzionale Linux o dato/profilo/credenziale reale modificato. Tempo controllato nei test, non benchmark Windows10/i3/HDD né hard timeout su I/O/callback non cooperativa; Known Folders/policy e localizzazione registrazioni precedono il budget. Prossimo017: indicatore HUD mentre Gemma elabora, senza creare/caricare modello per leggere lo stato. Conservate001–011,018,014,015;016 resta una funzione separata da valutare, build soltanto su richiesta esplicita.

## JRV-AUD-015 — review runtime completata, Green Windows da acquisire

Review indipendente readonly sul diff esatto dalla014 senza rilievi bloccanti: una deadline, timeout residuo, directory vuote, risultati/cancellazione e protocollo legacy verificati staticamente. Entrambi i gap preventivi recepiti,17nuovi/869attesi. Non è una prova eseguita: suite Windows e probe ancora necessari. Runtime candidata soltanto in file_access/service.py, guida operativa e rapporto aggiornati; nessuna build/estrazione/pubblicazione autorizzata. Main, versioni precedenti, dati e permessi conservati. Prossimo: esito Green, eventuali errori analizzati e checkpoint remoto.

## JRV-AUD-015 — Red Windows acquisito, candidata minima da verificare

Red1 source82379bfe793aa35938542408ff007a7cc5e02903/run42358971980:867test per job,10failure0errori tutti nel nuovo015;3.11job128363078992192.808s,3.12job128363079143181.795s. Confermati timeout8s ripetuti, nuove scansioni oltre limite, falsa copertura completa e nessun controllo del tempo tra directory vuote. Nessun022/023 osservato; Search live3.12 eseguito separatamente, nessuna build. Nessun fallimento occultato o retry.

Candidata soltanto in file_access/service.py: deadline unica indice/fallback, timeout min(8,residuo) al wrapper produzione, protocollo legacy2arg senza retry TypeError, controlli prima di directory e voci, scadenza con risultati validi e copertura parziale. Review preventiva ha rafforzato TypeError interno e risultato fallback conservato:17nuovi/869attesi,2aggiunti dopoRed senza rivendicare ulterioreRed. Review runtime readonly richiesta; Green Windows ancora da eseguire, AST/diff locali soltanto. Nessun nuovo indice/dipendenza/build/merge o dato utente modificato. Prossimo: recepire rilievi e Green.

## JRV-AUD-015 — quindici prove pronte prima del runtime

Nuovo tests/test_file_search_deadline.py: wrapper Windows reale con subprocess e orologio controllati, add-on/policy/filesystem temporaneo reali. Copre budget globale multiradice, timeout residuo e cap8s, fallback con residuo e directory vuote, progressi che consumano il budget, risultati validi tardivi/selezione numerica, esclusioni e reinclusioni, callback legacy, cancellazione/revoca e nuova passata senza toccare il profilo.867test attesi; runtime invariato014. Review indipendente preventiva avviata; Red Windows da acquisire in bozza, nessuna esecuzione funzionale Linux/build/merge. Lentezza simulata, non benchmark HDD; nessuna garanzia hard timeout su I/O o callback non cooperativa.

## 7 novembre 2026 — JRV-AUD-015 avviata: scadenza globale della ricerca

Base014 4f436630b3aae935c808b13e798c9b8991fdedc8, ramo isolato fix/jrv-aud-015-search-deadline-20261107. Il servizio applica8s per ogni radice e avvia soltanto dopo il budget10s di scansione; attesa teorica cumulativa, non misurata sul PC. Riusare il timeout già presente nel wrapper Windows con il residuo di una sola deadline, conservando radici, permessi/reinclusioni, risultati validi e cancellazione. Dichiarare copertura parziale alla scadenza. Callback iniettate legacy a due argomenti conservate; nessuna promessa di hard timeout su I/O o callback non cooperativa. Specifica/piano015 salvati prima del runtime. Prossimo: test Red Windows, poi intervento minimo e review. Nessuna build/merge/test funzionale Linux, nessun dato o impostazione reale modificato;016 non implementata.

## 7 novembre 2026 — JRV-AUD-014 verificata nei sorgenti in bozza

L'autodiagnosi ora include le quattro cartelle runtime approvate, con priorità rispetto ai test, senza eseguire o inviare il codice. Mantiene140file/260000byte e limita a140anche le directory enumerate. Profili, cache, modelli, upstream, link/junction e cartelle Hidden Windows sono esclusi; limiti e copertura restano visibili anche dopo molti errori. File spariti o metadati illeggibili non interrompono il resto. Nessun nuovo comando o indice.

Base01876e392f, source verificato d74333ebe09182a8d3aa84f571fc664be405e51f, [bozza47](https://github.com/MATRIXNEO23/jarvis/pull/47). Conservate001–011,018 e014. [Run42357790841](https://github.com/MATRIXNEO23/jarvis/actions/runs/42357790841) SUCCESS al tentativo1 del source corretto:852test per Python3.11.9 (job128359597362,121.214s) e3.12.10 (job128359597262,149.326s),0failure/errori/skip. Tutti23nuovi metodi passati, incluse junction, attributo Hidden e alias8.3 reali. [Rapporto](CORREZIONE-JRV-AUD-014-20261107.md), [evidenza](evidence/jrv-aud-014-fix-20261107.json).

Red1:1d69632/run42355483101,844test/job14failure+2errori; Red2:4ec1a9f/run42355703061,846test/job16failure+2errori. Errori reali di stat/file sparito, nessun022/023. Review preventiva rafforza privacy interna; review runtime trova limite nascosto da molti errori e Hidden Windows, entrambi corretti. Prima candidata f423fdb6/run42357007265 fallisce851test/job1failure+8errori per fixture conTEMP8.3 confrontato con path canonico: radice della fixture risolta, spy rafforzato e caso pubblico GetShortPathNameW aggiunto. Runtime identico alla prima candidata; hash confrontati. Vecchio testo di assenza modulo aggiornato all'inventario accessibile, con caso file davvero assente e0consigli preservato. Ultima review indipendente senza blocchi rilevati.

Sintassi/probe passati, Searchlive3.12 con servizio/fixture ripristinati. Checkpoint finale solo documenti/evidenze, runtime/test uguali al source verde. Nessuna build/ZIP/merge/release, test funzionale Linux, profilo/dato/credenziale reale modificato o nuova dipendenza. Prove statiche su fixture e checkout, non Windows10/i3/HDD, modello, account, microfono o pacchetto estratto. Non è una sandbox contro modifiche malevole concorrenti né audit universale;022/023 restano aperti.

Prossimo015: limite globale delle interrogazioni dell'indice Windows e della passata di ricerca, preservando permessi, cancellazione e risultati validi. Nessun nuovo indice persistente016.012/013 e019/020 restano separati; continuare correzioni mirate autorizzate, build soltanto su richiesta esplicita.

## JRV-AUD-014 — prima candidata fallita per fixture Windows8.3

Sourcef423fdb6/run42357007265 FALLITO:851test per job,1failure+8errori solo nel nuovo014.3.11job128357180996133.861s,3.12job128357181094124.005s. Le fixture confrontavano il TEMP con aliasRUNNER~1 con i percorsi canonici runneradmin restituiti correttamente dall'inventario;8relative_to sollevanoValueError e lo spy della directory negata non scatta. Non è un difetto dimostrato del runtime, né022/023. Nessun retry cieco.

Normalizzata la radice della fixture conresolve(strict=True), mantenendo tutti gli assert e rendendo sensibili gli spy. Rafforzato testmetadata con contatore che prova l'effettiva negazione; aggiunto caso reale GetShortPathNameW suAPIpubblica per stessa copertura eprunatura dati conalias8.3.23nuovi/852attesi. Runtime invariato dalla candidata; nuova verifica Windows necessaria. Revisione indipendente mirata da richiedere prima Green2. Nessun testfunzionaleLinux/build/merge o dati reali, failure conservato nel rapporto/evidenza.

## JRV-AUD-014 — candidata pronta per Green Windows

Due componenti runtime esistenti, nessuna nuova dipendenza o indicizzatore. Inventario approvato e priorità runtime, criteri metadata/esclusione condivisi,140file/140directory e260000byte per file. Limiti visibili anche dopo molti errori, NoModule qualificato senza dichiarare inesistenza del programma. Hidden Windows e junction esclusi prima della lettura. Reviewer ricontrolla gli antenati lessicali prima del resolve; stat/file spariti non interrompono il resto.

Review preventiva e runtime con due correzioni della candidata recepite; ultimo ricontrollo senza blocchi.22nuovi/851attesi,5aggiunti dopoRed2 e vecchio assert di wording aggiornato intenzionalmente con verifica di file realmente assente/0consigli. Rapporto014 e guida operativa aggiornati. Red1/Red2 documentati con tutti esiti e limiti; nessun test funzionale Linux, soloAST/diff locali. Prossimo: Green Windows e checkpoint remoto, niente build/merge, profili o credenziali toccati.022/023 restano aperti.

## JRV-AUD-014 — Red acquisito e rilievi runtime corretti

Red1 source1d69632/run42355483101:844test per job,14failure+2errori;3.11job128352529225154.869s,3.12job128352529347142.961s. Red2 source4ec1a9f/run42355703061:846test per job,16failure+2errori;3.11job128353233323141.023s,3.12job128353233067207.049s. Errori reali di stat/file sparito, tutto nel nuovo014; junction create, nessuno skip e022/023 non osservati.

Candidata nei due componenti esistenti: whitelist runtime ricorsiva, dati/cache/upstream esclusi,140file/260000byte conservati e140directory per alberi vuoti; shared metadata lstat nega reparsepoint e reviewer verifica antenati prima di resolve. DataRoot configurato viene già passato dal caller. Review trova limiti nascosti da oltre8errori e WindowsHidden non escluso: corretti con copertura separata nel dettaglio e filtro attributo0x2; NoModule indica inventario accessibile senza falsa assenza fisica. Aggiornata intenzionalmente vecchia asserzione sul wording, conservando caso file davvero assente e0consigli. Test reali Windows hidden/junction, IO+limiti, modulo oltre limite e budget directory; aggiunto caso sul checkout reale.22nuovi/851attesi,5aggiunti dopoRed2 senza rivendicare altro Red. Runtime/test ancora da verificare suWindows; soloAST/diff locali. Nessun build/merge/testfunzionaleLinux o dato utente modificato. Prossimo: ricontrollo indipendente e Green.

## JRV-AUD-014 — review preventiva: esclusione junction e profili rafforzata

Review readonly richiede due casi mancanti: junction con target interno alla radice e nessuna enumerazione quando dati/codice coincidono. Aggiunte due prove reali: target profiles interno con spy su elenco/lettura e reviewer diretto; alias interno verso codice consentito non attraversato due volte. Il caso data_root==source_root ora rifiuta sia iterdir sia read_text.17nuovi/846attesi. Runtime ancora018, Red1source1d69632f7cb0fa355add17f681450ed95b0e85a6 inbozza47; Red ampliato da pubblicare. Nessuna esecuzione funzionale Linux/build/merge/dati reali. Prossimo: Red e controlli statici di review, poi inventario minimo.

## JRV-AUD-014 —15test pronti prima del runtime

Nuovo test_diagnostic_inventory.py,15nuovi/844totali attesi. Copertura di quattro cartelle runtime e sotto-moduli, raccomandazioni con righe senza esecuzione/literal, priorità runtime con170test e limite140, profili/cache/upstream/modelli esclusi prima di enumerare, data_root esplicito e coincidente, junction Windows reali e contenimento fisico, IO/stat/file sparito, budget byte e selettore modulo storico. Test solo su cartelle temporanee; junction non creabile è skip esplicito, non falsa prova. Runtime invariato018; review indipendente preventiva richiesta. Prossimo: RedWindows in bozza e correzione minima. Nessun build/merge/nuovo indice o test funzionale Linux, nessun accesso dati reali.

## 7 novembre 2026 — JRV-AUD-014 avviata: inventario autodiagnosi

Base01876e392f, ramo fix/jrv-aud-014-diagnostic-inventory-20261107. Il codice conferma che l'inventario legge solo radice e tests, saltando quattro cartelle runtime. Riusare AST e review esistenti, con ricorsione nelle sole local_model/file_access/program_apps/sveglia; runtime prima dei test, limiti140file/260000byte conservati e copertura dichiarata. Escludere dati/profili, cache/upstream/modelli, link/junction.90Python runtime dalla base, nessuna necessità dimostrata di aumentare limiti. Parser/review devono contenere errori di file spariti. Specifica/piano014 salvati prima del codice; runtime invariato, test RedWindows da preparare. Nessuna modifica a comandi/microfono/GPT o dati, nessun nuovo indice/dipendenza, build/merge o test funzionale Linux. Prossimo: test di copertura/esclusione e review.

## 7 novembre 2026 — JRV-AUD-018 verificata nei sorgenti in bozza

La correzione conserva le preferenze valide e i valori di prima installazione. Se il file esiste ma è illeggibile, l'avvio tiene spenti GPT e ascolto automatico, con un avviso nella console. Il salvataggio ricontrolla il file e rifiuta di sostituirlo prima di qualunque scrittura, anche dopo una copia del dizionario o una corruzione successiva al caricamento. Nessun reset o backup automatico; recupero manuale documentato.

Base 011:5994d17, source verificato 5fbb77d83b433c9c2f37694ac8bc96fb2f4b3dd0, [bozza46](https://github.com/MATRIXNEO23/jarvis/pull/46). Conservate 001–011 e018; gli altri ID restano distinti. [Run42354230043](https://github.com/MATRIXNEO23/jarvis/actions/runs/42354230043) SUCCESS al tentativo1:829 test per Python3.11.9 (job128348670591,140.607s) e3.12.10 (job128348670440,163.114s),0fallimenti/errori/skip. Tutti18nuovi metodi passati. [Rapporto](CORREZIONE-JRV-AUD-018-20261107.md), [evidenza](evidence/jrv-aud-018-fix-20261107.json), [recupero](RECUPERO-IMPOSTAZIONI.md).

Red1 c021a84/run42353608784:828test e34failure per job; Red2 59c6d3f/run42353743362:829test e37failure per job,0errori. Tutti i fallimenti appartengono ai nuovi controlli018, incluse le attese sul collector warning ancora assente; autorun MIC/GPT e perdita del file sono riprodotti indipendentemente. Review indipendente: tre lacune nei test coperte, nessun difetto residuo rilevato nel codice. Una vecchia asserzione che accettava un flag di tipoerrato come GPTTrue è intenzionalmente corretta e rafforzata con la verifica dell'originale intatto.

Sintassi e probe passati; Searchlive3.12 con servizio ripristinato e fixture rimossa.022/023 non riprodotti e ancora aperti. Checkpoint finale solo documenti/evidenze, runtime e test identici al source verde. Nessuna build, ZIP, merge, release o modifica ai dati/configurazioni/credenziali dell'utente. Nessun test funzionale Linux. Prove su profili temporanei e callback con servizi controllati: Windows10/i3/HDD, account, microfono e pacchetto estratto restano da collaudare. Nessuna garanzia CAS contro modifiche esterne dopo il controllo; file assente mantiene i valori iniziali, che possono abilitare MIC/GPT.

Prossimo014: includere le cartelle di codice runtime nell'inventario dell'autodiagnosi, escludendo profili/cache/upstream e mantenendo i limiti.012/013 richiedono anche futura verifica del pacchetto;016 resta una funzionalità incompleta da valutare, senza introdurre un indice duplicato. Continuare soltanto correzioni mirate autorizzate; build solo su richiesta esplicita.

## JRV-AUD-018 — Red acquisito, candidata revisionata

Red1sourcec021a84/run42353608784:828test/job34failure0errori;3.11job128346803002125.779s,3.12job128346802760133.185s. Red2source59c6d3f/run42353743362:829test/job37failure0errori;3.11job128347198453128.708s,3.12job128347198635139.055s. Tutti018 inclsubtest, collectorAPIassente fallisce esplicitamente; coreMIC/GPTautorun eperditafile al save riprodotti indipendentemente.022/023 nonriprodotti/aperti.

Candidata settings.py condivideloadparser eguardiasave prima diogni mutazione; fileassente separato, fileesistenteinvalido prudentOFF6flag, warningopzionale senza metadatisalvati ocontenutofile. jarvismaincollector/initiallaunchdrainonce, callbackTelegramgestisceerroresave. Vecchiotesttipoinvalido permissivo aggiornatoFalse+autoFalse+preservazionebytes, assertvalidi/legacy invariati. Review indipendente copre3gaptest e runtime senza difetti rilevati.18nuovi/829attesi; nessun testfunzionaleLinux, soloAST/diff. GuidaRECUPERO-IMPOSTAZIONI e rapporto018 pronti: recuperomanuale conbackupprivato, nessun reset/backupautomatico; assenza file usa defaultiniziali epuòabilitaremic/GPT, raceeditoresternaCAS nongarantita, HDDnonmisurato. Prossimo GreenWindows echeckpoint remoto, nessuna build/merge/config/account/datiutente.

## JRV-AUD-018 — review preventiva: compatibilità e guardia rafforzate

Review indipendente senza blocchi di contratto,3gaptest recepiti: profilo valido{} echiavimancanti confrontati coninteriDEFAULTS normalizzati; flagcriticiinvalidi conTTS/memoria/Telegram/keepawakeTrue perprovareOFFditutteautomazioni; nuovo test verifica rifiuto prima dimkdir/write_text/replace. Ora18nuovi/829attesi. Tutti callerssavegestisconoOSError/ValueError salvotelegram_reconfigure individuato nelpiano. Red1sourcec021a84bce5eb67d71c04d6d91f358569cda301f inbozza46, runtime ancora011. Redampliatodapubblicare, nessun testfunzionaleLinux/build/merge/configutente. Prossimo: RedWindows, poicorrezioneminima.

## JRV-AUD-018 —17test pronti prima del runtime

Nuovo test_settings_recovery.py:14test parser/persistenza conprofilitemporanei,3owner conprefixmain/Tkvalueassignment/schedulerGPT ecallbackinitial_launch/speak_result/telegram_reconfigure reali, servizi controllati.17nuovi/828attesi. ErroriJSON/UTF8/IO/nondict/flagtipoinvalido; assenti/validi/legacy; warningnonprivato; saveguardoriginal/copied/postloadcorruption/temp/history; ripristinomanualesimulato; bootstrapMIC/GPT/TTSoff ewarninguna volta. Runtime018 ancora invariato. Review indipendente preventiva richiesta; prossimopubblicareRedWindows inbozza su011. Nessun testfunzionaleLinux/build/merge/config/account/datoutente.

## 7 novembre2026 — JRV-AUD-018 prioritaria, preparazione Red

Base0115994d17, ramo fix/jrv-aud-018-settings-recovery-20261107. Anticipata protezione preferenze MIC/GPT rispetto alpackaging012/013. Fonteconferma fallback permissivo su JSON/UTF8/IO eflaginvalidi; save può sostituire originaleilleggibile. Contratto/piano018 registrati: assenza/validi/legacy invariati, fallbackprudente solo suerrori, warningconsole una volta, saveguardanche dictcopiati/corruzionedopoload, nessun reset o fileoriginalemodificato. Recuperomanuale conbackupprivato documentato. Niente nuovo archivio/dipendenza/popup; tipoerratoflag nonvalido da trattareprudente con aggiornamento intenzionale del vecchiotest permissivo. Nessun runtime018 ancora modificato, proveWindows da preparare. Nessun testfunzionaleLinux/build/merge/config/dati/credenzialiutente. Prossimo Red ereview.

## 7 novembre2026 — JRV-AUD-011 verificata nei sorgenti in bozza

Base010e65b5eb, sourceverde3ca986aaff89c176b684d44999b74e303814839c, [bozza45](https://github.com/MATRIXNEO23/jarvis/pull/45),001–010 conservate. [Run42352732284](https://github.com/MATRIXNEO23/jarvis/actions/runs/42352732284) SUCCESS tentativo1 delsourcecorretto:811test Python3.11.9/job128344138298151.630s e811 Python3.12.10/job128344138543133.249s;0failure/errori/skip, tutti19nuovi metodi passati. [Rapporto](CORREZIONE-JRV-AUD-011-20261107.md), [evidenza](evidence/jrv-aud-011-fix-20261107.json).

DomandeGPTscritte180s comealtri2canaliinferenza; login600/controlli40 conservati. Timeoutask chiede cancel_request solo al medesimoprocesso, IDcontrollonuovo senza pending/start/retry; wordinginvio/noninviato, non conferma remota. NodecontrollerperID primaawait, signalsDKgiàsupportato permodels/stream, guardierisultato, cleanupfinally, shutdownannulla tutteproprieinferenze. Risposte/acktardivi non raggiungono richiesta successiva; testownerreplacement/detach, pipefallita, epoch e2streamattivi isolati. Nessun nuovoSDK/dipendenza o login/scollegamento/consumoAPIaggiunto; tokenprecedenti non rimborsabili.

Red1source7a7589f/run42351877630:809test/job11failure+2errori,3.11job128341566504145.413s,3.12job128341566394113.026s. Review correggeID99contraddittorio, code/gate/owner/wording; Red2source53d674e/run42352051679:811test/job16failure0errori,3.11job128342078144157.782s,3.12job128342078389143.552s. Prima candidataruntimec6949e28/run42352333419 FALLITA:811test/job0failure1erroreshutdownwait3s,3.11job128342938450130.180s,3.12job128342938224174.701s. Annullamenti riusciti maNodeleggevaancorastdin. Causa verificata nel sorgenteNode22.12: Interfaceiterator→EventEmitter.on.return pulisceiterator ma noncloseInterface, contrariamente a indicazione generica docs. input.close esplicito prima break, pending/flush preservati; assert3s invariato. Review conferma causa/fix, nuovo sourceGreen nonreruncieco.022/023 non osservati/aperti.

Sintassi/probe passati, Searchlive3.12 conripristino servizio/fixture. Checkpoint finale solo documenti/evidenze, runtime/test uguali al sourceverde. Client/Node reali conSDKfinto temporaneo, nessun account/rete/DPAPI/inferenzareale/Windows10-i3-HDD collaudato. Abortbest-effort, nessuna finiremota/processo garantita conSDKnoncooperativo o refreshOAuthincorso; escalationstop precedente conservata. Nessuna build/ZIP/merge/release/config/dati/credenziali utente o testfunzionaleLinux. Prioritàsuccessiva da valutare018 protezioneconfigcorrotta prima dellarifinitura packaging012/013;016 indiceproprio incompleto resta funzione proposta, non duplicareWindowsSearch. Proseguire soltanto correzioni mirate nella sequenza autorizzata, build solo surichiestaesplicita.

## JRV-AUD-011 — prima candidata fallita, causa shutdown dimostrata

Sourcec6949e28/run42352333419 nonverde:3.11.9/job128342938450811test130.180s,1errore nel nuovo shutdown dopo ack e risposte di annullamento già accettate: proc.wait3s TimeoutExpired. Distinto daExplorer023; nessun rerun cieco. Node22.12 sorgente verificato: readline/interface.js1354 restituisce EventEmitter.on; events.js1112return→1196closeHandler rimuove listener dell'iteratore ma non invoca emitter.close. Le generiche istruzioni Node sul break automatico non bastano per questa implementazione. Il test è valido: GPTClient.stop tiene stdin aperto durante wait, mentre vecchio smoketest chiudeva stdin dalparent.

Fix minimo aggiuntivo: input.close() esplicito nelramo shutdown dopoack eabortcontroller, prima dibreak. Interface.close519→pause533→input.pause; pendingPromises eflushstdout proseguono senza process.exit o interruzioneOAuth forzata. Review readonly conferma fonti/causa eapproccio; stessaasserzione wait3s preservata, nessun timeout esteso. Nuova candidata da eseguire suWindows con suite completa, runtime prima non dichiarato verificato. Red2run42352051679:811test/job16failure0errori,3.11job128342078144157.782s,3.12job128342078389143.552s. Nessuna build/merge/dato utente/testfunzionaleLinux;022/023 separati.

## JRV-AUD-011 — Red1 riprodotto, candidata runtime revisionata

Red1source7a7589f/run42351877630:809test/job,11failure+2errori tutti011;3.11.9/job128341566504145.413s,3.12.10/job128341566394113.026s. Errori attesa rispostaabort mancante nelprotocollo; typed40s riprodotto indipendentemente dal testID99 poi corretto inreview. Red2source53d674e/run42352051679 ampliato19test/811attesi inverifica. Candidata3file: run_gpttyped180; clientcancelbest-effort al medesimoprocesso, IDunico/nopending/nostart, wordinginviato/non; bridgecontrollerperask primaawait, signal/checkdopoawait, cleanupfinally eabortshutdown. SDKpinriusato, nessun upgrade/dipendenza o retry/login/disconnessione. Reviewruntimeindipendente senza blocchi rilevati; precauzione nessuna exitgarantita conSDKnoncooperativo. Rapporto011/guidaGPT aggiornati. CheckAST/diff soltanto locali, nessun testfunzionaleLinux. Prossimo: GreenWindows echeckpoint remoto, nessun build/merge/configutente/account/rete;022/023 aperti.

## JRV-AUD-011 — review preventiva recepita prima del runtime

Review readonly rileva test99 incoerente conIDvalido ma inesistente: rimosso dagliinvalidi (unknown rimane cancelled:false). Due stream entrambi bloccati ora provano isolamento reale durante cancel; aggiunti2test cambio/detachowner tra send e timeout, wordingannullamento inviato/noninviato epropagazioneUI. FixtureSDK senza finestre200ms: rilascio esplicito attraverso status barriera già nelprotocollo.19nuovi/811attesi. Red1source7a7589f74316959738811e254cf277638fa8223c inbozza45; runtime ancora010, Red ampliato da pubblicare. Nessun testfunzionaleLinux/build/merge/configutente/account/rete. Prossimo: RedWindows e review, poicodice.

## JRV-AUD-011 —17test prima del runtime, Red da eseguire

Nuovo test_gpt_timeouts.py:5callback owner reali,4client/reader conpipecontrollata,8bridgeNode reale conSDKfinto temporaneo;17nuovi/809totali attesi. Timeout39/41/179/181s virtuali, busy/doppioni eepoch; timeoutclient richiede cancelsoloIDoriginario senza start/retry/pendingcontrollo, pacchettitardivi epipefallita; Nodecancel in session/models/stream, concorrenza,IDinvalidi/mapcleanup/SDKcheignoraabort/shutdown. Stato connected solo simulato, nessun login/rete/DPAPI/dato utente. Review indipendente preventiva richiesta; runtime invariato010. Prossimo: pubblicazione bozza e RedWindows, poi modifica3file esistenti. Nessun build/merge/testfunzionaleLinux;022/023 aperti.

## 7 novembre2026 — JRV-AUD-011 avviata dopo010 verde

Base010e65b5eb, ramo fix/jrv-aud-011-gpt-timeout-20261107. Prosegue sequenza autorizzata con cambi minimi. Causa verificata: run_gpt assegna40s a typed_conversation invece di180s; client ignora pacchetti tardivi ma non richiede annullamento. SDK fissato0a36fefe supporta già AbortSignal per listModels/streamResponse (types/index/responses verificati in fonte ufficiale). Riutilizzo senza upgrade/dipendenza: cancel_request per ID al bridge già esistente, AbortController per singolo ask, cleanup e abortshutdown. Nessun retry/login/disconnessione automatica o token rimborsati promessi. Specifica/piano011 registrati prima del runtime; testRedWindows da preparare. Nessun test funzionaleLinux, build/ZIP/merge/config/dati/credenziali utente.010 conservata con792test/job;022/023 distinti. Prossimo: prove protocollo/callback e Red.

## 7 novembre2026 — JRV-AUD-010 verificata nei sorgenti in bozza

Base0096e6b081, source060999046d6b232b4d3c05243c53f53b2b39fbd6, [bozza44](https://github.com/MATRIXNEO23/jarvis/pull/44),001–009 conservate. [Run42350951034](https://github.com/MATRIXNEO23/jarvis/actions/runs/42350951034) SUCCESS al tentativo1:792test Python3.11.9/job128338760673159.067s e792 Python3.12.10/job128338760391137.774s;0failure/errori/skip, tutti24nuovi metodi passati. [Rapporto](CORREZIONE-JRV-AUD-010-20261107.md), [evidenza](evidence/jrv-aud-010-fix-20261107.json).

Bridge richiede abort alla deadline e congiunge Timer prima del riuso; stop precede attesaRLock, close terminale revoca attive/code/turni differiti senza lockinferenza. Check prima/dopo init/load e prima C, provider stabile durante detach, guardia pubblicazione. Prova esplicita conserva reload005; memoria accettata, impostazioni e routing conservati. Nessun nuovo processo/dipendenza, fallbackGPT o pulsante. Getter GUI protetto e close usa solo owneresistente, continuando su erroreabort. Abort resta cooperativo: niente deadline per load/coda o garanzia di fine C/processo; backend non responsivo mantiene serializzazione.

Red1source5b6ca6d/run42350310207:784test/job,16failure+3errori;3.11job128336832048150.209s,3.12job128336832319132.052s. Red2source2a1e5ee/run42350462062:789test/job,21failure+3errori;3.11job128337282836127.965s,3.12job128337283043152.894s.3errori:validazioneTrue/NaN/Inf, non fixture. Review preventiva corregge fixtureThreadglobale e amplia copertura; review runtime trova due race della candidata, entrambe corrette con3test dopoRed2 (non rivendicato altroRed). Ricontrollo indipendente senza blocchi residui. Sintassi/probe passati; Searchlive3.12 con servizio/fixture ripristinati.022/023 non osservati e ancora aperti.

Checkpoint finale solo docs/evidenze, runtime/test identici al sourceverde. Nessuna build/ZIP/release/merge, test funzionale Linux o modifica configurazioni/dati utente. Test di inferenza ABI controllata e callback UI con servizi simulati, non modello reale/chiusura processo/benchmark Windows10-i3-HDD. Riscontro utente «funzionava nei limiti» senza versione identificata conservato, nessuna garanzia assoluta di zero regressioni. Prossimo011: timeout GPT scritto, correzione minima con verifica prima di build; funzionalità nuove/ottimizzazioni facoltative restano distinte.

## JRV-AUD-010 — Red2 acquisito e rilievi runtime corretti

Red2 source2a1e5ee/run42350462062:789test/job,21failure+3errori tutti010. Python3.11.9/job128337282836127.965s,3.12.10/job128337283043152.894s.3errori di validazione timeoutTrue/NaN/Inf, non fixture.022/023 non osservati. Review runtime ha trovato due difetti della candidata: provider ricontrollato dopo detach e generazione avviata dopo stop/deadline durante Timer.start. Corretti riferimento stabile in prepare e guard prima dell'ingresso C dentro try/finally.3nuovi test deterministici dopoRed2 portano24nuovi/792attesi; nessun ulteriore Red rivendicato. Richiesto ricontrollo indipendente, Green ancora da eseguire. Rapporto010 e README modulo aggiornati conlimiti: abort cooperativo, nessuna deadline per load/C non responsivo/processo e latenzaexport nonmisurata. Storia accettata conservata; niente nuovi pulsanti, fallback, servizi/dipendenze o dati. Nessun test funzionale Linux/build/merge. Prossimo: GreenWindows echeckpoint remoto.

## JRV-AUD-010 — Red1 dimostrato, candidata runtime in review

Red1 source5b6ca6d485ef2f4ca9508a205a3eef6134a04f98/run42350310207: Python3.11.9/job128336832048,784test150.209s;3.12.10/job128336832319,784test132.052s. Entrambi16failure+3errori, tutti nel nuovo modulo010. I3errori sono RuntimeError ABI invece di ValueError per True/NaN/Inf accettati erroneamente, non errori fixture. Riprodotti mancato abort alla deadline, stop che attende C, turni non revocati e ownerclose/getter non protetti. Nessun022/023 osservato. Red2source2a1e5ee92881c0f3130bc0c6e6fd9663ad8600ce/run42350462062 ampliato a21test, in verifica.

Candidata nei5file runtime esistenti: Timer per generate con revoca/join, stop/loadEvent e classificazione timeout; riferimento provider stabile durante detach; revisione/chiusura terminale della sessione, stop prima del lock e reset privato della prova esplicita; getter/close GUI sincronizzano solo creazione, non inferenza. Storia già accettata conservata, nessun retry o GPT automatico, nessun cambio schema/config/dati. Fixturethreading confinata alla UI generata come richiesto dalla review. CheckAST e git diff --check soltanto locali; nessun test funzionale Linux. Review runtime indipendente in corso; prossimo GreenWindows dopo risoluzione rilievi. Nessuna build/ZIP/release/merge,022/023 separati.

## JRV-AUD-010 — review preventiva: fixture e confini di annullamento

Review indipendente in sola lettura rileva che la fixture005 sostituiva threading.Thread globale: un Timer reale ne risulterebbe non inizializzato. Correzione solo fixture: namespace threading della UI generata, senza modificare stdlib o assert esistenti. Runtime ancora009. Rafforzato callback tardivo mentre seconda generazione è attiva; aggiunti stop con chat/prova in coda, close durante initialize, eccezione ABI dopo timeout/stop e completamento watchdog prima del reload.21nuovi metodi,789totali attesi. Primo Red5b6ca6d in esecuzione/da leggere; secondo Red di copertura da pubblicare. Nessun test funzionale Linux/build/merge/dato utente. Prossimo: leggere Red Windows valido, poi runtime minimo.

## 7 novembre2026 — JRV-AUD-010 autorizzata, riproduzione in preparazione

Utente: Jarvis funzionava nei suoi limiti; «procedi con le correzioni senza rompere niente». Feedback senza versione identificata, non attribuito a uno ZIP. Correzioni minime, comportamento/dati conservati. Base0096e6b081, ramo fix/jrv-aud-010-native-cancel-20261107. Specifica/piano010 registrati: riuso abort_generate già presente upstream, Timer limitato alla generazione con callback congiunta, revoca richiesta/turni e close senza lock inferenza. Nessun hard timeout garantito della DLL/load; niente nuovi processi/dipendenze o fallback GPT. Prima prove Red Windows, poi runtime/review/Green. Nessun test funzionale Linux, build/ZIP/release/merge o modifica configurazioni/dati utente.022/023 separati. Prossimo: pubblicare test riproduttivi in bozza su009.

## 7 novembre2026 — JRV-AUD-009: collegamento memoria verificato in bozza

Source5cb797a0d8e7cb1ed508ee1ed2367839fd8b4426, [bozza43](https://github.com/MATRIXNEO23/jarvis/pull/43) dalla42/base8ca4829,001–008 conservate. [Run42347553638](https://github.com/MATRIXNEO23/jarvis/actions/runs/42347553638) SUCCESS al tentativo1:768test Python3.11.9/job128328470822171.328s e768 Python3.12.10/job128328470641138.359s,0failure/errori/skip. Tutti21nuovi metodi passati. [Rapporto](CORREZIONE-JRV-AUD-009-20261107.md), [evidenza](evidence/jrv-aud-009-fix-20261107.json).

Gemma recupera estratti dagli archivi SecondBrain/Workspace e salva solo scambi accettati attraverso remember_exchange. Owner/epoca/progetto e revisione impediscono scritture vecchie o duplicate; generale conopt-in, progetti conpolitica separata già esistente. Reader nelworker/noTk, budget max600caratteri entro contesto, domanda/ruoli protetti e templatearchivio neutralizzati. Prove su nuova sessione/processo, ricordi pertinenti, isolamento, OFF/cicliowner, errori e Clear concorrente. Clear Gemmagenerale revoca prima dell'I/O e preserva progetti; non promessa di revoca dei flussiGPT esterni.

Red1 6b10d15/run42346405650:765test/job,16failure009/0errori. Red2 c6ce3e0/run42346662291:767test/job,18failure009/0errori. Review indipendente e ricontrollo senza rilievi residui dopo fix Clear: DELETE può essere committato anche conerrore successivoVACUUM; revoca anticipata e21°test reale-delete+errore prima delGreen. Non rivendicato ulterioreRed. Caratterizzazione002 di non-persistenza aggiornata alla009autorizzata, preservando righepreesistenti e altriassert.

Sintassi/probe passati; Searchlive3.12 passata conservizio/fixture ripristinati. Nessuna build/ZIP/release/merge o modifica di dati/configutente, nessun test funzionaleLinux. Callback/sessione/SQLite e processoPython reali, inferenza catturata: non GGUF/microfono/account/benchmarkWindows10-i3-HDD. Lessicale/estratti limitati, non ricordo universale; persistenza UI sincrona conserva timeoutSQLite5/6s, contesaHDDnonmisurata. CompactContext/IdleMemoryGate e sintesi ininattività nonattivati.022/023 aperti e nonriprodotti;010distinto. Checkpoint finale solo documentazione/evidenze, runtime/test identici al sourceverde. Fermarsi; prossimo010 solo al via.

## JRV-AUD-009 — Red confermato, candidata in verifica, 2026-11-07

Red1 6b10d15/run42346405650:765test/job,16failure009/0errori;3.11job128324998261182.984s,3.12job128324998507171.711s. Red2 c6ce3e0/run42346662291:767test/job,18failure009/0errori;3.11job128325781974152.013s,3.12job128325781765151.260s. Mancano persistenza/richiamo e revocaClear; nessun errore fixture né022/023 riprodotto.

Candidata nei4file esistenti jarvis.py, chat_transport.py, native_conversation_session.py e workspace_memory.py: owner/contesto/revisione catturati suUI; reader limitato nelworker senzaTk; budget max600caratteri di archivio entro spazio disponibile, domanda/ruoli conservati e template neutralizzati. Persistenza attraverso remember_exchange solo dopo accettazione unica e owner ancora autorizzato; warning su lettura/scrittura fallita, nientefallbackonline. Workspace prefer_related solo opt-in del nuovo caller, default invariato; Clear revoca prima dell'I/O e pulisce soloRAMgenerale senza attenderelockinferenza. Nessun nuovo archivio/dipendenza/schema/processo.

Review preventiva e finale in sola lettura;3gap test coperti. Rilievo importante della candidata Clear-after-DELETE/VACUUM: prima revocava solo dopo ritorno clear_all, ora revoca subito dopo conferma; aggiunto test eliminazione reale seguita daerrore, ricontrollo senza rilievi residui. Rafforzato OwnerValue conregistroviolazioni; testpriorità correlati usa budget stretto.21nuovi test/768attesi; nuovo erroreClear aggiunto dopoRed2, non dichiarato Red eseguito. Fixture002 allineata: recordesistenti preservati + append ora autorizzato009, altriassertsinvariati. Prossimo: GreenWindows e checkpoint. Nessun build/merge/dato utente/testLinux;022/023 e010 aperti. Compattazione/riassunti in inattività non attivati.

## JRV-AUD-009 — review preventiva e copertura ampliata, 2026-11-07

Review indipendente del contratto senza blocchi progettuali; tre lacune test recepite: OFF con assert esplicito zero letture, reader su thread reale e Value che rifiuta accessi fuori owner, Clear con inferenza bloccata da Event e conservazione RAM/disco progetto. Ora20nuovi test/767totali attesi. Runtime invariato; Red1 source6b10d15/run42346405650 da acquisire, Red ampliato da eseguire. Nessuna promessa di prestazioni dalla persistenza sincrona esistente, nessun nuovo DB/dipendenza/build/merge/testLinux. Prossimo: leggere Red ampliato, poi collegamento minimo.

## JRV-AUD-009 — collegamento memoria autorizzato in verifica, 2026-11-07

Base8ca4829/bozza42 con001–008, ramo fix/jrv-aud-009-gemma-memory-20261107. L'utente approva collegare Gemma al recupero dei ricordi già presente, con opt-in generale e progetti separati. Specifica/piano009 salvati; nessun nuovo archivio/embedding/servizio o riassunto automatico. Codice attuale: pollGemma accetta soloRAM, prompt non usa archivi. Nuovi test usano callback/trasporto/sessione e SQLite reali con inferenza catturata, inclusi nuovo processo, revoche/owner e Clear, errori/budget/template. Runtime ancora invariato; Red da eseguire suWindows. Nessun test funzionale Linux, build/merge/dato utente;022/023 e010 separati. Prossimo: Red e review preventiva, poi collegamento minimo.

## 7 novembre2026 — JRV-AUD-008 verificato nei sorgenti in bozza

Sourceb10453d5ddfda2155f4969dd8f1fa501cdcda8f9, [bozza42](https://github.com/MATRIXNEO23/jarvis/pull/42) dalla41/baseb25f54a,001–007 conservate. [Run42344534309](https://github.com/MATRIXNEO23/jarvis/actions/runs/42344534309) SUCCESS al tentativo1:747test Python3.11.9/job128319288492119.191s e747 Python3.12.10/job128319288706114.697s,0failure/errori/skip. Tutti17nuovi metodi passati. [Rapporto](CORREZIONE-JRV-AUD-008-20261107.md), [evidenza](evidence/jrv-aud-008-fix-20261107.json).

Salva continua senza inferenza/load. Prossima richiesta usa snapshot validato unico per budget e motore; samplers senza reload, modello/thread/batch/context/DLL con sostituzione serializzata. Cache esclude solo carattere, già nel prompt. Bridge conservaDLLbundled anche rawDLLvuoto; stop detacha e revoca readiness/cache prima di abort. Storia RAM/isolamento e permessi conservati. UI e guide allineate; nessuna dipendenza/schema/migrazione nuova.

Red1:6eaf7be/run42343723225,740test/job,16failure008/0errori. Red2:6c62ae9/run42343974322,745test/job,22failure008/0errori. Review indipendente copre gap DLL/loadfail/isolato-picker e trova regressione candidata trial005 con provider trattenuto: corretta e ricontrollata, test dedicato verde. Due nuove coperture stato/recupero dopoRed2 portano747; non rivendicate come Red separati. Nessun altro rilievo statico residuo.

Sintassi/probe passati; Search live3.12 passata con servizio/fixture ripristinati. Nessuna build/ZIP/release/merge o modifica dati/config utente.008 usa Tk/Save/JSON e pipeline reale con ABI controllata; nessun GGUF/account/microfono reale o benchmarkWindows10/i3/HDD. Nessun test funzionale Linux. La suite include il distinto probe006 DLL/export; non inferenza.022/023 non riprodotti e aperti;010/aborttimeout distinto,009memoria duratura non aggiunta. Ultimo checkpoint solo documentazione/evidenze, codice/test identici al sourceverde. Prossimo al via: verifica009 con opt-in e isolamento progetti, niente build automatica.

## JRV-AUD-008 — confermato, candidata in verifica Windows, 2026-11-07

Red1 source6eaf7be/run42343723225:740test/job,16fallimenti/0errori;3.11job128316811765113.998s,3.12job128316811896113.969s. Red2 source6c62ae9/run42343974322:745test/job,22fallimenti/0errori;3.11job128317587284124.310s,3.12job128317587390135.665s. Solo nuovi casi008 falliscono: impostazioni stale, reload assente e snapshot discordante. Nessun errore fixture,022/023 non riprodotti ma aperti.

Candidata: helper sessione passa snapshot a prepare quando cambiano valori di inferenza; chiave esclude il solo carattere, già letto nel prompt. Adapter riusa bridge per samplers e valida candidato prima di sostituire provider per campi reload+DLL. Bridge aggiorna solo5valori sotto lock, preservando DLL bundled; stop revoca stato/cache e detacha prima di abort anche dopo errori. UI/guida e2firme fixture allineate, nessuna asserzione precedente allentata.

Review indipendente:3gap iniziali coperti; trovato e corretto prima del Green un difetto della candidata: Prova005 non ricaricava il provider trattenuto dopo impostazione non caricabile. Ora usa sempre stop sicuro; nuovo test sequenzaA/Bmissing/A/trial e successivo riuso. Aggiunti anche stop pubblico fallito e provider trattenuto. Totale candidato747(17nuovi), ancora da eseguire. Ricontrollo mirato senza rilievi residui; abortcount test reso>=1 per consentire pulizia legittima, serializzazione ancora richiesta. Nessuna build/merge/dati utente/test funzionali Linux. Prossimo: Green Windows747 e checkpoint prove;009 fuori da questo passo.

## JRV-AUD-008 — copertura ampliata prima del runtime, 2026-11-07

Prima review indipendente del contratto/test senza falsi positivi certi. Coperti gap: DLL interna salvata, errore load dopo sostituzione/recupero e reload avviato da isolato/picker. Aggiunti anche stop fallito con recupero e factory realmente trasformata su copia temporanea: DLL bundled conservata quando rawconfig.dll è vuoto. Non è build/ZIP e non esegue DLL reali. Ora15nuovi test/745totali attesi. Red iniziale6eaf7be/run42343723225 ancora da acquisire completo; seconda prova ampliata da eseguire. Runtime invariato. Prossimo: leggere Red e applicare correzione minima;022/023 aperti.

## JRV-AUD-008 — verifica/correzione autorizzata, 2026-11-07

Baseb25f54a/bozza41 con001–007, ramo fix/jrv-aud-008-gemma-settings-20261107. L'utente approva controllo e correzione delle impostazioni salvate non applicate. Codice: sessione rilegge config/budget ma normale prepare soltanto iniziale;005 aggiorna solo Prova esplicita. Nuovi10test Windows in tests/test_native_settings_propagation.py: callback Salva/Tk e JSON reali, sessione/factory/provider/bridge reali, ABI controllata. Salva senza inferenza/load, samplers senza reload, modello/thread/contesto con reload serializzato, flussi isolati/picker/storia, errori/recupero e snapshot. Specifica/piano008 salvati; runtime ancora invariato, Red740atteso da eseguire. Nessuna build/merge/dato utente/test funzionale Linux;022/023 aperti. Prossimo: prova Windows, poi modifica minima solo se confermata.

## 7 novembre 2026 — JRV-AUD-007: correzione verificata nei sorgenti in bozza

Source425bfc38c1232ca26c5d1939bda7f0f95b07c04e, [bozza41](https://github.com/MATRIXNEO23/jarvis/pull/41) dalla40/basec9d1d29,001–006 conservate. [Run42342496402](https://github.com/MATRIXNEO23/jarvis/actions/runs/42342496402) SUCCESS al tentativo1:730 test Python3.11.9/job128313038365159.103s e730 Python3.12.10/job128313038104113.337s,0 failure/errori/skip. Tutti14metodi007 passano. [Rapporto](CORREZIONE-JRV-AUD-007-20261107.md), [evidenza](evidence/jrv-aud-007-fix-20261107.json).

Eventi vocali ora portano la generazione originaria; `poll` la verifica prima di effetti UI/log/memoria/dettatura/comandi/modello. Payload malformati o scaduti scartati senza svuotare coda o perdere risultati non vocali. Confermati vecchio+nuovo, TTS intermedio, close, status/errori correnti e una sola esecuzione per frase nuova. Nessuna dipendenza/processo/migrazione. Review indipendente senza difetti runtime residui; gap dettaturaCONT e errore corrente risolti e ricontrollati.

Red ampliato887e3db/run42342113095:729 test/job,24 fallimenti007 in entrambi;3.11 anche1errore023/fixtureExplorerTimeout15s,3.12 zeroerrori. Test nuovi completati a730 dopo review; riproduttori originali conservati. Sintassi/probe passati, Windows Search live3.12 passata con servizio/fixture ripristinati.022 non riprodotto;023 ricomparso nel Red e non corretto. Entrambi aperti.

Nessuna build/ZIP/release/merge, modifica configurazioni/dati utente o test funzionale Linux. Nessun microfono/Vosk acustico/GPT reale né prova Windows10/i3/HDD; non coperti interleaving modali dopo controllo, cambio progetto e PTT nella stessa modalità. Ultimo checkpoint soltanto documentale; sorgenti/test identici alla run verde. Prossimo solo al via: verificare008/parametri Gemma dopo005, senza supporre che l'audit storico sia ancora attuale.

## JRV-AUD-007 — Red ampliato acquisito, candidata in verifica, 2026-11-07

Red887e3db1eddaf734c440348d628b6702399eb943, run42342113095:729 test/job,24 fallimenti comportamentali007 in entrambi. Python3.11.9/job128311857151153.433s ha anche1errore023, TimeoutExpired15s nella fixture Explorer (test_file_access.py793/787); Python3.12.10/job128311857388167.838s ha0errori. Nessun errore fixture007, nessun Green dichiarato. Vecchia ipotesi confermata e prove storiche conservate.

Candidata minima: `_report` trasporta generazione; nuovo `accepts_event` verifica intero esatto e sessione aperta/attiva sotto lock esistente; guard iniziale `poll` filtra solo voice_text/status malformati o scaduti prima degli effetti. Nessuno svuotamento coda o handler modificato. Review iniziale contratto senza blocchi; due gap minori recepiti: dettatura raggiungibile inCONT e controllo positivo errore corrente. Test attuali730totali, ancora da eseguire su questa candidata; il nuovo controllo errore corrente è caratterizzazione attesa, non un ulteriore Red rivendicato. Runtime review finale e GreenWindows pendenti;022/023 restano aperti, niente build/merge/dati utente/test Linux.

## JRV-AUD-007 — correzione autorizzata in preparazione, 2026-11-07

Dopo spiegazione semplice l'utente dà «ok»: applicare007, un solo passo. Basec9d1d29 (bozza40), ramo fix/jrv-aud-007-voice-generation-20261107. Specifica docs/superpowers/specs/2026-11-07-jrv-aud-007-design.md e piano docs/superpowers/plans/2026-11-07-jrv-aud-007-fix.md. Red già valido2632321/run42340988254,723 test/job,9 fallimenti e0 errori. Aggiunti6 test di confine (effetti vecchi, misti, malformed, close, stato nuovo); runtime ancora invariato, nuovo Red da acquisire prima del fix. Scelta minima: numero sessione nell'evento, check nel consumer prima degli effetti; nessuna coda parallela/svuotamento globale. Nessun build/merge/dato utente/test funzionale Linux.022/023 aperti. Prossimo: Windows Red ampliato, poi implementazione e Green.

## 7 novembre 2026 — JRV-AUD-007 confermato, sola verifica

[Bozza40](https://github.com/MATRIXNEO23/jarvis/pull/40), base7920c4d (001–006 conservate), source2632321c258d9a20d44a7e6cbba8538476505412. [Rapporto](VERIFICA-JRV-AUD-007-20261107.md), [evidenza](evidence/jrv-aud-007-20261107.json), [run42340988254](https://github.com/MATRIXNEO23/jarvis/actions/runs/42340988254): Windows3.11.9/job128308391527 e3.12.10/job128308391854,723 test ciascuno,9 fallimenti comportamentali e0 errori,153.353s/148.019s. Suite rossa attesa:007 CONFERMATO/ALTO, non corretto. Quattro nuovi metodi falliscono (9 sottocasi); tre controlli passano; nessun altro fallimento.

Causa: `_report` verifica generazione prima della coda ma manda solo(kind,value); `poll` usa modo corrente. OFF→ON permette a testo vecchio di arrivare a comando/modello e a status vecchio di sostituire stato nuovo; frase senza hotword GPT diventa locale passando a continuo. Controlli: standby blocca; produttore vecchio non accoda; comando/modello corrente passa una volta. Producer/Queue/callback/loop dispatch reali, audio/azioni/modello controllati; nessun programma o account usato per007.

Errore iniziale della fixture (mock refresh_buttons assente) registrato e superato; aggiunti controlli positivi modello/hotword dopo review indipendente, senza ulteriori rilievi. Nessuna modifica runtime, configurazione/dato utente, merge, build/ZIP/release o test funzionale Linux. Sintassi Python/JS passata; PowerShell/probe file saltati dopo Red; Search live3.12 passata con servizio/fixture ripristinati. Windows10/i3/HDD, microfono/Vosk e modello reale non verificati.022/023 aperti, non riprodotti in questo run.

Prossimo passo soltanto dopo via utente: identità di sessione nell'evento e controllo al consumo prima di qualunque effetto; preservare altri eventi/mode/consensi, rendere verdi i test e rieseguire Windows. Non svuotare tutta la coda condivisa. Checkpoint finale soltanto documentale.

## JRV-AUD-007 — verifica in corso, 2026-11-07

Richiesta «ok verifica»: soltanto test/documentazione. Base `7920c4d9c32049d49f848aef3af0006a037dfedf`, ramo `verify/jrv-aud-007-voice-queue-20261107`, dipendente dalla bozza39. Ipotesi: evento vocale già in coda reinterpretato dopo cambio modalità/standby. Piano: `docs/superpowers/plans/2026-11-07-jrv-aud-007-verification.md`; test `tests/test_voice_queue_generation.py`. Nessuna correzione runtime applicata. Prova Windows ancora da eseguire; nessun test funzionale Linux, microfono, GPT reale, build o merge. Prossimo passo: Windows CI e confronto tra eventi vecchi e controlli nuovi. 022/023 restano aperti.

## 7 novembre 2026 — JRV-AUD-006: recupero dipendenza verificato, nessuna build

Sourcec0007689154efa574917ddb2ce23279ddf36c5f8, [PR draft39](https://github.com/MATRIXNEO23/jarvis/pull/39) dipendente dalla38. [Run42339214356](https://github.com/MATRIXNEO23/jarvis/actions/runs/42339214356) SUCCESS: Python3.11.9/job128302928559,716 test/122.394s; Python3.12.10/job128302928433,716 test/131.725s. [Evidenza](evidence/jrv-aud-006-20261107.json), [mappa/provenienza](NATIVE-ENGINE-REFERENCE.md). Red709 test/un fallimento per job per capacità autonoma assente, senza fingere una build attualmente fallita: vecchio artifact ancora valido fino al18 novembre.

Quattro consumer ora recuperano lo stesso componente da archivio Git fissatof147b1a; SHA archivio/DLL e source ABI controllati, estrazione selettiva, staging senza sovrascrittura divergente, riuso identico e archivio locale facoltativo. Source checkout pin, controlli hash esistenti e guardie build/publisher preservati. Runtime Jarvis, vecchi artifact/ZIP, configurazioni e dati non modificati; nessun binario nuovo in Git.

Otto nuove prove Windows passate: recupero pubblico reale senza artifact, sorgente upstream fissato reale, probe DLL caricamento/export con7 simboli e token iniziali0, corruzione/dimensioni/hash, membro mancante/duplicato, download errato, conservazione/idempotenza e LF/CRLF. Review indipendente senza blocchi dopo ricontrollo dei gap; archivio e DLL anche verificati dal revisore, otto blob uguali ai remoti. Sintassi/probe e Windows Search live passati, servizio/fixture ripristinati; package/publisher skipped.

Limiti: non eseguiti action checkout/full workflow di inferenza/build completa, GGUF o target Windows10/i3/HDD. Non è compilazione C++ bit-per-bit; è recupero dei medesimi byte senza scadenza Actions, con dipendenza dal repository GitHub o copia locale verificata. Nessuna nuova build, ZIP applicativo, release, merge o test funzionale Linux.022/023 restano aperti. Checkpoint successivo solo documentale; prossimo JRV-AUD-007: verificare e riprodurre trascrizioni vocali vecchie in coda dopo spegnimento/riattivazione o cambio modalità.

## 7 novembre 2026 — JRV-AUD-006, candidata di preparazione build in verifica

Red2da23de / run42338424815/job128300496475:709 test/un fallimento senza errori per capacità autonoma assente, non una build dichiarata fallita oggi. Implementati tools/native_model/restore_engine.py e manifest: archivio Git f147b1a, streaming limitato/hash archivio e DLL, membro unico, staging senza sovrascrivere file diversi, archivio locale identico facoltativo. Quattro consumer ora usano il helper dopo setup Python; pin upstream e hash esistenti conservati, guardie build/publisher invariate. Trigger suite estesi a manifest e workflow. Runtime Jarvis invariato.

Review indipendente iniziale senza blocchi: archivio e DLL verificati anche dal revisore. Gap minore coperto estendendo il recupero reale al sorgente upstream fissato, oltre alle fixture; source normalizzato identico al blob Git7805cd49. Otto prove preparate: download reale senza artifact, probe DLL/export senza GGUF, ZIP sintetici corrotti/duplicati/dimensione/hash, file preesistenti/idempotenza, source ABI e download troncato. Nuova mappa docs/NATIVE-ENGINE-REFERENCE.md. AST/JSON/diff controllati; Green Windows ancora pendente. Nessuna compilazione/build/ZIP applicativo, release, esecuzione modello o test funzionale Linux;022/023 aperti.

## 7 novembre 2026 — JRV-AUD-006, recupero dipendenza in preparazione

Base649d1a0 con001–005 conservate; ramo fix/jrv-aud-006-native-reference-20261107. Artifact13339099748/run41860087656 non ancora scaduto, scadenza verificata18 novembre2026 ore15:49:03UTC. Quattro workflow lo consumano. Identica DLL già presente nello ZIP61a95f8 in Git al commitf147b1a, hashac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba; nessun binario nuovo necessario.

Piano tools/native_model/restore_engine.py con manifest immutabile, recupero pubblico/hash/extraction selettiva, consumer aggiornati. Test Red della capacità di recuperare da checkout vuota senza artifact (baseline manca il helper): non si finge che la build attuale sia già fallita, non si cancella artifact. Dopo recupero il test userà il probe DLL esistente, senza modello/GGUF/build. Runtime/workflow ancora invariati, nessun test funzionale Linux, nuova build/ZIP, release o dato personale.

## 7 novembre 2026 — JRV-AUD-005 verificata in CI con ABI controllata, non distribuita

Checkpoint357c65122bb0faa0b07871c8b59cb65692831b93, runtimee20e4b88451541d650d0a9160f536290a6daaa25, [PR draft38](https://github.com/MATRIXNEO23/jarvis/pull/38) dipendente dalla37. [Run42337129314](https://github.com/MATRIXNEO23/jarvis/actions/runs/42337129314) SUCCESS: Python3.11.9/job128296467283,708 test/114.337s; Python3.12.10/job128296467507,708 test/106.014s. [Evidenza](evidence/jrv-aud-005-20261107.json).

Red700 test/tre fallimenti per job ha dimostrato chat+trial e due pannelli con picco2 generazioni, reload e abort concorrenti al confine ABI controllato. Il builder aggiungeva un proprietario separato alla UI del pacchetto. Ora il getter condiviso passa al pannello senza attivazione automatica; prova, chat e Telegram usano lo stesso proprietario/lock. Reload esplicito e generazione isolata nella sessione, storico invariato, nessuno stop finale del proprietario condiviso. Adapter.prepare riceve snapshot validato; richieste obsolete in coda rifiutate, ulteriori salvataggi non cambiano il modello già acquisito.

Dieci nuove prove, callback apertura reale, trasformazione UI effettiva su copia temporanea senza ZIP. Review indipendente senza blocchi; lacuna getter/lock corretta con osservatore del tentativo reale e ricontrollata, confronti DOS/canonici corretti con samefile senza rimuovere verifiche modello/parametri. CI intermedie706/708 fallite solo per quelle fixture, conservate nei riferimenti. Sette blob runtime/test recensiti uguali ai remoti. Sintassi/probe nativi e Windows Search live passati, servizio/fixture ripristinati; package/publisher skipped.

Non è una prova di crash risolto con C/DLL/GGUF reali: nessun modello reale, target Windows10/i3-2100/HDD, account Telegram o microfono collaudato; nessuna build, ZIP, merge, chiamata GPT o modifica dati/configurazioni personali.022/023 restano aperti. Il checkpoint seguente cambia solo documentazione. Prossimo JRV-AUD-006: dipendenza da artifact nativo in scadenza il18 novembre, da risolvere prima di quella data senza build automatica.

## 7 novembre 2026 — JRV-AUD-005, correzione della fixture percorsi Windows

Run42336668228 sul runtimee20e4b8:706 test per Python3.11/3.12, un fallimento della nuova prova per confronto testuale fra percorso DOS RUNNER~1 e nome completo runneradmin del medesimo GGUF. Difetto della fixture, non del runtime. Corretti solo confronti con numero di load e os.path.samefile, mantenendo verifiche modello/parametri. La lezione sui nomi Windows era già presente e va applicata anche alle prove nuove.

Review finale runtime senza blocchi; gap queued-settings ora coperto da osservatore sul tentativo reale del RLock (non solo getter), ricontrollato indipendentemente. Anche prova snapshot→prepare aggiunta. Nessuna ulteriore modifica runtime; prossimo controllo:708 test Windows sul checkpoint di test corretto. Nessuna build/ZIP/merge, prova DLL/GGUF reale o test funzionale Linux.022/023 restano aperti.

## 7 novembre 2026 — JRV-AUD-005, review e due nuove prove mirate

Candidata runtimee20e4b8 recensita indipendentemente: nessun difetto bloccante. Rilievo minore: manca prova del cambio configurazione durante attesa del lock. Aggiunti test deterministici del callback trial mentre chat è bloccata, poi salvataggio; e dello snapshot letto prima di un ulteriore salvataggio, verificando modello/parametri effettivi e file nuovo preservato. Runtime invariato; le nuove prove richiedono CI Windows aggiornata. Nessun test funzionale Linux, DLL/GGUF reale, build, ZIP o merge.

## 7 novembre 2026 — JRV-AUD-005 confermata al confine ABI, candidata in verifica

Red728ef2d / run42336282687/job128293840609:700 test/tre fallimenti senza errori. Trial generato dal builder insieme alla chat o a un altro pannello: ABI controllata registra picco2 generazioni, ricaricamento e abort sovrapposti; callback apertura senza owner. Dimostrato il difetto di ownership, non un crash C/DLL reale.

Candidata: get_gemma_session trasmesso al pannello senza invocarlo; test_model generato chiama test_generation sul proprietario app esistente, senza stop finale. La sessione attende il lock, valida snapshot/configurazione, esegue reload esplicito e prova isolata, lascia backend pronto a chat/Telegram senza cambiare lo storico. NativeChatAdapter.prepare accetta lo snapshot per impedire cambi di modello fra validazione e caricamento. Nuove prove per stile/storia, modello/parametri appena salvati, configurazione obsoleta, errore, Telegram concorrente e pannello senza owner. AST/diff controllati; Green Windows e review indipendente pendenti. Nessun test funzionale Linux, DLL/GGUF/Pavilion reale, build/ZIP, merge o dati personali.022/023 restano aperti.

## 7 novembre 2026 — JRV-AUD-005, riproduzione in corso

Basefa4eec2 con001–004 conservate; ramo fix/jrv-aud-005-native-owner-20261107, piano dedicato. La root UI non ha Prova generazione: il builder la aggiunge nel pacchetto creando una seconda sessione, mentre chat/Telegram già condividono get_gemma_session. Test Windows preparati: stessa trasformazione UI su copia temporanea (nessun ZIP), callback generato e factory/bridge/adapter/session reali con ABI controllata; chat+prova e due pannelli, reload/abort durante altra generazione. Ingresso impostazioni reale verificato senza attivazione automatica. Runtime invariato, Red da eseguire; nessun crash DLL/GGUF reale dichiarato, test funzionale Linux, build, merge o dato personale. Proposta: riusare il proprietario esistente e una prova isolata con reload serializzato.

## 7 novembre 2026 — JRV-AUD-004 verificata nei sorgenti, non distribuita

Runtime8557ddb9b23c34c11aaee7a1b65bf57470dfd7f5, [PR draft37](https://github.com/MATRIXNEO23/jarvis/pull/37), dipendente dalla36. [Run42332441469](https://github.com/MATRIXNEO23/jarvis/actions/runs/42332441469) SUCCESS dopo un retry del solo job3.12: Python3.11.9/job128281773601,698 test/90.906s; Python3.12.10/job128282998223,698 test/113.115s. [Evidenza completa](evidence/jrv-aud-004-20261107.json).

Confermati quattro incastri lifecycle/richiesta file in Red692 test per job. Review ha trovato un rischio della candidata1, poi riprodotto con Red2 Python3.11/698 test/tre fallimenti: vecchi pending/selezioni potevano rivivere. Candidata2 serializza lifecycle e invalidazione con RLock separato, conserva i permessi transazionali, rilascia manager-lock prima di file.reset e completa reset prima della riattivazione. Refresh iniziale completo invalida anche revoche esterne prima della riapprovazione. Runtime modificato solo addon_manager.py; FileAccessService, schemi, autorizzazioni e dati conservati. Sette nuove prove reali verificano incastro, reenable con/senza nuova richiesta, vera selezione, ledger mancante, permessi durante transazione, limiti/copie e refresh attivo. Review finale senza blocchi residui; blob locali/remote uguali.

Limiti CI conservati:022 crash Tcl_AsyncDelete nel Red2/job3.12, senza conteggio completo;023 timeout15s nel vecchio harness PowerShell al primo Green/job3.12 (698 test/un errore), passato al retry sullo stesso codice. Le cause di022/023 restano da investigare: il successivo verde non costituisce correzione di quei problemi. [022](evidence/jrv-aud-022-20261107.json), [023](evidence/jrv-aud-023-20261107.json). Sintassi/probe nativi e Windows Search live passati, servizio ripristinato/fixture rimossa, package/publisher skipped. Nessun test funzionale Linux, PC Windows10/i3/HDD, nuova build, ZIP, merge o dato/configurazione personale modificato. Checkpoint successivo solo documentale. Prossimo JRV-AUD-005: verificare proprietà e concorrenza del backend nativo prima di correggere;022/023 aperti per affidabilità del collaudo prima della distribuzione.

## 7 novembre 2026 — JRV-AUD-004, seconda candidata; nuovo limite CI tracciato022

Red2 dc1e4f2 / run42332104260: nel job128280722034 Python3.12 i nuovi casi no-fresh pending/selezione e ledger sono falliti; il vecchio incastro invece non si riproduceva più. Questo conferma la regressione della candidata1 rilevata dalla review. La suite del job si interrompe poi per Tcl_AsyncDelete/Variable.__del__: nessun conteggio finale disponibile, non è un collaudo completo. JRV-AUD-022: crash confermato della suite Tkinter, causa da verificare (finalizzazione di oggetti Tk da thread diverso nel test003 Win32); priorità media per affidabilità CI, non ancora corretto.

Candidata2: RLock separato serializza lifecycle, reset e riattivazione; callback permessi mantengono solo manager-lock. Refresh iniziale completo prima della transazione invalida revoche esterne; metadati sotto manager-lock, reset file fuori manager-lock prima del rilascio lifecycle-lock. ProgramService.reset nella posizione originale, FileAccessService ripristinato identico alla base. Test reenable richiede attesa del reset e conserva la nuova richiesta; altri test no-fresh e ledger invariati. Design riesaminato indipendentemente senza ciclo bloccante individuato. AST/diff controllati; Green e review sul codice finale ancora pendenti, nessuna build/merge/dato personale.

## 7 novembre 2026 — JRV-AUD-004, rilievo bloccante della review e nuova riproduzione

La prima candidata elimina il ciclo ma il reset condizionale può saltare una revoca se la riattivazione arriva prima del reset: vecchi pending/risultati/selezione tornano validi. Caso anche sequenziale: ledger rimosso e subito set_enabled(True), che osserva inattivo nel refresh iniziale e attivo alla fine senza invalidare. Rilievo statico importante del revisore; non dichiarato ancora riprodotto su Windows. Aggiunte prove con risultati/selezione reali, reenable senza nuova richiesta e ledger mancante. La candidata corrente è pubblicata solo per ottenere Red2, non è pronta. Prossima correzione proposta: serializzare i lifecycle separatamente dai permessi, completare reset fuori dal lock manager prima della riattivazione e fare refresh iniziale completo prima della transazione. Nessuna nuova build o merge.

## 7 novembre 2026 — JRV-AUD-004 confermata, candidata in verifica

Red baa9317 / run42331515560, job128278876066 Python3.11.9:692 test/quattro fallimenti senza errori. Nei quattro lifecycle reader e changer restano bloccati dopo join, con entrambi i confini raggiunti e lock reali. Causa: manager→file.reset e pending→manager.files_enabled. Candidata: guardia comune per refresh/install/set_enabled/remove; refresh record separato da reset file, eseguito dopo rilascio del lock esterno anche su return/eccezione. Reset condizionale ricontrolla attivazione sotto lock file per non cancellare richieste successive alla riattivazione.

Scartata prima di implementarla la proposta iniziale di callback senza lock: potrebbe leggere il vecchio enabled=True durante una revoca ancora in I/O. I callback mantengono il lock transazionale; ProgramService.reset non bloccante conservato nella posizione originale. Nuove prove: revoca durante transazione, reset ritardato dopo reenable, limiti per operazione/copie dei descrittori, refresh attivo che conserva il chiarimento e policy. AST/diff verificati; Green Windows e review indipendente pendenti. Nessun test funzionale Linux, build, merge o dato/configurazione personale.

## 7 novembre 2026 — JRV-AUD-004, riproduzione in corso

Base386fcd1, ramo separato fix/jrv-aud-004-addon-locks-20261107,001/002/003 conservate. Piano docs/superpowers/plans/2026-11-07-jrv-aud-004-addon-locks.md. Test Windows con manager/servizio/lock e file temporanei reali, eventi ai confini enabled/reset e processo isolato: chiarimento pendente insieme a disable/remove/upgrade/revoca ledger. Runtime invariato; inversione dei lock ancora ipotesi statica fino al Red. Proposta minima: leggere lo snapshot già pubblicato nei callback file senza lock inverso, mantenendo reset/revoca sincroni. Nessun test funzionale Linux, build, merge o dato personale.

## 7 novembre 2026 — JRV-AUD-003 verificata su Windows, non distribuita

Correzione4dabf48fd71e433d43a6b97ae1a057730b1ee3b8, [PR draft36](https://github.com/MATRIXNEO23/jarvis/pull/36), dipendente dalla35. [Run42330792141](https://github.com/MATRIXNEO23/jarvis/actions/runs/42330792141) SUCCESS:691 test per Python3.11.9/3.12.10; nove test nuovi con Edit Windows nativo e file temporanei. Red precedente684 test/due asserzioni fallite senza errori per ciascun job. [Evidenza](evidence/jrv-aud-003-20261107.json).

Salva e chiudi ora distingue snapshot salvato e scarto esplicito. La chiusura verifica il testo sotto blocco temporaneo della digitazione; modifiche sopraggiunte lasciano aperti editor/sessione e copia salvata. Ripristino dirty/stile originale anche dopo lock parzialmente applicato, lettura/PostMessage/timeout e cambio titolo. close_clean confronta la copia su disco; save_only, scarto autorizzato e versioni immutabili conservati. Review indipendente senza difetti bloccanti, lacune iniziali titolo/documentazione risolte e ricontrollate; cinque blob runtime/test identici ai remoti.

Sintassi/probe nativi e Windows Search live passati, servizio ripristinato/fixture rimossa; package/publisher skipped. Nessun test funzionale Linux, Notepad installato/Windows10/Pavilion, nuova build, ZIP, merge o modifica dati/configurazioni utente. Il parent nascosto di test non replica il dialogo Save di Notepad. Readonly tutela la digitazione, non scritture programmatiche di automazioni estranee; un processo bloccato può impedire anche il tentativo di ripristino. Checkpoint successivo solo documentale. Prossimo JRV-AUD-004: riprodurre la possibile inversione dei lock add-on/file con barriere, ancora da confermare.

## 7 novembre 2026 — JRV-AUD-003 confermata, candidata in verifica

Red f92eef2 / run42330339439:684 test per Python3.11/3.12, due fallimenti comportamentali senza errori. La finestra Edit reale accetta digitazione dopo dirty-clear; modifica durante I/O chiusa e scartata. Candidata: salva e chiudi passa lo snapshot salvato anziché consenso allo scarto; bridge protegge Edit in sola lettura dal confronto finale alla chiusura, ripristina dirty/stile originale in errore. close_clean richiede copia salvata corrispondente. Scarto esplicito e save_only preservati. Test aggiunti per lock rifiutato/timeout dopo applicazione, lettura, PostMessage, chiusura non confermata, stile iniziale readonly, titolo rinominato, versioni immutabili e identità estranea. AST/diff controllati, Green Windows e review indipendente pendenti; nessun test funzionale Linux, Notepad/Pavilion personale, build o merge.

## 7 novembre 2026 — JRV-AUD-003, riproduzione in corso

Base784edad, ramo isolato fix/jrv-aud-003-save-close-20261107 con001/002 conservate. Piano docs/superpowers/plans/2026-11-07-jrv-aud-003-save-close.md. Test Windows: worker/orchestratore/bridge reali, file temporanei e controllo Edit nativo nascosto del solo test; modifica durante I/O e digitazione tra dirty-clear/WM_CLOSE. Runtime ancora invariato, rischio non ancora riprodotto. Prossimo passo Red Windows; poi confronto del testo con blocco temporaneo della digitazione e ripristino in errore. Nessun Notepad personale, test Linux, build o merge.

## 7 novembre 2026 — JRV-AUD-002 verificata su Windows, non distribuita

Correzione `05926bdc34516624eb3c5ef21321b801cb466586`, [PR draft35](https://github.com/MATRIXNEO23/jarvis/pull/35), dipendente dalla34. [Run42329422636](https://github.com/MATRIXNEO23/jarvis/actions/runs/42329422636) SUCCESS:682 test per Python3.11.9/3.12.10, sintassi/probe nativi e indice Windows live passati; servizio e fixture ripristinati. Red precedente675 test/cinque asserzioni fallite senza errori fixture. [Evidenza](evidence/jrv-aud-002-20261107.json).

Un solo backend, buffer globale di16 scambi partizionati per progetto/generale, nessuna persistenza aggiunta. Solo turni accettati nel poll con epoca/progetto validi entrano nella memoria e nel follow-up app. Verificati ritorno al progetto, revoca voce/testo, contesto catturato prima del worker, budget globale, commit idempotente, poll non bloccato dall'inferenza, isolamento Telegram/picker e conservazione dei ricordi su disco. Review indipendente senza difetti bloccanti; coperte anche le lacune iniziali follow-up/poll concorrente. I blob runtime/test condivisi coincidono col commit remoto. Nessun test account/microfono/GGUF/Pavilion, nuova build, ZIP o merge. Il checkpoint successivo cambia solo documentazione. Prossimo ID003: riprodurre la modifica manuale durante salva e chiudi prima di correggere; il rischio resta da confermare.

## 7 novembre 2026 — JRV-AUD-002, candidata in verifica

Red Windows run42328846716 / job128270410711 su a988b63:675 test, cinque fallimenti comportamentali, nessun errore fixture. Riprodotti contaminazione A→generale/B, turni vocali/scritti revocati ancora ricordati e contesto errato del worker. Piano invariato: un backend,32 messaggi globali, nessun archivio persistente modificato.

Candidata: buffer di16 scambi etichettati per contesto; prepare_turn produce una proposta, il poll UI la accetta solo se epoca/progetto sono correnti. Commit idempotente con lock breve distinto dall'inferenza; follow-up app aggiornato soltanto dopo accettazione. API ask sincrona e chat isolata Telegram/picker conservate. Nuove prove di budget, commit differito/idempotente, metadati non bloccati dall'inferenza e contesto invalido. AST/diff controllati; Green Windows e review indipendente ancora da completare. Nessun test funzionale Linux, GGUF/account reale, build o merge. PR35 dipende da PR34.

## 7 novembre 2026 — JRV-AUD-002, riproduzione in corso

Base53717eb con001 conservata; ramo separato fix/jrv-aud-002-gemma-history-20261107. Piano docs/superpowers/plans/2026-11-07-jrv-aud-002-history.md. Test nuovi dei callback reali con NativeConversationSession e WorkspaceMemory temporanei: progetti/generale, risultato revocato prima del poll, cambio contesto durante inferenza e prima dell'avvio worker, conservazione dati persistenti. Backend controllato senza DLL/GGUF/account. Runtime invariato. Prossimo passo: Red Windows, poi partizionare un buffer globale limitato e inserire nella memoria soltanto risposte accettate dalla UI. Nessun test funzionale Linux, build, ZIP o merge.

## 7 novembre 2026 — JRV-AUD-001 verificata su Windows, non distribuita

Correzione runtime `daa7a6a8760688f6081bca95ee6c9d6df6ac8ce8`, [PR draft34](https://github.com/MATRIXNEO23/jarvis/pull/34). [Run42327319575](https://github.com/MATRIXNEO23/jarvis/actions/runs/42327319575) SUCCESS: 670 test per Python3.11.9 e3.12.10, sintassi/probe nativi e Windows Search live passati; servizio e fixture ripristinati. I14 test aggiunti coprono policy, revoca, file, diagnosi e planner. Red precedente659 test/cinque asserzioni fallite conservato. Review indipendente in sola lettura: nessun difetto bloccante; lacune iniziali file/diagnosi coperte dai test aggiunti. [Evidenza](evidence/jrv-aud-001-20261107.json).

Mai prevale su consenso precedente e sessione Telegram; ask conserva la conferma; allowed evita la richiesta ripetuta; il grant viene ricontrollato prima della pipe. File assente/danneggiato nega; nessuna preferenza migrata o riscritta. Login e autorizzazioni alle azioni restano separati. Nessuna nuova build, ZIP, merge, modifica ai dati o prova di account/microfono/Pavilion. La005 e le candidate Gemma distribuite restano invariate. Il checkpoint seguente cambia solo documentazione, non i blob runtime/test verificati. Prossimo passo JRV-AUD-002: isolamento dello storico Gemma tra progetti/generale, senza scaricare il backend caricato; riproduzione Windows prima del fix.

## 7 novembre 2026 — JRV-AUD-001, correzione candidata in verifica

Red Windows run42326631728 / job128263321901 sul commit4b21693: 659 test, cinque asserzioni fallite nei tre nuovi test di integrazione, nessun errore fixture. Riprodotti il bypass di Mai (tre azioni console e sessione Telegram) e il dialogo superfluo per allowed. Ramo correttivo isolato; PR draft34. Nessun pacchetto o pubblicazione Download.

La candidata introduce grant di richiesta per funzione, riletto prima dell'invio: never nega, ask richiede conferma, allowed evita il dialogo. Integra console, raffinamento e spiegazione file, planner, diagnosi e Telegram; il consenso di sessione non supera Mai. UI estesa ai permessi effettivi di spiegazione file, planner e diagnosi. Configurazioni mancanti/danneggiate restano negate; nessun file utente scritto. Fixture storiche aggiornate con permessi ask espliciti solo in profili temporanei. Verifica statica AST/diff eseguita; Green Windows e review in corso, nessuna dichiarazione di fix verificato. Prossimo controllo: matrice completa Windows 3.11/3.12 e regressioni.

## 7 novembre 2026 — JRV-AUD-001, riproduzione in corso

Autorizzate le correzioni dell'audit con spiegazioni sintetiche. Base evoluta61a95f8, ramo isolato fix/jrv-aud-001-permissions-20261107. Prima unità: permessi GPT per funzione. Aggiunti piano docs/superpowers/plans/2026-11-07-jrv-aud-001-permissions.md e tests/test_online_permissions_integration.py: Mai nella console anche dopo conferma, allowed senza dialogo e revoca prima del worker, Mai Telegram prevale sul consenso di sessione. Solo callback reali con confini controllati e profilo temporaneo; nessun account/dispositivo. Runtime ancora invariato. Prossimo controllo: Red Windows; nessun test funzionale Linux, nuova build, ZIP, merge o modifica ai dati.

# JARVIS — handoff tecnico, mappa architetturale e checkpoint (2026-11-05)

## 6 novembre 2026 — Carattere di Gemma locale

La configurazione del modello include istruzioni facoltative di stile (240 caratteri). Il valore è locale e compatibile con i profili precedenti. Si applica alle nuove risposte della conversazione Gemma e a Prova generazione, senza richiedere un ricaricamento per il solo cambio di stile. Si preserva la domanda se il budget è stretto. Le risposte Telegram continuano a usare il contesto del contatto. La prima run 42268657858 ha rilevato un'asserzione UI eseguita dopo Ripristina anziché dopo Salva. Sul commit correttivo `3c71ca4` le due suite Windows e la verifica dello ZIP estratto sono passate nella [run 42269297921](https://github.com/MATRIXNEO23/jarvis/actions/runs/42269297921). Resta il collaudo con il GGUF sul Pavilion.

## 6 novembre 2026 — Consenso GPT per Telegram durante la sessione

La modalità predefinita resta la conferma per messaggio. L'opzione esplicita in Impostazioni → Telegram autorizza l'invio dei messaggi e del contesto recente dei soli contatti selezionati. Il consenso è solo in RAM e si azzera disattivando o disconnettendo GPT oppure chiudendo Jarvis. Il trasporto ricontrolla token, epoca e bridge prima dell'invio e scarta risposte obsolete. Console e planner mantengono i propri controlli. Le due suite Windows e la verifica dello ZIP estratto sono passate nella [run 42246973814](https://github.com/MATRIXNEO23/jarvis/actions/runs/42246973814). I test simulano conferma, rifiuto, sessione e revoca. Resta il collaudo con l'account reale sul Pavilion.

## 6 novembre 2026 — Indicatore Telegram dei messaggi da vedere

Base `0055607`. Il pallino del contatto riusa il conteggio dei messaggi in arrivo non ancora visti. L'animazione HUD esistente alterna due tonalità viola per i nuovi messaggi e mantiene una tonalità tenue e fissa dopo l'apertura della cronologia. Il clic registra solo gli ID in arrivo mostrati, così un messaggio concorrente resta da vedere. Nessuna modifica alle ricevute di Telegram. Le due suite Windows e la verifica dello ZIP estratto sono passate nella [run 42221709872](https://github.com/MATRIXNEO23/jarvis/actions/runs/42221709872) sul commit `addc19e`. Resta la prova visiva sul Pavilion. Nessuna pubblicazione in Download.

## Telegram con Gemma locale

Il bridge mantiene contatti autorizzati, contesto recente della singola chat, presentazione, sintesi e invio dei vocali. Se GPT è attivo e connesso, resta il consenso per richiesta. Se GPT non è disponibile, Gemma riusa il modello caricato senza accedere alla cronologia della console o dei progetti. Il collaudo con account Telegram e modello reali resta separato dalla CI Windows.

## 6 novembre 2026 — rimossa la barra sostitutiva

La candidata `Download/Jarvis-Gemma-Comandi-e-Interfaccia-6e73e3b.zip` è pubblicata su main `14967a4`. Il commit `6e73e3b` mantiene solo i tre pulsanti, integrati nell'intestazione HUD esistente o raggruppati in alto a destra nelle finestre secondarie. Eliminata la fascia aggiuntiva con il titolo. I dialoghi nativi Windows mantengono l'aspetto di sistema. [Suite Windows, archivio estratto e pubblicazione](https://github.com/MATRIXNEO23/jarvis/actions/runs/42147766728) riusciti.

## Segnalazione Pavilion — dialogo Gemma e apertura app

La foto mostra «Apri Netflix» come risposta della chat. Il percorso scritto di Gemma non condivideva la selezione app del percorso vocale. Ora «con Gemma» può essere scritto oppure pronunciato. Dopo uno scambio recente che identifica una sola app autorizzata, una richiesta esplicita come «me lo apri?» passa al motore come proposta da confermare. Il testo del dialogo continua ad andare in chat. Scambio valido per 120 secondi e solo nella stessa epoca di conversazione. [Matrice Windows e ZIP estratto](https://github.com/MATRIXNEO23/jarvis/actions/runs/42145643937) superati sul commit `0d99357`. Nessuna pubblicazione in Download.

## Finestre Windows con comandi integrati

Le finestre Tk di Jarvis usano una barra interna scura con riduci, massimizza/ripristina e chiudi. La rimozione della cornice avviene sul wrapper Win32 e mantiene i protocolli di chiusura Tk. La barra si applica anche alle finestre secondarie mappate dopo l’avvio e alla finestra separata di configurazione segreti Telegram. Le finestre native di sistema seguono l'aspetto Windows. La run [42144862058](https://github.com/MATRIXNEO23/jarvis/actions/runs/42144862058) sul commit `72af40e` ha superato 639 test per versione Python, compresa la prova Windows della barra su finestra principale e secondaria. Il pacchetto CI è stato generato e verificato dopo estrazione. Nessuna pubblicazione in `Download` per questa modifica.

## 6 novembre 2026 — candidata Gemma pubblicata

La [run Windows 42142495567](https://github.com/MATRIXNEO23/jarvis/actions/runs/42142495567) sul commit `5d554c8` ha superato la matrice Windows, i 26 test mirati dal pacchetto estratto e il caricamento della DLL inclusa. Il commit `7088b95` su main ha pubblicato `Download/Jarvis-Gemma-Avvio-Programmi-5d554c8.zip` e aggiornato `Download/README.md`. Archivio: 8.093.345 byte, SHA-256 `e54912b4e3de94c06dc654cd2fc4f64b698f0f2f2249ff67dab6e091022b8944`. Candidata per il collaudo su Pavilion. Voce, Gemma e app reali restano da provare.

## 6 novembre 2026 — avvio app con varianti locali e prova Gemma

I commit `9c08935` e `56fd9e4` riusano il catalogo e le autorizzazioni di Programmi e app. Una selezione abilita i verbi comuni. Frase senza nome, risposta successiva con nome esatto e suggerimenti per somiglianza sono stati verificati con launcher controllato. Il suggerimento Gemma richiede il prefisso vocale «con Gemma» in modalità conversazione e una conferma della scelta. La prova del selettore usa un modello simulato e verifica una generazione e l'esclusione della cronologia.

La [run Windows 42139706373](https://github.com/MATRIXNEO23/jarvis/actions/runs/42139706373) su `56fd9e4` ha superato 638 test per versione di Python. Restano il collaudo con voce, Gemma e app reali sul Pavilion, e il gate di rilascio. Nessuna nuova build pubblicata.

## Apertura locale e prova Gemma su richiesta

Programmi e app riconosce anche aprimi, avviami, lanciami, esegui, fai partire e metti in esecuzione. Una frase senza nome apre un chiarimento locale. I nomi simili suggeriscono un'app autorizzata e attendono una scelta. La prova vocale esplicita «Jarvis, con Gemma, mi serve qualcosa per vedere un film» seleziona una proposta fra 1–12 app abilitate e disponibili, senza cronologia nel prompt. Il motore chiede conferma e applica i permessi correnti. Gemma usa una sola generazione con il modello già caricato se disponibile. Prova Windows CI e collaudo Pavilion da registrare.

## 6 novembre 2026 — JRV-004, verifica Windows

La [run 42129127625](https://github.com/MATRIXNEO23/jarvis/actions/runs/42129127625) sul commit `e51c269` ha superato 635 test per job con Python 3.11 e 3.12. È passata anche la prova live Windows Search sul job previsto. Copertura mirata nei log: rifiuto e revoca dei callback, Telegram simulato, disconnessione immediata, revoca durante avvio del bridge e toggle HUD.

`dea28e6`: consenso console e planner. `4dd0e1f`: consenso Telegram e generazione di revoca del planner. `43d29e4`: ripristina il guard esplicito di rifiuto dell'autodiagnosi, mantenendo il controllo dell'epoca. `36d549e`: verifica nel trasporto prima dell'invio e scarto dei piani di un contesto superato. `e51c269`: inizializza lo stato Telegram nella fixture del pannello rapido dopo il fallimento della run 42129015218. Il risultato è simulato per account GPT e Telegram. Restano la configurazione persistente per funzionalità, le prove con account reale e il gate di rilascio. Una revoca dopo l'invio può scartare la risposta in Telegram, mentre i dati già trasmessi restano fuori dal controllo di Jarvis.

Prossimo intervento: JRV-005, isolare la cronologia Gemma tra progetto e contesto generale conservando il modello caricato e gli archivi persistenti. Verificare anche la configurazione applicata al provider quando si modificano contesto massimo e output.

## JRV-004 — Telegram e revoca durante la conferma

Il worker Telegram attende fino a 30 secondi una decisione monouso della console prima di inviare messaggio e contesto recente a GPT. Il collegamento Telegram e il recapito dei messaggi approvati dal proprietario restano separati. Una richiesta scaduta o riferita a un bridge disattivato viene scartata. Il pianificatore usa lo stesso dialogo e conserva la generazione di consenso fino al worker. La disattivazione o la perdita del collegamento GPT revoca l'accesso del worker Telegram. Verifica Windows e collaudo con account reale distinti.

Il trasporto ricontrolla il consenso dopo l’avvio del bridge e prima di scrivere la richiesta. La disconnessione revoca subito planner e Telegram. Telegram scarta le risposte arrivate dopo la revoca. Un piano ricevuto o confermato dopo un cambio di contesto viene scartato prima dell’esecuzione.

## 6 novembre 2026 — JRV-004, consenso per richiesta dalla console

Il percorso `run_gpt` richiede il consenso prima di avviare un worker di inferenza e ricontrolla connessione, stato ed epoca dopo il dialogo. Login, stato e disconnessione seguono il loro percorso. Il raffinamento chiede prima di consumare il token, la spiegazione distingue il testo dell'anteprima, il chiarimento progetto conserva il riepilogo locale e l'autodiagnosi riusa il consenso specifico già esistente. I comandi locali precedono il dialogo del pulsante GPT. Il pianificatore separa il consenso a inviare la richiesta dall'approvazione del piano. Aggiornati i test Windows dei callback. Verifica CI sul nuovo commit in attesa. Restano il worker Telegram, la policy persistente per funzionalità e il collaudo con account reale.

## Verifica Windows e blocchi di rilascio

`db0b3a4`: [run 42113303954](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113303954) verde su entrambi i job, 628 test per job. Il test di finestra Tk reale e i casi di accettazione, PID e finestra sono passati. Nessuna prova di apertura Netflix sul Pavilion.

`09c5e95`: [run 42113573907](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113573907) ha riprodotto un errore della nuova fixture, che non passava `queue` all'esecuzione isolata del poll. `75bef3a` ripristina la dipendenza mantenendo le asserzioni. Nella [run 42113970995](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113970995) i test unitari risultano verdi in entrambe le versioni Python. I job 127548563547 e 127548564393 hanno registrato 629 test ciascuno e hanno superato la nuova prova sulla risposta vocale obsoleta. La prova live di Windows Search è passata nel job Python 3.12 previsto. L'intera matrice è conclusa con successo.

Prossimo intervento JRV-004: trattare separatamente login e inferenza. Il pulsante GPT verifica un consenso condizionato alla presenza della configurazione Gemma prima di instradare azioni locali. Il chiarimento progetto, il raffinamento file e la spiegazione del file arrivano a `run_gpt`. Telegram chiama direttamente `service.call` dal worker e il pianificatore riceve lo stesso servizio. L'autodiagnosi ha un dialogo già dedicato. Per ogni percorso verificare esplicita autorizzazione, rifiuto, revoca e assenza di invio di contenuti altrimenti. Conservare il percorso locale e il consenso alle azioni come controlli distinti.

Per JRV-011 resta da collegare il pacchetto a una dipendenza esplicita dalla matrice Windows sullo stesso SHA, mantenendo separata la verifica dell'archivio estratto. La DLL no-AVX2 deve restare disponibile e verificabile per una ricostruzione futura. Il rilascio pubblico dipende anche dai collaudi obbligatori sul Pavilion, ancora aperti. Nessuna build pubblicata nel checkpoint.

## Voce Gemma: risposta in corso e cambi di contesto

La run [42112965273](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112965273) su `cfa0e19` ha concluso la matrice Windows con successo. `db0b3a4` ha introdotto l'osservazione del PID e della finestra, run [42113303954](https://github.com/MATRIXNEO23/jarvis/actions/runs/42113303954). Il controllo osserva una finestra Win32 con titolo dello stesso PID, non minimizzata e non nascosta da DWM. Può rilevare una finestra già esistente o coperta. L'app Store può usare un altro processo per la finestra.

JRV-001/002: `jarvis.py` descrive Gemma locale quando si attiva la modalità conversazione. Il risultato vocale, compreso l'errore, ora appartiene alla generazione di contesto che ha avviato la richiesta: il poll scarta la risposta quando nel frattempo sono cambiati modalità, progetto o stato GPT. La risposta scritta mantiene il percorso esistente. La nuova prova esegue il callback reale su eventi controllati. Restano microfono e TTS reali, oltre all'isolamento della cronologia interna della sessione Gemma (JRV-005).

## Checkpoint Windows e osservazione avvio programmi

La matrice Windows della run [42112346657](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112346657) su `57c3dd1` ha completato 626 test per job con esito OK. La revisione ha trovato il conflitto app/progetti nel ramo generico del parser. `c8c697c` ha riservato il ramo progetti esplicito, ma la run [42112742159](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112742159) ha riprodotto un errore del nuovo test: Accesso file, ancora attivo nella fixture, consumava «apri Netflix». `cfa0e19` isola il test del ramo di riserva nella run [42112965273](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112965273). Resta da verificare la precedenza app/file con i due componenti configurati insieme, mantenendo l'apertura implicita nella cartella Explorer.

JRV-003: `program_apps/native.py` conserva il PID fornito da Windows per l'attivazione Store o ricavato dall'handle ShellExecute. Il messaggio distingue accettazione, PID disponibile e osservazione immediata di una finestra Win32 visibile con lo stesso PID. App con finestra ospitata da un processo differente e finestre che appaiono più tardi richiedono verifica ulteriore. `tests/test_program_apps_native.py` copre i tre esiti e la prova Win32 su una finestra Tk controllata. Restano CI Windows sul commit, Netflix reale e affidabilità della corrispondenza finestra/app Store.

Altri blocchi registrati: il workflow ZIP scarica la DLL da un artefatto CI con scadenza 18 novembre 2026 e riscrive parti del runtime durante il packaging. La sessione Gemma conserva in RAM il dialogo anche quando cambia progetto e il provider già caricato conserva la configurazione precedente dopo un cambio delle impostazioni. Da verificare isolamento, aggiornamento della configurazione, consenso GPT, collaudi Pavilion e gate di rilascio.

## Riesame integrazione e programma di verifica

La run 42112126088 ha confermato la correzione del raffinamento file e del contesto in attesa. Il job 127542105108 ha chiuso con 2 fallimenti e 11 errori residui su 626 test. Il successivo checkpoint `57c3dd1` è in verifica nella run 42112346657. La revisione indipendente ha rilevato che anticipare il gestore progetti senza filtro avrebbe classificato «apri Netflix» come progetto quando l'add-on è spento. Il checkpoint successivo riserva i comandi che nominano esplicitamente un progetto e aggiunge il caso Netflix al test del callback di console.

| Sequenza | Integrazione | Prova richiesta |
| --- | --- | --- |
| 1 | File, voce, autodiagnosi, app e progetti | Callback reali con trascrizione e servizi controllati, suite Windows 3.11/3.12 |
| 2 | Gemma, TTS e hotword (JRV-001/002) | Output pulito nei due ingressi, ascolto automatico con hotword e standby manuale, collaudo Vosk/TTS sul Pavilion |
| 3 | Programmi e add-on (JRV-003/007) | Verificare precedenze, alias, revoca, accettazione Windows, PID osservabile e finestra associata. Collaudare Netflix con add-on attivo e app autorizzata |
| 4 | GPT e Telegram (JRV-004/008) | Inventario chiamate, consenso monouso prima dell'invio, rifiuto e nessun fallback implicito, collaudo account separato |
| 5 | Memoria, file e progetti (JRV-005/006/009) | Isolamento tra contesti, revoca permessi, conservazione dati esistenti, Windows Search e fallback su più unità |
| 6 | Risorse e rilascio (JRV-010/011) | Confronto con Kobold sul Pavilion, stessa configurazione. ZIP dallo stesso SHA collaudato, avvio da estrazione pulita e gate automatico senza dipendenza dal workflow assente su main |

Blocchi individuati da verificare: raffinamento file, spiegazione file e chiarimento progetto chiamano `run_gpt` senza passare dalla policy per funzionalità. Il launcher Store dispone di un PID ma lo scarta. L'attuale workflow Gemma manca su main e il percorso manuale può arrivare alla pubblicazione indipendentemente dalla suite. Lo ZIP modifica anche file Python in fase di assemblaggio, quindi i sorgenti della suite e quelli effettivamente distribuiti richiedono un controllo separato.

## 5 novembre 2026 — suite Windows del ramo Gemma

La run [42106340408](https://github.com/MATRIXNEO23/jarvis/actions/runs/42106340408) ha riprodotto 8 fallimenti e 13 errori su 626 test. `7ff60e2` collega il vero `ChatTransport` al servizio simulato in `tests/test_file_refinement.py`, usato anche da `tests/test_pending_file_context.py`. La relativa [run 42112126088](https://github.com/MATRIXNEO23/jarvis/actions/runs/42112126088) è stata avviata sul commit esatto.

Il checkpoint corrente applica lo stesso cablaggio a `tests/test_activity_status.py`. La fixture in `tests/test_voice_corrections_review.py` riproduce il contenitore `[False]` usato dal callback. `tests/test_gpt_voice_addressing.py` verifica che Gemma occupata rifiuti solo la richiesta indirizzata e che il parlato ambientale non venga inviato o accodato. `tests/test_self_review.py` controlla la precedenza della diagnosi rispetto al percorso Gemma della voce e al percorso GPT del testo. In `jarvis.py` i progetti espliciti tornano a precedere il filtro generico di avvio app, dopo la gestione dei file.

Gate aperto: verificare test mirati e matrice Windows 3.11/3.12 sul checkpoint, quindi analizzare eventuali fallimenti residui. JRV-001 e JRV-002 richiedono ancora collaudo reale. JRV-003 non ha conferma di apertura Netflix. Il rilascio resta subordinato alle prove obbligatorie.

## Fonte di verità e stato
Repository: `MATRIXNEO23/jarvis`. Ramo di integrazione Gemma: `feature/gemma-local-20261104`. Pubblicazione ZIP su `main/Download/Jarvis-Gemma-PROVA-CORRETTA.zip`; pagina `main/Download/README.md`. Il ramo `main` contiene anche pubblicazioni automatiche: NON assumere che il codice applicativo su main coincida con il ramo Gemma. Verificare sempre ref/commit, ZIP e workflow prima di dichiarare un rilascio.

Checkpoint verificato: il modello Gemma risponde nella chat principale (test visivo dell'utente); la sintesi vocale è stata collegata via `speak_result` (commit `5481310272c474de9a8f210dd8d196cf39698627`), build Windows riuscita run `42081191577`. Il guardrail per richieste esplicite di avvio senza esecuzione è nel commit `950acac1ed3d33d0bae8f4428ed1be4e6350a99f`, build riuscita run `42081766861`, ZIP pubblicata su main. Non equivale a test reale del PC.

Problema Netflix: prima Gemma rispondeva «Ti aiuterò a avviare Netflix» senza prova dell'avvio; poi la console mostrava «PROGRAMMI > Non ho avviato il programma. Attiva Programmi e app...». L'utente ha confermato che Netflix era già spuntato ma l'add-on **Programmi e app era disattivato**. È la causa operativa individuata; l'utente deve ancora confermare un avvio riuscito dopo attivazione. NON registrare «Netflix funziona» come collaudato.

## Mappa di esecuzione (codice verificato sul ramo Gemma)
```text
Utente: tastiera / microfono (Vosk e controlli voce)
                 |
                 v
          jarvis.py (GUI, eventi, stato, console)
                 |
       +---------+---------------------+
       |                               |
  comandi espliciti                conversazione
  try_file_command                 send_console_input
       |                               |
  try_program_command             configurazione GGUF valida?
       |                            /             \
  ProgramService.parse_command    sì             no
       |                           |               |
  addon_manager.is_active       submit_gemma_trial  GPT solo secondo
       |                           |                impostazioni/permessi
  submit_local / LocalEngine       | 
       |                       NativeConversationSession
  execute_program                 -> NativeChatAdapter
       |                          -> NativeLocalProvider
  ProgramService.execute          -> NativeGemmaBridge
       |                          -> DLL KoboldCpp no-AVX2 / GGUF
  allowlist app, consenso,           |
  identità e disponibilità       poll_gemma_trial
       |                          -> write_line + speak_result
  program_apps/native.py
  avvio Windows EXE/LNK/Store
       |
  risultato reale in console / voce
```
Il modello non esegue programmi autonomamente: il testo libero generato non è un comando sicuro. Il servizio ProgramService verifica app consentita, identità, catalogo, disponibilità, ambiguità, revoca e permesso add-on. Evitare shell arbitraria e bypass delle spunte.

## File chiave
- `jarvis.py`: punto di composizione GUI, eventi voce/chat, `send_console_input`, `try_file_command`, `try_program_command`, `submit_local`, `submit_gpt`, `submit_gemma_trial`, `poll_gemma_trial`, `speak_result`. Attenzione ai rami di risposta e alle priorità di routing.
- `local_engine.py`: motore deterministico e TaskResult, delega alle capacità approvate; nessun codice generato eseguito.
- `addon_manager.py` / `addon_ui.py`: installazione, attivazione e permessi separati. Manifest `.jaddon` dichiarativi, nessun codice eseguibile nell'installazione.
- `program_apps/ProgrammiApp.jaddon`: azione `addon.programmi_app.avvia` -> `apps.launch`; **OFF iniziale**.
- `program_apps/service.py`: `launch_query`, `protected`, `blocked`, `parse_command`, `execute`, `save_preferences`, `refresh_catalog`. `available()` dipende da `enabled()`; la spunta della singola app NON abilita l'add-on. `programs.json` salva elenco, disponibilità, preferenze e alias. L'esecuzione richiede `enabled=True` per l'app e add-on attivo.
- `program_apps/native.py`, `windows_apps.ps1`: enumerazione e avvio app Windows (classiche/Store); `program_apps/ui.py`: selezione, alias, aggiornamento, test avvio.
- `local_model/native_config.py`, `native_settings.py`, `native_ui.py`: GGUF, DLL, threads, context_size, max_output, sampling; impostazioni configurabili.
- `local_model/native_conversation_session.py`: storico locale limitato, costruzione prompt con budget; esplicitamente nessuna azione desktop né fallback online.
- `local_model/native_chat_adapter.py`, `native_factory.py`, `native_initializer.py`, `native_provider.py`, `native_bridge.py`: trasporto e inferenza KoboldCpp in processo, senza servizio HTTP; errore nativo con status/stopreason.
- `local_model/online_permissions.py`: controlli permessi online; verificare TUTTI i percorsi prima di affermare che nessuna chiamata online parte senza consenso.
- `file_access/`: accesso file e ricerca; `project_voice.py`, `workspace_memory.py`, `conversation_memory.py`: progetti e continuità; `voice_control.py`, `speech_activity.py`: comandi e stato voce.
- `.github/workflows/gemma-windows-test-package.yml`: build prova Windows da ramo Gemma; scarica DLL no-AVX2 pinned, esegue test e pubblica ZIP su main. Trigger push include `jarvis.py`, `local_model/**`, build script e workflow; **modifiche solo a `program_apps/**` non attivano necessariamente questa build**.
- `tools/build_gemma_clean_trial.py`: creazione ZIP. `Download/README.md`: indice download. `docs/PROGRAMMI-APP-IMPLEMENTAZIONE-20261103.md`: design, controlli e prove precedenti.

## Vincoli e decisioni permanenti
Windows 10 x64, HP Pavilion i3-2100 (AVX, NO AVX2), 10 GB RAM, Radeon HD6450 1GB; zero costi extra, nessuna API a consumo. Preferire CPU no-AVX2 e mini-LLM locale; online solo con consenso esplicito. Gemma deve usare la chat principale e TTS esistente, non una chat separata. Tutte le nuove capacità preferibilmente add-on `.jaddon`, core solo per collegamenti tecnici motivati. Non migrare indiscriminatamente le vecchie funzioni. App Store e desktop devono essere supportate, ma solo se selezionate. Sinonimi e alias vocali; non eseguire comandi senza autorizzazione. Microfono in standby/spento all'avvio, poi controllo manuale e wake word «Jarvis»; evitare consumo token a microfono acceso. Preservare preferenze, memoria, progetti, salvataggi e rollback. Non dichiarare un successo basandosi sulla sola risposta testuale del modello.

## Rischi / opportunità di miglioramento
1. Diagnostica specifica di `try_program_command`: distinguere add-on OFF, app non selezionata, catalogo obsoleto, parser non riconosce, ambiguità, permesso revocato, avvio Windows fallito. Il guardrail del commit `950acac` usa ancora un messaggio generico; non è una riparazione del launcher.
2. Allineare messaggi TTS/console all'esito `ProgramResult`, non al testo del modello. Eseguire prove reali per EXE/LNK e Store (Netflix) su Windows.
3. Testare input sia scritto sia vocale (wake word, varianti «apri», «avvia», alias) e tutte le combinazioni: add-on OFF/ON, app non spuntata/spuntata, app assente, due match, modifica/revoca consenso.
4. Verificare che la sintesi vocale non blocchi la UI e rispetti mute e preferenze; testare risposte Gemma e errori.
5. Verificare l'integrazione tra modello locale e azioni: le richieste non parseabili non devono diventare «ho fatto» fittizi; proporre eventualmente un intent strutturato validato, senza dare al modello privilegi di esecuzione.
6. Audit di tutti i percorsi online (chat, voce, fallback, comandi GPT) per conferma esplicita e zero traffico non autorizzato.
7. Test regressione, benchmark reali su CPU AVX-only (RAM, latenza, TTFT), timeout e recupero errori; nessuna garanzia di prestazioni senza misure.

## Ripresa operativa per un nuovo agente / programma
1. Aprire questo file e `docs/PROGRAMMI-APP-IMPLEMENTAZIONE-20261103.md`; verificare SHA corrente di main e ramo Gemma.
2. Leggere `jarvis.py` (funzioni nominate sopra), `addon_manager.py`, `program_apps/service.py`, `program_apps/native.py`, `local_engine.py`, `local_model/native_conversation_session.py`.
3. Chiedere soltanto l'esito mancante: «Dopo aver attivato l'add-on, Netflix si apre?». Non assumere fallimento o successo.
4. Se fallisce, riprodurre con app spuntata e add-on ON, aggiungere test mirato e diagnostica, correggere causa minima, preservare permessi e percorsi esistenti.
5. Eseguire test Windows, compilare ZIP, verificare workflow e artefatto pubblicato, aggiornare `Download/README.md` con nome chiaro, commit e stato di collaudo. Evitare di dire «pubblicato» prima di controllare.
6. Aggiornare questo handoff dopo ogni modifica: data, ref, commit, test, ZIP, risultati reali, problemi aperti. Nessun lavoro in background presunto.

## Riferimenti release
- Gemma chat/voce: `5481310`, run `42081191577`.
- Guardrail programmi: `950acac`, run `42081766861`.
- README Download aggiornato: `7e1cfad8113205a266d63785c374dc967116f7a9`.
- URL ZIP: `https://github.com/MATRIXNEO23/jarvis/raw/refs/heads/main/Download/Jarvis-Gemma-PROVA-CORRETTA.zip`.
- **Non ancora collaudato**: Netflix dopo riattivazione add-on; TTS reale su Pavilion.

## JRV-002 — console senza trascrizione vocale, 6 novembre 2026

Confronto tra le candidate `f387779` e `9adc86e`: il percorso da `voice_text` alla riga `TU` non è cambiato con Telegram. Riprodotti due difetti: il profilo Gemma ignorava un modello Vosk presente solo nel profilo sorgente del launcher e lo stato generico di microfono spento sostituiva il messaggio di errore.

Jarvis ora cerca il modello anche nel profilo sorgente e conserva l'errore di avvio del microfono, visibile anche in console. Restano il controllo della hotword e la modalità selezionata. Le due regressioni riprodotte falliscono prima del fix e passano dopo. Suite Windows e prova acustica sul Pavilion da verificare.

## JRV-002 — Ascolto continuo senza parola di richiamo

Il richiamo è richiesto in modalità Hey Jarvis. Ascolto continuo accetta la trascrizione direttamente. Entrambe mostrano sotto TU le richieste riconosciute, provano prima i gestori locali e usano Gemma per le richieste rimaste senza risposta. Durante la dettatura manuale le frasi libere vanno al campo di destinazione e il comando esplicito di arresto funziona anche senza prefisso. Il collaudo acustico sul Pavilion resta da fare.
