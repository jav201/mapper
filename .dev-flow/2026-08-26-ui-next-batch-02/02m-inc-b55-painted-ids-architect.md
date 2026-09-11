# 02m · Inc-B55 — what shape the painted-set declaration takes

**Verdict: `B`, and the increment is MIS-CUT.** Keep `painted_ids(graph, state)` module-level, one per
view module. `lane.py` does not belong in this increment. `D` is rejected because its sole
justification — three geometries in one module — is manufactured by including `lane.py`, which
`B-55`'s own requirement text does not ask for and which no operator can reach. `C` is rejected
because it re-opens the sealed A3 *and* silently disarms the very tripwire built to force this
decision.

Three findings change the increment more than the shape question does, and all three were found by
measurement rather than by reading notes. They are in §7.

---

## 1. Recommendation

**`B`, re-cut into two increments, with `lane.py` dropped.**

| | shape | files |
|---|---|---|
| **Inc-B55a** | `painted_ids(graph, state)` in `views/outline.py`; dispatch arm in `app.py` | `views/outline.py`, `mapper/app.py` — **2** |
| **Inc-B55b** | `painted_ids(graph, state)` in `views/radial.py`; second dispatch arm | `views/radial.py`, `mapper/app.py` — **2** |
| **not cut** | `views/lane.py` | **0** |

A single 3-file increment (`outline.py`, `radial.py`, `app.py`) also fits the cap of 4 and is an
acceptable coordinator choice. I recommend the split because the two renderers' costs are
**qualitatively** different — outline's declaration is a wrap-aware row model, radial's is a
cell-ownership replay — and because each one independently reddens the A-98 tripwire, which is worth
one gate each rather than one gate for both.

---

## 2. Your claims: verified, refuted, corrected

### VERIFIED — constraint 1, the `runtime_checkable` hazard is real

`mapper/views/state.py:104-116` declares `IRenderer` with exactly one member, `render`. Executed
(`C:\Users\jjgh8\clde\arch_b55_probe.py`), a two-member Protocol flips **all six** shipped renderers:

```
  LayeredRenderer          isinstance(IRenderer)=True  isinstance(ITwoMember)=False
  OutlineRenderer          isinstance(IRenderer)=True  isinstance(ITwoMember)=False
  RadialRenderer           isinstance(IRenderer)=True  isinstance(ITwoMember)=False
  LaneRenderer             isinstance(IRenderer)=True  isinstance(ITwoMember)=False
  HybridLaneRenderer       isinstance(IRenderer)=True  isinstance(ITwoMember)=False
  RailTimelineRenderer     isinstance(IRenderer)=True  isinstance(ITwoMember)=False
```

Independently derived; I did not read `02j`'s probe before running mine. The consumer that goes red is
`tests/test_a3_census.py:382`, `assert all(isinstance(cls(), IRenderer) for cls in classes)`, over a
**derived** class set.

**One correction to the docstring's own framing.** The blast radius is test-side, not product-side:
`isinstance(..., IRenderer)` appears **exactly once in the tree**, at `tests/test_a3_census.py:382`,
and **zero times in `mapper/`**. So "flips all six shipped renderers to `isinstance -> False`" is
true but reads as a runtime break; it is a census break. That does not rescue `C` — the census is the
structural guard `state.py:108-115` says it is, and reddening a guard to ship a feature is the wrong
direction — but the record should not overstate it.

### VERIFIED — constraint 4, the side-channel cross-contamination hazard is real and live today

`mapper/app.py:1201` holds one long-lived `self.renderer = LayeredRenderer()`. `action_export_svg`
(`app.py:3079`) calls `self._current_renderer()` at `:3084` — the **same instance** — and renders it
at `size = self.size or self.app.size`, while `refresh_canvas` (`app.py:2351`, renderer fetched at
`:2354`, rendered at `:2363`) renders it at `self._canvas_size()`. Two sizes, one instance, no reset. The docstring's stated reason holds
verbatim. A data-member Protocol is worse than the docstring says: I measured `isinstance` against a
data-member `runtime_checkable` Protocol returning `False` before any render and `True` after — an
`isinstance` whose answer depends on whether the object has been drawn yet.

