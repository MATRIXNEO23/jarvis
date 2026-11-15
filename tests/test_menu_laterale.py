import tempfile
import tkinter as tk
import unittest
from pathlib import Path

import chat_elenco
import contesto_lumi
import menu_laterale
from local_model.chat_sessions import ChatSessionStore

P1 = "a" * 32
P2 = "b" * 32


class FakeWorkspace:
    def __init__(self):
        self.items = {P1: "Lavoro", P2: "Casa"}
        self.trashed = []

    def projects(self, limit=200):
        return [{"id": k, "name": v} for k, v in self.items.items()]

    def create_project(self, name):
        ident = "c" * 32
        self.items[ident] = name
        return ident

    def rename_project(self, ident, name):
        self.items[ident] = name

    def trash_project(self, ident):
        self.items.pop(ident)
        self.trashed.append(ident)

    def project_directory(self, ident):
        return Path("/non/esiste") / ident


class Base(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = ChatSessionStore(Path(self.folder.name) / "chat.sqlite3")
        self.workspace = FakeWorkspace()
        self.current = [None]
        self.refreshed = []
        self.notes = []

        def switch(ident):
            self.current[0] = ident
            self.refreshed.append("switch")
            return True

        self.albero = menu_laterale.Albero(
            self.store,
            projects=lambda: [(p["id"], p["name"]) for p in self.workspace.projects()],
            create_project=self.workspace.create_project,
            rename_project=self.workspace.rename_project,
            trash_project=self.workspace.trash_project,
            current_project=lambda: self.current[0], switch=switch,
            after_change=lambda: self.refreshed.append("refresh"), notify=self.notes.append)

    def tearDown(self):
        chat_elenco._CURRENT["elenco"] = None
        self.folder.cleanup()


class AlberoTest(Base):
    def test_chat_nei_progetti_e_fuori(self):
        inside = self.albero.nuova_chat(P1)
        self.assertEqual(self.current[0], P1)                 # aprire cambia progetto
        outside = self.albero.nuova_chat(None)
        self.assertEqual(self.current[0], None)
        self.assertEqual([c.id for c in self.albero.chats(P1)], [inside])
        self.assertEqual([c.id for c in self.albero.chats(None)], [outside])

    def test_sposta_dentro_e_fuori(self):
        chat = self.albero.nuova_chat(None)
        self.store.append_exchange(chat, "domanda", "risposta")
        self.assertTrue(self.albero.sposta_chat(chat, None, P2))
        self.assertEqual([c.id for c in self.albero.chats(P2)], [chat])
        self.assertEqual(self.albero.chats(None), [])
        self.assertEqual(self.store.exchange_count(chat, project_id=P2), 1)   # messaggi intatti
        self.assertTrue(self.albero.sposta_chat(chat, P2, None))
        self.assertFalse(self.albero.sposta_chat(chat, None, None))

    def test_apri_chat_di_un_altro_progetto(self):
        first = self.store.create_chat("Uno", project_id=P1, activate=True).id
        self.store.create_chat("Due", project_id=P1, activate=True)
        self.assertTrue(self.albero.apri_chat(first, P1))
        self.assertEqual(self.current[0], P1)
        self.assertEqual(self.store.active_chat(project_id=P1), first)

    def test_nuovo_rinomina_elimina_progetto(self):
        ident = self.albero.nuovo_progetto("Studio")
        self.assertEqual(self.workspace.items[ident], "Studio")
        self.assertTrue(self.albero.rinomina_progetto(ident, "Esami"))
        chat = self.albero.nuova_chat(ident)
        self.assertTrue(self.albero.elimina_progetto(ident))
        self.assertIsNone(self.current[0])                    # si torna fuori dai progetti
        self.assertNotIn(ident, self.workspace.items)
        self.assertEqual(self.albero.chats(ident), [])
        self.assertIsNone(self.albero.nuovo_progetto("  "))

    def test_vecchi_progetti_cancellati_una_volta(self):
        flag = Path(self.folder.name) / "progetti_nuovi.json"
        self.store.create_chat("Vecchia", project_id=P1)
        self.assertTrue(menu_laterale.vecchi_progetti_da_chiedere(flag))
        moved = []
        count = menu_laterale.cancella_vecchi_progetti(self.workspace, self.store, flag,
                                                       trash_folders=moved.extend)
        self.assertEqual(count, 2)
        self.assertEqual(self.workspace.items, {})
        self.assertEqual(self.store.list_chats(project_id=P1), ())
        self.assertFalse(menu_laterale.vecchi_progetti_da_chiedere(flag))


class AltreChatTest(Base):
    def test_le_chat_del_progetto_si_vedono(self):
        elenco = chat_elenco.ElencoChat(self.store, lambda: P1, lambda *a: None)
        other = self.store.create_chat("Preventivi", project_id=P1, activate=True).id
        self.store.append_exchange(other, "Quanto costa il tetto?", "Circa 5000 euro.", project_id=P1)
        self.store.create_chat("Idee", project_id=P1, activate=True)
        pieces = contesto_lumi.altre_chat()
        self.assertEqual(len(pieces), 1)
        self.assertIn("Preventivi", pieces[0])
        self.assertIn("5000 euro", pieces[0])
        outside = chat_elenco.ElencoChat(self.store, lambda: None, lambda *a: None)
        self.assertEqual(contesto_lumi.altre_chat(), [])     # fuori dai progetti: niente
        self.assertIsNotNone(elenco)
        self.assertIsNotNone(outside)


class SimboliEdEsportaTest(Base):
    def test_simboli_dei_modelli(self):
        chat = self.store.create_chat("Prova", activate=True)
        self.assertEqual(menu_laterale.etichetta("Prova", None), "💬 Prova")
        self.assertTrue(self.store.mark_model(chat.id, "offline"))
        self.assertFalse(self.store.mark_model(chat.id, "offline"))     # già segnato
        self.assertEqual(menu_laterale.etichetta("Prova", self.store.models()[chat.id]), "🤖 Prova")
        self.store.mark_model(chat.id, "online")
        self.assertEqual(menu_laterale.etichetta("Prova", self.albero.modelli()[chat.id]), "🤖📡 Prova")
        self.store.delete_chat(chat.id)
        self.assertEqual(self.store.models(), {})

    def test_registra_scambio_segna_chi_ha_risposto(self):
        elenco = chat_elenco.ElencoChat(self.store, lambda: None, lambda *a: None)
        chat_elenco._CURRENT["elenco"] = elenco
        chat_elenco.segna_modello("online")
        self.assertTrue(chat_elenco.registra_scambio("ciao", "ciao a te"))
        chat_elenco.registra_scambio("azione", "fatto")        # nessun modello: niente simbolo
        chat_id = elenco.current()
        self.assertEqual(self.store.models(), {chat_id: {"online"}})

    def test_esporta_json_tutta_la_chat(self):
        import json
        chat = self.store.create_chat("Progetto lungo", project_id=P1, activate=True)
        for n in range(3):
            self.store.append_exchange(chat.id, "domanda %d" % n, "risposta %d" % n, project_id=P1)
        self.store.mark_model(chat.id, "online")
        path = Path(self.folder.name) / "chat.json"
        self.assertEqual(menu_laterale.esporta_json(self.store, chat.id, P1, path), 6)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["title"], "Progetto lungo")
        self.assertEqual(data["models"], ["online"])
        self.assertEqual([m["role"] for m in data["messages"][:2]], ["user", "assistant"])
        self.assertEqual(data["messages"][-1]["content"], "risposta 2")


