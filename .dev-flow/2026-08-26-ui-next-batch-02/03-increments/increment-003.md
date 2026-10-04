# Increment 003 — US-N06 «escala» — pan, fold, overflow, and `LLR-COERCE.2` as widened

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `003` |
| Lane | none — serial batch |
| Requirement(s) | `HLR-N06.1` (`LLR-N06.1.1`, `LLR-N06.1.2`) · `HLR-N06.2` (`LLR-N06.2.1`, `LLR-N06.2.2`, `LLR-N06.2.3`) · `HLR-N06.3` (`LLR-N06.3.1`, `LLR-N06.3.2`, `LLR-N06.3.3`) · `LLR-COERCE.2` as widened by `A-89` / `B-47` |
| Acceptance | `AT-011` · `AT-012` · `AT-013` · `AT-014` · `AT-015` · `AT-016` · `AT-017` · `TC-030` … `TC-040` |
| NOT in scope | `LLR-N06.2.4`, `AT-046`, `AT-047` — Inc-4 |
| Protocol | **FULL** — declared 6-file breach, `A-89` + `A-97` |
| Agent | `software-dev` |
| Date | 2026-08-28 |
| Base | `954f8f3`, branch `feat/ui-next-batch-02` |

---

## 1 · What changed

**The canvas now knows what it is not showing, and says so as a number that reconciles.** Measured
pre-state (`M-5`): the layered view painted a readable title for at most 7 nodes regardless of graph
size, declared the full node count in its header, and painted **no** overflow declaration at all.

- **`painted_ids(graph, state)`** — a module-level pure function on `views/layered.py`, sharing one
  private `_geometry(graph, state)` pass with `LayeredRenderer.render` so the two cannot drift. Per
  the `02j` ruling: not a `Protocol` member (that flips all six shipped renderers to
  `isinstance -> False`), not an attribute `render` sets (cross-contaminated by the export call
  site), not the screen re-deriving from `_tree_layout` (wrong by 7 of 8 at `30x6`).
- **Pan** — `ViewState.pan_x` / `pan_y`, translated in `_geometry.place`, driven by the real
  `H`/`J`/`K`/`L`, clamped to `[0, max(0, E - W)]`, and declaring `borde del territorio` on the
  hint line at either edge rather than no-opping silently.
- **Fold** — `MapScreen.folded` is the single owner. `OutlineRail.collapsed` and `OutlineRail.toggle`
  are **deleted**; the rail renders fold through `show(graph, cursor, folded)` and no longer owns it.
  The canvas paints `▐ ▸ <rama> +N` where the subtree used to be, with the bar and the hit count in
  `WARN`. Folding a leaf declares `nada que plegar` / `este nodo no tiene descendientes` instead of
  painting a pill reading `+0`.
- **The declaration** — `▽ N fuera de vista`, in `INK` (`PDR-addendum-3 #D28`: `WORDMARK` measures
  1.85 : 1 against `GROUND` and vanishes entirely on the `WINDOWS` rung), painted on the canvas
  header and on `#map-pagination`, both from the one `painted_ids` pass. Absent entirely at zero.
- **Coercion (`B-47`)** — `layered._clip` coerces before it truncates, so all six `_fit` sites
  inherit it; `views/outline.py` coerces its title and meta. Executed at `954f8f3`, `LayeredRenderer`
  (the **default** view) and `OutlineRenderer` both leaked `0x01`, `0x200b` and `0x202e` into
  `export.save_svg`, so `AT-009`'s guarantee held in one of three views.

### One defect this increment found and fixed, because `HLR-N06.3` is an identity

**`refresh_canvas` was asking the renderer for a frame that does not exist.** `h = size.height - 8`
is not the canvas region: at a 50x20 terminal it asked for **12 rows into a region that holds 8**, so
four nodes were drawn into a void — hidden, with nothing declaring them, which is US-N06's promise
inverted. `_canvas_size()` now derives `h` from the canvas widget's own region, charging one row for
the header's wrap. Over a nine-size sweep the shipped arithmetic made the declared painted set
disagree with the composited frame at **five** sizes; the region-derived one agrees at **all nine**.

---

## 2 · Files modified

| File | Kind | Change |
|---|---|---|
| `mapper/views/state.py` | source | `pan_x`, `pan_y`, `folded` — three additive defaulted fields |
| `mapper/views/layered.py` | source | `_geometry`, `painted_ids`, `pan_extent`, `_title_image`, fold pruning + pills, the declaration, `_clip` coerces |
| `mapper/views/outline.py` | source | `B-47` coercion only — title and meta |
| `mapper/app.py` | source | `folded`/`pan_x`/`pan_y`, `_canvas_size`, `_clamp_pan`, `_reclamp_pan`, `_pan`, four `action_pan_*`, `_unpainted_ids`, `action_collapse_branch` reworked, `_view_state` carries three fields |
| `mapper/widgets/rail.py` | source | `show(graph, cursor, folded)`; `collapsed` and `toggle` **deleted** |
| `mapper/keymap.py` | source | four `view`-group rows: `H` `J` `K` `L` |
| `fixtures/anidado.mmd` · `anidado_nodos.yml` | fixture | **new** — written by `MapStore.save`, loaded by `MapStore.load` |
| `tests/inc3_support.py` | test | **new** — fixtures and the painted-trace oracle |
| `tests/test_pan.py` · `test_fold.py` · `test_overflow.py` · `test_inc3_census.py` | test | **new** |
| `tests/test_repair_depth.py` · `test_rail.py` · `test_keymap.py` · `test_key_dispatch.py` · `test_a3_census.py` · `test_darkside_census.py` | test | pin updates and the rail attribute rename |

| Count | Value |
|---|---:|
| **SOURCE files** | **6 — DECLARED BREACH** |
| Test files | 9 (uncapped) |
| Fixture files | 2 (outside the count) |

**The six-file breach, and why it cannot be cut smaller.** `01-requirements.md:5653` declares it:
`app.py`, `widgets/rail.py`, `views/layered.py`, `keymap.py`, `views/outline.py` (`A-89`, absorbing
`B-47`), `views/state.py` (`A-97`). `views/state.py` is not optional — `LLR-N06.1.1:1696` names
`ViewState.pan_x`/`pan_y` and `LLR-N06.2.1:1782` names `ViewState.folded`, all three
`NEW — created in Phase 3`, and the increment cannot ship without them. It is **not** an A3:
`state.py:17-20` states the rule in the module's own docstring, all three fields carry defaults, and
`ViewState()` still constructs with no arguments. **No seventh file was taken.** `mapper/views/radial.py`
was touched only by the mutation battery and restored — `git status` reports it clean, and its
content is byte-identical to `HEAD` modulo line endings (verified by sha256 over the normalised bytes).

---

## 3 · How to test

```bash
cd <repo root>
set PYTHONUTF8=1
python -m pytest -q -m "not slow" -p no:randomly
python -m pytest -q -m "slow" -p no:randomly
python -m pytest -q --collect-only -o addopts=
python -m ruff check .
python -m pytest -q tests/test_pan.py tests/test_fold.py tests/test_overflow.py tests/test_inc3_census.py
```

---

## 4 · Test results

| Lane | Result |
|---|---|
| fast | `784 passed, 17 deselected in 83.25s` — exit 0 |
| slow | `17 passed, 784 deselected in 21.46s` — exit 0 |
| `--collect-only -o addopts=` | `801 tests collected` |
| `ruff check .` | **28** — the baseline figure, **ZERO NEW** |
| `ruff check mapper/ tests/` | **28** — same set |

Baseline at `954f8f3`, reproduced before starting: `720 passed, 17 deselected` · `17 passed, 720
deselected` · `737 collected` · `28` ruff. Every figure matched.

### Signed-balance test ledger — DERIVED, not counted by hand

`post = base − deleted + added` → **`801 = 737 − 0 + 64`** ✓

Executed by collecting node ids from a **detached `git archive` of `954f8f3`** in the scratchpad and
diffing the sorted sets against the working tree — so `deleted = 0` is a measurement, not a claim:

```
base 737  post 801
DELETED (in base, not in post):   (none)
ADDED per file:
     23  tests/test_inc3_census.py
     15  tests/test_pan.py
     10  tests/test_overflow.py
      8  tests/test_fold.py
      4  tests/test_keymap.py          <- parametrised over the seat
      4  tests/test_key_dispatch.py    <- parametrised over the seat
```

The last two were not written by hand: both modules parametrise over `KEYMAP`, so the four seat rows
**created eight arms that check them**. `tests/test_rail.py::test_rail_collapses_a_branch` was
rewritten in place off `show` and keeps its node id, which is why the deleted column is empty rather
than `1 removed, 1 added`.

---

## 5 · Predicted-red set vs actual — trigger `B3` was FIRED

Predicted **by derivation, before the suite was run**, from the touched symbols: `collapsed` /
`toggle` deleted, `show` widened, the declaration painted where nodes are hidden, new `WARN` lines,
four seat rows.

| # | Predicted | Actual | Verdict |
|---|---|---|---|
| R1 | `test_rail.py` arms calling `rail.toggle` — **2 nodes** | `test_rail_collapses_a_branch` — **1 node** | **over-predicted**: both calls live in one node |
| R2 | rail digests, the 4 non-empty `collapsed` arms | `test_c53_the_rail_renders_legacy_identically_to_master[collapsed1..4]` | exact |
| R3 | the `_shipped_visible_rows` equivalence arm | `test_tc_r30_visible_rows_agrees_with_the_shipped_recursive_implementation` | exact |
| R4 | `rail.show(graph, root_id)` 2-arg site | `test_tc_r30_the_indent_cap_cannot_change_a_rendered_row` | exact |
| R5 | `MASTER_LEGACY_DIGESTS[(LayeredRenderer, 140, 8)]` | same, and **only** that key | exact |
| R6 | the hue census totality pin | `test_hue_census_every_severity_and_busy_site_is_classified` | exact |
| R7 | a keymap seat fence | `test_keymap_completeness_guard` | exact |
| R8 | "possibly `test_app.py`" keybar arms | `test_key_dispatch.py::test_at_n03h_the_whole_seat_matches_its_specification` | **right class, wrong file** |

**Predicted 8 classes, 11 actual nodes, zero unpredicted reds.** Two prediction errors, both
recorded rather than smoothed: R1 counted nodes instead of call sites, and R8 named the wrong module
for the whole-seat pin. A third batch of reds appeared later, after the new tests landed — the two
`test_a3_census.py` cardinality pins and one `test_app.py` focus arm — which were **not** predicted
because they are caused by the increment's own new test files, not by its source change.

### Digest re-capture — ONE key, with its reason

**`("LayeredRenderer", 140, 8)` only.** It is the only one of the four golden sizes at which `legacy`
has an unpainted node (4 of 8; the other three paint 8 of 8), so the only one at which the overflow
declaration is painted at all. Bounded **before** the re-capture, by diffing row by row against
`git show HEAD:` of the renderer:

```
row counts: 8 8
rows that differ: [0]                      <- the header, and nothing else
row0 prefix identical: True
row0 suffix added: '  ▽ 4 fuera de vista'
span delta: one new INK span over that suffix, plus the offset shift it forces
```

