# PDR addendum 3 — the routed cross-artifact rulings

**Date:** 2026-08-27 · **Batch:** `2026-08-26-ui-next-batch-02` · **Author:** orchestrator
**Status:** SEALED on issue. Ids `#D25`–`#D27` are new; no sealed decision is edited in place.
**Instrument:** each ruling executed against disk. A citation of another document is not evidence.

---

## 0 · Why this file exists

Amendment set 3 pass 2 closed 25 of the 27 live lens conditions **inside `01-requirements.md`**
and routed six cross-artifact edits to the orchestrator, because they land in artifacts the
requirements lane may not write. Two were mechanical and are landed in this same commit; three
needed a **ruling**; one was already discharged.

| Routed item | Kind | Disposition |
|---|---|---|
| `P2-B3` — the stale legend literal in `01b` | edit | **Already discharged at pass 2.** Re-read here, not trusted: `01b-ux-decisions.md:382-385` carries the derived count and no literal. ✓ |
| `P2-C4` — `with_header` in the ARQ roster | edit | **LANDED** — `ARCHITECTURE-proposed-at-ARQ.md:275` struck; the stale `layered.py:78-87` address corrected to `:131-140`. |
| `P2-C7` — the `dots`/`bgs` commitment row | edit | **LANDED** — `docs/ARCHITECTURE.md` §4 gains the second A3's `COMMITTED, NOT PRESENT` row. |
| `UX2-C-03` — the seat-diff cap | **ruling** | **`#D25`** below. |
| `UX2-C-05` — the legend layout | **ruling** | **`#D26`** below. |
| `UX2-C-09` — the damaged-card token | **ruling** | **`#D27`** below. |

---

## 1 · A finding that governs how these ids are read — two registries collide

**Measured, before any ruling was made.** This batch runs **two** decision registries that share
one id grammar:

| Registry | `D10` means |
|---|---|
| `PLAN.md` §9 decision log (`:244`) | **Q-3 answered, option (a)** — search takes `n`/`N`; `next_gap` moves `n → M`. Three new seat rows. |
| the sealed PDR (`:566`) | **Q-10 — the three census exceptions.** Three *hue* dispositions. Nothing to do with seats. |

The PDR's own prose at `:372`, `:396` and `:484` writes bare **`D10`** meaning the **PLAN's** D10.
So *"`#D10`'s seat-diff cap"* — the phrasing the routing inherited — **names the wrong artifact's
decision**: the sealed `#D10` is about hues.

**The cap's real carrier is `#D5b`** (`PDR-2026-08-26-ui-next-batch-02.md:394-398`), which is what
`#D25` re-opens. Recorded rather than quietly corrected, because C-50 says the ids are the glue of
the repo/vault split, and an id that resolves to two different decisions is the glue failing.

⚠ **Carry:** bare `Dn` citations in `PLAN.md` and in PDR prose are ambiguous batch-wide. Backlog
`B-34`.

---

## 2 · `#D25` — the three-row seat-diff figure is a PIN on `#D5b`'s own diff, not a per-increment budget

**Re-opens:** `#D5b`. **Supersedes:** nothing — it *states the scope* `#D5b` left implicit.
**Verdict: the premise that `UX2-C-03` breaches a cap executes FALSE. There is no breach.**

### The question, stated before the answer

`A-65` names four pan chords `H` `J` `K` `L` for `Inc-3` and reports: *"Four rows breaches `#D10`'s
three-row seat-diff cap … `Inc-3` shall not open until the cap is ruled."* That is only a breach if
the figure is a **budget over every increment**. Read as written, it is not.

### `#D5b` verbatim, and what it actually quantifies over

> **`#D5b` — Inc-4 owns the seat rebind `n → M` plus `n`/`N` (D10), alone.** Three seat rows change
> in one increment: `map/n → next_hit (nav)`, `map/N → prev_hit (nav)`, `map/M → next_gap (view)`.
> D10's three-row seat-diff cap is reviewed row-by-row at DDR. Inc-3, Inc-6 and Inc-9 also touch
> `keymap.py`, so the file is a **four-way collision resolved by serial ordering, not by ownership**
> — each must re-run `duplicate_chords()` and the whole-seat pin.

