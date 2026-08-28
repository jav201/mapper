# Code Review Confirmation — Increment 3 (post-fix tree)

## VERDICT: **BLOCK** — 2 HIGH (new), 9 MEDIUM, 8 LOW

Four of the five blocking HIGHs are **genuinely discharged**, each re-executed rather than re-read:
`SEC-F1`, `SEC-F2`, `CR-F2`, `CR-F3`. The fifth — **`CR-F1` — is NOT discharged**: the three
reported sizes are fixed and the mutant dies by its documented oracle, but the identical
over-declaration reproduces at **22+ reachable terminal sizes on the shipped fixtures**, because the
fix is written against `HEADER_ROWS = 2` while the header measurably occupies 3 rows at canvas
width 21–28 (and 3 at width ≤ 34 with more nodes) and 4 rows at width 20. This is the same fact that
refutes the author's **`B-61` "latent, not live"** claim — the only thing that stood between `B-61`
and a sixth HIGH, and it did not survive execution. Three independent hands (two subagent lanes and
my own repro in a third copy) reached the same frames.

The second HIGH is the **`B-60` carry, recorded on measurements that are wrong in the same two ways
the prior round blocked `CR-F3` for**: the header numeral is *absent*, not stale, at ordinary sizes,
and "any repaint at all reconciles them" is false — measured over nine keys, only `l` (and `o`)
heal it; `j`/`k`/`h`/arrows/`tab` do not. The standard is the increment's own: a carry recorded on
wrong measurements cannot be accepted as evidence.

Everything was executed in detached copies; the shared working tree was never written (evidence in
§7), with one instructed exception: this file itself, which is new and touches nothing existing.

---

## 1 · Scope reviewed

- `git diff HEAD` over base `954f8f3` on `feat/ui-next-batch-02` plus untracked files: 22 files,
  +3635/−101. Source: `mapper/app.py`, `mapper/views/layered.py`, `mapper/views/outline.py`,
  `mapper/views/state.py`, `mapper/widgets/rail.py`, `mapper/keymap.py`. Diff read in full,
  including the six smaller source diffs no fix-round claim covers.
- Prior verdicts (`increment-003-code-review.md`, `increment-003-security-review.md`) and the fix
  record (`increment-003.md` §11) read **after** independent execution was planned, per the
  fresh-reviewer mandate.
- Method: five parallel execution lanes, each in its own full copy of the working tree
  (`wsA`…`wsE`), plus my own probes in `export`/`wsF`. Every mutation restored and proven by
  sha256 returning to its pre-mutation value.

**Harness defect found and neutralised before any verdict:** a bare copy of the tree is not a git
repo, and several census arms shell out to `git ls-files` (the `SEC-F8` carry). A suite run in a
non-git copy produces ~25 spurious FAILED census arms. Reproduced, then every lane was instructed to
`git init && git add -A` and to re-establish a green baseline before trusting any mutant verdict.
Post-correction baseline in every lane: **789 passed, 17 deselected, exit 0**.

---

## 2 · The five HIGHs — DISCHARGED or NOT, by execution

### SEC-F1 (schema key → SVG) — **DISCHARGED**

- **The crux held:** the widened census fixture actually enters the legacy branch. Instrumented in
  the lane's copy: `bool(graph.schema)` evaluated True at all 3 parametrised sizes and the `sf.key`
  sink line executed **24×** during the arm; raw `{0x1, 0x202e}` at the sink arrive as `{0xfffd}`
  on the canvas. The fix is not the original defect wearing a widened fixture.
- **End-to-end re-run of the defect:** hostile sidecar (`schema[0].key = U+202E`,
  `schema[1].key = U+0001`, hostile labels) through the real `MapStore.load` → default
  `LayeredRenderer` → `export.save_svg`: **zero banned code points in terminal and SVG;
  `ElementTree` parses.** With the sink coercion reverted, both leak and the SVG breaks
  (`ParseError`) — the defect and the fix both reproduce.
- **M1 kill mode:** documented oracle (`assert leaked == []`), not a crash.
- **M14 (`SEC-F4`) spot-check:** attribute-form renderer wiring reddens **2 arms** by documented
  oracles, including the equality pin that previously survived with 23 passing. Counterfactual
  executed: `ast.Name`-only census + the mutant = mutant survives — the `ast.Attribute` widening is
  load-bearing, not decorative.

