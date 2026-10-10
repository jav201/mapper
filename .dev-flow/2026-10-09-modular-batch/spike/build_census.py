"""Build census/mapscreen-census.md from census.json + hand classification.

Concern taxonomy (closed set, one concern per method, classified by the unit
worker from each method's name + docstring + body):

- lifecycle : construction, compose, mount, graph establishment, load warnings,
              resize, focus/blur/reume events, region visibility, focus-owner
              query, focus parking, app-level chrome actions (rail/inspector/
              palette/help).
- nav       : cursor movement, breadcrumbs, open-ficha / home / back, repoint.
- pan       : pan offsets: clamp, reclaim, step actions, animated/selection pan,
              renderer pan consumption query.
- views     : everything the canvas/rail paint from: geometry, painted-set,
              coverage glyph, minimap, legend docking, view-state assembly,
              refresh/paint pass, render-mode toggles, fold state, layout repaint.
- search    : search index/order/hits, query echo, counts/pagination, search
              input handling, live-search predicate, branch unfolding, hit
              walking, coverage-gap walking.
- draft     : draft guard, save, field application, draft cursor/field focus.
- edits     : structural mutations: add/remove attachments, add child, archive
              (+ subtree helpers), focus-mode mutation guard.
- undo      : snapshot stack push/pop, undo action.
- focus     : focus mode toggle (graph/nav swap).
- hints     : hint line + toast machinery: event toast, seat lookups, field/
              search/resting hints, pan-hint clearing, rebind declaration,
              walk toast, "opened ..." hint suffix.
- open      : opening attachments/documents through the OS/factory boundary.
- export    : SVG export action and its view-state/budget helpers.
"""
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "census.json").read_text(encoding="utf-8"))

CONCERN = {
    # lifecycle & chrome
    "__init__": "lifecycle", "compose": "lifecycle", "_notice_load_warnings": "lifecycle",
    "_establish_graph": "lifecycle", "on_mount": "lifecycle", "_chrome_width": "lifecycle",
    "_apply_region_visibility": "lifecycle", "action_toggle_rail": "lifecycle",
    "action_toggle_inspector": "lifecycle", "action_focus_rail": "lifecycle",
    "_park_focus": "lifecycle", "on_resize": "lifecycle", "on_descendant_focus": "lifecycle",
    "on_descendant_blur": "lifecycle", "on_screen_resume": "lifecycle",
    "_restore_after_legend": "lifecycle", "_focus_owner": "lifecycle",
    "action_palette": "lifecycle", "action_help": "lifecycle",
    # nav
    "_current_crumb": "nav", "_repoint": "nav", "action_next_sibling": "nav",
    "action_prev_sibling": "nav", "action_child": "nav", "action_parent": "nav",
    "action_open_ficha": "nav", "action_home": "nav", "action_back_or_home": "nav",
    # pan
    "_clamp_pan": "pan", "_consumes_pan": "pan", "_reclamp_pan": "pan", "_pan": "pan",
    "action_pan_left": "pan", "action_pan_right": "pan", "action_pan_up": "pan",
    "action_pan_down": "pan", "_move_pan": "pan", "_pan_revealing_selection": "pan",
    # views
    "action_collapse_branch": "views", "_header_rows": "views", "_header_rows_for": "views",
    "_canvas_width": "views", "_canvas_size": "views", "_unpainted_ids": "views",
    "_painted_ids_for": "views", "_current_renderer": "views", "legend_view": "views",
    "legend_view_left": "views", "legend_docked": "views", "legend_closed": "views",
    "_declare_after_layout": "views", "_branch_coverage_glyph": "views",
    "_minimap_entry_limit": "views", "_minimap_text": "views", "_open_paint_pass": "views",
    "_view_state": "views", "refresh_canvas": "views", "action_toggle_outline": "views",
    "action_toggle_radial": "views", "action_toggle_diff": "views",
    # search
    "_search_index": "search", "_whole_graph_tally": "search", "_query_echo": "search",
    "_suspended_count_line": "search", "_count_line": "search", "_pagination_text": "search",
    "_search_order": "search", "_search_hits": "search", "action_search": "search",
    "on_input_submitted": "search", "on_input_blurred": "search", "_search_is_live": "search",
    "_unfold_onto": "search", "_branch_name": "search", "_walk_hits": "search",
    "action_next_hit": "search", "action_prev_hit": "search", "action_coverage": "search",
    "_incomplete_order": "search", "_goto_gap": "search", "action_next_gap": "search",
    # draft
    "_paint_draft_hint": "draft", "_drop_orphan_draft": "draft", "has_pending_draft": "draft",
    "guard_open": "draft", "_guard_draft": "draft", "_apply_field": "draft",
    "action_save_draft": "draft", "_save_draft": "draft", "_focused_field_id": "draft",
    "_refocus_field": "draft", "on_field_input_left": "draft",
    # edits
    "on_ficha_inspector_attachment_add_requested": "edits", "_add_attachment": "edits",
    "on_ficha_inspector_attachment_remove_requested": "edits", "_remove_attachment": "edits",
    "action_add_attachment": "edits", "action_remove_attachment": "edits",
    "_guard_focus_mutation": "edits", "action_add_child": "edits", "_add_child": "edits",
    "action_archive": "edits", "_archive": "edits", "_subtree_size": "edits",
    "_remove_subtree": "edits",
    # undo
    "_snapshots": "undo", "_push_snapshot": "undo", "_pop_snapshot": "undo",
    "action_undo": "undo",
    # focus
    "action_toggle_focus": "focus",
    # hints
    "_event_toast": "hints", "_seat_row": "hints", "_seat_glyph": "hints",
    "_seat_label": "hints", "_field_hint": "hints", "_search_hint": "hints",
    "_declare_rebind": "hints", "_walk_toast": "hints", "_hint_with_opened": "hints",
    "_clear_pan_hint": "hints", "_resting_hint": "hints",
    # open
    "on_ficha_inspector_attachment_activated": "open", "action_open_documents": "open",
    # export
    "action_export_svg": "export", "_export_view_state": "export",
    "_within_export_budget": "export",
}

