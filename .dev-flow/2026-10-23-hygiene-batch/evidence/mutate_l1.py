"""L1 mutation battery runner — batch 2026-10-23-hygiene-batch, increment-002.

One (edit, node) arm per run, C-40 discipline: hash before, one anchored edit,
run the single node, restore, hash after; the restore digest must equal the
pre-mutation digest.  Exit 1 = a test failed (RED/KILLED), 0 = GREEN/SURVIVED,
anything else = CRASH/BAD.  Run from the worktree root under
`env -u NO_COLOR -u TERM`; transcripts of this run are stored beside this file.

Arms (proposal §5 / ledger .3):
  M-Q1-1 — delete the neutralisation in `MapperApp.__init__` (the
           `os.environ.pop("NO_COLOR", None)` that runs before
           `super().__init__()`), run against each node of
           `tests/test_colour_always_on.py` separately.
"""
import hashlib
import os
import pathlib
import subprocess
import sys

ARMS = [
    (
        "M-Q1-1",
        pathlib.Path("mapper/app.py"),
        b'os.environ.pop("NO_COLOR", None)',
        b'pass  # M-Q1-1: neutralisation deleted',
        ["tests/test_colour_always_on.py::test_no_color_removed_before_super"],
    ),
    (
        "M-Q1-1",
        pathlib.Path("mapper/app.py"),
        b'os.environ.pop("NO_COLOR", None)',
        b'pass  # M-Q1-1: neutralisation deleted',
        ["tests/test_colour_always_on.py::test_painted_screen_byte_identical_with_and_without_no_color"],
    ),
]

ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
bad = 0
for mutant, f, old, new, nodes in ARMS:
    src = f.read_bytes()
    h0 = hashlib.sha256(src).hexdigest()
    print(f"{mutant} before: {h0}", flush=True)
    if src.count(old) != 1:
        print(f"{mutant}: BAD (anchor count {src.count(old)} != 1)")
        bad += 1
        continue
    for node in nodes:
        arm = f"{mutant} {node}"
        try:
            f.write_bytes(src.replace(old, new, 1))
            if hashlib.sha256(f.read_bytes()).hexdigest() == h0:
                print(f"{arm}: BAD (the edit did not apply)")
                bad += 1
                continue
            r = subprocess.run(
                [sys.executable, "-B", "-m", "pytest", "-q",
                 "-p", "no:cacheprovider", "--color=no", node],
                env=ENV,
            )
        finally:
            f.write_bytes(src)
        h1 = hashlib.sha256(f.read_bytes()).hexdigest()
        print(f"{mutant} after:  {h1}", flush=True)
        if h1 != h0:
            print(f"{arm}: BAD (restore not proven)")
            bad += 1
            continue
        verdict = {1: "RED (KILLED)", 0: "GREEN (SURVIVED)"}.get(r.returncode)
        if verdict is None:
            verdict = f"CRASH/BAD (exit {r.returncode})"
            bad += 1
        print(f"{arm}: {verdict}", flush=True)
print("arms:", len(ARMS), "bad:", bad)
sys.exit(1 if bad else 0)
