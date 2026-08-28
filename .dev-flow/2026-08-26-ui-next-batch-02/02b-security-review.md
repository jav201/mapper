# 02b · Security review — PDR gate, batch `2026-08-26-ui-next-batch-02`

> Lens: **security**, at PDR. Reviewed: `01-requirements.md` (2707 lines), `PLAN.md`,
> `docs/ARCHITECTURE.md` §1/§3/§4a, batch 1's `02b-security-review.md` and `04b-security-signoff.md`,
> and the shipped tree at `d6b60e6` + working changes.
>
> **Nothing below is a reading.** Every finding carries a probe that was run against the real
> parser, the real store, the real renderers or the real Textual compositor. Fixtures were built in
> the system temp directory; nothing was written into the repo, nothing was staged, `prototypes/`
> was not touched, no source file was modified, and no control byte was spelled into any file —
> every one was constructed from its code point with `chr()`.

---

## 0 · Verdict

> ### `blocked`
>
> **3 `blocker` · 6 `major` · 5 `minor`.**
>
> The batch may not enter Phase 3 until S-01, S-02 and S-03 are closed in the **requirements**, not
> deferred to the implementer. All three are the same shape: *this batch takes a Graph that nothing
> validates and puts it on a screen that renders **every map in the workspace**.* Two of them are
> already app-killing defects on `master` — I reproduced both crashes under `App.run_test`, and
> US-N13 is what makes them reachable from the home screen for a map the operator never opened.

---

## 0b · Identifier reconciliation (read this before matching against the brief)

The task brief refers to carries as `B-01 … B-11`. **That series does not exist in batch 1's
documents.** `02b` uses `F-B1/F-B2`, `F-M1…F-M6`, `F-m1…F-m6`, conditions `C-1…C-18`; `04b` uses
`N-1 … N-14`, `N-4-shape`, mutants `M9/M5/M-AB/M-W/M-X/M-Y/M-AD/M-AE/M-AC`. Mapping used below:

| Brief | Actual | Batch-1 disposition |
|---|---|---|
| B-01 (`MapStore.load` KeyError) | **F-M5 / condition C-12** — the *store half* | **never discharged in `04b`** — open, not "carried" |
| B-03 (~20 `rich.markup.escape` sites) | **F-m1**, referenced in `01-requirements.md:1039`, `:1558` as "carry B-03" | recommendation-only, **now explicitly deferred again by this batch** |
| B-06 (ADS · `urlparse` · exe policy · U+202E) | **four findings**: `N-6`, `N-8`, `N-9`, **`N-10`** | all four carried unchanged |
| B-07 (uncoerced `notify`/toast sinks) | **N-14** (aggregate) | `_event_toast` half **fixed on master**; **markup half still open** |
| B-10, B-11 | `N-10`, `N-11` | carried |

Also carried and never discharged: **C-8** (`F-M3`, file-derived inventory omits schema labels,
`state`, `meta`, `path`, `node.id`) and **C-12** (`F-M5`, `MapStore.load` value tolerance). Both are
load-bearing for this batch — see S-02.

---

## 1 · Probe method

| # | Probe | What it drove |
|---|---|---|
| A1 | 8 hostile sidecars through `MapStore.load`, then each downstream consumer | real `store.py`, real `model.py` |
| A2 | 13 payload classes through `darkside.plain()`; the exact `app.py:499-508` resume-row construction | real `darkside.py`, Rich console |
| A3 | 14 malformed style strings through `Text.append` and through `Canvas.rows()`, truecolor on | real `canvas.py`, `rich.style` |
| A4 | cycle · deep chain · balanced tree · flat 10 000 · 1 MB titles · YAML alias bomb, wall-clocked | real renderers, real store |
| A5 | the real mermaid parser; the exact `app.py:537-545` recents loop; workspace scale 10/50/200 | real `mermaid.py`, real `store.py` |
| A6 | **`App.run_test(size=(140,45))`** against a workspace of three hostile maps | real `MapperApp`, real compositor |
| A7 | painted-strip read of the home screen with a bidi title; lens substrate; schema echo | real compositor via `render_strips()` |
| A8 | truncation/bidi leak; `Content.from_markup` in textual 8.2.8; **named weaker-variant mutants** | real `darkside.fit`, real `textual.content` |

Toolchain as executed: Python 3.12.7 · textual 8.2.8 · rich 15.0.0 · PyYAML 6.0.3.

---

## 2 · Findings

### S-01 — a cycle in a `.mmd` kills the app, and US-N13 makes it reachable without opening the map · `[blocker]`

- **What.** `mapper/views/radial.py:23` `_leaves`, `:54` `place` and `:95` `tag` recurse over
  `graph.children_of` with **no visited set and no memoisation**. `Graph.focus` (`model.py:144`) has
  a `keep` guard; these three do not. A cycle is a `RecursionError`; a deep-but-acyclic chain is
  also a `RecursionError`; a balanced tree is a quadratic-time blowup.

- **Where.** `mapper/views/radial.py:23,54,95`; the unguarded render call at
  `mapper/app.py:1300-1308` (`MapScreen.refresh_canvas` — **no `try`/`except`**);
  `mapper/views/layered.py` (`_tree_layout`, same class).

- **Executed evidence.** The **real** mermaid parser accepts a cycle:

  ```
  parse("graph TD\n  a[uno] --> b[dos]\n  b --> c[tres]\n  c --> a\n")
    nodes: ['a','b','c']  edges: [('a','b'),('b','c'),('c','a')]  root_id: a
    _leaves(root)             2.5 ms  RecursionError
    RadialRenderer.render     1.0 ms  RecursionError
    LayeredRenderer.render    1.2 ms  RecursionError
    graph.focus(root)         0.0 ms  ok          <- the guard that exists, elsewhere
  self-loop  a --> a :  _leaves RecursionError
  ```

  And under the real app — this is the crash, not the raise:

  ```
  A6.2  open the CYCLIC map through the real MapScreen
    survived push; screen = MapScreen
    first painted rows:
    *** RecursionError: maximum recursion depth exceeded
  ```

  `App.run_test` re-raised it out of `message_pump._flush_next_callbacks`. The app died.

  Acyclic DoS, same function, wall-clocked:

  ```
  _leaves depth=500                    5.7 ms  ok
  RadialRenderer depth=500          2635.1 ms  ok          <- 2.6 s on a 500-node chain
  _leaves depth=1500                  49.6 ms  RecursionError
  RadialRenderer b=3 d=7  n= 3280   3444.4 ms  ok
  RadialRenderer n=10000            9123.5 ms  ok
  children_of x N  (O(N*E)) n=10000 1923.6 ms  ok
  ```

- **Why it matters for THIS batch.** Today the blast radius is "the operator opened a hostile map".
  US-N13 changes that: `HomeScreen.on_mount` already calls `store.load` for **every** map
  (`app.py:539`, and `01-requirements.md:1393-1399` confirms it as executed premise M-12), and
  US-N13 adds a **per-map constellation thumbnail** and coverage bar computed from each `Graph`. The
  moment any per-card computation walks the tree the way `_leaves`, `rail.subtree_missing` or
  `layered._tree_layout` do, **one cyclic map in the workspace denies the home screen for all of
  them** — with no operator action beyond starting the app. US-N06 additionally adds fold/pan
  descendant counting over the same unvalidated edge set.

