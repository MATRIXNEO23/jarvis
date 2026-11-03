Stato: Red osservato e correzione verificata in Windows. Runtime1265360/run41612658412;505 test per Python3.11/3.12. Rapporto: docs/CONTINUITA-R02-20261103.md. Nuove capacità differite; mantenere priorità contesto.

# R02 — domanda file pendente, 3 novembre 2026

Obiettivo: conservare il compito locale durante un chiarimento non riconosciuto, prima dell'interpretazione GPT. Nessun lavoro su nuove funzioni di ricerca/apertura.

1. Riprodurre su Windows con callback effettivo e dati temporanei: richiesta incompleta/scelta → parafrasi → prompt → risposta successiva. Verificare che non parta un'azione sulla sola parafrasi.
2. Solo dopo il Red, correggere il punto di reset per domande realmente pendenti e vive. Usare stato locale, revisione policy e scadenza; non aggiungere parole chiave come prova di cambio argomento. Conservare invalidazione dei lavori in corso e dei risultati senza domanda pendente.
3. Verificare Green, suite esistente Windows, annullamento, nuova richiesta, cambio progetto, scadenza, revoca e disattivazione. Nessun test Linux, account o microfono.
4. Salvare source/run/esito e limiti in handoff/stato/lezioni. Nessun ZIP o build.

Recupero: base 870fa27a68bc95c6e30944ecc93e144e454290e7; il primo checkpoint modifica solo test e documentazione. Le correzioni precedenti restano nel ramo; nessun dato personale interessato.
