# 02h · Security lens — PDR iteration 3 (final), batch `2026-08-26-ui-next-batch-02`

> **Base:** `94ad8d3` (branch `docs/amendment-set-3`) · **Instrument:** my own pass-2 ledger
> (`02e`), audited item-by-item against DISK. **Not** the amendment table, and **not** `02g`'s
> discharges — the 11 discharges recorded there were re-executed here from scratch, not inherited.
>
> **Working-tree discipline.** Three lenses read the tree concurrently. No file under `mapper/`,
> `tests/` or `fixtures/` was modified. Every probe ran against a `git archive HEAD` export in the
> system temp directory; every `MapStore`/`MapperApp` was rooted at a `tempfile.mkdtemp()`
> workspace. `fixtures/` was copied, never opened for write. **Fixture integrity verified by
> sha256 before and after every app-level probe — all three files MATCH**, and
> `git status --short fixtures/` is empty.
>
> **A correction to my own pass-2 instrument, first.** `02e` §1 says *"3 blockers · 3 majors"*;
> `grep -c "\[major\]"` returns **2** (`S-19`, `S-20`), and `02e`'s own evidence checklist and
> closing note both say two. `02g` §2 caught this. **The roll-up over-counted by one; the body was
> right.** Adopted.
>
> **A second correction, and it matters more.** `02g` §0 recorded that `01-requirements.md` had not
> been edited since the lenses wrote, so every `02e` line citation still resolved. **That is no
> longer true at this base** — amendment set 3 landed. `LLR-N13.1.5`, cited in `02e` at `:2391`, is
> now at `:3060`. **No line citation in `02e` is inheritable.** Every address below was re-derived.

---

## 1 · VERDICT

> ### `approved with conditions`
>
> **All three of my pass-2 blockers are lifted on executed evidence.** `S-16` closes (0 leaks over
> 15 derived positions, positive control fires). `S-17` resolves — and the resolution is better
> than the repair I demanded. `S-18`/`S-19` are CUT under `#D24` by operator re-scope, and their
> deferral is recorded honestly, which is all I was asked to audit.
>
> **19 of 19 of my items are addressed. Zero remain LIVE-unaddressed.** 14 discharged, 4 cut with
> an honest deferral record, 1 (`S-20`) closed as a requirement with the defect explicitly
> unrepaired and carried as `B-33` — which is the disposition the standing decision names.
>
> **The two defects this batch owns are real, are present today, and are adequately specced.**
> `S-22` and `S-23` both reproduce at this base; `LLR-REPAIR.1` and `LLR-REPAIR.2` each carry a
> statement, a numeric threshold, an owning increment (`Inc-REPAIR`, sequenced before `Inc-7`), an
> `AT`, a `TC`, and named weaker variants that redden the naive fix. `LLR-REPAIR.2`'s
> sentinel-based threshold is the strongest single requirement in this batch.
>
> **What I am conditioning on is one thing, and it is authored in this batch's own artifact.**
> `PDR-addendum-3` §5 offers, as the minimal alternative if a lens refuses the `UX2-C-01` deferral,
> *"gate `_commit` on a non-empty delta"*. **That predicate is already implemented on `master` at
> `mapper/app.py:1393-1395`, and I reproduced `UX2-C-01` with it in place.** The offered remedy is
> invariant under the defect it is offered against. A refusal routed through it would be
> implemented, found already present, and recorded as closed while the data loss stayed exactly as
> live as it is today. **That converts a refusal into a silent pass, and it is the most dangerous
> shape in the batch.**
>
> Four conditions, §6. None is a design question; each is one edit.

---

## 2 · My 19 items, audited against disk

Statuses re-derived. Where I assert an absence, the positive control is named in the same row.