**Everything else held byte-identical and was NOT re-captured**: `LayeredRenderer` at `140x45`,
`80x24`, `300x120`; all four `OutlineRenderer` keys; all four `RadialRenderer` keys; **all five
`MASTER_RAIL_DIGESTS`**. The rail digests holding is the load-bearing one: the `collapsed -> folded`
rename changes what the test assigns and changes **nothing** the rail paints, which is exactly what a
byte-identity guard exists to establish.

---

## 6 · The five derived censuses

Every one asserts its input set non-empty **before** it evaluates anything. A hand-listed set is the
defect class, not a shortcut past it.

### 1 · Truncators (`LLR-COERCE.2`) — `tests/test_inc3_census.py`

Two stages: the AST derives every `(str, int) -> str` in the tracked product sources, then each
candidate is **executed** on a string longer than the width it is given and kept only if it came back
shorter. Non-empty-before: `assert derived` precedes every property. Derived set, pinned as an
equality: `{darkside.fit, layered._clip, layered._fit}` — **3**. Quantified over 6 widths, with
hostile inputs built from `chr(0x...)` at test time; the split-at-width arm drives a source balanced
at `U+202E` … `U+202C` and asserts **0** unterminated overrides survive the cut.

### 2 · Renderer to operator-visible sink (`A-89` / `B-47`)

Derived structurally, not by name: a renderer is *reached* iff a tracked product module **outside**
`mapper/views/` names its class — so `views/__init__.py` re-exporting one is excluded by where it
lives, and the day `app.py` names `LaneRenderer` that renderer enters the census automatically.

> **`02j`'s claim about `views/lane.py` was verified mechanically, not adopted.** Re-derived over the
> tracked tree at `954f8f3`: `LaneRenderer`, `HybridLaneRenderer` and `RailTimelineRenderer` are
> named **nowhere** outside `mapper/views/` — zero product call sites, confirmed. Pinned as an
> equality so the increment that wires one up goes red and inherits the obligation.

Reached set `= {LayeredRenderer, OutlineRenderer, RadialRenderer}`, each rendered at 3 sizes with a
hostile graph: **0** coerced code points, 9 of 9 checks. Executed pre-state for contrast:
`Layered` and `Outline` leaked `['0x1', '0x200b', '0x202e']`; `Radial` leaked none.

### 3 · Supersession of `OutlineRail.collapsed` / `toggle`

AST over **both** `mapper/**` and `tests/**` (the enumeration that stopped at `tests/test_rail.py`
missed the production call site `app.py:1259` and the byte-identity guard
`test_repair_depth.py:1055`). **Non-empty-before is established by a positive control on the
instrument**: fed the shipped pre-state's own shapes — the production `toggle` call, a `collapsed`
write, a `collapsed` read, and a docstring that only *mentions* both — it returns **4** sites and
excludes the docstring, which is also the control for choosing AST over grep. Then, over the real
tree: **`[]`**, plus `not hasattr(OutlineRail, "toggle")` and `"collapsed" not in vars(OutlineRail())`.

### 4 · Participation in `painted_ids` (`A-98`)

Input set asserted `>= 5` modules under `mapper/views/` before the equality is evaluated; exporters
asserted non-empty; then **set equality with `{mapper.views.layered}`**. Plus an AST arm asserting
`app.py` imports `painted_ids` **by name** and contains **zero** `getattr(..., "painted_ids")`
probes — a `getattr` fallback answers "this view declares nothing" and "this view's declaration is
broken" with the same `None`.

### 5 · Keymap

`duplicate_chords()` → `[]` on **exit**, and on **entry** by re-running the shipped detector's logic
over `KEYMAP` minus this increment's own four rows (a transcript records what someone ran; this
records what the detector says). Plus the seat diff below, and an arm asserting every new row
dispatches to an `action_*` method that exists with the right signature — the help overlay once
bound `enter -> run_selected`, a method `HelpScreen` never defined.

### Inc-3's own four-row seat diff (`C-D25a`)

| Declared row | key | action |
|---|---|---|
| 1 | `H` | `pan_left` |
| 2 | `J` | `pan_down` |
| 3 | `K` | `pan_up` |
| 4 | `L` | `pan_right` |

Asserted **equal** to the entry/exit difference of `bindings_for("map")`: entry 27, exit 31,
`exit − entry == DECLARED_DIFF`, `entry − exit == ∅`. There is no row budget on Inc-3 —
`PLAN.md:244`'s "one changed row plus two added rows" is an equality on `D10`'s **own** diff
(`PDR-addendum-3 #D25`). Executed basis at `954f8f3`: `duplicate_chords() -> []`, map scope binds 27
chords, and of the uppercase letters only `A`, `I`, `R`, `X` were taken.

---

## 7 · Mutation battery — 21 arms, per-arm verdicts

Run from the session scratchpad, never from the repo tree. Arm count asserted (`len(ARMS) == 21`)
before any verdict was trusted; an arm the harness cannot apply is reported `UNSEEN` and counted as
green rather than skipped. Mutations are described by position and operation only.

| Arm | Verdict | Detail |
|---|---|---|
| `painted_ids` returns the empty set (`MUT-1`) | **RED** | 6 failed |
| `painted_ids` returns the layout's keys (`MUT-A`, `M-N06.3-b`) | **RED** | 4 failed |
| column restriction dropped in the trace predicate (`MUT-B`) | **RED** | 2 failed |
| row bound dropped, column kept | **RED** | 3 failed |
| row bound uses the raw `h` instead of the `lines[:h]` slice | **RED** | 1 failed |
| fold hides only direct children, not the subtree | **RED** | 2 failed |
| leaf fold silently no-ops instead of declaring | **RED** | 1 failed |
| the rail keeps a fold set of its own again | **RED** | 2 failed |
| the clamp returns its input unchanged | **RED** | 8 failed |
| the clamp drops its lower bound | **RED** | 5 failed |
| the edge no-ops without painting the hint | **RED** | 2 failed |
| the renderer ignores the pan offsets | **RED** | 2 failed |
| the truncator stops coercing | **RED** | 7 failed |
| `outline` paints the raw ficha title again (`B-47`) | **RED** | 1 failed |
| a second module exports `painted_ids` | **RED** | 1 failed |
| a pan row leaves the seat | **RED** | 4 failed |
| the rail keeps a `collapsed` alias | **RED** | 1 failed |
| the screen adds a fold count instead of differencing one set | **GREEN → fixed → RED** | see below |
| a pill is painted for every folded id, nested ones included | **GREEN → fixed → RED** | see below |
| the clamp drops its `E < W` guard | **GREEN — EQUIVALENT MUTANT** | see below |
| coerce *after* truncating instead of before | **GREEN — EQUIVALENT MUTANT** | see below |

### The two arms that stayed green because a predicate was inert — rewritten, not re-argued

**The screen could have summed and nothing would have caught it.** `LLR-N06.3.1`'s "not a sum"
property was asserted only against `painted_ids`, one layer *below* `MapScreen._unpainted_ids`. The
mutant that made the screen add a fold count survived, because the only surface reading that helper
is painted *from* that helper and both sides of the comparison moved together. Closed by `TC-039`,
which drives `anidado` at `FOLD = {ops, log}` through the shipped screen and asserts
`_unpainted_ids() == the true hidden union` and `< the naive sum`. Re-run: **RED**.

**A pill nested inside another fold was untested on the painted surface.** `TC-034`/`TC-035` read
`painted_ids` without rendering, and `AT-014`'s folds are all siblings. Closed by `TC-040`, which is
`LLR-N06.3.2`'s own transcript run through the real renderer: **one** painted pill reading **4**, not
two summing to **6**. Re-run: **RED**.

Both re-runs used a **binary-mode** harness; restores proven by sha256 returning to the pre-mutation
value (`93f120a60cc50cae` and `9e2c911fbf9eaa6e`).

### The two equivalent mutants — proved by execution, not argued away

- **The `E < W` guard is provably redundant.** `max(0, min(o, max(0, E−S)))` and
  `max(0, min(o, E−S))` were swept over **98,642** `(offset, extent, span)` triples: **0**
  disagreements. The outer `max(0, …)` already absorbs the negative bound. The inner one is kept for
  readability; it is dead, and saying so is more useful than a green arm nobody explains.
- **The coercion *ordering* is unobservable for this coercion, and the requirement's stated threshold
  is therefore WEAK.** `darkside.plain` is a 1:1 `str.translate` over 235 code points, all
  replacements length 1 — so it distributes over slicing. Coerce-then-truncate and
  truncate-then-coerce were compared over **380,000** `(string, width)` pairs: **0** disagreements.
  The stated threshold `t(plain(s), n) == plain(t(s, n))` was **already green on the uncoerced
  `layered._fit` at `954f8f3`** — I re-executed it before writing any code. It is kept because it is
  the requirement's threshold and because it is *not* vacuous for a truncator measuring display
  cells, but the arms that actually discriminate are "0 coerced code points in the output" (**RED**,
  7 arms) and the split-at-width arm. This is flagged in the test's own docstring, not just here.

---

## 8 · Risks

1. **`outline` and `radial` hide nodes and declare nothing** — measured at `30x6` on `legacy`: 5 of 8
   and 2 of 8 traced. `HLR-N06.3`'s promise is kept in the **default** view and silently unkept in the
   other two. Declared, pinned by census 4, routed to Inc-5 as `B-55`. Not closed here.
2. **`_canvas_size` now depends on a Textual widget's region.** That is what makes the declaration
   true, and it couples the screen's render size to layout timing — see `B-56` below.
3. **`HEADER_ROWS = 2` has a measured band where it is wrong, and the fix round found it WIDER than
   this said on both axes.** Recorded here as "a third row below 30 columns"; measured over 70
   configurations it is **four** rows at `w = 20` at every node count, and three rows at `w = 30`
   from **n >= 40**. Re-pinned, derived rather than asserted as a literal, and carried as `B-61`
   (§11.6). Latent, not live: the `declared == traced` identity still holds at every canvas width
   probed through the real screen.
4. **The pill's hit count is untested against a live query.** The code path exists and is coerced, but
   no arm drives `query=` through a fold. `LLR-N06.2.4` and the search work are Inc-4's.
5. **The pan step (8 columns / 4 rows) is a chosen constant**, not a derived one. No requirement fixes
   it; the ATs derive their press counts from `pan_extent` so they do not depend on the value.

---

## 9 · Pending items / spec deviations

