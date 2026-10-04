# Increment W1 — the boundary generalised, and the last hand-spelled DOMAIN and TITLE removed

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Increment:** `Inc-W1` · **Branch:** `feat/ui-next-batch-02`
**Entry commit:** `6aee286` (Inc-5 close), tree clean at entry · **SOURCE FILE COUNT: 0** — tests only.
**Protocol:** lighter lane (tests-only, zero source files) **plus one confirmation scoped to the design call**, per coordinator ruling 2026-09-10.
**Language:** English (engineering artifact).

---

## BLUF

`W1` is closed. The `B-55` boundary now covers **every** member of the domain rather than `root`
alone, and the fixture's titles are **derived from `_graph()`** rather than spelled a second time.

```
default lane : 904 passed, 17 deselected, 3 xfailed   exit 0
all markers  : 921 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27, zero NEW, zero GONE
arms         : 50, zero skipped        (unchanged -- an arm body, no new arm)
battery      : 56 fired = 2 kinds x 4 members x 7 sites; 42 KILLED, 14 proven equivalent
source files : 0
```

**Ledger unchanged** (`904`/`921`), census pin unchanged (`59`), `git status -- mapper/` empty.

## 1 · What `W1` was

Inc-5's oracle derived its domain at **w=120**, while the sibling arms backstopping `first` and `hit`
run at **w=80**. The `B-55` boundary re-externalised the derivation for **`root` alone**. So a drop of
`first` or `hit` that bit only at w ≥ 100 fell out of `hittable`, left the floor satisfied at 3, never
touched the boundary — and the unions then quantified over a domain the defect had already emptied.

Measured by the pass that found it, at `radial.py:232`: both shapes survived all 50 arms **and the
entire 904-arm default lane**, both proven non-equivalent by digest.

## 2 · The fix — two changes, one of them the coordinator's ruling

**(a) The boundary covers every member.** `for m in ALL: assert (m in hittable) == (TITLES[m] in drawn)`.
Every member the derivation can drop is now re-externalised against what the renderer actually draws,
so there is no member whose only guard sits at a different width from the derivation.

**(b) `TITLES` is DERIVED from the fixture, not spelled.** Per coordinator ruling: *no hand-maintained spelling of the fixture's DOMAIN or TITLES survives* -- hand-spelled node IDS remain and are legitimate, since they drive a specific input, which this file's own rule permits. The property achieved is narrower than the round-1 wording, and saying so is the sixth exhibit's whole point. Superseded wording: *no hand-maintained
spelling survives this batch.* The reasoning is Inc-5's own five rounds — every one of its four blocks
was a hand-named thing drifting from a derived truth (a named member, a named member list, a named
cardinality, a named domain). A second spelling of the fixture's titles is that shape at generation
six. So:

```
fixture = _graph()
TITLES = {m: fixture.nodes[m].ficha.title for m in ALL}
```

### 2.1 · Where the instrument boundary lies — stated in the docstring, because it is a real question

Deriving `TITLES` makes the oracle read the fixture. That is worth naming rather than glossing:

- **Deriving the DOMAIN from the fixture is legal.** The fixture is this test's own input, authored in
  this module. It is not the artifact under verification, and asking "what did I put in?" is not
  circular.
- **The ASSERTION about what got painted must stay an independent instrument.** `HIT_STYLE` is pinned
  in this module and is **never** imported from a renderer; the spans are read out of rendered output
  and compared against that pin.

The line, in the docstring's own words: **a test may say what it asked for; it may not let the thing
under test tell it what the answer was.** Had `TITLES` been read from a renderer's output, that would
be the reader-as-oracle defect — and it is not what this does.

## 3 · The battery — both quantifiers, per site

`W1` needs **two** quantifiers to become live: a member and a width band. A flat mutant dies to a
sibling arm at w=80; a width-conditioned one slipped between the derivation and those siblings. So the
battery fires **both kinds, all four members, all seven sites**.

```
                     S1   S2   S3   S4   S5   S6   S7
  FLAT drop root      K    K    S    S    S    S    K
  FLAT drop first     K    K    K    K    S    K    K
  FLAT drop hit       K    K    K    S    K    K    K
  FLAT drop other     K    K    K    S    K    K    K
  WIDE drop root      K    K    S    S    S    S    K
  WIDE drop first     K    K    K    K    S    K    K     <- S2 was the W1 survivor
  WIDE drop hit       K    K    K    S    K    K    K     <- S2 was the W1 survivor
  WIDE drop other     K    K    K    S    K    K    K

  56 fired · 42 KILLED · 14 survivors
```

