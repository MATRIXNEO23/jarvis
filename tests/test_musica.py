"""Add-on Musica: frasi, ricerca nella cartella, YouTube nel browser, lettore, dati."""
import json
import tempfile
import time
import unittest
from pathlib import Path

from musica import config, library
from musica.commands import parse_command
from musica.player import MusicPlayer
from musica.service import MusicService
from musica.youtube import first_video_url, results_url, url_for


class CommandTests(unittest.TestCase):
    def test_play_and_controls(self):
        self.assertEqual(parse_command("Lumi, metti Bohemian Rhapsody"), ("play", "Bohemian Rhapsody"))
        self.assertEqual(parse_command("fammi sentire la musica di Vasco"), ("play", "Vasco"))
        self.assertEqual(parse_command("pausa"), ("pause", ""))
        self.assertEqual(parse_command("metti in pausa"), ("pause", ""))
        self.assertEqual(parse_command("riprendi"), ("resume", ""))
        self.assertEqual(parse_command("ferma la musica"), ("stop", ""))
        self.assertEqual(parse_command("prossima canzone"), ("next", ""))
        self.assertEqual(parse_command("abbassa il volume della musica"), ("volume_down", ""))
        self.assertEqual(parse_command("torna indietro"), ("prev", ""))
        self.assertEqual(parse_command("avanti"), ("next", ""))
        self.assertEqual(parse_command("indietro"), ("prev", ""))
        self.assertEqual(parse_command("stop"), ("stop", ""))
        self.assertEqual(parse_command("play"), ("resume", ""))
        self.assertEqual(parse_command("Lumi, pausa"), ("pause", ""))
        self.assertEqual(parse_command("brano precedente"), ("prev", ""))

    def test_other_features_are_not_taken(self):
        for text in ("metti un timer di 5 minuti", "metti la sveglia alle 7", "metti il film Matrix",
                     "metti la serie Dark", "apri chrome", "che ore sono", "metti il volume a 50"):
            self.assertIsNone(parse_command(text), text)


class LibraryTests(unittest.TestCase):
    def test_scan_and_best_match(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "Queen").mkdir()
            for name in ("Queen/Bohemian Rhapsody.mp3", "Queen/Don't Stop Me Now.mp3",
                         "Imagine - John Lennon.wav", "note.txt"):
                (root / name).write_bytes(b"x")
            tracks = library.scan(root)
            self.assertEqual(len(tracks), 3)          # note.txt escluso
            self.assertEqual(library.best_matches(tracks, "bohemian rhapsody")[0].stem,
                             "Bohemian Rhapsody")
            self.assertEqual(len(library.best_matches(tracks, "queen")), 2)   # cartella artista
            self.assertEqual(library.best_matches(tracks, "lennon")[0].suffix, ".wav")
            self.assertEqual(library.best_matches(tracks, "nirvana"), [])
            self.assertEqual(library.scan(""), [])


class FakePlayer:
    def __init__(self):
        self.calls, self.state, self.volume, self.playlist = [], "stopped", 70, []

    @property
    def title(self):
        return self.playlist[0].stem if self.playlist else ""

    def play(self, tracks, start=0):
        self.calls.append(("play", [t.name for t in tracks]))
        self.playlist, self.state = list(tracks), "playing"

    def pause(self):
        self.calls.append(("pause",))
        self.state = "paused"

    def resume(self):
        self.calls.append(("resume",))
        self.state = "playing"

    def stop(self):
        self.calls.append(("stop",))
        self.state = "stopped"

    def next(self):
        self.calls.append(("next",))

    def prev(self):
        self.calls.append(("prev",))

    def set_volume(self, value):
        self.calls.append(("volume", value))

    def close(self):
        pass


