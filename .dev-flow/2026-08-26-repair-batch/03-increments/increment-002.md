# Increment 002 — HLR-R02 · `depth safety in mapper/views`

| Field | Value |
|---|---|
| Batch | `2026-08-26-repair-batch` |
| Increment | `002` |
| Lane (if the batch forked) | not forked · this increment owns `mapper/views/**` and `tests/test_repair_depth.py` |
| Requirement(s) | `HLR-R02` · `LLR-R02.1`, `LLR-R02.2`, `LLR-R02.3` |
| Acceptance | `AT-R04`, `AT-R05` · white-box `TC-R10` through `TC-R14` · unit: `_leaf_counts`, `_tree_layout.walk`, `subtree_counts` |
| Agent | `software-dev` (supervised-incremental-development) |
| Date | 2026-08-26 |

---

## 1 · What changed

**A depth-5000 acyclic chain now draws in 0.04 s on all three renderers; before this
increment a depth-500 chain died with `RecursionError` in 0.01 s.** The operator reaches this
through `MapScreen`, whose renderer is one of the three touched here.

The mechanism: every graph traversal in `mapper/views/` is now a flat loop over an explicit
stack, and each loop declares its own bound on the active path. Three secondary changes fell
out of the same work and are named because they change cost, not behaviour:

- **Adjacency is indexed once per render.** `Graph.children_of` and `Graph.parent_of` rescan
  the whole edge list on every call, so the old renderers were `O(N·E)`. `model.py` belongs to
  increment 1 and is not touched; the index is built locally in each view module.
- **`outline.subtree_counts` was quadratic** — it re-walked the whole subtree for every
  internal node. It is now one memoised post-order pass.
- **`layered` painted a canvas taller than the terminal** and then threw the extra rows away at
  the `lines[:h]` slice. On a deep chain that was the dominant cost: 0.985 s → 0.039 s at depth
  5000. No visible output changes, because those rows were never emitted.

Above a **declared bound of 12000 nodes** each renderer paints a Spanish degradation naming what
it dropped and returns normally instead of drawing (`LLR-R02.3`).

**The surprise, and the reason this increment is not just "remove the recursion".** Making the
traversals iterative turned a *bounded crash* into an *unbounded hang*. The recursion used to
answer a cyclic graph with `RecursionError`, which increment 1's screen guards catch; a plain
loop answers it by never returning. Increment 1's own
`test_tc_r08b_import_preview_survives_a_cyclic_csv` caught it — the run stalled at that node
with the interpreter at 23.7 GB resident. Cycles are refused at load by HLR-R01, but
`_ImportPreviewScreen` builds a graph from a CSV without going near the parser, so each
traversal now carries an active-path guard and raises instead of looping. That is the
"**or explicitly depth-bounded**" half of `LLR-R02.1`, and it is not optional.

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped.**

| File | Kind | Change |
|---|---|---|
| `mapper/views/radial.py` | source | `_leaves` iterative + memoised via new `_leaf_counts`; `place` and `tag` closures converted to stack loops; child/parent adjacency indexed; `MAX_RENDER_NODES` + `_degraded` |
| `mapper/views/layered.py` | source | `_tree_layout.walk` converted to a stack loop with an active-path bound; adjacency indexed in `_tree_layout` and in `render`; canvas height capped to the visible height; `MAX_RENDER_NODES` + `_degraded` |
| `mapper/views/outline.py` | source | `walk` converted to a stack loop; `subtree_counts` made one memoised post-order pass with an active-path bound; adjacency indexed; `MAX_RENDER_NODES` + `_degraded` |
| `tests/test_repair_depth.py` | test | new, 28 nodes |

| Count | Value |
|---|---|
| **SOURCE files** | **3** / 4 |
| Test files | 1 (uncapped) |
| Doc files | 1 — this packet (outside the count) |

- Not at the cap. The AST derivation (§4) found recursion in exactly these three modules;
  `mapper/views/lane.py` and `mapper/views/__init__.py` contain no recursive function, so the
  fourth-file allowance was not needed.
- **No file outside `mapper/views/` was read-modify-written.** Increment 1's set
  (`model.py`, `mermaid.py`, `store.py`, `app.py`) is disjoint and was left alone; a
  concurrent session holds uncommitted work there.
