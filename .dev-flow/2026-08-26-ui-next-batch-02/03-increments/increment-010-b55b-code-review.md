# Increment 010 — Inc-B55b — Independent Code Review

**Reviewer:** code-reviewer (independent)
**Range:** `git diff 10fd573..f828d7b -- mapper/ tests/`
**Tree at review:** `f828d7b`, clean on entry, byte-identical on exit (hashes below).
**Verdict: BLOCK** — one HIGH finding, empirically reproduced, with a fix verified against
the full suite and a 234-combination sweep.

---

## Verdict summary

| | |
|---|---|
| HIGH | 1 (F1) |
| MEDIUM | 6 (F2–F7) |
| LOW | 5 (F8–F12) |
| Verified-OK (explicitly checked, no defect) | 7 (V1–V7) |

The construction is right in its shape. The cell-ownership replay is the correct answer to
`M-N06.3-b`, the one-pass sharing is right, the body move is faithful, and `AT-059` kills
every mutant I aimed at the predicate. What fails is a **boundary case the predicate excuses
instead of failing** (F1), and — matching the calibration note exactly — **five of the
comments that explain the measurements are wrong on checkable numbers** (F3, F4, F5, F8, F9).

---

## F1 — Canvas-edge clipping is EXCUSED, not failed [Severity: HIGH]

**Where:** `mapper/views/radial.py:280-287`

**What.** The gate skips the `title_cells` append as well as the `owners` write:

```python
if (x + j, y) not in cv.cells:
    continue
owners[(x + j, y)] = nid
if j:
    title_cells.setdefault(nid, []).append((x + j, y))
```

A title cell that falls outside the canvas therefore never enters `cells`, so
`all(owners.get(c) == nid for c in cells)` **never examines it**. The node is not failed —
its requirement is silently reduced to the cells that happened to fit. Only the
*all-cells-clipped* case fails, via the separate `if cells and` guard.

**Fired, not reasoned.** At `legacy` 20×30 (`_canvas_size` → 20×15, `inner=18`, `body_h=11`)
the root pill needs `cw = 21 > inner = 18`, so its last cell is refused. Measured frame:

```
row 8|◆Sistema ERP Legac  |          <- the trailing "y" is gone
declared hidden = ['inv', 'rrhh']    <- 'erp' declared PAINTED
'Sistema ERP Legacy' in frame? False
```

**Why it matters.** This is over-declaration in the dangerous direction: `LLR-N06.3.3` makes
the absence of `erp` from the hidden set a positive claim that the operator can read it, and
they cannot. It is `CR-F1` / `B-61`'s defect verbatim — "declared nodes that leave no trace"
— one renderer over. `w=20` is the floor `_canvas_size` enforces (`app.py:1448`), so this is
the edge of the supported band, not outside it. The ledger catches *pill-on-pill* clipping
(row 11 shows `●Inv●Almacen`, and `inv` is correctly declared hidden); it misses
*canvas-edge* clipping. That asymmetry has no stated justification.

**Suggested fix** — record the demand unconditionally, gate only the ownership:

```python
            if j:
                title_cells.setdefault(nid, []).append((x + j, y))
            if (x + j, y) not in cv.cells:
                continue
            owners[(x + j, y)] = nid
```

An out-of-bounds cell is then in `cells` with `owners.get(c) is None != nid`, so the node
fails — which is what the comment at `:310-315` already claims happens.

**Fix verified (fired):** full suite `99 passed`; the 234-combination sweep goes from
**1 disagreement to 0**. No arm regresses.

---

## F2 — The predicate comment asserts the opposite of F1's behaviour [MEDIUM]

**Where:** `mapper/views/radial.py:310-315`

> "A cell outside the canvas is dropped by `put`, so it never enters `owners` and **the node
> fails this test** — but ONLY because the recording above is gated on the put having landed."

False. The cell also never enters `title_cells`, so the node **passes** on its survivors.
This is the same class as the defect already recorded in this file's history (a comment
describing `put`'s behaviour while the ledger did something else) — the correction went half
the distance: the gate now prevents crediting an unlanded cell, but does not make a missing
cell *disqualifying*. F1's fix makes this sentence true; ship them together.

---

## F3 — "over-declares by 6 of 8 at 30x6" is wrong [MEDIUM]

**Where:** `mapper/views/radial.py:218` (the load-bearing justification for the whole
construction), echoed as `M-N06.3-b`.