### SEC-F2 (minimap title) and the self-reported breadcrumb — **DISCHARGED**

- Hostile titles through the real `MapStore` + `run_test(size=(160,40))`: minimap region, canvas,
  whole composited frame, raw minimap `Text` — all clean post-fix.
- **M2** (minimap coercion removed): the `LLR-N06.2.3` arm goes RED by its documented
  region-half assertion. **M3** (crumb coercion removed): RED by the **frame half** — consistent
  with the author's account of how the breadcrumb defect was found.
- **The id-less blind spot is generally closed, not one-bug-closed:** a *new, different* id-less
  hostile leak injected into another `refresh_canvas`-touched sink (`KeyBar`) was caught by the
  frame half. The census's frame half is genuinely independent of widget ids.
- Legitimate-input check: accented Spanish titles and ordinary crumbs pass `darkside.plain`
  unaltered; a title that coerces to empty falls back to `cid` (verified behaviour, correct).

### CR-F1 (`_canvas_size` short-terminal over-declaration) — **NOT DISCHARGED** → see HIGH-1

What is fixed, confirmed: at terminals `(31,18)`, `(50,14)`, `(100,10)` — `region.height == 2`,
`h = 1`, `row_limit = 0`, `declared = []`, strip `▽ 8 fuera de vista`, corroborated by **two
independent oracles** (the shipped one and a lane-written glyph-anchored one that recomputes no
layout) and by direct row-reading (zero `▐` card marks in the frames). The boundary transition
`region.height == 3 → row_limit = 1` is right **where the header truly is 2 rows**: exactly one
body row paints and declared == traced at `(31,16)`, `(40,16)`, `(50,15)`, `(80,12)`, `(100,11)`,
`(120,10)`. **M4** (branch reverted) is killed by the documented `assert declared == traced` at the
documented terminal.

What is not fixed: `row_limit` is priced with `HEADER_ROWS = 2`, and the header's *measured*
physical row count is **4 at canvas w=20, 3 at w=21–28** (extending to w=34 at high node counts).
The `region.height <= HEADER_ROWS` guard cannot see those regions — they are 3, 8 and 13 rows
tall — so the renderer believes 1–2 more body rows survive than the region can show, and
`painted_ids` declares nodes that leave no trace. Reproduced across ≈1180 driven sizes in one lane
(22 disagreements, all over-declaring, all at canvas width ≤ 28) and 280 in another (10
disagreements, 7 on shipped fixtures), and **re-reproduced by me in a third copy**:

```
term=(28,17) region_h=3  canvas=(28,2)  declared=['erp']              traced=[]            strip '▽ 7'  truth 8   <- the original defect verbatim
term=(28,30) region_h=13 canvas=(28,12) declared=['cont','erp','fin','pres'] traced=['erp','fin']  strip '▽ 4'  truth 6
term=(26,19) region_h=3  canvas=(26,2)  declared=['erp']              traced=[]            strip '▽ 7'  truth 8
term=(80,24) control: declared == traced, 8 of 8                                                    <- fix intact where header is 2 rows
```

The batch's own identity arm goes **RED on the unmutated tree** the moment these sizes enter its
sweep (executed in-lane: `terminal (22, 30): … declares ['fin'] with no trace`). It is green today
only because the sweep's narrowest width is 31 — one column above the band. The band is reachable:
`_canvas_size` floors `w` at 20 and `_apply_region_visibility` hides both side regions below 58
columns, so a narrow terminal lands here directly.

### CR-F2 (naive fold-sum at the paint site) — **DISCHARGED**

- **M5 re-run** (a genuine `len(viewport-hidden) + Σ per-branch descendants` in
  `_pagination_text`; liveness proven first — strip paints `▽ 6` against truth 4): `TC-039` is the
  one arm that goes RED, at its **strip-reading** assertion:
  `AssertionError: ▰▱▱▱▱▱▱ 1/7 ▽ 6 fuera de vista … assert 6 == 4` — a clean documented oracle,
  not the `TC-040` crash pattern.
- **TC-039 reads the strip for real**, proven by instrumentation, not reading: the arm's read makes
  exactly one `_compositor.render_strips` call, and the text it clips is region-width (140 chars)
  vs 35 for the widget's own `render().plain`. Under M5 the three helper-level assertions all pass
  and execution reaches the strip assertion — the arm has genuinely moved to the paint site.