Three observations, each decisive:

1. **The sentence enumerates its own three rows.** The figure is not a limit chosen in advance; it
   is the **count of `D10`'s diff**, pinned so that diff cannot grow silently between PDR and DDR.
   *"Reviewed row-by-row at DDR"* is a review obligation over those three rows, not an allowance.
2. **The very next sentence anticipates `Inc-3` touching `keymap.py`** and states what `Inc-3` owes:
   `duplicate_chords()` plus the whole-seat pin. **It imposes no row budget.** A decision that
   contemplated a per-increment cap and then listed three other increments' obligations without
   mentioning one is not a decision that has a per-increment cap.
3. **`#D5b`'s subject is `Inc-4`'s ownership** — *"alone"*. Its scope is one increment's diff.

**Ruling.** The three-row figure is a **regression pin on `Inc-4`'s seat diff**, in C-40's exact
sense — a pin, not a gate — and is hereby labelled so. It binds `Inc-4` and nothing else. `Inc-3`'s
four pan rows are a separate, legitimate diff. **`Inc-3` is unblocked.**

### The enlarging half — a successful challenge must leave the base of truth larger

Reading a pin as a budget was a *false-fail*, and C-53 prices a false-fail as high as a false pass.
But the alarm was not baseless: **no obligation was attached to `Inc-3`'s seat rows at all.** So
`#D25` adds one rather than merely removing an alarm:

- **C-D25a — every increment that changes a seat row declares its OWN row diff in its packet**
  (rows added / removed / rebound, by seat key), and pins it the way `#D5b` pins `Inc-4`'s.
  **A pin per diff, no global cap** — a global cap would price a well-cut increment against an
  unrelated one's spending.
  > **CORRECTED 2026-08-27 at PDR-3, on two independent lens findings.**
  > **(a) The increment set was wrong.** It named the **vacated** `Inc-6` (`01-requirements.md:5586`)
  > and omitted `Inc-8`, which `:4539-4540` puts in the collision set. The set was stated **four ways
  > across the batch and no two agreed**. **Derived, not transcribed — the true set is `Inc-3`,
  > `Inc-4`, `Inc-8`, `Inc-9`.** `keymap.py` must be added to `Inc-8`'s §5.4 budget row, which omits
  > it (→ 4 of 4 source files, no breach).
  > **(b) It had no oracle — C-40 limb 1.** A declared diff joined to nothing is not a pin: rebind a
  > fifth seat row and declare four, and `duplicate_chords()` still returns `[]` because no duplicate
  > is created. **The declared diff shall be asserted EQUAL to the entry/exit difference of
  > `bindings_for(scope)`** — which `C-D25b`'s whole-seat pin already computes, so this binds two
  > existing artifacts rather than building a third.
- **C-D25b — `duplicate_chords()` and the whole-seat pin run on ENTRY and EXIT of each of the four**,
  as `#D5b` already requires. Unchanged, restated because it is now the *only* cross-increment control
  on `keymap.py`.
- **C-D25c — DDR reviews the four diffs as one set**, since serial ordering means the last increment
  sees a seat none of the earlier ones did.

**Executed basis.** `A-65` records: all four chords arrive as their own `event.key`, all four free in
map scope, `H` changes nothing on the shipped screen, `duplicate_chords()` returns `[]`. No collision
exists to adjudicate.

**What would reverse this:** a statement anywhere in the sealed PDR that budgets seat rows across
increments. Searched: `seat-diff`, `three-row`, `cap` — the only occurrence is the `#D5b` sentence
quoted above.

---

## 3 · `#D26` — the legend scrolls; the tabbed redesign is deferred

**Re-opens:** nothing sealed. **Answers:** `UX2-C-05` / `A-72`'s routed layout question.

### The question is already half-ruled, and the routing did not say so

The routed question was *"is a flat ~44-row scroll the right information design?"* — but `01b` §3.8
has already **ruled the flat panel out**, on a measurement:

```
  MINIMUM legend height : 54 rows
  walkthrough terminal  : 34 rows
  VERDICT: DOES NOT FIT — short by 20 rows
```

