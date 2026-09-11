# Code Review -- Increment `S-B(+C)` (increment-013, defect 2 + caps + floor exception)

**VERDICT: BLOCK**

Gate 1 of 2 (code review). Three HIGH findings, all of the same kind: **the production code is
sound, and the arms that the two ratifications rest on do not discriminate.** Every HIGH was
FIRED, not inferred. None is self-cleared.

| Duty | Verdict |
|---|---|
| 1. `LLR-N06.3.5` EMPTY-FRAME FLOOR EXCEPTION -- wording | **NOT RATIFIED AS WRITTEN.** The normative text is precise, its proviso is load-bearing, its trigger is derived, and its measurements reproduce exactly. One sentence is false: the **`Armed:` sentence**. The arm keys on the CONSEQUENCE (canvas silent), not on the stated geometric trigger. Fix the arm or the sentence -- see F3. |
| 2. `AT-056` cost-cap amendment -- wording | **NOT RATIFIED AS WRITTEN.** Every measured figure reproduces to the digit (8,029 / 102 / 4,016 / 34.1x / 9-of-90) and the attribution is honest. Two normative claims are unpinned: *"never by a constant (`B-61`)"* (F1) and *"a compressed indent carries the true depth"* (F2). The text says `tests/test_outline_caps.py` pins both. It pins neither. |
| 3. Increment's own code review | **PASS.** Correctness, reuse, dispatch, and the deliberate asymmetry all verified by firing. Two LOW notes, one MEDIUM. No code change is required to unblock; the blocking work is in the arms. |

---

## Scope reviewed

- `git diff fc0aeff~1..ae501ea -- mapper/ tests/` read in full: `mapper/app.py` (+80), `mapper/views/outline.py` (+117), `tests/test_a3_census.py` (+41), `tests/test_agree_floor.py` (new, 135), `tests/test_canvas_header_charge.py` (new, 275), `tests/test_outline_caps.py` (new, 153).
- Read beyond the diff for context: `mapper/app.py:1440-1640` (`_header_rows`, `_header_rows_for`, `_canvas_size`), `:1690-1762` (`_painted_ids_for`), `:1875-1880` (`_current_renderer`), `:2547-2600` (`refresh_canvas`); `mapper/views/layered.py` (`_clip`, `_fit`, `header_rows`, `plain`); `mapper/views/outline.py::_fit_declared`; `mapper/widgets/rail.py:231-236` (the cited cap precedent); `mapper/darkside.py::plain`.
- Both ratification texts read in full in `01-requirements.md` (the `AT-056` block and the `LLR-N06.3.5` block).
- `.dev-flow/state.json` -> `PAN-1` entry.

### What I did NOT review
- **Security** -- gate 2's lane. `_clip` now sits on a file-derived path (`node.ficha.title`); the coercion ORDER is correct here, but I did not assess the bidi/control surface. Flagged to `security-reviewer`.
- The six docs-only commits' prose beyond the two ratified blocks I was asked to rule on.
- `mapper/views/radial.py` -- untouched by this increment and owned by `S-D`.
- Suite/functional coverage breadth -- `qa-reviewer`'s lane.

### What I could not determine
- Whether `S-D` can in fact redden the two residue arms as written. They assert a strict inequality and an identity; both look reddenable, but I did not simulate `S-D`.
- Whether the 90-size sweep behind "9 of 90" used the same fixture pair. I reproduced **9 floor frames per fixture at the identical sizes** over this module's 42-size sweep, which corroborates the shape and the count but is not the same sweep.

---

## Method

All mutants fired byte-level via the Edit tool (never PowerShell -- trap (a) respected). Anchor
match count asserted `== 1` before every edit. `__pycache__` purged before every run. Every mutant
restored unconditionally and **sha256 verified back to baseline**. No ANCHOR MISS occurred: all
four outline anchors and both app.py anchors matched exactly once.

Final tree state -- **byte-identical to `ae501ea`**, `git status --porcelain` empty:

