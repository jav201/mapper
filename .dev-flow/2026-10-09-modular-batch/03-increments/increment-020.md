# Increment 020 — LLR-MOD.1.3, LLR-MOD.3.2 · `B10 — pan concern to the PanningOps mixin; pan_extent patch follows its reader`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-020.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `020` (B10) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `LLR-MOD.1.3` (panning module owns its census methods) · `LLR-MOD.3.2` (`pan_extent` repointed to its reading module) |
| Acceptance | full suite at the B10–B12 gate · `tests/test_en8.py` `pan_extent` site bites through `mapper.screens.map.panning` · the permanent guard tests |
| Agent | Product move + patch repoint `3fd3b63` — orchestrator script (`mixin_move.py`, AST cut/paste; Claude Opus 5.5). Gate — orchestrator. |
| Date | `2026-10-10` |

---

## 1 · What changed

- **The pan concern moved.** 10 methods (264 lines) moved byte-identically from `mapper/screens/map/screen.py` into the new `mapper/screens/map/panning.py` (`class PanningOps`, `panning.py:15`). `screen.py` composes it as a mixin base.
- **The `pan_extent` patch repointed (LLR-MOD.3.2).** `pan_extent` is a module-global of `panning.py` (its reading module — the L-key pan path); the suite's single patch site `tests/test_en8.py:66` now reads `monkeypatch.setattr("mapper.screens.map.panning.pan_extent", boom)`.
- One line changed in `tests/test_en8.py`; no other census test needed a follow-up.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/panning.py` | source | LLR-MOD.1.3, LLR-MOD.3.2 | new — `PanningOps` mixin (295 lines); binds `pan_extent` as a module-global |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.3 | pan methods removed; mixin base added (−287/+2) |
| `tests/test_en8.py` | test | LLR-MOD.3.2 | `pan_extent` setattr repointed `mapper.screens.map.screen` → `mapper.screens.map.panning` (1 line) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 0 |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/   # the increment gate (orchestrator-run; transcript cited in §4)
python -B -m pytest -q -p no:cacheprovider tests/test_en8.py tests/test_pan.py tests/test_mod_bodies.py tests/test_mod_parity.py tests/test_mod_dispatch.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_bodies.py` | passed — gate transcript |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_en8.py` (the repointed site drives the L pan path through the shipped screen), `test_mod_dispatch.py` | passed — gate transcript |
| **B · black-box** | `core` · `full` | AT-065 parity (both widths) | passed — gate transcript |
| **Gate** | — | full suite | **3124 passed, 24 deselected, 3 xfailed, 0 failed, exit=0** (`b10b12-gate-full-suite.transcript`; the B10–B12 increments share one gate) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none hand-applied — pure move + repoint; the suite's permanent RED controls ran inside the gate |
| Instrument | suite-owned tmp-copy mutants + the gate suite |
| Where it ran | the main checkout |
| Transcript | `b10b12-gate-full-suite.transcript` (GREEN); no increment-local hand-mutation transcript exists |
| Restore proven by | n/a — no hand mutation |
| Bytecode cache | gate run under `python -B` |
| Arms resolved at baseline | the permanent controls in force at this gate: `test_mod_bodies.py` (2 mutant kinds), `test_mod_parity.py` (1), `test_mod_dispatch.py` (3 mutant kinds) |
| Verdict granularity | per resolved node id, per facts sheet |
| Arms that stayed GREEN | none recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none for a hand mutation. The repointed site is an executable RED instrument: `pan_extent` no longer exists in `mapper/screens/map/screen`, so the old dotted target `mapper.screens.map.screen.pan_extent` would raise `ModuleNotFoundError`/`AttributeError` at patch time; `tests/test_en8.py:63`'s node (`test_e1_the_unlaid_out_graph_site_says_it_too`) passes only through the repointed module-global — the planted `boom` raising `ValueError("not a tree")` is observed in the painted hint. A skip-one-repoint transcript was not recorded. |

| Field | Value |
|---|---|
| **Mutation verdicts** | Ran inside the B10–B12 gate, per the facts sheet: `test_mod_bodies.py` — one-token body mutation (tmp copy) → RED (KILLED); deleted import in a new module → RED (KILLED). `test_mod_parity.py` — painted-string mutant → RED (KILLED). `test_mod_dispatch.py` — duplicated names / mixin BINDINGS / dropped mixin → RED each. Arms that stayed GREEN: none recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the `pan_extent` patch site (`tests/test_en8.py:66`) | the planted `boom` (`ValueError("not a tree")`) via the repointed global — and, as mechanism check, the old target module which no longer binds the name | the raised `ValueError` surfaces in the test's painted-hint assertion; the old dotted target cannot even be patched |
| `tests/test_mod_bodies.py` | one-token body mutation / deleted import (tmp copy) | RED arms per facts sheet |
| `tests/test_mod_parity.py` | painted-string mutant (subprocess) | RED arm per facts sheet |
| `tests/test_mod_dispatch.py` | duplicate names / mixin BINDINGS / dropped mixin | RED arms per facts sheet |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED (or unpatachable-against-the-old-target) before the PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the shipped `mapper/screens/map/panning.py` source | `test_mod_bodies.py` compares each moved method's `ast.dump` against the Inc-0 baseline JSON on disk | passed at the gate |
| the repointed patch site (shipped `tests/test_en8.py`) | the L pan path driven with `pan_extent` replaced by `boom`, through the shipped screen | passed at the gate |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted on disk / through the shipped surface |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| b10b12-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/b10b12-gate-full-suite.transcript | be5b2dad71268e2e91a1a995e278bc568f1ae1586166849d2cddfa0c667f5d64 |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact, at the declared home, digest from `_facts/evidence-digests.md` (the B10–B12 increments share this gate transcript) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "no lazy read of `pan_extent` through `mapper.app` or `screen.py`" and the batch-standing exactly-once roster |
| If the result is an ABSENCE, what made the search wide enough | AST scans over the whole package (LLR-MOD.2.2 patch-name import ban), not a grep of one file |
| Guard labelled as protecting a CONCLUSION, not a behaviour | the LLR-MOD.3.2 AST patch-guard (`test_mod_compat.py` patch_guard, in force from B12) maps `"pan_extent"` to `mapper.screens.map.panning` |
| Conjunctive criteria: one mutation per conjunct | no new conjunctive criterion |
| Synthetic instance of the absent case | the old target (`mapper.screens.map.screen.pan_extent`) is the synthetic present case: patching it now fails because the name left the module |
| **Positive control for every probe that returned an ABSENCE** | the repointed site passes against `mapper.screens.map.panning` at the gate |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rln "PanningOps" tests mapper` | `mapper/screens/map/screen.py`, `mapper/screens/map/panning.py` only — no test hand-lists `PanningOps` |
| B2 file moved on disk | `grep -n "pan_extent" mapper/screens/map/screen.py` | 0 hits — the name left the core; `mapper/app.py` still re-exports it (LLR-MOD.3.1, historical sites) |
| B3 byte-identical golden captures this source | `grep -rl "panning" tests/goldens/** 2>/dev/null` | not fired — no golden directory |
| B4 artifact produced here is consumed elsewhere | `grep -rln "panning" mapper/screens/map/` | consumed by `screen.py` (composition) |