- ✓ **Frozen interface untouched.** `git diff -U0 -- mapper/views/` filtered for every line of
  every `render` signature returns **empty**. `IRenderer.render` and `Canvas` are byte-identical
  to `master` in this diff.

---

## 3 · How to test

```bash
cd C:/Users/jjgh8/Github/mapper

# the gate run
PYTHONUTF8=1 python -m pytest -q -p no:randomly > out.txt 2>&1

# this increment alone, per-node
PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_repair_depth.py \
    -p no:randomly -v --tb=short

# lint
python -m ruff check mapper tests
```

---

## 4 · Test results

**One complete run.** `PYTHONUTF8=1 python -m pytest -q -p no:randomly > out.txt 2>&1`
→ exit `0`, tail of `out.txt`:

```
293 passed in 39.33s
```

| Layer | Nodes | Result |
|---|---|---|
| **0 · unit** — `_leaf_counts` value equivalence, the AST derivation and its own positive control | `test_tc_r10_the_ast_derivation_finds_the_functions_it_is_supposed_to_find`, `test_tc_r11_no_graph_traversal_in_views_is_recursive`, `test_tc_r13_leaves_agrees_with_the_shipped_recursive_implementation` | 3 passed |
| **A · white-box** `TC-R10` … `TC-R14` ↔ LLR | the 3 above + `test_tc_r12_a_cyclic_graph_terminates_instead_of_looping_forever` ×3, `test_tc_r14_the_renderers_declare_one_shared_bound`, `test_tc_r14_a_map_past_the_bound_degrades_in_spanish_and_does_not_raise` ×3, `test_tc_r14_a_map_at_the_bound_still_draws` ×3 | 13 passed |
| **B · black-box** `AT-R04`, `AT-R05` through the shipped surface | `test_at_r04_a_deep_acyclic_chain_renders_through_the_shipped_surface` ×3, `test_at_r04_depth_safety_does_not_depend_on_the_recursion_limit` ×3, `test_at_r04_a_render_never_nests_deeper_than_the_declared_call_depth` ×3, `test_at_r05_a_3000_node_tree_renders_within_the_declared_bound` ×3, `test_c53_legacy_fixture_renders_identically_to_master` ×3 | 15 passed |

`ruff check mapper tests` → **29 findings, the pre-existing count.** Filtering the concise
output for `views/` and `test_repair_depth` returns **0 lines**: this increment adds none.

### The RED — reproduced before anything was written

```
$ PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python scratch/red.py
nodes=501 edges=500 recursionlimit=1000
RadialRenderer: RecursionError at radial.py:24 in _leaves (frames=1000)
LayeredRenderer: rendered OK
OutlineRenderer: rendered OK
```

Same script after the change:

```
nodes=501 edges=500 recursionlimit=1000
RadialRenderer: rendered OK
LayeredRenderer: rendered OK
OutlineRenderer: rendered OK
```

Note what the RED also says: **at depth 500 only `radial` dies.** `layered` and `outline`
recurse one frame per level and survive 500 under the default limit of 1000. That fact is what
forces the fixture-depth decision below.

### The AST-derived traversal set — `LLR-R02.1`, control C-31

The set is produced by walking the AST of every module in `mapper/views/` and reporting each
function that calls its own name or an enclosing function's name. It is not hand-listed; the
derivation ships as `recursive_functions_in_views()` in the test file, so a recursive traversal
added to `views/` later reddens `test_tc_r11` by construction.

**Before this increment** (five members, three modules):

```
mapper/views/layered.py:46 walk
mapper/views/outline.py:48 walk
mapper/views/radial.py:23 _leaves
mapper/views/radial.py:54 place
mapper/views/radial.py:95 tag
```

**After:** empty. `lane.py` and `__init__.py` never appeared in either run — they contain no
recursive function, which is why the source budget is 3 and not 4.

The derivation's own positive control is `test_tc_r10`: the same `_scan` is run over two
synthetic modules that *do* recurse — one plain, one nested closure — and must report them.
An empty result from a blind probe and an empty result from a working probe are otherwise
textually identical.

### The design decision — why the fixture is depth 5000

`AT-R04`'s declared plausible-weaker arm is `sys.setrecursionlimit`. At depth 500 that arm is
green, so a depth-500 fixture cannot tell a fix from a limit-raise. Two measurements settled
the depth (both executed, neither predicted):

