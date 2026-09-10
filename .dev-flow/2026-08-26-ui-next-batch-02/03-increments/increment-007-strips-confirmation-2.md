# Increment 007 · Inc-STRIPS — Confirmation 2 (final)

**Batch** `2026-08-26-ui-next-batch-02` · **Repo** `C:\Users\jjgh8\Github\mapper`
**Scope** the four axes from `increment-007-strips-confirmation.md` (H1, H2, M1, M2) and §9.7's ledger
**Sole writer** asserted · **Date** 2026-09-10

---

## BLUF

**PASS. 0 HIGH.** Both HIGH axes are discharged by execution, not by reading: the H1 mutant reddens
the new small-map arm, `MUT-A` is genuinely KILLED where round 2 recorded it SURVIVED, and `MUT-Q`
reddens both AT arms. The `legacy` regression is fixed and the pathological case is provably
un-touched — the guard is a no-op at 600 branches, so the fix **cannot** have un-bounded it. §9.7's
ledger reproduces to the digit, including `ruff 27 = 27` once the measurement method is stated
properly.

The residue is documentary and sits **inside** two of the four axes rather than outside them: M1 was
raised as a four-part finding and round 3 fixed parts 1–2 while leaving parts 3–4 neither fixed nor
declared as carries, and H2's "corrected to five" lands on a number its own next sentence refutes by
enumerating six. Neither is a correctness defect, neither touches shipped behaviour, and neither
makes a test lie — so neither blocks. Both are named below with reproductions, for the split.

---

## Tree state — sole writer, asserted

Restore pins held at every boundary. Every mutant's digest was asserted **after installation and
before believing any verdict**, per the Windows/POSIX path hazard; every restore was asserted
byte-identical to the pin.

```
mapper/app.py        70699785f8dc2c0c661f398221781ca2cb8c3ea8bca4a1e50e89e711415412f5   pre = post ✓
tests/test_strips.py fdb1b687a28e1d1477c04754b089bdc6037183f3a1d2de1d48c77d255e0bd68d   untouched ✓
tests/test_pan.py    ae4cb900fd1167d978264a8d2b1ab6823f835e0c63402848e419eaeab1d1d40e   untouched ✓
```

`git status --porcelain` at exit is byte-identical to entry. `PYTHONDONTWRITEBYTECODE=1` on every
invocation; `find -newermt` confirms **no** bytecode was written during this pass, and all
`__pycache__` directories were purged at exit (count 0). Three scratch files (`_mut.py`,
`_probe_h1.py`, `_app.bak`) were created in the repo root and **removed**; they are named here
because they briefly polluted a ruff measurement, which is recorded in Axis 5 rather than hidden.

All anchors were single-line plain strings. **No anchor matched zero times**, so no BAD/CRASH arose;
had one, it would be recorded as BAD and never as SURVIVED.

---

## Axis H1 — the unconditional reserve · **DISCHARGED**

### The mutant, fired

Guard disabled at `mapper/app.py:1804` (`if max(0, base) // per_entry >= branches:` →
`if False:`), digest `7ef5ec6d…` asserted before the run.

```
tests/test_strips.py -m ""     1 failed, 10 passed
FAILED test_a_small_map_declares_NOTHING_because_it_drops_nothing
```

**KILLED, by exactly the new arm and by nothing else.** The other ten arms stay green under the
mutant — which is the measured explanation for how the regression shipped through round 2, and it is
what makes the new arm non-vacuous rather than decorative.

### The shipped map, measured both ways

Rendered the **real** `maps/legacy` fixture through `install()` + `open_map` (measured fanout **3**,
8 nodes), reading `rows_in` over `#map-minimap`:

| tree | size | limit | branches drawn | remainder declared | strip.h | canvas.h |
|---|---|---|---|---|---|---|
| **fixed** | 35x14 | 3 | **3 of 3** | **NONE** | 3 | 3 |
| **unconditional reserve** | 35x14 | 1 | **1 of 3** | `+2 ramas sin mostrar` | 3 | 3 |
| fixed | 80x24 | 3 | 3 of 3 | NONE | 2 | 15 |
| fixed | 118x34 | 3 | 3 of 3 | NONE | 1 | 27 |

