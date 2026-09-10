# Code Review — Increment 4c, ROUND-2 CONFIRMATION PASS

**Reviewer:** code-reviewer (fresh, independent — did not participate in round 1) · **Date:** 2026-08-29
**Branch:** `feat/ui-next-batch-02` · **Entry:** `9ba2f26` · nothing committed
**Verdict: BLOCK** — one HIGH survives. It is round-1 **F1 narrowed, not closed**: the ban's
*method* axis is now genuinely derived, but the closure stops at the class boundary, and the same
defect re-enters through a module-level helper. Reproduced against the full default lane
(`853 passed`) with the identical operator-visible lie round 1 measured (**4501 painted over a graph
holding 6001**). The minimal fix is proven below — no false positive on the shipped tree, kills the
mutant by name.

Everything else in scope is genuinely closed. H2, S1/S1b, R2-E and R2-G each went RED under a
mutation I constructed myself, with the correct arm reddening in each case.

---

## State verified before anything was read

| Check | Expected | Measured |
|---|---|---|
| branch | `feat/ui-next-batch-02` | ✓ |
| HEAD | `9ba2f26` | `9ba2f26139cc6bf32853bef63e2a6bb5d97e2110` ✓ |
| `mapper/app.py` | `3aff3829…fcea4` | `3aff38298f2cea33d4f891066f117f3d05614678c74bf2cf2a5333c6aa7fcea4` ✓ |
| `tests/test_search.py` | `a257b9c1…be084` | `a257b9c1d2769a11c32856b72314a797cea87902f0cde5943b5c789f0c3be084` ✓ |
| working tree | Inc-4c uncommitted | 4 modified, 3 untracked ✓ |

The tree did not move under me. Re-verified identical after the last arm.

### Mirror fidelity — and a fidelity trap worth recording for the batch

`git clone --local --no-hardlinks` into the scratchpad produced a mirror that was **NOT** byte-identical
to the source: `core.autocrlf=true` is set in both repos, so the clone's checkout re-materialised every
tracked file with CRLF while the source working tree holds LF. Measured on one file:
`mapper/search.py` 5910 bytes at source, 6032 in the clone, different sha256. Overlaying `app.py` and
`test_search.py` by hand hides this — those two match, and every other file silently does not.

**Both round-1 reviews and both of the author's batteries used `git clone --local --no-hardlinks` +
overlay.** Their `app.py` / `test_search.py` verdicts are unaffected (the two overlaid files are
byte-exact), but any claim resting on the *rest* of the tree from those mirrors rests on
line-ending-converted sources. Recording it as a batch control, not as an Inc-4c defect.

I discarded the clone and rebuilt the mirror by `tar` copy, then verified all **236 tracked files
byte-for-byte identical** (`git ls-files -z | xargs -0 sha256sum`, diff empty).

- Baseline on the mirror: `tests/test_search.py` → **36 passed in 52.58s**; full default lane →
  **853 passed, 17 deselected, 3 xfailed in 194.47s**, matching R2.6 exactly.
- Every arm fired **one at a time, foreground, single writer**. No two batteries ever ran against one
  tree. `sha256` restore verified after every arm — `3aff38298f2cea33` / `a257b9c1d2769a11` every time.
- **The real repo was never written to.** `PYTHONUTF8=1` on every python/pytest invocation.

---

## Findings

### H1-R — the derived ban closes only over `self.X` edges INSIDE `MapScreen`; the same defect re-enters through a module-level helper  [Severity: HIGH]

**What.** The fix is real as far as it goes: the six-name tuple is gone and the governed set is closed
transitively (`tests/test_search.py:657-666`) over the read map, with the leak assertion at `:677-682`.
I re-derived it from the code rather than trusting the transcript and **reproduce R2.1 exactly** —
93 methods parsed, closure from `_count_line` = 8 methods, 0 leaks, and the three the round-1 hand-list
missed are genuinely in it:

```
seed ['_count_line'] -> 8: ['_count_line', '_query_echo', '_search_index', '_search_order',
                            '_seat_glyph', '_seat_row', '_suspended_count_line', '_whole_graph_tally']
   leaks: {}
```

And it **can** go red. MUT-1 (a bare `self.folded` read added to `_query_echo`, one of the three names
the hand-list never covered):

