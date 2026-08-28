# Security Review — Inc-3 (`feat/ui-next-batch-02`, uncommitted over `954f8f3`)

## VERDICT: **BLOCK** — 2 HIGH, 3 MEDIUM, 3 LOW

Both HIGHs are the same defect class the increment exists to close — a file-derived
string reaching an operator-visible sink uncoerced — on surfaces the increment's own
requirements scope in, and **both are missed by the census the increment ships**.
`F1` reaches the exported SVG through the default renderer and makes it non-well-formed
XML, which is verbatim the `B-47` failure the increment claims to have fixed.

The widened guarantee *is* real for the payload the increment tested (title / meta /
notes): 24 of 24 renderer × size × fold configurations came back clean end-to-end
through `save_svg`. It is not real for two file-derived strings the census never feeds it.

**Adjudication of the author's `B-58`: CONFIRMED by execution.** The `LLR-COERCE.2`
numeric threshold is inert. The security value lives entirely in the leaked-code-point
and split-at-width arms, which are genuinely discriminating (mutation-tested).

---

## Scope reviewed

`git diff HEAD` plus untracked files at branch `feat/ui-next-batch-02`, base `954f8f3`:
21 files, +2821 / −89. Product: `mapper/app.py`, `mapper/keymap.py`,
`mapper/views/layered.py`, `mapper/views/outline.py`, `mapper/views/state.py`,
`mapper/widgets/rail.py`. New fixtures `fixtures/anidado.mmd` / `anidado_nodos.yml`.
Tests `tests/inc3_support.py`, `test_inc3_census.py`, `test_fold.py`, `test_overflow.py`,
`test_pan.py` + 6 modified.

**Shared working tree not modified.** All work ran in an exported copy at
`C:\Users\jjgh8\AppData\Local\Temp\claude\C--Users-jjgh8-clde\9192a111-06ab-49d6-93e0-be74df48d23d\scratchpad\mapper-wt`
(Inc-3) and `…\9192a111-…\mapper-base` (`git archive 954f8f3`). A sha256 manifest of
167 tracked `.py/.yml/.mmd/.md` files under `mapper/ tests/ fixtures/ .dev-flow/` was
taken before and after: **167/167 digests identical**. The single manifest delta is one
*added* file, `03-increments/increment-003-code-review.md`, written by the concurrent
gate — not by this review.

Environment: Python 3.12.7, rich 15.0.0, textual 8.2.8, pytest 8.3.4, `PYTHONUTF8=1`.
Baseline suite in the exported copy: **784 passed, 17 deselected in 87.46 s**.

> Every hostile code point below was constructed with `chr(0x…)` at run time. No raw
> control byte is written into this document or into any file this review created;
> payloads are named by code point and position only.

---

## Findings

### F1 — A file-derived schema key reaches the exported SVG uncoerced and breaks XML well-formedness  [Severity: HIGH]

- **What:** The legacy card paints `SchemaField.key` straight onto the canvas with no
  `darkside.plain`. `MapStore.load` does **not** coerce schema keys or labels either, so
  a `.yml` sidecar carrying a control code point in `schema[i].key` reaches the terminal
  *and* `export.save_svg`. This is `B-47`'s exact failure — the default renderer writing
  an SVG that is not well-formed XML — surviving the increment that was scoped to close it.

- **Where:**
  - `mapper/views/layered.py:464` — `cv.put(xx, y + 2, sf.key, darkside.MUT)`
    (contrast `:459` and `:469`, which correctly route through `_fit` → `_clip` → `darkside.plain`).
  - `mapper/store.py:342` — `graph.schema` is built via `_coerce_text_fields`, which does
    **not** strip `COERCION_RANGES` from `key` / `label`.
  - Census blind spot: `tests/test_inc3_census.py:242-248` — the `A-89` fixture sets only
    `title`, `meta`, `notes` and never populates `graph.schema`, so
    `test_a89_every_reached_renderer_coerces_what_it_paints` cannot see this. `legacy`
    mode is selected by `bool(graph.schema)` (`layered.py:283`), so the arm never enters
    the branch that leaks.

- **Why it matters:** The exported SVG is the artifact a third party opens. It is not
  parseable, and it carries attacker-controlled invisible content. The stated `A-89`
  guarantee ("every renderer reaching an operator-visible sink coerces what it paints")
  is false as shipped, in the **default** view.

