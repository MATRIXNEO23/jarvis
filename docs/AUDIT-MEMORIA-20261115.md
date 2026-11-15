# Audit memoria (Second Brain) — 15/11/2026 sera

Richiesta utente (voce): una sola memoria letta in modo diverso da offline e online, categorie dei ricordi
(su di te, persone, progetti, cose da fare, altro, «Su Lumi» fissa in cima al prompt), pagina di ricerca
ordinata, «cosa ti ho detto prima» trovato nella cronologia, etichetta lavoro/chiacchiere scelta
dall'utente per ogni progetto, simboli 📡/🤖 prima del nome delle chat, frasi varie per «chi sei» /
«cosa puoi fare». Audit severo prima di toccare codice; riusare sistemi consolidati.

## Com'è oggi (letto nel codice)
- second_brain.py: sqlite con `conversations` (ogni scambio, tagliato a 320/350 caratteri),
  `action_receipts` (azioni verificate), `recent_dialogue` (ultimi 16). Salvato da regole fisse, non
  dal modello. Niente fatti, niente categorie.
- Ricerca: a ogni domanda legge fino a 1500 conversazioni + 3000 ricevute e conta parole in comune in
  Python; nessun indice. Cresce lineare con l'uso; trova per parole uguali, non per significato.
- preference_voice.py: «ricordati che…» accetta solo 10 preferenze fisse (lunghezza, lingua, voce/testo);
  il resto → «non supportato».
- local_model/compact_context.py: riassunto = estratto deterministico, non scritto da Gemma.
- local_model/persona.py: blocco fisso del carattere già in cima al prompt (riuso cache KoboldCpp).
- Gemma riceve ~530 caratteri di memoria (jarvis.py, prompt_context budget 530).
=> Oggi Gemma NON scrive ricordi: il rischio «salva cose sbagliate» oggi non c'è.

## Sistema consolidato di riferimento
MemGPT/Letta (Apache-2.0): core memory (blocchi brevi sempre nel prompt: persona e utente), recall
memory (cronologia cercabile), archival memory (fatti con tag cercabili). Corrisponde alla richiesta:
«Su Lumi» + «Su di te» = core; chat = recall; categorie = archival. Indice: SQLite FTS5 con BM25,
dentro SQLite, nessuna installazione. Scartati: ricerca vettoriale/embedding (modello in più, RAM sul
Pavilion), Letta stesso (server, troppo pesante).

## Contro e rischi
1. Chi scrive i fatti. In Letta li scrive il modello: con Gemma piccolo = errori. Solo «ricordati che»
   = memoria quasi vuota. Proposta: Gemma mai; scrivono l'utente («ricordati che…» libero, pagina
   ricordi) e il modello online quando è in uso, ogni ricordo mostrato in chat con «salvato: … (di'
   «cancellalo»)». Da confermare.
2. Categorie: regole a parole chiave sbagliano. Chi scrive sceglie la categoria; Lumi la mostra.
3. Prompt di Gemma: core memory con tetto fisso (proposta 600 caratteri) e sempre uguale → resta in
   cache; ogni modifica costa una rilettura una volta sola.
4. FTS5 e italiano: niente radici («progetto»/«progetti») → ricerca per prefisso. FTS5 nel Python di
   Windows da verificare in CI; se manca resta la ricerca attuale.
5. «Cosa ti ho detto 5 turni fa / prima»: risposta diretta di Lumi dalla cronologia della chat
   (esatta, senza Gemma). «Prima di questo argomento» non si può riconoscere in modo affidabile: si
   mostrano gli ultimi scambi e si sceglie.
6. Lavoro/chiacchiere: serve definire cosa cambia (proposta: nei progetti «chiacchiere» niente fatti
   di progetto, solo su di te / persone / Lumi).
7. Dati esistenti intatti: tabella nuova accanto, niente migrazione distruttiva.

Stato: PROPOSTA, nessun codice. Attende conferma utente (punto 1 per primo).
