# Code review — increment 002b (`rail.py`, `factory.py`)

| Field | Value |
|---|---|
| Reviewer | `code-reviewer` (independent gate) |
| Date | 2026-08-26 |
| Scope | `mapper/widgets/rail.py`, `mapper/screens/factory.py`, `tests/test_repair_depth.py`, `pyproject.toml` — diff against `d6b60e6` |
| Requirement | `HLR-R02` · `LLR-R02.1` as amended by **A-6** · `LLR-R02.2` · `LLR-R02.3` |
| Verdict | **PASS WITH CONDITIONS** — one HIGH, in the TEST file, not in the source |

---

## Verdict

**PASS WITH CONDITIONS.** The two de-recursed traversals are correct — I re-derived
equivalence independently over 46,548 comparisons across five shape families the author's
own equivalence set does not contain, and found **zero** disagreements. The memo's decline
condition is correct **and** complete — I proved it exhaustively rather than by argument.
The active-path guards do **not** false-fire on a diamond. `_depth` terminates on every
cyclic parent chain I could generate.

The HIGH is not a source bug. It is a test whose docstring says *"This is the node that
notices"* about the one thing it provably cannot notice. I changed the rail's indent cap
from `RAIL_WIDTH` to `6` in a **copy** of the tree and the entire 356-node suite passed —
while that cap renders the wrong row at 33 of 40 depths. Per this batch's own rubric a test
that gives false confidence blocks; the fix is small and local to `tests/test_repair_depth.py`.

Everything else is MEDIUM or LOW and is a recommendation.

---

## Findings

### F1 — the indent cap's value is unpinned; the node that claims to pin it cannot fail · **HIGH**

- **Where:** `mapper/widgets/rail.py:227` (the cap) ·
  `tests/test_repair_depth.py:1149-1166` (`test_tc_r30_the_indent_cap_cannot_change_a_rendered_row`)
- **What:** the test re-implements the production expression in its own body —

  ```python
  capped = darkside.fit("  " * min(depth, RAIL_WIDTH) + marker + label, width)
  true   = darkside.fit("  " * depth              + marker + label, width)
  assert capped == true
  ```

  It asserts a property of `darkside.fit` against a literal it wrote itself. It never calls
  `_body`, `render`, or anything that reads `rail.py:227`. So it is **structurally incapable
  of failing** when the cap in `_body` changes — which is exactly what its docstring claims
  it protects: *"If a future change stops truncating, the cap would silently eat the indent
  and no golden at depth 2 would notice. This is the node that notices."*

  The packet's Risk 2 half-names this and then mis-states it: it says the gap is *"someone
  who removed the `fit` call"*. The real gap is one level earlier — **the cap value itself**.

- **Executed.** Copy of the tree in the session scratchpad, working tree never touched:

  ```
  MUTATED cap 24 -> 6 in the COPY only
  --- working tree untouched? --- 1     (grep -c "min(depth, RAIL_WIDTH)" == 1)

  $ pytest -q -p no:randomly -o addopts=      # in the copy
  356 passed in 57.27s
  ```

  And `cap = 6` is genuinely wrong:

  ```
  cap=24: depths whose rendered row is WRONG -> [] (n=0)
  cap= 6: depths whose rendered row is WRONG -> [7, 8, 9, ... 18] ... (n=33)

  depth 12, true cap 24 : '                   …'
  depth 12, mutated cap 6: '            ▾ titulo'
  ```

  Any cap `C` with `3 <= C <= 9` is wrong at some depth and green on the whole suite. Only
  `C >= 10` is safe (at `C >= 10` the indent alone already exceeds `RAIL_WIDTH - 4 = 20`
  cells, so `fit` truncates identically).

- **Why the mutation battery missed it.** Transcript line 66:
  `N7 [plausible-weaker] rail.py: lower the indent cap from RAIL_WIDTH to 1`. Measured,
  `fixtures/legacy.mmd` is **8 nodes, max depth 2** — so `cap = 1` reddens the six legacy
  goldens (5 `MASTER_RAIL_DIGESTS` + the composed-screen node) and the arm reports 6 RED.
  The arm went green-to-red for a reason that has nothing to do with the predicate it was
  written to pin. This is a *plausible-weaker* arm that was not weak enough: the plausible
  mutation is not `1`, it is "a number that looks like it fits the pane".

