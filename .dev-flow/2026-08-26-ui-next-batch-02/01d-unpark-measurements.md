# 01d · Un-park measurements — QA lane

**Batch:** `2026-08-26-ui-next-batch-02` · **Base ref:** `d877784` · **Date:** 2026-08-27
**Lane:** QA measurement (discharging `02a-qa-acceptance-review.md` §3 blockers)
**Toolchain:** Python 3.12.7 · Textual 8.2.8 · Windows · `PYTHONUTF8=1`

## 0 · BLUF

Four measurements were owed. All four are executed below with transcripts. **Three of the four
contradict the parked review's own remedy**, and in each case the executed result governs:

| # | Blocker | Verdict | The contradiction |
|---|---|---|---|
| **M-U1** | `QA-B-01` | **Discharged, remedy CORRECTED** | The two-predicate replacement oracle the review prescribes is **missed by the pure-deletion mutation**. A third arm (converse containment) is mandatory. The review's suggested `≥ 8`-character prefix false-fails **69 times**; the only discriminating prefix length is **exactly 2**, a one-value window. |
| **M-U2** | `QA-B-05` | **Discharged, review CONFIRMED** | Synthetic fixture built, `naive_sum = 6 ≠ 4 = painted_sum`. Shipped fixture confirmed unfalsifiable by **exhaustive enumeration of all 7 fold configurations**, not just by the nestable-candidate argument. |
| **M-U3** | `QA-B-06` | **Discharged, caveat REFINED** | Pre-state on disk **0**; positive control recovers **12 of 12**. The review's claim that a substring oracle "returns False even for correct content" is **conditionally** true — it depends on per-cell style variation. Measured both arms. |
| **M-U4** | `QA-B-09` | **Discharged, the parked glyph set is WRONG** | The hand-listed set `· ◆ ● ─ │ ┌ ┐ ┬ ┼ ▐` is **False on a correct implementation** (7 of its 10 members are Layered glyphs radial never paints) and **does not redden the precedence mutation**. The measured radial set is 19 glyphs, and the 3 the mutation destroys are all ASCII letters. |
| **QA-B-03** | census | **Confirmed, and refined** | 47 declared · 3 pure padding · **44 real** — derived, not typed. New tier found: only **39** have a requirement `Acceptance:` line. |

**Scope honoured:** exactly one file created (this one). Nothing under `mapper/`, `tests/`,
`prototypes/` or any other `.dev-flow/` file was created, modified, staged or deleted. Nothing was
`git add`-ed or committed. All probes and fixtures live in the session scratchpad. Four scope items
marked `SATISFIED-EXTERNALLY` in `PLAN.md` §12.5 (S-7, S-8, S-01, S-02) were **not** re-measured.

**Suite:** not run. The orchestrator owns the complete run; baseline for reference is `429 passed`.

---

## 1 · Probe harness (shared)

All probes import the production modules directly and are pure readers.

```python
# common.py  (scratchpad)
REPO = Path(r"C:\Users\jjgh8\Github\mapper")
sys.path.insert(0, str(REPO))
from mapper.model import Edge, Ficha, Graph, Node
from mapper.store import MapStore
from mapper.views.layered import _child_index, _clip, _fit, _tree_layout

BRAILLE_LO, BRAILLE_HI = 0x2800, 0x28FF

def braille_count(s: str) -> int:
    return sum(1 for ch in s if BRAILLE_LO <= ord(ch) <= BRAILLE_HI)

def load_legacy(tmp):                      # the 8-node shipped fixture
    ws = tmp / "legacy_ws"; ws.mkdir(parents=True, exist_ok=True)
    for name in ("legacy.mmd", "legacy_nodos.yml"):
        (ws / name).write_text((REPO / "fixtures" / name).read_text(encoding="utf-8"),
                               encoding="utf-8")
    return MapStore(ws).load("legacy")

def make_seed(tmp, map_id="nomina"):       # the 3-node seed map
    ws = tmp / f"seed_ws_{map_id}"; ws.mkdir(parents=True, exist_ok=True)
    return MapStore(ws).create_seed(map_id)
```

### 1.1 The declared painted id set — reference implementation

`HLR-N06.3` needs an id set the renderer *returns*. `LayeredRenderer.render` does not return one
today, so the probe carries a reference implementation that replicates the renderer's own geometry
(`layered.py:141-190`) exactly. **It is cross-checked against the real painted text** (§2.2) so it
is not an independent guess.

```python
def declared_painted(graph, w, h, with_header=True):
    index = _child_index(graph)
    all_ids = list(graph.nodes)
    n_leaves = sum(1 for nid in all_ids if not index.get(nid))
    gap = 3
    widest = max(max(len(graph.nodes[n].ficha.title) + 3,
                     len(graph.nodes[n].ficha.meta) + 2) for n in all_ids)
    card_w = min(26, max(14, widest))
    avail = w - 2
    if n_leaves * (card_w + gap) - gap > avail:
        card_w = max(9, (avail - (n_leaves - 1) * gap) // n_leaves)
    legacy = bool(graph.schema)
    card_h, edge_h = (3 if legacy else 2), 2
    level_h = card_h + edge_h
    pos = _tree_layout(graph, card_w, gap)
    depth_max = max(lv for _, lv in pos.values()) if pos else 0
    body_h = min(max((depth_max + 1) * card_h + depth_max * edge_h, h - 5), max(h, 1))
    hdr = 1 if with_header else 0
    title_w = max(1, card_w - 3)
    painted, images = set(), {}
    for nid in all_ids:
        cx_raw, lv = pos[nid]
        cx = max(0, cx_raw - card_w // 2)
        y = lv * level_h
        if not (0 <= y < body_h) or hdr + y >= h:
            continue
        img = _clip(graph.nodes[nid].ficha.title, title_w)   # the "▐ " prefix takes cx, cx+1
        vis = "".join(ch for j, ch in enumerate(img) if 0 <= cx + 2 + j < avail)
        if vis.strip():
            painted.add(nid); images[nid] = vis
    return {"painted": painted, "images": images, "card_w": card_w,
            "title_w": title_w, "avail": avail, "body_h": body_h}
```

---

## 2 · M-U1 — discharging `QA-B-01`: the overflow-declaration oracle

### 2.1 BLUF

The parked census reproduces on the current tree, with one refinement. But the measurement's most
important result is **not** in the census: **the replacement oracle the review prescribes — "return
the painted id set, then assert every declared id has a visible trace" — is green on the pure
deletion mutation.** It certifies a renderer that declares *nothing* painted, which is exactly the
shipped pre-state failure. A third predicate is required and is specified in §2.6.

### 2.2 The parked census, re-executed at `d877784`

`python p1_census.py` — non-overflowing sizes, restated in the "declared hidden" frame the
requirement uses (`declared = N − traced`; **truth = 0 hidden at every one of these sizes**):

