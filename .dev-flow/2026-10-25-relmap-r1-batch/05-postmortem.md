# Post-mortem — mapper — Batch 2026-10-25-relmap-r1-batch

> **Artifact language:** English (`state.json` `language`).
> Phase 5 artifact. Co-authors (roles executed by the dev-flow worker as a records-only unit; no product or test code changed): `architect` + `qa-reviewer`. **LOCAL STAGING:** the canonical copy is `artifact_homes.postmortem` in the vault, written only by `/dev-flow-sync`.
> Source of every number below: the batch records (`PLAN.md`, `02-review.md`, `03-increments/`, `04-validation.md`, `design/DDR-…`, `01-requirements-ledger.md`, `state.json` `decisions_log`) and `git log` of branch `feat/relmap-r1`. A figure that no record carries is marked `not recorded`.

## 0 · Gate record — which tree this close gated

| Field | Value |
|---|---|
| Gate record | `python devflow-validate.py --brief .` → exit 0, `0 block` · 2026-10-25 (the P5/P6 records gate; this is NOT the close gate: the batch is not merged and not synced) |
| Gated tree | `3d76687090ca14e13daaa9b8b1d0c7fcd0ab44c2` · dirty — the P5/P6 records of this unit (`05-postmortem.md`, `06-docs/executive-summary.md`, `06-docs/functionality.md`, `06-docs/traceability-matrix.md`, `PLAN.md`, `BACKLOG.md`, `state.json`, `03-increments/increment-005.md` §2 rows for the V59 limb, and `REQUIREMENTS.md`: the canon fold of the batch's 35 requirement ids by `devflow-init.py --fold-canon`, 35 folded / 0 refused) |

## 🔑 At a glance (read first)

- **Outcome:** closed with carry-over. Validation PASS-WITH-NOTES (35/35 requirements, 12/12 ATs as real `mapper --audit` subprocess nodes, 3 accepted deviations); DDR approved with conditions; full suite 4017 passed / 0 failed at `934e935`. One iteration of P1 (re-entered after the first P2 pass); every other station 0 recorded iterations.
- **Top 3:** ① **worked** — independent reviewers at every gate found real defects the author's own battery missed (a blocker at P2, a surviving mutant at Inc-2, the unpinned M3 at DDR), and every one was closed with a RED/GREEN transcript. ② **didn't** — three regressions reached the closing full-suite gate because two whole-corpus guards sat outside every increment's targeted run. ③ **root cause** — P2 took three passes because the contract carried what a contract should reference (AT bodies, mutant tables, amendment history) and grew to 109,299 characters against a 54,000 budget.
- **New control this batch:** the per-increment guard set names `tests/test_fold.py` and `tests/test_repair_artifact_claims.py` (adopted inside this batch at the P3 follow-up; see Control lineage).
- **Open items → next batch:** 12 — the biggest: **R2 views** (matrix + lens, gaps view, node-sheet sections), whose PDR inherits DDR §E items 10–12 and the 16 carries B-140…B-155.
- **Metrics:** iterations P1=1, others 0 · findings (recorded reviewer rows) P2 ≥ 54 / P3 gates 22 / closing gate 3 · mutants 100 battery + 4 reviewer/DDR = all killed after fixes · ledger `3579 − 4 + 447 = 4022` selected (+1 after the DDR gate = 4023) · LED entries `.1`–`.76`.

> Enough to know the batch's health and what carries forward. Detail below for the why.

---

## Detail (reference)

### What worked
- **Independent review earned its cost.** Evidence: Q-1 (blocker, byte-identity of the moved prescan was asserted by substring tests that a reworded refusal would pass) was caught at P2 and answered by an equality golden captured on the base BEFORE the move (`ecfea03`, `evidence/inc3-golden-green-on-base.txt`); the reviewer's own mutant kept the golden honest (`evidence/inc3-golden-mutant-m-rml-6.txt`).
- **RED before GREEN, with transcripts.** Every increment stores a code-absent RED, a first GREEN and a hash-verified mutant battery (`evidence/incN-red-*.txt`, `incN-green-*.txt`). The DDR also forced a labelled reproduction of the three escaped regressions on a detached checkout of `6331206` (`evidence/ddr-reproduction-escaped-regressions-2026-10-25.txt`): exactly the 3 nodes fail, then go green.
- **Acceptance through the shipped surface.** The twelve ATs are `mapper --audit` subprocess nodes (60 s timeout) over a tmp git repo; `04-validation.md` lists the real block on the real snapshot canon read at 80 columns.
- **Parallel author/reviewer pipelining in one worktree worked** under strict file ownership: the commit order shows increments authored while the previous increment's review ran, and each review landed as its own commit (`25d69fe`, `97e7384`, `ab412fc`, `837abd3`).
- **Privacy guards held (control exercised).** No account name, home path, email or handle entered the batch: `state.json` `owner` is `OMITTED` by design (A-110, `tests/test_no_operator_paths.py`); the UX walkthrough transcript redacts the account to `<user>`; the guard and `tests/test_fold.py` pass on this P5/P6 tree.
- **Honest scoping of what is NOT proven.** The Python 3.10 floor is recorded `not-run` (G-003, B-148) rather than inferred from the AST proxy; three contract/behaviour differences are accepted deviations with the shipped behaviour normative (D-1…D-3).

### What didn't / friction
1. **Whole-corpus guards were outside every increment's targeted run (3 closing-gate regressions).** Evidence: DDR §C table and `04-validation.md` G-001 — the orchestrator's first full run was 4013 passed / 3 failed: `test_fold::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts` (live U+200B/U+2028/U+202E in `tests/test_relmap_model.py` and three batch records, LED `.69`) and `test_repair_artifact_claims::test_every_path_line_citation_resolves[search.py]` and `[04-gate-findings-disposition.md]` (a bare `model.py:149` became ambiguous the moment `mapper/relmap/model.py` existed, LED `.70`/`.71`). The original run's transcript was not stored; the DDR replaced it with a labelled reproduction.
2. **Reviewer-surviving mutants (the author's battery was not enough).** Four times an independent party's own mutant stayed GREEN against a battery reported as fully killed:
   - Inc-2 mutant D (drop the edge-type filter in `_lacks`): `50 passed`; the packet's "15/15 killed" did not cover the conjunct "edge is of the row's type" (`review-inc002.md` F1, MAJOR, BLOCK-UNTIL; closed at `f02dbbd`, RED in `evidence/inc2f-red-mutant-d.txt`).
   - Inc-4 mutant C (`if "." in s:` → `if True:`, the dot guard in the unparsed-count sibling rule): `38 passed` (`review-inc004.md` F1, MINOR; closed with `test_unparsed_count_of_a_dotless_hlr_is_not_doubled`, `evidence/inc4f-red-f1-mutant-c.txt`).
   - Inc-5 M-RMU-9 (print the resolved path in the sources line): defined in the ledger (`.59`), never run, and the two tests the ledger named for it did not kill it — only the 120-character cut test did (`review-inc005.md` F1, MEDIUM; closed with the end-to-end sources-line assertion). *This one is beyond the three the commission listed; the record carries it.*
   - DDR M3 (count excluded rows with an unknown status): the unknown-status arm of ledger `.61` was pinned by no node (software-dev S-1); closed by `test_unknown_status_counts_kept_nodes_only` (LED `.72`, `evidence/ddr-m3-pin-red-green-2026-10-25.txt`).
3. **P2 needed three passes; the contract outgrew its budget.** First pass: architect, QA and security all `iterate-to-refine` — 39 findings (1 blocker, 22 majors, 16 minors), amended under rulings R1–R16 (LED `.1`–`.16`). Second pass: security and architect approve, QA iterate (13 new findings; 2 majors N-1/N-2). Third pass (QA only): N-1/N-2/N-4/N-5/N-6 verified, N-3 reopened, one new MAJOR X-1 (AT-122 arm 3 could not reach the escaper with U+2028), dispositioned without a fourth pass (LED `.29`–`.31`). Contract size: 87,832 characters at the first pass note, 92,888 after the R1–R16 amendment, **109,299 measured on the final file** against the 54,000-character `V26` budget (a NOTICE, never a block). The defects P2 found were mostly in what had the least structure: AT bodies existed only as ids (Q-2), AT-120/AT-123 were not black-box (A-6, Q-4, Q-14), and absolute counts of a living file were pinned as oracles (A-4).
4. **Stray files and stat-only index marks in the shared worktree.** Leftovers seen while pipelining: a file literally named `=` and a scratch copy placed outside the repository, plus stat-only entries in the index (files that `git status` listed as modified with no content difference) after authors and reviewers touched the same tree. None reached a commit (the final tree has no stray file), but each cost a manual check. Source: the dev-flow worker's brief for this unit; no packet records them, so there is no transcript to cite.
5. **Kimi quota ran out; all work moved to Claude Sonnet subagents.** Every reviewer line in the records reads `Claude Sonnet subagent` (`02-review.md`, DDR). Source: the orchestrator's brief; the records carry no quota event. The reviewers' independence from the author held (separate subagent, separate transcript), but the switch happened mid-batch and is not marked in `state.json`.
6. **The Python 3.10 floor is unproven (B-148).** The package declares `>= 3.10`; the machine has 3.12 and 3.14 only and the project has no CI. `test_py310_floor` (AST) and `test_stdlib_bans` (banned-name census) are a proxy; the real run is `not-run`, owner the operator. One more instance of the A-11 finding ("CI owes the real run" while there is no CI).
7. **Records weight.** `V41` (evidence cited by bare name, not under the evidence home), `V56` (transcripts cited but unreadable from the packet's location), `V9` (no SOURCE count) and `V53` (specified-but-not-yet-written test names) produce hundreds of NOTICEs on this batch's packets (751 notices at the P5 gate, none a block once the plan cell is current). They are NOTICEs by design on a living record and were not chased; they do cost the reader time.

### Scope drift (planned vs actual)
| Planned | Actual | Note |
|---------|--------|------|
| 4 stories, 5 increments (Inc-1 profile/model, Inc-2 gaps, Inc-3 yamlscan + store delegation + descriptor, Inc-4 canon adapter, Inc-5 audit block) | 4 stories, 5 increments + 1 closing-gate fix unit (`456da08`, `934e935`) + 1 post-gate test (LED `.72`) | the fix unit and the extra test are corrections of this batch's own defects, not new scope |
| US canon, AT → test table, `covers`/`binds`/`verifies` edges | only HLR/LLR skeleton and `refines` derived; 7 of the 8 gap kinds have formatter + Layer A evidence only | declared in the contract (OQ-R1-2); sources do not exist yet (B-141) |
| Contract at ≤ 54,000 characters | 109,299 | see friction 3 |
| P2 in one pass | three passes, P1 re-entered once | friction 3 |
| `mapper --audit` byte-identical but for the added block | true for the report and exit code; the `verdict:` line is no longer the LAST line (UX MAJOR-4), documented and accepted | a CI step must read `grep '^verdict: '` |

### Metrics (full)
| Metric | Value |
|--------|-------|
| Iterations per station | `{P0:0, ARQ:0, P1:1, P2:0, PDR:0, P3:0, DDR:0, P4:0, P5:0, P6:0}` (`state.json`; P2 ran three review passes inside one station visit) |
| Findings recorded | P2: 39 (first pass) + 13 (second) + X-1 and the reopened N-3 (third) = **≥ 54 rows**; PDR: 38 conditions (4 reviewers); P3 increment reviews: 22; closing full-suite gate: 3; DDR: conditions dispositioned one by one in DDR §C (4 reviewers, no blocker) |
| Findings by severity (P2 first pass) | blocker 1 · major 22 · minor 16 |
| Findings by severity (P3 independent reviews) | blocker 0 · major/medium 2 (Inc-2 F1, Inc-5 F1) · minor 20 (Inc-1 F1–F5, Inc-2 F2–F5, Inc-3 MINOR-1–3, Inc-4 F1–F4, Inc-5 F2–F5) |
| Where caught (P2 / P3 gate / closing gate) | ≥ 54 / 22 / 3 — the 3 closing-gate defects are the only ones a gate EARLIER than the full suite could have caught |
| Mutants | battery: Inc-1 19/19, Inc-2 15/15, Inc-3 20/20, Inc-4 19/19, Inc-5 27/27 = **100/100 killed**; plus reviewer/DDR mutants that SURVIVED the author's battery: 4 (Inc-2 D, Inc-4 C, Inc-5 M-RMU-9, DDR M3), each killed after its added test |
| Test ledger (base − D + A = post) | `3579 − 4 + 447 = 4022` selected at `934e935` (4046 collected, 24 deselected); full suite 4017 passed, 0 failed, 2 skipped, 3 xfailed; +1 node after the DDR gate (4023) |
| Files touched · increments (cap trips) | product: 7 modules under `mapper/relmap/` + `mapper/yamlscan.py`, edits to `mapper/store.py`, `mapper/reqharness/audit.py`, `mapper/app.py`; every increment ≤ 4 source files per PLAN (`A-15`); cap trips: none recorded |
| Requirement ledger | `LED-2026-10-25-relmap-r1-batch.1` … `.76` (76 entries) |
| Duration | `decisions_log` carries dates only (all `2026-10-25`). From commit times on the branch: batch opened 08:05, P2 closed 08:57, Inc-1 code 09:12, Inc-4 approved 11:06, Inc-5 approved 11:19, closing-gate fixes 11:55–11:57, full-suite transcript 12:29, P4 record 12:44, DDR sealed 13:08 — about five hours wall clock. Per-phase effort/tokens: `not recorded` |

### Root causes (only if a phase took ≥2 iterations)
- **P1 re-entered after the first P2 pass → the contract was drafted before its acceptance tests existed.** The ATs were ids without bodies and one limb (byte-identity) was asserted by a test that could not fail (Q-1/A-1/Q-2). The fix was 16 rulings and an AT section; the cost was two more review passes. Cause: AT bodies are written AFTER the review that needs them.
- **P2 second/third passes → each amendment created new surface to review.** Ledger entries `.17`–`.31` mostly refine wording the first amendment introduced (closed cause set K1–K17, escape arms, hook semantics). A closed cause set is correct, but it multiplies exact-text requirements, each of which needs an AT arm.
- **Closing-gate regressions (not an iteration, but the same family as the hygiene batch's B1 miss).** The increment gate is scoped by the files an increment edits; the failing guards scan every tracked file. A census by import surface cannot see "a new file whose basename already exists elsewhere" or "a literal coerced code point in any batch record".

### Process / workflow findings
| # | Finding | Suggested workflow change |
|---|---|---|
| W-1 | Whole-corpus guards run only at the full-suite gate | the increment gate's guard set lists every guard that scans the whole tree (done in this batch's PLAN); consider a flow-level rule: a guard that scans all tracked files belongs in every increment's gate |
| W-2 | A mutant battery authored by the same party that wrote the tests reports "N/N killed" and is blind to the conjuncts it never thought to break | the independent reviewer runs **at least one mutant of their own per increment** and the packet cell records it by name; a battery claim is not complete until that line exists |
| W-3 | The 54,000-character `V26` budget is a NOTICE and was exceeded twice over without any gate stopping | decide: raise the budget for `full` batches that carry AT bodies, or split the contract (see Control lineage C-3) |
| W-4 | Pipelined author/reviewer work in one worktree leaves stat-only index marks and stray files | scratch under a named folder; `git update-index --really-refresh` before a review starts |
| W-5 | A runner/model switch mid-batch (quota) is invisible in `state.json` | record the runner per `decisions_log` entry, or note a switch as a decision |
| W-6 | A transcript the orchestrator did not store (the original 4013/3 run) had to be rebuilt as a "labelled reproduction" | the orchestrator stores every gate transcript, failing ones included, at the moment of the run |

### Product findings
- **R1 delivers a correct, bounded, headless read model**, but R1's live output is flat: all seven gaps tie at reach 0 and rank only by severity then id, so the reach ranking is not yet exercised by real data (DDR §E 5, B-141).
- **The canon needs hygiene** before the structure block reads clean: 7 rows do not parse (a pipe inside the statement) and 3 LLRs resolve to no HLR (B-142); rule D-1 (LLR → HLR by id) is a convention, not canon content.
- **Presentation sits in the data layers** (`cut`, `DISPLAY_MAX` in `relmap/model.py`; `refusal_line` in `descriptor.py`) — move to a leaf before R2 adds a second printer (B-153).
- **The pre-existing `repo:` line prints the absolute repository path** (B-155), a CI-log exposure older than this batch.
- **`build_map` runs twice per derivation** (about one second on the 100,001-row canon test; B-146).

### Control lineage
- **New controls proposed this batch** (owner · status):

| # | Control | Origin finding | Owner | Status |
|---|---------|----------------|-------|--------|
| C-1 | The guard set every increment runs names `tests/test_fold.py` and `tests/test_repair_artifact_claims.py`; and when an increment ADDS FILES, two censuses run: a new file whose basename already exists elsewhere, and a literal coerced code point in any tracked file or batch record | friction 1; DDR §C *Lesson (guard set)* | orchestrator (PLAN guard line) | **adopted** in `PLAN.md` (guard set line 94) from the P3 follow-up on; carry to the next batch's PLAN seed |
| C-2 | Each independent code review records at least one reviewer-authored mutant by name and its result; "N/N killed" in a packet is not final until that cell is filled. Where a reviewer mutant survives, the closing test is added and the mutant re-run RED (the Inc-2 F1 / Inc-4 F1 / Inc-5 F1 / DDR S-1 pattern, already practised) | friction 2 | orchestrator + `code-reviewer` | propose / adopt-next-batch |
| C-3 | **Contract shape, not just budget.** Keep `01-requirements.md` to the statements (US/HLR/LLR with ids) and move the AT bodies and the AT↔requirement matrix to an acceptance-design companion (`01b-acceptance-design.md`, the file other batches already use), mutant tables to the ledger, and amendment history to the ledger only. Decision owed: whether `V26` stays 54,000 for the contract alone, or `full` batches get a larger limit | friction 3; W-3 | flow maintainer (operator decides) | propose; carried as B-156 |
| C-4 | Parallel worktree hygiene: scratch under one named folder inside the unit's scratch directory (never beside the repo, never a bare symbol name); run `git update-index --really-refresh` and `git status --short` before every review hand-off; a stray file is removed or excluded before the review starts | friction 4; W-4 | orchestrator | propose / adopt-next-batch; carried as B-157 |
| C-5 | Record the runner/model switch as a `decisions_log` entry when a quota or tool change moves work to another agent family | friction 5; W-5 | orchestrator | propose |
| C-6 | A real-interpreter run of the declared floor is an operator action with a date, not a proxy: add the Python 3.10 run to the next CI/operator checklist | friction 6; B-148 | operator | open (B-148) |

- **Prior controls exercised:** held — privacy guard A-110 (no operator path in any tracked file), the independence of review from authoring, the change-first census (B1 fired; per-increment reverse census held for `run_cli`, `_prescan_sidecar`, `test_a3_census.py:329`, the A3 pin unmoved at 86), RED-before-GREEN, hash-verified mutant restore. Stress-tested — the signed test-ledger arithmetic (balance reconciles against actual collects on a clean detached `194f885` worktree). Near-miss — the hygiene batch's B1 lesson ("a census scoped by import surface misses fixture content") recurred in a new form at the closing gate (friction 1); the control did not exist at the file-basename and code-point level until this batch.

### Open / deferred items → next batch
| Item | Type (process/product) | Reason deferred | Trigger / owner |
|------|------------------------|-----------------|-----------------|
| **R2 views** (matrix + lens, gaps view, node-sheet sections) re-skinned through `Canvas`, scalecheck at the 118 reference width — prototype verdicts exist in `prototypes/round-2026-10-23/verdict-2026-10-24.json` (git-ignored in the main checkout; not present in this worktree and not read in this unit) | product | a screen/view batch; R1 is headless by design (B-140) | next batch; owner: orchestrator with the operator |
| **R2 PDR inherits DDR §E items 10–12**: move `cut`/`DISPLAY_MAX`/`refusal_line` out of the data layers (B-153); derive-per-descriptor seam for R5 (B-154); decide the hook per-line length bound (B-147) | product | owned by the R2 PDR (OP-11) | R2 PDR; owner: architect |
| **The UI batch from the round-2026-10-23/24 verdicts** | product | verdict content not read in this unit; scope to be taken from the verdict files at the next P0 | next P0; owner: orchestrator |
| B-140 series R2–R5 (R3 evidence search behind `security-check-before-tools`, R4 timeline, R5 `lineage`) | product | each its own batch, in order | per series |
| B-141 US canon and AT → test table do not exist ("B-next-2") | product | sources must exist before 7 of 8 gap kinds have end-to-end evidence | decide formats before R2 |
| B-142 canon hygiene (7 unparsed rows, 3 unlinked LLRs) | product | editing a canon row changes its digest | a canon-hygiene act, own batch |
| B-143 MAP-TYPES §3.2 `binds` prose contradicts the rule | product | the file lives in the QuickMap repo | operator, QuickMap repo |
| B-144 third prescan copy in `reqharness/config.py`; B-145 `Profile.__post_init__` gaps; B-146 double `build_map`; B-147 hook per-line bound | product | accepted watch-items | before R2 / R5 as each names |
| B-148 real Python 3.10 run | process | no interpreter, no CI | operator |
| B-149 three contract wordings differ from shipped behaviour; B-150 UX observations; B-151/B-152 cause classification and hygiene; B-155 `repo:` line path | product | accepted deviations D-1…D-3, cosmetic | any later `--audit` change |
| **B-156 contract shape and `V26` budget (C-3)**, **B-157 worktree hygiene (C-4)**, **B-158 reviewer-mutant cell and runner record (C-2, C-5)** | process | new from this post-mortem | flow maintainer / orchestrator |

**Backlog reconciliation (mandatory close step).** Done for the carries: B-140…B-155 were recorded in `.dev-flow/BACKLOG.md` during the batch; this unit appends B-156…B-158 and records no item as shipped (the batch closed no pre-existing backlog item). **Still owed at merge:** refresh the header's `origin/master` tip SHA and the "last refresh" line, and mark the PR number and merge SHA once the operator merges (merge authority was NOT granted at kickoff; the PR is not opened by this unit). The default branch is `master`.

### Working-file reconciliation (C-44) — MANDATORY, every file this batch touched
> Sweep run 2026-10-25 in the worktree `feat/relmap-r1` only; the main checkout and any auxiliary repository (skills, commands, config) were not swept in this unit. `git status --short` before this unit's edits was clean; `git log @{u}..HEAD`: no upstream configured for the branch (never pushed — no `origin` push by this unit).

| Repo | File(s) | Terminal state | Landing / backlog ref |
|------|---------|----------------|-----------------------|
| mapper (worktree, branch `feat/relmap-r1`) | `mapper/relmap/*`, `mapper/yamlscan.py`, edits to `store.py`, `reqharness/audit.py`, `app.py`, tests, fixtures, batch records through `3d76687` | committed, **not pushed, no PR yet** | operator merges; branch `feat/relmap-r1` |
| mapper (worktree) | `05-postmortem.md`, `06-docs/*`, `PLAN.md`, `BACKLOG.md`, `state.json` | committed by this unit (see its commit id in the report), not pushed | same branch |
| mapper (main checkout) | `prototypes/round-2026-10-23/verdict-2026-10-24.json` | git-ignored there, not touched by this batch | referenced by B-140 / R2 |
| unit scratch (outside the repo) | a scratch copy of a repository file, and the stray file `=` | seen during the batch; the final tree holds neither | 🗑️ discarded; control C-4 |

- **Found before the batch:** none — no tracked file was modified when the batch began (the batch opened in a worktree of a clean primary checkout; `state.json` `owner` note).

**Conditional gate verdicts:** the PDR and DDR closed *approved with conditions*. Discharge verified by re-reading:

| Conditional item | Discharged? | Verified how |
|---|---|---|
| PDR: 38 conditions, each with an owning increment gate | ✅ | DDR §C *Conditions of the DDR reviews* and §A/§B tables re-read: "All 38 PDR conditions are discharged" |
| DDR: M3 unknown-status arm pinned (software-dev S-1) | ✅ | `ddr-m3-pin-red-green-2026-10-25.txt`, LED `.72`, node `tests/test_relmap_adapter.py::test_unknown_status_counts_kept_nodes_only` |
| DDR: real reproduction of the 3 escaped regressions (QA F-1/F-2) | ✅ | `ddr-reproduction-escaped-regressions-2026-10-25.txt` (3 failed on `6331206`, mutants RED then restored sha256-verified) |
| DDR: README Audit section; residual risks owned by the R2 PDR | ✅ (owner recorded) | DDR §E items 10–15, BACKLOG B-151…B-155 |
| P4: Python 3.10 real run | ❌ not-run | B-148, operator |

### Evidence checklist — architect + qa-reviewer
- architect — (a) module boundaries and the frozen `relmap` public names held: ✓ DDR §A/§B, additions only, two additive revisions in §D; (b) dependency edges match ARCHITECTURE R-016/R-017: ✓ `tests/test_relmap_isolation.py` AST census; (c) residual design risks owned: ✓ DDR §E 1–15 with BACKLOG ids; (d) Python 3.10 floor: ✗ proxy only, B-148.
- qa-reviewer — (a) 35/35 requirements and 12/12 ATs traced to executed nodes: ✓ `06-docs/traceability-matrix.md`, `04-validation.md`; (b) ledger reconciles against collects: ✓ `3579 − 4 + 447 = 4022`; (c) escaped regressions reproduced RED/GREEN: ✓ `ddr-reproduction-escaped-regressions-2026-10-25.txt`; (d) mutation evidence independent of the author: ✓ with the four surviving reviewer/DDR mutants recorded (friction 2); (e) real interpreter at the declared floor: ✗ `not-run`; (f) original first full-run transcript: ✗ not stored (labelled reproduction used instead).
