# Increment 027 — Inc-9c · wording, naming, hints, toasts, and the Inc-9 test-strength fixes

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `027` — **Inc-9c**, the second half of the Inc-9 split (`VERDICT-inc9-2026-09-30.md` § "Split") |
| Agent | `software-dev` |
| Date | 2026-09-30 |
| Authority | `VERDICT-inc9-2026-09-30.md` (operator answers **K1–K4**, the coordinator's defect rulings); `A-112` (+ dated note below); `increment-025-inc9.md` (copy table, `INC9-Fn`); `increment-026-inc9b.md` (`INC9B-F1`); `state.json` → `p3_progress.G6_CLOSED_AND_INC-9_LANDED_2026-09-30` (`G6-SEC-F9`) |
| Starting state | `feat/ui-next-batch-02` @ `bab76c1`, clean |
| Commits | `930be78` (arms, RED) → `90c8ce8` (toasts) → `8303a60` (wording, groups, K2/K4) → `5495f5e` (hints, K3) → `2147205` (UX-F2/F3/F4/F10/F11) → `a0b63ba` (test-strength, G6-SEC-F9) → `9994499` (census reads painted headers) → `(the commit that adds this record)` (this record) |
| Source files | **6** (see below). Operator approval 2026-09-30: *"Déjalo terminar con los 6"* — the operator's global cap is now 4 source files per increment; this increment finishes with its 6 declared files and goes no further |

The six source files: `mapper/keymap.py`, `mapper/app.py`, `mapper/darkside.py`, `mapper/screens/settings.py`,
`mapper/screens/help.py`, and `mapper/screens/factory.py` — the last **only** for the two `INC9-SEC-F1` toasts
(`generado`, `no se pudo generar`) and the factory hint line. `mapper/screens/palette.py` and `screens/editor.py` were
**not** touched (see `INC9C-F2`, `INC9C-F5`).

---

## 1 · What changed

1. **`INC9-SEC-F1` (MEDIUM) — toasts name the file and the exception TYPE, never a path.** Nine sites: create-map
   (seed and template), CSV not-found and unreadable, the export refusal's stale-file sentence, export failed, the
   export-success strip (`exportado <abs path>`), the factory `generado` / `no se pudo generar`, and the repo
   screen's unexpected-error toast. Same rule as `_save_or_toast` (`G6-C-F2`, `B-30`): the map or file NAME (through
   `plain()`) plus `type(e).__name__`.
2. **K1 — the ux reviewer's table, all of it.** 13 seat labels, the new `home enter` row, and the group headers.
   Group **ids** still name exactly one scope; a new `GROUP_HEADER` table carries the word the operator reads, so
   `nav` (map) and `tree` (factory) can both be `move`. `keymap.group_header` and `keymap.bar_group_order` are the
   seat's two readers for it (key bar, legend). Home `q quit` leaves the list group for its own (`exit`).
   `KEYBAR_MORE` is `all keys`; the legend's own-scope line reads `home end top/bottom`.