- An off-by-one sum variant (`+1` when folded) is also killed at the same assertion.
- Residual (MEDIUM-3 below): a *partial-overlap* sum mutant survives the whole module while
  painting `▽ 15` on an 8-node map.

### CR-F3 (`B-56` closed by declaration-only post-layout repaint) — **DISCHARGED**, carry mis-graded

- **The close is real at the sizes previously measured absent.** Real app, mount + pauses, no
  repaint, no keypress, truth from an independent trace: `legacy` 50×20 → `▽ 4` (truth 4), 60×20 →
  `▽ 4` (truth 4), 30×20 → `▽ 7` (truth 7), 40×20 → `▽ 7`, `anidado` 30–60×20 all agree, and the
  zero case correctly paints no numeral.
- **M6** (scheduling removed): RED by the documented oracle at the documented size and mode —
  `(50, 20): the strip declares None on a first look that is hiding 4`. Not a crash.
- **Both at-risk arms genuinely green** on the shipped tree, and **both alternative-cost
  measurements reproduce**: `call_after_refresh(refresh_canvas)` reddens the `LLR-CNV.3.1` focus
  arm (`assert 'rail' == 'inspector'` — a real behavioural regression), and the canvas+strip
  variant reddens the A-3 pin (`derived 50 … against a pinned 49`).
- **But the two costs are not commensurable, and the packet presents them as if they were.** The
  A-3 pin's own docstring says it is updated deliberately with its reason, and it has already moved
  35→50→51→49 across increments; the canvas+strip variant keeps the focus arm green, keeps overflow
  green, **and closes `B-60`** — for the price of one deliberate pin bump. Executed in-lane: under
  that variant, header == strip == truth at all four previously-diverging sizes.
- Timing measured honestly: the fix needs **two pump turns**; at one turn the strip is still absent
  at exactly 50×20/60×20. The acceptance arm's `range(3)` pauses are generous enough to hide this.
  Fed into MEDIUM-4.

---

## 3 · The three adjudications — ruled by execution

### `CR-F7` (pan docstring / "H·L are inert") — **the author is right on the unit; the reviewer's underlying worry is right about the product**

