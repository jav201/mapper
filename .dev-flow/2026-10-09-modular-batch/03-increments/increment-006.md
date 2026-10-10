# Increment 006 — B0 · LLR-MOD.1.2 · `MapScreen moved whole to mapper/screens/map/screen.py`

> **Artifact language:** English.

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-006.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `006` (B0) |
| Lane (if the batch forked) | n/a — the spine is serial until B11 (§2.8 of the contract); no lane |
| Requirement(s) | `LLR-MOD.1.2 v1` · `LLR-MOD.3.1` · `LLR-MOD.3.2` · `LLR-MOD.5.2` · `LLR-MOD.6.2` · `HLR-MOD.1, 3, 4, 5, 6` |
| Acceptance | `AT-065` (painted parity) · `LLR-MOD.4.1` (full suite at the gate) · `LLR-MOD.4.3` (`tests/test_mod_bodies.py`) · unit `tests/test_mod_parity.py -k parity`. The dedicated structure node (`-k b0` / AT-068) lands at B12 — not yet in force here. |
| Agent | Product move by the **orchestrator's AST cut/paste scripts** (`b0_move.py`, `b0_prune.py` — bodies byte-identical); B0 census follow-ups (`bc2ff81`) by the orchestrator; the gate run by the orchestrator. No Kimi worker unit in this increment. |
| Date | `2026-10-09/10` (commits dated 2026-10-10) |

---

## 1 · What changed

**`MapScreen` (app.py:1536–4989, 3454 lines) now lives whole in `mapper/screens/map/screen.py`; `mapper/app.py` shed 3510 lines and keeps only `MapperApp`, `main`, the CSS and the re-export block.**

- New package `mapper/screens/map/`: `screen.py` (3541 lines — MapScreen with its lifecycle concern, all class constants and `BINDINGS`) and a re-export-only `__init__.py` (4 lines). `mapper/app.py` re-exports `MapScreen` so all 70 `from mapper.app import` sites keep resolving (LLR-MOD.1.2, LLR-MOD.3.1).
- Patch sites repointed to their reading modules in the same increment (LLR-MOD.3.2, premise 4): `MAX_RENDER_NODES` ×5 + `SearchIndex` ×1 (`tests/test_search.py`), `save_svg` ×3 (`tests/test_app.py`, `tests/test_inc9c.py`), `pan_extent` ×1 (`tests/test_en8.py`).
- Census follow-up `bc2ff81` (LLR-MOD.5.2): `test_fold.py` and `test_inc3_census.py` locate MapScreen through the class (`inspect.getfile`) instead of the `app.py` path pin.
- `docs/ARCHITECTURE.md` TARGET rows updated to record the move as landed.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | LLR-MOD.1.2, LLR-MOD.3.1 | MapScreen body deleted (−3510 lines); re-export block + `MapperApp` remain |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.2 | new — MapScreen whole (3541 lines) |
| `mapper/screens/map/__init__.py` | source | LLR-MOD.1.2, LLR-MOD.3.1 | new — re-export only (4 lines, no logic) |
| `docs/ARCHITECTURE.md` | doc | | TARGET rows amended (6 lines) |
| `tests/test_search.py` | test | LLR-MOD.3.2 | MAX_RENDER_NODES ×5 + SearchIndex patch sites repointed to `screens/map/screen.py` |
| `tests/test_app.py` | test | LLR-MOD.3.2 | save_svg patch sites repointed |
| `tests/test_inc9c.py` | test | LLR-MOD.3.2 | save_svg patch site repointed |
| `tests/test_en8.py` | test | LLR-MOD.3.2 | pan_extent patch site repointed |
| `tests/test_app_imports_used.py` | test | LLR-MOD.5.2 | source set follows the package |
| `tests/test_arch_osopen_callers.py` | test | LLR-MOD.5.2 | launcher-set follow-up (see §6 — it carried a defect) |
| `tests/test_mod_bodies.py` | test | LLR-MOD.4.3 | baseline keys follow the moved bodies |
| `tests/test_fold.py` | test | LLR-MOD.5.2 | MapScreen located through the class, not the app.py path (`bc2ff81`) |
| `tests/test_inc3_census.py` | test | LLR-MOD.5.2 | same generalisation (`bc2ff81`) |