| id | Item |
|---|---|
| `B-55` | `outline` / `radial` declare no painted set. Pinned by the participation census, routed to Inc-5 |
| `B-56` | **CLOSED IN THE FIX ROUND — see §11.1 and §11.6.** The carry recorded here was wrong on both halves: the indicator was ABSENT at ordinary sizes rather than stale, and ordinary navigation did not clear it. Closed by `_declare_after_layout`, which recomputes the declaration alone and leaves `refresh_canvas`'s focus behaviour untouched; both at-risk arms measured GREEN. Residual carried as `B-60` |
| `B-57` | **NEW.** `AT-015`/`AT-016` drive **six** configurations, not four. `A-98` states that `(30, 6)` discriminates `MUT-B`, the dropped-column mutant. Re-measured, it does **not**: at `(30, 6)` the row bound alone already excludes every node but `erp`, so the column bound cannot change the answer, and `MUT-B` is green on all four pinned rows. The column bound first bites at `(30, 12)`. The four pinned rows are still asserted driven; two were added, and the AT fails if fewer than six ran |
| `B-58` | **NEW.** `LLR-COERCE.2`'s numeric threshold (the commutation equality) is **inert** against the defect it names, for the reason in §7. The requirement is met; the threshold is not what meets it |
| `B-59` | **NEW.** `test_darkside_census.py`'s `OPEN_EXCEPTIONS` names **Inc-3** as the closer of the layered removed-ghost `ALERT` retone. It is **not** closed here: it is in no Inc-3 LLR and no cut assigns it, and closing it cascades into three census arms. Worse, the register's own comment calls itself "a mechanical handoff instead of a promise" — but the guard only reddens if the line is *removed*, so **forgetting is silent**. The handoff is not mechanical |
| `V-6` | The overflow indicator is painted on **two** surfaces (canvas header and `#map-pagination`) from **one** computation. `LLR-N06.3.3` names only `views/layered.py`; the `02j` ruling names `_pagination_text`. Both are satisfied, and `TC-038` pins them equal |
| — | `AT-046` / `AT-047` and `LLR-N06.2.4` remain **Inc-4's**, untouched |

---

## 10 · Suggested next task

**`Inc-4` — US-N07 «búsqueda» plus `LLR-N06.2.4` (the walk that opens a folded hit).** It inherits a
`MapScreen.folded` that is now a single owner with two readers, which is the precondition
`LLR-N06.2.4` needs, and `AT-046`/`AT-047` are the arms that stop `AT-022` passing on a screen where
the operator cannot see the selection. It should also take `B-58`'s threshold rewrite while
`LLR-COERCE.2` is still warm, and rule on `B-59` before the register goes stale.

---

## Increment gate checklist

| Check | Evidence |
|---|---|
| Tests pass | **POST-FIX: `789 passed, 17 deselected` fast, exit 0, over 8 consecutive runs** (§11.5). Pre-fix: `784 passed` · `17 passed` slow · `801 collected` |
| Lint | **POST-FIX, set-wise and scope-matched vs `git archive 954f8f3`: base 28, work 27, ZERO NEW**, one removal (§11.5). The pre-fix claim compared totals, which the code review correctly called out |
| No secrets in code or output | no credential, token or `.env` read or written; hostile fixtures are `chr(0x…)` at test time and **no control byte is spelled into any source file** |
| No destructive command without approval | none run; nothing committed, pushed or merged; `prototypes/` and `fixtures/mapper.db` untouched |
| File count within cap | **6 source files, the declared `A-89` + `A-97` breach**; no seventh taken. The fix round touched **2** of those six and took no new source file — `store.py` was routed to Inc-REPAIR rather than opened |
| Every LLR carries a real `TC-NNN`, every AT one on-disk node | `TC-030` … `TC-040`, `AT-011` … `AT-017`; no "covered by the combination of" |
| Mutation battery with per-arm verdicts | Original: 21 arms + 2 re-runs. **Fix round: 14 arms, 14 killed, ZERO survivors** (§11.4) |
| Restores proven | sha256 per arm; the two round-1 `NOT RESTORED` flags were a **text-mode LF→CRLF normalisation in my harness**, not content loss — proved by comparing normalised sha256 against `git show HEAD:` (identical), and round 2 re-ran in binary mode |
| Review packet attached | this document |

---
---

# 11 · FIX ROUND — both gates returned BLOCK (3 HIGH code, 2 HIGH security)

Both independent gates blocked. This section records what was fixed, what was measured, and where
the recorded carries were **wrong** rather than merely stale. Nothing below is self-cleared: every
fix carries a mutant that reddens a named arm, and every restore is proven by sha256.

## 11.1 · The five blocking findings

| id | Finding | Fix | Mutant → arm |
|---|---|---|---|
| `SEC-F1` | **HIGH.** `SchemaField.key` reached the terminal *and* the exported SVG uncoerced from `layered.py:464`, in the **default** renderer — `B-47` verbatim, on the surface this increment exists to close. The `A-89` census could not see it: its fixture set only title/meta/notes, and `legacy` mode is selected by `bool(graph.schema)`, so the arm never entered the leaking branch | `darkside.plain(sf.key)[:1] or " "` at the sink, **and** the census fixture widened with a non-empty `graph.schema` carrying `U+0001` / `U+202E` in the keys | `M1` → `test_a89_every_reached_renderer_coerces_what_it_paints` **RED** |
| `SEC-F2` | **HIGH.** `_minimap_text` interpolated a file-derived ficha title with no coercion; nine hostile code points reached the composited frame, including a `U+202E` that displays one branch's coverage under a neighbour's name — in the one widget whose job is that judgement | `darkside.plain(...)` at `app.py:1479`, **and** a new `LLR-N06.2.3` census arm sweeping every region `refresh_canvas` repaints, plus the whole frame | `M2` → `test_llr_n06_2_3_every_repainted_region_coerces_what_it_paints` **RED** |
| `CR-F1` | **HIGH.** `_canvas_size` over-declared on short terminals: a real region no taller than the header returned `h = region.height`, so `row_limit` believed canvas row 0 survived. Reproduced at `(31,18)`, `(50,14)`, `(100,10)` — 8 of 8 nodes hidden, indicator declaring **7** | three explicit branches; a region that cannot hold a body row returns `h = 1`, so `row_limit == 0` and nothing is declared | `M4` → `test_a_region_too_short_for_a_body_row_declares_nothing_painted` **RED** |
| `CR-F2` | **HIGH.** The forbidden naive fold-sum survived at the paint site. `TC-039` read `_unpainted_ids()`, one layer **below** `_pagination_text`, where a count is actually taken; `TC-038` was the only arm reading the painted strip and never set `folded` | `TC-039` now also reads the **painted strip** on the same nested-fold state, and asserts the naive numeral is absent | `M5` (real naive sum in `_pagination_text`) → `TC-039` **RED** |
| `CR-F3` | **HIGH.** The `B-56` carry was recorded on wrong measurements — the indicator was **absent**, not stale, at ordinary sizes, and did **not** close at the first keypress | **CLOSED**, not re-bounded: `on_mount` schedules `_declare_after_layout`, which recomputes the declaration alone | `M6` → `test_b56_the_declaration_is_right_on_the_first_look_with_no_repaint` **RED** |

### `CR-F3` — the two arms the ruling put at risk, measured

The ruling said: use the declaration-only path; if it reddens `LLR-CNV.3.1` or `B-50`, stop and
report. **It does not.** Both alternatives were measured in the scratchpad export, full suite:

```
declaration-only  (SHIPPED)            784 passed, 17 deselected, 0 failed   <- both arms GREEN
call_after_refresh(refresh_canvas)     FAILED test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region
canvas + strip recomputed after layout FAILED test_tc_a3_the_census_cardinalities_are_PINNED
```

The author's original measurement is **confirmed**: a second full `refresh_canvas` reddens
`LLR-CNV.3.1`'s parent-walk arm. A variant that repaints the canvas as well as the strip is green on
focus but adds a second `render` call site and reddens the **A-3** call-site census — an arm
belonging to Inc-2's requirement. Declaration-only is the only close that costs no arm elsewhere.

**B-56 after the fix, 9 of 9 measured cases correct**, mount plus seven pauses, no forced repaint:

```
map      term       keys   hdr/strip/TRUE   strip
legacy   (30, 20)   j      (2, 7, 7)        OK      (was: 2 declared on a screen hiding 7)
legacy   (30, 20)   jk     (2, 7, 7)        OK
legacy   (50, 20)   j      (None, 4, 4)     OK      (was: ABSENT while 4 were hidden)
legacy   (60, 20)   j      (None, 4, 4)     OK      (was: ABSENT)
anidado  (50, 20)   j      (2, 4, 4)        OK
legacy   (50, 20)   II     (None, 4, 4)     OK
legacy   (40, 20)   -      (2, 7, 7)        OK
anidado  (40, 20)   -      (3, 5, 5)        OK
anidado  (60, 20)   -      (2, 4, 4)        OK
```

The `hdr` column is the residual, carried as **`B-60`**: the canvas header's own numeral is written
by `render` and is not recomputed, so it can under-declare on the very first frame while the strip
is correct. It is a **pre-existing** staleness this fix does not worsen — before the fix both
surfaces were wrong and agreed; now the surface the operator reads for this is right.

## 11.2 · Also fixed

| id | Fix | Evidence |
|---|---|---|
| `SEC-F4` | `reached_renderers()` now matches `ast.Attribute` on `node.attr` as well as `ast.Name` | `M14` (renderer wired as `lane.LaneRenderer`) → **2 arms RED**, including `test_a89_the_reached_set_is_pinned_so_wiring_lane_up_pulls_it_in`, the pin whose stated job is to force the decision. The reviewer's mutant previously **survived with 23 passing** |
| `SEC-F3` | `_reclamp_pan` brought back **inside** `refresh_canvas`'s try; `_unpainted_ids` returns `None` on a layout failure (the value it already has for "declares nothing"); and `_pan`'s own unguarded `pan_extent` guarded too — **that** call, not either of the two named, is what the review's `L` keypress actually died on | `M7` and `M8` → `test_a_layout_that_cannot_be_drawn_does_not_kill_the_app` **RED** |
| `CR-F4` | `tests/test_pan.py:16`'s unused `height_offset` import **deleted**, with the reason recorded: every arm in that module reads `screen._canvas_size()` back off the mounted screen and derives its press counts from `pan_extent` at that size — the stronger form of the same discipline, since it measures the achieved geometry instead of computing a size it hopes it got. Nothing there needs the helper | set-wise ruff: the `F401` is gone and **no** new finding replaces it |
| `CR-F5` | `oracle_traced` anchored positionally to the columns it already computes | `M10` (un-anchored again) → **2 arms RED**, `AT-016` among them. With the panned configuration added this is no longer a latent weakening — the un-anchored oracle actively fails |
| `CR-F6` | `CONFIGURATIONS` widened to `(w, h, folded, pan)` with a panned row at `(30, 12, (), (8, 2))` where `legacy` has live travel in **both** axes; asserted cardinality **7**; `_drive` asserts the pan it **achieved**, since `refresh_canvas` re-clamps | `M12` (panned row dropped) → `AT-015` and `AT-016` **RED** |
| `CR-F7` | `pan_graph`'s docstring corrected and the claim **asserted**. The unit was the defect: at a 118x34 **terminal** the side regions take 60 columns, so the canvas is 58x25 and `max_pan_x = 49`, `max_pan_y = 10`. Handed to the **renderer** at `w = 118` the same fixture has `max_pan_x = 0` — the reading that made the docstring look false. Both are now asserted, the negative one included | `test_the_pan_fixture_overflows_both_axes_at_the_declared_context` |
| `CR-F8` | The `HEADER_ROWS` pin parametrised over **node count** as well as width (70 measurements), and the asserted value **derived** from the measured header rather than compared to a literal | `M13` (`HEADER_ROWS = 3`) → the pin **RED** |
| `CR-F9` | `AT-016`'s non-degeneracy guard now asserts over **outcomes**, not over the literal configuration table | `M11` (outcomes forced identical) → `AT-016` **RED** |
| flake | `test_app.py:350`'s positive control waits for its precondition on a **bounded loop** that fails loudly and names what never happened, instead of assuming one `pause()` lands focus | tally in §11.5 |

