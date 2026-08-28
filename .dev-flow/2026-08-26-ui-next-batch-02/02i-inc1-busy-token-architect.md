# `02i` · ARCHITECT ruling — `#D10`'s busy token and the promoted grey

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Scope:** Inc-1 · **Lens:** architect
**Question routed:** `#D10` disposes of `mapper/app.py:879`; neither the token's NAME nor its HEX
exists anywhere in the batch docs. Rule both, or rule that no new token is created.
**Re-opens:** nothing. **Discharges:** an internal contradiction inside sealed `#D10`.

---

## BLUF

1. **The NEW-TOKEN reading governs.** The "one of the three (`SAGE`/`TEAL`/`VIOLET`)" reading is
   **dead on the batch's own normative text** — it cannot be executed without breaking
   `HLR-S06.1` (a `shall` that fixes all three jobs) and `LLR-S06.1.1` (one job per token).
   Three independent tiebreaks all land the same way. Details in §1.
2. **The busy token is `PULSE = "#ff9ecb"`.** `EIGHT_BIT` slot **218**, free. Minimum CIEDE2000
   to any declared token **24.74** (nearest is `INK`, a neutral). **The semantic floor stays
   `13.99` (`ACCENT`/`VIOLET`) — `PULSE` does not become the binding pair.** §2.
3. **The promoted grey is `ASH = "#a3a3a3"`**, slot **247**, between `INK` and `MUT` in the block. §3.
4. **No `01b` §3.5 row is owed.** The retone site lives in `RepoScreen`, not the atlas/sala views
   whose legend §3.5 is. `LLR-N16.2.1`'s derived sets are untouched. §5.
5. **Within-envelope discharge, not an A3 re-open.** §6.

Two constants, two docstring sentences, one style expression. `mapper/darkside.py` +
`mapper/app.py` only.

---

## 1 · Verdict on the contradiction

### 1.1 · The contradiction is real, and it is worse than "two readings"

Re-read at the six cited sites. All six say what was reported, verbatim:

| Site | Reading |
|---|---|
| `PDR-…-batch-02.md:571` | *"Assign the busy/in-progress job to **one of the three tokens Inc-1 is already adding** (`SAGE`/`TEAL`/`VIOLET`, LLR-S06.1.1)"* |
| `PLAN.md:531` | *"the **busy job assigned to one of the three v2 tokens** — squarely S-6's own work"* |
| `01-requirements.md:984` | the `#D10` table row, copied forward — *"one of the three tokens Inc-1 is already adding"* |
| `01-requirements.md:992` | *"**The busy job goes to a new token**; `WARN` keeps its one job."* |
| `01-requirements.md:994` | Touched symbols — *"the promoted grey token **and the busy token** … — both `NEW — created in Phase 3`"* |
| `01-requirements.md:6534` | §6.5 A-26 ledger — *"assign the **busy** job to **a new token** and retone the progress site"* |

The sharpest fact: **`:984` and `:992` are fourteen lines apart inside one LLR** (`LLR-S06.3.2`), and
they contradict each other. This is not a stale-citation problem like the `:848`→`:879` address
drift. It is a substantive fork that a Phase-3 implementer cannot resolve by reading harder.

### 1.2 · Three tiebreaks, all pointing the same way

**Tiebreak 1 — the "one of the three" reading is not executable.** `HLR-S06.1`'s Statement is
normative and exhaustive: the module *shall* declare *"the single job each token carries: `SAGE`
completitud/vigente, `TEAL` procedencia repo, `VIOLET` relaciones/enlaces"* (`01-requirements.md:786-789`).
`LLR-S06.1.1` requires the docstring to state *"a token carries exactly one job"* (`:812-814`).
Handing the busy job to any of the three produces a token with two jobs **in the same increment that
declares the one-job rule.** `LLR-S06.3.5`'s census then has no oracle for that token — which is
`QA-B-08`'s original finding, re-created. The reading is self-defeating, not merely disfavoured.

> A disposition row inside an LLR cannot override the `shall`-Statement of its own parent HLR. The
> requirement hierarchy settles this without needing a date.

