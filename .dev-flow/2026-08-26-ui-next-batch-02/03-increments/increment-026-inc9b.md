# Increment 026 — Inc-9b · map-view headers and two screen titles in English (`INC9-F2`)

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `026` — **Inc-9b**, the `INC9-F2` split of Inc-9 |
| Agent | `software-dev` |
| Date | 2026-09-30 |
| Authority | `VERDICT-inc9-2026-09-30.md` § "Split" (Inc-9b); `A-112` st. 4 and 5; `VERDICT-inc8-legend-2026-09-28.md` § LANGUAGE RULING; `INC9-CR-F1` (widen the gate) |
| Starting state | `feat/ui-next-batch-02` @ `77200b8`, clean |
| Commits | `36304a3` (gate, RED by design) → `ce753f9` (implementation) → (this record) |
| Source files | **5 of a cap of 5**: `views/layered.py`, `views/radial.py`, `views/outline.py`, `screens/coverage.py`, `screens/editor.py`. `darkside.py` read, not edited |
| Tests touched | `tests/test_inc9.py` (gate, register), plus the three sealed files listed under "Changed sealed arms" (tests are uncapped) |

---

## 1 · What changed

1. **Gate first (`INC9-CR-F1`).** The single strict-xfail arm probed two headers. It is now four strict-xfail arms:
   every header and every `_degraded` banner of the three map views (atlas concept and legacy, mind map, outline);
   that each one READS `VIEW_NAMES` (every entry is monkeypatched to a sentinel and each header must follow it, so a
   header that spells its name fails even when the spelling equals the ratified word); that the atlas states its kind
   as English secondary text; and the coverage and editor titles, mounted for real, English and state-free.
   Committed RED. `--runxfail` on `77200b8`'s source: **4 of 4 arms fail**.
2. **Implementation.** The atlas header now reads `· atlas · concept map` / `· atlas · legacy tree` through one helper
   (`layered._view_label`, used by the header and the banner, so the two cannot drift). The mind map and outline headers
   and banners read `VIEW_NAMES`. The coverage title is `coverage`; the editor title is `edit document`. The xfail is
   removed and `LANGUAGE_EXCEPTIONS` is empty (the stale guard still runs and reddens the moment an entry outlives its source).
3. **Sealed arms re-derived**: only those that pin a label value or a measurement of a label's width (below).

### Assumption `INC9B-A1` (the operator may adjust)

The atlas header named the map KIND, not the view. It now names the view (`atlas`, from `VIEW_NAMES["canvas"]`) and
states the kind as secondary text: `atlas · concept map` / `atlas · legacy tree`. Changing the secondary words is a
one-line edit in `layered._view_label`; the gate pins only that an English kind follows the view name.

## English copy table

| File | Old | New |
|---|---|---|
| `views/layered.py` `_header_line`, `legacy=False` | `· mapa de conceptos` | `· atlas · concept map` (`atlas` read from `VIEW_NAMES["canvas"]`) |
| `views/layered.py` `_header_line`, `legacy=True` | `· árbol legacy` | `· atlas · legacy tree` |
| `views/layered.py` `_degraded` (both kinds) | `· mapa de conceptos` / `· árbol legacy` | same as the header, same helper |
| `views/radial.py` `_header_line` | `· mapa mental` | `· mind map` (read from `VIEW_NAMES["radial"]`) |
| `views/radial.py` `_degraded` | `· mapa mental` | `· mind map` (read) |
| `views/outline.py` `_header_line` | `· outline` (literal) | `· outline` (read from `VIEW_NAMES["outline"]`) |
| `views/outline.py` `_degraded` | `· outline` (literal) | `· outline` (read) |
| `screens/coverage.py` `#coverage-title` | `cobertura incompleta` | `coverage` |
| `screens/editor.py` `#editor-title` | `editar documento` | `edit document` |

Coverage: the old title asserted a state. The screen sets `complete` when no node is incomplete and paints
`todo completo.` under the same title (seen in the render below). `coverage` names the screen and is true in both states.
Left alone on purpose: every body string under those headers (banner prose `mapa de N nodos: ...`, the coverage table
columns `nodo` / `faltantes` / `cobertura`, `todo completo`, the editor hints and `detectados`). Those belong to Inc-9c / Inc-EN.

