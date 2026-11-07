# Jarvis006 — consegna candidata, 7 novembre2026

[Scarica Jarvis-006.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-006.zip). Richiesta esplicita: «allora pubblicami la build in download». Nuova candidata pubblicata dopo le verifiche Windows. Non e un aggiornamento installato automaticamente sul PC.

- Source esatto `3e2cc05b0b08fdc5b47054b19593cf3151aff75a`; [sorgenti](https://github.com/MATRIXNEO23/jarvis/tree/3e2cc05b0b08fdc5b47054b19593cf3151aff75a), [workflow](https://github.com/MATRIXNEO23/jarvis/actions/runs/42384228753), tentativo1 del source finale.
- SHA256 `066c6f0cb0af78a9e064119d1a9a39a9317f7524456e14c1716555d9d08f103a`, 8134642 byte, 118 file; metadata [Download/Jarvis-006.json](../Download/Jarvis-006.json).
- Deriva dal runtime f9458557074b528d2a480c124f54e3efe7ff9e05; le sole nuove modifiche sono strumenti/workflow di build e documenti. Nessuna nuova funzionalita runtime o dipendenza residente.
- Numero006/next007,001–005 e tutte le ZIP storiche conservate. Main mantiene il runtime storico; il codice evoluto e fissato nel source sopra, non copiato in blocco su main.

## Contenuto e installazione

Correzioni a permessi GPT, separazione dei progetti, memoria locale, documenti, voce, concorrenza Gemma/add-on, timeout, HUD, impostazioni e risorse. Guide operative incluse. Nessun nuovo indice autonomo; causa del timeout intermittente CI ancora da chiarire.

Estrai in una cartella nuova, apri `Jarvis-Gemma` e usa soltanto `avvia_jarvis.bat`. Conserva la cartella precedente e i suoi dati. Il launcher mantiene `Jarvis-Gemma-Trial`, come le candidate Gemma precedenti; chi proviene da005 usa un diverso profilo rispetto ad AccessoFile-Trial. Nessuna migrazione/cancellazione di dati personali eseguita. Non avviare due istanze Telegram insieme. Il GGUF non e incluso; dipendenze Python/Node/Vosk/Telegram richiedono predisposizione secondo le funzioni usate. DLL CPU no-AVX2 inclusa con digest fissato. Guide operative voce/recupero/file/app incluse.

## Evidenze osservate

[
  {
    "job_id": 128438128625,
    "python": "3.11.9",
    "tests": 911,
    "seconds": 182.379,
    "failures": 0,
    "errors": 0,
    "skipped": 0,
    "conclusion": "success"
  },
  {
    "job_id": 128438128858,
    "python": "3.12.10",
    "tests": 911,
    "seconds": 138.055,
    "failures": 0,
    "errors": 0,
    "skipped": 0,
    "conclusion": "success"
  },
  {
    "job_id": 128439016715,
    "python": "3.12.10 extracted",
    "tests": 911,
    "seconds": 156.659,
    "failures": 0,
    "errors": 0,
    "skipped": 0,
    "conclusion": "success"
  }
]

Tutti i911 test dei sorgenti superati per Python3.11/3.12, sintassi/probe e Windows Search live3.12 con ripristino. Il package dipende da entrambi i job. La DLL viene recuperata da Git immutabile, con SHA256 `ac834f409855bd7e12a0f0c0ffc8601a663b036b2403d74af4b6b3d3afd49bba` e upstream fissato.

Build effettiva Windows: file Python/MJS/PS1 verificati immutati dopo il builder. Normalizzati solo metadati del contenitore ZIP; aggiunti VERSIONE.json e LEGGIMI-BUILD-006.txt. Due esecuzioni del builder con clock diverso producono la stessa006 dopo normalizzazione. Manifest completo per file, CRC, struttura, unico launcher, guide/link, DLL e parita dei contenuti col source verificati.

Estratto pulito: import e caricamento DLL, UI reale avviata/chiusa dal callback normale con servizi live OFF in un profilo temporaneo. Controllo negativo: lo stesso smoke con eccezione Tk iniettata e rifiutato; smoke positivo senza errori callback. Successivamente911 regressioni complete sui moduli operativi estratti con soli supporti tests/tools/.github/documenti aggiunti temporaneamente, NON distribuiti. Nessun modulo operativo copiato dal checkout per soddisfare la suite; hash runtime ricontrollati dopo i test. Questo distingue la suite sul runtime estratto dalla sola prova di un archivio senza fixture.

Review indipendente readonly del delta build: corretto il gate sulle eccezioni Tk e fissato Node22.12; ricontrollo senza blocchi. Primo dispatch42383621234/source dcd35a81919cd8fe98dcc7ac3e064418184ba96a annullato per rafforzare il gate prima della consegna; non presentato come test superato. Il secondo tentativo42383777615/source9c6061acc78f6c584232b86a135ed90fb9d605d8 ha911test verdi per job ma smoke package fallito: la fixture sostituiva tk.Tk con una funzione, incompatibile con isinstance in window_chrome. La fixture ora usa una sottoclasse; il gate non e stato allentato. Il source finale ha una nuova run, non un retry che nasconde failure. Nei911test rimangono avvisi Tk della fixture storica test_telegram_secret_dialog che patcha Tk con Mock; non sono conteggiati come failure dal runner. Lo smoke pulito della006 deve invece essere privo di errori callback. Nessun errore runtime dimostrato da tali avvisi.

[Evidenza release](evidence/jarvis-006-release-20261107.json), [verifica package](evidence/jarvis-006-package-20261107.json), [rapporto audit aggiornato](RAPPORTO-FINALE-AUDIT-CORREZIONI-20261107.md).

## Limiti e recupero

Restano016 (indice autonomo non implementato) e023 (causa del timeout PowerShell intermittente CI non identificata; assenza nell’ultima run non equivale a fix).022 verificato solo per i quattro grafi di fixture Tk riprodotti, non garanzia universale dell’app.

Non collaudati Windows10 fisico/i3-2100/HDD/Radeon, microfono e audio SAPI, account GPT/Telegram/Store reali, inferenza con GGUF reale e prestazioni prolungate. Abort C/OS e cancellazione remota restano cooperativi/best effort. Non sono stati effettuati test funzionali Linux. La candidata richiede il collaudo sul PC; non promette assenza di ogni regressione.

Per tornare indietro, chiudi006 e riapri la versione precedente conservata nella sua cartella. Non cancellare/configurare a mano i profili e non sovrascrivere database con copie di versioni diverse. Tutti gli archivi storici restano nel [registro](../Download/REGISTRO-VERSIONI.md).
