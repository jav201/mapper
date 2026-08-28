# `02i` · `#D10` — the busy rung of the loading ladder · UX ruling

**Batch:** `2026-08-26-ui-next-batch-02` (SEALED) · **Lens:** ux · **Scope:** `mapper/app.py:879` and the
ladder it belongs to (`_stages_text`, `:865-882`). Nothing else re-opened.

**Glyph convention in this file:** per the batch's standing rule, no raw glyphs. `FILLED` = U+25CF,
`HALF` = U+25D0, `HOLLOW` = U+25CB, `UP-TRI` = U+25B2, `LIGHT-SHADE` = U+2591.

---

## BLUF

**No new colour token. `#D10` is fixed by re-ranking the ladder on the NEUTRAL RAMP, which carries no
`§3.5` job at all — and by striking the `in flight` limb from `WARN`'s declared job.**

The ladder is already glyph-led with three distinct shapes, so `#D27`'s ruling governs directly. But
this case is *stronger* than `#D27`, not merely analogous: `#D27` had to invent a glyph to carry a
distinction that colour was being asked to carry. Here **the glyph vocabulary already exists and
already carries the full three-way distinction** — `FILLED` / `HALF` / `HOLLOW`. Colour in this widget
is the secondary carrier by construction. Spending a scarce hued token to duplicate a distinction the
shape channel already makes is the definition of paying for nothing.

**Verdict: `pass-with-notices`** on "no new token", with **two blocking conditions** and **one carry**.

---

## 1 · VERDICT — what `CURRENT` paints

`#D10`'s complaint is correct but its diagnosis is off by one. It reads as a census problem; it is not.
`WARN`'s declared job **already contains the limb `in flight`**, so `LLR-S06.3.5`'s one-job census
**passes on line 879 today**. Nothing is currently violated.

The defect is a **reading** defect, which is this lens's subject: a token whose job string spans both
*"you have an outstanding obligation"* (`pending`, `due`, `at risk`) and *"the machine is working"*
(`in flight`) has a job that cannot be scanned, because those two demand **opposite things of the
user** — one demands action, the other demands patience. That is not one job wearing two hats. It is
two jobs sharing a hex.

**The evidence that this is real and not theoretical is in the repo.** `mapper/views/lane.py:16-17`
maps `risk` and `late` to `WARN`; `mapper/views/lane.py:67` paints `HALF` + `" run"` in `WARN`. **Both
meanings are painted in the same token, in the same view, adjacent to each other.** An operator looking
at the lane view cannot tell *the machine is busy* from *you are late* by colour. `#D10` found the
second-cheapest instance of this; `lane.py:67` is the first.

### Ruled ladder

| Rung | Glyph | Token | Why |
|---|---|---|---|
| DONE | `FILLED` | **`TRACE` `#a3a3a3`** | finished business; present, recedes |
| CURRENT | `HALF` | **`INK` `#f5f5f5`** | the one row that is true *now* — the brightest thing in the widget |
| PENDING | `HOLLOW` | **`MUT` `#737373`** | legible, clearly subordinate |

**Two orthogonal channels, one carrier each:**

- **brightness = has this stage been REACHED** — a monotone recency ramp, `INK` > `TRACE` > `MUT`.
- **glyph = is it FINISHED or IN FLIGHT** — `FILLED` vs `HALF`, filled vs half-filled vs hollow.

Neither channel is asked to carry the other's meaning. This is why no hue is needed: **"busy" is not a
colour role here, it is a *shape* role, and the shape already exists.**

### Why this also fixes a hierarchy inversion nobody filed

Today `DONE` is `INK` — the **brightest** rung is the work that is already over — while `CURRENT` is
amber and `PENDING` is functionally invisible. The eye lands on the past. In a progress ladder the eye
should land on **where am I now**. Inverting the ramp so `CURRENT` is brightest is the correct
hierarchy and costs zero tokens. This is a free rider on `#D10`, not scope creep: retoning line 879 to
a neutral **forces** a decision on line 876, because if `DONE` and `CURRENT` are both `INK` the colour
channel goes flat and the ladder degrades to glyph-only. All three arms live in one function, the one
`#D10` names.

### The `#D27` weighing, point by point

`PDR-addendum-3.md` §4's five grounds, applied here:

1. **Spends nothing scarce** — holds, and harder. `#D27` still had to spend `MUT on PANEL`. This
   ruling spends only the neutral ramp, which `§3.5` does not govern.
2. **Reuses the shipped pairing** — holds. `INK`/`MUT` on `PANEL` is the sidebar's existing text
   pairing; `#repo-stages` already declares `color: #737373` as its CSS default (`app.py:1939`), so
   `MUT on PANEL` is **literally the widget's own resting tone**. `PENDING` is not being given a new
   colour; it is being allowed to fall back to the one the stylesheet already sets.
