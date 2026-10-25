"""L2b mutation battery runner — batch 2026-10-23-hygiene-batch, increment-004 (lane L2b).

One (edit, node) arm per run, C-40 discipline: hash before, one anchored edit,
run the single node, restore, hash after; the restore digest must equal the
pre-mutation digest.  Exit 1 = a test failed (RED/KILLED) OR an expected-RED
arm SURVIVED, 0 = every arm killed, anything else = CRASH/BAD.
Run from the worktree root under `env -u NO_COLOR -u TERM`; transcripts of this
run are stored beside this file.

Arms (contract negative controls / HLR-Q2.2, ledger .9):
  M-Q2-3 — the NUL probe shrunk to one byte (`data[:probe]` -> `data[:1]`):
           the byte-8,191 NUL arm must go RED (byte 0 stays caught by design).
  M-Q2-5 — the typed toast reverts to type-name-only (`{refusal}` ->
           `{type(refusal).__name__}`): the AT-114 screen arm must go RED.
"""
import hashlib
import os
import pathlib
import subprocess
import sys

ARMS = [
    (
        "M-Q2-3",
        pathlib.Path("mapper/osopen.py"),
        b'if probe and b"\\x00" in data[:probe]:',
        b'if probe and b"\\x00" in data[:1]:  # M-Q2-3: probe shrunk',
        ["tests/test_ingestion_limits.py::test_csv_nul_at_last_probe_byte_refuses_as_binary"],
    ),
    (
        "M-Q2-5",
        pathlib.Path("mapper/screens/home.py"),
        b'f"could not read CSV {path.name!r}: {refusal}"',
        b'f"could not read CSV {path.name!r}: {type(refusal).__name__}"',
        ["tests/test_ingestion_limits.py::test_at_114_csv_refusal_toast_shows_the_reason"],
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
        if verdict != "RED (KILLED)":
            bad += 1
            if verdict is None:
                verdict = f"CRASH/BAD (exit {r.returncode})"
        print(f"{arm}: {verdict}", flush=True)
print("arms:", sum(len(n) for _, _, _, _, n in ARMS), "bad:", bad)
sys.exit(1 if bad else 0)
