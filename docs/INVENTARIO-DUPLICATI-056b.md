# Inventario duplicati nelle impostazioni (056b, 17/11)

| Impostazione | Dove compariva | Dove resta |
|---|---|---|
| Configurazione del modello (thread, contesto, uscita, stile) | «Configura Gemma locale…» (finestra) + «Anteprima multimodello» (finestra, bozza non salvata) + profili | Impostazioni > Modelli > «Modelli offline», nella pagina (base native.json, un solo Salva, scrive anche nel profilo) |
| Memoria del prompt (token cronologia, messaggi recenti, sintesi) | «Configura memoria e inattività…» (finestra) | stessa pagina Modelli, dentro il profilo (profili.json `memoria`; il file letto resta memory.json) |
| Salva profilo | «Salva in questo profilo» + «Salva» della finestra | solo «Salva» della pagina |
| Autorizzazioni GPT per funzione | pulsante nel riquadro del modello | solo nel riquadro «Connessione ChatGPT» (Modelli) |
| Modello GGUF in uso | campo «Modello GGUF» + elenco/caselle | solo elenco e caselle (nel modulo resta un'etichetta) |
| Pagina add-on «Modello locale» | già ridotta nella 055 | resta solo Attivo/Disattivo e «Apri impostazioni modelli» |
| Titolo «Modello locale Gemma (sperimentale)», «Prova Gemma locale» ecc. | testi visibili | «Modelli offline», «modello offline» |
| Second Brain | accensione/cancellazione in Memoria | invariato (unico per tutti i modelli) |
| «Contesto del modello locale» (chat continua, ricordi) e «Memoria del prompt» | due punti vicini, scrivono file diversi (contesto_lumi / memory.json) | NON unificati: chiavi diverse, da decidere con l'utente |

File non cancellati: `local_model/multimodel_ui_f5.py`, `local_model/memory_ui.py` (importati da test e dal codice F5); non sono più raggiunti dalle impostazioni.
Test: `tests/test_056b_nessun_duplicato_impostazioni.py` (un solo pulsante per finestra, nessun titolo di riquadro ripetuto, registro menu senza voci doppie, pagina add-on con un solo pulsante).
