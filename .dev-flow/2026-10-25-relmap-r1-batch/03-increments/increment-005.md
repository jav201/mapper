# Increment 005 — US-RM-003 · `The structure block of mapper --audit, the injected hook, and the Layer B acceptance nodes`

> **Artifact language.** English (the batch language). **Owed in.** `core` ✓ · `full` ✓
> Where this lives: the repo, `.dev-flow/2026-10-25-relmap-r1-batch/03-increments/increment-005.md`. Written by the
> `software-dev` author in the batch worktree on branch `feat/relmap-r1` (base `ab412fc`, Inc-1..4 in); the transcripts it
> cites are under `.dev-flow/2026-10-25-relmap-r1-batch/evidence/`, redacted of the account name (`<user>`) before hashing.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r1-batch` |
| Increment | `005` (the last) |
| Lane (if the batch forked) | none — one chain · modules `relmap`, `reqharness` (`audit.py` only), `app` |
| Requirement(s) | US-RM-003 · HLR-RMU.1 · LLR-RMU.1.1–.1.4 · AT-117…AT-122, AT-124…AT-129 · TC-RM-02, TC-RM-03 · ledger `.29`, `.30`, `.35`, `.38`, `.40`–`.44`, `.56` and the new `.58`–`.64` · PDR conditions X-1, N-3, D-4, D-5, D-9, PD-7, C2, M4, M5, MAJOR-1…4, MINOR-1…3 |
| Acceptance | Layer B: the twelve ATs as real `mapper --audit` subprocess nodes in `tests/test_relmap_audit.py` · Layer A: TC-RM-02, TC-RM-03, `test_hook_line_bound`, `test_format_structure_cuts_inside`, `test_refusal_line_hostile_name`, `test_canon_derived_once` |
| Agent | `software-dev` |
| Date | 2026-10-25 |

---

## 0 · Rulings recorded first (Inc-4 packet §6) and the review follow-ups

The orchestrator's seven rulings are ledger entries `.58`–`.64` plus contract text in `01-requirements.md`, written BEFORE any Inc-5 code: (1) `.58` `Derivation.reported` holds the printed note text (LLR-RMA.1.3 reworded); (2) `.59` the "configured, not derivable in R1" statement is carried by the audit's sources line, the adapter emits no such note (LLR-RMA.1.4 and the note order of LLR-RMU.1.2 amended); (3) `.60` only `LLR-` ids count toward `Node.unparsed`, a reported HLR row is a note only; (4) `.61` `unknown_status` counts kept nodes only; (5) `.62` `RelMapLimitError` propagates out of the adapter and `structure_lines` turns it into `structure: unavailable (canon: over the node or edge limit)`; (6) `.63` AT-117/119/124/125 cleared `V2` at Inc-4 only through Layer A names — their real Layer B nodes are minted here; (7) `.64` the double `build_map` is accepted, a watch-item for R2. The "Ledger:" line of each touched LLR/HLR names its new entries (`V26` both ways).

The Inc-4 independent review (`evidence/review-inc004.md`, approve-with-nits) is committed with this work. **F1** closed: `test_unparsed_count_of_a_dotless_hlr_is_not_doubled`; reviewer mutant C (`if "." in s:` → `if True:`) re-run for real, RED on that node alone, restore hash-equal (`evidence/inc4f-red-f1-mutant-c.txt`). **F4** closed: the ledger heading is asserted present before it is indexed. **F2** discharged here (`test_reported_note_with_bidi_is_cut_and_escaped`, a U+202E inside a reported row's id: cut to 120, escaped by the sink; M-RMU-5/-11 and M-RMA-3' kill it). **F3** discharged here (`test_canon_over_the_node_cap_is_one_fixed_line`, a real 100,001-row canon; M-RMU-15). `increment-004.md` has its Independent review cell filled.

---

## 1 · What changed

**`mapper/relmap/audit.py`** (NEW): `format_structure(relmap, gaps, notes, refusals, *, label, sources, unknown_status, reach_not_computed, unlinked, ignored)` — the pure formatter and tested seam; it performs the 120-character cut ITSELF on every repository-derived value (ids, label, sources, notes, unlinked ids, ignored keys; the gap sentence has a 400-character safety cap because it carries the qualifier). It returns exactly the given refusal lines when `refusals` is non-empty, else, in contract order: label · summary (`profile=… nodes=N (HLR=…) edges=E (…) cycles=C`, kinds and edge types in PROFILE order, zero counts omitted, a zero total without parentheses) · sources · gap total (`HIGH/MED/LOW` always) · at most 20 gap rows + `structure: gaps shown X of Y (Z lowest-ranked not shown)` · the skipped-rows line (parts only when > 0) · at most 10 notes + `structure: notes shown 10 of Y (Z not shown)`. `structure_lines(repo)` (D5, UNESCAPED): header first, then the canon map derived ONCE (`derive_reqharness_map`, default descriptor), gaps detected and ranked ONCE (`limit=20`), then per descriptor in name order a block (`label` = base name, or `(built-in default)` when none exists) or the `refusal_line` imported from `relmap.descriptor` (ledger `.56`), then `structure: refused: more descriptors than the limit (8)`. `CanonUnavailable` → `structure: unavailable (canon: <K1–K7>)` (K5 rendered `exceeds the <N> byte limit`); `RelMapLimitError` → the fixed `LIMIT_LINE` (ledger `.62`).

**`mapper/reqharness/audit.py`**: `run_cli(argv, extra_lines=None)` (D4). `None` is byte-identical to before (`test_run_cli_without_the_hook_is_byte_identical` against the base-captured prefix). With a hook: after the existing report, no-repo / no-registry reports print ONE fixed line each, keyed on `report.chain_status` (never the verdict text) with the hook NOT called; any other report prints the lines of ONE call of `extra_lines(Path(report.repo))`, at most 1,000 consumed (`itertools.islice`; a 1,001st is not consumed past and `structure: output truncated at 1000 lines` follows), each through the existing `_visible` escaper; a raising hook prints `structure: unavailable (internal error: <Type>)`. The exit code expression is unchanged; when `audit()` raises (the `--baseline` refusal) no hook call and no structure line. `reqharness` imports nothing from `relmap`.

**`mapper/app.py`**: the `--audit` branch passes `relmap.audit.structure_lines` as `extra_lines` (2 lines; the file is 361 lines, `test_mod_structure` cap 400).

**Verdict by prefix (UX MAJOR-4), documented:** the `verdict: ` line is no longer the last line of the output; a CI step that read the last line must read `grep '^verdict: '`. The first block line says on screen that the block is informational (MAJOR-1). Written into the ARCHITECTURE `relmap` row (see §4 *Correction population*).

**Real block on the repository's own canon** (a tmp repo seeded with a registry, `REQUIREMENTS.md` = this worktree's; `mapper --audit <repo>`; the worktree itself has no `reqharness/` registry, so `--audit .` prints only `structure: unavailable (no registry)`), 20 lines after the verdict, long lines cut at 210 columns here:

```
structure: informational - does not change the verdict or the exit code
structure: descriptor (built-in default)
structure: profile=reqharness nodes=275 (HLR=76, LLR=199) edges=196 (refines=196) cycles=0
structure: sources: canon=REQUIREMENTS.md us_canon=unset at_table=unset
structure: gaps: 7 (HIGH=0, MED=7, LOW=0)
structure gap: MED · HLR WITHOUT LLR · HLR-N13.3 · reach=0 · HLR-N13.3 has no LLR under it: While the workspace holds maps, a map that cannot be summarised shall be declared as such on its own card, and every ot…
structure gap: MED · HLR WITHOUT LLR · HLR-N16.3 · reach=0 · HLR-N16.3 has no LLR under it: When the operator presses the help chord twice in succession, the system shall produce a declared outcome that does not…
  … (HLR-N16.4, HLR-REPAIR.1 [qualified: 2], HLR-S06.2, HLR-CAN.1 [qualified: 2], HLR-RS.3 — 5 more gap rows)
