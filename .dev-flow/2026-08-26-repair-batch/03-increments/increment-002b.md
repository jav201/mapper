# Increment 002b — A-6 · `the derivation root is the traversal surface`

| Field | Value |
|---|---|
| Batch | `2026-08-26-repair-batch` |
| Increment | `002b` |
| Lane | not forked · this increment owns `mapper/widgets/rail.py`, `mapper/screens/factory.py` and `tests/test_repair_depth.py` |
| Requirement(s) | `HLR-R02` · `LLR-R02.1` **as amended by A-6** |
| Acceptance | `AT-R16` · white-box `TC-R29` (widened derivation), `TC-R30` (rail equivalence), `TC-R31` (factory equivalence), `TC-R32` (cycle termination) · plus the two reviewer findings folded in, `F2` and `F4` |
| Agent | `software-dev` (supervised-incremental-development) |
| Date | 2026-08-26 |

---

## 1 · What changed

**A depth-5000 map now draws in the rail in 0.09 s and in the factory tree in 1.56 s;
before this increment both died with `RecursionError`.** The rail is composed on every
map, and its `render()` is called by Textual's compositor — outside
`MapScreen.refresh_canvas`'s `try/except`, which wraps `renderer.render(...)` only. So
the crash escaped the message pump exactly as S-01a did.

**The finding that made this increment two files instead of one.** Amendment A-6 widened
`LLR-R02.1`'s derivation root from the `mapper/views/` directory to "the traversal
surface", and then named `mapper/widgets/rail.py` as what had been outside it. Rooting
the probe at `mapper/` rather than at a named module returns **three** members, not one:

```
mapper/model.py             Graph.resolve_document
mapper/screens/factory.py   FactoryScreen._tree_lines.walk
mapper/widgets/rail.py      OutlineRail.visible_rows.walk
```

All three reproduce identically, each with its own positive control (§4). Two are closed
here. `Graph.resolve_document` is **not touched**: `mapper/model.py` is fenced from this
increment and amendment A-3 already disposed that member to increment 3, so it is carried
as a single requirement-backed deferral with an anti-rot guard, not as an exception list.

Three secondary changes fell out of the same work. They change cost, not output, and each
is pinned byte-for-byte against `master`:

- **`OutlineRail.subtree_missing` was cubic through `render`.** It was called once per
  visible row, and each call re-walked the branch through `Graph.children_of`, which
  rescans every edge. Measured on a chain: 0.016 s at depth 100, 5.616 s at depth 800,
  ~8x per doubling. **De-recursing `visible_rows` alone would have converted a bounded
  `RecursionError` into a ~23-minute hang** — increment 2's lesson in a third shape. It is
  now one memoised post-order pass, with an exact-walk fallback for the one shape where a
  post-order sum and the shipped deduplicated walk genuinely differ.
- **`FactoryScreen._max_depth` was cubic** for the same reason: `_depth` per node, and
  `parent_of` per step. 0.004 s at depth 100, 1.717 s at depth 800. It is now one pass
  with the chains memoised.
- **The rail built a full indent it then threw away.** `darkside.fit` truncates each row
  to `RAIL_WIDTH - 4` cells, so an indent already past that width cannot change the row;
  building the true indent made a deep chain quadratic in characters. 3.257 s at depth
  5000 against 0.091 s capped.

**Two guards, and one place that must never propagate.** Both rewritten traversals carry
an active-path guard and raise `ValueError` with increment 2's message, so the guard's
identity is assertable and uniform across the batch. But raising is not enough where
nothing catches: `OutlineRail.render` and `FactoryScreen._tree_lines` are the two surfaces
Textual calls, and each now paints a Spanish notice instead of propagating. A guard that
converts a `RecursionError` into a `ValueError` inside the compositor has moved the
crash, not removed it.

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped.**

| File | Kind | Change |
|---|---|---|
| `mapper/widgets/rail.py` | source | `visible_rows`'s inner `walk` converted to a stack loop with an active-path bound; adjacency indexed once; `subtree_missing` made one memoised post-order pass with an exact-walk fallback; the row indent capped at the width `fit` keeps; `render` catches and paints a Spanish notice |
| `mapper/screens/factory.py` | source | `_tree_lines`'s inner `walk` converted to a stack loop with an active-path bound, split into a raising `_tree_text` and a never-propagating `_tree_lines`; `_depth` given a seen-set so a cyclic parent chain terminates; `_max_depth` made one memoised pass; parent adjacency indexed once |
| `tests/test_repair_depth.py` | test | extended, 28 nodes -> 91 |
| `pyproject.toml` | config | registers the `slow` marker and deselects it by default (§4, suite runtime). No dependency added |

| Count | Value |
|---|---|
| **SOURCE files** | **2** (V9 declared) |
| Test files | 1 (uncapped) |
| Config files | 1 — `pyproject.toml`, marker registration only |
| Doc files | 1 — this packet (outside the count) |

**Why two and not one.** The brief budgeted one source file, `rail.py`, and pre-authorised
a second if declared and justified. `mapper/screens/factory.py` is the justification: it
is a member of the widened derivation, it crashes at depth 5000 exactly as the rail does
with the same positive control, and **no increment in §5 of the requirements owns it** —
it appears in none of the four rows. Leaving it would have shipped the widened derivation
RED, or forced a two-member hand-listed exception set, which is the defect A-6 exists to
name. Scope call confirmed before implementation.

**What was NOT touched, and why.**

- `mapper/model.py` — fenced from this increment; `Graph.resolve_document` is disposed to
  increment 3 by amendment A-3, which already records it and its reason. Reported, not
  changed.
- `mapper/views/**`, `mapper/mermaid.py`, `mapper/store.py`, `mapper/app.py` — increments
  1 and 2's set, read only. `git status --porcelain` shows this session modified nothing
  under any of them.
- ✓ **Frozen interfaces untouched.** `IRenderer.render` and `Canvas` are not in this
  diff at all; neither file imports them.
- ✓ **`OutlineRail`'s public API is unchanged.** `mapper/app.py` calls
  `OutlineRail(id=...)`, `.display`, `.focus()`, `.toggle(node_id)` and
  `.show(graph, cursor)` at lines 1126, 1209, 1226, 1236 and 1351; `tests/test_rail.py`
  additionally calls `.visible_rows()`, `.subtree_missing(node_id)` and `.render()`. Every
  one of those signatures is byte-identical, and `tests/test_rail.py` passes unmodified.
  `FactoryScreen`'s constructor is called at `app.py:621` and `app.py:1759`; unchanged.

---

## 3 · How to test

