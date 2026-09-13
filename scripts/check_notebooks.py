"""Validate notebook structure and cell syntax without running inference or setup."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

import nbformat
from IPython.core.inputtransformer2 import TransformerManager


class NotebookCheckError(ValueError):
    """A notebook cannot pass the static checks."""


def validate_notebook(path: Path) -> int:
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        nbformat.validate(notebook)
    except (OSError, ValueError, nbformat.ValidationError) as exc:
        raise NotebookCheckError(f"{path}: invalid notebook: {exc}") from exc

    language = notebook.get("metadata", {}).get("kernelspec", {}).get("language")
    language = language or notebook.get("metadata", {}).get("language_info", {}).get("name")
    if language and language != "python":
        raise NotebookCheckError(f"{path}: unsupported notebook language: {language}")

    transformer = TransformerManager()
    code_cells = 0
    for number, cell in enumerate(notebook["cells"], start=1):
        if cell["cell_type"] != "code":
            continue
        code_cells += 1
        location = f"{path}: cell {number}"
        if any(output["output_type"] == "error" for output in cell["outputs"]):
            raise NotebookCheckError(f"{location}: saved execution error output")

        source = cell["source"]
        if isinstance(source, list):
            source = "".join(source)
        header, _, body = source.lstrip().partition("\n")
        magic = header.split(maxsplit=1)[0] if header else ""
        if magic in {"%%bash", "%%sh"}:
            try:
                result = subprocess.run(
                    [magic[2:], "-n"],
                    input=body,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise NotebookCheckError(f"{location}: shell syntax check failed: {exc}") from exc
            if result.returncode:
                raise NotebookCheckError(f"{location}: {result.stderr.strip()}")
            continue

        if magic in {"%%time", "%%timeit", "%%capture", "%%prun", "%%python", "%%python3"}:
            source = body
        elif magic.startswith("%%"):
            raise NotebookCheckError(f"{location}: unsupported cell magic: {magic}")

        try:
            transformed = transformer.transform_cell(source)
            compile(
                transformed,
                location,
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
                dont_inherit=True,
            )
        except (SyntaxError, ValueError) as exc:
            raise NotebookCheckError(f"{location}: Python syntax error: {exc}") from exc
    return code_cells


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*", type=Path)
    paths = parser.parse_args().notebooks
    if not paths:
        tracked = subprocess.run(
            ["git", "ls-files", "-z", "--", "*.ipynb"],
            capture_output=True, text=True, check=True,
        )
        paths = [Path(name) for name in tracked.stdout.split("\0") if name]
    if not paths:
        parser.error("no tracked notebooks found")

    failed = False
    for path in paths:
        try:
            count = validate_notebook(path)
            print(f"PASS {path}: format, saved-error outputs, and {count} code cells checked")
        except NotebookCheckError as exc:
            print(f"FAIL {exc}", file=sys.stderr)
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
