# PLAN — mapper — Batch 2026-10-25-relmap-r2-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> **Owed in.** `full` ✓ · living plan owed at every gate (`shared-batch.md` §Living plan).
> **Field guide:** `templates/guides/plan-template.md` (ships with the flow, not copied).
> The header labels `Standing authorization` and `Last updated` are read literally and
> are never translated.

The living compendium of this batch: where-we-are · objective · per-story/per-station
status · roadmap + increment plan · key decisions · risks/watch-items · conventions
honored · out-of-scope carries · test ledger · decision log (human-readable mirror of
`state.json`).

## Header

| Field | Value |
|---|---|
| Project | mapper |
| Batch | 2026-10-25-relmap-r2-batch |
| Objective | Relation-map port R2 — the VIEWS. Per the operator verdict of round 2026-10-23 (`verdict-2026-10-24.json`): **matrix-panel** side-panel impact lens with **binds-glyphs** cells; **gaps-ranked** in Darkside casing (not Solari ALL CAPS); **sheet-direct** node sheet (`c` = full chain). A read-only relation screen in the Darkside TUI hosts the three views through the one `Canvas` adapter with the C10 audit hook; scalecheck at the 118 reference width (87 checked); colour always on; English UI. Shell: Home lists relation maps (`.relmap.yml` + derived reqharness map) with a kind badge, opens them by descriptor `kind`, keys via the keymap single seat, help/palette entries (MAP-TYPES §6.2). Consumes ONLY the R1 frozen API (`PDR-2026-10-25-relmap-r1-batch#D3`); inherits DDR §E items 10-14 (presentation leaf `relmap/text.py`, single `refusal_line` import path, default-only derivation noted for R5, B-147 per-line hook bound). OUT: timeline (R4), metro (R5), FTS (R3), edge editing. |
| Last updated | P6 · 2026-10-26 (the P5/P6 close records unit, station P4 → P6 — records only, no product or test code: **COND-DDR-1 discharged** — the drifted census citations re-repaired by content match (`01-requirements.md:255/:785/:813`, `design-proposal.md:254/:255`, plus the same-drift unnamed site `:304`), each new line re-read against the symbol it cites (`palette_items` :475, `duplicate_chords()` :488, the whole-seat pin :189); the DDR record's F-2/F-3 rows and §H D6 now carry the as-built lane counts `4/1/4/1/1/1/2/0/1` — a declared amendment per the §G dispositions, never a silent edit; the A-110 staged-tree guard re-run green; **COND-DDR-2 discharged** — both escaped-regression pre-fix REDs captured on detached scratch checkouts (created and removed outside the repo) and stored sanitized: `evidence/p5-cond-ddr2-census-prefix-red-2026-10-26.txt` (exactly the 3 named census nodes fail at `2e83cf6^`, 69 passed) + `evidence/p5-cond-ddr2-a110-prefix-red-2026-10-26.txt` (both A-110 arms fail at `cdc4491^`); B-166 records the content-anchor citation census; ledger `LED-2026-10-25-r2.32/.33`; `05-postmortem.md` completed — lessons as controls with owners (L-1 guard-set derivation, L-2 staged-tree privacy test, L-3 trunk-review-before-fork, L-4 lane disjointness, L-5 crash recovery by re-read, L-6 reviewer mutants), metrics from the records, open items R3/R4/R5 + the UI batch + B-141…B-166; Phase 6 documents written (`06-docs/executive-summary.md`, `06-docs/functionality.md`) and the traceability matrix signed off; the batch's requirement ids folded into the `REQUIREMENTS.md` canon; `state.json` records the P4 approval + the P5/P6 decisions, `phase_status: awaiting-sync`; the A-110 + fold guard ran on the STAGED tree before the commit; gate `0 block`; the batch awaits the operator's merge and `/dev-flow-sync` — no push); previously: DDR · 2026-10-26 (the DDR gate unit — the JOIN-point review of the A4 fork, station DDR → P4: four independent reviews over the joined tree (`evidence/ddr-architect.md` · `ddr-software-dev.md` · `ddr-qa.md` · `ddr-ux.md`), verdicts architect `approved with conditions` · software-dev `approved` · qa-reviewer `approved with conditions` · ux-reviewer `approved with conditions`; the DDR record sealed `approved with conditions` 2026-10-26 — C-18 ruled satisfied under the R1 reading, the §F D-1 two-hatch deviation ratified (qa + ux independently), the P4 gate transcript sha256 `7feaa2f1…0ca330` re-verified by the qa-reviewer, the ledger post side re-derived (`4231 collected`), 6 reviewer mutants under control C-2 all KILLED with sha256-verified restores; two MAJOR conditions open at the seal — **COND-DDR-1** (the COND-ARCH-3/COND-UX-3 citation repair drifted again before the fork — records-only re-repair due at the P5 close records pass; proposed B-166) and **COND-DDR-2** (the two escaped-regression pre-fix REDs asserted but never stored — capture them or record the accepted gap with the operator's ruling, due P5); five MINOR notices dispositioned to the records pass / BACKLOG (§H D6 as-built counts `4/1/4/1/1/1/2/0/1`, the `fb336ed` row-6 parenthetical, the `darkside.py:576` citation, the AT-148 supplementary arm ids, the ledger base-side limit); the ux-reviewer's own walkthrough of the real screens at 118/87 reproduced the worker's transcript; gate `0 block · 919 notice · 55 n/a`; the P4 validation record stands, P5 close is next); previously: P3+ · 2026-10-25 (the P3 census-amendment unit — the orchestrator's clean full-suite run (`4223 passed, 3 failed`) surfaced three whole-corpus census failures no increment's guard set named, all test-side, no product code touched: ① `test_darkside_census.py::test_hue_census_every_severity_and_busy_site_is_classified` — the 12 new severity/busy sites in `mapper/screens/relmap/{matrix,sheet}.py` classified individually (the `!` verifies-missing glyph ALERT ×3, the `◐` binds-missing glyph WARN ×3, the open-node `○` badge and the `relates to nothing` hatch ALERT ×2, the two `not computed` words and the reach-gauge fill WARN ×3, the sheet gap head ALERT; pin 82 → 94) and registered with per-site judgements; ② `test_inc9.py::test_a112_the_chrome_is_english[seat]` — the relmap seat's words added to `CHROME_LEXICON` (by, chain, gaps, impact, kind, lens, matrix, on, refresh, sheet + the six `r`-prefixed group handles rview/rnav/rlens/rchain/rkind/rleave); ③ `test_inc9.py::test_cd25a_the_seat_diff_is_exactly_what_inc9_declares` — the 13 `relmap` seat rows declared in `DECLARED_ADDED`; records integrated: ledger `LED-2026-10-25-r2.31` (C11), PLAN guard-set definition extended with `tests/test_darkside_census.py` + `tests/test_inc9.py`, post-mortem note seeded in `05-postmortem.md` for P5; lesson — every increment's guard set must name the whole-corpus censuses, not only the fold/repair pair; evidence `evidence/p3-census-amendment-green.txt`); previously: P3+ · 2026-10-25 (the Inc-3/4/5/6 independent-review follow-up unit + the Inc-6b/Inc-7 records integration: the four review records `evidence/review-inc003…006.md` committed with the discharges — Inc-5 F1 (degenerate-height default body arm; M-REV-1 killed; the packet's Load-bearing-emptiness claim corrected) and F2 (stacked INK→MUT id-style oracle; M-REV-2 killed), F3 recorded for the DDR (hatch count: the Statement's two wins), F4 noted (LF/TAB canon-excluded; renderer-arm covers them); Inc-6 F2 fixed (relation/derived row keys kind-prefixed `relmap:`; the DuplicateKey arm RED→GREEN; M-REV-HOME-1 killed; the inc9c LEAK_EXCEPTIONS pin re-pinned 240 → 246 per B-113) and F1 declared (the recents NAME column clips `REQUIREMENTS` → `REQUIR` — packet rendering note amended; BACKLOG B-159 parks the two-column width pass); Inc-3 F1 fixed (the `╌╌╌ root — nothing feeds it` line pinned word + MUT) and F2 fixed (the degenerate-height flap guard `max(1, …)`; RED at h=6 reproduced `01–00`); Inc-4 F1 fixed (the `_budget` floor tightened to the degenerate value; explicit heights 2–3 respected), F2 accepted → BACKLOG B-160, F3 accepted with reason; the four packets' §4b cells filled (verdicts + follow-ups tables; approvals NOT logged anywhere else); records integrated: ledger `LED-2026-10-25-r2.30` (C11 naming — the Inc-7 gate amendment, Before/After over the two R1 snapshot gap lines cut by the 240 bound; the contract's LLR-RVU.1.1 asserting-tests line and Ledger back-pointer updated, P10/P11 superseded in its measurement scope), PLAN test-ledger rows for Inc-6b (+2), Inc-7 (+7 new file; audit 49 → 49; guard 31 files 1218 passed) and this unit; measurements: guard set 1206 passed, 2 skipped, 3 xfailed (wall 248s), the commission's `test_home*.py` glob names no file in this tree — dropped, not substituted; gate run below); previously: P3 · 2026-10-25 (Inc-7 landed: `4853b16` — the hook per-line bound 240 in the F-SEC-3 order — `HOOK_LINE_CELLS` + `_cut_hook_line` (239+ellipsis, spelling-aware back-off) in `mapper/reqharness/audit.py`, 7 nodes new in `tests/test_hook_line_bound.py`, the R1 arms `test_at_125…`/`test_snapshot_run` re-derived onto the D5 seam (49 → 49), M-RVU-1/2/3 all KILLED, AT-152/TC-RM-30 minted; packet `03-increments/increment-007.md`; evidence `p3-inc7-*`; the Inc-7 4b review pending — the orchestrator schedules it with 6b's); previously: P3 · 2026-10-25 (the lanes forked and JOINED: L3 matrix `c38f929` + L4 gaps `e2f0d90` + L5 sheet `2d332b2` + L6 shell `996b0ca` merged into `feat/relmap-r2` (`3b9eada` → `ee39668` → `4a9ecf8` → `7a56db7`), zero source conflicts — the disjoint lane file sets held; per lane — matrix 1 SOURCE, 32 nodes (6 L0 + 16 A + 10 B), M-RVM-1…11 (ten defined + M-RVM-1 dual-form) all KILLED; gaps 1 SOURCE, 33 nodes (27 view + 6 sweep), M-RVG-1…13 all KILLED incl. the COND-UX-2 per-band membership arm; sheet 1 SOURCE, 29 nodes, M-RVS-1…12 all KILLED, COND-SEC-2 c-chain BFS at the 100k cap measured 0.164 s (recorded, never asserted); shell 2 SOURCE (home + app), 14 shell arms, M-RVH-1…7 all KILLED, `test_inc9c.py` pin re-pinned 176 → 240 in-increment; measurements: AT-137 303-node baseline median 0.005 s → recorded 10× budget 0.048 s, 100k cap-scale paint 0.66 s @118 / 0.70 s @87 (COND-QA-3 — packet measurements, no clock asserts); records integrated: ledger `LED-2026-10-25-r2.19…29`, contract + `01b` amendments per r2.20/.21/.24/.29, ARCHITECTURE §3 home→`relmap.descriptor` discovery edge (r2.27); packets `increment-003…006`; evidence `p3-inc003…006-*`; every packet's Independent review `pending — orchestrator schedules`; the join guard set + gate run recorded in Gate notices below); previously: P3 · 2026-10-25 (trunk Inc-2 landed: the screen host + keymap seat — `mapper/screens/relmap/{__init__,screen,base}.py` + `mapper/keymap.py` (**4 SOURCE**, at the cap, the §2 ⚠ declares the cut): the D1 host↔renderer surface is BUILT and frozen as sealed — `base.ViewState(relmap, notice, focus, cursor, lens, gaps, width, height)`, `RelMapView.paint(state)`, `RelMapView.toggle(kind) -> str` (COND-ARCH-1), `build_view(name)` with the `PendingView` placeholder; `SCOPE_RELMAP` seats 13 bindings (`1`/`2`/`3`, cursors, `enter`/`c`/`k`, `r`, `q`/`escape`), no chord twice, the whole-seat pin re-runs per COND-QA-2; derive-on-open + `r` (count 1→2, the counter WRAPS derive_reqharness_map per COND-QA-4); out-of-view inert per COND-UX-1; the `_row_text`/`fit` sink per COND-SEC-1; `tests/test_relmap_shell.py` new (15 arms), `test_keymap.py`/`test_key_dispatch.py` pins extended, 7 census repairs (test-side); guard set green `1066 passed, 2 skipped, 3 xfailed`; M-RVH-8/9/10/11/13/14/15/16/17/18/19 all KILLED (11/11); packet `03-increments/increment-002.md`; evidence `p3-inc2-*`; reviews of Inc-1a/1b/2 pending — orchestrator schedules; F-1…F-5 re-read at each lane's entry — the lanes may fork); previously: P3 · 2026-10-25 (trunk Inc-1b landed: `adapter.py` re-point (1 SOURCE) — the `relmap.model.cut` reader census is zero and the text-leaf move is complete (one definition site, one import path); full-surface byte-identity proven (probe hash `b7ff2e38…5a07` equals the base); full guard set green `762 passed, 2 skipped, 3 xfailed`; M-RVT-2/3 KILLED; packet `03-increments/increment-001b.md`; evidence `p3-inc1b-*`; COND-ARCH-2/COND-QA-1 discharged by Inc-1a+1b; reviews of both increments pending — orchestrator schedules; trunk Inc-2 next); previously: P3 · 2026-10-25 (trunk Inc-1a landed: `mapper/relmap/text.py` + the `model`/`descriptor`/`audit` re-points and the `audit.__all__` re-export drop — 4 SOURCE; `tests/test_relmap_text.py` new (13 nodes); RED code-absent + move-aside, M-RVT-1/2/3 all KILLED, live probe surfaces byte-identical; packet `03-increments/increment-001a.md`; evidence `p3-inc1a-*`; mid-move declared — `adapter.py:29` re-points at Inc-1b; review pending — orchestrator schedules); previously: P3 · 2026-10-25 (PDR sealed `approved with conditions`; the author-artifact conditions due
at seal are applied in this records-only unit: COND-ARCH-1 toggle-state channel named in the
proposal §4 D1 row + `docs/ARCHITECTURE.md` §4 surface row (the frozen renderer entry
`toggle(kind) -> str`); COND-ARCH-2/COND-QA-1 + the orchestrator ruling — Inc-1 splits into
Inc-1a (`text.py` + the `model`/`descriptor`/`audit` re-points, 4 SOURCE) and Inc-1b (the
`adapter.py` re-point, 1 SOURCE), both trunk before Inc-2, each step byte-identical — PLAN,
proposal §2.1/§4/§5.1/§8 and the §6 lane worksheet updated; COND-SEC-1 — the frozen seam reworded
to `darkside._row_text`/`fit` + LF/TAB added to the P12 vocabulary + the AT-134/AT-148 LF/TAB
arms; COND-ARCH-3/COND-UX-3 — the three census citations repaired; COND-QA-2 — `test_keymap.py`
relabelled existing + `test_key_dispatch.py` added to Inc-2's run; COND-UX-1 — `enter`/`c`/`k`
declared inert off their home view (LLR-RVH.4.1 clause + AT-148 arm); ledger
`LED-2026-10-25-r2.14…17`; the per-increment conditions QA-3/4/5, SEC-2, UX-2 stay open at
their owner increments; station P3 unchanged — Phase 3 next); previously: P1 · 2026-10-25 (contract + acceptance design drafted by the 4-agent module swarm and merged by the
orchestrator (P1 amendment 2026-10-25 corrected the census by script to 20 HLR / 52 LLR —
LLR-RVH.3.3 added; the original draft stated 26/52, see the ledger measurement; the
by-kind toggle, the 240 hook bound, the Inc-2 keymap seat and both seam probes folded back
per the P2 first-pass findings; AT-130…152 / TC-RM-04…30 unchanged at 23/27; security scan
answered in §6.3; increment plan below; P1 gate run — see state.json decisions_log); previously: ARQ · 2026-10-25 (`docs/ARCHITECTURE.md` amended as commitments; `test_repair_map_truth.py` 52 passed); previously: P0 · 2026-10-25 (rollover; six stories READY; triggers fired A1 A2 A3 A4 B1 C6 C8 D1 E1) |
| Standing authorization | standing authorization — the operator's approval of the relation-map series, cited per the commission: «Arranca las tres, delega todo lo que puedas a kimi» (2026-10-23), «continue» / «adelante» and «haz el push por favor y continúa llamando a kimi 2.8» (2026-10-25). Runtime cannot prompt: autonomy over the gates the commission opens is read from silence (`shared-batch.md` §Batch-kickoff authorization); MERGE NOT granted — the default stands; NEVER push (the 2026-10-25 «haz el push» was discharged by the previous unit on its own branch; this unit commits locally only). |
| First gate | run before Phase 0 on 2026-10-25 against the closed R1 batch: `0 block · 752 notice · 58 n/a`, exit 0 — a green flow identity. `V7` reported the bundle identical to the manifest, both directions (`flow_hash` not recomputable from a subset). The NOTICEs are the closed batches' own records (V8/V9 on historical increments, V56/V57/V62 on the R1 line); declared in §Gate notices. |
| Premises / RC-1 | `git fetch origin` 2026-10-25: default branch is `master`; `origin/master` = `HEAD` = merge-base = `867dfd7f747b` (R1 squash `c74cbca` + vault sync `867dfd7`) — base current, no rebase. RC-2: `git ls-remote --exit-code --heads origin` answered (exit 0); newest refs pushed today (`feat/relmap-r1` line). Already-shipped check (RC-1 b): `git ls-files` finds no `mapper/screens/relmap/`, no `mapper/relmap/text.py`; `git grep -l "relmap" -- mapper/screens` → no hit; `view_matrix`/`view_gaps`/`view_sheet` port targets do not exist; home globs only `*.mmd` (`mapper/screens/home.py:209`) → none of the six outcomes shipped on `origin/master`. Outgoing batch (`2026-10-25-relmap-r1-batch`): closed P6, vault-synced 2026-10-25; 19 decisions archived to `.dev-flow/2026-10-25-relmap-r1-batch/decisions-log.json`; single-slot fields retired in this rollover; `base_ref` re-stamped to `867dfd7`. |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at this table: one row per
trigger evaluated, fired or not (re-evaluate families C and F at every gate over the
diff; family B at every increment cut).

| Id | Verdict | Probe output |
|---|---|---|
| A1 | fired | judged — creates the screens module `mapper/screens/relmap/` (screen host + three renderers); `docs/ARCHITECTURE.md` §2 has no row for it (committed at this batch's ARQ) |
| A2 | fired | judged — touches `screens/relmap` (new), `screens/home.py`, `app.py`, `keymap.py`, `screens/help.py`, `screens/palette.py`, and inside `relmap` the new `text.py` leaf — ≥2 modules by any count |
| A3 | fired | judged — (a) the DDR §E-10/11 extraction moves `cut`/`DISPLAY_MAX`/`refusal_line` between modules of `relmap`, changing the import surface other `relmap` modules consume; (b) Home→screen routing gains a relation branch, changing the interface `screens/home.py` and `app.py` consume (today Home opens only `MapScreen`) |
| A4 | fired | judged — the increment plan (§Roadmap, final at P1) forks: after the shared screen-host + base-renderer increment lands, the matrix/gaps/sheet renderer lanes have disjoint file sets over the frozen D3 API; the shell lane (`home.py`/`app.py`/`keymap.py`/`help.py`/`palette.py`) is disjoint from all renderers |
| B1 | fired | `git grep -l "glob(\"\*.mmd\")\|MapScreen\|keymap" -- tests` → existing home/keymap/help/palette/screen-routing tests assert surfaces this batch touches, owned by other batches → reverse census per increment |
| B2 | not fired | judged — no FILE moves on disk; the DDR §E-10 symbol move (`model.cut` → `text.cut`) is a symbol move, and the old import paths are swept by a reader census in the same increment that lands the leaf (B2's file-move probe does not apply) |
| B3 | not fired | `git grep -l "relmap\|structure_lines\|DISPLAY_MAX" -- tests/goldens` → no hit; no byte-identical golden captures the sources this batch touches |
| B4 | not fired | judged — the views write nothing to disk; the in-memory derived map is consumed by the screens of this same batch (C-12 output-then-consume chains apply inside the batch); the R1-declared external consumer is this batch itself |
| C1 | not fired | judged — no authentication surface |
| C2 | not fired | judged — no secrets handling |
| C3 | not fired | judged — no external integration |
| C4 | not fired | judged — no sensitive-data category beyond what the canon already holds |
| C5 | not fired | judged — no destructive operation; relation maps open read-only |
| C6 | fired | judged — operator-supplied bytes are parsed on the new open path (`.relmap.yml` descriptors via the D2-frozen reader; the canon via the D3 derivation); same input class as R1, already under the shipped limits; the scan output is in §Gate notices |
| C7 | not fired | judged — no network exposure |
| C8 | fired | judged — the screens place canon-derived strings (node ids, titles, gap sentences) into rendered labels; Textual interprets console markup by default and the repo's own precedent (`mapper/screens/draft_guard.py:57` — `markup=False` alone leaves ESC in) shows the trap this batch must not re-open → C-17 controls (markup-safety LLR + hostile-input AT) are mandatory at Phase 1 |
| D1 | fired | judged — the user-visible surface gains a whole screen and Home entries; `ux-reviewer` is owed at PDR |
| D2 | not fired | judged — the prototype was built in Textual 8.2.8, the same tech as the shipping target; C-16's flag still binds the ATs (real key presses on the real surface, not proxies) |
| E1 | fired | 6 stories (US-RMV-001…006) / ≥5 planned increments |
| E2 | not fired | judged — HANDOFF scores the PORT high risk; R2 is the UI slice over a P4-validated core with a binding prototype verdict — the risk is ordinary batch risk |
| E3 | not fired | judged — internal tool; no client or regulated context |
| F1 | not fired | from a bundle — probe is the gate's `V7` line: bundle identical to the manifest, both directions; `flow_hash` not recomputable from a subset |
| F2 | not fired | judged — BACKLOG header refreshed 2026-10-25 at R1's open; but its base-ref cell still read `194f885`, owed since R1's merge (operator merged R1: `c74cbca`). Discharged at THIS rollover: header re-stamped to `867dfd7` (R2 opening) — the refresh R1 owed, folded here |

## Where we are

P0, ARQ and P1 are closed (2026-10-25, under the standing authorization); the P2
cross-review first pass ran the same day (four lenses; verdict `iterate-to-refine`; 2 blocker
+ 7 major + 12 minor, all requirement/plan-class) and its return edge is folded as the
**P1 amendment of 2026-10-25** (this unit): census corrected by script to 20 HLRs /
52 LLRs (LLR-RVH.3.3 added for the workspace-canon rule), by-kind toggle SHIPS on `k`,
hook bound ruled at 240 with a no-mid-spelling cut, `mapper/keymap.py` moved into trunk
Inc-2, both `assumed — verify in Phase 2` seams discharged by executed probes
(`evidence/p2-seam-*.md`), ledger entries `LED-2026-10-25-r2.01…11`. The contract
(`01-requirements.md`) + acceptance design (`01b-acceptance-design.md`) as amended:
20 HLRs, 52 LLRs, 23 ATs, 27 TCs; the security scan is answered in §6.3; the module map
carries the lane worksheet. **Owed next:** Phase 3 — trunk Inc-1a + Inc-1b (the text-leaf move,
split per the orchestrator ruling answering COND-ARCH-2/COND-QA-1), then trunk Inc-2; the lanes
fork only after the PDR-sealed surface is consumed (F-2). The PDR-seal author amendments are
applied in the P3 records-only unit of 2026-10-25 (see `Last updated` and the ledger
`LED-2026-10-25-r2.14…17`).

## Objective

See the header. Success is observable through the TUI: Home lists a relation map with
its kind badge and opens it; the relation screen shows the matrix + lens (matrix-panel,
binds-glyphs), the ranked gaps (Darkside casing, count column) and the sheet-direct node
sheet with the `c` chain; scalecheck stays green at 118 and 87; `mapper --audit` hook
lines respect the new per-line bound; the presentation census finds one `cut` /
`DISPLAY_MAX` / `refusal_line` definition with a single import path.

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| P0 | approved under the standing authorization | six stories READY (below); triggers fired A1 A2 A3 A4 B1 C6 C8 D1 E1 — ARQ/PDR/DDR stand |
| US-RMV-001 matrix + lens | P0 READY | verdicts matrix-panel + binds-glyphs cited; family RVM |
| US-RMV-002 gaps view | P0 READY | verdict gaps-ranked; Darkside casing; family RVG |
| US-RMV-003 node sheet | P0 READY | verdict sheet-direct; `c` = full chain; family RVS |
| US-RMV-004 shell | P0 READY | home badge/list, routing, keymap, help, palette; family RVH |
| US-RMV-005 presentation leaf | P0 READY | DDR §E 10-11; B-153; family RVT |
| US-RMV-006 hook per-line bound | P0 READY | B-147; DDR §E 13; family RVU |
| ARQ · P1 | not started | ARQ owed before P1 derivation |

## Roadmap + increment plan

Triggers A4 fired: ONE trunk, then FOUR lanes, then the join (§6 of the module map; fork
preconditions in contract §2.8). Constraint set: ≤4 SOURCE files per increment; guard set
per increment includes `tests/test_fold.py` + `tests/test_repair_artifact_claims.py`
(R1 control C-1) + `tests/test_darkside_census.py` + `tests/test_inc9.py` (whole-corpus
censuses — added by the P3 census-amendment unit `LED-2026-10-25-r2.31`: the closing
full-suite run surfaced three failures in these two files that no increment's guard set
named; lesson recorded in `05-postmortem.md`); each independent review records a
reviewer-authored mutant (C-2);
scratch under one named folder (C-4); runner switch logged (C-5); contract shape per C-3
(AT bodies in `01b-acceptance-design.md`). Requirements: **20 HLRs · 52 LLRs ·
AT-130…AT-152 (23 ATs) · TC-RM-04…TC-RM-30** (census re-counted by script at the P1
amendment — 51 LLRs held before LLR-RVH.3.3 was added; the command and output are recorded
in the ledger measurement `LED-2026-10-25-r2-census`).

| Inc | Lane | Story | Source files | What | Owning requirements | Tests (provisional) |
|---|---|---|---|---|---|---|
| 1a · text leaf (first half) | trunk (first) | US-RMV-005 | `mapper/relmap/text.py` (new); `model.py`, `descriptor.py`, `audit.py` re-point (**4**) | `cut`/`DISPLAY_MAX`/`refusal_line` to the leaf; one site; the `audit.__all__` re-export drops HERE; byte-identity probe before/after; reader census over the re-pointed paths (`relmap.model.DISPLAY_MAX`, `relmap.descriptor.refusal_line`, `relmap.audit.refusal_line`) zero in this increment — the one remaining old-path reader `mapper/relmap/adapter.py:29` re-points in Inc-1b, declared | HLR-RVT.1 · LLR-RVT.1.1–1.3 | `test_relmap_text.py` (new), the re-pointed R1 files enumerated — `tests/test_relmap_model.py:17-26`, `tests/test_relmap_descriptor.py:38`, `tests/test_relmap_audit.py:33-35` — R1 suite re-counted |
| 1b · text leaf (second half) | trunk | US-RMV-005 | `mapper/relmap/adapter.py` re-point (**1**) | `adapter.py` imports `cut` from the leaf; reader census over `relmap.model.cut` zero in this increment; byte-identity probe before/after; R1 suite green | HLR-RVT.1 · LLR-RVT.1.1–1.3 | `test_relmap_text.py` re-run + the R1 suite re-counted, AT-150/151 |
| 2 · screen host | trunk | US-RMV-004 (host half) | `screens/relmap/__init__.py`, `screen.py`, `base.py`, `mapper/keymap.py` (**4**) | `RelMapScreen` host; seat-driven chrome; view switching; derive-on-open + `r`; markup-safe label assembly in `base.py` through `darkside._row_text`/`fit` (COND-SEC-1); PDR freezes the host↔renderer surface HERE (the toggle-state channel `toggle(kind) -> str` named per COND-ARCH-1); the additive `relmap` keymap scope lands HERE (moved from Inc-6 per ARC-02 — the single seat gates `BINDINGS` before the lanes fork); `enter`/`c`/`k` inert off their home view (COND-UX-1); the AT-driver fixture-workspace injection is verified HERE (probe PASS 2026-10-25, `evidence/p2-seam-at-driver.md`) | HLR-RVH.3.2/.4 · LLR-RVH.3.3, 4.1–4.3, RVM.4.2/RVG.3.1/RVS.5.1 (sink), RVH.5.2 | `test_relmap_shell.py` (host arms), `test_keymap.py` (EXISTING — R1 US-N03 universal, extended), `test_key_dispatch.py` (whole-seat pin, re-run — COND-QA-2), AT-148 (host arms) |
| 3 · matrix | L1 ∥ L2 ∥ L3 ∥ shell | US-RMV-001 | `screens/relmap/matrix.py` (**1**) | grid + windowing + lens + reach gauge + skeleton honesty | HLR-RVM.1–4 · LLR-RVM.* | `test_relmap_matrix.py`, AT-130…134, TC-RM-04…09 |
| 4 · gaps | L1 ∥ L2 ∥ L3 ∥ shell | US-RMV-002 | `screens/relmap/gaps.py` (**1**) | ranked screen, chips, count column, casing census, honest zeros + by-kind grouping on `k` (SHIPPED per ruling LLR-RVG.1.5) | HLR-RVG.1–3 · LLR-RVG.* | `test_relmap_gaps_view.py`, `test_relmap_scalecheck.py` (sweep), AT-135…139 |
| 5 · sheet | L1 ∥ L2 ∥ L3 ∥ shell | US-RMV-003 | `screens/relmap/sheet.py` (**1**) | header, FEEDS IT / A CHANGE REACHES, cuts, `c` chain, node gaps, read-only census | HLR-RVS.1–6 · LLR-RVS.* | `test_relmap_sheet.py`, AT-140…144, TC-RM-15…20 |
| 6 · shell | L1 ∥ L2 ∥ L3 ∥ shell | US-RMV-004 | `screens/home.py`, `app.py` (**2**) | home glob + badge + order; routing; the seat scope moved to trunk Inc-2 (ARC-02) | HLR-RVH.1–3/.5 · LLR-RVH.1.1–1.3, 2.1–2.3, 3.1, 5.1/.5.2 | `test_relmap_shell.py`, `test_inc9c.py` (LEAK_EXCEPTIONS line-pin re-pin), AT-145…147 |
| 6b · help/palette | with/after shell | US-RMV-004 | `screens/help.py`, `screens/palette.py` (**2**) | help + palette entries from the seat | LLR-RVH.4.4 | `test_relmap_shell.py` (help/palette arms), AT-149 |
| 7 · hook bound | any boundary | US-RMV-006 | `mapper/reqharness/audit.py` (**1**) | per-line bound after escaping; D4 unchanged | HLR-RVU.1 · LLR-RVU.1.1 | `test_hook_line_bound.py` (new), R1 audit suite green, AT-152 |

Order of merit: Inc-1a (unblocks the renderers' value cuts) → Inc-1b (completes the one-path
census) → Inc-2 (unblocks everything) →
lanes 3/4/5/6 in parallel (shell and matrix first — they carry the most ATs) → 6b → 7.
Join: all-lane AT run on the joined tree before the DDR (precondition F-5).

Lane fixture policy (declared at the P1 amendment, ARC-05): renderer lanes build their
synthetic `build_map` maps INLINE per test file (R1 style); shared fixture modules
(`tests/_relmap_fixtures.py`) are trunk-only — two lanes never append to one shared fixture
file, so the crossed reverse census cannot be silently violated.

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-25 | Rollover from R1: 19 decisions archived; single-slot fields retired; `base_ref` = `867dfd7`; BACKLOG base-ref cell re-stamped (F2-adjacent discharge) | shared-batch §Batch rollover; one commit |
| 2026-10-25 | C-3 adopted: contract keeps statements; AT bodies → `01b-acceptance-design.md`; amendments → ledger | R1's contract hit 111,049 chars vs the 54,000 budget (V26 NOTICE); keep R2's contract lean from the first draft (B-156 proposes exactly this) |
| 2026-10-25 | C-8 fired and the C-17 controls mandated at Phase 1 | canon-derived strings reach new labels; draft_guard precedent |
| 2026-10-25 | No `mapper.db` caching of derived nodes in R2 — recompute-on-open + explicit refresh (OQ6 recommendation) | smallest correct slice; store schema stays untouched; B-4 stays not-fired |
| 2026-10-25 | P2 first-pass return edge folded as the P1 amendment (this unit): census corrected by script (20 HLR / 52 LLR — LLR-RVH.3.3 added); by-kind toggle SHIPS on `k`; hook bound ruled 240 with the no-mid-spelling cut; `mapper/keymap.py` moved into trunk Inc-2 (4 files, Inc-6 = home+app); both `assumed` seams discharged by executed probes (`evidence/p2-seam-*.md`); fixture policy declared (inline per lane, shared modules trunk-only); WARN tone scope clause; ledger `LED-2026-10-25-r2.01…11` | iterate-to-refine gate — all 19 findings are requirement/plan-class; per-finding dispositions recorded in `02-review.md` |
| 2026-10-25 | PDR sealed `approved with conditions` (four independent reviews — architect · QA · security C6/C8 · UX D1); 13 conditions. Orchestrator ruling on COND-ARCH-2/COND-QA-1: Inc-1 would hold 5 source files, so it splits into Inc-1a (`text.py` + the `model`/`descriptor`/`audit` re-points, 4) and Inc-1b (the `adapter.py` re-point, 1) — both trunk, before Inc-2, each step byte-identical. The author-artifact conditions due at seal are applied at P3 (toggle-state channel named; seam reworded to `_row_text`/`fit` + LF/TAB in P12 and the AT-134/148 arms; citations repaired; `test_keymap.py` relabelled existing + `test_key_dispatch.py` in Inc-2's run; `enter`/`c`/`k` inert off-home declared); ledger `LED-2026-10-25-r2.14…17`; QA-3/4/5, SEC-2, UX-2 stay open at their owner increments | the four PDR reviews are in `evidence/pdr-*.md`; the seal record is `design/PDR-2026-10-25-relmap-r2-batch.md` |
| 2026-10-25 | P1 rulings on the swarm's open questions (contract §3/§4 carry the folded text): empty-matrix policy = sourced rows + zero columns + the verbatim declaration (OQ-M1) · sweep sizes = 118 + 87 only (OQ-M2) · reqharness glyph table = verifies `✓`, binds `●`/`◐`, refines `•`, covers `≡`, `▪`/`·`, frozen at PDR (OQ-M3) · edge-type/kind casing = Darkside lowercase census-pinned everywhere, PNG caps transcensions overridden by the operator note + the PNGs' own lowercase (OQ-M4, OQ-G3, OQ-SHEET-1) · MED severity token = INK per the QuickMap oracle (OQ-G2; the WARN reservation is SCOPED by the P1 amendment — see the row above: gauge, `not computed`, sheet `◐` only) · by-kind toggle = CONTINGENT LLR-RVG.1.5 + `k` key, the PDR rules it in or out (OQ-G1/OQ-G4 — SUPERSEDED by the P1 amendment: the standing ruling ships it, `LED-2026-10-25-r2.01`) · sheet empties = declared `╌╌ none on record` (OQ-SHEET-3) · symmetric downstream cut accepted (OQ-SHEET-2) · overflow = counted line, wording RVT-owned (OQ-SHEET-4) · both-direction hop-2 nodes render in both sections (OQ-SHEET-5) · chain depth unbounded min-hop (OQ-SHEET-6) · header = id · title + kind chip, no source segment (OQ-SHEET-7) · home listing = one name-sorted list, badge distinguishes (OQ-R2) · workspace-as-repo accepted (P1 amendment: RULED by probe — canon resolves at the workspace root, `LED-2026-10-25-r2.03`) · derived row = canon stem, only at zero descriptors · `escape` = quiet leave alias · cursor keys in a painted nav group. | the module agents' recommendations were consistent with the verdict + MAP-TYPES; ruling them now keeps the P2 cross-review for genuine blockers |

## Risks / watch-items

- The R1 map is the HLR/LLR skeleton only (7 gaps, flat reach 0) — the views must look
  right on the honest partial map and must not fake US/AT/TC content (A2).
- The 87-column sweep is where the lens panel and the matrix grid fight for width; the
  prototype proved the cuts, the ATs pin them (risk owned by the PDR renderer cuts).
- B-137/B-139 known flakes still stand: a red in `test_reqharness_cache_fastpath.py` or
  the AT-113/AT-114 arms is not automatically a regression (P-05).
- The pre-existing recents kind-column clip measured at Inc-6 (header-width columns render
  `legacy` → `leg`, badge → `rel`; affects tree and relation chips identically, verified on the
  base HEAD) — a candidate for the home-table width pass, parked per the Inc-6 packet.
- B-155: the pre-existing `repo:` absolute-path line in `--audit` stays out of scope.

## Conventions honored

English artifacts · BLUF · `shall` only inside HLR/LLR · dual traceability
(US → HLR → LLR → TC; US → AT) · Darkside only, colour always on, reference width 118
(87 checked) · PYTHONDONTWRITEBYTECODE=1 + PYTHONIOENCODING=utf-8 in every shell call ·
privacy guard A-110 (no operator paths/names/handles in tracked files; `username_subject`
/ `<home>` / `<owner>` placeholders) · tests run as
`PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 python -m pytest
-q -p no:cacheprovider <files>` after proving `mapper.__file__` resolves in the worktree,
never the full suite in-unit · commit locally only, never push.

## Out-of-scope carries

B-140 (series R3-R5) · B-141 (US canon / AT→test table — gates the US/AT/TC view data) ·
B-142 (canon hygiene) · B-143 (QuickMap repo prose) · B-144/B-145/B-146 (R1 watch items,
named before R3/R5 as each names) · B-148 (Python 3.10 run, operator) · B-149/B-150
(audit wording cosmetics) · B-151/B-152/B-155 (audit/descriptor hygiene; `repo:` line) ·
B-156/B-157/B-158 (flow controls — C-3 adopted here, C-4/C-5 adopted in the conventions) ·
**B-159 (recommended, this batch):** the V23 citation grammar `_V23_OK` predates the
project's `<date>-<slug>-batch` directory naming, so every citation of the R1 record's own
published id (`PDR-2026-10-25-relmap-r1-batch#D3`) NOTICEs — widen the grammar's batch
segment to admit the slug form (flow maintainer) · the uifix D1/D2 screens (hero-inset-2,
plug-A-centre-left) and D3/D4/D5 — the separate UI batch from the same verdict round.

## Gate notices and runtime absences

- **2026-10-26 P5/P6 close records gate run** (this unit — records only): `0 block ·
  967 notice · 54 n/a`, exit 0 — the run and its tree are recorded in `05-postmortem.md`
  §0 (the designated home). Declared additions, per the gate-notices exception (not
  code, no re-review): increment-007's §2 table gains **doc rows** for this unit's
  records files (`05-postmortem.md`, `06-docs/executive-summary.md`,
  `06-docs/functionality.md`, `06-docs/traceability-matrix.md`,
  `design/DDR-2026-10-25-relmap-r2-batch.md` — the declared COND-DDR-1 amendment,
  `01-requirements.md`, `01-requirements-ledger.md`, `design/design-proposal.md`,
  `PLAN.md`, `BACKLOG.md` (B-166), `state.json`, the two `evidence/p5-cond-ddr2-*.txt`
  captures — kind `generated`, traced to the census trio, and `REQUIREMENTS.md` — the
  canon fold) AND **V59 close-limb rows** for the nine files of increments 001a/001b/006b
  and the census amendment (`mapper/relmap/{text,model,descriptor,audit,adapter}.py`,
  `tests/{test_relmap_text,test_relmap_model,test_darkside_census,test_app_imports_used}.py`)
  — the packet reader enumerates digit-named packets only, so the close gate's diff limb
  (running for the first time at this station) charged those files until named here; the
  sealed PDR and the `LED-…-r2.17` entry keep their historical citation text unchanged
  (a record of the repair as written then). First run of this gate carried **16 block**
  (V26: the new ledger entries' pairings one-way + `.33` naming no requirement — repaired
  by the contract `**Ledger:**` back-pointers and the `.33` requirement names; V59: the
  row kinds outside the closed set, multi-file rows, an id-less `Traces to`, and the nine
  close-limb files above) — all repaired in this unit, the re-run is the transcript
  above. Runtime absences: no reviewer sub-agents ran in this unit (post-mortem co-author
  and docs-writer roles executed by the dev-flow worker, marked as such in each
  artifact); the two COND-DDR-2 reproductions ran on detached scratch checkouts under
  the unit's scratch dir (deleted), not in this worktree.

- **2026-10-25 P3+ review-follow-up gate run** (after the Inc-3/4/5/6 review
  discharges + the Inc-6b/Inc-7 records integration): `0 block · 888 notice ·
  54 n/a`, exit 0 — transcript `evidence/p3-followup-gate.txt` (the first
  run carried exactly 1 BLOCK, V26: the `LED-2026-10-25-r2.30` ledger entry
  paired `LLR-RMU.1.2`, which names no r2.30 back-pointer — the entry's
  Requirement field was narrowed to LLR-RVU.1.1 alone, the only amended
  requirement; the re-run is the transcript above). The follow-up guard run
  (`1206 passed, 2 skipped, 3 xfailed`, wall 248s, exit 0) is recorded in
  `evidence/p3-followup-green-guards.txt`; the commission's `tests/test_home*.py`
  guard glob names no file in this tree (home arms live in
  `tests/test_relmap_shell.py`, already in the set) — dropped, not substituted.
  The V36 NOTICE on increment-007's §4b cell names no reviewer: that review
  (6b/7) is the concurrent reviewer's record, not this unit's.

- **2026-10-25 P3 join guard run** (after the four lane merges L3→L4→L5→L6 and the join
  census repairs): `1200 passed, 2 skipped, 3 xfailed` (wall 325s), exit 0 — the joined
  tree is green across the commission's guard set plus every lane's test files.  The
  first crossed run surfaced 11 join-time failures (all census/test-side, zero source
  defects): `test_fold` `.toggle(` allowance ×22 lane sites + one literal U+202E in the
  sheet arms (re-spelled), the AT-P04 owned-path parse (my own ARCHITECTURE edit
  backticked bare names — repaired), `test_app_imports_used` re-export allowances ×2,
  the trunk D1 arm's placeholder assumption, and the gaps AT-137 arm's lane-tree
  viewport geometry (now derived from the painted frame per `LED-2026-10-25-r2.19`).
- **2026-10-25 P3 gate run** (after the lane merges + the join census repairs + the
  records-integration pass): `2 block · 883 notice · 53 n/a`, exit refused only by the
  single station-expected red class published in the spine — both blocks are `V2` naming
  `AT-149` (owned by Inc-6b, not yet built) and `AT-152` (owned by Inc-7, not yet built);
  blocks outside that published class: **0**.  The first post-join run carried 12
  records-class blocks (10 V59 packet traces + 2 V26 pairings); all repaired in the
  integration pass (packet §2 traces, ledger Requirement fields, 16 contract Ledger
  back-refs).  Declared NOTICE classes: V41/V56 (the packets' `…/evidence/` citation
  shape, the same accepted class the trunk Inc-2 packet carries), V45/V46, V53.

- **2026-10-25 P3 gate run** (after the PDR-seal author amendments, records-only unit):
  `18 block · 837 notice · 56 n/a` — every one of the 18 blocks is `V2` naming an
  `AT-130…AT-152` id with no node on disk, the single **station-expected red** published in
  the spine (`commands/dev-flow.md` §Two-layer validation model: `**Station-expected reds:**`
  `V2` at `P3`) — each AT mints its node when its Phase-3/4 increment lands, and this unit is
  records-only by commission. Blocks outside that published class: **0**. Walked past per
  `SKILL.md` §step 2's one exception; the run is otherwise green (exit refused only by the
  expected reds). V62 satisfied: this plan's `Last updated` names station P3.
- **2026-10-25 P1-amendment gate re-run** (after the P2 first-pass fold-back: FLOW colons,
  census corrected by script, rulings folded, LLR-RVH.3.3 added, ledger entries
  `LED-2026-10-25-r2.01…11`): `0 block · 814 notice · 57 n/a`, exit 0 — both pre-existing
  V10 blocks (`01-requirements.md:843,851` at review time) cleared by the `FLOW: <id>`
  normalization of all six IFC openers. **V26** pairing clean both directions (every amended
  requirement's `**Ledger:**` field and every ledger entry's `**Requirement:**` line agree);
  the contract is 102,415 characters — the accepted V26 budget NOTICE class (same as R1,
  B-156). The second P2 pass runs on this amended contract.
- **2026-10-25 P1 gate run** (after the contract + acceptance design were drafted): `0 block ·
  806 notice · 57 n/a`, exit 0. First run (before fixes) carried 52 BLOCKs — all V4 on the 52
  LLRs (the field label `Asserting test(s)` collides with the rule's `test(` trigger; reworded
  to `Asserting tests`) plus V26 on the six stories' missing `Ledger` field (added `none`) —
  both fixed and the gate re-run green. Declared R2 NOTICEs: **V23** — the citations
  `PDR-2026-10-25-relmap-r1-batch#D3/#D4/.md` and `DDR-2026-10-25-relmap-r1-batch` are the R1
  record's own published ids (its §D table binds them verbatim), which predate the validator's
  rev44 grammar (`<date>-batch-<alnum>` vs the project's `<date>-<slug>-batch` dirs) — the
  citation is correct per the record, the grammar is stale; recommended flow fix recorded as
  an open question below. **V26** — the live contract is 96,092 characters, past the 54,000
  budget (the C-3 shape kept it 15% under R1's 111,049; the draft-time verification cites are
  the weight); accepted as the same NOTICE class R1 accepted (B-156 carries the budget
  decision).
- **2026-10-25 pre-Phase-0 run** (against the closed R1 batch): `0 block · 752 notice ·
  58 n/a`, exit 0. Declared NOTICE families: V8/V9 (historical increment packets of
  closed batches), V56 (R1 packets cite evidence under the main-checkout line), V57 (the
  R1 close record predates this squash-merged tree by 35 commits on the main checkout's
  line — the benign "record predates this tree" case), V62 (R1's plan `Last updated`
  cell names its gates, not P6). Not a refusal; the batch proceeds.
- **Runtime absences (named once, per SKILL.md §What refuses an invocation here step
  5):** no slash commands, no named reviewer roles, no hooks, no prompt channel — the
  reviewer roles run as spawned generic subagents carrying `agents/<role>.md`, and the
  standing authorization closes the gates the runtime cannot ask about. `V15`/`V16`/`V17`
  SKIP (no canon tree beside the bundle); `V30` half-runs (interpreter floor only);
  `V25` quiet (origin answered).

## Test ledger

Filled per increment at P3. Guard set for every targeted run (C-1):
`tests/test_fold.py`, `tests/test_repair_artifact_claims.py`,
`tests/test_darkside_census.py`, `tests/test_inc9.py`; pre-commit gate:
`tests/test_no_operator_paths.py`, `tests/test_fold.py`.

| Increment | Run | Counts | Evidence |
|---|---|---|---|
| baseline (pre-1a) | guard set + R1 relmap suite | 744 passed, 2 skipped, 3 xfailed (wall 157s) | scratch `byteid-before.txt` |
| Inc-1a | targeted (text/model/descriptor) | 155 passed, 1 skipped (wall 19s) | `evidence/p3-inc1a-green-targeted.txt` |
| Inc-1a | guard set (audit/adapter deferred, mid-move declared) | 672 passed, 1 skipped, 3 xfailed (wall 128s) | `evidence/p3-inc1a-green-guards.txt` |
| Inc-1a | signed balance | model 53→53 · descriptor 90→90 · audit 49→49 · text +13 | packet §4 |
| Inc-1b | targeted (text/adapter/audit) | 103 passed, 1 skipped (wall 40s) | `evidence/p3-inc1b-green-targeted.txt` |
| Inc-1b | FULL guard set | 762 passed, 2 skipped, 3 xfailed (wall 157s) | `evidence/p3-inc1b-green-guards.txt` |
| Inc-1b | R1 audit-surface suite (deferred mid-move) | 14 passed (wall 12s) | `evidence/p3-inc1b-green-reqrelease.txt` |
| Inc-1b | signed balance | text 13→15 (+2 arms) · isolation 97→98 (file-set param) · repair-claims 177→179 (corpus param); adapter 40→40 · audit 49→49 | packet §4 |
| 3 · matrix (lane L3) | targeted | 32 passed (6 L0 + 16 A + 10 B, wall 7s) | `evidence/p3-inc003-green-targeted.txt` |
| 3 · matrix (lane L3) | guard set + signed balance | 206 passed, 3 xfailed (wall 43s); fold +1 allowance (enumerated) | `evidence/p3-inc003-green-guards.txt` |
| 4 · gaps (lane L4) | targeted (both lane files) | 33 passed (27 view + 6 sweep) | `evidence/p3-inc004-green-targeted.txt` |
| 4 · gaps (lane L4) | guard set | 206 passed, 3 xfailed | `evidence/p3-inc004-green-guards.txt` |
| 5 · sheet (lane L5) | targeted | 29 passed | `evidence/p3-inc005-green-targeted.txt` |
| 5 · sheet (lane L5) | guard set | 206 passed, 3 xfailed | `evidence/p3-inc005-green-guards.txt` |
| 6 · shell (lane L6) | targeted (shell arms + inc9c) | 102 passed (39 shell + 63 inc9c) | `evidence/p3-inc006-green-targeted.txt` |
| 6 · shell (lane L6) | guard + census set | 337 passed, 3 xfailed; isolation +home.py door (enumerated) · inc9c pin 176→240 | `evidence/p3-inc006-green-guards.txt` |
| 6b · help/palette (after shell) | targeted | 41 passed (39 shell + 2 AT-149) | `evidence/p3-inc006b-green-targeted.txt` |
| 6b · help/palette (after shell) | guard set | 1207 passed, 2 skipped, 3 xfailed + the one sanctioned re-run (4 failures inside the concurrent reviewers' mutation window, each green on the single re-run the commission allows) | `evidence/p3-inc006b-green-guards.txt` |
| 7 · hook bound (trunk) | targeted (new file) | 7 passed | `evidence/p3-inc7-green-targeted.txt` |
| 7 · hook bound (trunk) | R1 audit suite (D4 pins) | 48 passed, 1 skipped | `evidence/p3-inc7-green-audit.txt` |
| 7 · hook bound (trunk) | guard set (31 files) | 1218 passed, 2 skipped, 3 xfailed | `evidence/p3-inc7-green-guards.txt` |
| Inc-3/4/5/6 review follow-up | targeted per lane | sheet 30 passed · matrix+fold 52 passed, 3 xfailed · gaps view+sweep 34 passed · shell trio 203 passed | `evidence/p3-inc003-followup-green.txt` · `p3-inc004-followup-green.txt` · `p3-inc005-followup-green.txt` · `p3-inc006-followup-green.txt` |
| Inc-3/4/5/6 review follow-up | guard set | 1206 passed, 2 skipped, 3 xfailed (the `test_home*.py` glob names no file in this tree — dropped, not substituted) | `evidence/p3-followup-green-guards.txt` |

## Decision log

Mirror of `state.json` `decisions_log` (empty at open; entries appended per gate).
