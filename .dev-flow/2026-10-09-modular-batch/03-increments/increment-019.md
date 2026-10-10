# Increment 019 — LLR-MOD.1.3, LLR-MOD.3.2, LLR-MOD.5.2 · `B9 — search concern to the SearchingOps mixin; patches and census follow it`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-019.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `019` (B9) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `LLR-MOD.1.3` (searching module owns its census methods) · `LLR-MOD.3.2` (`MAX_RENDER_NODES` + `SearchIndex` repointed to their reading module) · `LLR-MOD.5.2` (extraction-riding test follow-ups land in the increment) |
| Acceptance | full suite at the B3–B9 gate · `tests/test_search.py` patch sites bite through `mapper.screens.map.searching` · the permanent guard tests |
| Agent | Product move + test follow-up `dd5ec28` — orchestrator script (`mixin_move.py`, AST cut/paste; Claude Opus 5.5). Gate — orchestrator. |
| Date | `2026-10-10` |

---

## 1 · What changed

- **The search concern moved.** 21 methods (675 lines) moved byte-identically from `mapper/screens/map/screen.py` into the new `mapper/screens/map/searching.py` (`class SearchingOps`, `searching.py:26`). `screen.py` shrinks by 707 lines; it composes `SearchingOps` as a mixin base.
- **Two patch names repointed (LLR-MOD.3.2).** `MAX_RENDER_NODES` and `SearchIndex` became module-globals of `searching.py` (their reading module); the suite's patch sites followed: 5 `monkeypatch.setattr(..., "MAX_RENDER_NODES", ...)` sites in `tests/test_search.py` now target the `searching` module, and the direct-assignment site `tests/test_search.py:1431` (`searching_module.SearchIndex = Counting`) follows likewise.
- **`test_search.py` walks the mixins (LLR-MOD.5.2).** The count-chain and walk-vocabulary censuses gained `_map_screen_methods`, which collects methods across the core **and its Spine B mixins**, so the source-reading censuses follow the move without weakening.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/searching.py` | source | LLR-MOD.1.3, LLR-MOD.3.2 | new — `SearchingOps` mixin (728 lines); binds `MAX_RENDER_NODES`, `SearchIndex` as module-globals |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.3 | search methods removed; mixin base added (−707/+1) |
| `tests/test_search.py` | test | LLR-MOD.3.2, LLR-MOD.5.2 | 5 `MAX_RENDER_NODES` setattrs + `SearchIndex` assignment repointed to `searching_module`; `_map_screen_methods` helper (±66) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 1 (uncapped) |
| Doc files | 0 |

- ⚠ LLR-MOD.5.2's contract names `test_inc9p.py`/`test_inc9q.py` "one home" arms for B9; no edit to those files appears in `dd5ec28` (see §6).

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/   # the increment gate (orchestrator-run; transcript cited in §4)
python -B -m pytest -q -p no:cacheprovider tests/test_search.py tests/test_inc9p.py tests/test_inc9q.py tests/test_mod_bodies.py tests/test_mod_parity.py tests/test_mod_dispatch.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_bodies.py` | passed — gate transcript |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_search.py` (count-chain/walk censuses over the mixins), `test_mod_dispatch.py` | passed — gate transcript |
| **B · black-box** | `core` · `full` | AT-065 parity; the 5 repointed `MAX_RENDER_NODES` patch sites + the `SearchIndex` assignment bite through `mapper.screens.map.searching` | passed — gate transcript |
| **Gate** | — | full suite | **3060 passed, 24 deselected, 3 xfailed, 0 failed, exit=0** (`b3b9-gate-full-suite.transcript`) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none hand-applied — pure move + repoint; the suite's permanent RED controls ran inside the gate. The contract's named negative control for LLR-MOD.3.2 ("RED when one repoint is skipped — the patch stops biting while the rest of the suite passes") is the shape of the risk; the AST patch-guard that proves the reader (`test_mod_compat.py` patch_guard node, in force from B12) pins the reader-module mapping `"SearchIndex": "mapper.screens.map.searching"` and the `MAX_RENDER_NODES` reader likewise. |
| Instrument | suite-owned tmp-copy mutants + the gate suite |
| Where it ran | the main checkout |
| Transcript | `b3b9-gate-full-suite.transcript` (GREEN); no increment-local hand-mutation transcript exists |
| Restore proven by | n/a — no hand mutation |
| Bytecode cache | gate run under `python -B` |
| Arms resolved at baseline | the permanent controls in force at this gate: `test_mod_bodies.py` (2 mutant kinds), `test_mod_parity.py` (1), `test_mod_dispatch.py` (3 mutant kinds) |
| Verdict granularity | per resolved node id, per facts sheet |
| Arms that stayed GREEN | none recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none for a hand mutation. The repointed patch sites are themselves executable RED instruments: with `MAX_RENDER_NODES` bound in `searching.py`, a site still targeting `screen_module` would raise `AttributeError` (the name no longer exists there) — the suite's search-refusal nodes (e.g. the AT-055/graph-size arms at `tests/test_search.py:2345+`) passed only through the repointed module-global. A dedicated skip-one-repoint transcript was not recorded. |

| Field | Value |
|---|---|
| **Mutation verdicts** | Ran inside the B3–B9 gate, per the facts sheet: `test_mod_bodies.py` — one-token body mutation (tmp copy) → RED (KILLED); deleted import in a new module → RED (KILLED). `test_mod_parity.py` — painted-string mutant → RED (KILLED). `test_mod_dispatch.py` — duplicated names / mixin BINDINGS / dropped mixin → RED each. Arms that stayed GREEN: none recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the 5 `MAX_RENDER_NODES` patch sites in `tests/test_search.py` | a target module that no longer binds the name (`screen_module` after the move) | `AttributeError` at setattr — the site cannot pass against the old target |
| `tests/test_mod_bodies.py` | one-token body mutation / deleted import (tmp copy) | RED arms per facts sheet |
| `tests/test_mod_parity.py` | painted-string mutant (subprocess) | RED arm per facts sheet |
| `tests/test_mod_dispatch.py` | duplicate names / mixin BINDINGS / dropped mixin | RED arms per facts sheet |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments; the repoint itself is shown biting by the impossibility of the old target (the name left `screen.py`), plus the 3 permanent guards |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the shipped `mapper/screens/map/searching.py` source | `test_mod_bodies.py` compares each moved method's `ast.dump` against the Inc-0 baseline JSON on disk | passed at the gate |
| the repointed patch sites (shipped `tests/test_search.py`) | the refusal/limit search nodes run with the patched limit one node below the map size, through the shipped screen | passed at the gate |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted on disk / through the shipped surface |

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
| Does any claim here rest on the tree holding NO instance of some case? | yes — "no lazy read of `MAX_RENDER_NODES`/`SearchIndex` through `mapper.app` or `screen.py`" (LLR-MOD.3.2's F4 ban) and the batch-standing exactly-once roster |
| If the result is an ABSENCE, what made the search wide enough | AST scans over the whole package (`test_mod_dispatch.py`'s patch-name import ban; `test_mod_deps.py` from B12), not a grep of one file |
| Guard labelled as protecting a CONCLUSION, not a behaviour | the LLR-MOD.2.2/3.2 AST guard (patch sites target a module that binds/reads the name) — lands as `test_mod_compat.py` patch_guard at B12, mapping `"SearchIndex"` and `"MAX_RENDER_NODES"` to `mapper.screens.map.searching` |
| Conjunctive criteria: one mutation per conjunct | no new conjunctive criterion |
| Synthetic instance of the absent case | the old target (`screen_module`) is the synthetic present case: the same setattr against it now fails with `AttributeError` |
| **Positive control for every probe that returned an ABSENCE** | the repointed sites pass against `searching_module` (the present case) at the gate |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rln "SearchingOps\|searching_module" tests mapper` | `tests/test_search.py` (re-run green in the gate), `mapper/screens/map/screen.py`, `mapper/screens/map/searching.py` — no stale reader of the moved methods |
| B2 file moved on disk | `grep -n "def .*search\|def _walk" mapper/screens/map/screen.py` | search/walk handlers gone from the core |
| B3 byte-identical golden captures this source | `grep -rl "searching" tests/goldens/** 2>/dev/null` | not fired — no golden directory |
| B4 artifact produced here is consumed elsewhere | `grep -rln "searching" mapper/screens/map/` | consumed by `screen.py` (composition) |

