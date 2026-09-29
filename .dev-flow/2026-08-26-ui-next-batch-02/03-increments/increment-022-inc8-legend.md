# Increment 022 · Inc-8 · the legend panel (US-N16 «leyenda») · 2026-09-28

Implements `Inc-8` per §5.4 of `01-requirements.md` on `feat/ui-next-batch-02`.
Entry HEAD `261e8df`, tree clean (`git status --porcelain` = 0 lines). Exit HEAD
is this record's commit; the tree is clean after it. Operator authorization is
dated 2026-09-28. The implementer does not review this work; independent code,
security and UX reviews follow.

## Scope and trace

| Requirement | What shipped | Arm(s) |
|---|---|---|
| `HLR-N16.2` title | `HelpScreen(scope, view=)`; the title reads `leyenda · <view>`. `MapScreen.legend_view` returns `atlas`/`outline`/`radial`, read from the same two booleans `_current_renderer` reads. `HomeScreen.legend_view = "sala"`. `MapperApp.action_help` passes it. | `test_hlr_n16_2_legend_names_the_map_view[atlas,outline,radial]`, `..._names_the_sala` |
| `LLR-N16.2.1` one declaration | `help.vocabulary_for(view)` filters `darkside.DECLARED_VOCABULARY` by `darkside.LEGEND_VIEWS`. It is a read, not a copy. Each sample is painted in `darkside.resolve_style(<declared token style>)`. Colour rows are read from `darkside.DECLARED_COLOURS`. The section headers follow 01b §3.6's order. | `test_llr_n16_2_1_every_member_is_painted_in_its_declared_style[atlas,sala]` (painted frame, clipped to `#help-dialog`, harvested over every scroll position) |
| `LLR-N16.2.1` set equality (`INC7-CR-R2-F3`) | The declaration is re-derived from 01b. The test asserts 4-tuple set **equality** in both directions, including the id. | `test_inc7_cr_r2_f3_the_declaration_EQUALS_the_document` |
| Glyph column (`INC7-CR-R2-F2`) | Every glyph now comes from the written rule G1-G4 (below) and is checked row by row. | `test_inc7_cr_r2_f2_every_glyph_follows_the_written_rule_row_by_row`, `..._the_rule_leaves_exactly_the_operator_questions_open` |
| 01b Amendment 2(b), V4/V4a | `V4a` collapses into `V4` (same triple). `darkside.DECLARED_GLYPH_RANGES = {"V4": ((0x2800, 0x28FF),)}` is derived from `V4a`'s cell. | `test_amendment_2b_V4a_collapses_into_V4_carrying_its_braille_range` |
| 01b Amendment 2(a), `#D7` on V18 | V18 contributes no member. | `test_amendment_2a_the_D7_row_contributes_no_member` (plus the existing `..._the_D7_removal_step_HAS_A_SUBJECT`) |
| Per-view partition | `LEGEND_VIEWS` is derived from the 01b section of each row (see Assumption A2). | `test_hlr_n16_2_each_view_paints_the_rows_of_its_own_01b_sections` |
| Colour rows (§3.5) | `DECLARED_COLOURS`. The test asserts equality with 01b, token hex included. | `test_llr_n16_2_1_the_colour_rows_EQUAL_section_3_5` |
| `LLR-N16.2.2` | An empty vocabulary omits the vocabulary section and the colour rows. Key rows are unchanged. | `test_llr_n16_2_2_empty_vocabulary_omits_the_section[atlas (positive control), outline]` |
| `LLR-N16.2.3` | Every string reaches the surface through `darkside.fit`, which coerces through `plain` and bounds the row in cells. The title was a `str` handed to `Static` (a markup-parsing sink) and is now a `Text`. Row width is declared as `LEGEND_ROW_CELLS = 75`. | `test_llr_n16_2_3_legend_coerces_and_bounds_every_string` (seat label, caption, sample and view name, each carrying markup, BEL, U+202E and a 60-char CJK run) |
| `HLR-N16.4` | Six help-scope seat rows: `up`, `down`, `pageup`, `pagedown`, `home`, `end`. `HelpScreen.action_legend_*` act on the pane whatever the focus state. | `test_hlr_n16_4_legend_declares_its_own_keys[140x45, 100x24]`: the key universe is **derived** from the live binding chain, and each key is pressed for real from mid-scroll |
| `C-D25a` / `C-D25b` | The declared diff is these 6 rows, all in help scope, and equals the entry/exit difference of `bindings_for("help")`. `duplicate_chords()` is empty on entry and on exit. | `test_cd25a_the_seat_diff_is_exactly_the_six_rows_inc8_declares`, `test_cd25b_no_chord_collides_on_entry_or_on_exit` |
| `#D28` | Legend chrome sits on `PANEL`: title in bold `INK`, headers and group names in `ASH`, keys in `ACCENT`, captions in `INK`. The pre-existing `MUT`-on-`PANEL` labels (3.95:1) are escalated. Samples and swatches are exempt because they paint the view's style. | `test_d28_the_legend_chrome_clears_the_contrast_floor` |