```
MUT-1  KILLED  |  1 failed in 0.23s
E  AssertionError: `_query_echo` is in the count chain and reads ['folded']: the number the
   region paints would be narrowed by the viewport, which is risk A-6
```

**But the read map is built from `self.X` reads only** — `_map_screen_self_reads` filters on
`isinstance(sub.value, ast.Name) and sub.value.id == "self"` at `tests/test_search.py:1257-1259`, and
its keys are `MapScreen` methods only (`:1261-1262`). **A helper that takes the screen as a parameter
has no `self.` in it and is not a method, so it is invisible on both axes at once.**

**Where.** `tests/test_search.py:650` (`reads_by_method = _map_screen_self_reads()`), `:657-666` (the
closure), `:1253-1263` (the map's construction).

**Evidence — constructed, not argued.** MUT-2 adds one module-level function to `mapper/app.py` and
points the tally at it:

```python
def _visible_matches(screen, ids):
    """Narrow a hit set to what is not hidden by the fold state."""
    return {i for i in ids if i not in screen.folded}
```

`_whole_graph_tally`'s own `self.X` reads are unchanged (`_search_index`, `query_text`), so `:698`
still passes, the `SearchIndex` census at `:729-737` still counts one construction, and the leak loop
sees nothing.

| Arm / lane | Verdict |
|---|---|
| `tests/test_search.py` (36 arms, per-arm) | **36 passed** — including `test_the_count_and_the_paint_share_one_resolution` |
| full default lane | **853 passed, 17 deselected, 3 xfailed in 194.47s** |

That is the declared baseline, digit for digit, on a tree whose count region lies. Measured on the same
12002-node graph, 1500 matching nodes folded:

```
whole-graph truth             : 6001
tally, nothing folded         : 6001
tally, 1500 matching folded   : 4501
painted: búsqueda: «zeta» · 4501 coincidencias en el mapa · esc limpiar · resaltado y recorrido suspendidos
```

**Why it matters.** This is risk A-6, **fifth instance**, and it is the round-1 finding's own sentence
still true after the fix: *"a new link in the count chain evades it and the entire suite."* `C-31` says
a hand-listed set survives every mutation of the code it governs — the author correctly applied that to
the method names and left the *shape of the edge* hand-scoped instead. A module-level helper taking the
screen is not an exotic mutation; it is the ordinary way a Python author factors a set operation out of
a method, and the file already carries module-level functions.

**Suggested fix — proven on this tree, both directions.** Let the closure cross the class boundary:
module-level functions join the map keyed by name, valued by every attribute they read off *any* base
plus every function they call by bare name, and each `MapScreen` method gains its bare-name calls as
edges. Insert immediately before `reaching = {"_count_line"}` at `tests/test_search.py:657`:

```python
_tree = _app_tree()
_cls = next(n for n in ast.walk(_tree)
            if isinstance(n, ast.ClassDef) and n.name == "MapScreen")

def _calls(f):
    return {n.func.id for n in ast.walk(f)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}

for _item in _cls.body:
    if isinstance(_item, (ast.FunctionDef, ast.AsyncFunctionDef)):
        reads_by_method[_item.name] |= _calls(_item)
for _fn in _tree.body:
    if isinstance(_fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        reads_by_method.setdefault(_fn.name, set())
        reads_by_method[_fn.name] |= _calls(_fn) | {
            n.attr for n in ast.walk(_fn) if isinstance(n, ast.Attribute)
        }
```

Verified, both arms of the control:

```
A · shipped tree + fix            1 passed in 0.32s      (no false positive)
B · MUT-2      + fix              FAILED
   E  AssertionError: `_visible_matches` is in the count chain and reads ['folded']: ...
```

Fold **F-D below into the same edit** (seed the closure from `{"_count_line", "_search_hits"}`); I
measured that it reaches 9 methods and still reports zero leaks, so it is free.

---

### F-B — the coercion arm cannot tell coercion from TRUNCATION, and a truncating echo misreports the operator's query on a green suite  [Severity: MEDIUM]

**What.** `test_the_query_echo_coerces_the_operators_text` asserts the five control points are absent
(`tests/test_search.py:979-980`) and that the region is still declaring (`:984-985`, label + `"zeta"`).
It never asserts that the text **after** the hostile run survives. So an echo that sanitises by
*cutting at the first coerced code point* satisfies every predicate in the arm.

The brief asked whether the control discriminates. It discriminates the two failures it was written
for and not this one:
- **cannot pass on an empty/absent region** — ✓ confirmed. An echo returning `""` drops `"zeta"` and
  `:985` reddens.
- **five absences mean coercion, not deletion** — ✗ only partly. The arm's own docstring claims this
  at `:950-955`; the assertions establish "not *total* deletion", not "not truncation".

**Where.** `tests/test_search.py:938-985`, specifically the missing tail assertion after `:985`.

**Evidence.** MUT-8 replaces the echo with a flatten-then-cut-at-first-coerced-point form:

```
MUT-8  SURVIVED  |  36 passed in 50.52s   (tests/test_search.py, per-arm: all 36 green)

operator typed/pasted : 'zeta<U+200B>informe'
region echoes         : 'zeta'
```

U+200B is **reachable through the real operator path**: the security review established that
`Input._on_paste` takes `event.text.splitlines()[0]`, which strips line breaks and nothing else, so a
query pasted from a web page carrying a zero-width space arrives verbatim. The region then declares
`búsqueda: «zeta»` for a search the operator ran as `zeta<U+200B>informe`. That is the **same**
lying-affordance class as R2-E — "a region that misreports the query it is declaring"
(`tests/test_search.py:1053-1059`) — one code point over from where the author closed it.

**Why it matters.** R2-E was found and fixed because the flattening merged tokens; nothing generalised
the lesson to the coercion sink beside it. MEDIUM rather than HIGH because the **shipped code is
correct** — `darkside.fit` replaces rather than truncates, verified: `'abc' in painted` is `True` on the
shipped tree. This is a test-strength gap, not a live defect.

**Suggested fix — one line**, after `tests/test_search.py:985`:

```python
# The coercion REPLACES; it does not truncate.  An echo that cut at the first
# coerced point passes every assertion above while declaring a query nobody ran
# (`zeta<U+200B>informe` echoes as `zeta`) -- R2-E's defect, one sink over.
assert "abc" in painted, ("the echo truncated at the hostile run", painted)
```

Under MUT-8 `painted` ends at `zeta`, so this reddens; on the shipped tree it passes.

---

### F-D — `_search_hits` carries a ONE-METHOD ban with no closure, which is the shape H1 just failed on  [Severity: MEDIUM]

**What.** The count chain is now derived; the paint chain is not. `_search_hits` is banned by a single
`_self_reads(MapScreen._search_hits)` call at `tests/test_search.py:689-690` — no transitive closure at
all, so it is weaker than the hand-list the increment just deleted. Every evasion in H1-R applies here
one hop earlier, and this is the surface where round 1's *previous* A-6 instance was constructed
(count 5 against 4 painted highlights on the `adjuntos` fixture).

**Where.** `tests/test_search.py:684-690`.

**Why it matters.** The author's stated reason for excluding `_search_hits` from the closure is
**sound** — I verified `_count_line` does not reach it (`_search_hits` reads `_search_order`, not the
reverse; `:693`), so it genuinely belongs to `_view_state`'s chain, not the count's. The defect is not
the exclusion, it is that the exclusion drops it into a weaker regime instead of its own derivation.

**Suggested fix.** Seed the (H1-R-corrected) closure from both entry points and delete the special
case: `reaching = {"_count_line", "_search_hits"}`. Measured on the shipped tree: 9 methods reached,
**zero leaks**, so it costs nothing today.

---

### F-C — `VIEWPORT` is still a hand-list, and it has NO non-vacuity anchor  [Severity: MEDIUM]

**What.** `VIEWPORT = ("folded", "pan_x", "pan_y")` at `tests/test_search.py:615` governs both the
derived ban (`:678`) and the `_search_hits` ban (`:690`). Nothing anywhere asserts these three names
correspond to anything in the source. `C-40`: if the attributes were renamed, the whole ban becomes a
loop over three names no method reads — **satisfied on every method, forever, green**. It would then be
a regression PIN with a dead subject, not a gate, and nothing would say so.

**Where.** `tests/test_search.py:615`; both consumers at `:677-682` and `:689-690`.

**Why it matters.** The increment closed the hand-list on the *method* axis and left the identical
`C-31` shape on the *attribute* axis, in the same predicate. A rename would be caught collaterally by
the fold/pan arms in other files — which is why this is MEDIUM, not HIGH — but a **newly added**
viewport dimension would be covered by nothing at all, and that is precisely how A-6 has re-opened
four times.

**Suggested fix — one line**, after `tests/test_search.py:615`. `_view_state` is the renderer's
parameter builder and is the natural source of truth:

```python
# Non-vacuity for the BAN'S OWN VOCABULARY.  A renamed or removed viewport
# attribute would leave this tuple naming nothing, and every leak assertion
# below would pass on every method forever.
assert set(VIEWPORT) <= _map_screen_self_reads()["_view_state"], VIEWPORT
```

Verified on the shipped tree: `_view_state` reads `['folded', 'pan_x', 'pan_y']`, so it passes today.

---

### F-E — the flattening table duplicates `darkside.PRESERVED_CODE_POINTS` and the arm asserts a SUBSET, so growth there silently reopens S1  [Severity: LOW]

**What.** `mapper/app.py:1874` hand-writes `{0x0A: " ", 0x09: " "}`. The authoritative set is
`darkside.PRESERVED_CODE_POINTS` (`mapper/darkside.py:370`), and the arm's control asserts
`{LF, TAB} <= set(darkside.PRESERVED_CODE_POINTS)` at `tests/test_search.py:1024` — a **subset**, so
adding a third preserved code point (U+000D and U+2028 are the obvious candidates; the darkside comment
at `:379-384` records that both were previously mis-classified) leaves the translate table short and
`test_the_query_echo_bounds_rows_and_not_only_cells` green.

I verified the coverage is **exact today**: `PRESERVED_CODE_POINTS = frozenset({0x0009, 0x000A})`, and
`COERCION_RANGES` sweeps all remaining Cc/Cf/Zl/Zp, so no other code point can reach the echo as a row
break. The S1 fix is correct as shipped.

**Suggested fix — either half is enough.** Derive the table:
`self.query_text.translate({cp: " " for cp in darkside.PRESERVED_CODE_POINTS})`; **or** tighten
`tests/test_search.py:1024` from `<=` to `==` so growth reddens by name.

---

### F-F — R2.1's non-vacuity claim overstates what the code does  [Severity: LOW]

R2.1 states: *"Non-vacuity is derived too, and deliberately not a second hand-list."* Half of that is
right and half is not. The transitive receipt at `tests/test_search.py:675`
(`reaching - {"_count_line"} - reads_by_method["_count_line"]` non-empty) **is** derived and is a good
instrument. But `:673-674` — `len(reaching) >= 6` and
`{"_search_index", "_suspended_count_line"} <= reaching` — is a two-name pin plus a magic floor.

That is **correct practice**: a non-vacuity anchor has to be pinned or it is circular, and the choice of
`_search_index` (an owner a re-routing mutant preserves) is well reasoned. The record should just say so
rather than claim the anchor is derived. The floor of `6` will also redden spuriously if the chain is
legitimately shortened; consider anchoring on the named pair alone.

---

## Closures I confirm — each with the arm that reddened

Every mutation was constructed by me from the diff, applied to the mirror only, and sha256-restored.
Verdicts are **per resolved arm**, not per process exit code.

| Arm | Operation | Verdict | Reddened (per-arm) |
|---|---|---|---|
| **MUT-1** | a viewport read added to `_query_echo` — one of the three the round-1 hand-list missed | **KILLED** | `test_the_count_and_the_paint_share_one_resolution` (`:679`) |
| **MUT-4** | R2-E regression: the separator mapped to nothing instead of to a space | **KILLED** | `test_the_query_echo_bounds_rows_and_not_only_cells` (`:1062`) |
| **MUT-5** | R2-G regression: the region declines to declare for queries of ≤3 characters | **KILLED** | `test_above_the_bound_the_count_line_declares_the_search` (`:922`) |
| **MUT-6** | S1: the row flattening removed, coercion and cap kept | **KILLED** | `…bounds_rows_and_not_only_cells` (`:1041`) **and** `test_a_line_bearing_query_does_not_take_the_frame` (`:2290`) |
| **MUT-7** | H2: `fit` replaced by an equivalent-length raw slice | **KILLED** | `test_the_query_echo_coerces_the_operators_text` (`:980`) |
| **MUT-2** | H1: fold-narrowing moved into a module-level helper | **SURVIVED** | — (853 passed) → **F H1-R** |
| **MUT-8** | the echo truncates at the first coerced code point | **SURVIVED** | — (36 passed) → **F-B** |

Notes on the five that closed:

- **H2 is genuinely gated (MUT-7).** The control at `tests/test_search.py:974-976` — asserting the raw
  slice *would* have carried all five through before any absence is read — is the right shape and it
  does discriminate deletion-of-the-whole-echo. Its residual weakness is F-B, not the control itself.
- **S1/S1b is asserted LOCALLY, at the right sink, and both halves are real (MUT-6).** The flattening
  sits in `_query_echo` (`mapper/app.py:1873-1875`) and not in `darkside.plain`, which I verified is
  untouched (`PRESERVED_CODE_POINTS` still `{0x09, 0x0A}` at `mapper/darkside.py:370`), so the surfaces
  whose layout reads U+000A/U+0009 are unaffected. `textual==8.2.8` is pinned exactly at
  `pyproject.toml:11` — **I confirmed the pin myself** — and the arm's docstring is right that a pin is
  not a guarantee. The split into a sink arm and a composited-frame arm is justified and both reddened
  under MUT-6: the frame arm's `bad_height <= height + 1` at `:2290` is a **relative** bound against the
  ordinary query at the same size, which is the correct instrument (a constant ceiling would pass on an
  implementation that always wrapped).
- **R2-E is closed (MUT-4).** `tests/test_search.py:1060-1062` pins the separator directly; deleting it
  instead of spacing it reddens by name.
- **R2-G is closed (MUT-5), and the count IS checked against the owner.** The loop at `:917-926` runs
  `("z", "ze", "zet")`, asserts each is non-vacuous (`short_expected` truthy, `:920`) and compares the
  painted numeral against `len(SearchIndex(graph).query(short))` at `:926` — the *ordered* form, so the
  cheap `hits` path the product takes is checked against the expensive one and not against itself. That
  is the right oracle. `LLR-N07.3.3`'s line is `blank`, and `_count_line`'s guard at
  `mapper/app.py:1972` is `not self.query_text.strip()`, which matches the requirement exactly.
- **`_search_hits`'s exclusion from the closure is sound** — see F-D. Correct reasoning, weaker regime.

### Also reviewed — clean

- **The derivation is genuinely derived, and I reproduced R2.1's transcript independently:** 93 methods
  parsed, 8 in the closure, 0 leaks, `_query_echo` / `_seat_glyph` / `_seat_row` genuinely present.
  R2.1's numbers are accurate.
- **`_query_echo` is one expression and reads nothing it should not** (`mapper/app.py:1873-1875`). The
  docstring's corrected bound claim (cells vs rows, `:1811-1824`) and the "this number is not stable"
  correction on the swept widths (`:1848-1865`) are both honest and are the right response to three
  disagreeing measurements. No over-engineering: `translate` at the sink is the minimum edit.
- **The M1 comment correction at `mapper/app.py:1990-1994`** now says "necessary but not sufficient" and
  attributes the collapse to two independent causes, which matches the measured control.
- **Simplicity.** Three helpers, each single-purpose. `_search_index` is a real consolidation
  (one construction site, censused at `tests/test_search.py:729-737`). Nothing speculative added in
  round 2 — the fixes are one `translate`, one closure, three arms and two assertion blocks.
- **Ledger arithmetic checks out.** 850 → 853 = the three new arms; the two gap fixes added assertions
  to existing arms, so they move no count. I measured 853 on the mirror.
- **Convention conformance.** Docstrings carry the file's house style (measured claims, named mutants,
  stated departures). Hostile code points are built from their numbers throughout
  (`tests/test_search.py:935`, `:1033`, `:2254`) and never spelled — the increment record holds that
  line too.