| Probe | Result |
|---|---|
| shipped `sum(genexpr)` recursion under `sys.setrecursionlimit(1_000_000)`, binary-searched | terminates at depth **1499** and no further — CPython 3.12's separate C-recursion ceiling, which the recursion limit does not lift |
| plain Python-to-Python recursion (`walk` shape) under the same raised limit | survives depth **200000** in 0.128 s — a limit-raise *does* rescue this shape |

So depth 5000 makes a limit-raise useless against `radial`, but not against `layered`/`outline`.
Those are pinned from the other side by two further predicates:

1. `test_at_r04_depth_safety_does_not_depend_on_the_recursion_limit` **lowers** the limit to
   `current stack depth + 120` around the render. An implementation that raised the limit from
   *outside* cannot pass.
2. `test_at_r04_a_render_never_nests_deeper_than_the_declared_call_depth` counts frames with a
   `sys.setprofile` hook and requires a peak of ≤ 40. Measured peak on the depth-5000 chain:
   **radial 5, layered 5, outline 5.** This is the arm-proof form — see M10 below, an
   implementation that raises the limit from *inside* `render` defeats (1) but not (2).

### The measured bound — `AT-R05` and `LLR-R02.3`, control C-39

Worst of five repeats per cell, `w=140 h=45`, Python 3.12.7 on win32:

```
shape                                       radial     layered     outline
--------------------------------------------------------------------------
AT-R05  balanced tree, 3000 nodes          0.0885s     0.0416s     0.0253s
AT-R04  chain, depth 5000                  0.0383s     0.0547s     0.0804s
at the bound: balanced 12000               0.2197s     0.2051s     0.0798s
at the bound: chain 11999                  0.0973s     0.1525s     0.2899s
past the bound: balanced 12001             0.0000s     0.0000s     0.0000s
legacy.mmd (8 nodes)                       0.0033s     0.0033s     0.0001s
```

`MAX_RENDER_NODES = 12000` is chosen from the cost curve past it, measured with the bound
temporarily lifted (worst of three):

```
chain 6000                       0.0466s     0.0528s     0.1020s
chain 12000                      0.0974s     0.1003s     0.2558s
chain 24000                      0.1871s     0.2106s     1.0080s
chain 48000                      0.4146s     0.4659s     3.8867s
balanced 48000                   0.5739s     0.7463s     0.2655s
```

`outline` sets the bound: its per-line indent is `"  " * depth`, so a deep chain is quadratic in
characters and crosses one second between 12000 and 24000 nodes. 12000 is the largest round
figure whose worst measured render stays under 0.3 s, and it is 4× the `AT-R05` fixture.
**`RENDER_BOUND_SECONDS = 2.0`** in the test — ~7× the worst measurement anywhere at or under
the node bound, headroom for a loaded machine.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | ten arms, one at a time — see the matrix |
| Where it ran | **my own tree**, `C:/Users/jjgh8/Github/mapper`, files under `mapper/views/` only |
| Restore proven by | **sha256 of the file returned to its pre-mutation value**, asserted in the harness after every arm; every arm printed `<sha> == <sha>` |
| Bytecode cache | every arm run with `PYTHONDONTWRITEBYTECODE=1` |
| Arms resolved at baseline | **28** — printed by the harness as `BASELINE: 28 nodes, 28 passed` before the first mutation. The node pattern is `^tests[/\\]\S+?::\S+? (PASSED\|FAILED\|ERROR)`, which resolves parametrized ids; 28 is the full collected count of the file, so no arm was invisible |
| Verdict granularity | **per resolved node id**; the process exit code is not used anywhere below |
| Arms that stayed GREEN | **none.** Every one of the ten arms reddened at least one node |

Mutations are described **by position and operation**; no mutated token is reproduced here.