| A3 | interface consumed by another module changed | `grep -rn "MAX_RENDER_NODES\|SearchIndex" mapper/screens/` | bound and read only in `searching.py` (screen.py imports neither) — re-validated at the gate |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1, B2, B4, A3 fired with the hits above, re-validated green in the gate; B3 did not fire) |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| `MAX_RENDER_NODES` patch sites must follow their reader | every suite patch site of the 7 module-global targets | premise 4 census (`grep -Hn "monkeypatch.setattr" tests/test_search.py \| grep MAX_RENDER_NODES`) | 5 in `tests/test_search.py` | 5, all to `searching_module` | 0 — complete |
| `SearchIndex` patch site must follow its reader | the direct-assignment site of premise 4 | premise 4 census ("×1, direct attribute assignment") | 1 (`tests/test_search.py:1431`) | 1, to `searching_module` | 0 — complete |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections, both enumerated at premise 4 before the batch and executed in this increment; both populations fully edited, none left |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `screen_module` / `mapper.screens.map.screen` as the `MAX_RENDER_NODES`/`SearchIndex` patch target in `tests/test_search.py` | 0 hits for `setattr(screen_module, "MAX_RENDER_NODES"`; assignment reads `searching_module.SearchIndex` | yes | `tests/test_search.py:2345-2712` (setattrs), `:1431` (assignment); gate GREEN |

