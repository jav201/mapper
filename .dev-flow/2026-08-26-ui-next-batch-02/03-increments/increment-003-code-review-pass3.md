# Increment 3 — Code Review, Pass 3 (narrow confirmation of fix round 2)

**Verdict: BLOCK. 3 HIGH.** This increment is **not** ready to commit.

One HIGH is new and mechanical: the increment contains a test that **turns red on the
commit that lands it**. The other two are the two HIGHs fix round 2 targeted; neither is
discharged. The rest of the round holds up well — F-A, the A-3 bump, the five F-D
coercion arms, MEDIUM-5, the ledger and the ruff delta all verified clean by
re-execution.

| Item | Ruling |
|---|---|
| **1 · HIGH-1** measured header | **NOT DISCHARGED** — the safety claim is false as measured, and the arm guarding it is circular |
| **2 · HIGH-2** `B-60` close | **NOT DISCHARGED** — first-look divergence reproduces at 4 sizes on `legacy` and 2 on `anidado` |
| **3 · F-A** routed obligation | **DISCHARGED** (2 MEDIUM) |
| **4 · rail carry** | **Right call, and the arm does not overstate** — but a production comment does (MEDIUM) |
| Also: F-D arms · MEDIUM-5 · ledger · ruff | **All DISCHARGED** |

## Method and harness

Everything below was executed in an isolated export, never in the shared working tree:

```
$ tar --exclude=.git --exclude=__pycache__ -cf - . | (cd <scratch>/exp3 && tar -xf -)
$ cd <scratch>/exp3 && git init -q . && git add -A && git commit -q -m base
FILES: 192
```

Every mutation was restored from a `cp` snapshot and the restore proven by `sha256sum -c`,
never by `git status` (the export's index is CRLF-normalised, so `git status` there is not
an honest instrument).

**Baseline in the export — and it is not green:**

```
$ PYTHONUTF8=1 python -m pytest -q -m "not slow" -p no:randomly
FAILED tests/test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts
1 failed, 795 passed, 17 deselected, 1 xfailed in 109.20s
EXIT=1
```

That single failure is **HIGH-A** below, not an export artifact. All targeted runs below
therefore select specific arms so it cannot mask a verdict.

Corroborating your own lane figures: 795 passed + 1 (the arm that only fails once the
artifacts are tracked) + 1 xfailed = **796 passed / 17 deselected / 1 xfailed**, matching
what you measured. Lane counts confirmed.

---

# F1 — The artifact code-point scan fails on the commit that lands this increment [HIGH]

**What.** `tests/test_fold.py:220` guards the N15 widening with

```python
assert not set(artifacts) <= set(
    _tracked(".dev-flow/*.md", ".dev-flow/**/*.md", ".dev-flow/*.json")
), "no untracked artifact is in scope; the rglob is buying nothing today"
```

The `rglob` half must be **strictly wider** than the `git ls-files` half. Today it is,
because exactly five `.dev-flow` artifacts are untracked. Committing this increment tracks
all five, the two sets become equal, and the assertion fires.

**Where.** `tests/test_fold.py:216-221`.

**Executed proof — the export, where `git add -A` tracked everything:**

```
tests\test_fold.py:223: AssertionError
FAILED tests/test_fold.py::test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts
```

**And measured in the real tree, showing the transition is exactly the commit:**

```
rglob artifacts : 91
tracked (today) : 86
untracked today : ['.dev-flow/2026-08-26-ui-next-batch-02/02j-inc3-painted-set-architect.md',
                   '.../increment-003-code-review-confirmation.md',
                   '.../increment-003-code-review.md',
                   '.../increment-003-security-confirmation.md',
                   '.../increment-003-security-review.md']
assert holds today (rglob NOT subset of tracked): True
after committing those 5, rglob subset of tracked -> True
```

**Why it matters.** The increment's deliverable is a commit. CI on that commit is red, and
red for a reason that has nothing to do with the rule the arm exists to enforce. The
non-vacuity guard is correct in intent — a widening that buys nothing should say so — but
it is written against a condition that this increment's own act of landing destroys. It is
also self-perpetuating: it will be green again only while some artifact is uncommitted,
i.e. only mid-increment, which is the one moment nobody runs the full lane on a clean tree.

