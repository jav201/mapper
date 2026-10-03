# Increment 050 -- Inc-EN-4: English strings in the store, the legend and the components; `Z1`

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `d5bedd4`. Authority: `A-132` (appended to `01-requirements.md`, dated 2026-10-02), `VERDICT-inc-en-2026-10-02.md` (EN-Q1, EN-Q2, `Z1`) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING. 4 source files (the cap): the three in scope plus `widgets/inspector.py`, declared in section 2.

## 1. What changed

Every user-facing Spanish string in `store.py`, `darkside.py` and `widgets/components.py` is plain operator English, found by a FULL non-docstring literal dump (an AST walk, 3 files). `check_map_id` accepts and refuses exactly what it did; each message echoes exactly what it echoed (a test drives all seven sentences and checks that a distinctive rejected id is not echoed). Accents are written in `A-132`; this table is ASCII for the shell.

| File | Old | New |
|---|---|---|
| `store.py` `MapIdError` | `el nombre del mapa esta vacio` / `es demasiado largo (maximo N caracteres)` / `no puede contener separadores de ruta (/ \) ni letra de unidad (:)` | `the map name is empty` / `is too long (maximum N characters)` / `cannot contain path separators (/ \) or a drive letter (:)` |
| | `contiene caracteres no validos en Windows (< > " \| ? * o de control)` / `...que no se pueden guardar en un archivo` | `contains characters that are not valid on Windows (... or control characters)` / `...that cannot be saved to a file` |
| | `usa un nombre reservado de Windows (CON, NUL, COM1...)` / `no puede empezar con espacio ni terminar en punto o espacio` | `uses a reserved Windows name (CON, NUL, COM1...)` / `cannot start with a space or end with a dot or a space` |
| | `ya existe el mapa 'X'; elige otro nombre (no se sobrescribe)` | `map 'X' already exists; choose another name (nothing is overwritten)` |
| `store.py` load notices | `campo ilegible:` / `campo duplicado:` / `adjunto sin campos:` | `unreadable field:` / `duplicate field:` / `attachment without fields:` |
| | `documento duplicado:` / `nodo duplicado:` / `nodo fantasma:` | `duplicate document:` / `duplicate node:` / `ghost node:` |
| | `... y mas registros omitidos (limite N)` | `... and more entries omitted (limit N)` |
| `store.py` refusals | `no existe el mapa 'X'` / `no se pudo leer X: Tipo` | `map does not exist: 'X'` / `could not read X: Tipo` |
| | `no se pudo leer la ficha de X: f.yml ilegible` | `could not read the card of X: f.yml unreadable` (three sites, the optional `(Tipo)` suffix kept) |
| | `el mapa tiene un ciclo:` (x2) / `mapa desincronizado:` / `no se pudo indexar` | `the map has a cycle:` / `map out of sync:` / `could not index` |
| `store.py` seeds (EN-Q2) | `nuevo mapa` / `primer hijo` + `presiona l` / `segundo hijo` + `navega con j/k` | `new map` / `first child` + `press l` / `second child` + `navigate with j/k` |
| | `legacy-audit` labels `documento dueno estado criticidad notas`; seed title `auditoria legacy` | `document owner state criticality notes`; `legacy audit` |
| `darkside.py` legend | `V2` `nomina` / `V25` `ACTA-7` / `V26` `sin acta` | `payroll` / `REC-7` / `no record` (term `record`, `A-131`) |
| | `V31` `35 fuera de vista` / `V20` `2 vencen hoy` / `V41` `retomar` | `35 out of view` / `2 due today` / `resume` |
| | `DAMAGED_MAP_STATE` `mapa danado - (enter) ver por que` | `damaged map - (enter) see why` (the `↵` invitation kept) |
| `widgets/components.py` | `DsSpinner` default `cargando...` / `DsTextField` default placeholder `nombre del mapa...` | `loading...` / `map name...` |

Beyond the census hints, the dump found: `documento duplicado`, `V2` `nomina`, `V25` `ACTA-7`, `V20`, `V41`, and the `ilegible` of the card refusal. Not found: `territorio sin explorar` is in none of the three files (the rail's `territory` is EN-2's), so nothing to translate there.

Kept as is, declared: the on-disk sidecar name `_nodos.yml` (a file-name format; renaming would orphan every saved map; the census exempts that exact literal and the control proves `_nodos.yml!` is still flagged) and the Windows device name `CON` (the census exempts the upper-case token only). A map created before this increment keeps its Spanish seed text; nothing is migrated.

