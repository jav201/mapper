# PLAN — mapper — Batch 2026-10-10-perf-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓
> Seeded by `/dev-flow-init` step 4 at both levels; the living plan is owed at every gate
> that follows (`/dev-flow` §Living plan is the rule's home).

> **Field guide:** `templates/guides/plan-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

The living compendium of this batch: where-we-are · objective · per-story/per-station status ·
roadmap + increment plan · key decisions · risks/watch-items · conventions honored ·
out-of-scope carries · test ledger · decision log (the human-readable mirror of `state.json`).
**Create at batch open and update at every gate and significant checkpoint** — the
orchestrator presents the full plan in-conversation at each phase gate.

## Header

| Field | Value |
|---|---|
| Project | mapper |
| Batch | 2026-10-10-perf-batch |
| Objective | Performance and scale (B-33): measure first, then bound and reduce the work a large map costs — open, keypress repaint, search, save/load |
| Standing authorization | full + autonomous + merge — operator: "Si, remedia rendimiento y escala." (2026-10-09), "sigue, usa kimi-for-coding como está" (2026-10-10); see `state.json` `standing_authorization` |
| First gate | <the first gate run's exit code and what its `V7` line reported> |
| Premises / RC-1 | <the verified `origin/main` tip, or: no origin — RC-1 not possible, local tip <sha>; each premise the batch rests on> |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at: one row per trigger evaluated, fired or not.

| Id | Verdict | Probe output |
|---|---|---|
| A1 | **fired** | a shared render walk / layout cache may become its own module under `mapper/views/` (decided at ARQ) |
| A2 | **fired** | renderers (`mapper/views/layered.py`, `outline.py`, `radial.py`, `mapper/canvas.py`), `mapper/model.py`, `mapper/mermaid.py`, the mount path (`mapper/screens/map/painting.py`, `screen.py`) |
| A3 | **fired** | a `Graph` adjacency index changes an interface every renderer and the store consume |
| A4 | **fired** | three disjoint lanes are planned — renderer cost, model/serialisation cost, mount paint count — the first batch to use the modular split for parallel work |
| B1 | **fired** | renderer and `Graph` symbols are asserted by many other batches' tests (`grep -rlE "LayeredRenderer|OutlineRenderer|RadialRenderer|children_of" tests/`) |
| B2 | not fired | no file moves planned |
| B3 | **fired** | the AT-065 parity goldens (`evidence/mod_parity_118.txt`, `mod_parity_87.txt` of the modular batch, pinned in `tests/test_mod_parity.py`) and `tests/test_repair_golden_census.py` capture painted output — every remedy must keep them byte-identical; that is the batch's behaviour oracle |
| B4 | not fired | no new artifact consumed elsewhere (the `.mmd` text must stay byte-identical — asserted, not a new consumer) |
| C1–C8 | not fired | no auth, secrets, integration, sensitive data, destructive DB, input surface, network or new markup over file text |
| D1 | not fired for this scope | behaviour-preserving remedies paint identical output; the S-18 work budget (changes what is painted) is OUT of this batch's first scope and goes to a prototype round first |
| D2 | not fired | — |
| E1 | **fired** | ≥ 3 planned increments |
| E2 / E3 | not fired | — |
| F1 | **fired** | flow bundle differs from its manifest (`V7`, external) |
| F2 | not fired | backlog refreshed this session |

## Where we are

**P0, RESUMED 2026-10-10** after `2026-10-10-csv-safety-batch` merged (PR #18 `6364a02`, state PR #19 `e7d433d`); master merged into this branch, `base_ref` re-stamped to `e7d433d`, the csv-safety log archived. Earlier: **P0, PAUSED 2026-10-10.** The measurement is done (`spike/perf-baseline.md` §1–§7; `evidence/perf0*-*.transcript`). The P0 spike also found a data-safety defect outside this batch's scope (B-114: a CSV import saves a map that cannot be re-opened). The operator ruled 2026-10-10 to fix it first in a short separate batch, opened in its own worktree per §Batch rollover; this batch resumes at P0's gate after that batch merges (rebase onto master, archive its log).

**P1, 2026-10-10.** The contract (`01-requirements.md`) and this PDR were authored (unit PERFARQ, ledger `LED-2026-10-10-perf-batch.1`).

**P1 iteration 1, 2026-10-10.** Round-1 review of the contract + PDR (transcription `PERF-review-r1.md`) returned **ITERATE-to-refine**; rulings R1–R9 applied to `01-requirements.md`, the ledger, `02-review.md` and this PDR (ledger `LED-2026-10-10-perf-batch.2`). Key moves: the layout memo caches the UNSCALED layout on strong references (premise 3 was FALSE); the adjacency cache is a strong-reference `is` check with a widened AST census guard (one mutation per in-place form) and a fresh-list `children_of`; the dump oracle is per-dump ≤ 2E + c plus a scaling ratio [1.8, 2.2] with dangling edges covered; AT-076 drives a real persisting edit gesture through `_save_or_toast` (bare `ctrl+s` with no draft saves nothing); every verification names exact `file::test` node ids (no `-k` substrings); new goldens are pinned at base SHA `e7d433d` with sha256 each, and the wire counter resets after mount; the wire cap tightens to ≤ 1,200,000 (≈ 1/20 of the 23,983,998 baseline); M-M3 becomes the file-diff check `git diff e7d433d -- mapper/views` empty; P4 wall-clock runs base/head interleaved on the same machine and session (median of 3, raw runs into `04-validation.md`). **Lane S was GATED on spike unit PERFS** — the gate resolved below.

**Spike gate, 2026-10-10 — Lane S WITHDRAWN (else branch, ledger `LED-2026-10-10-perf-batch.3`).** Spike unit PERFS did not establish feasibility: on the seed map at 118×34 and 87×34 the mount renders 2× before AND after the prototype (baseline: one pre-layout `refresh_canvas` render at canvas 0×0 + one settle render; prototype: two settle renders), the final canvas is byte-identical, wide-2000 was not measured (the unit timed out), and the prototype needed a second guarded render site in `_declare_after_layout` plus an A3 census pin change (65→66). Per the pre-written ruling, Lane S leaves the batch to backlog **B-118**; HLR-PERF.3 / LLR-PERF.3.1–3.2 / AT-077 / AT-077b are withdrawn with it. The batch forks **two** lanes — R and M (file sets still disjoint) — and the trunk owns the join.

**P1 iteration 2, 2026-10-10 — round-2 review approve-with-conditions; PDR sealed (ledger `LED-2026-10-10-perf-batch.4`).** Round 2 (architect probes p3/p4 + qa-reviewer; no HIGH) returned approve-with-conditions on both artifacts; rulings R10–R18 applied to the contract, ledger, proposal, this PLAN and the PDR: AT-076's gesture is the `a` add_child action through real keys on a saved map with the counting wrapper on `mapper.mermaid.dump` itself (golden pinned to the map AFTER the edit); the linear dump is a LOCAL incident pass (≤ 2E + c per call, ratio [1.8, 2.2]); the layout memo lives on the `LayeredRenderer` INSTANCE (passed into `_geometry` as an argument — no module-global state; spy = `_layout_misses`); the `resize`/`title` arms gain mutation M-R2c and the `undo` arm is a plain "new Graph misses" check plus M-R2d's forced-address-reuse node (with the determinism escape); Lane R gains its own `nodes`-writer census guard (M-R2e); §5.2 is scoped to the surviving LLRs/controls; the wire-cap rationale names the y-only failure (probe p4: x-only carries the whole gain — no clip 524,313 · x-only 6,547 · y-only 524,313 · x+y 6,547 per render at wide-2000, 118×34; exact count recorded at execution); M-M3 runs per lane at the DDR; the census alias form states its limits. The PDR was sealed `approved with conditions` — conditions: R10–R18 re-read at the DDR + the goldens-at-base capture owed BEFORE the lanes fork.

## Objective

Bound and reduce the work a large map costs. Measured (P0): opening a wide 2000-node map takes 4.8 s and 6000+ times out; every navigation key repaints the whole map (0.6–1.9 s at 2000–6000 nodes); mount paints three times; save is O(N·E) in the Mermaid dump; load is YAML-bound. The dense-DAG cost of B-33 (72.5 s) is not reachable by opening a saved map (the parser refuses multi-parent nodes).

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| P0 | done | measurement done (`spike/perf-baseline.md` §1–§7); resumed after the B-114 batch merged |
| P1 | in progress | contract + PDR authored (PERFARQ, ledger .1); round-1 review iterated — rulings R1–R9 applied (iteration 1, ledger .2); spike gate resolved the else branch — Lane S withdrawn to B-118 (ledger .3), lanes R and M fork; round-2 review approve-with-conditions — rulings R10–R18 applied and the PDR sealed (iteration 2, ledger .4); next: capture the goldens at the trunk (base SHA `e7d433d`), then fork lanes R and M in parallel worktrees |

## Roadmap + increment plan

Planned at P1 from `spike/perf-baseline.md` §4/§7; refined at P1 iteration 1 per round-1 rulings
R1–R9 (ledger `LED-2026-10-10-perf-batch.2`); Lane S withdrawn at the spike gate (ledger
`LED-2026-10-10-perf-batch.3` — the batch now forks TWO lanes, R and M); refined at P1 iteration 2
per round-2 rulings R10–R18 (ledger `LED-2026-10-10-perf-batch.4`). The trunk
owns requirements/PDR/PLAN + the join (DDR). All verifications name exact `file::test` node ids.

**Fork plan (2026-10-10, after the PDR seal):** (0) the TRUNK captures every new golden first —
AT-075 painted lines, AT-075b painted lines, AT-076 `.mmd` bytes (pinned to the map AFTER the
add_child edit) — on base SHA `e7d433d` (pre-remedy) with base SHA + sha256 per golden (the AT-065
precedent), BEFORE any lane fork; (1) lanes R and M fork into PARALLEL WORKTREES off the stamped
trunk (the A4 modular split — first parallel fork), each with the disjoint file set below; (2)
each lane lands its increments and executes its own negative-control transcripts inside the lane;
(3) the trunk joins at the DDR: full suite + AT-065 parity goldens + golden census byte-checks,
the surviving controls re-executed (M-R1a/b, M-R2/b/c/d/e, M-M1a/b/c, M-M2a/b), M-M3 recorded PER
LANE (it runs on the Lane M branch before the join — not a Lane R control), golden provenance
verified, P4 wall-clock evidence interleaved base/head on one machine and session.

- **Lane R** (2 source files): Inc-R1 — `mapper/canvas.py` span clipping + `tests/test_perf_paint_clip.py`
  (wire-count oracle with the tightened ≤ 1,200,000 cap, bare-`Canvas` equality vs in-test reference
  copies of the old loops, byte-identity grid with a panned ViewState and a fold). Inc-R2 —
  `mapper/views/layered.py` unscaled-layout memo (strong-reference key threaded through
  module-level `_geometry`; `card_w`/`gap` scaling re-applied per call) +
  `tests/test_perf_layout_memo.py` (memo-miss spy at the named hit-check point + seven named arms:
  resize, title, fold, focus, undo, add_child, round_trip).
- **Lane M** (2 source files): Inc-M1 — `mapper/model.py` strong-reference adjacency cache
  (`children_of` returns a fresh list) + `tests/test_perf_adjacency.py` (mutation script with the
  two-replacement no-lookup stretch, counted ops, widened AST census guard with one mutation per
  in-place form, LOW-10 minimap/outline bytes). Inc-M2 — `mapper/mermaid.py` linear incident pass
  (dangling edges covered) + `tests/test_perf_dump.py` (per-dump ≤ 2·E + c + scaling ratio
  [1.8, 2.2], fixture goldens incl. dangling-edge, AT-076 through a real persisting edit gesture
  via `_save_or_toast`).
- **Lane S — WITHDRAWN to backlog B-118 (2026-10-10, ledger `LED-2026-10-10-perf-batch.3`).** The
  gate resolved to the pre-written else branch: spike unit PERFS did not establish feasibility
  (mount renders 2× before AND after the prototype at 118×34/87×34 on the seed map, byte-identical
  final canvas, wide-2000 unmeasured after the unit timed out, prototype needing a second guarded
  render site in `_declare_after_layout` plus an A3 census pin change). Inc-S1 does not ship;
  HLR-PERF.3 / LLR-PERF.3.1–3.2 / AT-077 / AT-077b are withdrawn with the lane — lanes R and M
  proceed regardless.
- **Join (DDR):** full suite + AT-065 parity goldens + golden census byte-checks; every named
  negative control executed as a transcript; golden provenance verified (base SHA `e7d433d` +
  sha256 per golden, captured at the trunk before the fork); P4 wall-clock evidence (base and head
  on the same machine and session, interleaved, median of 3, raw runs pasted into
  `04-validation.md`).

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-10 | pause at P0 for B-114 | operator ruling: data safety before performance |
| 2026-10-10 | resume at P0, rebased on master `e7d433d` | the csv-safety batch merged; its `MapStore.save` round-trip check adds one `parse` per save (+3.2 % at 6 000 nodes) — the save-cost baseline in `spike/perf-baseline.md` §7 predates it |
| 2026-10-10 | round-1 rulings R1–R9 applied at P1 iteration 1 (ledger .2) | reviewer findings: premise 3 false, AT-076 vacuous, unsound cache keys, an equivalent M-R1b mutant, a contradicted Lane S mechanism, selector ambiguity, golden provenance, loose P4 protocol |
| 2026-10-10 | Lane S gated on spike PERFS; else B-118 | the round-1 mechanism was contradicted by the code (finding B4); the replacement (skip the canvas render only while `canvas.size.width == 0`) ships only with spike evidence, else the lane leaves the batch |
| 2026-10-10 | Lane S WITHDRAWN to B-118 (else branch; ledger .3) | spike PERFS inconclusive: mount renders 2× before AND after the prototype at 118×34/87×34 on the seed map, final canvas byte-identical, wide-2000 unmeasured (unit timed out), prototype needed a second guarded render site + an A3 census pin change; HLR-PERF.3 / LLR-PERF.3.1–3.2 / AT-077/077b withdrawn with it; lanes R and M proceed |
| 2026-10-10 | wire cap tightened to ≤ 1,200,000 (from 4,800,000) | a one-axis-only clip passed the loose cap (qa baseline note); the tightened cap is ≈ 1/20 of the measured 23,983,998 baseline for two keypresses |
| 2026-10-10 | cache validity = strong reference (`is` + `len`), never `id()` | `id()` can be recycled after free (findings B1/MED-4); soundness today is accidental (`_remove_subtree` calls `children_of` before reassigning) |
| 2026-10-10 | round-2 rulings R10–R18 applied at P1 iteration 2; PDR sealed `approved with conditions` (ledger .4) | reviewer findings (no HIGH): AT-076's gesture was still a non-persisting ficha edit; the ≤ 2E+c dump bound held only for a local incident pass; the memo location was self-contradictory; the resize/title arms named no mutation; the undo arm relied on non-deterministic allocator reuse; §5.2 still demanded the withdrawn Lane S scope; the wire-cap rationale was half false (a y-only clip fails — x-only carries the gain); M-M3 is per-lane; the census alias form stated no limits |
| 2026-10-10 | the layout memo is INSTANCE state on `LayeredRenderer` (spy `_layout_misses`), passed into `_geometry` as an argument — no module global | a module-global memo would leak across screens and pin `Graph`s (qa finding 3); each `MapScreen` holds one renderer (`screen.py:73`) and the import preview's fresh renderer per paint (`import_preview.py:103`) simply misses |

## Risks / watch-items

- Any remedy that changes what is painted (e.g. a work-budget degradation notice) needs a prototype verdict first · likely for S-18 · prototype round before implementing

## Conventions honored

- Worker model: Kimi `kimi-for-coding`; reviews by Claude; measurements by subprocess with timeouts, never in-process repeated apps (PERF0B harness hang)

## Out-of-scope carries

- Does not fix B-114 (separate batch) nor accept multi-parent maps end to end

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| `python -B .dev-flow/2026-10-10-perf-batch/spike/perf_harness.py` (see baseline for args) | 2026-10-10 | baseline tables in `spike/perf-baseline.md` |
