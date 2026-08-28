# 02h — PDR iteration 3, QA / acceptance lens · `2026-08-26-ui-next-batch-02`

> **Method.** Audited against **my own eight conditions in `02d-pdr-qa-pass2.md` §1.1**, never against
> §6.5's amendment table — that instrument dropped conditions twice in this batch. Every number below
> was executed at **`94ad8d3`** in this session; transcripts pasted. **READ-ONLY**: nothing under
> `mapper/`, `tests/` or `fixtures/` was created, modified or staged; probe scripts live in the
> session scratchpad. No `MapperApp` was constructed anywhere in this pass, and no probe touched
> `fixtures/`. Mutated ids are described by position and operation, never pasted (C-56).

---

## 1 · VERDICT

**`approved with conditions`.** Seven of my eight pass-2 conditions are **DISCHARGED** with executed
evidence; one is **PARTIAL** on a limb that gates nothing. Six new conditions are raised, all of them
document edits with named remedies and no new measurement — the same boundary between condition and
blocker I applied at pass 2, applied consistently.

**On the deferral in `PDR-addendum-3` §5: I accept `UX2-C-02` and REFUSE `UX2-C-01`** — the
affordance *design* may defer; the *data loss* may not. §5 asks the lenses to rule explicitly rather
than inherit, and this is the explicit ruling. Costed in §6.

**Three things this pass found that were not on anyone's list:**

1. **`#D25` is correct on the merits and its own artifact does not follow it.** Two live sentences in
   `01-requirements.md` still read the three-row figure as a budget, and one of them tells an
   implementer that `Inc-8` is *"arithmetically breached"*. That is the false-fail `#D25` just
   abolished, left standing in a requirement that gates `Inc-8`. **Fourth false-oracle occurrence in
   this batch.**
2. **`keymap.py`'s collision set is stated four different ways at HEAD and no two agree** — and
   `C-D25a`, now the only cross-increment control on seat rows, is quantified over a hand-list that
   contains a **vacated** increment id and misses a live one. C-40 limb 2, on the addendum's own new
   condition.
3. **My own pass-2 `QA2-C-02` census was wrong**, and the document caught it. I reported 48 sites /
   17 files / 15 test files from a line-oriented grep. The AST census is **23 arg-ful call sites /
   10 files**; the grep swept in 25 zero-arg Textual `Widget.render()` sites and one docstring
   mention. I re-executed independently and reproduce the document's figure exactly. **My pass-2
   number was the sixth wrong generation of this census, and my prescribed remedy — "paste the
   grep" — would have written a seventh.** Recorded first because a lens that does not audit itself
   has no standing to audit a fold.

### 1.1 · Baseline re-verified

```
$ PYTHONUTF8=1 python -m pytest -q
630 passed, 17 deselected in 54.55s
$ git log --oneline -1
94ad8d3 docs: land amendment set 3 pass 2 and discharge all six routed cross-artifact edits
$ git status --porcelain fixtures/
(empty)
$ grep -n "erp\[" fixtures/legacy.mmd
2:    erp[Sistema ERP Legacy]
```

The fixtures damaged during the RIDER-1 audit are **restored and clean** — confirmed independently,
not taken from `02g`. `03-increments/` is empty, so every `AT-NNN` legitimately has no node on disk;
that is the pre-implementation state and is not scored as a defect anywhere below.

---

## 2 · My eight conditions, audited against disk

