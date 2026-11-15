"""Riquadro dei comandi per modalità e tutorial brevi (passo 7, decisione 15/11 10:22).

- Il riquadro semitrasparente (striscia di controllo_pc/overlay) si aggiorna da solo dopo
  ogni comando del Controllo PC con i comandi della modalità del momento: griglia,
  video (Netflix, YouTube…), Esplora file, Blocco note, generale.
- Acceso all'inizio, con scritto come toglierlo («nascondi i comandi») e riaverlo
  («mostra i comandi»); la scelta resta salvata.
- Dopo USI_PRIMA_DI_CHIEDERE comandi Lumi chiede una volta se toglierlo (sì/no).
- Prima volta in una modalità: Lumi dice in breve cosa si può fare lì (tutorial).
- Impostazioni: casella del riquadro e «Rivedi i tutorial».
Nessun controllo continuo: si aggiorna solo quando dai un comando.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

USI_PRIMA_DI_CHIEDERE = 20

NOMI = {"griglia": "Griglia del mouse", "video": "Video (Netflix, YouTube…)",
        "explorer": "Esplora file", "notepad": "Blocco note", "generale": "Finestra"}

COMANDI = {
    "griglia": ["«il 5»: entra nella casella", "«indietro»: griglia più grande",
                "«clicca»: clic al centro", "«tasto destro»", "«mouse a destra di poco»",
                "«ancora»", "«chiudi la griglia»"],
    "video": ["«pausa»", "«play»", "«indietro»", "«home»", "«scorri la riga a destra»",
              "«mostra i numeri» e poi «il 3»", "«schermo intero»", "«esci dallo schermo intero»"],
}

TUTORIAL = {
    "griglia": "Griglia: di' il numero della casella per avvicinarti, poi «clicca». "
               "«Indietro» torna alla griglia più grande.",
    "video": "Video: puoi dire «pausa», «play», «indietro» e «home». Per scegliere un "
             "titolo di' «mostra i numeri» e poi il numero.",
    "explorer": "Esplora file: di' «vai su Download», poi «mostra i numeri» e il numero per "
                "aprire. «Su di un livello» torna indietro.",
    "notepad": "Blocco note: di' «digita» e il testo, «premi invio», «premi Ctrl più S» per "
               "salvare.",
    "generale": "Per cliccare di' «mostra i numeri» e poi il numero, oppure «clicca su» e il "
                "nome del pulsante.",
}


def percorso() -> Path:
    from settings import default_path
    return default_path().parent / "aiuto_comandi.json"


class Aiuto:
    def __init__(self, path: Path | None = None, *, base_help=None):
        self.path = path
        self.base_help = base_help or {}       # controllo_pc.service._HELP
        self.state = {"riquadro": True, "usi": 0, "chiesto": False, "tutorial": []}
        try:
            data = json.loads(self._path().read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for key, default in self.state.items():
                    if isinstance(data.get(key), type(default)):
                        self.state[key] = data[key]
        except (OSError, ValueError, RuntimeError):
            pass

    def _path(self) -> Path:
        return Path(self.path) if self.path is not None else percorso()

    def _save(self) -> None:
        try:
            path = self._path()
            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_suffix(".tmp")
            temp.write_text(json.dumps(self.state), encoding="utf-8")
            os.replace(temp, path)
        except (OSError, RuntimeError):
            pass

    @property
    def riquadro(self) -> bool:
        return bool(self.state["riquadro"])

    def imposta_riquadro(self, on: bool) -> None:
        self.state["riquadro"] = bool(on)
        self._save()

    def rivedi_tutorial(self) -> None:
        self.state["tutorial"] = []
        self._save()

    def comandi(self, mode: str) -> list[str]:
        if mode in COMANDI:
            return COMANDI[mode]
        key = {"explorer": "explorer.exe", "notepad": "notepad.exe"}.get(mode, "")
        return list(self.base_help.get(key, self.base_help.get("", [])))

    def testo(self, mode: str) -> str:
        lines = ["Comandi: " + NOMI.get(mode, NOMI["generale"])]
        lines += ["• " + item for item in self.comandi(mode)]
        lines.append("«nascondi i comandi» per toglierlo, «mostra i comandi» per riaverlo")
        return "\n".join(lines)

    def dopo_comando(self, mode: str, *, show, speak, ask) -> None:
        """Dopo ogni comando del Controllo PC: riquadro, tutorial, domanda una volta."""
        if mode not in self.state["tutorial"]:
            self.state["tutorial"].append(mode)
            speak(TUTORIAL.get(mode, TUTORIAL["generale"]))
        if self.riquadro:
            show(self.testo(mode))
            self.state["usi"] += 1
            if self.state["usi"] >= USI_PRIMA_DI_CHIEDERE and not self.state["chiesto"]:
                self.state["chiesto"] = True
                ask("Vuoi che tolga il riquadro dei comandi? Di' sì o no. "
                    "Lo riaccendi quando vuoi con «mostra i comandi».")
        self._save()