### VERIFIED — your pre-gate numbers, reproduced exactly on an independent probe

`C:\Users\jjgh8\clde\arch_b55_measure.py`, `legacy` (8 nodes) at 30x6, full-title oracle:

```
  LayeredRenderer           0/8       OutlineRenderer           5/8
  RadialRenderer            2/8       LaneRenderer              2/8
  HybridLaneRenderer        2/8       RailTimelineRenderer      1/8
```

Identical to yours in all six cells.

### VERIFIED — your self-reported oracle mismatch, and it is more interesting than a probe defect

`painted_ids(graph, state)` returns `{'erp'}` at 30x6 while the frame contains only `Siste` — five
cells of the eighteen-character title `Sistema ERP Legacy`. Your full-title oracle is strictly
harsher than the product predicate `_title_image(...).strip()` (`layered.py:309-323`). You were right
to flag it, and it is **not** a defect in your probe. It is a live architectural gap: see §7.3.

### REFUTED — "the crux: `lane.py` holds THREE renderer classes"

True as a statement about the module. **False as a statement about this increment's scope**, on three
independent pieces of evidence.

1. **`B-55`'s requirement text does not name lane.** `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:8544`:
   *"MEASURED HOLE, carried under `B-55` — **`outline` and `radial`** hide nodes and declare nothing."*
   Then `:8547-8548`: *"Executed full-title traces at `30x6` on `legacy`: **outline 5/8** (3 hidden,
   undeclared), **radial 2/8** (4 hidden, undeclared)."* Two renderers, named, measured. Lane appears
   nowhere in the carry.

2. **The three lane renderers are unreachable, and a test pins it.** `LaneRenderer`,
   `HybridLaneRenderer` and `RailTimelineRenderer` are named nowhere outside `mapper/views/` —
   `mapper/views/__init__.py:2` re-exports them and nothing else in `mapper/` imports them.
   `MapScreen._current_renderer()` (`app.py:1695-1700`) can return exactly three instances, all
   constructed at `app.py:1201-1203`: `LayeredRenderer`, `OutlineRenderer`, `RadialRenderer`. This is
   already pinned as an equality by
   `tests/test_inc3_census.py::test_a89_the_reached_set_is_pinned_so_wiring_lane_up_pulls_it_in`
   (`:229-246`), whose docstring states the intent: *"Pinned as an EQUALITY so that the increment
   which wires one of them up turns this red and inherits the obligation."* The tree already has the
   mechanism that will force lane to declare **on the day it becomes reachable**. Declaring for it now
   is speculative work for dead code, and it spends the leverage of that tripwire early.

