# Increment 001b — HLR-RVT.1 · the `adapter.py` re-point (text leaf, second half)

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `001b` |
| Lane (if the batch forked) | trunk · `relmap` (data layer) |
| Requirement(s) | `HLR-RVT.1 / LLR-RVT.1.1-.1.3` (PDR `D2`, frozen) |
| Acceptance | `AT-150` (census now zero over ALL old paths) · `AT-151` (full-surface byte-identity, hash `b7ff2e38…5a07` re-proven) · white-box `TC` via `tests/test_relmap_text.py` |
| Agent | `software-dev` (trunk; orchestrator self-executed — no sub-agent delegation for this records+code unit) |
| Date | `2026-10-25` |

---

## 1 · What changed

BLUF: `mapper/relmap/adapter.py:29` now imports `cut` from the leaf
(`mapper/relmap/text.py`) instead of `mapper.relmap.model`. The reader census
over `relmap.model.cut` — the one old-path reader declared at Inc-1a — is zero.
The presentation primitives now have one definition site and one import path
across the whole package; the full probe surface (including `structure_lines`)
is byte-identical to the base tree (hash `b7ff2e38…5a07`).

This increment is one SOURCE file; its tests are two census arms added to the
Inc-1a test file (`tests` are uncapped; no new test file).

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/relmap/adapter.py` | source | HLR-RVT.1 · LLR-RVT.1.1/.1.2 | `cut` re-pointed from `mapper.relmap.model` to the `text` leaf (one import line) |
| `tests/test_relmap_text.py` | test | LLR-RVT.1.2 | +2 arms: `test_no_old_path_readers_inc_1b` (census zero over `relmap.model.cut`), `test_audit_and_adapter_import_the_leaf_for_own_use` (runtime identity + old attribute path gone) |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc1b-*.txt` | generated | — | seven transcripts (RED ×2, GREEN ×3, byte-identity, mutants) |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** |
| Test files | 1 (arms added; uncapped) |
| Doc files | 0 |

## 3 · How to test

```bash
PYTHONPATH=<worktree> python -c "import mapper; print(mapper.__file__)"
# targeted:
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_relmap_text.py tests/test_relmap_adapter.py tests/test_relmap_audit.py
# full guard set (as the commission lists it, tests/test_relmap_*.py included):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_fold.py tests/test_repair_artifact_claims.py tests/test_no_operator_paths.py \
  tests/test_mod_bodies.py tests/test_mod_census.py tests/test_mod_compat.py tests/test_mod_deps.py \
  tests/test_mod_dispatch.py tests/test_mod_parity.py tests/test_mod_structure.py \
  tests/test_repair_map_truth.py tests/test_a3_census.py tests/test_arch_osopen_callers.py \
  tests/test_relmap_adapter.py tests/test_relmap_audit.py tests/test_relmap_descriptor.py \
  tests/test_relmap_gaps.py tests/test_relmap_isolation.py tests/test_relmap_model.py \
  tests/test_relmap_profile.py tests/test_relmap_text.py tests/test_prescan_refusal_goldens.py
# the R1 audit-surface suite deferred mid-move:
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider tests/test_reqharness_release.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `full` | the R1 behaviour pins re-run (in the 15) | 15 + 103 passed (targeted, incl. adapter + audit suites) |
| **A · white-box** `TC` ↔ LLR | `full` | `test_no_old_path_readers_inc_1b`, `test_audit_and_adapter_import_the_leaf_for_own_use` | passed |
| **B · black-box** `AT` ↔ story | `full` | AT-150 full census (1/1/1, zero old paths); AT-151 byte-identity over the shipped `--audit` surface (`structure_lines` in the probe + `test_reqharness_release.py`'s refusal-line CLI arms) | full-surface hash equals the base hash |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (1) census-before-code: the two Inc-1b arms run while `adapter.py:29` still imports `cut` from `mapper.relmap.model`; (2) move-aside (C-20): the landed `adapter.py` renamed out of the tree |
| Instrument | project code, orchestrator's hand (no stash; C-20 move-aside) |
| Where it ran | this worktree, orchestrator (no other session reading) |
| Transcript | `evidence/p3-inc1b-red-census.txt` — 2 failed (the old-path reader + the leaf-identity arm), exit 1; `evidence/p3-inc1b-red-move-aside.txt` — collection error, exit 2 |
| Restore proven by | move-aside restore sha256 `e163a9fa14cd245dc5fbafff301148120988829e20f703621052cdab69936756` → `e163a9fa…36756` (MATCH) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` in every run (C-46) |
| Arms resolved at baseline | 2 RED arms, both seen failing |
| Verdict granularity | per node id — `test_no_old_path_readers_inc_1b`, `test_audit_and_adapter_import_the_leaf_for_own_use`; move-aside: collection error |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | census-before-code + move-aside, transcripts at `evidence/p3-inc1b-red-census.txt` (sha256 `7cf30dee…b2ec`) and `evidence/p3-inc1b-red-move-aside.txt` (sha256 `4220b6c7…c550`) |

