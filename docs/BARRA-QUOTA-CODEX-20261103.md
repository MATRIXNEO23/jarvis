# Barra quota Codex — progetto concordato, 3 novembre 2026

**Stato corrente:** implementazione autorizzata nel turno seguente. Prima fase di fattibilità verificata suWindows:9test per Python e probeRPC con0turni;quota personale non letta. [Rapporto e scelta necessaria](QUOTA-CODEX-FATTIBILITA-20261103.md). Nessuna barra o nuova build.
**Piano:** [passi di attuazione](superpowers/plans/2026-11-03-barra-quota-codex.md).
**Base:** candidata004/source a1b93f34ff25bd9a972ed971a432af4984366f28, ramo operativo build/jarvis-004; non usare la radice storica main come runtime.

## Obiettivo e comportamento concordato
Una barra compatta nello spazio superiore vicino a «Interfaccia neurale», coerente con il tema ciano:
- legge la quota alla connessione del relativo account;
- aggiorna automaticamente ogni60 secondi mentre Jarvis è aperto, il modulo è attivo e l’account corretto è collegato;
- un clic o Invio/Spazio sul controllo richiede l’aggiornamento immediato;
- mostra percentuale residua, prossimo ripristino e ora dell’ultima lettura riuscita;
- nel dettaglio mostra le finestre effettivamente ricevute, con durata, consumo/residuo e ripristino;
- segnala chiaramente dati assenti, vecchi o errore, senza inventare percentuali.

Non vengono eseguiti turni del modello per leggere la quota: nessun prompt, streamResponse, turn/start, acquisto o riscatto di crediti. Le conversazioni richieste dall’utente continuano ad avere il normale consumo. L’autenticazione può richiedere credenziali/token OAuth; questi non sono token di inferenza e non devono apparire nell’interfaccia o nei log.

## Fonte reale e vincolo di fattibilità
Codex documenta account/rateLimits/read e account/rateLimits/updated, con limitId, primary/secondary, usedPercent, windowDurationMins e resetsAt.
La004 usa invece sign-in-with-chatgpt-devkit fissato a0a36fefeb913055c8c7a1a29b63d82b96b2e841a: index.ts/types.ts non espongono quote; responses.ts ritorna solo text. gpt_bridge.mjs/gpt_client.py non trasportano quota.
Un provider Responses con OAuthSiwC non prova l’accesso ai servizi account Codex. Non trattare quotaSiwC,quotaCodex,token del singolo messaggio o header rate-limit API come valori equivalenti.

**Condizione prima dell’implementazione completa:** prova Windows in sola lettura di una fonte ufficiale con autenticazione compatibile e account identificato. Se la connessione attuale non basta, documentare il limite e la soluzione minima prima di aggiungere un runtime/login diverso. Nessun account personale va letto o registrato senza il normale consenso di collegamento.

## Presentazione
L’etichetta del bucket letto rimane visibile: quotaCodex soltanto se limitId=codex; un altro bucket non lo sostituisce silenziosamente.
Per codex, percentuale residua=100-usedPercent. Finestre mancanti restano mancanti: non supporre5ore/settimana. Se sono presenti più finestre, la barra principale usa quella con meno percentuale residua e ne indica la durata; il dettaglio mostra tutte le finestre di quel bucket.
Valori non finiti o fuori0–100 sono rifiutati, non corretti silenziosamente. Un reset passato non ricostruisce100%: avvia una nuova lettura quando consentita. Lo zero reale resta0%, distinto da dato assente.
Ultimo aggiornamento significa ultimo successo, non ora del clic. Tempo trascorso con clock monotono; orario/ripristino visualizzati nel fuso locale Windows. Dopo75s dall’ultimo successo, dato segnato «non aggiornato».
In aggiornamento conserva eventualmente il vecchio valore con l’etichetta «Aggiornamento…»; errore successivo conserva il valore soltanto come precedente/non aggiornato. Nessun valore vecchio di un altro account.
Tema ciano per dati validi, testo attenuato per assenza/disconnessione e indicazione ambra per dati vecchi/errore. Nessun annuncio vocale o allarme aggiunto.
Posizionamento nel header di animated_hud.py dopo la scritta e prima dei controlli MIC/GPT/MEMORIA: riduzione della larghezza del controllo e dettaglio accessibile se spazio stretto, senza coprire tasti o scritte. Verifica Tk a1024×768 e1280×720; DPI del Pavilion da collaudare.

