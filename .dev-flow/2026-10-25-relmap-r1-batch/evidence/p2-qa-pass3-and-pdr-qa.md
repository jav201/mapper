# QA lens: P2 third pass and PDR review. Batch 2026-10-25-relmap-r1-batch

**Mode:** plan (no result claimed). **Base:** `feat/relmap-r1` HEAD `c1f3e01`. **Read:** `01-requirements.md` (amended), ledger `.17`-`.28`, `design/design-proposal.md`, `design/PDR-2026-10-25-relmap-r1-batch.md`, and the assertion bodies of the existing `--audit` subprocess tests. **Executed:** one Python check against `parse_canon` (results quoted in X-1). No test run, nothing changed.

## Verdicts

- **P2: iterate (one small amendment).** N-1..N-7 are verified, except N-3 (reopened, minor). Verifying N-1 exposed one new major in the same family: AT-122 arm 3 cannot reach the escaper with U+2028 (X-1). It is a two-line text fix, not a redesign, so a full third review is not needed; the coordinator can disposition it directly.
- **PDR: approved with conditions.** Three conditions (D-1, D-2, D-3) must be discharged in the packets or the proposal before the named increment starts. Everything else is minor.

## (a) Second-pass findings N-1..N-7

| Id | Status | Evidence |
|---|---|---|
| N-1 NBSP in AT-124 | verified | AT-124 (contract line 649) now uses U+202E and U+200B (both match `\S+`, both unprintable), states that the NBSP row is skipped by the canon reader, and defines "parsed rows" as the objects `parse_canon` returned. Executed: `'\u200b'.isspace()` is `False`; the regex accepts U+202E and rejects NBSP. `excluded=3 (duplicate id=1, unsafe id=2) unknown_status=1` is now reachable. Ledger .17. |
| N-2 note-table contradiction | verified | LLR-RMU.1.2 note row now orders: one `unparsed row <id>` per reported row, one unlinked line, sources, ignored keys; cap 10 then overflow. AT-119 expects exactly 8 lines (7 + 1). The arithmetic fits (8 of 10). Ledger .18. |
| N-3 AT-128 control may not flip | reopened, MINOR | Seeds 0..3 and a set of 17 names (ledger .19, line 549). The live output only contains `HLR` and `LLR` (plus `refines`) from that set, so a mutant's output differs only in the relative order of two strings. Two orderings over four seeds all coincide with probability 2·(1/2)^4 = 12.5%: the mutant survives one run in eight. Fix: use 8 seeds (0.8% survive) or pre-select, at Inc-5, two seeds proven (by executing the mutant) to give different orders and record them in the packet. |
| N-4 AT-121 overclaim | verified | AT-121 now covers K1, K2, K5-K17 and `a: [`; K3/K4 are named Layer A (`test_read_repo_text_*`). |
| N-5 weak controls | verified | AT-117 controls are M-RMA-1 (199 edges) and M-RMA-6 (274 nodes); AT-120 has M-RMU-8, also cited in HLR-RMU.1; AT-129 drives four accepted surfaces (1 MiB ignored key, 255-character `us_canon` at the probed accepted limit, 5,000-character statement, 200-character id: a 200-character id is still a safe id, so it is printed and cut). |
| N-6 prescan failure vs K10 | verified | LLR-RML.1.1 threshold names `a: [` as failing in the prescan and K10 covering prescan and `safe_load`; M-RML-15 in ledger .21. |
| N-7 snapshot fixture | verified, nit | `test_snapshot_sha256` is named (LLR-RMA.1.1) and created in Inc-4 (proposal §2.1, D7). Nit X-3: M-RML-15 and M-RMA-7 appear only in the ledger and the proposal, not in the LLR "Negative control" lines (V26 pairs requirements and ledger entries, so this is tolerable, but a reader of the LLR alone cannot see the mutant). |

### New findings from this pass