- **Recommendation.** A requirement, at PDR, in `01-requirements.md`, not an implementation note:

  > **LLR-CNV.4.1** — Every traversal of the graph's parent/child relation shall terminate on a
  > graph whose edge list contains a cycle and on a graph of arbitrary depth, and shall not raise.
  > *Threshold:* a 3-node cycle, a self-loop and a 20 000-node chain each return a value with **0**
  > exceptions; the value returned for an acyclic balanced tree is **byte-identical** to the shipped
  > `_leaves` result (positive control: `b=3 d=7` → `2187`).

  **The only implementation I could get to satisfy that is iterative with an explicit stack plus
  memoisation** — see the mutants below, including one of my own that failed.

- **Named weaker variants that must also be shown to break it.**

  | Mutant | Suite | Assessment |
  |---|---|---|
  | **M-C1** `if depth > 64: return 1` — a depth cap, no visited set | **survives the cycle arm** | **Executed: returns `1` on the cycle in 0.1 ms and `1` on the 3000-deep chain in 3.8 ms.** It *terminates*, so a test asserting "0 exceptions" passes — while silently returning a **wrong leaf count**, which reshapes the radial layout of every legitimate deep map. A cap without a correctness arm is a lie that renders. |
  | **M-C2** wrap `_leaves` in `try/except RecursionError: return 1` | **survives** | **Executed: returns `1` in 25.6 ms.** Catches the symptom at the top of a stack that has already been unwound 1000 frames; leaves the O(N·E) blowup (2.6 s at depth 500, 9.1 s at n=10 000) completely untouched, and still returns a wrong count. |
  | **M-C3** `seen`-set guard, still recursive — **this was my own first candidate control** | **survives the cycle arm, FAILS the depth arm** | **Executed: `proposed on 3000-deep chain -> RecursionError`.** I am recording my own broken proposal because it is the exact shape a reviewer would wave through: it passes every cycle test and dies on a legitimate deep map. **The depth arm is not optional.** |
  | **M-C4** memoise without a visited set | **survives** | Memoisation alone does not break a cycle — the recursion re-enters before any memo is written. |

  The version that survives all three arms, executed:

  ```
  iterative+memoised cycle a->b->c->a              ->      1       0.0 ms
  iterative+memoised 20000-deep chain              ->      1      20.5 ms
  iterative+memoised balanced b=3 d=7 (3280 nodes) ->   2187       2.3 ms
  shipped _leaves    balanced b=3 d=7              ->   2187     201.4 ms
  ```

  Same answer, 87× faster, all three arms green.

---

### S-02 — a non-string ficha field value loads clean and then kills every consumer · `[blocker]`

- **What.** `MapStore._graph_from_sidecar` (`store.py:186-196`) assigns
  `fields=ndata.get("fields", {})` straight into `Ficha.fields: dict[str, str]` with **no type
  coercion**. YAML gives `D: 20260826` as an `int` and `D: yes` as a `bool`. `store.load` **succeeds**
  — so every `try: store.load(...) except Exception:` guard in the product is bypassed — and the
  failure lands in the consumers.

- **Where.** `mapper/store.py:186-196` (origin); `mapper/model.py:49` `missing_required`
  (`.strip()`), `:179` `search_hits` (`" ".join`), `mapper/app.py:371` `_map_metrics`
  (`.strip()`), `mapper/views/layered.py:145-148` (`.lower()`), `mapper/widgets/rail.py:145`.

- **Executed evidence (A1).** `store.load` returns a valid `Graph`; then:

  ```
  == intfield ==            (fields: {D: 20260826})
    store.load OK: 2 nodes
      graph.coverage()         OK -> (2, 2)
      search_hits('a')         RAISED TypeError: sequence item 0: expected str instance, int found
      missing_required(root)   RAISED AttributeError: 'int' object has no attribute 'strip'
      HomeScreen D-strip       RAISED AttributeError: 'int' object has no attribute 'strip'
      layered hit predicate    RAISED AttributeError: 'int' object has no attribute 'lower'
  == boolfield ==           (fields: {D: yes})
      same four, 'bool' object has no attribute 'strip'
  ```

  `HomeScreen D-strip` is the verbatim expression at `app.py:371`. Under the real app:

  ```
  A6.4  open the int-field map through the real MapScreen
    screen = MapScreen
    *** AttributeError: 'int' object has no attribute 'strip'
    locals: schema = [SchemaField(key='D', label='doc', required=True, kind='text')]
            self   = Ficha(title='raiz', ..., fields={'D': 20260826}, attachments=[])
  ```

  The crash site is `Ficha.missing_required` — reached through the rail's coverage lattice, which is
  **the exact widget US-N13's per-map constellation thumbnail is modelled on**.

- **Why it is a blocker for US-N13 specifically.** I built both shapes the story admits and ran them
  over a workspace of 5 good maps + 1 hostile:

  ```
  A5.4  ONE hostile map among many
    metrics inside the try : 6 cards built -> [('hostil', None), ('ok0', (33,1)), ... ('ok4', (33,1))]
    metrics after the try  : RAISED AttributeError: 'int' object has no attribute 'strip'
                             <== whole home screen denied
  ```

  **"metrics after the try" is the natural refactor**, because LLR-N13.1.1 (`:1448`) requires
  *"shall not load any map more than once per mount"* — the obvious way to satisfy that is to collect
  the graphs in the loop and compute the card data afterwards. **The requirement as written pushes
  the implementer toward the shape that fails.**

- **Recommendation.** Two requirements, both owed at PDR.

  > **LLR-STO.1.1** — `MapStore.load` shall coerce every ficha field value, title, state, meta,
  > notes, attachment `kind`/`path`/`caption` and schema `key`/`label` to `str` at the store
  > boundary, so that no consumer of a `Graph` can receive a non-`str` where the model declares
  > `str`. *Threshold:* over a sidecar carrying an `int`, a `bool`, a `float`, a `list`, a `dict`
  > and `null` in each of those positions, **0** exceptions from `Graph.coverage`,
  > `Ficha.missing_required`, `Graph.search_hits`, `HomeScreen._map_metrics` and every renderer.

  > **LLR-N13.1.5** — Every per-map card datum shall be computed inside the same failure boundary as
  > that map's load, and a map whose load **or whose card computation** raises shall paint a card in
  > a declared degraded form without preventing any other map's card from painting.
  > *Threshold:* over a workspace of 5 well-formed maps and 3 hostile ones (cyclic, non-string field,
  > missing attachment `path`), painted card count `== 8` and the degraded marker count `== 3`.

  This discharges **C-12**, which batch 1 raised as `F-M5` and `04b` never dispatched.