The comments at the new seams name their LLR (`help.py`, `darkside.py`, `keymap.py`, `app.py`).

**S-8 truncation** was already struck as `SATISFIED-EXTERNALLY` (PLAN §D17, `A-03`): the scroll container shipped in the repair batch. Inc-8 did no truncation work. It keeps the new sections inside that same `#help-bindings` pane, so `_painted_bindings` and `TC-R24/R36` still govern, and `HLR-N16.4` makes the keys that scroll the pane discoverable.

**Out of scope, deliberately not touched** (these belong to Inc-9): the five un-scoped `HelpScreen()` routes, the `KEY_SCOPE` declarations for Factory and Settings, and `LLR-N16.1.x`. `HLR-N16.3` / `AT-044` (the doubled chord) and the `minus` reservation are not in this brief; they are listed under Pending.

## The glyph rule (`INC7-CR-R2-F2`)

The rule is stated once, in `tests/test_vocabulary_declaration.py::sample_by_style`, and applied to every row of 01b §3.1-3.4. The rule decides what the legend **paints** as each member's sample. It is applied per style, and the first rule that yields a sample wins:

- **G1 · legend chip.** When the cell names the legend's own form (`legend chip `X``), that token is the sample for every style in the row. Applies to V17 → `⇄ enlazado` and V20 → `▲ vence`.
- **G2 · qualified pairs.** When the style cell has two or more `;`-segments, each opening with a qualifier word, and the glyph cell pairs a token with each of those words, each style takes the token of its qualifier. Applies to V19: SAGE→`█`, INK→`█`, WORDMARK→`░`.
- **G3 · leading run.** Take the backtick tokens that open the cell, separated only by whitespace, and join them with one space. Drop any token containing a `<placeholder>`, because it is a template. If nothing remains, the `e.g.` token stands in. Prose after the run is a gloss, not glyph. Examples: V3 → `▸ inv +23`, V10 → `▓ ▒ ░`, V9 → `┌──┐ │ │ └──┘`, V1 → ` rrhh ` (spaces kept).
- **G4 · nothing.** When no token exists, the result is `None`: the declaration carries `""` and the row becomes an **operator question**, never a guess. Applies to V4b and V12, which the test pins as `OPERATOR_QUESTIONS`.

Codepoint ranges (`` `U+2800`–`U+28FF` ``) are read separately. They widen the glyph set (Amendment 2(b)) and never become the sample.

Derived result: **26 members**. That equals `len(DECLARED_VOCABULARY)` before and after this increment. Only the glyph column moved:

| Row | Hand value | Rule |
|---|---|---|
| V1 | `""` | `" rrhh "` |
| V2 | `ó` | `" nómina "` |
| V3 | `+▸` | `▸ inv +23` |
| V4 | `∙` | `∙ ∙ ∙` + range |
| V5 | `▔` | `▔▔▔▔` |
| V6 | `─┌┐` | `┌─┐` |
| V7 | `·—` | the full `plegadas: …` line |
| V8 | `·` | `minimapa · 128 nodos` |
| V9 | `─│┌┐└┘` | `┌──┐ │ │ └──┘` |
| V10 | `░▒▓` | `▓ ▒ ░` |
| V14 | `✓` | `ficha completa ✓` |
| V15 | `░` | `faltan campos ░` |
| V17 | `⇄` | `⇄ enlazado` |
| V19 | `█░` (x3) | `█`, `█`, `░` |
| V20 | `▲` | `▲ vence` |