3. **I can trace where `lane.py` entered the cut, and it is a routing artefact.** `01-requirements.md:5985`
   defines **Inc-5** as *hit painting* in `views/outline.py`, `views/radial.py`, `views/lane.py` —
   three files, owner `LLR-N07.2.2b`. `B-55` was then routed to Inc-5 for budget convenience
   (`:8555-8557`: *"routed to `Inc-5`, the only increment that already owns all three of those files
   … and can pay for it with no budget"*). The file set `{outline, radial, lane}` belongs to **hit
   painting**. `B-55` inherited the *list* rather than the *scope*. This increment then inherited the
   list from the routing note. The "three geometries in one module" crux is downstream of that
   inheritance, not of `B-55`.

**Consequence: with `lane.py` out, `outline.py` and `radial.py` each hold exactly one renderer class,
and one module-level `painted_ids(graph, state)` answers for each. The crux dissolves, and with it
the only argument for `D`.**

---

## 3. Attacking `D`, as asked

I evaluated `D` as a peer. It loses, and it loses for a reason more decisive than the concerns you
listed.

**The fatal one: with lane out of scope, `renderer` is an unused parameter in three modules out of
three.** `layered.py`, `outline.py` and `radial.py` each contain exactly one renderer class. Under
`D` the first parameter would be ignored by every implementation that ships. The justification would
be a future in a module this verdict deliberately excludes. That is an abstraction built for a
single hypothetical caller — and it is not free: it breaks every existing call site
(`mapper/app.py:1600`; `tests/test_fold.py:751`, `:1048`; `tests/test_overflow.py:141`, `:177`,
`:200`, `:260`, `:268`), i.e. churn on the two test files that sit closest to the A-98 tripwire, to
buy nothing measurable.

**On your specific concerns, for the record:**

- *Does identity-dispatch inside the module relocate the `getattr` smell?* **No — this attack fails.**
  A total `if r is X … elif r is Y … else: raise` is materially better than `getattr`: it is
  AST-visible, greppable and has an else-branch. The A-98 ruling's objection is to a probe that
  answers "declares nothing" and "declaration is broken" with the same `None`, and a raising
  type-switch does not do that. `D` is not *unsound*; it is *unmotivated*.
- *Unknown renderer → empty frozenset?* Under a correctly written `D` it raises. But see §5 — under
  **every** shape including `D`, the raise is currently laundered into `None` by `app.py:1601-1602`.
  That hazard is real and shape-independent, and `D` does not fix it.
- *Does it break `layered`'s call site and the A-98 arms?* It breaks the call sites (8 of them, listed
  above). It does **not** break `test_a98_the_screen_imports_painted_ids_by_name_never_by_getattr`,
  because that arm reads `alias.name`, which is pre-`as` and signature-blind.
- *Is an unused parameter a defect or the price of a uniform contract?* Neither — because the
  contract does not need to be uniform. See §8: under per-module dispatch, `lane.py` can later export
  `painted_ids(renderer, graph, state)` **while the other three keep the two-argument form**, since
  `app.py` already dispatches per arm. `D`'s forward-compatibility argument is therefore worth zero:
  nothing is foreclosed by not paying for it now.

---

## 4. Exact signatures, and where the geometry knowledge is reached

```python
# mapper/views/outline.py  (NEW, module-level, pure)
def painted_ids(graph: Graph, state: ViewState) -> frozenset[str]: ...

# mapper/views/radial.py   (NEW, module-level, pure)
def painted_ids(graph: Graph, state: ViewState) -> frozenset[str]: ...

# mapper/views/layered.py:326  (UNCHANGED)
def painted_ids(graph: Graph, state: ViewState) -> frozenset[str]: ...
```

**`layered.py` — unchanged.** Geometry reached through `_geometry(graph, state)` (`:199`), shared with
`render` so the two cannot drift. The predicate is `_title_image(...).strip()` non-empty (`:309-323`).

**`outline.py` — the module has no shared pass today and must grow one.** `render` (`:47-166`) is one
monolithic method; the walk is a closure. The painted set is a function of the pre-order traversal
from `graph.root_id` and the `lines[:h]` cut (`:161`). To meet the standard `layered` already holds —
`render` and `painted_ids` share **one** pass so they cannot drift — the walk must be extracted to a
module-level helper returning the ordered node list, which both then consume. **The cut is not
`i + 1 < h`; see §7.1.** Two structural facts the declaration must carry, both measured:
- the walk starts at `graph.root_id`, so a node not reachable from the root is **never** painted at
  any size. Measured: a graph of 9 nodes with one orphan renders 9 outline lines at 200x200 and the
  orphan's title is absent; `LayeredRenderer` paints it and `layered.painted_ids` declares it. Outline's
  hidden set therefore has a structural component independent of the viewport.
- `render` reads only `state.selected_id`, `state.h` and `state.hits` (`outline.py:49`, `:52`). It
  never reads `w`, `pan_x`, `pan_y` or `folded`. So fold contributes nothing to outline's hidden set,
  and width contributes through wrapping only — §7.1.

