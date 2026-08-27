# PDR pass 2 — `2026-08-26-ui-next-batch-02` · architect lens

| | |
|---|---|
| **Station** | PDR second pass — architect lens |
| **Batch** | `2026-08-26-ui-next-batch-02` · variant B «atlas» + round-10 capabilities |
| **Date** | 2026-08-27 |
| **Base** | `d8777840313145fec341687f0081afd7230c755b` — executed, `git rev-parse HEAD` |
| **Input** | `PLAN.md` §12–§14 · `PDR-2026-08-26-ui-next-batch-02.md` (my sealed first pass, `#D1`…`#D20`) · `01-requirements.md` §6.5 amendment sets 1 and 2 (`A-01`…`A-41`) · `ARCHITECTURE-proposed-at-ARQ.md` · live `docs/ARCHITECTURE.md` |
| **Method** | Every tree claim below was executed in this session against `d877784` with the output pasted. No line number, count or verdict is inherited from a parked artifact, from `PLAN.md`, or from my own first pass (C-43). Where my first pass is now wrong, it is corrected here against itself. |
| **Verdict** | **REJECTED — iterate to Phase 1 for amendment set 3.** |

---

## 1 · VERDICT

**REJECTED.** The fold is substantial and mostly good work — `A-20`, `A-21`, `A-22`, `A-23`, `A-24`,
`A-25`, `A-26`, `A-32`, `A-38` each replaced a predicate that could not fail with one that can, and
three of them corrected the review that prescribed them. **But the PDR cannot go to APPROVED,
because the batch's primary implementation artifact now carries two live increment cuts, three
acceptance tests that belong to no increment, a set-equality threshold whose right-hand side does
not exist as written, two shipped byte-identity guards that this batch will turn red without saying
so, and one security control that no requirement owns.** Each is a document repair, none needs the
design re-derived — but six of them change what an increment *contains*, and an increment cut that
is not single-valued is not a cut.

**Why REJECTED and not a second "approved with conditions".** My first pass closed conditionally on
eight named conditions plus three scaffolding items. **Four of them — `C-D4a`, `C-D4c`, `#D15`, and
risk `A-11`'s `isinstance` gate — were dropped by the fold and no amendment noticed**, while the
41-row amendment table reports green throughout. That is the failure mode the operator named: an
amendment table is a container, and a green count cannot see what the fold dropped. Re-applying the
instrument that just failed, on a longer condition list, would be softening a finding to let the
batch proceed. The iteration list below is short, named and mechanical; amendment set 3 should be
one sitting.

**What is NOT re-opened.** Both A3 moves stay approved (`#D1`, `#D4`) — re-verified in §5 below, and
neither reversal condition is met. `#D5a`, `#D5b`, `#D6`, `#D7`, `#D8`, `#D9`, `#D10`, `#D11`,
`#D12`, `#D13`, `#D14`, `#D16`, `#D17`, `#D18` stand; `A-26` folded `#D6`/`#D7`/`#D8`/`#D9`/`#D10`
into requirement **bodies**, verified by re-reading, not by trusting the table. The 9-increment
serial cut is **confirmed in content** and **rejected in the document that carries it**.

### 1.1 · The iteration list — each item individually dischargeable

| # | Finding | Grade | Discharged by |
|---|---|---|---|
| **P2-B1** | `01-requirements.md` carries **both** the ARQ 7-increment cut (rejected by `#D5`) and the ratified 9-increment cut, simultaneously | **blocker** | §6.1 — restate the three story headers and five body references |
| **P2-B2** | `AT-009`, `AT-031`, `AT-040` are live and belong to no requirement and therefore no increment (C-21) | **blocker** | §6.2 — give each an `Acceptance:` owner or delete it |
| **P2-B3** | `LLR-N16.2.1` asserts set equality against "21 rows `V1` through `V21`"; executed, `01b` DECISION 3 carries **23** labels with `V4` and `V4a` byte-identical, and mandates rows for `◍` which `#D7` ruled OUT | **blocker** | §3 (flag b) — four named edits |
| **P2-B4** | Inc-1 and Inc-3 each turn a shipped sha256 byte-identity guard red; no artifact names it. `LLR-N06.2.1`'s "enumerated, not asserted as a zero" census enumerates **2 of 9** external references | **blocker** | §6.3 — name the predicted-red set by derivation |
| **P2-B5** | §3.0's `COERCION_RANGES` declaration and the `_CONTROL_MAP` widening — the load-bearing half of security condition **C-4** — have no HLR, no LLR, no `AT`, no `TC` and no increment | **blocker** | §2 (flag a) option a2 |
| **P2-B6** | `LLR-N06.2.5` is parented so that its owning increment must edit a 5th source file that a later increment owns | **blocker** | §2 (flag a) option a2 |
| **P2-C1** | `C-D4a` LIVE — the IFC `canvas_rows` consumer list is still wrong, and now wrong in a second way | condition | §4 |
| **P2-C2** | `C-D4c` LIVE — nobody's input, C-49 empty row | condition | §4 |
| **P2-C3** | `#D15` (the AT↔TC mapping) LIVE after 41 amendments — the one item my first pass graded ✗ | condition | §4 |
| **P2-C4** | `#D2` half-discharged: `with_header` struck from `01-requirements.md`, still declared at `ARCHITECTURE-proposed-at-ARQ.md:275` | condition | §4 |
| **P2-C5** | `IRenderer` as a real `runtime_checkable` Protocol appears in **no requirement**; risk `A-11`'s `isinstance` gate was dropped | condition | §5 |
| **P2-C6** | `LLR-N07.2.2a` has no threshold over the **22** call sites, and its `>= 6` floor is a floor on a census whose naive derivation returns **17** | condition | §5 |
| **P2-C7** | The live `docs/ARCHITECTURE.md` at `d877784` still freezes **both** A3 subjects; no increment owns amending it | condition | §5 |
| **P2-C8** | `HLR-N13.3` threshold 1 (`< 1000 ms` for 200 maps) is an absolute wall-clock assertion with no stated headroom | condition | §7 |

---

## 2 · FLAG (a) RULING — `LLR-N06.2.5` under `HLR-N06.2`

### 2.1 · Ruling

**Option (a2), widened. `LLR-N06.2.5` is RE-PARENTED out of `HLR-N06.2`, and §3.0 is promoted from a
definitions block to a requirement that owns the whole coercion class.** Sealed as
`PDR-2026-08-26-ui-next-batch-02#D21`.

Option **(a1)** — leave it with the imperfection recorded — is rejected on executed evidence, below;
it is not a stylistic smell. Option **(a3)** — re-parent under whichever HLR owns security condition
C-8 — **is not available**: executed, C-8 has no other owner. It is cited in exactly one requirement
in the document, and that requirement is `LLR-N06.2.5` itself.

### 2.2 · The criterion — adopted, and given a second limb that makes it executable

I **adopt** the operator's criterion and **add** a mechanical limb, because as stated it is a thought
experiment and a gate needs a measurement:

> **Limb 1 (adopted).** If the parent story were descoped, would the child's subject be deleted with
> it? If no, the parent is wrong.
> **Limb 2 (added).** Does satisfying the child require editing source files outside the parent
> increment's declared file set? If yes, the mis-parenting is not stylistic — it makes the owning
> increment unsatisfiable within its declared budget.

Limb 2 is what converts "a cross-cutting LLR under a story-scoped HLR is a smell" into something a
reviewer can execute and a gate can fail on.

**The criterion is not one that condemns everything — control, executed.** Applied to a sibling under
the same parent: `LLR-N06.2.3` (a branch name reaching the fold pill is coerced,
`01-requirements.md:1565`). Descope US-N06 and there is no fold pill, so the subject is deleted with
the parent — limb 1 passes. Its touched symbols are `mapper/darkside.plain` and the pill construction
in `mapper/views/layered.py`, both inside Inc-3's declared set — limb 2 passes. **Correctly parented.**
The criterion discriminates between two LLRs under the same HLR, which is what makes it a criterion
rather than a verdict.

### 2.3 · Executed basis

**Limb 1 — the census, independently re-derived.** I did not read the amendment's figures; I wrote my
own AST walk over `mapper/**/*.py` and ran it:

```
D1 total .notify( call sites                       : 30
D2 sites with a NON-LITERAL first argument         : 19
D3 of D2, markup NOT disabled                      : 0
D4 of D2, first argument not routed through plain(): 15
     mapper/app.py: 11
       :647  :661  :682  :687  :760  :1053  :1055  :1058  :1455  :1646  :1738
     mapper/screens/factory.py: 4
       :423  :444  :468  :470
```

