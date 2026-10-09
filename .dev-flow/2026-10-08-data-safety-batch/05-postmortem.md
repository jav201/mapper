# Post-mortem — mapper — Batch `2026-10-08-data-safety-batch`

> Phase 5 artifact. Drafted by two small Kimi units (P5a core, P5b open items / reconciliation / conditional verdicts; `kimi-code/kimi-for-coding`) from the batch's own records; assembled and fact-checked by the orchestrator (Claude Opus 5.5). The `architect` and `qa-reviewer` co-author roles are discharged at the final PR-level `qa-reviewer` pass, which reads this record.

## 0 · Gate record — which tree this close gated

| Field | Value |
|---|---|
| Gate record | pending — filled by the orchestrator at the close gate |
| Gated tree | pending — filled by the orchestrator at the close gate |

## 🔑 At a glance (read first)

- **Outcome:** closed with carry-over — P4 `PASS-WITH-NOTES` (gate `2920 passed / 0 failed / 3 xfailed` on `cab8181`, `.dev-flow/2026-10-08-data-safety-batch/04-validation.md:9`); batch closed at P6 after the final PR-level qa-reviewer pass (MERGE).dev-flow/state.json:68-69`). P1 needed 3 iterations (soft cap).
- **Top 3:** ① prototype-first US-001 (operator verdict C) gave the batch a validated design before requirements — zero design churn after P0 (`.dev-flow/2026-10-08-data-safety-batch/VERDICT-b36-prototype-2026-10-08.md:5-9`). ② the round-2 save-failure disposition (disk-hash classification) was itself unsound and cost an extra full P1/P2 cycle (`.dev-flow/2026-10-08-data-safety-batch/02-review.md:93`). ③ root cause of the cap: failure-case semantics over-specified against an incompletely understood store (`.dev-flow/2026-10-08-data-safety-batch/02-review.md:90-98`).
- **New control this batch:** none named in the artifacts; nearest candidate is the mutation-battery driver running `python -u` after an interrupted battery left a mutant applied (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-003.md:270`).
- **Open items → next batch:** 3 accepted residuals (A-13 typed-ahead `d`, A-14 saved-but-raised, A-15 double index failure) + F5 + external V7 (`.dev-flow/2026-10-08-data-safety-batch/04-validation.md:261-265`) — biggest: A-15 (disk/edit divergence after a double `_reindex` failure).
- **Metrics:** iterations `3` (all at P1) · findings `closed ≈ opened` (all rounds discharged by P2 round 4) · ledger `2800 → 2923`.

---

## Detail (reference)

