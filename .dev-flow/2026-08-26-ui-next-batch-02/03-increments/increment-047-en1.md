# Increment 047 -- Inc-EN-1: English strings in `osopen`, `github`, the factory screen and the editor

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `2f80142`. Authority: `A-129` (appended to `01-requirements.md`, dated 2026-10-02), `VERDICT-inc-en-2026-10-02.md` (EN-Q1) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING. 4 source files (the cap).

## 1. What changed

Every user-facing Spanish string in the four files is plain operator English. Constant NAMES are unchanged; only values and literals moved. `app.py` compares the open status by the constant (`OK as OSOPEN_OK`, `app.py:3455`), so the value change needs nothing there. No condition, refusal sentence (`U1`, `V1`, `V2`, `W1`, `W2`, `X1`, `Y1`), `darkside.plain` call or value-echo rule was touched.

| File | Old | New |
|---|---|---|
| `osopen.py` | `abierto` / `tipo no abrible` / `destino inválido` / `esquema no permitido` / `fuera del espacio de trabajo` / `no se pudo abrir` | `opened` / `cannot open this type` / `invalid target` / `scheme not allowed` / `outside the workspace` / `could not open` |
| `github.py` | `ramas {n} · tags {n} · default …` | `branches {n} · tags {n} · default …` |
| | `leyendo ramas` (2 sites) / `calculando métricas` (2 sites) / `listo` | `reading branches` / `computing metrics` / `ready` |
| `factory.py` | `archivo de plantilla no encontrado` | `template file not found` |
| | `no se puede dibujar: el mapa tiene un ciclo` | `cannot draw: the map has a cycle` |
| | `sin documento` / `(vacío)` / `(sin tags)` | `no document` / `(empty)` / `(no tags)` |
| | `archivo no encontrado: {name}` | `file not found: {name}` |
| | `solo .docx / .pptx / .xlsx` | `only .docx / .pptx / .xlsx` |
| | `no se pudo importar {name}: {Type}` / `plantilla importada: {rel}` | `could not import {name}: {Type}` / `template imported: {rel}` |
| | `ruta del archivo office` (2 sites) / `el documento actual no es office` | `office file path` / `the current document is not an office file` |
| | `generado: {shown}` / `no se pudo generar: {Type}` | `generated: {shown}` / `could not generate: {Type}` |
| | `documento` (default tab name) / `proceso` (default `process_name`) | `document` / `process` |
| `editor.py` | `Guardar` / `Cancelar` / `Prever` | `Save` / `Cancel` / `Preview` |
| | `ctrl+s salvar · esc cancelar · tab prever` | `ctrl+s save · esc cancel · tab preview` |
| | `detectados: ` / `ninguno` | `detected: ` / `none` |

Three strings were not in the census list and were found by a full literal dump of the four files: `documento`, `proceso`, `detectados: `. The first scan (a Spanish-word regex) missed `detectados: `; the census arm's word list includes it.

Tests: `tests/test_en1.py` (new, 5 items); labels relabelled in seven files (section 3). Docs: `A-129`, this file.

## 2. Files modified

Source (4, the cap): `mapper/osopen.py`, `mapper/github.py`, `mapper/screens/factory.py`, `mapper/screens/editor.py`. Tests: `tests/test_en1.py` (new); relabelled `test_darkside_census`, `test_inc9c`, `test_inc9n`, `test_inc9o`, `test_inc9p`, `test_inc9q`, `test_repair_depth`; `test_inc9x3` (one new assertion, no relabel). Docs: `01-requirements.md` (append `A-129`), this file. `state.json`, `BACKLOG.md`, `prototypes/`, `mapper.db` not touched. Commits: `e9648db`, `9603110`, then the records.

## 3. Sealed-arm label changes (labels only; no assertion weakened)

Each is a literal substitution of the pinned text; the comparison (`==`, `in`, `not in`, `startswith`) and the surrounding structure are unchanged.

