# Post-mortem — mapper — Batch 2026-10-23-hygiene-batch

> Phase 5 artifact (`full`), station P5. Co-authors: `architect` + `qa-reviewer`
> (the DDR reviewer swarm evidence stands as both co-authors' checklists — §Evidence
> checklist below). Structured for cross-batch sweeping — section order kept.

## 0 · Gate record — which tree this close gated

| Field | Value |
|---|---|
| Gate record | `PYTHONIOENCODING=utf-8 python <flow bundle>/scripts/devflow-validate.py --brief .` · exit 0 · **0 BLOCK** · 2026-10-24 (first P5+P6 run: 19 BLOCK — 17 × V22 canon fold-back + 2 × V59 carried-base; repaired by `--fold-canon` (17 rows into `REQUIREMENTS.md`) + two packet §2 rows (PLAN.md declares the additions) · final run 0 BLOCK · 639 notice · 61 n/a) |
| Gated tree | dirty — `05-postmortem.md` · `06-docs/*` · `PLAN.md` · `03-increments/increment-003.md` · `03-increments/increment-004.md` · `state.json` · `REQUIREMENTS.md` (the close records + the canon fold — the declared norm at this gate) · HEAD `438ff61` |

> Expected NOTICEs, declared: `V57` (this batch is at `awaiting-sync`, not `closed` —
> the gated-tree comparison runs at the close gate of the next unit); `V25` (no `origin`
> remote — local branch only, never pushed per batch instruction); `V50`/`V51`/`V54`
> read `05-close.md`, which exists only under `core` — the `nofile` SKIP is by design for
> `full`; their substance is carried in this record's §Conditional gate verdicts and
> §Control lineage instead.

## 🔑 At a glance (read first)

- **Outcome:** closed with carry-over — DDR sealed `approved with conditions` (two MINOR
  conditions C1/C2 owed as record work at the trunk join — both DISCHARGED there, commit
  `78d51a2`); validation PASS-WITH-NOTES
  (the one gate failure is the pre-existing flake B-137).
- **Top 3:** ① machine-derived oracles (AST census, derived roster, move-aside RED
  counterfactuals, mutation batteries) caught every requirement drift in-station ·
  ② four process incidents — a concurrent-edit worktree breach, three A-110 privacy
  leaks, a worker-shell env artefact behind a 171-failure run, and a census that missed
  a whole fixture-content consumer class · ③ root cause of the misses: re-derivation
  scoped to the lane's own import surface instead of the input class's full consumer
  set — closed by ruling R10 and proposed as a flow-template control.
- **New control this batch:** none minted (A-110, minted 2026-10-11, held three times);
  one flow-template amendment *proposed*: the C-52 condition-3 census must re-derive
  consumers by fixture content, not import surface alone (owner: flow author).
- **Open items → next batch:** 9 — biggest: the relation-map port (S1 strategy) — the
  operator's map-types definition was APPROVED on 2026-10-23 (record
  `quickmap/docs/handoff-mapper/map-types-veredicto-2026-10-23.json`, outside this repo),
  so the port is unblocked and ready to schedule; plus DDR conditions C1/C2, discharged
  at the trunk join (`78d51a2`).
- **Metrics:** iterations corrected at the trunk join to P1:1 / P2:1 per the counter-honesty
  finding (state.json) · findings
  20 opened / 20 closed (0 blocker · 5 major · 15 minor; C1/C2 closed at the trunk join) · ledger 3546 → 3579 (−0 +33) ·
  gate suite 3575 passed / 1 pre-existing flake.

---

## Detail (reference)

### What worked
- **Machine-derived oracles over prose.** The osopen import census
  (`tests/test_arch_osopen_callers.py`), the renderer roster derived from
  `mapper/views.__all__`, the B-44 signature pin, and the per-deliverable move-aside
  RED counterfactuals kept every record honest; when sealed Q3 thresholds contradicted
  the live tree, the correction came from measurement (ruling R10, ledger `.11`–`.13`)
  and the DDR ruled the derived allow-list — not the ARCHITECTURE prose — the binding
  record (A-DDR-1 ruling, `evidence/ddr-architect.md:29`).