### What worked
- Prototype round before requirements: four B-36 variants mounted in the real app, operator picked C (draft + explicit save); measured stray-key safety; rulings R1–R9 pre-decided the open points (`.dev-flow/2026-10-08-data-safety-batch/VERDICT-b36-prototype-2026-10-08.md:3-24`).
- FLAKE-2 spike refuted the intake hypothesis (horizontal reflow) and traced the real mechanism — `scroll_to` defers via `call_after_refresh`, so the setup lands inside the next key's measurement window under load; fix is 2 lines, test-side (`spike/FLAKE-2-spike.md:16-35`).
- Small-unit implementation: Inc-1c/Inc-2 as eleven units, each one change + one test + its own RED proof, orchestrator-verified before chaining (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-005.md:9`).
- Security lens caught real defects early: SEC-M1 (failed-save disk/memory divergence) and SEC-M2 (ESC through `markup=False`) at P2 round 1 (`.dev-flow/2026-10-08-data-safety-batch/02-review.md:27-28`).
- The DDR architect lens re-read the PDR discharge log and caught C14 marked discharged while three boundary arms were missing — the arms were then realised with executed REDs (`.dev-flow/2026-10-08-data-safety-batch/01-requirements-ledger.md:485-489`).
- Every executed result names its executor (orchestrator / units / `human:Javier` for the C14 smoke) (`.dev-flow/2026-10-08-data-safety-batch/04-validation.md:278`).

### What didn't / friction
- P1 consumed all 3 iterations; the soft cap was reached and the operator had to rule (`Simplificar y seguir`, then `Aplicar y verificar ligero`) to converge (`.dev-flow/state.json:181-193`).
- Round-2's disk-hash classification of failed saves was unsound in four ways (identical-bytes rewrite reads as torn; external edit reads as committed; `_pop_snapshot` writes; reload fallback can lock structural writes) — a full requirement rewrite at round 3 (`.dev-flow/2026-10-08-data-safety-batch/02-review.md:93-98`).
- Three DeepSeek runs produced no output and were killed (1 h at P1 iteration 2 — its rerun succeeded; 40 min at P1 iteration 3 — applied by the orchestrator instead; 9 min at the DDR AT-025b unit — re-run on Kimi) (`.dev-flow/state.json:177-188`, `.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-006.md:9`).
- The interrupted Inc-1b mutation battery left mutant `A-prefix-always` applied to `mapper/app.py` (killed before its `finally` restore; block-buffered transcript); found only because the driver printed `BAD` (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-003.md:270`).
- Inc-1b default-lane run 1 failed on a static census false positive (`focus` callback read as self-recursion); needed a rename + full re-run (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-003.md:80`).

### Scope drift (planned vs actual)
| Planned | Actual | Note |
|---------|--------|------|
| B-36 (draft model + explicit save) | Delivered (Inc-1a/1b/1c, Inc-2, Inc-3) | `state.json:5` objective; landed on `feat/data-safety-batch` (`state.json:202`) |
| B-100/B-101 acceptance tests | DONE, reconciled on disk | commit `3d3e999`; AT-033/034/035 retired to deferred US-N14 — the B-101 attribution was the orchestrator's own error at the prior close (`.dev-flow/2026-10-08-data-safety-batch/PLAN.md:79`) |
| B-98 legend-paint flake | Fixed test-side at four `scroll_to` sites + regression arms | `PLAN.md` decision row (`US-004 READY with a test-side fix at four scroll_to sites`); commit `c5c4d62` |
| HLR-004 as drafted | Widened: LLR-004.4 states focus mode writes the whole map; TC-004.4 planned in the design proposal | PDR probe found a present data-loss path (inspector edit under focus writes only the focused subtree as the whole map); accepted under HLR-004 (`.dev-flow/2026-10-08-data-safety-batch/01-requirements-ledger.md:417-422`) |
| Eleven units U1–U10 + Z2 | U11 added at the §4b review (+2 test nodes) | `.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-005.md:216` (via `04-validation.md:216`) |
| `test_en2.py` Z2 arms as written | Rescoped (intent kept) | `.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-005.md:85` |

### Metrics (full)
| Metric | Value |
|--------|-------|
| Iterations per station | `{P0:0,P1:3,P2:0,P3:0,P4:0,P5:0,P6:0,ARQ:0,DDR:0,PDR:0}` (`.dev-flow/state.json:82-93`) |
| Findings opened / closed | Round 1: 28 opened (4 blocker · 10 major · 14 minor, `.dev-flow/2026-10-08-data-safety-batch/02-review.md:9`); round 2: 19 (0/6/13, `:74`); rounds 3–4: majors countable (3 + 2), minors grouped per row — per-finding counts **not recorded** (grouped `minors` disposition rows, `:98-101`, `:107-109`). Closed: all rounds discharged — round-2 ids 12/12 + 3/3 + all qa (`:73`), round-4 fixes confirmed by one reviewer (`:108`); P2 approved at round 4 (`.dev-flow/state.json:193`) |
| Findings by severity (blocker/major/minor) | Round 1 `4/10/14`; round 2 `0/6/13`; rounds 3–4 minors not individually countable — see above (`.dev-flow/2026-10-08-data-safety-batch/02-review.md:9,74,98,107`) |
| Where caught (P2 / P3 gate / P4) | `28+` / 0 / 0 (all requirement-phase findings at P2's four rounds; P3 closed on lane evidence + independent reviews, `.dev-flow/state.json:202`) |
| Test ledger (base − D + A = post) | `2800 + 123 = 2923` (2800 at batch start → 2923 at gate = 2920 passed + 3 xfailed, `.dev-flow/2026-10-08-data-safety-batch/04-validation.md:15`) |
| Files touched · increments (cap trips) | `28` files, `3082 insertions(+), 221 deletions(-)` (`git diff --stat 07dd930..HEAD -- mapper/ tests/ | tail -1`) · `6` packets (`03-increments/increment-001..006.md`) · `1` cap trip (P1 soft cap at iteration 3, `.dev-flow/state.json:183`) |

### Root causes (only if a phase took ≥2 iterations)
- P1 iteration 2 trigger → root cause: the round-2 disposition it implemented (classify failed saves by sha256 of the on-disk pair) was unsound against the real store in four named ways; round 3 replaced the three-case table with ONE rule (reload from disk, keep draft re-diffed, undo untouched, no writes from failure handling) (`.dev-flow/2026-10-08-data-safety-batch/02-review.md:93-98`).
- Contributing: the defect class (save-failure semantics) was specified before the store's real failure surface was understood — the review kept finding new mechanism-level holes (SEC-N-A/B/C/D, ARCH-R3-1/2/3/4), so convergence came from simplification under operator ruling, not from iterated refinement of the complex rule (`.dev-flow/2026-10-08-data-safety-batch/02-review.md:90-94`).

### Process / workflow findings
- Long single-shot DeepSeek runs hang with no output (three kills this batch: 1 h, 40 min, 9 min). Splitting the same work into small units with a 15-min watchdog fixed it — operator method ruling 2026-10-08: "partir el trabajo de deepseek en partes más pequeñas" (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-005.md:9`; hangs at `.dev-flow/state.json:177-188`, `.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-006.md:9`).
- Kimi CLI as the small-unit runner: five units launched as `kimi -m kimi-code/kimi-for-coding -p`, one per worktree, in parallel; one DeepSeek unit that produced no output for 9 min was re-run on Kimi with the same plan (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-006.md:9`). Any further flag-level lessons (beyond `-m` model + `-p` print) are **not recorded** in the batch artifacts.
- Attribution error by the flow runner: the prior batch's close attributed AT-033/034/035 to US-N13; the canonical record assigns them to US-N14 (deferred), so they were retired here — "the B-101 attribution was the orchestrator's own error at close" (`.dev-flow/2026-10-08-data-safety-batch/PLAN.md:79`; settled at P0, `.dev-flow/2026-10-08-data-safety-batch/01-requirements.md:108`).
- A mutation battery killed mid-run can leave the tree mutated and its transcript truncated (block buffering); detection came from the driver's own `BAD` anchor check. Workflow change applied: driver runs `python -u`, and survivors of interrupted runs are re-run and re-killed before counting (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-003.md:156,270`).
- Operator rulings at the cap (`Simplificar y seguir`, `Aplicar y verificar ligero`) converged the phase faster than another full review round would have — but the light verification traded per-lens review depth for speed, leaving A-14/A-15 as recorded residuals (`.dev-flow/state.json:183-193`).

