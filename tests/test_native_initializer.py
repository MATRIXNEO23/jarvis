"""F5N.5: initializer must not read the host process command line.

KoboldCpp 6d2fedf added ``launch_args = parser.parse_args()`` inside its
``__main__`` block, which Jarvis executes (without ``main()``). Under Jarvis
or a probe started with arguments, sys.argv belongs to the host process.
"""
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

from local_model.native_initializer import initialize_kobold_cpu

FAKE_UPSTREAM = '''
import argparse
calls = []
def init_library():
    calls.append(("init", args.threads, args.contextsize, args.noavx2))
def get_cli_arg_overrides(parser):
    return set(vars(parser.parse_args()))
def main(launch_args=None):
    raise AssertionError("main must never run inside Jarvis")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--usecpu", action="store_true")
    parser.add_argument("--noavx2", action="store_true")
    parser.add_argument("--gpulayers", type=int, default=0)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--blasthreads", type=int, default=1)
    parser.add_argument("--contextsize", type=int, default=2048)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("model_param", nargs="?")
    parser.add_argument("port_param", nargs="?", type=int, default=5001)
    launch_args = parser.parse_args()
    cli_arg_overrides = get_cli_arg_overrides(parser)
    main(launch_args=launch_args)
'''


class NativeInitializerArgvTests(unittest.TestCase):
    def _run(self, argv):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "koboldcpp.py"
            source.write_text(FAKE_UPSTREAM, encoding="utf-8")
            dll = Path(temp) / "koboldcpp_noavx2.dll"
            dll.write_bytes(b"MZ")
            upstream = ModuleType("jarvis_native_kobold_pinned")
            exec(compile(FAKE_UPSTREAM, str(source), "exec"), upstream.__dict__)
            config = SimpleNamespace(dll=str(dll), threads=3, batch_threads=2,
                                     context_size=1024)
            with mock.patch.object(sys, "argv", list(argv)):
                initialize_kobold_cpu(upstream, config, source)
                after = list(sys.argv)
            return upstream, after

    def test_host_arguments_do_not_reach_upstream_parser(self):
        # Same shape as tools/probe_jarvis014_native.py <root> <model>.
        argv = ["probe.py", "upstream-kobold", "probe-model.gguf"]
        upstream, after = self._run(argv)
        self.assertEqual(upstream.calls, [("init", 3, 1024, True)])
        self.assertEqual(after, argv)
        self.assertEqual(upstream.maxctx, 1024)

    def test_host_argv_restored_even_when_bootstrap_fails(self):
        argv = ["jarvis.py", "--unknown-jarvis-flag"]
        broken = FAKE_UPSTREAM.replace("launch_args = parser.parse_args()",
                                       "raise RuntimeError('bootstrap')")
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "koboldcpp.py"
            source.write_text(broken, encoding="utf-8")
            dll = Path(temp) / "koboldcpp_noavx2.dll"
            dll.write_bytes(b"MZ")
            upstream = ModuleType("k")
            exec(compile(broken, str(source), "exec"), upstream.__dict__)
            config = SimpleNamespace(dll=str(dll), threads=2, batch_threads=2,
                                     context_size=1024)
            with mock.patch.object(sys, "argv", list(argv)):
                with self.assertRaisesRegex(RuntimeError, "bootstrap"):
                    initialize_kobold_cpu(upstream, config, source)
                self.assertEqual(sys.argv, argv)


if __name__ == "__main__":
    unittest.main()