3. **K2 — `components`.** The `s` door, the crumb and the legend title read `components`; the tab strip marks no tab.
4. **K4 — `connect repo`.** The tab, the title, the crumb, the key-group header and the legend title
   (`legend · connect repo`, read from the screen's `legend_view`, not the scope id). Import and repo keep their names.
5. **K3 — key hints in English, each key with its seat label's word.** `keymap.hint_pair` builds a hint from the one
   seat row. See the table below for what moved and what did not.
6. **`INC9-UX-F2` / `INC9-F3`.** A real `?` with focus in the connect-repo field opens `legend · connect repo` and the
   field is unchanged. **Two causes, both measured, and the brief's recommendation was not enough:** Textual removes
   from the binding chain every key a focused widget would consume (`Input.check_consume_key` is `True` for every
   printable character), priority or not — and the priority pass never reaches the app's own non-priority `?`. So
   `priority=True` alone did nothing (`_binding_chain` held no `question_mark` at all). The fix has three parts, each
   killed by its own mutant: the field (`_RepoInput`) gives `?` up; the screen binds it with priority
   (`screen_bindings(priority_actions=("help",))`, this screen only, the seat untouched); the screen answers it
   (`action_help` → `app.action_help()`), so the legend still opens on this screen's scope.
7. **`INC9-UX-F3`.** The components grid is a `VerticalScroll` that is not itself a tab stop; focus starts on the
   first row instead of the last (each row used to focus its own cell on mount, so the tag chip below the fold won).
   Measured before: focus at `y=37` on a 34-row terminal, tab stops 10–13 of 14 off screen. After: every stop visible
   at 118×34 and 87×34.
8. **`INC9-UX-F10`.** The legend's key groups follow the key bar's order (`bar_group_order`), not the alphabet.
9. **`INC9-UX-F4`.** The home door list and the home key bar read their keys and names from the seat.
10. **`INC9-UX-F11`.** `enter` on home is a seat row (`open map`, `open_selected`), answered from anywhere on the
    screen, so the legend lists it. On the repo screen `↵ details` was advertised with **no binding and no handler**;
    it is removed from the bar and the body panel instead of being given a seat row (`INC9C-F1`).
11. **Test strength:** `INC9-CR-F2` (entry seat pinned as a literal — verified to pass on a `--depth 1` clone),
    `CR-F3` (comment: the tab drop was a repair), `CR-F4` (census judges `message=`), `CR-F5` (exact `? all keys`
    tail), `CR-F6` (focus ORDER), `CR-F7` (record correction, below), `CR-F8` (old home name absent), `INC9-F7`
    (stale `help.py` comment). **`G6-SEC-F9` (MEDIUM):** `_store_save_calls` is structural — see below.

### Correction to the Inc-9 record (`INC9-CR-F7`)

`increment-025-inc9.md` § "Changed sealed arms" says `EXPECTED_SEAT`: "60 label + 3 group fields re-derived". The
count was wrong: Inc-9 re-derived **60 label fields and 5 group fields** — `lista` → `list` on `home j`, `k`, `q` (3) and
`salir` → `leave` on `map q`, `esc` (2); the 12 factory/settings rows were ADDED, not re-derived. This note is the append the reviewer asked for; the Inc-9 record itself is not edited.

### `G6-SEC-F9`: what the census is now

`_store_save_calls` judged a call whose receiver's last identifier was literally `store`; `db = store; db.save(...)`
evaded it (demonstrated live by the security reviewer). It now judges the **method**, not the receiver's spelling:
every `Attribute` named `save` (a call, or a reference like `go = store.save`) and every `getattr(x, "save")` is a
site, and each must sit inside `_save_or_toast` or a `try` body. The one exemption, named and narrow: `self.save(...)`
inside `class MapStore` (its `create_seed` / `create_from_template`, whose callers carry the `try`). Six synthetic
evasions (alias of a parameter, of an attribute, of a chain; a bound method; `getattr`; an unknown receiver) and the
exemption are arms; the mutant `db = store; db.save(...)` in product code is RED (G1). Not covered, stated: a
string-built `getattr(store, "sa" + "ve")`.

## English copy table

Everything Inc-9c changed. "Surface" names where the string paints.

### Seat labels (`mapper/keymap.py::KEYMAP`)

| scope | key | old | new | surface |
|---|---|---|---|---|
| home | `j` | down | **next map** | key bar, legend, palette |
| home | `k` | up | **previous map** | key bar, legend, palette |
| home | `s` | settings | **components** | key bar, legend, palette |
| home | `↵` (new row) | — | **open map** | key bar, legend, palette |
| map | `f` | toggle focus | **focus branch** | key bar, legend, palette |
| map | `=` | toggle diff | **show/hide diff** | key bar, legend, palette |
| map | `z` | fold branch | **fold/unfold** | key bar, legend, palette |
| map | `m` | coverage | **coverage report** | key bar, legend, palette |
| map | `M` | next missing | **next incomplete** | key bar, legend, palette |
| repo | `j` | next sibling | **next branch** | key bar, legend, palette |
| repo | `k` | previous sibling | **previous branch** | key bar, legend, palette |
| repo | `q` | home | **back** | key bar, legend, palette |
| factory | `0` | start node | **back to start** | key bar, legend, palette |
| app | `ctrl+p` | command palette | **palette** | key bar, legend, palette |

### Group headers (`GROUP_HEADER`; the painted word)

| group id (scope) | old | new | surface |
|---|---|---|---|
| `doors` (home) | doors | **open** | key bar, legend |
| `list` (home) | list | **maps** | key bar, legend |
| `exit` (home, new; holds `q quit`) | (was in `list`) | **exit** | key bar, legend |
| `nav` (map) | nav | **move** | key bar, legend |
| `tree` (factory) | tree | **move** | key bar, legend |
| `app` (every screen) | app | **global** | key bar, legend |
| `plug` (connect repo) | plug | **connect repo** | key bar, legend |
| `settings` (components) | settings | **components** | key bar, legend |
| `repo` (repo) | `repo` in the legend, `nav` in the bar | **repo**, both | key bar, legend |

The **palette** paints the raw group id, not this header — `INC9C-F2`.

### Chrome

| where | old | new |
|---|---|---|
| key-bar overflow marker | `… +N  ? all` | `… +N  ? all keys` |
| legend own-scope line | `home end ends` | `home end top/bottom` (and it packs by the layout's row budget) |
| tab strip `p` | repo | **connect repo** |
| connect-repo title | connect repository | **connect repo** |
| connect-repo legend title | `legend · plug` | **`legend · connect repo`** |
| components legend title / crumb | `legend · settings` / settings | **`legend · components`** / **components** |
| active tab on components | `c browse` | **none** |
| home door list (`_empty_text`), from the seat | consult / repo / construct / template / import / factory | **browse maps / connect repo / build map / from template / import csv / factory** |

### Key hints (K3)

| surface | old | new |
|---|---|---|
| prompt footer | `↵ confirmar   esc cancelar` | `↵ confirm   esc cancel` |
| confirm footer | `y sí   n no` | `y yes   n no` |
| construct footer | `↵ crear   esc cancelar` | `↵ create   esc cancel` |
| repo body panel | `j/k navega tabla` / `↵ detalle` / `q inicio` / `? ayuda` | `j next branch` / `k previous branch` / `q back` / `? legend` (no `↵`: `INC9C-F1`) |
| factory hint | `j/k/h/l navega · d edita · i importa · g genera · 0 inicio · q salir` | `j/k/h/l move · d edit document · i import office file · g generate office file · 0 back to start · q back` |
| import hint | `s guarda · esc volver` | `s save map · esc back` |
| map resting hint | `navega con j/k/h/l · ↵ ficha · / buscar` | `navega con j/k/h/l · ↵ open card · / search` |
| rail hint | `rail · ↵ plegar rama · esc volver al mapa` | `rail · ↵ fold/unfold · esc back` |
| ficha hint | `… · ↵ guarda · esc deja el campo` | `… · ↵ save · esc leave field` |
| repo key bar | `nav j/k next/previous ↵ details` / `app … q home` | `repo j next branch  k previous branch  q back` / `global ctrl+p palette  ? legend` |

**Not moved, by scope:** the palette footer `↵ ejecutar esc cerrar` (`screens/palette.py`, a 7th source file —
`INC9C-F2`); the editor hints (`screens/editor.py`, `INC9C-F5`); the contextual search hint `n siguiente · N anterior
· esc limpiar` (about 25 sealed arms in `test_search` / `test_fold` pin its verbs, and `esc limpiar` states what `esc`
does in that state, which the seat's `back` does not — `INC9C-F5`); the components and connect-repo hint lines (prose
with a key glyph, Inc-EN). Toasts and prose stay Spanish.

### Toasts (`INC9-SEC-F1`)

| site | old | new |
|---|---|---|
| create map (seed, template) | `no se pudo crear el mapa: {e}` | `no se pudo crear el mapa 'mapa': OSError` |
| CSV not found | `archivo no encontrado: {path}` | `archivo no encontrado: nodos.csv` |
| CSV unreadable | `no se pudo leer CSV: {e}` | `no se pudo leer CSV 'nodos.csv': OSError` |
| export refusal (stale file) | `… el archivo en {path} no corresponde …` | `… el archivo layout.svg no corresponde …` |
| export failed | `exportación fallida: {e}` | `exportación fallida: OSError` |
| export success strip | `exportado {absolute path}` | `exportado layout.svg` |
| factory generated / failed | `generado: {target}` / `no se pudo generar: {exc}` | `generado: {name}` / `no se pudo generar: OSError` |
| repo unexpected error | `error inesperado: {exc}` | `error inesperado: OSError` |

## 2 · Files modified

| File | Kind | Why |
|---|---|---|
| `mapper/keymap.py` | source | labels, `GROUP_HEADER`, `group_header`, `bar_group_order`, `hint_pair`, `label_for`, `home enter`, `exit` group, comment (`CR-F3`) |
| `mapper/app.py` | source | toasts, home bar / door list from the seat, `open_selected`, repo bar and panel, plug (`_RepoInput`, title, `legend_view`, `action_help`), footers, hints, `screen_bindings(priority_actions)` |
| `mapper/darkside.py` | source | tab `connect repo`, `KEYBAR_MORE = "all keys"` |
| `mapper/screens/settings.py` | source | `components`, scrolling grid, focus on the first row |
| `mapper/screens/help.py` | source | header + bar-order legend groups, own-scope packing, stale comment (`INC9-F7`) |
| `mapper/screens/factory.py` | source — **only** the two toasts and the hint | see `INC9-SEC-F1`, K3 |
| `tests/test_inc9c.py` | test, new | 55 arms (`OPEN_STEPS` mechanism; empty now) |
| `tests/test_inc9.py`, `test_g6_store_surrogates.py`, `test_key_dispatch.py`, `test_keymap.py`, `test_rail.py`, `test_help_scope.py`, `test_export_state.py` | test | re-derived / strengthened arms — below |
| `01b-ux-decisions.md`, `01-requirements.md`, this file | doc | §3.6 `top/bottom`; dated note under `A-112`; record |

## 3 · How to test

```
set PYTHONUTF8=1
python -m pytest tests/test_inc9c.py tests/test_inc9.py tests/test_g6_store_surrogates.py -q
python -m pytest -q          # full default lane, about 15 minutes (run in sequential chunks if a timeout applies)
ruff check mapper tests      # 27, the baseline set
```

Manual: on the connect-repo screen type `owner/na` and press `?` (legend opens, field unchanged); open components
(`s`) at 87×34 and `tab` through it (the grid scrolls, every stop is visible); on home press `↵` with nothing focused.

## 4 · Test results

### RED first (`930be78`, `--runxfail`, source = `bab76c1`)

55 arms committed as strict xfails keyed by `OPEN_STEPS` (48 in `tests/test_inc9c.py`, 7 in
`test_g6_store_surrogates.py`); `--runxfail` on the base source: **55 failed**, 27 guard/control arms passed. Each
failed on its named defect (e.g. `toasts that can paint an absolute path: [('mapper/app.py', 948, 'path'), ...]`;
`'all' == 'all keys'`; `the census missed: alias of a parameter`). Two arms (the group-order arm and the
"bar and legend agree" arm) read `keymap.group_header` through a fallback so they fail on the ORDER, not on a missing
name. **One committed arm was wrong and was corrected in the toast commit (`INC9C-F9`):** the repo-unexpected-error
driver made the fetch raise inside `@work(thread=True)`, which exits the app (`exit_on_error`), so it was RED for a
different reason; it now drives the `except` through a stub worker.

### Targeted GREEN (`executed`)

`tests/test_inc9c.py`: 55 passed. `tests/test_inc9.py` + `tests/test_g6_store_surrogates.py` + `tests/test_rail.py`:
102 passed. After the last source commit, the affected files (inc9, inc9c, keymap, key_dispatch, palette, help_scope,
darkside, darkside_census, rail, legend_design, vocabulary_declaration, fold, no_operator_paths, overflow, crumb,
repair_layout, components, app, factory, g6): **579 passed, 10 xfailed** in 728 s (the 10 xfails are the pre-existing
`test_fold.py::test_f_a_*` (3) and the 7 G6-SEC-F9 arms as they stood before the test-strength commit).

### Full default lane (`executed`)

**Run as six sequential chunks by test file** (alphabetical, 62 files) on `a0b63ba`, no docs staged; chunk 3 (the
legend arms) took 587 s. Same tree, same interpreter, default markers.

| chunk | files | result |
|---|---|---|
| 0 | `test_a3_census` .. `test_darkside` | 188 passed |
| 1 | `test_darkside_budget` .. `test_hermetic` | 197 passed, 1 deselected, 3 xfailed |
| 2 | `test_import_csv` .. `test_legacy_fixture` | 278 passed |
| 3 | `test_legend_design` .. `test_radial` | 216 passed |
| 4 | `test_rail` .. `test_repair_store_boundary` | 415 passed, 17 deselected |
| 5 | `test_search` .. `test_worklist_safety` | 144 passed, 2 deselected |
| **sum** | | **1438 passed, 3 xfailed, 20 deselected, 0 failed** |

**Reconciled against 1373.** `--collect-only` per file on an extracted `git archive` of `bab76c1` and on this tree
(`test_views_hits.py` excluded from both: it needs a git repo): **+65** = 55 (`test_inc9c.py`) + 7 (`G6-SEC-F9`
arms, `test_g6_store_surrogates.py`) + 2 (`test_inc9.py`: the pinned-seat fence and the keyword-census arm) + 1
(`test_keymap.py`: the per-row `AT-N03` parametrization for the new `home enter` row). 1373 + 65 = **1438**, measured
1438. The 3 xfailed are the pre-existing `test_fold.py::test_f_a_*`; no Inc-9c arm is an xfail any more.

**0 failed.** `FLAKE-1` and the `FLAKE-2` candidate did not fire. The last commit after the lane (`9994499`) changes
`tests/test_inc9.py` only (the census reads the painted headers); that file was re-run: 40 passed.

### ruff (`executed`)

`ruff check mapper tests` → **26 errors**, against the baseline of **27** at `bab76c1`. The error SET (file + code +
message, positions stripped) is the baseline set **minus one**: `screens/settings.py` `F401` (`Horizontal` imported but
unused), which went away because that import line was replaced by `VerticalScroll`. No new finding.

### Shallow clone (`executed`)

`git clone --depth 1 file://…` of `a0b63ba` (one commit in the clone): `tests/test_inc9.py -k cd25` → 3 passed. On
`bab76c1` these arms ran `git show 6fe35f5:…`, which the reviewer reported as an ERROR on a shallow clone; that failure
was not re-measured here, only the pass of the literal version.

### Guards before the docs commit (`executed`)

`tests/test_fold.py` + `tests/test_no_operator_paths.py`, run with this record and the `A-112` note staged: **21 passed, 3 xfailed** (the 3 pre-existing `test_f_a_*`), 0 failed. The record writes the render path as `%TEMP%\claude\<project-slug>\...`, never a real profile path.

## Changed sealed arms (label values and measurements of a label's width only)

| Arm | Change | Justification |
|---|---|---|
| `test_key_dispatch.py::test_at_n03h_*` (`EXPECTED_SEAT`) | 13 labels; `home q` group `list` → `exit`; +1 row (`home enter`) | K1 label values; the declared group; the declared new row. `action`, `glyph`, `priority` of every pre-existing row unchanged — `test_cd25a_*` proves it against the pinned entry seat |
| `test_keymap.py` `EXPECTED_PER_SCOPE` | `home` 11 → 12 | the declared new row (a size fence is a deliberate edit by design) |
| `test_keymap.py::test_groups_for_keybar_order_and_glyphs` | group names `["nav", "app"]` → `["move", "global"]` | the painted header is the operator's word, not the id (K1) |
| `test_inc9.py` `CHROME_LEXICON` | + `components exit global incomplete keys move report unfold` | the declared vocabulary grows with the words painted (`A-112`'s rule: same commit) |
| `test_inc9.py` `DECLARED_REGROUPED` / `DECLARED_ADDED` | + `("lista","exit")`; + `("home","enter","open_selected")` | the declared `q` regroup; the declared row |
| `test_rail.py::test_at_n03e_*` | body counted without the marker; exact tail `  ? all keys` | `all keys` contains `l ` and was counted as the `l` key — **a label's word is a hidden input of the measurement** (`INC9B-F1`); the exact tail is `INC9-CR-F5` |
| `test_help_scope.py::test_inc8_p2_cr_f2_the_own_scope_group_is_its_title_and_two_lines` | "exactly two lines in both layouts" → the FEWEST lines the four items need at each layout's budget (2 modal, 3 docked), computed independently in the arm | `INC9B-F1`, realised: `home end top/bottom` (K1) makes the second pair 42 cells against the docked row's 37 (`LEGEND_DOCKED_ROW_CELLS`; grid: 44 − 4 padding − 1 scrollbar − 2 indent); the renderer cut it, dropping two keys (`test_hlr_n16_4_*`, `test_e3_*`, `test_e1_*` went red). The packing is now by the row budget; the modal is unchanged |
| `test_export_state.py::test_a_refusal_DECLARES_the_stale_artifact_it_leaves_behind` | `str(path) in message` → `path.name in message` and the absolute path forbidden | the old pin demanded the very leak `INC9-SEC-F1` closes |
| `01b-ux-decisions.md` §3.6 (read by `test_e3_*`) | `ends` → `top/bottom` | the ratified source the sealed arm compares the painted copy with |

Strengthened, not label-value arms (each has a mutant below): `test_inc9.py::test_cd25a_*` / `test_cd25b_*` (entry seat
as a literal), `test_llr_n06_2_5_notify_sites_are_coerced` (+ keyword arm), `test_cd9a_*` (focus order),
`test_a112_the_home_header_reads_its_one_name` (old name absent), `test_g6_store_surrogates.py::_store_save_calls`.

## Mutant table

Harness outside the repo (`%TEMP%\inc9c\mutants9c.py`): per mutant a sha256 pin of every touched file, byte-level
edits in each file's own line endings, the killing tests run, the verdict **printed before** the restore, the pins
re-checked. **Every pin matched after restore (45 of 45, and 5 of 5 in the survivor run); the tree was clean afterwards.** Run on `a0b63ba` (`X1` on `9994499`).

| # | Mutant | File | Killing arm(s) | Verdict |
|---|---|---|---|---|
| S1 | create-map toast back to `{e}` | `app.py` | `sec_f1_no_toast…[create-map]`, `sec_f1_census…` | **KILLED** 2 |
| S2 | CSV not-found toast back to `{path}` | `app.py` | `sec_f1_no_toast…[csv-not-found]` | **KILLED** |
| S3 | CSV unreadable toast back to `{e}` | `app.py` | `…[csv-unreadable]` | **KILLED** |
| S4 | export refusal names the absolute path | `app.py` | `…[export-too-large]`, `test_a_refusal_DECLARES…` | **KILLED** 2 |
| S5 | export failed back to `{e}` | `app.py` | `…[export-failed]` | **KILLED** |
| S6 | export success strip back to `str(path)` | `app.py` | `…[export-ok]` | **KILLED** |
| S7 | factory `generado` back to `{target}` | `factory.py` | `…[generate-ok]` | **KILLED** |
| S8 | factory failure back to `{exc}` | `factory.py` | `…[generate-failed]` | **KILLED** |
| S9 | repo unexpected error back to `{exc}` | `app.py` | `…[repo-unexpected]` | **KILLED** |
| S10 | a NEW leaky notify site (`f"… {e}"`) | `app.py` | `sec_f1_census…` | **KILLED** |
| S11 | `notify(message=f"…")` (`INC9-CR-F4`) | `app.py` | `test_llr_n06_2_5_notify_sites_are_coerced` | **KILLED** — *the pre-Inc-9c arm SURVIVES* |
| X1 | a Spanish group header (`nav` → `mover`) | `keymap.py` | `test_a112_the_chrome_is_english[seat]` (+`[keybar]`, `[headers]`, which judge the same lexicon) | **KILLED** |
| K1 | `focus branch` back to `toggle focus` | `keymap.py` | `k1_each_ruled_label…`, `test_at_n03h_*` | **KILLED** 2 |
| K2 | `nav` header back to `nav` | `keymap.py` | `k1_group_headers…` | **KILLED** |
| K3 | home `q` back in the list group | `keymap.py` | `k1_group_headers…`, `test_at_n03h_*` | **KILLED** 2 |
| K4 | `KEYBAR_MORE = "all"` | `darkside.py` | `k1_keybar_overflow…`, `test_at_n03e_*` | **KILLED** 2 |
| K5 | own-scope `ends` back | `help.py` | `k1_keybar_overflow…`, `test_e3_*` | **KILLED** 2 |
| K6 | door list spells `consult` | `app.py` | `ux_f4_home_reads…`, `k1_home_door_list…` | **KILLED** 2 |
| K7 | home key bar hand-written again | `app.py` | `ux_f4_home_reads…` | **KILLED** |
| K8 | components crumb back to `settings` | `settings.py` | `k2_components…` | **KILLED** |
| K9 | components marks tab `c` active | `settings.py` | `k2_components…` | **KILLED** |
| K10 | connect-repo `legend_view` dropped | `app.py` | `k4_connect_repo…`, `ux_f2…` | **KILLED** 2 |
| K11 | connect-repo title back to `connect repository` | `app.py` | `k4_connect_repo…` | **KILLED** |
| K12 | tab `p` back to `repo` | `darkside.py` | `k4_connect_repo…` | **KILLED** |
| K13 | `plug` header back to `plug` | `keymap.py` | `k4_connect_repo…` | **KILLED** |
| K14 | `repo` header renamed | `keymap.py` | `k4_import_and_repo…` | **KILLED** |
| H1 | prompt footer back to `confirmar` | `app.py` | `k3_modal_footers…` | **KILLED** |
| H2 | factory hint `q salir` | `factory.py` | `k3_the_factory_import…` | **KILLED** |
| H3 | map hint back to `↵ ficha` | `app.py` | `k3_the_factory_import…` | **KILLED** |
| H4 | repo panel re-adds `↵ detalle` | `app.py` | `k3_modal_footers…`, `k3_…dead_enter` | **KILLED** 2 |
| H5 | import hint back to `s guarda · esc volver` | `app.py` | `k3_the_factory_import…` | **KILLED** |
| H6 | a seat word drifts from its hint (`make office file`) | `keymap.py` | `test_at_n03h_*` | **KILLED** (the hint itself follows the seat by construction) |
| U1 | plug screen loses the priority `?` | `app.py` | `ux_f2…` | **KILLED** |
| U2 | `_RepoInput` consumes `?` again | `app.py` | `ux_f2…` | **KILLED** |
| U3 | plug screen has no `action_help` | `app.py` | `ux_f2…` | **KILLED** |
| U4 | components grid is a plain `Vertical` | `settings.py` | `ux_f3…` ×2 sizes | **KILLED** 2 |
| U5 | focus starts on the last row | `settings.py` | `ux_f3…` ×2 sizes | **KILLED** 2 |
| U6 | legend groups alphabetical again | `help.py` | `ux_f10…` ×7 screens | **KILLED** 7 |
| U7 | `home enter` row dropped | `keymap.py` | `ux_f11…`, `test_cd25a_*` | **KILLED** 2 |
| U8 | `open_selected` does nothing | `app.py` | `ux_f11…` | **KILLED** |
| C1 | a shipped seat row loses `priority` | `keymap.py` | `test_cd25a_*`, `test_at_n03h_*` | **KILLED** 2 |
| C2 | `KEYBAR_MORE = ""` (`CR-F5`) | `darkside.py` | `test_at_n03e_*` | **KILLED** — *the pre-Inc-9c arm SURVIVES* |
| C3 | `tab` on components skips a stop (`CR-F6`) | `settings.py` | `test_cd9a_*` | **KILLED** — *the pre-Inc-9c arm SURVIVES* (8 transitions, wrong order) |
| C4 | home header paints both names (`CR-F8`) | `app.py` | `test_a112_the_home_header_reads_its_one_name` | **KILLED** — *the pre-Inc-9c arm SURVIVES* |
| G1 | `db = store; db.save(...)` in product code (`G6-SEC-F9`) | `app.py` | `test_g6c_f3_census_every_store_save_call_is_guarded` | **KILLED** — *the pre-Inc-9c arm SURVIVES* |

"The pre-Inc-9c arm SURVIVES" means the same mutant was also run against the test file as it stood at `bab76c1`
(copied to a scratch name, deleted afterwards): `SURVIVED` for S11, C2, C3, C4 and G1, 5 of 5. `INC9-CR-F2` has no
mutant (it is an environment fix); it is shown by the shallow-clone run above. **Correction:** the message of
`9994499` says the pre-change census *survives* `X1`. That was not measured (the pre-change file fails on the new tree
for lexicon reasons, so its verdict says nothing); what is true is structural — it read only the group ids, never the
painted headers.

## Renders (`executed`; saved OUTSIDE the repo)

Real Textual renders of the final source tree, each as SVG (Textual's own screenshot) plus a text dump of the
composited frame, at **118×34** (reference), **87×34** and **140×45**. For each of `home`, `atlas` (a map view),
`import`, `connect_repo`, `repo`, `factory` and `components`: `<name>_screen_<size>` and `<name>_legend_<size>` (the
legend opened with `?`). 84 files in
`%TEMP%\claude\<project-slug>\<session>\scratchpad\renders-inc9c\` (outside the repo; the harness is
`%TEMP%\inc9c\render.py`).

Key bars at 118×34, read from the dumps:

```
home          maps j next map  k previous map  ↵ open map   open c browse maps  p connect repo  n build map … +8  ? all keys
atlas         move j next sibling  k previous sibling  h parent  l child  ↵ open card  / search  n next match … +26  ? all keys
repo          repo j next branch  k previous branch  q back   global ctrl+p palette  ? legend
connect_repo  connect repo esc back   global ctrl+p palette  ? legend
components    components q back  esc back   global ctrl+p palette  ? legend
factory       move j next sibling  k previous sibling  h parent  l child  0 back to start   factory q back … +6  ? all keys
```

At **87×34** the home bar shows `maps j next map  k previous map  ↵ open map   open c browse maps … +10  ? all keys`
(`q quit` and `ctrl+p` are behind the `+10`), the atlas and factory bars stop after `l child`, and the repo,
connect-repo and components bars fit whole. The legend titles read `legend · home`, `legend · repo`,
`legend · connect repo`, `legend · components`, `legend · factory`, `legend · atlas`. The components sheet at 87×34
scrolls (seen in the render: the first row is on screen and focused). Measured, not rendered: the factory hint is one
row at 118 and two at 87. Not rendered: a busy or overflowing map, the repo screen after a real fetch (the fetch is
stubbed to an empty graph).

## 5 · Risks

- **Wording is the operator's to correct** — the copy table is the place. Where the seat's word is long (`from template`,
  `connect repo`) the home door list and bar are long too; the bar truncates visibly (`… +N  ? all keys`).
- **The factory hint wraps to two rows at 87 columns** (measured; one row at 118). It is a seat-derived sentence, not
  a designed one.
- **The legend's own-scope group is 3 lines in the docked layout** (2 modal): a consequence of the operator's
  `top/bottom`. One row fewer for the keys section in the docked panel.
- **`?` is now special on one screen** (connect repo). Every other text field (the inspector's, the search field)
  still types `?`, by `H1`'s footer ("outside text fields"); the connect-repo screen is the exception only because
  its one widget is a text field.
- **Mixed language remains** until Inc-EN: toasts, prose hints, the palette footer, the editor hints, the search hint.

## 6 · Pending items, findings, carries

| id | What | Owner |
|---|---|---|
| `INC9C-F1` | The repo screen advertised `↵ details` with no binding and no handler. It is removed from the bar and the body panel (an honest affordance beats a K3 translation of a dead key). If the operator wants a repo detail view it is a feature, not a label | operator |
| `INC9C-F2` | **`screens/palette.py` needs a 7th source file.** Its footer still reads `↵ ejecutar   esc cerrar` (K3 lists it) and its group column paints the raw group ID (`nav`, `tree`, `plug`, `doors`, `list`, `app`), so the palette disagrees with the key bar and legend (`move`, `connect repo`, `open`, `maps`, `global`). Two lines. Not done: the operator's approval covers six files | coordinator / operator |
| `INC9C-F3` | Declared leak carries in the notify census (`LEAK_EXCEPTIONS`): `str(exc)` of `GitHubError` (git stderr can name a local path) and of `store.load`'s path-free `MapStoreError`. The first is a real residual | security / next owner |
| `INC9C-F4` | `factory.py` `archivo no encontrado: {source}` echoes the path the operator typed (a `~` expands to the profile). Fixing it is a third toast edit in `factory.py`, outside the two sanctioned sites | coordinator |
| `INC9C-F5` | Key hints not moved, by scope: the contextual search hint (`n siguiente · N anterior · esc limpiar`, ~25 sealed arms), the editor hints (`screens/editor.py`), the components and connect-repo hint lines | Inc-EN |
| `INC9C-F6` | Textual removes a key from the binding chain while a focused widget would consume it, priority or not (`Screen._binding_chain`). A priority binding for a printable key is inert under an `Input` unless the input gives the key up. Worth knowing for any future global chord | whoever adds one |
| `INC9C-F7` | The legend's own-scope group is 3 lines docked (`INC9B-F1` realised, see the changed-arm table) | closed here |
| `INC9C-F8` | `RepoScreen.on_mount`'s `except GitHubError` / `except Exception` around `worker.wait()` is effectively unreachable for a failing fetch: `@work(thread=True)` defaults to `exit_on_error`, so a raising fetch exits the app (seen in the committed RED run). Pre-existing | next owner of `RepoScreen` |
| `INC9C-F9` | The committed `repo-unexpected` driver reached the wrong defect and was corrected in `90c8ce8` | closed here |
| `INC9C-F10` | `G6-SEC-F9` not covered: a string-built `getattr(store, "sa" + "ve")` | accepted |
| — | `BACKLOG.md` and `state.json` not edited (outside this brief) | coordinator |

## 7 · Suggested next task

Rule on `INC9C-F2` (a seventh source file for `palette.py`: footer and group column) and `INC9C-F4`, then start
Inc-EN (B-71) with the carries above.

---

## Evidence checklist

- [x] Tests / lint — lane and ruff above.
- [x] No secrets — every staged diff and message byte-scanned (Cc/Cf/Zl/Zp/Cs and the account name): CLEAN, 8 of 8 (the seven code commits and this one).
- [x] No destructive commands; no push, merge, amend, rebase or force; `backup/pre-q9-reword-2026-09-28` untouched.
- [x] File count — 6 source files, operator approval 2026-09-30 (*"Déjalo terminar con los 6"*); tests and docs uncapped.
- [x] Review packet — this record and the final message.
