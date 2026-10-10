# Increment 021 — LLR-MOD.1.3 · `B11 — views concern to the PaintingOps mixin; Spine B complete`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-021.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `021` (B11) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `LLR-MOD.1.3` (painting module owns its census methods; all 11 concern modules present) |
| Acceptance | full suite at the B10–B12 gate · the permanent guard tests (`test_mod_bodies.py`, `test_mod_parity.py`, `test_mod_dispatch.py`) |
| Agent | Product move `e7fff33` — orchestrator script (`mixin_move.py` / `screen_prune.py`, AST cut/paste; Claude Opus 5.5). No test follow-up commit. Gate — orchestrator. |
| Date | `2026-10-10` |

---

## 1 · What changed

- **The views concern moved — Spine B complete.** 22 methods (686 lines, `refresh_canvas` included) moved byte-identically from `mapper/screens/map/screen.py` into the new `mapper/screens/map/painting.py` (`class PaintingOps`, `painting.py:27`). `screen.py` is now the core: lifecycle + `action_open_ficha`, **840 lines**, composing all 11 concern mixins.
- `refresh_canvas` was the batch's largest funnel (25 call sites in 9 concerns, R-2/R-3 of the contract); its body moved unchanged and its cross-concern call surface is what the F1/F2 freeze (LLR-MOD.7.2) makes mechanical at B12.
- No patch surface and no census test moved in this increment; no test file was edited.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/painting.py` | source | LLR-MOD.1.3 | new — `PaintingOps` mixin (741 lines) |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.3 | views/paint methods removed; final mixin base added (−729/+2) — 840-line core |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 0 |
| Doc files | 0 |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/   # the increment gate (orchestrator-run; transcript cited in §4)
python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py tests/test_mod_parity.py tests/test_mod_dispatch.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_bodies.py` | passed — gate transcript |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_dispatch.py` (disjoint names across now-12 modules, core-only BINDINGS) | passed — gate transcript |
| **B · black-box** | `core` · `full` | AT-065 parity (both widths) over the fully-composed screen | passed — gate transcript |
| **Gate** | — | full suite | **3124 passed, 24 deselected, 3 xfailed, 0 failed, exit=0** (`b10b12-gate-full-suite.transcript`; shared with B10 and B12) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none hand-applied — pure move; the suite's permanent RED controls ran inside the gate |
| Instrument | suite-owned tmp-copy mutants |
| Where it ran | the main checkout |
| Transcript | `b10b12-gate-full-suite.transcript` (GREEN); no increment-local hand-mutation transcript exists |
| Restore proven by | n/a — no hand mutation |
| Bytecode cache | gate run under `python -B` |
| Arms resolved at baseline | the permanent controls in force at this gate: `test_mod_bodies.py` (2 mutant kinds), `test_mod_parity.py` (1), `test_mod_dispatch.py` (3 mutant kinds) |
| Verdict granularity | per resolved node id, per facts sheet |
| Arms that stayed GREEN | none recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none for a hand mutation — no new assertion in this increment. The move's RED side is carried by the permanent controls below (the "no new assertion" form of C-20). |

| Field | Value |
|---|---|
| **Mutation verdicts** | Ran inside the B10–B12 gate, per the facts sheet: `test_mod_bodies.py` — one-token body mutation (tmp copy) → RED (KILLED); deleted import in a new module → RED (KILLED). `test_mod_parity.py` — painted-string mutant → RED (KILLED). `test_mod_dispatch.py` — duplicated names / mixin BINDINGS / dropped mixin → RED each. Arms that stayed GREEN: none recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_bodies.py` | one-token body mutation / deleted import (tmp copy) | RED arms per facts sheet |
| `tests/test_mod_parity.py` | painted-string mutant (subprocess) | RED arm per facts sheet |
| `tests/test_mod_dispatch.py` | duplicate names / mixin BINDINGS / dropped mixin | RED arms per facts sheet |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED at this gate's tmp-copy arms before the PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the shipped `mapper/screens/map/painting.py` source | `test_mod_bodies.py` compares each moved method's `ast.dump` against the Inc-0 baseline JSON on disk | passed at the gate |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact (the shipped PaintingOps methods), asserted on disk against the Inc-0 baseline |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| b10b12-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/b10b12-gate-full-suite.transcript | be5b2dad71268e2e91a1a995e278bc568f1ae1586166849d2cddfa0c667f5d64 |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact, at the declared home, digest from `_facts/evidence-digests.md` (shared with B10/B12) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — the batch-standing "every census method exactly once" and "no `mapper.app` import under `screens/`"; with the core now minimal, "no concern method left in `screen.py`" becomes load-bearing for B12's AT-068 |
| If the result is an ABSENCE, what made the search wide enough | the full census roster (`test_mod_bodies.py`) — no hand-scoped subset |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_mod_bodies.py` exactly-once arms; `test_mod_structure.py` AT-068 lands at B12 and pins the core/module boundary |
| Conjunctive criteria: one mutation per conjunct | no new conjunctive criterion |
| Synthetic instance of the absent case | the tmp-copy mutants of the guards per the facts sheet |
| **Positive control for every probe that returned an ABSENCE** | the same unmodified guards report the present cases on the real tree (GREEN at the gate) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rln "PaintingOps" tests mapper` | `mapper/screens/map/screen.py`, `mapper/screens/map/painting.py` only — no test hand-lists `PaintingOps` |
| B2 file moved on disk | `grep -n "def refresh_canvas\|def _paint" mapper/screens/map/screen.py` | paint handlers gone from the core |
| B3 byte-identical golden captures this source | `grep -rl "painting" tests/goldens/** 2>/dev/null` | not fired — no golden directory; AT-065's text golden is path-agnostic (parity over the painted screen) and passed |
| B4 artifact produced here is consumed elsewhere | `grep -rln "painting" mapper/screens/map/` | consumed by `screen.py` (composition) |

