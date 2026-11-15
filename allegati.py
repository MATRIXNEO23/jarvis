"""Allegati della chat (passo 5, 15/11): pulsante 📎, trascinamento, Ctrl+V.

- File di testo (txt, md, csv, json, log, codice…) e documenti: Word .docx, PDF (pypdf
  incluso in terze_parti/), LibreOffice .odt/.ods/.odp, PowerPoint .pptx, Excel .xlsx, .rtf,
  pagine .html, libri .epub. Formati vecchi .doc/.xls/.ppt: chiede di salvarli nel nuovo
  formato. Immagini e PDF scansionati: niente testo (servirebbe l'OCR).
- Testo lungo incollato con Ctrl+V (oltre INCOLLA_COME_ALLEGATO caratteri) diventa un
  allegato invece di finire nella casella.
- Niente modello per scegliere: il testo è diviso in pezzi e Lumi tiene quelli con più
  parole della domanda, pesate per rarità (come un motore di ricerca). Al modello locale
  vanno PEZZI_LOCALE pezzi, a GPT PEZZI_ONLINE; se la domanda non ha parole utili, i
  primi pezzi (es. «riassumi il file»).
- Gli allegati restano finché li togli (✕, «togli gli allegati») o cambi chat.
"""
from __future__ import annotations

import math
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

MAX_BYTES = 5 * 1024 * 1024
MAX_BYTES_DOCUMENTI = 60 * 1024 * 1024     # PDF e documenti (libri impaginati)
MAX_CHARS = 400_000
PEZZO = 700
PEZZI_LOCALE = 3
PEZZI_ONLINE = 8
INCOLLA_COME_ALLEGATO = 1500
FILE_LUNGO = 6000
TESTO = {".txt", ".md", ".csv", ".tsv", ".json", ".log", ".ini", ".cfg", ".xml", ".html",
         ".htm", ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".cs", ".bat", ".ps1",
         ".yml", ".yaml", ".sql", ".srt", ".rtf"}
_STOP = frozenset(
    "il lo la i gli le un una uno di da in con su per tra fra che non come cosa del della "
    "dei delle degli al alla ai alle nel nella nei sul sulla questo questa quello quella "
    "sono mi ti ci si ne ed e o ma se anche più file testo allegato dimmi spiegami".split())


class AllegatoError(ValueError):
    pass


@dataclass
class Allegato:
    nome: str
    testo: str

    @property
    def pezzi(self) -> list[str]:
        return dividi(self.testo)


