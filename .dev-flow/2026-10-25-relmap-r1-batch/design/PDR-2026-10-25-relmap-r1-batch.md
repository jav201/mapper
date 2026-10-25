# Design review record — PDR — mapper — Batch 2026-10-25-relmap-r1-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.

> **Owed in.** `core` by trigger · `full` ✓ (trigger A1 fired).

> **Where this lives.** Repo copy under `.dev-flow/<batch>/design/`, as the hygiene batch did. It is **sealed** and **cited by id**; if it changes after the seal it is a NEW version with a NEW id, never a silent edit.

> **Notice convention.** `⚠` yellow = notice, declare the reason and continue · `✗` red = block · `✓` green = satisfied **with its evidence cited**. Without a citation an item is asserted, not satisfied. At this seal every §A row is `✓` with the reviewer evidence cited; what remains is the condition table in §B, each condition applied to the artifact now and re-read at the DDR (the test-level ones also at the named increment gate).

| Field | Value |
|---|---|
| Record id | `PDR-2026-10-25-relmap-r1-batch` |
| Reviews | `design/design-proposal.md` (`PDR-2026-10-25-relmap-r1-batch`, revised 2026-10-25 for the conditions below); one chain, no lanes to join at DDR |
| Participants | PDR: `architect — Claude Sonnet subagent executing agents/architect.md · approved with conditions` · `qa-reviewer — Claude Sonnet subagent executing agents/qa-reviewer.md · approved with conditions` · `security-reviewer — Claude Sonnet subagent executing agents/security-reviewer.md · approved with conditions` · `ux-reviewer — Claude Sonnet subagent executing agents/ux-reviewer.md · approved with conditions` |
| Date sealed | `2026-10-25` |
| **Verdict** | `approved with conditions` |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` | ✓ | proposal §1–§6; §6 lists five rejected alternatives where a real decision exists and one honest `n/a`; architect `evidence/pdr-architect.md` row 1 (two rationales reworded, PD-6); QA `evidence/p2-qa-pass3-and-pdr-qa.md` row 1 (D-3 applied) |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | proposal §2: no boundary moves; architect `evidence/pdr-architect.md` row 2 and the allow-list re-derivation; the stale internal-order sentence (PD-4) is amended in the `relmap` row of `docs/ARCHITECTURE.md` |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | proposal §7 (six rows, none empty); architect `evidence/pdr-architect.md` row 3 |
| 4 | Every requirement has foreseen coverage | ✓ | proposal §1 chain map + §5.1 LLR rows (26 LLRs and TC-RM-01/02/03; ATs per contract §5.3–§5.4); QA `evidence/p2-qa-pass3-and-pdr-qa.md` row 4 (26 LLRs counted by group) |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ✓ | proposal §5.1; QA conditions D-1, D-2, D-3 applied (ledger `.32`, `.33`, `.34`): the ceiling mutants are killed by a visit counter and a `down` tripwire, two tests moved to the increment that holds their subject, the cap+1 arm instruments bytes read |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | proposal §2.1 (exit checks, Layer phasing, timing) and §6; QA `evidence/p2-qa-pass3-and-pdr-qa.md` row 6; golden provenance and wall-time lines added (D-7, D-9, ledger `.35`) |
| 7 | Interfaces **frozen** for the chain are listed | ✓ | proposal §4: D1 `yamlscan`, D2 `descriptor`, D3 `profile`/`model`/`gaps`/`adapter` R2 API, D4 `run_cli`, D5 `structure_lines` only; architect PD-2 and PD-3 applied (ledger `.37`, `.38`); security C1/C2 (ledger `.39`, `.40`) |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ — n/a for lanes | proposal §8 (no fork); §2.1 file sets disjoint, SOURCE counts 3, 1, 3, 1, 3 (≤ 4; the helper `tests/_relmap_fixtures.py` and `.gitattributes` are not source); §5.2 census corrected to 16 `--audit` sites, 10 printing the block and 6 refused before the hook, with the hostile-canon arms added (QA D-6, architect PD-5) |
| 9 | UX lens applied (if family D fired): interaction design reviewed | ✓ | `ux-reviewer` `evidence/pdr-ux.md` (`approved with conditions`): MAJOR-1..4 and MINOR-1,2,3,5,6 applied to LLR-RMU.1.2 and the AT oracles (ledger `.42`, `.43`); MINOR-4,7,8 stated in proposal §5.3. State of evidence: inspected, not exercised; the real-output walk at 80 columns is owed at Phase 4 |
| 10 | Security lens applied (if family C fired) | ✓ | `security-reviewer` `evidence/pdr-security.md` (`approved with conditions`): C1 (one shared visit budget) and C2 (UNESCAPED lines, cut inside `format_structure`) applied; M1, M2, M3, M5 folded in, M4 as an Inc-5 arm (ledger `.39`–`.41`) |

**No increment starts without an approved PDR.**

---

## B · DDR checklist — detailed design review · **and the JOIN point when the batch forked**

Not forked: the rows below are filled at the DDR, after Inc-5.

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, **and why** | | filled at the DDR |
| 2 | Frozen interfaces still intact — or the work returned to the trunk and it is declared | | filled at the DDR |
| 3 | **Reverse census CROSSED between lanes** | | n/a — no lanes; proposal §5.2 re-run at the DDR |
| 4 | Every `AT-NNN` realises in **exactly one** on-disk node (C-18) | | filled at the DDR |
| 5 | Test ledger **summed** across increments, reconciled | | filled at the DDR |
| 6 | No increment touched another increment's file | | filled at the DDR |
| 7 | Source-file budget: any increment that reached or exceeded 4, reviewed here | | filled at the DDR (planned maximum is 3) |
| 8 | **Every open PDR condition discharged one by one, by RE-READING the artifact** | | the table below, re-read at the DDR |

**Conditions left open at the seal.** Every condition below is APPLIED to the contract, the proposal or `docs/ARCHITECTURE.md` now (the "artifact line" column names where); `Discharged?` records whether the test-level part still has to execute at an increment gate. Nothing here is `executed`: every test is `planned` until its increment.

| # | Condition left open at PDR | Discharged? | The artifact line that proves it |
|---|---|---|---|
| X-1 (P2) | AT-122 arm 3 cannot carry U+2028 through the canon: ESC + U+202E in the statement, U+2028 via a descriptor ignored key and a Layer A arm | applied; executes at the Inc-5 gate | ledger `.29`; contract AT-122, LLR-RMM.1.2 boundary, LLR-RMU.1.3 |
| N-3 (P2) | AT-128 two pre-picked seeds proven by a recorded probe | applied; real-mutant re-proof at the Inc-5 gate | ledger `.30`; `evidence/p2-closure-probe-2026-10-25.txt`; contract AT-128, LLR-RMU.1.4 |
| N-7 (P2) | M-RML-15 and M-RMA-7 in the LLR negative-control lines | applied | ledger `.31`; contract LLR-RML.1.1, LLR-RMA.1.1 negative controls |
| D-1 (QA, MAJOR) | ceiling mutants killed by a deterministic visit counter and a `down` tripwire; int-memo check on a 2,000-node chain | applied; executes at the Inc-1 and Inc-2 gates | ledger `.32`; contract LLR-RMM.2.2 (`test_reach_memo_is_counts`, `test_reach_budget_per_row`), LLR-RMG.1.3 (`test_rank_visit_cap`); proposal §3 *Resource* |
| D-2 (QA, MAJOR) | `test_snapshot_gaps` moved to Inc-4, `test_canon_derived_once` to Inc-5 (chosen over stand-ins) | applied | ledger `.33`; contract LLR-RMG.1.2, LLR-RML.1.6, LLR-RMU.1.4; proposal §2.1 rows 2, 4, 5 and §5.1 |
| D-3 (QA, MAJOR) | M-RML-8 arm instruments bytes read, at most cap+1 | applied; executes at the Inc-3 gate | ledger `.34`; contract LLR-RML.1.5 Executed verification and Negative control |
| D-4 (QA) | Layer B first runs at Inc-5; Layer A stand-ins at Inc-3 and Inc-4 | applied | ledger `.35`; proposal §2.1 *Layer phasing*; contract §5.1 |
| D-5 (QA) | AT fixture builder imported (`tests/_relmap_fixtures.py`), not copied | applied; executes at the Inc-5 gate | ledger `.35`; proposal §2.1 row 5, §5.1; contract §5.1 |
| D-6 (QA) | census corrected: 16 `--audit` sites, 10 print the block, 6 refused before the hook, with lines | applied | ledger `.35`; proposal §5.2 first table |
| D-7 (QA) | golden constants generated by running the base; capture command and base SHA recorded; committed alone before the `store.py` edit | applied; evidenced in the Inc-3 packet | ledger `.35`; contract LLR-RML.1.4 *Provenance*; proposal §2.1 row 3 |
| D-8 (QA) | K1 arm uses a directory junction on Windows | applied; executes at the Inc-3 gate | ledger `.35`; contract LLR-RML.1.5, AT-121; proposal §6 risk 4 |
| D-9 (QA) | each packet records measured wall time, about one minute for `test_relmap_audit.py` | applied; recorded in every packet | ledger `.35`; proposal §2.1 *Timing*, §6 risk 5 |
| PD-1 (architect, MAJOR) | snapshot pin hashes LF-normalised bytes (authoritative) and `.gitattributes` gets `-text` for the fixture directory; ledger entry correcting `.4` | applied; `.gitattributes` line and fresh-LF-checkout run at the Inc-4 gate | ledger `.36` (`b093c920…`); contract LLR-RMA.1.1; proposal §2.1 row 4 |
| PD-2 (architect, MAJOR) | frozen R2 API completed: `default_descriptor()`, `RelMap.nodes`/`.edges` types, `up`/`down` return types, `rank_gaps(limit=None)` | applied | ledger `.37`; proposal §4 D2/D3 rows; contract LLR-RMM.1.1, LLR-RMM.2.2, LLR-RMG.1.3, LLR-RML.1.2 |
| PD-3 (architect) | freeze only `structure_lines`, the exception classes and the R2 API; `format_structure`, `refusal_line`, `CAUSE` are tested seams | applied | ledger `.38`; proposal §4 D5 row and the *frozen set is exactly* sentence |
| PD-4 (architect) | ARCHITECTURE internal-order sentence fixed | applied | ledger `.38`; `docs/ARCHITECTURE.md` `relmap` row (`audit` → `adapter`, `gaps`, `descriptor`, `model`) |
| PD-5 (architect) | hostile-canon arms (`tests/test_reqharness_release.py:665-680`, `:755-770`) in the census and the Inc-5 exit check | applied | ledger `.38`; proposal §5.2 second row, §2.1 row 5 |
| PD-6 (architect) | two rejected-alternative rationales corrected | applied | proposal §6 rejected-alternatives rows 1 and 3 |
| PD-7 (architect) | `run_cli` keys the fixed lines on `chain_status`; TC for the `--baseline` refusal path | applied; TC-RM-03 executes at the Inc-5 gate | ledger `.38`; contract LLR-RMU.1.1, §5.3 Layer A pins; proposal §4 D4 row |
| C1 (security, MED) | one visit budget per `RelMap` shared by `reach` and `rank_gaps`; typed "not computed" result; docstring, ARCHITECTURE row and a per-row test arm | applied; executes at the Inc-1 gate | ledger `.39`; contract LLR-RMM.2.2, LLR-RMG.1.3; `docs/ARCHITECTURE.md` `relmap` row; proposal §4 model row |
| C2 (security, MED) | `structure_lines` documented as UNESCAPED; Inc-5 arm calls `format_structure` directly with a 1 MiB value and asserts the cut lives inside | applied; executes at the Inc-5 gate | ledger `.40`; contract LLR-RMU.1.2 (`test_format_structure_cuts_inside`); `docs/ARCHITECTURE.md` `relmap` row; proposal §4 D5 row |
| M1 (security) | `st_ino = 0` tolerance, with an arm | applied; executes at the Inc-3 gate | ledger `.41`; contract LLR-RML.1.5 |
| M2 (security) | `CAUSE` as `MappingProxyType`, with a test | applied; executes at the Inc-3 gate | ledger `.41`; contract LLR-RML.1.1 (`test_cause_is_read_only`) |
| M3 (security) | `confine_reason` again at the future open time, noted beside the ban | applied (note); acted on by a later batch | ledger `.41`; contract LLR-RML.1.3 |
| M4 (security) | direct `refusal_line` hostile-name arm (U+0301 and 300 characters) | applied; executes at the Inc-5 gate | ledger `.40`; contract LLR-RMU.1.2 (`test_refusal_line_hostile_name`) |
| M5 (security) | bounded iteration over hook lines | applied; executes at the Inc-5 gate | ledger `.41`; contract LLR-RMU.1.1 (`test_hook_line_bound`) |
| MAJOR-1 (UX) | first block line `structure: informational - does not change the verdict or the exit code` | applied; executes at the Inc-5 gate | ledger `.42`; contract LLR-RMU.1.2 table, AT-120 |
| MAJOR-2 (UX) | count line `structure: skipped N canon rows (…); unknown status=N; reach not computed=N` | applied; executes at the Inc-5 gate | ledger `.42`; contract LLR-RMU.1.2 table, AT-124 |
| MAJOR-3 (UX) | overflow lines `structure: gaps shown X of Y (Z lowest-ranked not shown)` and `structure: notes shown X of Y (Z not shown)` | applied; executes at the Inc-5 gate | ledger `.42`; contract LLR-RMU.1.2 table |
| MAJOR-4 (UX) | verdict found by the `verdict: ` prefix, no longer the last line, documented | applied | ledger `.42`; contract LLR-RMU.1.1 and HLR-RMU.1; `docs/ARCHITECTURE.md` `relmap` row; proposal §5.3 |
| MINOR-1 (UX) | refusal line `… - descriptor skipped`; K17 names the field, K16 the key, K5 the byte limit | applied; executes at the Inc-3 and Inc-5 gates | ledger `.43`; contract LLR-RMU.1.2 refusal row, LLR-RML.1.2/.1.3/.1.5, AT-121 |
| MINOR-2 (UX) | hook failure `structure: unavailable (internal error: <Type>)` | applied | ledger `.43`; contract LLR-RMU.1.1, TC-RM-02 |
| MINOR-3 (UX) | gap qualifier `(canon rows near this id could not be parsed or linked: <n>)` | applied | ledger `.43`; contract LLR-RMG.1.1, AT-125 |
| MINOR-4 (UX) | width not guaranteed, stated | applied | contract LLR-RMU.1.2 *Reading notes*; proposal §5.3 |
| MINOR-5 (UX) | `reach` defined once | applied | ledger `.43`; contract LLR-RMU.1.2 gap row; `docs/ARCHITECTURE.md` `relmap` row |
| MINOR-6 (UX) | `structure: descriptor (built-in default)`, `us_canon=unset at_table=unset` | applied | ledger `.43`; contract LLR-RMU.1.2 label and sources rows |
| MINOR-7 (UX) | gap rows are for reading, not parsing, stated | applied | contract LLR-RMU.1.2 *Reading notes*; proposal §5.3 |
| MINOR-8 (UX) | worst-case length stated (about 298 lines) | applied | contract LLR-RMU.1.2 *Reading notes*; proposal §5.3 |

---

## C · Verdict and what it means

- **Verdict: `approved with conditions`, sealed 2026-10-25.** The four independent reviews returned `approved with conditions` (`evidence/pdr-architect.md`: PD-1, PD-2 major, PD-3 to PD-7 minor; `evidence/p2-qa-pass3-and-pdr-qa.md`: D-1, D-2, D-3 major, D-4 to D-9 minor; `evidence/pdr-security.md`: C1, C2 medium, M1 to M5 notes; `evidence/pdr-ux.md`: MAJOR-1 to MAJOR-4, MINOR-1 to MINOR-8). The author applied every condition to the contract, the proposal and `docs/ARCHITECTURE.md` in the same unit (ledger `.29`–`.43`); the table in §B lists each with where it is discharged. The P2 decision and this PDR decision are recorded by the orchestrator.
- Approval means the D1–D5 freeze binds across Inc-1…Inc-5 (the frozen set is exactly the sentence in proposal §4, with `format_structure`, `refusal_line` and `CAUSE` as tested seams) and the per-increment file sets of proposal §2.1 are the plan (SOURCE counts 3, 1, 3, 1, 3).
- A conditional verdict is not an authorisation of the unexecuted: every test named here is `planned`; each increment gate re-reads the conditions it owns and the DDR re-reads all of them.

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| D1 — frozen interface: `yamlscan.prescan(text)`, `YamlLimitError(Exception)` with `kind`/`shown`/`limit`, `ANCHOR_NAME_DISPLAY = 40`; `store` converts byte-identically and drops `MAX_DEPTH` | `PDR-2026-10-25-relmap-r1-batch#D1` | LLR-RML.1.4; `docs/ARCHITECTURE.md` `yamlscan` row |
| D2 — frozen interface: `read_repo_text`, `RepoReadError` (with `limit`), `DescriptorError`, `Descriptor`, `default_descriptor`, `load_descriptor`, `discover_descriptors` in `relmap/descriptor.py` (`CAUSE`, K1–K17, is a read-only tested seam) | `PDR-2026-10-25-relmap-r1-batch#D2` | LLR-RML.1.1–.1.3, .1.5, .1.6 |
| D3 — frozen interface: `Profile`/`EdgeType`/`GapRow`, `Node`/`Edge`/`Problem`/`RelMap` (with `VISIT_BUDGET`, `visits`, `reach -> int \| None`), `build_map`, `Gap`/`detect_gaps`/`rank_gaps(limit: int \| None)`, `CanonUnavailable`/`Derivation`/`derive_reqharness_map` — the API R2 consumes | `PDR-2026-10-25-relmap-r1-batch#D3` | LLR-RMP.1.1, RMM.1.1–.2.2, RMG.1.1–.1.3, RMA.1.1–.1.4; `docs/ARCHITECTURE.md` `relmap` row |
| D4 — frozen interface: `run_cli(argv, extra_lines=None)`; fixed no-repo / no-registry lines keyed on `chain_status`, hook-failure and truncation lines; the hook receives `Path(report.repo)`; no hook call when `audit()` raises | `PDR-2026-10-25-relmap-r1-batch#D4` | LLR-RMU.1.1 |
| D5 — frozen interface: `structure_lines(repo)` (UNESCAPED lines, informational header first); `format_structure` and `refusal_line` are tested internal seams, not frozen | `PDR-2026-10-25-relmap-r1-batch#D5` | LLR-RMU.1.2–.1.4 |
| D6 — the byte-identity golden is inline constants in `tests/test_prescan_refusal_goldens.py`, generated by running the base code, committed alone before the `store.py` edit | `PDR-2026-10-25-relmap-r1-batch#D6` | LLR-RML.1.4 |
| D7 — the snapshot canon fixture is created in Inc-4 and pinned by its LF-normalised sha256 `b093c920…` (authoritative), with `-text` in `.gitattributes` as defence in depth | `PDR-2026-10-25-relmap-r1-batch#D7` | LLR-RMA.1.1 |
| D8 — five sequential increments, ≤ 3 source files each, osopen allow-list entries in the increment that adds the import | `PDR-2026-10-25-relmap-r1-batch#D8` | LLR-RMP.2.1; PLAN increment table |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the design record: it is reflected in the requirement or in the module map, which are versioned beside the code.