```
==============================================================================
PART 1 - the PARKED oracle re-executed at d877784
==============================================================================
map              w x h        N  id-cs  id-ci  title-full  truth
legacy(8 nodes)  60x30        8      0      7           4      8
legacy(8 nodes)  80x30        8      0      8           7      8
legacy(8 nodes)  100x30       8      0      8           8      8
legacy(8 nodes)  140x45       8      0      8           8      8
seed(3 nodes)    60x30        3      0      0           3      3
seed(3 nodes)    80x30        3      0      0           3      3
seed(3 nodes)    100x30       3      0      0           3      3
seed(3 nodes)    140x45       3      0      0           3      3

REPLICATION POSITIVE CONTROL - every id my declared_painted() claims painted
must have its _clip image present in the real painted text:
  mismatches: 0  (0 => the replication tracks the real renderer)
```

(`id-cs` / `id-ci` / `title-full` are counts **traceable**; `truth` is `|declared painted set|`.)

| Reading | Parked claim | Executed at `d877784` | Verdict |
|---|---|---|---|
| id, case-sensitive | 0 of 8 | **0 of 8 at every width** → declares **8 hidden when 0 are** | **Confirmed** |
| id, case-insensitive | 8 of 8 "by fixture luck" | **8 of 8 at w ≥ 80; 7 of 8 at w = 60** | **Confirmed and refined** — the luck also runs out under truncation |
| id, on the seed map | 0 of 3 | **0 of 3 at every width** → declares **3 hidden when 0 are** | **Confirmed** |
| full-title, `_fit` truncation | "declares 4 hidden at w=60 when 0 are" | **4 of 8 traced at w=60 → declares exactly 4 hidden, truth 0** | **Confirmed exactly** |

**The replication positive control matters (C-55):** 0 mismatches across 8 map×width cases means the
reference `declared_painted` is not producing a plausible fiction — every id it calls painted really
does have its `_clip` image in the real painted text.

### 2.3 A vacuity the parked review did not catch: neither fixture overflows at those sizes

The first run of the census was **vacuous in its negative arm**: at all four sizes above, `truth`
equals `N` — every node is painted, so no oracle can be caught declaring a *painted* node hidden.
Any prefix-discrimination number derived there would be meaningless. Sweeping 7 widths × 8 heights:

```
====================================================================================
SWEEP - which (w,h) actually leave nodes UNPAINTED?  truth = |declared painted set|
====================================================================================

legacy: 31 of 56 sizes hide at least one node
   w= 30 h= 6  hidden=7  ['alm', 'cont', 'fin', 'inv', 'nom', 'pres', 'rrhh']
   w= 30 h= 8  hidden=5  ['alm', 'cont', 'inv', 'nom', 'pres']
   w= 30 h=10  hidden=5  ['alm', 'cont', 'inv', 'nom', 'pres']
   w= 30 h=12  hidden=2  ['alm', 'inv']
   w= 30 h=16  hidden=2  ['alm', 'inv']
   ...
   w= 40 h=12  hidden=2  ['alm', 'inv']

seed: 0 of 56 sizes hide at least one node
```

**The seed map cannot be made to overflow at any of 56 sizes.** This settles §2.7.

### 2.4 The census on the overflowing sizes — the only ones where an oracle can be wrong

```
====================================================================================
PART 1 re-run ON THE OVERFLOWING SIZES
====================================================================================
map      w x h      N truth true_hidden id-cs decl id-ci decl title-full decl
legacy   30x6       8     1           7          8          8               8
legacy   30x8       8     3           5          8          7               8
legacy   30x12      8     6           2          8          5               8
legacy   40x8       8     3           5          8          6               7
legacy   40x12      8     6           2          8          3               6
legacy   50x8       8     4           4          8          5               7
legacy   60x8       8     4           4          8          5               6
legacy   80x8       8     4           4          8          4               5
legacy  100x8       8     4           4          8          4               4
legacy  140x8       8     4           4          8          4               4
```

(`* decl` = the number of hidden nodes that oracle would declare; compare against `true_hidden`.)

**Every reading is wrong on at least some overflowing size.** The case-sensitive id oracle declares
`8` unconditionally — it is a constant, not a measurement. The case-insensitive oracle is right at
`100x8` and `140x8` and wrong at all nine other sizes. The full-title oracle is right at `100x8` and
`140x8` only.

### 2.5 The truncation-tolerant trace predicate — measured, not guessed

Two candidates were swept over the 31 overflowing cases (negative arm size = **129 unpainted
node-observations**).

**P-A — the title's own `_clip` image at that width:**

```
P-A (_clip image) re-run on the overflowing sizes:
  across 31 overflowing cases: false-neg=0  false-pos=0
```

**P-B — a fixed prefix of length L:**

```
====================================================================================
PART 2b - prefix sweep WITH a non-empty negative arm
====================================================================================
negative arm size (unpainted node-observations across 31 cases): 129
  L= 1  false-neg=  0  false-pos= 83  ["FP legacy 30x6 cont='C'", "FP legacy 30x6 alm='A'"]
  L= 2  false-neg=  0  false-pos=  0  <== MINIMUM DISCRIMINATING L  []
  L= 3  false-neg= 12  false-pos=  0  ["FN legacy 30x8 rrhh='RRH'", ...]
  L= 4  false-neg= 12  false-pos=  0  ["FN legacy 30x8 rrhh='RRHH'", ...]
  L= 5  false-neg= 12  false-pos=  0
  L= 6  false-neg= 69  false-pos=  0  ["FN legacy 30x6 erp='Sistem'", ...]
  L= 7  false-neg= 69  false-pos=  0
  L= 8  false-neg= 69  false-pos=  0  ["FN legacy 30x6 erp='Sistema '", ...]
  L= 9  false-neg= 74  false-pos=  0
  ...
  L=18  false-neg= 77  false-pos=  0

MINIMUM PREFIX LENGTH = 2
```

**Findings, and they contradict the parked review.**

1. **The minimum discriminating prefix length is 2** — measured, over both maps and all widths.
2. **The window of validity is exactly `{2}`.** L=1 admits **83** false positives (single letters
   collide with the doc chips `◫ sin acta`, the schema letters, and the header `8 nodos`); L≥3
   produces false *negatives* because `_clip` truncates. A predicate whose only correct parameter
   value is a single integer with failure on both sides is **not a sound oracle** — it is fixture-fitted.
3. **`QA-B-02`'s prescription of "a declared prefix of ≥ 8 characters" is executed-FALSE here:
   at L=8 it false-fails 69 times.** (`QA-B-02` is itself dissolved by `PLAN.md` D16, but the same
   prefix idea is offered as the remedy shape in `QA-B-01`, so the number matters.)
