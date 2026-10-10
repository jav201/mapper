# Increment 013 — LLR-MOD.1.3 / 5.2 / 7.1 · `B3 — open concern to the OpeningOps mixin`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-013.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `013` (Inc-B3) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `HLR-MOD.1 v1 / LLR-MOD.1.3` · `HLR-MOD.5 v1 / LLR-MOD.5.2` · `HLR-MOD.7 v1 / LLR-MOD.7.1` |
| Acceptance | LLR-MOD.5.2 — `test_arch_osopen_callers.py` allow-list gains `screens/map/opening.py` in this increment · LLR-MOD.7.1 — §3 dependency rules hold with `opening.py` as the sole map launcher · white-box `tests/test_mod_bodies.py`, `test_mod_dispatch.py`, `test_mod_deps.py -k arch` · full-suite gate |
| Agent | Each worker ran in its own worktree.<br>• **the move** (2 methods, byte-identical, `mixin_move.py` + `screen_prune.py`): the orchestrator (Claude Opus 5.5);<br>• **the census follow-up + ARCHITECTURE §3 osopen row:** Kimi (`kimi-for-coding`) — per the commit message "Census and ARCHITECTURE §3 osopen row by Kimi";<br>• **the gate run:** the orchestrator. |
| Date | `2026-10-09/10` |

---

## 1 · What changed

**The open concern moved out of `MapScreen` into the new `mapper/screens/map/opening.py`, carrying the only `osopen` launch site with it — the §3 amendment the contract schedules for exactly this increment.**

- 2 methods moved **byte-identically** into `mapper/screens/map/opening.py` (78 new lines); `screen.py` shrank by ~62 lines and composes `OpeningOps`.
- The attachment-activated handler — the one `open_external` launch site — moved with the concern; `screen.py` now imports **nothing** from `osopen`, asserted by the new `test_map_screen_core_does_not_import_osopen_at_all`.
- LLR-MOD.5.2 / LLR-MOD.7.1: `tests/test_arch_osopen_callers.py` was updated in the same increment — `ALLOWED_FILES` went from `{"osopen.py", "screens/map/screen.py"}` to `{"osopen.py", "screens/map/opening.py"}`; the `ALLOWED_OUTSIDE_APP` row for `screens/map/screen.py` moved to `screens/map/opening.py` (`ATTACHMENT_HARD_LINKED`, `OK`, `open_external`).
- `docs/ARCHITECTURE.md` §3 `osopen` row and the Spine-B table were amended in the same commit (B0→B3 history collapsed to the final state; the B3 row marked DONE).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/opening.py` | source | LLR-MOD.1.3, LLR-MOD.7.1 | new — 2 methods moved byte-identically (78 lines); the one osopen launch site |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.3 | open methods pruned; composes `OpeningOps`; imports nothing from osopen |
| `tests/test_arch_osopen_callers.py` | test | LLR-MOD.5.2, LLR-MOD.7.1 | allow-list repointed to `opening.py`; new `test_map_screen_core_does_not_import_osopen_at_all` (+21/−…) |
| `docs/ARCHITECTURE.md` | doc | | §3 `osopen` row amended; B3 row DONE (4 lines) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 1 (`docs/ARCHITECTURE.md`, outside the count) |

- ✓ Spine B shape — one new concern module plus its composing `screen.py`.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_arch_osopen_callers.py
python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py -k arch
python -B -m pytest -q -p no:cacheprovider tests/test_mod_bodies.py tests/test_mod_dispatch.py
python -B -m pytest -q -p no:cacheprovider   # the increment gate — full suite, orchestrator-run
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_bodies.py` body oracle; `test_mod_deps.py -k arch` | GREEN at gate |
| **A · white-box** ↔ LLR | `core` · `full` | `test_arch_osopen_callers.py` (allow-list + no-osopen-import arm); `test_mod_dispatch.py` | GREEN at gate |
| **B · black-box** | `core` · `full` | attachment-activated open flow through `MapperApp` (existing suite) | GREEN at gate |
| **Increment gate — full suite** | — | whole suite | **3060 passed, 0 failed** (`b3b9-gate-full-suite.transcript`: `3060 passed, 24 deselected, 3 xfailed in 1583s`, exit=0) |

The pre-existing `test_at_n03f` keymap failure from B1/B2 is fixed by this point (B7 landed inside the B1–B9 window; the b3b9 gate transcript is clean: 0 failed).

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none new of its own beyond the gate controls — the increment's new assertion (`screen.py` imports nothing from osopen) has its RED side in the checker's tmp-copy mutant per the contract's Phase-3 arms for `test_mod_deps.py -k arch` |
| Instrument | permanent gate controls (see below) |
| Where it ran | the orchestrator's checkout / the gate |
| Transcript | `b3b9-gate-full-suite.transcript` |
| Restore proven by | n/a — no in-place mutation in this increment |
| Bytecode cache | gate runs with `python -B` |
| Arms resolved at baseline | the new no-osopen-import arm resolves 1 node |
| Verdict granularity | per node id |
| Arms that stayed GREEN | none named |

| Field | Value |
|---|---|
| **RED counterfactual** | none of its own beyond the permanent controls — this increment's new assertion is a pure-move absence claim ("`screen.py` imports nothing from osopen"), whose RED arm runs as the `test_mod_deps.py` tmp-copy mutant per the contract. Transcript: `.dev-flow/2026-10-09-modular-batch/evidence/b3b9-gate-full-suite.transcript`. |

