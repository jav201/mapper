# PDR — `2026-08-26-ui-next-batch-02` · architect lens

| | |
|---|---|
| **Station** | PDR (Preliminary Design Review) — architect lens |
| **Batch** | `2026-08-26-ui-next-batch-02` · variant B «atlas» + round-10 capabilities |
| **Date** | 2026-08-26 |
| **Participants** | architect lens (this document). ux lens ruled separately in `01b-ux-decisions.md`. security lens **not yet run** — see `PDR-2026-08-26-ui-next-batch-02#D18`. |
| **Repo state at review** | `d6b60e6` + uncommitted `docs/ARCHITECTURE.md` (ARQ amendment) and `.dev-flow/2026-08-26-ui-next-batch-02/` |
| **Baseline** | `pytest -q` → **245 passed in 35.01s** (executed) |
| **Verdict** | **APPROVED WITH CONDITIONS.** Two frozen-interface moves approved (one with conditions). The 7-increment cut is **STALE and REJECTED**; a 9-increment cut is re-derived below. Four open questions ruled. Three requirement artifacts rejected as unconsumed. |

**Decision id grammar (validator V23):** every decision in this document is
`PDR-2026-08-26-ui-next-batch-02#D<n>`. No other form appears.

---

## 0 · BLUF

**The design is sound and implementable, but the cut it arrived with is stale and three of its
recorded numbers are wrong.** The `ViewState` shape is right and I approve it after deleting one
speculative field. The `Canvas` freeze move is safe — its blast radius is **smaller than the batch
believes**, and I measured it. The increment cut predates S-8 and D13 and now hides a **6-file
undeclared budget breach in Inc-7** plus an **ordering inversion** that would make US-N16's own
acceptance unpassable. `⇥` is ruled out and the unified *coincidencias* walk is ratified. `◍` is
ruled out of the batch, with the migration story it would need written down so the ruling is a
decision and not a deferral.

**What I am rejecting outright**, each with executed evidence below:

| # | Rejected | Why |
|---|---|---|
| 1 | `ViewState.with_header` | Zero requirement citations, zero non-default call sites. C-49 empty row. |
| 2 | The ARQ 7-increment cut | C-21: the AT set changed (S-8, D13) after the cut was set. |
| 3 | `AT-027`, `AT-028`, `AT-045` | Each appears exactly once in §3 and is never described. They observe nothing. |
| 4 | `◍` repo provenance (Q-5) | No persisted provenance, no `maps` table, **no migration machinery at all**. |
| 5 | `⇥` for the lens walk (Q-7) | Two green shipped guards; `tab` is the inspector's only keyboard route. |
| 6 | PLAN §9 D12's "17 of 27 / the ten it drops" | Pilot-measured: **16 of 27, and the eleven it drops are the entire `view` group.** |

---

## 1 · The two frozen-interface moves — ruled SEPARATELY

### 1.1 · `IRenderer.render(self, graph: Graph, state: ViewState) -> Text`

**`PDR-2026-08-26-ui-next-batch-02#D1` — APPROVED WITH ONE DELETION.**

The shape is right, and the ARQ's argument for it is the rare kind that is made from evidence rather
than taste. I re-executed both of its supporting defects and both hold:

| ARQ claim | My execution | Holds? |
|---|---|---|
| `IRenderer` is not a Python type | `grep -rn "IRenderer" mapper/` → 2 prose comments (`views/layered.py:228`, `widgets/rail.py:6`), no class, no Protocol | ✓ |
| 6 `def render` in 4 view files | `lane.py:108,171,311`, `layered.py:78`, `outline.py:17`, `radial.py:33` | ✓ |
| 3 production call sites | `app.py:711`, `:1301`, `:1671` | ✓ |
| Call sites have drifted — export loses diff tinting | `app.py:1301` passes `query=` **and** `diff=`; `app.py:1671` passes `query=` **only**. Read both. | ✓ |
| `**kwargs` swallows `query` | `layered.py:84` names `query`; `lane.py:114,177,317`, `outline.py:23`, `radial.py:39` take `**kwargs` and never read it | ✓ |

**One correction to the ARQ's own wording.** §4a says *"`**kwargs` is abolished from all six."*
Executed: `grep -rn "\*\*kwargs" mapper/views/` returns **five** hits, not six. `LayeredRenderer.render`
has no `**kwargs` — it has three explicitly-named extra parameters (`query`, `with_header`, `diff`).
The migration is *five* `**kwargs` removals plus *one* named-parameter collapse. Trivial, but a PDR
that ratifies a miscount teaches the batch that counts are decorative.

#### The `ViewState` field audit — speculative fields, and missing fields

I tested each of the eleven fields against two questions: **does a requirement need it**, and **does a
shipped call site pass it**. A field needs to pass *at least one*. Passing neither is speculative
design.

| Field | Requirement citing it | Shipped call site passing it | Verdict |
|---|---|---|---|
| `w`, `h` | Threshold text only (LLR-N06.1.1, LLR-CNV.1.3), never as a named field | `app.py:711`, `:1301`, `:1671` all pass `w=`/`h=` | **KEEP** — migration-preserving |
| `pan_x`, `pan_y` | LLR-N06.1.1, LLR-N06.1.2 | new | **KEEP** |
| `selected_id` | **String absent from the requirements doc (0 hits).** But HLR-N07.3 is *"the system shall move **the selection** to the next matching node"* — `selected_id` **is** the search cursor | all three call sites pass `selected_id=` | **KEEP** — the string-absence is a naming artifact, not a gap |
| `focus_owner` | LLR-CNV.3.1, HLR-CNV.3 (6 hits) | new (closes B-05) | **KEEP** |
| `folded` | LLR-N06.2.1 | new | **KEEP** |
| `hits` | LLR-N07.1.1 | new (replaces `query`) | **KEEP** |
| `lens_matches` | LLR-N14.2.1, LLR-N14.2.2 | new | **KEEP** |
| `diff` | 0 requirement hits | `app.py:1301` passes `diff=` | **KEEP** — migration-preserving; deleting it deletes shipped diff tinting |
| `with_header` | **0 requirement hits** | **0 call sites.** Declared `layered.py:85`, read `layered.py:122`, and **no caller anywhere in `mapper/` or `tests/` ever passes it** — executed | **DELETE** |

**`PDR-2026-08-26-ui-next-batch-02#D2` — `with_header` is struck from `ViewState`.** It is a
parameter that has been permanently `True` for its entire life. Carrying it into the new contract
migrates a dead branch into a frozen dataclass and makes the very first field of the new interface
one that nothing reads. Inc-2 removes the parameter and makes the header unconditional at
`layered.py:122` — behaviour-preserving, because the value has never been anything but `True`.
*Re-open if* a requirement appears that needs a headerless render (the export path is the plausible
one; it does not ask for it today).

#### Is a field MISSING? — two candidates tested, both resolved

