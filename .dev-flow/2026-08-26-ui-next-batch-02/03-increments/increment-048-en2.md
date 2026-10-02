# Increment 048 -- Inc-EN-2: English strings in the coverage report, the components sheet, the inspector and the rail

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `6092d26`. Authority: `A-130` (appended to `01-requirements.md`, dated 2026-10-02), `VERDICT-inc-en-2026-10-02.md` (EN-Q1; Round 2, `Z2`) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING. 4 source files (the cap).

## 1. What changed

Every user-facing Spanish string in the four files is plain operator English; no condition, style, geometry or key moved. `Z2` is implemented inside the inspector (section 7).

| File | Old | New |
|---|---|---|
| `screens/coverage.py` | binding labels `Seleccionar` / `Cerrar` (x2) | `Select` / `Close` |
| | columns `nodo` / `faltantes` / `cobertura` | `node` / `missing` / `coverage` |
| | `todo completo.` / `no falta ningun campo requerido.` | `all complete.` / `no required field is missing.` |
| `screens/settings.py` | hint `tab recorre componentes - el foco es el bloque solido` | `tab walks the components - focus is the solid block` |
| | demo values `luna` / `marea` / `noche` | `moon` / `tide` / `night` |
| | `cargando...` / `sistema-leg` | `loading...` / `system-leg` |
| `widgets/inspector.py` | `salir del campo` (FieldInput binding label) | `leave the field` |
| | `(selecciona un nodo)` | `(select a node)` |
| | header `ficha` | `card` |
| | row labels `titulo` / `estado` / `notas` / `adjuntos` / `cobertura` | `title` / `state` / `notes` / `attachments` / `coverage` |
| | `+ agregar adjunto` / `requerido` | `+ add attachment` / `required` |
| | state segments `ok riesgo tarde bloq` | `ok risk late blocked` |
| `widgets/rail.py` | `no se puede dibujar:` + line break + `el mapa tiene un ciclo` | `cannot draw:` + line break + `the map has a cycle` |
| | `(mapa vacio)` | `(empty map)` |
| | `mapa . {n}n . {m} faltan` | `map . {n}n . {m} missing` |
| | `territorio` / `cobertura {pct}%` | `territory` / `coverage {pct}%` |

(Accents and the middle dot are written in `A-130`; this table is ASCII for the shell.)

Found by the FULL non-docstring literal dump (an AST walk, 4 files), beyond the census list in the task: `cobertura` (coverage column, inspector label, rail footer), `estado` / `notas` / `adjuntos` (inspector labels), `riesgo` / `tarde` / `bloq` (state segments), `territorio` (rail caption), `luna` / `marea` / `noche`, `cargando...`, `sistema-leg` (settings demo values). The word `bloq` became `blocked`, the same word `STATE_VALUES` already uses; the segmented control stays 28 cells wide, as before. The comment `the Spanish words shown for them` lost its adjective.

Tests: `tests/test_en2.py` (new, 8 items: 4 file arms, 1 oracle control, 3 `Z2` items); labels relabelled in eight files (section 3). Docs: `A-130`, this file.

## 2. Files modified

Source (4, the cap): `mapper/screens/coverage.py`, `mapper/screens/settings.py`, `mapper/widgets/inspector.py`, `mapper/widgets/rail.py`. Tests: `tests/test_en2.py` (new); relabelled `test_darkside_census`, `test_inspector`, `test_repair_depth`, `test_worklist_safety`; comment or sibling-pin edits in `test_legacy_fixture`, `test_legend_design`, `test_repair_layout`. Docs: `01-requirements.md` (append `A-130`), this file. `keymap.py`, `app.py`, `state.json`, `BACKLOG.md`, `prototypes/`, `mapper.db` not touched. Commit: `48a354a`, then this record.

## 3. Sealed-arm label changes (labels only; no assertion weakened except where stated)

