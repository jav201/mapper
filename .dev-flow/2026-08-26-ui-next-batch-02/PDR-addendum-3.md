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
  Applies to `Inc-3` (4 rows), `Inc-4` (3 rows), `Inc-6`, `Inc-9`. **A pin per diff, no global cap** —
  a global cap would price a well-cut increment against an unrelated one's spending.
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
- **C-D26c — deferral is recorded as a carry, not dropped.** Backlog `B-35`.

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
asked to rule on it explicitly rather than to inherit it. **If any lens refuses, the minimal
alternative is stated:** gate `_commit` on a non-empty delta, which also closes `UX2-C-11` and is one
predicate, no new surface, no design ruling.

---

## 6 · Forward applicability (C-49) — every output has a named consumer

| Output | Consumed by | Where |
|---|---|---|
| `#D25` + C-D25a/b/c | `Inc-3`, `Inc-4`, `Inc-6`, `Inc-9` packets; DDR | seat-diff declaration per packet |
| `#D26` + C-D26a/b/c | `Inc-8` (`HLR-N16.4`, `AT-053`, `TC-086`) | the scroll container and its keystroke assertions |
| `#D27` + C-D27a/b/c/d | `Inc-7` (`HLR-N13.3`, `PRED-VIS`); `Inc-1` (token set unchanged) | the sala card's painted limb |
| §1's registry-collision finding | every artifact citing a bare `Dn`; backlog `B-34` | id disambiguation |
| §5's disposition | PDR iteration 3, all four lenses | accept / refuse the deferral |

## 7 · Seal

| Field | Value |
|---|---|
| Decisions issued | `#D25` `#D26` `#D27` |
| Sealed decisions edited in place | **none** |
| Sealed decisions re-opened | `#D5b` (by `#D25`, scope stated; figure re-labelled a pin) |
| Open, referred | `UX2-C-01`, `UX2-C-02` → PDR iteration 3 |
| New backlog carries | `B-34` (bare-`Dn` ambiguity), `B-35` (tabbed legend) |
| Base | `master` `20f86de`; batch branch `docs/amendment-set-3` |