**Measured at 30×6 on `legacy`:** `_canvas_size` → 30×1, `body_h = -3`, canvas region has
**0 rows**, replay paints **0 of 8**, placement (`frozenset(pos)`) would claim 8 →
over-declares by **8 of 8, not 6**. Confirmed by a second route: mutant M3
(`painted = frozenset(pos)`) reddens both 30×16 arms, where the truth is likewise 0 painted.

The "6 of 8" appears to be a stale carry from the pre-B55 frame-trace figure in
`app.py:1607` ("2 of 8 traced" → 6 not traced), which is a *different quantity* measured
under a *different predicate*. **Fix:** state 8 of 8, or cite the size the 6 actually came from.

---

## F4 — "the full-title read traces 0 of 8 at five sizes" is refuted; the truncation is untested [MEDIUM]

**Where:** `tests/test_overflow.py:1623` and `mapper/views/radial.py:304-307`.

**Measured.** I computed the oracle both ways (`title[:18]` vs. full title) at 12
size/fixture combinations including all five `AT059_SIZES`. The two are **identical at every
one**. At 80×24 and 118×34 the full-title read finds 8 of 8 / 7 of 7 *visible* — not "0 of 8".

**Cause.** No fixture title exceeds 18 characters (longest: `'Sistema ERP Legacy'`, exactly
18), so `[:18]` is the identity on every node the suite renders.

**Fired.** Mutant M5 — remove `[:18]` from the test oracle — **survives** all 14 arms.
Mutant M6 — widen the renderer's `title[:18]` to `[:60]` — **survives the full 99-test suite**.
The distinction the comment calls "not cosmetic" is, in this suite, entirely inert, and the
magic number `18` is now spelled in two unpinned places (`radial.py:235`,
`test_overflow.py:1622`) — the same `F7` shape this increment set out to close for the sentence.

**Suggested fix:** either add a fixture node with a >18-char title (which would make the
claim true and kill M5/M6), or delete the measurement sentence and state the truncation as a
design fact rather than a measured one. Coverage gap handed to `qa-reviewer`.

---

## F5 — The no-fixed-point argument's stated reason is false [MEDIUM]

**Where:** `mapper/views/radial.py:334-338`

> "`render` emits `1 + body_h` rows against a budget of `h = body_h + 4`, so **the header can
> never evict a body row** and the count cannot change by being declared."

The row arithmetic is right (`1 + body_h = h - 3 ≤ h`) but it is not the operative constraint.
The header is rendered into a wrapping `Static` (`#map-canvas`, `app.py:3494`, no `no_wrap`),
and **measured, it occupies two physical rows** at 24×20 and 30×16:

```
row0='◆ mapper · mapa mental  ▽ 8   '
row1='fuera de vista                '
```

So the header *does* consume body budget. `app.py:1442-1458` records that this exact
reasoning already failed for `layered` (`B-61`): "Charging 2 there left the screen believing
one or two more body rows survived than the region could show, and `painted_ids` declared
nodes that leave no trace." Radial has no `header_rows` equivalent.

**The conclusion is nevertheless correct, for a stronger reason the comment does not give:**
`painted` is computed at `:316-319`, **before the header is constructed at `:321-342`**, and
takes no input from it. There is no feedback edge at all, so no fixed point is possible in
principle — independent of row arithmetic. (Clipping margin, measured: region rows `= h + 1`,
logical lines `= h - 3`, so a body row is clipped only once the header wraps to **6+**
physical rows; at the `w = 20` floor it wraps to 3. Safe, with ~2× margin, but unmeasured.)

**Suggested fix:** replace the row-arithmetic sentence with the no-feedback-edge argument,
which is airtight, and note the wrap margin as the thing that keeps the *frame* honest.

---

## F6 — AT-058's "absent" arm cannot distinguish the state it simulates [MEDIUM]

**Where:** `tests/test_overflow.py:1328-1345`; seam at `mapper/app.py:2243-2251`.

You flagged that the simulation replaces the dispatch rather than going through it. The
sharper problem is **downstream of that**: there is nothing to observe even if it did.

`_pagination_text` has no `None` branch — it has `if hidden:`, which is equally false for
`None` and for `frozenset()`. So the "absent" strip is byte-identical to a declaring view
that happens to hide nothing.

**Fired.** Mutant A1 — `_unpainted_ids`: `if declare is None: return None` →
`return frozenset()` — **passes the entire 99-test suite**, including this arm and `tc_038`.
The `None` value has zero observable consequence anywhere the suite looks.

