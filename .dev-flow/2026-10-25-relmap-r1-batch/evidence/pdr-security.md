# PDR security review (trigger C6) — relmap-r1 batch

Reviewer: security-reviewer (independent; authored none of it). Read-only; this is the only file written.
Scope: `design/design-proposal.md` (§2 boundaries, §2.1 file sets, §3 algorithms, §4 frozen D1-D5, §5.1 test plan, §5.2 census, §6 risks), `design/PDR-2026-10-25-relmap-r1-batch.md` (row 10, D1-D8), against the contract (`01-requirements.md` LLR-RML.1.5, RMM.2.2, RMG.1.3, RMU.1.2) and the ledger (mutants M-RML-14/15, M-RMM-10, M-RMU-9). HEAD c1f3e01. Design-level review: evidence state of every item is `planned`; the executed arms are verified at each increment gate.

## Verdict: approved with conditions

Every pass-1/pass-2 mitigation is carried into the design with a named test and a named mutant. The frozen surface exposes two ways for R2 to re-open a closed risk (C1, C2 below). Neither needs a redesign: each is a one-line freeze note plus one test arm, recorded as PDR conditions to discharge at the DDR (or at Inc-1/Inc-5 for the test arms).

## Mitigation carry-through

| Id | Mitigation | Where in the design | Test | Mutant | Status |
|---|---|---|---|---|---|
| F1 | canon read via lstat + capped reader, no `load_canon` | §2 `descriptor` owns `read_repo_text`; `adapter` "opened only through `read_repo_text`"; divergence from `load_canon` recorded in the `relmap` row | `test_read_repo_text_*` (link, directory, FIFO where possible, cap±1, NUL, non-UTF-8), `test_canon_causes` | M-RML-7, M-RML-8 | carried |
| F2 | canon-problem line carries a fixed K1-K7 | §4 D3 `CanonUnavailable.cause`; §3 interaction diagram `unavailable (canon: …)` | `test_canon_causes`, AT-126 marker arm | M-RMU-4, M-RML-7 | carried |
| F3 | discovery cap 8, links/non-regular refused, canon derived once | §4 D2 `discover_descriptors -> (≤ 8 paths, overflow)`; §3 "parse_canon ONCE" | `test_repo_root_census`, `test_canon_derived_once`, AT-127 | M-RML-9, M-RML-13 | carried |
| F4 | 120-char cut BEFORE escaping; note/gap caps | §2 `model` owns `DISPLAY_MAX`, `cut`; `audit` "truncation"; every line then goes through the report's escaper (§3) | `test_line_formats`, AT-129, `test_escaped_and_no_forged_verdict` | M-RMU-5, M-RMU-3, M-RMU-1 | carried; see C2 for where the cut must live |
| F5 | YAML failure = constant K10 | §4 D2 `CAUSE` K1-K17; `DescriptorError.cause` | causes K1-K10 arms (hostile snippet, big integer), `test_closed_cause_set` | M-RML-10, M-RML-15 | carried |
| F6 | iterative reach, visit bound, `reach_not_computed` | §3 "bounded ranking"; §4 D3 `rank_gaps -> (ranked, reach_not_computed)` | `test_reach_chain_at_cap`, `test_rank_visit_cap`, `test_rank_100k_sinks` | M-RMM-8, M-RMG-5 | carried; see C1 |
| F7 | problems counted on one line | §4 D5 `format_structure(…, unknown_status, reach_not_computed)` | AT-124, `test_line_formats` | M-RMU-7, M-RMM-1 | carried |
| F8 | confinement before any filesystem call; K17 closed reason | §2 `descriptor` "path confinement … any open of us_canon/at_table" forbidden | `test_paths_confined` (UNC: 0 `stat`/`open`) | M-RML-4 | carried |
| N1 | fstat identity after lstat | contract LLR-RML.1.5 (open once, compare `st_dev`/`st_ino` and type, K2 on mismatch; the second window to `read_capped` is stated as accepted); design §6 risk 4 names the identity-mismatch arm | `test_read_repo_text_*` identity arm (monkeypatched `os.fstat`) | M-RML-14 | carried (residual window accepted and stated; see M1) |
| N2 | sources line prints the configured string | §4 D5 `sources=(None, None)` are strings (not `Path`) | `test_sources_line_configured_string`, AT-126 marker arm | M-RMU-9 | carried |
| N3 | reach memo is a count, never a set | §3 "count memoised, never a set" | `test_reach_chain_at_cap` | M-RMM-10 | carried |

## Frozen-surface review (D1-D5): can R2 bypass a mitigation?