- **Named weaker variants.**

  | Mutant | Suite | Assessment |
  |---|---|---|
  | **M-S1** coerce only `Ficha.fields` values | **survives** an LLR-STO.1.1 test written around `fields` | The identical defect ships in `title`, `state`, `meta`, `notes`, `attachment.caption` and `SchemaField.label`. **This is batch 1's §2.1b failure exactly** — a control implemented to the edge of the noun the requirement happened to name. Executed proof the siblings are real: `titlemap` (`title:` as a mapping) → `sqlite3.ProgrammingError: Error binding parameter 4: type 'dict' is not supported`; `listfield` → the same. The threshold must quantify over the **positions**, derived from `_build_sidecar` (`store.py:116-149`), not hand-listed. |
  | **M-S2** `str(value)` with no `None` arm | **survives** | `str(None)` is `"None"` — a card that reads `documento: None` where the field is empty. Fails *visibly wrong* rather than loudly. Add a `null` arm. |
  | **M-S3** coerce in `HomeScreen` instead of in `MapStore.load` | **survives a US-N13-scoped test** | Fixes the sala and leaves `MapScreen`, the rail, the lens and `search_hits` broken — A6.4's crash is on `MapScreen`, not home. **Scope the requirement to the store boundary, which is the one place every consumer is downstream of.** |
  | **M-S4** `try/except AttributeError` around each consumer | **survives** | Converts a crash into a silently wrong coverage number on a screen whose entire promise is that the number is trustworthy (D14 exists because three coverage definitions already disagreed by 100 points). |

---

### S-03 — the sala's failure containment is a checkbox, not a requirement, and nothing anywhere bounds the work `[blocker]`

- **What.** §4's `FLOW: home_cards` (`:2190-2211`) declares four transform nodes and **no error
  node**. The only error-handling statement for a failed map load in all 2707 lines is a
  boundary-catalog line (`:1422-1423`): *"`AT-025` includes a map whose load raises; the card paints
  without the screen failing, matching the existing `except Exception` fallback at `app.py:551`."*
  There is **no HLR and no LLR** behind it. An acceptance test with no requirement above it is a test
  the next refactor deletes without reddening anything.

- **Where.** `01-requirements.md:2190-2211` (the flow), `:1422-1423` (the checkbox),
  `mapper/app.py:537-552` (the loop being replaced).

- **Executed evidence — no bound of any kind exists.** Grepping 2707 lines for `timeout`, `DoS`,
  `denial`, `max nodes`, evaluation bound, map-count cap, node-count cap or size cap returns
  **nothing**. Measured cost of the mount US-N13 widens:

  ```
  maps=  10  cold load-all=    67.4 ms   warm=  12.5 ms   _sparkline_text=  4.1 ms
  maps=  50  cold load-all=   255.5 ms   warm=  65.2 ms   _sparkline_text= 14.8 ms
  maps= 200  cold load-all=  1064.2 ms   warm= 253.5 ms   _sparkline_text= 58.0 ms
  ```

  Those are 3-node maps. `store.load` calls `_reindex` (`store.py:288`), which opens a SQLite
  connection and **writes** per map per mount; `_sparkline_text` (`app.py:415-437`) is a
  14 × N_maps `stat()` loop. Add S-01's renderer numbers (3.4 s at n=3280, 9.1 s at n=10 000) and a
  single large map in the workspace stalls the home screen before any card paints.

- **Recommendation.**

  > **HLR-N13.3** — The home screen shall paint within a declared budget for a workspace of a
  > declared size, and a map that cannot be summarised within that budget shall be declared as such
  > on its own card rather than delaying or preventing the screen.
  > *Threshold:* mount completes in `< 1000 ms` for 200 maps of ≤ 128 nodes; a map of 10 000 nodes
  > paints a declared over-budget card and the other cards paint unaffected.

  Promote `AT-025` to sit under `LLR-N13.1.5` (S-02) rather than floating in the boundary catalog.

- **Named weaker variants.**

  | Mutant | Suite | Assessment |
  |---|---|---|
  | **M-H1** one `try/except Exception` wrapping the whole card loop | **survives** an `AT-025` written as "the screen does not fail" | One hostile map costs **every** subsequent card. Executed as `metrics after the try` in A5.4: 6 maps in, 0 cards out. The threshold must be *painted card count*, not *screen did not raise*. |
  | **M-H2** cap the number of maps rather than the work per map | **survives** | A single 10 000-node map is under any map-count cap and still costs 9.1 s. The bound has to be on the **work**, not the **count**. |
  | **M-H3** compute the budget from `len(graph.nodes)` before rendering | **survives** | `len(graph.nodes)` is 3 for the cycle fixture that hard-crashes (S-01). Node count is not a proxy for traversal cost on an unvalidated edge list. |

---

### S-04 — four coercion thresholds drive a right-to-left override and none of them asserts anything about it · `[major]`

- **What.** LLR-N06.2.3 (`:1035`), AT-031 (`:1421`) and LLR-N13.2.1 (`:1554`) each drive *"a
  right-to-left override"* as a hostile input. All four coercion thresholds
  (`:1037`, `:1555`, `:1769`, `:2064`) read **"0 control bytes in the painted text; 0 Rich markup tags
  interpreted"**, with two adding a row-length clause. **U+202E is not a control byte** under
  `plain()`'s declared contract — `01-requirements.md:1030` states that contract as *"every C0 byte
  except tab and newline"*. Every threshold is satisfied with the override intact.

- **Where.** `darkside.py:272-287` (`_CONTROL_MAP`, `plain`); thresholds at
  `01-requirements.md:1037`, `:1555`, `:1769`, `:2064`. Carry **N-10** (`04b:379`, `04b:597`).

- **Executed evidence.** `plain()` coverage census — what survives it:

  ```
  U+202E RLO         SURVIVES   survivors=['0x202e']
  U+202D LRO         SURVIVES   survivors=['0x202d']
  U+2067 RLI         SURVIVES   survivors=['0x2067']
  U+061C ALM         SURVIVES   survivors=['0x61c']
  U+200F RLM         SURVIVES   survivors=['0x200f']
  U+FEFF BOM         SURVIVES   survivors=['0xfeff']
  U+2028 LINE SEP    SURVIVES   survivors=['0x2028']
  U+0007 BEL         COERCED    U+001B ESC  COERCED    OSC-52  COERCED
  ```

  And it is on the **painted** home screen today — read from the real compositor's strips at
  140 × 45, node title `"informe " + chr(0x202E) + "fdp.acta"` in `bidi_nodos.yml`:

  ```
  A7.1  U+202E on the PAINTED home screen (resume row)
    U+202E in painted output? True
    painted |  ↩ retomar  bidi / informe <U+202E>fdp.acta   última sesión
    codepoints of the tail: ['0x21a9', '0x202e']
  ```

  The operator reads `atca.pdf`; the file is `fdp.acta`. Route: `app.py:505`
  `escape(node_name)` — `escape()` does not touch it, and **`plain()` would not either**:

  ```
  same title through plain(): informe <U+202E>fdp.acta | still contains U+202E? True
  ```

  Against the requirements' own four thresholds:

  ```
  A7.5  threshold '0 control bytes'                     -> PASS
        threshold '0 Rich markup tags interpreted'      -> PASS
        U+202E neutralised?  -> no  <== NOT asserted by any threshold
  ```

- **Why this batch and not another carry.** The sala is the first surface that puts **many maps'
  titles adjacent to each other** in one column, and the legend is the first that puts a vocabulary
  caption next to a glyph whose meaning the operator is being taught. A reordering attack is worth
  more on a comparison surface than on a single ficha.