3. **The vocabulary is already glyph-led** — holds *a fortiori*. `#D27` argued this about a view whose
   glyphs it had to add. Here the three glyphs **ship today**. A glyph is scanned, not read.
4. **Answers the finding's own complaint** — holds. `#D10` says the token set "has no *busy* role". The
   ruling agrees and declines to create one, because the busy role is discharged by `HALF`.
5. **The derived set grows by one row either way** — holds, and the ruling picks the cheaper set: a
   **glyph-vocabulary** row (`§3.4` register, already derived) instead of a `colores con empleo` row
   plus a fourteenth token plus a permanent census obligation.

**The `C-55` limb-2 trap `#D27` avoided does not even apply here** — no token is being spent on an
emptiness that is an artifact of today's scope, because no token is being spent.

---

## 2 · If a new token — declined, and why the best candidate still fails

Not applicable under this ruling. Recording the reasoning so it is not re-litigated:

The strongest measured candidate was **`#f97316` deep orange** (slot 208, min CIEDE2000 25.12 vs
`WARN`). It clears every distance test and **still fails on semantics**, which is the test that
matters: deep orange sits **between `WARN` amber and `ALERT` red** — it lands *inside the severity
family*. A user does not read a hue against a table of CIEDE2000 floors; they read it against the
neighbours already on their screen. Placing the busy state between "attention" and "failure" tells the
operator that a normal, successful load is **the most alarming thing in the sidebar**, which is the
exact misreading `#D10` filed. The candidate with the best number is the worst answer.

The remaining families fail the same way and faster: **lime** (`#84cc16`, 19.66) reads as `SAGE`
completion — a stage that is *running* would paint as *done*; **sky** (`#38bdf8`, 11.89) reads as
`ACCENT` interactivity — it invites a click on a row that is not actionable; **the fuchsia/orchid
family** collapses into `VIOLET`'s relational job. **There is no free hue, because there is no free
*meaning*.** The palette is austere by design and the meaning-space, not the colour-space, is what is
exhausted.

---

## 3 · Job statements

Because no hued token is created, the rows owed are **`§3.4` glyph-vocabulary rows**, not `§3.5`
colour rows.

**Spanish-facing (`01b` §3.4 register — three rows, one ladder):**

> `HALF etapa en curso` — `la etapa que corre ahora; el mapa está trabajando, no hay nada que hacer`
> — painted `INK on PANEL`.
> (`FILLED etapa cumplida` — `TRACE on PANEL`; `HOLLOW etapa pendiente` — `MUT on PANEL`.)

The clause **`no hay nada que hacer`** is the whole point of the ruling and should survive review
verbatim: it is the sentence that distinguishes this state from everything `WARN` means.

**English docstring line, at `_stages_text`:**

```python
# Ladder channels are orthogonal: brightness = reached (INK > TRACE > MUT),
# glyph = finished vs in flight. Busy is a SHAPE role, not a colour role --
# no hued token is spent, per PDR-addendum-3 §4 (#D27) and #D10.
```

---

## 4 · The promoted `#a3a3a3` ramp step

**NAME: `TRACE`.**

```python
TRACE = "#a3a3a3"  # secondary stroke: structure and text that must read, but is not the subject
```

**Spanish job:** `trazo secundario — se lee, pero no es el asunto`.

**Register check.** The shipped names are **role nouns, not colour nouns** — `GROUND` / `PANEL` /
`STEP` are surfaces, `INK` / `MUT` / `WORDMARK` are marks. `SLATE`, `ASH`, `SILVER` would break that
convention by naming the hue. `TRACE` names the role and covers **both** observed sites: the mid-grey
**branch tint** in `mapper/views/radial.py:18` (a drawn stroke) and the `DONE` rung here (a mark that
has been made and is now background). It is the step between the ink and the mute.

**It changes no floor.** 18.35 CIEDE2000 from `MUT`, 20.14 from `INK`; the semantic pair-set floor
stays at 13.99 (`ACCENT`/`VIOLET`). `TRACE` joins the **ramp**, not the job list — so, like `INK`,
`MUT` and `WORDMARK`, it owes `§3.5` nothing.

---

## 5 · Distinguishability — measured, not asserted

Executed against the shipped hexes with `rich 15.0.0`, `PYTHONUTF8=1`, a fresh `Color` per call.
The ladder's surface is **`PANEL #121212`**, not `GROUND` — `app.py:1937`,
`#repo-sidebar { background: #121212 }`. Contrast is WCAG 2.x on the **rendered** triplet at each rung.

