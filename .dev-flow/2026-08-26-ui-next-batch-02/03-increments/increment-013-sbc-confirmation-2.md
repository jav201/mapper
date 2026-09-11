# Increment 013 · S-B(+C) — Code Review CONFIRMATION PASS 2

**VERDICT: NOT CONFIRMED.**

**F1 is closed** — both cap derivations now die, independently, neither masking the other.
**F6 is closed** — the 2-arm measurement reproduces exactly and the rewritten docstring is
true in every checkable claim. **F2 / F3 / F4 survived the fold** — all three re-fired, all
three still killed. **F5 is not closed.** Its three named fixes all verify, and the
re-pointed arm does real work rather than riding the old assertion. But the brief's second
question — *is there a fifth place?* — has a yes, and it is **a live arm**, not prose:
`tests/test_inc3_census.py::test_llr_coerce_2_the_split_at_width_arm`, the **derived,
repo-wide** version of exactly the arm the fold re-pointed in `test_fold.py`. Fired: under
the forbidden order it stays **green**. Pass 1's own sentence applies verbatim —
*"Retracting the copy and leaving the original is how the claim comes back."*

| Item | Claim | Confirmed? |
|---|---|---|
| **F1** [HIGH] | row-cap arm parametrized over three geometries | **YES.** `row_cap = 4012` KILLED — 4 arms in module, **4 failed / 1059 passed** in the full lane. Indent mutant KILLED, 6 arms. Neither masks the other |
| **F5** [MED] | retraction completed in four places | **NO.** The four are correct. A **fifth** place stands — and it is an arm (`F7` below), plus two doc sites, one of them an **Acceptance criteria** bullet |
| **F6** [MED] | "zero signal" claim corrected | **YES.** 2 arms red reproduced exactly; census unchanged; `TC-081` absent; docstring true |
| **F2 / F3 / F4** | still closed after four post-pass-1 edits | **YES.** All three mutants re-fired and KILLED |

---

## Boundary statement

**Reviewed.** The `f3c1795..278fd36` diff in full (`layered.py` +31/−9, `test_fold.py`
+21/−4, `test_outline_caps.py` +43/−12, `01-requirements.md` +17); `mapper/views/layered.py`
`_clip`/`_fit` (`:73-115`); `mapper/darkside.py` `_CONTROL_MAP`/`plain` (`:496-536`);
`tests/test_fold.py:360-410`; `tests/test_outline_caps.py:1-200, 250-270`;
`tests/test_inc3_census.py:135-190`; `mapper/views/outline.py:190-270, 396-420`;
`01-requirements.md` §3.0 (`:496-535`), `LLR-COERCE.2` (`:588-616`), `LLR-N06.2.3`
(`:2000-2021`), `AT-056` (`:2528-2564`); pass 1's report in full.

