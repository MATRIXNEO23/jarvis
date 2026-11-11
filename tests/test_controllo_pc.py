import tempfile
import unittest
from pathlib import Path

from controllo_pc.commands import parse_command, parse_keys
from controllo_pc.service import ControlService
from controllo_pc import runtime


class FakeBackend:
    def __init__(self):
        self.calls = []
        self.items = [
            {"hwnd": 11, "title": "Documento.txt - Blocco note", "process": "notepad.exe", "pid": 1},
            {"hwnd": 22, "title": "YouTube - Google Chrome", "process": "chrome.exe", "pid": 2},
            {"hwnd": 33, "title": "WhatsApp", "process": "WhatsApp.exe", "pid": 3}]

    def open_windows(self):
        return list(self.items)

    def focus(self, hwnd):
        self.calls.append(("focus", hwnd))
        return True

    def close(self, hwnd):
        self.calls.append(("close", hwnd))
        return True

    def click(self, x, y, visible=True, double=False):
        self.calls.append(("click", x, y))

    def type_text(self, text):
        self.calls.append(("type", text))

    def press(self, keys):
        self.calls.append(("press", tuple(keys)))
        return True

    def window_rect(self, hwnd):
        return (0, 0, 100, 100)

    def move_mouse(self, x, y, visible=True):
        self.calls.append(("move", x, y))

    def scroll(self, amount):
        self.calls.append(("scroll", amount))


ELEMENTS = {33: [{"name": "Cerca", "type": "Edit", "x": 10, "y": 20, "w": 100, "h": 20, "enabled": True},
                 {"name": "Invia", "type": "Button", "x": 300, "y": 400, "w": 40, "h": 20, "enabled": True}],
            11: [{"name": "File", "type": "MenuItem", "x": 0, "y": 0, "w": 30, "h": 20, "enabled": True}]}


def make(folder, enabled=True):
    backend = FakeBackend()
    service = ControlService(lambda: enabled, Path(folder), backend,
                             elements=lambda hwnd: ELEMENTS.get(hwnd, []), clock=lambda: 0)
    return service, backend


class CommandTests(unittest.TestCase):
    def test_phrases(self):
        self.assertEqual(parse_command("Lumi, che finestre sono aperte?"), ("list_windows", {}))
        self.assertEqual(parse_command("passa a Blocco note"), ("switch", {"window": "Blocco note"}))
        self.assertEqual(parse_command("vai alla 2"), ("switch", {"window": "2"}))
        self.assertEqual(parse_command("chiudi la finestra di Chrome"), ("close", {"window": "Chrome"}))
        self.assertEqual(parse_command("chiudi la finestra"), ("close", {"window": None}))
        self.assertEqual(parse_command("premi ctrl più c"), ("press", {"keys": ["ctrl", "c"]}))
        self.assertEqual(parse_command("premi Alt+F4"), ("press", {"keys": ["alt", "f4"]}))
        self.assertEqual(parse_command("premi il pulsante Invia")[0], "click")
        self.assertEqual(parse_command("clicca su Cerca")[1]["target"], "Cerca")
        self.assertEqual(parse_command("scrivi ciao mamma nel campo Cerca"),
                         ("type_in", {"text": "ciao mamma", "target": "Cerca"}))
        self.assertEqual(parse_command("scorri giù"), ("scroll", {"amount": -3}))
        self.assertEqual(parse_command("scorri su di 5"), ("scroll", {"amount": 5}))
        self.assertEqual(parse_command("chiama questa finestra lavoro"),
                         ("name_window", {"window": None, "name": "lavoro"}))
        self.assertIsNone(parse_command("metti Imagine"))
        self.assertIsNone(parse_keys("a"))


class ServiceTests(unittest.TestCase):
    def test_list_switch_by_number_name_and_nickname(self):
        with tempfile.TemporaryDirectory() as folder:
            service, backend = make(folder)
            self.assertIn("2. YouTube - Google Chrome", service.handle("list_windows", {}))
            self.assertIn("Passo a YouTube", service.handle("switch", {"window": "2"}))
            self.assertIn("Blocco note", service.handle("switch", {"window": "blocco note"}))
            # Frasi di altri comandi o finestre inesistenti: lasciate agli altri.
            self.assertIsNone(service.handle("switch", {"window": "GPT"}))
            self.assertIsNone(service.handle("switch", {"window": "Paint"}))
            self.assertIn("lavoro", service.handle("name_window", {"name": "lavoro", "window": "chrome"}))
            service2, _ = make(folder)                       # nome ricordato
            self.assertIn("YouTube", service2.handle("switch", {"window": "lavoro"}))
            self.assertIn("già un comando", service.set_nickname("GPT", backend.items[0]))

    def test_confirm_first_times_then_remember_but_delicate_always(self):
        with tempfile.TemporaryDirectory() as folder:
            service, backend = make(folder)
            for _ in range(2):
                self.assertIn("Di' «sì»", service.handle("close", {"window": "blocco note"}))
                self.assertIn("Chiudo", service.answer("sì"))
            self.assertIn("Chiudo Documento", service.handle("close", {"window": "blocco note"}))
            self.assertEqual([c for c in backend.calls if c[0] == "close"], [("close", 11)] * 3)
            # Delicata: «Invia» chiede sempre, anche dopo i sì.
            for _ in range(3):
                self.assertIn("delicata", service.handle("click", {"target": "Invia", "window": "WhatsApp"}))
                self.assertEqual(service.answer("sì"), "Clic su «Invia».")
            self.assertIn(("click", 320, 410), backend.calls)
            self.assertIn("Di' «sì»", service.handle("press", {"keys": ["alt", "f4"]}))
            self.assertEqual(service.answer("no"), "Annullato.")
            self.assertIsNone(service.answer("sì"))         # niente in sospeso

    def test_type_in_field_and_missing_element(self):
        with tempfile.TemporaryDirectory() as folder:
            service, backend = make(folder)
            service.settings["confirm_times"] = 0
            self.assertIn("Scritto", service.handle("type_in", {"text": "ciao", "target": "cerca",
                                                                "window": "whatsapp"}))
            self.assertIn(("type", "ciao"), backend.calls)
            self.assertIn("non trovo «Pippo»", service.handle("click", {"target": "Pippo",
                                                                         "window": "whatsapp"}))
            self.assertIsNone(service.handle("click", {"target": "il secondo"}))

    def test_runtime_off_does_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            service, backend = make(folder, enabled=False)
            runtime.register(service)
            lines = []
            self.assertFalse(runtime.handle_text("passa a Chrome", lines.append, lines.append))
            service.is_enabled = lambda: True
            self.assertTrue(runtime.handle_text("passa a Chrome", lines.append, lambda t: None))
            self.assertFalse(runtime.handle_text("passa a GPT", lines.append, lambda t: None))
            runtime.register(None)


if __name__ == "__main__":
    unittest.main()
