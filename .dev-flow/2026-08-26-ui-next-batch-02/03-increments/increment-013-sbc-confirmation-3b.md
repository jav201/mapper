# Increment 013 — S-B(+C) — Confirmation pass 3b (re-ratification on the corrected record)

**VERDICT: RATIFIED**

- **The amended text** — **RATIFIED.** The Statement restores the ordering clause as normative, the
  invariant is genuinely *added* rather than substituted, the budget is correctly named as the
  load-bearing conjunct, and the fixed-point half is correctly described as structurally incapable.
  The three-step history is accurate and cites what it should. Both of my measurements are carried
  at the right numbers. One stale sentence inside it (`F16`, LOW).
- **The budget arm's discrimination** — **CONFIRMED BY FIRING.** Forbidden-order mutant on
  `darkside.fit`, proven live (2 cells into a budget of 1): **8 failed** in
  `tests/test_darkside_budget.py`, **13 failed / 1067 passed** on the full default lane. Your counts
  reproduce exactly.
- **The metric derivation** — **SOUND AND NON-VACUOUS**, and stronger than you claimed. Fired the
  guard (`M3`): degrading `_metric_of` collapses all three to `codepoints` and the guard reddens all
  8 parametrizations with its own message. Separately: the probe uses a **benign** wide source, so a
  coercion-ordering mutant **cannot** reclassify its way out — verified, `darkside.fit` still reports
  `cells` under `M1`. That is a real property worth stating in the docstring; it currently isn't.
- **The seventh-site sweep** — **A SEVENTH SITE EXISTS** (`F14`, MEDIUM). All six you corrected are
  correctly scoped. But the *substitution* framing — the thing the re-ruling reversed — survives in
  **two live assertion messages and one comment**, telling a reader on a red arm that the fixed point
  is "the property the ordering clause was reaching for."
- **The `B-53` routing** — **THE JUDGMENT HOLDS; THE ID DOES NOT.** Asserting cells against `_clip`
  would be the wrong oracle and you were right to refuse it. But **`B-53` is already taken** (`F13`,
  MEDIUM) — it is `#map-canvas is can_focus=False` in the `A-95` carries table, referenced by that
  meaning in four increment artifacts.

Nothing here blocks the re-ratification. `F13`/`F14` are bookkeeping and narration defects in the
corrective commit, not defects in the requirement.

## Boundary statement

**Reviewed:** the amended `LLR-COERCE.2` Statement, acceptance-level invariant and three-step
history; `tests/test_darkside_budget.py` in full; the six corrected narration sites; a repo-wide
sweep for a seventh; the `B-53` routing on its merits and its id.

**Not reviewed:** the increment at large; `F1`–`F8` from passes 1–2; the security lane; `B-50`/
`B-51`/`B-52`; the `-m slow` lane's content; the 27 ruff hits beyond confirming the count.

**Could not determine:** nothing.

## Method and environment