**Suggested fix.** Assert the widening structurally rather than incidentally — that the
`rglob` half reaches paths the tracked query *would* miss if they were untracked, or drop
the subset check and assert instead that the scan is anchored on `rglob` by construction:

```python
# The rglob half must not degrade into `git ls-files`.  Asserted on the QUERY,
# not on today's tracking state: the artifacts an increment writes are untracked
# only until it is committed, so a subset check goes red on its own commit.
assert set(_tracked(".dev-flow/*.md", ".dev-flow/**/*.md", ".dev-flow/*.json")) <= set(
    artifacts
), "the rglob half is narrower than the tracked view; it is the wrong instrument"
assert len(artifacts) >= len(_tracked(...))
```

---

# F2 — HIGH-1 is NOT discharged: the safety claim is false, and its pin cannot see that [HIGH]

The fix is a real improvement — I confirm 0 PRED-2 and 0 PRED-3 failures on `legacy`
post-repaint over 943 configurations, against 9 before. But three of the four things you
asked me to check come back negative.

## F2a — the divisor justification is factually wrong

`header_rows` divides by `w - 2`, and both the function's docstring and
`MapScreen._header_rows`'s docstring justify that as "the canvas widget's CONTENT width".
Measured, it is not:

```
SWEEP map=legacy n=943
  content_w != w-2 : 806   (in all 806, content_w == w)
```

`#map-canvas` carries `width: 1fr; height: 100%` and **no padding and no border**
(`mapper/app.py:2362`), so the widget's content width equals its region width. At the
transcript the docstring quotes:

```
=== map=legacy term=(28,17) region=(28,3) content_w=28 cw=28 w=28 h=1
    charged=3  real_rows=3  worst_rows=3
```

`content_w` is **28**, not 26. The docstring says the frame shows three rows "which is
`ceil(55/26) = 3`, not `ceil(55/28) = 2`". The frame does show three rows — but at wrap
width **28**, because Rich **word-wraps**. The right answer was reached through a wrong
mechanism. That is exactly the off-by-two one layer down you asked about; it is currently
compensating rather than causing, which is why nothing above it went red.

## F2b — "always safe" is REFUTED

The claim in §12.1 is `charged >= measured` everywhere, over-charging in 9 of 738 probes.
Measured against an actual render of the line (Rich, at the charitable divisor `w - 2`, so
this is not the divisor question):

```
MAP=legacy n=943 AFTER REPAINT
  UNDER-CHARGE vs real render = 23:  [(w=30, charged=2, real=3)]
```

23 of 943 configurations charge 2 rows for a line that physically occupies 3. Direct
transcript at one of them:

```
=== map=legacy term=(30,10) region=(28,1) content_w=28 cw=30 w=30 h=1
    charged=2  real_rows=3  worst_rows=3
    [ 0] '◆ mapper · árbol            '
    h[0] '◆ mapper · árbol            '
    h[1] 'legacy▰▰▰▰▰8 nodos  ▽ 8 fuera '
    h[2] 'de vista                    '
```

`ceil(55/28) = 2`; the line renders in 3. **Under-charging is, by the increment's own
definition, `B-61`.** It is currently latent — I found no PRED failure attributable to it —
which is precisely the state `B-61` was recorded in before this round proved it live.

## F2c — the pin that guards this is circular [this is the load-bearing finding]

`tests/test_overflow.py:271-287`, the "measured" side of
`test_llr_n06_3_1_the_charged_header_height_is_never_short_of_the_measured_one`:

```python
    header = LayeredRenderer().render(graph, ViewState(w=w, h=h)).plain
    header = header.split("\n")[0]
    avail = max(1, w - 2)
    return -(-len(header) // avail)          # <- the charge's own formula
```

against the product's

```python
    avail = max(1, w - 2)
    return max(1, -(-len(first) // avail))
```

The two sides differ only in which `unpainted` count feeds the line. The **row-counting
arithmetic is identical**, so the pin cannot fail on a wrong divisor (both use `w - 2`), on
word-wrapping (neither wraps), or on a wide character (both use `len`). Its docstring says
it compares "the CHARGE against a measurement instead of comparing two literals" —
`ceil(len / (w - 2))` *is* the assumption, re-typed.

This is the same discipline failure as a re-captured digest, one layer down: the constant
`HEADER_ROWS = 2` was a formula asserted rather than measured, and the fix replaced it with
a different formula pinned against itself.

