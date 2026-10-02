# Increment 049 -- Inc-EN-3: English strings in the lane, layered, outline and radial views

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `5865bc8`. Authority: `A-131` (appended to `01-requirements.md`, dated 2026-10-02), `VERDICT-inc-en-2026-10-02.md` (EN-Q1) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING. 4 source files (the cap).

## 1. What changed

Every user-facing Spanish string in the four files is plain operator English. No condition, style, key or row order moved; two geometry pins moved because a string got shorter (section 3b).

| File | Old | New |
|---|---|---|
| `views/lane.py` | `(sin ramas)` | `(no branches)` |
| `views/layered.py` | ` fuera de vista` (the overflow sentence, `overflow_phrase`) | ` out of view` |
| | `{n} nodos` (header) | `{n} nodes` |
| | `◫ sin acta` (card chip) | `◫ no record` |
| | `eliminados` (diff ghost strip) | `removed` |
| | `mapa de {n} nodos: supera el límite de {M} nodos. Se omitió el dibujo del árbol completo (fichas, aristas y cobertura).` | `map of {n} nodes exceeds the {M}-node limit; the full tree (cards, edges and coverage) was not drawn.` |
| `views/outline.py` | ` fuera de vista` (`_widen`, a second spelling of the same sentence) | ` out of view` |
| | `  {total} nodos` / ` · {missing} sin acta` (collapsed branch) | `  {total} nodes` / ` · {missing} no record` |
| | over-bound notice | `map of {n} nodes exceeds the {M}-node limit; the node list and the per-branch counts were not drawn.` |
| `views/radial.py` | over-bound notice | `map of {n} nodes exceeds the {M}-node limit; the full radial drawing (nodes, edges and labels) was not drawn.` |

Found by the FULL non-docstring literal dump (an AST walk, 4 files), beyond the census hints: `eliminados` (layered), the second `fuera de vista` spelling in `outline._widen`, and the outline note's own `nodos`. The dump also lists the already-English strings (`(no repo loaded)`, `cycle through`, ` more`, style names, ...), none Spanish.

**Chosen term for `acta`: `record`.** `acta` is the node's document field (`fields["D"]`, the `◫` chip). The legend already describes it in English as "the node's record" / "missing record" (`darkside.py` `V25`/`V26`). So: `no record` for the absence, `with record` for a count of the filled ones. `A-131` declares it for `darkside.py` (EN-4) and `app.py` (EN-5).

## 2. Files modified

Source (4, the cap): `mapper/views/lane.py`, `layered.py`, `outline.py`, `radial.py`. Tests: `tests/test_en3.py` (new, 6 items: 4 file arms, 1 oracle control, 1 lane arm); relabelled or re-derived in `test_overflow`, `test_inc3_census`, `test_repair_depth`; the call-site pin `64 -> 65` in `test_a3_census`; comment only in `test_canvas_header_charge`. Docs: `01-requirements.md` (append `A-131`), this file. `darkside.py`, `app.py`, `keymap.py`, `store.py`, `views/state.py`, `state.json`, `BACKLOG.md`, `prototypes/`, `mapper.db` not touched. Commits: `7a9d383` (code, tests, A-131), `c36ea34` (this record), then the `test_a3_census` pin.

## 3. Sealed-arm changes