1. **A search cursor / current-hit index.** Not needed. HLR-N07.3 makes the walk move *the
   selection*, so `selected_id` is the cursor. One field, one meaning. ✓
2. **The Q-6 third outcome class.** `lens_matches: frozenset[str] | None` encodes only two states,
   while §2.8.2 declares three (`MATCH` / `EMPTY` / `UNDEFINED-FIELD`). I traced where each is
   painted: `UNDEFINED-FIELD` is decided at the **parse layer** (`LensQuery.unknown_keys`,
   LLR-N14.1.1) and painted by `app` in the count line and chip — it never reaches a renderer.
   LLR-N14.2.2 requires only that `None` and `frozenset()` paint differently. **Two states is
   sufficient and correct.** ✓ Recorded so a later reader does not re-litigate it.

#### `views/state.py` as the home — the import-cycle claim, EXECUTED

ARCHITECTURE §4a rule 7 asserts: *"`views/__init__.py` imports `layered`, and `layered` imports
`ViewState` — putting the dataclass in `__init__` creates an import cycle. This is a mechanical
constraint, not a style preference."*

I did not reason about this. I built the exact topology in a scratch package and ran it both ways.

| Variant | `__init__.py` layout | Result |
|---|---|---|
| **A** | `from .layered import …` **then** `class ViewState` | `ImportError: cannot import name 'ViewState' from partially initialized module … (most likely due to a circular import)` |
| **B** | `class ViewState` **then** `from .layered import …` | `IMPORT OK`; `LayeredRenderer().render(None, ViewState())` returns normally |

**`PDR-2026-08-26-ui-next-batch-02#D3` — the conclusion is ratified, the stated reason is corrected.**
`views/state.py` is the right home, but **not because a cycle is mechanically unavoidable** — variant B
proves it is avoidable by ordering. It is the right home because variant B's correctness depends on
statement order inside a module, which is invisible, unenforced, and reversible by any import-sorter.
`ruff 0.8.4` is installed in this environment and `E402` (module-level import not at top of file)
exists precisely to forbid variant B's shape.

The honest justification is **fragility, not impossibility**, and it must be recorded that way. A
design document that overstates a constraint as mechanical is one nobody can audit: the next reader
who tries variant B finds it works, and then trusts §4a less on everything else. Conclusion APPROVED;
ARCHITECTURE §4a rule 7 to be reworded at Phase 6 to say *"order-dependent and therefore forbidden"*.

**Dependency bans re-checked for the new file** (executed): `views/state.py` will import
`rich.text`, `mapper.diff` (for `DiffResult`) and `mapper.model`. `views → diff` already exists at
`layered.py:9`, so **no new edge**. `grep -rn "textual" mapper/views/` → nothing. Ban intact. ✓

---

### 1.2 · `Canvas` — the second, unnamed A3

**`PDR-2026-08-26-ui-next-batch-02#D4` — APPROVED, and the blast radius is smaller than the batch
believes.**

**The freeze was real.** `git show HEAD:docs/ARCHITECTURE.md` line 134 reads, verbatim:

> `| Canvas drawing buffer | canvas | views | put(x,y,ch,tone), wire(x,y,mask,tone), elbow_down(...), rows() -> list[str] | yes for MVP |`

So D9's premise checks out: `Canvas` **was** declared frozen at `HEAD`, and the working-tree
amendment has already flipped it to *"NO — Inc-1 owns it. See R-016."* PDR approving it explicitly is
therefore the correct procedure, not a formality.

**The frozen row was wrong about its own subject, twice.** Before approving the move I checked what
was actually frozen:

- It declares `rows() -> list[str]`. Executed: `canvas.py:67` is `def rows(self) -> list[Text]`. The
  freeze described a **return type the code has never had**.
- It omits `wire`'s sibling `edge` and lists `dline`, which `grep -rn "dline" mapper/ tests/` shows
  does not exist. (ARQ caught the `dline` half; the `list[str]` half was not caught.)

A freeze that misstates the return type of the one method its consumers index is not a constraint that
was protecting anything. This *strengthens* the case for moving it now, under a review, rather than
leaving it nominally frozen and actually undefined.

#### The measured blast radius

The brief states *"its `rows()` output bytes change and `export.save_svg` consumes them (trigger B4).
Say what the blast radius actually is — measure it."* Measured:

| Surface | Count | Probe |
|---|---|---|
| Modules importing `canvas` | **3**, all in `views` | `grep -rn "from mapper.canvas import"` → `views/lane.py:10`, `views/layered.py:8`, `views/radial.py:9` |
| `rows()` call sites | **4**, **all inside `mapper/views/`** | `grep -rn "\.rows()"` → `lane.py:216`, `lane.py:299`, `layered.py:223`, `radial.py:165` |
| `rows()` call sites outside `views` | **0** | same probe |
| Direct `Canvas` unit tests | **0** | no `tests/test_canvas.py` exists |
| Tests reaching `rows()` transitively | **5** | `test_layered`, `test_lane`, `test_radial`, `test_legacy_fixture`, `test_export` |

**The B4 claim needs correcting: `export.save_svg` does NOT consume `Canvas.rows()`.** Read
`mapper/export.py:15-19` — `save_svg(text: Text, path)` consumes a `rich.Text`. The only production
caller is `app.py:1679`, fed by `app.py:1671`'s `renderer.render(...)`. `Canvas.rows()` output reaches
the SVG **transitively, through a renderer**, and `mapper/export.py` itself is untouched and unaware.

That distinction is not pedantry, it changes who pays. The IFC (§4.2 `canvas_rows`) lists
`mapper/export.py` as a *consumer* of the `rows()` address. It is not one. Its consumer set is
**exactly the four `views` call sites**, and the export path is a downstream *observer* of renderer
output. LLR-CNV.2.1 already gets this right — it says *"none changed in `mapper/export.py`"* and
drives the assertion through a renderer. **The IFC row is what is wrong, not the LLR.**

**Conditions on the approval:**

- **C-D4a — the IFC `canvas_rows` consumer list is corrected** to the four `views` call sites, with
  `mapper/export.py` moved to a declared *transitive observer* line. Its absence from the direct list
  is what makes Inc-1's reverse census countable.
- **C-D4b — `Canvas` gets a direct unit test in Inc-1.** It has **zero** today. A buffer whose output
  bytes are being changed under an A3, with no test that addresses it directly, is being changed
  blind. This is the cheapest control in the batch: `rows()` is 16 lines and takes no event loop.
- **C-D4c — AT-007 / AT-009 (the export arm) are re-run after Inc-2.** Inc-1 asserts export bytes
  against `app.py:1671`'s call site; Inc-2 rewrites that call site. An acceptance verified against a
  signature that is about to change is verified against nothing.

**Why approve rather than defer.** `canvas` has one inbound edge (`views`), no outbound edges, no
Textual, and 82 lines. It is the least-coupled module in the tree. The change is additive (two new
dict layers) and widening, with the address and cardinality unchanged. Deferring it would strand
HLR-CNV entirely and force `views/radial.py:47-48` to keep monkey-patching attributes onto a class
that does not declare them — which is the actual current state and is worse than the change.