| Id | Sev | Area | Evidence | Fix |
|---|---|---|---|---|
| X-1 | MAJOR | AT-122 arm 3 and LLR-RMM.1.2 boundary line | AT-122 arm 3 is "a statement with ESC and U+2028". `parse_canon` iterates `text.splitlines()`, which splits at U+2028. Executed with `\| HLR-A.1 \| active \| he\u2028llo \x1b[31m \| r \|`: objects `['HLR-B.1']`, reported `HLR-A.1 (3 cells, expected 4)`. The row never becomes a node, so no title or gap sentence carries the character; only `unparsed row HLR-A.1` (id only) is printed. The U+2028 half of the arm passes whatever the escaper does, so M-RMU-1 cannot turn that half RED. The same applies to the LLR-RMM.1.2 boundary text that lists "ESC or U+2028" in an *id* as `unsafe id`: through the canon it surfaces as a reported row (builder-level U+2028 ids exist only in Layer A). | Arm 3: ESC plus U+202E in the statement (neither splits a line, both reach the title). Move U+2028 to a surface that can carry it: a descriptor ignored key written as a YAML double-quoted `"\u2028verdict: ready"` (the forge scenario), plus a Layer A `format_structure` arm. Reword the RMM.1.2 boundary: "U+2028 in a canon id is a reported row; as a builder input it is `unsafe id`". |

## (b) PDR review, QA lens

### Checklist rows (QA's share of the PDR record §A)

| # | Item | QA verdict | Evidence |
|---|---|---|---|
| 1 | Proposal complete | ✓ with D-3 | All sections present; §5.1 lists a move-aside RED per new source file (profile, `__init__`/isolation, model, gaps, yamlscan, descriptor, adapter, audit, hook) and the golden. |
| 4 | Every requirement has foreseen coverage | ✓ | 26 LLRs counted by group (RMP 3, RMM 6, RMG 3, RML 6, RMA 4, RMU 4); each appears in a §5.1 row with a test and a mutant. |
| 5 | Observable and non-vacuous, mutation named | ⚠ conditions D-1, D-2, D-3 | Mutants are named per row; three of them cannot be killed as specified (below). |
| 6 | Gauntlet controls declared | ✓ | Golden-before-move ordering in Inc-3; RED section per packet; A3 pin and staging rule in §2.1. |
| 7 | Frozen interfaces listed | ✓ (not a QA lens item) | D1-D5 in §4. |

### Findings

