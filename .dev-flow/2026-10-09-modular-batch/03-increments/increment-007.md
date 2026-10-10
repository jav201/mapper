# Increment 007 — A5b · LLR-MOD.1.1 · `RepoScreen moved to mapper/screens/repo.py; OSOPEN_OWNERS split from the launcher set`

> **Artifact language:** English.

> **Owed in.** `core` ✓ · `full` ✓

> **Where this lives:** the repo, `.dev-flow/2026-10-09-modular-batch/03-increments/increment-007.md`.

| Field | Value |
|---|---|
| Batch | `2026-10-09-modular-batch` |
| Increment | `007` (A5b) |
| Lane (if the batch forked) | n/a — serial spine, no lane |
| Requirement(s) | `LLR-MOD.1.1 v1` · `LLR-MOD.3.1` · `LLR-MOD.5.2` · `HLR-MOD.1, 3, 5` |
| Acceptance | `AT-065` (painted parity) · `LLR-MOD.4.1` (full suite at the gate) · `LLR-MOD.4.3` (`tests/test_mod_bodies.py`) · unit `tests/test_mod_parity.py -k parity` |
| Agent | Product move by a **Kimi (`kimi-for-coding`) unit** in an isolated worktree, with its own RED + sha256 restore in its own log (session scratch — not committed, see §6). Gate follow-up `d5c463d` (test_inc9n package scan, store.py symbol citations, transcript) and the gate run by the **orchestrator**. |
| Date | `2026-10-09/10` (commits dated 2026-10-10) |

---

## 1 · What changed

**`RepoScreen` now lives in `mapper/screens/repo.py` (337 lines); `mapper/app.py` shed 315 lines and re-exports the name; the OSOPEN_OWNERS skip-set defect that B0's follow-up introduced is fixed here.**

