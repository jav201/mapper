# Increment 012 — LLR-MOD.1.3 / 3.2 / 5.2 · `B2 — export concern to the ExportingOps mixin`

> **Artifact language:** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the **repo**, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-012.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `012` (Inc-B2) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `HLR-MOD.1 v1 / LLR-MOD.1.3` · `HLR-MOD.3 v1 / LLR-MOD.3.2` · `HLR-MOD.5 v1 / LLR-MOD.5.2` |
| Acceptance | LLR-MOD.3.2 — the 3 `save_svg` patch sites repointed to `mapper.screens.map.exporting` · LLR-MOD.5.2 — `test_search` mixin-aware census · white-box `tests/test_mod_dispatch.py` (AT-066 mutant generalised) · full-suite gate |
| Agent | Each worker ran in its own worktree.<br>• **the move** (3 methods, 217 lines, byte-identical, `mixin_move.py` + `screen_prune.py`) and the **census follow-ups:** the orchestrator (Claude Opus 5.5);<br>• **the gate run:** the orchestrator. No Kimi-authored test files in this increment. |
| Date | `2026-10-09/10` |

---

## 1 · What changed

**The export concern moved out of `MapScreen` into the new `mapper/screens/map/exporting.py`, and the `save_svg` monkeypatch surface was repointed to its new reading module.**

- 3 methods (217 lines) moved **byte-identically** into `mapper/screens/map/exporting.py` (243 new lines); `screen.py` shrank by ~228 lines and composes `ExportingOps`.
- LLR-MOD.3.2: the three `save_svg` patch sites were repointed — `tests/test_app.py:371`, `tests/test_app.py:475` and `tests/test_inc9c.py:134` now patch `mapper.screens.map.exporting.save_svg` instead of `mapper.screens.map.screen.save_svg`; `exporting.py` binds `save_svg` at module level from its true home (`mapper.export`).
- LLR-MOD.5.2 follow-ups: `test_search.py`'s self-read census and `_app_tree` now read `MapScreen`'s body **plus every mixin it inherits from** — the paint-pass census had gone blind at B1 once methods left the core class; `test_inc9c.py`'s census follows the mixin.
- `tests/test_mod_dispatch.py`'s AT-066 mutant was generalised to drop `HintsOps` from whatever bases `MapScreen` has (`re.subn` over the base list), so the RED arm keeps biting as Spine B composes more mixins.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/map/exporting.py` | source | LLR-MOD.1.3, LLR-MOD.3.2 | new — 3 methods moved byte-identically (243 lines); binds `save_svg` at module level |
| `mapper/screens/map/screen.py` | source | LLR-MOD.1.3 | export methods pruned; composes `ExportingOps` |
| `tests/test_app.py` | test | LLR-MOD.3.2 | 2 `save_svg` patch sites repointed (`:371`, `:475`) |
| `tests/test_inc9c.py` | test | LLR-MOD.3.2 | 1 `save_svg` patch site repointed (`:134`) + census follows mixins |
| `tests/test_search.py` | test | LLR-MOD.5.2 | self-read census + `_app_tree` read MapScreen's body plus all mixins (+25/−…) |
| `tests/test_mod_dispatch.py` | test | LLR-MOD.2.3 | AT-066 mutant drops `HintsOps` from whatever bases exist |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 4 (uncapped) |
| Doc files | 0 |

