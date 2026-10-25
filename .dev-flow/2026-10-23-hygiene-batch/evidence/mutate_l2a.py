"""L2a mutation battery runner — batch 2026-10-23-hygiene-batch, increment-003 (lane L2a).

One (edit, node) arm per run, C-40 discipline: hash before, one anchored edit,
run the single node, restore, hash after; the restore digest must equal the
pre-mutation digest.  Exit 1 = a test failed (RED/KILLED), 0 = GREEN/SURVIVED,
anything else = CRASH/BAD.  Run from the worktree root under
`env -u NO_COLOR -u TERM`; transcripts of this run are stored beside this file.

Arms (contract negative controls / HLR-Q2.1):
  M-Q2-1 — the prescan bypassed (design-proposal §5: remove the prescan OR its
           depth check; executed on the event-loop anchor so anchors, aliases
           AND depth all go unguarded).
  M-Q2-2 — the byte cap's read re-check removed (LLR-Q2.1.1's TOCTOU limb).
  M-Q2-4 — the node count cap raised by one (asserting mutant, ledger .1/.5).
"""
import hashlib
import os
import pathlib
import subprocess
import sys

ARMS = [
    (
        "M-Q2-1",
        pathlib.Path("mapper/store.py"),
        b"for event in yaml.parse(yml_text):",
        b"for event in []:  # M-Q2-1: prescan bypassed",
        [
            "tests/test_ingestion_limits.py::test_at_111_anchor_refused_names_anchor_and_map",
            "tests/test_ingestion_limits.py::test_at_110_depth_65_refuses_naming_depth_limit",
        ],
    ),
    (
        "M-Q2-2",
        pathlib.Path("mapper/osopen.py"),
        b"if len(data) > cap:",
        b"if False and len(data) > cap:  # M-Q2-2: read re-check removed",
        ["tests/test_ingestion_limits.py::test_at_109_byte_cap_grow_between_stat_and_read_refuses"],
    ),
    (
        "M-Q2-4",
        pathlib.Path("mapper/store.py"),
        b"if len(graph.nodes) > MAX_NODES:",
        b"if len(graph.nodes) > MAX_NODES + 1:  # M-Q2-4: node cap raised",
        ["tests/test_ingestion_limits.py::test_at_112_node_count_cap_plus_1_refuses"],
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
print("arms:", sum(len(n) for _, _, _, _, n in ARMS), "bad:", bad)
sys.exit(1 if bad else 0)
