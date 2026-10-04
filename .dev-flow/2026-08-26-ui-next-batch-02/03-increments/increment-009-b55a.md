# Increment B55a — outline declares what it hides, and stops holding a render its layout outgrew

**Cut:** `mapper/views/outline.py`, `mapper/app.py` — **2 source files** (A-94).
**Requirement:** `HLR-N06.3` via `LLR-N06.3.4` (`AT-056`/`TC-089`), `LLR-N06.3.5` (`AT-057`/`TC-090`),
`LLR-N06.3.6` (`AT-058`/`TC-091`).
**Protocol:** full, serial reviews, soft cap 3, terminal-boundary available at the cap.

## BLUF

`B-55`'s hole is that `outline` hides nodes and declares nothing. Closing it turned out to require
fixing something underneath first: **the canvas holds content rendered against a region that has
since grown**, so at four of eleven driven terminal sizes the outline is one line short with a blank
row beneath it. A declaration wired on top of that would have declared a node hidden that the canvas
had room to show.

**Order, fixed by ruling:** `AT-058` hazard → settle fix → `painted_ids` → both surfaces.

## 1 · Why the order is not negotiable

`app.py:1596-1603` catches **every** exception and returns `None`, and `None` reads as *"this view
declares nothing"* (`app.py:1569`, `:2142`), which `LLR-N06.3.3` makes mean *nothing is hidden*.
`Inc-B55` is what makes that seam reachable by more than one renderer. **It would silently swallow
`AT-056` and `AT-057` themselves** — a declaration that raised would present as a view with nothing
to declare, and both arms would go green over a broken feature. So `AT-058` lands first, or the
increment's own acceptance evidence is worthless.

## 2 · The diagnosis that re-centred this increment

Approved read-only at the pre-gate, before any design, because designing against the wrong mechanism
is the birth certificate of this batch's last three regressions.

Three candidates were tested **against each other**, not confirmed one at a time:

| hypothesis | verdict |
|---|---|
| `H1` the `lines[:h]` logical/physical cut | **not the cause** of the observed loss — at every loss size the held content fits the region exactly |
| `H2` `Static.update` / widget cropping | **REFUTED** — every line the widget holds appears on the frame |
| `H3`/`H4` the render used a stale, smaller `h` | **CONFIRMED** |

```
  terminal region_h  cs_h  held  resettled  gap  blank_tail
  (24, 20)        8     6     5          6    1           2
  (30, 16)        5     4     3          4    1           1
  (32, 16)        5     4     3          4    1           1
  (34, 14)        3     2     1          2    1           2
  (35, 14)        3     2     2          2    0           0
  (40, 16)        5     4     4          4    0           1
  (50, 16)        5     4     4          4    0           1
  (60, 20)       11    10     9          9    0           2
  (80, 24)       16    15     9          9    0           7
 (118, 34)       27    26     9          9    0          18
  (28, 14)        3     1     1          1    0           2
```

Exactly **one** line short at four sizes, **zero** at the other seven. The large blank tails at
`(80,24)` and `(118,34)` are legitimate: the outline is 9 lines and the canvas is taller.

### 2.2 · MY STATED SEAM WAS FALSE — corrected before a line was written

The first version of this section said `_declare_after_layout` (`app.py:1609`) *"repaints the
declaration and not the canvas content"*, and called that asymmetry the seam. **Reading the function
refutes it:**

- `app.py:1642` renders the **current** renderer at the **current** `_canvas_size()`.
- `app.py:1649` is `canvas.update(text)` — **the content IS repainted.**
- `app.py:1661-1663` is a **settle loop**: it re-schedules itself while `region != self._declared_for`
  and stops when the region stops moving, so *"nothing re-renders after the settle"* is also wrong.
- `on_resize` (`app.py:1665`) adds a second entry point, and its own docstring records that a SCREEN
  resize is not a CANVAS resize.

So the code already does the thing I proposed to add. **The observable stands** — `held < resettled`
at four of eleven sizes, reproduced in two independent probes — **but the mechanism does not**, and
the seam I named is not a seam.

**This is exactly the trap this pre-gate was approved to prevent, caught one step before the code.**
Designing the settle fix on the refuted story would have added a repaint next to an existing repaint
and left the four sizes red.