| Test file | Pin | Old -> new |
|---|---|---|
| `test_overflow.py:81` | `_DECLARED`, the regex every overflow arm parses the painted declaration with | `fuera\s+de\s+vista` -> `out\s+of\s+view` (label); its docstring example `... fuera de ` / `vista ...` -> `... out of ` / `view ...` |
| `test_overflow.py:964` | NEGATIVE pin: the strip must not say the naive sum | `f"{naive} fuera de vista" not in strip` -> `f"{naive} out of view" not in strip` (the strip is built from `overflow_phrase`, so the English pin is the live one, not a vacuous Spanish one) |
| `test_inc3_census.py:383` | the diff ghost row is painted | `"eliminados" in diff_frame` -> `"removed" in diff_frame` (and the comment's `"◫ sin acta"` -> `"◫ no record"`) |
| `test_repair_depth.py:191-192` | `OMITTED`, `OVER_BOUND` (the over-bound notice fragments; the test name still says "spanish", ids unchanged on purpose) | `"Se omiti"+chr(0xF3)` -> `"not drawn"`; `"supera el l"+chr(0xED)+"mite"` -> `"exceeds the"`. The negative pin `OMITTED not in text.plain` (a map AT the bound still draws) stays live: the degraded notice is the only place the phrase appears, and the positive arm pins it in all three renderers |
| `test_repair_depth.py` `MASTER_LEGACY_DIGESTS` | 8 sha256 keys (Layered x4, Outline x4) | re-derived, see 3a. The four Radial keys did not move |
| `test_canvas_header_charge.py:253` | comment only | `fuera de vista` -> `out of view` |
| `test_a3_census.py:270` | `len(sites["argful"]) == 64`, the pinned count of arg-ful `.render(...)` call sites (found by the first full lane, which the targeted run had not covered) | `64` -> `65`, with an itemised ledger entry: the +1 is `test_en3.py`'s lane arm, the only new renderer call site |

Not relabelled, and why:
- `test_legacy_fixture.py:40-41` (`"selecciona un nodo" not in`, `"cobertura" not in`) and `"SIN ACTA" not in ... or ...`: the Spanish negative pins stay (a Spanish regression would still trip them) and EN-2 already added the English counterparts; the `SIN ACTA` pin was already vacuous (upper case against a lower-case `sin acta`) and is not made worse. Not touched.
- `test_app.py:557` (`nodos sin acta`, the dashboard hero), `test_inc9h.py:243` (`conectado: N nodos` toast), `test_strips.py:413` (`ramas sin mostrar`): painted by `app.py`, EN-5.
- Historical comments that recount an old measurement (`test_overflow.py` ~847 and ~932 `paints ▽ 15 fuera de vista`, `test_agree_floor.py:20-21`, `test_repair_depth.py` ~114 and ~135, `test_vocabulary_declaration.py:245` `V31`): they say what was painted when measured; left as the record they are. `V31` is the legend sample in `darkside.py` (EN-4).
- `test_legend_design.py:495` (`the count's sin acta`): the app's count, EN-5.

### 3a. Re-derived digests (8)

Both sides were rendered by the test file's own helpers (`_legacy_graph`, `_fingerprint`, `selected_id="fin"`) in the sizes of the pin: `5865bc8` in a scratch worktree (its twelve digests equal the pinned ones, so the harness reads the same thing) and this tree. Each render was cut into `(substring, style)` segments at every span boundary and adjacent equal-style pieces merged. With only the four mappings `sin acta -> no record` (chip and note), `nodos -> nodes`, `fuera de vista -> out of view` and `eliminados -> removed` applied to the base segments, the two segment lists are identical at all twelve keys (`True` x12; trailing pad ignored inside a segment, because the chip is padded to a fixed width). Raw widths: the chip segment is the same width (no card cell moved); the declaration segment is 20 -> 17 cells (Layered 140x8, Outline 140x8); the outline branch notes are 22 -> 23 cells (every Outline key). The four Radial digests are unchanged. The new digests are in the file under a comment saying so. The harness lives outside the repo (`%TEMP%\en3-harness`).

### 3b. Re-derived geometry pins (not label changes), declared

The declaration is three cells shorter, so two width pins moved. Both were found by the first targeted run and re-derived by sweeping on both trees, not by editing until green.
- `test_overflow.py::test_llr_n06_3_1_the_charge_band...`: `header_rows(_balanced(11999), 34, 34) == 3` and `(35, 35) == 2` became `(32, 32) == 3` and `(33, 33) == 2`. Sweep `w` 28..39: base `3` up to 34, this tree `3` up to 32.
- `test_overflow.py::test_p1_survives_a_strip_reflow...`: sizes `(32, 16)` and `(34, 14)` became `(29, 16)` and `(31, 14)` (ids `29x16`, `31x14`). The arm needs a width at which the real outline strip wraps to two rows, so the one-row stub hands the canvas a row back. Sweep `w` 24..37 at h 14, 16, 20: the stub moved the region up to w = 34 on the base (9 failures from w = 35) and up to w = 31 on this tree (18 failures from w = 32, before the change). `(24, 20)` and `(30, 16)` are unchanged.

## 4. Width checks (118 and 87 columns, and the small-height frames)

Battery rendered on both trees by one script (`%TEMP%\en3-harness\render.py`): legacy fixture through `LayeredRenderer`, `OutlineRenderer`, `RadialRenderer`, each plain and with every branch folded, at 118x34, 118x12, 87x30, 87x12; layered with a diff ghost; layered without a schema; the over-bound notice (the bound patched to 3) for the three renderers; the three lane renderers on a repo with no branches; `header_rows` of each view. 72 cases. Compared with the same word mapping (segments, trailing pad ignored): all 72 identical after the mapping; the cases where raw widths moved:
- layered and outline header declaration: -3 cells (shown in the 12-row frames);
- outline collapsed-branch rows: +1 cell (max row 40 -> 41; far inside 87);
- over-bound notice, first row: layered 115 -> 97, outline 99 -> 96, radial 111 -> 105 cells (all shorter, so it wraps no later);
- lane `(no branches)`: 12 -> 14 cells;
- card chip and `removed` caption: no row width changed; `header_rows` unchanged at 118 and 87 for the three views.

The two pins that DO depend on the shorter declaration (section 3b) are at 20..37 columns, narrower than the two reference widths.

## 5. RED / GREEN and mutants

**Census arm, RED on the base.** A scratch `git worktree` of `5865bc8` under `%TEMP%` (removed), temp HOME, `tests/test_en3.py` copied in with `@pytest.mark.xfail(strict=True)` on the four file arms and the lane arm. Without `--runxfail`: `1 passed, 5 xfailed`. With `--runxfail`: `5 failed, 1 passed` (the four file arms and the lane arm fail; the oracle control passes on both sides, by design). `mapper` was imported from the worktree (its `__file__` checked). GREEN on this tree: `6 passed`.

**Mutants.** Harness `%TEMP%\en3-harness\mut.py` (outside the repo): byte-level read and write, sha256 pin per file checked before and after, verdict printed before the restore, `-B`, `-W error::SyntaxWarning`, `-x`, temp HOME and USERPROFILE, git identity from environment. 9 run, 9 killed, 0 survived; all four files restored (`True`). Pins (first 8 hex): `radial.py 1a313966`, `lane.py a9a13b86`, `outline.py 427cd6af`, `layered.py 2f9f6226`.

| # | Exact text -> mutant | Killed by |
|---|---|---|
| C1 | radial `(nodes, edges and labels)` -> `(nodos, aristas y etiquetas)` | `test_en3` radial arm (run alone; the rest of the suite was not run against it) |
| C2 | lane `"(no branches)"` -> `"(sin ramas)"` | `test_en3` (first failure: the census; the lane arm reads the same string) |
| C3 | outline `the node list and the per-branch counts were not drawn.` -> Spanish clause | `test_en3` outline arm (run alone) |
| S1 | layered `out of view"` -> `fuera de vista"` | `test_overflow` (`test_b56...`, the relabelled regex) |
| S2 | layered `"removed"` -> `"eliminados"` | `test_inc3_census::test_a89...` |
| S3 | radial `exceeds the {MAX_RENDER_NODES}` -> `supera el {MAX_RENDER_NODES}` | `test_repair_depth::test_tc_r14...[radial]` |
| S4 | layered `"◫ no record"` -> `"◫ sin acta"` | `test_repair_depth::test_c53_legacy...[layered-140-45]` (re-derived digest) |
| S5 | outline `{missing} no record` -> `{missing} sin acta` | `test_c53_legacy...[outline-140-45]` |
| S6 | outline `_widen` `{hidden} out of view"` -> `fuera de vista"` | `test_c53_legacy...[outline-140-8]` |

## 6. Test results

- Ruff 0.8.4, `ruff check mapper tests --output-format json --no-cache`, base `5865bc8` in a scratch worktree vs this tree, a programmatic set difference on (file, code, message): **26 and 26, new: none, gone: none.**
- `-W error::SyntaxWarning`: the four sources, `test_en3.py` and the edited tests compile clean; every pytest run below carried it (the mutant runs too).
- Targeted before the fixes (one process, 466 tests: `test_layered*`, `test_outline*`, `test_overflow`, `test_radial*`, `test_lane*`, `test_strips*`, `test_canvas_header_charge`, `test_agree_floor`, `test_vocabulary*`, `test_inc3_census`, `test_repair_depth`, `test_repair_cycles`, `test_darkside_census`, `test_legend_design`, `test_app`, `test_inc9h`): `29 failed, 437 passed, 19 deselected` -- 17 `test_overflow` (the regex, the charge band, the strip stub), 1 `test_inc3_census`, 11 `test_repair_depth` (3 over-bound, 8 digests). After the section 3 / 3b changes: `test_overflow` + `test_inc3_census` + `test_repair_depth` + `test_en3`: 4 failed (3 geometry, 1 outline over-bound fragment: `"was not drawn"` against outline's `"were not drawn"`, fixed by the shorter fragment `"not drawn"`); then `test_overflow` + `test_repair_depth` + `test_en3`: `161 passed, 15 deselected`.
- Account-name grep of the staged diff (name read at run time from the environment, not printed): 0 hits; no `prototypes/`, `mapper.db` or scratch staged; Cf characters in the staged diff: none (decoded UTF-8, category `Cf`), U+2011: 0, bidi controls: 0.
- Environment: temp HOME and USERPROFILE, git identity from environment variables, no network, UNC, device, real cache or real gh; no file launched; scratch worktree removed. One scratch file a harness wrote into the repo root (`dnew.json`) was moved out before any commit; one scratch test copy (`tests/zz_scratch_p1.py`, a widened-size sweep) was deleted, never staged. No `git stash`. The EN-2 reviewer's worktrees were not touched.

## 7. Risks, unmeasured, next

- Risks: (1) until EN-4/5 the screen mixes languages around these views: the legend sample `◫ sin acta` (V26) and `▽ 35 fuera de vista` (V31) in `darkside.py` now disagree with the canvas; the dashboard hero and the strips in `app.py` still say `sin acta`, `ramas sin mostrar`. (2) The census word list is explicit and finite; a Spanish word not on it passes. (3) The outline branch note is one cell longer; at a clipped width it loses one more trailing cell.
- Unmeasured: widths other than 118, 87 and the sweep sizes; a rendered image of the canvas (digests and segment lists are the evidence); `radial`'s own labels at other fixtures; whether C1/C3 are caught by any test other than the census (run alone); POSIX.
- Left for later increments (declared): `darkside.py` `V26`, `V31` and the rest of the legend (EN-4); `app.py` `sin acta`, `con acta`, `nodos sin acta`, `ramas sin mostrar`, hints and toasts (EN-5); `keymap.py` (EN-6); `store.py` schema labels, the `views/state.py` comment mentioning `eliminados`. `test_repair_depth` test name still says "spanish" (ids unchanged on purpose).
- Suggested next: EN-4 (`store`, `darkside`, `widgets/components`), following the declared term `record`.