**`Z1`.** `DsChip(label, selected=False, toggle=True)`. With `toggle=False`, `action_activate` posts `DsChip.Changed` with `selected` unchanged and never flips it; the inspector builds its `insp-att-*` chips with `toggle=False`. Opening still works (the inspector listens to `Changed`). The settings demo chip keeps the default and still toggles. Chosen over a chip class or an id test inside `components.py`: it is the explicit flag the operator preferred, and it is one keyword at the one call site.

## 2. Files modified

Source (4, the cap, no overage): `mapper/store.py`, `mapper/darkside.py`, `mapper/widgets/components.py`, and `mapper/widgets/inspector.py` (one line, `toggle=False`, which `Z1` needs; declared because the task said the inspector would be a 4th file). Tests: `tests/test_en4.py` (new, 10 items); relabelled or re-derived in `test_g6_store_surrogates`, `test_repair_cycles`, `test_repair_fields`, `test_repair_sidecar`, `test_repair_store_boundary`, `test_store`, `test_vocabulary_declaration`; the zero-arg render pin `35 -> 36` in `test_a3_census` (section 3); one docstring in `test_seed2`. Docs: `01-requirements.md` (append `A-132`), this file. `app.py`, `keymap.py`, `state.json`, `BACKLOG.md`, `prototypes/`, `mapper.db` not touched. Commits: `99331cc` (code, tests, A-132), then the `test_a3_census` pin, then this record.

## 3. Sealed-arm changes (labels only; none weakened)

| Test file | Pin | Old -> new |
|---|---|---|
| `test_repair_store_boundary.py` (32 occurrences, lines ~163-184, 447-461, 529-555, 632, 649) | the load-warning text per coerced position, collisions, malformed list items | `campo ilegible` / `campo duplicado` / `nodo duplicado` / `documento duplicado` -> the English prefixes; the coordinates after the colon are untouched |
| `test_repair_fields.py` (10) | field warnings, the map screen/home toast filters, the cyclic save, the refused sidecar | same prefixes; `el mapa tiene un ciclo` -> `the map has a cycle`; `no se pudo leer la ficha` -> `could not read the card` |
| `test_repair_sidecar.py` (8) | phantom id, attachment without keys, bounded origins | `nodo fantasma:` / `adjunto sin campos` / `documento duplicado:` / `campo ilegible` -> English |
| `test_repair_cycles.py` | the store's cycle message (3 pins) | `el mapa tiene un ciclo` -> `the map has a cycle`. `test_at_r01`: `"ciclo" in n` -> `"cycle" in n` while `error cargando mapa` stays: that prefix is `app.py`'s (EN-5), only the store half changed |
| `test_g6_store_surrogates.py:737` | out-of-sync warning | `"desincronizado" in w` -> `"out of sync" in w` |
| `test_store.py:46` | template seed title | `auditoria legacy` -> `legacy audit` |

Two items are not pure substitutions, declared:
- **The card-string oracle.** `test_repair_cycles._declared_card_state_string` derived the expected string from `LLR-N13.1.5` in `01-requirements.md` (so the constant has something outside the module to disagree with). That requirement is a dated record and is not rewritten, so the arm now reads the same kind of line from `A-132` (`Declared card state (English, the string that ships)`). The oracle stays outside `darkside.py`; mutant S5 shows a constant that drifts back to Spanish is caught.
- **The vocabulary equality.** `test_vocabulary_declaration` derives the declared members from `01b-ux-decisions.md`, whose samples are Spanish and also a dated record. It now carries `EN4_SAMPLES`, a one-to-one map of the six exact old samples to the six new ones, applied while deriving. It bridges only the declared relabel: a sample that is not in the map still has to equal the document, so mutant S4 (`no record` -> `sin acta`) is caught by the equality.

- **`test_a3_census.py` zero-arg pins, 35 -> 36 (both arms, one derivation).** Found by the first full lane, which the targeted run had not covered. The `Z1` arms read what a `DsChip` paints (a zero-arg Textual WIDGET `.render()`, correctly outside the A3). The first draft had five such sites (5 failures in 2 arms: derived 40 against 35); the three arms now share one helper `_look` in `test_en4.py`, so the +1 is that helper's single call, itemised in the ledger comment beside the pin.

