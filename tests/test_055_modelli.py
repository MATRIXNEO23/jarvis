"""055 D-E: modelli aggiunti senza copia, caselle 1/2/3, profili per modello, GGUF, salvataggio atomico."""
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from local_model import miei_modelli, profili_famiglia as pf, registro_modelli as rm, scelta_modello as sm
from local_model.native_config import NativeModelConfig


def _kv_string(key, value):
    k, v = key.encode(), value.encode()
    return struct.pack("<Q", len(k)) + k + struct.pack("<IQ", 8, len(v)) + v


def gguf(path: Path, arch="", filler=0) -> Path:
    """GGUF valido: prima `filler` coppie (array di stringhe lungo, oltre i 64 KiB), poi l'architettura."""
    pairs = b""
    count = 0
    if filler:
        key = b"tokenizer.ggml.tokens"
        items = b"".join(struct.pack("<Q", 20) + b"x" * 20 for _ in range(filler))
        pairs += struct.pack("<Q", len(key)) + key + struct.pack("<IIQ", 9, 8, filler) + items
        count += 1
    pairs += struct.pack("<Q", 9) + b"general.n" + struct.pack("<II", 4, 7)   # u32 qualunque
    count += 1
    if arch:
        pairs += _kv_string("general.architecture", arch)
        count += 1
    path.write_bytes(b"GGUF" + struct.pack("<IQQ", 3, 0, count) + pairs + b"x" * 64)
    return path


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.dir = root / "addon-data" / "modello_locale"
        (self.dir / "modelli").mkdir(parents=True)
        self.cfg = self.dir / "native.json"
        self.downloads = root / "Downloads"
        self.downloads.mkdir()
        self.gemma = gguf(self.dir / "modelli" / "gemma-2-2b.gguf", "gemma2")
        self.qwen = gguf(self.downloads / "Qwen3-1.7B.gguf", "qwen3")
        self.save(self.gemma)

    def save(self, model, **values):
        NativeModelConfig(model=str(model), **values).save(self.cfg)


class GgufTests(Base):
    def test_architecture_found_after_a_long_metadata_array(self):
        file = gguf(Path(self.tmp.name) / "lungo.gguf", "qwen3", filler=20000)   # > 64 KiB prima della chiave
        self.assertGreater(file.stat().st_size, 1 << 16)
        self.assertEqual(pf.leggi_architettura(file), "qwen3")
        self.assertEqual(pf.riconosci_famiglia(file), ("qwen", True))

    def test_uncertain_family_is_flagged_and_broken_files_do_not_crash(self):
        odd = gguf(Path(self.tmp.name) / "modello-xyz.gguf", "")
        self.assertEqual(pf.riconosci_famiglia(odd), ("generico", False))
        self.assertIn("incerta", pf.messaggio_famiglia("generico", False, 1))
        broken = Path(self.tmp.name) / "rotto.gguf"
        broken.write_bytes(b"GGUF" + b"\x00" * 5)
        self.assertEqual(pf.leggi_architettura(broken), "")
        self.assertEqual(pf.riconosci_famiglia("Qwen3-1.7B-Q4_K_M.gguf"), ("qwen", True))


class RegistroTests(Base):
    def test_add_does_not_copy_and_shows_up_in_list_and_choice(self):
        before = sorted(p.name for p in (self.dir / "modelli").iterdir())
        target = miei_modelli.aggiungi_modello(self.qwen, self.cfg)
        self.assertEqual(target, self.qwen)
        self.assertEqual(sorted(p.name for p in (self.dir / "modelli").iterdir()), before)
        names = [m.name for m in sm.elenca_modelli(self.cfg)]
        self.assertIn("Qwen3-1.7B.gguf", names)
        with self.assertRaises(ValueError):
            miei_modelli.aggiungi_modello(self.qwen, self.cfg)              # già presente
        with self.assertRaises(ValueError):
            miei_modelli.aggiungi_modello(Path(self.tmp.name) / "no.txt", self.cfg)

    def test_vanished_file_is_reported_not_listed(self):
        miei_modelli.aggiungi_modello(self.qwen, self.cfg)
        self.qwen.unlink()
        self.assertEqual([p.name for p in rm.mancanti(self.cfg)], ["Qwen3-1.7B.gguf"])
        self.assertNotIn("Qwen3-1.7B.gguf", [m.name for m in sm.elenca_modelli(self.cfg)])

    def test_remove_of_added_model_keeps_the_file(self):
        miei_modelli.aggiungi_modello(self.qwen, self.cfg)
        trash = mock.Mock()
        miei_modelli.rimuovi_modello(self.qwen, self.cfg, trash)
        trash.assert_not_called()
        self.assertTrue(self.qwen.is_file())
        self.assertNotIn(self.qwen.name, [m.name for m in sm.elenca_modelli(self.cfg)])

    def test_three_fixed_slots_are_preassigned_and_voice_order_follows(self):
        extra = [gguf(self.downloads / ("m%d.gguf" % n), "llama") for n in range(4)]
        for item in [self.qwen] + extra:
            rm.aggiungi(item, self.cfg)
        listing = sm.elenca_modelli(self.cfg)
        slots = rm.caselle(listing, str(self.gemma), self.cfg)
        self.assertEqual(set(slots), {1, 2, 3})
        self.assertEqual(slots[1], self.gemma)                      # il modello in uso va in casella 1
        self.assertEqual(len({str(v) for v in slots.values()}), 3)
        self.assertEqual(listing[:3], [slots[1], slots[2], slots[3]])
        self.assertEqual(len(listing), 6)
        rm.assegna_casella(3, self.qwen, self.cfg)
        self.assertEqual(rm.caselle(listing, str(self.gemma), self.cfg)[3], self.qwen)
        text, spoken = sm.testo_elenco(listing)
        self.assertIn("Ne ho 6", spoken)
        self.assertNotIn("Qwen", spoken)

    def test_registry_file_is_written_atomically(self):
        rm.aggiungi(self.qwen, self.cfg)
        self.assertEqual(json.loads((self.dir / "modelli_aggiunti.json").read_text(encoding="utf-8"))["aggiunti"],
                         [str(self.qwen)])
        self.assertEqual([p.name for p in self.dir.glob("*.tmp")], [])


