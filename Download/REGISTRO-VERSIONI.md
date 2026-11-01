# Registro versioni e punti di ripristino Jarvis
Aggiornato il 2026-11-01. Questo è l'indice diretto per recuperare una versione senza analizzare tutta la cronologia o cercare artifact.

## Riferimento funzionante confermato
**Non ancora identificato con sufficiente precisione in questa sessione.**
L'utente riferisce un dialogo molto migliorato sul Pavilion, ma versione/ZIP/SHA installato non sono stati acquisiti. Non attribuire quel feedback a un pacchetto a caso.
La correzione nucleo a86c2c932af988b23916e8d4495025de5ee0a730 ha CI documentata (386 test per combinazione e smoke bridge), ma non ha un nuovo ZIP corrispondente pubblicato in questa fase. Non associarla ai pacchetti precedenti.

| Riferimento | Test automatici | Prova PC | ZIP corrispondente | Uso come ripristino |
|---|---|---|---|---|
| Nucleo a86c2c9; sorgenti evoluti 5e61e53 | Esiti registrati nell'handoff | Feedback positivo non ancora collegato a SHA esatto | Nessuno nuovo pubblicato qui | Sorgenti recuperabili, non pacchetto stabile PC certificato |
| ZIP già presenti sotto | Presenza verificata, prove da associare a ciascuna versione | Non ricostruire per supposizione | Presenti e versionati | Inventario storico, non promozione automatica a funzionante |

## Scheda obbligatoria per ogni punto di ripristino
Compilare una scheda compatta prima della promozione:
- ID leggibile/versione e data; stato: candidato, test automatici superati, collaudato sul PC nell'ambito indicato, oppure superato/non consigliato.
- Commit esatto dei sorgenti e riferimento immutabile recuperabile; nome/versione delle add-on.
- Percorso ZIP completo versionato in Download, commit che lo conserva, dimensione e SHA-256 del pacchetto. Il Git blob SHA è un identificatore diverso: non chiamarlo SHA-256.
- Link diretto nel README Download, verifica di download ed estrazione, contenuto/manifest del pacchetto, istruzioni di installazione e dipendenze/versioni.
- Test automatici: comando, ambiente, esito, commit e workflow; distinguere simulazioni da componenti reali.
- Prova dell'utente: data, pacchetto identificato, funzioni effettivamente provate, esito e limiti. «Funziona» non equivale a ogni funzione collaudata al cento per cento.
- Compatibilità del profilo/schema dati, backup privato necessario e procedura per tornare indietro senza perdere dati o usare database incompatibili. Nessuna credenziale o backup personale in repository.
- Motivo della scelta e link alla scheda decisione/errore, problemi noti e riferimento funzionante precedente.

Dopo il collaudo PC, aggiornare il puntatore in cima a questo file con il nome esatto. Non sovrascrivere lo ZIP di una versione funzionante con contenuti diversi. I rilasci nuovi usano nomi univoci, per esempio Jarvis-VERSIONE-SHA.zip.
Gli artifact CI sono prove o copie ausiliarie: il pacchetto di recupero deve essere conservato in Download nel repository, non soltanto in un artifact che può scadere. Conservare anche i sorgenti corrispondenti.

## Quando l'utente dice «riprendi da lì» o «torniamo a quella»
1. Aprire questo registro e la scheda identificata dal contesto. Se il riferimento è ambiguo, chiedere soltanto quale delle versioni nominate intende; non scegliere in silenzio.
2. Distinguere ripresa dello sviluppo da ripristino del programma sul PC. Individuare subito commit, ZIP e compatibilità dati dalla scheda.
3. Verificare presenza e integrità del pacchetto esatto; usare il riferimento immutabile se main si è spostato.
4. Per sviluppo: recuperare i sorgenti in un checkout/ramo separato o proporre un ripristino tracciato, conservando la cronologia. Nessun reset distruttivo o force-push implicito.
5. Per il PC: chiudere Jarvis, conservare profilo e pacchetto correnti, estrarre quello scelto in cartella separata e usare un profilo compatibile. Non cancellare dati né aprire un database nuovo con codice vecchio senza verifica.
6. Registrare l'operazione e le verifiche essenziali in piano/handoff. I test già documentati non vanno rifatti tutti senza un motivo; verificare soltanto integrità, ambiente cambiato e aspetti irrisolti.

La procedura consente recupero diretto dei riferimenti registrati. Richiede accesso al repository e file ancora conservati; non garantisce scritture mai completate o file rimossi. Nessun ripristino è stato eseguito creando questo registro.