> **US-N16 cannot paint one flat panel.** It needs a scrolling container or a two-pane/tabbed
> legend, and whichever is chosen, the set-equality criterion must assert over the panel's
> **content**, not over what happens to be visible.

So the live choice is **scroll vs tabbed**, not flat vs scroll. And `LLR-N16.2.1` grows the
vocabulary well past the prototype's 6 rows, so the shortfall is **larger** than 20.

**Ruling: a scrolling container, this batch. The two-pane/tabbed legend is deferred.**

1. `01b` §3.8 admits the scrolling container explicitly. It is not a workaround.
2. **It closes the defect actually raised.** `UX2-C-05` is a *discoverability* finding — `down`,
   `pagedown` and `end` all work and none was declared. `HLR-N16.4` (`A-72`) fixes that by set
   equality between keys-that-work and keys-declared, asserted by **real presses**. That holds under
   either layout.
3. **Content is not lost** — the union over scroll positions is total. This is purely discoverability,
   which is what makes deferral honest rather than convenient.
4. **The tabbed route is not specified anywhere.** It is a new information architecture on the one
   screen whose entire job is discoverability, with a new AT surface and a new focus model. Adopting
   it here would be new scope entering at the final PDR iteration.

**Conditions:**

- **C-D26a — set equality asserts over CONTENT, never over visible rows** (`01b` §3.8, verbatim).
  An assertion over what is visible passes on a clipped panel, which is what ships today.
- **C-D26b — the scroll keys are asserted by real keystrokes, not by `scroll_to(...)`.** `A-72`
  already records why: `tests/test_repair_layout.py` scrolls by **method call**, which proves the
  container scrolls and says nothing about whether an operator can make it. C-16 verbatim.
  > **SCOPED 2026-08-27 to `HLR-N16.4` / `AT-053` ONLY**, on the qa lens's finding — unscoped it
  > **manufactures a false-fail** (C-53). `scroll_to(...)` remains **legal as a HARVESTING
  > mechanism**: `tests/test_repair_layout.py:118` uses it to union painted rows across scroll
  > positions, which is precisely how `C-D26a` observes *content* rather than visible rows. It is
  > forbidden **only as the assertion that an operator can scroll**. Applied literally to every arm
  > it would rewrite the content oracle into keystrokes and couple `AT-053`'s subject into `AT-041`,
  > `AT-042`, `AT-043`, `AT-044` and the negative control `AT-R14`.
- **C-D26c — deferral is recorded as a carry, not dropped.** Backlog `B-35`. **Landed 2026-08-27**
  (it was cited four times before it existed — a condition of this ruling dropped at the moment of
  approval, caught by the architect lens).

---

## 4 · `#D27` — the damaged card gets a GLYPH; `ALERT` is not spent

**Re-opens:** nothing sealed. **Answers:** `UX2-C-09` / `A-69`'s routed token choice.
**Constraint honoured:** `LLR-S06.3.5` — `WARN` and `ALERT` each carry exactly one job.

### What the palette actually has left — executed

`mapper/darkside.py:12-20` ships nine tokens; `Inc-1` adds `SAGE`, `TEAL`, `VIOLET`. Against `01b`
§3.4's sala vocabulary and §3.5's `colores con empleo`, **all three new tokens are already spent**:
`VIOLET` = `enlaza mapas` (V17), `TEAL` = `procedencia repo` (V18), `SAGE` = `completo / vigente`
(V14, V19). There is **no unspent colour token**.

### Why `ALERT` looks free, and why that is exactly the trap

`01b` §3.5, verbatim:

> `ALERT #ff4f42` is **deliberately absent** from this list and is the only token DECISION 2 assigns
> to **the malformed-query chip**. If ALERT acquires a second job it must acquire a row here too.

`ALERT`'s one job is the malformed-query chip — which belongs to **DECISION 2, the lens**, and the
lens is **CUT from this batch** (re-scope A, carried as `B-31`/`B-32`). So *within this batch* `ALERT`
has zero jobs and the damaged card would be its first.