### Signed-balance test ledger

No test files added or deleted; `tests/test_search.py` was edited in place. Per-increment collection delta: not recorded (gate is shared across B3–B9; gate count 3060 passed / 0 failed).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only; group review B1–B12) · **APPROVE-WITH-NITS, 0 HIGH / 0 MED** · "patch repoints correct" and "census generalisations are not weakenings" are the findings touching this increment. 4 LOW: **CR-2** names this increment — a duplicate-name assert in `test_search`'s helpers was missing → added by the post-review census-repair commit (Kimi unit MODREV; its sha is not recorded in this worktree's history). CR-1/CR-3/CR-4 belong to B7/B2/B5. |

---

## 5 · Risks

- `searching.py` is the largest mixin (728 lines) and owns the render-bound constant; the silent-failure mode is a future lazy read re-entering through `mapper.app` — guarded only mechanically from B12 (AT-067/AST guard); between B9 and B12 the gate suite is the only bite.
- The count-chain census now resolves names across 12 modules; a method name collision between mixins would silently merge the censuses — LLR-MOD.2.2's disjointness guard covers it and ran at this gate.

## 6 · Pending items / spec deviations

- LLR-MOD.5.2 names `test_inc9p.py`/`test_inc9q.py` "one home" arms as B9 follow-ups, but `dd5ec28` contains no edit to those files; whether their scanned sets already covered the package at Inc-0 (LLR-MOD.5.1) or needed an extension is **not recorded**. They passed at the gate either way.
- The post-review census-repair commit (CR-2) is not present in this worktree's git history — sha **not recorded**.

## 7 · Suggested next task

B10 — the pan concern to `PanningOps`, with the `pan_extent` repoint (`increment-020`).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ✓ | `dd5ec28` — `tests/test_search.py` follow-ups |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_bodies.py` at the gate |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | repoint bite + permanent battery (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | bodies byte-identical per `test_mod_bodies` |
| 9 | Coverage claims verified **on disk** | all | ✓ | 3060 passed at the gate |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | bodies/parity/dispatch arms KILLED (§4) |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | 2 corrections, both complete (§4) |
| 14 | **Emitted-form assertion** declared | all | ✓ | shipped `searching.py` + repointed sites |
| 15 | **Independent review** names somebody | all | ✓ | group review B1–B12 |
| 16 | **Evidence files** declared | all | ✓ | 1 file with sha256 |