## Aggiornamenti e concorrenza
Un solo timer e una sola lettura in corso per il modulo: niente richieste sovrapposte. Clic multipli durante il lavoro sono accorpati; non accodare una lettura per ogni clic.
Il timer60s decorre dalla fine dell’ultimo tentativo; il clic a riposo anticipa la scadenza e la riprogramma. Timeout finito10s; dopo errore nessun ciclo immediato di retry. UI sempre reattiva, worker esterno a Tk; risultati consegnati al poll già presente.
Una notifica ufficiale autenticata può aggiornare lo snapshot senza un’altra richiesta, se supportata dal provider scelto. Il timer resta il meccanismo base; nessun obbligo di processo sempre acceso per ricevere eventi.
Disconnessione, cambio account, disattivazione/rimozione add-on e chiusura annullano timer/pending e invalidano risultati tardivi con revisione/sessione. Non avviare login o GPT per aggiornare la barra.

## Organizzazione e compatibilità
Nuova funzione in add-on modulare .jaddon, come regola del progetto; cartella proposta codex_quota con provider.py (fonte), service.py (snapshot/timer), ui.py (barra/dettaglio), QuotaCodex.jaddon e LEGGIMI.md. Riutilizzare gestore,IPC GPT e header esistenti. Provider può restituire «non disponibile» senza import/installazioni pesanti.
Il gestore attuale richiede1–N azioni e whitelist core_action: un semplice manifest vuoto non è compatibile. L’eventuale azione fidata di sola lettura account.quota.read e binding addon.quota_codex.aggiorna devono essere verificati/testati come adattamento minimo, non spacciati per già esistenti. Timer/clic invocano il servizio direttamente,mai un’interpretazione del modello.
Installazione OFF e controllo Attivo/Disattivo nel gestore; barra disattivata senza traffico,poi aggiornamento su attivazione con account disponibile. Ripristino impostazioni riporta60s,senza cancellare credenziali o dati delle altre funzioni. Nessuna cache quota persistente necessaria; snapshot inRAM.
Nessun cambio al backend delle conversazioni per la sola telemetria. Nessuna dipendenza o runtime aggiuntivo scelto prima della prova di fattibilità. Sul Pavilion i3-2100/10GB/Windows10x64 misurare RAM/CPU aggiuntive e reattività; nessun numero garantito prima della misura.

## Prove richieste prima della consegna
Solo Windows/CI Windows. Intercettare i trasporti di inferenza e far fallire i test se il controllo quota li chiama; contare0 turni/token generati dal probe per costruzione. Le letture account sono chiamate di servizio,non valutazioni del modello.
Prove significative: snapshot0/100/più finestre,percentuali malformate,bucket diverso,reset passato,quota assente; timeout/errore e timestamp non falsato; timer60s,clic/raffiche,eventi senza doppioni; cambio account/disconnessione/revoca/chiusura durante lettura; layout/tastiera e nessun blocco Tk.
Prova autenticata personale eventualmente necessaria dopo i controlli riproducibili,senza prompt né credenziali nei log. Un test simulato non dimostra l’accesso alla quota dell’utente.
Aggiornare registro capacità,guide/installazione e selettore pacchetto; verificare lo ZIP estratto solo per una build esplicitamente richiesta. Conservare004,dati e impostazioni. Nessuna005 autorizzata dal solo progetto.

## Fonti e verifica iniziale
- [Codex App Server](https://learn.chatgpt.com/docs/app-server): account/rateLimits/read e notifiche; consultato3novembre2026.
- [Accounts and sessions SiwC](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions): gestione account e paginaUso.
- [Codex con provider SiwC](https://developers.openai.com/siwc/token-sharing-open-source/codex-app-server): configurazione inferenza,non prova di lettura quotaCodex.
- Sorgenti004 letti: gpt_bridge.mjs,gpt_client.py,installa_gpt.ps1,animated_hud.py,jarvis.py,addon_manager.py; SDK fissato index.ts/types.ts/responses.ts.

## Collaudo004 conservato
Riscontro utente: elenco popolato,appStore trovata,Prova avvio riuscita e «apri Netflix» a voce apreNetflix. Nomi difficili/frasi personali ancora da provare. Non avviare fix del catalogo dal primo riscontro poi rettificato.