**Live candidate, NOT yet confirmed and NOT to be implemented against until it is:** `_canvas_size()`
subtracts a MEASURED header height (`app.py:1492-1495`), and that measurement is `layered`'s header
geometry. In `outline` mode the painted header is `◆ mapper · outline` — one row — while the
subtraction may still be priced for `layered`'s, which wraps at narrow widths. That would under-give
`h` by exactly one row in outline, at narrow widths only, which is the **exact shape** of the measured
gap: `1` line at `(24,20)`, `(30,16)`, `(32,16)`, `(34,14)` and `0` everywhere else. The docstring at
`:1495` already names charging a constant in either place as `B-61`.

> **REFUTED BY `02o` (independent diagnostic lane, 2026-09-10).** The candidate is TRUE AS A FACT —
> layered's header height IS charged regardless of view — and **structurally incapable** of explaining
> the gap: `gap = re - held`, both priced at the same `_canvas_size()`, so a wrong constant moves both
> equally and **cannot appear in their difference**. The gap is by construction a staleness measure.
> The real mechanism is a **stale final write**: `refresh_canvas` paints the canvas at `:2370`, then
> updates the strip at `:2425`; in outline the strip loses its `▽` token (36 cells → 17), unwraps from
> 2 rows to 1 at width ≤ 34, and `#map-body` gains a row **after** the canvas was painted. Nothing
> repaints. See `02o` §3 and the two-defect split in `state.json`.

**Superseded — owed before implementation:** confirm or refute that candidate by direct observation, and identify
what the settle loop's terminating pass actually rendered at. Until then the mechanism line in §2's
table reads `H3/H4 CONFIRMED AS AN OBSERVABLE, MECHANISM OPEN`.

### 2.1 · The KeyBar mirror — same law, both directions

`Inc-CRUMB` fixed a widget that kept an **auto-height computed from a render it had already
replaced**. This increment fixes a widget that keeps **content rendered against a layout it has since
outgrown**. They are the same law seen from opposite ends:

> **A widget must never be laid out from a render it replaced, nor left holding a render from a
> layout it outgrew.**

That pairing is the final form of the batch's geometry control: *measure what the operator reads AND
the geometry it stands in; either alone can lie.* In `Inc-CRUMB` the painted text was correct and the
geometry lied. Here the geometry is correct and the content lies. **An arm on either one alone passes
one of these two defects.**

## 3 · Evidence this increment owes — coordinator ruling, shared-path risk handled by evidence

The settle fix touches `app.py`'s layout path, which every view shares. It stays **inside** this
increment rather than splitting — splitting would hold `B55a` uncommitted behind a dependency, the
`Inc-4c` limbo shape — and the shared-path risk is discharged by three named obligations:

1. **The seven zero-gap sizes are the negative controls.** Frames **byte-identical pre/post fix** at
   every size where `gap = 0`, for **outline AND layered AND radial**. Tests-only, in scope.
2. **The stale-height inference becomes a measured invariant.** The diagnosis *inferred* the stale
   height from produced line count — it could not observe the `h` passed at the live call. Post-fix,
   `held == resettled` is asserted **directly at all eleven driven sizes**, converting the inference
   into an observation, per the diagnosis's own boundary statement.
3. **The left-open item stays open in the record until re-measured.** Whether `outline.py:161`'s
   logical/physical cut manifests at **any** size once the settle lands is **UNMEASURED**. It is
   re-measured *after*, and only then does the cut change ship or get dropped as non-manifesting.
   **A fix for a defect that no longer manifests is speculative code.**

## 4 · Acceptance, as ratified

`02n` rejected `AT-057` as first drafted — *"equal counts · zero disagreements"* was **green on the
shipped build**, satisfied by universal silence while 7 of 8 nodes were hidden. It corrected `AT-056`
and struck `35x14`, where nothing is lost. The coordinator then re-framed `AT-056` to the
operator-statable claim and demoted the rendering-correctness clauses to a pinned pilot arm.

| id | clauses | driven |
|---|---|---|
| `AT-056` | `PHYS-3` declaration matches a frame-derived hidden set · `PHYS-4` fixture non-degenerate, asserted first | `(30,16)` `(32,16)` `(24,20)` + controls `(50,16)` `(80,24)` |
| pinned pilot | `PHYS-1` nothing emitted the canvas cannot show · `PHYS-2` the cut is **maximal** (`lines[:0]` passes everything else) | same table |
| `AT-057` | `AGREE-1` both surfaces **speak** · `AGREE-2` equal · `AGREE-3` **right**, not merely equal | `(35,14)` `(30,16)` + control `(80,24)` |
| `AT-058` | unregistered renderer **raises**; layout failure still degrades to absent; the two produce **different frames** | unit + pilot |