- **Recommendation.**

  > Amend LLR-N06.2.3, LLR-N13.2.1, LLR-N14.2.3 and LLR-N16.2.3's thresholds from *"0 control
  > bytes"* to: *"the painted text contains **no code point** in `U+0000–U+0008`, `U+000B–U+000C`,
  > `U+000E–U+001F`, `U+007F–U+009F`, `U+00AD`, `U+061C`, `U+200B–U+200F`, `U+202A–U+202E`,
  > `U+2028–U+2029`, `U+2066–U+2069`, `U+FEFF`"*, and widen `darkside._CONTROL_MAP` to that set.
  > The range list is the requirement; "control byte" is not a testable term.

- **Named weaker variants.** Measured, four implementations side by side:

  ```
  payload        shipped plain()   M-P1              M-P2              proposed
  U+202E RLO     ['0x202e']        []                []                []
  U+202D LRO     ['0x202d']        ['0x202d']        []                []
  U+2067 RLI     ['0x2067']        ['0x2067']        ['0x2067']        []
  U+061C ALM     ['0x61c']         ['0x61c']         ['0x61c']         []
  U+200F RLM     ['0x200f']        ['0x200f']        ['0x200f']        []
  U+FEFF BOM     ['0xfeff']        ['0xfeff']        ['0xfeff']        []
  U+2028 LS      ['0x2028']        ['0x2028']        ['0x2028']        []
  ```

  | Mutant | Suite | Assessment |
  |---|---|---|
  | **M-P1** add only `U+202E` to `_CONTROL_MAP` | **survives** any test whose fixture is "a right-to-left override" | **Executed above.** `U+202D` (LRO) reorders exactly as well; `U+2067` (RLI) is the modern isolate form and is what a current attacker reaches for. The fixture must quantify over the **class**, and the requirement must name the ranges. |
  | **M-P2** delete the characters instead of replacing them | **survives** | **Executed:** `len("acta"+RLO+"x")` is 6 before, **5** after M-P2, 6 after replacement. LLR-N06.2.3's own *"row length equals canvas width"* clause is computed on the coerced string, so it still passes — but any width arithmetic done **before** coercion silently under-runs by one cell per stripped character. Replacement preserves the cell count; deletion does not. |
  | **M-P3** validate that overrides are balanced rather than removing them | **survives** | Balanced at the source is not balanced after `fit()` truncates — see **S-05**, executed. A balance check upstream of a truncation is not a control. |
  | **M-P4** apply the widened map in `plain()` but leave `fit()` calling the old one | **survives** | `fit()` calls `plain()` at `darkside.py:292`, so this is currently a non-issue — but it becomes one the moment either helper is copied. Pin it: *"`fit` shall coerce through the same helper"*, with a test asserting `fit` and `plain` agree on the corpus. |

---

### S-05 — `fit()` truncation splits a bidi override from its terminator, and the override then governs the rest of the row · `[major]`

- **What.** New; not in batch 1's ledger. `darkside.fit` (`:290-297`) truncates to a cell budget
  with no awareness of paired formatting characters. A title that is *balanced on disk* becomes
  *unbalanced on screen*, and the surviving override then reorders every column painted after it in
  the same line.

- **Where.** `mapper/darkside.py:290-297`; consumed by `mapper/widgets/rail.py:122,124,142` today and
  by every fixed-width cell US-N13 and US-N16 add (LLR-N13.1.2 pins the bar at exactly 10 cells;
  `legend_vocabulary_rows` are fixed-width rows).

- **Executed evidence.** Title `"Q3 " + chr(0x202E) + "nomina cierre anual auditoria" + chr(0x202C)`
  — override at position 3, terminator at the end, i.e. **well-formed input**:

  ```
  w=10 cell='Q3 <U+202E>nomina…'          RLO=True PDF=False -> UNTERMINATED OVERRIDE: True
  w=14 cell='Q3 <U+202E>nomina cie…'      RLO=True PDF=False -> UNTERMINATED OVERRIDE: True
  w=20 cell='Q3 <U+202E>nomina cierre an…' RLO=True PDF=False -> UNTERMINATED OVERRIDE: True

  full row (the override now governs the rest of the line):
    'Q3 <U+202E>nomina… concept  8  0'
    renders as: Q3 <U+202E>nomina… concept  8  0
  ```

  The `kind`, `nodos` and `docs` columns of that home card — data the *product* wrote, not the
  attacker — are now rendered under an override the attacker opened.

- **Recommendation.** Fold into the S-04 amendment: coerce **before** truncating (the widened map
  removes the override, so nothing survives to be split), and add one arm to each of the four
  hostile fixtures: *"a title whose override is balanced at source and whose terminator falls outside
  the painted width"*. Assert on the **full painted row**, not the cell.

- **Named weaker variants.**

  | Mutant | Suite | Assessment |
  |---|---|---|
  | **M-F1** append a terminator (`U+202C`) after every truncation | **survives** a cell-scoped test | Costs one cell that the width budget does not account for, and does nothing for `U+2066–U+2069` isolates, which take `U+2069`, not `U+202C`. Removal is one rule; re-balancing is a table. |
  | **M-F2** assert on the truncated **cell** rather than the painted **row** | **survives** | The cell is where the override *is*; the damage is in the columns after it. This is **C-32's family** — assert the painted result. The requirement must name the row. |
  | **M-F3** cap the title length in `store.load` instead of coercing | **survives** | A 12-character title fits every cell and still carries an override. Length is not the property. |

---

### S-06 — the lens's undefined-field declaration echoes file-derived **schema key names**, which no coercion LLR covers · `[major]`

- **What.** LLR-N14.1.1 (`:1628`) requires the painted declaration to contain the unresolved key,
  and (`:1650`) *"The list after `· campos:` shall be derived from `graph.schema`, never
  hand-listed"*. `SchemaField.key` and `.label` come from `_nodos.yml`
  (`store.py:158-166`). **LLR-N14.2.3 (`:1763`) is scoped to *"every ficha field value"*** — key
  names and labels are a different noun and are covered by nothing. This is the same
  requirement-scoped-to-a-noun failure batch 1 named at `04b:628-631`.

- **Where.** `01-requirements.md:1621-1652` (LLR-N14.1.1), `:1760-1772` (LLR-N14.2.3);
  `mapper/store.py:158-166`.

- **Executed evidence.** A schema whose key and label carry an override and literal markup, through
  the D11 copy verbatim:

  ```
  schema KEYS    raw     U+202E present: True   markup literal present: True
  schema KEYS    plain() U+202E present: True   markup literal present: True
  schema LABELS  raw     U+202E present: True   markup literal present: True
  schema LABELS  plain() U+202E present: True   markup literal present: True
  ```

  `plain()` leaves literal markup in the string by design (`darkside.py:280-283` — correct, because
  `Text` does not parse it). That is only safe while the string never reaches a markup-parsing sink.
  See **S-09** for the sinks where it still does.