- **Why it matters:** `AT-R16`'s only depth-5000 rail node asserts `text.plain.strip()` —
  non-emptiness — and `len(visible_rows()) == DEEP + 1`. Nothing anywhere in the suite reads
  a *rendered row at depth ≥ 3*. The cap is the increment's largest behavioural change to
  the shipped picture and it is unprotected.

- **Suggested fix** — replace the self-referential assertion with one that drives `_body`:

  ```python
  def test_tc_r30_the_indent_cap_cannot_change_a_rendered_row():
      rail = _rail_for(_chain(40))          # depths 0..40, past the cap
      capped = _fingerprint(rail.render())

      import mapper.widgets.rail as rail_mod
      # the same render with the TRUE indent, built by the production path
      original = rail_mod.OutlineRail._body
      ...  # simplest form: parametrise the cap for the test, or
      # compare rail.render() row-by-row against darkside.fit("  " * depth + ...)
      rows = rail.render().plain.splitlines()[2:]
      for (nid, depth), line in zip(rail.visible_rows(), rows):
          want = darkside.fit("  " * depth + "▾ " + darkside.plain(nid), RAIL_WIDTH - 4)
          assert line.startswith(want), f"depth {depth}: the cap changed the row"
  ```

  The load-bearing property is *the assertion must read `rail.py:227` through a call*. Any
  form that does is acceptable; the current form is not. Re-run arm N7 with `cap = 6` (not
  `1`) afterwards and require it RED.

---

### F2 — the rail refuses a map it can draw: a false refusal, and a public-method regression · **MEDIUM**

- **Where:** `mapper/widgets/rail.py:96-106` (`subtree_missing`), `122-170` (`_missing_map`),
  `192-201` (`_body`)
- **What:** `_missing_map` visits **every node in the graph**, not the queried subtree, and
  raises on a cycle anywhere. `subtree_missing` calls it unconditionally and does not catch
  the raise. `_body` therefore also raises, and `render` paints
  `no se puede dibujar: el mapa tiene un ciclo` for a map whose drawn tree is clean.

- **Executed:**

  ```
  P2 - DISCONNECTED CYCLE: does the rail refuse a map master draws?
    visible_rows() = [('r', 0), ('a', 1)]  <- the drawn tree is clean
    MASTER subtree_missing('r') = 2 (returns, no raise)
    NOW    subtree_missing('r') -> ValueError: cycle through p: the graph is not a tree
    NOW    render() = '  no se puede dibujar:\n  el mapa tiene un ciclo'
  ```

  Graph: `r→a` plus a disconnected `p⇄q`. On `master` the rail draws this map. After this
  increment it refuses it.

