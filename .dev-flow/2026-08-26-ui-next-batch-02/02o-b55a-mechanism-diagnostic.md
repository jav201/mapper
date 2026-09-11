# 02o · B-55a mechanism diagnostic — independent lane

Read-only lane. No repo source or test file was edited, created or deleted; no
`print`/logging was added to `mapper/`. All instrumentation was in-process
monkeypatching from probes under `C:\Users\jjgh8\clde\`. Working tree observed
CLEAN at `c6f3f25` before and after; no evidence of another writer.

Probes written for this lane (all outside the repo):

- `C:\Users\jjgh8\clde\b55a_trace.py` — wraps `_canvas_size`,
  `_declare_after_layout`, `on_resize`, `refresh_canvas` and `Static.update`,
  logs the ordered pass sequence.
- `C:\Users\jjgh8\clde\b55a_region.py` — snapshots every id'd widget's region
  before `o`, immediately after the `o` repaint returns, and after `pause()`.
- `C:\Users\jjgh8\clde\b55a_intervene.py` — three causal interventions.
- `C:\Users\jjgh8\clde\b55a_reverse.py` — the outline → layered direction.

---

## BLUF

The gap is **not** a header-pricing defect. It is a **stale final write**: the
canvas is painted, and *then* the layout moves under it, and nothing repaints.

The thing that moves the layout is the strip below the canvas.
`_unpainted_ids()` returns `None` in outline (`app.py:1596`), so
`_pagination_text()` drops the `▽ N fuera de vista` token (`app.py:2143-2146`).
That shortens the strip's line from 36 cells to 17. `#map-pagination` is
`max-height: 3; overflow: hidden` with no fixed height (`app.py:3375`), i.e.
content-driven, and `#map-body` is `height: 1fr`. So at any width where 36 cells
wrap and 17 do not — measured threshold: terminal width ≤ 34 — the strip goes
from 2 rows to 1 and **the canvas region gains a row**. `refresh_canvas` writes
the canvas at `:2370` and the strip at `:2425`, so the canvas content for that
frame was already fixed, computed from the pre-reflow region. Nothing re-renders
afterwards: `refresh_canvas` never schedules `_declare_after_layout`, never
touches `_declared_for`, and no `on_resize` fires because the *screen* did not
resize.

