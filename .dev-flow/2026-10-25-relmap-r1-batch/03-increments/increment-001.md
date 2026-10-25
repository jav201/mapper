# Increment 001 — US-RM-001 · `Relation-map profile table and typed multi-parent read model`

> **Artifact language.** English (the batch language). **Owed in.** `core` ✓ · `full` ✓
> Where this lives: the repo, `.dev-flow/2026-10-25-relmap-r1-batch/03-increments/increment-001.md`. Written by the
> `software-dev` author in the batch worktree on branch `feat/relmap-r1` (base `358ab41`); the transcripts it cites
> are under `.dev-flow/2026-10-25-relmap-r1-batch/evidence/`, redacted of the account name before hashing.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r1-batch` |
| Increment | `001` |
| Lane (if the batch forked) | none — one chain, trigger A4 not fired · module `relmap` |
| Requirement(s) | US-RM-001 · HLR-RMP.1, HLR-RMP.2, HLR-RMM.1, HLR-RMM.2, HLR-RMM.3 · LLR-RMP.1.1, LLR-RMP.1.2, LLR-RMP.2.1, LLR-RMM.1.1, LLR-RMM.1.2, LLR-RMM.1.3, LLR-RMM.2.1, LLR-RMM.2.2, LLR-RMM.3.1 |
| Acceptance | Layer B: none in this increment — the twelve ATs run `mapper --audit` through the hook that lands in Inc-5 (proposal §2.1 *Layer phasing*); white-box `TC-RM-01` (tree kind still refuses a cycle) · unit: the model, profile and census nodes in §4 |
| Agent | `software-dev` |
| Date | 2026-10-25 |

---

## 1 · What changed

The headless core of the relation-map kind now exists as an importable package that nothing outside it imports yet:
`mapper/relmap/profile.py` declares the `reqharness` profile as frozen data (5 node kinds, 4 edge types with 6 allowed pairs, direction of
change and evidence rule, and the 8-row gap catalogue with its closed four-pattern set and sentence templates), and
`mapper/relmap/model.py` builds the typed multi-parent read model from it. `build_map(profile, nodes, edges, *, sourced)` holds every valid node and
edge in input order, reports each invalid element as one of the six typed `Problem` kinds instead of raising, refuses only over the node or edge cap
(`RelMapLimitError`, naming the limit), reports cycles with an iterative Tarjan (never raising, flagging `Edge.in_cycle`), and answers `up`, `down`,
`reach` and `neighbourhood` iteratively. `reach` draws on ONE per-map visit budget (`VISIT_BUDGET = 2,000,000`, readable as `RelMap.visits`) read through
the single counted `down` seam and returns `None` ("not computed") once it is spent, with an int memo only (security C1, QA D-1). `mapper/relmap/__init__.py`
is empty and re-exports nothing.

Enforcement that lands with the code: `tests/test_relmap_isolation.py` is an AST census of the whole tree (the package imports only the stdlib, PyYAML and the
named `mapper` names, in both import forms and at any scope; only `app.py` and the package may import it; the engine names no profile literal; the Python-3.10 floor is
a feature-version parse plus a qualified-name census), and the two osopen-boundary artefacts were amended in this same landing as the first
import (R16): the allow-list entry `relmap/model.py: {MAX_NODES, MAX_EDGES}` in `tests/test_arch_osopen_callers.py`, the `relmap` row's owned-paths cell and both
`osopen` cells (§2 exposes, §3) in `docs/ARCHITECTURE.md` (as built for Inc-1, still commitment for Inc-3). No shipped surface changes: the user-visible
output of `mapper --audit` is Inc-5.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/relmap/__init__.py` | source | HLR-RMP.2, LLR-RMP.2.1 | NEW, zero bytes: re-exports nothing |
| `mapper/relmap/profile.py` | source | HLR-RMP.1, LLR-RMP.1.1, LLR-RMP.1.2 | NEW: `EdgeType`, `GapRow`, `Profile` (frozen, validated at construction), `REQHARNESS`, `PATTERNS`, `SEVERITIES` |
| `mapper/relmap/model.py` | source | HLR-RMM.1, HLR-RMM.2, HLR-RMM.3, LLR-RMM.1.1, LLR-RMM.1.2, LLR-RMM.1.3, LLR-RMM.2.1, LLR-RMM.2.2, LLR-RMM.3.1, LLR-RMP.2.1 | NEW: `Node`, `Edge`, `Problem`, `RelMap`, `build_map`, `RelMapLimitError`, `VISIT_BUDGET`, `DISPLAY_MAX`, `cut` |
| `tests/test_relmap_profile.py` | test | HLR-RMP.1, LLR-RMP.1.1 | NEW: cell-by-cell tables, closed sets, frozen values, construction refusals (16 nodes) |
| `tests/test_relmap_model.py` | test | HLR-RMM.1, HLR-RMM.2, HLR-RMM.3, LLR-RMM.1.1, LLR-RMM.1.2, LLR-RMM.1.3, LLR-RMM.2.1, LLR-RMM.2.2, LLR-RMM.3.1 | NEW: builder, six problem kinds, caps ±1, direction table, premise-6 figures, reach/neighbourhood, budget and memo arms, cycles |
| `tests/test_relmap_isolation.py` | test | HLR-RMP.2, LLR-RMP.2.1, LLR-RMP.1.2, LLR-RMM.1.1 | NEW: import/importer census, engine-literal census, `test_py310_floor`, `TC-RM-01`, each with a planted-violation arm |
| `tests/test_arch_osopen_callers.py` | test | LLR-RMP.2.1 | allow-list entry `relmap/model.py: {MAX_NODES, MAX_EDGES}` (R16, same landing as the import) |
| `docs/ARCHITECTURE.md` | doc | | §2 `relmap` row owned paths (3 files, as built); §2 and §3 `osopen` cells: `relmap/model.py` as built, Inc-3 entries still commitment |
| `.dev-flow/2026-10-25-relmap-r1-batch/03-increments/increment-001.md` and `evidence/inc1-*.txt` | doc | | this packet and four redacted transcripts |

