# 02j · Inc-3 — how the renderer declares its painted set

**Architect ruling.** Read-only pass at `954f8f3`, branch `feat/ui-next-batch-02`.
Every claim below carries an executed probe. Probe sources are in the session scratchpad;
each transcript is pasted verbatim.

---

## RULING

**A module-level pure function in `mapper/views/layered.py`:**

```
painted_ids(graph: Graph, state: ViewState) -> frozenset[str]
```

sharing one private `_geometry(graph, state)` pass with `LayeredRenderer.render`, which is
refactored onto that same helper so the two cannot drift.

- **`IRenderer` gains nothing.** `mapper/views/state.py` is not touched *by this mechanism*.
- **Not a Protocol member. Not a method. Not a mutable attribute. Not a richer return type.**
- **`MapScreen` imports it by name** and calls it behind an explicit, greppable branch —
  never `getattr(renderer, "painted_ids", None)`.
- **`folded` reaches it only through `ViewState.folded`.** The screen's overflow helper computes
  `set(graph.nodes) - painted` and **never** subtracts a fold count, which is `LLR-N06.3.1`'s
  statement read literally. This resolves the ambiguity in that LLR's `Touched symbols` line:
  "consumes `MapScreen.folded`" means *`MapScreen.folded` is what the screen puts into the
  `ViewState` it hands to `painted_ids`*, not that the helper takes a second set and differences it.

### Does this re-fire trigger A3?

**NO.** `mapper/views/state.py` is byte-identical under this mechanism. `IRenderer.render`'s
signature, its member set, and its return type are all unchanged. No module that consumes the
renderer interface (`app.py`, `export.py`, `tests/test_a3_census.py`) sees a changed interface.
The sealed PDR `#D5a` A3 is not re-opened.

---

## Why — each candidate, priced against an executed probe

### (a) A second Protocol member `painted_ids(graph, state)` — **REJECTED, it IS an A3**

`IRenderer` is `runtime_checkable` (`state.py:74`), and `runtime_checkable` `isinstance` checks
**member presence**. Adding a member makes all six shipped renderers stop satisfying the Protocol.

```
$ python scratchpad/probeA.py
shipped IRenderer (one member):
  LayeredRenderer          isinstance -> True
  OutlineRenderer          isinstance -> True
  RadialRenderer           isinstance -> True
  LaneRenderer             isinstance -> True
  RailTimelineRenderer     isinstance -> True
  HybridLaneRenderer       isinstance -> True

candidate (a): IRenderer + painted_ids as a SECOND PROTOCOL MEMBER:
  LayeredRenderer          isinstance -> False
  OutlineRenderer          isinstance -> False
  RadialRenderer           isinstance -> False
  LaneRenderer             isinstance -> False
  RailTimelineRenderer     isinstance -> False
  HybridLaneRenderer       isinstance -> False

  positive control FakeFull      isinstance -> True
```

The probe returns the other answer (the positive control), so it is not rigged.

