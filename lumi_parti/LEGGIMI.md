# lumi_parti — pezzi di Lumi spostati fuori da jarvis.py

Ogni file contiene funzioni che prima erano dentro `main()` di `jarvis.py`, con il codice
invariato. `main()` le crea con `installa(d)`, dove `d` (`lumi_contesto.Vivo`) dà sempre il
valore attuale delle variabili di `main()` che usano.

| File | Cosa contiene |
|---|---|
| `voce.py` | scelta e prova delle voci, voci naturali, dettatura, premi per parlare, ascolto all'avvio |
| `documenti_progetti.py` | documenti, progetti, piani di lavoro |
| `diagnostica.py` | rapporto e finestra della diagnostica dei servizi |
| `modello_memoria.py` | anteprima multimodello, memoria, richieste al modello locale, «cervello locale/online» |
| `interfaccia.py` | pagine delle impostazioni, chat, avvio, comandi su Lumi (riduci, riavvia, sveglia…) |

Interfaccia Telegram: `telegram_addon/lumi_ui.py`. Strumento usato per spostare:
`tools/sposta_funzioni.py` (solo sviluppo). Piano e registro: `docs/PIANO-DIVISIONE-JARVIS.md`.
Nessun dato o impostazione qui: restano nel profilo utente come prima.
