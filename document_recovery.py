"""Explicitly synchronize an externally closed owned Notepad and dialog state.

Only acts after the original owned process or HWND is definitely gone.
Never closes a window, deletes a file, discards text, or trusts an
inconclusive control read as proof that a user document was closed.
"""
from __future__ import annotations

from document_dialog import DocumentDialog
from managed_documents import ManagedDocuments


def release_closed_document(documents: ManagedDocuments, dialog: DocumentDialog) -> bool:
    """Forget a lost session *and* its pending save/close confirmations."""
    if not documents.forget_if_closed():
        return False
    dialog.reset()
    return True