**Which side of the line.** By your own criterion — "legitimate exactly when the property
belongs to the SEAM and the arm declares the simulation; the line is whether it exercises the
seam's real code path" — it is **on the legitimate side**: it does traverse
`_unpainted_ids`'s real `is None` branch and `_pagination_text`'s real `if hidden:`, and it
declares the simulation at length. It is not fiction.

It is, however, **mislabelled**. Its real content is a *two*-state guard — `broken` (distinct
words) vs. not-broken (silence) — wearing a three-state docstring. `len({declaring, absent,
broken}) == 3` passes because `declaring` is a frame that hides something, not because
`absent` has an identity of its own.

**Right construction (cheapest honest version):** keep the arm and the simulation, and change
what it claims. Assert explicitly that absent and nothing-hidden **share** the silent strip by
design, and that the load-bearing distinction is `broken != silence`. That makes the label
match the content without inventing an observable.
If the three-state contract is genuinely wanted, `None` needs its own words in
`_pagination_text` — at which point A1 dies and the arm becomes real. That is a requirements
decision (does a view that declares nothing deserve distinct text?), not a reviewer's call;
raise it at `LLR-N06.3.3` rather than deciding it in the test.

---

## F7 — `_unpainted_ids`'s docstring is stale, and it is the authoritative one [MEDIUM]

**Where:** `mapper/app.py:1605-1610`

> "`painted_ids` lives on `views/layered.py` **only**, and `outline` and `radial` **also hide
> nodes without declaring them** (measured at 30x6 on `legacy`: 5 of 8 and 2 of 8 traced).
> That hole is carried as `B-55` **to Inc-5**."

All three clauses are now false: `painted_ids` is exported by three modules (the census arm
asserts exactly that), both views declare, and `B-55` is closed. The stale "2 of 8 traced"
figure here is also the likely source of F3's wrong number. The increment updated the
`_painted_ids_for` comment and the tests but left the docstring that *defines the `None`
contract* describing the pre-B-55 world — in a file whose thesis this increment is ("one
spelling, consumed rather than repeated").

**Fix:** rewrite the second paragraph to state the surviving reason for `None` (a layout
failure, and a future view that declares nothing by design), and drop the B-55 carry.

---

## F8 — `overflow_phrase`'s stated reason for returning `str` is false [LOW]

**Where:** `mapper/views/layered.py:38-41`

> "Returned as a `str` rather than a `Text` because **its three callers style it differently**
> at their own seams."

They do not. All three apply `darkside.INK`:

- `layered.py:417` — `style=darkside.INK`
- `radial.py:341` — `style=darkside.INK`
- `app.py:2251` — `style=darkside.INK`

**Is `str` the right contract?** Yes, but on the *other* ground the docstring gives — the
padding genuinely differs (two leading spaces vs. one trailing), and `Text` composition
across differing padding is worse. So: keep `str`, fix the sentence. Worth noting that the
increment single-sourced the **words** and left the **style** spelled three times; if `F7`'s
argument holds for one it holds for the other, and that is a fair thing to carry.

---

## F9 — The `body_h` worked example is wrong [LOW]

**Where:** `mapper/views/radial.py:268-270`

> "`body_h` can be ZERO — at a 30x16 terminal `_canvas_size` hands this renderer h=4, so
> `h - 4` is 0."

Measured: at 30×16, `_canvas_size` returns **h=3** → `body_h = -1`. At 30×6, h=1 →
`body_h = -3`. The h=4 / `body_h = 0` case is **50×16**, a different size. Behaviour is
correct either way (`range(-1)` is empty and `put` refuses), but the comment names the wrong
size and understates the range as "zero" when it is negative.

---

## F10 — "16 size/fixture combinations" is not reproducible from the tree [LOW]

**Where:** `mapper/app.py:1663`, `tests/test_inc3_census.py:400`

The suite exercises radial's declaration in **13** arms: 10 (`AT-059`, 5 sizes × 2 fixtures)
+ 3 (`AT-057`, 3 sizes × `legacy` only — that arm hardcodes the fixture). The 16 is presumably
your offline 8×2 sweep, which is not checked in. A reader auditing the claim counts 13 and
cannot find 16. **Fix:** cite the suite's 13, or name the sweep as an offline measurement.

---

## F11 — Two newly added ledger decisions have no discriminating arm [LOW]

Both survive the **full 99-test suite**:

- **M9** — `if j:` → include the `j == 0` pad in `title_cells` (`radial.py:283`). A genuine
  semantic change (a later node overwriting the marker cell would then disqualify), just
  unreachable by these fixtures.
- **M10** — delete the marker's ownership record (`radial.py:298-299`). Its only effect is to
  catch a *marker*-on-title overwrite; in every sampled frame the victim already fails via a
  title-on-title collision, so the line is correct but unexercised.

Neither is a defect. Recording them so the increment does not claim coverage it lacks.

---

## F12 — `MAX_RENDER_NODES`'s rationale is now stale for radial [LOW]

**Where:** `mapper/views/radial.py:25-29` (adjacent, not diffed — but this diff is what
invalidated it).

> "At 12000 nodes the worst **render** measured 0.29 s; at 24000 it measured 1.01 s, which is
> past the point a redraw still feels immediate."

**Measured:** `painted_ids` costs the same as `render` (ratio 0.99 over 2000 iterations), so a
refresh now costs **1.99×** one render. The bound was chosen against a 1× redraw; at 12000
nodes a redraw is now ~0.58 s, half-way to the figure the comment calls unacceptable. The
amplification itself is the trade `outline` already made and is correctly carried — the
**bound's justification** is what went stale. Note only; no action required this increment.

---

## Verified OK — checked, no defect

- **V1 — the ~170-line body move is FAITHFUL.** *Fired, not reasoned.* I extracted
  `10fd573:mapper/views/radial.py`, dedented `render`'s body by exactly 4 columns (0 lines
  failed to dedent) and diffed it against `_paint`'s body. **Every hunk is a pure addition.**
  Zero deletions, zero reorderings, zero modified lines other than the three returns becoming
  tuples. The `place`/`tag` closures, the cycle guard, the `on_path`/`branch_of` precedence
  chain, and the coercion site `darkside.plain(node.ficha.title)[:18]` are byte-identical.
