# Prima installazione di Jarvis
Guida aggiornata il 1 novembre 2026 per Windows 10 x64 e HP Pavilion i3-2100, 10 GB RAM. Il modello GPT è esterno; il PC esegue interfaccia, voce, memoria e azioni.

**Riferimento di questa guida:** sorgenti evoluti 5e61e53fbb58ccb5d95b85671604cc5f365d6e04, ramo feature/timer-settings-ui-20261031. Sono codice di prova, non un nuovo pacchetto stabile pubblicato con questa guida. La radice del ramo main contiene anche sorgenti storici: scaricare main non equivale a ottenere l'app evoluta.

Istruzioni ricavate da codice e script; questa revisione non ha eseguito una nuova installazione sul Pavilion. I controlli applicativi nuovi elencati come «da implementare» non sono già disponibili.

## Se parti da zero
1. Leggi [Requisiti](01-Requisiti.md): installa Python e soltanto i componenti delle funzioni che userai.
2. Usa un pacchetto Jarvis identificato da versione/commit e verifiche. Estrai tutto in una cartella nuova, per esempio Documenti\Jarvis. Non avviare il programma dentro lo ZIP. In assenza di un pacchetto verificato non usare un vecchio link casuale come «ultima versione».
3. Nella cartella estratta devi trovare jarvis.py e gli script di installazione/avvio descritti qui. La presente cartella di istruzioni su main non contiene da sola l'app completa.
4. Per GPT segui [Collegamento GPT](02-GPT.md).
5. Per parlare al microfono e ascoltare le risposte segui [Voce](03-Voce.md).
6. Solo se lo desideri, configura [Telegram](04-Telegram.md).
7. Avvia avvia_jarvis.bat. Nel riferimento esaminato il launcher usa il profilo separato Jarvis-Telegram50-Trial. Il codice parte con microfono in standby: l'echo del vecchio launcher che dice «ON» è superato.
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