- **P2 caught requirement-defect majors before any code.** F1 (the caps premise
  excluded the tracked 12,000-node perf workspaces), F2 (`osopen.py` missing from the
  C-52 table), F3 (state matrix unrecorded) — all re-derived and folded
  (`02-review.md:10`; ledger `.5`–`.8`), and F1's re-derivation later proved the caps
  carry 8.3× headroom.
- **The lane fork absorbed a mid-batch seam discovery.** L2a's gate found BOUND
  unimplementable without breaking the inc9h `subprocess.run` seam pin; ruling R9/R10
  machinery revised S1 to the seam-pinned form with the cap one call later, and the DDR
  confirmed the revision from the pin itself (`evidence/ddr-software-dev.md:30`).
- **A-110 held three times.** Every home-path/account leak (below) was caught by the
  guard before any push, each repaired by redaction + sha256 re-pin — the guard plus the
  redact-and-re-pin discipline is now a standing convention (`PLAN.md:244,247`).
- **The DDR swarm re-read every claim against on-disk, hash-pinned evidence** — the
  B1 fixture-content miss was discharged with a complete red/green/mutant chain whose
  sha256 prefixes match the ledger (`evidence/ddr-qa.md:18`).

### What didn't / friction
- **Incident 1 — the orchestrator's completion-detection bug let two sessions edit one
  worktree.** During the L3 gate (2026-10-23) an unidentified concurrent session —
  spawned because the orchestrator's completion detection reported the previous session
  done while it was still alive — edited `tests/test_scalecheck.py` mid-gate, planting a
  defective derived "Canvas-backing split" test (source-text derivation ≠ runtime
  construction; it false-flagged `RadialRenderer`, whose construction lives in a
  helper), plus mtime-only touches on `design/design-proposal.md` and the PDR record
  (`PLAN.md:178-181`; declared `03-increments/increment-001.md:210-216`). Fallout: the
  foreign test was RED on the live tree and unaccounted; cost was removal + full L3
  evidence re-capture (battery + GREEN re-run); no shipped-code contamination. Closed by
  the re-capture + declaration (`PLAN.md:182-184`).
- **Incident 2 — home-path leaks, caught by A-110 three separate times.** (a) The
  L1/L2a/L2b evidence transcripts carried the Windows home-path account segment — caught
  pre-commit by the A-110 gate; redaction commit `b202856` replaced it with `<user>`
  byte-exact and re-pinned every citation (23 files; ripple: `78bba97`'s and `a4d573f`'s
  messages cited pre-redaction digests, corrected in the increment reviews). (b) The
  committed post-merge full-suite transcript contained the segment — A-110's own two
  tests FAILED inside that very run (`evidence/full-suite-after-merge-2026-10-23.txt`
  lines 8846-8847); repaired by `cd32081` (441 lines) + re-pin. (c) `evidence/
  review-inc003.md` quoted the privacy-grep positive control's real planted path;
  repaired by rephrase `7117945`. Standing convention recorded in every follow-up
  transcript header: account name → `<user>` before hashing/storage.
- **Incident 3 — the 171-failure run was a worker-shell artefact.** The post-merge full
  suite ran in a worker shell exporting `NO_COLOR=1`/`TERM=dumb` and reported
  `171 failed, 3314 passed … in 1788.61s` (`evidence/full-suite-after-merge-2026-10-23.txt:8984`)
  — an environment artefact, not a regression; the record marks it SUPERSEDED
  (`04-validation.md:31,172`). Remedy adopted as written convention: every run as
  `env -u NO_COLOR -u TERM python -m pytest …` (`PLAN.md:188-189`); the orchestrator's
  clean-env re-run isolated the true state (3 failed / 3568 passed, later fully
  discharged — see Incident 4).
