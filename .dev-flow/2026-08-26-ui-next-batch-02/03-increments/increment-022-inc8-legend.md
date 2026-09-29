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

## Corrective pass 1 (2026-09-28)

Three independent reviews (code: BLOCK-UNTIL `INC8-CR-F1`; UX: BLOCK-UNTIL `INC8-UX-F1`/`F2`; security: PASS) followed `8dea408`. This section is that corrective pass. Design questions (label copy, vocabulary source, empty-vocabulary views, side panel vs modal, V4b/V12/V4 samples, V11-V16 deferral, `⊘`/`⦸`, V19's legend chip, glyph placement) went to the operator untouched, per the brief; they are not addressed here.

Entry HEAD `fc57ac3`, tree clean. Exit is this record's commit.

### Findings, disposition

| Finding | Disposition |
|---|---|
| `INC8-CR-F1` / `INC8-UX-F1` / `INC8-UX-F10` (HIGH, blocking) | **Fixed.** `_render_own_scope_keys` paints `bindings_for(SCOPE_HELP)` (`up`/`down`/`pageup`/`pagedown`/`home`/`end`/`escape`/`q`) as its own always-visible widget (`#help-own-scope`), directly under the title, outside the scrollable pane. `LEGEND_OWN_SCOPE_GROUP` (`"en esta leyenda"`) and `LEGEND_OWN_SCOPE_FIRST` are named constants -- see ASSUMPTION A5. The arm (`test_hlr_n16_4_legend_declares_its_own_keys`) now compares `effective` against `painted` (read from the composited frame via `_painted_help_keys`, matching glyph+label together on one row) instead of `declared` (the seat). Mutants M1/M2 below. |
| `INC8-CR-F2` (MEDIUM) | **Fixed.** `test_llr_n16_2_3_legend_coerces_and_bounds_every_string` now asserts `#help-bindings`'s `scrollable_content_region.width == LEGEND_ROW_CELLS`. Mutant M3. |
| `INC8-CR-F3` (MEDIUM) | **Fixed.** `test_inc8_cr_f3_the_section_headers_and_footer_EQUAL_section_3_6` (`tests/test_vocabulary_declaration.py`) walks 01b §3.6 the way §3.5's colour table is walked: byte-read, UTF-8 decoded, anchored on `"Section headers, in order:"` / `"Footer, two lines:"`, compared in order against `help.SECTION_KEYS`/`SECTION_VOCABULARY`/`SECTION_COLOURS`/`FOOTER_LINES`. `LEGEND_OWN_SCOPE_GROUP` is deliberately NOT in that equality: 01b does not name it. Mutants: `teclas`->`atajos` and footer `SU`->`su`, both confirmed RED directly against the test (not run through the harness below, since neither is a byte-safe single-occurrence source mutation -- both were verified by monkeypatching `help_screen.SECTION_KEYS`/`FOOTER_LINES` at the module level and re-running the new test, shown in the session). |
| `INC8-CR-F4` (MEDIUM) | **Fixed.** `tests/test_inc4_census.py:91`'s `len(restored) == 58` replaced with `len(restored) == len(entry) + 1`, derived from the assertion two lines above that already pins `len(entry)`. **Checked and NOT changed:** the `== 33` at `test_cd25a_the_seat_diff_is_exactly_the_three_rows_inc4b_declares` (~L62). Both are, strictly, implied by the surrounding set-equality assertions plus the literal sizes of `ENTRY_MAP_SEAT`/`DECLARED_ADDED`/`DECLARED_REMOVED` -- but `==33` is scoped to `bindings_for("map")` alone and carries none of `==58`'s actual defect (a count over the WHOLE `KEYMAP`, which drifted when Inc-8 added six unrelated help-scope rows and needed hand-bumping 52->58). Mutant M11 demonstrates the asymmetry directly: an unrelated dummy `repo`-scope binding added to `KEYMAP` leaves the now-derived `test_inc4_census.py` green (would have reddened the old `58` literal) while the untouched `==33` stays correctly green throughout, since `bindings_for("map")` is unaffected by a `repo`-scope addition. |
| `INC8-CR-F5` (MEDIUM) | **Fixed.** `_harvest`'s member-style arm (`test_llr_n16_2_1_every_member_is_painted_in_its_declared_style`) now reads `#help-vocabulary` instead of `#help-dialog`, so the colours section's SAGE swatch (same glyph `█`, same style as `V19`'s SAGE sample) can no longer stand in for the vocabulary section actually painting it. Mutants M10a (paired: mutant + OLD region -> GREEN, proving the old arm's blindness) / M10b (same mutant + FIXED region -> RED). |
| `INC8-CR-F7` (LOW) | **Fixed.** `_render_vocabulary` groups by a `dict` keyed on row id (first-seen order preserved) instead of `itertools.groupby`, which only merges adjacent runs. `_vocabulary_line` fits each sample into the room left after the ones before it and clamps the pad with `max(0, ...)`. Mutants M4 (grouping) / M5 (pad), plus a same-shape non-adjacent-row arm (`test_inc8_cr_f7_grouping_survives_a_non_adjacent_same_id_row`) and a compound-overflow arm (`test_inc8_cr_f7_a_compound_line_cannot_exceed_the_row_budget`). |
| `INC8-SEC-F1` (LOW) | **Fixed.** `darkside.fit` maps LF/CR/TAB to a single space after `plain`'s own coercion (`_ROW_BREAKERS`), so an embedded LF can no longer paint a fabricated row and a TAB can no longer jump a terminal's own tab stops. `plain`'s own documented behaviour (LF/TAB preserved, e.g. for `widgets/inspector.py`'s notes field) is unchanged. Callers of `fit` audited: `mapper/app.py` (4 sites), `mapper/widgets/rail.py` (2 sites), `mapper/screens/help.py` (all sites), and `darkside._crumb_line`/`keybar` internally -- none depends on LF/TAB surviving into `fit`'s output. Mutant M6. |
| `INC8-SEC-F2` (LOW) | **Fixed.** `resolve_style` allow-lists darkside's own token names plus the modifiers `DECLARED_VOCABULARY`/`DECLARED_COLOURS` actually use (`bold`, `on`), derived rather than hand-listed, and raises `ValueError` on anything else. Docstring's false "stays visible" claim corrected. Mutant M7. |
| `INC8-SEC-F3` (LOW) | **Fixed.** `_render_title` clamps `hint_cells`/`glyph_cells`/`label_cells`/`title_cells`/`gap` so the assembled row can never exceed `LEGEND_ROW_CELLS`, however wide the seat's `dismiss_none` label gets. Mutant M8. |
| `INC8-SEC-F4` (LOW) | **Fixed.** A hostile `DECLARED_COLOURS` member added to `test_llr_n16_2_3_legend_coerces_and_bounds_every_string` (label only; token stays real), plus a fast isolated arm (`test_inc8_sec_f4_a_hostile_colour_label_is_coerced_and_bounded`). Mutant M9. |
| `INC8-UX-F11` (MEDIUM) | **Fixed.** `#help-bindings`'s `scrollbar-color`/`scrollbar-background` set to `ASH`/`PANEL` (7.43:1, `test_inc8_ux_f11_...` derives the ratio from the token hexes via `_contrast`), replacing Textual's own default (unstyled) thumb (measured 1.55:1). **Not `ACCENT`**: `LLR-S06.3.3` seals the `#1783ff` literal at exactly 8 tracked sites (`B-43`); a 9th would break that sealed, unrelated requirement, discovered when the first attempt (styling with `ACCENT`) reddened `tests/test_darkside_census.py::test_hue_census_no_blue_LITERAL_ships_outside_an_interactive_site`. Mutant M12. |
| `INC8-CR-F9` (LOW) | **Fixed.** `help._cells` replaced by `_cells = darkside._cells`. `LEGEND_VIEWS`/`DECLARED_GLYPH_RANGES` "Derived" comments reworded to "declared, checked against 01b" (both are hand-written literals a TEST pins equal to a derivation, not values computed from 01b at import time). `resolve_style` carries its `LLR-N16.2.1` tag. |

### New finding

- **`INC8-C1-F1`** (found while fixing `SEC-F3`): `darkside.fit(s, 0)` on single-cell-width text returned a ~15-cell string, not `""`. Rich's `set_cell_size` special-cases non-positive width with `return ""` only on its NON-single-cell-width path; on the single-cell-width path it falls through to a plain Python slice, and `text[:max_width - 1]` with `max_width = 0` slices as `text[:-1]` -- everything but the last character -- then appends the ellipsis. Measured: `darkside.fit("leyenda · atlas", 0)` returned `"leyenda · atla…"` (15 cells). Fixed with an explicit `if w <= 0: return ""` guard at the top of `fit`, before `Text` is even constructed. No existing caller passed `w <= 0` (checked: `mapper/app.py`, `mapper/widgets/rail.py`, `tests/test_darkside*.py`, `tests/test_repair_depth.py`), so this is a latent-bug fix with no behaviour change for any live caller.

### Mutation table

Discipline: sha256-pin every file before mutating, apply via text-level `str.replace` (universal-newline decoded, so the harness never has to hand-spell each file's own CRLF/LF convention) after asserting the old text occurs exactly once, run the named pytest node(s), print the verdict BEFORE restoring, restore the EXACT original bytes, and re-verify the pin. The harness lives outside the repo at `C:\Users\jjgh8\AppData\Local\Temp\inc8c1\mutants.py`.

Pins (post corrective-pass, pre-mutation -- these are also the exit pins, since every mutant restored and re-verified):

- `mapper/darkside.py` `58f24ca4c463f2aa669488ff3f9175b09d067484aca3d7b27441094f3fd01e40`
- `mapper/screens/help.py` `a95058bb9172fbf7324d9433d4b19fde1a5e9c9b2b1b3f7f680c05fa9a920699`
- `mapper/keymap.py` `31f9beb2d6aef1bad1ddf122a80279c512061b912fc4b4daf2b1881bcc2140ec`

| # | Mutant | File(s) | Verdict |
|---|---|---|---|
| M1 | `compose()` stops including the own-scope `Static` | help.py | **RED** `test_hlr_n16_4_legend_declares_its_own_keys` -- as claimed |
| M2 | PAIRED: M1's paint-mutant + the OLD (seat-comparand) arm restored | help.py + test_help_scope.py | **GREEN** (expected) -- proves the pre-corrective arm was blind to M1's exact defect |
| M3 | CSS `#help-dialog` width `80`->`64` | help.py | **RED** `test_llr_n16_2_3_legend_coerces_and_bounds_every_string` (the new pane-width assertion) |
| M4 | `_render_vocabulary`'s dict grouping reverted to `itertools.groupby` | help.py | **RED** `test_inc8_cr_f7_grouping_survives_a_non_adjacent_same_id_row` |
| M5 | `_vocabulary_line`'s per-sample room budget reverted to per-glyph-only clamp | help.py | **RED** `test_inc8_cr_f7_a_compound_line_cannot_exceed_the_row_budget` |
| M6 | `fit()` stops translating LF/CR/TAB to a space | darkside.py | **RED** `test_inc8_sec_f1_fit_never_fabricates_a_row` |
| M7 | `resolve_style` stops raising on an undeclared word | darkside.py | **RED** `test_inc8_sec_f2_resolve_style_raises_on_an_undeclared_word` |
| M8 | `_render_title` stops clamping glyph/label/title widths | help.py | **RED** `test_inc8_sec_f3_a_wide_close_label_cannot_blow_the_row_budget` |
| M9 | `_render_colours` stops fitting the label (raw label instead) | help.py | **RED** `test_inc8_sec_f4_a_hostile_colour_label_is_coerced_and_bounded` |
| M10a | V19's SAGE sample stops being painted; OLD test region (`#help-dialog`) | help.py + test_help_scope.py | **GREEN** (expected) -- proves the pre-corrective region was blind |
| M10b | SAME product mutant, FIXED region (`#help-vocabulary`) | help.py | **RED** `test_llr_n16_2_1_every_member_is_painted_in_its_declared_style[sala]` |
| M11 | Unrelated dummy `repo`-scope binding added to `KEYMAP` | keymap.py | **GREEN** (expected) -- the derived `test_inc4_census.py` line does not redden on an unrelated scope's growth, unlike the literal `58` it replaced |
| M12 | CSS `scrollbar-color` declaration removed | help.py | **RED** `test_inc8_ux_f11_the_scrollbar_thumb_clears_the_non_text_contrast_floor` |

All 13 mutants (M1-M12, M10 counted as two) ran to their expected verdict; `git status --porcelain` was 0 lines after the batch, and every pin re-verified post-restore.

`INC8-CR-F3`'s two mutants (`teclas`->`atajos`, footer `SU`->`su`) were verified directly in-session by monkeypatching `mapper.screens.help.SECTION_KEYS`/`FOOTER_LINES` and re-running `test_inc8_cr_f3_the_section_headers_and_footer_EQUAL_section_3_6`, both RED, rather than through the file-mutation harness (there is no single-occurrence byte-level source location for either -- `SECTION_KEYS`'s and `FOOTER_LINES`' definitions are one-line literals, and the harness's job of restoring the EXACT file is better served by exercising the module attribute directly for a two-word text substitution than by adding two more file mutants to the batch).

