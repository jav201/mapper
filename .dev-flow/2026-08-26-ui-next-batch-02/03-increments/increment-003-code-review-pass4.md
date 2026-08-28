# Increment 3 — Code Review, Pass 4 (narrow confirmation of fix round 3)

**Verdict: PASS. 0 HIGH.** All three pass-3 findings are DISCHARGED, both riders rule in
round 3's favour, and **this increment is ready to commit.**

Round 3 is the strongest of the four. Every headline number it published reproduces on an
independent instrument, the one claim it made about its own weakness (`N8` survived its
first pin) is honest and was closed by strengthening the pin rather than the mutant, and the
one thing it declined to fix is correctly a carry — measured, the increment makes that
latent defect's symptom *better*, not reachable.

| Item | Ruling |
|---|---|
| **1 · pass-3 F1** artifact scan | **DISCHARGED** — structural, probe-driven, cannot flip on a commit |
| **2 · pass-3 F2** header cost | **DISCHARGED** — the pin is a genuinely different instrument; every number reproduces |
| **3 · pass-3 F3** `B-60` / settle | **DISCHARGED** — terminates, bounded at 5 passes; all six sizes red pre-fix, green post-fix (1 MEDIUM) |
| **Rider A** — the new carry | **Correctly a carry.** The increment improves the symptom; it does not make the defect reachable |
| **Rider B** — `pytest-timeout` | **DISCHARGED** — dev-only, pinned, rationale true, `N9` red at 33 s |

Findings: **0 HIGH, 1 MEDIUM, 3 LOW.** None blocks.

## Method and harness

Two isolated exports, never the shared working tree:

```
$ tar --exclude=.git --exclude=__pycache__ -cf - . | (cd <scratch>/expN && tar -xf -)
$ cd <scratch>/expN && git init -q . && git add -A && git commit -q -m base
EXP5/EXP6 FILES: 194   UNTRACKED: 0          <- the POST-COMMIT state, which is item 1's case
```

Every mutation restored from a `cp` snapshot and proven by `sha256sum -c`. `git checkout`
was used once by mistake and immediately caught by the sha256 check (the export's index is
CRLF-normalised); all restores below are snapshot restores. **Shared tree verified unchanged
at the end: 34 status entries, identical to session start; no probe leaked.**

**Your own figures, corroborated by re-execution in the export:**

```
$ PYTHONUTF8=1 python -m pytest -q -m "not slow" -p no:randomly --durations=12
801 passed, 17 deselected, 3 xfailed in 126.46s          EXIT=0    zero FAILED lines
$ PYTHONUTF8=1 python -m pytest -q -m slow -p no:randomly
17 passed, 804 deselected in 29.90s                      EXIT=0

$ git diff --name-only 954f8f3 -- mapper/
mapper/app.py  mapper/keymap.py  mapper/views/layered.py
mapper/views/outline.py  mapper/views/state.py  mapper/widgets/rail.py      <- exactly six
```

---

# Item 1 — the artifact scan: DISCHARGED

## The widening is structural, and it cannot flip on a commit

Two clauses replace the strict-superset check, and they fail in opposite directions from
the one that broke:

- **the probe** (`tests/test_fold.py:249-258`) — creates `.dev-flow/_scan_probe.md`, asserts
  the `rglob` sees it, removes it in a `finally`. The probe is created at run time and is
  never tracked by construction, so this clause is **independent of tracking state by
  definition**, not by today's accident.
- **the instrument comparison** (`:268-272`) — `set(_tracked(".dev-flow/**")) <= set(artifacts)`.
  A commit can only add to the tracked side, and anything it adds is on disk and therefore
  in the `rglob` side too. The direction is monotone the right way; a commit can only
  strengthen it.

Executed in the fully-tracked export — the exact state that reddened pass 3's baseline:

```
$ PYTHONUTF8=1 python -m pytest -q -p no:randomly tests/test_fold.py::test_no_tracked_..._artifacts
1 passed in 1.49s                                        EXIT=0
probe present after run: NO
git status count: 0
```

And the whole lane is green in that state (801 passed above, 0 untracked). **Item 1's
defect is gone.**

## Probe hygiene — cleaned up, and a kill is diagnosable rather than silent

The `finally` covers the assertion path. For a mid-run kill, the arm's own leading guard is
the diagnostic:

```
$ printf 'scan probe\n' > .dev-flow/_scan_probe.md      # simulate a killed run
E  AssertionError: <...>\.dev-flow\_scan_probe.md already exists; a previous run leaked it
```