**Executed proof.** Swapping only the *test helper* for a real render of the line, leaving
the product untouched:

```
MUT applied  (helper renders the line instead of re-deriving ceil(len/avail))
E  AssertionError: [(8, 30, 8, 3, 2), (8, 30, 40, 3, 2), (10, 31, 8, 3, 2),
                   (10, 31, 40, 3, 2), (11, 31, 8, 3, 2), (11, 31, 40, 3, 2), ...]
E  assert [...] == []           # `short == []`, the safety direction
E  Left contains 21 more items, first extra item: (8, 30, 8, 3, 2)
tests\test_overflow.py:338: AssertionError
FAILED tests/test_overflow.py::test_llr_n06_3_1_the_charged_header_height_is_never_short_of_the_measured_one
tests/test_overflow.py: OK          # restore verified by sha256
```

Tuples are `(n, w, h, measured, charged)`: 27 of 520 grid cells charge short. The arm is
green only because of its instrument.

## F2d — the self-consistency / cycle argument: SOUND, nothing oscillates

Ruled clean. `header_rows` never reads `painted`, `row_limit`, or `body_h`; it prices
`unpainted = len(graph.nodes)` unconditionally, so it is a pure function of `(graph, w)`.
There is no fixed point being iterated and therefore nothing that can oscillate. The
docstring's "a row lost to the charge hides a node, which paints the token the charge
already paid for" is a *post-hoc* consistency remark, not a load-bearing step — the cycle
is broken by the unconditional worst-case pricing alone. Cut the paragraph or mark it as
commentary; the argument does not depend on it.

**Suggested fix for F2 as a whole.** Make the measurement a measurement, in one place, and
let both the product and the pin consume it:

```python
def header_rows(graph: Graph, w: int) -> int:
    ...
    avail = max(1, w - 2)
    con = Console(width=avail, legacy_windows=False)
    return max(1, len(con.render_lines(line, con.options.update_width(avail))))
```