## Inventario dei pacchetti già versionati
Fotografia del commit bb94afa1865fe0315021f783736be3cb77c4af84. Presenza, dimensioni e Git blob SHA verificati via API GitHub; non sono test di download, estrazione o funzionamento PC. I link fissati al commit evitano che un cambiamento di main confonda il riferimento.
| ZIP | Byte | Git blob SHA |
|---|---:|---|
| [Jarvis-AddOn-Registro-GPT-Test.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-AddOn-Registro-GPT-Test.zip) | 369432 | ea1fb192dc257be6defeae01ff3d39e905b776f3 |
| [Jarvis-Autodiagnosi-Ibrida-GPT.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Autodiagnosi-Ibrida-GPT.zip) | 313324 | d73a4bb98f75c5417e5af73afff9bf4eba49d0f9 |
| [Jarvis-Autodiagnosi-e-Miglioramenti.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Autodiagnosi-e-Miglioramenti.zip) | 300368 | 49b36bab7fe6522a749576909820c31c1268690f |
| [Jarvis-Contesto-e-Risposte-Brevi.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Contesto-e-Risposte-Brevi.zip) | 262463 | 14fa07cf4e3484fc4fb60f430b22bdd71584e965 |
| [Jarvis-Conversazione-Naturale.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Conversazione-Naturale.zip) | 290170 | b0d6ce6b042d35401646b7a68dc78a4eec27f8c8 |
| [Jarvis-Diagnostica-Runtime-GPT.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Diagnostica-Runtime-GPT.zip) | 330999 | a34d8a62bca7168fbf108c14025d8310273f068b |
| [Jarvis-Fix-Autodiagnosi-Vocale.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Fix-Autodiagnosi-Vocale.zip) | 304402 | f806bfe7f4680369c10d6721b57c4bdd87bea53b |
| [Jarvis-Fix-Diagnostica-Visibile.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Fix-Diagnostica-Visibile.zip) | 321915 | ad9c7b4a2b41229ccccd085d95739024eeb0a4f2 |
| [Jarvis-Full-Audit-Telegram50-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Full-Audit-Telegram50-20261031.zip) | 394717 | 68c0cd7e9b699c161fc5945453eb4984a3b7b559 |
| [Jarvis-Gestione-Progetti-e-Diagnostica.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Gestione-Progetti-e-Diagnostica.zip) | 256542 | bbe95ce13823042461b71068ba7b4f14e26e529d |
| [Jarvis-HUD-Riferimento-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-HUD-Riferimento-20261031.zip) | 394707 | 0c716780755ec9a4ae4b5f6bfa4c5e0db10755c2 |
| [Jarvis-Memoria-Affidabile.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Memoria-Affidabile.zip) | 282608 | 209b027df98c0177fa0af8465a33fd78a240cd02 |
| [Jarvis-Memoria-Automatica.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Memoria-Automatica.zip) | 234564 | 90ee4e0b5ebb850994d15fea757ad74e0244767d |
| [Jarvis-Progetti-Vocali-e-Salvataggio.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Progetti-Vocali-e-Salvataggio.zip) | 244349 | 16634118983f39d337ba6856b5fb9eb0892cb244 |
| [Jarvis-Recupero-Documenti.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Recupero-Documenti.zip) | 293782 | 84c550f6a45cf9d1f61702f3570f5c54e3ac119b |
| [Jarvis-Telegram-Contatti-Vocali-Test.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Telegram-Contatti-Vocali-Test.zip) | 345603 | 6d96e5bbd63f21b216a07895ea0d7099386b32e2 |
| [Jarvis-Timer-Audio-Corretto-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Corretto-20261031.zip) | 407889 | 5019a79d91b5fcbfe28fc9a65155c5fc47f25fb8 |
| [Jarvis-Timer-Audio-Fix2-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Audio-Fix2-20261031.zip) | 406653 | 6aa9e6f9eb040dc7390b4edb55c9ae175bd4e512 |
| [Jarvis-Timer-Impostazioni-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Impostazioni-20261031.zip) | 405091 | d6335a69325d02edf061603a2e4707ecf92e9c16 |
| [Jarvis-Timer-Vocale-20261031.zip](https://github.com/MATRIXNEO23/jarvis/raw/bb94afa1865fe0315021f783736be3cb77c4af84/Download/Jarvis-Timer-Vocale-20261031.zip) | 407868 | 5d10f8ab35cb6e31ccc89921b0aecefab760530c |

## Fonti rapide
[Handoff](../docs/HANDOFF-CODEX-ARCHIFY-20261031.md), [decisioni e lezioni](../docs/DECISIONI-E-LEZIONI.md), [stato attività](../docs/STATO-ATTIVITA.md), [sorgenti](../docs/INDICE-SORGENTI.md), [installazione e dati](../Prima-installazione/06-Reinstallazione-e-dati.md).