- **The evidence-integrity disclosure in R2.8 is the right call** and I take it at face value; the
  digest-mismatch mechanism the author describes (`4c59b051…` appearing as a baseline) is internally
  consistent, and none of the discarded verdicts appears in the document.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix the HIGH finding before advancing**

**BLOCK on H1-R.** Round-1 F1's own sentence is still true on the shipped tree: a new link in the count
chain evades the ban and the entire suite, and the region paints 4501 over a graph holding 6001 with
`853 passed` on the lane. The fix is one insertion in `tests/test_search.py`, proven clean on the
shipped tree and proven to kill the mutant by name; fold F-D's extra seed into the same edit.

F-B and F-C are cheap one-line assertions I would want in the same commit — F-B in particular, because
its mutant is reachable through the real paste path. F-E and F-F are a constant and a sentence.

**Nothing in shipped behaviour needs to change.** `mapper/app.py` is correct as it stands; every
finding here is about what the suite would let a later reader do to it.

**What is genuinely good in round 2:** the derivation is real work and it closed the exact mutant that
walked through round 1; the H2 arm carries its own mutant as a control, which is the right shape and
rare; splitting the S1 gating into a sink arm and a composited-frame arm was correct and both halves
redden; and the two survivors the author found himself (R2-E, R2-G) were found by aiming at machinery
he believed was strong, which is the discipline working. The calibration now reads **six for six** —
this pass's two survivors also sat between the arms the battery fired.

