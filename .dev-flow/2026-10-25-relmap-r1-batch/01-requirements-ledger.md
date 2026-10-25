# Requirements ledger — mapper — Batch 2026-10-25-relmap-r1-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

### LED-2026-10-25-relmap-r1-batch.1 — the prescan extraction is pinned by a byte-identity golden captured on the base
- **Requirement:** HLR-RML.1, LLR-RML.1.4
- **Date:** 2026-10-25
- **What changed:** LLR-RML.1.4 no longer claims that `tests/test_ingestion_limits.py` asserts today's strings; it requires a golden of 4 refusals x 2 call sites (8 exact strings) captured on the base commit before the move, RED when one refusal is reworded.
- **Why:** P2 findings Q-1 (BLOCKER) and A-1: the existing suite asserts substrings only and the diff-side arms assert `None`, so byte-identity — the whole mitigation of the highest-census edit — was pinned by nothing. Orchestrator ruling R1.
- **Asserting test:** `tests/test_prescan_refusal_goldens.py` (NEW, Inc-3, lands before the move)
- **Mutant:** M-RML-6 (`{shown!r}` -> `{shown}`): golden RED, `tests/test_ingestion_limits.py` GREEN
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.2 — the gap catalogue is data in the profile
- **Requirement:** HLR-RMP.1, LLR-RMP.1.1, LLR-RMP.1.2, LLR-RMG.1.1
- **Date:** 2026-10-25
- **What changed:** HLR-RMP.1 and LLR-RMP.1.1 now include the eight-row gap catalogue (severity, closed pattern, needed kinds, sentence template) as profile data; LLR-RMG.1.1 makes the detectors generic over it; LLR-RMP.1.2 extends the no-literal census to gap kinds (set >= 17).
- **Why:** P2 finding A-2: HLR-RMP.1 listed kinds and edge types only while LLR-RMP.1.2 forbade kind/edge literals in `gaps.py`, which the catalogue necessarily names — a contradiction. Ruling R2.
- **Asserting test:** `tests/test_relmap_profile.py::test_catalogue_table`, `tests/test_relmap_isolation.py::test_engine_names_no_kind`
- **Mutant:** M-RMP-1 (hard-code `"refines"` in `gaps.py`) RED; M-RMP-5 (change a catalogue severity) RED
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.3 — a gap caused by the adapter's own unparsed or unlinked rows is reported but qualified
- **Requirement:** HLR-RMG.1, LLR-RMG.1.1, LLR-RMG.1.2, LLR-RMM.1.1, LLR-RMA.1.3, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** `Node.unparsed` added; the adapter counts the orphan rows related to each HLR (starts-with branch and shared-stem branch); `lacks_*` gap sentences end `(<n> canon rows unparsed under this id)`; the live expectation is restated as 7 gaps of which `HLR-CAN.1` and `HLR-REPAIR.1` carry the qualifier (2 rows each).
- **Why:** P2 findings Q-3 and A-3: `HLR-CAN.1` has only the two unparsed LLRs `LLR-CAN.1.1/.2` and `HLR-REPAIR.1` pairs with the unlinked `LLR-REPAIR.1`, so two of the seven gaps were artefacts of the adapter's own limits, against the honest-partial-map principle. Ruling R3.
- **Asserting test:** `tests/test_relmap_gaps.py::test_gap_sentence_qualified`, `tests/test_relmap_adapter.py::test_unparsed_counts`, AT-125
- **Mutant:** M-RMG-4 (drop the qualifier) RED; M-RMA-5 (starts-with branch only) RED on the `HLR-REPAIR.1` arm
- **Evidence:** `evidence/p2-amendment-probe-2026-10-25.txt`: the rule run over the live canon gives 7 gaps, qualified 2 (`HLR-CAN.1`: LLR-CAN.1.1, LLR-CAN.1.2; `HLR-REPAIR.1`: LLR-REPAIR.1, LLR-REPAIR.2), five plain

### LED-2026-10-25-relmap-r1-batch.4 — exact figures move to a frozen snapshot; the live canon gets invariants
- **Requirement:** HLR-RMA.1, LLR-RMA.1.1, LLR-RMA.1.2, LLR-RMA.1.3, LLR-RMG.1.2, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** 275/196/7/3/7-gaps are asserted only against `tests/fixtures/relmap/REQUIREMENTS.snapshot.md`; the live `REQUIREMENTS.md` is checked by invariants against an independent line counter and its figures are recorded as evidence, never pinned.
- **Why:** P2 finding A-4: pinning absolute counts of a living file makes the oracle go red on the next unrelated canon edit and invites retyping numbers, which is vacuous. Ruling R4.
- **Asserting test:** `tests/test_relmap_adapter.py::test_snapshot_census`, `::test_live_invariants`, `tests/test_relmap_audit.py::test_snapshot_run`
- **Mutant:** M-RMA-1 (resolve an unlinked LLR to the nearest prefix) RED on the snapshot; M-RMA-6 (skip the last table row) RED on the live invariant
- **Evidence:** snapshot source: `REQUIREMENTS.md` at the P1 base, sha256 93b18472c40fac24ec818bbe1b2808d66d16c021bf2f9234dfee5a1083c44cc7