| # | Status | Executed evidence |
|---|---|---|
| **QA2-C-01** | **DISCHARGED** | Three-way rule re-derived by me at HEAD: **40 live `AT`, live union 40, 0 failing.** Full derivation in §3. `AT-009` now carries the `Acceptance:` line `A-29` claimed and did not have (`01-requirements.md:1517`); `AT-031` gains `LLR-N13.2.1` (`:3340`); `AT-046` and `AT-047` gain US-N06's story-list leg (`:1592`); `AT-034b` and `AT-040` leave with US-N14 under `#D23`. Every one of my six is dispositioned, and the dispositions are **enumerated in §5.2 rather than absorbed** — which is the failure mode I was watching for. |
| **QA2-C-02** | **PARTIAL — substance discharged, `PLAN.md` limb live** | Discharged **better than I prescribed**: `LLR-N07.2.2a`'s threshold is now set equality on both sides of the protocol (`01-requirements.md:2520-2530`) with an **AST** instrument (`:2535-2551`), and the floor is struck. I re-executed the AST independently — see §2.1 — and reproduce 23/10 exactly. **Live residual:** `PLAN.md:222`'s `R-1` row still reads *"6 definitions and 3 call sites plus 7 test files"* (definitions ✓ 6, production call sites ✓ 3, test files ✗ 9), and `PLAN.md:310` §9 C-1 still reads 29 sites / 14 files. **Not verdict-bearing:** `R-1` is a risk-register sizing; the mitigation it sizes is now specified correctly in the requirement, and no gate reads `R-1`. |
| **QA2-C-03** | **DISCHARGED** | Resolved as a cross-batch reference rather than re-authored (`A-57`, `01-requirements.md:7225`), and I verified the claim rather than the citation: `grep -rn "^#\+ .*LLR-STO" .dev-flow/` finds the heading at **`.dev-flow/2026-08-27-repair-batch-02/01-requirements.md:114`**, with its own increment at `.dev-flow/2026-08-27-repair-batch-02/03-increments/increment-001.md:1`. **I accept that re-authoring would have been the worse repair** — a second block under one id is the two-definitions defect this batch removed twice. The one arm the reference does *not* discharge (the alias bomb under the traversed `nodes:` key) is separated out into `LLR-N13.1.7` with `TC-088` (`:5450`), which is the correct handling. |
| **QA2-C-04** | **DISCHARGED** | `HLR-S06.3`'s threshold now reads per-token against the two adjudicated jobs — *"every `WARN` site classifies as outstanding attention and every `ALERT` site classifies as failure or blockage, each against `LLR-S06.3.5`'s single declared job"* (`01-requirements.md:897-903`). The old parent threshold is **struck in place** at `:904-914` with the reason, rather than silently replaced. The mutant its own child must redden is no longer its pass condition. |
| **QA2-C-05** | **DISCHARGED, and the answer is stronger than either option I offered** | The classifier is defined as a **declared per-site register over a derived input set**, with a **totality clause**: a derived site with no register row is a failure, not a skip (`01-requirements.md:915-935`). The split is stated explicitly — the judgement is in the artifact, the check is in the code — which is what keeps `AT-005` / `AT-006` at `test (unit)` honestly. `M-S06.3-classifier` is named as the weaker variant (assert only registered rows) and is reddened by totality. **I offered "or demote to `analysis`"; the fold refused it with a reason I accept** — an analysis is performed once, and this must fail later on work nobody has written. |
| **QA2-C-06** | **DISCHARGED** | §5.4 now states the cut **once**, with `#D5` named sole authority (`01-requirements.md:5548-5558`). The two live cuts are reconciled: §3.6's header reads `*(Inc-7 — §5.4)*` (`:2876`) and §3.8's reads `*(Inc-8 and Inc-9 — §5.4)*` (`:4062`). `Inc-6` is **vacated, not renumbered and not reused**, with both alternatives rejected on executed grounds (`:5563-5571`), and the repair increment is named `Inc-REPAIR` specifically so no substring scan collides. Three hard orderings are stated with their failure modes. **A new residual inside this area is raised separately at QA3-C-01 rather than reopening this condition** — it is not a carry of what I asked for. |
| **QA2-C-07** | **DISCHARGED** | §5.4.1 is a fixture budget with one row per increment (`01-requirements.md:5619-5638`). All three of my unbudgeted fixtures reconcile: `anidado` → Inc-3, the synthetic attachments/`meta` graph (`QA-N-08`) → Inc-4, and `AT-048`'s generated 200-map workspace **left with `#D24`** and is recorded as having left rather than absorbed (`:5652-5658`). `QA-M-02` is restored to a ledger with a line saying where it was discharged. The section also carries the `tempfile.mkdtemp` hard rule with its executed reason. |
| **QA2-C-08** | **DISCHARGED** | All three substitutions landed: `01-requirements.md:1359` (the vacuous-empty-arm sentence), `:1395` (the title/§5.2-row/id sentence), `:5497` (§5.3 criterion 5's containment arm). Each is written as a **strike plus correction with the reason**, not an overwrite, so the id that moved is recoverable. |

**Roll-up: 7 DISCHARGED · 1 PARTIAL · 0 LIVE-in-full.** Zero dropped: every one of my eight is
addressed under its own id somewhere in the fold, which is the first time in this batch that has been
true of a condition set.

### 2.1 · The A3 census, re-executed by me under AST (rule 4)

```
$ PYTHONUTF8=1 python ast_census.py      # ast.Call, func=Attribute named 'render', >=1 arg
CALL SITES (Attribute .render with >=1 arg): 23 sites / 10 files
  of which tests/: 20 sites / 9 files
   mapper/app.py 3 · tests/test_app.py 1 · tests/test_export.py 1 · tests/test_lane.py 3 ·
   tests/test_layered.py 2 · tests/test_legacy_fixture.py 1 · tests/test_outline.py 1 ·
   tests/test_radial.py 1 · tests/test_repair_depth.py 9 · tests/test_repair_perf_shape.py 1
RENDER DEFS in mapper/views/: 6 defs / 4 files
   mapper/views/lane.py 3 · mapper/views/layered.py 1 · mapper/views/outline.py 1 ·
   mapper/views/radial.py 1
```

Identical to `01-requirements.md:2545-2551`, independently derived. **The document's figure is right
and mine was wrong.** The mechanism it names is the mechanism: `.render` names two protocols in this
tree, and only an AST separates them.

---

## 3 · The three-way `AT` rule, re-derived

### 3.1 The rule I applied

§5.2 (`01-requirements.md:5286-5289`) mandates the count be the cardinality of the set of `AT-NNN`
tokens appearing in **all three** of:

- **A** — an `Acceptance tests:` line of a story's Acceptance block;
- **B** — an `Acceptance:` line of some HLR or LLR;
- **C** — the §5.2 behavioral table.

Liveness rules, applied uniformly to all three legs and stated before running:

1. §3.1 (`SUPERSEDED`, `#D16`) and §3.7 (`DEFERRED`, `#D23`) are excluded from A and B.
2. For **B**, an `Acceptance:` line under a heading matching `^#{4,5} \`?(HLR|LLR)-` carrying
   `SUPERSEDED` or `DEFERRED` is dead; a token **struck in place** inside a live bullet is dead.
3. For **C**, a row whose first cell is struck, or which carries `DEFERRED` / `SUPERSEDED`, is dead.
4. **§6 (Appendices) is excluded from A and B.** The amendment log quotes *before*-states verbatim,
   including whole `Acceptance tests:` bullets. A scanner that reads them harvests deleted ids out of
   a historical quotation. This is the same class as `A-55`'s known false gap and I hit it on the
   first run: without this rule the derivation reports three spurious failures at `:5937`, which is
   `A-07`'s quoted *"Before:"* line for `US-N13`.

### 3.2 Executed

```
$ PYTHONUTF8=1 python at3b.py

headings matching ^#{4,5} `?(HLR|LLR)-  : 87 total   73 live   14 dead
  live HLR = 21      live LLR = 52
section 3.1 = lines 609..756 (SUPERSEDED)   section 3.7 = lines 3560..4061 (DEFERRED #D23)

LIVE |A| = 40   |B| = 40   |C| = 40
THREE-WAY INTERSECTION = 40
LIVE UNION = 40 ;  FAILING THE RULE = 0

distinct AT tokens in the file = 56
not in the live intersection (16): AT-001 AT-002 AT-027 AT-028 AT-032 AT-033 AT-034
                                   AT-034b AT-035 AT-036 AT-037 AT-038 AT-039 AT-040
                                   AT-045 AT-048
```

**The lane's claim — 40 live `AT`, 0 failing the three-way rule — is confirmed independently.** The
live heading census `21 HLR / 52 LLR` also reproduces exactly.

### 3.3 The 56 → 40 difference, confirmed rather than assumed

The brief asked me to confirm the gap rather than accept it. Every one of the sixteen has a named
disposition and I checked each:

| Ids | Count | Disposition | Verified at |
|---|---:|---|---|
| `AT-001`, `AT-002` | 2 | struck with §3.1 (`#D16`) | `:5269` — §5.2's S-7 row reads *"none — `AT-001` and `AT-002` are struck"* |
| `AT-027`, `AT-028`, `AT-045` | 3 | deleted at amendment set 1 (`A-07`) — each appeared exactly twice and was claimed by no requirement | present at HEAD **only** inside `A-07`'s quoted *"Before:"* at `:5937` |
| `AT-032`, `AT-033`, `AT-034`, `AT-034b`, `AT-035`, `AT-036`, `AT-037`, `AT-038`, `AT-039`, `AT-040` | 10 | deferred whole with US-N14 (`#D23`) | §3.7's heading carries `DEFERRED` at `:3559`; §5.2's US-N14 row is struck at `:5275` |
| `AT-048` | 1 | deferred with `HLR-N13.3`'s thresholds 1 and 2 (`#D24`) | struck **in place** on `HLR-N13.3`'s `Acceptance:` bullet at `:3527-3530`, with the reason — its whole subject is threshold 1 |

`2 + 3 + 10 + 1 = 16`, and `56 − 16 = 40`. **The arithmetic closes.** Two of my six pass-2 failures
(`AT-034b`, `AT-040`) are dispositioned by the cut, and §5.2 says so in those words at `:5299-5302`
rather than letting the cut absorb them silently — which is precisely what I was watching for.

**One structural improvement worth naming.** §5.2 no longer delegates the figure to
`01d-unpark-measurements.md`. My pass-2 finding was that naming a sibling artifact as the authority
on a derived figure is a typed count with extra steps; the fold removed the delegation and states the
derivation in place. That closes the defect rather than the symptom.

---

## 4 · `A-55`'s `#D15` `AT`↔`TC` join, re-executed at HEAD

**The join as stated** (`01-requirements.md:5424-5434`): for every live `AT`, its `TC` set is the
union of the functional-table `TC`s of the requirements carrying that `AT` on an `Acceptance:` line.
Question: does every live `AT` reach at least one `TC`?

```
$ PYTHONUTF8=1 python join.py          # measured at 94ad8d3

live AT = 40 ; AT with >=1 live owning requirement = 40

NAIVE scanner (drops any functional row containing 'DEFERRED')
  -> live AT reaching NO TC: 1
     ('AT-025b', owners ['HLR-N13.3'])

CORRECT scanner (strike-through on the requirement cell only)
  -> live AT reaching NO TC: 0

HLR-N13.3 functional row @5381:
| HLR-N13.3 | test (pilot) | `TC-076` | containment on **load failure**, not on a clock;
  thresholds 1 and 2 **DEFERRED (`#D24`)** with `AT-048` |
```

**Result: the join is TOTAL at `94ad8d3` — 0 live `AT` ids reach no `TC`.** `A-55`'s result holds
at the current HEAD, not only at `ea1fbf9`.

**The known false gap reproduced exactly, and NOT reported as a gap.** `A-55` warns that a scanner
discarding rows containing the word `DEFERRED` loses `HLR-N13.3`'s **live** `TC-076` row, because the
row's *note* records `#D24`'s deferral of thresholds 1 and 2. I ran the naive scanner deliberately
and it reports precisely that: `AT-025b` unreachable. **The row is live; only its note mentions a
deferral.** `A-55` predicted two false positives (`AT-025b` and `AT-048`); at HEAD only `AT-025b`
surfaces, because `AT-048` has since left the live set — so the warning is now *more* accurate than
when it was written, not less. `A-55`'s decision to record the trap is vindicated: I would have
reported it as real had it not been written down, and *"the scanner said zero"* is how a correct
artifact gets damaged to satisfy a broken oracle.

**`#D15` is discharged.** I also endorse the form: a join stated once and computed cannot go stale,
where a transcribed third table goes stale on the next id that moves — and eleven moved in pass 1
alone.

---

## 5 · Testability review of the three new rulings — C-40's two limbs

For each condition: **limb 1** — is the declared *subject* actually in the predicate's expression?
**limb 2** — does any quantified set come from the RULE rather than from the implementation? Plus the
mutation that reddens it.

### 5.1 `#D25` — the seat-diff pin

**The ruling itself is CORRECT and I verify its search.** `#D25` claims the only occurrence of the
cap language in the sealed PDR is `#D5b`'s own sentence. Executed:

```
$ grep -n "seat-diff\|three-row\|cap\b" PDR-2026-08-26-ui-next-batch-02.md
396:`map/M → next_gap (view)`. D10's three-row seat-diff cap is reviewed row-by-row at DDR. Inc-3, Inc-6
```

One hit, and it is the sentence quoted. **The premise that `UX2-C-03` breaches a cap executes FALSE;
there is no breach; `Inc-3` is unblocked.** I confirm the false-fail and endorse C-53's pricing of it.
`#D25`'s executed basis also reproduces without an App:

```
$ PYTHONUTF8=1 python -c "from mapper import keymap; print(len(keymap.bindings_for('map')),
                          len(keymap.bindings_for('help')), keymap.duplicate_chords())"
27 2 []
```

| Condition | Limb 1 — subject in the expression? | Limb 2 — set from the RULE? | Mutation that reddens it | Verdict |
|---|---|---|---|---|
| **C-D25a** | **✗** | **✗** | — | **FAILS BOTH LIMBS** |
| **C-D25b** | ✓ — `duplicate_chords()` and the whole-seat pin read `keymap.py` itself | ✓ — the seat is read at run time | add a colliding chord in map scope → `duplicate_chords()` is non-empty | **sound**, unchanged from `#D5b` |
| **C-D25c** | ✓ — DDR reviews the diffs as one set; the subject is the diffs | n/a — a review obligation, not a gate | n/a | **sound as a process control**, and correctly labelled one |

**C-D25a fails limb 1.** The subject is *the increment's actual seat row diff*. The predicate is
*what the increment's packet declares*. Nothing joins the two. **The mutation that passes it:** an
increment rebinds a fifth seat row and writes four in its packet. `C-D25a` is green — a packet cannot
disagree with itself. `C-D25b` does **not** catch it either: a legitimate extra rebind creates no
duplicate chord, so `duplicate_chords()` still returns `[]`. This is a declaration obligation with no
oracle, which is the exact shape `LLR-N16.4`'s own `M-N16.4-a` is written to reject one section away.

**Remedy, using an instrument the batch already has** (`QA-M-04`, `LLR-N16.1.2`): require the packet's
declared diff to **equal** the difference between `keymap.bindings_for(scope)` measured on entry and on
exit — the whole-seat pin `C-D25b` already mandates. One clause, no new measurement, and it converts a
declaration into a gate. → **QA3-C-02**.

**C-D25a fails limb 2 separately.** Its quantified set is the hand-list *`Inc-3`, `Inc-4`, `Inc-6`,
`Inc-9`*, and `C-D25b` says *"each of the four"*. **`Inc-6` is VACATED** by `01-requirements.md:5586`
— *"the id is retired, not reassigned"*, with the ruling stated at `:5565-5575`. And the set omits `Inc-8`, which
`01-requirements.md:4539-4540` states *"adds seat rows, so `Inc-8` joins `keymap.py`'s collision set"*.
So the addendum's control is quantified over a retired id and misses a live one. → **QA3-C-01**.

**The set is stated four ways at HEAD and no two agree:**

| Statement | Set | Where |
|---|---|---|
| `#D5b`, sealed | Inc-3, Inc-4, Inc-6, Inc-9 (four-way) | `PDR-2026-08-26-ui-next-batch-02.md:396-397` |
| `#D25` `C-D25a`/`C-D25b` | Inc-3, Inc-4, Inc-6, Inc-9 (*"the four"*) | `PDR-addendum-3.md:91-95` |
| §5.4 and §3.4 | Inc-3, Inc-4, Inc-9 (*"THREE-way, not four"*) | `01-requirements.md:5610-5613`, `:2759-2761` |
| `HLR-N16.4` | adds Inc-8 | `01-requirements.md:4539-4540` |

Note also that §5.4's `Inc-8` row (`:5589`) lists `screens/help.py`, `darkside.py`, `app.py` and does
**not** list `keymap.py` — so `HLR-N16.4` obliges `Inc-8` to touch a file its own budget row omits. At
four source files that is still inside budget, so the remedy is a budget-row edit, not a re-cut.

**Remedy:** state the set as a derivation — *"every increment whose source-file budget includes
`keymap.py`, or that adds or rebinds a seat row"* — instead of enumerating ids. That is C-40 limb 2
applied to the addendum's own condition, and it is the same fix `A-32` applied to three floors and
`A-45` applied to the vocabulary count.

**A third `#D25` residual — the ruling does not retract its own abolished reading.** Two live
sentences still read the figure as a budget:

- `01-requirements.md:4540` — *"**and its rows count against `#D10`'s cap**, which §3.4 already
  routes to the PDR lane as **arithmetically breached**"*, inside `HLR-N16.4`, the requirement that
  gates `Inc-8`.
- `01-requirements.md:2759` — *"reviewed row-by-row at DDR (D10's three-row seat-diff cap)"*.

An implementer reading `HLR-N16.4` learns that `Inc-8` is blocked by a cap `#D25` has ruled does not
exist. **That is the fourth false-oracle in this batch** and it is the same shape as the other three:
a plausible predicate that fails a correct implementation. Both sentences also cite bare `#D10` /
`D10`, which the addendum's own §1 measured as resolving to two different decisions (`B-34`) — so
`#D25` diagnosed the ambiguity and then left its two live instances standing. → **QA3-C-03**.

### 5.2 `#D26` — the legend scrolls

**The ruling is sound and I endorse the deferral of the tabbed layout.** Deferring an information
architecture that is specified nowhere, at the final PDR iteration, on a screen whose entire job is
discoverability, is the right call; and the deferral is honest because the content is not lost —
`01-requirements.md:4509` records `union over real-key scroll positions : 27/27`.

| Condition | Limb 1 | Limb 2 | Mutation that reddens it | Verdict |
|---|---|---|---|---|
| **C-D26a** — set equality over CONTENT | ✓ | ✓ | see below | **sound, and already realizable on disk** |
| **C-D26b** — real keystrokes, not `scroll_to(...)` | ✓ | ✓ | see below | **sound at `AT-053`; DANGEROUS if left unscoped** |
| **C-D26c** — deferral recorded as a carry (`B-35`) | n/a | n/a | n/a | correct handling |

**C-D26a, limb 1: the subject is in the expression, and the oracle already exists.**
`tests/test_repair_layout.py:104-122` — `_painted_bindings` unions `_rows_in(app.screen,
dialog.region)` across **every** scroll position, failing if the pane never reaches the bottom. It
reads the composited frame, not the widget's own `render_lines`. So the object under assertion is the
panel's *content*, not its visible rows, exactly as `C-D26a` requires.
**Limb 2:** the quantified set is `declared_vocabulary`, derived from `01b` DECISION 3 §3.1 through
§3.4 by projecting every row onto the triple `(glyph, label, painted-in style)` and removing
`DEFERRED(#D7)` rows (`01-requirements.md:4368-4380`), with the cardinality **deliberately not
transcribed**. From the rule, never from the implementation. ✓
**Mutation that reddens `C-D26a`:** assert over `_rows_in` at rest instead of the union — the panel
paints 16 of 27 rows at rest (`:4506`), so eleven declared rows are missing and set equality fails.
That is the mutant `C-D26a` names, and it is the one that **passes on the panel that ships today**.

**C-D26b, limb 1:** the subject is *whether an operator can scroll*, and `HLR-N16.4`'s threshold puts
it in the expression — *"the set of keys with a measured effect while the legend is open equals the
set the legend paints for its own scope, derived by pressing each real key and observing `scroll_y`
or the screen stack, never by reading the seat alone"* (`01-requirements.md:4527-4530`). ✓
**Limb 2:** both sides measured at run time — the effect side from `scroll_y`, the declared side from
`bindings_for` on the legend's scope, which I confirm returns **2** today against 27 map rows. ✓
**Mutation:** `M-N16.4-a` is already named at `:4535` — add the three rows to the seat and assert the
seat. Green without pressing anything, and green if a later change makes the container non-focusable.
Reddened by the measured-effect side. Sound.

**But `C-D26b` is written unscoped, and unscoped it manufactures a false-fail.** It says *"the scroll
keys are asserted by real keystrokes, not by `scroll_to(...)`"*. `_painted_bindings` reaches its
scroll positions **by `scroll_to(...)`** (`tests/test_repair_layout.py:118`). An implementer applying
`C-D26b` literally will rewrite the content oracle to harvest by keystrokes — and that **couples
`AT-053`'s subject into every other legend `AT`**: a broken or undeclared scroll key would then redden
`AT-041`, `AT-042`, `AT-043`, `AT-044` and the negative control `AT-R14`, none of which is about
scroll keys. Five correct assertions fail for a defect in a sixth.

The distinction is real and cheap to state: **`scroll_to` as a content-harvesting mechanism is
legitimate; `scroll_to` as the assertion that an operator can scroll is not.** `C-16` bites on the
second only. → **QA3-C-04**.

### 5.3 `#D27` — the damaged card takes a glyph

**The ruling is sound and its reasoning on `ALERT` is the best argument in the addendum.** `01b` §3.5
is quoted correctly (`01-requirements.md:3101-3103` carries the same rule), and C-55 limb 2 is applied
correctly: `ALERT`'s emptiness is an accident of *this batch's* scope, because the malformed-query
chip belongs to the cut lens. Spending it here would hand the follow-on batch a token with two jobs
and break `LLR-S06.3.5`'s one-job census — a defect this batch would never see. **Refusing to spend a
token that is only free because its consumer was deferred is exactly right**, and I would have raised
it had the ruling gone the other way.

The requirement it answers is real and its pre-state is executed (`01-requirements.md:3090-3093`):

```
workspace: roto (cycle) + sano (2 nodes) + sano_vacio (healthy, 0 nodes)
  row: ['roto',       ' concept ', '0', '0']
  row: ['sano_vacio', ' concept ', '0', '0']      <- byte-identical as painted
```

| Condition | Limb 1 | Limb 2 | Mutation that reddens it | Verdict |
|---|---|---|---|---|
| **C-D27a** — glyph declared as a new `V` row, enters the derived set through the derivation | ✓ for the *legend*; **✗ for the card** | ✓ | remove the row from `01b` §3.4 → `LLR-N16.2.1`'s set equality fails | **sound for what it covers; does not reach the card** |
| **C-D27b** — codepoint NOT fixed here | n/a — an anti-literal rule | ✓ by construction | n/a | **correct discipline**, and it is the right lesson from four wrong hand-counts |
| **C-D27c** — the arm runs at 118 × 34 | ✓ | ✓ — the declared context of use, not a convenient size | run at 140 × 45 and the longest card string fits where it would not at 118 | **sound** |
| **C-D27d** — healthy-empty control retained | ✓ — the subject is the **painted** row | ✓ | paint the difference only in the transient toast → the two painted rows stay byte-identical → RED | **sound, and it is the condition that carries the ruling** |

**One gap, and it is created by the interaction of `C-D27a` with `C-D27b`.** `PRED-VIS` requires *"the
difference is carried by a **declared** token or glyph, not by the string alone"*
(`01-requirements.md:3079-3080`). `C-D27b` correctly refuses to fix a codepoint and points at *"the
derived-set test"* to assert it. **But that test is `LLR-N16.2.1`, and `LLR-N16.2.1` asserts what the
LEGEND paints, not what the CARD paints** — its verification compares the style the renderer emits
against the style the legend emits, over the vocabulary (`:4358-4360`). Nothing joins the glyph on the
sala card to `declared_vocabulary`.

**The mutation nothing catches:** `Inc-7` paints a glyph on the damaged card that is **not** a member
of the declared vocabulary — a bare `!`, or any codepoint the implementer prefers. `PRED-VIS`'s
inequality holds, the difference is carried by a glyph rather than a string, `C-D27d`'s control holds,
and `LLR-N16.2.1` is green because the legend's own vocabulary is untouched. The card then explains
itself with a glyph the legend does not explain — on the batch whose story is *"`?` explains **this**
view, with its real keys and its real glyphs"*.

**Remedy, one clause:** the glyph painted on the damaged card shall be a **member of
`LLR-N16.2.1`'s `declared_vocabulary`**, asserted by membership at run time. This preserves `C-D27b`
completely — no codepoint is fixed anywhere — and it is what makes `C-D27a`'s derived row load-bearing
rather than decorative. → **QA3-C-05**.

**Ordering check, verified rather than assumed.** `LLR-N16.2.1` is owned by `Inc-8`; the card is
painted by `Inc-7`; §5.4's serial order is `Inc-7` → `Inc-8`. `Inc-7`'s budget already includes
`darkside.py` (`01-requirements.md:5588`), which is where the vocabulary declaration lands, so `Inc-7`
can carry the declaration without a budget breach. **No conflict.** Recorded because it is the obvious
place one would appear.

---

## 6 · `UX2-C-01` / `UX2-C-02` — my ruling

`PDR-addendum-3` §5 asks the lenses to rule explicitly rather than inherit. This is the explicit
ruling, and it splits.

### 6.1 `UX2-C-02` — **ACCEPT the deferral**

The lens is cut by re-scope A. `c` (`consultar campos`) is an entry chord into a feature that does not
exist this batch, so it has no consumer, no `AT` that could press it and no screen it could open. A
chord seated for an absent feature is a seat row with no observable behaviour — the shape
`M-N16.4-a` is written to reject. **Deferring it is correct, not merely convenient**, and it should
travel with `UX2-C-11` under `B-31`/`B-32` as proposed.

### 6.2 `UX2-C-01` — **ACCEPT the deferral of the affordance design; REFUSE the deferral of the data loss**

**The defect is confirmed on the current tree, statically, without constructing an App:**

`mapper/widgets/inspector.py:277-278` — `on_input_blurred` calls `self._commit(event.input)`
unconditionally, with no guard. `_commit` at `:280-291` resolves the field from the widget id and
posts `FieldCommitted(self.node.id, field, widget.value)` **regardless of whether the value changed**.
So every focus departure from an inspector `Input` is a write. Focus traversal is not an edit gesture,
and the operator is given no confirmation and no undo.

**Why the affordance design may defer.** Whether a commit needs an explicit gesture, a confirmation
step or a dirty indicator is a genuine design question, it shares its shape with `UX2-C-11`, and
answering it at the final PDR iteration would be new scope on a screen this batch does not otherwise
touch. I accept that half without reservation.

**Why the data loss may not, on four grounds — none of them a preference:**

1. **It is a live durable-data-loss defect on `master`**, at the file and lines above, not a design
   gap. One keystroke, no confirmation, permanent overwrite of a tracked file.
2. **It has already fired inside this batch**, on the repository's own tracked fixtures, during the
   RIDER-1 audit — the incident this session's hard rule about never pointing a `MapperApp` at
   `fixtures/` exists because of. A defect that has already caused damage once in the batch that is
   deciding whether to defer it is not a hypothetical.
3. **The batch's own control against it is a process control, not a fix.** §5.4.1's
   *"every fixture is built in a `tempfile.mkdtemp` workspace, never by writing into `fixtures/`"*
   (`01-requirements.md:5639-5646`) protects the **repository's fixtures from the tests**. It does
   nothing for the **operator's maps from the app**. Those are different subjects, and reading the
   first as coverage for the second is the substitution this batch has caught three times.
4. **This batch multiplies the trigger.** Nine increments of Pilot acceptance tests press real keys
   through real focus traversal — `C-16` requires exactly that, and `AT-034b`'s own pass-2 record is
   that `pilot.press("n")` over nine focusables committed a ficha overwrite on five of them.
   **The batch's mandated test method is the reproduction.** Shipping it against an unfixed `_commit`
   means every new acceptance test is a live rehearsal of the defect.

**I therefore adopt the addendum's own stated minimal alternative:** gate `_commit` on a non-empty
delta — return when `widget.value` equals the node's current value for that field. One predicate, one
file, no new surface, no design ruling, and it closes `UX2-C-11` as §5 already notes.

**The cost of my refusal, stated so it is not free either.** `mapper/widgets/inspector.py` appears in
**no live increment's source-file budget** — I checked all nine rows of §5.4's table
(`01-requirements.md:5581-5590`) and it is in none. So the fix needs:

- **a budget line.** The cheapest honest home is `Inc-REPAIR`, currently the smallest increment in the
  batch at one source file (`store.py`); adding `inspector.py` makes it two, still the smallest, and
  it is already the increment whose subject is *"shipped defects repaired inside this batch"* (§3.9).
- **a requirement and an `AT`/`TC`.** `PLAN.md:831` records `D26` — *"a code fix never discharges a
  missing requirement"* — as an adopted rule of this batch, and it was adopted precisely because
  `mapper/store.py`'s shipped fix made a missing requirement *harder* to notice. Landing this as an
  unwritten code change would breach that rule on the batch's own third repair. It needs a sibling to
  `LLR-REPAIR.1` and `LLR-REPAIR.2` with the delta predicate as its threshold, and a negative arm: an
  actual edit still commits.
- **a fixture note.** Its `AT` must run in a `tempfile.mkdtemp` workspace under §5.4.1's hard rule,
  which is the one place the process control and the code fix are about the same thing.

That is one file, one requirement block, one `AT` and one `TC`. **If the orchestrator judges that too
expensive for iteration 3, the honest alternative is not to defer silently but to record
`UX2-C-01` as a KNOWN LIVE DATA-LOSS DEFECT carried on `master` through this batch, with the
reproduction and the one-line remedy written down** — so the follow-on batch inherits a defect, not a
discovery. What I refuse is the deferral being recorded as if it were cost-free; §5 of the addendum
says the same thing in its own warning, and I am agreeing with it.

---

## 7 · Newly raised — six conditions, all document edits

| # | Condition | Discharge | Severity |
|---|---|---|---|
| **QA3-C-01** | `keymap.py`'s collision set is stated four ways and no two agree (§5.1's table). `C-D25a`/`C-D25b` name a **vacated** `Inc-6` and omit `Inc-8`, which `01-requirements.md:4539` puts in the set. §5.4's `Inc-8` budget row omits `keymap.py`. | State the set as a **derivation** — every increment whose budget includes `keymap.py` or that adds/rebinds a seat row — and add `keymap.py` to `Inc-8`'s budget row (4 of 4, no breach). | **condition** — C-40 limb 2 on the addendum's own new control |
| **QA3-C-02** | `C-D25a` has no oracle: a packet's declared diff is joined to nothing. An increment rebinding a fifth row and declaring four is green, and `duplicate_chords()` does not catch it. | Require the declared diff to **equal** the entry/exit difference of `keymap.bindings_for(scope)` — the whole-seat pin `C-D25b` already mandates. | **condition** — C-40 limb 1 |
| **QA3-C-03** | Two live sentences still read the three-row figure as a budget, and `01-requirements.md:4540` tells an implementer `Inc-8` is *"arithmetically breached"* by a cap `#D25` ruled does not exist. Both cite the ambiguous bare `#D10`/`D10` (`B-34`). | Strike both in place with `#D25` named, as this document strikes elsewhere. | **condition — the sharpest one.** Fourth false-oracle in this batch |
| **QA3-C-04** | `C-D26b` is unscoped. Applied to `_painted_bindings` (`tests/test_repair_layout.py:118`) it couples `AT-053`'s subject into `AT-041`, `AT-042`, `AT-043`, `AT-044` and the negative control `AT-R14`. | Scope `C-D26b` to `HLR-N16.4`/`AT-053`'s threshold; state that `scroll_to` remains legitimate as a content-harvesting mechanism and is forbidden only as the assertion that an operator can scroll. | **condition** — false-fail generator |
| **QA3-C-05** | `PRED-VIS` says *"a **declared** token or glyph"*; `C-D27b` correctly fixes no codepoint; nothing asserts the card's glyph is a member of `declared_vocabulary`. A glyph outside the vocabulary passes every arm. | One clause: the card's glyph shall be a member of `LLR-N16.2.1`'s `declared_vocabulary`, asserted by membership at run time. Preserves `C-D27b` intact. | **condition** |
| **QA3-C-06** | §5.3's exit criteria are numbered 1, 2, 3, 4, 5, 7, 8 — **there is no criterion 6** at HEAD (it was 6 at `ea1fbf9` and a new criterion was inserted above it). And criterion 8 (`:5544-5547`) specifies the A3 census as `grep -rn "\.render(" mapper/ tests/`, which is **`M-N07.2.2a-b`**, the named weaker variant `01-requirements.md:2572-2575` says can never equal the migrated set. | Renumber; restate criterion 8's instrument as the AST census of `LLR-N07.2.2a`. | **minor**, but it is an *exit criterion* citing its own rejected mutant, and my pass-2 artifact cites "criterion 6" |

**None of these makes a wrong implementation pass an acceptance test.** `QA3-C-01` through `QA3-C-05`
make a *correct* implementation fail, or let a specific wrong one through a control that was supposed
to catch it; every remedy is a document edit and every number they need is executed above. That is the
condition side of the boundary, and it is the same boundary I drew at pass 2.

---

## 8 · Evidence checklist

| | Item | Evidence (re-runnable) |
|---|---|---|
| ✗ | Acceptance criteria use Given/When/Then | **By design, and accepted** — the batch uses EARS (`While … the system shall …`), the ISO 29148 register this project standardised on. Recorded rather than waved through, as at passes 1 and 2. |
| ✓ | Test cases have explicit Expected, not vague "works" | Every live row of §5.2's functional table carries a method and a numeric threshold; the `#D15` join (§4) confirms all 40 live `AT` reach one. The eight thresholds pass 1 called weaker than their statement are closed; `HLR-S06.3`'s (`QA2-C-04`) and the classifier's (`QA2-C-05`) closed this pass. |
| ✓ | Edge cases include empty, boundary, invalid, error | Empty: `AT-015` zero-hidden and the 0-node graph; `LLR-N07.3.3` blank query. Boundary: `HLR-N06.3`'s four pinned `(w,h,folded)` triples; `LLR-N06.1.2`'s clamp over 6 inputs. Invalid: §3.0 `COERCION_RANGES`; `LLR-CNV.1.4`'s 14 malformed style strings; `LLR-N13.1.7`'s alias bomb with its un-aliased control. Error: `LLR-N13.1.5` load-failure containment; `LLR-REPAIR.1`/`LLR-REPAIR.2`. |
| ✓ | Regression checklist exists | §5.4's three hard orderings each state the failure mode of reversal; `LLR-N06.2.1` enumerates the two predicted-red `toggle` call sites; `C-D25b`'s entry/exit whole-seat pin on four increments; §5.4.1's per-increment fixture budget. `C-D6b`'s standing re-run left with US-N14 under `#D23` and that is recorded, not dropped. |
| ✓ | Exit criteria stated | §5.3. **Two defects raised** → `QA3-C-06` (no criterion 6; criterion 8 cites its own rejected mutant). |
| ✓ | No real PII / secrets | Fixtures only. No credentials in any probe. `git status --porcelain fixtures/` empty; `fixtures/legacy.mmd:2` verified intact. |
| ✓ | Test results left blank for the human | §5.2 reads `pending Phase 4` in every live behavioral row. Nothing in this review marks an unrun test as passed. `03-increments/` is empty and every `AT` correctly has no node on disk — reported as the pre-implementation state, never as a failure. |
| ✓ | **Layer B (black-box) through the shipped surface** | Export read from disk by code-point scan (`LLR-CNV.2.1`); legend read through the region-clipped union oracle at `tests/test_repair_layout.py:104-122`; overflow read from the composited frame via `_rows_in`, not `render().plain`. `#D26` **strengthens** this — `C-D26a` forces content over visible rows. **Two declared residuals:** `LLR-N06.3.2`'s arithmetic (§6.2 item 5, honest); and `#D27`'s card glyph, which reaches no Layer-B membership assertion → `QA3-C-05`. |
| ✓ | **Bidirectional surface-reachability** | Input side: `AT-051` closes the last unpressed relocated chord (`UX2-C-07`); `C-D26b` closes the scroll keys; `A-26` folded the five rulings so every `AT` drives a real key. Output side: the `#D15` join is TOTAL (§4), so every declared black-box outcome reaches a white-box case through an owning requirement. **The trace-link gap I recorded at pass 2 (`AT-009` observable but not traceable) is closed** — `AT-009` now carries `LLR-CNV.2.1` at `01-requirements.md:1517`. |
| ✓ | **No unfilled template** | No `<...>` placeholders; no `TC-NNN` literals standing in for real ids; no empty required rows. **And this pass the document's own derivation holds on itself**: the three-way rule returns 0 failures (§3) and the `#D15` join returns 0 gaps (§4). That was the one item I marked ✗ at pass 2. |
| ✓ | No control bytes written | This file byte-scanned before write; probe scripts in the session scratchpad only; nothing under `mapper/`, `tests/` or `fixtures/` touched; no `MapperApp` constructed. |

---

## 9 · What PDR should carry out of this pass

1. **`#D25` is right and its own artifact does not follow it.** A ruling that abolishes a false-fail
   has to retract the sentences that assert it, or the false-fail survives in the place an
   implementer actually reads. `01-requirements.md:4540` is the fourth instance in this batch of the
   same failure — a plausible predicate that fails correct work — and the first one *created by the
   fix for a previous one*.
2. **A condition written as "declare it in your packet" is not a control.** `C-D25a` is the only
   cross-increment guard on seat rows and nothing joins its declaration to `keymap.py`. The batch has
   the instrument (`bindings_for` at run time) and used it correctly four sections away; the control
   just has to point at it.
3. **The lane boundary is still where things fall, but it is now narrow.** My pass-2 blind-spot
   finding holds: the one residual on my eight conditions is a `PLAN.md` row (`QA2-C-02`), the same
   lane both pass-2 drops landed in. It is now one stale sizing row that gates nothing, down from two
   silently dropped findings. The mechanism that fixed it — §5.4.1 recording *where a deflected
   finding went* — is worth keeping as a house form.
4. **The rule I asked for in pass 2 now runs and passes.** 40 live `AT`, 0 failing, 0 join gaps,
   arithmetic reconciled 56 = 40 + 16 with every excluded id dispositioned under a named ruling. The
   document's derivations hold on the document. That is the thing that was not true at pass 2, and it
   is why this is `approved with conditions` and not a stop.
