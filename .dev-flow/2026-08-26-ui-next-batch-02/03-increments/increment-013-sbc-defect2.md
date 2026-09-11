# Increment 013 — `S-B(+C)` part 1 of 2 · **defect 2**: the canvas header charge is per renderer

**Status: the `S-C` half is complete and witnessed. The `S-B` half is NOT started** — outline's
F2 per-row ceiling, walk cost, F7 residue and the AGREE-1 floor remain. Labelled partial rather than
delivered as if whole.

Defect 2 lands first because the coupling is **directional**: it sets the `h` that outline's `_fit`
spends, so fixing outline's cut against a wrong `h` and re-fixing when defect 2 landed would open the
same seam twice.

## The pre-gate table

`MapScreen._canvas_size` charged `layered.header_rows(...)` **unconditionally** — no renderer branch
— while `refresh_canvas` picked the renderer separately. So outline and radial were priced with
layered's header.

| w | charged (`layered.header_rows`) | **layered's own row 0** | outline's row 0 | radial's row 0 |
|---:|---:|---:|---:|---:|
| 20 | 3 | **3** | 1 | 3 |
| 24 | 3 | **3** | 1 | 2 |
| 28 | 3 | **3** | 1 | 2 |
| 34 | 2 | **2** | 1 | 2 |
| 40 | 2 | **2** | 1 | 2 |
| 50 | 2 | **2** | 1 | 1 |
| 60 | 2 | **2** | 1 | 1 |
| 80 | 2 | **2** | 1 | 1 |
| 100 | 2 | **2** | 1 | 1 |
| 118 | 2 | **2** | 1 | 1 |

**THE BOLD COLUMN IS THE LOAD-BEARING ROW OF THIS TABLE.** `layered.header_rows` agrees with
layered's own first line at **all ten widths**. That is what makes the other two columns a *finding*
rather than instrument error — an arm that only showed outline differing from layered could not tell
*"outline is overcharged"* from *"the instrument disagrees with the charge"*.

**Outline is overcharged at every width in the sweep** — by 2 at 20–28, by 1 from 34 up. Each
overcharged row is a body row the region could have shown and the renderer was never told about.

Measured with `Console.render_lines`, the instrument `outline._fit` and `layered.header_rows` already
use. Never `ceil(cells / w)`, which is `B-61`.

## What changed

- **`mapper/views/outline.py`** — `_header_line()` extracted so `_rows` and the new `header_rows`
  come off **one** helper (layered's own note: two copies of a header's shape drift). `header_rows`
  measures that line, with a signature matching `layered.header_rows` exactly so the caller needs no
  special case. `graph` and `w` are unused *here* and deliberately kept: a narrower signature would
  push the branch back to the call site.
- **`mapper/app.py`** — `_header_rows` routes through a new `_header_rows_for`, identity dispatch
  matching `_painted_ids_for`, `LookupError` for unregistered.

## The declared residue — radial

Radial is overcharged too, but `views/radial.py` is **S-D's** file and registering its charge here
would breach the cap. Per ruling, the hole is **stated in code** rather than omitted — this batch's
own `AT-058` doctrine applied to a *charge* instead of a *declaration*. Radial keeps layered's
number, the fallback says so and names **S-D as its closer**, and two arms pin it so
**S-D's fix reddens them**. The residue cannot be closed silently or forgotten loudly.

## Mutation evidence — and my first arm set could not fail

```
BASELINE  36 passed

M-REV   dispatch reverted to layered      KILLED   1 failed, 35 passed
M-CONST outline charge constant           KILLED   7 failed, 29 passed
M-RAISE unregistered defaults             KILLED   1 failed, 35 passed
RESTORES VERIFIED byte-identical · ALL KILLED
```

**Both of the first two SURVIVED the first 28 arms, and that is the finding worth keeping:**

- **`M-REV`** — the arms tested the module-level charges and `_header_rows_for` *in isolation*, so
  reverting `_header_rows`'s **body** to layered-everywhere left the dispatch present, correct, and
  **uncalled**, with 28 green arms. This batch's `P1` lesson exactly: trigger-independence is not
  discriminating power. Fixed by an arm that drives `_header_rows` and asserts the number came from
  the branch it names.
- **`M-CONST`** — outline's header is 18 cells, so it prices at **one row at every width in the
  ten-width sweep**, and `return 1` passed all of them. That is control **20** in this batch's own
  catalog: *a parametrization that samples one failure mode tests one failure mode.* Fixed with a
  narrow-width regime, plus a **meta-arm** asserting those widths still produce a wrap — so the
  regime cannot silently stop exercising it.

## The strict/degrading asymmetry — fired, not foreseen

I copied `_painted_ids_for`'s strict shape wholesale, and **`TC-R08` caught it**: it installs a
renderer that is not one of the three and asserts the app still paints *"no se pudo dibujar el
mapa"*. **Both of its parameter cases failed.**