def leggi_file(path) -> Allegato:
    path = Path(path)
    if not path.is_file():
        raise AllegatoError("File non trovato: " + path.name)
    suffix = path.suffix.lower()
    limit = MAX_BYTES_DOCUMENTI if suffix in DOCUMENTI else MAX_BYTES
    if path.stat().st_size > limit:
        raise AllegatoError(path.name + ": file oltre %d MB, non allegato." % (limit // (1024 * 1024)))
    if suffix in DOCUMENTI:
        text = DOCUMENTI[suffix](path)
    elif suffix in (".doc", ".xls", ".ppt"):
        raise AllegatoError(path.name + ": formato vecchio di Office; salvalo come "
                            + {".doc": ".docx", ".xls": ".xlsx", ".ppt": ".pptx"}[suffix]
                            + " e riprova.")
    elif suffix in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".mp3", ".mp4", ".wav",
                    ".zip", ".exe"):
        raise AllegatoError(path.name + ": non è un documento di testo.")
    else:
        data = path.read_bytes()
        if suffix not in TESTO and b"\0" in data[:4096]:
            raise AllegatoError(path.name + ": non è un file di testo.")
        text = _decode(data)
    text = text.strip()
    if not text:
        raise AllegatoError(path.name + ": nessun testo da leggere.")
    return Allegato(path.name, text[:MAX_CHARS])


def da_testo(text: str, nome: str = "testo incollato") -> Allegato:
    text = str(text).strip()
    if not text:
        raise AllegatoError("Niente da allegare.")
    return Allegato(nome, text[:MAX_CHARS])


def _decode(data: bytes) -> str:
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", errors="replace")
    try:
        return data.decode("utf-8-sig")
    except UnicodeError:
        return data.decode("cp1252", errors="replace")


def _docx(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml").decode("utf-8", errors="replace")
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise AllegatoError(path.name + ": documento Word non leggibile.") from exc
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<w:tab/>", "\t", xml)
    text = re.sub(r"<[^>]+>", "", xml)
    for entity, char in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"),
                         ("&amp;", "&")):
        text = text.replace(entity, char)
    return text


# --- documenti (16/11: «documenti in generale») ------------------------------------------
def _zip_xml(path: Path, names) -> list[str]:
    try:
        with zipfile.ZipFile(path) as archive:
            wanted = [n for n in archive.namelist() if names(n)]
            return [archive.read(n).decode("utf-8", errors="replace") for n in sorted(wanted, key=_natural)]
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise AllegatoError(path.name + ": documento non leggibile.") from exc


def _natural(name: str):
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", name)]


def _xml_text(xml: str, paragraph=r"</(?:w:p|text:p|text:h|a:p)>") -> str:
    xml = re.sub(paragraph, "\n", xml)
    xml = re.sub(r"<(?:w:tab|text:tab)\s*/>", "\t", xml)
    xml = re.sub(r"<(?:w:br|text:line-break)\s*/>", "\n", xml)
    return _entities(re.sub(r"<[^>]+>", "", xml))


def _entities(text: str) -> str:
    import html
    return html.unescape(text)


def _odf(path: Path) -> str:
    return "\n".join(_xml_text(x) for x in _zip_xml(path, lambda n: n == "content.xml"))


def _pptx(path: Path) -> str:
    slides = _zip_xml(path, lambda n: re.fullmatch(r"ppt/slides/slide\d+\.xml", n) is not None)
    return "\n\n".join("[Diapositiva %d]\n%s" % (i + 1, _xml_text(x).strip())
                       for i, x in enumerate(slides))


def _xlsx(path: Path) -> str:
    shared_xml = _zip_xml(path, lambda n: n == "xl/sharedStrings.xml")
    shared = [_entities(re.sub(r"<[^>]+>", "", si))
              for si in re.findall(r"<si>(.*?)</si>", shared_xml[0], re.S)] if shared_xml else []
    out = []
    for index, sheet in enumerate(_zip_xml(path, lambda n: re.fullmatch(
            r"xl/worksheets/sheet\d+\.xml", n) is not None)):
        out.append("[Foglio %d]" % (index + 1))
        for row in re.findall(r"<row[^>]*>(.*?)</row>", sheet, re.S):
            cells = []
            for attrs, body in re.findall(r"<c([^>]*)>(.*?)</c>", row, re.S):
                value = re.search(r"<v>(.*?)</v>", body, re.S)
                inline = re.search(r"<t[^>]*>(.*?)</t>", body, re.S)
                if 't="s"' in attrs and value:
                    try:
                        cells.append(shared[int(value.group(1))])
                    except (ValueError, IndexError):
                        cells.append("")
                elif inline:
                    cells.append(_entities(inline.group(1)))
                elif value:
                    cells.append(_entities(value.group(1)))
            if any(c.strip() for c in cells):
                out.append("\t".join(cells))
    return "\n".join(out)


def _html_text(markup: str) -> str:
    markup = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", markup)
    markup = re.sub(r"(?i)<(?:br|/p|/div|/h\d|/li|/tr)[^>]*>", "\n", markup)
    return _entities(re.sub(r"<[^>]+>", "", markup))


def _html(path: Path) -> str:
    return _html_text(_decode(path.read_bytes()))


def _epub(path: Path) -> str:
    return "\n\n".join(_html_text(x) for x in _zip_xml(
        path, lambda n: n.lower().endswith((".xhtml", ".html", ".htm"))))


def _rtf(path: Path) -> str:
    text = _decode(path.read_bytes())
    text = re.sub(r"\{\\\*[^{}]*\}", "", text)
    text = re.sub(r"\{\\(?:fonttbl|colortbl|stylesheet|info)[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", "", text)
    text = re.sub(r"\\'([0-9a-fA-F]{2})",
                  lambda m: bytes([int(m.group(1), 16)]).decode("cp1252", errors="replace"), text)
    text = re.sub(r"\\(?:par|line)\b ?", "\n", text)
    text = re.sub(r"\\[a-zA-Z]+-?\d* ?", "", text)
    return text.replace("{", "").replace("}", "").replace("\\", "")


def _pdf(path: Path) -> str:
    """Testo dei PDF con pypdf (terze_parti/pypdf, BSD; o quello già installato)."""
    try:
        import pypdf
    except ImportError:
        import sys
        sys.path.append(str(Path(__file__).with_name("terze_parti")))
        try:
            import pypdf
        except ImportError as exc:
            raise AllegatoError(path.name + ": manca il lettore PDF (terze_parti/pypdf): "
                                "reinstalla il pacchetto di Lumi.") from exc
    try:
        reader = pypdf.PdfReader(str(path))
        if reader.is_encrypted and not reader.decrypt(""):
            raise AllegatoError(path.name + ": PDF protetto da password.")
        parts, total = [], 0
        for index, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            if text:
                parts.append("[Pagina %d]\n%s" % (index + 1, text))
                total += len(text)
            if total > MAX_CHARS:
                break
    except AllegatoError:
        raise
    except Exception as exc:          # PDF rovinati o particolari
        raise AllegatoError(path.name + ": PDF non leggibile (" + type(exc).__name__ + ").") from exc
    if not parts:
        raise AllegatoError(path.name + ": il PDF non contiene testo (forse è una scansione).")
    return "\n\n".join(parts)


DOCUMENTI = {".docx": lambda p: _docx(p), ".pdf": _pdf, ".odt": _odf, ".ods": _odf, ".odp": _odf,
             ".pptx": _pptx, ".xlsx": _xlsx, ".html": _html, ".htm": _html, ".epub": _epub,
             ".rtf": _rtf}


def dividi(text: str, size: int = PEZZO) -> list[str]:
    """Pezzi di circa `size` caratteri, tagliati tra paragrafi o frasi quando si può."""
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], ""
    for part in parts:
        while len(part) > size:
            cut = part.rfind(". ", 0, size)
            cut = cut + 1 if cut > size // 2 else size
            if current:
                chunks.append(current)
                current = ""
            chunks.append(part[:cut].strip())
            part = part[cut:].strip()
        if current and len(current) + len(part) + 2 > size:
            chunks.append(current)
            current = ""
        current = (current + "\n\n" + part) if current else part
    if current:
        chunks.append(current)
    return chunks


