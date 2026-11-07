# Jarvis007 — consegna, 7 novembre2026

[Download007](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-007.zip). Richiesta esplicita di concludere le modifiche, pubblicare direttamente se i controlli passano e preparare l’handoff. Source `9f8c5f582b98a4ac131c41a4170b194c98abc3fa`, [run42420559553](https://github.com/MATRIXNEO23/jarvis/actions/runs/42420559553), stato candidata con collaudo PC pendente. SHA256 `a5a24f35b410a45bed3dd08ed2180563d429e82cbe0a878045f4e7157182408f`, 8138643 byte/119file.

## Modifiche incluse

- JRV-AUD-024: timer numerico o in lettere dalla console Invio/Invia, gate prima dei programmi/Gemma, priorità documenti/file/progetti mantenuta. Parser limitato ai comandi espliciti: menzioni negate/conversazionali non avviano timer. Sveglia mattina07:30 e giorno successivo.
- JRV-AUD-025: aiuto/help/comandi apre una guida locale anche se un modello è configurato o un dialogo è pendente, senza interpretare l’aiuto come filename/risposta.8sezioni: primi passi, catalogo base, timer/sveglia, voce, modelli/permessi, file/app, progetti/Telegram, tastiera. Cataloghi esistenti riutilizzati e aggiornati alla riapertura. Nessun invio modello o esecuzione degli esempi, testi readonly/scorrevoli e non letti a voce.
- Pulsante? e F1, Ctrl+L dalla guida e dalle impostazioni al campo comando, Ctrl+, preesistente. La guida spiega **Esegui locale** per i comandi base che Invio non intercetta. Scelta Gemma/GPT invariata: nessuna nuova modalità GPT per sessione implementata.

## Verifica e provenienza

[
  {
    "id": 128547855883,
    "python": "3.11.9",
    "scope": "source",
    "tests": 922,
    "seconds": 135.838,
    "failures": 0,
    "errors": 0,
    "skipped": 0
  },
  {
    "id": 128547856153,
    "python": "3.12.10",
    "scope": "source",
    "tests": 922,
    "seconds": 148.153,
    "failures": 0,
    "errors": 0,
    "skipped": 0
  },
  {
    "id": 128548730673,
    "python": "3.12.10",
    "scope": "extracted runtime with test-only supports",
    "tests": 922,
    "seconds": 152.733,
    "failures": 0,
    "errors": 0,
    "skipped": 0
  }
]

Source922test su3.11/3.12 Windows2022, zero failure/errori/skip. Quattro nuovi metodi aiuto includono UI/Tk e scorciatoie reali; nessun modello/microfono/account. Red aiuto9d96/run42419450038: atteso mancato invio alla guida;926test poiché l’import della classe timer duplicava7metodi, corretto a import modulo. Tentativocee342/run42419926302 annullato prima della pubblicazione per review su scorciatoie da finestre secondarie e istruzioni fedeli al router. Review readonly e ricontrolli senza blocchi; nessun assert indebolito. Sourceb38/run42420088509 aveva922test verdi nei sorgenti, ma il package è stato sostituito prima della pubblicazione: un riferimento forte al callback focus tratteneva un ciclo con il root Tk. Usato weakref e verificato il rilascio del callback dopo destroy; non dichiarato un crash runtime riprodotto.

Build effettiva Windows con dipendenza nativa persistente e digest DLL fissato `ac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba`. Nessuna trasformazione di Python/MJS/PS1 dopo la suite; metadati ZIP normalizzati, manifest/versione007, riproducibilità con clock diverso. Estratto pulito: CRC, hash, guide/link, import/DLL, avvio/chiusura normali e rifiuto di errore callback Tk iniettato. Poi922test sui moduli estratti con soli supporti di sviluppo aggiunti temporaneamente, non distribuiti; nessun runtime copiato dal checkout. Hash ricontrollati dopo i test. Searchlive3.12 con ripristino servizio/fixture.

[Evidenza release](evidence/jarvis-007-release-20261107.json), [package](evidence/jarvis-007-package-20261107.json), [timer024](CORREZIONE-JRV-AUD-024-20261107.md). Avvisi delle vecchie fixture Tk con Mock restano nei log; zero errori del runner non equivale a stderr sempre vuoto.

## Installazione e limiti

Estrai in cartella nuova, avvia solo `Jarvis-Gemma/avvia_jarvis.bat`. Profilo Gemma-Trial come006; non sovrascrivere o cancellare vecchie cartelle/configurazioni. Non avviare due istanze Telegram. GGUF e account non inclusi, dipendenze esterne da predisporre. Nessuna migrazione dati eseguita. Tutti i precedenti archivi restano disponibili.

Windows10/i3-2100/HDD/audio/account/GGUF reali e consumi prolungati non provati.016 indice autonomo e023 causa timeout CI restano aperti. Abort nativo e remoto cooperativi/best effort; nessuna garanzia universale di assenza regressioni. Nessun test funzionale Linux. [Handoff](HANDOFF-JARVIS-007-20261107.md).