- **Recommendation.**

  > Amend LLR-N14.2.3's statement from *"every ficha field value"* to *"every file-derived string
  > placed into a lens surface — ficha field values, **schema field keys, schema field labels**,
  > node ids and node titles"*, and derive the fixture's positions from `MapStore._build_sidecar`
  > (`store.py:116-149`) rather than listing them, per **C-31**.

  Same amendment is owed to **LLR-N16.2.3**, whose own acceptance text (`:2066-2069`) already
  anticipates *"captions describing glyphs painted from file-derived branch names"* — the door is
  declared open and the threshold does not cover what walks through it. Note also that
  LLR-N16.2.3's threshold, alone among the four, **has no row-length clause at all**.

- **Named weaker variants.**

  | Mutant | Suite | Assessment |
  |---|---|---|
  | **M-L1** coerce the `· campos:` list but not the echoed unresolved key | **survives** | The unresolved key is operator-typed, so it looks trusted — but the operator pastes it, and D11's chip ` Z ? sin definir ` renders it in ALERT beside a control the operator is meant to trust. Both halves, one rule. |
  | **M-L2** coerce at the point of assembling the line | **survives** | Then `graph.schema` is still hostile everywhere else it is read — the inspector's field list, the settings screen, the lens's own key-resolution error path. Coerce at the store boundary (S-02's LLR-STO.1.1) and this class closes once. |
  | **M-L3** derive the fixture's positions by hand-listing `key` and `label` | **survives** | `SchemaField` has four fields; `kind` also reaches a renderer via `darkside.kind_chip` (`darkside.py:202`, which uses `escape()` — B-03's family). Derive from the serialiser. |

---

### S-07 — the lens query language is undefined where it matters and unbounded everywhere · `[major]`

- **What.** D6 makes `search` **the single owner of "what matches"** and deletes
  `views/layered.py:144-149`. The requirements then never define the predicate. Searched across all
  2707 lines: **`re.`, `regex`, `fnmatch`, `eval(`, `compile(` — zero occurrences.** Good news first:
  **there is no regex path and no eval-shaped path in the specified design**, so catastrophic
  backtracking and code execution are both out of scope by construction, and LLR-N14.2.1 (`:1719`)
  correctly forbids the renderer from receiving a query string or a predicate (`frozenset[str]` only).
  What is missing is everything else:

  - **exact vs substring vs prefix vs case-folded is nowhere stated.** LLR-N14.1.2's thresholds
    (`state:risk` → 3 nodes, `E:riesgo` → 2 nodes) are satisfied by *either* reading.
  - **case sensitivity is never stated normatively**, and LLR-N07.1.1 (`:1203-1211`) **deletes** the
    only case rule that ships (`qlower`), replacing it with nothing.
  - **no term-count bound, no query-length bound, no evaluation bound.** LLR-N14.1.3 (`:1672`)
    requires only *"shall classify that token by a declared rule and shall not raise"* — satisfiable
    by any rule at all.
  - **Q-8 is OPEN and blocks Inc-5** (`:2627`): whether a bare word is a free-text term or a
    malformed token.

- **Executed evidence — the substrate D6 promotes to sole owner is already wrong.**

  ```
  A7.2  search_hits('')  -> ['a','b']   (empty query matches EVERY node)
        search_hits(' ') -> ['a','b']
        len(nodes)       -> 2
  ```

  `model.py:182` `if q in hay` — the empty string is a substring of every haystack. The requirements
  document notes this at `:1384` and **no LLR fixes it**; AT-023 (`:1167`) asserts a whitespace query
  is not treated as match-everything for the *lens*, leaving `search_hits` — the thing US-N07's
  trustworthy **count** is taken from — unfixed.

  Cost of evaluation over the whole graph, measured, for the record that the bound is affordable:

  ```
  search_hits('nodo') n=  500    0.3 ms
  search_hits('nodo') n= 2000    1.3 ms
  search_hits('nodo') n=10000    6.5 ms
  search_hits over a 1 MB title  1.1 ms
  ```

  Evaluation is cheap. The exposure is the **undefined predicate**, not the time.

- **Recommendation.** PDR must rule, in requirement text:

  > **LLR-N14.1.4** — A lens term shall match a node when the coerced string form of the addressed
  > value **equals** the term's value under Unicode simple case folding, and shall not match on a
  > substring. *Threshold:* `C:alt` returns **0** nodes where `C:alta` returns 5;
  > `c:ALTA` returns the same set as `C:alta`; the empty query and a whitespace-only query each
  > return **0** matches and are painted as a distinct state from `MATCH` and from `UNDEFINED-FIELD`.

  Equality rather than substring is the recommendation because it is the reading under which
  `EMPTY` and `UNDEFINED-FIELD` — the distinction D11 says the story exists to make — stay
  distinguishable. If PDR prefers substring, that is defensible; **what is not defensible is
  shipping the batch without the sentence.** Add a declared bound (a term-count cap and a query-length
  cap) so LLR-N14.1.3's *"declared rule"* has something to declare.

- **Named weaker variants.**

  | Mutant | Suite | Assessment |
  |---|---|---|
  | **M-Q1** `value.lower() in field.lower()` — substring | **survives every threshold in §3.7 as written** | `state:risk` still returns `['erp','rrhh','alm']`; `E:riesgo` still returns `['rrhh','alm']`. **The requirement cannot tell the two implementations apart**, which is the finding. The `C:alt` arm is what separates them. |
  | **M-Q2** case-sensitive equality | **survives** | Schema keys are uppercase single letters in the shipped fixture, so `c:alta` vs `C:alta` never arises in any declared threshold. Add the lowercase-key arm. |
  | **M-Q3** treat the empty query as `UNDEFINED-FIELD` | **survives** an "is not match-everything" test | Paints the *wrong one* of D11's two carefully distinguished states. AT-023 must assert **which** state, not merely "not all nodes". |
  | **M-Q4** split terms on any whitespace with no quoting rule | **survives** | A field value containing a space becomes two terms; the second is a bare word and lands in Q-8's undecided branch. Q-8 must be answered before this can be tested. |

---

### S-08 — "sink class" is defined as *"every new text sink **this batch creates**"*, which re-encodes batch 1's own failure into the requirement · `[major]`

- **What.** LLR-N06.2.3 (`:1038`) and LLR-N13.2.1 (`:1557`) both scope coercion to *"the **sink
  class** — every new text sink this batch creates — not to a file"*. The intent is right and the
  wording defeats it: **a pre-existing sink that starts receiving newly file-derived text is out of
  scope by the letter.** Both LLRs then name their exclusions explicitly — LLR-N13.2.1 (`:1558-1560`)
  excludes *"the one the recents loop uses today at `app.py:547` and the resume-row pair at `:503`,
  `:505`"* — which is precisely the row US-N13 is rebuilding.

- **Where.** `01-requirements.md:1038-1041`, `:1557-1560`.

- **Executed evidence.** `app.py:505` is the resume row. It is a *pre-existing* sink. A7.1 painted
  U+202E through it, on the home screen, at 140 × 45, in this batch's own surface. The requirement
  that governs this batch's home coercion **names that line as out of scope**.

  Batch 1's closing sentence (`04b:628-631`) reads: *"a condition scoped to a filename gets
  implemented to the edge of that filename. … Fix the wording (`"no code path"`), not just the lines
  — otherwise this recurs a fourth time."* This is the fourth time, one abstraction level up.

