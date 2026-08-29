# Security Review — Inc-4a (`feat/ui-next-batch-02`, entry `5f4816c`, working tree)

**Verdict: BLOCK.** One HIGH (availability / operator-visible hang), introduced by this
increment, on a green suite (813 passed). The content-sink axis — the one this batch's
history predicts — came back **clean**.

## Scope reviewed

`git diff HEAD -- mapper/` plus staged `git diff --cached`. Four source files:
`mapper/search.py`, `mapper/views/state.py`, `mapper/views/layered.py`, `mapper/app.py`.
`.dev-flow/**` excluded as instructed. Reviewed against the six axes in the brief.

All evidence below is executed command output. Hostile fixtures were built in
`tempfile.mkdtemp` workspaces (`C:\Users\jjgh8\AppData\Local\Temp\secrev4a_*`); every
hostile code point was constructed with `chr()` and never spelled. **No tracked file was
mutated:** `git status --porcelain` is byte-identical before and after all probes, and
`git diff --quiet -- fixtures/` exits 0.

---

## Findings

### F1 — `SearchIndex.query` is quadratic and runs 4× per frame: an operator-visible hang [Severity: HIGH — INTRODUCED]

- **What:** The new whole-graph resolution is O(N·E) + O(N²) and is re-run from scratch
  three-to-four times on every `refresh_canvas`. There is no memo, no bound, and no
  short-circuit. On a large-but-legal graph a single navigation keypress freezes the UI
  for tens of seconds. The project's own standard — *a hang is worse than a crash* — is
  the one this violates.

- **Where:** three independent, compounding causes:
  - `mapper/search.py:60` — `graph.children_of(nid)` inside the walk. `children_of`
    (`mapper/model.py:149`) is a full linear scan of `graph.edges`, called once per node
    → **O(N·E)**.
  - `mapper/search.py:93` — `nid not in set(walked)` inside a comprehension. `set(walked)`
    is rebuilt for **every candidate** → **O(N²)** on its own.
  - `mapper/app.py:1724` + `mapper/app.py:1849` — `_count_line` and `_view_state` each
    reach `_search_order` (`mapper/app.py:1829`), and `refresh_canvas` calls `_view_state`
    twice plus `_pagination_text` once. Measured: **4 calls per frame** with a query
    active, 3 with a blank one.

- **Why it matters — measured, not reasoned:**

```
P1.4 SCALING of tree_order alone          P2.2 the `set(walked)` rebuild
   N=  250    1.35 ms                        N=  500  shipped   2.78 ms  hoisted 0.026 ms  x108
   N=  500    5.44 ms  x4.03                 N= 1000  shipped   8.81 ms  hoisted 0.068 ms  x130
   N= 1000   25.42 ms  x4.68                 N= 2000  shipped  45.40 ms  hoisted 0.202 ms  x225
   N= 2000  103.06 ms  x4.05
```

  x4 per doubling of N in both — textbook quadratic. Driven through the **real app**
  (`MapperApp.run_test`), one `refresh_canvas` — which is exactly one `j`/`k`/`h`/`l`
  press, since `action_next_sibling` / `prev_sibling` / `child` / `parent` all end in
  `self.refresh_canvas()` at `mapper/app.py:2090-2113`:

```
query ACTIVE:
  N=   301  ONE refresh_canvas: _search_order x4   search-walk     13.5 ms of     94.8 ms wall (14%)
  N=  1201  ONE refresh_canvas: _search_order x4   search-walk    186.1 ms of    369.4 ms wall (50%)
  N=  3001  ONE refresh_canvas: _search_order x4   search-walk   1229.9 ms of   1754.4 ms wall (70%)
  N=  6001  ONE refresh_canvas: _search_order x4   search-walk   6531.1 ms of   8143.8 ms wall (80%)
  N= 12002  ONE refresh_canvas: _search_order x4   search-walk  25795.0 ms of  30601.7 ms wall (84%)
```

  **30.6 seconds of frozen UI for one arrow key.** The search walk is 84% of it.

- **Recommendation (minimal, measured):** build the child index once per walk and hoist
  the `seen` set. Executed side by side, identical output on every graph tested:

```
   N=  3001  shipped   0.297s   fixed 0.006s   x 54   identical result: True
   N=  6001  shipped   1.486s   fixed 0.007s   x199   identical result: True
   N= 12002  shipped   5.974s   fixed 0.024s   x244   identical result: True
```

  ```python
  def tree_order(graph: Graph) -> list[str]:
      out: list[str] = []
      if graph.root_id is None:
          return out
      kids: dict[str, list[str]] = {}          # ONE O(E) pass, not N of them
      for e in graph.edges:
          kids.setdefault(e.parent_id, []).append(e.child_id)
      seen: set[str] = set()
      stack = [graph.root_id]
      while stack:
          nid = stack.pop()
          if nid in seen or nid not in graph.nodes:
              continue
          seen.add(nid)
          out.append(nid)
          for cid in reversed(kids.get(nid, [])):
              if cid not in seen:
                  stack.append(cid)
      return out
  ```
  and at `mapper/search.py:93`, hoist the set out of the comprehension:
  ```python
      walked = [nid for nid in tree_order(self.graph) if nid in found]
      seen = set(walked)
      return walked + [nid for nid in self.graph.nodes
                       if nid in found and nid not in seen]
  ```
  Separately, memoise `_search_order` per `(graph identity, query_text)` for the frame so
  one refresh resolves once rather than four times. Both fixes are needed: the algorithmic
  one removes the quadratic, the memo removes the 4×.

---

### F1a — the blank-query guard does not short-circuit the walk [Severity: HIGH — INTRODUCED, same fix family as F1]

- **What:** `LLR-N07.3.3` is correctly enforced *for the result* but not *for the work*.
  `hits()` returns `frozenset()` in 4 microseconds, then `query()` runs the full O(N·E)
  walk anyway against an empty `found`.

- **Where:** `mapper/search.py:91-93` — `found = self.hits(q)` is followed
  unconditionally by `walked = [nid for nid in tree_order(self.graph) if nid in found]`.

- **Why it matters:** an operator who has **never searched** pays the full cost on every
  navigation key. This is the default state of the screen, not an edge case:

```
q=''     -> hits=    0  tree_order called x1  cost  0.321s     (N=4001)
q='   '  -> hits=    0  tree_order called x1  cost  0.319s
q='x'    -> hits= 4001  tree_order called x1  cost  0.518s
hits("") = 0  cost 0.000004s   (the guard IS cheap — it just isn't reached in time)

query BLANK, through the real app:
  N= 12002  ONE refresh_canvas: _search_order x3  search-walk 10701.1 ms of 15232.6 ms wall (70%)
```

- **Recommendation:** return early in `query`, before the walk.
  ```python
      found = self.hits(q)
      if not found:
          return []
  ```

---

### F1b — the walk ignores `MAX_RENDER_NODES`: the app burns 26 s to paint "I will not draw this" [Severity: HIGH — INTRODUCED, aggravator of F1]

- **What:** `MAX_RENDER_NODES = 12000` (`mapper/views/layered.py:18`) makes the renderer
  refuse to draw past the bound. The new search walk honours no such bound, so above the
  limit the frame's entire cost *is* the search.

- **Where:** `mapper/app.py:1829` — `SearchIndex(self.graph).query(...)` is unconditioned
  on graph size.

- **Why it matters:** this is `S-15`'s shape ("the bound limits the render COUNT, not the
  WORK") escalated from a recorded observation to a hang. Measured:

```
MAX_RENDER_NODES = 12000
N=12002  over bound=True   ONE SearchIndex.query: 5.938 s   ONE render(): 0.000 s
   renderer painted: 'mapa de 12002 nodos: supera el límite de 12000 nodos. Se omitió el dibujo...'
N=15001  over bound=True   ONE SearchIndex.query: 9.425 s   ONE render(): 0.001 s
```

  The renderer costs **zero** and the search costs **6-9 seconds per call, ×4 per frame**,
  on a graph the app has already declared it will not draw. At `HEAD` this path was free:
  `_view_state` passed `query=self.query_text` (a string) and `render()` returned the
  overflow declaration before ever evaluating `_matches`. The regression is clean.

- **Recommendation:** short-circuit above the bound at the app seam, so the search obeys
  the same declared ceiling the renderer does:
  ```python
  def _search_order(self) -> list[str]:
      if len(self.graph.nodes) > MAX_RENDER_NODES:
          return []          # the map paints no tree; the count declares nothing
      return SearchIndex(self.graph).query(self.query_text)
  ```
  If a count above the bound is wanted instead, take it from `SearchIndex.hits()` alone
  (linear, no walk) and skip the ordering.

---

### F2 — `hits.index()` scans the list twice per frame [Severity: LOW — INTRODUCED]

- **What:** `mapper/app.py:1727` — `hits.index(self.nav.cursor) + 1 if self.nav.cursor in hits else 0`
  performs two O(N) list scans.
- **Why it matters:** dwarfed by F1 and harmless once F1 is fixed; recorded so it is not
  reintroduced as the "obvious" shape when the next-match walk lands.