### Lane and ruff

- **Targeted, three times over the course of the pass:** `pytest tests/test_help_scope.py tests/test_vocabulary_declaration.py tests/test_inc4_census.py` -- final run **37 passed**.
- **Full default lane, once, in the main tree, post both commits (`e7b2f00`):** **1206 passed, 20 deselected, 3 xfailed, 0 failed** in 434.28s. `FLAKE-1` did not fire. Reconciliation: 1198 (Inc-8's own exit figure) + 8 new arms (`test_inc8_cr_f3_...` in `test_vocabulary_declaration.py`; `test_inc8_sec_f1/f2/f3/f4`, `test_inc8_cr_f7_...` x2, `test_inc8_ux_f11_...` in `test_help_scope.py`) = 1206.
- An earlier full-lane run (before the second commit) caught one real regression: `tests/test_repair_artifact_claims.py::test_every_cited_test_identifier_exists[help.py]`, a phantom test-name citation (`test_inc8_cr_f2_...`) left in a `help.py` comment that named a test that was never given that name (the actual arm lives inside `test_llr_n16_2_3_legend_coerces_and_bounds_every_string`). Fixed by citing the real test name. A second, earlier-still regression (`tests/test_repair_layout.py::test_tc_r25`/`test_tc_r26`, `LLR-R05.2`'s sealed requirement) is described under Findings/`INC8-CR-F1` and the commit log -- caught before any commit, by the same "run the untouched-file suite" discipline.
- **ruff** (`--output-format=concise --no-cache`, no per-file diff needed: the SET of 27 errors matches the entry baseline exactly, verified by full-corpus count both before and after). One self-introduced error (an unused `LEGEND_OWN_SCOPE_GROUP` import in `tests/test_help_scope.py`, from an early draft that referenced it only in a docstring) was caught and removed before the count was taken.

### Render

Real Textual `run_test` + `export_screenshot`, top of the atlas legend through the real `question_mark` chord, saved outside the repo:

- `C:\Users\jjgh8\AppData\Local\Temp\inc8c1\render\atlas_top_118x34.svg`
- `C:\Users\jjgh8\AppData\Local\Temp\inc8c1\render\atlas_top_80x24.svg`

### Commits (this pass)

- `9295135` fix(legend): paint the legend's own scope (HLR-N16.4) -- `INC8-CR-F1`/`INC8-UX-F1`/`UX-F10` alone.
- `e7b2f00` fix(legend): coercion, row-budget and derivation findings (CR-F2/F4/F5/F7/F9, SEC-F1-F4, UX-F11) -- every other finding, grouped in one commit rather than the brief's suggested three (test-derivation / SEC / F11+F9) because several land inside the SAME methods `9295135` already touches (`_render_title`, `_render_vocabulary`, `_vocabulary_line`), and splitting those hunks further risked staging a syntactically-broken intermediate file. `F1` -- the one split the coordinator specifically asked to see first -- is isolated in its own commit; the rest is not further subdivided. This is a deviation from the brief's exact grouping, made under time pressure at the coordinator's explicit prompt to commit as soon as green rather than continue refining commit granularity; documented here rather than left silent.
- this record (docs)

## Design pass (2026-09-28)

**What this pass is.** The operator's design verdict on the legend
(`VERDICT-inc8-legend-2026-09-28.md`, the authority for this pass), applied under the batch's
`/dev-flow` rules. Entry HEAD `ca36a3f`, tree clean. Independent reviews follow; this record does not
review its own work. Hashes cited from before the Q9 message rewrite are mapped in the verdict record.

### Verdict items applied

| Item | What was done | Commit | Arm(s) |
|---|---|---|---|
| `D2` derive from what is painted | A catalogue instrument drove each view over real fixtures and harvested every painted non-alphanumeric glyph with its style. `01b` DECISION 3 §3.1–§3.4 was rewritten from it, with a change log above §3.1 and a new **Views** column. `DECLARED_VOCABULARY` was re-derived from `01b` by the existing instrument: 41 members. | `7e1c2e2` | `test_inc7_cr_r2_f3_the_declaration_EQUALS_the_document`, `test_design_pass_a_retired_id_is_never_a_row_again` |
| `D2` close `INC8-F2` / `UX-F3` | Each view is rendered and checked in both directions: every member is painted by its view in its declared style (soundness), and every meaningful glyph the view paints belongs to a member of that view (completeness). The exclusion rule is written once and has its own arm. | `efbb9ac` | `test_d2_the_legend_and_the_view_agree_in_both_directions[atlas, esquema, mapa mental, sala]`, `test_d2_the_exclusion_rule_keeps_the_forms_the_catalogue_kept` |
| `D1` copy | Every surviving and new row has short, lowercase Spanish copy. It starts from the ux reviewer's proposal and is corrected where the painted form means something else. See *Copy, in one place* below. | `7e1c2e2` | `test_llr_n16_2_1_every_declared_row_is_FAITHFUL_to_the_document`, EQUALS |
| `D3` esquema and mapa mental | `LEGEND_VIEWS` has four views. Radial gets braille (`V4b`), `●` (`V42`, `V43`) and the root `◆` (`V44`). All three map views share the rail and strip rows, so `▾ ▸ ▽` (`V33`, `V34`, `V31`) are in esquema. Braille left the atlas. | `7e1c2e2` | `test_hlr_n16_2_each_view_paints_the_rows_its_01b_views_column_names`, the D2 arm |
| `Q1·Q2` | `V4b` moved to radial with a measured braille run as its sample, `⣉⡉⠉`. `V4`'s braille range left `DECLARED_GLYPH_RANGES`. The mechanism stays, because `V29` (box-drawing wires), `V4b` (braille) and `V40` (activity bars) own ranges. `V4` itself is retired; see `INC8-D-Q2`. | `7e1c2e2` | `test_every_declared_range_EQUALS_the_document` |
| `Q4` | `V11`–`V16` carry `DEFERRED(#D7)`, so they leave the declaration. Their rows stay in §3.3. | `7e1c2e2` | `test_design_pass_q4_the_lens_rows_are_marked_deferred_and_not_declared` |
| `Q8` | `V19`'s sample stays `█ █ ░`, now in the tones the sala paints (`INK`, `WARN`, `WORDMARK`). | `7e1c2e2` | EQUALS, the D2 arm `[sala]` |
| `Q7` | No change (`⊘`). | — | — |
| `D4` side panel | Docked top-right at ≥ 118 columns, the modal below. The panel is modal for keys in both layouts. See *D4* below. | `9136a3f` | six `test_d4_*` arms |
| `D5` names | `MapScreen.legend_view` returns `atlas` / `esquema` / `mapa mental`; the sala stays `sala`. Other screens' headers are untouched (Inc-9 carry). | `7e1c2e2` | `test_hlr_n16_2_legend_names_the_map_view[atlas, esquema, mapa mental]` |
| `A5` | Unchanged. The own-scope group `en esta leyenda` is still pending ratification. | — | — |

### The catalogue instrument

`%TEMP%\inc8d\catalogue.py`, outside the repo. Re-run it from the repo root:

```
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python %TEMP%/inc8d/catalogue.py --md
```

- **What it drives.** `MapperApp.run_test` at 118×34 and 140×45. Two fixtures: a legacy map
  (8 branches × 5 leaves; every third branch complete; one leaf due today) and a concept map
  (6 × 3, with meta lines). Each state runs in a **fresh app**. The atlas states are rest, walk,
  fold a branch, search `fin`, rail focus, rail focus after a walk (the unfocused selection), and
  fold the root (the rail's lattice shows only when the rail is short). Esquema (`o`) and mapa
  mental (`r`) use the same fixtures and similar states. The sala uses a legacy map, a concept map,
  a cyclic `roto.mmd` and a recorded session.
- **What it reads.** The composited frame (`screen._compositor.render_strips()`), cell by cell. For
  each cell it records the glyph, fg, bg, bold and the widget under it. Nothing in it judges
  meaning; the `--md` table below adds each row's disposition with the **same** rule the arm
  enforces (it imports `tests/test_legend_design.py`).
- **Two date-driven glyphs.** A re-run on another day can differ in the tab strip's moon
  (`darkside.moon(date.today())`) and in the sala's sparkline tiers (file mtimes). Both are named
  here so a difference there is not read as drift.
- **Its own defect, caught and fixed before use (`INC8-D-F3`).** The first run harvested the rest
  state during the screen's fade-in and recorded interpolated tones the product never declares
  (`#b8b8b8` for `INK`, `#1c1c1c` for `STEP`, `#c33c32` for `ALERT`). Every state now waits for
  scheduled animations and runs in a fresh app. The arm does the same.

**The exclusion rule**, written once in `tests/test_legend_design.py` (`meaningful`,
`_excluded_widget`):

| Rule | Excludes | Why |
|---|---|---|
| `X1` text | letters, digits, spaces (`L*`, `N*`, `Z*`) | text is not a glyph; also covers padding |
| `X2` punctuation | Unicode `P*`, and every ASCII symbol | separators (`·` in `mapa · 36n`), ellipses, `+`, `/`, `%` |
| `X3` app chrome | the tab strip (with the moon wordmark `◕`), the hint line, the key bar, the sala's identity row | the same on every screen; not the view |
| `X4` key glyphs | a character the seat uses as a key's glyph (`↵`, `↑`, `↓`) | the legend's key section explains them |
| `X5` table header | a `DataTable`'s column-header row (`▐ name` in the sala) | column chrome |

**Known blind spots**, stated so a green run is not over-read:

- Completeness is per **character**, not per style. A declared glyph painted in an undeclared tone
  is caught only if that tone is itself a member (by soundness). Overlay tones — the selection
  block, hit livery, rail selection, radial pills on `PANEL` — are therefore not individually
  declared for every glyph they cover.
- `X2` hides `·`, which the rail's lattice uses as a mark (`V21b`). Soundness still checks it.
- The diff mode (`=`) is not driven, because it needs a git history. Its tones are seen by neither
  direction: `▐` in `ACCENT` for an added node, the `WARN` change chip, `ALERT` ghosts, and
  `ACCENT` wires. This is a carry.
- The hero's large numerals are drawn in `█`. They are covered character-wise by `V19` and
  style-wise by coincidence, because they paint `INK` or `WARN` like the bars.

**The catalogue table** (both sizes and all states merged; ASCII rows painted by the view are omitted as `X1`/`X2`; `n` is the cell count over all harvested frames). The disposition column is computed by the arm's own rule: `= Vn` is the member that explains the row in its declared style; *glyph of Vn, tone of an overlay* is a declared glyph under a selection, hit or rail-cursor tone (covered by completeness per character, see the blind spots).

| view | glyph | code point | fg | bg | bold | widget(s) | n | disposition |
|---|---|---|---|---|---|---|---|---|
| atlas | `/` | U+002F | #737373 | #000000 |  | HintLine | 64 | X3 app chrome |
| atlas | `·` | U+00B7 | #737373 | #000000 |  | HintLine | 56 | X3 app chrome |
| atlas | `↵` | U+21B5 | #737373 | #000000 |  | HintLine | 24 | X3 app chrome |
| atlas | `▸` | U+25B8 | #737373 | #000000 |  | HintLine | 28 | X3 app chrome |
| atlas | `+` | U+002B | #3a3a3a | #000000 |  | KeyBar | 28 | X3 app chrome |
| atlas | `/` | U+002F | #1783ff | #000000 |  | KeyBar | 28 | X3 app chrome |
| atlas | `?` | U+003F | #1783ff | #000000 |  | KeyBar | 28 | X3 app chrome |
| atlas | `…` | U+2026 | #3a3a3a | #000000 |  | KeyBar | 28 | X3 app chrome |
| atlas | `↵` | U+21B5 | #1783ff | #000000 |  | KeyBar | 28 | X3 app chrome |
| atlas | `/` | U+002F | #737373 | #000000 |  | TabStrip | 28 | X3 app chrome |
| atlas | `◕` | U+25D5 | #3a3a3a | #000000 |  | TabStrip | 28 | X3 app chrome |
| atlas | `▰` | U+25B0 | #f5f5f5 | #121212 |  | insp-coverage | 28 | = V32 |
| atlas | `▱` | U+25B1 | #262626 | #121212 |  | insp-coverage | 14 | = V32 |
| atlas | `·` | U+00B7 | #737373 | #000000 |  | map-canvas, map-rail | 84 | X2 punctuation |
| atlas | `…` | U+2026 | #000000 | #1783ff | b | map-canvas | 4 | X2 punctuation |
| atlas | `…` | U+2026 | #737373 | #000000 |  | map-canvas | 8 | X2 punctuation |
| atlas | `…` | U+2026 | #f5f5f5 | #000000 |  | map-canvas | 13 | X2 punctuation |
| atlas | `…` | U+2026 | #f5f5f5 | #262626 |  | map-canvas | 4 | X2 punctuation |
| atlas | `…` | U+2026 | #f5f5f5 | #121212 |  | map-canvas | 4 | X2 punctuation |
| atlas | `…` | U+2026 | #ff4f42 | #000000 |  | map-canvas | 7 | X2 punctuation |
| atlas | `─` | U+2500 | #f5f5f5 | #000000 |  | map-canvas | 2168 | = V29 |
| atlas | `│` | U+2502 | #f5f5f5 | #000000 |  | map-canvas | 35 | = V29 |
| atlas | `┌` | U+250C | #f5f5f5 | #000000 |  | map-canvas | 71 | = V29 |
| atlas | `┐` | U+2510 | #f5f5f5 | #000000 |  | map-canvas | 29 | = V29 |
| atlas | `┬` | U+252C | #f5f5f5 | #000000 |  | map-canvas | 44 | = V29 |
| atlas | `┼` | U+253C | #f5f5f5 | #000000 |  | map-canvas | 35 | = V29 |
| atlas | `▐` | U+2590 | #000000 | #1783ff | b | map-canvas | 11 | = V23 |
| atlas | `▐` | U+2590 | #262626 | #000000 |  | map-canvas | 148 | = V1 |
| atlas | `▐` | U+2590 | #f5f5f5 | #262626 |  | map-canvas | 20 | = V2 |
| atlas | `▐` | U+2590 | #f5f5f5 | #121212 |  | map-canvas | 4 | = V24 |
| atlas | `▐` | U+2590 | #ffd230 | #000000 |  | map-canvas | 8 | = V3 |
| atlas | `░` | U+2591 | #262626 | #000000 |  | map-canvas | 24 | = V28 |
| atlas | `▰` | U+25B0 | #f5f5f5 | #000000 |  | map-canvas, map-pagination | 70 | = V32 |
| atlas | `▱` | U+25B1 | #262626 | #000000 |  | map-canvas, map-pagination | 672 | = V32 |
| atlas | `▸` | U+25B8 | #737373 | #000000 |  | map-canvas | 8 | = V3/V34 |
| atlas | `▽` | U+25BD | #f5f5f5 | #000000 |  | map-canvas, map-pagination | 56 | = V31 |
| atlas | `◆` | U+25C6 | #f5f5f5 | #000000 |  | map-canvas | 28 | = V30 |
| atlas | `◫` | U+25EB | #f5f5f5 | #000000 |  | map-canvas | 74 | = V25 |
| atlas | `◫` | U+25EB | #ff4f42 | #000000 |  | map-canvas | 12 | = V26 |
| atlas | `✓` | U+2713 | #f5f5f5 | #000000 |  | map-canvas | 148 | = V27 |
| atlas | `╱` | U+2571 | #3a3a3a | #000000 |  | map-minimap | 28 | = V39 |
| atlas | `█` | U+2588 | #f5f5f5 | #000000 |  | map-minimap | 70 | = V36 |
| atlas | `░` | U+2591 | #ffd230 | #000000 |  | map-minimap | 154 | = V38 |
| atlas | `▒` | U+2592 | #737373 | #000000 |  | map-minimap | 56 | = V37 |
| atlas | `·` | U+00B7 | #3a3a3a | #000000 |  | map-rail | 36 | X2 punctuation; = V21b |
| atlas | `∙` | U+2219 | #737373 | #000000 |  | map-rail | 262 | = V21a |
| atlas | `▸` | U+25B8 | #f5f5f5 | #262626 |  | map-rail | 8 | glyph of V3/V34, tone of an overlay |
| atlas | `▾` | U+25BE | #000000 | #1783ff | b | map-rail | 8 | glyph of V33, tone of an overlay |
| atlas | `▾` | U+25BE | #737373 | #000000 |  | map-rail | 138 | = V33 |
| atlas | `▾` | U+25BE | #f5f5f5 | #262626 |  | map-rail | 8 | glyph of V33, tone of an overlay |
| esquema | `/` | U+002F | #737373 | #000000 |  | HintLine | 64 | X3 app chrome |
| esquema | `·` | U+00B7 | #737373 | #000000 |  | HintLine | 48 | X3 app chrome |
| esquema | `↵` | U+21B5 | #737373 | #000000 |  | HintLine | 20 | X3 app chrome |
| esquema | `▸` | U+25B8 | #737373 | #000000 |  | HintLine | 24 | X3 app chrome |
| esquema | `+` | U+002B | #3a3a3a | #000000 |  | KeyBar | 24 | X3 app chrome |
| esquema | `/` | U+002F | #1783ff | #000000 |  | KeyBar | 24 | X3 app chrome |
| esquema | `?` | U+003F | #1783ff | #000000 |  | KeyBar | 24 | X3 app chrome |
| esquema | `…` | U+2026 | #3a3a3a | #000000 |  | KeyBar | 24 | X3 app chrome |
| esquema | `↵` | U+21B5 | #1783ff | #000000 |  | KeyBar | 24 | X3 app chrome |
| esquema | `/` | U+002F | #737373 | #000000 |  | TabStrip | 24 | X3 app chrome |
| esquema | `◕` | U+25D5 | #3a3a3a | #000000 |  | TabStrip | 24 | X3 app chrome |
| esquema | `▰` | U+25B0 | #f5f5f5 | #121212 |  | insp-coverage | 24 | = V32 |
| esquema | `▱` | U+25B1 | #262626 | #121212 |  | insp-coverage | 12 | = V32 |
| esquema | `·` | U+00B7 | #000000 | #1783ff | b | map-canvas | 18 | X2 punctuation |
| esquema | `·` | U+00B7 | #737373 | #000000 |  | map-canvas, map-rail | 72 | X2 punctuation |
| esquema | `·` | U+00B7 | #ffd230 | #000000 |  | map-canvas | 114 | X2 punctuation |
| esquema | `▽` | U+25BD | #f5f5f5 | #000000 |  | map-canvas, map-pagination | 24 | = V31 |
| esquema | `◆` | U+25C6 | #f5f5f5 | #000000 |  | map-canvas | 24 | = V30 |
| esquema | `╱` | U+2571 | #3a3a3a | #000000 |  | map-minimap | 24 | = V39 |
| esquema | `█` | U+2588 | #f5f5f5 | #000000 |  | map-minimap | 60 | = V36 |
| esquema | `░` | U+2591 | #ffd230 | #000000 |  | map-minimap | 132 | = V38 |
| esquema | `▒` | U+2592 | #737373 | #000000 |  | map-minimap | 48 | = V37 |
| esquema | `▰` | U+25B0 | #f5f5f5 | #000000 |  | map-pagination | 24 | = V32 |
| esquema | `▱` | U+25B1 | #262626 | #000000 |  | map-pagination | 552 | = V32 |
| esquema | `·` | U+00B7 | #3a3a3a | #000000 |  | map-rail | 36 | X2 punctuation; = V21b |
| esquema | `∙` | U+2219 | #737373 | #000000 |  | map-rail | 237 | = V21a |
| esquema | `▸` | U+25B8 | #f5f5f5 | #262626 |  | map-rail | 8 | glyph of V34, tone of an overlay |
| esquema | `▾` | U+25BE | #000000 | #1783ff | b | map-rail | 4 | glyph of V33, tone of an overlay |
| esquema | `▾` | U+25BE | #737373 | #000000 |  | map-rail | 116 | = V33 |
| esquema | `▾` | U+25BE | #f5f5f5 | #262626 |  | map-rail | 8 | glyph of V33, tone of an overlay |
| mapa mental | `/` | U+002F | #737373 | #000000 |  | HintLine | 48 | X3 app chrome |
| mapa mental | `·` | U+00B7 | #737373 | #000000 |  | HintLine | 40 | X3 app chrome |
| mapa mental | `↵` | U+21B5 | #737373 | #000000 |  | HintLine | 16 | X3 app chrome |
| mapa mental | `▸` | U+25B8 | #737373 | #000000 |  | HintLine | 20 | X3 app chrome |
| mapa mental | `+` | U+002B | #3a3a3a | #000000 |  | KeyBar | 20 | X3 app chrome |
| mapa mental | `/` | U+002F | #1783ff | #000000 |  | KeyBar | 20 | X3 app chrome |
| mapa mental | `?` | U+003F | #1783ff | #000000 |  | KeyBar | 20 | X3 app chrome |
| mapa mental | `…` | U+2026 | #3a3a3a | #000000 |  | KeyBar | 20 | X3 app chrome |
| mapa mental | `↵` | U+21B5 | #1783ff | #000000 |  | KeyBar | 20 | X3 app chrome |
| mapa mental | `/` | U+002F | #737373 | #000000 |  | TabStrip | 20 | X3 app chrome |
| mapa mental | `◕` | U+25D5 | #3a3a3a | #000000 |  | TabStrip | 20 | X3 app chrome |
| mapa mental | `▰` | U+25B0 | #f5f5f5 | #121212 |  | insp-coverage | 20 | = V32 |
| mapa mental | `▱` | U+25B1 | #262626 | #121212 |  | insp-coverage | 10 | = V32 |
| mapa mental | `braille` | U+28xx | #1783ff | #000000 |  | map-canvas | 70 | = V4b |
| mapa mental | `braille` | U+28xx | #737373 | #000000 |  | map-canvas | 1135 | = V4b |
| mapa mental | `braille` | U+28xx | #737373 | #121212 |  | map-canvas | 80 | = V4b |
| mapa mental | `braille` | U+28xx | #a3a3a3 | #121212 |  | map-canvas | 110 | = V4b |
| mapa mental | `braille` | U+28xx | #a3a3a3 | #000000 |  | map-canvas | 1380 | = V4b |
| mapa mental | `braille` | U+28xx | #f5f5f5 | #000000 |  | map-canvas | 1470 | = V4b |
| mapa mental | `braille` | U+28xx | #f5f5f5 | #121212 |  | map-canvas | 80 | = V4b |
| mapa mental | `·` | U+00B7 | #737373 | #000000 |  | map-canvas, map-rail | 60 | X2 punctuation |
| mapa mental | `▽` | U+25BD | #f5f5f5 | #000000 |  | map-canvas, map-pagination | 20 | = V31 |
| mapa mental | `◆` | U+25C6 | #000000 | #1783ff | b | map-canvas | 16 | glyph of V44/V30, tone of an overlay |
| mapa mental | `◆` | U+25C6 | #1783ff | #121212 |  | map-canvas | 4 | = V44 |
| mapa mental | `◆` | U+25C6 | #f5f5f5 | #000000 |  | map-canvas | 20 | = V30 |
| mapa mental | `●` | U+25CF | #000000 | #1783ff | b | map-canvas | 4 | glyph of V42/V43, tone of an overlay |
| mapa mental | `●` | U+25CF | #1783ff | #121212 |  | map-canvas | 4 | = V43 |
| mapa mental | `●` | U+25CF | #737373 | #121212 |  | map-canvas | 160 | = V42 |
| mapa mental | `●` | U+25CF | #a3a3a3 | #121212 |  | map-canvas | 202 | = V42 |
| mapa mental | `●` | U+25CF | #f5f5f5 | #121212 |  | map-canvas | 220 | = V42 |
| mapa mental | `╱` | U+2571 | #3a3a3a | #000000 |  | map-minimap | 20 | = V39 |
| mapa mental | `█` | U+2588 | #f5f5f5 | #000000 |  | map-minimap | 50 | = V36 |
| mapa mental | `░` | U+2591 | #ffd230 | #000000 |  | map-minimap | 110 | = V38 |
| mapa mental | `▒` | U+2592 | #737373 | #000000 |  | map-minimap | 40 | = V37 |
| mapa mental | `▰` | U+25B0 | #f5f5f5 | #000000 |  | map-pagination | 20 | = V32 |
| mapa mental | `▱` | U+25B1 | #262626 | #000000 |  | map-pagination | 460 | = V32 |
| mapa mental | `·` | U+00B7 | #3a3a3a | #000000 |  | map-rail | 36 | X2 punctuation; = V21b |
| mapa mental | `∙` | U+2219 | #737373 | #000000 |  | map-rail | 212 | = V21a |
| mapa mental | `▸` | U+25B8 | #f5f5f5 | #262626 |  | map-rail | 4 | glyph of V34, tone of an overlay |
| mapa mental | `▾` | U+25BE | #000000 | #1783ff | b | map-rail | 4 | glyph of V33, tone of an overlay |
| mapa mental | `▾` | U+25BE | #737373 | #000000 |  | map-rail | 92 | = V33 |
| mapa mental | `▾` | U+25BE | #f5f5f5 | #262626 |  | map-rail | 8 | glyph of V33, tone of an overlay |
| sala | `▸` | U+25B8 | #737373 | #000000 |  | HintLine | 2 | X3 app chrome |
| sala | `+` | U+002B | #3a3a3a | #000000 |  | KeyBar | 2 | X3 app chrome |
| sala | `/` | U+002F | #1783ff | #000000 |  | KeyBar | 2 | X3 app chrome |
| sala | `?` | U+003F | #1783ff | #000000 |  | KeyBar | 2 | X3 app chrome |
| sala | `…` | U+2026 | #3a3a3a | #000000 |  | KeyBar | 2 | X3 app chrome |
| sala | `↵` | U+21B5 | #1783ff | #000000 |  | KeyBar | 2 | X3 app chrome |
| sala | `◕` | U+25D5 | #3a3a3a | #000000 |  | TabStrip | 2 | X3 app chrome |
| sala | `▁` | U+2581 | #3a3a3a | #121212 |  | home-hero | 26 | = V40 |
| sala | `█` | U+2588 | #737373 | #121212 |  | home-hero | 2 | = V40 |
| sala | `█` | U+2588 | #ffd230 | #121212 |  | home-hero | 42 | = V19 |
| sala | `▲` | U+25B2 | #ffd230 | #121212 |  | home-hero | 2 | = V20 |
| sala | `◕` | U+25D5 | #3a3a3a | #000000 |  | home-identity | 2 | X3 app chrome |
| sala | `█` | U+2588 | #f5f5f5 | #000000 |  | home-microbar | 12 | = V19 |
| sala | `█` | U+2588 | #ffd230 | #000000 |  | home-microbar | 8 | = V19 |
| sala | `░` | U+2591 | #3a3a3a | #000000 |  | home-microbar | 20 | = V19 |
| sala | `—` | U+2014 | #f5f5f5 | #121212 |  | home-recents | 2 | X2 punctuation |
| sala | `—` | U+2014 | #f5f5f5 | #1c1c1c |  | home-recents | 4 | X2 punctuation |
| sala | `↵` | U+21B5 | #f5f5f5 | #121212 |  | home-recents | 2 | X4 key glyph |
| sala | `⊘` | U+2298 | #f5f5f5 | #121212 |  | home-recents | 2 | = V22 |
| sala | `▐` | U+2590 | #737373 | #2f2f2f | b | home-recents(header) | 4 | X5 table header |
| sala | `↩` | U+21A9 | #000000 | #1783ff | b | home-resume | 2 | = V41 |

### `01b` change log

It lives in `01b` itself, above §3.1, so there is one copy. In summary:

- **Reused, form survives:** `V1` (card edge `▐`), `V2` (hit card), `V3` (fold pill, now with its
  `WARN` bar), `V4b` (braille, now in radial), `V19` (microbar), `V20` (`▲`), `V22` (`⊘`).
- **Split:** `V21` becomes `V21a` / `V21b`, the rail lattice's lit and unlit dot, in the same two
  styles.
- **Retired, never reused:** `V4`, `V4a`, `V5`, `V6`, `V7`, `V8`, `V9`, `V10`, `V17`.
- **Deferred with the `#D7` marker:** `V11`–`V16` (verdict `Q4`), and `V18` as before.
- **New:** `V23`–`V44`.

`01-requirements.md` gained **`A-106`**, because `HLR-N06.3`'s `PRED-4` discharge literally names
`V7`, `V8` and `V4`. The amendment resolves those ids to `V31` and `V21b` and changes no threshold.
`A-106` was the next free id after a scan of all of `.dev-flow`; `A-105` was the last taken.

### Copy, in one place (`D1`) — for the operator to correct

The Spanish label each row paints, in the order the legend paints it. **Deviation** marks where the
copy departs from the reviewer's proposal, with the reason.

| Row | Sample | Label | Note |
|---|---|---|---|
| `V1` | `▐` | nodo del mapa | |
| `V2` | `▐ nómina` | coincidencia de búsqueda | |
| `V23` | `▐ erp` | nodo seleccionado | |
| `V24` | `▐ erp` | seleccionado, con el foco en otra región | |
| `V3` | `▐ ▸ inv +23` | rama plegada (23 dentro) | |
| `V25` | `◫ ACTA-7` | acta del nodo | |
| `V26` | `◫ sin acta` | nodo sin acta | painted in `ALERT`; `INC8-D-Q1` |
| `V27` | `✓` | campo del esquema lleno | |
| `V28` | `░` | campo del esquema pendiente | |
| `V29` | `┬─┐` | enlace entre nodos | |
| `V4b` | `⣉⡉⠉` ×4 tones | enlace entre nodos (en azul, camino al seleccionado) | |
| `V42` | `● ● ●` | nodo (gris de su rama) | |
| `V43` | `●` | nodo en el camino al seleccionado | |
| `V44` | `◆` | raíz del mapa | |
| `V30` | `◆` | encabezado de la vista | |
| `V31` | `▽ 35 fuera de vista` | nodos fuera de vista | **deviation:** the proposal gave V7 *ramas plegadas fuera de vista*; the count the product paints is nodes, not branches, and V7 is retired |
| `V33` | `▾` | rama abierta | |
| `V34` | `▸` | rama plegada | |
| `V35` | `3` | campos pendientes bajo la rama | |
| `V21a` | `∙` | nodo con la ficha completa | **deviation:** the proposal split V21 into *con acta* / *sin acta*; the lattice lights a node when its ficha has no missing required field, which is more than an acta. `INC8-D-Q6` |
| `V21b` | `·` | nodo con campos pendientes | as above |
| `V36` | `█` | rama con todas sus actas | |
| `V37` | `▒` | rama con la mitad o más de sus actas | |
| `V38` | `░` | rama con menos de la mitad de sus actas | |
| `V39` | `╱` | rama sin datos | |
| `V32` | `▰ ▱` | medidor de avance | |
| `V19` | `█ █ ░` | nodos con y sin acta, en 10 celdas | **deviation:** the proposal was *cobertura de fichas (10 celdas)*; the bars the sala paints count nodes with and without an acta, and the coverage figure is the text beside them. `INC8-D-Q6` |
| `V20` | `▲ 2 vencen hoy` | actas que vencen hoy | |
| `V22` | `⊘` | mapa dañado — no se pudo leer | unchanged (Q7) |
| `V40` | `▁▂▃ ▅▇█` | actividad de los últimos 14 días | |
| `V41` | `↩ retomar` | volver a la última sesión | |

The D1 proposals for `V8`, `V9` and `V10` are not used, because D2 retired those rows.

### `D4` — layout and keyboard, decided and pinned

- **Width.** `LEGEND_PANEL_CELLS = 80` is the one panel width for both layouts.
  `LEGEND_ROW_CELLS = LEGEND_PANEL_CELLS - 2*_PAD_X - _SCROLLBAR_CELLS = 75`, derived rather than a
  literal. The `INC8-CR-F2` arm holds in both layouts
  (`test_d4_the_row_budget_is_the_painted_pane_width_in_both_layouts[100, 117, 118, 140]`).
- **Switch.** At `LEGEND_DOCK_MIN_WIDTH = 118` columns and wider, the legend screen takes the
  `-docked` class. It is aligned `right top` with a `0%` backdrop, so the view stays visible and
  undimmed on the left. Below 118 it is the centred modal over a 70% backdrop, as before. A resize
  moves an open legend between layouts.
- **Depth and chrome.** The panel sits on `PANEL` over the view's `GROUND`, one grey step, with no
  border. `ACCENT` appears only on key glyphs. Chrome copy is unchanged and lowercase, apart from
  §3.6's verbatim `SU` (A4). Readable text stays on `PANEL`, where `ACCENT` measures 5.11:1 (`#D28`,
  `test_d28_the_legend_chrome_clears_the_contrast_floor`, unchanged and green).
- **Height.** The docked panel keeps the modal's height rules. **`TC-R36`**
  (`test_repair_layout.py`, `LLR-R05`, a sealed prior batch) pins `max-height` as what governs at
  140×45. A full-height dock reddened it in this pass and was reverted, so it is `INC8-D-Q5`.
- **Keys (decision).** The panel is **modal for keys in both layouts**. A map key does nothing while
  the legend is open, a second `?` stacks nothing (`HLR-N16.3`), and `esc` / `q` close it. The
  scroll keys scroll it: `HLR-N16.4`'s arm runs at 140×45, now docked, and at 100×24, modal, and is
  green in both. Pinned by `test_d4_the_docked_panel_is_modal_for_keys`, which also asserts the
  trigger: the same key moves the bare view once the legend is closed.
- **Overlap — what is and is not claimed.** `test_d4_the_view_stays_visible_and_undimmed_beside_the_docked_panel`
  compares every cell left of the panel, glyph and style, before and after `?`. They are identical
  at 118. At 117 they must differ, and they do, because the backdrop dims them. That shows the arm
  can see a covered view. `test_d4_the_docked_panel_paints_nothing_over_the_visible_view` asserts
  that no legend widget reaches left of the panel's edge. **What is not claimed:** the view is not
  reflowed. At 118 columns the 80-column panel covers the map screen from column 38 on, which is 44
  of the canvas's 58 columns and the whole ficha inspector. That is `INC8-D-Q4`, measured below,
  and it is the operator's call.

### Findings (`INC8-D-Fn`)

- **`INC8-D-F1` — the verdict record itself fails the lane.**
  `VERDICT-inc8-legend-2026-09-28.md:23` (committed at `ca36a3f`, entry HEAD) carries a literal
  U+202E. The sentence meant to spell it as six escape characters and wrote the character instead.
  `test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts` is RED
  on the entry tree and on every commit of this pass. The byte was confirmed in `git show HEAD:`
  (line 23). The file is outside this pass's permitted docs and is the operator's authority record,
  so it is **not** fixed here. Routed to the coordinator. The fix is a one-character edit.
  This is the same defect class as `INC8-F5`, one document over.
- **`INC8-D-F2` — the legend-side style arm read the wrong rows once the panel moved.**
  `_harvest` read a scrolled widget's **unclipped** region. At the docked height `#help-vocabulary`
  scrolls to `y=-10`, and `strips[-10:16]` slices from the **end** of the frame. The old centred
  geometry happened to keep `y` non-negative. Fixed by clipping to the pane (`9136a3f`). `MH1`
  re-proves the arm after the fix: it goes RED on all four views.
- **`INC8-D-F3` — the catalogue's own first run measured a fade-in.** See the instrument section.
  Caught because impossible tones appeared, not by review.
- **`INC8-D-F4` — this pass's own view arm was blind to `V21b` on its first run.** `glyph_set`
  filtered samples through the exclusion rule, which drops `·` (punctuation). The arm went RED on
  soundness for `V21b` in three views. The instrument was fixed so that a sample with no meaningful
  character stands for its own characters. The product was not changed.
- **`INC8-D-F5` — a line-ending count lied, the trap control 37 names.** `grep -c $'\r$'` reported
  `01b` as all-CRLF. It is LF in the worktree. The splice briefly wrote CRLF into the new section;
  a byte count caught it before staging, and it was normalised.
- **`INC8-D-F6` — a second literal 118.** `LEGEND_DOCK_MIN_WIDTH = 118` reddened
  `test_crumb.py::test_decl_118_is_spelled_ONCE` in the first full lane. It was fixed in `40c5c6a`
  and the D4 mutants were re-fired on the fixed file (7 of 7 RED, pins OK). This is the tree's own
  census firing on this pass's work.

### Operator questions (`INC8-D-Qn`)

- **`INC8-D-Q1` — ALERT has a second job, and it is painted.** `01b` §3.5 says `ALERT`'s only job
  is the malformed-query chip. The atlas paints `◫ sin acta` in `ALERT` (`views/layered.py:613`),
  so `V26` declares it as painted. §3.5 was **not** widened and the renderer was **not** changed.
  Either §3.5 gains an `ALERT` row, or the card moves to another tone. That is a renderer change,
  which belongs to a later increment.
- **`INC8-D-Q2` — `V4` is retired, although `Q1·Q2` said V4 keeps `∙`.** The catalogue finds `∙`
  painted only as the rail's lit territory dot. That is `V21`'s form: a lit or unlit dot per node,
  in `MUT` / `WORDMARK`, which are exactly `V21`'s declared styles. So the `∙` survives in `V21a`
  and the id `V4` is retired. If the operator wants the id `V4` on that dot instead, `V21a` is
  renamed. It is one row in `01b` and one line in `darkside`.
- **`INC8-D-Q3` — §3.5's colour rows explain hues no view paints.** The catalogue found `SAGE`,
  `TEAL` and `VIOLET` painted **nowhere** in the four views, yet the legend still paints their three
  §3.5 rows. §3.5 was outside this rewrite (§3.1–§3.4), so it is unchanged.
- **`INC8-D-Q4` — the docked panel covers most of the map at 118 columns.** Measured, with the
  inspector shown: at 118×34 the rail is columns 0–23, the canvas 24–81 and the inspector 82–117.
  The panel spans 38–117, so it covers 44 of the canvas's 58 columns and all of the inspector. At
  140 it covers 44 of 80 canvas columns, and at 160 it covers 44 of 100. With the inspector shown,
  the covered part is always 80 − 36 = 44 columns (`%TEMP%\inc8d\probe_q4.py`). The round-10
  prototype's panel was 43 wide. Three options:
  - a narrower panel: the budget follows, and `LEGEND_ROW_CELLS` changes in both layouts;
  - reflowing the view beside the panel: this touches `MapScreen`'s region logic, whose
    auto-collapse is sticky;
  - accepting the overlay.
- **`INC8-D-Q5` — full-height docking is blocked by a sealed arm.** The prototype's panel is full
  height. `TC-R36` pins `max-height: 28` as governing at 140×45. Full height needs `TC-R36`
  amended, or a docked-only exemption ruled.
- **`INC8-D-Q6` — three labels depart from the D1 proposal because the painted form means
  something else:**
  - `V19` counts nodes with and without an acta; it is not coverage.
  - `V21a` / `V21b` mean a complete or incomplete ficha, not an acta.
  - `V31` counts nodes, not branches.

  See the copy table.
- **`INC8-D-Q7` — which 118 does D4 mean?** The threshold reads `darkside.DECLARED_CONTEXT_CELLS`,
  the batch's declared context of use (the width every render is drawn at). The other candidate is
  `MapScreen`'s auto-hide threshold (`MIN_CANVAS_WIDTH + RAIL_WIDTH + INSPECTOR_WIDTH`), which
  equals 118 by arithmetic, lives in `app.py`, and cannot be imported into `help.py` without a
  cycle. If the operator means the second, the difference shows only when one of those widths
  changes.
- **`A5`** (`en esta leyenda`) is still open, unchanged.

### Mutation table (this pass)

Harness `%TEMP%\inc8d\mutants.py`, outside the repo. Discipline:

- a sha256 pin per touched file;
- a byte-level replace in the file's own line endings, with each `old` occurring exactly once;
- stdout and stderr captured separately, and the summary line asserted as found;
- the verdict printed **before** the restore;
- a byte restore, and the pin re-verified.

All 19 restores matched their pins, and `git status --porcelain` showed 0 lines afterwards. Pins
before the battery:

- `mapper/darkside.py` `64ab8d0d74930c51595416b5198e67c30315591a9c1e45c2203806fe1666d048`
- `mapper/screens/help.py` `ee549666c83be63129e3a47d67d5a29bd4cf5d0b78d3068b2ce73f525a1c72ed`
- `mapper/app.py` `8bf4b8407e1d9b08eab1c68f39fea473e6fdf829c7321db3cda2f0c0169cb1ce`
- `mapper/views/layered.py` `0d1ac59d031fb5766b81d389e39ad95e13d6ca8c20584d7eb8432deb38d7a60c`
- `mapper/views/radial.py` `df3512af876b9ff4ac2be130e77cbdb65a30a28eb16570590f01723ccf00e920`
- `tests/test_legend_design.py` `925281a994b992a8bb75ee7a599315db287bcfda5f16a83f122ff4f703e37bbb`
- `01b-ux-decisions.md` `1ed8029eedaaea99df469a820c337b490f3c994294cc9e0c79f4533538c65dce`

| # | Mutant | Verdict |
|---|---|---|
| MD1 | `◫ sin acta` painted `INK`, not `ALERT` (`layered.py`) | **RED** D2`[atlas]`, SOUNDNESS: `V26` |
| MD2 | the sparkline never reaches its `MUT` tier (`app.py`) | **RED** D2`[sala]`, SOUNDNESS: `V40`/`MUT` |
| MD3 | the fold pill paints `►` (`layered.py`) | **RED** D2`[atlas]`, COMPLETENESS: `U+25BA`; soundness empty |
| MD4 | radial's header paints `◆◇` (`radial.py`) | **RED** D2`[mapa mental]`, COMPLETENESS: `U+25C7` |
| MD5 | `V37` dropped from `01b` **and** the declaration together | **RED** only D2`[atlas]` (COMPLETENESS: `▒`); EQUALS and the partition arm stay **GREEN**. This is the gap the view arm closes |
| MD6 | the exclusion rule drops every symbol (`S*`) | **RED** `test_d2_the_exclusion_rule_keeps_…` |
| MV1 | retired `V5` comes back as a table row | **RED** `test_design_pass_a_retired_id_is_never_a_row_again` |
| MV2 | `V13` loses its `#D7` marker | **RED** `test_design_pass_q4_…` |
| MV3 | braille back in the atlas's Views cell | **RED** `test_hlr_n16_2_each_view_paints_the_rows_its_01b_views_column_names` |
| MV4 | `V4b`'s braille range dropped from `darkside` | **RED** `test_every_declared_range_EQUALS_the_document` |
| MV5 | `legend_view` returns `radial` again | **RED** `…names_the_map_view[mapa mental]` |
| MH1 | the legend paints every sample `INK` (after `INC8-D-F2`) | **RED** `…every_member_is_painted…[atlas, esquema, mapa mental, sala]` |
| M4a | dock threshold off by one (`>`) | **RED** `switches[118]`, `view_stays_visible[118]` |
| M4b | docked backdrop `70%` (dims the view) | **RED** `view_stays_visible[118]`; `[117]` GREEN |
| M4c | docked panel centred | **RED** `…paints_nothing_over_the_visible_view` |
| M4d | a `key_l` on the legend forwards to the view | **RED** `…is_modal_for_keys` |
| M4e | a `key_question_mark` pushes a second legend | **RED** `…is_modal_for_keys` |
| M4f | row budget one cell short of the pane | **RED** `…row_budget…[100, 117, 118, 140]` |
| M4g | `on_resize` ignored | **RED** `…a_resize_moves_the_open_legend_between_layouts` |

**The pre/post pair (control: fire the same mutant against both oracles).** The pre-increment tree
`ca36a3f` was exported with `git archive` to `%TEMP%\inc8d\base_ca36a3f`. Its `mapper` import
resolves to the export, not the repo's editable install. That was checked by path, and by base's
title arm passing on `outline`, which only base's `app.py` returns. MD1 and MD3 were fired there
against base's legend oracles (`test_help_scope.py`, `test_vocabulary_declaration.py`,
`test_repair_layout.py`, 51 nodes). **Both SURVIVED: 51 passed each.** Post-increment, both go
**RED**. The view-side sight is new with this pass.

### Lane and ruff

- **First full-lane run**, once, main tree, at `9136a3f` (before the threshold fix), with stdout and
  stderr kept separate: **`2 failed, 1225 passed, 20 deselected, 3 xfailed`** in 428 s. This is a
  faithful record of that tree, so it is annotated, not struck.
  - `test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts` is
    **`INC8-D-F1`**, which was already present at entry.
  - `test_crumb.py::test_decl_118_is_spelled_ONCE` was **mine** (`INC8-D-F6`).
    `LEGEND_DOCK_MIN_WIDTH = 118` was a second literal of a number the package spells once. Fixed
    in `40c5c6a` by reading `darkside.DECLARED_CONTEXT_CELLS`. The lane caught it; care did not.
  - `FLAKE-1` did not fire.
- **Reconciliation.** 1206 at entry, plus 21 new nodes, gives 1227, and 1225 + 2 = 1227 ✓. The 21:
  - `test_vocabulary_declaration.py` +2: the retired-id arm and the `Q4` arm. The other changes
    there were renames.
  - `test_help_scope.py` +2: the member-style arm now runs over four views instead of two.
  - `test_legend_design.py` +17, a new file: D2 ×4, the rule arm, the switch ×3, visible ×2,
    overlap, keys, the budget ×4, and resize.
- **Final full-lane run**, on the final tree with the docs in place: **`1 failed, 1226 passed, 20 deselected, 3 xfailed`** in 573 s at `40c5c6a`, with this record and `A-106` in the tree. The one failure is `INC8-D-F1`, and 1226 + 1 = 1227 ✓. `FLAKE-1` did not fire. This run is a
  deviation from "once", and it is declared: the first run's tree was not the final one, and a lane
  figure for a tree that did not ship is weaker than one for the tree that did.
- **ruff** (`--output-format=concise --no-cache`, line and column dropped, paths normalised; the
  instrument is `%TEMP%\inc8d\ruffset.py`):
  - entry `ca36a3f`: **27** errors; exit: **27**; the sets are identical;
  - the four touched Python files are clean.
  - The export of `ca36a3f` reports 45, because an export has no `.git`, so ruff stops honouring
    `.gitignore` and counts `prototypes/`. Compared like for like, excluding `prototypes/`, both
    are 27.

### Render — real `run_test` + `export_screenshot`, with PNGs rasterised from them

`C:\Users\jjgh8\AppData\Local\Temp\inc8d\render\`. Every file exists as `.svg` and `.png`.
`_top` / `_vocab` / `_end` are the legend's top, its vocabulary section and its end. The legend was
opened through the real `?`.

- **118×34, docked, with the view beside it:**
  - `atlas_118x34_view`, `atlas_118x34_legend_top`, `_legend_vocab`, `_legend_end`
  - `esquema_118x34_view`, `esquema_118x34_legend_top`, `_legend_vocab`, `_legend_end`
  - `mapa-mental_118x34_view`, `mapa-mental_118x34_legend_top`, `_legend_vocab`, `_legend_end`
  - `sala_118x34_view`, `sala_118x34_legend_top`, `_legend_vocab`, `_legend_end`
- **80×24, modal:** `atlas_80x24_legend_{top,vocab,end}`, `esquema_…`, `mapa-mental_…`,
  `sala_…`.

### Carries

- **Inc-9: rename the other screens' own headers** to `atlas` / `esquema` / `mapa mental` / `sala`.
  The canvas headers still read `mapa de conceptos` / `outline` / `mapa mental` (`views/*.py`),
  and the keymap's seat labels still read `alternar outline` / `alternar radial`. Verdict `D5` routes
  these to Inc-9. The legend's own title is done.
- **`INC8-D-F1`**: fix the literal U+202E in the verdict record. Coordinator.
- **The diff mode's tones** (`▐` `ACCENT`, the `WARN` chip, `ALERT` ghosts, `ACCENT` wires) are in
  neither the catalogue nor the arm, because a git history is needed to drive them.
- **Per-style completeness** (see the instrument's blind spots).
- `INC8-D-Q1`–`INC8-D-Q7` and `A5` go to the operator.
- The earlier carries are unchanged: `INC8-F1`, `INC8-F3`, `UX-F9`, `UX-F12`, B-69 and B-70.
  This pass closes `INC8-F2` and `UX-F3`.

### Files

| Source (3 of 4 permitted) | Tests | Docs |
|---|---|---|
| `mapper/darkside.py` | `tests/test_vocabulary_declaration.py` | `01b-ux-decisions.md` (DECISION 3 §3.1–§3.4 rewritten, with its change log) |
| `mapper/screens/help.py` | `tests/test_help_scope.py` | `01-requirements.md` (`A-106` appended) |
| `mapper/app.py` (`legend_view` only) | `tests/test_legend_design.py` (new) | this record |

`keymap.py` was not needed. No renderer under `mapper/views/` was changed; the mutants touched them
only temporarily, and every file was restored and verified against its pin. `.dev-flow/state.json`,
`prototypes/`, `mapper.db`, `basewt` and the backup branch were not touched. Nothing was pushed.

### Commits (this pass)

- `7e1c2e2` feat(legend): the vocabulary derived from what the product paints — `01b`, the
  declaration, names, and test updates
- `efbb9ac` test(legend): the legend and the view agree in both directions
- `9136a3f` feat(legend): the legend docks beside the view at ≥ 118 columns, including `INC8-D-F2`
- `40c5c6a` fix(legend): the dock threshold reads the declared context of use (`INC8-D-F6`)
- this record and `A-106` (docs)

## Design pass 2 (2026-09-29)

**What this pass is.** The operator's second design verdict and language ruling
(`VERDICT-inc8-legend-2026-09-28.md`, sections *Round 2* and *LANGUAGE RULING*), plus the findings
the final reviews of `4ae3091` carried in (`state.json` → `p3_progress.INC-8_ROUND_2_2026-09-29`),
applied under the batch's `/dev-flow` rules. Entry HEAD `4b40587`, tree clean. Independent reviews
follow; this record does not review its own work.

### Verdict items and findings applied

| Item | What was done | Commit | Arm(s) |
|---|---|---|---|
| **Language ruling** | Every string the legend paints is English: vocabulary and colour labels, §3.6 headers and footer, the group title, the title and close hint, the view names. `01b` §3.1–§3.6 rewritten, with a pass-2 change log above §3.1. Samples keep what the renderers paint (see `INC8-D2-Q3`) | `9d51593` | EQUALS, FAITHFUL, the §3.6 arms, the title arms |
| **View names** (`D5` in English) | `atlas` / `outline` / `mind map` / `home`, behind ONE constant, `darkside.VIEW_NAMES` (assumption **`A6`**, `INC8-D2-Q1`). `legend_view` and `LEGEND_VIEWS` read it. Other screens' headers untouched (Inc-9) | `9d51593` | `test_hlr_n16_2_each_view_paints_…` (pins the `01b` Views column to `VIEW_NAMES`) |
| **E1** narrow docked panel | 44 columns, full height, flush right at ≥ 118; the modal stays 80 × ≤ 28. Two row budgets, each derived (`_row_cells`) and each pinned against the painted pane in its own layout. The vocabulary section first in both layouts. Keys stay modal while docked (pinned, unchanged). A resize re-budgets the painted rows | `9fbc6a8`, `a4dcdd2` | switches ×3, budget ×4, resize, `test_e1_the_docked_panel_covers_the_inspector_whole_and_little_canvas` ×2, `test_e1_the_vocabulary_section_is_painted_first` ×2, `test_e1_no_painted_string_is_cut_at_either_budget` ×2, `TC-R36` ×3 |
| **A-107** | `TC-R36`'s cap: the DOCKED layout is exempt (full height); the modal keeps it, re-measured at 100×45 | `9fbc6a8` | `test_tc_r36_…[cap-governs, percentage-governs, docked-full-height]` |
| **E2** | Every sample cell painted on `GROUND` (a member declaring its own ground keeps it); the label stays on `PANEL` | `29781d6` | `test_llr_n16_2_1_every_member_is_painted_in_its_declared_style` ×4 now checks the ground |
| **E3** | Group titled `in this legend`, two lines: `esc q close · ↑ ↓ line` / `pageup pagedown page · home end ends`. Words are legend copy per action (`help.OWN_SCOPE_COPY`), glyphs from the seat. The close hint uses the same word | `9fbc6a8` | `test_hlr_n16_4_…` ×2 (all 8 keys), `test_e3_the_title_hint_and_own_scope_copy_EQUAL_section_3_6` |
| **E4** | §3.5 derived from what is painted. `SAGE`, `TEAL`, `VIOLET` leave; `ALERT` joins with its second job, `red — missing record`. `DECLARED_COLOURS` re-derived | `9d51593`, `29781d6` | `test_e4_the_colour_rows_are_the_hues_the_views_paint` (both directions), §3.5 EQUALS |
| **E6** | `V19`, `V21a/b`, `V31` keep their corrected meanings; `V35` = `pending fields here and below`; `V27`'s sample is `D✓`, `field initial · ✓ filled` | `9d51593` | EQUALS, the rule arm |
| `INC8-F-CR-F1` | Own keys read with the pane at rest AND at its end equal every own key painted | `9fbc6a8` | `test_e3_the_own_keys_are_visible_at_rest_and_at_the_end` ×2 |
| `INC8-F-CR-F2` | `X2` = ASCII punctuation + the separators found (`·` `…` `—`); `•` and `‹` must be meaningful | `29781d6` | the rule arm; D2 |
| `INC8-F-CR-F3` | `V29` owns exactly the eleven wires of `canvas._GLYPH` (`01b` "glyph set" notation) | `29781d6` | `test_inc8_f_cr_f3_V29_owns_exactly_the_wires_the_canvas_paints`, `test_every_declared_range_EQUALS_the_document` |
| `INC8-F-CR-F4` | Completeness per (glyph, style); one overlay allow-list `OVERLAY_STYLES` (`V23`, `V24`, the rail cursor's `INK on STEP`) | `29781d6` | D2 ×8 |
| `INC8-F-CR-F5` | D2 parametrized on `sorted(LEGEND_VIEWS)` × both sizes; `<= 28` → `LEGEND_MODAL_MAX_ROWS`; `- 5` removed (the pane measurement is the pin) | `9d51593`, `9fbc6a8` | D2, budget |
| `INC8-F-CR-F6` | ONE state table in the test module; the catalogue imports it and the rule; deep outline fixture; harvest advances by `cell_len` | `29781d6`, `27be355` | D2, `test_cr_f6_the_harvest_advances_by_cell_width` |
| `INC8-F-CR-F7` | The glyph-rule docstring's examples are current | `29781d6` | — (prose) |
| `INC8-F-SEC-F1` | `_STYLE_MODIFIERS = frozenset({"bold", "on"})` is the allow-list; `_declared_modifiers()` must sit inside it; a declared `link file:///x` row raises at `resolve_style`, so no `Text` is returned | `29781d6` | `test_inc8_f_sec_f1_the_style_allow_list_does_not_authorize_itself` |
| `INC8-F-SEC-F2` | Option **(a)**: callers size `fit` by `darkside.shown_cells` (the width after `fit`'s own coercion). `fit`'s contract stays exact; the defect was the caller measuring a different string than the one painted | `4b7c2ba` | `test_inc8_f_sec_f2_an_invisible_only_part_is_not_painted_empty` |
| `INC8-F-UX-F4` | Row `V45` `⇲15`, `MUT`, outline only; a 26-level fixture | `29781d6` | D2 `[outline-*]`, EQUALS |
| `INC8-F-UX-F6/F7` | Covered by E6 | `9d51593` | — |

### The English copy — every string the legend paints, in one place

For the operator to correct in one pass. "Was" is the Spanish it replaces. A **sample** is what the
view paints and is not copy (see `INC8-D2-Q3`).

**Framing (`01b` §3.6, `help.py`)**

| Where | English | Was |
|---|---|---|
| Title | `legend · <view>` | `leyenda · <view>` |
| Close hint (top right) | `esc close` (glyph from the seat) | `esc cerrar` (seat label) |
| Own-scope group title | `in this legend` | `en esta leyenda` |
| Own-scope words | `close` (esc, q) · `line` (↑, ↓) · `page` (pageup, pagedown) · `ends` (home, end) | seat labels `cerrar`, `subir`/`bajar`, `página arriba/abajo`, `al principio/al final` |
| Section 1 | `what this view paints` | `vocabulario de esta vista` |
| Section 2 | `colours with a job` | `colores con empleo` |
| Section 3 | `keys in this view` | `teclas de esta vista` |
| Footer | `each view has its own legend —` / `same key, this view's content` | `cada vista tiene SU leyenda — ` / `misma tecla, contenido de la vista` |
| Reserved chord (not painted) | `??` `opens the full field guide` | `abre la guía de campo completa` |

**View names (`darkside.VIEW_NAMES`, `A6`)**: `atlas` · `outline` (was `esquema`) · `mind map` (was
`mapa mental`) · `home` (was `sala`).

**Colours (`01b` §3.5)**: `blue — where you can act` (`ACCENT`), `amber — attention / due` (`WARN`),
`red — missing record` (`ALERT`, new).

**Vocabulary (`01b` §3.1–§3.4)**

| Row | Sample | English label | Was |
|---|---|---|---|
| `V1` | `▐` | map node | nodo del mapa |
| `V2` | `▐ nómina` | search match | coincidencia de búsqueda |
| `V23` | `▐ erp` | selected node | nodo seleccionado |
| `V24` | `▐ erp` | selected, focus elsewhere | seleccionado, con el foco en otra región |
| `V3` | `▐ ▸ inv +23` | folded branch, 23 inside | rama plegada (23 dentro) |
| `V25` | `◫ ACTA-7` | the node's record | acta del nodo |
| `V26` | `◫ sin acta` | missing record | nodo sin acta |
| `V27` | `D✓` | field initial · ✓ filled | campo del esquema lleno (sample `✓`) |
| `V28` | `░` | field still pending | campo del esquema pendiente |
| `V29` | `┬─┐` | link between nodes | enlace entre nodos |
| `V4b` | `⣉⡉⠉` ×4 tones | link; blue: path to selected | enlace entre nodos (en azul, camino al seleccionado) |
| `V42` | `● ● ●` | node, in its branch's grey | nodo (gris de su rama) |
| `V43` | `●` | node on the selected path | nodo en el camino al seleccionado |
| `V44` | `◆` | map root | raíz del mapa |
| `V30` | `◆` | view header | encabezado de la vista |
| `V31` | `▽ 35 fuera de vista` | nodes off screen | nodos fuera de vista |
| `V45` | `⇲15` | true depth, indent capped | (new) |
| `V33` | `▾` | open branch | rama abierta |
| `V34` | `▸` | folded branch | rama plegada |
| `V35` | `3` | pending fields here and below | campos pendientes bajo la rama |
| `V21a` | `∙` | node with a complete card | nodo con la ficha completa |
| `V21b` | `·` | node with pending fields | nodo con campos pendientes |
| `V36` | `█` | branch with all its records | rama con todas sus actas |
| `V37` | `▒` | branch: half or more records | rama con la mitad o más de sus actas |
| `V38` | `░` | branch: under half records | rama con menos de la mitad de sus actas |
| `V39` | `╱` | branch with no data | rama sin datos |
| `V32` | `▰ ▱` | progress meter | medidor de avance |
| `V19` | `█ █ ░` | record / no record, 10 cells | nodos con y sin acta, en 10 celdas |
| `V20` | `▲ 2 vencen hoy` | records due today | actas que vencen hoy |
| `V22` | `⊘` | damaged map — unreadable | mapa dañado — no se pudo leer |
| `V40` | `▁▂▃ ▅▇█` | activity, last 14 days | actividad de los últimos 14 días |
| `V41` | `↩ retomar` | back to your last session | volver a la última sesión |

Terms used consistently: *acta* → **record**, *ficha* → **card**. The deferred lens rows (`V11`–`V16`,
`V18`) were translated in `01b` too, and are painted by no legend.

### §3.5 — derived from what is painted, and its change log

The rule, written once (`tests/test_legend_design.py::has_a_job`): a painted colour has a job when it
is a hue (`r`, `g`, `b` not all equal). The greys (the surfaces and the text ramp) explain nothing.
The census reads every harvested cell's fg and bg outside `X3`/`X5`, over the same states as D2.

Catalogue colour census (both sizes, all states; cells):

| view | ACCENT | WARN | ALERT | SAGE | TEAL | VIOLET | PULSE |
|---|---|---|---|---|---|---|---|
| atlas | 730 | 405 | 90 | 0 | 0 | 0 | 0 |
| outline | 1362 | 2707 | 0 | 0 | 0 | 0 | 0 |
| mind map | 1296 | 393 | 0 | 0 | 0 | 0 | 0 |
| home | 34 | 90 | 0 | 0 | 0 | 0 | 0 |

**Change log** (also in `01b` §3.5): `SAGE`, `TEAL` and `VIOLET` leave the table, painted by no view
(closes `INC8-D-Q3`). `ALERT` joins with its second job, the missing-record mark `◫ sin acta` and the
inspector's `sin acta` (closes `INC8-D-Q1`). Its first job, DECISION 2's malformed-query chip, is
unchanged; that chip belongs to the deferred lens and no view here paints it (`INC8-D2-Q6`).

### E1 — geometry, measured

| | modal (< 118) | docked (≥ 118) |
|---|---|---|
| panel width | 80 (`LEGEND_PANEL_CELLS`) | 44 (`LEGEND_DOCKED_CELLS`) |
| panel height | `90%`, capped at 28 (`TC-R36`) | 100% — 34 at 118×34, 45 at 140×45 (`A-107`) |
| row budget (`_row_cells`) | 75 | 39 |
| vocabulary label budget (row − indent 2 − sample 8) | 65 | 29 |
| key label budget (row − 2 − 10) | 63 | 27 (longest seat label: 22) |
| colour label budget (row − 2 − 3) | 70 | 34 |

- **Sample column 8** (was 12), so `V35`'s ruled label (29 cells) fits the docked budget on one row. A
  sample of 8 cells or more takes its own line, as before. No label was shortened below its ruled
  wording; the arm that pins "nothing is cut" is `test_e1_no_painted_string_is_cut_at_either_budget`.
- **Canvas visible beside the docked panel** (composited frame, `render.py` → `measures.json`):
  **50 of 58** columns at 118×34 (was 14 of 58 with the 80-column panel), **72 of 80** at 140×45.
- **No "L" (`UX-F9`)**: the inspector (x 82–117 at 118; 104–139 at 140) lies wholly inside the panel,
  full height, at both sizes. Pinned by the E1 arm.
- **Radial nodes**: **31 of 31** `●` stay visible beside the docked panel at 118×34 (was **0 of 31**),
  and 39 of 39 at 140×45. The 80×24 modal still covers them (0 of 31), as a modal does.
- **Keys stay modal while docked**: `test_d4_the_docked_panel_is_modal_for_keys`, unchanged and green.

### `A-107`

Appended to `01-requirements.md` (Amendment set 15). `TC-R36` (repair batch, `LLR-R05`) pinned
`max-height: 28` at 140×45. The docked layout is exempt and runs full height; the modal keeps the cap,
re-measured at 100×45; the sealed arm gains `docked-full-height`. Nothing is loosened: the modal bound
is the same number, and the docked bound is an exact equality. `A-107` was the next free id after a
scan of all of `.dev-flow` (no `A-107` anywhere; `A-106` was the last).

### The catalogue instrument (pass 2)

`C:\Users\jjgh8\AppData\Local\Temp\inc8d\catalogue.py`, outside the repo; the pass-1 script is kept
beside it as `catalogue_pass1.py` (sha256 `616b8edc…`). Re-run from the repo root:

```
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python %TEMP%/inc8d/catalogue.py --md --colours
```

- **It re-states nothing** (`INC8-F-CR-F6`). It imports `SIZES`, `MAP_STATES`, `drive_map`,
  `drive_home`, `meaningful`, `_excluded_widget`, `OVERLAY_STYLES`, `glyph_set`, `_paints_as` and
  `has_a_job` from `tests/test_legend_design.py`. It adds only counting and widget names.
- **States** (the D2 arm drives the same ones): every map view × {legacy, concept} × {rest, walked,
  folded, folded-walk, search `fin`, rail-focus, unfocused-selection, folded-root}, plus a 26-level
  deep outline; the home screen with a legacy map, a concept map, a cyclic `roto.mmd` and a recorded
  session; at 118×34 and 140×45; each state in a fresh app.
- **Result**: 1292 rows, **0 UNEXPLAINED**. `⇲` painted 17 times, all `= V45`. Depth-mark levels
  measured (`probe_depth.py`): 15–25 at 118×34 (26 is below the fold), 21–26 at 140×45.
- Output: `C:\Users\jjgh8\AppData\Local\Temp\inc8d2\catalogue.md` and `catalogue.json`.

### Findings (`INC8-D2-Fn`)

- **`INC8-D2-F1` — the title hint overflowed by one cell.** A close-key glyph as wide as the row left
  `word_cells` at 0, and the space before the word was painted anyway: 76 cells in a 75-cell row. It
  was latent in the pass-1 code too. The pass-1 SEC-F3 arm widened only the label, which cannot reach
  it. Found when that arm was widened to the glyph (the title's word is legend copy now). Fixed
  (`9fbc6a8`); mutant `MA10` pins it.
- **`INC8-D2-F2` — the same family, one caller over, outside this boundary.** `app.py:2625` (the
  map toast) sizes `fit(detail, min(room, len(detail)))` by code points. It never blanks, since
  `len` ≥ 1, but it cuts a wide-glyph string early. Not in `legend_view`, so not touched. Carry.
- **`INC8-D2-F3` — the tool converted `\u` escapes into literal characters, twice in this pass.**
  First the SEC-F2 arm (`test_help_scope.py`: three U+202E, one U+200B, two U+FFFD), then the CR-F6
  arm (`test_legend_design.py`: `漢`, `▲`). The staged-diff byte scan caught the first before the
  commit; the second was caught by reading the file. Both were restored byte-level. **0 banned
  code points** in every staged diff and every commit message of this pass, scanned before and after
  each commit (`inc8d2\scan.py`).
- **`INC8-D2-F4` — the cell-width fix was unpinned.** No view paints a wide glyph, so reverting
  `cell_len` in `harvest` survived D2. Seen while planning the battery; the arm
  `test_cr_f6_the_harvest_advances_by_cell_width` was added (`27be355`), and `MH6` is RED on it.
- **`INC8-D2-F5` — the narrow-panel arm was tautological.** Mutant `MA1` (panel 44 → 80) **SURVIVED
  every arm**: the canvas bound was written against `LEGEND_DOCKED_CELLS` itself. The arm now holds
  the verdict's own number (`VERDICT_E1_PANEL_CELLS = 44`, ±1) (`a4dcdd2`). `MA1` re-fired: RED at
  both sizes.
- **`INC8-D2-F6` — the resize arm broke a sealed census.** The first full lane went **2 failed**,
  both in `tests/test_a3_census.py`. It pins the tree's zero-argument `.render()` call sites at 35,
  and the resize arm had added a 36th by asking `#help-footer` what it held. Moving a pin in a file
  outside this increment was not the fix. The arm now reads the composited frame instead: the title
  row is right-aligned to the budget, so the close hint's last cell shows which budget the painted
  rows were built for (`5d45c93`). The census is green again. `MA9` and `M4g` were re-fired against
  the rewritten arm: both RED, pins OK. This is the tree's own census firing on this pass's work, as
  `INC8-D-F6` did in pass 1.
- **Cost, stated.** D2 now drives 16–17 states per (view, size): 26–38 s per node, ~4 min for its
  8 nodes, against a 120 s per-test ceiling.

### Operator questions (`INC8-D2-Qn`)

- **`INC8-D2-Q1` — the view names (assumption `A6`).** `atlas` / `outline` / `mind map` / `home`. A
  correction is one line in `darkside.VIEW_NAMES` plus the `01b` Views column; the partition arm
  forces the two to agree.
- **`INC8-D2-Q2` — the English copy.** Any row of the table above to reword.
- **`INC8-D2-Q3` — samples keep what the renderers paint.** `◫ sin acta`, `▽ 35 fuera de vista`,
  `▲ 2 vencen hoy` and `↩ retomar` are Spanish because the views paint them in Spanish; translating
  the sample alone would misdescribe the view until `Inc-EN` (`B-71`). The example titles `nómina`,
  `erp` and `inv` are data, not renderer copy, and could switch to English now. Kept as-is.
- **`INC8-D2-Q4` — "two lines" for the own-scope group (`E3`).** Read as two KEY lines under the group
  title, so three rows with the title. Folding the title into the lines does not fit: the second line
  is 36 of 39 docked cells.
- **`INC8-D2-Q5` — section order.** `E1` ruled "vocabulary first". The colours follow the vocabulary
  because they explain its hues, and the keys come last: `vocabulary · colours · keys`. The
  alternative is `vocabulary · keys · colours`.
- **`INC8-D2-Q6` — `ALERT`'s row names only the job the views paint** (`missing record`). DECISION
  2's malformed-query chip, `ALERT`'s first job, is painted by none of these views.
- **`INC8-D2-Q7` — `V28`** keeps the bare `░` with `field still pending`. The alternative mirrors
  `V27` as `D░` / `field initial · ░ pending`.
- Still open from pass 1: `INC8-D-Q7` (which 118). `INC8-D-Q1`, `-Q3`, `-Q4`, `-Q5`, `-Q6` and `A5`
  are closed by `E4`, `E1`/`A-107`, `E6` and `E3`.

### Mutation table (this pass)

Harness `C:\Users\jjgh8\AppData\Local\Temp\inc8d2\mutants.py`, outside the repo, with the pass-1
discipline:

- a sha256 pin per touched file;
- a byte-level replace in the file's own line endings, each `old` occurring exactly once;
- stdout and stderr kept separate, and the summary line asserted as found;
- the verdict printed **before** the restore;
- a byte restore, and the pin re-verified.

**36 of 36 restores matched their pins**, and `sha256sum -c` against `pins_before.txt` passed for
all 11 pinned files afterwards. `layered.py`'s pin `0d1ac59d…` equals pass 1's, so the renderer is
untouched.

| # | Mutant | Verdict |
|---|---|---|
| MA0 | dock threshold `>` | **RED** switches[118], visible[118] |
| MA1 | docked panel 80 wide | **SURVIVED** first run (`INC8-D2-F5`) → arm fixed → **RED** inspector arm ×2 |
| MA2 | docked panel keeps the modal cap | **RED** `TC-R36[docked-full-height]`, switches[118,140], inspector ×2 |
| MA3 | keys painted before the vocabulary | **RED** order ×2 |
| MA4 | own-scope group into the pane, top | **RED** at-rest-and-end ×2 (at the end) |
| MA5 | own-scope group into the pane, end | **RED** at-rest-and-end ×2 (at rest) |
| MA6 | `home`/`end` lose their word | **RED** `HLR-N16.4` ×2, §3.6 E3 arm |
| MA7 | samples on `PANEL` (E2 undone) | **RED** member-style arm ×4 |
| MA8 | sample column 12 | **RED** no-cut[docked]; [modal] GREEN |
| MA9 | a resize does not repaint | **RED** resize (re-fired after `INC8-D2-F6`: RED) |
| MA10 | the hint's space painted with no word (`INC8-D2-F1`) | **RED** SEC-F3 ×2 |
| MA11 | the MODAL loses its cap (40) | **RED** `TC-R36[cap-governs]` only |
| M4b | docked backdrop 70% | **RED** visible[118] |
| M4c | docked panel centred | **RED** nothing-over, switches |
| M4d | a map key reaches the view | **RED** modal-for-keys |
| M4e | a second `?` stacks | **RED** modal-for-keys |
| M4f | row budget one short | **RED** budget ×4 |
| M4g | `on_resize` ignored | **RED** resize (re-fired after `INC8-D2-F6`: RED) |
| MC1 | `ALERT` row dropped from `01b` AND the declaration | **RED** E4 only; §3.5 EQUALS **GREEN**, the gap the E4 arm closes |
| MC2 | a `VIOLET` row no view paints | **RED** E4 |
| MF4 | `◫` in a new tone (`WARN`) beside `INK`/`ALERT` (`layered.py`) | **RED** D2[atlas-118x34] |
| MF2 | a new `•` mark (`outline.py`) | **RED** D2[outline-118x34] |
| MF2b | `X2` back to every `P*` | **RED** rule arm |
| MF3 | `╳` at a crossing (`canvas.py`) | **RED** D2[atlas-118x34], V29 arm |
| MS1 | the allow-list authorizes itself again | **RED** SEC-F1 arm |
| MS2 | crumb tail sized by the raw string | **RED** SEC-F2 arm |
| MS3 | legend sample sized by the raw string | **RED** SEC-F2 arm |
| MU4 | `V45` dropped from `01b`, the declaration and the partition | **RED** D2[outline] ×2 only; EQUALS and partition **GREEN** |
| MV27 | `V27`'s sample back to `✓` | **RED** EQUALS, rule-by-row |
| ML1 | title word `leyenda` | **RED** §3.6 E3 arm |
| ML2 | `mind map` → `mapa mental` | **RED** partition arm |
| MP5 | a view declared with no state | **RED** D2[relief-118x34], partition |
| MH6 | harvest advances per character | **RED** CR-F6 arm |
| ME3 | `01b`'s own-scope word drifts | **RED** §3.6 E3 arm |

**The pre/post pair.** The commit-1 tree `9d51593` (English copy, before the per-style and
narrowed-`X2` rule) was exported with `git archive` to `inc8d2\base_9d51593`. Its `mapper` import
resolves to the export, checked by path. MF4 and MF2 were fired there against its own D2 arm, and
**both SURVIVED** (1 passed each). On the final tree both are **RED**. The per-(glyph, style) and `•`
sight is new with this pass.

### Lane and ruff

- **First full-lane run**, once, main tree, at `a4dcdd2` with this record drafted in the tree,
  stdout and stderr kept separate: **`2 failed, 1245 passed, 20 deselected, 3 xfailed`** in 691 s.
  Both failures are **`INC8-D2-F6`** (`test_a3_census.py`, mine), fixed in `5d45c93`. This is a
  faithful record of that tree, so it is annotated, not struck. `FLAKE-1` did not fire.
- **Final full-lane run** on the final tree (`5d45c93`, with this record and the `01b` `:264`
  citation in the working tree): **`1247 passed, 20 deselected, 3 xfailed, 0 failed`** in 641 s.
  `FLAKE-1` did not fire. Running the lane twice is a deviation from "once", and it is declared: the
  first run's tree was not the one that ships.
- **Reconciliation.** 1227 at the reviewers' baseline (`4ae3091`, the same tests as entry `4b40587`),
  plus **20** new nodes, gives 1247 ✓, and 1245 + 2 = 1247 ✓ for the first run. The 20, by node, are
  from `--collect-only` diffed between an export of `4b40587` and the tree:
  - `test_help_scope.py` **+9**:
    - no-cut ×2, section order ×2, own keys at rest and at the end ×2;
    - SEC-F1 +1, SEC-F2 +1;
    - SEC-F3 is now ×2 (modal, docked), replacing the ×1 label version.
  - `test_legend_design.py` **+8**: D2 4 → 8 (× two sizes), E4 +1, the inspector arm ×2, the
    harvest arm +1.
  - `test_vocabulary_declaration.py` **+2**: the §3.6 E3 arm and the V29 arm.
  - `test_repair_layout.py` **+1**: `TC-R36[docked-full-height]` (`A-107`); the other two ids are
    unchanged.
  - Nothing else changed. The export collected 0 nodes of `test_views_hits.py` (57 in the repo
    tree). That is an artifact of the export, which has no `.git` and no `prototypes/`, not a
    difference in the product. Counted with those 57 nodes, the export equals the repo's entry
    count.

- **ruff** (`inc8d\ruffset.py`, line and column dropped, paths normalised): entry **27**, exit **27**,
  and the **sets are identical**. The capture at `40c5c6a` is the entry baseline, since no `.py`
  changed between `40c5c6a` and `4b40587`.

### Render — real `run_test` + `export_screenshot`, PNGs rasterised by headless Chrome

`C:\Users\jjgh8\AppData\Local\Temp\inc8d2\render\`: 40 SVGs and 40 PNGs, plus `measures.json`.
`render.py` writes them; `rasterise_chrome.py` rasterises them. Each legend was opened through the
real `?`. `_legend_top` is at rest, `_legend_keys` is scrolled to the keys section, and
`_legend_end` is the end.

- **Plain views, 118×34:** `atlas_118x34_view`, `outline_118x34_view`, `mind-map_118x34_view`,
  `home_118x34_view`.
- **Docked, 118×34 and 140×45:** `{atlas,outline,mind-map,home}_{118x34,140x45}_legend_{top,keys,end}`.
- **Modal, 80×24:** `{atlas,outline,mind-map,home}_80x24_legend_{top,keys,end}`.
- **The radial count and the canvas columns** are in `measures.json`. See *E1 — geometry*.

### Carries

- **Inc-9:** the seat's key labels (including `SCOPE_HELP`'s `cerrar`, `subir`, …, which the legend
  no longer paints), group headers, and the other screens' own headers, renamed to
  `darkside.VIEW_NAMES`.
- **Inc-EN (`B-71`):** the renderer-painted Spanish that the samples copy (`INC8-D2-Q3`).
- **`INC8-D2-F2`** (`app.py:2625`, sizing the toast by `len`).
- The diff mode's tones: still in neither the catalogue nor the arm, since a git history is needed.
- The D2 arm's lane cost (~4 min).
- The earlier carries are unchanged: `INC8-F1`, `INC8-F3`, `UX-F12`, B-69 and B-70. `UX-F9` is closed
  by E1.

### Files

| Source (3 of 4 permitted) | Tests | Docs |
|---|---|---|
| `mapper/screens/help.py` | `tests/test_legend_design.py` | `01b-ux-decisions.md` (§3.1–§3.6 in English; §3.5 derived; pass-2 change log) |
| `mapper/darkside.py` | `tests/test_help_scope.py` | `01-requirements.md` (`A-107` only) |
| `mapper/app.py` (`legend_view` only) | `tests/test_vocabulary_declaration.py` | this record |
| | `tests/test_repair_layout.py` (`TC-R36`, per `A-107`) | |

No renderer under `mapper/views/` or `mapper/canvas.py` was changed. The mutants touched them only
temporarily, and each was restored and verified against its pin. `.dev-flow/state.json`,
`prototypes/`, `mapper.db`, the scratch files and `backup/pre-q9-reword-2026-09-28` were not
touched. Nothing was pushed.

### Commits (this pass)

- `9d51593` feat(legend): the legend in English; `01b` §3.5 derived from what is painted
- `29781d6` feat(legend): the declaration and its arms (E2, E4, UX-F4, CR-F2/F3/F4, SEC-F1)
- `9fbc6a8` feat(legend): the narrow full-height dock, vocabulary first, two-line own keys (E1, E3, A-107)
- `4b7c2ba` fix(legend): size `fit` by what it paints (`INC8-F-SEC-F2`)
- `27be355` test(legend): pin that the harvest advances by cell width (`INC8-F-CR-F6`)
- `a4dcdd2` test(legend): the narrow-panel arm reads the verdict, not the constant (`INC8-D2-F5`)
- `5d45c93` test(legend): the resize arm reads the frame, not `render()` (`INC8-D2-F6`)
- this record and the `01b` `:264` citation (docs)