- **V2 — "`ch` is always a single character."** True: `ch` iterates `" " + title`, so every
  value is a length-1 `str`, always truthy. `put`'s `ch` conjunct can never refuse here.
- **V3 — "an out-of-bounds cell cannot have been stored by any earlier node."** True.
  `self.cells` is written at exactly one site, `canvas.py:105`, inside the bounds guard
  (grepped; `text()` routes through `put`, and `bgs`/`dots`/`bits` are separate dicts). So
  `cv.cells` can never contain an out-of-bounds key from any writer. **The exactness claim
  holds as stated** — F1 is a different failure: the gate is exact about *what landed* and
  wrong about *what that should mean*.
- **V4 — `AT-059` has real discriminating power** (four mutants fired, all killed):

  | Mutant | Killed |
  |---|---|
  | M1 — drop the put-landed gate (your prior bug) | 3 of 10 |
  | M2 — `all` → `any` | 3 of 10 |
  | M3 — placement-derived (`M-N06.3-b`) | **6 of 10 = 3 of 5 sizes** |
  | M4 — saturate (`painted = frozenset()`) | 7 of 10 |

  **Your "3 of 5 sizes" for the placement mutant is CONFIRMED.** (Caveat: the non-degeneracy
  guard at `:1888`, `1 <= len(frame_hidden) <= total`, excludes the `0 == 0` end as its
  comment says but **not** the saturated `total == total` end — 3 of 10 arms sit there. M4
  dying at 7 arms means the parametrization compensates; the guard alone is weaker than it reads.)
- **V5 — outline's remaining spelling IS pinned.** Mutant F7-B (drift outline's wording to
  "fuera de pantalla") reddens 2 arms (`AT-057` outline at 35×14 and 30×16); the
  single-sourced phrase reddens 15. So the surviving spelling **cannot drift silently**, and
  the carry to `Inc-REPAIR` as a 2-line change (`outline.py:9` import + `:243` append) is
  safe. **Leaving one spelling behind was the right call** — widening to 4 files bought
  nothing the guard was not already providing.
- **V6 — "~2× amplification" CONFIRMED.** Measured 1.99× (render 6.159 s vs. `painted_ids`
  6.069 s over 2000 iterations each). The trade is the same one `outline` made and is
  correctly carried. See F12 for the knock-on.