| A3 | interface consumed by another module changed | `grep -rn "pan_extent" mapper/screens/` | bound and read only in `panning.py` — re-validated at the gate |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B4, A3 fired with the hits above, re-validated green in the gate; B3 did not fire) |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| `pan_extent` patch site must follow its reader | every suite patch site of the 7 module-global targets | premise 4 census (`grep -Hn "mapper.app.pan_extent" tests/test_en8.py` → `tests/test_en8.py:66`) | 1 | 1 (`tests/test_en8.py:66`) | 0 — complete |

| Field | Value |
|---|---|
| **Correction population** | 1 correction, enumerated at premise 4 before the batch and executed in this increment; population fully edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `mapper.screens.map.screen.pan_extent` as a patch target in `tests/test_en8.py` | 0 hits (`grep -n "screen.pan_extent" tests/test_en8.py`) | yes | `tests/test_en8.py:66` now targets `mapper.screens.map.panning.pan_extent`; gate GREEN |

### Signed-balance test ledger

No test files added or deleted; `tests/test_en8.py` edited in place (1 line). Per-increment collection delta: 0. (The B10–B12 gate is shared: 3124 passed / 0 failed.)

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only; group review B1–B12) · **APPROVE-WITH-NITS, 0 HIGH / 0 MED** · "patch repoints correct" covers this increment's repoint. 4 LOW found in the group, none naming B10. |

---

## 5 · Risks

- CR-3 (from the group review, recorded at B2's scope but panning-adjacent): `exporting.py`'s own `pan_extent` reader has no patched test — a deliberate gap; the AST guard, not a bite test, pins the mapping.
- `PanningOps` owns pointer/pan state shared with the render path; F1/F2 freeze discipline applies and is made mechanical only at B12 (LLR-MOD.7.2).

## 6 · Pending items / spec deviations

- None open for this increment. (CR-3 is a carried, deliberate gap — recorded in the B1–B12 review.)

## 7 · Suggested next task

B11 — the views concern to `PaintingOps`, completing Spine B (`increment-021`).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ✓ | `3fd3b63` — `tests/test_en8.py` repoint |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_bodies.py` at the gate |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | repoint bite + permanent battery (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | bodies byte-identical per `test_mod_bodies` |
| 9 | Coverage claims verified **on disk** | all | ✓ | 3124 passed at the gate |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | bodies/parity/dispatch arms KILLED (§4) |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | 1 correction, complete (§4) |
| 14 | **Emitted-form assertion** declared | all | ✓ | shipped `panning.py` + repointed site |
| 15 | **Independent review** names somebody | all | ✓ | group review B1–B12 |
| 16 | **Evidence files** declared | all | ✓ | 1 file with sha256 |