4. **P-A is the sound predicate:** 0 false negatives and 0 false positives across all 31 overflowing
   cases. **Recommendation: the trace predicate is `_clip(title, card_w - 3) in painted_text`, the
   title's own `_fit` image at that width — not a prefix of any length.**

### 2.6 Falsifiability (C-40) — and the arm the review's remedy misses

Predicates under test (`p1c_mutants.py`, legacy at 40×12, where `alm` and `inv` are genuinely
off-canvas):

- **PRED-1** `parsed_indicator_numeral == len(graph.nodes) - len(declared_painted_set)`
- **PRED-2** every id in `declared_painted_set` has a truncation-tolerant trace (P-A)
- **PRED-3** *(added by this measurement)* every graph node **with** a trace is **in**
  `declared_painted_set` — the converse containment

```
BASELINE  legacy at 40x12   N=8  declared_painted=['cont', 'erp', 'fin', 'nom', 'pres', 'rrhh']
          truly off-canvas=['alm', 'inv']  indicator numeral=2
          PRED-1=True  PRED-2=True  PRED-3=True

mutation                                                              P1     P2     P3  verdict
------------------------------------------------------------------------------------------------
MUT-1 deletion: declared set = empty                                True   True  False  MISSED by P1/P2, caught only by P3
MUT-2 weakening: indicator numeral off by one                      False   True   True  CAUGHT by P1/P2
MUT-3 weakening: declared set omits ['cont','pres']                 True   True  False  MISSED by P1/P2, caught only by P3
      (both PAINTED, but reported hidden)
MUT-4 over-declare: declared set adds off-canvas 'alm'              True  False   True  CAUGHT by P1/P2
MUT-5 canvas silently loses nodes, declaration unchanged            True  False   True  CAUGHT by P1/P2

Note: True = predicate holds (green).  A mutation is CAUGHT when a predicate goes False.
```

**This is the headline result of M-U1 and it contradicts `QA-B-01`'s prescribed remedy.**

- **`MUT-1`, the pure deletion, is GREEN on both prescribed predicates.** `PRED-1` holds because
  `8 == 8 - 0`; `PRED-2` holds **vacuously** — `all()` over an empty set is `True`. A renderer that
  declares nothing painted passes the batch's headline predicate. That is *precisely* the shipped
  pre-state (the case-sensitive id oracle declares `8` unconditionally, §2.4), so the replacement
  oracle as specified would re-certify the very defect it was written to catch.
- **The structural reason:** once the indicator is computed from the renderer's declared set,
  `PRED-1` is an **identity between a value and itself**. Its only real job is catching a
  formatting/off-by-one fault between compute and paint (`MUT-2`, correctly caught). It carries no
  information about whether the declared set is *true*.
- **`MUT-3` is the requested weakening mutation** — "a value that looks like it fits". The declared
  set omits exactly the nodes a fold would hide, the indicator is recomputed consistently from that
  same set, and the arithmetic is internally coherent. Both prescribed predicates stay green while
  the indicator over-reports hidden nodes by 2.
- **`PRED-3` catches both**, and costs nothing extra: the traced set is already computed for `PRED-2`.

**Required correction to `QA-B-01`'s remedy:** the acceptance is **three** predicates, not two —
`PRED-1` (reconciliation), `PRED-2` (soundness: declared ⊆ traced), `PRED-3` (completeness:
traced ⊆ declared). Stated together, `PRED-2 ∧ PRED-3` is set **equality** between the declared
painted set and the traced set, which is the assertion the story actually needs.

### 2.7 Is the seed map a viable acceptance fixture? **No.**

`HLR-N06.3` requires the identity to hold "over at least 4 configurations: nothing hidden; hidden by
fold only; hidden by viewport only; hidden by both."

```
HLR-N06.3 requires 4 configurations: nothing hidden | fold only | viewport only | both

--- legacy: N=8 nodes-with-children=['erp', 'fin', 'inv', 'rrhh']
   nothing hidden   YES   (50, 12, ())
   fold only        YES   (50, 12, ('erp',))
   viewport only    YES   (30, 6, ())
   BOTH (overlap)   YES   (30, 6, ('erp',), ['alm','cont','fin','inv','nom','pres','rrhh'])

--- seed: N=3 nodes-with-children=['root']
   nothing hidden   YES   (30, 6, ())
   fold only        YES   (30, 6, ('root',))
   viewport only    NO  -- unreachable on this fixture
   BOTH (overlap)   NO  -- unreachable on this fixture
```

**Disposition.**

- **The seed map is NOT viable for `HLR-N06.3`.** It reaches 2 of the 4 required configurations, and
  its only foldable node is the root — folding which is a degenerate case, not the story's.
