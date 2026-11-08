# Gemma: risposta testuale rifiutata come JSON
Segnalazione: Gemma risponde alla domanda conversazionale «rispondimi al contesto» con un errore «GPT non ha restituito un JSON valido». Fonte009: poll_gemma_trial usa parse_conversation_intent per tutti i turni con allowed_actions impostato; il parser comune pretende JSON ed emette messaggi GPT. Il punto non prova assenza di memoria.
Correzione autorizzata e circoscritta: accettare testo libero come sola chat locale, mantenendo validazione stretta per ogni payload strutturato e ogni azione. Test callback reale, sessione reale, nessuna inferenza o account; output del modello controllato. Non intervenire qui su riassunti, budget o persistenza, che restano questioni distinte.
Fase Red: aggiunta tests/test_native_plain_reply.py prima di cambiare runtime. Verifica Windows da leggere. Nessun nuovo pacchetto o pubblicazione autorizzato da «Correggi»;009 immutabile.

## Correzione Gemma testo libero — 8 novembre 2026, candidata
Segnalazione: domanda conversazionale «rispondimi al contesto», modello Gemma, errore JSON che cita GPT. Riproduzione Windows run42445972822, fonte286d94d65f74d7f5c1fb7112b697a3d3e7e58d96:966 test,5 failure di asserzione,0 errori; due canali scartano la prosa e tre casi citano erroneamente GPT. La risposta grezza del PC utente non è stata acquisita: l’errore originario da solo non distingue testo libero da JSON troncato.
Correzione mirata: adapter parse_native_conversation_intent accetta soltanto prosa come chat; payload strutturati anche malformati restano al validatore comune. Nessuna riparazione JSON o esecuzione di testo; parser online invariato; errori locali etichettati Gemma. Callback reale conserva commit differito, epoch, isolamento e permessi. Riassunti/memoria post-riavvio/budget e timeout HUD precedente restano problemi distinti, non dichiarati risolti.
Candidata da verificare Windows3.11/3.12, nessun test Linux, nessun nuovo ZIP.009 pubblicata resta immutabile.