- **Recommendation.**

  > Replace *"every new text sink this batch creates"* with *"**every text sink on the surfaces this
  > batch touches, whether the sink is new or pre-existing**"*, and gate it with a **derived**
  > census: a test that enumerates every `Text.assemble`/`.append`/`Static.update`/`notify` call
  > reachable from `HomeScreen`, `MapScreen`, `HelpScreen` and asserts each file-derived argument is
  > coerced. Deriving the list is what stops it being wrong for the fourth time (**C-31**).

  I am **not** asking for B-03's ~20 legacy `escape()` sites tree-wide — that deferral is a
  legitimate scope decision. I am asking that the three sites on the surfaces this batch rebuilds
  (`app.py:503`, `:505`, `:547`) come **in**, because excluding them means US-N13 ships a coerced
  card in a row whose neighbour cell is not.

- **Named weaker variants.**

  | Mutant | Suite | Assessment |
  |---|---|---|
  | **M-K1** hand-list the in-scope sinks in the requirement | **survives** | Batch 1's hand-maintained dependant list *"was wrong three times in a row"* — the IFC template's own words, quoted at `01-requirements.md:2119-2121`. D13 in `PLAN.md` is a fourth instance: the Phase-0 census said three routes and the derived count was five. Derive. |
  | **M-K2** census only `mapper/app.py` | **survives** | D13 is the executed counterexample: `screens/factory.py:416` and `screens/settings.py:95` were both missed by an `app.py`-scoped census. Quantify over the tracked tree. |
  | **M-K3** census the call sites but not their arguments | **survives** | A `notify()` with a constant string and a `notify()` interpolating `str(e)` are the same call site and different findings. The census oracle must be *"file-derived argument"*, which means it needs a provenance rule, not a grep. |

---

### S-09 — N-14's markup half is still open: thirteen `notify()` sites interpolate exception text with markup parsing on · `[major]`

- **What.** Batch 1's N-14 had two halves. The `_event_toast` half **is fixed on `master`** — I
  verified `app.py:1352`, `:1395/1397`, `:1418`, `:1439`, `:1751` all route through
  `darkside.plain`, and `:1134` and `:1399` and `:1768` carry `markup=False`. **The `notify` half is
  not.** Thirteen sites interpolate without `markup=False` and without coercion.

- **Where.** `mapper/app.py:626`, `:640`, `:661`, `:666`, `:729`, `:1022`, `:1024`, `:1027`,
  `:1682`; `mapper/screens/factory.py:350`, `:371`, `:395`, `:397`.

- **Executed evidence.** The sink still raises in textual 8.2.8:

  ```
  Content.from_markup RAISES MarkupError: closing tag '[/bold]' does not match any open tag
      <- 'error cargando mapa: [/bold]OWNED'
  Content.from_markup ok : 'no se pudo crear el mapa: [bold red]x'
  ```

  The second row matters as much as the first: it does **not** raise — it silently **restyles** the
  operator's error message, which is N-2's forgery argument. `app.py:1024` is
  `self.notify(str(exc), severity="error")` on the repo-connect path, where the exception text can
  carry remote-derived content.

- **Why it belongs in this batch's report even though it is a carry.** LLR-N06.2.2 (`:1008`) **adds a
  new notification** (`nada que plegar` / `este nodo no tiene descendientes`). Its copy is a fixed
  literal, so it is safe as specified — but it is a **new toast sink that appears in no `SINK` line
  of §4** and under no coercion LLR. The batch is adding to a sink class it has not finished
  cleaning.

- **Recommendation.** `markup=False` plus `darkside.plain()` on all thirteen, and add the new
  notification to §4's flow so the next reviewer reads a declaration rather than an omission.
  One line each; no design question.

- **Named weaker variants.**

  | Mutant | Suite | Assessment |
  |---|---|---|
  | **M-N1** `markup=False` without `plain()` | **survives** | Stops the `MarkupError` and the restyling; leaves ESC/OSC-52 reaching the terminal. Batch 1 measured both channels separately and needs both arms. |
  | **M-N2** `plain()` without `markup=False` | **survives** | `plain()` deliberately does not escape markup (`darkside.py:280-283`). Executed above: `'[/bold]OWNED'` survives `plain()` and still raises `MarkupError`. |
  | **M-N3** fix `app.py` and not `screens/factory.py` | **survives an `app.py`-scoped census** | §2.1b again. `factory.py:397` is `f"no se pudo generar: {exc}"` over an office-template path. |
  | **M-N4** assert `notify` was called rather than asserting the painted toast | **survives** | Batch 1 stopped at *"the render raises"* because `ToastRack` does not mount under `run_test` (`04b:492-496`) and correctly declined to call it a blocker. If this batch wants it closed, the test must reach the rendered toast; otherwise it stays `major`. |

---

## 3 · Minors

