"""Local recall for the owner conversation; never a source of action consent.

Returns bounded records, not a pre-packed prompt. The final prompt builder owns
its one character budget. No schema migration, network or background process.
"""
from __future__ import annotations

import json

from conversation_memory import ConversationMemory, pending_question
from dialogue_focus import focus_hint


def _turn(row):
    if not isinstance(row, dict):
        return None
    user = row.get("utente", row.get("user", ""))
    answer = row.get("jarvis", row.get("lia", row.get("reply", "")))
    kind = row.get("tipo", row.get("kind", "chat"))
    if not isinstance(user, str) or not isinstance(answer, str) or not user or not answer:
        return None
    if kind not in ("chat", "clarify", "action", "error"):
        kind = "chat"
    result = {"utente": user, "jarvis": answer, "tipo": kind}
    question = row.get("question") or pending_question(answer, kind)
    if question:
        result["question"] = question
    return result


def merge_recent(saved, live):
    """Remove only the overlapping tail: repeated exchanges stay chronological.

    SQLite stores shorter copies than RAM. Compare their common stored prefix,
    not fuzzy similarity; near matches outside this overlap remain distinct.
    """
    older = [item for row in saved if (item := _turn(row)) is not None]
    newer = [item for row in live if (item := _turn(row)) is not None]
    def same(a, b):
        return (a["tipo"] == b["tipo"]
                and a["utente"][:320] == b["utente"][:320]
                and (a["jarvis"][:350] == b["jarvis"][:350]
                     or (a.get("question") and a.get("question") == b.get("question")
                         and a["jarvis"][:150] == b["jarvis"][:150])))
    overlap = 0
    for count in range(1, min(len(older), len(newer)) + 1):
        if all(same(a, b) for a, b in zip(older[-count:], newer[:count])):
            overlap = count
    return (older[:-overlap] + newer if overlap else older + newer)[-16:]


def recall_context(utterance, memory: ConversationMemory, *, brain=None,
                   workspace=None, project_id=None, preferences=()):
    """Call with brain=None when general memory is disabled.

    A selected project never falls back to the owner's general memory. Errors
    propagate to the UI; the caller may explicitly fall back to the same RAM.
    """
    saved, related, progress, name = [], [], [], ""
    if project_id is not None:
        if workspace is not None:
            project = workspace.project(project_id)
            saved = workspace.recent("project", project_id, 12)
            data = json.loads(workspace.prompt_context(
                "project", project_id, utterance, budget=620))
            related = data.get("evidence", [])
            if project:
                name = project["name"]
                if project["summary"]:
                    related.insert(0, {"source": "conversation",
                        "when": project["updated_utc"],
                        "fact": "Stato progetto fornito dall'utente: " + project["summary"][:260]})
            progress = [{"title": step["title"][:95], "status": step["status"],
                         "detail": step["detail"][:110], "verified": bool(step["verified"])}
                        for step in workspace.project_steps(project_id, limit=4)]
    elif brain is not None:
        # Read recent rows directly: they must not compete with search hits in
        # an intermediate character budget or disappear for a short pronoun.
        saved = brain.recent_turns(8)
        related = json.loads(brain.prompt_context(utterance, budget=530)).get("related", [])
    recent = merge_recent(saved, memory.snapshot())
    question = ""
    if recent:
        latest = recent[-1]
        question = latest.get("question", "") if latest["tipo"] in ("chat", "clarify") else ""
    return json.dumps({"breve": recent, "focus": focus_hint(
        utterance, active_project_name=name, last_question=question),
        "permanente": {"related": related}, "progress": progress,
        "preferences": list(preferences)}, ensure_ascii=False, separators=(",", ":"))


def context_question(raw):
    """The actual latest question for the local short-reply guard, not consent."""
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return ""
    focus = data.get("focus", {}) if isinstance(data, dict) else {}
    return focus.get("pending_question", "") if isinstance(focus, dict) else ""