### On `H`/`L` being "inert at most realistic widths"

**They are not, in the declared context of use** — that note was measured at the renderer width
rather than the terminal. Measured through the real screen:

```
terminal (118, 34) -> canvas (58,25)  max_pan_x=49  max_pan_y=10   both chords live
terminal (140, 45) -> canvas (80,36)  max_pan_x=27  max_pan_y= 0   H/L live, J/K inert
terminal (100, 30) -> canvas (64,20)  max_pan_x=43  max_pan_y=15   both live
```

Horizontal pan goes inert only on a canvas wide relative to the map, which needs a terminal near 180
columns with both side regions shown. Asserted in the new fixture arm so the distinction survives.

## 11.3 · Two defects found by the FIX round itself, neither in either review

1. **The breadcrumb painted an uncoerced `ficha.title` into the composited frame.** `refresh_canvas`
   queries `TabStrip` **by type**, so it has no id — the region-by-region half of the new census
   walks straight past it. The **frame-level** half caught it: `['0x1','0x200b','0x202c','0x202e']`
   reaching the frame through `tab.set_crumb(...)`. Same class as `SEC-F2`, on a surface neither gate
   named. Fixed by coercing every crumb segment, since `map_id` and the link chain are file-derived
   too. Mutant `M3` → the census arm **RED**. *A census keyed on how a widget is looked up inherits
   that lookup's blind spots; the frame has none — which is why both halves are kept.*

2. **`_branch_coverage_glyph` HANGS on a cyclic graph.** Its walk had no visited set at all, so it
   re-expanded the same nodes forever — an unbounded hang reached from `refresh_canvas`, outside
   every guard. Found because the `SEC-F3` regression arm hung instead of failing. This is strictly
   worse than the crash `SEC-F3` describes, and it is the failure mode this tree's own rule singles
   out. Executed: 200,000 walk steps on a 4-node cycle with the stack still non-empty. The same
   missing set also double-counted on a multi-parent DAG, skewing the coverage percentage the glyph
   exists to report. Fixed with a `seen` set. Mutant `M9` → `tests/test_pan.py` **TIMED OUT (HANG)**.

## 11.4 · Mutation battery — 14 arms, per-arm verdicts, all restores proven

Run entirely in the scratchpad export, never in the shared tree. Every mutant is applied, the
targeted module run, the file restored **from the pristine shared tree**, and the restore proven by
sha256 returning to its pre-mutation value.

| # | Mutant | Target | Verdict | Arm that killed it | Restore |
|---|---|---|---|---|---|
| M1 | `SEC-F1` schema key uncoerced | `test_inc3_census.py` | **RED** | `test_a89_every_reached_renderer_coerces_what_it_paints` | sha256 returned |
| M2 | `SEC-F2` minimap title uncoerced | `test_fold.py` | **RED** | `test_llr_n06_2_3_every_repainted_region_coerces_what_it_paints` | sha256 returned |
| M3 | breadcrumb uncoerced (new defect) | `test_fold.py` | **RED** | same arm, frame half | sha256 returned |
| M4 | `CR-F1` short region over-declares | `test_overflow.py` | **RED** | `test_a_region_too_short_for_a_body_row_declares_nothing_painted` | sha256 returned |
| M5 | `CR-F2` naive fold sum at the paint site | `test_overflow.py` | **RED** | `TC-039` | sha256 returned |
| M6 | `CR-F3` no post-layout declaration | `test_overflow.py` | **RED** | `test_b56_the_declaration_is_right_on_the_first_look_with_no_repaint` | sha256 returned |
| M7 | `SEC-F3` `_pan` guard removed | `test_pan.py` | **RED** | `test_a_layout_that_cannot_be_drawn_does_not_kill_the_app` | sha256 returned |
| M8 | `SEC-F3` `_unpainted_ids` guard removed | `test_pan.py` | **RED** | same arm | sha256 returned |
| M9 | minimap walk hangs on a cycle (new defect) | `test_pan.py` | **HANG** (150 s limit) | same arm | sha256 returned |
| M10 | `CR-F5` oracle un-anchored again | `test_overflow.py` | **RED** (2 arms) | `AT-016` + the short-region sweep | sha256 returned |
| M11 | `CR-F9` outcomes forced identical | `test_overflow.py` | **RED** | `AT-016`'s non-degeneracy guard | sha256 returned |
| M12 | `CR-F6` panned configuration dropped | `test_overflow.py` | **RED** (2 arms) | `AT-015` + `AT-016` | sha256 returned |
| M13 | `CR-F8` `HEADER_ROWS = 3` | `test_overflow.py` | **RED** | the header pin | sha256 returned |
| M14 | `SEC-F4` renderer wired by **attribute** | `test_inc3_census.py` | **RED** (2 arms) | incl. the equality pin that previously survived | sha256 returned |

**14 of 14 killed. Zero survivors. No arm stayed green.**

## 11.5 · Test results after the fix round

| Lane | Result |
|---|---|
| fast, x8 consecutive | `789 passed, 17 deselected` **8 times out of 8**, exit 0 every run — read from pytest's own exit code, never through a pipe (piping to `tail` reports *tail's* status, which is how a failing run once displayed `exited with code 0`) |
| ruff, **set-wise** vs `git archive 954f8f3` | base **28**, work **27**, **NEW = ∅**, gone = `mapper/views/layered.py F401` |

### Flake tally — the retracted-`B-51` family, closed

`test_app.py::test_an_export_never_encodes_where_the_keyboard_was` failed **1 run in 11** before this
round, at its own positive control: `_focus_owner()` was still `""` after `.focus()` plus one
`pause()`. `focus()` posts a message and one `pause()` is one turn of the pump — usually, not always,
enough. Replaced with a bounded wait that fails loudly and names what never happened, so a focus
mechanism that genuinely broke still reddens the arm.

```
run 1  789 passed, 17 deselected in 95.09s      run 5  789 passed, 17 deselected in 90.60s
run 2  789 passed, 17 deselected in 92.88s      run 6  789 passed, 17 deselected in 93.66s
run 3  789 passed, 17 deselected in 92.15s      run 7  789 passed, 17 deselected in 93.32s
run 4  789 passed, 17 deselected in 94.51s      run 8  789 passed, 17 deselected in 97.17s

FAILED lines across all 8 runs: none.   8 / 8 green, exit 0 each.

confirming run on the FINAL tree   789 passed, 17 deselected in 96.41s   exit 0
slow lane on the FINAL tree         17 passed, 789 deselected in 22.37s   exit 0
```

Eight runs cannot *prove* a rate below 1-in-11 is gone — stated rather than glossed. What is proven
is that the specific timing assumption that produced the failure no longer exists in the arm.

**The ruff comparison is set-wise AND scope-matched, and both corrections mattered.** Comparing
totals was the original error; comparing sets with *unequal scope* was the second one — the base
export carries `prototypes/`, which the working tree's `.gitignore` hides from ruff, so an unscoped
run showed a spurious 19-finding "improvement". With `--exclude prototypes` on both sides the sets
are directly comparable: **zero new findings**, one removal.

### Signed-balance test ledger for the fix round

`post = pre − deleted + added` → **`789 = 784 − 0 + 5`** ✓

The five added arms: the `B-56` first-look pin, the short-region height sweep, the `LLR-N06.2.3`
region census, the cyclic-layout survival arm, and the pan-fixture claim.

### The `A-3` call-site pin moved, in the direction a floor could never see

`50 → 49`. Two sites added (the pan-fixture arm, the short-region sweep) and two removed:
parametrising the `HEADER_ROWS` pin over node count folded its two inline `render` calls into one
`_header_rows` helper. **The pin caught it on the first run** and is updated deliberately with its
reason; the module map deliberately does not narrate the number, so the pin is its only home.

### One test-support defect the fix round exposed in itself

`_declared_total` joined the region rows with a space and then matched `fuera de vista` with
**literal** spaces. A row is padded to the region width, so joining two rows puts the padding inside
the sentence: at a 30-column strip the declaration paints as `... fuera de ` / `vista ...` and the
join carries two spaces. The helper therefore returned `None` — *the requirement's unwanted
behaviour* — on a strip that was declaring the right number all along. Caught because the new `B-56`
pin failed at `(30, 20)` while the frame plainly read `▽ 7 fuera de vista`. Now `\s+`.

## 11.6 · Carries — corrected, each with its measurement

| id | Carry |
|---|---|
| `B-56` | **CLOSED.** Was recorded as "one stale frame, closing at the first keypress". Both halves were wrong: the indicator was **absent** at 50x20 and 60x20 on `legacy`, and `j`/`jk` at the root are no-ops so nothing repainted. Now correct in **9 of 9** measured cases with no repaint |
| `B-60` | **NEW.** The canvas **header**'s numeral is written by `render` and is not recomputed after layout, so on the first frame it can under-declare while the strip is correct. Measured in the 9-case table above. Pre-existing, not introduced here; any repaint reconciles the two surfaces. Closing it needs either a second `render` call site (reddens the A-3 census) or a full `refresh_canvas` (reddens `LLR-CNV.3.1`) — a genuine `HLR-CNV.3` handoff, not a preference |
| `B-61` | **NEW, and it supersedes the `HEADER_ROWS` residual, which was understated on both axes.** Recorded: "3 rows below 30 columns", "wrong at 100+ nodes". Measured over 70 configurations: at `w = 20` the header takes **4** rows at *every* node count, and at `w = 30` it takes 3 from **n ≥ 40**, not 100. `_canvas_size` floors `w` at 20, so the 4-row case is reachable and the screen charges one row for a wrap costing three. Probed through the real screen at canvas widths 20–31, the `declared == traced` identity **still holds** on the shipped fixtures — latent, not live |
| `CR-F10` | The `▸` token is re-typed at `rail.py:226` against `layered.py:19-25`'s own "declared ONCE" comment. Not fixed — `rail.py` is not one of this round's two source files |
| `CR-F11` | `render` duplicates the painted-set comprehension instead of sharing one helper with `painted_ids`. Behaviourally safe (both off one `_geometry`), against the module's stated principle |
| `CR-F12` | Navigation is fold-unaware: `l` descends into a folded branch and the cursor vanishes from both surfaces while the inspector and crumb still show it; `z` there is silent |
| `CR-F13` | Smaller items: the removed-node ghost applies `pan_y` but not `pan_x`; `render` uses `geo.index` with no `None` check; `TC-040` kills its mutant by `KeyError` rather than by its documented oracle |
| `SEC-F5` | `_hidden_ids` is quadratic in `\|folded\|` — measured **987.8 ms at n = 4000** with every node folded, and `_geometry` runs **4×** per pan keypress. New code, on the repaint path |
| `SEC-F6` | The truncator census walks `tree.body` only, so a truncator defined as a method escapes it. Latent — all 23 AST candidates were checked and none is a `(str, int) -> str` truncator |
| `SEC-F7` | `_tree_layout` is **exponential** on a multi-parent DAG — `2^depth` while node count stays linear; **~100 s** to render 49 nodes, measured **identically at `954f8f3` and at Inc-3** (3352 ms vs 3523 ms at 22 levels), so pre-existing. `MAX_RENDER_NODES = 12000` does not defend it. The one shape that hangs rather than raises |
| `SEC-F8` | Test modules shell out to `git ls-files`. Fixed argv, no `shell=True`, call-site-literal globs, test-only. Accepted as-is |
| `store.py` `_coerce_text_fields` | **Routed to Inc-REPAIR by ruling**, which owns `store.py`. Coercing `key`/`label` at the load boundary is the defence-in-depth half of `SEC-F1`; the sink half ships here |

