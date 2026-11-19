import threading
import time
import tkinter as tk
import unittest

import audio_player
import lumi_comandi
import stato_lumi
from offline_tts import OfflineSpeaker


class StatoTest(unittest.TestCase):
    def s(self, **kw):
        base = dict(speaking=False, busy=False, thinking=False, mic_on=True,
                    always_listening=False, armed=False)
        base.update(kw)
        return stato_lumi.stato(**base)

    def test_cinque_stati_e_priorita(self):
        self.assertEqual(self.s(), "attesa")
        self.assertEqual(self.s(mic_on=False), "spento")
        self.assertEqual(self.s(armed=True), "ascolto")
        self.assertEqual(self.s(always_listening=True), "ascolto")
        self.assertEqual(self.s(thinking=True), "elabora")
        self.assertEqual(self.s(thinking=True, busy=True), "occupato")
        self.assertEqual(self.s(thinking=True, busy=True, speaking=True), "parla")

    def test_frasi_di_stop(self):
        for text in ("fermati", "Lumi, fermati!", "ehi lumi fermo", "ferma tutto", "basta"):
            self.assertTrue(stato_lumi.is_stop(text), text)
        # «stop/pausa/play» restano dei lettori audio-video (decisione 15/11).
        for text in ("stop", "Lumi stop", "pausa", "fermati qui", "annulla", "", None):
            self.assertFalse(stato_lumi.is_stop(text), text)

    def test_segno_di_stop_del_modello_vale_una_volta(self):
        self.assertFalse(stato_lumi.consume_model_stop())
        stato_lumi.mark_model_stop()
        self.assertTrue(stato_lumi.consume_model_stop())
        self.assertFalse(stato_lumi.consume_model_stop())


class ComandoFermatiTest(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.running = True
        lumi_comandi.register({"stop_all": self.stop_all, "minimize": lambda: None}, lambda: False)

    def tearDown(self):
        lumi_comandi.register({}, lambda: False)
        lumi_comandi._STATE["actions"] = None

    def stop_all(self):
        self.calls.append("stop")
        return self.running

    def test_fermati_ferma_se_c_e_qualcosa_in_corso(self):
        self.assertTrue(lumi_comandi.handle_text("fermati", lambda *_: None, lambda *_: None))
        self.assertEqual(self.calls, ["stop"])

    def test_fermati_passa_oltre_se_non_c_e_niente(self):
        self.running = False
        self.assertFalse(lumi_comandi.handle_text("fermati", lambda *_: None, lambda *_: None))

    def test_stop_da_solo_non_ferma_lumi(self):
        lumi_comandi.handle_text("stop", lambda *_: None, lambda *_: None)
        self.assertEqual(self.calls, [])


class InterruzioneVoceTest(unittest.TestCase):
    def tearDown(self):
        audio_player.release()

    def test_interrupt_svuota_la_coda_e_le_frasi_dopo_ripartono(self):
        gate = threading.Event()
        spoken = []

        def runner(payload, timeout):
            gate.wait(2)
            spoken.append(payload["text"])

        speaker = OfflineSpeaker(runner=runner)
        speaker.speak("Prima frase.")
        speaker.speak("Seconda frase.")
        speaker.speak("Terza frase.")
        for _ in range(40):
            if speaker.is_speaking():
                break
            time.sleep(0.05)
        self.assertEqual(speaker.interrupt(), 2)
        gate.set()
        for _ in range(40):
            if not speaker.is_speaking():
                break
            time.sleep(0.05)
        self.assertNotIn("Seconda frase.", spoken)
        self.assertFalse(audio_player._HOLD.is_set())   # rilasciato a fine frase
        speaker.speak("Mi fermo.")
        for _ in range(40):
            if "Mi fermo." in spoken:
                break
            time.sleep(0.05)
        speaker.close()
        self.assertIn("Mi fermo.", spoken)

    def test_audio_bloccato_non_parte(self):
        audio_player.hold()
        try:
            audio_player.play("non-esiste.wav")    # su Windows ritorna subito
        except OSError:
            pass                                   # fuori da Windows: nessuna riproduzione
        audio_player.release()
        self.assertFalse(audio_player._HOLD.is_set())


class RigaStatoTest(unittest.TestCase):
    def test_pulsante_ferma_attivo_solo_se_serve(self):
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk non disponibile: %s" % exc)
        root.withdraw()
        state = ["attesa"]
        stops = []
        try:
            riga = stato_lumi.RigaStato(root, read_state=lambda: state[0],
                                        on_stop=lambda: stops.append(1), bg="#000000")
            self.assertEqual(str(riga.button.cget("state")), "disabled")
            self.assertEqual(riga.label.cget("text"), "In attesa di «Lumi»")
            state[0] = "parla"
            riga.aggiorna()
            self.assertEqual(str(riga.button.cget("state")), "normal")
            riga.button.invoke()
            self.assertEqual(stops, [1])
            state[0] = "boom"
            riga.read_state = lambda: 1 / 0
            riga.aggiorna()                        # un errore non rompe la riga
            self.assertEqual(riga.current, "parla")
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