---

## Evidence checklist

- [x] **Diff read in full** — `git diff 9ba2f26 -- mapper/app.py tests/test_search.py`, +946/−149.
  Shipped source read at `mapper/app.py:1759-2002` and `:2183-2212`; `tests/test_search.py:534-760`,
  `:809-1063`, `:1238-1310`, `:2138-2300`. `mapper/darkside.py:370-403` and `pyproject.toml:11` read as
  dependencies of the S1 claim.
- [x] **Correctness pass** — blank-query guard (`mapper/app.py:1972`) checked against `LLR-N07.3.3`;
  `_search_order() is None` branch traced into `_suspended_count_line`; the coercion sink's code-point
  coverage checked exhaustively against `PRESERVED_CODE_POINTS` ∪ `COERCION_RANGES`. No error path
  found that the diff opens and leaves unhandled.
- [x] **Simplicity pass** — no premature abstraction in round 2; the three added arms each carry a
  stated reason and a constructed control.
- [x] **Reuse / duplication checked** — one `SearchIndex` site; the closure algorithm is reused from
  `_map_screen_self_reads` rather than re-written (correct); **F-E** is the one duplication found (the
  flattening table against `darkside.PRESERVED_CODE_POINTS`).
- [x] **Tests reviewed for intent** — 5 declared closures independently re-fired (all KILLED, per-arm
  verdicts above); **2 new mutants written, both SURVIVED** (MUT-2 on the full lane, MUT-8 on the
  owning file).