`A-18`'s figures reproduce **exactly**, addresses included. Now apply limb 1: **descope US-N06 and
all 15 sites survive.** Not one of them is a fold toast. Eleven are in `app.py` on paths unrelated to
the canvas, and four are in a screen US-N06 never touches. The child's subject is not deleted with
the parent. **Limb 1: parent is wrong.**

**Limb 2 — the executed consequence, which is the part that makes this blocking.** `LLR-N06.2.5`
parents to `HLR-N06.2` → US-N06 → **Inc-3**. Inc-3's declared source set under `#D5` is `app.py`,
`widgets/rail.py`, `views/layered.py`, `keymap.py` — **four of four, at budget**. Satisfying
`LLR-N06.2.5` requires editing `mapper/screens/factory.py` for the four sites above. That is:

1. a **fifth** source file in Inc-3, **undeclared** — the batch's only declared breach is Inc-2's,
   and an undeclared one is what validator rule `V9` exists to catch;
2. a **collision with Inc-9**, which owns `screens/factory.py` under `#D5` and `#D9`;
3. checked against `C-D9c` — the four notify addresses are `:423`, `:444`, `:468`, `:470`, none of
   which is the `screens → app` back-edge at `:343`, so `C-D9c` is **not** violated by the move
   itself. That is why the fix is a re-parent and not a scope cut.

**Limb 2: the parent makes the child unsatisfiable in its own increment.** That is a structural
defect, not an imperfection.

### 2.4 · The second, larger instance the flag exposed — `P2-B5`

Chasing (a2)'s natural home surfaced a bigger gap. Executed:

```
$ grep -n "COERCION_RANGES" 01-requirements.md
386 1244 1578 2520 2984 3442 4035 4574 4578 4580 5149
$ grep -n "_CONTROL_MAP" 01-requirements.md
400 404 437 458 1571 4582
```

Every one of those is either §3.0 itself (`:386`, `:400`, `:404`, `:437`, `:458`), a *reference* from
a threshold (`:1244`, `:1578`, `:2520`, `:2984`, `:3442`), a traceability-table note (`:4035`), the
amendment record (`:4574`–`:4582`, `:5149`), or — at `:1571` — a **descriptive parenthetical** in
`LLR-N06.2.3`'s touched symbols saying what `_CONTROL_MAP` does *today*.

**No requirement creates `COERCION_RANGES`. No requirement widens `_CONTROL_MAP`.** §3.0 carries no
HLR id, no LLR id, no `Acceptance:` line, no `Touched symbols:` line, no validation method and no
increment. Its own text is normative — *"It shall be declared once in `mapper/darkside.py`"*,
*"`_CONTROL_MAP` shall be widened to cover the list"* — and §3.0 measures the gap itself at **22 of
84 code points uncovered**, including every bidi range the hostile fixtures drive.

So the load-bearing half of security condition **C-4** — which `A-14` correctly identified as the
widening rather than the ordering — is owned by nobody. Four LLRs in **four different increments**
(`LLR-N06.2.3` Inc-3, `LLR-N13.2.1` Inc-7, `LLR-N14.2.3` Inc-6, `LLR-N16.2.3` Inc-8) each *assert*
against a list none of them *creates*. Under the serial cut the de facto owner is whichever lands
first — Inc-3 — whose declared file set does not contain `darkside.py`.

### 2.5 · The amendment text the ruling requires

Amendment set 3 shall make the following edits. The id `HLR-COERCE` is a placeholder; the
requirements lane owns the id-space convention.

**Edit a-1 — promote §3.0 to a requirement.** Give §3.0 an HLR heading and the standard block:

> `#### HLR-COERCE — file-derived text is coerced before it reaches any painted surface`
> - **Traceability:** security conditions **C-4**, **C-5**, **C-7**, **C-8** (`02b` S-04, S-05, S-06,
>   S-09); risk **A-7**. *(This HLR has no parent story by design: it is a product-wide control whose
>   subject survives the descoping of every story in the batch. That property is stated here so a
>   later reader does not "fix" it by re-parenting it under a story.)*
> - **Statement:** The system shall declare one list of code points that may not reach a painted
>   surface, shall coerce every file-derived string against that list before it is painted, and shall
>   derive the set of coercion sites from the tracked product sources at run time rather than from a
>   list maintained by hand.
> - **Owned LLRs:** `LLR-COERCE.1` (the `COERCION_RANGES` declaration and the `_CONTROL_MAP`
>   widening — the 22 uncovered code points §3.0 measures); `LLR-COERCE.2` (the ordering clause,
>   scoped to `mapper/views/layered.py::_fit`, which `A-14` executed as the truncator that coerces
>   nothing); `LLR-N06.2.5`, **re-parented here**.
> - **Acceptance:** the batch's existing coercion `AT` ids stay on their surface-specific LLRs; this
>   HLR owns `TC-073` and the new `TC` ids for `LLR-COERCE.1` and `LLR-COERCE.2`.

**Edit a-2 — re-parent `LLR-N06.2.5`.** At `01-requirements.md:1508`, change
`**Traceability:** HLR-N06.2, risk A-7, security condition **C-8**` to
`**Traceability:** HLR-COERCE, risk A-7, security condition **C-8**`. Move the block out of §3.4 into
§3.0. At `:1503`, `LLR-N06.2.2`'s cross-reference *"Its coercion is governed by `LLR-N06.2.5`"*
**stays** and is now a cross-section reference, which is correct and is the point: the fold toast is
governed by the class, and the class is not owned by the toast.

**Edit a-3 — strike the recorded imperfection.** At `:4697`–`:4702`, `A-18`'s parent-HLR re-read
paragraph ends *"a cross-cutting LLR under a story-scoped HLR is a smell, and the alternative —
inventing an HLR for it — would have been worse."* Replace with the executed reason it was not worse:
the notify class spans `mapper/screens/factory.py`, which Inc-3 does not own, so the mis-parenting is
an undeclared budget breach and not a stylistic cost. Record the criterion (§2.2) so the next
cross-cutting LLR is tested rather than argued.

**Edit a-4 — increments.** `LLR-COERCE.1` and `LLR-COERCE.2` land in **Inc-1**: `darkside.py` is
already in Inc-1's declared set for the S-6 tokens, and `views/layered.py` is not — so
`LLR-COERCE.2` moves to Inc-3, which owns `views/layered.py` and is the increment that first asserts
against the list. `LLR-N06.2.5` lands in **Inc-9**.

**Why Inc-9 for the notify census, ruled and not deferred.** Inc-9's declared set is `keymap.py`,
`screens/factory.py`, `screens/settings.py`, `app.py` — the census's 15 sites are in `app.py` (11)
and `screens/factory.py` (4), so it adds **zero** files and stays at 4 of 4. `C-D9c` is unaffected
(none of the four factory addresses is `:343`, executed above). And the ordering is already right:
`LLR-COERCE.1` widens `plain()` at Inc-1 and the census asserts routing *through* `plain()`, so
Inc-1 → Inc-9 is a real dependency, not a convenience. **Cost of the ruling:** the coercion half of
S-09 stays live for eight increments. Accepted, and stated rather than hidden: the defect is
pre-existing on `master`, C-8 is a condition and not a blocker (C-3 is the only live security
blocker), and the alternative — forcing `screens/factory.py` into Inc-3 — creates the two-owner
collision `#D5` exists to prevent.

**What would reverse this ruling.** Evidence that a `notify` site inside `mapper/views/` or
`mapper/widgets/` exists — which would put the class inside a renderer's boundary and make the
`views` dependency ban, not the story tree, the governing constraint. Executed: the census returns
**0** such sites; all 30 are in `app.py`, `screens/`, and nothing else.

---

## 3 · FLAG (b) RULING — the map-canvas braille promise

### 3.1 · Ruling

**Option (b2) — explicit deferral to the batch that reworks the canvas. And YES: the prose must be
amended — but the prose is not where the operator located it, and the real defect is one layer down.**
Sealed as `PDR-2026-08-26-ui-next-batch-02#D22`.

### 3.2 · The criterion

> **A batch may declare a gap only where no requirement in the batch is made unsatisfiable or vacuous
> by that gap. Where a declared gap collides with a normative threshold, it is not a gap — it is a
> contradiction, and one of the two must move.**

I adopt the operator's framing that a §6.2 declared gap contradicting normative prose leaves two live
definitions of what the batch delivers — the `#D6`/`D14` defect — and I sharpen it: prose is the
cheap half. The expensive half is a **threshold** that cannot be evaluated because of the gap. That
is what is actually here.

### 3.3 · Executed basis — (b1) is structurally unavailable

