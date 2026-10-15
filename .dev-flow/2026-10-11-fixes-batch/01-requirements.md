# Requirements Document — mapper — Batch 2026-10-11-fixes-batch

> **Artifact language.** English (`state.json` `language: en`). `shall` is the only normative keyword and appears only inside HLR/LLR statements.

> **Owed in.** `core` ✓ · `full` ✓

> **Reserved field names** (parsed literally, never translated):
> `Validation` · `Acceptance test(s)` · `Boundary catalog` · `Negative control` · `Premise evaluation` · `Fork preconditions` · `Ledger` · `Requirement` · `⏸ DEFER`

---

## 1. Introduction

### 1.1 Purpose
Fix four shipped defects reproduced at P0 on `master` `5a991c6` (`spike/intake.md`): B-115 (an empty slug becomes node `n`; an empty CSV parent cell is read as a reference to `n`), B-116 (a CSV that lists a child before its root is refused as a cycle), B-117 (a forest map's root changes on save + reload), B-127 (the roles screen runs three git calls on the UI thread at mount); and, as a test-only increment, two test-hygiene carries: B-110 (`exporting.py`'s own `pan_extent` reader has no patched test) and B-113 (the leak-exception registry of `tests/test_inc9c.py` is keyed too coarsely).

### 1.2 Scope
In: `mapper/mermaid.py` (`slugify`, `dump`), `mapper/import_csv.py` (`preview_csv`), `mapper/store.py` (a stale docstring only), `mapper/screens/roles.py` (load path), and the tests and pins that encode the old behaviour; for increment 004, `tests/test_export_state.py` and `tests/test_inc9c.py` only (0 source files). Unicode ids and labels: `slugify` today keeps any `\w` character (so `niño` stays `niño`); that behaviour is unchanged and is the whole Unicode scope, pinned by one non-regression arm of AT-084 (LED-2026-10-11-fixes-batch.11); anything beyond it (transliteration, normalisation) is out of scope. Out: any visible loading chrome for the roles screen (needs a prototype verdict first — operator ruling R4), `parse`'s root rule, the model's `add_node` root stamp, `reqharness/identity.py` (not needed: the cache lives in the screen), B-118/B-120/B-124..B-126.

### 1.3 Definitions, acronyms, abbreviations
| Term | Definition |
|------|------------|
| parentless row | a CSV row with no parent edge after the second pass |
| parked | a node whose title carries the `? ` prefix because its parent is missing or unknown |
| forest | a graph with more than one parentless node |
| discovery | the three git reads of the roles screen: `identity.repo_root`, then `identity.read` (`config --get user.name`, `config --get user.email`) |
| facts | the `(top, who)` pair a discovery returns |