| Count | Value |
|---|---|
| **SOURCE files** | **3 / 4** |
| Test files | 4 (3 new, 1 edited; uncapped) |
| Doc files | 1 product doc + packet and evidence (outside the count) |

---

## 3 · How to test

```bash
cd <worktree>   # C:/Users/<user>/AppData/Local/Temp/ds-units/wt-r1
export PYTHONPATH=<worktree>
env -u NO_COLOR -u TERM python -c "import mapper; print(mapper.__file__)"      # must resolve inside the worktree
git add mapper/relmap tests/test_relmap_*.py                                 # the A3 census needs new files staged
env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider tests/test_relmap_profile.py tests/test_relmap_model.py tests/test_relmap_isolation.py tests/test_arch_osopen_callers.py
env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider tests/test_mod_*.py tests/test_repair_map_truth.py tests/test_arch_osopen_callers.py tests/test_a3_census.py tests/test_no_operator_paths.py
```

Targeted files only; never the full suite (the orchestrator schedules the one full run).

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** (`build_map` validation, the Tarjan, reach, neighbourhood, `cut`, profile construction) | `core` · `full` | `test_relmap_model.py` (53 nodes), `test_relmap_profile.py` (16) | executed: GREEN |
| **A · white-box** `TC-NNN` ↔ LLR | `core` · `full` | `test_relmap_isolation.py` (58 nodes incl. `TC-RM-01`), `test_arch_osopen_callers.py::test_outside_app_only_the_allowed_names_are_imported_from_osopen` | executed: GREEN |
| **B · black-box** `AT-NNN` through the shipped surface | `core` · `full` | n/a — no shipped surface in Inc-1; AT-117/AT-124 first realise at Inc-5 (proposal §2.1) | n/a — Layer B starts at Inc-5 |

