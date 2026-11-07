# JRV-AUD-002 — isolamento memoria breve Gemma

Goal: separare conversazione generale e progetti nella sessione Gemma, senza ricaricare il backend né modificare dati persistenti.
Base: 53717ebe42defdfed6ac7ae3a0e12418123e8c44, include la correzione001 verificata. Ramo002 distinto, PR dipendente dalla001; nessuna build/merge.

Architettura: un solo NativeConversationSession/backend; turni brevi etichettati dal progetto catturato al submit. Conservare il limite globale esistente di32 messaggi (16 scambi), evitando una cache illimitata per progetto. Proposta di risposta separata dal suo inserimento nella memoria: solo il poll UI accetta un turno con epoca e progetto ancora validi. Telegram e selettore programmi restano isolati dalla chat. Nessuna persistenza nuova: il recupero duraturo del dialogo nativo resta ID009.

Alternative: cancellare tutto al cambio progetto evita mescolanze ma perde il ricordo breve al ritorno; una sessione/backend per progetto consuma RAM e ricarica il modello. Scelta: turni partizionati nello stesso buffer globale limitato, commit sul thread UI.

- [ ] Riproduzione Windows dei callback reali: A→generale→B→A; risultato in coda revocato; cambio A→B→A durante generazione; contesto catturato prima di avviare il worker.
- [ ] NativeConversationSession: filtro per context_id, limite globale invariato, turno proposto con commit idempotente e lock breve separato dall'inferenza; API ask esistente compatibile.
- [ ] ChatTransport: selezione locale esplicita con contesto e risposta differita per la GUI. Nessun fallback remoto.
- [ ] jarvis.py: cattura progetto al submit, poll scarta prima del commit; follow-up app aggiornato solo dal risultato accettato.
- [ ] Verifica: callback scritti/vocali, riuso backend, memoria limitata e commit non bloccante durante altra inferenza; Telegram/picker non leggono né scrivono turni chat; archivi persistenti invariati.
- [ ] Review indipendente e suite completa Windows3.11/3.12. Nessun test funzionale Linux o collaudo account/modello reale.

Rischi: conservare un turno poi revocato; bloccare Tk aspettando il lock nativo; perdere il contesto nel passaggio GUI/trasporto; introdurre buffer non limitati. Recupero: ramo isolato e nessuna modifica al ramo distribuito/profili.
Stato: test di riproduzione preparati, runtime ancora invariato; attesa Red Windows.