| Count | Value |
|---|---|
| **SOURCE files** | **3 / 4** |
| Test files | 9 (uncapped) |
| Doc files | 1 (`docs/ARCHITECTURE.md`, outside the count) |

- ✓ Under the 4-source cap: the move is one logical unit — `screen.py`, the package `__init__.py` and the `app.py` re-export cannot be split without breaking the import surface mid-increment.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider            # the orchestrator's gate command (verbatim from the transcript)
python -B -m pytest -q -p no:cacheprovider tests/test_fold.py tests/test_inc3_census.py tests/test_arch_osopen_callers.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** (LLR-MOD.4.3 bodies oracle) | `core` · `full` | `tests/test_mod_bodies.py` | passed within the gate run (every census method exactly once, bodies `ast.dump`-equal to the Inc-0 baseline) |
| **A · white-box** ↔ LLR | `core` · `full` | census follow-ups `test_fold`, `test_inc3_census`, `test_arch_osopen_callers` | 2 of 3 RED at the gate (stranded by the move); re-run after the fixes: **46 passed, 3 xfailed** (transcript header) |
| **B · black-box** AT-065 ↔ painted screen | `core` · `full` | `tests/test_mod_parity.py` (widths 118/87) | 0 painted-line diffs within the gate run |

Gate (`a5a-b0-gate-full-suite.transcript`, run at `f2cec90`): **`3 failed, 2997 passed, 24 deselected, 3 xfailed in 1528.19s (0:25:28)`** — cited verbatim, including the failures:

- `FAILED tests/test_arch_osopen_callers.py::test_outside_app_only_the_allowed_names_are_imported_from_osopen` — the B0 follow-up reused the launcher set as the osopen-owner skip set (a defect in this increment's own test change; fixed in the next increment's A5b commit, §6).
- `FAILED tests/test_fold.py::test_llr_n06_2_3_every_repainted_region_coerces_what_it_paints` and `FAILED tests/test_inc3_census.py::test_a98_the_screen_imports_painted_ids_by_name_never_by_getattr` — both read MapScreen from `app.py` by path; **fixed in `bc2ff81` (this increment)**.