| # | Item | Status | Executed evidence at `94ad8d3` |
|---|---|---|---|
| **C-1** | cycle- and depth-safe traversal | **DISCHARGED** | Re-executed, `recursionlimit=2000`: `LayeredRenderer.render` on chains of depth 500 / 1500 / 3000 / 20000 → **OK, 0 `RecursionError`**. 3-cycle → refused with `ValueError`. **Positive control:** leaf count for `b=3 d=7` returns **2187** (expected 2187) — the rewrite is memoised, not capped, so the absence of a crash is not the absence of work. |
| **C-2a** | store-boundary coercion over **derived** positions | **DISCHARGED** | Poisoned each of the 15 positions I derive from the model (`_text_fields` over `Ficha` 4 / `Attachment` 3 / `SchemaField` 3 / `Document` 4, plus the node-id dict key) with a coercible non-`str`. **0 LEAKS / 15.** **Positive control:** `Attachment(kind=1,…)` constructed *without* the ladder → `.kind` is not `str`, so the detector fires on a real leak. Threshold-2 arm re-run: a container field lands `''` (not the repr `'{…}'`), appends `campo ilegible: a.acta`, and `coverage()` returns `(0, 2)` — the miscount does not survive its own fix. |
| **C-2b** | `LLR-STO.1.1` exists as a requirement | **DISCHARGED — as a cross-batch reference (`A-57`)** | See §4. The target block is on disk at `.dev-flow/2026-08-27-repair-batch-02/01-requirements.md:114` with a statement, four thresholds, `AT-P01`–`AT-P03`, `M-STO-a`/`M-STO-b`, and executed verification. |
| **C-3** | `HLR-N13.3` mount budget | **CUT (`#D24`) — deferral honestly recorded** | Thresholds 1 and 2 struck **in place** with `#D24` annotations (`:3451`, `:3454`); `AT-048` **deferred, not deleted** (`:2907`, `:5303`); mutants `M-H2`/`M-H3`/`M-H5` carried **named** (`:3514`–`:3516`); traceability row (`:5381`) carries the deferral. Threshold 4 re-scoped from *"over budget"* to *"fails to load"* and survives whole. Per the standing decision I audit the record, not the defect. **The record is honest.** |
| **C-4** | `COERCION_RANGES` replaces *"0 control bytes"* | **DISCHARGED** | The list is now owned by a first-class requirement — `HLR-COERCE` §3.0 / `LLR-COERCE.1` (`:540`, `TC-080`) — declared once in `mapper/darkside.py`, referenced by the surface thresholds at `:1985` (canvas), `:3313` (home cards), `:3943` (legend), `:4477`. §3.0's own honesty note stands: `grep -rn COERCION_RANGES mapper/` returns nothing and it is declared a Phase-3 obligation (`:411`), not asserted as shipped. |
| **C-5** | widen to every file-derived string; row-length clause | **DISCHARGED** | `LLR-N16.2.3` at `:4456` carries the row-length clause (`:3943` *"row length equals"*). `LLR-N14.2.3` is **deferred with its story** (`#D23`, `:3921`) — see the orphan check in §5. |
| **C-6** | lens predicate / case rule / bounds; `Q-8` | **CUT with US-N14 (`#D23`)** | `LLR-N14.1.4` deferred at `:3724`, traceability row struck at `:5386`. The surface it governed is cut with it, so nothing is orphaned. |
| **C-7** | derived census; pre-existing sinks in scope | **DISCHARGED** | Re-read at `:1991`–`:2007`: the old wording is struck **in place**, scope is *"every file-derived string painted on a surface this batch touches, whether its sink is new or pre-existing"*, the census **shall assert its own input set is non-empty**, and `layered._fit` is named in scope with five uncoerced emit sites. `M-N06.2.3-a` is reddened by the census, not by the LLR's own fixture. |
| **C-8** | `markup=False` + `plain()` on `notify` | **DISCHARGED** | AST census independently re-derived on my own walker over `mapper/**/*.py`: **30 total / 19 non-literal / 0 with markup enabled / 15 not routed** — identical to `A-18`, and the 15 addresses resolve (11 in `app.py`, 4 in `screens/factory.py`). |
| **C-9** | `dots`/`bgs` as a token set with a fallback | **DISCHARGED** | `LLR-CNV.1.4` at `:1310`; statement requires the value be a token from the declared set and that `rows()` paint an out-of-set tone in a **declared fallback tone** — validation at the one convergence point. |
| **C-10** | coercion extended to the SVG export sink | **DISCHARGED** | `LLR-CNV.2.1` at `:1442`; `:1513` — the exported SVG shall contain no code point in `COERCION_RANGES`, sharing the §3.0 list. |
| **C-11** | cached metrics read for `list_maps` | **DISCHARGED** | `LLR-N13.1.6` at `:3150`; requires the sala draw thumbnails **without reindexing**, and correctly records that the warm figure (253.5 ms vs cold 1 064.2 ms) is fast only because the text hash matches — a warm measurement is not evidence the mount is cheap. |
| **C-12** | `F-m4` disposition | **DISCHARGED, and the carried arm now has an owner** | `A-58` gives the alias-bomb-under-`nodes:` arm a real home: `LLR-N13.1.7` (`:3245`), `TC-088`, owned by `Inc-REPAIR`, with an **un-aliased control mandated** because reusing the existing bomb fixture under an unread key is green forever. |
| **S-11** | `load` raises only `MapStoreError` | **DISCHARGED, both halves** | **Code:** 19 hostile sidecars (non-mapping yml, scalar `nodes:`, broken syntax, non-list `schema`, scalar attachment entries, int node id, 60-deep nesting bomb, alias fan, …) → **0 leaks of a non-`MapStoreError`**. **Positive control:** calling the inner builder unguarded raises `AttributeError`, so the leak detector is live. **Requirement:** the repair batch's `LLR-STO.1.1` threshold 3 states it verbatim. |
| **S-16** | coercion covers only 2 of 5 position families | **CLOSED** | Superseded by C-2a's census above: 0 leaks over every derived position, including the three families I reported uncovered at pass 2 (`Attachment` `kind`/`path`/`caption`, `SchemaField` `key`/`label`/`kind`, and the node id — the latter now coerced at the dict key, `nodes` ids came back `['777','a','b']` from an int key). |
| **S-17** | `LLR-STO.1.1` does not exist | **RESOLVED** | See §4. **Positive control on the census regex:** `grep -rnE '^#+ .*LLR-STO' .dev-flow/` returns the repair batch's heading at `:114` **and** `A-57`'s own amendment heading in this document — the same pattern that found nothing at pass 2 now finds two things, so the probe discriminates rather than merely reporting silence. |
| **S-18** | the work budget declares the stall, bounds nothing | **CUT (`#D24`), paired with `S-19`** | `A-43` (`:6798`) and the §3.7 block at `:3364`. Deferral record verified honest. Not re-raised, per the standing decision. |
| **S-19** | the 51-node fixture is under budget on `RadialRenderer` | **CUT (`#D24`) as `S-18`'s PRECONDITION** | `:3366` states the pairing and the precondition relation explicitly, which is the correct reading — it was my finding and the document states it more sharply than I did. Not re-raised. |
| **S-20** | three `MAX_RENDER_NODES`, three private walks, `children_of` O(E) | **CLOSED as a requirement · defect explicitly NOT repaired** | `A-59` (`:7271`) and `:3427`–`:3446`. The record states in the same breath what is *not* fixed, cross-references `B-33`, re-measures `children_of` as O(E) per call and O(N·E) through `Graph.focus`, and writes *"deferring a bound does not repair a defect"* twice. `:7593` carries the roll-up row. **This is exactly the honest record the standing decision asked me to audit for, and it is present.** |
| **S-21** | the IFC declares coercion at one flow node | **DISCHARGED** | `A-60` (`:7289`) promotes the coercion node to a **class** applying to every flow whose SOURCE includes file-derived text (`:4846`–`:4855`), with surface thresholds `LLR-N06.2.3` (`canvas_paint`) · `LLR-N13.2.1` (`home_cards`) · `LLR-N16.2.3` (`legend`). **The one flow still declaring no coercion is `match_set`, and I verified that absence is CORRECT** — see §5. |

