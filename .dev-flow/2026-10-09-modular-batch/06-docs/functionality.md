# Functionality — mapper — Batch `2026-10-09-modular-batch`

> Phase 6 artifact (drafted by a Kimi `kimi-for-coding` unit). Audience: **the maintainer** — this batch changed the repository layout, not the app. There is no user-visible change: AT-065 proves painted-output parity against pre-move goldens at 118 and 87 columns (`tests/test_mod_parity.py:159`, goldens `evidence/mod_parity_118.txt` / `mod_parity_87.txt`).

## 🔑 At a glance (read first)

- **What this batch added:** `mapper/app.py` (5255 lines, the file every increment collided on) is now 340 lines of `MapperApp` + `main` + `CSS` + re-exports; the 3454-line `MapScreen` lives in `mapper/screens/map/` as one core class + 11 concern mixins, beside 7 sibling-screen modules under `mapper/screens/` (`wc -l` figures, post-mortem §Product findings).
- **Capabilities:** one feature = one file (a lane edits exactly one concern module) · Textual dispatch preserved through plain mixins (mechanism A) · the suite keeps importing and monkeypatching `mapper.app` unchanged (21 re-exports, 7 patch repoints) · the §3 dependency rules are executable (AT-071).
- **How to use it:** to work on a map feature, edit its concern module in `mapper/screens/map/`; run the guard file for that concern's contract (table below).

---

## Detail (reference)

### The module map (what moved where)

`mapper/app.py` keeps only `MapperApp`, `main`, the `CSS` block and a permanent re-export block (`mapper/app.py:11-40`, `__all__` since `d4948b`). Everything else moved, byte-identical bodies (`tests/test_mod_bodies.py` diffs per-method `ast.dump` against the Inc-0 baseline):

| File | Concern / role | Mixin / names |
|------|----------------|---------------|
| `mapper/screens/map/screen.py` (840 lines) | the **core** class: lifecycle (`__init__` with the 30 attribute slots, `compose`, `on_mount`, region visibility, focus parking), **every class constant + `BINDINGS`**, and `action_open_ficha` (stays in the core — moving it needs a `navigation ↔ screen` cycle, recorded at `03-increments/increment-018.md:22`) | `MapScreen(PaintingOps, PanningOps, SearchingOps, NavOps, DraftsOps, EditingOps, FocusModeOps, UndoOps, OpeningOps, ExportingOps, HintsOps, Screen)` — `screen.py:54` |
| `mapper/screens/map/painting.py` | views concern: `refresh_canvas`, view state, header/canvas sizing, minimap, legend docking, toggles | `PaintingOps` |
| `mapper/screens/map/searching.py` | search concern: order/hits, count line, pagination, echo, hit & gap walking | `SearchingOps` |
| `mapper/screens/map/panning.py` | pan concern: clamp/consume/reclamp, `_pan`, pan-revealing selection | `PanningOps` |
| `mapper/screens/map/navigation.py` | the shared value class `NavigationModel` (A5a, pre-B0) + the nav mixin | `NavigationModel`, `NavOps` |
| `mapper/screens/map/drafts.py` | draft concern: `_guard_draft` funnel, `guard_open`, `_save_draft`, field focus | `DraftsOps` |
| `mapper/screens/map/editing.py` | edits concern: attachments, add-child, archive, subtree removal | `EditingOps` |
| `mapper/screens/map/focus_mode.py` | focus concern: `action_toggle_focus` | `FocusModeOps` |
| `mapper/screens/map/undo.py` | undo concern: snapshot stack, `action_undo` | `UndoOps` |
| `mapper/screens/map/opening.py` | open concern: attachment-activated handler, `action_open_documents` — the one sanctioned `open_external` call site | `OpeningOps` |
| `mapper/screens/map/exporting.py` | export concern: `action_export_svg`, export-budget helpers | `ExportingOps` |
| `mapper/screens/map/hints.py` | hints concern: `_seat_*`/`_hint_*`/`_toast` helpers | `HintsOps` |
| `mapper/screens/map/__init__.py` | re-exports `MapScreen` only — no logic (`map/__init__.py:12`) | — |
| `mapper/screens/common.py` | shared screen helpers, hint-string constants, `MapHintLine` (A1 — it is NOT in the hints concern) | — |
| `mapper/screens/prompt.py` · `construct.py` · `repo.py` · `plug_repo.py` · `import_preview.py` · `home.py` | the four literal modals, `ConstructScreen`, `RepoScreen`, `PlugRepoScreen`, `_ImportPreviewScreen`, `HomeScreen` (A2, A3, A5b, A6, A7, A4) | — |

### How a key binding reaches a concern