- **Executed transcript** — sidecar written with `schema[0].key = chr(0x202E)` and
  `schema[1].key = chr(0x01)`, loaded through the real `MapStore.load`:

  ```
  1. loaded from disk. legacy= True warnings= []
  2. terminal Text leak: ['0x1', '0x202e']
  3. exported SVG leak: ['0x1', '0x202e']
  4. SVG parses: NOT well-formed -> not well-formed (invalid token): line 149, column 377
     first banned code point at SVG char index 9231, U+202E
  ```

  And the load boundary does not defend it (key `U+202E` + `U+004B`, label `U+004C` + `U+0001`):

  ```
  loaded schema key code points: ['0x202e', '0x4b']
  loaded schema label code points: ['0x4c', '0x1']
  banned survived load? True
  load_warnings: []
  ```

- **Recommendation:** Coerce at the render sink, matching the module's own convention:

  ```python
  # mapper/views/layered.py:464
  cv.put(xx, y + 2, darkside.plain(sf.key)[:1] or " ", darkside.MUT)
  ```

  and widen the census fixture so the arm can see it — in
  `test_a89_every_reached_renderer_coerces_what_it_paints`, add
  `graph.schema = [SchemaField(key=hostile("k")[:1], label=hostile("l"))]` (or a second
  parametrised graph with a non-empty schema), so the legacy branch is entered. Consider
  also coercing `key`/`label` in `store.py:342`'s `_coerce_text_fields` set, so the
  defence is at the boundary as well as the sink.

---

### F2 — `_minimap_text` interpolates a file-derived ficha title with no coercion  [Severity: HIGH]

- **What:** The coverage minimap builds its branch labels from
  `graph.nodes[cid].ficha.title` with no `darkside.plain`. A hostile title reaches the
  **composited frame** carrying a right-to-left override, zero-width characters, a C0
  control byte and a TAG-block payload. `LLR-N06.2.3` scopes the census to "every
  file-derived string painted on a surface this batch touches, whether its sink is new or
  pre-existing", and `refresh_canvas` — restructured by this increment — is the caller
  that repaints this widget (`app.py:1616`).

- **Where:** `mapper/app.py:1479-1480`

  ```python
  name = self.graph.nodes[cid].ficha.title or cid
  parts.append((f"{name} ", darkside.MUT))
  ```

- **Why it matters:** The minimap's job is to tell the operator which branch has which
  coverage. `U+202E` reorders the row's rendered text, so a branch can be made to display
  under a neighbour's name — the operator is deceived about which branch is at risk, by
  the one widget whose purpose is that judgement. The TAG-block code points render as
  nothing and are recovered trivially by any later reader. Blast radius is smaller than
  `F1`'s: this is a `Text.assemble` sink (no markup parsing) and the export path renders
  only the canvas renderer, so **this does not reach `save_svg`** — it is terminal-only.

- **Executed transcript** — hostile titles loaded through `MapStore`, real
  `MapperApp.run_test(size=(160, 40))`, read off the compositor:

  ```
  MINIMAP leaks: ['0x1', '0x200b', '0x200d', '0x202c', '0x202e', '0xe004e', '0xe0050', '0xe0057', '0xe007f']
  CANVAS  leaks: []
  FRAME   leaks: ['0x1', '0x200b', '0x200d', '0x202c', '0x202e', '0xe004e', '0xe0050', '0xe0057', '0xe007f']
  MINIMAP raw Text leaks: ['0x1', '0x200b', '0x200d', '0x202c', '0x202e', '0xe004e', '0xe0050', '0xe0057', '0xe007f']
  ```

  Payload by position, all built with `chr()`: index 0-3 tag prefix, then a Rich-markup
  literal (inert here), then `U+0001`, then `U+202E` … `U+202C` around three ASCII
  letters, then `U+200D`, `U+200B`, then three TAG-block code points `U+E0050 U+E0057
  U+E004E` and `U+E007F`. Nine of these survive to the frame; the canvas and the new
  pagination strip are clean.

- **Recommendation:** One call, matching every sibling sink in the file:

  ```python
  name = darkside.plain(self.graph.nodes[cid].ficha.title) or cid
  ```

  Then add the minimap region to the `LLR-N06.2.3` census so the arm is not a promise.