def _parole(text: str) -> list[str]:
    return [w for w in re.findall(r"\w{3,}", text.casefold()) if w not in _STOP]


def scegli(chunks: list[str], question: str, count: int) -> list[int]:
    """Indici dei pezzi più utili (in ordine di lettura)."""
    if len(chunks) <= count:
        return list(range(len(chunks)))
    terms = set(_parole(question))
    words = [_parole(chunk) for chunk in chunks]
    scores = []
    if terms:
        n = len(chunks)
        df = {t: sum(1 for w in words if t in w) for t in terms}
        for index, w in enumerate(words):
            score = 0.0
            for t in terms:
                tf = w.count(t)
                if tf:
                    idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                    score += idf * (tf * 2.2) / (tf + 1.2)
            scores.append((score, -index))
    best = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True) if (
        scores and max(s for s, _ in scores) > 0) else list(range(count))
    return sorted(best[:count])


class Allegati:
    """Allegati della chat attuale (UI thread)."""

    def __init__(self, on_change=lambda items: None):
        self.items: list[Allegato] = []
        self.on_change = on_change

    def aggiungi(self, item: Allegato) -> None:
        self.items = [a for a in self.items if a.nome != item.nome] + [item]
        self.on_change(self.items)

    def togli(self, nome: str | None = None) -> int:
        before = len(self.items)
        self.items = [] if nome is None else [a for a in self.items if a.nome != nome]
        if len(self.items) != before:
            self.on_change(self.items)
        return before - len(self.items)

    def pezzi(self, question: str, count: int) -> list[str]:
        """Pezzi da dare al modello, con il nome del file e la posizione."""
        out = []
        for item in self.items:
            chunks = item.pezzi
            for index in scegli(chunks, question, count):
                out.append("[%s, parte %d di %d]\n%s" % (item.nome, index + 1, len(chunks),
                                                         chunks[index]))
        return out

    def lungo(self) -> bool:
        return any(len(a.testo) > FILE_LUNGO for a in self.items)