| id | Finding | Where | Executed evidence | Recommendation |
|---|---|---|---|---|
| **S-10** | **`Canvas.rows()`'s style sink fails open, silently.** No tone is file-derived today — every value is a `darkside` constant or a `_GREYS` literal indexed by an integer (`radial.py:111-114`, `:134`) — but LLR-CNV.1's only threshold on the value is *"the background cell's style names the written tone"* (`:713`), which asserts **pass-through**, the opposite of a guard. | `mapper/canvas.py:74,78`; `01-requirements.md:713` | 14 malformed style strings (`#zzzzzz`, `not-a-colour`, `on nosuchcolour`, `color(999)`, `rgb(300,300,300)`, `link https://evil.example/x`, a constructed ESC sequence, a 1600-char style) through `Text.append` **and** through the real `Canvas.rows()`, truecolor on: **all 14 render OK, none raises.** Meanwhile `Style.parse('not-a-colour')` **does** raise `StyleSyntaxError` — Rich's `Text.render` swallows it via `get_style(..., default="")`. **So a malformed tone does not crash a render; it silently paints unstyled.** | Answer the traced question in the LLR: *"the value of `dots` and `bgs` shall be a token name drawn from the design module's declared token set; `rows()` shall paint a cell whose tone is not in that set in a declared fallback tone."* Closes **Q-10** (`#a3a3a3` at `radial.py:18`, `:620-621`) in the same sentence. **M-V1** *validate at write time in `put`/`dots`* — **survives**, and misses `radial.py:121`'s direct `cv.dots[...] = hue` assignment, which bypasses any setter. Validate in `rows()`, which is the one place all four layers converge. |
| **S-11** | **B-01's family is five exception types, not one `KeyError`.** `store.load` raises non-`MapStoreError` exceptions on five distinct hostile sidecars, so `except MapStoreError` callers do not catch them. | `mapper/store.py:193`, `:181-182`, `:186`, `:302-317` | `noattpath` → `KeyError: 'path'` · `toplist` (sidecar is a list) → `AttributeError: 'list' object has no attribute 'get'` · `nodescalar` (a node is a string) → `AttributeError: 'str' object has no attribute 'get'` · `titlemap` (`title:` is a mapping) → `sqlite3.ProgrammingError: Error binding parameter 4: type 'dict' is not supported` · `listfield` → same `ProgrammingError`. | Fold into **LLR-STO.1.1** (S-02): *"`MapStore.load` shall raise only `MapStoreError` for any input it rejects"*, with the fixture set derived from `_build_sidecar`'s positions. **M-B1** *add a `.get("path","")` default* — **survives** the `KeyError` arm and leaves the other four. |
| **S-12** | **`mapper/export.py::save_svg` is a declared §4 `SINK`** (`:2145`, and on `canvas_rows`'s consumer list `:2286`) **with no coercion requirement anywhere.** Trigger B4 fired on it for the byte change; nobody asked what text it writes. | `01-requirements.md:2145`, `:2286`; `mapper/export.py` | LLR-CNV.2.1's threshold (`:797`) asserts braille-glyph parity between the exported and on-screen objects, and nothing about the text. | State it: *"the exported SVG shall contain no code point excluded by the coercion range list"*, sharing S-04's ranges. An SVG leaves the machine; the terminal's own escaping does not travel with it. |
| **S-13** | **Home-mount cost is unbounded and writes to disk per map per mount.** `store.load` calls `_reindex` (`store.py:288`), which opens a SQLite connection and writes; `_sparkline_text` (`app.py:415-437`) is a 14 × N_maps `stat()` loop (**P-15**'s hand-glob). | `mapper/app.py:415-437`, `:451`, `:537-552`; `mapper/store.py:208`, `:288` | 200 trivial maps: cold **1064.2 ms**, warm **253.5 ms**, sparkline **58.0 ms**. Warm is faster only because the text hash matches and `_reindex` short-circuits at `store.py:295` — the first mount after any edit pays full price. | Fold the budget into **HLR-N13.3** (S-03). Also: **`P-15` proposes `MapStore.list_maps`** — give it a cached metrics read so the sala does not reindex the workspace to draw thumbnails. |
| **S-14** | **Correction to the record: batch 1's `F-m4` (YAML alias bomb) is not exploitable here, and should be closed as measured rather than left undispositioned.** | `mapper/store.py:206` | Bombs of 411 / 511 / 625 bytes at 8 / 10 / 12 alias levels: load **24.2 / 14.6 / 17.0 ms**, peak Python heap **0.0 MB**, amplification ×73 / ×56 / ×49. PyYAML aliases **share objects rather than deep-copying**, and `_graph_from_sidecar` (`store.py:151-197`) reads only `schema`, `documents` and `nodes` — a bomb under any other key is never traversed. | Record the disposition. `F-m4` has sat undischarged since PDR; *"no disposition"* is what turns a measured non-issue into a recurring review cost. Note this does **not** cover a bomb placed **under `nodes:`**, which is traversed — that arm belongs in **LLR-STO.1.1**'s fixture set. |

---

## 4 · Answers to the questions the brief asked

**Does `darkside.plain()` cover every new sink, and is it actually called on every path?**
No, on both halves.

- **Coverage of the character class:** it covers C0 (minus tab/newline) and C1. It does **not** cover
  bidi overrides, isolates, marks, zero-width characters, `U+FEFF` or `U+2028/9` — seven classes
  measured surviving. **S-04.**
- **Coverage of the sinks:** §4 names `darkside.plain` at **exactly one flow node** — `home_cards`,
  line 2206. `canvas_paint`, `match_set`, `overflow_declaration` and `legend` declare **no coercion
  transform at all**, even where the owning LLR *is* the coercion LLR (`overflow_declaration`'s pill
  node is owned by LLR-N06.2.3 and its declared `in`/`out` shows no coercion). The IFC therefore
  cannot be read to tell you where the helper is required.
- **Called on every path:** the `_event_toast` family **is** fixed on `master` (verified at
  `app.py:1352`, `:1395`, `:1397`, `:1418`, `:1439`, `:1751`). Thirteen `notify` sites are not.
  **S-09.**
- **Batch 1's §2.1b lesson, applied to the new sinks as instructed:** the load-error path *was*
  fixed (`app.py:1133-1137` now has `plain(str(e))` **and** `markup=False`). The identical defect
  ships in its siblings at `:626`, `:640`, `:661`, `:666`, `:729`, `:1022`, `:1024`, `:1027`,
  `:1682` and four sites in `screens/factory.py`. And the *requirement wording itself* now carries
  the same defect one level up — **S-08**.

**U+202E in a home card or a legend row — can it reorder what the operator reads?**
Yes, and it does today. A7.1 read it off the real compositor at 140 × 45: the painted resume row is
`↩ retomar  bidi / informe <U+202E>fdp.acta   última sesión`, with `0x202e` present in the painted strip.
The operator reads `atca.pdf`. And **S-05** shows truncation turns a *balanced* override into an
unterminated one that governs the card's remaining columns. The legend is worse in one respect:
LLR-N16.2.3's threshold is the only one of the four with **no row-length clause at all**.

**Does file-derived text reach a markup-parsing sink on the new surfaces?**
On the *specified* new surfaces, no: `Text.from_markup` and `Panel(title=` appear **zero** times in
2707 lines, ViewState carries no free text, `views/` may not import Textual, and LLR-N14.2.1 forbids
the renderer receiving a query or a predicate. The exposure is in the sinks the batch **inherits**
and in the one it **adds without declaring**: thirteen `notify()` sites (**S-09**) and LLR-N06.2.2's
new toast, which appears in no `SINK` line of §4.

**Denial of service.** Measured throughout §2. Summary: **titles are not the problem** (a 1 MB title
renders in 2.1 ms and `fit()` handles it in 16.1 ms); **structure is** — a 3-node cycle is an instant
crash, a 500-node chain is 2.6 s, a 3280-node tree is 3.4 s, a 10 000-node map is 9.1 s, and a
200-map workspace is 1.06 s before any card paints. No bound of any kind is specified anywhere.

**Does anything persist new state?** No. **Q-5 is OPEN** and `01-requirements.md:2624`, `:327-334`
record it as neither IN nor OUT — S-3b stays `REFINE`, **no HLR, LLR or AT references repo
provenance, a `◍` glyph or any persisted source field**, and the disposition explicitly reserves a
migration answer for a future increment. **Nothing to review, and that is the correct outcome.** If
the architect lens rules Q-5 **IN**, this review must be re-opened: a new sidecar key is a new
file-derived string on a new persisted surface, and it inherits S-02, S-06 and S-11 wholesale.

---

## 5 · Which carried items this batch's new surfaces make more reachable

| Carry | Was | Becomes | Why |
|---|---|---|---|
| **N-10** (U+202E passes `plain()`) — brief's B-06 part 4 | `minor`, carried | **`major`** (S-04) | The sala is the first surface putting many maps' titles in one adjacent column, and it renders **without the operator opening anything**. A reordering attack is worth more on a comparison surface. Executed on the painted screen. |
| **F-M5 / C-12** (`MapStore.load` value tolerance) — brief's B-01 | `major`, **never discharged** | **`blocker`** (S-02) | `HomeScreen` loads every map and US-N13 computes card data from each. Executed: one non-string field value denies all six cards in the shape the story's own "load once per mount" threshold pushes you toward. |
| **F-m1 / B-03** (~20 `escape()` sites) | `minor`, recommendation-only | **still `minor`, but the deferral is now load-bearing** (S-08) | `01-requirements.md:1558-1560` excludes `app.py:503`, `:505`, `:547` **by name** — the exact rows US-N13 rebuilds. The tree-wide deferral is fine; these three are not. |
| **N-14** (uncoerced sinks) — brief's B-07 | `major`, open | **`major`, half closed** (S-09) | `_event_toast` half fixed on `master`. Markup half open at 13 sites, and LLR-N06.2.2 adds a fourteenth toast sink undeclared in §4. |
| **C-8 / F-M3** (inventory omits schema labels, `state`, `meta`, `path`, `node.id`) | `major`, **never discharged** | **directly reachable** (S-06) | LLR-N14.1.1 echoes `graph.schema` into a painted line and LLR-N14.2.3 covers *values* only. The omitted nouns are exactly the ones the lens now paints. |
| **N-6 / N-8 / N-9** (ADS · `urlparse` · exe policy) | carried | **unchanged** | `osopen` is not touched by this batch (`PLAN.md` §5 trigger C row). Re-confirmed: no scope change. Carry forward. |
| **N-11** (kind inference substring) | informational | **unchanged** | Operator-typed input; not a file-derived surface. Carry. |
| **F-m4** (YAML alias bomb) | `minor`, **no disposition** | **close as measured** (S-14) | Amplification ×49–×73 with peak heap 0.0 MB; unread keys are never traversed. |

---

## 6 · Conditions

Blocking — must land in `01-requirements.md` **before** any Phase-3 increment starts:

- **C-1 (S-01)** — `LLR-CNV.4.1`, cycle- and depth-safe traversal, with the correctness positive
  control (`b=3 d=7` → `2187`) and the depth arm (20 000-node chain). Mutants M-C1…M-C4 named.
- **C-2 (S-02)** — `LLR-STO.1.1` (store-boundary type coercion, positions **derived** from
  `_build_sidecar`) and `LLR-N13.1.5` (per-map failure containment, threshold = **painted card
  count**). Discharges C-12. Mutants M-S1…M-S4 named.
- **C-3 (S-03)** — `HLR-N13.3`, a declared home-mount budget with a per-map over-budget declaration;
  `AT-025` promoted under `LLR-N13.1.5`. Mutants M-H1…M-H3 named.

Due within the increments they touch:

- **C-4 (S-04, S-05)** — replace *"0 control bytes"* with the explicit range list in all four
  coercion thresholds; widen `_CONTROL_MAP`; coerce **before** truncating; add the
  balanced-at-source / split-at-width fixture arm and assert on the **painted row**.
- **C-5 (S-06)** — widen LLR-N14.2.3 and LLR-N16.2.3 from *"field value"* / *"binding label"* to
  every file-derived string on those surfaces, fixture positions derived from `_build_sidecar`.
  Add the missing row-length clause to LLR-N16.2.3.
- **C-6 (S-07)** — settle the lens predicate (equality vs substring, case folding) and the empty-query
  state in requirement text; declare a term-count and query-length bound; **answer Q-8**.
- **C-7 (S-08)** — reword *"every new text sink this batch creates"* to cover pre-existing sinks on
  the touched surfaces, gated by a **derived** census; bring `app.py:503`, `:505`, `:547` in scope.
- **C-8 (S-09)** — `markup=False` + `plain()` on all 13 `notify` sites; declare LLR-N06.2.2's toast
  in §4.

Recommendations — do not gate:

- **C-9 (S-10)** — declare the `dots`/`bgs` value domain as a token set with a fallback tone; closes
  Q-10 in the same sentence.
- **C-10 (S-12)** — extend the coercion range list to the SVG export sink.
- **C-11 (S-13)** — give `MapStore.list_maps` (P-15) a cached metrics read.
- **C-12 (S-14)** — record F-m4's disposition.

---

## 7 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Each finding has what · where · why · recommendation | ✓ | §2 headings S-01…S-09; §3 table columns for S-10…S-14 |
| Each finding has a severity rating | ✓ | `[blocker]` ×3, `[major]` ×6, `[minor]` ×5 — counts restated in §0 |
| No secret values appear in the output | ✓ | No credential, token or key was read or emitted. Attachment/`osopen` surfaces were not touched by this batch and were not probed. |
| Verdict is explicit | ✓ | §0 — `blocked` |
| New tool/integration scope and blast radius addressed | ✓ | **None added.** `PLAN.md` §5 trigger C: *"`osopen` is not touched."* Verified: no new dependency in `pyproject.toml`, no MCP/Composio/network surface in scope. Blast radius of the batch is local rendering of local files. |
| Every finding backed by an executed probe | ✓ | A1–A8, §1. The three blockers were reproduced **under `App.run_test`**, not inferred. |
| Every required control carries a **named weaker variant**, not only its deletion | ✓ | M-C1…M-C4, M-S1…M-S4, M-H1…M-H3, M-P1…M-P4, M-F1…M-F3, M-L1…M-L3, M-Q1…M-Q4, M-K1…M-K3, M-N1…M-N4, M-B1, M-V1 — **31 named mutants** |
| **My own proposed control was mutation-tested against itself** | ✓ | **M-C3 is my first candidate for S-01 and it FAILED** the depth arm (`RecursionError` on a 3000-deep chain). Recorded rather than quietly replaced. |
| No code modified | ✓ | `git status --short` over `mapper/`, `tests/`, `01-requirements.md`: clean. Only `02b-security-review.md` created. |
| `prototypes/` untouched, nothing staged | ✓ | Not read, not written, not staged. No `git add`, no commit. `mapper.db` not committed. |
| No control byte written into any file | ✓ | Every payload constructed with `chr(0x...)` at runtime. This document names code points and uses `\u`-escape *text*; it contains no control byte. Batch 1's three incidents (two NULs, one backspace-in-a-regex) not repeated. |
| Fixtures outside the repo | ✓ | All under the system temp directory (`mapsec_a1_*` … `mapsec_pilot_*`); probe scripts under the session scratchpad. |

---

## 8 · Gate verdict

> ### `blocked`
>
> **The PDR may not approve the interface changes for implementation until C-1, C-2 and C-3 are
> written into `01-requirements.md`.**
>
> The two interface changes themselves — `ViewState`/`IRenderer` (D4, R-012) and `Canvas`'s widening
> (D9, R-016) — are **sound from a security standpoint and I approve both.** `ViewState` is frozen,
> fully defaulted, carries no live object, no predicate and no free text; every field is an int, a
> bool, an id string, an id set or a `DiffResult`, and Rule 4's *"the renderer receives ids, never
> predicates"* is the right call. `Canvas`'s widening is additive. Neither is why the gate fails.
>
> The gate fails because **the batch puts a `Graph` that nothing validates onto a screen that renders
> every map in the workspace**, and two of the three ways that goes wrong are already app-killing
> defects on `master` that 245 green tests do not see. US-N13 is what turns "the operator opened a
> hostile map" into "the operator started the application".
>
> On re-submission I will re-execute A1, A4, A5.4, A6.2, A6.4, A7.1 and the M-C/M-S/M-P mutant sets.
> A claim that these landed is not evidence that they landed.