### (a) Truecolour

| Rung | Token | On `PANEL` |
|---|---|---|
| CURRENT | `INK #f5f5f5` | **17.18:1** |
| DONE | `TRACE #a3a3a3` | **7.43:1** |
| PENDING | `MUT #737373` | **3.95:1** |

Monotone, three levels, plus three distinct glyph shapes. **Pass.**

### (b) `EIGHT_BIT` — the guaranteed rung

Downgrade lands on **three distinct slots: 255 / 247 / 242**. Rendered and re-measured on `PANEL`:

| Rung | Renders as | On `PANEL` |
|---|---|---|
| CURRENT | `#eeeeee` (255) | **16.15:1** |
| DONE | `#9e9e9e` (247) | **6.99:1** |
| PENDING | `#6c6c6c` (242) | **3.57:1** |

No collision. **Pass.**

### (c) The declared-known-limit 16-colour rung

Measured downgrade to `ColorSystem.STANDARD`:

| Rung | Token | → | Renders as | On black |
|---|---|---|---|---|
| CURRENT | `INK` | `15` white | `#ffffff` | **21.00:1** |
| DONE | `TRACE` | `7` silver | `#c0c0c0` | **11.54:1** |
| PENDING | `MUT` | `8` bright black | `#808080` | **5.32:1** |

Three distinct slots; the ladder is **more** legible here, not less. Note `WORDMARK` **also** maps to
`8` at this rung — `MUT` and `WORDMARK` collapse, which is a *fourth* known 16-colour collision beyond
the two the batch declares (`ACCENT`/`VIOLET`, `SAGE`/`TEAL`). It does not touch this ladder, since the
ruling puts no `WORDMARK` on it. **Recorded in §7 as a carry.** **Pass.**

**Stated against my own ruling:** today's set (`INK 15` / `WARN 11` / `WORDMARK 8`) *also* survives at
16 colours. **The 16-colour rung is not an argument for this ruling.** The arguments are semantic
(§1) and contrast (below). Claiming rung survival as a win here would be a vacuous check.

### (d) Red–green colour vision deficiency

**The ruled ladder is fully achromatic.** Deuteranopia and protanopia leave a neutral ramp
mathematically untouched, so all three rungs are distinguishable by luminance alone, at every rung,
with **no simulation required** — the invariance is structural, not empirical. This is a strict
improvement over `WARN` amber, which darkens under protanopia and drifts toward the `WARN`/`ALERT`
confusion axis that the sidebar's neighbouring `UP-TRI` and `LIGHT-SHADE` indicators sit on. **Pass.**

### The defect the ruling repairs, which `#D10` did not file

`PENDING` today is `WORDMARK #3a3a3a` on `PANEL #121212` = **1.65:1**. That is below the 3:1 non-text
threshold and far below 4.5:1 for text. **The pending rungs of the shipped ladder are not dim — they
are not there.** A three-state indicator is shipping as a two-state one, and the glyph channel
(`HOLLOW`) is invisible along with it. `MUT` takes `PENDING` to 3.95:1 truecolour / 3.57:1 at
`EIGHT_BIT`. This is the reason the ruling must touch all three arms and not line 879 alone.

⚠ `MUT on PANEL` is **3.95:1 — under 4.5:1 AA for body text**. Accepted here, declared not hidden: the
rung is a 2-3 word label carrying redundant information (the glyph and its ladder position both say
"not yet"), and `MUT` is the widget's own declared CSS default (`app.py:1939`). Raising `PENDING` to
`TRACE` would clear AA but collapse `DONE` and `PENDING` into one tone. **Not blocking.**

---

## 6 · Does `01b` §3.5 owe a row?

**No.**

`§3.5` `colores con empleo` is the **hued** register — every row is a hue word: `azul`, `ámbar`,
`sage`, `teal`, `violeta`. `INK`, `MUT` and `WORDMARK` hold no rows there despite painting most of the
app, because the neutral ramp is the substrate a job is painted *on*, not a job. `TRACE` joins that
ramp. **No new row; the `LLR-S06.3.5` census stays adjudicable; `LLR-N16.2.1`'s derived set grows by
`§3.4` glyph rows only.**

**But `§3.5` does owe an EDIT — and this is blocking.** `WARN`'s job string must **lose the `in flight`
limb**, leaving `ámbar — atención / vence` (which is already exactly what the shipped `§3.5` row says;
the drift is in the job prose, not the table). Without this, the one-job census would still certify
amber as a legal busy colour and `#D10` reopens in the next batch. **Narrowing costs exactly two
sites**, censused: `app.py:879` (this ruling) and `views/lane.py:67`. Every other `WARN` site —
`app.py:392`, `:399`, `:410-411`, `:924`, `:1296`, `:1311`, `lane.py:16-17`, `layered.py:20-21`, `:69`,
`:230`, `outline.py:39`, `:136`, `radial.py:99`, `rail.py:251` — is `vence` / `riesgo` / `falta` /
`baja`, all squarely `atención`. **The limb has no other dependents.**

