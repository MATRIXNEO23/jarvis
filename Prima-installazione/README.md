# Prima installazione di Lumi (build di prova 023 e successive)

Lumi è il nuovo nome di Jarvis. Guida per Windows 10 x64 (riferimento: HP Pavilion i3-2100, 10 GB RAM). Il pacchetto si scarica da [Download](../Download/README.md): prendi la build più alta in cima alla pagina.

## Passi, in ordine
1. **Python** 3.11 o 3.12 a 64 bit con Tcl/Tk e launcher `py` → [Requisiti](01-Requisiti.md). È l'unica installazione obbligatoria.
2. **Estrai lo ZIP** `Lumi-0xx-PROVA.zip` in una cartella NUOVA (per esempio Documenti\Lumi-023). Non avviare dallo ZIP e non sovrascrivere la cartella di una build precedente.
3. **Modello locale (GGUF)**: Lumi include già il motore (KoboldCpp, cartella `native_engine`) ma non il modello. Serve un file `.gguf` istruito: Gemma 2 2B, Qwen2.5 (1.5B/3B) o Qwen3 (1.7B), quantizzazione Q4_K_M consigliata per il Pavilion. Mettilo in una cartella fissa.
4. **Avvia** `avvia_lumi.bat` (doppio clic). Usa il profilo dati `%LOCALAPPDATA%\Jarvis-Gemma-Trial`: impostazioni, chat e memoria restano da una build all'altra.
5. **Scegli il modello**: ingranaggio → GPT e memoria → «Configura Gemma locale...» → Sfoglia il file `.gguf` → Salva → **chiudi e riapri Lumi** (il modello si carica una sola volta per avvio). La famiglia (Gemma/Qwen) viene riconosciuta dal file.
6. **Voce che risponde**: ingranaggio → Voce → «Scarica Paola» o «Scarica Serena» → scegli la voce → «Prova voce». Il motore voce è già incluso, non serve installare nulla → [Voce](03-Voce.md).
7. Facoltativi, solo se li usi:
   - **Microfono** (riconoscimento offline): `installa_voce.bat` → [Voce](03-Voce.md).
   - **Voci Microsoft Edge** (online, gratuite): `installa_voce_edge.bat` → [Voce](03-Voce.md).
   - **Telegram**: `installa_telegram.bat`, poi configurazione → [Telegram](04-Telegram.md).
   - **GPT esterno** (account ChatGPT): Node.js + `installa_gpt.bat` → [GPT](02-GPT.md).

Se qualcosa non va: [Componenti mancanti](07-Componenti-mancanti.md). Per reinstallare senza perdere dati: [Reinstallazione e dati](06-Reinstallazione-e-dati.md).

## Dove si trovano le cose (build 023)
| Elemento | Dove |
|---|---|
| Programma | Cartella dove hai estratto lo ZIP |
| Dati (impostazioni, chat, memoria, accesso Telegram) | `%LOCALAPPDATA%\Jarvis-Gemma-Trial` |
| Voci Paola/Serena scaricate | `%LOCALAPPDATA%\Jarvis-Gemma-Trial\voci` |
| Motore del modello e motore voce | `native_engine` e `voce_engine` nella cartella del programma |
| SDK e account GPT | `%LOCALAPPDATA%\Jarvis\runtime` e `gpt_account` |
| Modello microfono | `%LOCALAPPDATA%\Jarvis\models\vosk-model-small-it-0.22` |

Per aprire un percorso: Windows+R, incolla, Invio.

---
## Storico (versioni Jarvis precedenti)
> **007:** [consegna e istruzioni](../docs/CONSEGNA-JARVIS-007-20261107.md). Cartella nuova, profilo Gemma-Trial conservato; guida con F1/aiuto. Sezioni successive storiche.

> **Candidata006:** segui [consegna e istruzioni](../docs/CONSEGNA-JARVIS-006-20261107.md) e [registro versioni](../Download/REGISTRO-VERSIONI.md). Usa una cartella nuova; il profilo e quello Gemma-Trial. Le istruzioni sotto sono storiche, specifiche delle versioni indicate.