**Tiebreak 2 — the last-sealed document forecloses it explicitly.** `PDR-addendum-3.md:183-186`
(§4 `#D27`, sealed last at `5d8ee0d`): *"`Inc-1` adds `SAGE`, `TEAL`, `VIOLET` … **all three new
tokens are already spent** … There is **no unspent colour token**."* It then names each one's
claimant (V17/V18/V14+V19). Addendum-3 is not ruling on `#D10`, which makes it the stronger
witness: it is a *disinterested* recital of palette state, written for a different question, and it
says the "one of the three" reading has nothing to spend.

**Tiebreak 3 — the machine-checkable field already says two tokens.** `:994`'s **Touched symbols**
is the field Phase 3 is gated against, and it reads *"the promoted grey token **and the busy
token** in `mapper/darkside.py` — **both** `NEW — created in Phase 3`"*. Prose can be loose;
a Touched-symbols entry is a build contract. `LLR-CNV.1.4:1336-1338` independently confirms the set
grows: *"`LLR-S06.1.1`'s declared set **plus** the token `#D10` promotes"* — and `LLR-CNV.1.4`'s
"plus" is the promoted grey, leaving the busy token to be the other new one at `:994`.

**Conclusion.** `:984` and its two forward-copies (`PDR:571`, `PLAN.md:531`) are a **superseded
drafting artefact.** They were written when `#D10` was framed as *"retone to something in the
palette"*, before `LLR-S06.3.5` adjudicated the one-job rule out of `QA-B-08`. The prose at `:992`,
the touched-symbols at `:994` and the ledger at `:6534` are the corrected text; the table row was
never re-typed. **The new-token reading governs.**

### 1.3 · The fourth reading, taken seriously and priced

It exists and it has a real precedent, so it gets a full hearing rather than a dismissal.

> **Reading (d): create no token. Let the glyph carry *busy*, and paint the current stage `INK`.**
> The ladder becomes `● INK` / `◐ INK` / `○ WORDMARK`. Nothing is spent; the census is green,
> because `INK`'s job (primary foreground) already covers the site.

**Its precedent is strong.** `PDR-addendum-3.md` §4 is *exactly this move*, one document later and
one question over: the damaged card gets a **glyph**, `ALERT` is not spent, *"no colour token is
spent"*, and point 1 counts *"`01b` §3.5 gains no row"* as a benefit. If `#D27` refused to spend a
token, why should `#D10` mint one?

**Three reasons it fails here, in ascending order of weight:**

1. **The glyph remedy is already applied at this site.** `#D27`'s finding was that `roto` and
   `sano_vacio` *"paint byte-identically today"* — the glyph added the **only** distinction those
   states had. At `app.py:877-879` the glyph `◐` is **already there** and already distinguishes
   in-progress. Reading (d) does not add a carrier; it **removes** one and leaves the site with
   strictly less signal than it ships with today.
2. **It degrades the ladder at the one row the operator is watching.** `INK` would carry both DONE
   and CURRENT, collapsing a three-tone ladder to two. Worse, the shipped expression is
   `marker = "◐" if self.loading else "●"` — so under reading (d) a loading ladder paints
   `● INK / ● INK / ◐ INK / ○ WORDMARK`, and the active row is separated from three identical
   siblings by **one glyph's interior shading, at one cell.** That is the weakest possible channel
   for the fastest-scanned question the screen answers ("where am I?").
3. **It overturns `#D10` rather than discharging it.** `#D10`'s disposition is *"**Assign** the
   busy/in-progress job … **and retone the site**"*. Both `#D10` readings agree a **token carries
   the busy job**; they disagree only about *which*. Reading (d) refuses the assignment. `#D10`'s
   own diagnosis — *"The token set has no *busy* role"* — is stated as a **gap to be filled**
   (it is the justification for the assignment clause that follows it in the same cell), not as a
   standing condition to be preserved. **Choosing (d) is an A3 re-open of a sealed decision. It
   would need PDR, not this ruling.**

**Where the `#D27` precedent actually applies, and why it does not bind here.** `#D27` declined to
spend **a token that already had a job** (`ALERT`, whose single job is deferred, not absent — that
is C-55 limb 2 by name). This ruling spends **nothing**: `PULSE` is new, so no existing job is
displaced and no follow-on batch inherits a two-job token. The two rulings are consistent — both
protect the one-job law. `#D27` protected it by not spending; `#D10` protects it by not
double-booking. **Reading (d) is priced and rejected.**

Readings ruled out in passing, for completeness:

