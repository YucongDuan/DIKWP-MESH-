# Reproduce MESH2 from source

The pinned reference environment is Python 3.12. Install `requirements.lock` into
a virtual environment and run `python scripts/reproduce.py`. The original
`requirements.txt` remains the broader compatibility declaration; the lock records
the exact tested package resolution.

SciPy is an explicit dependency because the NetworkX PageRank path used by the
analyzer requires it. The original package omitted this dependency; a clean
environment exposed and now covers this installation defect.

For an offline machine with matching Python/OS/architecture, prepare a wheelhouse
on a connected machine:

```bash
python -m pip download -r requirements.lock -d wheels
```

Then copy the source and wheelhouse to the offline machine:

```bash
python -m venv .venv
# Activate .venv using the command appropriate for your shell.
python -m pip install --no-index --find-links wheels -r requirements.lock
python scripts/reproduce.py
```

Do not copy an existing virtual environment between operating systems. A Linux
CPython 3.12 wheelhouse is not a Windows/macOS or universal Python bundle. The
checked-in `outputs/dashboard.html` can also be opened directly as a static
historical demonstration without Python, but that does not recompute results.

The runner executes the original eight tests and three snapshot-regression tests,
regenerates the semantic analysis and dashboard, checks rejection of the known
hierarchical fixture, and runs the path router. It compares fresh concept and
observer/atom counts, all transformation usage values, numeric metrics (`1e-6`
tolerance), the hierarchy verdict, invariant feature names and conflict feature
names. Required HTML/PNG artifacts must exist and be nonempty; binary image
identity is explicitly not asserted.

Each run generates a new `.reproduction/<timestamp>/receipt.json` with commands,
statuses, dependency versions and current source hashes. Failed commands,
timeouts, missing packages and mismatches produce a nonzero result. Historical
`RUN_PROOF.json` and checksums are under `docs/source-import/`, not evidence of a
fresh rerun. These fixture-level checks do not prove universal semantic invariants,
subjective consciousness, production fitness or external institutional adoption.