**Score: 14 discharged · 4 cut with an honest deferral record · 1 closed-with-defect-carried. 0 live-unaddressed.**

---

## 3 · The two defects this batch owns — verified present, then verified specced

### `S-22` — the phantom sidecar node · `B-29` / `LLR-REPAIR.1` · **PRESENT · ADEQUATELY SPECCED**

**Positive control first**, per the C-55 rider — because the finding is an *absence* (`warnings == []`),
and an absence is admissible only if the same probe can produce a non-absence:

```
POSITIVE CONTROL (a container field, known-refusable)
    load_warnings = ['campo ilegible: a.acta']      -> the probe CAN observe a non-absence
```

Only then the case. Sidecar declares `ghost`; the `.mmd` defines only `a` and `b`:

```
    graph.nodes ids       = ['a', 'b', 'ghost']
    coverage()            = (2, 3)
    baseline, no phantom  = (2, 2)        DELTA in the denominator = +1
    load_warnings         = []            <== EMPTY
    app.py:459 predicate `if graph.load_warnings:` -> False
```

**The reported shape is right: `+1`, not the doubling an earlier pass argued.** `load_or_notice`'s
warning arm never fires and `LLR-N13.1.5`'s containment never engages, because there is no failure
to contain. This matches `LLR-REPAIR.1`'s own declared pre-state at `20f86de` — *"`coverage() = (2, 3)`
with `warnings = []`"* — exactly, on an independently written harness.

**One sharpening, and it is not a blocker.** Measured with **ten** phantom ids: `coverage() = (0, 12)`
against a 2-node map — the inflation is **+1 per phantom id, unbounded**, not capped at +1.
`LLR-REPAIR.1`'s *statement* quantifies correctly (*"When the sidecar declares a node id…"*, which
applies per id). Its **numeric threshold** does not: *"`len(graph.load_warnings) >= 1` and the
offending id appears in one of them"* is written for the single-phantom fixture, and a variant that
warns for the first phantom and stays silent about the rest passes it. Filed as `S-24`, **minor** —
containment engages either way once the list is non-empty, so the operator is told. One clause fixes
it (§6, condition 4).

**Spec adequacy: PASS, and better than the condition asked for.** Statement ✓ · numeric threshold
with a declared executed pre-state ✓ · owning increment `Inc-REPAIR`, sequenced **before `Inc-7`**
(`:5587`, `:5635`) ✓ · `AT-049` ✓ · `TC-082` (`:5401`) ✓ · two named weaker variants ✓. Three
clauses deserve naming:

- **`M-REPAIR.1-a`** — validate the new warning against the existing `legacy` fixture. Green,
  because `legacy` has no phantom. The requirement names this as *"an absence admitted as evidence
  with no positive control proving the oracle can produce a non-absence"* — the C-55 rider written
  into a requirement, correctly.
- **`M-REPAIR.1-b`** — drop the phantom instead of warning. The denominator becomes correct and the
  card looks healthy. Reddened by the damaged-card-state clause.
- **The synthetic fixture is MANDATED, and `fixtures/` is prohibited by name**, citing `02g` §6.
  **No fixture in the repository carries a phantom sidecar id**, so `LLR-N13.1.5`'s containment arm,
  `AT-025b` and this threshold are all green over an empty set without it. That is `C-55` limb 2
  applied to the batch's own gate, and it is the load-bearing clause.
- **`coverage()`'s semantics are explicitly out of scope** — *"the defect is silence, not
  arithmetic"* — because three call sites agree on its meaning and `LLR-N13.1.3` pins one at 100.
  Correct: a semantics change riding inside a defect fix would redden an unrelated requirement.

### `S-23` — the absolute path in an operator toast · `B-30` / `LLR-REPAIR.2` · **PRESENT · ADEQUATELY SPECCED**

The brief asked me to verify the username **actually reaches a rendered surface** rather than assume
it. Executed against a store rooted under the real home directory:

```
store.load('no-such-map') -> MapStoreError
  str(exc)                 contains the OS username : True
  darkside.plain(str(exc)) contains the OS username : True     <== survives the coercion helper
  the path is absolute                              : True
  rendered, username REDACTED:  Map not found: C:\Users\<USER>\.mapper-probe-ws\no-such-map.mmd
```

**Discriminating control** — the *repaired* arm four lines below it (`store.py:468`,
`UnicodeDecodeError`):

```
  str(exc) = 'no se pudo leer bad: UnicodeDecodeError'
  contains a path separator : False       contains the username : False
  -> the probe DISTINGUISHES the two arms: True
```

So the probe is not reporting a property of every message; it separates the leaking raise from the
repaired one. `mapper/store.py:456` is the leak; the comment asserting the class was closed is at
`:458`–`:462`. **The comment is true about the reads it describes and false about the line above it.**

**Spec adequacy: PASS — this is the sharpest threshold in the batch.** Statement ✓ · `AT-050` ·
`TC-083` · `Inc-REPAIR` ✓. The threshold is **sentinel-based**: 0 occurrences of the workspace path,
**of any of its components**, and of the platform separator; the map id appears exactly once —
*"the assertion is on the sentinel, not on the literal word 'path'"*. And `M-REPAIR.2-a` (interpolate
the **basename**) is named as the fix an implementer reaches for first: it removes the username and
reads as repaired, is **not** reddened by the separator clause, and is reddened instead by the
id-appears-exactly-once clause on the `<id>.mmd` form. That is a requirement that anticipated its
own near-miss.

---

## 4 · `A-57` — does ONE reference genuinely resolve all FOUR?

The brief's question is the right one: this is exactly where a fold drops one. **Audited: it
resolves three of the four outright, the fourth is resolved with a residue, and the residue was
separated out and given its own owner rather than absorbed.**

**First, the premise is true on disk, not merely asserted.** The target exists:

```
$ grep -rnE '^#+ .*LLR-STO' .dev-flow/
.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:7225  <- A-57's own amendment heading
.dev-flow/2026-08-27-repair-batch-02/01-requirements.md:114    <- THE REQUIREMENT
.dev-flow/2026-08-27-repair-batch-02/03-increments/increment-001.md:1
```