```bash
cd C:/Users/jjgh8/Github/mapper

# the gate run
PYTHONUTF8=1 timeout 600 python -m pytest -q -p no:randomly > out.txt 2>&1

# this increment alone, per-node
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_repair_depth.py \
    -p no:randomly -v --tb=short

# the two files this increment's changes are consumed by
PYTHONUTF8=1 python -m pytest tests/test_rail.py tests/test_factory.py -p no:randomly

# lint
python -m ruff check mapper tests
```

---

## 4 · Test results

### The two lanes

The suite is now run in two lanes, because the depth-5000 acceptance nodes build and
draw a 25 MB picture and were 16 s of one wall clock.

| Lane | Command | Collected | Result | Wall clock |
|---|---|---|---|---|
| **default (fast)** | `PYTHONUTF8=1 timeout 600 python -m pytest -q -p no:randomly` | 342 selected, 14 deselected | **342 passed** | **47.36 s** |
| **slow** | `... -m slow` | 14 selected, 342 deselected | **14 passed** | **15.90 s** |
| both | `... -o addopts=` | **356** | 356 passed | 63.3 s |

`pyproject.toml` registers the marker and sets `addopts = "-m 'not slow'"`. **The slow
lane is not optional** — it is where `AT-R16`'s acceptance lives — and that is stated in
the `pyproject.toml` comment as well as in Risk 7 below.

### Suite runtime — measured, before marking

`pytest -q -p no:randomly --durations=25`, whole tree, 68.11 s:

```
8.76s  test_repair_depth.py::test_at_r16_the_rail_survives_a_depth_5000_map_through_the_composed_screen
5.17s  test_app.py::test_repo_screen_two_pane_renders                       <- pre-existing, not this increment
2.40s  test_repair_depth.py::test_at_r16_the_factory_tree_survives_a_depth_5000_map
2.37s  test_repair_depth.py::test_at_r16_a_traversal_never_nests_deeper_than_the_declared_call_depth[factory._tree_lines]
2.30s  test_repair_depth.py::test_at_r16_depth_safety_does_not_depend_on_the_recursion_limit[factory._tree_lines]
1.51s  test_rail.py::test_at_n06d_regions_collapse_by_key_and_by_width      <- pre-existing
1.10s  test_worklist_safety.py::test_at_n05c_undo_survives_leaving_and_re_entering_the_map   <- pre-existing
1.08s  test_worklist_safety.py::test_at_n05b_accepting_removes_exactly_that_subtree          <- pre-existing
0.98s  test_worklist_safety.py::test_at_n05e_archiving_the_whole_map_is_refused              <- pre-existing
0.87s  test_inspector.py::test_at_n01a_editing_a_schema_field_persists_to_disk               <- pre-existing
0.58s  test_repair_depth.py::test_at_r16_depth_safety_does_not_depend_on_the_recursion_limit[factory._depth]
0.55s  test_repair_depth.py::test_tc_r32_every_graph_touching_method_terminates_on_a_cyclic_graph[entry_in_cycle]
0.54s  test_repair_depth.py::test_tc_r32_every_graph_touching_method_terminates_on_a_cyclic_graph[cycle_in_a_disconnected_component]
0.54s  test_repair_depth.py::test_tc_r32_every_graph_touching_method_terminates_on_a_cyclic_graph[cycle_off_root]
0.54s  test_repair_depth.py::test_tc_r32_every_graph_touching_method_terminates_on_a_cyclic_graph[self_loop_below]
```

**Four nodes are 15.8 s of it**, all in the `AT-R16` family, and all four are depth-5000
acceptance. What dominates is not the traversal — it is the store round-trip for a
5001-node map (1.70 s save + 1.28 s load, measured) and the 25 MB of text the factory
tree legitimately emits. Those four plus the rest of the `AT-R16` family are the 14 nodes
now marked `slow`.

**On the reported figure.** The gate was said to exceed 120 s; my complete runs measure
**63.3 s** for all 356 nodes and **47.36 s** for the default lane, against increment 2's
recorded 39.33 s for 293. The delta this increment adds is ~24 s at 356 nodes, ~8 s at
342. I did not reproduce a 120 s run and am not going to claim one.

### The RED — the widened derivation, before anything was changed

Captured from the shipped derivation in `tests/test_repair_depth.py`, run on the tree as
increment 2 handed it over, before a byte of `rail.py` or `factory.py` moved:

```
tests/test_repair_depth.py::test_tc_r10_the_ast_derivation_finds_the_functions_it_is_supposed_to_find PASSED
tests/test_repair_depth.py::test_tc_r10_the_graph_filter_keeps_the_probe_from_reporting_everything PASSED
tests/test_repair_depth.py::test_tc_r11_no_graph_traversal_in_views_is_recursive PASSED
tests/test_repair_depth.py::test_tc_r29_no_recursive_graph_traversal_outside_the_deferred_member FAILED
tests/test_repair_depth.py::test_tc_r29_the_deferral_record_is_not_stale PASSED

E   AssertionError: assert {'mapper/scre...le_rows.walk'} == set()
E     Extra items in the left set:
E     'mapper/screens/factory.py FactoryScreen._tree_lines.walk'
E     'mapper/widgets/rail.py OutlineRail.visible_rows.walk'
```

`test_tc_r11` — increment 2's `views/` check, re-pointed at the new engine — stayed GREEN
throughout, so the widening is strictly additive and does not re-open increment 2.

### The widened derivation, before and after

| | Members |
|---|---|
| **Before** | `mapper/model.py Graph.resolve_document` · `mapper/screens/factory.py FactoryScreen._tree_lines.walk` · `mapper/widgets/rail.py OutlineRail.visible_rows.walk` |
| **After** | `mapper/model.py Graph.resolve_document` — the single deferral, backed by amendment A-3 |

Three changes to the derivation, each with its reason:

1. **The root is `mapper/` by rglob**, not a named directory — A-6.
2. **Recursion is a call cycle of any length.** Increment 2's scanner flagged a function
   only when its own call names met `enclosing + [own name]`, which sees self-recursion
   and nothing else; a mutually recursive pair and a call through a module-level alias
   both measured `[]` against it (finding F3). The engine now builds a per-module call
   graph — resolving each call name against the nearest def visible in the caller's
   lexical scope chain, plus module-level `x = y` aliases in both directions — and reports
   every def that lies on a cycle.
3. **"Traverses a `Graph`" is derived from `Graph` itself**: `dir(Graph)` unioned with
   `Graph.__dataclass_fields__`. The union is load-bearing — `dir()` omits the fields
   declared with a `default_factory`, which are `nodes` and `edges`, i.e. exactly the
   structural ones. Without it a traversal that only read `graph.nodes` would be invisible.