| Field | Value |
|---|---|
| **Mutation verdicts** | In force at this gate, per the facts sheet: `tests/test_mod_bodies.py` — one-token body mutation on a tmp copy → RED; deleted import in a new module → RED. `tests/test_mod_parity.py` — painted-string mutant in a subprocess → RED. `tests/test_mod_dispatch.py` — duplicate names / `BINDINGS` in a mixin / `HintsOps` dropped → RED. `tests/test_mod_deps.py` — synthetic sibling-concern import / `MapScreen`-from-app import mutants → RED. Per-arm granularity; no arm reported inert. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_bodies.py` | one-token body mutation; a deleted import in the new module | baseline-diff RED; undefined-global RED |
| `tests/test_mod_parity.py` | painted-string mutant in a subprocess | parity capture RED |
| `tests/test_mod_dispatch.py` | tmp copy with `HintsOps` dropped / duplicated `on_*` / `BINDINGS` in a mixin | respective assertions RED |
| `tests/test_mod_deps.py` | synthetic sibling-concern import into the map package | §3-rules assertion RED |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/screens/map/opening.py` on disk | `tests/test_mod_bodies.py` compares each moved method's `ast.dump` against the Inc-0 baseline JSON | GREEN — bodies byte-identical, every census method exactly once |
| the osopen launch surface | `test_arch_osopen_callers.py` derives the launcher census from the ASTs of the shipped files | GREEN at gate |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts (the moved module's AST and the osopen census), each asserted against the emitted form |

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
| Does any claim here rest on the tree holding NO instance of some case? | yes — the new arm is precisely an absence: "`screen.py` imports nothing from osopen at any scope" |
| If the result is an ABSENCE, what made the search wide enough | the AST walk of `screen.py` catches every import form (plain, aliased, function-local), not only top-level ones |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_map_screen_core_does_not_import_osopen_at_all` (docstring: "must not import osopen only via opening.py") |
| Conjunctive criteria: one mutation per conjunct | the osopen boundary is conjunctive (launchers vs. non-launcher names); each conjunct has its own arm in `test_arch_osopen_callers.py` |
| Synthetic instance of the absent case | the contract's tmp-copy mutants for `test_mod_deps.py -k arch` |
| **Positive control for every probe that returned an ABSENCE** | the same AST probe returns the present osopen imports in `opening.py` (the launcher row is asserted, not just the absence) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "OpeningOps" mapper tests` | 2 files: `opening.py`, `screen.py` — only the composition consumes the mixin |
| B2 file moved on disk | the osopen launch site moved `screen.py` → `opening.py` | `grep -rln "open_external" mapper` → `app`-side callers plus `opening.py`; the census test follows it (allow-list updated in the same commit) |
| B3 byte-identical golden captures this source | none for this concern | not fired |
| B4 artifact produced here is consumed elsewhere | `opening.py` is imported only by `screen.py` | 1 consumer |

| A3 | interface consumed by another module changed | the osopen launcher census (`LAUNCH_NAMES` readers) | `test_arch_osopen_callers.py` is the consumer; updated in the same commit (LLR-MOD.5.2) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run. B1: 2 hits, both this increment's own files. B2 fired — the launch site moved and its census consumer followed in-commit. A3 fired — `test_arch_osopen_callers.py` re-validated green. B3 and B4 did not fire. |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the osopen launcher allow-list names the launcher file | every file referencing a `LAUNCH_NAMES` name | the AST-derived census inside `test_arch_osopen_callers.py` (derives both facts from the ASTs) | 1 launcher file moved | `ALLOWED_FILES` row + `ALLOWED_OUTSIDE_APP` row + new no-import arm | none — the launcher moved, so every row naming it moved with it |

| Field | Value |
|---|---|
| **Correction population** | 1 correction, enumerated by the test's own AST census before the first site was edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `screens/map/screen.py` in the osopen launcher allow-list | 0 surviving refs in `ALLOWED_FILES` / `ALLOWED_OUTSIDE_APP` | yes | `test_arch_osopen_callers.py` GREEN at gate; ARCHITECTURE §3 row amended in-commit |

### Signed-balance test ledger

The gate count stepped from the b1b2 transcript (`3034 passed + 1 failed`) to the b3b9 transcript (`3060 passed, 0 failed`). The exact added/deselected node arithmetic is in the orchestrator's gate logs — **not recorded** in the facts sheet.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, independent of Kimi and the orchestrator) · group review **B1–B12** · **APPROVE-WITH-NITS, 0 HIGH / 0 MED / 4 LOW** — moved bodies byte-identical (AST); imports exact; the osopen boundary stayed countable through the move (census follows the launcher, not a hand list); §3 amendment landed with B3 as scheduled. LOWs recorded at the group level (CR-1…CR-4, see increment-011 §4b); none names this increment's files beyond the group-level CR list. |

---

## 5 · Risks

- The osopen boundary is an absence claim twice over (no launchers outside the allow-list; `screen.py` imports nothing). Both arms are AST-wide and have tmp-copy RED mutants per the contract, but a future function-local import of an osopen name into `screen.py` would be the exact failure shape — the new `test_map_screen_core_does_not_import_osopen_at_all` exists to catch it.

## 6 · Pending items / spec deviations

- None open. The B1-carried keymap failure is resolved by the b3b9 gate window (fixed at B7 `5229b12`).

## 7 · Suggested next task

B4 — undo concern to `screens/map/undo.py` (LLR-MOD.1.3).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ✓ | `test_arch_osopen_callers.py` new arm + repoint |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_deps.py -k arch`; `test_mod_bodies.py` |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | permanent controls + no-osopen-import absence arm (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b group review B1–B12, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | osopen census follows the move in-commit |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate transcript 3060 passed, 0 failed |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | mod_bodies / mod_parity / mod_dispatch / mod_deps RED arms |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | 1 correction — the osopen allow-list rows |
| 14 | **Emitted-form assertion** declared | all | ✓ | moved AST + osopen census |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` (§4b) |
| 16 | **Evidence files** declared | all | ✓ | 1 file with sha256 (§4) |