| Field | Value |
|---|---|
| **Mutation verdicts** | M-RVT-2 — `adapter.py` reverted to import `cut` from `mapper.relmap.model` → `test_no_old_path_readers_inc_1b` RED (KILLED), restore sha256 `e163a9fa…36756` · M-RVT-3 — the moved `cut` drops the ellipsis → `test_cut_reproduces_the_r1_contract` RED (KILLED), restore sha256 `88c81769…cc2` · arms that stayed GREEN: none · transcript `evidence/p3-inc1b-mutants.txt` (sha256 `17b3f962…f2d8`), runner exit 0 |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` | the two RED states above | exit 1 (2 failed) and exit 2 (collection error), transcripts |
| the Inc-1b census arm | the pre-re-point adapter (its genuine state at the Inc-1b entry) | `mapper/relmap/adapter.py:29 mapper.relmap.model.cut` — printed in the RED transcript |
| the byte-identity probe | n/a this increment (no emitted byte changed; the probe hash is the same instrument that pinned the base) | the probe would print a different `PROBE-SHA256` on any wording drift |
| the mutation runner | its own `BAD` controls | none fired; battery exit 0 |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments (2 exercised this increment, 2 carried green with controls intact) |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the probe's canonical dump (full surface incl. `structure_lines`) | run on the base worktree and on the Inc-1b tree; sha256 of both dumps | base `b7ff2e38aeb79a0629bcf36bc09cc7c231fa25110fe32d59b14991575d2d5a07` == inc1b `b7ff2e38…5a07`; dumps diff-empty | 
| the R1 `--audit` refusal surface | `tests/test_reqharness_release.py` (14 nodes, incl. `test_audit_cli_refusal_line_has_one_prefix`) | 14 passed |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted on its emitted bytes |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED census-before-code transcript | `…/evidence/p3-inc1b-red-census.txt` | `7cf30dee2c99515284ce8ec8adbde6917741680a963b58b7de508108c06eb2ec` |
| RED move-aside transcript | `…/evidence/p3-inc1b-red-move-aside.txt` | `4220b6c7ffe901a04aa942bc6529e24ce49f946a03875ef1173bf1bbee02c550` |
| GREEN targeted transcript | `…/evidence/p3-inc1b-green-targeted.txt` | `2bf9f16a41803722be2915eb65388d2ea4a0880d2a2171a22193562339787c38` |
| GREEN guard transcript | `…/evidence/p3-inc1b-green-guards.txt` | `32565d1c689e0b571268465098c72b76cc844de7952b3956b341d7a6072b390f` |
| GREEN reqharness-release transcript | `…/evidence/p3-inc1b-green-reqrelease.txt` | `11dc0bf0ce1d6661d8971876dba8c61d89b79fa2a5a4525b28272b6592f2809f` |
| byte-identity probe dumps | `…/evidence/p3-inc1b-byteid.txt` | `b0d060ad7705f798c382ae39100f69eb28e0ec423699528a0955f9fc4f384d95` |
| mutation battery transcript | `…/evidence/p3-inc1b-mutants.txt` | `17b3f962204880afa2112f276173353de2969822355b3703bbe14a65006f02d8` |

All transcripts redacted (account name → `<user>`) before hashing; exit codes and wall time in each header.

| Field | Value |
|---|---|
| **Evidence files** | 7 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — zero readers of `relmap.model.cut` |
| If the result is an ABSENCE, what made the search wide enough | the same AST import census as Inc-1a, over `mapper/**` + `tests/test_*.py` — the widest reader search the tree admits |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_no_old_path_readers_inc_1b` — a census, not a behaviour |
| Conjunctive criteria: one mutation per conjunct | M-RVT-2 kills the import-statement conjunct; the identity arm (`test_audit_and_adapter_import_the_leaf_for_own_use`) covers the runtime-object conjunct (`hasattr(model, "cut")` is False) |
| Synthetic instance of the absent case | M-RVT-2 IS the synthetic instance: the same unmodified census flags the reverted adapter (printed in the mutant transcript) |
| **Positive control for every probe that returned an ABSENCE** | the Inc-1b RED transcript: the census printed `mapper/relmap/adapter.py:29 mapper.relmap.model.cut` when the reader genuinely existed — the probe's non-absent output on the known-present case |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rl "refusal_line\|DISPLAY_MAX\|\bcut(" tests/ --include="*.py"` | same 5 files as Inc-1a; none imports the old paths (the import census proves it) |
| B2 file moved on disk | `git grep` over the old import line | the old `from mapper.relmap.model import …, cut` is gone from `adapter.py` (census zero) |
| B3 byte-identical golden captures this source | `grep -rl "relmap\|refusal_line\|DISPLAY_MAX" tests/goldens/` | no hits — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "structure_lines" mapper/ \| grep -v relmap/audit.py` | one consumer: `mapper/app.py:353` — green in the guard run |
| A3 interface consumed by another module changed | old-path import grep over `mapper/ tests/` | zero hits (the planted-violation string inside `test_relmap_text.py` is the synthetic control, declared) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3); B3 not fired; A3 zero |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — no correction in this increment |

### Signed-balance test ledger

`post = base − deleted + added` → adapter suite `40 = 40 − 0 + 0` · audit `49 = 49 − 0 + 0` · `test_relmap_text.py` `15 = 13 − 0 + 2` ✓ reconciles. Guard-set totals: `762 passed, 2 skipped, 3 xfailed` (wall 157s) vs the pre-move baseline `744 passed, 2 skipped, 3 xfailed` — Δ +18 = +15 (`test_relmap_text.py`) + 1 (`test_relmap_isolation.py` is parametrized over the package file set, which now includes `text.py`) + 2 (`test_repair_artifact_claims.py` parametrizes its citation checkers over the batch corpus + `mapper/` source, which now include `increment-001a.md` and `text.py`); every touched R1 file reconciles node-for-node (model 53, descriptor 90, audit 49, adapter 40 — base and current counts compared per file on both trees).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | code-reviewer — Kimi K2.8 session executing `agents/code-reviewer.md` + `agents/security-reviewer.md` · **approve-with-nits** |
| Review evidence | `evidence/review-inc001ab.md` · sha256 `ba2506d5104baba16d76bde7c2c00bf8bf195759492823dda85cb3504272ca06` |
| Follow-ups disposition | N-1 **fixed**: `assert K5_CAUSE == CAUSE["K5"]` added to `test_refusal_line_reproduces_the_r1_contract` — R-1-style reword mutant shown RED at the drift site, restore sha256 MATCH `88c81769…cc2`, GREEN · N-2 **fixed (widen chosen)**: definition census `_relmap_sources` now walks all of `mapper/**` (`PKG.rglob`), expected site `relmap/text.py`, `test_relmap_text.py` 15 nodes GREEN · OBS-1 **verified**: Inc-2's census repair extended the descriptor fence `mine` set (`tests/test_relmap_descriptor.py:739` names `test_relmap_shell.py`); suite green (89 passed, 1 skipped) — concurrent-session artifact, not an Inc-1 defect |

## 5 · Risks

- None new: the trunk text-leaf move is complete (F-1's census half is green;
  F-1 also wants the R1 suite green — it is, here and at Inc-1a for its files).
- The carried K5-literal risk from Inc-1a stands (B-151 is the cure).

## 6 · Pending items / spec deviations

- None. COND-ARCH-2/COND-QA-1 are discharged by Inc-1a + this increment
  (one re-read closes both, per the PDR record).
- Contract issues: none.

## 7 · Suggested next task

Trunk Inc-2 — the screen host (`screens/relmap/{__init__,screen,base}.py` +
`mapper/keymap.py`, 4 SOURCE), which freezes nothing further (D1 is sealed) but
lands the host↔renderer surface and the `SCOPE_RELMAP` seat.

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1/4 |
| 2 | Tests written in this same increment | all | ✓ | 2 census arms added and run RED-before-GREEN |
| 3 | Layer 0 written where the criterion applies | `full` | ✓ | carried from Inc-1a; re-run green |
| 4 | RED counterfactual declared | all | ✓ | census-before-code (exit 1) + move-aside (exit 2), restore sha256 MATCH |
| 5 | Reverse census declared | all | ✓ | §Reverse census — 5 probes, B3 not fired, A3 zero |
| 6 | `code-reviewer` passed | all | ✓ | §4b — approve-with-nits; review `evidence/review-inc001ab.md` sha256 `ba2506d5…ca06` |
| 7 | No file from another lane touched | all | ✓ | trunk increment; adapter is the Inc-1b row of proposal §2.1 |
| 8 | Frozen interfaces untouched | all | ✓ | D2 completed exactly as amended by the ruling; D1/D3/D4/D5 untouched |
| 9 | Coverage claims verified on disk | all | ✓ | 15 nodes collected on disk; 103 passed targeted |
| 10 | Load-bearing emptiness declared | all | ✓ | §Load-bearing emptiness — positive control = the Inc-1b RED transcript |
| 11 | Mutation verdicts declared | all | ✓ | M-RVT-2, M-RVT-3 KILLED, per-arm, restore digests cited |
| 12 | Instrument RED-proof declared | all | ✓ | pytest + census exercised RED this increment |
| 13 | Correction population declared | all | ✓ | none |
| 14 | Emitted-form assertion declared | all | ✓ | full-surface hash equality + `--audit` CLI suite green |
| 15 | Independent review names somebody | all | ✓ | code-reviewer — Kimi K2.8 session · `evidence/review-inc001ab.md` sha256 `ba2506d5…ca06` |
| 16 | Evidence files declared | all | ✓ | 7 files at `artifact_homes.evidence`, digests of stored bytes |
