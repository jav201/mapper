# ARQ proposal — modular split of `mapper/app.py` (`2026-10-09-modular-batch`)

> **Intake note.** The unit referenced `.dev-flow/2026-10-09-modular-batch/PLAN.md`; that
> directory does **not** exist on disk (only `2026-10-09-canon-batch` and
> `2026-10-09-hygiene-batch` do). This proposal therefore works from the operator objective
> quoted at intake — *"tenemos que modularizar para poder paralelizar el trabajo, eso es
> primordial"* — plus `docs/ARCHITECTURE.md` R-009 (the recorded decision NOT to split
> `app.py`, whose re-open condition, "≥3 increments touching `app.py` for unrelated
> reasons", is now met) and the factual base `census/mapscreen-census.md`.
>
> **Goal.** Split `mapper/app.py` (5255 lines, 10 `*Screen` classes) so later batches get
> parallel product lanes: two workers changing different features must never edit the same
> file. Behaviour-preserving. Every increment ≤ 4 source files.

---

## 1 · Target module map

All paths under `mapper/`. "Must NOT hold" rows are the mechanical bans the PDR freezes.

### 1a · What stays in `mapper/app.py` (~350 lines, from 5255)

| Keeps | Why |
|---|---|
| `MapperApp` (:4990–5236), `main` (:5239–5251), the `CSS` block | The `App` object is `app`'s reason to exist (ARCHITECTURE §2). `MapperApp.action_quit` calls `isinstance(s, MapScreen)`, `s.has_pending_draft()`, `s.guard_open()`, `s._guard_draft(...)` (:5214–5231) — that surface is frozen (§3 F5). |
| Re-exports of **every** moved name (§5 list) | Tests do `from mapper.app import X` at ~110 sites; a re-export makes the move invisible to them. |
| Bound names `MAX_RENDER_NODES` (:58, from `views.layered`) and `refusal_sentence` (:49, from `osopen`) | The two monkeypatch surfaces (§5). The `from`-imports **stay** even after the last reader moves out. |

Must NOT hold after the cut: any `Screen` subclass other than `MapperApp`, any module-level
helper with a home below, any MapScreen concern method.

### 1b · New leaf modules under `mapper/screens/`

| Path | Owns (from app.py) | Exposes | Must NOT hold |
|---|---|---|---|
| `mapper/screens/common.py` *(new)* | `screen_bindings` (:228), `keybar_groups` (:240), `map_hint` (:158), `home_hint` (:196), `_home_door_key` (:204), `_refusal_toast` (:249), `_save_or_toast` (:261), `_path_refusal` (:358); string constants `COUNT_REGION_ID` (:90), `PAN_INERT_HINT` (:109), `PAN_EDGE_HINT` (:110), `SEARCH_COUNT_SUBJECT` (:118), `SEARCH_ACTIVE_LABEL` (:131), `SEARCH_SUSPENDED_NOTICE` (:132), `_QUERY_ECHO_CELLS` (:150), `_HINT_BRANCHES/_HINT_BRANCH_CELLS/_HINT_NAME_OVERHEAD/_HINT_NAME_MIN_CELLS` (:222–225) | All of the above | Screen classes; `NavigationModel`; any **top-level** binding of `refusal_sentence` (see §5: `_path_refusal` reads it lazily through `mapper.app`) |
| `mapper/screens/prompt.py` *(new)* | `_PromptScreen` (:368–413), `_ConfirmScreen` (:416–469), `_TemplateScreen` (:472–508), `_FichaScreen` (:511–583) | The four modal classes | `ConstructScreen`; store calls; the SEC-H2 `markup=False` rule stays inside each modal |
| `mapper/screens/construct.py` *(new)* | `ConstructScreen` (:586–624) | `ConstructScreen` | The other modals |
| `mapper/screens/home.py` *(new)* | `HomeScreen` (:632–1112, 481 lines) | `HomeScreen` | Map-screen concern code |
| `mapper/screens/repo.py` *(new)* | `RepoScreen` (:1234–1533, 300 lines) | `RepoScreen` | `NavigationModel` (imports it from `screens/map/navigation.py`) |
| `mapper/screens/plug_repo.py` *(new)* | `PlugRepoScreen` (:1184–1231) | `PlugRepoScreen` | — |
| `mapper/screens/import_preview.py` *(new)* | `_ImportPreviewScreen` (:1115–1181) | `_ImportPreviewScreen` | — |

