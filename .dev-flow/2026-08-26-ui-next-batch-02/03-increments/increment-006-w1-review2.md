# Confirmation 2 — Inc-W1 · declaration-vs-code

**Scope:** ONE question — does every DECLARATION in this increment match what the code derives?
Declarations = every comment, docstring sentence, assertion message, gate checkbox and packet claim
that asserts a property. Mechanism and renderers not re-audited.

**Read in full:** `tests/test_views_hits.py` (1-420), `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-006-w1.md` (1-221).

**Verdict: BLOCK — 1 HIGH.**

The domain finding from round 1 is genuinely closed. The HIGH is **new**, and it is in the code the
round-1 fix introduced: `F2`'s two-direction split gave the `if` branch a message that **asserts a
diagnosis its reaching condition does not entail**, and that message **contradicts this same file's
`:192` message about the same observable**. Both fire in one run — measured below.

---

## Sole-writer discipline

Four mutants applied to `mapper/views/radial.py`, each restored from original bytes.
Post-run sha256, all four pins re-asserted identical:

```
tests/test_views_hits.py  21c34f19a9d670461e478f28c2db9ce00a7c284e8dc306fb8854b9f95925b56b  OK
mapper/views/outline.py   06a0e9493f10bbc392bf4e175ee737f3ca1ef95cf10b996de139de7105325b39  OK
mapper/views/radial.py    aa462076e911c3983c4a02589094fbadd150fcfb6f1dab8d740b6fd7420f6d85  OK
mapper/views/lane.py      098b90b4baad538e9fda51be662a52f9354781e85085496153119d289ee602ef  OK
git status --porcelain -- mapper/   (empty)
```

`PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`, `--color=no`, `-p no:cacheprovider`, `__pycache__` purged.
Every mutant asserted its anchor matched **exactly once** before writing (see `O3`).

## Cross-check of the packet's figures — one run of my own

| claim | measured | |
|---|---|---|
| `904 passed, 17 deselected, 3 xfailed` | `904 passed, 17 deselected, 3 xfailed` in 206.67s | OK |
| `921 passed, 3 xfailed` (all markers) | `921 passed, 3 xfailed` in 233.15s | OK |
| ruff SET 27 = 27, `--isolated`, inside repo | `Found 27 errors`; **none** in `tests/test_views_hits.py` — the only touched file contributes zero, so the set cannot have moved | OK |
| 50 arms, zero skipped | `50 passed in 0.40s`, no skip line | OK |
| `git status -- mapper/` empty | empty | OK |
| census pin 59 | `tests/test_a3_census.py:191` `assert len(sites["argful"]) == 59` | OK |
| battery arithmetic `2x4x7 = 56`, `42 K / 14 S` | table sums to 42 K, 14 S; digest `6x16x3x3 = 864` | OK |

**Mechanism, re-verified because it was cheap** (0.4s per arm-file run). `WIDE drop first` and
`WIDE drop hit` at `radial.py:232` are **KILLED, each by exactly one node id**:

```
WIDE drop first -> FAILED ...EVERY_member_of_the_hit_set_is_painted[radial.RadialRenderer]   1 failed, 49 passed
WIDE drop hit   -> FAILED ...EVERY_member_of_the_hit_set_is_painted[radial.RadialRenderer]   1 failed, 49 passed
WIDE drop other -> 2 failed (also the :192 arm)      WIDE drop root -> 1 failed (same node id)
unmutated control -> 50 passed
```

## Measurements behind the declarations

Derived at w=120 over the 6-renderer derived set:

```
ALL = ('root', 'first', 'hit', 'other')          <- identical members and order to the removed tuple
TITLES  root 'Raiz del mapa' 13 | first 'Presupuesto' 11 | hit 'analisis de riesgo' 18 | other 'Cronograma' 10

HybridLaneRenderer    hittable=(first,hit,other)        root:0  first:1  hit:1  other:1     k=[2,3]
LaneRenderer          hittable=(first,hit,other)        root:0  first:1  hit:1  other:1     k=[2,3]
RailTimelineRenderer  hittable=(first,hit,other)        root:0  first:13 hit:28 other:20    k=[2,3]
LayeredRenderer       hittable=(root,first,hit,other)   root:20 ...                          k=[2,3,4]
OutlineRenderer       hittable=(root,first,hit,other)   root:1  ...                          k=[2,3,4]
RadialRenderer        hittable=(root,first,hit,other)   root:13 first:11 hit:18 other:10     k=[2,3,4]
```