methods = D["methods"]
by_name = {m["name"]: m for m in methods}
unclassified = [m["name"] for m in methods if m["name"] not in CONCERN]
assert not unclassified, f"unclassified: {unclassified}"

CONCERN_ORDER = ["lifecycle", "nav", "pan", "views", "search", "draft",
                 "edits", "undo", "focus", "hints", "open", "export"]

STATE_ATTRS = set(D["state_first"])

# ---------------------------------------------------------------- section 1
lines = []
lines.append("| method | first line | lines | concern | reads own state (self) | writes state (self) | calls MapScreen methods | module-level names used |")
lines.append("|---|---|---|---|---|---|---|---|")
for m in methods:
    own_reads = [r for r in m["reads"] if r in STATE_ATTRS]
    api_reads = [r for r in m["reads"] if r not in STATE_ATTRS and r not in by_name]
    calls = [c for c in m["calls"] if c in by_name]
    read_cell = ", ".join("`" + r + "`" for r in own_reads) or "—"
    if api_reads:
        read_cell += f" <br>(API: {', '.join(api_reads)})"
    lines.append(
        f"| `{m['name']}` | {m['first_line']} | {m['line_count']} | {CONCERN[m['name']]} "
        f"| {read_cell} "
        f"| {', '.join('`'+w+'`' for w in m['writes']) or '—'} "
        f"| {', '.join('`'+c+'`' for c in calls) or '—'} "
        f"| {', '.join('`'+n+'`' for n in m['module_names']) or '—'} |")
sec1 = "\n".join(lines)

# ---------------------------------------------------------------- section 2
readers = defaultdict(set)
writers = defaultdict(set)
for m in methods:
    c = CONCERN[m["name"]]
    for r in m["reads"]:
        readers[r].add(c)
    for w in m["writes"]:
        writers[w].add(c)

lines = ["| attribute | first assigned | concerns reading | concerns writing | multi-writer |",
         "|---|---|---|---|---|"]