`:114` carries a statement, a **derived** position set (*"a test that hand-lists positions is
rejected"*), thresholds 1–4, `AT-P01`–`AT-P03`, `M-STO-a`/`M-STO-b`, and executed verification
against `tests/test_repair_store_boundary.py`. **It is a real requirement.**

| Folded item | Resolved by the reference? | Basis |
|---|---|---|
| `S-17` — the id is phantom | **YES, outright** | The id is not phantom; it is a cross-batch reference that was never *declared* as one. My pass-2 diagnosis was right about the symptom and wrong about the cause. |
| `C-2b` — coercion over derived positions | **YES, outright** | Threshold 1 quantifies over the derived position set. Independently executed here: 0 leaks / 15 positions, positive control fires. |
| `QA2-C-03` — 4 prose refs, 0 headings | **YES, outright** | The complaint was a missing reference declaration. A-57 supplies one naming the definition site, the statement, the thresholds and the shipped suite. |
| `S-11` — `load` raises only `MapStoreError`, fixture set derived | **YES for the stated substance; NO for one carried arm** | Threshold 3 states it verbatim, and 0 of 19 hostile inputs leak. **But** the YAML-bomb-under-`nodes:` arm, which `02e` `C-12` folded into `LLR-STO.1.1`'s fixture set, is **not** covered by it. |

**The residue was caught, and that is the finding.** `A-58` states it in terms: *"This is the one
thing the `LLR-STO.1.1` reference does NOT discharge, and separating the two is why the reference
could be taken safely."* It gives the arm `LLR-N13.1.7` (`:3245`), `TC-088`, `Inc-REPAIR`, and a
**mandated un-aliased control** — because reusing the existing bomb fixture under an unread key
measures PyYAML's alias sharing rather than this code path, and is green today and green forever.

**Ruling: `A-57` is a sound fold, not four findings collapsed into one.** It is a fold that named
its own residue and paid for it separately, which is the opposite of the failure mode.

**And I adopt A-57's correction of my own condition.** I demanded the block be authored in this
document. Executed, that would have put **two headings under one id that shipped code cites
normatively in six places** — `grep -rn 'LLR-STO' mapper/` returns 6 hits in `mapper/store.py` — and
the code would obey whichever copy the reader found first. That is the two-live-definitions defect
`#D6` and `#D14` removed, reintroduced at higher stakes. **The briefed fix would have made it
worse.** A-57's anchored-census rider (`^#{4,5} \`?(HLR|LLR)-`) is also correct and I used it here.

One over-claim A-57 declines to make, correctly: `MapStoreError` is a bare `Exception` subclass and
both real `load` callers catch bare `Exception` (`app.py:453`, `:1181`), so the typed refusal changes
the operator's **message**, not crash-resistance at any existing call site. Verified.

---

## 5 · `PDR-addendum-3` — security review

### 5.1 · `#D27` — is a failure state in the "absent information" pairing acceptable? · **ACCEPTED, with `C-D27d` promoted to a gate**

**First, the premise is true today.** Executed on a synthetic two-map workspace:

```
  sano_vacio   loads OK   nodes=0  warnings=[]
  roto         RAISES MapStoreError: no se pudo leer la ficha de roto: …

  roto       painted row, non-name cells = [' concept ', '0', '0', 'None', 'None', 'None', 'None']
  sano_vacio painted row, non-name cells = [' concept ', '0', '0', 'None', 'None', 'None', 'None']
  BYTE-IDENTICAL apart from the name: True
```

`A-69` is confirmed independently. A map that **failed to load** and a map that is **empty and
healthy** paint the same bytes; the only thing separating them is a toast that is gone in seconds.

**Ruling: the glyph is the right call and I accept it. The pairing is not the problem — the
discriminator is.** Three reasons, in order of weight:

1. **`#D27`'s refusal to spend `ALERT` is correct, and the reasoning is the good kind.** `ALERT`
   looks free only because US-N14's malformed-query chip is **cut, not cancelled**. Spending it here
   means the follow-on batch reinstates the chip into a token with two jobs, at which point
   `LLR-S06.3.5`'s one-job census can no longer adjudicate `ALERT` at all. That is `C-55` limb 2 by
   name — an emptiness that is an accident of today's scope — and ruling on it would cost the
   follow-on batch a defect this batch would never see. **I would have made the same call.**
2. **In this view the glyph, not the colour, is the carrier.** The sala vocabulary is already
   glyph-led (`⇄` V17, `◍` V18, `▲` V20, `█`/`░` V19, `∙` V21) with colour secondary in every one.
   `PRED-VIS` says *"a declared token **or glyph**"*. A glyph is scanned; a card that differs only in
   text differs only to someone already reading it.
3. **`MUT on PANEL` as the pairing is defensible on a narrow but real argument** — a map that cannot
   be summarised genuinely *is* an absence of information at the card's own level of description,
   and reusing a shipped pairing beats inventing a role. I record my reservation: a failure and an
   absence are not the same event to an operator, and the tone will not distinguish them. **I accept
   it only because the glyph carries the distinction.** If the glyph is dropped or made subtle, this
   ruling does not survive.

**Condition (§6, condition 3): `C-D27d` must be a THRESHOLD with a positive control, not a note.**
As written it says *"`roto` vs `sano_vacio` must now differ in the painted row"*. That is the right
property and it has no oracle. It needs the one I just ran: assert the painted non-name cells of
`roto` differ from `sano_vacio`'s, **with `sano_vacio` retained as the known-healthy control** so the
arm cannot pass by both rows changing. Without it, `#D27` ships the same invisibility with a glyph
nobody asserted — and `A-45` already records what a hand-checked count costs here.

**A compounding I raise as new.** For the `roto` class above, a toast *does* fire (the load raises).
For the **`S-22` phantom class there is no toast at all** — `warnings == []`, nothing raises. So for
that class the glyph is not the *durable* signal, it is the **only** signal, and it is unreachable
until `LLR-REPAIR.1` makes the warning arm fire. **`LLR-REPAIR.1` is therefore a hard precondition
for `#D27` being non-vacuous, not merely for `AT-025b`.** The batch already sequences `Inc-REPAIR`
before `Inc-7` (`:5587`) and `:4602` states the dependency — **correct as sequenced**; I record the
second reason it matters.

### 5.2 · `UX2-C-01` — the deferral · **RULING: the affordance deferral is ACCEPTED. The stated minimal alternative is REFUSED — it does not work.**

**The defect is real and I reproduced it, on a temp copy, at this base.** One keystroke:

```
  BEFORE  insp-title.value       = 'Sistema ERP Legacy'
  BEFORE  .mmd first data line   = '    erp[Sistema ERP Legacy]'
  AFTER   insp-title.value       = 'n'
  AFTER   .mmd first data line   = '    erp[n] --> fin[Finanzas]'

  keystrokes to permanent loss : 1        confirmation prompts shown : 0
  explicit edit gesture needed : none (focus alone arms it)
  .mmd changed on disk : True   .yml changed on disk : True   (84 of 86 sidecar lines)
```

That is `02g` §6's fixture corruption, reproduced deliberately and safely. **`UX2-C-01` is a live
durable-data-loss defect on `master`.** The batch's own record says so and refuses to call the
deferral cost-free; that honesty is why this is a condition and not a block.

**The decisive finding, and it is new.** `PDR-addendum-3` §5 states: *"If any lens refuses, the
minimal alternative is stated: gate `_commit` on a non-empty delta, which also closes `UX2-C-11` and
is one predicate, no new surface, no design ruling."*

**That predicate is already on the tree**, at `mapper/app.py:1393-1395`, in the sole consumer of
`FichaInspector.FieldCommitted`:

```python
current = self._ficha_value(node.ficha, event.field)
if current == event.value:
    return
```

And the overwrite above was produced **with it in place**. It is **invariant under the defect**
(C-40 limb 1): after the keystroke the delta is genuinely non-empty, so the predicate passes and the
write proceeds. **Positive control that the guard is live at all** — focus then blur with **no**
keystroke, across all 8 focusable `Input`s: **0/8** sidecar writes. The guard works. It simply does
not address `UX2-C-01`.

**Why this is worth a condition rather than a footnote.** The addendum offers this predicate as the
escape hatch for a refusing lens. A lens that refuses, routes through it, and has it implemented
would get: *"already present — closed"*, with the data loss untouched. **The escape hatch converts a
refusal into a silent pass.** That is authored in this batch's artifact, now, and it is the one thing
here I will not let stand.

**Corollary — `UX2-C-11` does not reproduce as stated.** It claims `_commit` rewrites the sidecar on
blur *"even when the delta is empty (`insp-title`, `insp-notes` show `SIDECAR REWRITTEN=True` with no
value change)"*. Measured: `insp-title`'s value **did** change (to `'n'`), `insp-notes` did **not**
rewrite, and the empty-delta control is 0/8. My 8-focusable walk shows 4 sidecar writes against 1
value change, so *something* writes without a ficha delta — but it is **not** the empty-delta commit
path, and I did not isolate what it is. **Recorded as an unverified observation, not a finding.**
`B-31`/`B-32` must not inherit `UX2-C-11`'s stated mechanism as fact, or the follow-on batch designs
against a defect that is not there while the real one stays live.