class VistaTest(Base):
    def test_albero_disegnato_e_clic(self):
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        root.withdraw()
        try:
            header, body = tk.Frame(root), tk.Frame(root)
            header.pack()
            body.pack()
            before = tk.Text(body)
            before.pack()
            self.store.create_chat("Preventivi", project_id=P1, activate=True)
            self.store.create_chat("Libera", activate=True)
            view = menu_laterale.MenuView(header, body, before, self.albero,
                                          ask_text=lambda *a: None, confirm=lambda *a: True)
            calls = []
            view.extra = [("✈ Telegram", lambda: calls.append("telegram"))]
            view.toggle()
            texts = [view.tree.item(i, "text") for i in view.items]
            self.assertIn("📁 Lavoro", texts)
            self.assertIn("💬 Preventivi", texts)
            self.assertIn("💬 Libera", texts)
            self.assertEqual(texts[-1], "✈ Telegram")
            self.assertEqual(view.title.get(), "Libera")
            telegram = [i for i, v in view.items.items() if v[0] == "extra"][0]
            view.tree.focus(telegram)
            view._click()
            self.assertEqual(calls, ["telegram"])
            chat = [i for i, v in view.items.items() if v[0] == "chat" and v[1] == P1][0]
            view.tree.focus(chat)
            view._click()
            self.assertEqual(self.current[0], P1)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