- **Incident 4 — the crossed census missed the B1 consumer.** The PDR condition-3
  crossed census and L2a's reverse census re-derived consumers by *import surface*
  (`tests/test_ingestion_limits.py` / `store.py`), missing three pre-existing
  `LLR-N13.1.7` arms in `tests/test_repair_sidecar.py` whose *fixtures* are
  anchor-bearing sidecars fed through `load` with post-compose expectations — exactly
  what L2a's prescan now refuses (`increment-003.md:311-323`). The miss surfaced as
  3 failed / 3568 passed in the orchestrator's clean run, was ruled by R10 (LLR-Q2.1.2
  stands; N13.1.7 superseded in part; the three arms amended in place — typed-refusal
  assertions, original value-leak bounds kept, commit `37a8175`), and discharged with
  the M-Q2-1-XB14 red/green/mutant chain (`xbatch14-*-2026-10-24.txt`, sha256 prefixes
  pinned at `increment-003.md:333-335`; ledger `.14`). Lesson (proposed flow control):
  *a rule that refuses an input CLASS must re-derive its consumer tests by fixture
  content, not only by import surface* (`increment-003.md:337-341`); qa-reviewer
  endorsed baking it into the C-52 condition-3 census template as a flow-authoring
  decision (`evidence/ddr-qa.md:34`).
- **Counter honesty finding:** `state.json iterations_per_station` recorded 0 for every
  station at P5, yet P1's first gate pass returned 4 BLOCKs (V4/V14) that were repaired before
  the green re-run (`PLAN.md:234`), and P2 formally iterated (`iterate-to-refine` →
  amendments → second pass `approve`, `02-review.md:10`; `PLAN.md:87-97`). Neither
  re-pass incremented the counter — the metric under-reported real iteration. Corrected
  at the trunk join: state.json now records P1:1, P2:1. Proposed
  flow fix (owner: flow author): count repaired first-pass gate BLOCKs and formal
  iterate-to-refine passes, or record them in a side field this artifact names.

### Scope drift (planned vs actual)
| Planned | Actual | Note |
|---------|--------|------|
| 3 increments (L1 colour · L2 ingestion · L3 sweep/audit) | 4 lanes — L2 forked by ruling R7 into L2a {store,diff,osopen} + L2b {import_csv,screens/home} | F-UX-1 (CSV refusal toast, MAJOR) fit no lane's set; fork at the PDR gate, AT-114 observed through the running screen (ledger `.9`, `PLAN.md:103-105`) |
| L2b owns 2 source files | L2b commit `a4d573f` touches 5 (2 own + 3 declared L2a revision) | S1 seam revision forced by the inc9h pin + newline parity; over-budget landing declared, reason recorded (`increment-004.md:267-268`); lane union = the C-52 L2 set exactly |
| Sealed Q3 thresholds `.11`/`.12`/`.13` stand as written | R10 corrected all three from measurement at the L3 RED gate | measured-truth amendments, ledger `.11`–`.13` (`PLAN.md:160`); the sweep oracle now asserts construction-census truth |
| S1 BOUND (streamed `git show`) | S1 seam-pinned form; cap enforced one call later in `store._capped_side_graph`; D3 seals | pin sweep at the L2b gate found the inc9h seam pin; ruling recorded, DDR-confirmed (`increment-003.md:215-223`; `evidence/ddr-software-dev.md:30`) |
| Cross-batch tests untouched | 3 sealed `LLR-N13.1.7` arms amended in place | owning batch sealed, not edited — amendment by ruling R10 with names unchanged (`01-requirements-ledger.md:106`) |

