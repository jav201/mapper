# Increment 014 — LLR-MOD.1.3 · `B4 — undo concern to the UndoOps mixin`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-014.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `014` (Inc-B4) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `HLR-MOD.1 v1 / LLR-MOD.1.3` |
| Acceptance | no new test of its own — correctness rides on the permanent controls (`tests/test_mod_bodies.py` body oracle, `test_mod_parity.py`, `test_mod_dispatch.py`, `test_mod_deps.py`) · full-suite gate |
| Agent | The move (methods byte-identical, `mixin_move.py` + `screen_prune.py`) and the gate run: the orchestrator (Claude Opus 5.5). No separate Kimi-authored files in this increment (per the facts sheet: B1/B3 follow-ups and B12 tests by Kimi; B4–B6 are pure orchestrator moves). |
| Date | `2026-10-09/10` |

---

## 1 · What changed

**The undo concern moved out of `MapScreen` into the new `mapper/screens/map/undo.py` — the first plain Spine-B move after the spike, with no test follow-ups of its own.**

- The undo methods moved **byte-identically** into `mapper/screens/map/undo.py` (70 new lines); `screen.py` shrank by ~55 lines and composes `UndoOps`.
- No patch surface, no census and no §3 row ride this concern (per the batch plan: "undo concern — calls in only from drafts/edits/focus"), so the commit touches only the two source files.
- Dispatch correctness rides on the guards already in force: the byte-identical body oracle, the parity capture, the disjointness/BINDINGS guards and the §3 dependency test.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/undo.py` | source | LLR-MOD.1.3 | new — undo methods moved byte-identically (70 lines) |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.3 | undo methods pruned; composes `UndoOps` |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 0 |
| Doc files | 0 |

- ✓ The minimal Spine B shape — exactly the two source files the batch plan budgets per B-increment.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py tests/test_mod_dispatch.py tests/test_mod_deps.py -k arch
python -B -m pytest -q -p no:cacheprovider   # the increment gate — full suite, orchestrator-run
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_bodies.py` body oracle (undo methods now traced through the mixin MRO) | GREEN at gate |
| **A · white-box** ↔ LLR | `core` · `full` | `test_mod_dispatch.py` disjointness/BINDINGS; `test_mod_deps.py -k arch` | GREEN at gate |
| **B · black-box** | `core` · `full` | undo flows through `MapperApp` (existing suite) | GREEN at gate |
| **Increment gate — full suite** | — | whole suite | **3060 passed, 0 failed** (`b3b9-gate-full-suite.transcript`: `3060 passed, 24 deselected, 3 xfailed in 1583s`, exit=0) — the gate shared by B3–B9 |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none of its own — no new assertion in this increment (pure move) |
| Instrument | permanent gate controls |
| Where it ran | the orchestrator's checkout / the gate |
| Transcript | `b3b9-gate-full-suite.transcript` |
| Restore proven by | n/a |
| Bytecode cache | gate runs with `python -B` |
| Arms resolved at baseline | the body oracle resolves every census method (including the moved undo methods) exactly once |
| Verdict granularity | per node id |
| Arms that stayed GREEN | none named |

| Field | Value |
|---|---|
| **RED counterfactual** | none — no new assertion in this increment (C-20 `none` case for a pure move); the moved bodies' RED side is the permanent `test_mod_bodies.py` one-token mutant, in force at this gate. Transcript: `.dev-flow/2026-10-09-modular-batch/evidence/b3b9-gate-full-suite.transcript`. |