---

## 7 · Conditions and carries

**Blocking:**

- **`C-D10a`** — `§3.4` gains the three ladder rows (§3 above) **before the increment paints them**,
  and they enter `LLR-N16.2.1`'s derived set through the derivation, never as literals. Codepoints are
  drawn from the declared vocabulary by the increment, not fixed here — `C-D27b`, same reasoning.
- **`C-D10b`** — `WARN`'s declared job loses `in flight` in the same increment that retones line 879.
  A ruling that removes the use without removing the licence is half a ruling.

**Carries (not this batch):**

- **`B-NEW-1` — `mapper/views/lane.py:67` is the same defect, unfiled.** `HALF` + `" run"` in `WARN`,
  adjacent to `risk`/`late` in `WARN` at `:16-17`. It resolves identically (`HALF` in `INK`) and
  **must not be fixed here** — it is outside `#D10`'s named site and outside the sealed scope. Filing
  it is the point; fixing it silently would be scope creep.
- **`B-NEW-2` — `MUT` and `WORDMARK` collapse to slot `8` at the 16-colour rung.** A third declared
  collision pair, measured in §5(c). Does not affect this ladder; belongs in the known-limits register
  next to `ACCENT`/`VIOLET` and `SAGE`/`TEAL`.

---

## 8 · Criteria — how each was exercised

| # | Criterion | Exercised by | Painted / computed result | Verdict |
|---|---|---|---|---|
| 1 | Ladder surface is `PANEL`, not `GROUND` | read shipped CSS, `app.py:1937` | `#repo-sidebar { background: #121212 }` | pass |
| 2 | Three rungs occupy distinct `EIGHT_BIT` slots | `rich 15.0.0` `Color.downgrade`, fresh `Color` per call | `255 / 247 / 242` | pass |
| 3 | Three rungs survive the 16-colour rung | same, `ColorSystem.STANDARD` | `15 / 7 / 8` | pass |
| 4 | Each rung is legible on `PANEL` | WCAG 2.x on **rendered** triplets | `16.15 / 6.99 / 3.57` @ 8-bit | pass ⚠ |
| 5 | Shipped `PENDING` is legible | same, on `WORDMARK #3a3a3a` | **1.65:1 — fails 3:1** | **fail (repaired by ruling)** |
| 6 | `in flight` limb has ≤ 2 dependents | grep census of all 19 `darkside.WARN` sites | 2 (`app.py:879`, `lane.py:67`) | pass |
| 7 | `TRACE` does not move the semantic floor | batch's pinned reproduction (given) | floor stays 13.99 `ACCENT`/`VIOLET` | pass |
| 8 | Three-way distinction survives loss of colour entirely | glyph channel inspected in source | `FILLED`/`HALF`/`HOLLOW` — three shapes | pass |

---

## 9 · Explicitly NOT covered

- **No pilot run was executed.** This ruling is a **source-and-colour inspection**, not a
  `App.run_test()` walkthrough. The ladder is reachable only during a live repo load, and driving that
  state means touching implementation mid-increment, which the mandate forbids. **The criteria above
  are computed from the shipped hexes and the shipped CSS, not observed on a painted `Strip`.**
  Criterion 4's contrast figures are therefore *derived*, not *painted*. **The increment that lands
  `#D10` must assert the three rungs on a real `Pilot` snapshot** — that is where `C-32` is discharged,
  not here.
- **Evaluation with real users was not performed.** ISO 9241-210 asks for it; this team is one person.
  What was done is a cognitive walkthrough over the declared context of use (118 × 34, dark terminal,
  Spanish UI) plus measurement of the real colour pipeline. **A measured contrast ratio is not a user
  telling you the ladder reads as a warning.** The claim that amber "reads as a spinner that looks like
  an alarm" originates in `#D10` and is adopted on the strength of the `lane.py:67` adjacency, not on
  observed user behaviour.
- **The `TRACE` name is not validated against `radial.py`'s other consumers.** Its second site
  (`radial.py:18`) was read but the radial view's full tone system was not re-opened.
- **Motion, latency and failure states of the loader are out of scope.** `#D10` is a retone. What the
  ladder does when a load *stalls* or *fails* — the states where `ALERT` would genuinely be in
  question — is not ruled and not filed here.