| A3 | interface consumed by another module changed | `grep -rn "refresh_canvas" mapper/screens/map/` | defined in `painting.py`; ~25 call sites across the other concern modules call it via `self` (MRO) — byte-identical bodies per `test_mod_bodies` |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B4, A3 fired with the hits above, re-validated green in the gate; B3 did not fire) |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — no correction; pure move with no repoint and no census follow-up |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| views/paint methods in `mapper/screens/map/screen.py` | 0 hits for the moved roster | yes | `screen.py` is 840 lines (lifecycle + `action_open_ficha`); bodies baseline diff empty at the gate |

### Signed-balance test ledger

No test files added or deleted. Per-increment collection delta: 0. (The B10–B12 gate count, 3124 passed, is unchanged by this increment.)

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only; group review B1–B12) · **APPROVE-WITH-NITS, 0 HIGH / 0 MED** · "No MRO shadowing; imports exact" — the findings that cover this increment, since it completes the MRO with all 11 mixins. 4 LOW found in the group, none naming B11. |

---

## 5 · Risks

- `PaintingOps` owns every paint pass; a regression in `refresh_canvas`'s cross-concern call surface is the highest-blast-radius change left in the batch — LLR-MOD.7.2's census diff (B12) is the mechanical guard, and it did not exist until B12.
- The 840-line core still holds `action_open_ficha` (B8 deviation); AT-068 at B12 pins that boundary.

## 6 · Pending items / spec deviations

- None open for this increment.

## 7 · Suggested next task

B12 — `app.py __all__`, ARCHITECTURE landed, and the structure/deps/compat/census guard test files (`increment-022`).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ⚠ | none — pure move, no test needed a follow-up; the permanent guards cover it (§4) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_bodies.py` at the gate |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | `none` — no new assertion in this increment (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | bodies byte-identical per `test_mod_bodies` |
| 9 | Coverage claims verified **on disk** | all | ✓ | 3124 passed at the gate |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | bodies/parity/dispatch arms KILLED (§4) |
| 12 | **Instrument RED-proof** declared | all | ✓ | 3 instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | none — no correction (§4) |
| 14 | **Emitted-form assertion** declared | all | ✓ | shipped `painting.py` vs Inc-0 baseline |
| 15 | **Independent review** names somebody | all | ✓ | group review B1–B12 |
| 16 | **Evidence files** declared | all | ✓ | 1 file with sha256 |
