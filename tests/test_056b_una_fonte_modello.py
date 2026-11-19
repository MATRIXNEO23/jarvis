"""056b: una sola fonte del modello in uso (native.json.model): scegliere Qwen3 dall'elenco
cambia campo, template e configurazione mostrata; il modulo «Configura» non lo riscrive vecchio."""
import struct
import tempfile
import unittest
from pathlib import Path

from local_model import scelta_modello
from local_model.chat_templates import model_family
from local_model.native_config import NativeModelConfig

ROOT = Path(__file__).resolve().parents[1]


def gguf(path, arch):
    body = b"GGUF" + struct.pack("<IQQ", 3, 0, 1) + struct.pack("<Q", 20) + b"general.architecture" + struct.pack("<IQ", 8, len(arch)) + arch.encode()
    path.write_bytes(body + b"x" * 100)
    return path


class UnaFonteTests(unittest.TestCase):
    def test_scelta_qwen3_aggiorna_campo_template_e_configurazione(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            gemma = gguf(tmp / "gemma-2-2b.gguf", "gemma2")
            qwen = gguf(tmp / "Qwen3-1.7B-Q4_K_M.gguf", "qwen3")
            config = tmp / "native.json"
            NativeModelConfig(model=str(gemma)).save(config)
            self.assertEqual(Path(scelta_modello.modello_in_uso(config)).name, gemma.name)
            scelta_modello.salva_scelta(qwen, config)
            self.assertEqual(Path(NativeModelConfig.load(config).model).name, qwen.name)   # native.json.model
            self.assertEqual(Path(scelta_modello.modello_in_uso(config)).name, qwen.name)  # elenco e caselle
            self.assertEqual(model_family(NativeModelConfig.load(config).model), "qwen3")  # template
            shown = NativeModelConfig.load(config)                                  # «Configura»
            self.assertEqual(Path(shown.model).name, qwen.name)

    def test_il_modulo_configura_si_riallinea_prima_di_salvare(self):
        src = (ROOT / "local_model" / "native_ui.py").read_text(encoding="utf-8")
        corpo = src[src.index("def save(self):"):src.index("changes = {")]
        self.assertIn("if self.sync_modello():", corpo)
        self.assertIn("<FocusIn>", src)

    def test_configura_salva_anche_nel_profilo_del_modello_in_uso(self):
        src = (ROOT / "local_model" / "native_ui.py").read_text(encoding="utf-8")
        self.assertIn("profili_famiglia.salva_in_slot(", src)
        self.assertIn("slot_ricordato(revised.model", src)

    def test_scegliere_copia_in_native_json_i_valori_del_profilo(self):
        from local_model import profili_famiglia
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            a = gguf(tmp / "a.gguf", "gemma2")
            b = gguf(tmp / "b.gguf", "qwen3")
            config = tmp / "native.json"
            NativeModelConfig(model=str(a), context_size=1024, max_output=96).save(config)
            scelta_modello.salva_scelta(b, config)
            profili_famiglia.salva_in_slot(b, 1, config)     # «Configura» in b
            scelta_modello.salva_scelta(a, config)
            self.assertEqual(NativeModelConfig.load(config).max_output, 96)   # valori di a
            scelta_modello.salva_scelta(b, config)
            loaded = NativeModelConfig.load(config)
            self.assertEqual(Path(loaded.model).name, "b.gguf")

    def test_nessuna_seconda_fonte_nei_profili(self):
        src = (ROOT / "local_model" / "profili_famiglia.py").read_text(encoding="utf-8")
        self.assertIn('{"model": str(model_path)', src)       # applica_modello scrive native.json
        self.assertNotIn("modello_in_uso_profili", src)


if __name__ == "__main__":
    unittest.main()
