# Increment 004 — LLR-MOD.1.1, LLR-MOD.3.1 · `A3 — ConstructScreen to mapper/screens/construct.py`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-004.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `004` (A3) |
| Lane (if the batch forked) | n/a — the spine is serial |
| Requirement(s) | `LLR-MOD.1.1` (`screens/construct.py` owns `ConstructScreen`, re-exported) · `LLR-MOD.3.1` (imports keep resolving with identity) |
| Acceptance | `AT-065` parity · white-box `tests/test_mod_bodies.py` (byte-identical body), `tests/test_mod_parity.py` (0 diffs) · gate: full suite green (a2a3 transcript, 2987/0) |
| Agent | Product move: **Kimi (`kimi-for-coding`) unit in an isolated worktree**, RED + sha256-restore in its own log (session scratch — not stored as an evidence file). Gate: **orchestrator (Claude Opus 5.5)**. Group review: `code-reviewer` (Claude Sonnet). This packet: Kimi unit MODPKT-p1. |
| Date | `2026-10-10` (commit 9f5975e, 01:25 −0600) |

---

## 1 · What changed

- **`ConstructScreen` moved to `mapper/screens/construct.py` (new, 61 lines):** the map-construction modal leaves `mapper/app.py`; body byte-identical (AST-checked against the Inc-0 baseline).
- **`mapper/app.py` shrinks by ~49 lines** and keeps the name re-exported — every `from mapper.app import ConstructScreen` site resolves to the same object (LLR-MOD.3.1).
- `docs/ARCHITECTURE.md` records the landed `screens/construct` row. No test file needed an edit (no source-reading pin named the class's file).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/construct.py` | source | LLR-MOD.1.1 | new — owns `ConstructScreen` |
| `mapper/app.py` | source | LLR-MOD.1.1, LLR-MOD.3.1 | ~49 lines cut; re-export keeps the name |
| `docs/ARCHITECTURE.md` | doc | | `screens/construct` row records the landed file |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 0 (none needed — see §1) |
| Doc files | 1 (outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py tests/test_mod_parity.py
python -B -m pytest -q -p no:cacheprovider tests/    # the increment gate (full suite)
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | none meeting the criterion standalone | n/a |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_bodies.py` (byte-identical), `tests/test_mod_parity.py` (0 diffs) | passed |
| **B · black-box** `AT-NNN` ↔ story | `core` · `full` | AT-065 painted session | passed |

**Gate (`a2a3-gate-full-suite.transcript`, 79ea316f…):** `2987 passed, 24 deselected, 3 xfailed in 1538.62s`, `exit=0` — the same shared gate as A2 (see increment-003); it is the gate evidence for both increments. No A3-only gate transcript exists.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | the Kimi unit's own RED (mutation of the moved surface + sha256 restore) — recorded in the unit's log in session scratch, **not stored** as an evidence file |
| Instrument | Kimi unit hand in its isolated worktree |
| Where it ran | the A3 worktree — no other session reading it |
| Transcript | not recorded at the evidence home |
| Restore proven by | sha256 equality in the unit log (facts sheet: "each with its RED + sha256 restore in its own log") |
| Bytecode cache | `python -B`, `-p no:cacheprovider` |
| Arms resolved at baseline | not recorded |
| Verdict granularity | per node id (unit log) |
| Arms that stayed GREEN | not recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none stored — pure code move; the permanent gate control set (below) is the stored RED evidence; the unit-level RED ran and was restored byte-identically per the facts sheet, but its bytes are not recorded. |

| Field | Value |
|---|---|
| **Mutation verdicts** | In force at this gate, from Inc-0: `tests/test_mod_bodies.py` (one-token body mutation + deleted import on a tmp copy → RED) and `tests/test_mod_parity.py` (painted-string mutant → RED). `tests/test_mod_dispatch.py` not yet in force (lands at B1). Increment-specific battery: none stored. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_bodies.py` | one-token body mutation / deleted import on tmp copy | baseline diff / undefined-global report (Inc-0 RED arms, permanent) |
| `tests/test_mod_parity.py` | painted-string mutant in subprocess | painted-line diff (Inc-0 RED arm, permanent) |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 2 instruments — both shown RED at Inc-0 and permanent; no new instrument in this increment |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the painted screen through the scripted session | `tests/test_mod_parity.py` vs `mod_parity_118.txt`/`mod_parity_87.txt` | 0 diffs at both widths (gate 2987/0) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact, asserted on the emitted painted lines |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| a2a3-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a2a3-gate-full-suite.transcript | 79ea316f511a8a7e8514e01351d13fec2aa3c9070c4f087df46f99aa8499dff1 |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact (the shared A2+A3 gate), digest of its stored bytes re-verified on disk 2026-10-10 — match |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | no new one — the move claims presence (the class lives in exactly one home), not absence |
| If the result is an ABSENCE, what made the search wide enough | n/a |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_mod_bodies.py` exactly-once arm (no method lost or duplicated by the move) |
| Conjunctive criteria: one mutation per conjunct | the exactly-once + byte-identical conjuncts each have their own mutant (Inc-0 arms) |
| Synthetic instance of the absent case | n/a — no absence claim |
| **Positive control for every probe that returned an ABSENCE** | n/a |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `git grep -ln "ConstructScreen" 9f5975e -- tests/` | 4 test files name the class (test_en5, test_en7, test_inc9c, test_seed_safety) — all import via `mapper.app`, all green at the gate |
| B2 file moved on disk | `git show 9f5975e:mapper/app.py \| grep -c "^class ConstructScreen"` | 0 — the class is gone from `app.py` |
| B3 byte-identical golden | not applicable | not fired |
| B4 artifact produced here is consumed elsewhere | `git grep -ln "ConstructScreen" 9f5975e -- mapper/` | consumers: `mapper/app.py` (re-export), `screens/construct.py` — in-tree |

| A3 | interface consumed by another module changed | `git grep -n "ConstructScreen" 9f5975e -- mapper/screens/factory.py` | factory constructs it via the `mapper.app` re-export — the legal edge direction (`app` → `screens` only) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B4, A3 fired; B3 not applicable). All hits re-validated green at the gate |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — no correction; a pure extraction with no claim changed |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `class ConstructScreen` in `mapper/app.py` | 0 hits at 9f5975e | yes | probe output above; gate 2987/0 |

### Signed-balance test ledger

`post = base − deleted + added` → collected per-layer counts are not recorded; gate trajectory: 2987 passed / 0 failed at the shared a2a3 gate (covers A2 + A3).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) — group review **A2–A4 + B0**, covering this increment · **APPROVE-WITH-NITS, 0 HIGH** · `ConstructScreen` verified byte-identical (AST) in `screens/construct.py`; re-export complete; no back-edge. Group findings (3 MED vacuous census scans → post-review MODREV repair; 1 LOW carried) are recorded in increment-003 §4b. |

---

## 5 · Risks

- No test file changed in this increment — the move's safety rests entirely on the permanent byte-identity/parity controls and the re-export; a dropped re-export would be caught by the B12 `test_mod_compat.py -k reexport` identity arm, not by anything here.
- `factory.py` still imports the class through `mapper.app`; the B12 dependency tests pin the allowed edge set.

## 6 · Pending items / spec deviations

- None.

## 7 · Suggested next task

A5a (increment 005): `NavigationModel` → `mapper/screens/map/navigation.py`, creating the `screens/map/` package ahead of B0.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ✓ | 0 needed — no pin named the class's file; permanent controls carry the move (§1) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | n/a — no unit meets the criterion |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — none stored; permanent controls in force; unit-level RED per facts sheet |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — 5 probes, 4 fired |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — group A2–A4+B0, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | serial spine, single lane |
| 8 | Frozen interfaces untouched | all | ✓ | body-preserving move; F1–F5 freeze intact |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate transcript 2987/0 cited verbatim |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — no new absence; exactly-once guard named |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — permanent controls listed; none stored for this increment |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 2 permanent instruments |
| 13 | **Correction population** declared | all | ✓ | §4 — none (no correction) |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — painted session on emitted lines |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` group review |
| 16 | **Evidence files** declared | all | ✓ | §4 — 1 file, sha256 re-verified |