---

## Findings

### F1 — the `if`-branch B-55 message asserts a diagnosis its reaching condition does not entail, and contradicts `:192` [Severity: HIGH]

- **What:** `:339-344` fails with *"shorten the fixture title, **do not blame the renderer**"*. Two
  distinct conditions reach that branch: (a) a fixture title grew past the clip — the case §6.2 was
  written for, message correct; (b) **a renderer's own clip tightened, or it stopped drawing a title it
  still paints** — message wrong, and that is a real `B-55` regression. The comment above it is careful
  (`:325-326`, "one of them *can* fire for a reason that is not the renderer's fault"); the message
  itself is not — it exculpates unconditionally.
- **Where:** `C:\Users\jjgh8\Github\mapper\tests\test_views_hits.py:339-344`; declared in packet §6.2.
- **Proven, not argued.** One mutant, `radial.py:221` slice `[:18] -> [:6]` (a renderer-side change,
  no fixture edit), produces **both messages in the same run**, blaming opposite parties for one cause:

```
E  AssertionError: RadialRenderer no longer draws the third branch at 120 columns, so this arm has
   stopped measuring the paint and is measuring the clip. See B-55: a clipped hit is an UNDECLARED hit
E  AssertionError: RadialRenderer paints a root hit but the fixture's title 'Raiz del mapa' does not
   survive this renderer's clip whole; this arm has stopped measuring the paint and is measuring the
   clip -- shorten the fixture title, do not blame the renderer
```

- **Why it matters:** the file's own `:195` declares this observable a violation — *"a clipped hit is
  an UNDECLARED hit"*. The new message declares the opposite and **prescribes a remedy that restores
  green while the defect ships**: shortening the fixture titles greens `:339` *and* `:192`, because
  both test the same substring. That is a documented red-to-green-with-defect path, authored inside
  the increment whose subject is `B-55`. It is also the batch's rule-7 shape — two declarations about
  one observable, averaged rather than reconciled.
- **Suggested fix** — keep the two directions, stop assigning blame in the one that is ambiguous:

```python
            assert TITLES[m] in drawn, (
                f"{cls.__name__} paints a {m} hit but the fixture's title "
                f"{TITLES[m]!r} does not survive this renderer's clip whole; this arm has "
                "stopped measuring the paint and is measuring the clip. TWO CAUSES, and they "
                "need opposite fixes: if the FIXTURE title grew, shorten it -- if this "
                "RENDERER's clip tightened, that is a B-55 violation (a clipped hit is an "
                "UNDECLARED hit, see :192) and shortening the title would hide it"
            )
```

  and delete the now-false half of the comment at `:334-335` (*"a fixture edit must not be able to
  produce a message that blames the code"* is fine; the message must not exculpate the code either).

### F2 — "the SHORTEST title" is false of the fixture [Severity: MEDIUM]

- **What:** *"generalising this boundary from `root` alone to EVERY member moved the binding case from
  the **SHORTEST** title to the LONGEST"*. Under the `root`-only boundary the only title checked was
  `root`'s, **'Raiz del mapa' = 13**. The shortest fixture title is **'Cronograma' = 10** (`other`),
  which was never the binding case. Measured above.
- **Where:** `tests\test_views_hits.py:327-329`; same sentence in packet §6.2 (line 168-170).
- **Why it matters:** it is presented as a measured fact inside the comment whose other measured facts
  I confirmed exactly (`RadialRenderer` slices to 18 at `radial.py:221`; longest title 18; margin
  zero — all three true). One false number in a block of true ones is what teaches a later reader to
  stop checking.
- **Suggested fix:** `moved the binding case from `root`'s 13-cell title to the fixture's LONGEST, 18.`

### F3 — "SEVEN of seven renderers"; the derived set is SIX [Severity: MEDIUM]

- **What:** *"that shape survived on SEVEN of seven renderers and across a 199-arm run."* The derived
  renderer set is **6** (measured). Seven is the mutant **SITE** count — packet §3's `S1..S7` over six
  renderers, `RailTimelineRenderer` carrying two sites (`S4` trunk / `S5` label, per §3's own
  equivalence notes).
- **Where:** `tests\test_views_hits.py:246-247`.
- **Why it matters:** this file pins the renderer count three other ways — `:103` `len(classes) >= 6`,
  `:113` *"RED on five of six"*, `:394` *"The six call sites"*. A fourth statement saying seven makes
  the file disagree with itself about its own derived set, which is the quantity every arm is
  parametrised over.
- **Suggested fix:** `survived at SEVEN of seven mutant SITES (six renderers; the rail carries two)`.

### F4 — the clip-precondition line citation is `:190`, the assert is at `:192` [Severity: LOW]

- **Where:** packet §6.2 (*"Same shape as this file's existing clip precondition at `:190`"*) and §6.3
  (*"exactly one of four members has its drawn-ness pinned (`other`, at `:190`)"*).
- **What:** `:190` is inside the comment block; the assertion is `:192`. The §6.3 *claim* is true — I
  checked: `other`'s drawn-ness is the only one pinned independently of the hit set; the W1 boundary
  pins the other three only *relative* to `hittable`. Only the number drifts.

### F5 — "the last hand-spelled thing" / "no hand-maintained spelling survives this batch" are broader than what was done [Severity: LOW]

- **What:** hand-spelled node ids remain throughout the file: `{"hit"}` at `:118, :132, :154`,
  `{"first"}` at `:153, :220`, `["first", "hit"]` at `:365`, `nodes["other"]` at `:183`.
- **Where:** increment title (packet line 1) and §2(b) line 42-43.
- **Why it matters:** those ids are **legitimate** — they are driving inputs, and this file's own rule
  covers them (*"a test may say what it asked for"*). No hand-spelled TITLE and no hand-spelled DOMAIN
  survives, which is the property actually achieved. The declaration simply claims more territory than
  the fix took, and the sixth-generation lesson is precisely about claims outrunning code.
- **Suggested fix:** title it *"the last hand-spelled DOMAIN and TITLE removed"*; narrow §2(b) to
  *"no hand-maintained spelling of the fixture's DOMAIN or TITLES survives"*.

---

## Declarations checked and found TRUE

Recorded so the coordinator can see what the BLOCK is *not* about.

- `:283-288` **"THE DOMAIN AND THE TITLES BOTH COME FROM THE FIXTURE, spelled nowhere"** vs
  `:290-291` `ALL = tuple(fixture.nodes)` / `TITLES = {...}` — **now true**. Derived `ALL` is
  `('root','first','hit','other')`, identical members **and order** to the tuple it replaced. The
  round-1 HIGH is closed.
- `:251-252` **"sizes 2..len(hittable), which is 2-4 on the renderers that draw the root and 2-3 on
  the lane family"** vs `range(2, len(hittable)+1)` — true, measured: `k=[2,3,4]` on outline/radial/
  layered, `k=[2,3]` on the three lane renderers. §6.4's correction landed.
- `:276-278` **"outline, radial and layered all DRAW the root and DO paint it (measured: 1, 13 and 20
  hit-styled spans)"** — exact match: 1 / 13 / 20.
- `:279` **"`SearchIndex.hits("raiz")` returns it"** — returns `frozenset({'root'})`.
- `:330-333` **"`RadialRenderer` slices titles to 18 cells and the longest fixture title is 18, so the
  margin is ZERO"** — `radial.py:221` `[:18]`; `'analisis de riesgo'` is 18 and renders whole. True.
  (The slice is a constant, not width-derived; "measured at w=120" is still accurate.)
- `:260-264` **soundness premise** — including *"`layered` DOES append a per-branch hit tally to a
  folded pill's text"*: `layered.py:598-599` `n_hits = len(...); tail = f" {n_hits}" if n_hits else ""`.
  True, and the caveat *"pins that, though at a different width"* is honest (that arm runs at w=80).
- `:310-315` **"Scoped to `root` alone, this boundary left `first` and `hit` guarded only by sibling
  arms that run at w=80"** — true: the three arms driving `first`/`hit` all route through `_spans`
  (w=80); the only w=120 arm touching them asserts an *equality* that a paint-drop cannot redden.