| Id | Sev | Area | Evidence | Fix / condition |
|---|---|---|---|---|
| D-1 | MAJOR (condition) | Ceiling mutants cannot be killed in bounded time | M-RMG-5 (no visit bound: reach recomputed per gap) "exceeds its ceiling, RED", and the proposal says there is "no wall-clock assertion below the ceiling". On the 50,000-gap hub shape the mutant does about 2.5×10^9 visits: the run does not finish in 30 s, it takes hours, and an elapsed-time assert only fires after the function returns. M-RMM-10 (cache reachable sets) on a 100,000-node chain holds about 5×10^9 elements, i.e. out-of-memory on the mutation run. M-RMM-8 (recursive reach) is fine (RecursionError). | Give `rank_gaps` a deterministic work counter (a visits attribute on the ranking result, or a returned stat) and assert `visits <= 2,000,000` and `reach_not_computed > 0` for the hub arm: the mutant then fails in milliseconds on the counter, not by wall clock. For M-RMM-10 assert on the memo's value types at a 2,000-node chain (integers, not sets), and keep the 100,000 chain only for the "no RecursionError" arm. Decide before Inc-1/Inc-2 and record in the packet. |
| D-2 | MAJOR (condition) | Tests assigned to increments that do not contain their subject yet | `test_snapshot_gaps` is listed under `relmap/gaps.py` (Inc-2) but needs `adapter.py` and the snapshot fixture (both Inc-4); the M-RMG-3 snapshot arm likewise. `test_canon_derived_once` is listed under `test_relmap_descriptor.py` (Inc-3, M-RML-9) but "once across 3 descriptors" runs through `structure_lines`/adapter (Inc-4/5; LLR-RMU.1.4 puts the derive-once rule on `structure_lines`). Neither can be written green at its increment's exit. | Move `test_snapshot_gaps` to Inc-4 and `test_canon_derived_once` to Inc-5 (or give each a synthetic stand-in at its own increment, named). Update §5.1 and the PLAN test column; M-RMG-3 keeps its synthetic `test_unsourced_kind_is_silent` kill at Inc-2. |
| D-3 | MAJOR (condition) | M-RML-8 cannot be seen by the named arm | M-RML-8 ("read the whole file before the size check") is killed by "the cap+1 arm" per LLR-RML.1.5, but a mutant that reads and then compares raises the same K5 text for the same input: the arm's observable is identical. The bound is about bytes read, not the result. | Instrument the read: monkeypatch `open`/`os.stat` (or wrap the file object) to record bytes requested, and assert at most `cap + 1`; or use a sized fixture with a read counter. State it in the `test_read_repo_text_*` arm, otherwise M-RML-8 survives. |
| D-4 | MINOR | Layer B timing and the per-increment honesty | All twelve ATs run `mapper --audit` through the hook that lands in Inc-5, but the PLAN assigns AT-121 to Inc-3 and the adapter ATs to Inc-4. Inc-1..Inc-4 exit checks list only Layer A. A defect in Inc-2/3/4 shows at Inc-5. | State in §2.1 that Layer B evidence first exists at Inc-5; require each of Inc-3/Inc-4 to run an in-process stand-in (descriptor load per cause; `derive_reqharness_map` over the snapshot with the exact counts) so Layer A already carries the figures the ATs will check. |
| D-5 | MINOR | Shared AT builder by copying | "reuse by copying the minimal builder into a shared `tests/` helper, decided at Inc-5". `tests/` is a package with `conftest.py`; copying `_seed`/`_git_repo`/`_write_canon` forks the registry builder, and the next change to `test_reqharness_release.py` silently desyncs it. | Import the helpers (or move them to `conftest.py`/`tests/_audit_fixtures.py` used by both files, with the release test importing them) and decide now. Touching `test_reqharness_release.py` is a reverse-census item (§5.2 would then count it). |
| D-6 | MINOR | Reverse census counts | The proposal says 12 sites in `test_reqharness_release.py` and 3 in `test_reqharness_baseline.py`. Actual: 12 `_audit_cli("--audit", ...)` calls (lines 318, 400, 429, 464, 544, 562, 574, 585, 667, 689, 758, 781) plus 1 direct subprocess at line 513 (`main(); --audit ..`, cwd inside a subdirectory), plus baseline 182, 244, 264 = 16 sites. Six of them are refused before a report exists (464, 544, 585, 781, baseline 244, 264) so the hook never runs; ten print the block (318, 400, 429, 513, 562, 574, 667, 689, 758, baseline 182). The conclusion holds (below) but the table should say 16/10/6. | Correct the counts and add the 513 site. |
| D-7 | MINOR | Golden provenance | "Captured on the base" is stated; nothing requires that the 8 constants were produced by running the base code rather than typed, or that the golden lands in a commit before the `store.py` edit. | Packet records the capture command and base SHA; the golden is committed alone before the delegation commit so `git checkout <that commit> -- mapper/store.py` demonstrates GREEN-on-base. |
| D-8 | MINOR | K1 arm needlessly `blocked` on Windows | Risk 4 / LLR-RML.1.5: the symlink arm reports `blocked` where the platform refuses. A directory junction (`mklink /J`) needs no privilege and is a reparse point, which `osopen.is_link` is meant to catch; the K2 directory arm needs none. | Create a junction on Windows for the K1 arm so it executes; keep `blocked` only if even that fails. |
| D-9 | MINOR | Runtime budget unstated | Heavy arms are listed (100,000 chain, hub, 100,000 sinks, 8 MiB cap±1 for descriptor and canon, 4-8 seed subprocess runs, about 12 ATs each building a git repo with a registry and spawning `python -c`). No total is estimated and no way to run the heavy set apart. | Put heavy arms in separately named functions (already planned) and give each increment packet a measured wall time; estimate for `test_relmap_audit.py` is on the order of a minute (about 40 subprocess runs at 1-2 s), within the 60 s per-run timeout individually. |

### Reverse census: verification of the `--audit` subprocess sites

