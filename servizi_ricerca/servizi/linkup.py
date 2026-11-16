"""Linkup: ricerca web con risposta e fonti. Voce predisposta: chiave e link, ricerca non ancora collegata."""
from servizi_ricerca.base import Ricerca

SERVIZIO = Ricerca(
    id="linkup", nome="Linkup", ordine=4, chiavi="https://app.linkup.so",
    limite="Crediti gratuiti iniziali.",
    passi=("Apri app.linkup.so e accedi.", "Copia la chiave API dalla pagina principale.",
           "Incollala in Lumi con «Chiave…»."))
