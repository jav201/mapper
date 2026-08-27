# 01 — Requirements · `2026-08-26-repair-batch` (PR A) · four shipped defects

> **Artifact language: English.** Quoted UI strings are **Spanish**, because Spanish is what ships.
> Normative keyword: **shall**. `should` never appears inside an HLR/LLR statement.
>
> **Scope fence.** This batch changes **no frozen interface.** `IRenderer.render` and `Canvas` stay
> byte-for-byte as they are on `master`; the `ViewState` migration and the `dots`/`bgs` work belong to
> the parked feature batch. A repair PR whose diff also moves two frozen interfaces is not a sharper
> gate — and a sharper gate was the entire argument for splitting.

---

## 1 · The four defects, each with its executed reproduction

All four were reproduced by the orchestrator independently of the review that raised them. Transcripts
live in `.dev-flow/2026-08-26-ui-next-batch-02/PLAN.md` §6 and §11.

| id | Defect | Reproduction |
|---|---|---|
| **S-01a** | `mermaid.parse` accepts a cycle (`c --> a`); `RadialRenderer` and `LayeredRenderer` both raise `RecursionError`; `MapScreen.refresh_canvas` (`app.py:1300`) has no guard, so it escapes the Textual message pump and the app dies | executed, with a positive control |
| **S-01b** | A **depth-500 acyclic chain** raises `RecursionError` in 0.01 s — no cycle needed | executed |
| **S-02** | `D: 20260826` in a sidecar loads clean as `int`; `Ficha.missing_required` then raises `AttributeError: 'int' object has no attribute 'strip'`, `Graph.search_hits` raises `TypeError`, and **`coverage()` returns `(2, 2)` — silently counting the malformed field as documented** | executed, with a positive control |
| **S-07** | With the rail visible, `#map-rail` takes the whole body width; canvas is laid out at `x = 140` on a 140-column compositor (width 1) and the inspector at `x = 141` — both entirely off-screen | executed via post-layout `widget.region` + compositor strips |
| **S-08** | `?` paints **16 of 27** map-scope bindings at **both** 118×34 and 200×80; the 11 dropped are the whole `view` group, `z plegar rama` included. `help.py:36-39` caps a non-scrolling container at 28 rows over ~38 rows of content | executed |

**Why these four and no others.** The accepted scope rule is that a batch repairs exactly what its own
successor's stories make newly reachable. S-07 and S-08 are preconditions of US-N06 and US-N16.
S-01 and S-02 become reachable **without opening anything** once US-N13's sala loads every map in the
workspace on mount. Nothing else is admitted.

---

## 2 · Stories

### US-R01 · A malformed map is refused, not fatal

> **As** an operator who has just been handed a `.mmd` from a colleague or a repo,
> **I want** a map that cannot be drawn to be **refused with a reason I can act on**,
> **so that** a bad file costs me an error message instead of the application.

**Acceptance (black-box).** *When a map whose `.mmd` contains a cycle is opened, the operator sees a
Spanish message naming the cycle and the application remains usable.* → `AT-R01`, `AT-R02`, `AT-R03`.

### US-R02 · A deep map draws, or says why not

> **As** an operator with a genuinely deep legacy map,
> **I want** depth to be a rendering problem, not a crash,
> **so that** the tool's limit is something it tells me rather than something it does to me.

**Acceptance.** *When a map 500 levels deep is rendered, a picture is produced — or a declared
degradation is shown. `RecursionError` never reaches the operator.* → `AT-R04`, `AT-R05`.

### US-R03 · A malformed ficha field is never counted as documented

> **As** an operator relying on the coverage figure to decide where to work,
> **I want** a field the tool cannot read to count as **missing**, loudly,
> **so that** the number I plan against is not quietly inflated.

**Acceptance.** *When a sidecar carries a non-string field value, the map still loads, every consumer
survives, the operator is told which node and which field were malformed, and `coverage()` does not
count an unreadable field as documented.* → `AT-R06`, `AT-R07`, `AT-R08`, `AT-R09`.

### US-R04 · The three regions are on the screen

> **As** an operator on a terminal wide enough to show the rail,
> **I want** the canvas and the ficha to be visible,
> **so that** the map is visible at all.

**Acceptance.** *When a map is opened at 140 × 45 and at 120 × 40, the rail, the canvas and the
inspector each occupy a disjoint, on-screen column range, and the canvas paints map content.*
→ `AT-R10`, `AT-R11`.

### US-R05 · `?` shows every key that works here

> **As** an operator learning the tool from inside it,
> **I want** `?` to show **every** binding of the current scope,
> **so that** the help is a description of the keyboard rather than a sample of it.

