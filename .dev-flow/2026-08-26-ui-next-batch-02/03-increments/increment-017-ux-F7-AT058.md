# increment-017 — UX rulings: `F7` (Inc-5) and `UI-AT058` (Inc-B55a), plus two newer strings

**Lens:** `ux-reviewer`, independent. **Date:** 2026-09-19.
**Pickup:** Inc-CONFIRM / whole-branch gate, per `state.json::p3_progress.routed_findings`.
**This report authorises nothing.** It issues rulings and criteria; `software-dev` implements, the coordinator authorises.

---

## Verdict

| Item | Verdict | Axis |
|---|---|---|
| **F7** — selected node that is also a hit | **RULED · precedence stays** | but `LLR-N07.2.2b` is **unmet as written** — requirements finding, below |
| **UX-F7b** — NEW, found while verifying F7 | **FAIL · MEDIUM, fix owed** | a **non-hit** is painted in the **hit style** in `layered` whenever focus is off the canvas |
| **UI-AT058** — `"declaración no disponible"` | **PASS WITH NOTICES** | register OK, **vocabulary domain** and **transience** both mis-set |
| **`PAN_INERT_HINT`** | **PASS** | correct, actionable, paints in full at 118x34 and 80x24 |
| **UX-HINT1** — NEW, found while verifying the hint | **FAIL · LOW-MEDIUM, fix owed** | the *clear* outlives its truth: one inert pan press blanks the hint line permanently |
| **ExportTooLarge refusal · the absolute path** | **RULED · appending the path stays** | the declared risk is **measured and FALSE**; a different, smaller one is measured and true |

Criterion states use `/dev-flow` §*Evidence states*.

---

## Context of use (ISO 9241-210 activity 1), as driven

| | |
|---|---|
| **User** | the map's single operator; keyboard-only; knows the chord seat |
| **Task A** | run a search, step the hit set with `n`/`N`, judge the node under the cursor |
| **Task B** | press `e` on a map that exceeds the export budget, and act on the refusal |
| **Environment** | Windows terminal, Textual 8.2.8. Declared context **118x34** (below it `_apply_region_visibility` hides the rail and the inspector). Swept down to **80x10**. |

---

## Mechanism — what drove every reading

`App.run_test()` + `Pilot.press()` on the **shipped chords** — `/`, the typed query, `enter`, `n`, `N`, `j/k/h/l`, `g`, `o`, `r`, `L`, `e` — with every assertion read from **`screen._compositor.render_strips()`**, i.e. the composited frame, taken **per cell with its style**. No `action_*` was called in place of a key.

**One declared injection.** `"declaración no disponible"` is reachable only through a code defect, so it was reached by substituting `screen._current_renderer` with a renderer that has no `_painted_ids_for` entry — the state `AT-058` exists for. The *painting* is real; the *defect* is injected, and it is labelled that way in the table.

**One declared stub-avoidance.** The toast was read through the real `notify()` → real `Toast` widget → compositor, using `run_test(notifications=True)`. The shipped arms at `tests/test_export_state.py:434` and `:471` stub `screen.notify` and assert the message **string**; that is a pre-layout proxy in `C-32`'s exact sense and cannot see footprint or clipping. See N-C2.

Probes, runnable by copying into a mirror's `tests/`:
`C:\Users\jjgh8\AppData\Local\Temp\claude\C--Users-jjgh8-clde\5fba800c-287a-459a-b7c8-dd44777ea077\scratchpad\ux-probes\test_ux_probe_f7.py`
`C:\Users\jjgh8\AppData\Local\Temp\claude\C--Users-jjgh8-clde\5fba800c-287a-459a-b7c8-dd44777ea077\scratchpad\ux-probes\test_ux_probe_strings.py`
Combined output digest, stable across 3 consecutive runs: `69fd8ab4a2791c7d`. See M3 for one unreproduced divergence.

---

## Item 1 — `F7`: a selected node that is also a hit

### What is actually painted (composited frame, 118x34, query `riesgo`, hits `{riesgo-root, b, c, d, e}`, non-hit `f`)