Targeted run (4 files): **132 passed**, exit 0, 7.4 s wall (`evidence/inc1-green-first.txt`). Heaviest arms (separate functions, no clock assertion): `test_reach_budget_per_row` 1.6 s, the 100,000-node chain and ring arms 0.9 s each.
Guard run (`test_mod_*` ×7, `test_repair_map_truth`, `test_arch_osopen_callers`, `test_a3_census`, `test_no_operator_paths`): **142 passed**, exit 0, 36.9 s wall (`evidence/inc1-guards.txt`); the A3 pin `test_a3_census.py:329` (86) did not move. Battery driver: 34.0 s wall.
`tests/test_no_operator_paths.py` was also re-run on the final tree before the commit (see §6 and the commit record).

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | per new source file, the file moved out of the tree (C-20 move-aside); then the 19 named mutants of the next table |
| Instrument | project code: a short Python driver (`battery.py`, scratch outside the repo) — hash before, one edit or one move, the targeted pytest run, restore, hash after, one verdict per mutant |
| Where it ran | the batch worktree, by the `software-dev` author (one worktree, nothing else reading it); the orchestrator may re-run, the driver is deterministic |
| Transcript | `evidence/inc1-red-code-absent.txt` (tests on the code-absent tree) and `evidence/inc1-red-mutants-battery.txt` (move-aside + mutants) |
| Restore proven by | file sha256 returned to its pre-mutation value, printed per arm; `git status` showed no unstaged change afterwards |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` and the `__pycache__` of `mapper/`, `mapper/relmap/`, `tests/` purged before every run |
| Arms resolved at baseline | 132 (battery baseline `132 passed`, the same four files as the green run) |
| Verdict granularity | per mutant, by the named assigned test nodes that failed (the driver reports failing node ids, not only the exit code) |
| Arms that stayed GREEN | none of the assigned nodes stayed green for any mutant; the move-aside of `__init__.py` leaves 54 isolation nodes GREEN by design (a namespace package still imports), 3 go RED |

| Field | Value |
|---|---|
| **RED counterfactual** | (1) code-absent tree (captured before a one-line tripwire off-by-one fix inside `test_reach_budget_per_row`, which does not change any collection-time or allow-list result): `1 failed, 4 passed, 3 errors` (`ModuleNotFoundError: No module named 'mapper.relmap'` ×3, and the new allow-list entry fails `test_outside_app_only_the_allowed_names_are_imported_from_osopen`), exit 1, `evidence/inc1-red-code-absent.txt`. (2) move-aside per new source file: `profile.py` → 3 collection errors; `model.py` → 1 collection error; `__init__.py` → 3 failed (`test_the_relmap_package_exists_and_the_probe_sees_files`, `test_init_re_exports_nothing`, `test_py310_floor`); each restored, digest equal (`2a759d01f0ca9576…`, `6ebcf7ea82caac5d…`, `e3b0c44298fc1c14…`), `evidence/inc1-red-mutants-battery.txt` |

| Field | Value |
|---|---|
| **Mutation verdicts** | 19 mutants, **19 KILLED, 0 SURVIVED, 0 BAD, 0 CRASH**; every assigned node failed, none stayed green. Per mutant (position and operation → killing node): M-RMP-1 `model.py` `if types[e.type].downstream:` → `if e.type == "refines":` → `test_engine_names_no_kind` · M-RMP-2 tree `mapper/model.py` gains `from mapper.relmap import profile` → `test_only_app_and_the_package_import_relmap` · M-RMP-3 `profile.py` `verifies` downstream False→True → `test_edge_table` · M-RMP-4 tree `mapper/mermaid.py` `raise MermaidError(cycle)` → `pass` → `test_tc_rm_01_a_cyclic_tree_map_is_still_refused_at_load` · M-RMP-5 `profile.py` `US WITHOUT AT` HIGH→MED → `test_catalogue_table` · M-RMP-6 `model.py` also imports `MAX_MAP_BYTES` → `test_outside_app_only_the_allowed_names_are_imported_from_osopen` · M-RMP-6b the allow-list entry deleted → same node · M-RMM-1 disallowed-pair branch → `elif False:` → `test_problem_disallowed_pair`, `test_problem_mixed_input_yields_six_and_keeps_the_valid_remainder` · M-RMM-2 `if not types[e.type].downstream:` → `test_direction_per_edge_type` (+8 sibling arms), `test_direction_premise_six_figures_on_the_reqharness_profile` · M-RMM-3 `raise ValueError` when `cycles` → `test_cycle_self_loop`, `…three_nodes…`, `…two_disjoint…` · M-RMM-4 nodes sorted by id → `test_multi_parent_and_order` · M-RMM-5a node-cap check → `if False:` → `test_caps_nodes_at_cap_load_and_cap_plus_one_refuses` · M-RMM-5b edge-cap check → `if False:` → `test_caps_edges_at_cap_load_and_cap_plus_one_refuses` · M-RMM-6 reach counts path expansions not distinct nodes → `test_reach_diamond_counts_nodes_not_paths` · M-RMM-7 `import tomllib` planted in `model.py` → `test_py310_floor` · M-RMM-8 reach rewritten recursively → `test_reach_chain_at_cap_has_no_recursion_error` · M-RMM-9 the census flags every `.walk` (the `os` exemption removed, in the test) → `test_py310_floor_does_not_flag_a_legitimate_310_name` · M-RMM-10 memo stores the reachable set → `test_reach_memo_is_counts` · M-RMM-11 budget check → `if False:` → `test_reach_budget_per_row` (the `down` tripwire). Transcript `evidence/inc1-red-mutants-battery.txt` |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| import census (`forbidden_imports`) | 11 planted sources: function-local `from mapper.model import Graph`, `import mapper.mermaid`, relative `from ..model import Graph`, `import textual`, … (parametrised, each must report ≥ 1) | `test_planted_violations_are_reported` green only because each plant is found; on the real tree M-RMP-6 (an extra osopen name) fails `test_outside_app_only_…` |
| importer census (`importers_of_relmap`) | 5 planted importers in four spellings (`from mapper.relmap.model import …`, `import mapper.relmap`, `from mapper import relmap`, relative, function-local) | `test_the_importer_census_can_see_an_importer`; M-RMP-2 plants a real importer in the tree kind → `test_only_app_and_the_package_import_relmap` failed (`evidence/inc1-red-mutants-battery.txt`) |
| engine-literal census (`engine_literal_violations`) | 4 planted literals (`"refines"`, `"US"`, `"HLR WITHOUT LLR"`, `"binds"`) plus the empty-set guard (`ValueError`) | M-RMP-1 hard-codes `"refines"` into `model.py` → `test_engine_names_no_kind` failed |
| floor census (`floor_violations`) | 13 planted post-3.10 forms (`import tomllib`, `StrEnum`, `typing.Self`, `itertools.batched`, `datetime.UTC`, `Path.walk`, `ExceptionGroup`, …) and 6 legitimate 3.10 forms that must NOT be flagged; `except*` must raise `SyntaxError` | M-RMM-7 plants `import tomllib` into `model.py` → `test_py310_floor` failed; M-RMM-9 mutates the census itself → the legitimate-name arm failed |
| the `down` tripwire (`test_reach_budget_per_row`) | M-RMM-11: reach bypasses the shared budget | the wrapper raised `AssertionError: tripwire: more node expansions than the budget` on the 2,000,001st `down` call (the assertion is `calls <= VISIT_BUDGET`) instead of hanging (`evidence/inc1-red-mutants-battery.txt`, M-RMM-11: 1 failed in 1.68 s) |
| int-memo check (`test_reach_memo_is_counts`) | M-RMM-10: memo stores a set | 1 failed (a non-`int` memo value) |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 6 instruments, each shown RED by a planted or mutated known-bad input before its green was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/relmap/__init__.py` (the file as written) | `test_init_re_exports_nothing` parses the file on disk and asserts an empty body; `sha256sum` of the stored file | `e3b0c44298fc1c14…` (the SHA-256 of zero bytes); body empty |
| `docs/ARCHITECTURE.md` §2 `relmap` row | `test_at_p04_every_owned_path_exists_on_disk[relmap-mapper/relmap/{__init__,profile,model}.py]` over the written row | 3 arms collected and passed (`evidence/inc1-guards.txt`) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against the form its producer wrote |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED on the code-absent tree (exit code 1, 1.6 s wall) | `.dev-flow/2026-10-25-relmap-r1-batch/evidence/inc1-red-code-absent.txt` | `25fdbe2c81a2bbda17732807ae4ae09966098983f609296946c6e318b396fa40` |
| GREEN, targeted run, 132 passed (exit code 0, 7.4 s wall) | `.dev-flow/2026-10-25-relmap-r1-batch/evidence/inc1-green-first.txt` | `3d85b30bfe648b17642069fabd74fbfe154cb3da2efc375c1eb1c66d916fe996` |
| Guard suites, 142 passed (exit code 0, 36.9 s wall) | `.dev-flow/2026-10-25-relmap-r1-batch/evidence/inc1-guards.txt` | `b46995a0c362a4decbe5a29b0f66aab0a5a6b73348f58fc22afcd101793fda3a` |
| Move-aside RED + 19-mutant battery (driver exit code 0, 34.0 s wall) | `.dev-flow/2026-10-25-relmap-r1-batch/evidence/inc1-red-mutants-battery.txt` | `b8e59c1485c33c2745567c64a18b33d8f3a1d7783c78272c94be816a7b1b0032` |