**`WIDE drop first` and `WIDE drop hit` at `S2 radial.py:232` are KILLED** — the two shapes that
survived everything before this increment.

**All 14 survivors proven EQUIVALENT**, by output digest over **864 renders each** (6 renderers × 16
subsets × 3 widths × 3 selections), with a positive control per site that **must** differ — and all
four fired:

```
SHIPPED   c231ba3f3d6d0e12
  FLAT/WIDE drop root   at S3, S4, S5, S6   EQUIVALENT   (lane family never draws the root)
  FLAT/WIDE drop first  at S5               EQUIVALENT   (label path is branches[1:]; first is the trunk)
  FLAT/WIDE drop hit    at S4               EQUIVALENT   (trunk path is branches[0] only)
  FLAT/WIDE drop other  at S4               EQUIVALENT   (same)
  ctrl MAX at S3/S4/S5/S6                   DIFFERS      <- all four controls fire
```

The digest's widths span the mutants' own 100-column boundary, so a width-conditioned mutant that DID
change behaviour could not hide inside it.

The 7 structural cases are `B-55` and the rail's trunk/label split holding exactly where they are
true — **measured per site**, never asserted per family, which is this batch's own mis-route lesson
applied to itself.

## 4 · Gate checklist

- [x] **Tests / lint pass** — `904 passed, 17 deselected, 3 xfailed` exit 0; `921 passed, 3 xfailed` all markers; ruff SET-identical, 27 = 27. One complete run each, tree sha256-pinned before and after.
- [x] **The defect this increment exists to close is KILLED** — both `W1` survivors at `radial.py:232`, §3.
- [x] **Every predicate demonstrated able to go RED** — 56 fired, 42 KILLED, 14 proven equivalent with controls that fire.
- [x] **Derived, not named** — the domain AND the titles, §2 and §6. ⚠ This box was checked FALSELY in round 1 and the review caught it: the titles were derived and the DOMAIN was not. Now true.
- [x] **Instrument boundary declared** — §2.1, and in the test's own docstring.
- [x] **Zero source files** — `git status -- mapper/` empty; `A-91`'s source verdicts inherit unchanged.
- [x] **Arm count and census pin unmoved** — 50 arms, pin 59; the fix replaced an arm body.
- [x] **No destructive commands** — every mutant restored from original bytes, sha256-asserted, `__pycache__` purged, `PYTHONDONTWRITEBYTECODE=1`.
- [x] **Confirmation on the design call** — returned **BLOCK, 1 HIGH**. Folded in §6. The `TITLES` derivation was confirmed **sound, not circular**.

## 5 · Carries

- `Inc-B55` and `Inc-STRIPS` unchanged in the cut; `LLR-N07.3.4` still OPEN, blocked on Inc-STRIPS.
- `F7` (a selected node that is also a hit is indistinguishable from a selected non-hit) still routed
  to `ux-reviewer`, still not fixed.
- A hit on the map **root** remains declared-but-unpaintable in the three lane renderers. That is
  `B-55` proper, it is pre-existing, and this increment now **asserts** it rather than assuming it —
  so if a lane renderer ever starts drawing the root, the boundary reddens instead of quietly widening.

## 6 · Round 2 — the confirmation, and the sixth generation of one defect

**The confirmation returned `BLOCK — 1 HIGH`, and it was right about the thing that matters most:
a gate box I had checked for a property the code did not have.**

It also confirmed the two claims the increment rests on, each proven rather than accepted:

- **The `TITLES` derivation is SOUND, not circular.** Traced: `_graph()` is authored in this module,
  reaches product code only through `mapper.model`, and `Graph.add_node` is verbatim storage into a
  plain dict with `Ficha` a plain dataclass carrying no `__post_init__`. **`mapper.views.*` — the
  artifact under verification — is nowhere on that read path.** `TITLES[m]` supplies only the KEY;
  both sides of the assertion are read out of rendered output.
- **`W1` is genuinely closed**, by the decisive control I had not thought to run: the same mutant
  fired against BOTH oracles. `WIDE drop first` and `WIDE drop hit` at `radial.py:232` are
  **SURVIVED against the pre-increment tree** and **KILLED against Inc-W1**, each by exactly one node
  id — the generalised boundary. That proves the arm *newly gained* the ability to see it, which is a
  stronger claim than "it is killed now".

