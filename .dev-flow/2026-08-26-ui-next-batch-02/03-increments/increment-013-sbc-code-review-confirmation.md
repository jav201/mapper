# Increment 013 · S-B(+C) — Code Review CONFIRMATION PASS

**VERDICT: NOT CONFIRMED.**

Three of the four findings are closed by firing. **F1 is half-closed**: the fix pinned the
*indent* derivation and left the *row-cap* derivation unpinned. A constant equal to its
118×34 value survives the **entire default lane at 1059 passed** while building a
**4,016-cell row into a 240-cell canvas** — the exact pathology F1 named, at a geometry
these arms now drive but never drive this fixture through.

| Finding | Claim | Confirmed? |
|---|---|---|
| **F1** [HIGH] | both caps' derivation pinned | **NO — half.** indent pinned (6 arms red); `row_cap` mutant survives 1059/1059 |
| **F2** [HIGH] | depth marker pinned adjacent to glyph | **YES.** 10× lying marker KILLED, 3 arms, isolated |
| **F3** [HIGH] | floor armed on trigger, not consequence | **YES.** widened-fallback KILLED on both fixtures; 9→17 / 9→14 reproduced |
| **F4** [MED] | pan premise armed by AST | **YES.** never-executed pan read KILLED it |
| **Ratification texts** | say what is true | **PARTLY.** `AT-056`/`LLR-N06.3.5` blocks are accurate; the **retraction is incomplete** — the refuted mechanism still stands in four other places, one of them a live arm |

---

## Boundary statement

**Reviewed.** `mapper/views/outline.py` in full (463 lines); `tests/test_outline_caps.py`
(282); `tests/test_agree_floor.py` (156); the `a6598b2..f3c1795` diff of all four; the
`LLR-N06.3.5` and `AT-056` blocks of `01-requirements.md`; `layered._clip`;
`tests/test_fold.py:375-392`.