| Field | Value |
|---|---|
| **Evidence files** | 4 artifacts, each at the declared home and cited with the digest of its stored bytes; every transcript is redacted (`<user>`) before hashing and records its own exit code and wall time |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no module outside `relmap` and `app.py` imports `relmap`" and "no engine literal in `model.py`" are absences over today's tree |
| If the result is an ABSENCE, what made the search wide enough | both censuses walk `ast.walk` over every `mapper/**/*.py` and count function-local imports and relative imports; the literal set is derived from the shipped profile and guarded by `len(set) >= 17` |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_engine_names_no_kind` (the `len >= 17` guard and the empty-set refusal), `test_the_relmap_package_exists_and_the_probe_sees_files` (a census over an absent package is refused), `test_py310_floor` (`len(files) >= 3`) |
| Conjunctive criteria: one mutation per conjunct | the node/edge caps: M-RMM-5a and M-RMM-5b, one each; the six problem kinds: M-RMM-1 for the pair check, the other five by one node each in `test_problem_*` (arms, not a separate mutant) |
| Synthetic instance of the absent case | planted sources for every census (11 + 5 + 4 + 13 + 6 cases) and a synthetic `LOOPY` profile for cycles the `reqharness` kind graph cannot form (premise 5) |
| **Positive control for every probe that returned an ABSENCE** | the importer census returned `{}` on the real tree; the same unmodified function returns `True` on each of the 5 planted importers; the real `forbidden_imports` returned `[]` on 3 files and ≥ 1 on each of the 11 plants |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `git grep -l "relmap" -- tests mapper docs`; `git grep -l "MAX_NODES\|MAX_EDGES" -- tests` | `relmap`: only this increment's files and `docs/ARCHITECTURE.md`; `MAX_NODES`/`MAX_EDGES`: `tests/test_arch_osopen_callers.py` (edited here) and `tests/test_ingestion_limits.py` (the hygiene batch's; it reads the `osopen` constants, which this increment does not change, so it was not run: no symbol it asserts moved) |
| B2 file moved on disk | none moved — nothing renamed | no readers to find |
| B3 byte-identical golden captures this source | `git grep -il relmap -- tests/goldens` | 0 hits |
| B4 artifact produced here is consumed elsewhere | nothing is written; `relmap` has no importer in `mapper/` yet (`git grep -n relmap -- 'mapper/*.py' ':!mapper/relmap'` → 0 hits) | no consumers until Inc-5 |
| A3 interface consumed by another module changed | the module-map oracles over the touched surfaces: `test_mod_*`, `test_repair_map_truth`, `test_arch_osopen_callers`, `test_a3_census` | 142 passed; the A3 pin 86 unmoved |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B3, B4, A3), each with its command and verdict; the one B1 hit outside the new files that this increment edits (`test_arch_osopen_callers.py`) was re-validated green; B2 did not fire (no file moved) and B3 did not fire (0 hits) |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the osopen importers of `MAX_NODES`/`MAX_EDGES` named in the architecture map move from commitment to as built | places in `docs/ARCHITECTURE.md` that name `relmap/model.py` as an osopen importer | `git show HEAD:docs/ARCHITECTURE.md | grep -n "relmap/model.py"` run before the edit | 4 (lines 136 §2 osopen cell, 187 §3 osopen cell, 316 the Inc-1 row of the batch table, 327 the census list) | the §2 and §3 osopen cells (136, 187) | lines 316 and 327 state the file set and the allow-list as the PLAN of the batch (future-tense planning text that stays true); left unchanged |

| Field | Value |
|---|---|
| **Correction population** | 1 correction, enumerated before its first site was edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `commitment, batch 2026-10-25-relmap-r1-batch, planned Inc-1 to Inc-5: the package directory` (the old `relmap` owned-paths cell) | `git grep -c "planned Inc-1 to Inc-5: the package directory" -- docs` → 0 hits | yes | `docs/ARCHITECTURE.md` §2 `relmap` row now lists the three landed paths |

### Signed-balance test ledger

`post = base − deleted + added` → `132 = 5 − 0 + 127` for the four targeted files (`test_arch_osopen_callers.py` keeps its 5 nodes, edited in place; the three new files add 16 + 53 + 58 = 127, counted with `--collect-only`) ✓ reconciles with `132 passed`.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Claude Sonnet subagent executing agents/code-reviewer.md · approve-with-nits` · no BLOCKER, no MAJOR; F1-F5 MINOR; 5/5 own mutants killed and restored by hash · `evidence/review-inc001.md` |