---

### F3 — Inc-3 moved two layout calls outside the guard that keeps a drawing failure from killing the app  [Severity: MEDIUM]

- **What:** `refresh_canvas`'s `try/except` carries the comment "this method runs inside
  the message pump, so an escape here kills the app. Scoped to the sink, not to the
  exception types known today." This increment adds two calls that reach
  `_geometry` → `_tree_layout` — which raises `ValueError` by design on a cyclic graph —
  and places **both outside** that try.

- **Where:** `mapper/app.py:1593` (`self._reclamp_pan(w, h)` → `pan_extent`) and
  `mapper/app.py:1623` (`_pagination_text` → `_unpainted_ids` → `painted_ids`). At
  `954f8f3` the only `_tree_layout`-reaching call in `refresh_canvas` was
  `renderer.render(...)`, inside the try, and `_pagination_text` had no `painted_ids` call.

- **Why it matters:** A contained, declared degradation ("no se pudo dibujar el mapa")
  becomes an uncaught exception in the message pump. Executed against Inc-3 with a cyclic
  graph on `MapScreen`:

  ```
  graph: nodes=5 edges=5 find_cycle=['n0', 'n1', 'n2', 'n3', 'n0']
    _tree_layout -> RAISES ValueError: cycle through n0: the graph is not a tree
    MapScreen.refresh_canvas -> ESCAPES ValueError: cycle through n0: the graph is not a tree
    keypress 'j' -> survived (running=True)
    keypress 'L' -> survived (running=False)
  ```

  The pan keypress killed the app — `app.is_running` went `False` — losing unsaved edits.

- **Reachability, stated honestly:** I could **not** construct a graph that reaches
  `MapScreen.graph` in this shape through the shipped loaders. `mermaid.parse` rejects
  multi-parent (`"node 'a' has multiple parents (out of MVP scope)"`, executed) and both
  `store.load` and `store.save` reject cycles via `find_cycle` (`store.py:565`).
  `preview_csv` *can* build a multi-parent graph with `find_cycle() -> None` (executed:
  37 nodes / 70 edges, max 2 parents per child), but it lands on
  `_ImportPreviewScreen`, which keeps its own `try/except` (`app.py:743`), and
  `action_save` → `store.save` → the reloading `MapScreen` gets an empty graph. So this is
  a **defence-in-depth regression, not a live exploit** — which is precisely why the guard
  was written "scoped to the sink, not to the exception types known today".

