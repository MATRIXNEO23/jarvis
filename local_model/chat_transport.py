"""Transport routing for Jarvis requests; explicit caller-supplied selection.

Never automatically sends a local prompt to the online transport.
"""
class ChatTransport:
    def __init__(self, online, native):
        self.online = online
        self.native = native

    def call(self, action, *, use_native=False, timeout=120, **arguments):
        if type(use_native) is not bool:
            raise ValueError("Invalid model selection")
        if use_native and action == "ask":
            return self.native.call("ask", timeout=timeout, **arguments)
        if use_native:
            raise ValueError("Native transport does not support account actions")
        return self.online.call(action, timeout=timeout, **arguments)
