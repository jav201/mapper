# Design proposal — mapper — Batch 2026-10-11-fixes-batch

> **Artifact language.** English (`state.json` `language: en`).
> **Owed in.** `core` by trigger (PDR fired: A2, A3, D1, E1 — `PLAN.md` §Triggers) · staged under `design/`, cited by id from the repo.
> **Written against:** `01-requirements.md` (P2-reviewed), `01-requirements-ledger.md` (LED .1-.13), rulings R1-R6 (`PLAN.md` §Decision log), `design/arq-note.md`.
> **Proportionate on purpose:** a bug-fix batch. Where the requirements already hold the design (§6.2 of `01-requirements.md`), this cites it instead of restating it. Sections 9 and 10 are the two lenses the fired triggers owe (D1 UX, C1/C6 security).
> **Evidence rule:** every render and number below was produced by running code in a **scratch copy outside the repository** (the patched copy holds the design as specified here; the worktree has no code edit). Commands are named so they can be re-run.

| Field | Value |
|---|---|
| Id | `PDR-2026-10-11-fixes-batch` |
| Requirements covered | HLR-FX.1-FX.6, LLR-FX.1.1-FX.6.1, AT-084-AT-089, US-FX-001-006; rulings R1-R6 |
| Modules touched (from `docs/ARCHITECTURE.md`) | `mermaid`, `import_csv`, `store` (docstring only), `screens` (`roles.py` — unclaimed by the map today, ARQ finding F1); tests only for increment 004 |
| Triggers that fired | A2 · A3 · B1 · B3 · B4 · C1 · C6 · D1 · E1 |
| Author / reviewers | `software-dev` (author) · `architect` · `qa-reviewer` · `ux-reviewer` (D1 fired) |

---

## 1 · Objective and scope