### Product findings
- Focus-mode data loss found at PDR: an inspector edit under focus mode writes only the focused subtree as the whole map (probe on the real tree: on-disk nodes after the edit `['a']`). Accepted under HLR-004 as "save writes the whole map"; planned node TC-004.4 (`.dev-flow/2026-10-08-data-safety-batch/01-requirements-ledger.md:417-422`; ``MapScreen._save_draft` (`mapper/app.py:3524`) and ledger `.59``).
- Z2 hint-borrow interference: leaving a field re-announced an attachment chip's `open attachment`, because the chip swap works inside the resting hint the U2 field hint had replaced; U2's borrow and the chip's borrow now coordinate through the screen's blur handler, with a hand-back rule for future borrowers (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-005.md:18,80`; fix commit `5ad158e`).
- The interrupted Inc-1b battery left mutant `A-prefix-always` applied to `mapper/app.py` while the visible-card assertion still passed — a passing test over a mutated product; restored byte-identically (digest match) and closed with a new visible-card arm (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-003.md:270`).
- Save-failure handling: the shipped model is one rule (reload from disk = truth, keep draft re-diffed, undo stack untouched, reload-failure restores in memory with a refusal to write); residual A-14 (edit on disk with no undo step) and A-15 (double `_reindex` failure leaves disk ahead of memory) accepted and recorded (`.dev-flow/2026-10-08-data-safety-batch/02-review.md:98`; `.dev-flow/2026-10-08-data-safety-batch/04-validation.md:262-263`).

