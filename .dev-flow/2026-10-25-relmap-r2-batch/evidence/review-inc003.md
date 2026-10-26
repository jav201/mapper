# Independent review — Increment 003 (lane L3): the traceability-matrix renderer

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `003` (lane L3) — lane commit `c38f929` on `da6f10b` |
| Reviewer | independent increment reviewer — code + security + UX lenses; authored none of this increment |
| Lenses | `agents/code-reviewer.md` · `agents/security-reviewer.md` · `agents/ux-reviewer.md`; record per `templates/increment-template.md` §4b |
| Scope reviewed | 1 source file: `mapper/screens/relmap/matrix.py` (573 lines) + the lane's test files `tests/test_relmap_matrix.py` (1113 lines, 32 nodes) and `tests/test_fold.py` (one scoped census allowance) |
| Owned PDR condition | `COND-SEC-1` (the lane half: the markup/ESC/RTL/control-char/LF/TAB battery through the real screen) |
| Verdict | **approve-with-nits** — 0 BLOCKER · 0 MAJOR · 2 MINOR |

---

## 1 · The key question: does the matrix renderer actually deliver LLR-RVM.1.1–4.2 through the frozen D1 surface — and is the hostile-text seam real?

The lane's one file implements the whole RVM family against the frozen `base.ViewState`/`paint`/`row_count`/`toggle` surface, and every LLR has at least one executable oracle that discriminates (fixtures carry non-default values; assertions would fail if the behavior were absent — spot-verified arm by arm, and independently re-proven by my probes and mutants below):

| LLR | Code | AT / TC | Test (tests/test_relmap_matrix.py) |
|---|---|---|---|
| RVM.1.1 rows/labels/windowing | `matrix.py:94` (`_window`), `:333-337` (label field), `:390-391` | AT-130 | `test_l0_window_centres_where_the_ends_allow` (:286), `test_window_declarations_keep_the_selection_visible` (:452) |
| RVM.1.2 cells, strongest edge, D5 glyphs, `○` badge | `:116` (`_winning_edge`), `:129` (`_cell`), `:406-412` | AT-133 | `test_l0_winning_edge_alert_before_plain` (:300), `test_l0_cell_glyph_table` (:319), `test_cell_census_on_the_synthetic_binds_map` (:608) |
| RVM.1.3 window declarations, ruler, legend | `:362-377` (out-of-view), `:378-388` (ruler), `:430-436` (flap+legend) | AT-130 | `test_columns_out_of_view_and_the_two_digit_ruler` (:469), `test_legend_line_names_the_evidence_glyphs` (:570) |
| RVM.2.1 rings, hop markers, hop-2 fold | `:162` (`_ring`), `:532` (`_ring_lines`), `:293` | AT-130/133 | `test_l0_rings_two_hop_same_direction_only` (:334), `test_hop2_rows_fold_below_the_sixty_cell_viewport` (:554) |
| RVM.2.2 summary + reach gauge + `not computed` | `:499-529` | AT-131/132 | `test_summary_and_gauge_against_the_oracle` (:654), `test_reach_not_computed_renders_honestly` (:675) |
| RVM.2.3 neighbourhood dimming, focused-node-only | `:296`, `:342-344` | AT-131/132 | `test_neighbourhood_is_called_for_the_focused_node_only` (:695), the black-box FAINT census `_assert_dimming_census` (:797) |
| RVM.3.1 zero test columns, declared | `:363-368` | AT-130 | `test_no_test_columns_declaration_and_skeleton_honesty` (:495) |
| RVM.3.2 empty / unknown / relates-to-nothing | `:279-287`, `:321-327`, `:477-479` | AT-130 | `test_empty_map_paints_no_node_on_record` (:403), `test_unknown_focus_paints_the_empty_state_without_raising` (:414), `test_relates_to_nothing_when_the_selection_is_isolated` (:423) |
| RVM.4.1 geometry, C10 audit, pre-cut labels | `:269-272` (audit Canvas), `base.label` everywhere | TC-RM-09 | `test_geometry_audit_sweep_is_clean_at_every_size` (:523) |
| RVM.4.2 markup-safe labels (C8/C-17 sink) | every canon-derived string through `base.label` (`base.py:65-76` → `darkside._row_text`/`fit`) | AT-134 | `test_hostile_title_renders_on_one_row_through_the_sink` (:584), `test_at134_hostile_payload_on_the_live_surface` (:1050), `test_at134_lf_tab_payload_renders_on_one_row` (:1090) |