**`radial.py` — the hard one; a placement filter is the rejected mutant.** Geometry is `pos`, built by
`place()` (`:132-165`), then pills are drawn in `for nid in graph.nodes` order (`:210-262`) with
`cv.put`, which is last-write-wins (`mapper/canvas.py:103-105`, `self.cells[(x, y)] = (ch, style)`)
and records no owner. Deriving the painted set from `pos` is **`M-N06.3-b` verbatim, the
placed-not-painted mutant `02j` rejected for `layered`**. Measured:

```
  30x  6: placed=8/8  full-label in frame 2/8    <- pos over-declares by 6 of 8
  50x 12: placed=8/8  full-label in frame 7/8
  80x 24: placed=8/8  full-label in frame 8/8
```

and the pills genuinely destroy one another:

```
  30x 6: pills partly OVERWRITTEN by a later pill: ['cont','erp','fin','inv','nom','rrhh']  (6 of 8)
  50x12: pills partly OVERWRITTEN by a later pill: ['erp']
  80x24: pills partly OVERWRITTEN by a later pill: []
```

So radial's `painted_ids` is **not a filter over placement — it is a replay of cell ownership**. The
only drift-proof construction is to extract the pill loop into a module-level pass that records, per
cell, which node last wrote it, and have both `render` and `painted_ids` consume that one pass. This
is a restructure of `radial.py`, not an addition, and it is why I recommend splitting it out.

---

## 5. Failure mode for an unknown renderer — and the hazard that defeats every shape

**This is the most important implementation constraint in this verdict, and the brief does not list
it.** `mapper/app.py:1596-1603` reads:

```python
if self._current_renderer() is not self.renderer:
    return None
w, h = self._canvas_size()
try:
    painted = painted_ids(self.graph, self._view_state(w, h))
except Exception:
    return None
return frozenset(self.graph.nodes) - painted
```

`except Exception: return None` is total. Under **any** multi-renderer shape — `B`, `C` or `D` — a
registry miss that raises is caught here and returned as `None`, and `None` means *"this view declares
nothing"* (`:1569`, `:2142`). **The loud failure is laundered into exactly the silent skip A-98
exists to prevent.** Whatever shape ships, the resolution must happen **outside** that `try`.

**Two layers, because the runtime cannot both fail loud and keep the app alive.** `_unpainted_ids`
runs inside the message pump via `refresh_canvas`, and the docstring at `:1587-1592` correctly argues
an escape there turns a contained degradation into a dead app. The resolution is to separate the two
failure kinds, which are not alike:

- **A layout failure is data-dependent** — some graphs and sizes, not others. It stays caught and
  returns `None`, which is honest: the frame was never laid out.
- **A missing declaration is a code defect** — deterministic, present at every frame, independent of
  data. It must not be caught.

So: resolution raises, outside the `try`; and a **census arm makes it unreachable in a shipped build**
by deriving the screen's renderer attributes rather than listing them, so a fourth renderer added
without a declaration is a RED TEST before the app ever runs. That is where "loud" actually reaches a
human. If someone ships past a red test, the app crashes rather than lying — the correct ordering of
harms for a feature whose entire purpose is not lying.

`frozenset()` is never an acceptable answer for "unregistered", and `C-55`'s load-bearing-emptiness
concern is exactly right: `frozenset()` is a **legitimate** return here. `outline.py:63` and
`radial.py:117` both return a degraded frame above `MAX_RENDER_NODES`, where *nothing* is painted and
`frozenset()` is the truth. An unregistered renderer returning the same value is indistinguishable
from a map that genuinely hid all of itself.

---

## 6. What `app.py`'s dispatch looks like

Imports — by name, aliased for symmetry. `alias.name` is pre-`as`, so
`test_a98_the_screen_imports_painted_ids_by_name_never_by_getattr` (`:390-417`) stays green; I checked
its AST logic rather than assuming.

```python
from .views.layered import (..., painted_ids as layered_painted_ids)
from .views.outline import OutlineRenderer, painted_ids as outline_painted_ids
from .views.radial  import RadialRenderer,  painted_ids as radial_painted_ids
```