**What would reverse this ruling:** evidence that any consumer outside `mapper/views/` indexes
`rows()` output positionally. I looked for one and there is none.

---

## 2 · Forward applicability (C-49)

> *Every output of this design review must be NAMED as the input of a later activity. An artifact that
> is nobody's input should not exist.*

### 2.1 · This review's own outputs

| # | Output | Named consumer | Where the consumer reads it |
|---|---|---|---|
| 1 | `PDR-2026-08-26-ui-next-batch-02#D1`/`PDR-2026-08-26-ui-next-batch-02#D2` ViewState roster minus `with_header` | Inc-2 implementer | `mapper/views/state.py` at creation |
| 2 | `PDR-2026-08-26-ui-next-batch-02#D3` `views/state.py` home + corrected justification | Inc-2 implementer; Phase 6 docs | file placement; ARCHITECTURE §4a rule 7 rewording |
| 3 | `PDR-2026-08-26-ui-next-batch-02#D4` Canvas approval + conditions C-D4a/b/c | Inc-1 implementer; Inc-1 gate reviewer | `mapper/canvas.py`; `tests/test_canvas.py` (new); IFC §4.2 |
| 4 | `PDR-2026-08-26-ui-next-batch-02#D5` the re-derived 9-increment cut | every increment; DDR | `.dev-flow/…/03-increments/` task files |
| 5 | `PDR-2026-08-26-ui-next-batch-02#D6` Q-7 ruling (unified *coincidencias*) | Inc-4 (seat rows), Inc-6 (walk reuse) | `mapper/keymap.py`; `mapper/app.py::MapScreen` |
| 6 | `PDR-2026-08-26-ui-next-batch-02#D7` Q-5 ruling (`◍` out) + the migration story it would need | batch close | `BACKLOG.md` |
| 7 | `PDR-2026-08-26-ui-next-batch-02#D8` Q-8 ruling (bare word = malformed) | Inc-6 implementer | `mapper/search.py::parse_lens` |
| 8 | `PDR-2026-08-26-ui-next-batch-02#D9` Q-9 ruling (migrate both, gated) | Inc-9 implementer; DDR | `mapper/keymap.py`, `screens/factory.py`, `screens/settings.py` |
| 9 | `PDR-2026-08-26-ui-next-batch-02#D10` Q-10 dispositions (3 census sites) | Inc-1 (2 sites), Inc-9 (1 site) | `mapper/darkside.py`; the census exception register |
| 10 | `PDR-2026-08-26-ui-next-batch-02#D11` the synthetic fixture SPEC (C-55 limb 2) | Inc-3 implementer | `fixtures/` — new file, before Inc-3's gate |
| 11 | `PDR-2026-08-26-ui-next-batch-02#D12` LLR-N07.2.2 split into a/b | requirements amendment; Inc-2 & Inc-5 | `01-requirements.md` §6.5 |
| 12 | `PDR-2026-08-26-ui-next-batch-02#D13` S-8 count correction (16/11, entire `view` group) | PLAN §9 D12 amendment; Inc-8 acceptance | `PLAN.md`; AT text for Inc-8 |
| 13 | `PDR-2026-08-26-ui-next-batch-02#D14`–`PDR-2026-08-26-ui-next-batch-02#D17` rejections of unconsumed requirement artifacts | requirements amendment | `01-requirements.md` §6.5 |
| 14 | `PDR-2026-08-26-ui-next-batch-02#D18` security-lens referral | security lens, before Inc-9 sign-off | this document, §6 |

**No row in this table has an empty consumer column.** Anything I could not name a consumer for is not
in it — it was deleted from the draft rather than written down for symmetry.

### 2.2 · Applying the same test to the requirements set

**LLRs that no increment will consume: none.** All 48 LLRs land in an increment under the cut in §4.
Two are worth flagging as *weak* rather than empty:

- **LLR-S07.1.3** declares `Touched symbols: none` and asserts the *outcome* of LLR-S07.1.1. It is an
  acceptance restated as a requirement. Keep — it is the only limb that observes the user-visible
  result — but it must not be counted as a separate unit of work at the gate.
- **LLR-N06.3.2** declares `Touched symbols: none new`. It is an identity between two other LLRs'
  outputs. Keep, and it is the one that needs `PDR-2026-08-26-ui-next-batch-02#D11`'s fixture to be provable at all.

**ATs that observe nothing a user can see — three, and I reject them:**

**`PDR-2026-08-26-ui-next-batch-02#D14` — `AT-027`, `AT-028` and `AT-045` are struck.** Each appears
**exactly once** in the whole of §3 — inside a story's `Acceptance tests:` enumeration — and is never
described, never attached to an HLR, never given an observable, and never given a TC. An acceptance
test with no statement of what it observes cannot fail, which makes it the purest form of the vacuous
check. Either Phase 1 writes an observable for each in §6.5, or they are deleted from the story
enumerations so the AT count drops from 47 to 44. **Do not carry them as ids.**

**Five ATs are orphaned from the HLR chain but DO observe something real** — `AT-002`, `AT-009`,
`AT-024`, `AT-031`, `AT-040`. Each is named on a story and in the QC-3 boundary catalog but on no HLR,
so the transitive `AT → HLR → LLR` path is broken. These are **traceability defects, not vacuous
tests**. The cut in §4 gives each of them an owning increment (`AT-024` gets one for the first time,
in Inc-5), and §6.5 must attach each to its obvious HLR.

**`PDR-2026-08-26-ui-next-batch-02#D15` — the LLR→AT chain is not expressed anywhere and must be.**
Executed: exactly **one** of 48 LLRs carries its own `Acceptance:` line (LLR-N06.2.4 → `AT-046`,
`AT-047`). Every other AT is reachable only by walking up to the parent HLR, and §5.2's two
traceability tables never cross — Table 1 is US→AT, Table 2 is Requirement→TC, and **no table anywhere
maps AT→TC**. A reviewer cannot answer *"which TC exercises AT-030?"* from the traceability section.
This is the "BOTH traceability chains exist" item on the gate checklist and it is currently **half
built**. §6.5 owes an AT↔TC column before Inc-1 starts.

**Two HLRs have no LLRs:** `HLR-S06.2` (256-colour downgrade) and `HLR-N16.3` (doubled chord
reserved). Both are green-pre-state guards with a single TC each. Acceptable as leaves — recorded so
the decomposition gap is not mistaken for an omission. Note that `HLR-S06.2` is *also* the item §6.2
declares unobservable by any test this batch can write; it is therefore an HLR with **no
decomposition and no mechanical acceptance**, resting entirely on the ux lens. That is a legitimate
place to land, but it must be stated as such at the gate rather than counted as covered.

---

## 3 · Boundary walk — do the requirements respect the ARQ bans?

I walked all 48 LLRs against ARCHITECTURE §3 and then executed the bans against the tree.

