"""Bounded execution boundary for Jarvis-owned Notepad operations.

Never lets an unexpected document worker exception leave the main UI busy.
The caller receives a data-only outcome and handles all Tk updates on its
own thread. Never performs unrelated document or filesystem operations.
"""
from __future__ import annotations
from pathlib import Path


def execute_document(documents, operation: str, *, content: str = "",
                     target: str = "", document_id: str = "",
                     path: Path | None = None):
    if operation == "open" or (operation == "compose" and target == "new_notepad"):
        documents.forget_if_closed()
    if operation == "open":
        return documents.open_blank()
    if operation == "compose":
        return documents.compose(content, target)
    if operation == "save" and path is not None:
        return documents.save_and_close(document_id, path)
    if operation == "save_only" and path is not None:
        return documents.save_only(document_id, path)
    if operation == "discard":
        return documents.discard_and_close(document_id)
    raise ValueError("Operazione documento non consentita.")


def run_document_worker(documents, operation: str, *,
                        content: str = "", target: str = "",
                        document_id: str = "", path: Path | None = None,
                        close_after: bool = False):
    """Return a queue-compatible message even when a bridge fails unexpectedly."""
    try:
        result = execute_document(
            documents, operation, content=content, target=target,
            document_id=document_id, path=path)
        return ("document_ok", operation, result, close_after)
    except (OSError, ValueError) as exc:
        return ("document_error", operation, str(exc)[:250])
    except Exception as exc:
        # Never send a traceback, document text, or private path to the log.
        return ("document_error", operation,
                "Errore imprevisto gestore documento: "+type(exc).__name__)
