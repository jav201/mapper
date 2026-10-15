# PLAN — mapper — Batch 2026-10-11-fixes-batch

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
| Batch | 2026-10-11-fixes-batch |
| Objective | Bug fixes: B-115 (`slugify("")` → `"n"`; empty parent cell slugified on CSV import), B-116 (CSV listing a child before its root refused as a cycle), B-117 (a forest map's root changes on reload), B-127 (roles screen runs git discovery + identity reads on the UI thread at mount) |
| Standing authorization | NOT ASKED. This batch opens on a worker unit (FIXES-P0) whose commission covers the P0 intake only; the runtime cannot prompt mid-unit. Per the flow's stated default the operator approves every gate and merges the PR — the two kickoff questions (autonomy + merge authority; decision-recording acknowledgement) are owed at the P0 gate before any implementation. The previous batch's standing authorization is never carried (§Batch-kickoff authorization). |
| First gate | `devflow-validate.py --brief` after the rollover: exit 1 · `3 block · 532 notice · 46 not applicable` — all 3 blocks are environment (`V7` flow-bundle revision, `V16` ×2 `~/.claude` uncommitted), none names this batch; the new batch id appears in no finding. Full readback: `spike/intake.md` §Validator. |
| Premises / RC-1 | RC-1 (a): `git fetch origin` NOT run — this unit forbids network; premise recorded instead: local `master` = `5a991c683bc9abd2769f9c60b9e812ed8047c7ca`, tracking `origin/master` with no ahead/behind at unit start, so the local tip is the base. RC-2: `git ls-remote` probe NOT run (no network) — recorded as a configuration fact per the no-network premise. `base_ref` = `5a991c6…db85` (40-hex `git rev-parse HEAD` at rollover). |

## Triggers

The trigger evaluation `state.json`'s `triggers.record` points at: one row per trigger evaluated, fired or not.

Evaluated 2026-10-15 (the P0 evaluation, run late, after P1/P2; no product code exists yet: `git diff --stat 5a991c6 -- mapper` is empty). Conditions: `stations/shared-controls.md` §Trigger evaluation. "judged" is the legal form where no probe exists.

| id | probe | output / judgement | fired? | turns on |
|---|---|---|---|---|
| A1 | judged — read `docs/ARCHITECTURE.md` §2 module rows and the PLAN increments · no module is created, no boundary moves; every touched file sits under a declared module (`mermaid`, `import_csv`, `store`, `screens`) | not fired | no | n/a |
| A2 | judged — module-map paths vs planned source files · inc 001 = `mapper/mermaid.py` (`mermaid`) + `mapper/import_csv.py` (`import_csv`); inc 002 = `mermaid` + `mapper/store.py` (`store`, docstring only) | ≥2 modules in one increment | **yes** | ARQ (with it PDR, DDR) |
| A3 | judged — `ARCHITECTURE.md` row `mermaid` EXPOSES `slugify(s) -> str` and `dump`; `slugify("")` changes `"n"` → `""` and `dump` changes its line order; consumers: `import_csv`, `screens/map/editing.py` (keeps its own `or "n"`), `store` | an exposed contract changes behaviour for consumers | **yes** | ARQ (with it PDR, DDR) |
| A4 | judged — PLAN §Roadmap: 001 and 002 both touch `mermaid` (module intersection non-empty); plan is serial 001→004 | not fired | no | n/a |
| B1 | `grep -rl slugify tests/` → `test_csv_safety_store.py`, `test_mermaid.py`; `grep -rl preview_csv tests/` → 8 files (`test_csv_safety_preview`, `test_gate2`, `test_import_csv`, `test_inc9c`, `test_inc9n`, `test_mod_compat`, `test_repair_cycles`, `test_repair_fields`); `grep -rl 'dump(' tests/` → 17 files; `_open_roles` → `test_roles_screen.py` | touched symbols are asserted by other batches' tests (csv-safety, perf, repair, reqharness); the pins that move are already listed in §6.3 and PLAN | **yes** | reverse census (C-26), re-validated at the P2/P3 supersession census; no station |
| B2 | `git diff --name-status --diff-filter=RD 5a991c6 -- mapper tests` → empty; requirements/PLAN name no file move | no file moves | no | n/a |
| B3 | `ls tests/goldens/perf` → `dump/*.mmd` (8 dump goldens), `render/`, `at076_saved_wide6000_after_add_child.mmd`; `tests/perf_goldens_capture.py` captures `mermaid.dump` bytes; literal `grep -rl mermaid tests/goldens` → empty (goldens are data) | `dump` (inc 002) is captured byte-identically; §6.3 states no golden changes (8/8 + AT-076) | **yes** | golden drift named in the census (C-24) |
| B4 | `grep -rln 'slugify\|mermaid.parse\|import_csv' mapper` → `import_csv`, `keymap`, `mermaid`, `model`, `store`, `screens/home`, `screens/import_preview`, `screens/map/editing`, `widgets/rail` | `dump` writes `.mmd` that `parse`/`store.load` read; `preview_csv` returns a `Graph` the import preview and `store.save` consume | **yes** | output-then-consume AT (C-12) — AT-086 (dump → parse) and AT-084/085 (import → save) already exist |
| C (scan) | `python scripts/devflow-scan-spec.py .dev-flow/2026-10-11-fixes-batch/01-requirements.md` → all 5 control rows ok (positive, negative, placeholder, placeholder-unbracketed, authored-in-brackets); `flags: session, form`; exit 1, `security_required: true` | per-id rows below | C1, C6 | see below |
| C1 | scan flag `session` (Auth / identity) | the hit is "disk changed mid-session" in a boundary catalog: ordinary vocabulary, declared and not reworded (C-53) | **yes** | security questions in §6.3 (answered); review judgment, item 4 below |
| C2 | scan: no Secrets / config flag | not fired | no | n/a |
| C3 | scan: no External-integration flag; judged — the roles worker runs the same allow-listed read-only `git` calls, `identity.py` untouched | not fired | no | n/a |
| C4 | scan: no Sensitive-data flag; judged — the `user.email` read already exists, stored only as `email_sha256` | not fired | no | n/a |
| C5 | scan: no Destructive-DB flag | not fired | no | n/a |
| C6 | scan flag `form` ("rows that form a genuine cycle", "the form the orphan pass uses") — a textual false positive; judged — the CSV import is nonetheless an input surface and B-115/B-116 change how its cells are read | declared (C-53) | **yes** | security questions in §6.3 (answered); review judgment, item 4 below |
| C7 | scan: no Network / exposure flag | not fired | no | n/a |
| C8 | `grep -n -i -E "markup\|ansi\|rich\|escape\|html" 01-requirements.md` → empty; judged — no new rendering of file-derived text; import-preview and roles painting paths are unchanged | not fired | no | n/a |
| D1 | judged — read `spike/intake.md` §B-115/§B-127 and LLR-FX.1.* / FX.4.* · B-127 is non-visual by ruling, but B-115 removes the `? ` park prefix on top-level rows and changes the ids shown (`row-N`), and B-127 changes when the roles matrix first paints (blank until the worker returns, keys inert) | the change alters what the user sees | **yes** | `ux-reviewer` at PDR; walkthrough at validation |
| D2 | judged — no prototype was built for this batch (only throwaway repro scripts in `spike/intake.md`) | not fired | no | n/a |
| E1 | `grep -o "US-FX-00[0-9]" 01-requirements.md \| sort -u` → US-FX-001…006 (6 stories); PLAN lists 4 increments | ≥3 stories and ≥3 increments | **yes** | size/risk rigour: per-increment census, test ledger summed across increments |
| E2 | judged — PLAN §Risks read; no high risk declared at intake (the pin moves are certain but mitigated inside their increments) | not fired | no | n/a |
| E3 | judged — internal TUI tool; no client deliverable, no regulated context | not fired | no | n/a |
| F1 | `devflow-validate.py .` → `V7 … bundle identical to the manifest it ships, BOTH DIRECTIONS … at 2026-10-12-rev102`; `flow_hash` is not recomputable from a bundle (the intake's V7 mismatch is gone) | not fired | no | n/a |
| F2 | `git log -- .dev-flow/BACKLOG.md` → last refresh `4c3ae66` (2026-10-11), after P6 approval `d9a32d3` and before the close sync `5a991c6`; rows B-115…B-127 present | backlog refreshed since the last close | no | n/a |

**fired:** A2, A3, B1, B3, B4, C1, C6, D1, E1
**not fired:** A1, A4, B2, C2, C3, C4, C5, C7, C8, D2, E2, E3, F1, F2

### What the fired triggers owe in this `core` batch, now that P1/P2 already ran

Proportionate retroactive actions; nothing reopens the requirements, and P3 stays blocked until 1–3 are done.

1. **ARQ (A2, A3)** — `stations_active` gains ARQ, PDR, DDR (V61 refuses a fired trigger whose station is missing), each with a zero iteration count; each taken-up station behind `current_station` needs its gate decision in `decisions_log`. ARQ is a short note by `architect` in `docs/ARCHITECTURE.md` or the batch record: "no module boundary moves, no dependency edge added; one exposed-contract change (`mermaid.slugify` empty result, `mermaid.dump` root ordering)", with the empty map diff as evidence.
2. **PDR (with ARQ)** — one short design proposal written against the P2-reviewed requirements and reviewed by `architect` + `qa-reviewer` + `ux-reviewer` (D1) before increment 001. §6.2 and rulings R1–R4 already hold most of the design; the proposal cites them.
3. **ux-reviewer (D1)** — a bounded pass at PDR on two observable changes (import preview without the `? ` prefix and with `row-N` ids; roles screen blank-then-populate with inert keys), and a cognitive walkthrough at validation against the real mechanism (`run_test`).
4. **Security (C1, C6)** — §6.3 already holds the security questions and answers and says `security-reviewer` is not required. Because the scan did fire, propose one light `security-reviewer` read of §6.3 plus increment 003 (worker and generation guard); skipping it is the orchestrator's recorded call.
5. **DDR (with PDR)** — owed before formal validation: the reverse census of the B1 hits crossed between increments, and the B3 golden-drift census (dump goldens 8/8 unchanged).
6. **At every increment cut** re-run B1–B4 and record in the packet; B4's output-then-consume ATs (AT-084/085/086) already exist. **At every gate** re-run the C scan over the diff, and F.
7. **Record** with `devflow-init.py --fired A2,A3,B1,B3,B4,C1,C6,D1,E1 --not-fired A1,A4,B2,C2,C3,C4,C5,C7,C8,D2,E2,E3,F1,F2` (orchestrator; this evaluation did not touch `state.json`).

## Where we are

P0, `not-started`. The batch opened by rollover from `2026-10-11-reqharness-batch` (closed and
synced); the outgoing `decisions_log` is archived at
`.dev-flow/2026-10-11-reqharness-batch/decisions-log.json` + `state-snapshot-at-close.json`.
This unit delivered the P0 intake: all four backlog items reproduced on `master`
(`5a991c6`), code located, expected behaviour + risk + proposed fix recorded in
`spike/intake.md`. Owed next: the P0 Definition-of-Ready gate (operator picks which READY
stories proceed + answers the two kickoff questions), then the trigger evaluation, then P1.
P1 requirements for all four stories are drafted (unit FIXES-P1: `01-requirements.md`,
`01-requirements-ledger.md`, rulings R1-R4 in the decision log); the P1 gate has not been run.
The independent P2 review (approve-with-conditions, 0 blocker, 2 major, 5 minor) is applied: LED .7–.11, dispositions in `02-review.md`. Increment 004 (B-110, B-113; test-only) is added: LED .12, .13, AT-088/AT-089.

## Objective

Fix four shipped defects, all reproduced at intake (evidence: `spike/intake.md`):

- **B-115** — `slugify("")` returns `"n"` (`mapper/mermaid.py:51`) and the CSV import slugifies
  an empty parent cell (`mapper/import_csv.py:70`), so every parentless row points at node `n`,
  ids that slugify to empty collide on `n`, and a root literally named `N` saves as a self-cycle.
- **B-116** — a CSV listing a child before its root is refused as a cycle
  (`mapper/import_csv.py:107-112` closes the later-declared root's tree back into the first row).
- **B-117** — a forest map's root changes on reload: `mermaid.dump` writes edges before
  parentless nodes and `parse` takes the first parentless node in text order
  (`mapper/mermaid.py:127`, `:135-166`).
- **B-127** — the roles screen runs `identity.repo_root` + two `git config --get` sequentially
  on the UI thread at mount (`mapper/screens/roles.py:471-483`, `:178`, `:222`), worst case
  ≈ 30 s freeze (10 s timeout each).

## Per-story / per-station status

| Story / station | Status | Notes |
|---|---|---|
| B-115 | READY | reproduced; fix = skip the slugify call for an empty parent cell + row-N fallback for ids that slugify to empty; 2 source files (`mapper/mermaid.py`, `mapper/import_csv.py`) |
| B-116 | READY | reproduced; fix = pick the root as the parentless node after edge building (never attach a would-be root under the first row); shares `mapper/import_csv.py` with B-115 — same increment |
| B-117 | READY | reproduced; fix = `dump` writes the declared root's node line first; pins the current behaviour (csv-safety R11, LLR-CSV.1.3 forest regression) must move with it |
| B-127 | READY (non-visual alternative) | reproduced; moving `_load` off the UI thread needs a Textual worker; a visible loading state is a UI-design decision requiring a prototype verdict — proposed minimal alternative in `spike/intake.md` §B-127 |
| P0 | in-progress (intake delivered by FIXES-P0) | gate owed: operator picks READY stories + kickoff answers |
| P1 | requirements drafted (unit FIXES-P1), gate not run | `01-requirements.md` (4 US, 4 HLR, 12 LLR, AT-084…AT-087, IFC Part A), `01-requirements-ledger.md` (LED-2026-10-11-fixes-batch.1…6); validator line below |
| P2 | review applied (qa-reviewer role, DeepSeek): 7 findings resolved | `02-review.md` dispositions; ledger LED .7–.11; gate decision owed |
| B-110 | READY (test-only) | increment 004; 0 source files |
| B-113 | READY (test-only) | increment 004; 0 source files; backlog file pointer corrected |
| P3–P5 | not-started | |

## Roadmap + increment plan

Four increments (004 is test-only), each ≤ 4 SOURCE files (tests uncapped), each with its own review packet,
RED counterfactual and sha256 restore check. Exact test node names: `01-requirements.md` §5.1.

1. **Increment 001 — B-115 + B-116 (CSV import)** · `HLR-FX.1`, `HLR-FX.2` · AT-084, AT-085.
   Source (2): `mapper/mermaid.py` (`slugify` returns `""`), `mapper/import_csv.py` (blank-first
   parent read; `row-N` for an empty slug; root chosen by parentage). New tests:
   `tests/test_fixes_csv_import.py`. **Moves:** `tests/test_mermaid.py::test_slugify_allows_hyphens`
   (the `"---" == "n"` pin → `""`) — the only existing test that fails on the patched tree
   (14-file suite: base 490 passed; patched fails only that pin). RED mutants: M-FX1…M-FX5.
2. **Increment 002 — B-117 (forest root round-trip)** · `HLR-FX.3` · AT-086.
   Source (2): `mapper/mermaid.py` (`dump` hoists the declared root inside its two existing edge
   passes), `mapper/store.py` (`_check_round_trip` docstring only; no behaviour change). New tests:
   `tests/test_fixes_forest_root.py`. **Moves:** `tests/test_csv_safety_store.py::
   test_save_accepts_legacy_forest_after_edit` (adds `reloaded.root_id == loaded.root_id == "a"`; the
   R11 comment is rewritten); `tests/test_perf_dump.py::test_dump_fixture_goldens` (inline
   `orphan-order` arm gains `ordered.root_id = "root"`, expected bytes unchanged — without it the arm
   fails). **Golden files: none change** (8/8 dump goldens + AT-076 bytes identical, visit bound
   2E + 4 holds). RED mutants: M-FX6, M-FX7, M-FX12.
3. **Increment 003 — B-127 (roles screen mount)** · `HLR-FX.4` · AT-087.
   Source (1): `mapper/screens/roles.py` (`_discover` in a thread worker at mount/resume; cached
   facts; paint gate; generation guard; key guards). `mapper/reqharness/identity.py` is NOT
   touched (cache lives in the screen). New tests: `tests/test_fixes_roles_thread.py`. **Moves:**
   `tests/test_roles_screen.py::_open_roles` (adds `await app.workers.wait_for_complete();
   await pilot.pause()`; 22 of 22 pass with it, 6 and 12 fail on two runs without it).
   RED mutants: M-FX8…M-FX11, plus M-FX13 (late result applied to a popped screen) and M-FX14 (discovery catch removed) from the P2 review (LED .7, .8). The worker catches exactly `(OSError, ValueError, subprocess.SubprocessError, ValidationError)` and maps them to `no repo`; the screen cancels its workers on unmount and the hand-back discards a late result. No visual chrome.
4. **Increment 004 — B-110 + B-113 (test-only guards)** · `HLR-FX.5`, `HLR-FX.6` · AT-088, AT-089.
   Source (0). Test files (2): `tests/test_export_state.py` (one async spy test,
   `test_exporting_reads_pan_extent_through_its_own_module_global`, patching
   `mapper.screens.map.exporting.pan_extent`), `tests/test_inc9c.py` (`LEAK_EXCEPTIONS` retyped
   `(file, lineno, expr)`, both consumers compare the full record, one negative control
   `test_at_089_a_second_leak_site_in_an_excused_file_is_still_flagged`). **Moves:** the three
   `LEAK_EXCEPTIONS` keys (call lines `home.py:175`, `screens/map/screen.py:214`,
   `common.py:213`). RED mutants: M-FX15 (rebind `exporting.py` to `layered.pan_extent`), M-FX16
   (key back to `(file, expr)`). Risk: the leak key becomes line-sensitive (fail loud by design).
   The B-113 backlog row pointed at `tests/test_inc9q.py`; the registry is in `tests/test_inc9c.py`
   (correction appended in `BACKLOG.md`).

## Key decisions

| Date | Decision | Why |
|---|---|---|
| 2026-10-11 | Mode `core` | `/dev-flow` routing matrix: any change to product code or tests → `/dev-flow`; the level table sends a small/non-trivial fix to `core` (`full` is for client/regulated or ISO 29148 need — none here); four small fixes, no frozen interface, one lane |
| 2026-10-11 | Batch opened in a worktree (`feat/fixes-batch` @ `5a991c6`) | §Batch rollover: one checkout holds one active batch; a prototype round may be using the primary checkout, so all work lands in the worktree and its own `state.json` |
| 2026-10-11 | B-127 scoped to the non-visual alternative | A visible loading state is a TUI design change; the recorded standing practice requires a prototype verdict first — the minimal worker-based fix needs none |
| 2026-10-11 | `.git/info/exclude` build-cache append skipped | In a worktree the path resolves to the primary checkout's shared `.git/info/exclude`, which this unit must not touch; `.gitignore` already covers `__pycache__/` and `.venv/`, and the test rule runs pytest with `-p no:cacheprovider`, so no cache can reach the close-gate diff |

## Risks / watch-items

- B-117 changes behaviour pinned by the csv-safety batch (ruling R11: round-trip check must NOT
  compare the root; LLR-CSV.1.3's forest regression). Likelihood certain; mitigation: those
  pins move in the same increment, with the RED proof showing the old pin failing first.
- B-115's empty-parent fix touches every parentless CSV row (the `? ` parked prefix on
  legitimately top-level rows disappears); the import preview's collision/park surfaces need
  re-assertion, not just the new cases.
- B-127's worker changes mount timing; roles-screen tests that assert paint state immediately
  after push may need a `pilot.pause()` — watch for flaky-looking failures, not code defects.
- `devflow-validate.py` V7/V15/V16 are environment blocks (flow bundle hash / kit state), not
  batch defects — recorded, not chased.

## Conventions honored

- All UI strings English; colours would come from `mapper/darkside.py` tokens and keys from
  `mapper/keymap.py` (no hard-coded glyphs/hex) — no UI change in this batch's scope.
- Tests drive `MapperApp(tmp_path)` + `run_test` + real `pilot.press`, reusing
  `tests/test_draft_save.py` helpers; pytest from the worktree root with
  `-p no:cacheprovider`, single test files.
- No Windows user name, user-profile path, account name or GitHub handle in any file;
  `state.json.owner` stays OMITTED (project guard A-110).
- RED counterfactual evidence and sha256 restore check owed per increment (worker-unit rule).

## Out-of-scope carries

- A visible loading state for the roles screen (prototype verdict first) — tracked in B-127's
  backlog row once the non-visual fix lands.
- B-118 (mount renders 2–3×), B-120 (selection-only layout thrash) — perf items, stay in the
  backlog; this batch is not a perf batch.
- B-124..B-126 (ReqHarness follow-ups) — stay in the backlog.

## Test ledger

| Suite / command | Last run | Result |
|---|---|---|
| `python <flow>/tools/devflow-validate.py --brief` (in the worktree) | 2026-10-11 | see below (run at intake; block lines recorded in `spike/intake.md` §Validator) |
| Repro probes B-115/116/117/127 (`python - <<EOF` from the worktree root, master state) | 2026-10-11 | all four reproduced — transcripts in `spike/intake.md` |
| P1 draft-time probes, run in a SCRATCH COPY of the tree (nothing in the worktree changed): 14-file CSV/mermaid/dump suite (`test_import_csv`, `test_csv_safety_preview`, `test_csv_safety_store`, `test_mermaid`, `test_gate2`, `test_inc9`, `test_inc9c`, `test_inc9m`, `test_inc9n`, `test_key_dispatch`, `test_repair_cycles`, `test_repair_fields`, `test_perf_dump`, `test_model`) | 2026-10-11 | base: 490 passed, 1 failed (the scratch copy lacks `.dev-flow/` for one census test — environment); patched CSV+dump rule: only the slugify pin moves, `test_perf_dump` passes (3 failures of a first draft that re-walked the edges fixed) |
| `tests/test_roles_screen.py` in the scratch copy with discovery on a worker | 2026-10-11 | 22 passed with the `_open_roles` wait; 6 and 12 failed without it (timing) |
| Gated-git thread probe for B-127 (scratch copy) | 2026-10-11 | base: first git call on the main thread, blocks the mount; prototype: 3 of 3 calls off the main thread, surfaces empty and inert while gated, painted after release |

## Decision log

Human-readable mirror of `state.json.decisions_log` (empty at open; the archive of the
outgoing batch is `.dev-flow/2026-10-11-reqharness-batch/decisions-log.json`).

| Date | Id | Ruling / decision | Reason | Ledger |
|---|---|---|---|---|
| 2026-10-11 | R1 (B-115) | A blank or whitespace-only parent cell is "no parent" (root candidate); a non-blank cell with an empty/unknown slug parks the row. `slugify` returns `""` when nothing survives (no silent `"n"`); the CSV importer gives such an id the next `row-N`. Callers read: `import_csv.py:59`, `import_csv.py:70`, `screens/map/editing.py:115` (already `slugify(title) or "n"` + uniqueness loop). | A raised error would make an importable spreadsheet unimportable; a hash placeholder is non-deterministic and no caller needs it; `""` lets each caller decide and leaves `editing.py` untouched. Pin `tests/test_mermaid.py:12` moves in 001. | LED-2026-10-11-fixes-batch.2 |
| 2026-10-11 | R2 (B-116) | The root is the first row, in file order, with no parent edge that was not parked for a missing parent. More than one parentless row: the existing forest rule — the first is root, the others attach under it and are parked `? `. A genuine cycle stays unattached and is named by `find_cycle`. | Row order must not decide the root; the existing forest rule is kept so only the wrong-root results change (permutations: 24 of 24 identical vs 6 of 24 on base). | LED-2026-10-11-fixes-batch.3 |
| 2026-10-11 | R3 (B-117) | `dump` hoists the declared root's line first only when the root appears in the text, is no edge's child and is not already the first parentless node, using bookkeeping inside its two existing edge passes; `parse` unchanged. Goldens: none change. Pins moved: legacy-forest test (+root assertion), `_check_round_trip` docstring, the inline `orphan-order` arm's fixture (`root_id = "root"`, bytes unchanged). No root comparison added to the round-trip check. | Conditional hoist keeps 8/8 goldens and AT-076 bytes; an unconditional line moves `forest`/`wide6000`; a re-walk breaks the 2E + 4 bound (36000 > 12004, executed); a root comparison would refuse maps that open today. | LED-2026-10-11-fixes-batch.4, LED-2026-10-11-fixes-batch.6 |
| 2026-10-11 | R4 (B-127) | `repo_root` + `identity.read` run in a Textual thread worker at mount and resume; no new chrome. Until the first discovery returns: the four Statics stay empty and every key is silent and inert (a decision beyond the ruling's "existing messages": the existing inert hint says `no repo`, untrue while loading). On resume the previous paint stays. Latest discovery wins. Keypress-time reloads reuse cached facts and run no git. Cache lives in the screen, not `identity.py`. | Honours the operator's non-visual alternative without painting a wrong viewer, head or message. | LED-2026-10-11-fixes-batch.5 |
| 2026-10-15 | R5 (P2 review) | Worker lifetime: a result returning after the roles screen was popped is discarded (worker cancellation on unmount + `is_mounted`/not-cancelled guard in the hand-back). Discovery catch is exactly `(OSError, ValueError, subprocess.SubprocessError, ValidationError)` → existing `no repo` state; anything else propagates; test seam = monkeypatched function. Unicode: only what `slugify` does today, one non-regression arm. CSV counter, depth-parentage, HLR/LLR `Esc` wording and AT-085 helper amended. | Orchestrator rulings on the independent P2 review's two MAJORs and MINOR-5; the MINORs accepted as proposed. A bare `except Exception` was rejected: it would hide defects. | LED-2026-10-11-fixes-batch.7, .8, .9, .10, .11 |
| 2026-10-15 | R6 (increment 004) | Add a test-only increment for B-110 and B-113 from the read-only spike: 2 test files, 0 source files. Correct the B-113 backlog pointer to `tests/test_inc9c.py`. | Both are accepted gaps from the modular batch; each fits one increment well under the cap. `state.json` `decisions_log` mirror of R5/R6 is owed to the orchestrator (this unit does not edit `state.json`). | LED-2026-10-11-fixes-batch.12, .13 |
| 2026-10-15 | R7 (PDR, architect) | The roles worker RETURNS its facts and `on_worker_state_changed` (SUCCESS) applies them with the generation and `is_mounted` checks; no `call_from_thread`. ARQ F2 corrected: a map loaded from disk takes its root from `parse`, so the hoist does not fire on resave; it fires only for in-session roots (CSV import; `editing.py:221`); B-117 stops future drift but cannot repair already drifted maps. Increment 003 also amends `docs/ARCHITECTURE.md:113` (`roles.py` in the `screens` row paths, ownership prose and exposes list) and the `mermaid` row note citing the batch id. The `store` to `mermaid` map gap is B-132; the doubled discovery start is a DDR item. | A `call_from_thread` from a worker still running at app exit can hang the exit; the F2 claim was checked against `parse` and was wrong; the staleness rule amends the map before the touched file. | LED-2026-10-11-fixes-batch.14, .15 |
| 2026-10-15 | R8 (PDR, ux-reviewer) | Key-bar subtraction while loading (navigation and `Esc` only, no edit keys; test + mutant M-FX17); no extra status-line signal; walkthrough evidence for the blank window is `executed (injected delay)` only; AT-084/085/087 assert painted frame text (C-32); real-user evaluation `not performed — one-person team`; follow-ups B-128 (visible loading prototype, J5) and B-129 (`? ` prefix on top-level import rows, J1). | Honours R4's no-new-chrome ruling by subtracting, not adding; a new signal needs a prototype round first. | LED-2026-10-11-fixes-batch.16 |
| 2026-10-15 | R9 (PDR, qa-reviewer + light security) | Threshold arm `,Alpha,` then `,,` gives `{alpha, row-1}` on LLR-FX.1.3 / TC-FX-1.3; one sentence in §6.3 naming the `row-N` collision surface; BOM `utf-8-sig` (B-130) and quoted embedded newline (B-131) are pre-existing backlog rows; the large-forest dump scaling test stays an optional note in the proposal. PDR sealed `approved with conditions` 2026-10-15 (`design/PDR-2026-10-11-fixes-batch.md`). | Closes a counter-semantics gap in the importer; the two CSV findings do not belong to this batch's defects. | LED-2026-10-11-fixes-batch.17 |