### 1.4 References
`spike/intake.md` (four reproductions) · `PLAN.md` · `.dev-flow/2026-10-10-csv-safety-batch` (rulings R11, LLR-CSV.1.3, LLR-CSV.2.1) · `.dev-flow/2026-10-10-perf-batch` (LLR-PERF.2.2, the `dump` edge-visit budget) · `.dev-flow/2026-10-11-reqharness-batch` (format; B-127's origin as a DDR residual).

### 1.5 Document overview
§2 context and the executed premise table · §3 six HLRs · §4 fourteen LLRs and the Information Flow Contract · §5 validation · §6 appendices · ledger in `01-requirements-ledger.md`.

---

## 2. Overall description

### 2.1 Product perspective
`slugify` and `dump`/`parse` are the map text codec (`mapper/mermaid.py`); `preview_csv` feeds the import preview and the save-as flow, which write through `MapStore.save` and re-open through `MapStore.load`. `RolesScreen` is the ReqHarness roles surface (reqharness batch).

### 2.2 Product functions
Unchanged functions, repaired: CSV import, map save + reload, roles screen mount and resume.

### 2.3 User characteristics
One operator in a terminal; spreadsheets exported in any row order; repositories whose git may be slow.

### 2.4 Constraints
All strings English; colours from `mapper/darkside.py`; keys from `mapper/keymap.py`; **no new visible state** (R4). At most 4 source files per increment. `dump` keeps its edge-visit budget of at most 2E + 4 per call (LLR-PERF.2.2). No file in this batch names an operator, an account or a home path.

### 2.5 Assumptions and dependencies
Textual thread workers (`@work(thread=True)`) are the in-repo pattern (premise 6); the roles screen hands its result back through the worker's return value and `on_worker_state_changed`, not `call_from_thread` (R7). `MapperApp(tmp_path)` + `run_test` + `pilot.press` is the test driver.

### 2.6 Source user stories

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-FX-001 | As an operator importing a spreadsheet, I want a blank parent cell to mean "top-level row" and an unreadable id to get a row id, so that my rows are never re-parented under a phantom node `n`. | B-115 | READY |
| US-FX-002 | As an operator importing an unsorted spreadsheet, I want the root to be the row with no parent wherever it sits, so that listing a child first never reads as a cycle. | B-116 | READY |
| US-FX-003 | As an operator saving a map that has several top-level nodes, I want the same root after reload, so that focus and canvas state keyed to the root survive a save. | B-117 | READY |
| US-FX-004 | As an operator opening the roles screen, I want the screen never to freeze on a slow git, so that the app stays responsive while the repository is read. | B-127 (non-visual alternative) | READY |
| US-FX-005 | As a maintainer, I want a regression in `exporting.py`'s own `pan_extent` read to turn a test RED, so that the export concern is guarded as the pan concern already is. | B-110 | READY |
| US-FX-006 | As a maintainer, I want each excused notify-leak keyed to its exact call site, so that one excuse can never silently cover a second leak in the same file. | B-113 | READY |

#### Refinement log (one block per story)

**US-FX-001 — blank parent is a root candidate**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = operator importing CSV · outcome = rows with a blank parent cell are root candidates, never children of `n`; an id with no slug characters imports as `row-N` · why = silent re-parenting, and a `n→n` self-edge that save refuses · out of scope = any change to the `? ` copy.
- **Feasibility (E, S):** path = `slugify` returns `""`, `preview_csv` reads blank before slugifying · unknowns = none · fits one batch = yes.
- **Evaluability (T):** When the operator imports `alpha,Alpha,` / `beta,Beta,` / `!!!,Bang,`, the preview shows no node `n`, three rows under one root, ids `alpha`, `beta`, `row-1`.
- **Open questions:** none.
- **Classification:** `READY`.

**US-FX-002 — root independent of row order**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = operator · outcome = `child,Child,root` before `root,Root,` imports as root `root`, one edge `root→child`, and saves · why = legitimate unsorted exports are unimportable · out of scope = changing how a genuine cycle is named.
- **Feasibility (E, S):** path = choose the root after the edges exist · fits = yes (shares the file with US-FX-001 → one increment).
- **Evaluability (T):** When the operator imports the child-first CSV and presses `s`, the map saves and re-opens with root `root`.
- **Open questions:** none.
- **Classification:** `READY`.

**US-FX-003 — root survives save + reload**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = operator · outcome = `graph TD / a / b --> c` with declared root `a` re-opens with root `a` after a save · why = focus and canvas state keyed to the root break · out of scope = changing `parse`.
- **Feasibility (E, S):** path = writer-side: `dump` emits the declared root's line first when text order would otherwise elect another, inside the existing two edge passes · fits = yes.
- **Evaluability (T):** When a forest map with root `a` is saved and re-opened through the store, the operator sees root `a`.
- **Open questions:** none.
- **Classification:** `READY`.

**US-FX-004 — roles screen never freezes on git**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = operator · outcome = the three git reads run on a worker thread; the screen paints when they return · why = ≈ 30 s worst-case freeze · out of scope = visible loading chrome, perf items.
- **Feasibility (E, S):** path = `_discover` in a Textual thread worker; file reads stay on the UI thread (they are not git) · fits = yes.
- **Evaluability (T):** When the operator presses `R` and git is slow, the app keeps answering and the screen paints the matrix only when git returns.
- **Open questions:** silent keys before the first load (decided, §6.3).
- **Classification:** `READY` (non-visual alternative).

**US-FX-005 — export's own `pan_extent` read is guarded**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = maintainer · outcome = a spy on `mapper.screens.map.exporting.pan_extent` records the read made by a real export · why = the suite's only patch site (`tests/test_en8.py:66`) bites `panning.py`, so a re-bind in `exporting.py` is invisible · out of scope = any product change, extending `PATCH_SURFACE`.
- **Feasibility (E, S):** path = one async test in the export concern's home file · fits = yes (0 source files).
- **Evaluability (T):** When `exporting.py` is re-bound to read `layered.pan_extent`, the new node is RED and the rest of the suite is GREEN.
- **Open questions:** none.
- **Classification:** `READY`.

**US-FX-006 — one leak excuse covers one site**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = maintainer · outcome = `LEAK_EXCEPTIONS` is keyed `(file, lineno, expr)` and a second `str(exc)` in an excused file is reported · why = the coarse `(file, expr)` key absorbs a genuine second leak · out of scope = any `mapper/` change; the backlog row names `tests/test_inc9q.py` wrongly, the registry is in `tests/test_inc9c.py` (corrected in `BACKLOG.md`).
- **Feasibility (E, S):** path = retype three dict keys, change two membership expressions, add one negative control · fits = yes (0 source files).
- **Evaluability (T):** When a second `str(exc)` notify site appears in `home.py`, the census names it as undeclared.
- **Open questions:** none.
- **Classification:** `READY`.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| 1 | The next free acceptance-test number is `AT-084`. | low | ✅ TRUE | `grep -ohE "\bAT-[0-9]+" REQUIREMENTS.md tests/*.py \| sort -u \| tail -2` → `AT-082`, `AT-083`; no `AT-084` or higher in the reqharness or csv-safety batch records. New: `AT-084`…`AT-087`. | relied on (AT numbering) |
| 2 | `slugify` has exactly three production callers; one already tolerates an empty result. | low | ✅ TRUE | `grep -rn "slugify" --include=*.py mapper` → `import_csv.py:59` (row id), `import_csv.py:70` (parent cell), `screens/map/editing.py:115` (`base = slugify(title) or "n"`); tests: `tests/test_mermaid.py:12` (`slugify("---") == "n"`) is the only pin. | relied on (LLR-FX.1.1) |
| 3 | A `dump` that hoists the declared root only when text order would elect another, computed inside the existing two edge passes, leaves all 8 dump goldens, the 2 inline arms, the AT-076 bytes and the 2E + 4 visit budget intact. | high | ✅ TRUE | Executed (scratch copy of the tree, rule implemented there, not in the worktree): `pytest -p no:cacheprovider tests/test_perf_dump.py tests/test_csv_safety_store.py tests/test_mermaid.py` → `15 passed, 1 failed` (the failure is the `slugify("---") == "n"` pin, LLR-FX.1.1); `test_dump_counted_ops_scaling_ratio`, `test_dump_fixture_goldens`, `test_at_076_real_save_dump_budget` pass. A first draft that re-walked the edges failed all three (`36000 > 2*6000 + 4`), which is why the rule reuses pass 1's bookkeeping. One inline arm needed a fixture line (see premise 4). Every parentless node chosen as root in `a` / `b-->c`, `b-->c` / `a-->d`, and `x` / `b-->c` / `a[Alpha]-->d` / `z` re-parses to itself: 8 of 8 (old rule: 3 of 8). | relied on (LLR-FX.3.1; C-39) |
| 4 | The inline `orphan-order` arm of `test_dump_fixture_goldens` builds a forest whose declared root (`zeta`, the first node added) is not the first parentless node of the text, so its fixture moves; its expected bytes do not. | high | ✅ TRUE | `tests/test_perf_dump.py:130-137`: nodes `zeta`, `alfa`, `root`, `kid`, edge `root→kid`, no `root_id` set → root `zeta`. With the hoist and no fixture change the arm fails (`orphan-order: dump bytes drifted`, executed); with `ordered.root_id = "root"` added the same expected bytes `graph TD\n    root[raiz] --> kid\n    zeta\n    alfa\n` pass (executed). `dangling-solo` (`solo` has only a dangling edge, expected `graph TD\n`) passes because a root absent from the written text is never hoisted. | relied on (LLR-FX.3.1, LLR-FX.3.2; the one pin that moves) |
| 5 | The shipped fixtures are single-root trees, so none drifts on save (the intake's "legacy.mmd is a forest" is wrong). | low | ✅ TRUE | `parse(open('fixtures/legacy.mmd').read())` → parentless `['erp']`; `fixtures/{anidado,truncado}.mmd` and `maps/legacy.mmd` re-parse to the same root with unchanged bytes. The only forest pin is the in-test `a` / `b --> c` of `tests/test_csv_safety_store.py:195`. | relied on (corrects intake; LED-2026-10-11-fixes-batch.6) |
| 6 | A thread worker (`@work(thread=True)`) is the repository's existing pattern. | low | ✅ TRUE | `mapper/screens/repo.py:259` `@work(thread=True, exit_on_error=False)`; `:267` `self.app.call_from_thread(...)`. | relied on for the worker only (LLR-FX.4.1); the hand-back is the worker's return value (R7, LED .14), not `call_from_thread`, which would risk an exit-time hang |
| 7 | The CSV rule of LLR-FX.1.* / FX.2.* fixes all B-115/B-116 reproductions, keeps a genuine cycle named and moves no existing test but the slugify pin. | high | ✅ TRUE | Executed (scratch copy): empty parents → nodes `alpha, beta, row-1`, edges `alpha→beta, alpha→row-1`, no `n`; `N` root + `k,K,n` → one edge `n→k`, no self-edge; child-first → root `root`, edge `root→child`, cycle `None`; grandchild-first → root `a`; ring of three → cycle `['a','b','c','a']`; ring beside root `r` → root `r`, cycle `['a','c','a']`. Permutations of `r` / `a←r` / `b←r` / `c←a`: 24 of 24 give one outcome with root `r` (base tree: 6 of 24, 4 distinct outcomes). Suite over 14 files (`test_import_csv`, `test_csv_safety_preview`, `test_csv_safety_store`, `test_mermaid`, `test_gate2`, `test_inc9`, `test_inc9c`, `test_inc9m`, `test_inc9n`, `test_key_dispatch`, `test_repair_cycles`, `test_repair_fields`, `test_perf_dump`, `test_model`): base 490 passed; patched 486 passed + the 5 failures above/below accounted (slugify pin; 3 `test_perf_dump` before the budget-safe rewrite, 0 after; 1 base-only failure from the scratch copy lacking `.dev-flow/`). | relied on (LLR-FX.1.*, FX.2.*) |
| 8 | The roles load makes exactly three git calls, sequentially, on the calling thread today, and moving them to a worker keeps the screen's tests green once the helper waits for workers. | high | ✅ TRUE | Intake probe and a re-run with a gated `identity._run_git`: calls `('rev-parse','--show-toplevel')`, `('config','--get','user.name')`, `('config','--get','user.email')`; base: the first runs on the main thread and blocks the mount (`AssertionError: gate never released` after the 5 s guard); prototype: all 3 recorded with `is_main_thread == False`, surfaces empty and inert while gated, `chain  ✓ verified  viewer subject (admin)` after release. `pytest tests/test_roles_screen.py` with `_open_roles` ending in `await app.workers.wait_for_complete(); await pilot.pause()` → `22 passed`; without it 6 and 12 failures on two runs (timing). | relied on (LLR-FX.4.*; increment 003 moves `_open_roles`) |
| 9 | The only patch site of `pan_extent` is `tests/test_en8.py:66` and it targets `mapper.screens.map.panning`; `exporting.py` has its own module-global reader. | low | ✅ TRUE | Read-only spike (B-110/B-113 scoping): `exporting.py:13` imports, `:203` reads; `tests/test_en8.py:66` is the only `monkeypatch.setattr(... pan_extent ...)`; `tests/test_mod_compat.py:59` maps `pan_extent` to `panning` only; `pytest tests/test_en8.py -k unlaid_out` → 1 passed. | relied on (LLR-FX.5.1) |
| 10 | `LEAK_EXCEPTIONS` is keyed `(file, expr)` in `tests/test_inc9c.py`, not in `tests/test_inc9q.py`, and `_notify_leaks()` already returns `(path, lineno, expr)`. | low | ✅ TRUE | Spike: `tests/test_inc9c.py:266` the dict, `:291` `leaks.append((path, node.lineno, expr))`, `:299` and `:305` drop the line; `pytest tests/test_inc9c.py -k sec_f1` → 13 passed. `tests/test_inc9q.py:340,508` hold only exact-toast pins. | relied on (LLR-FX.6.1; corrects BACKLOG B-113) |

- **Premise evaluation:** 10 premise(s) · ✅ TRUE 10 / ❌ FALSE 0 / ❓ UNDECIDABLE 0.

### 2.8 Fork preconditions (C-52) — MANDATORY, and the declared empty when the batch does not fork

| # | Condition (`C-52`) | Discharged? | The executed evidence |
|---|---|---|---|
| 1 | **Frozen contract** — no shared interface is touched inside a lane | ✅ | One lane. `slugify`'s return domain widens by one value (`""`); its three callers are enumerated in premise 2 and all are in-batch or already tolerant. |
| 2 | **Disjoint FILE sets**, not just modules | ✅ | One lane; increments 001 and 002 both touch `mapper/mermaid.py`, sequentially, never concurrently. |
| 3 | **Crossed reverse census** — family B per lane | ✅ | Premise 2's grep is the census for `slugify`; `grep -rln "import_csv\|preview_csv" mapper tests` → `mapper/import_csv.py`, `keymap.py`, `model.py`, `screens/home.py` and 11 test files, all in the suite run of premise 7. |
| 4 | **One owner of the trunk** | ✅ | This document, the ledger and `PLAN.md` are written only by the P1 unit. |

- **Fork preconditions:** none — this batch runs one lane (declared empty; the four conditions hold trivially, evidenced above).

---

## 3. High-level requirements (HLR)

### HLR-FX.1 — A blank parent cell is no parent, and an empty slug is never `n`
- **Traceability:** US-FX-001
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.2, LED-2026-10-11-fixes-batch.9, LED-2026-10-11-fixes-batch.11, LED-2026-10-11-fixes-batch.16
- **Statement:** When a CSV is imported, the system shall read a blank or whitespace-only parent cell as "no parent" so the row is a root candidate and is never linked to a node named by the slug of an empty string; and when a label has no slug characters, the system shall not substitute the id `n`: a row id with no slug characters shall import under the next `row-N` id.
- **Rationale (informative):** B-115. The empty parent cell was slugified to `n`; every top-level row was parked and attached to `n`, ids with no slug characters collided on `n`, and a root literally named `N` saved as a self-cycle.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_csv_import.py tests/test_mermaid.py`
- **Numeric pass threshold:** 0 failed; on the three-row empty-parent CSV the imported node ids are exactly `{alpha, beta, row-1}` (0 nodes named `n`) and 0 edges have `n` as parent or child; a non-ASCII label arm (`niño,Niño,` imports under the id `niño`, exactly what `slugify` returns on the base tree: 0 behaviour change) passes.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the import preview of the empty-parent CSV paints no node `n`; the first row is the root and carries no `? ` prefix; the unreadable id appears as `row-1`.
  - **Shipped surface:** `preview_csv` through the real `i` import key and the import preview screen.
  - **Acceptance test(s):** AT-084 (the painted preview shows titles, not ids: `row-1` is asserted through `preview_csv`, the title `Bang` on the painted frame — code-review note F2)
  - **Boundary catalog (QC-3):** ☑ empty (blank and whitespace-only parent cell) ☑ boundary (parent cell of punctuation only; root literally named `N`) ☑ invalid (id of punctuation only) ☑ boundary (non-ASCII word characters: unchanged from today) ☐ error (n/a — no error path: a missing parent already parks)
  - **Negative control:** M-FX1 (slugify returns `"n"` again) and M-FX2 (blank parent cell slugified again) — each executed RED at increment 001.

### HLR-FX.2 — The CSV root is chosen by parentage, not by row order
- **Traceability:** US-FX-002
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.3, LED-2026-10-11-fixes-batch.9, LED-2026-10-11-fixes-batch.16
- **Statement:** When a CSV is imported, the system shall choose the root as the first row, in file order, that has no parent edge and was not parked for a missing parent, so that no permutation of the rows of a valid tree changes the node set, the edge set or the root; and a genuine cycle among the rows shall still be reported by the cycle's node names.
- **Rationale (informative):** B-116. The first row was always the root; a later-declared parentless row was then attached under it, closing a two-cycle that save refuses.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_csv_import.py tests/test_csv_safety_preview.py tests/test_import_csv.py`
- **Numeric pass threshold:** 0 failed; `child,Child,root` / `root,Root,` yields `root_id == "root"`, edges `[("root","child")]`, `find_cycle() is None`; all 24 permutations of a four-row tree yield one node set, one edge set and one root.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the child-first CSV imports, saves under a typed name, and re-opens as a two-node tree rooted at `root`; the cycle sentence does not appear.
  - **Shipped surface:** the `i` import, the preview and the `s` save in the real app, then `MapStore.load`.
  - **Acceptance test(s):** AT-085
  - **Boundary catalog (QC-3):** ☑ boundary (child first; grandchild first; two parentless rows; parentage from the `depth` column alone) ☑ invalid (ring of three rows; ring beside a root; self-parent) ☑ empty (no parentless row at all) ☐ error (n/a — covered by the ring arms)
  - **Negative control:** M-FX4 (root = first row again) and M-FX5 (parked rows allowed as root) — each executed RED at increment 001.

### HLR-FX.3 — A map's root survives save and reload
- **Traceability:** US-FX-003
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.4, LED-2026-10-11-fixes-batch.6
- **Statement:** When a graph is dumped to text, the system shall write the declared root so that `parse` of that text recovers the same root, while the text of every graph whose root is already elected by text order stays byte-identical to today's and the dump still iterates the edges no more than 2E + 4 times.
- **Rationale (informative):** B-117. `dump` wrote edges before parentless nodes and `parse` takes the first parentless node in text order, so a forest re-opened with the first edge's parent as root.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_forest_root.py tests/test_csv_safety_store.py tests/test_perf_dump.py`
- **Numeric pass threshold:** 0 failed; for each parentless node chosen as root in the three forest shapes of premise 3, `parse(dump(g)).root_id` equals it (8 of 8; old rule 3 of 8); 8 of 8 dump goldens, the 2 inline arms and the AT-076 bytes pass byte-identical; the AT-076 visit count stays ≤ 2E + 4.
- **Priority:** high
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** a forest map saved through the store re-opens with the root it had; the saved `.mmd` names the root first.
  - **Shipped surface:** `MapStore.save` then `MapStore.load` (the path the app's save and open use).
  - **Acceptance test(s):** AT-086
  - **Boundary catalog (QC-3):** ☑ boundary (root is an orphan; root is an edge parent not first in edge order) ☑ empty (empty graph; single node) ☑ invalid (dangling edge, including a root whose only edge dangles) ☐ error (n/a — `dump` has no error path)
  - **Negative control:** M-FX6 (hoist removed) and M-FX7 (root line always written) — M-FX7 reddens the byte-stability arms; each executed RED at increment 002.

### HLR-FX.4 — The roles screen reads git off the UI thread without changing what it shows
- **Traceability:** US-FX-004
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.5, LED-2026-10-11-fixes-batch.7, LED-2026-10-11-fixes-batch.8, LED-2026-10-11-fixes-batch.10, LED-2026-10-11-fixes-batch.14, LED-2026-10-11-fixes-batch.16
- **Statement:** When the roles screen mounts or resumes, the system shall perform its git discovery on a worker thread and shall paint only after it returns; until the first discovery returns the screen shall paint no status, matrix, band or hint and shall treat every editing key (cursor keys, `space`, `a`, `r`) as inert while `Esc` keeps its existing action; a result that returns after the screen has been popped shall be discarded; once it has returned, behaviour shall equal today's, with keypress-time reloads reading disk (chain, pending, config) but running no git.
- **Rationale (informative):** B-127. Three sequential `subprocess.run` calls (10 s timeout each) blocked the UI thread: ≈ 30 s worst case. Operator ruling R4: the non-visual alternative — no new loading chrome.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_roles_thread.py tests/test_roles_screen.py`
- **Numeric pass threshold:** 0 failed; with a gated `identity._run_git`, 3 of 3 recorded git calls run off the main thread; with `Esc` pressed while the gate is closed and the gate then released, 0 exceptions, 0 notifications and 0 paints reach the popped screen; with the gate closed the four painted surfaces (`#roles-status`, `#roles-body`, `#roles-band`, the hint) are empty and keys `j`, `space`, `a` change none of them, raise no notification and write 0 bytes; after release `#roles-status` carries `chain` and `viewer subject`; the 22 existing roles-screen nodes pass.
- **Priority:** medium
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** pressing `R` with a slow git returns control immediately; the screen is blank and inert until git returns, then paints exactly as before.
  - **Shipped surface:** the real app: `R` from home, `pilot.press` keys, the screen's four Statics.
  - **Acceptance test(s):** AT-087
  - **Boundary catalog (QC-3):** ☑ boundary (keys before the first load) ☑ empty (no repo: the `no repo` state still paints after the worker) ☑ error (a discovery that raises one of the four named exception types degrades to the named `no repo` state; any other exception propagates) ☑ boundary (screen popped before the worker returns) ☐ invalid (n/a)
  - **Negative control:** M-FX8 (discovery run synchronously on mount), M-FX9 (inert guard removed), M-FX10 (keypress reload re-runs git), M-FX11 (stale result applied), M-FX13 (late result applied to a popped screen), M-FX14 (the discovery catch removed) — each executed RED at increment 003.

### HLR-FX.5 — The export concern's own `pan_extent` read is guarded by a test
- **Traceability:** US-FX-005
- **Ledger:** LED-2026-10-11-fixes-batch.12
- **Statement:** When a layered map is exported, the test suite shall observe the extent being read through the `pan_extent` name of `mapper.screens.map.exporting`, so that rebinding that module to another reader turns a test RED.
- **Rationale (informative):** B-110. The only patch site (`tests/test_en8.py:66`) bites `panning.py`; `exporting.py:13`/`:203` is a second reader nothing patches, a deliberate gap recorded at DDR B1(b).
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_export_state.py::test_exporting_reads_pan_extent_through_its_own_module_global`
- **Numeric pass threshold:** 0 failed; the spy installed on `mapper.screens.map.exporting.pan_extent` records ≥ 1 call during one real export, and the export artifact `m.svg` exists (positive control: a zero count cannot be vacuous); under mutation M-FX15 the node fails and the other nodes of `tests/test_export_state.py` and `tests/test_en8.py` stay green.
- **Priority:** low
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** the export produces `m.svg` and the spy's call count is above zero.
  - **Shipped surface:** the real app: `MapperApp(tmp_path)`, a layered map, the `e` key.
  - **Acceptance test(s):** AT-088
  - **Boundary catalog (QC-3):** ☑ boundary (layered renderer is the one that consumes `pan_extent`) ☐ empty (n/a) ☐ invalid (n/a) ☐ error (n/a)
  - **Negative control:** M-FX15 (rebind `exporting.py` to `layered.pan_extent`, the same function object through another name) — executed RED at increment 004, with the sha256 restore check.

### HLR-FX.6 — One leak excuse covers one call site
- **Traceability:** US-FX-006
- **Ledger:** LED-2026-10-11-fixes-batch.13
- **Statement:** When the notify-leak census compares a flagged interpolation with the declared exceptions, the test suite shall key each exception by file, call-site line and flagged expression, so that a second flagged site in an excused file is reported as undeclared.
- **Rationale (informative):** B-113. The registry keyed `(file, expr)` and dropped the line the census already computed; one excuse silently covered any later site with the same expression.
- **Validation:** `test`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_inc9c.py -k "sec_f1 or at_089"`
- **Numeric pass threshold:** 0 failed; the 13 existing `sec_f1` nodes pass with the three excuses retyped to `(file, lineno, expr)` at the call lines `home.py:175`, `screens/map/screen.py:214`, `common.py:213`; the negative control reports exactly the second record `("mapper/screens/home.py", 412, "str(exc)")` as undeclared.
- **Priority:** low
- **Acceptance (black-box) — the user-verified outcome (the WHAT):**
  - **Observable outcome:** a planted second `str(exc)` record in `home.py` is listed as undeclared by the census comparison.
  - **Shipped surface:** the leak census of the test suite (`_notify_leaks` consumers).
  - **Acceptance test(s):** AT-089
  - **Boundary catalog (QC-3):** ☑ boundary (second site, same file and expression) ☑ empty (no leaks: unchanged) ☐ invalid (n/a) ☐ error (n/a)
  - **Negative control:** M-FX16 (both consumers key `(file, expr)` again) — the AT-089 node and the staleness consumer fail; executed RED at increment 004.

---

## 4. Low-level requirements (LLR)

### LLR-FX.1.1 — `slugify` returns the empty string when nothing survives
- **Traceability:** HLR-FX.1
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.2, LED-2026-10-11-fixes-batch.11
- **Statement:** The `slugify` function shall return `""` for a blank value or a value with no word characters instead of `"n"`, and its docstring shall say so; the one caller that wants a placeholder (`screens/map/editing.py`, `slugify(title) or "n"` followed by a uniqueness loop) shall keep working unchanged.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_mermaid.py::test_slugify_allows_hyphens tests/test_mermaid.py::test_slugify_returns_empty_when_nothing_survives`
- **Numeric pass threshold:** `slugify("") == ""`, `slugify("   ") == ""`, `slugify("---") == ""`, `slugify("!!!") == ""`; `slugify("Mi Hijo Nuevo") == "mi-hijo-nuevo"` and `slugify("a_b") == "a_b"` unchanged; `slugify("Niño") == "niño"` exactly as on the base tree (the Unicode scope is only what `slugify` already does; no new Unicode behaviour is specified). The pin `assert slugify("---") == "n"` (`tests/test_mermaid.py:12`) moves to `""` in the same increment (the only existing test that fails on the patched tree, premise 7).
- **Negative control:** M-FX1 — restore `value[:32] or "n"`; the new node fails on `"n" != ""` (the old pin would pass: that is why it moves).
- **Boundary catalog:** ☑ empty ☑ boundary (whitespace only, punctuation only, non-ASCII word characters kept) ☐ invalid (n/a — any string is accepted) ☐ error (n/a)

### LLR-FX.1.2 — The parent cell is read blank-first
- **Traceability:** HLR-FX.1
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.2
- **Statement:** The `preview_csv` function shall decide "no parent" from the stripped parent cell being empty, before any slugging; a non-blank cell whose slug is empty or names no row shall park the row (missing parent) exactly as an unknown id does; a blank cell shall neither create an edge nor park the row.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_csv_import.py::test_blank_parent_cell_is_a_root_candidate_not_a_reference_to_n tests/test_fixes_csv_import.py::test_punctuation_only_parent_cell_parks_the_row`
- **Numeric pass threshold:** 3 of 3 arms pass with 0 nodes named `n` and 0 self-edges; for rows `r,R,   ` / `k,K,r`: nodes `{r, k}`, edges `[("r","k")]`, title of `r` is `R` (no `? `); for `r,R,` / `k,K,!!!`: `k` titled `? K`, attached under `r`; for `N,N,` / `k,K,n`: edges `[("n","k")]`, `find_cycle() is None` (base: `[("n","n"),("n","k")]`, cycle `['n','n']`).
- **Negative control:** M-FX2 — compute `parent_id = slugify(cell)` and decide "has parent" from the slug. Once LLR-FX.1.1 lands (`slugify("") == ""`) a blank cell and an empty slug give the same edges, so M-FX2 is killed by the punctuation-before-root arm of `test_punctuation_only_parent_cell_parks_the_row`; M-FX2b (M-FX2 + M-FX1) is the blank-cell control (`r` titled `? R`). Amended after the increment-001 code review (finding F1).
- **Boundary catalog:** ☑ empty ☑ boundary (whitespace only) ☑ invalid (punctuation only) ☐ error (n/a)

### LLR-FX.1.3 — An id with no slug characters imports as `row-N`
- **Traceability:** HLR-FX.1
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.2, LED-2026-10-11-fixes-batch.6, LED-2026-10-11-fixes-batch.9, LED-2026-10-11-fixes-batch.17
- **Statement:** When a row's typed or title-derived id has an empty slug, the `preview_csv` function shall take the next value of the same `row-N` counter the empty-id path uses as the node id, shall keep the typed text as the `CsvRow.raw_id` it records for collisions and as the title fallback, and shall leave an exact `row-N` typed by the operator subject to the existing collision record. The counter is a single sequence shared by both paths and advances by exactly one for each row that takes a `row-N` id, whether the row's id cell was empty or had an empty slug; a row whose id cell is empty but whose title slugifies to a non-empty id takes that title id and does not advance the counter.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_csv_import.py::test_id_with_no_slug_characters_becomes_row_n tests/test_csv_safety_preview.py::test_preview_csv_records_collisions`
- **Numeric pass threshold:** `!!!,Bang,` imports as node `row-1` titled `Bang`; with no title it is titled `!!!`; the collision record's `raw_id` for it is `!!!`; two such rows get `row-1` and `row-2` (0 collisions); an empty id cell with a punctuation-only title (`,!!!,`) takes `row-1`, titled `!!!`; an empty-slug row immediately followed by an empty-id row with no title (`!!!,Bang,` / `,,`) take `row-1` and `row-2`; a title-derived id followed by an empty-id row with no title (`,Alpha,` then `,,`) imports ids `{alpha, row-1}` (the title id does not advance the counter, so the empty-id row takes `row-1`); an operator-typed `row-1` after an auto-assigned `row-1` is recorded in the collision record with `raw_id` `row-1` (it is not renumbered); the existing collision record for `a-b` / `A B` is unchanged.
- **Negative control:** M-FX3 — drop the fallback; the id stays `""` and the node-id assertion fails.
- **Boundary catalog:** ☑ empty (empty id and empty title) ☑ boundary (counter shared with the empty-id path; interleaved empty-slug and empty-id rows; typed `row-N` after an auto `row-N`) ☑ invalid (punctuation-only id) ☐ error (n/a)

### LLR-FX.2.1 — Root selection by parentage
- **Traceability:** HLR-FX.2
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.3, LED-2026-10-11-fixes-batch.9
- **Statement:** After the edges are built, the `preview_csv` function shall set `graph.root_id` to the first row in file order with no parent edge that was not parked for a missing parent; when every parentless row was parked it shall use the first parentless row; when no row is parentless it shall leave the first row as root; a parent edge is an edge built from either the `parent` column or the `depth` column, so a row given a parent by depth alone is neither parentless nor parked; and it shall then attach every other parentless row under that root and park it, as the current forest rule does.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_csv_import.py -k root`
- **Numeric pass threshold:** truth table (each cell executed in the scratch copy, premise 7): child-first → root `root`; grandchild-first (`c←b←a`) → root `a`, edges `{b→c, a→b}`; two parentless rows `x` / `y` with `child←y` → root `x`, `y` titled `? Y` and attached under `x`; all parents unknown → root = first row, titled `? A`; ring → root = first row (the cycle sentence names the ring); ring beside root `r` → root `r`; `depth` column only (blank `parent`): rows `a,A,,0` / `b,B,,1` / `c,C,,2` → root `a`, edges `{a→b, b→c}`, no title carries `? ` (the exact depth semantics are confirmed against `import_csv.py` at the increment-001 RED proof). 0 failures.
- **Negative control:** M-FX4 — leave `graph.root_id` as stamped by `add_node` (the first row); the child-first node fails (`root_id == "child"`). M-FX5 — allow a parked row to be root; the unknown-parent-before-root arm fails.
- **Boundary catalog:** ☑ empty (no parentless row) ☑ boundary (root last in file; root in the middle; parentage from `depth` alone) ☑ invalid (ring; self-parent) ☐ error (n/a)

### LLR-FX.2.2 — Attaching orphans never creates a cycle, and row order never changes the tree
- **Traceability:** HLR-FX.2
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.3
- **Statement:** The `preview_csv` function shall attach other parentless rows only under a root that has no parent edge, so the attach step adds no cycle, and shall leave rows that form a genuine cycle unattached so `Graph.find_cycle` still names them in the preview and in `MapStore.save`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_csv_import.py -k "permutation or cycle" tests/test_csv_safety_preview.py::test_cycle_csv_paints_the_neutral_cycle_sentence tests/test_csv_safety_preview.py::test_colliding_cyclic_csv_paints_the_collision_sentence`
- **Numeric pass threshold:** over `itertools.permutations` of the four rows `r` / `a←r` / `b←r` / `c←a`, 24 of 24 imports have the same node-id set, the same edge set and `root_id == "r"` (the set comes from the rule — every ordering — not from the code's current handling); `a,A,c` / `b,B,a` / `c,C,b` still gives cycle `['a','b','c','a']`; `r,R,` / `a,A,c` / `c,C,a` gives cycle `['a','c','a']`; the evidence CSV keeps its collision-first precedence.
- **Negative control:** M-FX4 reddens the permutation node: executed on the base tree, 6 of 24 orderings give root `r` and an acyclic graph (the 6 that start with `r`), 18 of 24 are RED, with 4 distinct outcomes.
- **Boundary catalog:** ☑ boundary (all orderings) ☑ invalid (rings, self-parent) ☐ empty (n/a — covered by LLR-FX.2.1) ☐ error (n/a)

### LLR-FX.3.1 — `dump` writes the declared root first, only when text order would elect another
- **Traceability:** HLR-FX.3
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.4, LED-2026-10-11-fixes-batch.6, LED-2026-10-11-fixes-batch.15
- **Statement:** The `dump` function shall, when `graph.root_id` names a node that appears in the text it writes, is not the child of a written edge, and is not the first parentless node of that text, write that root's declaration line (`    id` or `    id[label]`, the form the orphan pass uses) immediately after `graph TD` and drop the same line from the orphan block, and shall otherwise write the text it writes today; it shall derive the decision from bookkeeping kept inside its two existing passes over `graph.edges`, adding no pass; and the `parse` function shall not change.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_forest_root.py tests/test_perf_dump.py`
- **Numeric pass threshold:** the B-117 reproduction dumps to `graph TD\n    a\n    b --> c\n` (base: `graph TD\n    b --> c\n    a\n`) and re-parses with root `a`; every parentless node of the three forest shapes, set as root, re-parses to itself (8 of 8; base 3 of 8) with no duplicated declaration line for an orphan root; `tests/test_perf_dump.py` passes its 8 golden files and AT-076's bytes byte-identical and its visit bound `visits <= 2*E + 4`; single-root trees and the four shipped `.mmd` fixtures dump to the same bytes as before.
- **Negative control:** M-FX6 — delete the hoist; the reproduction re-parses with root `b`. M-FX7 — always write the root line; the `forest`, `wide6000` and fixture goldens drift (a different failure from M-FX6). M-FX12 — re-walk `graph.edges` to decide; the visit bound fails (`36000 > 12004`, executed on the first draft).
- **Disk effect (informative, PDR condition):** a map loaded from disk takes its root from `parse` (the first parentless node in text order), so for such a map the hoist does not fire on resave and the bytes are unchanged; the hoist fires only when the root was set in-session (CSV import, or `editing.py:221` after a root delete). B-117 stops future drift; it cannot repair a map that already drifted, because the declared root was never stored.
- **Boundary catalog:** ☑ empty (empty graph) ☑ boundary (single node; root already first; root an edge parent not first in edge order; root with a label) ☑ invalid (dangling edge; a root whose only edge dangles stays unwritten, as `dangling-solo` pins; a root id absent from nodes leaves the text unchanged) ☐ error (n/a)

### LLR-FX.3.2 — The pins that encoded the old order move with it
- **Traceability:** HLR-FX.3
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.4
- **Statement:** The `MapStore._check_round_trip` docstring shall stop claiming that a forest's root drifts on reparse and shall keep its node-set and edge-multiset comparison without adding a root comparison; the forest regression of the legacy-forest test shall assert that the root is unchanged after the reload; and the inline `orphan-order` arm of `test_dump_fixture_goldens` shall declare its root (`root`) so it keeps pinning orphan order with unchanged expected bytes.
- **Validation:** `inspection` + `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_csv_safety_store.py::test_save_accepts_legacy_forest_after_edit tests/test_perf_dump.py::test_dump_fixture_goldens`; `grep -n "root drifts\|R11" mapper/store.py` → 0 lines asserting drift.
- **Numeric pass threshold:** the first test gains `assert reloaded.root_id == loaded.root_id == "a"` and passes; `grep -c "root drifts" mapper/store.py` → 0; the second passes with its expected bytes unchanged (premise 4); `_check_round_trip` still raises `MapStoreError` on the three refusal arms of `tests/test_csv_safety_store.py` — 0 regressions in that file (15 passed in the premise-3 run).
- **Negative control:** M-FX6 reddens the new root assertion (`"b" != "a"`); a root comparison added to `_check_round_trip` is deliberately NOT specified (it would refuse maps that open today whose in-memory root is not parentless).
- **Boundary catalog:** ☑ boundary (forest after an edit; orphan order with a declared root) ☐ invalid (n/a) ☐ empty (n/a) ☐ error (n/a — refusal arms unchanged)

### LLR-FX.4.1 — Discovery runs on a worker thread, is caught narrowly, and is discarded after a pop
- **Traceability:** HLR-FX.4
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.5, LED-2026-10-11-fixes-batch.7, LED-2026-10-11-fixes-batch.8, LED-2026-10-11-fixes-batch.14, LED-2026-10-11-fixes-batch.18
- **Statement:** The `RolesScreen` shall run `identity.repo_root` and `identity.read` in a Textual thread worker started at mount and at resume, shall RETURN the `(top, who)` facts from the worker (no `call_from_thread`) and apply them on the UI thread in `on_worker_state_changed` when the worker state is SUCCESS, and shall run `_load`'s file reads (chain, pending, config, verdict) on the UI thread from those facts. The worker shall wrap the two `identity` calls in `try/except (OSError, ValueError, subprocess.SubprocessError, ValidationError)` (`ValidationError` = `mapper.reqharness.records.ValidationError`) and on any of those shall hand back the facts `(NO_REPO, None)`, which paint the existing `no repo` state with its existing copy; no other exception type is caught, so anything else is a defect and propagates. When the screen is popped before the worker returns, the screen shall cancel its workers on unmount and `on_worker_state_changed` (SUCCESS) shall check the generation of the worker that finished and that the screen `is_attached` before touching any widget, so the late result is discarded: no paint, no notification, no exception.
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_roles_thread.py::test_at_087_roles_screen_git_reads_run_off_the_ui_thread tests/test_fixes_roles_thread.py::test_roles_discovery_failure_degrades_to_no_repo tests/test_fixes_roles_thread.py::test_roles_popped_screen_discards_late_discovery`
- **Numeric pass threshold:** the gated `identity._run_git` records 3 calls, 3 of 3 with `threading.current_thread() is not threading.main_thread()`; the test finishes inside its 5 s gate guard (the base tree blocks the mount and trips the guard); with `identity.repo_root` replaced by a monkeypatched function that raises each of `OSError`, `ValueError`, `subprocess.SubprocessError`, `ValidationError` in turn, 4 of 4 arms paint `no repo`; with it raising `RuntimeError` the exception is not swallowed (the node asserts it surfaces through the worker, `exit_on_error` left at its default); with `Esc` pressed while the gate is closed and the gate then released, 0 exceptions, 0 notifications, 0 paints on the popped screen and the app still answers a following key.
- **Negative control:** M-FX8 — call `_discover` directly in `on_mount`; the call is recorded on the main thread and the node fails. M-FX13 — drop the generation and `is_attached` checks in `on_worker_state_changed`; the popped-screen node fails (exception or paint on the dead screen). M-FX14 — remove the `try/except`; the four degradation arms fail. The failure seam in the tests is a monkeypatched function on `identity.repo_root` (and, for the `read` arm, `identity.read`) that raises the chosen type; no production seam is added.
- **Boundary catalog:** ☑ boundary (mount; resume; screen popped before the worker returns) ☑ empty (no repo: facts `(NO_REPO, None)` degrade to the named state) ☑ error (a discovery that raises one of the four named types is caught and the screen shows `no repo`; any other type propagates) ☐ invalid (n/a)

### LLR-FX.4.2 — Nothing wrong is painted while loading; the latest discovery wins
- **Traceability:** HLR-FX.4
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.5, LED-2026-10-11-fixes-batch.7
- **Statement:** Until the first discovery returns, the `RolesScreen` shall leave `#roles-status`, `#roles-body`, `#roles-band` and the hint line as composed (empty) and shall not paint the default `no repo` snapshot; on resume it shall keep the previous paint until the new discovery returns; and it shall apply only the result of the most recently started discovery; a result that arrives after the screen was popped is never applied (LLR-FX.4.1).
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_roles_thread.py::test_roles_paints_nothing_until_discovery_returns tests/test_fixes_roles_thread.py::test_roles_latest_discovery_wins`
- **Numeric pass threshold:** with the gate closed, `_plain(screen, "roles-status") == ""`, the body and band content are empty, `HintLine.text == ""` (4 of 4 surfaces); a first discovery released after a second started changes nothing (generation guard): the final paint equals the second result.
- **Negative control:** M-FX11 — drop the generation check; the late first result overwrites the second and the node fails.
- **Boundary catalog:** ☑ empty (before first load) ☑ boundary (mount then immediate resume) ☐ invalid (n/a) ☐ error (n/a)

### LLR-FX.4.3 — Keys pressed before the first load are inert
- **Traceability:** HLR-FX.4
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.5, LED-2026-10-11-fixes-batch.10, LED-2026-10-11-fixes-batch.16
- **Statement:** Until the first discovery returns, the cursor keys, `space`, `a` and `r` of the `RolesScreen` shall do nothing observable: no repaint, no hint, no notification, no write; `Esc` shall keep its existing action; and until the first facts arrive the key bar shall show only the navigation keys and `Esc`, none of the edit keys (`space`, `a`, `r`), so the screen advertises no key that does nothing (subtraction of existing chrome, no new string, glyph or colour; R8).
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_roles_thread.py::test_roles_keys_before_first_load_are_inert`
- **Numeric pass threshold:** after `j`, `space`, `a`, `r` with the gate closed the four surfaces equal their pre-key value, `list(app._notifications) == []`, and the `roles.yml` and `reqharness/pending/` digests are unchanged (0 bytes written); `Esc` pops the screen; the painted key bar with the gate closed contains none of the edit-key labels and contains the navigation and `Esc` labels, and after release it equals today's key bar (read from the painted frame, not from a call argument).
- **Negative control:** M-FX17 — leave the key bar unconditional; the painted key bar with the gate closed still carries the edit keys and the node fails. M-FX9 — remove the guard; `space` paints the `no repo` hint on a repository that has one and the node fails (executed in the scratch copy: without the guard the keys changed the painted hint).
- **Boundary catalog:** ☑ boundary (each of the five key families) ☐ empty (n/a) ☐ invalid (n/a) ☐ error (n/a)

### LLR-FX.4.4 — Keypress-time reloads read disk and run no git
- **Traceability:** HLR-FX.4
- **Ledger:** LED-2026-10-11-fixes-batch.1, LED-2026-10-11-fixes-batch.5
- **Statement:** After the first discovery, `_load` called from `space`, `a` and `r` shall reuse the cached facts and shall make 0 git calls, while still re-reading the chain, pending requests and config from disk so the RHFIX6B freshness arms hold.
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_fixes_roles_thread.py::test_roles_keypress_reload_runs_no_git tests/test_roles_screen.py`
- **Numeric pass threshold:** the recorded git-call count after pressing `space` and `a` equals the count before (3 → 3); the 22 nodes of `tests/test_roles_screen.py` pass with `_open_roles` ending in `await app.workers.wait_for_complete(); await pilot.pause()` (premise 8; `test_rhfix6b_admin_revoked_on_disk_refuses_a_at_keypress` and `…granted_on_disk_allows_a_at_keypress` among them).
- **Negative control:** M-FX10 — make the keypress reload call `_discover`; the count rises above 3 and the node fails.
- **Boundary catalog:** ☑ boundary (disk changed mid-session) ☑ error (the writer `OSError` arms already in the file) ☐ empty (n/a) ☐ invalid (n/a)

### LLR-FX.5.1 — A spy on `exporting.pan_extent` sees the export's read
- **Traceability:** HLR-FX.5
- **Ledger:** LED-2026-10-11-fixes-batch.12
- **Statement:** The test `test_exporting_reads_pan_extent_through_its_own_module_global` shall patch `mapper.screens.map.exporting.pan_extent` with a spy that delegates to the real `pan_extent`, drive one real export of a layered map, and assert both that the artifact was written and that the spy recorded at least one call.
- **Validation:** `test (integration)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_export_state.py::test_exporting_reads_pan_extent_through_its_own_module_global`
- **Numeric pass threshold:** call count ≥ 1 and `m.svg` is a file; with M-FX15 applied (`from mapper.views import layered` and `layered.pan_extent(...)` at `exporting.py:203`) the count is 0 and the node fails while `pytest tests/test_export_state.py tests/test_en8.py tests/test_mod_compat.py` otherwise passes.
- **Negative control:** M-FX15 as above.
- **Boundary catalog:** ☑ boundary (layered renderer) ☐ empty (n/a) ☐ invalid (n/a) ☐ error (n/a)

### LLR-FX.6.1 — The leak registry is keyed `(file, lineno, expr)`
- **Traceability:** HLR-FX.6
- **Ledger:** LED-2026-10-11-fixes-batch.13
- **Statement:** The `LEAK_EXCEPTIONS` registry of `tests/test_inc9c.py` shall be typed `dict[tuple[str, int, str], str]`, both its consumers (the undeclared-leak census and the stale-exception check) shall compare the full `(path, lineno, expr)` record, and one negative-control node shall show that a second record with the same file and expression but another line is reported as undeclared.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest -p no:cacheprovider tests/test_inc9c.py -k "sec_f1 or at_089"`
- **Numeric pass threshold:** the three existing excuses are retyped to their call lines; `undeclared == [("mapper/screens/home.py", 412, "str(exc)")]` for the two-record input of the negative control; under M-FX16 that node fails. Accepted cost, declared: the key is line-sensitive, so moving those three `notify` calls reddens `test_inc9c_sec_f1_every_leak_exception_is_still_real` (fail loud by design).
- **Negative control:** M-FX16 — compare `(p, e)` again in the census; the AT-089 node fails.
- **Boundary catalog:** ☑ boundary (same file, same expression, different line) ☐ empty (n/a) ☐ invalid (n/a) ☐ error (n/a)

### Information Flow Contract (IFC) — C-54

- **Part A — flows:**

```text
FLOW: csv-import
  SOURCE: a CSV/TSV file chosen at the import prompt (utf-8 text; columns id, title, parent, depth, extras)
  - fn : import_csv.py::preview_csv (blank-first parent read)
    owner : LLR-FX.1.2
  - fn : mermaid.py::slugify (empty string when nothing survives)
    owner : LLR-FX.1.1
  - fn : import_csv.py::preview_csv (row-N id for an empty slug; typed raw_id kept)
    owner : LLR-FX.1.3
  - fn : import_csv.py::preview_csv (root selection by parentage)
    owner : LLR-FX.2.1
  - fn : import_csv.py::preview_csv (orphan attach under a parentless root; cycles left for find_cycle)
    owner : LLR-FX.2.2
  SINK: the Graph handed to the import preview screen and to MapStore.save (find_cycle refusal and csv_collisions unchanged)

FLOW: map-text-roundtrip
  SOURCE: an in-memory Graph with a declared root_id
  - fn : mermaid.py::dump (root declaration first when text order would elect another)
    owner : LLR-FX.3.1
  - fn : store.py::MapStore._check_round_trip (docstring only; comparison set unchanged) and the moved pins
    owner : LLR-FX.3.2
  SINK: the .mmd text written by MapStore.save, re-read by mermaid.py::parse (unchanged) in MapStore.load

FLOW: roles-load
  SOURCE: git rev-parse --show-toplevel / git config --get user.name / user.email (hardened allowlist, unchanged)
  - fn : screens/roles.py::_discover on a Textual thread worker
    owner : LLR-FX.4.1
  - fn : screens/roles.py::RolesScreen paint gate (blank until first facts; latest discovery wins)
    owner : LLR-FX.4.2
  - fn : screens/roles.py action guards (cursor, space, a, r)
    owner : LLR-FX.4.3
  - fn : screens/roles.py::_load from cached facts (file reads only)
    owner : LLR-FX.4.4
  SINK: the screen's four Statics and reqharness/ writes through chain.propose and the approve/reject calls only
```

- **Part B — boundary decomposition:** no — no component of the boundary is addressable on its own by a consumer in this batch: the codec and the importer are library functions in one process, and the roles screen keeps its four Static ids and its key scope exactly as they are (no address is added, moved or renamed).

---

## 5. Validation strategy

### 5.1 Methods

> **Two layers** (per the Two-layer validation rule). Every batch declares BOTH:
> - **Layer A — white-box / functional (`TC-NNN`):** validates the HLR/LLR mechanism (the HOW). Methods: `test`, `inspection`, `analysis`.
> - **Layer B — black-box / behavioral acceptance (`AT-NNN`):** validates the user story's outcome through the shipped surface (the WHAT). Method: `acceptance`.

- **Layer A (test):** `tests/test_fixes_csv_import.py` · `tests/test_fixes_forest_root.py` · `tests/test_fixes_roles_thread.py` · `tests/test_export_state.py` and `tests/test_inc9c.py` (increment 004) · the moved pins in `tests/test_mermaid.py`, `tests/test_csv_safety_store.py`, `tests/test_perf_dump.py`, `tests/test_roles_screen.py`. **Layer A (inspection):** LLR-FX.3.2's docstring grep.
- **Layer B (acceptance), exact node names** (each node's docstring carries its bare `AT-NNN` token, the form `V2` resolves):
  - AT-084 → `tests/test_fixes_csv_import.py::test_at_084_empty_parent_cells_are_roots_not_node_n`
  - AT-085 → `tests/test_fixes_csv_import.py::test_at_085_child_listed_before_root_imports_saves_and_reopens`
  - AT-086 → `tests/test_fixes_forest_root.py::test_at_086_forest_root_survives_save_and_reload`
  - AT-087 → `tests/test_fixes_roles_thread.py::test_at_087_roles_screen_git_reads_run_off_the_ui_thread`
  - AT-088 → `tests/test_export_state.py::test_exporting_reads_pan_extent_through_its_own_module_global` (docstring carries `AT-088`)
  - AT-089 → `tests/test_inc9c.py::test_at_089_a_second_leak_site_in_an_excused_file_is_still_flagged`

  AT-084, AT-085 and AT-087 assert on the painted frame text (the `_painted` pattern), never on the arguments of an `update()` call (C-32; R8, LED .16). AT-084 and AT-085 drive the real app (`MapperApp(tmp_path)` + `run_test(size=(118,34))` + `pilot.press` for `i`, the path, `enter`, `s`), reusing the `_painted` pattern of `tests/test_csv_safety_preview.py`; AT-084's preview-only assertion may use `_import_and_press_save` (it stops at `s`), but AT-085 saves under a typed name and re-opens, so it shall use `tests/test_seed_safety.py::_open_import` (the full `i`/path/`enter`/`s`/name/`enter` drive, as AT-074 does), not `_import_and_press_save`. AT-086 drives `MapStore.save`/`load` on a temp workspace. AT-087 drives `R` from home with a gated `identity._run_git`, helpers from `tests/test_roles_screen.py`.
- Every LLR names its reddening mutant (M-FX1…M-FX17); each increment executes at least one of its own at the RED proof, with the sha256 restore check.

### 5.2 Batch acceptance criteria
- 100% of LLR-FX.* covered by a named node or an inspection verdict, each with a pass result.
- 0 blocker fails; no requirement without a validation method.
- Every user story has ≥ 1 passing AT with boundary and negative evidence: US-FX-001 → AT-084 · US-FX-002 → AT-085 · US-FX-003 → AT-086 · US-FX-004 → AT-087 · US-FX-005 → AT-088 · US-FX-006 → AT-089.
- 8/8 dump goldens, the 2 inline arms' bytes and the AT-076 bytes are identical after increment 002; the file lists in `PLAN.md` are green after each increment.
- No visible string, glyph, colour or key is added (R4); the operator-path guard `tests/test_no_operator_paths.py` stays green.

---

## 6. Appendices (optional)

### 6.1 Extended glossary
See §1.3.

### 6.2 Relevant design decisions
- **`slugify` returns `""` (R1).** The three callers were read (premise 2): `preview_csv`'s row id and parent cell cannot accept a placeholder (it would collide or re-parent), and `editing.py` already writes `slugify(title) or "n"` with a uniqueness loop, so returning `""` is honest everywhere and changes no caller outside the CSV importer. Rejected: raising a named error (the importer must degrade to `row-N`, not refuse) and a hash placeholder (non-deterministic across edits, no caller needs it).
- **Root hoisted only when needed, inside the existing passes (R3).** Writing the root line unconditionally changes the `forest` and `wide6000` goldens; re-walking the edges breaks LLR-PERF.2.2's 2E + 4 bound; the chosen rule changes no golden (premise 3).
- **No root comparison in `_check_round_trip` (R3).** It would refuse saves of maps that open today whose in-memory root is not parentless; the fix is writer-side and AT-086 proves it.
- **Git facts cached in the screen, not in `identity.py` (R4).** Keeps increment 003 to `roles.py` plus tests.

### 6.3 Open risks
- **Existing tests each increment moves** (measured in a scratch copy, premises 3, 4, 7, 8):
  - 001: only `tests/test_mermaid.py::test_slugify_allows_hyphens` (the `"---" == "n"` pin → `""`). The 14-file CSV suite otherwise passes unchanged, so the removal of the `? ` prefix from top-level rows is guarded only by the new AT-084 and `test_blank_parent_cell_is_a_root_candidate_not_a_reference_to_n`.
  - 002: `tests/test_perf_dump.py::test_dump_fixture_goldens` — the inline `orphan-order` arm gains `ordered.root_id = "root"` (expected bytes unchanged); `tests/test_csv_safety_store.py::test_save_accepts_legacy_forest_after_edit` gains the root assertion and its R11 comment is rewritten; `mapper/store.py::_check_round_trip` docstring. No golden file changes (8/8).
  - 003: `tests/test_roles_screen.py::_open_roles` gains the worker wait (22/22 with it; 6 and 12 failures on two runs without it).
- **`row-N` collision surface.** The generated `row-N` ids share one namespace with ids the operator types; an operator-typed exact `row-N` is recorded in the existing collision record, never renumbered (LLR-FX.1.3, design proposal §10 and §9.1(d)). No other collision handling is added. (PDR condition, LED .17.)
- **Open question for the operator (non-blocking, decided here):** before the first load, keys are silent; the alternative is the existing `no repo` hint, which would say something untrue while git is still being read. Decided silent (LLR-FX.4.3).
- **A visible loading state** stays out of scope until a prototype verdict.
- **Security questions (scan flags `session`, `form`; both are false positives of the word match: the batch adds no login, no cookie, no web form).** The scan's real questions, answered: (1) *new input surface?* No — the CSV file was already imported; the change narrows what an empty cell and an empty slug can reference, and ids still pass through `slugify` before they reach the graph or the `.mmd` text. (2) *new subprocess surface?* No — the same three allow-listed read-only git calls (`stations`-hardened in the reqharness batch) run on a worker thread instead of the UI thread; `identity.py` is untouched. (3) *thread safety?* The worker only calls the two `identity` functions and returns plain values from the worker, applied on the UI thread in `on_worker_state_changed`; no screen state is touched off the UI thread, and a stale result is dropped by the generation guard. (4) *writes?* The roles screen still writes only through `chain.propose` / `approve_pending` / `reject_pending`; keys are inert until the first load, so no write can precede a verified read. (5) *secrets, paths, accounts?* None added; the operator-path guard stays in the verification list. `security-reviewer` is not required for this batch; the orchestrator may still route increment 003. The cancel-and-guard of LLR-FX.4.1 adds no input surface; the narrowed catch lets an unexpected exception propagate rather than hiding it.
- **The intake's proposed fix for B-116/B-115 is superseded** by LLR-FX.1.* / FX.2.* (it kept `slugify`'s `"n"`, and its "last parentless row" attach target would have mis-rooted the all-parked case).

### 6.4 Phase-1 reconciliation log — moved to the ledger (§7)

### 6.5 Requirement amendments — moved to the ledger (§7)

---

## 7. The ledger — authored as a SEPARATE FILE

`01-requirements-ledger.md` holds LED-2026-10-11-fixes-batch.1 … .13.