Not relabelled, and why:
- Fixture schemas that carry their own Spanish labels (`dueno`, `criticidad`, `estado`, `documento` in `test_model`, `test_coverage`, `test_inspector`, `test_rail`, `test_diff`, `test_worklist_safety`, `test_repair_*` fixtures): test data built in the test, not read from the store seed, so no pin depends on them.
- `app.py`-painted strings that wrap or sit beside a store message (`error cargando mapa`, `no se pudo cargar X`, `no se pudo dibujar el mapa`, `no se pudo guardar`, `nodos sin acta`, `retomar`, `sin acta`, `vencen hoy`, `crea un nuevo mapa`): EN-5.
- `test_legacy_fixture.py` Spanish negative pins: unchanged (the renderer is EN-3's, English counterparts exist from EN-2).
- No negative pin went vacuous: the only Spanish `not in` pins found are the `test_legacy_fixture` pair above (already declared in EN-3) and fixture-label asserts in `test_coverage` (`criticidad`), which test a fixture, not the store.
- Historical comments that recount an old measurement were left as the record they are.

## 4. Width checks

Legend samples, cells (Python `len`, all single-cell glyphs): `payroll` 9 vs 8 (`nomina`), `REC-7` 5 vs 6, `no record` 11 vs 10, `out of view` 16 vs 19, `due today` 13 vs 14, `resume` 8 vs 9, damaged card 23 vs 27. The largest is `no record` at 11, inside the "up to eleven cells" `screens/help.py` states for the atlas samples; `test_legend_design` and `test_vocabulary_declaration` pass. The seed titles are stored text, not layout. Not measured at other widths: the help screen rendered as an image.

## 5. RED / GREEN and mutants

**Census arm, RED on the base.** A scratch `git worktree` of `d5bedd4` under `%TEMP%` (removed), temp HOME, `tests/test_en4.py` copied in with `@pytest.mark.xfail(strict=True)` on the 8 items that must fail there (three file arms, the `MapIdError` item, the seed item, and the three `Z1` items). Without `--runxfail`: `2 passed, 8 xfailed`. With `--runxfail`: `8 failed, 2 passed` (the two passes are the oracle control and `the default chip still toggles`, by design). `mapper` was imported from the worktree (its `__file__` checked). GREEN here: `10 passed`. A first draft of the real-key `Z1` arm passed on the base (two presses toggle twice and end `False`), so it was strengthened to assert after EACH press, then re-run RED.

**Mutants.** Harness `%TEMP%\h\mut.py` (outside the repo): byte-level read and write, sha256 of the file checked after the restore (every `restored True`), verdict printed before the restore, `-B`, `-W error::SyntaxWarning`, `-x`, temp HOME and USERPROFILE, git identity from environment. 13 run, 13 killed, 0 survived. Two harness slips were fixed and re-run (a pattern with two sites, a backslash eaten on the way in); the count of 13 is after those.

| # | Mutant | Killed by |
|---|---|---|
| C1 | store `the map name is empty` -> Spanish | `test_en4` store census |
| C2 | darkside `35 out of view` -> `35 fuera de vista` | `test_en4` darkside census |
| C3 | components `loading...` -> `cargando...` | `test_en4` components census |
| S1 | store `unreadable field: {node_id}.{key}` -> `campo ilegible:` | `test_repair_store_boundary` (`test_at_p02...[fields.value]`) |
| S2 | store `duplicate node:` -> `nodo duplicado:` | `test_repair_store_boundary::test_at_p02d...[node-ids-both-refused...]` |
| S3 | store seed title -> `auditoria legacy` | `test_store::test_store_create_from_template` |
| S4 | darkside `V26` `no record` -> `sin acta` | `test_vocabulary_declaration::...EQUALS_the_document` |
| S5 | darkside `DAMAGED_MAP_STATE` -> Spanish | `test_repair_cycles::test_llr_n13_1_5_...DECLARED_state_string` |
| S6 | store `map out of sync:` -> Spanish | `test_g6_store_surrogates::test_g6c_f8b...` |
| S7 | store save-time `the map has a cycle:` -> Spanish | `test_repair_cycles::test_tc_r07...` |
| S8 | store `could not read the card of ... unreadable` -> Spanish | `test_repair_fields::test_tc_r37...` |
| Z1a | inspector `toggle=False` -> `toggle=True` | `test_en4` real-key `Z1` arm (both keys) |
| Z1b | components `if self.toggle:` -> `if True:` | `test_en4` unit `Z1` arm |

Pins (first 8 hex, before and after): `store.py 1f649ca8`, `darkside.py d8c4da4b`, `components.py bc3ed8ab`, `inspector.py cb531478`.

## 6. Test results

- Ruff 0.8.4, `ruff check mapper tests --output-format json --no-cache`, base `d5bedd4` in a scratch worktree vs this tree, a programmatic set difference on (file, code, message): **26 and 26, new: none, gone: none.**
- `-W error::SyntaxWarning`: every pytest run carried it.
- Targeted (one process, 906 tests: every test file naming a changed string, plus `test_legacy_fixture`, `test_seed*`, `test_darkside_census`, `test_vocabulary*`, `test_legend*`, `test_app`, `test_search`) BEFORE the fixes: `61 failed, 844 passed` -- `test_repair_store_boundary` (37), `test_repair_fields` (11), `test_repair_sidecar` (5), `test_repair_cycles` (4), `test_g6` (1), `test_store` (1), `test_vocabulary_declaration` (2). After the section 3 changes: the failed files re-run together with `test_en4`: `269 passed, 1 failed` (`test_repair_cycles::test_at_r01`, the `"ciclo"` half, fixed), then `test_repair_cycles` `33 passed`, `test_en4` `10 passed`.
- Account-name grep of the staged diff (name read at run time, not printed): 0 hits; no `prototypes/`, `mapper.db` or `state.json` staged; Cf characters in the staged diff: none, U+2011: 0.
- Environment: temp HOME and USERPROFILE, git identity from environment variables, default basetemp, rootdir inside the repo or the worktree, no network, UNC, device, real cache or real gh; no file launched (the attachment launcher is the recording stub); scratch worktree removed; the EN-3 reviewer's worktrees under `%TEMP%\en3-rev` were not touched. No scratch file written inside the repo. No `git stash`.

## 7. Risks, unmeasured, next

- Risks: (1) until EN-5 the screen mixes languages: `app.py` still paints `sin acta`, `vencen hoy`, `retomar`, `nodos sin acta`, and prefixes store messages with `error cargando mapa` / `no se pudo cargar X:`, so the legend sample now disagrees with the dashboard hero and the resume button. (2) Maps created before this increment keep Spanish seed text and Spanish schema labels in their sidecar (nothing is migrated); only new maps get English. (3) The census word list is explicit and finite; a Spanish word not on it passes. (4) Two sealed oracles read a dated record through a declared bridge (the `A-132` line, the `EN4_SAMPLES` map); a future edit to `A-132`'s declared line moves the card oracle.
- Unmeasured: widths other than the sample cell counts; the legend rendered as an image; Windows-only behaviours of the reserved-name sentence (the text is checked, the rule is unchanged); POSIX.
- Left for later (declared): `app.py` (EN-5): `error cargando mapa`, `no se pudo cargar`, `no se pudo guardar`, `no se pudo dibujar el mapa`, `sin acta`, `con acta`, `nodos sin acta`, `vencen hoy`, `retomar`, `crea un nuevo mapa`, hints and toasts, and the `abierto` attachment toast pinned by `test_inc9x3`; `keymap.py` / `screens/palette.py` (EN-6); `?` in text fields (EN-7). Note for EN-5: `test_darkside_census.py` pins the SOURCE lines of `app.py` strings (`sin acta`, `vencen hoy`), which will need relabelling there.
- Suggested next: EN-5 (`app.py` alone).

## Full-lane result

`2677 passed, 24 deselected, 3 xfailed` in 1705.7 s (28 min 26 s), `python -B -m pytest -rf -q -W error::SyntaxWarning -p no:cacheprovider`, one uninterrupted process, temp HOME and USERPROFILE, git identity from environment variables, on `0c3e454` (the last code and test change), run as the last step. Baseline 2667; the delta is the 10 new `test_en4.py` items (2667 + 10 = 2677). No flake failed this time (FLAKE-1, FLAKE-4 did not appear).

Lane history, declared: a first full lane on `99331cc` ended `2 failed, 2675 passed` -- `test_a3_census::test_tc_a3_the_census_cardinalities_are_PINNED` and `test_llr_n07_2_2a_the_widget_protocol_was_not_swept_into_the_migration` (derived 40 zero-arg widget `.render()` sites against a pinned 35: the five `chip.render()` calls in `test_en4.py`). Not flakes. Fixed by one shared helper (+1) and the pin `35 -> 36` with a ledger entry (section 3); the two arms and `test_en4` re-run alone `25 passed`; the lane above was then re-run in full from a fresh output file, nothing else of mine running.