B-02 (ARCHITECTURE §3 known violations) is closed as part of this: `factory.py:198/:217`
and `settings.py:89` become module-level imports from `screens/common.py`;
`factory.py:507` becomes a module-level import of `_PromptScreen` from `screens/prompt.py`.
The four function-local imports — each of which exists only to dodge the cycle — disappear.

### 1c · New package `mapper/screens/map/` — the MapScreen home

| Path | Owns | Exposes | Must NOT hold |
|---|---|---|---|
| `mapper/screens/map/__init__.py` | Re-export only (mirrors `screens/__init__.py:4-11`) | `MapScreen` | Logic (same rule as root `package` row) |
| `mapper/screens/map/screen.py` | `class MapScreen(<11 mixins>, Screen)`: the **lifecycle concern** (`__init__` :1547 with all 30 attribute slots, `compose` :1632, `_notice_load_warnings`, `_establish_graph`, `on_mount`, `_chrome_width`, `_apply_region_visibility`, `action_toggle_rail/inspector/focus_rail`, `_park_focus`, `on_resize`, `on_descendant_focus/blur`, `on_screen_resume`, `_restore_after_legend`, `_focus_owner`, `action_palette`, `action_help`), all class constants (`KEY_SCOPE` :1539, `PAN_STEP_X/Y` :1810, `MIN_CANVAS_WIDTH` :1730, `REVEAL_MARGIN_CELLS` :2424, `METER_STEPS` :3031, `_TOAST_CHROME_CELLS` :3111, `_FOCUS_REGIONS` :3150, `UNDO_DEPTH` :3731, `EXPORT_*` :4326/:4448/:4666, `_MINIMAP_*` :2719–2722) and `BINDINGS` | `MapScreen` | Any method of the other 11 concerns |
| `mapper/screens/map/painting.py` | **views** mixin (22 methods/686 lines: `refresh_canvas` :3311, `_view_state`, `_declare_after_layout`, header/canvas sizing, minimap, legend docking, fold/render-mode/diff toggles) | mixin class | — |
| `mapper/screens/map/searching.py` | **search** mixin (21 methods/674 lines: `_search_order` :3190, `_walk_hits` :4053, count/pagination/echo, hit & gap walking) | mixin class | A top-level `MAX_RENDER_NODES` binding (§5) |
| `mapper/screens/map/panning.py` | **pan** mixin (10 methods/264 lines: `_clamp_pan`, `_consumes_pan`, `_reclamp_pan`, `_pan`, `_move_pan`, `_pan_revealing_selection`, 4 step actions) | mixin class | — |
| `mapper/screens/map/hints.py` | **hints** mixin (11 methods/180 lines: `_event_toast`, `_seat_*`, `_field_hint`, `_search_hint`, `_resting_hint`, `_declare_rebind`, `_walk_toast`, `_hint_with_opened`, `_clear_pan_hint`) **plus `MapHintLine`** (:165–190) | mixin class, `MapHintLine` | — |
| `mapper/screens/map/navigation.py` | `NavigationModel` (:314–351) **plus nav** mixin (9 methods/77 lines: cursor actions, `_repoint`, `_current_crumb`, open-ficha/home/back) | `NavigationModel`, mixin class | — |
| `mapper/screens/map/drafts.py` | **draft** mixin (11 methods/168 lines: `_guard_draft` :3473, `guard_open`, `has_pending_draft`, `_save_draft` :3535, `_apply_field`, `_drop_orphan_draft`, `_paint_draft_hint`, field focus) | mixin class | — |
| `mapper/screens/map/editing.py` | **edits** mixin (13 methods/185 lines: attachments, add-child, archive, `_remove_subtree`, `_guard_focus_mutation`) | mixin class | — |
| `mapper/screens/map/undo.py` | **undo** mixin (4 methods/45 lines: `_snapshots`, `_push_snapshot`, `_pop_snapshot`, `action_undo`) | mixin class | — |
| `mapper/screens/map/focus_mode.py` | **focus** mixin (`action_toggle_focus` :4152) | mixin class | — |
| `mapper/screens/map/opening.py` | **open** mixin (2 methods/53 lines: `on_ficha_inspector_attachment_activated` :3626 with the `open_external` call site, `action_open_documents` :4835) | mixin class | — |
| `mapper/screens/map/exporting.py` | **export** mixin (3 methods/217 lines: `action_export_svg` :4339, `_export_view_state` :4668, `_within_export_budget`) | mixin class | — |

