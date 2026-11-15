import tkinter as tk
import unittest
from tkinter import ttk
from unittest import mock

import addon_righe
import addon_ui
import impostazioni_menu as im


class FakeManager:
    def __init__(self):
        self.items = [{"id": "musica", "name": "Musica", "version": "1", "description": "",
                       "enabled": True, "action_count": 2},
                      {"id": "nuovo", "name": "Nuovo", "version": "1", "description": "",
                       "enabled": False, "action_count": 1}]
        self.calls = []

    def list_installed(self):
        return tuple(dict(i) for i in self.items)

    def set_enabled(self, ident, enabled):
        self.calls.append((ident, enabled))
        next(i for i in self.items if i["id"] == ident)["enabled"] = enabled


class Base(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()


class RigheTest(Base):
    def test_icone_colori_e_clic(self):
        self.assertEqual(addon_righe.icona("musica"), "🎵")
        self.assertEqual(addon_righe.icona("sconosciuto"), addon_righe.ICONA_GENERICA)
        manager, opened = FakeManager(), []
        changes = []

        def cambia(ident, on):
            changes.append((ident, on))
            manager.set_enabled(ident, on)
            return True
        rows = addon_righe.RigheAddon(self.root, elenco=manager.list_installed,
                                      apri=opened.append, cambia=cambia)
        _row, icon, _name, switch = rows.righe["musica"]
        self.assertEqual(icon.cget("fg"), addon_righe.AZZURRO)
        self.assertTrue(switch.acceso)
        self.assertEqual(rows.righe["nuovo"][1].cget("fg"), addon_righe.ARANCIONE)
        switch.clic()                                  # interruttore: spegne, non apre
        self.assertEqual(changes, [("musica", False)])
        self.assertFalse(switch.acceso)
        self.assertEqual(icon.cget("fg"), addon_righe.ARANCIONE)
        self.assertEqual(opened, [])
        rows.apri("nuovo")                             # icona/nome: apre il menu
        self.assertEqual(opened, ["nuovo"])

    def test_cambio_rifiutato_non_scorre(self):
        manager = FakeManager()
        rows = addon_righe.RigheAddon(self.root, elenco=manager.list_installed,
                                      apri=lambda _i: None, cambia=lambda _i, _on: False)
        switch = rows.righe["nuovo"][3]
        switch.clic()
        self.assertFalse(switch.acceso)
        self.assertEqual(rows.righe["nuovo"][1].cget("fg"), addon_righe.ARANCIONE)

    def test_sincronizza_dopo_cambio_altrove(self):
        manager = FakeManager()
        rows = addon_righe.RigheAddon(self.root, elenco=manager.list_installed,
                                      apri=lambda _i: None, cambia=lambda _i, _on: True)
        manager.set_enabled("nuovo", True)
        rows.sincronizza()
        self.assertTrue(rows.righe["nuovo"][3].acceso)
        self.assertEqual(rows.righe["nuovo"][1].cget("fg"), addon_righe.AZZURRO)


class SezioneTest(Base):
    def test_accendere_e_spegnere_senza_domande(self):
        manager, after = FakeManager(), []
        frame = ttk.Frame(self.root)
        section = addon_ui.SezioneAddon(frame, manager, window=self.root,
                                        after_change=lambda: after.append(1))
        section.mostra("nuovo")
        self.assertTrue(frame.winfo_children())
        with mock.patch.object(addon_ui.messagebox, "askyesno") as ask:
            self.assertTrue(section.cambia("musica", False))
            self.assertTrue(section.cambia("nuovo", True))
            ask.assert_not_called()
        self.assertEqual(manager.calls, [("musica", False), ("nuovo", True)])
        self.assertEqual(after, [1, 1])
        self.assertFalse(section.cambia("nuovo", True))   # già acceso: niente


class NavigazioneConRigheTest(Base):
    def test_pagina_propria_e_righe_in_cima(self):
        win = tk.Toplevel(self.root)
        nb = ttk.Notebook(win)
        nb.pack()
        pages = {}
        for title, box in (("Progetti e servizi", "Add-on — installazione"), ("Add-on scelto", None)):
            page = ttk.Frame(nb)
            nb.add(page, text=title)
            pages[title] = page
            if box:
                ttk.LabelFrame(page, text=box).pack(fill="x")
        ttk.Label(pages["Add-on scelto"], text="menu").pack()
        built = []

        def righe(container):
            built.append(container)
            return tk.Frame(container)
        nav = im.Navigazione(win, nb, pages, main_root=self.root, righe={"Add-on": righe},
                             proprie=("Add-on scelto",))
        self.assertEqual(list(nav.voci()), ["Add-on"])
        self.assertEqual(len(built), 1)
        nav.mostra_pagina("Add-on scelto")
        self.assertEqual(nb.select(), str(pages["Add-on scelto"]))
        nav.mostra("Add-on", "Gestisci add-on")
        self.assertTrue(pages["Add-on scelto"].winfo_children()[0].winfo_manager())


if __name__ == "__main__":
    unittest.main()
