# Increment 013 — S-B(+C) — Confirmation pass 3

**VERDICT: NOT CONFIRMED**

- **Item 1 — is the declination sound?** **NO.** The two orders differ. `mapper.darkside.fit`
  measures in **display cells**, and `darkside.plain` is length-preserving in *code points* but
  **not in cells** — 221 of the 235 banned points have cell width 0, `U+FFFD` has cell width 1.
  The orders differ on the arm's **own source at all four of its own widths**, and the forbidden
  order **overruns its own budget every time** (up to 11x). Fired: the forbidden-order mutant on
  `darkside.fit` turns the full default lane **RED — 5 failed / 1058 passed**.
- **Item 2 — does the F7 re-point discriminate?** **YES, and it is NOT shadowed.** Fired: the
  remap mutant is killed by `out == darkside.plain(out)` at `test_inc3_census.py:183` — the first
  assertion in the loop — while the retained `count(U+202E) == 0` holds in **12/12** cells and
  survives. The `test_fold.py` shadowing does not apply here.
- **Item 3 — ratify the amended `LLR-COERCE.2` wording?** **NOT RATIFIED.** The invariant itself
  is sound and the derived-set half is intact, but the blockquote states **two measured facts that
  are false** (`the same function`; `left every arm in the suite green`), and its survives-the-
  hypothetical argument names the **wrong conjunct**. A **sixth site** exists — six, in fact — but
  the finding has inverted: they no longer carry the original refuted mechanism, they carry the
  **refutation**, over-generalized from the one truncator where it holds.

## Boundary statement

**Reviewed:** Item 1 (order equivalence over the derived truncator set), Item 2 (the F7 re-point's
mutation power and its shadowing), Item 3 (the amended `LLR-COERCE.2` Statement text, its
derived-set half, and a repo-wide sweep for the ordering narration).

**Not reviewed:** the increment at large; `F1`–`F6`/`F8` from passes 1–2; the security lane; the
routed defects `B-50`/`B-51`/`B-52`; the 27 pre-existing ruff hits; the `-m slow` lane's content;
anything outside the three named items.

**Could not determine:** nothing.

## Method and environment