**Acceptance.** *When `?` is pressed, the set of bindings the panel presents equals
`keymap.bindings_for(scope)` exactly — derived by set equality, never hand-listed — and no binding is
dropped in silence at any terminal size.* → `AT-R12`, `AT-R13`, `AT-R14`.

---

## 3 · HLR / LLR

### HLR-R01 — cycle refusal *(US-R01)*

**HLR-R01.** The system **shall** refuse to construct a `Graph` whose edge set contains a directed
cycle, and **shall** report the cycle's node path.
*Validation: test.* *Touched symbols: `mapper/model.py::Graph`, `mapper/mermaid.py::parse`, `mapper/store.py::MapStore.load`.*

- **LLR-R01.1.** `model` **shall** expose `Graph.find_cycle() -> list[str] | None` returning the node
  ids of one directed cycle in traversal order with the entry node repeated last (`['a','c','a']`), or
  `None` when the edge set is acyclic. It **shall** be iterative — no recursion — and **shall**
  terminate on any edge set, including self-loops and disconnected components.
  *Layer 0 (cyclomatic ≥ 3, and it transforms data at a declared module boundary). TC-R01, TC-R02, TC-R03, TC-R04.*
- **LLR-R01.2.** `mermaid.parse` **shall** raise `MermaidError` when `find_cycle()` is non-`None`,
  and the exception text **shall** name the cycle path joined by `CYCLE_ARROW` (`mermaid.py:14`, a bare `U+2192` with no surrounding spaces).
  *TC-R05, TC-R06.*
- **LLR-R01.3.** `MapStore.load` **shall** surface that refusal as `MapStoreError` whose message is
  exactly `el mapa tiene un ciclo: <path>` where `<path>` is the node ids joined by `CYCLE_ARROW` — measured `el mapa tiene un ciclo: a→b→a`, with no surrounding spaces.
  *TC-R07.*
- **LLR-R01.4.** `MapScreen.refresh_canvas` and `HomeScreen.on_mount` **shall** each render a
  non-fatal notice instead of propagating, for **any** exception raised by load or by a renderer —
  scoped to the **sink class**, not to the two exception types this batch happens to know about.
  *Rationale: batch 1 §2.1b — a requirement naming specific cases gets satisfied at those cases'
  boundary while the siblings keep the defect.* *TC-R08, TC-R09.*

**Acceptance `AT-R01`** — a cycle map is opened through the shipped surface; the app survives and the
Spanish message names the cycle.
**`AT-R02`** — the message names the **actual** cycle nodes, not a fixed string (drive two different
cycles, assert the two messages differ and each contains its own nodes).
**`AT-R03`** — an acyclic map **still loads** (the discriminating negative: a refusal that refuses
everything is not a fix).

### HLR-R02 — depth safety *(US-R02)*

**HLR-R02.** No renderer **shall** raise `RecursionError` for any acyclic graph the store can load.
*Validation: test.* *Touched symbols: `mapper/views/radial.py::_leaves,place,tag`, `mapper/views/outline.py::walk`, `mapper/views/layered.py`.*

- **LLR-R02.1.** Every graph traversal in `views` **shall** be iterative or explicitly depth-bounded.
  The set of traversals is **derived by an AST walk for recursive functions in `mapper/views/`**, not
  hand-listed — C-31: a hand-listed set omits the member that fails.
  *TC-R10, TC-R11, TC-R12.*
- **LLR-R02.2.** `_leaves` **shall** be memoised, and **shall** return the same value as the shipped
  recursive implementation for every graph on which the shipped one terminates.
  *Positive control — the rewrite is only correct if it agrees where the old one worked.* *TC-R13.*
- **LLR-R02.3.** Where a graph exceeds a declared rendering bound, the renderer **shall** paint a
  declared degradation naming what was omitted, and **shall not** raise.
  *TC-R14.*

**`AT-R04`** — a depth-500 chain renders through the shipped surface without `RecursionError`.
**`AT-R05`** — a 3000-node tree renders, and the render completes within a declared time bound
(bound **measured** at implementation, pasted into the packet — never predicted; C-39).

### HLR-R03 — field-type integrity *(US-R03)*

**HLR-R03.** Every `Ficha` attribute the model declares as text **shall** hold a `str` after load —
**the set of such attributes derived from `Ficha`'s own field annotations, never named in this
requirement** — and a value the loader cannot faithfully represent as text **shall not** be counted
as documented. *(Amended by A-7; the prior form bounded the set to `Ficha.fields` by hand, and a
non-string `title` breaks the identical consumers by the identical mechanism.)*
*Validation: test.* *Touched symbols: `mapper/store.py::MapStore._graph_from_sidecar`, `mapper/model.py::Graph`, `mapper/model.py::Ficha.missing_required`.*

