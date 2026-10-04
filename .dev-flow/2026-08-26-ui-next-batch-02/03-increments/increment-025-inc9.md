# Increment 025 — Inc-9 · help scope routing, the seat migration, English chrome, `LLR-N06.2.5`

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `025` — **Inc-9**, the last planned feature increment of the ratified cut (§5.4) |
| Agent | `software-dev` |
| Date | 2026-09-29 |
| Authority | §5.4 (`Inc-9` row: help scope routing, `KEY_SCOPE` declarations, seat migration, `LLR-N06.2.5` by `#D21`); `PDR#D9` (migrate both), `#D10` (`.factory-tag`), `#D6`/`C-D6b`; `VERDICT-inc8-legend-2026-09-28.md` LANGUAGE RULING and `D5` (names ratified 2026-09-29: `atlas` / `outline` / `mind map` / `home`) |
| Requirement added | `A-112` (`01-requirements.md`, appended) |
| Starting state | main tree, `feat/ui-next-batch-02` @ `6fe35f5`, clean |
| Commits | `7e64508` → `b998085` → `bd1d99c` → `6b39b78` → `66fae00` → `82a231c` → `68e3675` → (this record) |
| Source files | **5 of a cap of 5**: `mapper/keymap.py`, `mapper/app.py`, `mapper/darkside.py`, `mapper/screens/factory.py`, `mapper/screens/settings.py`. `mapper/screens/help.py` untouched. No renderer file touched — see `INC9-F2` (split) |

---

## 1 · What changed

1. **`LLR-N16.1.1` / `LLR-N16.1.2` / `HLR-N16.1` / B-18.** `SCOPE_FACTORY` and `SCOPE_SETTINGS` are
   declared; `FactoryScreen` (10 bindings) and `SettingsScreen` (2) are generated from the seat
   (`BINDINGS` and key bar), `priority=True` carried over. The five un-scoped `HelpScreen()` routes
   (three in `app.py`, one each in `factory.py`, `settings.py`) are deleted, so every help chord
   reaches `MapperApp.action_help`, which opens the legend on the source screen's `KEY_SCOPE`,
   `legend_view` and host. The factory's un-scoped `CommandPalette()` route is deleted too (same
   defect, palette reader). The derived help-screen set is **7**; each is driven with the real chord
   and its painted key rows are set-equal to `bindings_for(source.KEY_SCOPE)`.
2. **`C-D9b`.** `UNMIGRATED_SCREENS` = `("EditorScreen", "CoverageScreen")`. **`C-D9c`**: the
   `from mapper.app import _PromptScreen` line in `factory.py` is byte-identical (not in any diff).
3. **`C-D9a` — measured, and the measurement reversed the PDR's assumption.** The positive control
   could not be built on the shipped sheet: `_StateRow` assigned a widget to Textual's own
   `Widget.disabled`, which disabled every component (`focus_chain` length **0**; the PDR probe's
   `None` x 9). Renamed to `self.inert` (`INC9-F1`). On the repaired sheet, 9 real `tab` presses make
   **8 transitions** (positive control); the pre-drop `tab`/`shift+tab` bindings re-declared verbatim
   on a subclass hold focus on **1** target for all 9 presses — `LLR-N06.5`'s own measurement,
   reproduced. The drop is a repair, it ships, and `SettingsScreen` leaves `TAB_BINDING_EXCEPTIONS`.
   `A-112` st. 8 records this.
4. **`#D10`.** `.factory-tag` retoned `#1783ff` → `#737373` (MUT). Register row closed (6 → 5), blue
   literal census 8 → 7.
5. **`LLR-N06.2.5`.** AST census over every product module: 33 `notify` sites, 21 dynamic, 0 with
   markup on (already), **16 → 0** not routed through `plain()`. Each fixed site routes the whole
   message through `darkside.plain()` (`A-112` st. 7: equivalent for an index-preserving replacer).
6. **English chrome (`A-112` st. 1–5).** All 72 seat labels, the two Spanish group headers
   (`lista` → `list`, `salir` → `leave`), the Home and Repo hand-written key bars, the keybar
   truncation word (`KEYBAR_MORE = "all"`), the tab strip, the crumbs and titles, and the home header
   (reads `darkside.VIEW_NAMES["home"]`). `toggle_radial` reads `toggle mind map`.