structure note: unparsed row LLR-HYG.1.1
structure note: unparsed row LLR-CAN.1.1
structure note: unparsed row LLR-CAN.1.2
structure note: unparsed row HLR-RH.6
structure note: unparsed row LLR-RH.6.1
structure note: unparsed row LLR-RH.7.3
structure note: unparsed row LLR-Q3.1.2
structure note: unlinked LLRs (3): LLR-REPAIR.1, LLR-REPAIR.2, LLR-RH.6.2
```

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/relmap/audit.py` | source | LLR-RMU.1.2–.1.4 (D5) | NEW (~190 lines) |
| `mapper/reqharness/audit.py` | source | LLR-RMU.1.1 (D4) | `run_cli` gains `extra_lines`; `_hook_lines`; 4 constants; docstring |
| `mapper/app.py` | source | LLR-RMU.1.1 | passes the hook (2 lines) |
| `tests/test_relmap_audit.py` | test | LLR-RMU.1.1, LLR-RMU.1.2, LLR-RMU.1.3, LLR-RMU.1.4, LLR-RMA.1.1, LLR-RML.1.5 | NEW: 48 nodes (47 run + 1 platform-skipped) |
| `tests/_relmap_fixtures.py` | fixture | LLR-RMU.1.2 (PDR D-5, ledger `.35`) | NEW: IMPORTS `_seed`, `_git_repo`, `_write_canon`, `_audit_cli`, `ONE_ROW`, `HLR_FIELDS`, `CANON_HEADER`, `_add_ana`, `_grant_reviewer`, `_record_review`; adds `registry_repo`, `ready_repo`, `run_audit` (child pinned to this checkout), `run_audit_nohook`, `report_of` |
| `tests/test_relmap_adapter.py` | test | LLR-RMA.1.3 (Inc-4 F1, F4) | +1 node (`test_unparsed_count_of_a_dotless_hlr_is_not_doubled`), one assertion |
| `tests/test_relmap_descriptor.py` | test | LLR-RML.1.6 (census) | one allow-list entry: `test_relmap_audit.py` may name `.relmap.yml` (it writes them as Layer B fixtures) |
| `docs/ARCHITECTURE.md` | doc | PD-4 | §2 `relmap` row: `audit.py` as built; §3 contract note: `run_cli` hook, verdict-by-prefix, fixed lines, sources-line-only |
| `01-requirements.md`, `01-requirements-ledger.md` | doc | §0 | contract text and entries `.58`–`.64` |
| `increment-004.md`, `evidence/review-inc004.md`, `evidence/inc4f-*`, `evidence/inc5-*` | doc | | review cell, F1/F4 note, 9 transcripts |
| `mapper/search.py` | source | LLR-RMM.1.1 (the new `mapper/relmap/model.py` made the citation ambiguous), P3 follow-up, ledger `.70` (commit `456da08`, after this increment) | comment wording only: bare `model.py:149` became `mapper/model.py:149` (ambiguous once `mapper/relmap/model.py` exists) |
| `tests/test_ingestion_limits.py` | test | LLR-RML.1.4 (Inc-3 follow-up `f02dbbd`) | two comment wordings; no assertion changed |
| `tests/test_repair_artifact_claims.py` | test | LLR-RMM.1.1 (same cause), P3 follow-up, ledger `.71` (commit `934e935`) | declared `_CITATION_EXCEPTIONS` row for the sealed bare `model.py` citation and `test_every_declared_citation_exception_is_still_needed` |
| `tests/test_repair_sidecar.py` | test | LLR-RML.1.4 (Inc-3 follow-up `f02dbbd`) | comment wording tied to the moved prescan; no assertion changed |
| `README.md` | doc | DDR condition (README Audit section), commit `def89c8` | `mapper --audit` structure block and the verdict-by-prefix note |