### Control lineage
- **New control proposed this batch:** none adopted by name in the artifacts. Candidate from the interrupted-battery incident: mutation drivers must run unbuffered (`python -u`) and every interrupted battery's survivors re-run before counting (`.dev-flow/2026-10-08-data-safety-batch/03-increments/increment-003.md:270`) — status: propose.
- **Prior controls exercised:**
  - C-18 (one on-disk node per acceptance id): enforced at Inc-4 reconciliation — every declared AT resolves to a named node or a recorded retirement; AT-025b joined into one node (`.dev-flow/2026-10-08-data-safety-batch/01-requirements-ledger.md:455-460,477-482`).
  - C-25 (single orchestrator-owned gate run): the one complete gate run was launched and collected by the orchestrator; fragments drafted separately (`.dev-flow/2026-10-08-data-safety-batch/04-validation.md:5`).
  - C-26 reverse census: architect table at P2 round 1; `FieldCommitted` removal confirmed with 0 hits (`.dev-flow/2026-10-08-data-safety-batch/02-review.md:12`; `.dev-flow/2026-10-08-data-safety-batch/04-validation.md:14`).
  - A-110 (no operator paths in tracked files): `state.json` `owner` omitted by design (`.dev-flow/state.json:6`).
  - RED proof with sha256 restore: per-unit and per-mutant batteries; totals 105 mutants run · 92 killed · 0 BAD (`.dev-flow/2026-10-08-data-safety-batch/04-validation.md:210-219`).
  - Stress-tested: the PDR discharge log — DDR re-read it and caught C14 marked discharged while arms were missing (`.dev-flow/2026-10-08-data-safety-batch/01-requirements-ledger.md:485-489`).

> Drafted by unit P5b (Kimi, kimi-code/kimi-for-coding) for postmortem assembly. All facts re-read from the batch's artifacts; `not recorded` where absent. Sources: `.dev-flow/state.json`, `.dev-flow/2026-10-08-data-safety-batch/` (01-requirements.md, 02-review.md, 03-increments/increment-001..006.md + inc4-reconciliation-proposal.md, 04-validation.md, design/PDR + DDR, VERDICT-b36-prototype-2026-10-08.md, 00-checklists.md), `.dev-flow/BACKLOG.md`, `git status --short`, `git worktree list`, `git log --oneline 07dd930..HEAD`.

## Open / deferred items → next batch