Probe scripts were written **outside** the repo (`C:\Users\<operator>\clde\scratch-c3\`). Every
anchor count was asserted `== 1` in-process on the absolute path with CRLF-normalised needles
before firing; both target files are pure CRLF (`mapper/darkside.py`: 545 `\r\n`, **zero** bare
LF). No PowerShell file I/O touched a repo file. `__pycache__` was purged before every run. pytest
ran `--color=no`. **No ANCHOR MISS occurred.** **`FLAKE-1` did not fire.**

**Every mutant was proven to alter behaviour before its verdict was trusted**, per pass 2's
`{override} | {comprehension}` lesson. M2 specifically placed the override on a line *after* the
comprehension and printed `_CONTROL_MAP[0x202E]` to prove the override took.

**One writer per tree; tree left byte-identical at `11d0a12`:**

| file | sha256 (before == after) |
|---|---|
| `mapper/darkside.py` | `4568b40d1f4d04470f82deeafad091bec4341093cb731b6dee15792a770fd9f0` |
| `mapper/views/layered.py` | `dfe06f82766d78a4455876c5e2873547ad6d84f53b627ce388113d2a39ba2660` |
| `tests/test_inc3_census.py` | `a3085b0a03abaa9532308065663b6616f6da1455fd812a8a8c83ee578ba92148` |
| `01-requirements.md` | `efc062966be72ff8b8135ef02bab899997f78cd5cda34a779c6f549342792e74` |

`git status --porcelain` empty; restoration re-verified green
(`tests/test_inc3_census.py tests/test_fold.py` → **42 passed, 3 xfailed**).

---

## Findings

### F9 — THE DECLINATION IS WRONG. The two orders are not the same function, and the forbidden order breaks the budget. [Severity: HIGH]

- **What:** Confirmation pass 2 declined to redden the arm on this measurement: *"`_CONTROL_MAP`
  maps all 235 banned code points to exactly one `U+FFFD` each, making `plain` length- and
  index-preserving"* — therefore *"the two orders are the same function."* **The premise is true
  and the inference is invalid.** `plain` is index-preserving in **code points**. It is **not**
  preserving in **display cells**, and `mapper.darkside.fit` truncates by
  `Text.cell_len` / `Text.truncate`, not by index.

  Measured over the full banned set:

  | | count | e.g. |
  |---|---|---|
  | banned points with cell width **0** | **221** / 235 | `U+0000`, `U+200B`, `U+202E`, `U+E0041` |
  | banned points with cell width **1** | 14 / 235 | `U+00AD`, `U+0600` |
  | `U+FFFD` (the replacement) | — | cell width **1** |

  So coercion **inflates** the cell width of 221 of 235 banned points from 0 to 1. Run before the
  measurement (the spec order), the truncator budgets the inflated string. Run after (the forbidden
  order), it budgets the *deflated* one and then inflates it past the budget.

  **Minimal witness — two characters, width 1:**

  ```
  src = U+200B + "A" ,  w = 1
    coerce-then-truncate (spec)      -> U+2026                 1 cell   (in budget)
    truncate-then-coerce (forbidden) -> U+FFFD + "A"           2 cells  (200% of budget)
  ```

  **The arm's own source, at the arm's own four widths** — `darkside.fit` differs at **4/4**:

  | w | A: coerce-then-truncate | B: truncate-then-coerce | B cells vs budget |
  |---|---|---|---|
  | 5 | `aaaa` `U+2026` | `aaaa` `U+FFFD` `U+2026` | **6 > 5** |
  | 6 | `aaaa` `U+FFFD` `U+2026` | `aaaa` `U+FFFD` `b` `U+2026` | **7 > 6** |
  | 10 | `aaaa` `U+FFFD` `bbbb` `U+2026` | `aaaa` `U+FFFD` `bbbbb` `U+2026` | **11 > 10** |
  | 20 | `aaaa` `U+FFFD` `b`×14 `U+2026` | `aaaa` `U+FFFD` `b`×15 `U+2026` | **21 > 20** |

  `layered._clip` and `layered._fit` are **`same` at all four** — `_vis_width` is `len(s)`, so for
  those two the pass-2 measurement is correct. **That is the whole error: the property was measured
  on the one length-based truncator and generalised to a clause that quantifies over all three.**

- **The corpus I searched** (built independently; none of pass 2's five sources reused):
  **4,015 sources × 41 widths (0–40) × 3 derived truncators = 493,845 comparisons.**
  Sources: zero-width runs (`U+200B`) at prefix/interleaved/suffix positions; balanced and
  unbalanced `U+202E`/`U+202C`; `U+E0041` TAG-block payloads; `U+0000` runs; the two **width-1**
  banned families (`U+00AD` soft hyphen, `U+0600` Arabic sign) which behave *differently* from the
  width-0 ones; **wide/CJK** cells (`U+4E2D U+6587`); **astral** points (`U+1F600`);
  **regional-indicator pairs** (`U+1F1E6 U+1F1E7`); **combining marks** (`U+0301`, not banned,
  width 0 — to separate "width 0" from "banned"); a **lone unpaired surrogate** (`U+D800`);
  `\t`/`\n` (the two PRESERVED points); and 4,000 randomised fuzz strings of length 1–14 over an
  alphabet mixing all of the above (seed `20260911`). Widths were swept **contiguously 0..40**, so
  every boundary and both sides of it were hit, not sampled. The probe first asserted
  `raw(plain(s), w) == shipped(s, w)` for all three truncators, so the "raw" bodies are provably
  the shipped bodies minus the internal coercion.

  **DIFFERING OUTPUTS: 133,176.** All in `mapper.darkside.fit`; 0 in the two length-based
  truncators. Over the four-source × 41-width budget sweep, **157 of 164** forbidden-order outputs
  exceeded their own budget, worst overrun **11.0x** (budget 2, emitted 22 cells); the spec order
  overran **never**.

- **FIRED, not inferred.** **M1** — `mapper/darkside.py:538-545`, `fit` rewritten to the forbidden
  order (`s = plain(s)` removed from the top, both returns wrapped in `plain(...)`); anchor count
  `1`; mutant proven live (budget overrun printed at all four widths before any test ran).

  | lane | result |
  |---|---|
  | `tests/test_inc3_census.py tests/test_fold.py` | **5 failed, 37 passed**, 3 xfailed |
  | **full default lane** | **5 failed, 1058 passed**, 19 deselected, 3 xfailed, **exit 1**, 307 s |

  The five: `test_llr_coerce_2_every_truncator_coerces_before_it_truncates[2, 5, 8, 13, 40]`.

  **So pass 2's claim "a mutant running the forbidden order left every arm in the suite green" is
  false.** It is true only of a `_clip` mutant. A `darkside.fit` mutant reddens the lane — and the
  arm that catches it is the commutation arm whose own docstring calls it **weak** and says *"the
  arms below are the ones that discriminate."* Measured, that is **backwards**: the commutation arm
  is the **only** arm in the census that discriminates the ordering, and the arms below it do not.

- **Where:** `mapper/darkside.py:538-545`; `tests/test_inc3_census.py:155-190`;
  `increment-013-sbc-confirmation-2.md` (the declination).
- **Why it matters:** the declination is the sole evidentiary basis for amending a **security**
  requirement traced to `C-4`. It concludes that an ordering clause protects nothing, when for one
  of the three truncators it governs, reversing the order emits **up to 11x the budget** onto a
  painted surface — an overflow of the row the caller sized. The ordering clause is *load-bearing
  for `darkside.fit` right now*, not hypothetically after some future change to `plain`.
- **Suggested fix:** `software-dev` to (a) retract the declination and the "same function" claim,
  scoping the 0-difference measurement to **length-based truncators only**; (b) arm the budget at
  `LLR-COERCE.2` — see `F11`; (c) correct the commutation arm's docstring, which currently
  disclaims the power it actually has:

  ```python
  # in test_llr_coerce_2_every_truncator_coerces_before_it_truncates
  """The stated threshold, quantified over the DERIVED set and 6 widths.

  WEAK on the two LENGTH-based truncators and STRONG on the cell-based one, and
  the distinction is the whole point.  `darkside.plain` is a 1:1 `str.translate`,
  so it distributes over an INDEX slice: `layered._clip` / `layered._fit` satisfy
  this equality whether or not they coerce (measured at `954f8f3`).  It does NOT
  distribute over a CELL slice: 221 of the 235 banned points have cell width 0 and
  `U+FFFD` has cell width 1, so coercion INFLATES width and `darkside.fit` budgets
  a different string in each order.  Fired at `S-B(+C)` confirmation pass 3: with
  `darkside.fit` rewritten to truncate-then-coerce, THIS ARM IS THE ONE THAT GOES
  RED -- 5 failed / 1058 passed on the full lane, at widths 2, 5, 8, 13 and 40.
  It is the only arm in this census that can see the ordering reversed.
  """
  ```

- **Evidence state:** `executed` — M1 fired on the full lane, restored, sha256-verified.

---

### F10 — The amended `LLR-COERCE.2` blockquote states two measured facts that are false, and its survives-the-hypothetical argument names the wrong conjunct. NOT RATIFIED. [Severity: HIGH]

Taking the four ratification questions in order.

**(a) Is the invariant order-independent, and stronger than or equal to what it replaces? — YES, but only because of the conjunct the document treats as an afterthought.**

The **fixed-point half alone is strictly weaker** than the ordering clause it replaces, and
provably so: under **M1**, the forbidden order satisfies `out == darkside.plain(out)` at **every
one of the arm's four widths** (measured `True, True, True, True`), because the forbidden order
*ends* in a coercion and `plain` is idempotent (`U+FFFD` is not itself banned). **Any**
truncate-then-coerce implementation is a fixed point of `plain` by construction. So
`out == plain(out)` is **structurally incapable** of detecting the reversal it replaced.

The **length-bound half is what carries the load**: under M1 the forbidden order overruns at 4/4
widths. So the **conjunction** is genuinely `>=` the ordering clause, and the amended statement is
**sound as written** — the invariant is order-independent *and* at least as strong. That half of
the ratification passes. But the document nowhere says that the length bound is the discriminating
conjunct; it presents `out == plain(out)` as the load-bearing property throughout, and arms only
that one.

**(b) Does it survive the hypothetical it claims to survive? — The invariant does; the stated
reason does not.**

The blockquote argues:

> *"a multi-character replacement would make order matter again, and `out == plain(out)` still
> holds the line, because a string that is not a fixed point of its own coercion fails it whichever
> order produced it."*

**That reasoning is false.** Under a multi-character replacement, `plain`'s output still contains
no banned points, so `plain` stays idempotent, so the forbidden order's output is **still** a fixed
point and **still** passes `out == plain(out)`. What catches a multi-char replacement is again the
**length bound** — an expanding replacement blows the budget hard. The conclusion survives; the
argument given for it does not.

The companion hypothetical fares worse. `mapper/views/layered.py:96-99` and
`mapper/views/outline.py:245-247` both say the ordering *"would have become load-bearing the day
`plain` DELETED rather than replaced"*. Under a deleting `plain`: `plain` is still idempotent, so
the fixed-point half passes; deletion **shortens**, so the length bound passes too; and there is no
override left to strand, because deletion removed it. **Neither conjunct fires, and the old
stranding rationale does not return.** A deleting `plain` makes the forbidden order *under-fill*
the row — cosmetic, not a defect. The one hypothetical that **is** real is the one no site names:
**a replacement whose cell width differs from the source's**, which is not hypothetical at all —
it is `U+FFFD` today.

**(c) Is the attribution honest, and is anything unmeasured? — Two statements of measured fact are
false.** Both are asserted inside the requirement, in bold, as measurement:

| blockquote claim | measured |
|---|---|
| *"coerce-then-truncate and truncate-then-coerce are **the same function** — **0 differing outputs over 5 hostile sources × 60 widths = 300 comparisons**"* | **FALSE as a clause-level claim.** 133,176 differing outputs over 493,845 comparisons; 4/4 on the arm's own source. True only for `layered._clip` / `layered._fit`. |
| *"a mutant running the forbidden order left every arm in the suite green"* | **FALSE.** M1 (forbidden order in `darkside.fit`): **5 failed / 1058 passed**, exit 1. True only of a `_clip` mutant. |

The "235 banned points → exactly one `U+FFFD` each" and "length- and index-preserving" claims are
**true and correctly measured**. The unmeasured step is the unstated inference from *index*-
preserving to *cell*-preserving, which is where the whole amendment turns. The corpus is also thin
for the claim resting on it — **300 comparisons**, and evidently all five sources from one family;
the smallest witness that breaks it is **two characters long**.

**(d) Is the derived-set half intact? — YES.** *"and the set of such functions shall be **derived
from the tracked product sources** rather than named by hand"* survives verbatim, and
`test_llr_coerce_2_the_truncator_set_is_derived_and_non_empty` still pins it as an **equality** of
exactly three members (not a floor). No finding.

- **Where:** `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:589-619` (the amended
  Statement and its blockquote); mirrored at `mapper/views/layered.py:88-99`,
  `mapper/views/outline.py:232-247`.
- **Why it matters:** a requirement traced to security condition `C-4` now carries, as bolded
  measurement, a claim that reversing the coercion order costs nothing. It does not. A future
  reader who trusts the blockquote may reverse it in `darkside.fit` and ship an 11x row overflow
  with the requirement's blessing.
- **Suggested fix:** keep the amended invariant — it is the right invariant — and repair the
  evidence around it. Replace the refutation blockquote's two false sentences with the scoped
  version, and re-point the hypothetical at the real one:

  > **The mechanism it rested on is refuted FOR THE LENGTH-BASED TRUNCATORS, AND ONLY THOSE.**
  > `_CONTROL_MAP` maps all **235** banned code points to exactly one `U+FFFD` each, so
  > `darkside.plain` is **code-point-index-preserving**, and for a truncator that slices by index
  > (`layered._clip`, `layered._fit`, whose `_vis_width` is `len`) the two orders are the same
  > function — 0 differing outputs, and a `_clip` mutant running the forbidden order left the lane
  > green. **It is NOT cell-preserving, and that is where the ordering is still load-bearing.**
  > 221 of the 235 banned points have cell width **0** and `U+FFFD` has cell width **1**, so
  > coercion INFLATES display width. `darkside.fit` budgets in cells, so reversing the order
  > budgets the deflated string and then inflates it past the budget: measured at confirmation
  > pass 3, **133,176 differing outputs over 493,845 comparisons**, the arm's own source differing
  > at **4/4** widths, **157 of 164** forbidden-order outputs over budget, worst **11.0x**, and a
  > `darkside.fit` mutant running the forbidden order turning the full lane **RED, 5 failed /
  > 1058 passed**. The minimal witness is two characters: `U+200B` + `"A"` at width 1 emits one
  > cell in the spec order and **two** in the forbidden one.
  >
  > **The invariant above is therefore a REPLACEMENT, not a relaxation.** Of its two conjuncts it
  > is **the length bound** that excludes the forbidden order — `out == plain(out)` cannot, because
  > truncate-then-coerce ends in a coercion and every coerced string is a fixed point of an
  > idempotent `plain`. The fixed-point conjunct earns its place elsewhere: it kills a banned-point-
  > to-banned-point remap that `count(U+202E) == 0` survives. **Both conjuncts must be armed.**

- **Evidence state:** `failed` — ratification refused; the amendment's direction stands, its
  evidence does not.

---

### F11 — The discriminating conjunct is unarmed at `LLR-COERCE.2`, and six sites narrate the over-generalised refutation. [Severity: MEDIUM]

**The sixth site exists — and the family has inverted.** Pass 1 found four sites still carrying the
*original* refuted mechanism (truncation strands an override); pass 2 found a fifth. Those are
correctly struck. What stands now is the **refutation itself**, stated unqualified, in six live
sites plus the requirement — and per `F9` it is false outside the length-based truncators:

| # | site | text | verdict |
|---|---|---|---|
| 1 | `mapper/views/layered.py:92-94` | *"`truncate(plain(s)) == plain(truncate(s))` IDENTICALLY … a mutant running the FORBIDDEN order stayed green on all 1058 arms"* | scoped to `_clip` locally, but the **suite claim is global and false** |
| 2 | `mapper/views/outline.py:237-240` | same sentence, verbatim | same |
| 3 | `tests/test_fold.py:388-392` | same, plus *"this arm among them"* | same |
| 4 | `tests/test_outline_caps.py:173-175` | *"a mutant running the forbidden order stays green"* | unqualified |
| 5 | `tests/test_outline_caps.py:286-288` | *"`plain` … is length- and index-preserving and **the coerce/truncate order cannot matter**"* | stated as a **general property of `plain`** — **false** |
| 6 | `tests/test_inc3_census.py:117-121` | *"⚠ THIS PREDICATE IS WEAK … The arms below are the ones that discriminate"* | **backwards** — this is the only arm that discriminates the ordering (`F9`) |

`tests/test_inc3_census.py:159-160` is **honest** and needs no change: it says *"with `_clip`
rewritten to run the FORBIDDEN order — this arm stayed GREEN"*, which is exactly true and exactly
scoped. It is the model the other six should follow. Note the irony worth recording in the
postmortem: **site 1 is `_clip`'s own docstring, i.e. the retraction text has itself become the
thing needing retraction** — the second turn of the cycle this batch keeps cataloguing.

**And the budget is unarmed.** Repo-wide sweep for a cell/length bound asserted on truncator
output: `tests/test_crumb.py:314` and `tests/test_rail.py:204` assert `cells <= width`, but on the
crumb and rail surfaces — **neither runs over the derived truncator set**. **No arm under
`LLR-COERCE.2` asserts the length bound at all.** The requirement was just amended to a two-part
invariant and only part one is armed — and per `F10(a)` it is the *unarmed* part that carries the
order.

- **Suggested fix:** add the second conjunct to the split-at-width arm, in the unit each truncator
  budgets in. This arm goes **RED under M1** as written:

  ```python
  from rich.cells import cell_len
  # ... inside the existing (name, width) loop, beside the fixed-point assertion:
  measured = cell_len if name == "mapper.darkside.fit" else len
  assert measured(out) <= width, (
      name, width, measured(out),
      "the output exceeds the budget it was given -- THE CONJUNCT THAT CARRIES "
      "THE ORDER. `out == plain(out)` cannot see a reversed order, because "
      "truncate-then-coerce ends in a coercion and every coerced string is a "
      "fixed point of an idempotent `plain`. This one can: 221 of 235 banned "
      "points have cell width 0 and U+FFFD has width 1, so coercing AFTER a "
      "cell-budgeted cut inflates the result past the budget -- measured at "
      "confirmation pass 3, 11.0x at the worst.",
  )
  ```

  (`darkside.fit` pads to exactly `width`, so `<=` is an equality there in the non-truncating case;
  `layered._fit` pads on `_vis_width`, `_clip` does not pad. `<=` holds for all three on the
  current code — verified — and fails for `darkside.fit` at 4/4 widths under M1.)

- **Evidence state:** `executed` for the sweep and the unarmed-budget finding; `planned` for the
  suggested arm — **I did not write it.** Whoever applies it is its author and owes it an
  independent reviewer.

---

## Item 2 — the F7 re-point, confirmed in detail

**M2** — `mapper/darkside.py:521`, `_CONTROL_MAP[0x202E] = chr(0x200B)` appended **after** the
comprehension (pass 2's `{override} | {comprehension}` trap avoided by construction, not by hope);
anchor count `1`. **Mutant proven live before any test ran:** printed
`map[0x202E] -> U+200B` (not `U+FFFD`), and `darkside.fit(src, 5)` returning
`aaaa U+200B U+2026` with `fixedpoint=False, count202E==0=True`.

| assertion | holds under M2 | verdict |
|---|---|---|
| retained `count(U+202E) == 0` **and** `count(U+202C) == 0` | **12/12** (truncator, width) cells | **SURVIVES** |
| re-pointed `out == darkside.plain(out)` | 2/12 | **KILLS** |

Fired: `tests/test_inc3_census.py::test_llr_coerce_2_the_split_at_width_arm` → **1 failed**, at
**`tests/test_inc3_census.py:183`**, on `('mapper.darkside.fit', 5, ...)`, with
`assert 'aaaa\u200b…' == 'aaaa\ufffd…'`.

**Shadowing: NO.** Line 183 is the **first** assertion inside the `(name, width)` loop; the count
assertions sit below it and are never reached. The two preceding assertions (`assert derived` and
the balanced-source precondition) read the **raw** source, not its coercion, and are unaffected by
M2 — both pass. This is the opposite arrangement from the `test_fold.py` sibling pass 2 flagged,
where the new assertion sat below a broader one. **The power is real and it is observable at the
pytest level.**

One honest qualification: M2 is not killed *solely* by this arm — the targeted lane showed
**13 failed**, including the two census arms above it and four coercion arms in `test_fold.py`.
The re-point's power is genuine and unshadowed within its own arm; it is not the last line of
defence against this particular mutant.

---

## Evidence checklist

- [x] **Diff read in full** — `11d0a12` (`01-requirements.md:589-619`), `21809fd`
  (`tests/test_inc3_census.py:148-190`, `tests/test_outline_caps.py`), plus the standing
  `mapper/darkside.py:495-545` and `mapper/views/layered.py:73-116`. `executed`
- [x] **Correctness pass** — cell-vs-index width audit over all 235 banned points; 493,845-comparison
  order sweep; budget-overrun sweep. `executed`
- [x] **Simplicity pass** — `n/a — no production code changed in scope; the three items are an
  evidentiary and documentary review.`
- [x] **Reuse / duplication** — the refutation narration is duplicated verbatim across 6 sites
  (`F11`); flagged, not factored (a shared docstring constant would be worse here). `executed`
- [x] **Tests reviewed for intent** — `F9` (commutation arm disclaims the power it has),
  `F11` (budget conjunct unarmed), Item 2 (re-point verified by firing). `executed`
- [x] **Verdict explicit** — **NOT CONFIRMED**; `F9` and `F10` are HIGH and **open**. No fix was
  written by me, so no HIGH carries applied-and-verified evidence. `executed`

## Verdict

- [ ] OK to advance
- [ ] BLOCK-UNTIL
- [x] **Block — HIGH findings open (`F9`, `F10`).**

`BLOCK-UNTIL` would understate this. `F9` is not a fix awaiting application; it is a **reversal of
the finding this pass was convened to confirm**. The declination is unsound, and `LLR-COERCE.2`'s
amended evidence rests on it. The amendment's **direction** survives — the order-independent
invariant is the right requirement and I would ratify it on a corrected record — but its
**text** asserts measured facts that are false, and I do not ratify that.

Nothing here advances the increment. The corrective pass is `software-dev`'s; **I am not its
reviewer for the parts I drafted snippets for** — those snippets are recommendations, and
whoever applies them owes them an independent pair of eyes.

**Handoffs.** `security-reviewer`: the 11x budget overrun under a reversed order in `darkside.fit`
is a painted-surface overflow on a `C-4`-traced path — your lane, not mine, and the security
review is the artifact that first published the "same function" claim. `qa-reviewer`: no arm under
`LLR-COERCE.2` measures the emitted budget (`F11`); that is a coverage gap, not a correctness bug.

**Lanes this pass.** Baseline restored and re-verified: `tests/test_inc3_census.py
tests/test_fold.py` → 42 passed, 3 xfailed. Mutant lanes: M1 full default **5 failed / 1058
passed** (exit 1, 307 s); M2 targeted **13 failed / 29 passed**. ruff not re-run — no repo file
was left changed (`not-run`, `n/a — tree byte-identical to 11d0a12`).
