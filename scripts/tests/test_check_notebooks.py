"""Behavioral checks for the notebook CI gate; no notebook code is executed."""

import json
import tempfile
import unittest
from pathlib import Path

import nbformat

from scripts.check_notebooks import NotebookCheckError, validate_notebook


class NotebookValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "sample.ipynb"

    def write_notebook(self, *sources, outputs=None):
        cells = [nbformat.v4.new_code_cell(source) for source in sources]
        if outputs:
            cells[0]["outputs"] = outputs
        document = nbformat.v4.new_notebook(cells=cells)
        self.path.write_text(json.dumps(document), encoding="utf-8")

    def test_valid_cells_are_checked_without_execution(self):
        marker = Path(self.directory.name) / "must-not-exist"
        self.write_notebook(
            f"from pathlib import Path\nPath({str(marker)!r}).touch()",
            "%pip install must-not-be-installed",
            "await some_coroutine()",
            f"%%bash\ntouch '{marker}'\nexit 9",
        )
        before = self.path.read_bytes()
        self.assertEqual(validate_notebook(self.path), 4)
        self.assertFalse(marker.exists())
        self.assertEqual(self.path.read_bytes(), before)

    def test_python_syntax_error_is_rejected(self):
        self.write_notebook("if True\n    pass")
        with self.assertRaisesRegex(NotebookCheckError, "cell 1: Python syntax"):
            validate_notebook(self.path)

    def test_bash_syntax_error_is_rejected(self):
        self.write_notebook("%%bash\nif true; then\n echo incomplete")
        with self.assertRaisesRegex(NotebookCheckError, "cell 1"):
            validate_notebook(self.path)

    def test_python_inside_cell_magic_is_checked(self):
        self.write_notebook("%%time\nvalue =")
        with self.assertRaisesRegex(NotebookCheckError, "Python syntax"):
            validate_notebook(self.path)

    def test_unsupported_cell_magic_is_rejected(self):
        self.write_notebook("%%javascript\nnot python")
        with self.assertRaisesRegex(NotebookCheckError, "unsupported cell magic"):
            validate_notebook(self.path)

    def test_malformed_json_is_rejected(self):
        self.path.write_text("{", encoding="utf-8")
        with self.assertRaisesRegex(NotebookCheckError, "invalid notebook"):
            validate_notebook(self.path)

    def test_invalid_notebook_schema_is_rejected(self):
        self.write_notebook("value = 1")
        document = json.loads(self.path.read_text(encoding="utf-8"))
        del document["cells"][0]["outputs"]
        self.path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(NotebookCheckError, "invalid notebook"):
            validate_notebook(self.path)

    def test_saved_execution_error_is_rejected(self):
        self.write_notebook(
            "1 / 0",
            outputs=[nbformat.v4.new_output(
                "error", ename="ZeroDivisionError", evalue="division by zero", traceback=[]
            )],
        )
        with self.assertRaisesRegex(NotebookCheckError, "saved execution error"):
            validate_notebook(self.path)

    def test_missing_notebook_is_rejected(self):
        with self.assertRaisesRegex(NotebookCheckError, "invalid notebook"):
            validate_notebook(self.path)


if __name__ == "__main__":
    unittest.main()