- **The `legacy` fixture IS viable for `HLR-N06.3`** — all four configurations reachable, with
  concrete `(w, h, folded)` triples derived above. `AT-015` / `AT-016` should **name `legacy` and pin
  those sizes** (`QA-B-02`'s naming lesson, re-homed by `PLAN.md` D16 §13, applies verbatim).
- **A synthetic fixture is still required — but for `LLR-N06.3.2`, not for `HLR-N06.3`.** See M-U2.

---

## 3 · M-U2 — discharging `QA-B-05`: the nested-fold negative control

### 3.1 BLUF

The fixture is built, written through `MapStore.save` and reloaded through `MapStore.load`, and the
two rules **disagree**: `naive_sum = 6`, `painted_sum = 4`. The shipped fixture is confirmed
unfalsifiable by **exhaustive enumeration of all 7 non-empty fold configurations**, which is a
stronger statement than the parked review's nestable-candidate argument.

### 3.2 The fixture

Built as a `Graph`, persisted with `MapStore.save`, then **reloaded with `MapStore.load`** so the
transcript exercises the real load path — the shape `tests/test_repair_layout.py::_tree` and
`tests/test_legacy_fixture.py` use today. It lives in a system temp dir, **not** in the repo.

```python
def build_nested(store):
    g = Graph()
    spec = [("raiz", "Plataforma", None), ("ops", "Operaciones", "raiz"),
            ("fin", "Finanzas", "raiz"), ("log", "Logistica", "ops"),
            ("comp", "Compras", "ops"), ("alm", "Almacenes", "log"),
            ("flo", "Flota", "log")]
    for nid, title, _ in spec:
        g.add_node(Node(id=nid, ficha=Ficha(title=title, meta="sintetico")))
    for nid, _, par in spec:
        if par:
            g.add_edge(Edge(par, nid))
    store.save("anidado", g)
    return store.load("anidado")

def pill_is_painted(idx, parents, folded, nid):
    """A fold pill is painted only if NO ancestor of nid is itself folded."""
    cur = parents.get(nid)
    while cur is not None:
        if cur in folded:
            return False
        cur = parents.get(cur)
    return True
```

### 3.3 Executed transcript

```
==============================================================================
THE SYNTHETIC FIXTURE - written and reloaded through MapStore
==============================================================================
files on disk: ['anidado.mmd', 'anidado_nodos.yml', 'mapper.db']

graph TD
    raiz[Plataforma] --> ops[Operaciones]
    raiz[Plataforma] --> fin[Finanzas]
    ops[Operaciones] --> log[Logistica]
    ops[Operaciones] --> comp[Compras]
    log[Logistica] --> alm[Almacenes]
    log[Logistica] --> flo[Flota]

root='raiz'  N=7  MAX DEPTH = 3  depths={'raiz': 0, 'ops': 1, 'fin': 1, 'log': 2,
                                         'comp': 2, 'alm': 3, 'flo': 3}
nestable candidates (non-root, >0 children): ['log', 'ops']
   log   descendants=2 ['alm', 'flo']
   ops   descendants=4 ['alm', 'comp', 'flo', 'log']

==============================================================================
THE TWO RULES, on FOLD = {'ops','log'}   (log is nested INSIDE folded ops)
==============================================================================
naive_sum   = 6   contributions: [('log', ['alm', 'flo']),
                                  ('ops', ['alm', 'comp', 'flo', 'log'])]
painted_sum = 4   painted pills: ['ops']
                  contributions: [('ops', ['alm', 'comp', 'flo', 'log'])]
true hidden set (union, the LLR-N06.3.1 set difference) = ['alm','comp','flo','log']
                                                          cardinality=4

naive_sum != painted_sum  ->  6 != 4  ->  True
painted_sum == |hidden union|  ->  4 == 4  ->  True
nodes the naive rule DOUBLE-COUNTS: ['alm', 'flo']  (inflation = 2)
```

**The fixture satisfies every condition the review set.**

| Condition | Required | Measured |
|---|---|---|
| depth | ≥ 3 | **3** (`raiz`→`ops`→`log`→`alm`) |
| inner folded branch nested inside another fold | yes | `log`, whose parent `ops` is folded |
| that inner branch's descendants | ≥ 2 | **2** — `alm`, `flo` |
| the two rules disagree | **mandatory** | **6 ≠ 4** |
| the correct rule equals the true hidden set | — | **4 == 4** (ties `LLR-N06.3.2` to `LLR-N06.3.1`) |

The naive rule double-counts exactly `alm` and `flo` — the two descendants of the nested fold —
inflating the declared total by 2. This is the failure mode `LLR-N06.3.2`'s acceptance-criteria note
describes, now demonstrated rather than argued.

### 3.4 Control — the shipped fixture, exhaustively

```
==============================================================================
CONTROL - the SHIPPED fixture, same two rules
==============================================================================
legacy: N=8  MAX DEPTH = 2
nestable candidates: ['fin', 'inv', 'rrhh']
nestable candidates with >0 descendants that could sit INSIDE another fold:
   []   -> count = 0
all 7 non-empty fold configurations of legacy: 0 where naive != painted
   fold=['fin']                 naive=2  painted=2  agree
   fold=['inv']                 naive=1  painted=1  agree
   fold=['rrhh']                naive=1  painted=1  agree
   fold=['fin', 'inv']          naive=3  painted=3  agree
   fold=['fin', 'rrhh']         naive=3  painted=3  agree
   fold=['inv', 'rrhh']         naive=2  painted=2  agree
   fold=['fin', 'inv', 'rrhh']  naive=4  painted=4  agree
```

**Confirms the parked review and strengthens it.** The review argued unfalsifiability from a
structural property (max depth 2, zero nestable candidates with descendants). This enumerates the
**entire fold configuration space** — all 7 non-empty subsets — and finds **0** disagreements. The
predicate is not merely likely to be unfalsifiable on `legacy`; it is provably unfalsifiable there.

The parked `M-6` arithmetic in `LLR-N06.3.2` (`{fin} → 2`; `{fin,rrhh} → 3`; `{fin,rrhh,inv} → 4`)
**reproduces exactly** — rows 1, 5 and 7 above.

**`QA-B-05` is discharged.** The transcript the review demanded as a PDR condition now exists. The
implementer should carry `anidado` into `tests/` as `LLR-N06.3.2`'s negative control; note that
`MapStore.save`/`load` round-trips it without modification, so no new fixture machinery is needed.

---

## 4 · M-U3 — discharging `QA-B-06`: the export chain must touch the written artifact (C-12)

### 4.1 BLUF

**Pre-state on disk: 0 braille glyphs. Positive control: 12 of 12 recovered.** The read-back oracle
works and its absence reading is admissible under C-55. The review's substring caveat is **confirmed
for the real case but is conditional**, and the condition is worth writing into the requirement
because a naive positive control would otherwise "prove" the substring oracle is fine.

### 4.2 (a) The pre-state / counterfactual — the real chain

```
==============================================================================
(a) PRE-STATE - the real chain: RadialRenderer -> save_svg -> disk
==============================================================================
in-memory Text braille count           : 0
ON-DISK braille count (code-point scan): 0   distinct=[]
file exists=True  size=19679 bytes  (LLR-CNV.2.1's only on-disk assertion is
                                     size > 0 -> True)

Why: Canvas.rows() never reads the dots layer.  Direct check -
   Canvas with 3 dots + 1 bg set  ->  rows() braille count = 0
   (canvas.py:67-82 reads cells and bits only)
```

**This is the PRE-STATE.** It is `0` for the reason `PLAN.md` §12.3 P-1 records: `Canvas.rows()`
(`canvas.py:67-82`) reads `self.cells` and `self.bits` and never `dots`/`bgs`, which
`radial.py:123-124` assigns onto the instance and writes at `:209`.

**And it demonstrates the C-12 defect directly:** the file is 19 679 bytes, so
`LLR-CNV.2.1`'s only on-disk assertion — `size > 0` — **passes on an artifact containing zero
braille**. The producer's artifact is never consumed.

### 4.3 (b) The positive control — mandatory under C-55

The payload is 12 braille code points constructed at runtime, never typed:
`chr(0x2800 + k) for k in (1, 3, 7, 15, 31, 63, 127, 255, 0x40, 0x80, 0xC0, 0xFF)` — i.e. U+2801,
U+2803, U+2807, U+280F, U+281F, U+283F, U+287F, U+28FF, U+2840, U+2880, U+28C0, U+28FF. (The last
two entries collide on U+28FF, which is why the distinct count below is 11 while the glyph count is
12 — the oracle counts occurrences, correctly.)

```
==============================================================================
(b) POSITIVE CONTROL - a Canvas whose CELLS already hold braille code points
==============================================================================
payload glyphs placed                  : 12
in-memory rows() braille count         : 12
ON-DISK braille count (code-point scan): 12   distinct=11
RECOVERED 12 of 12  ->  oracle is CAPABLE of a non-absence: True

==============================================================================
NEGATIVE CONTROL - a payload-free export must read back 0
==============================================================================
ON-DISK braille count: 0  size=2732 (size > 0 = True, i.e. the shipped threshold
                                     PASSES here)
```

**Which number is which:**

| Reading | Value | Role |
|---|---|---|
| `RadialRenderer` → `save_svg` → disk | **0** | **PRE-STATE / counterfactual.** What ships today. |
| braille-in-`cells` → `save_svg` → disk | **12 of 12** | **POSITIVE CONTROL.** The oracle can produce a non-absence. |
| plain-text → `save_svg` → disk | **0**, size 2 732 | **NEGATIVE CONTROL.** The oracle reports absence when content is absent, and `size > 0` still passes — the shipped threshold's vacuity, shown twice. |

The oracle:

```python
def disk_braille(path):
    raw = path.read_text(encoding="utf-8")
    pts = [ord(c) for c in raw if 0x2800 <= ord(c) <= 0x28FF]
    return len(pts), sorted({hex(p) for p in pts})
```

The review's "12 of 12" reproduces exactly. **`QA-B-06`'s required fix is confirmed cheap and
correct: assert `disk_braille(path)[0] == braille_count(on_screen_text.plain)`.**

### 4.4 The substring caveat (C-42) — confirmed for the real case, but conditional

The first run of the probe **contradicted the review**: with a uniformly-styled payload the
contiguous 12-glyph run *was* present as a substring of the SVG. Rather than report that as a
refutation, the discriminating variable was isolated and both arms measured.

```
==============================================================================
ARM 1 - uniform style on every braille cell
==============================================================================
<text> nodes: 5   contiguous 12-glyph run as SUBSTRING: True
code-point scan: 12

==============================================================================
ARM 2 - per-cell alternating style, exactly radial.py's 3-tone branch scheme
==============================================================================
<text> nodes: 16   contiguous 12-glyph run as SUBSTRING: False
code-point scan: 12
longest run that IS a substring: 1 of 12
span fragments carrying braille: ['⠁', '⠃', '⠇', '⠏', '⠟', '⠿']

==============================================================================
ARM 3 - a REAL rendered string out of the shipped radial SVG
==============================================================================
  Finanzas       in painted Text: True    as SUBSTRING of the SVG: False   <-- FALSE-NEGATIVE
  Inventarios    in painted Text: True    as SUBSTRING of the SVG: False   <-- FALSE-NEGATIVE
  Contabilidad   in painted Text: True    as SUBSTRING of the SVG: False   <-- FALSE-NEGATIVE
  mapper         in painted Text: True    as SUBSTRING of the SVG: True
```

**Verdict — the review is right about the real case and the caveat needs one added clause.** The
substring oracle's failure is **conditional on adjacent cells carrying different styles**. That is
exactly the layer-drawing case: `radial.py` assigns a per-branch tint from `_GREYS` to every dot
(`:207-209`) and a per-character style to every pill glyph (`:225-236`), so Rich emits one `<text>`
span per style run — 16 spans for 12 glyphs — and the longest recoverable substring collapses to
**1 of 12**. Three of four real rendered titles are false-negatives; `mapper` survives only because
the header paints it in a single style.

**Why the added clause matters operationally:** an implementer who writes a positive control the
easy way — one uniform style — will measure ARM 1, see `True`, and conclude the substring oracle is
acceptable. It is not. **The requirement must say: scan code points, or parse `<text>` nodes
(`re.findall(r"<text[^>]*>(.*?)</text>", raw, re.S)` recovered all 12 in the probe). Never grep for
a rendered string, and never validate a string-based read-back against a uniformly-styled fixture.**

---

## 5 · M-U4 — discharging `QA-B-09`: the braille containment arm

### 5.1 BLUF

The containment arm works and reddens the precedence mutation while `> 0` does not — the review's
core claim is **confirmed**. But **the specific glyph set the review hand-listed is wrong in both
directions and would not do the job**: it false-fails a correct implementation *and* fails to redden
the mutation. The set must be **derived at runtime**, and it must include ASCII.

### 5.2 The painted set, re-derived on the current tree

The repair batch rewrote `radial.py`, so the parked `M-1` set was re-derived rather than cited.

```
================================================================================
STEP 1 - distinct painted non-space set, RE-DERIVED on the current tree
================================================================================

legacy 8-node  RadialRenderer 80x24
  |distinct non-space| = 33
  non-ASCII subset (3): · ◆ ●
  ASCII subset (30): A C E F H I L N P R S a b c d e g i l m n o p r s t u v y z
  braille count = 0   |cv.dots| = 267  |cv.bits| = 0  |cv.cells| = 85

M-1 6-node  RadialRenderer 80x24
  |distinct non-space| = 19
  non-ASCII subset (3): · ◆ ●
  ASCII subset (16): a b d e f g i l m n o p r s t z
  braille count = 0   |cv.dots| = 195  |cv.bits| = 0  |cv.cells| = 34

PARKED CLAIM was the radial set is  ·  ◆  ●  ─  │  ┌  ┐  ┬  ┼  ▐
LayeredRenderer 80x24 non-ASCII subset: · á … ─ │ ┌ ┐ ┬ ┴ ┼ ▐ ░ ▰ ◆ ◫ ✓
```

**The parked set is a blend of two renderers.** `RadialRenderer` never calls `Canvas.wire()` —
measured `|cv.bits| = 0` — so it cannot paint a single box-drawing glyph. The seven members
`─ │ ┌ ┐ ┬ ┼ ▐` belong to `LayeredRenderer` (whose measured non-ASCII set contains all of them).
Radial's true non-ASCII contribution is exactly three glyphs: `·` (the header separator), `◆` (the
root marker and wordmark bullet) and `●` (the non-root markers).