All assertions read from the files; none counts stdout lines, indexes `splitlines()[-1]`, or compares full stdout equality. The new block follows the `verdict:` line, so substring and prefix assertions hold.

| Site | Assertions that matter (file:line) | Tolerates a structure block? |
|---|---|---|
| release 318 | `returncode == 1`, `in proc.stdout` for chain and verdict (319-322) | yes |
| release 400 | digest before/after (402-403), `"counts: ..." in out` (410-413), `"verdict: not ready · unreviewed requirements" in out` (418) | yes; also proves the block writes nothing (digest equality, no `.git/reqharness-cache`) |
| release 429 | `returncode == 0`, `"verdict: ready" in ok.stdout`, counts (431-433) | yes |
| release 464, 544, 585, 781 | refusal on stderr; `proc.stderr.splitlines() == [...]` (585-587), one stderr line (781-794) | hook not reached (refused before a report); stderr untouched |
| release 513 (direct) | `returncode == 0`, chain and verdict substrings (522-524) | yes (hook root is `report.repo`, the toplevel) |
| release 562 | `"canon unreadable: REQUIREMENTS.md: file not found" in stdout` (571) | yes: the new line is `structure: unavailable (canon: file not found)` and the old line stays |
| release 574 | `"canon unreadable: REQUIREMENTS.md: not valid UTF-8"` (578) | yes; K7 wording lives on the new line only |
| release 667 | no raw `\x1b`, `\x7f`, `\r`, C1 over the WHOLE stdout (670-673); `verdict_lines == ["verdict: ready"]` (676-677) | yes, and it is a free regression: the block passes through the same scan; relies on the escaper reaching every printed value |
| release 689 | `"chain: no registry yet" in stdout`, `"chain broken" not in stdout` (693) | yes; no-registry prints `structure: unavailable (no registry)` which contains neither |
| release 758 | no raw U+2028/U+202E/U+200B in the whole stdout (762); `verdict_lines == ["verdict: ready"]`; escapes present | yes; same free regression |
| baseline 182 | substring assertions: `baseline v0: dirty=false`, `changed:`, `new:`, `retired:`, `deleted:`, `verdict: not ready` | yes |
| baseline 244, 264 | stderr and a marker absent from stdout and stderr | refused before the hook; the marker test also constrains the new block if it ever ran |

One residual: tests 667 and 758 run a canon whose statements carry hostile characters and assert exit 0. The block adds a gap sentence from those statements (through the 120 cut and the escaper), so those two become incidental regression tests for the escaper on the real surface; they assume the canon of those fixtures does not make the hook raise (a raise would add one `structure: unavailable (...)` line, still tolerated, but would hide a bug), so the AT should assert absence of that line in the happy fixtures.

### Fixture plan

- **Snapshot:** created Inc-4, pinned by `test_snapshot_sha256` (ledger .4 digest, matches the probe file `93b18472…`). Sound once D-2 is applied. It is a byte copy of the repository canon, so it contains only repository text.
- **Golden on base:** correct design (inline constants, `_capped_side_graph` called directly because `git_diff` returns `None`); add D-7.
- **Layer A/B split:** honest. TC-RM-01 and TC-RM-02 are named Layer A; 7 of 8 gap kinds are formatter-evidence only (`format_structure`); the K3/K4 causes are Layer A.

## Evidence checklist (qa-reviewer)

- [x] Mode declared: plan.
- [x] Acceptance criteria Given/When/Then: ✓ §5.3 (X-1 is an oracle error in one arm).
- [x] Explicit Expected, edge cases empty/boundary/invalid/error: ✓.
- [x] Regression checklist: ✓ reverse census (D-6 corrects counts).
- [x] Exit criteria stated: ✓.
- [x] No real PII or secrets: ✓.
- [ ] Layer B negative controls able to flip: ⚠ X-1 (half of AT-122 arm 3), N-3 residual.
- [ ] Mutant per LLR killed by the named test: ⚠ D-1, D-3 (M-RMG-5, M-RMM-10, M-RML-8).
- [x] Bidirectional surface reachability: ✓.
- [x] No unfilled placeholders in the PDR proposal; PDR record rows are `⚠ pending review` by design.
