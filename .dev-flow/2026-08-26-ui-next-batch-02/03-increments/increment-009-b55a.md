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

**Owed before implementation:** confirm or refute that candidate by direct observation, and identify
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

## 7 · Gate checklist

- [ ] Pre-gate captures landed on the pre-fix tree
- [ ] `AT-058` first, then settle, then `painted_ids`, then both surfaces
- [ ] Seven zero-gap sizes byte-identical pre/post, three views
- [ ] `held == resettled` at all eleven sizes
- [ ] `outline.py:161` re-measured; cut change ships or is dropped **with the measurement recorded**
- [ ] `A-98` tripwire RED→GREEN, pinned set widened **and its docstring amended** (not a `-k` exclusion)
- [ ] Independent code review — serial
- [ ] Security review — serial
