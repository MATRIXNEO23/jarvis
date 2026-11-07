# JRV-AUD-022 — finalizzazione Tk su worker nella suite Windows

Blocco già osservato prima della021, ricomparso su source021 `6504abffe0553461a2f44c07c9833d67a2abf2e1`, run42363252951/job128375837908 Python3.12.10. Variable.__del__/Image.__del__ chiamano Tcl dal thread sbagliato, poi Tcl_AsyncDelete interrompe la suite durante DocumentSaveRace; nessun riepilogo completo. I test021 non erano ancora iniziati. Python3.11 dello stesso source completa900test in172.068s, tutti16nuovi passati. Non è prova di causa nel runtime vocale.

## Indagine limitata, prima della correzione

Il test attivo usa un worker Win32 senza Tk. Prima di esso girano fixture HUD con vere variabili/immagini Tk: ipotesi di cicli di riferimenti rimasti dopo destroy e raccolti in seguito da un worker. Riprodurre con GC automatico disabilitato soltanto in un figlio temporaneo, eseguire fixture vere con il loro teardown e forzare raccolta da worker dopo il ritorno. Non sopprimere finalizer/errori o saltare casi. SAPI/account/microfono e poller di rete non fanno parte della prova; request del solo campionatore di rete intercettata nel figlio.

Una nuova prova con quattro subtest isolati: ActivityStatus, AnimatedHUD, header e HUD nativo. Ogni figlio deve completare la fixture senza skip, pubblicare thread/stadio diagnostico e terminare senza warning Tk/fatal dopo worker GC. Le fixture successive servono a evitare lo stesso difetto di ownership dopo i test header/Gemma. Non attribuire a priori ogni aborto passato a questi oggetti: distinguere riproduzione specifica e sintomo storico.

## Correzione subordinata alle evidenze

Se riprodotto, ritirare i riferimenti ai widget già chiusi e raccogliere le risorse Tk sul thread principale nel teardown delle fixture interessate. Nessuna modifica al GC globale dell'app, scheduler nativo, comandi Windows o dati. Non mascherare l'errore con skip/retry/disabilitazione GC nella suite principale. Il controllo avviene nei soli test e non certifica ogni possibile ciclo Tk del runtime.

022 è un intervento distinto tracciato ma accompagna021 nella bozza51 perché blocca il suo Green. Runtime TTS resta identico durante questa indagine, nessuna build/merge/release. Prove funzionali solo Windows; Linux solo lettura/AST. Prima del prossimo fix serve Green completo sulle due versioni, rapporto/evidenza e checkpoint remoto di entrambi gli ID.