The two declared readings (hop-2 fold keyed to viewport width; the whole-word ` change <id>: not computed` row) are lane interpretations, honestly declared in the packet §1/§5 and pinned by tests on both sides — they match the operator-approved reference renders at both shipped sizes (§4 below). They are proposed as contract clarifications, nothing applied by the lane: acceptable.

Source-file budget: `git show c38f929 --stat` — exactly **1 source file** (`mapper/screens/relmap/matrix.py`), 2 test files, 6 evidence transcripts. Within budget; no other lane's file touched (gate item 7 ✓; the D1 base is consumed, not modified).

## 2 · Findings

### BLOCKER — none.

### MAJOR — none.

### MINOR

**F1 · MINOR · `mapper/screens/relmap/matrix.py:471` — the ` ╌╌╌ root — nothing feeds it` line is unpinned: it appears in no LLR and no test asserts it.**
The line is the renderer's own invention for the up-ring-empty-but-down-nonempty case (LLR-RVM.3.2 mandates `╌╌╌ relates to nothing` only when BOTH rings are empty, which IS pinned at `tests/test_relmap_matrix.py:423-449`). The intent is honest (a declared empty line rather than a disappearing section — the same principle RVS.2 states for the sheet), and it is UX-acceptable, but nothing would redden if the line were dropped, mis-worded or mis-styled; it is also not among the packet's declared deviations. Pin one assertion (word + MUT tone) or drop the line to the plain `what feeds it ←` head.

