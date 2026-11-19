"""Riquadro dei comandi per modalità e tutorial brevi (passo 7, decisione 15/11 10:22).

- Il riquadro semitrasparente (striscia di controllo_pc/overlay) si aggiorna da solo dopo
  ogni comando del Controllo PC con i comandi della modalità del momento: griglia,
  video (Netflix, YouTube…), Esplora file, Blocco note, generale.
- Acceso all'inizio, con scritto come toglierlo («nascondi i comandi») e riaverlo
  («mostra i comandi»); la scelta resta salvata.
- Dopo USI_PRIMA_DI_CHIEDERE comandi Lumi chiede una volta se toglierlo (sì/no).
- Prima volta in una modalità: Lumi dice in breve cosa si può fare lì e chiede «Ti guido
  passo passo?»; con sì parte il tutorial guidato (PASSI): Lumi dice un comando, aspetta
  che tu lo faccia e passa al successivo («salta passo», «esci dal tutorial»).
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

    # --- tutorial guidato passo per passo (15/11, seconda parte) -----------------------
    guida: tuple | None = None          # (modalità, indice del passo)
    offerta: str | None = None          # modalità per cui Lumi ha chiesto «ti guido?»

    def avvia_guida(self, mode: str | None = None) -> str:
        mode = mode or self.offerta or "generale"
        self.offerta = None
        self.guida = (mode, 0)
        steps = PASSI.get(mode, PASSI["generale"])
        return ("Ti guido in %d passi. Di' «salta passo» per andare avanti o «esci dal "
                "tutorial» per smettere. Primo passo: %s" % (len(steps), steps[0][0]))

    def avanza(self, action: str | None) -> str | None:
        """Testo del passo successivo se l'azione è quella attesa, altrimenti None."""
        if self.guida is None:
            return None
        mode, index = self.guida
        steps = PASSI.get(mode, PASSI["generale"])
        if action not in steps[index][1]:
            return None
        return self._prossimo()

    def salta(self) -> str:
        if self.guida is None:
            return "Non c'è nessun tutorial in corso."
        return self._prossimo()

    def _prossimo(self) -> str:
        mode, index = self.guida
        steps = PASSI.get(mode, PASSI["generale"])
        index += 1
        if index >= len(steps):
            self.guida = None
            return "Bravo, tutorial finito! I comandi restano nel riquadro."
        self.guida = (mode, index)
        return "Bene. Passo %d: %s" % (index + 1, steps[index][0])

    def esci(self) -> str:
        was, self.guida = self.guida, None
        return "Tutorial chiuso." if was else "Non c'è nessun tutorial in corso."

    def dopo_comando(self, mode: str, *, show, speak, ask, action: str | None = None) -> None:
        """Dopo ogni comando del Controllo PC: riquadro, passo del tutorial guidato,
        offerta del tutorial la prima volta in una modalità, domanda sul riquadro una volta.
        ask(domanda, azione_sì, azione_no)."""
        if self.offerta is not None and self.guida is None:
            self.offerta = None          # domanda «ti guido?» lasciata cadere: niente insistenza
        if self.guida is not None:
            text = self.avanza(action)
            if text:
                speak(text)
        elif mode not in self.state["tutorial"]:
            self.state["tutorial"].append(mode)
            self.offerta = mode
            ask(TUTORIAL.get(mode, TUTORIAL["generale"])
                + " Ti guido passo passo? Di' sì o no.", "tutorial_yes", "tutorial_no")
        if self.riquadro:
            show(self.testo(mode))
            self.state["usi"] += 1
            if (self.state["usi"] >= USI_PRIMA_DI_CHIEDERE and not self.state["chiesto"]
                    and self.guida is None and self.offerta is None):
                self.state["chiesto"] = True
                ask(__import__("frasi_lumi").say("togli_riquadro"), "help_off", None)
        self._save()


# Passi del tutorial guidato: (cosa dire, azioni del Controllo PC che lo completano).
PASSI = {
    "video": [("di' «pausa».", ("media_pause",)), ("ora di' «play».", ("play",)),
              ("di' «mostra i numeri».", ("show_numbers",)),
              ("di' un numero, per esempio «il 2».", ("pick",)),
              ("per finire di' «home».", ("home",))],
    "griglia": [("di' il numero di una casella, per esempio «il 5».", ("grid_pick",)),
                ("di' «indietro» per tornare alla griglia più grande.", ("grid_back",)),
                ("di' «chiudi la griglia».", ("grid_close",))],
    "explorer": [("di' «mostra i numeri».", ("show_numbers",)),
                 ("di' un numero, per esempio «il 3».", ("pick",)),
                 ("di' «giù» per scendere di un file.", ("step",)),
                 ("di' «su di un livello».", ("nav",))],
    "notepad": [("di' «digita ciao».", ("type", "type_in")),
                ("di' «premi invio».", ("press", "open_selected"))],
    "generale": [("di' «mostra i numeri».", ("show_numbers",)),
                 ("di' «nascondi i numeri».", ("hide_numbers",))],
}