7. **`INC8-P2-CR-F9` (`A-112` st. 6).** `_painted_help_keys` matches an own-scope item whole, in the
   exact painted form; a padded key-section row (`esc` + `close`) no longer counts.
8. **`C-D6b` / `LLR-N14.3.2` re-run** (new arm): 9 `tab` presses from the map walk the derived ring,
   8 transitions, each to the next member. **`C-D25a/b`** (new arms): the seat diff against
   `6fe35f5` (read with `git show`) is exactly the 12 declared rows plus the two declared regroups;
   no row lost or rebound; `duplicate_chords()` empty on entry and exit.
9. **Found in the renders, fixed: `INC9-F6`.** The new groups were declared after `app`, so both
   migrated key bars led with `app`. Reordered; arm added.

## 2 · Files modified

| File | Kind | Why |
|---|---|---|
| `mapper/keymap.py` | source | scopes, 12 seat rows, groups, English labels, fences |
| `mapper/app.py` | source | 3 un-scoped help routes removed; 12 notify sites coerced; Home/Repo key bars, titles, crumb, home header |
| `mapper/darkside.py` | source | tab strip labels; `KEYBAR_MORE` |
| `mapper/screens/factory.py` | source | seat migration, `KEY_SCOPE`, routes removed, `.factory-tag`, 4 notify sites |
| `mapper/screens/settings.py` | source | seat migration, `KEY_SCOPE`, tab drop, `_StateRow` fix, crumb/header |
| `tests/test_inc9.py` | test, new | every Inc-9 arm (§ Traceability) |
| `tests/test_help_scope.py`, `test_key_dispatch.py`, `test_keymap.py`, `test_palette.py`, `test_rail.py`, `test_darkside.py`, `test_darkside_census.py` | test | sealed arms re-derived — § Changed sealed arms |
| `01-requirements.md` | doc | `A-112` |
| this file | doc | record |

`01b-ux-decisions.md` **not** edited: §3.6 names no key group; the group names at `01b:54-73` are a
historical listing.

## 3 · How to test

```
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest tests/test_inc9.py tests/test_help_scope.py tests/test_keymap.py tests/test_key_dispatch.py -q
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest -q          # full default lane
ruff check .                                                      # 27, the baseline set
```

Manual: open the factory (`f` from home) and settings (`s`); press `?` — the legend title names
`factory` / `settings` and lists that screen's keys; `ctrl+p` lists them too; on settings, `tab`
now walks the components.

## 4 · Test results

### RED before (commit `7e64508`, `--runxfail`)

19 failed, 10 passed. Each RED arm failed on its named defect, e.g.
`help screens with no declared seat scope: ['FactoryScreen', 'SettingsScreen']`;
`FactoryScreen opened the legend on 'app'` (and `PlugRepoScreen`, `RepoScreen`, `SettingsScreen`,
`_ImportPreviewScreen`); five un-scoped `HelpScreen()` sites; C-D9a walk
`[-1, -1, -1, -1, -1, -1, -1, -1, -1]`; `'#1783ff' == '#737373'`; 16 uncoerced notify sites;
`[('r', 'alternar radial')]`; home row `◕ mapper   mapas vivos`; CR-F9 `esc       close` counted.

### Full default lane, once, on the final source tree (`68e3675`)

**Run as six sequential chunks by test file** (alphabetical, 61 files): a single run takes about
16 minutes here and was stopped twice by the 10-minute background limit (once by a session restart).
Same tree, same interpreter, same default markers; chunks 4 and 5 ran concurrently.

| chunk | files | result |
|---|---|---|
| 0 | `test_a3_census` .. `test_darkside` | 188 passed |
| 1 | `test_darkside_budget` .. `test_help_scope` | 164 passed, 3 xfailed |
| 2 | `test_hermetic` .. `test_legacy_fixture` | 242 passed, 1 deselected, 1 xfailed |
| 3 | `test_legend_design` .. `test_radial` | 216 passed |
| 4 | `test_rail` .. `test_repair_perf_shape` | 304 passed, 17 deselected |
| 5 | `test_repair_sidecar` .. `test_worklist_safety` | 255 passed, 2 deselected |
| **sum** | | **1369 passed, 4 xfailed, 20 deselected, 0 failed** |