```
$ grep -rn "\.dots\b" mapper/ tests/ --include=*.py
mapper/views/radial.py:123:        cv.dots = {}
mapper/views/radial.py:209:                cv.dots[(int(dx * 2), int(dy * 4))] = hue
$ grep -rn "\.bgs\b" mapper/ tests/ --include=*.py
mapper/views/radial.py:124:        cv.bgs = {}
mapper/views/radial.py:224:                cv.bgs[(x + j, y)] = pill_bg
```

Two `.dots` sites, both in `radial.py` — `A-24` reproduces exactly. And measured directly, by spying
on `Canvas.rows()` for `fixtures/legacy.mmd` with `selected_id="fin"` at the four sizes the repair
batch pins:

```
RadialRenderer    140x45   canvases=1 dots=  483 bgs=  101 cells=   85 bits=    0
LayeredRenderer   140x45   canvases=1 dots=    0 bgs=    0 cells=  424 bits=   99
OutlineRenderer   140x45   canvases=0 dots=    0 bgs=    0 cells=    0 bits=    0
RadialRenderer     80x24   canvases=1 dots=  267 bgs=  101 cells=   85 bits=    0
LayeredRenderer    80x24   canvases=1 dots=    0 bgs=    0 cells=  328 bits=   78
RadialRenderer    140x8    canvases=1 dots=  305 bgs=   96 cells=   84 bits=    0
LayeredRenderer   140x8    canvases=1 dots=    0 bgs=    0 cells=  212 bits=   67
RadialRenderer    300x120  canvases=1 dots= 1094 bgs=  101 cells=   85 bits=    0
LayeredRenderer   300x120  canvases=1 dots=    0 bgs=    0 cells=  424 bits=   99
```

`LayeredRenderer` — the map canvas's default view — writes **0 dots at every size**. No change to
`Canvas.rows()` can raise it above 0, because `rows()` can only composite what a renderer wrote.
**`A-24`'s structural argument is confirmed on independent measurement.** (b1) would require new
free-angle-edge geometry in `LayeredRenderer` — new mechanism, outside declared scope, expanding
Inc-1 and Inc-2. **Rejected.** (b2) it is.

*(Two by-products worth keeping: `OutlineRenderer` builds **no `Canvas` at all**, which is why its
digests are the only ones the Canvas A3 cannot touch; and `bgs` is live at ~96–101 cells per radial
render and equally discarded, so the `bgs` half of `HLR-CNV.1` is not a speculative layer.)*

### 3.4 · Correction to the flag as posed — the prose is not in §3.4

The brief locates the surviving promise at *"US-N06's prose in §3.4"*. **Executed: §3.4 does not
mention braille.** I read `01-requirements.md:1292`–`:1334` in full. US-N06's Acceptance block
promises pan, fold pills and an overflow declaration; its `Deliverable + observation` is *"a painted
canvas whose visible column range changes with pan; a painted pill …; and a painted overflow
indicator"*. No braille clause exists there to amend.

The surviving map-canvas braille promise is in **three** other places:

```
$ grep -n -i "braille" 01-requirements.md   (relevant rows)
107  > **As** an operator who has just been shown a canvas of braille edges, fold pills and coloured
113  | US-N06 and US-N14 introduce a whole new glyph vocabulary (`▸ +N` pills, braille dust, ...) |
3343 - **Rationale:** US-N06 and US-N14 introduce a whole new glyph vocabulary — the fold pill,
     braille dust, the overflow indicator, ...
```

`:107` and `:113` are §2.6 story **S-5** (US-N16 «leyenda»); `:3343` is `HLR-N16.2`'s rationale.
All three assert that **US-N06** introduces braille dust. Under `#D22` that is false: US-N06 is the
layered map canvas, which paints none.

### 3.5 · The real defect — a normative threshold the gap makes unevaluable (`P2-B3`)

This is the finding, and it is why flag (b) is a blocker and not a prose edit.

`LLR-N16.2.1` (`01-requirements.md:3394`), amended by `A-36`:

> *"style equality over **every** declared glyph; and the declared vocabulary **equals** `01b`
> DECISION 3's enumeration — **21 rows `V1` through `V21`, plus 5 colour rows** — asserted as a set
> against the single declaration, not as `count > 0`."*

`HLR-N16.2` (`:3352`): *"For **every** glyph in the declared vocabulary, the legend's style string
equals **the renderer's style string for that glyph**."*

Three things are executed-false about the right-hand side of that set equality.

**(i) The cardinality does not reproduce.**

```
$ grep -oE "^\| V[0-9]+[ab]? \|" 01b-ux-decisions.md
V1 V2 V3 V4 V5 V6 V4a V4b V7 V8 V9 V10 V11 V12 V13 V14 V15 V16 V17 V18 V19 V20 V21
count: 23
```

**23 labels, not 21.** `A-36` replaced a hand-chosen floor with a set equality precisely so the
number would come from the declaration — and then transcribed the number wrong. A set-equality
threshold whose right-hand side has the wrong cardinality is a floor with extra steps.

**(ii) The braille row has three live definitions.** Read at `01b-ux-decisions.md:271`–`:288`: `V4` is
`∙ ∙ ∙` / `territorio sin explorar` / `WORDMARK`, and `V4a` is `∙ ∙ ∙` / `territorio sin explorar` /
`WORDMARK` — **byte-identical in glyph, label and style** — with `V4b` added beside it. The prose says
*"the legend collapses them into V4, which under-declares. Specified here as two rows"* and then
**does not strike `V4`**. Three rows for one concept, two of them identical. This is the exact defect
`#D6` removed for *"hit"*, `D14` for *"coverage"* and `A-10` for `WARN`'s job — in the artifact a
set-equality threshold points at.

**(iii) The set mandates legend rows for glyphs this batch does not and will not paint.** Reachability
census over `mapper/**/*.py` at `d877784`:

```
V4/V4a braille (U+2800-U+28FF)  -> mapper/widgets/components.py only (10)  — no view, no canvas
V5  U+2594  (selection seat)    -> ABSENT from mapper/
V10 U+2593  (minimap density)   -> ABSENT from mapper/
V16 U+2217  (lens glyph)        -> ABSENT from mapper/
V17 U+21C4  (enlaza mapas)      -> ABSENT from mapper/
V18 U+25CD  (repo provenance)   -> ABSENT from mapper/
```

`V18` is `◍ github` / `procedencia repo` — **the marker `#D7` ruled OUT of this batch**, with the four
things a later batch would need written down. `A-36` then made a requirement mandate a legend row for
it. That is a live second definition of what the batch delivers, and it is `#D7`'s own subject.

`V17` (map linking) and the minimap family have no story in this batch either. And for **all** of
them, `HLR-N16.2`'s predicate — *"the legend's style string equals the renderer's style string for
that glyph"* — **has no defined value**, because no renderer emits the glyph and therefore no renderer
style string exists. `LLR-N16.2.1`'s touched symbols name `mapper/views/layered.py` as the consumer of
the declaration; `LayeredRenderer` paints 0 braille, so the braille arm of the predicate compares the
legend against nothing. That is `C-40` limb 2 in its purest form, inside the requirement `A-36` wrote
to remove `C-40` limb 1.

This lands squarely in **Inc-8**, whose entire content after §13.4's strike is the glyph vocabulary.

### 3.6 · The amendment text the ruling requires

**Edit b-1 — the prose (three sites, not §3.4).**
- `01-requirements.md:107` — the S-5 story clause *"a canvas of braille edges"*. Amend to name the
  radial view, or drop the braille term: `> **As** an operator who has just been shown a canvas of
  fold pills, coloured chips and — on the radial view — braille edges, …`
- `01-requirements.md:113` — the INVEST *Valuable / Negotiable* row lists *"braille dust"* among what
  **US-N06** introduces. Move the term out of the US-N06 list; it is `HLR-CNV.2`'s, and `HLR-CNV.2`
  is a `PIN (radial)`.
- `01-requirements.md:3343` — `HLR-N16.2`'s rationale repeats the same list. Same edit.
- Add to **§6.2 item 4** the sentence that closes the loop, since item 4 is currently silent on it:
  *"The prose at §2.6 S-5 and at `HLR-N16.2`'s rationale is amended in the same edit; a declared gap
  that leaves the prose standing is two live definitions of what the batch delivers."*

**Edit b-2 — the set-equality target.** `LLR-N16.2.1:3394` and `HLR-N16.2:3352` shall assert equality
against **the batch's own declared vocabulary**, derived from the single declaration
`LLR-N16.2.1` creates — **not** against `01b` DECISION 3 verbatim, and with **no literal count**. The
declared vocabulary is the subset of DECISION 3 whose glyph some renderer in this batch paints; the
predicate reads `len(declared_vocabulary)` from the declaration, exactly as the amendment's own second
clause already says. Delete *"21 rows `V1` through `V21`"* from both sites. `A-07`'s reasoning applies
verbatim: correcting `21` to `23` would repeat the defect with a fresher wrong number.