| Count | Value |
|---|---|
| **SOURCE files** | **3 / 4** in the increment (`relmap/audit.py`, `reqharness/audit.py`, `app.py`); `mapper/search.py` is listed above for the later P3 follow-up commit (a comment wording only, not part of the increment count) |
| Test files | 1 new + 1 fixture module + 2 edited (uncapped) |
| Doc / config files | 4 (outside the count) |

---

## 3 · How to test

```bash
cd <worktree>   # C:/Users/<user>/AppData/Local/Temp/ds-units/wt-r1
export PYTHONPATH=<worktree>
env -u NO_COLOR -u TERM python -c "import mapper; print(mapper.__file__)"      # inside the worktree
git add mapper/relmap tests                                                   # the A3 census needs new files staged
env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_relmap_audit.py tests/test_relmap_adapter.py
env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_relmap_*.py tests/test_reqharness_*.py tests/test_mod_*.py tests/test_repair_map_truth.py tests/test_arch_osopen_callers.py tests/test_a3_census.py tests/test_no_operator_paths.py tests/test_prescan_refusal_goldens.py tests/test_yamlscan.py tests/test_ingestion_limits.py
```

Targeted files only; never the full suite. `mapper.__file__` printed `C:\Users\<user>\AppData\Local\Temp\ds-units\wt-r1\mapper\__init__.py` (executed), and `test_child_runs_this_checkout` asserts that the subprocess children (PYTHONPATH set in their env) import the same file.

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** (formatter branches: caps, cut, skipped parts, notes order) | `core` · `full` | `test_line_formats`, `test_gap_cap_*`, `test_note_cap_*`, `test_skipped_rows_line_counts_only`, `test_notes_come_in_the_stated_order…` | executed: GREEN |
| **A · white-box** TC ↔ LLR | `core` · `full` | TC-RM-02, TC-RM-03, `test_hook_line_bound`, `test_fixed_lines_key_on_chain_status…`, `test_canon_derived_once`, `test_canon_over_the_node_cap…`, `test_format_structure_cuts_inside`, `test_refusal_line_hostile_name`, `test_reported_note_with_bidi_is_cut_and_escaped`, `test_escaped_and_no_forged_verdict`, `test_header_first`, `test_sources_line_configured_string` | executed: GREEN |
| **B · black-box** AT through `mapper --audit` | `core` · `full` | AT-117, -118, -119, -120, -121 (×2 + controls), -122 (×6 arms), -124, -125, -126, -127, -128 (`test_byte_stable`), -129, `test_snapshot_run`, `test_exit_code_unchanged`, `test_the_block_on_the_repository_itself` | executed: GREEN — **this is where the Layer B nodes of AT-117/119/124/125 are minted for real (ledger `.63`)** |

