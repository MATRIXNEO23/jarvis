# Continuità Gemma — esecuzione M1 poi M2

Goal: non perdere l'ultimo scambio per un limite espresso nell'unità sbagliata; recuperarlo anche dopo riapertura quando Memoria è attiva.
Architecture: stesso owner nativo e tokenizer KoboldCpp; selezione limitata per coppie, estratti locali senza inferenza; successivamente recupero da archivi esistenti con ruoli originali.
Tech stack: Python standard library, SQLite, DLL KoboldCpp fissata, CI Windows 3.11/3.12.
Spec: docs/superpowers/specs/2026-11-08-context-dialogue-design.md.
Constraints: autorizzazione utente «Fai entrambi prima uno poi l'altro». Nessuna nuova build/ZIP; 010 immutabile. Nessun aumento automatico C/O, modello aggiuntivo o riassunto generativo. Controlli revision/stop/memoria/azioni invariati.
Review focus: conteggio con special token, budget finale, ruoli, antecedente recente, cancellazione e isolamento.

1. M1 RED: regressioni di sessione con contatore al confine; prova Windows nativa confronta tokenize_ids con prompt_tokens della generazione sullo stesso GGUF.
2. M1 GREEN: bridge/provider/adapter espongono contatore serializzato, selettore protegge ultima coppia e usa estratto pertinente se necessario. Nessuna domanda troncata. Conteggio finale, eccezione se contatore attivo fallisce.
3. Migrazione: preservare schema e numeri legacy; nuova politica usa budget fisico token e separa limite storico. Nessuna conversione silenziosa del vecchio campo: nuovo limite di storia esplicito nella politica, impostazione legacy conservata per rollback. UI e diagnostica dichiarano l'unità.
4. M1 verifica: suite Windows, confronto ABI, review indipendente; solo dopo risultato procedere a M2.
5. M2 RED: riapertura archivio, richiamo di dettaglio oltre i vecchi tagli, progetti separati, cancellazione, memoria disattiva.
6. M2 GREEN: retention recente limitata e recupero prima dei ricordi correlati, medesima selezione/budget M1. Preservare vecchi record e filtri. Non ricostruire testi già troncati.
7. M2 verifica: suite Windows, review; aggiornare stato/handoff/lezioni con SHA e prove effettive. Nessuna affermazione di prestazioni sul Pavilion senza collaudo.

## Esito
M1 completata e verificata prima di M2; entrambe concluse. Evidenze e limiti: docs/VERIFICA-CONTINUITA-GEMMA-20261108.md. Nessuna nuova build autorizzata o creata.
