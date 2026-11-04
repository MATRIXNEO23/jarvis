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

    def call_feature(self, capability, action, *, policy, confirmed=False,
                     use_native=False, timeout=120, **arguments):
        """Guard online calls for an explicitly identified capability.

        Legacy account/login methods stay on call(); feature calls cannot
        accidentally inherit that legacy unguarded route.
        """
        decision = policy.decide(capability, confirmed=confirmed)
        if use_native:
            return self.call(action, use_native=True, timeout=timeout, **arguments)
        if decision == "local_only":
            raise PermissionError("GPT online disabilitato per questa funzione.")
        if decision == "request_consent":
            raise PermissionError("Conferma GPT online richiesta per questa operazione.")
        return self.call(action, timeout=timeout, **arguments)
