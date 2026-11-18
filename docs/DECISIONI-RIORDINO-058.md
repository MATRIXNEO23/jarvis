A1: PARZIALE (060) — LEGGIMI_PROVA_TELEGRAM_50.txt spostato in docs/; prepara_test_telegram50.py RESTA in radice (vedi domanda). Approvato — spostare fuori dal pacchetto (tools/, docs/), oppure eliminare se non serve a nulla (utente 05:48)
A2/A4/A5 (installatori): rimandati. L'utente (05:50) vuole un'installazione unica fatta bene: al primo avvio Lumi controlla i componenti mancanti e chiede solo quelli; quelli già installati non li richiede. Da progettare come voce a parte.
A3: FATTO (060) — approvato — togliere LEGGIMI-ACCESSO-FILE.txt dal pacchetto (verificare che nessun .bat/codice lo citi)
A6: alternativa — cartella documenti/ (document_recovery, document_execution, project_documents, document_language), senza unire
A7: FATTO (060) — approvato — unire chat_link + chat_ruoli + chat_stream in un file (stato STREAM unico)
A8: FATTO (060) — approvato — unire menu_modello + menu_ricerca + menu_modelli (riverificare test tendine 056c/057)
A9: RIMANDATO alla riprogettazione della memoria — DA FARE: ricordi + ricordi_ui + cancella_memoria (riordino/unione)
A10: FATTO (060) — approvato — unire dialogue_style+dialogue_focus e plan_runner+action_planner; ATTENZIONE: correggere tutti i richiami (conversation_router, jarvis_persona, planner_ui, __import__ stringa), test
A11: B — cartella voce/ con i 12 file voce (speech_activity, voice_style, preference_voice, voice_control, piper_voice, edge_voice, offline_tts, audio_player, adaptive_voice, desktop_dictation, project_voice, la_mia_voce), senza unire
A12: RIMANDATO al restyling — DA FARE: cartella hud/ con hud_orbits, hud_backdrop, hud_raster, hud_reference, barra_tasti, slide_modalita, network_telemetry, animated_hud
A13: FATTO (060) — approvato — unire finestra_adatta in window_chrome
A14: approvato — spostare gli 11 file telegram_* + configura_telegram nella cartella dell'add-on Telegram, PER ULTIMO, senza cambiare comportamento; attenzione ai 13 richiami di telegram_security. DOPO: audit riga per riga per snellirlo, con proposte all'utente
B: approvato a GRUPPI — build 1: sveglia+meteo+musica in addon/; poi una build ciascuno: programmi, accesso file, Controllo PC, modello locale, diagnostica, Telegram (ultimo). Ogni spostamento: prima elenco richiami, poi sposta, correggi, CI, build vera, prova dal vivo che l'add-on si carichi.
C1: lasciare «Mic» com'è, da definire nel restyling
C2: numeretto dei non letti accanto al simbolo Telegram (si azzera aprendo la chat) — con lo spostamento di Telegram. BUG da correggere SUBITO (prossima build): clic sul simbolo Telegram nella barra non apre più la chat Telegram (regressione 057)
C3: approvato — aggiungere probabilità di pioggia alla frase. In più (utente 06:10): meteo di QUALSIASI giorno e QUALSIASI luogo, anche combinati: «meteo giovedì a Roma», «meteo sabato», «meteo il 25», «meteo tra 3 giorni», «meteo dopodomani a Milano». Open-Meteo arriva a 16 giorni: oltre, dirlo chiaramente. Verificare cosa la 058 fa già e coprire i mancanti, con test.
C4: limite 120 caratteri per i comandi meteo: lasciare così

## Struttura finale approvata (utente 18/11 23:36, dopo la mappa Floorplan)
Le cartelle seguono il percorso di una richiesta. L'utente ha lasciato a Claude la scelta della struttura più funzionale e più facile da manutenere:
- ascolto/: microfono, dettatura, ingresso del testo
- comprensione/: motore dei comandi, catena, dialogo, orchestratore
- addon/<nome>/: sveglia, meteo, musica, controllo_pc (+ controllo_comune), program_apps, file_access, telegram (ultimo)
- modello/: oggi local_model/
- online/: GPT dal browser, servizi_online, servizi_ricerca
- uscita/: voce che parla (piper, edge, offline_tts, audio), chat, finestre e menu; l'HUD SOLO con il restyling
- memoria/: ricordi, second brain, documenti (con la riprogettazione della memoria)
- diagnostica/
- jarvis.py e avvia_lumi.bat restano nella radice.
Sostituisce: A6 (documenti/ → memoria/) e A11 (voce/ → divisa tra ascolto/ e uscita/). Le unioni A7, A8, A10 e A13 restano valide e si fanno dentro le nuove cartelle.
Ordine: file tolti dal pacchetto e unioni → online/ → comprensione/ → ascolto/ e uscita/ (senza HUD) → diagnostica/ → addon a gruppi → modello/ → memoria/ con la sua riprogettazione → HUD con il restyling. Un passo per build, ciascuno con l'elenco dei richiami, i test, la build e la prova dal vivo.

## Stato build 060 (passo 1 del riordino)
- A3 fatto: LEGGIMI-ACCESSO-FILE.txt in docs/ (nessun .bat né codice lo citava; solo tools/build_file_access.py, corretto).
- A7 fatto: chat_testo.py (ruoli + link + stream; STREAM unico). A8 fatto: menu_tendine.py. A10 fatto: dialogue.py e action_planner.py (con run_approved_plan). A13 fatto: finestra_adatta dentro window_chrome.py; wintypes caricato solo all'uso.
- Nessun file ponte. Richiami corretti: jarvis.py, selettore_chat.py, local_model/conversazione_lumi.py, lumi_parti/* (5), conversation_router, planner_ui, capability_registry, project_voice, jarvis_persona, prompt-audit.yml, 13 test, README, publish-audit-zip.yml.
- DOMANDA per l'utente (A1): avvia_lumi.bat lancia `py -3 prepara_test_telegram50.py` a ogni avvio (profilo isolato) e `tools/` è escluso dal pacchetto: spostarlo lì romperebbe l'avvio. Rimasto in radice. Scelte: (a) lasciarlo (consigliato, nessun rischio); (b) spostarlo in tools/ e togliere dall'avvio la preparazione del profilo isolato, cambiando il comportamento dell'avvio.