**Edit b-3 — `01b-ux-decisions.md` DECISION 3.** Strike row `V4` (superseded in place by `V4a` and
`V4b`, per D20's marking convention), so one concept has one row. This is a ux-lens artifact; the ruling
is architect-owned but the edit belongs to that lane and should be routed, not made here.

**Edit b-4 — the deferred rows, marked by derivation and never by hand-list.** Every DECISION 3 row
whose glyph no renderer in this batch paints — executed above: `V4a`, `V4b` (for every view except
radial), `V5`, `V10`, `V16`, `V17`, `V18` — shall carry an explicit
`deferred — no renderer in this batch` marker, and `HLR-N16.2`'s style-equality predicate shall skip
marked rows **by reading the marker**, never by a carve-out list in the test. `#D10`'s own reasoning
is the authority: an exemption list is the pattern that cost six rediscoveries. `V18` additionally
gains a cross-reference to `#D7`, so the next reader sees the ruling and not a gap.

**What would reverse `#D22`.** A requirement appearing in this batch that gives `LayeredRenderer`
free-angle-edge geometry — which would make the map-canvas braille promise owned again and turn
`HLR-CNV.2` from a `PIN (radial)` back into a renderer-neutral requirement. Nothing in the batch
proposes it, and adding it expands Inc-1 and Inc-2 past their declared budgets.

---

## 4 · BLOCKER AND CONDITION DISCHARGE AUDIT

**Method (C-44).** Every row was verified by **re-reading the amended artifact** for the thing the
condition demands, never by reading the amendment table's claim that a corrective pass ran. Where the
two disagree, the artifact governs. Audited against the **source** conditions in my first pass and in
`02b`, not against `A-01`…`A-41`.

### 4.1 · My first pass's conditions

| Condition | Demanded | State | Executed re-read |
|---|---|---|---|
| **`C-D4a`** | IFC `canvas_rows` consumer list corrected to the four `views` call sites; `mapper/export.py` moved to a transitive-observer line | **LIVE** | `01-requirements.md:3746`–`:3752` still lists consumers `views/layered.py`, `views/lane.py`, `views/outline.py`, `views/radial.py`, **`mapper/export.py`**. `:3760` re-asserts it in prose. `A-40` at `:5150` re-asserts it a third time. **And it is now wrong in a second way**: executed, `views/outline.py` builds **no `Canvas`** (probe §3.3, `canvases=0`) and calls `rows()` nowhere. Real list at `d877784`: `lane.py:216`, `lane.py:299`, `layered.py:283`, `radial.py:253` — **4 sites, 3 files, 0 outside `views`** |
| **`C-D4b`** | `Canvas` gets a direct unit test in Inc-1 | **DISCHARGED as specified** | Five `Executed verification` lines now name `pytest tests/test_canvas.py` with distinct `-k` selectors (`:988`, `:1009`, `:1025`, `:1040`, `:1069`). `ls tests/test_canvas.py` → absent, which is correct: the file is Inc-1's deliverable, and the requirement now names it and its predicates |
| **`C-D4c`** | `AT-007` / `AT-009` re-run after Inc-2 | **LIVE** | `grep -rn "C-D4" .dev-flow/2026-08-26-ui-next-batch-02/` returns hits **only in my own first-pass PDR**. Zero in `01-requirements.md`, zero in `PLAN.md`. C-49 empty row |
| **`C-D6a`** | *"only one result set is live"* becomes a tested Layer-0 invariant | **DISCHARGED** | Requirement **bodies** at `:2127`, `:2878`, `:4153`, `:4211`, not only the amendment table at `:4922`/`:4928`/`:4930` |
| **`C-D6b`** | `LLR-N14.3.2` retained verbatim; re-run after Inc-4, Inc-6, Inc-9 | **DISCHARGED** | Bodies at `:3072`, `:4074`, `:4153`. `A-35` additionally strengthened it with the `escape` clause and executed why the parked invariant could not see the failure it was written for |
| **`C-D9a`** | `tab` drop gated behind a probe with a working positive control | **DISCHARGED** | Bodies at `:3310`, `:4078`, `:4155`, `:4212`. `A-26` at `:4934` carries my probe's vacuity forward verbatim rather than banking it |
| **`C-D9b`** | `UNMIGRATED_SCREENS` shrinks in the same increment | **DISCHARGED** | Bodies at `:3325`, `:4078`, `:4155` |
| **`C-D9c`** | `screens/factory.py:343` byte-identical | **DISCHARGED** | Bodies at `:3328`, `:4078`, `:4155` |
| **`#D2`** | `ViewState.with_header` struck | **HALF** | `grep -n "with_header" 01-requirements.md` → **0 hits**, struck. But `ARCHITECTURE-proposed-at-ARQ.md:275` still declares `with_header: bool = True` inside the `ViewState` dataclass, and `:235` still names it. Two live rosters → **`P2-C4`** |
| **`#D15`** | An AT↔TC mapping before Inc-1 | **LIVE** | `grep -rn "D15\|AT↔TC" 01-requirements.md` → **NONE**. §5.2 re-read in full: still exactly two tables, US→AT at `:3965` and Requirement→TC at `:4013`, and they still never cross. **This is the single item my first pass graded ✗ on the evidence checklist, and 41 amendments did not touch it** |
| **`#D14`** | `AT-027`, `AT-028`, `AT-045` struck | **DISCHARGED** | `A-07`. Confirmed by census: none appears on any `Acceptance:` line in §3 |
| **risk `A-11`** | Inc-2's gate includes `isinstance(r, IRenderer)` over all six renderers | **LIVE** | `grep -n "runtime_checkable\|Protocol\|isinstance" 01-requirements.md` → **0 hits**. It survives only in `ARCHITECTURE-proposed-at-ARQ.md:527`. → **`P2-C5`** |
| **§6.2 scaffolding 1** (`tests/test_canvas.py`) | before Inc-1 | **DISCHARGED as specified** | see `C-D4b` |
| **§6.2 scaffolding 2** (AT↔TC) | before Inc-1 | **LIVE** | see `#D15` |
| **§6.2 scaffolding 3** (§6.5 amendments) | `#D2`, `#D12`, `#D14`, `#D15`, `#D13` | **4 of 5** | `#D2` `A-07`-adjacent ✓ (half, see above) · `#D12` `A-28` ✓ · `#D14` `A-07` ✓ · `#D13` — `A-41` records that neither figure is quoted in `01-requirements.md` and leaves them against `PLAN.md`, correctly ✓ · `#D15` ✗ |

### 4.2 · Architect-owned blockers from the source reviews

| Blocker | Owner | State | Re-read |
|---|---|---|---|
| `QA-B-09` (a) subject | architect/measurement | **DISCHARGED** | `A-24` relabels `HLR-CNV.2` `PIN (radial)` on a structural argument I reproduced independently (§3.3) |
| `QA-B-09` (b) containment arm | architect | **DISCHARGED** | `A-24`'s derived-set argument is stronger than the review's: hand-listed sets fail in **both** directions, executed |
| `QA-B-10` five gating questions | architect | **DISCHARGED** | `A-26` folds `#D6`, `#D7`, `#D8`, `#D9`, `#D10` into requirement bodies. `PLAN.md` §13.3's correction is right and is the honest read: the fold was the fix, not a re-ruling |
| `S-03` / security `C-3` | architect + security | **DISCHARGED as design** | `A-04` (`LLR-N13.1.5`) and `A-05` (`HLR-N13.3`) both exist and both re-read. The `PLAN.md` §14.1 self-correction — the card **is** painted and misdeclares — is the load-bearing one, and `A-04` folds it correctly |
| Security `C-4` | architect | **PARTIAL — `P2-B5`** | §3.0 exists and is excellent; it belongs to no requirement and no increment |
| Security `C-8` | architect | **PARTIAL — `P2-B6`** | `A-18` is right; the parenting makes it unsatisfiable in its increment |
| `#D18` security-lens referral | architect | **CARRIED, unchanged** | No security lens has run since the parked `02b`. Both surfaces `#D18` names are still live, and the second one (`screens/factory.py`, Inc-9) is now **larger** because `#D21` adds the notify census to Inc-9. The referral stands and its scope has grown |

### 4.3 · One correction to my own first pass (C-43 applied to myself)

My §1.2 wrote: *"the working-tree amendment has already flipped it to 'NO — Inc-1 owns it. See
R-016.'"* **That is now false.** The tree at `d877784` is clean apart from `.dev-flow/state.json`, and:

```
$ git log --oneline -2 -- docs/ARCHITECTURE.md
e359148 feat(ui): variant A «taller» ...
a190d08 Phase 2-3: architecture, frozen interfaces, increment plan
$ git status --porcelain docs/ARCHITECTURE.md
(empty)
$ grep -n -i canvas docs/ARCHITECTURE.md | sed -n '5p'
134:| `Canvas` drawing buffer | `canvas` | `views` | put(...), wire(...), elbow_down(...), rows() -> list[str] | yes for MVP |
```

The ARQ amendment was never committed and no longer exists anywhere except as the uncommitted
proposal in `.dev-flow/`. **The live governing architecture document at `d877784` still freezes both
A3 subjects**, and still declares `IRenderer.render(graph, selected_id, w, h, **kwargs)` at `:58` and
`:136`. That is normal for a PDR — Phase 6 amends docs — but **no increment in the cut owns the
amendment**, so nine increments would run against a governing document that forbids two of them.
→ **`P2-C7`**.

---

## 5 · A3 RE-VERIFICATION

### 5.1 · The executed census — and both prior figures answer a different question

Neither the orchestrator's 29-sites-across-14-files nor my own parked 3-production-call-sites is the
migration surface. **`.render` is two different protocols in this tree**, and a line-oriented count
cannot tell them apart. AST walk over `mapper/**/*.py` and `tests/**/*.py`:

```
ZERO-ARG .render() (Textual Widget protocol) : 25 sites, 9 files
ARG-FUL  .render(...) (IRenderer protocol)   : 22 sites, 9 files
    mapper/app.py:737   mapper/app.py:1352   mapper/app.py:1727
    tests/test_app.py:74
    tests/test_export.py:12
    tests/test_lane.py:15  :30  :45
    tests/test_layered.py:13  :28
    tests/test_legacy_fixture.py:35
    tests/test_outline.py:13
    tests/test_radial.py:15
    tests/test_repair_depth.py:583  :604  :631  :697  :722  :749  :779  :792  :814
  PRODUCTION arg-ful: 3  ['mapper/app.py:737', 'mapper/app.py:1352', 'mapper/app.py:1727']
```

And the definition side:

```
$ grep -rn "def render" mapper/ --include=*.py | wc -l
17
   of which in mapper/views/  : 6   lane.py:108 :171 :311 · layered.py:131 · outline.py:47 · radial.py:107
   of which Textual widgets   : 11  widgets/components.py (9) · widgets/rail.py:177 · app.py:974 (render_group)
```

| Surface | `d877784` | Parked figure | Verdict |
|---|---|---|---|
| `IRenderer` definitions | **6**, in `mapper/views/` | 6 | ✓ holds |
| Arg-ful call sites | **22**, 9 files — 3 production, **19 in 8 test files** | mine: "3 production" · orchestrator: "29 / 14" | **both incomplete** |
| Textual `Widget.render()` — **not in the A3** | 25 sites, 9 files, 11 definitions | not separated | the source of the 29/14 figure |
| `**kwargs` in `mapper/views/` | **5** — `lane.py:114`, `:177`, `:317`, `outline.py:53`, `radial.py:113` | 5 | ✓ `A-28`'s `QA-N-03` correction holds |
| `IRenderer` as a Python type | **0** — `layered.py:288` and `widgets/rail.py:6`, both prose comments | 0 | ✓ holds |
| `mapper/views/state.py` | **absent** | absent | ✓ holds |
| `rows()` call sites | **4**, in 3 files, **0 outside `views`** — `lane.py:216`, `lane.py:299`, `layered.py:283`, `radial.py:253` | 4 sites, 4 files (`layered.py:223`, `radial.py:165`) | ✓ count holds, **every address stale**, and the file count was 4 not 3 |
| Modules importing `Canvas` | **3** — `lane.py:10`, `layered.py:8`, `radial.py:9` | 3 | ✓ holds |
| `tests/test_canvas.py` | **absent** | absent | ✓ holds |

**`#D1` and `#D4` both stand.** `#D4`'s stated reversal condition — a consumer outside `mapper/views/`
indexing `rows()` positionally — is executed **still not met**. `#D1`'s field audit is unaffected.

### 5.2 · Is the A3 still one increment? — YES in intent, NO as written (`P2-C6`)

`LLR-N07.2.2a` (`:2019`–`:2040`) states *"All six `render` definitions shall take `(graph, state)`"* —
correct, all definitions in one increment. Its thresholds are:

> *"derived renderer count `>= 6` (executed: 6 `def render` definitions across 4 files); `**kwargs`
> occurrences across those six `== 0` after the change (pre-state 5); and every renderer's output
> byte-identical to pre-change."*

Two defects, both executed:

1. **No threshold quantifies over the call sites.** The A3 is 6 definitions **and 22 call sites**.
   `ARCHITECTURE-proposed-at-ARQ.md:406` says *"all three call sites"* and `:527` says *"seven test
   files"* — executed, **3 production plus 19 test sites across 8 test files**; the ARQ figures
   predate `tests/test_repair_depth.py`, which alone carries **9**. A signature migration whose gate
   counts definitions and not callers can half-land, which is `A-1`'s own named risk.
2. **`>= 6` is a floor on a derived count** — precisely what `A-32` abolished everywhere else for
   `LLR-S06.3.1`, `LLR-S06.3.3` and `LLR-S06.3.4`. It survived here, and here it is worse than
   elsewhere: the naive derivation `grep -rn "def render" mapper/` returns **17**, of which **11 are
   Textual widgets that must NOT be migrated**. A census that sweeps them in passes `>= 6`
   comfortably while being wrong by eleven files. `A-32`'s own argument applies verbatim — *"a
   derivation losing three files sits comfortably above the floor"* — with the sign flipped.

**Amendment text for `P2-C6`:** replace `>= 6` with set equality against a derivation that is
protocol-aware, and add a call-site clause:

> **Numeric pass threshold.** The set of migrated definitions **equals** the set of `render`
> definitions in `mapper/views/*.py` (executed at `d877784`: 6 — `lane.py:108`, `lane.py:171`,
> `lane.py:311`, `layered.py:131`, `outline.py:47`, `radial.py:107`); the set is derived with an
> `ast` walk restricted to `mapper/views/`, **never** by `grep -rn "def render" mapper/`, which
> returns 17 by sweeping in 11 Textual `Widget.render(self)` definitions that must not be migrated.
> `**kwargs` occurrences across the six `== 0` after the change (pre-state 5, plus one explicit
> `query: str = ""` at `layered.py:131`). **And**: the set of call sites passing arguments to a
> `render` attribute **equals** the migrated set — derived by an `ast` walk over `mapper/` and
> `tests/` selecting `Call` nodes on attribute `render` with at least one argument, which separates
> the 22 `IRenderer` sites from the 25 zero-arg Textual sites (executed pre-state: 22 sites, 9 files,
> of which 3 production and 19 test). **Zero call sites of the old shape survive.**

### 5.3 · `#D3` — `views/state.py` as the home

Unchanged and still correct. Executed re-check of the ban surface for the new file:
`grep -rn "textual" mapper/views/` → **0**. `views → diff` already exists at `layered.py:9`, so no new
edge. Ban intact.

### 5.4 · One gap the fold left in the A3's own artifact

**No requirement creates `mapper/views/state.py::ViewState` itself.** Six LLRs name individual fields
as `NEW — created in Phase 3` — `focus_owner` (`LLR-CNV.3.1:1280`, Inc-2), `pan_x`/`pan_y`
(`LLR-N06.1.1:1375`, Inc-3), `folded` (`LLR-N06.2.1:1461`, Inc-3), `hits` (`:1924`, Inc-4),
`lens_matches` (`:2926`, Inc-6) — and **nothing owns the dataclass, its frozen-ness, its
fully-defaulted contract, or its Inc-2 roster.**

Adding a defaulted field to a frozen dataclass is additive and correctly does **not** re-open A3 —
`ARCHITECTURE-proposed-at-ARQ.md:343` (R-012) says so explicitly and I ratify it. **But no requirement
says so**, so an implementer reading `01-requirements.md` alone sees a dataclass gaining fields in four
increments and no statement that only the first is an A3. Fold into `P2-C5`'s amendment: one LLR under
`HLR-CNV.3` or `HLR-N07.2` creating `views/state.py::ViewState` — frozen, fully defaulted, roster
pinned at Inc-2 — plus `IRenderer` as a `runtime_checkable` `Protocol` and the per-renderer
`isinstance` assertion that is this interface's first mechanical enforcement, with R-012's
"adding a defaulted field is additive and never A3" stated normatively.

---

## 6 · THE INCREMENT CUT

### 6.1 · Content — CONFIRMED. Document — REJECTED (`P2-B1`)

`PLAN.md` §13.4's re-derivation is **correct in content**: Inc-1 loses S-7's layout work, Inc-7 gains
S-03, Inc-8 shrinks to the glyph vocabulary, and the `8 before 9` HARD ordering **DISSOLVES**. I
confirm the dissolution and the reason: `#D5`'s hazard was that Inc-9's oracle reads the painted panel
while Inc-8 makes the panel able to paint 27 rows; the repair batch shipped
`#help-bindings { height: 1fr; overflow-y: auto }` inside a `VerticalScroll`
(`mapper/screens/help.py:49`–`:53`, `:73`–`:75`) and `_painted_bindings`
(`tests/test_repair_layout.py:104`–`:123`) unions rows across every scroll position, so the panel can
paint all of them before Inc-8 runs. **The hazard is gone; the dependency is ordinary.** Keeping the
serial chain for `keymap.py`'s four-way collision is a preference, and §13.4 is right to record that
it is one.

**But the cut lives in `PLAN.md` and the implementer reads `01-requirements.md`, which carries the
rejected cut.** Executed:

```
$ grep -n "^### 3\." 01-requirements.md
 472  3.1 · S-7  (Inc-1) — SUPERSEDED
 621  3.2 · S-6  (Inc-1)
 945  3.3 · HLR-canvas  (Inc-1 and Inc-2)
1292  3.4 · US-N06  (Inc-3)
1865  3.5 · US-N07  (Inc-4)
2212  3.6 · US-N13  (Inc-6)     <- ratified Inc-7
2657  3.7 · US-N14  (Inc-5)     <- ratified Inc-6
3103  3.8 · US-N16  (Inc-7)     <- ratified Inc-8 + Inc-9
```

Five further body references carry the same rejected numbering: `:2116` (the `#D6` fold table's own
increment column gives Q-7 to *Inc-5*), `:2638` (`HLR-N13.3` *"gates Inc-6"*), `:3402` and `:3452`
(*"`PLAN.md` §6 sequences Inc-7 last"*, *"red the moment Inc-7 lands the vocabulary"*), `:4212`
(R-8, *"not at the Inc-7 gate"*). Meanwhile `:775`, `:790`, `:2013`, `:2042`, `:2120`, `:2134`,
`:2135`, `:2136`, `:4016`, `:4074` carry the **ratified** numbering.

**Two live cuts, in the same document, in the same section in two cases.** An implementer opening §3.8
reads Inc-7, opens Inc-7's task file and finds US-N13. This is `C-21` in its exact form — the `AT` set
changed and the cut set was not re-stated where it is read — with the aggravation that the *superseded*
cut is still normatively present. No amendment among `A-01`…`A-41` touches it.

**Discharge:** amendment set 3 restates all eight sites to the ratified numbering and adds one line to
§5.3 or §6.5 naming `#D5` as the sole authority on the cut, so a future re-cut has one place to land.

### 6.2 · C-21 — every AT mapped to an owning increment

Derived, not transcribed. Harvest of `AT-\d+[ab]?` over §3 (`01-requirements.md:348`–`:3501`), minus
the five struck ids, cross-checked against the 27 `Acceptance:` lines in §3:

```
distinct AT tokens in section 3 : 51
struck                          : AT-001, AT-002, AT-027, AT-028, AT-045
LIVE                            : 46
```

**This reconciles the validator exactly**: 51 distinct tokens = 55 blocks minus the 4 non-V2 blocks
= the 51 `V2` blocks the orchestrator measured. `A-19`'s caveat is right in mechanism and its figure
of 48 is stale — set 2 added `AT-007b`, `AT-025b`, `AT-034b`, taking it to 51. Recorded because
`A-19` explicitly warns against reading `V2` as the `AT` count; the reconciliation is what makes the
warning checkable.

| Inc | Owning requirements | `AT` ids owned | Count |
|---|---|---|---|
| **1** | `HLR-S06.1`, `HLR-S06.2`, `HLR-S06.3`, `LLR-S06.3.5`, `HLR-CNV.1`, `HLR-CNV.2` | `AT-003`, `AT-004`, `AT-005`, `AT-006`, `AT-007`, `AT-007b`, `AT-008` | 7 |
| **2** | `HLR-CNV.3`, `LLR-N07.2.2a` | `AT-010` | 1 |
| **3** | `HLR-N06.1`, `HLR-N06.2`, `HLR-N06.3` | `AT-011`, `AT-012`, `AT-013`, `AT-014`, `AT-015`, `AT-016`, `AT-017` | 7 |
| **4** | `HLR-N07.1`, `HLR-N07.2`, `HLR-N07.3`, `LLR-N06.2.4` | `AT-018`, `AT-019`, `AT-020`, `AT-021`, `AT-022`, `AT-023`, `AT-046`, `AT-047` | 8 |
| **5** | `LLR-N07.2.2b` | `AT-024` | 1 |
| **6** | `HLR-N14.1`, `LLR-N14.1.3`, `LLR-N14.1.4`, `HLR-N14.2`, `HLR-N14.3` | `AT-032`, `AT-033`, `AT-034`, `AT-034b`, `AT-035`, `AT-036`, `AT-037`, `AT-038`, `AT-039` | 9 |
| **7** | `HLR-N13.1`, `HLR-N13.2`, `HLR-N13.3` | `AT-025`, `AT-025b`, `AT-026`, `AT-029`, `AT-030`, `AT-048` | 6 |
| **8** | `HLR-N16.2`, `HLR-N16.3` | `AT-043`, `AT-044` | 2 |
| **9** | `HLR-N16.1` | `AT-041`, `AT-042` | 2 |
| **— NONE —** | *no requirement claims these on an `Acceptance:` line* | **`AT-009`, `AT-031`, `AT-040`** | **3** |

43 owned + 3 unowned = **46** ✓, reconciling with the live set exactly.

**The cut absorbs every new and split id without re-cutting.** `AT-007b` → Inc-1 via `HLR-CNV.2`;
`AT-025b` and `AT-048` → Inc-7 via `HLR-N13.3`, which §13.4 already gives Inc-7; `AT-034b` → Inc-6 via
`LLR-N14.1.3` and `LLR-N14.1.4`. **C-21's structural test passes: the cut is not stale in content.**

**But C-21 also says every AT must have an owning increment, and three do not** — `P2-B2`:

- **`AT-009`.** `A-29` states it is *"**promoted** under `LLR-CNV.2.1`, whose threshold A-23 rewrote."*
  **The promotion did not land.** Executed listing of all 27 `Acceptance:` lines in §3 (`:566` through
  `:3474`): `AT-009` appears on none of them. `LLR-CNV.2.1` has no `Acceptance:` line at all — the
  nearest are `AT-007b` at `:1103` (`HLR-CNV.2`) and `AT-010` at `:1269` (`HLR-CNV.3`). `AT-009`
  survives only at `:957` (story block), `:972` (boundary catalog) and `:3969` (behavioral table).
  **This is an amendment that reports a change it did not make** — precisely the failure the operator
  warned the amendment table cannot see.
- **`AT-031`, `AT-040`.** `A-29` admits both *"remain catalog-only and are recorded here as such
  rather than counted as specified."* Honest, and the honesty is worth keeping — but a catalog clause
  names no fixture, no size and no threshold, so both ids are in the behavioral table (`:3972`,
  `:3973`) and in no increment. Under C-21 that is not a disclosure, it is an unowned test.

**Discharge for `P2-B2`:** for each of the three, either add it to the `Acceptance:` line of the
requirement that actually observes it — `AT-009` to `LLR-CNV.2.1` (which is where `A-29` believes it
already is, and where `A-23`'s on-disk read-back threshold makes it observable); `AT-031` to
`LLR-N13.2.1`, which owns the coercion of the card title it drives; `AT-040` to `LLR-N14.1.3`, which
owns the malformed-token class it drives — **or delete it**, as `#D14` deleted three others. Do not
carry a fourth tier.

### 6.3 · `P2-B4` — two shipped byte-identity guards this batch turns red, named nowhere

The repair batch shipped **18 sha256 pins** on the exact surfaces this batch changes. Executed:

```
tests/test_repair_depth.py:93   MASTER_LEGACY_DIGESTS  = 12 pins
    3 renderers x GOLDEN_SIZES = ((140,45),(80,24),(140,8),(300,120))
    asserted at :815 in test_c53_legacy_fixture_renders_identically_to_master
tests/test_repair_depth.py:113  MASTER_RAIL_DIGESTS    =  5 pins (parametrized on `collapsed`)
    asserted at :1056 in test_c53_the_rail_renders_legacy_identically_to_master
tests/test_repair_depth.py:121  MASTER_FACTORY_TREE_DIGEST = 1 pin
```

```
$ grep -c "MASTER_LEGACY_DIGESTS\|MASTER_RAIL_DIGESTS\|test_repair_depth\|GOLDEN_SIZES\|test_c53" \
      01-requirements.md PLAN.md PDR-2026-08-26-ui-next-batch-02.md
0  0  0
```

**Zero mentions in all three artifacts.**

**Inc-1 reddens four of them, by construction.** The `dots`/`bgs` occupancy probe in §3.3 measures
`RadialRenderer` writing **267 to 1094 dots and 96 to 101 bgs per render at exactly the four
`GOLDEN_SIZES`**, all currently discarded by `Canvas.rows()`. `HLR-CNV.1`'s whole content is making
them reach the output. The four `("RadialRenderer", w, h)` pins therefore go red the moment Inc-1
lands — **which is correct behaviour**, and is exactly why it must be predicted. The hazard is the
repair: an implementer facing four red digests re-captures the dictionary wholesale, and the eight
`LayeredRenderer` and `OutlineRenderer` pins — which must **not** move, since neither renderer's
output changes (`LayeredRenderer` dots = 0, `OutlineRenderer` builds no `Canvas`) — silently lose
their guard. That converts the repair batch's C-53 false-failure arm into a rubber stamp.

**Inc-3 breaks the rail guard, and `LLR-N06.2.1`'s census under-derives by 7.** `LLR-N06.2.1:1478`
deletes `OutlineRail.collapsed` (`rail.py:35`) and `OutlineRail.toggle` (`rail.py:42`) and widens
`show`. Its amended threshold (`A-41`, `QA-N-07`) reads: *"'0 remaining references' names no
reference, so nobody can check the census found them all… Re-executed at `d877784`,
`OutlineRail.toggle` has **2** call sites, both in `tests/test_rail.py` (`:73`, `:77`), and both are
predicted red. They are named here at Phase 1 rather than discovered at the gate."* Executed:

```
$ grep -rn "\.collapsed\b\|collapsed=" mapper/ tests/ --include=*.py
mapper/widgets/rail.py:35 :46 :47 :49 :85 :227      (the definition being deleted)
tests/test_repair_depth.py:841   in walk
tests/test_repair_depth.py:949   in test_tc_r30_visible_rows_agrees_with_the_shipped_recursive_implementation
tests/test_repair_depth.py:1055  in test_c53_the_rail_renders_legacy_identically_to_master
$ grep -rn "\.toggle(" mapper/ tests/ --include=*.py
mapper/app.py:1259   in action_collapse_branch          <- PRODUCTION, not named
tests/test_rail.py:73  :77                              <- the 2 that are named
$ grep -rn "\.show(" mapper/ tests/ --include=*.py      (rail only)
mapper/app.py:1374   in refresh_canvas
tests/test_repair_depth.py:1158  in test_tc_r30_the_indent_cap_cannot_change_a_rendered_row
```

**The enumerated set is 2 of 9 external references** — and one of the seven it misses is a
**production** call site (`mapper/app.py:1259`), while another (`tests/test_repair_depth.py:1055`) is
the rail byte-identity guard itself, parametrized over five fold configurations. The amendment fixed
*"a zero that names no reference"* by substituting *an enumeration that is short by seven*, which is
the same defect with a number attached. `C-18` — a premise counted at one file scope is under-counted
tree-wide — fires on the amendment.

**Discharge for `P2-B4`:** `LLR-N06.2.1`'s threshold shall derive the supersession set rather than
enumerate it (`grep`/`ast` over `mapper/` **and** `tests/` for the attribute and the method, asserting
the derived set is non-empty before evaluating it, exactly as `LLR-N06.2.5` and `LLR-S06.3.1` already
do), and `HLR-CNV.1` and `LLR-N06.2.1` shall each carry a **predicted-red** clause naming
`tests/test_repair_depth.py`'s pins with the rule that only the digests whose renderer's output the
increment actually changes may be re-captured, one at a time, each with its own recorded reason. The
eight `LayeredRenderer` and `OutlineRenderer` digests are predicted **green** and re-capturing them is
a gate failure.

### 6.4 · Budget after the rulings

| Inc | Source files after `#D21` and `#D22` | vs budget |
|---|---|---|
| 1 | `darkside.py`, `canvas.py`, `views/radial.py`, `app.py` — `LLR-COERCE.1` lands in `darkside.py`, already present | **4** ✓ |
| 2 | `views/state.py` *(new)*, `views/layered.py`, `views/lane.py`, `views/outline.py`, `views/radial.py`, `app.py` | **6 — declared breach**, unchanged |
| 3 | `app.py`, `widgets/rail.py`, `views/layered.py`, `keymap.py` — `LLR-COERCE.2` lands in `views/layered.py`, already present; **`LLR-N06.2.5` removed by `#D21`** | **4** ✓ *(was 5, undeclared)* |
| 4 | `search.py`, `app.py`, `views/layered.py`, `keymap.py` | **4** ✓ |
| 5 | `views/outline.py`, `views/radial.py`, `views/lane.py` | **3** ✓ |
| 6 | `search.py`, `app.py`, `views/layered.py`, `keymap.py` | **4** ✓ |
| 7 | `app.py`, `darkside.py`, `store.py` | **3** ✓ |
| 8 | `screens/help.py`, `darkside.py`, `app.py` | **3** ✓ |
| 9 | `keymap.py`, `screens/factory.py`, `screens/settings.py`, `app.py` — **`LLR-N06.2.5` added by `#D21`, adds no file** | **4** ✓ |

**`#D21` removes an undeclared breach rather than creating one.** That is the strongest argument for
option (a2) over (a1) and it is arithmetic, not judgement.

---

## 7 · `S-15` AND `HLR-N13.3` — CONFIRMED, WITH ONE CONDITION

**Architecturally right, and it does not create a second definition of *"too big"*.** Re-read
`HLR-N13.3` at `01-requirements.md:2553`–`:2644` in full. The reason it works is that the two bounds
are on **different dimensions**, each with exactly one owner:

| Dimension | Owner | Where |
|---|---|---|
| **count** | `MAX_RENDER_NODES = 12000`, shipped | `views/layered.py:15` enforced `:143` · `views/outline.py:14` at `:65` · `views/radial.py:28` at `:117` |
| **work** | `WORKSPACE_CARD_BUDGET_MS = 250`, new | `HLR-N13.3` threshold 2 |

Threshold 3 *consumes* the count refusal rather than restating it — *"A map of `> MAX_RENDER_NODES`
nodes is over budget by definition and needs no timing; the renderers already refuse it"* — which is
what keeps the count dimension single-owner and satisfies `D19`. The paragraph at `:2616`–`:2621`
states the *additional, not replacing* rule explicitly and cites the `D6`/`D14` precedent, which is
the sentence `A-25` says it is. **Confirmed.**

The `M-H5` mutant row (*reuse `MAX_RENDER_NODES` as the whole budget*) is the load-bearing one and it
is reddened by threshold 2 with the executed `allowed by MAX_RENDER_NODES: True` column on every row
of the DAG table — a mutant reddened by a column of its own evidence, which is the right shape.
`M-H2` (cap the map count) and `M-H3` (compute from `len(graph.nodes)`) are both correctly reddened by
the same threshold. The **51-node / ~1.9 s** acceptance fixture with the 73-node / 72.5 s shape as
demonstration is right: a 70-second node has no place in a gate, and 1.9 s against a 250 ms budget is
a 7.7× margin.

**`P2-C8` — one condition.** Threshold 1 is *"Mount completes in `< 1000 ms` for 200 maps of `<= 128`
nodes each."* That is an **absolute wall-clock assertion with no stated measured headroom**, unlike
threshold 2 whose 7.7× margin is derived. A gate that false-fails correct work on a slower CI box
costs as much as one that passes wrong work — `tests/test_repair_depth.py:807`'s own docstring says
so, and that file is the batch's neighbour. `HLR-N13.3` shall state the **measured** mount time for
the 200-map workspace at `d877784` and choose threshold 1 with a declared multiple of it, the way
threshold 2 is chosen. If the measured value is close to 1000 ms, the requirement must say so and pick
a different figure rather than shipping a coin-flip gate.

---

## 8 · FORWARD APPLICABILITY (C-49)

> Every output of this pass is named as the input of a later activity. Anything I could not name a
> consumer for was deleted from the draft rather than written down for symmetry.

| # | Output | Named consumer | Where the consumer reads it |
|---|---|---|---|
| 1 | `#D21` — re-parent `LLR-N06.2.5`; promote §3.0 to `HLR-COERCE`; edits a-1 … a-4 | requirements lane, amendment set 3 | `01-requirements.md` §3.0, §3.4, §6.5 |
| 2 | `#D22` — (b2) deferral; edits b-1 … b-4 | requirements lane (b-1, b-2, b-4); **ux lens** (b-3) | `01-requirements.md:107`, `:113`, `:3343`, `:3352`, `:3394`, §6.2 item 4; `01b-ux-decisions.md` DECISION 3 |
| 3 | `P2-B1` — the eight sites carrying the rejected cut | requirements lane | `01-requirements.md:2116`, `:2212`, `:2638`, `:2657`, `:3103`, `:3402`, `:3452`, `:4212` |
| 4 | `P2-B2` — `AT-009`, `AT-031`, `AT-040` disposition | requirements lane; QA lens census | `01-requirements.md` §3 `Acceptance:` lines; `01d-unpark-measurements.md` |
| 5 | `P2-B4` — the derived supersession set and the predicted-red clause | requirements lane; **Inc-1 and Inc-3 implementers**; Inc-1 and Inc-3 gate reviewers | `LLR-N06.2.1`, `HLR-CNV.1`; `tests/test_repair_depth.py` digest dictionaries |
| 6 | §5.1's protocol-aware A3 census (6 defs · 22 arg-ful sites · 25 zero-arg sites) | **Inc-2 implementer**; Inc-2 gate reviewer | `LLR-N07.2.2a`'s reverse census |
| 7 | `P2-C6` — the replacement threshold text for `LLR-N07.2.2a` | requirements lane; Inc-2 | `01-requirements.md:2038` |
| 8 | `P2-C5` + §5.4 — the `ViewState` / `IRenderer` creation LLR | requirements lane; Inc-2 | new LLR under `HLR-CNV.3` or `HLR-N07.2` |
| 9 | `P2-C1` — the corrected `canvas_rows` consumer list (4 sites, 3 files, `export.py` and `outline.py` off it) | requirements lane; **Inc-1** reverse census | `01-requirements.md` §4.2 `:3746`–`:3752`, `:3760`, `:5150` |
| 10 | `P2-C2` — `C-D4c` re-stated as a requirement clause | requirements lane; Inc-2 gate | `HLR-CNV.2` / `LLR-CNV.2.1` |
| 11 | `P2-C3` — the AT↔TC mapping (`#D15`, third time of asking) | requirements lane; **every increment gate** | `01-requirements.md` §5.2, as a third table or a column on the functional table |
| 12 | `P2-C4` — strike `with_header` from the proposed architecture | requirements/ARQ lane; Phase 6 docs | `ARCHITECTURE-proposed-at-ARQ.md:235`, `:275` |
| 13 | `P2-C7` — the increment that amends the live `docs/ARCHITECTURE.md` frozen rows | orchestrator (cut); Phase 6 docs | `docs/ARCHITECTURE.md:58`, `:134`, `:136`; `#D3`'s §4a rule-7 rewording rides with it |
| 14 | `P2-C8` — measured headroom for `HLR-N13.3` threshold 1 | requirements lane; Inc-7 | `01-requirements.md:2579` |
| 15 | §6.2's AT→increment table and the 46/51 validator reconciliation | orchestrator; DDR; Phase 4 | `03-increments/` task files; the `V2` disposition |
| 16 | `#D18` restated with grown scope (Inc-9 now also carries the notify census) | **security lens**, before Inc-6 and Inc-9 sign-off | this document §4.2 |

---

## 9 · EVIDENCE CHECKLIST

| Item | ✓/✗ | Evidence a third party can re-run |
|---|---|---|
| Constraints stated explicitly | ✓ | §6.4 budget table (≤4 source files, Inc-2's declared breach); 429-test baseline; serial chain; `git rev-parse HEAD` = `d877784` |
| At least 2 alternatives considered | ✓ | §2.1 options a1 / a2 / a3, with a3 shown unavailable by `grep -n "C-8" 01-requirements.md`; §3.1 options b1 / b2, with b1 shown structurally unavailable by the `.dots` probe |
| Recommendation has rationale tied to constraints | ✓ | §2.3 limb 2 ties `#D21` to Inc-3's ≤4-file budget; §6.4 shows `#D21` **removes** a breach; §3.5 ties `#D22` to `HLR-N16.2`'s evaluability |
| Risks listed | ✓ | `P2-B1`…`P2-B6`, `P2-C1`…`P2-C8` in §1.1; the digest-recapture hazard in §6.3; the eight-increment exposure window accepted and stated in §2.5 |
| Cost / latency estimated where relevant | ✓ | §7: `WORKSPACE_CARD_BUDGET_MS = 250` vs the 51-node ~1.9 s fixture (7.7× margin) confirmed; threshold 1's missing headroom raised as `P2-C8`. No model calls, no network — cost is source-file budget and increment count |
| Diagram included when flow is non-trivial | ✓ | §6.2's AT→increment table; §5.1's two-protocol census table; §6.4's budget table. The batch's flow is a serial chain with one branch point (Inc-7's resequenceability), which a table carries better than a graph |
| What would change the recommendation is stated | ✓ | §2.5 (a `notify` site inside `mapper/views/` or `mapper/widgets/`, executed **0**); §3.6 (a requirement giving `LayeredRenderer` free-angle geometry); §5.1 (`#D4`'s reversal condition re-executed, still unmet) |
| **Two-layer requirements: Acceptance block + `AT-NNN`, BOTH chains** | **✗** | **Unchanged from my first pass and this is the third asking.** Behavioral US→AT exists (§5.2 table 1, `:3965`). Functional US→HLR→LLR→TC exists (§5.2 table 2, `:4013`). `grep -rn "D15\|AT↔TC" 01-requirements.md` → **NONE**; the chains still never cross. Compounded by `P2-B2`: three live `AT` ids are in the behavioral chain and in **neither** the functional chain nor any increment |

**Executed-verification note (C-43).** Every count, address and verdict above was produced in this
session against `d877784` by a command whose output is pasted. Probe scripts are in the session
scratchpad (`a3census.py`, `notify_census.py`, `dots_probe.py`, `glyphs.py`, `atcensus.py`,
`owner.py`); each is short enough to re-derive from the pasted output alone. **Nothing under
`mapper/` or `tests/` was modified**, no pytest gate was run (C-25), and `~/.claude` was not touched.

---

## 10 · SEAL

| | |
|---|---|
| **Date** | 2026-08-27 |
| **Base** | `d877784`, executed |
| **Verdict** | **REJECTED — iterate to Phase 1 for amendment set 3.** Six blockers, eight conditions, each individually named and dischargeable by a document edit. No increment starts. |
| **New decisions** | `PDR-2026-08-26-ui-next-batch-02#D21` (flag a — re-parent `LLR-N06.2.5`; promote §3.0 to `HLR-COERCE`) · `PDR-2026-08-26-ui-next-batch-02#D22` (flag b — deferral, with the prose and the set-equality target both amended) |
| **Sealed decisions re-affirmed** | `#D1` `#D3` `#D4` `#D5` `#D5a` `#D5b` `#D6` `#D7` `#D8` `#D9` `#D10` `#D11` `#D12` `#D13` `#D14` `#D16` `#D17` `#D18` `#D19` `#D20` |
| **Sealed decisions half-discharged** | `#D2` (struck in the requirements, live in the proposed architecture) · `#D15` (untouched by 41 amendments) |
| **Corrections to my own first pass** | The `docs/ARCHITECTURE.md` working-tree amendment I cited **no longer exists** (§4.3) · my "3 production call sites" and the orchestrator's "29 / 14" both answer the wrong question; the migration surface is **6 definitions and 22 arg-ful call sites across 9 files** (§5.1) · every `rows()` address in my first pass is stale, and the file count was 4 not 3 (§5.1) |
| **Cut** | **Confirmed in content** (9 increments, serial; `8 before 9` correctly dissolved; every new and split `AT` absorbed without re-cutting). **Rejected in the document that carries it** — `P2-B1` |
| **Security** | `#D18` stands and its scope has **grown**: `#D21` adds the notify census to Inc-9. C-3 discharged as design by `A-04` and `A-05`; **C-4 and C-8 are partial** — `P2-B5`, `P2-B6`. No security lens has run since the parked `02b` |
| **Baseline to preserve** | 429 collected · 413 fast + 16 slow · both exit 0 · ruff 29 pre-existing |
