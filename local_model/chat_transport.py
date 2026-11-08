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

    def ask_local_first(self, prompt, *, session, timeout=180,
                        context_id=None, defer_history=False, memory_context=None,
                        intent_context=None):
        """Use a prepared local Gemma session; errors never trigger GPT."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Richiesta vuota.")
        if type(defer_history) is not bool:
            raise ValueError("Modalità memoria locale non valida.")
        memory_args = {} if memory_context is None else {"memory_context": memory_context}
        if intent_context is not None:
            if not defer_history:
                raise ValueError('Le proposte native richiedono accettazione del chiamante.')
            memory_args['intent_context'] = intent_context
        if defer_history:
            return session.prepare_turn(prompt, timeout=timeout, context_id=context_id,
                                        **memory_args)
        if context_id is not None:
            return session.ask(prompt, timeout=timeout, context_id=context_id, **memory_args)
        return session.ask(prompt, timeout=timeout, **memory_args)