No count is written anywhere in product code.

## Questions for the operator (none blocks; each was picked explicitly or left open)

- **Q1 · V4b and V12 have prose glyph cells.** G4 applies, so the legend paints V4b's caption (`enlace entre nodos`) with an empty sample column. The consequence: V4b's two styles (`MUT`, `ACCENT`) are painted by no sample, and the style-equality arm skips members without a sample. V12 is lens-only and painted by no legend. Should 01b give V4b a sample (for example, a braille run in its range)?
- **Q2 · V4's sample `∙ ∙ ∙` is U+2219**, which is *outside* its own declared range U+2800-U+28FF. The canvas paints braille (`canvas.py` `_BRAILLE_BASE`). So the legend explains the form with a codepoint the view does not paint. Should the sample be braille?
- **Q3 · Six label cells are specification prose, not Spanish UI copy.** V7 ("overflow declaration; the `N` **shall** reconcile …"), V8, V9, V10, V19 ("coverage microbar"), and V21 (``lit `= nodo con acta`, unlit `= sin acta` ``, with backticks). They are painted **verbatim**, because the declaration must equal 01b. They are visible in the render. They need Spanish copy in 01b.
- **Q4 · The lens rows V11-V16 are declared.** They carry no `#D7` marker, but US-N14 is deferred whole (`#D23`). No legend paints them. Should they carry a deferral marker the instrument removes, as V18 does?
- **Q5 · outline and radial have an empty vocabulary** (LLR-N16.2.2 applies). Whether they paint any of §3.1/§3.2's forms (hit tone, minimap) was not ruled.
- **Q6 · V7 and V8 describe prototype lines** (`plegadas: … — N nodos`, `minimapa · N nodos`). A grep of `mapper/` finds neither string painted. See `INC8-F2`.
- **Q7 · V22 `⊘` vs `⦸`** is unchanged. `DAMAGED_MAP_GLYPH` is now defined **before** the tuple and referenced by it, so the product side is one line. Measured by mutant M25: the swap also needs 01b's V22 row to move, or `test_llr_n16_2_1_the_damaged_map_row_is_declared_and_not_deferred` reddens. The source of truth is 01b.

## Assumptions (made, recorded, swappable)

- **A1 · A-104 compound layout.** All samples of one 01b row go on one line, each in its own style, under one caption (`help.COMPOUND_ON_ONE_LINE = True`). The round-10 render has no compound row; this is the closest match to its one-caption-per-form lines. Setting it to `False` gives one line per member. Mutant M24 (the swap) leaves every arm GREEN, so layout independence is measured, not just asserted.
- **A2 · View partition.** §3.1 names "the atlas view" and §3.4 names "Sala (home)". §3.2 (minimap and overflow indicators) is assigned to **atlas**, because it lives on the map canvas and 01b §3.8 budgets the "atlas legend" with those rows. §3.3 is assigned to no view. The mapping is `SECTION_VIEW` in the test.
- **A3 · View names.** `atlas` comes from 01b §3.6's `leyenda · atlas`. `outline` and `radial` come from the seat labels `alternar outline` / `alternar radial`. `sala` names the home screen (01b §3.4, US-N13). A screen that declares no view is titled by its scope name.
- **A4 · Deviations from the round-10 frame, each forced by a ratified rule.** The alternatives were measured before being handed to a human.
  - **Dialog ground stays `PANEL`, not the prototype's `STEP`.** On `STEP` the prototype's own tones fail `#D28`: `ACCENT` keys measure 4.13:1, `MUT` labels 3.19:1, and `WORDMARK` headers 1.33:1. On `PANEL`: `ACCENT` 5.11, `ASH` 7.43, `INK` 17.18. The cost is that V1's ` rrhh ` card sample (`INK on PANEL`) does not stand out from the dialog as a card.
  - **Top-right `? cierra` became `esc cerrar`, read from the seat.** `?` is not bound inside the legend, and `HLR-N16.3` requires a second `?` to leave the stack depth unchanged. Painting `? cierra` would advertise a key that does nothing.
  - **The `?? abre la guía de campo completa` line is not painted.** The guía is batch 3. The line would advertise an inert chord, which is the US-N03 discoverability bug.
  - **The footer `cada vista tiene SU leyenda — / misma tecla, contenido de la vista`** is painted verbatim from §3.6, capital `SU` included.
  - **No border.** The legend is a modal, where borders are allowed, but the shipped dialog has none and depth comes from `PANEL` over the 70% backdrop.