### Metrics (full)
| Metric | Value |
|--------|-------|
| Iterations per station | `{P0:0,P1:1,P2:1,P3:0,P4:0,P5:0,P6:0,ARQ:0,DDR:0,PDR:0}` — corrected at the trunk join to the real counts the counter-honesty finding names (P1 first-pass 4 BLOCKs repaired pre-re-run → 1; P2 one formal `iterate-to-refine` → 1); the P5-time zeros under-reported (see Counter honesty finding) |
| Findings opened / closed | 20 / 20 (the 2 DDR conditions C1/C2 discharged at the trunk join, commit `78d51a2`) |
| Findings by severity (blocker/major/minor) | 0 / 5 / 15 — majors: P2 ×3 requirement-defects (F1 caps premise, F2 osopen omission, F3 state matrix) + P3 ×2 code (inc003-F1 unbounded anchor name; inc004-F1 dropped decode guard), all discharged at `a860a27` |
| Where caught (P2 / P3 gate / P4) | 7 / 9 / 0 — P4 caught no new defects; it recorded B-137/138/139 to the backlog and validated PASS-WITH-NOTES |
| Test ledger (base − D + A = post) | 3546 − 0 + 33 = 3579 (31 new defs + 2 parametrized expansions; collect re-derived 3579/3603 on the gate tree — `04-validation.md:154-158`) |
| Files touched · increments (cap trips) | 7 product source files across 4 lanes + 1 follow-up commit (`a860a27`) · 4 increments (0 undeclared cap trips; 1 declared over-budget landing) |
| Gate suite | 3575 passed / 1 failed / 24 deselected / 3 xfailed, 1858 s at `a860a27` — transcript sha256 `00652d2c…4bd592`; the 1 failure = B-137, reproduced 1/6 on master `1609bbe` |
| Prescan cost at scale | +3.54 s median on the 12,000-node shape (41.60 % of an 8.51 s load, 5 reps) — measured, watch item, not a gate (`evidence/l2a-prescan-cost-2026-10-23.txt`) |

### Root causes (only if a phase took ≥2 iterations)
- **P2's formal iteration:** the caps premise was written from the nominal map corpus and
  never re-derived against the *tracked* workspace content (the 12,000-node perf
  workspaces) — a fixture-population blind spot in a premise; the C-52 table likewise
  omitted `osopen.py` because the seam module had no consumers yet. Root cause class:
  *premises and censuses scoped to what the author remembered, not what the tree
  holds* — the same class as Incident 4, closed both times by machine re-derivation.

### Process / workflow findings
- Incident 1 → **adopted control: per-lane worktrees from the fork onwards + an
  immediate trunk commit to freeze state + a CAUTION contamination check
  (`git status` before each packet)** — exercised by later lanes (`increment-004.md:247-249`
  records a clean check). Owner: orchestrator.
- Incident 2 → **A-110 privacy gate before every commit + redact-and-re-pin discipline**
  (existing control, stress-tested ×3, held ×3). Owner: every dev-flow worker; enforced
  by `tests/test_no_operator_paths.py`.
- Incident 3 → **clean-env convention (`env -u NO_COLOR -u TERM`) for every test run +
  supersession inspection of any anomalous headline before it is believed.** Owner: all
  workers; the orchestrator's gate run re-derives suspect claims.
- Incident 4 → **proposed flow-template control: the C-52 condition-3 census template
  mandates a fixture-content consumer pass** for any rule refusing an input class.
  Owner: flow author (qa-reviewer endorsement, `evidence/ddr-qa.md:34`).
- inc001-F1 → **adopted convention: `exit=$?` final line on every evidence transcript**
  (`increment-001.md:258-259`; visible in all `fu-*-2026-10-24.txt`).
- Counter honesty → proposed flow fix for `iterations_per_station` (owner: flow author).

### Product findings
- Prescan +3.54 s on the 12,000-node shape (41.6 % of load) — candidates named:
  CSafeLoader / scanner-only prescan; real maps ≤ 8 nodes pay ≈ 0 (`design/DDR-…md:114`).
- `LLR-N13.1.7` superseded in part by LLR-Q2.1.2 (ruling R10) — sealed arms amended in
  place, names unchanged.
- Carried to backlog: B-136 (dim-text audit events, ruled R4), B-137 (mtime flake),
  B-138 (outline dangling-edge crash — derivation-found at P2 F3; latent, no shipped
  parser route reaches it), B-139 (transient review-env flakes; poll-with-deadline
  remedy deliberately not applied mid-batch).