ATTUALI = Allegati()


def per_modello_locale(question: str) -> list[str]:
    return ATTUALI.pezzi(question, PEZZI_LOCALE)


def per_online(question: str) -> list[str]:
    return ATTUALI.pezzi(question, PEZZI_ONLINE)


# --- Windows: file trascinati e file copiati negli appunti -------------------------------
def file_negli_appunti() -> list[str]:
    """Percorsi dei file copiati in Esplora file (CF_HDROP), o lista vuota."""
    import os
    if os.name != "nt":
        return []
    import ctypes
    from ctypes import wintypes
    user32, shell32 = ctypes.windll.user32, ctypes.windll.shell32
    user32.GetClipboardData.restype = wintypes.HANDLE
    shell32.DragQueryFileW.argtypes = (wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR,
                                       wintypes.UINT)
    if not user32.IsClipboardFormatAvailable(15) or not user32.OpenClipboard(None):
        return []
    try:
        handle = user32.GetClipboardData(15)
        return _drop_paths(shell32, handle) if handle else []
    finally:
        user32.CloseClipboard()


def _drop_paths(shell32, handle) -> list[str]:
    import ctypes
    count = shell32.DragQueryFileW(handle, 0xFFFFFFFF, None, 0)
    paths = []
    for index in range(min(count, 20)):
        length = shell32.DragQueryFileW(handle, index, None, 0)
        buffer = ctypes.create_unicode_buffer(length + 1)
        shell32.DragQueryFileW(handle, index, buffer, length + 1)
        paths.append(buffer.value)
    return paths


_HOOKS = []          # tiene vivi i callback di Windows


def abilita_trascinamento(widget, on_files) -> bool:
    """File trascinati sulla finestra di Lumi → on_files(percorsi). False se non possibile.

    Sottoclasse della finestra con ctypes (WM_DROPFILES), stesso metodo della libreria
    windnd (MIT), senza dipendenze nuove."""
    import os
    if os.name != "nt":
        return False
    import ctypes
    from ctypes import wintypes
    try:
        user32, shell32 = ctypes.windll.user32, ctypes.windll.shell32
        LRESULT = ctypes.c_ssize_t
        WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT,
                                     wintypes.WPARAM, wintypes.LPARAM)
        user32.CallWindowProcW.restype = LRESULT
        user32.CallWindowProcW.argtypes = (ctypes.c_void_p, wintypes.HWND, wintypes.UINT,
                                           wintypes.WPARAM, wintypes.LPARAM)
        setter = getattr(user32, "SetWindowLongPtrW", None) or user32.SetWindowLongW
        setter.restype = ctypes.c_void_p
        setter.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_void_p)
        shell32.DragQueryFileW.argtypes = (wintypes.HANDLE, wintypes.UINT, wintypes.LPWSTR,
                                           wintypes.UINT)
        shell32.DragFinish.argtypes = (wintypes.HANDLE,)
        shell32.DragAcceptFiles.argtypes = (wintypes.HWND, wintypes.BOOL)
        user32.GetAncestor.restype = wintypes.HWND
        user32.GetAncestor.argtypes = (wintypes.HWND, wintypes.UINT)
        hwnd = user32.GetAncestor(widget.winfo_id(), 2) or widget.winfo_id()   # GA_ROOT
        old = [None]

        def proc(h, msg, wparam, lparam):
            if msg == 0x0233:                       # WM_DROPFILES
                try:
                    paths = _drop_paths(shell32, wparam)
                finally:
                    shell32.DragFinish(wparam)
                try:
                    widget.after_idle(lambda: on_files(paths))
                except Exception:
                    pass
                return 0
            return user32.CallWindowProcW(old[0], h, msg, wparam, lparam)

        callback = WNDPROC(proc)
        _HOOKS.append(callback)
        shell32.DragAcceptFiles(hwnd, True)
        old[0] = setter(hwnd, -4, ctypes.cast(callback, ctypes.c_void_p))   # GWLP_WNDPROC
        return bool(old[0])
    except (AttributeError, OSError, ValueError):
        return False


