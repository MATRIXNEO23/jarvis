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

    def show_window(self, hwnd, how):
        self.calls.append(("show", hwnd, how))
        return True


ELEMENTS = {33: [{"name": "Cerca", "type": "Edit", "x": 10, "y": 20, "w": 100, "h": 20, "enabled": True},
                 {"name": "Invia", "type": "Button", "x": 300, "y": 400, "w": 40, "h": 20, "enabled": True}],
            11: [{"name": "File", "type": "MenuItem", "x": 0, "y": 0, "w": 30, "h": 20, "enabled": True}]}


def make(folder, enabled=True, clock=lambda: 0):
    backend = FakeBackend()
    service = ControlService(lambda: enabled, Path(folder), backend,
                             elements=lambda hwnd: ELEMENTS.get(hwnd, []), clock=clock)
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
                         ("type_in", {"text": "ciao mamma", "target": "Cerca", "window": None,
                                      "append": False}))
        self.assertEqual(parse_command("scorri giù"), ("scroll", {"amount": -3}))
        self.assertEqual(parse_command("scorri su di 5"), ("scroll", {"amount": 5}))
        self.assertEqual(parse_command("chiama questa finestra lavoro"),
                         ("name_window", {"window": None, "name": "lavoro"}))
        self.assertIsNone(parse_command("metti Imagine"))
        self.assertIsNone(parse_command("apri chrome"))                 # resta a Programmi
        self.assertEqual(parse_command("clicca il 3")[0], "pick")
        self.assertEqual(parse_command("apri l'ultima cartella"),
                         ("pick", {"position": -1, "kind": "cartella", "how": "double"}))
        self.assertEqual(parse_command("aprilo"), ("open_selected", {}))
        self.assertEqual(parse_command("apri"), ("open_bare", {}))
        self.assertEqual(parse_command("giù"), ("step", {"dir": "giù"}))
        self.assertEqual(parse_command("su di un livello"), ("nav", {"dir": "su di un livello"}))
        self.assertEqual(parse_command("pulisci la ricerca"), ("clear_field", {"target": "cerca"}))
        self.assertEqual(parse_command("minimizza"), ("window_state", {"how": "minimizza", "window": None}))
        self.assertIsNone(parse_keys("a"))


class ServiceTests(unittest.TestCase):
    def test_list_switch_by_number_name_and_nickname(self):
        with tempfile.TemporaryDirectory() as folder:
            service, backend = make(folder)
            self.assertIn("2. YouTube - Google Chrome", service.handle("list_windows", {}))
            self.assertIn("YouTube", service.handle("switch", {"window": "2"}))
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
                self.assertIn("Documento", service.answer("sì"))
            self.assertIn("Documento", service.handle("close", {"window": "blocco note"}))
            self.assertEqual([c for c in backend.calls if c[0] == "close"], [("close", 11)] * 3)
            # Delicata: «Invia» chiede sempre, anche dopo i sì.
            for _ in range(3):
                self.assertIn("delicata", service.handle("click", {"target": "Invia", "window": "WhatsApp"}))
                self.assertIn("Invia", service.answer("sì"))
            self.assertIn(("click", 320, 410), backend.calls)
            self.assertIn("Di' «sì»", service.handle("press", {"keys": ["alt", "f4"]}))
            from frasi_lumi import phrases
            self.assertIn(service.answer("no"), [p for p, _ in phrases("annullato")])
            self.assertIsNone(service.answer("sì"))         # niente in sospeso

    def test_type_in_field_and_missing_element(self):
        with tempfile.TemporaryDirectory() as folder:
            service, backend = make(folder)
            service.settings["confirm_times"] = 0
            self.assertIn("Cerca", service.handle("type_in", {"text": "ciao", "target": "cerca",
                                                              "window": "whatsapp"}))
            self.assertIn(("type", "ciao"), backend.calls)
            self.assertIn(("press", ("ctrl", "a")), backend.calls)      # sostituisce
            service.handle("type_in", {"text": "neri", "target": "cerca", "window": "whatsapp",
                                       "append": True})
            self.assertIn(("press", ("fine",)), backend.calls)          # accoda
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