---

## 5 · Risks

- **No real Python 3.10 run** (no interpreter on this machine, no CI): the floor is proxied by `ast.parse(feature_version=(3, 10))` and a qualified-name census; the operator-run 3.10 check stays a Phase 4 item (`not-run`).
- **Budget exhaustion is sticky**: after `VISIT_BUDGET` expansions every not-yet-memoised `reach` returns `None`, including for cheap rows. That is what the contract says ("None occurs only after the budget is spent"), but Inc-2's ranking must treat it as "not computed" for the rest of the map's life, not per call.
- **The memo seam is private**: `test_reach_memo_is_counts` reads `RelMap._reach_memo` (a stated seam, not frozen). Renaming it fails that test loudly, not silently.
- **The census guards the tree it can see**: a dynamic import (`importlib`) would escape `forbidden_imports`; the contract bans nothing of the kind and none exists.
- **Layer B does not exist yet**: AT-117/AT-124 first run at Inc-5; until then the figures are asserted in-process only.

---

## 6 · Pending items / spec deviations

Contract issues found (none changed behaviour silently; each is a proposed amendment or a stated reading):

1. **`cut` and "120 characters"** (LLR-RMU.1.2 and the `DISPLAY_MAX` definition say "cut to 120 and ends `…`"; AT-129 says "≤ 120 characters before escaping and ends `…`"). Read as 119 characters plus `…` = 120 in total (`cut` in `model.py`, `test_cut_boundary_120_and_121`). If the intended reading is 120 characters plus the ellipsis, one line in `model.py` and one arm change. Proposed ledger note.
2. **LLR-RMM.2.2's "2,000-node chain" for the memo arm**: calling `reach` for EVERY node of a 2,000-node chain costs 2,001,000 expansions, 1,000 over the budget, so the tail rows would return `None`. The arm therefore calls every 7th row (about 286 rows, about 286k expansions) and asserts every retained memo value is an `int`; the M-RMM-10 kill does not need more. Proposed wording amendment: "a 2,000-node chain, sampled rows".
3. **No test enforces the ARCHITECTURE bans on `subprocess`, network modules and any write under the repo** for `relmap` (§3 `relmap` row); LLR-RMP.2.1 permits "the standard library" without exception, and I did not add an unapproved assertion. Proposed: a one-line census addition with the Inc-3 descriptor (the first module that touches files), via a ledger entry.
4. **Contract-silent choices, stated** (all in `model.py`, each with a test): `Problem.subject` for an edge is `<src>-><dst>`; a node is a `duplicate id` only against ACCEPTED ids (an earlier node excluded for an unknown kind does not make a later same-id node a duplicate); cycles are computed on the authored `src -> dst` graph (premise 5: the kind graph is a DAG over those pairs), members and components in node input order, a self-loop is a component of one; `Profile.__post_init__` also refuses a `severity` outside {HIGH, MED, LOW} (an addition to the contract's "kinds not in `node_kinds`" refusal; the four-pattern closed set is the contract's).
5. **M-RMP-2 reading**: the contract's "a `model.py` import of `relmap`" was applied to the TREE kind's `mapper/model.py` (HLR-RMP.2: nothing outside the package imports it); M-RMP-6 is run in both forms (an extra osopen name in source, and the allow-list entry deleted).
6. The `ARCHITECTURE.md` `relmap` §3 row and the `yamlscan` rows stay commitments (Inc-2..5 / Inc-3 own them).

