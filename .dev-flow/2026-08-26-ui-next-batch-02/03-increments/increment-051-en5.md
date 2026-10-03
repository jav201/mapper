# Increment 051 -- Inc-EN-5: English strings in `app.py`

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `6fc218c`. Authority: `A-133` (appended to `01-requirements.md`, dated 2026-10-02), `VERDICT-inc-en-2026-10-02.md` (EN-Q1, EN-Q2) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING. 3 source files (cap 4, no overage): `mapper/app.py`, `mapper/screens/editor.py` (binding labels lowercased, `EN1-REV-F4`), `mapper/widgets/inspector.py` (one comment, `EN2-REV-F1`; see the uncertainty in section 7). The 4th slot was not used. `keymap.py`, `screens/palette.py` and the `?` rule were not touched.

## 1. What changed

Every user-facing Spanish string in `app.py` is plain operator English, found by a FULL non-docstring literal dump (an AST walk; 448 literals read, not grepped). The old to new table is `A-133` (appended to `01-requirements.md`); it is grouped there as toasts and notices, search, home / ficha modal / minimap, repo screen, and prompts / confirmations. The terms follow `A-130`..`A-132`: `record` for `acta` (`no record`, `with record`, `A-131`), `↩ resume` (the `EN-4` legend sample), `blocked` / `risk` (the inspector's), `reading branches` / `computing metrics` / `ready` (`EN-1`'s, plus `starting`).

Key points, declared:
- **Search** goes through ONE constants block at the top of `app.py` (`SEARCH_COUNT_SUBJECT` `matches in the map`, `SEARCH_ACTIVE_LABEL` `search`, `SEARCH_SUSPENDED_NOTICE` `highlighting and walk suspended`); the `test_search.py` arms that derive from the constants moved with them; the ones that pin a literal were relabelled (section 3).
- **Binding labels**: `Sí` / `No` / `Cancelar` became `yes` / `no` / `cancel`, lowercase as the keymap's. `Cancel` and `Close` (already English, capitalised, on three other modal screens) were NOT changed: they were not Spanish and the task named only the Spanish ones.
- **Closes two carries**: the `A-129` CSV carve-out (`file not found: {name}`, the CSV prompt) and the `Inc-X3` `abierto` toast (`opened`); the three `test_inc9x3` pins and the `test_inc9m` / `test_inc9n` CSV pins were relabelled.
- **Not found by the census list, found by the dump**: `completa «campo»` (the gap hint, `fill in «campo»`), `celdas` / `tardar` words in the export arms of `test_export_state` (found by a failing run, not by my first grep), the metrics dict keys `con_acta` / `sin_acta` / `vencen` (renamed `with_record` / `no_record` / `due` so that no literal is Spanish), `exportado`, `deshacer`, `archivado`, `ayer`, `hace N sem`.
- **Security**: untouched sentences `U1` / `V1` / `V2` / `W1` / `W2` / `X1` / `Y1` and `refusal_sentence`; every `darkside.plain` site is still there (the diff only changes the words inside them); no message echoes anything it did not echo. A new arm (`test_the_csv_missing_file_toast_names_the_file_coerced_and_not_the_path`) types a name with U+202E into the CSV prompt and asserts the toast is exactly `file not found: miss<U+FFFD>ing.csv` with neither the override nor the typed directory in it. It exists because mutant Q2 (drop that `darkside.plain`) SURVIVED every existing test; it is killed now.
- **Kept**: the guillemets `«»` around a quoted name; the pluralisation `1 descendants` (the Spanish `1 descendientes` had the same shape); local variable names `sin_acta` / `vencen` (identifiers; the hue census pins source lines that name them); test function names that contain `limpiar` / `abrio`.

## 2. Files modified