- `:317-324` **instrument boundary** — accurate as written. `HIT_STYLE` (`:36`) is built from
  `darkside`, never from a renderer; both sides of the union assertion are read out of rendered
  output; `TITLES[m]` supplies only the key. The one place the artifact under test *does* tell the
  test something — `hittable`, read off the paint at `:293` — is **declared** at `:303-308` and
  re-externalised by the boundary, and its residue is declared as `F3` in §6.3.
- `:345-349` **the `else` branch message** — describes its reaching condition correctly. Fired by
  `WIDE drop first`: `"RadialRenderer draws first but paints no first hit; a DRAWN node that is a
  declared hit must be painted -- see B-55"`. Exact.
- §4 gate box **"Every predicate demonstrated able to go RED"** — now backed for *both* boundary
  directions: the else branch by the battery's drop-member mutants, the if branch by my clip mutant.
- §6.3's structural statement, §6.5's harness postmortem, and every carry in §5 — consistent with
  what I read.

## Outside the declaration-vs-code axis

Reported precisely, **not** for fixing here.

- **O1 — one redundant render, twice.** `drawn` (`:336`) and `none` (`:351`) are the same
  `_spans_at(cls, 120, set())` call, kept as two locals; same duplication at `:184` / `:197`. No
  correctness effect, ~6 extra renders per parametrised arm. Simplicity nit only.
- **O2 — §6.3's co-drop gap is real and already declared.** I confirm the equivalence absorbs a mutant
  that stops drawing *and* painting a member. It is declared, scoped out with a reason, and routed to
  `qa-reviewer`. Not a mismatch; noted so the route is not lost. Note `F1`'s fix and this share a
  root: three of four members have no independent pin on `drawn`.
- **O3 — my own harness, and it is §6.5's lesson recurring.** My first mutant pair matched the anchor
  **zero times** — `radial.py` is CRLF and I anchored on `\n`. Both runs printed `50 passed`, which
  would have read as *"the mutants survive"* had I not asserted the match count. Same class as §6.5's
  POSIX-path-to-Windows-interpreter failure, in a different reviewer's harness, one round later. The
  control that must fire is the only reason either was caught.

---

## Evidence checklist

- [x] **Diff read in full** — `tests/test_views_hits.py:1-420` and `increment-006-w1.md:1-221`, every line.
- [x] **Correctness pass (edge / None / error paths)** — `combinations` never empty at k>=2 so
      `set().union(*...)` cannot raise; floor `>=3` is an assert not a filter; substring test has no
      title that is a substring of another in this fixture.
- [x] **Simplicity pass** — one duplication found (`O1`), no premature abstraction.
- [x] **Reuse / duplication checked** — `renderer_classes` imported not re-derived (`:47`); `TITLES`
      derived from `_graph()`; `_spans_at` remains the one render call site.
- [x] **Tests reviewed for intent** — both boundary directions driven RED by real mutants; `F1` is a
      finding about intent-encoding, not behaviour.
- [x] **Verdict explicit** — below.

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — `F1` (HIGH) must be fixed before advancing.** `F2` and `F3` are one-line corrections in
      the same edit; `F4`/`F5` are packet wording.

---

**BLOCK — HIGH count: 1.**

**(a) Not every declaration matches the code.** The round-1 domain finding is genuinely closed —
`ALL = tuple(fixture.nodes)` makes *"the domain and the titles both come from the fixture, spelled
nowhere"* true, and I verified the derived tuple is identical in members and order. Four declarations
still do not match: `tests\test_views_hits.py:339-344`, whose failure message tells the reader not to
blame the renderer in a case where the renderer **is** to blame and contradicts `:192` for the same
observable (**HIGH**, proven with one mutant that fires both messages in one run); `:327-329` and
packet §6.2, where *"the SHORTEST title"* is false — `root`'s title is 13 cells, the shortest is
`other`'s 10; `:246-247`, where *"SEVEN of seven renderers"* names a six-member derived set; and the
`:190` / `:192` citation plus the *"last hand-spelled thing"* framing, which claim more than was done.

**(b) I found three things outside the declaration-vs-code axis**, none inflated and none for fixing
here: one duplicated render call at `:336`/`:351` and `:184`/`:197`; a confirmation that §6.3's
co-drop gap is real and correctly routed to `qa-reviewer`; and an instrument failure in **my own**
harness — a CRLF-blind anchor that matched zero times and printed a clean `50 passed`, caught only by
the match-count assert, which is §6.5's lesson recurring one round later in a different harness.
