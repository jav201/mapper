# Increment 005 — LLR-MOD.1.1, LLR-MOD.3.1 · `A5a — NavigationModel to mapper/screens/map/navigation.py (the map package is born)`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-005.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `005` (A5a) |
| Lane (if the batch forked) | n/a — the spine is serial |
| Requirement(s) | `LLR-MOD.1.1` (`screens/map/navigation.py` owns `NavigationModel` only, re-exported; the package lands before B0 because `MapScreen` itself reads it) · `LLR-MOD.3.1` (imports keep resolving with identity) |
| Acceptance | `AT-065` parity · white-box `tests/test_mod_bodies.py` (byte-identical body), `tests/test_mod_parity.py` (0 diffs) · gate: full suite (a5a-b0 transcript — see the honest note in §4) |
| Agent | Product move: **Kimi (`kimi-for-coding`) unit in an isolated worktree**, RED + sha256-restore in its own log (session scratch — not stored as an evidence file). Gate: **orchestrator (Claude Opus 5.5)**. Group review: `code-reviewer` (Claude Sonnet). This packet: Kimi unit MODPKT-p1. |
| Date | `2026-10-10` (commit 911ce1f, 01:40 −0600) |

---

## 1 · What changed

- **`mapper/screens/map/` package created** with a re-export-only `__init__.py` (docstring-only, no logic, no imports — the same rule as the root `mapper/__init__.py` row of ARCHITECTURE §2; B0 adds the `MapScreen` re-export later).
- **`NavigationModel` moved to `mapper/screens/map/navigation.py` (new, 57 lines):** the class — and only the class — lands in the package, ahead of B0, because `MapScreen` itself reads it (premise 11 / the MOD-REQ2 spine order). Body byte-identical (AST-checked against the Inc-0 baseline).
- **`mapper/app.py` shrinks by ~40 lines** and imports `NavigationModel` from `.screens.map.navigation` (`app.py:73`), re-exporting it so the test sites resolve with identity (LLR-MOD.3.1). `MapScreen` inside `app.py` constructs it as before.
- `docs/ARCHITECTURE.md` records the landed `screens/map` package rows.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/navigation.py` | source | LLR-MOD.1.1 | new — owns `NavigationModel` |
| `mapper/screens/map/__init__.py` | source | LLR-MOD.1.2 | new — package identity only, no logic/imports until B0 |
| `mapper/app.py` | source | LLR-MOD.1.1, LLR-MOD.3.1 | ~40 lines cut; `from .screens.map.navigation import NavigationModel` + re-export |
| `docs/ARCHITECTURE.md` | doc | | `screens/map` rows record the landed package |

| Count | Value |
|---|---|
| **SOURCE files** | **3 / 4** |
| Test files | 0 (none needed — no pin named the class's file) |
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

**Gate (`a5a-b0-gate-full-suite.transcript`, 9e070362…):** `3 failed, 2997 passed, 24 deselected, 3 xfailed in 1528.19s`, `exit=1`. **Honest account:** the orchestrator ran one gate over A5a **and** B0 together, and no A5a-only gate transcript exists. The 3 failures are B0-stage stranded census/follow-up tests, not A5a regressions:

- `tests/test_arch_osopen_callers.py::test_outside_app_only_the_allowed_names_are_imported_from_osopen`
- `tests/test_fold.py::test_llr_n06_2_3_every_repainted_region_coerces_what_it_paints`
- `tests/test_inc3_census.py::test_a98_the_screen_imports_painted_ids_by_name_never_by_getattr` (`assert 'painted_ids' in {'LayeredRenderer', 'MAX_RENDER_NODES', 'pan_extent'}` — the screen's import block changed under B0)

All three were fixed in follow-up commits `9e87ccd` (A5b) and `bc2ff81` (B0 follow-up). The next full gate (a5b, transcript cited in increment-007) shows the repaired state; the final 0-failure state of the batch is recorded at the B10+B11+B12 gate.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | the Kimi unit's own RED (mutation of the moved surface + sha256 restore) — recorded in the unit's log in session scratch, **not stored** as an evidence file |
| Instrument | Kimi unit hand in its isolated worktree |
| Where it ran | the A5a worktree — no other session reading it |
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
| the painted screen through the scripted session | `tests/test_mod_parity.py` vs `mod_parity_118.txt`/`mod_parity_87.txt` | 0 diffs at both widths (2997 passed at the gate; the 3 failures are census tests, not parity) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact, asserted on the emitted painted lines |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| a5a-b0-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a5a-b0-gate-full-suite.transcript | 9e070362760d219c51163119272861a5733b18b8580194d6b59286f6b9106424 |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact (the shared A5a+B0 gate), digest of its stored bytes re-verified on disk 2026-10-10 — match |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes, a deliberate one: `map/__init__.py` holds **no logic and no imports** until B0 — the package is identity-only |
| If the result is an ABSENCE, what made the search wide enough | the whole file — 8 lines, docstring only |
| Guard labelled as protecting a CONCLUSION, not a behaviour | the B12 `test_mod_structure.py -k b0` arm asserts the `__init__` is re-export-only (0 logic) |
| Conjunctive criteria: one mutation per conjunct | the no-logic and no-import conjuncts are one file — a single added import or statement breaks both (B0 mutants) |
| Synthetic instance of the absent case | a tmp-copy `__init__.py` with an added import/statement |
| **Positive control for every probe that returned an ABSENCE** | every other package `__init__.py` with content is the known-present case the same structure probe sees at B0, when the `MapScreen` re-export lands there legitimately |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `git grep -ln "NavigationModel" 911ce1f -- tests/` | 1 test file imports it (via `mapper.app`) — green at the gate |
| B2 file moved on disk | `git show 911ce1f:mapper/app.py \| grep -c "^class NavigationModel"` | 0 — the class is gone from `app.py` |
| B3 byte-identical golden | not applicable | not fired |
| B4 artifact produced here is consumed elsewhere | `git grep -ln "NavigationModel" 911ce1f -- mapper/` | consumers: `mapper/app.py` (import + re-export, 6 use sites incl. `MapScreen`) — the sanctioned `app → screens/map` edge |

| A3 | interface consumed by another module changed | `git show 911ce1f:mapper/app.py \| grep -n "NavigationModel"` | `app.py:73` imports from `.screens.map.navigation`; `MapScreen` constructs it at :731, :987, :1034, :1160, :3636, :3647 — same objects through the re-export |

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
| `class NavigationModel` in `mapper/app.py` | 0 hits at 911ce1f | yes | probe output above; gate 2997 passed |

### Signed-balance test ledger

`post = base − deleted + added` → collected per-layer counts are not recorded; gate trajectory: 2987 passed (a2a3) → 2997 passed / 3 failed (a5a-b0, the 3 B0-stage census follow-ups) → the a5b gate (transcript cited in increment-007) → 0 failed at the B10+B11+B12 gate (b10b12 transcript, cited in a later packet).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) — group review **A2–A4 + B0**, covering this increment per the facts sheet · **APPROVE-WITH-NITS, 0 HIGH** · `NavigationModel` verified byte-identical (AST) in `screens/map/navigation.py`; re-export complete; `map/__init__.py` identity-only. Group findings (3 MED vacuous census scans → post-review MODREV repair; 1 LOW carried) are recorded in increment-003 §4b. |

---

## 5 · Risks

- The 3 gate failures in the shared transcript are B0's stranded follow-ups, but they show the cost of the A5a→B0 pairing: census tests that pin `app.py`'s import block redden the moment the screen wholesale-moves. They were repaired before the next increment closed; the backlog owns any recurrence.
- `NavigationModel` now lives in the package while its main reader (`MapScreen`) is still in `app.py` — a temporary cross-boundary read that B0 resolves by moving the screen into the same package.

## 6 · Pending items / spec deviations

- The 3 census follow-ups were fixed in 9e87ccd + bc2ff81 (B0-stage commits), recorded in the facts sheet; none open against A5a itself.
- None.

## 7 · Suggested next task

B0 (increment 006): `MapScreen` whole → `screens/map/screen.py`, by the orchestrator's move/prune scripts.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 / 4 |
| 2 | Tests written in this same increment | all | ✓ | 0 needed — permanent controls carry the move (§1) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | n/a — no unit meets the criterion |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — none stored; permanent controls in force; unit-level RED per facts sheet |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — 5 probes, 4 fired |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — group A2–A4+B0, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | serial spine, single lane |
| 8 | Frozen interfaces untouched | all | ✓ | body-preserving move; F1–F5 freeze intact |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate transcript 2997 passed / 3 failed cited verbatim, with the fix commits named |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — the identity-only `__init__` absence |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — permanent controls listed; none stored for this increment |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 2 permanent instruments |
| 13 | **Correction population** declared | all | ✓ | §4 — none (no correction) |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — painted session on emitted lines |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` group review |
| 16 | **Evidence files** declared | all | ✓ | §4 — 1 file, sha256 re-verified |