- ✓ At the Spine B shape — one new concern module plus its composing `screen.py`.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_app.py tests/test_inc9c.py tests/test_search.py
python -B -m pytest -q -p no:cacheprovider tests/test_mod_dispatch.py tests/test_mod_bodies.py
python -B -m pytest -q -p no:cacheprovider   # the increment gate — full suite, orchestrator-run
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_bodies.py` body oracle | GREEN at gate |
| **A · white-box** ↔ LLR | `core` · `full` | `test_search.py` mixin-aware census; `test_mod_dispatch.py` generalised mutant | GREEN at gate |
| **B · black-box** | `core` · `full` | the 3 repointed `save_svg` patch tests (`test_app.py`, `test_inc9c.py`) | GREEN at gate |
| **Increment gate — full suite** | — | whole suite | **3034 passed, 1 failed** (`b1b2-gate-full-suite.transcript`: `1 failed, 3034 passed, 24 deselected, 3 xfailed in 1575s`, exit=1) |

The one failure is the same pre-existing `tests/test_keymap.py::test_at_n03f_bound_keys_match_the_seat_exactly[map]` base-class blind spot carried from B1 — **fixed at B7 (`5229b12`)**, unrelated to the export concern. The repointed patch tests passed, proving the patches bite at the new module-global (a stale repoint would have failed these tests, not silently passed).

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none new of its own beyond the gate controls — the increment's own assertions are the repointed patch tests, whose RED side is a *stale* target (patching `screen.save_svg` after the reader left) — prevented by construction and covered by the LLR-MOD.3.2 AST guard |
| Instrument | permanent gate controls (see below) |
| Where it ran | the orchestrator's checkout / the gate |
| Transcript | `b1b2-gate-full-suite.transcript` |
| Restore proven by | n/a — no in-place mutation in this increment |
| Bytecode cache | gate runs with `python -B` |
| Arms resolved at baseline | the generalised AT-066 mutant (`HintsOps` dropped from whatever bases) resolves 1 arm |
| Verdict granularity | per node id |
| Arms that stayed GREEN | none named |

| Field | Value |
|---|---|
| **RED counterfactual** | none of its own beyond the permanent controls — this increment's correctness is "patches bite where the name is read", demonstrated by the repointed patch tests passing at the new home while `test_mod_compat.py`'s AST guard proves every patch site targets a name its module binds. Transcript: `.dev-flow/2026-10-09-modular-batch/evidence/b1b2-gate-full-suite.transcript`. |

| Field | Value |
|---|---|
| **Mutation verdicts** | In force at this gate, per the facts sheet: `tests/test_mod_bodies.py` — one-token body mutation on a tmp copy → RED; deleted import in a new module → RED. `tests/test_mod_parity.py` — painted-string mutant in a subprocess → RED. `tests/test_mod_dispatch.py` — duplicate names / `BINDINGS` in a mixin / `HintsOps` dropped (now base-list-generalised) → RED. Per-arm granularity; no arm reported inert. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_bodies.py` | one-token body mutation; a deleted import in the new module | baseline-diff RED; undefined-global RED |
| `tests/test_mod_parity.py` | painted-string mutant in a subprocess | parity capture RED |
| `tests/test_mod_dispatch.py` | tmp copy with `HintsOps` dropped from `MapScreen`'s bases | AT-066 pilot capture drifts → RED |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED before its first PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/screens/map/exporting.py` on disk | `tests/test_mod_bodies.py` compares each moved method's `ast.dump` against the Inc-0 baseline JSON | GREEN — bodies byte-identical, every census method exactly once |
| the repointed patch surface | `tests/test_mod_compat.py` AST-guards every `tests/` patch site against the names its module binds | GREEN at gate |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts (the moved module's AST and the patch-site surface), each asserted against the emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| b1b2-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/b1b2-gate-full-suite.transcript | e85dc07bb63ac1304fab58541ccf35ff52fe3ccd93f6f21581be07947dcfd343 |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact, at the declared home and cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no `screens/**` module imports any of the 8 patch names from `mapper.app`" and "no duplicated method across the 12 map modules" |
| If the result is an ABSENCE, what made the search wide enough | the AST scan covers every `mapper/screens/**` module (the LLR-MOD.2.2 guard) |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_mod_dispatch.py -k disjoint`; `test_mod_compat.py` AST guard |
| Conjunctive criteria: one mutation per conjunct | per contract the guard's conjuncts are mutated separately in the checker's tmp-copy arms |
| Synthetic instance of the absent case | the checkers' tmp-copy mutants |
| **Positive control for every probe that returned an ABSENCE** | the same unmodified suite reports the present patch bindings GREEN at the gate |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "ExportingOps" mapper tests` | 2 files: `exporting.py`, `screen.py` — only the composition consumes the mixin |
| B2 file moved on disk | none moved (new module) | not fired |
| B3 byte-identical golden captures this source | `grep -rln "save_svg" tests` | repointed patch tests in `test_app.py`, `test_inc9c.py` + compat/parity consumers — all re-validated green |
| B4 artifact produced here is consumed elsewhere | `exporting.py` is imported only by `screen.py` | 1 consumer |

| A3 | interface consumed by another module changed | `save_svg` module-global moved from `screen` to `exporting` | 3 patch sites repointed in the same commit (LLR-MOD.3.2) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run. B1: 2 hits, both this increment's own files. B3/A3 fired: the 3 patch sites moved with the reader, re-validated green. B2 and B4 did not fire beyond the composition itself. |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| `save_svg` patch sites must target the module that reads the name | every `monkeypatch` site naming `save_svg` (premise-4 census) | `grep -Hn "mapper.app.save_svg" tests/` (premise 4 of the contract) | 3 | `test_app.py:371`, `test_app.py:475`, `test_inc9c.py:134` | none — the reader moved, so every site moved with it |

| Field | Value |
|---|---|
| **Correction population** | 1 correction, enumerated by the contract's premise-4 census before the first site was edited |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `mapper.screens.map.screen.save_svg` as a patch target | 0 surviving patch sites (all 3 repointed) | yes | `test_mod_compat.py` AST guard GREEN at gate |

### Signed-balance test ledger

The gate count is carried from B1 (same transcript): `3034 passed + 1 failed = 3035`. Per-file deltas for this increment's test edits are in the commit diff but a collected-count reconciliation is **not recorded**.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, independent of the orchestrator) · group review **B1–B12** · **APPROVE-WITH-NITS, 0 HIGH / 0 MED / 4 LOW** — moved bodies byte-identical (AST); patch repoints correct; census generalisations ("read MapScreen's body plus every mixin") are **not weakenings** — they widen the scanned set. LOWs recorded at the group level: CR-1 → narrowed (MODREV); CR-2 → added (MODREV); CR-3 `exporting.py`'s own `pan_extent` reader has no patched test — deliberate gap; CR-4 `focus_mode`'s `NavigationModel` import — sanctioned by `test_mod_deps`. |

---

## 5 · Risks

- CR-3 (review): `exporting.py` reads `pan_extent` but no test patches it at the new module — acknowledged gap, recorded at the group review; the panning repoint lands at B10.

## 6 · Pending items / spec deviations

- The B1-carried `test_at_n03f` keymap failure is still red at this gate; fixed at B7 (`5229b12`). No deviation from the contract.

## 7 · Suggested next task

B3 — open concern to `screens/map/opening.py`, carrying the osopen §3 amendment and the `test_arch_osopen_callers.py` allow-list update (LLR-MOD.5.2, LLR-MOD.7.1).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 / 4 |
| 2 | Tests written in this same increment | all | ✓ | 4 test files follow the move |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_bodies.py` body oracle |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | permanent controls; repoint-by-construction (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b group review B1–B12, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | patch surface repointed per LLR-MOD.3.2, not broken |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate transcript 3034 passed |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | mod_bodies / mod_parity / mod_dispatch RED arms |
| 12 | **Instrument RED-proof** declared | all | ✓ | 3 instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | 1 correction — the 3 `save_svg` sites |
| 14 | **Emitted-form assertion** declared | all | ✓ | moved AST + patch-site surface |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` (§4b) |
| 16 | **Evidence files** declared | all | ✓ | 1 file with sha256 (§4) |