A leaked probe produces a **named failure on the next run**, not a silent pass. It is also
an untracked file in `git status`, so it is visible even without running the suite.

**No other census can mistake it for a real artifact.** The only other readers of `.dev-flow`
are `tests/test_repair_artifact_claims.py` (a fixed batch directory and `state.json`) and
`tests/test_repair_golden_census.py` (`state.json`) — neither globs. And the offender loop
recomputes `artifacts` *after* the `finally`, so the probe is never read for code points.

## The `fixtures/` / `maps/` globs catch a planted code point

Both mutants killed, both restores proven:

```
N2  U+200B planted in fixtures/anidado.mmd
E   AssertionError: [('fixtures/anidado.mmd', ['0x200b'])]              1 failed
N3  U+200B planted in maps/legacy.mmd
E   AssertionError: [('fixtures/anidado.mmd', ['0x200b']),
                     ('maps/legacy.mmd', ['0x200b'])]                   1 failed
    fixtures/anidado.mmd: OK      maps/legacy.mmd: OK      (sha256)

N1  the rglob half degrades to `git ls-files`
E   AssertionError: the rglob does not see an untracked artifact; it is the
    tracked sweep wearing a different instrument                        1 failed
    tests/test_fold.py: OK        (sha256)
```

`N1` is the load-bearing one: it dies **in the fully-tracked export**, which is precisely
where the old subset check could not have caught anything. The probe clause works in the
state that broke its predecessor.

I also tried the negative control — remove the `fixtures/`/`maps/` globs and plant the code
points — and got a better answer than expected:

```
E  AssertionError: the fixtures/maps half collapsed: []       tests\test_fold.py:264
```

The arm asserts that half non-empty on its own, so the widening cannot be silently removed
either.

**LOW-1.** The probe writes into the real repository during a test. Harmless today
(single-process, cleaned in `finally`, guarded on entry), but it is not `pytest-xdist`-safe:
two workers would race on `assert not probe.exists()`. Worth one sentence in the docstring
if parallel test execution is ever considered. Not a defect today — `xdist` is not
installed and `addopts` does not request it.

---

# Item 2 — the header cost: DISCHARGED

## The pin is genuinely a different instrument

The circular helper is **deleted, not renamed**. `grep -rn "_header_rows" tests/` returns
only `_header_rows_in_frame` (a new body) and calls to the product's `screen._header_rows`.
Traced, the two sides share nothing that computes a row count:

| | product (`layered.header_rows:473-483`) | pin (`test_overflow.py:296-306`) |
|---|---|---|
| builds the line | `_header_line(...).plain`, worst-case `unpainted` | `renderer.render(...).plain.split("\n")[0]` |
| **counts rows** | `Console.render_lines(Text(first), pad=False)` at `wrap_w` | scans `canvas_rows(screen)` for the prefix join matching the line |
| wrap width | `wrap_w`, passed in by the caller | **none — it does not wrap at all** |

The pin borrows the line's *content* (unavoidable: you must know what to look for) but the
quantity under test — the row count — comes from the compositor. The decisive proof is that
it now fails in **both** directions, which the `ceil`-vs-`ceil` helper could do in neither:

```
N4  product reverts to ceil(len / avail)          -> UNDER-charge caught
E   legacy  (28,30): charged 2 physical header rows against 3 in the composited frame (region 28x13)
E   anidado (28,30): charged 2 physical header rows against 3 in the composited frame (region 28x14)
N5  product wraps at w-2 instead of the measured width -> OVER-charge caught
E   legacy  (29,30): charged 3 physical header rows against 2 in the composited frame (region 29x13)
E   anidado (29,30): charged 3 physical header rows against 2 in the composited frame (region 29x14)
    mapper/views/layered.py: OK   (sha256)
```

**The defect has not been relocated.**

## The headline numbers, verified on my own sweep

My own 943-configuration harness (terminals 20..60 x 8..30), driving the real app and
reading the composited frame — written independently of `tests/test_overflow.py`:

```
MAP=legacy n=943                          MAP=anidado n=943
  content_w == region.width      : 943      content_w == region.width      : 943
  content_w == _canvas_width()   : 724      content_w == _canvas_width()   : 743
  content_w == _canvas_width()-2 : 219      content_w == _canvas_width()-2 : 200
  content_w anything else        :   0      content_w anything else        :   0
  frame-measurable               : 642      frame-measurable               : 660
  charge vs frame  UNDER         :   0      charge vs frame  UNDER         :   0
  charge vs frame  OVER          :   0      charge vs frame  OVER          :   0
  charge vs frame  EXACT         : 642/642   charge vs frame  EXACT        : 660/660
```