- **Why it matters:** §4 of the requirements prices a false refusal *"as high as passing
  wrong work"* (C-53), and amendment A-4 restated `AT-R03` specifically to prove *"the new
  cycle rule has not widened into a false cycle claim"*. `HLR-R02` asks for depth not to
  crash; it does not ask for a new refusal. Separately, `subtree_missing(node_id)` is a
  public method that `tests/test_rail.py` calls: it answered a single-node question in
  `O(subtree)` and now does `O(N + E)` whole-graph work and can raise for a cycle it was
  never asked about.

  **Two things hold the severity at MEDIUM, and I verified both.** (1) It is declared —
  packet Risk 4, measured and asserted. (2) It is unreachable through the shipped surface:
  `OutlineRail` is constructed only at `mapper/app.py:1126` (MapScreen), `_ImportPreviewScreen`
  composes no rail, and increment 1 made `MapStore.load` refuse cycles — so no cyclic graph
  reaches the rail at all today. It is also consistent with 2 of the 3 renderers (per the
  packet's own table, radial and layered both refuse the disconnected shape).

- **Suggested fix** — the same fallback the `None` branch already has, plus stop making a
  single-node query pay for a whole-graph memo:

  ```python
  def subtree_missing(self, node_id: str) -> int:
      # one node, one exact walk — no whole-graph memo, no cycle it was not asked about
      return self._missing_walk(node_id, self._child_index())

  # in _body:
      try:
          totals = self._missing_map(index)
      except ValueError:
          totals = None            # a cycle outside the drawn tree is not the rail's refusal
      if totals is None:
          needed = {self.graph.root_id, *(nid for nid, _ in rows)}
          totals = {nid: self._missing_walk(nid, index) for nid in needed}
  ```

  `_rows` keeps raising, so a cycle **on the drawn path** still paints the notice — which is
  the case the guard exists for.

---

### F3 — the factory's `AT-R16` node asserts strictly less than its rail sibling · **MEDIUM**

- **Where:** `tests/test_repair_depth.py:1198-1209`
  (`test_at_r16_the_factory_tree_survives_a_depth_5000_map`)
- **What:** the rail's `AT-R16` node drives the composed screen through `app.run_test`, and
  its docstring is explicit that this matters (*"through the composed surface, not through a
  direct call"*). The factory's node calls `screen._tree_lines()` directly. The composed
  factory screen at depth 5000 **still dies**, in `_refresh` — the exact method
  `_tree_lines`'s own docstring names as *"outside any guard"*:

  ```
  recursionlimit: 1000
  POSITIVE CONTROL cursor=root: OK
  _tree_lines() at depth 5000: OK, 5001 lines
  _step_meter() at depth 5000: OK
  _preview() with the cursor deep (what _refresh calls): *** RecursionError
  ```

  `_refresh` (`factory.py:341-353`) calls `_preview()` → `Graph.resolve_document`
  (`model.py:97`), which is still recursive.

- **Why it matters:** the cause is legitimately out of scope — `model.py` is fenced and A-3
  defers `resolve_document` to increment 3, and the packet says so in pending item 1. My
  finding is against the **claim and the oracle**, not the source: §1's headline *"A
  depth-5000 map now draws … in the factory tree in 1.56 s"* is true of the tree pane and
  false of the factory screen, and the asymmetry between the two `AT-R16` nodes is
  undeclared. A reader comparing the two nodes will conclude the factory was tested the same
  way the rail was.

- **Suggested fix:** no code change. Add one sentence to the node's docstring and to §1 —
  *"the tree pane, not the screen: `_refresh` also calls `_preview`, which is still fatal at
  depth via `resolve_document` (A-3, increment 3)"* — and carry a composed-screen factory
  node into increment 3 as the thing that must go green when `resolve_document` is fixed.

---

### F4 — C-17: the factory tree uses `rich.markup.escape` where this codebase's documented coercion helper is `darkside.plain`; ANSI/OSC bytes from a file-derived title reach the compositor · **MEDIUM**

- **Where:** `mapper/screens/factory.py:246` (`title = escape(node.ficha.title or nid)`);
  contrast `mapper/widgets/rail.py:222` (`label = darkside.plain(node.ficha.title or nid)`)
- **What:** `darkside.plain`'s docstring (`darkside.py:276-287`) is unambiguous — it is *"the
  single coercion helper every renderer of sidecar text must pass through"*, and it says in
  as many words that `rich.markup.escape` *"is a no-op that merely prints visible
  backslashes"* in a `Text`. `_CONTROL_MAP` (`darkside.py:269-273`) exists precisely because
  *"an ANSI cursor-move or an OSC-52 clipboard write inside a ficha title reaches the
  compositor verbatim, and markup escaping does nothing about either — measured"*.

- **Executed** with a title carrying `ESC[31m` and an OSC-52 clipboard write:

  ```
  P6 - C-17: control bytes in a file-derived title
    rail  ESC present: False | BEL: False
    factory ESC present: True | BEL: False
    factory raw: '▸ ok\x1b[31mRED\x1b]52;c;aGVsbG8=\n'
    darkside.plain(evil): 'ok�[31mRED��]52;c;aGVsbG8=�'
    rich escape(evil)   : 'ok\x1b[31mRED\x07\x1b]52;c;aGVsbG8=\x07'
  ```

  Same increment, same threat, two files, opposite answers. The rail is right.

- **Why it matters, and its honest severity:** this is **pre-existing on `master`** — the
  increment inherited the `escape(...)` call and moved it into the stack loop. It is not a
  regression. It is a MEDIUM because (a) the increment rewrote that exact line and had the
  correct helper open in the sibling file, (b) the codebase documents the rule and this
  violates it, and (c) `factory.py` has **eleven** more `escape(...)` call sites
  (lines 286, 289, 300, 304, 306, 309, 327-329, 336-338, 344), all on file-derived text, so
  a one-line change here does not close the surface.

- **Suggested fix (this line only, in this increment):**

  ```python
  title = darkside.plain(node.ficha.title or nid)
  ```

  This changes rendered bytes for titles containing markup metacharacters, so
  `MASTER_FACTORY_TREE_DIGEST` must be re-captured — do it deliberately, with the reason
  recorded. Hand the remaining eleven sites to `security-reviewer` as a `factory.py`-wide
  C-17 sweep; they are outside this increment's correctness lane.

---

### F5 — "Never propagates" is over-claimed: both surfaces catch `ValueError` only · **LOW**

- **Where:** `rail.py:173-190` (`render`), `factory.py:215-222` (`_tree_lines`)
- **What:** both docstrings say *"Never propagates"*. Both catch `except ValueError`.
  An edge whose `child_id` is not in `graph.nodes` reaches `self.graph.nodes[nid]` and
  escapes:

  ```
  P5 - dangling child edge: does render/_tree_lines still propagate?
    rail.render: PROPAGATED KeyError: 'ghost'
    factory._tree_lines: PROPAGATED KeyError: 'ghost'
  ```

- **Why it is LOW and not higher:** identical on `master`, and I could not find a shipped
  door that produces one — `mermaid.py:113`, `import_csv.py:81/87/102` and `github.py`
  register both endpoints before adding the edge, and `preview_csv`'s second pass explicitly
  guards `if parent_id in graph.nodes`. So it is a false docstring, not a live crash.
- **Suggested fix:** either say what is actually true (*"never propagates the cycle guard"*)
  or widen to `except (ValueError, KeyError)`. Prefer the docstring fix — do not widen a
  catch to make a sentence true.

---

### F6 — `except ValueError` is over-broad in type: an unrelated `ValueError` is reported to the operator as a cycle · **LOW**

- **Where:** `rail.py:184`, `factory.py:219`
- **What:** any `ValueError` from anywhere under `_body` / `_tree_text` — not only the guard —
  paints `el mapa tiene un ciclo`. That is a false diagnosis shown to the operator, in a
  batch whose subject is *"a bad file costs me an error message I can act on"*. Packet
  Risk 3 discusses the message's *language*, not its *truthfulness*.
- **Why LOW:** I could not construct a reachable non-guard `ValueError` on today's tree.
- **Suggested fix:** a module-level `class CycleError(ValueError)` shared with increment 2's
  renderers, raised by the guards and caught by name. It keeps increment 2's `ValueError`
  identity (subclass) while making the catch exact.

---

### F7 — `chr(10)` where the file means `"\n"` · **LOW**

- **Where:** `rail.py:187`
- `"  no se puede dibujar:" + chr(10) + "  el mapa tiene un ciclo"` — the rest of both files
  uses `"\n"` in f-strings (`rail.py:207/244`, `factory.py:247`). The packet's byte-scan
  explicitly permits `\n`, so there is no probe forcing this. Unexplained obfuscation in a
  line an operator reads. Use `"\n"`.

---

### F8 — the `TC-R32` termination census is rooted at a hand-listed file tuple · **LOW (informational)**

- **Where:** `tests/test_repair_depth.py:1396-1399` (`TRAVERSAL_FILES`)
- `graph_touching_methods()` is beautifully derived *within* its root, and its root is two
  hand-typed paths. That is the A-6 shape one level down — the pattern the packet itself
  records as *"a derived probe with a hand-picked root is not a derived probe"*. It is
  defensible here (the census is scoped to *this increment's* two files by design, and
  `TC-R29`'s recursion probe is rooted at the whole package), but the requirement's amended
  wording is *"the traversal surface … derived from the tree, never named"*. Worth a line in
  the post-mortem rather than a change now.

---

### F9 — `_tree_text`'s indent is uncapped and quadratic in characters · **LOW (observation)**

- **Where:** `factory.py:244` — `prefix = "  " * depth + "▸ "`
- The rail got the indent cap; the factory did not, and the author measured the consequence:
  **25,043,898 characters** of `Text` for a depth-5000 chain. Growth is `O(depth²)` in
  characters, so a depth-20,000 map is ~400 MB of `Text` — an unbounded-memory surface that
  `MapStore.load` places no ceiling on.
- **Why I am not asking for the fix:** `#factory-tree` is a `Static` in a `40%`-width pane
  with no `darkside.fit` call, so unlike the rail it may **wrap** rather than truncate, and a
  cap there would change output. The rail's proof does not transfer. Recording it so the
  asymmetry is a decision rather than an omission; `LLR-R02.3`'s *declared degradation* is the
  natural home for it if it is ever worth closing.

---

## What I established independently, versus what I accepted

### Established independently (executed, not read)

| # | Question the brief asked | How I answered it | Result |
|---|---|---|---|
| 1 | Do the two stack loops emit the same rows, at the same depths, as the recursive originals? | Differential fuzz against verbatim copies of the `d6b60e6` implementations, over **my own** shape families — random trees, general DAGs, multi-root forests, **duplicate edges**, **dangling child edges** — × derived collapse sets × 4 cursor positions. **46,548 comparisons.** Exceptions compared as values, so a spurious raise counts as a mismatch. | **0 mismatches** across `visible_rows`, `subtree_missing`, `_tree_text`, `_depth`, `_max_depth`. The author's 8-shape set contains none of duplicate edges, dangling edges, or multi-root forests; all three are clean. |
| 2 | Is `_missing_map`'s decline condition correct **and complete**? Can it answer and be wrong? | **Exhaustive**, not sampled: every graph on 5 nodes in which each node has ≤1 parent (all 6⁵ parent assignments), every node's total compared against the verbatim shipped dedup walk. | **6,480 answered node-totals checked, 0 wrong.** The in-degree ≤ 1 test is exactly right: it admits precisely the graphs where each node has one path into it, so post-order sum ≡ dedup walk. I could not construct a counter-example and I now believe none exists. |
| 3 | Do the active-path guards distinguish a real cycle from a legitimate diamond? | Traced the invariant (`visiting` = exactly the set of nodes with a pending `(n, True)` marker = the active path), then confirmed by execution: **335 of 400** generated DAGs contain a node with >1 parent, and the explicit diamond renders with no notice. | **No false refusal on any diamond or DAG.** `visible_rows` on `a→b, a→c, b→d, c→d` = `[('a',0),('b',1),('d',2),('c',1),('d',2)]` — the shipped duplicate-emission preserved exactly. |
| 4 | Does `_depth`'s seen-set terminate on every cyclic parent chain, and agree on acyclic ones? | 3,000 random graphs in which **every** node has a parent (so a cycle is guaranteed), driving `_depth` on every node plus `_max_depth` and `_tree_lines`. Acyclic agreement covered by (1). | **All terminated, none propagated.** Both `_depth` and `_parent_index` follow first-parent-in-edge-order, so the memoised `_max_depth` and the shipped `parent_of` chain cannot diverge. |
| 5 | Are any assertions unable to fail? | Mutated the cap in a **copy** and ran the full suite. | **F1 — one is, and it is the one whose docstring claims otherwise.** |
| 6 | Anything the AST probe could not see — an already-a-loop traversal that hangs or is quadratic? | Read both files method by method against the author's own table, then measured. | The author found the real one (`_depth`'s unguarded `while True`) by the same method and reported it honestly. I add **F9** (`_tree_text`'s quadratic indent) and the `subtree_missing` cost inversion inside **F2**. |
| 7 | C-17 / markup and control-byte injection | Executed a title carrying `ESC[31m` and an OSC-52 clipboard write through both surfaces. | **F4 — the rail neutralises it, the factory does not.** |
| 8 | Does the suite actually pass? | `pytest -q -p no:randomly -o addopts=` on the working tree. | **356 passed in 59.98 s.** Matches the packet's 356 and its ~63 s. |
| 9 | Is the cyclic-graph guard reachable at all today? | `OutlineRail(` appears once in `mapper/app.py` (line 1126, MapScreen); `_ImportPreviewScreen.compose` yields no rail; increment 1 made `MapStore.load` refuse cycles. | Confirms the packet's §7.2: the guards — **and F2's false refusal** — are unreachable through the shipped surface today. This is what holds F2 at MEDIUM. |

### Accepted without independent re-execution

- **The mutation battery's 14 arms, 72 RED verdicts, and the sha256 restore proofs.** I did
  not re-run the battery. I did read the transcript for arm N7 and found its mutation
  (`cap → 1`) does not pin what its row claims — see **F1**. I did **not** audit the other
  13 arms the same way, and on this evidence I would not assume they are all tight.
- **Every wall-clock number in §4** (0.09 s, 1.56 s, 5.616 s, the cubic growth table, the
  RSS readings). Not reproduced; they are plausible and the count-based pins
  (`MAX_EDGE_LIST_SCANS`) are the load-bearing ones and I read those.
- **The `MASTER_*_DIGEST` constants** — I did not regenerate them from `master` sources.
  Pending item 6 (no checked-in regeneration tool) remains the right carry-forward.
- **The `TC-R32` subprocess harness** (RSS watchdog, wall clock, verdict parsing). Read, not
  re-executed under fault injection. Its own positive control node exists and I accept it.
- **Increments 1 and 2's uncommitted work** in `model.py`, `mermaid.py`, `store.py`,
  `app.py`, `views/*` — read for context, not reviewed; gated separately.
- **`pyproject.toml`.** The marker registration is correct and the comment states the CI
  obligation. I have no finding, but I will restate the packet's own Risk 7 as the sharpest
  operational risk in this increment: **`addopts = "-m 'not slow'"` means the default gate no
  longer runs `AT-R16`.** Until a `-m slow` CI lane exists, `HLR-R02`'s acceptance is
  deselected by default. That is a batch-level item, not a reason to block this increment.

---

## Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Diff read in full | ✓ | `git diff d6b60e6 -- mapper/widgets/rail.py mapper/screens/factory.py pyproject.toml`; `rail.py:1-269` and `factory.py:1-270` read whole; `tests/test_repair_depth.py` read at `498-540`, `836-1278`, `1364-1440`, `1540-1599`, structure outlined for the rest |
| Correctness pass (edge / None / error paths) | ✓ | 46,548 differential comparisons, 0 mismatches; 6,480 exhaustive memo checks, 0 wrong; empty graph, single node, self-loop, dangling child, duplicate edge, multi-root forest all driven |
| Simplicity pass (no premature abstraction) | ✓ | No finding. `_child_index` / `_parent_index` / `_missing_walk` / `_missing_map` / `_body` / `_tree_text` each earn their existence — the split into raising and never-propagating halves is the shape the requirement asks for, not speculative generality |
| Reuse / duplication checked | ✗ | **F4** — `factory.py:246` re-solves a problem `darkside.plain` already owns, in the same increment where the sibling file uses it correctly. **F1** — the test duplicates `min(depth, RAIL_WIDTH)` instead of calling the code that holds it |
| Tests reviewed for intent, not just behaviour | ✗ | **F1** (cannot fail), **F3** (asserts less than its sibling and does not say so). The rest are strong: `_collapsed_configurations` is derived (C-31), `compared >=` floors guard vacuity, the decline is asserted at both polarities, `TC-R29` and `graph_touching_methods` are genuinely derived with live positive controls |
| Verdict explicit | ✓ | **PASS WITH CONDITIONS** — F1 fixed and arm N7 re-run with a cap in `[3, 9]` before the increment advances; F2, F3, F4 recommended before increment 3 builds on this code |

---

## Conditions for advancing

1. **F1 (HIGH) — fix before advancing.** Make
   `test_tc_r30_the_indent_cap_cannot_change_a_rendered_row` read `rail.py:227` through a
   call, then re-run arm N7 with `cap = 6` and require it RED. As it stands the increment's
   largest change to the shipped picture is pinned by nothing.
2. **F2 (MEDIUM) — recommended before increment 3.** Three lines; it removes a false refusal
   and makes `subtree_missing` cheaper than the code it replaced, not more expensive.
3. **F3 (MEDIUM) — declare it.** No code change; one sentence in the node's docstring and in
   §1, and a composed-screen factory node carried into increment 3.
4. **F4 (MEDIUM) — one line here, plus a hand-off.** `darkside.plain` at `factory.py:246`
   (re-capture the digest deliberately); the other eleven `escape(...)` sites in that file go
   to `security-reviewer` as a C-17 sweep, not to this increment.
5. **F5–F9 (LOW)** — take or leave; F5 and F7 are free.

**Not my lane, handed off:** `security-reviewer` — `factory.py`'s remaining eleven
`escape(...)` sites on file-derived text (C-17). `qa-reviewer` — Risk 7: the default lane no
longer runs `AT-R16`, and there is no `-m slow` CI lane.

**Nothing in this review was written into the working tree.** The only file created is this
one. The cap counterfactual ran in a `tar`-cloned copy under the session scratchpad;
`grep -c "min(depth, RAIL_WIDTH)" mapper/widgets/rail.py` still returns `1`.