### Control lineage
- **New control proposed this batch:** none minted into the project's control catalog;
  the fixture-content census amendment is proposed to the flow author (status: propose).
  Working conventions adopted this batch (orchestrator-level, recorded in PLAN.md):
  clean-env runs · per-lane worktrees + contamination check · redact-and-re-pin ·
  `exit=$?` transcript line.
- **Prior controls exercised:** A-110 (held ×3 — see Incident 2) · B-44 same-landing pin
  discipline (osopen allow-list, D1 signature — both amended with their first import)
  · C-18 (held; two honestly-declared exceptions written into the contract itself:
  AT-111 realized as two lowercase-named nodes, AT-116 one-chain-three-nodes) ·
  C-25 clean-shell full-suite as the only verdict-bearing run · C-44 working-file
  reconciliation (sweep below; the seeded found-before field preserved) · C-52 lane
  file budgets (1 declared over-budget landing, reason recorded).

### Open / deferred items → next batch
| Item | Type (process/product) | Reason deferred | Trigger / owner |
|------|------------------------|-----------------|-----------------|
| ⏸ DEFER B-136 — dim-text Canvas audit events | product | ruled R4 (hook ships clip+overprint; `dim` kind lands later on the same `put` path, no interface change) | next hygiene increment touching `mapper/canvas.py` (BACKLOG.md:247) |
| ⏸ DEFER B-137 — `test_changed_size_or_mtime_takes_full_path` flake | product | pre-existing, reproduced 1/6 on master `1609bbe`; per P-05 no batch arm rests on it | backlog; investigate order/load dependence (BACKLOG.md:257) |
| ⏸ DEFER B-138 — dangling-edge graphs crash `OutlineRenderer` | product | latent: no shipped parser route reaches it (DDR-residual 5 verified from the parsers) | batch owning `mapper/views/outline.py` — decide refusal vs tolerance (BACKLOG.md:258) |
| ⏸ DEFER B-139 — poll-with-deadline for transient review flakes | product | remedy deliberately not applied mid-batch (inc003-F4/inc004-F3, unreproduced) | next touch of the AT-114 arm (BACKLOG.md:259) |
| C1 — amend `docs/ARCHITECTURE.md` "ONE name" prose to the measured six-name import | process (record) | DDR condition; record work, not code | ✅ DISCHARGED at the trunk join — commit `78d51a2` (`docs/ARCHITECTURE.md:65` + §3 `store`/`import_csv`/`osopen` rows re-read; the derived allow-list binds) |
| C2 — record the LEAK_EXCEPTIONS carry as the inline declaration + reword `mapper/screens/home.py:533-534` | process (record) | DDR condition; a registry entry is impossible by construction (F-SD-1 ruling) | ✅ DISCHARGED at the trunk join — commit `78d51a2` (comment reworded at `mapper/screens/home.py:527-534`; the inline declaration is the carry) |
| Prescan cost at scale (+3.54 s / 12,000-node shape) | product | measured watch item, not a gate | future perf pass — CSafeLoader / scanner-only prescan candidates |
| Relation-map port (the S1 port strategy; operator reference "R1") | product | the operator's map-types definition was APPROVED on 2026-10-23 (record `quickmap/docs/handoff-mapper/map-types-veredicto-2026-10-23.json`, outside this repo) — the port is NOT blocked; ready to schedule | next batch owning the port; tracked via the B-107 line of carries and HANDOFF §9 (this batch: `PLAN.md:199-202`; no dedicated BACKLOG row yet — the close/sync unit files one) |
| Prototype verdicts `round-2026-10-23` / `round-2026-10-24` (under `prototypes/`) → the next UI batch | process | **gap closed (record correction):** the verdicts exist — `prototypes/round-2026-10-23/verdict-2026-10-24.json` and `prototypes/round-2026-10-24/verdict-2026-10-24.json` in the main checkout; `prototypes/` is git-ignored by design, so they are not in this worktree | the next UI batch's P0 intake reads them at those paths (main checkout) — RC-1 reads the backlog |

