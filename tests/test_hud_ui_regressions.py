"""HUD visual regressions, kept independent of audio/GPT/network operations."""
from pathlib import Path
import os
import unittest

from hud_reference import ReactorArt


class RecordingCanvas:
    def __init__(self):
        self.changed=[]

    def itemconfigure(self,item,**kwargs):
        self.changed.append((item,kwargs))

    def settings(self,item):
        return [args for target,args in self.changed if target==item]


class CenterOnlyColorTests(unittest.TestCase):
    def test_audio_hues_affect_only_nucleus_not_outer_rings_or_raster(self):
        art=ReactorArt()
        c=RecordingCanvas()
        art.canvas=c
        art.geometry=(180,180,140)
        art._glow_photos={"idle":"only-blue-raster"}
        art._glow_photo_item="raster"
        art.core_fill=[("inner","#061729","#144b51")]
        art.rim="rim"
        art.pulse_items=["inner_pulse","core_pulse"]
        art.core_name="name"
        art.arc_items=[("outer_arc",15,3,True)]
        art.system_lamps=["microphone_led","gpt_led","memory_led"]
        art.tick(.5,"listening",connected=True,listening=True)
        listening=dict(c.settings("rim")[-1])
        art.tick(1.2,"speaking",connected=True,listening=True)
        speaking=dict(c.settings("rim")[-1])
        self.assertNotEqual(listening["outline"],speaking["outline"])
        self.assertTrue(all(
            kwargs.get("image")=="only-blue-raster"
            for kwargs in c.settings("raster")))
        self.assertGreaterEqual(len(c.settings("outer_arc")),2)
        self.assertTrue(all(
            set(kwargs)=={"start"} for kwargs in c.settings("outer_arc")))
        self.assertTrue(any("fill" in kwargs for kwargs in c.settings("inner")))

    def test_outer_lamps_depend_on_system_flags_not_audio_color(self):
        art=ReactorArt()
        c=RecordingCanvas()
        art.canvas=c
        art.geometry=(180,180,140)
        art._glow_photos={"idle":"static"}
        art._glow_photo_item="raster"
        art.core_fill=[]
        art.rim="rim"
        art.pulse_items=[]
        art.core_name="name"
        art.arc_items=[]
        art.system_lamps=["mic","gpt","memory"]
        art.tick(.4,"listening",listening=True,connected=True,memory=False)
        before={key:c.settings(key)[-1]["fill"]
                for key in art.system_lamps}
        art.tick(.9,"speaking",listening=True,connected=True,memory=False)
        after={key:c.settings(key)[-1]["fill"]
               for key in art.system_lamps}
        self.assertEqual(before,after)


class BuildLayoutTests(unittest.TestCase):
    def test_single_launcher_still_uses_isolated_profile(self):
        root=Path(__file__).resolve().parent.parent
        self.assertTrue((root/"avvia_jarvis.bat").is_file())
        self.assertFalse((root/"AVVIA_TEST_TELEGRAM50.bat").exists())
        launcher=(root/"avvia_jarvis.bat").read_text(encoding="utf-8")
        self.assertIn("JARVIS_TRIAL_HOME",launcher)
        self.assertIn("prepara_test_telegram50.py",launcher)
        self.assertIn("py -3 jarvis.py",launcher)

    def test_all_metric_tiles_get_equal_grid_columns_when_tk_available(self):
        import tkinter as tk
        from animated_hud import JarvisHUD
        try:
            root=tk.Tk()
        except tk.TclError:
            self.skipTest("No Tk desktop available")
        try:
            root.geometry("1380x820")
            hud=JarvisHUD(root,lambda:None)
            root.update_idletasks()
            canvases=[hud.cpu_tile.canvas,hud.ram_tile.canvas,
                      hud.disk_tile.canvas,hud.network_tile.canvas]
            self.assertEqual(
                [int(tile.grid_info()["column"]) for tile in canvases],
                [0,1,2,3])
            widths=[tile.winfo_width() for tile in canvases]
            self.assertLessEqual(max(widths)-min(widths),2)
            hud.close()
        finally:
            root.destroy()

    def test_diagnostics_not_permanently_packed_or_white(self):
        src=(Path(__file__).resolve().parent.parent/"jarvis.py").read_text(
            encoding="utf-8")
        creation=src.split("diagnostic_row = tk.Frame",1)[1].split(
            "doc_choices =",1)[0]
        self.assertNotIn("diagnostic_row.pack(",creation)
        self.assertNotIn("ttk.Progressbar(diagnostic_row",src)
        self.assertIn('diagnostic_row.pack_forget()',src)
        self.assertIn('text="×"',creation)


if __name__=="__main__":
    unittest.main()