`super().__init__()` is excluded, and the exclusion is a decision rather than a
convenience: a `super()` call targets the parent class by definition, so it can never be a
self-call, and without the exclusion the scan reports **30 false positives** across
`widgets/` and `screens/` — every `__init__` that chains to its base. A probe that
false-fails 30 correct functions gets routed around, which is C-53's failure mode applied
to a probe instead of to a gate.

### The derivation's positive control — it is not blind

The same unmodified engine over `git show HEAD:mapper/views/*.py` reproduces increment
2's five members, at increment 2's line numbers:

```
pre_layered.py 46 walk    ['children_of', 'parent_of', 'root_id']
pre_outline.py 48 walk    ['children_of', 'root_id']
pre_radial.py  23 _leaves ['children_of']
pre_radial.py  54 place   ['children_of', 'parent_of', 'root_id']
pre_radial.py  95 tag     ['children_of', 'parent_of', 'root_id']
```

and returns empty on today's `views/`. In the test file the control is
`test_tc_r10_the_ast_derivation_finds_the_functions_it_is_supposed_to_find`, which drives
six synthetic shapes: self-recursion, a nested closure, **a mutually recursive pair**,
**recursion through a module-level alias**, a non-recursive function (negative), and a
`super().__init__()` chain (negative). `test_tc_r10_the_graph_filter_keeps_the_probe_from_
reporting_everything` is the filter's own control: recursive-and-graph-touching versus
recursive-and-not, each asserted separately, so neither conjunct can go vacuous.

### All three members crash, each with its own positive control

```
recursionlimit=1000
rail.visible_rows
POSITIVE CONTROL depth 3 -> 4 rows
  depth   500: OK, 501 rows
  depth  5000: *** RecursionError ***
factory._tree_lines
POSITIVE CONTROL depth 3 -> 4 rows
  depth   500: OK, 501 rows
  depth  5000: *** RecursionError ***
model.resolve_document
POSITIVE CONTROL depth 3 -> doc
  depth   500: OK, doc
  depth  5000: *** RecursionError ***
```

### Every traversal in both files, not only the ones the scanner named

The scanner names recursion. It cannot name a traversal that was already a loop, and two
of the four real problems here were loops. Both files were read method by method:

| Method | What it was | Disposition |
|---|---|---|
| `OutlineRail.visible_rows.walk` | recursive, one frame per level | iterative + active-path guard |
| `OutlineRail.subtree_missing` | **already iterative and already cycle-safe** (its `seen` set) — depth was never its problem | its COST was: called once per visible row, each call rescanning every edge. Now one memoised post-order pass |
| `OutlineRail._lattice` | iterates `sorted(graph.nodes)`, no traversal | unchanged; driven on all four cycle shapes anyway |
| `OutlineRail.render` / `show` / `toggle` / `__init__` / `on_click` | no traversal | `render` gained the catch; the rest unchanged |
| `FactoryScreen._tree_lines.walk` | recursive, one frame per level | iterative + active-path guard, split into raising `_tree_text` and never-propagating `_tree_lines` |
| **`FactoryScreen._depth`** | **a `while True` up the parent chain with no cycle guard at all — it hung, forever, on any cyclic graph** | seen-set; terminates with the acyclic prefix |
| `FactoryScreen._max_depth` | `_depth` per node, `parent_of` per step — cubic | one memoised pass |
| `_Nav.*` | single-step cursor helpers, no traversal | unchanged; driven on all four cycle shapes |

**`_depth` is the finding worth naming.** It is not recursive, so no AST probe over
recursion would ever have reported it — not increment 2's, not the widened one in this
increment. It was found by reading the file. A derived probe answers the question it
encodes; it does not answer the question you meant.

### The census — derived, so "did you check them all" has an answer

`graph_touching_methods()` derives **35** methods across the two files: every method that
references `Graph`'s structural surface, closed over calls inside its own class (so
`OutlineRail.render` is in because `_body` is, and `FactoryScreen._tree_lines` because
`_tree_text` is). `TC-R32` drives every one of the 35 on all four cycle shapes and requires
each to terminate. The census is the assertion — a method the harness cannot instantiate
or supply arguments for reports `NO-INSTANCE` / `NO-ARGUMENT` and **fails the node** rather
than being silently skipped.

"Structural" is itself derived, from `Graph`'s own source: the dataclass fields plus every
`Graph` method that LOOPS over one of them. The loop is the discriminator, and it does real
work: `resolve_document` reads `parent_of` but never iterates the structure, and
`_preview` reads `nodes` with a dict lookup — neither is dragged in, so the census does not
inflate to every method that touches a graph.

### Cycle termination — one process per shape, wall clock and RSS ceiling

`_run_cycle_child` spawns `python -c` per shape with `PYTHONDONTWRITEBYTECODE=1`, bounded
by a 90 s wall clock in the parent and an 800 MB RSS watchdog inside the child that samples
every 50 ms and calls `os._exit(9)`. The parent reads a verdict line per method from
stdout; **the process exit code is not used as any verdict**.

| Shape | Wall | Child RSS at exit | Guard fired in | Terminated |
|---|---|---|---|---|
| `entry_in_cycle` (a→b→c→a) | 0.018 s | 52.1 MB | `rail._rows`, `rail._missing_map`, `rail.subtree_missing`, `rail._body`, `rail.visible_rows`, `factory._tree_text` | 35/35 |
| `self_loop_below` (r→a, a→a) | 0.018 s | 52.2 MB | `rail._rows`, `rail._body`, `rail.visible_rows`, `factory._tree_text` | 35/35 |
| `cycle_off_root` (r→a→b→c→a) | 0.018 s | 52.1 MB | `rail._rows`, `rail._body`, `rail.visible_rows`, `factory._tree_text` | 35/35 |
| `cycle_in_a_disconnected_component` (r→a; p→q→p) | 0.018 s | 52.4 MB | `rail._missing_map`, `rail.subtree_missing`, `rail._body` | 35/35 |

Two readings worth keeping. On `cycle_off_root` the rail's `_missing_map` **returns rather
than raising**, because `a` has two parents there so the forest check declines first and
the exact walk — which carries its own `seen` set — answers it. On the disconnected shape
`visible_rows` returns normally (the root never reaches `p`) while `_missing_map` raises,
because it visits every node; the rail therefore paints the cycle notice for a map whose
reachable tree is fine. That is deliberate and declared in Risk 4.

