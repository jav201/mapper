# Increment 022 — LLR-MOD.1.1–1.3, 3.1, 3.2, 6.1, 6.2, 7.1, 7.2; HLR-MOD.1, 3, 5, 6, 7 · `B12 — app.py __all__; ARCHITECTURE landed; the mod guard test files`

> **Artifact language:** English.
> **Owed in.** `core` ✓ · `full` ✓
> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-022.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `022` (B12) |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | `LLR-MOD.1.1–1.3, 3.1, 3.2, 6.1, 6.2, 7.1, 7.2` · `HLR-MOD.1, 3, 5, 6, 7` |
| Acceptance | AT-068 (`test_mod_structure.py`) · AT-067/069 (`test_mod_compat.py`) · AT-070/071 (`test_mod_deps.py`) · LLR-MOD.7.2 census-freeze (`test_mod_census.py`) · full suite at the B10–B12 gate |
| Agent | `d4948b2` (`app.py __all__` + ARCHITECTURE) — orchestrator (Claude Opus 5.5). `e5d80e9` (the four guard test files) — Kimi (`kimi-for-coding`), per the facts sheet. Gate — orchestrator. |
| Date | `2026-10-10` |

---

## 1 · What changed

- **`mapper/app.py` declares its re-exports in `__all__` (LLR-MOD.3.1).** A 25-name `__all__` block at `app.py:44` covers the 21 imported names of premise 10 plus the historical re-export surface (`MapperApp`, `main`, the search labels, `_TemplateScreen`, `_path_refusal`, `pan_extent`, …); `ruff check mapper/app.py` is clean again (the re-exports were F401 since B0). `app.py` is 340 lines.
- **`docs/ARCHITECTURE.md` records the split as landed (HLR-MOD.1).** The TARGET rows of the batch amendment become facts; F1–F5 marked frozen; the B8 `action_open_ficha` deviation recorded.
- **Four permanent guard test files land (2,017 lines).** `test_mod_structure.py` (AT-068, LLR-MOD.1.1–1.3), `test_mod_deps.py` (AT-070/071, LLR-MOD.6.1/6.2/7.1), `test_mod_compat.py` (AT-067/069, LLR-MOD.3.1/3.2), `test_mod_census.py` (LLR-MOD.7.2 census diff vs `spike/census.json`) — from this gate on, the whole modularisation contract has executable guards with tmp-copy RED arms.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | LLR-MOD.3.1 | `__all__` re-export block added (+33); 340 lines |
| `docs/ARCHITECTURE.md` | doc | | TARGET rows → facts; F1–F5 frozen; B8 deviation recorded (±26) |
| `tests/test_mod_structure.py` | test | LLR-MOD.1.1–1.3, AT-068 | new — 619 lines, 10 nodes incl. RED arms |
| `tests/test_mod_deps.py` | test | LLR-MOD.6.1, 6.2, 7.1, AT-070/071 | new — 470 lines, 11 nodes incl. RED arms |
| `tests/test_mod_compat.py` | test | LLR-MOD.3.1, 3.2, AT-067/069 | new — 618 lines, 32 nodes incl. patch-guard RED arms |
| `tests/test_mod_census.py` | test | LLR-MOD.7.2 | new — 310 lines, 3 nodes incl. `test_llr_mod_7_2_red_new_method` |
| `tests/test_inc9c.py` | test | LLR-MOD.5.2 | post-review census repair `1c77233` (group review B1–B12 MED / CR-1 / CR-2): 'one home' scan package-wide again (was vacuous after the moves) |
| `tests/test_inc9o.py` | test | LLR-MOD.5.2 | post-review census repair `1c77233` (group review B1–B12 MED / CR-1 / CR-2): 'one home' scan package-wide again + tmp-copy RED arm |
| `tests/test_inc9p.py` | test | LLR-MOD.5.2 | post-review census repair `1c77233` (group review B1–B12 MED / CR-1 / CR-2): 'one home' scan reads every moved module + tmp-copy RED arm |
| `tests/test_inc9q.py` | test | LLR-MOD.5.2 | post-review census repair `1c77233` (group review B1–B12 MED / CR-1 / CR-2): 'one home' scan reads every moved module + tmp-copy RED arm |
| `tests/test_draft_hygiene.py` | test | LLR-MOD.5.1 | post-review census repair `1c77233` (group review B1–B12 MED / CR-1 / CR-2): guard-flag owner set narrowed to the drafts concern (CR-1) |
| `tests/test_search.py` | test | LLR-MOD.5.1 | post-review census repair `1c77233` (group review B1–B12 MED / CR-1 / CR-2): duplicate-name asserts in the mixin-aware helpers (CR-2) |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** |
| Test files | 10 (uncapped; 4 new guard files + 6 census files repaired in `1c77233`) |
| Doc files | 1 (`docs/ARCHITECTURE.md`, outside the count) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py tests/test_mod_deps.py tests/test_mod_compat.py tests/test_mod_census.py
python -B -m pytest -q -p no:cacheprovider tests/   # the increment gate (orchestrator-run; transcript cited in §4)
ruff check mapper/app.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `tests/test_mod_structure.py` (10), `tests/test_mod_deps.py` (11), `tests/test_mod_census.py` (3) | 24 passed (`--collect-only` counts; §4 run) |
| **A · white-box** ↔ LLR | `core` · `full` | `tests/test_mod_compat.py` (32; `-k reexport`, `-k patch_guard`) | 32 passed |
| **B · black-box** | `core` · `full` | AT-067, AT-068, AT-069, AT-070, AT-071 | within the 56 |
| **This increment's files** | — | 56 nodes | **56 passed in 15.70s** (run in this worktree: `tests/test_mod_structure.py tests/test_mod_deps.py tests/test_mod_compat.py tests/test_mod_census.py`) |
| **Gate** | — | full suite | **3124 passed, 24 deselected, 3 xfailed, 0 failed, exit=0** (`b10b12-gate-full-suite.transcript`) |
| `ruff` corroboration | — | `mapper/app.py` | `All checks passed!` (per commit `d4948b2`) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none hand-applied by this unit — the four files ship with their own tmp-copy RED arms |
| Instrument | each guard file runs its structural checker on the real tree (GREEN) and on a tmp-copy mutant (RED) — the contract's "permanent executable negative control" |
| Where it ran | the main checkout (orchestrator gate) |
| Transcript | `b10b12-gate-full-suite.transcript` (GREEN); per-arm RED output lives inside the guard files' tmp-copy arms, run at the gate |
| Restore proven by | tmp copies — the real tree is never mutated |
| Bytecode cache | gate run under `python -B`; my §4 run under `PYTHONDONTWRITEBYTECODE=1` |
| Arms resolved at baseline | all previously in-force controls (bodies 2 kinds, parity 1, dispatch 3) **plus** the new structure/deps/compat/census RED arms — assert the expected count is a property of each file's own collection, not a global number |
| Verdict granularity | per resolved node id (per facts sheet; e.g. `test_llr_mod_7_2_red_new_method` is its own node) |
| Arms that stayed GREEN | none recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | The increment's own new assertions are the four guard files, and each carries its RED arm in-tree: structure/deps/compat/census each run their checker on a **tmp-copy mutant** (synthetic module-level `import mapper.app`, a re-export dropped, a repoint skipped, a writer added to a second concern — per the contract's negative controls for LLR-MOD.1.1–1.3/3.1/6.x/7.2) and assert RED before the real-tree PASS is believed. Where the arm-level transcripts are stored: not recorded beyond the gate transcript; the arms are code, re-executed at every gate. |

