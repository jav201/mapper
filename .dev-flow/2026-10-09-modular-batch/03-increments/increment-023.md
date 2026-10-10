# Increment 023 — LLR-MOD.7.1, LLR-MOD.6.2 · DDR conditions D-C1/D-C2/D-C3 (+ LOW-5, QA-3) · `DDR review conditions closed — docs + guard tests only, 0 product files`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-023.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `023` (MODDDRFIX) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `LLR-MOD.7.1` · `LLR-MOD.6.2` — DDR conditions **D-C1** (HIGH), **D-C2** (MED), **D-C3** (MED), **LOW-5**, **QA-3**, from the independent DDR reviews (architect Claude Opus, qa Claude Sonnet) |
| Acceptance | the increment verification run: `tests/test_mod_deps.py` + `tests/test_arch_osopen_callers.py` + `tests/test_mod_compat.py` + `tests/test_repair_map_truth.py` (§3) |
| Agent | Kimi (`kimi-code/kimi-for-coding`) via the kimi CLI — worker unit MODDDRFIX |
| Date | `2026-10-10` |

---

## 1 · What changed

- **D-C1 — §4 F4 patch surface row corrected against the shipped guard map.** The row named three of the seven repoint targets at their pre-move homes: `save_svg` → `export.py` now → `screens/map/exporting.py` (`test_app.py`; `test_inc9c.py:134`); `refusal_sentence` → `osopen.py` now → `screens/common.py` (`test_inc9q.py`; `test_inc9q.py:33`); `SearchIndex` → `search.py` now → `screens/map/searching.py` (`test_search.py`; `test_search.py:1434`); `LayeredRenderer` → `views/layered.py` (the definition site) now → `screens/import_preview.py` (`test_en8.py:335`). The other three targets were checked against the guard map and were already right (`pan_extent` → `screens/map/panning.py`, `preview_csv` → `screens/home.py`, `MAX_RENDER_NODES` → `screens/map/searching.py`). Row structure and its other claims (eight names, `GitHubConnector.fetch` not repointed) untouched.
- **D-C2 — §3 `screens/map` row amended; `concern_cross_imports` narrowed.** (a) The row now names the one sanctioned edge — a concern module MAY import the non-mixin value class `NavigationModel` from `navigation.py` (the shared model, not a concern's behaviour; `focus_mode.py:9`); nothing else crosses between concern modules *(amended DDR `2026-10-09-modular-batch`)*. (b) The checker flagged only mixin-class names or module-object imports; it now flags ANY name imported from a sibling concern module except exactly `NavigationModel` from `navigation`. New RED arm plants `from mapper.screens.map.painting import RAIL_WIDTH` — a real module-level name in `painting.py`, not a mixin — into `hints.py`.
- **D-C3 — `screens` dependency declared; package `__init__` guard added.** (a) The `screens/map` row "Depends on" gains `screens` (the package `__init__` re-exports only — the modal screens `DraftGuardScreen` / `FactoryScreen` / `CoverageScreen`; NOT the sibling screen modules `home`, `repo`, `plug_repo`, `import_preview`, `construct`). (b) New checker `screens_init_sibling_imports`: the banned set is derived from disk — (1) top-level `screens/*.py` whose AST imports `mapper.screens.map` (the cycle-closers), (2) top-level `screens/*.py` the `__init__` does not itself import, (3) the `map` package — because any of them closes the cycle `screens/map → screens → <sibling> → screens/map`. RED arm plants `from mapper.screens.home import HomeScreen` into `__init__.py`.
- **LOW-5 — launcher census renamed; §3 `osopen` row reworded.** `test_arch_osopen_callers.py`'s launcher test is renamed `test_the_launcher_names_appear_only_in_osopen_and_opening` (the old name claimed `app`, which the asserted set does not contain); the §3 `osopen` row's ban now names `osopen.py` (its own definition site) and `screens/map/opening.py` only — `app.py` no longer references any launcher name.
- **QA-3 — design proposal AT-069 re-pointed.** `design-proposal.md`'s AT-069 line now reads `tests/test_mod_compat.py -k at069` (citing ledger LED .11, the same fix LED .11 made in `01-requirements.md`).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `docs/ARCHITECTURE.md` | doc | D-C1, D-C2, D-C3, LOW-5 | §4 F4 row: 4 repoint targets corrected; §3 `screens/map` row: `NavigationModel` edge + `screens` dep; §3 `osopen` row: launcher census reworded (±4 lines) |
| `tests/test_mod_deps.py` | test | LLR-MOD.7.1, D-C2, D-C3 | `concern_cross_imports` narrowed to any-name (±10); new `screens_init_sibling_imports` checker (+44); 2 new nodes with tmp-copy RED arms (+40) |
| `tests/test_arch_osopen_callers.py` | test | LLR-MOD.6.2, LOW-5 | launcher test renamed + docstring; module docstring and §3-row assertion reworded (±6 lines) |
| `.dev-flow/2026-10-09-modular-batch/design/design-proposal.md` | doc | QA-3 | one line — AT-069 re-pointed to `tests/test_mod_compat.py -k at069` (LED .11) |
| `.dev-flow/2026-10-09-modular-batch/03-increments/increment-023.md` | doc | — | this packet (new) |

| Count | Value |
|---|---|
| **SOURCE (product) files** | **0 — NO product file under `mapper/` changed; this increment is docs + guard tests only** |
| Test files | 2 (`tests/test_mod_deps.py`, `tests/test_arch_osopen_callers.py`) |
| Doc files | 3 (`docs/ARCHITECTURE.md`, `design-proposal.md`, this packet — outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_mod_deps.py tests/test_arch_osopen_callers.py tests/test_mod_compat.py tests/test_repair_map_truth.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_deps.py` (13), `tests/test_arch_osopen_callers.py` (6) | within the 91 |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_compat.py` (-k at069/at067 guards), `tests/test_repair_map_truth.py` (AT-P04/P05) | within the 91 |
| **This increment's files** | — | 91 nodes | **91 passed in 15.43s** (run in this worktree, §3 command) |

New / renamed nodes:

- `tests/test_mod_deps.py::test_llr_mod_7_1_arch_concern_helper_name_import_is_flagged` (D-C2 RED arm)
- `tests/test_mod_deps.py::test_llr_mod_7_1_arch_screens_init_does_not_import_sibling_screens` (D-C3 RED arm)
- `tests/test_arch_osopen_callers.py::test_the_launcher_names_appear_only_in_osopen_and_opening` (renamed, LOW-5)

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (1) tmp-copy plant `from mapper.screens.map.painting import RAIL_WIDTH` into `hints.py` (D-C2 arm, in-tree); (2) tmp-copy plant `from mapper.screens.home import HomeScreen` into `screens/__init__.py` (D-C3 arm, in-tree); (3) hand revert of the narrowed `concern_cross_imports` to its pre-DDR body; (4) hand revert of `screens_init_sibling_imports`'s return to `set()` |
| Instrument | each guard runs its checker on the real tree (GREEN) and on a tmp-copy mutant (RED); the hand reverts exercise the RED-proof rule |
| Where it ran | this worktree |
| Transcript | §4 run output in this unit's log; gate transcript added by the orchestrator |
| Restore proven by | sha256 of `tests/test_mod_deps.py` before revert = after restore = `9921d2f0ecbbc8c63c5e539bb0dd26794a7c7881c144a9519346445c34d0e3e4`; `cmp` byte-identical |
| Bytecode cache | run under `python -B` |
| Arms resolved at baseline | the two new tmp-copy RED arms + the two hand-revert RED proofs |
| Verdict granularity | per node id |
| Arms that stayed GREEN | none recorded |

RED outputs (verbatim tails):

- revert (3) + node `..._concern_helper_name_import_is_flagged` → `E Failed: DID NOT RAISE <class 'AssertionError'> — tests\test_mod_deps.py:465: Failed` — which is simultaneously the proof that the OLD checker passed the planted helper import (`RAIL_WIDTH` is not in `mixins`, so the old `form == "module" or any(n in mixins for n in names)` condition at the reverted lines was False and the plant produced an empty violation set).
- revert (4) + node `..._screens_init_does_not_import_sibling_screens` → `E Failed: DID NOT RAISE <class 'AssertionError'> — tests\test_mod_deps.py:486: Failed`.

| Field | Value |
|---|---|
| **RED counterfactual** | Both new guards ship in-tree tmp-copy RED arms, each executed at this run: the D-C2 arm plants a real non-mixin module-level name of `painting.py` (`RAIL_WIDTH`) into a sibling concern; the D-C3 arm plants a sibling-screen import into the package `__init__.py`. Additionally the narrowed checker was reverted to its pre-DDR body and the new node FAILED (`DID NOT RAISE` — the old body returned an empty violation set for the planted helper import), then restored byte-identically (sha256 match). |

| Field | Value |
|---|---|
| **Mutation verdicts** | 2 planted-defect mutants → RED each (in-tree arms); 2 hand reverts → RED each; restored file byte-identical (sha256) and the full §3 run re-run GREEN (91 passed in 15.43s). Arms that stayed GREEN: none recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `concern_cross_imports` (narrowed, D-C2) | tmp copy planting `from mapper.screens.map.painting import RAIL_WIDTH` into `hints.py` | `DID NOT RAISE AssertionError` under the OLD body (revert proof); reported as a violation `painting -> RAIL_WIDTH` under the new body |
| `screens_init_sibling_imports` (new, D-C3) | tmp copy planting `from mapper.screens.home import HomeScreen` into `screens/__init__.py` | `DID NOT RAISE AssertionError` under a vacuous body (revert proof); reports `{'home'}` under the real body |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 2 instruments, each shown RED on its planted mutant and on its hand-reverted body before the GREEN is believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `docs/ARCHITECTURE.md` §3 `osopen` row | `test_the_architecture_map_says_what_the_modules_import` asserts the new wording "`open_external` is referenced only from `osopen.py`" | passed |
| `docs/ARCHITECTURE.md` F4/§3 rows as shipped | read back by `tests/test_repair_map_truth.py` (AT-P04 owned paths, AT-P05 corrected-falsehood pins — incl. the `SearchIndex(store)` pin, which the D-C1 edit does not reintroduce) | passed |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against its emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| gate transcript added by the orchestrator | .dev-flow/2026-10-09-modular-batch/evidence/ | — |

| Field | Value |
|---|---|
| **Evidence files** | gate transcript added by the orchestrator |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — both new guards are empty-set claims: no concern module imports any name from a sibling concern (except `NavigationModel` from `navigation`), and `screens/__init__.py` imports no banned sibling/`map` tail |
| If the result is an ABSENCE, what made the search wide enough | whole-package AST scans (`_py_files` rglob in `concern_cross_imports`; every top-level `screens/*.py` parsed in `screens_init_sibling_imports`); the banned set is derived from disk, not hand-listed |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_mod_deps.py -k at070/at071` family — the empty-set boundary of HLR-MOD.6/7 |
| Conjunctive criteria: one mutation per conjunct | per the contract, each arm plants one import |
| Synthetic instance of the absent case | each tmp-copy mutant IS the synthetic instance |
| **Positive control for every probe that returned an ABSENCE** | the same unmodified checkers return GREEN on the real tree; the mutants return the absent case (RED) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rn "concern_cross_imports\|screens_init_sibling_imports" tests` | consumed only inside `tests/test_mod_deps.py` (incl. the AT-071 roll-up node) — consumer in-tree, green at this run |
| B2 file moved on disk | n/a — no file moved in this increment | not fired |
| B3 byte-identical golden captures this source | n/a — no golden reads these files | not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "test_the_launcher_names_appear_only_in" tests` | the renamed node has no external referrer (single hit, its own definition) |

| Field | Value |
|---|---|
| **Reverse census** | 4 probes run (B1 and B4 fired with the hits above, re-validated green; B2, B3 did not fire) |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | D-C1: exactly the seven module-global F4 targets, enumerated from the AT-069 guard map (`tests/test_mod_compat.py` PATCH_SURFACE) before editing — 4 wrong (`save_svg`, `LayeredRenderer`, `refusal_sentence`, `SearchIndex`), 3 already right; plus the 3 doc-wording corrections (D-C2 row, D-C3 row, LOW-5 row) and the 1 design-proposal line (QA-3). No behavioural correction — 0 product files. |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| F4 row's stale pre-move targets (`export.py` / `osopen.py` / `search.py` / `views/layered.py` as patch homes) | the row now names `screens/map/exporting.py`, `screens/common.py`, `screens/map/searching.py`, `screens/import_preview.py` | yes — targets match the guard map | `docs/ARCHITECTURE.md` §4 F4 row |
| §3 `osopen` row "any module but `app`" wording | row now names `osopen.py` (definition site) + `screens/map/opening.py`; the test assertion pin updated in the same commit | yes | `docs/ARCHITECTURE.md` §3 `osopen` row; `tests/test_arch_osopen_callers.py` |

### Signed-balance test ledger

`post = base − deleted + added`: the first §3 run in this worktree (before the D-C3 checker fix) collected 91 nodes — 90 passed + 1 failed; the fixed, final run reports **91 passed**. Node-level ledger for these four files: `91 = 89 + 2 − 0` (2 nodes added in `tests/test_mod_deps.py`, 1 node renamed in `tests/test_arch_osopen_callers.py` with no net count change); the suite-wide delta is reconciled by the orchestrator at the gate.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | DDR reviews (architect Claude Opus, qa Claude Sonnet) raised these; re-review at DDR seal |

---

## 5 · Risks

- D-C2's arm plants `RAIL_WIDTH` — a name `painting.py` holds via its own import from `mapper.widgets.rail` — because `painting.py` defines no non-mixin top-level name of its own; the plant is still the exact shape the pre-DDR checker missed (a non-mixin name taken from a sibling concern module).
- The `screens` package `__init__` dependency (D-C3) is new in §3: if a future modal screen legitimately needs a home in the package `__init__`, the row and the guard's derived modal set move together.

## 6 · Pending items / spec deviations

- None beyond the DDR re-review at seal (§4b).

## 7 · Suggested next task

The DDR seal — architect + qa re-review of D-C1..D-C3 / LOW-5 / QA-3 against this increment, then the batch close.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | **0 product files** — declared in §2 |
| 2 | Tests written in this same increment | all | ✓ | 2 new nodes in `tests/test_mod_deps.py` (D-C2/D-C3 RED arms), 1 renamed node in `tests/test_arch_osopen_callers.py` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_deps.py` (13 nodes) + `test_arch_osopen_callers.py` (6 nodes) in the 91 |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | 2 in-tree tmp-copy arms + 2 hand-revert RED proofs (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 4 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | DDR reviews raised these; re-review at DDR seal (§4b) |
| 7 | No file from another lane touched | all | ✓ | one lane; only the 5 files named in the unit |
| 8 | Frozen interfaces untouched | all | ✓ | 0 product files; F1–F5 rows edited only where the DDR conditions name them (F4 targets are doc claims, not frozen code) |
| 9 | Coverage claims verified **on disk** | all | ✓ | 91 passed here (§3 command) |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 (2 planted + 2 reverts → RED each) |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 |
| 13 | **Correction population** declared | all | ✓ | §4 (7 F4 targets enumerated from the guard map before editing) |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 (ARCHITECTURE rows read back by tests) |
| 15 | **Independent review** names somebody | all | ✓ | §4b — DDR reviews (architect Claude Opus, qa Claude Sonnet) |
| 16 | **Evidence files** declared | all | ✓ | §4 — gate transcript added by the orchestrator |