Audit + adapter files: **86 passed, 1 skipped**, exit 0, 29.4 s (`evidence/inc5-green-final.txt`; the skip is the ESC-in-a-file-name arm, `blocked: this file system refuses an ESC in a file name`, stated, with the ESC-in-a-descriptor-key arm covering the same sink). Guard run — `test_relmap_*` ×7, `test_reqharness_*` ×10 (includes the 16 `--audit` sites in `test_reqharness_release.py` and `test_reqharness_baseline.py`, and the hostile-canon arms at `:665-680`, `:755-770`), `test_mod_*` ×7, `test_repair_map_truth`, `test_arch_osopen_callers`, `test_a3_census` (pin 86 unmoved), `test_no_operator_paths`, `test_prescan_refusal_goldens`, `test_yamlscan`, `test_ingestion_limits`: **701 passed, 2 skipped** (FIFO, ESC-in-name), exit 0, 132.4 s (`evidence/inc5-guards.txt`). A first guard run was RED on one node, `test_relmap_descriptor.py::test_the_input_class_is_new_…` (its allow-list did not name the new suite); fixed by the one-line allow-list entry above and the whole guard set re-run (the transcript is the second run). **Measured wall time:** `test_relmap_audit.py` about 28 s (many subprocess runs, each over a tmp git repository), budget "about a minute" met; the two heavy arms (100,001-row canon, 8 MiB descriptors) are in their own functions. No elapsed-time assertion anywhere.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (1) code-absent: `relmap/audit.py` absent, the tests present; (2) move-aside of `relmap/audit.py` with hash check; (3) `reqharness/audit.py` and `app.py` replaced by their `HEAD` versions (hook arms must fail, compatibility limb must hold); (4) 27 mutants (next table) |
| Instrument | `battery5.py`, `pt.sh`, `n3.py` (scratch outside the repo): hash before, edits, targeted pytest, restore from the original bytes, hash after, one verdict per mutant |
| Where it ran | the batch worktree, by the `software-dev` author; deterministic, the orchestrator may re-run |
| Transcript | `evidence/inc5-red-code-absent.txt`, `inc5-red-moveaside-relmap-audit.txt`, `inc5-red-moveaside-hook.txt`, `inc5-red-mutants-battery.txt`, `inc5-n3-seed-pair.txt` |
| Restore proven by | sha256 after every arm equals the one before: `relmap/audit.py` `afcd7836…`, `reqharness/audit.py` `0a0f78f6…`, `app.py` `465642cc…`, `descriptor.py` `4aad6f80…`, `adapter.py` `cd58d797…`, `gaps.py` `dd180acf…`, `model.py` `1b602e84…` |
| Bytecode cache | `-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1`; each arm its own process |
| Arms resolved at baseline | the audit file GREEN (47 passed, 1 skipped) before the battery |
| Verdict granularity | per mutant, by failing node ids |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | (1) code-absent: `ImportError: cannot import name 'audit' from 'mapper.relmap'` at collection, exit 2; (2) move-aside: the same error, exit 2, hash equal after restore; (3) base `reqharness/audit.py` + `app.py`: **28 of 48 nodes FAIL** (`TypeError: run_cli() got an unexpected keyword argument`, and the Layer B nodes for want of any structure line), exit 1, while `test_reqharness_release` / `_baseline` (compat limb) stay GREEN in the guard run |