- **Retone to `MUT`** — `MUT` is the sala's pairing for *absent information* (`addendum-3:212-213`,
  V15/V21). Busy is not absent, and `MUT` (#737373) is **darker** than the DONE rows, inverting the
  ladder's salience.
- **Retone to `ACCENT`** — blue is interactivity-**only** (`LLR-S06.3.3`). Non-starter.
- **Retone to the promoted grey `ASH`** — gives `ASH` a second job, and paints CURRENT dimmer than
  DONE. Same two defects.

---

## 2 · The busy token — `PULSE = "#ff9ecb"`

```python
PULSE = "#ff9ecb"
```

| Property | Value | Constraint |
|---|---|---|
| `EIGHT_BIT` slot | **218** | `HLR-S06.2` — free; occupied set is `{16, 33, 35, 38, 105, 203, 221, 233, 235, 237, 242, 247, 255}` |
| min CIEDE2000 vs all 13 declared | **24.74** (`INK`) | `>= 10` addendum — clears by 2.5× |
| semantic floor **after** adding it | **13.99** (`ACCENT`/`VIOLET`, unchanged) | the floor does not move |
| nearest **hue** token | `ALERT` at **25.06** | see §2.2 |
| relative luminance | 0.5003 | semantic member (§3.2) |

### 2.1 · Re-derivation (I did not take the handed-down table on trust)

Executed here, `rich 15.0.0`, fresh `Color` per call, no `Style` reuse (`HLR-S06.2`'s caching
hazard). CIEDE2000 implemented directly from the CIE formulation over CIE L\*a\*b\* (D65), against
each slot's own `EIGHT_BIT` RGB. **Every figure in the routing packet reproduced exactly:**

```
pinned semantic set {ACCENT, ALERT, INK, MUT, SAGE, TEAL, VIOLET, WARN}
  floor        ACCENT/VIOLET  13.99      <- matches HLR-S06.2's addendum verbatim
  ACCENT/TEAL                 20.18      <- matches
  incl. surfaces GROUND/PANEL  3.20      <- surfaces are NOT semantic pairs, confirmed
slots  GROUND 16 · PANEL 233 · STEP 235 · INK 255 · MUT 242 · ACCENT 33
       WARN 221 · ALERT 203 · WORDMARK 237 · SAGE 35 · TEAL 38 · VIOLET 105
#a3a3a3  slot 247 · INK 20.14 · MUT 18.35 · WORDMARK 38.40   <- matches
```

The candidate sweep also reproduced line-for-line, and I extended it with six further
rose/pink options. Result: `#ff9ecb`, `#ffa6c9` and `#f9a8d4` **all downgrade to slot 218** and are
therefore *the same shipped colour at the guaranteed rung*. I take `#ff9ecb` because it is the
literal the batch already measured — this ruling introduces no unmeasured hex into the record.

### 2.2 · Why rose, and not the higher-scoring orange

`#f97316` deep orange scores 25.12 — nominally the best. **It is the wrong choice, and the margin
is noise.** Its nearest neighbour is `WARN` at 25.12; rose's nearest *hue* is `ALERT` at 25.06.
**Perceptual isolation from the hue tokens is a statistical tie (25.12 vs 25.06).** The decision is
therefore entirely semantic, and there the two separate sharply:

- **Deep orange interpolates the severity ladder.** It sits geometrically *between* `WARN` amber
  (`#ffd230`) and `ALERT` red (`#ff4f42`) — the exact axis `LLR-S06.3.5`'s one-job rule exists to
  keep legible. A third warm tone on that axis invites *"is this worse than a warning or better?"*.
  It re-creates `#D10`'s own complaint (*"a spinner that reads as a warning"*) one hue over.
- **Rose departs the axis.** Its nearest neighbour is `INK`, a **neutral** — it is the only
  candidate in the sweep whose nearest declared token is not a semantic hue. It reads as a
  lightness-and-hue departure, not as a severity step.

Same disqualification, briefly, for the rest: `#84cc16` lime → `SAGE` "completo" (a busy row is
precisely *not* complete); `#f0abfc`/`#d946ef`/`#e879f9` → `VIOLET` "enlaces"; `#38bdf8`/`#bfa5ff`
→ `ACCENT` "donde puedes actuar"; `#eab308` gold → `WARN`; `#06b6d4` **collides with `TEAL` on slot
38** outright.

**Stated plainly rather than buried:** `PULSE`'s nearest hue token *is* `ALERT`, at 25.06. For
scale, `WARN`/`ALERT` — two tokens deliberately built to be told apart — measure 45.36. So `PULSE`
sits closer to red than the amber does. I judge 25.06 sufficient (≈11× the ~2.3 JND, 1.8× this
batch's own floor) because the two differ in **lightness** as much as hue (0.50 vs 0.27 relative
luminance): a pale rose against a saturated alarm red. **This is the ruling's main perceptual risk
and it is recorded, not hidden** — see Risks R-2.

### 2.3 · The 16-colour rung — one new known limit, and it is harmless

`HLR-S06.2` guarantees `EIGHT_BIT` and above and declares `STANDARD` a known limit (not
auto-reachable; `legacy_windows` is `False`). Measured with `PULSE` and `ASH` added:

```
 0 GROUND, PANEL, STEP      6 SAGE, TEAL        8 MUT, WORDMARK     12 ACCENT, VIOLET
 7 ASH, PULSE               9 ALERT            11 WARN              15 INK
```

**New collapse: `ASH ≡ PULSE` at colour 7.** It costs nothing, and the reason is structural rather
than lucky: `ASH` is painted only in `mapper/views/radial.py`'s `_GREYS` (`MapScreen`) and `PULSE`
only at `mapper/app.py:879` (`RepoScreen`). **They never co-occur in a view.** The progress ladder
itself survives the rung intact — `INK 15` / `PULSE 7` / `WORDMARK 8`, three distinct colours.
Declare the row alongside the existing `ACCENT ≡ VIOLET` limit; do not fix it.

---

## 3 · The promoted grey — `ASH = "#a3a3a3"`

```python
INK = "#f5f5f5"
ASH = "#a3a3a3"      # <- inserted here, per #D10 "between INK and MUT"
MUT = "#737373"
```

Slot **247**. `INK` 20.14 · `MUT` 18.35 · `WORDMARK` 38.40. The floor stays **13.99**. No
identifier named `ASH` or `PULSE` exists anywhere under `mapper/` (grepped: no matches).

`ASH` is chosen to sit in the shipped register — plain, physical, one syllable, alongside `GROUND`,
`PANEL`, `STEP`, `INK`, `MUT`, `WORDMARK`. It reads as a grey without claiming a meaning, which is
right: its job is a **ramp position**, not a semantic role.

### 3.2 · A by-product this ruling owes you: the semantic set becomes decidable

`HLR-S06.2`'s addendum quantifies over *"semantic token pairs"* and `LLR-CNV.1.4` requires the
declared set's membership to be **decidable**. Adding two tokens forces the question of which side
each lands on. Ruling:

- **Declare `SURFACES = frozenset({GROUND, PANEL, STEP, WORDMARK})` in `darkside.py`; derive the
  semantic set as `TOKENS - SURFACES`.** The *pairs* stay derived (`itertools.combinations`), which
  is what `C-31` forbids hand-listing — a declared four-name surface set is not a hand-listed pair
  list. `ASH` and `PULSE` are both semantic.
- **Guard it with the measured luminance gap.** The two classes separate cleanly and by a wide
  margin: surfaces top out at `WORDMARK` **0.0423**; semantics start at `MUT` **0.1714** — a 4×
  gap with nothing in it. A test asserting *every surface < 0.10 < every semantic token* turns a
  mis-filed future token red. `ASH` 0.3663 and `PULSE` 0.5003 both sit far inside the semantic band.

This is the shape `LLR-CNV.1.4` asks for: a declaration for decidability, a measurement for the
mutation arm. **Note it is floor-safe either way** — `ASH`'s minimum (18.35) and `PULSE`'s (24.74)
both exceed 13.99, so a mis-classification could not silently move the floor.

---

## 4 · The two job statements

Register matched to `LLR-S06.3.5`'s declared jobs (`TOKEN #hex — *role*: one sentence`).

> **`ASH` `#a3a3a3` — *segundo escalón legible*: the middle rung of the text ramp on the black
> ground, for the tone one step below `INK` where `STEP` and `WORDMARK` are too dark to be read as
> text.**

> **`PULSE` `#ff9ecb` — *trabajo en curso*: this item is being worked on right now, and nothing is
> pending, overdue, at risk, or failed.**

`PULSE`'s trailing clause is load-bearing, not decoration: it is what makes `LLR-S06.3.5`'s census
adjudicable between `PULSE`, `WARN` (*pending, due, at risk, or in flight*) and `ALERT`. **It
requires one consequential edit to `WARN`'s declared job, and I am flagging it rather than
performing it** — see §5, item 3.

### The retone

```python
darkside.PULSE if self.loading else darkside.INK    # mapper/app.py:879
```

Ladder after: `● INK` (done) / `◐ PULSE` (in progress) / `● INK` (settled, not loading) /
`○ WORDMARK` (pending). Both carriers now agree — glyph *and* tone change on the active row —
and `WARN` leaves the file's progress path entirely.

---

## 5 · Artifacts this ruling obliges

**Code — two files, as budgeted. Nothing beyond them.**

1. `mapper/darkside.py` — `ASH` after `INK`; `PULSE` after `WORDMARK`; both jobs in the module
   docstring; `SURFACES` declared (§3.2).
2. `mapper/app.py:879` — the retone above.

**`01b-ux-decisions.md` §3.5 `colores con empleo` — NO row is owed. Ruled, with the reason.**

`PDR-addendum-3` §4 point 1 treats a §3.5 row as the price of a new coloured job, so the question is
live. It does not apply here:

- §3.5 is a **per-view legend**, not a registry of every token with a job. §3.6 fixes its framing as
  `leyenda · atlas` with *"cada vista tiene SU leyenda"*, and §3.5's five rows are sourced verbatim
  from the atlas/sala prototype (`ui_next2/generate.py:623-630`). **`ALERT`, `INK`, `MUT` and
  `WORDMARK` all carry declared jobs and none has a §3.5 row** — membership is "painted in this
  view", not "has a job".
- `PULSE` is painted **only** at `mapper/app.py:879`, inside `RepoScreen` (`app.py:828`,
  `KEY_SCOPE = SCOPE_REPO`) — a different view from the atlas/sala legend's.
- Therefore `LLR-N16.2.1`'s **second derived set is unchanged**, no legend row is added, and the
  panel-height pressure recorded at `02f-pdr-ux-pass2.md:617` is not touched. (`colores con empleo`
  has **zero** occurrences under `mapper/` today — it is a Phase-3 deliverable, so nothing shipped
  needs editing either.)
- **Falsifiable condition `C-D10a`:** if any later increment paints `PULSE` inside the atlas or sala
  views, it buys the §3.5 row **then**, at that increment's cost. This ruling does not pre-pay it.

**One flag I am raising and deliberately not deciding — `WARN`'s "or in flight" clause.**
`LLR-S06.3.5:1086-1087` declares `WARN` as *"pending, due, at risk, **or in flight**"*. Once `PULSE`
owns *in progress*, that clause makes `app.py:879` classify under **both** tokens — and
`LLR-S06.3.5`'s own threshold is *"sites classifying as **both** `== 0`"*. **The census goes red at
Inc-1 unless `WARN`'s clause is narrowed.** Note `:1127-1130` already saw this coming from the other
side (*"`app.py:879` becomes classifiable"*), and `#D10` answered it by retoning — but nobody struck
the clause. Minimal repair, at Inc-1, in the same docstring edit:

> `WARN #ffd230` — *outstanding attention*: work is pending, due, or at risk, and nothing has failed.

Dropping three words (`, or in flight`) restores a single owner per site. It **narrows** `WARN`,
never widens it, so `LLR-S06.3.5`'s one-job constraint is strengthened, not bent. It touches
`01-requirements.md:1086-1087` and the docstring — **the only doc edit this ruling requires, and it
is `LLR-S06.3.5`'s own consistency, not new scope.** Route it to the batch owner: I will not edit a
sealed requirements file.

**Tests** (inside the LLRs already written, no new LLR): `HLR-S06.2`'s slot/floor test now quantifies
over 14 tokens; `LLR-S06.3.2`'s register still lands at **1** entry after Inc-1 (`factory.py:104`);
`LLR-CNV.1.4`'s declared set is `TOKENS`, 14 members.

---

## 6 · Re-open or discharge?

**Within-envelope discharge of sealed `#D10`. Not an A3 re-open.** Three grounds:

1. **No sealed decision changes direction.** `#D10`'s disposition — *assign the busy job to a token,
   retone the site* — is executed exactly as written. What is settled is **which token**, on which
   the document contradicted itself. Choosing between two readings a sealed document already
   contains is discharge; choosing a third is re-opening.
2. **The governing reading was already the majority and the latest.** Three sites state it, the
   last-sealed document (`addendum-3`, `5d8ee0d`) presupposes it, and the normative parent
   (`HLR-S06.1`) makes the rival reading unexecutable. This ruling **records** that, it does not
   create it.
3. **The name and hex were always Phase-3 fill-in.** `:994` marks the busy token `NEW — created in
   Phase 3`. A batch that says a token is created in Phase 3, and never names it, has **delegated**
   the name — the same shape as `C-D27b` deliberately leaving a codepoint to the painting increment.

**Reading (d) would have been an A3 re-open** (it refuses `#D10`'s assignment clause), which is a
further reason it needed the full hearing it got in §1.3 rather than a footnote.

---

## 7 · Risks

| # | Risk | Severity | Mitigation / status |
|---|---|---|---|
| **R-1** | **`WARN`'s "or in flight" clause is not struck, and `LLR-S06.3.5`'s census reddens at Inc-1** on *sites classifying as both `== 0`* | **HIGH — the one thing that blocks the gate** | §5 item 3. Three-word deletion. **Must land in the same increment as `PULSE`, or Inc-1 does not go green.** |
| **R-2** | `PULSE` 25.06 from `ALERT`; a pale rose could read as a soft alarm to an operator | Medium | Above the floor by 1.8×; separated in lightness (0.50 vs 0.27) as much as hue. Confirmable in ~2 min at 118×34 — **hand to the ux lens before Inc-1's gate**; if it fails, `#f0abfc` (24.23, slot 219) is the fallback, at the cost of `VIOLET` proximity |
| **R-3** | Two new tokens instead of one — a wider Inc-1 diff than `PDR:571` implied | Low | Both were already budgeted at `:994` as `NEW — created in Phase 3`. No file count changes |
| **R-4** | `ASH ≡ PULSE` at the 16-colour rung | Low — accepted | Not auto-reachable; the two never co-occur in a view (§2.3). Declare as a known-limit row |
| **R-5** | A future increment paints `PULSE` in the atlas/sala and silently owes a §3.5 row | Low | `C-D10a` (§5) makes the debt explicit and assigns it to that increment |
| **R-6** | The `SURFACES` declaration is a hand-written four-name list — the shape `C-31` distrusts | Low | Pairs stay derived; the luminance guard (§3.2) reddens a mis-filed token. Recorded so it is a choice, not an oversight |

---

## Evidence checklist

- [✓] **Constraints stated explicitly** — all five restated and each checked in §2 (slot 218 free;
      floor 13.99 held; one job each in §4; `WARN`/`ALERT` unchanged except the narrowing in §5;
      set decidability ruled in §3.2).
- [✓] **At least 2 alternatives considered** — 4 readings: one-of-three (§1.2, unexecutable),
      new token (adopted), glyph-only/`INK` (§1.3, priced and rejected), retone to
      `MUT`/`ACCENT`/`ASH` (§1.3). Plus 20 candidate hexes swept.
- [✓] **Recommendation tied to constraints** — §2.2: orange rejected on `LLR-S06.3.5`'s severity
      axis despite a 0.06 higher score; rose adopted because its nearest neighbour is a neutral.
- [✓] **Risks listed** — R-1…R-6, with R-1 named as a gate blocker.
- [✓] **Cost/latency** — n/a (two string constants); perceptual budget quantified instead:
      floor 13.99 unmoved, `PULSE` min 24.74, slot 218, luminance gap 0.0423→0.1714.
- [✗] **Diagram** — not included; the flow is a 4-row ladder and the §4 listing carries it fully.
- [✓] **What would change the recommendation** — §2.2 + R-2: a ux-lens read at 118×34 finding rose
      reads as an alarm → `#f0abfc`. A decision to strike `#D10`'s assignment clause → reading (d),
      but that is an A3 re-open (§6).
- [n/a] **Two-layer requirements** — this is a ruling inside a sealed batch, not a new story. It
      adds no US/HLR/LLR and no AT; it discharges an ambiguity inside `LLR-S06.3.2` and lands in
      existing thresholds (`HLR-S06.2`, `LLR-S06.3.5`, `LLR-CNV.1.4`).

**Files this ruling authorises Inc-1 to touch:** `mapper/darkside.py`, `mapper/app.py`.
**Routed to the batch owner, not performed here:** the three-word narrowing of `WARN`'s declared
job at `01-requirements.md:1086-1087` (R-1).