and delete `tests/test_overflow.py:_header_rows`, replacing the pin's "measured" side with
the composited frame (the widget's own `content_size.width`, which is what actually wraps).
Then correct both docstrings: the divisor is not the widget content width, and the reason
narrow headers take three rows is word-wrap, not a two-column inset.

---

# F3 — HIGH-2 is NOT discharged: `B-60` recurs on the first look at reachable sizes [HIGH]

`_declare_after_layout` closes the divergence at the four sizes the `B-56` arm names. It
does not close it generally. Extending that arm's own size tuple by four more reachable
terminal sizes, changing nothing else:

```
for term in ((50,20), (60,20), (40,20), (30,20), (31,16), (32,16), (34,15), (35,14)):
...
E  AssertionError: (31, 16): the strip declares 8 on a first look that is hiding 7
E  assert 8 == 7
E   +  where 8 = _declared_total([' ▰▱▱▱▱▱▱▱   1/8  ▽ 8 fuera de   vista  '])
E   +  and   7 = len(frozenset({'alm','cont','fin','inv','nom','pres', ...}))
tests\test_overflow.py:416: AssertionError
tests/test_overflow.py: OK          # restore verified by sha256
```

It fails on the **strip**, which the original carry called "the surface the operator reads
— correct". Full operator-visible transcript, first look versus one repaint:

```
=== (31,16) h_before=2 h_after=2
  FIRST LOOK    declared=['erp'] traced=[]
    b[0] '◆ mapper · árbol legacy▰▰▰▰▰8  '
    b[1] 'nodos  ▽ 8 fuera de vista      '
    b[2] '                               '
  AFTER REPAINT declared=['erp'] traced=['erp']
    a[1] 'nodos  ▽ 7 fuera de vista      '
    a[2] '                     ▐ Siste…  '
```

Reproduced identically at **(31,16), (32,16), (34,15), (35,14)** on `legacy`, and
independently at **(34,14) and (35,14)** on the new `anidado` fixture — so it is not a
`legacy` quirk.

**Mechanism, traced.** `_canvas_size` instrumented across mount at (31,16):

```
calls (region_w, region_h, header_rows, returned (w,h)):
    (0, 0, 2, (31, 8))     <- pre-layout guess
    (0, 0, 2, (31, 8))
    (29, 2, 2, (31, 1))    <- _declare_after_layout runs HERE; region is mid-reflow
    (29, 2, 2, (31, 1))
final settled region: (31, 3)   -> would give h=2, and nothing recomputes
```

`_declare_after_layout` fires on the *first* `call_after_refresh`, while
`_apply_region_visibility`'s show/hide is still reflowing the row: the canvas region is
29x2, so `_canvas_size` takes the short-region branch and returns `h = 1`, declaring
nothing painted. The region then settles to 31x3 and **`MapScreen` has no `on_resize`
handler** — grep confirms none — so nothing repaints. Both declaring surfaces keep a
numeral computed for a frame that no longer exists, and `painted_ids` at the settled
geometry disagrees with both.

This is `B-56`/`B-60` in the same shape the carry described; the round closed the two
instances it measured and left the mechanism. The arms cannot see it because `B-56` tests
four sizes and `TC-038` tests one, and none is inside the band.

**Suggested fix.** Repaint on the event that actually signals the layout is final, rather
than on a one-shot post-mount callback:

```python
def on_resize(self, event: events.Resize) -> None:
    """The region settles AFTER `_declare_after_layout`'s callback at narrow
    widths -- `_apply_region_visibility` reflows the row, and measured at
    (31,16) the declare pass saw a 29x2 region that then became 31x3.  A
    one-shot post-mount callback cannot see that; the resize can."""
    self._declare_after_layout()
```

and widen the `B-56` size tuple to include (31,16), (32,16), (34,15), (35,14) so the
regression is pinned. Keep the strip *and* canvas assertions; both were needed to see it.

## What IS discharged inside HIGH-2

- **`TC-038` no longer repaints away its own claim.** `tests/test_overflow.py:744-756`:
  `screen.refresh_canvas()` is gone, replaced by `for _ in range(3): await pilot.pause()`;
  the docstring states the property and why the old form hid `B-60`, and the word "always"
  is gone. **DISCHARGED.**
- **`LLR-CNV.3.1` focus arm is genuinely green.** 46 focus/CNV arms pass, exit 0.
  **DISCHARGED.**
- **The A-3 pin bump 49 -> 52 is evidence, not a rubber stamp.** All three claimed sites
  are real and individually verifiable by the census itself:

  ```
  argful: 52   zeroarg: 26
  mapper/app.py:1534         -> _declare_after_layout's `.render(...)`   (+1)
  tests/test_inc3_census.py:338, :339 -> plain_frame / diff_frame        (+2)
  tests/test_inc3_census.py:326       -> the pre-existing loop site
  ```

  The +2 land on the non-vacuity guard (`assert plain_frame != diff_frame`), which is what
  the pin's comment names. 52 − 3 = 49 is consistent. No wholesale re-baseline.
  **DISCHARGED.**

---

# F4 — F-A: DISCHARGED, with two MEDIUM weaknesses

Verified by independent re-execution.

- **Strict.** `tests/test_fold.py:531-532`, `@pytest.mark.xfail(strict=True, reason=...)`,
  inline on the marker — it does not depend on config (`pyproject.toml` sets no
  `xfail_strict`). **DISCHARGED.**
- **Drives the real crash.** `--runxfail` exposes the genuine path:
  `mapper/widgets/inspector.py:139` `id=f"insp-field-{field.key}"` inside `_rows()`, called
  from `_rebuild` at `:95`, arriving via `message_pump.py:702 _flush_next_callbacks` — i.e.
  scheduled by `call_next`, outside every guard. `textual.dom.BadIdentifier`. The arm's
  oracle is `assert app.is_running` preceded by `assert len(screen.graph.nodes) == 2`, so
  it proves the map opened first. **DISCHARGED.**
- **Byte-identity.** `git diff --stat 954f8f3 --` is empty for `mapper/widgets/inspector.py`,
  `mapper/screens/coverage.py`, `mapper/screens/factory.py`, `mapper/store.py`. Raw sha256
  differs on all four, and the delta is **exactly** the CR count (299/157/489/676 bytes,
  0 CRs in the blob) under `core.autocrlf=true`; CR-stripped, all four hash to the blob.
  `git diff` is authoritative here. **DISCHARGED.**
- **Six source files.** `mapper/app.py`, `keymap.py`, `views/layered.py`, `views/outline.py`,
  `views/state.py`, `widgets/rail.py`. No untracked additions under `mapper/`.
  **DISCHARGED.**

**F4a [MEDIUM] — no `raises=`.** The marker guarantees "this test fails", not "this test
fails from `BadIdentifier`". An import error, a renamed fixture, or a broken `open_map`
would satisfy the xfail silently, and Inc-REPAIR would be handed a marker that no longer
proves anything. Add `raises=BadIdentifier`.

**F4b [MEDIUM] — the docstring's headline case is never exercised.** The body loops over
`chr(0x01)`, `año`, `fecha limite` and fails on the **first** iteration, so `año` and
`fecha limite` are asserted but not driven. I verified out-of-tree that both do crash
(`'insp-field-año' is an invalid id`, `'insp-field-fecha limite' is an invalid id`, with
`ok_key` exiting clean as a control), so the claim is true — but the arm does not
demonstrate it, and the Spanish-first happy path is the whole reason F-A outranks `SEC-F1`.
Put `año` first, or parametrise the three keys so each is its own node id.

---

# F5 — The rail carry: right call, honest arm, dishonest production comment [MEDIUM]

**The N8 arm does not overstate its coverage.** `tests/test_pan.py:210-251` states in terms
what it asserts and what it does not: "this arm asserts what this increment fixed (the
method does not let the exception escape) and does not assert that the frame survives,
because it does not." Its non-vacuity is carried by two `pytest.raises(KeyError)` clauses
at the sink, so it cannot pass on an ordinary graph. That is the correct way to land a
partial fix.