**That is C-55 limb 2 by name: an emptiness that is an accident of today's scope.** The lens is not
cancelled, it is scheduled. Spend `ALERT` here and the follow-on batch reinstates the malformed-query
chip into a token that now has two jobs — at which point `LLR-S06.3.5`'s one-job census can no longer
adjudicate `ALERT` at all, and `01b` §3.5 owes a `colores con empleo` row that `LLR-N16.2.1`'s derived
set must then carry. **Ruling on the emptiness costs the follow-on batch a defect this batch would
not see.**

**Ruling: the damaged card's `PRED-VIS` limb is a declared GLYPH in the sala vocabulary, painted in
`MUT on PANEL`. No colour token is spent.**

1. **It spends nothing scarce.** `ALERT` keeps its single, deferred job; `01b` §3.5 gains no row;
   `LLR-S06.3.5`'s census stays adjudicable.
2. **`MUT on PANEL` is the sala's existing pairing for absent information** — V21's unlit `∙`
   (`sin acta`), V15's `faltan campos ░`. **A map that cannot be summarised is an absence of
   information, not an alarm.** Reusing the shipped pairing over inventing a role.
3. **The sala vocabulary is already glyph-led** — `⇄` (V17), `◍` (V18), `▲` (V20), `█`/`░` (V19),
   `∙` (V21). The colour is the secondary carrier in every one. A glyph is the *conventional* choice
   in this view, not a fallback.
4. **It satisfies `PRED-VIS` as written** — *"a declared token **or glyph**"* — and answers the
   finding's own complaint: `roto` and `sano_vacio` paint byte-identically today, and *"a card that
   differs only in text differs only to someone already reading it."* A glyph is scanned.
5. **`LLR-N16.2.1`'s derived set grows by exactly one row either way.** The difference is *which*
   set: a **glyph-vocabulary** row (already derived, no literal moves) instead of a `colores con
   empleo` row plus a broken one-job law.

**Conditions:**

- **C-D27a — the glyph is DECLARED in `01b` §3.4 as a new `V` row before `Inc-7` opens**, and enters
  `LLR-N16.2.1`'s derived set through the derivation, never as a literal. `A-45` records what a
  hand-written count costs here: four wrong generations.
- **C-D27b — the codepoint is NOT chosen in this ruling.** It is drawn from the declared vocabulary
  by the increment that paints it, and asserted by the derived-set test. A codepoint fixed here would
  be a fifth hand-listed count.
- **C-D27c — the arm runs at 118 × 34**, the declared context of use, per `A-69`. Unchanged.
- **C-D27d — the healthy-empty control is retained.** `roto` vs `sano_vacio` must now differ in the
  **painted** row, not only in a transient toast.

---

## 5 · `UX2-C-01` / `UX2-C-02` — disposition

**Not ruled here. Referred to PDR iteration 3 as an explicit question**, per the routing.

- **`UX2-C-01`** — the inspector's commit-on-blur durably rewrites the sidecar: `pilot.press("n")`
  over 9 focusables committed a ficha overwrite on 5 and rewrote the sidecar on 6. It was
  **reproduced by accident on the repository's own tracked fixtures** during the RIDER-1 audit
  (`02g` §6), turning `erp[Sistema ERP Legacy]` into `erp[n]`. Restored and sha256-verified.
- **`UX2-C-02`** — proposes `c` (`consultar campos`) as the lens entry chord. **The lens is cut**, so
  the chord has no consumer this batch.

**Recommended disposition, for the lenses to accept or refuse:** both DEFER to the follow-on design
batch with `UX2-C-11` (`B-31`/`B-32`) — they share one confirmation-affordance question, and
`UX2-C-02`'s chord is unbuildable without the feature it enters.

⚠ **The deferral is NOT cost-free and must not be recorded as if it were.** `UX2-C-01` is a **live
durable-data-loss defect on `master`**, not a design gap: one keystroke, no confirmation, no explicit
edit gesture, permanent overwrite of a tracked file. Deferring the *affordance design* is
defensible; leaving the *data loss* live for a whole batch is a separate decision, and the lenses are
asked to rule on it explicitly rather than to inherit it. ~~**If any lens refuses, the minimal
alternative is stated:** gate `_commit` on a non-empty delta, which also closes `UX2-C-11` and is one
predicate, no new surface, no design ruling.~~

