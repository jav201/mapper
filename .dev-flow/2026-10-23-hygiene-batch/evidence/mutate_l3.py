"""L3 mutation battery runner — batch 2026-10-23-hygiene-batch, increment-001.

One (edit, node) arm per run, C-40 discipline: hash before, one anchored edit,
run the single node, restore, hash after; the restore digest must equal the
pre-mutation digest.  Exit 1 = a test failed (RED/KILLED), 0 = GREEN/SURVIVED,
anything else = CRASH/BAD.  Run from the worktree root under
`env -u NO_COLOR -u TERM`; transcripts of this run are stored beside this file.

Arms (proposal §5 / ledger .10 / contract negative controls):
  M-Q3-1 — break one renderer's bounds handling (executed on the WIDTH limb:
           radial's viewport widened past w; the h+1-line shape is structurally
           self-absorbed by every renderer's own `[:h]` cut on small-map
           renders — measured, recorded in increment-001 §5).
  M-Q3-2 — event append removed (the overprint append).
  M-Q3-3 — the sink touches the cell write (bytes move under audit).
  M-Q3-4 — the alphanumeric gate on the NEW character dropped (ledger .10).
"""
import hashlib
import itertools
import os
import pathlib
import subprocess
import sys

ARMS = [
    (
        "M-Q3-1",
        pathlib.Path("mapper/views/radial.py"),
        b"inner = w - 2",
        b"inner = w + 2",
        ["tests/test_scalecheck.py::test_sweep"],
    ),
    (
        "M-Q3-2",
        pathlib.Path("mapper/canvas.py"),
        b'self._audit.setdefault("overprint", []).append((x, y))',
        b"pass  # M-Q3-2: event append removed",
        ["tests/test_canvas_audit.py::test_events"],
    ),
    (
        "M-Q3-3",
        pathlib.Path("mapper/canvas.py"),
        b"self.cells[(x, y)] = (ch, style)",
        b"self.cells[(x, y)] = (ch.upper() if self._audit is not None else ch, style)",
        ["tests/test_canvas_audit.py::test_byte_identity"],
    ),
    (
        "M-Q3-4",
        pathlib.Path("mapper/canvas.py"),
        b"and ch.isalnum()",
        b"and True  # M-Q3-4: alphanumeric gate on the new character dropped",
        ["tests/test_canvas_audit.py::test_events"],
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
print("arms:", len(ARMS) * 1, "bad:", bad)
sys.exit(1 if bad else 0)
