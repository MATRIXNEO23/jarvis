# Piano: dividere jarvis.py in moduli per argomento (12/11/2026)

Stato: **piano approvato dall'utente come direzione** («dividere così rende più facile correggere senza migliaia di righe»). Codice non ancora toccato; ogni passo parte solo col via dell'utente, build solo su richiesta.

## Audit (commit di riferimento: build 042, 7a23f1b + note)
- 5.457 righe; ~95 di import/intestazione; **5.361 dentro `main()`** con 140 funzioni annidate e ~1.050 righe di costruzione UI.
- Righe delle funzioni annidate per argomento: ciclo eventi/console 1.120 (`poll` da sola 763), documenti/progetti 690, modello locale 550, Telegram 500, GPT 360, diagnostica 280, impostazioni/UI 250, voce/microfono 210, timer/file/programmi 160, memoria 120, comandi Lumi 60.
- Le funzioni condividono variabili di `main()` (root, write_line, variabili Tk, servizi): non si possono spostare senza un contesto comune.
- 23 file di test estraggono funzioni dal testo di `jarvis.py`: vanno adattati nello stesso passo in cui la funzione si sposta (regola già nota: non aggiungere nomi nuovi nelle funzioni estratte).

## Obiettivo
`jarvis.py` di poche centinaia di righe che avvia Lumi e collega i moduli; nessun cambiamento di comportamento. Ogni modulo ha un nome chiaro e test propri.

## Passi (uno per build, ciascuno con CI Windows e prova sul Pavilion)
1. **Contesto comune** (`lumi_contesto.py`): oggetto con root, console (`write_line`), voce (`speak_result`), impostazioni e servizi; `main()` lo crea e lo passa. Nessuna funzione spostata ancora.
2. **Telegram** → `telegram_addon/` (~500 righe).
3. **Modello locale** → `local_model/` (~550 righe): anche primo passo per KoboldCpp come add-on separato.
4. **`poll`** spezzato in gestori per tipo di evento (microfono, modelli, Telegram, diagnostica).
5. **Documenti e progetti, GPT, diagnostica**, poi il resto della UI.

## Regole per ogni passo
- Spostare, non riscrivere: stesso codice, stesse frasi, stessi tasti.
- Test estratti adattati insieme al codice; suite Windows completa verde prima della build.
- Se un passo rompe qualcosa, si torna alla build precedente e si registra causa e lezione qui.