| Field | Value |
|---|---|
| **Mutation verdicts** | In force at this gate, per the facts sheet: `tests/test_mod_bodies.py` — one-token body mutation on a tmp copy → RED; deleted import in a new module → RED (the exact mutants that would catch a mangled undo move). `tests/test_mod_parity.py` — painted-string mutant in a subprocess → RED. `tests/test_mod_dispatch.py` — duplicate names / `BINDINGS` in a mixin / `HintsOps` dropped → RED. `tests/test_mod_deps.py` — synthetic import mutants → RED. Per-arm granularity; no arm reported inert. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_bodies.py` | one-token body mutation; a deleted import in the new module | baseline-diff RED; undefined-global RED |
| `tests/test_mod_parity.py` | painted-string mutant in a subprocess | parity capture RED |
| `tests/test_mod_dispatch.py` | tmp-copy mutants (duplicated `on_*`, mixin `BINDINGS`, dropped mixin) | respective assertions RED |
| `tests/test_mod_deps.py` | synthetic sibling-concern import | §3-rules assertion RED |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/screens/map/undo.py` on disk | `tests/test_mod_bodies.py` compares each moved method's `ast.dump` against the Inc-0 baseline JSON | GREEN — bodies byte-identical, every census method exactly once |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact (the moved module's AST), asserted against the emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| b3b9-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/b3b9-gate-full-suite.transcript | 027b617017a980f3dab46ff218e837f1e497e9b97c03c4b73cae2a0153e7e6d3 |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact, at the declared home and cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — the same batch-wide absences every B-increment rests on: no duplicated method name across the 12 map modules; no `screens/**` import of the 8 patch names from `mapper.app`; no mixin declaring `BINDINGS`/`DEFAULT_CSS`/`@on` |
| If the result is an ABSENCE, what made the search wide enough | the AST scans cover all 12 `screens/map` modules and every `mapper/screens/**` file |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_mod_dispatch.py -k disjoint`; `test_mod_deps.py -k arch` |
| Conjunctive criteria: one mutation per conjunct | the checkers' tmp-copy arms mutate one conjunct each |
| Synthetic instance of the absent case | the checkers' tmp-copy mutants |
| **Positive control for every probe that returned an ABSENCE** | the same unmodified suite reports the present methods/bindings GREEN at the gate |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "UndoOps" mapper tests` | 2 files: `undo.py`, `screen.py` — only the composition consumes the mixin |
| B2 file moved on disk | none moved (new module) | not fired |
| B3 byte-identical golden captures this source | none for this concern | not fired |
| B4 artifact produced here is consumed elsewhere | `undo.py` is imported only by `screen.py` | 1 consumer |

| A3 | interface consumed by another module changed | `grep -rl "UndoOps" mapper` | the mixin base list is the interface; only `screen.py` consumes it |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run. B1: 2 hits, both this increment's own files. B4: 1 consumer (the composition). B2, B3 and A3 did not fire. |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| none | — | — | — | — | — |

| Field | Value |
|---|---|
| **Correction population** | none — pure move; nothing was corrected, only relocated |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| undo method defs in `screen.py` | 0 hits for the moved defs (bodies now in `undo.py`) | yes | `test_mod_bodies.py` baseline diff GREEN at gate |

### Signed-balance test ledger

The b3b9 gate transcript reports `3060 passed, 24 deselected, 3 xfailed` for the whole B3–B9 window; a per-increment node reconciliation is **not recorded** in the facts sheet.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, independent of the orchestrator) · group review **B1–B12** · **APPROVE-WITH-NITS, 0 HIGH / 0 MED / 4 LOW** — moved bodies byte-identical (AST); no MRO shadowing; `BINDINGS`/CSS/`@on` only on the core; imports exact; B8's deviation sound; patch repoints correct; census generalisations not weakenings. None of the 4 LOWs names B4's files. |

---

## 5 · Risks

- Undo has callers in drafts/edits/focus (per the batch plan), which move later (B6, B7). A caller-side regression would only surface when those concerns move — but the byte-identical body oracle already pins every moved body at each step, so cross-concern drift would redden at the gate that introduces it.

## 6 · Pending items / spec deviations

- None open.

## 7 · Suggested next task

B5 — focus concern to `screens/map/focus_mode.py` (LLR-MOD.1.3); it rewrites `graph`/`nav` wholesale, so it moves early and freezes the multi-writer set under F1.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ✓ | none needed — permanent controls carry the move (declared in §1) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_bodies.py` body oracle |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | none — pure move; permanent controls in force (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b group review B1–B12, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | no patch surface on this concern |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate transcript 3060 passed, 0 failed |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | mod_bodies / mod_parity / mod_dispatch / mod_deps RED arms |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | none — pure move |
| 14 | **Emitted-form assertion** declared | all | ✓ | moved AST on disk |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` (§4b) |
| 16 | **Evidence files** declared | all | ✓ | 1 file with sha256 (§4) |