| Field | Value |
|---|---|
| **Mutation verdicts** | 27 mutants, **27 KILLED, 0 SURVIVED**, every restore hash-equal. The Inc-5 mutants of the proposal: **M-RMU-1** (print raw) → 7 (`test_escaped_and_no_forged_verdict` (named `test_escaped_and_no_forged_verdict` in the battery transcript; renamed afterwards to carry the contract's name, behaviour unchanged) and the six AT-122 arms, each RED on its own) · **M-RMU-2** (exception escapes) → TC-RM-02 · **M-RMU-3** (no gap cap) → the 21-gap arm · **M-RMU-4** (hook for the no-repo report) → AT-126 and the chain-status test · **M-RMU-5** (no cut) → `test_format_structure_cuts_inside`, `test_reported_note_with_bidi…`, AT-129 · **M-RMU-6** (set iteration) → `test_byte_stable` (AT-128) and 4 more · **M-RMU-7** (drop the skipped line) → AT-124 · **M-RMU-8** (exit 1 on a structural gap) → AT-120 · **M-RMU-10** (hook on the baseline refusal) → TC-RM-03 · **M-RMU-11** (cut moved to the wrapper; AT-129 stays GREEN) → ONLY `test_format_structure_cuts_inside` and `test_reported_note_with_bidi…` · **M-RMU-12** (unbounded) → `test_hook_line_bound` · **M-RMU-13** (`refusal_line` skips the cut) → `test_refusal_line_hostile_name` + 3 Inc-3 arms · **M-RMU-14** (no header) → `test_header_first`, AT-120 and 4 more · **M-RMU-15** (new: `RelMapLimitError` escapes) → `test_canon_over_the_node_cap…` · **M-RML-9** (derive per descriptor) → `test_canon_derived_once` · **M-RML-13** (no count cap) → AT-127 + `test_repo_root_census_counts[9]` · **M-RML-7** (no link check) → AT-121 k01 + 5 Inc-3 arms · **M-RML-1** (no prescan) → AT-121 + 3 · **M-RML-10** (`str(exc)`) → AT-121 + 2 · **M-RML-11** (`in` over a set) → AT-121 + 2. **Layer B kills of the upstream mutants:** M-RMA-1 → AT-117/119/125, `test_byte_stable`, `test_snapshot_run` · M-RMA-6 → 12 (AT-117, -118, -120, -122, -124 …) · M-RMA-3' (drop the notes; the literal M-RMA-3 is Inc-4's) → AT-119 · M-RMA-5 → AT-125 · M-RMG-4 → AT-125 · M-RMG-6' (eligibility ignored) → AT-118 · M-RMM-1 (unsafe ids kept) → AT-124. **Not run:** M-RMU-9 (named in the proposal's line-formats row, defined nowhere in the contract or ledger — §6 item 6). |

**N-3 re-proof (AT-128's two seeds), executed for real** (`evidence/inc5-n3-seed-pair.txt`): on the snapshot plus three descriptors, clean code gives equal bytes under `PYTHONHASHSEED=0` and `2` (sha256 `1675dd00…` both); with M-RMU-6 applied the two stdout byte strings DIFFER (`7dcfc6d9…` vs `1675dd00…`), the first differing line being `nodes=275 (LLR=199, HLR=76)` under seed 0 against `(HLR=76, LLR=199)` under seed 2. The pair is the one the probe picked, and the mutant is killed by it.

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the sink-escape scans (`"\x1b" not in out`, …) | M-RMU-1 prints the hook lines raw | the six AT-122 arms RED, each alone, and each also asserts the ESCAPED spelling is present (a positive control, so an empty block cannot pass) |
| `report_of` / `block_of` (finds the verdict by prefix) | a stdout with zero or two `verdict: ` lines | asserts exactly one; `test_at_122_forged_verdict_in_a_descriptor_key` counts the prefix lines |
| the max-line-length scan | a 1 MiB value passed to `format_structure`; M-RMU-5 | RED (`test_format_structure_cuts_inside`, AT-129) |
| the byte-equality of two seeded runs | M-RMU-6 | RED; the two byte strings recorded as different (N-3) |
| the pull counter of the line-bound generator | M-RMU-12 | RED (`len(pulled) <= 1001` fails with 5,000) |
| the child-checkout probe | a child that imports another `mapper` | `test_child_runs_this_checkout` compares the child's `mapper.__file__` with the test process's |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 6 instruments, each shown RED by a mutated or known-bad input |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the report prefix (every line up to and including `verdict:`) | equals the golden CAPTURED BY RUNNING `mapper --audit` on the base commit `ab412fc` (no hook), repository path as `<repo>` — `GOLDEN_PREFIX` in the test, asserted in-process (`run_cli` without the hook) and in the subprocess (with and without a refused descriptor) | GREEN |
| the summary / skipped / sources / gap-total lines | exact line equality on the snapshot run, on a 3 HLR + 2 LLR canon, and on the AT-124 canon | GREEN |
| the refusal lines of K1, K2, K5–K17 | the literal fixed text per cause (K5 `exceeds the 8388608 byte limit`) in the stdout of a real run; no path, anchor name or YAML snippet | 16 literals GREEN |
| the ESC / bidi / combining / variation-selector / U+2028 surfaces | scanned in the captured stdout of the real run, next to the escaped spelling | GREEN |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 4 artifacts, each asserted against the form its producer wrote |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` (`.dev-flow/2026-10-25-relmap-r1-batch/evidence/`) | SHA-256 |
|---|---|---|
| RED, code-absent (exit 2) | `inc5-red-code-absent.txt` | `d515de0c9f67173a230f7a988cd28512d1e75c53b56463200fbc0899335829b7` |
| RED, move-aside of `relmap/audit.py` (exit 2, restore hash equal) | `inc5-red-moveaside-relmap-audit.txt` | `5f6a2f7f246e8cea742680ce4cc1683f6fa34c1e76c032132d8e314715b40f55` |
| RED, base `reqharness/audit.py` + `app.py` (28 failed, restore hashes equal) | `inc5-red-moveaside-hook.txt` | `c5350686b9e355026297fb251afdeea1994df0ab4c9e4b436b868933d0f622aa` |
| GREEN, audit + adapter files (86 passed, 1 skipped, 29.4 s) | `inc5-green-final.txt` | `6eeed420dd20fecbade7e00408307f5ac516918c78feedb142cd4c86a386640c` |
| Guard suites (701 passed, 2 skipped, 132.4 s) | `inc5-guards.txt` | `c700f8c8ac8be676c09fc080dde2f3891c0f83be811f46778732be1f622c98cb` |
| 27-mutant battery | `inc5-red-mutants-battery.txt` | `1d6625fbe500d2d3afbddb85a49dd7da6a0bf5ab45dbf173e991f9dc37d4355d` |
| N-3 seed pair against the real M-RMU-6 | `inc5-n3-seed-pair.txt` | `b46315ff8ef3b4a2e528bab56cf8d67c5bcbefe065f7039dcfa0714d38bef064` |
| Inc-4 F1 mutant C re-run | `inc4f-red-f1-mutant-c.txt` | `a06d05b4a466d2a49222c82ff09e76a3138204420c5fa9d133b217e02c0cdd66` |
| Inc-4 independent review (committed here) | `review-inc004.md` | `1d2ab29a397bb33f64a5736badcc773ce715ab48076b73f0c0181f5826440454` |
| Inc-5 independent review | `review-inc005.md` | `e037820f5757f44612bf89b2c2626787258265340ce7f901aff43c30d3c8dbbc` |
| Follow-up RED (F1 M-RMU-9, F2 guard) | `inc5f-red.txt` | `5d494d02ec2bc32be173f9c6c0abf795649a3984286e546fd52f67ae1f139403` |
| Follow-up GREEN (107 passed, 1 skipped) | `inc5f-green.txt` | `1e8562dc544d542832caed1d47dd2bfb6aed9f6256fc7f8fabfa29834a03fe02` |
| Follow-up guards (231 passed, 1 skipped) | `inc5f-guards.txt` | `b8cfc3765f6e2d0bd98038e9718f83a6daa8ec86ac570ac9161cdb1173a7c565` |
| Follow-up gate (`devflow-validate --brief .`, exit 0, 0 blocks; V15/V16 did not fire on this run; one Phase-4 notice V47) | `inc5f-gate.txt` | `00d161116d7a361c0d1c67d6745da43f5f5b2419de088149697ca0f0f144c50c` |
| Gate (`devflow-validate --brief .`) | `inc5-gate.txt` | `3e6a1e426621e6af7ad35708fa1a2ee2fcfa547386d0b3e75f4c76a8ae87559b` |

| Field | Value |
|---|---|
| **Evidence files** | 10 artifacts at the declared home, each with its digest prefix; every transcript is redacted (`<user>`) before hashing and records its exit code and wall time (the battery records per-arm wall time) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: (a) "no printed structure line contains the path marker" (the `repo:` line of the OLD report does print the path); (b) "the exit-0 fixture has a gap" and "the no-gap fixture has none"; (c) "no existing `--audit` test counts stdout lines or takes `[-1]`" |
| If the result is an ABSENCE, what made the search wide enough | (a) asserted over the block lines only, with the marker in six different repository names, paired with the positive case where the same repo path DOES appear in the report line; (b) both fixtures assert their gap count first (`_gap_lines` non-empty / empty); (c) the 16 sites ran in the guard set (701 passed) |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_run_cli_without_the_hook_is_byte_identical` protects "the hook is additive"; `test_exit_code_unchanged` protects "informational" |
| Conjunctive criteria: one mutation per conjunct | the hook's four duties each have a mutant: no-repo/no-registry (M-RMU-4), bounded (M-RMU-12), raising (M-RMU-2), refusal path (M-RMU-10) |
| Synthetic instance of the absent case | the over-cap canon (100,001 rows), the 21-gap and 11-note maps, the 5,000-line generator, the 1 MiB values, the combining-mark base name |
| **Positive control for every probe that returned an ABSENCE** | each escape scan is paired with the escaped spelling (`\\u0301`, `\\x1b[31m`, `\\u2028verdict: ready`) present in the same stdout |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `git grep -n "run_cli\|extra_lines\|structure_lines" -- mapper tests docs` | `run_cli` has one caller (`app.py`) plus the new tests; no earlier test passes a second argument |
| B2 file moved on disk | none moved | no readers to find |
| B3 byte-identical golden captures this source | `git grep -il "structure" -- tests/goldens` | 0 hits |
| B4 artifact produced here is consumed elsewhere | the block is read by humans and CI; `tests/_relmap_fixtures.py` is consumed by `test_relmap_audit.py` only | stated in ARCHITECTURE (verdict by prefix) |
| B5 fixture content | the 16 `--audit` sites (10 print the block, 6 refuse first) | all in the guard run, 701 passed; the happy fixtures assert no `internal error` line |
| A3 interface consumed by another module changed | `test_mod_*`, `test_repair_map_truth`, `test_arch_osopen_callers`, `test_a3_census` | all in the guard run; pin 86 unmoved; `app.py` 361 ≤ 400 |
| content census of the suffix | `test_the_input_class_is_new_…` (by CONTENT) | fired once on the new suite; allow-list updated, then GREEN |

| Field | Value |
|---|---|
| **Reverse census** | 7 probes run, each with its command and verdict; B2 did not fire |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| ARCHITECTURE §2 `relmap` paths: audit "planned for Inc-5" → built | statements that the audit path is planned | `grep -n "planned for Inc-5\|audit module is planned" docs/ARCHITECTURE.md` (the edit asserted the old sentence occurs exactly once) | 1 | 1 | the §4 *Current batch* table row 5 names `relmap/audit.py` as a file of Inc-5, which is plan text, still true |
| the five "stays on the map" / "configured, not derivable" / orphan-class / kept-nodes / limit wordings of §0 | contract sentences naming the adapter's output | each `sub()` in the edit script asserted exactly one match (7 sentences) | 7 | 7 | none |

| Field | Value |
|---|---|
| **Correction population** | 2 correction families, 8 sentences, each matched exactly once before replacement |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `the audit module is planned for Inc-5` | `grep -c` over `docs/ARCHITECTURE.md` → 0 | yes | `docs/ARCHITECTURE.md` §2 `relmap` |
| `full report text stays on the map for Layer A` | `grep -c` over `01-requirements.md` → 0 | yes | LLR-RMA.1.3 |
| `one note per configured` | `grep -c` over `01-requirements.md` → 0 | yes | LLR-RMA.1.4 |
| `the configured-not-derivable sources` | `grep -c` over `01-requirements.md` → 0 | yes | LLR-RMU.1.2 note row |

### Signed-balance test ledger

`post = base − deleted + added`: `test_relmap_audit.py` `48 = 0 − 0 + 48` (collected with `--collect-only`); `test_relmap_adapter.py` `39 = 38 − 0 + 1`; `test_relmap_descriptor.py` unchanged count (one assertion line edited); `_relmap_fixtures.py` holds no test.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Claude Sonnet subagent executing agents/code-reviewer.md + agents/security-reviewer.md + agents/ux-reviewer.md · approve-with-nits` — `evidence/review-inc005.md` (sha256 `e037820f5757f44612bf89b2c2626787258265340ce7f901aff43c30d3c8dbbc`) |

### Review follow-ups (closed in commit `c2d244b`)

| # | Sev | Disposition | RED / GREEN |
|---|---|---|---|
| F1 | MEDIUM | Closed. `test_byte_stable` (Layer B, `beta` descriptor) asserts the sources line `canon=REQUIREMENTS.md us_canon=docs/us.md at_table=docs/at.md` and the repository's absolute path absent from the block. Ledger .27 (the entry that names M-RMU-9; the review said .59) re-pointed, .59 cross-referenced. | M-RMU-9 applied: `test_byte_stable` RED (`inc5f-red.txt`); restore hash-equal (`afcd78363a0f`); GREEN |
| F2 | MINOR | Closed. Sink guard: a hook line starting `verdict: ` after `_visible` is PREFIXED with `structure: ` (not dropped: nothing lost silently). Layer A arm `test_hook_line_can_never_forge_a_verdict_line` (generic hook returning `verdict: ready`). Per-line length bound: not added (shipped formatter bounds its lines; generic hook is the caller's); noted for R2. Ledger .67. | Guard absent: RED; guard removed (`if False:`): RED; with guard: GREEN |
| F3 | MINOR | Closed, wording only (3 sites in `01-requirements.md`): "total collection depth 64 loads, 65 refused (the top-level mapping counts as depth 1)". Ledger .66. No code change. | n/a |
| F4 | MINOR | Closed, doc only: `reach` defined in `docs/ARCHITECTURE.md` relmap row. Widths unchanged. Ledger .68. | n/a |
| F5 | MINOR | Recorded: the verdict-by-prefix note lives in `docs/ARCHITECTURE.md` (section 3 contract note) and the on-screen header; README has no `--audit` text. Ledger .68. | n/a |

Evidence: `evidence/inc5f-red.txt`, `inc5f-green.txt` (107 passed, 1 skipped), `inc5f-guards.txt` (231 passed, 1 skipped: `test_mod_*`, `test_repair_map_truth`, `test_a3_census` pin 86, `test_no_operator_paths`, `test_relmap_descriptor`). `mapper.__file__` proved inside the worktree. Full suite: `not-run` (by instruction). Gate after the follow-ups: exit 0, no blocks (`evidence/inc5f-gate.txt`; the first run flagged V26 for the three new ledger entries, fixed by back-pointers in `01-requirements.md` before the recorded run); the earlier V36 on the pending cell is cleared by this review cell.

---

## 5 · Risks

- **The block repeats the gap rows once per descriptor** (the map and the gaps are the same for every descriptor; only the label, sources and ignored keys differ). With 8 descriptors the output is about 298 lines as stated in the reading notes; a reader who wants one list sees it repeated. Not changed: the contract says "one labelled block each".
- **A single refused descriptor prints only its refusal line**: no map summary and no gaps at all (the contract's "block | refusal line"). An operator with one broken `*.relmap.yml` and nothing else loses the structure report for that run.
- **A canon the audit cannot read prints header + one `unavailable (canon: …)` line and nothing about the descriptors** (the descriptors are not loaded when there is no map to describe).
- **`structure_lines` ranks the gaps once for all descriptors**; the shared visit budget (2,000,000) is therefore spent once per run, not per descriptor.
- **The 100,001-row canon test builds a 2.8 MB canon and runs `build_map` twice** (Inc-4 watch-item `.64`): about a second; an R2 change to the adapter should look at the double build before views multiply the cost.
- **Subprocess ATs depend on `git`** (a repository per fixture); a host without `git` fails them loudly in the fixture, not silently.
- **The `--audit` output now has more lines after the verdict**: a CI step reading the last line breaks (UX MAJOR-4, documented in ARCHITECTURE and the first block line).

---

## 6 · Pending items / spec deviations

Nothing is deferred silently. For the orchestrator:

1. **AT-126(c), symlinked canon.** The contract says a symlinked canon prints `structure: unavailable (canon: is a link)`. Through the shipped CLI it never does: `audit()`'s own confinement sweep refuses a linked `REQUIREMENTS.md` BEFORE any report exists (stdout empty, stderr `audit: …: refused (link)`, exit 1), so the hook is not called. The node asserts exactly that, and the over-cap / binary / missing arms carry the other K texts; the K1 text for the canon is pinned at Layer A (`test_canon_causes`, Inc-4). Suggest amending AT-126(c) to drop the symlink arm.
2. **AT-126 "the marker never appears in stdout".** The existing `repo:` line prints the repository path, marker included, by design. The marker assertion is made over the BLOCK (every line after the verdict). Suggest wording "never appears in the structure block".
3. **AT-121 K9 numbers.** The contract says depth 65 refused / 64 loading; Inc-3's tests measured the real boundary for a flow-nested value as 64 refused / 63 loading (`x: {k: {k: …}}`, under the key `x`). The node uses the measured numbers (`_nested_flow(64)` / `(63)`), reusing Inc-3's helper.
4. **Wordings the contract left open, now fixed by the code and tests:** the unlinked note is `unlinked LLRs (<total>): <first 5 ids>[ and <K> more]`; an ignored descriptor key is `ignored descriptor key: <key>`; the gap sentence has a 400-character safety cap beyond the 120-character cut of its ingredients (the qualifier must survive, so the sentence itself is not cut to 120). Suggest a one-line addition to the LLR-RMU.1.2 table.
5. **`relmap.audit` uses `exc.limit` for the canon's K5 text** (it equals `LIMIT_ROLES_YML_BYTES`); no new import of `reqharness` in `audit.py`.
6. **M-RMU-9** appears in the proposal's line-formats row and in no contract line or ledger entry, so no mutant was defined or run for it. Either name it or drop it from the proposal.
7. **ESC in a descriptor FILE name (Inc-3 MINOR-2)** is `blocked` on this host (Windows refuses control characters in names; the arm skips with that reason). The ESC-in-a-descriptor-KEY arm and the Layer A hook arm exercise the same sink on every platform.
8. **`tests/test_relmap_descriptor.py`** got a one-entry edit to its content census (the new suite is allowed to name `.relmap.yml`); declared because the file belongs to Inc-3.
9. **Gate (`devflow-validate --brief .`):** `devflow-validate --brief .`, exit 1, `evidence/inc5-gate.txt`. **5 blocks, none of them in this increment's work, no V2 left:** `V15` x2 and `V16` x2 are the environment (the `dev-flow` bundle under `~/.claude/skills` carries a `__pycache__`, and `~/.claude` has uncommitted changes), the same class Inc-3 recorded; `V36` x1 is `increment-005.md`'s Independent review cell reading `pending`, which BLOCKs here because `V27`'s harvest reads the Inc-3 decision's text `(MINOR-2 escaping verified at Inc-5)` as a decision NAMING increment 5, so the packet counts as gated before its review exists (`state.json` `decisions_log`, entry `P3 increment 003 approved`; rewording `Inc-5` there, or logging the Inc-5 decision, clears it; I did not touch `state.json`). Cleared by this work: the `V2` blocks of Inc-4 (AT-118, AT-120, AT-122, AT-126, AT-128, AT-129 now have Layer B nodes; `AT-123` is the retired id, written as a citation, ledger `.65`), `V56` on `increment-004.md` (its evidence digests are now full 64-hex, which the reader requires) and `V59`. The transcript is of the packet as written just before this cell was filled.
10. **Not done, by instruction:** no push, the station is not moved, no approval is logged, the one full-suite run is the orchestrator's.

---

## 7 · Suggested next task

The batch's five increments are in. Next is Phase 4: the independent review of this increment (code + security lenses: the sink, the 1,000-line bound, the cut inside the formatter), the DDR (`PDR-…` §B rows filled by re-reading), the one full-suite run, the operator-run Python 3.10 check, and the decisions on §6 items 1–4 and 6 (contract wording).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 / 4: `relmap/audit.py`, `reqharness/audit.py`, `app.py` (§2) |
| 2 | Tests written in this same increment | all | ✓ | 48 new nodes + 1 + helper; 86 passed, 1 skipped (`evidence/inc5-green-final.txt`) |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | the formatter's caps, parts and orders; the hook's dispatch; 27/27 mutants killed |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | code-absent and move-aside exit 2; base hook files 28 failed (`evidence/inc5-red-*`) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | seven probes with commands in §4 |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | approve-with-nits, `evidence/review-inc005.md`; F1-F5 closed in `c2d244b` (§4b) |
| 7 | No file from another lane touched | all | ✓ | no lane; file set is proposal §2.1 row 5 (+ the declared one-line census edit, §6 item 8) |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D4 `run_cli(argv, extra_lines=None)` and D5 `structure_lines(repo)` as the proposal states; D1–D3 untouched; `format_structure` gained two keyword arguments (`unlinked`, `ignored`) as a tested seam, not frozen (PD-3) |
| 9 | Coverage claims verified **on disk**, not from intent | all | ✓ | every node named in §4 exists and was collected (48) |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | all | ✓ | §4 *Load-bearing emptiness* |
| 11 | **Mutation verdicts** declared — per arm | all | ✓ | 27 mutants, 27 KILLED, per mutant and node in §4 |
| 12 | **Instrument RED-proof** declared | all | ✓ | 6 instruments, §4 |
| 13 | **Correction population** declared | all | ✓ | §4: 2 families, 8 sentences, matched exactly once |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4: 4 artifacts |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` (Claude Sonnet subagent, code + security + UX lenses) (§4b) |
| 16 | **Evidence files** declared | all | ✓ | §4: 10 artifacts with SHA-256 |
