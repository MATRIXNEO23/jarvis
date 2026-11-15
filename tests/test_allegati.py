import tempfile
import tkinter as tk
import unittest
import zipfile
from pathlib import Path

import allegati
import lumi_comandi
from allegati import Allegati, AllegatoError, da_testo, dividi, leggi_file, scegli
from local_model.memory_preferences import MemoryPreferences
from local_model.native_config import NativeModelConfig
from local_model.native_conversation_session import NativeConversationSession
from test_native_context_window import CountingAdapter


class LetturaTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.dir = Path(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def test_testo_utf8_e_cp1252(self):
        (self.dir / "a.txt").write_text("Perché sì", encoding="utf-8")
        (self.dir / "b.txt").write_bytes("Perché".encode("cp1252"))
        self.assertEqual(leggi_file(self.dir / "a.txt").testo, "Perché sì")
        self.assertEqual(leggi_file(self.dir / "b.txt").testo, "Perché")

    def test_docx(self):
        path = self.dir / "c.docx"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml",
                             "<w:document><w:p><w:r><w:t>Primo &amp; due</w:t></w:r></w:p>"
                             "<w:p><w:r><w:t>Secondo</w:t></w:r></w:p></w:document>")
        self.assertEqual(leggi_file(path).testo, "Primo & due\nSecondo")

    def test_rifiuti_chiari(self):
        (self.dir / "d.pdf").write_bytes(b"%PDF-1.4")
        (self.dir / "e.bin").write_bytes(b"\0\1\2" * 10)
        (self.dir / "f.txt").write_text("   ", encoding="utf-8")
        for name in ("d.pdf", "e.bin", "f.txt", "manca.txt"):
            with self.assertRaises(AllegatoError, msg=name):
                leggi_file(self.dir / name)


class SceltaPezziTest(unittest.TestCase):
    def test_divide_in_pezzi_limitati(self):
        text = "\n\n".join("Paragrafo %d. " % n + "parola " * 40 for n in range(10))
        chunks = dividi(text, 300)
        self.assertTrue(all(len(c) <= 300 for c in chunks))
        self.assertEqual("".join(chunks).count("Paragrafo"), 10)

    def test_sceglie_i_pezzi_con_le_parole_rare_della_domanda(self):
        chunks = ["il gatto mangia"] * 5 + ["la ricetta della carbonara con guanciale",
                                            "il gatto dorme"] + ["altro testo"] * 3
        self.assertEqual(scegli(chunks, "come si fa la carbonara?", 1), [5])
        # Senza parole utili: i primi pezzi.
        self.assertEqual(scegli(chunks, "riassumi il file", 2), [0, 1])

    def test_allegati_della_chat(self):
        changes = []
        items = Allegati(on_change=changes.append)
        items.aggiungi(da_testo("uno " * 10, "a"))
        items.aggiungi(da_testo("due", "a"))           # stesso nome: sostituisce
        self.assertEqual(len(items.items), 1)
        piece = items.pezzi("due", 3)[0]
        self.assertTrue(piece.startswith("[a, parte 1 di 1]"))
        self.assertEqual(items.togli(), 1)
        self.assertEqual(items.togli(), 0)
        self.assertEqual(len(changes), 3)

    def test_comando_vocale(self):
        self.assertEqual(lumi_comandi.parse("togli gli allegati"), "attachments_clear")
        self.assertEqual(lumi_comandi.parse("Lumi, rimuovi l'allegato"), "attachments_clear")
        self.assertIsNone(lumi_comandi.parse("togli il file"))


class PromptConAllegatoTest(unittest.TestCase):
    def session(self, context=2048):
        adapter = CountingAdapter()
        session = NativeConversationSession(
            adapter, config_loader=lambda: NativeModelConfig(context_size=context, max_output=128),
            memory_loader=MemoryPreferences)
        return session, adapter

    def test_pezzi_nel_prompt_prima_della_domanda(self):
        session, adapter = self.session()
        reader = lambda budget: ""
        reader.attachment = ["[nota.txt, parte 1 di 1]\nIl codice segreto è 42."]
        turn = session.prepare_turn("Qual è il codice?", memory_context=reader)
        session._commit_turn(turn)
        session.ask("Qual è il codice?", memory_context=reader)
        prompt = adapter.calls[-1]
        self.assertIn("Dati di riferimento (allegati o scheda di Lumi", prompt)
        self.assertLess(prompt.rindex("codice segreto"), prompt.rindex("Qual è il codice?"))

    def test_allegato_troppo_grande_avvisa(self):
        session, adapter = self.session(context=512)
        reader = lambda budget: ""
        reader.attachment = ["x" * 4000]
        turn = session.prepare_turn("Domanda", memory_context=reader)
        self.assertIn("allegato non entra", turn.context_note)