- **Under-charge 0 of 943 on both fixtures: CONFIRMED.**
- **Charge-vs-frame exact: CONFIRMED** (I measure 642/642 and 660/660 against your 636/636
  and 657/657 — a handful more configurations were frame-measurable on my harness, a pause-count
  difference. Zero under, zero over, all exact on both instruments.)
- **`724 / 219 / 0` is reproduced to the unit.** This is a measurement, not a
  rationalisation.

## The pre-fix 23 reproduces — the delta is real, not an instrument change

Reproduced on the pre-round-3 arithmetic, compared against a real Rich wrap at the *same*
`w - 2` so the divisor is not in play:

```
[legacy] PRE-round-3 arithmetic charge < Rich wrap at w-2, over 943: 23
```

**Exactly pass 3's number.** The improvement from 23 to 0 is a genuine behavioural delta.

## The residual against the `w - 2` stick: a measured mechanism, not a rationalisation

I adjudicated every disagreement against the frame rather than counting them:

```
[legacy] new charge != obsolete w-2 stick at 45 of 943
        frame agrees with the NEW charge : 22
        frame agrees with the STICK      :  0
        frame could not adjudicate       : 23
        e.g. term=(20,21) content_w=20 canvas_w=20 new=3 stick=4 FRAME=3
```

**22 to 0.** At every configuration the compositor can rule on, the frame backs the new
charge and never the stick. `wrap_w` being a required argument with no default is the right
call: there is no constant that is correct at both 724 and 219 configurations.

(My 45 counts all disagreements; your 31/33 count under-charges only. Different denominators,
same ruling.)

## The `None` oracle is not one `if` away from vacuous

Your 307-of-943 figure is about the *sweep*. The arm drives 27 terms, not 943, and they were
chosen tall enough that the frame can see the header. Measured on the arm's own `_HEADER_TERMS`:

```
[legacy]  terms=27  checked=27  clipped=0  rows seen=[2, 3]
          bounds: clipped <= 9 (headroom 9), checked >= 18 (headroom 9), {2,3} <= seen: yes
[anidado] terms=27  checked=26  clipped=1  rows seen=[2, 3]
          bounds: clipped <= 9 (headroom 8), checked >= 18 (headroom 8), {2,3} <= seen: yes
          clipped terms: [(28, 17)]
```

The oracle returns `None` at **0 of 27 and 1 of 27** where it is actually used. The `None`
branch still asserts (`region.height <= charged`) rather than skipping, the count is bounded
both ways, and `{2, 3} <= seen` proves the band really contains three-row headers. **This
arm cannot pass by going blind.**

## `N8`: the survivor was closed by strengthening the pin, not weakening the mutant

Re-run, unmodified mutant — `_canvas_size` passes a guessed `w - 2` instead of the measured
content width:

```
E  AssertionError: legacy  (29,30): `_canvas_size` gave the renderer row_limit 10 into the
                   11 body rows the frame actually left (region height 13, header 2)
E  AssertionError: anidado (29,30): `_canvas_size` gave the renderer row_limit 11 into the
                   12 body rows the frame actually left (region height 14, header 2)
tests\test_overflow.py:402                     2 failed
mapper/app.py: OK   (sha256)
```

It dies at **line 402 — the wiring clause that was added to close it** — on both fixtures,
with the message you reported. The mutant is the honest one (it injects exactly the defect
described); the kill comes from the added assertion. `charged == measured` at line 388 still
does not catch it, because that clause asks the helper directly with the measured width —
which is precisely why the wiring clause is load-bearing rather than decoration. **Reported
survivor, properly closed.**

---

# Item 3 — `B-60` and the settle: DISCHARGED (1 MEDIUM)

## It terminates, and the bound is measured

The chase has no explicit counter, so I measured it. Instrumented `_declare_after_layout`
across **all 943 mounts** on `legacy`:

```
MAP=legacy  configs=943
  passes-per-mount histogram: [(3, 643), (4, 219), (5, 81)]
  WORST: 5 passes at (20,20)  region trace [(20,1), (18,1), (18,1), (20,2), (20,2)]
```

**Never more than 5 passes, at any reachable configuration.** The worst case shows the
mechanism working: the region moves, revisits a size, and settles.

And under deliberate abuse — a resize storm and a forced two-size oscillation:

```
[legacy] passes to settle a MOUNT at (140,45): 3
[legacy] 60-resize storm: 181 passes during, 181 after draining 30 pauses,
         181 after 30 MORE pauses   -> chain TERMINATED   (3.02 passes per resize event)
[legacy] 100 alternating resizes (31,16)<->(32,16): 260 passes, then 260 after
         40 more quiet pauses       -> TERMINATED         app running: True
```

The chain stops the instant the resizes stop. Cost is O(resize events) at ~3 passes each,
not a live loop. Two structural properties make this hold: the chase re-schedules only on a
*change*, and concurrent chains converge because they share `_declared_for` — the second
chain to run sees equality and dies.

**MEDIUM-1 — the termination is empirical, and there is a live feedback path under it.**
`#map-canvas` is `width: 1fr; height: 100%`, so its region is layout-determined and
converges. But `_declare_after_layout` also updates `#map-pagination`, which is a `Static`
with Textual's default `height: auto` — and measured, its height is **content-determined**:

```
[legacy]  #map-pagination region HEIGHTS over the grid: [(1, 102), (2, 66)]
[anidado] #map-pagination region HEIGHTS over the grid: [(1, 110), (2, 58)]
```

So the cycle *declared numeral -> strip text length -> strip height -> canvas region height
-> declared numeral* is closed in the layout. It does not oscillate on either shipped
fixture at any of 943 configurations, because the numeral's length changes by at most a
digit and never at the wrap point. But nothing asserts that, and a future graph whose hidden
count straddles the wrap boundary would make the chase live. At runtime that is a spinning
app, not a red test.

**Suggested fix** (cheap, and it retires the whole class):

```python
# `_declared_for` alone assumes the region CONVERGES.  It does on both fixtures
# (measured: at most 5 passes over 943 configurations), but `#map-pagination` is
# `height: auto` and this method writes it, so the region-to-numeral cycle is
# closed in the layout and convergence is a property, not a guarantee.
self._declare_passes = getattr(self, "_declare_passes", 0) + 1
if region != self._declared_for and self._declare_passes < 8:
    self._declared_for = region
    self.call_after_refresh(self._declare_after_layout)
```

with `self._declare_passes = 0` in `on_resize` beside the existing `_declared_for = None`,
and the measured 5 quoted as the reason 8 is the number. Recommendation, not a block: the
120 s ceiling landed in this same round already converts a wedge into a red arm in CI.

## The six regression sizes: red pre-fix, green post-fix, both surfaces

Measured directly on the first look, no repaint, both surfaces, with the chase removed
(`N6`) and restored:

```
  [PRE ] legacy   (31,16)  region=31x3  hidden=7  strip=8  canvas=8   DIVERGES
  [PRE ] legacy   (32,16)  region=32x3  hidden=7  strip=8  canvas=8   DIVERGES
  [PRE ] legacy   (34,15)  region=34x3  hidden=7  strip=8  canvas=8   DIVERGES
  [PRE ] legacy   (35,14)  region=35x3  hidden=7  strip=8  canvas=8   DIVERGES
  [PRE ] anidado  (34,14)  region=34x3  hidden=6  strip=7  canvas=7   DIVERGES
  [PRE ] anidado  (35,14)  region=35x3  hidden=6  strip=7  canvas=7   DIVERGES

  [POST] legacy   (31,16)  region=31x3  hidden=7  strip=7  canvas=7   OK
  [POST] legacy   (32,16)  region=32x3  hidden=7  strip=7  canvas=7   OK
  [POST] legacy   (34,15)  region=34x3  hidden=7  strip=7  canvas=7   OK
  [POST] legacy   (35,14)  region=35x3  hidden=7  strip=7  canvas=7   OK
  [POST] anidado  (34,14)  region=34x3  hidden=6  strip=6  canvas=6   OK
  [POST] anidado  (35,14)  region=35x3  hidden=6  strip=6  canvas=6   OK
```

**Exactly your table, on an independent instrument.** And the arms themselves die on the
mutants:

```
N6  the declaration stops chasing the region
E   AssertionError: legacy  (31,16): the strip declares 8 on a first look that is hiding 7
E   AssertionError: anidado (34,14): the strip declares 7 on a first look that is hiding 6
    2 failed, 2 passed         mapper/app.py: OK (sha256)
N7  MapScreen has no working resize handler
E   AssertionError: after a resize the strip declares None against 7 hidden, with no key pressed
    1 failed                   mapper/app.py: OK (sha256)