Fix four shipped defects and close two test-hygiene carries, in four serial increments, without changing any module boundary: B-115 (an empty slug / empty parent cell becomes node `n`), B-116 (a child listed before its root reads as a cycle), B-117 (a forest map's root changes on reload), B-127 (the roles screen runs git on the UI thread), plus B-110 and B-113 (test-only).

**Will not do:** any new loading chrome for the roles screen (R4: needs a prototype verdict first); any change to `parse`, the `? ` copy, `_check_round_trip`'s comparison set, `reqharness/identity.py`, or any golden file; transliteration or normalisation in `slugify` (Unicode scope = what it does today, R5). Perf items B-118/B-120 and ReqHarness follow-ups B-124..B-126 stay in the backlog.

## 2 · Modules and boundaries

| Module | What it owns here | What it exposes | What it must NOT reach into |
|---|---|---|---|
| `mermaid` | `slugify` returns `""` when nothing survives; `dump` hoists the declared root | `slugify(s) -> str` (domain +`""`), `dump(graph) -> str` (text changes only for a forest whose root is not text-first), `parse` unchanged | UI, network (map row) |
| `import_csv` | blank-first parent read, `row-N` ids, root by parentage | `preview_csv(path) -> Graph` (signature, `csv_collisions` shape, `CsvRow(line_no, raw_id)` unchanged) | UI, persistence writes, `store`, `app` |
| `store` | docstring of `_check_round_trip` only | unchanged | `app`, `views` |
| `screens` (`roles.py`) | discovery on a thread worker, facts cache, paint gate | `RolesScreen` (class name, Static ids `roles-status` / `roles-body` / `roles-band`, key scope `SCOPE_ROLES` unchanged) | `app`; any new `reqharness` import beyond what `roles.py` has |

- Boundaries respected as declared in `docs/ARCHITECTURE.md`: ✓ — no boundary moves and no edge is added (`arq-note.md` §1). One thing the map must still receive: `mapper/screens/roles.py` added to the `screens` row and the two contract notes on the `mermaid` row (ARQ §1.2); that is the map catching up with the tree, not a design decision.

## 3 · Diagrams

Only the viewpoints that apply. Interaction (state dynamics) for B-127 and the algorithm for `dump`; the rest are in `01-requirements.md` §6.2.

**Roles screen, state dynamics** (the only new state: `_facts` and `_gen`):

```text
push R ── compose (chrome + 4 empty Statics) ── on_mount ─┐
                                                          ├─ _start_discovery(): gen += 1, worker(gen)
                         on_screen_resume (fires at push)─┘          │ thread: repo_root, read   (catch set: 4 types)
                                                                      ▼
  _facts is None  ── keys j/k/h/l/space/a/r: return, no paint ──   worker RETURNS facts; on_worker_state_changed(SUCCESS)
  (Esc works)                                                        │ applied on the UI thread there; if gen != latest or not is_attached: drop
                                                                      ▼
                                                   _facts = facts; _reload() = file reads + paint
  later keys: _reload() from cached _facts, 0 git calls
```

**`dump`, algorithm** (bookkeeping inside the two existing edge passes; no third pass over `graph.edges`):

```text
pass 1 (writes edge lines)   also records: written ids, written children, parents in first-seen order
pass 2 (incident ids)        unchanged
first_parentless = first recorded parent that is no written child, else first orphan
hoist  <=>  root in text  and  root is no written edge's child  and  root != first_parentless
if hoist: insert the root's declaration line right after "graph TD"; skip it in the orphan block
```

## 4 · Interfaces that change — and which ones FREEZE

| Interface | Current | After | Consumers | **Frozen for the fork?** |
|---|---|---|---|---|
| `mermaid.slugify(s) -> str` | returns `"n"` for nothing-survives | returns `""` | `import_csv.py:59`, `:70`; `screens/map/editing.py:115` (`or "n"`, unchanged result); `tests/test_mermaid.py:12` (pin moves) — `arq-note.md` §2.1 | n/a — one lane (`01-requirements.md` §2.8) |
| `mermaid.dump(graph) -> str` | edges, then orphans | root's line first when text order would elect another | `store.py:873` (save), `:878` round trip, `undo.py:42`→`:59`→`store.py:508`, `perf_goldens_capture.py`, 17 test files — `arq-note.md` §2.2 | n/a |
| `import_csv.preview_csv(path) -> Graph` | root = first row; blank parent = ref to `n` | root by parentage; blank = no parent; `row-N` for empty slugs | `screens/home.py:518`; `ImportPreviewScreen`; `MapStore.save` (via the preview graph) | n/a |
| `RolesScreen` load path | `_load(workspace)` sync at mount/resume/keypress | `_load(facts)`; discovery on a worker; keys inert until first facts | `app.py:37`, `screens/home.py:45` (push only), `tests/test_roles_screen.py::_open_roles` (gains a worker wait), `tests/test_keymap.py:30` | n/a |

**Not touched inside this batch (the invariants the tests defend):** `parse`, `_check_round_trip`'s node-set + edge-multiset comparison (no root comparison — R3), `identity.py`, the four Static ids and key scope, every on-screen string, all dump goldens.

## 5 · Proposed test cases

All names are the ones fixed in `01-requirements.md` §5.1 / the LLR executed-verification lines; `pytest -p no:cacheprovider`, single files, from the worktree root. Layer: 0 unit · A white-box · B black-box (`AT`) · UX.

### Increment 001 — B-115 + B-116 (source: `mapper/mermaid.py`, `mapper/import_csv.py`; new `tests/test_fixes_csv_import.py`)

| Id | Layer | What it asserts | **Mutation that turns it RED** |
|---|---|---|---|
| TC-FX-1.1 | 0 | `slugify("") == slugify("   ") == slugify("---") == slugify("!!!") == ""`; `slugify("Niño") == "niño"`, `"Mi Hijo Nuevo"` and `"a_b"` unchanged (`test_slugify_returns_empty_when_nothing_survives`; the moved pin `test_slugify_allows_hyphens` now `== ""`) | **M-FX1** `value[:32] or "n"` restored — the new node fails `"n" != ""` while the *old* pin would stay green, which is why it moves |
| TC-FX-1.2 | 0 | blank and whitespace parent cell = no parent (`r` keeps its title with no `? ` prefix, edge `r→k`); punctuation-only parent parks `k` (`? K`) under `r`; `N,N,` + `k,K,n` gives one edge `n→k`, no self-edge (`test_blank_parent_cell_is_a_root_candidate_not_a_reference_to_n`, `test_punctuation_only_parent_cell_parks_the_row`) | **M-FX2** decide "has parent" from the slug again — `r` is titled `? R` |
| TC-FX-1.3 | 0 | `!!!,Bang,` → node `row-1`, titled `Bang`, `raw_id` `!!!`; the shared counter advances by one per `row-N` row only; typed `row-1` after an auto `row-1` is a recorded collision; `,Alpha,` then `,,` → ids `{alpha, row-1}` (title id does not advance the counter) (`test_id_with_no_slug_characters_becomes_row_n`; unchanged `test_preview_csv_records_collisions`) | **M-FX3** drop the fallback — id stays `""` |
| TC-FX-2.1 | 0 | truth table of root choice: child-first, grandchild-first, two parentless rows, all-parked, ring, ring beside a root, `depth`-only parentage (`-k root`) | **M-FX4** leave `root_id` as `add_node` stamped it (first row); **M-FX5** let a parked row be root |
| TC-FX-2.2 | 0 | 24 of 24 permutations of `r` / `a←r` / `b←r` / `c←a` give one node set, one edge set, root `r`; rings still named by `find_cycle` (`-k "permutation or cycle"` + the two `test_csv_safety_preview` nodes) | **M-FX4** (6 of 24 pass on the base tree: the 6 that start with `r`) |
| **AT-084** | B | the real `i` import of `alpha,Alpha,` / `beta,Beta,` / `!!!,Bang,` paints no node `n`, one root, three rows; id `row-1` (`test_at_084_empty_parent_cells_are_roots_not_node_n`; includes the `niño` arm) | M-FX1 + M-FX2 |
| **AT-085** | B | child-first CSV imports, saves under a typed name via `_open_import`, re-opens with root `root`, no cycle sentence (`test_at_085_child_listed_before_root_imports_saves_and_reopens`) | M-FX4, M-FX5 |
| **TC-FX-S1** *(proposed addition, test-only)* | 0 | a hostile-cell matrix (`"]|x"`, `"--> y"`, `"#93;"`, `"]"`, `""`, a 5 000-character id) imported through `preview_csv` yields only node ids matching `[\w-]+`, none empty; and `dump` → `parse` of the result keeps the node set (§10) | **M-FX3** (an empty or malformed id reaches the graph) |

### Increment 002 — B-117 (source: `mapper/mermaid.py`, `mapper/store.py` docstring; new `tests/test_fixes_forest_root.py`)

| Id | Layer | What it asserts | **Mutation that turns it RED** |
|---|---|---|---|
| TC-FX-3.1 | 0 | each parentless node of the three forest shapes, set as root, re-parses to itself (8 of 8; base 3 of 8); empty graph, single node, root with a label, root already first, a root whose only edge dangles (unwritten, as `dangling-solo` pins), root id absent from `nodes` (text unchanged); no duplicated declaration for an orphan root | **M-FX6** delete the hoist (reproduction re-parses to `b`); **M-FX7** always write the root line (reddens the byte-stability arms: `forest`, `wide6000`, fixtures — a *different* failure from M-FX6) |
| TC-FX-3.2 | 0 | pins that moved: `test_save_accepts_legacy_forest_after_edit` gains `reloaded.root_id == loaded.root_id == "a"`; `test_dump_fixture_goldens` `orphan-order` arm gains `ordered.root_id = "root"` with unchanged bytes; `grep -c "root drifts" mapper/store.py` → 0 | M-FX6 (`"b" != "a"`) |
| TC-FX-3.3 *(proposed addition, test-only)* | A | an undo snapshot of a forest map (`dump` + sidecar → `store._graph_from_sidecar`, the path of `undo.py:42` / `:59`) restores the declared root | **M-FX6** — covers the one consumer no AT reaches (`arq-note.md` §2.2) |
| visit bound | A | `tests/test_perf_dump.py` AT-076: `visits <= 2*E + 4`; 8/8 goldens + AT-076 bytes identical | **M-FX12** re-walk `graph.edges` to decide (`36000 > 12004`, executed on a first draft) |
| **AT-086** | B | `MapStore.save` then `load` of a forest with declared root `a` re-opens with root `a`; the saved `.mmd` names it first (`test_at_086_forest_root_survives_save_and_reload`) | M-FX6 |

### Increment 003 — B-127 (source: `mapper/screens/roles.py`; new `tests/test_fixes_roles_thread.py`; `_open_roles` gains `await app.workers.wait_for_complete(); await pilot.pause()`)

| Id | Layer | What it asserts | **Mutation that turns it RED** |
|---|---|---|---|
| TC-FX-4.1 | A | gated `identity._run_git` records 3 calls, 3 of 3 off the main thread, inside a 5 s guard (`test_at_087_…`, `test_roles_discovery_failure_degrades_to_no_repo` with the four exception types, plus `RuntimeError` surfacing) | **M-FX8** call `_discover` directly in `on_mount`; **M-FX14** remove the `try/except` |
| TC-FX-4.1b | A | `Esc` while gated, gate released: 0 exceptions, 0 notifications, 0 paints on the popped screen, app still answers (`test_roles_popped_screen_discards_late_discovery`) | **M-FX13** remove the generation and `is_attached` checks in `on_worker_state_changed` (the framework's own cancel stays; see `arq-note.md` §3) |
| TC-FX-4.2 | A | gate closed: the four surfaces are empty; latest discovery wins (`test_roles_paints_nothing_until_discovery_returns`, `test_roles_latest_discovery_wins`) | **M-FX11** drop the generation check |
| TC-FX-4.3 | A | `j`, `space`, `a`, `r` with the gate closed change nothing, notify nothing, write 0 bytes (digests of `roles.yml` and `reqharness/pending/`); `Esc` pops; the painted key bar shows only navigation and `Esc` while gated and equals today's after release (`test_roles_keys_before_first_load_are_inert`) | **M-FX9** remove the guard; **M-FX17** leave the key bar unconditional |
| TC-FX-4.4 | A | git-call count 3 → 3 after `space` and `a`; the 22 existing roles-screen nodes pass (`test_roles_keypress_reload_runs_no_git`) | **M-FX10** make the keypress reload call `_discover` |
| **AT-087** | B | pressing `R` returns control while git is gated; blank and inert until release, then `chain` and `viewer subject` painted (`test_at_087_roles_screen_git_reads_run_off_the_ui_thread`) | M-FX8 |

### Increment 004 — B-110 + B-113 (0 source files; `tests/test_export_state.py`, `tests/test_inc9c.py`)

| Id | Layer | What it asserts | **Mutation that turns it RED** |
|---|---|---|---|
| **AT-088** | B | a spy on `mapper.screens.map.exporting.pan_extent` records ≥ 1 call during one real export and `m.svg` exists (positive control) | **M-FX15** rebind `exporting.py` to `layered.pan_extent` |
| **AT-089** | 0 | `LEAK_EXCEPTIONS` keyed `(file, lineno, expr)`; a second `str(exc)` record in an excused file is reported undeclared; the 13 `sec_f1` nodes pass at the call lines `home.py:175`, `screens/map/screen.py:214`, `common.py:213` | **M-FX16** compare `(p, e)` again |

**Optional (QA note, not a condition):** a large-forest dump scaling test (a forest with thousands of parentless roots, asserting the visit bound still holds with the hoist firing) may be added in increment 002 if cheap; AT-076 already pins the bound for the shipped shapes.

**Layer 0 applies** wherever the unit has cyclomatic complexity ≥ 3 or crosses a module boundary: `preview_csv` (root selection, depth parentage) and `dump` (hoist) both do. **Declared once for the batch:** every increment runs its own RED proof with the sha256 restore check; the mutants above are named, and none is a hope.

**Already measured in the scratch copy** (design as specified, ten files, existing tests only): 170 passed, 3 failed — the `slugify("---")` pin (expected, moves in 001), the `orphan-order` arm (expected, moves in 002), and `test_repair_cycles::test_llr_n13_1_5…`, which fails **identically on the unpatched base copy** (the copy lacks files outside `mapper/` and `tests/`; environment, not design). The roles-screen file passes 22 of 22 with the worker wait.

## 6 · Risks and rejected alternatives

**Risks**

| Risk | Likelihood / impact | Mitigation |
|---|---|---|
| The pin moves (3 files) hide a regression | certain moves, low impact | each pin moves in its own increment with the RED proof showing the old pin failing first |
| `dump` hoist breaks a golden or the visit bound | measured: no (8/8, AT-076) | bookkeeping inside the existing passes; M-FX7/M-FX12 pin both failure modes |
| The `? ` prefix disappears from the single chosen root only; **extra parentless rows keep it** (existing forest rule) | certain; visible | judged in §9 — the ruling keeps the forest rule |
| Operator keys are **dropped, not queued**, during the loading window | low at healthy git (a few ms), visible at slow git | R4 decision; §9 J4 asks the UX reviewer to accept or reject it |
| Both `on_mount` and `on_screen_resume` start a discovery at push (6 git calls, as today) | low | generation guard; ARQ F3b — DDR may coalesce |
| A map that already drifted stays drifted | certain for existing files; none for new ones | corrected ARQ F2 (R7): a map loaded from disk takes its root from `parse` (first parentless node in text), so the hoist does not fire on resave and the bytes stay the same; it fires only when the root was set in-session (CSV import; `editing.py:221` after a root delete). B-117 stops future drift; it cannot repair a map that already drifted, because the declared root was never stored |
| Unexpected exception in the worker ends the app (Textual default `exit_on_error`) | low; intended | the narrowed catch (R5): defects fail loud, not blank |
| Line endings: the working tree is CRLF while the index is LF (`git ls-files --eol` → `i/lf w/crlf`, `core.autocrlf=true`); a multi-line string edit that assumes LF fails to match or writes a mixed file (hit once while building the scratch copy) | low | each increment's packet checks `git diff --stat` shows only intended hunks; no reformat |

**Rejected alternatives — only where a real decision existed** (rulings R1-R5 hold the rest)

| Alternative considered | Why it was rejected |
|---|---|
| `slugify` raises a named error, or returns a hash placeholder (R1) | the importer must degrade to `row-N`, not refuse an importable spreadsheet; a hash is non-deterministic across edits and no caller needs it (`01-requirements.md` §6.2) |
| `dump` writes the root line unconditionally / re-walks the edges / `_check_round_trip` compares the root (R3) | unconditional moves the `forest` and `wide6000` goldens; a re-walk breaks the 2E + 4 bound (executed: 36000 > 12004); a root comparison would refuse maps that open today |
| Cache the git facts in `identity.py` (R4) | keeps increment 003 to one source file and leaves the hardened module untouched |
| Before the first load, show the existing `no repo` hint on keypress (R4) | it says something untrue while git is still being read |
| Bare `except Exception` around discovery (R5) | hides defects; the four named types are the ones the helper layers can raise |
| Explicit `on_unmount: workers.cancel_node(self)` (open, `arq-note.md` §3) | the pinned Textual (`==8.2.8`) already does this in `Widget._on_unmount`; a duplicate is a line no mutant can redden. Closed at the PDR: the architect review raised no condition against it; the framework behaviour stands and the hand-back guard is the owned behaviour |

## 7 · Forward-applicability table — **the section that makes this document honest**

| Output of this PDR | Named consumer downstream | Where the consumer will read it |
|---|---|---|
| Design characteristics: blank-first parent read, `row-N` counter rule, root by parentage | increment 001 implementer (`software-dev`) | §3-§5 here; `01-requirements.md` LLR-FX.1.*, FX.2.* |
| Design characteristics: hoist rule and bookkeeping inside the two passes | increment 002 implementer | §3 algorithm; LLR-FX.3.1 |
| Design characteristics: worker, generation guard, catch set, paint gate, key guards, `_load(facts)` | increment 003 implementer | §3 state sketch; LLR-FX.4.1-FX.4.4; `arq-note.md` §3 |
| Map amendment (`roles.py` in the `screens` row's paths, ownership prose and exposes list at `docs/ARCHITECTURE.md:113`; two `mermaid` contract notes citing batch `2026-10-11-fixes-batch`) lands in increment 003 itself | `architect` at the ARQ gate; the A-family triggers of later batches | `docs/ARCHITECTURE.md` §2, per `arq-note.md` §1.2 |
| Proposed test cases TC-FX-* and the named mutants | layers 0/A/B of each increment; DDR item 5; validation (P4) | §5 here; each increment packet's RED counterfactual |
| Added cases TC-FX-3.3 (undo keeps root) and TC-FX-S1 (hostile-cell matrix) | `qa-reviewer` approval at PDR; increments 002 and 001 | §5 here; `tests/test_fixes_forest_root.py`, `tests/test_fixes_csv_import.py` |
| Before/after renders and the five judgement items J1-J5 | `ux-reviewer` at PDR; the validation walkthrough (P4) against the real mechanism | §9 here |
| Security note (CSV input surface, thread boundary) | `security-reviewer` (optional light read of increment 003, orchestrator's call); DDR | §10 here; `01-requirements.md` §6.3 |
| Design → requirement traceability (HLR/LLR/AT ↔ TC ↔ mutant ↔ file) | traceability matrix and the DDR | the §5 tables, which cite the LLR id on every row |
| Reverse census (B1/B3/B4) per increment | each increment packet; DDR items 3 and 5 | `arq-note.md` §2 end; `PLAN.md` §Triggers |

## 8 · Parallelisation plan

The batch does **not** fork: one lane, serial 001 → 004 (001 and 002 both edit `mapper/mermaid.py`, so `modules(001) ∩ modules(002)` is not empty — A4 did not fire only because the plan is serial). `01-requirements.md` §2.8 declares the fork preconditions discharged trivially. No lane table is owed.

## 9 · UX section (D1)

**Context of use.** *User:* one operator in a terminal. *Tasks:* (a) turn a spreadsheet into a map (`i` → path → preview → `s`); (b) open the roles screen (`R`) to read or change who holds which role. *Environment:* terminal of variable width; the harness reference is 118 × 34 (no layout is added or changed here, so no width-derivation question arises). *Constraint from R4:* no new visible chrome.

**What the user sees differently — three changes**, each shown as text produced by driving `MapperApp` with `run_test(size=(118, 34))` and real key presses in the scratch copy (`PYTHONPATH=. python drive_csv.py` / `drive_roles.py`; the 118-column header line's blank run is elided as `[…]`).

### 9.1 Import preview: the root loses its `? ` and the "cycle" refusal goes away

**(a) The common export — root row first, blank parent.** *Before* (base):

```text
◆ mapper · atlas · concept map […]  3 nodes
        ▐ ? Root
               │
       ┌───────┴────────┐
▐ A              ▐ B
```

*After:*

```text
◆ mapper · atlas · concept map […]  3 nodes
        ▐ Root
               │
       ┌───────┴────────┐
▐ A              ▐ B
```

The `? ` prefix on a row that is simply top-level was a lie ("parked: parent missing"); base even **saved** it in the title (`root[? Root]` in the `.mmd`). Change: the one chosen root is no longer prefixed; the saved text becomes `root[Root] --> a[A]`.

**(b) Several parentless rows** (`alpha,Alpha,` / `beta,Beta,` / `!!!,Bang,`). *Before:* the preview refuses with the cycle sentence:

```text
 could not draw the preview

 the import builds a cycle (n → n); a saved map must be a tree, so fix the parent references and import again.
```

*After:*

```text
◆ mapper · atlas · concept map […]  3 nodes
        ▐ Alpha
               │
       ┌───────┴────────┐
▐ ? Beta         ▐ ? Bang
```

Saved text after: `alpha[Alpha] --> beta[? Beta]` / `alpha[Alpha] --> row-1[? Bang]`. **Note what did not change:** the second and third top-level rows still carry `? ` — the existing forest rule (R2) attaches extra parentless rows under the first and marks them parked; the ruling keeps that copy. See J1.

**(c) Child listed before its root** (`child,Child,root` / `root,Root,`). *Before:*

```text
 could not draw the preview

 the import builds a cycle (child → root → child); a saved map must be a tree, so fix the parent references and import again.
```

*After:*

```text
◆ mapper · atlas · concept map […]  2 nodes
▐ Root
       │
       ┼
▐ Child
```

**(d) Where the ids `row-N` become visible.** They are **not** shown in the preview tree (the canvas paints titles; a row with no id and no title paints `row-N` as its title, unchanged from today). They appear (i) in the saved `.mmd` / `_nodos.yml` (`row-1[? Bang]` above), and (ii) in the existing collision sentence, new only when an operator types an id that equals an auto-assigned one (`root,Root,` / `!!!,Bang,root` / `row-1,Rowone,root`):

```text
 could not draw the preview

 CSV rows 3 (id '!!!') and 4 (id 'row-1') collapse into the node id 'row-1'; a map can hold only one parent per node, so rename the duplicated ids and import again.
```

(The base tree shows a *different* wrong refusal for the same file: `the import builds a cycle (root → n → root)`.) The sentence's wording is unchanged; its row numbers are the existing `line_no` (the header counts as line 1).

### 9.2 Roles screen: first paint timing

Measured with git made slow on purpose (1.5 s injected into each of the three calls, 4.5 s total; `identity._run_git` wrapped in the scratch copy), then with real git.

| Moment | Before (base) | After |
|---|---|---|
| `R` pressed | the app **does not answer for 9.2 s** (two loads: mount and resume, 6 git calls on the UI thread) | returns in **0.1 s** |
| What is on screen right after `R` | (nothing visible during the freeze) then the finished screen | tab strip (`home › roles`) and key bar only; `#roles-status`, `#roles-body`, `#roles-band` and the hint line are **empty** (0 characters each) |
| `j` then `space` while git runs | not possible: the UI is frozen; the keys are consumed after the paint and act | **ignored**: no repaint, no hint, no notification, no write; they are dropped, not queued |
| `Esc` while git runs | not possible | works, and a result that arrives later is discarded |
| First full paint | at 9.2 s: `chain  ✓ verified  viewer subject (admin)`, the matrix, the band, the hint `space propose change — …` | at about 4.9 s from `R` (the same strings, same matrix, cursor on the first person) |
| Each later `space` / `a` / `r` | re-runs 3 git calls (another 4.5 s freeze in the same run) | re-reads disk only, 0 git calls |
| **Real git, no injected delay** | populated at the first `pilot.pause()` after `R` (`R` returns in 0.2 s) | populated at the first `pilot.pause()` after `R` (`R` returns in 0.1 s) — in the harness the blank window is not observable |

After-state at the moment the keys were pressed (verbatim from the run): `[status] ''`, `[body] 0 chars`, `[band] 0 chars`, `[hint] ''`; after release: `[status] ' chain  ✓ verified  viewer subject (admin)'`, 717 and 594 characters in body and band, hint `'space propose change — as admin, a change to someone else applies now; your own changes pend'`, and the matrix:

```text
 person                        admin             req-reviewer                safety-lead            board        qa
 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 ▸ subject                        ●                    ○                          ○                   ○           ○
 reviewer-2                       ○                    ●                          ○                   ○           ○

 ● in force    ◐ pending toggle    ○ not held   space on a cell proposes the change
genesis — declared at registry creation
```

### 9.3 Observable UX criteria and the judgement items for the reviewer

Criteria (each checkable in the walkthrough at validation against the real mechanism):

1. A blank parent cell never produces `? ` on the chosen root, and never a reference to a node `n` (AT-084).
2. A child-first CSV imports and saves; the cycle sentence appears only for a genuine cycle (AT-085).
3. `R` returns control at once; nothing wrong is ever painted while git is read (AT-087).
4. After the first paint the screen is indistinguishable from today's (the 22 existing nodes).

Judgement items — **where this proposal asks for a ruling, not just a check:**

- **J1.** In (b) all three rows are "top-level" to the operator, yet `Beta` and `Bang` still read `? ` ("parked"). Accept as the existing forest rule (out of scope: "any change to the `? ` copy"), or open a follow-up?
- **J2.** Row ids `row-N` are invisible in the preview and only surface in the collision sentence and the saved file. Is that discoverable enough, given the importer now invents ids?
- **J3.** During the load window the key bar still advertises `space` and the edit keys that do nothing. R4 forbids new chrome; is an advertised-but-inert key bar acceptable for a window that is a few milliseconds at healthy git and seconds only when git is slow?
- **J4.** Keys pressed in that window are dropped, not queued. Acceptable, or should the operator get any signal? (Any signal is new chrome ⇒ a prototype round before implementation, per the standing practice; **this proposal does not add one**.)
- **J5.** The screen is silent when git is slow: a blank body with a tab strip. The existing `no repo` copy is deliberately *not* used (untrue while loading). Does the reviewer want the visible-loading follow-up (B-127's backlog row) scheduled?

### 9.4 PDR rulings on J1-J5 (ux-reviewer, orchestrator, 2026-10-15)

| Item | Ruling | Where it landed |
|---|---|---|
| J1 (`? ` on other top-level rows in the preview) | accepted as the existing forest rule; follow-up row | backlog B-129 |
| J2 (`row-N` ids invisible) | no ruling beyond §9.1(d); the collision sentence stays the surface | requirements §6.3 (LED .17) |
| J3 (advertised-but-inert key bar) | ACCEPT as a subtraction: until the first facts arrive the key bar shows only navigation and `Esc`, no edit keys; no new chrome | LLR-FX.4.3, TC-FX-4.3, M-FX17 (LED .16) |
| J4 (keys dropped, not queued) | accepted; NO extra status-line signal in this batch | R8 |
| J5 (visible loading state) | out of scope; a prototype round is owed before any implementation | backlog B-128 |

Evidence honesty: the blank window is evidenced `executed (injected delay)` only (the harness cannot observe it at healthy git); AT-084, AT-085 and AT-087 assert painted frame text, not `update()` arguments (C-32; requirements §5.1); real-user evaluation is `not performed — one-person team`.

## 10 · Security note (C1, C6)

**Scope.** The scan flags are `session` (C1) and `form` (C6), both textual false positives (`01-requirements.md` §6.3 holds the questions and answers; this section answers the one the scan was really asking for C6: *what can an attacker-controlled CSV do now that it could not before?* — and re-checks the thread boundary for C1).

**CSV input surface — answer: nothing new; two things it can no longer do.**

| What a hostile CSV controls | Before | After | Why no new capability |
|---|---|---|---|
| Node ids | every id passes `slugify` (charset `[\w-]`, ≤ 32 chars) | same, **or** the generated `row-<integer>`; `""` never reaches the graph (M-FX3 reddens it) | executed on a hostile matrix in the scratch copy (`]|x`, `--> y`, `#93;`, `]`, empty, titles of punctuation): **all resulting ids match `[\w-]+`**, none empty. The `.mmd` writer escapes labels only (`_escape_mermaid`), never ids, so the id charset is the defence, and it is unchanged |
| Which row is the root | always the first row | the first row without a parent edge that was not parked | the root is one of the CSV's own rows; choosing it by row order grants no authority anywhere (no path, command, or file derives from it) |
| Phantom parent | a blank parent cell re-parented every top-level row under a node named `n`, and a row id `n` or `N` could capture the whole sheet | **removed** | a confused-deputy over structure that existed before and is closed by LLR-FX.1.2 |
| Parked marker | `? ` set on every blank-parent row | `? ` only on rows whose parent is missing or unknown, or extra roots | `? ` is a display cue, not a control; nothing reads it |
| Raw text reaching sinks | `CsvRow.raw_id` (typed id) in the collision sentence, through `darkside.plain` at assembly (`import_preview.py` `_collision_sentence`); title fallback = typed text | identical sinks, identical coercion; the typed text for an empty-slug id (`!!!`) now reaches the same two sinks it already reached for the colliding ids | no new sink |
| Resource use | `n` empty-parent rows → adjacency rebuilt per attached orphan: 4 000 parentless rows took **0.86 s** | one pass: **0.03 s** (same file) | a CPU-amplification vector narrowed, not widened |
| Inputs that raise | `int(depth_raw)` guarded by `isdigit`; delimiter sniffing | unchanged | no new parse path |

**Thread boundary (increment 003).** The worker runs only `identity.repo_root` and `identity.read` — the same three allow-listed read-only git calls (argv list, `shell=False`, 10 s timeout, scrubbed env), `identity.py` untouched. It touches no widget and no screen attribute; it RETURNS plain values, applied on the UI thread in `on_worker_state_changed` (SUCCESS) after the generation and `is_attached` checks (no `call_from_thread`: R7, which avoids an exit-time hang). The module-level `_GIT_CACHE` dict (`identity.py:73`) can be written by two concurrent discoveries with the same value: benign under the GIL. No write path moves: `chain.propose` / `approve_pending` / `reject_pending` remain the only writers and are reachable only after the first facts arrive (keys inert before it), so no write can precede a verified read. Exception text is never painted (the catch maps to the existing `no repo` state; toasts keep the type-only rule `INC9-SEC-F1`). An unexpected exception in the worker ends the app with Textual's traceback — the same disposition as an unexpected exception on the UI thread today.

**Review route.** `01-requirements.md` §6.3 says `security-reviewer` is not required; `PLAN.md` item 4 proposes one light read of §6.3 plus increment 003 because the scan fired. This proposal repeats that recommendation for **increment 003 only** (hand-back guard and catch set); skipping it is the orchestrator's recorded call.