| Test file | Pin | Old -> new |
|---|---|---|
| `test_darkside_census.py:221` | hue-census site key (the census pins the SOURCE line) | `("  requerido", darkside.ALERT),` -> `("  required", darkside.ALERT),` |
| `test_inspector.py:155` | the flagged-row finder (`test_at_n01d_required_and_empty_is_flagged`) | `"requerido" in ...` -> `"required" in ...` |
| `test_worklist_safety.py:127` | the empty coverage report (`test_at_n04d_...`) | `"todo completo" in ...` -> `"all complete" in ...` |
| `test_repair_depth.py:190` | `CYCLE_NOTICE`, the rail's notice | `el mapa tiene un ciclo` -> `the map has a cycle` (`FACTORY_CYCLE_NOTICE` is now the same sentence; its "rail is EN-2's" comment updated) |
| `test_repair_depth.py:1240-1243` | the `test_tc_r30` header oracle | comment `mapa . Nn . M faltan` -> `map . Nn . M missing`; `startswith("mapa")` -> `startswith("map " + chr(0xB7))` |
| `test_repair_depth.py:174-179` | `MASTER_RAIL_DIGESTS` (5 sha256 of the rail render) | re-derived, see below |
| `test_legacy_fixture.py:40-41` | NEGATIVE pins: the renderer must not repaint the inspector strip | the two Spanish pins stay (the renderer is EN-3's); `"select a node" not in` and `"coverage" not in` added beside them, so the guarantee is not vacuous against the inspector's new copy |
| `test_legend_design.py:81,272,495`, `test_repair_layout.py:25,364` | comments only | `mapa . 36n`, `requerido`, `cobertura 100%` -> `map . 36n`, `required`, `coverage 100%` |

Two items in that table are not a pure substitution, declared:
- **Rail digests.** A sha256 of text cannot be relabelled by hand. Both sides were rendered by the same test helpers (`_legacy_graph`, `OutlineRail`, `_fingerprint`): `6092d26` in a scratch worktree (its five digests equal the pinned ones, so the harness reads the same thing) and this tree. Each render was cut into `(substring, style)` segments; with only `mapa . / faltan / territorio / cobertura -> map . / missing / territory / coverage` applied to the base segments, the two segment lists are identical for all five collapse sets (`True` x5), so only the four words moved. The factory-tree digest is unchanged (`True`). The five new digests are in the file under a comment saying so.
- **`chr(0xF3) not in CYCLE_NOTICE`** ("the notice needs no accent to survive") would have become trivially true on an English constant. It now reads `chr(0xF3) not in text.plain` (the painted rail), which is the claim it made.

Pins found and NOT relabelled, and why:
- `test_rail.py:175-181` (`"cobertura"` in the wide key bar) and `test_repair_layout` AT-R14: the key bar's `m cobertura` is `keymap.py`'s label (EN-6). Note for EN-6: once the key bar says `coverage`, the AT-R14 "whole rows, never substrings" rule matters even more, because the rail now paints `coverage 100%`.
- `test_components.py:55-63` (`cargando`, `sistema-leg`): they build their own widgets; `components.py`'s default `cargando...` is EN-4's.
- `test_search.py:2131`, `app.py` `cobertura completa` / `no falta ningun campo requerido` toast: `app.py` (EN-5). Same text, different surface from the coverage report's empty line.
- `inc4_support.py`, `test_model.py`, `test_repair_store_boundary.py` (`estado`, `notas`, `adjuntos`, `riesgo`): fixture data and schema labels from `store.py` (EN-4), not copy of these four files.
- Help and legend tests that read binding labels: grep found no pin of `Seleccionar` / `Cerrar` / `salir del campo` anywhere in `tests/`.

## 4. RED / GREEN and mutants

**Census arm, RED on the base.** A scratch `git worktree` of `6092d26` under `%TEMP%` (removed), temp HOME, `tests/test_en2.py` copied in with `@pytest.mark.xfail(strict=True)` on the four file arms and the first `Z2` item. Without `--runxfail`: `2 passed, 6 xfailed`. With `--runxfail`: `6 failed, 2 passed` (the four file arms and both `Z2` sizes fail; the oracle control and the "other field leaves open card alone" item pass on both sides, by design). `mapper` was imported from the worktree (checked: its `__file__`). GREEN on this tree: `8 passed`.

**Mutants.** Harness `%TEMP%\en2-harness\mut.py` (outside the repo): byte-level read and write, sha256 pin per file checked before and after, verdict printed before the restore, `-B`, `-W error::SyntaxWarning`, temp HOME and USERPROFILE. 12 run, 12 killed, 0 survived, all four files restored (`True`). Pins (first 8 hex): `coverage.py 56528515`, `settings.py a8939696`, `inspector.py 6e0f32a3`, `rail.py 496c9432`. (`-x` stops at the first failing test, so the failure counts below are first-failure counts.)

| # | Exact text -> mutant | Killed by |
|---|---|---|
| C1 | `("q", "dismiss", "Close")` -> `"Cerrar"` (coverage) | `test_en2` coverage arm ONLY |
| C2 | `"tab walks the components` -> `"tab recorre componentes` (settings) | `test_en2` settings arm ONLY |
| C3 | `self._label("attachments")` -> `"adjuntos"` (inspector) | `test_en2` inspector arm ONLY |
| C4 | `territory` -> `territorio` (rail) | `test_en2` rail arm ONLY |
| S1 | `  the map has a cycle"` -> `  el mapa tiene un ciclo"` (rail) | `test_repair_depth` (the rail notice, `CYCLE_NOTICE`) |
| S2 | `("  required", ...)` -> `("  requerido", ...)` (inspector) | `test_inspector` / `test_darkside_census` (first failure, 1 failed) |
| S3 | `("  all complete. "` -> `("  todo completo. "` (coverage) | `test_worklist_safety` |
| S4 | `f"map . {len` -> `f"mapa . {len` (rail) | `test_repair_depth` (digests, header oracle) |
| S5 | `{total_missing} missing` -> `{total_missing} faltan` (rail) | `test_repair_depth` (digests) |
| Z1 | `_restore_open_words` never restores (`if True: return`) | `test_z2_a_focused_chip...hands_back` |
| Z2 | the key bar keeps `open card` (`if False:` in place of `groups != bar.groups`) | the same `Z2` item (key-bar half) |
| Z3 | `isinstance(widget, DsChip)` dropped and the prefix widened to `insp-` | the `Z2` items (the other-field item and the hand-back item) |

C1..C4 are killed ONLY by the census arm: no existing test pins the coverage labels or the settings hint.

## 5. Test results

- Ruff 0.8.4, `ruff check mapper tests --output-format json --no-cache`, base `6092d26` in a scratch worktree vs this tree, a programmatic set difference on (file, code, message): **26 and 26, new: none, gone: none.** (The first attempt had two new findings, `E741` in the inspector and `E402` in `test_en2.py`; both fixed before the commit.)
- `-W error::SyntaxWarning`: the four sources and `test_en2.py` compile clean; the lane below runs with it.
- Targeted: `test_en2` 8 passed; `test_inspector` + `test_en2` 20 passed; `test_repair_depth`, `test_darkside_census`, `test_inspector`, `test_worklist_safety`, `test_en2` (not slow) 131 passed; `test_arch*`, `test_attach*`, `test_inc9x3`, `test_vocabulary*`, `test_key*` 195 passed. The first targeted run, before the relabels, failed 15: 1 census, 1 inspector, 12 repair_depth (rail digests, header oracle, cycle notice), 1 worklist, all in the table above.
- Account-name grep of the staged diff (name read at run time from the environment, not printed): 0 hits; no `prototypes/`, `mapper.db` or scratch staged; Cf characters in the staged diff: none (decoded UTF-8, category `Cf`), U+2011: 0.
- Environment: temp HOME and USERPROFILE, git identity from environment variables, no network, UNC, device, real cache or real gh; no file launched (no `enter` is pressed on a chip in any new arm); scratch worktrees removed. No `git stash`. The reviewer's worktrees under `%TEMP%\en1-rev` were not touched.

## 5b. Coordinator items from the EN-1 review (folded in before the lane)

- **EN1-REV-F1 (docs).** A dated correction note was inserted under `A-129` in `01-requirements.md` (not a rewrite): the `archivo no encontrado` remap is the office prompt only; the CSV prompt at `app.py:1044` stays Spanish until EN-5; `A-129`'s blanket sentence applies only at the sites in its table. `A-130` is scoped the same way (its Statement now limits the remap to the strings as painted by its four files).
- **EN1-REV-F2 (census).** `test_en2.py`'s word list now carries common function words (`con de del el en es etiqueta la las los ningun ninguna ninguno nombre para por se sin un una y`) with whole-word matching (tokens, never substrings); the oracle control plants `(ninguna etiqueta)` and `nombre de la ruta` and asserts `delta porter lasso unity` is not flagged. `test_en1.py` was NOT changed (its `(ninguna etiqueta)`-class gap is declared for the reviewer, not fixed here). `test_en2` still 8 items, 8 passed.
- **Lane history, declared.** A first lane launch died after 18 tests (its shell exited); a second was stopped by me, about 11 minutes in, to fold in the two items above. Neither counts. The recorded lane is the one below, started after the last code and test change.

## 6. Risks, unmeasured, next

- Risks: (1) until EN-4/5/6 the UI still mixes languages around these surfaces: the key bar's `cobertura`, the legend's `territorio sin explorar`, `app.py`'s state words and toasts; the rail's `territory` caption sits beside the legend's Spanish row. (2) The census word list is explicit and finite (about 45 words); a Spanish word not on it passes. (3) `Z2` borrows the screen's hint line and key bar; a hint written by the screen WHILE a chip has focus (a search hint, for example) is left alone on blur, by design (the restore only fires if the line still carries our words), so such a hint is never clobbered, but the `open attachment` words then stay until the next hint write. Not exercised.
- Unmeasured: `Z2` while a chip is removed with focus on it (`_rebuild` restores first; no arm drives the remove key); `Z2` on screens other than the map; a rendered capture of the inspector or rail (no image was taken; the digests and AST are the evidence); POSIX; the narrow-width key bar truncation with the longer `open attachment` word beyond 87 columns (measured at 87 and 140 only).
- Left for later increments (declared): `app.py` `cobertura completa` toast, `cobertura {pct} %`, `adjuntos`, `riesgo` / `bloqueado`, `borde del territorio` (EN-5); the key bar `m cobertura` and `siguiente faltante` (EN-6, `keymap.py`); `components.py` `cargando...` default and `store.py` schema labels `estado` / `notas` (EN-4); `views/*` and the renderer-side strip (EN-3). `test_repair_depth` test names still say "spanish_notice" (ids unchanged on purpose).
- Suggested next: EN-3 (`views/*`).

## 7. Z2 (operator): done, inside the four files

`Z2` fit: no `keymap.py` or `app.py` change. `FichaInspector` handles `DescendantFocus` / `DescendantBlur` for its `insp-att-*` chips (a `DsChip` with that id prefix; the add row and the target rows are `Static`s and do not count). On focus it reads the seat's own row (`hint_pair(SCOPE_MAP, "open_ficha")`, `up arrow-enter open card`), and in the screen's `HintLine` and `KeyBar` replaces only that pair with `open attachment`, saving what it replaced. On blur, and at the start of `_rebuild` (the chip that held focus is about to be removed), it puts the saved text back if the line still carries its words. The seat still says `open card`; `map_hint()` is untouched. `ATTACHMENT_OPEN_LABEL` is the one new literal.

Evidence (`tests/test_en2.py`, real `tab` keys, both 140 and 87 columns): with a chip focused the hint reads `<enter> open attachment` and no `open card`, the key bar holds `(enter, open attachment)` and not `(enter, open card)`; chip to chip keeps it; tabbing off restores the hint and the key-bar pairs byte for byte; focusing any other field leaves `open card` alone.

## Full-lane result

`2660 passed, 1 failed, 24 deselected, 3 xfailed` in 1486 s (24 min 46 s), `python -m pytest -rf -q -W error::SyntaxWarning`, one uninterrupted process, temp HOME and USERPROFILE, git identity from environment variables, on `0ac089b` (the last code and test change), run as the last step. Baseline 2653/0; the delta is the 8 new `test_en2.py` items (2653 + 8 = 2661 = 2660 passed + 1 failed).

The one failure: `tests/test_inc9c.py::test_inc9c_ux_f3_components_scroll_and_every_tab_stop_is_on_screen[size0]` -- `tab stops off screen at (118, 34): [(12, 'DsSwitch')]`. It is a layout-timing check on the components sheet (`settings.py`, one of this increment's files), so it was not waved away:
- Alone, `-k ux_f3_components_scroll`: 2 passed. The whole file `test_inc9c.py`, three times in a row: 55 passed each (20 s).
- The edit to `settings.py` is strings only (four literals; the hint line stays one line, the demo values are the same width: `moon tide night` vs `luna marea noche` is a shorter row, never a taller one), no CSS, no row added.
- The lane ran while another process family on this machine (a different project's validator runs, dozens of python processes at once, seen in the process list) was loading the CPU; the check measures where the scroll settled after a `pause`.
- NOT measured: the same lane on `6092d26` under the same load, so "flaky under load" is the inference, not a measurement. If the reviewer reproduces it on a quiet machine, the cause is in `settings.py`'s edit and this record is wrong.

Lane history, declared: earlier launches in this session were invalid and not counted: (1) died after 18 tests when its shell exited; (2) stopped by me to fold in EN1-REV-F1/F2; (3) a lane whose temp HOME had no git identity (5 failures in `test_github.py`, all `Author identity unknown`: an environment fault of mine, not code) -- a wrapper I stopped did not stop its python child, so a second lane overlapped and wrote into the same output file; I stopped the survivor and ran the lane above to a fresh file with nothing else of mine running.