Dispatch by identity — the same `is` form `_current_renderer` already uses, run in reverse, and total:

```python
def _painted_ids_for(self, renderer):
    """The function this renderer declares its painted set through.

    Identity, not `getattr`, per A-98 / ruling 02j: a probe answers "this view
    declares nothing" and "this view's declaration is broken" with the same
    `None`.  RAISES for a renderer with no declaration, and the raise is the
    point -- `frozenset()` is a legitimate return here (both degraded paths
    return it), so an unregistered renderer answering with one is a lie the
    strip would paint as "nothing hidden".
    """
    if renderer is self.renderer:
        return layered_painted_ids
    if renderer is self.outline_renderer:
        return outline_painted_ids
    if renderer is self.radial_renderer:
        return radial_painted_ids
    raise LookupError(f"no painted_ids declared for {type(renderer).__name__}")

def _unpainted_ids(self) -> frozenset[str] | None:
    # OUTSIDE the guard, and that is load-bearing: `except Exception` below
    # would turn a missing declaration into `None`, which reads as "this view
    # declares nothing" -- the silent skip A-98 exists to prevent.
    declare = self._painted_ids_for(self._current_renderer())
    w, h = self._canvas_size()
    try:
        painted = declare(self.graph, self._view_state(w, h))
    except Exception:
        return None
    return frozenset(self.graph.nodes) - painted
```

The guard at `:1596` (`if self._current_renderer() is not self.renderer: return None`) is deleted; it
*is* the one-view restriction `B-55` closes. Both consumers — the strip (`:2143`) and, per §7.2, the
canvas header — then read the same pass.

---

## 7. Three findings that change the increment more than the shape does

### 7.1 Outline's row model is `B-61` one renderer over — measured, 15 of 15 narrow configurations

The obvious model is "node at pre-order index `i` is painted iff `i + 1 < h`". Measured at `w=200` it
is exact at every height (h = 2, 3, 5, 6, 9, 20 — all MATCH). Measured against **real wrapping**
through `Console.render_lines`, the same width the widget wraps at, it **over-declares at every narrow
configuration tested**:

```
  w=20 h=3: logical=3 physical=5  model=2 real=1  OVERDECLARE=1
  w=20 h=5: logical=5 physical=7  model=4 real=2  OVERDECLARE=2
  w=20 h=8: logical=8 physical=11 model=7 real=5  OVERDECLARE=2
  w=25 h=6: logical=6 physical=7  model=5 real=4  OVERDECLARE=1
  w=30 h=6: logical=6 physical=7  model=5 real=4  OVERDECLARE=1
                                          ... 15 of 15 configurations over-declare
```

This is `B-61` verbatim: *"a formula standing in for a measurement"*, the defect `header_rows`
(`layered.py:398-440`) was built to fix, and its docstring already records the mechanism — *"Rich
WORD-WRAPS, so a line that `ceil` prices at 2 rows can occupy 3."* Outline's rows are wide enough to
wrap on real canvases: at `w=20`, 3 of 9 `legacy` rows and 7 of 8 `anidado` rows exceed the width;
at `w=40` and above, none do.

**It is also a pre-existing render defect, not only a declaration gap.** `outline.py:161` cuts
`lines[:h]` counting **logical** rows while the widget shows **physical** rows, so at `w=20, h=3`
outline emits 3 logical lines that occupy 5 physical rows on a 3-row canvas. Outline believes content
fit that the canvas cannot show. Closing `B-55` for outline honestly requires fixing that cut, which
is scope this increment did not name.

### 7.2 Both declaring surfaces are in scope, not one

`layered.py:520` shows `render` itself computing `len(graph.nodes) - len(painted)` and painting the
`▽ N fuera de vista` token into its own header (`_header_line`, `:360-396`). The strip is the
*second* surface. `_declare_after_layout` (`app.py:1609`) exists precisely because the two must
agree — its docstring: *"Repaint BOTH declaring surfaces once layout is real — B-56 and B-60."*