class ServiceTests(unittest.TestCase):
    def make(self, folder, enabled=True, key=""):
        opened, keys = [], []
        service = MusicService(lambda: enabled, open_url=opened.append, player=FakePlayer(),
                               data_folder=Path(folder) / "data",
                               url_for=lambda q, k: (results_url(q), "risultati"),
                               media_key=lambda a: keys.append(a) or True)
        service.api_key = lambda: key
        return service, opened, keys

    def test_local_track_plays_inside_lumi(self):
        with tempfile.TemporaryDirectory() as folder:
            music = Path(folder) / "musica"
            music.mkdir()
            (music / "Imagine.mp3").write_bytes(b"x")
            service, opened, _ = self.make(folder)
            service.configure(str(music), None)
            self.assertEqual(service.handle("play", "imagine"), "Metto Imagine.")
            self.assertEqual(service.snapshot()["mode"], "local")
            self.assertEqual(service.handle("pause"), "Pausa.")
            self.assertEqual(service.handle("stop"), "Musica fermata.")
            self.assertEqual(opened, [])
            saved = json.loads((Path(folder) / "data" / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["folder"], str(music))

    def test_missing_track_opens_youtube_and_controls_use_media_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            service, opened, keys = self.make(folder)
            self.assertIn("YouTube", service.handle("play", "bohemian rhapsody"))
            for _ in range(50):
                if opened:
                    break
                time.sleep(0.01)
            self.assertEqual(opened, ["https://www.youtube.com/results?search_query=bohemian+rhapsody"])
            service.handle("pause")
            service.handle("next")
            self.assertEqual(keys, ["toggle", "next"])

    def test_disabled_addon_does_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            service, opened, _ = self.make(folder, enabled=False)
            self.assertIn("spento", service.handle("play", "imagine"))
            self.assertEqual(opened, [])


class FakePanel:
    def __init__(self):
        self.sent, self.started, self.closed, self.state, self.position = [], [], 0, "playing", 0.0
        self.on_event = None

    def start(self, hwnd):
        self.started.append(hwnd)

    def send(self, **command):
        self.sent.append(command)
        return True

    def file(self, path):
        return self.send(cmd="file", path=str(path))

    def youtube(self, video_id):
        return self.send(cmd="youtube", id=video_id)

    def close(self):
        self.closed += 1


class VideoTests(unittest.TestCase):
    def make(self, folder, key="", video_id=lambda q, k: "abcDEF12345"):
        panel, opened = FakePanel(), []
        self.files = []
        service = MusicService(lambda: True, open_url=opened.append, player=FakePlayer(),
                               data_folder=Path(folder) / "data",
                               url_for=lambda q, k: (results_url(q), "risultati"),
                               media_key=lambda a: True, video_id_for=video_id, video_panel=panel,
                               open_file=self.files.append)
        service.video_hwnd = 1234
        service.api_key = lambda: key
        return service, panel, opened

    def wait(self, condition):
        for _ in range(100):
            if condition():
                return True
            time.sleep(0.01)
        return False

    def test_folder_video_plays_in_panel_then_next_on_end_and_stop_frees_ram(self):
        with tempfile.TemporaryDirectory() as folder:
            music = Path(folder) / "m"
            music.mkdir()
            for name in ("Concerto 1.mp4", "Concerto 2.mp4"):
                (music / name).write_bytes(b"x")
            service, panel, _ = self.make(folder)
            service.configure(str(music), None)
            self.assertEqual(service.handle("play", "concerto"), "Metto Concerto 1.")
            self.assertEqual(panel.started, [1234])
            self.assertEqual(panel.sent[-1]["cmd"], "file")
            panel.on_event({"ev": "state", "state": "ended"})
            self.assertTrue(panel.sent[-1]["path"].endswith("Concerto 2.mp4"))
            service.set_volume(30)
            self.assertIn({"cmd": "volume", "value": 30}, panel.sent)
            self.assertEqual(service.handle("stop"), "Musica fermata.")
            self.assertEqual(panel.closed, 1)
            self.assertIsNone(service.snapshot()["mode"])

    def test_reduce_video_keeps_music_and_youtube_keeps_minimum_size(self):
        with tempfile.TemporaryDirectory() as folder:
            music = Path(folder) / "m"
            music.mkdir()
            (music / "Live.mp4").write_bytes(b"x")
            service, panel, _ = self.make(folder, key="KEY")
            service.configure(str(music), None)
            service.handle("play", "live")
            self.assertIn("solo la musica", service.toggle_video_visible())
            self.assertFalse(service.snapshot()["video_visible"])
            self.assertEqual(panel.closed, 0)                 # l'audio continua
            self.assertEqual(service.snapshot()["mode"], "video")
            service.video_items = [("youtube", "abcDEF12345", "queen")]
            service.video_index = 0
            service.video_hidden = False
            self.assertIn("riquadrino", service.toggle_video_visible())
            self.assertTrue(service.snapshot()["video_mini"])          # YouTube: 200x200
            self.assertIn("ripristinato", service.toggle_video_visible())

    def test_unsupported_formats_open_with_windows_player(self):
        with tempfile.TemporaryDirectory() as folder:
            music = Path(folder) / "m"
            music.mkdir()
            (music / "Vecchio.avi").write_bytes(b"x")
            (music / "Nuovo.mp4").write_bytes(b"x")
            service, panel, _ = self.make(folder)
            service.configure(str(music), None)
            self.assertIn("lettore di Windows", service.handle("play", "vecchio"))
            self.assertEqual([p.name for p in self.files], ["Vecchio.avi"])
            service.handle("play", "nuovo")
            panel.on_event({"ev": "error", "code": "file", "detail": 4})   # codec non supportato
            self.assertEqual([p.name for p in self.files], ["Vecchio.avi", "Nuovo.mp4"])

    def test_prev_restarts_after_three_seconds(self):
        with tempfile.TemporaryDirectory() as folder:
            music = Path(folder) / "m"
            music.mkdir()
            for name in ("A.mp4", "B.mp4"):
                (music / name).write_bytes(b"x")
            service, panel, _ = self.make(folder)
            service.configure(str(music), None)
            service.play_tracks(service.tracks(), 0)
            service.handle("next")
            panel.position = 10
            self.assertEqual(service.handle("prev"), "Dall'inizio.")
            panel.position = 1
            self.assertEqual(service.handle("prev"), "Metto A.")

    def test_youtube_with_key_plays_in_panel_and_unembeddable_goes_to_browser(self):
        with tempfile.TemporaryDirectory() as folder:
            service, panel, opened = self.make(folder, key="KEY")
            self.assertEqual(service.handle("play", "queen"), "Cerco «queen» su YouTube.")
            self.assertTrue(self.wait(lambda: panel.sent and panel.sent[-1].get("cmd") == "youtube"))
            self.assertEqual(panel.sent[-1]["id"], "abcDEF12345")
            panel.on_event({"ev": "error", "code": 150})
            self.assertEqual(opened, ["https://www.youtube.com/watch?v=abcDEF12345"])

    def test_without_key_or_panel_youtube_opens_in_browser(self):
        with tempfile.TemporaryDirectory() as folder:
            service, panel, opened = self.make(folder, key="")
            self.assertIn("browser", service.handle("play", "queen"))
            self.assertTrue(self.wait(lambda: opened))
            self.assertEqual(panel.started, [])


class YoutubeTests(unittest.TestCase):
    def test_api_first_video_and_fallback(self):
        class Response:
            def __init__(self, body):
                self.body = body
            def read(self, _n):
                return self.body
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
        good = lambda url, timeout: Response(json.dumps(
            {"items": [{"id": {"videoId": "fJ9rUzIMcZQ"}}]}).encode())
        self.assertEqual(first_video_url("queen", "KEY", opener=good),
                         "https://www.youtube.com/watch?v=fJ9rUzIMcZQ")
        def broken(url, timeout):
            raise OSError("quota")
        self.assertEqual(url_for("queen", "KEY", opener=broken),
                         (results_url("queen"), "risultati"))
        self.assertEqual(url_for("queen", "", opener=good)[1], "risultati")


class ConfigTests(unittest.TestCase):
    def test_api_key_is_stored_protected_and_removable(self):
        flip = lambda data, encrypt: bytes(b ^ 0x5A for b in data)
        with tempfile.TemporaryDirectory() as folder:
            config.save_api_key(" AIza-Test_123 ", Path(folder), protect=flip)
            raw = (Path(folder) / "youtube-key.dpapi").read_bytes()
            self.assertNotIn(b"AIza", raw)
            self.assertEqual(config.load_api_key(Path(folder), protect=flip), "AIza-Test_123")
            config.save_api_key("", Path(folder), protect=flip)
            self.assertEqual(config.load_api_key(Path(folder), protect=flip), "")


class PlayerTests(unittest.TestCase):
    def test_plays_next_track_when_one_ends_and_skips_unreadable(self):
        log, modes = [], iter(["stopped"] * 100)
        def mci(command):
            log.append(command)
            if command.startswith('open "') and "rotto" in command:
                return 263, ""
            if command.endswith(" mode"):
                return 0, next(modes)
            return 0, ""
        states = []
        player = MusicPlayer(on_state=states.append, mci=mci)
        player.play([Path("a.mp3"), Path("rotto.mp3"), Path("b.mp3")])
        for _ in range(100):
            if states and states[-1]["state"] == "stopped" and any("b.mp3" in c for c in log):
                break
            time.sleep(0.05)
        player.close()
        opened = [c for c in log if c.startswith("open")]
        self.assertEqual([c.split('"')[1] for c in opened], ["a.mp3", "rotto.mp3", "b.mp3"])
        self.assertTrue(any(c.startswith("setaudio") for c in log))


class RuntimeTests(unittest.TestCase):
    def tearDown(self):
        from musica import runtime
        runtime.register(None)

    def test_unregistered_or_disabled_does_nothing_and_programs_keep_priority(self):
        from musica import runtime
        lines = []
        self.assertFalse(runtime.handle_text("metti Imagine", lines.append, lines.append))
        with tempfile.TemporaryDirectory() as folder:
            service, opened, _ = ServiceTests.make(ServiceTests(), folder)
            runtime.register(service, lambda text: object() if "netflix" in text.lower() else None)
            self.assertFalse(runtime.handle_text("metti Netflix", lines.append, lines.append))
            self.assertFalse(runtime.handle_text("che ore sono", lines.append, lines.append))
            self.assertFalse(runtime.handle_text("stop", lines.append, lines.append))  # niente in corso
            service.mode = "browser"
            self.assertTrue(runtime.handle_text("pausa", lines.append, lines.append))


class ManifestTests(unittest.TestCase):
    def test_bundled_manifest_is_valid_and_local_only(self):
        from addon_manager import validate_manifest
        data = json.loads(Path("musica/Musica.jaddon").read_text(encoding="utf-8"))
        manifest = validate_manifest(data)
        self.assertEqual(manifest["actions"][0]["core_action"], "music.local")
        bad = dict(data, id="altro")
        bad["actions"] = [dict(data["actions"][0], id="addon.altro.riproduci")]
        with self.assertRaises(Exception):
            validate_manifest(bad)


if __name__ == "__main__":
    unittest.main()


class MultiFolderTests(unittest.TestCase):
    def test_old_single_folder_config_is_migrated_and_list_saved(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            (base / "config.json").write_text(json.dumps({"folder": "C:/Musica", "volume": 40}),
                                              encoding="utf-8")
            data = config.load(base)
            self.assertEqual(data["folders"], ["C:/Musica"])
            self.assertEqual(data["volume"], 40)
            config.save({"folders": ["C:/A", "C:/A", "", "C:/B"], "volume": 40}, base)
            saved = json.loads((base / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["folders"], ["C:/A", "C:/B"])
            self.assertEqual(saved["folder"], "C:/A")

    def test_several_folders_with_subfolders_and_tree(self):
        from musica import library
        with tempfile.TemporaryDirectory() as folder:
            a, b = Path(folder) / "A", Path(folder) / "B"
            (a / "Rock" / "Live").mkdir(parents=True)
            b.mkdir()
            (a / "Rock" / "Live" / "One.mp3").write_bytes(b"x")
            (a / "Rock" / "Two.mp3").write_bytes(b"x")
            (b / "Three.mp3").write_bytes(b"x")
            service, _o, _k = ServiceTests.make(ServiceTests(), folder)
            self.assertEqual(service.configure([str(a), str(b), str(a / "Rock")], None), 3)
            self.assertEqual(service.handle("play", "three"), "Metto Three.")
            self.assertEqual(library.root_of(a / "Rock" / "Two.mp3", service.folders()),
                             str(a / "Rock"))
            roots, dirs = library.folder_tree(service.tracks(), service.folders())
            # Cartella scritta in altra forma (barra finale, «.»): la radice si apre lo stesso.
            other = [str(a / "Rock") + "/", str(b) + "/."]
            roots2, dirs2 = library.folder_tree(service.tracks(), other)
            self.assertTrue(all(dirs2.get(r) for r in roots2))
            self.assertEqual(set(roots), {str(a / "Rock"), str(b)})
            self.assertEqual(dirs[str(a / "Rock")]["subdirs"], [str(a / "Rock" / "Live")])
            self.assertEqual([t.stem for t in library.tracks_under(dirs, str(a / "Rock"))],
                             ["Two", "One"])


class QueueAndPlaylistTests(unittest.TestCase):
    def test_voice_commands_for_queue_and_playlist(self):
        self.assertEqual(parse_command("Lumi, aggiungi in coda Imagine"), ("queue", "Imagine"))
        self.assertEqual(parse_command("metti in coda bohemian rhapsody"), ("queue", "bohemian rhapsody"))
        self.assertEqual(parse_command("aggiungi Imagine alla coda"), ("queue", "Imagine"))
        self.assertEqual(parse_command("metti la playlist Viaggio"), ("playlist", "Viaggio"))
        self.assertEqual(parse_command("metti Imagine"), ("play", "Imagine"))
        self.assertEqual(parse_command("metti in pausa"), ("pause", ""))

    def test_queue_adds_without_stopping_and_playlists_persist(self):
        with tempfile.TemporaryDirectory() as folder:
            music = Path(folder) / "m"
            music.mkdir()
            for name in ("Imagine.mp3", "Yesterday.mp3", "Clip.mp4"):
                (music / name).write_bytes(b"x")
            service, _o, _k = ServiceTests.make(ServiceTests(), folder)
            added = []
            service.player.add = lambda tracks: added.extend(t.name for t in tracks)
            service.configure(str(music), None)
            # Niente in riproduzione: «in coda» fa partire il brano.
            self.assertEqual(service.handle("queue", "imagine"), "Metto Imagine.")
            self.assertEqual(service.handle("queue", "yesterday"), "Aggiunto in coda: Yesterday.")
            self.assertEqual(added, ["Yesterday.mp3"])
            self.assertIn("solo brani audio", service.enqueue([music / "Clip.mp4"]))
            self.assertIn("Non trovo", service.handle("queue", "zzz"))
            # Playlist: salvata nel profilo, si suona per nome, eliminarla non tocca i file.
            self.assertIn("2 aggiunti", service.add_to_playlist("Viaggio", [music / "Imagine.mp3",
                                                                           music / "Yesterday.mp3"]))
            self.assertIn("0 aggiunti", service.add_to_playlist("Viaggio", [music / "Imagine.mp3"]))
            self.assertEqual(config.load_playlists(Path(folder) / "data")["Viaggio"],
                             [str(music / "Imagine.mp3"), str(music / "Yesterday.mp3")])
            self.assertEqual(service.handle("playlist", "viaggio"), "Metto Imagine.")
            service.remove_from_playlist("Viaggio", [music / "Imagine.mp3"])
            self.assertEqual([t.name for t in service.playlist_tracks("Viaggio")], ["Yesterday.mp3"])
            self.assertIn("eliminata", service.remove_from_playlist("Viaggio"))
            self.assertTrue((music / "Yesterday.mp3").exists())
            self.assertIn("Non trovo la playlist", service.handle("playlist", "viaggio"))


class YouTubeContinueTests(unittest.TestCase):
    def test_youtube_queues_more_results_and_goes_on_after_end(self):
        found = [("abcDEF12345", "Thunderstruck"), ("ghiJKL67890", "Back in Black")]
        with tempfile.TemporaryDirectory() as folder:
            v = VideoTests()
            service, panel, _ = v.make(folder, key="KEY", video_id=lambda q, k: found)
            service.handle("play", "acdc")
            self.assertTrue(v.wait(lambda: service.video_index == 0))
            self.assertEqual(service.snapshot()["title"], "Thunderstruck")
            service._video_event({"ev": "state", "state": "ended"})
            self.assertEqual(service.snapshot()["title"], "Back in Black")
            self.assertEqual(service.snapshot()["mode"], "video")

    def test_video_list_parses_titles(self):
        import io
        from musica.youtube import video_list
        body = json.dumps({"items": [
            {"id": {"videoId": "abcDEF12345"}, "snippet": {"title": "AC/DC &amp; Co"}},
            {"id": {"videoId": "abcDEF12345"}, "snippet": {"title": "doppione"}},
            {"id": {"videoId": "bad id!"}}]}).encode()

        class Resp(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False
        self.assertEqual(video_list("acdc", "K", opener=lambda url, timeout: Resp(body)),
                         [("abcDEF12345", "AC/DC & Co")])


class YouTubeQueueTests(unittest.TestCase):
    def test_queue_during_youtube_adds_after_current_without_interrupting(self):
        results = {"acdc": [("abcDEF12345", "Thunderstruck"), ("ghiJKL67890", "Back in Black")],
                   "queen": [("qqqQQQ11111", "Bohemian Rhapsody")],
                   "vasco": [("vvvVVV22222", "Albachiara")]}
        notes = []
        with tempfile.TemporaryDirectory() as folder:
            v = VideoTests()
            service, panel, _ = v.make(folder, key="KEY", video_id=lambda q, k: results[q])
            service.notify = notes.append
            service.handle("play", "acdc")
            self.assertTrue(v.wait(lambda: service.video_index == 0))
            self.assertIn("per la coda", service.handle("queue", "queen"))
            self.assertTrue(v.wait(lambda: len(service.video_items) == 3))
            service.handle("queue", "vasco")
            self.assertTrue(v.wait(lambda: len(service.video_items) == 4))
            self.assertEqual([t for _k, _i, t in service.video_items],
                             ["Thunderstruck", "Bohemian Rhapsody", "Albachiara", "Back in Black"])
            self.assertEqual(service.snapshot()["title"], "Thunderstruck")   # non interrotto
            self.assertIn("Aggiunto in coda: Albachiara.", notes)
            self.assertIn("solo video YouTube", service.enqueue([Path(folder) / "x.mp3"]))
            service._video_event({"ev": "state", "state": "ended"})
            self.assertEqual(service.snapshot()["title"], "Bohemian Rhapsody")