- **LLR-R03.1.** `_graph_from_sidecar` **shall** coerce a **scalar** value (`int`, `float`,
  `bool`, `date`, `datetime`, `None`) to `str` deterministically, and `None` **shall** become `""`.
  This applies to **each value of `Ficha.fields` and to every `Ficha` attribute annotated `str`**,
  the latter derived from `Ficha.__dataclass_fields__` rather than enumerated here.
  *Deterministic means: the same input yields the same output on every platform and Python version —
  asserted, not assumed.* *TC-R15, TC-R16.*
- **LLR-R03.2.** `_graph_from_sidecar` **shall** replace a **container** value (`list`, `dict`)
  with `""` and **shall** record the offending `(node_id, key)` as malformed, over the same derived
  set. A container is not faithfully representable as a ficha value, and `str({})` is a truthy
  string that would be counted as content.
  *TC-R17, TC-R18.*
- **LLR-R03.3.** `Graph` **shall** expose `load_warnings: list[str]`, one Spanish entry per malformed
  field: `campo ilegible: <node_id>.<key>`.
  *TC-R19.*
- **LLR-R03.4.** `MapScreen` and `HomeScreen` **shall** surface a non-fatal notice when
  `load_warnings` is non-empty, coerced through `darkside.plain()`.
  *TC-R20.*
- **LLR-R03.5.** **The map shall still load.** A malformed field **shall not** deny the map — that is
  defect `F-M5`'s shape (one malformed node denying the whole map) and this batch does not reproduce it.
  *TC-R21.*

**`AT-R06`** — a sidecar with `D: 20260826` loads; the field reads `"20260826"`; `missing_required`,
`search_hits` and `coverage` all return without raising.
**`AT-R07`** — **the container regression.** A sidecar whose only value for a required field is a
container loads, and `coverage()` reports that field as **missing**. *Pre-fix this node goes RED by
**denying the map**, not by miscounting — see A-8. The miscount is the SCALAR case, `AT-R06` and
`AT-R09`.*
**`AT-R07b`** — **the out-of-fields regression (A-7).** A sidecar whose `title` is a non-string
loads and `Graph.search_hits` returns without raising. *Driven for a non-string and for a bare
`title:` key, which YAML parses as `None` — the realistic hand-edited shape.*
**`AT-R07c`** — **the discriminating negative for A-7.** A sidecar whose `state` is a non-string
must ALSO load and survive every consumer — measured, `state` is joined by no consumer, so a fix
that coerces only the attributes that happen to break today is bounded by hand exactly as the
original requirement was.
**`AT-R08`** — the operator is told which node and which field were malformed.
**`AT-R09`** — a well-formed sidecar's coverage figure is **unchanged** from `master` (the
discriminating negative: a fix that counts everything as missing also passes `AT-R07`).

### HLR-R04 — three-region layout *(US-R04)*

**HLR-R04.** When the rail is displayed, the rail, canvas and inspector **shall** occupy disjoint
column ranges wholly inside the terminal width.
*Validation: test.* *Touched symbols: `mapper/app.py` `MapperApp.CSS` `#map-rail`* — corrected by **A-10**; `MapScreen` declares no CSS block of its own.

- **LLR-R04.1.** `#map-rail` **shall** declare a width equal to `rail.RAIL_WIDTH`, and a test
  **shall** assert the CSS value and the constant agree — so a later change to one reddens rather than
  silently re-opening this defect.
  *TC-R22, TC-R23.*

**`AT-R10`** — at 140 × 45 and 120 × 40, each region's `region.x` and `region.width` place it inside
the compositor, the three ranges are disjoint, and `canvas.width` equals
`terminal_width − _chrome_width()`.
**`AT-R11`** — the canvas **paints map content**: cells belonging to `#map-canvas`'s own region carry
node text. *Oracle is region-clipped to the widget under test.*

### HLR-R05 — complete legend *(US-R05)*

**HLR-R05.** The help surface **shall** present every binding of the active scope, and **shall not**
drop any binding without declaring it.
*Validation: test.* *Touched symbols: `mapper/screens/help.py::HelpScreen`.*

- **LLR-R05.1.** The bindings region **shall** be scrollable, so content taller than the viewport is
  reachable rather than discarded.
  *TC-R24.*
- **LLR-R05.2.** The set of bindings the panel presents **shall** equal
  `set(keymap.bindings_for(scope))` by set equality, with the expected set **derived from `keymap`**
  and never hand-listed.
  *TC-R25, TC-R26.*