for attr, first in sorted(D["state_first"].items(), key=lambda kv: kv[1]["line"]):
    rs = readers.get(attr, set())
    ws = writers.get(attr, set())
    lines.append(
        f"| `{attr}` | `{first['where']}` :{first['line']} "
        f"| {', '.join(sorted(rs)) or '—'} "
        f"| {', '.join(sorted(ws)) or '—'} "
        f"| {'**YES**' if len(ws) > 1 else ''} |")
sec2 = "\n".join(lines) + """

Footnotes:
- `lifecycle` appears in every "concerns writing" cell because `__init__`
  declares all 30 slots; **YES** means a concern other than `__init__`'s also
  writes it. Rows where `lifecycle` is the *only* writer are pure `__init__`
  declarations.
- `_last_save_error` is the one attribute with an external writer the self-scan
  cannot see: the module-level `_save_or_toast` assigns it through its `screen`
  parameter (app.py:300). MapScreen itself only declares and reads it.
"""

# ---------------------------------------------------------------- section 3
matrix = defaultdict(int)
for m in methods:
    src = CONCERN[m["name"]]
    for call in m["calls"]:
        if call in by_name:
            matrix[(src, CONCERN[call])] += 1
lines = ["caller ↓ / callee → | " + " | ".join(CONCERN_ORDER) + " | total out", "|---|" + "---|" * (len(CONCERN_ORDER) + 1)]
for a in CONCERN_ORDER:
    row = [str(matrix.get((a, b), 0)) for b in CONCERN_ORDER]
    lines.append(f"| {a} | " + " | ".join(row) + f" | {sum(matrix.get((a, b), 0) for b in CONCERN_ORDER)} |")
totals = [sum(matrix.get((a, b), 0) for a in CONCERN_ORDER) for b in CONCERN_ORDER]
lines.append("| total in | " + " | ".join(map(str, totals)) + f" | {sum(totals)} |")
sec3 = "\n".join(lines)

# ---------------------------------------------------------------- section 6
def group_attrs(concerns):
    reads, writes = set(), set()
    for m in methods:
        if CONCERN[m["name"]] in concerns:
            reads |= set(m["reads"])
            writes |= set(m["writes"])
    return reads, writes

def shared_state(group_a, rest):
    """Attributes written by one side and read-or-written by the other."""
    ra, wa = group_attrs(group_a)
    rb, wb = group_attrs(rest)
    return sorted((wa & (rb | wb)) | (wb & (ra | wa)))

cuts = [
    ("export", ["export"]),
    ("open", ["open"]),
    ("undo", ["undo"]),
    ("draft", ["draft"]),
    ("edits", ["edits"]),
    ("focus", ["focus"]),
    ("hints", ["hints"]),
    ("search+nav", ["search", "nav"]),
    ("views+pan", ["views", "pan"]),
    ("lifecycle", ["lifecycle"]),
]
lines = []
for label, group in cuts:
    rest = [c for c in CONCERN_ORDER if c not in group]
    shared = shared_state(set(group), set(rest))
    n_methods = sum(1 for m in methods if CONCERN[m["name"]] in group)
    n_lines = sum(m["line_count"] for m in methods if CONCERN[m["name"]] in group)
    calls_out = sum(matrix.get((a, b), 0) for a in group for b in rest)
    calls_in = sum(matrix.get((b, a), 0) for b in rest for a in group)
    lines.append(
        f"- **{label}** ({n_methods} methods, {n_lines} lines): shared attributes with the rest = "
        f"{len(shared)} {shared}; calls out = {calls_out}, calls in = {calls_in}.")
sec6 = "\n".join(lines)

rc_callers = {CONCERN[m["name"]] for m in methods if "refresh_canvas" in m["calls"]}
rc_sites = sum(1 for m in methods if "refresh_canvas" in m["calls"])