**What I accept, and what I require.** The *affordance design* — explicit edit gesture, confirmation
model, undo surfacing — is genuinely a design question and belongs with US-N14 in the follow-on
batch. **Deferral of the design: ACCEPTED.** What I require is that the deferral record name a
remedy that is not invariant under the defect. There are two, each one line, each needing no design
ruling and no new surface:

- gate the commit on **"the operator edited this Input since it took focus"** — a dirty flag set by
  `Input.Changed` — rather than on a delta against the model; or
- **do not commit on blur at all**: drop `on_input_blurred` (`mapper/widgets/inspector.py:277-278`)
  and keep `on_input_submitted` (`:275`), which already exists. Blur then discards, `enter` commits.

Either makes the edit gesture explicit, which is the actual property `UX2-C-01` is about.
**Recommendation, not a gate:** the second is one deleted method, `Inc-REPAIR` already exists as this
batch's defect-repair increment, and the file is not `store.py` so there is no owner collision. Where
it lands is the operator's call; **that it be named correctly is mine.**

### 5.3 · The "new string → rendered or persisted surface" lens across the batch's scope

Trigger family **C-17**. No new external endpoint, no MCP/Composio/n8n surface, no network I/O — the
blast radius stays local rendering of local files. Enumerated against the current tree:

| Surface | Owning threshold | Covered? |
|---|---|---|
| US-N06 fold pill / overflow declaration | `LLR-N06.2.3` (`:1972`), coercion class at `:4850` | **YES** — and `layered._fit`'s five uncoerced emit sites are named in scope by C-7's census. |
| US-N07 hit counts | `match_set` (`:4775`) — **no coercion node** | **CORRECTLY UNCOVERED.** Verified rather than assumed: the flow's `SINK` is *"the `#map-canvas` widget (**tone only**) and the count line"*, and its nodes carry `list[str]` of node ids into a `frozenset[str]` used to select **tone**. No file-derived text is painted through this flow. The absence is right, not a drop. |
| US-N13 sala cards | `LLR-N13.2.1` (`:3301`), `home_cards` flow declares `darkside.plain` at `:4835` | **YES** |
| US-N16 legend rows | `LLR-N16.2.3` (`:4456`), row-length clause at `:3943` | **YES** |
| Toasts, product-wide | `LLR-N06.2.5` (`:1873`), AST-derived census | **YES** — re-derived 30/19/0/15. |
| Exported SVG | `LLR-CNV.2.1` (`:1442`) | **YES** — `:1513`. |
| Store boundary (all 15 derived positions + node id) | cross-batch `LLR-STO.1.1` | **YES** — 0 leaks executed. |

