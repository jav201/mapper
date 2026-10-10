# Post-mortem — mapper — Batch 2026-10-09-modular-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`).
> Phase 5 artifact. Co-authors: `architect` + `qa-reviewer`. Structured for cross-batch sweeping — keep the section order.

> **Owed in.** `core` — · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-mode table, which is this fact's one home. A mode marked `—` **does not owe this artifact, and its absence is not an omission**; `by trigger` means the station exists only when the `triggers` block fired, and `stations_active` in `state.json` is the authority for *this* batch. Where a SECTION or a gate row is owed more narrowly than the artifact, it says so on the row.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Gated tree` · `Found before the batch` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.

## 0 · Gate record — which tree this close gated

| Field | Value |
|---|---|
| Gate record | `pytest -m "not slow and not network"` (default `addopts`, `pyproject.toml:46`) → exit 0 — **3133 passed / 3 xfailed / 0 failed** · 2026-10-10 — stored at `evidence/p4-gate-full-suite.transcript` (the numbers `04-validation.md` carries; P4 was under qa review at this close) |
| Gated tree | `69676cf` · clean — HEAD at this close is `c5905d6`; `git diff --name-only 69676cf..HEAD` returns 9 files, all under `.dev-flow/` (requirements/DDR re-pointing, evidence transcripts, `state.json`) — no product or test file differs from the gated tree |

> **This is `full`'s copy of the two rows `close-template.md` §0 carries for `core`, and that
> file's §0 note is the rule's one home** — `full` is not seeded `05-close.md`, so `V57` reads
> the record here instead. Write it at the close gate from that run's own `git rev-parse HEAD`
> and `git status --porcelain`.

## 🔑 At a glance (read first)