Both readings reproduce exactly, in two independent lanes: renderer `w=118` → `max_pan_x = 0`
(the reviewer's number); real screen at a 118×34 **terminal** → chrome takes 60 columns, canvas
**58×25**, `max_pan_x = 49`, `max_pan_y = 10` (the author's numbers), and real `L`/`J` presses move
the window (`(0,0)→(8,0)→(8,4)`). The corrected docstring states only true, measured numbers, and
the new arm asserts both halves non-vacuously (a shrunk fixture reddens the positive half; a
widened one reddens the asserted negative half).

**Ruling: the review's `CR-F7` is refuted as written — the unit was the defect.** However, the
product consequence the review was reaching for is real and sharper than either party recorded: a
2-D sweep over the **shipped** maps found horizontal pan live at exactly **one** terminal width
(40 — with `max_pan_x = 7`, less than one `PAN_STEP_X`, exhausted by a single press) and inert at
every other width × height driven; vertical pan on the shipped maps dies at height ≥ ~34. The only
map with live two-axis travel is `pan_graph`, a test-support fixture that ships in no `fixtures/`
or `maps/` directory. **The pan mechanism is correct and well-tested; no shipped map exercises
it.** Recorded as product feedback, not a defect in the increment.

### `CR-F6` half-fix (`oracle_traced` takes `pan_x`, not `pan_y`) — **the author's reasoning holds for divergence; a lockstep blind spot remains**

- `rows` **is** the already-panned frame: `_drive` sets the pan, repaints, and only then reads
  `canvas_rows`; executed, the frames at `pan_y = 0` vs `2` differ and `erp` drops out of the
  declaration. The vertical component is genuinely carried by `rows`; the panned configuration row
  `(30, 12, (), (8, 2))` has live travel in both axes (`max_pan_x = 17`, `max_pan_y = 2` — I
  verified the vertical component discriminates: the declared set changes when `pan_y` goes 0→2),
  and the asserted cardinality is 7.
- **The discriminating injections are caught, symmetrically.** A `painted_ids`-side bug that
  ignores `pan_y` (`_title_image` un-panned) reddens `AT-016` at the panned row
  (`declares ['erp'] painted with no trace`); the off-by-one variant reddens 6 arms; the equivalent
  `pan_x` bug reddens the same arm the same way. **There is no axis asymmetry for
  declaration-vs-render divergence.** The author's `CR-F4` argument against a dead parameter holds.
- **But I found the bound of that guarantee by execution:** a *lockstep* mutant — `geo.place` drops
  `pan_y` entirely, so `render` and `painted_ids` both ignore it — makes vertical pan a complete
  product no-op (`J` changes `screen.pan_y` and nothing on screen) and **survives all 789 tests**
  (run full, exit 0; mutant liveness note: the render is provably invariant under `pan_y` with it
  applied). The identity is structurally blind to lockstep edits, and `oracle_traced` is "invariant
  under `pan_y` by construction" — the docstring states that as a strength; it is also the reason
  no arm can catch this on the vertical axis, while the same lockstep edit on `pan_x` *would* be
  caught (the oracle consumes `pan_x` explicitly). **Ruling: the half-fix reasoning holds;
  the vertical *feature* (as opposed to the declaration identity) has no content-level oracle.**
  MEDIUM-5 below.

### `B-61` "latent, not live" — **REFUTED. Live.** → merged into HIGH-1

The header grid confirms half the author's numbers and corrects the other half: **4 rows at w=20 at
every node count — confirmed** (8 counts); "3 rows at w=30 from n≥40" — the true threshold is
**n = 14** (n=13 → 2 rows, n=14 → 3), the "n≥40" is an artifact of a sample grid that jumps 10→40;
and the band extends past the pin's `w <= 30` bound to **w=34** within `MAX_RENDER_NODES`. The
identity was then probed through the real screen at 280 configurations: **10 break it, 7 on the
shipped fixtures** — e.g. `legacy` at terminal (22,30): header physically 3 rows, `row_limit = 6`,
`fin` declared painted at canvas y=5 which the region cannot show; the frame contains **no card
mark at all** while the strip reads `▽ 7` against a truth of 8. Frames were read directly, not
through the oracle. The author's probe stopped one column and a few heights short of the band.

---

## 4 · The two self-reported defects — confirmed with the same scepticism

- **Breadcrumb**: confirmed fixed and generalised — see SEC-F2 above (M3 killed by the frame half;
  a new id-less sibling injection also caught).
- **`_branch_coverage_glyph` hang**: all three sub-claims reproduce. Pre-fix walk on a 4-node
  cycle: **2,000,001 steps, stack non-empty, unbounded in memory too**; the live method in a
  subprocess died only by SIGKILL at 45 s. The `seen` set fixes it (returns `('█', …)` on the same
  graph). The DAG double-count is real and the shipped number is the correct one (pre-fix 60% on a
  branch that is 75% covered — a two-band glyph error). The regression arm exists and fails by
  **hang, not by pass** (seen removed → the arm runs until an external 120 s kill; shipped → 0.92 s
  green). Caveat: no `pytest-timeout` is configured, so in CI this failure mode is a stuck run
  (LOW-8). Residual on the same path: MEDIUM-6.

---

## 5 · Battery claim ("14 arms, 14 killed, zero survivors")

**8 of the 14 arms were re-executed** across the lanes — M1, M2, M3, M4, M5, M6, M9, M14 — which
includes all three whose subjects are HIGHs plus both named special cases. **All 8 kill, and every
kill is by the arm's documented oracle** (M9 by the claimed TIMEOUT — verified as a genuine hang,
not a slow pass). No `TC-040`-style crash-kill was found among them; the M14 kill that previously
survived now reddens the equality pin itself, with a counterfactual proving the `ast.Attribute`
widening is what does it. The remaining 6 arms (M7, M8, M10–M13) were not independently re-run:
**unverified**, stated rather than assumed.

The zero-survivors claim is true of the battery's own arms. It is **not** true of the mutant space
around the fixes — this pass found three survivors the battery does not cover: the
partial-overlap sum (MEDIUM-3), the one-row-under `_canvas_size` (MEDIUM-2), and the vertical-pan
lockstep drop (MEDIUM-5). Ledger and lint re-verified independently: base `954f8f3` collects 720,
work collects 789 (= 720 + 64 + 5 ✓); ruff 0.8.4 set-wise, scope-matched (`--exclude prototypes`
both sides): **NEW = ∅**, gone = `mapper/views/layered.py F401`.

---

## 6 · New findings

### HIGH-1 — `B-61` is live: the CR-F1 over-declaration recurs wherever the header wraps past `HEADER_ROWS`  [Severity: HIGH]
- **What:** `row_limit` is priced with `HEADER_ROWS = 2`; the header measurably takes 3–4 physical
  rows at canvas widths 20–28 (3 up to w=34 at higher node counts), so `painted_ids` declares 1–2
  rows of nodes that leave no trace, and the `▽ N` numeral under-reports by the same amount. The
  story's promise inverted, on shipped fixtures, at reachable sizes.
- **Where:** `mapper/app.py:1340` (`HEADER_ROWS = 2`), `:1376-1378` (the fix that consumes it);
  pin at `tests/test_overflow.py` (header-rows arm) whose own measurements enumerate the 3/4-row
  band the fix never consumes.
- **Evidence:** three independent reproductions; 22/≈1180 and 10/280 driven configurations;
  `legacy` (28,17) declares `erp` on a frame with zero cards, strip `▽ 7`, truth 8; the shipped
  identity arm goes RED unmutated when the band enters its sweep. Transcripts in §2-CR-F1 and §3-B-61.
- **Suggested fix:** charge the *measured* header height instead of the constant — it is derivable
  at call time from the same `w` (`ceil(len(header_line)/(w-2))`, or have the renderer report it);
  use it in both the `<=` guard and the subtraction. Then extend the identity sweep's widths down
  to 20 (the arm already reddens there today) and re-derive the `B-61` note from the corrected pin
  (whose own bounds are sample artifacts — MEDIUM-9).

### HIGH-2 — the `B-60` carry is recorded on refuted measurements; `TC-038`'s "one truth" holds only after a forced repaint  [Severity: HIGH]
- **What:** the carry ("the header can under-declare on the very first frame … any repaint at all
  reconciles them") is wrong twice, the same two ways `CR-F3` was blocked for: (1) at `legacy`
  50×20/60×20 the header numeral is **absent** while 4 are hidden — `LLR-N06.3.3` makes absence
  mean "nothing hidden", on a declaring surface, at ordinary sizes; (2) measured over nine keys,
  `j`/`k`/`h`/arrows/`tab` do **not** reconcile — only `l` (and `o`) do; a reader who only looks at
  the map keeps two contradicting indicators indefinitely. Meanwhile `TC-038` ("both declaring
  surfaces read one truth, always") calls `refresh_canvas()` before measuring — remove that line
  and it fails `assert 4 == 7` on the first look — and its justifying comment repeats the exact
  "window is one frame, closing at first keypress" measurement the fix round itself retracted.
- **Where:** `mapper/app.py:1220-1232` (the carry note), `tests/test_overflow.py:535-541` (stale
  comment + the load-bearing forced repaint in TC-038).
- **Why it matters:** the increment's own standard — a carry recorded on measurements this far off
  is not evidence — plus a test whose docstring promises a first-look property it deliberately
  repaints away. The cheap close was measured in-lane: the canvas+strip variant reconciles all four
  diverging sizes for one deliberate A-3 pin bump (see §2-CR-F3).
- **Suggested fix:** either take the canvas+strip variant and bump the pin with its reason, or
  re-record `B-60` on the true numbers (absent-not-stale; nav does not heal; TC-038's repaint is
  load-bearing) and delete the stale comment. Either way `TC-038`'s docstring must stop claiming
  "always".

### MEDIUM-1 — `SchemaField.label` reaches the coverage report uncoerced  [Severity: MEDIUM — carry, security lane]
`mapper/screens/coverage.py:88` — `escape(",".join(missing))` strips Rich markup, not control/bidi;
executed leak `['0x1','0x200b','0x202e']` in the "faltantes" cell (adjacent title cell same
treatment). Outside this increment's diff (pre-existing) — same `B-47` class `SEC-F1` just closed at
a sibling sink. Route with the `store.py` `_coerce_text_fields` item already sent to Inc-REPAIR.

### MEDIUM-2 — a one-row-under `_canvas_size` mutant survives all 789 tests  [Severity: MEDIUM]
`return w, region.height - self.HEADER_ROWS` is non-equivalent (permanently discards one body row —
at (31,16) the only visible card disappears) yet the full suite is green with it in place. The
`declared == traced` identity is structurally one-sided: `h` feeds both render and declaration, so
under-sizing shrinks both together. Nothing pins that `h` is as large as the region allows.
Suggested: one canvas-utilisation arm (`row_limit == region.height − measured_header_rows`).

### MEDIUM-3 — no arm drives the paint site on the viewport×fold overlap state; a live sum mutant survives  [Severity: MEDIUM]
A sum that over-counts only when viewport-hidden ∩ fold-hidden is partial paints
**`▽ 15 fuera de vista` on an 8-node map** (`legacy` 30×12 with `erp` folded, and three more
ordinary sizes) with `tests/test_overflow.py` 12/12 green: `AT-015` reads the renderer-written
header, `TC-039` runs at 140×45 where the viewport hides nothing, `TC-038`/B-56 run unfolded. The
shipped code is correct (set difference) — coverage gap on exactly the double-count `LLR-N06.3.1`
forbids. One folded row at a small size in `CONFIGURATIONS`, asserted through the strip, closes it.

### MEDIUM-4 — the pre-layout declaration is composited for one frame, contradicting the `B-60` note's scoping  [Severity: MEDIUM]
The `not region.height` branch's guess produces a strip numeral that is **visible in the composited
frame at pause 0** and replaced at pause 1 (`▽ 7` at (100,10) truth 8; `▽ 5` at (31,18) truth 8) —
the note at `app.py:1229-1232` claims "the strip — the surface the operator reads — is correct".
Every arm pauses ≥ 3 times, so the suite cannot see it. Transient (one frame), hence MEDIUM.

### MEDIUM-5 — vertical pan has no content-level oracle: a lockstep `pan_y` drop survives all 789 tests  [Severity: MEDIUM]
`geo.place` without the `- self.pan_y` term makes `J`/`K` a product no-op (attribute moves, frame
does not) and the **full suite passes** (executed, exit 0). Divergence bugs are caught on both axes
(§3-CR-F6), but render and declaration share `place`, and `oracle_traced` is row-scan-invariant
under `pan_y` by construction — so the one bug class the identity cannot see is the one the oracle
also cannot see, on the vertical axis only (the same lockstep edit on `pan_x` is caught). One arm
asserting canvas rows differ after a live `J` press closes it.

### MEDIUM-6 — `_minimap_text` sits outside `refresh_canvas`'s guard; a raise there kills the app  [Severity: MEDIUM]
`app.py:1698` is past the `try` that closes at `:1676`. Executed: an exception on that path escapes
the pump and `app.is_running` → False on the next repainting keypress. `_branch_coverage_glyph`
also raises `KeyError` on a dangling edge (`children_of` returns unchecked `child_id`s;
`nodes[nid]` at `:1526` throws) — executed; a shipped path creating one was **not** found
(`_remove_subtree` prunes both endpoints; `mermaid.parse` `_ensure_node`s both; csv/github/store
guard), so the KeyError is defence-in-depth — but the unguarded sink is structural, the same
asymmetry `SEC-F3` fixed one helper over (`_unpainted_ids` has its own try/except; the minimap has
none). One guard, matching the sibling.

### MEDIUM-7 — `insp-field-{key}` widget id is built from the raw schema key  [Severity: MEDIUM — carry]
`mapper/widgets/inspector.py:139`: Textual `BadIdentifier` raised out of the inspector rebuild for
`U+202E`, `U+0001` — **and for a legitimate `Ñ`**, in a Spanish-first product. Pre-existing, no
try/except in the rebuild. Not this increment's diff; worth an early Inc-REPAIR slot because the
benign-input crash is one accented schema key away.

### MEDIUM-8 — `_ImportPreviewScreen`'s crumb paints a file-derived name uncoerced  [Severity: MEDIUM — carry]
`app.py:727`: `TabStrip("i", crumb=["import", self.source_path.name])` — a filename with RLO spoofs
the crumb (executed in-lane). Verified **outside every diff hunk** of this increment, so graded as
a carry in the `LLR-N06.2.3` family rather than a blocking finding (the lane that found it graded
HIGH; the fence disagrees). Same one-call fix as the `MapScreen` crumb.

### MEDIUM-9 — the header-rows pin's recorded bounds are artifacts of its own sample grid  [Severity: MEDIUM]
`n ≥ 40 at w=30` is really **n ≥ 14** (grid jumps 10→40); `w ≤ 30` is really **w ≤ 34** at high
node counts (grid jumps 30→50). The arm's assertions are true of what it samples and understate the
band HIGH-1 lives in — part of why `B-61` was mis-read as latent. Densify the grid over n=11..39
and w=31..40, and derive the bounds from the measurements.

### LOW-1 — `_declare_after_layout`'s `query_one` is unguarded; `NoMatches` in the pump kills the app; no reachable trigger found (escape/`q` at 0/1/2 pauses all survive). Latent.
### LOW-2 — `_canvas_size`'s `<=` vs `<` is behaviourally unobservable (proven over 128 sizes); the middle branch earns its place only at `region.height == 1`. Docstring presents the boundary as meaningful; a one-line note prevents a false future "fix".
### LOW-3 — the `borde del territorio` hint is sticky across axes: set on a no-op, never cleared on success; on the shipped maps (where `H`/`L` are always no-ops) it latches immediately and then misdescribes every live `J`. `app.py:1407-1417`.
### LOW-4 — `oracle_traced`'s column-only anchor over-traces on collinear same-image nodes: on `pan_graph` all eight chain nodes share column 96 and image `nivel…`; over-traced in 24/30 panned configurations (PRED-2 held in all 30; PRED-3 fails loudly on such graphs, so a bad configuration cannot be added silently). The docstring's "invariant under `pan_y` by construction" is the blind spot of MEDIUM-5 stated as a strength.
### LOW-5 — TAB is a live path to the schema-letter row: `COERCION_RANGES` preserves `0x09` and the census scan excludes `"\t\n"` — terminal-only misalignment no arm can see. Carry to the coercion ladder's owner.
### LOW-6 — the `[:1]` at the `sf.key` sink counts code points, not cells: a wide char (`日`, emoji) still overflows the `xx += 3` stride exactly as pre-fix (byte-identical, so not a regression), and a valid multi-char key is silently truncated with no ellipsis. `darkside.fit` is the module's consistent instrument.
### LOW-7 — stale narration: `test_overflow.py:535-541`'s `B-56` comment restates the retracted "one frame, closes at first keypress" measurement (see HIGH-2); `on_mount`'s "any repaint at all reconciles" likewise. Comments contradicting the fix round's own corrections.
### LOW-8 — no `pytest-timeout` in `pyproject.toml`: the hang-regression arm fails by hanging, which in CI is a stuck run, not a red report. One dev-dependency and one ini line.

---

## 7 · Working-tree integrity

- Baseline: sha256 over all 319 non-git files of `C:\Users\jjgh8\Github\mapper`, manifest digest
  `a9daf76c34010a8de004737aaea2e2a2cff31d77d800a07bae92003ced115669`, taken before any lane started.
- Re-verified **mid-pass** and **at the end**: `diff` of the manifests → identical, all 319 files.
  (`git status` was not relied on — vacuous for untracked files.)
- All mutation ran in detached copies (`wsA`…`wsF`, `export`); every mutant restore proven by
  sha256 returning to its pre-mutation value, per lane, including cross-checks against the shared
  tree's own digests (`mapper/app.py f9083556…455`, `mapper/views/layered.py d4d82a20…553`,
  `tests/test_overflow.py bd5fd68f…2c5`, `tests/inc3_support.py c980463b…24a` — all matched).
- The single write to the shared tree is **this file**, new and instructed by the gate.

## 8 · Evidence checklist

- [x] Diff read in full — 22 files over `954f8f3`, all six source diffs read line-by-line (§1).
- [x] Correctness pass — five HIGHs re-executed; boundary/edge sweeps ≈1500 driven configurations (§2, §3).
- [x] Simplicity pass — no new premature abstraction found in the fix-round diffs; the one duplication carry (`CR-F11`) stands as recorded.
- [x] Reuse/duplication — `_declared_total`, oracle and censuses checked against shipped utils; `darkside.fit` vs `[:1]` flagged (LOW-6).
- [x] Tests reviewed for intent — three false-confidence patterns found and executed (HIGH-2/TC-038, MEDIUM-2, MEDIUM-5).
- [x] Verdict explicit — **BLOCK** on HIGH-1 and HIGH-2.

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — 2 HIGH.** Fix HIGH-1 (measured header height in `_canvas_size`, widen the identity
  sweep into the 20–30 band) and HIGH-2 (close or honestly re-record `B-60`; un-stale `TC-038`).
  Four of five prior HIGHs are cleanly discharged and the battery's own arms all kill by their
  documented oracles — the fix round's craft is real; what blocks is one recurrence band the
  constant cannot price and one carry recorded on refuted measurements.