### Working-file reconciliation (C-44) — MANDATORY, every file this batch touched
Sweep run: `git status --short` in this worktree (the only repository this unit touched);
`git log @{u}..HEAD` — no upstream (never pushed, per batch instruction); no open PRs.

| Repo | File(s) | Terminal state | Landing / backlog ref |
|------|---------|----------------|-----------------------|
| mapper (worktree `wt-hyg`, branch `feat/hygiene-batch`) | `.dev-flow/2026-10-23-hygiene-batch/05-postmortem.md` + `06-docs/executive-summary.md` · `functionality.md` · `traceability-matrix.md` (+ this PLAN edit) | ✅ committed at this unit's close — local branch, never pushed | local commit on `feat/hygiene-batch` (this record's §0 gate names it); vault sync at `/dev-flow-sync` |

- **Found before the batch:** `.dev-flow/2026-10-15-review-screen-batch/05-close.md @ cc239c4a2512abbe30222d04ce020e05daf01a46`

**Conditional gate verdicts:** gates that closed as *"once items 1–N land this is a
PASS/MERGE"*, each discharge verified by re-reading the artifact.

| Conditional item | Discharged? | Verified how |
|---|---|---|
| PDR condition F-UX-1 — CSV refusal toast (owner owed before the fork) | ✅ | `mapper/screens/home.py:524-541` ships the typed toast; AT-114 observed through the running screen (ruling R7, ledger `.9`; DDR row `evidence/ddr-software-dev.md:21` executed green) |
| PDR condition S1 — diff-side capture bounded at the L2 gate | ✅ | seam-pinned form at `mapper/diff.py:35-55` + cap at `mapper/store.py:762-767`; DDR open point 3 ruling (`evidence/ddr-software-dev.md:30`); D3 seals |
| PDR condition N3 — `diff → osopen` import barred | ✅ | R8 bar pinned by `tests/test_arch_osopen_callers.py`; DDR row 4 re-verified (`evidence/ddr-architect.md:20`) |
| DDR condition C1 (A-DDR-1) — ARCHITECTURE.md "ONE name" prose amendment | ✅ | discharged at the trunk join — commit `78d51a2`; `docs/ARCHITECTURE.md:65` + §3 rows re-read, now stating the measured six-name set |
| DDR condition C2 (F-SD-1) — LEAK_EXCEPTIONS inline carry recorded + comment reword | ✅ | discharged at the trunk join — commit `78d51a2`; `mapper/screens/home.py:527-534` re-read, the inline declaration recorded |

### Evidence checklist — architect + qa-reviewer
The DDR swarm's re-read tables stand as both co-authors' completed checklists
(`evidence/ddr-architect.md` — 9 checklist rows re-read, 2 rulings; `evidence/ddr-qa.md`
— 8 rows + an independent fixture-content re-derivation closing open point 1, 6 residual
risk rulings; `evidence/ddr-software-dev.md` — 12 rows + open points 3/4 rulings, 5
targeted tests executed green). P5-specific items:

| Item | ✓/✗ | Evidence |
|---|---|---|
| Metrics re-derived from 04-validation.md (ledger 3546−0+33=3579; gate 3575/1/24/3) | ✓ | `04-validation.md:26,35,154-158`; transcript sha256 pinned |
| Four incidents cited to file:line / transcript | ✓ | `PLAN.md:178-189,244,247`; `increment-001.md:210-216`; `increment-003.md:311-341`; `full-suite-after-merge-2026-10-23.txt:8846-8847,8984` |
| Open items keyed (B-136…B-139 in BACKLOG; C1/C2; port; prototype-rounds gap) | ✓ | `BACKLOG.md:247,257-259`; DDR §C; `PLAN.md:199-202,52` |
| Working-file sweep run, found-before field preserved | ✓ | §Working-file reconciliation above |
| Gate run 0 BLOCK at the §0 record | ✓ | §0 Gate record row |