**The RSS ceiling has its own positive control.** `test_tc_r32_the_rss_ceiling_can_actually_
fire` drives the same child with the ceiling set to 4 MB and requires the watchdog to trip
and the child to die before `_done`. This exists because the first version of `_rss_bytes()`
**returned 0 on every call** — `GetCurrentProcess` defaults to a C `int` restype and its
pseudo-handle was truncated on 64-bit — so the ceiling was decoration and the watchdog
could never fire. It now raises on failure instead of returning 0, reads 52.1 MB in the
child, and is verified to move (+100 MB allocated → +100 MB read).

### The guard's identity — F2, folded in

Increment 2's `TC-R12` drove one cycle shape and asserted `pytest.raises(Exception)`. It is
now parametrised over three reachable shapes × three renderers, asserting `ValueError`, the
guard's own words, **and that the node the message names is really on the cycle**.

The fourth shape is the one that shows why `Exception` was not an oracle. Measured, on this
tree and on `master` both:

| Shape | radial | layered | outline |
|---|---|---|---|
| `entry_in_cycle` | ValueError | ValueError | ValueError |
| `self_loop_below` | ValueError | ValueError | ValueError |
| `cycle_off_root` | ValueError | ValueError | ValueError |
| `cycle_in_a_disconnected_component` | ValueError | **KeyError `'p'`** | rendered, 3 lines |

`layered` raises a `KeyError` that has nothing to do with the cycle guard —
`_tree_layout` indexes a node it never placed. `pytest.raises(Exception)` accepts it. It is
**pre-existing on `master`**, verified by running the `master` sources, so it is not a
regression and not this increment's file; it is recorded by identity in
`DISCONNECTED_COMPONENT_OUTCOMES` so that it cannot be absorbed and so a change to it
reddens deliberately. Named for increment 2's owner in §6.

### C-53, the false-failure arms — F4 folded in

| Golden | Varied over | Result |
|---|---|---|
| three renderers × `fixtures/legacy.mmd` | **4 sizes**: 140×45, 80×24, 140×8, 300×120 | 12 digests, all byte-identical to `master` |
| `OutlineRail.render` × `legacy.mmd` | **5 collapsed-set configurations** | 5 digests, all byte-identical to `master` |
| `OutlineRail.render` through the composed screen | 3 terminal sizes | identical to the expanded-set digest at every size |
| `FactoryScreen._tree_lines` × `legacy.mmd` | cursor on `fin` | byte-identical to `master` |

Increment 2 pinned one size, 140×45, while its riskiest change — `layered.py`'s `body_h`
cap — is a function of `h` (finding F4). The three 140×45 digests captured here are
**byte-equal to the three increment 2 pinned**, which is what says this capture method
reproduces the one that produced them; the other nine are new. `collapsed` is the axis
varied for the rail because `RAIL_WIDTH` is fixed, so the terminal size cannot move its
output — and `collapsed` is the input a memo keyed on the wrong thing would corrupt.
`_missing_map` deliberately does not read `collapsed` at all: a collapsed parent must still
count its hidden child's gaps, which `tests/test_rail.py:76` has always asserted.

### The equivalence proofs — positive controls, LLR-R02.2's shape

Each rewritten traversal is compared against a **verbatim copy of the shipped
implementation**, over shapes the shipped one terminates on. A rewrite that merely stops
crashing could be returning anything.

| Node | Control | Coverage |
|---|---|---|
| `TC-R30` `visible_rows` | `_shipped_visible_rows`, the recursive closure verbatim | 8 shapes × derived collapse configurations |
| `TC-R30` `subtree_missing` | `_shipped_subtree_missing` verbatim | every node of 8 shapes, count asserted |
| `TC-R30` the fallback | — | the memo must DECLINE a two-parent shape and accept a one-parent one |
| `TC-R30` the indent cap | `fit` applied to the true indent | every depth 0..79 × 2 label shapes |
| `TC-R31` `_tree_lines` | `_shipped_tree_lines` verbatim | 8 shapes × 5 cursor positions, sha256 per render |
| `TC-R31` `_depth` / `_max_depth` | `_shipped_depth` / `_shipped_max_depth` verbatim | every node of 8 shapes, count asserted |

The shape set is the same 8 increment 2 used, and **the diamond earns its place twice**:
it is the one shape where a memoised post-order sum could have changed an answer, and it is
the shape that makes `_missing_map` decline. On a graph where two paths reach one node, the
shipped walk counts that node's gaps once (it carries a `seen` set) and a post-order sum
counts them twice. Rather than answer that shape wrong and fast, `_missing_map` returns
`None` and the exact walk answers it. `mermaid.parse` has refused multiple parents since
long before this batch and a CSV preview gives every node one parent, so the shape cannot
arrive through the shipped surface — but it is asserted, not assumed.

### The cost fixes are pinned by a COUNT, not by a clock

A wall-clock assertion catches a cubic regression on this machine and misses it on a faster
one — and one of mine reddened at 2.236 s against a 2.0 s bound purely under load. The
memos are therefore pinned by the number of full edge-list scans, which is identical on
every machine:

| Node | Oracle | Measured now | With the memo removed |
|---|---|---|---|
| `test_at_r16_the_rail_render_scans_the_edge_list_a_bounded_number_of_times` | calls to `Graph.children_of` during `render()` on a 401-node chain | **0** (ceiling 4) | ~80,000 |
| `test_at_r16_max_depth_scans_the_edge_list_a_bounded_number_of_times` | calls to `Graph.parent_of` during `_max_depth()` on a 401-node chain | **0** (ceiling 4) | ~80,200 |

Both are cheap (depth 400) and both are in the **fast lane**, so the default gate still
holds the cost fix even though the depth-5000 acceptance moved to the slow lane.

### The measured numbers

Worst of five repeats, depth 5000 unless stated:

```
                                   before          after
rail.render (chain 5000)           RecursionError  0.1024 s   (3.2569 s before the indent cap)
rail.render (chain 800)            5.616 s         0.0859 s
factory._tree_lines (chain 5000)   RecursionError  2.2472 s   (25,043,898 characters of output)
factory._max_depth (chain 5000)    ~419 s (extrap) 0.0052 s
factory._max_depth (chain 800)     1.717 s         0.0005 s
rail.render (balanced 12000)       —               0.0958 s
factory._tree_lines (balanced 12000) —             0.0466 s
```

The cubic growth before the change, measured rather than predicted — ~8x per doubling for
both, which is what put the ~23-minute figure on a depth-5000 rail render:

```
depth   rail.render     factory._max_depth
100     0.016 s         0.004 s
200     0.096 s         0.030 s
400     0.703 s         0.232 s
800     5.616 s         1.717 s
```