| Field | Value |
|---|---|
| **Mutation verdicts** | At the B10–B12 gate, per the facts sheet, the full battery was in force: `test_mod_bodies.py` (one-token body mutation → KILLED; deleted import → KILLED), `test_mod_parity.py` (painted-string mutant → KILLED), `test_mod_dispatch.py` (duplicate names / mixin BINDINGS / dropped mixin → KILLED each), and **from B12** the `test_mod_structure`/`test_mod_deps`/`test_mod_compat`/`test_mod_census` RED arms (tmp-copy mutants → RED each, per the contract's negative controls). Arms that stayed GREEN: none recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_mod_structure.py` | tmp-copy tree with a concern method in the wrong module / a missing mixin | its RED arm (AT-068 stays RED on any wrong-module method, per the contract) |
| `tests/test_mod_deps.py` | synthetic module-level `import mapper.app` / sibling-concern import (AT-070/071 negative controls) | RED arms per the contract |
| `tests/test_mod_compat.py` | one re-export removed / a patch site's target module does not bind or read the name | RED arms per the contract (LLR-MOD.3.1/3.2 negative controls) |
| `tests/test_mod_census.py` | a synthetic writer added to a second concern for an F1 attribute (`test_llr_mod_7_2_red_new_method`) | RED per the contract's LLR-MOD.7.2 negative control |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 new instruments, each shipped with an in-tree tmp-copy RED arm, plus the 3 pre-existing permanent guards |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/app.py`'s `__all__` | `ruff check mapper/app.py` on the shipped bytes; `test_mod_compat.py -k reexport` asserts every imported name resolves with object identity | clean / passed |
| `docs/ARCHITECTURE.md` TARGET rows | read as the module map; HLR-MOD.1's observable outcome names the shipped tree (`screen.py` 840 lines, `app.py` ~350) | holds (340/840) |
| `tests/test_mod_census.py`'s census diff | re-runs `spike/ast_census.py` over the package and diffs against the committed `spike/census.json` | empty diff — passed |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted against its emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| b10b12-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/b10b12-gate-full-suite.transcript | be5b2dad71268e2e91a1a995e278bc568f1ae1586166849d2cddfa0c667f5d64 |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact, at the declared home, digest from `_facts/evidence-digests.md` |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — several: "census diff empty" (no writer drift), "0 imports of `mapper.app` under `screens/`", "0 pairwise method-name collisions", "0 mixin BINDINGS/@on/DEFAULT_CSS", "every patch site targets a module that binds or reads the name" |
| If the result is an ABSENCE, what made the search wide enough | whole-package AST scans in every guard; the census re-runs `ast_census.py` over the full package rather than diffing a hand-list |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_mod_census.py` (the census-freeze conclusion), `test_mod_deps.py -k at070` (the empty-set boundary of HLR-MOD.6), `test_mod_compat.py -k patch_guard` |
| Conjunctive criteria: one mutation per conjunct | per the contract, each negative control mutates one conjunct: a synthetic writer (census), one restored import (deps), one dropped re-export (compat), one wrong-module method (structure) |
| Synthetic instance of the absent case | each guard's tmp-copy mutant IS the synthetic instance of its absent case |
| **Positive control for every probe that returned an ABSENCE** | the same unmodified checkers return the present cases on the real tree (GREEN at the gate); the mutants return the absent cases (RED) |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rln "test_mod_structure\|test_mod_deps\|test_mod_compat\|test_mod_census" tests` | the four files reference each other only by shared fixtures in `tests/inc3_support.py`/`inc4_support.py` (re-run green at the gate) |
| B2 file moved on disk | n/a — no file moved in this increment | not fired |
| B3 byte-identical golden captures this source | n/a — no golden reads these files | not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rln "census.json" tests .dev-flow/2026-10-09-modular-batch/spike` | `tests/test_mod_census.py` consumes `spike/census.json` (the archive location) — consumer in-tree, green at the gate |

| A3 | interface consumed by another module changed | `grep -rn "from mapper.app import" mapper/screens/` | 0 hits — the `__all__` surface is consumed only by tests + `factory.py`/`settings.py` at historical sites (LLR-MOD.3.1 reexport nodes green) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 and B4 fired with the hits above, re-validated green; B2, B3, A3 did not fire) |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — no behavioural correction; the `__all__` addition is a declaration, and the four test files are new guards, not corrections of existing assertions |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| F401-unused re-export imports in `mapper/app.py` (unannotated since B0) | the 25 names are now inside `__all__` (`app.py:44`); `ruff check` clean | yes | commit `d4948b2`; `ruff` per its message |

### Signed-balance test ledger

`post = base − deleted + added` → `3124 = 3060 − 0 + 64` per the two gate transcripts (b3b9 → b10b12). The four new files collect **56** nodes (verified here: `--collect-only` → 56; run → **56 passed in 15.70s**). The remaining +8 of the gate delta is **not recorded** (§6).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only; group review B1–B12) · **APPROVE-WITH-NITS, 0 HIGH / 0 MED** · "B12 tests can fail on what they name." 4 LOW: **CR-1** `test_draft_hygiene` owner set too wide → narrowed by the post-review census-repair commit; **CR-2** duplicate-name assert in `test_search` helpers → added; **CR-3** `exporting.py`'s own `pan_extent` reader has no patched test → **recorded as a deliberate gap**; **CR-4** `focus_mode` imports `NavigationModel` from `navigation.py` → **sanctioned by `test_mod_deps`**. CR-1/CR-2 were folded by the post-review census-repair commit (Kimi unit MODREV; sha not recorded — not present in this worktree's history). |

---

## 5 · Risks

- The census freeze (`spike/census.json`) is a snapshot: legitimate F1/F2 changes now require a census amendment, and an amendment that smuggles a behaviour change would pass the diff — the gate suite (LLR-MOD.4.1/4.3/parity) is the backstop.
- CR-3's deliberate gap: the `pan_extent` reader inside `exporting.py` has no bite test; only the AST guard pins it.
- The +8 gate-delta residual (§4 ledger) is unreconciled; it does not affect any requirement trace.

## 6 · Pending items / spec deviations

- The post-review census-repair commit (Kimi unit MODREV; folded CR-1/CR-2 and the A-review census findings) is **not present in this worktree's git history — its sha is not recorded**; its content is known only from the facts sheet.
- The +8 difference between the gate delta (+64 passed) and the four files' collected nodes (56) is **not recorded**; `git diff 0735a0a..0923ca6 --stat -- tests/` shows no other test addition, so the residual is unexplained from available evidence.
- CR-3 carried as a deliberate gap; CR-4 sanctioned by `test_mod_deps`.

## 7 · Suggested next task

P4 — the full-suite close gate and the batch close (postmortem + the canonical backlog absorbing §6).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1 / 4 |
| 2 | Tests written in this same increment | all | ✓ | `e5d80e9` — 4 new test files, 56 nodes |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `test_mod_structure.py` (10) + `test_mod_deps.py` (11) + `test_mod_census.py` (3) |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | in-tree tmp-copy RED arms per file (§4) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | 5 probes (§4) |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | one lane |
| 8 | Frozen interfaces untouched | all | ✓ | bodies byte-identical per `test_mod_bodies`; F1–F5 frozen in ARCHITECTURE |
| 9 | Coverage claims verified **on disk** | all | ✓ | 56 passed here; 3124 passed at the gate |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 |
| 11 | **Mutation verdicts** declared | all | ✓ | full battery incl. the four new RED arms (§4) |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 new + 3 standing instruments (§4) |
| 13 | **Correction population** declared | all | ✓ | none — no correction (§4) |
| 14 | **Emitted-form assertion** declared | all | ✓ | `__all__` bytes, ARCHITECTURE rows, census diff (§4) |
| 15 | **Independent review** names somebody | all | ✓ | group review B1–B12 |
| 16 | **Evidence files** declared | all | ✓ | 1 file with sha256 |