- [x] **Verdict explicit** — BLOCK, one HIGH, with a proven minimal fix.
- [x] **Real repo unmutated** — sha256 and `git status` identical before and after; all work in a
  scratchpad mirror verified byte-identical across 236 tracked files.
- [x] **No hostile code point spelled verbatim** — all named `U+XXXX`; mutations described by position
  and operation.

### What I could NOT verify

1. **MUT-8 was fired against `tests/test_search.py` only (36 arms), not the full 853-arm lane.** The
   coercion property is owned entirely by that file, but I state the scope rather than implying a lane
   result I did not take.
2. **The `all markers` lane (`870 passed, 3 xfailed`) and the ruff SET comparison** I did not re-run;
   I reproduced the default lane exactly, which is the lane every mutation verdict here rests on.
3. **The round-2 battery's own applied digests** (`5f10f790…`, `58a34e37…`, etc.) cannot be verified
   from outside. I re-derived five of the seven arms' *verdicts* independently instead, which is the
   check that matters, and all five agreed with the author's table.
4. **R2.8's two contaminated concurrent runs.** I can confirm the exit digests match the tree I
   reviewed and that this tree reproduces `853/17/3`. The declaration is consistent with everything I
   can measure; I cannot audit it from outside.
5. **Predicate 1 in the real frame above the genuine bound.** I did not re-measure the 12002-node
   collapse; I accept the concurring round-1 F4 and security F-2/F-3 findings and the R2.5 bookkeeping
   (`Inc-STRIPS` as a blocker on closing `LLR-N07.3.4`). That call is correct and unchanged by this
   pass.
6. **Spanish copy** — still unreviewed by a native-speaking operator, carried as R5.
7. **Whether the CRLF-converted mirrors used in round 1 affected any non-`app.py` claim.** I did not
   re-run those reviews; I recorded the trap and the measurement that proves it.