### RED counterfactual — executed, not predicted

**14 arms, 0 inert, 0 failed restores, 72 reddened node-verdicts.** One verdict per
resolved node id; the process exit code is never a verdict (C-40 rider). The baseline and
the post-battery run both resolved **356 of 356 nodes, all passed**. Every arm ran with
`PYTHONDONTWRITEBYTECODE=1` and a purged `__pycache__`, and every arm's file was restored
and proven by **sha256 returning to its pre-mutation value**.

| Arm | Kind | File | Resolved | RED | Restore | What it proves |
|---|---|---|---:|---:|:--:|---|
| N1 | deletion | `rail.py` | 356 | **12** | ✓ | `_rows` recursion restored |
| **N2** | **plausible-weaker** | `rail.py` | 356 | **10** | ✓ | **raising the limit does not rescue it** |
| N3 | deletion | `rail.py` | 350 | **3** | ✓ | `_rows` active-path guard |
| N4 | deletion | `rail.py` | 350 | **2** | ✓ | `_missing_map` active-path guard |
| N5 | plausible-weaker | `rail.py` | 356 | **1** | ✓ | the memo must DECLINE a two-parent shape |
| N6 | plausible-weaker | `rail.py` | 356 | **10** | ✓ | child-order reversal is load-bearing |
| N7 | plausible-weaker | `rail.py` | 356 | **6** | ✓ | the indent cap's value is load-bearing |
| N8 | deletion | `rail.py` | 356 | **3** | ✓ | `render` must paint, not propagate |
| N9 | deletion | `factory.py` | 356 | **10** | ✓ | `_tree_text` recursion restored |
| **N10** | **plausible-weaker** | `factory.py` | 356 | **8** | ✓ | **same, for the factory tree** |
| N11 | deletion | `factory.py` | 350 | **3** | ✓ | `_tree_text` active-path guard |
| N12 | deletion | `factory.py` | 350 | **1** | ✓ | `_depth`'s seen-set |
| N13 | plausible-weaker | `factory.py` | 356 | **2** | ✓ | `_max_depth` cannot answer with the node count |
| N14 | plausible-weaker | test file | 356 | **1** | ✓ | the widened call-cycle probe against a self-name-only one |

Wall clock per arm ranges from 55.6 s to 1291.5 s; the two limit-raise arms are the long
ones (**N2 666.1 s**, **N10 1291.5 s**) because they keep recursion alive rather than
killing it quickly, which is the property they exist to demonstrate.

**The four guard-deletion arms resolve 350, not 356, and the 6 absent nodes are named.**
Deleting an active-path guard makes the notice-painting nodes loop forever, so those arms
run under `-k "not paints_a_spanish_notice"`, deselecting exactly
`test_tc_r32_the_rail_paints_a_spanish_notice_instead_of_propagating` and
`test_tc_r32_the_factory_tree_paints_a_spanish_notice_instead_of_propagating`, three cycle
shapes each. **Those 6 nodes are not left unmeasured:** N8 reddens the three rail ones and
N9 and N10 redden the three factory ones. No node in the tree escapes every arm.

**The reading that matters, and it was claimed before it was executed.** Compare N1 against
N2, and N9 against N10. The limit-raise arm *does* rescue the depth-5000 acceptance node —
`test_at_r16_the_factory_tree_survives_a_depth_5000_map` is RED under N9 and **GREEN under
N10** — and it likewise rescues
`test_at_r16_depth_safety_does_not_depend_on_the_recursion_limit[rail.visible_rows]`, RED
under N1 and GREEN under N2. What still catches it is
`test_at_r16_a_traversal_never_nests_deeper_than_the_declared_call_depth`, the
frame-counting probe, together with `test_tc_r29`'s AST derivation. §4 of the requirements
predicted precisely this — *"green to 500, dead at 5000, and it moves the crash rather than
fixing it"* — and increment 2's packet asserted it from a node-for-node reading. **It is now
executed rather than reasoned, and the prediction held.** Had the acceptance rested on the
depth-5000 node alone, this batch would have shipped a recursion-limit raise as a fix.

**N6 is the arm that reaches outside this increment's own test file.** Dropping the child
order reversal reddens `tests/test_rail.py::test_rail_collapses_a_branch` and
`tests/test_rail.py::test_rail_lists_the_tree_and_counts_missing_per_branch` — nodes owned
by another requirement — which is trigger B1's reverse census confirmed by execution rather
than by grep.

Raw transcript: `.dev-flow/2026-08-26-repair-batch/03-increments/mutation-battery.txt`.

#### The harness was the finding — five defects, four of which report a FALSEHOOD

The previous session's battery wrote a 0-line log. It was not merely interrupted: **as
written it could not have produced a valid result.** Each defect was found by reading the
harness or by running it, none from the brief, and each is recorded because this failure
mode is the batch's own subject.

| # | Defect | What it would have reported |
|---|---|---|
| 1 | the pytest command carried **both `-v` and `-q`**, which cancel to verbosity 0 | pytest prints dots, **0 nodes resolve**, the baseline is empty, and **every arm reports INERT**. A vacuity detector, vacuous — the C-40 rider's named failure mode, verbatim |
| 2 | no `-o addopts=`, so the `slow` lane stayed deselected | the only nodes that can redden N2 and N10 never run |
| 3 | node-id pattern stops at the first space | one node permanently invisible. Positive control on real pytest output: old pattern **28**, new **29**, the recovered node being the whitespace-id one in `tests/test_attachments.py` |
| 4 | N2 and N10 aim **both** anchors at one file; the restore rebuilt the second target from a snapshot taken **after** the first mutation | wrote the intermediate mutated state back over the good restore — **left `rail.py` mutated on disk** — and the assert fired before the RED ids were printed, destroying the arm's measurement |
| 5 | `read_text`/`write_text` are **not byte-round-trip stable on Windows** | reading folds CRLF to LF, writing expands LF to `os.linesep`. `rail.py` is CRLF, so eight arms round-tripped cleanly; `factory.py` is LF, so arm N9 **rewrote 483 line endings while "restoring" it** |

**Defect 5 is the one worth keeping.** The restore was correct by every check except the
right one: the text was identical, a text comparison passed, and `git status` still read
`M` because the file was already modified. **Only the sha256 caught it.** C-40's requirement
that a restore be proven by hash — and its explicit note that `git status` alone is
insufficient — usually reads as pedantry. It was load-bearing here.