The handed hypothesis (layered's header height charged in outline) is **true as a
fact and refuted as the explanation of the gap**. It is a real, separate defect
that costs outline rows at a different set of sizes — including two of the seven
"zero-gap" sizes, where it shows up as a wasted row with `gap == 0`.

---

## (a) Is the subtracted header height computed from `layered`'s geometry
regardless of the active view? — **YES, confirmed.**

Call chain, with no branch on the active renderer anywhere in it:

- `app.py:1509` — `_canvas_size` does
  `rows = self._header_rows(canvas.content_size.width or region.width)`
- `app.py:1456` — `_header_rows` returns
  `header_rows(self.graph, self._canvas_width(), wrap_w)` — imported from
  `mapper/views/layered.py`.
- `layered.py:469-471` — `header_rows` builds its measured line from
  `_header_line(graph, avail, bool(graph.schema), _METER_PCT, len(graph.nodes))`,
  i.e. **layered's** header (`◆ mapper · árbol legacy … N nodos ▽ N fuera de
  vista`), priced at its worst case.
- `layered.py:472-473` — that line goes through `Console.render_lines` at
  `wrap_w` and the row count is returned.

Nothing on that path reads `self.outline_mode`, `self.radial_mode` or
`_current_renderer()` (`app.py:1695-1700`). Measured values in outline, from the
trace: `header_rows=3` at canvas width 24 and 28, `header_rows=2` at 30/32/34/35/
40/60. Outline's own header is `◆ mapper · outline` — 18 cells, one physical row
at every sampled width (`outline.py:54-58`).

So in outline `_canvas_size` returns `region.height - (rows - 1)` where `rows` is
layered's: **outline is charged 1 extra logical line at widths ≥ 30 and 2 at
widths 24/28**, plus the `region.height <= rows` guard (`app.py:1510-1511`) fires
on outline using layered's header height — that is what clamps `h` to 1 at
(28,14) and at (34,14)'s pre-reflow region.

This is real. It is not what the `gap` column measures (see the VERDICT).

---

## (b) What `h` did the terminating pass actually render at?

Observed, not inferred: every `_canvas_size()` return and every
`Static.update()` on `#map-canvas` was logged in order.

**The settle loop is not involved in the outline frame at all.** At every size,
`_declare_after_layout` ran exactly 3 passes, all in **layered** mode during map
open, and terminated correctly — its last pass rendered at the then-current
region and `region == self._declared_for`, so it did not re-schedule. The `o`
press then produced **exactly one** canvas write, from `refresh_canvas`, and
`on_resize` fired exactly once per run — during open, *before* `o`, never after.

The terminating (and only) write for the outline frame, per loss size:

| terminal | pass | region at render | `header_rows` | `h` used | lines written | region after settle | `cs_h` after settle |
|---|---|---|---|---|---|---|---|
| (24,20) | `refresh_canvas` (seq 22-24) | (24,**7**) | 3 | **5** | 5 | (24,**8**) | 6 |
| (30,16) | `refresh_canvas` (seq 22-24) | (30,**4**) | 2 | **3** | 3 | (30,**5**) | 4 |
| (32,16) | `refresh_canvas` (seq 22-24) | (32,**4**) | 2 | **3** | 3 | (32,**5**) | 4 |
| (34,14) | `refresh_canvas` (seq 22-24) | (34,**2**) | 2 | **1** | 1 | (34,**3**) | 2 |

Verbatim (30,16):

```
22 [ press-o] refresh_canvas> view=outline
23 [ press-o] canvas_size  by=refresh_canvas region=(30, 4) content_w=30 header_rows=2 h=3 view=outline
24 [ press-o] UPDATE       by=refresh_canvas n=3 region=(30, 4) first=◆ mapper · outline last=  - Finanzas  3 nodos
26 [ settled] canvas_size  by=probe        region=(30, 5) content_w=30 header_rows=2 h=4 view=outline
```

`header_rows` is **identical (2) on both sides** of the change. The only thing
that moved is `region.height`: 4 → 5.

What moved it (`b55a_region.py`, three-instant widget snapshot, (30,16)):

```
map-pagination  before=(0,10,30,2)  after_o=(0,11,30,1)  settled=(0,11,30,1)  <-- MOVED
map-body        before=(0,6,30,4)   after_o=(0,6,30,5)   settled=(0,6,30,5)   <-- MOVED
map-canvas      before=(0,6,30,4)   after_o=(0,6,30,5)   settled=(0,6,30,5)   <-- MOVED
strip layered : ' ▰▱▱▱▱▱▱▱   1/8  ▽ 7 fuera de vista '   (36 cells -> 2 rows at w=30)
strip outline : ' ▰▱▱▱▱▱▱▱   1/8  '                      (17 cells -> 1 row)
```

`#map-rail` and `#map-inspector` did not move at any size.

---

## 3. VERDICT — **the handed hypothesis is REFUTED as the mechanism of the gap; the mechanism is a post-write region reflow driven by the strip's content height.**

Causal chain, each link with evidence:

1. `o` sets `outline_mode`; `refresh_canvas` runs (`app.py:2351`).
2. `:2355` `_canvas_size()` reads the **pre-reflow** region → `h`.
   *(observed: seq 23)*
3. `:2364` outline renders `lines[:h]` (`outline.py:162`).
4. `:2370` `canvas.update(text)` — **this is the content that stays on screen**.
   *(observed: seq 24)*
5. `:2425` the strip is updated **last**, with `_pagination_text()`, which at
   `:2143-2146` appends the overflow token only `if hidden:` — and
   `_unpainted_ids()` short-circuits to `None` for any non-layered view at
   `:1596`. Token gone, line 36 → 17 cells.
6. `#map-pagination` is content-height (`app.py:3375`, `max-height: 3;
   overflow: hidden`, no `height`); `#map-body` is `1fr`. Strip 2 rows → 1 row,
   canvas region +1 row. *(observed: region snapshot)*
7. Nothing re-renders. `refresh_canvas` neither schedules
   `_declare_after_layout` nor resets `_declared_for`; `on_resize` does not fire
   (no screen resize). *(observed: zero further events after seq 24)*

**The decisive observation** is intervention C: keep the overflow token in
outline (monkeypatch `_unpainted_ids` to answer) — the layered header charge left
fully in place — and the gap goes to **0 at all four loss sizes**, because the
region never moves (region_h 5 → 4 at (30,16), 8 → 7 at (24,20)):

```
MODE C: strip keeps the overflow token in outline
  terminal region_h  cs_h  held   re  gap
  (24, 20)        7     5     5    5    0
  (30, 16)        4     3     3    3    0
  (32, 16)        4     3     3    3    0
  (34, 14)        2     1     1    1    0
```

Corroborating intervention B: force one extra repaint after settle, change
nothing else — gap 0 at all four, and `held` differs from the pre-reflow render
at exactly those four sizes and nowhere else.

```
MODE B: one forced extra repaint after settle
  terminal region_h  cs_h  held   re  gap  held==render(pre_h)
  (24, 20)        8     6     6    6    0                False
  (30, 16)        5     4     4    4    0                False
  (32, 16)        5     4     4    4    0                False
  (34, 14)        3     2     2    2    0                False
  (35, 14)        3     2     2    2    0                 True
  (40, 16)        5     4     4    4    0                 True
```

And intervention A (baseline): the widget's held text is **byte-identical** to
`OutlineRenderer().render(graph, _view_state(w, h_pre_reflow))` at **all nine**
sampled sizes. A stale `h` alone reproduces the screen exactly.

### Operator-visible consequence, restated correctly

At (30,16), `    - Contabilidad` is missing because of the **stale write**
(`held=3`, `re=4`). The layered-header over-charge costs a *further* line
(`region_h=5` vs `cs_h=4`) — at this size that one is invisible, because
`Sistema ERP Legacy  8 nodos · 2 sin acta` is 40 cells and wraps to 2 physical
rows at width 30, so 4 logical lines already fill all 5 physical rows
(`phys(held)=5` in mode B). At (40,16) it is the other way round: gap 0, but
`cs_h=4` where 5 logical lines would fit in 5 physical rows — a whole node line
lost to the header charge with no gap at all.

---

## 4. Alternatives checked and EXCLUDED

**(i) The handed hypothesis — layered's header height under-gives `h` in outline
at narrow widths.** EXCLUDED as the cause of the gap, on four independent
observations:

- **It cancels.** `gap = re − held`, and `re` is produced at the *same*
  `_canvas_size()` that priced `held`'s frame would be. A wrong constant in
  `_canvas_size` moves both sides equally and cannot appear in their difference.
  The gap is, by construction, a staleness measure.
- **The charge does not move across the event.** `header_rows` is 2 at (30,16),
  (32,16), (34,14) and 3 at (24,20) — *identical* before and after the reflow
  (trace seq 23 vs seq 26). Only `region.height` changed.
- **It does not select the four.** The same charge is levied at all eleven
  sizes, including `header_rows=2` at 40/50/60/80/118 where the gap is 0.
- **Intervention C removes the gap while leaving the charge in place.**

It *is* a real second defect — see §6 — just not this one.

**(ii) The settle loop terminating one pass early / `_declared_for` holding a
stale region so the final render used a stale `h`.** EXCLUDED: the trace shows
the loop ran 3 passes, all in layered, all at the same settled region, and
terminated with `region == _declared_for` — correct behaviour. The stale write
is produced *after* the loop has legitimately finished, by `refresh_canvas`,
which is not part of the loop and never re-arms it.

**(iii) `on_resize` racing `_declare_after_layout`, last write wins with an older
render.** EXCLUDED: exactly one `on_resize` per run, logged at seq 5, before the
map's settle passes and long before `o`. Zero resize events after the `o` press
at every size.

**(iv) `_apply_region_visibility` changing the region after the last render.**
EXCLUDED: `#map-rail` and `#map-inspector` regions are byte-identical across all
three snapshot instants at every size; the only widgets that move are
`#map-pagination` (shrinks) and `#map-body`/`#map-canvas` (absorb its row).

**(v) The canvas widget's own auto-height feeding back into the region.**
EXCLUDED: `#map-canvas` height follows `#map-body` (`1fr`), and at (24,20) the
content written was 5 lines while the region went to 8 — the height is not a
function of the canvas's content. It changed because a *sibling's* content height
changed.

**(vi) `_view_state(w, h)` carrying something other than `h` that changes the
emitted line count, or outline's `lines[:h]` cut behaving unlike layered's.**
EXCLUDED: intervention A — the held text equals a render that differs from the
probe's re-render in `h` and nothing else, byte for byte, at all nine sizes. If
any other field of `ViewState` were implicated the two would differ somewhere.

---

## 5. What a correct fix must satisfy — properties, not a patch

- **P1 (the invariant).** After any operator action has settled, for every view
  and every size: `canvas.render()` must equal
  `renderer.render(graph, _view_state(*_canvas_size()))`. This is the `gap == 0`
  oracle; it is view-independent, size-independent, and it is what the four loss
  sizes violate.
- **P2 (the seam is the ordering, not the arithmetic).** No write to
  `#map-canvas` may be the last write for a frame whose region changed
  afterwards. `refresh_canvas` currently writes the canvas at `:2370` and the
  content-height strip at `:2425`. Any fix that only corrects `h` leaves the
  ordering intact and the defect reachable by any other content-height sibling —
  `#map-minimap`, `#map-toast` and `TabStrip` are all named in this file as
  content-driven strips.
- **P3 (physical rows, not logical lines).** `h` is a logical-line budget but the
  region is physical rows, and outline's *body* lines wrap too. Rendering outline
  at `h = region.height` **overflows** at 6 of 9 sampled sizes — measured
  physical rows vs region: (24,20) 10 vs 8, (30,16) 6 vs 5, (32,16) 6 vs 5,
  (34,14) 4 vs 3, (28,14) 4 vs 3, (35,14) 4 vs 3. "Charge the active renderer's
  header instead of layered's" is therefore **not sufficient and not safe on its
  own**: the correct property is that the emitted text occupies ≤ `region.height`
  physical rows, and occupies *exactly* `region.height` whenever the view still
  has content to show.
- **P4 (both directions).** The reverse switch is currently worse than the one
  the ground-truth table sampled. outline → layered (`o` twice) writes layered
  content at outline's larger `h` into a region that then *shrinks*, and it
  **OVERFLOWS by 1 physical row at (24,20), (30,16), (32,16), (34,14)** — clipped
  content, not blank rows. A fix validated only on the first `o` is half a fix.

  ```
    terminal            instant region_h  cs_h phys(held)  strip_h            verdict
    (30, 16)    mounted-layered        4     3          4        2               fits
    (30, 16)    after-o-outline        5     4          4        1    underfills by 1
    (30, 16)   after-oo-layered        4     3          5        2     OVERFLOWS by 1
  ```

- **P5 (the trap for the negative controls).** `B-55` — making `_unpainted_ids`
  answer for outline — would **incidentally close the reflow trigger** (that is
  literally intervention C). If B-55 lands first, a test that presses `o` and
  asserts `gap == 0` **passes without the staleness defect being fixed at all**.
  Any acceptance arm for this mechanism must either run before B-55, or drive the
  region change through a different content-height strip, or assert P1 directly
  after a forced region change.

---

## 6. One mechanism or two? — **Two defects, and the seven zeros have four
different reasons, only three of which are honest controls.**

**Defect 1 — stale final write on a post-write region reflow.** Explains the
`gap` column exactly: it fires wherever the strip's layered line (36 cells) wraps
and its outline line (17 cells) does not, i.e. terminal width ≤ 34. Sampled
widths 24, 28, 30, 32, 34 all reflow; 35, 40, 50, 60, 80, 118 do not. Threshold
confirmed at the boundary: `strip_h` is 2 → 1 at width 34, and 1 → 1 at width 35.

**Defect 2 — layered's header height charged in outline** (question (a)). Levied
at all eleven sizes. Invisible where outline's own line wrapping happens to
consume the row anyway ((30,16), (32,16), (35,14)); **visible as a wasted body
row with `gap == 0`** at (40,16) and (50,16) (`cs_h=4`, `region_h=5`,
`phys(held)=4` — a fifth logical line would fit in 5 physical rows); visible as
2 wasted rows at (24,20).

The seven zero-gap sizes, by reason:

| size | gap | why it is 0 | usable as a negative control for defect 1? |
|---|---|---|---|
| (35,14) | 0 | strip fits on one row in both views; region never moves | **yes, honest** |
| (40,16) | 0 | same | **yes** — and it is a *positive* control for defect 2 (1 row wasted) |
| (50,16) | 0 | same | **yes** — same, positive for defect 2 |
| (60,20) | 0 | region stable **and** content saturated (`cs_h=10` > 9 lines the fixture has) | weak — insensitive to a gap of 1 |
| (80,24) | 0 | layered strip has **no** overflow token either (0 hidden), so nothing to drop; also saturated | vacuous |
| (118,34) | 0 | same | vacuous |
| **(28,14)** | **0** | **the region DID reflow, 2 → 3, exactly like the loss sizes** — but `_canvas_size`'s `region.height <= rows` guard (`app.py:1510`, `header_rows=3` at width 28) clamps `h` to 1 on *both* sides, masking it | **NO — this is a positive case of the mechanism reporting zero.** Treating it as a negative control is wrong |

So: the four loss sizes share one mechanism. The seven zeros do not share one
reason with each other, and one of them ((28,14)) is not a zero-gap case at all —
it is the mechanism, hidden by a second defect's guard. Three of the seven
((60,20), (80,24), (118,34)) cannot distinguish a fixed system from a broken one
because the 8-node fixture saturates the frame.

---

## 7. Boundary (control 11) — what this analysis saw, and what it did not

**Saw, directly:**

- Every `MapScreen._canvas_size()` call in the run, with the canvas region,
  `content_size.width`, the `header_rows` value it used, and the `h` returned.
- Every `Static.update()` targeting `#map-canvas`, with the region at that
  instant and the line count and first/last line of what was written.
- Entry and exit of `_declare_after_layout`, `on_resize` and `refresh_canvas`,
  with `_declared_for` at both ends.
- Every id'd widget's region at three instants: before `o`, immediately after the
  `press("o")` coroutine returned, and after `pause()`.
- The composited frame once, at settle, via `rows_in(screen, canvas.region)`.

**Did not see, and therefore did not verify:**

- The compositor's painted cells at the intermediate instants. The claim that the
  canvas write at `:2370` precedes the strip write at `:2425` within one pass is
  read from the source plus the before/after region snapshots — I did not observe
  a frame painted between them.
- Anything between `canvas.update()` and the settled region: I sampled at
  `press` return and at `pause()` return, not at each layout pass in between. If
  more than one layout pass occurred there, I would not have distinguished them.
- A real terminal. Everything is Textual's headless `run_test`. Terminal-specific
  wrapping (ambiguous-width glyphs, a non-UTF8 console) could shift the 34/35
  width threshold.
- Fixtures other than `legacy`, and views other than `layered`/`outline`.
  `_unpainted_ids` short-circuits for **radial** too (`app.py:1596`), so the same
  reflow trigger is predicted for `r`; **I did not measure it.**
- Entry points into outline other than pressing `o` after a mount in layered —
  e.g. a session restored already in outline, or `o` pressed while a search query
  is active (the query echo also changes the strip's height).
- Whether any *layered*-only action that changes the hidden count from N to 0
  (fold/navigate) reproduces defect 1 within layered. The mechanism predicts it;
  I did not measure it.
- The width threshold: derived from a cell count of the strip line (36 cells with
  token, 17 without) plus the sampled sizes 34 and 35 bracketing it. It is not a
  width sweep.