## Mutation table

Discipline: a sha256 pin before each mutant, byte-level replace (each `old` must match exactly once), the named nodes run, the verdict printed **before** restoring, a byte-level restore, and the pin re-verified. The harness lives outside the repo at `%TEMP%/inc8/mutants.py`. The final battery ran on the committed state `8dea408`: 27 of 27 restores matched their pin, and `git status --porcelain` showed 0 lines afterwards.

Pins:

- `mapper/darkside.py` `50bf034fb38ad0086dddb84079698a45105f4a7f70c834e10ecb25c8193926ea`
- `mapper/screens/help.py` `44913afa7979714fa22ef3c935c04db1ab859e710b1a86a28c79d2f269f27666`
- `mapper/app.py` `b262043c50b16efc9263e43626265cdd2514caafa6f644a051d3d9d4200cca2e`
- `mapper/keymap.py` `31f9beb2d6aef1bad1ddf122a80279c512061b912fc4b4daf2b1881bcc2140ec`
- `tests/test_vocabulary_declaration.py` `0f51f8063488a5ba25f56bcc2afb0ce7b22d938ad9a796030cfc647de1f11464`

| # | Mutant | File | Verdict: arms RED |
|---|---|---|---|
| M1 | drop V10 from the declaration | darkside | **RED** `f3_EQUALS` (faithfulness stays GREEN, which is the gap F3 named) |
| M2 | rename V9's id to V9x | darkside | **RED** `f3_EQUALS` (faithfulness GREEN) |
| M3 | V3 glyph back to hand value `+▸` | darkside | **RED** `f2_row_by_row` |
| M4 | **suffix hazard**: instrument `ROW` digits-only `(V\d+)` | test instrument | **RED** `instrument_finds_the_suffixed_rows`, `f3_EQUALS`, `view_partition` |
| M5 | V4 range upper bound `0x28FE` | darkside | **RED** `2b_V4a_collapses` |
| M6 | V18 declared | darkside | **RED** `2a_D7`, `f3_EQUALS` |
| M7 | rule G1 removed | test instrument | **RED** `f2_row_by_row` |
| M8 | rule G2 removed | test instrument | **RED** `f2_row_by_row` |
| M9 | G4 guessed: V4b/MUT gets `⠿` | darkside | **RED** `f3_EQUALS`, `f2_row_by_row` |
| M9b | G3 placeholder filter removed | test instrument | **RED** `f2_row_by_row` |
| M10 | atlas partition loses V4b | darkside | **RED** `view_partition` |
| M11 | colour label drift | darkside | **RED** `colour_rows_EQUAL_3_5` |
| M12 | samples painted `INK`, not declared style | help | **RED** `every_member_painted[atlas,sala]` |
| M13 | legend reads one member only | help | **RED** `every_member_painted[atlas,sala]` |
| M14 | title names scope, not view | help | **RED** 4 title arms |
| M15 | `legend_view` loses the outline branch | app | **RED** `title[outline]`, `empty_vocabulary[outline]` |
| M15b | `action_help` drops `view=` | app | **RED** 4 title arms |
| M16 | vocabulary section painted when empty | help | **RED** `empty_vocabulary[outline]` |
| M17 | seat label uncoerced and unbounded | help | **RED** `coerces_and_bounds` |
| M18 | title handed to markup-parsing `Static(str)` | help | **RED** `coerces_and_bounds` (see F6) |
| M19 | vocabulary caption uncoerced | help | **RED** `coerces_and_bounds` |
| M20 | `home` works but its seat row is removed | keymap | **RED** `hlr_n16_4[both sizes]` |
| M21 | `M-N16.4-a`: `end` declared, pane unfocusable, action inert | help | **RED** `hlr_n16_4[both sizes]` |
| M22 | a help row rebound to `ctrl+home` | keymap | **RED** `cd25a` |
| M23 | key labels back to `MUT` on `PANEL` | help | **RED** `d28` (see F6) |
| M24 | A-104 layout swapped (expected **GREEN**) | help | **GREEN** member-style, `f3_EQUALS`, coercion |
| M25 | V22 verdict applied in darkside only | darkside | **RED** `V22 pin`, `f3_EQUALS` |

