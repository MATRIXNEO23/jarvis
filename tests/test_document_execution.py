"""Regression tests: a document bridge error never strands Jarvis's work state."""
from pathlib import Path
import unittest
from types import SimpleNamespace

from document_execution import run_document_worker, execute_document


class FakeDocuments:
    def __init__(self, error=None):
        self.error=error
        self.recovered=0
        self.calls=[]

    def forget_if_closed(self):
        self.recovered+=1

    def open_blank(self):
        self.calls.append(("open",))
        if self.error:
            raise self.error
        return SimpleNamespace(kind="opened")

    def compose(self, content, target):
        self.calls.append(("compose",content,target))
        if self.error:
            raise self.error
        return SimpleNamespace(kind="created")

    def save_and_close(self, ident, path):
        self.calls.append(("save",ident,path))
        if self.error:
            raise self.error
        return SimpleNamespace(kind="saved_and_closed")

    def save_only(self, ident, path):
        self.calls.append(("save_only",ident,path))
        if self.error:
            raise self.error
        return SimpleNamespace(kind="saved_open")

    def discard_and_close(self, ident):
        self.calls.append(("discard",ident))
        if self.error:
            raise self.error
        return SimpleNamespace(kind="closed_without_saving")


class DocumentExecutionTests(unittest.TestCase):
    def test_open_and_compose_preserve_existing_operation_contract(self):
        docs=FakeDocuments()
        result=run_document_worker(docs,"compose",content="Ciao",
                                   target="new_notepad",close_after=True)
        self.assertEqual(result[0],"document_ok")
        self.assertEqual(result[1],"compose")
        self.assertTrue(result[3])
        self.assertEqual(docs.recovered,1)
        self.assertEqual(docs.calls,[("compose","Ciao","new_notepad")])

    def test_unexpected_exception_becomes_error_event_without_private_text(self):
        docs=FakeDocuments(RuntimeError("TOKEN-123 document secret"))
        result=run_document_worker(docs,"open")
        self.assertEqual(result[0:2],("document_error","open"))
        self.assertIn("RuntimeError",result[2])
        self.assertNotIn("TOKEN-123",result[2])

    def test_expected_io_error_surfaces_explanation(self):
        docs=FakeDocuments(OSError("File non disponibile"))
        result=run_document_worker(docs,"save",document_id="note",
                                   path=Path("new.txt"))
        self.assertEqual(result[0],"document_error")
        self.assertIn("File non disponibile",result[2])

    def test_reject_unknown_action_without_calling_bridge(self):
        docs=FakeDocuments()
        result=run_document_worker(docs,"arbitrary_shell")
        self.assertEqual(result[0],"document_error")
        self.assertEqual(docs.calls,[])

if __name__=="__main__":
    unittest.main()