The transcript header records: "3 failures, all census tests the B0 move stranded … Fixed in the A5b commits (next); re-run of the three files: 46 passed, 3 xfailed."

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none unique to this increment — a pure move; the permanent controls below ran inside the gate |
| Instrument | the in-force permanent RED controls (this increment's gate): `tests/test_mod_bodies.py` (one-token body mutation and deleted import on a tmp copy → RED, LLR-MOD.4.3) and `tests/test_mod_parity.py` (painted-string mutant in a subprocess → RED, LLR-MOD.4.2/AT-065) |
| Where it ran | the orchestrator's gate environment |
| Transcript | `a5a-b0-gate-full-suite.transcript` |
| Restore proven by | tmp-copy mutants — the tree itself untouched |
| Bytecode cache | `python -B`, `-p no:cacheprovider` (gate command verbatim) |
| Arms resolved at baseline | not recorded per arm for this gate; the suite totals are 2997 passed / 3 failed |
| Verdict granularity | suite pass/fail per node (the 3 FAILED node ids are named above) |
| Arms that stayed GREEN | not recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none separate beyond the in-force permanent controls — this increment adds no new assertion of its own; its honest RED evidence is the gate itself: the move stranded three real census pins and the suite printed 3 FAILED (named above) until `bc2ff81` and the A5b commit repaired them. |

| Field | Value |
|---|---|
| **Mutation verdicts** | No separate mutation battery. In force at this gate: the `test_mod_bodies.py` battery (body mutation / deleted import → RED) and the `test_mod_parity.py` mutant (painted-string → RED) — both GREEN on the shipped tree within the gate. Not yet in force: `test_mod_dispatch.py` (lands B1), the `test_mod_structure/deps/compat/census` RED arms (land B12). Per-arm verdict granularity beyond suite pass/fail: not recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_fold.py`, `tests/test_inc3_census.py` | MapScreen no longer at the pinned `app.py` path | both printed `FAILED` at this very gate (node ids above) |
| `tests/test_arch_osopen_callers.py` | the B0 follow-up's defective osopen-owner skip set | `FAILED …test_outside_app_only_the_allowed_names_are_imported_from_osopen` at this gate |
| `tests/test_mod_bodies.py` | (tmp-copy) one-token body mutation / deleted import | RED per its Inc-0 negative controls — proven at Inc-0, GREEN here |
| `tests/test_mod_parity.py` | (tmp-copy) painted-string mutant | RED per LLR-MOD.4.2's negative control — proven at Inc-0, 0 diffs here |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments; three of them printed FAILURE at this increment's own gate, the two permanent oracles were proven RED at Inc-0 |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/screens/map/screen.py` + pruned `mapper/app.py` (on-disk AST) | `tests/test_mod_bodies.py` — per-method `ast.dump` against `mod-bodies-baseline.json`, every census method exactly once across the package | passed (within the 2997); a lost or duplicated method or a changed body reddens the diff |
| the re-export block in `mapper/app.py` | every `from mapper.app import MapScreen` site resolves (68 test files + `screens/factory.py`/`settings.py` in the gate) | 2997 passed — no ImportError |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts (the moved AST, the re-export surface), asserted on disk |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| a5a-b0-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a5a-b0-gate-full-suite.transcript | 9e070362760d219c51163119272861a5733b18b8580194d6b59286f6b9106424 |
| mod-bodies-baseline.json | .dev-flow/2026-10-09-modular-batch/evidence/mod-bodies-baseline.json | 7c76289cb7ed2649cc01edb870bc7d49d28d1cbf15eca3e1f7947f504aec6836 |
| mod_parity_118.txt | .dev-flow/2026-10-09-modular-batch/evidence/mod_parity_118.txt | 43af8e1e7613f23e9da0b9a3090c880c6b6f1cc0341f9befb8e032efd95fbf2d |
| mod_parity_87.txt | .dev-flow/2026-10-09-modular-batch/evidence/mod_parity_87.txt | 6ba755535f10274293193af98a54889ea4ecc6e132f43a1db78f8461a889b9b |

| Field | Value |
|---|---|
| **Evidence files** | 4 artifacts, cited with the digest of the stored bytes (from `_facts/evidence-digests.md`) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no census method lost or duplicated by the move" and "no `Screen` subclass left in `app.py` other than `MapperApp`" |
| If the result is an ABSENCE, what made the search wide enough | the bodies oracle searches **every** `*.py` under the package root for each baseline key — a key found 0 or ≥2 times fails |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_mod_bodies.py` — its docstring states it pins "no method lost or duplicated by a move" |
| Conjunctive criteria: one mutation per conjunct | one-token body mutation and lost-import mutation are separate tmp-copy arms (LLR-MOD.4.3), each RED at Inc-0 |
| Synthetic instance of the absent case | a key deleted from `screen.py` or pasted twice (the oracle's own tmp-copy arms) |
| **Positive control for every probe that returned an ABSENCE** | the gate's 3 FAILED census nodes: the same unmodified probes reported the PRESENT (stale) cases when the pins pointed at real code |
| ⚠ honesty note | the dedicated "no `mapper.app` import under `screens/`" ban (LLR-MOD.6.2) is **not test-enforced until B12** (`test_mod_deps.py`); at this gate it holds by convention and by the group review's no-back-edges finding |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "from mapper.app import" tests` (premise 2: 68 files) | all 68 + `screens/factory.py`/`settings.py` still resolve through the re-export — the gate's 2997 passed includes every importer |
| B2 file moved on disk | readers of MapScreen at the old `app.py` path | **fired**: `test_fold`, `test_inc3_census` (fixed in `bc2ff81`), `test_arch_osopen_callers` (defect fixed next increment) |
| B3 byte-identical golden captures this source | `grep mapper/app.py tests/goldens/**` | no golden captures source bytes — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rln "screens.map\b\|from mapper.screens.map" mapper tests` | `mapper/app.py` (re-export) + `test_mod_bodies.py` baseline keys; consumers re-validated by the gate |

| A3 | interface consumed by another module changed | patch sites now target `screens/map/screen.py` module-globals | the repointed sites bite — `test_search.py`, `test_app.py`, `test_inc9c.py`, `test_en8.py` all green in the gate |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run: B2 fired (3 readers found, all repaired), B1/B4 re-validated green, B3 not fired, A3 fired via the repointed patch surface |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| patch sites must target the module-global of the name's reader | the 8 patch targets of premise 4 | premise 4's full census over every patch form in `tests/` (enumerated at P0, before any move) | 7 module-global names / 16 sites total | this increment: MAX_RENDER_NODES ×5 + SearchIndex ×1 (`test_search.py`), save_svg ×3 (`test_app.py` ×2, `test_inc9c.py` ×1), pan_extent ×1 (`test_en8.py`) = 4 names / 10 sites | refusal_sentence (A1, already landed); LayeredRenderer (A7); preview_csv (A4); GitHubConnector.fetch needs no repoint (class-attribute patch, ARCH-11) |
| census pins that name MapScreen's home | every test reading `app.py` by path | premise 3's census (17 source-reading files) | 17 files scanned | the 3 that fired (`test_fold`, `test_inc3_census`, `test_arch_osopen_callers`) | rest already generalised at Inc-0 (LLR-MOD.5.1) |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections, each enumerated before the first site was edited (premises 3 and 4, P0) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| MapScreen's home = `mapper/app.py` (path pins) | 3 stranded readers at the gate | yes — after `bc2ff81` + the A5b commit, 0 surviving stale refs; re-run 46 passed, 3 xfailed | gate transcript FAILED lines; `bc2ff81` diff |

### Signed-balance test ledger

`post = base − deleted + added` → per-increment **collected** counts are not recorded (the gate transcripts record passed/failed, not collected totals). The executed progression at the gates: 2977 passed (A1) → 2987 (A2/A3) → **2997 passed / 3 failed** (this gate, A5a+B0). ⚠ stated as not recorded where the ledger's exact terms are unavailable — no number invented.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only, independent of the orchestrator scripts) · group review **A2–A4+B0** · **APPROVE-WITH-NITS, 0 HIGH** · every moved class/function of the pre-batch `app.py` (33 names) byte-identical (AST) in its new module; re-exports complete; every patch repointed to its reader; no back-edges/cycles. 3 MED (vacuous census scans: `test_inc9c:570`, `test_inc9o:338-345`, `test_inc9p:348` + `test_inc9q:387` still hand-listed) → repaired by the post-review census-repair commit (unit MODREV); 1 LOW (leak-exception key granularity, pre-existing coarseness) — carried. |

---

## 5 · Risks

- The gate exited 1: the `test_arch_osopen_callers` stranding was a defect **introduced by this increment's own follow-up** (launcher set reused as the osopen-owner skip set) and stayed red until the A5b commit — carried openly in §6.
- LLR-MOD.6.2's `screens → app` import ban is convention-plus-review only until `test_mod_deps.py` lands at B12; a regression in between would be caught by nothing automatic.
- `screen.py` at 3541 lines concentrates the whole MapScreen monolith; relief is the planned B1–B11 mixin split, not this increment.

## 6 · Pending items / spec deviations

- `test_arch_osopen_callers.py` failure at this gate: fixed in the next increment (A5b — the OSOPEN_OWNERS split from the launcher set).
- Per-arm mutation granularity beyond suite pass/fail: not recorded.
- None else open.

## 7 · Suggested next task

A5b: `RepoScreen` → `mapper/screens/repo.py`, landing before A6 because `PlugRepoScreen` pushes `RepoScreen` (ARCH-9); also closes this increment's `test_arch_osopen_callers` stranding.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 / 4 — `screen.py`, `__init__.py`, `app.py` are one indivisible move |
| 2 | Tests written in this same increment | all | ✓ | census follow-ups `bc2ff81` (`test_fold.py`, `test_inc3_census.py`); patch repoints in `f2cec90` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `tests/test_mod_bodies.py` (LLR-MOD.4.3) passed in the gate |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — in-force permanent controls (bodies, parity); the gate's own 3 FAILED census nodes |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — 5 probes; B2 fired, 3 readers repaired |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — group review A2–A4+B0, APPROVE-WITH-NITS, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | serial spine, one lane |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | F1–F5 freeze respected; patch surface repointed per PDR, not redesigned |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate run on the shipped tree: 2997 passed / 3 failed, cited verbatim |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — incl. the ⚠ that the deps ban is test-enforced only at B12 |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — bodies + parity batteries in force; dispatch/structure arms not yet (named) |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 4 instruments, 3 printed FAILURE at this gate |
| 13 | **Correction population** declared | all | ✓ | §4 — patch-repoint population from premise 4 (P0 census) |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — moved AST byte-compared; re-export surface resolved |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` (Claude Sonnet) |
| 16 | **Evidence files** declared | all | ✓ | §4 — 4 files with sha256 |