> ### ✗ STRUCK 2026-08-27 — THE STATED MINIMAL ALTERNATIVE IS FALSE, AND IT WAS THE DANGEROUS KIND
>
> **The remedy above does not close `UX2-C-01`.** It was written by the orchestrator and never
> executed — a remedy is a hypothesis, and this one is false. **Three lenses caught it independently
> and two of them ran it:**
>
> - **security executed it:** the non-empty-delta gate is **already implemented at
>   `mapper/app.py:1393-1395`**, and the overwrite reproduces **with it in place** —
>   `erp[Sistema ERP Legacy]` → `erp[n]`, one keystroke, both `.mmd` and `.yml` rewritten, 84 of 86
>   sidecar lines. Positive control that the guard is live at all: focus + blur with no keystroke
>   writes **0 of 8**.
> - **ux executed it** on a fresh app per target: **7 of 8** focusables overwrite. It also ran the
>   obvious second candidate — clearing Textual's `select_on_focus` — which **converts destruction
>   into corruption**, still 7 of 7 written to disk.
> - **architect derived it statically:** pressing `n` *types into the focused `Input`*, so
>   `'ACTA-2011-034' → 'n'` is a **genuinely non-empty delta**. The predicate is **invariant under
>   the defect it was offered to fix** (C-40 limb 1).
>
> **Why this was worse than offering nothing.** A lens that refused the deferral and routed through
> this remedy would have implemented it, found it **already present**, and recorded `UX2-C-01` as
> closed — with the data loss untouched. **The escape hatch launders a refusal into a silent pass**,
> inside the very artifact that exists to keep the deferral honest.
>
> **What the remedy actually closes:** `UX2-C-11` / `B-31` only — and even that is now in doubt,
> since security could not reproduce `UX2-C-11`'s stated empty-delta mechanism (`insp-title` *did*
> change; the empty-delta control is 0 of 8). `B-31` inherits an **unverified observation**, not a
> diagnosed mechanism.
>
> **Both cheap fixes fail, and that STRENGTHENS the deferral rather than weakening it:** this is a
> design ruling with no cheap fix, not a cheap fix postponed. Candidate real remedies, none of them
> one-line and all needing the confirmation-affordance ruling: a **dirty-since-focus flag**
> (`Input.Changed`), or dropping `on_input_blurred` (`inspector.py:277-278`) and keeping the shipped
> `on_input_submitted` (`:275`).
>
> **Standing record, required by every lens that ruled:** `UX2-C-01` is carried as a **KNOWN LIVE
> DURABLE-DATA-LOSS DEFECT ON `master`**, with its reproduction and its two failed remedies written
> down — so the follow-on batch inherits a defect, not a discovery. `mapper/widgets/inspector.py` is
> in **no** live increment's source budget, so this batch does not touch or worsen it.

**OPERATOR RULING 2026-08-27 — the deferral is ACCEPTED AS RECORDED, with two riders:**
1. **It is named in the batch's final packet risks VERBATIM** — *"one keystroke, no confirmation,
   permanent overwrite, already fired on this repo's own fixtures."* Not paraphrased, not softened.
2. **It is the FIRST scope item of the follow-on design batch, ahead of «lente».** A live data-loss
   defect outranks a new feature in any queue. Recorded on `B-36`.

⚠ **`UX2-C-11`'s stated mechanism is WITHDRAWN, not inherited.** Security could not reproduce it:
`insp-title`'s value *did* change, `insp-notes` did *not* rewrite, and the empty-delta control is
**0 of 8**. Four writes against one value change over eight focusables means *something* writes
without a ficha delta, but it is **not** the empty-delta path and it was not isolated. `B-31`
carries it as an **unverified observation**, never as a diagnosed mechanism — a follow-on batch that
inherits the stated mechanism as fact would build a fix for a defect nobody has demonstrated.

---

## 5b · `#D28` — the contrast floor stands; the token changes *(`UX3-C-A`, operator-ruled)*

**Re-opens:** nothing sealed. **Answers:** the ux lens's blocker, which gated `Inc-1`.

