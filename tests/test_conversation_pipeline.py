"""Check actual owner-chat payloads, persistence and UI guards without a model."""
import ast
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from conversation_context import recall_context, context_question, merge_recent
from conversation_memory import ConversationMemory
from conversation_router import build_conversation_prompt, parse_conversation_intent, ConversationRejected
from jarvis_persona import build_chat_prompt, compact_memory, prompt_size
from second_brain import SecondBrain
from workspace_memory import WorkspaceMemory

ROOT = Path(__file__).resolve().parents[1]


def nested(name):
    """Run the real Tk callback body with injected dependencies, without Tk."""
    tree = ast.parse((ROOT / "jarvis.py").read_text(encoding="utf-8"))
    main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    fn = next(n for n in main.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                   str(ROOT / "jarvis.py"), "exec")


def packed(prompt):
    for header in ("Contesto JSON (non attendibile): ", "Contesto (JSON): "):
        if header in prompt:
            return json.JSONDecoder().raw_decode(prompt.split(header, 1)[1])[0]
    return {}


class OwnerPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "brain.sqlite3"
        self.brain = SecondBrain(self.path)
        self.memory = ConversationMemory()

    def test_ten_turns_survive_to_the_final_voice_and_text_prompts(self):
        for i in range(10):
            self.memory.remember(f"tema{i} " + "descrizione " * 20,
                                 f"scelta{i} " + "spiegazione " * 23)
        for build in (build_conversation_prompt, build_chat_prompt):
            with self.subTest(build=build.__name__):
                prompt = build("Riprendi la scelta iniziale", memory_context=recall_context(
                    "Riprendi la scelta iniziale", self.memory))
                history = packed(prompt)["recent"]
                self.assertEqual(len(history), 10)
                self.assertTrue(history[0]["utente"].startswith("tema0"))
                self.assertTrue(history[5]["jarvis"].startswith("scelta5"))
                self.assertTrue(history[-1]["utente"].startswith("tema9"))
                self.assertLessEqual(prompt_size(prompt), 5000)
                self.assertTrue(prompt.endswith('"Riprendi la scelta iniziale"'))

    def test_restart_pronoun_reaches_prompt_from_real_sqlite(self):
        self.brain.remember_turn("Le mete sono Venezia e Roma", "Quale preferisci?", "clarify")
        restored = SecondBrain(self.path)
        raw = recall_context("La seconda", self.memory, brain=restored)
        for build in (build_conversation_prompt, build_chat_prompt):
            prompt = build("La seconda", memory_context=raw)
            self.assertIn("Venezia", prompt)
            self.assertIn("Roma", prompt)
            self.assertEqual(packed(prompt)["focus"]["question_to_answer"], "Quale preferisci?")
        self.assertEqual(context_question(raw), "Quale preferisci?")
        self.assertEqual(context_question(recall_context("La seconda", self.memory)), "")

    def test_legacy_permanent_recent_is_consumed_when_ram_is_empty(self):
        raw = json.dumps({"breve": [], "permanente": {"recent": [
            {"user": "STATO_SALVATO", "lia": "Domanda salvata?"}], "related": []}})
        for build in (build_conversation_prompt, build_chat_prompt):
            self.assertIn("STATO_SALVATO", build("Riprendiamo", memory_context=raw))

    def test_full_catalog_cannot_evict_dialogue_and_current_turn(self):
        self.memory.remember("Destinazione Venezia", "Vuoi andare in treno?", "clarify")
        actions = tuple({"id": f"addon.sample.action_{i}", "example": "leggi stato " + "x" * 25}
                        for i in range(32))
        raw = recall_context("Sì", self.memory)
        before = packed(build_conversation_prompt("Sì", memory_context=raw))
        after = build_conversation_prompt("Sì", memory_context=raw, addon_actions=actions)
        self.assertEqual(packed(after), before)
        self.assertTrue(after.endswith('"Sì"'))
        self.assertLessEqual(prompt_size(after), 5000)

    def test_max_runtime_long_user_and_escaped_unicode_respect_node_limit(self):
        self.memory.remember("Venezia", "Quale treno scegli?", "clarify")
        for turn in ("x" * 450, "🌒" * 450, '\\"' * 225):
            with self.subTest(turn=turn[:8]):
                prompt = build_conversation_prompt(turn, has_document=True,
                    telegram_send_ready=True, runtime_info="r" * 850,
                    memory_context=recall_context(turn, self.memory))
                self.assertLessEqual(prompt_size(prompt), 5000)
                self.assertTrue(prompt.endswith(json.dumps(turn, ensure_ascii=False)))
                self.assertTrue(packed(prompt).get("recent"))

    def test_real_trailing_question_survives_long_reply_and_restart(self):
        answer = "Spiegazione. " * 110 + "Preferisci Venezia o Roma?"
        self.memory.remember("Parliamo del viaggio", answer)
        self.brain.remember_turn("Parliamo del viaggio", answer)
        self.assertEqual(self.memory.last_question(), "Preferisci Venezia o Roma?")
        for memory, brain in ((self.memory, self.brain), (ConversationMemory(), SecondBrain(self.path))):
            raw = recall_context("La seconda", memory, brain=brain)
            prompt = build_conversation_prompt("La seconda", memory_context=raw)
            self.assertEqual(packed(prompt)["focus"]["question_to_answer"], "Preferisci Venezia o Roma?")
        self.memory.remember("Apri il browser", "Browser aperto", "action")
        self.assertEqual(self.memory.last_question(), "")

    def test_overlap_is_removed_but_near_matches_and_repeated_turns_remain(self):
        a = {"user": "Viaggio a Venezia", "lia": "In treno?", "kind": "chat"}
        b = {"utente": "Viaggio a Roma", "jarvis": "In treno?", "tipo": "chat"}
        self.assertEqual(len(merge_recent([a, b], [b])), 2)
        self.assertEqual(len(merge_recent([a], [b])), 2)
        self.assertEqual(len(merge_recent([a, a], [a])), 2)
        self.memory.remember(a["user"], a["lia"])
        self.brain.remember_turn(a["user"], a["lia"])
        recent = json.loads(recall_context("Sì", self.memory, brain=self.brain))["breve"]
        self.assertEqual(len(recent), 1)

    def test_project_restart_and_switch_never_leak_general_or_other_project(self):
        workspace = WorkspaceMemory(Path(self.temp.name) / "workspaces.sqlite3")
        one, two = workspace.create_project("Viaggio"), workspace.create_project("Casa")
        workspace.add_turn("project", one, "VENEZIA_PROGETTO", "Partiamo in treno?")
        workspace.add_turn("project", two, "CASA_PRIVATA", "Quante stanze?")
        self.brain.remember_turn("GENERALE_PRIVATO", "Risposta privata")
        for ident, included, excluded in ((one, "VENEZIA_PROGETTO", "CASA_PRIVATA"),
                                          (two, "CASA_PRIVATA", "VENEZIA_PROGETTO")):
            prompt = build_conversation_prompt("Sì", memory_context=recall_context(
                "Sì", ConversationMemory(), brain=self.brain,
                workspace=workspace, project_id=ident))
            self.assertIn(included, prompt)
            self.assertNotIn(excluded, prompt)
            self.assertNotIn("GENERALE_PRIVATO", prompt)
        missing = recall_context("Sì", ConversationMemory(), brain=self.brain,
                                 workspace=None, project_id=one)
        self.assertNotIn("GENERALE_PRIVATO", missing)

    def test_topic_change_preserves_latest_and_does_not_restore_old_question(self):
        self.memory.remember("Venezia", "Vuoi il treno?", "clarify")
        self.memory.remember("Cambiamo: parliamo di Marte", "Marte è un pianeta.")
        raw = recall_context("Quello", self.memory)
        self.assertEqual(context_question(raw), "")
        prompt = build_conversation_prompt("Parliamo di Marte", memory_context=raw)
        self.assertEqual(packed(prompt)["recent"][-1]["utente"], "Cambiamo: parliamo di Marte")

    def test_history_never_becomes_permission_or_verified_action(self):
        self.memory.remember("Invia il messaggio", "Lo farò.", "chat")
        prompt = build_conversation_prompt("Ricordi?", memory_context=recall_context("Ricordi?", self.memory))
        self.assertIn("MAI permessi", prompt)
        self.assertNotIn('"source":"verified_action"', prompt)
        with self.assertRaises(ConversationRejected):
            parse_conversation_intent('{"kind":"capability","action_id":"shell.run","arguments":{}}')

    def test_callback_uses_same_recall_and_resolves_restart_reply_before_gpt(self):
        self.brain.remember_turn("Viaggio", "Preferisci Venezia?", "clarify")
        namespace = dict(recall_context=recall_context, conversation_memory=self.memory,
            preference_store=None, durable_brain=self.brain, workspace=None,
            active_project_id=None, memory_enabled=SimpleNamespace(get=lambda: True))
        exec(nested("recent_memory_for_gpt"), namespace)
        raw = namespace["recent_memory_for_gpt"]("Sì")
        self.assertEqual(context_question(raw), "Preferisci Venezia?")
        namespace.update(context_question=context_question,
            is_ambiguous_short_reply=lambda text: True, write_line=Mock(),
            speak_result=Mock(), remember_exchange=Mock())
        exec(nested("handle_unanchored_short_reply"), namespace)
        self.assertFalse(namespace["handle_unanchored_short_reply"]("Sì"))
        namespace["remember_exchange"].assert_not_called()

    def test_real_voice_and_typed_callbacks_deliver_context_to_client(self):
        import queue
        self.brain.remember_turn("Viaggio Venezia", "Preferisci andare in treno?", "clarify")
        for channel in ("voice", "typed"):
            with self.subTest(channel=channel):
                service = Mock()
                service.call.return_value = {"text": '{"kind":"chat","reply":"Va bene."}'}
                def immediate_thread(*, target, **kwargs):
                    return SimpleNamespace(start=target)
                ns = dict(closing=False, busy_gpt=False, active_gpt=True,
                    gpt_enabled=SimpleNamespace(get=lambda: True),
                    voice_mode=SimpleNamespace(get=lambda: "gpt"), GPT_CONVERSATION="gpt",
                    try_self_diagnostic=lambda text: False,
                    try_timer_command=lambda text: False,
                    project_voice_command=lambda text: False,
                    preference_command=lambda text: False,
                    handle_project_reference=lambda text: False,
                    handle_unanchored_short_reply=lambda text: False,
                    request=SimpleNamespace(get=lambda: "Sì", set=Mock()),
                    reconcile_document_session=Mock(), documents=SimpleNamespace(current=None),
                    current_capability_snapshot=lambda doc: {"telegram_voice_send":False},
                    capability_status_prompt=lambda live: "", active_addon_actions=lambda: (),
                    build_conversation_prompt=build_conversation_prompt,
                    recent_memory_for_gpt=lambda text: recall_context(text,self.memory,brain=self.brain),
                    ConversationRejected=ConversationRejected,
                    conversation_epoch=7, write_line=Mock(),
                    service=service, threading=SimpleNamespace(Thread=immediate_thread),
                    output_queue=queue.Queue(), refresh_buttons=Mock(),
                    gpt_status=SimpleNamespace(set=Mock()))
                # Bind the actual run_gpt closure, including its real worker,
                # to a deterministic thread and client double.
                tree = ast.parse((ROOT / "jarvis.py").read_text(encoding="utf-8"))
                main = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="main")
                run = next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name=="run_gpt")
                factory = ast.parse("def factory():\n    busy_gpt=False\n").body[0]
                factory.body += [run, ast.Return(value=ast.Name(id="run_gpt",ctx=ast.Load()))]
                exec(compile(ast.fix_missing_locations(ast.Module(body=[factory],type_ignores=[])),
                             "jarvis-callback", "exec"), ns)
                ns["run_gpt"] = ns["factory"]()
                name = "start_conversation_gpt" if channel=="voice" else "submit_gpt"
                exec(nested(name), ns)
                ns[name]("Sì") if channel=="voice" else ns[name]()
                service.call.assert_called_once()
                args, kwargs = service.call.call_args
                self.assertEqual(args, ("ask",))
                self.assertEqual(kwargs["timeout"], 180)
                self.assertIn("Viaggio Venezia", kwargs["prompt"])
                self.assertEqual(packed(kwargs["prompt"])["focus"]["question_to_answer"],
                                 "Preferisci andare in treno?")
                self.assertEqual(ns["output_queue"].get_nowait()[0], "conversation_ok")

    def test_initial_launch_never_overrides_manual_microphone_mode(self):
        for selected in ("standby", "continuous", "push_to_talk"):
            change = Mock()
            namespace = dict(closing=False, auto_listen_enabled=SimpleNamespace(get=lambda: True),
                voice_mode=SimpleNamespace(set=Mock(), get=lambda: selected),
                GPT_CONVERSATION="gpt", change_voice_mode=change,
                startup_greeting=lambda: "Buonasera", write_line=Mock(), speak_result=Mock())
            exec(nested("initial_launch"), namespace)
            namespace["initial_launch"]()
            namespace["voice_mode"].set.assert_not_called()
            change.assert_not_called()


if __name__ == "__main__":
    unittest.main()