- **Recommendation:** Bring both inside the guard, or wrap them individually:

  ```python
  try:
      self._reclamp_pan(w, h)
      text = renderer.render(self.graph, self._view_state(w, h))
  except Exception as exc:
      ...
  ```

  and guard the `_pagination_text()` call the same way (or make `_unpainted_ids` return
  `None` on a layout failure, which is the value it already uses for "this view declares
  nothing").

---

### F4 — The `A-89` renderer census is blind to an attribute-style reference  [Severity: MEDIUM]

- **What:** `reached_renderers()` matches only `ast.Name` nodes, so it sees
  `from .views.lane import LaneRenderer` but **not** `lane.LaneRenderer`. `A-89` requires
  the renderer set be DERIVED "never named by hand" so that a later increment wiring a
  renderer up inherits the coercion obligation automatically. For one plausible wiring
  shape it does not.

- **Where:** `tests/test_inc3_census.py:200-202`

  ```python
  if isinstance(node, ast.Name) and node.id in renderers:
  ```

- **Why it matters:** Mutation-tested both ways against the full census:

  | mutant | wiring in `app.py` | census result |
  |---|---|---|
  | **M3a** | `from .views.lane import LaneRenderer` | **KILLED** — 2 arms red, incl. leaked `['0x1','0x20…e','0xe0041']` |
  | **M3b** | `from .views import lane as _lane_mod` / `_lane_mod.LaneRenderer` | **SURVIVED — 23 passed** |

  Under M3b an uncoerced renderer is reached from a product module outside
  `mapper/views/` and every arm stays green, including the equality pin
  `test_a89_the_reached_set_is_pinned_so_wiring_lane_up_pulls_it_in`, whose stated job is
  to "go red and force the decision".

- **Item 1 verified in your favour otherwise:** the derivation genuinely walks the tracked
  sources; both halves assert non-emptiness before evaluating
  (`test_a89_the_renderer_census_derives_a_non_empty_set`); `git ls-files "mapper/*.py"`
  does match nested paths (git wildmatch, verified: 34 files incl. `mapper/views/*`,
  `mapper/widgets/*`, `mapper/screens/*`); and M3a proves a newly-wired renderer is pulled
  in automatically. Your `02j` claim about `lane.py` is **confirmed independently**: an AST
  sweep of every tracked product module outside `mapper/views/` finds **zero** references
  to `LaneRenderer`, `HybridLaneRenderer` or `RailTimelineRenderer`, by `Name` *or* by
  `Attribute`. They reach no sink today.

- **Recommendation:**

  ```python
  for node in ast.walk(tree):
      name = (node.id if isinstance(node, ast.Name)
              else node.attr if isinstance(node, ast.Attribute) else None)
      if name in renderers:
          reached.setdefault(name, []).append(f"{rel}:{node.lineno}")
  ```

---

### F5 — `_hidden_ids` is quadratic in the number of folded branches  [Severity: MEDIUM]

- **What:** `_hidden_ids` calls `_descendants` once per folded node with no shared memo,
  so cost is `O(|folded| × V)`. New code, on a path that runs on every repaint.
- **Where:** `mapper/views/layered.py:92-102`, called from `_geometry:262`. `_geometry`
  now runs up to 4× per pan keypress (measured: `_pan` → `pan_extent`, then
  `refresh_canvas` → `_reclamp_pan` → `pan_extent`, → `render`, → `_pagination_text` →
  `painted_ids`; instrumented count for one `L` press = **4** `_tree_layout` passes).
- **Why it matters:** measured on a deep chain with every node folded:

  ```
  deep chain n=  500, ALL nodes folded: _hidden_ids      14.8 ms
  deep chain n= 1000, ALL nodes folded: _hidden_ids      58.4 ms
  deep chain n= 2000, ALL nodes folded: _hidden_ids     253.6 ms
  deep chain n= 4000, ALL nodes folded: _hidden_ids     987.8 ms
  ```

  Clean quadratic. It is not a practical denial of service — reaching it needs one `z`
  press per node — but at 4 passes per keypress it is a real interactivity cliff on a
  large map, and the growth is in new code.
- **Recommendation:** single-pass union with a shared `seen` set across the whole
  `folded` iteration, or memoise `_descendants` per `_geometry` call.

---

### F6 — The truncator census walks module top level only  [Severity: LOW]

- **What:** `truncators()` iterates `tree.body`, so a truncator added as a class method or
  a nested function is invisible to it, and the equality pin would still pass.
- **Where:** `tests/test_inc3_census.py:66` — `for node in tree.body:`
- **Why it matters:** No member is lost *today* — an `ast.walk` sweep of every tracked
  product module for a `str`-returning function taking a `str` found 23 candidates, and
  all four nested/method ones (`app._normalize_repo`, `app._branch_kind`,
  `app._ficha_value`, `canvas._tone`, `store._text_hash`) are not `(str, int) -> str`
  truncators. So `{darkside.fit, layered._clip, layered._fit}` is complete and the
  equality is correct as shipped. The hole is latent.
- **Recommendation:** `for node in ast.walk(tree):` and skip `self`-first arg lists.

### F7 — `_tree_layout` is exponential on a multi-parent DAG (PRE-EXISTING; carry)  [Severity: LOW]

- **What:** `walk`'s `visiting` set guards *cycles*, not *re-convergence*. On an acyclic
  multi-parent graph each node is re-expanded once per path, so cost is `2^depth` while
  node count stays linear. `MAX_RENDER_NODES = 12000` does not defend it — the attack uses
  ~50 nodes.
- **Where:** `mapper/views/layered.py:155-179` (unchanged by this increment).
- **Why it matters / not a blocker:** measured identically at `954f8f3` and at Inc-3, so
  **this increment does not introduce it**:

  ```
  levels  nodes   edges         ms          BASE 954f8f3
      12     25      46       3.68            3.31
      16     33      62      53.06           55.23
      18     37      70     214.82          220.91
      20     41      78     843.50          867.76
      22     45      86    3352.94         3523.06
  ```

  Cost ×4 per 2 levels. A full `render` at 49 nodes took **100.5 s**. Reachable only as far
  as `_ImportPreviewScreen` (see F3's reachability note), which is guarded. The project's
  own rule is "a hang is worse than a crash", and this is the one shape that hangs rather
  than raising — worth a carry, not a block. Inc-3 amplifies it 4× on the new pan keys.
- **Recommendation:** carry. Fix is a `placed` memo in `walk` so a node is expanded once,
  or reject multi-parent at `_geometry` the way `mermaid.parse` already does at load.

### F8 — Test modules shell out to `git`  [Severity: LOW]

- **What:** `subprocess.run(["git", "ls-files", *globs], cwd=REPO, capture_output=True, check=True)`
- **Where:** `tests/test_inc3_census.py:34`, `tests/test_darkside_census.py` (same helper).
- **Why it matters:** Minimal. Fixed argv, no `shell=True`, `*globs` is call-site
  literal and never file- or user-derived, test-only. It does mean the census silently
  becomes vacuous outside a git checkout — but each census asserts non-emptiness first,
  which converts that into a red test rather than a silent pass. **Accept as-is**; noted
  because it is the only new process surface in the increment.

---

## Adjudications requested

### Item 2 — does the coercion hold end-to-end through the shipped surface? **Yes for title/meta/notes; no for schema keys (F1).**

`action_export_svg` (`app.py:1988-1996`) renders through `self._current_renderer()` — so
all three reached renderers hit `save_svg`. Driving a hostile title through each, at four
sizes, folded and unfolded, and parsing the written SVG:

```
LayeredRenderer   80x24  fold=0 term_leak=[] svg_leak=[] xml=well-formed
LayeredRenderer   80x24  fold=1 term_leak=[] svg_leak=[] xml=well-formed
LayeredRenderer  140x45  fold=0/1 …            all clean
LayeredRenderer   30x12  fold=0/1 …            all clean
LayeredRenderer  200x60  fold=0/1 …            all clean
OutlineRenderer   (8 configurations)           all clean
RadialRenderer    (8 configurations)           all clean
FAILURES: 0            (24 of 24)
```

Payload per title, all `chr()`-constructed: a Rich-markup literal, `U+0001`, a balanced
`U+202E`…`U+202C` pair, `U+200D`, `U+200B`, six TAG-block code points `U+E0053 U+E0045
U+E0043 U+E0052 U+E0045 U+E0054` and `U+E007F`.

**The pre-state defect was real.** The same probe at `954f8f3`:

```
  Layered   80x24  svg_leak=[]                                     xml=well-formed
  Layered  200x60  svg_leak=['0x1', '0x202e']                      xml=NOT-well-formed (line 230, col 2533)
  Outline   80x24  svg_leak=[11 distinct code points]              xml=NOT-well-formed (line 76, col 151)
  Outline  200x60  svg_leak=[11 distinct code points]              xml=NOT-well-formed (line 76, col 151)
  Radial    80x24  svg_leak=[]                                     xml=well-formed
  Radial   200x60  svg_leak=[]                                     xml=well-formed
```

`AT-009` held in radial only, exactly as `B-47` states. Note `Layered` leaked at 200×60
but not at 80×24 — the payload was truncated away at the narrow width — which is why the
width sweep is load-bearing.

### Item 3 — the split-at-width arm. **Closed, and `_clip` / `_fit` / `darkside.fit` now agree.**

The ordering in `_clip` (coerce at `layered.py:52`, then truncate) is what closes it.
On the uncoerced pre-state, with a source balanced at exactly one `U+202E` and one `U+202C`:

```
  layered._clip  w=5   n_202E=0 n_202C=0
  layered._clip  w=6   n_202E=1 n_202C=0     <- unterminated override, manufactured
  layered._clip  w=10  n_202E=1 n_202C=0
  layered._clip  w=20  n_202E=1 n_202C=0
  layered._fit   w=6/10/20  n_202E=1 n_202C=0
  darkside.fit   w=5/6/10/20 n_202E=0 n_202C=0   <- already coerced at base
```

At Inc-3 all three return 0/0 at every width. `_fit` funnels through `_clip`, so there is
one statement of the ordering rather than one per call site.

### Item 4 — `B-58`. **CONFIRMED. The stated threshold is inert.**

`darkside.plain` is `str.translate` over a 1:1 map (`darkside.py:410-428`), so it is
length-preserving and distributes over slicing. Executed against the **uncoerced**
`954f8f3` truncators:

```
  layered._clip  w=1..40  commutes=True   (all six widths)
  layered._fit   w=1..40  commutes=True   (all six widths)
  layered._clip  w=40     commutes=True  leaked=['0x1','0x200b','0x200d','0x202c','0x202e','0xe0043','0xe0045','0xe0052','0xe0053','0xe0054','0xe007f']
  layered._fit   w=40     commutes=True  leaked=[same 11]
```

The equality `f(plain(s), w) == plain(f(s, w))` is `True` at every width on the truncator
that was returning the payload **intact**. `LLR-COERCE.2`'s headline threshold cannot fail
on a length-preserving coercion, and the increment's own docstring at
`test_inc3_census.py:112-119` says so honestly — that self-report is accurate.

**Does the shipped test set still discriminate a genuinely uncoerced implementation? Yes.**
Mutation-tested by removing `darkside.plain` from the shipped code and running the full suite:

| mutant | result |
|---|---|
| **M1** — `layered._clip` stops coercing | **KILLED, 7 failed / 777 passed.** `test_fold.py::test_tc_033_the_fold_pill_coerces_a_hostile_branch_title`; `test_inc3_census.py::…no_truncator_emits_a_coerced_code_point[5,8,13,40]`; `…the_split_at_width_arm`; `…a89_every_reached_renderer_coerces_what_it_paints` |
| **M2** — `outline.py` stops coercing | **KILLED, 1 failed / 783 passed** (`…a89_every_reached_renderer_coerces_what_it_paints`) |

Two details worth keeping: `test_llr_coerce_2_every_truncator_coerces_before_it_truncates`
(the commutation arm) **passed under M1** — independent confirmation of `B-58` from the
shipped suite's own perspective. And `no_truncator_emits_a_coerced_code_point[1]` and `[2]`
also passed under M1, because widths 1-2 truncate before reaching the payload — so the
six-width parametrisation is doing real work and should not be narrowed.

### Item 5 — new sinks. **Pill and overflow declaration clean; minimap leaks (F2).**

| sink | file-derived input | result |
|---|---|---|
| fold pill `▸ <rama> +N` | branch title | **clean** — `_clip` at `layered.py:490`; killed by M1 via `test_tc_033` |
| overflow declaration (header) | none — numeral only | **clean** (`layered.py:421`) |
| overflow declaration (pagination strip) | none — numeral only | **clean**; executed: `▰▱▱▱▱▱▱   1/7  ▽ 1 fuera de vista`, `PAGINATION leaks: []` |
| leaf notification | none — two literals | **clean**, and `markup=False` is passed explicitly (`app.py:1305`), matching the file's convention at 12 other sites |
| removed-node ghosts | `removed_titles` | **clean** — `escape()` then `_fit` (`layered.py:510`) |
| legacy doc chip | `ficha.fields["D"]` | **clean** — `_fit` (`layered.py:459`) |
| legacy schema letters | `SchemaField.key` | **LEAKS — see F1** |
| `_minimap_text` | `ficha.title` | **LEAKS — see F2** |
| inspector schema labels | `SchemaField.label` | clean — `_label` coerces (`inspector.py:194`) |

Executed on the folded hostile map: `CANVAS leaks (folded): []`, `PILL folded: ['b0']`.
The pill's `+N` is a deduplicated union (`_descendants` uses a `set`), so the
`LLR-N06.3.1` double-count is genuinely closed.

### Item 6 — denial of service / resource shape. **No hang added; the cycle guard is preserved.**

```
chain-2000             n= 2000     43.5 ms  -> ok
chain-2000-folded      n= 2000      6.5 ms  -> ok
fan-4000               n= 4001   4101.7 ms  -> ok        (pre-existing wide-fan cost)
fan-4000-folded        n= 4001      7.7 ms  -> ok
cycle/render          0.04 ms -> ValueError: cycle through n0: the graph is not a tree
cycle/painted_ids     0.02 ms -> ValueError: cycle through n0: the graph is not a tree
cycle/pan_extent      0.02 ms -> ValueError: cycle through n0: the graph is not a tree
_hidden_ids on cycle -> ['n0', 'n1', 'n2', 'n3'] in 0.006 ms
```

The new entry points `painted_ids` and `pan_extent` **raise rather than hang**, matching
the tree's stated rule. `_hidden_ids` / `_descendants` terminate on a cycle because both
dedupe through a `set`. The clamp (`_clamp_pan`) is pure arithmetic, `O(1)`. Fold pruning
is `O(V+E)`. The two resource concerns are `F5` (quadratic in `|folded|`, new) and
`F7` (exponential on a DAG, pre-existing).

### Item 7 — standard sweep. **Clean.**

- **Secrets:** no API key, token, bearer, password, private key, or provider-prefixed
  credential pattern in the diff. The `*_TOKEN` hits are the glyph constants
  `OVERFLOW_TOKEN = "▽"` / `FOLD_PILL_TOKEN = "▸"`.
- **Paths / environment:** no absolute path, username, `os.environ`, or `getenv` in any
  added line.
- **Destructive filesystem:** none — no `rmtree`, `unlink`, `os.remove`, `shutil.*`,
  `eval`, `exec`, `pickle`, or `__import__` in added lines.
- **Network:** none.
- **Process:** only the `git ls-files` helper — see F8.
- **New fixtures:** `fixtures/anidado.mmd` (241 chars) and `anidado_nodos.yml` (809 chars)
  contain generic Spanish business nouns (Plataforma, Operaciones, Finanzas, Logistica,
  Compras, Almacenes, Flota). No PII, no client data, no credentials. Nothing here
  triggers LFPDPPP concerns.
- **No hostile code point is spelled into any shipped file.** Scanned all new fixtures,
  test modules and `.dev-flow` artifacts against `COERCION_RANGES`: **0 banned code points
  in all 10 files** (`test_inc3_census.py` 17,927 chars, `test_fold.py` 14,564,
  `test_overflow.py` 21,499, `increment-003.md` 24,482, `01-requirements.md` 608,005 — all
  clean). The `hostile()` helpers build every payload with `chr()` at run time, as `A-89`
  requires.
- **`.gitignore`** covers `.env`, `.env.*`, `*.svg`, `*.png`, `*.db`, `.mapper/`,
  `prototypes/`. An exported SVG carrying a payload cannot be committed.

---

## Mitigations required before this increment ships

1. **F1** — coerce `sf.key` at `layered.py:464`; add a non-empty `graph.schema` to the
   `A-89` census fixture so the legacy branch is exercised. *(Blocking.)*
2. **F2** — wrap `_minimap_text`'s title in `darkside.plain` at `app.py:1479`; add the
   minimap region to the `LLR-N06.2.3` census. *(Blocking.)*
3. **F3** — bring `_reclamp_pan` and the `_pagination_text` call back inside
   `refresh_canvas`'s guard. *(Recommended before merge; the guard's own comment is the
   argument.)*
4. **F4** — extend `reached_renderers()` to `ast.Attribute`. *(Recommended; it is the
   control that is supposed to stop `B-47` recurring.)*
5. **F5, F6, F7, F8** — carry.

---

## Verdict

- [ ] OK to ship
- [ ] OK to ship with the listed mitigations applied first
- [x] **Block — must fix the HIGH findings (F1, F2) before ship**

---

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — F1-F8 above, each with a
      `file:line` and a named fix.
- [x] Each finding has a severity rating — 2 HIGH, 3 MEDIUM, 3 LOW.
- [x] No secret values appear in this output — none were found; no raw control byte is
      written here, every payload is named by code point and position.
- [x] Verdict is explicit — **Block**.
- [x] New tool/integration scope and blast radius addressed — no MCP/Composio/n8n/network
      surface added. Sole new process surface is a fixed-argv `git ls-files` in two test
      modules (F8), no `shell=True`, test-only.
- [x] Every behavioural claim carries its executed transcript; nothing is asserted from
      reading alone. Where I could not establish a fact — F3's reachability through the
      shipped loaders — it is stated as "could not construct", not as "unreachable".
- [x] Shared working tree not modified — 167/167 sha256 digests identical before and after.
