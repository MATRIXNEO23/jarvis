"""CPU runtime contracts; Windows only, no model or external inference."""
import os
from pathlib import Path
import tempfile
import unittest
from local_model.runtime import LocalConfig

@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class LocalRuntimeConfigTests(unittest.TestCase):
    def test_cpu_command_is_loopback_noavx2_and_no_browser(self):
        c=LocalConfig(executable='C:/Kobold/koboldcpp.exe',model='C:/Models/gemma.gguf')
        self.assertEqual(c.command(),[c.executable,'--model',c.model,'--usecpu','--noavx2',
            '--host','127.0.0.1','--port','5002','--threads','2','--blasthreads','2',
            '--contextsize','2048','--skiplauncher'])
    def test_custom_threads_and_context_survive_save_reload(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'config.json'
            c=LocalConfig(executable='C:/Kobold/koboldcpp.exe',model='C:/Models/gemma.gguf',threads=4,context=4096)
            c.save(p)
            self.assertEqual(LocalConfig.load(p),c)
    def test_invalid_resource_values_rejected_before_launch(self):
        for kw in ({'threads':0},{'threads':True},{'context':12},{'output':9000},{'port':80}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                LocalConfig(**kw).validate()
    def test_missing_or_corrupt_configuration_does_not_erase_user_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'config.json';p.write_text('{broken')
            with self.assertRaises(ValueError):
                LocalConfig.load(p)
            self.assertEqual(p.read_text(),'{broken')