```
33499cfb0707ad44bdbd44766e9d11d6f1be15177ba102d6cca1e03e8cd79bb5  mapper/app.py
6f707d348858be71fc3c71824b3591114769b37a4785d496a6584b6f244938d1  mapper/views/outline.py
ac993a0ab1c6a10125ecbacbf519116481ed6f93488bb16d6072d2b7e81eeea0  mapper/views/layered.py
0da7987e510b192259e8bd6b926c9876b02dca0c72b2fd920e5c783a38a162fd  tests/test_outline_caps.py
ee95673291a64d9b3f7eb455abe59145a2a52826c02245040dbeb9856b14bca6  tests/test_canvas_header_charge.py
c3b457fb0877a70389d98dd01db3ed103aa2abf93ebb6e7c6d5048eb4e529ad4  tests/test_agree_floor.py
```

`ruff check .` -> **27**, unchanged. `FLAKE-1` did not fire in any run.

---

## Findings

### F1 -- Both cost caps are derived in the code and pinned as constants by the arms [Severity: HIGH]

- **What:** `tests/test_outline_caps.py` drives ONE geometry (`W, H = 118, 34`). Replacing both
  derivations with constants tuned to that geometry passes **the entire default lane**.
- **Where:** `tests/test_outline_caps.py:24` (`W, H = 118, 34`), against
  `mapper/views/outline.py:212-213` (`indent_budget = max(2, state.w // 2)`,
  `row_cap = max(state.w, state.w * state.h)`).
- **Fired:** `indent_budget = 59` and `row_cap = 4012` (both equal to their derived values at
  118x34), stacked. Result: **`1051 passed, 19 deselected, 3 xfailed` -- the full lane green.**
- **Why it matters:** this is not a style regression, it is the pathology the cap exists to
  prevent, shipped green. Measured under the mutant on `chain(200)`:

  | w | h | widest row | over canvas |
  |---|---|---|---|
  | 40 | 20 | 96 | **yes** |
  | 24 | 10 | 96 | **yes** |
  | 118 | 34 | 96 | no |

  A 96-cell row into a 24-cell canvas -- a 4x overrun -- with 1051 arms green. The `AT-056`
  amendment's sentence *"never by a constant (`B-61`)"* is exactly the property that is unarmed,
  and this module is where the batch's own control 20 (recorded verbatim in
  `test_canvas_header_charge.py:66-71`: *"a parametrization that samples one failure mode tests one
  failure mode"*) was NOT applied. The header-charge module learned this lesson in this same
  increment; the caps module did not inherit it.
- **Suggested fix:** make the geometry a parameter, not a module constant, so a constant fails at
  the widths it was not tuned to:

  ```python
  GEOMETRIES = ((118, 34), (40, 20), (24, 10))

  def _rows_of(graph: Graph, w: int, h: int):
      rows, _sc = outline._rows(graph, ViewState(selected_id=graph.root_id, w=w, h=h))
      return rows

  @pytest.mark.parametrize("w,h", GEOMETRIES)
  @pytest.mark.parametrize("depth", (200, 1000, 4000))
  def test_the_indent_is_bounded_by_geometry(depth, w, h):
      widest = _widest(_rows_of(chain(depth), w, h))
      assert widest <= w, (...)
  ```

  and the same `w,h` parametrization on `test_a_monster_title_is_clipped_to_one_frame`, asserting
  `widest <= w * h + w`. Both mutants above then redden at `(24, 10)`.

---

### F2 -- The depth-marker truth oracle is satisfied by the fixture's own title [Severity: HIGH]

- **What:** `test_a_compressed_indent_still_tells_the_truth_about_depth` asserts
  `str(depth - 1) in leaf`. The fixture titles are `f"nodo {i}"`, so **the leaf's title already
  contains the level**. The assertion passes whatever the marker says.
- **Where:** `tests/test_outline_caps.py:87-90`, against `mapper/views/outline.py:55`.
- **Fired:** marker mutated to report `level // 10`, i.e. a marker that lies about depth by 10x.
  `tests/test_outline_caps.py` -> **10 passed.** The rendered leaf under the mutant:

  ```
  '<U+21F2>399 - nodo 3999'
       marker says: 399        (the truth is 3999)
       arm oracle "3999" in leaf: True   <- satisfied by the TITLE
       anchored oracle "<U+21F2>3999" in leaf: False
  ```