| Arm | Kind | File | Operation | Nodes reddened |
|---|---|---|---|---|
| **M1** | deletion | `radial.py` | replace the body of the module-level `_leaves` with the pre-repair recursive definition | `test_tc_r11_no_graph_traversal_in_views_is_recursive` |
| **M2** | deletion | `radial.py` | replace the `place` closure's stack loop in `RadialRenderer.render` with a self-call per child | `test_at_r04_a_deep_acyclic_chain_renders_through_the_shipped_surface[radial-RadialRenderer]`, `test_at_r04_a_render_never_nests_deeper_than_the_declared_call_depth[radial-RadialRenderer]`, `test_at_r04_depth_safety_does_not_depend_on_the_recursion_limit[radial-RadialRenderer]`, `test_tc_r11_no_graph_traversal_in_views_is_recursive` |
| **M3** | deletion | `layered.py` | replace `_tree_layout.walk`'s stack loop and its active-path bound with a self-call per child | `test_at_r04_a_deep_acyclic_chain_renders_through_the_shipped_surface[layered-LayeredRenderer]`, `test_at_r04_a_render_never_nests_deeper_than_the_declared_call_depth[layered-LayeredRenderer]`, `test_at_r04_depth_safety_does_not_depend_on_the_recursion_limit[layered-LayeredRenderer]`, `test_tc_r11_no_graph_traversal_in_views_is_recursive`, `test_tc_r12_a_cyclic_graph_terminates_instead_of_looping_forever[layered-LayeredRenderer]` |
| **M4** | plausible-weaker | `radial.py` | M1 **plus** a module-level call raising the recursion limit to 100000 | `test_tc_r11_no_graph_traversal_in_views_is_recursive` |
| **M5** | plausible-weaker | `layered.py` | M3 **plus** a call raising the recursion limit to 100000 executed inside `_tree_layout` | `test_at_r04_a_render_never_nests_deeper_than_the_declared_call_depth[layered-LayeredRenderer]`, `test_tc_r11_no_graph_traversal_in_views_is_recursive`, `test_tc_r12_a_cyclic_graph_terminates_instead_of_looping_forever[layered-LayeredRenderer]` |
| **M6** | deletion | `radial.py` | delete the two-line size guard at the head of `RadialRenderer.render` | `test_tc_r14_a_map_past_the_bound_degrades_in_spanish_and_does_not_raise[radial-RadialRenderer]` |
| **M7** | plausible-weaker | `radial.py` | lower `MAX_RENDER_NODES` from its declared value to 2, so every real map degrades | `test_c53_legacy_fixture_renders_identically_to_master[radial-RadialRenderer]`, `test_tc_r12_a_cyclic_graph_terminates_instead_of_looping_forever[radial-RadialRenderer]`, `test_tc_r14_a_map_past_the_bound_degrades_in_spanish_and_does_not_raise[layered-LayeredRenderer]`, `test_tc_r14_a_map_past_the_bound_degrades_in_spanish_and_does_not_raise[outline-OutlineRenderer]`, `test_tc_r14_the_renderers_declare_one_shared_bound` |
| **M8** | plausible-weaker | `radial.py` | in `_leaf_counts`, replace the post-order sum over children with the constant 1 — iterative, depth safe, fast, and wrong | `test_c53_legacy_fixture_renders_identically_to_master[radial-RadialRenderer]`, `test_tc_r13_leaves_agrees_with_the_shipped_recursive_implementation` |
| **M9** | plausible-weaker | `layered.py` | drop the order reversal on the child push in `_tree_layout.walk` — still iterative, still depth safe, ordinary maps come out mirrored | `test_c53_legacy_fixture_renders_identically_to_master[layered-LayeredRenderer]` |
| **M10** | plausible-weaker | `radial.py` | M2 **plus** a call raising the recursion limit to 100000 executed **inside** `RadialRenderer.render`, so a limit pinned from outside is overwritten before the traversal runs | `test_at_r04_a_render_never_nests_deeper_than_the_declared_call_depth[radial-RadialRenderer]`, `test_tc_r11_no_graph_traversal_in_views_is_recursive` |

**What the matrix says, beyond "nothing was inert".**

- **M5 and M10 are the point of the increment.** Both are the declared plausible-weaker arm in
  its strongest form, and both stayed **green** on
  `test_at_r04_a_deep_acyclic_chain_renders_through_the_shipped_surface` *and* on
  `test_at_r04_depth_safety_does_not_depend_on_the_recursion_limit`. A limit raised from inside
  the render defeats a limit pinned from outside it. Only the frame-counting predicate and the
  AST derivation caught them. Had this increment shipped with the deep-chain test alone, the
  limit-raise non-fix would have passed the gate.
- **M1 and M4 reddened only the AST derivation.** That is correct rather than weak: after the
  rewrite the render path calls `_leaf_counts` directly, so mutating the thin `_leaves` facade
  changes nothing a render can observe. The derived structural test is exactly the control that
  notices — which is C-31's argument, executed. `_leaves` is kept because `LLR-R02.2` names it
  and it is the equivalence point of the positive control; see §6.