Source (3): `mapper/app.py`, `mapper/screens/editor.py`, `mapper/widgets/inspector.py` (comment only). Tests: `tests/test_en5.py` (new, 9 items); relabelled `test_app`, `test_confirm_markup`, `test_darkside_census`, `test_export_state`, `test_fold`, `test_g6_store_surrogates`, `test_inc9d`, `test_inc9f`, `test_inc9h`, `test_inc9i`, `test_inc9m`, `test_inc9n`, `test_inc9o`, `test_inc9x3`, `test_pan`, `test_repair_cycles`, `test_search`, `test_sparkline_floor`, `test_strips`, `test_worklist_safety`; widened `test_overflow` (section 3). Docs: `01-requirements.md` (append `A-133`), this file. `keymap.py`, `screens/palette.py`, `state.json`, `BACKLOG.md`, `prototypes/`, `mapper.db` not touched. Commits: `cb53c57` (code, tests, A-133), then this record.

## 3. Sealed-arm changes (labels only; none weakened)

Each is a literal substitution of the pinned text; the comparison (`==`, `in`, `not in`, `startswith`, a regex) and the structure are unchanged. Counts are changed lines.

| Test file | Pin | Old -> new |
|---|---|---|
| `test_search.py` (23 lines; 29 pins) | hint line, E1b / E1c toasts, the walk toast, the gap toast, the `limpiar` promises (5), negative pins that must not go vacuous (`0 matches`, `is not in this map`, `no active search`) | `n siguiente · N anterior · esc limpiar` -> `n next · N previous · esc clear`; `sin coincidencias` -> `no matches`; `sin búsqueda activa` / `no hay coincidencias que recorrer` -> `no active search` / `no matches to step through`; `0 coincidencias` -> `0 matches`; `» no aparece en este mapa` -> `» is not in this map`; `recorrido suspendido` -> `walk suspended`; `cobertura completa` -> `coverage complete` |
| `test_pan.py` (7) | the edge hint (6 sites), the unreadable-layout canvas | `borde del territorio` -> `edge of the territory`; `no se pudo dibujar el mapa` -> `could not draw the map` |
| `test_fold.py` (5) | the leaf-fold toast, the walk-opened-branch hint (3) | `nada que plegar` / `este nodo no tiene descendientes` -> `nothing to fold` / `this node has no descendants`; `abrió` -> `opened`; `limpiar` -> `clear` |
| `test_repair_cycles.py` (5) | home / map / preview notices | `no se pudo cargar X` -> `could not load X` (2); `no se pudo dibujar ...` (2) -> English; `error cargando mapa` -> `error loading map` (the store half was `EN-4`'s) |
| `test_export_state.py` (4) | the refusal, the stale-file sentence (2), the wait declaration | `no corresponde a esta exportación` -> `does not match this export` (2); `celdas` -> `cells`; `celdas` + `tardar` -> `cells` + `take a moment` |
| `test_darkside_census.py` (5) | source lines of `app.py` | `vencen hoy` -> `due today`; `("sin acta ", ...)` -> `("no record ", ...)`; `bloqueado` / `riesgo` / ` baja ` -> `blocked` / `risk` / ` low `. The `sin_acta` variable line and the `if doc else ALERT` key are unchanged (identifiers / code) |
| `test_strips.py` (4) | minimap | `ramas sin mostrar` (3, one a regex) -> `branches not shown`; `sin datos` -> `no data` |
| `test_inc9x3.py` (3) | the attachment-open toast | `abierto` -> `opened` (ends the `X3` carry) |
| `test_inc9n.py` (4), `test_inc9m.py` (4), `test_inc9o.py` (1) | the CSV prompt and the add-attachment toast | `archivo no encontrado` -> `file not found` (incl. 3 `not in` pins in `test_inc9m`); `adjunto agregado` -> `attachment added` (3); the `word = ... if surface == "csv" else ...` in `test_inc9n` is now the one word `file not found` (ends the `A-129` carve-out) |
| `test_inc9h.py` (2), `test_inc9i.py` (2), `test_inc9f.py` (1) | connect stage and toast | `listo` -> `ready` (incl. the `not in` pin in `test_inc9f`); `conectado: N nodos` -> `connected: N nodes` |
| `test_g6_store_surrogates.py` (2) | save-failure toast | `no se pudo guardar` -> `could not save` |
| `test_worklist_safety.py` (2) | undo on empty stack; archive confirmation | `nada que deshacer` -> `nothing to undo`; `descendiente` -> `descendant` |
| `test_confirm_markup.py` (2) | the arm builds the archive sentence it quotes | `¿archivar «x»?` -> `archive «x»?` |
| `test_app.py` (3) | hero; fake progress callback (2) | `nodos sin acta` -> `nodes with no record`; `listo` -> `ready` (argument never asserted) |
| `test_inc9d.py` (1), `test_sparkline_floor.py` (2) | recents header; sparkline caption | `nodos` -> `nodes`; `actividad 14d  ` -> `activity 14d  ` |

Total: 20 sealed test files relabelled (82 changed lines, `test_search` alone 23), 1 widened (`test_overflow`).

**Geometry, re-derived by sweep (not edited until green).** `test_overflow::test_a_region_too_short_for_a_body_row_declares_nothing_painted` failed its non-vacuity assert (`no size in the sweep reaches the short-region branch`). Cause, measured with a probe run on `6fc218c` and on this tree (outside the repo): the English minimap strip is one row shorter at 100 columns (`#map-minimap` 2 rows became 1), so at terminal 100x10 the canvas is 3 rows and no longer the short region; on the base that one size (100, 10) was the ONLY size of the sweep in the short branch (`region_h <= charged`). The probe over heights gave the sizes that are short now: `(100, 9)`, `(80, 10)`, `(60, 11)`, `(50, 12)` (region 2, charged 2). These four were ADDED; the 15 old sizes stay, so the identity `declared == traced` is still asserted at every old size. Result: the arm passes with `short` non-empty.

**Digests.** None re-derived (no sha256 fingerprint depends on a string that `app.py` paints).

Not relabelled, and why:
- `test_darkside.py` `time_row(..., "hoy")` / `"hace 15 d"`: arguments to the renderer under test, not text `app.py` paints.
- `test_inc9x3` `acta` URL and node caption, `test_inc9n` `https://example.com/acta`, `test_g6` `docs/acta.pdf`: test data typed into the prompts or stored in a fixture.
- `test_legacy_fixture` `selecciona un nodo` / `cobertura` negative pins: `EN-3`'s, still about the views' English counterparts.
- `test_inc9e` (`"siguiente" not in` hint lines): a census over `darkside.hint_line`, still true.
- `test_rail`, `test_palette`, `test_repair_layout` `cobertura`: grep hits on fixture labels and docstrings; they pass unchanged.
- Fixture schemas with Spanish labels (`dueño`, `documento`): test data.

## 4. Width checks

Measured in `Python len`, one cell per glyph here: minimap caption `  coverage   ` 13 against `  cobertura   ` 14 (budget `_MINIMAP_CAPTION_CELLS = 14` stands), legend `█ complete ▒ medium ░ low ╱ no data` 35 against 37 (budget 37 stands), declaration `+N branches not shown   ` 24 / 25 / 26 cells for 1 / 2 / 3 digits against the budget 26 (the Spanish was 23 / 24 / 25, so the three-digit case now equals the budget exactly and no more); hero caption `nodes with no record` 20 against 14; `▲ N due today` 13 against 14; the home microbar (60 / 40, two digits) 71 against 68, so it wraps at 68..70 columns where it did not before (it already wrapped below 68; `tests` pass at the sizes the suite uses). `test_strips` (the budget arms) and `test_search` (the count region sweep at 60..160 columns) pass. NOT measured: the home screen, the repo sidebar and the ficha modal rendered as images; widths other than the suite's; the long export sentence at each width.

## 5. RED / GREEN and mutants

**Census arm, RED on the base.** A scratch `git worktree` of `6fc218c` under `%TEMP%` (removed), temp HOME, `tests/test_en5.py` copied in with `@pytest.mark.xfail(strict=True)` on the 8 items that must fail there (the census and seven behaviour arms). Without `--runxfail`: `1 passed, 8 xfailed`. With `--runxfail`: `8 failed, 1 passed` (the pass is the oracle control, by design); the census reported 143 Spanish literals on the base. `mapper` was imported from the worktree (its `__file__` checked). GREEN here: `9 passed`. An earlier GREEN check of the CSV arm that ran from the base directory against the repo's path imported the repo's `mapper`; it was discarded and redone by copying the file into the worktree (the numbers above).

**Mutants.** Harness `%TEMP%\...\scratchpad\en5\mut.py` (outside the repo): byte-level read and write of `app.py`, sha256 pin checked after every restore (all `restored True`), verdict printed before the restore, `-B`, `-W error::SyntaxWarning`, `-x`, temp HOME and USERPROFILE. 17 run: 16 killed, 1 survived (equivalent, below). Pin `app.py` (working-copy bytes, first 8 hex): `1d558c1c` before and after every mutant.

| # | Group | Mutant | Killed by |
|---|---|---|---|
| C1 | census | `no templates available` -> `no hay plantillas disponibles` | `test_en5` census |
| T1 | toast | `could not save` -> `no se pudo guardar` | `test_g6_store_surrogates::test_g6c_...[add_child]` |
| S1 | search | `no matches · {clear}` -> `sin coincidencias · ...` | `test_search::test_p052_2_the_hint_line_reads_its_glyphs_from_the_seat` |
| H1 | home | hero `nodes with no record` -> `nodos sin acta` | `test_app::test_home_screen_renders_hero_when_maps_exist` |
| R1 | repo | `connected: N nodes` -> `conectado: N nodos` | `test_inc9h::test_inc9h_p2_...[size0]` |
| K1 | confirm | `archive «x» and its N descendants?` -> Spanish | `test_worklist_safety::test_at_n05a_...` |
| P1 | prompt | `file not found: {name}` -> `archivo no encontrado: ...` | `test_inc9n::test_inc9n_f2_the_csv_prompt_requires_a_file_not_a_directory` |
| E1 | pan | `edge of the territory` (both sites) -> Spanish | `test_pan::test_at_012_pan_is_bounded_...` |
| O1 | toast | `opened` -> `abierto` | `test_inc9x3::...click_on_a_file_chip...[size0]` |
| X1 | export | `does not match` -> `no corresponde` | `test_export_state::test_a_refusal_DECLARES_the_stale_artifact...` |
| N1 | minimap | `branches not shown` -> `ramas sin mostrar` | `test_strips::test_the_CELL_BUDGET_is_the_bound_that_binds` |
| Z1 | binding | `yes` -> `Sí` | `test_en5` binding-label arm |
| D1 | ficha | `created` -> `creado` | `test_en5` census ONLY |
| Y1 | toast | `saved` -> `guardado` | `test_en5` census ONLY |
| Q2 | security | drop `darkside.plain` from `file not found: {name}` | SURVIVED all existing tests; killed by the new `test_the_csv_missing_file_toast_...` arm |
| Q3 | security | `Static(self.message, ..., markup=False)` -> no `markup=False` | `test_confirm_markup::test_sec_h2_a_message_cannot_bind_a_clickable_action` |
| Q1 | security | drop `darkside.plain` from `connected: {count} nodes` | SURVIVED: equivalent, `count` is an `int`, so `plain` changes nothing observable |

D1 and Y1 (the ficha modal labels, the `saved` toast) have no pin except the census: no existing test reads the ficha modal or the field-commit toast. Declared, not fixed here.

## 6. Test results

- Ruff 0.8.4, `ruff check mapper tests --output-format json --no-cache`, base `6fc218c` in a scratch worktree vs this tree, a programmatic set difference on (file, code, message): **26 and 26, new: none, gone: none.**
- `-W error::SyntaxWarning`: every pytest run carried it.
- Targeted lane before the fixes (60 test files that name a changed string, plus `test_en5`): `73 failed, 1759 passed, 22 deselected, 3 xfailed` in 1380 s: `test_search` (9), `test_repair_cycles` (10), `test_inc9x3` (10), `test_g6_store_surrogates` (7), `test_inc9n` (5), `test_fold` (5), `test_pan` (4), `test_inc9h` (4), `test_export_state` (3), `test_strips` (3), `test_sparkline_floor` (3), `test_worklist_safety` (2), `test_a3_census` (1, the new test file was untracked: fixed by staging it), and one each in `test_app`, `test_darkside_census`, `test_inc9d`, `test_inc9i`, `test_inc9m`, `test_inc9o`, `test_overflow`. All relabelled or re-derived as in section 3, then those files re-run: the groups ran `211 passed`, `581 passed` and `1 failed` (`test_worklist_safety::...n05a`, the `descendiente` pin, fixed), then `9 passed` for `test_en5`.
- Account-name grep of the staged diff (name read at run time, not printed): 0 hits; no `prototypes/`, `mapper.db`, `fixtures/.mapper` or `state.json` staged; Cf characters in the staged diff: 0 after one fix (the tool expanded my `U+202E` and `U+FFFD` escapes into the raw characters in `test_en5.py`; replaced by the six-character escapes before the commit and re-checked); U+2011: 0.
- Environment: temp HOME and USERPROFILE, git identity from environment variables, default basetemp, rootdir inside the repo or the worktree, no network, UNC, device, real cache or real gh; no file launched (the attachment launcher is the recording stub); scratch worktrees removed (the EN-4 reviewer's worktrees under `%TEMP%\en4-rev` were not touched). No scratch file written inside the repo. No `git stash`.

## 7. Risks, unmeasured, next

- **Uncertain: `EN2-REV-F1`.** The text of that finding was not in the repo or the task. I read `widgets/inspector.py` for a comment that the `EN-2` relabel left stale and found one: `# The four states a ficha may carry, and the words shown for them.` (the stored value and the shown word are now the same four English words). I changed it to say so. If the finding named another comment, this is the wrong one and the real one is still open.
- Risks: (1) the census word list is explicit and finite; a Spanish word not on it passes (it was widened with the words read from the dump, and still cannot see Spanish in an identifier or a docstring). (2) `D1` / `Y1`: the ficha modal and the `saved` toast are pinned only by the census. (3) The microbar is three cells wider; it wraps at 68..70 columns (section 4). (4) `1 descendants` is ungrammatical; it was `1 descendientes`. (5) `Cancel` / `Close` stay capitalised on three modals while `cancel` / `yes` / `no` are lowercase.
- Unmeasured: widths beyond the suite's; the home, repo and ficha screens as images; POSIX; the long English sentences at every width.
- Left for later: `EN-6` (`keymap.py`, `screens/palette.py` footer `↑↓ move`; the keymap labels are already English in this tree, so `EN-6` is smaller than the verdict implied); `EN-7` (`?` in text fields, including the connect-repo field). Comments and docstrings in `app.py` still quote Spanish phrases (history, not copy). Test function names that contain Spanish words were not renamed.
- Suggested next: `EN-6`.

## Full-lane result

`2686 passed, 24 deselected, 3 xfailed` (0 failed) in 1749.9 s (29 min 9 s), `python -B -m pytest -rf -q -W error::SyntaxWarning -p no:cacheprovider`, one uninterrupted process, temp HOME and USERPROFILE, git identity from environment variables, on `cb53c57` (the last code and test change), run as the last step before this record. Baseline 2677; the delta is the 9 new `test_en5.py` items (2677 + 9 = 2686). FLAKE-1 and FLAKE-4 did not appear.

Lane history, declared: the first (targeted) lane above is not the gate. The full lane was started once and not interrupted. The `A-133` legend figure (35 cells against 37; the first draft said 32 against 33) was corrected in a docs-only commit after the lane, together with this record.
