"""Actual packager selection; no builder execution or archive generation."""
import ast
from contextlib import chdir
import os
from pathlib import Path
import re
import tempfile
import unittest


GUIDES = ('docs/VOCE_OFFLINE.md', 'docs/RECUPERO-IMPOSTAZIONI.md',
          'file_access/LEGGIMI.md', 'program_apps/LEGGIMI.md')


def selector():
    tree = ast.parse(Path('tools/build_gemma_clean_trial.py').read_text(encoding='utf-8'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'include')
    namespace = {'Path': Path}
    exec(compile(ast.Module(body=[function], type_ignores=[]), 'actual-package-selector', 'exec'), namespace)
    return namespace['include']


@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class OperationalGuideSelectionTests(unittest.TestCase):
    def test_four_required_operational_guides_are_selected(self):
        include = selector()
        with tempfile.TemporaryDirectory(prefix='jarvis-guides-') as temporary:
            root = Path(temporary)
            for name in GUIDES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('Fixture operativa', encoding='utf-8')
            with chdir(root):
                for name in GUIDES:
                    with self.subTest(guide=name):
                        self.assertTrue(include(Path(name)), 'Required guide excluded: '+name)

    def test_guide_exception_does_not_include_development_or_private_fixtures(self):
        include = selector()
        excluded = ('docs/HANDOFF.md', 'docs/evidence/private.json', 'docs/other.md',
                    'tools/helper.py', 'tests/test_private.py', 'Download/old.zip',
                    'upstream-kobold/koboldcpp.py', '.github/workflows/tests.yml',
                    'AGENTS.md', 'RECUPERO.md', 'file_access/development.md')
        with tempfile.TemporaryDirectory(prefix='jarvis-guide-exclusions-') as temporary:
            root = Path(temporary)
            for name in (*excluded, 'README.md', 'jarvis.py'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('Fixture only', encoding='utf-8')
            with chdir(root):
                for name in excluded:
                    with self.subTest(path=name):
                        self.assertFalse(include(Path(name)), name)
                self.assertTrue(include(Path('README.md')))
                self.assertTrue(include(Path('jarvis.py')))

    def test_installer_remedy_and_relative_guide_links_are_shipped(self):
        include = selector()
        root = Path.cwd().resolve()
        installer = Path('installa_voce.bat').read_text(encoding='utf-8')
        remedies = re.findall(r'docs[\\/]([A-Za-z0-9_-]+\.md)', installer)
        self.assertTrue(remedies, 'Installer must retain a local troubleshooting remedy')
        for name in remedies:
            target = Path('docs') / name
            self.assertTrue(target.is_file(), str(target))
            self.assertTrue(include(target), 'Installer points to excluded guide: '+str(target))
        for guide in GUIDES:
            self.assertTrue(Path(guide).is_file(), guide)
            for link in re.findall(r'\]\(([^)]+)\)', Path(guide).read_text(encoding='utf-8')):
                if '://' in link or link.startswith('#'):
                    continue
                target = (root / guide).parent.joinpath(link.split('#')[0]).resolve()
                relative = target.relative_to(root)
                self.assertTrue(target.is_file(), str(relative))
                self.assertTrue(include(relative), 'Local guide link excluded: '+str(relative))