EXPLORER = {44: [
    {"name": "Indietro", "type": "Button", "x": 0, "y": 0, "w": 20, "h": 20, "enabled": True},
    {"name": "Download", "type": "TreeItem", "x": 0, "y": 50, "w": 80, "h": 20, "enabled": True},
    {"name": "Cerca in Download", "type": "Edit", "x": 300, "y": 0, "w": 100, "h": 20, "enabled": True},
    {"name": "Foto vacanze", "type": "ListItem", "x": 100, "y": 100, "w": 100, "h": 20, "enabled": True},
    {"name": "mare.jpg", "type": "ListItem", "x": 100, "y": 120, "w": 100, "h": 20, "enabled": True},
    {"name": "lettera.pdf", "type": "ListItem", "x": 100, "y": 140, "w": 100, "h": 20, "enabled": True}]}


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.now = [1000.0]
        self.backend = FakeBackend()
        self.backend.items = [{"hwnd": 44, "title": "Download", "process": "explorer.exe", "pid": 9}]
        self.service = ControlService(lambda: True, Path(self.tmp.name), self.backend,
                                      elements=lambda hwnd: EXPLORER.get(hwnd, []),
                                      clock=lambda: self.now[0])
        self.service.focused = lambda: EXPLORER[44][4]
        self.overlay = []
        self.service.show_overlay = self.overlay.append

    def tearDown(self):
        self.tmp.cleanup()

    def test_numbers_then_pick_and_open_selected(self):
        reply = self.service.handle("show_numbers", {})
        self.assertIn("1. Indietro", reply)
        self.assertEqual(len(self.overlay[-1]), 6)
        self.service.handle("pick", {"position": 5, "kind": "", "how": "select", "bare": True})
        self.assertEqual(self.backend.calls[-1], ("click", 150, 130))   # puntatore su mare.jpg
        self.service.handle("open_selected", {})
        self.assertIn(("click", 150, 130), self.backend.calls)
        self.assertIsNone(self.overlay[-1])                             # numeri tolti

    def test_position_and_kind_without_numbers(self):
        self.service.handle("pick", {"position": 1, "kind": "immagine", "how": "double"})
        self.assertEqual(self.backend.calls[-1], ("click", 150, 130))
        self.service.handle("pick", {"position": -1, "kind": "", "how": "select"})
        self.assertEqual(self.backend.calls[-1], ("click", 150, 150))   # ultimo: lettera.pdf
        self.service.handle("pick", {"position": 1, "kind": "cartella", "how": "select"})
        self.assertEqual(self.backend.calls[-1], ("click", 150, 110))   # Foto vacanze

    def test_open_bare_asks_and_short_words_need_recent_use(self):
        self.assertFalse(self.service.claims("step", {"dir": "giù"}))   # non usato da poco
        self.service.handle("pick", {"position": 2, "kind": "", "how": "select"})
        self.assertTrue(self.service.claims("step", {"dir": "giù"}))
        self.assertIn("mare.jpg", self.service.handle("open_bare", {}))
        self.assertIn("mare.jpg", self.service.answer("sì"))
        self.now[0] += 500
        self.assertFalse(self.service.claims("nav", {"dir": "indietro"}))

    def test_step_nav_explorer_vai_su_and_clear(self):
        self.service.handle("pick", {"position": 1, "kind": "", "how": "select"})
        self.assertIn("mare.jpg", self.service.handle("step", {"dir": "giù"}))
        self.assertIn(("press", ("giu",)), self.backend.calls)
        self.service.handle("nav", {"dir": "indietro"})
        self.assertEqual(self.backend.calls[-1], ("click", 10, 10))     # sulla freccia Indietro
        self.service.handle("switch", {"window": "Download"})
        self.assertEqual(self.backend.calls[-1], ("click", 40, 60))     # voce nel riquadro
        self.service.handle("clear_field", {"target": "cerca"})
        self.assertIn(("press", ("canc",)), self.backend.calls)
        self.service.handle("window_state", {"how": "minimizza", "window": None})
        self.assertIn(("show", 44, "minimizza"), self.backend.calls)
        self.assertIn("puoi dire", self.service.handle("context_help", {}))
        self.assertIn("puoi dire", self.service.handle("more_help", {}))


if __name__ == "__main__":
    unittest.main()


class ConflictTests(unittest.TestCase):
    """Nessun comando di un'altra sezione deve essere preso dal Controllo PC, se non
    come parola corta valida solo mentre si usa il Controllo PC (claims)."""

    def test_other_sections_commands_not_taken(self):
        import command_aliases
        from controllo_pc.service import ControlService
        catalog = command_aliases.catalog(None, music=False, pc=False)
        for section, commands in catalog.items():
            if section == "Controllo PC":
                continue
            for command in commands:
                text = command.replace("{testo}", "prova")
                with self.subTest(section=section, command=text):
                    request = parse_command(text)
                    self.assertTrue(request is None or request[0] in ControlService.SHORT_ACTIONS,
                                    f"{text!r} -> {request}")