| Test file | Pin | Old -> new |
|---|---|---|
| `test_darkside_census.py:188` | hue-census site key | `no se puede dibujar: el mapa tiene un ciclo` -> `cannot draw: the map has a cycle` |
| `test_inc9c.py:307-308` | leak-detector snippets (analysed, not mutated) | `darkside.plain(f'no se pudo: {e}')` -> `darkside.plain(f'could not generate: {e}')`; `f'generado: {target}'` -> `f'generated: {target}'` |
| `test_inc9m.py` | NONE (see the full-lane correction below) | the csv prompt's `archivo no encontrado` is `app.py:1044`'s literal (EN-5) |
| `test_inc9n.py` (3 sites) | the missing sentence is not painted; the office prompt names its file | `archivo de plantilla no encontrado` -> `template file not found`; office `archivo no encontrado: t.docx` -> `file not found: t.docx`; the parametrized `missing.{ext}` pin picks the word by surface (`csv`: unchanged Spanish, `office`: `file not found`) |
| `test_repair_depth.py` | the factory tree notice (`test_tc_r32_the_factory_tree_…`) | new constant `FACTORY_CYCLE_NOTICE = "the map has a cycle"` used at that one assert; `CYCLE_NOTICE` (the rail's, EN-2) unchanged |
| `test_inc9o.py` (2 sites) | `MISSING`; the generate toast | `MISSING` -> `template file not found`; `generado: plantilla-root.docx` -> `generated: plantilla-root.docx` |
| `test_inc9p.py` (7 sites) | `MISSING`; generate toasts; import toast; one docstring | `template file not found`; `generated: …` (3); `could not generate: OSError`; `template imported: templates/t.docx` |
| `test_inc9q.py` (3 sites) | import failure; generate toasts | `could not import t.docx: `; `generated: plantilla-root.docx`; `could not generate: RuntimeError` |

Pins found by grep that were NOT relabelled, and why:
- `test_inc9x3.py` (3 sites `"abierto" in _strip(screen)`), `test_inc9f.py:439` / `test_inc9h.py:222` / `test_inc9i.py:206` (`listo`): these read text that `app.py` paints from its OWN literals (`self._event_toast("abierto", …)` at `app.py:3456`; the stage list at `app.py:1265`), not from the osopen or github values. Relabelling them now would fail. They go with `EN-5`. The coordinator's request to relabel the `test_inc9x3` `"abierto"` together with the osopen word was checked against the code and cannot be done inside EN-1 for this reason.
- `test_app.py:19,107` `progress(1, 1, "listo")`: an argument to a fake progress callback, never asserted; the app stores the label in `progress_stage` and never paints it.
- `tests/inc4_support.py:83` `E: abierto`: a fixture YAML value, not UI copy.
- `test_g6_store_surrogates`, `test_repair_*`, `test_pan`, `test_canvas_header_charge`, `test_strips`, `test_inspector`: strings from other modules (`store`, `app`, `views`, `widgets`), EN-2..EN-5.
- `test_factory`, `test_github`, `test_office`, `test_editor*` (named in the plan): grep found no pin of any translated string in them.

`test_inc9x3.py` also gains one assertion (coordinator item X3-REV-F1, not a relabel): in the file-chip key arm the same key is pressed a second time and `launcher.calls == [resolved, resolved]`.

## 4. RED / GREEN and mutants

**Census arm, RED on the base.** A scratch `git worktree` of `2f80142` under `%TEMP%` (removed), temp HOME, `tests/test_en1.py` copied in with `@pytest.mark.xfail(strict=True)` on the four file arms: without `--runxfail` `1 passed, 4 xfailed`; with `--runxfail` `4 failed, 1 passed` (the four file arms fail; `test_scanner_sees_what_it_claims` passes on both sides because it scans synthetic source). `mapper` was imported from the worktree (checked). GREEN: `5 passed` on this tree.

**Mutants.** Harness `%TEMP%\en1-harness\mut.py` (outside the repo): byte-level read and write, sha256 pin per file checked before and after (all restored: True), verdict printed before the restore, `-B`, `-W error::SyntaxWarning`, temp HOME. 10 run, 10 killed, 0 survived. Pins (HEAD files, first 8 hex): `components.py 06f77b43`, `factory.py b8f3932d`, `osopen.py 54a6b47f`, `github.py f7f29159`, `editor.py 219fa3a8`.

| # | Exact text -> mutant | Killed by |
|---|---|---|
| M1 | `f"file not found: {name}"` -> `f"archivo no encontrado: {name}"` (factory) | `test_inc9n`: 3 failed (the office-surface pins only; re-run after the correction below) |
| M2 | `f"generated: {shown}"` -> `f"generado: {shown}"` | `test_inc9p`: 4 failed |
| M3 | `f"could not generate: {type` -> `f"no se pudo generar: {type` | `test_inc9q`: 1 failed (CR-F2) |
| M4 | `"cannot draw: the map has a cycle"` -> the Spanish sentence | `test_darkside_census`: 1 failed |
| M5 | `f"template imported: {rel}"` -> `f"plantilla importada: {rel}"` | `test_inc9p`: 1 failed (CR-F2) |
| C1 | `OK = "opened"` -> `OK = "abierto"` (osopen) | `test_en1` osopen arm only |
| C2 | `progress(total, total, "ready")` -> `"listo"` (github) | `test_en1` github arm only |
| C3 | `"Save"` -> `"Guardar"` (editor) | `test_en1` editor arm only |
| C4 | `"detected: "` -> `"detectados: "` (editor) | `test_en1` editor arm only |
| MX3 | `return self.chip` -> `return self.chip if self.selected else None` (`components.py`, X3-REV-F1) | `test_inc9x3`: 4 failed (file-chip key arms, enter and space, both widths) |

C1..C4 are killed ONLY by the census arm: no existing test pins the osopen words or the editor labels, which is why the census arm exists.

**Full-lane correction (found by the first full lane, 7 failed).** My grep-driven relabel had two errors, both fixed in the commit after `0e20cc6`: (a) the csv import prompt's `archivo no encontrado: {name}` is `app.py:1044`'s own literal, not the factory's, so the csv pins in `test_inc9m` (4 sites) and `test_inc9n` (`d.csv`, and the csv half of `missing.{ext}`) went back to Spanish (a negative `not in` pin on the English word would have been vacuous); (b) `test_repair_depth` pinned `el mapa tiene un ciclo`, a fragment my grep pattern missed. The first M1 run counted 6 kills of which 3 were the csv pins, which do not depend on the factory; the 3 above are the honest count. First full lane on `0e20cc6`: `7 failed, 2646 passed, 24 deselected, 3 xfailed`.

## 5. Test results

- Ruff 0.8.4, `ruff check mapper tests --output-format json --no-cache`, base `2f80142` in a scratch worktree vs this tree, a programmatic set difference on (file, code, message): **26 and 26, new: none, gone: none.**
- `tests/test_en1.py`: 5 passed. `tests/test_inc9x3.py` (with the new assertion): 14 passed.
- Account-name grep of the staged diff (name read at run time, not printed): 0 hits; no `prototypes/`, `mapper.db` or scratch staged; no Cf characters in the changed files (decoded UTF-8; one stray U+2011 in the word list was found and removed in `9603110`).
- Environment: temp HOME and USERPROFILE, git identity from environment variables, no network, UNC, device or real cache, no real gh, no real file launched; the launcher is a recording stub in the x3 arms; scratch worktrees removed. No `git stash`. The reviewer's Inc-X3 worktree was not touched.

## 6. Risks, unmeasured, next

- Risks: (1) until EN-5 the UI mixes languages in two places: the attachment toast `abierto` and the connect-repo stage list. (2) The census word list is explicit and finite (about 45 words plus accents); a Spanish word not on it passes. (3) `github.py` progress labels are stored but never painted today; if EN-5 paints them they are already English.
- Left for EN-5 (declared): `app.py:1044` `archivo no encontrado: {name}` (the csv prompt; pinned in `test_inc9m` and `test_inc9n`); `app.py:3456` `abierto`; `app.py:1265` `iniciando` / `leyendo ramas` / `calculando métricas` / `listo`; the tests that pin them (`test_inc9x3`, `test_inc9f`, `test_inc9h`, `test_inc9i`) and the `test_app.py` fake-callback `listo`.
- Unmeasured: no rendered editor or factory screen was captured in this increment (the editor labels have no test beyond the census); POSIX; the source files outside EN-1.
- Suggested next: EN-2 (`coverage`, `settings`, `inspector`, `rail`).

## Full-lane result

`2653 passed, 24 deselected, 3 xfailed` (0 failed) in 1650 s (27 min), `python -m pytest -rf -q -W error::SyntaxWarning`, uninterrupted, on `f31480e` (the first lane, on `0e20cc6`, is the 7-failure run above), temp HOME, run as the last step. Baseline 2648/0; the delta is the 5 new `test_en1.py` items (the `test_inc9x3` assertion adds no item).

## Correction note (EN-8, 2026-10-02)

Appended; nothing above was rewritten. Scope note: the `EN1-REV` finding text was not in the EN-8 brief, so this note records only what was checked against the tree. (1) The editor labels in section 1 (`Save` / `Cancel` / `Preview`) are superseded: `EN-5` lowercased them (`save` / `cancel` / `preview`, `EN1-REV-F4`) and `tests/test_en5.py::test_the_editor_binding_labels_are_lowercase` pins them, so the claim in section 4 that no test other than the census arm pins the editor labels (C3) no longer holds for the lowercase labels. (2) The `Cancel` / `Close` labels left in `app.py` and `screens/coverage.py` were lowercased in `EN-8` (`A-136`).