`_canvas_size` runs **before** `refresh_canvas`'s guard, so my `LookupError` escaped the one path
`LLR-R01.4` ratifies as survive-anything. **The pattern transferred; the consequence did not** — a
declaration that raises costs a numeral, a *charge* that raises costs the whole picture. That is why
`frozenset()`-legitimacy makes raising right for `painted_ids` and wrong here.

Resolved by splitting them deliberately: `_header_rows_for` stays **strict** (an absent charge is a
code defect, pinned by its own arm), and `_header_rows` **degrades** to layered's charge inside the
drawing path — a wrong row budget on a frame that is about to paint a failure notice anyway. A third
arm pins the asymmetry itself, so anyone making the two symmetric again reddens it.

## Two census arms fired on the way through, and both were right to

Neither was a stale pin; both are controls doing their job, and both are recorded because a bumped
pin with an unexplained reason is a pin that has stopped working.

1. **`test_tc_a3_no_source_file_is_invisible_to_the_census`** — my new test module existed on disk but
   was **untracked**, so a git-derived census could not see it. Staged; the arm is exactly the guard
   against a test file that runs locally and is invisible to every derivation.
2. **`test_tc_a3_the_census_cardinalities_are_PINNED`** — 61 → **62** arg-ful `render(...)` call
   sites. Itemised: `+1` for `tests/test_canvas_header_charge.py::_first_line_rows`, which renders
   each renderer to measure the physical rows its own first line occupies. It cannot share an
   existing site — every other arg-ful site renders to check **content**, this one renders to price
   **geometry**, and a helper returning a finished picture would already have spent the width this
   arm measures at. **Derived mechanically**, not counted by eye: exactly one `.render(` in the
   module.

The arm's message says to update *"the pin AND the module map together, or one of them is stale"*.
Checked: `docs/ARCHITECTURE.md` carries the **interface contract**, not this count, and the
historical figures (23, 27, 32) live in increment records, which are point-in-time and must not be
retro-edited. **The test pin was the only live copy**, so nothing else went stale.

## A regime split the narrow widths forced, and it is a finding

Driving the equality oracle at narrow widths **fails**, and not because the charge is wrong:
`_fit_declared` **widens** `rows[0]` with the `fuera de vista` declaration when rows are hidden, so
the renderer's first emitted line is the *declaring* header while the charge prices the *bare* one.

The charge is right to price the bare header. `_canvas_size` runs **before** the renderer and hands
it an `h`; the widening then happens inside that budget, where `_fit` prices every row physically and
drops one to make room. A charge that anticipated the widening would be pricing a frame that does not
exist yet — and would need the fit whose input it is computing.

So the two regimes assert different properties, and each says which oracle it is **not** using.

## Gates

| Gate | Result |
|---|---|
| Default lane (`-m 'not slow'`) | **1037 passed, 19 deselected, 3 xfailed** in 248.77 s · exit 0 |
| Slow lane (`-m slow`) | **19 passed, 1040 deselected** in 52.86 s · exit 0 |
| All markers (`-o addopts=`) | **1056 passed, 3 xfailed** in 310.47 s · exit 0 |
| Ruff, whole repo | **27** — unchanged from this batch's previous close |
| Ruff, changed files in place | 1 finding: a pre-existing `F401` on `re` in `app.py`, present at `HEAD` too |

Lane arithmetic: 1056 + 3 = **1059**; 1037 + 3 + 19 = **1059**; 19 + 1040 = **1059**. Three runs
partition the same collected set with no residue. Growth 1000 → 1037 is this increment's 37 arms.

### MY OWN RUFF GATE WAS BROKEN, AND IT RETROACTIVELY CORRECTS AN S-E CLAIM

The gate scanned `HEAD` blobs from a **flat temp directory** and the worktree files **in place**.
Import-sorting classification depends on location, so — measured on three files — **the same bytes
yielded `I001` in the temp copy and not in place.** That inflates the *baseline*, and an inflated
baseline can **mask a genuinely added finding**, which is the one thing the gate exists to catch.

**Correction to the record:** the *"REMOVED 1 × `I001`"* I reported as evidence at `Inc-REPAIR` S-E
was this artifact, **not** a real improvement. The S-E `ADDED 0` verdict still stands — an inflated
baseline cannot invent an addition — but the removal figure was instrument noise and I reported it as
a result.

Copying `pyproject.toml` beside the blobs was not enough (the temp `mapper/` has no `__init__.py`).
The fix is **symmetry, not accuracy**: both sides measured the same way, so the artifact cancels in
the set difference. That works for files with a baseline; a **new** file has none, so its
temp-context `I001` still reads as added — which is why the authoritative check here is the
**in-place** scan above, and `tests/test_canvas_header_charge.py` is clean in its real location.

Self-check: `C:\Users\jjgh8\clde\gate_selfcheck.py`.

## Still owed by this increment

The **S-B half**: F2 per-row ceiling · walk cost · F7 residue · outline's AGREE-1 floor
(`LLR-N06.3.5` remains OPEN). And the composited-frame question — *which terminal sizes turn the
mischarge into a visibly wrong row* — is scoped to this increment and **not yet answered**; the
pre-gate priced the charge, not the frame.