# --- interfaccia -----------------------------------------------------------------------
NOTA_GPT = ("lo legge il modello locale (i pezzi utili per ogni domanda); GPT dal browser "
            "non lo riceve, per il suo limite di 5000 caratteri.")


class AllegatiView:
    """Riga «📎 nome ✕» sopra la casella, pulsante 📎, Ctrl+V e trascinamento."""

    def __init__(self, host, before, input_row, input_box, *, notify, bg, ask_files):
        import tkinter as tk
        self.tk = tk
        self.notify = notify
        self.ask_files = ask_files
        self.row = tk.Frame(host, bg=bg)
        self.before = before
        self.bg = bg
        self.packed = False
        ATTUALI.on_change = self.ridisegna
        self.button = tk.Button(
            input_row, text="📎", width=2, font=("Segoe UI Emoji", 11), bg=bg, fg="#76b9d1",
            activebackground="#0b344b", activeforeground="white", bd=0, relief="flat",
            cursor="hand2", command=self.scegli_file)
        self.button.pack(side="left", padx=(0, 4), before=input_box)
        input_box.bind("<Control-v>", self.incolla, add="+")
        input_box.bind("<Control-V>", self.incolla, add="+")
        self.input_box = input_box
        self.dnd = abilita_trascinamento(input_box, self.aggiungi_file)

    def scegli_file(self):
        paths = self.ask_files()
        if paths:
            self.aggiungi_file(list(paths))

    def aggiungi_file(self, paths, *, run_async=None, run_ui=None):
        """Legge i file in un thread (un PDF grande può metterci un po' sull'i3) e li
        aggiunge sull'interfaccia."""
        import threading
        run_ui = run_ui or (lambda fn: self.row.after(0, fn))
        run_async = run_async or (lambda fn: threading.Thread(
            target=fn, daemon=True, name="lumi-allegati").start())
        paths = list(paths)[:10]
        if any(Path(p).suffix.lower() in DOCUMENTI for p in paths):
            self.notify("ALLEGATI > Leggo il documento…")

        def work():
            for path in paths:
                try:
                    item = leggi_file(path)
                except (AllegatoError, OSError) as exc:
                    message = "ALLEGATI / ERRORE > " + str(exc)[:160]
                    run_ui(lambda m=message: self.notify(m))
                    continue
                run_ui(lambda i=item: self._added(i))
        run_async(work)

    def _added(self, item):
        ATTUALI.aggiungi(item)
        self.notify("ALLEGATI > «%s» allegato (%d caratteri): %s"
                    % (item.nome, len(item.testo), NOTA_GPT))

    def incolla(self, _event=None):
        files = file_negli_appunti()
        if files:
            self.aggiungi_file(files)
            return "break"
        try:
            text = self.input_box.clipboard_get()
        except self.tk.TclError:
            return None
        if len(text) > INCOLLA_COME_ALLEGATO:
            ATTUALI.aggiungi(da_testo(text, "testo incollato"))
            self.notify("ALLEGATI > Testo lungo incollato come allegato (%d caratteri): %s"
                        % (len(text), NOTA_GPT))
            return "break"
        return None

    def ridisegna(self, items):
        tk = self.tk
        for child in self.row.winfo_children():
            child.destroy()
        if not items:
            self.row.pack_forget()
            self.packed = False
            return
        for item in items:
            chip = tk.Frame(self.row, bg="#0b2f44")
            chip.pack(side="left", padx=(0, 4), pady=(0, 3))
            tk.Label(chip, text="📎 " + item.nome[:40], bg="#0b2f44", fg="#9fd8f0",
                     font=("Segoe UI", 8)).pack(side="left", padx=(6, 2))
            tk.Button(chip, text="✕", command=lambda n=item.nome: ATTUALI.togli(n),
                      bg="#0b2f44", fg="#ffb3b3", bd=0, relief="flat", cursor="hand2",
                      font=("Segoe UI", 8)).pack(side="left", padx=(0, 4))
        if not self.packed:
            self.row.pack(fill="x", before=self.before)
            self.packed = True