**Defects 4 and 5 are each "the battery left a mutation on disk", which is pending item 8's
failure recurring a second and a third time.** The durable fix is structural and is now
applied: **the harness lives outside the repository it mutates**, so a fault cannot leave an
untracked mutator beside a mutated tracked file. Carried to the post-mortem as a pattern
rather than an accident.

**Restores verified across the whole session, not only per arm.** After the battery, all
twelve files this batch touches were hashed against their session-start values —
`rail.py`, `factory.py`, `model.py`, `mermaid.py`, `store.py`, `app.py`,
`views/radial.py`, `views/outline.py`, `views/layered.py`, `pyproject.toml`,
`tests/test_repair_depth.py`, `tests/test_repair_cycles.py` — **12 of 12 byte-identical**,
and the anchor census re-run post-battery matched every anchor exactly once.

### Signed-balance test ledger

`post = base − deleted + added` → **`356 = 293 − 6 + 69`** ✓ reconciles against a complete
run, not against intent.

- base **293 collected**, the tree state handed to this increment.
- **D = 6**, each with a named predecessor and a strictly stronger successor. Computed by
  diffing the resolved node ids against increment 2's recorded 28:
  - `test_tc_r12_a_cyclic_graph_terminates_instead_of_looping_forever[radial|layered|outline]`
    — replaced by `test_tc_r12_a_cyclic_graph_raises_the_guard_and_names_it` (9 nodes) and
    `test_tc_r12_a_cycle_the_renderer_never_visits_is_asserted_not_absorbed` (3 nodes),
    per finding F2.
  - `test_c53_legacy_fixture_renders_identically_to_master[radial|layered|outline]` — the
    same node re-parametrised over 4 sizes, so the ids gained a size suffix (12 nodes),
    per finding F4.
  No test was skipped or xfailed. `git status --porcelain` shows no modification to any
  file under `tests/` other than `tests/test_repair_depth.py`.
- **A = 69.** `tests/test_repair_depth.py` went 28 → 91 nodes; the whole tree 293 → 356.
- ✓ **Frozen interfaces untouched.** `IRenderer.render` and `Canvas` are not in this diff
  at all — neither `rail.py` nor `factory.py` imports either, and `git diff` for this
  session touches no file under `mapper/views/` or `mapper/canvas.py`.

### Byte-scan — every file this increment touched

Executed after the battery, so these are the bytes that will be committed.

| File | Bytes | BOM | bare CR | TAB | ESC `0x1B` | other control bytes | UTF-8 |
|---|---:|:--:|:--:|:--:|:--:|:--:|:--:|
| `mapper/widgets/rail.py` | 11 300 | ✗ | 0 | 0 | 0 | none | ✓ |
| `mapper/screens/factory.py` | 18 502 | ✗ | 0 | 0 | 0 | none | ✓ |
| `tests/test_repair_depth.py` | 66 715 | ✗ | 0 | 0 | 0 | none | ✓ |

sha256: `b2202db3…761aed`, `6a3e8290…c2dba0`, `3be0c8dd…337bde` — the same digests the
battery restored to, so the scanned bytes and the measured bytes are the same bytes.

Non-ASCII code points are enumerated and all are intentional: `U+00B7` MIDDLE DOT,
`U+00ED`/`U+00F3` accented Spanish vowels, `U+2014` EM DASH, `U+2019`-free, `U+2026`
HORIZONTAL ELLIPSIS, `U+2219` BULLET OPERATOR, `U+25B8` and `U+25BE` the tree glyphs. No
`U+2028`/`U+2029`, no zero-width or bidi characters. Characters following a backslash are
`n`, `s`, `w`, `{`, `}` — regex and format-string escapes, no stray escapes.

**Two columns of this probe report a falsehood, and are corrected rather than pasted.**
The probe is `scratch/bytescan.py`, and reading its output uncritically is the error this
batch keeps naming:

1. **`line ending: MIXED` is wrong for two of the three files.** The probe prints `LF only`
   when the CRLF count is 0 and `MIXED` otherwise, so a file with a *pure CRLF* convention
   is mislabelled. Measured: `rail.py` **269 CRLF / 0 bare LF** and
   `tests/test_repair_depth.py` **1598 CRLF / 0 bare LF** — both pure CRLF, neither mixed.
   `factory.py` is pure LF.
2. **`trailing-ws lines` is an artefact of the same confusion.** It decodes the raw bytes
   and splits on `\n`, leaving the `\r` at the end of every line, so a CRLF file reports one
   trailing-whitespace line per line: `rail.py` 269 of 269, `test_repair_depth.py` 1598 of
   1598. **The true count of lines with trailing whitespace is 0 in all three files.**

**The line-ending split is pre-existing and does NOT reach the commit.** Five of this
batch's files are CRLF in the worktree while `master` holds LF (`rail.py`, `model.py`,
`mermaid.py`, `store.py`, `app.py`); the other five match. `git config core.autocrlf` is
**`true`** and there is no `.gitattributes`, so Git normalises to LF in the object store.
Confirmed by `git diff --numstat` rather than assumed: `rail.py` is **129 added / 14
deleted** against 269 total lines — a content diff, not a whole-file rewrite. Had
normalisation not been in effect, this batch would have put a five-file line-ending churn
into the PR.

### Load-bearing emptiness — C-55

