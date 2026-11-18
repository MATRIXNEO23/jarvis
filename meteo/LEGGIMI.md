# Meteo (add-on)

Attivalo in Impostazioni > Add-on > Meteo e scegli la **città predefinita** (la prima volta).

- A voce o scritto: «che tempo fa a Roma», «meteo Milano», «che tempo fa» (città predefinita), «meteo domani» e «meteo domani a Roma» (minima, massima e cielo di domani). Risponde a voce e in chat per qualsiasi città. Nessun modello, nessuna quota, nessuna conferma.
- 058: «meteo settimana» (riassunto a voce, 7 giorni nella finestra dei risultati); giorno preciso («che tempo farà sabato», «meteo weekend»); «meteo stasera/stanotte/domattina»; «temperatura adesso», «vento», «umidità», «alba e tramonto»; «pioverà domani?», «serve l'ombrello?», «fa freddo?»; «buongiorno Lumi» / «com'è la giornata»; «meteo completo» / «dettagli meteo» (anche «a <città>»).
- 059: qualsiasi giorno entro 16 giorni e qualsiasi città, anche insieme: «meteo giovedì a Roma», «meteo il 25», «meteo il 25 dicembre», «meteo tra 3 giorni», «meteo tra una settimana», «meteo dopodomani a Milano». Oltre i 16 giorni Lumi lo dice. Ogni previsione include la probabilità di pioggia. La finestra dei risultati ha colonne proprie (Giorno, Cielo, Minima, Massima, Pioggia %).
- Non è meteo: «cerca online meteo …» (ricerca) e le domande sul «clima» («com'è il clima a Tokyo in primavera»).
- HUD: sotto il globo, sopra Disco C e Rete, un'icona (sole, nuvola, pioggia, neve, temporale) con città e temperatura, senza riquadro. Aggiornamento all'avvio e al massimo ogni 30 minuti, senza polling continuo.
- Add-on disattivato: niente icona, niente comando, nessuna connessione.
- Dati: Open-Meteo (geocoding e previsioni), gratuiti e senza chiave, con urllib della libreria standard. Nessuna dipendenza da installare.
- Impostazioni: `addon-data/meteo/config.json` nel profilo dati. Per tornare indietro basta cancellarlo o disattivare l'add-on.
- Prova: `tests/test_056_meteo.py`.
