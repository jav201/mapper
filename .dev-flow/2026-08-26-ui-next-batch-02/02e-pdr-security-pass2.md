# 02e · Security review — PDR pass 2, batch `2026-08-26-ui-next-batch-02`

> Lens: **security**, second PDR pass, base `d877784` (= HEAD = `origin/master`).
> Re-read: `02b-security-review.md` (my first pass), `PLAN.md` §12.3 / §12.4 / §13 / §14,
> `01-requirements.md` §3.0, §3.6, §3.7, §3.8, §4.1, §5.2, §6.1, §6.5 (A-04, A-05, A-13 … A-18,
> A-25, A-26, A-38, A-39, A-40, A-41), and the live tree.
>
> **Nothing below is discharged by reading an amendment.** Every condition was re-verified by
> re-reading the requirement text it claims to live in, and every defect claim was re-executed
> against `d877784`. Per C-43 a citation is not evidence; per C-44 a corrective pass having run is
> not a discharge. Three probe lanes ran on independently written harnesses in the system temp
> directory. No file under `mapper/` or `tests/` was modified; no pytest gate was run (C-25).
> Every code point below is written as a `U+XXXX` **name** and was constructed with `chr(0x...)` at
> probe time — this document contains no control byte.

---

## 1 · VERDICT

> ### `BLOCKED`
>
> **3 blockers · 3 majors · 1 minor.** Ten of my twelve conditions are genuinely discharged, and
> the amendment set is the strongest requirements work in this batch's history. **C-2 and C-3 are
> not discharged**, and the reason is the same in both cases: a control was implemented or written
> to the edge of the noun that was named, and the artifact then recorded the narrow control as
> closing the wide class.
>
> **The decisive finding is `S-16`.** `PLAN.md` §12.3 and decision `D18` strike `S-02` as
> `SATISFIED-EXTERNALLY` and discharge `C-2` "by execution". Re-executed: the repair batch's
> `_coerce_field` covers **2 of the 5 file-derived position families** in `MapStore.load`. The
> other three — attachment `kind`/`path`/`caption`, schema `key`/`label`/`kind`, and the node id —
> are uncoerced, and `S-02`'s exact signature (*loads clean, then kills a consumer*) **reproduces
> verbatim on them**, on this batch's own new surfaces. This is `M-S1`, the mutant `02b` named at
> authoring time, executed on `master`.
>
> **`S-17` is why nobody caught it.** `LLR-STO.1.1` — the requirement `C-2` demanded, whose whole
> point was to quantify over positions **derived from `_build_sidecar`** rather than hand-listed —
> **does not exist in the document**. It is referenced four times as an owner of obligations and has
> no heading, no statement, no threshold, no `TC`, no `AT` and no traceability row. `A-40` folds
> `S-11` into it. The live half of `S-02` and the whole of `S-11` fall through that hole.
>
> The two interface changes I approved in `02b` — `ViewState`/`IRenderer` (D4, R-012) and `Canvas`'s
> widening (D9, R-016) — **I still approve.** Neither is why this gate fails.

**What would lift the block:** write `LLR-STO.1.1` as a real requirement (S-17), scope its coercion
to the derived position set so it covers the three uncovered families (S-16), and add an abort
clause plus a renderer-qualified fixture to `HLR-N13.3` (S-18). None of the three is a design
question; all three are one requirement each.

---

## 2 · Condition discharge audit

Each row was verified by **re-reading the requirement text named in the "Verified by re-reading"
column**, not by trusting `§6.5`'s claim that the fold happened.