**`AT-R12`** — pressing the real `?` on a map, the presented binding set equals
`bindings_for(SCOPE_MAP)` — **at three terminal sizes**, including one short enough to force scrolling.
**`AT-R13`** — the same holds for a second scope (home), so the requirement is not satisfied at one
screen's boundary.
**`AT-R14`** — **the oracle's own guard.** The assertion **shall** be region-clipped to the
`HelpScreen` widget subtree. *`HelpScreen` is a `ModalScreen` with `background: #000000 70%`, so an
unclipped read of the compositor composites `MapScreen`'s keybar through the translucent backdrop and
counts `m cobertura` as a legend row — measured. An oracle that reads another widget's pixels is not
a painted-result oracle.*

---

## 4 · Declared mutations (C-40, authored now, executed at each increment)

Every predicate above owes a mutation that reddens it, and — per batch 1's main lesson — the set
includes at least one **plausible weaker implementation**, not only deletion.

| Predicate | Deletion arm | **Plausible-weaker arm** (the one that matters) |
|---|---|---|
| `AT-R01` cycle refused | remove the `find_cycle` call | **detect only self-loops** (`parent_id == child_id`) — passes a naive test, misses `a→b→c→a` |
| `AT-R02` message names the cycle | return a fixed string | **name only the first node** — reads correct, loses the path |
| `AT-R03` acyclic still loads | — | **refuse any graph with a re-visited node**, which flags a legitimate diamond (two parents) as a cycle: a *false* refusal, and C-53 prices that as high as passing wrong work |
| `AT-R04` depth safe | restore recursion | **raise the recursion limit** instead of removing recursion — green to 500, dead at 5000, and it moves the crash rather than fixing it |
| `AT-R06`/`AT-R07` field integrity | remove coercion | **`str(v)` for every value including containers** — `str({})` is truthy, so the miscount survives with the suite green |
| `AT-R09` coverage unchanged | — | **count every field as missing** — passes `AT-R07` while destroying the figure |
| `AT-R10` layout | remove the CSS rule | **`width: 1fr` on the rail** — on-screen and disjoint, but it steals half the canvas |
| `AT-R12` legend complete | remove scrolling | **raise `max-height` to a number that fits today's 27** — green now, silently re-broken by the next binding added |
| `AT-R14` oracle clipped | — | **read the whole compositor** — the arm that must show the oracle itself can fail |

---

## 5 · Increment plan

| Inc | Content | SOURCE files | n | ATs |
|---|---|---|---|---|
| 1 | S-01a cycle refusal | `mapper/model.py`, `mapper/mermaid.py`, `mapper/store.py` | 3 | `AT-R01`, `AT-R02`, `AT-R03` |
| 2 | S-01b depth safety | `mapper/views/radial.py`, `mapper/views/outline.py`, `mapper/views/layered.py` | 3 | `AT-R04`, `AT-R05` |
| 3 | S-02 field integrity | `mapper/store.py`, `mapper/model.py`, `mapper/app.py` | 3 | `AT-R06`, `AT-R07`, `AT-R08`, `AT-R09` |
| 4 | S-07 + S-08 | `mapper/app.py`, `mapper/screens/help.py` | 2 | `AT-R10` … `AT-R14` |

Serial: Inc-1 and Inc-3 both touch `store.py` and `model.py`; Inc-3 and Inc-4 both touch `app.py`.
**0 of 6 pairs parallelisable.** Every increment is within the ≤4 source-file budget.

**Ledger.** `post = base − D + A`, base = **245 collected** (`pytest -q --collect-only`). Deletions
expected: **0** — this batch adds behaviour and removes none, so any `D > 0` needs a named predecessor.

---

## 6 · Traceability

| US | HLR | LLR | AT | TC |
|---|---|---|---|---|
| US-R01 | HLR-R01 | `LLR-R01.1`, `LLR-R01.2`, `LLR-R01.3`, `LLR-R01.4`, `LLR-R01.5` *(A-2)* | `AT-R01`, `AT-R02`, `AT-R03`, `AT-R03b` *(A-4)*, `AT-R15` *(A-2)* | `TC-R01`, `TC-R02`, `TC-R03`, `TC-R03b`, `TC-R04`, `TC-R04b`, `TC-R05`, `TC-R05b`, `TC-R06`, `TC-R06b`, `TC-R07`, `TC-R08`, `TC-R08b`, `TC-R09`, `TC-R09b`, `TC-R27`, `TC-R28` |
| US-R02 | HLR-R02 | `LLR-R02.1` *(A-6)*, `LLR-R02.2`, `LLR-R02.3` | `AT-R04`, `AT-R05`, `AT-R16` *(A-6)*, `AT-R16b`, `AT-R17` | `TC-R10`, `TC-R11`, `TC-R12`, `TC-R13`, `TC-R14`, `TC-R29`, `TC-R30`, `TC-R31`, `TC-R32` |
| US-R03 | HLR-R03 *(A-7, A-9)* | `LLR-R03.1`, `LLR-R03.2`, `LLR-R03.3`, `LLR-R03.4`, `LLR-R03.5` | `AT-R06`, `AT-R07`, `AT-R07b` *(A-7)*, `AT-R07c` *(A-7)*, `AT-R08`, `AT-R09` | `TC-R15`, `TC-R16`, `TC-R16b`, `TC-R17`, `TC-R18`, `TC-R19`, `TC-R20`, `TC-R20b`, `TC-R20c`, `TC-R21`, `TC-R33`, `TC-R33b`, `TC-R34`, `TC-R35`, `TC-R37`, `TC-R38` |
| US-R04 | HLR-R04 *(A-10)* | `LLR-R04.1` | `AT-R10`, `AT-R10b`, `AT-R11` | `TC-R22`, `TC-R23` |
| US-R05 | HLR-R05 | `LLR-R05.1`, `LLR-R05.2` | `AT-R12`, `AT-R13`, `AT-R14` | `TC-R24`, `TC-R25`, `TC-R26`, `TC-R36` |