### 5.3 The precedence mutation, executed

`cv.dots` is folded from sub-cell space into cell-space braille code points using the standard 2×4
matrix, then composed two ways:

```python
DOTBIT = {(0,0):0, (0,1):1, (0,2):2, (1,0):3, (1,1):4, (1,2):5, (0,3):6, (1,3):7}

def braille_cells(cv):
    acc = {}
    for (dx, dy) in getattr(cv, "dots", {}):
        acc[(dx // 2, dy // 4)] = acc.get((dx // 2, dy // 4), 0) | (1 << DOTBIT[(dx % 2, dy % 4)])
    return {k: chr(0x2800 + v) for k, v in acc.items() if v}

# dots_first=False -> node cards WIN (correct).  True -> braille OVERWRITES (mutation).
ch = dot if (dots_first and dot) else ((cell[0] if cell else None) or dot)
```

```
================================================================================
STEP 2 - the two composition orders, on M-1
================================================================================
PRE-change painted set  |19| = a b d e f g i l m n o p r s t z · ◆ ●
PRE-change braille count = 0

arm                                 braille  |set|   >0 ?  PRE subset POST ?
--------------------------------------------------------------------------------
CORRECT: cards win over braille          75     36   True               True
MUTANT : braille overwrites cards        90     35   True              False

glyphs LOST under the precedence mutation: f g z
glyphs LOST under the correct order      : (none)

=> AT-007's 'count > 0' is TRUE on both arms; the containment arm separates them.
```

