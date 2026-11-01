# Verifica concreta della base Jarvis — 2026-11-01
**Esito:** identità e provenienza dello ZIP verificate, test inclusi superati, differenze dal ramo successivo accertate. Documentazione da allineare alla base corretta; nessuna modifica del programma o add-on nuova.

## Base funzionante identificata
L'utente conferma il primo ZIP nel catalogo Download come build attualmente usata e funzionante per il momento.
- Pacchetto: Jarvis-Timer-Audio-Fix2-20261031.zip.
- [Copia persistente immutabile](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Fix2-20261031.zip).
- Dimensione: 406653 byte.
- Git blob SHA-1: 6aa9e6f9eb040dc7390b4edb55c9ae175bd4e512.
- SHA-256: c37270265918c63ddb3a9cf6a2c0982d468dd1af83a1af330c5af1dfb20f9352.
- **Sorgenti esatti:** [b936879a431370d206152be7b089baf587d15499](https://github.com/MATRIXNEO23/jarvis/tree/b936879a431370d206152be7b089baf587d15499).

## Verifiche realmente eseguite
| Fase | Metodo | Esito |
|---|---|---|
| Acquisizione | Lettura ZIP reale dal repository, decodifica e hash sui byte | PASS, dimensione/blob coincidenti |
| Archivio | CRC, controllo percorsi prima dell'estrazione, collisioni Windows | PASS, 155 file |
| Provenienza | Git blob SHA-1 di ciascuno dei 155 file contro tree b936879, esclusi i vecchi ZIP non inclusi dal publisher | PASS, nessun file diverso/mancante/extra |
| Riproduzione | Ricreato ZIP separato con lo stesso algoritmo, ordine, date e compressione del workflow | PASS, identico byte per byte e stesso SHA-256 |
| Moduli richiesti | Verifica componenti richiesti dal publisher e analisi import locali/stdlib/terze parti | PASS per presenza; import facoltativi diretti Telethon, Vosk, sounddevice |
| Test dello ZIP estratto | python -m unittest discover -s tests -v; Linux, Python 3.12.14 | 373 test, OK, 5 Windows-only saltati; zero failure/error |
| Sintassi Python | python -m compileall -q . | PASS |
| Sintassi bridge | node --check gpt_bridge.mjs; Node v24.22.1 locale | PASS |
| Prove CI storiche | Letti log della pubblicazione e quattro job Windows/Linux, Python 3.11/3.12 | 373 test per job; Windows senza skip, Linux 5 skip |
| Corrispondenza CI | Confronto di tutti i file inclusi col merge CI 9988788284850d4b4beac3bff2b77fba5d2079d8 | PASS, tutti i 155 file identici |
| Diff ramo successivo | Confronto contro sorgenti 5e61e53 | Differenze reali: 10 file cambiati, 5 presenti solo nel ramo successivo |

Il confronto del publisher esclude i precedenti ZIP in Download, come previsto dal suo codice. Non considera mancanti pacchetti storici che non devono essere annidati nell'archivio.

## Provenienza confermata anche dai log
[Pubblicazione 41229495866](https://github.com/MATRIXNEO23/jarvis/actions/runs/41229495866), job 124620508446: SOURCE_COMMIT b936879..., FILES 155, ZIP_BYTES 406653 e SHA256 corrispondono alla copia scaricata.
[Test 41229501460](https://github.com/MATRIXNEO23/jarvis/actions/runs/41229501460): job 124620525560 Ubuntu/Python 3.11, 124620525712 Ubuntu/3.12, 124620525714 Windows/3.12, 124620525776 Windows/3.11. Anche step parser PowerShell Windows risulta superato.
Sono esecuzioni precedenti rilette, non nuovi job lanciati dall'audit. Il test CI usa il merge PR indicato sopra; il confronto prova corrispondenza dei file col pacchetto.

## Scostamenti importanti dimostrati
1. **Base utente e ramo più recente non coincidono.** Il pacchetto contiene il nucleo precedente da 373 test; non include conversation_context.py né tests/test_conversation_pipeline.py della successiva correzione a86c2c9. Non attribuire i 386 test successivi a questa ZIP o il miglioramento riferito a un codice che non contiene.
2. **Avvio microfono diverso.** Nel pacchetto b936879 il preparatore imposta auto_listen=True nel nuovo profilo/una tantum e jarvis.py:3620 attiva Conversazione GPT se la preferenza è attiva. Nel ramo a86c2c9/5e61e53 l'avvio è in standby. Il risultato è da codice e test: questo audit non ha aperto un microfono Windows.
3. **Le guide appena create descrivevano soprattutto il ramo successivo.** La specifica versione era indicata, ma come ingresso per la base confermata occorre rendere esplicito il doppio riferimento, soprattutto per microfono e memoria. Correggere la documentazione, senza modificare silenziosamente la base.
4. **La mappa Archify del nucleo a86c2c9 non è la mappa esatta di questa ZIP.** Usarla come riferimento successivo, non come prova dell'architettura installata.
5. **Nessun manifesto di versione interno dedicato nella ZIP.** La provenienza è ora provata esternamente da confronto dei 155 file e log. Per i pacchetti futuri prevedere manifest di versione; non riscrivere questa base per aggiungerlo.

File diversi rispetto al ramo 5e61e53: .github/workflows/gpt-smoke.yml, conversation_memory.py, conversation_router.py, jarvis.py, jarvis_persona.py, prepara_test_telegram50.py, second_brain.py, tests/test_second_brain.py, tests/test_telegram_trial_launcher.py, workspace_memory.py.
File presenti solo nel ramo successivo: AGENTS.md, conversation_context.py, docs/CORREZIONE-NUCLEO-DIALOGO-20261031.md, docs/DECISIONI-E-LEZIONI.md, tests/test_conversation_pipeline.py.

## Evidenze persistenti
- [Manifest dei 155 file e confronto ramo successivo](evidence/base-20261101/manifest.json)
- [Corrispondenza sorgenti b936879](evidence/base-20261101/provenance.json)
- [Log completo dei test locali](evidence/base-20261101/unittest.log)
- [Sintesi test e limiti](evidence/base-20261101/test-summary.json)
- [Sintassi](evidence/base-20261101/syntax.json)
- [Controlli pacchetto e riproduzione identica](evidence/base-20261101/package-checks.json)
- [Corrispondenza col merge CI](evidence/base-20261101/ci-source-match.json)
- [Estratti tecnici CI/pubblicazione](evidence/base-20261101/ci-evidence.json)

## Cosa resta fuori da questa prova
Non eseguiti nuovi login/inferenza GPT, Telegram reale, GUI/audio/microfono Windows, parser PowerShell locale, nuova installazione sul Pavilion o misure RAM/CPU. La CI storica e il riscontro dell'utente hanno ambiti distinti. Queste lacune non vengono segnate PASS né trasformate in difetti dimostrati.

## Punto di ripresa
Preservare questa ZIP e usare b936879 come base delle prossime aggiunte, come richiesto dall'utente. Il ramo 5e61e53 resta un candidato separato con modifiche da valutare, non un sostituto automatico.
L'audit non autorizza la nuova add-on: completare il progetto tecnico partendo dalla base verificata e presentare eventuali modifiche necessarie prima del codice. Correggere gli indici e le guide con questi fatti, chiudere l'handoff e fermarsi.