- **D1 `yamlscan`** — clean. Leaf, no file reads, error type is not a `ValueError`; the golden pins the strings. Nothing for R2 to bypass.
- **D2 `descriptor`** — clean on reads: `load_descriptor`, `derive_reqharness_map` and `discover_descriptors` all go through `read_repo_text`, so R2 cannot read a descriptor or the canon without the lstat/fstat/cap guard unless it imports `osopen` directly, which the allow-list census (`test_arch_osopen_callers`) forbids for `relmap` consumers. Two notes below (M2, M3).
- **D3 model/gaps** — **C1 below.**
- **D4 `run_cli`** — clean. Only `app.py` passes the callable; no-repo/no-registry lines are fixed; hook failure prints the exception type only; exit code unchanged; `None` is byte-identical.
- **D5 audit** — **C2 below.**

## Conditions (to discharge at the DDR, by re-reading the artifact)

- **C1 (MED) — `RelMap.reach(id)` is public, unbounded, and the 2,000,000-visit bound lives only inside `rank_gaps`.** Frozen in D3 as `reach(id) -> int`. An R2 matrix or node-sheet view that calls `reach` for every row costs up to V x (V+E) (per-node counts are cached, but each distinct node is a fresh BFS), which is the F6 hang by another door. Discharge by one of: (a) a per-`RelMap` shared visit budget that `reach`/`neighbourhood` also draw from, returning the documented "not computed" result when exhausted; (b) a bounded bulk call (`reach_all(limit)`) as the only R2-facing form; or (c) at minimum a sentence in the `relmap` row of `docs/ARCHITECTURE.md` and the D3 docstring: "`reach` is O(V+E) per uncached node; a view may call it only for the rows it paints, at most N per frame", carried as a named constraint into the R2 PDR. Add a test arm (`test_reach_per_node_cost_documented` or the budget arm) so the choice is not prose only.
- **C2 (MED) — D5 returns UNESCAPED lines and the escaper is private to `reqharness.audit`.** `format_structure` / `structure_lines` return plain strings; escaping happens in `run_cli` (`_visible`, `audit.py:81`), which `relmap` cannot import. Any future caller that prints these lines (an R2 status strip, a log, Rich markup) bypasses escaping. Discharge: state in the D5 docstring and the `relmap` ARCHITECTURE row that returned lines are repository-derived and UNESCAPED and the sink must escape (or give `relmap` its own escape helper in R2's batch); plus, at Inc-5, one unit arm that calls `format_structure` DIRECTLY with a 1 MiB id, label and sources value, to prove the 120-character cut happens INSIDE the frozen function and not in `structure_lines` (as written, M-RMU-5 is exercised through `structure_lines`/subprocess, so a cut moved to the wrapper would still pass AT-129 while D5's own callers lose it).

## Notes for Phase 3 (non-gating)

- **M1 (LOW, Inc-3):** the identity check closes the lstat-to-open swap, but `read_capped` re-stats and re-opens afterwards; the residual is stated and accepted in LLR-RML.1.5. On filesystems that report `st_ino = 0` (some network or FAT mounts) a literal comparison could refuse a good file as K2: compare identity only when both inodes are non-zero, or document it; add that arm.
- **M2 (LOW, Inc-3):** `CAUSE: dict[str, str]` is a public mutable mapping in a frozen interface; expose it as `types.MappingProxyType` (and add a one-line test) so no caller can rewrite the closed set at runtime.
- **M3 (LOW, Inc-3/Inc-4, carry to R2/B-141):** `Descriptor` is a plain frozen value constructible with any `us_canon`/`at_table` string, and `read_repo_text(path, cap)` is a file-type guard, not a confinement. When a later batch first opens `us_canon`/`at_table` it must call `osopen.confine_reason` again at open time, then `read_repo_text`; record that sentence beside the "never opened in R1" ban in the `descriptor` row.
- **M4 (LOW, Inc-5):** `DescriptorError.name` carries the raw base name; only `refusal_line` cuts and the escaper cleans it. Keep the base-name arm (descriptor name with U+0301 and a 300-character name) on `refusal_line` directly.
- **M5 (LOW, Inc-5):** D4 types the hook's return as `Iterable[str]`; consume it with a bounded iteration in `run_cli` (or require a list) so a generator cannot produce unbounded output. Only `app.py` supplies it today, so this is hygiene.

## Gate

Approved with conditions C1 and C2. No increment is blocked by them: Inc-1 owns C1 (the `reach` contract in `model.py`) and Inc-5 owns C2 (the direct `format_structure` arm); the DDR discharges both by re-reading the docstring/ARCHITECTURE line and the named test. A clean ship verdict still needs each carried mitigation executed and re-verified at its increment gate.