**Not opening `rail.py` was defensible** — it costs no file (it is already among the six),
but it is a distinct sink on a distinct path, and mixing it into a fix round aimed at
`_canvas_size` and `_declare_after_layout` would have widened the round without a measured
need. The reachability is bounded: the arm records that no `.mmd`/`.yml` pair produces a
dangling edge, and I did not find one either.

**What is not right is the production comment.** `mapper/app.py:1745-1752` reads:

> a dangling edge raises `KeyError` from inside the message pump -- which kills the app,
> exactly the shape the cycle guard was added for. ... A coverage strip that cannot be
> drawn is a drawing problem, so it degrades to empty.

Measured, the app is **not** saved:

```
4)  refresh_canvas survived dangling edge: True
4b) COMPOSITED FRAME RAISED KeyError: 'fantasma'
4c) OutlineRail.render RAISED KeyError: 'fantasma'
```

A reader of `app.py` alone concludes the failure mode is closed. Only the test docstring,
in another file, says otherwise. Add one sentence to the `app.py` comment pointing at the
carry, so the two files stop disagreeing.

---

# Also verified — all clean

**F-D coercion arms.** Spot-checked two of five; both die by their **documented oracle**,
not by a crash, and both restores are sha256-proven:

```
N9  doc chip uncoerced (layered.py:520)
E   AssertionError: ('LayeredRenderer', (80,24), False, ['0x1','0x200b','0x202c','0x202e','0xe0041'])
    FAILED test_a89_every_reached_renderer_coerces_what_it_paints
    mapper/views/layered.py: OK

N11 diff chip uncoerced (layered.py:510)
E   AssertionError: ('LayeredRenderer', (80,24), True,  ['0x1','0x200b','0x202c','0x202e','0xe0041'])
    FAILED test_a89_every_reached_renderer_coerces_what_it_paints
    mapper/views/layered.py: OK
```

The `False` / `True` in the two tuples is the `state_diff is not None` flag — N11 dies only
in the diff-bearing pass, which is the direct evidence that the widened fixture reaches the
diff-only sink rather than merely covering it. **DISCHARGED.**

**MEDIUM-5, the lockstep `pan_y` drop.** Killed by its own oracle with its own message:

```
N6  `geo.place` drops `- pan_y`
E   AssertionError: `J` moved `pan_y` and the painted canvas is byte-identical;
    the vertical pan is a no-op the operator cannot see
    FAILED tests/test_pan.py::test_a_live_J_press_changes_what_the_canvas_paints
    1 failed, 19 passed        mapper/views/layered.py: OK
```

**DISCHARGED.**