### 3.1 · Executed state of the bans

| Ban | Probe | State |
|---|---|---|
| `views` → textual | `grep -rn "textual" mapper/views/` | **0** ✓ |
| `design` → textual | `grep -n "^from\|^import" mapper/darkside.py` → stdlib + `rich.markup`, `rich.panel`, `rich.text` only | **clean** ✓ |
| `canvas` → anything | `mapper/canvas.py:4` imports `rich.text` only | **clean** ✓ |
| `keymap` → anything | `mapper/keymap.py` imports `dataclasses`, `typing` only. (`textual_bindings` at `:175` is a *function name*, not an import.) | **clean** ✓ |
| `export` → app | `mapper/export.py` imports `io`, `pathlib`, `rich` only | **clean** ✓ |
| `views` → `search` | `grep -rn "search" mapper/views/` | **0** ✓ |
| `screens` → `app` | `grep -rn "from mapper.app import" mapper/screens/` → **`factory.py:343`, and only that** | **1 violation — carry B-02, not fixed here** ✓ |

### 3.2 · LLRs that would require a banned import

**Zero LLRs mandate a banned import.** Four are *designed around* a ban and should be recognised as
such rather than merely permitted — LLR-CNV.3.1 (`focus_owner` as `str`, not a widget), LLR-N06.2.1
(`show(graph, cursor, folded)` so the rail never reads back from `app`), LLR-N07.1.1 and LLR-N14.2.1
(`frozenset[str]`, so no `views → search`).

**Three LLRs are under-specified in a way that could produce one.** All three are in US-N16, and all
three are now in Inc-8/Inc-9:

| LLR | The risk | Ruling |
|---|---|---|
| **LLR-N16.2.1** — glyph vocabulary in `darkside.py`, read by both `views/layered.py` (headless) and `screens/help.py` (Textual) | The LLR never states the *representation* of "the style applied to each glyph". If it is a Textual type or a CSS construct, it is `design` → textual **and** transitively `views` → textual | **`PDR-2026-08-26-ui-next-batch-02#D16` — the vocabulary is `tuple[str, str, str]` (glyph, Rich style string, caption) and nothing else.** `darkside.py` already returns Rich style strings and `help.py:74-75` already consumes them that way (`Text.assemble` with `darkside.INK` / `darkside.MUT`). The compliant route exists and is already the house idiom; the LLR just failed to name it. Both bans stay intact by construction. |
| **LLR-N16.2.2** — the legend names "the view opened from" | If `HelpScreen` reads its source screen's class or attributes, that is `screens` → `app` — banned, and it would *widen* the B-02 carry rather than hold it | **`PDR-2026-08-26-ui-next-batch-02#D17` — the view name and glyph vocabulary are passed IN at construction**, exactly as `HelpScreen(scope)` already does today (`help.py:55-57`; caller `app.py:1987`). `app` may import `screens`; `screens` may not import `app`. Signature becomes `HelpScreen(scope, view_name, glyphs)`. **No new inbound edge.** |
| **LLR-N16.1.2** — edits `screens/factory.py` | That file carries the recorded, unwaived `screens → app` back-edge at `:343`, whose remediation is explicitly not authorised this batch | **Permitted, with a standing constraint:** Inc-9 may edit `factory.py` but **must not touch `:343`** in either direction. The B-02 carry neither closes nor widens. Its reverse census at DDR asserts the line is byte-identical. |

**One latent smell, recorded not fixed.** LLR-CNV.1.2 requires `rows()` to apply a background tone
from the `bgs` layer. ARCHITECTURE gives `canvas` the dependency set `—`. If an implementer resolves
that tone by importing `darkside`, it contradicts that row (though it is not one of the enumerated
bans). **Constraint on Inc-1: the tone travels as a written value inside `bgs`; `mapper/canvas.py`
gains no import.** Its current import list is one line (`rich.text`) and must stay one line.

---

## 4 · The increment cut — re-derived under C-21

**`PDR-2026-08-26-ui-next-batch-02#D5` — the ARQ 7-increment cut is STALE and is replaced.**

C-21 fires: the AT set changed after the cut was set. **S-8** (help truncation) and **D13** (five
routes drop the scope; two screens declare no `KEY_SCOPE`) both landed at Phase 1, both after the ARQ
worksheet was written, and neither is costed in it. Re-deriving surfaced two things the stale cut hid.

### 4.1 · What re-derivation exposed

**(a) Inc-7 is a 6-file undeclared breach.** The ARQ gives Inc-7 three files
(`screens/help.py`, `app.py`, `darkside.py`). Post-D13 it must also touch `screens/factory.py`,
`screens/settings.py` and `keymap.py` — **six**, against a budget of four, undeclared. The batch's
only *declared* breach is Inc-2's. An undeclared one is exactly what V9 exists to catch.

**(b) An ordering inversion that makes US-N16's acceptance unpassable.** This is the sharper finding.
PLAN §9 D12 rules that US-N16's set-equality assertion **must read the painted panel** and never
`_render_keymap()`'s return value (C-32). I pilot-measured the painted panel:

```
size=(118, 34)   declared=27   painted=16   MISSING=11
size=(200, 80)   declared=27   painted=16   MISSING=11
#help-dialog size=Size(width=76, height=26)   #help-content size=Size(width=76, height=38)
```

The content widget is laid out at **height 38 inside a container of height 26** and the overflow is
discarded in silence. **Therefore AT-041/AT-042, read off the painted panel for scope `map`, CANNOT
PASS until the truncation is fixed.** The ARQ cut has scope-routing and truncation in the same
increment with no ordering between them; they must be two increments, truncation first.

**(c) Correction to D12's numbers — `PDR-2026-08-26-ui-next-batch-02#D13`.** D12 records *"paints 17
of 27"* and *"the ten it drops are the entire `view` group"*. Pilot-measured at both sizes:
**16 painted, 11 missing** — and the missing set is **exactly the `view` group, which has eleven
members, not ten**. D12's own prose is internally inconsistent (it says "the entire view group" and
then lists ten of its eleven; `m cobertura` is the one it omits). The mechanism D12 identifies is
correct and the ruling stands; the arithmetic is amended. Group membership executed:

```
view  =  alternar diff        MISSING       view  m  cobertura              MISSING
view  I  mostrar/ocultar ficha MISSING      view  n  siguiente faltante     MISSING
view  R  mostrar/ocultar rail  MISSING      view  o  alternar outline       MISSING
view  e  exportar svg          MISSING      view  r  alternar radial        MISSING
view  f  alternar foco         MISSING      view  z  plegar rama            MISSING
view  g  ir al rail            MISSING                                    (11 of 11)
```

### 4.2 · The re-derived cut — 9 increments, serial

Parallelism is not re-derived: ARQ measured **0 of 21 pairs parallelisable**, `modules(A) ∩ modules(B)
⊇ {app}` without exception, and splitting Inc-7 and Inc-4 only adds `app.py`-touching increments. The
chain stays serial. Budget **≤4 SOURCE files**; tests uncapped.