Arms must be named `test_at056_*` / `test_at057_*` / `test_at058_*`. **The names are normative** —
`C-18` needs the `AT id → node` edge, and this batch already carries `AT-005`/`AT-006` with no node on
disk and therefore no way to verify them.

## 5 · Traceability

`§5.2`'s dual-traceability matrix was checked **before** editing: no generator script exists, no test
asserts row completeness, and the section's own note derives only the **count**, not the rows. It is
**hand-maintained**, so it was hand-edited — `AT-056`, `AT-057`, `AT-058` added to the `US-N06` row
with its observable outcome extended. Had it been generated, regenerating would have been the only
legal move: hand-editing a generated table is the two-registries defect.

## 6 · Pre-gate captures — taken on the PRE-FIX tree, before any code

All four are the "before" half of this increment's two-oracle evidence. Captured 2026-09-10 at
`258e83c`, one fixture (`legacy`), through the live screen.

- [x] **`C1` — `A-98` tripwire, pre-fix.** `painted_ids_exporters() == {'mapper.views.layered'}` —
  the pinned equality holds today. It must go **RED** the moment `outline` declares; repairing it
  means widening the pinned set **and amending its docstring**, never a `-k` exclusion.
- [x] **`C2` — the stale-geometry reproduction, and the negative controls it defines.**

  ```
    terminal region_h  cs_h  held   re  gap
    (24, 20)        8     6     5    6    1
    (30, 16)        5     4     3    4    1
    (32, 16)        5     4     3    4    1
    (34, 14)        3     2     1    2    1
    (28, 14)        3     1     1    1    0
    (35, 14)        3     2     2    2    0
    (40, 16)        5     4     4    4    0
    (50, 16)        5     4     4    4    0
    (60, 20)       11    10     9    9    0
    (80, 24)       16    15     9    9    0
   (118, 34)       27    26     9    9    0
  ```

  **LOSS (4):** `(24,20)` `(30,16)` `(32,16)` `(34,14)`.
  **ZERO-GAP negative controls (7):** `(28,14)` `(35,14)` `(40,16)` `(50,16)` `(60,20)` `(80,24)`
  `(118,34)` — these are the frames that must be **byte-identical pre/post** across outline, layered
  and radial.
- [x] **`C3` — `AGREE-1`'s pre-state, confirming `02n` independently.**

  ```
    outline  (35,14)  hidden=7/8  canvas_token=False  _unpainted_ids=None
    outline  (30,16)  hidden=6/8  canvas_token=False  _unpainted_ids=None
    outline  (32,16)  hidden=6/8  canvas_token=False  _unpainted_ids=None
    outline  (80,24)  hidden=0/8  canvas_token=False  _unpainted_ids=None
  ```

  Both surfaces silent at every size, including one hiding **7 of 8** nodes. This is why the first
  draft of `AT-057` was green on the shipped build.
- [x] **`C4` — `AT-058`'s pre-state.** `_unpainted_ids()` returns `None` for outline at `(80,24)`,
  where **nothing is hidden**, and the identical `None` at `(35,14)`, where **7 of 8 are**. The seam
  answers *"nothing to declare"*, *"not this view"* and *"the declaration broke"* with **one value**.
  That is the collision `AT-058` exists to break.

## 6.5 · The settle-arming cost — MEASURED, not handed to the reviewer as a question

I flagged repaint cost as a residual risk for the code review. The ruling was to measure it instead,
under `S-15` discipline: **work, not call count**, because `S-15` proved render cost is the thing that
explodes and the settle pass re-renders.

Driven on the `Inc-STRIPS` fixture — **4001 branches, 12002 nodes** — at the declared context and at
`80x24`. Decomposed rather than simulated, because pre-fix and post-fix cannot both run in one
process without editing the tree:

```
STRIPS fixture: 4001 branches, 12002 nodes      median of 5 repeats, wall seconds

  terminal  passes   A refresh_canvas   B one settle pass  post/pre
 (118, 34)       1             0.0148              0.0018     1.12x
           pre-fix ~ 0.0148s   post-fix ~ 0.0166s   added +0.0018s
  (80, 24)       0             0.0089              0.0012     1.00x
           pre-fix ~ 0.0089s   post-fix ~ 0.0089s   added +0.0000s
```

**Verdict: the delta is noise, and the measurement closes the question for free.** One settle pass
costs **1.2–1.8 ms** against a `refresh_canvas` of **8.9–14.8 ms** on the largest graph this batch
ships a bound for. The added work at the declared context is **+1.8 ms, about 12% of one repaint**,
and it is **bounded**: `_declare_after_layout` re-schedules only while the region CHANGED, so a
settled layout costs exactly one no-op pass. **No cheap guard is needed**, and adding one — arming
only when the strip content changed — would buy 1.8 ms at the price of a second mechanism to keep
correct, which is the trade `Inc-B55a` exists to stop making.

The settle pass is cheap *relative to* `refresh_canvas` for a structural reason worth recording:
`_declare_after_layout` repaints the canvas and the strip only, while `refresh_canvas` also rebuilds
the minimap, the rail, the inspector and the tab strip.

**Boundary.** Wall time in a headless `run_test` on one machine, one process, median of 5. It
measures the Python-side render and update work — **not** the terminal I/O a real session adds on
top — for THIS fixture at THESE sizes, and cannot speak for a differently shaped graph. **The
`passes` column is pause-dependent and is the weakest number here**: `0` at `80x24` means the
scheduled callback had not run when `pause()` returned, not that arming was skipped. The robust
figure is the **per-pass cost**, which is what the bound above is built from.

## 6.6 · The cost re-measured — and §6.5's number was measured in the wrong regime

Re-run on the current tree per ruling. **The first measurement was not wrong, it was BLIND**: the
`Inc-STRIPS` fixture is **12002 nodes**, above `outline`'s `MAX_RENDER_NODES` of **12000**, so
`_rows` short-circuits to `_degraded` and outline's whole path never ran. §6.5 priced a fixture the
expensive view refuses to render. A second regime was added at **11999 nodes** — the largest graph
`outline` will actually render, and its worst case.

```
median of 5 repeats, wall seconds                    BEFORE the P1 guard
regime                                 terminal   refresh    settle     added
A  12002 nodes, layered (_fit unused)  (118, 34)   0.0156    0.0015   +0.0015
A  12002 nodes, layered (_fit unused)   (80, 24)   0.0104    0.0012   +0.0012
B  11999 nodes, OUTLINE (_fit runs)    (118, 34)   0.3554    0.3325   +0.3325
B  11999 nodes, OUTLINE (_fit runs)    (80, 24)   0.3251    0.2774   +0.2774
```

**Regime A replaces §6.5's number like-for-like and it holds.** Regime B did not: a settle pass cost
a **full re-render**, roughly DOUBLING a repaint that already costs 0.36 s. Arming the settle from
`refresh_canvas` without a guard would have shipped that, and §6.5's "the delta is noise" would have
been a true sentence about the wrong fixture.

### The guard is `P1` itself, which is why it is not the second mechanism I argued against

`P1` says content and geometry agree at rest. If they **already** agree, the settle's re-render is
byte-identical and there is nothing to reconcile. So `_declare_after_layout` skips it when
`_canvas_size()` still equals the geometry the canvas's current content was rendered at
(`_rendered_for`). **The predicate skipped on is the same one the invariant asserts**, so the guard
cannot drift from the property it protects — unlike "re-render only when the strip changed", which
would have been a second rule to keep correct.

```
                                                     AFTER the P1 guard
A  12002 nodes, layered                (118, 34)   0.0149    0.0011   +0.0011
A  12002 nodes, layered                 (80, 24)   0.0100    0.0011   +0.0011
B  11999 nodes, OUTLINE                (118, 34)   0.3448    0.1527   +0.1527
B  11999 nodes, OUTLINE                 (80, 24)   0.3310    0.1498   +0.1498
```

**332 ms → 153 ms.** All 11 `P1` arms stay green, so the guard does not buy the time by weakening the
invariant.

### The residual 153 ms is the FEATURE's cost, not the settle's — and it is carried, not hidden

