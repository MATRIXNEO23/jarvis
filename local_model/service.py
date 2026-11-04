"""Shared local-first model boundary (red-stage contract)."""
import queue
class ModelService:
    def __init__(self, online, local, *, local_enabled=False, online_enabled=False, consent=None):
        self.online=online
        self.local=local
        self.local_selected=local_enabled
        self.online_enabled=online_enabled
        self.consent=consent
        self.events=queue.Queue()
    def call(self, action, *, timeout=120, **arguments):
        return {"text":"", "blocked":True}