`§9.1`'s claim is confirmed **to the digit, including the part that makes it a defect**: the strip's
height and the canvas's height are **identical** at 35x14 either way, so the two dropped branches
bought nothing. The legend is on the frame in every row of the table.

### The pathological case was not un-bounded

600 branches, fixed tree, `rows_in` over the strip:

```
118x34   strip.h=3  canvas.h=25  drawn=16  declared=584  conserved ✓  legend ✓
 80x24   strip.h=3  canvas.h=14  drawn= 9  declared=591  conserved ✓  legend ✓
 60x34   strip.h=3  canvas.h=23  drawn= 6  declared=594  conserved ✓  legend ✓
```

Stronger than a spot check: **the same three rows are produced byte-identically by the mutant tree.**
At 600 branches the guard's cheap test is false, so the fix takes the identical code path as the
unconditional reserve. The fix is therefore a strict improvement — it changes behaviour only where
everything fits, and cannot regress the bound by construction, not merely by measurement.

Arithmetic checked independently at 118: `base = 3·118 − 14 − 37 = 303`, `per_entry = 17`,
`(303 − 26) // 17 = 16` — matching the painted count.

Edge paths read: `branches == 0` returns 0; negative `base` at tiny widths falls through to
`max(0, base − 26) // per_entry = 0` and declares the whole fanout. No circularity — when the cheap
test fails, `(base − 26) // per_entry ≤ base // per_entry < branches`, so `undrawn > 0` always holds
on the declaring path.

## Axis H1b — `MUT-A` · **DISCHARGED**

`_MINIMAP_ENTRY_OVERHEAD = 5` → `40`, digest `a139c705…` asserted.

```
tests/test_strips.py -m ""     1 failed, 10 passed
FAILED test_a_small_map_declares_NOTHING_because_it_drops_nothing
```

**KILLED.** Round 2's "SURVIVED — equivalent by contract" is refuted on the round-3 tree, and §9.2's
reading is the correct one: the survival was the coverage gap, and the explanation was the defect.

## Axis M2 — `MUT-Q` · **DISCHARGED**

Query echo dropped from the count region (`f"{head}{self._query_echo()}{tail}"` →
`f"{head}{tail}"`, `mapper/app.py:2004`), digest `aa273529…` asserted.

```
tests/test_strips.py -m ""     2 failed, 9 passed
FAILED test_at_llr_n07_3_4_..._at_the_shipped_bound[118x34]
FAILED test_at_llr_n07_3_4_..._at_the_shipped_bound[80x24]
```

**KILLED by both AT arms**, where round 2's `MUT-Q` reddened zero here. The clause now has a
shipped-bound oracle and it is discriminating for the stated reason — the region holds no titles.

## Axis H2 — the closure marking · **DISCHARGED** (one blemish, below)

`01-requirements.md:3163-3181` now agrees with `state.json` on every load-bearing point:

| claim | `01-requirements.md` | `state.json` | agree |
|---|---|---|---|
| predicate 1 status | PARTIALLY CLOSED, "THIS REQUIREMENT REMAINS OPEN" | `open_blocks[0].status = "OPEN — fanout vector CLOSED…"` | ✓ |
| fanout vector | closed at the shipped bound, counterfactual executed | `vectors.fanout: CLOSED by Inc-STRIPS` | ✓ |
| title-length vector | OPEN, 4000-char title, routed to `Inc-CRUMB` | `vectors.title_length: OPEN … Routed to Inc-CRUMB` | ✓ |
| flip condition | "flips only when **both** vectors are closed" | `blocks:` same sentence | ✓ |

The superseded `✅ CLOSED` marking is **named** rather than quietly replaced, and a repo-wide grep
confirms the only surviving occurrence of that string is the one naming it as superseded. This is the
discipline the batch's own `discharge` rule asks for, applied to itself.

## Axis M1 — the meter comment · **DISCHARGED on its headline; residue below**

The two blocks are genuinely changed this time — verified against the prior pass's byte-identity
claim, not taken on the packet's word:

- `mapper/app.py:95-109` — a `SUPERSEDED BY Inc-STRIPS` preamble stating today's truth first
  (`max-height: 3; overflow: hidden`, over-long echo **dropped** not grown), then
  `HISTORICAL, from the pre-bound tree:` over the old text unedited. This closes the prior pass's
  *demonstrably harmful* sub-item: a reader is now told the cap must not be relaxed.