**`AT-007`'s bound is confirmed too weak.** `count > 0` is `True` on both arms — indeed the mutant
scores *higher* (90 vs 75) because braille also occupies cells the cards used to hold. The
containment arm is `True` on the correct order and `False` on the mutant. **The review's required
fix is correct and is now demonstrated by execution.**

### 5.4 But the parked glyph set does not implement it

```
================================================================================
ADDENDUM - which containment SET actually reddens the mutation?
================================================================================
full distinct non-space (measured)   |S|=19  S<=POST_GOOD=True   S<=POST_BAD=False  reddens mutation=True
non-ASCII subset only                |S|= 3  S<=POST_GOOD=True   S<=POST_BAD=True   reddens mutation=False
the PARKED hand-listed set           |S|=10  S<=POST_GOOD=False  S<=POST_BAD=False  reddens mutation=False

parked set members radial NEVER paints: ─ │ ┌ ┐ ┬ ┼ ▐
measured members the parked set OMITS : a b d e f g i l m n o p r s t z
```

**Three findings, and the executed result governs over the parked review.**

1. **The parked hand-listed set is `False` on a correct implementation.** Seven of its ten members
   are Layered glyphs radial never paints, so `S ⊆ POST` fails on *both* arms. As written,
   `QA-B-09`'s containment arm would **false-fail the correct fix** — the same defect class as
   `QA-B-02`'s root-title oracle, reappearing in the remedy for a different blocker.
2. **A non-ASCII-only containment set is vacuous.** All three of `· ◆ ●` survive the mutation
   (markers sit at pill origins that braille happens not to overwrite in this layout), so the arm is
   green on both — it discriminates nothing.
3. **The glyphs the mutation actually destroys are `f`, `g`, `z` — all ASCII letters**, contributed
   by the M-1 pill titles `alfa`, `gama` and `raiz` respectively; each appears in exactly one title,
   so overwriting that pill removes the letter from the painted set entirely. **The containment arm
   is only falsifying if the set is the full distinct non-space set, ASCII included.**

**Required correction to `QA-B-09`:** the containment arm's set must be **derived at runtime from
the pre-change render** (`{c for c in painted_text if not c.isspace()}`), never hand-listed. This is
`C-31` — a sentinel chosen by hand discriminating nothing — which `tests/test_repair_layout.py`'s
`_rows_outside` docstring already records as a lesson learned *in this repo*, on this exact failure
mode.

### 5.5 The subject mismatch, settled by measurement

```
================================================================================
STEP 3 - the SUBJECT MISMATCH: the default map-canvas view is LayeredRenderer
================================================================================
  legacy 8-node    LayeredRenderer braille = 0   RadialRenderer braille = 0   radial |dots| = 267
  M-1 6-node       LayeredRenderer braille = 0   RadialRenderer braille = 0   radial |dots| = 195
  single node      LayeredRenderer braille = 0   RadialRenderer braille = 0   radial |dots| = 0

LayeredRenderer sets NO dots at all - grep evidence:
mapper/views/lane.py:203:        # Commit dots and head on main      <- a comment, not code
mapper/views/radial.py:123:        cv.dots = {}
mapper/views/radial.py:203:            # Draw a few dots along the line.
mapper/views/radial.py:209:            cv.dots[(int(dx * 2), int(dy * 4))] = hue
```

**It is 0 both ways, plainly.** `LayeredRenderer` — the default map-canvas view — measures **0
braille before and 0 after**, and the reason is structural, not incidental: `git grep dots -- mapper/`
returns exactly one assignment site and it is in `radial.py`. `LayeredRenderer` never populates a
`dots` layer, so **no fix to `Canvas.rows()` can raise its braille count above 0.** Fixing P-1
changes the radial view and nothing else.

**Which disposition the evidence supports.** `QA-B-09` offers two: relabel the predicate a regression
PIN on the radial renderer, or move the subject.

> **The evidence supports RELABELLING — `HLR-CNV.2` becomes a regression pin on `RadialRenderer`.**

Reasons, in order of force:

1. **Moving the subject would make the requirement unsatisfiable by the change under test.** The map
   canvas measures 0 both ways; a gate on it could only be met by *also* teaching `LayeredRenderer`
   to draw free-angle edges, which is a different feature, not in `PLAN.md`'s scope, and not what
   `LLR-CNV.1.1`'s `rows()` fix does.
2. **The story's mechanism is radial-only by construction.** The `dots` layer has one writer.
3. **`PLAN.md` D19's precedent applies:** the batch already refuses to re-derive a second definition
   of a shipped concept. Moving the subject would create a second definition of "the canvas that
   draws free-angle edges".

**Two consequences the implementer must carry.**

- **`AT-007`'s empty arm is currently vacuous.** Its `count == 0` on a single-node graph passes today
  for the wrong reason — `|cv.dots| = 0` *and* `rows()` drops dots regardless. After the P-1 fix it
  will pass for the right reason. The AT should assert the single-node graph produces
  **`|cv.dots| == 0`**, not merely that the rendered count is 0, or it cannot tell the two apart.
- **The relabelled `HLR-CNV.2` must name the renderer, the fixture and the Pilot/render size in its
  own statement** — `80 x 24`, `M-1` 6-node — because §5.2's table entry currently reads
  "count > 0, and 0 on a single node" with no subject at all.

---

## 6 · QA-B-03's census, re-derived

### 6.1 BLUF

**47 declared · 3 pure padding · 44 real.** `QA-B-03` is confirmed exactly, including the specific
three ids and the "exactly twice" occurrence profile. The census also surfaces a **third tier the
review did not separate**: only **39** of the 44 have a requirement `Acceptance:` line.

### 6.2 Method

Classified by *where* each id appears, with section 5.2 located by heading search and never by a
typed line number:

```python
ACCEPT  = re.compile(r"^\s*-\s*\*\*Acceptance:\*\*")
STORY   = re.compile(r"^\s*-\s*\*\*Acceptance tests:\*\*")
CATALOG = re.compile(r"^\s*-\s*[\u2610\u2611\u2612]\s*\*\*(empty|boundary|invalid|error|auth|concurrency)\*\*")
# section 5.2 located by: re.match(r"^#+\s*5\.2\b", line.strip())
# wrapped story lists and wrapped catalog bullets are folded into their opening bullet
```

### 6.3 Executed transcript