- **Why it matters:** this arm is the **condition attached to the coordinator's licence**. The
  `AT-056` amendment stakes the whole cap on it -- *"a compressed indent carries the true depth
  beside its marker ... What the operator sees may compress; what it asserts stays true"* -- and
  names this module as the pin. A marker that silently reports a tenth of the real depth is
  precisely "compression became a lie", and it ships green. Separately: the **code is correct** --
  `_indent` does carry the true level, and I verified the real marker reads `3999`. Only the oracle
  is vacuous. This is the batch's own `M-TXT` shape (an arm asserting a property of something the
  fixture supplied).
- **Suggested fix:** anchor on the marker, and remove the level from the fixture titles so the two
  cannot collide again:

  ```python
  # in chain(): ficha=Ficha(title="nodo")        # no level in the title
  assert f"{outline.DEPTH_MARK}{depth - 1}" in leaf, (
      f"depth {depth}: the marker does not carry the true level ({depth - 1}): {leaf[:60]!r}"
  )
  ```

---

### F3 -- The floor exception is armed on its consequence, not on its stated trigger [Severity: HIGH]

- **What:** the amendment's trigger is geometric -- *"when the declaring header cannot fit without
  evicting the last content row"* -- and the text is emphatic that it is **derived, never a list of
  sizes**. The arm instead selects floor frames by `f["canvas"] is not None -> continue`, i.e. by
  **"the canvas declared nothing"**. That is the consequence, and it is strictly broader than the
  trigger: *any* cause of canvas silence is absorbed into the exception and then only the strip is
  checked.
- **Where:** `tests/test_agree_floor.py:87-88`, against `mapper/views/outline.py:368`
  (`if not candidate and kept: return kept` -- the real, and correctly worded, trigger).
- **Fired:** widened the fallback to `if len(candidate) < len(kept) and kept:` -- the canvas now
  falls silent whenever declaring costs a row, far beyond the empty-frame floor.
  `tests/test_agree_floor.py` -> **4 passed.** Non-vacuity of my own mutant, counted over the
  module's own `SIZES`:

  | fixture | floor-classified (clean) | floor-classified (mutant) |
  |---|---|---|
  | `legacy` | 9 | **17** |
  | `anidado` | 9 | **14** |

  The exempted set nearly doubles, silence spreads to 8 and 5 additional frames, and all four arms
  stay green. The control arm (`..._above_the_floor_the_canvas_still_declares`) only requires that
  *at least one* frame still declares, so it cannot see a partial expansion.
- **Why it matters:** the exception WEAKENS a ratified clause, and the text earns that weakening by
  promising the exception can **lapse**. As armed it cannot lapse in the direction that matters:
  the clause proper silently stops governing frames it used to govern. The amendment's sentence
  *"Armed: `tests/test_agree_floor.py` derives the floor sizes and asserts the proviso at each"* is
  therefore false as written -- it derives silences. Note the test's own docstring is **honest**
  about this (`:14-16` says it selects on "something is hidden, and the canvas declared nothing");
  it is the requirement text that overclaims.
- **Suggested fix:** make the classification two-way against the geometric condition, so a widened
  silence reddens. Derive the trigger from the same mechanism the code uses rather than from the
  observable:

  ```python
  # per size, independently of what the canvas painted:
  rows, _sc = outline._rows(screen.graph, screen._view_state(w, h))
  hidden = len(screen.graph.nodes) - len(outline.painted_ids(...))
  header = rows[0][1].copy()
  header.append(f"  {outline.OVERFLOW_TOKEN} {hidden} fuera de vista")
  at_floor = not outline._fit([(rows[0][0], header), *rows[1:]], w, h)

  assert (f["canvas"] is None) == at_floor, (
      f"{map_id} at {size}: canvas silent={f['canvas'] is None} but the geometric "
      f"floor condition is {at_floor}. The exception is firing somewhere it was "
      "not licensed, or not firing where it was"
  )
  ```

  Keep the existing proviso assertions (`strip_on_frame`, `strip == truth`) and the non-vacuity
  guard -- those are good and they work.

---

### F4 -- The cap's licence depends on `PAN-1`, which is declared but not armed [Severity: MEDIUM]

