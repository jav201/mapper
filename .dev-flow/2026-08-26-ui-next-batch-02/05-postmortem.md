# Post-mortem — mapper — Batch 2026-08-26-ui-next-batch-02

> **Artifact language:** English (the batch's development language, `state.json` `language`).
> Phase 5 artifact. Co-authors: `architect` + `qa-reviewer` (in `full`). This copy is **drafted by
> `deepseek/deepseek-v4-pro` via `opencode run`, to be verified by the orchestrator** — no `architect`
> or `qa-reviewer` agent authored it.

## 0 · Gate record — which tree this close gated

| Field | Value |
|---|---|
| Gate record | `python devflow-validate.py --brief <repo root>` exit 1 · 48 block, every one dispositioned in §Validator waivers (V59 28, V53 10, V2 5 → B-101, V56 3, V1 1, V22 1) · 2026-10-08 |
| Gated tree | `e56b774d9901b01ca2c77f96697607bac26b2124` · dirty — `.dev-flow/BACKLOG.md`, `.dev-flow/2026-08-26-ui-next-batch-02/05-postmortem.md` (the close record itself) |

> Written at the close gate from that run's own `git rev-parse HEAD` and `git status --porcelain`.
> The merge itself is squash `46e190b` (branch tip `4572e52`), and the one complete gate run on that
> tree is **2797 passed / 0 failed** (`gate-run-master-tree.txt`).

## 🔑 At a glance (read first)

- **Outcome:** closed with carry-over — the batch was **parked at its first PDR gate** (2026-08-26) and
  **un-parked** (2026-08-27) on a repair-batch base, then merged as squash `46e190b` on 2026-10-03
  with 24 open items carried to the next batch.
- **Top 3:** ① the Inc-9 security line only converged after deny-lists were replaced by closed
  allow-lists (`S1` for URLs, `safe_local_path` for paths). ② Five instruments across three agents
  failed their own controls first — every one caught and withdrawn by its own author
  (`postmortem_thesis_VERBATIM`). ③ Record-accuracy defects survived to be caught by reviewers, not
  eliminated by the process (`B-81`, `INC9G-R8`).
- **New control this batch:** the closed allow-list rule (typed repo URLs `S1`; local paths
  `safe_local_path`/`confine_reason`), plus the `test_no_operator_paths` guard (`A-110`).
- **Open items → next batch:** 24 — biggest is `B-36`, the one-keystroke durable data-loss defect
  (first scope item of the follow-on design batch).
- **Metrics:** iterations 7 · findings not recorded (no cumulative open/closed tally — see below) ·
  ledger 429 → 2797.

---

## Detail (reference)

### What worked
- **The security line converged only after moving from deny-lists to closed allow-lists.** For typed
  repo URLs, operator ruling `S1` ("Lista cerrada", `VERDICT-inc9-2026-09-30.md:167`) accepts only
  `https://host[:port]/path` or `git@host:path` and refuses everything else before any process. For
  local paths, `osopen.safe_local_path` / `confine_reason` (`04-validation.md:145`, A-119…A-127)
  replaced the drifting deny-list with one containment helper. The squash commit message records it:
  "closed allow-lists for typed repo URLs (S1) and local paths" (`git show 46e190b`).
- **Repeated review rounds per increment forced defects out, and no HIGH was ever self-cleared.**
  Inc-4c ran three code-review rounds, Inc-5 five, Inc-STRIPS four, Inc-CRUMB four
  (`state.json` `p3_progress.closed` Inc-4c / Inc-5 / Inc-STRIPS / Inc-CRUMB). Every fixed tree went
  to a fresh independent reviewer.
- **The whole-UI English migration (`Inc-EN`, EN-1…EN-9) was driven by a mechanical census**, not
  hand-editing: ~230 Spanish strings across 14 source files and ~150–180 pinning assertions
  (`VERDICT-inc-en-2026-10-02.md:3-7`), cut after the operator's ruling "Todo en inglés, también la UI"
  (`VERDICT-inc8-legend-2026-09-28.md` § LANGUAGE RULING, `BACKLOG.md` B-71).
- **`test_no_operator_paths` (A-110) made the operator-identity scrub executable** — 261 occurrences
  across 70 tracked files replaced, guarded by `tests/test_no_operator_paths.py`
  (`BACKLOG.md:99`, `04-validation.md:92`).
- **The squash merge kept operator data out of `master`'s history.** Ruled by `M2`/`M5`
  (`VERDICT-merge-2026-10-03.md:15,26`): one squash commit with the operator's noreply identity,
  verified tree-identical to the branch tip and free of account name / personal email.
- **Reviewers caught record-accuracy defects that the process did not.** `INC9G-R8` (the Inc-9g record
  claims "34/34 run killed" while reviewer R8 survives) and `B-81` (Inc-9r record overstates, names
  intended killers not the first `-x` failure) are both recorded as gaps, not shipped
  (`04-validation.md:97,172,189`).

### What didn't / friction
- **The batch was parked and then rejected twice at PDR.** First PDR pass: 13 blockers (10 qa + 3
  security), parked by operator decision. On un-park, a live `S-02` was found — the `SATISFIED-EXTERNALLY`
  strike was wrong — plus a phantom requirement (`LLR-STO.1.1`, 24 occurrences, zero headings) and
  `docs/ARCHITECTURE.md` never actually amended despite ARQ recorded approved (`state.json`
  `decisions_log` 2026-08-26 / 2026-08-27 entries).
- **Five instruments across three agents failed their own controls first**, every one caught and
  withdrawn by its own author — the batch's thesis, recorded verbatim as evidence
  (`state.json` `p3_progress.postmortem_thesis_VERBATIM`).
- **The suite was not hermetic for the whole batch.** `HERMETIC-1` (a default-lane test shelling out to
  the `gh` CLI over the network) made the suite un-runnable offline until the Inc-CONFIRM fix
  (`state.json` `p3_progress.hermetic_defects`).
- **Agent incidents during reviews, each disclosed in the record:** a code-reviewer probe walked pytest
  from `C:\` (`state.json:1287`, Inc-9q); a code-reviewer probed a UNC path — possible local name lookup
  (`state.json:1401`, Inc-9m); the security reviewer's harness let a real `resolve()` reach a
  non-existent host (`SPYHOST`) — possibly one name lookup (`VERDICT-inc9-2026-09-30.md:207-208`);
  eight of nine Inc-EN commits carried the repository's configured author identity, not the
  environment identity (`increment-055-en9.md:63`, `state.json:1169`).
- **External blocks declared, not hidden:** the flow bundle's `V7` revision-label drift (15 other
  pre-existing blocks) and `C-45 PULL` (~37 unadopted flow revisions) are both recorded as deferred
  (`state.json` `p3_progress.external_blocks`).
- **One open flake at merge:** `FLAKE-2` (`test_hlr_n16_4_legend_declares_its_own_keys`), failed once
  under load, 10/10 alone (`04-validation.md:168`, `state.json:1184-1186`).

### Scope drift (planned vs actual)
| Planned | Actual | Note |
|---------|--------|------|
| US-N06 atlas canvas, US-N07 search, US-N13 sala, US-N16 leyenda + palette-v2 tokens + B-05 + `Canvas.rows()` defect (`PLAN.md:26-29,74-80`) | All four landed (N06/N07/N13/N16) | On scope |
| US-N14 «lente» field query | **Cut to a follow-on design batch** | Operator option A RE-SCOPE, removing ~7 of ~11 design rulings (`state.json` `decisions_log` 2026-08-27 "operator option A — RE-SCOPE") |
| Not planned | Inc-8 legend, Inc-9a…9s (repo/path hardening + English chrome), Inc-SEED / SEED-2, Inc-SCRUB, G6 surrogates, Inc-X3 attachment chips, Inc-EN (EN-1…EN-9) English UI, whole-branch Gate-1 / Gate-2 | Large scope **addition** — the security line and the English migration both grew after the batch opened |
| Not planned | Whole-branch adversarial PR QA + security gate | `VERDICT-merge-2026-10-03.md` — the merge gate the plan already named (`PLAN.md:64`) |

### Metrics (full)
| Metric | Value |
|--------|-------|
| Iterations per station | `{P0:2,ARQ:1,P1:1,PDR:3,P2:0,P3:0,DDR:0,P4:0,P5:0,P6:0}` (sum 7) — `state.json` `iterations_per_station` |
| Findings opened / closed | not recorded — the batch tracks findings per review block (`F1`, `F2`, …) with no single cumulative open/closed tally in `state.json` or any review record |
| Findings by severity (blocker/major/minor) | not recorded — no batch-wide severity tally exists; per-station figures ARE recorded (see note below) |
| Where caught (P2 / P3 gate / P4) | not recorded — no cross-phase "where caught" tally exists |
| Test ledger (base − D + A = post) | base 429 collected (`PLAN.md:405`) → post 2797 passed (`gate-run-master-tree.txt`; units differ); `base − D + A` not closed — D/A were not recorded as one pair (`04-validation.md:160`) |
| Files touched · increments (cap trips) | 292 · 126 (`2`) — `git show --stat 46e190b` reports 292 files changed; 126 `increment-0*.md` packet files across 57 numbered increments (counted with `ls`); 2 declared source-file-cap breaches |

> **Findings note (why not recorded):** the only recorded, citable finding counts are per-station or
> per-gap, not a batch total — PDR pass 1 "qa 10 blockers / 14 majors / 11 minors; security 3 blockers
> / 6 majors / 5 minors" and PDR pass 2 "architect 6 blockers; security S-16/S-17/S-18; qa 8; ux 10
> (two blocker-class)" (`state.json` `decisions_log`); and 22 terminal open items in `04-validation.md`
> §Gaps. Counting "findings opened/closed" across ~40 review blocks would be an invention, not a
> citation, so it is left `not recorded`.
>
> **Increments note:** 126 `increment-0*.md` files under `03-increments/` (the `ls` count requested)
> span 57 numbered increments `001`–`057` plus their code/security/confirmation review packets. The
> two **cap trips** are both declared source-file-budget breaches: Inc-2 at 6 source files ("the
> breach #D5", `state.json:413`) and Inc-3 at 6 source files ("DECLARED breach, widened from A-89's
> five to six by A-97", `state.json:429`).

### Root causes (only if a phase took ≥2 iterations)
- **P0 = 2 iterations (park / un-park).** Root cause: the parked record carried a false premise. The
  un-park's `SATISFIED-EXTERNALLY` strike for `S-02` was wrong — `S-02` was independently reproduced on
  a third harness with a positive control (`state.json` `decisions_log` 2026-08-27, "orchestrator
  verifications of lens blockers").
- **PDR = 3 iterations.** Root cause: the requirement record and the tree disagreed. The
  reconciliation audit found **51 union items against 6 briefed** — `docs/ARCHITECTURE.md` never
  amended (work that never landed, C-44), a phantom `LLR-STO.1.1`, and a 12-vs-18 pinned-digest
  miscount (`state.json` `decisions_log` "RIDER-1 reconciliation executed"). The batch was referred to
  the operator and re-scoped (option A) rather than spending the final iteration
  (`02g-lens-reconciliation.md`, merged as PR #7).

### Process / workflow findings
> About the dev-flow itself. Feeds workflow improvement — kept separate from product.
- **A code fix never discharges a missing requirement** — ruling D26 (`state.json` `decisions_log`
  "D26-D31 recorded"). → keep the requirement-stub + repair-increment pattern for carries.
- **STRIKE-OR-ANNOTATE**, and the deeper **A correction that changes the number but keeps the
  instrument has not corrected anything** — both minted 2026-09-19, and the second exists because the
  first failed on its own third exhibit the same day (`state.json` `controls_for_engineering_rules`).
  → a newly minted control does not protect the increment that minted it; controls need their own
  worked example re-validated.
- **"Flaky" describes a symptom; the cause is often an undeclared external dependency.** the repair-era `FLAKE-2` (a
  different test) was renamed `HERMETIC-1` because it shelled out to `gh` over the network
  (`state.json` `hermetic_defects`); this batch re-used the id `FLAKE-2` for the legend paint race (B-98). → name the cause, not the symptom.
- **A record cited by a reader in flight is frozen until that reader returns** — a multi-agent
  operating rule minted 2026-09-18 (`state.json:1785`). → belongs in `docs/engineering-rules.md`
  beside one-writer-per-tree.
- **A hand-maintained census is a defect, including in a requirements table** (P-18) and **a hand-count
  in a carry is the same defect** (P-19) — carried from the repair batch and reproduced again this
  batch (`BACKLOG.md:136-137`). → derive counts by walk, never by hand.

### Product findings
> About the code/product under development.
- **`B-36` — one keystroke durably overwrites a map and its sidecar, no confirmation. LIVE through this
  batch by decision.** Both cheap remedies were executed and both failed, so it is a design ruling with
  no cheap fix (`BACKLOG.md:159`). First item of the next design batch.
- **`B-33` / S-15 / M-H3 — `MAX_RENDER_NODES` bounds the count, not the work.** A 73-node map cost
  72.5 s while the 12 000-node cap waved it through, because cost is edge-driven
  (`BACKLOG.md:156`). Live on `master`.
- **`B-31` — mechanism withdrawn, carried as an unverified observation**, so a fix built for it would
  target a defect nobody has demonstrated (`BACKLOG.md:154`).
- **Inc-9 line LOW residuals (`B-79`)**: the walk-to-write TOCTOU is narrowed, not closed; hard links
  are not detected on an opened attachment's parents (`BACKLOG.md:168`).

### Control lineage
- **New control proposed this batch (status: propose):**
  - The **closed allow-list rule** for typed repo URLs (`S1`) and local paths (`safe_local_path`) —
    origin finding: four rounds in a row found a new odd URL form under the deny-list
    (`VERDICT-inc9-2026-09-30.md:162`).
  - The **`test_no_operator_paths` guard** (`A-110`) — origin: operator-identity scrub (Inc-SCRUB,
    `BACKLOG.md:99`, `04-validation.md:92`).
  - **STRIKE-OR-ANNOTATE** and the **correction-keeps-instrument** corollary — origin: three cases in
    one increment, including the `EXPORT_MAX_CELLS` double-defect (`state.json`
    `controls_for_engineering_rules`).
- **Prior controls exercised:** `C-21` (re-derive the cut on any amendment — fired for the Inc-4 split
  and the Inc-B55/S-D re-cuts, `state.json` `cut_amendments`); `C-44` (un-landed work — caught
  `docs/ARCHITECTURE.md` never amended); `C-55` (positive/negative controls on absence claims);
  `C-25`/`C-19` (one complete run, read from captured output); the ≤4-source-file budget (2 declared
  breaches, both re-ratified rather than hidden); the `full`-mode merge gate (adversarial PR QA +
  security sign-off, `VERDICT-merge-2026-10-03.md`).

### Open / deferred items → next batch
| Item | Type (process/product) | Reason deferred | Trigger / owner |
|------|------------------------|-----------------|-----------------|
| B-36 | product | one keystroke overwrites map + sidecar; both cheap remedies failed; design ruling, no cheap fix | next design batch — first item, ahead of «lente» (`BACKLOG.md:159`) |
| B-79 | product | Inc-9 line LOW residuals: TOCTOU narrowed not closed; hard links undetected on attachment parents | next hardening pass (`BACKLOG.md:168`) |
| B-80 | product | fixed ~60-col toast leaves one-word orphans at 118/140 and overlays the key-bar | next design batch, prototype round first (`BACKLOG.md:169`) |
| B-81 | product | Inc-9 record accuracy: `increment-044-inc9r.md` overstates / names intended killers | correct with Inc-9s or a later cleanup (`BACKLOG.md:170`) |
| B-82 | product | coverage/editor modals have no legend route (`UNMIGRATED_SCREENS`) | give both a legend route in a later design batch (`BACKLOG.md:186`) |
| B-83 | product | at 87 cols `M` focuses the hidden `#insp-field-D`, typed text goes into it | design batch (with B-86) (`BACKLOG.md:187`) |
| B-84 | product | `_write_tmp` and `export.save_svg` write through a planted hard link (`BRANCH-SEC-F5`) | security hardening batch (`BACKLOG.md:188`) |
| B-85 | product | lane renderers paint raw control chars; latent, unreachable today (`BRANCH-SEC-F6`) | hardening (`BACKLOG.md:189`) |
| B-86 | product | coverage `↵` focuses the hidden field — second route of B-83 (`PR-QA-F6`) | design batch, with B-83 (`BACKLOG.md:190`) |
| B-87 | product | focus parks on the hidden rail after a modal closes (`PR-QA-F7`) | design batch (`BACKLOG.md:191`) |
| B-88 | product | connect-repo selection marker on two rows; `1 releases` (`PR-QA-F8`) | small polish (`BACKLOG.md:192`) |
| B-89 | product | prompt placeholder reads like a default; empty `↵` closes silently (`PR-QA-F9`) | design batch (`BACKLOG.md:193`) |
| B-90 | product | palette lists `legend ?` on connect-repo where `?` types (`PR-QA-F10`) | with B-82 (`BACKLOG.md:194`) |
| B-91 | product | connect-repo chrome + `press ↵ ↵` hint + github badge for any https host (`PR-QA-F11`) | design batch (`BACKLOG.md:195`) |
| B-92 | product | dead `c`/`r` on an empty home (`PR-QA-F12`) | design batch (`BACKLOG.md:196`) |
| B-93 | product | CSV import paints the root row as `? Root` | small (`BACKLOG.md:197`) |
| B-94 | product | mirror fetch config keys not pinned (`remote.<n>.uploadpack`, `core.sshCommand`) | with B-96/B-97 (`BACKLOG.md:198`) |
| B-95 | product | `I`-toggle keeps a false `edge of the map` hint (`GATE2-REV-F1`, MEDIUM) | next batch (operator: backlog, merge first — VERDICT-merge M4) (`BACKLOG.md:199`) |
| B-96 | product | repo-config parsing hardening (`column.ui`, `i18n.logOutputEncoding`) (`GATE2-REV-F2`, LOW) | with B-94 (`BACKLOG.md:200`) |
| B-97 | product | tampered-cache hook + small carries (`GATE2-REV-F3/F4`, LOW) | next hardening pass (`BACKLOG.md:201`) |
| FLAKE-2 | product | `test_hlr_n16_4_legend_declares_its_own_keys` fails once under load (`left` worked but not painted), 10/10 alone | re-run solo on flake (`04-validation.md:168`, `state.json:1184-1186`) |
| INC9G-R8 | product | Inc-9g mutant R8 survives (reviewer) though the record claims 34/34 killed; an A-115 branch has no killing witness | next batch: add the witness arm and correct `increment-033-inc9g.md` (`04-validation.md:189`) |
| B-100 | product | HLR-N13.3 has no on-disk test and HLR-N16.3's `AT-044` was never realised (P6 traceability gaps G-2/G-3, found by the qa-reviewer pass) | not found until P6 | next batch |
| B-101 | product | AT-033/034/035/041/042 have no on-disk node by id (validator V2 at close) | found at close | next batch |

### Working-file reconciliation (C-44) — MANDATORY, every file this batch touched
> Run as a sweep in this worktree: `git status --short` (→ one untracked file, below) and
> `git log origin/master..HEAD --oneline` (→ the two close-record commits on `docs/ui-next-02-close`,
> landed by PR to `master` per the operator's 2026-10-08 ruling). The batch's code merge is already on `master`.

| Repo | File(s) | Terminal state | Landing / backlog ref |
|------|---------|----------------|-----------------------|
| mapper | merged batch — source, tests, `.dev-flow/` records | ✅ committed + landed | squash `46e190b` on `master` (branch tip `4572e52`, 391 commits) |
| mapper | `04-validation.md`, `06-docs/`, `REQUIREMENTS.md`, `state.json` | ✅ committed — landing by PR | `6e3bb67`, `e56b774` on `docs/ui-next-02-close` |
| mapper | `05-postmortem.md`, `.dev-flow/BACKLOG.md` | ✅ committed — landing by PR | the close commit after `e56b774` on `docs/ui-next-02-close` |
| mapper (remote) | `origin/feat/ui-next-batch-02` | ✅ committed + landed (on the remote) | left untouched, pending operator decision M3 (`VERDICT-merge-2026-10-03.md:16`) |

- **Found before the batch:** not recorded — no record in this repo states that a tracked file was
  already modified when the batch began (`state.json` carries no `found:` entry for this batch).

**Conditional gate verdicts:** gates that closed as "once items 1–N land this is a PASS/MERGE", each
discharge verified by re-reading the artifact (not by trusting the corrective pass ran).

| Conditional item | Discharged? | Verified how |
|---|---|---|
| Adversarial PR QA `BLOCK-UNTIL PR-QA-F1` (home `j`/`k` crash with ≥1 map) | ✅ | `A-139` fixes PR-QA-F1 and `test_gate2.py::test_gate2_f1_no_other_call_site_uses_a_widget_method_that_does_not_exist` (`04-validation.md:121`); Gate-2 "fixes + review PASS, 2797/0" (`state.json` `MERGED_2026-10-03.gates.Gate-2`) |
| Whole-branch security `BRANCH-SEC-F3` (repo-local git config can run a program via `log.showSignature`) | ✅ | `M1` fixes it in Gate-2 (`VERDICT-merge-2026-10-03.md:14`); `test_gate2.py::test_gate2_sec3_every_git_call_pins_the_config_keys_that_can_run_a_program` (`04-validation.md:39`) |
| Gate-2 review `GATE2-REV-F1` (stale `edge of the map` hint, MEDIUM) | ✅ (deferred, not blocking) | operator ruling `M4` "Al backlog, mergear ya" → recorded as B-95 (`VERDICT-merge-2026-10-03.md:25`, `BACKLOG.md:199`) |

### Validator waivers at close (operator ruling 2026-10-08)

`devflow-validate.py --brief` at close reported blocks outside this close's own artifacts. The operator chose: waive the sealed-record blocks with this reason, fix the state ones, and land by PR.

| Rule | Where | Count | Disposition |
|---|---|---|---|
| `V59` (code row without a requirement trace) | `03-increments/increment-001.md` … `003.md` | 28 | **Waived.** The packets were sealed in August; the trace-to-requirement rule landed in flow rev96 (2026-09-25). Re-anchoring a closed record to a later rule is editing the past |
| `V56` (packet claims a run, cites no evidence file) | `increment-001.md`, `003.md`, `005.md` | 3 | **Waived**, same reason |
| `V53` (anchor names a symbol its file does not bind) | increments 002–004b, 022 | 10 | **Waived** — sealed records; the validator itself counts these as a census, not a reason to rewrite |
| `V1` (live placeholder) | `increment-004b.md:351` | 1 | **Waived** — sealed record |
| `V2` (AT with no node on disk) | `AT-033/034/035/041/042` | 5 | **Carried** as B-101 (with `AT-044` in B-100) |
| `V22` (split parent `LLR-N07.2.2` has no `Statement:`) | `01-requirements.md` (sealed) | 1 | **Waived** — the canon carries it as `split`; the sealed requirements block is not rewritten |
| `V22` (no requirements canon) | `state.json` | — | **Fixed**: `artifact_homes.requirements_canon = repo:REQUIREMENTS.md`, canon folded (91 rows; S07 rows marked superseded, N14 rows deferred; `LLR-COERCE.2` and the split parent `LLR-N07.2.2` added by hand after the fold refused them) |
| `V61` (ARQ gate never decided) | `state.json` `decisions_log` | 1 | **Fixed** with a RETROACTIVE entry dated by the ARQ artifact's commit (`8675151`, 2026-08-27) and labelled as written at close |

- **DDR was never held** as its own gate or artifact. The nearest evidence is the whole-branch Gate-1, Gate-2 and security sign-off before merge (`VERDICT-merge-2026-10-03.md`). Logged as such in `decisions_log`; a process gap, not discharged retroactively.
- **P4/P5/P6 were written after the merge**, from existing evidence, drafted by `deepseek-v4-pro` and corrected by the orchestrator and a `qa-reviewer` pass (which found an off-by-one citation shift along the Inc-9 chain in P4 and two untraced HLRs in P6, now B-100). Process finding: the closing artifacts should be written before merge, while the evidence is fresh.

### Evidence checklist — architect + qa-reviewer
> Drafted by `deepseek-v4-pro`; the `qa-reviewer` rows mirror the checklist the `qa-reviewer` agent evaluated in
> `04-validation.md` §Evidence checklist. No `architect` agent ran; the architect rows are drafted from the record and verified by the orchestrator. Each row is ✓/✗ with one-line evidence.

**qa-reviewer lens (from `04-validation.md` §Evidence checklist):**

| # | Item | ✓/✗ | Evidence |
|---|---|---|---|
| 1 | ONE complete run, launched by the orchestrator — never stitched | ✓ | `gate-run-master-tree.txt` — "2797 passed, 24 deselected, 3 xfailed … executed by the orchestrator … on the squash tree 46e190b" |
| 2 | Layer 0 unit · Layer A white-box · Layer B black-box | ✓ | `04-validation.md` §Layer 0 (mutation tables), §Layer A (35 amendment rows A-105…A-139), §Layer B (driven surface) |
| 3 | UX walkthrough with the real mechanism and the painted result | ✓ | `04-validation.md` §UX walkthrough — Textual pilot at each test file's declared widths, painted frame asserted |
| 4 | Representative + boundary + negative | ✓ | `04-validation.md` §Layer B repr·boundary·negative column |
| 5 | The deliverable actually observed | ✓ | `04-validation.md` §Bidirectional matrix output rows (`open_external`, on-disk save pair, `row-N` CSV) |
| 6 | Bidirectional surface-reachability matrix | ✓ | `04-validation.md` §Bidirectional matrix — 8 rows |
| 7 | A negative result names its over-breadth, and that over-breadth is guarded (C-55 limb 1) | ✓ | census arms carry a scanner self-check (`test_en1.py::test_scanner_sees_what_it_claims`) |
| 8 | Every probe that returned an absence carries its positive control (C-55 limb 2) | ✓ | e.g. `test_inc9n_f2_pin_a_name_that_only_looks_like_a_device_is_accepted` |
| 9 | Verdict `PASS` / `PASS-WITH-NOTES` / `FAIL` | ✓ | `PASS-WITH-NOTES` (clean one-complete-run gate; notes = open FLAKE-2 + deferred residuals) |
| 10 | No unfilled template (no angle-bracket placeholder as a live value) | ✓ | quoted prose only |
| 11 | Ledger reconciles | ✗ | not closed: 2797 is the passed count, collected not recorded, baseline 429 counts deselected nodes; D/A not recorded as a pair |
| 12 | No real PII / secrets; no account name spelled out | ✓ | operator referenced only as "the operator"; no `%USERPROFILE%` path spelled out |

**architect lens (from `00-checklists.md` §2 ARQ + §6 DDR, filled from the record):**

| # | Item | ✓/✗ | Evidence |
|---|---|---|---|
| 1 | Module map updated — or "no architecture change" with its empty diff | ⚠ | `docs/ARCHITECTURE.md` was never amended despite ARQ recorded approved — flagged by the orchestrator (`state.json` `decisions_log` 2026-08-27) |
| 2 | Every planned file falls under a declared module | ✓ | per-increment cuts name files under declared modules (`state.json` `p3_progress.closed` `scope`/`source_files`) |
| 3 | Interfaces that change, listed | ✓ | `IRenderer.render` A3 migration, frozen signature `render(graph, state)`, done in one increment (Inc-2, `state.json` `p3_progress.closed`) |
| 4 | Lanes proposed with disjoint FILE sets | ⚠ | two declared source-file breaches (Inc-2 6 files, Inc-3 6 files), both re-ratified, not hidden (`state.json:413,429`) |
| 5 | `rationale` per structural decision | ✓ | `cut_amendments` records measurement-based re-cuts (S-D, Inc-B55) with `reason_is_MEASUREMENT_not_preference` |
| 6 | Reverse census crossed between lanes | ✓ | Inc-2 "AST not grep: 7 definitions, 35 arg-ful call sites …" (`state.json` `p3_progress.closed` Inc-2) |

---

*Drafted by `deepseek/deepseek-v4-pro` (via `opencode run`) from existing evidence; verified and corrected by
the orchestrator (Claude Opus 5.5), which filled §0 at the close gate. Every number and verdict is cited to a repo file or the attached gate transcript; where the
record is silent the field says `not recorded`.*