| frame | cursor | focus | cursor's card | a non-selected hit | the non-hit `f` | strip |
|---|---|---|---|---|---|---|
| A1 `layered`, after `n` | `b` (a **hit**) | `""` | `bold #000000 on #1783ff` | `#f5f5f5 on #262626` | `#f5f5f5 on #000000` | `2/5 coincidencias en el mapa` |
| A3 `layered` | `f` (**non**-hit) | `""` | `bold #000000 on #1783ff` | `#f5f5f5 on #262626` | — | `0/5 coincidencias en el mapa` |
| B1 `outline` | `b` (hit) | `""` | `bold #000000 on #1783ff` | `#f5f5f5 on #262626` | `bold #f5f5f5 on #000000` | `2/5` |
| C1 `radial` | `b` (hit) | `rail` | `bold #000000 on #1783ff` | `#f5f5f5 on #262626` | `#a3a3a3 on #121212` | `2/5` |

**F7 is confirmed, not taken on trust.** A1 and A3 are byte-identical in the cursor's style: a selected hit and a selected non-hit are the same picture, in all three reachable views.

### RULING — the precedence is correct. It stays.

Three grounds, each checkable:

1. **The answer already ships on a second channel that costs no cells.** The pagination strip carries `at/N`: measured `2/5` with the cursor on a hit, `3/5` after another `n`, and **`0/5` with the cursor on a non-hit** (`mapper/app.py:2378`). The operator stepping with `n`/`N` — the exact task in the context of use — reads "am I on a hit" off a numeral that is present in every frame, is not a colour, and does not compete for the title row. F7 names a lost signal; the signal is not lost, it moved.
2. **The cursor is the one mark that may never be ambiguous.** On a 58-column canvas the card's title row is the only cell run either signal can occupy. A blended style would weaken a mark consulted on every keystroke in order to strengthen one that is redundant with the strip. That is the wrong trade for this task.
3. **Diverging would have been the silent UX change the implementer declined to make.** That judgement was right, and this ruling ratifies it rather than second-guessing it.

**Scope correction, measured.** The finding says "all five renderers changed by Inc-5". Three of those five — `LaneRenderer`, `RailTimelineRenderer`, `HybridLaneRenderer` — are exported from `mapper/views/__init__.py` and **instantiated nowhere in product code** (`mapper/app.py:1228-1230` builds only `Layered`, `Outline`, `Radial`; no chord in `mapper/keymap.py` reaches the lane family). So F7's operator-visible surface is **three views, not six**. Recorded because a finding sized at six renderers reads as broader than the thing it describes.

### REQUIREMENTS FINDING — `LLR-N07.2.2b` is unmet and will stay unmet

`LLR-N07.2.2b` says hits are painted *"distinguishably from non-hit nodes"*, quantified over nodes with no exception for the cursor. Under this ruling the selected node is deliberately **not** so painted. **The requirement text and good UX disagree, and the requirement is the one that is wrong.**

> **Amendment owed (A-101 suggested):** `LLR-N07.2.2b` excepts the selected node explicitly, and names the pagination strip's `at/N` numeral as the channel that answers hit/non-hit at the cursor. Without the amendment, this ruling and the requirement cannot both stand, and the implementation — not the requirement — would have to move.

### UX-F7b — NEW FINDING · MEDIUM · fix owed · **not** covered by the ruling above

`mapper/views/layered.py:703` paints the unfocused selection `f"{darkside.INK} on {darkside.STEP}"` — **byte-identical to the hit style** at `layered.py:597`.

Driven: query `riesgo` live, cursor navigated to the non-hit `f`, then `g` (`ir al rail`, a shipped chord). Read off the composited frame:

```
>>> UX-F7b: 6 titles in HIT livery ['Cartera','Contra','Audito','Provee','Seguro','Hallaz']
>>> declared hits: ['b','c','d','e','riesgo-root']   strip: '... 0/5 coincidencias en el mapa'
```

**Six cards in hit livery, five declared hits, and the strip in the same frame says the cursor is on none of them.** This is the opposite error from F7 and it is the worse one: F7 withholds a signal the strip can replace; this **paints a false one**, and against *"distinguishably from non-hit nodes"* it fails in the direction that has no compensating channel. The canvas and the strip contradict each other in a single frame.

Confirmed `layered`-only: `outline` (B2) and `radial` (C1) keep `bold #000000 on #1783ff` regardless of `focus_owner`; neither consults it.

Reachability: `g` is a seated chord (`keymap.py`, `view` group, *"ir al rail"*), so a search followed by a jump to the rail is an ordinary move, not a contrived one.