**Reconciled against 1320.** `--collect-only` on the final tree: 1373 selected (1393 collected,
20 deselected). At the base, 1320 passed + 3 xfailed = 1323 selected. The +50 is exactly: 35 nodes in
`tests/test_inc9.py`, 1 CR-F9 arm in `test_help_scope.py`, +12 `AT-N03a` parametrizations (the 12 new
seat rows), +2 `AT-N03f` parametrizations (the 2 new scopes). Expected 1373 - 4 xfail = **1369
passed**, measured 1369. The 4 xfailed: the 3 pre-existing `test_fold.py::test_f_a_*` and the
deliberate `test_inc9.py::test_inc9b_each_map_view_header_names_its_view` (strict, `Inc-9b`).

**0 failed.** FLAKE-1 and the FLAKE-2 candidate were not observed. Chunk 0 printed a Textual
`Task cancelling ... _win_sleep` line after its summary (teardown noise, exit 0).

**The reviewer's partial run on `6fe35f5` (about 15–20 `F` at about 30%), NOT settled by this lane.**
This lane ran on `68e3675`, not `6fe35f5`, and saw no failure. Two observations, labelled as such:
my own full lane at an intermediate state (after the relabel, before re-deriving the label pins)
showed exactly 4 `F` near 42%, all label pins, all fixed in `6b39b78`; and at `6fe35f5` none of
Inc-9's changes exist. I did not re-run `6fe35f5` (no second tree was in my brief), so the
reviewer's failures are **unmeasured** here.

### ruff

`ruff check .` → **27 errors**, and the error SET (file + code + message, positions stripped) is
**identical** to the baseline set taken at `6fe35f5`. No new finding.

### Guards before the docs commit

`tests/test_fold.py` + `tests/test_no_operator_paths.py`, run with this record staged: **21 passed, 3 xfailed** (the 3 pre-existing `test_f_a_*`), 0 failed.

## 5 · Risks

- **Wording is a proposal.** Every string is in the copy table below; the operator corrects it there.
- **`?` inside a text field types `?`.** The plug screen's only widget is a text input, so `?` never
  opens its legend by keyboard (`INC9-F3`, pre-existing, `B-72` family). The route arm moves focus off
  the field before pressing, as the `H1` footer ("outside text fields") allows.
- **Settings sheet now has focus.** The components react to `space`/`enter`/arrows when focused; the
  sheet is a canary, and this is what its hint line always claimed.
- **`CHROME_LEXICON` is a declaration.** A new English word in the chrome must be added to it
  deliberately; that is the intended friction, and `Inc-EN` will meet it.
- **Mixed language remains** until `Inc-EN`: hint lines (`siguiente ▸ …`), toasts, prompts and modal
  hints are still Spanish — visible in every render.

## 6 · Pending items / carries