- **Recommendation:** optional. A dict built alongside the ordered list, or accept it —
  it is linear, not quadratic.

---

## What came back CLEAN (probed, not assumed)

These are the axes this batch's history (`B-47`, `SEC-F2`, `F-A`, `C-17`) predicts, and
the increment is disciplined on every one of them.

**No new sink for file-derived text.** A hostile fixture was built through the real
`MapStore.load` path with a title carrying markup brackets, an ANSI escape sequence,
U+202E, U+200B and BEL; a `meta` carrying a fake credential and a Windows user path; and
an attachment path pointing at an SSH key. Both new painted strings interpolate only
integers and a module constant:

```
f-strings inside _count_line: ['f"0 {SEARCH_COUNT_SUBJECT}  "', 'f"{at}/{len(hits)} {SEARCH_COUNT_SUBJECT}  "']
   -> interpolated values are: ['SEARCH_COUNT_SUBJECT', 'at', 'len(hits)', 'SEARCH_COUNT_SUBJECT']
   painted count line   : '0/5 coincidencias en el mapa  '
   contains U+202E? False   contains U+200B? False   contains ESC U+001B? False   contains BEL U+0007? False
   contains 'INYECTADO'? False   contains a node id? False   contains 'jjgh8'? False   contains 'sk-live'? False
   markup spans on it   : []
```
The fold-pill tail is `mapper/views/layered.py:599` → `tail = f" {n_hits}" if n_hits else ""`,
an integer. Both reach the surface through `Text.assemble` / `Text(...)`, which do not
parse markup — confirmed on the canvas, where injected markup survives as literal text
rather than being interpreted: `raw markup left unparsed? '[bold red]' present as literal: True`.
`darkside.plain` is correctly *not* needed here, because no file-derived value reaches
either string.

**Not the `F-A` class.** The diff's only interpolated widget selector is
`query_one(f"#{COUNT_REGION_ID}", ...)` at `mapper/app.py:1579` and `:1922`.
`COUNT_REGION_ID = "map-pagination"` is a module constant, not file-derived. Replacing a
literal with a constant of the same value is a naming change, not a new sink. No node id,
schema key, or ficha value reaches a widget id or CSS selector anywhere in this diff.

**`ViewState.hits` crosses its new boundary safely.** Node ids now travel
`search → app → ViewState → renderer → export`. In the renderer they are consumed only as
membership tests that select a *style* (`mapper/views/layered.py:528`, `:598`) — never as
text. The SVG export (`action_export_svg` → `save_svg`) was driven on the hostile graph
with a populated `hits` set: `SVG contains U+202E? False / U+200B? False / ESC? False /
BEL? False / 'jjgh8'? False / 'sk-live'? False / 'id_rsa'? False`. `frozenset` (not `set`)
correctly prevents a renderer mutating the caller's set mid-draw.

**No hang, no unbounded recursion in the walk itself.** The walk is iterative with a
`seen` guard and terminates on every hostile graph shape tried — a 4-cycle, a self-loop,
a root not present in `nodes`, and a disconnected second component:
```
P1.1 cyclic tree_order -> ['a','b','c','d']  in 0.009 ms (TERMINATED)
P1.2 self-loop tree_order -> ['r'] (TERMINATED)
P1.3 depth-20000 chain -> len=20000 (NO RecursionError)
P1.9 root_id not in nodes -> tree_order: []  query: ['a']
```
It is *slow*, not *non-terminating* — F1 is a latency defect, not a liveness one. The
`len(query(q)) == len(hits(q))` invariant the docstring claims holds on a
cyclic-plus-disconnected graph (verified P1.8).

**The blank-query rule is enforced at the owner, as `LLR-N07.3.3` requires.** Verified
against eight blank forms including NBSP (U+00A0), U+2028 and the ideographic space
U+3000, and contrasted with the raw `Graph.search_hits` it wraps:
```
q=''    hits=0 query=0  raw search_hits=6      <- the shipped match-everything, correctly stopped
q=' '   hits=0 query=0  raw search_hits=6
q='\xa0' hits=0 query=0  raw search_hits=0
```
The guard sits in `SearchIndex.hits` (`mapper/search.py:76`), which `query` routes
through — one owner, not one caller. (The *work* it fails to skip is F1a; the *result* is
correct.)

**The query reaches no sink.** `_count_line` touches `self.query_text` exactly once, as
`if not self.query_text.strip():` — a predicate, never painted. `Graph.search_hits` uses
`q in hay`, a substring test with no regex, so there is no catastrophic-backtracking
surface; a long query is linear.