- **What:** the caps are safe *because* outline reads no pan. That dependency is recorded honestly
  in `state.json` -> `PAN-1.outline_half` (*"If outline ever gains pan, that licence lapses and the
  caps must be revisited -- recorded here so the dependency is not invisible"*). But it is prose
  only. No arm reddens if outline gains a `pan_x`/`pan_y` read.
- **Where:** `.dev-flow/state.json` `PAN-1`; `mapper/views/outline.py:37-40`.
- **Verified:** `mapper/views/outline.py` has **0** live pan references (its single textual match is
  the docstring sentence added by this increment -- the `state.json` entry already says exactly
  this, correctly). `radial.py` also has 0; `layered.py` has 6. So the claim is substantively true,
  and the prompt's `PAN-1` challenge does not defeat it: the reasoning is sound for outline on its
  own terms. `rail.py`'s precedent is real (`mapper/widgets/rail.py:235`,
  `indent = "  " * min(depth, RAIL_WIDTH)`) -- and outline's version is strictly MORE honest than
  the precedent, since rail carries no depth marker at all.
- **Why it matters:** this increment set its own standard one seam over -- the radial header charge
  is a declared residue **pinned by two arms** so `S-D` must redden them. The pan dependency is the
  same kind of residue, declared with the same honesty, and left unpinned. `PAN-1` is routed to
  `S-D`'s pre-gate, which is exactly where it could regress.
- **Suggested fix:** one cheap arm, in the census idiom the batch already uses:

  ```python
  def test_outline_reads_no_pan_which_is_what_licenses_the_caps():
      src = (REPO / "mapper" / "views" / "outline.py").read_text(encoding="utf-8")
      code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
      assert "state.pan_x" not in code and "state.pan_y" not in code, (
          "outline now reads pan; the cap's licence (PAN-1.outline_half) has lapsed "
          "and the indent/row caps must be revisited before this arm is deleted"
      )
  ```

---

### F5 -- `_indent` returns `budget + 1` cells, and can exceed `budget` on the clamp branch [Severity: LOW]

- **What:** the capped branch returns `run + 1 + len(str(level)) + 1` cells where
  `run = budget - len(str(level)) - 1`, i.e. **`budget + 1`**. On the `max(0, ...)` clamp branch it
  returns `len(str(level)) + 2` regardless of budget.
- **Where:** `mapper/views/outline.py:54-55`.
- **Why it matters:** bounded in practice (`_canvas_width` floors at 20, so `budget >= 10` and
  `level <= MAX_RENDER_NODES = 12000`, capping the overshoot at a cell or two) -- so this is a
  documentation-accuracy nit, not a defect. But the docstring and the `AT-056` text both assert the
  indent is bounded BY the budget, and in an increment whose entire subject is bounds being exact
  and derived, an off-by-one in the bound is worth stating rather than leaving for a later reader to
  rediscover.
- **Suggested fix:** either `run = max(0, budget - len(str(level)) - 2)`, or say `budget + 1` in the
  docstring. Prefer the docstring -- the extra cell is harmless and the arithmetic is clearer as-is.

---

### F6 -- `_clip` is the only cross-module private import in `mapper/` [Severity: LOW]

- **What:** `from mapper.views.layered import OVERFLOW_TOKEN, _clip`. Checked across `mapper/`: this
  is the sole underscore-prefixed cross-module import. `radial.py` imports `overflow_phrase`
  (public); `app.py` imports public names only.
- **Where:** `mapper/views/outline.py:9`.
- **Assessment:** **the reuse itself is correct and I endorse it.** `_clip` is the right call --
  verified: it applies `darkside.plain` and then truncates, so the coerce-then-truncate ordering of
  `LLR-COERCE.2` is preserved, and a second truncator in this family would be a second thing to keep
  in step. Only the name's privacy is off: a symbol imported by a sibling module is part of that
  module's surface.
- **Suggested fix:** rename to `clip` with the docstring intact, updating the three call sites in
  `layered.py` plus this one -- **or** leave it and note the deliberate exception in `layered.py`.
  Either is fine; do not add a second truncator.

---

## What I verified and found SOUND (fired, not assumed)

These were the claims I was asked to attack. They held.

1. **The per-renderer charge holds at the CALL SITE, not just in the dispatch table.** Reverted
   `_header_rows`'s body to `return header_rows(self.graph, self._canvas_width(), wrap_w)`.
   Result: **1 failed, 36 passed** -- killed by
   `test_the_header_rows_METHOD_routes_through_the_dispatch` and by that arm alone. The author's
   report that 36 other arms are blind to this mutant is **accurate**, and the arm they added to
   close it works. `_header_rows` has exactly one caller (`_canvas_size:1608`), and `layered.header_rows`
   is no longer called directly anywhere in `app.py`.
