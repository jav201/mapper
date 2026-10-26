# Post-mortem — mapper — Batch 2026-10-25-relmap-r2-batch

> **Artifact language:** English (`state.json` `language`).
> Phase 5 artifact. Co-authors (roles executed by the dev-flow worker as a records-only unit; no product or test code changed): `architect` + `qa-reviewer`. **LOCAL STAGING:** the canonical copy is `artifact_homes.postmortem` in the vault, written only by `/dev-flow-sync`.
> Source of every number below: the batch records (`PLAN.md`, `02-review.md`, `03-increments/`, `04-validation.md`, `design/DDR-…`, `design/design-proposal.md`, `01-requirements-ledger.md`, `state.json` `decisions_log`) and `git log` of branch `feat/relmap-r2`. A figure that no record carries is marked `not recorded`.

## 0 · Gate record — which tree this close gated

| Field | Value |
|---|---|
| Gate record | `PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 python <bundle>/scripts/devflow-validate.py --brief .` → exit 0, `0 block` · 2026-10-26 (the P5/P6 records gate; this is NOT the close gate: the batch is not merged and not synced) |
| Gated tree | `55205081df3081f4a780835523b416dda868ca10` · dirty — the P5/P6 records of this unit (`05-postmortem.md`, `06-docs/executive-summary.md`, `06-docs/functionality.md`, `06-docs/traceability-matrix.md`, `PLAN.md`, `BACKLOG.md`, `state.json`, `01-requirements.md`, `01-requirements-ledger.md`, `design/design-proposal.md`, `design/DDR-2026-10-25-relmap-r2-batch.md` (the declared COND-DDR-1 records-pass amendment), `03-increments/increment-007.md` §2 rows for the V59 limb, `evidence/p5-cond-ddr2-*.txt`, and `REQUIREMENTS.md`: the canon fold of the batch's requirement ids by `devflow-init.py --fold-canon`) |

## 🔑 At a glance (read first)

- **Outcome:** closed with carry-over. Validation PASS-WITH-NOTES (72/72 requirements, 23/23 ATs, 2 accepted deviations); DDR `approved with conditions` — **both MAJOR conditions discharged at this close** (COND-DDR-1 citations re-repaired, COND-DDR-2 pre-fix REDs captured); full suite 4226 passed / 0 failed at `cdc4491`. P1 took 2 amendment iterations; P2 ran two review passes inside one station visit; every other station 0 recorded iterations.
- **Top 3:** ① **worked** — independent review at every gate earned its cost again: the Inc-2 review caught the D1 axis defect BEFORE any lane forked, reviewer-authored mutants found 4+ test holes the author batteries missed, and the DDR's re-read rule caught a falsified P3 discharge (the third citation drift). ② **didn't** — the whole-corpus census escape recurred one layer up (3 closing-gate failures), and a committed evidence transcript leaked the account path after its unit reported green. ③ **root cause** — guard sets and citation repairs ENumerated by hand are lagging indicators: they name the last escape's files, so the next batch repeats the escape with the next layer.
- **New control this batch:** the per-increment guard set is DERIVED from "every test that derives its input set from the whole tracked tree", not listed by hand (see Control lineage L-1); and the citation census gains a content anchor (BACKLOG **B-166**).
- **Open items → next batch:** 20+ — the biggest: the R-series continues (R3 FTS evidence search, R4 timeline, R5 metro/lineage) and the UI batch from the round-2026-10-23/24 verdicts.
- **Metrics:** iterations P1=2, others 0 (P2: two passes in one visit) · findings P2 25 / PDR 13 conditions / P3 reviews ~19 / closing gate 2 escapes / DDR 7, all dispositioned · mutants 62 battery + ~7 review + 6 DDR, all killed after fixes · ledger `4023 − 4 + 212 = 4231` · LED `.1`–`.33`.

> Enough to know the batch's health and what carries forward. Detail below only for the why.

---

## Detail (reference)

### What worked
- **The trunk-review-before-fork rule paid off (L-3).** The D1 amendment (`row_count(state) -> int`, one clamped cursor per view on each view's own axis, the per-view toggle word, the `lens` field dropped) was found by the Inc-2 INDEPENDENT review (`evidence/review-inc002.md`, `iterate` BLOCK-UNTIL F1/F2) and ruled at trunk `64bc1bc` BEFORE lanes 3/4/5 forked — one ruling instead of three lanes improvising (the DDR §A.1 "why" verbatim). The as-built surface is pinned by the `test_d1_*` freeze nodes.
- **The 4-lane swarm merged with zero source conflicts (L-4).** Strict file ownership held across `3b9eada → 7a56db7`: each lane 1–2 SOURCE files, trunk 4/1/4, and the follow-up `fb336ed` touched tests across lanes by declaration (each of its 3 source edits the lane's OWN review discharge — verified by both the architect and the software-dev at the DDR). The JOIN-point reverse census — the one check impossible from inside a lane — re-ran green on the joined tree.
- **Independent review found real defects the author's own battery missed, at every gate.** P2: 21 first-pass findings (2 blocker, 7 major, 12 minor) + 4 second-pass (incl. P2V-1, a V10 blocker invisible at P1); PDR: 13 conditions; P3: per-increment reviews with BLOCK-UNTILs; DDR: 2 MAJOR + 5 MINOR, each re-read against the named artifact line. Every finding closed with a RED/GREEN transcript.
- **Reviewer-authored mutants stayed a live control (L-6, C-2).** Reviewer/DDR mutants found 4+ test holes again: the Inc-2 follow-ups (M-REV-3, M-FU-1/2, killed by the `64bc1bc` arms), Inc-5 (M-REV-1 degenerate-height, M-REV-2 INK→MUT id-style), Inc-6 (M-REV-HOME-1 duplicate row keys, killed by the kind-prefixed keys at `fb336ed`), Inc-6b (M-R-6B-2 palette independence), and 6 mutants at the DDR gate under C-2 (all KILLED, all restores sha256-verified).
- **RED-before-GREEN with stored transcripts, and honest limits.** Every increment stores code-absent REDs, GREENs and hash-verified mutant batteries; the two escaped regressions of this batch had their pre-fix REDs MISSING from the record — COND-DDR-2 closed that gap at this close with labelled reproductions on detached scratch checkouts (`evidence/p5-cond-ddr2-*.txt`). The Python 3.10 floor is recorded `not-run` (B-165) rather than inferred.
- **Privacy guards held on this tree (L-2 exercised).** No account name, home path, email or handle entered the batch records: `state.json` `owner` is `OMITTED` by design (A-110); every transcript this unit authored passed the Python sanitizing filter that refuses to write on any profile segment; the A-110 guard + `tests/test_fold.py` ran on the STAGED tree before this commit (green).

### What didn't / friction
1. **The whole-corpus census escape recurred, one layer up (the seeded P5 note, full text below).** The orchestrator's clean full-suite run at the close of Phase 3 reported `4223 passed, 3 failed`. All three failures sat in whole-corpus census tests that no increment's guard set named: `tests/test_darkside_census.py::test_hue_census_every_severity_and_busy_site_is_classified` (the 12 new severity/busy sites in the relmap matrix/sheet renderers derived by the census but registered by no one), and `tests/test_inc9.py::test_a112_the_chrome_is_english[seat]` + `test_cd25a_the_seat_diff_is_exactly_what_inc9_declares` (the relmap seat's words and rows undeclared in the chrome lexicon and the seat diff). Every increment's own guard run was green when it landed.
   **Root cause.** The R1 batch's closing-gate escape had the identical shape — its post-mortem's top "didn't" was "whole-corpus guards were outside every increment's targeted run (3 closing-gate regressions)" — and R1's adopted control added `tests/test_fold.py` + `tests/test_repair_artifact_claims.py` to the per-increment guard set. That control named the two files the R1 escape hit; it did not generalise to the next layer of whole-corpus censuses. A guard set defined by enumerating the files the LAST escape hit is a lagging indicator: each batch can repeat the escape with the next corpus test layer.
   **Repair (test-side only, no product code touched).** `LED-2026-10-25-r2.31`: the 12 sites classified individually with judgements pinned by the batch's own requirement tests (pin 82 → 94); the ten painted seat words plus the six `r`-prefixed group handles added to `CHROME_LEXICON`; the 13 `relmap` rows declared in `DECLARED_ADDED`.
   **Control adopted at the time, generalised here (L-1).** The PLAN's guard-set definition now names `tests/test_darkside_census.py` and `tests/test_inc9.py` alongside `tests/test_fold.py` + `tests/test_repair_artifact_claims.py`, so every targeted run in this batch derives the whole-corpus layer by construction, not by enumeration of the last escape. The carry-forward for the next batch: generalise the control wording from "these N files" to "every census test that derives its input set from the whole tracked tree" — see Control lineage.
2. **A committed evidence transcript leaked the account path AFTER its unit reported green (L-2).** Run 2 of the P4 gate failed A-110: the census unit's `evidence/p3-census-amendment-green.txt` had been committed unredacted (3 header lines carried the account profile segment). The leak was patched after the fact (`cdc4491`, in place) — the adopted control now forbids that path: transcripts are sanitized AT AUTHORING TIME with a PYTHON filter (never `sed` after commit), and `tests/test_no_operator_paths.py` runs on the STAGED tree before every records commit (B-164).
3. **The citation repair drifted for the THIRD time (COND-DDR-1).** R1 repaired the census citations; the P3 re-repair (`75f9e28`) drifted again before the lanes forked (`8be99a3` shifted the cited lines); no guard catches symbol-at-line drift (`test_repair_artifact_claims.py` checks past-EOF only). The DDR re-opened it as a MAJOR condition; this close re-repaired all sites by content match and recorded the content-anchor census as B-166 — the third hand repair of the same class is the argument for the control, not the fix.
4. **Two escaped defects reached the full-suite gate.** Both were of this batch's own making (targeted-only guard runs; an unredacted transcript), both fixed pre-validation, both now have stored pre-fix REDs (COND-DDR-2). They are the only defects a gate EARLIER than the full suite could have caught — see L-1.
5. **Kimi crashed at a session end ("workspace not materialized") (L-5).** The crash terminated a worker session after its records commits; it was harmless — the tree was verified by re-reading git state before any continuation, and nothing was re-done or lost — but crash-recovery-by-re-read is now an explicit step, not an assumption. Source: the dev-flow worker's brief for this unit; the records carry no transcript (no output was produced).
6. **Records weight (same family as R1's friction 7).** `V41`/`V56`/`V9`/`V53` produce hundreds of NOTICEs on a living batch (919 notice · 55 n/a at the DDR gate); they cost the reader time and were not chased.
7. **The Python 3.10 floor is unproven for the R2 code too (B-165, re-stamps B-148).** AST guard + banned-name census are the proxy; the real run is `not-run`, owner the operator.

### Scope drift (planned vs actual)
| Planned | Actual | Note |
|---------|--------|------|
| Inc-1 text leaf (5 SOURCE) | Inc-1a (4) + Inc-1b (1), both trunk | COND-ARCH-2/COND-QA-1 + the orchestrator ruling `78ee993` — the ≤4 cap held |
| D1 frozen at the PDR | D1 amended at trunk Inc-2 BEFORE any lane forked (`64bc1bc`) | found by the Inc-2 independent review; a declared ruling annotation, not a silent edit |
| 4 lanes + join | 4 lanes + join, zero source conflicts; as-built counts `4/1/4/1/1/1/2/0/1` (Inc-6b shipped 0 SOURCE) | DDR §H D6 quotes as-built; the planned `…/2/2/1` wording was an F-2 fix at this close |
| `k` toggle CONTINGENT at the PDR | `k` SHIPPED (ruling at P2, normative in LLR-RVH.4.1 after P2Q-1) | decided before the PDR; recorded in DDR §A.3 |
| 2 P2 passes | 2 passes (first: 21 findings; second: 4, incl. the V10 blocker P2V-1) + a surgical re-amendment | better than R1's 3; the C-3 contract-shape control (AT bodies in `01b`) held — the contract stayed inside its V26 budget (96,092 chars declared at P1) |

### Metrics (full)
| Metric | Value |
|--------|-------|
| Iterations per station | `{P0:0, ARQ:0, P1:2, P2:0, PDR:0, P3:0, DDR:0, P4:0, P5:0, P6:0}` (`state.json`; P2 ran two review passes inside one station visit) |
| Findings recorded | P2: 21 (first pass) + 4 (second) = **25**; PDR: 13 conditions (3 MAJOR, 10 MINOR); P3 independent reviews: 001ab N-1/N-2 + OBS-1, 002 F1/F2 (BLOCK-UNTIL), 003 2 MINOR, 004 3 MINOR, 005 2 MAJOR (test-only) + 2 MINOR, 006/006b/007 nits — **~19 rows**; closing full-suite gate: 2 escapes (the 3-node census trio + the A-110 transcript); DDR: 7 (2 MAJOR, 5 MINOR) |
| Findings by severity (P2 first pass) | blocker 2 · major 7 · minor 12 |
| Where caught (P2 / PDR / P3 reviews / closing gate / DDR) | 25 / 13 / ~19 / 2 / 7 — the 2 closing-gate escapes are the only ones an earlier gate could have caught (L-1) |
| Mutants | increment batteries: 1a 3, 2 11, 3 11 (ten defined + M-RVM-1 dual-form; M-RVM-4 undefined — B-162), 4 13, 5 12, 6 7, 6b 2, 7 3 = **62/62 killed**; review mutants ~7 (M-REV-3, M-FU-1/2, M-REV-1/2, M-REV-HOME-1, M-R-6B-2) each killed after its arm; DDR gate 6/6 under C-2 |
| Test ledger (base − D + A = post) | `4023 − 4 + 212 = 4231` collected (24 deselected both sides); gate run 4226 passed, 0 failed, 2 skipped, 3 xfailed at `cdc4491` |
| Requirements / ATs | 20 HLR + 52 LLR (72/72 pass) · AT-130…AT-152 (23/23) · TC-RM-04…30 (27/27) |
| Files touched · increments (cap trips) | product: `mapper/relmap/text.py` (new leaf) + re-points in `relmap/{model,descriptor,audit,adapter}.py` + `mapper/screens/relmap/{__init__,screen,base,matrix,gaps,sheet}.py` (new) + `mapper/{keymap,screens/home,app}.py` + `mapper/reqharness/audit.py`; every increment ≤ 4 SOURCE (`A-15`), cap trips: none (trunk Inc-1a/Inc-2 at 4 declared) |
| Requirement ledger | `LED-2026-10-25-r2.1` … `.33` (33 entries) |
| Duration | `decisions_log` dates 2026-10-25 (batch open, P1, P2, PDR, all increments, join) → 2026-10-26 (P4 validation, DDR seal, this close). Per-phase effort/tokens: `not recorded` |

### Root causes (only if a phase took ≥2 iterations)
- **P1 = 2 iterations → the swarm-drafted contract carried census and wording defects the gate caught at P2** (26/52 vs 20/51, the seat-scope contradiction ARC-02, the ruling fold-backs QA-04/F-UX-1). The C-3 companion (`01b-acceptance-design.md`) and the ledger rulings (LED `.01/.02`) resolved them in two amendments; the second P2 pass then found only 4 rows. Cause: draft-time totals asserted, not measured (the re-count was by script).
- **P2 second pass → the amendment itself created new surface** (the six IFC FLOW blocks' arrow-form NODES, invisible to V10 at P1 — the same blind spot as VAL-01/02). Cause: a validator station-condition (past-Phase-1) made the P1-measured "0 block" false at P2; the re-run must be measured at the true station.

### Process / workflow findings
| # | Finding | Suggested workflow change |
|---|---|---|
| W-1 | The whole-corpus escape recurred one layer up: an enumerated guard set names the last escape's files (friction 1) | **L-1:** the next batch's P2/PLAN defines the guard set DERIVATIVELY — "every test that derives its input set from the whole tracked tree is in every increment's guard set" — and the seed script lists such tests by inspecting fixtures/census input classes, not by hand |
| W-2 | An evidence transcript leaked the account path and was patched after commit (friction 2) | **L-2 (adopted, B-164):** transcripts are sanitized at authoring time by a Python filter that REFUSES to write on any profile segment; `test_no_operator_paths.py` runs on the STAGED tree before every records commit |
| W-3 | A hand-repaired citation drifted a third time; the guard checks existence, not symbol-at-line (friction 3) | **B-166:** the citation census anchors on content (re-derive the line from the named symbol), not on a line-count existence |
| W-4 | A runner crash ("workspace not materialized") ended a session mid-close (friction 5) | **L-5:** after any runner crash, verify the tree by re-reading git state before continuing; never assume the crash lost or kept work |
| W-5 | Two closing-gate escapes were the batch's own defects caught only by the full suite (friction 4) | folded into L-1 (the only structural fix); the orchestrator stores every gate transcript, failing runs included (R1's W-6, still open) |

### Product findings
- **The relation screen ships honest at every edge**: declared test-column gap (no phantom AT/TC columns until B-141), honest zeros (`000`, `not computed`), closed-set refusals, hostile payloads literal on one row — the matrix/gaps/sheet renderers and the shell all pin these.
- **Parked cosmetics**: the Home kind/name column clips the painted values at both widths (B-159); the unavailable refusal line paints twice (B-163); the by-kind mid-band split is unsignalled (B-160); the hook bound counts code points, not cells (B-161).
- **Carried from R1, now discharged**: the presentation leaf (B-153 → `relmap/text.py`, AT-150/151) and the double `refusal_line` import path (B-151 partially — the re-export dropped; the K5 text twice is B-151's remainder).
- **Still carried**: double `build_map` per derivation (B-146), default-only derivation seam for R5 (B-154), defensive branches (B-152), the `repo:` line path (B-155), the third prescan copy (B-144), `Profile.__post_init__` validation (B-145).

### Control lineage
- **New controls proposed this batch** (owner · status):

| # | Control | Origin finding | Owner | Status |
|---|---------|----------------|-------|--------|
| L-1 | The per-increment guard set is derived from "every test that derives its input set from the whole tracked tree" — enumerated by inspecting the tests' input classes, never listed by hand; the enumeration is re-derived at each batch's P2 | friction 1 (the second recurrence of the R1 escape, one layer up) | orchestrator (next batch's P2/PLAN seed) | **adopt-next-batch**; this batch's mid-batch extension (darkside census + inc9 into the PLAN guard line) is the interim form |
| L-2 | Evidence transcripts are sanitized at authoring time by a Python filter that refuses to write on any account-profile segment; the operator-path test runs on the STAGED tree before every records commit | friction 2 (the A-110 run-2 failure) | orchestrator (standing records-commit control) | **adopted** — exercised by this unit (both COND-DDR-2 transcripts and the staged-tree guard run) |
| L-5 | After any runner crash, verify the tree by re-reading git state before continuing | friction 5 | orchestrator | propose |
| B-166 | The citation census anchors on content (symbol-at-line), not line-count existence | friction 3 (DDR F-1 arch/ux MAJOR + software-dev MINOR) | the batch that next touches `mapper/keymap.py` or the census | **recorded in BACKLOG** |

- **Prior controls exercised:** held — privacy A-110 (after the run-2 failure: held on the staged tree), C-2 reviewer-authored mutants (7 review mutants + 6 DDR mutants, all killed; the "N/N killed" cell is never final without them), the ≤4-SOURCE cap (split, not breached), RED-before-GREEN with hash-verified restores, the change-first census, lane file-ownership disjointness (zero conflicts), the trunk-before-fork order (L-3: the D1 amendment landed once, at trunk). Stress-tested — the signed test-ledger arithmetic (re-derived at the DDR gate: 4231 collected post side) and the guard-set enumeration (failed once, extended, now replaced by L-1). Near-miss — the whole-corpus layer escaped again before L-1 existed.

### Open / deferred items → next batch
| Item | Type (process/product) | Reason deferred | Trigger / owner |
|------|------------------------|-----------------|----------------|
| **R3 — FTS evidence search** (behind `security-check-before-tools`) | product | its own batch in the R series, in order | next batch; owner: orchestrator with the operator |
| **R4 — timeline (C5)** | product | its own batch; the DDR carries the C5 design reading | after R3 |
| **R5 — metro / `lineage` profile** | product | its own batch; B-154 holds the derive-per-descriptor seam | after R4 |
| **The UI batch from the round-2026-10-23/24 verdicts** — canvas follow · outline diff gutter · roles skeleton · home hm-queue · connect-repo rg-panel · hero margin | product | verdict content lives in the git-ignored `prototypes/round-2026-10-23/verdict-2026-10-24.json` of the main checkout (not on this tree); scope to be taken from the verdict files at the next P0 | next P0; owner: orchestrator |
| B-141 US canon + AT→test table · B-142 canon hygiene | product | sources must exist before 7 of 8 gap kinds have end-to-end evidence | decide formats before the matrix gains test columns |
| B-144…B-147, B-151, B-152, B-154, B-155 relmap carries | product | accepted watch-items; each names its touching batch | as each names |
| B-148/B-165 real Python 3.10 run | process | no interpreter, no CI | operator |
| B-149 contract wordings (R1) · B-150 UX observations · B-156 contract shape · B-157 worktree hygiene · B-158 reviewer-mutant cell | process/product | carried from R1; B-156 answered by practice this batch (`01b` companion + ledger rulings kept the contract in budget) | flow maintainer / orchestrator |
| B-159…B-163 R2 parked observations (home columns, mid-band split, code-point bound, M-RVM-4 numbering, refusal double-paint) | product | cosmetic/declared; no criterion broken | the batch that next touches each file |
| **B-166 content-anchor citation census** | process | this close's third hand repair is the argument for it | the batch that next touches `mapper/keymap.py` or `tests/test_repair_artifact_claims.py` |

**Backlog reconciliation (mandatory close step).** Done: B-159…B-165 were recorded during the batch; this unit appends **B-166** and records no item as shipped by this records-only unit. **Still owed at merge:** refresh the backlog header's `origin/master` tip SHA and the "last refresh" line, and mark the PR number and merge SHA once the operator merges (merge authority was NOT granted; no push by this unit). The default branch is `master`.

### Working-file reconciliation (C-44) — MANDATORY, every file this batch touched
> Sweep run 2026-10-26 in the worktree `feat/relmap-r2` only; the main checkout (`mapper-clean`) and auxiliary repositories were not swept in this unit (no change expected — this unit touched only this worktree). `git status --short` before this unit's edits was clean; `git log @{u}..HEAD`: no upstream configured for the branch (never pushed — no `origin` push by this unit).

| Repo | File(s) | Terminal state | Landing / backlog ref |
|------|---------|----------------|-----------------------|
| mapper (worktree, branch `feat/relmap-r2`) | product + tests through `2e83cf6`, records through `5520508`, this unit's records (see the §0 dirty list) | committed by this unit (see its commit id in the report), **not pushed, no PR** | operator merges; branch `feat/relmap-r2` |
| unit scratch (outside the repo) | two detached checkouts (`1b3b151`, `2e83cf6`) + the sanitize filter + raw captures, under `ds-units/p5scratch` | created for the COND-DDR-2 captures; **deleted** (verified: `git worktree list` names only the two standing worktrees; the scratch dir is gone) | COND-DDR-2 evidence `evidence/p5-cond-ddr2-*.txt` |

- **Found before the batch:** none — no tracked file was modified when the batch began (the batch opened in a worktree of a clean primary checkout; `state.json` `owner` note).

**Conditional gate verdicts:** the PDR and DDR closed `approved with conditions`. Discharge verified by re-reading:

| Conditional item | Discharged? | Verified how |
|---|---|---|
| PDR: 13 conditions, each discharged at its owning gate | ✅ | DDR §B row 8 + the conditions table re-read at the DDR gate by the owning reviewers (12 of 13 honest; COND-ARCH-3/UX-3 re-opened as COND-DDR-1) |
| DDR: COND-DDR-1 (citation re-repair + F-2/F-3 folds + staged-tree guard) | ✅ | the 6 repaired sites + `design-proposal.md:304` re-read against the symbols they cite (`palette_items` :475, `duplicate_chords()` :488, the whole-seat pin :189); the DDR record's F-2/F-3 rows and §H D6 carry the as-built counts; the A-110 staged-tree guard re-run after the edit (green); `LED-2026-10-25-r2.32` |
| DDR: COND-DDR-2 (store the two pre-fix REDs) | ✅ | `evidence/p5-cond-ddr2-census-prefix-red-2026-10-26.txt` (exactly the 3 named nodes fail at `2e83cf6^`, 69 passed) and `evidence/p5-cond-ddr2-a110-prefix-red-2026-10-26.txt` (both A-110 arms fail at `cdc4491^`); `LED-2026-10-25-r2.33` |
| DDR: F-2 (qa) AT-148 supplementary arm ids · F-3 (qa) ledger base-side limit | ✅ (as dispositioned) | F-2 (qa) → BACKLOG (owner: software-dev, next shell-suite batch); F-3 (qa) → recorded here: the base side (4023) rests on the dev-flow worker's removed detached-`867dfd7`-worktree collect, re-verified post side only — a named limit |
| P4: Python 3.10 real run | ❌ not-run | B-165 (re-stamps B-148), operator |

### Evidence checklist — architect + qa-reviewer
- architect — (a) the frozen D1 surface as amended is what ships: ✓ the `test_d1_*` freeze nodes + the per-view wiring nodes (DDR §B row 2 re-read in code); (b) lane disjointness and the ≤4 cap: ✓ git-proven at the join and the DDR (as-built `4/1/4/1/1/1/2/0/1`); (c) residual risks owned: ✓ DDR §E + BACKLOG B-151…B-166; (d) Python 3.10 floor: ✗ proxy only, B-165.
- qa-reviewer — (a) 72/72 requirements and 23/23 ATs traced to executed nodes: ✓ `06-docs/traceability-matrix.md`, `04-validation.md`; (b) the signed ledger reconciles: ✓ `4023 − 4 + 212 = 4231`, post side re-derived at the DDR gate; (c) escaped regressions have stored pre-fix REDs: ✓ `evidence/p5-cond-ddr2-*.txt` (this close; previously the R1-noted limit); (d) mutation evidence independent of the author: ✓ 7 review mutants + 6 DDR mutants, all killed with sha256-verified restores; (e) real interpreter at the declared floor: ✗ `not-run`; (f) privacy: ✓ A-110 + fold green on the staged tree of this unit's commit.