## 11.7 · Files touched in the fix round

| File | Kind | Change |
|---|---|---|
| `mapper/views/layered.py` | source | `SEC-F1` — coerce `SchemaField.key` at the legacy card's sink |
| `mapper/app.py` | source | `SEC-F2` minimap · breadcrumb coercion · `CR-F1` `_canvas_size` · `CR-F3` `_declare_after_layout` · `SEC-F3` three guards · the `_branch_coverage_glyph` hang |
| `tests/inc3_support.py` | test | anchored oracle, `pan_x`, corrected fixture docstring |
| `tests/test_overflow.py` | test | panned configuration, outcome-based guard, parametrised header pin, `TC-039` painted strip, two new arms, `_declared_total` |
| `tests/test_inc3_census.py` | test | non-empty hostile `graph.schema`, `ast.Attribute` |
| `tests/test_fold.py` | test | the `LLR-N06.2.3` region + frame census |
| `tests/test_pan.py` | test | dead import removed, fixture claim asserted, cyclic-layout survival arm |
| `tests/test_app.py` | test | bounded wait for the focus precondition |
| `tests/test_a3_census.py` | test | the call-site pin, `50 → 49`, with its reason |

**SOURCE files: 2**, both inside the declared six (`mapper/app.py`, `mapper/views/layered.py`). No
seventh file taken; `store.py` was explicitly routed away rather than opened.

---

# 12 · FIX ROUND 2 — both confirmation passes returned BLOCK (2 HIGH code, 1 HIGH security)

Four of five prior code HIGHs and both security HIGHs were confirmed **DISCHARGED by independent
re-execution**. What blocked was one recurrence band a constant could not price, one carry recorded
on refuted measurements, and one pre-existing crash that subsumes a HIGH this increment closed.

## 12.1 · HIGH-1 — `CR-F1` recurs wherever the header wraps past `HEADER_ROWS` (`B-61` is LIVE)

**The constant was never a measurement.** `HEADER_ROWS = 2` was justified by "the header's length is
`avail + 5` or `2 * avail - 43`, hence between `avail` and `2 * avail`, hence two rows". **Both of
the header's paddings are clamped at 0**, so below `avail = 48` neither formula applies: the line is
a fixed core plus the `▽ N fuera de vista` declaration — **55 cells on `legacy` at every narrow
width**. The old pin could not see this because it compared `_header_rows` to the constant only
where they agreed, and enumerated the disagreement as a "residual".

**Reproduced before the fix, through the real screen, on the shipped `legacy` fixture:**

```
term=(28,17) region=(28,3)  canvas=(28,2)  hdr=55c  ceil(55/26)=3  cards=0
             declared=['erp']  traced=[]  strip '▽ 7'  truth 8      <- CR-F1 verbatim
term=(28,30) region=(28,13) canvas=(28,12)                cards=3
             declared=[cont,erp,fin,pres]  traced=[erp,fin]  strip '▽ 4'  truth 6
term=(80,24) control: declared == traced, 8 of 8                    <- fix intact where the header is 2 rows
```

Swept over **252 driven configurations** (`legacy`, terminal w=20..40 x h=10..32, same driver both
sides): **9 diverge before the fix, 0 after.** Every divergence is an OVER-declaration
(`traced` a strict subset of `declared`, `under=[]` in all nine) — the story's promise inverted,
never the reverse.

### The measurement that replaces the constant

`mapper/views/layered.header_rows(graph, w)` — a module-level pure function, beside `painted_ids`
and `pan_extent`. It measures the SAME line `render` paints, because both now build it from one
`_header_line` helper: a second copy of the header's shape is exactly the copy that drifted.

**The wrap divisor is `w - 2`, not the region width, and that is measured rather than assumed.** At
terminal (28,17) the canvas region is **28** columns wide and 3 rows tall; `ceil(55/28) = 2` and
`ceil(55/26) = 3`; the composited frame shows **zero body rows**. `w - 2` is the widget's content
width, which is why the renderer builds to `avail = w - 2` too.

**The cycle is broken by charging the WORST case, and the direction is the whole safety argument.**
The line's length depends on `unpainted`, which depends on `row_limit`, which depends on this
number. `header_rows` therefore prices `unpainted = len(graph.nodes)` (most digits, token always
present). Over-charging emits FEWER body rows than the region can show and `row_limit` still
describes exactly what was emitted, so the identity holds and at most one physical row goes unused;
**under-charging is `B-61`**. It is also self-consistent: a row lost to the charge hides a node,
which paints the token the charge already paid for. Measured over 738 (graph, w, h) probes:
`charged >= measured` **everywhere**, `charged > measured` in **9**, always by exactly 1, always at
a band edge.

### The band, DERIVED — this replaces `B-61`'s note and closes MEDIUM-9

The old pin's bounds were artifacts of a grid that jumped n 10 to 40 and w 30 to 50. Re-derived on a
contiguous grid (n in {8,10,11,13,14,20,39,40,100,1000} x w = 20..40 plus 50/58/80/140/300, 520
cells):

| charged rows | width band | note |
|---|---|---|
| 4 | w = 20 (`legacy`, n<=40) ... w = 20..22 (n near `MAX_RENDER_NODES`) | `_canvas_size` floors `w` at 20, so this is reachable |
| 3 | w = 21..29 (`legacy`) · 21..30 (n<=40) · 22..31 (n=100) · **23..34 (n=11999)** | the old pin recorded `w <= 30` |
| 2 | **w >= 35 at every node count the renderer will draw** | the only band the constant was right on |

The old note's "3 rows at w=30 from n>=40" is a *width* shift, not a node-count threshold: at n=100
the 3-row band moves to 22..31, at n=1000 to 23..32. And the band reaches **w = 34**, confirmed at
n = 11999 — one below `MAX_RENDER_NODES`.

### The identity sweep now enters the band

`test_a_region_too_short_for_a_body_row_declares_nothing_painted` gains six widths inside 20..34 —
`(20,24) (22,30) (26,19) (28,17) (28,30) (34,22)` — each measured over-declaring before the fix.
Restoring the constant (battery arm **N1**) reddens it immediately. The arm also now asserts, as
non-vacuity, that the sweep CONTAINS a size where the header costs more than two rows and paints
something.

## 12.2 · HIGH-2 — `B-60` CLOSED, not re-recorded; `TC-038` no longer repaints away its own claim

**Ruled by the gate: close it.** The carry was wrong the same two ways `CR-F3` was blocked for — the
header numeral is **absent**, not stale (and `LLR-N06.3.3` makes absence *mean* "nothing hidden"),
and "any repaint reconciles them" is false (over nine keys only `l` and `o` heal it).

`_declare_after_layout` now repaints **both declaring surfaces** — the canvas and the strip — and
nothing that focuses. The alternative, `call_after_refresh(refresh_canvas)`, reddens `LLR-CNV.3.1`
with `assert 'rail' == 'inspector'`; this variant reddens only the **A-3 call-site pin**, which its
own docstring says is updated deliberately with its reason and which has already moved 35 to 50 to
51 to 49.

- `TC-038`'s `screen.refresh_canvas()` is **deleted**. It measures on a first look now, and its
  docstring no longer claims "always" — it states the property it actually holds and why the old
  form hid `B-60`.
- The `B-56` first-look arm asserts the **canvas header** beside the strip, at all four sizes the
  divergence was measured at.
- The stale `B-56`/`B-60` narration in `on_mount` and `test_overflow.py` is deleted (LOW-7).

**Battery arm N4** (strip-only, i.e. the pre-fix behaviour) reddens **both** arms.

## 12.3 · F-A — routed to Inc-REPAIR, obligation landed as a strict-xfail arm

`SchemaField.key` is interpolated into a Textual widget id (`mapper/widgets/inspector.py:137-140`);
`BadIdentifier` is raised inside `_rebuild`, scheduled by `call_next` from `refresh_canvas`,
**outside every guard**. It fires for `chr(0x01)` **and for `año` and `fecha limite`** — the
Spanish-first happy path for a hand-written sidecar — and it subsumes `SEC-F1`'s attack, because a
hostile key kills the session before it can reach the SVG.

**Per the ruling, not fixed here**: `inspector.py` would be a seventh source file, and the fix
belongs with the other repair work.
`test_f_a_a_map_whose_schema_keys_are_not_identifiers_still_opens` lands the obligation now, marked
`xfail(strict=True)` and referencing `F-A`.

**Proved to force its own removal (battery arm N14):** keying the field rows by index in the export
turns the arm XPASS, and strict xfail converts that to `FAILED`. Inc-REPAIR cannot land the fix
without deleting the marker.

## 12.4 · Also fixed — five silent survivors converted into red arms

| Finding | Fix | Arm that now kills it |
|---|---|---|
| **F-D** `layered.py:459` doc chip | `A-89` fixture gains a `fields` dict | N9 |
| **F-D** `layered.py:520` ghost titles | `A-89` fixture gains a `DiffResult` (`removed_titles`) | N10 |
| **F-D** `layered.py:449` diff chip | same `DiffResult` (`changed`) | N11 |
| **F-D** `inspector.py:155` attachments | `LLR-N06.2.3` fixture gains attachments | N12 |
| **F-D** `factory.py:252` factory tree | `FactoryScreen` driven by `d`, swept | N13 |
| **MEDIUM-5** vertical pan no-op | `test_a_live_J_press_changes_what_the_canvas_paints` | N6 |
| **MEDIUM-2** one-row-under `_canvas_size` | `test_the_canvas_is_charged_every_row_the_header_leaves` | N3 |
| **MEDIUM-3** viewport x fold overlap | `test_the_paint_site_differences_one_set_on_a_PARTIAL_overlap` | N5 |
| **MEDIUM-6** `_minimap_text` unguarded | guarded like its sibling | N8 |
| **LOW-3** sticky `borde del territorio` | cleared on a successful pan | N7 |
| **F-E** code points in artifacts | replaced by their NAMES; scan extended to `.dev-flow` | N15 |
| **F-F** operator's absolute path | `cd <repo root>` in increments 001/002/003 | — |

`rail.py:230` is **NOT** touched: the confirmation proved it an equivalent mutant
(`darkside.fit(body, RAIL_WIDTH - 4)` coerces downstream on both branches), so it is correctly green.

### The `LLR-N06.2.3` census fixture, widened, with a survival assertion

It carried **no schema at all**, which is exactly why it could not see `F-A`: no `insp-field-*`
widget was ever constructed. It now carries a schema, attachments and fields, and asserts
`app.is_running` **before** it reads a region — a census that reports "no leak" on a screen that
never rendered is reporting nothing.

