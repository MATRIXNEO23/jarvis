"""Native session role boundaries before inference; Windows-only regression."""
import os
import unittest
from local_model.native_config import NativeModelConfig
from local_model.memory_preferences import MemoryPreferences
from local_model.native_conversation_session import NativeConversationSession

class Capture:
    def __init__(self): self.requests = []
    def prepare(self, **kwargs): pass
    def call(self, action, **kwargs):
        self.requests.append(kwargs)
        return {'text': 'Risposta controllata'}
    def stop(self): pass

@unittest.skipUnless(os.name == 'nt', 'Windows-only project requirement')
class SessionFormatTests(unittest.TestCase):
    def test_history_reaches_provider_as_alternating_roles(self):
        adapter = Capture()
        session = NativeConversationSession(adapter,
            config_loader=lambda: NativeModelConfig(context_size=2048),
            memory_loader=lambda: MemoryPreferences(prompt_max_tokens=1600))
        session.ask('Mi chiamo Alberto')
        session.ask('Come mi chiamo?')
        request = adapter.requests[-1]
        self.assertIn('messages', request)
        messages = request['messages']
        self.assertEqual([m['role'] for m in messages], ['user','assistant','user'])
        self.assertIn('Mi chiamo Alberto', messages[0]['content'])
        self.assertEqual(messages[1]['content'], 'Risposta controllata')
        self.assertEqual(messages[2]['content'], 'Come mi chiamo?')
        self.assertNotIn('prompt', request)

    def test_history_budget_never_leaves_orphan_assistant(self):
        adapter = Capture()
        session = NativeConversationSession(adapter,
            config_loader=lambda: NativeModelConfig(context_size=512, max_output=128),
            memory_loader=lambda: MemoryPreferences(prompt_max_tokens=600, recent_messages=3))
        session.ask('x' * 90)
        session.ask('y' * 90)
        session.ask('z' * 90)
        self.assertIn('messages', adapter.requests[-1])
        messages = adapter.requests[-1]['messages']
        self.assertEqual(messages[0]['role'], 'user')
        self.assertEqual(len(messages) % 2, 1)