```

`B-56` stays green under `N6`, which confirms the two arms cover different sizes rather than
duplicating.

## `anidado` at (34,15): a genuine geometric limit

Ruled **geometry, not a residual `B-60`**, and the discriminator is the strip:

```
  [PRE ] anidado (34,15)  region=34x1  hidden=7  strip=7  canvas=None
  [POST] anidado (34,15)  region=34x1  hidden=7  strip=7  canvas=None      <- byte-identical
```

At the six `B-60` sizes the strip was **wrong** pre-fix (8 against 7) and right post-fix.
At (34,15) the strip is **right in both states** — the declaration is correctly computed;
the canvas region is one row tall and the numeral sits at the end of a line that wraps past
it, so it is physically clipped. Different mechanism, unchanged by the fix, correctly
excluded from `_SETTLE_TERMS`.

**LOW-2.** At that size the canvas numeral is absent while 7 nodes are hidden, and
`LLR-N06.3.3` makes absence *mean* "nothing is hidden" — so the canvas surface states
something false there. Pre-existing and geometry-bound, and the surface the operator reads
is correct. It deserves a line in the carries table rather than silence, because it is the
one place the story's promise cannot be kept.

---

# Rider A — correctly a carry, and the increment improves the symptom

The defect reproduces exactly as round 3 measured it:

```
  MOUNTED at (50,20)  : region 50x8   rail_hidden=True  insp_hidden=True  chrome=0
  at (140,45)         : region 80x38  hidden=0
  SHRUNK to (50,20)   : region 1x10   rail_hidden=False insp_hidden=False chrome=60 of 50 columns
```

The decisive question is whether the new resize handler makes this *newly reachable* or
newly owned. Measured both ways, same shrink:

```
  POST (as shipped)          : hidden=8  strip declares=8     canvas=None   app running=True
  PRE  (on_resize inert)     : hidden=8  strip declares=None  canvas=None   app running=True
```

**The region collapse is byte-identical pre and post — 1x10 either way.** What changed is
that the strip now tells the truth about the collapsed frame (8 against 8 hidden) where
before it declared *nothing*, which `LLR-N06.3.3` makes mean "nothing is hidden" — a false
statement about a frame hiding the entire map.

So the increment does not create the path, does not widen it, and does not own it. It makes
the operator-visible surface **strictly more honest** in exactly the state the carry
describes. Declining the fix — because re-running `_apply_region_visibility` moves focusable
regions and reopens `LLR-CNV.3.1` / `B-50` — remains the right call, and the arm's docstring
records the bound accurately.

**LOW-3.** The carry's entry in 13.9 describes the geometry but not the residual it leaves:
after a shrink, the canvas numeral is absent while the whole map is hidden. Same shape as
LOW-2. One clause on the carry row would close the gap between what 13.9 says and what the
surface does.

---

# Rider B — `pytest-timeout`: DISCHARGED

Diffed against `954f8f3`; the change is exactly two things and nothing else:

```
-dev = ["pytest>=8.0", "pytest-asyncio>=0.23"]
+dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "pytest-timeout==2.3.1"]
+timeout = 120
+timeout_method = "thread"
```

- **Dev extra only, runtime `dependencies` untouched** — still `textual==8.2.8`,
  `rich==15.0.0`, `pyyaml>=6.0`. Confirmed.
- **Pin is exact** (`==2.3.1`); installed version confirmed 2.3.1.
- **The Windows/SIGALRM rationale is true**, not folklore:
  `platform win32 / has SIGALRM False`. `thread` is the correct method here.
- **The hang arm fails red rather than wedging.** `N9` — cycle guard deleted from
  `mapper/views/radial.py`:

```
$ PYTHONUTF8=1 python -m pytest -q -p no:randomly tests/test_repair_depth.py -k "tc_r12 and radial"
+++++++++++++++++++++++++++++++++++ Timeout +++++++++++++++++++++++++++++++++++
pytest EXIT=1        elapsed 33 s
mapper/views/radial.py: OK   (sha256)
```

**Exit 1 after 33 s — your number, reproduced.** The `@pytest.mark.timeout(30)` marker is
what does it: it wins even over `--timeout=0` on the command line, so the arm cannot be
silently disarmed by a CI flag.

- **Nothing else is newly sensitive to the 120 s ceiling.** Both lanes, measured:

```
fast lane slowest arm: 8.82s   test_llr_n06_3_1_the_charged_header_height_is_the_composited_one[legacy]
slow lane slowest arm: 14.13s  test_at_r16b_the_factory_screen_survives_a_depth_5000_map_composed
```

The ceiling is per-test. Headroom is **8.5x** on the worst arm in either lane. The claim
"slowest measured arm under 20 s" is true.

---

# Findings

### F1 — `_declare_after_layout`'s chase has no bound, over a live feedback path  [MEDIUM]
- **What:** the self-reschedule terminates only if the canvas region converges, and
  `#map-pagination` is `height: auto` and is written by this same method, closing a
  content-to-layout cycle.