> **Late-registered ids (merge-gate finding `M-1` / `PM-2`).** Four ids existed on disk with no
> row here: **`AT-R17`** (`resolve_document` survives a depth-5000 chain — US-R02), **`TC-R36`**
> (which declaration governs the help dialog's height — US-R05, added for review finding `F2`),
> **`TC-R37`** (an unparseable sidecar is refused in Spanish, not raised raw — US-R03) and
> **`TC-R38`** (the `notify` markup census — US-R03, and it also discharges backlog `B-07`/`B-10`).
> `AT-R03b`, `AT-R10b`, `AT-R16b`, `TC-R33b` are likewise now counted.
> 
> **This is `G5(b)` recurring.** The increment-3 re-gate raised exactly this defect about exactly
> this table, it was discharged, and increment 4 plus the close-out fold reintroduced it — the
> third instance in this batch of *the work was done and the record was not landed*. **The count
> above is therefore no longer maintained by hand**: it is the output of a walk over
> `tests/test_repair_*.py` collecting every `test_at_r*` / `test_tc_r*` definition, and it is
> **22 AT · 48 TC**. A hand-maintained census is the defect this batch exists to stop, and this
> table was the last one still hand-maintained.

> **Increment 3 id reallocation (condition C5, completed at the re-gate — finding `G5`).**
> `TC-R22` and `TC-R23` were originally allocated to increment 3 and **collided with the ids
> `LLR-R04.1` owns above.** They were renumbered in place to `TC-R33` and `TC-R34`; `TC-R35`
> was added as A-3's gate when review finding `F1` established the traversal was dead. The
> US-R04 row's `TC-R22`/`TC-R23` are therefore **free and still allocated to increment 4** —
> which is the whole point of the renumbering. `TC-R33` and `TC-R33b` are **regression pins,
> not gates** (C-40's corollary): the walk they once certified no longer exists, so no
> traversal defect can redden them, and they earn their place by pinning that removing it
> changed no observable value. `TC-R35` is the gate.

**5 stories · 5 HLR · 16 LLR · 22 AT · 48 TC.** Every id is enumerated individually — **the previous
revision of this table used en-dash ranges (`TC-R01 – TC-R09`) while asserting in the same breath
that no ranges appeared in the document.** A range is not a range to an id-scanner (C-56), and an
en-dash range is no more scannable than a dotted one; the claim and the table now agree.

Every AT is realisable as **exactly one** on-disk node driving the whole chain (C-18); none is
"covered in parts".

---

## 7 · Requirement amendments (recorded Before → After)

### A-1 · `LLR-R01.4` — the sink class is enumerated, not named

**Before:** *"`MapScreen.refresh_canvas` and `HomeScreen.on_mount` **shall** each render a non-fatal
notice … for **any** exception raised by load or by a renderer — scoped to the **sink class**, not to
the two exception types this batch happens to know about."*

**After:** *"**Every** screen that renders a `Graph` it did not itself validate **shall** render a
non-fatal notice instead of propagating, for **any** exception raised by load or by a renderer. The
set of such screens **shall** be derived from the tree, not enumerated in this requirement."*

**Why.** The requirement scoped the *exception type* to a class but left the *sink set* as two named
symbols — and a third sink existed. `_ImportPreviewScreen.refresh_canvas` (`mapper/app.py:721`) renders
a graph from `import_csv.preview_csv`, which **never passes through `mermaid.parse`**, so the refusal
LLR-R01.2 builds provably cannot reach it. Both the implementer and the reviewer reproduced the
identical `RecursionError` through a 3-row CSV with a circular `parent` column.

This is the batch-1 §2.1b shape appearing **inside the requirement written to prevent it**: I scoped
one axis correctly (the exception type) and left the other axis (the sink set) hand-listed — which is
control **C-31** applied to a requirement rather than to a test. The lesson generalises: *naming any
set by hand in a requirement is the same defect as hand-listing a test's input set.*

### A-2 · New `LLR-R01.5` — never write what cannot be read

**New.** *`MapStore.save` **shall** refuse a `Graph` whose `find_cycle()` is non-`None`, with the same
Spanish message `LLR-R01.3` produces.*

**Why.** `LLR-R01.2` made the store's **read** side stricter than its **write** side, and the asymmetry
is worse than the original defect for one specific case. `_ImportPreviewScreen.action_save`
(`mapper/app.py:743`) still persists a cyclic preview graph; the very next load — the one `action_save`
itself triggers — raises, so the file becomes a **permanent poison pill**: listed in the sala with 0
nodes, with no in-app route to repair it. **On `master` that file at least loaded.**

**Disposition:** implemented in **Inc-3**, which already opens `store.py` and `model.py`. Recorded here
rather than carried, because a repair batch that ships a new way to create an unopenable file has not
finished its job. *Verification: `TC-R27` (save refuses), `TC-R28` (the CSV round-trip no longer
produces an unloadable file), `AT-R15` (a well-formed graph still saves — the discriminating negative).*

### A-3 · `LLR-R02.1` — `resolve_document` is named as out of scope, with its reason

**Added, informative:** `mapper/model.py:108 resolve_document` recurses over the parent chain and sits
**outside** `mapper/views/`, so LLR-R02.1's AST walk does not reach it. **Two independent reviewers
flagged it** — a convergence worth recording rather than rediscovering.

It is unreachable via `mermaid.parse` now that cycles are refused, but **reachable from a
`preview_csv` graph**, which is exactly the door A-1 and A-2 exist for. Assessed in **Inc-3**, which
opens `model.py`. If it is left recursive, that is a decision with a reason, not an omission.

### A-4 · `AT-R03` — the diamond assertion, restated to what is satisfiable

**Before:** *"an acyclic map **still loads** … a diamond still loads."*

**After:** *"`find_cycle()` **shall** return `None` for a diamond, **and** the parser's refusal of a
diamond **shall** remain `ParseError` and specifically **not** `MermaidError`."*

**Why.** Verified against `master`: `mermaid.py:83-86` has refused multiple parents as out-of-MVP-scope
since long before this batch, so the literal wording was **unsatisfiable**. The restated form is
stronger than a weaker substitute — its second conjunct is what proves the new cycle rule has not
widened into a *false* cycle claim, which is the false-refusal property `AT-R03` exists to protect.

### A-5 · §4 — a census row that was vacuously true

**Before:** *"every existing `except ParseError` still catches the new refusal — no caller is bypassed."*

**After:** *"**no incumbent `except ParseError` handler exists** anywhere in `mapper/` or `tests/`;
`MermaidError` subclasses `ParseError` to keep the parser's error family coherent, not to preserve
callers. `MapStore.load` translates **only** `MermaidError`, so the Spanish-message guarantee is
**cycle-only** — an unsupported-syntax `ParseError` still surfaces in English, unchanged from `master`."*

**Why.** The original row was written by the orchestrator and is **vacuously true**: there was nothing
to preserve. It carries no behavioural risk, but it would let a future reader believe a compatibility
check was performed that had nothing to check — the same family as an input set that omits the case
that would fail it.

### A-6 · `LLR-R02.1` — scope the traversal set by SURFACE, not by directory

**Before:** *"Every graph traversal **in `views`** shall be iterative or explicitly depth-bounded. The
set of traversals is derived by an AST walk **for recursive functions in `mapper/views/`**…"*

**After:** *"Every recursive traversal **of a `Graph`, anywhere in `mapper/`**, shall be iterative or
explicitly depth-bounded. The derivation's root is the **traversal surface** — every module that walks
a `Graph` — and is derived from the tree, never named in this requirement."*

**Why — and this is the third instance of one mistake.** The AST derivation was correctly *derived*
within its root, and its root was **hand-picked by me**. `mapper/widgets/rail.py:59-66`
(`OutlineRail.visible_rows`'s inner `walk`) is a recursive traversal of the same `Graph`, one frame per
level. Executed, with a positive control:

```
POSITIVE CONTROL depth 3 -> 4 rows
  depth  500: OK, 501 rows
  depth 5000: *** RecursionError ***
```

It runs inside `OutlineRail.render()`, which Textual's compositor calls — **not** inside
`MapScreen.refresh_canvas`'s `try/except`, which wraps only `renderer.render(...)` (`app.py:1328-1336`,
read). So it escapes the message pump exactly as S-01a did, and the rail is composed on every map.

**The pattern, recorded because it is now a pattern.** Three times in this batch I bounded a set by
hand and the omitted member was the live one:

| # | The set I bounded by hand | What was outside it |
|---|---|---|
| A-1 | the *sink set* of `LLR-R01.4` — two named screens | `_ImportPreviewScreen`, fed by the CSV door that bypasses the parser |
| A-5 | the `except ParseError` census | the set was **empty** — nothing to preserve |
| **A-6** | the *traversal root* of `LLR-R02.1` — the `views/` directory | `widgets/rail.py`, which crashes outside every guard |

**C-31 is normally read as a rule about a test's input set. All three of these are the same defect one
level higher: a set bounded by hand inside a REQUIREMENT.** A derived probe with a hand-picked root is
not a derived probe — it is a hand-picked answer with a derivation wrapped around it, and it reports an
empty result with the same confidence either way.

### A-7 · `HLR-R03` — the text set is derived from the model, not bounded at `Ficha.fields`

**Before:** *"Every value in **`Ficha.fields`** shall be a `str` after load…"*

**After:** *"Every `Ficha` attribute the model declares as text shall hold a `str` after load — **the
set derived from `Ficha`'s own field annotations**, never named in this requirement…"*

**Why — and this is the FOURTH instance of the pattern A-6 recorded.** `Graph.search_hits` joins
`node.ficha.title`, `.meta` and `.notes` into one string alongside the field values. A non-string in
*any* of them raises the identical `TypeError` by the identical mechanism, so bounding the fix at
`fields` repairs one member of a set and leaves its siblings broken. Executed, with a control:

```
CONTROL: everything well-formed        load OK · search_hits OK ['root','a'] · coverage (2,2)
fields.D = int 20260826                load OK · search_hits RAISES TypeError · coverage (2,2)
title    = int 12345                   load OK · search_hits RAISES TypeError
meta     = float 3.14                  load OK · search_hits RAISES TypeError
title:   (bare key -> YAML null)       load OK · search_hits RAISES TypeError
meta:    (bare key -> YAML null)       load OK · search_hits RAISES TypeError
state    = int 7                       load OK · search_hits OK   · coverage (2,2)
```

**`state` is the discriminating negative and it is why the set must be DERIVED rather than widened
by hand.** It is the one text attribute no consumer joins, so a fix shaped to "the attributes that
break today" would be a hand-bounded set with a derivation wrapped around it — A-6's exact
criticism. Deriving from `Ficha.__dataclass_fields__` covers `state` uniformly without my having to
decide whether any consumer will ever read it.

**The bare-key rows are the realistic shape.** `_build_sidecar` + `yaml.safe_dump` always quote an
empty string, so mapper's own writer cannot produce them; a human editing `_nodos.yml` and leaving
`title:` empty produces `None`, and US-R03's premise is a sidecar *"handed to you by a colleague"*.

**Disposition:** implemented in **Inc-3**, which already owns `store.py`. It widens no file set — the
same loop in `_graph_from_sidecar` — and the cost is one derived tuple instead of one literal.
*Verification: `AT-R07b` (non-string and bare-key `title` survive `search_hits`), `AT-R07c` (the
`state` control), `TC-R15`/`TC-R16` extended over the derived attribute set.*

### A-8 · `AT-R07` — a container DENIES the map today; it does not miscount

**Before:** *"`AT-R07` — **the miscount regression.** A sidecar whose only value for a required field
is a container loads, and `coverage()` reports that field as missing."*

**After:** the acceptance text is unchanged — it describes post-fix behaviour and remains correct —
but it is relabelled **the container regression**, and the pre-fix cause is recorded.

**Why.** §1 reports S-02 as *"loads clean … and `coverage()` returns `(2, 2)`"*, which is **true for
the scalar case and false for the container case**. Executed:

```
fields.D = dict {}       load RAISES ProgrammingError: Error binding parameter 4: type 'dict' is not supported
fields.D = list [1, 2]   load RAISES ProgrammingError: Error binding parameter 4: type 'list' is not supported
notes    = list [1, 2]   load RAISES ProgrammingError: Error binding parameter 7: type 'list' is not supported
```

`MapStore._reindex` binds ficha values straight into SQLite, which cannot bind a `dict` or a `list`.
So pre-fix a container-valued field **denies the whole map** — strictly worse than the miscount, and
`F-M5`'s shape, which `LLR-R03.5` exists to refuse.

**Why it matters beyond bookkeeping: `AT-R07`'s pre-fix RED would have been recorded with the wrong
cause.** The node does go RED before the fix, so a careless reading confirms the requirement while
the mechanism is a `ProgrammingError` at load rather than a wrong coverage number — C-40's *"a
typo'd mutation also fails, for the wrong reason"* applied to the counterfactual itself.

**The fix design is unaffected.** Decision D3 rejects coercion for containers because `str({})` is a
truthy string that would survive as content; that reasoning stands. What changes is the claim about
what is being repaired: **the container case is a repaired crash, the scalar case is a repaired
miscount, and they are different defects sharing one fix.**

**Disposition:** closed in **Inc-2b**, not carried. A repair batch whose subject is *"depth must not
kill the application"* cannot ship a recursive traversal that kills the application at depth 5000.
*Verification: `TC-R29` (the widened derivation, RED on today's tree before the fix), `AT-R16` (the
rail survives depth 5000 through the composed screen, not through a direct call).*

---

### A-9 · `HLR-R03` — one owner of "what is missing", and it is `missing_required`

**Recorded late.** Increment 3 allocated this id and described the change in its packet, but never
wrote the amendment here. Found at the increment-4 close while discharging re-gate finding `G5`,
which was the same omission one row down in §6's traceability table.

**Before:** `Ficha.required_coverage` re-derived *"what is missing"* with its own bare truthiness
test, while `Ficha.missing_required`'s docstring already described itself as *"the single owner of
what is missing"*.

**After:** `required_coverage` **delegates** to `missing_required`. The docstring's claim becomes
true rather than aspirational.

**Why.** The two predicates agreed on every input **except a whitespace-only value**: the worklist
called it missing, the coverage figure counted it documented. That is precisely the quiet inflation
`US-R03` exists to stop, sitting inside the function whose own docstring claimed to prevent it.

**Why no assertion over output could have found it.** On every other input the two expressions are
the same set counted from opposite ends, so restoring the duplication leaves every behavioural test
green except one. This is the **structural rider** in the flow's §Artifact-homes section, met in the
field: a duplicated predicate is guarded by asserting the shape — that the predicate is called from
the one function that owns it — never by comparing what the two produce. Battery arm **`M8`**
reverts the delegation and reddens exactly one node, at its whitespace-only row.

**Scope note.** `mapper/screens/coverage.py` and `mapper/widgets/inspector.py` both consume
`required_coverage`, so a whitespace-only field now reads as missing there too. That is the intended
direction — they now agree with the worklist — and it is a behavioural change in files increment 3
did not open. *Verification: `test_coverage_never_counts_an_unreadable_field_as_documented`, plus
`tests/test_model.py`'s existing consumers.*

---

### A-10 · `LLR-R04.1` — the touched symbol is `MapperApp.CSS`, not `MapScreen.CSS`

**Before:** *"**LLR-R04.1.** `#map-rail` **shall** declare a width equal to `rail.RAIL_WIDTH` … 
*Touched symbols: `mapper/app.py` `MapScreen.CSS` `#map-rail`.*"*

**After:** the requirement statement is unchanged. Only the touched-symbol citation changes:
***Touched symbols: `mapper/app.py` `MapperApp.CSS` `#map-rail`.***

**Why — the premise was false and executing it is what revealed that.** `MapScreen` declares **no
CSS block at all**. The sibling `#map-canvas` and `#map-inspector` rules that `#map-rail` must sit
beside live on `MapperApp.CSS`. Adding a second stylesheet to `MapScreen` for a single rule would
fork the convention for no gain, so the rule joined its siblings and the **spec** was corrected.

```
CSS in MapScreen.__dict__ : False
MapScreen.CSS repr        : ''          <- inherited from textual.screen.Screen
Screen.CSS repr           : ''
#map-rail in MapperApp.CSS: True
```

**Found by `TC-R22` failing on its first run against the real tree**, which is the argument for
C-43's *execute the premise, do not read it*: the citation was plausible, specific, and wrong.

**A second lesson, from the correction rather than the defect.** The first attempt to guard this
asserted `not hasattr(MapScreen, "CSS")` — which is **False**, because Textual's `Screen` base
defines `CSS = ""` and the name resolves to an inherited empty string. That is **C-15's
inherited-attribute trap verbatim**: existence is satisfied while denoting the wrong object. The
honest predicate is `"CSS" not in MapScreen.__dict__`, and it is written into `TC-R22` with the
reason, so the next reader does not re-derive it.

*Verification: `TC-R22` (the CSS literal and `rail.RAIL_WIDTH` agree, and `MapScreen` still declares
no CSS of its own), `TC-R23` (the declared width is the width actually painted). Battery arms `L1`
(rule deleted, 5 RED), `L2` (`width: 1fr`, 4 RED), `L3` (off by one, 4 RED).*
