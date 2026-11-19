# Decisioni per la 056 (dall'utente, 17/11/2026, a voce e in chat)

Questo documento contiene solo quello che l'utente ha detto o approvato. Il resto è nella sezione «Da decidere» e non va implementato.
Stato: **approvato dall'utente il 17/11 alle 16:38 (punti A, B, C, C2, C3, D, E); implementato nella build 056.**

## A. Catena, modalità «Basso consumo» (quella normale)
1. **Motore dei comandi.** Se la frase è un comando, il motore lo esegue e non la passa a nessun modello.
2. **Modello offline.** Tutto quello che non è un comando va subito al modello offline, che risponde senza passaggi preliminari: niente classificatore e niente controlli col modello, per la velocità sul Pavilion.
3. **Online solo con il «sì».** Lumi va online solo se lo chiedi tu, e prima chiede sempre conferma a voce («Vado online?»). Rispondi sì o no senza dire «Lumi».
4. **Approfondisci.** Dopo una risposta, dici «approfondisci» oppure premi il pulsante «Approfondisci» sotto la risposta in chat. Lumi chiede conferma e manda la stessa domanda al primo servizio online della lista (Gemini, Groq, GPT…), nell'ordine scelto dall'utente.
5. **Regole fisse.** Né online né quota consumata senza il tuo «sì», tranne il meteo. I comandi non passano mai da un modello. Gli elenchi non si leggono mai a voce.

La 055 fa il contrario (prima l'online, poi il locale): va corretta. Non era una decisione dell'utente.

## B. Modalità «Veloce»
- Risponde direttamente il primo modello online della lista, senza chiedere conferma ogni volta.
- Il modello offline resta di riserva se manca la connessione.
- Si sceglie con un **interruttore a slide**, fatto bene, in alto a sinistra al posto della scritta «Interfaccia neurale», con «Basso consumo» da un lato e «Veloce» dall'altro.

## C. Meteo, comando del motore
- Il meteo è un comando del motore, come il timer: niente IA, niente quota, niente conferma.
- I dati vengono da **Open-Meteo** (gratuito, senza chiave), per qualsiasi città. È l'add-on Meteo (vedi C2).
- Le domande più complesse sul clima, tipo «com'è il clima a Tokyo in primavera», restano ricerche online.

## C2. Meteo come add-on, con icone nell'HUD (17/11, 16:40)
- Il meteo è un **add-on** (.jaddon, cartella propria, in Impostazioni > Add-on): attivo/disattivo e configurazione. La prima volta si sceglie la **città predefinita**.
- Nell'HUD **niente riquadro**: solo iconcine che cambiano (sole, nuvola, pioggia, ecc.) con la scritta della città e la temperatura, nello spazio vuoto sotto il globo e sopra Disco C e Rete.
- L'HUD mostra la città predefinita. Il meteo delle altre città che chiedi te lo dice a voce.
- Aggiornamento leggero: all'avvio e poi al massimo ogni 30 minuti, senza polling continuo. Con l'add-on disattivato non compare niente.

## C3. Risultati di ricerca
- «apri il 2» (o un altro numero) apre quel risultato nel browser predefinito, senza conferma perché non consuma quota.
- Cerca: resta Tavily Search, con conferma prima di andare online.

## D. Barra in alto
- Togliere «GPT ON». GPT sta solo dentro la tendina ONLINE, insieme agli altri.
- Nuova tendina **MODELLO** (offline), come le altre: le 3 caselle per cambiare modello al volo, senza passare dalle impostazioni. Accanto alla tendina c'è UN solo tastino on/off, che accende o spegne il modello offline (scelta 1 dell'utente, 16:24). In memoria resta un solo modello alla volta.

## E. Bug da correggere (prove della 055)
- Mistral risulta spuntato anche se l'utente aveva spento tutti i servizi online: controllare che la spunta si salvi.
- Con tutto spento, «chi ha scritto i Promessi sposi?» deve avere la risposta dall'offline. Nelle prove di Codex risulta NON PROVATO.

## Da decidere (NON implementare)
- **Navigazione autonoma** (prossime build). Obiettivo dell'utente: usare il PC senza mouse e tastiera, con Lumi che naviga, legge le pagine e scarica i file da sola. Da valutare: estensione di Chrome per Lumi oppure Playwright (gratuito, ma pesa sulla RAM; va avviato solo quando serve). Restano da definire anche «leggi il N» (il riassunto di una pagina intera è troppo pesante per l'offline sul Pavilion), i download e Tavily Extract.
- **Ricerche online** (Tavily, Exa, Firecrawl, Linkup): quando si usano le ricerche e quando i modelli online, quali frasi le attivano («cercami…», «ultime novità», «informazioni su…») e come si collegano all'«approfondisci» su un risultato. L'utente vuole definirle a parte, dopo.
- Fino ad allora la ricerca resta com'è, ma con conferma prima di andare online (regola A.5).

## Passi successivi (dopo l'approvazione)
1. Analisi del codice attuale: dove passa una richiesta (motore, catena, barra) e cosa cambiare.
2. Piano di prove, con una frase da dire per ogni decisione e il risultato atteso, da far eseguire a Codex.
3. Codice, test, CI e build 056.