- **Where:** `mapper/app.py:1572-1574`.
- **Why it matters:** measured safe today (max 5 passes over 943 configurations; storms and a
  forced oscillation both terminate), but nothing asserts it. A graph whose hidden count
  straddles the strip's wrap point makes the chase live — a spinning app at runtime.
- **Suggested fix:** the pass counter above, reset in `on_resize`, with the measured 5 quoted
  as the reason for the bound.

### F2 — the probe is not parallel-safe  [LOW]
- **Where:** `tests/test_fold.py:249-258`. Fine today; one docstring sentence would stop a
  future `-n auto` from producing a confusing race.

### F3 — two surfaces state something false at a region the numeral cannot fit  [LOW]
- **Where:** `anidado` at (34,15) (region 34x1), and after an operator shrink across the
  collapse threshold (region 1x10). Both geometry-bound, both with a correct strip, both
  unchanged or improved by this increment. They deserve a clause on the carries in 13.9
  rather than silence.

# Evidence checklist

- [x] **Diff read in full for the fix-round-3 surface** — `mapper/views/layered.py`
      (`_header_line` 370-407, `header_rows` 410-483, `_METER_PCT` 33), `mapper/app.py`
      (`_header_rows` 1349-1368, `_canvas_size` 1377-1424, `_declare_after_layout` 1521-1574,
      `on_resize` 1576-1604, `_declared_for` 1141-1143), `tests/test_overflow.py` 272-500 and
      562-689, `tests/test_fold.py` 182-281, `pyproject.toml` in full,
      `tests/test_repair_depth.py` 705-760.
- [x] **Correctness pass** — two independent 943-configuration sweeps driving the real app;
      a 943-mount reschedule census; two resize storms; a seven-size first-look pre/post
      comparison on both surfaces.
- [x] **Simplicity pass** — no premature abstraction. `wrap_w` as a required argument with no
      default is the right shape and the measurement justifies it. `_METER_PCT` is the
      minimal form of the `F6` fix.
- [x] **Reuse / duplication** — the one duplication pass 3 found (`test_overflow.py::_header_rows`)
      is **deleted**, verified by grep, not renamed. No new duplication introduced.
- [x] **Tests reviewed for intent** — the composited pin kills in both directions (`N4`
      under, `N5` over) where its predecessor could kill in neither; `N8` dies on the wiring
      clause added to close it; `N6`/`N7` die at the sizes and with the messages claimed;
      `N1`/`N2`/`N3` die in the fully-tracked state; the `None` oracle is exercised 26-27
      times of 27 with 8-9 configurations of headroom on its own bound.
- [x] **Verdict explicit** — PASS.
- [x] **Shared working tree untouched** — all mutation in `<scratch>/exp5` and `<scratch>/exp6`,
      every restore proven by `sha256sum -c`; shared tree at 34 status entries, unchanged,
      no probe leaked.

# Verdict

- [x] **OK to advance**
- [ ] OK with the listed fixes applied first
- [ ] Block

**0 HIGH. This increment is ready to commit.** The three pass-3 findings are discharged on
independent instruments, not on restated claims: the artifact scan passes in the exact
post-commit state that reddened pass 3's baseline and its widening is driven by a probe
rather than inferred from tracking state; the header charge is a real wrap at a measured
width, its pin fails in both directions where the old one could fail in neither, and the
23-of-943 under-charge that pass 3 found is reproduced pre-fix and is 0 of 943 post-fix on
both fixtures; the `B-60` residual is closed at all six sizes on both surfaces and the chase
that closes it is bounded at 5 passes over every reachable configuration.

Both riders rule for round 3. `pytest-timeout` is scoped, pinned, justified by a rationale
that is true on this platform, and proven by a mutant that turns a wedge into exit 1 in 33 s.
Rider A is correctly a carry — the collapse is byte-identical with and without the new
resize handler, and the handler makes the operator-visible declaration correct in a state
where it was previously absent.

The one MEDIUM is a hardening recommendation, not a defect: the chase's termination is a
measured property rather than an asserted one, and a three-line counter would make it a
guarantee. It does not need to happen before this commit.
