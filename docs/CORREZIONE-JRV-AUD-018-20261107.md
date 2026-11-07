# JRV-AUD-018 — protezione delle impostazioni illeggibili

Stato: candidata nei sorgenti in bozza, GreenWindows ancora da eseguire.
Base011 `5994d1751fdf02037f2ce3082dbc19a072d4c4a3`, [bozza46](https://github.com/MATRIXNEO23/jarvis/pull/46), ramo `fix/jrv-aud-018-settings-recovery-20261107`. Conservate001–011;012–017 restano distinti. Priorità anticipata perché protegge avvioMIC/GPT e dati, prima delle rifiniture packaging.
[Specifica](superpowers/specs/2026-11-07-jrv-aud-018-design.md), [piano](superpowers/plans/2026-11-07-jrv-aud-018-fix.md), [recupero manuale](RECUPERO-IMPOSTAZIONI.md).

## Problema e modifica minima

load_settings tornava ai DEFAULTS permissivi dopo errori JSON/UTF8/IO o radice nonoggetto: auto_listen eGPTTrue. initial_launch poteva quindi riattivare ascolto automatico nonostante il file originario contenesse un opt-out non più leggibile. save_settings poteva sostituire quel file con il dizionario di fallback, perdendo preferenze recuperabili. Questo non dimostra inviiGPT automatici: collegamento/status e inferenza sono distinti.

|File/funzione|Intervento|Compatibilità e rischio|
|---|---|---|
|settings.py/_read_settings_object,load_settings|Parser condiviso controlla oggettoJSON eflagcritici presenti booleani. Fileassente separato daglierrori; esistenteilleggibile avvia prudente con6flagFalse e warning opzionale senza contenuto privato|Assente/valido/legacy mantengono default/normalizzazione. Tipoerrato gpt/auto diventa errore invece di default permissivo; scelta intenzionale documentata|
|settings.py/save_settings|Rilegge targetindipendentemente dal dict passato; errore rifiutato comeOSError prima di mkdir/tmp/replace|Impedisce perdita dopo dictcopy/corruzione successiva a load. Non resetta/rinomina/cancella/creabackup. Lettura aggiuntiva piccola per save, HDDnonmisurato|
|jarvis.py/main,initial_launch|Collector warning caricato primaTk, avviso inconsole una volta prima dell'avvio automatico|Conprofilocorrotto valoriUIoff e0schedulerGPT/mic/TTS; profilo valido conserva comportamento confermato. Nessun nuovo popup|
|jarvis.py/telegram_reconfigure|Errore save mostrato nello status senza eccezioneTk non gestita|Altrocaller già compatibili conOSError/ValueError. Nessun contatto/persistenza alterato in profilo reale|

Il test storico che richiedeva GPTTrue dopo `{"gpt_enabled":"no"}` è aggiornato intenzionalmente aFalse, autoFalse eoriginaletextidentico. Non è una preferenza valida. Altre asserzioni di default/migrazione/roundtrip conservate.

## Red e review

Windows2022 x64, `python -m unittest discover -s tests -v`.

|Fase|Source/run|Python/job|Esito|
|---|---|---|---|
|Red1|c021a84bce5eb67d71c04d6d91f358569cda301f /42353608784|3.11.9/128346803002|828test,34failure,0errori,125.779s|
|Red1|stesso|3.12.10/128346802760|828test,34failure,0errori,133.185s|
|Red2|59c6d3f48015607cac5a554e0e26f7ccfff4e1ae /42353743362|3.11.9/128347198453|829test,37failure,0errori,128.708s|
|Red2|stesso|3.12.10/128347198635|829test,37failure,0errori,139.055s|

Fallimenti tutti nel nuovo modulo018, più asserzioni per subtest. I casi del nuovo collector falliscono per APIwarnings ancora assente (TypeError trasformato infailure esplicita); non indicano regressioni del profilo valido preesistente. Mic/GPTautorun e salvataggio distruttivo sono riprodotti indipendentemente.022/023 non osservati/aperti.

Review preventiva readonly:3gaptest corretti prima del runtime: DEFAULTScompleti anche per{} echiavimancanti, invalidicritici conaltri4automatismiTrue, mutazioniguardmonitorate prima dirifiuto.18nuovi metodi/829attesi. Reviewruntime e ricontrollo senza difetti/blocchi rilevati; revisore non ha eseguito test. Locale soloAST/diff, nessun test funzionaleLinux.

## Limiti e recupero

La correzione protegge il file rilevato illeggibile; non ricostruisce preferenze mancanti e non fa backup/reset automatici. Il percorso manuale è documentato; viene simulato solo su fixture. Fileassente conserva defaultiniziali, quindi non va presentato comeavvioprudentementeOFF. Cronologie/progetti/credenziali non sono toccati.

Guard non è un CAS filesystem: un editor esterno può cambiare il target dopo la verifica e prima dell'atomicreplace, limite di concorrenza già esistente. Nessuna nuova garanzia perpiùistanze. No benchmarkWindows10/i3/HDD, profilo utente reale, microfono/account o ZIPestratto testati. Nessuna nuova dipendenza/schema/servizioAPI, build/ZIP/merge/release o modifica configurazioni/dati reali. Ramo reversibile; prima di build affidabile servono Green e successivo collaudo pacchetto/target.