**Criterion for the fix (observable, drivable, can fail):**

> With a search live in `layered` at 118x34 and the focus on any region other than the canvas, **no node outside `state.hits` is painted with the hit style** in the composited frame, and the number of titles painted in hit livery equals the number the strip declares.

The style chosen is `software-dev`'s call; the constraint the code states — *"while another region owns the focus the selection is still SHOWN but stops claiming to be active"* — is satisfiable without borrowing the hit background (e.g. a reduced-strength ACCENT). **I do not prescribe the style; I prescribe that it not be the hit style.**

---

## Item 2 — the operator-visible strings

### (a) `"declaración no disponible"` — PASS WITH NOTICES

Painted, at all three sizes, no truncation (injected defect, real paint):

```
[118x34] healthy: | ▰▱▱▱▱▱   1/6|
[118x34] broken : | ▰▱▱▱▱▱   1/6  declaración no disponible|
[100x30] broken : | ▰▱▱▱▱▱   1/6  declaración no disponible|
[80x24]  broken : | ▰▱▱▱▱▱   1/6  declaración no disponible|
```

**Register against the strip's neighbours: PASSES structurally.** The strip's other content is `▽ 1 fuera de vista`, `1/6`, `2/5 coincidencias en el mapa` — lowercase, verbless noun phrases, no terminal punctuation. The new string is the same shape.

**⚠ N-A1 — the routed concern is UPHELD: *"no disponible"* reads as transient.** In Spanish it is the idiom of the outage (*servicio no disponible*, *temporalmente no disponible*) and it invites waiting or retrying. The condition is deterministic, permanent and reproduces on every frame. Recommend a wording that cannot be waited out.

**⚠ N-A2 — *"declaración"* is the wrong register, by vocabulary domain rather than by tone.** Every neighbour on this strip names something about the operator's **map** — what is *fuera de vista*, how many *coincidencias en el mapa*. *"declaración"* names an **internal contract** (`HLR-N06.3`'s declared painted set). It is the only word on the strip the operator has no model for, and it tells them nothing about their map. The sentence's real content is *this view cannot tell you what is hidden*.

Suggested, in the strip's own vocabulary and immune to both problems — **`no se sabe qué queda fuera`**. It uses the neighbour's own noun (*fuera de vista*), states a knowledge gap rather than an availability gap, and cannot be waited out.

**⚠ N-A3 — naming the view: RECOMMENDED, for an operator reason.** Not merely so a bug report is actionable: the operator has a **real workaround** — `o` / `r` switch to a view that does declare — and naming the failing view is what makes that workaround findable. Width permits; measured, the strip at 80 columns ends at column ~44 of 80 with the string present.

**⚠ N-A4 — the string has no arm that reads it as painted.** `grep` over `tests/` finds the literal **zero** times. `AT-058`'s two arms (`tests/test_overflow.py:1214`, `:1259`) pin the **raise** and the `None` degradation — the mechanism, correctly — but nothing pins that the strip paints words rather than falling silent, which is the collision `AT-058` exists to break. The probe above is the missing arm, near enough to lift.

### (b) `PAN_INERT_HINT` = `"esta vista no se desplaza · navega con j/k/h/l"` — PASS

Driven with the real `L` in `outline`. Painted in full at 118x34 and 80x24, no wrap, no truncation:

```
siguiente ▸ esta vista no se desplaza · navega con j/k/h/l
```

Register matches the hint line's own voice; it states a standing property (not a transient one) and it **is actionable** — it names the keys that do move. The comment at `mapper/app.py:91-96` anticipates exactly the `UI-AT058` failure mode and avoids it. Nothing to change in the wording.

### UX-HINT1 — NEW FINDING · LOW-MEDIUM · fix owed

Measured lifecycle, hint line read off the composited frame:

```
layered, fresh        |siguiente ▸ navega con j/k/h/l · ↵ ficha · / buscar|
o -> outline          |siguiente ▸ navega con j/k/h/l · ↵ ficha · / buscar|
L (inert pan)         |siguiente ▸ esta vista no se desplaza · navega con j/k/h/l|
after j/k/l/h         |siguiente ▸ esta vista no se desplaza · navega con j/k/h/l|   <- correct: standing property
o -> back to layered  |siguiente ▸|                                                  <- DEFECT
j in layered          |siguiente ▸|
```

