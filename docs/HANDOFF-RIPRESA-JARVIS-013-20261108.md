# Handoff Jarvis013 — 8 novembre 2026

## Stato e arresto
Pubblicazione richiesta dall'utente e completata. Fermarsi dopo questa consegna; nuove modifiche o build richiedono nuova istruzione. Questo handoff supera come ingresso il precedente012, che conserva la storia e il problema Telegram ancora aperto.

## Consegna verificata
[Scarica Jarvis-013.zip](https://raw.githubusercontent.com/MATRIXNEO23/jarvis/main/Download/Jarvis-013.zip). Estrarre in cartella nuova, conservando012e il profilo. Launcher unico avvia_jarvis.bat, profilo Jarvis-Gemma-Trial preservato; GGUF personale non incluso.
- 8154995byte,121file manifest, SHA2561926bb5b65d98bb78d1c829cd9143b1e39773c8c14581f6f63a8d0d9454ed781.
- Pubblicazione main5037f77, registro latest13/next14.012e tutte le versioni precedenti conservate.
- Fonte ramo752bd84a1ac3c340c8bd8ba54a4bfaaedb455a95, checkout PR/pacchetto b9db9e0dc158b07f0c057cffa7b5c97a6f9ff974. Ramo audit/native-prompt-performance-20261108, PR59draft aperta, base fix/service-diagnostics-20261108. Main contiene catalogoDownload e sorgenti storici: nessun merge indiscriminato.
- Copia pubblica scaricata e verificata: hash, manifest completo, versione, dati correzione, indici e012immutata. [Evidenza persistente](evidence/jarvis013-public-verification-20261108.json).

## Modifica consegnata
Nel pannello Memoria e inattività: Token cronologia e ricordi Gemma250iniziali, intero128–600. Salva applica al prossimo invio senza reload; Valori iniziali richiede Salva. Il vecchio limite in caratteri mantiene significato/valore e schema memory.json. Nuovo budget in memory.native.json accanto al file legacy; nessuna migrazione/scrittura alla lettura, file nuovo assente usa250, file invalido dà errore. Scritture atomiche per file, non transazione fra entrambi: dopo erroreSalva correggere e ripetere.
Ultimo scambio protetto dall'estrattore già esistente; dati esclusi dal prompt non cancellati da RAM/archivio. Ricordi variabili nell'ultimo user prima della domanda per preservare prefisso; catalogo, validatori, ruoli, autorizzazioni, annullamenti, isolamento progetti/Telegram e scelta GPT/Gemma invariati. Nessun riassuntore generativo, dipendenza, processo o aumento automatico contesto. [Rapporto RED/GREEN e scelte](CORREZIONE-PROMPT-GEMMA-20261108.md).

## Prove e limiti
[Run42501645142](https://github.com/MATRIXNEO23/jarvis/actions/runs/42501645142)SUCCESS:1006test Windows/Python3.11(job128795473515),1006su3.12(job128795473544),1006sulloZIPestratto(job128796349677). DLL pinned, clean imports, avvio/chiusuraUI, rifiuto erroreTk iniettato, guide/manifest/parità sorgenti e riproducibilità verificati. Package non contiene test/tools/CI/handoff o dati personali; supporti di sviluppo aggiunti soltanto dopo accettazione pulita nella verifica. Publisher128797389351SUCCESS.
Prove native42501645119/42501645123SUCCESS; precedenti verifiche dettagliate e review indipendente nel rapporto. Esempio sintetico705→349token con due scambi recenti preservati; non è una promessa di stessa accelerazione sul Pavilion. Nessun test funzionale Linux, account/microfono reali o confronto105→30s sul PC.

## Prossimo passo
Solo collaudo dell'utente con013: stesse impostazioni modello/contesto/output, qualche scambio e tempo effettivo. Controllare il nuovo budget nel pannello. Per Telegram usare la diagnostica servizi già consegnata012e copiare il rapporto prima di riavviare: la causa sul suo account non è identificata né dichiarata risolta da013. Non chiedere credenziali/APIhash/sessioni.

## Persistenza e vincoli
Leggere AGENTS.md, questo handoff e STATO-ATTIVITA prima di riprendere. Conservare dati, impostazioni e controllo manuale microfono, zero costi aggiuntivi e versioni funzionanti. Gate una tantum di build/publisher spenti nel checkpoint finale con skipci; nessuna modifica runtime dopo le prove. Nessuna nuova attività o pubblicazione implicita da questo documento.