**Removal completeness: clean.** `ViewState.query` has no surviving reader anywhere.
Grepped `mapper/` and `tests/` for direct access, `dataclasses.fields`, `asdict`,
`__dict__` and `getattr`; the only residual occurrences are prose in docstrings, and
unrelated `query` parameters in `keymap.palette_items` and `screens/palette.py`. All three
migrated readers are accounted for: the renderer (`mapper/views/layered.py:485`), the
writer (`mapper/app.py:1849`), the test (`tests/test_app.py:453`). The export site at
`mapper/app.py:2288` shares `_view_state` via `replace(...)`, so it migrated for free.
Full suite: **813 passed, 17 deselected, 3 xfailed**.

**No new secret or path leak.** Every added line in `mapper/` mentioning path/toast/
notify/log/print is comment prose; all five added f-strings interpolate constants or
integers. This diff does **not** add a second instance of the `store.py` username
path-leak. *(Pre-existing and untouched, recorded not fixed here:
`mapper/app.py:2296` — `self._event_toast("exportado", str(path))` paints an absolute
workspace path to the screen. Same family as the `store.py` defect routed to Inc-REPAIR;
outside this diff.)*

---

## Pre-existing, touched but not owned by this increment

- **`F-A`** (HIGH, open, Inc-REPAIR) — schema key into a widget id. This diff does not
  touch that site and does not add a sibling. Still blocks the batch on its own ticket.
- **`S-15`** — `MAX_RENDER_NODES` bounds count, not work. Inc-4a does not create this
  observation, but F1b escalates its consequence from "some wasted work" to "26-second
  frame". Fixing F1b closes the new escalation, not the underlying `S-15`.
- **Username path leak in the export toast** (`mapper/app.py:2296`) — unchanged here.

## What I could not determine

- **Real-world graph sizes.** I have no measurement of the largest `.mmd` an operator
  actually opens. If every real map is under ~500 nodes, F1's practical impact is ~14 ms
  per frame and the severity argument rests on `MAX_RENDER_NODES = 12000` being the
  *declared* supported ceiling — the app promises to handle 12000, and at 12000 it does
  not. I rated on the declared ceiling, not on an assumed workload. If Javier wants to
  re-scope the ceiling instead, that is a requirements decision, not a review one.
- **`pilot.press("j")` did not route to `MapScreen` in my harness** (fired
  `_search_order` zero times). I did not chase why. I substituted a direct
  `refresh_canvas()` call, which is the exact mechanism every navigation action ends in
  (`mapper/app.py:2090-2113`, read and cited), so the measurement stands — but it is a
  reconstruction of the keypath, not the keypath itself.

---

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — F1, F1a, F1b, F2 above.
- [x] Each finding has a severity rating — HIGH ×3 (one family), LOW ×1.
- [x] No secret values appear in this output — the hostile fixture's planted credential is
      referenced by the substring searched for (`'sk-live'`), never by value; it was
      synthetic and lived only in `mkdtemp`.
- [x] Verdict is explicit — **BLOCK**, below.
- [x] New tool/integration scope and blast radius — **N/A**: this diff adds no MCP,
      Composio, n8n connector, network call, subprocess, or new dependency.
      `mapper/search.py` imports only `mapper.model`; it correctly imports no Textual and
      no `views`, so the `views → search` edge is not created.
- [x] No tracked file mutated — `git status --porcelain` byte-identical pre/post
      (md5 `8b6853c25f7287660d1d5904a3ad1c66`); `git diff --quiet -- fixtures/` exit 0.
      All fixtures built in `tempfile.mkdtemp`.

## Verdict

- [ ] OK to ship
- [ ] OK to ship with the listed mitigations applied first
- [x] **Block — must fix HIGH findings before ship**

**BLOCK.** F1 / F1a / F1b must be fixed before merge. They are one defect family with one
small fix: build the child index once, hoist the `seen` set, return early on an empty hit
set, and bound the walk by `MAX_RENDER_NODES`. Add a memo so one frame resolves once
instead of four times. This is a contained change to `mapper/search.py:37-93` and
`mapper/app.py:1829`; it is `software-dev`'s to apply, not mine.

The design of this increment is sound and its content discipline is genuinely good — the
single-owner refactor is correct, the resolved-set boundary is the right shape, and every
sink this batch's history warned about came back clean under a hostile fixture. What ships
alongside it is a quadratic in the hot path that the suite cannot see, on a green
813-test run. That is precisely the failure mode this batch is spending its budget to
stop, which is why it blocks rather than being waved through as a performance nit.