- **Outcome:** closed with carry-over — 2 review LOWs and 3 accepted gaps carried to the backlog (B-108…B-110); no open condition on the design record.
- **Top 3:** ① a 3454-line `MapScreen` moved into 12 concern modules with **zero rewritten tests** — byte-identity (`tests/test_mod_bodies.py`), a pre-move parity golden (AT-065) and per-gate full suites held behaviour ② **5 of 9 increment gates went red first** on stranded/vacuous census tests that still rooted at `mapper/app.py` after the code moved ③ root cause of ②: census tests were generalised to the package in follow-up commits instead of in the same commit as the move — cheap to fix each time, expensive in gate iterations.
- **New control this batch:** AT-071 (`tests/test_mod_deps.py::test_at071_the_module_graph_allows_parallel_lanes`) — an executable dependency rule over `mapper/screens/map/` that makes per-concern parallel lanes legal; plus the LLR-MOD.7.2 census freeze (`tests/test_mod_census.py` vs `spike/census.json`).
- **Open items → next batch:** 6 — B-33 performance/scale (first datapoint: `test_strips` 16.3 s at 118×34, `evidence/ddr-acbd087-slow-lane.transcript`); then B-107 (ReqHarness), B-106 (flow-side id namespacing), B-108…B-110 (this batch's carries).
- **Metrics:** iterations 14 across stations · findings 48 opened / 46 closed (2 LOWs carried) · ledger 2941 → 3133 (192 added, 0 deleted)

> Enough to know the batch's health and what carries forward. Detail below only for the why.

---

## Detail (reference)

### What worked
- **The verification spine, not heroics, carried the risk.** A 3454-line move shipped with zero behavioural drift: per-method `ast.dump` against an Inc-0 baseline + undefined-global check (`tests/test_mod_bodies.py`, QA-2 ruling), a text golden captured at Inc-0 before any move at 118 and 87 columns (AT-065, QA-1 ruling), the full suite at every one of the 9 increment gates, and the parity baselines `evidence/mod_parity_118.txt` / `mod_parity_87.txt`.
- **The MRO spike happened before the cut, not after.** `evidence/arq-mro-spike.transcript` (Textual 8.2.8) showed `BINDINGS` / `DEFAULT_CSS` / `@on` in a plain (non-`DOMNode`) mixin are silently ignored while `on_*` handlers dispatch from every MRO class — so mechanism A shipped with `BINDINGS` frozen on the core class, an AST ban on mixin decorators/CSS (`tests/test_mod_dispatch.py -k bindings/disjoint`), and the disjoint-`on_*` guard (AT-066).
- **Scripted moves for the mechanical spine.** B0 and B1–B11 were executed by orchestrator AST scripts with byte-identical method bodies, pinned by `tests/test_mod_bodies.py` against `evidence/mod-bodies-baseline.json` — the reviewer's "identical body can still raise `NameError`" scenario is closed by the per-module undefined-global check.
- **The reviews earned their keep.** P2 round 1 found 4 blockers before a line moved (02-review.md:35-38); the DDR found what the PDR's checks had missed (D-C1, below) and every condition was discharged by re-reading, with the proving line quoted (DDR B8).
- **Outcome for the operator's goal:** `mapper/screens/map/` now holds 12 modules with guarded disjoint names and the AT-071 dependency rule — two workers can edit separate concern files without touching the same file, which is what the next batches need to run parallel product lanes.

### What didn't / friction
- **5 of 9 increment gates went red first** — inc0 (8 failed), a5a-b0 (3), a5b (2), b1b2 (1), a6a7a4 (2) — each a stranded or vacuous census test still rooted at `mapper/app.py`; each fixed in a follow-up commit (named per gate in DDR B5; the b1b2 one was the keymap seat scan's base-class blind spot, fixed at B7, `5229b12`). None was a product defect; all were avoidable.
- **Group code review found 3 MED vacuous census scans** after the gates had gone green (repaired in `1c77233`, six test files) — the scans passed while scanning less than they claimed (ARCH-3's class, found late).
- **Kimi worker timeouts (exit 124) on big units** — mitigated by splitting units smaller, longer timeouts, and the orchestrator running the wide test sets itself.
- **Tooling self-inflicted wounds:** `ruff --fix` stripped the re-exports after B0 (fixed by declaring `__all__` in `mapper/app.py`, `d4948b2`); a text-replace prune script corrupted `app.py` once (line-range edits, bottom-up, since); a packet-copy loop overwrote `increment-001.md` with the template (recopied — checksum packets after copy); operator-path PII reached transcripts (scrub step now runs before every evidence commit).
- **Runner fed an empty prompt** when handed a relative plan path — exit 0, no work done. The runner now resolves paths and refuses an empty plan (exit 3).
- **Network lane not run** (no network at the gates) — `pyproject.toml:46` deselects it; it stays unwired as before.

### Scope drift (planned vs actual)
| Planned | Actual | Note |
|---------|--------|------|
| 22 increments (Inc-0 + spine A1–A7/A4 + B0 + B1–B11 + B12) | 23 packets (`03-increments/increment-001..023.md`) | increment-023 is a docs+guards-only increment (0 product files, `increment-023.md:41`) that closed DDR conditions D-C1..D-C3 at `69676cf` |
| Parallel extraction increments in separate Kimi worktrees | One trunk, sequential increments | the spine's own dependency order (A5b before A6, B0 before everything) made lanes illegal until AT-071 landed; the fork mechanics were exercised only as the six disjoint Inc-0 sub-lanes (PDR A8, DDR B6/B8) |
| `MapScreen` split into concern mixins only | Same, plus one declared deviation | `action_open_ficha` stays in the core `mapper/screens/map/screen.py` — moving it needs a `navigation ↔ screen` import cycle or a changed body; recorded at `03-increments/increment-018.md:22` and `docs/ARCHITECTURE.md:51` |
| F4 lazy-read design | Dropped at P2 (ARCH-2 ruling) | full patch census instead; every patch target repointed to its reading module in the moving increment, guarded by `tests/test_mod_compat.py:54` (`PATCH_SURFACE`) |

### Metrics (full)
| Metric | Value |
|--------|-------|
| Iterations per station | `{P0:1,P1:2,P2:3,P3:1,P4:1,P5:1,P6:0}` (plus ARQ:1 · PDR:2 · DDR:3 — P1 iteration 1 after P2 round 1; P2 round 1 → iterate → round 2; DDR draft → revision → re-review seal; `state.json` `iterations_per_station`, `decisions_log`) |
| Findings opened / closed | 48 / 46 (2 LOWs carried to the backlog) |
| Findings by severity (blocker/major/minor) | 6/7/12 at P2 (round 1: 4/6/8, `02-review.md:17`; round 2: 2/1/4 — ARCH-8/9 blockers, ARCH-10 major, ARCH-11 + N-1/N-2/N-3 minors) · PDR conditions C1–C9: 9 · group code reviews: 0 HIGH / 3 MED (vacuous census scans, repaired `1c77233`) · DDR: D-C1 HIGH, D-C2/D-C3 MED, QA-MED-1/2, 2 LOWs carried |
| Where caught (P2 / P3 gate / P4) | 25 / 8 (5 red-first gates + 3 MED scans) / 15 (C1–C9 re-discharge is verification; the new work was D-C1..D-C4, QA-MED-1/2, 5 LOWs of which 3 discharged, 2 carried) |
| Test ledger (base − D + A = post) | 2941 − 0 + 192 = 3133 (base per PDR proposal §5; post = the P4 gate at `69676cf`: 3133 passed / 3 xfailed / 0 failed, 24 deselected; the `acbd087` mid-count 3131 + 2 nodes from increment 023; slow lane 19/0 at `acbd087`; network lane not run) |
| Files touched · increments (cap trips) | 108 in `git diff --name-status e4d58c1 HEAD` (25 product+docs, 25 tests, 58 batch record/flow state; pre-`e4d58c1` batch records — PLAN.md, 00-checklists.md, the original P1 contract, `arq-mro-spike.transcript` — committed before the reconciliation base) · 23 increments · 1 source-file cap trip: increment-002 (A1) at 4/4, none exceeded (`increment-002.md:50`, DDR B7) |

### Root causes (only if a phase took ≥2 iterations)
- **P1 iteration 1 ← P2 round-1 iterate-to-refine.** Round 1 found 4 blockers: ARCH-1 (no legal `MapScreen` import edge for the sibling screens — ruled: siblings import from `mapper.screens.map`, spine reordered), ARCH-2 (8 patch targets, not 2 — ruled: full patch census, repoint in the moving increment), QA-1 (parity capture undefined — ruled: text golden at Inc-0), QA-2 (no body identity — ruled: `tests/test_mod_bodies.py`). Kimi K2 applied all 18 round-1 findings in four units.
- **P2 round 2 + iterate ← the ARCH-1 ruling itself.** Reordering the spine surfaced ARCH-8 (`MapHintLine` would stay in `app.py` at B0 — moves at A1) and ARCH-9 (`PlugRepoScreen` pushes `RepoScreen`, so A6 cannot precede A5b); the orchestrator's spine probe then verified 0 illegal edges (`evidence/p2r2-spine-probe.transcript`).
- **DDR revision ← the reviews, not the design.** D-C1 (a wrong frozen row, below) and QA-MED-1/2 (record overstatement / a gate figure that predated `1c77233`) each took one revision pass; all discharged by re-reading at increment 023.

### Process / workflow findings
> About the dev-flow itself (phases, gates, templates, agents, controls). Feeds workflow improvement — keep separate from product.
- **A design-review row that verifies a frozen interface must quote the CONTENT it checked, never its status label.** The PDR/B2 checks cited the F4 row as "frozen" and passed; the row named 4 of 7 repoint targets at their pre-move homes. The DDR caught it (D-C1) only because it re-read content. Suggested change: the PDR/DDR template's frozen-interface row requires the quoted content inline (D-C4 now does exactly this — make it the template's default, not this record's exception).
- **Store the RED run per increment, not just assert "permanent control".** QA-MED-1: stored per-increment RED transcripts existed only for AT-067 (`evidence/a1-red-patch-repoint.transcript`); the in-tree RED arms of every guard file were executed and stored once, at the DDR (`evidence/ddr-red-arms.transcript`). Suggested change: the packet template gains a RED-transcript row that must name a stored path per increment.
- **Census tests must be generalised to the package in the SAME commit that moves the code.** 5 of 9 gates went red first because the generalisation landed in follow-up commits. Suggested change: the increment template's gate row requires the moved code's census tests re-pointed before the gate, not after.
- **Worker-unit sizing:** Kimi exit-124 timeouts on big units → the orchestrator now splits units smaller, sets longer timeouts, and runs the wide test sets itself. Suggested change: fold the split/timeout defaults into the runner.
- **Tooling guards:** `ruff --fix` strips re-exports (guard: `__all__`, now in `mapper/app.py`); bulk text-replace scripts corrupt files (rule: line-range edits, bottom-up); packet copies overwrite (rule: checksum after copy); transcripts carry PII (rule: scrub before every evidence commit); a runner given a relative plan path once ran an empty prompt with exit 0 (rule: resolve paths, refuse empty plan, exit 3).

### Product findings
> About the code/product under development.
- Mechanism A (plain mixins) is sound on Textual 8.2.8 **only** with the shipped guards: `BINDINGS`/`DEFAULT_CSS`/`@on` in a non-`DOMNode` mixin are silently ignored; `on_*` handlers run from every MRO class, so names must be disjoint — enforced by `tests/test_mod_dispatch.py -k bindings/disjoint` and AT-066.
- `mapper/screens/map/` ships 12 modules (core `screen.py` + 11 concern mixins + `navigation.py` value class) with the AT-071 dependency rule; sibling screens import `MapScreen` from `mapper.screens.map`, never from `mapper.app`; B-02 (`factory.py` importing `mapper.app._PromptScreen`) is closed at A2 (`02959fb`).
- **CR-3 (accepted gap):** `mapper/screens/map/exporting.py:13` is its own unpatched reader of `pan_extent`; the suite's only patch site (`tests/test_en8.py:66`) bites through `panning.py`. Carried as B-110.
- **D-C3 residual (architect LOW):** the cycle guard sees direct importers only (`tests/test_mod_deps.py:303`). Carried as B-109.
- **Census-baseline location (B1(h)):** `tests/test_mod_census.py:39` reads `.dev-flow/2026-10-09-modular-batch/spike/census.json`; it must move under `tests/` before the batch folder is archived. Carried as B-108.
- B-33 (performance/scale) is the NEXT batch; the slow-lane timings (`evidence/ddr-acbd087-slow-lane.transcript` — `test_strips` 16.3 s at 118×34, 19 passed / 0 failed) are its first datapoint.

### Control lineage
- **New control proposed this batch:** AT-071 (`tests/test_mod_deps.py::test_at071_the_module_graph_allows_parallel_lanes`, :444-448) — the module-graph rule that makes per-concern lanes legal; origin: ARCH-1/P2 + the operator's parallelisation goal. **Status: adopt** — already in force at the P4 gate. Companion: the LLR-MOD.7.2 census freeze (`tests/test_mod_census.py` vs `spike/census.json`, DDR B3), adopt-next-batch once B-108 relocates its baseline.
- **Prior controls exercised:** the full suite at every increment gate (held — 9 gates, each red-first failure caught before integration); the byte-identity oracle `tests/test_mod_bodies.py` (held — every scripted move byte-identical); the parity golden AT-065 with its tmp-copy mutant arm (held); the patch-surface guard `tests/test_mod_compat.py:54` (held — and it is what made D-C1 detectable). **Stress-tested:** the family-B census controls (ARCH-3 class) — they failed open three times (3 MED vacuous scans) and were repaired package-wide in `1c77233`.

### Open / deferred items → next batch
| Item | Type (process/product) | Reason deferred | Trigger / owner |
|------|------------------------|-----------------|-----------------|
| B-108 — census baseline must move under `tests/` before the batch folder is archived | product | out of this batch's freeze; must land before archiving | next batch touching `tests/test_mod_census.py` / orchestrator at archive time |
| B-109 — D-C3 cycle guard one-hop closure (`tests/test_mod_deps.py:303`) | product | accepted residual; a missed cycle fails loudly at import time, not silently | next batch touching `tests/test_mod_deps.py` |
| B-110 — CR-3: patched test for `exporting.py`'s own `pan_extent` reader | product | deliberate gap, recorded at DDR B1(b); zero observed exposure | next batch touching the export concern |
| B-33 — performance/scale (`MAX_RENDER_NODES` bounds count, not work; O(E) walks) | product | the NEXT batch by prior routing; this batch adds only the slow-lane datapoint | next batch (design), with B-33's existing reproduction |
| B-107 — ReqHarness, mapper's product direction | product | awaits the operator's verdict on the unified decision gallery | operator verdict, then the next feature batch |
| B-106 — flow-side requirement-id namespacing | process | belongs to the flow's bundle, not this repo | the rev101 session owns the flow bundle |

### Working-file reconciliation (C-44) — MANDATORY, every file this batch touched
> **Run it as a sweep, never from memory:** `git status --short` in **every repository touched, auxiliary repos outside the project tree included** (skills / commands / config are where this hides) · `git log @{u}..HEAD` for commits that exist but were never pushed · an open-PR check for any branch other work depends on. **Report pre-existing uncommitted changes as FOUND, never fold them into this batch's commit.** A tracked file already modified when the batch began goes in the `Found before the batch` field below the table, not in it (`templates/docs/close-template.md` §3 holds the rule).
>
> **A commit that never lands is NOT a terminal state.** Work that is finished but unlanded is indistinguishable from work never done — and it makes the state files the next batch reads assert something false, which that batch then inherits as a premise (**C-43 §2.7**).

Base verified: `e4d58c1` (the amended P1 contract, parent of the in-range work; P0/ARQ and the original P1 contract predate it and are committed records, per `PLAN.md` §Header / `state.json` `base_ref` = `d8cf942` = the pre-batch tip). Sweep: `git diff --name-status e4d58c1 HEAD` = 108 files, tree clean (`git status --porcelain` empty at this close); no auxiliary repos, no unpushed-check done here (orchestrator owns the push).

| Repo | File(s) | Terminal state | Landing / backlog ref |
|------|---------|----------------|-----------------------|
| mapper | `mapper/app.py` (M — 5255 → ~50 lines + `__all__` re-exports); `mapper/store.py`, `mapper/screens/factory.py`, `mapper/screens/settings.py` (M — patch-site/cite follow-ups); new `mapper/screens/common.py`, `prompt.py`, `home.py`, `repo.py`, `plug_repo.py`, `import_preview.py`, `construct.py`; new package `mapper/screens/map/` (`__init__.py`, `screen.py`, `navigation.py`, `drafts.py`, `editing.py`, `exporting.py`, `focus_mode.py`, `hints.py`, `opening.py`, `painting.py`, `panning.py`, `searching.py`, `undo.py`) — 24 files | ✅ committed + landed | commits `b024a13`…`69676cf`; HEAD `c5905d6` |
| mapper | `docs/ARCHITECTURE.md` (M — module map, F1–F5 freeze rows, §3 rules; TARGET-row rule added only for files on disk, `20c0161`) | ✅ committed + landed | `d4948b2`, `69676cf` |
| mapper | tests: 18 modified (`test_app.py`, `test_app_imports_used.py`, `test_arch_osopen_callers.py`, `test_darkside_census.py`, `test_draft_hygiene.py`, `test_en5.py`, `test_en7.py`, `test_en8.py`, `test_fold.py`, `test_inc3_census.py`, `test_inc9c.py`, `test_inc9m.py`, `test_inc9n.py`, `test_inc9o.py`, `test_inc9p.py`, `test_inc9q.py`, `test_keymap.py`, `test_search.py`) + 7 new (`test_mod_bodies.py`, `test_mod_census.py`, `test_mod_compat.py`, `test_mod_deps.py`, `test_mod_dispatch.py`, `test_mod_parity.py`, `test_mod_structure.py`) | ✅ committed + landed | `90e731b`…`69676cf` |
| batch record | `.dev-flow/2026-10-09-modular-batch/` — 56 files in range (3 requirements/review records, 23 increment packets, 3 design records, 23 evidence transcripts, 4 spike scripts incl. `census.json`) + pre-range records (`PLAN.md`, `00-checklists.md`, `evidence/arq-mro-spike.transcript`, spike proposal/census notes) | ✅ committed + landed | `PLAN.md`, packets `03-increments/increment-001..023.md`, sealed `DDR-2026-10-09-modular-batch` |
| flow state | `.dev-flow/BACKLOG.md` (M — B-104…B-107 earlier; B-108…B-110 at this close), `.dev-flow/state.json` (M) | ✅ committed + landed | `a213c2b`…HEAD; B-108…B-110 rows appended in this close |
| — | removed files | 🗑️ none — the batch moved code, no file was deleted (trigger B2 not fired, `PLAN.md` §Triggers) | — |

- **Found before the batch:** none — no tracked file was modified when the batch began (the tree opened clean at `d8cf942`, the committed pre-batch tip; `git status --porcelain` is empty at this close apart from this artifact's own write).

**Conditional gate verdicts:** if any gate this batch ran closed as *"once items 1–N land this is a PASS/MERGE"*, list each item and its discharge **verified by re-reading the artifact** — not by trusting that the corrective pass ran.

| Conditional item | Discharged? | Verified how |
|---|---|---|
| PDR conditions C1–C9 (PDR sealed `approved with conditions`) | ✅ | DDR B8 table re-reads each against its proving line — e.g. C1 → `tests/test_inc9c.py:114`; C4 → pinned sha256 == `tests/test_mod_dispatch.py:60`; C9 → `evidence/ddr-c9-allowlist-mutation.transcript` executed at the DDR (`DDR-2026-10-09-modular-batch.md:64-74`) |
| DDR conditions D-C1..D-C4 + QA-MED-1/QA-MED-2 (DDR re-review `approved with conditions`) | ✅ | Discharged at increment 023 (`69676cf`), re-read at DDR B8: D-C1 → corrected F4 row `docs/ARCHITECTURE.md:199` matching `tests/test_mod_compat.py:54`; D-C2 → `:135` + narrowed checker `tests/test_mod_deps.py:185`; D-C3 → `:135` + `tests/test_mod_deps.py:252`/`:303`; QA-MED-2 → re-summed gate at `acbd087`, `evidence/ddr-acbd087-full-suite.transcript` (`DDR-2026-10-09-modular-batch.md:75-80`) |

### Evidence checklist — architect + qa-reviewer
> Attach both co-authors' completed evidence checklists (items in their agent files), each ✓/✗ with one-line evidence.

- **architect:** PENDING — the orchestrator dispatches the co-author pass at the close gate (P4 was under qa review at this close).
- **qa-reviewer:** PENDING — same dispatch.
