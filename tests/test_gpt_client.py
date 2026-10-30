"""Protocol integration tests for Python GPTClient without an OpenAI account.

Use a tiny local fake child process; do not simulate a successful OAuth login.
"""
from __future__ import annotations

import json
import subprocess
import sys
import threading
import unittest

from gpt_client import GPTClient, GPTUnavailable


FAKE_CHILD = r"""
import json, sys
for line in sys.stdin:
    item = json.loads(line)
    action = item.get('action')
    result = {'status': 'disconnected', 'sharing': False}
    if action == 'shutdown':
        print(json.dumps({'id': item['id'], 'ok': True, 'result': {'stopped': True}}), flush=True)
        break
    if action == 'error':
        print(json.dumps({'id': item['id'], 'ok': False, 'error': 'testing error'}), flush=True)
        continue
    if action == 'send_event':
        print(json.dumps({'event': 'open_browser', 'url': 'https://auth.openai.com/example'}), flush=True)
    print(json.dumps({'id': item['id'], 'ok': True, 'result': result}), flush=True)
"""


class GPTClientTests(unittest.TestCase):
    def setUp(self):
        self.client = GPTClient()
        process = subprocess.Popen(
            [sys.executable, "-u", "-c", FAKE_CHILD],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        self.client._process = process
        self.reader = threading.Thread(target=self.client._read_loop, args=(process,), daemon=True)
        self.reader.start()

    def tearDown(self):
        self.client.stop()
        self.reader.join(timeout=4)

    def test_status_command(self):
        status = self.client.call("status", timeout=5)
        self.assertEqual(status, {"status": "disconnected", "sharing": False})

    def test_errors_are_returned_not_hidden(self):
        with self.assertRaisesRegex(GPTUnavailable, "testing error"):
            self.client.call("error", timeout=5)

    def test_events_are_separated_from_responses(self):
        self.client.call("send_event", timeout=5)
        event = self.client.events.get(timeout=5)
        self.assertEqual(event["event"], "open_browser")
        self.assertTrue(event["url"].startswith("https://auth.openai.com/"))


if __name__ == "__main__":
    unittest.main()