`_clear_pan_hint` (`mapper/app.py:3369-3371`) calls `set_hint("")`, and `HintLine` (`mapper/widgets/chrome.py:150`) has **no default to fall back to**. So one press of a pan key in a non-panning view **permanently blanks the hint line in `layered` too**, leaving the label `siguiente ▸` pointing at nothing. The default affordances (`↵ ficha · / buscar`) never return; only another handler writing a hint refills the line, with different content (a search writes `n siguiente · N anterior · esc limpiar`).

This is the same family the method's own docstring is about — a hint that outlives its truth — advanced one step: **the clear outlives its truth.** The docstring is right that the hint must not latch; emptying is not the same as restoring.

**Kept out of HIGH** because the `KeyBar` below still carries `nav j siguiente  k anterior  h padre  l hijo`, so no capability is lost — only the hint line's own guidance, and the label's promise.

**Criterion:** *after any view toggle, the hint line paints a non-empty hint.* Fails today, passes on a restore-the-default fix.

### (c) The `ExportTooLarge` refusal notice, and the absolute path

Full string (`mapper/app.py:3512-3516`):

> `mapa demasiado grande para exportar: {cells} celdas, límite {limit}. Enfoca un subárbol con f y exporta esa vista.` + `" El archivo en {path} es de una exportación anterior y ya no refleja este mapa."`

**Register: PASS.** Lowercase, plain, no blame, measured figures, and it names the route forward with the chord. Consistent with the batch's other notices.

**The declared risk was UNMEASURED. It is now measured, and it is FALSE.** Toast footprint read off the composited frame, real `notify()` → real `Toast`; `prior=True` is the arm that appends the path:

| terminal | rows **without** the stale sentence | rows **with** it (106-char path) | headline painted | **action painted** | stale painted |
|---|---|---|---|---|---|
| 118x34 | 5 | **8** | yes | **yes** | yes |
| 100x30 | 5 | **9** | yes | **yes** | yes |
| 80x24 | 6 | **11** | yes | **yes** | yes |
| 70x20 | 6 | **13** | yes | **yes** | yes |
| 80x12 | 6 | **11** | yes | **yes** | yes |
| 80x10 | 6 | **11** (`y = -2`, clipped) | **NO** | **yes** | yes |

With a realistic 30-char workspace path (`C:\Users\jjgh8\mapas\crece.svg`) the same frames measure 6 / 9 / 9 rows at 118x34 / 80x24 / 80x12, all three parts intact — so the 106-char figures above are `tmp_path`'s worst case, not the operator's normal one.

- **`Enfoca un subárbol con f y exporta esa vista.` is painted intact at every size measured, down to 80x10.** `ToastRack` is `dock: bottom; align: right bottom`, so an over-tall toast is clipped **at the top**, not the bottom. The actionable half is structurally the last thing to go.
- **What the path does cost:** at 80x10 the **headline** `mapa demasiado grande para exportar` is clipped away, and it is clipped *because of* the appended path — the same terminal without the stale sentence paints it. So the path can cost the operator the sentence saying **what happened** while preserving the one saying **what to do**. That is the better half to keep, and it is the opposite trade from the one anticipated.
- **The real cost is footprint**: the path roughly doubles the toast, from 5-6 rows to 8-13, covering 46% of an 80x24 terminal and 65% of a 70x20 one — over the canvas the operator is being told to navigate with `f`.