### 6.1 · `F1` (HIGH) — I derived the titles and left the DOMAIN spelled

`ALL = ("root", "first", "hit", "other")` sat **seven lines below** a comment reading *"THE DOMAIN AND
THE TITLES BOTH COME FROM THE FIXTURE, spelled nowhere"*, under an increment titled *"the last
hand-spelled thing removed"*, with a checked `[x]` gate box asserting it.

**The drift it left is asymmetric, and the silent half is the dangerous half.** A *rename* in
`_graph()` is loud — `KeyError`. An *addition* is silent: a fifth node stays outside `ALL`, therefore
outside the domain, the boundary and the unions. **That is `W1`'s own failure mode — a member the
derivation never sees — reinstated one level up, inside the increment written to end it.** Sixth
generation of the same defect: named member → named list → named cardinality → named domain → the
width the domain is derived at → **the domain's own membership**.

**Fixed:** `ALL = tuple(fixture.nodes)`. Verified: `('root', 'first', 'hit', 'other')`, identical
members and order; 50 arms green; both `W1` mutants still KILLED.

### 6.2 · `F2` (MEDIUM) — generalising the boundary spent the whole clip margin

`TITLES[m] in drawn` is a substring test, and moving from `root` alone to every member moved the
binding case from `root`'s 13-cell title to the fixture's **longest**, 18. (An earlier wording said *"from the SHORTEST title"* -- FALSE: the shortest is `other`'s 10-cell title, which was never binding, and it sat in a block whose other three numbers were exact.) Measured at w=120: `RadialRenderer`
slices to 18 cells, the longest fixture title is 18 — **margin zero**. A 19-character title would make
this arm accuse that renderer of a `B-55` violation it did not commit, and deriving `TITLES` was
adopted precisely to make fixture edits safe.

**Fixed by splitting the equivalence into its two directions**, each with the message its own
direction warrants: a painted member whose title does not survive the clip now reports *"this arm has
stopped measuring the paint and is measuring the clip — shorten the fixture title, do not blame the
renderer"*. Same shape as this file's existing clip precondition, whose assertion is at `:192`.

### 6.3 · `F3` (MEDIUM) — DECLARED as a carry, deliberately not fixed

The boundary is an **equivalence**, so `False == False` satisfies it: a mutant that stops **drawing** a
member as well as **painting** it passes rather than reddening. Measured — a co-drop at
`radial.py:221` under the same width condition **survives the 50 arms and the entire 904-arm default
lane** — and it is not equivalent, it makes `RadialRenderer` draw an empty title.

**Not fixed here, and that is a scope judgement rather than an omission.** The class is *drawing*, not
*hit-painting*: `LLR-N07.2.2b` is about painting hits distinguishably, and widening this arm to police
what each renderer draws would pull a different requirement into a tests-only micro-increment. The
structural statement is worth recording: **the boundary is only as strong as the independent pinning
of `drawn`, and exactly one of four members has its drawn-ness pinned** (`other`, at `:192`).
**Routed to `qa-reviewer`.**

### 6.4 · `F4` / `F5` (LOW) — fixed in the same edit

`title = "Cronograma"` at `:183` became `_graph().nodes["other"].ficha.title` — a hand-spelled title
surviving one arm above the one that removed hand-spelled titles. And the arm's docstring said
*"subsets of size 2 and 3"* where the code is `range(2, len(hittable)+1)`, which reaches **4** on the
three renderers that draw the root; corrected to say what it does.

### 6.5 · An instrument failure in the REVIEWER's own harness, recorded because it is the batch's lesson

The reviewer's first digest run passed a POSIX path to a Windows interpreter, so every invocation
returned the same error string, every mutant compared equal, and it printed a clean sweep of
`EQUIVALENT` — **false survivals across the board**. **The positive controls caught it**: four rows
that must differ, didn't. Same class as an anchor matching zero times, and the reason this batch
requires a control that must fire rather than a comparison that merely agrees.

### 6.6 · Post-fix evidence

```
default lane : 904 passed, 17 deselected, 3 xfailed   exit 0
all markers  : 921 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27, zero NEW, zero GONE
arms         : 50, zero skipped
battery      : 56 fired, 42 KILLED, 14 proven equivalent -- unchanged by the fixes
source files : 0
```

- [ ] **Second confirmation** — NOT dispatched. A HIGH is never self-cleared, and the coordinator
      authorised **one** confirmation for this tests-only increment. Held for the coordinator.

## 7 · Round 3 — the declaration audit

Scoped by coordinator ruling to one question: **does every declaration match what the code derives?**
It returned **BLOCK, 1 HIGH**, and the HIGH was **in the code round 2 introduced** — which is the
honest outcome of pointing a reader at declarations rather than at mechanism.

**The round-1 HIGH is confirmed closed.** `ALL = tuple(fixture.nodes)` derives to
`('root','first','hit','other')` — identical members *and order* to the tuple it replaced — so
*"the domain and the titles both come from the fixture, spelled nowhere"* is now true.

### 7.1 · `F1` (HIGH) — a message that exculpated the renderer unconditionally

`F2`'s two-direction split gave the `if` branch the message *"shorten the fixture title, **do not blame
the renderer**"*. **Two** conditions reach that branch: a fixture title grew (message right), or **a
renderer's clip tightened** (message wrong — and that is a real `B-55` violation).

**Proven with one renderer-side mutant**, which fired this assertion *and* the clip precondition in the
same run, blaming opposite parties for one cause. And the advice was **actionable in the wrong
direction**: shortening the fixture titles greens both arms *while the defect ships* — a documented
red-to-green-with-defect path, authored inside the increment whose subject is `B-55`.

**Fixed.** The message no longer picks a culprit, because the condition does not identify one. Verified
under the same mutant — the two messages now agree, and the new one says explicitly that shortening the
title would **hide** a renderer-side clip:

```
E  ... no longer draws the third branch at 120 columns ... See B-55: a clipped hit is an UNDECLARED hit
E  ... paints a root hit but the fixture's title 'Raiz del mapa' does not survive this renderer's clip
   whole ... TWO CAUSES, needing OPPOSITE fixes: if the FIXTURE title grew, shorten it -- if this
   RENDERER's clip tightened, that is a B-55 violation ... and shortening the title would HIDE it
```

### 7.2 · `F2` / `F3` / `F4` / `F5` — four more declarations that outran the code

- **`F2`** *"moved the binding case from the SHORTEST title to the longest"* — **false**. Under the
  `root`-only boundary the only title checked was `root`'s, at 13 cells; the shortest is `other`'s 10,
  which was never binding. It sat in a block whose other three numbers I had measured exactly, and
  **one false number among true ones is what teaches a reader to stop checking**. Corrected.
- **`F3`** *"survived on SEVEN of seven renderers"* — the derived set is **six**; seven is the mutant
  **site** count (the rail carries two). The file pins six in three other places, so this made it
  disagree with itself about the quantity every arm is parametrised over. Corrected.
- **`F4`** the clip precondition's assertion is at `:192`, not `:190` (`:190` is inside its comment).
  The §6.3 *claim* was verified true; only the citation drifted. Corrected.
- **`F5`** *"the last hand-spelled thing removed"* claims more territory than the fix took. Hand-spelled
  node **ids** remain and are legitimate — they drive inputs, which this file's own rule permits. Title
  and §2(b) narrowed to `DOMAIN and TITLE`.

### 7.3 · Out of axis — reported, NOT fixed, per the terminal boundary

- **`O1`** one duplicated render call (`drawn` / `none` are the same `_spans_at(cls, 120, set())`), and
  the same shape at `:184`/`:197`. Simplicity nit, no correctness effect.
- **`O2`** the co-drop gap is confirmed real and **already routed** to `qa-reviewer`. The reviewer adds
  the connection worth carrying: `F1` and the co-drop **share a root** — three of four members have no
  independent pin on `drawn`.
- **`O3`** an instrument failure in the reviewer's **own** harness: a CRLF-blind anchor matched **zero**
  times and printed a clean `50 passed`, which reads as *"the mutants survive"*. Caught only by the
  match-count assert. That is §6.5's lesson recurring one round later in a different harness, and it is
  the third time in this batch that **a control which must fire** was the only thing standing between a
  reviewer and a false all-green.

### 7.4 · Post-fix evidence

```
default lane : 904 passed, 17 deselected, 3 xfailed   exit 0
all markers  : 921 passed, 3 xfailed                  exit 0
ruff SET     : 27 = 27, zero NEW, zero GONE
arms         : 50, zero skipped   |   source files: 0
battery      : 56 fired, 42 KILLED, 14 proven equivalent -- unchanged
```

**Inc-W1 closes here** per the coordinator's terminal boundary: no further cycle. The in-axis findings
are fixed; `O1`/`O2`/`O3` are recorded and routed.