| Field | Value |
|---|---|
| Does any claim rest on the tree holding NO instance of some case? | **Yes** — `test_tc_r29_no_recursive_graph_traversal_outside_the_deferred_member` asserts a derived set minus one member is **empty** |
| What made the search wide enough | the root is `Path(mapper.__file__).parent.rglob("*.py")` — every module in the package, at any depth, not a named list; recursion is a call cycle of any length; the Graph filter is derived from `Graph` itself |
| Guard labelled as protecting a CONCLUSION | `test_tc_r29_the_deferral_record_is_not_stale`, whose docstring says in plain words that it protects a RECORD and not a behaviour, and that it must go RED when increment 3 fixes `resolve_document` |
| Conjunctive criteria, one mutation per conjunct | `LLR-R02.1` is *iterative* **and** *bounded*. N1/N9 mutate the iterative conjunct; N2/N10 mutate it while satisfying the recursion limit; N3/N4/N11/N12 mutate the bound conjunct |
| Synthetic instance of the absent case | `test_tc_r10` builds six synthetic modules containing what `mapper/` now lacks — including the two shapes increment 2's scanner measured `[]` on |
| **Positive control for every probe that returned an ABSENCE** | the unmodified engine returned increment 2's five members on the pre-repair `views/` sources, and returns `{"walk"}`, `{"render.tag"}`, `{"ping","pong"}`, `{"walk"}` on the synthetic modules. The RSS ceiling has its own separate control (above), added because its first version was blind |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rn` for `visible_rows`, `subtree_missing`, `_lattice`, `OutlineRail`, `RAIL_WIDTH`, `FactoryScreen`, `_tree_lines`, `_max_depth`, `_step_meter`, `_depth` across `tests/` and `mapper/` | **fired.** `tests/test_rail.py` asserts `visible_rows()` and `subtree_missing()` at lines 54-58 and 74-78; `mapper/app.py` constructs `OutlineRail` and `FactoryScreen`. All signatures unchanged; `tests/test_rail.py` and `tests/test_factory.py` pass unmodified |
| B2 file moved on disk | `git status --porcelain` — both files show `M`, neither `R` | did not fire |
| B3 byte-identical golden captures this source | this increment INTRODUCES the first goldens for `rail.py` and `factory.py`, as sha256 constants in its own test file, captured from the `master` bytes | not applicable before, pinned now |
| B4 artifact produced here is consumed elsewhere | `grep -rn "OutlineRail\|FactoryScreen" mapper/` → `app.py` lines 46, 621, 1126, 1209, 1226, 1236, 1351, 1759; `screens/__init__.py`; `keymap.py:40` | **fired.** None is touched; every call site uses a signature this increment did not move |
| A3 interface consumed by another module changed | `git diff` for the public members `app.py` calls | **empty** — `show`, `toggle`, `focus`, `display`, `visible_rows`, `subtree_missing`, `render`, and `FactoryScreen.__init__` are byte-identical in signature |

---

## 5 · Risks

1. **`_missing_map` declines a non-forest, and the fallback is quadratic.** Where a node
   has two parents the memo returns `None` and `render` falls back to one exact walk per
   visible row — correct, but back to the cost this increment removed. No such graph can
   reach the rail through the shipped surface today (`mermaid.parse` refuses multiple
   parents; a CSV preview gives every node one parent). If a future door admits one, the
   rail is slow rather than wrong, and nothing measures that.
2. **The rail's indent cap depends on `darkside.fit` continuing to truncate.**
   `test_tc_r30_the_indent_cap_cannot_change_a_rendered_row` asserts the property over
   every depth 0..79, so a change to `fit` reddens — but the assertion tests `fit`'s
   behaviour, not the fact that `_body` still calls it. Someone who removed the `fit` call
   would silently lose the indent on deep rows.
3. **The cycle guard raises a bare English `ValueError`**, matching increment 2 so the
   identity is uniform across the batch. The two surfaces that Textual calls paint Spanish;
   any future sink that surfaces the exception text directly shows English.
4. **The rail refuses a whole map for a cycle in a component it never draws.**
   `visible_rows` walks from the root and would return normally, but `_missing_map` visits
   every node, so a graph with a disconnected `p→q→p` paints the cycle notice even though
   the reachable tree is fine. Measured and asserted. Defensible — the map does contain a
   cycle, and HLR-R01's stance is that a map that cannot be drawn is refused with a
   reason — but it is stricter than `visible_rows` alone.
5. **`layered`'s `KeyError` is now pinned as a recorded outcome.** If increment 2's owner
   fixes it, `test_tc_r12_a_cycle_the_renderer_never_visits_is_asserted_not_absorbed[layered
   -LayeredRenderer]` reddens. That is deliberate: the record must be updated by whoever
   changes the behaviour. It is a maintenance cost, and it is the price of not letting
   `Exception` absorb it.
6. **The RSS watchdog samples every 50 ms.** A single allocation between two samples could
   exceed the ceiling unseen. The wall clock bounds the child regardless, so the failure
   mode is a slower report, not a missed one.
7. **The default gate no longer runs the depth-5000 acceptance.** `addopts = "-m 'not
   slow'"` keeps the default lane at 47 s, and `AT-R16` lives in the 14 deselected nodes.
   **If CI runs only the default lane, HLR-R02's acceptance stops being tested.** The
   marker's help text and the `pyproject.toml` comment both say so; the durable fix is a
   second CI lane running `-m slow`, which is not this increment's to add. The cost fix
   itself is pinned in the fast lane by the two scan-count nodes, deliberately.
8. **`_max_depth`'s answer on a cyclic graph is path-dependent** and is not claimed to
   equal the shipped `_depth`'s — the shipped one never returned on a cycle. Equivalence is
   asserted only where the shipped implementation terminated, which is `LLR-R02.2`'s own
   scope.

---

## 6 · Pending items / spec deviations

1. **`Graph.resolve_document` is still recursive** (`mapper/model.py:97`, a self-call up
   the parent chain). Reproduced here at depth 5000 with a positive control at depth 3.
   `mapper/model.py` is fenced from this increment and amendment A-3 already disposed this
   member to **increment 3**, which opens that file. It is carried as
   `DEFERRED_BY_AMENDMENT_A3`, a single member backed by a requirement id, with
   `test_tc_r29_the_deferral_record_is_not_stale` as its anti-rot guard. **That guard must
   go RED the moment increment 3 makes it iterative, and the record must be deleted in the
   same commit.** Arm N17 proves the guard can actually fail.
2. **`FactoryScreen._depth` was a `while True` with no cycle guard, and no AST probe could
   ever have named it.** It is not recursive, so neither increment 2's derivation nor the
   widened one in this increment would have reported it; it was found by reading every
   method in the file. **This is the limit of the whole derived-probe approach and it
   belongs in the post-mortem:** the probe answers the question it encodes — "what
   recurses" — not the question the requirement asks, which is "what fails to terminate".
   `LLR-R02.1` says *iterative **or explicitly depth-bounded***, and a probe scoped to
   recursion can only ever see the first conjunct.
3. **`_rss_bytes()` returned 0 on every call in its first version**, so the RSS ceiling was
   decoration and the watchdog could never fire — `GetCurrentProcess` defaults to a C `int`
   restype and its pseudo-handle was truncated on 64-bit. **A probe that can only return
   "nothing found" is not a probe.** Same family as batch 1's regex that collapsed to a
   control byte and passed on everything. It now raises rather than returning 0, and it has
   its own positive control that drives the child with a 4 MB ceiling and requires the
   watchdog to trip. For the post-mortem.
4. **The mutation harness's node pattern silently dropped one node of 356. CLOSED.**
   `tests/test_attachments.py` has a parametrized node whose id is whitespace-only, and a
   node-id pattern built from non-space characters stops at the first space. Increment 2's
   packet records the same pattern and claims full coverage of its own 28-node file, which
   is true there and would not have been true tree-wide. A measuring instrument that
   under-reports and says nothing about it. **Fixed and proven by a positive control on
   real pytest output — old pattern 28 nodes, new pattern 29, the recovered node named** —
   and the battery now asserts an expected baseline node COUNT before trusting any verdict,
   because an arm the harness cannot see is an arm it cannot report inert. See §4 defect 3.
