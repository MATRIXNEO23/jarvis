# Piano — chat leggera stile Kobold dentro Jarvis (9 novembre 2026)

Richieste dell'utente (conversazione vocale con Claude, 9/11). Base: ramo F5 dopo chiusura F5N.4. Nessuna modifica a main, ZIP014, dati o memoria esistenti. Test solo Windows CI, un passo alla volta, build solo su richiesta.

## Stato del codice verificato (sola lettura, HEAD 9484d35)
- Comandi: motore locale già davanti al modello; `program_apps/service.py` accetta già apri/aprimi/avvia/avviami/lancia NOME + comando personalizzato. **Nessuna modifica prevista.**
- Catalogo azioni Gemma: `conversation_router.build_native_intent_context`, 652 caratteri / 12 azioni base (~220 token) + add-on. Oggi viene allegato a tutto ciò che NON è chiaramente informativo.
- Generazione: `native_bridge.py` passa a `koboldcpp.generate` solo prompt, contesto, max_output, temperature, top_k, top_p, seed, stop fisso Gemma. Nessuna grammatica, rep_pen, min_p.
- Impostazioni: `NativeModelConfig` (threads, batch_threads, context 2048, max_output 128, temp, top_k, top_p, seed, personality).
- Memoria: cronologia ≤250 token (128–600), Second Brain `prompt_context` ≤1100 caratteri, `workspace_memory` già con FTS5. Diagnostica prompt F3 misura il peso reale.
- Sessioni: archivio F1/F2 `jarvis_chat_sessions.sqlite3`; pallini HUD (`hud_orbits.py`) mostrano progetti e Telegram.

## Passi (ognuno: test RED→GREEN Windows, checkpoint, rollback = revert del commit)
1. **Catalogo solo quando serve.** Allegare il catalogo solo se la frase contiene un verbo d'azione o un nome noto (filtro testuale, stdlib); altrimenti chat semplice. Riduce il prompt nelle domande normali. Comandi esatti invariati.
2. **Comando in JSON vincolato.** Passare a KoboldCpp una grammatica GBNF solo nei turni con catalogo: risolve il JSON incompleto. Prima verificare che il `koboldcpp.py` fissato accetti `grammar` nella DLL in uso.
3. **Stile di risposta.** Impostazione «massimo N frasi» (1–10, predefinito Breve=2, Bilanciato=4) + campo personalizzato. Istruzione di una riga; max_output resta rete di sicurezza.
4. **Impostazioni a due livelli dalla chat.** Base: modello, contesto, max output, temperatura, stile. Avanzate (chiuse): top-p, top-k, min-p, rep_pen, seed, threads. Salvate per sessione.
5. **Memoria a tre strati.** (a) memoria fissa ≤100 token modificabile; (b) schede a parola chiave (stile World Info) inserite solo se la parola compare; (c) archivio FTS5 esistente interrogato solo su richiesta di ricordo. *Recupero da definire meglio con l'utente.*
6. **Sessioni nei pallini HUD** al posto dei progetti (progetti restano accessibili dal menu, nessun dato migrato o cancellato).

## Misura
Ogni passo che tocca il prompt riporta prima/dopo dalla Diagnostica prompt F3 (token). Velocità reale solo sul Pavilion.

## Dubbi aperti
- Recupero ricordi vecchi (passo 5c): quando e quanti frammenti.
- Coordinamento con Codex: stesso ramo F5, evitare modifiche concorrenti agli stessi file.
