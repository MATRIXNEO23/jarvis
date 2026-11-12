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
1. **[FATTO 12/11, CI Windows verde: 1296 test, run 43303116959]** **Contesto comune** (`lumi_contesto.py`): oggetto con root, console (`write_line`), voce (`speak_result`), impostazioni e servizi; `main()` lo crea e lo passa. Nessuna funzione spostata ancora.
2. **Telegram** → `telegram_addon/` (~500 righe).
3. **Modello locale** → `local_model/` (~550 righe): anche primo passo per KoboldCpp come add-on separato.
4. **`poll`** spezzato in gestori per tipo di evento (microfono, modelli, Telegram, diagnostica).
5. **Documenti e progetti, GPT, diagnostica**, poi il resto della UI.

## Regole per ogni passo
- Spostare, non riscrivere: stesso codice, stesse frasi, stessi tasti.
- Test estratti adattati insieme al codice; suite Windows completa verde prima della build.
- Se un passo rompe qualcosa, si torna alla build precedente e si registra causa e lezione qui.

## Registro dei passi
- Passo 1 (12/11): `lumi_contesto.py` (dataclass `Contesto`, `crea()`, `attuale()`); `main()` lo crea subito prima di `la_mia_voce.ON_LEARNED`, quando tutti i riferimenti esistono. Nessuna funzione spostata, nessun comportamento cambiato. Test: `tests/test_lumi_contesto.py` (anche controllo statico che i riferimenti siano definiti prima della creazione). Limite noto: il contesto conserva i riferimenti al momento della creazione; se in futuro un servizio viene sostituito durante l'esecuzione, il modulo spostato dovrà aggiornarlo nel contesto.
- Prossimo, passo 2 (Telegram): 23 funzioni, usano 31 nomi di main(); 8 file di test le estraggono da jarvis.py (test_activity_status, test_hud_quick_toggles, test_selected_conversation_model, test_telegram_multi_contacts, test_file_access, test_file_refinement, test_program_apps_integration, test_addon_lifecycle) e vanno adattati insieme.
- Passo 2a (12/11): 12 funzioni dell'interfaccia Telegram (~210 righe) spostate in `telegram_addon/lumi_ui.py` con il codice invariato: i nomi di main() che usano sono diventati `d.nome`, dove `d = lumi_contesto.Vivo(nome=lambda: nome, …)` legge sempre il valore attuale (stesso comportamento delle funzioni annidate, anche per variabili definite più avanti o cambiate dopo). main() riceve le funzioni con gli stessi nomi. jarvis.py: 5.457 → 5.248 righe. Test adattato: test_telegram_multi_contacts (controlla i pulsanti nel nuovo file). Nuovi test in test_lumi_contesto.
  Restano in jarvis.py (passo 2b): 5 funzioni che cambiano stato condiviso con `nonlocal` (save_telegram_contact_selection, open_telegram_contact_list, send_owner_telegram_voice, toggle_telegram_automatic, telegram_reconfigure) e 6 provate dai test direttamente su jarvis.py (set_telegram_gpt_session, ask_telegram_gpt, ask_telegram_reply, resolve_telegram_gpt_consent, maybe_queue_telegram_note, try_telegram_voice_send).
  Errore trovato dalla CI Windows (run 43307068875) prima di ogni build: `installa()` usava `locals()` dentro una dict comprehension, che in Python 3.11 ha un ambito proprio → KeyError all'avvio (Lumi non sarebbe partita; lo ha visto anche test_program_apps_integration, che avvia l'applicazione). Corretto salvando `locals()` prima. Lezione: verificare sempre con un test che avvii davvero il codice spostato.
  Verifica passo 2a: CI Windows verde (1298 test, run unit su 2691745); pacchetto e prova reale UIA verdi (run 43307884449). Nessuna build pubblicata.
- Passo A (12/11 sera, richiesta utente «passo passo finisci la build con i criteri definiti»): strumento `tools/sposta_funzioni.py` (stesso metodo del passo 2a, con controlli automatici). Sposta solo funzioni dirette di main() senza nonlocal/global, senza decoratori, non lette dai test su jarvis.py e senza nomi di main() nei valori predefiniti. Primo tentativo (59 funzioni) fallito in CI Windows: molti test estraggono funzioni da main() tramite helper senza scrivere «jarvis.py», quindi lo strumento non li vedeva (es. recent_memory_for_gpt, native_memory_request, snapshot_services_report). Annullato e rifatto considerando «fissata» ogni funzione nominata tra virgolette in un qualunque test: spostate 50 funzioni (~525 righe) in `lumi_parti/` (voce, documenti_progetti, modello_memoria, interfaccia). jarvis.py: 5.248 → 4.865 righe.
  Non spostabili senza cambiare i test o il codice (lista con `python tools/sposta_funzioni.py --analizza`): le funzioni lette dai test direttamente su jarvis.py (tra cui poll, send_console_input, submit_gpt, submit_gemma_voice…) e quelle con nonlocal (stato condiviso). Sono il lavoro dei passi successivi: adattare ogni test a leggere il nuovo modulo e trasformare lo stato condiviso in un oggetto; vanno fatti a piccoli gruppi con CI ogni volta.
  Verifica passo A: CI Windows verde su 4090b86 (unit, diagnostica servizi, Telegram, tokenizer). Build 043 dal commit successivo (solo numero di versione).
