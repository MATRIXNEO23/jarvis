"""Cooperative idle scheduler for memory work.

The caller supplies a monotonic clock and runs tick from its normal event loop.
No thread or model generation is started automatically.
"""


class IdleMemoryGate:
    def __init__(self, preferences, clock):
        self.preferences = preferences.validate()
        self.clock = clock
        self.last_activity = clock()
        self.busy = False
        self.heavy_load = False
        self.pending = False

    def activity(self):
        self.last_activity = self.clock()
        self.busy = True

    def conversation_finished(self):
        self.last_activity = self.clock()
        self.busy = False

    def queue_summary(self):
        self.pending = True

    def ready(self):
        p = self.preferences
        return (p.background_summaries and self.pending
                and not self.busy
                and (not p.pause_on_heavy_load or not self.heavy_load)
                and self.clock() - self.last_activity >= p.idle_seconds)

    def begin(self):
        if not self.ready():
            return False
        self.busy = True
        return True

    def finish(self, *, saved):
        self.busy = False
        self.last_activity = self.clock()
        if saved:
            self.pending = False