**F2 · MINOR · `mapper/screens/relmap/matrix.py:425-434` — degenerate-height flap can read `01–00 / N`.**
When the body height falls below 6 rows, `row_avail` is 0, `row_window` is empty, and the flap still paints `01–00 / N` (`row_window.stop` is 0). Cosmetically wrong only at terminal heights no contract size reaches (the C10 sweep's smallest arm is (40,12)); the shipped 118/87×34 sizes derive 30 rows. Not blocking; a `max(1, …)` guard on the flap would close it.

No correctness, duplication, or convention defects found in the read of the full file. The renderer owns no write vocabulary, no `.render(` call, no markup-parsing sink; `_blit` writes per-char into the audited `Canvas` only.

## 3 · PDR condition verification — COND-SEC-1 (executed, not trusted from the packet)

Condition (from `evidence/pdr-security-reviewer.md`): hostile canon text pushed through the REAL screen — brackets, ESC, U+202E, control chars, and **LF+TAB** — must render literally, on ONE row each, markup inert, no injection, no row splitting; the seam is `darkside._row_text`/`fit` (not bare `plain`), coerce-then-cut.

Reviewer probe (`$TMP/r2-revl-l3/probe.py`, driven via `MapperApp(workspace=$TMP/r2-revl-l3/ws)` + `run_test(size=(118,34))`, `RelMapScreen` pushed the trunk-idiom way, REAL keys, painted frame read through `screen._compositor.render_strips()`). Hostile canon rows: an id `HLR-[bold]HOST[/bold].1` with title `hostile [bold]x[/] \x1b\x07xyz`; a title `[@click=app.quit] [bold]x[/]`; a title `bidi \u202e ereh`. Trimmed output — all 24 checks PASS:

```
[PASS] payload 'hostile [bold]x[/]' literal on ONE row carriers=1
[PASS] coerced form 'hostile [bold]x[/] ��xyz' present
[PASS] zero raw ESC in frame / zero raw BEL / zero raw U+202E / no raw LF/TAB
[PASS] payload '[@click=app.quit] [bold]x[/]' literal on ONE row carriers=1
[PASS] payload 'bidi � ereh' literal on ONE row carriers=1
[PASS] payload run carries no bold style style='#737373 on #000000'
[PASS] hostile id prefix literal  (HLR-[bold]H in the gutter)
[PASS] LF/TAB payload on ONE row carriers=1   (in-process build_map title "left\tright\nnext payload")
[PASS] no raw TAB in frame
[PASS] enter -> panel lens crumb   (app alive, toggle channel works)
```

Two probe-oracle corrections made during the run, both on MY side, not the renderer's: (a) a 43-cell payload is cut at the 37-cell panel seat with the declared C-10 ellipsis, so only the fitting printable prefix asserts — the cut tail is the contract's cut-after-coerce behavior, not a security hole; (b) the LF/TAB vehicle must be an in-process `build_map` map, because the canon derivation itself truncates a table cell at a raw LF and pre-coerces TAB (verified directly against `mapper/relmap/adapter.py:derive_reqharness_map` — `left\tright\nnext` derives to the title `'left right'`), so LF/TAB cannot physically reach the renderer through the canon path. The lane's AT-134 LF/TAB arm uses exactly that in-process vehicle (`tests/test_relmap_matrix.py:1090-1113`), consistent with the condition's intent: the renderer's one-row seam is what the arm exercises.

What would falsify COND-SEC-1 here: any raw `\x1b`/U+202E in the frame, a payload split across two painted rows, a `bold` style on the payload run, a `MarkupError`, or an audit `clip`/`overprint` event. None observed. **Condition satisfied — executed.**

## 4 · Verdict fidelity vs the prototype (`prototypes/round-2026-10-23/`, read-only)

References read: `PROTOTYPE.md`, `verdict-2026-10-24.json`, `shots/png/matrix-panel.png` (118) and `shots/png87/matrix-panel.png` (87). The real app was driven by the same probe at `run_test(size=(118,34))` and `(87,34)` — the live 303-node skeleton (worktree `REQUIREMENTS.md` copied into `$TMP/r2-revl-l3/ws`) plus the synthetic binds map injected in-process (the `matrix-panel.png` reference class, since the honest skeleton sources no TC columns). Frames captured to `$TMP/r2-revl-l3/ws/fidelity-{118,87}.txt` and `binds-{118,87}.txt` (deleted with the workspace).

**118 columns: match — declared-deviations-accepted.** Painted at 118 (trimmed): `row → col` + `matrix: HLR, LLR, AT, TC × AT, TC` note inside the left region; two-digit ruler `12345`; rows `1 HLR-T.1   ····✓` with the `▪` diagonal; flap `▁▁▁▁▁  01–07 / 7`; right panel `lens · HLR-T.1`, `what feeds it ←` / `a change reaches →`, ring rows `↓1 verifies TC-3 ✓` / `↓2 verifies TC-2 !`, summary `change HLR-T.1 reaches 6 nodes`, `hop 1: 2 direct · hop 2: 2 chained`, WARN gauge `reach  ██████████ 06`; legend `✓ verifies · ! evidence missing · · no verifies edge`. On the live skeleton: the verbatim `no test columns yet — the AT→test table (B-141) feeds this view` declaration, window `14–37 / 303` after 25 real `down` presses, `↑1 refines HLR-CNV.1` — matching the packet's pinned capture. Each of the packet's six declared deviations confirmed present and honest: (1) no US/AT/TC columns on the skeleton + verbatim declaration; (2) the panel's dim title line under the head band (the hostile-title surface); (3) single-spaced ring rows vs the prototype's padded 10-cell edge-type field (the acceptance strings pin `↑1 refines <id>` verbatim); (4) `reaches N nodes` wording per LLR-RVM.2.2; (5) full-transitive reach counts with hops 1–2 rings; (6) at 87 the declaration and summary cut inside their regions with the ellipsis — observed: `…the AT→test table (B-141) feeds …` and `change HLR-T.1 reaches 6 n…`.

**87 columns: match — declared-deviations-accepted.** Same composition at 87 (panel min-width preserved, gutter intact, `+10` keybar truncation, zero row over 87 cells, summary cut with `…` inside the panel) — matching `shots/png87/matrix-panel.png`'s behavior class.

**Undeclared deviations: none found** against the reference layout at either width. The only unpainted-by-contract surface is the F1 `root — nothing feeds it` line, an addition (not a deviation from a painted prototype behavior) and UX-acceptable; it is the one place the fidelity claim leans on unpinned intent.

UX limit declared: this is an automated walkthrough through the real mechanism (Textual headless driver, real keys, compositor-read frames) — `performed`. Expert inspection against the prototype chrome — `performed` (composition, tones, wording all consistent with the verdict PNGs modulo the declared deviations). Evaluation with real users — *not performed — this team is one person and no user of this surface exists outside it.*

## 5 · Reviewer mutation battery (control C-2 — mutants of my own, not the author's 11)

Every arm: pristine bytes saved (`sha256 a5e2142f50aafdf442e921a88d317860c1fb28565c77d4b02919f26287f05424`), mutant applied, the lane command run, restored from MY saved copy, restore sha256 verified. Mutated only `mapper/screens/relmap/matrix.py`.

| Id | Site | Change (the plausible shortcut) | Instruments | Verdict |
|---|---|---|---|---|
| M-REV-L3-1 | `matrix.py:138-141` (`_cell`) | graduated-binds glyphs swapped: `●` when evidence_missing, `◐` when bound (a plausible inversion of the graduation rule) | the lane pair (51 nodes) | **KILLED ×3** — `test_l0_cell_glyph_table`, `test_cell_census_on_the_synthetic_binds_map`, `test_at133_binds_cell_census_through_real_keys`. Restore `a5e2142f…` MATCH |
| M-REV-L3-2 | `matrix.py:102-113` (`_pair_index`/`_between`) | unordered-pair normalization dropped: edges keyed raw `(src, dst)`, lookup raw `(a, b)` ("edges are stored in input order anyway") | the lane pair (51 nodes) | **KILLED ×4** — `test_hop2_rows_fold_below_the_sixty_cell_viewport`, `test_cell_census_on_the_synthetic_binds_map`, `test_at131_lens_summary_hop_counts_and_dimming`, `test_at133_binds_cell_census_through_real_keys`. Restore `a5e2142f…` MATCH |
| BAD-CONTROL | — | **no mutation applied** (harness-honesty arm) | the lane pair (51 nodes) | **SURVIVED, rc=0** — `51 passed, 3 xfailed`; the harness cannot fabricate a kill |

Cross-check against the author's battery: the packet's 11/11 KILLED claims are consistent with the arms on disk (each named mutant maps to a real assertion that discriminates), the M-RVM-4 numbering gap is honestly declared, and the author's M-RVM-2/3 and my M-REV-L3-1 attack the same rule through different edits — agreeing verdicts, independent application.

## 6 · Traceability — evidence re-hash (C-59)

`sha256sum` recomputed over the packet's six declared transcripts, 2026-10-25, worktree `da6f10b`:

| Transcript | Declared in packet | Recomputed | Match |
|---|---|---|---|
| `p3-inc003-red-tests.txt` | `c13d8460…5f21` | `c13d84607a8926a33678e48319dd2d0deeda67c34103457dcaab2188985a5f21` | ✓ |
| `p3-inc003-red-move-aside.txt` | `3b90f544…b05a` | `3b90f5444ab49994438e60735351deddf41a440cfb3844bd6b34c1e18a07b05a` | ✓ |
| `p3-inc003-green-targeted.txt` | `f1c800cd…c7a` | `f1c800cd52621a775d609a0da1bf08a80b8b7b157a5aaef13433224ea0b34c7a` | ✓ |
| `p3-inc003-green-guards.txt` | `9ed10ffa…1e7` | `9ed10ffa8dd905a9e039ee37472dfcb1869d217cfb2f074888132e6e356df1e7` | ✓ |
| `p3-inc003-mutants.txt` | `dc681df1…f175` | `dc681df15e00e744baafacbc2c8df1e6db3cea192e8d9725922652703049f175` | ✓ |
| `p3-inc003-renders.txt` | `8ac38a1e…55f7` | `8ac38a1ee8067d0e3e9c1a2b01a61ebccc30d72e27b066fec1b0dcdc7b7e55f7` | ✓ |

**6/6 MATCH.** The transcripts the packet cites are the bytes on disk.

## 7 · Verdict

Per the commission's scale: **approve-with-nits** — 0 BLOCKER · 0 MAJOR · 2 MINOR (F1 the unpinned `root — nothing feeds it` line; F2 the degenerate-height flap), both foldable into a future pass without re-opening the increment.

Per the role rules' tokens: **OK to advance** with notes — no HIGH; the two MINORs recommend, they do not block.

Why not iterate: every owned LLR traces LLR → AT → test name → code line with a discriminating oracle; the lane's RED counterfactuals, 11/11 mutation battery, correction population, and 6/6 re-hashable transcripts verify clean; my independent hostile battery through the real screen (24/24 checks) satisfies COND-SEC-1 including the LF/TAB one-row arm; my two reviewer mutants died to named tests and the bad control proved the harness honest; and the shipped surface matches the operator-approved prototype at both 118 and 87 with exactly the six declared deviations — honest declarations, no undeclared ones.

| Lens | State |
|---|---|
| code | 2 MINOR (F1, F2) open — approve-with-nits |
| security | COND-SEC-1 executed clean: brackets/`@click`/ESC/U+202E/BEL/LF/TAB all literal on one row, zero raw bytes, no forged style, coercion precedes the width cut (executed probe, §3) |
| ux | real-mechanism walkthrough passed at both widths; declared deviations accepted; one unpinned presentation line noted (F1); user evaluation not performed — one-person team, no external user of this surface |

Post-review hygiene: `mapper/screens/relmap/matrix.py` sha256 `a5e2142f…` equals the pre-review baseline; `tests/test_relmap_matrix.py`/`tests/test_fold.py` byte-untouched; `git status` on the lane files clean (concurrent out-of-lane edits to `tests/test_relmap_shell.py` and other agents' evidence files observed, not touched, none caused a lane failure); tmp workspace `$TMP/r2-revl-l3` deleted.