The remainder is not the re-render. It is `painted_ids` itself: `_pagination_text` calls
`_unpainted_ids`, which for outline now runs `_rows` over **every node**. Before `Inc-B55a` that call
returned `None` immediately, because outline declared nothing — which is precisely the hole `B-55`
names. **Closing `B-55` for outline costs a second full walk per frame**, ~150 ms on the largest
graph outline renders.

Not optimised here, deliberately. The obvious fix — memoise `_rows` per `(graph, state)` — is a
CACHE, and a cache is a second mechanism with its own staleness failure mode, in an increment whose
entire subject is two things disagreeing about one frame. The honest options are a shared per-frame
pass (forbidden here: `layered.painted_ids` records why a side-channel attribute set by `render` is
cross-contaminated by the export call site, which renders the same long-lived renderer at a different
size) or accepting the cost. **Carried to `Inc-REPAIR` with this measurement attached**, alongside
defect 2, so the two outline-geometry costs are priced together rather than one at a time.

**Boundary.** Wall time, headless `run_test`, one machine, median of 5, Python-side work only — not
the terminal I/O a real session adds. `branchy_graph` at these two sizes; `_fit`'s per-line cost is
wrap-dependent, so a differently shaped graph prices differently.

## 7 · Gate checklist — CLOSED

- [x] Pre-gate captures landed on the pre-fix tree (`C1`-`C4`, §6)
- [x] `AT-058` first, then the mechanism fix, then `painted_ids`, then both surfaces
- [x] Negative controls: `(35,14)`, `(40,16)`, `(50,16)` — the honest three, not the seven
- [x] `outline.py:161` re-measured post-settle; the cut change **ships**, measured not assumed
- [x] `A-98` tripwire RED→GREEN, pinned set widened **and its docstring amended**
- [x] Independent code review — **BLOCK, 2 HIGH**, folded
- [x] Security review — **SIGN-OFF, 0 HIGH**, its MEDIUM fixed

## 8 · Close

**Commits.** Source landed across seven commits as each stage was acknowledged —
`3920e06` (`AT-058`), `7a973df` (settle), `ff55ab6` (`painted_ids`), `f355499` (the P1 guard),
`45663b6` (canvas declaration), `a4862bf` (code-review fixes), `1ab87d8` (security fix) — plus this
close record. **That is not the two-commit shape** `Inc-CRUMB` used, where the work stayed
uncommitted until the gate. Stated rather than dressed up: the staged shape came from reporting at
each boundary, and it left every stage independently revertible, but it is a different shape and the
record should say which one it is.

**Evidence at close:**

```
default lane : 968 passed, 19 deselected, 3 xfailed   exit 0
all markers  : 987 passed, 3 xfailed                  exit 0
ruff SET     : 19 (file,rule) pairs / 27 both sides — SET-IDENTICAL, zero NEW/GONE,
               parse counts asserted, positive control fires
arms added   : AT-056 x10 · AT-057 x6 · AT-058 x3 · P1 x11 + x4 forced-trigger · pilot x10
mutants      : M0, M9, M10 byte-level with sha256 restores; M1, M2 in-process — all caught
```

**What this increment actually closed.** `B-55`'s outline vector: the view now declares what it
hides, on both surfaces, with the declaration and the cut sharing one pass so they cannot disagree.
Underneath it, a stale-write defect nobody had named, and a seam that answered "nothing to declare",
"not this view" and "the declaration broke" with one value.

**What it did not close, recorded rather than absorbed.** `AGREE-1` is OPEN at the empty-frame floor
(11 sizes enumerated in `state.json`). `radial` still declares nothing — `Inc-B55b`. Defect 2, the
`painted_ids` walk, `F2`'s per-row ceiling and `F7`'s triplicated sentence ride `Inc-REPAIR`.

### 8.1 · The ledger, honestly

Four of five comment claims the security review fired held up. The fifth did not, and it was the one
I was proudest of: the settle guard's `P1`-is-the-predicate claim was a **projection** of the
invariant onto two of its ten inputs, and the reviewer demonstrated `B-60` reintroduced through the
mechanism built to prevent it. The code review before it found that **deleting the entire settle fix
left the suite green** — an arm built trigger-independent and mistaken for one that discriminates.

Both were caught by the process built to catch them. That is the system working, not the system
being lucky — but the pattern holds across this increment as it has across the batch: **the
measurements survived; the explanations attached to them did not.**