| # | Condition | Status | Verified by re-reading |
|---|---|---|---|
| **C-1** | `LLR-CNV.4.1` — cycle- and depth-safe traversal, with the `b=3 d=7` → `2187` positive control and the depth arm | **DISCHARGED — by execution, not by requirement** | The requirement was never written and no longer needs to be: the repair batch shipped the control. Probe 1 (below): memoised iterative rewrite at `mapper/views/radial.py:47-80` / `:83-86` and `mapper/views/layered.py:84-108`; **0** `RecursionError` across depth 500 / 1500 / 3000 / 20000; correctness control returns **2187**. Both arms of `M-C3` (my own failed candidate) are green. |
| **C-2** | `LLR-STO.1.1` (store-boundary coercion, positions **derived** from `_build_sidecar`) **and** `LLR-N13.1.5` (per-map containment) | **LIVE — half written, half executes FALSE** | **`LLR-N13.1.5`: DISCHARGED.** Re-read at `01-requirements.md:2391-2441` — statement, the declared card state, a two-clause threshold and mutants covering the "smallest edit", the "change nothing" and the "toast only" shapes. `A-04`'s correction of `M-H1` is real and correctly reasoned. **`LLR-STO.1.1`: DOES NOT EXIST** (S-17), and the coercion it was to mandate is 2-of-5 complete on the tree (S-16). |
| **C-3** | `HLR-N13.3` mount budget; `AT-025` promoted under `LLR-N13.1.5` | **LIVE — written, and its threshold cannot see the harm** | Re-read at `:2553-2653`. The promotion of `AT-025` is real (`:2642-2647`). The budget is a genuine work bound and `D19`'s single-definition discipline is correctly held (`:2570-2576`, `:2616-2621`). But nothing in it bounds the **stall** — see S-18. |
| **C-4** | `COERCION_RANGES` replaces *"0 control bytes"* in all four thresholds; widen the control map; coerce before truncating; split-at-width arm; assert the **painted row** | **DISCHARGED** | §3.0 re-read at `:376-468`. All four thresholds re-read individually and each now references `COERCION_RANGES` on the painted row with the split-at-width arm: `LLR-N06.2.3` `:1577-1583`, `LLR-N13.2.1` `:2519-2522`, `LLR-N14.2.3` `:2984-2987`, `LLR-N16.2.3` `:3441-3446`. **Re-executed by me** (§6): 84 declared points, 62 covered, **22 uncovered**; both truncators reproduce; positive controls green. `A-14`'s correction — that `darkside.fit` already coerces first and the live ordering defect is a *second* truncator — is executed-true and is a better finding than my own condition. |
| **C-5** | Widen `LLR-N14.2.3` and `LLR-N16.2.3` to every file-derived string; derive fixture positions; add the missing row-length clause to `LLR-N16.2.3` | **DISCHARGED** | `LLR-N14.2.3` re-read `:2968-2992` — scope now names schema **key names** and labels explicitly, with a threshold clause requiring `>= 1` derived position to be a schema key name (that clause is what reddens the narrow fix). `LLR-N16.2.3` re-read `:3428-3452` — the row-length clause is present and its rationale (an unbounded caption defeats `HLR-N16.1`'s `x`-clipped oracle) is correct. |
| **C-6** | Settle the lens predicate, case rule and empty-query state; declare term-count and query-length bounds; **answer Q-8** | **DISCHARGED** | `LLR-N14.1.4` re-read `:2765-2819`. Equality under case folding; the `C:alt` → 0 arm; the lowercase-key arm; the empty/whitespace arm binding **both** owners, which closes the `search_hits` half `AT-023` left open. **Q-8 is folded into the requirements, not merely ruled in the PDR** — `:2871-2882` and the §6.1 row at `:4154`, both naming `LLR-N14.1.3` as the home. |
| **C-7** | Reword *"every new text sink this batch creates"*; gate with a **derived** census; bring the three home `escape()` sites in scope | **DISCHARGED** | `LLR-N06.2.3` acceptance re-read `:1584-1604` — the old wording is struck in place, the scope is *"every file-derived string painted on a surface this batch touches, whether its sink is new or pre-existing"*, and the census must assert its own input set is non-empty. `LLR-N13.2.1` acceptance re-read `:2523-2546` — the three addresses are re-derived and explicitly labelled *"evidence, not the census"*. That distinction is the condition's substance and it is correctly held. |
| **C-8** | `markup=False` + `plain()` on the `notify` sites; declare the new toast in §4 | **DISCHARGED** | `LLR-N06.2.5` re-read `:1506-1563`. **Census independently re-derived by AST walk on a separately written harness: 30 total / 19 non-literal / 0 with markup enabled / 15 not routed through the coercion helper — matching `A-18` exactly, and the 15 addresses match one for one.** The rule is stated as a class whose gate is the derivation; the addresses are labelled evidence. `M-N06.2.5-b` correctly records that the line-oriented count returns 30 *by coincidence*. §4 declaration confirmed at `:3685`. |
| **C-9** | Declare the `dots`/`bgs` value domain as a token set with a fallback tone | **DISCHARGED** | `LLR-CNV.1.4` re-read `:1047-1076`. Validation is placed in `rows()` — the one convergence point — and `M-V1` (validate at write time) is named as surviving because it misses the direct-assignment site. Closes `Q-10`'s other half without creating a second vocabulary. |
| **C-10** | Extend the coercion range list to the SVG export sink | **DISCHARGED** | `LLR-CNV.2.1` re-read `:1241-1248`. The exported SVG shall contain no code point in `COERCION_RANGES`, sharing the §3.0 list. The rationale — the file leaves the machine and the terminal's escaping does not travel with it — is the right one. `save_svg` is also a declared `SINK` on `canvas_paint` (`:3533`). |
| **C-11** | Give `MapStore.list_maps` a cached metrics read | **DISCHARGED** | `LLR-N13.1.6` re-read `:2460-2466`. Requires the sala to draw thumbnails without reindexing, and correctly records that a **warm** measurement is not evidence the mount is cheap because the reindex short-circuits on a hash match. |
| **C-12** | Record `F-m4`'s disposition | **DISCHARGED** | `LLR-N13.1.6` re-read `:2476-2483`. Dispositioned measured-and-closed with the mechanism (aliases share objects rather than deep-copying; only three keys are traversed), **and the carried arm named** — a bomb under `nodes:`, which *is* traversed. That carried arm is assigned to `LLR-STO.1.1`, so it inherits S-17. |
| **S-11** | `MapStore.load` shall raise only `MapStoreError`; fixture set derived from `_build_sidecar` | **FOLDED IN NAME ONLY — and the defect is LIVE** | The *substance* is written as prose at `:2467-2475` inside `LLR-N13.1.6`, with the statement and `M-B1` named. But it is assigned to `LLR-STO.1.1`, which does not exist (S-17), while `LLR-N13.1.6`'s own statement is about **load counts** and says nothing about exception types. Re-executed: **3 of 3 rejected inputs still leak a non-`MapStoreError` type.** |

**Score: 10 discharged, 2 live, 1 folded in name only.**

---

## 3 · `S-01` / `S-02` / `S-03` status, on executed evidence

### `S-01` — a cycle or a deep chain kills the app · **DISSOLVED. `C-1` discharged.**

The repair batch's claim holds and is better than claimed. Executed at `d877784`:

```
=== (b) battery on 3-node CYCLE ===
  [cycle a->b->c->a]  nodes=3 edges=3 root='a'
    _leaves(root)               0.01 ms  RAISED ValueError: cycle through a: the graph is not a tree
    RadialRenderer.render       0.02 ms  RAISED ValueError
    LayeredRenderer.render      0.03 ms  RAISED ValueError
    graph.focus(root)           0.01 ms  OK

=== (d) deep acyclic CHAIN ===
  [chain depth=20000]  _leaves 58.48 ms  OK      (parked: RecursionError at depth 1500)

=== (e) correctness positive control ===
  LEAF-COUNT VALUE for b=3 d=7 = 2187   (expected 2187)  -> CORRECT
```

Cycles are refused at **three** layers — the parser (`mapper/mermaid.py:116-118`), `_leaf_counts`
(`mapper/views/radial.py:72`) and `_tree_layout` (`mapper/views/layered.py:103`) — and all three
production render call sites sit inside `except Exception` (`mapper/app.py:743`, `:1360`, `:1737`).
The depth arm passes to 20000. **The correctness arm passes**, which is what separates this from
`M-C1` and `M-C2`: the rewrite is memoised and iterative, not capped, and it returns the right
number. My own failed candidate `M-C3` is superseded by a better implementation than I proposed.

### `S-02` — a non-string ficha field loads clean and kills every consumer · **STILL LIVE. `C-2` NOT discharged.** → `S-16`

`_coerce_field` (`mapper/store.py:39-56`) is real, correct in its semantics, and applied at exactly
**two** call sites — `store.py:235` (text attributes) and `store.py:239` (field values). Its input
set for the first is `_text_attributes()` (`store.py:20-32`), which **derives** from
`Ficha.__dataclass_fields__`. That is exactly the discipline `C-2` asked for — **applied to one
dataclass.** Two lines below, `Attachment` and `SchemaField` are hand-constructed from raw
`.get()`:

| Position family | Coerced? | Address |
|---|---|---|
| ficha `fields` values | **yes** | `store.py:239` |
| `title`, `state`, `meta`, `notes` | **yes** | `store.py:235` + derived at `:20-32` |
| attachment `kind` / `path` / `caption` | **no** | `store.py:243` — `Attachment(kind=a["kind"], path=a["path"], caption=a.get("caption", ""))` |
| schema `key` / `label` / `kind` | **no** | `store.py:199-205` — plain `f.get(...)` |
| node `id` | **no** | `store.py:222-224` — `nid` taken raw as the sidecar mapping key |

`S-02`'s exact signature reproduces on the uncoerced families. Executed:

```
--- attachment path INT, no caption ---
    store.load OK  warnings=[]                          <== loads completely clean
      search_hits('a')     RAISED TypeError: sequence item 0: expected str instance, int found

--- node id INT (sidecar mapping key) ---
    store.load OK  warnings=[]                          <== loads completely clean
    node ids=['a', 'b', '123', 123]                     <== DUPLICATE node created
      graph.coverage()     OK -> (0, 4)                 <== denominator silently DOUBLED, 2 -> 4
      search_hits('a')     RAISED TypeError

--- schema key INT / label INT ---
    store.load OK  warnings=[]
      missing_required(first)  OK -> [5]                <== an int reaches the lens's field echo
```

**Why this is a blocker for THIS batch specifically, on this batch's own new surfaces:**

1. **The int-node-id case is the worst one and it raises nothing.** It loads with `warnings=[]`, so
   `load_or_notice`'s warning arm (`mapper/app.py:459-464`) never fires, nothing raises, and
   `LLR-N13.1.5`'s containment never engages — there is no failure to contain. The map paints a
   card with a **silently doubled coverage denominator**. US-N13 paints a per-map coverage bar
   (`LLR-N13.1.2`) and a coverage percentage (`LLR-N13.1.3`, pinned at 100 by `A-08`). A wrong
   coverage number on the sala is precisely what `D14` exists to prevent — the batch's own record
   is that three coverage definitions once disagreed by 100 points. This is a fourth way to be
   wrong, and it is invisible to every guard the batch has written.
2. **`search_hits` is the single owner of "what matches" under `D6`**, and `HLR-N07.2`'s
   trustworthy count is taken from it. Two of the uncovered families make it raise `TypeError`.
3. **Schema keys reach the lens's `· campos:` echo** — `S-06`'s surface. `LLR-N14.2.3` now coerces
   **code points** there (C-5, correctly discharged), but it assumes it is handed a `str`. A
   non-`str` schema key defeats it upstream of the coercion it was widened to perform.

`A-16` (`:4647-4650`) draws the type-vs-code-point distinction carefully and correctly — and then
describes `_coerce_field` as *"applied at `:235` for attributes and `:239` for fields"* without
asking what it is **not** applied to. That is the one question `LLR-STO.1.1` existed to force.

**This is `M-S1` executed.** `02b` named it at authoring time: *"coerce only `Ficha.fields` values
— survives; the identical defect ships in its siblings; the threshold must quantify over the
**positions**, derived from `_build_sidecar`, not hand-listed."* The repair batch shipped `M-S1`'s
larger cousin and the batch recorded it as the class being closed.

### `S-03` — the sala's failure containment is a checkbox and nothing bounds the mount · **PARTIALLY CLOSED. `C-3` NOT discharged.** → `S-18`, `S-19`

The structural half **is** closed and closed well: `HLR-N13.3` and `LLR-N13.1.5` exist, `AT-025`'s
error arm is promoted out of the boundary catalog under a real LLR, and `A-04`'s correction of my
`M-H1` threshold is right — I verified the shipped misdeclaration independently at
`mapper/app.py:559-573`, where the row is added unconditionally and the `else` arm at `:566-567`
sets `"concept", "0", "0"`. **A requirement written to painted card count alone would pass on the
shipped defect, and `LLR-N13.1.5` correctly asserts count AND distinguishability.** That is a
genuine improvement on my own condition and I adopt it.

What is **not** closed is the bound itself — see the next section.

---

## 4 · `S-15` adequacy ruling

**Reproduced independently, with positive controls, on a third harness.** Controls first, as the
brief requires:

```
POSITIVE CONTROL A  12001-node chain, layered   0.1 ms   refusal fired: True    cap read back = 12000
POSITIVE CONTROL B  12000-node chain, layered 179.3 ms   refusal fired: False
```

Control A proves the harness reaches the enforcement point; Control B lands at 179.3 ms against the
reported 179.8 ms. Only then the shapes:

| shape | nodes | edges | LayeredRenderer | refusal fired |
|---|---|---|---|---|
| 3 layers × 5 | 16 | 55 | 2.1 ms | False |
| 4 layers × 8 | 33 | 200 | 50.6 ms | False |
| **5 layers × 10** | **51** | **410** | **1536.0 ms** | **False** |
| 6 layers × 12 | 73 | 732 | **53857.0 ms** | False |

The mechanism is confirmed quantitatively, not just reproduced: cost per predicted root-to-node
path visit is **10.8 – 16.5 µs, constant across four orders of magnitude**, chain and DAG alike.
The renderer's cost is linear in **path** count; the guard counts **nodes**. `S-15` is real.

**Ruling: folding it under `HLR-N13.3` is the right home and the fold as written is NOT sufficient.
Three defects, each individually fixable.**

### `S-18` — the budget declares the stall, it does not bound it · `[blocker]`

- **What.** Threshold 2 is *"`WORKSPACE_CARD_BUDGET_MS = 250` per map — a **work** bound measured
  as **elapsed time** of that map's summarise-and-render step"*. To know a step exceeded 250 ms by
  measuring its elapsed time you must first let it finish. On the 73-node shape that is 53.9 s of
  frozen UI, after which the card is correctly labelled over-budget. **The harm `S-15` describes is
  the stall, and no threshold in `HLR-N13.3` bounds it.** Threshold 1 bounds mount only for a
  workspace of healthy maps (200 maps of ≤ 128 nodes); threshold 4 bounds card *count* and *state*;
  neither bounds wall clock when an over-budget map is present.
- **Where.** `01-requirements.md:2578-2587` (the four thresholds), `:2628-2636` (the mutant table).
- **Executed.** `grep -n "abort\|interrupt\|cancel\|deadline\|pre-render\|stall" 01-requirements.md`
  → **1 hit, and it is the word "installed"** in an unrelated sentence at `:3956`. Zero occurrences
  of any abort concept in 5199 lines. And no mechanism exists to build on:
  `grep -rn "perf_counter\|monotonic\|deadline\|timeout\|budget\|elapsed" mapper/views/ mapper/app.py mapper/canvas.py`
  → **no output**. By contrast the bound that *does* work is a cheap **pre-traversal** check:
  `if len(graph.nodes) > MAX_RENDER_NODES:` at `mapper/views/layered.py:143`,
  `mapper/views/outline.py:65`, `mapper/views/radial.py:117`. The work budget has no equivalent.
- **Named weaker variant `M-H7`** *(new; not in the requirement's table)* — **measure the step's
  elapsed time after the call returns and label the card over-budget.** Survives thresholds 1, 2, 3
  and 4; survives the 51-node acceptance fixture; leaves the 53.9-second stall exactly as it is.
  It is the *most natural reading of the requirement's own wording*, which is what makes it
  dangerous. Reddened by neither of the five mutants the requirement names.
- **Recommendation.** One added threshold clause and one added mutant:
  > **Threshold 5 — the mount's total wall clock is bounded in the presence of an over-budget map.**
  > On a workspace of `N` maps of which `k` exceed the per-map budget, total mount wall clock
  > `< (N + k) × WORKSPACE_CARD_BUDGET_MS + declared slack`, measured. A map is refused **before**
  > its traversal by a work estimate, or its traversal yields to a deadline — post-hoc measurement
  > does not satisfy this clause. **`M-H7`** is named as the variant this clause exists to redden.

  Detection-after-the-fact is the weakest of the three control classes; this batch's own rule is
  prevention over detection where prevention is cheap, and here it is: an edge-product or fan-out
  estimate is O(edges), the same cost class as the node count already being read.

### `S-19` — the 51-node fixture is under budget on one of the three affected renderers · `[major]`

`HLR-N13.3` (`:2613-2615`) elects the 51-node shape as *the* acceptance fixture. Measured on the
same shape across renderers:

| renderer | 5 × 10 (51 nodes, 410 edges) | vs the 250 ms budget |
|---|---|---|
| `LayeredRenderer` | 1536.0 ms | over ✓ |
| `OutlineRenderer` | 677.7 ms | over ✓ |
| **`RadialRenderer`** | **177.5 ms** | **UNDER — threshold 4 never fires** |
| `LaneRenderer` | 0.3 ms | unaffected (never traverses) |

**On `RadialRenderer` the acceptance fixture is inside the budget**, so `k = 0`, no over-budget card
is produced, and threshold 4's containment arm cannot distinguish a correct implementation from a
missing one. The fixture must either **name the renderer it is measured against**, or be sized so
it exceeds the budget on the **cheapest affected** renderer. This is the fourth time in this batch
a plausible-looking value would have read as data, and the first three are all recorded in
`PLAN.md` §14.1.

**The 51-node shape is otherwise the right choice** and I endorse the reasoning that a 70-second
node has no place in a gate — the defect is the missing renderer qualifier, not the size.

### `S-20` — the fold treats one traversal helper where there are three, and two more shapes are in the same class · `[major]`

- **Three of four renderers carry their own private copy of the un-memoised walk**, not one shared
  helper: `mapper/views/layered.py:84` (`_tree_layout.walk`), `mapper/views/outline.py:115`
  (`walk`), `mapper/views/radial.py:134` / `:181` (`place`, `tag`). Each also carries its own
  private `MAX_RENDER_NODES`. There is nothing to fix once. Inc-2 rewrites all three behind
  `IRenderer`, which is the increment where this either gets fixed uniformly or gets fixed in one
  place and left in two.
- **Two further shapes in `S-15`'s class, executed, that the fold does not cover:**
  - A **flat 10 000-node fan** renders in **33 479 ms** through `LayeredRenderer`. 10 000 is under
    the 12 000 cap so nothing short-circuits — it genuinely draws. The cost driver here is **leaf
    count**, a third quantity, neither node count nor path count.
  - `graph.focus(root)` at depth 20 000 takes **12 545 ms**. It is iterative and correct, but
    `children_of` (`mapper/model.py:149-150`) rescans every edge per node, i.e. O(N·E). **`focus`
    is not a renderer**, so `HLR-N13.3` threshold 3 — which consumes the renderers' refusal —
    does not reach it, and no cap guards it.
- **Scope note, and it is a correction to the requirement's rationale.** `HLR-N13.3`'s rationale
  (`:2562-2564`) says the sala *"loads and summarises every map before any card paints"*. The load
  half is true — `mapper/app.py:476` globs and `:558-560` loads every map. The **summarise** half
  is not true *today*: the recents loop takes only `len(graph.nodes)` and `len(graph.documents)`
  (O(1)), `_map_metrics` runs on the hero map only, and **no renderer is invoked from
  `on_mount`**. The rationale is correct about the *planned* state — US-N13 adds the per-map
  constellation thumbnail — and should say so, because as written it asserts a shipped property
  that executes false, and the next reader will check it. Meanwhile the defect's **live** blast
  radius is `MapScreen`: one keystroke from home, 53.9 s of frozen UI, and `HLR-N13.3` is scoped
  to the sala and does not bound it.

---

## 5 · Sink census — every new file-derived-text sink this batch creates

The batch's shape is trigger family **C-17**: *new string → rendered or persisted surface*, not
*new external endpoint*. Enumerated, with the scoping verdict:

| # | New file-derived-text sink | Owning requirement | Scoped as a class with a derived census? |
|---|---|---|---|
| 1 | Map titles → home / sala card rows | `LLR-N13.2.1` (`:2508-2551`) | **YES.** Scope is *"a surface this batch touches, new or pre-existing"*; the three `escape()` addresses are explicitly evidence, not the census. |
| 2 | Node titles → sala thumbnails | `LLR-N13.2.1` | **YES** — same class. |
| 3 | Branch titles → fold pill on the canvas | `LLR-N06.2.3` (`:1565-1607`) | **YES** — and it owns the census itself (`:1591-1594`), which must assert its own input set is non-empty. |
| 4 | Ficha field values → lens result line and count | `LLR-N14.2.3` (`:2968-2992`) | **YES** — positions derived from `_build_sidecar`. |
| 5 | Schema key names and labels → lens `· campos:` echo | `LLR-N14.2.3` | **YES for code points** (the `>= 1` derived-key clause reddens the narrow fix). **NO for type** — the schema key is uncoerced at `store.py:199-205` and may not be a `str` at all (S-16). |
| 6 | Glyph vocabulary captions and binding labels → legend | `LLR-N16.2.3` (`:3428-3452`) | **YES** — widened past *"binding label"*, row-length clause added. |
| 7 | Interpolated toast messages (product-wide) | `LLR-N06.2.5` (`:1506-1563`) | **YES — the strongest of the set.** Gate is an AST-derived census; addresses labelled evidence; the grep variant named as a coincidence. |
| 8 | Exported SVG text | `LLR-CNV.2.1` (`:1241-1248`) | **YES** — shares the §3.0 list. |
| 9 | Attachment `kind` / `path` / `caption` → rail, inspector, `search_hits` haystack | **none** | **NO — uncovered entirely** (S-16). Executed: an int `path` loads clean and raises `TypeError` in `search_hits`. |
| 10 | Node ids → every surface that renders an id | **none** | **NO — uncovered entirely** (S-16). Executed: an int node id loads clean, duplicates the node and doubles the coverage denominator. |

**Verdict on the census question the brief asked: eight of ten sinks are correctly scoped as a
class with a derived census, and the scoping discipline is genuinely good.** Sinks 9 and 10 have no
owner because they were assigned to `LLR-STO.1.1`, which does not exist.

### `S-21` — the IFC declares coercion at exactly one flow node · `[minor]`

`§4.1` has five flows. `darkside.plain` appears at **exactly one node**, `home_cards` (`:3594`), and
that node's contract still reads `out : str with no control bytes and no live markup` (`:3597`) —
the phrase §3.0 supersedes, stating a weaker `out` than its own owning LLR's threshold.
`canvas_paint`, `match_set`, `overflow_declaration` and `legend` declare **no coercion transform at
all**, even though `overflow_declaration`'s pill node is owned by `LLR-N06.2.3` (`:3572`) and
`legend`'s `_render_keymap` node is owned by `LLR-N16.2.3` (`:3610`) — both coercion LLRs. The lens
result line, `LLR-N14.2.3`'s own surface, owns no node in `match_set` at all.

`A-18` argues, correctly, that *"a text sink that no contract row names is a sink the reverse census
does not see"* — and applies that argument to one toast while leaving the pill, the lens chip and
the legend undeclared. **This does not defeat the gate**, because the gate is the derived census in
code and it does not read §4. It is a minor: the IFC is what a Phase-3 implementer reads to find
where the helper is required, and it currently says "one place".

---

## 6 · Evidence checklist

| Item | ✓/✗ | Re-runnable citation |
|---|---|---|
| Every finding has what · where · why · recommendation | ✓ | §3 (`S-16`), §4 (`S-18`, `S-19`, `S-20`), §5 (`S-21`), §2 (`S-17` in the `C-2` and `S-11` rows) |
| Every finding has a severity | ✓ | `S-16` blocker · `S-17` blocker · `S-18` blocker · `S-19` major · `S-20` major · `S-21` minor. Counts restated in §1 |
| No secret value appears in this output | ✓ | `grep -rniE "api[_-]?key|secret|token|password|BEGIN .*PRIVATE KEY|credential|Bearer " .dev-flow/2026-08-26-ui-next-batch-02/` → only design-token hits (`SAGE`, `TEAL`, `VIOLET`, "token set"). `git ls-files \| grep -iE "\.env\|credential\|secret\|\.pem\|\.key"` → empty. `.gitignore` covers `*.db`, `.mapper/`, `*.svg`, `*.png` |
| Verdict is explicit | ✓ | §1 — `BLOCKED` |
| New tool/integration scope and blast radius addressed | ✓ | **None added.** `git diff d6b60e6..d877784 -- pyproject.toml` = +8 lines, pytest markers only, **no new dependency**. No MCP, Composio, n8n or network surface in scope. Blast radius remains local rendering of local files |
| Every condition discharged by RE-READING, never by trusting the fold | ✓ | §2's fourth column names the line range re-read for each of C-1, C-2, C-3, C-4, C-5, C-6, C-7, C-8, C-9, C-10, C-11, C-12 and S-11 individually |
| Every defect claim re-EXECUTED at `d877784` | ✓ | Probe 1 (`S-01` battery + cap boundary), Probe 2 (`S-02` ten hostile sidecars + four uncovered-surface cases), Probe 3 (`S-15` shapes with two positive controls), my own §3.0 re-execution (84 / 62 / 22 + both truncators) |
| Timing probes carry a positive control | ✓ | `S-15` lane: Control A (12001 nodes, refusal fires, cap read back = 12000) and Control B (12000 nodes, 179.3 ms) both reported **before** any DAG figure. Coercion probe: ESC/OSC-52 coerced = True, benign string unchanged = True |
| `02b`'s stale renderer timings NOT quoted | ✓ | The parked 3.4 s / 9.1 s figures appear nowhere in this document. All timings are re-measured at `d877784` |
| `M-H1`'s already-green remedy NOT used as a threshold | ✓ | §3 `S-03` adopts `A-04`'s correction: the threshold is painted card count **AND** state distinguishability. I verified the shipped misdeclaration independently at `mapper/app.py:559-573` |
| Every new required control carries a **named weaker variant** | ✓ | `M-H7` (post-hoc elapsed measurement) for `S-18`; `M-S1` re-executed on `master` for `S-16`; the renderer-unqualified fixture for `S-19` |
| No mutated token spelled verbatim (C-56) | ✓ | Mutants described by position and operation only |
| Ids enumerated individually, no dotted ranges | ✓ | §2 table; the checklist row above |
| No control byte written into this file | ✓ | Every code point named as `U+XXXX`; every payload constructed with `chr(0x...)` at probe time |
| No code modified; no gate run | ✓ | `git status --porcelain` → `M .dev-flow/state.json` + the untracked batch dir only. No pytest invoked (C-25). Harnesses in the system temp directory |

---

## 7 · Gate verdict

> ### `BLOCKED`
>
> **The security lens cannot go `approved`. Three blockers:**
>
> - **`S-16`** — `C-2`'s discharge executes FALSE. `_coerce_field` covers 2 of 5 file-derived
>   position families; `S-02`'s signature reproduces verbatim on the other three, on this batch's
>   own new surfaces, including a **silently doubled coverage denominator that raises nothing** and
>   therefore defeats `LLR-N13.1.5`'s containment by never triggering it. `PLAN.md` §12.3 and `D18`
>   must be corrected: `S-02` is narrowed, not dissolved.
> - **`S-17`** — `LLR-STO.1.1` does not exist. Four prose references, no heading, no statement, no
>   threshold, no `TC`, no `AT`, no traceability row. `S-11` (executed: 3 of 3 rejected inputs still
>   leak a non-`MapStoreError` type) and the YAML-bomb-under-`nodes:` arm are folded into it. **A
>   condition folded into a phantom id is folded in name only**, and the brief asked me to say so.
> - **`S-18`** — `HLR-N13.3` declares the over-budget card state and bounds nothing. A post-hoc
>   elapsed-time measurement satisfies all four thresholds and leaves the stall; zero abort concepts
>   appear in 5199 lines; no deadline mechanism exists in the tree to build on.
>
> **What I am not blocking on.** `C-1`, `C-4`, `C-5`, `C-6`, `C-7`, `C-8`, `C-9`, `C-10`, `C-11`
> and `C-12` are genuinely discharged, and several are discharged *better than I specified* —
> `A-14`'s discovery of a second uncoerced truncator, `A-04`'s correction of my own `M-H1`
> threshold, and `A-18`'s AST census are each stronger than the condition that asked for them. The
> `ViewState`/`IRenderer` and `Canvas` interface changes remain approved. `S-19`, `S-20` and `S-21`
> are recommendations against their increments and do not gate.
>
> **On re-submission I will re-execute** the `_coerce_field` position census over all five families,
> the three-exception-leak battery, the `S-15` shapes on all three affected renderers against the
> chosen fixture, and the `notify` AST census. A claim that these landed is not evidence that they
> landed.