class ProfiliPerModelloTests(Base):
    def test_profiles_belong_to_each_model_not_to_the_family(self):
        other = gguf(self.downloads / "gemma-3-4b.gguf", "gemma3")       # stessa famiglia
        pf.scegli_slot(self.gemma, 2, self.cfg)
        pf.salva_in_slot(self.gemma, 2, self.cfg)
        data = pf.carica(self.cfg)
        self.assertIn(pf.chiave(self.gemma), data["modelli"])
        self.assertNotIn(pf.chiave(other), data["modelli"])
        self.assertEqual(pf.slot_ricordato(self.gemma, self.cfg), 2)
        self.assertEqual(pf.slot_ricordato(other, self.cfg), 1)

    def test_choose_model_loads_its_own_remembered_slot(self):
        self.save(self.gemma, temperature=0.3)
        pf.assicura(self.cfg)
        pf.salva_in_slot(self.gemma, 1, self.cfg)
        pf.scegli_slot(self.gemma, 3, self.cfg)
        revised = sm.salva_scelta(self.qwen, self.cfg)                   # modello nuovo: slot 1 default
        self.assertEqual(revised.model, str(self.qwen))
        self.assertEqual(revised.temperature, NativeModelConfig().temperature)
        back = sm.salva_scelta(self.gemma, self.cfg)                     # torna: ricorda lo slot 3
        self.assertEqual(pf.slot_ricordato(self.gemma, self.cfg), 3)
        self.assertEqual(back.model, str(self.gemma))

    def test_migration_from_family_profiles_keeps_user_values(self):
        legacy = {"versione": 1, "famiglie": {"qwen": {"ultimo": 2, "slot": {
            "1": pf.default_valori(), "2": {**pf.default_valori(), "temperature": 0.11},
            "3": pf.default_valori()}}}}
        (self.dir / "profili.json").write_text(json.dumps(legacy), encoding="utf-8")
        sm.salva_scelta(self.qwen, self.cfg)
        self.assertEqual(NativeModelConfig.load(self.cfg).temperature, 0.11)

    def test_atomic_save_rolls_back_profiles_when_native_fails(self):
        pf.assicura(self.cfg)
        before = (self.dir / "profili.json").read_text(encoding="utf-8")
        real = pf.os.replace

        def flaky(src, dst, *a, **k):
            if Path(dst).name == "native.json":
                raise OSError("disco pieno")
            return real(src, dst, *a, **k)
        with mock.patch.object(pf.os, "replace", flaky), self.assertRaises(OSError):
            pf.scegli_slot(self.gemma, 2, self.cfg)
        self.assertEqual((self.dir / "profili.json").read_text(encoding="utf-8"), before)
        self.assertEqual([p.name for p in self.dir.glob("*.tmp")], [])
        self.assertEqual(NativeModelConfig.load(self.cfg).model, str(self.gemma))


class UiSourceTests(unittest.TestCase):
    SRC = (Path(__file__).resolve().parents[1] / "local_model" / "miei_modelli.py").read_text(encoding="utf-8")

    def test_slot_number_is_read_before_any_refresh(self):
        body = self.SRC[self.SRC.index("def choose_slot"):self.SRC.index("def save_slot")]
        self.assertLess(body.index("slot_var.get()"), body.index("scegli_slot"))
        self.assertNotIn("profile_refresh()", body)

    def test_add_button_is_locked_while_working(self):
        self.assertIn('add_button.configure(state="disabled" if value else "normal")', self.SRC)
        self.assertIn('if state["busy"]:', self.SRC)
        self.assertNotIn("shutil", self.SRC)


if __name__ == "__main__":
    unittest.main()