```
section 5.2 spans lines 2492..2591 (heading: '### 5.2 Dual-traceability')
distinct AT ids in the document: 47

[A] with a requirement '- **Acceptance:**' line  : 39  AT-001 AT-003 AT-004 AT-005 AT-006
    AT-007 AT-008 AT-010 AT-011 AT-012 AT-013 AT-014 AT-015 AT-016 AT-017 AT-018 AT-019
    AT-020 AT-021 AT-022 AT-023 AT-025 AT-026 AT-029 AT-030 AT-032 AT-033 AT-034 AT-035
    AT-036 AT-037 AT-038 AT-039 AT-041 AT-042 AT-043 AT-044 AT-046 AT-047

[B] NO Acceptance line, described only in a boundary catalog :  5  AT-002 AT-009 AT-024
                                                                    AT-031 AT-040

[C] NO Acceptance line, mentioned only in running prose      :  0

[D] PURE PADDING - only story list + section 5.2 table       :  3  AT-027 AT-028 AT-045

DERIVED COUNTS
  total declared ids                       = 47
  ids backed by a requirement Acceptance   = 39
  ids with SOME predicate text (A + B + C) = 44
  padding ids                              = 3
  total - padding                          = 44

OCCURRENCE PROFILE of the padding candidates (the review says 'exactly twice'):
  AT-027: 2 occurrences -> [(1414, 'story-list'), (2504, 'sec5.2-table')]
  AT-028: 2 occurrences -> [(1414, 'story-list'), (2504, 'sec5.2-table')]
  AT-045: 2 occurrences -> [(1886, 'story-list'), (2506, 'sec5.2-table')]

Lowest-occurrence ids overall (sanity: is anything else near-padding?):
  AT-027:  2 occ  kinds=['sec5.2-table', 'story-list']
  AT-028:  2 occ  kinds=['sec5.2-table', 'story-list']
  AT-045:  2 occ  kinds=['sec5.2-table', 'story-list']
  AT-003:  3 occ  kinds=['acceptance', 'sec5.2-table', 'story-list']
  AT-009:  3 occ  kinds=['boundary-catalog', 'sec5.2-table', 'story-list']
  AT-010:  3 occ  kinds=['acceptance', 'sec5.2-table', 'story-list']
  AT-011:  3 occ  kinds=['acceptance', 'sec5.2-table', 'story-list']
  AT-014:  3 occ  kinds=['acceptance', 'sec5.2-table', 'story-list']

§5.2's own bolded claim, located by search:
  2509: **47 acceptance tests across 8 derivable stories.** Every `AT` id above is enumerated; no dotted
```

### 6.4 Adjudication

| `QA-B-03` claim | Executed | Verdict |
|---|---|---|
| `AT-027`, `AT-028`, `AT-045` are pure padding | **Confirmed** — the padding set is exactly those three, derived not typed | **CORRECT** |
| each appears exactly twice (story list + §5.2 table) | **Confirmed** — with line numbers 1414/2504, 1414/2504, 1886/2506 | **CORRECT** |
| the real count is 44, not 47 | **Confirmed** — `47 − 3 = 44`, derived | **CORRECT** |
| `AT-002, AT-009, AT-024, AT-031, AT-040` described only in a boundary catalog | **Confirmed** — exactly those 5 | **CORRECT** |

**The corroboration holds.** `PLAN.md` §12.2 records the mechanical validator reporting **47** `AT`
ids with no node on disk — independent of this census, which derives **47** declared ids from the
document. The two agree on the declared count, and this census supplies the number the validator
cannot see: **44** are backed by predicate text.

**One refinement the review's binary split obscures.** The review reports 44 "predicates". Only
**39** are backed by a requirement `- **Acceptance:**` line. The other **5** (`AT-002`, `AT-009`,
`AT-024`, `AT-031`, `AT-040`) exist only as a clause inside a story's boundary catalog — e.g.
`AT-009` is described solely by `01r:693` (*"`AT-009` asserts `export.save_svg` still …"*), which is
also the AT that `QA-B-06` finds has no on-disk consumption. **A boundary-catalog clause is a
coverage claim, not a predicate**; it names no fixture, no size and no threshold. The batch has
three tiers, not two: **39 specified · 5 gestured-at · 3 fabricated.**

**Recommended renumber:** strike `AT-027`, `AT-028`, `AT-045`; promote the 5 catalog-only ids to
real `Acceptance:` lines or strike them too. If both, §5.2's derived count becomes **39**. Whatever
the choice, §5.2's bolded total must be *computed from the id list below it*, not maintained by
hand — `PLAN.md` R-6.

---

## 7 · Where the executed result contradicts the parked review

Recorded explicitly, per the lane's instruction that the executed result governs.

| # | Parked review says | Executed at `d877784` says | Consequence |
|---|---|---|---|
| **C-1** | `QA-B-01`: two predicates suffice — return the painted set, and assert every declared id has a visible trace | **`MUT-1` (declared set = ∅) is GREEN on both.** `PRED-1` is an identity; `PRED-2` is vacuously true over an empty set | **A third predicate (traced ⊆ declared) is mandatory.** Without it the replacement oracle re-certifies the shipped defect |
| **C-2** | `QA-B-02` (dissolved, but its remedy shape is reused in `QA-B-01`): assert "a declared prefix of ≥ 8 characters" | **L=8 false-fails 69 times.** The only discriminating length is **exactly 2**, failing on both sides | **Use the `_clip` image at that width (0 FN / 0 FP over 31 cases), not a prefix** |
| **C-3** | `QA-B-01`: the case-insensitive id reading is "8-of-8" | **8 of 8 at w ≥ 80; 7 of 8 at w = 60** | Minor; strengthens the review's "fixture luck" point — the luck also runs out under truncation |
| **C-4** | `QA-B-06`: a substring oracle over the SVG "returns False **even for correct content**" | **Conditional.** `True` under uniform styling (5 spans); `False` under per-cell styling (16 spans, longest run 1 of 12) | The requirement must forbid validating a string read-back against a **uniformly-styled** fixture, or the caveat will be "disproved" by a bad positive control |
| **C-5** | `QA-B-09`: the containment arm's set is `· ◆ ● ─ │ ┌ ┐ ┬ ┼ ▐` | **That set is `False` on BOTH arms** — 7 members are Layered glyphs radial never paints. Radial's real non-ASCII set is `· ◆ ●`, and *that* set is green on both arms | **The set must be derived at runtime and include ASCII** — the 3 glyphs the mutation destroys (`f`, `g`, `z`) are all letters |

Items **C-1** and **C-5** are the material ones: in both, the review's *prescribed remedy* — not just
the shipped code — is inadequate, and an implementer following `02a` literally would ship a green
test that certifies nothing (C-1) or a red test that blocks a correct fix (C-5).

---

## 8 · What each blocker still needs before Inc-3