If `outline` and `radial` gain `painted_ids` but not a header token, the strip will declare *"N fuera
de vista"* while the canvas header beside it says nothing — and `LLR-N06.3.3` makes silence mean
"nothing is hidden". That is `B-60` reintroduced in two views. Each renderer's `render` must paint its
own token. This fits inside the per-increment file budget but roughly doubles the work per file.

### 7.3 "Painted" is not one predicate, and shipping three definitions is a known-shipped defect class

`layered` declares `erp` painted at 30x6 on the strength of `Siste` — 5 of 18 title cells — because
its predicate is `_title_image(...).strip()` non-empty. Outline's natural predicate is "the node's
line survives the cut". Radial's is "at least one cell of the pill survives overwrite and the frame
bound". Left unnamed, `B-55` ships **three different definitions of painted** behind one operator-facing
numeral.

`mapper/views/state.py:63-66` records that this exact failure already shipped once, in the adjacent
concept: *"This replaced a `query: str` the renderer had to interpret for itself, which is how two
definitions of 'hit' came to ship at once and disagree by `{id, meta, attachments}`."* The same
mechanism, one concept over.

**I am not recommending one predicate be forced on all three geometries** — a pill and an indented
line are not commensurable, and a shared formula would be the same "formula standing in for a
measurement" error. I am recommending the predicate be **named and stated per module in the
docstring**, in the form `layered` already uses, and that the requirement record which reading
`HLR-N06.3`'s numeral carries. A per-view predicate that is *written down* is defensible; three
undocumented ones summed into one integer are not.

---

## 8. Tests that go RED, and why each is intended

| test | file:line | verdict |
|---|---|---|
| `test_a98_exactly_one_renderer_declares_its_painted_set` | `tests/test_inc3_census.py:387` | **RED — intended, this is the tripwire firing.** `painted_ids_exporters()` becomes `{layered, outline}` after Inc-B55a and `{layered, outline, radial}` after Inc-B55b, so the equality with `{mapper.views.layered}` breaks. Its docstring states the design: *"the day a second renderer joins, this goes red and forces the decision rather than letting the guarantee quietly widen — or quietly not."* Repair is to widen the pinned set **and amend the docstring** to record that `B-55` closed outline and radial, and that `lane` stays out because it is unreachable — pinned by `test_a89…` (`:229`), which remains the tripwire for the day lane is wired up. |
| `test_a98_the_participation_census_input_is_non_empty` | `:369` | green — unaffected. |
| `test_a98_the_screen_imports_painted_ids_by_name_never_by_getattr` | `:390` | green — verified against its AST logic. **But it has a control gap and should be widened in the same increment:** it collects imports only from modules whose name `endswith("layered")` (`:404`), so nothing stops the implementer reaching `outline`/`radial` by `getattr` as long as the layered import still exists. Widen the module filter to the `views` package. Test-side change; no source-file cost. |
| `test_a89_the_reached_set_is_pinned_so_wiring_lane_up_pulls_it_in` | `:229` | green under my recommendation (lane untouched). **Note it would also stay green under the brief's 4-file cut**, because it counts *reached renderer classes*, not `painted_ids` exporters — so it offers no protection against the lane work being written and wasted. |
| `test_llr_n07_2_3_every_renderer_satisfies_the_protocol` | `tests/test_a3_census.py:382` | green under `B`. Under `C` this goes **RED for all six renderers**, which `02j` classifies as trigger A3 — stop-and-escalate, not designable-around. |
| `tests/test_overflow.py`, `tests/test_fold.py` call sites | 8 sites, listed §3 | green under `B` (signature unchanged). All 8 would need editing under `D`. |

Baseline confirmed green before this analysis: `pytest tests/test_inc3_census.py -k "a98 or a89"` → **6 passed**.

---

## 9. The `layered.py:326` record