**Not reviewed.** Security (gate 2's lane); the routed defects `B-50` / `B-51` / `B-52`;
the 27 pre-existing ruff hits; the `-m slow` lane's content beyond its exit code; any
increment before 013.

**Could not determine.** Nothing material.

**One writer.** Eight mutants, all applied with the Edit tool, all restored
unconditionally, all sha256-verified back to baseline. Final state — `git status` empty,
HEAD `278fd36`:

| file | sha256 (pre = post) |
|---|---|
| `mapper/views/outline.py` | `eac1eb1a…7484e` |
| `mapper/views/layered.py` | `dfe06f82…2660` |
| `mapper/darkside.py` | `4568b40d…d9f0` |
| `tests/test_outline_caps.py` | `3c33cda2…3c10` |
| `tests/test_fold.py` | `778cb484…ce01` |
| `tests/test_inc3_census.py` | `1153552a…a366` |
| `tests/test_agree_floor.py` | `3dc6f501…1aa3` |

Probe scripts were written **outside** the repo (`C:\Users\<operator>\clde\probe\`).

**Baseline reproduced**: **1063 passed**, 19 deselected, 3 xfailed, exit 0, 299 s. `FLAKE-1`
did not fire in any of the three full-lane runs in this pass.

**Environment traps observed.** All four files are pure CRLF (462 / 710 / 1276 / 302
`\r\n`, zero bare LF); every mutant re-verified the CRLF count after the edit, and every
one came back unchanged. No PowerShell file I/O was used on repo files. Every anchor count
was asserted `== 1` in-process with absolute paths before firing. `__pycache__` was purged
before every run. pytest was run `--color=no` so `^FAILED` parsing is real.
**No ANCHOR MISS occurred.**

---

## Findings

### F1 — CLOSED  [was HIGH]

The fix is the one pass 1 specified, and it works.

- **M1** — `mapper/views/outline.py:212`, `row_cap = max(state.w, state.w * state.h)` →
  `row_cap = 4012` (anchor count `1`, CRLF preserved 462/462):

  | scope | result |
  |---|---|
  | `tests/test_outline_caps.py` | **4 failed**, 18 passed |
  | **full default lane** | **4 failed, 1059 passed**, 19 deselected, 3 xfailed, **exit 1** |

  The four are `test_a_monster_title_is_clipped_to_one_frame[10000-geom1|geom2]` and
  `[400000-geom1|geom2]`. The reported message is the real pathology, not a proxy:
  `a 400000-character title produced a 4016-cell row at (24, 10); the frame is 24x10 = 240
  cells`. Pass 1's 16.7× overrun is now a red arm.

- **M2** — `indent_budget = max(2, state.w // 2)` → `indent_budget = 59` (anchor count `1`):
  **6 failed**, 16 passed — all six `test_the_indent_is_bounded_by_geometry[200|1000|4000-geom1|geom2]`.

- **Neither masks the other.** Each mutant was fired with the *other* derivation left
  intact. Under M1 all six indent arms stayed **green**; under M2 all six row-cap arms
  stayed **green**. The two pins are disjoint and each stands alone — which is the property
  the first fold lacked and pass 1 named.

- `geom0` = `(118,34)` correctly never reddens under either mutant, because that is the
  geometry whose value the constant was taken from. The sweep is doing exactly the work
  control 20 asks of it.

### F5 — NOT CLOSED  [MEDIUM — carried forward]

The three claimed fixes are real, and one of them is stronger than I expected. What is
missing is the thing the brief asked me to look for.

**(a) The re-pointed arm discriminates — it is not riding the old assertion.** This was the
brief's sharpest question, and the answer is measured, not reasoned.

- **M3** — `_clip`'s coercion removed (`s = darkside.plain(s)` → `s = s`, anchor count `1`).
  Probed directly on the arm's own fixture, `cut = _fit(source, 10)`:
  `cut` = `['0x61'×4, '0x202e', '0x62'×4, '0x2026']` — **NEW** `cut == plain(cut)` → **False**;
  **OLD** `count(U+202E) == 0` → **False**. Both fire. So M3 alone cannot separate them.
- **M4, the separation mutant** — `_CONTROL_MAP` altered so `U+202E` maps to a *different
  banned* point (`U+200E`) instead of `U+FFFD` (anchor count `1`, CRLF 545/545). Now:
  `cut` = `[…, '0x200e', …]` — **OLD** `count(U+202E) == 0` → **True, survives**;
  **NEW** `cut == plain(cut)` → **False, kills**.

  **That is the decisive measurement.** The re-pointed assertion kills a mutant the retained
  assertion lets through. It is doing work the old one cannot, and the re-point is a real
  strengthening rather than a comment edit.

- **[LOW] but it is shadowed inside its own test function.** Both M3 and M4 redden
  `tests/test_fold.py:369` (`assert leaked == []`) **first** — M3 reports
  `['0x1','0x202c','0x202e', …]`, and under M4 `U+200E` is itself banned. Line 369 is the
  broader predicate ("no banned point in the painted frame") and sits 35 lines above line
  404 in the same function, so at the pytest level no coercion mutant ever *reaches* the
  re-pointed assertion. Its discriminating power is real but only observable in isolation.
  Not a defect — the assertion is correct and states the honest property — but the arm's
  kill is attributable to line 369, and a future reader should not credit line 404 with it.

- **[LOW] the retained assertion's message still speaks the refuted vocabulary.**
  `test_fold.py:409` remains `assert cut.count(chr(0x202E)) == 0, "an unterminated override
  survived the cut"`. "Unterminated override" is precisely the refuted mechanism's language,
  and it is the one line of this arm the retraction comment above it does not reach.

**(b) `_clip`'s new docstring claims nothing unmeasured.** Every checkable claim verifies:
`_CONTROL_MAP` has **exactly 235** entries, **every** value is a single `U+FFFD`
(`distinct replacements: {'\uFFFD'}`, `all single char: True`) — so "length- and
index-preserving" follows. The 20,000-pair and 1058-arm figures are explicitly **attributed**
to gate 2 rather than asserted as this docstring's own measurement, which is the right
shape. The one forward-looking sentence — *"it is the order that stays correct if `plain`
ever DELETES rather than replaces"* — is presented as reasoning about a hypothetical, not as
a measurement. Honest.

**(c) The requirement blockquotes are an honest disposition, not narration.** I checked this
specifically because the brief asked. `01-requirements.md:597-608` and `:2011-2015` each (i)
name which clause is true and which cannot discriminate, (ii) give the refuting measurement,
(iii) state that the arm has been re-pointed, and (iv) close with **"Whether `LLR-COERCE.2`'s
ordering clause should survive at all now that its mechanism is refuted is a requirements
question, flagged and not decided by the gate."** The gate downgrades the clause's
*evidentiary status* — a statement of measured fact, inside a gate's lane — and explicitly
**refuses** to settle its survival, routing it instead. That is the correct boundary. No
finding.

**(d) — and this is why F5 is not closed — there is a fifth place, and it is an arm.**
See F7.

### F6 — CLOSED  [was MEDIUM]

Reproduced independently, and the corrected docstring is true.

- **M6** — coercion isolated at outline's call site: `title = _clip(node.ficha.title,
  row_cap)` → a local clip that keeps the cap **and** the ellipsis idiom but does not coerce
  (anchor count `1`). **Full default lane: 2 failed, 1061 passed**, exit 1. The two:

  ```
  FAILED tests/test_inc3_census.py::test_a89_every_reached_renderer_coerces_what_it_paints
  FAILED tests/test_outline_caps.py::test_outlines_title_path_is_coerced_not_merely_clipped
  ```

  **Every cap arm stayed green.** Gate 2's "zero signal" premise is refuted exactly as pass 1
  measured it, and the count is **2**, not 1 and not 3.

- **Sub-claims of the rewritten docstring, each checked:**
  - *"UNCHANGED across both folds"* — `git diff --stat a6598b2 278fd36 -- tests/test_inc3_census.py` is **empty**.
  - *"written two increments earlier"* — last touched at `540123c`, three commits before `a6598b2`.
  - *"`TC-081` … still does not exist"* — no `TC-081` node in `tests/` or `mapper/`.

  The docstring now says the call site *was* armed and explains why the arm still earns its
  place (call-site specificity, `C-56` code-point naming, legible failure). That is true and
  it is the correction pass 1 asked for.

### F7 — the fifth place, and it is a LIVE ARM  [Severity: MEDIUM — new]

`tests/test_inc3_census.py:148-165`:

```python
def test_llr_coerce_2_the_split_at_width_arm(tmp_path):
    """A source BALANCED at U+202E … U+202C, cut at width, leaves 0 overrides.

    The clause that makes the ordering non-vacuous: truncation MANUFACTURES the
    defect out of a source that was well-formed, so coercing afterwards cannot
    put the terminator back.
    """
    ...
            assert out.count(chr(0x202E)) == 0, (name, width)
            assert out.count(chr(0x202C)) == 0, (name, width)
```

This is the **same defect F5 item 2 named**, in the **canonical** version of the arm:
it runs over the **derived set of every truncator** at four widths, where `test_fold.py`'s
copy runs over one truncator at one width. Its docstring states the refuted mechanism as
*"the clause that makes the ordering non-vacuous"*, and its assertions are the exact
non-discriminating proxy the fold removed next door.

- **Fired — M5**, `_clip` rewritten to run the **forbidden order** (truncate, then coerce;
  anchor count `1`, CRLF 709/709 after the 4→3-line edit):
  `pytest tests/test_inc3_census.py tests/test_fold.py` → **42 passed, 3 xfailed**.
  The arm that exists to make the ordering non-vacuous **cannot see the ordering reversed.**
  (The re-pointed `test_fold.py` arm also stays green here, and that is *correct* — it no
  longer claims to test ordering. The difference is that this one still does.)
- **Why it matters:** the fold's own commit message says *"a test whose stated intent it
  cannot verify is worse than no test, because it reads as coverage."* This is that test,
  and it is the broader of the two. The retraction moved the copy and left the original —
  the precise failure F5 was raised to stop, recurring one file over.
- **Two further sites in the same class**, both uncorrected:
  1. **`tests/test_outline_caps.py:166-167`** — `test_the_clip_uses_the_existing_ellipsis_idiom`'s
     docstring: *"`layered._clip` is also where `LLR-COERCE.2`'s ordering lives — coerce,
     THEN truncate — so **routing through it fixes the ordering as well as the bound**."*
     That is the **verbatim sentence** retracted at `outline.py:232-247` and at
     `01-requirements.md:2535-2543` — still standing **in a file this fold edited**, two
     docstrings above the one it corrected.
  2. **`01-requirements.md:613-616`**, `LLR-COERCE.2`'s own **Acceptance criteria** bullet:
     *"truncation manufactures the defect out of a balanced source, so the ordering clause is
     not vacuous"* — uncorrected, **five lines below** the blockquote that refutes it. And
     **`:504-505`** (§3.0, governing a threshold the document calls *"mandatory in all four
     thresholds"*): *"necessary and not sufficient, because truncation can manufacture the
     defect out of a balanced source."* Site 2 is a live acceptance criterion, not prose.
- **Suggested fix** — the same shape already applied next door, so no new judgement is needed:

  ```python
  def test_llr_coerce_2_the_split_at_width_arm(tmp_path):
      """A source BALANCED at U+202E … U+202C, cut at width, is COERCED.

      RE-POINTED, `S-B(+C)` confirmation pass 2. This docstring read "truncation
      MANUFACTURES the defect … so coercing afterwards cannot put the terminator
      back" -- refuted: `_CONTROL_MAP` maps all 235 banned points to one U+FFFD
      each, so `plain` is index-preserving and a mutant running the FORBIDDEN
      order leaves this arm GREEN. The count was zero because the COERCION
      replaced the override, never because of the order.
      """
      ...
              out = function(source, width)
              assert out == darkside.plain(out), (name, width, "the cut is not coerced")
  ```

  For the two doc sites: carry the existing correction blockquote to `:613-616` and
  `:504-505`, and strike the "fixes the ordering as well as the bound" clause from
  `test_outline_caps.py:166-167`. All three are doc-only.

### F8 — the `AT-056` ratification text is now stale on F1  [Severity: LOW — new]

`01-requirements.md:2546-2551` is **unchanged** by this fold and still reads:

> *"derived, never a constant"* is pinned by driving **three geometries** … and asserting
> the **indent run** against `w // 2` at each.

That sentence is exactly what pass 1's F1 flagged as describing one of two siblings. The
fold closed the **code** half (verified above: the row-cap arm now sweeps, and M1 dies) and
left the **text** half untouched, so the ratification now *understates* what the arms pin.
That is the benign direction — a reader is told less than is true rather than more — which
is why this is LOW and not MEDIUM. But `AT-056` is the ratification of record, and the
17 lines this fold added to `01-requirements.md` went to `LLR-COERCE.2` and `LLR-N06.2.3`,
not here.

- **Suggested fix:** one clause — *"…and asserting the **indent run** against `w // 2` and
  the **widest row** against `w * h` at each; re-fired at the confirmation pass, each
  derivation replaced by its 118×34 constant reddens its own arms and only its own
  (row-cap: 4 arms, 1059 passed; indent: 6 arms)."*

---

## Regression — F2 / F3 / F4 after four post-pass-1 edits

`mapper/views/outline.py` was **not** touched by `278fd36` (sha256 identical to pass 1's
recorded `EAC1EB1A…7484E`), and `tests/test_agree_floor.py` likewise (`3DC6F501…1AA3`).
`tests/test_outline_caps.py` **was** edited, and F2's and F4's arms live in it — so all
three were re-fired rather than argued from hashes.

| finding | mutant | result |
|---|---|---|
| **F2** | `_indent` → `f"{DEPTH_MARK}{level // 10} "` (`outline.py:55`) | **KILLED — 3 failed**, 19 passed; all three `test_a_compressed_indent_still_tells_the_truth_about_depth[200\|1000\|4000]` |
| **F3** | `_fit_declared`'s `if not candidate and kept:` → `if len(candidate) < len(kept) and kept:` (`outline.py:418`) | **KILLED — 2 failed**, 24 passed; `test_at057_above_the_floor_the_canvas_still_declares[legacy]` and `[anidado]` |
| **F4** | module-level `_never_called(state) -> int: return state.pan_x` (never executed) | **KILLED — 1 failed**, 21 passed; `test_the_caps_licence_holds_outline_still_reads_no_pan` |

All three still closed. The fold broke nothing it did not touch.

---

## Evidence checklist

- [✓] **Diff read in full** — `f3c1795..278fd36` across all four files, plus `test_inc3_census.py:135-190` and `01-requirements.md` §3.0 / `LLR-COERCE.2` / `LLR-N06.2.3` / `AT-056` as context the diff did not cover.
- [✓] **Correctness pass** — both cap derivations fired independently (`outline.py:211-212`); `_clip`'s coercion fired three ways (removed, re-mapped, reordered); `_CONTROL_MAP` cardinality and value-shape verified in-process (235 / single `U+FFFD`).
- [✓] **Simplicity pass** — no new abstraction in this fold; the F1 fix is one `parametrize` decorator on an existing arm and adds no fixture.
- [✓] **Reuse / duplication checked** — found the duplication that is this pass's finding: `test_inc3_census.py:148` and `test_fold.py:399-409` are the same arm, and only one was re-pointed (`F7`).
- [✓] **Tests reviewed for intent** — `F7` (an arm whose docstring states an intent a forbidden-order mutant proves it cannot verify); `F5(a)` LOW (the re-pointed assertion is shadowed by an earlier, broader one in its own function).
- [✓] **Verdict explicit** — below.
- [✓] **Eight mutants fired, all restored, all sha256-verified**; five anchors asserted `== 1` before firing; CRLF counts re-verified after every edit; `__pycache__` purged before every run; **no ANCHOR MISS**.

---

## Verdict

- [ ] OK to advance
- [x] **OK with the listed fixes applied first**
- [ ] Block

**NOT CONFIRMED, but nothing HIGH stands.** F1 — the one HIGH — is **closed by firing**, and
closed properly: each cap derivation now dies on its own and neither pin masks the other.
F6 is closed and its docstring is true. F2, F3 and F4 survived the fold intact.

F5 is carried forward at **MEDIUM** for one reason: the brief asked for a fifth place and
there is one, and it is **a live arm asserting an intent a fired mutant shows it cannot
verify** (`F7`) — the derived, repo-wide sibling of the arm this fold re-pointed. The
re-point itself was done well; `M4` proves the new assertion kills a mutant the old one
lets through, so this is not a cosmetic gap in a cosmetic fix. It is the same claim, still
standing in the broader place, which is the exact recurrence F5 was raised to prevent.

`F7`'s fix is mechanical — the pattern already exists 20 lines away in `test_fold.py` — plus
three doc corrections and `F8`'s one clause. None of it is a code change to a shipping path.
A third confirmation pass should fire **one** mutant: the forbidden order against
`tests/test_inc3_census.py`, which must go **red**.