- `mapper/app.py:2095-2124` — same shape, and it names the packet's own false claim in the comment
  itself (*"An earlier revision of THIS increment claimed to have corrected it in place and had
  not"*).

Both surviving `height: auto` assertions about `#map-pagination` (`:103`, `:2112`) are now **inside**
HISTORICAL blocks. The remaining `height: auto` hits in the file are unrelated widgets.

§8.3's table row still reads *"corrected in place"* — but §9.4, in the same document, states plainly
that the claim was false. Self-correction by a named note is the increment's own declared convention,
so this is not counted against it.

---

## Findings — residue, all in-axis, none blocking

### R1 — M1's sub-items 3 and 4 are neither fixed nor carried [Severity: MEDIUM]

The prior pass raised M1 as four enumerated sub-items with a suggested fix naming each. Round 3 fixed
sub-items 1–2 and §9.8's carry list names four **different** items (L1–L4). Sub-items 3–4 fall
between the two lists.

- **`mapper/app.py:1899`** — `_query_echo`'s **live** docstring: *"it is unbounded in length on a
  region that **WRAPS**, so without a cell budget it grows the strip and takes rows from
  `#map-body`."* False since `#map-pagination { max-height: 3; overflow: hidden; }`.
  This is the sharpest form: the corrected module-level comment at `:99` warns that *"a reader who
  trusts the superseded reasoning below would relax the cap"* — and the method **the cap lives on**
  still carries that superseded reasoning as live text, un-relabelled.
- **`tests/test_search.py:2337-2340`** — the same premise verbatim: *"`#map-pagination` has no height
  rule, so it is `height: auto` and it WRAPS"*.
- **`mapper/app.py:3339`** — *"the minimap holds **24** branch entries and its legend at 118
  columns."* **Measured: 16.** (`(3·118 − 14 − 37 − 26) // 17 = 16`, and the 600-branch render paints
  16.) `MINIMAP_BRANCHES` no longer exists.
- **`mapper/app.py:3346`** — *"`legacy` has **eight branches**."* **Measured: 8 nodes, root fanout 3.**
  The minimap renders one entry per branch, so the number that matters here is 3. The sentence's
  conclusion (*"its minimap wants ONE row"*) is true at 118 — only the count is wrong.
- **`mapper/app.py:3336`** — *"Capping the meter and the branch list is **NECESSARY AND NOT
  SUFFICIENT**."* §8.1 declares this refuted by measurement and lands on *"the meter was the binding
  cause; the minimap bound and the clip are defence in depth."* Defensible as a forward-looking claim
  about the title-length vector, but written as present fact and contradicted by the packet's own §8.1.

**Why it matters:** stale comments that assert the opposite of the stylesheet are the exact class this
increment spent two rounds closing, and the fix for the class was applied to two sites while four
more were left. **Why it does not block:** no shipped behaviour, no assertion, no test that can pass
vacuously — `tests/test_search.py:2340` is a docstring, not an oracle.
**Reproduction:** `grep -n "WRAPS" mapper/app.py tests/test_search.py`; `sed -n '3330,3350p' mapper/app.py`.

### R2 — H2's "corrected to five" is refuted by its own next sentence [Severity: MEDIUM]

`01-requirements.md:3178-3181`:

> **"The three unbounded strips" is corrected too: there are FIVE** content strips outside
> `#map-body`. This increment bounds two; `HintLine` and `KeyBar` were already bounded in Python;
> `TabStrip` and `#map-toast` are `Inc-CRUMB`'s.

The enumeration names **six**: `#map-minimap`, `#map-pagination`, `HintLine`, `KeyBar`, `TabStrip`,
`#map-toast`. `MapScreen.compose` (`mapper/app.py:1233-1252`) confirms all six are siblings of
`#map-body`, with a seventh widget (`Input#search-input`) outside it too.

A correction mandated because a number in the artifact of record was wrong has replaced it with
another wrong number. **Why it does not block:** the enumeration is complete and every routing
decision on it is correct, so a reader following the list reaches the right picture; only the headline
count is wrong, and no decision hangs on it.
**Reproduction:** `sed -n '3178,3181p' .dev-flow/.../01-requirements.md`; `sed -n '1233,1252p' mapper/app.py`.