class VistaTest(unittest.TestCase):
    def test_incolla_lungo_diventa_allegato_e_chip(self):
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        root.withdraw()
        notes = []
        try:
            host = tk.Frame(root)
            host.pack()
            row = tk.Frame(host)
            row.pack()
            box = tk.Entry(row)
            box.pack()
            view = allegati.AllegatiView(host, row, row, box, notify=notes.append, bg="#000",
                                         ask_files=lambda: ())
            root.clipboard_clear()
            root.clipboard_append("breve")
            self.assertIsNone(view.incolla())
            root.clipboard_clear()
            root.clipboard_append("lungo " * 400)
            self.assertEqual(view.incolla(), "break")
            self.assertEqual(allegati.ATTUALI.items[0].nome, "testo incollato")
            self.assertTrue(view.packed)
            self.assertIn("ALLEGATI >", notes[-1])
            allegati.ATTUALI.togli()
            self.assertFalse(view.packed)
        finally:
            allegati.ATTUALI.togli()
            allegati.ATTUALI.on_change = lambda items: None
            root.destroy()


if __name__ == "__main__":
    unittest.main()


def _pdf_bytes(text):
    stream = ("BT /F1 12 Tf 20 100 Td (%s) Tj ET" % text).encode("latin-1")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents 4 0 R "
               b"/Resources << /Font << /F1 5 0 R >> >> >>",
               b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offsets = b"%PDF-1.4\n", []
    for number, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    return out


class DocumentiTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.dir = Path(self.folder.name)

    def tearDown(self):
        self.folder.cleanup()

    def zipped(self, name, files):
        path = self.dir / name
        with zipfile.ZipFile(path, "w") as archive:
            for inner, content in files.items():
                archive.writestr(inner, content)
        return path

    def test_pdf_con_pypdf_incluso(self):
        path = self.dir / "libro.pdf"
        path.write_bytes(_pdf_bytes("Ciao dal PDF"))
        self.assertIn("Ciao dal PDF", leggi_file(path).testo)
        self.assertIn("[Pagina 1]", leggi_file(path).testo)

    def test_office_e_libreoffice(self):
        odt = self.zipped("a.odt", {"content.xml": "<o><text:p>Uno &amp; due</text:p><text:p>Tre</text:p></o>"})
        self.assertEqual(leggi_file(odt).testo, "Uno & due\nTre")
        pptx = self.zipped("b.pptx", {"ppt/slides/slide2.xml": "<p><a:p><a:t>Secondo</a:t></a:p></p>",
                                      "ppt/slides/slide1.xml": "<p><a:p><a:t>Titolo</a:t></a:p></p>"})
        text = leggi_file(pptx).testo
        self.assertLess(text.index("Titolo"), text.index("Secondo"))
        xlsx = self.zipped("c.xlsx", {
            "xl/sharedStrings.xml": "<sst><si><t>Nome</t></si><si><t>Mario</t></si></sst>",
            "xl/worksheets/sheet1.xml": ('<w><row><c t="s"><v>0</v></c><c><v>42</v></c></row>'
                                         '<row><c t="s"><v>1</v></c><c t="inlineStr"><is><t>ok</t></is></c></row></w>')})
        self.assertIn("Nome\t42", leggi_file(xlsx).testo)
        self.assertIn("Mario\tok", leggi_file(xlsx).testo)

    def test_html_epub_rtf(self):
        page = self.dir / "p.html"
        page.write_text("<html><style>x{}</style><p>Ciao</p><p>Mondo &egrave;</p></html>", encoding="utf-8")
        self.assertEqual(leggi_file(page).testo.split(), ["Ciao", "Mondo", "è"])
        epub = self.zipped("l.epub", {"OEBPS/c1.xhtml": "<html><body><p>Capitolo uno</p></body></html>"})
        self.assertIn("Capitolo uno", leggi_file(epub).testo)
        rtf = self.dir / "r.rtf"
        rtf.write_text(r"{\rtf1\ansi{\fonttbl{\f0 Arial;}}\f0 Perch\'e8 s\'ec\par Fine}", encoding="ascii")
        self.assertEqual(leggi_file(rtf).testo.split(), ["Perchè", "sì", "Fine"])

    def test_formati_vecchi_e_immagini(self):
        for name, words in (("v.doc", ".docx"), ("i.png", "non è un documento")):
            (self.dir / name).write_bytes(b"x")
            with self.assertRaises(AllegatoError) as ctx:
                leggi_file(self.dir / name)
            self.assertIn(words, str(ctx.exception))

    def test_lettura_in_un_thread_poi_aggiunta(self):
        path = self.dir / "n.txt"
        path.write_text("nota", encoding="utf-8")
        added, notes = [], []
        view = allegati.AllegatiView.__new__(allegati.AllegatiView)
        view.notify = notes.append
        view._added = added.append
        allegati.AllegatiView.aggiungi_file(view, [path, self.dir / "manca.txt"],
                                           run_async=lambda fn: fn(), run_ui=lambda fn: fn())
        self.assertEqual([a.nome for a in added], ["n.txt"])
        self.assertIn("non trovato", notes[-1])