Two mutants survived the **first** battery. The arms were fixed and both went RED; see F6. One mutant (M7) failed to apply on the first pass because the test file uses LF line endings, and ran RED once the harness was corrected.

## `keymap.py` collision set (`C-D25a`/`C-D25b`, §5.4)

- **Entry**, measured at `261e8df` in a temporary worktree outside the repo (removed after): `duplicate_chords()` = `[]`; help seat = `{(escape,dismiss_none), (q,dismiss_none)}`, which equals `ENTRY_HELP_SEAT`. `pytest -k "cd25 or duplicate or whole_seat or tab or completeness"` over `test_keymap`, `test_key_dispatch`, `test_inc3_census` and `test_inc4_census` gave **15 passed**.
- **Exit** (this tree): the same selection plus Inc-8's census gave **17 passed**. That covers `test_no_duplicate_chord_inside_one_scope`, `test_at_n03h_the_whole_seat_matches_its_specification`, the Inc-3 and Inc-4b censuses, `test_llr_n06_5_no_screen_binds_tab_outside_the_recorded_exceptions`, `test_no_seat_entry_binds_tab` and `test_tab_binding_exceptions_are_still_real`.
- **Deliberate pin edits**, made in the same change as the seat:
  - `EXPECTED_PER_SCOPE[help]` 2→8
  - `EXPECTED_SEAT` +6 rows
  - the glyph display map gains `up→↑`, `down→↓`
  - `test_inc4_census`'s reconstructed-entry size 52→58, with a comment (see F4)
- **The nine-press `tab` guard** is `LLR-N14.3.2`. It is **DEFERRED (`#D23`)** and names `MapScreen`/the walk chord, not Inc-8, so it is not owed here. The shipped `tab` pins listed above were re-run on both sides and pass. Inc-8 adds no `tab` binding.

## Lane and ruff

