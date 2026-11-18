# Prove Lumi 058 (bb42836)
1. HP/approfondisci/si: KO/non verificabile. Nessun servizio online spuntato; "chi ha scritto Harry Potter?" senza risposta ne' riga di salto (contesto 0 scambi); "approfondisci" -> "Cosa vuoi approfondire?"; "si" -> "A quale domanda ti riferisci?". Nessun motivo Gemini (ultimo_errore null).
2. Meteo: completo, settimana, stasera, ombrello, buongiorno Lumi: tutti ok, risposta da comando meteo (San Vendemiano).
3. cambia modello: caselle 1,2,3 ok; "2" -> "gia' in uso", nessun caricamento. Arch qwen3, CtxLimit 209/1024.
4. lumi_online: "ChatGPT dal browser" (account) distinto da "GPT con chiave (OpenAI API)": ok. ultimo_errore presente (null) su tutti.
5. Log motore: CtxLimit 209/1024; KV cache 1280 celle (140 MiB), profilo ampio = 1024: non coincide.
6. lumi_impostazioni: nessuna pagina "GPT dal browser" separata: ok.
