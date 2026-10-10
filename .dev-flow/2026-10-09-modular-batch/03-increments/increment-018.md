# Increment 018 — LLR-MOD.1.3 · `B8 — nav concern to the NavOps mixin; action_open_ficha stays in the core`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-018.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `018` (B8) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `LLR-MOD.1.3` (navigation module owns its census methods) |
| Acceptance | full suite at the B3–B9 gate · the permanent guard tests (`test_mod_bodies.py`, `test_mod_parity.py`, `test_mod_dispatch.py`) |
| Agent | Product move `47bed83` — orchestrator script (`mixin_move.py`, AST cut/paste; Claude Opus 5.5). No test follow-up commit. Gate — orchestrator. |
| Date | `2026-10-10` |

---

## 1 · What changed

- **The nav concern moved.** 8 nav methods (86 lines) moved byte-identically from `mapper/screens/map/screen.py` into `mapper/screens/map/navigation.py` — the module that already held `NavigationModel` (A5a) — as `class NavOps` (`navigation.py:62`). `screen.py` composes it as a mixin base.
- **Recorded deviation: `action_open_ficha` stays in the core.** It constructs `MapScreen` itself; moving it would need a `navigation ↔ screen` import cycle or a changed body. Self-construction is a core concern. The deviation is recorded here and later in `docs/ARCHITECTURE.md` at B12 (`d4948b2`).
- No patch surface moved in this increment and no census test needed a follow-up edit.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/navigation.py` | source | LLR-MOD.1.3 | `NavOps` mixin added (+86) beside `NavigationModel` |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.3 | nav methods removed; mixin base added (−76/+2) |

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
| **0 · unit** | `core` · `full` | `tests/test_mod_bodies.py` (per-method byte-identity + undefined-globals) | passed — gate transcript |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_dispatch.py` (disjoint names, core-only BINDINGS) | passed — gate transcript |
| **B · black-box** | `core` · `full` | AT-065 parity (`test_mod_parity.py`, both widths) | passed — gate transcript |
| **Gate** | — | full suite | **3060 passed, 24 deselected, 3 xfailed, 0 failed, exit=0** (`b3b9-gate-full-suite.transcript`) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none hand-applied — pure move; the suite's permanent RED controls ran inside the gate |
| Instrument | suite-owned tmp-copy mutants |
| Where it ran | the main checkout |
| Transcript | `b3b9-gate-full-suite.transcript` (GREEN); no increment-local hand mutation transcript exists |
| Restore proven by | n/a — no hand mutation |
| Bytecode cache | gate run under `python -B` |
| Arms resolved at baseline | the permanent controls in force at this gate: `test_mod_bodies.py` (2 mutant kinds), `test_mod_parity.py` (1), `test_mod_dispatch.py` (3 mutant kinds) |
| Verdict granularity | per resolved node id, per facts sheet |
| Arms that stayed GREEN | none recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none for a hand mutation — no new assertion in this increment. The move's RED side is carried by the permanent controls below (C-20 satisfied by the batch-standing battery; the "no new assertion" form). |

