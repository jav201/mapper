# PLAN — mapper — Batch 2026-10-23-hygiene-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> **Owed in.** `core` ✓ · `full` ✓
> Seeded by `/dev-flow-init` step 4 at both levels; the living plan is owed at every gate
> that follows (`/dev-flow` §Living plan is the rule's home).

> **Field guide:** `templates/guides/plan-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.
> **Two header labels are read literally and are never translated:** `Standing authorization` and `Last updated`; the field guide names their readers.

The living compendium of this batch: where-we-are · objective · per-story/per-station status ·
roadmap + increment plan · key decisions · risks/watch-items · conventions honored ·
out-of-scope carries · test ledger · decision log (the human-readable mirror of `state.json`).
**Create at batch open and update at every gate and significant checkpoint** — the
orchestrator presents the full plan in-conversation at each phase gate.

## Header

| Field | Value |
|---|---|
| Project | mapper |
| Batch | 2026-10-23-hygiene-batch |
| Objective | Hygiene batch Q (QuickMap handoff C9/C10/C11 + §5 rulings 2/7): Q1 mapper renders in colour ALWAYS, even under NO_COLOR=1 (operator ruling Q5); Q2 ingestion limits on _nodos.yml loading (bytes, nesting depth, anchors/aliases refused, node/edge caps) + content-read limits (per-file byte cap, NUL probe) + Windows device-name ids; Q3 scalecheck sweep (every renderer exactly h lines of at most w cells at 80x24, 90x30, 118x34, 160x45, 200x50) + a Canvas.put audit hook recording overprint/clip events. C11 habits as process: move-aside RED counterfactual per deliverable file, close the axis not the instance, every LLR clause added by amendment names its asserting test and mutant. |
| Last updated | P6 2026-10-24 — P5 post-mortem written (`05-postmortem.md`: four incidents with evidence — concurrent-edit worktree breach, A-110 leaks ×3, the 171-failure worker-shell env artefact, the missed B1 fixture-content consumer; metrics 20 findings 0B/5M/15m, ledger 3546−0+33=3579; open items B-136…B-139 + C1/C2 + relation-map port + prototype-rounds traceability gap); P6 docs written (`06-docs/executive-summary.md` · `functionality.md` · `traceability-matrix.md` finalized); P5 + P6 decisions logged; gate `devflow-validate.py --brief` 0 BLOCK; state → P6 `awaiting-sync`; records only, never pushed |
| Standing authorization | standing authorization — operator commission 2026-10-23, quoted by the orchestrator: «Arranca las tres, delega todo lo que puedas a kimi» (after approving the series where batch Q = hygiene). Runtime cannot prompt: autonomy over the gates the commission opens is read from silence (shared-batch.md §Batch-kickoff authorization); MERGE NOT granted — the default stands. |
| First gate | run before Phase 0 on 2026-10-23: exit 1 — 15 BLOCK, all on the OUTGOING closed batch's record (V59 ×14 diff-limb charging PR #27's squash-merged files to the stale base_ref; V64 §3 citation `6121987` not carrying its row); `V7` reported the bundle identical to the manifest, both directions, at 2026-10-12-rev102. Repaired (V64 row re-cited to the merge commit `1609bbe`; rollover re-stamps `base_ref` to HEAD) and re-run green before derivation. |
| Premises / RC-1 | `git fetch origin` 2026-10-23: the repo's default branch is `master` (no `origin/main` exists — RC-1 read against `origin/master`, the same limb); `origin/master` = `1609bbe` = HEAD = merge-base — base current. RC-2: origin answered, newest commit 2026-10-16 (`1609bbe`, 7 days). Already-shipped check (RC-1 b): Q1/Q2/Q3 outcomes grepped on `origin/master` — none shipped (details in 01-requirements.md §2.6). Outgoing batch's light vault sync DONE: synced 2026-10-23 (light, README only) — the vault README was written 2026-10-23, after this batch's rollover check; the vault folder is the flag (orchestrator ruling R6; the outgoing batch's sealed state is not rewritten). |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at: one row per trigger evaluated, fired or not.

| Id | Verdict | Probe output |
|---|---|---|
| A1 | not fired | judged — the increment plan creates no module and moves no boundary (caps live as constants inside `store`); file sets in `01-requirements.md` §2.8 |
| A2 | fired | judged — one batch, three modules: `app` (Q1) · `store`/`diff`/`import_csv`/`osopen` (Q2) · `canvas` (Q3) |
| A3 | fired | judged — `Canvas.__init__` gains the `audit` parameter; consumers: 3 construction sites in `mapper/views/`; pins: `docs/ARCHITECTURE.md:197,211`, `tests/test_a3_census.py:658-674` (B-44) |
| A4 | fired | judged — §2.8 plans 4 parallel lanes (L1/L2a/L2b/L3) with disjoint FILE sets (L2 forked at the PDR seal, ruling R7) |
| B1 | fired | `grep -rl "Canvas" tests/` → `test_canvas.py`, `test_a3_census.py`, `test_repair_depth.py`, `test_perf_paint_clip.py`, `test_canvas_header_charge.py` assert symbols this batch touches, owned by other requirements → reverse census per increment |
| B2 | not fired | judged — no planned change moves a file's location |
| B3 | fired | `git grep -n "MASTER_LEGACY_DIGESTS\|goldens/perf/render" tests/` → `test_repair_depth.py:109` (12 SHA-256 of rendered plain+spans), `test_perf_paint_clip.py:172` (16 byte-identical render goldens) → byte-identity requirement LLR-Q3.2.2; golden drift census at each increment |
| B4 | not fired | judged — no new cross-component artifact (refusals reuse the existing `MapStoreError` surface; the audit sink is consumed by tests only) |
| C1 | not fired | judged — no authentication surface in the plan |
| C2 | not fired | judged — no secrets handling |
| C3 | not fired | judged — no external integration |
| C4 | not fired | judged — no sensitive-data category |
| C5 | not fired | judged — no destructive database operation |
| C6 | fired | judged — Q2's subject is the input surface: operator-supplied files parsed at load; the batch's own new code reads them (prescan) → §6.3 carries the posture; scan output below |
| C7 | not fired | judged — no network exposure |
| C8 | not fired | judged — no render mode flips to markup interpretation; file-derived text keeps rendering through explicit-style `Text` (Q1 restores colour without changing the Text pipeline) |
| D1 | fired | judged — Q1 changes what the user sees (restores colour); the scope ruling is honoured: no design change, no prototype owed (operator ruling Q5 + LLR-Q3.2.2 byte-identity) |
| D2 | not fired | judged — no prototype round in this batch |
| E1 | fired | 3 stories (US-Q1-001, US-Q2-001, US-Q3-001) / 3 planned increments |
| E2 | not fired | judged — risk declared low at intake (brief: effort S, risk low) |
| E3 | not fired | judged — internal tool; no client/regulated context |
| F1 | not fired | from a bundle — probe is the gate's `V7` line: bundle identical to the manifest, both directions, at 2026-10-12-rev102; `flow_hash` not recomputable from a subset |
| F2 | not fired | judged — BACKLOG content refreshed at the review-screen close (B-124…B-135 rows present); the header's `Last refresh 2026-10-09` cell is stale → watch-item, corrected at this batch's close reconciliation |

## Where we are

Phase 0 and ARQ closed, Phase 1 drafted and gated — all on 2026-10-23. P0: three stories READY,
trigger evaluation recorded above (fired: A2, A3, A4, B1, B3, C6, D1, E1). ARQ: `docs/ARCHITECTURE.md`
amended as commitments (no boundary moves; two `osopen` inbound edges; the additive `Canvas`
`audit` parameter; R-015; the §6 worksheet declares L1/L2/L3). P1: the contract
(`01-requirements.md`) holds 3 US / 6 HLR / 11 LLR / AT-108…116, a 12-row premise table (all TRUE,
executed evidence), §2.8 fork preconditions (condition 3 owed at PDR), the IFC (4 flows, 2
components) and §6.3 scan answers; the ledger is intentionally empty (no amendments yet). The P1
gate ran green (exit 0; 0 BLOCK). **P1 rulings applied (this unit, 2026-10-23):** orchestrator
rulings R1–R6 recorded — R1 node/edge caps 100,000/100,000 (wide6000 measured at 6,000 nodes fired
the UNLESS clause; ledger `.1`), R2 content-read surface confirmed (ledger `.2`), R3 Q1 mechanism
decided (ledger `.3`), R4 audit v1 = clip + overprint with dim-text deferred to BACKLOG B-136
(ledger `.4`), R5 condition-3 stays PDR-gated, R6 sync-owed notes replaced ("synced 2026-10-23
(light, README only)"). All five open questions in the refinement log are now closed. **This
worker stops here per the unit brief — P2 (cross-review) is the orchestrator's next station.** Owed
at P2/PDR: the condition-3 crossed reverse census, the reader/`Canvas` signature freeze.

**P2 second pass + PDR seal (reviewer unit, 2026-10-23):** four reviewer lenses ran as parallel
subagents over the amended contract and the design proposal (evidence `evidence/recheck-*.md`).
Second pass: F1–F3 and m1–m4 **verified**, m5/m6 confirmed open-correctly-carried; gate
`approve`. PDR sealed `approved with conditions` — condition 2 (F-UX-1, major: the CSV refusal
toast at `mapper/screens/home.py:524-530` paints only `type(e).__name__`, and `home.py` is in no
lane's file set) must be discharged by a trunk amendment BEFORE the lanes fork; condition 3 (S1,
diff-side `git show` uncapped capture) at the L2 gate; conditions 4–5 (record amendments) at
their named gates. New contract-record minors N1/N2 named in `02-review.md`. Next unit: the
trunk amendment discharging condition 2, then the D1 trunk landing and the lane fork.

**P2 dispositions + PDR transition (previous unit, 2026-10-23):** the P2 cross-review returned
`iterate-to-refine` (3 requirement-defect majors F1/F2/F3, 6 minors). Author dispositions: F1
re-measured including the tracked perf-evidence workspaces (largest committed map = 12,000 nodes /
11,999 edges) — caps stay 100,000/100,000 at 8.3× headroom under a ≥5× floor re-ruled by the
standing authorization (ledger `.5`); F2 adds `mapper/osopen.py` to L2's file set in the C-52
table, this plan and the ARQ worksheet (ledger `.6`); F3 records the Q3 sweep state matrix as an
explicit artifact at `design/state-matrix.md`, keyed on by AT-115 (ledger `.7`). Minors m1/m2/m3
fixed inline (m3 = ledger `.8`); m4/m5/m6 carried into the PDR design proposal / Phase-3 packets.
The PDR design proposal is drafted at `design/design-proposal.md` and the PDR record seeded at
`design/PDR-2026-10-23-hygiene-batch.md`; the crossed reverse census (ruling R5) is recorded
there. The amended contract owes its second P2 pass to the reviewers.

**P2 second pass + PDR seal (this unit, 2026-10-23):** the reviewers' second pass verified F1/F2/F3
and m1–m4 against the live tree and confirmed m5/m6 correctly carried (evidence
`evidence/recheck-{architect,qa,security,ux}.md`); the PDR review returned `approved with
conditions` — architect (N3), qa (approve), security (S1 LOW), ux (F-UX-1 major, F-UX-2 minor).
Orchestrator rulings: **R7** (F-UX-1) `mapper/screens/home.py` joins the Q2 lane — L2 forks into
L2a {store, diff, osopen} + L2b {import_csv, screens/home}, each ≤ 4 SOURCE files; AT-114 observed
through the running screen per m5 (ledger .9, mutant M-Q2-5) · **R8** (N3) the proposal's diff row
now bars a `diff → osopen` import — capped reads reach diff only via store's prescan, pinned by
`tests/test_arch_osopen_callers.py` · **R9** (S1) stays a named watch-item owned by the L2a
increment gate (cap `git show` output or accept with rationale — decided there) · minors
N1/N2/n1–n4/F-UX-2 fixed in the trunk records at the seal; n3 mints mutant M-Q3-4 (ledger .10).

## Objective

The batch objective from `state.json`: Q1 colour always on under `NO_COLOR` (operator ruling Q5);
Q2 ingestion limits on map-file loading + bounded content reads + device-name verification;
Q3 scalecheck sweep + `Canvas.put` audit hook; C11 process habits on this batch's own increments.

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| US-Q1-001 (Q1 colour) | READY — P0 approved | 1 source file (`mapper/app.py`); AT-108; mechanism DECIDED by ruling R3 (env removal in `MapperApp.__init__`; no `--no-color`) |
| US-Q2-001 (Q2 ingestion) | READY — P0 approved | 5 source files across L2a (`store.py`, `diff.py`, `osopen.py`) + L2b (`import_csv.py`, `screens/home.py`); AT-109…114; caps 100,000/100,000 per ruling R1 |
| US-Q3-001 (Q3 scalecheck+audit) | READY — P0 approved | 1 source file (`mapper/canvas.py`); A3 → ARQ/PDR freeze; AT-115/116; audit v1 = clip + overprint (ruling R4; dim-text → B-136) |
| P0 intake | closed 2026-10-23 | gate run green (exit 0) after V64 repair + rollover; ledger entry `P0` |
| ARQ | closed 2026-10-23 | `docs/ARCHITECTURE.md` amended as commitments; decision recorded |
| P1 requirements | drafted + rulings applied | contract + ledger entries .1–.4 + scan + gate; decision recorded; rulings R1–R6 recorded 2026-10-23 |
| P2 cross-review | closed 2026-10-23 — second pass `approve` | F1/F2/F3 + m1–m4 verified against the live tree; m5/m6 confirmed open-correctly-carried; new minors N1/N2 (contract record) owning station: trunk record-keeping; second pass 2026-10-23: verified/carried (evidence/recheck-*.md) |
| PDR | sealed 2026-10-23 — `approved with conditions` | D1/D2 frozen; S1 carried to the L2a gate; N3/F-UX-1 discharged by rulings R7/R8 at the seal; DDR re-reads all |
| P3 / P4 / P5 / P6 | P3 closed + P4 recorded 2026-10-24 — DDR drafted, P5/P6 not started | four lanes implemented, independently reviewed (4× OK-with-notes), merged + follow-ups at `a860a27`; P4 gate run by the orchestrator (3575 passed / 1 pre-existing flake / 24 deselected / 3 xfailed) — `04-validation.md` PASS-WITH-NOTES; DDR record drafted, verdict pending the three reviewers; P5 post-mortem + P6 docs/sync next, after the DDR seals |

## Roadmap + increment plan

In order: P2 cross-review of this contract → PDR (freeze `Canvas(w, h, tones=(), fallback="",
audit=None)`; discharge §2.8 condition-3 crossed census; cap constants confirmed) → P3 lanes
**L1 = Q1** (`mapper/app.py`), **L2a = Q2-core** (`mapper/store.py` + `mapper/diff.py` +
`mapper/osopen.py` — prescan, caps, bounded reader) and **L2b = Q2-csv** (`mapper/import_csv.py` +
`mapper/screens/home.py` — CSV import + refusal-toast wording, ruling R7), **L3 = Q3** (`mapper/canvas.py` + `tests/test_scalecheck.py` +
`tests/test_canvas_audit.py` + B-44 pin amendment) → DDR → P4 validation → P5 post-mortem → P6
docs + sync. Each increment packet carries: the move-aside RED counterfactual per deliverable
file, the C-40 mutation arms (M-Q1-1, M-Q2-1…4, M-Q3-1…3) with per-arm verdicts, and the B3
golden census. Max 4 SOURCE files per increment (L2a = 3, L2b = 2); tests uncapped.

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-23 | Rollover executed by hand (`devflow-init.py` refuses an existing `.dev-flow/`): outgoing `decisions_log` archived to `.dev-flow/2026-10-15-review-screen-batch/decisions-log.json`; single-slot fields retired per the table; full-level record seeded | shared-batch.md §Batch rollover |
| 2026-10-23 | Outgoing close record §3 row re-cited: the merge commit `1609bbe` (PR #27) added beside the branch-tip citation `6121987`, which changes none of the row's paths on this tree | gate V64 BLOCK repair |
| 2026-10-23 | Outgoing batch's light vault sync DONE: synced 2026-10-23 (light, README only) — the vault README landed after this batch's rollover check; SUPERSEDED case of /dev-flow-sync (the vault folder is the flag); the outgoing batch's sealed state is not rewritten | orchestrator ruling R6 correction |
| 2026-10-23 | Caps adopt QuickMap's constants verbatim (8 MiB / 64 / 4 MiB / 8 KiB); node/edge caps SUPERSEDED for mapper by ruling R1: 10,000/50,000 gave 1.67× node headroom — ruled too tight; the measured wide-6000 fixture (6,000 nodes / 5,999 edges) exceeds 1/10 of the proposed 50,000, so the UNLESS clause fired and the caps are 100,000/100,000 (16.7× over the then-measured population; re-derived 2026-10-23 as 8.3× over the true largest committed map of 12,000 nodes — headroom floor re-ruled ≥5×, caps unchanged; ledger `LED-2026-10-23-hygiene-batch.1` amended by `.5`) | orchestrator ruling R1 + executed measurement 2026-10-23 |
| 2026-10-23 | `NO_COLOR` neutralised in `MapperApp.__init__` (not `main()`) — mechanism DECIDED by ruling R3 (env removal before the Textual base constructor); no `--no-color` opt-out (operator ruling Q5) | constructor is the one path shared by CLI and tests; ledger `LED-2026-10-23-hygiene-batch.3` |
| 2026-10-23 | Audit events v1 = clip + overprint (overprint = both cells alphanumeric and different); dim-text deferred to BACKLOG B-136 | orchestrator ruling R4; ledger `LED-2026-10-23-hygiene-batch.4` |
| 2026-10-23 | Content-read surface = map files + CSV import; attachments OS-handed via `osopen`, no caps | orchestrator ruling R2; ledger `LED-2026-10-23-hygiene-batch.2` |
| 2026-10-23 | Condition-3 crossed reverse census STAYS owed at PDR before lanes fork | orchestrator ruling R5 — no change to the contract's PDR-gated record |
| 2026-10-23 | Q2 device-name defence: verify + pin (census), not rewrite | `check_map_id` + `osopen.safe_local_path` already cover it (premise 12) |
| 2026-10-23 | Q3 keeps rendered bytes identical (audit hook is observational); no golden re-baselining | B3 census; LLR-Q3.2.2 |
| 2026-10-23 | P2 review dispositions applied (author pass): F1 caps evidence re-derived from the true largest committed map (12,000 nodes, perf-evidence workspaces re-measured 2026-10-23; headroom 8.3×; floor re-ruled ≥5×; ledger .5) · F2 `osopen.py` added to L2's file set everywhere (ledger .6) · F3 state matrix recorded at `design/state-matrix.md` and bound in the contract (ledger .7) · m3 LLR-Q3.2.1 statement folded R4's second limb (ledger .8) · m1/m2 fixed inline · m4 carried into the PDR design proposal (capped cap+1 read) · m5/m6 carried to Phase 3 (screen-toast AT arm; device-name arms named in the Q2 packet test ledger) | author disposition pass under the standing authorization; gate `iterate-to-refine` answered by amendment |
| 2026-10-23 | PDR sealed — approved with conditions: second P2 pass verified F1/F2/F3 + m1–m4 (m5/m6 carried to Phase 3); conditions N3 + F-UX-1 discharged at the seal by rulings R7/R8 (ledger .9), S1 carried to the L2a increment gate (ruling R9); minors N1/N2/n1–n4/F-UX-2 fixed in trunk records; n3 mints M-Q3-4 (ledger .10) | reviewers' second pass 2026-10-23 (evidence/recheck-*.md); orchestrator rulings R7–R9 |
| 2026-10-23 | L2 forked into L2a {store, diff, osopen} + L2b {import_csv, screens/home}; AT-114's shipped surface = the home-screen CSV toast showing the typed refusal's str(e) (generic branch keeps type-name discipline) | ruling R7 answering PDR F-UX-1 (major); ledger LED-2026-10-23-hygiene-batch.9; mutant M-Q2-5 |
| 2026-10-23 | R10 — LLR-Q3.1.2's geometry oracle corrected to measured truth at the L3 RED gate: line bound 1..h (Layered renders h−4 lines on graphs smaller than the frame — measured) and width bound w per line, with the single exception of Layered's wordmark header whose node-count meter spills past w by construction — the sweep asserts that spill exactly ((w−2)+cell_len('{n} nodes'), byte-pinned by the perf goldens). The pre-amendment "exactly h lines / headers painted inside the canvas budget" text contradicted the live tree and was unexecutable without re-baselining goldens (forbidden by LLR-Q3.2.2). Ledger `.11`; state-matrix `plain` row erratum; the state SET is untouched (no PDR re-seal); the DDR re-reads this entry | L3 RED measurement over all 120 combos (`evidence/l3-sweep-measurement-probe-2026-10-23.txt`, sha256 5d0a7bae…0af47); orchestrator ruling R10 |

## Risks / watch-items

- Node/edge-cap headroom is 8.3× over the largest committed map (12,000 nodes / 11,999 edges in
  the tracked perf-evidence workspaces `perf0b-ws-*`; real maps ≤ 8 nodes) — caps stay 100,000/100,000
  per ruling R1 as re-derived by amendment LED-2026-10-23-hygiene-batch.5 (headroom floor re-ruled
  ≥10× → ≥5×); if a future fixture needs more, the cap moves by amendment · low · the sweep/load
  tests bound the blast radius (§6.3 of the contract).
- Prescan adds one pass over the sidecar — load-time delta on the largest perf sidecar
  (1,369,835 B / 12,000 nodes) measured at the L2a gate (record drift N1 fixed at the seal) · low · watch-item, not a gate.
- Diff-side `git show` capture is a full in-memory read before any cap (PDR security finding S1, LOW) · low · named watch-item owned by the L2a increment gate — the gate decides: bound the capture (stream stdout, abort after MAX_MAP_BYTES+1) or record acceptance with rationale; must not pass silently (ruling R9).
- `diff.py`'s `None`-on-error contract must survive the shared caps · low · AT/TC arms cover it.
- BACKLOG header `Last refresh 2026-10-09` is stale (content refreshed at the review-screen
  close; B-136 added 2026-10-23) · low · corrected at this batch's close reconciliation.
- Outgoing batch vault sync DONE (synced 2026-10-23, light, README only) · closed · ruling R6.
- The B-44 signature pin (`test_a3_census.py:658`) must be amended in the L3 increment, never
  silently · medium · named in LLR-Q3.2.1's traceability and the increment plan.
- **Contamination incident at the L3 gate (2026-10-23):** an unidentified concurrent process
  edited `tests/test_scalecheck.py` mid-gate (a defective derived "Canvas-backing split" test —
  source-text derivation ≠ runtime construction) and touched `design/design-proposal.md` + the
  PDR record byte-equality (mtime only, content unchanged). The foreign test was RED on the
  live tree and unaccounted; it was removed, all L3 evidence re-captured after the removal, and
  the incident declared in increment-001 §5. Lane worktrees (per-lane trees) are the structural
  defence from the fork onwards; the trunk commit for L3 lands immediately to freeze state. · medium · closed by the re-capture + declaration.

## Conventions honored

- Tests run as `env -u NO_COLOR -u TERM python -B -m pytest …` (the harness shell exports
  `NO_COLOR=1`/`TERM=dumb`; Q1 tests set `NO_COLOR=1` deliberately as their input).
- ≤4 SOURCE files per increment; tests uncapped; C11 move-aside RED counterfactual per
  deliverable file; close the axis not the instance (C-65); amendment LLR clauses name their
  asserting test and mutant.
- Refusals name the limit and the map id, never a path; no real person's name, account, email,
  handle or home path in any tracked file (A-110 guard).
- BLUF in every artifact and gate summary; ids grouped by module (Q1/Q2/Q3).

## Out-of-scope carries

- Relation-map port (HANDOFF §9 S1 strategy) — the operator's map-types definition was
  APPROVED on 2026-10-23 (record `quickmap/docs/handoff-mapper/map-types-veredicto-2026-10-23.json`,
  outside this repo), so the port is no longer blocked;
  tracked in `.dev-flow/BACKLOG.md` (B-107 line of carries) and HANDOFF §9 Q2.
- FTS/evidence indexing (C8) and its content-read limits — part of the port, not this batch;
  mapper's only in-app content reads today are the map files and CSV import (verified by grep).
- Attachment file contents — handed to the OS via `osopen`, never read into the app; no cap owed.
- QuickMap's `--no-color` opt-out — ruled out by Q5.
- Deck defects, toast layout (B-80), unfocused-selection-tone verdict (B-70) — their own batches.

## Gate notices and runtime absences

Gate run before Phase 0 (2026-10-23): exit 1 — 15 BLOCK, all on the OUTGOING closed batch's
record (V59 ×14: PR #27's squash-merged files charged to the stale `base_ref`; V64 ×1: §3 citation
not carrying its row). `V7`: bundle identical to the manifest, both directions, 2026-10-12-rev102.
Repaired and re-run green (exit 0) after the V64 re-citation and the rollover re-stamp.

Runtime absences (SKILL.md gate step 5, named once): the reviewer roles (`code-reviewer`,
`qa-reviewer`, `security-reviewer`, `architect`, `ux-reviewer`) have no named sub-agents on this
runtime — the orchestrator (Claude) holds the gates and this worker drafts/runs; every gate
decision is recorded in `decisions_log` under the standing authorization declared in this plan's
header. `V15`, `V16`, `V17` SKIP (no canon tree / hooks on a bundle runtime) — recorded as
not-run. `V30` runs half (interpreter witnessed; flow floors not derivable from a bundle).
Benign NOTICEs declared: `V25` (n/a — origin answered), `V40` (owner is the house-style OMITTED
string — A-110 forbids a profile path in tracked files; the NOTICE is by design), `V57` (the
outgoing batch's close record names no gated-tree commit — pre-existing on the sealed record),
`V62` risk retired at the next gate (Last updated cell maintained), `V53` census counts on
sealed records (never a block). `V8` (ARCHITECTURE.md declares no `path/**` prefixes) pre-exists;
this batch's ARQ amendment does not retire it.

Close-gate packet additions (declared per the close-gate exception — the rows' files are
tests, not code, so no re-review is owed): `tests/test_repair_sidecar.py` row added to
increment-003's §2 table (the R10 cross-batch amendment, landed `37a8175`, previously named
only in the follow-up prose) and `tests/test_diff.py` row added to increment-004's §2 table
(the inc004-F1 follow-up arm, landed `a860a27`) — both to satisfy V59's carried-base limb at
the close gate, 2026-10-24.

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| `python devflow-validate.py --brief <root>` (flow gate #1, pre-repair) | 2026-10-23 | exit 1 — 15 BLOCK on the outgoing record (V59/V64); V7 green |
| `python devflow-validate.py --brief <root>` (gate, post-rollover readback) | 2026-10-23 | exit 0 — 0 BLOCK |
| Measurement probe (sidecar sizes/depths; premises 1, 5) | 2026-10-23 | pasted in §2.7 |
| `python devflow-validate.py --brief <root>` (P1 gate) | 2026-10-23 | exit 0 — 0 BLOCK (first pass: 4 BLOCK — V4 numeric threshold on LLR-Q3.1.1, V14 ×3 future-file consumers — repaired by edit, re-run green) |
| `python devflow-scan-spec.py <contract>` (security scan) | 2026-10-23 | controls ok; flags `session`/`expose` — vocabulary collisions, answered in §6.3 |
| Measurement probe (ruling R1: every perf builder shape constructed + every committed golden parsed) | 2026-10-23 | deep5000 = 5,000/4,999 · wide2000 = 2,000/1,999 · wide6000 = 6,000/5,999 · forest = 6/4 · real maps ≤ 8 · no dense shape exists; largest measured = 6,000 nodes / 5,999 edges → caps 100,000/100,000 — SUPERSEDED by the full-population re-measurement of the F1 disposition (largest committed = 12,000 nodes / 11,999 edges, ledger .5); builders-only population noted for the historical record |
| `python devflow-validate.py --brief <root>` (post-rulings gate) | 2026-10-23 | exit 0 — 0 BLOCK; V62 retired by the `Last updated` cell repair; remaining NOTICEs pre-existing (V53 planned-node citations, template placeholders) |
| Product tests | — | not run in this unit (orchestrator schedules the suite; targeted probes only, per brief) |
| `python devflow-validate.py --brief <root>` (post-disposition gate) | 2026-10-23 | run at this unit's close — see commit message |
| `python devflow-validate.py --brief <root>` (P2 second pass + PDR seal gate, reviewer unit) | 2026-10-23 | exit 0 — 0 BLOCK; NOTICEs pre-existing (V53 planned-test citations incl. the new `evidence/recheck-*.md`, V8, V47 on the seeded 04-validation.md, V23 id-grammar notices as across the record) |
| `python devflow-validate.py --brief <root>` (PDR seal gate) | 2026-10-23 | exit 0 — 0 BLOCK · 640 notice at the PDR station (pre-existing classes: V53 planned-test citations, seeded 04-validation placeholders); after the PDR decision + move to P3/not-started, 9 V2 reds (AT-108…116, no node on disk) — the flow's declared station-expected pair (V2 @ P3: AT ids are provisional until Phase 3 mints the nodes, reconciled at the DDR) |
| Orchestrator's full suite after the merge, `a860a27` tree (P4 gate run; `PYTHONIOENCODING=utf-8 env -u NO_COLOR -u TERM python -m pytest -q`) | 2026-10-24 | exit 1 — 3575 passed, 1 failed, 24 deselected, 3 xfailed (1858 s); the failure = pre-existing flake `test_reqharness_cache_fastpath.py::test_changed_size_or_mtime_takes_full_path`, reproduced 1/6 on master `1609bbe` → B-137. Transcript `evidence/p4-full-suite-a860a27-2026-10-24.txt` (sha256 `00652d2c…4bd592`), committed as `201646c` |
| Collect-only re-derivation of the signed balance (`python -m pytest --collect-only -q`, same env) on the gate tree and on a clean `1609bbe` worktree | 2026-10-24 | gate tree 3579/3603 (24 deselected); base `1609bbe` 3546/3570 (24 deselected) = 3543 passed + 3 xfailed → ledger `3546 − 0 + 33 = 3579` reconciles (`04-validation.md` §Signed-balance) |
| `env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider tests/test_no_operator_paths.py` (A-110 privacy gate before commit) | 2026-10-24 | exit 0 — see the P4 unit's commit message |
| `python devflow-validate.py --brief <root>` (DDR seal gate, reviewer unit) | 2026-10-24 | exit 0 — 0 BLOCK · 633 notice (pre-existing classes: V53 planned-node citations, V23 id-grammar notices incl. the new `evidence/ddr-*.md` finding ids, V41 digest-path shape on increment-002, V26 contract size) |
| Reviewer targeted tests (DDR unit; `env -u NO_COLOR -u TERM`, sequential, never the full suite) | 2026-10-24 | architect: `test_arch_osopen_callers.py` + B-44 node → 6 passed · software-dev: AT-114 toast + diff-side arms → 3 passed; inc9c leak-census → 2 passed · qa-reviewer: hash/collect verifications only |
| `env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider tests/test_no_operator_paths.py` (A-110 privacy gate before the DDR commit) | 2026-10-24 | exit 0 — 2 passed |
| `python devflow-init.py --fold-canon` (P5 close-gate step) | 2026-10-24 | 17 rows folded into `REQUIREMENTS.md`, 0 refused |
| `python devflow-validate.py --brief <root>` (P5+P6 gate #1) | 2026-10-24 | exit 1 — 19 BLOCK (17 × V22 canon fold-back owed + 2 × V59 carried-base) → fold-canon run, two packet §2 rows added (declaration above), re-run green |
| `python devflow-validate.py --brief <root>` (P5+P6 gate, final) | 2026-10-24 | run at this unit's close — see commit message |

## Handoff note — P2 disposition pass (2026-10-23)

This unit (P2 dispositions + PDR transition drafting) closes here. Done: F1 re-measurement
executed and ledgered (.5); F2 file-set correction in contract §2.8/§6, this plan and the ARQ
worksheet (.6); F3 state matrix recorded at design/state-matrix.md and bound in the contract +
AT-115 (.7); m1/m2/m3 fixed inline (.8 names m3's C11 pair); m4 carried to the design proposal
risks; m5/m6 carried to Phase-3 packets; design proposal + PDR record seed drafted; review table
Status column updated for the reviewers' re-check. Next unit: the reviewers' second P2 pass over
the amended contract, then the PDR seal (architect + qa-reviewer), then lanes L1/L2/L3 fork. Open
risks: the PDR seal still owes the reviewers' sign-off; the L2 increment must land the
test_arch_osopen_callers.py allow-list amendment in the same commit as the first reader import
(B-44 discipline); prescan cost measurement owed at the L2 gate.