`PRED-4` sets a **`4.5 : 1`** floor; its own DISCHARGE clause moved `V7`/`V8` to **`MUT`**, measured
**`4.00 : 1`** at the guaranteed rung — **a number printed four lines above the predicate that
rejects it.** Separately `#D27`'s `MUT on PANEL` measures **`3.57 : 1`**. The batch set a floor and
then picked `MUT` twice.

**Ruling — the floor stands and the token changes.**

1. **The `4.5 : 1` floor is RETAINED for readable, load-bearing text.** It is an accessibility floor;
   restating it downward to rescue a token choice is **the floor-bends-to-the-implementation defect
   this batch keeps catching**. Text at `3.57 : 1` is text fading into space.
2. **Both cited sites take `INK`** — the only free candidate clearing the floor. `ACCENT`, `ALERT`
   and `WARN` keep their single declared jobs (`LLR-S06.3.3`, `LLR-S06.3.5`).
3. **The general rule, so it is not re-derived per seat:** **`MUT` is legal for readable,
   load-bearing text only on `GROUND`** (`4.43 : 1`); **any `MUT`-on-`PANEL` readable-text seat
   escalates to `INK`** (`3.57 : 1`).
   **EXEMPT — stated explicitly so the rule cannot be over-applied and kill the dim tier:** purely
   **decorative / non-load-bearing** marks — rules, lattice dots, ground texture — carry no floor.
   `V4` (`territorio sin explorar`) stays on `WORDMARK` under this exemption.
4. **Carried to the follow-on design batch (`B-37`):** evaluate recalibrating `MUT`'s hex to clear
   `4.5 : 1` on `PANEL`, so `INK`-escalation does not erode the hierarchy ladder if more such seats
   appear. **Cost stated honestly: a `MUT` change reddens byte-identity pins tree-wide**, which is
   exactly why it is **not** done mid-batch.

---

## 6 · Forward applicability (C-49) — every output has a named consumer

| Output | Consumed by | Where |
|---|---|---|
| `#D25` + C-D25a/b/c | **`Inc-3`, `Inc-4`, `Inc-8`, `Inc-9`** packets; DDR *(set corrected — `Inc-6` is vacated)* | seat-diff declaration per packet, pinned to `bindings_for(scope)` |
| `#D26` + C-D26a/b/c | `Inc-8` (`HLR-N16.4`, `AT-053`, `TC-086`) | the scroll container and its keystroke assertions |
| `#D27` + C-D27a–e | `Inc-7` (`HLR-N13.3`, `PRED-VIS`); `Inc-1` (token set unchanged) | the sala card's painted limb |
| `#D28` + the `MUT`/`INK` rule | `Inc-1` (`PRED-4`, `V7`/`V8` → `INK`); `Inc-7` (card glyph → `INK`) | every readable-text token seat |
| §1's registry-collision finding | every artifact citing a bare `Dn`; backlog `B-34` | id disambiguation |
| §5's disposition | PDR iteration 3, all four lenses | accept / refuse the deferral |

## 7 · Seal

| Field | Value |
|---|---|
| Decisions issued | `#D25` `#D26` `#D27` `#D28` |
| Sealed decisions edited in place | **none** |
| Sealed decisions re-opened | `#D5b` (by `#D25`, scope stated; figure re-labelled a pin) |
| Open, referred | **none** — `UX2-C-01`/`UX2-C-02` ruled; deferral accepted with riders (`B-36`) |
| New backlog carries | `B-34` `B-35` `B-36` `B-37`; `B-31` mechanism withdrawn |
| Base | `master` `20f86de` |

---

## 8 · PDR ITERATION 3 — THE SEAL

**VERDICT: PASSED with conditions, all conditions DISCHARGED. The PDR is SEALED.**