**RULING — appending the path is the right call and stays.** The stale-file declaration is load-bearing (`B-68`'s family, `A-100.2`), and a path the operator can act on is what makes it a declaration rather than a warning. The declared risk does not materialise at or above 80x12; below that the casualty is the headline, not the action.

**⚠ N-C1 — ROUTED TO THE OPERATOR, not ruled.** Shortening the path to the filename plus a locative (e.g. *"El archivo `crece.svg` en la carpeta del mapa es de una exportación anterior…"*) would recover 2-4 rows at every size and lose nothing the operator needs — they know their workspace. **I do not rule it**, because `tests/test_export_state.py:432` asserts `str(path) in message`: shortening the path **reddens a shipped acceptance arm**, and weakening an acceptance criterion needs ratification the asymmetry principle denies to the party proposing it. **Question for the operator:** *is the absolute path in this toast there for the operator, or for a bug report? If the former, may the arm be re-scoped from "contains the absolute path" to "identifies the stale file"?*

**⚠ N-C2 — no arm reads this toast as painted.** `tests/test_export_state.py:434` and `:471` both stub `screen.notify` and assert on the message **string**. Correct for *what is said*; blind to *what is shown* — the 13-row footprint, the top-clipping at 80x10, and any wrap that could separate the chord `f` from its sentence. This is `C-32` one surface over: the assertion reads a pre-layout proxy. The mechanism to close it exists and is demonstrated above (`run_test(notifications=True)` + `app.screen.query("Toast")[0].region` + compositor strips). **Recommend one arm at 80x24 asserting the action phrase is painted intact in the toast's region.**

---

## Criteria table

| # | Criterion | How exercised | Painted result observed | Verdict | State |
|---|---|---|---|---|---|
| U1 | A selected hit is distinguishable from a selected non-hit | `/riesgo` `enter` `n` `n`, then `h h h l j l`; per-cell styles from compositor | identical: `bold #000000 on #1783ff` in both | **not met — ACCEPTED by ruling** | executed |
| U2 | The operator can tell, at the cursor, whether they are on a hit | same chords; strip region clipped from the frame | `2/5` → `3/5` → `0/5 coincidencias en el mapa` | **met, on the strip** | executed |
| U3 | No **non-hit** is painted in the hit style | `/riesgo`, cursor to `f`, then `g` | 6 titles in hit livery vs 5 declared hits; strip `0/5` | **FAIL — UX-F7b** | failed |
| U4 | `outline` / `radial` keep selection distinct when focus leaves the canvas | `o` / `r` then `g` | `bold #000000 on #1783ff` unchanged | met | executed |
| U5 | The lane renderers are operator-reachable | grep of product instantiation + full keymap | instantiated nowhere; no chord | **n/a — not reachable**; F7's surface is 3 views, not 6 | executed |
| U6 | `"declaración no disponible"` paints, untruncated, at 118x34 / 100x30 / 80x24 | unregistered renderer substituted (**declared injection**); strip region from the frame | paints in full at all three | met | executed |
| U7 | That string reads as permanent, not transient | expert inspection against the strip's neighbours | *"no disponible"* is the outage idiom; *"declaración"* is not map vocabulary | **not met — N-A1, N-A2** | executed |
| U8 | `PAN_INERT_HINT` paints in full and names a live alternative | `o` then the real `L`; hint region from the frame | full line, both halves, no wrap, at 118x34 and 80x24 | met | executed |
| U9 | After a view toggle the hint line paints a non-empty hint | `o` `L` `j k l h` `o` | `|siguiente ▸|` — label with no payload | **FAIL — UX-HINT1** | failed |
| U10 | The refusal's actionable half survives on a narrow terminal | real `e` → real `Toast`, 6 sizes × 2 arms | intact at every size to 80x10 | met — risk retired | executed |
| U11 | The refusal's headline survives | same sweep | lost at 80x10 (`y = -2`), and only with the path appended | **not met below 80x12 — declared, not blocking** | executed |
| U12 | The appended path's footprint cost is bounded | same sweep, with and without the stale sentence | +3 to +7 rows (106-char path); +1 to +3 (30-char path) | met, with N-C1 open | executed |
| U13 | An arm reads the refusal toast as painted | grep + read of `tests/test_export_state.py` | both arms stub `notify` and read the string | **not met — N-C2** | failed (test-evidence axis) |
| U14 | An arm reads `"declaración no disponible"` as painted | grep over `tests/` | zero occurrences of the literal | **not met — N-A4** | failed (test-evidence axis) |

---

## ⚠ Notices (declared, not blocking)

- **N-A1 / N-A2 / N-A3** — `"declaración no disponible"`: transience idiom, internal vocabulary, and the un-named view that hides a real workaround.
- **N-A4 / N-C2** — two operator-visible strings with no arm reading them as painted.
- **N-C1** — the absolute path could be shortened; routed to the operator because it reddens a shipped arm.
- **M1** — `mapper/app.py` in the repo **worktree is ahead of my mirror** by an uncommitted `SEC-H2` change (confirm-dialog `markup=False`; `darkside.plain` on the confirm title; plus untracked `tests/test_confirm_markup.py`). **All four regions I ruled on are byte-identical between mirror and worktree** — `_pagination_text` `97d7cc7dc63b`, `action_export_svg` `d185bb4e6970`, `_pan` `2670e4a5d7ff`, `_clear_pan_hint` `b95946ba9d6f` — and `views/*.py`, `darkside.py`, `keymap.py` match exactly. The rulings hold against the live tree; the mirror is not a snapshot of it.
- **M2 — the mirror cannot run the lane, and this extends `S-F14`.** `pytest` from the mirror root fails **collection**: `tests/test_views_hits.py` (via `test_a3_census.tracked`, which shells `git ls-files`; the mirror has no `.git` — the `S-F15` family) and `tests/test_repair_map_truth.py` (missing `docs/ARCHITECTURE.md`). `fixtures/` is absent too, so every arm using `inc3_support.install` fails at runtime. Excluding the two modules, 1051/1071 collect. **A mirror provisioned as `mapper/ + tests/ + pyproject.toml` is sufficient for targeted probes and insufficient for the lane** — so "reviewed in an isolated mirror" and "ran the lane" cannot both be true of the same tree as provisioned. Worth adding to catalog entry 15 beside the `.pth` trap.
- **M3 — evidence stability, with one unexplained divergence declared.** Ten consecutive probe runs (6 warm, 2 cold-cache, 2 after forced recompilation) were byte-identical apart from pytest's wall-clock line. The rebuilt probe pair ran 3× at digest `69fd8ab4a2791c7d`. **One earlier run produced a different digest (`3265fdfebe7a3877`) that I could not reproduce in the ten that followed and whose cause I did not isolate.** Declared rather than dropped. No load-bearing reading — no style string, no strip text, no hint text, no toast geometry — varied in any run.
- **`mapper.__file__` was asserted inside the mirror** in every probe module, per the `_editable_impl_mapper.pth` trap. No probe file was named after a stdlib module. All probe files were removed from the mirror afterwards; `tests/*.py` there now matches the repo except the untracked `test_confirm_markup.py`.

---

## The three evaluation acts, declared separately (ISO 9241-210 activity 4)

- **Automated walkthrough through the real mechanism — PERFORMED.** Textual `App.run_test()` + `Pilot.press()` on shipped chords; every assertion read from the composited frame, per cell with its style. Two departures declared inline: the `_current_renderer` substitution that is the only route to `AT-058`'s string, and `run_test(notifications=True)` to make the real toast paint. Evidence: the two probe files named above; digest `69fd8ab4a2791c7d`.
- **Expert inspection against declared criteria — PERFORMED.** Cognitive walkthrough over Tasks A and B; register comparison of the four strip strings against each other and against the hint line and the toast; reachability audit of the six renderer classes against `app.py` and `keymap.py`.
- **Evaluation with real users — NOT PERFORMED.** This team is one person and no user of this surface exists outside it. No participants, no population, no PII. Nothing in this report is offered as evidence of what a user would do; U1-U14 are claims about what the product paints.

---

## Explicitly NOT covered

- `FLAKE-1`, `.gitattributes` / `autocrlf`, `SEC-F4`, the socket-level guard, the export budget's derivation, and `F3` — out of scope by the brief. `F3` is `qa-reviewer`'s, running concurrently.
- **The default lane was not run** — it cannot be, in this mirror (M2). No claim is made that my findings leave the suite green; nothing I ran changed product code, and the mirror was restored to its provisioned state.
- **The concurrent `SEC-H2` change in the repo worktree was not reviewed.** It is outside both routed items and belongs to the security lens.
- **No colour-vision / contrast evaluation.** `#f5f5f5 on #262626` vs `bold #000000 on #1783ff` were compared as *distinct tokens*, not as perceptually separable under any deficiency model. If that axis matters, it is a separate pass with a separate instrument.
- **Terminals narrower than 70 columns and shorter than 10 rows were not swept.**
- **No real terminal emulator.** Everything is Textual's headless compositor. It is the frame the app composes; it is not a photograph of a console window. Font, true-colour downgrade and emulator-specific wrapping are untested.
- **No fix was implemented.** Two fixes are owed (UX-F7b, UX-HINT1) and two test arms are recommended (N-A4, N-C2); all four are `software-dev`'s.
