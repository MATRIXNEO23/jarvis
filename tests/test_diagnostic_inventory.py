"""JRV-AUD-014: bounded source inventory on temporary Windows directories.

Inspected source is never executed. Junction probes only link fixture folders;
no user data, model, network or real profile is inspected.
"""
import os
import ctypes
from ctypes import wintypes
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from self_diagnostics import _source_list, inspect_jarvis, format_audit
from source_review import review_sources


RUNTIME = ("local_model", "file_access", "program_apps", "sveglia", "musica")
SIGNAL = "def controlled():\n    try:\n        work()\n    except Exception:\n        pass\n"


@unittest.skipUnless(os.name == "nt", "Windows-only project requirement")
class DiagnosticInventoryTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        # Windows TEMP can use RUNNER~1 while resolve() expands runneradmin.
        # Match the public inspector's canonical root before comparisons/spies.
        self.base = Path(temporary.name).resolve(strict=True)
        self.root = self.base / "code"
        self.root.mkdir()

    def write(self, relative, text="def safe():\n    return 1\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text,encoding="utf-8")
        return path

    def names(self):
        return [p.relative_to(self.root).as_posix() for p in _source_list(self.root)]

    def test_each_approved_runtime_folder_is_checked_for_syntax(self):
        for module in RUNTIME:
            self.write(module + "/broken.py", "def broken(:\n")
        report = inspect_jarvis(source_root=self.root)
        for module in RUNTIME:
            with self.subTest(module=module):
                self.assertTrue(any(f.startswith(module+"/broken.py: sintassi non valida")
                                    for f in report.findings))

    def test_actual_checkout_runtime_modules_fit_the_unchanged_file_inventory_budget(self):
        checkout=Path(__file__).resolve().parents[1]
        collected=set(_source_list(checkout))
        self.assertLessEqual(len(collected),140)
        for module in RUNTIME:
            with self.subTest(module=module):
                expected=set((checkout/module).glob("*.py"))
                self.assertTrue(expected, "An implemented runtime folder must not silently disappear")
                self.assertTrue(expected.issubset(collected), "Current runtime omitted by inventory budget")

    def test_nested_runtime_source_is_inventoried_and_reviewed(self):
        self.write("local_model/adapters/deeper/worker.py",SIGNAL)
        self.assertIn("local_model/adapters/deeper/worker.py",self.names())
        report=inspect_jarvis(source_root=self.root)
        self.assertTrue(any(r.file=="local_model/adapters/deeper/worker.py"
                            for r in report.recommendations))

    def test_runtime_recommendations_have_file_lines_without_executing_or_echoing_literals(self):
        marker=self.base/"must-not-exist"
        for module in RUNTIME:
            self.write(module+"/engine.py",
                "from pathlib import Path\n"
                + "Path("+repr(str(marker))+").write_text('executed')\n"
                + "PRIVATE = 'DO_NOT_ECHO_LITERAL'\n"+SIGNAL)
        report=inspect_jarvis(source_root=self.root)
        recommendations={r.file:r for r in report.recommendations}
        for module in RUNTIME:
            self.assertIn(module+"/engine.py",recommendations)
            self.assertGreater(recommendations[module+"/engine.py"].line,0)
        self.assertFalse(marker.exists())
        self.assertNotIn("DO_NOT_ECHO_LITERAL",format_audit(report))

    def test_runtime_is_prioritized_over_many_tests_without_increasing_file_limit(self):
        self.write("entry.py")
        for module in RUNTIME:
            self.write(module+"/engine.py")
        for number in range(170):
            self.write(f"tests/test_{number:03}.py")
        names=self.names()
        self.assertEqual(len(names),140)
        for module in RUNTIME:
            self.assertIn(module+"/engine.py",names)
        self.assertEqual(names,self.names())
        first_test=next(n for n,name in enumerate(names) if name.startswith("tests/"))
        self.assertTrue(all(names.index(module+"/engine.py")<first_test for module in RUNTIME))
        report=inspect_jarvis(source_root=self.root)
        self.assertIn("140",report.summary)
        self.assertIn("limit",(report.detail+" "+" ".join(report.findings)).lower())

    def test_directory_traversal_is_bounded_and_reported_even_with_no_source_files(self):
        self.write("entry.py")
        for number in range(160):
            (self.root/f"local_model/folder_{number:03}").mkdir(parents=True)
        visited=[]
        real_iterdir=Path.iterdir
        def iterdir(path):
            visited.append(path)
            return real_iterdir(path)
        with patch.object(Path,"iterdir",iterdir):
            report=inspect_jarvis(source_root=self.root)
        self.assertLessEqual(len(visited),140)
        self.assertIn("limit",(report.detail+" "+" ".join(report.findings)).lower())

    def test_coverage_limit_stays_visible_after_more_than_eight_inventory_errors(self):
        for number in range(10):
            self.write(f"bad_{number:02}.py")
        for number in range(145):
            self.write(f"good_{number:03}.py")
        real_stat=Path.stat
        def stat(path,*args,**kwargs):
            if path.name.startswith("bad_"):
                raise PermissionError("Controlled source metadata denial")
            return real_stat(path,*args,**kwargs)
        with patch.object(Path,"stat",stat):
            report=inspect_jarvis(source_root=self.root)
        self.assertIn("limit",(report.summary+" "+report.detail).lower())
        self.assertIn("140",report.summary)

    def test_missing_module_in_capped_inventory_is_not_claimed_absent_from_program(self):
        for number in range(145):
            self.write(f"good_{number:03}.py")
        self.write("zz_goal.py",SIGNAL)
        report=inspect_jarvis(source_root=self.root,module="zz_goal.py")
        self.assertIn("limit",(report.summary+" "+report.detail).lower())
        self.assertNotIn("non è presente",report.detail)
        self.assertEqual(report.recommendations,())

    def test_nested_profiles_cache_models_upstream_and_hidden_dirs_are_not_entered(self):
        safe=self.write("local_model/engine.py",SIGNAL)
        denied=[]
        for directory in ("addon-data","profiles","cache","__pycache__",".git",
                          "runtime","projects","reports","Downloads","node_modules",
                          ".venv","native_engine","models","upstream-kobold",".private"):
            denied.append(self.write("local_model/"+directory+"/private.py",SIGNAL).parent)
        opened=[]
        real_iterdir=Path.iterdir
        def iterdir(path):
            if path in denied:
                opened.append(path)
                raise AssertionError("Inventory entered excluded fixture data")
            return real_iterdir(path)
        with patch.object(Path,"iterdir",iterdir):
            names=self.names()
            report=inspect_jarvis(source_root=self.root)
        self.assertIn(safe.relative_to(self.root).as_posix(),names)
        self.assertEqual(opened,[])
        self.assertFalse(any("private.py" in name for name in names))
        self.assertTrue(any(r.file=="local_model/engine.py" for r in report.recommendations))

    def test_unapproved_root_folders_never_expand_the_inventory(self):
        self.write("file_access/allowed.py")
        for directory in ("tools","native_engine","Download","arbitrary","addon-data"):
            self.write(directory+"/private.py","def broken(:\n")
        names=self.names()
        self.assertIn("file_access/allowed.py",names)
        self.assertFalse(any("private.py" in name for name in names))

    def test_windows_hidden_attribute_directory_is_not_enumerated_or_read(self):
        self.write("local_model/good.py",SIGNAL)
        private=self.write("local_model/ordinary-name/private.py",SIGNAL)
        hidden=private.parent
        kernel=ctypes.WinDLL("kernel32",use_last_error=True)
        kernel.GetFileAttributesW.argtypes=[wintypes.LPCWSTR]
        kernel.GetFileAttributesW.restype=wintypes.DWORD
        kernel.SetFileAttributesW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD]
        kernel.SetFileAttributesW.restype=wintypes.BOOL
        attributes=kernel.GetFileAttributesW(str(hidden))
        self.assertNotEqual(attributes,0xFFFFFFFF)
        self.assertTrue(kernel.SetFileAttributesW(str(hidden),attributes|0x2))
        self.addCleanup(lambda: kernel.SetFileAttributesW(str(hidden),attributes))
        self.assertTrue(kernel.GetFileAttributesW(str(hidden))&0x2)
        real_iterdir,real_read=Path.iterdir,Path.read_text
        def iterdir(path):
            if path==hidden:
                raise AssertionError("Windows-hidden directory was enumerated")
            return real_iterdir(path)
        def read(path,*args,**kwargs):
            if path==private:
                raise AssertionError("Windows-hidden directory source was read")
            return real_read(path,*args,**kwargs)
        with patch.object(Path,"iterdir",iterdir),patch.object(Path,"read_text",read):
            names=self.names()
            report=inspect_jarvis(source_root=self.root)
            self.assertEqual(review_sources(self.root,[private]),())
        self.assertIn("local_model/good.py",names)
        self.assertNotIn("local_model/ordinary-name/private.py",names)
        self.assertNotIn("private.py",format_audit(report))

    def test_explicit_data_root_inside_runtime_is_pruned_before_listing_or_reading(self):
        self.write("local_model/good.py",SIGNAL)
        private=self.write("local_model/unusual-owner-folder/private.py",SIGNAL)
        data=private.parent
        opened=[]
        real_iterdir,real_read=Path.iterdir,Path.read_text
        def iterdir(path):
            if path==data:
                opened.append(path)
                raise AssertionError("Explicit data root was enumerated")
            return real_iterdir(path)
        def read(path,*args,**kwargs):
            if path==private:
                opened.append(path)
                raise AssertionError("Explicit data file was read")
            return real_read(path,*args,**kwargs)
        with patch.object(Path,"iterdir",iterdir),patch.object(Path,"read_text",read):
            report=inspect_jarvis(source_root=self.root,data_root=data)
        self.assertEqual(opened,[])
        self.assertTrue(any(r.file=="local_model/good.py" for r in report.recommendations))
        self.assertNotIn("private.py",format_audit(report))

    def test_coincident_source_and_data_root_is_reported_without_reading_profile(self):
        self.write("private.py",SIGNAL)
        with patch.object(Path,"read_text",side_effect=AssertionError("Must not read a profile")), \
                patch.object(Path,"iterdir",side_effect=AssertionError("Must not enumerate a profile")):
            report=inspect_jarvis(source_root=self.root,data_root=self.root)
        self.assertIn("Nessun sorgente",report.summary)
        self.assertIn("dati",(report.detail+" "+" ".join(report.findings)).lower())

    def junction(self,link,target):
        result=subprocess.run(["cmd.exe","/d","/c","mklink","/J",str(link),str(target)],
            capture_output=True,text=True,timeout=10,
            creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        if result.returncode:
            self.skipTest("Windows runner cannot create fixture junction; junction coverage incomplete")
        # Remove only the link before TemporaryDirectory cleanup, never target contents.
        self.addCleanup(lambda: link.rmdir() if link.exists() else None)

    def test_real_windows_junction_inside_module_is_not_followed(self):
        self.write("local_model/good.py")
        outside=self.base/"private-fixture"
        outside.mkdir()
        (outside/"secret.py").write_text(SIGNAL,encoding="utf-8")
        link=self.root/"local_model/linked"
        self.junction(link,outside)
        names=self.names()
        self.assertIn("local_model/good.py",names)
        self.assertNotIn("local_model/linked/secret.py",names)
        self.assertEqual((outside/"secret.py").read_text(encoding="utf-8"),SIGNAL)

    def test_static_reviewer_rechecks_physical_containment_through_parent_junction(self):
        (self.root/"local_model").mkdir()
        outside=self.base/"outside-code"
        outside.mkdir()
        (outside/"private.py").write_text(SIGNAL,encoding="utf-8")
        link=self.root/"local_model/linked"
        self.junction(link,outside)
        self.assertEqual(review_sources(self.root,[link/"private.py"]),())

    def test_internal_junction_to_excluded_profile_is_not_listed_or_read(self):
        self.write("local_model/good.py",SIGNAL)
        private=self.write("profiles/private.py",SIGNAL)
        profile=private.parent
        link=self.root/"local_model/linked-profile"
        self.junction(link,profile)
        real_iterdir,real_read=Path.iterdir,Path.read_text
        opened=[]
        def iterdir(path):
            if path in (profile,link):
                opened.append(path)
                raise AssertionError("Internal profile junction was enumerated")
            return real_iterdir(path)
        def read(path,*args,**kwargs):
            if path.resolve()==private.resolve():
                opened.append(path)
                raise AssertionError("Internal profile junction was read")
            return real_read(path,*args,**kwargs)
        with patch.object(Path,"iterdir",iterdir),patch.object(Path,"read_text",read):
            names=self.names()
            report=inspect_jarvis(source_root=self.root)
            self.assertEqual(review_sources(self.root,[link/"private.py"]),())
        self.assertIn("local_model/good.py",names)
        self.assertEqual(opened,[])
        self.assertNotIn("private.py",format_audit(report))

    def test_internal_junction_alias_to_allowed_code_is_not_traversed_again(self):
        self.write("local_model/owned.py",SIGNAL)
        (self.root/"file_access").mkdir()
        link=self.root/"file_access/alias"
        target=self.root/"local_model"
        self.junction(link,target)
        real_iterdir=Path.iterdir
        target_visits=[]
        def iterdir(path):
            if path==link:
                raise AssertionError("Internal source junction was followed")
            if path==target:
                target_visits.append(path)
            return real_iterdir(path)
        with patch.object(Path,"iterdir",iterdir):
            names=self.names()
        self.assertEqual(target_visits,[target])
        self.assertIn("local_model/owned.py",names)
        self.assertNotIn("file_access/alias/owned.py",names)
        self.assertEqual(review_sources(self.root,[link/"owned.py"]),())

    def test_one_unreadable_runtime_directory_does_not_abort_other_modules(self):
        self.write("local_model/blocked.py")
        self.write("program_apps/good.py",SIGNAL)
        blocked=self.root/"local_model"
        real_iterdir=Path.iterdir
        def iterdir(path):
            if path==blocked:
                raise PermissionError("Controlled fixture directory denial")
            return real_iterdir(path)
        with patch.object(Path,"iterdir",iterdir):
            report=inspect_jarvis(source_root=self.root)
        self.assertTrue(any(r.file=="program_apps/good.py" for r in report.recommendations))
        self.assertIn("local_model",report.detail+" "+" ".join(report.findings))
        self.assertIn("disponibil",(report.detail+" "+" ".join(report.findings)).lower())

    def test_static_reviewer_contains_stat_or_symlink_metadata_read_failure(self):
        file=self.write("entry.py",SIGNAL)
        real_stat=Path.stat
        denied=[]
        def stat(path,*args,**kwargs):
            if path==file:
                denied.append(path)
                raise PermissionError("Controlled metadata denial")
            return real_stat(path,*args,**kwargs)
        with patch.object(Path,"stat",stat):
            self.assertEqual(review_sources(self.root,[file]),())
        self.assertTrue(denied,"The metadata denial must actually be exercised")

    def test_windows_short_alias_root_keeps_runtime_coverage_and_profile_exclusion(self):
        self.write("local_model/good.py",SIGNAL)
        private=self.write("local_model/owner-data/private.py",SIGNAL)
        kernel=ctypes.WinDLL("kernel32",use_last_error=True)
        kernel.GetShortPathNameW.argtypes=[wintypes.LPCWSTR,wintypes.LPWSTR,wintypes.DWORD]
        kernel.GetShortPathNameW.restype=wintypes.DWORD
        buffer=ctypes.create_unicode_buffer(32768)
        length=kernel.GetShortPathNameW(str(self.root),buffer,len(buffer))
        self.assertGreater(length,0)
        self.assertLess(length,len(buffer))
        short=Path(buffer.value)
        if short==self.root:
            self.skipTest("No distinct8.3alias on this Windows volume; short-name coverage incomplete")
        self.assertEqual(short.resolve(strict=True),self.root)
        canonical=inspect_jarvis(source_root=self.root,data_root=private.parent)
        aliased=inspect_jarvis(source_root=short,data_root=short/"local_model/owner-data")
        self.assertEqual(canonical.summary,aliased.summary)
        self.assertEqual(canonical.findings,aliased.findings)
        self.assertEqual(canonical.recommendations,aliased.recommendations)
        self.assertTrue(any(r.file=="local_model/good.py" for r in aliased.recommendations))
        self.assertNotIn("private.py",format_audit(aliased))

    def test_file_disappearing_before_recommendation_phase_does_not_abort_diagnosis(self):
        file=self.write("entry.py",SIGNAL)
        def progress(phase,index,total):
            if phase=="consigli" and index==0:
                file.unlink(missing_ok=True)
        report=inspect_jarvis(source_root=self.root,progress=progress)
        self.assertFalse(file.exists())
        self.assertEqual(report.recommendations,())

    def test_existing_byte_budget_is_enforced_before_reading_nested_source(self):
        large=self.write("local_model/large.py","x"*260001)
        real_read=Path.read_text
        reads=[]
        def read(path,*args,**kwargs):
            if path==large:
                reads.append(path)
                raise AssertionError("Oversized source must not be read")
            return real_read(path,*args,**kwargs)
        with patch.object(Path,"read_text",read):
            report=inspect_jarvis(source_root=self.root)
        self.assertEqual(reads,[])
        self.assertTrue(any(f.startswith("local_model/large.py: troppo grande") for f in report.findings))

    def test_simple_root_module_selection_and_traversal_rejection_remain_unchanged(self):
        self.write("entry.py",SIGNAL)
        self.write("local_model/entry.py",SIGNAL)
        report=inspect_jarvis(source_root=self.root,module="entry.py")
        self.assertTrue(report.recommendations)
        self.assertTrue(all(r.file=="entry.py" for r in report.recommendations))
        self.assertNotIn("local_model/entry.py",format_audit(report))
        with self.assertRaises(ValueError):
            inspect_jarvis(source_root=self.root,module="../private.py")


if __name__=="__main__":
    unittest.main()