**The US-N14 cut did not orphan a coercion obligation.** `LLR-N14.2.3` is deferred with its story
(`#D23`), and its traceability row states the disposition explicitly: *"the coercion **class** stays:
`HLR-COERCE` (§3.0) owns it"* (`:5392`). The class survives the cut with its own HLR, `LLR-COERCE.1`
and `TC-080`. **The surface and its obligation left together.** That is the check I most expected to
fail, and it holds.

### 5.4 · `#D25` and `#D26` — no security consequence

`#D25` (seat-diff figure is a pin on `Inc-4`'s diff, not a global budget) touches key bindings only;
no new sink, no new persistence, no new authority. Its enlarging half (`C-D25a`, a per-increment seat
diff declared in the packet) is a net gain in auditability. `#D26` (scrolling legend, tabbed deferred)
is layout; `C-D26a`'s *"set equality asserts over CONTENT, never over visible rows"* and `C-D26b`'s
*"real keystrokes, not `scroll_to(...)`"* are both the correct oracle discipline. **No objection.**

### 5.5 · Hygiene

| Check | Result |
|---|---|
| Tracked secrets | `git ls-files \| grep -iE '\.env\|credential\|secret\|\.pem$\|\.key$\|token'` → **empty** |
| `.gitignore` coverage | `.env`, `.env.*`, `*.db`, `.mapper/`, `*.svg`, `*.png`, `scratch/`, `prototypes/`. `fixtures/mapper.db` confirmed ignored by `*.db` and **untracked** (`git ls-files fixtures/` returns the two text files only). |
| New dependencies | `git diff 20f86de..HEAD --stat -- pyproject.toml` → **empty**. No new package, no install script, no supply-chain surface. |
| New external tool / integration | **None.** No MCP, Composio, n8n, HTTP client or credential store enters this batch. Scope and blast radius unchanged: local rendering of local files. |
| Secret values in this artifact | None. The one path disclosed is written with the username replaced by `<USER>`. |
| Corrupted tokens spelled verbatim (C-56) | None. Mutations described by position and operation. |
| Fixture integrity | sha256 before/after every app probe: `legacy.mmd`, `legacy_nodos.yml`, `mapper.db` all **MATCH**; `git status --short fixtures/` empty. |

---

## 6 · Conditions

Four. None is a design question; each is one edit. They gate the artifact, not the increments.

1. **Correct the stated minimal alternative in `PDR-addendum-3` §5.** *"Gate `_commit` on a non-empty
   delta"* is already implemented at `mapper/app.py:1393-1395` and is invariant under `UX2-C-01`
   (reproduced with it in place; empty-delta control 0/8). Replace it with a remedy that makes the
   **edit gesture** explicit — a dirty-since-focus flag, or dropping `on_input_blurred` at
   `mapper/widgets/inspector.py:277-278` and keeping `on_input_submitted` at `:275`. **This is the
   load-bearing condition:** an escape hatch that is already satisfied turns a lens refusal into a
   silent pass.
2. **Re-derive or withdraw `UX2-C-11`'s stated mechanism before `B-31`/`B-32` inherit it.** The
   empty-delta commit does not reproduce (0/8). Something writes without a ficha delta (4 writes / 1
   value change over 8 focusables) and it was not isolated — record that as open and unexplained, the
   way `A-73` correctly recorded `UX2-C-12`'s double-fire.
3. **Promote `C-D27d` from a note to a threshold with a positive control.** Assert the painted
   non-name cells of a `roto` card differ from a `sano_vacio` card, retaining `sano_vacio` as the
   known-healthy control so the arm cannot pass by both rows changing. Today they are byte-identical.
4. **`LLR-REPAIR.1` threshold: quantify over every phantom id** (`S-24`, minor). Measured: 10
   phantoms inflate the denominator by 10. The statement is already right; the numeric threshold is
   written for the one-phantom fixture and a warn-once-then-silent variant passes it.

**What I am explicitly NOT conditioning on:** `S-18`, `S-19` (cut, `#D24` — deferral record verified
honest); `S-20` (closed as a requirement, defect carried as `B-33` — recorded honestly, and the
record says *"deferring a bound does not repair a defect"* in the requirement itself); the
`ViewState`/`IRenderer` and `Canvas` interface changes, which I approved at `02b` and still approve.

---

## 7 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Each finding has what · where · why · recommendation | ✓ | §3 (`S-22`, `S-23`, `S-24`), §5.1 (`#D27`), §5.2 (`UX2-C-01`), §6 |
| Each finding has a severity | ✓ | `S-22` major · `S-23` minor · `S-24` minor · `UX2-C-01` **HIGH, live on `master`** · the false remedy in §5.2 **HIGH, authored in this batch** · `#D27` visibility major |
| No secret value appears in this output | ✓ | The one disclosed path is written `C:\Users\<USER>\…`; the username is never spelled. Tracked-secret scan empty; `.gitignore` covers `.env`, `.env.*` |
| Verdict is explicit | ✓ | §1 — `approved with conditions` |
| New tool/integration scope and blast radius addressed | ✓ | §5.5 — **none added**; no dependency change; blast radius unchanged (local rendering of local files) |
| Every asserted absence carries a positive control | ✓ | `S-22` (container field produces a warning) · `S-11` (unguarded inner call raises `AttributeError`) · `S-16` (ladder-free `Attachment` leaks) · `C-1` (leaf count = 2187) · `S-17` (the same regex finds two headings) · `S-23` (the repaired arm carries neither separator nor username) · `UX2-C-01` (focus+blur no-keystroke = 0/8) |
| Uniformity treated as a TRIGGER, never a verdict | ✓ | 15/15 coerced, 19/19 refused typed, 0/8 empty-delta — each paired with a control that can produce the opposite |
| Discharges re-executed, not inherited from `02g` | ✓ | All 11 re-run on independently written harnesses: recursion battery, coercion poison census, `notify` AST walk, hostile-input battery |
| No line citation inherited from `02e` | ✓ | The document moved (`LLR-N13.1.5` `:2391` → `:3060`); every address re-derived at `94ad8d3` |
| Working tree not mutated | ✓ | `git archive HEAD` export + `tempfile.mkdtemp()` workspaces only; `git status --short fixtures/` empty; sha256 MATCH on all three fixture files |
| No `MapperApp` pointed at real `fixtures/` | ✓ | Every app probe copies `*.mmd`/`*.yml` into `mkdtemp` first; integrity block printed at probe exit |
| No mutated token spelled verbatim (C-56) | ✓ | Mutations described by position and operation; no dotted id ranges |
| Known false oracles not propagated | ✓ | `UX2-C-04`'s raw-id trace not used — verified instead that `match_set` paints tone and a count, and that titles travel `canvas_paint` where the coercion class applies. `A-11`'s `isinstance` gate not cited as evidence of anything |
| One artifact written, nothing else | ✓ | `02h-pdr3-security.md`; harnesses in the session scratchpad |

---

## 8 · Gate verdict

> ### `approved with conditions`
>
> **The security lens lifts its block.** At pass 2 I blocked on `S-16`, `S-17` and `S-18`. `S-16`
> closes on execution. `S-17` resolves — and `A-57` is right that the repair I demanded would have
> made it worse, so I adopt its correction against my own condition. `S-18` is cut by operator
> re-scope with a deferral record I audited and found honest. **19 of 19 items addressed, 0 live-unaddressed.**
>
> **The two defects this batch owns are correctly found and correctly specced.** `LLR-REPAIR.2` in
> particular anticipates its own near-miss fix and reddens it, which is the standard the rest of this
> batch's thresholds should be read against.
>
> **The four conditions are artifact corrections, not increment work**, and condition 1 is the one
> that matters: a stated remedy that is already implemented and does not work is worse than no
> remedy, because it launders a refusal into a pass. Fix that sentence and this batch is safe to seal.
>
> **`UX2-C-01` stays live on `master` by decision, not by oversight** — the deferral of the
> affordance design is accepted, the record must name a working remedy, and I have recommended a
> one-line change that needs no design ruling. The operator should make that call knowingly: today,
> one keystroke on a focused inspector field permanently rewrites both the map and its sidecar, and
> it has already cost this repository its own tracked fixtures once.