1. The key chord lives in the single seat, `mapper/keymap.py` (`SCOPE_MAP` rows — keymap is data, zero dependencies).
2. The core class turns the seat into Textual bindings once: `BINDINGS = screen_bindings(SCOPE_MAP)` at `mapper/screens/map/screen.py:58` (`KEY_SCOPE = SCOPE_MAP` at `:57`; `screen_bindings` builds `Binding` objects in `mapper/screens/common.py:184`). **Spike-measured on Textual 8.2.8:** a `BINDINGS` declared in a plain mixin is silently NOT merged — so bindings live only on the core (`evidence/arq-mro-spike.transcript`).
3. Textual dispatches the key to `action_<name>`, resolved through the mixin MRO — the action method may live in any mixin (e.g. `action_export_svg` in `exporting.py:25`, `action_search` in `searching.py:434`). `on_*` handlers run from **every** MRO class that defines them, so handler names must be pairwise-disjoint across the 12 modules — guarded, not hoped for.
4. Because `BINDINGS` is generated from the keymap seat, adding a key row to `SCOPE_MAP` reaches the screen with **no edit to `screen.py`** — but the keymap file itself is a shared seam (see below).

### The dependency rules (`docs/ARCHITECTURE.md` §3, enforced by `tests/test_mod_deps.py`)

- **No `screens → app` edge, ever.** Neither `import mapper.app` (any alias) nor `from mapper.app import …`, at any scope, anywhere under `mapper/screens/` — the F4 function-local exception was deleted with the F4 design (B-02 closed at A2). The only legal direction is `app` re-exporting what moved.
- **`screens/map` imports only its allow-list** (`model`, `store`, `views`, `search`, `export`, `mermaid`, `diff`, `keymap`, `design`, `widgets`, `screens/common`, `screens/prompt`, `osopen` names, and the `mapper.screens` package `__init__` re-exports). The concern modules never import each other, with two declared exceptions (LED .12): `screen.py` MAY import its 11 concern modules (it composes the class), and a concern MAY import the non-mixin value class `NavigationModel` from `navigation.py` (`focus_mode.py:9` ships the edge). Concerns import the modal screens via the package `__init__` re-exports — `drafts.py:13` (`DraftGuardScreen`), `opening.py:11` (`FactoryScreen`), `searching.py:10` (`CoverageScreen`) — and that `__init__` never imports a sibling screen module or `screens/map`.
- **Who may import `screens/map`:** only `mapper/app` (the re-export), `screens/repo.py` (`NavigationModel` only, `repo.py:31`), and the sibling screens that construct `MapScreen` — `screens/home.py:42` and `screens/import_preview.py:24`, always from `mapper.screens.map`, never from `mapper.app`.
- **`open_external` call sites ⊆ {`osopen.py` (its definition), `screens/map/opening.py:46`}** — `app.py` references no launcher name since B3.
- Concerns communicate through `self` on the composed class; a concern module never calls another concern's method except through the frozen F2 surface (`docs/ARCHITECTURE.md` §4).

### Where to patch in tests (the F4 patch surface)

Eight names in the suite are monkeypatched. Seven are **module-global repoints** — each is a module-global of the module that READS it, and every patch site in `tests/` must target that module (so a vacuous repoint cannot pass):

| Patch name | Patch target module (reader) | Suite patch sites |
|------------|------------------------------|-------------------|
| `MAX_RENDER_NODES` | `mapper.screens.map.searching` | `tests/test_search.py` ×5 |
| `SearchIndex` | `mapper.screens.map.searching` | `tests/test_search.py` ×1 (attribute assignment) |
| `refusal_sentence` | `mapper.screens.common` | `tests/test_inc9q.py` ×1 |
| `save_svg` | `mapper.screens.map.exporting` | `tests/test_app.py` ×2, `tests/test_inc9c.py` ×1 |
| `pan_extent` | `mapper.screens.map.panning` | `tests/test_en8.py` ×1 |
| `LayeredRenderer` | `mapper.screens.import_preview` | `tests/test_en8.py` ×1 |
| `preview_csv` | `mapper.screens.home` | `tests/test_inc9c.py` ×1, `tests/test_inc9n.py` ×1 |
| `GitHubConnector.fetch` | **not repointed** — a class-attribute patch on the shared class object; survives the move | `tests/test_app.py`, `test_en8.py`, `test_inc9c.py`, `test_inc9.py` |

The guard map of record is `PATCH_SURFACE` at `tests/test_mod_compat.py:54`, asserted by the AST guard at `tests/test_mod_compat.py:356`. Rule for any NEW patchable name: bind it at module level in the module that reads it, patch THAT module in the test, and add the name→module row to `PATCH_SURFACE` in the same commit.

### The guards that keep it so (one line each)

| Guard file | Freezes |
|------------|---------|
| `tests/test_mod_structure.py` (10) | the tree is real: 7 siblings own their names, `MapScreen` in the package core, 11 mixins on the MRO, `app.py` ≤ 400 lines — tmp-copy RED arms |
| `tests/test_mod_dispatch.py` (7) | `BINDINGS`/constants/`@on`/`DEFAULT_CSS` only on the core; method names pairwise-disjoint across the 12 modules; pilot-driven dispatch through the mixins |
| `tests/test_mod_compat.py` (32) | 21 re-exports resolve with object identity; every suite patch site targets the module that reads the name (`PATCH_SURFACE`); AT-067/AT-069 baselines |
| `tests/test_mod_deps.py` (13) | zero `mapper.app` imports under `screens/` (both forms, any scope); §3 rules on the shipped ASTs (the map allow-list, the two LED-.12 edges, the `screens/map` importer set, `open_external` sites) |
| `tests/test_mod_census.py` (3) | the F1/F2 freeze is mechanical: AST census over the package diffs clean vs `spike/census.json` |
| `tests/test_mod_bodies.py` (4) | every moved method body `ast.dump`-equal to the Inc-0 baseline; no undefined globals in any new module |
| `tests/test_mod_parity.py` (3) | painted output of the scripted session byte-equal to the pre-move goldens at 118/87 columns; mutant-copy RED |