- **V7 — fixture hygiene.** No substring collisions between node images (which would make the
  `img not in painted` oracle credit a node for a neighbour's text), and no empty/blank
  titles (which would diverge: the oracle skips a falsy image, the predicate excludes a node
  with no `title_cells` entry). Both risks are latent, not live.

---

## Boundaries

**Reviewed.** All 5 diffed files, in full. `mapper/canvas.py` (`put`, `rows`, every writer to
`cells`), `mapper/views/outline.py:236-250`, `mapper/darkside.py:plain`,
`mapper/app.py:_unpainted_ids` / `_pagination_text` / the `B-61` note, and the two fixtures.

**Fired (11 mutants + 2 sweeps), all restored.** M1–M6, M9, M10, F7-A, F7-B, A1, the F1
candidate fix; a 12-combination numeric probe; a 234-combination property sweep; a 2000-iteration
perf measurement.

**Did not review** (out of lane): security (`darkside.plain`'s coercion adequacy → 
`security-reviewer`); suite execution beyond the arms above and functional/coverage adequacy → 
`qa-reviewer`, to whom F4's untested truncation and F11's unexercised paths are handed.

**Could not determine.** (a) Whether `node.ficha.title` can be empty in production — the
model's constraints were not traced; if it can, an empty title yields no `title_cells` entry
and the node is declared hidden while its marker is plainly visible, and the AT-059 oracle
would disagree (it skips a falsy image). Latent, not reachable from these fixtures.
(b) Whether the "16 combinations" sweep exists outside the tree (F10) — I could only count 13
arms. (c) Whether F1's 20×30 case *should* count `erp` as hidden is arguably a product call;
what is not arguable is that the declaration and the frame disagree there, so `AT-059`'s
property is false at a reachable size its parametrization does not sample.

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/views/radial.py` (429 lines changed), `mapper/app.py:45-53,1656-1666,2244-2252`, `mapper/views/layered.py:23-47,414-418`, `tests/test_overflow.py`, `tests/test_inc3_census.py:393-410`.
- [x] **Correctness pass (edge / None / error paths)** — F1 found at the canvas-edge boundary and reproduced at `legacy` 20×30; `body_h <= 0` confirmed handled (F9 corrects the example); `None` path traced through `_unpainted_ids:1640` → `_pagination_text:2243`.
- [x] **Simplicity pass** — no premature abstraction. `_paint` returning a tuple with two thin consumers is the right shape and matches `outline`. No finding.
- [x] **Reuse / duplication** — `overflow_phrase` correctly consumed at 3 sites; the 4th (`outline.py:243`) is pinned (V5). The magic `18` is newly duplicated unpinned (F4); `darkside.INK` remains triplicated (F8).
- [x] **Tests reviewed for intent** — `AT-059` kills 4 of 4 aimed mutants (V4); `AT-058`'s absent arm kills 0 (F6); the oracle's truncation kills 0 (F4); `tc_038` and both `AT-058` arms confirmed **updated, not narrowed** — each still asserts a strictly stronger property than before (`tc_038` now asserts strip/declaration equality for radial where it previously asserted only token-absence).
- [x] **Verdict explicit** — BLOCK.

---

## Boundary attestation

Sole writer; no evidence of another writer (`git status` clean on entry and exit, no
unexpected mtimes). No mutating git commands run. Every mutation was byte-level with a
CRLF-encoded anchor and **an asserted match count before firing** (the harness refuses to
write on a count mismatch), `__pycache__` purged around each, and pristine sha256 re-verified
after each restore.

Final state — `git status --porcelain` empty, `git diff --stat` empty:

```
mapper/views/radial.py   61e9e156372a9a6e   (pristine)
mapper/app.py            bee1e690dacf0e5e   (pristine)
mapper/views/layered.py  29455bce9c2817dd   (pristine)
tests/test_overflow.py   7a501df099398d0b   (pristine)
mapper/views/outline.py  88a5d987179a3f6b   (pristine)
```

Pristine baseline re-confirmed after all mutants: **99 passed**.

---

## To advance

1. **F1** — apply the 3-line reorder; it is the block. (Verified: 99/99 + sweep 1→0.)
2. **F2, F3, F5, F8, F9** — correct the five false comment claims. F2 becomes true via F1's fix.
3. **F6** — relabel the AT-058 arm to the two-state property it actually holds, or raise the
   `None`-observable question at `LLR-N06.3.3`.
4. **F4, F7, F10** — a fixture with a >18-char title (or drop the claim); rewrite
   `_unpainted_ids`'s docstring; correct the combination count.
5. Consider adding **20×30** (or any `inner < max pill width` size) to `AT059_SIZES` — it is
   the size that catches F1, and its absence is why the increment reached the gate green.