Probes outside the repo (`C:\Users\<operator>\clde\scratch-c3\`). Every anchor asserted `== 1`
in-process on the absolute path with CRLF-normalised needles; `mapper/darkside.py` 545 `\r\n` /
**0** bare LF, `tests/test_darkside_budget.py` 170 `\r\n` / **0** bare LF. **Edit tool only** on repo
files; no PowerShell file I/O. `__pycache__` purged before every run. pytest `--color=no`.
**No ANCHOR MISS. `FLAKE-1` did not fire** in either full-lane run.

**Both mutants proven to alter behaviour before their verdicts were trusted** — `M1` by printing the
overrun (2 cells into budget 1), `M3` by printing the collapsed classification map.

**Tree left byte-identical at `ce294f1`:**

| file | sha256 (before == after) |
|---|---|
| `mapper/darkside.py` | `4568b40d…70fd9f0` |
| `tests/test_darkside_budget.py` | `1cd91d2f…f5d9c470` |
| `tests/test_fold.py` | `76d95a39…db5929647f` |
| `tests/test_inc3_census.py` | `96c05c4c…346cfa184d0` |
| `mapper/views/layered.py` | `7b5e0be2…7748051a14ea` |

`git status --porcelain` empty. **Baseline re-verified after restoration: 1080 passed, 19
deselected, 3 xfailed, exit 0, 305 s. ruff: 27 — unchanged.**

---

## What I verified, item by item

### 1. The amended text — RATIFIED

| ratification question | verdict |
|---|---|
| ordering clause restored as normative | **YES** — Statement reads "shall apply … **before** truncating", unhedged |
| invariant *added*, not substituted | **YES** — it sits under its own `Acceptance-level invariant` heading, explicitly "ADDED, NOT SUBSTITUTED" |
| budget named as load-bearing | **YES**, and in bold, with the structural reason (idempotent `plain` ⇒ fixed point by construction) |
| the "if `plain` deletes" error corrected | **YES** — struck, and the real hypothetical (a replacement whose cell width differs from the source's, i.e. `U+FFFD` today) named in its place |
| derived-set half intact | **YES** — verbatim, and `test_llr_coerce_2_the_truncator_set_is_derived_and_non_empty` still pins the equality of three |
| my numbers carried correctly | **YES** — 133,176 / 493,845; 221-of-235 and `U+FFFD` at width 1; 11×; 5 failed / 1058 passed; the two-character witness. All match my record |
| attribution honest | **YES**, and unusually so — it names the instrument error as "a hand-built model of `_clip` generalised over three truncators", records the coordinator's own rule against itself, and credits the refusal-to-self-clear. I have no correction to make to the accountability section |

**No claim in the amended text is over-generalised or unmeasured.** The one defect is stale, not
false — see `F16`.

### 2. The budget arm discriminates — CONFIRMED

**M1** — `mapper/darkside.py:538-545`, `fit` rewritten to truncate-then-coerce; anchor count `1`;
proven live (`darkside.fit(U+200B + "A", 1)` → **2 cells, budget 1**).

| lane | result |
|---|---|
| `tests/test_darkside_budget.py` | **8 failed, 9 passed** |
| **full default lane** | **13 failed, 1067 passed**, 19 deselected, 3 xfailed, **exit 1**, 306 s |

The 13: 8 from the budget module (the minimal-witness arm + `stays_within_its_budget[2,3,5,8,13,20,40]`),
5 from `test_inc3_census.py::…_coerces_before_it_truncates[2,5,8,13,40]`. **Your counts reproduce
exactly.** The requirement's discriminating conjunct is now armed and it kills.

One observation, not a finding: `stays_within_its_budget[1]` **survives** M1 — at width 1 the
forbidden order happens to land inside budget for all five of that arm's sources. Width 1 is covered
only by the named minimal-witness arm, which does kill. The coverage is real; it just rests on one
arm at that width rather than two. Worth knowing if anyone ever trims the named case.

### 3. The metric derivation — SOUND, NON-VACUOUS, and stronger than claimed

**M3** — `tests/test_darkside_budget.py:88`, `if cells(out) <= 5:` → `<= 0:`; anchor count `1`;
proven live (classification map collapses to `{'fit': 'codepoints', '_clip': 'codepoints',
'_fit': 'codepoints'}`). Fired: **8 failed**, every one of them on the guard, with the guard's own
message — *"every derived truncator reports the same metric {'codepoints'}. `_metric_of` is no
longer discriminating, so the per-truncator oracle above is a constant wearing a derivation."*
**The guard is live and it discriminates.**

**And it is stronger than your description.** The classification probe drives a **benign** wide
source (`U+4F60 U+597D U+4E16 U+754C`, no banned points), on which the two orders are identical by
construction. So a coercion-ordering mutant **cannot escape by being reclassified** — verified under
M1: `darkside.fit` still reports `cells` while overrunning. That immunity is the reason the
per-metric oracle is safe, and it is the one thing `_metric_of`'s docstring does not say. Recommend
adding it; it is the strongest sentence available for that docstring and it is already true.

### 4. The seventh site — FOUND (`F14`)

### 5. The `B-53` routing — judgment holds, id collides (`F13`)

---

## Findings

### F13 — `B-53` is an id collision. The routed defect lands on an occupied id. [Severity: MEDIUM]

- **What:** `state.json:817-826` routes the new finding as
  `"B-53 (length-based truncators overrun a CELL budget on wide characters)"`. **`B-53` is already
  assigned.** `01-requirements.md:8817`, in the `A-95` carries table:

  > `B-53` — `#map-canvas` is `can_focus=False`, so the declared owner `"canvas"` is unreachable
  > through the real wiring … | **design batch**

  That meaning is load-bearing in at least four artifacts — `increment-002.md:411`,
  `increment-002-code-review-confirmation.md:184` and `:280`,
  `increment-002-retraction-check.md:131`, `:365`, `:373` — where `B-53` is the justification for
  substituting *nothing focused* for *from the canvas* in a live arm. `increment-004c.md:1085` uses
  the token for a third thing again.

  `B-54`, `B-55`, `B-56`, `B-60` and `B-61` are also in use. The next free id is **`B-62` or above**.

- **Where:** `.dev-flow/state.json:817` (`id` field); the occupant at
  `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:8817`.
- **Why it matters:** the routing's whole purpose is that a later increment picks it up. A later
  increment that looks up `B-53` gets the canvas-focus defect, owned by the **design batch**, and
  the cell-budget finding evaporates — which is precisely the failure mode `state.json`'s named
  carries exist to prevent. In a batch that has spent three passes on traceability, a collided id is
  the cheapest possible way to lose a real finding.
- **Suggested fix:** renumber to the next free id (`B-62` at time of writing — re-derive it, do not
  take my word for the maximum), update the `state.json` entry and the cross-reference in
  `tests/test_darkside_budget.py:_metric_of`'s docstring, and add the new id to the carries table so
  it is visible where `B-53` currently is.
- **Evidence state:** `executed` — collision confirmed by reading both the occupant and the four
  referring artifacts.

### F14 — THE SEVENTH SITE. The substitution framing survives in two live assertion messages. [Severity: MEDIUM]

- **What:** the six *narration* sites are correctly scoped — I re-read all six and each now carries
  an explicit SCOPE clause naming the length-based truncators, including site 6, which now says the
  opposite of what it said and says it correctly (*"THIS DOCSTRING CALLED THIS ARM WEAK AND IT IS THE
  OPPOSITE … it is the only arm here that discriminates the ORDER"* — verified: under M1 the five
  commutation arms are indeed the only census failures).

  What survives is the **substitution framing** in text that is not a docstring:

  | site | text | why it is now wrong |
  |---|---|---|
  | `tests/test_fold.py:398` (comment) | *"Re-pointed at the property that IS load-bearing: the output is coerced."* | The re-ruling names the **budget** load-bearing and the fixed point explicitly **not**. This sentence asserts the reverse. |
  | `tests/test_fold.py:409-411` (**live assertion message**) | *"…must be indistinguishable from its own coercion, **which is the property the ordering clause was reaching for**"* | Past tense frames the fixed point as the ordering clause's **successor**. The clause **stands**, and this half cannot substitute for it. |
  | `tests/test_inc3_census.py:187-189` (**live assertion message**) | same sentence, verbatim | same |

  A lesser instance, noted not charged: `tests/test_fold.py:412`'s message *"an unterminated override
  survived the cut"* still speaks the original stranding vocabulary, though it no longer asserts the
  mechanism.

- **Why it matters:** these are **failure messages**. They are read at exactly the moment someone is
  debugging a red coercion arm — the worst moment to be told that the fixed point is what the
  ordering clause was reaching for. Six docstrings were corrected and the two sentences a failing
  test actually prints were not. That asymmetry is how the claim comes back, which is the pattern
  this batch has now catalogued three times.
- **Suggested fix** (assertion message, both files — same replacement):

  ```python
  "the cut output is not coerced -- it must be indistinguishable from its own "
  "coercion. This is the WEAKER conjunct of `LLR-COERCE.2` and it is NOT the "
  "ordering clause's substitute: it cannot see a reversed order, because a "
  "truncate-then-coerce output is a fixed point by construction. It is kept "
  "because it catches a banned-point-to-banned-point remap that every length "
  "and cell check survives. The budget is armed in test_darkside_budget.py."
  ```

  and at `test_fold.py:398`, *"Re-pointed at the property that IS load-bearing"* →
  *"Re-pointed at the conjunct this arm CAN verify; the load-bearing one is the budget, armed in
  `tests/test_darkside_budget.py`."*
- **Evidence state:** `executed` for the sweep (two greps across `mapper/` and `tests/`, one on the
  refutation vocabulary and one on `LLR-COERCE`/ordering vocabulary); `planned` for the fix — **I did
  not write it**, and whoever applies it is its author.

### F15 — A new unmeasured over-generalisation, in the corrective arm's own docstring. [Severity: MEDIUM]

- **What:** `tests/test_darkside_budget.py:118-121` justifies the per-metric oracle with:

  > *"That is not a weakening: the ordering defect this clause guards shows up in EVERY metric,
  > because coercion inflates a zero-width banned point to one cell AND leaves the code-point count
  > unchanged — **so a reversed order overruns a cell budget and a length budget alike.**"*

  **The bolded half is false, and I measured it false.** Over 40 widths × 3 hostile sources = **120
  forbidden-order outputs** of the length-based truncator: **0 exceeded their code-point budget**,
  and the two orders were **byte-identical in all 120**. They must be — the premise of the sentence
  (`plain` leaves the code-point count unchanged) is exactly what makes a reversal *invisible* to a
  length budget, not visible to it. The sentence's own reason refutes its conclusion.

- **Why it matters:** it is the **same species** as the error that caused this entire chain — a
  mechanism claim stated as measurement, un-driven, inside the artifact that exists to prevent it.
  It is not load-bearing for the arm (the arm is correct as written), which is what keeps it MEDIUM;
  but left standing it licenses exactly the inference that produced `F9`.
- **Suggested fix:** replace the false justification with the true one, which is stronger:

  ```
  That is not a weakening, and the reason is not that the defect shows up in
  every metric -- IT DOES NOT.  A reversed order is INVISIBLE to a code-point
  budget, precisely because `plain` leaves the code-point count unchanged:
  measured, 0 of 120 forbidden-order `_clip` outputs exceed their budget and all
  120 are byte-identical to the specified order.  It is not a weakening because
  `darkside.fit` is the ONLY truncator whose order can differ at all, and it is
  the one held to CELLS.  The metric each truncator is held to is the metric in
  which its own reversal would show.
  ```

- **Evidence state:** `executed` — 120-comparison sweep, run read-only against the shipped `_clip`.

### F16 — One stale sentence inside the ratified text. [Severity: LOW]

- **What:** `01-requirements.md`, in the pass-3 corrections block: *"**The length bound is the
  discriminating conjunct** — and it is currently **unarmed**: no arm under `LLR-COERCE.2` asserts
  the emitted budget over the derived set."* It **is** armed now, by the same commit, and the
  `Acceptance-level invariant` twenty lines above says so.
- **Where:** `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md`, the second "further
  corrections" bullet.
- **Why it matters:** low — the surrounding block is explicitly pass-3's record and a careful reader
  will scope it. But "currently" is present tense in a live requirement, and this batch's whole
  lesson is that a stale claim in a requirement is read as a current one.
- **Suggested fix:** *"…and it was **unarmed at the time of this finding** — now armed at
  `tests/test_darkside_budget.py` by the re-ruling above."*
- **Evidence state:** `executed`.

### F17 — `tests/test_fold.py:396` is a 136-character line. [Severity: LOW]

An edit appended *"The ordering clause is normative."* mid-line without re-wrapping, leaving one
line at **136** chars in a file otherwise wrapped at ~79 (it is the only line over 100 in any of the
six edited files). **Not a ruff error** — E501 is not in the enabled rule set, and the count held at
**27** — so this is convention, not lint. Re-wrap when `F14` touches the same comment block.

---

## The `B-53` routing, judged on its merits

**The routing holds. Asserting cells against `_clip` would be the wrong oracle, and you were right
to refuse it.** Four reasons, each checked:

1. **`_clip`'s budget is code points by declaration.** `layered._vis_width`'s own docstring:
   *"Approximate visible width (simple: length, no CJK handling)."* Holding it to cells measures a
   documented approximation and reports it as a defect — the wrong-oracle error, and the requirement
   says "within the requested budget" without fixing a unit, so the declared unit is the defensible
   reading.
2. **It is genuinely pre-existing and out of the cut.** I checked provenance rather than taking the
   claim: `git log -S "no CJK handling" -- mapper/views/layered.py` resolves to **`2217cac`, a prior
   batch's Phase-6 close.** S-B(+C) did not introduce it and does not own `layered.py`'s width model.
   The `NOT_FIXED_HERE` field is accurate.
3. **Routing it costs `LLR-COERCE.2` nothing.** The ordering defect the clause guards lives *only* in
   the cell-measuring truncator, and `darkside.fit` **is** held to cells. So the per-metric oracle
   gives up no coverage of this requirement — verified by M1 killing 8 arms with the oracle as
   written. (This is the argument `F15`'s docstring should have made and didn't.)
4. **The finding itself is real and correctly sized.** Measured: `_clip(CJK, 2)` → 3 cells,
   `(CJK, 5)` → 9 cells, `(CJK, 20)` → **39 cells, 1.9×**. Titles are operator data and reach
   `_clip` through `_fit` at six call sites, so a CJK title overflows its card. MEDIUM is right, and
   so is routing it to the increment that owns the width model rather than smuggling it in here.

**The one thing wrong with the routing is its id** — see `F13`. Fix the number, keep the judgment.

---

## Evidence checklist

- [x] **Diff read in full** — `11d0a12..ce294f1`: `01-requirements.md` (+100/−40 at `LLR-COERCE.2`),
  `tests/test_darkside_budget.py` (170 lines, read entire), and all six narration sites. `executed`
- [x] **Correctness pass** — M1 fired on the full lane; M3 fired on the guard; metric stability under
  M1 verified; the 120-comparison length-budget sweep. `executed`
- [x] **Simplicity pass** — `_metric_of` is 10 lines and derives rather than lists; no premature
  abstraction. `n/a — no production code changed in this commit.`
- [x] **Reuse / duplication** — the new module reuses `truncators()` from `test_inc3_census` rather
  than re-deriving the set. Correct call. `executed`
- [x] **Tests reviewed for intent** — `F14` (failure messages narrate the refuted framing), `F15`
  (docstring justification false), plus the width-1 coverage observation. `executed`
- [x] **Verdict explicit** — **RATIFIED**; no HIGH findings open; `F13`/`F14`/`F15` MEDIUM,
  `F16`/`F17` LOW, none blocking. `executed`

## Verdict

- [x] **RATIFIED — the amended `LLR-COERCE.2` stands, and the budget arm is real.**

I fired what I was asked to fire and the record survives it. The reversal was accepted without
smoothing, the measurement is carried at my numbers, the discriminating conjunct is armed and kills,
and the guard on the derivation is itself driven. That is a corrected record, not a repaired
sentence.

The five findings are all in the corrective commit, none in the requirement's logic: an id
collision, a seventh site in the two places nobody re-read, one fresh over-generalisation of the
family this chain exists to catch, and two nits. **None of them blocks; all of them should be folded
before the increment closes**, and `F15` in particular — an unmeasured mechanism claim inside the
arm built to prevent unmeasured mechanism claims is worth catching now rather than at pass 4.

**I wrote no production code and no test code.** The snippets above are recommendations; whoever
applies them is their author and owes them an independent reviewer. I am not that reviewer for the
text I drafted.

**Handoffs.** `qa-reviewer`: the `stays_within_its_budget[1]` survivor under M1 — width-1 coverage
rests on a single named arm. `security-reviewer`: `B-53`'s substance (a 1.9× cell overrun from
operator-supplied CJK titles reaching six paint sites) is a painted-surface overflow, pre-existing
and unrelated to coercion — your call whether it wants a condition of its own in the batch it lands
in.

**Lanes this pass.** Baseline after restoration: **1080 passed**, 19 deselected, 3 xfailed,
**exit 0**, 305 s; ruff **27**, unchanged. Mutant lanes: **M1** full default **13 failed / 1067
passed** (exit 1, 306 s), budget module **8 failed / 9 passed**; **M3** budget module **8 failed /
9 passed**, all on the guard. `FLAKE-1` did not fire in either full-lane run.