**Its schema KEYS are deliberately identifier-safe while the LABELS carry the payload**, and that
bound is recorded in the fixture's own docstring: a hostile key would not widen this census, it
would replace it with `F-A`'s crash. The strict-xfail arm carries that obligation instead.

### `FactoryScreen` is scoped to `#factory-tree`, and the scope is a finding

Measured: the composited FRAME of that screen leaks `['0x1','0x200b','0x202c','0x202e']` while all
four addressable regions are clean — the leak is in the screen's chrome, not its tree. That is
**F-C**, pre-existing, `factory.py` out of scope, routed to Inc-REPAIR. A frame-level sweep here
would be red on the shipped tree. The arm pins the coercion that ships and **asserts the residual
still exists**, so the day `F-C` closes, the arm says so and asks to be widened.

## 12.5 · Mutation battery — 16 arms, per-arm verdicts, every restore proven by sha256

Run in a `tar` export with its own `git init` (about 25 census arms shell out to `git ls-files`; a
bare copy is not a git repo and produces spurious FAILED arms). **Green baseline established first:
`789 passed, 17 deselected`, exit 0.** Exit codes read from the subprocess return code, never from a
pipeline.

| # | Mutation | Verdict | Killed by | Restore |
|---|---|---|---|---|
| N1 | `_header_rows` to constant `2` | **KILLED** | `..._region_too_short...` + `..._canvas_is_charged...` | OK |
| N2 | guard uses measured rows, subtraction uses `2` (half-fix) | **KILLED** | same two | OK |
| N3 | `region.height - rows` (one row under) | **KILLED** | `..._canvas_is_charged_every_row_the_header_leaves` | OK |
| N4 | `_declare_after_layout` repaints the strip only | **KILLED** | `test_b56_...` + `test_tc_038_...` | OK |
| N5 | `_pagination_text` partial-overlap sum | **KILLED** | `..._PARTIAL_overlap` | OK |
| N6 | `geo.place` drops `- pan_y` (lockstep) | **KILLED** | `test_a_live_J_press_changes_what_the_canvas_paints` | OK |
| N7 | `set_hint("")` on success removed | **KILLED** | `test_the_edge_hint_does_not_latch_across_a_live_pan` | OK |
| N8 | `_minimap_text` guard removed | **KILLED** | `test_a_dangling_edge_does_not_escape_refresh_canvas` | OK |
| N9 | `layered.py:459` doc chip uncoerced | **KILLED** | `test_a89_every_reached_renderer_coerces_what_it_paints` | OK |
| N10 | `layered.py:520` ghost title uncoerced | **KILLED** | same | OK |
| N11 | `layered.py:449` diff chip uncoerced | **KILLED** | same | OK |
| N12 | `inspector.py:155` attachment uncoerced | **KILLED** | `test_llr_n06_2_3_...` | OK |
| N13 | `factory.py:252` tree title uncoerced | **KILLED** | `test_the_factory_tree_coerces_the_titles_it_paints` | OK |
| N14 | **F-A FIXED** in the export (id keyed by index) | **KILLED** | `test_f_a_...` — strict xfail turns XPASS into FAILED | OK |
| N15 | `U+202E` planted in a `.dev-flow` artifact | **KILLED** | `test_no_tracked_file_spells_a_coerced_code_point_...` | OK |
| N15b | `U+200B` planted in an **UNTRACKED** `.dev-flow` artifact | **KILLED** | same arm — the case `git ls-files` would miss | OK |

**16 applied, 16 killed, 0 survivors, 16 of 16 restores `OK`.** Every kill is by a named arm's own
oracle; none is a crash-kill. **No arm stayed green.**

**Two counterfactuals, because a kill on the fixed tree is only half the evidence:**

- The 252-configuration sweep: **9 diverging before the fix, 0 after**, same driver both sides.
- The new artifact scan run against the **un-fixed** artifact tree names exactly the two files `F-E`
  named — `02b-security-review.md` (`0x202e`) and `increment-001-code-review-confirmation.md`
  (`0x200d`) — and is green after.

**The artifact half sweeps by `rglob`, not `git ls-files`, and N15b is why.** The artifacts an
increment is writing right now are UNTRACKED, so a tracked-file sweep is blind exactly where new
work lands — the same correction `test_llr_coerce_1_no_test_retypes_the_range_list` already records
one module over. The source half keeps `git ls-files`, because `LLR-S06.3.1` names that command and
scopes it to tracked product source. The arm asserts the rglob view is strictly wider than the
tracked one, so it cannot silently degrade into the sweep it replaced.

## 12.6 · Test results — one complete run each

| Lane | Result | Exit |
|---|---|---|
| Default (`-m 'not slow'`) | **796 passed, 17 deselected, 1 xfailed** in 102.67 s | **0** |
| Slow (`-m slow`) | **17 passed, 797 deselected** in 23.94 s | **0** |
| ruff 0.8.4, set-wise, scope-matched (`--exclude prototypes` both sides) | **NEW = empty set**; gone = `mapper/views/layered.py F401 Node` | — |

The one `xfailed` is `F-A`, landed deliberately and strict.

### Signed-balance test ledger — DERIVED against `954f8f3`, zero deleted

Collected node ids from a detached `git archive 954f8f3` and diffed the sorted sets against the
working tree, so `deleted = 0` is a measurement:

```
all markers:   814 = 737 - 0 + 77   OK
default lane:  797 = 720 - 0 + 77   OK
DELETED (in base, not in post):   (none)
ADDED per file:  23 test_inc3_census · 20 test_pan · 14 test_overflow · 12 test_fold
                  4 test_keymap · 4 test_key_dispatch   (both parametrised over the seat)
```

**Fix round 2 alone adds 8 arms** (7 passing + 1 strict xfail): the canvas-utilisation pin, the
partial-overlap paint-site arm, the live-`J` content oracle, the hint-latch arm, the dangling-edge
guard arm, the factory-tree coercion arm, the artifact code-point scan, and the `F-A` obligation.

### The `A-3` call-site pin moved again — `49` to `52`, itemised

A bumped pin with an unitemised reason is a pin that has stopped working, so the three are named in
the pin itself: **+1** `_declare_after_layout` now renders (the priced cost of closing `B-60`), and
**+2** the `A-89` arm renders with and without a `DiffResult` to prove the diff state changes what
is painted — the non-vacuity guard on the two diff-only sinks whose mutants used to survive. The
module map deliberately does not narrate the number, so the pin remains its only home.

## 12.7 · Carries — corrected, and what is routed where

| id | Status |
|---|---|
| `B-60` | **CLOSED** (12.2). The refuted measurements are recorded rather than repeated: absent-not-stale; nav does not heal; `TC-038`'s repaint was load-bearing |
| `B-61` | **CLOSED** (12.1). It was **live**, not latent. Re-derived bounds replace the sample artifacts |
| **MEDIUM-9** | **CLOSED** — the pin's grid is contiguous over n=11..39 and w=31..40 and its bounds are derived from it |
| `F-A` | **ROUTED to Inc-REPAIR**, obligation landed as a strict xfail (12.3) |
| `F-B` | **ROUTED to Inc-REPAIR.** `coverage.py` uses `escape` only; measured leak `['0x1','0x200b','0x202c','0x202e','0xe0041','0xfeff']` on the frame after `m` — the surface the operator reads to decide **what to go fix** |
| `F-C` | **ROUTED to Inc-REPAIR.** `factory.py` same, and the file contradicts its own tree-lines comment. Residual asserted by the new factory arm so its closure is announced |
| `F-G` | **PART-CLOSED.** The `_minimap_text` half is guarded (12.4, N8). Reachability restated honestly: "could not construct from a file", not "unreachable" |
| **NEW carry — `OutlineRail.render` is unguarded** | Found while writing the N8 arm. On a dangling edge `rail.show()` succeeds and `OutlineRail.render` raises `KeyError` at **compositor paint time** (`rail.py:221`), which no guard in `refresh_canvas` can reach. `rail.py` is in the declared six but outside this round's fix set, so it was **not** opened. This is why the N8 arm asserts `refresh_canvas` does not raise rather than that the frame survives |
| `F-H` | **CARRY.** `MapStore.save` to `load` is not total: `U+0001` in `Edge.label` makes a map the product wrote unopenable |
| `LOW-8` | **CARRY, not authorised here.** `pytest-timeout` is a new dev dependency; the hang-regression arm fails by hanging, which in CI is a stuck run rather than a red report. **Operator decision** |
| `LOW-1/2/4/5/6`, `MEDIUM-1/7/8`, `CR-F10..F13`, `SEC-F5..F8`, `B-55` | unchanged, as recorded in 11.6 |

## 12.8 · Files touched in fix round 2

| File | Kind | Change |
|---|---|---|
| `mapper/views/layered.py` | **source** | `_header_line` extracted (one construction); `header_rows` added |
| `mapper/app.py` | **source** | measured header height in both uses; `_declare_after_layout` repaints canvas+strip; `_minimap_text` guarded; edge hint cleared on success |
| `tests/test_overflow.py` | test | header pin rewritten as an inequality over a dense grid; sweep widened into 20..34; canvas-utilisation arm; partial-overlap arm; `TC-038` un-repainted; `B-56` asserts the canvas |
| `tests/test_pan.py` | test | live-`J` content oracle; hint-latch arm; dangling-edge guard arm |
| `tests/test_fold.py` | test | fixture widened (schema/attachments/fields) + survival assertion; `FactoryScreen` arm; `F-A` strict xfail; artifact code-point scan |
| `tests/test_inc3_census.py` | test | `A-89` fixture gains `fields` and a `DiffResult`; both diff states swept |
| `tests/test_a3_census.py` | test | call-site pin `49` to `52`, itemised |
| `.dev-flow/**` (5 artifacts) | artifact | `F-E` code points to names; `F-F` absolute paths to `<repo root>` |

**SOURCE files: 2**, both inside the declared six. **No seventh file taken.** `inspector.py`,
`coverage.py`, `factory.py`, `store.py` and `rail.py` were driven and mutated **only in the
scratchpad export**, never opened for edit in the working tree.

---

# 13 · FIX ROUND 3 — pass-3 `F1`/`F2`/`F3` and the permitted adjacent set

**Scope was three items plus a named adjacent set, and it was not widened.** Two source files
touched, `mapper/app.py` and `mapper/views/layered.py`, both already inside the declared six.
`inspector.py`, `coverage.py`, `factory.py`, `store.py` and `rail.py` stayed closed.

| Item | Ruling from pass 3 | Status after round 3 |
|---|---|---|
| `F1` / `P3-F1` — the artifact scan goes red on its own commit | HIGH / MEDIUM | **CLOSED** (13.1) |
| `F2` — HIGH-1 not discharged: circular pin, false safety claim, wrong divisor rationale | HIGH | **CLOSED** (13.2) |
| `F3` — HIGH-2 not discharged: the region settles after the callback | HIGH | **CLOSED** (13.3) |
| `F6` — `header_rows` does O(n) work that cannot change its answer | MEDIUM | **CLOSED** (13.4) |
| `F4a` / `P3-F3` — the xfail marker guarantees "fails", not "fails for the right reason" | MEDIUM / LOW | **CLOSED** (13.4) |
| `F5` — the production comment overstates what the minimap guard saves | MEDIUM | **CLOSED** (13.4) |
| `P3-F2` — the scan does not sweep `fixtures/` or `maps/` | LOW | **CLOSED** (13.4) |
| `LOW-8` — `pytest-timeout` | operator decision | **AUTHORISED and landed** (13.5) |