### Shared seams for parallel work (post-mortem "Parallel-work outcome"; B-111 deferred)

Concern **bodies** are disjoint — a lane owns exactly one module file. These seams remain shared, and any lane touching them meets every other lane there:

- `BINDINGS` is generated on the core class (`screen.py:58`) from the `SCOPE_MAP` seat in `mapper/keymap.py` — **any new or changed key edits the keymap seat** (a shared file; B-111 proposes a per-concern bindings table the core composes, so a key change edits one concern row instead).
- `mapper/app.py` `__all__` — every new public name re-exports through it.
- `docs/ARCHITECTURE.md` §3/§4 — every structural change edits the module map and the F1–F5 rows (an F1/F2 change is trigger A3 — trunk work, never lane work).
- `PATCH_SURFACE` at `tests/test_mod_compat.py:54` — every patch-target move edits the guard map.
- the census baseline `spike/census.json` (B-108: must move under `tests/` before this folder is archived).
- the cycle guard sees direct importers only (`tests/test_mod_deps.py:303`, B-109).

### Recipes

**To add a search action (concern: searching):**
1. Add the key row to the `SCOPE_MAP` seat in `mapper/keymap.py` (shared seam — expect a merge hotspot; B-111).
2. Implement `action_<name>` in `mapper/screens/map/searching.py` (`SearchingOps`). `BINDINGS` needs no edit — it is generated from the seat.
3. If the action needs state or a helper another concern already touches, check the F1 roster / F2 surface in `docs/ARCHITECTURE.md` §4 first: a new shared attribute or cross-concern method is an F1/F2 amendment — census re-run (`spike/census.json`) and trunk sign-off, not a lane edit.
4. Test by driving real keys (`MapperApp(tmp_path)` + `run_test` + `pilot.press(...)`); the hint line goes through the hints concern if the action needs a hint.

**To add an export format (concern: exporting):**
1. Add the writer to `mapper/export.py` (headless — takes a `rich.Text` snapshot + path, like `save_svg`/`save_png`).
2. Bind it at module level in `mapper/screens/map/exporting.py` (`ExportingOps`) and add `action_export_<fmt>`; add the key row to `SCOPE_MAP` in `mapper/keymap.py`.
3. If the suite must monkeypatch the new writer, patch `mapper.screens.map.exporting.<name>` in the test and add the row to `PATCH_SURFACE` (`tests/test_mod_compat.py:54`) in the same commit — never import the name from `mapper.app` in a `screens/` module (that re-creates the banned edge and kills the patch).
4. Update the `export` and `map screen` rows of `docs/ARCHITECTURE.md` §2/§3 (trunk work).

### Components / modules touched

| Module | Role in this batch |
|--------|--------------------|
| `mapper/app.py` | 5255 → 340 lines; `MapperApp` + `main` + `CSS` + `__all__` re-export block only |
| `mapper/screens/map/` (13 files) | the `MapScreen` package: core `screen.py` + 11 concern mixins + `navigation.py` + re-export-only `__init__.py` |
| `mapper/screens/{common,prompt,construct,repo,plug_repo,import_preview,home}.py` | the 7 sibling-screen modules (new files) |
| `mapper/screens/factory.py`, `settings.py` | B-02 closed: the 4 function-local `mapper.app` imports became module-level imports of `screens/common`/`screens/prompt` |
| `docs/ARCHITECTURE.md` | TARGET rows for the moved files; amended §3 dependency rules; F1–F5 freeze rows |
| `tests/test_mod_*.py` (7 new files, 72 nodes) | the guards and ATs above; 18 pre-existing test files re-pointed (0 weakened, 0 deleted) |

### Diagrams

- [`diagrams/module-structure.md`](diagrams/module-structure.md) — the shipped import graph of `mapper/screens/`.

### Evidence checklist — docs-writer

- ✓ module map derived from the shipped tree (`grep -n "^class " mapper/screens/map/*.py`, `wc -l`), not memory · ✓ key-dispatch path read from `screen.py:54-58` + `common.py:184` + the MRO spike transcript · ✓ dependency rules match `docs/ARCHITECTURE.md` §3 and LED .12 · ✓ patch surface matches `tests/test_mod_compat.py:54` and `04-validation.md` Layer A · ✓ shared seams quoted from `05-postmortem.md` "Parallel-work outcome" · ✓ no user-visible change claimed — AT-065 parity goldens at 118/87 columns cited · ✓ no operator paths, home paths or account names in this artifact.
