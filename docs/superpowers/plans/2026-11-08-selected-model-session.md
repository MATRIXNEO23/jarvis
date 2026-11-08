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