| Blocker | Measurement owed | Status | Remaining action (requirement edit, not code) |
|---|---|---|---|
| `QA-B-01` | overflow oracle census + replacement + falsifiability | **DISCHARGED** | Rewrite `HLR-N06.3`'s threshold as **three** predicates (§2.6); name `legacy` and pin the four `(w, h, folded)` triples from §2.7; set the trace predicate to the `_clip` image |
| `QA-B-05` | nested-fold negative control | **DISCHARGED** | Carry `anidado` into `tests/` as `LLR-N06.3.2`'s fixture; record `6 ≠ 4` in the LLR's threshold |
| `QA-B-06` | on-disk read-back | **DISCHARGED** | Replace `LLR-CNV.2.1`'s threshold with the on-disk code-point equality; add the styled-fixture clause to the C-42 note |
| `QA-B-09` | containment arm + subject | **DISCHARGED** | Relabel `HLR-CNV.2` a regression pin on `RadialRenderer`; derive the containment set at runtime; fix `AT-007`'s empty arm to assert `|cv.dots| == 0` |
| `QA-B-03` | id census | **DISCHARGED** | Strike 3 ids; rule on the 5 catalog-only ids; make §5.2's total computed |

**Not in this lane's scope and still open:** `QA-B-04`, `QA-B-07`, `QA-B-08`, `QA-B-10`;
security condition **C-3** (S-03, the mount budget, `PLAN.md` D18); **F-14** (the V12 IFC imbalance);
and `PLAN.md` §12.4's live `load_or_notice` work.

---

## 9 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Acceptance criteria use Given/When/Then | **n/a** | This artifact is a **measurement** lane, not an acceptance-criteria lane. Its output is executed transcripts discharging PDR conditions; the AC rewrite it enables is listed in §8 and belongs to the requirements author |
| Test cases have explicit Expected, not vague "works" | ✓ | Every predicate in §2.6, §3.2, §4.3, §5.3 is a named boolean with a measured value and a stated expectation |
| Edge cases include empty, boundary, invalid, error | ✓ | empty — empty declared set (`MUT-1`, §2.6) and payload-free export (§4.3); boundary — the L-sweep's both-sided failure (§2.5), `w=30 h=6` where 7 of 8 nodes are off-canvas (§2.3); invalid — over-declared off-canvas id (`MUT-4`), sub-cell dot coords folded out of range (§5.3); error — `size > 0` passing on a zero-braille artifact (§4.2) |
| Regression checklist exists | ✓ | §5.4's containment arm **is** the regression guard; §7 lists the five parked claims that must not be re-adopted; §8 carries the open items forward |
| Exit criteria stated | ✓ | §8 — per blocker, with the remaining requirement edit named |
| No real PII / secrets | ✓ | Fixtures are the repo's own `fixtures/legacy*` (fictional names) and a synthetic `anidado`. No credentials, no `.env`, nothing read outside the repo and temp dirs |
| Test results left blank unless actually run | ✓ | Every number carries its producing script. Nothing is reported that was not executed; the full suite was **not** run and is **not** claimed |
| **Layer B (black-box):** deliverables observed through the SHIPPED surface | ✓ | §4 observes braille **on disk** through `export.save_svg` — the shipped artifact, not an in-memory `Text` — with a positive control (12 of 12) and a negative control (0). §2 observes the overflow oracle through `LayeredRenderer.render`'s returned painted text, the surface `MapScreen` composites. **Partial gap declared:** §2 and §5 read the renderer's returned `Text` rather than a Textual `Pilot` composited frame. `tests/test_repair_layout.py`'s `_rows_in` idiom is the project's painted-oracle for *screen-level* claims; the four claims measured here are **renderer-level** (`render()` is the producer under test in every case), and the renderers are pure functions of `(graph, w, h)`. **`AT-015`/`AT-016` are `test (pilot)` and must be written against `_rows_in`, not against `render().plain`** — §2's numbers pin the arithmetic, not the surface |
| **Bidirectional surface-reachability** | ✓ (with one declared gap) | Inputs exercised through the handler: map fixture (via `MapStore.load`, §3), width and height (56-point sweep, §2.3), fold set (all 7 legacy configurations exhaustively, §3.4), selection (`selected_id`, §5.2), composition order (§5.3). Outputs observed: painted text (§2), the written `.svg` on disk (§4), the distinct painted glyph set (§5), `cv.dots` / `cv.bits` / `cv.cells` cardinalities (§5.2). **Declared gap:** the *fold* input has no handler today — `render()` takes no `folded` argument — so §3's two rules are measured as set arithmetic over `(graph, folded)`, which is what `LLR-N06.3.2` specifies. It becomes surface-reachable only once Inc-3 ships the fold mechanism, and **`TC-032` must then re-run this transcript through the Pilot** |
| **No unfilled template** | ✓ | No angle-bracket placeholders, no un-substituted id stubs, no empty required rows. Every table cell carries a measured value or an explicit `n/a` with a reason |
| Falsifiability (C-40) | ✓ | §2.6 — 5 mutants × 3 predicates with per-arm verdicts, including two weakenings (`MUT-2` off-by-one, `MUT-3` omit-the-folded); §5.3 — the precedence mutation with both bounds; §5.4 — three candidate containment sets, two of which fail to discriminate |
| Absence paired with a positive control (C-55) | ✓ | §4.3 — the on-disk `0` is paired with a `12 of 12` recovery and a `0` negative control on the same oracle. §2.2 — the reference `declared_painted` is paired with a 0-mismatch replication control. §2.3 — the first census run's negative arm was **empty**, was caught, and was replaced with a 129-observation arm |
| Numbers derived, never typed (C-31) | ✓ | §6 derives 47/44/3 by classification; §5.4 derives the containment set at runtime and shows the hand-listed alternative failing; §2.5 derives L=2 by sweep |

---

## 10 · Provenance

Probes executed 2026-08-27 against a clean working tree at `d877784` (`git status --short` showed
only the pre-existing ` M .dev-flow/state.json` and the untracked batch directory; `prototypes/**`
untouched). All scripts and all synthetic fixtures were written to the session scratchpad and a
`tempfile.mkdtemp()` workspace. Commands, all run with `PYTHONUTF8=1`:

```
python p1_census.py        # §2.2  parked census + replication control
python p1b_overflow.py     # §2.3  56-size sweep, §2.4 overflow census, §2.5 L-sweep + P-A
python p1c_mutants.py      # §2.6  5 mutants x 3 predicates
python p2_nested_fold.py   # §3    synthetic fixture + exhaustive legacy control
python p3_export.py        # §4.2  pre-state, §4.3 positive + negative controls
python p3b_substring.py    # §4.4  substring oracle, 3 arms
python p4_containment.py   # §5    painted set, precedence mutation, subject mismatch
python p5_at_census.py     # §6    AT id classification
```

All braille payloads were constructed with `chr(0x2800 + k)` at runtime and are described by code
point in prose. No control byte was written into this artifact.