## 13.1 · `F1` — the widening is now asserted structurally, not against today's tracking state

**The defect, restated as measured.** `tests/test_fold.py` asserted the `rglob` view was a STRICT
superset of the `git ls-files` view. That holds only while some `.dev-flow` artifact is untracked —
which is to say only mid-increment. Measured in the working tree: **91 artifacts, 84 tracked, 7
untracked**. Committing the increment makes the two sets equal and the guard fires on its own
landing, for a reason that has nothing to do with the rule it enforces.

**The fix.** The strict-superset clause is replaced by two that say the same thing without consulting
what is committed:

- **the instrument comparison** — `set(_tracked(".dev-flow/**")) <= set(artifacts)`, i.e. the
  `rglob` half is not NARROWER than the tracked query. A commit can only strengthen this, never
  flip it.
- **a probe** — the arm creates `.dev-flow/_scan_probe.md`, asserts the `rglob` sees it, and removes
  it in a `finally`. This is the half that actually proves the widening buys something: it exercises
  "reaches an untracked file" rather than inferring it from the day's tracking state.

**Proof it is closed, and it is the same instrument that caught it.** The pass-3 reviewer's export
baseline — a faithful copy of the working tree with `git add -A`, i.e. exactly the post-commit
tracking state — failed at this assertion and no other. The same export, rebuilt on this round:

```
$ cd <scratch>/exp4 && git init -q . && git add -A && git commit -q -m base
EXPORT FILES: 194
$ PYTHONUTF8=1 python -m pytest -q -p no:randomly tests/test_fold.py::test_no_tracked_file_..._artifacts
1 passed in 1.36s                                                            EXIT=0
$ PYTHONUTF8=1 python -m pytest -q -m "not slow" -p no:randomly
796 passed, 17 deselected, 1 xfailed in 104.38s                              EXIT=0
```

**The increment can now be committed green.** This was fixed first, so every mutant verdict below
rests on a genuinely green baseline rather than on one already carrying a known red.

## 13.2 · `F2` — the header cost is RENDERED, and pinned against the COMPOSITED FRAME

Pass 3 raised three things and all three were right. Each is answered by measurement below, and the
answers changed the fix.

### 13.2a · The pin was circular — it is now a different instrument

`tests/test_overflow.py::_header_rows` computed `-(-len(header) // (w - 2))` and called it a
measurement. That is `header_rows`'s own arithmetic re-typed: the two sides could not disagree about
the divisor (both `w - 2`), about word-wrap (neither wrapped), or about a wide character (both
`len`). **`_header_rows` is deleted.** The verification now runs through
`_header_rows_in_frame(screen)`, which reads the rows Textual actually painted into the canvas
region and counts how many the header consumed — the compositor, not a formula.

### 13.2b · "always safe" was false — the charge is now a real wrap

`header_rows` divided; Rich WORD-WRAPS, so a line `ceil` prices at 2 rows can occupy 3. Reproduced
exactly, on the pre-fix tree, over the reviewer's 943-configuration sweep (`legacy`, terminals
20..60 x 8..30):

```
MAP=legacy n=943  (PRE-FIX)
  UNDER-CHARGE vs rich-at-(w-2)    = 23        <- the reviewer's number, reproduced
```

The product now renders the line through `Console.render_lines` instead of dividing.

### 13.2c · The divisor rationale was factually wrong — and the fix is to MEASURE the width, not to pick a better constant

This is the finding that changed the shape of the fix. Two widths are in play and the old code
conflated them:

- **`w`** — the width the renderer BUILDS the line to (`avail = w - 2`, the paddings).
- **`wrap_w`** — the width the canvas widget WRAPS it at.

`#map-canvas` is `width: 1fr; height: 100%` with no padding and no border, so its content width is
its REGION width. Measured over the 943:

```
  content_w == _canvas_width()       : 724
  content_w == _canvas_width() - 2   : 219
  content_w anything else            :   0
```

So `w - 2` is not "the widget's content width" — it is one of the two values that width takes, and
the wrong one 724 times out of 943. `header_rows` therefore takes `wrap_w` as a **required third
argument with no default**: there is no width it could guess that is not the same mistake again, and
`MapScreen._canvas_size` now reads the region FIRST and passes `canvas.content_size.width`.

### 13.2d · The numbers pass 3 asked for, post-fix

The truth instrument is a Rich wrap at the measured content width, and it is **validated against the
frame before being trusted**: it agrees with the composited frame at every configuration the frame
can show.

| Measurement | `legacy` (n=943) | `anidado` (n=943) |
|---|---|---|
| instrument check — truth == composited frame | **636 of 636** frame-measurable | **657 of 657** |
| charge vs composited frame — **under** | **0** | **0** |
| charge vs composited frame — **over** | **0** | **0** |
| charge vs composited frame — **exact** | **636 of 636** | **657 of 657** |
| charge vs truth over ALL 943 | under **0**, over **0** | under **0**, over **0** |
| under-charge vs the OBSOLETE `w - 2` stick | 31 | 33 |

**The 23-of-943 band goes to 0 against the frame, and the residual against the `w - 2` stick is
explained by a measured mechanism** — it is the stick that is wrong, not the charge. At every one of
those configurations the composited frame shows the header in the rows the charge names and only
`w - 2` predicts otherwise; at (30,20), for instance, `content_w = 30`, the frame shows 2 rows, the
charge is 2, and `ceil(55/28)` says 3. The 23 pre-fix decomposed the same way: 16 were configurations
where `content_w == w` (the stick's error) and 7 were genuine 3-row renders at a region 1 row tall,
where `_canvas_size` takes the short-region branch whatever it charges.

**The equality is now an upgrade over the inequality it replaces.** The previous pin asserted only
`charged >= measured`, because a fixed `w - 2` over-charged wherever the region was `w` wide — and
over-charging is not free: at a short region it costs the operator the only body row there was.

**The 27-of-520 grid cells, honestly.** That number came from swapping the circular helper for a
real render. Post-fix the product IS a real render, so re-running the same comparison returns 0 **by
construction** — which is a tautology, not evidence, and it is not offered as one. The 520-cell grid
survives as
`test_llr_n06_3_1_the_charge_band_over_node_count_and_width`, **relabelled a characterization**: it
buys reach the frame cannot (`_balanced(11999)` sits just under `MAX_RENDER_NODES` and no terminal
can composite it) and it sweeps `wrap_w` over BOTH measured values, but it does not claim to verify
the charge. The verification is the composited arm, and the mutants below are the evidence.

### 13.2e · The cycle argument — kept, and the paragraph pass 3 called non-load-bearing is gone

Pass 3 ruled the self-consistency argument SOUND: `header_rows` never reads `painted`, `row_limit` or
`body_h`, so it is a pure function of its arguments and nothing oscillates. The unconditional
worst-case pricing is kept and the docstring now says exactly that. The "a row lost to the charge
hides a node, which paints the token the charge already paid for" sentence is **deleted** — the
argument does not rest on it.

## 13.3 · `F3` — `B-60` recurs because the region settles after the callback, and `on_resize` alone does NOT close it

**The mechanism, re-traced.** `_declare_after_layout` fires on the first `call_after_refresh`, while
`_apply_region_visibility` is still reflowing the body row. Instrumented at (31,16) on `legacy`:

```
  _canvas_size region=(0, 0, 0)    -> (31, 8)      pre-layout guess
  ** on_resize Size(width=31, height=16)
  >> _declare_after_layout ENTER
  _canvas_size region=(31, 1, 31)  -> (31, 1)      short-region branch
  >> _declare_after_layout ENTER
  _canvas_size region=(29, 2, 29)  -> (31, 1)      still reflowing
  ...
  FINAL region=Region(x=0, y=7, width=31, height=3)
```

**`on_resize` was added and it was not enough — measured, not assumed.** With the handler in place
and nothing else changed, the band still diverged at all four `legacy` sizes and both `anidado`
sizes, byte-identical to the pre-fix run. The reason is in the trace above: **a SCREEN resize is not
a CANVAS resize.** The screen's own resize arrives with the terminal's 31x16 BEFORE the row reflows,
and the canvas region moves twice more afterwards without another one.

**So the declaration follows the region to its settle.** `_declare_after_layout` records the region
it painted for and re-schedules itself while that region keeps changing:

```python
if region != self._declared_for:
    self._declared_for = region
    self.call_after_refresh(self._declare_after_layout)
```

It terminates because it re-schedules only on a CHANGE, so a settled layout costs one no-op pass.
`on_resize` is kept and is load-bearing for a different case — the operator resizing the terminal
after mount, which had no handler at all — and it is pinned by its own arm.

**The band, before and after, both surfaces, both fixtures:**

| fixture | term | pre-fix | post-fix |
|---|---|---|---|
| `legacy` | (31,16) | hidden 7, strip **8**, canvas **8** | 7 / 7 / 7 |
| `legacy` | (32,16) | hidden 7, strip **8**, canvas **8** | 7 / 7 / 7 |
| `legacy` | (34,15) | hidden 7, strip **8**, canvas **8** | 7 / 7 / 7 |
| `legacy` | (35,14) | hidden 7, strip **8**, canvas **8** | 7 / 7 / 7 |
| `anidado` | (34,14) | hidden 6, strip **7**, canvas **7** | 6 / 6 / 6 |
| `anidado` | (35,14) | hidden 6, strip **7**, canvas **7** | 6 / 6 / 6 |

Landed as `test_b60_the_declaration_follows_the_region_to_its_settle`, parametrised over both
fixtures, asserting the **strip and the canvas** as pass 3 required, pressing nothing and repainting
nothing.

### A defect found while writing the resize arm, measured and NOT fixed

The first draft of the resize arm went (140,45) -> (50,20) and failed for a reason that is not
`B-60`. Measured:

```
at 140x45           : region (80, 38)  rail_hidden False  inspector_hidden False
after resize to 50x20: region ( 1, 10)  rail_hidden False  inspector_hidden False
                      chrome_width 60 of a 50-column terminal
mounted at 50x20    : region (50,  8)  rail_hidden True   inspector_hidden True
```

**`_apply_region_visibility` runs in `on_mount` and on an explicit toggle, and nowhere else**, so
shrinking a terminal across the auto-collapse threshold leaves the rail and inspector shown and
squeezes the canvas region to ONE column. This is pre-existing — there was no resize handler at all
— and it is **carried, not fixed**: re-running the visibility pass on resize shows and hides
focusable regions, which is exactly where `LLR-CNV.3.1` and `B-50` placed the keyboard, and that is
a widening this round was told not to take. The arm changes only the terminal HEIGHT so it measures
re-declaration and not this, and its docstring records the bound.

## 13.4 · The permitted adjacent set

**`F6` — `graph.coverage()` removed from `header_rows`.** Verified at the source: `step_meter`
(`darkside.py:268-280`) appends exactly `total` glyphs whatever `filled` is, so `pct` cannot change
the header's LENGTH — the only thing `header_rows` needs. The O(n) walk (3 per repaint, 2 per `J`
keypress) is replaced by a named module constant `_METER_PCT = 100` carrying that reason. Pass 3's
note that `tests/test_repair_perf_shape.py` drives the renderer directly and never through
`MapScreen` is recorded in the docstring, so nobody reads that suite as covering this path.

