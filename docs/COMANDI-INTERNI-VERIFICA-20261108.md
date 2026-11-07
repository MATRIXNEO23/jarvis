# Comandi interni — verifica per passi

Riferimento requisiti: [piano confermato](superpowers/plans/2026-11-08-local-command-routing.md).

1. Riproduzione `e4641bea24f8c2439d0b52e48c5de78aa8d9fa26`, PR56, run42426651526:928test Windows per Python3.11/3.12,7failure attese/0errori. Sintomo console/engine stato e browser e5varianti mancanti. Gli assert su negazioni e dialoghi già coperti passano; nessuna prova di microfono/GGUF personale.
2. Prima candidata `55be411ab9f1df450f1ae61767f96f7c6ab200ab`, stesso tree locale5d96302. Run42427227254 ancora da concludere. Riuso riconoscimento voce nella console e negli ingressi engine/file, sinonimi, mostra Download apertura, help. Il raccordo interpretazione Gemma resta da fare.
3. Review indipendente readonly dell'esatto diff e464..5d96302: individuata regressione statica nella priorità del chiarimento su progetti esistenti chiamati Cronologia/Stato sistema. Preparato test con callback console+risolutore progetti e WorkspaceMemory reali; solo cambio contesto finale controllato. Verifica Windows Red del nuovo caso prima della correzione.

Prossimo passo: leggere Red del caso review, poi conservare la priorità del risolutore progetti. Nessuna build o test funzionale Linux. Lacune dichiarate: nuovo test console sostituisce submit_local, quindi bookkeeping ledger non coperto direttamente da questo test; Netflix viene coperto solo dal gate simulato nel nuovo test, mentre le prove applicative preesistenti restano necessarie; verificare mostra Download anche con servizio file attivo.