md = f"""# MapScreen census — `mapper/app.py` (ARQ input for `2026-10-09-modular-batch`)

Mechanical census of `class MapScreen(Screen)` (AST-measured span lines
1536–4987, 3452 lines including decorators, 126 methods) so an architect can
split it into modules. Generated by
`census/ast_census.py` (AST) + `census/build_census.py`; attribute/call/name
columns are AST-computed, not eyeballed. Facts only — cut decisions belong to
the architect.

## Concern definitions (closed set, 12)

| concern | definition |
|---|---|
| `lifecycle` | construction, `compose`, mount, graph establishment, load warnings, resize, focus/blur/resume events, region visibility, focus-owner query, focus parking, app-level chrome actions (rail/inspector/palette/help) |
| `nav` | cursor movement, breadcrumbs, open-ficha/home/back, draft-driven repoint |
| `pan` | pan offsets: clamp, reclaim, step actions, animated/selection pan, renderer pan-consumption query |
| `views` | everything the canvas/rail paint from: geometry, painted-set, coverage glyph, minimap, legend docking, view-state assembly, refresh/paint pass, render-mode toggles, fold state, layout repaint |
| `search` | search index/order/hits, query echo, counts/pagination, search input handling, live-search predicate, branch unfolding, hit walking, coverage-gap walking |
| `draft` | draft guard, save, field application, draft cursor/field focus |
| `edits` | structural mutations: add/remove attachments, add child, archive (+ subtree helpers), focus-mode mutation guard |
| `undo` | snapshot stack push/pop, undo action |
| `focus` | focus mode toggle (graph/nav swap) |
| `hints` | hint line + toast machinery: event toast, keymap-seat lookups, field/search/resting hints, pan-hint clearing, rebind declaration, walk toast, "opened …" suffix |
| `open` | opening attachments/documents through the OS/factory boundary |
| `export` | SVG export action and its view-state/budget helpers |

Method counts per concern:
{chr(10).join(f"- `{c}`: {sum(1 for m in methods if CONCERN[m['name']] == c)} methods, {sum(m['line_count'] for m in methods if CONCERN[m['name']] == c)} lines" for c in CONCERN_ORDER)}

## 1. Method table (file order)

{sec1}

## 2. State table (every `self.<attr>` assigned in MapScreen)

All 30 attributes are first assigned in `__init__` (line 1547). "Concerns
writing" includes every method that assigns the attribute. **YES** = written by
more than one concern — the coupling points.

{sec2}

## 3. Cross-concern call matrix (method-call counts)

Counts of `self.<method>(...)` calls between concerns (diagonal = intra-concern).

{sec3}

## 4. Other top-level classes/functions of app.py

Lines 1–1535 and 4990–5255. "Used by" = imports/references found by grepping
`mapper/` (excluding app.py) and `tests/` (`-w` name match). Comments/docstring
mentions in other mapper modules are noted as such, not counted as code use.

| name | lines | app.py-internal deps | used by (mapper/) | used by (tests/) |
|---|---|---|---|---|
| `map_hint` | 158–162 (5) | — | — | test_en2, test_gate2, test_inc9c, test_inc9d |
| `MapHintLine` | 165–190 (26) | — | — | — (used only inside app.py) |
| `home_hint` | 196–199 (4) | — | — | — (used only inside app.py) |
| `_home_door_key` | 204–211 (8) | — | — | — (used only inside app.py) |
| `screen_bindings` | 228–237 (10) | — | — | — (used only inside app.py) |
| `keybar_groups` | 240–246 (7) | — | keymap.py (comment), screens/factory.py (lazy import), screens/settings.py (lazy import) | test_inc9, test_inc9c, test_inc9e |
| `_refusal_toast` | 249–259 (10) | — | — | — (used only inside app.py) |
| `_save_or_toast` | 261–311 (51) | `_refusal_toast` | screens/factory.py (lazy import) | test_draft_hygiene, test_g6_store_surrogates, test_inc9c, test_inspector |
| `NavigationModel` | 314–351 (37) | — | — | test_app |
| `_path_refusal` | 358–365 (8) | — | — | test_inc9p, test_inc9q |
| `_PromptScreen` | 368–413 (46) | — | screens/factory.py (lazy import) | test_confirm_markup, test_en5, test_en7, test_en8, test_g6_store_surrogates, test_inc9c, test_inc9d, test_inc9m, test_inc9n |
| `_ConfirmScreen` | 416–469 (54) | — | — | test_confirm_markup, test_ddr_archive_own, test_en5, test_en8, test_g6_store_surrogates, test_inc9c, test_worklist_safety |
| `_TemplateScreen` | 472–508 (37) | — | — | test_en8 |
| `_FichaScreen` | 511–583 (73) | — | — | test_en8, test_en9 |
| `ConstructScreen` | 586–624 (39) | `_refusal_toast` | — | test_en5, test_en7, test_inc9c, test_seed_safety |
| `HomeScreen` | 632–1112 (481) | ConstructScreen, MapScreen, PlugRepoScreen, _ImportPreviewScreen, _PromptScreen, _TemplateScreen, _home_door_key, _refusal_toast, home_hint, keybar_groups, screen_bindings | — | test_app, test_en5, test_en8, test_inc9, test_inc9c–i, test_keymap, test_legend_design, test_repair_cycles, test_repair_fields, test_repair_sidecar, test_sparkline_floor |
| `_ImportPreviewScreen` | 1115–1181 (67) | MapScreen, _PromptScreen, _save_or_toast, keybar_groups, screen_bindings | — | test_en8, test_fold, test_g6_store_surrogates, test_inc9, test_inc9c, test_inc9d, test_keymap, test_repair_cycles, test_repair_depth |
| `PlugRepoScreen` | 1184–1231 (48) | RepoScreen, keybar_groups, screen_bindings | — | test_app, test_en7, test_en9, test_inc9, test_inc9c, test_inc9e, test_inc9f, test_inc9j–l, test_keymap |
| `RepoScreen` | 1234–1533 (300) | NavigationModel, keybar_groups, screen_bindings | — | conftest, test_app, test_en5, test_en8, test_en9, test_hermetic, test_inc9, test_inc9c–m, test_keymap |
| `MapScreen` | 1536–4987 (3452) | MapHintLine, NavigationModel, _ConfirmScreen, _FichaScreen, _PromptScreen, _path_refusal, _save_or_toast, keybar_groups, map_hint, screen_bindings | darkside.py, search.py, views/layered.py, views/outline.py, views/radial.py, views/state.py, widgets/inspector.py, widgets/rail.py — all comments/docstrings only, no code imports | 55 test files (see section 5) |
| `MapperApp` | 4990–5236 (247) | HomeScreen, MapScreen, screen_bindings | — | ~68 test files |
| `main` | 5239–5251 (13) | MapperApp | — (matches in github.py/views/lane.py are git-branch strings) | test_darkside, test_gate2, test_inc9d–i, test_inc9l–n, test_lane, test_office |

## 5. Test coupling (tests that read app.py's SOURCE)

Scanned `tests/` for `app.py"`, `app.__file__`, `inspect.getsource`,
`ast.parse`. Files that only `from mapper.app import ...` (runtime import) are
not listed; almost every driving test imports `MapperApp`/`MapScreen` that way
and would follow a move via a re-export without source changes.

| test file | what it scans app.py for | breaks if the scanned code moves to another mapper module? |
|---|---|---|
| `test_app_imports_used.py` | AST unused-import census of `mapper/app.py` (AT-064) | No — app.py still exists and passes; but the moved module's imports leave the census silently |
| `test_draft_hygiene.py` | AST of `mapper.app.__file__`: `MapScreen.__init__` AnnAssign census (`_last_save_error`), package-wide `getattr` ban on it, `MapperApp.action_quit` must call `guard_open` | **YES** — `_find_class(tree, "MapScreen")` / `"MapperApp"` raise AssertionError if either class leaves app.py |
| `test_darkside_census.py` | ~20 hard-coded `("mapper/app.py", "<exact source line>")` pairs (styles, tokens, Text.assemble literals) | **YES** — every pair whose line moves to another file fails the census |
| `test_keymap.py` (:319) | AST string literals of `mapper.app.__file__`; every chord-shaped literal must be a key the map binds (M-1) | No — scan silently covers less; moved hint strings escape the arm |
| `test_en5.py` | `FILES = ("mapper/app.py",)` Spanish-string AST census | No — same silent-coverage-loss shape |
| `test_en7.py` (:221) | `inspect.getsource(app_module)`: `check_consume_key` must be absent | No — trivially passes after the move; guard rots |
| `test_search.py` | `_app_tree()` parses `inspect.getfile(MapScreen)` — follows the class; arms census `_search_order`/`_view_state`/`_pagination_text` bodies and MapScreen-vs-module-level name collisions | Mostly no — follows the class via inspect; **but** the name-collision arm (`methods` vs module-level `helpers`) assumes MapScreen's file has no same-named module-level functions |
| `test_arch_osopen_callers.py` | Package-wide AST: LAUNCH_NAMES (`open_external`, `_default_launcher`, `startfile`) may appear only in `{{app.py, osopen.py}}`; osopen import surface outside app.py is an allow-list | **YES** — moving a launcher call site or osopen import out of app.py changes both asserted sets |
| `test_inc9p.py` / `test_inc9q.py` | Assert `W2`/`CR_F3`/`ATT_HARD` strings are NOT in app.py/osopen.py ("one home" arms) | No — assertions become trivially true; arms rot |
| `test_crumb.py` (:350) | `rglob("*.py")` over the whole package: integer 118 spellings | No — file-agnostic |
| `test_a3_census.py` | `git ls-files` globs `mapper/**` + `tests/**`: `.render(` call-site migration census, headless-boundary import census | No — glob-based, follows moves across tracked files; asserts on `MapScreen._FOCUS_REGIONS` values follow the class |
| `test_en1/en3/en4.py` | Spanish-string AST census — FILES tuples do **not** include app.py (osopen/github/factory/editor; views/*; store/darkside/widgets) | No — app.py not scanned |

Driving helpers shared via `tests/test_draft_save.py` (`_seed_map`, `_open`, `_answer`, …) and `tests/inc3_support.py` import `MapScreen` at runtime — unaffected by file moves as long as `mapper.app` re-exports the names.

## 6. Seams (candidate cut lines, facts only)

For each candidate group: number of shared attributes (written by one side and
read or written by the other), and cross-concern call counts from section 3.

{sec6}

Notes for the architect (facts):
- `refresh_canvas` (views, 123 lines) is called from {len(rc_callers)} of 12 concerns
  ({", ".join(sorted(rc_callers))}) — {rc_sites} call sites total; the single
  hottest out-edge target. "(API: …)" in the reads column marks names that are
  not MapScreen instance state: inherited Textual `Screen`/`App` members
  (`notify`, `query_one`, `app`, `size`, `focus`, `set_focus`,
  `call_after_refresh`, `query`, `push_screen`), MapScreen class constants
  (`KEY_SCOPE`, `PAN_STEP_X/Y`), and imported constants (`MIN_CANVAS_WIDTH`).
- `graph`, `nav`, `focus_active` are each written by 3+ concerns
  (see section 2) — `focus` in particular rewrites `graph`/`nav` wholesale.
- `_guard_draft` (draft) is called from `nav` (open-ficha/home/back), `edits`
  (attachments/add-child/archive) and `views` (`refresh_canvas` drops an orphan
  draft before painting) — every leaving/editing action funnels through it.
- `_search_memo` is invalidated by views (`_open_paint_pass`, at the top of
  every repaint) and written/read only by search (`_search_order`) — a clean
  hand-off attribute with one writer per lifecycle phase.
"""

out = HERE / "mapscreen-census.md"
out.write_text(md, encoding="utf-8")
sizes = {s.splitlines()[0][:60]: len(s.splitlines()) for s in [sec1, sec2, sec3, sec6]}
print(f"wrote {out}")
print(f"total lines: {len(md.splitlines())}")
print(f"section lines: methods={len(sec1.splitlines())} state={len(sec2.splitlines())} "
      f"matrix={len(sec3.splitlines())} seams={len(sec6.splitlines())}")