- **M8 is the positive control's own arm.** A wrong-but-fast `_leaf_counts` passes every depth
  and timing predicate. Only `TC-R13` (agreement with the shipped recursion) and the C-53
  golden see it.
- **M7 and M9 are the false-failure arms (C-53).** Both leave depth safety intact and both
  wreck ordinary output; both are caught by the `master` goldens.

**Suite immediately after the battery:** `293 passed`, exit `0` — the same numbers as before it.

### Load-bearing emptiness — C-55

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | **Yes** — `test_tc_r11` asserts the derived recursive-function set is **empty** |
| If the result is an ABSENCE, what made the search wide enough | the probe walks `VIEWS_DIR.glob("*.py")` — every module in the package, not a named list — and flags a call to the function's own name **or any enclosing function's name**, at any nesting depth, via `ast.Name` and `ast.Attribute` call targets |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_tc_r11_no_graph_traversal_in_views_is_recursive` — its docstring names the five functions that used to be in the set and states explicitly that they are *not* named in the assertion, so a future reader cannot "simplify" the derivation into a list |
| Conjunctive criteria: one mutation per conjunct | `LLR-R02.1` is conjunctive — *iterative* **and** *bounded*. M2/M3 mutate the iterative conjunct; M5/M10 mutate it while satisfying the limit; `TC-R12` covers the bound conjunct, and M3 reddens it independently of the depth nodes |
| Synthetic instance of the absent case | `test_tc_r10` builds two synthetic modules that contain what `mapper/views/` now lacks — a plain self-recursive `walk` and a nested self-recursive closure — and requires the same unmodified `_scan` to report both |
| **Positive control for every probe that returned an ABSENCE** | the same `_scan`, unmodified, returned `{"synthetic.py:1 walk"}` and `{"synthetic.py:2 tag"}` on the known-present cases; and it returned the five-member set quoted above on the pre-repair sources. Both are non-empty outputs from the probe that returns empty on today's tree |

The `LLR-R02.2` positive control has the same shape and is answered the same way: `TC-R13`
compares against a verbatim copy of the pre-repair recursive `_leaves` over **8 shapes**
(single node, shallow chain, 150-deep chain, star, 300-node balanced tree, diamond, uneven
tree, `fixtures/legacy.mmd`), node by node — **487 comparisons**, asserted as an exact count so
a truncated shape set cannot pass vacuously. The diamond is in the set on purpose: it is the
one shape where memoisation could have changed an answer and does not.

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl <symbol> tests/` for `_leaves`, `_leaf_counts`, `_child_index`, `_parent_index`, `_tree_layout`, `_degraded`, `subtree_counts`, `_indent`, `_vis_width`, `_clip`, `_fit`, `STATE_STYLE`, `_GREYS`, `MAX_RENDER_NODES` | only `tests/test_repair_depth.py` (this increment's own file) matches any of them. **No other test file reads a symbol touched here** — did not fire, and this is the probe |
| B2 file moved on disk | `git status --porcelain` shows the three view modules as `M`, none as `R`; no path under `mapper/views/` changed | did not fire — no renames |
| B3 byte-identical golden captures this source | `ls tests/ \| grep -i golden` → nothing; `grep -rl "snap_compare\|syrupy\|snapshot" tests/` → one hit, `tests/test_worklist_safety.py`, and inspecting its three matching lines shows they are prose about `MapScreen._snapshots` (the undo stack), not a captured render | did not fire — the repo keeps no golden capture of any view renderer. This increment introduces the first pinned captures, as sha256 constants inside its own test file |
| B4 artifact produced here is consumed elsewhere | `grep -rln "RadialRenderer\|LayeredRenderer\|OutlineRenderer" mapper/ --include=*.py` → `mapper/app.py`, `mapper/widgets/rail.py`, `mapper/views/__init__.py` | **fired.** Two modules outside `views/` construct these renderers. Neither is touched: they call `render(...)`, whose signature is unchanged |
| A3 interface consumed by another module changed | `git diff -U0 -- mapper/views/` filtered for every parameter line of every `render` signature | **empty** — did not fire. `IRenderer.render` is byte-identical to `master`; no frozen interface moves in this increment |

### Signed-balance test ledger

`post = base − deleted + added` → **`293 = 265 − 0 + 28`** ✓ reconciles.

- base **265 collected**, the tree state handed to this increment (245 baseline + increment 1's 20).
- **D = 0.** No test was deleted, renamed, skipped, or xfailed. `git status --porcelain` shows no
  modification to any file under `tests/` other than the new `tests/test_repair_depth.py`.
- **A = 28**, all in the new file: `pytest tests/test_repair_depth.py --collect-only -q` →
  `28 tests collected`.
- Full-tree collection: `pytest -q -p no:randomly --collect-only` → `290 tests collected` at the
  time of the mid-increment check and `293` after the last three nodes were added; the gate run
  reports `293 passed`.

### Byte-scan — every file this increment touched

| File | bytes | sha256 | BOM | CRLF / bare CR | TAB | ESC `0x1B` | other control bytes | trailing-ws lines |
|---|---|---|---|---|---|---|---|---|
| `mapper/views/radial.py` | 9414 | `d9a4f61cb93592d6ef0573440782bc5fbb37c541aa50b87ba3cd0b4288d7a4be` | no | 0 / 0 | 0 | 0 | none | 0 |
| `mapper/views/layered.py` | 11561 | `46184a1fcea8452635efc912b314de6c11f2ce9504ad48622b7734ea18649e5e` | no | 0 / 0 | 0 | 0 | none | 0 |
| `mapper/views/outline.py` | 5857 | `df923ddb077c5d0d1ec6c69d491555d65f633d20f4a814a84e4aef1b2ec96e73` | no | 0 / 0 | 0 | 0 | none | 0 |
| `tests/test_repair_depth.py` | 18088 | `8f2d21dedcb634889bdb297eadba64801654ebbce3d8146f039ce8fd45aae6be` | no | 0 / 0 | 0 | 0 | none | 0 |

All four decode as UTF-8 and use bare LF throughout.

**Escape sequences.** No escape sequence was authored into any file by this increment. The new
degradation helpers emit their blank line with a code-point construction rather than a spelled
escape. The three view modules each still carry **one** distinct backslash sequence —
*U+006E after a backslash* — in the pre-existing `result.append(...)` line that joins canvas
rows, present on `master` and untouched here under the surgical-changes rule. The new test file
carries **none**.

**Non-ASCII.** All Spanish accented characters used in *assertions* are constructed from code
points (`chr(0xF3)`, `chr(0xED)`), following `tests/test_repair_cycles.py`'s convention; the two
occurrences the scanner reports in the test file are in the trailing comments that show the
intended Spanish for a human reader. The view modules' non-ASCII inventory is the existing
palette of box-drawing and marker glyphs (U+25C6, U+2590, U+2500, U+2713, U+00B7 …) plus the two
accented letters in the new Spanish notices; every code point was enumerated by name in the scan.

---

## 5 · Risks

1. **The cycle guard raises a bare `ValueError`.** For a cyclic graph the traversals now raise
   rather than hang. That is what increment 1's screen guards expect — they are scoped to the
   sink class, not to an exception type — but the exception carries no Spanish text of its own.
   If a future sink ever surfaces the exception message directly, the operator sees English.
   The three sinks that exist today paint their own Spanish notice.
2. **A DAG that re-converges is bounded but not exercised in production.** The rewrite is
   faithful for trees, and `TC-R13` includes a diamond, but `mermaid.parse` has refused multiple
   parents since long before this batch, so no DAG reaches a renderer through the shipped
   surface. `radial.tag` keeps the pre-repair no-visited-set behaviour and would blow up on a
   deeply re-convergent DAG — as the recursion did — but it is now protected upstream because
   `_leaf_counts` runs first and raises on the same graph.
3. **The `master` goldens are sha256, not readable text.** If one reddens it says *what*
   changed, not *where*. The regeneration recipe is a scratch script, not a checked-in tool.
4. **`MAX_RENDER_NODES` is one number for three cost profiles.** `outline` sets it because of a
   deep chain; `radial` and `layered` could afford roughly 2× more on a wide tree. Real maps at
   that size do not exist yet, so a single shared bound is the simpler statement — but a wide
   12000-node map degrades earlier than it strictly must.
5. **The canvas-height cap in `layered` relies on the `lines[:h]` slice staying at the end of
   `render`.** If a future change emits rows past `h`, the cap silently truncates. Nothing
   asserts the two agree.
6. **The frame-counting oracle uses `sys.setprofile`.** If a future test installs its own
   profile hook, or a coverage run is active, the hook is displaced and the peak reads as 0 —
   a false *pass*. It is restored in a `finally` and the suite currently installs no other hook.

---

## 6 · Pending items / spec deviations

1. **`_leaves` is now a facade the render path does not call.** `LLR-R02.2` names it and
   `TC-R13` uses it as the equivalence point, so it stays; but M1 showed that mutating it is
   invisible to every behavioural predicate. Either the LLR should name `_leaf_counts` or
   `_leaves` should be retired once the positive control has served its purpose. Backlog.
2. **The `master` render goldens have no regeneration tool in the repo.** They were captured by
   loading `git show HEAD:mapper/views/*.py` into a scratch package. Worth a small checked-in
   script before the next renderer change. Backlog.
3. **Risk 5 has no assertion.** A test tying `layered`'s canvas height to the emitted row count
   would close it. Not written here — it is outside `HLR-R02` and would have widened the
   increment. Backlog.
4. **`Graph.resolve_document` in `mapper/model.py` is recursive** (`model.py:108`, a self-call
   through the parent chain). It is outside `mapper/views/`, so `LLR-R02.1` does not reach it
   and this increment does not touch `model.py` — that file belongs to increments 1 and 3. It
   walks the parent chain, so a deep map makes it deep too. **Named for increment 3.**
5. **`out.txt` is left in the repo root** as the gate evidence the batch asked for. It is
   untracked and should not be committed.

---

## 7 · Suggested next task

**Increment 3 — `HLR-R03`, field-type integrity (S-02).** It touches `store.py`, `model.py` and
`app.py`, which is disjoint from this increment's file set but shared with increment 1, so it
must start from a tree where increment 1 is settled. Carry item 4 above into it: `model.py` is
already open in that increment, and `resolve_document`'s recursion is the same defect class this
one just closed, one module over.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|
| 1 | ≤4 source files, or reason declared | ✓ | 3 source files, §2. AST derivation found recursion in exactly those three modules; `lane.py` and `__init__.py` clean |
| 2 | Tests written in this same increment | ✓ | `tests/test_repair_depth.py`, 28 nodes, new in this increment |
| 3 | Layer 0 written where the criterion applies | ✓ | `test_tc_r13_leaves_agrees_with_the_shipped_recursive_implementation` (487 node comparisons over 8 shapes), `test_tc_r11_no_graph_traversal_in_views_is_recursive`, `test_tc_r10_the_ast_derivation_finds_the_functions_it_is_supposed_to_find` |
| 4 | RED counterfactual captured **and restored by hash** | ✓ | 10 arms, §4; each printed its sha256 equal before and after restore; all run with `PYTHONDONTWRITEBYTECODE=1`; suite `293 passed` immediately after the battery |
| 5 | Reverse census run on every touched symbol | ✓ | §4 reverse census: B1 over 14 symbols, B2, B3, B4 (fired — `app.py`, `widgets/rail.py`, neither touched), A3 (empty diff on every `render` signature line) |
| 6 | `code-reviewer` passed — a HIGH blocks | ⚠ | **not run.** Independent review is the orchestrator's gate, not this agent's; requested |
| 7 | No file from another lane touched | ✓ | `git status --porcelain`: the only files this session modified are the three under `mapper/views/` plus the new test file. Increment 1's `model.py`, `mermaid.py`, `store.py`, `app.py` carry another session's uncommitted work and were read only |
| 8 | Frozen interfaces untouched (or returned to the trunk) | ✓ | `git diff -U0 -- mapper/views/` filtered for every `render` signature line → empty; `mapper/canvas.py` not in the diff at all |
| 9 | Coverage claims verified **on disk**, not from intent | ✓ | ledger `293 = 265 − 0 + 28` reconciled against `--collect-only` counts, not against intent; gate tail read from `out.txt` |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | ✓ | §4 C-55 table; synthetic instance in `test_tc_r10`, positive control returned `{"synthetic.py:1 walk"}` and `{"synthetic.py:2 tag"}` from the unmodified probe |
| 11 | Mutation verdicts recorded **per arm**, inert arms named (C-40 rider) | ✓ | §4 matrix, one row per arm, node ids not exit codes; **no arm stayed green**; M5 and M10 named as the arms that survived every predicate except the frame count and the AST derivation |