| Field | Value |
|---|---|
| **Mutation verdicts** | Ran inside the B3–B9 gate, per the facts sheet: `test_mod_bodies.py` — one-token body mutation in a moved method (tmp copy) → RED (KILLED); deleted import in a new module → RED (KILLED). `test_mod_parity.py` — painted-string mutant in a subprocess → RED (KILLED). `test_mod_dispatch.py` — duplicated handler names → RED; `BINDINGS` in a mixin → RED; `HintsOps` dropped → RED. Arms that stayed GREEN: none recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_bodies.py` | one-token body mutation / deleted import (tmp copy) | RED arms per facts sheet (run at every gate) |
| `tests/test_mod_parity.py` | painted-string mutant (subprocess) | RED arm per facts sheet |
| `tests/test_mod_dispatch.py` | duplicate names / mixin BINDINGS / dropped mixin | RED arms per facts sheet |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED at this gate's tmp-copy arms before the PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the shipped `mapper/screens/map/navigation.py` source | `test_mod_bodies.py` compares each moved method's `ast.dump` against the Inc-0 baseline JSON on disk | passed at the gate |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact (the shipped NavOps methods), asserted on disk against the Inc-0 baseline |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| b3b9-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/b3b9-gate-full-suite.transcript | 027b617017a980f3dab46ff218e837f1e497e9b97c03c4b73cae2a0153e7e6d3 |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact, at the declared home, digest from `_facts/evidence-digests.md` |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "every census method appears exactly once across the package" and "no module-level `mapper.app` import under `screens/`" (batch-standing) |
| If the result is an ABSENCE, what made the search wide enough | the full census roster (`test_mod_bodies.py`) and the AST import scan (`test_mod_dispatch.py` / `test_mod_deps.py`) — no hand-scoped subset |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_mod_bodies.py` exactly-once arms; the LLR-MOD.2.2 import ban |
| Conjunctive criteria: one mutation per conjunct | no new conjunctive criterion |
| Synthetic instance of the absent case | the tmp-copy mutants of the guards (deleted/duplicated method, restored import) per the facts sheet |
| **Positive control for every probe that returned an ABSENCE** | the same unmodified guards report the present cases on the real tree (GREEN at the gate) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rln "NavOps" tests mapper` | `mapper/screens/map/navigation.py`, `mapper/screens/map/screen.py` only — no test hand-lists `NavOps` |
| B2 file moved on disk | `grep -n "def action_.*nav\|def _nav" mapper/screens/map/screen.py` | nav handlers gone from the core; `action_open_ficha` remains **by the recorded deviation** |
| B3 byte-identical golden captures this source | `grep -rl "navigation" tests/goldens/** 2>/dev/null` | not fired — no golden directory |
| B4 artifact produced here is consumed elsewhere | `grep -rln "navigation" mapper/screens/map/` | consumed by `screen.py` (composition) |

| A3 | interface consumed by another module changed | `grep -rn "NavigationModel" mapper/screens/` | `screens/map/screen.py` and `screens/repo.py` still import it from `mapper.screens.map.navigation`; re-validated at the gate |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B4, A3 fired with the hits above, re-validated green in the gate; B3 did not fire) |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — no correction; the one deviation (`action_open_ficha`) was declared in the commit message and enumerated as a single site, not edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| nav methods in `mapper/screens/map/screen.py` | 0 hits for the moved roster | yes | `screen.py` post-B8 is 78 lines lighter; bodies baseline diff empty at the gate |

### Signed-balance test ledger

No test files added or deleted; the B3–B9 gate count (3060) is unchanged by this increment. Per-increment collection delta: 0.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only; group review B1–B12) · **APPROVE-WITH-NITS, 0 HIGH / 0 MED** · "B8 deviation sound" is the review's explicit finding; no HIGH/MED against this increment. 4 LOW found in the group, none naming B8. |

---

## 5 · Risks

- The `action_open_ficha` deviation is a permanent census exception: any future move of it must solve the `navigation ↔ screen` cycle (e.g. a factory) — until then the census roster must keep assigning it to the core, and LLR-MOD.7.2's census diff will redden a silent move.
- `NavOps` shares the map's navigation state with `NavigationModel` in the same file; the §3 rule that `screens/map` otherwise imports only its allow-list is only enforced mechanically from B12 (AT-071).

## 6 · Pending items / spec deviations

- **Deviation (recorded, accepted):** `action_open_ficha` stays in `screen.py`, deviating from the census classification that would put it with nav. Rationale in the commit body (`47bed83`): it constructs `MapScreen`; moving it needs an import cycle or a changed body. Recorded in `docs/ARCHITECTURE.md` at B12 (`d4948b2`).

## 7 · Suggested next task

B9 — the search concern to `SearchingOps`, with the `MAX_RENDER_NODES`/`SearchIndex` patch repoints (`increment-019`).

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
| 9 | Coverage claims verified **on disk** | all | ✓ | 3060 passed at the gate |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | bodies/parity/dispatch arms KILLED (§4) |
| 12 | **Instrument RED-proof** declared | all | ✓ | 3 instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | none — no correction (§4) |
| 14 | **Emitted-form assertion** declared | all | ✓ | shipped `navigation.py` vs Inc-0 baseline |
| 15 | **Independent review** names somebody | all | ✓ | group review B1–B12 |
| 16 | **Evidence files** declared | all | ✓ | 1 file with sha256 |