- `RepoScreen` cut whole from `app.py` into `mapper/screens/repo.py`; `mapper/app.py` keeps the re-export (LLR-MOD.1.1/LLR-MOD.3.1) — the 70 `from mapper.app import` sites never change.
- `test_arch_osopen_callers.py`: the osopen-owner set (`OSOPEN_OWNERS`) is split out of the launcher set — the B0 follow-up had reused the launcher set as the osopen-owner skip set, which is exactly the failure that gate ran red on (LLR-MOD.5.2; closes increment 006's carried item).
- Gate follow-up `d5c463d`: `test_inc9n.py` scans the package for the repo badge instead of reading it from `app.py` by path; `mapper/store.py` cites its load callers **by symbol** instead of by `app.py` line numbers (the line citations were already stale before this batch).
- `docs/ARCHITECTURE.md` TARGET rows updated.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | LLR-MOD.1.1, LLR-MOD.3.1 | RepoScreen body deleted (−315 lines); re-export kept |
| `mapper/screens/repo.py` | source | LLR-MOD.1.1 | new — RepoScreen whole (337 lines) |
| `mapper/store.py` | source | LLR-MOD.5.2 | 5 comment lines: load callers cited by symbol, not by app.py line numbers (`d5c463d`) |
| `docs/ARCHITECTURE.md` | doc | | TARGET rows amended (4 lines) |
| `tests/test_app_imports_used.py` | test | LLR-MOD.5.2 | source set follows the package |
| `tests/test_arch_osopen_callers.py` | test | LLR-MOD.5.2 | OSOPEN_OWNERS split from the launcher set (B0 defect fix) |
| `tests/test_inc9n.py` | test | LLR-MOD.5.2 | repo badge located by package scan, not the app.py path (`d5c463d`) |
| `evidence/a5b-gate-full-suite.transcript` | generated | LLR-MOD.4.1 | the gate transcript, recorded (`d5c463d`) |

| Count | Value |
|---|---|
| **SOURCE files** | **3 / 4** |
| Test files | 3 (uncapped) |
| Doc files | 1 (`docs/ARCHITECTURE.md`, outside the count) |
| Generated | 1 (gate transcript) |

- ✓ Under the cap: `app.py` + the new module + the store.py citation repair; each is required by a different gate finding.

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider            # the orchestrator's gate command (verbatim from the transcript)
python -B -m pytest -q -p no:cacheprovider tests/test_inc9n.py tests/test_repair_artifact_claims.py   # the two failing files, post-fix
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** (LLR-MOD.4.3 bodies oracle) | `core` · `full` | `tests/test_mod_bodies.py` | passed within the gate run (RepoScreen's methods exactly once, `ast.dump`-equal to baseline) |
| **A · white-box** ↔ LLR | `core` · `full` | `test_arch_osopen_callers` (B0 defect), `test_inc9n`, `test_repair_artifact_claims[store.py]` | RED at the gate (2 failures); after `d5c463d`: **re-run of the two files 219 passed** (transcript header) |
| **B · black-box** AT-065 ↔ painted screen | `core` · `full` | `tests/test_mod_parity.py` (widths 118/87) | 0 painted-line diffs within the gate run |

Gate (`a5b-gate-full-suite.transcript`): **`2 failed, 3003 passed, 24 deselected, 3 xfailed in 1547.26s (0:25:47)`** — cited verbatim, including the failures:

- `FAILED tests/test_inc9n.py::test_inc9n_cr_f8_source_kind_is_public_and_the_badge_reads_it` — the repo-badge pin still read from `app.py` by path after the move.
- `FAILED tests/test_repair_artifact_claims.py::test_every_path_line_citation_resolves[store.py]` — a `store.py` comment cited `app.py` line numbers (already stale before this batch).

Transcript header: "2 failures, both code that pointed at moved code: test_inc9n read the repo badge from app.py by path; store.py comment cited app.py line numbers … Fixed in the next commit (package-wide scan; symbol citations); re-run of the two files: 219 passed." Both fixes are in `d5c463d`, part of this increment.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none unique to this increment — a pure move; the Kimi unit's own RED + sha256 restore lives in its session log (§6); the permanent controls below ran inside the gate |
| Instrument | in-force permanent RED controls: `tests/test_mod_bodies.py` (one-token body mutation / deleted import on a tmp copy → RED) and `tests/test_mod_parity.py` (painted-string mutant → RED) |
| Where it ran | the Kimi unit's isolated worktree (unit-level RED/restore); the orchestrator's gate environment (suite) |
| Transcript | `a5b-gate-full-suite.transcript` (suite); the unit-level RED transcript is not committed — not recorded here |
| Restore proven by | the unit's sha256 restore check (its own log); tmp-copy mutants for the permanent controls |
| Bytecode cache | `python -B`, `-p no:cacheprovider` (gate command verbatim) |
| Arms resolved at baseline | not recorded per arm for this gate |
| Verdict granularity | suite pass/fail per node (2 FAILED node ids named above) |
| Arms that stayed GREEN | not recorded |

| Field | Value |
|---|---|
| **RED counterfactual** | none separate committed beyond the in-force permanent controls — the move adds no new assertion; the gate's own 2 FAILED nodes (named above) are the increment's honest RED evidence, fixed within the increment (`d5c463d`). |

| Field | Value |
|---|---|
| **Mutation verdicts** | No separate mutation battery. In force at this gate: `test_mod_bodies.py` and `test_mod_parity.py` — both GREEN on the shipped tree. Not yet in force: `test_mod_dispatch.py` (B1), the B12 structure/deps/compat/census arms. Per-arm granularity beyond suite pass/fail: not recorded. |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `tests/test_inc9n.py` (repo badge) | badge source moved out of `app.py` | `FAILED …test_inc9n_cr_f8_source_kind_is_public_and_the_badge_reads_it` at this gate |
| `tests/test_repair_artifact_claims.py` | `store.py` comment citing stale `app.py` line numbers | `FAILED …[store.py]` at this gate |
| `tests/test_arch_osopen_callers.py` | B0's defective skip set (reused launcher set) | was already RED at the B0 gate — re-validated GREEN here after the OSOPEN_OWNERS split |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED on a known-bad input (two at this very gate, one at the preceding gate) before its GREEN was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| `mapper/screens/repo.py` + pruned `mapper/app.py` (on-disk AST) | `tests/test_mod_bodies.py` — per-method `ast.dump` against the Inc-0 baseline, exactly-once across the package | passed (within the 3003) |
| the re-export of `RepoScreen` | `from mapper.app import RepoScreen` resolves to the new module's object (suite + `test_app_imports_used.py` in the gate) | passed |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts (moved AST, re-export surface), asserted on disk |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| a5b-gate-full-suite.transcript | .dev-flow/2026-10-09-modular-batch/evidence/a5b-gate-full-suite.transcript | 9a9578a58b485384093557a16900580b271a6adc4734b59cd61ba3648e4c42df |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact, cited with the digest of its stored bytes (from `_facts/evidence-digests.md`) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no census method lost or duplicated by the move" (bodies oracle) |
| If the result is an ABSENCE, what made the search wide enough | every `*.py` under the package root is searched for each baseline key — 0 or ≥2 hits fail |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_mod_bodies.py` docstring: "no method lost or duplicated by a move" |
| Conjunctive criteria: one mutation per conjunct | body mutation and lost-import arms are separate (LLR-MOD.4.3) |
| Synthetic instance of the absent case | the oracle's own tmp-copy mutants |
| **Positive control for every probe that returned an ABSENCE** | the two gate FAILED nodes — the same unmodified probes reported the present (stale) cases |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "from mapper.app import" tests` (premise 2: 68 files) | all still resolve via the re-export — 3003 passed includes every importer |
| B2 file moved on disk | readers of RepoScreen / the repo badge at the old `app.py` path | **fired**: `test_inc9n` (fixed in `d5c463d`); `test_arch_osopen_callers` (B0 stranding) re-validated green |
| B3 byte-identical golden captures this source | `grep mapper/app.py tests/goldens/**` | no golden captures source bytes — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "RepoScreen" mapper tests` | consumed via `mapper/app.py` re-export and by A6's `PlugRepoScreen` (next increment — it imports `RepoScreen` from `screens/repo`, never from `mapper.app`, per LLR-MOD.1.1) |

| A3 | interface consumed by another module changed | `store.py` citation form (line numbers → symbols) | `test_repair_artifact_claims.py` bites on the emitted comment text — RED at the gate, green after `d5c463d` |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run: B2 and A3 fired (both repaired in-increment), B1/B4 re-validated, B3 not fired |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| patch/census pins naming moved code | every test that reads `app.py` by path or cites its line numbers | premise 3's census (17 source-reading files) + the gate's FAILED lines | the 2 that fired | `test_inc9n.py`, `store.py` comments (`d5c463d`) + `test_arch_osopen_callers.py` (`9e87ccd`) | rest already generalised at Inc-0 |

| Field | Value |
|---|---|
| **Correction population** | 1 correction class, enumerated at P0 (premise 3) and re-enumerated by the gate's own FAILED lines |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| repo badge / OSOPEN owners read from `app.py` | 2 stranded readers at the gate (+1 from B0) | yes — 0 surviving stale refs after `9e87ccd` + `d5c463d`; re-run 219 passed | gate transcript FAILED lines; `d5c463d` diff |

### Signed-balance test ledger

`post = base − deleted + added` → per-increment **collected** counts are not recorded (gate transcripts record passed/failed). Executed progression: 2997 passed / 3 failed (A5a+B0) → **3003 passed / 2 failed** (this gate) → 3018 (A6+A7+A4 gate). ⚠ not recorded where the ledger's exact terms are unavailable.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Sonnet, read-only) · group review **A2–A4+B0** · **APPROVE-WITH-NITS, 0 HIGH** · every moved class/function of the pre-batch `app.py` (33 names) byte-identical (AST) in its new module; re-exports complete; every patch repointed to its reader; no back-edges/cycles. 3 MED (vacuous census scans: `test_inc9c:570`, `test_inc9o:338-345`, `test_inc9p:348` + `test_inc9q:387`) → repaired post-review (unit MODREV); 1 LOW carried. |

---

## 5 · Risks

- The two gate failures were **path/citation rot on moved code** — the exact silent-failure mode the batch exists to catch; both were caught by the gate and fixed in-increment. The residual risk is the same class of rot in a file no gate reads — mitigated only at B12 by the mechanical census.
- LLR-MOD.6.2's `screens → app` ban is not test-enforced until B12 (`test_mod_deps.py`).

## 6 · Pending items / spec deviations

- The gate transcript header records the run "at `bc2ff81`"; the failures it lists are those of the A5b move (repo-badge pin, store.py citation), consistent with the gate covering the A5b landing — the counts are cited verbatim and both fixes are in this increment (`d5c463d`).
- The Kimi unit's own RED + sha256 restore log is session scratch, not committed — its content is not recorded here (only its existence, per the facts sheet).
- None else open.

## 7 · Suggested next task

A6: `PlugRepoScreen` → `mapper/screens/plug_repo.py` (it pushes `RepoScreen`, which now lives in `screens/repo.py` — the ARCH-9 ordering reason A5b landed first).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 / 4 |
| 2 | Tests written in this same increment | all | ✓ | `test_arch_osopen_callers` OSOPEN_OWNERS split (`9e87ccd`); `test_inc9n` package scan (`d5c463d`) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | `tests/test_mod_bodies.py` passed in the gate |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | §4 — in-force permanent controls + the gate's own 2 FAILED nodes |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | §4 — 5 probes; B2 and A3 fired and repaired |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b — group review A2–A4+B0, 0 HIGH |
| 7 | No file from another lane touched | all | ✓ | serial spine, one lane |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | re-export surface preserved; F1–F5 freeze respected |
| 9 | Coverage claims verified **on disk** | all | ✓ | gate on the shipped tree: 3003 passed / 2 failed, cited verbatim |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 — bodies-oracle absence + positive controls |
| 11 | **Mutation verdicts** declared | all | ✓ | §4 — bodies + parity in force; later arms named as not-yet |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 3 instruments, each shown RED |
| 13 | **Correction population** declared | all | ✓ | §4 — premise-3 census + gate FAILED lines |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — moved AST + re-export on disk |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` (Claude Sonnet) |
| 16 | **Evidence files** declared | all | ✓ | §4 — 1 file with sha256 |