`tests/test_a3_census.py:316` asserts `all(isinstance(cls(), IRenderer) for cls in classes)` over a
**derived** class set (`renderer_classes()`, `:249-268`, "every class in `mapper/views/` that
defines `render`"). Six renderers turn red the moment the member lands. That is *the definition of*
trigger A3 — an interface another module consumes, changed. **Stop-and-escalate, not designable-around.**

**The obvious escape hatch does not work either.** A Protocol member with a default body does not
rescue structurally-conforming classes:

```
PROBE A2 - defaulted Protocol member
  NonInheriting (shipped shape) isinstance -> False
  Inheriting    (explicit base) isinstance -> True
  Inheriting().painted_ids(None,None) -> set()
```

The default only reaches classes that **explicitly inherit** `IRenderer`. The six shipped renderers
are structural, not nominal. Paying for the default therefore costs edits to `views/lane.py`,
`views/outline.py`, `views/radial.py`, `views/layered.py` **and** `views/state.py` — five files, of
which two are outside Inc-3's ratified budget — to buy a method that returns `set()`, i.e. `MUT-1`,
the pure-deletion mutant the requirement already names as green-on-the-weak-oracle. **Rejected twice
over.**

### (b) A mutable attribute the renderer sets as a side effect of `render` — **REJECTED, measured wrong**

`MapScreen` holds **one long-lived** `LayeredRenderer` (`app.py:1116`) and calls `render` on it from
two sites with **different** `ViewState`s: the canvas repaint (`app.py:1418`, `w = size.width -
_chrome_width()`, `h = size.height - 8`) and the SVG export (`app.py:1800-1806`,
`replace(self._view_state(size.width, size.height - 10), focus_owner="")`). A third site
(`app.py:739`, the import-preview screen) constructs its own instance. The side channel is
cross-contaminated by design:

```
$ python scratchpad/probeC.py
after canvas repaint  30x6   last_painted = ['erp']  (n=1)
after `e` export      140x45 last_painted = ['alm','cont','erp','fin','inv','nom','pres','rrhh']  (n=8)

the screen's overflow helper now reads 8 painted for a canvas showing 1.
declared_total would be 8 - 8 = 0; the truth at 30x6 is 7.
```

**One `e` press makes the indicator declare `0 hidden` on a canvas hiding 7.** That is US-N06's
promise inverted, produced by a plain operator sequence, on the named fixture. It also breaks
`LLR-N06.1.1`'s acceptance — "the renderer is a pure function of `(graph, state)`" — because the
call now has an observable effect that outlives it.

### (c) The screen re-deriving the set from renderer-exported geometry — **REJECTED, it is `M-N06.3-b`**

`_tree_layout` (`layered.py:74`) returns *placed* positions. The `lines[:h]` slice at `layered.py:302`,
the `body_h` clamp at `:173` and the `avail = w - 2` column bound at `:160` each discard placed nodes
after the fact.

```
PROBE B - _tree_layout keys vs the visible set, fixtures/legacy (N=8)
  30x6:   |_tree_layout keys|= 8  |visible|= 1  |traced in real painted text|= 1
          layout-minus-visible=['alm','cont','fin','inv','nom','pres','rrhh']
  50x12:  |_tree_layout keys|= 8  |visible|= 8  |traced|= 8   layout-minus-visible=[]
  140x45: |_tree_layout keys|= 8  |visible|= 8  |traced|= 8   layout-minus-visible=[]
```

**Wrong by 7 of 8 at `(30, 6)`** — which is `HLR-N06.3`'s own named "hidden by viewport" configuration.
The probe agrees at `140x45`, so it can return the other answer. This is the requirement's
`M-N06.3-b` verbatim, and it is rejected for the reason the requirement already gives.

### (d) `render` returning a richer object — **REJECTED, it IS an A3, and a wider one**

`IRenderer.render`'s declared return type is `Text` (`state.py:86`). `mapper/export.py:15` declares
`def save_svg(text: Text, path: Path | str) -> None` and `app.py:1424` does `canvas.update(text)`.
`tests/test_a3_census.py:128` pins **35** arg-ful `render` call sites as an equality, not a floor.
Changing the return type changes an interface consumed by `app.py`, `export.py` and the census —
a strictly larger A3 than (a).

---

## What the other five renderers owe: **NOTHING — and that is a declared, measured carry**

They implement no new member, inherit nothing, and are not edited for this mechanism.
`views/outline.py` stays in Inc-3's budget for its `A-89`/`B-47` coercion work only.

**The carry, stated with numbers rather than waved past.** `outline` and `radial` also hide nodes,
and under this ruling neither declares:

```
PROBE D - do the NON-layered renderers also hide nodes?
  outline  30x6 : full-title traces 5/8      (3 nodes hidden, undeclared)
  outline  50x12: 8/8      outline 140x45: 8/8
  radial   30x6 : full-title traces 2/8      (4 nodes hidden, undeclared)
  radial   50x12: 7/8      radial  140x45: 8/8
```

So `HLR-N06.3`'s promise is kept in the **default** view and silently unkept in the other two.
Three things pay for that, and Inc-3 must ship all three:

1. **`MapScreen`'s branch is explicit and named, never a `getattr` probe.** The screen already
   hard-codes its renderer roster at `_current_renderer()` (`app.py:1269-1274`, a three-way branch
   on `self.outline_mode` / `self.radial_mode`), so a static import adds no coupling that is not
   already there — and it is greppable, AST-visible and type-checkable, whereas a `getattr` fallback
   is a silent-skip generator of exactly the kind this batch keeps catching.
2. **A pinned participation census**, in the idiom `tests/test_a3_census.py:108-141` already
   establishes: derive the set of modules under `mapper/views/` exporting `painted_ids`, assert it is
   non-empty **before** it is evaluated, and assert set **equality** with `{mapper.views.layered}`.
   When a later increment adds outline, the pin goes red and forces the decision instead of letting
   it drift.
3. **The gap is carried under a named id to Inc-5**, which already owns `views/outline.py`,
   `views/radial.py` and `views/lane.py` (`PDR #D5` row 5) — the only increment where it costs no
   budget at all.

**Zero further file-budget cost.** `painted_ids` lands in `views/layered.py` and the screen helper in
`app.py`; both are already in Inc-3's `A-89` five.

---

## How the AT observes it without becoming vacuous

**Product and oracle share no computation.** The product computes `declared_painted_set` from
`layered.py::_geometry`. The oracle computes `traced_set` from the **composited frame** —
`_rows_in(screen, canvas.region)` (`tests/test_repair_layout.py:74`), string-containment of the
clipped-and-visible title image, explicitly not `render().plain` and explicitly not `_tree_layout`'s
keys. The oracle never imports `_geometry` or `painted_ids`. `PRED-2 ∧ PRED-3` is then a genuine
comparison of two independently-derived sets, which is what makes it set equality rather than an
identity.

### The mutations that redden a test of this mechanism — executed

Legacy fixture, 8 nodes, at two of the four named AT configurations (`folded` arms are not
executable today; `ViewState.folded` does not exist yet — the gap `LLR-N06.3.2` already carries
to `TC-032`).

```
    config mutation   |declared|  |traced|  PRED-1  PRED-2  PRED-3
50x12     CORRECT             8         8   True   True   True
50x12     MUT-1               0         8   True   True   False
50x12     MUT-A               8         8   True   True   True
50x12     MUT-B               8         8   True   True   True
30x6      CORRECT             1         1   True   True   True
30x6      MUT-1               0         1   True   True   False
30x6      MUT-A               8         1   True   False  True
30x6      MUT-B               0         1   True   True   False
```

- **`MUT-1`** — `painted_ids` returns `frozenset()`. Reddened by **`PRED-3`** at both sizes.
- **`MUT-A`** — `painted_ids` returns `_tree_layout(...).keys()`, i.e. placed-not-painted
  (`M-N06.3-b`). Reddened by **`PRED-2`**, `8 ⊄ 1`.
- **`MUT-B`** — `painted_ids` keeps the row restriction and drops the column restriction
  (`0 <= cx + 2 + j < avail`), the "natural reading" `HLR-N06.3:2240-2254` warns about.
  Reddened by **`PRED-3`**.

**The load-bearing finding for whoever writes the AT: at `(50, 12)` — the "nothing hidden"
configuration — `MUT-A` and `MUT-B` are GREEN on all three predicates.** Only the `(30, 6)`
viewport-overflow configuration discriminates them. The requirement's four-configuration table
(`:2196-2199`) is not belt-and-braces; **two of the three mutants survive an AT that runs only the
first configuration.** Inc-3's AT must run all four, and `AT-015`/`AT-016` must fail if any
configuration is skipped rather than passing on the subset.

---

## What Inc-3 must build

1. **`mapper/views/layered.py`** — extract `_geometry(graph, state)` returning
   `(pos, card_w, avail, body_h, level_h)` from the block currently inline at `:151-173`;
   `render` calls it (output must stay byte-identical); add module-level

   ```
   def painted_ids(graph: Graph, state: ViewState) -> frozenset[str]
   ```

   applying **both** restrictions — row (`0 <= y < body_h` and `header + y < h`, the `lines[:h]`
   slice at `:302`) **and** column (`0 <= cx + 2 + j < avail`). Reference shape and its 0-mismatch
   positive control: `01d-unpark-measurements.md:65-98` and `:131-134`.
2. **`mapper/views/state.py`** — `ViewState.folded: frozenset[str] = frozenset()`,
   `pan_x: int = 0`, `pan_y: int = 0`. Additive defaulted fields, explicitly **never** an A3 per
   `state.py:17-20`. **See escalation 1 below: this file is not on Inc-3's declared list.**
3. **`mapper/app.py`** — `MapScreen._unpainted_ids()` computing `frozenset(self.graph.nodes) -
   painted_ids(self.graph, state)` for the *same* `state` object `refresh_canvas` just rendered
   with; returns `None` when `self._current_renderer() is not self.renderer`, and
   `_pagination_text` keeps its reserved-affordance content in that case. No fold count is
   subtracted anywhere.
4. **Tests** — the participation census pinned to `{layered}`; the four-configuration `AT-015`/
   `AT-016`; the three mutants above as documented red arms.

---

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| `_geometry` extraction changes `render`'s bytes | high — Inc-2's gate idiom is byte-identity | golden-text arm over the 56-size sweep before/after the extraction; it is a pure move |
| `painted_ids` and `render` drift apart in a later edit | medium | they share one `_geometry`; a test asserting `painted_ids ⊆ traced` at the four configurations catches drift as `PRED-2` |
| outline/radial hide nodes and declare nothing (measured: 3/8 and 4/8 at 30x6) | **medium — a real hole in US-N06's promise** | declared carry to Inc-5, plus the pinned participation census so it cannot go quiet |
| The screen's explicit branch hard-codes `layered` into the overflow path | low | reversible; promoting a module function to a Protocol member is an additive migration in a future batch, not a one-way door |
| `pan_x`/`pan_y` land in `ViewState` but `_geometry` ignores them | medium | `painted_ids` must consume the same pan offsets `render` does, or the declared set is right for an un-panned canvas only |

**What would change this ruling:** (i) a decision to re-open the A3 at batch level, which makes the
Protocol member the cleaner long-run shape; (ii) a requirement that outline/radial declare in Inc-3
rather than Inc-5, which makes the polymorphic form worth its A3; (iii) evidence that a second
consumer outside `app.py` needs the painted set, which would argue for putting it on the interface
rather than in one module.

---

## Two findings to escalate — both independent of this ruling

**1. `mapper/views/state.py` is a sixth Inc-3 source file and is not on the declared list.**
`01-requirements.md:5653` lists Inc-3 as `app.py`, `widgets/rail.py`, `views/layered.py`,
`keymap.py`, `views/outline.py` — **5, declared breach `A-89`**. But `LLR-N06.1.1:1696` names
`ViewState.pan_x` / `ViewState.pan_y` and `LLR-N06.2.1:1782` names `ViewState.folded`, all three
`NEW — created in Phase 3`, all three owned by Inc-3 LLRs. `views/state.py` must be edited for
Inc-3 to ship at all. That is a **6-file undeclared breach** — the exact defect class `#D5`
§4.1(a) caught on Inc-7 ("an undeclared one is exactly what V9 exists to catch"). My mechanism
neither creates nor worsens it; it needs zero files beyond the six. **Coordinator ruling owed
before Inc-3 opens.**

**2. `AT-015`/`AT-016` are non-discriminating on their first configuration alone.** Table above:
at `(50, 12, ())` the placed-not-painted mutant and the dropped-column mutant are both green on
all three predicates. The four-configuration table must be enforced as a **cardinality assertion in
the test**, not left to the implementer to run.

## Evidence checklist

- [x] Constraints stated explicitly — sealed A3, purity rule, six renderers, headless boundary, 5-file budget.
- [x] At least 2 alternatives considered — four, (a)-(d), each with an executed rejection.
- [x] Recommendation tied to constraints — probe A/A2 (A3), probe C (purity), probe B (soundness).
- [x] Risks listed — table above, five rows plus two escalations.
- [x] Cost estimated where relevant — file-budget cost 0 beyond the already-owed six.
- [ ] Diagram — not included; the flow is a single call chain already drawn at `01-requirements.md:4860-4873` (`FLOW: overflow_declaration`).
- [x] What would change the recommendation — stated.
- [x] Two-layer traceability — not re-derived here; this ruling amends no requirement and creates no story.
