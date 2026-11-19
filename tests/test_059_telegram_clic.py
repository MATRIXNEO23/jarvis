"""059: il clic sul simbolo Telegram (Canvas figlio del tasto) apre la tendina e non la richiude subito."""
import tkinter as tk
import unittest
from types import SimpleNamespace

import barra_tasti
import telegram_vista as tv


class ClicSimboloTest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.btn = barra_tasti.TastoBarra(self.root, "Telegram", lambda: None, simbolo="telegram")
        self.btn.pack()
        self.vista = tv.Telegram(self.root, self.btn, workspace=lambda: None, settings=lambda: {},
                                 auto_var=tk.BooleanVar(self.root, value=True), contacts=lambda: [],
                                 save_contacts=lambda r: True, toggle_auto=lambda: None,
                                 open_manager=lambda: None, show_chat=lambda *a: None,
                                 send_voice=lambda *a: True)

    def tearDown(self):
        self.vista.close()
        self.root.destroy()

    def test_clic_sul_simbolo_non_chiude(self):
        self.vista.open()
        self.vista._click_anywhere(SimpleNamespace(widget=self.btn.label))
        self.assertIsNotNone(self.vista.popup)

    def test_clic_fuori_chiude(self):
        self.vista.open()
        self.vista._click_anywhere(SimpleNamespace(widget=self.root))
        self.assertIsNone(self.vista.popup)

    def test_clic_sul_simbolo_apre_e_resta_aperta(self):
        self.root.update()
        self.btn._click(self.btn._command)
        self.vista._click_anywhere(SimpleNamespace(widget=self.btn.label))
        self.assertIsNotNone(self.vista.popup)


if __name__ == "__main__":
    unittest.main()
