# Impostazioni non leggibili

La correzione018 è nei sorgenti in bozza; non è una nuova build installabile.
Quando il file esiste ma Jarvis non riesce a leggerlo, l'avvio resta prudente:
ascolto automatico e GPT spenti, avviso nella console. Non significa che un
file assente o una prima installazione abbiano gli stessi valori iniziali.

L'originale rimane intatto. I salvataggi delle preferenze vengono rifiutati
finché quel file è illeggibile: non vengono sostituiti dati recuperabili con
valori iniziali. Anche un errore di accesso richiede di risolvere l'accesso,
senza cancellare il file. Nessun recupero o reset automatico.

Per recuperare manualmente:

1. Chiudi Jarvis.
2. Fai una copia privata del file indicato nell'avviso. Conserva l'originale
   danneggiato e le eventuali copie temporanee; non caricarli su GitHub.
3. Ripristina un backup valido di `settings.json`, in formato JSON UTF-8.
   I valori di `gpt_enabled` e `auto_listen`, se presenti, devono essere
   `true` o `false`, senza virgolette.
4. Riavvia e controlla le spunte prima dell'uso. Cronologie, progetti e
   credenziali sono separati e non vanno cancellati per questa operazione.

Se non hai un backup valido e scegli esplicitamente di ricreare le preferenze,
conserva prima la copia privata dell'originale. Puoi creare manualmente un nuovo
`settings.json` con questi soli valori, lasciando spenti microfono automatico
e GPT al primo avvio della nuova configurazione:

```json
{"gpt_enabled": false, "auto_listen": false}
```

Questa è una nuova configurazione scelta da te, non il recupero delle vecchie
preferenze: le altre impostazioni torneranno ai valori iniziali e potrai
riconfigurarle. Il file precedente rimane nella copia privata. Non limitarti a
eliminare il file: se è assente, Jarvis conserva i valori di prima installazione
già esistenti, che prevedono GPT e ascolto automatico abilitati.

Percorso ordinario: `%LOCALAPPDATA%\Jarvis\settings.json`. Un launcher di prova
può usare un profilo separato tramite `JARVIS_TRIAL_HOME`: segui il percorso
mostrato nell'avviso e non sostituire il profilo dell'altra installazione.