> **Prima scegli la versione:** [registro autorevole](../Download/REGISTRO-VERSIONI.md). Questa guida conserva istruzioni riferite alle versioni storiche indicate nelle sezioni. La candidata Gemma pubblicata e le correzioni audit in bozza sono riferimenti distinti; scaricare i sorgenti di main non equivale a un pacchetto operativo.

## Programmi e app — disponibile dalla004
[Guida del componente](Programmi-e-app.md) e [consegna Windows004](../docs/CONSEGNA-BUILD-004-20261103.md). Inclusa nella004 pubblicata; estrarre il pacchetto completo in cartella nuova. La guida storica sotto riguarda la base precedente; la003 non contiene l’add-on.

# Prima installazione di Jarvis
Guida aggiornata il 1 novembre 2026 per Windows 10 x64 e HP Pavilion i3-2100, 10 GB RAM. Il modello GPT è esterno; il PC esegue interfaccia, voce, memoria e azioni.

**Base di questa guida:** Jarvis-Timer-Audio-Fix2-20261031.zip, sorgenti esatti b936879a431370d206152be7b089baf587d15499, confermata funzionante dall'utente e verificata nell'audit. Download e checksum nel [registro](../Download/REGISTRO-VERSIONI.md). Le prime letture erano sul successivo 5e61e53: ora gli scostamenti sono distinti. Scaricare lo ZIP di main non equivale a scaricare questa base.

Istruzioni ricavate da codice e script; questa revisione non ha eseguito una nuova installazione sul Pavilion. I controlli applicativi nuovi elencati come «da implementare» non sono già disponibili.

## Se parti da zero
1. Leggi [Requisiti](01-Requisiti.md): installa Python e soltanto i componenti delle funzioni che userai.
2. Usa un pacchetto Jarvis identificato da versione/commit e verifiche. Estrai tutto in una cartella nuova, per esempio Documenti\Jarvis. Non avviare il programma dentro lo ZIP. In assenza di un pacchetto verificato non usare un vecchio link casuale come «ultima versione».
3. Nella cartella estratta devi trovare jarvis.py e gli script di installazione/avvio descritti qui. La presente cartella di istruzioni su main non contiene da sola l'app completa.
4. Per GPT segui [Collegamento GPT](02-GPT.md).
5. Per parlare al microfono e ascoltare le risposte segui [Voce](03-Voce.md).
6. Solo se lo desideri, configura [Telegram](04-Telegram.md).
7. Avvia avvia_jarvis.bat. Nel riferimento esaminato il launcher usa il profilo separato Jarvis-Telegram50-Trial. Nella base verificata il microfono può attivarsi all'avvio secondo auto_listen, inizialmente ON nel profilo Trial. Puoi scegliere Standby e cambiare la preferenza nelle impostazioni. Lo standby obbligatorio appartiene al ramo successivo, non a questo ZIP.
8. Apri l'ingranaggio: configura le funzioni richieste seguendo [Moduli e add-on](05-Moduli-e-addon.md). Fai una prova breve per volta. Un interruttore abilitato non dimostra che un account sia collegato.

Per reinstallare, prima leggi [Reinstallazione e dati](06-Reinstallazione-e-dati.md). Per un errore, leggi [Componenti mancanti](07-Componenti-mancanti.md).

## Dove si trovano le cose
| Elemento | Dove |
|---|---|
| Programma | Cartella dove hai estratto il pacchetto |
| Dati normali | %LOCALAPPDATA%\Jarvis |
| Dati del launcher di prova esaminato | %LOCALAPPDATA%\Jarvis-Telegram50-Trial |
| SDK GPT e account GPT condivisi | Sottocartelle runtime e gpt_account di %LOCALAPPDATA%\Jarvis |
| Modello voce normale | %LOCALAPPDATA%\Jarvis\models\vosk-model-small-it-0.22 |
| Progetti/documenti | Profilo attivo e percorsi scelti; alcuni documenti possono stare altrove |

Per aprire un percorso: premi Windows+R, incolla il percorso e premi Invio. Per vedere i percorsi effettivi puoi chiedere nella console «dove sono i tuoi file», se presente nel pacchetto corrispondente.

## Ordine e aggiornamento
Ogni nuovo modulo deve aggiornare questa cartella con requisiti, installazione, configurazione, prova ed errori. Le istruzioni tecniche di manutenzione sono in [Manutenzione](08-Manutenzione.md).