ARCHITECTURE §2 needs a matching amendment: the `screens` row currently owns
`mapper/screens/*.py`, and under the fnmatch semantics the map itself records ("`*` also
matches `/`") that glob would double-claim the subpackage. Amend the `screens` row to name
its top-level files literally (the same trick §2 already uses for `mapper/` top-level
files) and add a `map screen` row owning `mapper/screens/map/*.py`.

---

## 2 · How `MapScreen` is split — mechanism comparison

Three real mechanisms, measured against the census facts.

### Mechanism A — one mixin class per concern, composed into `MapScreen`  *(recommended)*

Each concern module defines a plain class (`class PaintingOps: …`) whose methods use
`self.` exactly as today; `screen.py` ends with
`class MapScreen(PaintingOps, SearchingOps, PanningOps, HintsOps, NavigationOps, DraftsOps, EditingOps, UndoOps, FocusModeOps, OpeningOps, ExportingOps, Screen)`.

- **Two workers, different files? YES, literally.** A search feature touches only
  `searching.py`; an export feature only `exporting.py`. This is the operator's goal.
- **Textual dispatch preserved.** `action_*` resolution and `BINDINGS` collection both walk
  the MRO in Textual 8.2.8, so actions and keys behave byte-identically. The known hazard
  is the other direction — the message pump calls an `on_*` handler found in **every** MRO
  class (ARCHITECTURE risk A-8). Census §1 assigns each of the 126 methods to **exactly
  one** concern, so the partition is disjoint by construction; a cheap derived test
  (AST-walk the 12 modules, assert pairwise-disjoint method names) keeps it that way.
- **The 30 shared attributes cost nothing.** They stay `self.*` slots declared in the core
  `__init__`; `graph`/`nav`/`focus_active` with 3+ writers (census §2) need no state-owner
  refactor; `refresh_canvas` keeps its 25 call sites in 9 concerns (census §3 note)
  untouched; `_guard_draft` stays the funnel (nav, edits, views).
- **`mapper.app.MapScreen` stays importable** via re-export; `MapperApp.action_quit`'s
  `isinstance` is unaffected (same class object).
- **Test impact:** runtime-import tests follow re-exports unchanged; private-attribute
  paths (`screen._search_order`) still resolve through the MRO. Only the source-reading
  tests of census §5 need generalising (§5 below).

### Mechanism B — collaborator objects owned by the screen

`self._search = SearchController(self)`; 126 methods move onto plain objects.

- Parallel lanes: yes, same file granularity as A.
- But Textual dispatch is **not** preserved for free: every `action_*` (≈30) and every
  `on_*` handler must remain a method on `MapScreen` and delegate, because Textual
  dispatches by method name on the widget. Each of the 25 `refresh_canvas` call sites and
  every cross-concern call (`self._search_order(...)` → `self._search.order(...)`) is a
  rewritten line, and tests that reach private helpers on the screen break unless shimmed.
  The diff stops being cut/paste and starts being a rewrite — the opposite of
  behaviour-preserving on a 3452-line class.

### Mechanism C — package with free functions per concern

`mapper/screens/map/searching.py` holds `def walk_hits(screen, ...)`, called from thin
methods left on the class.

- Worst of both: the shim methods stay in `screen.py`, so feature work that adds an action
  still edits the shared file (the collision we are removing), **and** every body is
  rewritten `self.x` → `screen.x`.

### Verdict

**Mechanism A, inside the package layout of §1c.** It is the only one of the three that
delivers disjoint feature files while keeping Textual's dispatch, `BINDINGS`, the 30-slot
shared state, and the `_guard_draft`/`refresh_canvas` funnels byte-identical. Mechanism B
is the documented fallback (§7 R-1) if the spike increment contradicts the MRO evidence.

---

## 3 · Frozen interfaces — what the PDR must pin before parallel work starts

The freeze is the census itself, made executable (`census/ast_census.py` already produces
it; a new test re-runs it and diffs `census.json`).

- **F1 — the state roster.** The 30 attributes of census §2, declared only in
  `MapScreen.__init__`, with the writer matrix as the discipline: no attribute gains a
  writer concern, no new cross-concern attribute is added, without amending the census.
  (`_last_save_error`'s external writer is `_save_or_toast` via its `screen` parameter,
  census §2 footnote — that signature is part of the freeze.)
- **F2 — the cross-concern method surface.** Every method with an in-edge from another
  concern (census §3): from painting `refresh_canvas`, `_view_state`, `_current_renderer`,
  `_canvas_size`, `_canvas_width`, `_header_rows`, `_unpainted_ids`, `_open_paint_pass`,
  `_declare_after_layout`, `_pagination_text`, `_minimap_text`; from panning `_clamp_pan`,
  `_consumes_pan`, `_reclamp_pan`, `_move_pan`, `_pan_revealing_selection`; from searching
  `_search_order`, `_search_hits`, `_search_is_live`, `_search_index`, `_count_line`,
  `_query_echo`, `_branch_name`, `_unfold_onto`, `_incomplete_order`, `_goto_gap`; from
  hints `_event_toast`, `_seat_glyph`, `_seat_label`, `_field_hint`, `_search_hint`,
  `_resting_hint`, `_declare_rebind`, `_walk_toast`, `_hint_with_opened`, `_clear_pan_hint`;
  from drafts `_guard_draft`, `guard_open`, `has_pending_draft`, `_save_draft`,
  `_drop_orphan_draft`, `_paint_draft_hint`, `_apply_field`, `_focused_field_id`,
  `_refocus_field`; from editing `_guard_focus_mutation`, `_subtree_size`,
  `_remove_subtree`; from undo `_push_snapshot`, `_pop_snapshot`, `_snapshots`; from
  navigation `_repoint`, `_current_crumb`; from the core `_establish_graph`,
  `_apply_region_visibility`, `_focus_owner`, `_chrome_width`. Names and signatures frozen;
  a concern module never calls a method of another concern that is not on this list.
- **F3 — the core's class surface.** `MapScreen` keeps inheriting `textual.Screen`;
  `KEY_SCOPE`, `PAN_STEP_X/Y`, `MIN_CANVAS_WIDTH`, `_FOCUS_REGIONS`, `REVEAL_MARGIN_CELLS`,
  `METER_STEPS`, `_TOAST_CHROME_CELLS`, `UNDO_DEPTH`, `EXPORT_*`, `_MINIMAP_*` and
  `BINDINGS` stay class attributes of the core (mixins never shadow them).
- **F4 — the patch surface.** `mapper.app.MAX_RENDER_NODES` and
  `mapper.app.refusal_sentence` remain bound in `app.py` and are read **at call time
  through the module object** by their consumers (§5).
- **F5 — the app↔screen surface.** `MapperApp` relies on `has_pending_draft()`,
  `guard_open()`, `_guard_draft(proceed, on_hold)` and `isinstance(s, MapScreen)`
  (app.py:5214–5231); widgets rely on the `on_*` handler names (census §1: the
  `FichaInspector.*`, `Input.*`, descendant-focus events). None may be renamed.

---

## 4 · Dependency rules to add to ARCHITECTURE.md §3

| Rule | Text to add |
|---|---|
| `screens/map` row | May import: `model`, `store`, `views`, `search`, `export`, `mermaid`, `diff`, `keymap`, `design`, `widgets`, `screens/common`, `screens/prompt`, `osopen` (see next row). **Forbidden:** any module-level import of `mapper.app` (cycle through the re-export); imports between concern modules or of sibling `screens/*` modules — concerns communicate through `self` on the composed class, never through each other's modules. The single sanctioned exception: function-local `import mapper.app` to read the F4 patch names. |
| `osopen` row amendment | The one non-`osopen` `open_external` call site moves from `app.py:3626` to `mapper/screens/map/opening.py`; the ban "any module but `app` → `open_external`" becomes "any module but `app` and `screens/map/opening`". `tests/test_arch_osopen_callers.py` derives its allow-list from the ASTs and is updated in the same increment. |
| `screens/common` + `screens/prompt` rows | Importable by any `screens/*` module and by `app`; they never import `app` or `widgets` internals beyond what `screens` already may. This is the remediation §3 already prescribes for B-02 — after Inc-A1/A2 the "known violations" note and the four function-local imports are deleted. |
| `app` row | `app` additionally depends on `screens/map` (the `MapScreen` re-export). No other module may import `screens/map` except `screens/repo.py` (`NavigationModel` only) and `mapper.app`. |

---

## 5 · Compatibility plan

### 5a · Re-exports `mapper/app.py` must keep

Measured by `grep -rhoE "from mapper\.app import [^\n]+" tests` (plus attribute-access
users from census §4): `MapScreen`, `HomeScreen`, `RepoScreen`, `PlugRepoScreen`,
`_ImportPreviewScreen`, `ConstructScreen`, `MapperApp` (never moves), `_PromptScreen`,
`_ConfirmScreen`, `_TemplateScreen`, `_FichaScreen`, `NavigationModel`, `keybar_groups`,
`map_hint`, `_save_or_toast`, `COUNT_REGION_ID`, `PAN_INERT_HINT`, `SEARCH_ACTIVE_LABEL`,
`SEARCH_COUNT_SUBJECT`, `SEARCH_SUSPENDED_NOTICE`, `_QUERY_ECHO_CELLS`, `MAX_RENDER_NODES`,
`GitHubConnector` (already a re-export today, app.py:26). One `from … import` block per
new home module, kept in `app.py` permanently.

### 5b · The two monkeypatch targets

- `MAX_RENDER_NODES` — patched on the `mapper.app` module object at `test_search.py:2393,
  2456, 2549, 2649, 2690`; read today as an `app.py` global in `_search_order` (:3196) and
  `_walk_hits` (:4053). After the move to `screens/map/searching.py` those two functions
  must read it via a function-local `import mapper.app` + attribute access. A top-level
  `from … import MAX_RENDER_NODES` in `searching.py` would bind a copy and the patches
  would silently stop biting — that import shape is banned by rule F4 and asserted by the
  disjoint-names guard of §7 R-5.
- `refusal_sentence` — patched at `test_inc9q.py:393` (on `mapper.app`; the `:403` patch on
  `factory_module` is independent and unaffected); read today in `_path_refusal` (:365).
  Same rule: after `_path_refusal` moves to `screens/common.py`, it reads
  `mapper.app.refusal_sentence` at call time.

### 5c · Source-reading tests (census §5) — per test, the change

| Test | Change (all in **Inc-0**, before any move) |
|---|---|
| `test_draft_hygiene.py` | `_find_class(tree, "MapScreen")` parses `mapper.app.__file__` and raises if the class leaves. Change: parse `inspect.getfile(MapScreen)` for the MapScreen arms; the `MapperApp` arm keeps parsing `app.py`. |
| `test_darkside_census.py` | 14 hard-coded `("mapper/app.py", "<exact line>")` pairs rot per extraction. Change: locate each pinned line by content across `mapper/**/*.py` (assert exactly one home) instead of by path. |
| `test_keymap.py:319` | Chord-literal AST scan of `app.py` only → scan `mapper/**/*.py`; moved hint strings stay under the M-1 arm. |
| `test_en5.py` | `FILES = ("mapper/app.py",)` Spanish census → scan the package (or extend FILES per new module in the extraction increments). |
| `test_en7.py:221` | `inspect.getsource(app_module)` absence check → scan package sources. |
| `test_app_imports_used.py` | AT-064 unused-import census of `app.py` → run per new module, or the moved imports leave the census silently. |
| `test_search.py` | Follows the class via `inspect.getfile(MapScreen)` — no change for the body arms; the MapScreen-vs-module-level name-collision arm must be re-scoped from "app.py's module level" to "the `screens/map` package's module levels". |
| `test_arch_osopen_callers.py` | Allow-list `{app.py, osopen.py}` for LAUNCH_NAMES and the osopen-import surface → add `screens/map/opening.py` (in Inc-B3, not Inc-0). |
| `test_inc9p.py` / `test_inc9q.py` | "One home" arms assert strings absent from `app.py`/`osopen.py` → extend the scanned set to the new homes or make them package-wide with an allow-list. |
| `test_a3_census.py`, `test_crumb.py`, `test_en1/3/4.py` | Glob/file-agnostic — **no change**. |

Driving helpers (`tests/test_draft_save.py`, `tests/inc3_support.py`) import at runtime —
unaffected as long as §5a holds.

---

## 6 · Increment cut

Rule applied: `modules(A) ∩ modules(B) = ∅` at file granularity (ARCHITECTURE §6). Honest
consequence: **every increment that deletes lines from `app.py` collides with every other
on that file**, so the extraction spine is serial; parallelism exists (a) inside Inc-0,
(b) between test-only follow-ups and the spine, and — the deliverable — (c) between
product lanes after Inc-B11.

**Inc-0 — test generalisation (0 source files; the six rows of §5c except osopen/inc9pq,
which ride their extraction increments).** The six test files are mutually disjoint → may
run as parallel sub-lanes.

**Spine A — `app.py` shrink, serial, helpers first (each increment re-exports from app.py):**

| Inc | Files (source) | Moves |
|---|---|---|
| A1 | `screens/common.py`*(new)*, `app.py`, `screens/factory.py`, `screens/settings.py` | §1b common row; B-02 helper imports repointed |
| A2 | `screens/prompt.py`*(new)*, `app.py`, `screens/factory.py` | Four modals; `factory.py:507` repointed — B-02 closed |
| A3 | `screens/construct.py`*(new)*, `app.py` | `ConstructScreen` |
| A4 | `screens/home.py`*(new)*, `app.py` | `HomeScreen` (needs A1 helpers + A2 modals) |
| A5 | `screens/map/navigation.py`*(new, `NavigationModel` only)*, `screens/repo.py`*(new)*, `app.py` | `RepoScreen` + the nav model |
| A6 | `screens/plug_repo.py`*(new)*, `app.py` | `PlugRepoScreen` |
| A7 | `screens/import_preview.py`*(new)*, `app.py` | `_ImportPreviewScreen` |

A2–A7 delete disjoint line ranges; if the orchestrator ever accepts import-block merges,
A3/A6/A7 could burst after A1+A2 — under the strict rule they are serial.

**Inc-B0 — MapScreen wholesale move (after A1–A7; its imports need their homes).**
Files: `screens/map/__init__.py`*(new)*, `screens/map/screen.py`*(new)*, `app.py`.
The whole class body moves unchanged; `screen.py` imports helpers from
`screens/common.py`, modals from `screens/prompt.py`, `NavigationModel` from
`navigation.py` — never from `app.py`. `app.py` is now ~350 lines: imports/re-exports,
`MapperApp`, `main`.

**Spine B — one concern per increment, serial on `screen.py` (delete methods + bases
line), 2 source files each.** Order = risk: smallest/cleanest first, the spike first of
all, the 686-line painting concern last.

| Inc | New mixin module | Census motivation for the order slot |
|---|---|---|
| B1 | `hints.py` (incl. `MapHintLine`) | **Spike.** 0 shared attributes (census §6) — proves MRO dispatch of `action_*`/`on_*`/`BINDINGS` with a pilot-driven hint test before anything coupled moves |
| B2 | `exporting.py` | 3 shared attrs, 0 calls in (§6) |
| B3 | `opening.py` (+ `test_arch_osopen_callers.py` allow-list) | 4 shared, 1 call out; carries the osopen §3 amendment |
| B4 | `undo.py` | 5 shared, calls in only from draft/edits/focus |
| B5 | `focus_mode.py` | 1 method, but rewrites `graph`/`nav` wholesale (§2) — moved early so the multi-writer set is frozen under F1 |
| B6 | `editing.py` | 13 methods, funnel consumer of `_guard_draft` |
| B7 | `drafts.py` | The funnel itself; after its consumers |
| B8 | `navigation.py` gains the nav mixin | File exists since A5 — only `screen.py` + `navigation.py` touched |
| B9 | `searching.py` | 21 methods; the F4 `MAX_RENDER_NODES` lazy-read lands here |
| B10 | `panning.py` | 10 methods, shares 21 attrs with painting — kept adjacent to it |
| B11 | `painting.py` | 22 methods incl. `refresh_canvas`; moves last so `screen.py` remains the integration point throughout |

**Inc-B12 — map amendment + executable freeze (docs + tests, 0 source).**
ARCHITECTURE.md §2/§3 amended per §1c/§4; new test re-runs `census/ast_census.py` over the
package and diffs `census.json` (F1/F2 made mechanical).

**Order constraints:** Inc-0 ∥ anything → Spine A (serial) → B0 → Spine B (serial) → B12.
Test-only follow-ups (inc9p/9q arm extension, en5 FILES if not package-scanned) ride their
extraction increment or run parallel to the spine afterwards.
**Payoff after B11:** `searching.py`, `editing.py`, `painting.py`, `exporting.py`,
`drafts.py`, `home.py`, `repo.py`… are disjoint files — two feature workers never share a
file. That is the operator's "primordial".

---

## 7 · Risks

| # | Risk (census fact) | Mitigation in this plan | What would change the recommendation |
|---|---|---|---|
| R-1 | Textual dispatches `on_*` across the **whole MRO** — a handler name in two mixins runs twice (ARCHITECTURE A-8; census §1: 126 methods, 12 disjoint concerns) | The partition is disjoint by construction; a derived AST test asserts pairwise-disjoint method names across the 12 modules; **B1 is a spike** that proves `action_*`/`BINDINGS` MRO behaviour with real keys before the coupled concerns move | If the spike shows `action_*`/`BINDINGS` do NOT resolve through mixin bases on Textual 8.2.8 → fall back to Mechanism B (collaborators) for the coupled concerns, accepting the delegation shims |
| R-2 | 30 shared attributes, 15 multi-writer; `graph`/`nav`/`focus_active` written by 3+ concerns (census §2) | Mixins keep `self.*` semantics byte-identical; F1 freezes the writer matrix; B12's census-diff test reddens any new cross-writer | If PDR instead wants state ownership enforced by the type system → Mechanism B with a `MapState` object; that is a rewrite, not this batch |
| R-3 | `refresh_canvas` called from 9 concerns, 25 sites (census §3 note); `_guard_draft` funnels nav+edits+views | Both stay methods; zero call-site rewrites | A decision to narrow `refresh_canvas`'s contract (e.g. split paint vs repoint) is an A3 and returns to trunk — not folded into this batch |
| R-4 | `MAX_RENDER_NODES` / `refusal_sentence` patches bite via module globals (§5b) | F4 lazy-read rule | — |
| R-5 | A future worker top-level-imports an F4 name or gives two mixins the same method name — both failures are **silent** (tests pass, patch/ dispatch quietly dead) | One guard test: AST-walk `screens/map/*.py`, assert (a) no top-level binding of the two F4 names, (b) pairwise-disjoint method names | — |
| R-6 | Source pins rot: 14 `("mapper/app.py", line)` pairs in `test_darkside_census.py`; `test_draft_hygiene` raises if `MapScreen` leaves app.py (census §5) | Inc-0 generalises them **before** the first move, so no extraction increment ever runs red against a stale pin | If PDR refuses to touch those tests, MapScreen cannot leave `app.py`: reduce to Spine A only (app.py → ~3900 lines, small screens extracted, **no** concern lanes) — a strictly weaker outcome against the operator's goal |
| R-7 | `MapperApp.CSS` selectors name classes (`MapScreen, PlugRepoScreen`, modal selectors :5036–5145); a rename during the move breaks styling silently | No class is renamed; the spike's pilot test paints at real sizes | — |
| R-8 | Cycle: `screens/map/screen.py` importing helpers from `mapper.app` at module level would re-enter a partially-initialised `app` | Spine A lands the helper homes **before** B0; §4 bans module-level `app` imports from the package | — |
| R-9 | Spine B is serial on `screen.py` — 12 increments, one worker | Each is ≤2 source files and Kimi-sized; the serial phase is short, and parallelism is the **output**, not the method | If calendar pressure demands parallel extraction: pre-declare all 11 mixin shells in B0 (13 files — over the 4-file cap; needs a cap waiver) and let B-increments run parallel on disjoint mixin files, resolving only the `screen.py` deletion hunks at merge |

---

*Prepared by Kimi K3 for the PDR of `2026-10-09-modular-batch`. No code changed.*