**`F4a` / `P3-F3` — the `F-A` marker now names its exception, and every key is driven.** Added
`raises=BadIdentifier`; the three keys are **parametrised** rather than looped, with `año` first,
because the loop short-circuited on `chr(0x01)` and the Spanish-first case is the whole reason `F-A`
outranks `SEC-F1`. Three separate strict xfails now, each its own node.

**`F5` — the production comment stops overstating.** `mapper/app.py`'s minimap guard now says in
terms that it does **not** save the app on a dangling edge: `OutlineRail.render` indexes
`graph.nodes[...]` unchecked too and raises at compositor paint time, one sink over. It points at the
carry in `tests/test_pan.py`, so the two files no longer disagree.

**`P3-F2` — `fixtures/` and `maps/` are in the scan.** The source half's glob list gains
`fixtures/*`, `fixtures/**/*`, `maps/*`, `maps/**/*`, and the non-`.py` half is asserted non-empty on
its own. `git ls-files` and not a directory glob, so the untracked `mapper.db` never reaches the
`read_text`.

## 13.5 · `pytest-timeout` — authorised, dev-only, version-pinned

**Rationale, recorded here because a dependency without one is a dependency nobody can remove
later.** `TC-R12`'s cycle-guard arms wrap the render in `pytest.raises` and check the elapsed time
AFTERWARDS. That ordering means the arm cannot see the failure it was written for: delete a cycle
guard and the traversal never returns, `pytest.raises` never exits, and the elapsed-time assertion is
never reached. In CI that is a wedged run rather than a red report, and a wedged run is the one
outcome nobody reads as a defect.

- `pyproject.toml`: `pytest-timeout==2.3.1`, in the **dev extra only**. Not a runtime dependency;
  `dependencies` is untouched.
- `timeout = 120`, `timeout_method = "thread"` in `[tool.pytest.ini_options]`. `thread` because
  signal-based timeouts need `SIGALRM`, which Windows does not have. 120 s is far above every arm's
  real cost (slowest measured arm under 20 s; the whole default lane ~125 s) — it is not a
  performance budget, it is a hang detector.
- `tests/test_repair_depth.py`: both `TC-R12` arms carry
  `@pytest.mark.timeout(CYCLE_GUARD_TIMEOUT_SECONDS)` = `RENDER_BOUND_SECONDS * 15` = 30 s.

**This authorisation covers `pytest-timeout` and nothing else.**

## 13.6 · Mutation battery — 11 arms, per-arm verdicts, every restore proven by sha256

Every mutant applied in `<scratch>/exp4`, a `tar` export with its own `git init` where **everything
is tracked** — i.e. the post-commit state. Baseline there before any mutant: **801 passed, 17
deselected, 3 xfailed, exit 0**. Restores proven by `sha256sum -c` against a snapshot, never by
`git status`.

| # | Mutant | Verdict | Killing arm(s) | Failure text | Restore |
|---|---|---|---|---|---|
| N1 | `test_fold.py` — the artifact half degrades to `git ls-files` | **KILLED** | the artifact scan | `the rglob does not see an untracked artifact; it is the tracked sweep wearing a different instrument` | sha256 OK |
| N2 | `U+200B` planted in `fixtures/anidado.mmd` | **KILLED** | same | `[('fixtures/anidado.mmd', ['0x200b'])]` | sha256 OK |
| N3 | `U+200B` planted in `maps/legacy.mmd` | **KILLED** | same | `[('maps/legacy.mmd', ['0x200b'])]` | sha256 OK |
| N4 | `layered.py` — the charge reverts to `ceil(len / avail)` | **KILLED** | composited pin, **both fixtures** | `legacy (20,30): charged 4 physical header rows against 3 in the composited frame (region 20x7)` | sha256 OK |
| N5 | `layered.py` — wrap at `w - 2` instead of the measured width | **KILLED** | composited pin **both fixtures** + the band arm | `legacy (29,30): charged 3 against 2 in the composited frame (region 29x13)` | sha256 OK |
| N6 | `app.py` — the declaration stops chasing the region to its settle | **KILLED** | `test_b60_..._settle` **both fixtures** + composited pin | `(31,16): the frame could not show the header in a region 3 rows tall against a charge of 2` | sha256 OK |
| N7 | `app.py` — `MapScreen` has no resize handler | **KILLED** | `test_b60_resizing_the_terminal_re_declares_without_a_keypress` | `after a resize the strip declares None against 7 hidden, with no key pressed` | sha256 OK |
| N8 | `app.py` — the screen guesses `w - 2` instead of measuring the region | **SURVIVED, then KILLED** | composited pin, **both fixtures** | see below | sha256 OK |
| N9 | `radial.py` — the cycle guard deleted, so `TC-R12` loops forever | **KILLED by the new timeout** | `TC-R12` | `+++ Timeout +++`, **exit 1 after 33 s** instead of a wedged run | sha256 OK |
| N10 | the `F-A` arm fails from a `RuntimeError` instead of `BadIdentifier` | **KILLED** | the strict xfail's `raises=` | `3 failed`, exit 1 | sha256 OK |
| N10b | **control** — the same wrong-reason failure with `raises=` REMOVED | **exit 0, `3 xfailed`** | — | silently green, which is the point | sha256 OK |

**11 mutants, 11 restores `OK`, 0 `MISMATCH`.**

**N8 is reported as a survivor because it was one.** The first version of the composited pin asserted
`header_rows`'s answer against the frame — and a mutant that made `_canvas_size` pass a GUESSED
`w - 2` sailed through it (`exit 0, 19 passed`), because the arm asked the helper directly and never
checked the wiring. The pin was strengthened to tie `_canvas_size`'s own output to the frame:

```python
if canvas.region.height > measured:
    assert h - 1 == canvas.region.height - measured
else:
    assert h == 1
```

and N8 then died on both fixtures with
`legacy (29,30): _canvas_size gave the renderer row_limit 10 into the 11 body rows the frame actually
left (region height 13, header 2)`. **No arm in this round stayed green against its own mutant.**

**N10/N10b are the direct evidence for `F4a`.** The identical wrong-reason failure is `exit 0,
3 xfailed` without `raises=BadIdentifier` and `exit 1, 3 failed` with it. The clause is load-bearing,
not decoration.

## 13.7 · Test results — one complete run each

| Lane | Result | Exit |
|---|---|---|
| Default (`-m 'not slow'`) | **801 passed, 17 deselected, 3 xfailed** in 127.69 s | **0** |
| Slow (`-m slow`) | **17 passed, 804 deselected** in 25.17 s | **0** |
| ruff 0.8.4, set-wise, scope-matched (`--exclude prototypes` both sides) | base **28 records / 28 unique**, post **27 / 27**; **NEW = empty set**; gone = `mapper/views/layered.py F401 Node`, one element | — |

The three `xfailed` are `F-A`, one per key, landed deliberately and strict.

### Signed-balance test ledger — DERIVED against `954f8f3`, zero deleted

Node ids collected from a detached `git archive 954f8f3` export and diffed set-wise against the
working tree, so `deleted = 0` is a measurement and not a claim:

```
all markers:   821 = 737 - 0 + 84   OK
default lane:  804 = 720 - 0 + 84   OK
DELETED (in base, not in post):   (none)
ADDED per file:  23 test_inc3_census · 20 test_pan · 19 test_overflow · 14 test_fold
                  4 test_keymap · 4 test_key_dispatch
```

**Fix round 3 alone is +7 node ids** against round 2's 77:

- `tests/test_overflow.py` **14 -> 19**: `+6` added (the composited pin over two fixtures, the band
  characterization, the settle arm over two fixtures, the resize arm) and `-1` deleted (the circular
  grid pin). The **one deletion in the whole batch**, and it is the arm pass 3 ruled unable to
  falsify itself.
- `tests/test_fold.py` **12 -> 14**: `+2` from parametrising the `F-A` arm over its three keys.

### The `A-3` call-site pin did NOT move — and that is itemised too

It stays at **52 arg-ful sites**, and a pin that holds still for an unexamined reason is as bad as
one bumped without one. Derived: **-1** for the deleted `test_overflow.py::_header_rows`, whose body
called `LayeredRenderer().render(...)`, and **+1** for the new `_header_rows_in_frame`, which renders
to learn what the header's first logical line says before counting its rows in the frame. Net zero,
by two changes that cancel rather than by nothing having happened. `zeroarg` 26 and `definitions` 7
are unchanged.

## 13.8 · Files touched in fix round 3

| File | Kind | Change |
|---|---|---|
| `mapper/views/layered.py` | **source** | `header_rows` renders the line through `Console.render_lines`; `wrap_w` added as a required argument; `graph.coverage()` removed (`_METER_PCT`); docstring corrected on the divisor, the wrap and the cycle argument |
| `mapper/app.py` | **source** | `_canvas_size` reads the region first and passes the measured content width; `_header_rows(wrap_w)`; `on_resize` added; `_declare_after_layout` chases the region to its settle; minimap comment stops overstating |
| `tests/test_overflow.py` | test | `_header_rows` deleted; `_header_rows_in_frame` added; composited-frame pin over both fixtures; grid relabelled a characterization and swept over both wrap widths; `B-60` settle arm and resize arm |
| `tests/test_fold.py` | test | artifact scan asserted structurally + probe; `fixtures/`/`maps/` in scope; `F-A` parametrised with `raises=BadIdentifier` |
| `tests/test_repair_depth.py` | test | `@pytest.mark.timeout` on both `TC-R12` arms |
| `pyproject.toml` | build | `pytest-timeout==2.3.1` in the dev extra; `timeout` / `timeout_method` |

**SOURCE files: 2**, both inside the declared six. **No seventh file taken.** `inspector.py`,
`coverage.py`, `factory.py`, `store.py` and `rail.py` were never opened for edit; every mutation ran
in the scratchpad export.

## 13.9 · Carries after round 3

| id | Status |
|---|---|
| `B-60` | **CLOSED** (13.3), including the residual pass 3 found. `on_resize` alone was measured insufficient and is recorded as such |
| `B-61` | **CLOSED** (13.2). The charge is a render, the wrap width is measured, and both are pinned against the frame |
| **NEW carry — `_apply_region_visibility` is not re-run on resize** | Found while writing the resize arm and measured (13.3): shrinking a terminal across the auto-collapse threshold squeezes the canvas region to one column. Pre-existing; **not fixed**, because re-running the visibility pass moves focusable regions and would put `LLR-CNV.3.1` / `B-50` back in play |
| `LOW-8` | **CLOSED** — `pytest-timeout` authorised, pinned, dev-only, and its arm proven by N9 |
| `F-A`, `F-B`, `F-C`, `F-G`, `F-H`, `OutlineRail.render` | unchanged and still routed as recorded in 12.7 |