### R3 — the two records now count the same strips differently [Severity: LOW]

`state.json:292` still reads *"TabStrip's crumb is a **fourth** unbounded strip"* — internally
consistent with the **old** "three unbounded strips" framing that `01-requirements.md` has just
replaced with a different metric ("content strips outside `#map-body`"). Not wrong on its own terms;
it is now the only place still counting on the superseded basis.

---

## Axis 5 — §9.7's ledger, re-executed

```
default lane : 913 passed, 19 deselected, 3 xfailed   exit 0   (197.67s)   ✓ matches
all markers  : 932 passed,                3 xfailed   exit 0   (251.44s)   ✓ matches
ruff SET     : working tree 27 violations = HEAD 27 violations
               NEW: none · GONE: none     (--isolated, per-(file,rule) from JSON)   ✓ matches
source files : 1  (mapper/app.py; test_strips.py + test_pan.py are tests)   ✓ matches
baseline     : tests/test_strips.py resolves 11 arms, 11 passed              ✓ matches
```

Ledger arithmetic confirmed against the prior pass's independently measured 912/931:
`913 = 912 + 1` and `932 = 931 + 1`, the one being `test_a_small_map_declares_NOTHING_because_it_drops_nothing`.

**Two method notes, recorded because either one would have produced a false figure:**

1. **"27" is a violation count, not a set size.** The per-`(file, rule)` **set** is 19 on both sides.
   The ledger's `27 = 27` is correct as violations; a reader taking "SET" literally measures 19 and
   reports a mismatch that is not there. Worth one word in a future ledger.
2. **The HEAD side must exclude `prototypes/`.** Materialising HEAD via `git archive` into a scratch
   directory yields 45 violations, because the scratch is not a git repository and ruff's
   `respect-gitignore` therefore does not apply — `prototypes/` is gitignored **and** tracked (a
   pre-existing repo quirk, out of scope). Excluding it: **HEAD = 27 violations, SET 19**, identical
   to the working tree with an empty NEW and an empty GONE.

My own scratch files added four `(file, rule)` pairs to a first ruff run; they were removed and the
measurement re-taken. Recorded rather than quietly re-run.

---

## Evidence checklist

- [x] **Diff read in full** — `mapper/app.py:1755-1849` (constants, `_minimap_entry_limit`,
      `_minimap_text`), `:85-109`, `:2088-2124`, `:3325-3352`; `tests/test_strips.py:1-440` entire;
      `01-requirements.md:3102-3216`; `state.json` `open_blocks` + `decisions_log`.
- [x] **Correctness pass** — `branches == 0`, negative `base`, and the declaring path's
      `undrawn > 0` invariant all traced; no unreachable-remainder or circularity path found.
- [x] **Simplicity pass** — the fix is one `if` and one early return; it resolves the
      limit/remainder circularity by ordering rather than by an added abstraction. No premature
      generality.
- [x] **Reuse / duplication** — no new util; `darkside.fit` and `rows_in` are the existing idioms.
- [x] **Tests reviewed for intent** — all three claimed kills fired against installed, digest-asserted
      mutants; the small-map arm is proven non-vacuous by its own mutant and is the sole killer of two.
- [x] **Verdict explicit** — below.

---

## Verdict

- [x] **OK to advance — PASS**
- [ ] OK with the listed fixes applied first
- [ ] Block

**PASS · 0 HIGH.** All four axes discharged: H1 and its `MUT-A` corollary by execution against
digest-asserted mutants and by direct render of the shipped `legacy` map in both directions; M2 by
`MUT-Q` reddening both AT arms; H2 and M1 by reading, with `01-requirements.md` and `state.json` now
agreeing on every load-bearing point and both superseded comment blocks genuinely rewritten.

**Outside the confirmed fixes:** M1 was raised as four sub-items and only two were fixed — four stale
comments still assert the pre-bound layout, including `_query_echo`'s own live docstring and two
measured-false numbers in the stylesheet comment (`24` branch entries where the measurement is 16,
`legacy` "eight branches" where the fanout is 3) — and H2's replacement count of "five" strips is
refuted by the six its own next sentence enumerates; all are documentary, none touches shipped
behaviour or any oracle, and they are recorded above as R1–R3 with reproductions for the split.
