# Increment 001a — HLR-RVT.1 · `text.py` + the `model`/`descriptor`/`audit` re-points

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `001a` |
| Lane (if the batch forked) | trunk · `relmap` (data layer) |
| Requirement(s) | `HLR-RVT.1 / LLR-RVT.1.1-.1.3` (PDR `D2`, frozen) |
| Acceptance | `AT-150` (census arm over the 1a paths) · `AT-151` (byte-identity, partial surface — the `structure_lines` surface re-proves at Inc-1b) · white-box `TC-RM` per LLR via `tests/test_relmap_text.py` |
| Agent | `software-dev` (trunk; orchestrator self-executed — no sub-agent delegation for this records+code unit) |
| Date | `2026-10-25` |

---

## 1 · What changed

BLUF: `cut`, `DISPLAY_MAX` and `refusal_line` now live in exactly one leaf,
`mapper/relmap/text.py` (stdlib-only: it imports nothing but `__future__`), and
`model.py`, `descriptor.py`, `audit.py` import them from the leaf. The `audit`
`__all__` re-export of `refusal_line` drops here (LLR-RVT.1.2). Every printed
line the primitives produce is byte-identical to the R1 tree (LLR-RVT.1.3).

Mechanism: the definitions moved verbatim out of `model.py:34,67-71` and
`descriptor.py:211-216`; `refusal_line`'s K5 match is by the fixed cause text
(`K5_CAUSE` in the leaf), not by importing `descriptor.CAUSE` — the leaf may not
import the package (that would be a cycle and would break the ARCHITECTURE
`relmap` row's `text` leaf commitment). Mid-move state, per the orchestrator
ruling at the PDR seal (COND-ARCH-2/COND-QA-1, `LED-2026-10-25-r2.16`):
`adapter.py:29` is the one remaining old-path reader and is unimportable on
purpose until Inc-1b re-points it — declared, and the Inc-1a test/probe surfaces
that route through `mapper.relmap.audit` (`test_relmap_audit.py`,
`test_relmap_adapter.py`, the probe's `structure_lines` section) re-run green at
the Inc-1b gate.

## 2 · Files modified

**The budget counts SOURCE files only.** One row per file.

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/relmap/text.py` | source | HLR-RVT.1 · LLR-RVT.1.1-.1.3 | NEW leaf: `DISPLAY_MAX`, `cut`, `refusal_line`, `K5_CAUSE`; stdlib-only |
| `mapper/relmap/model.py` | source | HLR-RVT.1 · LLR-RVT.1.1 | `DISPLAY_MAX` and `def cut` removed (moved to the leaf) |
| `mapper/relmap/descriptor.py` | source | HLR-RVT.1 · LLR-RVT.1.1/.1.2 | imports `cut` from the leaf; `def refusal_line` removed; docstring re-pointed |
| `mapper/relmap/audit.py` | source | HLR-RVT.1 · LLR-RVT.1.1/.1.2 | imports `cut`/`refusal_line` from the leaf; `refusal_line` dropped from `__all__`; docstring re-pointed |
| `tests/test_relmap_text.py` | test | LLR-RVT.1.1-.1.3 | NEW: AST census (one site/one path), `__all__` arm, R1 behaviour pins, planted-violation arms |
| `tests/test_relmap_model.py` | test | LLR-RVT.1.3 | re-pointed import lines 17-26 (`DISPLAY_MAX`, `cut` from the leaf); no assertion change |
| `tests/test_relmap_descriptor.py` | test | LLR-RVT.1.2/.1.3 | re-pointed import line 38 (`refusal_line` from the leaf); hygiene census `mine` set gains this file's new sibling; docstring |
| `tests/test_relmap_audit.py` | test | LLR-RVT.1.2 | re-pointed import line 34 (`refusal_line` from the leaf); docstring; **uncollectible mid-move — green at Inc-1b** |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc1a-*.txt` | generated | — | six transcripts (RED ×2, GREEN ×2, byte-identity, mutants) |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** |
| Test files | 4 touched + 1 new (uncapped) |
| Doc files | 0 |

- ⚠ At exactly 4 source files: the split itself is the smallest cut — the
  orchestrator ruling at the PDR seal (COND-ARCH-2/COND-QA-1) divided the
  five-file move into 4 + 1 so each increment stays ≤ 4; the leaf and the three
  1a re-points cannot be separated without leaving the tree with two definition
  sites or an importable-but-lying census.

## 3 · How to test

```bash
# prove the import resolves in the worktree first
PYTHONPATH=<worktree> python -c "import mapper; print(mapper.__file__)"
# targeted (Inc-1a):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_relmap_text.py tests/test_relmap_model.py tests/test_relmap_descriptor.py
# guard set (Inc-1a run excludes test_relmap_audit.py + test_relmap_adapter.py:
# uncollectible mid-move, declared; they re-run at the Inc-1b gate):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_fold.py tests/test_repair_artifact_claims.py tests/test_no_operator_paths.py \
  tests/test_mod_bodies.py tests/test_mod_census.py tests/test_mod_compat.py tests/test_mod_deps.py \
  tests/test_mod_dispatch.py tests/test_mod_parity.py tests/test_mod_structure.py \
  tests/test_repair_map_truth.py tests/test_a3_census.py tests/test_arch_osopen_callers.py \
  tests/test_relmap_gaps.py tests/test_relmap_isolation.py tests/test_relmap_model.py \
  tests/test_relmap_profile.py tests/test_relmap_text.py tests/test_relmap_descriptor.py \
  tests/test_prescan_refusal_goldens.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `full` | `cut` boundary paths (119/120/121/1M), `refusal_line` K5-with/without-limit — pinned inside `tests/test_relmap_text.py` and the re-pointed R1 files | 13 + 155 passed (targeted) |
| **A · white-box** `TC` ↔ LLR | `full` | `test_one_definition_site_per_primitive`, `test_no_old_path_readers_inc_1a`, `test_no_dotted_old_path_references_inc_1a`, `test_audit_all_drops_the_refusal_line_reexport` (+ planted-violation arms) | passed (in the 13) |
| **B · black-box** `AT` ↔ story | `full` | AT-150 census arm over the 1a paths (in the 13); AT-151 partial surface via the byte-identity probe; the `structure_lines` surface + `test_relmap_audit.py` re-prove at Inc-1b | probe live sections byte-identical |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (1) code-absent: `tests/test_relmap_text.py` present, `mapper/relmap/text.py` not yet written; (2) move-aside (C-20): the landed `text.py` renamed out of the tree |
| Instrument | project code, orchestrator's hand (no stash; C-20 move-aside) |
| Where it ran | this worktree, orchestrator (no other session reading) |
| Transcript | `evidence/p3-inc1a-red-code-absent.txt` — `ModuleNotFoundError: No module named 'mapper.relmap.text'`, exit 2; `evidence/p3-inc1a-red-move-aside.txt` — same at collection, exit 2 |
| Restore proven by | move-aside restore sha256 `88c8176984fb5d149d2b418994ca3dcff460e3f730f2fa8d1400a065c2682cc2` → `88c81769…cc2` (MATCH) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` in every run (C-46) |
| Arms resolved at baseline | 2 RED arms, both seen failing |
| Verdict granularity | per resolved node id — `tests/test_relmap_text.py` collection error in both |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | code-absent + move-aside, both transcripts at `evidence/p3-inc1a-red-code-absent.txt` (sha256 `76739b0c…7872b`) and `evidence/p3-inc1a-red-move-aside.txt` (sha256 `5e1e26e0…37dcb`) |

| Field | Value |
|---|---|
| **Mutation verdicts** | M-RVT-1 — second `def cut` planted in `model.py` → `test_one_definition_site_per_primitive[cut]` RED (KILLED), restore sha256 `f49ca449…ed40a` · M-RVT-2 — `tests/test_relmap_descriptor.py` reverted to import `refusal_line` from `mapper.relmap.descriptor` → `test_no_old_path_readers_inc_1a` RED (KILLED), restore sha256 `7b8e03a6…579c9` · M-RVT-3 — the moved `cut` drops the ellipsis (`text[: DISPLAY_MAX]`) → `test_cut_reproduces_the_r1_contract` RED (KILLED), restore sha256 `88c81769…cc2` · arms that stayed GREEN: none · transcript `evidence/p3-inc1a-mutants.txt` (sha256 `c8fa6799…f32a`), runner exit 0 |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` (targeted/guard) | the two RED states above | collection error, exit 2, transcripts |
| the AST census arms | planted second `def cut` / planted old-path import string | `test_definition_census_finds_a_second_site` / `test_reader_census_finds_a_planted_old_path_reader` fail by construction (in the GREEN run's 13) |
| the byte-identity probe | M-RVT-3 mutant run through the probe would change the dump hash | probe hash is content-derived: any wording change moves `PROBE-SHA256` (M-RVT-3 kills the asserting test arm directly) |
| the mutation runner | its own `BAD` controls (anchor-not-found / edit-did-not-apply / restore-mismatch) | each arm prints `BAD` and the battery exits 1 — 0 bad arms in the run |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED or BAD-able before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the probe's canonical dump (every `cut`/`refusal_line` line + the descriptor refusal over a K2 fixture) | run on the base worktree and on the Inc-1a tree; the live sections diffed | BYTE-IDENTICAL; base full-surface sha256 `b7ff2e38…5a07` (the `structure_lines` section is `AUDIT-SURFACE-SKIPPED` mid-move and must reappear unchanged at Inc-1b) |
| the R1 prescan-refusal goldens | `tests/test_prescan_refusal_goldens.py` in the guard run | passed unchanged |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted on its emitted bytes |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED code-absent transcript | `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc1a-red-code-absent.txt` | `76739b0c954675c3a21f3a7f840d07d1d0f44cb0157b47a5130444ec1d57872b` |
| RED move-aside transcript | `…/evidence/p3-inc1a-red-move-aside.txt` | `5e1e26e0e8e5a1a820e8d3bbd9c3375e2c4916c694831c4a799de77890837dcb` |
| GREEN targeted transcript | `…/evidence/p3-inc1a-green-targeted.txt` | `cbb45fd8aef78823a05727b5e662867078555862e3b6954f0ca667bc6ec767f5` |
| GREEN guard transcript | `…/evidence/p3-inc1a-green-guards.txt` | `755625d5a0dd6fbccb88f5272672891040478827d57e90b9ea79b2a7885e1178` |
| byte-identity probe dumps | `…/evidence/p3-inc1a-byteid.txt` | `2020147581d9fce88863339b041026911c4374f1564f46992f2ba18bf57530b6` |
| mutation battery transcript | `…/evidence/p3-inc1a-mutants.txt` | `c8fa6799de131f27128d1e7dbeec26f25e472f2a3849a1d9c0aff31b5ffaf32a` |

All transcripts redacted (account name → `<user>`) before hashing; exit codes and wall time in each header.

| Field | Value |
|---|---|
| **Evidence files** | 6 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — the census claims zero old-path readers (`relmap.model.DISPLAY_MAX`, `relmap.descriptor.refusal_line`, `relmap.audit.refusal_line`) |
| If the result is an ABSENCE, what made the search wide enough | the census walks `mapper/**` and `tests/test_*.py` ASTs (import statements) plus a dotted-reference regex over the `relmap` package — not a hand-listed file set; `tests/test_relmap_isolation.py` walks the same package for the import-surface rules |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `tests/test_relmap_text.py::test_no_old_path_readers_inc_1a` / `test_no_dotted_old_path_references_inc_1a` — censuses, not behaviour |
| Conjunctive criteria: one mutation per conjunct | M-RVT-2 kills the import-statement conjunct; a planted attribute-form reader is covered by the dotted census conjunct (same battery pattern, planted arm `test_reader_census_finds_a_planted_old_path_reader`) |
| Synthetic instance of the absent case | the planted-violation arms synthesise the forbidden case in a string and assert the census reports it |
| **Positive control for every probe that returned an ABSENCE** | the planted arms ARE the positive controls: the same unmodified census function returns the planted hit (`_definitions_in` finds the planted `def cut`; `_old_path_readers_in` finds the planted import) — printed in the GREEN transcript |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rl "refusal_line\|DISPLAY_MAX\|\bcut(" tests/ --include="*.py"` | 5 files: the 4 relmap suites (this increment's) + `test_reqharness_release.py` — which only names the words in test NAMES over the `--audit` subprocess (no symbol import); re-runs at Inc-1b |
| B2 file moved on disk | `git grep` over the old definition sites | no FILE moves; the §E-10 symbol move — old `def cut`/`DISPLAY_MAX` gone from `model.py`, old `def refusal_line` gone from `descriptor.py` (proven by the definition census) |
| B3 byte-identical golden captures this source | `grep -rl "relmap\|refusal_line\|DISPLAY_MAX" tests/goldens/` | no hits — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "structure_lines" mapper/ \| grep -v relmap/audit.py` | one consumer: `mapper/app.py:353` (the `--audit` CLI wiring) — unchanged surface |
| A3 interface consumed by another module changed | `grep -rn "from mapper.relmap.model import.*\(cut\|DISPLAY_MAX\)…"` over `mapper/ tests/` | one live hit: `mapper/relmap/adapter.py:29` — the declared Inc-1b reader; plus this file's own planted-violation string (synthetic instance, declared) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3); B3 not fired; A3's one hit is the declared Inc-1b reader |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — no correction in this increment |

### Signed-balance test ledger

`post = base − deleted + added` → touched files: `53 = 53 − 0 + 0` (model) · `90 = 90 − 0 + 0` (descriptor) · `49 = 49 − 0 + 0` (audit) ✓ reconciles; NEW file `test_relmap_text.py`: +13 (base 0). Guard-set totals: baseline `744 passed, 2 skipped, 3 xfailed` → Inc-1a guard run `672 passed, 1 skipped, 3 xfailed` with the two uncollectible relmap files deferred to Inc-1b (mid-move, declared).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | code-reviewer — Kimi K2.8 session executing `agents/code-reviewer.md` + `agents/security-reviewer.md` · **approve-with-nits** |
| Review evidence | `evidence/review-inc001ab.md` · sha256 `ba2506d5104baba16d76bde7c2c00bf8bf195759492823dda85cb3504272ca06` |
| Follow-ups disposition | N-1 **fixed**: `assert K5_CAUSE == CAUSE["K5"]` added to `test_refusal_line_reproduces_the_r1_contract` — R-1-style reword mutant shown RED at the drift site, restore sha256 MATCH `88c81769…cc2`, GREEN · N-2 **fixed (widen chosen)**: definition census `_relmap_sources` now walks all of `mapper/**` (`PKG.rglob`), expected site `relmap/text.py`, `test_relmap_text.py` 15 nodes GREEN · OBS-1 **verified**: Inc-2's census repair extended the descriptor fence `mine` set (`tests/test_relmap_descriptor.py:739` names `test_relmap_shell.py`); suite green (89 passed, 1 skipped) — concurrent-session artifact, not an Inc-1 defect |

## 5 · Risks

- Mid-move by design: `mapper --audit`'s structure surface and `test_relmap_audit.py` /
  `test_relmap_adapter.py` are uncollectible until Inc-1b lands the `adapter.py` re-point.
  If Inc-1b is delayed, trunk sits with a broken audit import — the trunk order of merit
  (1a → 1b immediately) is the mitigation, and no lane forks before Inc-2 anyway (F-1/F-2).
- The K5 literal (`K5_CAUSE`) in the leaf duplicates the `CAUSE["K5"]` value: a future edit
  to the cause table that rewords K5 without touching the leaf would silently break the
  limit rendering. Guard: the R1 refusal tests (`test_refusal_line_form_and_k5_rendering`,
  the probe's `k5-limit` arm) pin the rendered bytes; B-151 (one K5 renderer) is the
  carried cure.

## 6 · Pending items / spec deviations

- Inc-1b owes: the `adapter.py` re-point, the `relmap.model.cut` census arm, the
  full-surface byte-identity proof (base hash `b7ff2e38…5a07` must reappear), the GREEN
  re-run of `test_relmap_audit.py` / `test_relmap_adapter.py` / `test_reqharness_release.py`.
- Contract issues: none — LLR-RVT.1.1/.1.2 already name the two-increment split
  (`LED-2026-10-25-r2.16`); the plan and the §2.1/§5.1 rows read consistently with it.

## 7 · Suggested next task

Trunk Inc-1b — the `adapter.py` re-point (1 SOURCE), completing the one-path census (F-1).

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 4/4 — §2 count row + the why at the ⚠ |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_relmap_text.py` (13 nodes) + re-pointed R1 imports |
| 3 | Layer 0 written where the criterion applies | `full` | ✓ | `test_cut_reproduces_the_r1_contract`, `test_refusal_line_reproduces_the_r1_contract` — boundary (presentation) + ≥3 paths |
| 4 | RED counterfactual declared | all | ✓ | code-absent + move-aside transcripts, exit 2 both, restore sha256 MATCH |
| 5 | Reverse census declared | all | ✓ | §Reverse census — 5 probes, B3 not fired, A3's hit is the declared Inc-1b reader |
| 6 | `code-reviewer` passed | all | ✓ | §4b — approve-with-nits; review `evidence/review-inc001ab.md` sha256 `ba2506d5…ca06` |
| 7 | No file from another lane touched | all | ✓ | trunk increment; all touched files are trunk file-set rows (proposal §2.1 Inc-1a) |
| 8 | Frozen interfaces untouched | all | ✓ | D2 IS this increment; D1/D3/D4/D5 untouched |
| 9 | Coverage claims verified on disk | all | ✓ | every cited test id collected on disk (155 passed targeted) |
| 10 | Load-bearing emptiness declared | all | ✓ | §Load-bearing emptiness — census absence + planted positive controls |
| 11 | Mutation verdicts declared | all | ✓ | M-RVT-1/2/3 all KILLED, per-arm, restore digests cited |
| 12 | Instrument RED-proof declared | all | ✓ | 4 instruments, each RED/BAD-able first |
| 13 | Correction population declared | all | ✓ | none |
| 14 | Emitted-form assertion declared | all | ✓ | probe dumps diffed byte-for-byte; goldens green |
| 15 | Independent review names somebody | all | ✓ | code-reviewer — Kimi K2.8 session · `evidence/review-inc001ab.md` sha256 `ba2506d5…ca06` |
| 16 | Evidence files declared | all | ✓ | 6 files at `artifact_homes.evidence`, digests of stored bytes |