## Changed sealed arms (label values only; behaviour arms untouched)

The first full lane after the implementation had **10 failures**, all label-bearing. Each was bounded before it was re-derived.

| Arm | What it pinned | Re-derived how, and why it is a LABEL change |
|---|---|---|
| `tests/test_repair_depth.py::test_c53_legacy_fixture_renders_identically_to_master` x8 (Layered x4, Radial x4 sizes) | Full `(plain, spans)` digest of the render, which includes row 0 | New digests. Measured first against `git show 77200b8:` copies of both renderers: the old copy reproduces the pinned digest (same method), and at **every** one of the 8 keys exactly ONE row differs, row 0 (the header), row count unchanged. The four Outline keys are unmoved and were not re-captured |
| `tests/test_overflow.py::test_llr_n06_3_1_the_charge_band_over_node_count_and_width` | A band of the header's wrapped height over width, measured with the old label: `w >= 35` always 2 rows; node-count axis visible at `w = 31` | The legacy header is 7 cells longer after the `·` (`árbol legacy` 12, `atlas · legacy tree` 19 counting the kind), so it wraps two widths later. Re-read from the same grid: `w >= 37` always 2 rows; node-count axis at `w = 35`. The grid, the `{2,3,4}` set, the `w < 23` bound and the huge-graph `34 -> 3, 35 -> 2` pin hold unchanged |
| `tests/test_radial.py::test_at_007b_the_containment_arm_nothing_the_renderer_painted_is_lost` | `PRE_CHANGE_PAINTED`, the glyph set the pre-change render painted; it contained `l`, whose only source is `mapa mental` | `l` removed (`mind map` has none; no pill title has one). The derived containment half of the arm is unchanged |

## 2 · Files modified

Source (5): `mapper/views/layered.py`, `mapper/views/radial.py`, `mapper/views/outline.py`,
`mapper/screens/coverage.py`, `mapper/screens/editor.py`.
Tests: `tests/test_inc9.py`, `tests/test_repair_depth.py`, `tests/test_overflow.py`, `tests/test_radial.py`.
Docs: this record; `01-requirements.md` (dated note under `A-112`).

## 3 · How to test

```
set PYTHONUTF8=1
python -m pytest tests/test_inc9.py -q
python -m pytest tests/test_repair_depth.py tests/test_overflow.py tests/test_radial.py -q
python -m pytest -q          # full lane, about 15 minutes
ruff check mapper tests
```

## 4 · Test results

- **Gate RED on the base (`executed`).** `--runxfail -k inc9b` with `77200b8`'s source: 4 failed. Plain run of the same arms: 4 xfailed; `-k "inc9b or a112"`: 7 passed, 4 xfailed.
- **Targeted GREEN (`executed`).** `tests/test_inc9.py`: 38 passed. With the three sealed files: 198 passed, 15 deselected.
- **First full lane after the implementation (`executed`).** 10 failed, 1363 passed, 20 deselected, 3 xfailed (the 10 listed above; 3 xfailed = 4 minus the lifted arm).
- **Full lane at `ce753f9` (`executed`).** **1373 passed, 3 xfailed, 20 deselected, 0 failed** in 888 s (baseline 1369 passed, 4 xfailed: +4 new gate arms now green, the old xfail arm replaced by them, 3 pre-existing xfails remain).
- **Ruff (`executed`).** `ruff check mapper tests`: 27 errors, none in a file this increment changed; the same 27 on `77200b8`. (A 28th, an unused `Edge` import, was mine in the gate commit and is fixed in `ce753f9`.)
- **Known flakes:** neither `FLAKE-1` nor the `FLAKE-2` candidate fired in either lane run.

### Mutants (`executed`)

sha256 pin before, byte-level I/O in each file's own line endings, verdict printed BEFORE the restore, pin re-checked after;
harness outside the repo. Arms run per mutant: `tests/test_inc9.py -k "inc9b or a112"`.