**Ledger `814 = 737 − 0 + 77`.** Verified set-wise against a `git archive 954f8f3` export,
node ids sorted and compared: base_all 737, post_all 814, added 77, **deleted 0** (the
`comm -23` output is empty on both lanes); default lane `797 = 720 − 0 + 77` likewise.
The convention that makes it work is per-node-id, parametrised cases counted individually.
**DISCHARGED.**

**ruff, set-wise and scope-matched.** ruff 0.8.4 both sides,
`ruff check . --exclude prototypes --output-format=concise`, normalised to
`(file, code, message)` with line numbers dropped: base 28 records / 28 unique, post 27 / 27.
**NEW = ∅.** GONE = `{mapper/views/layered.py F401 mapper.model.Node imported but unused}`,
exactly one element. **DISCHARGED.**

---

# F6 — `header_rows` does O(n) work that cannot change its answer [MEDIUM]

`header_rows` calls `graph.coverage()` (`mapper/model.py:215`, a walk of every node's
`required_coverage(schema)`) to compute `pct`, which feeds `darkside.step_meter(filled, 5)`.
`step_meter` emits `total` glyphs regardless of `filled`, so **`pct` cannot change the
header's length**:

```
1) header length by (legacy,pct) over pct = 0,5,...,100:  [(False, 86), (True, 98)]
```

Two values, one per `legacy` flag; the pct axis is flat. Measured cost on the repaint path:

```
2) coverage() calls per refresh_canvas: 3
3) coverage() calls per J keypress:     2
```

**Yes, the perf-shape suite is green because it does not cover this path.**
`tests/test_repair_perf_shape.py` holds two arms, and the A-3 census shows it contributes a
single arg-ful `.render(...)` site — it drives the renderer **directly**, never through
`MapScreen`, so `_canvas_size` and `header_rows` are outside it entirely.

Bounded by `MAX_RENDER_NODES = 12000`, so this is a cost finding rather than a hang, but it
is pure waste on the key-repeat path. Pass a constant (`pct=100`) or hoist the meter out of
the length calculation, with a one-line note saying why the number is irrelevant to width.

---

# Evidence checklist

- [x] **Diff read in full for the fix-round-2 surface** — `mapper/views/layered.py`
      (`_header_line` 362-399, `header_rows` 402-440), `mapper/app.py` (`_header_rows`
      /`_canvas_size` 1380-1410, `_declare_after_layout` 1510-1545, minimap guard
      1740-1755), `tests/test_overflow.py` 265-560 and 713-770, `tests/test_pan.py`
      193-251, `tests/test_fold.py` 181-231 and 531-580, `tests/test_a3_census.py` 125-165,
      `tests/test_inc3_census.py` 318-345.
- [x] **Correctness pass** — 943-config sweeps on `legacy` first-look and post-repaint,
      288-config sweep on `anidado`; header charge measured against a real render.
- [x] **Simplicity pass** — no premature abstraction found; `_header_line` extraction is
      the right shape. F6 is waste, not over-engineering.
- [x] **Reuse / duplication** — one duplication found and it is the load-bearing one:
      `tests/test_overflow.py:_header_rows` re-types the product's row arithmetic (F2c).
- [x] **Tests reviewed for intent** — three arms found to be green for the wrong reason:
      the header pin (circular instrument), `B-56` (size list excludes the failing band),
      the artifact scan (guard keyed to a transient tracking state).
- [x] **Verdict explicit** — BLOCK.
- [x] **Shared working tree untouched** — all mutation in `<scratch>/exp3`, every restore
      proven by `sha256sum -c`.

# Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — F1, F2 and F3 must be fixed before advancing**

**F1** is a five-minute fix and is non-negotiable: the increment currently cannot be
committed green. **F3** is a real operator-visible regression of the exact residual this
round claimed to close, with a small fix (`on_resize`) and a size list to widen. **F2** is
the one that matters most for the batch's discipline: the fix is behaviourally better than
what it replaced, but its central safety claim is false as measured and the arm asserting
it is structurally unable to falsify it — which is the same failure that produced `B-61`,
relocated rather than removed.

The rest of fix round 2 is good work and I found nothing wrong with it: F-A is landed
honestly and forces its own removal, the A-3 bump is itemised and every site checks out,
the five F-D conversions kill by their own oracles, and the ledger and ruff deltas are
exactly what was claimed.
