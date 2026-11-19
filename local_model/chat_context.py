"""Restricted Gemma memory reader for one local Lumi chat instance.

No global Second Brain data, project memories, online provider or commands.
The only persistent input is the explicitly selected ChatSessionStore chat.
"""

from .chat_sessions import ChatSessionStore


def make_chat_history_reader(store, chat_id, *, project_id=None):
    """Return a callable accepted by NativeConversationSession.prepare_turn.

    The callable never appends global memories. recent_pairs() only yields
    validated exchanges from the selected project/chat ID after scope check.
    """
    if not isinstance(store, ChatSessionStore):
        raise TypeError("Archivio chat locale richiesto.")
    store.get_chat(chat_id, project_id=project_id)

    def read(_budget):
        # F6 may add explicit, permissioned global memories later. F2 never
        # combines unrelated chats or Second Brain automatically.
        return ""

    def recent_pairs(count):
        return store.recent_pairs(chat_id, project_id=project_id, count=count)

    read.recent_pairs = recent_pairs
    # Observability only: the prompt viewer must never mislabel this scoped
    # reader as global Second Brain or a legacy project memory owner.
    read.diagnostic_history_source = (
        "ChatSessionsStore.recent_pairs: istanza isolata ("
        + ("progetto" if project_id is not None else "generale") + ")")
    read.diagnostic_recall_source = (
        "Nessuno: Chat locali F2 non richiama Second Brain automaticamente")
    return read