**Not reviewed.** Security (gate 2's lane — findings routed, not re-litigated); the three
routed defects B-50 / B-51 / B-52; the 27 pre-existing ruff hits; any increment before 013.

**Could not determine.** Nothing material. One bookkeeping discrepancy I could not
reconcile to the author's numbers is recorded under F5 — I report my measurement and the
author's side by side rather than guessing which run produced "3 arms".

**One writer.** Every mutant was applied with the Edit tool, restored unconditionally, and
sha256-verified back to baseline. Final state: `git status` empty, HEAD `f3c1795`,
`outline.py` = `EAC1EB1A…7484E`, `test_outline_caps.py` = `F4BB063C…57B6`,
`test_agree_floor.py` = `3DC6F501…1AA3` — all identical to the pre-pass values. Probe
scripts were written **outside** the repo (`C:\Users\<operator>\clde\`).

**Baseline reproduced**: 1059 / 19 / 1078, both lanes exit 0; ruff 27, and **none of the 27
falls in the three files this fold touched** — the "pre-existing" attribution holds.
`FLAKE-1` did not fire in any of the three full-lane runs.

**Instrument traps, both caught in this pass.** (a) `[IO.File]::ReadAllText` does not follow
PowerShell's `cd`, so my first anchor-count call reported `COUNT=0` for all four anchors —
four false zeros next to a thrown exception. Re-run with absolute paths: all four
`COUNT=1`. (b) pytest colours its short summary; every failure parse in this pass strips
`\x1b[...m` before matching `^FAILED`.

---

## Findings

### F1 — the row-cap derivation is still unpinned  [Severity: HIGH — carried forward, not closed]

- **What:** F1 named **both** caps. The strengthened arm pins only one. Substituting
  `row_cap = 4012` (its value at 118×34) while leaving `indent_budget` derived leaves the
  **entire default lane green at 1059 passed**.
- **Where:** `mapper/views/outline.py:212`; the unpinning arm is
  `tests/test_outline_caps.py:137-149`, which drives `W, H` only.
- **Fired:**

  | mutant | cap arms | full default lane |
  |---|---|---|
  | both caps → constants | **6 failed**, 12 passed | (killed) |
  | `indent_budget` derived, `row_cap = 4012` | **18 passed** | **1059 passed, exit 0** |

  Measured under the surviving mutant, `wide(400_000)` through `_rows`:

  | geometry | widest row (mutant) | widest row (baseline) | frame |
  |---|---|---|---|
  | (118, 34) | 4016 | 4016 | 4012 |
  | (40, 20) | **4016** | 804 | 800 |
  | (24, 10) | **4016** | 244 | 240 |

  A **16.7× overrun** at (24,10), lane green.
- **Why it matters:** this is the same shape F1 raised and the same control 20 the fold
  quotes — "a parametrization that samples one failure mode tests one failure mode". The
  fold added three geometries to the *indent* arm and left the *row-cap* arm at one. The
  ratification bullet says the pin is "asserting the **indent run** against `w // 2`", which
  is accurate about what it does and is **not** a pin of "derived, never a constant" for the
  second cap, which the same bullet's heading claims.
- **The production code is correct** — `row_cap` tracks the frame (baseline column above).
  The defect is entirely in the arms.
- **Suggested fix** — parametrize the existing arm; no new fixture needed:

  ```python
  @pytest.mark.parametrize("geom", GEOMETRIES)
  @pytest.mark.parametrize("n", (10_000, 400_000))
  def test_a_monster_title_is_clipped_to_one_frame(n, geom):
      w, h = geom
      widest = _widest(_rows_of(wide(n), w, h))
      assert widest <= w * h + w, (
          f"a {n}-character title produced a {widest}-cell row at {geom}; the "
          f"frame is {w}x{h} = {w * h} cells"
      )
  ```

  Verified against the table above: baseline passes at all three (4016≤4130, 804≤840,
  244≤264); the `row_cap = 4012` mutant fails at (40,20) and (24,10).
- **Second-order note [LOW]:** in the *indent* arm the companion assertion
  `_widest(rows) <= w * h + w` (line 103) is near-unfalsifiable on a chain fixture — at
  (24,10) it permits 264 cells against rows of ~18. It is not wrong, but it is not the
  row-cap pin either, which is part of why the gap read as covered.

### F2 — closed  [Confirmed]

- **Fired:** `_indent` → `f"{DEPTH_MARK}{level // 10} "` (anchor count asserted `== 1`).
  **KILLED, 3 failed / 15 passed**, all three
  `test_a_compressed_indent_still_tells_the_truth_about_depth[200|1000|4000]`, each reporting
  the true level it failed to find. Nothing else moved — the mutant leaves `run` unchanged,
  so the isolation is clean.
- **Both halves of the fix verified.** The oracle reads `f"{DEPTH_MARK}{depth-1}"` —
  adjacent to the glyph (line 127) — and `chain(depth, titled=False)` gives every node the
  title `nodo` (line 47), which cannot contain the level. The old escape route is gone
  rather than papered over.

### F3 — closed  [Confirmed]

- **Fired:** `_fit_declared`'s `if not candidate and kept:` → `if len(candidate) < len(kept)
  and kept:` (widens the fallback far beyond the empty-frame floor). **KILLED:**
  `test_at057_above_the_floor_the_canvas_still_declares` red on **both** fixtures, at (24,16).
  The companion arm is doing exactly the work the fold assigned it.
- **Exempted-set counts independently reproduced** over the same 42-size sweep:

  | | frames hiding nodes | canvas silent | `at_floor` | disagreements |
  |---|---|---|---|---|
  | legacy, baseline | 32 | 9 | 9 | 0 |
  | legacy, mutant | 32 | **17** | 9 | 8 |
  | anidado, baseline | 31 | 9 | 9 | 0 |
  | anidado, mutant | 31 | **14** | 9 | 5 |

  The 9→17 and 9→14 figures are confirmed at the byte level, and the disagreeing sizes
  (24/28/31/34 × 16/20) are precisely the frames the companion now reddens on.
- **Did the extraction change behaviour?** **No.** The `_widen` body is a token-for-token
  lift of the four inline lines (the diff is a pure substitution; the only textual change is
  that the old `append` call was split across two lines). Empirically: the full lane is green
  at 1059, and the census above holds at **9 of 90 on each fixture**, matching the figure
  `01-requirements.md` re-measured. Both `_widen` call sites are guarded against empty `rows`
  (`floor_reached:356`, `_fit_declared:387`) before indexing `rows[0]`.
- **Is `floor_reached` being public a problem?** **No.** The module already exposes
  `painted_ids`, `header_rows`, `MAX_RENDER_NODES` and `DEPTH_MARK`; a pure
  `(rows, w, h) -> bool` fits that surface, and single-sourcing beats a transcribed second
  spelling in the test.
- **[LOW] the "single-sourced" claim is slightly stronger than the code.**
  `floor_reached` shares `_fit`/`_declared`/`_widen` with `_fit_declared` but **re-spells the
  predicate**, and it evaluates only the loop's **first** iteration, whereas `_fit_declared`
  applies `not candidate and kept` across three iterations with a re-derived `hidden`. I
  probed for divergence over **17,871 frames** (21 synthetic graphs × 38 widths × 23 heights),
  **109 of which actually fell back**: **0 divergences**. So the concern is real in principle
  and unobservable in practice. Worth one sentence softening "single-sourced" to "shares the
  helpers and agrees over the swept domain", not worth a code change.

### F4 — closed  [Confirmed]

- **Fired:** a `_never_called(state) -> int: return state.pan_x` inserted at module level —
  a read that **never executes**. **KILLED:**
  `test_the_caps_licence_holds_outline_still_reads_no_pan` red, reporting `['pan_x']`; nothing
  else moved (1 failed / 17 passed).
- **The "AST, not text" justification is non-vacuous, measured:** at baseline the module
  contains **2** textual `pan_x|pan_y` occurrences (docstring prose at lines 37-39) and **0**
  AST attribute reads. A grep arm would answer "present" on a clean file. The control is
  earning its keep, and a never-executed mutant is the case no runtime arm could reach.

### F5 — the retraction is accurate but **incomplete**  [Severity: MEDIUM — new]

The retraction itself is **correct where it was applied**. `outline.py:232-247` and the
`AT-056` blockquote both quote the false sentence, name the refuting measurement, and keep
the code unchanged — retracted rather than quietly dropped, which is the right shape.

But the brief asked whether *any other text still leans on the refuted mechanism*. **Four
places do**, and the fold touched none of them:

1. **`mapper/views/layered.py:81-85` — `_clip`'s own docstring, the canonical statement.**
   Still reads: *"Truncation MANUFACTURES the defect out of a source that was balanced … cut
   at `width` between the two leaves an unterminated right-to-left override in the painted
   row, and no amount of coercing afterwards puts the terminator back."* This is the
   originating text; `outline.py` only inherited it. Retracting the copy and leaving the
   original is how the claim comes back.
2. **`tests/test_fold.py:385-392` — and this one is an ARM, not prose.** The comment asserts
   *"Truncation MANUFACTURES the defect …, so the ordering clause is not vacuous"*, and the
   arm is `assert cut.count(chr(0x202E)) == 0`. Under the measured length-preserving
   `plain`, that assertion is satisfied **because the coercion replaced `U+202E` with
   `U+FFFD`**, not because of any ordering — it cannot distinguish the two orders. Gate 2's
   own evidence proves it: the mutant running the forbidden order *stayed green on all 1058
   arms*, and this arm was among them. **A test whose stated intent it cannot verify.**
3. **`01-requirements.md:594-595`** and **4. `:1996`** — the "split-at-width arm … leaves 0
   unterminated overrides" threshold, in both `LLR-COERCE.2` and `LLR-N06.2.3`.
   Notably, line 592-593 of the *same* bullet already states the **correct** property —
   *"the coerce-then-truncate and truncate-then-coerce images are **equal** over the hostile
   input set"* — which is exactly what gate 2 measured. The requirement contains the
   refutation and the refuted rationale in adjacent sentences.

- **Suggested fix:** carry the same retraction to `layered._clip`'s docstring; and either
  re-point `test_fold.py`'s split-at-width arm at the property that *is* load-bearing —
  `_clip(s, n) == plain(_clip(s, n))`, i.e. the output is coerced — or mark the arm as
  pinning "coerced at all" and delete the ordering claim from its comment. Items 3 and 4 are
  doc-only.
- **Out of my lane, flagged not judged:** whether `LLR-COERCE.2`'s ordering clause should
  survive at all now that its mechanism is refuted is a requirements question for
  `security-reviewer` / the coordinator, not a code-review call.

### F6 — gate 2's "zero signal" premise does not reproduce  [Severity: MEDIUM — new]

The brief asked whether the new coercion arm carries signal the cap arms don't. **It does** —
but the *reason given for adding it* is wrong, and that matters because the same reasoning
declared a coverage gap that did not exist.

- **Measured** (`title = node.ficha.title`, i.e. coercion **and** cap removed, full lane):
  **5 arms red**, not 3 —
  `test_inc3_census.py::test_a89_every_reached_renderer_coerces_what_it_paints`,
  `test_a_monster_title_is_clipped_to_one_frame[10000]` and `[400000]`,
  `test_the_clip_uses_the_existing_ellipsis_idiom`, and the new arm.
- **Isolating the coercion** (cap kept, coercion removed):
  **2 arms red — the new arm AND the A-89 census arm**; **every cap arm stayed green**.
- `tests/test_inc3_census.py` is **unchanged across both folds** (`git diff a6598b2 f3c1795`
  empty; last touched at `540123c`), so the A-89 census arm already pinned outline's
  coercion **before** gate 2 declared it unpinned.
- **Therefore:** the claim now standing in `test_outline_caps.py:243-247` and echoed in the
  commit — *"removing the COERCION and removing the CAP fail the identical three tests, all
  of them cap tests, so the coercion contributed **zero signal**"* — is **false as measured
  here**. The coercion had signal, from a census arm written two increments earlier.
- **Why it matters:** the new arm is good (sharper, names code points per C-56, non-vacuity
  guard at line 279) and I am **not** recommending its removal — a call-site-specific arm
  beside a census arm is defensible defence in depth. What must not stand is the docstring
  telling the next reader that this call site was unarmed when it was not. That is the
  batch's own recurring shape: a true outcome resting on a false measurement.
- **Suggested fix:** amend the arm's docstring to *"`_clip`'s coercion at this call site was
  already covered by `test_inc3_census.py`'s A-89 census; this arm pins it at the call site
  specifically, names the code points, and fails with a legible message"*, and drop the "zero
  signal" sentence. Same correction in the `AT-056` region if it repeats there.

---

## The two ratification texts

- **`LLR-N06.3.5` "Armed:" block — TRUE.** It claims the arm selects by
  `outline.floor_reached(rows, w, h)`, "the renderer's own predicate", with a non-vacuity
  guard and a companion covering non-floor frames. All four verified: selection at
  `test_agree_floor.py:99` and `:139`, guards at `:117` and `:152`, and the mutant it says is
  now KILLED **is** killed. The quoted 9→17 / 9→14 figures reproduce exactly. The only
  overstatement is "single-sourced … rather than transcribed" (see F3 [LOW]).
- **`AT-056` "what the arms actually pin" block — TRUE BUT INCOMPLETE.** Both sub-bullets are
  accurate about what they assert, and the retraction blockquote is correctly reasoned. The
  gap is the heading: the bullet is offered as pinning *"derived, never a constant"* for the
  caps, and it pins that for the indent run only (F1). The pan sub-bullet is accurate and
  armed.

---

## Evidence checklist

- [✓] **Diff read in full** — `a6598b2..f3c1795` over `outline.py` (+74/−9), `test_outline_caps.py`, `test_agree_floor.py`, `01-requirements.md`; plus `outline.py:1-463` entire.
- [✓] **Correctness pass** — empty-`rows` guards on both `_widen` call sites (`:356`, `:387`); `_widen` extraction behaviour-identical (diff + census 9/90 unchanged); `floor_reached` vs fallback: 0 divergences / 17,871 frames.
- [✓] **Simplicity pass** — `floor_reached` public is proportionate and matches the module's existing surface; `_widen` extraction removes a real duplication. No premature abstraction found.
- [✓] **Reuse / duplication checked** — found one: the new coercion arm duplicates coverage already held by `test_inc3_census.py`'s A-89 census arm (F6). `_clip` correctly reused rather than re-truncated.
- [✓] **Tests reviewed for intent** — F1 (arm cannot fail when `row_cap` stops deriving), F5 item 2 (`test_fold.py` arm cannot verify its stated ordering intent), F6 (arm's stated justification false).
- [✓] **Verdict explicit** — below.
- [✓] **Nine mutants fired, all restored, all sha256-verified**; 4 anchors asserted `== 1` before firing; `__pycache__` purged before every run; **no ANCHOR MISS occurred in this pass** (one false-zero *count* did, from a .NET CWD trap — recorded in the boundary statement).

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — F1 is not closed.** `row_cap`'s derivation survives constant substitution across the whole default lane; one parametrize decorator on an existing arm closes it, and the fix is verified above against measured numbers. F2, F3 and F4 are **confirmed closed by firing** and need nothing further. F5 and F6 are MEDIUM and doc-level — they should ride with the F1 fix rather than gate on their own, but the `test_fold.py` arm in F5 item 2 deserves a real re-point, not a comment edit.