| Item | Type (process/product) | Reason deferred | Trigger / owner |
|------|------------------------|-----------------|-----------------|
| **A-13** — a typed-ahead `d` while the guard is up discards the draft (`01-requirements.md:740`: "loses a draft but never writes … recorded, not mitigated") | product | Accepted residual under the operator's P1-cap ruling; never writes, so no data-safety impact | BACKLOG B-102 (`.dev-flow/BACKLOG.md:212`) — "revisit only if observed" |
| **A-14** — a save whose files reached disk but whose store call raised leaves no undo step (`01-requirements.md:741`) | product | Accepted under the operator's ruling (failure handling never pushes or writes); recorded, not mitigated | BACKLOG B-102 (`.dev-flow/BACKLOG.md:212`) — "revisit only if observed" |
| **A-15** — a double `_reindex` failure restores the pre-save graph in memory while disk holds the edit (`01-requirements.md:742`; error toast tells the operator to leave and reopen) | product | Accepted as a residual of a double index failure; recorded, not mitigated | BACKLOG B-102 (`.dev-flow/BACKLOG.md:212`) — "revisit only if observed" |
| **F5 (LOW)** — `toast=False` also suppresses `_refusal_toast`'s authored `MapIdError` text on a draft save; unreachable on an already-open map (`03-increments/increment-005.md:98`: "noted, not changed") | product | Unreachable in practice; rolled into a hygiene batch with two sibling LOWs (`_last_save_error` untyped, `action_quit` reading a private flag) | BACKLOG B-103 (`.dev-flow/BACKLOG.md:213`) — "small refactor batch" |
| **V7 (external)** — validator V7 flags the installed flow bundle's `SKILL.md` as differing from its own manifest (modified 2026-10-09 07:24 by the flow's own rev101 work in another session) | process (not this project's tree) | "Recorded, not acted on: the flow installation is not this project's tree" (`design/DDR-2026-10-08-data-safety-batch.md:93`; echoed `03-increments/increment-006.md:65-66`) | Flow maintainers / other session; no BACKLOG row exists (grep of `.dev-flow/BACKLOG.md` — not recorded) |

Packet `Pending` sections (§6 of each increment) hold no other live carries: increment-001:209 and increment-002:209 items were resolved in-flight (Inc-3 fix for `test_at_p07` on the branch's base, I-2 deviation amended by the orchestrator); increment-003:268's C14 smoke and UX-1 were discharged during P3/PDR; increment-004:62's V2 validator residue is a record-keeping note; increment-005:83's C14 smoke was discharged by the operator's real-terminal run (see verdicts below). `inc4-reconciliation-proposal.md` records no open items of its own (status PROPOSAL, all actions executed; AT-033/034/035 RETIRED with US-N14 `#D23`, lines 14-16, 71).

## Working-file reconciliation (C-44)

Commands run (read-only) from the worktree root:

- `git status --short` → ` M .dev-flow/BACKLOG.md` — the only tracked modification in the primary checkout. Verified as **this batch's own close edit**: the diff adds the "Last refresh 2026-10-09" line and rows B-102/B-103, which exist only in the worktree, not in `HEAD` (`git show HEAD:.dev-flow/BACKLOG.md` has no B-102/B-103). Must land in the orchestrator's close commit.
- `git worktree list` → 19 worktrees; 18 under `%TEMP%`. Of those, 17 are this batch's (see table); `%TEMP%\mapper-ds-p4` is a leftover from the **previous** batch's P6 vault sync — it holds branch `docs/ui-next-02-synced`, whose tip 5762947 ("batch ui-next-02 synced to the Obsidian vault") sits on bb8328f (PR #8 merge, already in `previous_batch` at `.dev-flow/state.json:228-237`). Flagged FOUND, not this batch's work.
- `git log --oneline 07dd930..HEAD` → 68 commits at the close (60 first-parent), all landed on `feat/data-safety-batch`. No unpushed-dependency check failed: the branch carries the whole increment/DDR/PDR/P4 chain.

| Repo | File(s) | Terminal state | Landing / backlog ref |
|------|---------|----------------|-----------------------|
| mapper (primary worktree) | `.dev-flow/BACKLOG.md` | ✅ committed + landed | `de40d6e` (B-36/B-98 DONE, B-102/B-103 added, refresh line) |
| mapper (temp worktrees) | — | 🗑️ cleanup candidates — worktrees removable after close | `git worktree remove` for each batch worktree below |
| flow bundle (external) | `SKILL.md` vs manifest drift | 📋 recorded external (V7) | `design/DDR-2026-10-08-data-safety-batch.md:93` |

Batch worktrees to clean up (rendered as `%TEMP%\<name>`, branch in brackets):

- `%TEMP%\mapper-ds-p0` [ds/p0-intake] — P0 intake (deepseek-v4-pro)
- `%TEMP%\mapper-arq` [arq/data-safety] — ARQ
- `%TEMP%\mapper-p1` [ds/p1-requirements] — P1 requirements (deepseek-v4-pro)
- `%TEMP%\mapper-pdr` [pdr/data-safety] — PDR
- `%TEMP%\mapper-proto-b36` [proto/b36-save-affordance] — B-36 prototype
- `%TEMP%\mapper-spike-flake2` [spike/flake2] — B-98 flake spike
- `%TEMP%\mapper-inc1a` [inc1a/draft-guard] — Inc-1a
- `%TEMP%\mapper-inc1b` [inc1b/draft-save] — Inc-1b / Inc-4
- `%TEMP%\mapper-inc2` [inc2/exits] — Inc-1c / Inc-2
- `%TEMP%\mapper-inc3` [inc3/flake2] — Inc-3
- `%TEMP%\mapper-inc4` [inc4/at-reconcile] — Inc-4 reconciliation
- `%TEMP%\mapper-k1` … `%TEMP%\mapper-k5` [ddr/k1…k5] — DDR Kimi units K1–K5
- `%TEMP%\mapper-ddr` [ddr/fixes] — DDR integration
- `%TEMP%\mapper-ds-p4` [docs/ui-next-02-synced] — **FOUND, previous batch's sync leftover**; verify nothing unpushed before removing (remote `origin/docs/ui-next-02-synced` exists)

- **Found before the batch:** none observed — the only tracked modification in the primary checkout is this batch's own BACKLOG.md close edit above; the close-checklist C-44 row at `00-checklists.md:127` was left blank by the batch (disposition not recorded there).

## Conditional gate verdicts

Re-read from the artifacts, not from the corrective pass's claim.

| Conditional item | Discharged? | Verified how |
|---|---|---|
| PDR C1 — ctrl+q under an open node guard must not wedge `_quit_walk_open` (architect MAJOR-1) | ✅ | `design/PDR-2026-10-08-data-safety-batch.md:107`; `03-increments/increment-005.md:23,56,81` (U7, mutant killed) |
| PDR C2 — `_repoint(target)` defined and listed in I-4 | ✅ | `design/PDR-…:108`; `03-increments/increment-003.md:283` (A-stay-repoints KILLED) |
| PDR C3 — row 1b.9 names the cursor `on_mount` passes to `_establish_graph` | ✅ | `design/PDR-…:108`; `03-increments/increment-003.md:284` |
| PDR C4 — AT-009 wording, US-001 summary, I-3 seat count 75 | ✅ at seal | `design/PDR-…:89,109`; `.dev-flow/state.json:198` |
| PDR C5 — R-5 records `f` with a draft opens the guard | ✅ at seal | `design/PDR-…:90,109`; `.dev-flow/state.json:198` |
| PDR C6 — hint line prefixes `● unsaved (N) · ctrl+s save` in ALERT while inspector hidden (operator R8) | ✅ | `design/PDR-…:110`; `03-increments/increment-003.md:285,181` (4 prefix mutants KILLED; colour == `darkside.ALERT` at 87/118/140); Inc-1c repair `increment-003.md:325` → `increment-005.md:6` |
| PDR C7 — after ctrl+s inside a field, focus returns to that field | ✅ | `design/PDR-…:111`; `03-increments/increment-003.md:286,144` (A-no-refocus KILLED, re-run on final tree) |
| PDR C8 — reload-failure toast states the cost | ✅ | `design/PDR-…:112`; `03-increments/increment-003.md:287` (A-reload-toast KILLED); records aligned at DDR D2 (`design/DDR-…:87`) |
| PDR C9 — guard title `unsaved draft on «{title}» · {map_id}` (R9) | ✅ | `design/PDR-…:113`; `03-increments/increment-002.md:217` |
| PDR C10 — enablers named with owners (AT-011 link, AT-014c/d, AT-013 two-screen helper) | ✅ | `design/PDR-…:114`; `03-increments/increment-003.md:288` |
| PDR C11 — E-6 save-path denylist; oracle = save count + hash pair | ✅ | `design/PDR-…:115`; `03-increments/increment-003.md:289` |
| PDR C12 — US-004 delayed-scroll arms or declared survivors | ✅ | `design/PDR-…:116`; `03-increments/increment-001.md:111` |
| PDR C13 — AT-015 executed RED with `plain()` dropped; oracle reads the Static's source | ✅ | `design/PDR-…:117`; `03-increments/increment-002.md:87,217`; `increment-003.md:290` |
| PDR C14 — LLR boundary arms, E-2 third mode, AT-012 RED, at_014a..d, AT-042 HelpScreen mutation, censuses, real-terminal smoke | ✅ **corrected at DDR** — first discharge claim was false; DDR architect lens caught three missing arms | `design/PDR-…:118` (corrected row); `design/DDR-…:38,86` (found NOT discharged, ledger `.68`); arms on disk `03-increments/increment-006.md:12`; operator smoke attributed `human:Javier` 2026-10-09 — "Todod funcionó, continuemos." — `04-validation.md:18,253` |
| DDR D1 — C14's three boundary arms (esc+live search, same-map link, archive own node) | ✅ | `design/DDR-…:86`; tests `test_ddr_esc_search.py`, `test_ddr_same_map_link.py`, `test_ddr_archive_own.py` (RED each, `03-increments/increment-006.md:12`) |
| DDR D2 — records aligned with code (C8 toast text, R8 ALERT, AT-044 `priority=True`) | ✅ | `design/DDR-…:87`; `03-increments/increment-006.md:15` |
| DDR D3 — `docs/ARCHITECTURE.md` describes the shipped code | ✅ | `design/DDR-…:88` |
| DDR D4 — AT-042 / AT-025b one node each | ✅ | `design/DDR-…:89`; joined node at `tests/test_repair_cycles.py:760` per `04-validation.md:143` |
| DDR D5 — operator real-terminal smoke attributed | ✅ | `design/DDR-…:90`; `04-validation.md:18` |
| DDR QA-3 — TC-009.1 missing; `I-remount-per-key` unproven | ✅ | `design/DDR-…:91`; `04-validation.md:87,217` |
| P2 round 1 — 4 blockers (ARCH-B1, ARCH-B2/QA-B2, QA-B1 + security SEC-M1/M2) + 10 majors, iterate-to-refine | ✅ all applied | `02-review.md:22-48` (findings), `:73` (round-2 header: architect 12/12, security 3/3, qa all discharged) |
| P2 round 2 — 6 majors | ⚠️ 5/6 — R2-N1 (disk-hash failure classification) **NOT discharged**, proven unsound at round 3 | `02-review.md:71-86` (findings), `:92-93` (discharge + root cause SEC-N-A/B/C/D) |
| P2 round 3 — operator ruling "Simplificar y seguir": one failed-save rule (reload from disk, keep draft re-diffed, no writes from failure handling) | ✅ applied; discharged at round 4 | `02-review.md:90-101` (R3-SAVE `:98`); `.dev-flow/state.json:183-188` |
| P2 round 4 — 0 blockers; operator ruling "Aplicar y verificar ligero": orchestrator applies, one reviewer confirms | ✅ applied (ledger `.58`, `02-review.md:109`); residuals A-14/A-15 recorded | `02-review.md:105-109`; `04-validation.md:262-263` (gaps table), `:75` (LLR-004.2 nodes green on cab8181) |
| P4 qa-reviewer ACCEPT-WITH-FIXES — 4 minors applied | ✅ applied — **individual texts not recorded** in any artifact; only the count survives | `04-validation.md:16` (0 blocker / 0 major / 4 minor, "8 of 8 rows ✓"), `:267`; applied edits visible as commit a513190's diff to `04-validation.md:3,16,59,203,267,277`. Caveat: §5 tally still reads "11 of 11 rows ✓" at `04-validation.md:283` — internal inconsistency left by the fix pass |

## Evidence checklist — architect + qa-reviewer

> Drafted by this unit (P5b) from the re-read evidence above; to be confirmed/ countersigned by the architect and qa-reviewer co-authors at assembly.

| # | Check | ✓/✗ | Evidence |
|---|-------|-----|----------|
| 1 | Gate record: validator run, exit 0, date | ✓ | `04-validation.md:9,38-40` — 2920 passed / 24 deselected / 3 xfailed / EXIT_CODE=0, single orchestrator run on cab8181; hash-verified transcript `04-validation.md:291` |
| 2 | Gated tree clean at P4 | ✓ | `04-validation.md:9` names cab8181; ledger reconciliation 2923 = 2920+3 at `04-validation.md:227,239` |
| 3 | PDR C1–C14 each discharged, verified by re-read | ✓ | table above; C14's false first claim caught by the DDR re-read (`design/DDR-…:38`) |
| 4 | DDR D1–D5 + QA-3 discharged | ✓ | `design/DDR-…:84-91`; `03-increments/increment-006.md:12,15` |
| 5 | P2 round dispositions traced to dispositions in 02-review.md | ✓ | `02-review.md:73,92-93,109`; round-3 operator ruling `02-review.md:94` |
| 6 | P4 qa minors applied | ✓ (with caveat) | commit a513190 diff; `04-validation.md:16,267`; texts not recorded — flag for next batch's record-keeping |
| 7 | Residuals A-13/A-14/A-15 carried to BACKLOG, not lost | ✓ | `.dev-flow/BACKLOG.md:212` (B-102); definitions `01-requirements.md:740-742` |
| 8 | F5 + sibling LOWs carried to BACKLOG | ✓ | `.dev-flow/BACKLOG.md:213` (B-103); `03-increments/increment-005.md:98` |
| 9 | External V7 recorded as not-this-project's | ✓ | `design/DDR-…:93`; `03-increments/increment-006.md:65-66`; no BACKLOG row (recorded here as a gap) |
| 10 | C-44 sweep run from the tree, not memory | ✓ | `git status --short` + `git worktree list` above; 17 batch worktrees + 1 FOUND leftover (`%TEMP%\mapper-ds-p4`); only modification is the batch's own uncommitted BACKLOG.md close edit |
