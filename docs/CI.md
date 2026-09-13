# Phase 8 continuous integration

The `Phase 8 CI` workflow runs on pull requests targeting `main` and pushes
to `main`. It also declares a manual trigger, available once the workflow is
on the default branch. Updates to the same PR cancel superseded runs.

| Job | What it verifies |
| --- | --- |
| `phase8-contract` | Backend Python syntax and the existing IndicLID adapter/router unit tests on Python 3.11. |
| `notebook-validation` | Tracked notebook JSON/schema, Python code-cell syntax, Bash/sh cell syntax and absence of saved execution-error outputs on Python 3.13. Includes tests that the validator rejects broken notebooks and never executes their cells. |
| `workflow-lint` | GitHub Actions YAML, expressions, job/step structure and shell commands using actionlint 1.7.12. The downloaded binary is checked against its release SHA-256. |

Notebook validation reads the files without rewriting them. It transforms
IPython syntax for parsing, uses `bash -n`/`sh -n` for shell cells, and rejects
unsupported cell magics rather than silently skipping their contents. Python
cell magics `time`, `timeit`, `capture`, `prun`, `python` and `python3`
are checked by parsing their Python bodies. Single-line magics are parsed by
IPython; their runtime behavior is outside this check.

These are static checks and adapter/router unit tests. They do not download
IndicLID models, execute notebook cells, validate runtime dependency compatibility,
prove fresh Colab reproducibility, or verify the frozen Phase 5 evaluation
metrics. Colab execution evidence and later backend integration tests remain
separate validation requirements.

## Run the notebook checks locally

From the repository root, using a suitable virtual environment:

```bash
python -m pip install -r .github/requirements-notebook-ci.txt
python -m unittest discover -s scripts/tests -v
python scripts/check_notebooks.py
```

An explicit notebook path can be supplied to check an untracked notebook:

```bash
python scripts/check_notebooks.py Phase8_IndicLID_Fix.ipynb
```

PR #3 separately introduces the broader backend/API, Phase 7 and extension CI
workflow. These jobs keep their scope separate from that work.