| Inc | Scope | LLR ids | AT ids | SOURCE files | n | Depends on |
|---|---|---|---|---|---|---|
| **1** | S-6 tokens · S-7 layout defect · **Canvas A3** | S07.1.1–.3, S06.1.1, S06.3.1–.4, CNV.1.1–.1.3, CNV.2.1 | 001–009 | `darkside.py`, `canvas.py`, `app.py`, `views/radial.py` | **4** | — |
| **2** | **ViewState + IRenderer A3** — signature only, behaviour-neutral | N07.2.2**a** *(new, see PDR-2026-08-26-ui-next-batch-02#D12)*, CNV.3.1 | 010 | `views/state.py` *(new)*, `views/layered.py`, `views/lane.py`, `views/outline.py`, `views/radial.py`, `app.py` | **6 — DECLARED BREACH** | 1 |
| **3** | US-N06 escala — pan, fold, overflow | N06.1.1, .1.2, .2.1, .2.2, .2.3, .3.1, .3.2, .3.3 | 011–017 | `app.py`, `widgets/rail.py`, `views/layered.py`, `keymap.py` | **4** | 2 |
| **4** | US-N07 búsqueda + **the seat rebind (D10)** | N07.1.1, .1.2, .2.1, .3.1, .3.2, .3.3, N06.2.4 | 018–023, 046, 047 | `search.py`, `app.py`, `views/layered.py`, `keymap.py` | **4** | 3 |
| **5** | Hit painting in the three remaining renderers | N07.2.2**b** *(new, see PDR-2026-08-26-ui-next-batch-02#D12)* | **024** | `views/outline.py`, `views/radial.py`, `views/lane.py` | **3** | 4 |
| **6** | US-N14 lente | N14.1.1–.1.3, .2.1–.2.3, .3.1–.3.3 | 032–040 | `search.py`, `app.py`, `views/layered.py`, `keymap.py` | **4** | 4 |
| **7** | US-N13 sala | N13.1.1–.1.4, N13.2.1 | 025, 026, 029, 030, 031 | `app.py`, `darkside.py`, `store.py` | **3** | 1 *(resequenceable)* |
| **8** | **S-8 truncation + glyph vocabulary** (the legend panel) | N16.2.1, .2.2, .2.3; HLR-N16.3 *(no LLR)* | 043, 044 | `screens/help.py`, `darkside.py`, `app.py` | **3** | 1 |
| **9** | Help scope routing + `KEY_SCOPE` declarations + seat migration | N16.1.1, N16.1.2 | 041, 042 | `keymap.py`, `screens/factory.py`, `screens/settings.py`, `app.py` | **4** | **8** *(hard)*, 4 |

`AT-027`, `AT-028`, `AT-045` are absent because `PDR-2026-08-26-ui-next-batch-02#D14` strikes them. `AT-004` rides HLR-S06.2 in Inc-1
as a ux-lens item with no mechanical arm (§2.2).

### 4.3 · The rulings the cut encodes

**`PDR-2026-08-26-ui-next-batch-02#D5a` — the A3s, and who owns them. There are TWO, and neither is
split.**

- **Inc-2 owns the `ViewState` / `IRenderer` A3, whole.** Six source files, declared over budget. The
  ARQ's justification is correct and I ratify it: between two halves the old signature and the new one
  would both be live and the suite would be green on a contract nobody holds.
- **Inc-1 owns the `Canvas` A3 (R-016), whole.** These are two *distinct* A3s that the batch has been
  narrating as "the A3" and "an unnamed second one". Naming both, in different increments, is what
  keeps each one's reverse census countable.

**`PDR-2026-08-26-ui-next-batch-02#D5b` — Inc-4 owns the seat rebind `n → M` plus `n`/`N` (D10),
alone.** Three seat rows change in one increment: `map/n → next_hit (nav)`, `map/N → prev_hit (nav)`,
`map/M → next_gap (view)`. D10's three-row seat-diff cap is reviewed row-by-row at DDR. Inc-3, Inc-6
and Inc-9 also touch `keymap.py`, so the file is a **four-way collision resolved by serial ordering,
not by ownership** — each must re-run `duplicate_chords()` and the whole-seat pin.

**`PDR-2026-08-26-ui-next-batch-02#D12` — LLR-N07.2.2 is split.** As written it bundles a mechanical
signature migration ("all six lose `**kwargs`") with a semantic capability ("every renderer paints
hit-set nodes distinguishably"). Those cannot live in one increment, because **Inc-2's gate is
byte-identical renderer output against the 245-test baseline**, and painting hits destroys byte
identity. Split:

- **LLR-N07.2.2a** *(Inc-2)* — all six `render` definitions take `(graph, state)`; output unchanged.
- **LLR-N07.2.2b** *(Inc-5)* — `outline`, `radial` and the three `lane` renderers paint `state.hits`
  distinguishably. **This is what finally gives `AT-024` an owner** — it was the orphan AT that
  observes exactly the `**kwargs` swallow, and until now no HLR claimed it.

**Why Inc-5 is its own increment and not folded into Inc-2 or Inc-4.** Into Inc-2: it breaks Inc-2's
byte-identity gate, as above. Into Inc-4: Inc-4 is already at 4 files and adding three view files
makes it 7. Standing alone it is 3 files with one crisp acceptance. This is the cleanest increment in
the batch.

**Ordering that is HARD, not preference:** **8 before 9.** Inc-9's acceptance reads the painted panel;
Inc-8 is what makes the panel able to paint 27 rows. Reversed, Inc-9 fails through no fault of its own
and the likely repair is to weaken the oracle back to `_render_keymap()`'s return value — which
**passes today on a panel showing 16 of 27**. That is the exact failure C-32 exists to prevent, and the
cut is what prevents it.

**Cross-increment regression to watch (owner: Inc-9).** Inc-4 relocates `next_gap` to `M`, in group
`view` — the group Inc-8 has not yet un-truncated at that point. So between Inc-4 and Inc-8 the
relocated chord is **undiscoverable through `?`**. The new `n`/`N` rows land in group `nav`, which is
painted, so search itself stays discoverable. Not a blocker; recorded because "we moved a key and the
help does not show it" is precisely the kind of regression that is found by a user and not by a suite.

---

## 5 · Rulings on the open questions

### Q-5 — the `◍` repo-provenance marker

**`PDR-2026-08-26-ui-next-batch-02#D7` — RULED OUT of this batch. Not deferred, not ambiguous: out.**

Executed evidence:

1. `grep -rn "provenance|repo_slug|source_repo|from_repo|origin_repo" mapper/` → **no output**
   (exit 1). Provenance is recorded nowhere.
2. **There is no `maps` table.** `store.py:71-104` creates `meta`, `nodes`, `fields`, `attachments`,
   `edges`. Map-level metadata has no home: `meta` is a **global** key/value table with
   `key TEXT PRIMARY KEY` — not keyed by `map_id` — so it cannot hold a per-map fact without key
   namespacing.
3. **There is no migration machinery at all.** `grep -n -i "migrat|schema_version|version"
   mapper/store.py` → **nothing**. `CREATE TABLE IF NOT EXISTS` is the entire story. A new *column*
   would silently not apply to existing databases; only a new *table* would appear.
4. Nothing in §3 derives from it — no HLR, no LLR, no AT (§2.8.6, re-confirmed by the census).
5. All nine increments already collide on `app.py`; 0 of 21 ARQ pairs were parallelisable. There is no
   slack to buy this with.

**Written down so the ruling is a decision.** If a later batch admits `◍`, it needs all four of:

- a `map_meta(map_id TEXT, key TEXT, value TEXT, PRIMARY KEY (map_id, key))` table — a **new table**,
  not a column, because the schema has no migration path for columns;
- a declared backfill rule for every map that predates it. The honest default is *"provenance unknown"*
  as a distinct third state, never silently rendered as "not from a repo" — a marker that lies about
  old maps is worse than no marker;
- a persist point in `RepoScreen`, which today builds a `Graph` in memory and never writes provenance;
- its own HLR, its own AT, and its own increment touching `store.py` + `app.py`.

That is a batch-3 story with a real cost. Admitting it here as a widening of HLR-N13.1 would smuggle a
persistence change and a migration into a UI increment.

### Q-7 — `⇥` for the lens walk

**`PDR-2026-08-26-ui-next-batch-02#D6` — `⇥` REJECTED. The orchestrator's unification is RATIFIED.**

Executed, not cited:

- `tests/test_keymap.py:160` — `test_no_seat_entry_binds_tab`, asserts no seat entry binds `tab`.
- `tests/test_keymap.py:165` — `test_llr_n06_5_no_screen_binds_tab_outside_the_recorded_exceptions`.
- `mapper/keymap.py:49` — `TAB_BINDING_EXCEPTIONS = ("SettingsScreen", "EditorScreen")`. **`MapScreen`
  is not in it.**
- `pytest -k tab -q` → **9 passed, 236 deselected**. Both guards green today.
- `tab` is the only keyboard route to the inspector (M-10: 9 targets, 8 transitions).

The ux lens measured that the mechanism *works* with `priority=True` (0 fires in 4 plain presses, 3 in
3 with priority). That is precisely the problem, not the solution: `priority=True` is what **takes**
`tab` away from focus traversal. The two findings are one question.

**Ruling.** `n` / `N` walk the single active *coincidencias* result set — whichever of search-hits or
lens-matches is live. `⇥` keeps its shipped job. `TAB_BINDING_EXCEPTIONS` gains nothing.

Why this is not the state-dependent chord D10 rejected: D10 rejected option (c) because `map/n` would
have had **no constant `label`**, which breaks the whole-seat pin's static set equality and
one-declaration-four-readers. Here the label `siguiente coincidencia` is **true in both cases**. The
seat stays a static set; the pin stays set equality; `groups_for_keybar` still returns
`binding.label` straight from the seat. The concept is unified, not the declaration.

**Conditions:**

- **C-D6a — "only one result set is live" becomes an explicit, tested invariant** on `MapScreen`, not
  an assumption. It is the load-bearing premise of the whole ruling. Submitting a lens must clear
  search hits and vice versa, asserted at Layer 0.
- **C-D6b — LLR-N14.3.2 is retained verbatim as the standing regression guard.** Nine `tab` presses on
  `MapScreen` still yield eight transitions, re-run after Inc-4, Inc-6 and Inc-9.

**What would reverse this:** the two guards being deliberately retired with a replacement route to the
inspector shipped in the same increment. Nothing in this batch proposes that.

### Q-8 — does a bare word in a lens query mean free text, or a malformed token?

**`PDR-2026-08-26-ui-next-batch-02#D8` — a bare word is a MALFORMED token, with a redirect.**

Under `PDR-2026-08-26-ui-next-batch-02#D6` I have just unified "search hits" and "lens matches" into one *coincidencias* concept
walked by one pair of chords. If a bare word in the lens box also meant free-text search, the two
features would become the same feature with two syntaxes and two entry points — and the "only one
result set is live" invariant that `PDR-2026-08-26-ui-next-batch-02#D6` rests on becomes much harder to reason about.

So: `/` is free text. The lens is structured `key:value`. A bare word parses to the declared malformed
class (LLR-N14.1.3, never raising), paints in the `sin definir` chip family, and the line reads as a
redirect — *the lens expects `campo:valor`; use `/` to search free text*. One concept per entry point,
and the error teaches the model rather than guessing at intent.

**What would reverse this:** a ux-lens finding that operators actually type bare words into the lens
box often enough that the redirect is friction rather than instruction. That is an observation nobody
has made yet, and it is cheap to reverse — the parse rule is one branch in `parse_lens`.

### Q-9 — migrate `FactoryScreen` / `SettingsScreen`, or only declare scopes?

**`PDR-2026-08-26-ui-next-batch-02#D9` — MIGRATE BOTH, with one gated condition.**

Declare-only does not actually work, which is the finding. LLR-N16.1.2's own threshold requires
`len(bindings_for(scope)) >= 3` for every declared scope. Declaring `SCOPE_FACTORY` without migrating
would force ≥3 seat rows that **duplicate** hand-written bindings — two declarations of the same key,
which is the exact defect the seat exists to abolish. Declare-only fails its own threshold or violates
one-declaration-four-readers. It is not an option; it only looked like one.

Executed, the migration is cheaper than it appears:

- `FactoryScreen` — **12** bindings (`factory.py:66-77`), binds no `tab`, not in
  `TAB_BINDING_EXCEPTIONS`. Clean migration.
- `SettingsScreen` — **6** bindings (`settings.py:49-56`). Two of them are
  `Binding("tab", "focus_next", …)` and `Binding("shift+tab", "focus_previous", …)` — they bind `tab`
  to **Textual's own focus-traversal actions**. They do not take `tab` from traversal; they
  *re-declare* it. Dropping them should be behaviour-neutral, and dropping them is what lets
  `SettingsScreen` leave `TAB_BINDING_EXCEPTIONS` cleanly, keeping `:160`, `:165` and `:194` green with
  the list shrunk to `("EditorScreen",)`.

**"Should be" is not evidence, and my probe could not upgrade it.** I drove nine `tab` presses on
`SettingsScreen` under Pilot at 118×34, with and without the two bindings:

```
drop_tab=False: distinct_targets=1  transitions=0   sequence: ['None'] × 9
drop_tab=True : distinct_targets=1  transitions=0   sequence: ['None'] × 9
```

Identical — but `app.focused` is `None` throughout, so **the probe cannot see a focus transition at
all and therefore cannot fail.** It is a vacuous control and I am recording it as one rather than
banking it as a green.

- **C-D9a — the `tab` drop on `SettingsScreen` is GATED.** Before Inc-9 removes those two bindings, it
  must build a probe with a **working positive control**: one that observes at least one real focus
  transition on `SettingsScreen` with the bindings present. If that control cannot be built, the drop
  does **not** ship — `SettingsScreen` keeps `tab`/`shift+tab` as screen-local bindings and stays in
  `TAB_BINDING_EXCEPTIONS`, and Inc-9 migrates its other four bindings only. Both outcomes are
  acceptable; shipping the drop on an unfalsifiable probe is not.
- **C-D9b — `UNMIGRATED_SCREENS` shrinks to `("EditorScreen", "CoverageScreen")` in the same
  increment**, or the fence at `tests/test_keymap.py:294-315` reddens. This is the supersession census
  and it belongs in Inc-9's packet.
- **C-D9c — `screens/factory.py:343` is not touched.** B-02 neither closes nor widens; asserted
  byte-identical at DDR.

### Q-10 — the three census exceptions

**`PDR-2026-08-26-ui-next-batch-02#D10` — dispositions, one per site.** All three read and confirmed.

| Site | What is actually there | Disposition | Owner |
|---|---|---|---|
| `views/radial.py:18` — `"#a3a3a3"` | A mid-grey inside `_GREYS = (INK, "#a3a3a3", MUT)`, with a comment explaining why `STEP`/`WORDMARK` are unusable as text on black. It is a **legitimate ramp step the token set is missing**, not a stray hue. | **Promote to a named token** in `darkside.py` between `INK` and `MUT`, with its job in the docstring per LLR-S06.1.1. Removes the exception rather than registering it. `views → design` is allowed and `radial.py` already imports `darkside`. | **Inc-1** |
| `app.py:848` — `darkside.WARN if self.loading else darkside.INK` | `WARN` (`#ffd230`) marks the **in-progress** stage of a progress indicator. That is a severity hue at a non-severity site: a spinner that reads as a warning. The token set has no *busy* role. | **Assign the busy/in-progress job to one of the three tokens Inc-1 is already adding** (`SAGE`/`TEAL`/`VIOLET`, LLR-S06.1.1) and retone the site. This is squarely S-6's stated work — "tokens with their jobs". | **Inc-1** |
| `screens/factory.py:104` — `.factory-tag { color: #1783ff; }` | `#1783ff` **is** `ACCENT`. A tag is a label, not an interactivity affordance, so it violates LLR-S06.3.3's "blue stays interactivity-only". (`.factory-node-selected` at `:101-103` uses the same blue as a selection background — that one is legitimate.) | **Retone to `MUT`.** But `screens/factory.py` is not in Inc-1's file set and adding it breaches Inc-1's budget. So: **Inc-1 registers it as a known-open exception; Inc-9 closes it** (Inc-9 already owns `factory.py`). LLR-S06.3.2's stale-exception guard then reddens if Inc-9 forgets — a mechanical handoff instead of a promise. | **Inc-1** registers · **Inc-9** closes |

---

## 6 · Risks, controls, and who pays

### 6.1 · Controls mapped to increments

| Control | Applies to | Who pays |
|---|---|---|
| **C-32** — assert the painted result, never a geometry-independent proxy | Inc-8, Inc-9 | Inc-9's oracle reads the painted panel; **Inc-8 pays** by making the panel able to paint 27 rows |
| **C-43** — execute, do not cite | every increment | each increment's packet |
| **C-49** — every output is someone's input | this document (§2), each increment's packet | increment author |
| **C-55 limb 2** — a negative control needs a fixture that can exhibit the failure | Inc-3 (LLR-N06.3.2) | **Inc-3**, before its gate — see `PDR-2026-08-26-ui-next-batch-02#D11` |
| **C-18 sweep** — a premise counted at one file scope may be under-counted tree-wide | DDR | DDR; R-9 already names it |
| **245-test baseline** — byte-identical renderer output | **Inc-2's entire gate** | Inc-2 |
| **Vacuous-control detection** | Inc-9's `tab` probe (`C-D9a`), LLR-N14.2.1's grep positive control | Inc-9; Inc-6 |
| **`duplicate_chords()` + whole-seat pin** | Inc-3, Inc-4, Inc-6, Inc-9 — the four-way `keymap.py` collision | each, on entry and exit |

### 6.2 · Scaffolding that must exist BEFORE Inc-1

1. **`tests/test_canvas.py`** — condition `C-D4b`. `Canvas` has **zero** direct tests today and its
   output bytes are changing under an A3. 82 lines, no event loop, no excuse.
2. **The AT↔TC mapping** — `PDR-2026-08-26-ui-next-batch-02#D15`. Without it neither traceability chain is checkable at any gate.
3. **The `01-requirements.md` §6.5 amendments** — `PDR-2026-08-26-ui-next-batch-02#D2`, `PDR-2026-08-26-ui-next-batch-02#D12`, `PDR-2026-08-26-ui-next-batch-02#D14`, `PDR-2026-08-26-ui-next-batch-02#D15`, and `PDR-2026-08-26-ui-next-batch-02#D13`'s number
   correction into `PLAN.md` §9 D12.

### 6.3 · `PDR-2026-08-26-ui-next-batch-02#D11` — the synthetic fixture spec (C-55 limb 2)

**The gap is real, and M-6's stated reason understates it.** M-6 concludes the shipped fixture cannot
exercise the double-count *because `pres` is a leaf with 0 descendants*. The real constraint is
structural. Executed tree of `fixtures/legacy.mmd`:

```
erp (root)
├── fin ── cont, pres          rrhh ── nom          inv ── alm
```

Depth 3. Branch nodes are `{erp, fin, rrhh, inv}`. A nested-fold negative control needs **two folded
branch nodes in an ancestor/descendant relation**. Among the non-root branches `{fin, rrhh, inv}` all
three are **siblings** — no such pair exists. The only ancestor/descendant branch pairs available all
involve `erp`, the root. So the fixture fails the control not because `pres` is a leaf but because
**the tree is not deep enough**, and the question of whether the root is foldable is one no
requirement answers.

**Spec for the synthetic fixture — not an argument, a shape.** Minimum viable structure, proven:

```
r ── a ── b ── c
│              d
└── z
```

Executed against that shape:

```
folded={a,b}  naive=5  painted_pills=['a']  correct=3  actually_hidden=3  NAIVE_WRONG=True
folded={a}    naive=3  painted_pills=['a']  correct=3  actually_hidden=3  NAIVE_WRONG=False
folded={b}    naive=2  painted_pills=['b']  correct=2  actually_hidden=2  NAIVE_WRONG=False
```

Requirements the fixture must satisfy: **depth ≥ 4**; at least two **non-root** branch nodes in an
ancestor/descendant relation (`a` and `b`); the inner branch has ≥ 1 descendant (`b` has `c`, `d`);
and a sibling subtree (`z`) so the painted-pill set is a proper subset of the folded set. The third
row above is the positive control — it proves the probe can also say `False`, so the test is not
green by construction. **Inc-3 owes this file before its gate; it is not optional and it is not an
argument.**

### 6.4 · Risks this review adds

| # | Risk | Increment | Mitigation |
|---|---|---|---|
| **A-11** | **Inc-2 has one AT (`AT-010`) for a six-file A3.** After `PDR-2026-08-26-ui-next-batch-02#D12`'s split it is almost entirely mechanical, which means almost nothing observes it. | Inc-2 | Its gate is not its AT: it is (a) the 245-test baseline byte-identical, and (b) a `runtime_checkable` `isinstance(r, IRenderer)` assertion over all six renderers, which is the first mechanical enforcement this interface has ever had. |
| **A-12** | **`keymap.py` is a four-way collision** (Inc-3, 4, 6, 9), up from ARQ's three-way. | 3, 4, 6, 9 | Serial ordering only; each re-runs `duplicate_chords()` and the whole-seat pin on entry and exit. |
| **A-13** | **Between Inc-4 and Inc-8, the relocated `M` chord is undiscoverable through `?`.** | 4 → 8 | Accepted, recorded. Closed by Inc-8. Do not "fix" it by reverting the rebind. |
| **A-14** | **Inc-1's export acceptance (AT-007/AT-009) is verified against a call site Inc-2 rewrites.** | 1 → 2 | `C-D4c`: re-run after Inc-2. |
| **A-15** | **HLR-S06.2 has no LLR and no mechanical acceptance** — it rests entirely on the ux lens (§6.2 item 2). | 1 | State it at the gate as ux-only. Do not count it as covered by a proxy assertion. |

### 6.5 · `PDR-2026-08-26-ui-next-batch-02#D18` — security lens referral

Per my own workflow, security-sensitive designs loop in the security lens before sign-off. Two
surfaces qualify and **neither has been reviewed**:

1. **The A-7 family — file-derived text reaching new rendered surfaces.** LLR-N06.2.3, LLR-N13.2.1,
   LLR-N14.2.3 all route ficha values from `_nodos.yml` through `darkside.plain` into new sinks. The
   sink class is right; whether `darkside.plain`'s `_CONTROL_MAP` (`darkside.py:272`) covers every
   byte class reaching these new sinks is a security question, not a design one.
2. **Inc-9's screen migration** touches `screens/factory.py`, the file carrying the unwaived
   `screens → app` back-edge, and changes which bindings are reachable on two screens.

**No increment past Inc-6 signs off without the security lens on (1); Inc-9 does not sign off without
it on (2).** This does not block Inc-1.

---

## 7 · Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Constraints stated explicitly | ✓ | §4.2 budget ≤4 source files; 245-test baseline; 0/21 pairs parallelisable; serial chain |
| At least 2 alternatives considered | ✓ | §1.1 ViewState vs additive kwargs; §1.2 approve vs defer Canvas; §5 Q-9 declare-only vs migrate (declare-only shown non-viable); §5 Q-7 `⇥` vs new chord vs unification |
| Recommendation has rationale tied to constraints | ✓ | §4.3 Inc-5 separated *because* Inc-2's gate is byte-identity; §4.3 8-before-9 *because* the oracle reads the painted panel |
| Risks listed | ✓ | §6.4 A-11..A-15; §6.5 security referral; conditions C-D4a/b/c, C-D6a/b, C-D9a/b/c |
| Cost/latency estimated where relevant | n/a | Local TUI, no model calls, no network in scope. Cost is expressed as source-file budget and increment count, which is the binding resource here. |
| Diagram included when flow is non-trivial | ✓ | §6.3 fixture tree + required shape; §4.2 dependency column |
| What would change the recommendation is stated | ✓ | §1.2, §5 Q-5, Q-7, Q-8 each carry an explicit reversal condition |
| Two-layer requirements: Acceptance block + `AT-NNN`, BOTH chains | **✗** | **Blocking-with-remedy.** Behavioral US→AT exists (§5.2 Table 1). Functional US→HLR→LLR→TC exists (Table 2). **The chains never cross: no AT↔TC mapping exists anywhere**, and only 1 of 48 LLRs carries its own Acceptance line. `PDR-2026-08-26-ui-next-batch-02#D15` names the remedy and §6.2 puts it before Inc-1. |

---

## 8 · Seal

| | |
|---|---|
| **Date** | 2026-08-26 |
| **Verdict** | **APPROVED WITH CONDITIONS** — Inc-1 may start once §6.2's three scaffolding items land. |
| **Participants** | architect lens. ux lens ruled separately (`01b-ux-decisions.md`). **security lens outstanding** — `PDR-2026-08-26-ui-next-batch-02#D18`. |
| **Approved** | `PDR-2026-08-26-ui-next-batch-02#D1` `PDR-2026-08-26-ui-next-batch-02#D2` `PDR-2026-08-26-ui-next-batch-02#D3` `PDR-2026-08-26-ui-next-batch-02#D4` `PDR-2026-08-26-ui-next-batch-02#D5` `PDR-2026-08-26-ui-next-batch-02#D5a` `PDR-2026-08-26-ui-next-batch-02#D5b` `PDR-2026-08-26-ui-next-batch-02#D6` `PDR-2026-08-26-ui-next-batch-02#D7` `PDR-2026-08-26-ui-next-batch-02#D8` `PDR-2026-08-26-ui-next-batch-02#D9` `PDR-2026-08-26-ui-next-batch-02#D10` `PDR-2026-08-26-ui-next-batch-02#D11` `PDR-2026-08-26-ui-next-batch-02#D12` `PDR-2026-08-26-ui-next-batch-02#D13` `PDR-2026-08-26-ui-next-batch-02#D14` `PDR-2026-08-26-ui-next-batch-02#D15` `PDR-2026-08-26-ui-next-batch-02#D16` `PDR-2026-08-26-ui-next-batch-02#D17` `PDR-2026-08-26-ui-next-batch-02#D18` |
| **Frozen-interface moves** | `IRenderer.render` → **APPROVED** with `with_header` struck (`PDR-2026-08-26-ui-next-batch-02#D1`, `PDR-2026-08-26-ui-next-batch-02#D2`). `Canvas` → **APPROVED WITH CONDITIONS** C-D4a/b/c (`PDR-2026-08-26-ui-next-batch-02#D4`). |
| **Rejected** | ARQ's 7-increment cut (stale, C-21) · `ViewState.with_header` · `AT-027` `AT-028` `AT-045` · `◍` this batch · `⇥` for the lens walk · PLAN §9 D12's 17/10 arithmetic |
| **Blocks lifted** | Q-5, Q-7, Q-8, Q-9, Q-10 all ruled. Inc-6 and Inc-9 unblocked. |
| **Blocks remaining** | §6.2 scaffolding (3 items) before Inc-1 · `PDR-2026-08-26-ui-next-batch-02#D18` security lens before Inc-6 sign-off |
| **Baseline to preserve** | `pytest -q` → 245 passed |
