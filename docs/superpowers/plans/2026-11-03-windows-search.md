# Windows search corrections Implementation Plan

> **For agentic workers:** Execute this plan task-by-task using the user's authorized project workflow. If available and appropriate, use subagent-driven-development or executing-plans. Never assume an unavailable skill is installed. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ricercare il nome richiesto nelle aree consentite, riusando Windows Search prima della scansione diretta e mantenendo i risultati utilizzabili nel dialogo.

**Architecture:** Riusare parse_command, _search_impl, indexed_candidates, policy e UI esistenti. Modifiche mirate e separate: grammatica della richiesta, poi ordine dei provider. Nessun nuovo indice, framework o processo residente.

**Tech Stack:** Python 3.11/3.12, Windows 10 x64, PowerShell, SYSTEMINDEX, unittest e CI windows-2022.

**Spec:** docs/VERIFICA-RICERCA-WINDOWS-20261103.md, docs/INDICE-WINDOWS-PRIORITA-20261102.md, requisiti correnti AGENTS.md.

## Global Constraints

- Zero costi aggiuntivi e nessuna API a consumo.
- Test funzionali esclusivamente Windows; editing Linux non è test dell'app.
- Conservare impostazioni, dati, ZIP e cronologia. Nessuna nuova build senza richiesta esplicita.
- Solo radici consentite e policy corrente; revoca e annullamento scartano risultati.
- Minecraft è un esempio: niente nomi o percorsi specifici nel runtime.
- Aprire cartelle in Explorer è esistente; aprire documenti nel programma associato resta una scelta da chiarire, non implementata qui.

## Review Focus

- Nomi letterali tra virgolette e parole che iniziano per di: non corrompere i nomi.
- Radice iniziale grande e risultato indicizzato in radice successiva: interrogare entrambe prima del fallback.
- Indice positivo ma con copertura incompleta: non dichiarare scansione completa del disco.
- Cancellazione o revoca durante il provider: nessuna esposizione di risultati vecchi.
- Cartelle installazione: la nota delle fonti Windows non deve nascondere la fase indice.

### Task 1: grammatica del nome cercato

**Files:** file_access/service.py; tests/test_file_search_phrase.py esistente.

**Interfaces:** parse_command(text) produce ('search', {'query': nome, 'scope': eventuale ambito}) senza cambiare la semantica di locate/open/read.

- [x] Red: letti i log della run Windows 41604955975/source e714e4d: 494 test, quattro failure sui tre nuovi test; query catturata 'di Minecraft', non problemi di import o fixture.
- [x] Modifica minima: eliminare solo la preposizione iniziale di dalle richieste search dopo l'estrazione dello scope; nomi quotati preservati.
- [x] Green: run41606786155, 494 test per Python3.11/3.12 PASS. Comando: python -m unittest discover -s tests -v su CI Windows; zero failure/errori, incluse varianti/scopo/ricerca su filesystem temporaneo.
- [x] Review indipendente mirata: nessun blocco statico; evidenza CI letta. Checkpoint remoto in questo commit.

### Task 2: indice prima delle scansioni

**Files:** file_access/service.py; nuovi casi comportamentali in tests/test_file_index_priority.py.

**Interfaces:** indexed_candidates(query, root) resta compatibile (paths, note); _search_impl usa lo stesso provider sostituibile nelle prove e la policy finale. coverage registra quante radici sono state interrogate e se i risultati provengono solo dall'indice o dal fallback.

- [ ] Red Windows: due radici reali, risultato nella seconda, budget scansione minimo; dimostrare indice saltato. Prova positiva con os.scandir proibito; revoca/cancel e nota locate separati.
- [ ] Correzione minima: fase indice per tutte le radici autorizzate prima di qualunque scansione. Se ci sono risultati utili, mostrarli dichiarando copertura indice non necessariamente completa; se nessuno, fallback finito esistente. Conservare note provider, policy, deduplica e 20 risultati.
- [ ] Green Windows dei casi mirati e suite, più probe nativo esistente; nessuna installazione o modifica dell'indice sul PC utente.
- [ ] Review del diff esatto, checkpoint di codice/evidenze e documentazione, nessuna consegna ZIP implicita.

## Limiti e recupero

Non si promette di trovare elementi non indicizzati quando è stato usato soltanto l'indice. Indice vuoto non prova assenza globale; il fallback mantiene limiti e li dichiara. Inventario completo di ogni programma, risoluzione automatica delle directory dati di qualunque launcher, apertura generale file/app e qualità di Vosk sono fuori da questi due fix. R02 contesto e R03 false conferme restano nelle priorità della review. Recupero non distruttivo dalla storia del ramo, base b936879 e ZIP d06e233 preservati.