- **First full-lane run** on `6e5275f`: `1 failed, 1197 passed, 20 deselected, 3 xfailed`. The failure was `test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts`, flagging `tests/test_help_scope.py`: the file held a literal U+202E. This is a faithful record of that tree, so it is annotated rather than struck. Fixed in `8dea408`; see F5.
- **Final full-lane run**, once, main tree, `8dea408`: **`1198 passed, 20 deselected, 3 xfailed, 0 failed`** in 428 s, with stderr kept separate from the summary. `FLAKE-1` did not fire.
- **Reconciliation.** 1170 at `c371a0d`, plus 1 from `239f242` (INC21-CR-F1's two-day arm), gives 1171 at entry `261e8df`. Measured by per-file collection, entry 1174 collected and exit 1201 collected, with 3 xfailed each. Inc-8 adds +27: `test_help_scope.py` +14, `test_keymap.py` +6 (the `at_n03a` parametrization over the six new seat rows), and `test_vocabulary_declaration.py` +7. 1171 + 27 = 1198.
- **ruff** (`--output-format=concise --no-cache`, ANSI stripped, file:line:col normalized to file:code:message): entry `261e8df` has **27 errors**, exit has **27 errors**, and `diff` of the normalized sets is empty. None of them sit in the files this increment added or rewrote.

## Render

Real Textual `run_test(size=(118, 34))` plus `export_screenshot`. The SVGs are saved outside the repo in `C:\Users\jjgh8\AppData\Local\Temp\inc8\render\`:

- `atlas_top.svg`: keys, from the map through the real `?`
- `atlas_vocab.svg`: after `end` then `pageup`, showing the atlas vocabulary
- `atlas_end.svg`: colour rows and footer
- `sala_top.svg` and `sala_end.svg`: from home

These were reached by pressing the real keys the legend now declares.

## Findings

- **`INC8-F1` · id collision on `AT-053`.** `01-requirements.md` assigns `AT-053` to `HLR-N16.4` (legend scroll keys, `A-72`, `TC-086`). Inc-4b later shipped `tests/test_search.py::test_at_053_esc_clears_a_live_search_and_stays_on_the_map` under the same id (`02l` proposed it for `esc limpiar`), and §3.5's Inc-4b list names `AT-053` too. One id now sits on two chains. Inc-8's arm is named by its HLR/TC (`test_hlr_n16_4_…`, `TC-086`) and does not claim `AT-053`. This is routed to the coordinator for re-numbering.
- **`INC8-F2` · `HLR-N16.2`'s "legend style equals the renderer's style" is unmeasured.** Inc-8 proves that the legend paints each member in its **declared** style, and that the declaration equals 01b. It does not prove the renderer paints the same, because `LLR-N16.2.1`'s "consumed by `views/layered.py`" is outside Inc-8's four files. The gap is sharpened by Q6: two declared forms (V7, V8) are not found painted by the product at all (grep of `mapper/`). **Carry**, owner to be ruled.
- **`INC8-F3` · `ctrl+q` (quit) and `ctrl+c` (Textual's own `App` bindings) have an effect inside the legend, and on every screen, yet no scope declares them.** The `HLR-N16.4` arm derives its universe with those framework keys subtracted, and says so in its docstring. **Routed**: this is a seat-wide question, not an Inc-8 one.
- **`INC8-F4` · The Inc-4b census's claim "two increments, two nodes, neither able to make the other red" is false.** Its reconstructed-entry size is a literal (`52`) over the live seat, so any later seat-toucher reddens it. Updated to 58 with a comment. A snapshot, as Inc-3 uses, would not have that property. Recorded rather than refactored.
- **`INC8-F5` (system working) · `test_fold`'s tracked-file census caught a literal U+202E.** It entered my own test through the authoring tool, which turned an escape into the character. The lane is what caught it, not care.
- **`INC8-F6` · Two of my arms were weaker than claimed until mutants showed it.**
  - M18: the coercion arm counted the markup literal anywhere, so the title was never checked on its own.
  - M23: the `#D28` arm exempted spans **by style value**, and `MUT` is also V4b's style.
  Both were fixed in `6e5275f` and re-measured RED.

## Carries

- `INC8-F1` (id collision) goes to the coordinator.
- `INC8-F2` (renderer-side style equality; V7/V8 unpainted) is open.
- `INC8-F3` (framework keys undeclared) is routed.
- Q1-Q7 go to the operator.
- The pre-existing carries from Inc-7 and the sparkline micro-increment are unchanged. Inc-8 closes `INC7-CR-R2-F2` and `INC7-CR-R2-F3`.

## Files

| Source (4 of 4 declared) | Tests and docs |
|---|---|
| `mapper/darkside.py` | `tests/test_help_scope.py` (new) |
| `mapper/screens/help.py` | `tests/test_vocabulary_declaration.py` |
| `mapper/app.py` | `tests/test_keymap.py` |
| `mapper/keymap.py` | `tests/test_key_dispatch.py` |
| | `tests/test_inc4_census.py` |
| | this record |

`.dev-flow/state.json` was not touched. Nothing was staged from `prototypes/`, `mapper.db` or scratch, and `basewt` was left untouched.

## Commits

- `1538f4a` feat(legend): the legend reads the one vocabulary declaration, derived from 01b by a written rule
- `0f342a1` test(legend): the legend panel through the painted frame
- `6e5275f` test(legend): two arms strengthened after surviving mutants
- `8dea408` test(legend): spell U+202E as an escape, not the character
- this record (docs)