### LED-2026-10-25-relmap-r1-batch.5 — every file the relation map reads is read through lstat and the capped reader; discovery is capped
- **Requirement:** HLR-RML.1, LLR-RML.1.1, LLR-RML.1.2, LLR-RML.1.5, LLR-RML.1.6, LLR-RMA.1.1, LLR-RMP.2.1
- **Date:** 2026-10-25
- **What changed:** New LLR-RML.1.5 (`read_repo_text`: lstat, refuse link/reparse/non-regular, then `osopen.read_capped`) is the only reader for the canon and every descriptor; the adapter no longer calls `load_canon`; new LLR-RML.1.6 caps discovery at 8 sorted descriptors with one overflow line and derives the canon once per run; the relmap osopen name list gains `is_link`.
- **Why:** P2 findings F1, F3 (security MAJOR), A-5, Q-12: `load_canon` reads the whole file before its size check and does no link or special-file check, and a discovered descriptor was read without confinement; N descriptors multiplied the work. Ruling R5.
- **Asserting test:** `tests/test_relmap_descriptor.py::test_read_repo_text_*`, `::test_repo_root_census`, `::test_canon_derived_once`, AT-121, AT-127
- **Mutant:** M-RML-7 (skip lstat) RED; M-RML-8 (read before the size check) RED; M-RML-9 (derive per descriptor) RED; M-RML-13 (no count cap) RED
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.6 — refusal and unavailable causes come from a closed set of fixed strings
- **Requirement:** HLR-RML.1, LLR-RML.1.1, LLR-RML.1.2, LLR-RML.1.3, LLR-RML.1.5, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** K1-K17 are the only causes a `refused` or `unavailable (canon: ...)` line may print; every YAML failure (YAMLError incl. ConstructorError and ComposerError, ValueError, RecursionError) is `not valid YAML`; `profile`/`kind`/`source` type errors map to their own causes, never raise; the path refusal is K17 with a closed reason and a UNC string causes no `stat`.
- **Why:** P2 findings F2, F5, F8, A-12(b), Q-8: `load_canon` text embeds the OS error string with the absolute path, and a YAML error embeds a source snippet; `profile: [x]` raised TypeError. Ruling R6.
- **Asserting test:** `tests/test_relmap_descriptor.py::test_closed_cause_set`, `::test_schema_table`, AT-121, AT-126
- **Mutant:** M-RML-10 (format `str(exc)` on a parse failure) RED; M-RML-11 (`profile` compared without a type check) RED
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.7 — repository-derived values are cut to 120 characters before escaping; the sentence template and note lines are pinned
- **Requirement:** HLR-RMU.1, LLR-RMP.1.1, LLR-RMU.1.2, LLR-RMU.1.3
- **Date:** 2026-10-25
- **What changed:** `DISPLAY_MAX` = 120 with the `…` marker applies to every printed repository value before the escaper; the gap sentence template is a column of the catalogue; note lines are capped at 10 plus an overflow line; the line formats live in a pure `format_structure` (Q-10: the formatting of HIGH, LOW and reach > 0 is otherwise untestable), with `structure_lines` a thin wrapper.
- **Why:** P2 findings F4, Q-16 and Q-10: the escaper is correct but unbounded, and an id or descriptor string could print megabytes; `<sentence>` had no required form. Ruling R7.
- **Asserting test:** `tests/test_relmap_audit.py::test_line_formats`, AT-129
- **Mutant:** M-RMU-5 (skip the cut) RED; M-RMU-3 (no gap cap) RED
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.8 — reach is iterative, memoised, computed for the gaps that can be printed, and bounded
- **Requirement:** LLR-RMM.2.2, LLR-RMG.1.3
- **Date:** 2026-10-25
- **What changed:** `reach` and `neighbourhood` are iterative; ranking computes reach once per node, once per cycle component, only for the severity bands needed to fill the printed list, under a 2,000,000-visit bound (uncomputed gaps rank with reach 0 and are counted); cap-size arms added.
- **Why:** P2 findings F6 and A-14(e): one BFS per gap candidate is O(gaps x (V+E)); at the 100,000 caps that is a hang. Ruling R8. Author's addition: the visit bound, without which the time bound the ruling asks for would not hold on a hub shape.
- **Asserting test:** `tests/test_relmap_model.py::test_reach_chain_at_cap`, `tests/test_relmap_gaps.py::test_rank_visit_cap`, `::test_rank_100k_sinks`
- **Mutant:** M-RMM-8 (recursive reach) RED; M-RMG-5 (no visit bound) RED
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.9 — builder problems and excluded rows are counted on one line
- **Requirement:** HLR-RMM.1, LLR-RMM.1.2, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** A `structure: notes excluded=<T> (<kind>=<n>, ...) unknown_status=<u> reach_not_computed=<r>` line reports the six problem kinds by count, unsafe-id rows included, never a value; `nodes + excluded = parsed rows`.
- **Why:** P2 findings Q-6, F7, A-12(a): problems were recorded but never observable, so a dropped row shifted the counts silently. Ruling R9.
- **Asserting test:** AT-124, `tests/test_relmap_audit.py::test_line_formats`
- **Mutant:** M-RMU-7 (drop the count line) RED; M-RMM-1 (drop the pair check) RED
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.10 — the acceptance tests get full bodies and a two-way matrix
- **Requirement:** HLR-RMP.1, HLR-RMM.1, HLR-RMG.1, HLR-RML.1, HLR-RMA.1, HLR-RMU.1
- **Date:** 2026-10-25
- **What changed:** §5.3 gives each AT a Given/When/Then, observation method and negative control, one AT per observable claim (AT-117 narrowed to the summary line; AT-124..AT-129 added); §5.4 is the US/HLR/LLR<->AT matrix marking the Layer-A-only HLRs; the HLR Acceptance blocks cite the new sets.
- **Why:** P2 findings Q-2 and Q-15: the ATs existed only as ids, AT-117 was shared by four HLRs, and the reverse chain could not be checked. Ruling R10.
- **Asserting test:** §5.3 rows (each AT is its own test), the matrix is checked by `V10`/`V21`
- **Mutant:** per AT, the mutant named in its §5.3 row
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.11 — the raising-callable arm and AT-123 move to Layer A; the exit-code arm needs an exit-0 baseline
- **Requirement:** HLR-RMP.2, HLR-RMU.1, LLR-RMU.1.1
- **Date:** 2026-10-25
- **What changed:** AT-123 is retired as an AT and becomes TC-RM-01; the raising callable is TC-RM-02 (`run_cli(argv, extra_lines=raiser)`); AT-120 asserts its exit-0 precondition.
- **Why:** P2 findings Q-4, A-6, Q-14: no shipped input makes `structure_lines` raise, `MapStore.load` is not a shipped surface, and 'exit unchanged' is vacuous if every fixture already exits 1. Ruling R11.
- **Asserting test:** `tests/test_relmap_audit.py::test_tc_rm_02_raising_callable`, TC-RM-01 in `tests/test_relmap_isolation.py`, AT-120
- **Mutant:** M-RMU-2 RED on TC-RM-02; M-RMP-4 RED on TC-RM-01
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.12 — the hostile arm targets what the escaper actually catches
- **Requirement:** HLR-RMU.1, LLR-RMU.1.3
- **Date:** 2026-10-25
- **What changed:** AT-122 arms are: an id with U+0301, an id with U+FE0F, ESC and U+2028 inside a statement, a descriptor base name with U+0301; bidi/ESC/U+2028/NBSP ids are excluded upstream as `unsafe id` and counted (AT-124).
- **Why:** P2 finding Q-5 (executed: those characters are `isprintable() == False`, so they never reach the escaper as an id and the AT would have passed on a raw print). Ruling R12.
- **Asserting test:** AT-122 (four arms), `tests/test_relmap_audit.py::test_escaped_and_no_forged_verdict`
- **Mutant:** M-RMU-1 (print raw), each arm RED alone
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.13 — every boundary outcome is defined; the hook and output rules are stated
- **Requirement:** HLR-RMP.1, HLR-RMM.1, HLR-RMG.1, HLR-RML.1, HLR-RMA.1, HLR-RMU.1, LLR-RMM.1.1, LLR-RMG.1.2, LLR-RML.1.1, LLR-RML.1.2, LLR-RML.1.6, LLR-RMA.1.1, LLR-RMU.1.1, LLR-RMU.1.2, LLR-RMU.1.4
- **Date:** 2026-10-25
- **What changed:** Defined: withdrawn-only HLR (not a gap), empty canon (`nodes=0`), unknown/empty/capitalised status, `profile: [x]`, big integers and multi-document streams (K10), `source` not a mapping (K15), cap-1 as comment-padded valid YAML, refusal causes counted once (17), Node/Edge fields and defaults, root = `report.repo`, no-repo and no-registry one fixed line, byte-stable output (LLR-RMU.1.4, new), zero-count kinds omitted (the HLR-RMP.1 vs LLR-RMU.1.2 contradiction removed).
- **Why:** P2 findings Q-7, Q-8, Q-9, Q-11, Q-13, A-13, A-14. Ruling R13.
- **Asserting test:** `test_withdrawn_only_llr_is_not_a_gap`, `test_status_words`, `test_schema_table`, `test_value_defaults`, AT-124, AT-126, AT-128
- **Mutant:** M-RMG-6, M-RML-11, M-RMU-4, M-RMU-6
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.14 — the one-definition claim of R-017 names the third copy; its fold-in is a backlog row
- **Requirement:** LLR-RML.1.4
- **Date:** 2026-10-25
- **What changed:** ARCHITECTURE R-017 now records that `reqharness/config.py` keeps its own prescan and why relmap does not reuse it; BACKLOG B-144 carries its fold into the leaf. No requirement text moves beyond the out-of-scope line of LLR-RML.1.4.
- **Why:** P2 finding A-7. Ruling R14: do not widen this batch.
- **Asserting test:** inspection of `docs/ARCHITECTURE.md` R-017 and `.dev-flow/BACKLOG.md` B-144 (`n/a` mutant: documentation); `tests/test_repair_map_truth.py` stays green
- **Mutant:** n/a — inspection
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.15 — yamlscan owns the anchor display and the error type; the MAX_DEPTH importer is named
- **Requirement:** LLR-RML.1.4, LLR-RMP.2.1
- **Date:** 2026-10-25
- **What changed:** `yamlscan` defines `ANCHOR_NAME_DISPLAY`, imports `MAX_DEPTH` (so `store.py` drops it and the allow-list entry), raises `YamlLimitError(Exception)` (not a ValueError) with `kind`, `shown`, `limit`; `store` converts it inside the existing `try` with byte-identical text.
- **Why:** P2 finding A-8: an ambiguous owner of the truncation constant and a `ValueError`-derived error would be rewritten to `unreadable` by the store's net. Ruling R15.
- **Asserting test:** `tests/test_yamlscan.py::test_limit_error_is_not_valueerror`, `tests/test_arch_osopen_callers.py`, the Inc-3 golden
- **Mutant:** M-RML-12 (`YamlLimitError` derives `ValueError`) RED on the golden
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.16 — census wording corrected; importer entries land with their increment; no re-exports; 3.10 declared not-run
- **Requirement:** HLR-RMP.2, LLR-RMP.2.1, LLR-RMM.1.1, LLR-RMU.1.1
- **Date:** 2026-10-25
- **What changed:** Premise 9 and LLR-RMU.1.1 name the real A3 pin (`tests/test_a3_census.py:329`, ARG-FUL `.render(` calls) and the staging precondition; the osopen allow-list and both ARCHITECTURE osopen rows are amended in the increment that adds each importer (Inc-1 `relmap/model.py`, Inc-3 `yamlscan.py` and `relmap/descriptor.py`); `relmap/__init__.py` re-exports nothing; the real 3.10 run is `not-run` with a banned-stdlib-name census beside the AST floor.
- **Why:** P2 findings A-9, A-10, A-15, A-11. Ruling R16.
- **Asserting test:** `tests/test_arch_osopen_callers.py` (each increment), `tests/test_relmap_isolation.py::test_py310_floor`, `tests/test_a3_census.py` (pin unmoved)
- **Mutant:** M-RMP-6 (importer without its allow-list entry) RED; M-RMM-7 (`import tomllib`) RED
- **Evidence:** P2 reviews `evidence/p2-architect.md`, `p2-qa.md`, `p2-security.md`; orchestrator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.17 — AT-124 and the escaper arms use U+200B, not NBSP; parsed rows are defined
- **Requirement:** LLR-RMM.1.2, LLR-RMU.1.2, LLR-RMU.1.3
- **Date:** 2026-10-25
- **What changed:** An NBSP id fails `_ROW_ID_RE` and is skipped silently by `parse_canon`; the unsafe-id examples are now U+202E and U+200B (both `\S`, both unprintable); the NBSP row is stated as silently skipped, not an R1 gap; "parsed rows" = the objects `parse_canon` returned; AT-124 expects `excluded=3 (duplicate id=1, unsafe id=2) unknown_status=1`.
- **Why:** Second-pass qa N-1 (MAJOR, executed: the regex rejects NBSP and accepts U+202E), superseding the NBSP wording of entry .12.
- **Asserting test:** AT-124, `tests/test_relmap_model.py::test_problem_*`, `tests/test_relmap_audit.py::test_escaped_and_no_forged_verdict`
- **Mutant:** M-RMM-1 and M-RMU-7 RED on AT-124; M-RMU-1 RED per arm
- **Evidence:** second-pass review `evidence/p2-qa-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.18 — reported rows print as id-only notes, one per row, under the note cap
- **Requirement:** LLR-RMA.1.3, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** Each reported row is one note `unparsed row <id>` (id cut to 120; `unparsed canon line` when no id); the note table lists the order (reported rows, unlinked line, sources, ignored keys), the cap of 10 and the overflow rule; snapshot prints 7 + 1 = 8 of 10; AT-119 expects those 8 lines.
- **Why:** Second-pass qa N-2 (MAJOR): the note table said one count line while LLR-RMA.1.3 and AT-119 expected one note per row.
- **Asserting test:** AT-119, `tests/test_relmap_adapter.py::test_reported_rows_are_notes`, `tests/test_relmap_audit.py::test_line_formats`
- **Mutant:** M-RMA-3 RED; M-RMU-3 style cap mutant: a note cap of 11 turns the 11-note arm RED
- **Evidence:** second-pass review `evidence/p2-qa-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.19 — AT-128 runs four seeds with a mutant that can flip
- **Requirement:** LLR-RMU.1.4, HLR-RMU.1
- **Date:** 2026-10-25
- **What changed:** Seeds 0..3; M-RMU-6 builds the output lists by iterating a set of the 17 profile names.
- **Why:** Second-pass qa N-3 (MINOR): two kinds and two seeds coincide half the time, so the mutant could survive.
- **Asserting test:** AT-128, `tests/test_relmap_audit.py::test_byte_stable`
- **Mutant:** M-RMU-6 RED
- **Evidence:** second-pass review `evidence/p2-qa-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.20 — AT-121 coverage, AT-117/AT-120/AT-129 controls and fixtures
- **Requirement:** HLR-RML.1, HLR-RMU.1, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** AT-121 covers K1, K2, K5-K17 and `a: [`; K3/K4 are Layer A. AT-117's controls are M-RMA-1 and M-RMA-6; AT-120's is M-RMU-8 (also in HLR-RMU.1's negative control); AT-129 drives four accepted surfaces (1 MiB ignored key, 255-character `us_canon`, 5,000-character statement, 200-character id).
- **Why:** Second-pass qa N-4 and N-5 (MINOR); executed probe: `confine_reason` accepts 255 characters and refuses 300 (`unreadable`), so a 1 MiB `us_canon` would never be printed.
- **Asserting test:** AT-121, AT-117, AT-120, AT-129
- **Mutant:** M-RMA-1, M-RMA-6, M-RMU-8, M-RMU-5 each RED on their AT
- **Evidence:** second-pass review `evidence/p2-qa-pass2.md`; coordinator rulings of 2026-10-25; probe: `confine_reason` over lengths 50..1,000,000 on a tmp workspace

### LED-2026-10-25-relmap-r1-batch.21 — descriptor failures in the prescan are K10 too
- **Requirement:** LLR-RML.1.1
- **Date:** 2026-10-25
- **What changed:** K10 covers `yaml.YAMLError`, `ValueError` and `RecursionError` from the prescan AND `safe_load`; `YamlLimitError` anchor is K8 and depth K9; a `a: [` arm.
- **Why:** Second-pass qa N-6 (MINOR): the prescan runs first and its `YAMLError` was not named in the descriptor's net.
- **Asserting test:** `tests/test_relmap_descriptor.py` (`a: [` arm), AT-121
- **Mutant:** M-RML-10 and a net that omits the prescan call (M-RML-15) RED on the `a: [` arm
- **Evidence:** second-pass review `evidence/p2-qa-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.22 — the snapshot fixture lands in Inc-4 with a digest test
- **Requirement:** LLR-RMA.1.1
- **Date:** 2026-10-25
- **What changed:** `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` is created in Inc-4; `test_snapshot_sha256` pins the digest recorded in entry .4.
- **Why:** Second-pass qa N-7 (MINOR): every exact oracle depends on one file that a quiet edit could change.
- **Asserting test:** `tests/test_relmap_adapter.py::test_snapshot_sha256`
- **Mutant:** M-RMA-7 (append a byte to the fixture) RED
- **Evidence:** second-pass review `evidence/p2-qa-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.23 — the qualifier says unparsed or unlinked; a report-line tripwire
- **Requirement:** LLR-RMG.1.1, LLR-RMG.1.2, LLR-RMA.1.3
- **Date:** 2026-10-25
- **What changed:** The sentence qualifier is now ` (<n> canon rows unparsed or unlinked near this id)` everywhere; `test_report_line_shape_yields_id` fails loudly if `derive.py` rewords `cannot parse row for '<id>'`.
- **Why:** Second-pass architect N-1 (MINOR): `LLR-REPAIR.1/.2` are parsed, so "unparsed" was false for them; a rewording in `derive.py` would silently zero `unparsed`.
- **Asserting test:** `tests/test_relmap_gaps.py::test_gap_sentence_qualified`, `tests/test_relmap_adapter.py::test_report_line_shape_yields_id`, AT-125
- **Mutant:** M-RMG-4 RED; M-RMA-8 (change the id regex in the adapter) RED on the tripwire
- **Evidence:** second-pass review `evidence/p2-architect-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.24 — the canon-link divergence from the review report is deliberate
- **Requirement:** LLR-RMA.1.1
- **Date:** 2026-10-25
- **What changed:** LLR-RMA.1.1 states that the relmap canon reader is stricter than `derive.load_canon` by design; the ARCHITECTURE `relmap` row records it.
- **Why:** Second-pass architect N-2 (MINOR).
- **Asserting test:** inspection of LLR-RMA.1.1 and `docs/ARCHITECTURE.md`; `tests/test_relmap_adapter.py::test_canon_causes` (K1 arm)
- **Mutant:** n/a — documentation; M-RML-7 covers the behaviour
- **Evidence:** second-pass review `evidence/p2-architect-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.25 — the 3.10 banned-name census is keyed on qualified names
- **Requirement:** LLR-RMM.1.1
- **Date:** 2026-10-25
- **What changed:** The census lists `enum.StrEnum`, `typing.Self`, `typing.assert_never`, `typing.LiteralString`, `tomllib`, `ExceptionGroup`, `itertools.batched`, `datetime.UTC`, `pathlib.Path.walk` and allows `os.walk`.
- **Why:** Second-pass architect N-3 (MINOR): bare `walk` would flag a valid 3.10 call.
- **Asserting test:** `tests/test_relmap_isolation.py::test_py310_floor` (including an `os.walk` allowed arm)
- **Mutant:** M-RMM-7 RED; M-RMM-9 (flag bare `walk`) RED on the allowed arm
- **Evidence:** second-pass review `evidence/p2-architect-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.26 — read_repo_text compares the opened file's identity with the lstat result
- **Requirement:** LLR-RML.1.5
- **Date:** 2026-10-25
- **What changed:** Open once read-only (`O_NONBLOCK` where present), compare `os.fstat` `st_dev`/`st_ino` and type with the `lstat` result (mismatch is K2), then `read_capped`; the remaining window is stated as accepted.
- **Why:** Second-pass security N1 (LOW).
- **Asserting test:** `tests/test_relmap_descriptor.py::test_read_repo_text_identity_mismatch`
- **Mutant:** M-RML-14 (skip the comparison) RED
- **Evidence:** second-pass review `evidence/p2-security-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.27 — the sources line prints the configured string, never the resolved path
- **Requirement:** LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** `us_canon`/`at_table` print as written in the descriptor (cut and escaped); `~/x` is refused as K17 (outside) and prints no home path (probed: `confine_reason('~/x', ws)` returns `outside`).
- **Why:** Second-pass security N2 (LOW): the resolved `Path` carries the absolute repository path.
- **Asserting test:** `tests/test_relmap_audit.py::test_byte_stable` (Layer B: the `beta` descriptor's sources line equals the configured strings and the repository's absolute path is absent from the block; added by the Inc-5 review F1) and `test_sources_line_configured_string` (formatter)
- **Mutant:** M-RMU-9 (print the resolved path) RED
- **Evidence:** second-pass review `evidence/p2-security-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.28 — the reach memo stores counts, not sets
- **Requirement:** LLR-RMM.2.2, LLR-RMG.1.3
- **Date:** 2026-10-25
- **What changed:** Memo values are integers per node or component; `test_reach_chain_at_cap` asserts it.
- **Why:** Second-pass security N3 (LOW): per-node reachable sets are O(n squared) memory on a 100,000 chain.
- **Asserting test:** `tests/test_relmap_model.py::test_reach_chain_at_cap`
- **Mutant:** M-RMM-10 (cache the reachable set) RED
- **Evidence:** second-pass review `evidence/p2-security-pass2.md`; coordinator rulings of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.29 — AT-122 arm 3 reaches the escaper; U+2028 moves to a surface that can carry it
- **Requirement:** LLR-RMM.1.2, LLR-RMU.1.3, HLR-RMU.1
- **Date:** 2026-10-25
- **What changed:** AT-122 has five arms: id with U+0301, id with U+FE0F, a statement with ESC and U+202E on an active HLR with no LLR (it reaches the gap sentence), a descriptor base name with U+0301, and a descriptor top-level ignored key NAMED `"\u2028verdict: ready"` (YAML double-quoted; the printed item is the key name, so the carrier is the key, not its value). A Layer A arm drives `run_cli` in-process with a hook returning `format_structure` over a synthetic map whose gap title carries U+2028 and `verdict: ready`. LLR-RMM.1.2's boundary wording now says: U+2028 in a canon id makes a reported row (`parse_canon` uses `splitlines()`), as a builder input it is `unsafe id`; ESC, U+202E and U+200B ids reach the builder through the canon and are `unsafe id`.
- **Why:** P2 third-pass QA X-1 (MAJOR): executed against `parse_canon`, a statement with U+2028 splits the row, so it never becomes a node and no title carries the character; the U+2028 half of arm 3 passed whatever the escaper did and M-RMU-1 could not turn it RED.
- **Asserting test:** AT-122, `tests/test_relmap_audit.py::test_escaped_and_no_forged_verdict` (five arms plus the Layer A arm), `tests/test_relmap_model.py::test_problem_*` (U+2028-id builder arm)
- **Mutant:** M-RMU-1 (print raw) RED on each arm alone, including the ignored-key arm and the Layer A arm
- **Evidence:** `evidence/p2-qa-pass3-and-pdr-qa.md` X-1; orchestrator ruling of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.30 — AT-128 runs two pre-picked seeds proven by a recorded probe
- **Requirement:** LLR-RMU.1.4, HLR-RMU.1
- **Date:** 2026-10-25
- **What changed:** AT-128 runs `PYTHONHASHSEED=0` and `PYTHONHASHSEED=2` and compares the two stdout byte strings. The probe (`evidence/p2-closure-probe-2026-10-25.txt`, Python 3.12.7) iterates a set of the 17 profile names under seeds 0..7: seed 0 gives `LLR` before `HLR`, seed 2 gives `HLR` before `LLR` (the only relative order visible in the output, since the edge type and the gap kind present are single). The Inc-5 packet re-proves the pair by running M-RMU-6 for real and recording that the two stdout byte strings differ; if the real mutant's set construction orders them alike, the seeds are re-picked and re-recorded before the AT is accepted.
- **Why:** P2 third-pass QA N-3 (MINOR, reopened): with four seeds and two visible orderings the mutant survived one run in eight.
- **Asserting test:** AT-128, `tests/test_relmap_audit.py::test_byte_stable`
- **Mutant:** M-RMU-6 RED (the pair differs by probe, not by chance)
- **Evidence:** `evidence/p2-qa-pass3-and-pdr-qa.md` N-3; `evidence/p2-closure-probe-2026-10-25.txt`

### LED-2026-10-25-relmap-r1-batch.31 — M-RML-15 and M-RMA-7 are named in their LLR negative-control lines
- **Requirement:** LLR-RML.1.1, LLR-RMA.1.1
- **Date:** 2026-10-25
- **What changed:** LLR-RML.1.1's negative control lists M-RML-15 (a net that omits the prescan call → the `a: [` arm RED); LLR-RMA.1.1's lists M-RMA-7 (append a byte to the fixture → `test_snapshot_sha256` RED).
- **Why:** P2 third-pass QA N-7 (nit): the two mutants lived only in the ledger and the proposal.
- **Asserting test:** `tests/test_relmap_descriptor.py` (`a: [` arm), `tests/test_relmap_adapter.py::test_snapshot_sha256`
- **Mutant:** M-RML-15, M-RMA-7 RED
- **Evidence:** `evidence/p2-qa-pass3-and-pdr-qa.md` N-7

### LED-2026-10-25-relmap-r1-batch.32 — the ceiling mutants are killed by a deterministic visit counter, not by elapsed time or memory
- **Requirement:** LLR-RMM.2.2, LLR-RMG.1.3
- **Date:** 2026-10-25
- **What changed:** Every reach traversal reads adjacency through `RelMap.down` (the single counted seam). `test_rank_visit_cap` and `test_reach_budget_per_row` install a counting wrapper on `RelMap.down` that raises an `AssertionError` tripwire at `VISIT_BUDGET + 1` calls, and assert `RelMap.visits <= 2,000,000` and, on the hub shape, `reach_not_computed > 0`. M-RMM-10 (cache the reachable set) is killed by `test_reach_memo_is_counts` on a 2,000-node chain (every memo value is an `int`); the 100,000-node chain stays only for the no-`RecursionError` arm. A 30 s test timeout may exist as a last resort and is never an assertion.
- **Why:** PDR QA D-1 (MAJOR): on the 50,000-gap hub shape the no-bound mutant makes about 2.5×10^9 visits and an elapsed-time assertion only fires after it returns; the cached-set mutant on a 100,000 chain holds about 5×10^9 elements.
- **Asserting test:** `tests/test_relmap_gaps.py::test_rank_visit_cap`, `tests/test_relmap_model.py::test_reach_memo_is_counts`, `::test_reach_budget_per_row`
- **Mutant:** M-RMG-5 RED (tripwire after about two million calls), M-RMM-10 RED (memo type), no elapsed-time or out-of-memory kill
- **Evidence:** `evidence/p2-qa-pass3-and-pdr-qa.md` D-1; orchestrator ruling of 2026-10-25

### LED-2026-10-25-relmap-r1-batch.33 — two tests move to the increment that contains their subject
- **Requirement:** LLR-RMG.1.2, LLR-RML.1.6, LLR-RMU.1.4
- **Date:** 2026-10-25
- **What changed:** `test_snapshot_gaps` moves to Inc-4 (`tests/test_relmap_adapter.py`: it needs the adapter and the snapshot fixture); `test_canon_derived_once` moves to Inc-5 (`tests/test_relmap_audit.py`: it runs through `structure_lines`). Chosen over synthetic stand-ins: a stand-in would assert something else. M-RMG-3 keeps its synthetic kill `test_unsourced_kind_is_silent` at Inc-2; M-RML-9 is killed at Inc-5.
- **Why:** PDR QA D-2 (MAJOR): neither test could be written green at the exit of the increment that listed it.
- **Asserting test:** `tests/test_relmap_adapter.py::test_snapshot_gaps`, `tests/test_relmap_audit.py::test_canon_derived_once`
- **Mutant:** M-RMG-3 (Inc-2 synthetic arm and Inc-4 snapshot arm), M-RML-9 (Inc-5) RED
- **Evidence:** `evidence/p2-qa-pass3-and-pdr-qa.md` D-2

### LED-2026-10-25-relmap-r1-batch.34 — the cap+1 arm instruments the bytes read
- **Requirement:** LLR-RML.1.5
- **Date:** 2026-10-25
- **What changed:** The `test_read_repo_text_*` cap+1 arm wraps the file object (or monkeypatches `open`) to record the bytes requested and asserts at most `cap + 1`.
- **Why:** PDR QA D-3 (MAJOR): a mutant that reads the whole file and then compares raises the same K5 text for the same input, so M-RML-8 survived the result-only arm.
- **Asserting test:** `tests/test_relmap_descriptor.py::test_read_repo_text_*` (cap+1 arm, bytes-read assertion)
- **Mutant:** M-RML-8 RED on the bytes-read assertion, not on the K5 result
- **Evidence:** `evidence/p2-qa-pass3-and-pdr-qa.md` D-3

### LED-2026-10-25-relmap-r1-batch.35 — Layer B phasing, shared fixture builder, census, golden provenance, junction arm, wall time
- **Requirement:** LLR-RML.1.4, LLR-RML.1.5, LLR-RMU.1.1, HLR-RMU.1
- **Date:** 2026-10-25
- **What changed:** (D-4) Layer B ATs first run at Inc-5; Inc-3 and Inc-4 carry in-process Layer A stand-ins that already assert the figures the ATs will check (descriptor causes with their K5/K16/K17 wording at Inc-3; snapshot census, notes and gaps through `derive_reqharness_map` at Inc-4). (D-5) `tests/_relmap_fixtures.py` (Inc-5) IMPORTS `_seed`, `_git_repo`, `_write_canon`, `_audit_cli` from `tests.test_reqharness_release` (the repo already imports across test modules at `tests/test_reqharness_release.py:31`) and adds only relmap wrappers; `test_reqharness_release.py` is not edited. (D-6) the reverse census counts 16 `--audit` subprocess sites, 10 printing the block, 6 refused before the hook (lines in the proposal §5.2). (D-7) the 8 golden constants are generated by running the base code; the packet records the capture command and the base SHA; the golden is committed alone before the `store.py` edit. (D-8) the K1 arm on Windows uses a directory junction (`mklink /J`); `blocked` only if even that cannot be created. (D-9) heavy arms are separate functions and each increment packet records measured wall time, budget about one minute for `test_relmap_audit.py`.
- **Why:** PDR QA D-4 to D-9 (MINOR).
- **Asserting test:** `tests/test_prescan_refusal_goldens.py` (provenance), `tests/test_relmap_descriptor.py::test_read_repo_text_*` (junction arm), the packets' timing lines
- **Mutant:** M-RML-6 (golden), M-RML-7 (link/junction arm) RED
- **Evidence:** `evidence/p2-qa-pass3-and-pdr-qa.md` D-4..D-9

### LED-2026-10-25-relmap-r1-batch.36 — the snapshot pin hashes LF-normalised bytes; entry .4's digest is the CRLF working copy
- **Requirement:** LLR-RMA.1.1
- **Date:** 2026-10-25
- **What changed:** Correction of entry .4: `93b18472c40fac24ec818bbe1b2808d66d16c021bf2f9234dfee5a1083c44cc7` is the digest of the CRLF Windows working copy; `git show HEAD:REQUIREMENTS.md` hashes to `b093c9203f0fe75f218298f56cc723a812902a1f4979424c8c2cb931bd39a25a`, and so does the working copy after `\r\n` → `\n` (both re-executed 2026-10-25). The AUTHORITATIVE pin is the LF-normalised sha256 (`b093c920…`), asserted by `test_snapshot_sha256` and by a CRLF arm that hashes a CRLF-rewritten copy; `.gitattributes` also gets `tests/fixtures/relmap/** -text` as defence in depth (it keeps the committed bytes on disk, it does not replace the normalised hash). The 275/196/7/3 figures are unaffected (`osopen.read_capped` normalises newlines). Inc-4 exit runs `test_snapshot_sha256` from a fresh LF checkout.
- **Why:** PDR architect PD-1 (MAJOR): a committed fixture is stored LF, so a raw-byte pin of the CRLF digest would pass here and fail on any LF checkout.
- **Asserting test:** `tests/test_relmap_adapter.py::test_snapshot_sha256`, `::test_snapshot_sha256_crlf_arm`
- **Mutant:** M-RMA-7 (append a byte) RED; M-RMA-9 (hash the raw bytes) RED on the CRLF arm
- **Evidence:** `evidence/pdr-architect.md` PD-1; `git show HEAD:REQUIREMENTS.md | sha256sum` and `sha256sum` of the working copy with CRs removed, 2026-10-25

### LED-2026-10-25-relmap-r1-batch.37 — the frozen R2 API is complete: default descriptor, collection types, `limit=None`
- **Requirement:** LLR-RMM.1.1, LLR-RMM.2.2, LLR-RMG.1.3, LLR-RML.1.2
- **Date:** 2026-10-25
- **What changed:** `default_descriptor() -> Descriptor` with `Descriptor(profile="reqharness", canon="REQUIREMENTS.md", us_canon=None, at_table=None, ignored_keys=())`; `RelMap.nodes` and `.edges` are tuples in input order with `RelMap.node(id) -> Node | None`; `up` and `down` return `tuple[str, ...]` in edge input order; `neighbourhood` returns `frozenset[str]`; `rank_gaps(map, gaps, limit: int | None)` accepts `None` (all bands), still inside the visit budget.
- **Why:** PDR architect PD-2 (MAJOR): R2 must call the adapter when no descriptor exists and needs ordered, id-addressable access.
- **Asserting test:** `tests/test_relmap_descriptor.py::test_schema_table` (default row), `tests/test_relmap_model.py::test_multi_parent_and_order`, `::test_value_defaults`, `tests/test_relmap_gaps.py::test_rank_limit_none`
- **Mutant:** M-RMM-4 (sort nodes) RED; M-RML-3 stays RED on the default row
- **Evidence:** `evidence/pdr-architect.md` PD-2

### LED-2026-10-25-relmap-r1-batch.38 — what is frozen, what is a tested seam; the hook discriminator; the baseline-refusal TC; the hostile-canon census arms
- **Requirement:** LLR-RMU.1.1, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** (PD-3) frozen = `structure_lines`, `DescriptorError`, `CanonUnavailable`, `RepoReadError`, `YamlLimitError` and the R2 API of D3; `format_structure`, `refusal_line` and `CAUSE` are tested internal seams, "stable within the batch, not frozen". (PD-4) the ARCHITECTURE `relmap` row's internal-order sentence now reads `audit` → `adapter`, `gaps`, `descriptor`, `model`. (PD-5) the census adds `tests/test_reqharness_release.py:665-680` and `:755-770` (whole-stdout control-character scans with hostile canon fixtures) as free regression arms, named in the Inc-5 exit check, with an absence-of-`structure: unavailable (internal error` assertion on the happy fixtures. (PD-6) two rejected-alternative rationales reworded in the proposal. (PD-7) `run_cli` keys the fixed lines on `report.chain_status` (`identity.NO_REPO`, `reqharness.audit.NO_REGISTRY`), not on verdict text; TC-RM-03 pins that the `--baseline` refusal path prints no structure line and never calls the hook.
- **Why:** PDR architect PD-3 to PD-7 (MINOR).
- **Asserting test:** `tests/test_relmap_audit.py::test_tc_rm_03_refusal_path`, AT-126; `tests/test_reqharness_release.py` arms at 667 and 758 (unchanged files)
- **Mutant:** M-RMU-10 (hook called, or structure printed, on the baseline refusal path) RED; M-RMU-4 RED
- **Evidence:** `evidence/pdr-architect.md` PD-3..PD-7

### LED-2026-10-25-relmap-r1-batch.39 — one visit budget per RelMap, shared by `reach` and `rank_gaps`
- **Requirement:** LLR-RMM.2.2, LLR-RMG.1.3
- **Date:** 2026-10-25
- **What changed:** `RelMap` carries ONE budget (`VISIT_BUDGET = 2,000,000` node expansions over the object's lifetime, `RelMap.visits`). `reach(id)` is typed `int | None`: `None` ("not computed") when a traversal would pass the budget, never a hang and never a partial count; `rank_gaps` draws on the same budget and counts the gaps whose reach came back `None` as `reach_not_computed`. `neighbourhood` is not on the budget (O(V+E) per call; a view calls it for the focused node only). Documented in the D3 docstring and the ARCHITECTURE `relmap` row; `test_reach_budget_per_row` calls `reach` for every node of the cap shape.
- **Why:** PDR security C1 (MED): `reach` was public and unbounded, so an R2 view painting every row costs V×(V+E), the F6 hang by another door.
- **Asserting test:** `tests/test_relmap_model.py::test_reach_budget_per_row`, `tests/test_relmap_gaps.py::test_rank_visit_cap`
- **Mutant:** M-RMM-11 (`reach` bypasses the shared budget) RED on the tripwire
- **Evidence:** `evidence/pdr-security.md` C1

### LED-2026-10-25-relmap-r1-batch.40 — returned structure lines are UNESCAPED; the cut lives inside `format_structure`
- **Requirement:** LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** D5 and the ARCHITECTURE `relmap` row state that `structure_lines` and `format_structure` return repository-derived UNESCAPED lines and the sink must escape; `format_structure` performs the 120-character cut itself. Inc-5 arms: `test_format_structure_cuts_inside` (a 1 MiB id, label and sources value passed directly) and `test_refusal_line_hostile_name` (`refusal_line` directly with a U+0301 name and a 300-character name).
- **Why:** PDR security C2 (MED) and M4: the escaper is private to `reqharness.audit`, so any future caller that prints these lines bypasses it, and a cut moved into the wrapper would still pass AT-129.
- **Asserting test:** `tests/test_relmap_audit.py::test_format_structure_cuts_inside`, `::test_refusal_line_hostile_name`
- **Mutant:** M-RMU-11 (cut moved to `structure_lines`) RED; M-RMU-13 (`refusal_line` skips the cut) RED
- **Evidence:** `evidence/pdr-security.md` C2, M4

### LED-2026-10-25-relmap-r1-batch.41 — security notes M1, M2, M3, M5 folded in
- **Requirement:** LLR-RML.1.5, LLR-RML.1.1, LLR-RML.1.3, LLR-RMU.1.1
- **Date:** 2026-10-25
- **What changed:** (M1) the identity check compares `st_ino` only when both values are non-zero, with an `st_ino = 0` arm. (M2) `CAUSE` is a `types.MappingProxyType`, with a one-line test. (M3) `read_repo_text` is a file-type guard, not a confinement: the batch that first opens `us_canon`/`at_table` calls `osopen.confine_reason` again at open time, recorded beside the "never opened in R1" ban. (M5) `run_cli` consumes at most 1,000 hook lines (`itertools.islice`), printing one `structure: output truncated at 1000 lines` line when more exist.
- **Why:** PDR security M1, M2, M3, M5 (LOW).
- **Asserting test:** `tests/test_relmap_descriptor.py::test_read_repo_text_*` (`st_ino = 0` arm), `::test_cause_is_read_only`; `tests/test_relmap_audit.py::test_hook_line_bound`
- **Mutant:** M-RML-16, M-RML-17, M-RMU-12 RED
- **Evidence:** `evidence/pdr-security.md` M1, M2, M3, M5

### LED-2026-10-25-relmap-r1-batch.42 — the block says it is informational; the verdict is found by prefix; overflow lines are not rows
- **Requirement:** LLR-RMU.1.2, LLR-RMU.1.1, HLR-RMU.1
- **Date:** 2026-10-25
- **What changed:** (MAJOR-1) the first line `structure_lines` returns is `structure: informational - does not change the verdict or the exit code`. (MAJOR-2) the count line becomes `structure: skipped N canon rows (duplicate id=1, unsafe id=2); unknown status=1; reach not computed=2`, each part only when its count is above 0, the line omitted when all are 0; `structure note:` stays for note lines. (MAJOR-3) overflow lines are `structure: gaps shown X of Y (Z lowest-ranked not shown)` and `structure: notes shown X of Y (Z not shown)`, so `structure gap:` and `structure note:` stay one row per item. (MAJOR-4) the `verdict: ` line is found by prefix and is no longer the last line; stated in LLR-RMU.1.1, HLR-RMU.1, the ARCHITECTURE row and the packet. Oracles updated: AT-120 (header), AT-124 (new literal), `test_line_formats`.
- **Why:** PDR UX MAJOR-1 to MAJOR-4.
- **Asserting test:** AT-120, AT-124, `tests/test_relmap_audit.py::test_header_first`, `::test_line_formats`
- **Mutant:** M-RMU-14 (drop the header) RED; M-RMU-7 (drop the skipped-rows line) RED; M-RMU-3 (no gap cap) RED on the overflow wording
- **Evidence:** `evidence/pdr-ux.md` MAJOR-1..4

### LED-2026-10-25-relmap-r1-batch.43 — UX wording minors adopted; three documented in the proposal
- **Requirement:** LLR-RMU.1.2, LLR-RMU.1.1, LLR-RMG.1.1, LLR-RML.1.2, LLR-RML.1.3, LLR-RML.1.5
- **Date:** 2026-10-25
- **What changed:** (MINOR-1) `structure: refused (<base name>): <cause> - descriptor skipped`; K17 `unsafe path in <field> (<reason>)`; K16 `source.<key> is not text`; K5 rendered `exceeds the <N> byte limit` (N from the reader's cap, carried as `RepoReadError.limit`; the stored cause text is unchanged). (MINOR-2) the hook-failure line is `structure: unavailable (internal error: <Type>)`. (MINOR-3) the gap qualifier is `(canon rows near this id could not be parsed or linked: <n>)`; AT-125 and the M-RMG-4 oracle updated. (MINOR-5) `reach` is documented as the number of distinct nodes downstream of the node, in LLR-RMU.1.2 and the ARCHITECTURE row. (MINOR-6) `structure: descriptor (built-in default)` and `us_canon=unset at_table=unset`. (MINOR-4, 7, 8) stated in LLR-RMU.1.2's reading notes and the proposal: width not guaranteed (first 40 characters carry severity, kind and node), gap rows are for reading not parsing, worst case about 298 lines of at most 1,000 characters.
- **Why:** PDR UX MINOR-1 to MINOR-8; no kind, severity or template changed.
- **Asserting test:** AT-121, AT-125, AT-126, AT-127, `tests/test_relmap_audit.py::test_line_formats`, `tests/test_relmap_gaps.py::test_gap_sentence_qualified`
- **Mutant:** M-RMG-4 (drop the qualifier) RED; M-RML-2 (path in message) RED; M-RMU-3 RED
- **Evidence:** `evidence/pdr-ux.md` MINOR-1..8

### LED-2026-10-25-relmap-r1-batch.44 — `DISPLAY_MAX` means 120 characters in total, the last being `…`
- **Requirement:** LLR-RMU.1.2, HLR-RMU.1, LLR-RMM.1.2
- **Date:** 2026-10-25
- **What changed:** Reading recorded: a cut value is 119 characters of the original plus `…`, 120 in total (`cut` in `model.py`, as built in Inc-1). The wording "a 121-character id prints 120 characters and `…`" in LLR-RMU.1.2's numeric threshold reads as 120 characters in total, the last being `…`; Inc-5's goldens are minted on that count. Orchestrator ruling on Inc-1 packet §6 item 1.
- **Why:** AT-129 asserts "no value longer than 120 characters before escaping"; 120 + `…` would break it. Inc-1 review opinion 1 agrees.
- **Asserting test:** `tests/test_relmap_model.py::test_cut_boundary_120_and_121`; Inc-5 `test_format_structure_cuts_inside`, AT-129
- **Mutant:** M-RMU-11, M-RMU-13 RED (Inc-5); an off-by-one in `cut` (`text[:DISPLAY_MAX] + "…"`) turns `test_cut_boundary_120_and_121` RED
- **Evidence:** `03-increments/increment-001.md` §6 item 1; `evidence/review-inc001.md` opinion 1

### LED-2026-10-25-relmap-r1-batch.45 — LLR-RMM.2.2's memo arm runs on sampled rows of the 2,000-node chain
- **Requirement:** LLR-RMM.2.2
- **Date:** 2026-10-25
- **What changed:** The wording "a 2,000-node chain" is amended to "a 2,000-node chain, sampled rows" (every 7th row): `reach` for EVERY row of a 2,000-node chain costs 2,001,000 expansions, 1,000 over the shared budget, so the literal text is unsatisfiable. The arm asserts every retained memo value is an `int`.
- **Why:** Inc-1 packet §6 item 2; orchestrator ruling; the kill for a set-valued memo needs only that retained values be `int`.
- **Asserting test:** `tests/test_relmap_model.py::test_reach_memo_is_counts`
- **Mutant:** M-RMM-10 (memo stores a set) RED
- **Evidence:** `03-increments/increment-001.md` §6 item 2; `evidence/review-inc001.md` opinion 2

### LED-2026-10-25-relmap-r1-batch.46 — A stdlib-ban census for `mapper/relmap/` lands with Inc-3
- **Requirement:** LLR-RMP.2.1
- **Date:** 2026-10-25
- **What changed:** Inc-3's planned tests gain a census over `mapper/relmap/*.py` and `mapper/yamlscan.py`: no `subprocess`, no network module (`socket`, `urllib`, `http`, `ftplib`, `smtplib`, `requests`), no write-mode `open`/`Path.write_*`, with a planted-violation arm per ban. It lands with the first file-touching module (`descriptor.py`).
- **Why:** ARCHITECTURE §3 bans these for `relmap`; LLR-RMP.2.1 permits the whole standard library, so nothing enforces the ban today (Inc-1 packet §6 item 3).
- **Asserting test:** `tests/test_relmap_isolation.py::test_stdlib_bans` (Inc-3, planned)
- **Mutant:** M-RMP-7: plant `import subprocess` in a relmap module -> `test_stdlib_bans` RED (Inc-3)
- **Evidence:** `03-increments/increment-001.md` §6 item 3; `evidence/review-inc001.md` opinion 3

### LED-2026-10-25-relmap-r1-batch.47 — Silent-contract choices of Inc-1 are accepted and stated
- **Requirement:** LLR-RMM.1.2, LLR-RMM.3.1, LLR-RMP.1.1
- **Date:** 2026-10-25
- **What changed:** Stated as readings: an edge `Problem.subject` is `<src>-><dst>`; a node is a `duplicate id` only against ACCEPTED ids (an earlier node excluded for an unknown kind does not make a later same-id node a duplicate); cycles are computed on the authored `src -> dst` graph (premise 5: a DAG over the profile's pairs), members and components in node input order, a self-loop is a component of one; `Profile.__post_init__` also refuses a severity outside HIGH, MED, LOW; `RelMap._reach_memo` is a private, tested seam (renaming it fails `test_reach_memo_is_counts` loudly, not frozen).
- **Why:** Inc-1 packet §6 item 4; the reviewer judged all acceptable.
- **Asserting test:** `tests/test_relmap_model.py::test_problem_*`, `::test_cycle_*`, `::test_reach_memo_is_counts`; `tests/test_relmap_profile.py` construction refusals
- **Mutant:** M-RMM-1, M-RMM-3 RED; a profile severity of `"CRIT"` accepted (refusal dropped) turns the profile refusal arm RED
- **Evidence:** `03-increments/increment-001.md` §6 item 4; `evidence/review-inc001.md` opinion 4

### LED-2026-10-25-relmap-r1-batch.48 — Problem subjects are raw (review F1)
- **Requirement:** LLR-RMM.1.2, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** Reading: `Problem.subject` is unescaped, uncut input (an unsafe id may be empty, over 200 characters or hold control characters; an edge subject concatenates two such values). The model stores it verbatim; the formatter cuts and escapes it, and Inc-5 asserts it (`test_format_structure_cuts_inside`, `test_refusal_line_hostile_name`). Any other holder of a map (R2 strip, log) must cut and escape too.
- **Why:** Inc-1 review F1 (MINOR); orchestrator ruling.
- **Asserting test:** Inc-5 `tests/test_relmap_audit.py::test_format_structure_cuts_inside`
- **Mutant:** M-RMU-11 RED (Inc-5)
- **Evidence:** `evidence/review-inc001.md` F1

### LED-2026-10-25-relmap-r1-batch.49 — Duplicate identical edges are kept (review F3)
- **Requirement:** LLR-RMM.1.1, LLR-RMM.1.2
- **Date:** 2026-10-25
- **What changed:** Reading: two identical `(src, dst, type)` edges both stay in `edges`, `up` and `down`; `reach` and `neighbourhood` are unaffected (distinct nodes), only edge counts would double. The contract has no problem kind for it. Inc-4's deriver emits unique pairs from the canon.
- **Why:** Inc-1 review F3 (MINOR); orchestrator ruling: state it.
- **Asserting test:** none new: stated reading, Inc-4 `test_rule_d1_table` asserts unique pairs
- **Mutant:** n/a - no behaviour change
- **Evidence:** `evidence/review-inc001.md` F3

### LED-2026-10-25-relmap-r1-batch.50 — `sourced` is not intersected with the profile's node kinds (review F5)
- **Requirement:** LLR-RMM.1.1, LLR-RMG.1.2
- **Date:** 2026-10-25
- **What changed:** Reading: `build_map` keeps `frozenset(sourced)` as given; a kind name outside the profile makes no row fire (rows name profile kinds) and a typo'd real kind never appears. Inc-4 builds the set from constants. `gaps.py` activates a row only when every `needs` kind is in `map.sourced`.
- **Why:** Inc-1 review F5 (MINOR); orchestrator ruling: state it.
- **Asserting test:** none new: stated reading
- **Mutant:** n/a - no behaviour change
- **Evidence:** `evidence/review-inc001.md` F5

### LED-2026-10-25-relmap-r1-batch.51 — Inc-2 readings the contract left silent: where an evidence gap sits, what `detect_gaps` returns for reach, how sentence slots are filled
- **Requirement:** LLR-RMG.1.1, LLR-RMG.1.3
- **Date:** 2026-10-25
- **What changed:** Stated as readings (no behaviour in the contract changes): (1) an `edge_unevidenced` gap sits on the edge's `dst` (the node whose change the missing evidence leaves unchecked; QuickMap's oracle does the same), its sentence names both ends; (2) `detect_gaps` returns every `Gap` with `reach = 0`; `rank_gaps(map, gaps, limit)` replaces it for the bands it asks about, through `RelMap.reach` only, and returns ALL gaps ranked (a caller prints the first `limit`); (3) sentence slots (`<id>`, `<title>`, `<n>`, `<src>`, `<dst>`) are filled in ONE pass, so an id or title containing a slot name is never re-expanded; (4) a `lacks_*` row with a `peer` counts only edges whose other end has that kind; (5) a cycle gap sits on the component's first member in node input order and its sentence counts the component's nodes.
- **Why:** Inc-1 review item 4 / F2: ranking must use only the counted `reach` (never `down` directly); the rest are choices the contract does not state.
- **Asserting test:** `tests/test_relmap_gaps.py::test_at_tagged_only_positive_and_negative`, `::test_verifies_without_evidence_positive_and_negative`, `::test_detect_returns_reach_zero_and_does_not_spend_the_budget`, `::test_sentence_slots_are_filled_in_one_pass`, `::test_peer_kind_restricts_the_linking_edge`, `::test_cycle_gap_reach_goes_through_the_first_member`, `::test_gaps_reads_no_adjacency_itself`
- **Mutant:** M-RMG-5 (own BFS over `down`) RED; M-RMG-12 (slots filled sequentially) RED; M-RMG-13 (cycle through the last member) RED; M-RMG-14 (evidence gap on `src`) RED; M-RMG-7 (peer ignored) RED
- **Evidence:** `evidence/inc2-red-mutants-battery.txt`; `evidence/review-inc001.md` F2

### LED-2026-10-25-relmap-r1-batch.52 — Inc-2 review dispositions F1-F5 (the edge-type filter is now asserted)
- **Requirement:** LLR-RMG.1.1, LLR-RMG.1.3
- **Date:** 2026-10-25
- **What changed:** F1: two arms assert that an edge of ANOTHER type never links (an LLR whose only edge is a `refines` is still `LLR NOT VERIFIED`; an open AT whose only edge is `covers` is still `OPEN AT WITHOUT TEST`). F2: the `gaps.py` docstring states that `eligible`, `open` and the qualifier apply to `lacks_*` rows only. F3: `_fill` leaves a slot the pattern does not supply as written (`values.get(name, m.group(0))`) instead of raising `KeyError`. F4: LLR-RMG.1.3 names the real node ids `test_rank_limit_none_ranks_every_band` and `test_rank_limit_none_stays_inside_the_budget`. F5: two long docstring lines wrapped (`gaps.py` `rank_gaps`, `model.py`).
- **Why:** Inc-2 independent review (`evidence/review-inc002.md`): mutant D (drop the filter in `_lacks`) survived all 50 arms; F2-F5 non-blocking.
- **Asserting test:** `tests/test_relmap_gaps.py::test_edge_type_filter_lacks_in_other_edge_type_is_no_verifier`, `::test_edge_type_filter_lacks_out_other_edge_type_is_no_binding`, `::test_a_slot_the_pattern_does_not_supply_stays_as_text`
- **Mutant:** M-RMG-16 (mutant D: `if e.type != row.edge` -> `if e.type == "x"`) RED on the two edge-type arms; the slot arm RED on the committed `_fill` (`KeyError: 'src'`)
- **Evidence:** `evidence/inc2f-red-mutant-d.txt`, `evidence/inc2f-red-f3-base.txt`, `evidence/inc2f-green-final.txt`, `evidence/inc2f-guards.txt`

### LED-2026-10-25-relmap-r1-batch.53 — M-RML-6 is a reword of the fixed refusal text, not the `{shown!r}` form
- **Requirement:** LLR-RML.1.4
- **Date:** 2026-10-25
- **What changed:** The negative control of LLR-RML.1.4 now reads: M-RML-6 = reword the fixed text of the anchor refusal (`are not allowed here` -> `are not permitted here`). The property "the old suite cannot see it" holds for that reword (golden 3 RED, `test_ingestion_limits.py` 22 GREEN); it does not hold for `{shown!r}` -> `{shown}`, which turns two old arms RED as well.
- **Why:** Inc-3 packet 6 item 1: the literal form contradicts the claim the golden exists to make.
- **Asserting test:** `tests/test_prescan_refusal_goldens.py`
- **Mutant:** M-RML-6 (reworded text) golden RED, ingestion suite GREEN
- **Evidence:** `evidence/inc3-golden-mutant-m-rml-6.txt`, `evidence/inc3-golden-mutant-m-rml-6-ingestion.txt`, `evidence/inc3-golden-mutant-m-rml-6-literal-form-ingestion.txt`

### LED-2026-10-25-relmap-r1-batch.54 — M-RML-12 is killed by the leaf test, not the golden
- **Requirement:** LLR-RML.1.4
- **Date:** 2026-10-25
- **What changed:** The negative control now says `YamlLimitError(ValueError)` is killed by `tests/test_yamlscan.py::test_limit_error_is_not_valueerror`. The golden does not see it: `_prescan_sidecar` catches `YamlLimitError` itself, inside the call and ahead of the `(YAMLError, ValueError, RecursionError)` net, and the descriptor catches it before its `ValueError` clause.
- **Why:** Inc-3 packet 6 item 2: no surviving mutant; the earlier sentence about the golden was untrue of this structure.
- **Asserting test:** `tests/test_yamlscan.py::test_limit_error_is_not_valueerror`
- **Mutant:** M-RML-12 RED on that test
- **Evidence:** Inc-3 packet 6 (`03-increments/increment-003.md`)

### LED-2026-10-25-relmap-r1-batch.55 — Stale pointers to `store.py::_prescan_sidecar` re-pointed to `mapper.yamlscan.prescan`
- **Requirement:** LLR-RML.1.4
- **Date:** 2026-10-25
- **What changed:** Comment-only edits of three docstrings: `tests/test_ingestion_limits.py` (the anchor-truncation arm), `tests/test_repair_sidecar.py` (module docstring and one arm). No code line, assertion or behaviour changed.
- **Why:** The prescan logic moved to `mapper/yamlscan.py` in Inc-3; the docstrings still named the old home.
- **Asserting test:** none new: comment-only; the touched files still pass unchanged
- **Mutant:** n/a - no behaviour change
- **Evidence:** `git diff` of the follow-up commit

### LED-2026-10-25-relmap-r1-batch.56 — `refusal_line` lives in `relmap/descriptor.py`; Inc-5 imports it from there
- **Requirement:** LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** Proposal 2 and the D5 seam row now place `refusal_line(base_name, cause, limit=None)` in `relmap.descriptor` (beside `CAUSE`), exported from there; `relmap.audit` imports it (the `audit` -> `descriptor` edge is already allowed). Inc-3 runs the hostile-name arm `test_refusal_line_hostile_base_name_is_cut_to_120`; Inc-5 keeps `test_refusal_line_hostile_name` as its own assertion over the import. LLR-RMU.1.2's text is unchanged: it never names the module.
- **Why:** Inc-3 packet 6 item 4, accepted: the cut and the K5 rendering are best kept beside the cause table.
- **Asserting test:** `tests/test_relmap_descriptor.py::test_refusal_line_hostile_base_name_is_cut_to_120`; Inc-5 `tests/test_relmap_audit.py::test_refusal_line_hostile_name`
- **Mutant:** M-RMU-13 (`refusal_line` skips the cut) RED on the Inc-3 arm
- **Evidence:** Inc-3 packet 6 (`03-increments/increment-003.md`)

### LED-2026-10-25-relmap-r1-batch.57 — `descriptor` imports `model.cut`: the edge is accepted
- **Requirement:** LLR-RMP.2.1
- **Date:** 2026-10-25
- **What changed:** Proposal 3 now lists `model` among the inputs of `descriptor` (internal order `profile`, `model`, `yamlscan`, `osopen` <- `descriptor`) and the diagram carries a `model -> descriptor` line. The import census (own modules are allowed) already admits it; no boundary outside the package moves.
- **Why:** Inc-3 packet 6: `descriptor` cuts the base name it prints with `model.cut` rather than keeping a second copy of the 120-character rule.
- **Asserting test:** `tests/test_relmap_isolation.py` (import census, unchanged and green)
- **Mutant:** n/a - architecture statement, no behaviour change
- **Evidence:** Inc-3 packet 6 (`03-increments/increment-003.md`)

### LED-2026-10-25-relmap-r1-batch.58 — `Derivation.reported` holds the printed note text, not the full report text
- **Requirement:** LLR-RMA.1.3
- **Date:** 2026-10-25
- **What changed:** LLR-RMA.1.3 no longer says the full report text "stays on the map for Layer A". The frozen `Derivation(map, reported, unlinked, unknown_status)` has no field for it: `Derivation.reported` holds the PRINTED note text (`unparsed row <id>` / `unparsed canon line`), repository-derived and uncut; Layer A reads the full report from `parse_canon` directly and the tripwire `test_report_line_shape_yields_id` pins its wording.
- **Why:** Inc-4 packet 6 item 1, orchestrator ruling: the sentence promised a field the frozen shape does not have, and no consumer needs it.
- **Asserting test:** `tests/test_relmap_adapter.py::test_reported_rows_are_notes`, `::test_report_line_shape_yields_id`
- **Mutant:** M-RMA-3 and M-RMA-8 (Inc-4 battery)
- **Evidence:** Inc-4 packet 6 (`03-increments/increment-004.md`)

### LED-2026-10-25-relmap-r1-batch.59 — the "configured, not derivable in R1" statement is carried by the audit's sources line; the adapter emits no such note
- **Requirement:** LLR-RMA.1.4, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** LLR-RMA.1.4 no longer has the adapter add a note per configured `us_canon` / `at_table`. The adapter never opens either field (`test_readonly`); the audit's sources line (`structure: sources: canon=REQUIREMENTS.md us_canon=<configured string or unset> at_table=<...>`) is what tells the operator they are configured. LLR-RMU.1.2's note order loses the item "the configured-not-derivable sources": the notes are the reported rows, the unlinked line and the ignored descriptor keys.
- **Why:** Inc-4 packet 6 item 2, orchestrator ruling: the frozen `Derivation` has nowhere to carry the note; the sources line already shows the configured string.
- **Asserting test:** `tests/test_relmap_adapter.py::test_readonly`; Inc-5 `tests/test_relmap_audit.py::test_sources_line_configured_string` and, end to end, `test_byte_stable` (see .27)
- **Mutant:** M-RMA-4 (adapter opens `us_canon`) RED on `test_readonly`
- **Evidence:** Inc-4 packet 6; Inc-5 packet

### LED-2026-10-25-relmap-r1-batch.60 — only `LLR-` ids count toward an HLR's `Node.unparsed`; a reported HLR row is a note only
- **Requirement:** LLR-RMA.1.3
- **Date:** 2026-10-25
- **What changed:** LLR-RMA.1.3 now states that the orphan relation is defined for `LLR-` ids only: a reported row whose id starts `HLR-` (for example `HLR-RH.6`) is printed as a note and relates to no HLR; `Node.unparsed` counts reported `LLR-` ids and unlinked LLRs.
- **Why:** Inc-4 packet 6 item 3, orchestrator ruling: the sentence read either way; the snapshot figures (2 / 2 / 0 on the other gap HLRs) confirm the narrow reading.
- **Asserting test:** `tests/test_relmap_adapter.py::test_unparsed_counts_ignore_unrelated_ids_and_hlr_rows`
- **Mutant:** M-RMA-16 (class filter)
- **Evidence:** Inc-4 packet 6

### LED-2026-10-25-relmap-r1-batch.61 — `unknown_status` counts only the nodes the builder kept
- **Requirement:** LLR-RMA.1.1
- **Date:** 2026-10-25
- **What changed:** LLR-RMA.1.1 now states that `unknown_status` counts only nodes the builder kept (a duplicate or unsafe id is a `Problem`, counted on the skipped line, never a node).
- **Why:** Inc-4 packet 6 item 4, orchestrator ruling: AT-124's `unknown status=1` and `nodes + skipped = parsed rows` are consistent only with this reading.
- **Asserting test:** `tests/test_relmap_adapter.py::test_duplicate_and_unsafe_ids_are_counted_never_linked`
- **Mutant:** M-RMA-10 (unknown status never counted)
- **Evidence:** Inc-4 packet 6

### LED-2026-10-25-relmap-r1-batch.62 — `RelMapLimitError` propagates out of the adapter; the hook turns it into one fixed `structure: unavailable (canon: ...)` line
- **Requirement:** LLR-RMU.1.1
- **Date:** 2026-10-25
- **What changed:** LLR-RMU.1.1 / the `structure_lines` contract now say: `RelMapLimitError` raised by `build_map` inside `derive_reqharness_map` is not caught by the adapter; `structure_lines` prints the informational header and then the single fixed line `structure: unavailable (canon: over the node or edge limit)`, no value in it, exit code untouched. `run_cli`'s `internal error: <Type>` line stays the fallback for anything else.
- **Why:** Inc-4 packet 5 / 6 and orchestrator ruling: the contract gave the limit no cause; an operator whose canon is over the cap should read the reason, not a type name.
- **Asserting test:** `tests/test_relmap_audit.py::test_canon_over_the_node_cap_is_one_fixed_line`
- **Mutant:** a hook that lets the error escape turns this RED (the exit code and the line are asserted); recorded in the Inc-5 battery as M-RMU-15
- **Evidence:** Inc-5 packet

### LED-2026-10-25-relmap-r1-batch.63 — AT-117 / AT-119 / AT-124 / AT-125 cleared V2 at Inc-4 only through Layer A names; their real Layer B nodes land at Inc-5
- **Requirement:** HLR-RMA.1
- **Date:** 2026-10-25
- **What changed:** No contract text changes. The record states that at the Inc-4 gate AT-117, AT-119, AT-124 and AT-125 stopped blocking (`V2`) only because `tests/test_relmap_adapter.py` NAMED them as Layer A stand-ins; the Layer B nodes (a real `mapper --audit` subprocess each) are minted in `tests/test_relmap_audit.py` at Inc-5, and the stand-ins stay as in-process pins.
- **Why:** Inc-4 packet 6 item 6, orchestrator ruling: the acceptance claim must rest on the shipped surface, not on a docstring.
- **Asserting test:** `tests/test_relmap_audit.py::test_at_117_*`, `::test_at_119_*`, `::test_at_124_*`, `::test_at_125_*`
- **Mutant:** M-RMA-1, M-RMA-6 (AT-117), M-RMA-3 (AT-119), M-RMU-7 (AT-124), M-RMG-4 / M-RMA-5 (AT-125) RED through the subprocess
- **Evidence:** Inc-5 packet

### LED-2026-10-25-relmap-r1-batch.64 — the double `build_map` per derivation is accepted; cost noted as a watch-item
- **Requirement:** HLR-RMA.1
- **Date:** 2026-10-25
- **What changed:** No contract text changes. The adapter builds the map twice (once to learn which nodes the builder keeps, once with the edges and the `unparsed` counts); at the node cap this doubles an O(V+E) build. Accepted as the only way found to avoid drawing an edge to an excluded node without copying the builder's unsafe-id predicate; recorded as a watch-item for R2.
- **Why:** Inc-4 packet 5, orchestrator ruling.
- **Asserting test:** none new
- **Mutant:** n/a - cost note, no behaviour change
- **Evidence:** Inc-4 packet 5

### LED-2026-10-25-relmap-r1-batch.65 — the retired `AT-123` is written as a citation, not a declaration
- **Requirement:** HLR-RMP.2
- **Date:** 2026-10-25
- **What changed:** Section 5.1 now writes `AT-123` in backticks. Its meaning is unchanged (retired; its claim is the Layer A pin TC-RM-01 of HLR-RMP.2); the gate rule `V2` reads a bare id as a declaration and a backticked id as a mention, so the bare spelling kept a retired id demanding a node on disk.
- **Why:** Inc-5 gate: the only remaining `V2` block was the retired id; the validator's own rule (C-56, an id quoted is not an id declared) is the stated remedy.
- **Asserting test:** `tests/test_relmap_isolation.py` (TC-RM-01 is the node that carries the claim)
- **Mutant:** n/a - wording
- **Evidence:** Inc-5 gate transcript (`evidence/inc5-gate.txt`)

### LED-2026-10-25-relmap-r1-batch.66 — K9 wording: total collection depth 64 loads, 65 refused
- **Requirement:** LLR-RML.1.1 (K9), AT-121
- **Date:** 2026-10-25
- **What changed:** `01-requirements.md` (boundary catalog, numeric pass threshold, AT-121 row) now reads "total collection depth 64 loads, 65 refused (the top-level mapping counts as depth 1)". No code change: `mapper/yamlscan.py` counts every collection START event, equal to the hygiene requirement LLR-Q2.1.2; nested values under a key are therefore 63 loads / 64 refused, which `_nested_flow(63)` / `(64)` pin.
- **Why:** Inc-5 independent review F3 (MINOR): the old wording was ambiguous between total depth and nested depth.
- **Asserting test:** AT-121 depth arms (unchanged)
- **Mutant:** n/a - wording
- **Evidence:** `evidence/review-inc005.md` (Depth verdict)

### LED-2026-10-25-relmap-r1-batch.67 — the `run_cli` sink keeps `verdict: ` exclusive to the report
- **Requirement:** LLR-RMU.1.1
- **Date:** 2026-10-25
- **What changed:** in `run_cli`'s hook-print loop a hook line that (after `_visible`) starts with `verdict: ` is printed with the prefix `structure: ` (prefixed, not dropped, so no content is lost silently). No per-line length bound: the shipped formatter bounds its lines and a generic hook is the caller's own; recorded as a note for R2.
- **Why:** Inc-5 independent review F2 (MINOR): "can never" held by construction of the shipped hook, not by the sink.
- **Asserting test:** `tests/test_relmap_audit.py::test_hook_line_can_never_forge_a_verdict_line`
- **Mutant:** guard removed (`if False:`) RED
- **Evidence:** `evidence/inc5f-red.txt`

### LED-2026-10-25-relmap-r1-batch.68 — `reach` defined where the structure lines are documented; verdict-by-prefix note location
- **Requirement:** LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** `docs/ARCHITECTURE.md` (relmap row) now states "reach = how many nodes a change to this node reaches". Widths stay as accepted. The verdict-by-prefix note lives in `docs/ARCHITECTURE.md` (section 3 contract note) and the on-screen header; `README.md` has no `--audit` text, so MAJOR-4's "packet and README" is met by those two places.
- **Why:** Inc-5 independent review F4 (UX, doc only) and F5.
- **Asserting test:** n/a - documentation
- **Mutant:** n/a - wording
- **Evidence:** `evidence/review-inc005.md`

### LED-2026-10-25-relmap-r1-batch.69 — literal coerced code points in the batch's tracked files are spelled as escapes
- **Requirement:** LLR-RMM.1.2
- **Date:** 2026-10-25
- **What changed:** `tests/test_relmap_model.py` (the `bad_id` parametrization) and four batch records (this ledger, `02-review.md`, `evidence/p2-qa-pass3-and-pdr-qa.md`) held live U+200B, U+2028 and U+202E; they now carry the escape text (`\u200b`, `\u2028`, `\u202e`). In the test the Python string value is byte-for-byte the same, so behaviour is identical. In the records only the transcription changed (the live character became its escape spelling); no hash cites any of the three records (grepped, full and 8-character prefixes), so no re-pin. This entry is the one place a past ledger entry's text was touched, and only for that spelling.
- **Why:** The full-suite run found `tests/test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts` red with three offenders; the targeted runs of Inc-1 to Inc-5 never included `test_fold.py`.
- **Asserting test:** `tests/test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts`
- **Mutant:** re-introduce a live U+200B into `tests/test_relmap_model.py`: RED (the sweep names the file)
- **Evidence:** PLAN.md section "P3 follow-up"

### LED-2026-10-25-relmap-r1-batch.70 — a second `model.py` makes bare `model.py:<line>` citations ambiguous
- **Requirement:** LLR-RMM.1.1
- **Date:** 2026-10-25
- **What changed:** `mapper/search.py` now cites `mapper/model.py:149` (comment only). The sealed `.dev-flow/2026-08-27-repair-batch-02/04-gate-findings-disposition.md` cites bare `model.py:82-83` and was NOT edited; the resolver in `tests/test_repair_artifact_claims.py` has no exception table, so that arm stays RED pending an operator ruling (options in PLAN.md section "P3 follow-up"). `mapper/relmap/model.py` keeps its frozen D3 path.
- **Why:** Creating `mapper/relmap/model.py` beside `mapper/model.py` turned every bare basename `model.py` into an ambiguous hit in `_resolve`, which returns `None` unless exactly one file matches.
- **Asserting test:** `tests/test_repair_artifact_claims.py::test_every_path_line_citation_resolves[search.py]` (green) and `[04-gate-findings-disposition.md]` (red, open)
- **Mutant:** n/a - comment qualification; the resolver is the oracle
- **Evidence:** PLAN.md section "P3 follow-up"

### LED-2026-10-25-relmap-r1-batch.71 — the sealed bare `model.py` citation is a declared exception, not a resolver change
- **Requirement:** LLR-RMM.1.1
- **Date:** 2026-10-25
- **What changed:** `tests/test_repair_artifact_claims.py` gains `_CITATION_EXCEPTIONS` with one row, (`04-gate-findings-disposition.md`, `model.py`) -> `mapper/model.py`, reason: sealed record of 2026-08-27-repair-batch-02 predates `mapper/relmap/model.py`; bare basename became ambiguous; the record is not edited. `_resolve` is untouched. A new arm checks every row still resolves to a file, names a corpus artifact that cites the token, and is still needed (the plain resolver fails on it). Operator ruling: option B.
- **Why:** closes the open item of LED .70 without editing a sealed record or changing a guard's rule.
- **Asserting test:** `tests/test_repair_artifact_claims.py::test_every_declared_citation_exception_is_still_needed` and `::test_every_path_line_citation_resolves`
- **Mutant:** drop the row (key renamed): the citation arm for `04-gate-findings-disposition.md` RED and the table arm RED (executed)
- **Evidence:** PLAN.md section "P3 follow-up"

### LED-2026-10-25-relmap-r1-batch.72 — `unknown_status` over kept nodes only is pinned by its own node (DDR software-dev MAJOR, mutant M3)
- **Requirement:** LLR-RMA.1.1
- **Date:** 2026-10-25
- **What changed:** A Layer A node now pins LED .61: a duplicate-id row and an unsafe-id row whose status is `done` are excluded by the builder and must not add to `unknown_status`; only the kept `Done` row does. Product code is unchanged.
- **Why:** DDR software-dev lens: mutant M3 (count over all input nodes instead of `final.nodes`) survived the whole relmap suite, so .61 was asserted, not pinned. Orchestrator ruling 1.
- **Asserting test:** `tests/test_relmap_adapter.py::test_unknown_status_counts_kept_nodes_only`
- **Mutant:** M3 (`sum(1 for n in nodes ...)` in `mapper/relmap/adapter.py`): RED (`assert 3 == 1`); restored, sha256-verified, GREEN (executed by the DDR worker)
- **Evidence:** `evidence/ddr-m3-pin-red-green-2026-10-25.txt`, `evidence/ddr-software-dev.md`

### LED-2026-10-25-relmap-r1-batch.73 — the three closing-gate regressions are reproduced and the two named mutants are executed, with transcripts (DDR QA F-1, F-2, OP-7)
- **Requirement:** LLR-RMM.1.1, LLR-RMM.1.2
- **Date:** 2026-10-25
- **What changed:** No contract or code change. A detached checkout of the parent of `456da08` (`6331206`) was run against `tests/test_fold.py` and `tests/test_repair_artifact_claims.py` (3 failed, the three LED .69/.70/.71 nodes), and on the current tree the .69 mutant (one literal U+200B in `tests/test_relmap_model.py`) and the .71 mutant (the `_CITATION_EXCEPTIONS` row dropped) were executed and restored. The transcript is labelled a reproduction run by the orchestrator's worker, not the original run; the original run's transcript is still not stored.
- **Why:** DDR qa-reviewer F-1/F-2: the escaped-bug table rested on ledger prose. Orchestrator ruling 2.
- **Asserting test:** `tests/test_repair_artifact_claims.py::test_every_declared_citation_exception_is_still_needed`, `tests/test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts`
- **Mutant:** .69 mutant: the fold sweep RED naming `tests/test_relmap_model.py` (`0x200b`); .71 mutant: `test_every_path_line_citation_resolves[04-gate-findings-disposition.md]` and `test_every_declared_citation_exception_is_still_needed` RED
- **Evidence:** `evidence/ddr-reproduction-escaped-regressions-2026-10-25.txt`

### LED-2026-10-25-relmap-r1-batch.74 — C-18 reads "every AT resolves to at least one node whose name or docstring carries its id" (DDR ruling OP-2)
- **Requirement:** LLR-RMU.1.3
- **Date:** 2026-10-25
- **What changed:** Ruling recorded in the DDR: C-18 is satisfied when every AT resolves to at least one node whose name or docstring carries its id - one realisation, several assertions (per-arm RED kept). The docstring of the second AT-120 node now carries the id; the AT-128 node already did.
- **Why:** DDR qa-reviewer F-7 and OP-2, software-dev OP-2: folding AT-121/AT-122 under one function each would let the first failing assert hide the others. Orchestrator ruling 4.
- **Asserting test:** `tests/test_relmap_audit.py::test_exit_code_unchanged`
- **Mutant:** n/a - docstring only; the node's own mutant is M-RMU-8 (exit 1 on a structural gap)
- **Evidence:** `design/DDR-2026-10-25-relmap-r1-batch.md`, `evidence/ddr-qa.md`

### LED-2026-10-25-relmap-r1-batch.75 — `README.md` gains an operator section for `mapper --audit`; the `verdict: ` sink guard is written into the module map (DDR UX F-1/F-2, architect F-1)
- **Requirement:** LLR-RMU.1.1, LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** `README.md` now has an `Audit` section: the verdict is the line that starts with `verdict: ` and not the last line; the `structure:` block is informational and never changes the verdict or the exit code; `reach` is how many other nodes a change to the node reaches downstream. `docs/ARCHITECTURE.md` (relmap row) gains the clause that `run_cli` rewrites a hook line starting `verdict: ` to `structure: verdict: ...`. The gap and note overflow lines (`structure: gaps shown ...`, `structure: notes shown ...`) do not start like data rows (`structure gap: `, `structure note: `): pinned by the Layer A nodes cited here.
- **Why:** DDR ux-reviewer F-1/F-2/F-3 and architect F-1; this supersedes the remark in LED .68 that `README.md` has no `--audit` text. Orchestrator rulings 6 and 8.
- **Asserting test:** `tests/test_relmap_audit.py::test_gap_cap_is_twenty_with_an_overflow_line`, `tests/test_relmap_audit.py::test_note_cap_is_ten_with_an_overflow_line`, `tests/test_relmap_audit.py::test_hook_line_can_never_forge_a_verdict_line`
- **Mutant:** n/a - documentation; the code arms keep M-RMU-3/5/7 and the forge-guard mutant of LED .67
- **Evidence:** `evidence/ddr-overflow-lines-2026-10-25.txt`, `evidence/ddr-ux.md`, `evidence/ddr-architect.md`

### LED-2026-10-25-relmap-r1-batch.76 — the three contract wordings that differ from the shipped behaviour are accepted deviations; the shipped behaviour is normative (DDR QA F-6, OP-10)
- **Requirement:** LLR-RMU.1.2
- **Date:** 2026-10-25
- **What changed:** No contract text is edited here. AT-126(c) (a symlinked canon prints `structure: unavailable (canon: is a link)`), the AT-126 marker scope (the path marker never appears in stdout; as built, in the structure block) and the LLR-RMU.1.2 note wordings (unlinked-list note, ignored-key note, 400-character sentence cap) are recorded in the DDR as accepted deviations. AT-126 and LLR-RMU.1.2 are `pass-with-deviation` in `04-validation.md` and the matrix. The shipped behaviour is normative: nobody changes the code toward the old wording; B-149 amends the contract.
- **Why:** DDR qa-reviewer F-6, architect and software-dev OP-10: a declared deviation is a debt, a silent one is a defect. Orchestrator ruling 3.
- **Asserting test:** `tests/test_relmap_audit.py::test_at_126_unavailable_lines_and_no_path_leak`
- **Mutant:** n/a - record; the node's mutants stay M-RMU-4 and M-RML-7
- **Evidence:** `04-validation.md` (G-004, Accepted deviations), `design/DDR-2026-10-25-relmap-r1-batch.md`, BACKLOG B-149