7. **Gate run** (`PYTHONIOENCODING=utf-8 python devflow-validate.py --brief .`, after the files were staged): exit 1, **13 BLOCK, all `V2`** (`AT-117` to `AT-129` have no node on disk). `V2` is the flow's declared station-expected red at `P3` (`_STATION_EXPECTED`): those thirteen Layer B nodes are minted by Inc-5 (proposal §2.1 *Layer phasing*), and a placeholder node here would be the vacuous check the batch avoids, so none was written. Every other finding is a NOTICE; this packet's own: `V36` (the independent review is pending, by instruction), `V56` (the highest failure count the packet reports is `3 failed` while the cited battery transcript holds `9 failed`: the 9 are M-RMM-2's sibling `test_direction_per_edge_type` arms, a deliberately failing mutant run, not a defect), `V41` (4 evidence rows resolved and hashing as cited). `V62` (PLAN `Last updated` does not name `P3`) is the orchestrator's cell and was not edited.

Nothing is deferred silently; items 1 to 3 go to the backlog at batch close if the orchestrator does not fold them first.

---

### Follow-ups after the independent review (recorded in the Inc-2 unit, 2026-10-25)

| Item | Disposition |
|---|---|
| §6 items 1, 2, 3, 4 | ruled and recorded: ledger `LED-…44` (`cut` = 120 characters in total, the last being `…`), `.45` (sampled-rows memo arm), `.46` (stdlib-ban census owned by Inc-3: a planned Inc-3 test named `test_stdlib_bans` (in the isolation test module), in PLAN row 3), `.47` (silent-contract choices stated) |
| F1 raw `Problem` subjects | ledger `.48`: stated; the formatter cuts and escapes, Inc-5 asserts it |
| F2 `model.py:14` docstring ("the one counted seam") | FIXED, comment-only edit to the module docstring in the Inc-2 commit (the counter lives in `reach`; `down` is the one adjacency read; a ranking must go through `reach`); no code line changed; Inc-2's `test_gaps_reads_no_adjacency_itself` enforces it for `gaps.py` |
| F3 duplicate identical edges kept | ledger `.49`: stated |
| F4 `Profile` does not validate `EdgeType.evidence` / duplicate names | BACKLOG `B-145`, due when R5 adds `lineage` |
| F5 `sourced` not intersected with node kinds | ledger `.50`: stated |

---

## 7 · Suggested next task

Inc-2 (`mapper/relmap/gaps.py`, 1 source file): the generic detectors over `Profile.gaps` with no kind/edge literal, qualified sentences, and `rank_gaps` on the shared visit budget (`reach` returns `None` once spent), with `test_rank_visit_cap` carrying the `down` tripwire. Before it starts: the orchestrator's `code-reviewer` pass over this diff and a decision on contract issues 1 and 2.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 / 4: `__init__.py`, `profile.py`, `model.py` (§2) |
| 2 | Tests written in this same increment | all | ✓ | 3 new test files + the allow-list edit; 132 passed (`evidence/inc1-green-first.txt`) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_relmap_model.py` (validation branches, Tarjan, reach, neighbourhood) and `test_relmap_profile.py` (construction refusals); mutation-measured, 19/19 killed |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | code-absent RED + move-aside per source file, `evidence/inc1-red-code-absent.txt` (`25fdbe2c…`) and `evidence/inc1-red-mutants-battery.txt` (`b8e59c14…`); restore digests per arm |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | five probes with commands in §4; A3 pin 86 unmoved (`evidence/inc1-guards.txt`) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | approve-with-nits, `evidence/review-inc001.md` (§4b) |
| 7 | No file from another lane touched | all | ✓ | no lane; the 7 touched paths are in the file set of proposal §2.1 row 1 (plus the tree-kind files only as mutation targets, restored by hash) |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D3 names created as frozen (`Profile`/`EdgeType`/`GapRow`/`REQHARNESS`, `Node`/`Edge`/`Problem`/`RelMap`, `build_map`, `RelMapLimitError`, `VISIT_BUDGET`, `DISPLAY_MAX`, `cut`); D1/D2/D4/D5 not touched |
| 9 | Coverage claims verified **on disk**, not from intent | all | ✓ | every test node named in §4 exists in `tests/test_relmap_{profile,model,isolation}.py`, collected and run (132 arms) |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | all | ✓ | §4 *Load-bearing emptiness* |
| 11 | **Mutation verdicts** declared — per arm | all | ✓ | 19 mutants, 19 KILLED, per mutant and node in §4 |
| 12 | **Instrument RED-proof** declared | all | ✓ | 6 instruments, §4 |
| 13 | **Correction population** declared | all | ✓ | §4: 1 correction, enumerated with its command |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4: 2 artifacts |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` (Claude Sonnet subagent), approve-with-nits (§4b) |
| 16 | **Evidence files** declared | all | ✓ | §4: 4 artifacts with SHA-256 |