**`B` does not contradict it, so it is not amended — it is extended.** Both clauses were re-verified
against today's code (§2) and both hold. What has changed is that the shape is now **plural**, and the
record should say why lane is not in the set. Suggested addition, appended below the existing
paragraph, leaving its wording intact:

```
    RE-VERIFIED at Inc-B55, and the shape is now one such function PER VIEW
    MODULE -- `outline` and `radial` export their own.  Both clauses above still
    hold: measured, a second Protocol member still flips all six renderers to
    `isinstance -> False`, and the export site (`app.py:2354`) still renders this
      same long-lived instance (`app.py:3084`) at a different size than the canvas
    does (`app.py:2354`).  `lane.py`
    exports NO such function and that is deliberate, not an oversight: its three
    renderer classes are named nowhere outside `mapper/views/`, so they reach no
    operator-visible sink and can hide nothing from anyone.  The day one is wired
    up, `test_a89_the_reached_set_is_pinned_so_wiring_lane_up_pulls_it_in` goes
    red and that increment inherits this obligation -- including the question this
    signature does not answer, which is how ONE module-level function serves THREE
    geometries.  Nothing here forecloses the answer: `app.py` dispatches per arm,
    so `lane.py` may take a different signature than its siblings without
    migrating them.
```

I am **not** supplying `C`'s amended wording, because I am not recommending `C`. If the coordinator
overrules to `C`, the amendment must state at minimum: (i) that the A3 was re-opened deliberately and
by whom; (ii) that `test_a3_census.py:382` was reddened as a consequence rather than as a regression;
(iii) that `test_a98_exactly_one_renderer_declares_its_painted_set` **stops measuring anything** under
`C` and was rebuilt to sweep classes — see §10, risk 1.

---

## 10. Risks

| # | risk | severity | mitigation / note |
|---|---|---|---|
| 1 | **Under `C`, the A-98 tripwire silently goes vacuous.** `painted_ids_exporters()` (`:355-365`) sweeps *modules* for a module-level function. A Protocol member or per-class method adds none, so the census stays `{layered}` and stays **green while the guarantee widens** — a control that quietly stopped measuring the thing it is named for. | **high** | Chief reason to reject `C` beyond the A3. If `C` is ever chosen, the census must be rebuilt to sweep classes **in the same increment**. |
| 2 | **The `except Exception` at `app.py:1601` launders a loud failure into `None`.** Shape-independent; applies to `B`, `C` and `D`. | **high** | §5. Resolution outside the guard, plus a derived census arm over the screen's renderer attributes. |
| 3 | **Radial's declaration ships `M-N06.3-b` if derived from `pos`.** Measured wrong by 6 of 8 at 30x6. | **high** | §4. Requires cell-ownership replay; the reason Inc-B55b is split out. |
| 4 | **Outline's declaration ships `B-61` if derived from logical row index.** Measured over-declaring at 15 of 15 narrow configurations. | **high** | §7.1. Must price wrap through `Console.render_lines`, as `header_rows` does. |
| 5 | **Two surfaces, not one.** Declaring only through the strip reintroduces `B-60` in two views. | medium | §7.2. `render` must paint its own token in both files. |
| 6 | **Three unnamed predicates behind one numeral.** The `query`/"two definitions of hit" failure, one concept over. | medium | §7.3. Name the predicate per module in the docstring. |
| 7 | Doing lane anyway "while we're here" | medium | Its acceptance can only ever be a unit test against an unreachable class — never an operator-visible AT. It also spends `test_a89`'s leverage early. |
| 8 | `B` needs a signature change on the day lane is wired up | **low — this is `B`'s strength, not its cost** | Per-arm dispatch means lane can take `(renderer, graph, state)` **without migrating its siblings**. Nothing is foreclosed. This is what removes `D`'s last argument. |

---

## 11. What I could NOT determine — boundaries of this analysis

- **I did not run the full suite.** I baselined `tests/test_inc3_census.py -k "a98 or a89"` (6 passed)
  and read `test_a3_census.py`. Other arms may bind on `outline`/`radial` internals in ways a
  geometry extraction would disturb; `tests/test_views_hits.py` and `tests/test_darkside_census.py`
  both reach into these modules and I read only enough of them to know that. **Unmeasured.**