| Lens | Pass-2 | Iteration 3 | Own-ledger result |
|---|---|---|---|
| architect | **REJECTED** (14/14 LIVE) | `approved with conditions` | **14 DISCHARGED, 0 LIVE** |
| qa | approved w/ conditions | `approved with conditions` | **7 DISCHARGED, 1 PARTIAL** (`PLAN.md` risk-register limb; no gate reads it) |
| security | **BLOCKED** (8 LIVE) | `approved with conditions` | **14 DISCHARGED, 4 cut w/ record, 1 carried, 0 LIVE-unaddressed** |
| ux | approved w/ conditions (10 LIVE) | `approved with conditions` | **8 DISCHARGED, 1 PARTIAL → `UX3-C-A`, 1 LIVE (`UX2-C-01`)** |

**Each lens audited its OWN condition ledger against disk (RIDER-1), never the amendment table.**

**Independently re-derived rather than inherited:** A3 blast radius **23 arg-ful sites / 10 files /
3 production** (AST); three-way AT rule **40 live, 0 failing**; `#D15` AT↔TC join **0 gaps**, with
`A-55`'s documented false gap reproduced and correctly *not* reported; supersession pins **18**;
`rows()` consumers **4 sites / 3 files, 0 outside `views/`**.

### Condition discharge — verified by RE-READING the artifact, never by trusting the pass ran (C-44)

| # | Condition | Source | Discharge |
|---|---|---|---|
| 1 | `UX3-C-A` — the `4.5:1` floor's own discharge clause measured `4.00:1` | ux | **`#D28`**: floor stands, `V7`/`V8` → `INK`; general `MUT`-on-`GROUND`-only rule + decorative exemption |
| 2 | The abolished cap survived at **3** sites | qa, architect, ux | all struck in place with `#D25` named (`:1673`, `:4549`, `:7387`) |
| 3 | `C-D25a`'s increment set wrong (named vacated `Inc-6`, omitted `Inc-8`) | qa, architect | derived set `Inc-3`/`Inc-4`/`Inc-8`/`Inc-9`; `keymap.py` added to `Inc-8`'s budget (→ 4, ⚠ declared) |
| 4 | `C-D25a` had no oracle (C-40 limb 1) | qa | declared diff bound to `bindings_for(scope)` entry/exit difference |
| 5 | §5's minimal alternative is FALSE | security, ux, architect | **struck**, with all three executions recorded |
| 6 | `C-D26b` unscoped manufactures a false-fail | qa | scoped to `HLR-N16.4`/`AT-053`; `scroll_to` legal as a harvesting mechanism |
| 7 | `PRED-VIS` glyph unbound to `declared_vocabulary` | qa | membership clause added, `C-D27b` left intact |
| 8 | `LLR-REPAIR.1` threshold written for a one-phantom fixture | security (`S-24`) | restated as **set equality over N phantoms**; `M-REPAIR.1-c` named |
| 9 | `C-D27e` legibility arm missing | ux | added at 118 × 34, against the background actually painted |
| 10 | `B-34`/`B-35` cited but non-existent | architect | landed, with `B-36`, `B-37` |
| 11 | `UX2-C-11`'s mechanism unreproduced | security | **withdrawn** on `B-31`; carried as an unverified observation |
| 12 | §5.3 criterion 8 cited its own rejected mutant | qa (`QA3-C-06`) | census restated as an **AST** walk; the missing criterion 6 recorded as known |

**Carried, NOT discharged, by decision:** `B-36` (`UX2-C-01`) — a **known live durable-data-loss
defect on `master`**, deferral accepted with the operator's two riders. `B-33` (`S-15`/`S-20` cost).
`QA2-C-02`'s `PLAN.md` limb (R-1 sizing; no gate reads it).

| Seal field | Value |
|---|---|
| Sealed | 2026-08-27 |
| Verdict | **PASS — proceed to implementation** |
| Participants | architect · qa-reviewer · security-reviewer · ux-reviewer (fresh, parallel) · orchestrator |
| Approved ids | `#D25` `#D26` `#D27` `#D28` + all decisions sealed at the original PDR |
| Lens artifacts | `02h-pdr3-{architect,qa,security,ux}.md` |
| Baseline at seal | **630 + 17 = 647 pass**, ruff 29, `fixtures/` clean |
| Live requirement census | **21 HLR / 52 LLR**, 40 live `AT`, 0 failing the three-way rule |
| Next station | **P3 — implementation.** Nine increments, not started. |