2. **The strict/degrading asymmetry is load-bearing, not narrative.** Made the method strict
   (`charge = self._header_rows_for(self._current_renderer())`, no `except`). Result:
   `tests/test_repair_cycles.py::test_tc_r08_refresh_canvas_survives_any_renderer_exception`
   **failed on both parameter cases**, exactly as claimed, plus the degrade arm. Confirmed
   structurally: `refresh_canvas:2551` calls `_canvas_size()` **outside** its `try`, so a raise
   there does escape the guard `LLR-R01.4` ratifies.
3. **The depth marker is substance, not decoration.** The real marker prints the true level
   (`U+21F2` + `3999`), which is strictly more information than the `rail.py` precedent it cites.
   Only its oracle is broken (F2).
4. **Every measured figure in both amendments reproduces to the digit.** Reconstructed the pre-fix
   renderer in memory (`_indent = lambda level, budget: "  " * level`, no tree edit):

   | depth | widest row (pre-fix) | amendment says |
   |---|---|---|
   | 4000 | **8,029** | 8,029 |

   Post-fix: **102** cells (deep chain) and **4,016** cells (400,000-char title) -- both as written.
   Floor sweep: **9** floor frames on `legacy` and **9** on `anidado`, at exactly the claimed sizes
   (widths 24-34 at heights 10 and 12, plus `(24,14)`). I found **no** inflated or stale number in
   either ratified block. Attribution is honest throughout, including the unflattering admissions
   (the 28-arm survival, the `TC-R08` failure, the superseded 14/135 and 15/135 figures, and the
   note that the caps do not move the floor set only because both fixtures are shallow).
5. **The floor exception's normative TEXT matches the code's actual mechanism.** `_fit_declared`'s
   `if not candidate and kept` fires exactly when the widened header leaves an empty frame, which is
   what *"cannot fit without evicting the last content row"* says. The proviso is genuinely
   load-bearing (it is the only thing standing between the exception and two silent surfaces), and
   the trigger as WORDED is derived. F3 is about the arm, not the text.

---

## Evidence checklist

- [x] **Diff read in full** -- `fc0aeff~1..ae501ea -- mapper/ tests/`, 6 files, +782/-19; plus both ratified blocks in `01-requirements.md` and the `PAN-1` state entry.
- [x] **Correctness pass (edge / None / error paths)** -- `LookupError` degrade path verified against `TC-R08`; `_canvas_size`'s three branches re-read; `row_cap` at `h == 0` falls back to `state.w`; `_indent` clamp branch analysed (F5).
- [x] **Simplicity pass** -- no premature abstraction found. `_header_line()` extraction is justified (charge and paint off one helper); `_degraded`'s deliberate non-routing through it is correctly reasoned. `_header_rows_for`'s identity dispatch correctly mirrors `_painted_ids_for`.
- [x] **Reuse / duplication checked** -- `_clip` is the right reuse and preserves `LLR-COERCE.2` ordering (F6 is the name only); `rail.py:235` precedent verified real; no second truncator introduced.
- [x] **Tests reviewed for intent** -- and this is where the increment fails: **F1, F2, F3** are three arms that cannot fail when the behaviour they name changes.
- [x] **Verdict explicit** -- BLOCK, with a separate verdict on each of the three duties above.

---

## Boundary

**Soft cap reached at 3 blocking findings -- stopping and surfacing rather than accumulating.**
I did not continue hunting after F3; there may be further unpinned arms in these three modules that
I did not fire at. The increment is **reviewable as cut** -- I am not invoking the terminal
boundary. No HIGH here is self-cleared.

All three HIGHs are **arm-only**: no production line needs to change to clear them. The estimated
work is a parametrization (F1), a one-line oracle anchor plus a fixture title change (F2), and one
two-way assertion (F3). Once those redden against the mutants recorded above, both ratification
duties become ratifiable and this gate flips to PASS.

**Handoffs:** `_clip` now sits on a file-derived path (`node.ficha.title`) -- coercion ORDER is
correct, but the bidi/control surface is **`security-reviewer`'s** call at gate 2. Coverage breadth
across the three lanes is **`qa-reviewer`'s**.