| id | What | Owner |
|---|---|---|
| `INC9-F2` | **Split (cap).** The map views' own headers — `views/layered.py` (`árbol legacy` / `mapa de conceptos`), `views/radial.py` (`mapa mental`), `views/outline.py` (literal `outline`, not read from `VIEW_NAMES`) — and two screen titles outside Inc-9's files (`screens/coverage.py` `cobertura incompleta`, `screens/editor.py` `editar documento`). Would take Inc-9 to 8 source files. Carried by the strict-xfail arm `test_inc9b_each_map_view_header_names_its_view` and by `LANGUAGE_EXCEPTIONS` (stale-guarded). `INC8-P2-UX-F4` stays open until then | **`Inc-9b`** (coordinator to cut) |
| `INC9-F3` | `?` is unreachable by keyboard on the plug screen (its only widget is a text field) | `B-72` / `B-36` |
| `INC9-F4` | The `#D10` register was **6** at Inc-9's entry, not 1: the Inc-3, Inc-5 and Inc-7 rows are still in the source. "After Inc-9: zero" does not hold; Inc-9 closed its own row (6 → 5) | coordinator / owners |
| `INC9-F7` | `help.py:90-91` comment still says the seat's labels "stay as they are until Inc-9"; not edited to keep the file count at 5 | whoever next owns `help.py` |
| `INC9-F8` | Legend titles for non-view screens name the SCOPE (`legend · plug`, `legend · import`, `legend · repo`) while the door/crumb say `connect repo` / `import`; one-name-per-screen for those three is not ruled | operator question |
| — | B-18 closed in code; `.dev-flow/BACKLOG.md` not edited (outside this brief's doc list) | coordinator |
| — | Every remaining Spanish string (hints, toasts, prompts, notices, sala, ficha, inspector) | `Inc-EN` (B-71) |

## 7 · Suggested next task

Operator verdict on the copy table and renders (the wording is unruled), then cut `Inc-9b`
(`INC9-F2`: three renderer headers from `VIEW_NAMES`, plus the coverage and editor titles).

---

## English copy table

All strings Inc-9 changed. "On screen" names where the string paints. Wording is the operator's to
correct.

### Seat labels (`mapper/keymap.py::KEYMAP`)

| # | scope | key | old Spanish | new English | on screen |
|---|---|---|---|---|---|
| 1 | home | `c` | consultar mapas | **browse maps** | yes — key bar, legend, palette |
| 2 | home | `p` | conectar repo | **connect repo** | yes — key bar, legend, palette |
| 3 | home | `n` | construir mapa | **build map** | yes — key bar, legend, palette |
| 4 | home | `t` | desde plantilla | **from template** | yes — key bar, legend, palette |
| 5 | home | `i` | importar csv | **import csv** | yes — key bar, legend, palette |
| 6 | home | `f` | fábrica | **factory** | yes — key bar, legend, palette |
| 7 | home | `r` | retomar último | **resume last** | yes — key bar, legend, palette |
| 8 | home | `s` | componentes | **settings** | yes — key bar, legend, palette |
| 9 | home | `j` | bajar | **down** | yes — key bar, legend, palette |
| 10 | home | `k` | subir | **up** | yes — key bar, legend, palette |
| 11 | home | `q` | salir | **quit** | yes — key bar, legend, palette |
| 12 | map | `j` | siguiente | **next sibling** | yes — key bar, legend, palette |
| 13 | map | `k` | anterior | **previous sibling** | yes — key bar, legend, palette |
| 14 | map | `h` | padre | **parent** | yes — key bar, legend, palette |
| 15 | map | `l` | hijo | **child** | yes — key bar, legend, palette |
| 16 | map | `↵` | abrir ficha | **open card** | yes — key bar, legend, palette |
| 17 | map | `/` | buscar | **search** | yes — key bar, legend, palette |
| 18 | map | `n` | siguiente coincidencia | **next match** | yes — key bar, legend, palette |
| 19 | map | `N` | coincidencia anterior | **previous match** | yes — key bar, legend, palette |
| 20 | map | `a` | agregar hijo | **add child** | yes — key bar, legend, palette |
| 21 | map | `d` | documentos | **documents** | yes — key bar, legend, palette |
| 22 | map | `x` | archivar | **archive node** | yes — key bar, legend, palette |
| 23 | map | `u` | deshacer | **undo** | yes — key bar, legend, palette |
| 24 | map | `A` | agregar adjunto | **add attachment** | yes — key bar, legend, palette |
| 25 | map | `X` | quitar adjunto | **remove attachment** | yes — key bar, legend, palette |
| 26 | map | `f` | alternar foco | **toggle focus** | yes — key bar, legend, palette |
| 27 | map | `o` | alternar outline | **toggle outline** | yes — key bar, legend, palette |
| 28 | map | `r` | alternar radial | **toggle mind map** | yes — key bar, legend, palette |
| 29 | map | `e` | exportar svg | **export svg** | yes — key bar, legend, palette |
| 30 | map | `=` | alternar diff | **toggle diff** | yes — key bar, legend, palette |
| 31 | map | `m` | cobertura | **coverage** | yes — key bar, legend, palette |
| 32 | map | `M` | siguiente faltante | **next missing** | yes — key bar, legend, palette |
| 33 | map | `R` | mostrar/ocultar rail | **show/hide rail** | yes — key bar, legend, palette |
| 34 | map | `I` | mostrar/ocultar ficha | **show/hide card** | yes — key bar, legend, palette |
| 35 | map | `g` | ir al rail | **go to rail** | yes — key bar, legend, palette |
| 36 | map | `z` | plegar rama | **fold branch** | yes — key bar, legend, palette |
| 37 | map | `H` | desplazar izquierda | **pan left** | yes — key bar, legend, palette |
| 38 | map | `J` | desplazar abajo | **pan down** | yes — key bar, legend, palette |
| 39 | map | `K` | desplazar arriba | **pan up** | yes — key bar, legend, palette |
| 40 | map | `L` | desplazar derecha | **pan right** | yes — key bar, legend, palette |
| 41 | map | `q` | inicio | **home** | yes — key bar, legend, palette |
| 42 | map | `esc` | volver | **back** | yes — key bar, legend, palette |
| 43 | repo | `j` | siguiente | **next sibling** | yes — key bar, legend, palette |
| 44 | repo | `k` | anterior | **previous sibling** | yes — key bar, legend, palette |
| 45 | repo | `q` | inicio | **home** | yes — key bar, legend, palette |
| 46 | plug | `esc` | volver | **back** | yes — key bar, legend, palette |
| 47 | import | `s` | guardar mapa | **save map** | yes — key bar, legend, palette |
| 48 | import | `esc` | volver | **back** | yes — key bar, legend, palette |
| 49 | palette | `↵` | ejecutar | **run** | yes — key bar, legend, palette |
| 50 | palette | `esc` | cerrar | **close** | yes — key bar, legend, palette |
| 51 | help | `esc` | cerrar | **close** | yes — key bar, legend, palette |
| 52 | help | `q` | cerrar | **close** | yes — key bar, legend, palette |
| 53 | help | `↑` | subir | **scroll up** | yes — key bar, legend, palette |
| 54 | help | `↓` | bajar | **scroll down** | yes — key bar, legend, palette |
| 55 | help | `pageup` | página arriba | **page up** | yes — key bar, legend, palette |
| 56 | help | `pagedown` | página abajo | **page down** | yes — key bar, legend, palette |
| 57 | help | `home` | al principio | **to top** | yes — key bar, legend, palette |
| 58 | help | `end` | al final | **to bottom** | yes — key bar, legend, palette |
| 59 | app | `ctrl+p` | paleta de acciones | **command palette** | yes — key bar, legend, palette |
| 60 | app | `?` | ayuda | **legend** | yes — key bar, legend, palette |
| 61 | factory (new) | `j` | key bar `sig/ant` (Binding text `Siguiente`, never painted) | **next sibling** | yes — key bar, legend, palette |
| 62 | factory (new) | `k` | key bar `sig/ant` (Binding text `Anterior`, never painted) | **previous sibling** | yes — key bar, legend, palette |
| 63 | factory (new) | `h` | key bar `padre/hijo` (Binding text `Padre`, never painted) | **parent** | yes — key bar, legend, palette |
| 64 | factory (new) | `l` | key bar `padre/hijo` (Binding text `Hijo`, never painted) | **child** | yes — key bar, legend, palette |
| 65 | factory (new) | `0` | key bar `inicio` (Binding text `Inicio`, never painted) | **start node** | yes — key bar, legend, palette |
| 66 | factory (new) | `d` | key bar `editar` (Binding text `Editar doc`, never painted) | **edit document** | yes — key bar, legend, palette |
| 67 | factory (new) | `i` | key bar `importar` (Binding text `Importar office`, never painted) | **import office file** | yes — key bar, legend, palette |
| 68 | factory (new) | `g` | key bar `generar` (Binding text `Generar`, never painted) | **generate office file** | yes — key bar, legend, palette |
| 69 | factory (new) | `q` | key bar `salir` (Binding text `Salir`, never painted) | **back** | yes — key bar, legend, palette |
| 70 | factory (new) | `esc` | key bar `salir` (Binding text `Salir`, never painted) | **back** | yes — key bar, legend, palette |
| 71 | settings (new) | `q` | key bar `salir` (Binding text `Salir`, never painted) | **back** | yes — key bar, legend, palette |
| 72 | settings (new) | `esc` | key bar `salir` (Binding text `Salir`, never painted) | **back** | yes — key bar, legend, palette |

Retired from the settings key bar: `tab siguiente`, `shift+tab anterior` (not seat rows; `tab` is
Textual's own traversal, `C-D9a`).

### Key-group headers (`GROUP_SCOPE`, painted verbatim in the key bar, legend and palette)

| scope | old | new | on screen |
|---|---|---|---|
| home | `lista` | **list** | yes |
| map | `salir` | **leave** | yes |
| factory | (`nav`, hand-written) | **tree** | yes |
| factory | (`doc`, hand-written) | **document** | yes |
| factory | (`app` holding `q/esc salir`) | **factory** | yes |
| settings | (`nav` holding `tab`) | **settings** | yes |
| — | `doors`, `nav`, `node`, `view`, `repo`, `plug`, `import`, `palette`, `help`, `app` | unchanged (already English) | yes |

### Hand-written key bars and the key bar's own word

| scope | key | old Spanish | new English | on screen |
|---|---|---|---|---|
| home | `j/k` | elegir | **choose** | yes |
| home | `↵` | abrir | **open** | yes |
| home | `r` | retomar | **resume** | yes |
| home | `c` | consultar | **browse** | yes |
| home | `n` | construir | **build** | yes |
| home | `t` | plantilla | **template** | yes |
| home | `i` | importar csv | **import csv** | yes |
| home | `f` | fábrica | **factory** | yes |
| home | `s` | componentes | **settings** | yes |
| home | `ctrl+p` | paleta | **palette** | yes |
| home | `?` | ayuda | **legend** | yes |
| home | `q` | salir | **quit** | yes |
| repo | `j/k` | sig/ant | **next/previous** | yes |
| repo | `↵` | detalle | **details** | yes |
| repo | `ctrl+p` / `?` / `q` | paleta / ayuda / inicio | **palette / legend / home** | yes |
| all | truncation marker | `… +N  ? todas` | **`… +N  ? all`** | yes |

### Screen headers (`A-112` st. 4)

| screen | where | old Spanish | new English | on screen |
|---|---|---|---|---|
| every screen | tab strip `c` | consultar | **browse** | yes |
| every screen | tab strip `n` | construir | **build** | yes |
| every screen | tab strip `f` | fábrica | **factory** | yes |
| home | identity row | mapas vivos | **home** (`VIEW_NAMES["home"]`) | yes |
| plug | crumb | conectar repo | **connect repo** | yes |
| plug | title | conectar repositorio | **connect repository** | yes |
| settings | crumb | preferencias | **settings** | yes |
| settings | column header | componente | **component** | yes |
| template picker | title | elegir plantilla | **choose template** | yes |
| new map | title | nuevo mapa | **new map** | yes |
| atlas / mind map / outline, coverage, editor | view header / title | árbol legacy, mapa de conceptos, mapa mental, cobertura incompleta, editar documento | **not changed — `Inc-9b`** | yes |

## Changed sealed arms

Arms that pin a LABEL value were re-derived; arms that pin behaviour are unchanged.

| Arm | Change | Justification |
|---|---|---|
| `test_key_dispatch.py::test_at_n03h_the_whole_seat_matches_its_specification` (`EXPECTED_SEAT`) | 60 label + 3 group fields re-derived; 12 rows added | label values (A-112) and the `#D9` migration; action/glyph/priority of every pre-existing row unchanged — `test_cd25a_*` proves it against `6fe35f5` |
| `test_keymap.py` `SCOPE_OWNER` / `EXPECTED_PER_SCOPE` | +`factory: FactoryScreen, 10`, +`settings: SettingsScreen, 2` | the seat-size fence is a deliberate edit by design; `AT-N03a`/`AT-N03f` then quantify over the new rows |
| `test_keymap.py::test_groups_for_keybar_order_and_glyphs` | `("j","siguiente")` → `("j","next sibling")`, `("↵","abrir ficha")` → `("↵","open card")` | label values |
| `test_keymap.py::test_palette_items_filters_by_scope_and_query` | query `cobertura` → `coverage` | label value; still narrows to exactly `coverage` |
| `test_palette.py::test_at_n03b_*` | query `cobertura` → `coverage` | label value; the dispatch oracle is unchanged |
| `test_palette.py::test_at_n03d_*` | absence literal `consultar mapas` → the home door's label **read from the seat** | the typed literal had gone vacuous with the relabel; reading it restores the check's bite |
| `test_rail.py::test_at_n03e_*` | `"todas"` → `darkside.KEYBAR_MORE` | label value, read from its one spelling |
| `test_darkside.py::test_tab_strip_has_tabs` | consultar/construir/fábrica → browse/build/factory | label values |
| `test_darkside_census.py` `OPEN_EXCEPTIONS`, blue-literal count, register size | factory row removed; 8 → 7; 6 → 5; owners drop `Inc-9` | the handoff `#D10` designed: the stale guard would redden otherwise |
| `test_help_scope.py::_painted_help_keys` | item matched whole (stricter) | `INC8-P2-CR-F9`; a narrower match can only turn more cases red |
| `test_help_scope.py` two synthetic `KeyBinding(..., "salir")` vehicles | group `salir` → `leave` | the group name no longer exists; the hostile-label check itself is unchanged |

Unchanged and green: `AT-N03a`, `AT-N03f`, the three `tab` guards, `duplicate_chords`, `AT-R12`,
`AT-R13`, `AT-R14`, every `HLR-N16.x` legend arm.

## Mutant table

Harness outside the repo (`%TEMP%\inc9\mutants.py`): per mutant a sha256 pin, a byte-level edit in
the file's own line endings, the killing tests run, the verdict **printed before** the restore, the
pin re-checked. Every pin matched after restore.

| # | Mutant | File | Killing arm(s) | Verdict | Pin before = after |
|---|---|---|---|---|---|
| M1 | re-add `action_help` → `HelpScreen()` on `_ImportPreviewScreen` | `app.py` | route arm `[_ImportPreviewScreen]`, B-18 AST arm | **KILLED** 2/2 | `3246ffb8c291` |
| M2 | drop `KEY_SCOPE = SCOPE_FACTORY` | `factory.py` | `LLR-N16.1.2`, route arm `[FactoryScreen]` | **KILLED** 2/2 | `7be6c60f6a91` |
| M3 | `_StateRow` also assigns `self.disabled` | `settings.py` | C-D9a arm | **KILLED** | `38fe364a9eed` |
| M4 | `.factory-tag` back to `#1783ff` | `factory.py` | `#D10` arm, blue-literal census | **KILLED** 2/2 | `7be6c60f6a91` |
| M5 | drop `plain()` on the `generado` toast | `factory.py` | `LLR-N06.2.5` census | **KILLED** | `7be6c60f6a91` |
| M6 | `next missing` → `siguiente faltante` | `keymap.py` | language census `[seat]` | **KILLED** | `86482e78da18` |
| M7 | add group `salir` | `keymap.py` | language census `[seat]` | **KILLED** | `86482e78da18` |
| M8 | `toggle mind map` → `toggle map` | `keymap.py` | view-name arm | **KILLED** | `86482e78da18` |
| M9 | home header back to literal `mapas vivos` | `app.py` | home-header arm | **KILLED** | `3246ffb8c291` |
| M10 | CR-F9 parser reverted to glyph/last-token pairing | `test_help_scope.py` | CR-F9 arm | **KILLED** | `dcb926303a40` |
| M11 | home key bar `legend` → `ayuda` | `app.py` | language census `[keybar]` | **KILLED** | `3246ffb8c291` |
| M12 | drop factory row `0` | `keymap.py` | `C-D25a` (the route arm stayed green: `0` also leaves the expected set) | **KILLED** 1/2 | `86482e78da18` |
| M13 | settings crumb → `preferencias` | `settings.py` | language census `[headers]` | **KILLED** | `38fe364a9eed` |
| M14 | tab strip `browse` → `consultar` | `darkside.py` | language census `[headers]` | **SURVIVED** first run → `INC9-F5` (the walk missed an annotated assignment and derived no tab label) → fixed in `82a231c` → **KILLED** | `6aa263d885cc` |
| M15 | `KEYBAR_MORE = "todas"` | `darkside.py` | language census `[keybar]` | **KILLED** | `6aa263d885cc` |
| M16 | re-add a screen `tab` binding on settings | `settings.py` | C-D9a arm, `LLR-N06.5` tree guard | **KILLED** 2/2 | `38fe364a9eed` |
| M17 | group `tree` declared after `app` | `keymap.py` | `INC9-F6` arm | **KILLED** | `99e6b4d67d21` |

Also in-suite: `LLR-N16.1.1`'s emptied-set mutation arm (`_help_screens([])` must raise), and
predicate controls for the notify census and the language judge.

## Renders

Real Textual renders of the final tree (`68e3675`), each as SVG (Textual's own screenshot) plus a
text dump of the composited frame, at **118×34** (reference), **87×34** and **140×45**. For each of
`home`, `atlas`, `outline`, `mind_map`, `import`, `plug`, `repo`, `factory`, `settings`:
`<name>_screen_<size>` (header row + key bar) and `<name>_legend_<size>` (the legend opened with
`?`). 54 renders, 108 files, in:

`C:\Users\<operator>\AppData\Local\Temp\inc9\render\`

Key bars at 118×34, read from the dumps:

```
home      nav j/k choose  ↵ open  r resume   doors c browse  p repo  n build  t template  i import csv  f factory … +4  ? all
factory   tree j next sibling  k previous sibling  h parent  l child  0 start node   document d edit document … +6  ? all
settings  settings q back  esc back   app ctrl+p command palette  ? legend
repo      nav j/k next/previous  ↵ details   app ctrl+p palette  ? legend  q home
plug      plug esc back   app ctrl+p command palette  ? legend
atlas     nav j next sibling  k previous sibling  h parent  l child  ↵ open card  / search  n next match … +26  ? all
```

Legend titles: `legend · atlas`, `legend · outline`, `legend · mind map`, `legend · home`,
`legend · factory`, `legend · settings`, `legend · import`, `legend · plug`, `legend · repo`.

## Traceability

| Arm (`tests/test_inc9.py` unless noted) | Requirement |
|---|---|
| `test_llr_n16_1_1_*` (2) | `LLR-N16.1.1` |
| `test_llr_n16_1_2_every_help_screen_declares_a_scope`, `test_cd9b_*` | `LLR-N16.1.2`, `C-D9b` |
| `test_hlr_n16_1_every_help_route_carries_its_scope[x7]`, `test_every_derived_help_screen_has_an_opener` | `HLR-N16.1`, `HLR-N16.2` (title), B-18 |
| `test_b18_no_product_site_constructs_an_unscoped_legend` | `HLR-N16.1`, B-18 |
| `test_cd9a_*` | `C-D9a`, `LLR-N06.5`, `A-112` st. 8 |
| `test_llr_n14_3_2_*` | `LLR-N14.3.2` / `C-D6b` |
| `test_d10_*` | `#D10`, `LLR-S06.3.2/3` |
| `test_llr_n06_2_5_*` (2) | `LLR-N06.2.5` (`HLR-COERCE`), `A-112` st. 7 |
| `test_a112_*` (7) | `A-112` st. 1–5 |
| `test_inc9b_*` (strict xfail) | `A-112` split, `INC8-P2-UX-F4`, `INC9-F2` |
| `test_cd25a_*`, `test_cd25b_*` | `C-D25a`, `C-D25b` |
| `test_inc9_f6_*[x7]` | `INC9-F6` (key-bar reader of the seat, US-N03) |
| `test_help_scope.py::test_inc8_p2_cr_f9_*` | `HLR-N16.4`, `A-112` st. 6 |

Changed seams: `keymap.KEYMAP`/`GROUP_SCOPE` (`LLR-N16.1.2`, `A-112`); `FactoryScreen`/
`SettingsScreen` `BINDINGS`/`KEY_SCOPE`/key bar (`LLR-N16.1.2`); removed `action_help` routes
(`HLR-N16.1`); `_StateRow` (`A-112` st. 8); notify sites (`LLR-N06.2.5`); `.factory-tag` (`#D10`);
`darkside.tab_strip`/`KEYBAR_MORE` (`A-112` st. 3–4).

## Evidence checklist

- [x] Tests / lint — lane and ruff above.
- [x] No secrets — every staged diff and message byte-scanned (Cc/Cf/Zl/Zp/Cs and the account name): CLEAN, 8 of 8.
- [x] No destructive commands; no push, merge, amend, rebase or force.
- [x] File count — 5 source of a cap of 5; tests and docs uncapped.
- [x] Review packet — this record.