- **I measured renderers directly, not through the live screen.** My `w`/`h` are renderer arguments.
  The screen derives them through `_canvas_size()` with chrome subtraction, and `02j`'s own
  correction (`tests/inc3_support.py:52-60`) records that *"the unit is the terminal, not the
  renderer"* and that conflating them made a docstring look false. My narrow-width numbers are
  therefore **directionally** sound and **not** the terminal sizes an operator reaches. The
  wrap-overdeclare finding (§7.1) needs re-measuring through the real screen before it is quoted as
  a configuration count.
- **I did not verify the fold interaction for radial.** `radial.render` does not read `state.folded`;
  I confirmed that for `outline` by reading `:49`/`:52` but did not sweep radial's state reads
  exhaustively.
- **Two fixtures only** (`legacy`, `anidado`), and `anidado` only for the width overflow probe.
- **I cannot see intent outside this repo.** If a coordinator ruling elsewhere has already put
  `lane.py` in this increment's scope for a reason not written into `01-requirements.md`, my §2
  refutation is wrong and I would want to see that ruling. On the evidence in the tree, it is not
  there.
- **I found no evidence of a second writer.** Working tree clean at `335d0e4`; no stray lock or
  editor files.

---

## Evidence checklist

- [x] **Constraints stated explicitly** — five, taken from the brief and each re-verified against code, not inherited (§2).
- [x] **At least 2 alternatives considered** — four: `B`, `C`, `D`, and the re-cut. Each with an executed measurement (§2, §3).
- [x] **Recommendation tied to constraints** — `B` because the crux is manufactured by out-of-scope `lane.py` (`01-requirements.md:8544`, `test_inc3_census.py:229`), `C` because it re-opens the A3 (probe, `test_a3_census.py:382`) and voids the tripwire (`:355-365`), `D` because its parameter is unused in 3 of 3 shipping modules.
- [x] **Risks listed** — 8 rows, §10, four rated high.
- [x] **Cost estimated** — file cost per increment (2 + 2, vs the cap of 4); the real cost is the geometry extraction, measured as a restructure in `radial.py` and a wrap-pricing change plus a render-cut fix in `outline.py` (§4, §7.1).
- [ ] **Diagram** — not included; the flow is a single call chain, unchanged in topology by this ruling, already drawn at `01-requirements.md:4860-4873` (`FLOW: overflow_declaration`). The only topology change is one extra dispatch arm, given as code in §6.
- [x] **What would change the recommendation** — stated in §12 below.
- [ ] **Two-layer traceability** — **not re-derived, and this is a gap I am declaring rather than papering over.** This ruling amends no requirement and creates no story, but §7.1 and §7.2 assert defects (`B-61`-class in `outline.py`, `B-60`-class across both views) that have no `AT-NNN` and no `US→AT` chain today. If the coordinator accepts §7, those need requirement rows before Inc-B55a opens. Owed.

## 12. What would change this recommendation

1. **Evidence that `lane.py` is in `B-55`'s scope by ruling** — a coordinator decision I could not see,
   or a decision to wire a lane renderer into `app.py` in this same batch. Either makes the three-geometry
   crux real, and **`D` becomes the correct shape immediately** — it is the right answer to the question
   the brief asked; the question is just not this increment's.
2. **A batch-level decision to re-open the A3.** `02j`'s own reversal trigger (i). Then `C` is the
   cleaner long-run shape, and §10 risk 1 must be paid in the same increment.
3. **A second consumer outside `app.py` needing the painted set.** `02j`'s reversal trigger (iii), still
   the correct trigger for promoting this to the interface.
4. **Measurement refuting §7.1 through the real screen** — if the wrap over-declaration is unreachable at
   terminal sizes an operator can produce, outline collapses back to a genuinely small addition and the
   single 3-file increment becomes the better cut.
