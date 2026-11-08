# Selected model and session implementation plan

Goal: rispettare la scelta GPT/Gemma e il consenso di sessione senza cambiare esecutori.
Spec: docs/CORREZIONI-POST-008-20261108.md.
Architettura: riusare gpt_enabled, run_gpt, autorizzazioni revocabili e dispatcher esistenti. Nessuna nuova dipendenza o migrazione.

1. Instradamento: callback start_conversation_gpt costruisce il protocollo già usato dalla chat; send_console_input verifica GPT prima della configurazione locale. Test callback reali, stato disconnesso e nessun fallback.
2. Consenso: grant chat.conversation in RAM, riusato tra voce/chat solo mentre valido; reset su scelta Gemma/disconnessione esplicita, permessi ricontrollati. Conferma iniziale anche con allowed. Permessi altre funzioni separati.
3. Cambio modello: riconoscimento locale di formule complete con sinonimi, niente negazioni o menzioni. Stesso toggle, revoca risposte pendenti.
4. Telegram: distinguere selezione da connessione con stato leggibile, mantenere consenso specifico e nessun fallback silenzioso.
5. Help e regressioni Windows. Prompt e contesto Gemma esclusi fino all'avviso all'utente.

Verifica: Red Windows prima delle modifiche; suite Windows 3.11/3.12 dopo il fix. Nessun test funzionale Linux, build o pacchetto in questo incremento.

## Ultimo passo: formato e contesto Gemma
Avviso all'utente dato prima dell'analisi. Fonte effettivamente letta: LostRuins/koboldcpp, koboldcpp.py al pin 7e0eb2dc4a23f1a0fc42a7660ad43be7a4b9e759 (blob 7805cd49cd1f7a8f0101aba52721af7a771067af). generate riceve prompt e lo codifica direttamente in inputs.prompt UTF-8: non applica il template della chat HTTP. Fonti Google: https://ai.google.dev/gemma/docs/core/prompt-structure e https://developers.googleblog.com/introducing-gemma3/ confermano ruoli user/model, turni delimitati e stesso formato testuale Gemma2/3 IT. Non cambiare DLL, sampler, modello o dipendenze.
Difetti: cronologia testuale inglobata in un solo user; taglio per singoli messaggi produce possibili risposte orfane; adapter ricontrolla budget originale e rifiuta il budget esteso del catalogo. Decisione: riusare messages nel provider; serializzazione in una sola funzione, istruzioni nel primo user; coppie complete recenti prima dei ricordi archiviati; budget comprensivo dei delimitatori, override interno limitato alla finestra/margine già configurati. Nessuna promessa di prestazioni sul Pavilion o miglioramento semantico misurato senza collaudo reale. Aggiunta copertura PTT: stessa conversazione dopo gate e comandi locali.
Prove: nuove regressioni Windows prima della correzione, poi suite completa e revisione indipendente. Gli adapter controllati nelle prove conservano il prompt serializzato per verificare isolamento/budget senza fare inferenza su Linux.