| # | Mutant | Verdict | Killed by |
|---|---|---|---|
| M1 | radial `_header_line` back to `mapa mental` | KILLED | `each_map_view_header_names_its_view`, `..._reads_view_names_not_a_literal` |
| M2 | atlas `_view_label` back to `árbol legacy` / `mapa de conceptos` | KILLED | the same two + `the_atlas_states_its_map_kind_in_english...` |
| M3 | radial `_degraded` back to `mapa mental` | KILLED | `names_its_view`, `reads_view_names...` |
| M4 | outline `_header_line` spells literal `outline` | KILLED | `reads_view_names_not_a_literal` only (the literal equals the ratified word, so a string compare cannot see it: this is why the sentinel arm exists) |
| M5 | outline `_degraded` spells literal `outline` | KILLED | `reads_view_names_not_a_literal` |
| M6 | coverage title back to `cobertura incompleta` | KILLED | `test_a112_the_chrome_is_english[headers]`, `coverage_and_editor_titles...` |
| M7 | editor title back to `editar documento` | KILLED | the same two |
| M8 | coverage title `coverage incomplete` (English, asserts a state) | KILLED | the same two (lexicon and the state-free check) |
| M9 | atlas drops the map kind | KILLED | `the_atlas_states_its_map_kind_in_english...` |

All 9 pins matched after restore.

## 5 · Renders (`executed`; saved OUTSIDE the repo)

Directory `%TEMP%\claude\<session>\scratchpad\renders-inc9b\`: 21 text frames `<view>-<W>x<H>.txt`, the composited frame of a real
`MapScreen` (or the real `EditorScreen`) through `run_test`. Views: `atlas-concept-map`, `atlas-legacy-tree`, `mind-map`,
`outline`, `coverage-incomplete`, `coverage-complete`, `editor`; sizes 118x34 (reference), 87x34, 140x45. Header row at 118x34:

```
◆ mapper · atlas · concept map                          3  ficha
◆ mapper · atlas · legacy tree        ▰▰▰▰▰                ficha
◆ mapper · mind map                                        ficha
◆ mapper · outline                                         ficha
coverage            (over the incomplete table AND over `todo completo.`)
edit document
```

Every header fits on one row at all three sizes. The fixtures are a 3-node map; a busy map or an overflowing one was not rendered.

## 6 · Risks

- The legacy header is longer, so at header widths 35 and 36 it can charge 3 rows where the old band was always 2 (measured on the `header_rows` grid, not seen in a render at those widths). The charge and the paint share one helper, so it is honest; the cost is one body row.
- `INC9B-A1` is an assumption; the atlas kind words may be changed by the operator.
- `outline` rendered the same text before, so its protection is structural (the sentinel arm), not visible in a render.

## 7 · Pending items, findings, carries

| id | Finding / carry | Owner |
|---|---|---|
| `INC9B-A1` | Atlas header = view name + English kind; wording is the operator's to correct | operator |
| `INC9B-F1` | A label's width is a hidden input of a sealed layout band (`test_overflow` band moved 35 -> 37 when the legacy label grew). Later wording changes to header text can move it again; the band is derived from the grid, so the red arm names the new edge | Inc-9c / Inc-EN |
| `INC9B-F2` | The banner prose under each header, the coverage table columns (`nodo`, `faltantes`, `cobertura`), `todo completo`, editor hints and `detectados` are still Spanish, by scope | Inc-EN (B-71) |
| `INC9B-F3` | `INC8-P2-UX-F4` (headers name views the legend does not) is closed for the three map views by `VIEW_NAMES` reads | closed |
| `INC9B-F4` | The language census (`_screen_headers`) does not reach renderer headers (not `Screen` `Static`/`Label` ids); the new arms carry them. A renderer header added later is outside both unless it joins `_map_view_first_lines` | whoever adds one |
| — | Inc-9c (wording, naming, hints, toasts: `keymap.py`, `app.py`, `darkside.py`, `settings.py`, `help.py`; INC9-CR-F2..F8, G6-SEC-F9) | next increment, not started |

**Suggested next task:** Inc-9c per the verdict, carrying `INC9B-F1`.
