A1: approvato — spostare fuori dal pacchetto (tools/, docs/), oppure eliminare se non serve a nulla (utente 05:48)
A2/A4/A5 (installatori): rimandati. L'utente (05:50) vuole un'installazione unica fatta bene: al primo avvio Lumi controlla i componenti mancanti e chiede solo quelli; quelli già installati non li richiede. Da progettare come voce a parte.
A3: approvato — togliere LEGGIMI-ACCESSO-FILE.txt dal pacchetto (verificare che nessun .bat/codice lo citi)
A6: alternativa — cartella documenti/ (document_recovery, document_execution, project_documents, document_language), senza unire
A7: approvato — unire chat_link + chat_ruoli + chat_stream in un file (stato STREAM unico)
A8: approvato — unire menu_modello + menu_ricerca + menu_modelli (riverificare test tendine 056c/057)
A9: RIMANDATO alla riprogettazione della memoria — DA FARE: ricordi + ricordi_ui + cancella_memoria (riordino/unione)
A10: approvato — unire dialogue_style+dialogue_focus e plan_runner+action_planner; ATTENZIONE: correggere tutti i richiami (conversation_router, jarvis_persona, planner_ui, __import__ stringa), test
A11: B — cartella voce/ con i 12 file voce (speech_activity, voice_style, preference_voice, voice_control, piper_voice, edge_voice, offline_tts, audio_player, adaptive_voice, desktop_dictation, project_voice, la_mia_voce), senza unire
A12: RIMANDATO al restyling — DA FARE: cartella hud/ con hud_orbits, hud_backdrop, hud_raster, hud_reference, barra_tasti, slide_modalita, network_telemetry, animated_hud
A13: approvato — unire finestra_adatta in window_chrome
A14: approvato — spostare gli 11 file telegram_* + configura_telegram nella cartella dell'add-on Telegram, PER ULTIMO, senza cambiare comportamento; attenzione ai 13 richiami di telegram_security. DOPO: audit riga per riga per snellirlo, con proposte all'utente
B: approvato a GRUPPI — build 1: sveglia+meteo+musica in addon/; poi una build ciascuno: programmi, accesso file, Controllo PC, modello locale, diagnostica, Telegram (ultimo). Ogni spostamento: prima elenco richiami, poi sposta, correggi, CI, build vera, prova dal vivo che l'add-on si carichi.
C1: lasciare «Mic» com'è, da definire nel restyling
C2: numeretto dei non letti accanto al simbolo Telegram (si azzera aprendo la chat) — con lo spostamento di Telegram. BUG da correggere SUBITO (prossima build): clic sul simbolo Telegram nella barra non apre più la chat Telegram (regressione 057)
C3: approvato — aggiungere probabilità di pioggia alla frase. In più (utente 06:10): meteo di QUALSIASI giorno e QUALSIASI luogo, anche combinati: «meteo giovedì a Roma», «meteo sabato», «meteo il 25», «meteo tra 3 giorni», «meteo dopodomani a Milano». Open-Meteo arriva a 16 giorni: oltre, dirlo chiaramente. Verificare cosa la 058 fa già e coprire i mancanti, con test.
C4: limite 120 caratteri per i comandi meteo: lasciare così