5. **`layered`'s `KeyError` on a disconnected cyclic component** (`mapper/views/layered.py`,
   `_tree_layout` indexing a node it never placed). Verified pre-existing on `master`, so
   not a regression and not this increment's file. **Named for increment 2's owner.**
6. **The `master` goldens still have no checked-in regeneration tool.** Increment 2 raised
   this; this increment captured 18 more digests the same way — a scratch script loading
   `git show HEAD:mapper/views/*.py` into a temporary package — and then deleted it under
   the working-file rule. Carried forward, unchanged.
7. **A CI lane for `-m slow` does not exist.** See Risk 7. This increment registered the
   marker and confirmed both lanes locally; wiring CI is outside it.
8. **The battery left a mutation applied on disk — THREE times, by three different
   mechanisms.** This is the increment's most repeated defect and it belongs in the
   post-mortem as a pattern, not as three accidents.
   - **(i)** the original session's battery was killed mid-arm, leaving `rail.py` mutated.
   - **(ii)** the same-file double-mutation restore (§4 defect 4) wrote the intermediate
     mutated state back over a correct restore, leaving `rail.py` mutated again — and,
     because the restore assertion fired before the verdict was printed, it also destroyed
     the arm's 9 RED node ids.
   - **(iii)** the text-mode round trip (§4 defect 5) "restored" `factory.py` while
     rewriting **483 line endings**, which no text comparison and no `git status` could see.
   All three were recovered by reversing the exact edit and **proving the restore by
   sha256**, then re-running the suite green. **Only the hash ever caught (iii)** — which is
   the concrete argument for C-40's rule that `git status` is not an acceptable restore
   proof.
   **Structural fix applied:** the harness and its anchor tables now live **outside the
   repository they mutate**, so a fault can no longer leave an untracked mutator beside a
   mutated tracked file. The battery additionally restores in `try/finally`, prints the
   verdict *before* asserting the restore, and halts the whole run on any restore mismatch
   rather than continuing into contaminated measurements.

---

## 7 · Suggested next task

**Increment 3 — `HLR-R03`, field-type integrity (S-02),** which owns `store.py`,
`model.py` and `app.py`. Carry two things into it:

1. **`Graph.resolve_document`** (pending item 1). `model.py` is already open in that
   increment, A-3 already assigned it, and the failure is reproduced above with a positive
   control. Deleting `DEFERRED_BY_AMENDMENT_A3` is part of the work, not a follow-up —
   `test_tc_r29_the_deferral_record_is_not_stale` will insist.
2. **Amendment A-2's `MapStore.save` refusal.** Until it lands, a cyclic graph can still be
   written by `_ImportPreviewScreen.action_save`, and that is the only door through which a
   cyclic graph reaches the rail at all — the guards added here are otherwise unreachable
   through the shipped surface. They are still required by `LLR-R02.1`'s second conjunct,
   because an unbounded loop is worse than a bounded crash whether or not today's callers
   can trigger it.

Then a small follow-up, unowned: a CI lane for `-m slow` (Risk 7).

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|
| 1 | ≤ budget source files, or reason declared | ✓ | **2 source files**, §2. One was the declared budget (`rail.py`); the second (`factory.py`) is a derived member of the widened probe owned by no increment in §5, declared and approved before implementation |
| 2 | Tests written in this same increment | ✓ | `tests/test_repair_depth.py`, 28 → 91 nodes |
| 3 | Layer 0 written where the criterion applies | ✓ | `TC-R30` / `TC-R31` equivalence against verbatim copies of all four shipped implementations; `TC-R29` derivation + two positive-control nodes; the two scan-count pins |
| 4 | RED counterfactual captured **and restored by hash** | ✓ | **14 arms** (the packet previously said 19 — corrected against the transcript), §4 matrix; **0 inert, 0 failed restores, 72 RED node-verdicts**; every arm's sha256 returned to its pre-mutation value; baseline and post-battery runs both **356/356 passed**; all arms `PYTHONDONTWRITEBYTECODE=1` with `__pycache__` purged. Transcript: `03-increments/mutation-battery.txt` |
| 5 | Reverse census run on every touched symbol | ✓ | §4 reverse census: B1 fired (`tests/test_rail.py`, `mapper/app.py`), B2, B3, B4 fired (`app.py`, `screens/__init__.py`, `keymap.py`), A3 empty |
| 6 | `code-reviewer` passed — a HIGH blocks | ⚠ | **not run by this agent.** Independent review is the orchestrator's gate; requested. This increment exists *because* increment 2's review raised a HIGH |
| 7 | No file from another lane touched | ✓ | `git status --porcelain`: this session modified `mapper/widgets/rail.py`, `mapper/screens/factory.py`, `tests/test_repair_depth.py`, `pyproject.toml` and this packet. `model.py`, `mermaid.py`, `store.py`, `app.py` and `mapper/views/**` carry other increments' work and were read only |
| 8 | Frozen interfaces untouched | ✓ | `IRenderer.render` and `Canvas` are not in this diff; neither touched file imports either |
| 9 | Coverage claims verified **on disk**, not from intent | ✓ | ledger `356 = 293 − 6 + 69` reconciled against `--collect-only`; D computed by diffing resolved node ids against increment 2's recorded 28; both lane runtimes measured |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | ✓ | §4 C-55 table; six synthetic shapes in `test_tc_r10`; the RSS ceiling carries its own separate control after its first version was measured blind |
| 11 | Mutation verdicts recorded **per arm**, inert arms named | ✓ | §4 matrix, one row per resolved arm, node ids never exit codes. **`INERT ARMS: none`** and **`FAILED RESTORES: none`** printed by the run itself; the 6 nodes deselected on the four guard-deletion arms are named, and each is reddened by another arm |
| 12 | Working files reconciled | ✓ | `scratch/` (11 files) and `out.txt` **moved out of the repository** to the session scratchpad, not merely deleted, so the anchor tables survive for increments 3 and 4. `git status --porcelain` now shows only the 11 intended modifications, the two new test files, the batch docs, and `prototypes/**` — which is untracked **by design and never staged** |
| 13 | Harness lives outside the tree it mutates | ✓ | structural fix for §4 defects 4 and 5 — the previous session left a mutation applied *and* the mutator untracked beside it. `battery.py` and the anchor tables are now under the scratchpad; the repo holds neither |
