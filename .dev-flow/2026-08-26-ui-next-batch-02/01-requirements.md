# 01 — Requirements · `2026-08-26-ui-next-batch-02` · variant B «atlas» + round-10 capabilities

> **Artifact language: English.** UI strings quoted inside requirements are **Spanish**, because
> Spanish is what ships. Normative keyword: **shall**. `should` never appears inside an HLR/LLR
> statement.
>
> **Status: Phase 1 (requirements) — derived.** §2.6 and §2.7 are closed and unchanged. §3 (HLR/LLR
> + acceptance blocks + `AT-NNN`), §4 (Information Flow Contract) and §5 (traceability) are derived
> below, and only from stories §2.6 marks `READY`. **S-3b (the `◍` repo marker) is `REFINE` and no
> requirement is derived for it** — see §2.8.
>
> **Draft-time verification.** Every claim below that names a code symbol, a constant, a framework
> behaviour, a threshold or a transform's output is either backed by a probe executed at draft time
> — transcripts in `01c-measurements.md`, cited as **M-n** — or carries an explicit
> `assumed — verify in Phase 3` / `assumed — verify in target framework` flag. A claim that is
> neither is a Phase-2 blocker. Probes ran against `master` at
> `d6b60e6b4f18b10123fffc76bbb36891473df653`; no `mapper/**` or `tests/**` file was modified.

---

## 2.6 · Story intake & refinement (INVEST + Definition of Ready)

Each story is judged on three axes. **Evaluability is judged black-box**: a story states an
observable outcome through the shipped surface, never a mechanism. Where a story as briefed reads
like an implementation spec, it is restated at the behaviour level and the mechanism is demoted to
a design note.

### S-1 · US-N06 «escala» — the canvas holds a map bigger than the screen

> **As** an operator reading a 128-node legacy map on a 118-column terminal,
> **I want** to move my window over the territory, put branches away, and be told what is not on
> screen, **so that** I can work at a scale the screen cannot hold **without ever losing something
> silently**.

| Axis | Finding |
|---|---|
| **Valuable / Negotiable** | Yes. The operator's stated priority is *navigation at scale*, and the round-9 verdict assigns exactly this to variant B. Negotiable: the minimap is a *means*; the outcome is "nothing is hidden without being declared". |
| **Estimable / Small** | Estimable, **not small.** It is the batch's largest change and the only one that moves a frozen interface. |
| **Testable (black-box)** | Yes, and strongly: every promise is a countable assertion. *When the operator presses `⇧L` on a map wider than the canvas, the painted canvas shows a different column range and the viewport indicator moves.* *When a branch is folded, a pill reading `▸ <rama> +N` is painted and `N` equals the hidden descendant count.* *When anything is off-screen or folded, an indicator declares it — and the declared total reconciles with the pills (`23 + 18 = 41`).* |
| **Independent** | No. It **must** land before or with the canvas-layer work, and the A3 migration gates every other renderer-touching increment. |

**Verdict: `READY`.** Carries two design questions to ARQ/PDR (Q-1, Q-2 below); neither blocks
derivation, both block the first increment.

---

### S-2 · US-N07 «búsqueda» — a search that says how much it found

> **As** an operator searching a map whose matches may be folded away or off-screen,
> **I want** the search to tell me how many matches exist and let me walk them,
> **so that** I can trust that what I see is all there is.

| Axis | Finding |
|---|---|
| **Valuable / Negotiable** | Yes. Today the query only tints whatever happens to be painted; a match inside a folded branch is indistinguishable from no match. With US-N06 landing folds, **shipping fold without a hit count would actively create the defect this story closes.** |
| **Estimable / Small** | Yes, small — *once Q-3 is settled.* |
| **Testable (black-box)** | Yes. *When the operator types `nóm` and submits, a line reading `n/N coincidencias` is painted and `N` equals the number of matching nodes in the whole graph, not the visible ones.* *When the operator advances, the index moves and the selection lands on the next matching node in tree order.* *When nothing matches, the painted state is visibly distinct from a match state.* |
| **Independent** | No — the count must be computed over the whole graph including folded branches, so it consumes US-N06's fold state. |

**Verdict: `READY`.** Carries **Q-3** (the `n` chord collision) and **Q-4** (two live definitions of
"hit"). Both are **blocking for implementation** and are settled at PDR, not by the implementer.

---

### S-3 · US-N13 «sala» — home shows each map's own shape

> **As** an operator returning to a workspace of several maps,
> **I want** each map to show its own structure, how documented it is, and what is due,
> **so that** I can choose where to work without opening anything — and so an empty workspace still
> shows me the door in.

| Axis | Finding |
|---|---|
| **Valuable / Negotiable** | Yes. Negotiable per marker: the thumbnail, the coverage bar, the due badge and the welcome seat are all derivable **today**; the `◍` repo marker is **not** — see Q-5. |
| **Estimable / Small** | Yes. `HomeScreen.on_mount` already calls `store.load()` for every map and discards the `Graph` (`app.py:530-552`) — the thumbnail and the coverage bar are computed from data already in hand. |
| **Testable (black-box)** | Yes. *When the workspace holds maps, each card paints a thumbnail whose lit-dot count tracks that map's acta coverage, a 10-cell bar, and a node count matching the graph.* *When a map has a node carrying a `map:` field, the card paints `⇄ n`.* *When the workspace is empty, the create door is painted with its copy — never a blank panel.* |
| **Independent** | **Yes.** Its module set is `{app, design, store?}` and it touches no renderer. It is the one story that could run as a parallel lane — decided at ARQ. |

**Verdict: `READY` for the thumbnail, coverage bar, due badge, `⇄` marker and welcome seat.**
The `◍` repo marker is **`REFINE`** pending Q-5: repo provenance is recorded nowhere in the product
(**P-12**, executed), so the marker has no data source and cannot be built without new persisted
state. Scope-add, therefore a decision, not an implementation detail.

---

### S-4 · US-N14 «lente» — ask the map a question about its fields — **DEFERRED (`#D23`)**

> **DEFERRED — follow-on design batch (amendment set 3 · A-42).** The operator re-scoped this batch.
> The intake below is **retained unchanged**, because the follow-on batch inherits it as its input;
> §3.7 carries the full deferral record and the enumerated id set. The `READY` verdict below is a
> record of what Phase 1 found, **not** a live claim that the story ships here.

> **As** an operator auditing a legacy map,
> **I want** to write `E:riesgo C:alta` and see only the nodes that answer, with the rest fallen
> back to ground, **so that** the shape of the answer — *where* the matches cluster — is itself
> visible.

| Axis | Finding |
|---|---|
| **Valuable / Negotiable** | Yes, and it is the round-10 frame with the strongest stated payoff: the prototype's own copy says *"la concentración ES el hallazgo"*. Negotiable: saved lenses on number keys are separable from the query itself. |
| **Estimable / Small** | The query language (AND of `key:value` terms over schema fields plus state) is small and pure — **a layer-0 unit**, testable with no event loop. The figure-ground render is not small: it is a renderer change, and therefore rides the same A3 contract as US-N06. |
| **Testable (black-box)** | Yes. *When the operator submits `E:riesgo C:alta`, the painted canvas shows the matching nodes as lit cards and every non-matching node as bare dim text with no card chrome, and a line declares `N nodos en M ramas`.* *When `⇥` is pressed, the selection advances through the matches with the inspector focused.* *When a term names a field the schema does not define, the outcome is declared, not silently empty.* |
| **Independent** | No — shares the renderer contract with US-N06. |

**Verdict: `READY`.** The unmatched-field behaviour (Q-6) must be specified in Phase 1; an
un-specified empty result is the classic vacuous-acceptance trap.

---

### S-5 · US-N16 «leyenda» — `?` explains the view you are in

> **As** an operator who has just been shown a canvas of braille edges, fold pills and coloured
> chips, **I want** `?` to explain **this** view — its keys and its glyph vocabulary —
> **so that** the visual language is legible without leaving the screen that uses it.

| Axis | Finding |
|---|---|
| **Valuable / Negotiable** | Yes, and it is a **dependency of the batch, not an extra**: US-N06 and US-N14 introduce a whole new glyph vocabulary (`▸ +N` pills, braille dust, the `▔` selection seat, the viewport rectangle, three new hues). Shipping them without the legend ships an unexplained language. |
| **Estimable / Small** | Yes. `?` already opens a **scope**-aware `HelpScreen` (**P-5**, executed), so this extends a surface. Two known gaps: the legend needs the **view**, and view family is two mutually-exclusive booleans with no accessor; and **three** screens drop the scope when routing `?` (**P-13**, executed — the census said two). |
| **Testable (black-box)** | Yes, and the bindings half is **derivable, so it must be derived**: *When `?` is pressed on view V, the panel's title names V, and the set of key rows it paints equals `keymap.bindings_for(scope)` for that surface — set equality, not a hand-list.* *Each glyph-vocabulary row is painted in the same style the canvas paints that glyph.* |
| **Independent** | Partly — the bindings half is independent; the vocabulary half consumes whatever US-N06/N14 actually paint, so it lands after them. |

**Verdict: `READY`.** `??` is **explicitly reserved**: it routes to a stub or the existing help, and
the guía is batch 3. That reservation is a requirement, not an omission — it is written down so a
later batch does not find the chord taken by accident.

---

### S-6 · Paleta v2 tokens

> **As** the design system, **I want** `SAGE`, `TEAL` and `VIOLET` to exist as named constants with
> their **jobs** written down, **so that** a later batch cannot quietly reuse a hue for a second
> meaning.

| Axis | Finding |
|---|---|
| **Valuable** | Yes — and the value is the *docstring*, not the hex. Three hues with no declared job is decoration; three hues with declared jobs is a contract. |
| **Estimable / Small** | Yes. Three constants plus a docstring in `mapper/darkside.py`, consumed by S-3 and S-4. |
| **Testable** | Yes, and non-trivially: *the tokens exist with the exact declared hexes*, *blue remains interactivity-only and severity remains WARN/ALERT* (a census over the tree, whose **input set must be derived, not hand-listed** — C-31), and the round-10 quantisation claim (256-colour slots 35 / 38 / 105) is **a prototype claim, therefore a hypothesis**: it is executed in Phase 1 and either confirmed or dropped. |
| **Independent** | Yes — but it is a **dependency** of S-3 and S-4, so it lands first. |

**Verdict: `READY`.**

---

### S-7 · The shipped three-region layout defect *(not in the brief — found at intake)*

> **As** an operator on a terminal wide enough to show the rail, **I want** the canvas and the ficha
> inspector to be on the screen, **so that** the map is visible at all.

Measured at intake, under Pilot, reading post-layout `widget.region` and the compositor's painted
strips: at 140 × 45 and 120 × 40 the rail occupies the **entire** body width, the canvas is laid out
at `x = 140` / `x = 120` (past the last addressable column, width 1) and the inspector is fully
off-screen. Full evidence, both the defect and its executed remedy, in `PLAN.md` §6 **P-20**.

| Axis | Finding |
|---|---|
| **Valuable** | Yes — it is the difference between the map being visible and not. |
| **Small** | Yes: one missing CSS rule, `#map-rail { width: 24 }`, verified to restore exactly the geometry `_chrome_width()` already assumes. |
| **Testable (black-box)** | Yes, and the test must drive a **wide** Pilot size, because the size is precisely what the 245-test suite was blind to (`_apply_region_visibility` hides the rail below ~118 columns, so the suite exercises only the sizes at which the bug is absent — **C-55 limb 2**). |
| **Independent** | Yes, but it is a **precondition**: pan, fold and an overflow indicator on an off-screen canvas are not a deliverable. |

**Verdict: `READY`, folded into this batch** as a precondition of US-N06 rather than a separate
story. It is a **regression of batch 1**, so it also owes an escaped-bug counterfactual: the
regression test must be shown RED against `master` before the fix.

---

### Intake summary

| id | Story | Verdict | Blocking questions |
|---|---|---|---|
| S-1 | US-N06 escala | **READY** | Q-1, Q-2 |
| S-2 | US-N07 búsqueda | **READY** | **Q-3**, **Q-4** |
| S-3 | US-N13 sala | **READY** (minus `◍`) | — |
| S-3b | US-N13 `◍` repo marker | **REFINE** | **Q-5** |
| S-4 | US-N14 lente | **READY** | Q-6 |
| S-5 | US-N16 leyenda | **READY** | — |
| S-6 | paleta v2 | **READY** | — |
| S-7 | layout defect | **READY** (folded in) | — |

### Open questions carried to ARQ / PDR

| # | Question | Why it cannot be left to the implementer |
|---|---|---|
| **Q-1** | **What shape does the extended `IRenderer.render` take** — additive kwargs (`pan`, `folded`, `lens`, …) or one `ViewState` value object? | It is the frozen interface (trigger A3). Every renderer and every call site migrates in one increment; the shape decides whether the next capability is additive or another A3. **ARQ records the new frozen signature; PDR approves it.** |
| **Q-2** | **Which layer owns fold state** — the screen, the rail (which already has `collapsed: set[str]` and a `z` toggle at `rail.py:42`), or a new view-state object? | Two owners of one truth is how the rail and the canvas start disagreeing about what is folded. The rail's `collapsed` set already exists and `z` already drives it, so the canvas must **consume** that state, not keep its own. |
| **Q-3** | **`n` is already `next_gap` in map scope** (P-11, executed). The prototype's own legend asks for `n`/`N` for search. `keymap.duplicate_chords()` and `test_no_duplicate_chord_inside_one_scope` will reject a second map-scope `n`. | One chord, one action, or the seat's whole-seat conformance spec is a lie — which is batch 1's §2.4c lesson exactly. Rebinding `next_gap`, choosing different search chords, or a state-dependent action with a **derived** label are three different products. **`ux-reviewer` + PDR decide.** |
| **Q-4** | **Two definitions of "hit" ship today** (P-18, executed): `views/layered.py:144-149` matches title + notes + field values; `Graph.search_hits` (`model.py:169-184`) also matches node id, meta and attachments. | A count taken from one and a highlight taken from the other disagree **on screen** — the exact failure the story exists to prevent. One owner must be named. |
| **Q-5** | **Repo provenance is recorded nowhere** (P-12, executed). Does this batch introduce persisted map-level provenance so `◍` has a source, or does `◍` leave scope? | New persisted state in the sidecar is a scope-add with a migration question (what do existing maps say?). Silently inventing a heuristic would make the marker lie. |
| **Q-6** | **What does a lens term naming an undefined schema field do?** | An unspecified empty result is the classic vacuous acceptance: "no matches" and "your query was meaningless" must not paint the same. |

---

## 2.7 · Premise table (C-43)

The complete table — 20 premises with tier, verdict and executed evidence — is maintained in
`PLAN.md` §6 and is **normative**. Summary of dispositions:

| Verdict | Count | Ids | Gate effect |
|---|---|---|---|
| ✅ TRUE | 17 | P-1 … P-12, P-14 … P-19 | pass |
| ❌ FALSE | 3 | **P-10** (prototype interactions are unverified for Textual) · **P-13** (three screens drop the help scope, not two) · **P-20** (the shipped three-region layout is off-screen at wide sizes) | **each dispositioned in writing below — none left open** |

**Dispositions of the three FALSE premises** — a FALSE premise blocks until dispositioned, and all
three are dispositioned constructively (they **enlarge** the requirement set, they do not delete
anything):

1. **P-10** → every `AT-NNN` in this batch drives the **real key or the real gesture**. A proxy
   (`.focus()`, calling `action_*` directly) is not acceptance. This is control **C-16**, and batch 1
   measured the identical premise FALSE, where it found four pre-existing defects.
2. **P-13** → US-N16 gains an explicit requirement that **every** screen routes `?` to its own
   scope, quantified over the screen set rather than naming the three known offenders — because
   batch 1's §2.1b lesson is that a requirement scoped to a *file* gets satisfied at that file's
   boundary while the identical defect ships in its siblings.
3. **P-20** → folded into scope as **S-7**, a precondition of US-N06, with an escaped-bug
   counterfactual (RED against `master`) and a regression test that drives a **wide** Pilot size.

**No premise is UNDECIDABLE.** One claim inherited from the prototypes is explicitly demoted to a
**hypothesis** rather than accepted: the round-10 note that SAGE / TEAL / VIOLET *"survive rich's
256-colour quantisation chromatic (slots 35 / 38 / 105)"*. Written down by a prior round is not
verified — it is executed in Phase 1 before any requirement depends on it.

---

## 2.8 · What Phase 1 executed, and what it changed *(added at derivation; §2.6 and §2.7 above are untouched)*

Five probe findings changed the requirement set before a line of §3 was written. Each is recorded
here because each **enlarges** the batch rather than confirming it, and three of them contradict a
document this batch was told to build on.

### 2.8.1 — The round-10 quantisation hypothesis: **CONFIRMED**

Executed (**M-2**): `Color.parse(hex).downgrade(ColorSystem.EIGHT_BIT).number` under rich 15.0.0
returns **35 / 38 / 105** for `#2fbf71` / `#22b8cf` / `#9775fa`, three distinct slots, none colliding
with any of the nine shipped tokens. The hypothesis is promoted to a fact and HLR-S06.2 may depend
on it. **What was NOT measured, and is not claimed:** distinct slot numbers are not perceptual
distinguishability, and `TEAL` at 38 sits five slots from the shipped `ACCENT` at 33 in the same
face of the colour cube. Perceptual separation is `assumed — verify with the ux lens at PDR`.

### 2.8.2 — **Q-6 is answered: three outcome classes, not two**

Executed over the shipped fixture `fixtures/legacy_nodos.yml` (**M-8**), whose schema keys
`['D','O','E','C','N']` were **derived from the file**, never assumed:

| Class | Definition | Executed example | Result |
|---|---|---|---|
| `MATCH` | every term's key resolves, and at least one node satisfies the conjunction | `state:risk C:alta` | 1 node in 1 rama |
| `EMPTY` | every term's key resolves, **no** node satisfies the conjunction | `E:riesgo C:alta` | 0 nodes — *the story's own example query* |
| `UNDEFINED-FIELD` | at least one term names a key in neither the schema nor the reserved set | `Z:algo` | 0 nodes, `unknown=['Z']` |

**`EMPTY` and `UNDEFINED-FIELD` both return zero nodes and must never paint the same thing.** The
distinction is carried in the parse result (`LensQuery.unknown_keys`), decided **before** evaluation,
and is therefore testable at Layer 0 with no UI — which is what makes it non-vacuous. HLR-N14.1 and
AT-033 / AT-034 are the spec.

Two riders the probe produced that a reading could not have:

1. **The story's worked example is an `EMPTY`.** `E:riesgo C:alta` returns nothing on the shipped
   fixture — `E:riesgo` alone matches two nodes, `C:alta` alone matches five, the conjunction is
   empty. A story whose only example returns zero *needs* this distinction or its acceptance is
   vacuous by construction.
2. **`state:` and `E:` are different namespaces with different vocabularies.** `Ficha.state`
   (`mapper/model.py:29`) takes `ok`/`risk`/`late`/`blocked`; schema key `E` is labelled *estado* and
   takes `obsoleto`/`estable`/`riesgo`/`atrasado`/`bloqueado`. Executed: `state:risk` returns 3 nodes,
   `E:riesgo` returns 2, and they are not the same 2. The parser routes by namespace; the Spanish
   word collision is settled in the spec, not discovered later. AT-035.

### 2.8.3 — **P-13 is under-counted: five routes drop the help scope, not three**

Executed (**M-11**): seven `action_help` definitions exist. Five push `HelpScreen()` with no scope —
`app.py:742`, `:793`, `:1058`, **plus `screens/factory.py:413` and `screens/settings.py:92`**.

**The census that produced P-13 was itself scoped to `mapper/app.py`** — which is the exact failure
shape P-13's own disposition was written to prevent, one level up. Recording it rather than quietly
correcting the number is the point.

A second defect sits underneath: `FactoryScreen` and `SettingsScreen` declare **no `KEY_SCOPE` at
all**. Repairing only the route on those two would resolve `getattr(self, "KEY_SCOPE", SCOPE_APP)`
to app scope and the legend would still be wrong — **a fix that passes its own test**. HLR-N16.1 is
therefore quantified over the derived screen set on **both** limbs: routes with its own scope, and
declares one.

And the oracle trap, which matters more than either defect: the naive set-equality check
"painted rows equal `bindings_for(help.scope)`" is **TRUE on the broken screen too** (2 rows for
scope `app`, matching), because the bug is in *which* scope was passed. The acceptance keys on the
**source screen's own declared scope**. AT-041, AT-042.

### 2.8.4 — **Q-7, NEW and blocking: US-N14's `⇥` walk is forbidden by two green guards**

Executed (**M-10**). US-N14 as briefed wants `⇥` to walk lens results. Against the tree:

- `tests/test_keymap.py:160` asserts the seat contains **no** `tab` binding;
- `tests/test_keymap.py:165` asserts **no** `Screen` subclass binds `tab` outside
  `keymap.TAB_BINDING_EXCEPTIONS = ("SettingsScreen", "EditorScreen")`. `MapScreen` is not in it;
- `mapper/keymap.py:46-48` records the measurement behind both: *a screen-level `tab` binding was
  measured to produce 0 focus moves in 9 presses* (batch-1 LLR-N06.5);
- `pytest tests/test_keymap.py -k tab` -> **5 passed** today.

And `tab` is load-bearing: nine real `tab` presses on `MapScreen` at 140 x 45 produce **nine distinct
focus targets and eight transitions** — the rail, then all eight editable inspector fields. Taking
`tab` for a lens walk removes the only keyboard path to the inspector, which is the same story's
other requirement.

**Disposition, in writing.** The walk requirement (HLR-N14.3) specifies the **behaviour** and leaves
the **chord** as a PDR decision, exactly as Q-3 leaves `n`. Whatever chord is chosen carries a
standing invariant: the eight measured focus transitions do not decrease. This was a blocking
question for the increment that would have shipped US-N14, not for derivation.
*(~~Inc-5~~: `Inc-5` under §5.4 is hit painting. US-N14 and its increment are **DEFERRED** by
`#D23`, and **Q-7 travels with them** — it is the follow-on design batch's blocking question now,
which is part of why the story is deferred rather than carried. §2.8.4 records it in full and is
retained unchanged as that batch's input.)*

**Reconciled with `01b-ux-decisions.md` DECISION 6 row 7, which measured the other half.** The ux
lens drove `tab` under Pilot and recorded **0 walk fires in 4 plain presses, but 3 in 3 with
`priority=True`**. So the mechanism is buildable and the framing above needed sharpening: **Textual
is not the obstacle — the two guards and the inspector's traversal are.** And `priority=True` is
precisely what would *take* `tab` from focus traversal, which is why the two findings are one
question and not two. Q-7 is stated in §6.1 in that corrected form.

### 2.8.5 — Three coverage percentages ship, and two of them disagree

Executed (**M-12**), input set derived by grepping every `graph.coverage()` consumer:

| Site | Expression | Value when the map has no schema |
|---|---|---|
| `mapper/app.py:379` | `int(100 * have / max(1, req))` | **0** |
| `mapper/views/layered.py:119` | `round(100*have/req) if req else 100` | **100** |
| `mapper/widgets/rail.py:149` | `round(have/req*100) if req else 100` | **100** |

On a schema-less concept map the home hero says 0 % while the canvas header and the rail say 100 %,
for the same graph in the same session. US-N13's coverage microbar would inherit whichever it copies.
Settled in LLR-N13.1.3: the sala consumes the majority definition and the outlier is corrected in the
same increment.

### 2.8.6 — S-3b `◍` remains deferred, and nothing below derives from it

**No HLR, no LLR and no `AT-NNN` in §3 references repo provenance, a `◍` glyph, or any persisted
map-level source field.** P-12 is re-confirmed by the ARQ census (`grep -rn
"provenance|repo_slug|source_repo|from_repo" mapper/` -> no output). The marker stays `REFINE`
pending **Q-5**; if PDR admits it, it enters as its own increment touching `mapper/store.py` and
`mapper/app.py`, with its own HLR and its own migration answer for existing maps — **not** as a
widening of HLR-N13.1. Recorded per `PLAN.md` §6 and the ARQ worksheet's own note.

### 2.8.7 — Two things this batch inherits as already shipped, recorded so no pass is double-counted

1. **The welcome seat is partly shipped.** `HomeScreen._empty_text` (`mapper/app.py:554`) already
   paints the six-door copy and `on_mount` already displays `#home-empty` and hides the recents table
   on an empty workspace (**M-12**). HLR-N13.2 is written as a **regression guard on shipped
   behaviour**, not as a new deliverable, and its acceptance says so.
2. **`z` already folds.** `map 'z' -> collapse_branch 'plegar rama'` is in the seat today
   (**M-9**), and `OutlineRail` owns `collapsed` (`rail.py:35`). US-N06 does not create fold; it
   **relocates its ownership** (R-013) and makes the canvas honour it.

---

## 3. High-level requirements (HLR) and Low-level requirements (LLR)

> **Normative convention.** `shall` is the only normative keyword and appears **only** inside HLR/LLR
> **Statement** lines. `should` appears nowhere inside an HLR or LLR statement. UI strings quoted in
> requirements are **Spanish**, because Spanish is what ships.
>
> **Reading order.** Requirements are grouped by story. Each story opens with a first-class
> **Acceptance block** — the observable outcome, the shipped surface that produces it, and its
> enumerated `AT-NNN` ids — which is independent of the LLR decomposition beneath it. A story is not
> done because its LLRs are green; it is done when its `AT` observes the outcome through the shipped
> surface.
>
> **Symbol citation.** Every LLR that changes a code symbol or a shared surface names the touched
> symbol(s) on a `Touched symbols` line, because that line is what the reverse census greps
> (control C-26). Symbols that do not exist yet carry `NEW — created in Phase 3`.
>
> **`AT-NNN` ids are always enumerated, never written as a dotted range** (control C-56). All ids in
> this document, plus the test files and `-k` selectors in every **Executed verification** line, are
> **provisional until Phase 3** and reconciled against the real tree at Phase 4 (rule V-5).
>
> **Every acceptance drives the real key or the real gesture** (control C-16, premise P-10 recorded
> FALSE). `.focus()`, calling `action_*` directly, or invoking a renderer method in place of a key
> press is **not** acceptance. Where the seat stores a key under a name that is not its glyph —
> `question_mark`, `slash`, `equals_sign` (**M-9**) — the acceptance presses the **seat's key name**,
> which is what Textual dispatches on.

---

### 3.0 · `HLR-COERCE` — the coercion class, and the range list it is defined over

*(Added by amendment; security condition **C-4** (`02b` S-04, S-05). §6.5 amendment **A-13**.
**Promoted from a definitions block to a requirement by `PDR-2026-08-26-ui-next-batch-02#D21`,
amendment set 3 · A-47** — see `P2-B5`.)*

#### HLR-COERCE — file-derived text is coerced before it reaches any painted surface

- **Traceability:** security conditions **C-4**, **C-5**, **C-7**, **C-8** (`02b` S-04, S-05, S-06,
  S-09); risk **A-7**. **This HLR has no parent story, by design.** It is a product-wide control
  whose subject survives the descoping of every story in the batch — which `#D23`'s deferral of
  US-N14 has now demonstrated rather than merely asserted: `LLR-N14.2.3` left with its story and the
  class did not move. **That property is stated here so a later reader does not "fix" it by
  re-parenting it under a story.**
- **Statement:** The system shall declare one list of code points that may not reach a painted
  surface, shall coerce every file-derived string against that list before it is painted, and shall
  derive the set of coercion sites from the tracked product sources at run time rather than from a
  list maintained by hand.
- **Rationale (informative):** `P2-B5`, executed. §3.0's own text was already normative — *"it shall
  be declared once in `mapper/darkside.py`"*, *"`_CONTROL_MAP` shall be widened"* — and it measured
  its own gap at **22 of 84** declared code points uncovered, including every bidi range the hostile
  fixtures drive. But it carried **no requirement id, no `Acceptance:` line, no `Touched symbols:`
  line, no validation method and no owning increment**, while four LLRs in four different increments
  each *asserted against* a list none of them *created*. Under a serial cut the de facto owner is
  whichever increment lands first, and that increment's declared file set does not contain
  `darkside.py`. **A control asserted by four requirements and created by none is a control nobody
  ships.** `grep -rn COERCION_RANGES mapper/` returns nothing; it is a Phase-3 obligation with, until
  now, no Phase-3 owner.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_darkside.py -k "coercion_ranges"` *(provisional)* —
  see the two owned LLRs, each of which carries its own threshold.
- **Numeric pass threshold:** the conjunction of `LLR-COERCE.1` and `LLR-COERCE.2`. This HLR states
  no threshold of its own, because a class-level threshold over two mechanically different
  obligations would be satisfiable by either half.
- **Owned LLRs:** `LLR-COERCE.1` (the `COERCION_RANGES` declaration and the `_CONTROL_MAP` widening
  — the uncovered code points measured below); `LLR-COERCE.2` (the ordering clause, scoped to
  `mapper/views/layered.py::_fit`, which §6.5 A-14 executed as the truncator that coerces nothing);
  and **`LLR-N06.2.5`, re-parented here by `#D21`** — see §3.4, where its block remains for
  line-stability, and `P2-B6` below.
- **Owning increments:** `LLR-COERCE.1` → **Inc-1** (`darkside.py` is already in Inc-1's declared
  set for the S-6 tokens). `LLR-COERCE.2` → **Inc-3** (which owns `views/layered.py` and is the
  increment that first asserts against the list). `LLR-N06.2.5` → **Inc-9**. All three per §5.4.
- **Acceptance:** none of its own, and that is a ruling rather than an omission (`#D21`). The
  batch's coercion `AT` ids stay on their **surface-specific** LLRs, where the observable outcome
  actually is — a painted row on a named screen. An `AT` on this HLR would have to observe "text was
  coerced" with no surface, which is a white-box claim wearing an acceptance test's clothes. This
  HLR owns `TC-080`, `TC-081` and, through the re-parent, `TC-073`.
- **THE ORDERING THIS CREATES IS REAL, NOT ADMINISTRATIVE.** `LLR-COERCE.1` widens `plain()` at
  Inc-1; `LLR-N06.2.5`'s census asserts routing *through* `plain()`; every surface threshold measures
  the painted row **after** that widening. So Inc-1 precedes all of them by dependency, not by
  convenience. **Cost of the `#D21` ruling, stated rather than hidden:** the coercion half of `S-09`
  stays live on `master` for the length of the batch. Accepted — the defect is pre-existing, `C-8` is
  a condition and not a blocker, and the alternative (forcing `screens/factory.py` into Inc-3)
  creates the two-owner collision `#D5` exists to prevent.
- **What would reverse the no-parent-story ruling:** evidence of a `notify` or paint site inside
  `mapper/views/` or `mapper/widgets/`, which would put the class inside a renderer's boundary and
  make the `views` dependency ban — not the story tree — the governing constraint. Executed at
  `20f86de`: the census returns **0** such sites.

---

**The range list this HLR is defined over.** Four coercion thresholds in this document —
`LLR-N06.2.3`, `LLR-N13.2.1`, `LLR-N16.2.3`, and `LLR-N14.2.3` until `#D23` deferred it with its
story — read *"**0** control bytes in the painted text"*. **That phrase is superseded
wherever it appears.** It is not a threshold: `U+202E RIGHT-TO-LEFT OVERRIDE` is not a control byte
under `darkside.plain`'s declared contract, and all three of those LLRs drive a right-to-left
override as their hostile input. The requirement asserted nothing about the thing it was testing.

**`COERCION_RANGES` — the declared list. It shall be declared once in `mapper/darkside.py` and read
from there by every threshold below and by every test; no test re-types it.**

| Group | Code points | Why |
|---|---|---|
| C0 except TAB and LF | `U+0000`–`U+0008`, `U+000B`–`U+000C`, `U+000E`–`U+001F` | cursor and terminal control |
| DEL and C1 | `U+007F`–`U+009F` | terminal control |
| Bidi marks | `U+061C`, `U+200E`, `U+200F` | reorder the row |
| Bidi embedding and override | `U+202A`–`U+202E` | **the attack in S-04** |
| Bidi isolates | `U+2066`–`U+2069` | same class, different mechanism |
| Zero-width and invisible | `U+200B`–`U+200D`, `U+2060`, `U+FEFF` | text that occupies no cell but changes matching |
| Line and paragraph separators | `U+2028`, `U+2029` | break a single-row contract |
| Interlinear annotation | `U+FFF9`–`U+FFFB` | out-of-band text in a row |

**`_CONTROL_MAP` shall be widened to cover the list.** Executed at `d877784` in this amendment
session, against `mapper/darkside.py:272-273`:

```
group                   points   covered by _CONTROL_MAP
C0 minus TAB/LF             29                        29
DEL + C1                    33                        33
bidi marks                   3                         0
bidi embed/override          5                         0
bidi isolates                4                         0
zero-width                   5                         0
line/para sep                2                         0
interlinear                  3                         0
TOTAL                       84                        62   -> UNCOVERED: 22
```

**22 of the 84 declared code points pass through `plain()` untouched today**, including every one
of the bidi ranges the hostile fixtures drive.

**COERCE BEFORE TRUNCATING — and the parked instruction was half right (§6.5 A-14).** `02b` C-4
requires *"coerce before truncating"*. Re-executed here, `darkside.fit` (`darkside.py:290-297`)
**already does**: its first statement is `s = plain(s)`, and
`fit(plain(s), 10) == plain(fit(s, 10))` evaluates `True`. **The load-bearing half of C-4 is
therefore the widening, not the ordering — for `darkside.fit`.** But the ordering clause is not
vacuous, because there is a **second truncator that coerces nothing**:

```
$ python -c "from mapper.views.layered import _fit; print(repr(_fit('a'+chr(1)+'b', 8)))"
'a\x01b     '
```

`mapper/views/layered.py::_fit` (`:38`) clips through `_clip` and pads, with **no coercion at all**,
and it is the function that emits every card title (`:217`, `:280`), the doc line (`:237`), the meta
row (`:247`), the diff chip (`:227`) and the removed-ghost row (`:266`). Two truncators ship; one
coerces and one does not. **Every threshold below is scoped to the painted row, which is what makes
that difference visible.**

**THE SPLIT-AT-WIDTH ARM — mandatory in all four thresholds.** Widening `_CONTROL_MAP` is necessary
and not sufficient, ~~because truncation can manufacture the defect out of a **balanced** source~~.
Executed at `d877784`:

> **THE STRUCK REASON IS REFUTED; THE ARM IS RETAINED AND RE-POINTED** (measured at `S-B(+C)`,
> confirmed at its second confirmation pass). `darkside.plain` **replaces** each of the 235 banned
> points with one `U+FFFD` rather than deleting it, so it is length- and index-preserving and
> truncation cannot strand an override: a mutant running the **forbidden** order left the derived
> census arm **green**. Widening `_CONTROL_MAP` is still not sufficient — but the reason is that
> **two truncators ship and only one coerces**, which is observable, not the ordering, which is not.
> The arm now asserts that every derived truncator's output is **indistinguishable from its own
> coercion** (`tests/test_inc3_census.py`), which is the property that separates a banned point
> mapped to `U+FFFD` from one mapped to a different banned point.

```
source:  'acta' U+202E 'gpj.evil' U+202C 'x'      (override and terminator both present)
darkside.fit(s, 10) -> 'acta' + U+202E + 'gpj.e' + HORIZONTAL ELLIPSIS
  override survives  : True
  terminator survives: False
layered._fit(s, 10) -> 'acta' + U+202E + 'gpj.'  + HORIZONTAL ELLIPSIS
```

*(The transcript above renders `U+202E` as its `\u`-escape **text**, exactly as `02b`'s evidence
checklist requires. The probe constructed it with `chr(0x202E)`; this document contains no such
character.)*

The source is balanced; the **painted row is not**. The override crosses the truncation boundary and
its terminator does not, so the override governs the remainder of the row — and every row painted
after it, if the sink does not reset. A fixture that is unbalanced at source tests the wrong thing;
this arm is balanced at source and split at width.

**Named weaker variant these thresholds redden (`M-COERCE-a`):** widen `_CONTROL_MAP`, keep
asserting on the **string handed to the sink** rather than on the painted row. It passes on every
balanced-at-source fixture and passes on the split-at-width fixture too, because the string handed
in is clean and the truncation happens downstream. Asserting on the painted row is what reddens it.

**Named weaker variant (`M-COERCE-b`):** coerce in `darkside.fit` only. Green on every path that
routes through `darkside.fit`, silently unchanged on the six `layered._fit` sites above. The
threshold's *"every file-derived string on the surface"* scoping is what reddens it.

**Byte hygiene.** Every code point above is written as a `U+XXXX` **name** in this document and
constructed with `chr(0x...)` at test time. **No control byte is written into this file.**

##### LLR-COERCE.1 — the range list is declared once, and the coercion map covers it

- **Traceability:** HLR-COERCE, security condition **C-4** (`02b` S-04, S-05)
- **Statement:** The design module shall declare `COERCION_RANGES` as the single source of the code
  points that may not reach a painted surface, `_CONTROL_MAP` shall cover every code point that list
  declares, and every threshold and every test shall read the list from that declaration rather than
  restating it.
- **Touched symbols:** `mapper/darkside.py::COERCION_RANGES` — `NEW — created in Phase 3`;
  `mapper/darkside.py::_CONTROL_MAP` (`darkside.py:272-273`) — **widened**;
  `mapper/darkside.py::plain` (`darkside.py:276`) — unchanged in signature, widened in effect.
- **Validation:** `test (unit)` + `inspection`
- **Executed verification:** `pytest tests/test_darkside.py -k "coercion_ranges_are_covered"`
  *(provisional)* — expand `COERCION_RANGES` to its code points, pass each through `plain()`, and
  assert none survives; plus a grep asserting no test file re-types a range.
- **Numeric pass threshold — DERIVED, no literal count:**

  > **QUESTION.** How many of the code points `COERCION_RANGES` declares survive `plain()`?
  >
  > **INSTRUMENT.** Expand the declared ranges at run time, apply `plain()` to each code point, count
  > the survivors. The declaration is the input set; the test does not carry its own list.
  >
  > **MEASURED AT.** `d877784` for the pre-state transcribed in the table above; re-derived at gate
  > time against whatever the declaration then says.

  **After:** survivors `== 0`. **Pre-state, from the table above:** the C0 and DEL/C1 groups are
  fully covered and every bidi, zero-width, separator and interlinear group is covered at zero — so
  the census's own input set is provably non-empty before it is evaluated, as `LLR-S06.3.1` requires.
  **Also asserted: the number of distinct declarations of the list in the tracked sources `== 1`.**
- **Named weaker variant (`M-COERCE.1-a`):** declare `COERCION_RANGES` and leave `_CONTROL_MAP`
  as shipped. The constant exists, every reference resolves, `grep` finds it — and **22 code points
  still pass through `plain()` untouched**, including every bidi range the hostile fixtures drive.
  Reddened by the survivors clause, which is why the threshold is over `plain()`'s behaviour and not
  over the constant's existence.
- **Named weaker variant (`M-COERCE.1-b`):** widen `_CONTROL_MAP` with a literal list and declare
  `COERCION_RANGES` separately from it. Both green on the day; they drift the first time one is
  edited. Reddened by the single-declaration clause.
- **Acceptance criteria:** this is the load-bearing half of `C-4` (§6.5 A-14 established that the
  *ordering* half was already satisfied for `darkside.fit`). Four surface LLRs assert against this
  list; **exactly one requirement may create it**, or the batch ships the two-definitions defect
  `#D6` removed for *"hit"* and `#D14` for *"coverage"*.

##### LLR-COERCE.2 — the second truncator coerces before it truncates

- **Traceability:** HLR-COERCE, security condition **C-4** (`02b` S-04, S-05)
- **Statement — THE ORDERING CLAUSE STANDS** (re-ruled 2026-09-11 on the corrected record; see the
  three-step history below): Every function that truncates a string destined for a painted surface
  shall apply the design module's plain-text coercion **before** truncating, and the set of such
  functions shall be **derived from the tracked product sources** rather than named by hand.
- **Acceptance-level invariant — ADDED, NOT SUBSTITUTED** (same re-ruling): every derived truncator's
  output shall satisfy **both** conjuncts — `out == darkside.plain(out)` **and the emitted width
  shall be within the requested budget.** **The budget is the load-bearing conjunct and is named as
  such:** the fixed-point half is *structurally incapable* of detecting a reversed order, because any
  truncate-then-coerce output ends in a coercion and `plain` is idempotent, so it is a fixed point by
  construction. The pairing is deliberate — a **mechanism clause** (the order) plus an **armed
  observable** (the budget) — so that a future change to `plain` which breaks the order-equivalence
  assumption *anywhere* is caught by the budget arm even on a surface where the ordering clause is
  not being watched.
  - **Armed:** `tests/test_darkside_budget.py`, driven over the **derived** truncator set and
    including the two-character minimal witness as a named case — `U+200B` + `"A"` at width **1**,
    which emits **1** cell in the specified order and **2** in the forbidden one.
  > ## THE FULL HISTORY, BECAUSE THIS CLAUSE WAS RULED, REVERSED AND RE-RULED
  >
  > **THE ORDERING CLAUSE IS LOAD-BEARING TODAY, AND THE MEASUREMENT THAT SAID OTHERWISE WAS MINE
  > AND WAS WRONG.** Recorded here immediately, ahead of any re-ruling, because a requirement must
  > not carry a statement of measured fact that is known false.
  >
  > **What I claimed:** that `_CONTROL_MAP` maps all 235 banned points to exactly one `U+FFFD` each,
  > so `darkside.plain` is index-preserving and the two orders are **the same function** — *"0
  > differing outputs over 5 hostile sources × 60 widths = 300 comparisons"*, and *"a mutant running
  > the forbidden order left every arm in the suite green."*
  >
  > **BOTH OF THOSE STATEMENTS OF MEASURED FACT ARE FALSE**, and are struck:
  > - `plain` is index-preserving in **code points**, **not in display cells**. **221 of the 235**
  >   banned points have cell width **0**; `U+FFFD` has cell width **1**. So coercion *inflates*
  >   width. `darkside.fit` truncates by `Text.cell_len`, not by index — so for that truncator the
  >   orders differ. Measured at pass 3 over **493,845** comparisons (4,015 sources × 41 widths × 3
  >   derived truncators): **133,176 differing outputs**, all in `darkside.fit`. The two
  >   length-based truncators (`_clip`, `_fit`) *are* order-equivalent — **which is all my 300
  >   comparisons ever measured.** I modelled one truncator and generalised to a clause that
  >   quantifies over three.
  > - The forbidden order **does not leave the suite green**: fired against `darkside.fit`, the full
  >   default lane goes **RED — 5 failed / 1058 passed**.
  >
  > **And the reversal is not academic:** run in the forbidden order, `darkside.fit` **overruns its
  > own budget** — 157 of 164 sampled outputs, worst **11×** (budget 2, emitted 22 cells). Minimal
  > witness, two characters: `U+200B` + `"A"` at width 1 gives 1 cell in the spec order and **2** in
  > the forbidden one. That is a painted-surface overrun on a `C-4`-traced path.
  >
  > **Two further corrections to the reasoning above, both from pass 3:**
  > - `out == plain(out)` **alone is strictly weaker** than the ordering clause and is *structurally
  >   incapable* of detecting the reversal: any truncate-then-coerce output is a fixed point by
  >   construction, because it ends in a coercion and `plain` is idempotent. **The length bound is
  >   the discriminating conjunct** — and it was **unarmed at the time of this finding**: no arm
  >   under `LLR-COERCE.2` asserted the emitted budget over the derived set. It is **armed now**, at
  >   `tests/test_darkside_budget.py`, by the re-ruling recorded below.
  > - The "survives if `plain` ever **deletes**" rationale is also wrong — under deletion the output
  >   is still a fixed point and is *shorter*, so neither conjunct fires. The hypothetical that is
  >   **real** is a replacement whose **cell width differs from the source's**, which is `U+FFFD`
  >   **today**.
  >
  > ### The three steps, each cited
  >
  > 1. **RULING (coordinator, 2026-09-11)** — replace the ordering clause with an order-independent
  >    invariant, on the grounds that the two orders were *"measurably the same function"*.
  > 2. **REVERSAL (confirmation pass 3, `increment-013-sbc-confirmation-3.md`, `F9`/`F10`)** — the
  >    grounds were false. **133,176 differing outputs of 493,845** across the derived set; the
  >    forbidden order **overruns its own budget** at up to **11×**; the full default lane goes
  >    **RED, 5 failed / 1058 passed**, under a `darkside.fit` forbidden-order mutant.
  > 3. **RE-RULING (coordinator, 2026-09-11, on the corrected record)** — **the ordering clause
  >    stands as normative**, and the invariant is **added at acceptance level** with the budget named
  >    as its load-bearing conjunct, and **armed**.
  >
  > **Accountability, recorded rather than smoothed.** The implementer's probe measured a
  > **hand-built model of `_clip`** and generalised it over a clause quantifying across three
  > truncators — parallel fiction at the instrument level, and it reached a ratified requirement,
  > which is the worst class in this batch's instrument ledger. The coordinator's own line:
  > **a direction ruling cites driven evidence or says it does not have it** — this one ruled
  > direction on an undriven measurement.
  >
  > **And the chain caught it.** Not by luck: the implementer **refused to self-clear** a declination
  > he believed correct, and the pass-3 reviewer **drove the derived set** instead of a model. Both
  > halves were necessary.
- **Touched symbols:** `mapper/views/layered.py::_fit` (`layered.py:38`) — the executed truncator
  that coerces nothing; its call sites at `layered.py:217`, `:227`, `:237`, `:247`, `:266`, `:280`.
  `mapper/darkside.py::fit` (`darkside.py:290-297`) is **unchanged** — executed, its first statement
  is already `s = plain(s)`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_darkside.py -k "truncators_coerce_first"`
  *(provisional)* — for every derived truncator `t`, assert `t(plain(s), n) == plain(t(s, n))` over
  hostile inputs constructed with `chr(0x...)`; and drive the split-at-width fixture through each.
- **Numeric pass threshold:** for every derived truncator, the coerce-then-truncate and
  truncate-then-coerce images are **equal** over the hostile input set; and the **split-at-width
  arm** passes — a source **balanced** at `U+202E` … `U+202C`, truncated at width, leaves **0**
  unterminated overrides in the painted row. Executed pre-state:
  `layered._fit('a' + chr(1) + 'b', 8)` returns the control byte intact.
  > **THE FIRST CLAUSE IS THE TRUE ONE, AND THE SECOND CANNOT DISCRIMINATE** — measured at
  > `S-B(+C)` (security review, confirmed at its confirmation pass). `_CONTROL_MAP` maps all 235
  > banned code points to exactly one `U+FFFD` each, so `darkside.plain` is length- and
  > index-preserving and the two images above are equal **identically**, for every input — 20,000
  > fuzzed hostile pairs, zero differences. The split-at-width arm therefore reports **0 unterminated
  > overrides because the coercion REPLACED the override**, never because of the ordering: a mutant
  > running the forbidden order stayed green on all 1058 arms, that arm among them. The arm has been
  > **re-pointed** at the property that is load-bearing — the cut output is indistinguishable from its
  > own coercion (`tests/test_fold.py`). The ordering clause is retained because it is the order that
  > stays correct if `plain` ever **deletes** rather than replaces; it is no longer offered as
  > independently verifiable. **Whether `LLR-COERCE.2`'s ordering clause should survive at all now
  > that its mechanism is refuted is a requirements question, flagged and not decided by the gate.**
- **Named weaker variant (`M-COERCE.2-a`, the same variant §3.0 names as `M-COERCE-b`):** coerce in
  `darkside.fit` only. Green on every path that routes through it, **silently unchanged on the six
  `layered._fit` sites above**. Reddened by the derived truncator set, which is why the set is
  derived and not the two names an author happened to think of.
- **Acceptance criteria:** widening the map is necessary and **not sufficient** — ~~truncation
  manufactures the defect out of a balanced source, so the ordering clause is not vacuous~~ — even
  though A-14 executed one of the two truncators as already correct. **Two truncators ship; one
  coerces and one does not**, and the requirement is scoped so that difference is visible.
  > **THE STRUCK CLAUSE IS THE REFUTED MECHANISM** (measured at `S-B(+C)`, confirmed at its second
  > confirmation pass). Truncation cannot manufacture an unterminated override, because
  > `darkside.plain` **replaces** each banned point with one `U+FFFD` rather than deleting it, so it
  > is index-preserving and the override is gone by coercion whichever order runs. **The non-vacuity
  > of this requirement rests on the surviving half of the same sentence** — two truncators ship and
  > only one coerces — which is a real, observable difference and is what the derived census arm
  > pins. It does **not** rest on the ordering.

---

### 3.1 · S-7 — the shipped three-region layout defect *(Inc-1)* — **SUPERSEDED**

> ## SUPERSEDED — SATISFIED-EXTERNALLY at `d877784`
>
> **The whole of §3.1 is struck from this batch's scope** — `HLR-S07.1`, `LLR-S07.1.1`,
> `LLR-S07.1.2`, `LLR-S07.1.3`, `AT-001`, `AT-002`, `TC-001`, `TC-002`, `TC-003`, `TC-004`,
> `TC-005`. It is **not re-derived**: the three-region layout shipped in the intervening repair
> batch (`003c3ad`, merged at `e164a28`), under `HLR-R04`, with a stronger guard than this section
> specified. Authority: `PLAN.md` §12.5 **D16**. The text below stays readable per **D20**; it is
> **not normative** and nothing in Phase 3 implements it.
>
> **Executed evidence at `d877784`, re-run in this amendment session — not carried from the parked
> document (C-43).** The guards now on disk, each a real collected node:
>
> ```
> $ grep -n "^async def test_\|^def test_" tests/test_repair_layout.py
> 130:def   test_tc_r22_the_rail_css_width_equals_the_rail_width_constant
> 176:async test_at_r10_the_three_regions_are_disjoint_and_on_screen        (parametrized over WIDE_SIZES)
> 209:async test_at_r10b_a_terminal_too_narrow_collapses_the_rail_and_still_fits
> 233:async test_at_r11_the_canvas_paints_map_content_in_its_own_region
> 403:async test_tc_r23_the_declared_rail_width_is_the_width_actually_painted
> $ grep -n "WIDE_SIZES\|NARROW_SIZE" tests/test_repair_layout.py | head -2
> 45:WIDE_SIZES = [(140, 45), (120, 40)]
> 46:NARROW_SIZE = (100, 24)
> ```
>
> `test_tc_r22` compares the CSS literal against `RAIL_WIDTH` and is deliberately able to disagree;
> `test_at_r10b` is the discriminating negative (rail absent at 100 columns). The repair batch's
> guard is **stronger** than `HLR-S07.1`'s because `test_at_r11` reads the canvas through
> `_rows_in(screen, canvas.region)` — the composited frame clipped to the canvas's own region —
> rather than through a widget's own `render_lines`.
>
> **Consequence — `QA-B-02` is DISSOLVED, not fixed.** `QA-B-02` attacked `AT-001` /
> `LLR-S07.1.3` / `TC-005`, whose oracle was *"the root title substring appears at least once"*.
> Those ids no longer exist in this batch, so the finding has no subject here. **Its lesson is not
> dissolved** and would be lost with it, so it is **re-homed into `HLR-N06.3`**, whose painted-node
> trace is the batch's single most important predicate and rests on exactly the same oracle. See
> the `Painted-trace oracle` block inside `HLR-N06.3` and §6.5 amendment **A-02**.
>
> **`LLR-S07.1.1`'s output row survives in the IFC.** `map_body_regions` (§4.2, `COMPONENT:
> map_screen`) is still a real contract line — the three regions still exist and are still consumed
> positionally. Its **owner is re-pointed** from the struck `LLR-S07.1.1` to the repair batch's
> `LLR-R04.1`; see §6.5 amendment **A-01**.

#### Acceptance (black-box) — S-7 *(superseded — retained for readability, not normative)*

- **Observable outcome:** on a terminal wide enough to show the rail, the operator sees the map
  canvas and the ficha inspector on screen beside the rail, instead of a full-width rail and nothing
  else.
- **Shipped surface:** `MapScreen` as composed by `MapperApp`, reached by the real `enter` key from
  `HomeScreen`; observed through post-layout `widget.region`, which is the compositor's own answer,
  not a CSS declaration.
- **Deliverable + observation:** three non-overlapping regions whose x-origins and widths satisfy
  `rail.x = 0`, `canvas.x = RAIL_WIDTH`, `inspector.x = width - INSPECTOR_WIDTH`, and
  `canvas.width = width - (RAIL_WIDTH + INSPECTOR_WIDTH)`; plus at least one painted canvas row
  containing the root node's title.
- **Acceptance tests:** `AT-001`, `AT-002`.
- **Escaped-bug counterfactual (mandatory).** `AT-001` shall be demonstrated **RED against `master`**
  before the fix, with the failing output pasted into the increment packet. A test that passes on
  `master` is not a regression test for this defect. Pre-state measured (**M-4**): at 140 x 45 the
  canvas region is `x=140 w=1` on a 140-column compositor whose last addressable column is 139.
- **Boundary catalog (QC-3):**
  - ☑ **boundary** — `AT-002` drives 118 and 117 columns, the two sides of the auto-hide transition
    `width - RAIL_WIDTH - INSPECTOR_WIDTH < MIN_CANVAS_WIDTH` (`app.py:1181`, constants 24 / 36 / 58).
  - ☑ **empty** — `AT-002` drives 80 x 24, where both side regions are auto-hidden and the canvas
    takes the full width; this is the regime the 245-test baseline already covers, asserted unchanged.
  - ☑ **invalid** — a terminal narrower than `MIN_CANVAS_WIDTH` itself (40 columns): the screen paints
    without raising, asserted in `AT-002`.
  - ☐ **error** — N/A: layout has no error path; a CSS rule either applies or does not, and the
    region readout is total.

#### HLR-S07.1 — the three map regions occupy their declared geometry — **SUPERSEDED — SATISFIED-EXTERNALLY at `d877784`**

- **Supersession:** `PLAN.md` §12.5 D16. Shipped as `HLR-R04`; guarded by
  `tests/test_repair_layout.py::test_at_r10_the_three_regions_are_disjoint_and_on_screen` and
  `::test_tc_r23_the_declared_rail_width_is_the_width_actually_painted`. Not implemented in this
  batch. `LLR-S07.1.1`, `LLR-S07.1.2` and `LLR-S07.1.3` below are struck with it.
- **Traceability:** S-7 (US-N06 precondition)
- **Statement:** While `MapScreen` is displayed on a terminal at least 118 columns wide with no
  region pinned, the system shall lay out the rail, the map canvas and the ficha inspector as three
  adjacent non-overlapping regions whose widths sum to the terminal width, with the canvas width
  equal to the terminal width minus `RAIL_WIDTH + INSPECTOR_WIDTH`.
- **Rationale (informative):** `MapScreen._chrome_width()` (`app.py:1166-1170`) already computes
  exactly this arithmetic and hands the result to the renderer as `w`; nothing enforced it, so the
  renderer was drawing into a width the compositor never granted. The remedy reproduces the
  function's own numbers, which is the evidence the arithmetic was right and the rule was missing.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_layout_regions.py -k "wide_regions"` *(file and
  selector provisional until Phase 3)* — drives `App.run_test(size=(140,45))` and `size=(120,40)`,
  presses the real `enter`, reads `widget.region` for `#map-rail`, `#map-canvas`, `#map-inspector`.
- **Numeric pass threshold:** at 140 x 45, `(rail.x, rail.width) == (0, 24)`,
  `(canvas.x, canvas.width) == (24, 80)`, `(inspector.x, inspector.width) == (104, 36)`; at 120 x 40,
  `(0, 24)`, `(24, 60)`, `(84, 36)`. Measured post-fix (**M-4**), 0 tolerance.
- **Priority:** high — it is the precondition of every other canvas requirement in the batch.
- **Acceptance:** `AT-001`

##### LLR-S07.1.1 — the rail declares a width

- **Traceability:** HLR-S07.1
- **Statement:** The `MapperApp` stylesheet shall declare an explicit width of `RAIL_WIDTH` columns
  for the `#map-rail` region.
- **Touched symbols:** the `MapperApp.CSS` string, `mapper/app.py:1889-1907` (executed: the block
  styles `#map-canvas { width: 1fr }` and `#map-inspector { width: 36 }` and **never mentions**
  `#map-rail`). `RAIL_WIDTH = 24` at `mapper/widgets/rail.py:18` — used today only to truncate text
  inside the rail's own `render` at `:122`, `:124`, `:142`, never as a width.
- **Validation:** `inspection`
- **Executed verification:** grep the `MapperApp.CSS` block for a `#map-rail` width declaration.
  Pre-state executed at draft: **0 occurrences** of `#map-rail` anywhere in the CSS block.
  Pass condition: exactly 1.
- **Numeric pass threshold:** 1 declaration; the declared value equals `RAIL_WIDTH`.
- **Acceptance criteria:** the declared numeral and the `RAIL_WIDTH` constant agree, so that the
  geometry and `_chrome_width()`'s arithmetic cannot drift apart silently.

##### LLR-S07.1.2 — the narrow regime is unchanged

- **Traceability:** HLR-S07.1
- **Statement:** While the terminal width is such that
  `width - RAIL_WIDTH - INSPECTOR_WIDTH < MIN_CANVAS_WIDTH` and no region is pinned, the system shall
  continue to hide the rail and shall lay out the canvas at `x = 0`.
- **Touched symbols:** none changed — `MapScreen._apply_region_visibility` (`mapper/app.py:1172-1186`),
  `MapScreen.MIN_CANVAS_WIDTH` (`:1164`), `MapScreen._regions_pinned`. This LLR exists to **pin
  existing behaviour** so the new width rule cannot silently move the transition.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_layout_regions.py -k "narrow_regime_unchanged"`
  *(provisional)* — drives 117 and 80 columns.
- **Numeric pass threshold:** at 100 x 30, `rail.display is False` and
  `(canvas.x, canvas.width) == (0, 64)`; at 80 x 24, `rail.display is False`,
  `inspector.display is False`, `(canvas.x, canvas.width) == (0, 80)`. Both measured on `master`
  (**M-4**) and identical post-fix, so this LLR's pass condition is *no change*.
- **Acceptance criteria:** the auto-hide transition sits at the same column count before and after
  the fix.

##### LLR-S07.1.3 — the canvas paints, not merely exists

- **Traceability:** HLR-S07.1
- **Statement:** While the map canvas region is at least `MIN_CANVAS_WIDTH` columns wide, the system
  shall paint at least one canvas row containing the root node's title.
- **Touched symbols:** none — this LLR asserts the *outcome* of LLR-S07.1.1 rather than a symbol.
  Recorded separately because a region with correct geometry and no content passes HLR-S07.1's
  region assertion while the operator still sees nothing.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_layout_regions.py -k "canvas_paints_at_wide_sizes"`
  *(provisional)* — reads the `#map-canvas` widget's rendered `Text.plain`.
- **Numeric pass threshold:** the root title substring appears at least once at both 140 x 45 and
  120 x 40. Measured post-fix (**M-4**): the row `'         ▐ nomina …'` is present at both sizes.
- **Acceptance criteria:** a geometry-only assertion cannot pass this LLR.

---

### 3.2 · S-6 — paleta v2 tokens with their jobs *(Inc-1)*

#### Acceptance (black-box) — S-6

- **Observable outcome:** a later batch that reaches for a hue finds three named constants whose
  **jobs are written down**, and a census that fails if a hue is reused for a second meaning. The
  operator-visible half is that completitud, procedencia and relaciones are told apart by colour on
  the sala cards and in the lens, without either borrowing the interactivity blue or the severity
  pair.
- **Shipped surface:** `mapper/darkside.py` as imported by `views`, `screens`, `widgets` and `app` —
  the four declared consumers of the design tokens (`docs/ARCHITECTURE.md` §4).
- **Deliverable + observation:** three module-level constants `SAGE`, `TEAL`, `VIOLET` carrying the
  exact hexes, plus a module docstring block stating each token's job; observed by importing the
  module and reading the constants, and by the census tests below.
- **Acceptance tests:** `AT-003`, `AT-004`, `AT-005`, `AT-006`.
- **Boundary catalog (QC-3):**
  - ☑ **boundary** — `AT-004` drives the 256-colour downgrade, the boundary between the truecolour
    the design assumes and the palette a real terminal may offer.
  - ☑ **invalid** — `AT-005` fails if any hue outside the declared token set appears at a new site;
    the input set is **derived from the tree**, so a hue nobody declared is an invalid input the
    census catches rather than a case it forgot.
  - ☑ **empty** — `AT-005`'s derivation is asserted non-empty (95 sites today, **M-3**); a census
    whose grep silently returns nothing would otherwise pass vacuously.
  - ☐ **error** — N/A: a colour constant has no failure mode at import; the risk is semantic reuse,
    which is what `AT-005` and `AT-006` measure.

#### HLR-S06.1 — three tokens exist and their jobs are declared

- **Traceability:** S-6
- **Statement:** The design module shall expose `SAGE`, `TEAL` and `VIOLET` as module-level colour
  constants with the values `#2fbf71`, `#22b8cf` and `#9775fa`, and shall declare in its module
  documentation the single job each token carries: `SAGE` completitud/vigente, `TEAL` procedencia
  repo, `VIOLET` relaciones/enlaces.
- **Rationale (informative):** the value of this story is the docstring, not the hex. Three hues with
  no declared job is decoration; three hues with declared jobs is a contract a later batch can be
  held to. `TEAL`'s declared job — procedencia repo — is declared **even though S-3b is deferred**,
  so the hue is reserved rather than left free for a second meaning to claim.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_darkside.py -k "paleta_v2_tokens"` *(provisional)* —
  imports `mapper.darkside` and compares the three constants against literals, and asserts each
  token's name appears in the module docstring.
- **Numeric pass threshold:** 3 constants present; 3 exact string equalities; 3 token names present
  in the docstring. 0 tolerance.
- **Priority:** high — S-3 and S-4 both consume these, and `PLAN.md` §6 orders Inc-1 first for this
  reason.
- **Acceptance:** `AT-003`
- **Value reconciliation (C-36):** all three hexes are `NEW — created in Phase 3`. Executed at draft
  (P-3, re-run): `grep -n "2fbf71\|22b8cf\|9775fa\|SAGE\|TEAL\|VIOLET" mapper/**/*.py` returns **no
  output**. The nine tokens they join are on disk today at `mapper/darkside.py:12-20`:
  `GROUND #000000`, `PANEL #121212`, `STEP #262626`, `INK #f5f5f5`, `MUT #737373`,
  `ACCENT #1783ff`, `WARN #ffd230`, `ALERT #ff4f42`, `WORDMARK #3a3a3a`.

##### LLR-S06.1.1 — the constants and the docstring land together

- **Traceability:** HLR-S06.1
- **Statement:** The design module shall define the three constants adjacent to the existing token
  block and shall carry, in the same module, prose naming each token's job and stating that a token
  carries exactly one job.
- **Touched symbols:** `mapper/darkside.SAGE`, `mapper/darkside.TEAL`, `mapper/darkside.VIOLET`
  — all three `NEW — created in Phase 3`; the existing token block at `mapper/darkside.py:12-20`
  and the module docstring at `mapper/darkside.py:1`.
- **Validation:** `inspection`
- **Executed verification:** read `mapper/darkside.py`; confirm the three names appear both as
  assignments and inside the module docstring, and that the docstring states the one-job rule.
- **Numeric pass threshold:** 3 assignments, 3 docstring mentions, 1 statement of the one-job rule.
- **Acceptance criteria:** a constant without its job in prose does not satisfy this LLR — that is
  the whole deliverable, per the story's own framing.

#### HLR-S06.2 — the tokens survive the 256-colour downgrade as distinct slots

- **Traceability:** S-6
- **Statement:** When each of the three new tokens is downgraded to the eight-bit colour system, the
  system shall yield three mutually distinct palette slots, none of which equals the slot yielded by
  any other declared design token.
- **Rationale (informative):** the terminal is the delivery medium and not every terminal offers
  truecolour. A palette whose three new hues collapse onto one another, or onto the blue, is a
  palette that stops carrying meaning exactly where the product is hardest to read. This was a
  prototype claim; §2.7 demoted it to a hypothesis and **M-2** executed it.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_darkside.py -k "tokens_survive_eight_bit"`
  *(provisional)* — for every declared token, `rich.color.Color.parse(value).downgrade(
  rich.color.ColorSystem.EIGHT_BIT).number`, then assert the three new slots are pairwise distinct
  and disjoint from the shipped nine.
- **Numeric pass threshold:** `len({slot(SAGE), slot(TEAL), slot(VIOLET)}) == 3` and
  `{slot(SAGE), slot(TEAL), slot(VIOLET)} ∩ {slots of the nine shipped tokens} == {}`.
- **Priority:** medium
- **Acceptance:** `AT-004`
- **Executed pre-state (M-2), rich 15.0.0:** `SAGE -> 35`, `TEAL -> 38`, `VIOLET -> 105`;
  shipped tokens land on `33, 221, 203, 255, 242, 235, 233, 16, 237`. Both threshold clauses hold
  **today** for the proposed values, so the test is a *guard against a later hex edit*, not a
  discovery. Recorded plainly: its pre-state is green by construction, and its non-trivial arm is the
  mutation in `AT-004` that changes one hex and must turn it red.
- **~~Flagged `assumed — verify with the ux lens at PDR`~~ — RETIRED, MEASURED (`UX2-C-10`,
  §6.5 A-67).** Perceptual separation is no longer assumed. Measured in CIE L\*a\*b\* (D65) over the
  eight-bit palette's own RGB, **0** slot collisions at `EIGHT_BIT`, and the **minimum** CIEDE2000
  distance over the declared semantic pairs is **13.99** — roughly six times the ~2.3 just-noticeable
  difference. The pair that produced it is `ACCENT`/`VIOLET`; the pair the parked flag actually
  worried about, `ACCENT`/`TEAL` at five slots apart, measures **20.18** — **further apart than the
  pair nobody worried about**, which is why slot-number adjacency was the wrong proxy all along.
- **THRESHOLD ADDENDUM — a perceptual floor, derived over the declared token set (`C-31`):** the
  minimum CIEDE2000 distance over all semantic token pairs at the guaranteed rung is `>= 10`. Derived
  from the declared token set at run time, never over a hand-listed pair list.

- **THE GUARANTEED RUNG IS DECLARED, AND THE 16-COLOUR RUNG IS A DECLARED KNOWN LIMIT
  (`UX2-C-10`, §6.5 A-67).** This requirement guarantees **`EIGHT_BIT` and above**. Executed on the
  delivery machine, Textual resolves `color_system` to **256**, and because `legacy_windows` is
  `False` the auto-detection can only yield truecolour or eight-bit — **the 16-colour rung is not
  auto-reachable.** At the rungs below the guarantee, measured through the real render path:

  ```
  EIGHT_BIT (guaranteed)  ACCENT 33 · SAGE 35 · TEAL 38 · VIOLET 105     no collisions
  STANDARD  (16 colour)   ACCENT = VIOLET = 94 · SAGE = TEAL = 36 · MUT = WORDMARK = 90
  WINDOWS                 ACCENT = VIOLET = 94 · WORDMARK = GROUND
  ```

  **`ACCENT ≡ VIOLET` is the semantically expensive one:** blue is declared **interactivity-only**
  — *«donde puedes actuar»* — and `VIOLET`'s job is the link marker. Collapsed, *"this map links to
  another"* reads as *"you can act here"*. **Declared as a known limit rather than fixed**, because
  the rung is not auto-reachable and is one unpinned environment variable away; **the product does
  not pin it**, and that is recorded here rather than left as a discovery.
- **⚠ MEASUREMENT HAZARD, RECORDED BECAUSE IT PRODUCED A PLAUSIBLE WRONG ANSWER.** `Style.parse` is
  LRU-cached and caches `_ansi`, so a downgrade probe that reuses a `Style` object **silently returns
  the first rung's codes for every later rung** — reporting "no collisions" at every rung. The
  verification **shall** construct a fresh `Style` per rung. The lens's own first attempt was
  contaminated this way and caught it; a Phase-3 implementer will meet the identical trap.

#### HLR-S06.3 — the hue census proves the jobs, over an input set derived from the tree

- **Traceability:** S-6
- **Statement:** The system shall carry a census that enumerates every colour literal and every
  design-token reference in the product source **by derivation from the tracked file set**, and shall
  fail if the interactivity hue appears at a site that is not an interactivity affordance or if a
  severity hue appears at a site that does not express severity.
- **Rationale (informative):** control C-31 — a hand-listed input set is an unproven spec claim. A
  census over a list of hues someone typed cannot detect the hue nobody typed, and **M-3 found
  exactly that**: `#a3a3a3` ships at `mapper/views/radial.py:18` inside `_GREYS` and is a member of
  no token set.
- **Validation:** `test (unit)` + `analysis`
- **Executed verification:** `pytest tests/test_darkside.py -k "hue_census"` *(provisional)* — the
  test derives its file list from the tracked product sources, harvests six-hex-digit literals and
  `darkside.<TOKEN>` references by regex, and classifies each site.
- **Numeric pass threshold (`QA2-C-04`, §6.5 A-61):** the derived site count is `> 0` (guards
  against a vacuous grep; measured **95** today); every `ACCENT` site classifies as
  **interactivity**; every `WARN` site classifies as **outstanding attention** and every `ALERT`
  site classifies as **failure or blockage**, each against `LLR-S06.3.5`'s single declared job for
  that token; the set of hues found equals the declared token set plus the explicitly registered
  exceptions, and the exception register is non-empty only for entries listed below.
- **~~"every `WARN`/`ALERT` site is classified **severity**"~~ IS SUPERSEDED — THE PARENT THRESHOLD
  WAS ITS OWN CHILD'S NAMED MUTANT.** `LLR-S06.3.5` names `M-S06.3.5-a` as *"give `WARN` and `ALERT`
  the single job severity"* and requires it to go **RED**. The parent, quantified over the same
  sites, asserted **exactly that mutant as its pass condition**. So the two requirements demanded
  opposite outcomes from one census, and the parent — being the one with the `Acceptance:` line —
  would have won. **A mutant a child must redden cannot be a threshold its parent greens.**
  *"Severity"* is the **family both tokens belong to**, so it cannot tell them apart and licenses
  painting a failure and an outstanding item identically. Executed over the 36 `darkside.WARN` /
  `darkside.ALERT` sites, the tree already distinguishes them — the correction is to say what the
  tree does, not to loosen the census.

- **THE CLASSIFIER IS DEFINED, AND IT IS A DECLARED PER-SITE REGISTER WITH A DERIVED INPUT SET
  (`QA2-C-05`, §6.5 A-62).** *"Every derived `WARN` site classifies as outstanding attention"* has
  no executable meaning until *classifies* is defined. It is defined as follows, and the definition
  is what keeps `AT-005` / `AT-006` at `test (unit)` rather than demoting them to `analysis`:

  > **INPUT SET — derived (`LLR-S06.3.1`).** Every `darkside.<TOKEN>` reference and every six-hex
  > literal in the tracked product sources. **Never hand-listed.**
  >
  > **CLASSIFICATION — a declared register, one row per derived site**, carried in the test module:
  > `(file, symbol, token, job)` where `job` is one of the declared jobs and is asserted to **equal**
  > the token's single declared job from `LLR-S06.3.5`.
  >
  > **TOTALITY — the clause that makes it a gate rather than a table.** The register shall be
  > **total** over the derived input set: a derived site with **no** register row is a **failure**,
  > not a skip. A new site added by a later increment therefore reddens this census until someone
  > classifies it.
  >
  > **THE VERDICT IS RECORDED, NOT RE-JUDGED.** Assigning a job to a site is a human judgement made
  > once and written down; the **test** asserts totality and job-equality mechanically. That split is
  > what makes the method `test (unit)` honestly — the judgement is in the artifact, the check is in
  > the code.

- **WHY NOT `analysis`, WHICH `QA2-C-05` OFFERS AS THE ALTERNATIVE.** Marking `AT-005` / `AT-006`
  `analysis` would be honest about the parked state and would **lose the property the story is
  for**: S-6's whole value is that *"a later batch cannot quietly reuse a hue for a second meaning"*,
  and only a **totality** clause evaluated at gate time catches the site a later batch adds. An
  analysis is performed once; this must fail later, on work nobody has written yet.
- **Named weaker variant (`M-S06.3-classifier`):** carry the register and assert only that every
  **registered** row's job matches its token. Green on the day it lands and blind to every site added
  afterwards — the register silently stops covering its own input set. **Reddened by the totality
  clause**, which is the whole difference between a register and a census.
- **Priority:** medium
- **Acceptance:** `AT-005`, `AT-006`

##### LLR-S06.3.1 — the census derives its own input set

- **Traceability:** HLR-S06.3
- **Statement:** The census shall obtain its file list from the tracked product source tree at run
  time and shall assert that list is non-empty before evaluating any classification.
- **Touched symbols:** the census test module — `NEW — created in Phase 3`. It reads
  `mapper/darkside.py`'s token names by introspection rather than by literal list.
- **Validation:** `test (unit)`
- **Executed verification:** the same node as HLR-S06.3, plus a mutation arm that empties the derived
  file list and asserts the test turns red rather than green.
- **Numeric pass threshold (`QA-M-03` / `QA-M-11`, §6.5 A-32):** the derived file list **equals**
  `git ls-files` over `mapper/` filtered to `*.py` — asserted as a set, not as a count against a
  floor. Executed at `d877784`: **33** files; `Path('mapper').rglob('*.py')` also **33**;
  `glob.glob('mapper/*.py')` **16**, the non-recursive plausible weakening. Derived literal-site
  count `> 0` (executed: **95**); the emptied-list mutation arm fails.
- **~~`>= 30`~~ is superseded, and the reason is subtler than "it fails".** `>= 30` **does** catch
  the 16-file `glob` — `QA-M-11` says so and it re-executes. The problem is that catching it is an
  accident of the gap between 16 and 30: a derivation that lost **three** files, or that gained a
  new module and lost four, sits comfortably above the floor and ships a census with holes. Naming
  the command and asserting the **set** removes the dependence on how large the loss happens to be.
- **Acceptance criteria:** a census that passes when its own input is empty is not a census. The
  mutation arm is what distinguishes this from control C-55 limb 2.

##### LLR-S06.3.2 — the three registered exceptions are named and fenced

- **Traceability:** HLR-S06.3
- **Statement:** The census shall carry an explicit register of pre-existing sites that its
  classification does not cover, and shall fail if a registered entry no longer exists in the tree.
- **Q-10 IS RULED — `PDR-2026-08-26-ui-next-batch-02#D10`, one disposition per site (`QA-B-10`,
  §6.5 A-26). All three sites were read and confirmed; two are RESOLVED rather than registered, so
  the register does not stay at three.**

  | Site (re-derived at `d877784`) | What is actually there | Disposition | Owner |
  |---|---|---|---|
  | `mapper/views/radial.py:18` — `"#a3a3a3"` | a mid-grey inside `_GREYS = (INK, "#a3a3a3", MUT)`, with a comment explaining why `STEP`/`WORDMARK` are unusable as text on black. A **legitimate ramp step the token set is missing**, not a stray hue | **Promote to a named token** in `darkside.py` between `INK` and `MUT`, with its job in the docstring per `LLR-S06.1.1`. **Removes the exception rather than registering it** | Inc-1 |
  | `mapper/app.py:879` — `darkside.WARN if self.loading else darkside.INK` **(parked `:848`; re-executed, the address moved)** | `WARN` marks the **in-progress** stage of a progress indicator — a spinner that reads as a warning. The token set has no *busy* role | **Assign the busy/in-progress job to one of the three tokens Inc-1 is already adding** (`SAGE`/`TEAL`/`VIOLET`) and retone the site. This is squarely S-6's stated work | Inc-1 |
  | `mapper/screens/factory.py:104` — `.factory-tag { color: #1783ff; }` | `#1783ff` **is** `ACCENT`. A tag is a label, not an interactivity affordance, so it violates `LLR-S06.3.3`. (`.factory-node-selected` at `:101-103` uses the same blue as a **selection background** — that one is legitimate) | **Retone to `MUT`.** But `factory.py` is not in Inc-1's file set. **Inc-1 registers it as a known-open exception; Inc-9 closes it** — this LLR's stale-exception guard then reddens if Inc-9 forgets. A mechanical handoff instead of a promise | Inc-1 registers · Inc-9 closes |

- **THIS RESOLVES THE FLAG A-10 RAISED, AND RESOLVES IT THE OTHER WAY.** A-10 observed that
  `LLR-S06.3.5`'s declared job for `WARN` — *outstanding attention … or in flight* — makes
  `app.py:879` **classifiable**, and asked PDR to retire the register entry or say why it stays.
  `#D10` had already answered: the site is **retoned**, not reclassified. A spinner is *busy*, not
  *outstanding*, and giving `WARN` a second reading to accommodate it would re-create exactly the
  two-jobs defect `QA-B-08` raised. **The busy job goes to a new token; `WARN` keeps its one job.**
- **Touched symbols:** the census exception register — `NEW — created in Phase 3`; the promoted grey
  token and the busy token in `mapper/darkside.py` — both `NEW — created in Phase 3`.
- **Validation:** `test (unit)` + `inspection`
- **Executed verification:** `pytest tests/test_darkside.py -k "hue_census_exceptions_are_real"`
  *(provisional)* — every registered `file:line` still resolves to the recorded literal.
- **Numeric pass threshold — the register's size is DERIVED from the dispositions, not typed
  (§6.5 A-31).** After Inc-1: **1** registered entry (`factory.py:104`), because `radial.py:18` is
  promoted to a token and `app.py:879` is retoned. After Inc-9: **0**. Every registered entry
  resolves to its recorded literal; a stale entry fails. **The parked *"exactly 3 registered
  entries"* is superseded** — it encoded the pre-ruling state and would have reddened Inc-1 for
  doing exactly what `#D10` requires.
- **`QA-N-05` recorded as verified:** all three sites were confirmed present on disk at draft and
  again here. The dispositions change what happens to them, not whether they exist.
- **Acceptance criteria:** fencing the exception list is what stops it silently licensing a fourth
  violation — the same shape as `keymap.TAB_BINDING_EXCEPTIONS` and its fence test
  (`tests/test_keymap.py:194`, executed green).

##### LLR-S06.3.3 — blue stays interactivity-only

- **Traceability:** HLR-S06.3
- **Statement:** The census shall fail if the interactivity hue appears at any product-source site
  outside its own definition, the registered exceptions, and sites classified as focus rings, table
  or list cursors, or key affordances.
- **Touched symbols:** none changed. The 8 sites this quantifies over, derived (**M-3**):
  `mapper/darkside.py:17` (definition), `mapper/app.py:1864`, `:1906`, `:1925`,
  `mapper/screens/coverage.py:58`, `mapper/screens/factory.py:101`, `:104`,
  `mapper/screens/palette.py:65`.
- **Validation:** `test (unit)`
- **Executed verification:** as HLR-S06.3.
- **Numeric pass threshold — EQUALITY AGAINST THE DERIVATION, not a floor (`QA-M-03`, §6.5 A-32):**
  the census asserts the **derived set itself**, not its cardinality against a constant. Executed at
  `d877784`: `grep -rn '#1783ff' mapper --include=*.py | wc -l` gives **8**, reproducing the parked
  figure. Unclassified sites `== 0` after the register is applied.
- **Why the floor had to go.** A `>=` bound on a *derived* count **cannot detect a census that
  under-derives**: a regex that silently loses sites still passes `>= 8`, and the census's whole job
  is to notice sites nobody remembered. The bound is stated against the derivation's own output so
  that a shrinking input set is a failure rather than a pass with slack.
- **The derivation method is NAMED, not left to the implementer (`QA-M-11`, §6.5 A-32):** the file
  list is `git ls-files` over `mapper/` — **not** `Path.rglob` and **not** `glob`. Executed at
  `d877784`:

  ```
  git ls-files 'mapper/**/*.py' 'mapper/*.py'  ->  33
  Path('mapper').rglob('*.py')                 ->  33
  glob.glob('mapper/*.py')                     ->  16     <- non-recursive
  ```

  `git ls-files` is chosen over `rglob` because the two agree **today** and stop agreeing the moment
  an untracked or ignored `.py` lands under `mapper/`; the census is over *tracked product source*,
  and saying so in the command is what keeps that true. **Correction to `QA-M-11` (§6.5 A-32):**
  `02a` states the non-recursive `glob` yields **5** files. Re-executed, it yields **16**. The
  finding stands — the non-recursive form is a plausible weaker commit and loses more than half the
  tree — but the number does not, and `>= 30` would **not** have caught it at 16 either.
- **Acceptance criteria:** the site count is derived at run time, so a ninth blue site added by any
  increment in this batch enters the census automatically instead of needing someone to remember it.

##### LLR-S06.3.4 — severity stays WARN and ALERT

- **Traceability:** HLR-S06.3
- **Statement:** The census shall fail if a severity hue appears at any product-source site that does
  not express node state in `risk`, `late` or `blocked`, a missing required field, an overdue count,
  or a failed check, outside the registered exceptions.
- **Touched symbols:** none changed. Quantifies over the derived `WARN`/`ALERT` reference set —
  executed today: **29** sites across `app.py`, `screens/coverage.py`, `screens/factory.py`,
  `views/lane.py`, `views/layered.py`, `views/outline.py`, `widgets/inspector.py`,
  `widgets/rail.py`.
- **Validation:** `test (unit)`
- **Executed verification:** as HLR-S06.3.
- **Numeric pass threshold — EQUALITY AGAINST THE DERIVATION, not a floor (`QA-M-03`, §6.5 A-32):**
  the census asserts the derived severity set itself. ~~`>= 29`~~ is superseded — re-executed at
  `d877784` the count is **36**, so the floor was green with seven sites of slack and could not have
  detected a census that under-derived by six. Unclassified sites `== 0` after
  the register is applied; the state vocabulary the classifier keys on equals
  `{"risk", "late", "blocked"}` read from `mapper/views/layered.py:15-17` and
  `mapper/views/lane.py:16-18` rather than typed into the test.
- **Acceptance criteria:** the state tokens are read from the shipped `STATE_STYLE` maps, so a new
  state added later cannot slip past a hard-coded list.
- **Threshold correction (§6.5 A-09).** The parked figure *"executed today: **29** sites"* does not
  reproduce at `d877784`. Re-executed in this amendment session:
  `grep -rnE 'darkside\.(WARN|ALERT)' mapper --include=*.py | wc -l` gives **36**, over 36 distinct
  lines. The `>= 29` bound is therefore green for the wrong reason — seven sites of slack, so a
  census that under-derived by six would still pass. **`QA-M-03`'s equality-versus-floor ruling is
  folded in the threshold above (§6.5 A-32)**; it was left to the QA lane in amendment set 1 and is
  settled here. `LLR-S06.3.3`'s hue figure **does** still reproduce:
  `grep -rn '#1783ff' mapper --include=*.py | wc -l` gives **8**.

##### LLR-S06.3.5 — `WARN` and `ALERT` each carry exactly one job, adjudicated from the tree

- **Traceability:** HLR-S06.3, HLR-S06.1 (the one-job rule)
- **Statement:** The design module shall declare exactly one job for `WARN` and exactly one job for
  `ALERT`, and the census shall fail if either token appears at a site the declared job does not
  cover.
- **THE DECLARED JOBS — normative, one sentence each:**
  - **`WARN` `#ffd230` — *outstanding attention*: work is pending, due, at risk, or in flight, and
    nothing has failed.**
  - **`ALERT` `#ff4f42` — *failure or blockage*: this item cannot proceed as it stands.**
- **This resolves `QA-B-08`, and it resolves it AGAINST BOTH of the parked definitions (§6.5 A-10).**
  The parked document gave `WARN` two contradictory jobs in two places, and `QA-B-08` is right that
  a classifier with two live definitions has no oracle. It is **not** right that one of the two is
  correct. Adjudicated by derivation rather than by preference — the full site list, executed in
  this amendment session:

  ```
  $ grep -rnE 'darkside\.(WARN|ALERT)' mapper --include=*.py        -> 36 sites
  WARN  : sin acta count and bar (app.py:410,411) · vencen hoy (:399) · hero number when
          anything is outstanding (:392) · states risk/late (lane.py:16,17; layered.py:20,21) ·
          the over-limit render notice (layered.py:69, outline.py:39, radial.py:99) ·
          diff chip (layered.py:230) · missing-field counts (outline.py:136, rail.py:251) ·
          low criticality (app.py:1296,1311) · run in progress (lane.py:67) ·
          loading progress (app.py:879)
  ALERT : missing acta (app.py:261) · bloqueado (:922) · missing required fields
          (coverage.py:88, inspector.py:191,192) · cycle refusal (factory.py:221) ·
          template not found (:284) · unsubstituted placeholder (:312) ·
          state blocked (lane.py:18, layered.py:22) · behind / fail (lane.py:41,56,69,93) ·
          removed ghost (layered.py:268) · rail (:198)
  ```

  **`WARN` never paints a search hit at any of the 36 sites** — `0` of `36`. The claim at
  `HLR-N06.2` that *"`WARN` does mean a hit"* is therefore **FALSE against the tree** and is
  corrected there. And *"severity"* alone, the claim at `LLR-N07.3.2`, is **too coarse to be a job**:
  it is the family both tokens belong to, so it cannot tell them apart and would license painting an
  empty result in either. The two tiers above are what the tree actually distinguishes.
- **Consequences, each stated rather than left to be discovered:**
  1. **`LLR-N07.3.2`'s conclusion survives; its reason is replaced.** The empty count line stays in
     `MUT`. Not because `WARN` means *a hit*, but because a query that completed with an empty
     answer is neither outstanding nor failed. D-1's ruling is upheld on corrected grounds.
  2. **The fold pill's hidden-hit count in `WARN` is consistent** with the declared job: matches
     hidden inside a folded branch are work the operator has pending. `01b` DECISION 5 step 3 is
     unchanged, and `HLR-N06.2` keeps the tone while losing the false reason.
  3. **The malformed lens chip in `ALERT` is consistent** and enters the census classified. `01b`
     DECISION 2 assigns `ALERT #ff4f42` to ` Z ? sin definir `, and `01b:332-333` warns that *"if
     `ALERT` acquires a second job it must acquire a row here too."* It does not acquire a second
     job: a query naming a field the map does not define **cannot proceed as it stands**, which is
     the declared job verbatim. §3.7 gains the classification row — see `LLR-N14.1.3`.
  4. **`app.py:879` becomes classifiable and may leave the exception register.**
     `darkside.WARN if self.loading else darkside.INK` paints work *in flight*, which the declared
     job covers. `LLR-S06.3.2` calls it *"the single site the severity rule does not fit"* — under
     the adjudicated job it fits. **Disposition owed at PDR**: retire the entry, or record why it
     stays. `LLR-S06.3.2`'s threshold is re-stated as a derivation below so the answer does not
     require re-typing a literal.
- **Validation:** `test (unit)`
- **Executed verification:** as `HLR-S06.3` — the classifier keys on the two declared jobs, read
  from the design module's own prose rather than typed into the test.
- **Numeric pass threshold:** every derived `WARN` site classifies as *outstanding attention*; every
  derived `ALERT` site classifies as *failure or blockage*; sites classifying as **both** `== 0`;
  sites classifying as **neither** `== 0` after the exception register is applied. Derived site
  count re-executed at `d877784`: **36**.
- **Named weaker variant (`M-S06.3.5-a`):** declare the job of both tokens as *"severity"*. Every
  one of the 36 sites classifies, the census is green, and the two tokens become interchangeable —
  which is the defect, not the fix. It is reddened by the *sites classifying as both* `== 0` clause,
  because a single "severity" job makes every site classify as both.
- **Named weaker variant (`M-S06.3.5-b`):** declare the jobs, then classify by asking whether the
  token appears in a `STATE_STYLE` map. Green on the 10 state-map sites, silently unclassified on
  the other 26. Reddened by the *neither* `== 0` clause.
- **Acceptance criteria:** one job statement per token, both derived-checkable, and the census fails
  before the batch adds a site that fits neither. With two live definitions the classifier has no
  oracle, which is `QA-B-08`'s finding and the reason this LLR is a precondition of the census gate
  rather than a companion to it.
- **Acceptance:** `AT-005`, `AT-006`

---

### 3.3 · HLR-canvas — the `dots` / `bgs` layers, braille edges, and carry B-05 *(Inc-1 and Inc-2)*

#### Acceptance (black-box) — HLR-canvas

- **Observable outcome:** the free-angle edges and pill backgrounds the radial view has been drawing
  all along reach the screen, so a radial map reads as a connected figure rather than as floating
  labels; and the selection tone stops claiming focus a region does not have.
- **Shipped surface:** `Canvas.rows()` as consumed by every renderer, reached through
  `MapScreen`'s canvas repaint on the real `r` key (`map 'r' -> toggle_radial`, executed **M-9**),
  and through `mapper/export.save_svg` for the exported artifact.
- **Deliverable + observation:** a rendered `rich.Text` whose painted characters include glyphs in
  the braille block; observed by counting characters in `U+2800` through `U+28FF` in `Text.plain`.
- **Acceptance tests:** `AT-007`, `AT-007b`, `AT-008`, `AT-009`, `AT-010`.
- **`AT-007` IS SPLIT — it named two different chains (`QA-M-12`, §6.5 A-37).** It was claimed by
  **both** `HLR-CNV.1` (a unit assertion on `Canvas`) and `HLR-CNV.2` (the `RadialRenderer` render
  chain) — two different chains under one id, which cannot be one on-disk node. **`AT-007`** stays
  with `HLR-CNV.1` (the `Canvas` layer reaches `rows()`); **`AT-007b`** is `HLR-CNV.2`'s
  `PIN (radial)` node, which drives `RadialRenderer` on the M-1 6-node fixture at 80 x 24 and
  carries the containment arm.
- **Boundary catalog (QC-3):**
  - ☑ **empty** — `AT-007b` drives a single-node graph, where the braille count is legitimately 0
    and the requirement must not claim otherwise. It asserts **`len(cv.dots) == 0`** as well as the
    rendered count, so the arm names one cause rather than passing for two (§6.5 A-24).
  - ☑ **boundary** — `AT-008` writes a background at the last addressable cell and one cell past it,
    asserting the out-of-bounds write is dropped rather than raising.
  - ☑ **invalid** — `AT-008` writes a `dots` sub-cell coordinate outside the canvas and asserts no
    exception and no painted cell.
  - ☑ **error** — `AT-009` asserts `export.save_svg` still writes a non-empty file when the layers
    carry content, because `rows()`'s output bytes are what it consumes (trigger B4).

#### HLR-CNV.1 — the declared layers reach the rendered output

- **Traceability:** HLR-canvas (US-N06, US-N14 both consume it)
- **Statement:** The canvas shall declare a `dots` layer and a `bgs` layer in its constructor, and
  `rows()` shall compose both into the returned text, so that a renderer writing to either layer
  produces painted output.
- **Rationale (informative):** `RadialRenderer` assigns `cv.dots = {}` and `cv.bgs = {}` onto the
  instance (`radial.py:47-48`) and writes to both (`:121`, `:135`), but `Canvas.__init__`
  (`canvas.py:30-33`) declares neither and `rows()` (`canvas.py:67-82`) reads only `self.cells` and
  `self.bits`. Every braille glyph and every pill background is discarded silently. This is the
  batch's **second, unnamed A3** (R-016, risk A-8): additive and widening, but it changes `rows()`
  output bytes, which `export.save_svg` consumes.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_canvas.py -k "layers_reach_rows"` *(provisional)* —
  construct a `Canvas`, write to `dots` and to `bgs`, call `rows()`, count braille-block characters
  and inspect the style of the background cell.
- **Numeric pass threshold:** braille-block character count `> 0` where the pre-state is exactly
  **0**; the background cell's style names the written tone.
- **Priority:** high — Inc-3's fold pills depend on `bgs` reaching the screen.
  *(~~"and Inc-5's figure-ground"~~ is superseded: the figure-ground consumer was US-N14, **DEFERRED**
  by `#D23`. The dependency is real and travels with the story; it is not a live dependency of this
  batch. Inc-5 under §5.4 is hit painting, which consumes the same layers for a different reason and
  keeps the priority where it was.)*
- **Acceptance:** `AT-007`, `AT-008`

- **PREDICTED-RED CLAUSE — four legacy digest pins, red BY CONSTRUCTION (`P2-B4`, `C-24`, §6.5
  A-46).** Trigger **B3** is FIRED: this HLR's entire content is making bytes reach `rows()` that a
  shipped sha256 guard has pinned. `C-24` therefore requires the predicted-red set be named **by
  derivation** rather than discovered at the gate:

  > **QUESTION.** Which shipped byte-identity pins does the increment owning this HLR turn red?
  >
  > **INSTRUMENT.** Take the key set of `MASTER_LEGACY_DIGESTS` (`tests/test_repair_depth.py:93`),
  > which is keyed `(renderer name, w, h)` over `GOLDEN_SIZES` (`:91`) and asserted at `:815`.
  > A key is predicted **red** if and only if this HLR changes that renderer's `rows()` output at
  > that size; predicted **green** otherwise. Evaluate the condition from the executed occupancy
  > probe, not by eye.
  >
  > **MEASURED AT.** `20f86de`. **Cardinality deliberately not transcribed** — the dictionary is the
  > authority and the test reads its keys.

  **Derived, and the derivation is short:** `RadialRenderer` is pinned at **every** `GOLDEN_SIZES`
  entry, and §3.3's executed occupancy probe measures it writing dots and bgs **at exactly those
  sizes**, all currently discarded by `Canvas.rows()`. So **every `RadialRenderer` key reddens, by
  construction, and that is CORRECT behaviour** — an expected re-baseline, not a regression. Every
  `LayeredRenderer` and `OutlineRenderer` key is predicted **green**: `LayeredRenderer`'s dots are
  **0** and `OutlineRenderer` builds no `Canvas`, so neither renderer's output changes.
- **THE HAZARD IS THE REPAIR, NOT THE RED.** An implementer facing red digests re-captures the
  dictionary wholesale, and the `LayeredRenderer` and `OutlineRenderer` pins — which must **not**
  move — silently lose their guard. **Re-capturing a predicted-green digest is a gate failure**, and
  each predicted-red re-capture is done one at a time with its own recorded reason. This is the same
  rule `LLR-N06.2.1` states for `MASTER_RAIL_DIGESTS`; it is stated in both places because the two
  increments meet it independently and neither reads the other's requirement.
- **`MASTER_FACTORY_TREE_DIGEST` (`:121`, asserted at `:1077`) is predicted GREEN here** and is
  named so the third dictionary is not the one nobody thought about. Its subject is
  `FactoryScreen._tree_lines`, which this HLR does not reach.

- **STANDING RE-RUN OBLIGATION — `AT-007` and `AT-009` are RE-RUN AFTER `Inc-2` (`C-D4c`, `P2-C2`,
  §6.5 A-54).** `AT-007` and `AT-009` are `Inc-1` deliverables: the layers reach `rows()`, and the
  bytes `rows()` returns reach the written SVG. **`Inc-2` then changes the signature of every
  function that drives that chain**, under a byte-identity gate that compares a renderer against
  *itself* before and after. **A byte-identity gate cannot see a chain that was already broken**, and
  it cannot see one that `Inc-2` breaks in the same way on both sides. So `Inc-2` shall re-run both,
  and **`Inc-2` does not close with either red**.
- **THIS CLAUSE EXISTED ONLY AS A REVIEW FINDING FOR THREE PASSES, AND THAT IS THE POINT `P2-C2`
  MAKES.** `C-D4c` was raised at the first architect pass and carried through two more. Executed at
  `3fe0e4b`, `C-D4c` appears in the reviewer files and in `PLAN.md` — **and in no requirement**.
  **A recorded finding is not a clause**: nothing in the increment's own gate would have failed if
  the re-run never happened, because a gate reads requirements, not review notes. It is written into
  the requirement here, which is the only place an increment gate looks.
- **Named weaker variant (`M-CNV.1-rerun`):** re-run only `AT-007`. It asserts the layers still reach
  `rows()` **in memory** and says nothing about the written artifact — and `LLR-CNV.2.1`'s own
  executed evidence is that a 19 679-byte SVG containing **zero** braille passes `size > 0` twice.
  Reddened by re-running `AT-009`, whose threshold is the on-disk code-point equality.
- **Executed pre-state (M-1):** a 6-node graph through `RadialRenderer` at 80 x 24 yields **0**
  glyphs in `U+2800`–`U+28FF`; distinct painted non-space characters are
  `['A','F','H','I','N','R', …, '·','◆','●']`. `LayeredRenderer` on the same graph also yields **0**.

##### LLR-CNV.1.1 — the layers are declared, not monkey-patched

- **Traceability:** HLR-CNV.1
- **Statement:** The canvas constructor shall initialise `dots` and `bgs` as empty mappings, and the
  radial renderer shall stop assigning them onto the canvas instance.
- **Touched symbols:** `mapper/canvas.py::Canvas.__init__` (`canvas.py:30-33`);
  `Canvas.dots` and `Canvas.bgs` — both `NEW — created in Phase 3`;
  the two assignments at `mapper/views/radial.py:47-48` are **deleted**.
- **Validation:** `test (unit)` + `inspection`
- **Executed verification:** `pytest tests/test_canvas.py -k "layers_declared"` *(provisional)*
  asserts a freshly constructed `Canvas` exposes both attributes; and a grep asserts
  `cv.dots =` / `cv.bgs =` no longer appear in `mapper/views/`.
- **Numeric pass threshold:** 2 attributes present on a bare `Canvas(10, 10)`; **0** instance
  assignments remaining in `mapper/views/` (pre-state executed: **2**, at `radial.py:47` and `:48`).
- **Acceptance criteria:** the deletion is **asserted**, not assumed. A monkey-patch left in place
  alongside a declared attribute is how the two definitions come back.

##### LLR-CNV.1.2 — `rows()` composes the layers in a declared order

- **Traceability:** HLR-CNV.1
- **Statement:** When a cell coordinate carries content in more than one layer, `rows()` shall
  resolve it by the declared precedence — an explicit cell outranks a wire, a wire outranks a braille
  dot — and shall apply a background from `bgs` to whichever glyph wins.
- **Touched symbols:** `mapper/canvas.py::Canvas.rows` (`canvas.py:67-82`).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_canvas.py -k "layer_precedence"` *(provisional)* —
  write a cell, a wire and a dot to one coordinate and assert the resolved character.
- **Numeric pass threshold:** 3 precedence pairs asserted, 3 of 3 resolve as declared.
- **Acceptance criteria:** precedence is written down because `rows()` today has an implicit
  cell-then-wire order (`canvas.py:69-79`) that this change must preserve rather than reshuffle.
  Existing behaviour for `cells` and `bits` is unchanged — asserted, so the widening cannot regress
  the 245-test baseline.

##### LLR-CNV.1.3 — out-of-bounds layer writes are dropped, not raised

- **Traceability:** HLR-CNV.1
- **Statement:** If a renderer writes to a `dots` or `bgs` coordinate outside the canvas bounds, then
  `rows()` shall omit it from the output and shall not raise.
- **Touched symbols:** `mapper/canvas.py::Canvas.rows`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_canvas.py -k "layers_out_of_bounds"` *(provisional)*.
- **Numeric pass threshold:** 0 exceptions raised; output row count equals `h`; every output row
  length equals `w`.
- **Acceptance criteria:** `put` already guards bounds (`canvas.py:35-37`); the new layers are
  written by coordinate arithmetic in `radial.py` that does **not** guard, so the guard has to live
  in `rows()`.

##### LLR-CNV.1.4 — the layer tone is a declared token, with a fallback *(closes `Q-10`'s other half)*

- **Traceability:** HLR-CNV.1, security recommendation **C-9** (`02b` S-10)
- **Statement:** The value stored in the `dots` and `bgs` layers shall be a token name drawn from the
  design module's declared token set, and `rows()` shall paint a cell whose tone is not in that set
  in a declared fallback tone.
- **THE STYLE SINK FAILS OPEN, SILENTLY — and the parked threshold asserted the opposite of a guard
  (§6.5 A-39).** `LLR-CNV.1`'s only threshold on the value is *"the background cell's style names the
  written tone"*, which asserts **pass-through**. `02b` drove 14 malformed style strings —
  `#zzzzzz`, `not-a-colour`, `on nosuchcolour`, `color(999)`, `rgb(300,300,300)`, a `link` style, a
  constructed ESC sequence, a 1 600-character style — through `Text.append` **and** through the real
  `Canvas.rows()` with truecolor on: **all 14 render OK and none raises.** Meanwhile
  `Style.parse('not-a-colour')` **does** raise `StyleSyntaxError` — Rich's `Text.render` swallows it
  via `get_style(..., default="")`. **A malformed tone does not crash a render; it silently paints
  unstyled**, which is indistinguishable from a tone that was never applied.
- **Named weaker variant (`M-V1`, from `02b`):** validate at write time in `put` / a `dots` setter.
  **Survives** — it misses `radial.py`'s direct `cv.dots[(...)] = hue` assignment, which bypasses any
  setter (executed: that is one of the two `.dots` sites in the tree). **The validation lives in
  `rows()`, the one place all four layers converge.**
- **Touched symbols:** `mapper/canvas.py::Canvas.rows`; the declared token set in
  `mapper/darkside.py`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_canvas.py -k "layer_tone_is_a_declared_token"`
  *(provisional)* — the 14 malformed style strings above, each constructed at run time.
- **Numeric pass threshold:** cells whose tone is outside the declared token set painted in the
  fallback tone `== 14 of 14`; **0** exceptions; and a cell whose tone **is** in the set keeps it.
- **No new bound is invented for the token set.** It is `LLR-S06.1.1`'s declared set plus the token
  `#D10` promotes from `radial.py:18`'s `#a3a3a3` — so **this LLR closes the other half of `Q-10` in
  the same sentence** rather than creating a second vocabulary.

#### HLR-CNV.2 — `PIN (radial)` · braille free-angle edges reach `RadialRenderer`'s painted output

- **Traceability:** HLR-canvas (US-N06)
- **Statement:** When a map graph with at least one parent-child edge is rendered through a renderer
  that draws free-angle edges, the system shall paint at least one character in the braille block,
  **and** the set of distinct non-space characters the same renderer painted for the same graph at
  the same geometry before the change shall remain a subset of the set it paints after.
- **Rationale (informative):** the acceptance is deliberately a **count**, not "braille appears"
  (risk A-8). A count has a measured pre-state of exactly 0 and a mutation that can move it; an
  adjective has neither. The **containment arm** is the second half, and it exists because a count
  alone is one-sided — see the mutation block below.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_radial.py -k "braille_edges_reach_the_screen"`
  *(provisional)* — render the 6-node graph of **M-1** at the declared geometry 80 x 24, count
  characters in `U+2800`–`U+28FF`, and compare the distinct painted non-space sets.
- **Numeric pass threshold:** through `RadialRenderer` on the **M-1** 6-node graph at **80 x 24** —
  braille count `> 0`; **and** `pre_set ⊆ post_set`, both derived at run time. On a **single-node**
  graph — braille count `== 0` **and `len(cv.dots) == 0`**.
- **`AT-007b`'S EMPTY ARM IS VACUOUS AS WRITTEN, AND THE FIX IS ONE ASSERTION (§6.5 A-24; id
  corrected by `QA2-C-08`, §6.5 A-63 — this requirement's `Acceptance:` line is `AT-007b`, and the
  empty arm is `AT-007b`'s under the A-37 split).**
  `count == 0` on a single-node graph passes **today**, before any fix, for **two independent
  reasons**: `|cv.dots| = 0` *and* `Canvas.rows()` drops the dots layer regardless. An arm that
  passes for two reasons cannot tell you which one held, and after the P-1 fix it would silently
  change from passing for the wrong reason to passing for the right one with no observable
  difference. Executed: `single node -> radial |cv.dots| = 0`, against `195` on M-1 and `267` on
  legacy. Asserting `len(cv.dots) == 0` names the one cause the arm is about.
- **Priority:** medium
- **Acceptance:** `AT-007b`

- **SUBJECT — SETTLED BY MEASUREMENT: this is a regression `PIN` on `RadialRenderer`, not a gate on
  the map canvas (§6.5 A-24, superseding A-12's open criterion).** A-12 wrote the criterion —
  *"the subject is whichever renderer the Inc-2 change causes to emit braille"* — and left the
  answer to measurement. The measurement is in, and it is **structural, not incidental**:

  ```
                   LayeredRenderer braille   RadialRenderer braille   radial |cv.dots|
  legacy 8-node          0                          0                      267
  M-1    6-node          0                          0                      195
  single node            0                          0                        0

  $ grep -rn "\.dots\b" mapper/ --include=*.py
  mapper/views/radial.py:123:        cv.dots = {}
  mapper/views/radial.py:209:            cv.dots[(int(dx * 2), int(dy * 4))] = hue
  ```

  **`LayeredRenderer` never populates a `dots` layer — there are exactly two `.dots` sites in the
  entire tree and both are in `radial.py`.** Also measured: `|cv.bits| = 0` for radial, so radial
  never calls `Canvas.wire()` and cannot paint a box-drawing glyph. Therefore **no fix to
  `Canvas.rows()` can raise the map canvas above 0 braille.** Moving the subject would make the
  requirement **unsatisfiable by the change under test** — it could only be met by also teaching
  `LayeredRenderer` to draw free-angle edges, which is a different feature and is not in scope.
  `PLAN.md` D19's precedent applies: moving the subject would create a second definition of *"the
  canvas that draws free-angle edges"*.
- **Consequences of the `PIN` label, carried rather than implied.** The title, the §5.2 row and
  `AT-007b` all name `RadialRenderer`, the `M-1` 6-node fixture and the render size `80 x 24`; the
  parked §5.2 entry read *"count > 0, and 0 on a single node"* with **no subject at all**. And **the
  map-canvas promise now belongs to no requirement in this batch** — recorded in §6.2 as a declared
  gap, per C-40's corollary that a pin must be labelled a pin.

- **THE CONTAINMENT ARM — `QA-B-09`'s second defect, which is the one `> 0` cannot see.** Where the
  pre-state is 0, `count > 0` reddens a **deletion** (compose neither layer) but **cannot redden a
  plausible wrong implementation**. Named mutation, stated at authoring time:

  | Mutant | Plausible because | `count > 0` | containment arm |
  |---|---|---|---|
  | **M-CNV.2-a** compose `dots` at the **wrong precedence**, so braille overwrites the node cards | precedence is one argument order in one composite call, and the layer *is* drawn | **passes** — the glyphs are emitted | **reddens** — the card glyphs vanish from the painted set, so `pre_set ⊄ post_set` |
  | **M-CNV.2-b** draw braille only in cells that were already blank | it looks like the safe version of the same change | passes | passes — correctly: nothing is lost, and this is not a defect |

  Braille is **added**; nothing is lost. That is what the arm asserts.

- **THE ARM'S SET IS DERIVED AT RUN TIME AND MUST INCLUDE ASCII — the parked hand-list fails in BOTH
  directions (§6.5 A-11, A-24).** `pre_set` is captured at run time from the renderer under test at
  the declared geometry, immediately before the change:
  `pre_set = {c for c in painted_text if not c.isspace()}`. Three candidate sets, measured against
  the two composition arms on **M-1** at 80 x 24:

  | Candidate set | `|S|` | `S ⊆ POST_good` | `S ⊆ POST_mutant` | reddens the mutation? |
  |---|---|---|---|---|
  | **full distinct non-space set (derived)** | **19** | **True** | **False** | **yes** |
  | non-ASCII subset only | 3 | True | True | **no — vacuous** |
  | the parked hand-listed set | 10 | **False** | False | **no — false-fails the correct fix** |

  Re-executed independently in this amendment session, the radial pre-change painted set is
  `abcdefilmnoprstz·◆●` — **19 glyphs, of which only 3 are non-ASCII** (`·` the header separator,
  `◆` the root marker, `●` the non-root markers). The parked set's other seven members
  `─ │ ┌ ┐ ┬ ┼ ▐` are **`LayeredRenderer` glyphs `RadialRenderer` never paints**, confirmed by
  `|cv.bits| = 0`. So the parked set is not even a subset of the *pre-change* render, and adopting
  it verbatim would **block the correct fix** — the same defect class as `QA-B-02`'s root-title
  oracle, reappearing inside the remedy for a different blocker.
  **And a non-ASCII-only set is vacuous**: all three of `· ◆ ●` survive the mutation, because the
  markers sit at pill origins the braille happens not to overwrite. **The glyphs the mutation
  actually destroys are ASCII letters** contributed by single pill titles, so a set that excludes
  ASCII discriminates nothing. A hand-listed `pre_set` is an unproven claim (C-31) and — measured —
  a wrong one, in both directions at once.

- **Flagged `assumed — verify in Phase 3`:** the *number* of braille glyphs a given graph produces.
  Only the strict positivity is specified, because the count depends on `radial.py`'s step
  arithmetic and pinning a number would make the test brittle against a layout tweak with no
  user-visible meaning. The **containment** arm is not brittle in that way: it is a subset relation
  over a set derived from the same code path on both sides.

##### LLR-CNV.2.1 — the export artifact is regenerated from the new bytes

- **Traceability:** HLR-CNV.2
- **Statement:** When the map is exported while a layer-drawing renderer is active, the system shall
  write an SVG file whose content is produced from the same `rows()` output the screen shows.
- **Touched symbols:** none changed in `mapper/export.py` — `save_svg` (`mapper/export.py`) consumes
  the `rich.Text` it is handed. This LLR pins the **B4 consequence** so it is asserted rather than
  merely permitted (risk A-8's explicit question).
- **Validation:** `test (integration)`
- **Executed verification:** `pytest tests/test_export.py -k "export_carries_canvas_layers"`
  *(provisional)* — render the radial view, call `save_svg` to a temporary path, assert the file
  exists and is non-empty.
- **Numeric pass threshold — the assertion is ON THE WRITTEN FILE (`QA-B-06`, §6.5 A-23):**
  `disk_braille(path) == braille_count(on_screen_text.plain)`, where `disk_braille` **scans code
  points in the written bytes**:

  ```python
  def disk_braille(path):
      raw = path.read_text(encoding="utf-8")
      return sum(1 for c in raw if 0x2800 <= ord(c) <= 0x28FF)
  ```

  File exists and `size > 0` are retained as preconditions **and are explicitly not the threshold**.
- **~~The equality is between the two `Text` objects.~~ SUPERSEDED — the chain never touched the
  written artifact.** `02b` C-12 and `QA-B-06` are right: an in-memory equality asserts the producer
  against itself. Executed at `d877784`, the real chain `RadialRenderer -> save_svg -> disk`:

  ```
  (a) PRE-STATE      in-memory braille = 0 ; ON-DISK braille = 0
                     file exists=True  size=19679 bytes   -> the shipped `size > 0` PASSES
  (b) POSITIVE CTRL  braille placed in cells -> ON-DISK 12 of 12 recovered (distinct 11)
  (c) NEGATIVE CTRL  payload-free export     -> ON-DISK 0, size=2732  -> `size > 0` PASSES again
  ```

  **`size > 0` passes on an artifact containing zero braille, twice.** That is the vacuity, shown
  rather than argued. The `0` in (a) is admissible as an absence only because (b) proves the oracle
  can produce a non-absence (C-55).
- **THE SUBSTRING CAVEAT IS CONDITIONAL, AND THAT IS THE TRAP (§6.5 A-23).** `QA-B-06` states a
  substring oracle over the SVG *"returns False even for correct content"*. Executed, that is true
  only under **per-cell style variation**:

  ```
  ARM 1  uniform style on every braille cell    ->  5 <text> nodes ; 12-glyph run as SUBSTRING: True
  ARM 2  per-cell 3-tone scheme, as radial.py   -> 16 <text> nodes ; SUBSTRING: False
                                                   longest recoverable run: 1 of 12
  ARM 3  real rendered titles from the shipped radial SVG
           Finanzas / Inventarios / Contabilidad  in painted Text: True   as SUBSTRING: False
           mapper                                 in painted Text: True   as SUBSTRING: True
  ```

  `radial.py` assigns a per-branch tint from `_GREYS` to every dot (`:207-209`) and a per-character
  style to every pill glyph, so Rich emits one `<text>` span per style run. **An implementer who
  writes the positive control the easy way — one uniform style — measures ARM 1, sees `True`, and
  concludes the caveat was wrong.** The requirement therefore carries **both** clauses:
  - the read-back **shall** scan code points, or parse `<text>` nodes
    (`re.findall(r"<text[^>]*>(.*?)</text>", raw, re.S)` recovered all 12); and
  - the read-back **shall not** be validated against a uniformly-styled fixture, and **shall not**
    grep for a rendered string.
- **Named weaker variant (`M-CNV.2.1-a`):** keep `size > 0` and add an in-memory `Text` equality.
  Green today on a 19 679-byte file containing zero braille — it asserts the producer against
  itself and never opens the file. Reddened by the on-disk code-point equality.
- **Named weaker variant (`M-CNV.2.1-b`):** assert a braille substring on disk, validated against a
  uniformly-styled positive control. Green on ARM 1, false-fails the real 3-tone output at ARM 2.
  Reddened by the second clause above.
- **THE SVG IS A DECLARED SINK AND SHALL CARRY THE COERCION RANGES (C-10, `02b` S-12, §6.5 A-40).**
  `mapper/export.py::save_svg` is a declared §4 `SINK` and sits on `canvas_rows`'s **transitive
  observer** line (corrected by `P2-C1`, §6.5 A-51 — it snapshots the SINK, it does not index
  `rows()`); trigger **B4** fired on it for the byte change and **nobody asked what text it writes**.
  *(The correction does not weaken this clause. Trigger B4 fires on an observer exactly as it fires
  on a consumer — the bytes change either way — and this LLR's on-disk threshold is what makes the
  change asserted rather than permitted.)* The
  exported SVG **shall** contain no code point in `COERCION_RANGES` (§3.0), sharing the same declared
  list. **An SVG leaves the machine; the terminal's own escaping does not travel with it** — the
  file is opened later by a browser or an editor with entirely different rules, which is why this is
  not covered by the on-screen coercion thresholds.
- **Acceptance:** `AT-009`
- **`AT-009`'S OWNERSHIP IS LANDED HERE, NOT MERELY ANNOUNCED (`P2-B2`, `QA2-C-01`, §6.5 A-44).**
  §6.5 A-29 recorded that `AT-009` *"is **promoted** under `LLR-CNV.2.1`, whose threshold A-23
  rewrote"* — but **the `Acceptance:` line that would have carried the promotion was never written**,
  so `AT-009` stayed catalog-only through two more PDR passes while an amendment said it had moved.
  **A promotion recorded in an amendment and not written into the requirement is not a promotion**;
  it is the amendment-table failure mode this batch has now hit three times. The line above is the
  promotion. `AT-009` is the export-artifact arm of the HLR-canvas boundary catalog (`:972`) and this
  is the only requirement in the document that asserts on the written file, so the ownership was
  never in doubt — only unwritten.
- **Acceptance criteria:** **the exported bytes change, and that change is asserted on the bytes.**
  Not against a stored golden — the repo has no byte-identity goldens (P-8, executed: no
  `tests/goldens/` directory), so a golden would be new infrastructure this batch has not budgeted.
  The comparison is on-disk count versus on-screen count, both computed at run time.

#### HLR-CNV.3 — the selection tone is focus-aware *(closes carry B-05)*

- **Traceability:** HLR-canvas, carry B-05
- **Statement:** While the region that owns the canvas does not hold focus, the renderer shall paint
  the selected node with a tone distinct from the tone it paints while that region holds focus.
- **Rationale (informative):** B-05 is that the canvas paints a full-strength selection block
  regardless of where the keyboard actually is, so three regions each claim the selection at once.
  The fix is a **field**, not a mechanism: `ViewState.focus_owner` is a plain string, which keeps the
  `views` module free of any Textual import (`docs/ARCHITECTURE.md` §3, §4a rule 5).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_layered.py -k "selection_tone_is_focus_aware"`
  *(provisional)* — render the same graph twice with `focus_owner` set to `"canvas"` and to
  `"inspector"`, and compare the style spans covering the selected node's cells.
- **Numeric pass threshold:** the two style strings differ; both renders paint the same characters,
  so the difference is tone only and not content.
- **Priority:** medium
- **Acceptance:** `AT-010`
- **Value reconciliation (C-36):** `focus_owner` is `NEW — created in Phase 3`, declared in the ARQ
  contract (`docs/ARCHITECTURE.md` §4a) with the value domain `"" | "canvas" | "rail" | "inspector"`.
  Executed: `grep -rn "focus_owner" mapper/` returns no output today.

##### LLR-CNV.3.1 — the screen supplies the real focus owner

- **Traceability:** HLR-CNV.3
- **Statement:** When `MapScreen` builds the view state for a repaint, it shall set the focus-owner
  field from the application's currently focused widget, mapped to one of the declared region names.
- **Touched symbols:** `mapper/app.py::MapScreen.refresh_canvas` and the `ViewState` construction
  inside it; `mapper/views/state.py::ViewState.focus_owner` — `NEW — created in Phase 3`.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_app.py -k "focus_owner_tracks_real_focus"`
  *(provisional)* — press the real `tab` key and read the value the screen puts into the state.
- **Numeric pass threshold:** after 1 real `tab` press from the canvas, the field reads `"rail"`;
  after 2, `"inspector"`. Pre-state measured (**M-10**): press 1 focuses `OutlineRail#map-rail`,
  press 2 focuses `FieldInput#insp-title`.
- **Acceptance criteria:** the acceptance drives the real `tab` key, never `.focus()` — control C-16.
  A mapping derived from `app.focused` is what makes the string true rather than declared.

---

### 3.4 · US-N06 «escala» — a canvas that holds a map bigger than the screen *(Inc-3)*

> **The story's whole promise is a quantity, not an adjective.** "Nothing clips silently" is
> specified below as: *the count of nodes not painted equals the count the indicator declares.*
> Measured pre-state (**M-5**): on an 80-column canvas the layered view paints a readable title for
> **at most 7 nodes regardless of graph size**, declares the full node count in its header, and
> paints **no** overflow declaration. At 129 nodes that is **121 nodes hidden with zero declaration**
> (94 %). That number is the defect, executed.

#### Acceptance (black-box) — US-N06

- **Observable outcome:** the operator moves a window over a map larger than the screen, folds
  branches away, and at every moment can read a declaration of how much is not on screen — and that
  declaration agrees with the fold pills painted beside it.
- **Shipped surface:** `MapScreen`'s canvas, driven by the real pan chords and the real fold chord
  (`z`, already `collapse_branch` in the seat — **M-9**), observed through the `#map-canvas` widget's
  rendered `Text.plain` and through the rail's rendered text.
- **Deliverable + observation:** a painted canvas whose visible column range changes with pan; a
  painted pill of the form `▸ <rama> +N` for each folded branch; and a painted overflow indicator
  declaring a total. All three observed as substrings and counts in the rendered text of the shipped
  widgets, never by reading a renderer's return value directly.
- **Acceptance tests:** `AT-011`, `AT-012`, `AT-013`, `AT-014`, `AT-015`, `AT-016`, `AT-017`,
  `AT-046`, `AT-047`.
- **`AT-046` and `AT-047` JOIN THIS LIST (`QA2-C-01`, §6.5 A-44).** Both were added at reconciliation
  for `LLR-N06.2.4` (the fold auto-open), reached `LLR-N06.2.4`'s `Acceptance:` line and §5.2's
  behavioral row — **and never reached this story list**, so the three-way intersection §5.2 defines
  as the batch's `AT` count silently excluded them. **The intersection is the count; an id missing
  one leg is not counted, however real its predicate is**, which is why this omission was a defect
  and not a formatting slip. `AT-046` and `AT-047` are the arms that stop `AT-022` passing on a
  screen where the operator cannot see the selection.
- **Boundary catalog (QC-3):**
  - ☑ **boundary** — `AT-012` drives pan at both edges: panning left at column 0 and right at the
    last column that leaves any content visible.
  - ☑ **empty** — **two cases, because the parked cell claimed coverage it did not have
    (`QA-M-07`, §6.5 A-34).** The parked entry filled ☑ **empty** with *"a map that fits entirely on
    screen with nothing folded"* — that is a **zero-hidden** case, not an empty one, and `01b`'s
    **E3** (a map with **0 nodes**) had no predicate anywhere, while `LLR-N06.3.3`'s fixture is the
    6-node M-1 graph. Both are now driven:
    - **zero-hidden** — `AT-015` at `(50, 12, ())` on `legacy`: declared hidden total **0**, and the
      indicator's behaviour at zero is specified rather than left to the implementer;
    - **genuinely empty (E3)** — `AT-015` drives a **0-node** graph and asserts the screen mounts,
      the indicator is absent, and no pill is painted. Executed at `d877784`:
      `LayeredRenderer.render` returns `Text("(no map loaded)")` when `graph.root_id is None or not
      graph.nodes` (`layered.py:141-142`), so the case has a defined shipped behaviour to pin and is
      not new mechanism.
  - ☑ **invalid** — `AT-013` folds a leaf (a branch with 0 descendants) and asserts the specified
    outcome rather than a pill reading `+0`.
  - ☑ **error** — `AT-017` folds while the rail is auto-hidden at 80 columns, the regime R-013 exists
    for; fold continues to work with its rendering surface not displayed.

#### HLR-N06.1 — pan moves the window and is bounded

- **Traceability:** US-N06
- **Statement:** When the operator presses a pan chord on a map wider or taller than the canvas, the
  system shall paint a different range of the map than before the press; and if a pan chord would
  move the window past the map's extent in that direction, then the system shall leave the painted
  range unchanged **and shall paint the hint line reading `borde del territorio`**, and shall not
  scroll past the content into blank space.
- **Rationale (informative):** a pan that runs off into empty space is a pan that loses the map, and
  an operator who cannot tell "I am at the edge" from "the keyboard stopped working" has been given
  a worse tool than no pan at all. The bound is stated as an **unwanted-behaviour** clause so it is
  a requirement rather than an implementation detail.
- **Reconciled against `01b-ux-decisions.md` DECISION 4 state E5.** This requirement's first draft
  specified a **silent** no-op at the edge, which the ux lens rules insufficient: blank space past
  the content is indistinguishable from "the map has nothing there", which is the exact confusion
  US-N06 exists to remove. The declaration clause is added. Audit row §6.4 D-2.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_pan.py -k "pan_moves_and_is_bounded"`
  *(provisional)* — drive the real pan chord under `App.run_test(size=(140,45))` on a graph whose
  layout exceeds the canvas, and compare `#map-canvas` rendered text before and after.
- **Numeric pass threshold:** after 1 pan press the rendered text differs from the pre-press text;
  after `K` further presses in the same direction, where `K` is large enough to exhaust the extent,
  the rendered text is **identical** to the text after the previous press, and no exception is
  raised, **and** the hint line contains `borde del territorio`. `K` is derived at run time from the
  graph's layout extent and the canvas width, never hard-coded.
- **Priority:** high
- **Acceptance:** `AT-011`, `AT-012`
- **THE PAN CHORD IS NAMED: `H`, `J`, `K`, `L` (`UX2-C-03`, §6.5 A-65).** ~~*"This requirement stays
  written chord-agnostic; PDR ratifies the specific chords"*~~ is superseded. `QA-B-10`'s rule is
  that **a chord-agnostic requirement is legitimate; a chord-agnostic acceptance test is not**
  (`C-16`) — and the rule was applied to US-N07 (`#D5b`) and to US-N14 (`#D6`) and **missed here**.
  `AT-011` and `AT-012` are acceptances that press no named key.
  - **The aggravator, which is what makes this a defect rather than an untidiness:** `AT-012`
    asserts the `borde del territorio` declaration — a clause the ux lens added **specifically
    because** the draft's silent no-op was ruled insufficient — **against a key nobody had named**.
    The most carefully argued clause in this requirement was unfalsifiable for want of a keystroke.
  - **Executed, not assumed.** `01b` DECISION 6 row 2 is a Pilot transcript: `H` `J` `K` `L` arrive
    as `event.key` values `'H' 'J' 'K' 'L'` in their own right (Textual reports `event.name`
    `upper_h` and the like), **all four are free in map scope**, and pressing `H` on the shipped
    `MapScreen` changes nothing today. Re-derived against the live seat at `ea1fbf9`: map scope
    binds 25 chords plus 2 app-scope, and of the uppercase letters only `A`, `I`, `R`, `X` are taken
    — `H`, `J`, `K`, `L` are free. `duplicate_chords()` on the shipped seat returns `[]`.
  - **The idiom is the argument.** `hjkl` already navigates in map scope; `⇧hjkl` pans. The shifted
    pair precedent is already in the seat.
- **THRESHOLD ADDENDUM:** `AT-011` and `AT-012` **shall press the real `H`, `J`, `K` and `L`**, never
  `action_*` directly. `AT-012`'s edge arm presses the same real key until the extent is exhausted
  and reads the hint line from the painted frame.
- **EVERY BINDING ADDED EXTENDS THE WHOLE-SEAT SPEC, AND THAT SPEC IS PINNED.** `mapper/keymap.py`'s
  `KEYMAP` and `GROUP_SCOPE` are the seat, pinned by `tests/test_keymap.py`. Adding four rows changes
  that pin, so `Inc-3` **shall** re-run `duplicate_chords()` and the whole-seat set equality, exactly
  as `Inc-4` and `Inc-9` must — this is the third participant in `keymap.py`'s three-way collision
  (§5.4), and it is the one that had no declared rows until now.
- ~~**⚠ ROUTED — `#D10`'s SEAT-DIFF CAP IS NOW ARITHMETICALLY BREACHED …** `Inc-3` shall not open
  until the cap is ruled.~~ — **STRUCK 2026-08-27 by `PDR-addendum-3#D25`. THERE IS NO BREACH AND
  `Inc-3` IS UNBLOCKED.** The premise executed FALSE: the "three-row seat-diff cap" is a
  **regression PIN on `Inc-4`'s own diff**, not a per-increment budget. `PLAN.md:244`, the pin's
  carrier, reads *"the seat-spec diff is **exactly one changed row plus two added rows**, reviewed
  row-by-row at DDR"* — an **equality on `D10`'s own diff**, not a bound on anyone else's. The
  sealed `#D5b` enumerates those same three rows and its **very next sentence** names `Inc-3` as a
  `keymap.py` toucher while imposing only `duplicate_chords()` + the whole-seat pin on it — **no row
  budget.** Ratified independently by all four PDR-3 lenses; the architect located the carrier
  clause the ruling itself had missed.
- **⚠ The bare id `#D10` is AMBIGUOUS and is not used normatively here.** `PLAN.md:244` `D10` is the
  Q-3 seat rebind; the sealed `PDR-…#D10` is the Q-10 **hue** dispositions. Two registries, one id
  grammar. Carried as `B-34`. Cite `#D5b` for the pin and `PDR-addendum-3#D25` for its scope.
- **`Inc-3` owes instead (`C-D25a`, `C-D25b`):** its **own** four-row seat diff, declared in its
  packet and asserted **equal to the entry/exit difference of `bindings_for("map")`** — a pin per
  diff, never a global cap. Executed basis: all four chords arrive as their own `event.key`, all
  four free in map scope, `H` inert on the shipped screen, `duplicate_chords()` → `[]`.

##### LLR-N06.1.1 — pan offsets travel in the view state

- **Traceability:** HLR-N06.1
- **Statement:** The screen shall pass the current pan offsets to the renderer as fields of the view
  state, and the renderer shall translate its drawing origin by those offsets.
- **Touched symbols:** `mapper/views/state.py::ViewState.pan_x`, `ViewState.pan_y` —
  `NEW — created in Phase 3`, declared in `docs/ARCHITECTURE.md` §4a;
  `mapper/views/layered.py::LayeredRenderer.render` (`layered.py:78`);
  `mapper/app.py::MapScreen.refresh_canvas` (the `ViewState` construction).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_layered.py -k "pan_translates_origin"` *(provisional)*
  — render the same graph at two pan offsets and compare the painted rows.
- **Numeric pass threshold:** the two renders differ; both return exactly `h` rows of exactly `w`
  cells, so pan cannot change the output shape.
- **Acceptance criteria:** the renderer is a pure function of `(graph, state)` — it holds no pan
  state of its own, per the ARQ rule that `ViewState` is a message and not a store.

##### LLR-N06.1.2 — the bound is computed from the layout extent

- **Traceability:** HLR-N06.1
- **Statement:** The screen shall clamp each pan offset to the range determined by the rendered
  layout's extent and the canvas dimensions, and shall not accept an offset outside that range.
- **Touched symbols:** `mapper/app.py::MapScreen` — a clamp helper, `NEW — created in Phase 3`;
  `MapScreen._chrome_width` (`app.py:1166`) supplies the canvas width the clamp uses.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_pan.py -k "pan_clamp"` *(provisional)* — call the
  clamp with offsets far outside the range in both directions.
- **Numeric pass threshold:** for a layout of extent `E` and canvas width `W`, the clamped offset
  lies in `[0, max(0, E - W)]` for every input, over at least 6 inputs including both far extremes,
  `E < W`, and `E == W`.
- **Acceptance criteria:** the `E < W` case is included because a map smaller than the canvas has a
  legal pan range of exactly one position, and an off-by-one there is how the map jumps off screen
  on a small graph.

#### HLR-N06.2 — a folded branch is declared with its hidden count

- **Traceability:** US-N06
- **Statement:** While a branch is folded, the system shall paint in place of that branch's subtree a
  pill naming the branch and stating the number of its hidden descendants, **and, while a query or a
  lens is active, the number of matching nodes that pill is hiding, painted in the severity-warning
  tone**; and when the operator unfolds it, the system shall paint that branch's subtree again and
  remove the pill.
- **Rationale (informative):** fold already exists (`map 'z' -> collapse_branch`, executed **M-9**)
  but only the rail honours it; the canvas has never known about it. This requirement does not create
  fold — it relocates ownership to `MapScreen` (R-013 / D5) and makes the canvas a second reader of
  one truth.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_fold.py -k "fold_pill_declares_hidden_count"`
  *(provisional)* — load `fixtures/legacy_nodos.yml`, navigate to a branch with the real `j`/`l`
  chords, press the real `z`, read `#map-canvas` text.
- **Numeric pass threshold:** the painted text contains a pill whose numeral equals the branch's
  descendant count, for each of the fixture's three ramas. Executed descendant counts (**M-6**):
  `fin -> 2`, `rrhh -> 1`, `inv -> 1`.
- **Priority:** high
- **Acceptance:** `AT-013`, `AT-014`, `AT-017`
- **Value reconciliation (C-36):** the pill glyph `▸`, the `+N` form and the trailing hit-count
  form are all `NEW — created in Phase 3`. Executed: `grep -rn "▸" mapper/` returns no output.
  The painted form is fixed by `01b-ux-decisions.md` DECISION 5 step 3 as branch name, `+N` hidden
  descendants, then the hit count, with the hit count and the pill's left bar in `WARN`.
  **~~Here `WARN` is correct precisely because it does mean *a hit*.~~ CORRECTED — that reason
  executes FALSE (`QA-B-08`, §6.5 A-10).** Re-executed at `d877784`:
  `grep -rnE 'darkside\.(WARN|ALERT)' mapper --include=*.py` gives 36 sites and **0 of them paints a
  search hit**. The tone is nevertheless **kept**, on the corrected reason: `LLR-S06.3.5` declares
  `WARN`'s single job as *outstanding attention — work pending, due, at risk or in flight, and
  nothing has failed*, and matches hidden inside a folded branch are work the operator has pending.
- **Canvas glyph vocabulary — DERIVED, never hand-listed (§6.5 A-11).** The parked line listed the
  distinct painted set as `· ◆ ● ─ │ ┌ ┐ ┬ ┼ ▐ …`. Re-executed at `d877784` on the **M-1** 6-node
  shape at 80 x 24, that list does not reproduce as any single renderer's painted set:

  ```
  RadialRenderer    distinct non-space glyphs = 22 : ABCDERaefilmnoprstz·◆●
  LayeredRenderer   distinct non-space glyphs = 31 : 6ABCDERacdefilmnoprstz·─│┌┐┴┼▐◆
  ```

  `●` appears only in the radial set; `┬` appears in **neither** (the layered set carries `┴`). The
  parked list blends two renderers and includes a glyph the fixture never paints. Every predicate in
  this document that quantifies over "the canvas vocabulary" therefore **derives** the set at run
  time from the renderer under test at the declared Pilot size, and never cites this list.
  `█ ░` from `darkside.microbar` (`darkside.py:232`) remain a separate, non-canvas source.

##### LLR-N06.2.1 — fold state has one owner and two readers

- **Traceability:** HLR-N06.2
- **Statement:** `MapScreen` shall hold the set of folded node ids, shall pass it to the rail through
  the rail's show method and to the renderer through the view state, and the rail shall not hold a
  collapsed set of its own.
- **Touched symbols:** `mapper/app.py::MapScreen.folded` — `NEW — created in Phase 3`;
  `mapper/widgets/rail.py::OutlineRail.show` — signature widened to
  `show(graph, cursor, folded)` per `docs/ARCHITECTURE.md` §4;
  `mapper/widgets/rail.py::OutlineRail.collapsed` (`rail.py:35`) — **deleted**;
  `mapper/widgets/rail.py::OutlineRail.toggle` (`rail.py:42`) — **deleted**;
  `mapper/views/state.py::ViewState.folded` — `NEW — created in Phase 3`.
- **Validation:** `test (unit)` + `inspection`
- **Executed verification:** `pytest tests/test_rail.py -k "rail_renders_fold_it_does_not_own"`
  *(provisional)*; plus a grep asserting `collapsed` and `toggle` no longer appear on `OutlineRail`.
- **Numeric pass threshold:** the derived supersession set (below) is **non-empty** before it is
  evaluated, and is **empty after the increment**; the rail's rendered text reflects a folded set it
  was handed and never stored.

- **THE SUPERSESSION SET IS DERIVED, NOT ENUMERATED AND NOT ASSERTED AS A ZERO (`P2-B4`, §6.5 A-46,
  superseding A-41's `QA-N-07` half).**

  > **QUESTION.** Which call and attribute-access expressions in the tracked sources reference
  > `OutlineRail.collapsed` or `OutlineRail.toggle`, and must therefore move or die when this LLR
  > deletes them?
  >
  > **INSTRUMENT.** A walk over the tracked `mapper/**/*.py` **and** `tests/**/*.py` for the
  > attribute and the method, asserting the derived set is **non-empty before it is evaluated** —
  > exactly as `LLR-N06.2.5` and `LLR-S06.3.1` already do. Both trees, not `mapper/` alone.
  >
  > **MEASURED AT.** `20f86de`. **Cardinality deliberately not transcribed.**

  **`~~0 remaining references~~` was replaced by an enumeration that was itself short — the same
  defect with a number attached.** A-41 answered *"a zero that names no reference"* with *"`toggle`
  has 2 call sites, both in `tests/test_rail.py`"*. Re-derived over **both** trees, that enumeration
  is a **strict subset** of the real set, and two of the members it misses are the ones that matter
  most:
  - **a PRODUCTION call site** — `mapper/app.py:1259`, in `action_collapse_branch`. A supersession
    census that reports only test call sites, on an attribute the product itself calls, is a census
    scoped to the wrong tree. `C-18`: a premise counted at one file scope is under-counted tree-wide.
  - **the rail byte-identity guard itself** — `tests/test_repair_depth.py:1055`, inside
    `test_c53_the_rail_renders_legacy_identically_to_master`, parametrized over five fold
    configurations. **Deleting the attribute reddens the guard that exists to prove the rail did not
    change.** That is the predicted-red clause below, and it was invisible while the census stopped
    at `tests/test_rail.py`.

  The enumeration is retained **as evidence that the class is non-empty**, never as the
  specification — the same rule `LLR-N06.2.5` states for its 15 addresses. **The gate is the
  derivation.** `mapper/search.py` is separately confirmed **dead** — no import of it across
  `mapper/` or `tests/` — so every `search` LLR is **new-module work** in the ledger, not
  modification (`QA-N-11`).

- **PREDICTED-RED CLAUSE — the rail digest pins (`P2-B4`, `C-24`, §6.5 A-46).** Trigger **B3** is
  FIRED for this increment: it deletes a shipped attribute that a shipped byte-identity guard
  reaches. `C-24` therefore applies and the predicted-red set is named **by derivation**, before the
  gate:

  > **QUESTION.** Which shipped sha256 byte-identity pins does this increment turn red?
  >
  > **INSTRUMENT.** For each digest dictionary in `tests/test_repair_depth.py`, take the keys whose
  > subject this increment's touched symbols reach. A pin is predicted **red** if and only if the
  > increment changes the output of the renderer or widget that key names; every other pin is
  > predicted **green**.
  >
  > **MEASURED AT.** `20f86de`. **Cardinality deliberately not transcribed** — the pin dictionaries
  > are the authority and the test reads them.

  **`MASTER_RAIL_DIGESTS` (`tests/test_repair_depth.py:113`) is the subject here**, asserted at
  `:1056` and `:1071` and parametrized on `collapsed` — **the very attribute this LLR deletes**.
  Recorded loudly for one reason: **`MASTER_RAIL_DIGESTS` is named in NO artifact of this batch** —
  not in this document before this amendment, not in `PLAN.md`, not in the PDR. A shipped guard that
  no requirement names is a guard an implementer meets for the first time as a red test, at the
  gate, with no ruling in hand.
- **THE RE-CAPTURE RULE, AND IT IS A GATE FAILURE TO BREAK IT.** Only a digest whose subject's
  output this increment **actually changes** may be re-captured; each re-capture is done **one at a
  time, with its own recorded reason**. Re-capturing the dictionary wholesale is a **gate failure**,
  not a repair — it converts the repair batch's `C-53` false-failure arm into a rubber stamp, which
  is the one thing that guard exists to prevent. **A red pin is evidence; a re-captured pin is a
  claim.**
- **Acceptance criteria:** the deletion is **asserted**, not assumed — two owners of one truth is how
  the rail and the canvas start disagreeing about what is folded (Q-2's stated reason).
- **Regime note:** the ownership move is justified by lifetime, not style. `_apply_region_visibility`
  (`app.py:1172-1186`) auto-hides the rail below 118 columns (executed **M-4**), so fold must keep
  working while the widget that used to own it is not displayed. `AT-017` is that case.

##### LLR-N06.2.2 — folding a leaf is specified

- **Traceability:** HLR-N06.2
- **Statement:** If the operator folds a node with no descendants, then the system shall leave the
  painted canvas unchanged, shall not paint a pill, and shall paint a notification whose title reads
  `nada que plegar` and whose body reads `este nodo no tiene descendientes`.
- **Touched symbols:** `mapper/app.py::MapScreen` fold action handler.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_fold.py -k "folding_a_leaf"` *(provisional)* —
  navigate to a fixture leaf and press the real `z`.
- **Numeric pass threshold:** painted text identical before and after; **0** pills painted;
  **1** notification with the declared copy. The fixture leaves, derived from `fixtures/legacy.mmd`
  (**M-6**): `cont`, `pres`, `nom`, `alm`.
- **Reconciled against `01b-ux-decisions.md` DECISION 4 state E6.** The first draft specified a
  silent no-op; the ux lens requires the declaration, matching the precedent the product already
  sets — `next_gap` with nothing missing already toasts `cobertura completa` (01b, executed).
  Audit row §6.4 D-3.
- **Acceptance criteria:** without this LLR the natural implementation paints a pill reading `+0`,
  which declares a hidden count of zero and is worse than nothing.
- **The toast is a declared output.** It is `leaf_fold_notice` in §4.2 (`COMPONENT: map_screen`),
  added by amendment per `02b` C-8's second clause — *"declare `LLR-N06.2.2`'s new toast in §4"* —
  because a text sink that no contract row names is a sink the reverse census does not see.
- **Its coercion is governed by `LLR-N06.2.5`.** This toast's copy is a literal, so it is safe
  today; the rule that keeps it safe is stated once, below, as a class.

##### LLR-N06.2.5 — every toast that interpolates a value is coerced, gated by a derived census

> **RE-PARENTED to `HLR-COERCE` (§3.0) by `PDR-2026-08-26-ui-next-batch-02#D21` — `P2-B6`,
> §6.5 A-48.** The id, the statement and the thresholds are unchanged; only the parent and the
> owning increment move. **Owning increment: Inc-9** (§5.4).
>
> **Why the parent was wrong, on the two-limb criterion `#D21` seals — both limbs executed:**
> - **Limb 1** (descope test): descope US-N06 and **every** site in the census survives. Not one is
>   a fold toast; the census is `mapper/app.py` on paths unrelated to the canvas, plus a screen
>   US-N06 never touches. The child's subject is not deleted with its parent.
> - **Limb 2** (source-budget test): `HLR-N06.2` → US-N06 → **Inc-3**, whose declared source set is
>   `app.py`, `widgets/rail.py`, `views/layered.py`, `keymap.py` — **four of four, at budget**.
>   Satisfying this LLR requires editing `mapper/screens/factory.py`, which is a **fifth,
>   undeclared** source file in Inc-3 and a **collision with Inc-9**, which owns that file. **This is
>   an undeclared source-budget breach, not a stylistic smell** — the batch's only declared breach is
>   Inc-2's, and validator rule `V9` exists to catch undeclared ones.
>
> **The criterion discriminates rather than condemning — control executed.** Applied to a sibling
> under the same parent, `LLR-N06.2.3` (a branch name reaching the fold pill is coerced): descope
> US-N06 and there is no fold pill, so limb 1 passes; its touched symbols are `darkside.plain` and
> the pill construction in `views/layered.py`, both inside Inc-3's set, so limb 2 passes.
> **Correctly parented, and it stays.** A criterion that moved both would be a verdict.
>
> **`#D21` REMOVES a breach rather than creating one**, which is the strongest argument for the
> ruling: Inc-3 goes from an undeclared 5 to a declared 4, and Inc-9 gains the census at **zero**
> added files — its declared set already contains both `app.py` and `screens/factory.py`.
>
> **`LLR-N06.2.2`'s cross-reference at the end of the block above — *"Its coercion is governed by
> `LLR-N06.2.5`"* — STAYS, and is now a cross-section reference.** That is correct and it is the
> point: the fold toast is governed by the class, and **the class is not owned by the toast**.
>
> **Recorded honestly — one clause of `#D21`'s edit a-2 is NOT performed in pass 1.** Edit a-2 also
> asks that this block be **physically moved** out of §3.4 into §3.0. It is not moved. The parent,
> the increment and the ownership — the whole substance of the ruling — are applied here and in
> §3.0's `Owned LLRs` line, and the id is deliberately **not** renumbered to an `LLR-COERCE.*` form,
> because `LLR-N06.2.5` is cited by §5.2 (`TC-073`), by `02c`, and by `PLAN.md`, none of which this
> lane may edit. Relocating ~60 lines of a 5 000-line document to satisfy a presentational clause,
> in a fold whose two predecessors dropped conditions, is a risk with no requirement-side payoff.
> **This is a deliberate, recorded deviation, not an omission**; §6.5 A-48 carries it as an open
> ledger line so pass 2 can close or ratify it.

- **Traceability:** `HLR-COERCE` (§3.0), risk A-7, security condition **C-8** (`02b` S-09)
  *(~~`HLR-N06.2`~~ — superseded by `#D21`, above.)*
- **Statement:** Every `notify` call site in the product whose message argument is not a literal
  shall disable markup parsing and shall route every interpolated value through the design module's
  plain-text coercion; and the verification shall obtain the set of such call sites **by derivation
  from the tracked product sources at run time**.
- **THE PARKED FIGURE OF 13 EXECUTES FALSE, AND THE DEFECT HAS MOVED (§6.5 A-18).** `02b` S-09 reads
  *"thirteen `notify()` sites interpolate exception text with markup parsing on"*. That figure
  predates the repair batch. Re-derived at `d877784` in this amendment session by walking the AST of
  every `mapper/**/*.py` — **not** by grep, because a `notify(` call spans lines and a line-oriented
  count answers a different question:

  ```
  D1 total .notify( call sites                          : 30
  D2 sites with a NON-LITERAL first argument             : 19
  D3 of D2, markup NOT disabled                          :  0     <- the markup half is REPAIRED
  D4 of D2, first argument not routed through plain()    : 15     <- the coercion half is LIVE
       mapper/app.py:647   :661   :682   :687   :760
       mapper/app.py:1053  :1055  :1058  :1455  :1646  :1738
       mapper/screens/factory.py:423  :444  :468  :470
  ```

  **The markup half of S-09 is discharged by execution**: all 19 dynamic sites pass `markup=False`.
  The 10 sites that carry no `markup=` keyword at all every one have a **literal** first argument, so
  no file-derived text reaches them. **The coercion half is live and is larger than the parked
  figure**: 15 dynamic sites interpolate a value — an exception string, a map name, a path — without
  `plain()`, so a `U+202E` in a file name reaches the toast body intact even with markup off.
- **SCOPED AS A CLASS WITH A DERIVED CENSUS, NOT AS A LIST OF LINE NUMBERS — and this is the whole
  point of the condition.** The repair batch's own post-mortem records that **naming a defect class
  without landing the census cost six rediscoveries**. The 15 addresses above are **evidence that
  the class is non-empty**, not the specification. Every one of the parked S-09 addresses is stale;
  every one of these will be stale after Inc-3. The gate is the derivation.
- **Touched symbols:** the `notify` call sites the census returns; `mapper/darkside.py::plain`
  (`darkside.py:276`); the census module — `NEW — created in Phase 3`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_darkside.py -k "notify_sites_are_coerced"`
  *(provisional)* — parse every tracked `mapper/**/*.py` with `ast`, select `Call` nodes whose
  `func` is an `Attribute` named `notify` and whose first positional argument is not a `Constant`,
  and assert each disables markup and coerces.
- **Numeric pass threshold:** derived total `.notify(` site count `> 0` (guards a vacuous walk;
  executed **30**); of the sites with a non-literal first argument, those not disabling markup
  `== 0` (executed **0** — already green, asserted so it stays green); those not routing through
  `plain()` `== 0` (executed pre-state **15**). The census asserts its own input set is non-empty
  before evaluating any site, as `LLR-S06.3.1` does.
- **Named weaker variant (`M-N06.2.5-a`):** fix the 15 addresses listed above and assert against a
  hand-written list of those 15. Green on the day it lands, blind to the sixteenth site the next
  increment adds — which is the exact failure the repair batch's post-mortem priced at six
  rediscoveries. Reddened by nothing, which is why the derivation is the requirement and the list is
  not.
- **Named weaker variant (`M-N06.2.5-b`):** derive the census with `grep -c "\.notify("`. A
  line-oriented count returns 30 here **by coincidence** — every call's `.notify(` is on one line
  today — and silently miscounts the moment a call is reformatted, while telling you nothing about
  the first argument or the keywords. The AST walk is named in the verification for that reason.
- **Acceptance criteria:** `markup=False` without `plain()` stops Rich from *parsing* the string and
  does nothing about what the string *does to the terminal*. Both clauses are required, and the
  executed split above — markup half green, coercion half 15 sites red — is why they are stated as
  two separate thresholds rather than one.

##### LLR-N06.2.3 — a branch name reaching the canvas is coerced

- **Traceability:** HLR-N06.2, risk A-7
- **Statement:** The system shall coerce every branch title placed into a fold pill through the
  design module's plain-text coercion before it reaches the canvas.
- **Touched symbols:** `mapper/darkside.plain` (`mapper/darkside.py:276`, executed — its
  `_CONTROL_MAP` at `:272` maps every C0 byte except tab and newline to a replacement character);
  the pill construction in `mapper/views/layered.py` — `NEW — created in Phase 3`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_fold.py -k "pill_coerces_hostile_titles"`
  *(provisional)* — render a graph whose branch title carries Rich markup, a C0 control byte
  constructed from its code point at test time, and a right-to-left override.
- **Numeric pass threshold (C-4, §6.5 A-13):** measured **on the painted row**, never on the string
  handed to the sink — **0** occurrences of any code point in `COERCION_RANGES` (§3.0); **0** Rich
  markup tags interpreted; the rendered row length equals the canvas width for every hostile input;
  and the **split-at-width arm** passes — a branch title **balanced at source** (`U+202E` … `U+202C`)
  truncated at `card_w` leaves **0** unterminated overrides in the painted row.
  *(~~"0 control bytes in the output"~~ is superseded: `U+202E` is not a control byte, and it is the
  input this LLR drives.)*
  > **THE SPLIT-AT-WIDTH CLAUSE CANNOT DISCRIMINATE**, for the reason recorded at `LLR-COERCE.2`:
  > `darkside.plain` replaces rather than deletes, so it is index-preserving and the override is gone
  > by coercion regardless of the order. The **0** is real; it is not evidence about ordering.
  > Measured at `S-B(+C)`. The first clause of this same threshold — 0 occurrences of any
  > `COERCION_RANGES` point at the sink — is the one that carries the weight, and it is armed.
- **Acceptance criteria — the sink class is DERIVED and includes PRE-EXISTING sinks (C-7,
  §6.5 A-15).** ~~"every new text sink **this batch creates**"~~ is superseded. That wording
  re-encodes batch 1's own §2.1b failure into the requirement — a scope that stops at the new code's
  boundary while the identical defect ships beside it — which is why `02b` S-08 raised it as a
  blocking-within-increment condition rather than a note. **The scope is every file-derived string
  painted on a surface this batch touches, whether its sink is new or pre-existing**, and the set is
  fixed by a **derived census**, never by a hand-listed set of line numbers.
  - **Census shape.** For each touched surface, walk the tracked product sources and enumerate every
    expression that places a file-derived value into a painted renderable; assert each is routed
    through the coercion helper. The census **shall** assert its own input set is non-empty before
    evaluating any site, exactly as `LLR-S06.3.1` does.
  - **`layered._fit` is in scope, and it is why the census cannot be hand-listed.** Executed (§3.0):
    it coerces nothing, and it emits the card title (`layered.py:217`, `:280`), the doc line
    (`:237`), the meta row (`:247`), the diff chip (`:227`) and the removed-ghost row (`:266`).
  - **Still explicitly OUT of scope:** legacy `rich.markup.escape` sites on surfaces this batch does
    **not** touch (carry B-03). The scoping predicate is *"on a touched surface"*, and it is
    evaluated in code, not by reading this sentence.
- **Named weaker variant (`M-N06.2.3-a`):** route the pill's branch title through `plain()` and leave
  `layered._fit` alone. The pill is clean; the card title beside it on the same canvas still carries
  the override. Reddened by the derived census, not by this LLR's own fixture — which is the point of
  making the census the gate.
- **Byte-hygiene note:** the control byte in the fixture is **constructed from its code point at test
  time**, never spelled into the source. Batch 1 shipped a literal backspace byte this way and the
  resulting test passed on everything.

##### LLR-N06.2.4 — walking onto a hidden match opens its fold and says so

- **Traceability:** HLR-N06.2, HLR-N07.3
- **Statement:** When the search or lens walk advances the selection onto a node inside a folded
  branch, the system shall unfold that branch, shall paint the hint line naming the branch it opened,
  and shall not re-close that branch when the walk moves past it.
- **Touched symbols:** `mapper/app.py::MapScreen.folded`; the walk action handler in
  `mapper/app.py::MapScreen` — `NEW — created in Phase 3`.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_fold.py -k "walk_opens_a_folded_hit"`
  *(provisional)* — fold a branch containing a known match with the real `z`, submit a query, walk
  with the real walk chord, and read the selected id, the painted canvas and the hint line.
- **Numeric pass threshold — REWRITTEN; the parked oracle executes FALSE at every width
  (`UX2-C-04`, §6.5 A-66):**
  1. **`PRED-A` — the walk lands on the match, observed as data.** After the walk press, the selected
     id is a member of the **painted id set the renderer returns**, obtained the way `HLR-N06.3`'s
     `PRED-2` / `PRED-3` already obtain it. Not by searching the painted text for the id.
  2. **`PRED-B` — the operator can see it, observed as pixels.** The selected node's **title**, under
     the clipped-and-visible `_clip` image at that width, has a trace in the painted frame — the
     truncation-tolerant predicate `A-21` settled and `HLR-N06.3` already uses.
  3. **`PRED-C` — the branch stays open, observed on the SURFACE.** ~~After 1 further walk press~~
     **once the walk has moved OUT of the opened branch — asserted, not counted in presses** — the
     previously opened branch paints **no fold pill**. Read from the painted frame.
  4. The hint line names the opened branch, **subject to the width proviso below**.

- **~~"After 1 further walk press"~~ WAS MEASURED INSUFFICIENT AND IS REPLACED (`#D36` fold,
  2026-08-29, `NEW-2` of `increment-004b-code-review-confirmation.md`).** The press count is not the
  property; *leaving the branch* is. On the shipped fixture the one further press lands on the **next
  hit inside the same branch**, so a re-close implementation re-opens it on that very press and the
  predicate never sees the defect. Measured, both forms under the identical re-close mutant, in one
  process:

  ```
  under the re-close mutant     118x34    80x24
    single-press form (parked)  PASSED    PASSED     <- cannot fail on the defect it names
    walk-out form (shipped)     FAILED    FAILED     <- fails at "b's fold pill is painted again"
  ```

  **This threshold was known-defective with the evidence already in hand**, and it is amended here
  rather than left for the next increment to read: `Inc-5` building an arm from the parked wording
  would have built the weak one, and it would have been green. The Statement is unchanged — only the
  predicate that observes it.

- **WIDTH PROVISO on clause 4 — the announcement degrades, and that is declared rather than
  discovered (`NEW-3`).** `HintLine` **wraps** rather than clips, so a name painted onto a row that
  has left the frame is not painted at all; insisting on it costs the operator `esc limpiar`, the
  recovery route `#D38` newly promises. The shipped budget therefore drops the branch announcement
  below a floor. **Executed sweep, 25 widths from 40 to 200:** `esc limpiar` is present in the frame
  at **every** width; the announcement is painted at **69 columns and dropped at 68**. The narrowest
  **declared** regime is **80** — eleven columns above the threshold — so within every size this
  document declares, clause 4 is satisfied, and satisfied by a **gated** mechanism: suppressing the
  announcement unconditionally reddens its arm. **A `shall` the code knowingly does not satisfy at
  some inputs, recorded only as a risk note, is how an undeclared exception becomes an undiscovered
  one** — hence this proviso, with its measured threshold, in the requirement itself.

- **~~"the selected node's id appears in the painted canvas text"~~ IS FALSE AT EVERY WIDTH, AND IT
  WOULD HAVE FALSE-FAILED CORRECT WORK.** The canvas paints **titles**, never ids. Re-executed over
  the shipped fixture's eight ids:

  ```
  50x12   raw-ID trace present for 0/8
  80x24   raw-ID trace present for 0/8
  120x40  raw-ID trace present for 0/8
  ```

  **Zero of eight, at every swept width.** `AT-046` is the arm that exists to stop `AT-022` passing
  on a screen where the operator cannot see the selection — and as written **it fails on a perfect
  implementation**, at every terminal size, for a reason that has nothing to do with the behaviour.
  **`C-53` prices a false-fail as high as passing wrong work**, and this is the sharper half of that
  rule: a gate that cannot be passed gets weakened, and the weakening is what ships. This is
  `QA-B-02`'s root-title oracle **for the third time** — the identical mistake A-02 re-homed into
  `HLR-N06.3` and A-21 then settled with the clipped-image predicate. **The fix is to use the
  document's own already-settled oracle rather than to invent a fourth.**
- **~~"still absent from the folded set"~~ IS THE SECOND DEFECT ON THE SAME THRESHOLD, and it is the
  opposite failure.** `MapScreen.folded` is a **model attribute**. Reading it asserts what the
  application *believes*, so `AT-047` can pass green while the branch is painted **closed** — the
  state change is silent, which is the one thing US-N06 forbids. **`PRED-A` reads data and `PRED-C`
  reads the surface, deliberately**: one arm proves the walk arrived, the other proves the operator
  can see that it did, and neither substitutes for the other.
- **Named weaker variant (`M-N06.2.4-a`):** keep `PRED-A` and `PRED-C`, drop `PRED-B`. Both green on
  a renderer that opens the fold and paints the node **off-canvas**, because the id set says painted
  and the pill is gone. Reddened by the clipped-and-visible trace.
- **Named weaker variant (`M-N06.2.4-b`):** assert `PRED-C` against `MapScreen.folded` as parked.
  Green on an implementation that mutates the set and never repaints. Reddened by reading the pill.
- **Acceptance criteria — this is the requirement that stops `AT-022` being vacuous.** Without it,
  "the selection lands on the next matching node in tree order" **passes on a screen where the
  operator cannot see the selection**, because the node is inside a fold. Landing a cursor on an
  invisible node is a silent state change, which is the one thing US-N06 forbids.
- **Source:** `01b-ux-decisions.md` DECISION 5 step 3, which names this the largest gap in the
  design and settles all three of its sub-questions. Added at reconciliation; audit row §6.4 D-4.
- **Acceptance:** `AT-046`, `AT-047`

#### HLR-N06.3 — nothing is hidden without being declared, and the declaration reconciles

- **Traceability:** US-N06
- **Statement:** While any node of the loaded graph is not painted on the canvas, the system shall
  paint an indicator declaring the total number of unpainted nodes; and that declared total shall
  equal the number of graph nodes absent from the painted canvas.
- **Rationale (informative):** this is the story, stated as an identity rather than as a promise.
  Measured pre-state (**M-5**), **restated (`QA-N-04`, section 6.5 A-41):** 121 of 129 nodes had **no
  full-title trace**, indicator absent. The parked wording read *"121 nodes hidden (94 %)"*, which
  over-states: the metric counted full-title traces, so nodes that were **truncated but drawn** were
  counted as hidden -- the very error the Painted-trace oracle below exists to remove. The identity
  is what makes "nothing clips silently" falsifiable; the pre-state number is a trace count, not a
  hidden count.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_overflow.py -k "declared_total_equals_unpainted"`
  *(provisional)* — render at a declared Pilot size that forces overflow, parse the numeral out of
  the painted indicator, and compare it to `len(graph.nodes)` minus `painted_node_count` as the
  **Painted-trace oracle** below defines it.
- **THE HEADER WRAPS — any `AT` parsing a numeral shall join wrapped rows first (`QA-N-06`,
  §6.5 A-41).** Executed: at 100 x 30 the canvas header renders as **two rows**, the count numeral
  landing on one and the word `nodos` on the next, so a per-row regex either misses the numeral or
  binds it to the wrong label. The oracle joins the region-clipped rows before parsing.
- **Numeric pass threshold — THREE predicates, all three required (`QA-B-01`, §6.5 A-20):**
  1. **`PRED-1` reconciliation** — `declared_total == len(graph.nodes) - |declared_painted_set|`.
  2. **`PRED-2` soundness** — every id in `declared_painted_set` has a painted trace:
     `declared_painted_set ⊆ traced_set`.
  3. **`PRED-3` completeness** — every graph node with a painted trace is in the declared set:
     `traced_set ⊆ declared_painted_set`.

  `PRED-2 ∧ PRED-3` is set **equality** between the declared painted set and the traced set, which
  is what the story actually promises. All three hold over **four configurations** on the **named
  fixture** below, each declaring its Pilot size.
  4. **`PRED-4` legibility** — the declaration is painted in a token whose contrast against `GROUND`
     is `>= 4.5 : 1` at the guaranteed rung (`HLR-S06.2`), and which is **not equal to `GROUND`** at
     any rung the product can reach.

- **`PRED-4` EXISTS BECAUSE THE DECLARATION IS CURRENTLY PAINTED IN A TOKEN THE OPERATOR CANNOT READ
  (`UX2-C-08`, §6.5 A-68).** `01b` DECISION 3 assigns the declared-overflow line `V7` — and the
  minimap caption `V8` — to **`WORDMARK` `#3a3a3a`**. Measured against `GROUND #000000`:

  ```
  WORDMARK  truecolor 1.85 : 1     EIGHT_BIT (slot 237) 1.85 : 1
  MUT       truecolor 4.43 : 1     EIGHT_BIT (slot 242) 4.00 : 1
  WINDOWS rung: WORDMARK collapses into GROUND  ->  1.00 : 1, INVISIBLE
  ```

  **1.85 : 1 is roughly 40 % of the 4.5 : 1 minimum, at both rungs**, and on the `WINDOWS` rung the
  line is not merely dim but **absent**. **`V7` carries US-N06's entire promise** — it is the
  declaration that *"nothing is hidden without being declared"* resolves to on the screen. A promise
  painted at 1.85 : 1 is a promise the story does not keep.
- **THE PARKED ORACLE IS BLIND TO THIS, WHICH IS WHY IT IS A NEW PREDICATE AND NOT A NOTE.**
  `AT-015` and `AT-016` assert the declaration **is present in the painted text** — equally true at
  1.85 : 1 and at 8 : 1, and equally true when the glyph is painted in the background colour.
  `PRED-1` through `PRED-3` are all satisfiable on a frame in which the operator sees nothing.
  **Every one of the four predicates can be green while the story fails**, unless `PRED-4` is there.
- ~~**DISCHARGE — `V7` and `V8` move off `WORDMARK` to `MUT`.** `MUT` clears the floor at the
  guaranteed rung…~~ **STRUCK 2026-08-27 — `MUT` DOES NOT CLEAR THE FLOOR, AND THE MEASUREMENT
  SAYING SO WAS FOUR LINES ABOVE THE CLAUSE (`UX3-C-A`, ruled `PDR-addendum-3#D28`).**
  `:2127` prints `MUT` **`EIGHT_BIT (slot 242) 4.00 : 1`** at the guaranteed rung, against a floor of
  `>= 4.5 : 1`. **The discharge clause of `PRED-4` failed `PRED-4`.**
- **DISCHARGE (ruled) — `V7` and `V8` move off `WORDMARK` to **`INK`**; `WORDMARK` keeps `V4`.**
  **The floor stands and the token changes** — restating an accessibility floor downward to rescue a
  token choice is the floor-bends-to-the-implementation defect this batch keeps catching. Derived,
  not picked: of the tokens clearing `4.5 : 1` at the guaranteed rung, `ACCENT`, `ALERT` and `WARN`
  each hold a single declared job (`LLR-S06.3.3`, `LLR-S06.3.5`), leaving **`INK` the only free
  candidate**. It is one token change in `mapper/darkside.py`'s usage and **`Inc-1` owns that file**,
  so it costs no file budget.
- **THE GENERAL RULE THE MEASUREMENTS IMPLY (`#D28`), stated so this is not re-derived per seat:**
  **`MUT` is legal for READABLE, load-bearing text only on `GROUND`**, where it clears the floor
  (`4.43 : 1` truecolor). **Any `MUT`-on-`PANEL` readable-text seat escalates to `INK`** — `MUT` on
  `PANEL` measures **`3.57 : 1`**.
  **EXEMPT, explicitly, so the rule cannot be over-applied and kill the dim tier:** purely
  **decorative / non-load-bearing** marks — rules, lattice dots, ground texture — carry no floor.
  **`V4` (`territorio sin explorar`) stays on `WORDMARK` under this exemption**: barely-there is the
  *point* for unexplored territory, and moving it would make dust compete with content.
- **Named weaker variant (`M-N06.3-legibility`):** move `V7` to `INK` and leave `V8`. Green on
  `PRED-4` as quantified over the overflow declaration alone, and the minimap caption — the other
  half of "how much is not on screen" — stays at 1.85 : 1. Reddened by quantifying `PRED-4` over
  **every** token carrying a declaration role, derived from `01b` DECISION 3 rather than named here.
- **TWO PREDICATES ARE NOT ENOUGH — executed, and this corrects `QA-B-01`'s own prescribed remedy
  (§6.5 A-20).** The review prescribed exactly `PRED-1` and `PRED-2`. Re-executed in this amendment
  session on `legacy` at 40 x 12, where `alm` and `inv` are genuinely off-canvas:

  ```
  BASELINE legacy 40x12  N=8 declared=['cont','erp','fin','nom','pres','rrhh']
    truly off-canvas=['alm','inv']   indicator numeral=2
  mutation                                             P1     P2     P3
  ---------------------------------------------------------------------
  BASELINE (correct)                                 True   True   True
  MUT-1 deletion: declared set = empty                True   True  False
  MUT-3 weakening: declared omits ['cont','pres']     True   True  False
  MUT-4 over-declare: declared adds off-canvas 'alm'  True  False   True
  ```

  **`MUT-1`, the pure deletion, is GREEN on both prescribed predicates.** `PRED-1` holds because
  `8 == 8 - 0`; `PRED-2` holds **vacuously** — `all()` over an empty set is `True`. A renderer that
  declares *nothing* painted passes the batch's headline predicate, which is precisely the shipped
  pre-state. **`MUT-3`, the requested plausible weakening**, omits exactly the nodes a fold would
  hide, recomputes the indicator consistently from that same set, and is internally coherent — also
  green on both. `PRED-3` catches both and **costs nothing**: `traced_set` is already computed for
  `PRED-2`. The structural reason `PRED-1` cannot carry this weight: once the indicator is computed
  from the declared set, `PRED-1` is an identity between a value and itself, and its only real job
  is catching an off-by-one between compute and paint (`MUT-2`, correctly caught).
- **Priority:** high — it is the outcome the story exists for.
- **Acceptance:** `AT-015`, `AT-016`
- **THE FIXTURE IS NAMED, AND THE SEED MAP IS NOT VIABLE (§6.5 A-20).** `AT-015` and `AT-016` shall
  drive `fixtures/legacy` at these `(w, h, folded)` triples, so the AT cannot pass or fail on the
  implementer's choice of fixture:

  | Configuration | `(w, h, folded)` |
  |---|---|
  | nothing hidden | `(50, 12, ())` |
  | hidden by fold only | `(50, 12, ('erp',))` |
  | hidden by viewport only | `(30, 6, ())` |
  | hidden by both | `(30, 6, ('erp',))` |

  Executed: `legacy` hides at least one node at **31 of 56** swept sizes and reaches all four
  configurations. **The seed map hides a node at 0 of 56 sizes** and reaches only 2 of the 4
  (its sole foldable node is the root, which is a degenerate case, not the story's). Naming it would
  make `AT-015` unfalsifiable in its two most important arms.
- **Painted-trace oracle — normative, and this is the re-homed `QA-B-02` lesson (§6.5 A-02).**
  `QA-B-02` attacked the struck `LLR-S07.1.3`, whose oracle asserted a **raw title substring** in
  the painted canvas. That section is gone (§3.1, D16) but the defect it named is **still
  load-bearing here**, because `painted_node_count` is the same kind of trace. Executed at
  `d877784` in this amendment session:

  ```
  $ python -c "...LayeredRenderer().render(g, w=80, h=24)  # title 36 chars"
  full title present: False
  ['▐ Un titulo bastante lar…                    ']
  ```

  `mapper/views/layered.py::_fit` (`:38`) clips through `_clip` and the card title is emitted at
  `:217` and `:280` at `card_w - 3`, where `card_w = min(26, max(14, widest))` (`:162`) and shrinks
  further when the leaves do not fit (`:164-165`). **A raw-title trace is therefore FALSE on any
  title longer than the card**, and a raw-**id** trace is false always, because the canvas paints
  titles and never ids.

  **~~The oracle shall use a truncation-tolerant prefix of the title, its first `k` display
  cells.~~ SUPERSEDED — a prefix of ANY length is not a sound predicate (§6.5 A-21).** Swept over
  the 31 overflowing sizes, negative arm **129 unpainted node-observations**, re-executed here:

  ```
    L= 1  false-neg=  0  false-pos= 83      <- single letters collide with chips and the header
    L= 2  false-neg=  0  false-pos=  0      <- the ONLY discriminating length
    L= 3  false-neg= 12  false-pos=  0
    L= 5  false-neg= 12  false-pos=  0
    L= 8  false-neg= 69  false-pos=  0      <- the shape QA-B-02 prescribed
    L=18  false-neg= 77  false-pos=  0
  ```

  The window of validity is exactly `{2}` — failure on **both** sides of a one-value window is
  fixture-fitting, not an oracle. And the *"declared prefix of `>= 8` characters"* that `QA-B-02`
  offered as the remedy shape **false-fails 69 times**.

  **THE NORMATIVE PREDICATE — and its exact form matters, because the natural reading of it is
  wrong (§6.5 A-21).** A node counts as painted when **the portion of its clipped title image that
  falls inside the canvas width** occurs in the region-clipped painted rows. That is
  `_clip(plain(title), card_w - 3)` **restricted to the columns `0 <= cx + 2 + j < w - 2`**, with
  `card_w` and `cx` taken from the renderer's own geometry at run time and never typed. Executed,
  the distinction is not cosmetic:

  ```
  P-A1  _clip(title, card_w-3)                    false-neg= 20  false-pos= 0
  P-A2  that image restricted to visible columns  false-neg=  0  false-pos= 0
  ```

  **Naming the predicate as "the `_clip` image" alone reintroduces 20 false negatives** — the
  20 observations are nodes whose card is partly past the right edge, where the full image is never
  painted but the node plainly is. The horizontal restriction is part of the predicate, not an
  implementation detail. The screen-level clip remains `_rows_in(screen, canvas.region)`
  (`tests/test_repair_layout.py:74`); `AT-015` and `AT-016` are `test (pilot)` and read the
  composited frame, **not** `render().plain` — the sweep above pins the arithmetic, not the surface.

  **Named weaker variant that this reddens (`M-N06.3-a`):** a trace that case-folds and matches raw
  ids. Executed: on `fixtures/legacy_nodos.yml` every id is an abbreviation of its own title
  (`fin`→`Finanzas`, `nom`→`Nomina`), so a case-insensitive id trace returns **8 of 8** at `w >= 80`
  — the right answer by fixture luck — **7 of 8 at `w = 60`**, where the luck runs out under
  truncation, and **0 of 3** on a seeded map. The case-**sensitive** id reading returns **0 of 8**
  at every width, so it declares `8` unconditionally: a constant, not a measurement.

  **Second named weaker variant (`M-N06.3-b`):** compute `painted_node_count` from the renderer's
  internal position map (`_tree_layout`'s keys) instead of from the painted rows. That survives an
  identity test and is exactly the vacuity the story exists to prevent — a node the renderer
  *placed* and the compositor *clipped* is not painted. The oracle reads the frame, never the
  layout.

##### LLR-N06.3.1 — the two hiding causes are counted as one set, not summed

- **Traceability:** HLR-N06.3
- **Statement:** The system shall compute the unpainted set as the graph's node set minus the set of
  nodes the current render painted, and shall not compute it by adding a fold count to a viewport
  count.
- **Touched symbols:** `mapper/app.py::MapScreen` — an overflow computation helper,
  `NEW — created in Phase 3`; it consumes `MapScreen.folded` and the renderer's declared painted set.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_overflow.py -k "unpainted_is_a_set_difference"`
  *(provisional)* — a case where a folded branch is **also** off-screen, so the two causes overlap.
- **Numeric pass threshold:** on the overlap case, the computed total equals the set-difference
  cardinality and is strictly **less** than the naive sum of the two counts.
- **Acceptance criteria:** the overlap case is the whole point. Summing two causes double-counts
  every node that is both folded and off-screen, and the indicator then declares more hidden nodes
  than the graph contains — a number that cannot be right and that no non-overlapping test can catch.

##### LLR-N06.3.2 — the pills reconcile with the declared total

- **Traceability:** HLR-N06.3
- **Statement:** While at least one branch is folded and no node is hidden by the viewport, the sum
  of the numerals painted on the fold pills shall equal the declared unpainted total.
- **Touched symbols:** none new — this LLR is an identity between two things HLR-N06.2 and HLR-N06.3
  each already produce. It is stated separately because it is the story's own worked example
  (§2.6 S-1: *"the declared total reconciles with the pills (23 + 18 = 41)"*).
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_overflow.py -k "pills_reconcile_with_total"`
  *(provisional)* — sum the numerals parsed from the **painted** pills and compare to the parsed
  indicator total.
- **Numeric pass threshold:** exact equality over the fixture's four fold configurations. Executed
  arithmetic (**M-6**), `fixtures/legacy_nodos.yml`, 8 nodes: `{} -> 0 = 0`; `{fin} -> 2 = 2`;
  `{fin,rrhh} -> 3 = 3`; `{fin,rrhh,inv} -> 4 = 4`. **And, on the `anidado` fixture below,
  `naive_sum == 6` while `painted_sum == 4`**, with the correct rule equal to the true hidden set.
- **THE NEGATIVE CONTROL IS NO LONGER OWED — the fixture exists and is specified here normatively
  (`QA-B-05` DISCHARGED, §6.5 A-22).** *"Owed at Phase 3"* was not a discharge; `02a` was right. The
  fixture is now built, written through `MapStore.save` and reloaded through `MapStore.load`, so it
  exercises the real load path and needs no new fixture machinery. **Inc-3 shall not open without
  it.**

  ```
  fixture `anidado` — 7 nodes, MAX DEPTH 3
      raiz[Plataforma] --> ops[Operaciones]
      raiz[Plataforma] --> fin[Finanzas]
      ops[Operaciones] --> log[Logistica]
      ops[Operaciones] --> comp[Compras]
      log[Logistica]   --> alm[Almacenes]
      log[Logistica]   --> flo[Flota]

  FOLD = {'ops','log'}          (log is nested INSIDE folded ops)
    naive_sum   = 6   contributions: log->['alm','flo'] ; ops->['alm','comp','flo','log']
    painted_sum = 4   painted pills: ['ops']
    true hidden union (the LLR-N06.3.1 set difference) = ['alm','comp','flo','log']  -> 4
    naive_sum != painted_sum  ->  6 != 4
    painted_sum == |hidden union|  ->  4 == 4
    nodes the naive rule DOUBLE-COUNTS: ['alm','flo']   (inflation = 2)
  ```

  Required properties, all met: depth `>= 3`; an inner folded branch nested inside another fold
  (`log`, whose parent `ops` is folded); that inner branch has `>= 2` descendants (`alm`, `flo`);
  **the two rules disagree**; and the correct rule equals the true hidden set, which is what ties
  this LLR to `LLR-N06.3.1`.
- **The shipped fixture is PROVABLY unfalsifiable here, not merely likely to be.** `02a` argued it
  structurally (max depth 2, zero nestable candidates with descendants). Executed exhaustively over
  **all 7 non-empty fold configurations** of `legacy`: **0** where `naive != painted`. Parked `M-6`'s
  three quoted rows reproduce exactly as configurations 1, 5 and 7. An acceptance that ran only on
  `legacy` could not fail, whatever the implementation did.
- **Declared gap, carried to `TC-032`.** The fold input has **no handler today** — `render()` takes
  no `folded` argument — so the transcript above is set arithmetic over `(graph, folded)`, which is
  what this LLR specifies. It becomes surface-reachable only once Inc-3 ships the fold mechanism,
  and **`TC-032` shall re-run this transcript through the Pilot at that point**. Recorded rather
  than left implicit, because "the arithmetic was proved" is not "the screen does it".
- **Acceptance criteria — and the trap this avoids:** the sum is taken over **painted** pills, not
  over the `folded` set. A pill for a branch nested inside another folded branch is not painted, and
  summing the `folded` set would double-count its descendants — measured above as exactly `alm` and
  `flo`, inflation 2.

##### LLR-N06.3.3 — the zero case is specified

- **Traceability:** HLR-N06.3
- **Statement:** While every node of the loaded graph is painted, the system shall not paint an
  overflow indicator.
- **Touched symbols:** the overflow indicator construction in `mapper/views/layered.py` —
  `NEW — created in Phase 3`.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_overflow.py -k "no_indicator_when_nothing_hidden"`
  *(provisional)* — render the 6-node graph of **M-1** at 140 x 45, where the canvas is 80 columns
  and everything fits.
- **Numeric pass threshold:** **0** occurrences of the indicator's leading token in the painted text.
- **Acceptance criteria:** an indicator permanently reading zero trains the operator to ignore it,
  which is the same failure as not having one.

---

##### LLR-N06.3.4 — the number outline shows matches what the operator cannot see

> **CORRECTED BY `02n` (qa-reviewer, 2026-09-10), THEN RE-FRAMED BY COORDINATOR RULING.** The
> thresholds are the reviewer's wording, transcribed. The implementer drafted the original row AND
> would have written the code satisfying it; it was reviewed before the increment opened precisely so
> the criteria and the work would not be argued by one voice at one table. **`02n` declined to ratify
> past a framing question rather than hide it**, and that question is settled here: `PHYS-1`/`PHYS-2`
> are a rendering-correctness property of one module, strong as regression but pressing a claim the
> operator cannot state. They are **demoted to a pinned pilot arm**. Acceptance keeps the claim the
> operator *can* state — *the number it shows me matches what I cannot see* — which is this batch's
> law of measuring what the operator reads.

- **Traceability:** HLR-N06.3
- **Origin:** `02m` §7.1, re-measured through the live screen by `02n`.
- **Statement:** While `OutlineRenderer` renders into `#map-canvas`, the system shall emit no line the
  canvas region cannot display, shall emit as many lines as it can display, and shall declare as
  hidden every node whose title is not painted as a result. **The unit of "can display" is
  `canvas.region.height` physical rows at `canvas.region.width` — not `_canvas_size()`'s `h`, which is
  the renderer's row BUDGET and is smaller** (measured at a `35x14` terminal: `region = 35x3`, `h = 2`).
- **Touched symbols:** the `lines[:h]` cut at `mapper/views/outline.py:161`, and the new module-level
  `painted_ids` in `mapper/views/outline.py` — `NEW — created in Phase 3`.
- **Validation:** `test (pilot)`
- **Executed verification (ACCEPTANCE):** `pytest tests/test_overflow.py -k "at056"` — one arm, **named
  normatively**: `test_at056_outline_declares_what_the_cut_hid` (`PHYS-3`, `PHYS-4`), parametrised over
  the driven table below. **The node name is part of this requirement, not a style preference:** `C-18`
  needs the `AT id → node` edge, and this batch already carries `AT-005` and `AT-006` with no node on
  disk and therefore no way to verify them. An arm asserting these clauses under a different name
  **does not discharge `AT-056`**. The arm drives `App.run_test(size=...)`, pushes `MapScreen("legacy")`,
  presses the real `o` chord, and reads the **composited frame** clipped to the widget region with
  `_rows_in` — never `render().plain`, never `painted_ids(...)`.
- **Acceptance threshold — TWO clauses, both required, both read from the composited frame:**
  1. **`PHYS-3` — the declaration follows the cut, against a frame-derived oracle.**
     `declared_hidden == |{ n in graph.nodes : n's painted trace is absent from the region-clipped
     frame }|`. **Outline's painted trace, stated here and not inherited (`02m` §7.3):** the node's
     title as `render` emits it, whitespace-collapsed, sought in the whitespace-collapsed join of the
     region rows. Outline paints titles **unclipped and word-wraps** rather than truncating, so a title
     survives a wrap whole — measured on `legacy` over 8 widths (`w = 20 … 32`), the per-row read and
     the joined read agree **8 of 8**. `HLR-N06.3`'s `_clip(title, card_w - 3)` predicate is
     **`layered`'s card geometry and does not apply here**: outline has no `card_w`. The hidden set
     shall be derived from the frame and **never** from `painted_ids(...)` nor from
     `len(graph.nodes) - len(painted)` (`C-31`).
  2. **`PHYS-4` — the fixture is non-degenerate, asserted BEFORE the equality.** At each driven
     clipping size, `1 <= declared_hidden < len(graph.nodes)` is asserted first, so `PHYS-3` cannot be
     satisfied by `0 == 0` (`C-55`) or by `N == N`. At the zero control the assertion is inverted and
     explicit: `declared_hidden == 0` **and** no overflow token, per `LLR-N06.3.3`.
- **Pinned pilot regression — NOT acceptance, and pinned here so it cannot be dropped:**
  `test_outline_cuts_at_the_rows_the_canvas_shows` (`tests/test_overflow.py`), same driven table.
  1. **`PHYS-1` — nothing is emitted that the canvas cannot show.** Every logical line
     `OutlineRenderer.render` returns is present in the region-clipped frame, compared on
     whitespace-collapsed text **joined across wrapped rows**. **Zero** emitted-but-unpainted lines at
     every driven clipping size.
  2. **`PHYS-2` — the cut is MAXIMAL, not merely safe.** The number of logical lines emitted is the
     largest `k` such that those `k` lines, wrapped at the **measured** `canvas.region.width`, occupy
     `<= canvas.region.height` physical rows; asserted by re-wrapping `k` and `k + 1` and showing `k`
     fits and `k + 1` does not — or that `k` is the whole outline. Widths and heights are read from the
     region at run time and **never typed**. **This clause exists because `lines[:0]` passes every
     other clause in this row** — a renderer painting nothing satisfies `PHYS-1` trivially and `PHYS-3`
     by declaring all `N` hidden against a frame where all `N` are absent. That is `MUT-1` of
     `HLR-N06.3`'s own mutation table, one renderer over. `PHYS-2` is the only clause it fails.
- **Driven size set — `fixtures/legacy` AND `fixtures/anidado`, outline mode, TERMINAL sizes. BOTH
  fixtures are normative: an arm on another map neither passes nor fails `AT-056`.**

  > **WIDENED from `legacy` alone (coordinator ruling 2026-09-10).** `02n` made `legacy` normative and
  > **was correct on the evidence it had**. The widening cites evidence `02n` could not have seen: with
  > the settle fix landed, a 144-combination sweep found **nine** cases where a node's title is held by
  > the canvas and **absent from the composited frame** — `Logistica` at `(30,16)`, `Flota` at
  > `(24,20)`, `Finanzas` at `(24,24)`, `(30,20)`, `(32,20)`, `(34,20)`, `(35,20)`, `Compras` at
  > `(28,20)` and `(30,20)` — **all of them on `anidado`, none on `legacy`**. On that evidence the
  > single-fixture set was blind to the defect this acceptance exists to forbid. Measured at
  > `anidado (30,16)`: the widget holds 4 logical lines needing 7 physical rows at region width 30
  > into a region of 5, and the fourth line reaches no cell of the frame.
  >
  > Ratified without a qa round-trip under **control 13**: an author may STRENGTHEN an acceptance
  > criterion against himself on measured evidence; only weakening it, or drafting criteria he can
  > satisfy, requires the independent pass. The qa-reviewer's `Inc-CONFIRM` pickup may revisit this.

  | terminal | region | `_canvas_size()` | role | measured 2026-09-10, pre-fix |
  |---|---|---|---|---|
  | `(30, 16)` | `30x5` | `30x4` | clipping | `    - Contabilidad` emitted, **absent from the frame**, region row 4 blank; 6 of 8 hidden |
  | `(32, 16)` | `32x5` | `32x4` | clipping | same loss; **already driven by this batch** (`tests/test_overflow.py:567`) |
  | `(24, 20)` | `24x8` | `24x6` | clipping | `  - RRHH  2 nodos` emitted, **absent from the frame** — a different logical index, so an off-by-one repair cannot pass all three |
  | `(50, 16)` | `50x5` | `50x4` | **negative control** | nothing lost; **5 of 8 still hidden** — a fix that clips everywhere fails here |
  | `(80, 24)` | `80x16` | `80x15` | **negative control** | nothing lost; **0 hidden** — `LLR-N06.3.3`'s zero form |

- **`35x14` IS STRUCK AS THE DRIVEN SIZE (`02n`, 2026-09-10).** Re-measured through the live screen:
  `region = 35x3`, `_canvas_size()` `35x2`, outline emits 2 logical lines occupying 3 physical rows,
  and **the frame shows all three**. **Nothing is lost at `35x14`.** The original `CLIPPED: 3 rows
  into 2` verdict compared physical rows against `_canvas_size()`'s `h` — the renderer's row BUDGET —
  rather than `region.height = 3`, the rows the canvas DISPLAYS. **That is `02j`'s unit rule one level
  in, committed inside the correction of `02m`'s version of the same error.** Reachability re-measured
  frame-side over a 135-size sweep: **14 of 135 on `legacy`, 15 of 135 on `anidado`**, every one at
  `w` in `{24, 28, 30, 32, 34}` — narrower than the size the original row drove.
- **Named weaker variant this reddens (`M-N06.3.4-a`):** keep the current mechanism and only add the
  declaration. Green on a frame-side `PHYS-1` at `35x14` and **red at `(30,16)`, `(32,16)`, `(24,20)`**.
- **Second named weaker variant (`M-N06.3.4-b`):** cut conservatively — `lines[:h-1]` or `lines[:0]`.
  Green on `PHYS-1` and `PHYS-3` at every size, **red on `PHYS-2` everywhere**, and red at `(50,16)`.
- **Open question carried into `Inc-B55a`'s pre-gate (`02n` §7.1):** at `(30,16)` outline emits 4
  logical lines needing 5 physical rows, `region.height` is 5, and the arithmetic FITS — yet the 4th
  line is absent and region row 4 is blank. **A second mechanism is in play beyond the `lines[:h]`
  cut.** A correct cut may therefore still leave `PHYS-1` red. Diagnosed read-only at the pre-gate,
  before the fix is designed — coordinator ruling 2026-09-10.
- **AMENDED AT `S-B(+C)` — OUTLINE'S TWO COST CAPS CHANGE WHAT `AT-056`/`AT-057` OBSERVE, AND THAT
  WAS RULED RATHER THAN ABSORBED** (coordinator ruling 2026-09-11; **wording ratified at
  `S-B(+C)`'s own full-protocol gate**, alongside `LLR-N06.3.5`'s floor exception):
  - **What changed.** `outline._indent` was `"  " * level`, unbounded and quadratic in depth, and a
    ficha title reached the row unclipped. Both are now bounded by **geometry** — half the render
    width for the indent, one frame (`w * h`) for the row — never by a constant (`B-61`).
  - **Why this touches an acceptance test at all.** `_fit` prices rows **physically**, so a shorter
    row occupies fewer physical rows, `_fit` **keeps more of them**, and the declared hidden count
    moves with the picture. These caps are therefore **not cost-only**, and the ruling took that
    deliberately rather than letting it arrive as a side effect.
  - **Measured before the ruling** (`C:\Users\<operator>\clde\cost_pregate.py`): at depth 4000 the widest
    row was **8,029 cells** into a 118-cell canvas and the walk **built 15,996,000 indent
    characters** against 468,460 capped (**34.1×**); `MAX_RENDER_NODES = 12000` puts the worst
    admissible chain at **~144 million**. A 400,000-character title produced a **400,004-cell row**
    and **3,390 physical rows** before `_fit` dropped it. After: **102 cells** and **4,016 cells**.
  - **The licence carries a condition, and the condition is armed.** A capped form must **declare its
    capping in the frame**: a clipped title uses the existing ellipsis idiom (`layered._clip` — one
    grammar, and the helper that also **coerces** the file-derived title), and
    a compressed indent **carries the true depth** beside its marker, so a deep chain reads as deep
    and not as shallow. **What the operator sees may compress; what it asserts stays true** —
    `PHYS-3`'s spirit.
    > **A CLAIM RETRACTED HERE.** This sentence first read *"the module where `LLR-COERCE.2`'s
    > coerce-then-truncate ordering already lives, so routing through it fixes the ordering as well as
    > the bound."* `S-B(+C)`'s **security review refuted the mechanism**: `_CONTROL_MAP` maps all 235
    > banned code points to exactly one `U+FFFD` each, so `plain` is length- and index-preserving and
    > `truncate(plain(s)) == plain(truncate(s))` **identically** — 20,000 fuzzed hostile pairs, zero
    > differences, and a mutant running the forbidden order stayed green on all 1058 arms. There is
    > never an override left to strand, because `plain` replaced it. The outcome was right and the
    > reason was wrong; the load-bearing property is simply that **outline's title path is coerced at
    > all**, which is now pinned rather than asserted.
  - **What `tests/test_outline_caps.py` actually pins, stated precisely because the first version of
    this sentence overclaimed and `S-B(+C)`'s code review fired both halves:**
    - *"derived, never a constant"* is pinned **for both caps** by driving **three geometries** —
      `(118,34)`, `(40,20)`, `(24,10)` — and asserting the **indent run** against `w // 2` **and the
      widest row against `w * h`** at each. Fired: with one geometry driven, replacing both
      derivations with constants equal to their 118-wide values left the **entire default lane green
      at 1051 passed**, while `chain(200)` under that mutant built a **96-cell row into a 24-cell
      canvas**. That is this batch's own **control 20**, which the sibling module quotes verbatim and
      this one had not inherited.
      > **AND THE FIRST FIX APPLIED IT TO ONE SIBLING ONLY**, which the confirmation pass caught: the
      > sweep went to the indent arm and the row-cap arm stayed at one frame, so `row_cap = 4012`
      > **survived the entire default lane at 1059 passed** while building a **4,016-cell row into a
      > 240-cell canvas** — a **16.7×** overrun at `(24,10)`. Applying a control to one of two
      > siblings has applied it to neither. Re-fired after the fix, each derivation replaced by its
      > 118×34 constant reddens **its own arms and only its own** — row-cap **4 arms** (4 failed /
      > 1059 passed in the full lane), indent **6 arms** — so neither pin masks the other.
    - *"carries the true depth"* is pinned by asserting the level **adjacent to its glyph**
      (`f"{DEPTH_MARK}{level}"`) over fixtures whose titles **cannot contain the level**. Fired: with
      the old oracle (`str(depth-1) in leaf`) over titles reading `nodo {i}`, a marker reporting
      `level // 10` — **lying about depth by 10×** — passed all ten arms, because the *title*
      satisfied the assertion.
    - A **control** asserts the caps do **not** fire on an ordinary map, and a further arm pins the
      caps' own premise: `views/outline.py` performs **zero** `pan_x`/`pan_y` attribute reads,
      checked by **AST rather than text** because the module's docstrings discuss pan in prose.
  - **Capping is safe from pan, checked not assumed:** `views/outline.py` contains **zero** `pan_x` /
    `pan_y` references, so cells past the canvas width are unreachable in this view. `rail.py`'s
    licence to cap came from its fixed width and absent pan; such a licence does not transfer by
    resemblance.
- **Acceptance:** `AT-056` · **Test case:** `TC-089`

##### LLR-N06.3.5 — both declaring surfaces speak, agree, and are right

> **REJECTED AS FIRST DRAFTED, REPLACED BY `02n` (qa-reviewer, 2026-09-10).** The original threshold
> — *"equal counts · zero disagreements"* — was **GREEN on the shipped pre-state**: measured at
> `(35,14)` on `legacy` in outline, 7 of 8 nodes hidden and **both surfaces silent**, so it was
> satisfied by universal silence before a line of code existed (`C-55`).

- **Traceability:** HLR-N06.3
- **Origin:** `02m` §7.2.
- **Statement:** While a renderer hides nodes, the system shall declare the hidden count on **both**
  declaring surfaces — the renderer's own header token and the screen's strip — and the two shall
  report the same number, and that number shall be correct. **Silence on both surfaces is not
  agreement:** `LLR-N06.3.3` makes silence mean *nothing is hidden*, so two silent surfaces over a
  frame that hides nodes are two surfaces agreeing on a falsehood.
- **THE EMPTY-FRAME FLOOR EXCEPTION** (amended `S-B(+C)`, coordinator ruling 2026-09-11; **wording
  ratified at this increment's own full-protocol gate**, per the spirit of `C-13` — the ruling set
  the direction, the gate ratifies the text): **when the declaring header cannot fit without evicting
  the last content row**, the renderer's header surface may be silent, **provided the strip is
  present in the same composited frame and declares the correct count.** That proviso is the
  exception's load-bearing condition, not a description of it: if the strip is ever absent or wrong
  at such a frame, the exception **lapses** and the clause above applies unamended.
  - **Why this is not the falsehood the clause forbids.** Agreement's purpose is that the operator
    learns the truth from *either* surface. At the floor, forcing the canvas to declare would spend
    the last content row to inform something **already informed one row below** — the shape
    `H1`-refined forbids (*spend content and inform nothing new*). This amends `LLR-N06.3.5`; it does
    not reopen `H1`.
  - **The trigger is DERIVED, never a list of sizes:** it is the geometric condition above. A
    hand-enumerated size list would silently stop matching the day a layout changed.
  - **Measured before amending**, on the tree with defect 2 fixed
    (`C:\Users\<operator>\clde\agree_sweep.py`): **9 of 90 sizes on `legacy` and 9 of 90 on `anidado` —
    eighteen in all**, every one the same shape, canvas silent and **strip correct**. Confined to
    widths 24–34 at heights 10 and 12, plus `(24,14)`. The prior frame-side figures (14/135, 15/135)
    were taken against a row budget defect 2 replaced, and are superseded.
  - **The code already stated this case**, and the amendment follows it rather than leading it:
    `outline.py::_fit_declared` — *"never return an EMPTY frame… Fall back to the header the frame
    CAN hold; the strip still declares."*
  - **Armed:** `tests/test_agree_floor.py` selects floor frames by the **geometric trigger itself** —
    `outline.floor_reached(rows, w, h)`, the renderer's own predicate, single-sourced with
    `_fit_declared` rather than transcribed — and asserts the proviso at each, with a non-vacuity
    guard so the arm cannot pass by never reaching the floor. Its companion asserts the **unamended**
    clause still governs every frame the predicate says is *not* at the floor, so the exception
    cannot silently spread.
    > **THIS SENTENCE WAS FALSE WHEN FIRST WRITTEN, and `S-B(+C)`'s code review caught it.** The arm
    > originally selected frames by *"the canvas said nothing"* — the floor's **consequence**, not the
    > floor. Fired: widening `_fit_declared`'s fallback **beyond** the empty-frame floor left the arm
    > green at 4 passed while the exempted set grew **9 → 17** on `legacy` and **9 → 14** on
    > `anidado`, so the exception could not lapse in the one direction that matters. Corrected, the
    > same mutant is **KILLED**.
  - **RE-MEASURED after `S-B(+C)`'s cost caps landed**, because those caps move the row budget and a
    stale figure in an amendment is the defect this batch keeps naming: **still 9 of 90 on each
    fixture, the same sizes, the same shape.** It did not move, and the reason is informative rather
    than reassuring — `legacy` and `anidado` are **shallow with short titles**, so neither cap
    engages for them. A deep or wide map **would** shift this set, which is exactly why the arm
    derives its floor frames instead of listing them.
- **Touched symbols:** the header token construction in `mapper/views/outline.py` and
  `mapper/views/radial.py` — `NEW — created in Phase 3` — reconciled by `_declare_after_layout`
  (`mapper/app.py:1609`), which exists because the two surfaces must agree (`B-56`, `B-60`).
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_overflow.py -k "at057"` — two arms, **named
  normatively** (`C-18`, and the `AT-005` / `AT-006` precedent):
  `test_at057_both_surfaces_declare_when_a_view_hides` (`AGREE-1`) and
  `test_at057_both_surfaces_report_the_same_correct_number` (`AGREE-2`, `AGREE-3`). Both read the
  composited frame with `_rows_in`, over `#map-canvas`'s region for the header surface and the search
  count region for the strip.
- **Numeric pass threshold — THREE clauses, all required:**
  1. **`AGREE-1` — both surfaces SPEAK when something is hidden.** At every driven size whose
     frame-derived hidden count is `>= 1`, the overflow token is **present in the canvas-header rows
     AND in the strip rows**. **This is the clause the shipped pre-state fails, and without it the row
     is green today.** Measured 2026-09-10 on `legacy` in outline at `(35,14)`, `(30,16)`, `(32,16)`,
     `(80,24)`: token absent from **both** surfaces at all four, `_unpainted_ids()` returning `None` at
     all four (`app.py:1596` short-circuits every view that is not `layered`) — while `(35,14)` hides
     **7 of 8**.
  2. **`AGREE-2` — the two numerals are equal.** The integer parsed after the token in the canvas
     header equals the integer parsed after the token in the strip. **Rows are joined before parsing** —
     the header wraps, and a per-row regex either misses the numeral or binds it to the wrong label
     (`QA-N-06`).
  3. **`AGREE-3` — both numerals are RIGHT, not merely equal.** Each equals
     `len(graph.nodes) - |painted set read from the frame|` under the view's own stated painted
     predicate (`LLR-N06.3.4`'s `PHYS-3` for outline; radial's is owed in its own row at `Inc-B55b`).
     Two surfaces fed from one `_declare_after_layout` computation agree **by construction**; equality
     alone is green when both are equally wrong.
- **Quantifier, stated so it cannot drift:** *"every view that declares"* is, at `Inc-B55a`'s gate,
  `{layered, outline}`; `radial` joins at `Inc-B55b`. The arm's parametrisation shall be **derived at
  run time** from `painted_ids_exporters()` rather than hand-listed, so a view gaining a declaration
  without gaining an arm goes red — the tripwire idiom `test_a98_*` already uses.
- **Driven size set — `fixtures/legacy`, per declaring view, TERMINAL sizes:**

  | terminal | role | measured 2026-09-10, outline, pre-fix |
  |---|---|---|
  | `(35, 14)` | hidden — live | **7 of 8 hidden; both surfaces silent** |
  | `(30, 16)` | hidden — live | 6 of 8 hidden; both surfaces silent |
  | `(80, 24)` | **negative control** | **0 hidden**; both surfaces correctly silent (`LLR-N06.3.3`) |

  **`(80,24)` is RETAINED BUT RELABELLED.** On `legacy` in outline it hides nothing, so as a positive
  arm it measures nothing. It earns its place only as the zero control, and only because `AGREE-1` is
  conditioned on the frame-derived hidden count rather than asserted unconditionally.
- **Named weaker variant this reddens (`M-N06.3.5-a`):** wire the **strip** through `_unpainted_ids`
  for outline and leave the canvas header alone. Green on `AGREE-2` only if absence is read as zero —
  exactly the `B-60` misreading — and **red on `AGREE-1`**.
- **Acceptance:** `AT-057` · **Test case:** `TC-090`

##### LLR-N06.3.7 — radial declares what the canvas lost, under its OWN painted predicate

- **Traceability:** HLR-N06.3
- **Origin:** `B-55`'s radial vector; construction constrained by `M-N06.3-b` and `02m` §7.3.
- **Statement:** While `RadialRenderer` hides nodes, the system shall declare them on both declaring
  surfaces, and the declared set shall equal the set the frame does not show under **radial's own**
  painted predicate.
- **Radial's painted predicate, STATED HERE AND NOT BORROWED:** a node is painted when it still owns
  **every cell of its title image** after the canvas's last-write-wins replay. The image is
  `plain(title)[:18]` — radial **truncates** — so outline's full-title read does not transfer
  (measured: 0 of 8 traced at five sizes where the frame plainly shows pills), and layered's does not
  either, because it anchors on card columns radial has no equivalent of.
- **The construction is a CELL-OWNERSHIP REPLAY, not a filter over placement.** `Canvas.put` is
  last-write-wins and records no owner, so `pos` says where a pill was **written**, not whether it
  **survived** — deriving from it is `M-N06.3-b`, measured wrong by 6 of 8 at `30x6`.
- **Touched symbols:** `mapper/views/radial.py` — `_paint` (the shared pass), `painted_ids`
  — `NEW — created in Phase 3`; the dispatch arm in `mapper/app.py`.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_overflow.py -k "at059"` — arm named normatively
  `test_at059_radial_declares_what_the_canvas_lost` (`C-18`, and the `AT-005`/`AT-006` precedent).
- **Numeric pass threshold:** the declared set **equals** the frame-derived hidden set at every driven
  size on both normative fixtures. Non-degeneracy asserted first, as in `AT-056`'s `PHYS-4`.
- **Acceptance criteria:** a declaration derived from placement over-declares — it names nodes the
  operator cannot see. The whole point of the requirement is that the number matches the frame.
- **Acceptance:** `AT-059` · **Test case:** `TC-092`

##### LLR-N06.3.6 — a declaration that BROKE is not a view that declares nothing

> **DRAFTED BY `02n` (qa-reviewer), PLACED BY COORDINATOR RULING 2026-09-10.** The reviewer wrote this
> row and explicitly declined to insert it — *"I am not authorised to insert it"* — so it is placed
> here rather than left as an assertion in a review artifact. It chains the hazard already ruled to
> ride `Inc-B55a` **first**, which until now carried no `AT` id, no `LLR` row and no node.

- **Traceability:** HLR-N06.3
- **Origin:** `A-94 ruling_2_hazard_first`; requirement form drafted in `02n` §6.
- **Statement:** While the declaration for the current view cannot be computed, the system shall not
  paint the same surface it paints when the view has nothing to declare; a **broken** declaration and
  an **absent** one shall be distinguishable observables.
- **Touched symbols:** `mapper/app.py:1596-1603` — renderer-to-function resolution moves **outside**
  the `try` and **raises** for an unregistered renderer; the `try` keeps catching layout failures only,
  for which `None` is the honest answer.
- **Validation:** `test (pilot)` + `test (unit)`
- **Executed verification:** `pytest tests/test_overflow.py -k "at058"` — arms named
  `test_at058_an_unregistered_renderer_raises_rather_than_declaring_nothing` and
  `test_at058_a_layout_failure_still_degrades_to_absent`.
- **Numeric pass threshold:** with a renderer that exports no `painted_ids`, resolution **raises** —
  **0** frames in which it returns `None`. With a renderer whose layout raises, `_unpainted_ids`
  returns `None` and the frame carries the declared degradation — **0** unhandled exceptions escaping
  the message pump. The two paths produce **different** painted frames.
- **Acceptance criteria:** `except Exception: return None` is total, and `None` reads as *"this view
  declares nothing"* (`app.py:1569`, `:2142`), which `LLR-N06.3.3` makes mean *nothing is hidden*.
  `Inc-B55` is what makes this seam reachable by more than one renderer. Wiring a declaration through
  a seam that can swallow *"declaration broken"* into *"declares nothing"* ships the silent skip
  `A-98` exists to prevent — **and it would silently swallow `AT-056` and `AT-057` themselves.**
- **Sequencing:** fixed **FIRST** inside `Inc-B55a`, before the declaration is wired through the seam.
- **Acceptance:** `AT-058` · **Test case:** `TC-091`
---

### 3.5 · US-N07 «búsqueda» — a search that says how much it found *(**Inc-4a** search core + **Inc-4b** seat and walk — §5.4, split by `#D36`)*

> **Header re-pointed 2026-08-29.** ~~*(Inc-4)*~~ is a **retired** id. §5.4 remains the sole authority
> for the cut; this header points there and states no cut of its own. Within this section:
> **`Inc-4a`** owns `HLR-N07.1` (the single owner, the deletion, `LLR-N07.1.3`'s pill tail),
> `HLR-N07.2`'s count, and `AT-018` `AT-019` `AT-020` `AT-021` `AT-052`. **`Inc-4b`** owns
> `HLR-N07.3`'s walk, the seat rebind, the toasts, `esc`, and `AT-022` `AT-023` `AT-046` `AT-047`
> `AT-051` `AT-051b` `AT-053`. **`AT-024` is `Inc-5`'s** and is struck from this story's Inc-4 scope.

#### Acceptance (black-box) — US-N07

- **Observable outcome:** the operator types a query and is told how many nodes in the **whole map**
  match — including nodes inside folded branches and nodes off the current viewport — and can walk
  them in the order they appear in the tree. When nothing matches, the screen says so in a way that
  cannot be mistaken for a result.
- **Shipped surface:** the search input on `MapScreen` (`Input(placeholder="/buscar",
  id="search-input")`, `mapper/app.py:1107`), opened by the real `slash` chord
  (`map 'slash' -> search`, executed **M-9**), with the count and the empty state observed in the
  rendered text of the shipped widgets.
- **Deliverable + observation:** a painted line of the form `n/N coincidencias` where `N` is the
  whole-graph match count; a selection that lands on successive matching nodes; and a painted
  empty-result state distinct in **both** text and tone from any non-empty state.
- **Acceptance tests:** `AT-018`, `AT-019`, `AT-020`, `AT-021` *(Inc-4a)* · `AT-022`, `AT-023`,
  `AT-051`, **`AT-051b`**, **`AT-053`** *(Inc-4b)* · `AT-052` *(Inc-4a)* · ~~`AT-024`~~ — **moved to
  `Inc-5`**.
- **`AT-024` LEAVES THIS INCREMENT (`#D36` fold, 2026-08-29).** Its owner is `LLR-N07.2.2b`, which
  §5.4 — the sole authority — places in **`Inc-5`** (`outline.py`, `radial.py`, `lane.py`: three files
  neither `Inc-4a` nor `Inc-4b` touches). Executed over the **derived** renderer set at `5f4816c`,
  driving `state.query="ana"` against `""`:

  ```
  lane.LaneRenderer          text_differs=False  spans_differ=False
  lane.RailTimelineRenderer  text_differs=False  spans_differ=False
  lane.HybridLaneRenderer    text_differs=False  spans_differ=False
  layered.LayeredRenderer    text_differs=False  spans_differ=True
  outline.OutlineRenderer    text_differs=False  spans_differ=False
  radial.RadialRenderer      text_differs=False  spans_differ=False
  ```

  **Five of six renderers are query-insensitive today**, and nothing in Inc-4's budget can change
  that. Realising `AT-024` here would mean pulling `LLR-N07.2.2b` in, taking the increment to **7
  source files**. Recorded so the omission reads as **known**, not as an oversight.
- **Two `Inc-5` defects found while measuring, recorded now rather than re-discovered there.**
  **(i)** `LLR-N07.2.2b`'s threshold says the rendered **text** differs; executed on the one compliant
  renderer, `text_differs=False` and `spans_differ=True` — **the threshold is false on a correct
  implementation**, the `AT-046` shape one LLR over. Restate as *"the hit node's style spans differ"*.
  **(ii)** The naive derivation of "every renderer" sweeps in `state.IRenderer`, a `Protocol` that
  raises on instantiation — `Inc-5`'s derived set must exclude `Protocol` subclasses or it **crashes
  rather than being wrong**.
- **`AT-051` and `AT-052` are NEW at amendment set 3 pass 2** (`UX2-C-07`, `UX2-C-06`; §6.5 A-70,
  A-71). `AT-051` presses the real `M`, the relocated chord no acceptance pressed; `AT-052` asserts
  the painted count line names which question it answers. Both are on `HLR-N07.3`'s `Acceptance:`
  line and in §5.2's behavioral row, so both satisfy the three-way rule at authoring time rather
  than being found missing a leg at the gate.
- **Boundary catalog (QC-3):**
  - ☑ **empty** — `AT-023` submits a query matching nothing, and separately submits an empty query.
  - ☑ **boundary** — `AT-022` walks past the last match and asserts the specified wrap behaviour,
    and walks backwards past the first.
  - ☑ **invalid** — `AT-023` submits a query consisting only of whitespace and one carrying Rich
    markup, asserting neither is treated as a match-everything.
  - ☑ **error** — `AT-024` drives the outline and radial views, where `query` is dropped on the floor
    today (`**kwargs` swallow, `docs/ARCHITECTURE.md` §4a defect 2); reporting a count a view does
    not paint is the error class this story exists to prevent.

#### HLR-N07.1 — one owner decides what matches

- **Traceability:** US-N07
- **Statement:** The search module shall be the single component that decides which node ids match a
  free-text query, the renderers shall receive matched ids as a set and shall not evaluate any query
  predicate, and the renderer's inline query predicate shall be removed.
- **Rationale (informative):** two definitions of "hit" ship today (P-18, risk A-3) and a count taken
  from one with a highlight taken from the other disagrees **on screen** — precisely what this story
  exists to prevent. R-014 / D6 names the owner. The `views -> search` edge is deliberately **not**
  created: the renderer receives `frozenset[str]`, which is a builtin and adds no dependency.
- **Validation:** `test (unit)` + `inspection`
- **Executed verification:** `pytest tests/test_search.py -k "search_owns_matching"` *(provisional)*;
  plus a grep asserting the inline predicate's tokens are absent from `mapper/views/`.
- **Numeric pass threshold:** **0** occurrences of the lowered-query comparison idiom in
  `mapper/views/` after the change. **Pre-state executed at draft:** `grep -n "qlower"
  mapper/views/layered.py` returns **4 hits** at lines `144`, `146`, `147`, `148`, with the `hit`
  binding at `:145` and its only consumer at `:159`. A probe that cannot show a non-trivial
  pre-state is unproven; this one shows 4.
- **Priority:** high
- **Acceptance:** `AT-020`, `AT-021`
- **Citation correction (recorded, not silently fixed):** the batch brief and `PLAN.md` §9 D6 cite the
  inline predicate as `views/layered.py:144-149`. Executed at draft, the predicate spans
  **`layered.py:144-148`** and its consumer sits at `:159`. The one-line drift does not change the
  decision; it is recorded because a stale line number is what turns an assertable deletion into a
  judgement call at the reverse census.

##### LLR-N07.1.1 — the inline predicate is deleted and its deletion asserted

- **Traceability:** HLR-N07.1
- **Statement:** The layered renderer shall paint a node as a hit if and only if that node's id is a
  member of the hit set carried in the view state.
- **Touched symbols — RE-EXECUTED AND CORRECTED 2026-08-29 (`#D36` fold); the parked addresses are
  Inc-2/Inc-3-stale and the consumer list was INCOMPLETE:**
  `mapper/views/layered.py` — the module-level predicate **`_matches` at `:113-119`** (not an inline
  expression), its **three** call sites at `:530`, `:535` and **`:600`**, and the `query` field are
  **deleted**; `mapper/views/state.py::ViewState.hits` — `NEW — created in Phase 3`;
  `mapper/views/state.py::ViewState.query` — **DELETED** (`#D39`);
  `mapper/app.py:1769` — the export-site writer, migrated from `query=` to `hits=`;
  `tests/test_app.py:448` — the **only causal break in the suite**, found by the architect lens after
  the orchestrator's own census missed it by sweeping `mapper/` and stopping there.

  > **~~"the `qlower` binding at `:144`, the `hit` expression at `:145-148`, the `query` parameter at
  > `:83`"~~ IS DECAYED AT EVERY ADDRESS.** Executed at `5f4816c`: `grep -rn "qlower" mapper/views/`
  > returns **9** occurrences, all in `layered.py` — `:113 :116 :117 :118 :119` (the predicate body),
  > `:530` (`qlower = query.lower()`), `:535` (the card hit), `:600` and `:601` (**the fold pill's hit
  > tail**). Per-file: `lane.py` 0, `outline.py` 0, `radial.py` 0, `state.py` 0, `__init__.py` 0.
  > Lines `:144-160` are now `_tree_layout`'s body. **A census asserting "4 → 0" measures a number
  > that no longer exists**; the restated threshold is **9 → 0**, and the predicate is an **AST walk**
  > (zero `FunctionDef` named `_matches`, zero `Name` nodes binding or loading `qlower`), never a
  > grep — a grep cannot separate a call from a mention, and an absence-only assertion is satisfied by
  > a rename.
  >
  > **THE THIRD CALL SITE IS THE FINDING.** `:600` powers the **fold pill's hidden-hit count** —
  > `HLR-N06.2`, shipped in Inc-3, *after* this LLR was sealed. Deleting `_matches` therefore either
  > breaks a painted surface or leaves the threshold at 9. It gets its own requirement:
  > **`LLR-N07.1.3`** below.
- **Validation:** `test (unit)` + `inspection`
- **Executed verification:** `pytest tests/test_layered.py -k "hits_come_from_the_state"`
  *(provisional)* — render with a hit set the renderer could not have computed itself (an id whose
  ficha contains none of the query text), and assert it is painted as a hit.
- **Numeric pass threshold:** the injected id is painted with the hit style; **0** occurrences of
  `qlower` remain in `mapper/views/` (pre-state: **4**).
- **Acceptance criteria:** the positive arm uses an id the old predicate would have rejected, so a
  surviving inline predicate fails the test rather than coincidentally agreeing with it. **A
  deletion asserted only by absence can be satisfied by a rename; this arm cannot.**

##### LLR-N07.1.3 — the fold pill's hit count is RE-ROUTED, not deleted *(NEW — `#D36` fold, 2026-08-29)*

- **Traceability:** HLR-N07.1, HLR-N06.2
- **Statement:** The layered renderer shall compute a folded branch's declared hit count as the size
  of the intersection between that branch's descendants and the hit set carried in the view state,
  and shall continue to paint that count in the fold pill.
- **Why this LLR exists.** `LLR-N07.1.1` deletes `_matches`, whose **third** call site
  (`layered.py:600`) is the pill's hit tail — a surface `HLR-N06.2` shipped in **Inc-3**, after
  `LLR-N07.1.1` was sealed. Without this requirement the increment has only two exits and both are
  defects: break a painted surface, or leave `HLR-N07.1`'s threshold at 9.
- **Touched symbols:** `mapper/views/layered.py` — the pill's `hits` term, and
  `tests/test_darkside_census.py`'s `CONFORMING_SEVERITY` row for
  `cv.text(cx + 2 + len(core), y + card_h, tail, darkside.WARN)`.
- **Validation:** `test (pilot)`
- **Executed verification:** fold a branch containing known hits with the real `z`, submit a query,
  and read the pill's tail **off the painted frame**.
- **Numeric pass threshold:** the painted tail equals `len(descendants(branch) ∩ hits)`, with the
  descendant set re-derived by the test's own walk over `graph.edges` and never obtained from the
  renderer. Asserted **non-zero** in at least one arm, or the predicate cannot fail.
- **THIS IS A DECLARED, MEASURED BEHAVIOUR CHANGE — it is not a refactor.** `LLR-N07.1.2` widens the
  hit definition, so the pill's number moves for existing fixtures. Executed on one fixture with the
  descendant count held constant so the tail is isolated: **`+4 1` → `+4 4`**. An empty hit set paints
  no tail, proving the value is query-driven.
- **AND NOTHING IN THE SUITE PINS IT — which is why the change is dangerous rather than merely
  visible.** Executed: both `_PILL` regexes (`test_fold.py:37`, `test_overflow.py:80`) stop at
  `+(\d+)`; zero `ViewState(query=…)` constructions exist; `query_text` is set in exactly one test,
  the export test, whose file contains **zero** folds. Root cause found and recorded:
  **`grep -rn "TC-026" tests/` returns no hit** — `TC-026`'s *"hit count when a query is live"* clause
  exists only as a row in the §5 matrix and was **never implemented**. That is an inherited Inc-3 gap,
  not one this increment creates; `Inc-4a` is where it becomes dangerous, because the number changes
  on a fully green suite.
- **`TC-026b` is therefore NON-NEGOTIABLE for this increment** (architect lens `02k`): it is the node
  that makes the pill's count falsifiable at all.
- **C-26 reverse census — one hit, outside this story.** `tests/test_darkside_census.py:212` pins the
  **literal source text** of the pill's tail line inside Inc-1's hue census, whose sibling arm asserts
  `len(sites) == 38` (a figure its own comment records moving 36 → 38 in Inc-3 for exactly these two
  `WARN` sites). A behaviour-preserving restructure still moves it. The drift is legitimate and
  expected; it shall be **named in the packet in advance**, never discovered as a surprise red.
- **Named weaker variant (`M-N07.1.3-a`):** let the `hits` term fall to `0` when `_matches` is
  deleted. The pill then paints `+2` with no tail on a suite that stays green, because nothing pins
  the tail. Reddened only by `TC-026b`.
- **Acceptance:** `TC-026b`

##### LLR-N07.1.2 — the widened hit definition is a declared user-visible change

- **Traceability:** HLR-N07.1, risk A-3
- **Statement:** When a query matches a node's id, its ficha subtitle, or an attachment's caption or
  path, the system shall paint that node as a hit.
- **Touched symbols:** `mapper/search.py::SearchIndex.query` (`search.py:13`) delegating to
  `mapper/model.py::Graph.search_hits` (**`model.py:224`** — ~~`169-184`~~ re-executed and corrected
  2026-08-29, `#D36` fold; a stale address is what turns an assertable citation into a judgement call
  at the reverse census — it joins `node.id`,
  `ficha.title`, `ficha.meta`, `ficha.notes`, the field values, and each attachment's caption or
  path).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_search.py -k "hit_widening_is_intentional"`
  *(provisional)* — one graph, one query, three nodes that match **only** by id, **only** by
  subtitle, and **only** by attachment.
- **Numeric pass threshold:** all 3 are hits under the new owner; all 3 are **not** hits under the
  old inline predicate, asserted by reproducing that predicate inline in the test as a negative
  control. Executed pre-state (**M-7**), query `"riesgo"` over a 6-node graph: old predicate returns
  `['b','d']` (2 hits), new owner returns `['riesgo-root','b','c','d','e']` (5 hits); the gained set
  is `['riesgo-root','c','e']`, matched by node id, by `ficha.meta` and by attachment respectively;
  the lost set is **empty**, so the widening is monotone.
- **Acceptance criteria:** this is a **user-visible behaviour change**, not a refactor, and it gets
  its own acceptance (`AT-020`) rather than riding in as a side effect of naming an owner.

#### HLR-N07.2 — the count is taken over the whole graph

- **Traceability:** US-N07
- **Statement:** When the operator submits a query, the system shall paint a count of matching nodes
  computed over every node of the loaded graph, including nodes inside folded branches and nodes
  outside the current viewport.
- **Rationale (informative):** risk A-6 names the classic defect — a count taken over
  `visible_rows()`. With US-N06 landing fold in the same batch, shipping fold without a whole-graph
  count would **actively create** the defect this story closes.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_search.py -k "count_is_whole_graph"` *(provisional)*
  — open search with the real `slash`, type the query, submit, read the painted count; then fold a
  branch containing a known match with the real `z` and read the count again.
- **Numeric pass threshold:** the count equals `len(SearchIndex(graph).query(q))` in all four states:
  nothing folded and everything on screen; a matching branch folded; the viewport panned so a match
  is off screen; both. The count is **identical** across all four.
- **Priority:** high
- **Acceptance:** `AT-018`, `AT-019`
- **THE COUNT REGION IS NAMED — `#D37`, 2026-08-29. It was named NOWHERE in the sealed text.**
  §5.2 addressed this story as *"`#search-input` and the count region beside it"*, and **"the count
  region" is not a widget id anywhere in this document** — while `LLR-N07.3.2` simultaneously requires
  `0 coincidencias` to paint *"at the same position a non-zero count occupies"*, a **positional claim
  about an unnamed surface**. That is unbuildable as written.

  **Ruling: the count region is `#map-pagination`**, declared once as `COUNT_REGION_ID` and read by
  every predicate rather than re-typed. It is the natural home and the choice is executed, not
  preferred: it already carries Inc-3's overflow declaration, whose painted content measures
  `' ▰▱▱▱▱▱▱▱   1/8  ▽ 2 fuera de vista'`, so the count line joins a strip that already exists to
  declare counts. One declaration, four readers — the same rule `UX-Q3-b` and `LLR-N14.1.1` invoke.

  **Two riders, both from executed measurement.** (a) **Any predicate parsing a numeral shall JOIN the
  region-clipped rows before parsing.** Measured, `#map-pagination` is height 1 at 118x34, 100x30 and
  80x24 on `legacy` — but `test_overflow.py:91-99` records a wrap at a 30-column strip, and the
  region's height is not a constant any predicate may assume. (b) **Position is asserted as a measured
  offset on the same screen, never as a literal column number** — a literal breaks at every width.
  Executed: `grep -rn "coincidencia" mapper/` returns no output. Search today is a bare `Input` with
  no count and no cursor (P-6, executed: `app.py:1107`, `:1524`, `:1531`, `:1539`).

##### LLR-N07.2.1 — the count is invariant under fold

- **Traceability:** HLR-N07.2
- **Statement:** While a branch containing at least one matching node is folded, the painted match
  count shall be unchanged from its value while that branch is unfolded.
- **Touched symbols:** the count computation in `mapper/app.py::MapScreen` —
  `NEW — created in Phase 3`; it consumes `SearchIndex.query` over the full graph and must not
  consume `MapScreen.folded`.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_search.py -k "count_invariant_under_fold"`
  *(provisional)* — on `fixtures/legacy_nodos.yml`, the **pinned** query below, then the real `z`
  on `fin`.
- **Numeric pass threshold (`QA-M-01`, §6.5 A-27):** the query is **`carlos`**; the two counts are
  equal; the count is `> 0` in both states; **and at least one hit lies strictly inside the folded
  branch `fin` and is painted before the fold**.
- **THE THRESHOLD WAS WEAKER THAN ITS OWN STATEMENT (`QA-M-01`).** The statement demanded *"a query
  matching a node **inside** rama `fin`"*; the threshold demanded only *"the two counts are equal,
  and `> 0` in both states"*. Those are not the same requirement, and the gap is not theoretical:
  `02a` measured that **`riesgo` — the batch's own working query — satisfies the threshold with
  `naive == correct` and is vacuous**, because it matches nothing inside the folded branch, so
  folding cannot change the count under either implementation. `carlos` is pinned because it
  discriminates (`bloqueado` and `ana` also do). The inside-the-branch clause is what carries the
  statement's actual meaning into the acceptance.
- **Named weaker variant (`M-N07.2.1-a`):** compute the count from the painted canvas rather than
  from the whole graph. Green on `riesgo`; red on `carlos` once the inside-the-branch clause holds.
  This is exactly the defect the story exists to close (risk A-6), and the parked threshold could
  not see it.
- **Acceptance criteria:** **this is the assertion that distinguishes the story from the defect it
  exists to close** (risk A-6, stated verbatim). The `> 0` clause stops it passing on two zeros; the
  pinned query and the inside-the-branch clause stop it passing on a query that never tests the
  invariant.

##### LLR-N07.2.2 — every view reports a count it can also paint · **SPLIT by `PDR-…#D12`**

**Split into `LLR-N07.2.2a` (Inc-2) and `LLR-N07.2.2b` (Inc-5), per `PDR-2026-08-26-ui-next-batch-02#D12`
(§6.5 A-28).** As written this LLR bundled a mechanical signature migration with a semantic
capability, and the two **cannot** live in one increment: **Inc-2's gate is byte-identical renderer
output against the baseline**, and painting hits destroys byte identity. The split is what lets both
be gated.

##### LLR-N07.2.2a — the signature migration *(Inc-2, output unchanged)*

- **Traceability:** HLR-N07.2
- **Statement:** All six `render` definitions shall take `(graph, state)`, and the rendered output
  shall be byte-identical to the pre-change output for the same graph and geometry.
- **Touched symbols, re-derived at `d877784` — three of the six addresses were stale (§6.5 A-28):**
  `lane.py:108`, `:171`, `:311` *(unchanged)*; `layered.py:131` *(parked `:78`)*;
  `outline.py:47` *(parked `:17`)*; `radial.py:107` *(parked `:33`)*.
- **CORRECTION — *"all six lose `**kwargs`"* executes FALSE (`QA-N-03`).** Executed:

  ```
  lane.py:108 / :171 / :311   **kwargs        outline.py:47   **kwargs
  radial.py:107               **kwargs        layered.py:131  query: str = ""   <- NOT **kwargs
  ```

  **5 of 6** declare `**kwargs`; `layered.py:131` takes an explicit `query` parameter. The reverse
  census greps this line, so the wrong figure would have made the census miss a file. The migration
  removes `**kwargs` from five and the explicit `query` from one.
- **Validation:** `test (unit)`
- **Numeric pass threshold — SET EQUALITY on both sides of the protocol, never a floor
  (`P2-C6`, `QA2-C-02`, §6.5 A-52):**
  1. **Definitions.** The set of migrated definitions **equals** the derived set of `render`
     definitions in `mapper/views/*.py`.
  2. **`**kwargs`.** Occurrences across that set `== 0` after the change, and the explicit
     `query: str = ""` parameter at `layered.py:131` is removed with them.
  3. **Call sites — THE CLAUSE THAT WAS MISSING ENTIRELY.** The set of call expressions passing
     arguments to a `render` attribute **equals** the migrated set, and **zero call sites of the old
     shape survive**.
  4. **Byte identity.** Every renderer's output byte-identical to pre-change.

- **THE A3 CENSUS — question, instrument, SHA. This is `02g` §3's settled figure, adopted verbatim
  (`P2-C6`, `QA2-C-02`).**

  > **QUESTION.** Which call expressions invoke the **MAP-RENDERER** protocol and therefore must
  > migrate when `IRenderer.render` gains `ViewState`?
  >
  > **INSTRUMENT. AST, not grep** — grep cannot tell a call from a **mention** of a call. An `ast`
  > walk over `mapper/**/*.py` and `tests/**/*.py`, selecting `Call` nodes whose `func` is an
  > `Attribute` named `render` **with at least one argument**; and, for the definition side, an `ast`
  > walk **restricted to `mapper/views/`**.
  >
  > **MEASURED AT.** `3fe0e4b`.
  >
  > ```
  > ARG-FUL call sites (the A3)  : 23      distinct files : 10
  >     production               :  3      -> mapper/app.py:737, :1352, :1727
  >     test                     : 20      (9 files)
  > ZERO-ARG .render() sites     : 25      <- Textual WIDGET protocol, NOT in the A3
  > def render in mapper/views/  :  6      <- lane.py:108, :171, :311; layered.py:131;
  >                                           outline.py:47; radial.py:107
  > ```

- **`.render` NAMES TWO DIFFERENT PROTOCOLS IN THIS TREE, AND THAT IS WHY FIVE GENERATIONS OF THIS
  NUMBER WERE WRONG.** The Textual `Widget.render()` sites take no arguments and **must not be
  migrated**; the `IRenderer` sites take arguments and must. A line-oriented count answers neither
  question. Executed at `3fe0e4b`, a grep returns **24** sites / 11 files — one more than the AST —
  and the extra is `mapper/widgets/rail.py:180`, a mention of `renderer.render(...)` **inside a
  docstring**. **Only the AST separates a value from its own encoding** (`C-42`'s rider). The QA
  lane's independent run reported the same 24 the same way, which is corroboration of the *method's*
  failure, not of the figure.
- **~~`>= 6`~~ IS SUPERSEDED, AND IT WAS WORSE HERE THAN ANYWHERE ELSE A-32 ABOLISHED A FLOOR.**
  `A-32` replaced floors with set equality for `LLR-S06.3.1`, `LLR-S06.3.3` and `LLR-S06.3.4`; this
  one survived. The naive derivation `grep -rn "def render" mapper/` returns **17**, of which **11
  are Textual widgets that must NOT be migrated** — so a census that sweeps them in **passes `>= 6`
  comfortably while being wrong by eleven definitions**. `A-32`'s argument applies verbatim with the
  sign flipped: a derivation that *gains* eleven wrong members sits just as comfortably above a floor
  as one that loses three right ones.
- **Named weaker variant (`M-N07.2.2a-a`):** gate on definitions only, as the parked threshold did.
  All six signatures change, the suite is green, and **the 23 call sites still pass the old shape** —
  the migration half-lands and two contracts are live at once, which is risk `A-1` stated verbatim.
  Reddened by threshold 3, which is why threshold 3 exists.
- **Named weaker variant (`M-N07.2.2a-b`):** derive the call-site set with
  `grep -rn "\.render(" mapper/ tests/`. It sweeps in the 25 zero-arg Textual sites and the one
  docstring mention, so the migrated set can never equal it and the gate either false-fails forever
  or gets weakened back to a floor. Reddened by naming the instrument as AST in the verification.
- **Executed verification:** `pytest tests/test_a3_census.py -k "render_protocol_migrated"`
  *(provisional)* — the two `ast` walks above, each asserting its derived set is **non-empty before
  it is evaluated**, as `LLR-S06.3.1` requires.

##### LLR-N07.2.2b — the hit-painting capability *(Inc-5)*

- **Traceability:** HLR-N07.2
- **Statement:** When a query is active, every renderer shall paint the nodes carried in
  `state.hits` distinguishably from non-hit nodes, in every view the operator can reach.
- **Touched symbols:** `outline`, `radial` and the three `lane` renderers.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_views_hits.py -k "every_renderer_paints_hits"`
  *(provisional)* — the renderer set is **derived** by iterating the classes that satisfy the
  `IRenderer` protocol, never hand-listed.
- **Numeric pass threshold — CORRECTED 2026-08-29 (`#D42`); the parked wording is FALSE ON A CORRECT
  IMPLEMENTATION:** for each derived renderer, the hit node's **style spans** with a non-empty hit set
  differ from its spans with an empty hit set.
- **~~"the rendered TEXT … differs from the text with an empty hit set"~~ WAS THE WRONG INSTRUMENT.**
  Executed during Inc-4a over the **derived** renderer set, driving `state.query="ana"` against `""`:

  ```
  lane.LaneRenderer          text_differs=False  spans_differ=False
  lane.RailTimelineRenderer  text_differs=False  spans_differ=False
  lane.HybridLaneRenderer    text_differs=False  spans_differ=False
  layered.LayeredRenderer    text_differs=False  spans_differ=True   <- the ONE compliant renderer
  outline.OutlineRenderer    text_differs=False  spans_differ=False
  radial.RadialRenderer      text_differs=False  spans_differ=False
  state.IRenderer            cannot construct: Protocols cannot be instantiated
  ```

  **A hit is painted by STYLE, never by adding characters** — so on the one renderer that already
  honours the query, `text_differs` is `False`. The parked threshold would have **false-failed a
  correct implementation**, which `C-53` prices exactly as high as passing a wrong one. This is the
  `AT-046` shape one LLR over: an oracle written from the requirement's *wording* rather than from the
  producer's *output*.
- **THE DERIVED SET SHALL EXCLUDE `Protocol` SUBCLASSES (`#D42`).** `state.IRenderer` is a **census
  artifact, not a participant** — it is the contract the renderers satisfy, and it raises on
  instantiation. A naive "every class with a `render` method" sweep pulls it in and **crashes rather
  than being wrong**, a failure mode that reads as a defect in the code under test. The set stays
  **derived, never hand-listed** (`C-31`); the exclusion is a property of the rule, not a carve-out for
  one name, so a second Protocol added later is excluded for the same reason.
- **This is what finally gives `AT-024` an owner.** `AT-024` was the orphan that observes exactly
  the `**kwargs` swallow and which no HLR claimed — one of the five `QA-B-03` catalog-only ids
  (§6.5 A-29). It is now claimed on an `Acceptance:` line.
- **Acceptance:** `AT-024`
- **Acceptance criteria:** today `outline`, `radial` and all three `lane` renderers absorb `query`
  into `**kwargs` and drop it (`docs/ARCHITECTURE.md` §4a defect 2), so the outline and radial views
  would report hits they do not paint. **The renderer set is derived from the protocol**, so a
  seventh renderer added later is covered without anyone remembering to add it — the A-4 lesson
  applied to a second surface.

##### LLR-N07.2.3 — the A3's two new types are CREATED, and the interface gains its first mechanical enforcement *(Inc-2)*

- **Traceability:** HLR-N07.2; risk **A-11**; `#D3` (`views/state.py` as the home); `R-012`
- **Statement:** `mapper/views/state.py` shall declare `ViewState` as a frozen dataclass in which
  every field carries a default, and `IRenderer` shall be declared as a `runtime_checkable` Protocol
  whose `render` method takes `(graph, state)` and returns `Text`; and the verification shall assert
  that every renderer class in `mapper/views/` satisfies that Protocol.
- **Rationale (informative):** `P2-C5` and `02c` §5.4, executed. **No requirement in this document
  creates either type.** Six LLRs name individual `ViewState` *fields* as `NEW — created in
  Phase 3`, and **nothing owns the dataclass itself, its frozen-ness, its fully-defaulted contract,
  or the roster it starts with**. `IRenderer` is worse: executed at `3fe0e4b`, it exists as a Python
  type **0** times — it survives only as prose comments at `mapper/views/layered.py:288` and
  `mapper/widgets/rail.py:6`. **The batch's headline A3 migrates a protocol that has never been
  written down in code**, and its first mechanical enforcement is this LLR.
- **Touched symbols:** `mapper/views/state.py` — `NEW — created in Phase 3`;
  `mapper/views/state.py::ViewState` — `NEW`; `mapper/views/state.py::IRenderer` — `NEW`.
  Consumed by all six renderer definitions in `mapper/views/` and by `mapper/app.py`.
- **Validation:** `test (unit)` + `inspection`
- **Executed verification:** `pytest tests/test_view_state.py -k "protocol_and_state"`
  *(provisional)* — construct `ViewState()` with no arguments; assert `dataclasses.fields` all carry
  defaults and the instance rejects attribute assignment; then, over the **derived** renderer set,
  assert Protocol satisfaction **and** the signature clause below.
- **Numeric pass threshold:**
  1. `ViewState()` constructs with **0** arguments; the count of fields lacking a default `== 0`;
     assigning to any field raises.
  2. `isinstance(r, IRenderer)` is `True` for **every** member of the derived renderer set, and the
     derived set is asserted **non-empty before it is evaluated**.
  3. **The signature clause.** For every member of that set, the `render` signature's parameter names
     **equal** `(self, graph, state)` — derived with `inspect.signature`, not by eye.
- **`isinstance` OVER A `runtime_checkable` PROTOCOL IS A VACUOUS CHECK ON ITS OWN, AND THIS IS THE
  WHOLE REASON THRESHOLD 3 EXISTS.** `runtime_checkable` makes `isinstance` check **member presence
  only — never signatures**. Every one of the six renderers already has a `render` attribute
  **today**, with the old `(graph, selected_id, w, h, **kwargs)` shape. **So threshold 2 passes at
  `3fe0e4b`, before any migration happens at all.** Risk `A-11` proposes the `isinstance` assertion
  as *"a one-line assertion per renderer"*, and taken literally that assertion is green on the
  unmigrated tree. It is admitted here as a **structural** guard — it catches a renderer that stops
  being a renderer — and threshold 3 is what makes the pair discriminating. `C-55` limb 1: an
  assertion whose pre-state is already green is not evidence unless something else can fail.
- **Named weaker variant (`M-N07.2.3-a`):** ship threshold 2 alone, as `A-11` words it. **Green on
  `master` with zero code changed.** Reddened by threshold 3.
- **Named weaker variant (`M-N07.2.3-b`):** declare `ViewState` with required fields and construct it
  at each call site. Every current test passes; the next increment adding a field breaks every
  existing construction, and the natural repair is to add the argument everywhere — which converts
  `R-012`'s additive property into an A3 per field. Reddened by threshold 1's zero-argument clause.
- **`R-012` IS STATED NORMATIVELY HERE, BECAUSE IT IS THE RULE THAT KEEPS FOUR INCREMENTS OUT OF A3
  TERRITORY.** Adding a **defaulted** field to this frozen dataclass is **additive and never
  re-opens the A3** (`ARCHITECTURE-proposed-at-ARQ.md:343`, ratified by `02c` §5.4). Without the
  clause an implementer reading this document alone sees a dataclass gaining fields across
  increments and no statement that **only the first is an A3** — and the safe-looking response is to
  re-run the A3 ceremony three times, or to freeze the roster and force each later field through a
  migration. The roster is pinned at **Inc-2** and grows by default-carrying addition thereafter.
- **The field roster and its owners, each already declared elsewhere — listed so the dataclass has a
  starting shape rather than being assembled by accident:** `focus_owner` (`LLR-CNV.3.1`, Inc-2 —
  in the initial roster); `pan_x` / `pan_y` (`LLR-N06.1.1`, Inc-3); `folded` (`LLR-N06.2.1`, Inc-3);
  `hits` (`HLR-N07.2`'s chain, Inc-4). **`lens_matches` is NOT in this roster** — it was US-N14's and
  is **DEFERRED (`#D23`)** with the story. The follow-on design batch adds it as a defaulted field,
  which by this LLR's own `R-012` clause is additive and does not re-open the A3. **That is the
  clause earning its keep on the first case that tests it.**
- **`with_header` IS NOT IN THE ROSTER, AND THE OTHER ROSTER MUST BE ROUTED (`P2-C4`, `#D2`,
  §6.5 A-56).** `#D2` struck `ViewState.with_header`. **Half of that landed:** executed at
  `3fe0e4b`, `grep -n "with_header" 01-requirements.md` returns **0** — this document is clean — but
  `ARCHITECTURE-proposed-at-ARQ.md` still names it at `:235` and still declares
  `with_header: bool = True` inside the `ViewState` dataclass at `:275`. **Two live rosters for one
  frozen dataclass**, and this LLR is the requirement that creates it, so the collision lands
  squarely here: an implementer reading the ARQ roster writes a field this LLR does not declare, and
  threshold 3's signature clause will not catch it because `with_header` is a *field*, not a
  parameter. **`ARCHITECTURE-proposed-at-ARQ.md` is not this lane's to edit.** The orchestrator
  **shall route** the strike of both lines to the lane that owns it. Recorded as **open** here, with
  this LLR's roster governing in the meantime (`C-44` — found, reported, not swept up).
- **Acceptance criteria:** `#D3` places the file in `views/`, and the dependency ban is re-checked
  rather than assumed — executed, `grep -rn "textual" mapper/views/` returns **0**, and the
  `views → diff` edge already exists at `layered.py:9`, so the new module adds **no** edge. A
  `ViewState` that imported Textual would put the app's state model inside the headless boundary and
  make `export` untestable without an event loop.

#### HLR-N07.3 — the operator walks matches in tree order, and an empty result looks empty

- **Traceability:** US-N07
- **Statement:** When the operator advances the search cursor, the system shall move the selection to
  the next matching node in the order the nodes appear in a pre-order walk of the tree; and if a
  submitted query matches no node, then the system shall paint a state distinct in both text and tone
  from any state in which at least one node matches.
- **Rationale (informative):** `Graph.search_hits` returns dict-insertion order (P-17), which makes
  the cursor jump around the canvas. The tree-order idiom already exists in the tree.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_search.py -k "walk_order and empty_state"`
  *(provisional)* — press the real walk chord repeatedly and record the selected id after each press;
  and submit a query matching nothing and compare the painted text and its style spans against a
  matching query's.
- **Numeric pass threshold:** the recorded selection sequence equals the hit list re-ordered by
  pre-order tree walk, exactly; and for the empty case, both the painted substring **and** at least
  one style span differ from the non-empty case. **Plus the three declared states below, each with
  its exact painted string.**
- **THE UX LENS'S `shall` CLAUSES REACHED NO REQUIREMENT — folded here (`QA-M-05`, `QA-M-06`,
  §6.5 A-33).** §6.4 claimed *"seven of its findings changed §3"*; these did not, and they are
  explicit `shall` clauses in `01b-ux-decisions.md`, not suggestions:

  | Id | State | Declared painted string (Spanish, verbatim) |
  |---|---|---|
  | **UX-Q3-a** | search committed vs still editing | the query chip is painted in a **committed** tone distinct from the editing tone; the two are asserted as different style spans, not different text |
  | **UX-Q3-b** | any live search | the hint line **shall read exactly** `n siguiente · N anterior · esc limpiar` |
  | **E1b** | `n` / `N` pressed with **no search ever submitted** | toast — title `sin búsqueda activa`, body `pulsa / para buscar` |
  | **E1c** | `n` pressed with a **submitted** query that has 0 hits | toast — title `0 coincidencias`, body `«nóm» no aparece en este mapa` |

  **`E1b` and `E1c` are different facts and shall be painted differently** — *"you have not
  searched"* and *"you searched and there is nothing"* — and neither is a silent no-op. The parked
  document contained neither string nor either state anywhere.
- **UX-Q3-b's string is now consistent with `#D5b`.** It names `n` and `N`, which is what the seat
  binds after the Q-3 ruling; had this clause been folded before the ruling it would have named the
  wrong keys. The hint line **shall** read its glyphs from the seat rather than hard-coding them,
  for the same one-declaration-four-readers reason as `LLR-N14.1.1`'s count line.
- **Named weaker variant (`M-N07.3-b`):** implement `E1b` and `E1c` as one toast. Green on any test
  that asserts *"a toast appears"*, and it tells an operator who has never searched to go and look
  for a query they never typed. The two distinct titles are what redden it.
- **Priority:** high
- **Acceptance:** `AT-022`, `AT-023`, `AT-051`, `AT-052`

- **`AT-052` — THE COUNT LINE DECLARES WHICH QUESTION IT ANSWERS (`UX2-C-06`, US-N07 half only;
  §6.5 A-71).** Executed, **nothing painted anywhere declares which result set is live.** The two
  count lines differ in *form* — `3/7 coincidencias` versus the lens's `N nodos en M ramas` — but
  **that difference is incidental, not declared**, and after `#D6` unified the walk it is the only
  cue there is. The named failure, user · task · consequence: an operator searches `/carlos`, reads
  `3/7 coincidencias`, then submits a lens; the seven search hits are silently cleared, `n` still
  reads `siguiente coincidencia`, and **the operator believes they are looking at an intersection
  when they are looking at the lens result over the whole map.** Nothing contradicts them.
  - **Threshold:** the painted count line **names its subject and its term** — one declared string
    per surface, so the two surfaces are distinguishable by **content**, not by an implementer's
    choice of wording. `AT-052` submits a search, reads the line, and asserts the subject is named.
  - **Submit paints no mode change at all, which is why this is the search half's defect too.**
    Executed under Pilot: after `enter`, `focused=None` — **no widget paints a focus ring**, and the
    query text sits in the box looking exactly as it did while it was accepting characters. The
    operator has no painted signal that a search is live.
  - **The US-N14 half of `UX2-C-06` left with the story** (`#D23`) and is not carried here. `C-D6a`'s
    *"only one result set is live"* Layer-0 invariant is unaffected and still owns the clearing.
- **`E1b`'S COPY IS RE-DERIVED, BECAUSE `#D6` INVALIDATED ITS ROUTE (`UX2-C-06`, §6.5 A-71).** `E1b`
  reads title `sin búsqueda activa`, body `pulsa / para buscar` — written under Q-3, **before** Q-7
  unified the walk. Under `#D6`, `n` walks *coincidencias* from **either** owner, so the toast sends
  the operator to `/` even when the surface they wanted was the other one. **This is `02f`'s root
  cause in one line: a consequence that was not re-derived after a decision changed.** **`Inc-4b`**
  shall restate `E1b`'s body against the unified walk.

  **RE-DERIVED AND RULED 2026-08-29 (`#D36` fold): `E1b`'s body becomes
  `no hay coincidencias que recorrer`.** The parked `pulsa / para buscar` prescribes a **route**, and
  `#D6` made the route conditional. Today `/` is the only producer, so the parked body is
  *accidentally* true — **worse than plainly false**, because it becomes misdirection the increment
  the lens lands, and nothing will re-derive it then either. The new body describes the **state** the
  toast reports (there is no live result set to walk), which is true under any number of owners; it
  uses the one noun the surface already declares four times over (seat label
  `siguiente coincidencia`, the count line, `E1c`'s title); and it stays distinct from `E1c` on both
  channels. **The operator is not left routeless, and that is executed, not assumed:** `map/slash` is
  seated with glyph `/` in group **`nav`**, which the keybar paints, and the default hint line already
  reads `navega con j/k/h/l · ↵ ficha · / buscar`. The route is painted **persistently**; carrying it
  in the toast is exactly what would make the toast go stale.

  `E1c` (`0 coincidencias` / `«nóm» no aparece en este mapa`) is **retained verbatim** — it describes a
  completed search with an empty answer, true under either ruling. **One rider, from an executed
  measurement:** its body interpolates the operator's query, making the toast a **coercion sink**.
  Executed on `"riesgo" + U+0008 + U+202E + "[bold]x[/]"` — `darkside.plain` strips the control byte
  and the right-to-left override; `Text.assemble(...).plain` **leaves the RLO alive**. `Text.assemble`
  does not parse markup, so `[bold]` is inert, but an RLO reverses the toast's own sentence.
  **`E1c`'s body shall route the query through `darkside.plain`**, and `AT-023` asserts it with a
  hostile query.
- **~~Flagged `assumed — verify in target framework`: the walk chord. Q-3 is live and unsettled.
  This requirement is written chord-agnostic.~~ SUPERSEDED — Q-3 AND Q-7 ARE RULED, AND THE CHORDS
  ARE NAMED HERE (`QA-B-10`, §6.5 A-26).** A chord-agnostic *requirement* was legitimate; a
  chord-agnostic *acceptance test* is not (C-16), and the rulings existed in the sealed PDR without
  ever reaching this document. Folded:

  | Ruling | Seat row | Group | Increment |
  |---|---|---|---|
  | `#D5b` (Q-3) | `map/n -> next_hit`, label `siguiente coincidencia` | `nav` | **Inc-4b** |
  | `#D5b` (Q-3) | `map/N -> prev_hit`, label `coincidencia anterior` | `nav` | **Inc-4b** |
  | `#D5b` (Q-3) | `map/M -> next_gap`, label `siguiente faltante` | `view` | **Inc-4b** |
  | `#D6` (Q-7) | `⇥` **rejected**; `n`/`N` walk the single active *coincidencias* set | — | ~~Inc-5~~ — **the lens half is DEFERRED (`#D23`)**; the search half rides **Inc-4b** |

  **`AT-022`, `AT-023` and `AT-051` shall press the real `n`, `N` and `M`.** Three seat rows change
  in **Inc-4b** and are reviewed **row-by-row at DDR** — and per `PDR-addendum-3` `#D25` that
  three-row figure is a **regression PIN on this increment's own diff, not a per-increment budget**.
  `keymap.py`'s collision set is **FOUR** — `Inc-3`, **`Inc-4b`**, `Inc-8`, `Inc-9` — as §5.4 now
  re-derives; the "three-way" reading was stale from the moment `#D25` corrected it. Resolved by
  serial ordering and not by ownership: each shall re-run `duplicate_chords()` and the whole-seat pin
  on entry **and** exit, and assert its declared diff **equal** to `bindings_for(scope)`'s entry/exit
  difference (`C-D25a`).
- **`AT-051` IS NEW: THE RELOCATED CHORD IS THE ONLY ONE NO ACCEPTANCE PRESSES (`UX2-C-07`,
  §6.5 A-70).** `#D5b` moves `next_gap` from `n` to **`M`** — and the parked clause named only `n`
  and `N`, so **the relocation was guarded solely by the whole-seat set-equality pin and
  `duplicate_chords()`**. Both are **declaration** checks: they prove the seat *says* `M` is
  `next_gap`, and neither presses it. A seat row can be correct while the action it names is
  unreachable, and this batch's own §6.4 already records the same shape of gap twice.
  **`AT-051` presses the real `M` and reads the painted result**, which is the only arm that
  distinguishes a rebind from a rename.
- **AND THE OPERATOR IS TOLD, ONCE — because the seat change is invisible where they would look.**
  This document already records that between `Inc-4` and `Inc-8` the relocated chord is
  **undiscoverable through `?`**. Measured: at **118 x 34** the label `siguiente faltante` is one of
  the eleven rows **below the fold** in the legend, behind `down` / `pagedown` / `end` — **none of
  which the legend declares** (`UX2-C-05`). So an operator who presses `n` expecting the old
  behaviour has no painted route to the new one. **`Inc-4b` shall paint a one-time declaration on the
  first `n` press after the rebind**, in the toast register the product already uses — the precedent
  is executed: `next_gap` with nothing missing already toasts `cobertura completa`.

  **THIS CLAUSE NOW HAS AN ID: `AT-051b` / `TC-084b` (`#D36` fold, 2026-08-29).** It was a sealed
  `shall` that **no acceptance covered**, found at the `Inc-4b` pre-gate. It cannot ride `AT-051`'s
  node under `C-18`: `AT-051` presses **`M`** and this declaration fires on **`n`** — different chord,
  different chain. Two predicates, because "one-time" is half the claim: **(1)** on a fresh
  `MapScreen`, one real `n` paints a toast naming both the new duty of `n` and the new home of
  `next_gap`, every string read from the **seat** rather than typed; **(2)** a **second** real `n`
  paints a toast that does **not** carry it. Persistence is read from the **frame twice**, never from
  a store. Executed pre-state: after `enter`, a real `n` press paints a **blank** toast row at 118x34
  and 100x30 — so predicate (1) is a genuine gate today.
- **Named weaker variant (`M-N07.3-rebind`):** ship the seat rows and the whole-seat pin, no `AT-051`
  and no declaration. **Green on every existing test**, because every existing test reads the seat.
  The operator's `n` does something new, `M` is undiscoverable for four increments, and *"we moved a
  key and the help does not show it"* is found by a user rather than by a suite.
  *(~~"four-way … Inc-3, Inc-4, Inc-6 and Inc-9"~~ is superseded: the fourth participant was `Inc-6`,
  US-N14's increment, **vacated** by `#D23`. `#D6`'s ruling itself survives the deferral unchanged —
  `⇥` stays rejected and `n`/`N` stay the walk — because it was a ruling about the **seat**, and the
  seat is not deferred. Only its lens-side consumer is.)*
- **Why the unification is not the state-dependent chord `#D10` rejected.** `#D10` rejected that
  option because `map/n` would have had **no constant `label`**, breaking the whole-seat pin's
  static set equality. Here the label `siguiente coincidencia` is **true in both cases**, so the
  seat stays a static set, the pin stays set equality, and `groups_for_keybar` still returns
  `binding.label` straight from the seat. **The concept is unified; the declaration is not.**
- **C-D6a — "only one result set is live" is a TESTED Layer-0 invariant, not an assumption.** It is
  the load-bearing premise of the whole `#D6` ruling: submitting a lens **shall** clear search hits,
  and submitting a search **shall** clear lens matches. Asserted at Layer 0 on `MapScreen`, not
  inferred from the walk behaving correctly. **Named weaker variant (`M-N07.3-a`):** implement the
  walk over `search_hits or lens_matches` without clearing either. `AT-022` passes whenever only one
  is populated — which is every single-feature test — and the two sets diverge silently the first
  time an operator uses both. The invariant is what reddens it.
- **Cross-increment regression, recorded (owner: Inc-9).** Inc-4 relocates `next_gap` to `M` in
  group `view` — the group Inc-8 has not yet un-truncated at that point — so **between Inc-4 and
  Inc-8 the relocated chord is undiscoverable through `?`**. The new `n`/`N` rows land in group
  `nav`, which is painted, so search itself stays discoverable. Not a blocker; recorded because
  *"we moved a key and the help does not show it"* is found by a user, not by a suite.

##### LLR-N07.3.1 — hit order is tree order, not dict order

- **Traceability:** HLR-N07.3
- **Statement:** The system shall order the hit list by a pre-order walk of the graph from its root,
  following each node's children in their declared order.
- **Touched symbols:** an ordering helper in `mapper/search.py` — `NEW — created in Phase 3`;
  it reproduces the walk shape of `mapper/app.py::MapScreen._incomplete_order` (`app.py:1601-1623`,
  executed — pre-order DFS pushing `reversed(children_of(nid))` onto a stack).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_search.py -k "hits_are_in_tree_order"`
  *(provisional)* — a graph whose dict-insertion order and tree order **differ**, asserted to differ
  inside the test itself so the ordering is not trivially satisfied.
- **Numeric pass threshold:** the ordered hits equal the expected tree-order list, exactly; and the
  test's own guard asserts `tree_order != dict_order` on its fixture. Executed pre-state (**M-7**),
  query `"riesgo"`: dict order `['riesgo-root','b','c','d','e']`, tree order
  `['riesgo-root','b','d','e','c']` — they differ at position 3, so the guard holds.
- **Acceptance criteria:** the self-guard is what stops this test passing on a fixture where the two
  orders coincide, which is the shape of vacuous check C-55 limb 2.

##### LLR-N07.3.2 — the empty-result state is observably distinct

- **Traceability:** HLR-N07.3
- **Statement:** If a submitted query matches no node, then the system shall paint the count line
  reading `0 coincidencias` at the same position a non-zero count occupies, shall repaint the query
  chip in the muted tone, shall paint the hint line reading `sin coincidencias · esc limpiar`, and
  shall paint no node with the hit style.
- **Touched symbols:** the count-line construction in `mapper/app.py::MapScreen` —
  `NEW — created in Phase 3`; it uses `mapper/darkside.py::MUT` (`darkside.py:16`, `#737373`).
- **Reconciled against `01b-ux-decisions.md` DECISION 4 state E1 — this requirement's first draft
  was WRONG and is corrected here.** The draft painted the empty count line in `WARN`. The ux lens
  ruled that out with an argument the draft had missed: **`WARN` is the tone that means *a hit*, so
  an empty result must not borrow the hit colour.** Painting "nothing found" in the same hue as
  "found something" is a distinctness claim that inverts its own meaning. The audit row is
  §6.4 D-1.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_search.py -k "empty_result_is_distinct"`
  *(provisional)* — compare the painted text and its style spans for a matching and a non-matching
  query.
- **Numeric pass threshold:** the painted numerals differ; at least 1 style span differs; **0** nodes
  are painted with the hit style.
- **Acceptance criteria — how the distinctness is observable:** two independent channels, text and
  tone, are asserted, because a distinctness claimed only in prose is the vacuous-acceptance trap the
  story's own verdict names. **~~Severity is the declared job of `WARN` (LLR-S06.3.4), and "your
  query found nothing" is a severity, so this use is consistent with the census.~~ SUPERSEDED —
  this sentence is stale pre-D-1 text arguing for the very tone D-1 removed, and it survived inside
  the LLR D-1 corrected (`QA-B-08`, §6.5 A-10).** *Severity* is the **family** both severity tokens
  belong to, not a job: it cannot tell `WARN` from `ALERT`, and as a job statement it would license
  painting the empty result in either. `LLR-S06.3.5` declares one job per token. Under it, a query
  that completed with an empty answer is **neither** outstanding attention **nor** failure or
  blockage — it is a finished question with an empty answer — so `MUT` is the correct tone and
  **D-1's conclusion stands on a corrected reason**. This use is consistent with the census, and it
  is consistent for a reason that survives execution.

##### LLR-N07.3.3 — a whitespace-only query is not a match-everything

- **Traceability:** HLR-N07.3
- **Statement:** If the submitted query contains no non-whitespace character, then the system shall
  treat no node as a hit and shall paint no count line.
- **Touched symbols:** the query normalisation in `mapper/search.py::SearchIndex.query`
  (`search.py:13`).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_search.py -k "blank_query"` *(provisional)*.
- **Numeric pass threshold:** hit count `== 0` for the empty string and for a whitespace-only string;
  **0** nodes painted with the hit style.
- **Acceptance criteria:** `Graph.search_hits("")` today returns **every** node, because the empty
  string is a substring of every haystack (`model.py:169-184`, `if q in hay`). Executed at draft
  (**M-15**): `search_hits("")` returns **all 6** ids of a 6-node graph, and `search_hits("   ")`
  returns all 6 as well. **A blank query lighting the whole map is the current behaviour**, and this
  LLR is what stops the count line inheriting it.

##### LLR-N07.3.4 — one regime, not two: an active search is declared and clearable at every graph size *(NEW — `#D43`, 2026-08-29 · Inc-4c)*

- **Traceability:** HLR-N07.2, HLR-N07.3, US-N06 (the no-hidden-state through-line), `#D38`
- **Statement:** While a submitted query is active, the system shall declare it **at every graph size,
  including sizes at which the renderer declines to paint highlights**, as follows:
  1. **Where highlights and the walk are live** — the count region shall paint the whole-graph match
     count, and the hint line shall name the chords that traverse the matches. These are the shipped
     `HLR-N07.2` and `UX-Q3-b` surfaces and this requirement changes **neither**.
  2. **Where they are suspended** — the count region shall additionally name **the query itself** and
     shall name **what is suspended**.
  3. Pressing `esc` while a query is active shall clear that query and remain on the map,
     **identically at every graph size**.
- **RE-SCOPED 2026-08-29 AT THE GATE — the orchestrator's own amendment OVER-CORRECTED and contradicted
  this requirement's own predicate 3 (`CR-F3`).** The previous wording required the declaration to name
  the query and the chord *at every graph size*. Below the bound the region paints
  `{at}/{len(hits)} coincidencias en el mapa`, which names **neither** — and predicate 3 requires
  exactly those shipped strings to stay unchanged. **The clause instructed a future implementer to do
  what its own threshold forbids.** Two errors on one Statement in two days, in opposite directions:
  first requiring a *false* painting above the bound, then requiring a *changed* painting below it.
  Both were caught by a reader who executed the clause against the tree instead of reading it for
  sense, which is the only method that finds this class.
- **AMENDED 2026-08-29, AT THE GATE — the first draft of this Statement would have FORCED A FALSE
  PAINTING, and the implementer refused it (`F-1`).** The parked wording required the region to
  declare *"that the walk chord traverses it"* **unconditionally**. Above `MAX_RENDER_NODES` that is
  **false**: `_search_order` returns `None` there — Inc-4a's own deliberate separation of *unanswered*
  from *answered zero* — so `_walk_hits` has nothing to walk and `n` does **not** traverse. Painting
  `n recorre` above the bound would be a lying affordance: **the exact defect `#D43` was issued to
  remove, reintroduced by the requirement written to remove it.**
  **This is the orchestrator's error, recorded rather than absorbed.** The clause was written as a
  universal without checking whether the walk survives above the bound — it does not, by an earlier
  increment's design. The honest declaration names **both** suspensions, and that is what ships.
  Refusing to implement a requirement that would make the product lie is the correct response to a
  bad requirement, not a shortfall against it.
- **Why this requirement exists — it CORRECTS a behaviour `Inc-4b` shipped and its gate approved.**
  Above `MAX_RENDER_NODES` the count line went silent (correctly — `0 coincidencias` over a graph
  holding real matches is a lying affordance) and `esc` therefore popped the screen on the first
  press, because the unified `_search_is_live()` predicate reads the resolution rather than the query.
  Both gates ruled that resolution correct **on the premise that nothing was painted to clear**.
  `#D43` rejects the premise instead of the conclusion: the fix is to **paint it**, not to make the
  chord inconsistent.
- **The two defects this closes, stated as the operator experiences them:**
  1. **Hidden state.** The query survives in `query_text` and still changes what `n` does — `n` toasts
     `búsqueda sin evaluar` rather than `sin búsqueda activa` — while **no surface advertises it**.
     *Live enough to change a keypress, invisible enough to have no affordance* is precisely the
     hidden-state class US-N06 exists to remove.
  2. **A chord that varies with graph size.** `esc` clearing below the bound and popping above it is
     **a lying affordance with extra steps**: the operator learns a rule that silently stops holding
     on a large map, and learns it by losing their place.
- **Declared painted string (Spanish), shape not verbatim wording:** the region names the query, the
  whole-graph count, that `n` traverses it, and — when highlights are suspended — that they are, e.g.
  `búsqueda: «riesgo» · 241 coincidencias · n recorre · resaltado suspendido`. The chord glyph is read
  **from the seat**, per `UX-Q3-b`'s one-declaration-four-readers rule; the count is the whole-graph
  figure `HLR-N07.2` already owns.
- **The suspension notice is the load-bearing half.** Without it the operator sees a live count and an
  unlit canvas and has no way to learn why. Declaring the count without declaring the suspension
  trades one hidden state for another.
- **Validation:** `test (pilot)`
- **Numeric pass threshold — three predicates, all required:**
  1. **Above the bound with a live query**, the count region names the query, carries the whole-graph
     count `== len(SearchIndex(graph).query(q))`, and carries the suspension notice.
     > ⚠ **PARTIALLY CLOSED BY `Inc-STRIPS` (2026-09-10) — AGAINST THE FANOUT VECTOR ONLY. THIS
     > REQUIREMENT REMAINS OPEN.** `#map-minimap` and `#map-pagination` are bounded, and the count is
     > readable **in its own region** at both declared sizes on a genuine 12002-node graph with a
     > 4001-way root fanout, driven at the **shipped** bound rather than a moved one. Counterfactual
     > executed: both acceptance arms RED on the pre-fix tree.
     >
     > **THE TITLE-LENGTH VECTOR IS OPEN.** `TabStrip`'s crumb is a **fourth** unbounded strip on the
     > same screen and it takes a raw ficha title: measured, **one 4000-character title reproduces this
     > collapse verbatim** at 80x24 — canvas one row off-viewport, count region off-viewport. Routed to
     > `Inc-CRUMB`; the `open_blocks` entry flips only when **both** vectors are closed.
     >
     > ⚠ **A first version of this amendment marked the predicate `✅ CLOSED` with no qualifier**,
     > contradicting `state.json` in the same commit and reproducing — one file over — exactly the
     > premature-closure marking the security review had just blocked. Corrected here rather than
     > quietly: the artifact of record is the one that has to carry the qualifier.
     >
     > **"The three unbounded strips" is corrected too: there are FIVE** content strips outside
     > `#map-body`. This increment bounds two; `HintLine` and `KeyBar` were already bounded in Python;
     > `TabStrip` and `#map-toast` are `Inc-CRUMB`'s. See `increment-007-strips.md`.
     >
     > ⚠ **AMENDED 2026-09-10 — the stated measurement below described the wrong quantity at one of
     > its two sizes, and the correction is recorded here rather than separately.** Re-measured on a
     > genuine 12002-node graph: at **80x24** `rows_in` over `#map-pagination` returns **0 rows**,
     > exactly as written. At **118x34** it returns **10 rows** — the region is partially on-viewport
     > and **the count inside it is not**, because `_pagination_text` appends the count AFTER the meter
     > and only the meter's first rows are on the frame. **The sealed conclusion stands** (the count was
     > unreadable at both sizes; predicate 1 was satisfied only under a moved bound); what was wrong is
     > the quantity the note measured. **A region's visibility is not its content's visibility**, and
     > the acceptance predicate this increment ships asserts the count is readable in the composited
     > frame rather than that its region is on-viewport — the same trap, closed.
     >
     > **The superseded text follows, unedited, because a note that quietly becomes right teaches nobody:**
     >
     > ⚠ **SATISFIED UNDER A MOVED BOUND, NOT AT THE SHIPPED BOUND — and `Inc-STRIPS` is a BLOCKER on
     > closing this requirement, not a follow-up.** Both reviewers independently measured that at a
     > genuine 12002-node graph `rows_in` returns **0 rows** at 118x34 **and** 80x24: `#map-minimap`
     > renders ~668 rows over the root's 4001 children, crushing `#map-canvas` to one row and putting
     > the count region off-viewport. Every above-bound arm therefore reaches the branch by **lowering
     > the constant**, which drives the handler honestly but cannot observe the field frame.
     > **The two halves of this requirement close differently and must not be reported together:** the
     > `esc` half (predicate 2) is real and size-independent by construction; the **paint** half lands
     > where no operator can read it until the collapse is fixed. Recording predicate 1 as simply
     > "met" would be the `C-18` "covered in parts" defect wearing a measurement.
  2. **`esc` parity, asserted as one fact across two regimes.** With a query active, one real `esc`
     leaves `query_text == ""` **and** `app.screen is still the MapScreen` — asserted **both** below
     and above the bound, in the same node, so the two cannot drift apart. A second `esc` pops, in
     both regimes.
  3. **Below the bound the shipped strings do not regress** — `n/N coincidencias`, `0 coincidencias`
     and the empty-state hint are unchanged, and no suspension notice is painted.
- **Named weaker variant (`M-N07.3.4-a`):** declare the query above the bound but leave `esc` reading
  the resolution. Green on any test that only reads the painted region, and the chord still varies
  with graph size — predicate 2 is what reddens it, and only because it asserts both regimes in one
  node rather than in two that can be fixed independently.
- **Named weaker variant (`M-N07.3.4-b`):** paint the count above the bound without the suspension
  notice. Green on predicate 1's first two clauses; the operator still cannot learn why nothing is
  lit.
- **THIS CLAUSE OWNS COPY THAT PREVIOUSLY OWNED NOTHING.** `Inc-4b` shipped `búsqueda sin evaluar` /
  `el mapa supera el límite de <N> nodos` and the `abrió «…»` hint prefix as **new copy no `shall`
  clause owned** — declared as a risk at its gate rather than absorbed silently. `#D43` folds that
  risk: this requirement is the owner, and the strings are reconciled against it in `Inc-4c`.
- **Acceptance:** `AT-054`, `AT-055`

---

### 3.6 · US-N13 «sala» — home shows each map's own shape *(Inc-7 — §5.4)*

> **Header corrected (`P2-B1`, `QA2-C-06`, §6.5 A-49).** ~~*(Inc-6)*~~ was the **stale ARQ 7-cut**
> number, left live in this header while the ratified cut put US-N13 at `Inc-7`. Under §5.4 `Inc-6`
> is a **vacated** id. The cut is stated once, in §5.4, and this header points there.

> **What is new and what is not.** Executed (**M-12**): `HomeScreen.on_mount` already calls
> `store.load(map_name)` once per map (`mapper/app.py:539`) and keeps only `kind`, `nodos`, `docs`.
> Every datum this story asks for is computable from the `Graph` it already holds and throws away.
> The **welcome seat is partly shipped** — `_empty_text` (`app.py:554`) already paints the six-door
> copy and `on_mount` already displays it on an empty workspace. HLR-N13.2 is written as a
> regression guard, not as a new deliverable, so no pre-existing pass is counted as this batch's.
>
> **The `◍` repo marker is NOT here.** S-3b is `REFINE` pending Q-5; see §2.8.6.

#### Acceptance (black-box) — US-N13

- **Observable outcome:** returning to a workspace of several maps, the operator sees, per map and
  without opening anything, its shape, how documented it is, what is due, and whether it links
  elsewhere — and an empty workspace still shows the door in.
- **Shipped surface:** `HomeScreen` as composed by `MapperApp`, the screen the app opens on;
  observed through the rendered text of the home widgets (`#home-recents`, `#home-empty`,
  `#home-hero`, `#home-microbar`).
- **Deliverable + observation:** per map, a painted thumbnail whose lit-dot count equals that map's
  acta count, a fixed-width coverage bar, a node count equal to the graph's, a due badge when a node
  is due today, and a `⇄ n` marker when `n` nodes carry a map link; observed as substrings and
  character counts in the rendered text.
- **Acceptance tests:** `AT-025`, `AT-025b`, `AT-026`, `AT-029`, `AT-030`, `AT-031`.
- **`AT-027` and `AT-028` are DELETED (`QA-B-03`, §6.5 A-07).** They were pure padding: each
  appeared in exactly two places — this list and the §5.2 table — and nowhere else in the document.
  No requirement claimed either on an `Acceptance:` line and no predicate was written for either.
- **`AT-048` is DEFERRED (`#D24`, §6.5 A-43), not deleted.** It was `HLR-N13.3`'s mount-budget arm
  and its whole subject is the deferred threshold 1. It leaves with the budget mechanism and is
  enumerated in `HLR-N13.3`'s deferral record. **The distinction from `AT-027` / `AT-028` matters:
  those two never had a predicate; this one has a good predicate whose mechanism moved.**
- **Boundary catalog (QC-3):**
  - ☑ **empty** — `AT-030` drives a workspace with zero maps; `AT-025` includes a map with zero
    documented nodes (`nomina` from `create_seed`, executed: 0 of 3 — **M-12**).
  - ☑ **boundary** — `AT-026` drives `count == 0` and `count == total`, the two ends of the bar, and
    asserts the painted width is constant at both.
  - ☑ **invalid** — `AT-031` drives a map whose title carries Rich markup, a constructed control byte
    and a right-to-left override (risk A-7 — map titles are file-derived text reaching a new sink).
  - ☑ **error** — **split into two on-disk nodes (`QA-M-12`, §6.5 A-37).** `AT-025` was claimed for
    the thumbnail, the zero-documented map **and** a map whose load raises. The error case needs a
    **different workspace and a poisoned file**; it cannot be the same on-disk node as the happy
    path, and a single id claiming both is an id that cannot be realised (C-18). Now:
    - `AT-025` — the happy path: thumbnail, coverage bar, node count, on a two-map workspace;
    - `AT-025b` — the error path: a workspace holding one loadable map and one whose `.mmd` carries
      a directed cycle, asserting `LLR-N13.1.5`'s two clauses (painted card count `== 2`, and the
      damaged card distinguishable from a healthy empty concept map).

    The parked cell's justification — *"matching the existing `except Exception` fallback at
    `app.py:551`"* — is **superseded**: re-executed at `d877784`, that fallback is the recents
    loop's `else` arm at `app.py:566-567`, and it produces the misdeclaring row `LLR-N13.1.5`
    exists to forbid, not an acceptable outcome to match.

#### HLR-N13.1 — each map card shows that map's own shape

- **Traceability:** US-N13
- **Statement:** While the workspace holds at least one map, the system shall paint for each map a
  thumbnail whose lit-cell count equals that map's count of nodes carrying an acta, a coverage bar of
  fixed width, and a node count equal to the number of nodes in that map's graph.
- **Rationale (informative):** the value is that the operator chooses where to work without opening
  anything. Every input is already in hand — the story costs one loop body, not a new load.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_home.py -k "map_card_shape"` *(provisional)* — a
  workspace holding `fixtures/legacy` and a seeded map, driven through `App.run_test`, reading the
  rendered text of the recents region.
- **Numeric pass threshold:** for `legacy`, lit cells `== 6` and total cells `== 8` and node count
  `== 8`; for a seeded map, lit cells `== 0` and total cells `== 3` and node count `== 3`. All four
  numbers executed at draft (**M-12**), derived from the fixture rather than typed.
- **Priority:** medium
- **Acceptance:** `AT-025`, `AT-026`, `AT-029`
- **Value reconciliation (C-36):** "acta" is the schema field key `D`, read as
  `ficha.fields.get("D", "").strip()` — executed at `mapper/app.py:379` inside `_map_metrics`, and
  labelled `documento` in `fixtures/legacy_nodos.yml`. The bar glyphs `█` and `░` come from
  `mapper/darkside.py::microbar` (`darkside.py:232`), whose output length always equals its `width`
  argument. The thumbnail's lit and unlit glyphs are `NEW — created in Phase 3`.

##### LLR-N13.1.1 — the card is built from the graph already loaded

- **Traceability:** HLR-N13.1
- **Statement:** The home screen shall compute every card datum from the graph object it already
  loads for that map and shall not load any map more than once per mount.
- **Touched symbols:** `mapper/app.py::HomeScreen.on_mount` (`app.py:439`), the recents loop at
  `app.py:536-552`; `mapper/app.py::HomeScreen._map_metrics` (`app.py:369`) — extended;
  a card-building helper — `NEW — created in Phase 3`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_home.py -k "one_load_per_map"` *(provisional)* —
  count calls into `MapStore.load` across one mount.
- **Numeric pass threshold:** load calls per map per mount `<= 1` for the recents loop. Note: the
  hero and resume rows load separately today (`app.py:459`, `:468`, `:494`), so the threshold is scoped to
  the recents loop rather than to the mount, and that scoping is deliberate — widening it would make
  this LLR a refactor of code the story does not touch.
- **Acceptance criteria:** the story's own feasibility argument is that the data is in hand; an
  implementation that re-loads makes home slower for a cosmetic gain.

##### LLR-N13.1.2 — the coverage bar reuses the shipped builder

- **Traceability:** HLR-N13.1
- **Statement:** The home card shall render its coverage bar through the design module's existing
  microbar builder at a declared fixed width.
- **Touched symbols:** `mapper/darkside.py::microbar` (`darkside.py:232`, executed — signature
  `microbar(count, total, width=10, fill=INK) -> Text`; `filled = 0` when `total <= 0` or
  `count <= 0`, else `max(1, round(count/total*width))`).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_home.py -k "coverage_bar_width"` *(provisional)*.
- **Numeric pass threshold:** painted bar length `== 10` for every map, including a map with 0
  documented nodes and a map with all nodes documented. Executed (**M-12**): `microbar(6, 8, 10)`
  emits `'████████░░'` (length 10); `microbar(0, 3, 10)` emits `'░░░░░░░░░░'` (length 10).
- **Acceptance criteria:** a fixed-width bar is what makes the cards comparable down a column; the
  builder already guarantees it, so this LLR is a reuse assertion rather than new arithmetic.

##### LLR-N13.1.3 — one definition of coverage percentage

- **Traceability:** HLR-N13.1
- **Statement:** When a map's schema declares no required field, every surface that states a coverage
  percentage for that map shall state the value **100**, and shall state the same value as every
  other such surface.
- **Touched symbols:** `mapper/app.py:379` — `pct = int(100 * have / max(1, req))`, **corrected** to
  agree with `mapper/views/layered.py:179` and `mapper/widgets/rail.py:274`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_home.py -k "coverage_pct_agrees_across_surfaces"`
  *(provisional)* — one schema-less graph, three call sites, one **pinned** expected value.
- **Numeric pass threshold — the value is PINNED, and this is `QA-B-07` (§6.5 A-08):**
  `pct(schema-less) == 100` at **every** consumer of `graph.coverage()`, **and** the consumers agree
  with one another. Both clauses are required; the agreement clause alone is satisfiable by a lie.
- **THE PIN IS WHAT STOPS THE PLAUSIBLE WRONG FIX.** The parked threshold was *"the three
  computations return the identical value"* with **no value pinned**. The plausible weaker commit —
  change the two correct sites to match the outlier — makes all three agree at **0** and ships
  *"0 % documentado"* on every schema-less map in the product. It passes an agreement-only test.
  Executed at `d877784` in this amendment session, with the addresses re-derived because **every
  parked address for this LLR was stale**:

  ```
  $ python -c "from mapper.model import Graph; g=Graph(); print(g.coverage())"
  schema-less coverage() -> (0, 0)

  mapper/app.py:379        pct = int(100 * have / max(1, req))        ->   0     <- the outlier
  mapper/views/layered.py:179  pct = round(100*have_total/req_total) if req_total else 100  -> 100
  mapper/widgets/rail.py:274   pct = round(have/req*100) if req else 100                    -> 100
  ```

  Parked addresses `layered.py:119` and `rail.py:149` no longer hold; the repair batch moved both.
  The **majority is 100 and the outlier is `app.py:379`** — `max(1, req)` turns an absent
  denominator into a real one and reports "0 % documented" for a map that has nothing to document.
  100 is the correct value on the merits: a map with no required field has no unmet requirement.
- **Named weaker variant (`M-N13.1.3-a`):** change `layered.py:179` and `rail.py:274` to
  `int(100 * have / max(1, req))`. Three sites, identical values, agreement clause green, product
  ships 0 % everywhere. The pin `== 100` is the only clause that reddens it.
- **Named weaker variant (`M-N13.1.3-b`):** special-case the schema-less map at the **home card
  only**, leaving the other two sites as they are. Passes any test that reads one surface. The
  cross-surface agreement clause is what reddens it — which is why **both** clauses stay.
- **Acceptance criteria:** the input set is **derived** — the test enumerates every consumer of
  `graph.coverage()` by walking the tracked product sources rather than naming them, so a fourth
  surface added later joins the check automatically. Executed today the derivation yields **3**
  consumers, at `app.py:378`, `layered.py:178` and `rail.py:273` (the `have, req = graph.coverage()`
  lines immediately above the three computations).
- **Scope note:** this is a **defect found at draft**, not in the brief. It is folded into US-N13
  because the sala's coverage microbar would otherwise inherit whichever definition it copies and
  ship a fourth disagreement. It is one expression on one line.

##### LLR-N13.1.4 — the due badge and the link marker are derived, never invented

- **Traceability:** HLR-N13.1
- **Statement:** The home card shall paint a due badge when at least one of that map's nodes carries
  a due date equal to today, and shall paint a link marker stating the number of that map's nodes
  that name a linked map.
- **Touched symbols:** `mapper/app.py::HomeScreen._map_metrics` — the `vencen` computation at
  `app.py:373-377`, executed: `ficha.fields.get("due", "").strip() == date.today().isoformat()`;
  `mapper/model.py::Node.linked_map_id` (`model.py:57-60`, executed — reads
  `ficha.fields.get("map", "").strip()` and returns it or `None`).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_home.py -k "due_badge and link_marker"`
  *(provisional)* — a graph with one node due today, one due yesterday, one with no due date; and a
  graph with two nodes carrying a map link.
- **Numeric pass threshold:** due badge painted for the first graph and **not** for a graph whose
  only due date is yesterday; link marker numeral `== 2` on the second graph and the marker absent on
  a graph with none. Executed pre-state (**M-12**) on the shipped fixtures: `vencen == 0` and linked
  nodes `== []` for both `legacy` and a seeded map — **the shipped fixtures exercise neither case**,
  so both fixtures are `NEW — created in Phase 3` and are counted in the increment's test budget.
- **Acceptance criteria:** the "not painted" arms matter more than the painted ones. A badge that
  appears unconditionally passes a presence-only assertion and tells the operator nothing.

##### LLR-N13.1.5 — per-map failure containment, with a card state that is not a lie

- **Traceability:** HLR-N13.1, HLR-N13.3, security condition **C-3** (`02b` S-03)
- **Statement:** When a map in the workspace cannot be loaded or cannot be summarised within the
  per-map budget of `HLR-N13.3`, the system shall paint a card for that map declaring it as such,
  shall paint the cards of every other map in the workspace unaffected, and shall not paint for
  that map a card whose fields are indistinguishable from those of a successfully loaded map.
- **Declared card state (Spanish, the string that ships):** `mapa dañado — ↵ ver por qué`.
- **Touched symbols:** `mapper/app.py::HomeScreen.on_mount` (`app.py:439`); its inner
  `load_or_notice` (`app.py:444-461`); the recents loop (`app.py:558-573`); the hero branch
  (`:481-492`); the resume branch (`:512-531`); the card-building helper —
  `NEW — created in Phase 3`.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_home.py -k "one_broken_map_costs_one_card"`
  *(provisional)* — a temporary workspace holding one loadable map and one map whose `.mmd`
  contains a directed cycle, mounted through `App.run_test(size=(140, 45))`.
- **Numeric pass threshold:** painted card count `== len(mmd_files)`, i.e. **2 of 2** on the
  two-map fixture; the broken map's card contains the declared damaged-state string; the loadable
  map's card carries its true node count; the broken map's card is **not equal** to the card a
  zero-node concept map produces; **and the difference is carried by a declared token or glyph, not
  by the string alone** (`PRED-VIS`, below).

- **`PRED-VIS` — THE INEQUALITY CLAUSE IS SATISFIED BY A TEXT-ONLY DIFFERENCE, AND THAT IS NOT WHAT
  THE SALA IS FOR (`UX2-C-09` limb 1, §6.5 A-69).** The damaged state is declared as a **string
  only** — no token, no colour, no glyph, in this LLR, in `HLR-N13.3`, or in `01b`'s home vocabulary
  rows. **Every other state in the batch carries one.** The sala's entire purpose is choosing where
  to work **without opening anything** — it is scanned, not read — and *"a card that differs only in
  text differs only to someone already reading it."* Reproduced with a healthy-empty control:

  ```
  workspace: roto (cycle) + sano (2 nodes) + sano_vacio (healthy, 0 nodes)
    row: ['roto',       ' concept ', '0', '0']
    row: ['sano_vacio', ' concept ', '0', '0']      <- byte-identical as painted
  ```

  **`roto` and `sano_vacio` paint identically**, and the notice that distinguishes them is a
  **transient toast** while the card is **permanent** — after the toast clears there is no trace at
  all. The parked inequality threshold passes on this frame the moment the string lands, so the
  clause needs the visual limb or it certifies the defect.
- **`PRED-VIS` RESOLVED (`PDR-addendum-3#D27` + `#D28`): a DECLARED GLYPH, painted `INK on PANEL`.**
  **No colour token is spent** — executed, there is no unspent one: `SAGE`, `TEAL` and `VIOLET` are
  each already jobbed in `01b` §3.4/§3.5, and `ALERT` is free only because the malformed-query chip
  travels with the **cut** lens, which is **C-55 limb 2** — an emptiness that is an accident of this
  batch's scope. Spending it hands the follow-on batch a two-job token and an unadjudicable
  `LLR-S06.3.5` census.
  - **`INK`, not `MUT on PANEL`.** `MUT on PANEL` measures **`3.57 : 1`** against this batch's own
    `4.5 : 1` floor, and the damaged card's copy invites an action (`mapa dañado — ↵ ver por qué`),
    so it is **readable, load-bearing text**, not a passive status. `#D28`'s rule applies:
    `MUT`-on-`PANEL` readable text escalates to `INK`.
  - **`PRED-VIS` MEMBERSHIP CLAUSE — the glyph shall be a member of `declared_vocabulary`, asserted
    at run time.** Without it the derived-set test cannot see this: `LLR-N16.2.1` asserts what the
    **legend** paints, not what the **card** paints, so `Inc-7` could paint a bare `!` and **every
    arm stays green**. The clause closes that with one predicate and leaves `C-D27b` intact — the
    codepoint is still not fixed here, it is drawn from the declared vocabulary by the increment
    that paints it.
  - **`C-D27e` — a legibility arm measured against the background it actually paints on**, at the
    declared context of use **118 × 34**. `PRED-4`'s floor was breached by a clause four lines under
    its own measurement; this arm is what stops the same shape recurring on the card.
  - **`C-D27d` is a THRESHOLD, not a note:** assert `roto`'s painted non-name cells differ from
    `sano_vacio`'s, keeping `sano_vacio` as the known-healthy control. **For the `S-22` class there
    is no toast at all**, so the glyph is the *only* signal — which is why the `Inc-REPAIR` → `Inc-7`
    sequencing is load-bearing rather than tidy.
- **⚠ THE TOKEN THIS WANTS IS `ALERT`, AND TAKING IT HAS A DECLARED COST.** `LLR-S06.3.5` gives
  `ALERT` the job *failure or blockage — this item cannot proceed as it stands*, which fits exactly.
  **But `01b` §3.5 records the rule that if `ALERT` acquires a second job it must acquire a row in
  `colores con empleo`** — and `LLR-N14.1.3`'s malformed-query chip already argued `ALERT` keeps
  **one** job. **This requirement does not silently spend that token.** It requires *a* declared
  token or glyph and **routes the choice** to the PDR/ux lane with the cost stated: choosing `ALERT`
  adds a colour row to the legend vocabulary and therefore changes `LLR-N16.2.1`'s derived set.
- **⚠ LIMB 2 — THE PILOT SIZE IS WRONG FOR THIS ARM (`UX2-C-09` limb 2).** This LLR and `HLR-N13.3`
  both declare `App.run_test(size=(140, 45))`; **the declared context of use is 118 x 34.** The
  damaged-state copy is the longest string any card carries, and whether it survives at 118 columns
  is measured by **no declared arm** — the ux lens marked this limb `✗ Not executed` precisely
  because the card layout does not exist until `Inc-7`. **This arm shall run at 118 x 34**, or at
  both sizes. *(A character count for the copy is deliberately **not** written here: the two
  available figures disagree by one, and a hand-counted glyph total in a document that has shipped
  four wrong counts would be the fifth. The test measures the painted row.)*
- **Glyph note, recorded because one glyph is doing two jobs on one screen:** `↵` in this card means
  *"explain the failure"*, while `↵` everywhere else on home means *"open the map"*. `Inc-7` shall
  declare which action fires on a damaged card. The Spanish copy itself is judged good and is
  unchanged.
- **THE PARKED PREMISE EXECUTES FALSE, AND THE EXECUTED RESULT GOVERNS (§6.5 A-04).** `PLAN.md`
  §12.4 and `02b` S-03 both state that `load_or_notice` *"toasts and returns `None`, so a refusable
  map produces a notification and **no card at all**"*. Re-executed at `d877784` in this amendment
  session, against a real workspace under `App.run_test`:

  ```
  workspace: bueno.mmd (acyclic, 3 nodes) + roto.mmd (a --> b --> c --> a)
  screen mounted without raising : True
  row_count                      : 2
     row: ['bueno', ' concept ', '3', '0']
     row: ['roto',  ' concept ', '0', '0']
  ```

  A card **is** painted for the refusable map. The recents loop's `else` arm
  (`app.py:566-567`) sets `kind, nodos, docs = "concept", "0", "0"` and then adds the row
  unconditionally at `:568-573`. **The failure is not omission, it is misdeclaration**: the card
  asserts that `roto` is a valid, empty concept map. The hero (`:481-492`) and resume (`:512-531`)
  branches *do* silently vanish, so both failure modes are live — but they are different failures
  and the requirement above names both.
- **This correction MOVES the threshold, and that is why it had to be executed.** `M-H1`'s
  threshold as `02b` states it — *"painted card count, not 'the screen did not raise'"* — is
  **already green at `d877784`**: 2 maps in, 2 rows out. A requirement written to that threshold
  alone would pass on the shipped defect. The threshold is therefore **painted card count AND
  per-card state distinguishability**, and the distinguishability arm is the load-bearing half.
- **Named weaker variants, each stated at authoring time:**

  | Mutant | Plausible because | Reddened by |
  |---|---|---|
  | **M-H1** one `try/except Exception` around the whole card loop | it is the smallest edit that makes the screen survive | painted card count `== len(mmd_files)`. Executed in `02b` A5.4: 6 maps in, **0** cards out. |
  | **M-H1b** keep today's `else` arm and add nothing | it already satisfies *"a card is painted"* and *"the screen did not raise"* | the distinguishability arm — `['roto',' concept ','0','0']` is byte-equal to a legitimate empty concept map's row, executed above |
  | **M-H4** paint the damaged state as a **toast only**, as `load_or_notice` does today | the operator *is* told | the card-state assertion: a toast is not a card, and it is gone on the next repaint |

##### LLR-N13.1.6 — the sala loads at most once per map per mount

- **Traceability:** HLR-N13.3
- **Statement:** The home screen shall not call `MapStore.load` more than once for any single map
  during one mount, and shall not perform a per-map filesystem scan whose cost grows with the
  number of maps multiplied by the activity window.
- **Touched symbols:** `mapper/app.py::HomeScreen._sparkline_text` (`app.py:415-437`, executed — a
  `for d in days` loop of 14 iterations, each running `store.workspace.glob("*.mmd")` and a
  `stat()` per file, i.e. `14 x N_maps` stat calls per mount); `mapper/store.py::MapStore.load`
  (`store.py:249`), which calls `_reindex` (`store.py:372`) and **writes** to SQLite per load;
  `mapper/store.py::MapStore.list_maps` — `NEW — created in Phase 3` (P-15).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_home.py -k "sala_scans_the_workspace_once"`
  *(provisional)* — count `MapStore.load` calls and `Path.glob` calls across one mount.
- **Numeric pass threshold:** `load` calls per map per mount `<= 1`; workspace `glob` calls per
  mount `<= 2` (pre-state executed at `d877784`: the sparkline alone issues **14**, at
  `app.py:421`, inside the day loop).
- **`MapStore.list_maps` shall expose a CACHED metrics read (C-11, `02b` S-13, §6.5 A-40).** P-15
  proposes `list_maps`; this LLR requires that the sala can draw its thumbnails **without
  reindexing the workspace**. Executed: `store.load` calls `_reindex` (`store.py:372`), which opens
  a SQLite connection and **writes** per map per mount. `02b` measured 200 trivial maps at cold
  **1 064.2 ms** / warm **253.5 ms**, and warm is faster only because the text hash matches and
  `_reindex` short-circuits — **the first mount after any edit pays full price**, so a warm
  measurement is not evidence the mount is cheap.
- **`LLR-STO.1.1` IS RESOLVED — AND IT IS NOT PHANTOM. IT IS A CROSS-BATCH REFERENCE THIS DOCUMENT
  NEVER DECLARED (`S-17`, `QA2-C-03`, `C-2b`, `S-11`; §6.5 A-57).**

  > **`LLR-STO.1.1` — every serialised text position is coerced.** Defined at
  > `.dev-flow/2026-08-27-repair-batch-02/01-requirements.md:114`. Statement: *"`MapStore.load`
  > shall apply the scalar-coercion ladder to every text position enumerated by
  > `MapStore._build_sidecar`, and shall raise only `MapStoreError` for any input it rejects."*
  > Four thresholds; parent `HLR-STO.1`; verified by `tests/test_repair_store_boundary.py`.
  > **Shipped and implemented.** This document **references** it and does not redefine it.

  **THE DIAGNOSIS IN EVERY PRIOR LENS WAS RIGHT ABOUT THE SYMPTOM AND WRONG ABOUT THE CAUSE, AND THE
  DIFFERENCE DECIDES THE FIX.** Executed at `ea1fbf9`:

  ```
  $ grep -rn "^#\+ .*LLR-STO" .dev-flow/
  .dev-flow/2026-08-27-repair-batch-02/01-requirements.md:114
  .dev-flow/2026-08-27-repair-batch-02/03-increments/increment-001.md:1
  ```

  The heading exists. What does **not** exist is any declaration **in this document** that the id is
  external — so a reader of `01-requirements.md` alone, and every census run over it alone, correctly
  reports *"4 prose references, 0 headings"* and concludes the id is fabricated. **The security lens's
  78-heading enumeration was accurate; its inference was not.** The defect is a **missing reference
  declaration**, not a missing requirement.

  **AUTHORING A SECOND `LLR-STO.1.1` BLOCK HERE WOULD BE THE WORSE REPAIR, AND IT IS THE ONE THE
  CONDITION AS WRITTEN ASKS FOR.** Two headings for one id is the two-live-definitions defect this
  batch removed for *"hit"* (`#D6`) and *"coverage"* (`#D14`) — and it would be strictly more
  dangerous here, because `mapper/store.py` cites the id **normatively in shipped code**. The two
  copies would drift, and the code would obey whichever the reader found first. **This document
  therefore follows the precedent it already set at §6.5 A-01**, which resolved `LLR-R04.1` as *"a
  reference, defined at"* the prior batch's document rather than restating it.
- **THE `S-11` HALF IS DISCHARGED BY THAT REFERENCE, VERIFIED RATHER THAN ASSERTED.** The statement
  this bullet demanded — *"`MapStore.load` shall raise only `MapStoreError`"* — **is** `LLR-STO.1.1`
  threshold 3, with the fixture set derived from `_build_sidecar`'s positions exactly as demanded.
  Its arms are parametrized over the derived position census, and the suite carries a
  **guard-versus-net distinguishability** arm, added because deleting the top-level type guard left
  every other arm green. `B-01`'s five exception types — `KeyError: 'path'`, two `AttributeError`s,
  two `sqlite3.ProgrammingError`s — are the **pre-fix** measurement and are retained as the
  historical pre-state, not as a live threshold. **Named weaker variant (`M-B1`), retained:** add a
  `.get("path", "")` default — survives the `KeyError` arm and leaves the other four.
- **A COUNT THIS DOCUMENT DECLINES TO ADOPT (rule: never a hand-maintained count).** The
  reconciliation reports *"**0 of 19** hostile inputs leak a non-`MapStoreError`"*. Executed, **that
  19 appears in exactly one artifact and is enumerated nowhere** — no input list backs it. The
  **derived** arm set for threshold 3 is the position census minus the key positions a container
  cannot occupy. **This document cites the derivation and not the 19**, because adopting an
  unaudited figure into a requirement is how the four wrong generations of the `AT` total began.
- **ONE PROPERTY THE TYPED NET DOES NOT BUY, RECORDED SO IT IS NOT OVER-CLAIMED.** `MapStoreError` is
  a bare `Exception` subclass (`mapper/store.py:17-18`), and **both real `load` callers catch bare
  `Exception`** — `mapper/app.py:450` in `load_or_notice`, and `mapper/app.py:1176`. So the typed
  refusal changes the **message** the operator sees; it does **not** change crash-resistance at any
  existing call site. `LLR-N13.1.5`'s containment depends on the **warning** channel, not on the
  exception type — which is why `LLR-REPAIR.1` (§3.9), not this reference, is what makes it engage.
- **`F-m4` is DISPOSITIONED as measured-and-closed, with one arm carried (C-12, `02b` S-14).** The
  YAML alias bomb is **not exploitable here**: bombs of 411 / 511 / 625 bytes at 8 / 10 / 12 alias
  levels load in **24.2 / 14.6 / 17.0 ms** at **0.0 MB** peak Python heap, because PyYAML aliases
  **share objects rather than deep-copying**, and `_graph_from_sidecar` reads only `schema`,
  `documents` and `nodes` — a bomb under any other key is never traversed. It has sat undischarged
  since PDR, and *"no disposition"* is what turns a measured non-issue into a recurring review cost.
- **THE CARRIED ARM IS THE ONE THING THE `LLR-STO.1.1` REFERENCE DOES *NOT* DISCHARGE, SO IT GETS A
  REAL HOME HERE (`C-12`, `S-14`; §6.5 A-58).** A bomb under `nodes:` **is** traversed. Verified at
  `ea1fbf9`: `_graph_from_sidecar` reads exactly three keys — `sidecar.get("schema")`,
  `sidecar.get("documents")` and `sidecar.get("nodes")` — and the `nodes` branch walks **every**
  entry, every `fields` map and every `attachments` list beneath it. The measured-and-closed
  disposition above rests on *"a bomb under any other key is never traversed"*, and `nodes:` is not
  any other key. **Executed: no test in the shipped boundary suite places a bomb under `nodes:`** —
  the nearest arms are a parser-recursion case and the malformed-shape family, neither of which is an
  alias bomb. **The arm is uncovered on every tree, in both batches**, and it has been carried
  forward as *"belongs in `LLR-STO.1.1`'s fixture set"* without anyone owning the fixture. It is
  written as an LLR below rather than carried a third time.

##### LLR-N13.1.7 — the traversed sidecar key carries the alias-bomb arm *(`Inc-REPAIR`)*

- **Traceability:** HLR-N13.1; security condition **C-12** (`02b` S-14); references
  `LLR-STO.1.1` (`.dev-flow/2026-08-27-repair-batch-02/01-requirements.md:114`)
- **Statement:** Loading a sidecar whose `nodes` key carries an alias-amplified structure shall
  complete within the same order of cost as the equivalent un-aliased sidecar, or shall be refused
  as a typed error, and shall not exhaust memory.
- **Touched symbols:** none in `mapper/` — this is a **fixture and threshold** obligation against the
  shipped `mapper/store.py::MapStore.load` nets. The fixture module is
  `NEW — created in Phase 3`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_repair_store_boundary.py -k "alias_bomb_under_nodes"`
  *(provisional)* — build sidecars whose `nodes:` value is alias-amplified at increasing levels,
  load each, and record wall time and peak heap through `tracemalloc`.
- **Numeric pass threshold:** peak heap over the bomb load stays within the same order as the
  un-aliased control, **and** the load either completes or raises `MapStoreError` — **0** untyped
  exceptions. **The un-aliased control is mandatory:** without it the arm passes on a bomb that
  PyYAML happened to share rather than expand, which is the measured behaviour for the *untraversed*
  keys and is exactly the reasoning this arm was carved out of.
- **Named weaker variant (`M-N13.1.7-a`):** reuse the existing under-an-unread-key bomb fixture and
  assert `0.0 MB`. **Green today and green forever** — that key is never traversed, so the assertion
  measures PyYAML's alias sharing and not this code path at all. Reddened by placing the bomb under
  `nodes:`, which is the entire content of this LLR.
- **Acceptance criteria:** the amplification measured on the untraversed keys was ×49 to ×73 at
  **0.0 MB** peak heap, and that is a real result — for those keys. Generalising it to the traversed
  one is the inference this arm exists to test rather than assume. **It is scoped as an obligation on
  the fixture set, not as a new bound**, because the count and work dimensions of "too big" are
  `MAX_RENDER_NODES` and the deferred `#D24` budget respectively, and a third definition here would
  re-create the defect `HLR-N13.3` was written to avoid.
- **Owning increment:** **`Inc-REPAIR`** (§5.4), which already owns `mapper/store.py`. This LLR adds
  **0** source files — tests are uncapped — so it rides at no budget cost, and keeping every
  store-boundary obligation in one increment avoids the two-owner collision `#D5` prevents.
- **Acceptance criteria:** this is the *count* dimension of the mount budget and it is the cheap
  half. It is stated separately from `LLR-N13.1.5` because a fix to one does not fix the other, and
  `HLR-N13.3` needs both.

#### HLR-N13.2 — the create door is never blank *(regression guard on shipped behaviour)*

- **Traceability:** US-N13
- **Statement:** While the workspace holds no map, the system shall paint the entry-action copy and
  shall not paint an empty panel.
- **Rationale (informative):** this behaviour **ships today** — `_empty_text` (`app.py:554`) and the
  `if not mmd_files` branch (`app.py:519-524`). The requirement exists so that the per-card work of
  HLR-N13.1, which rewrites that loop, cannot remove it. Recorded plainly as a guard so nobody counts
  a pre-existing pass as this batch's contribution.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_home.py -k "empty_workspace_shows_the_doors"`
  *(provisional)* — `App.run_test` against an empty temporary workspace.
- **Numeric pass threshold:** the empty region is displayed; the recents table is not; the painted
  text contains all **6** door labels. Executed at draft, the six on disk (`app.py:555-575`):
  `consult`, `repo`, `construct`, `template`, `import`, `factory`.
- **Priority:** low — it is a guard, and its pre-state is green.
- **Acceptance:** `AT-030`
- **Recorded honestly:** this test passes on `master` today. It is a **regression guard**, and its
  non-trivial arm is the mutation in `AT-030` that deletes the empty branch and must turn it red.

##### LLR-N13.2.1 — map titles reaching the home card are coerced

- **Traceability:** HLR-N13.1, HLR-N13.2, risk A-7
- **Statement:** The system shall coerce every map title and every node title placed into a home card
  through the design module's plain-text coercion.
- **Touched symbols:** `mapper/darkside.py::plain` (`darkside.py:276`); the card construction in
  `mapper/app.py::HomeScreen` — `NEW — created in Phase 3`.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_home.py -k "hostile_map_titles"` *(provisional)* —
  a workspace whose map file names and node titles carry Rich markup, a control byte constructed from
  its code point, and a right-to-left override.
- **Numeric pass threshold (C-4, §6.5 A-13):** measured **on the painted row** — **0** occurrences of
  any code point in `COERCION_RANGES` (§3.0); **0** Rich markup tags interpreted; the painted card
  row length equals the declared card width for every hostile input; the **split-at-width arm**
  passes; and the screen mounts without raising for every hostile input.
- **Acceptance criteria — the three `app.py` `escape()` sites are now IN SCOPE (C-7, §6.5 A-15).**
  ~~"scoped to the sink class — every **new** home text sink"~~, with the recents-row and resume-row
  `escape()` calls *"explicitly out of scope"*, is **superseded**. `02b` S-08's point is that a
  requirement scoped to what this batch creates ships the identical defect in the sink beside it —
  and `HLR-N13.1` **rewrites the very loop those calls sit in**, so they are on a touched surface by
  the batch's own definition.

  **The parked addresses were stale; re-derived at `d877784` in this amendment session:**

  ```
  $ grep -n "escape(" mapper/app.py        # HomeScreen sites only
  parked :503, :505  ->  now  app.py:524, :526   (resume row: map_id and node_name)
  parked :547        ->  now  app.py:568         (recents row: map_name)
  ```

  These three are in scope. They are **named here as evidence, not as the census**: the gate is the
  derived census of `LLR-N06.2.3`, which finds them by walking the tracked sources for file-derived
  values placed into painted renderables on a touched surface. A hand-listed set of three line
  numbers would go stale again the moment the loop moves — which is exactly what happened to the
  parked ones, and is `C-31`'s whole argument.

  **Still out of scope:** legacy `escape()` sites on surfaces this batch does not touch (carry
  B-03) — the inspector block at `app.py:242-293`, the palette table at `:205`, the layered ghost at
  `layered.py:266`.
- **Acceptance:** `AT-031`
- **`AT-031`'S OWNERSHIP IS LANDED HERE (`P2-B2`, `QA2-C-01`, §6.5 A-44).** §6.5 A-29 dispositioned
  `AT-031` as *"remains catalog-only and is **recorded here as such** rather than counted as
  specified"* — an honest record, but it left a live `AT` on a live story with no requirement above
  it, which §3.6's own boundary catalog (`:2247`) describes as *"a map whose title carries Rich
  markup, a constructed control byte and a right-to-left override"*. **That is this LLR's statement,
  word for word.** The id was never homeless; it was unclaimed. Claiming it here converts a coverage
  clause into a predicate with a fixture, a threshold and a named weaker variant, which is exactly
  what A-29 said a catalog clause is not.
- **Named weaker variant (`M-N13.2.1-a`):** coerce the new card fields, leave `escape(map_name)` at
  `app.py:568` as it is. Every new field is clean and the map-name column on the same row carries
  the override, which then governs the columns painted after it. Reddened by the derived census.
- **Byte-hygiene note:** the control byte is constructed from its code point at test time and is
  never spelled into a source file or into an evidence artifact.

#### HLR-N13.3 — the sala paints within a declared budget, and an unsummarisable map says so on its own card

- **Traceability:** US-N13, security condition **C-3** (`02b` S-03, `[blocker]` — the one security
  blocker still live after the repair batch; `PLAN.md` §12.5 D18 discharges C-1 and C-2 and
  **explicitly does not discharge C-3**)
- **Statement:** While the workspace holds maps, a map that cannot be summarised shall be declared as
  such on its own card, and every other map in the workspace shall still paint its own card with its
  own true values.

> ### THE WORK-BUDGET HALF IS CUT — `S-18` and `S-19` go together to the follow-on design batch (`#D24`, §6.5 A-43)
>
> **The pairing is the ruling, and it is not a sibling pairing: `S-19` is `S-18`'s PRECONDITION.**
> `S-18` asks for a render work budget; `S-19` is the measurement that would calibrate it. Executed
> on the 51-node / 410-edge shape, `02g` §4.3:
>
> ```
> LayeredRenderer  1283 ms      over the 250 ms budget
> OutlineRenderer   337 ms      over the 250 ms budget
> RadialRenderer    142 ms      UNDER the 250 ms budget
> ```
>
> **`RadialRenderer` is under budget on the acceptance fixture, so on that renderer `k = 0`.** With
> `k = 0`, threshold 4's containment arm quantifies over an empty set and threshold 2 asserts nothing:
> a correct implementation and a **missing** one paint the identical screen. The budget mechanism is
> therefore **unfalsifiable on one of the three renderers the fixture may be run against**, and the
> fixture as written does not say which renderer it runs. That is C-55 limb 1 — an absence admitted
> as evidence without a positive control proving the oracle can produce a non-absence.
>
> **The obligation the follow-on batch inherits, stated as a gate and not as advice:** its budget
> fixture **shall name its renderer**, and shall carry a renderer for which `k > 0` on the declared
> shape, with the `k = 0` renderer retained as the negative control. A budget fixture that does not
> name its renderer is not a fixture; it is three different experiments sharing a name.
>
> **What this disposes, said explicitly rather than left to be inferred:**
> - **`P2-C8`** — *"`< 1000 ms` for 200 maps is an absolute wall-clock assertion with no stated
>   headroom"*. **DISPOSED by the cut**: threshold 1 leaves with the budget mechanism, so there is no
>   longer an un-headroomed wall-clock assertion in this document. It is not answered; its subject is
>   gone. The follow-on batch inherits the headroom question with the budget.
> - **Security `C-3`** — threshold 2 *"measured as elapsed time"*, and the missing threshold 5.
>   **DISPOSED by the cut on the same ground**: `C-3`'s subject is threshold 2, which is deferred.
>   **What is NOT disposed and must not be read as disposed:** the *defect* `S-15` / `M-H3` is real,
>   measured twice, and stays on `master` — a 73-node map costs 72.5 s and `MAX_RENDER_NODES` waves
>   it through. **Deferring the bound does not repair the defect.** It is carried, named, to the
>   follow-on batch, and `.dev-flow/BACKLOG.md`'s lane owns that carry. Recording a live app-killing
>   defect as "disposed" would be the exact false record §3.0's own byte-hygiene note exists to stop.
>
> **What survives in this HLR, and why it survives the cut:** thresholds 3 and 4 below need **no**
> budget mechanism. Threshold 3 consumes `MAX_RENDER_NODES`, which is shipped and enforced.
> Threshold 4's containment is re-scoped from *"exceeds the per-map budget"* to *"fails to load"* —
> a condition `LLR-N13.1.5` already owns, `AT-025b` already drives on a real poisoned fixture, and
> which is observable with no timing at all.
- **Rationale (informative):** US-N13 is what turns *"the operator opened a hostile map"* into
  *"the operator started the application"* — the sala loads and summarises **every** map in the
  workspace before any card paints. Without a bound, one file decides whether the product starts.
- **Validation:** `test (pilot)` + `test (unit)`
- **Executed verification:** `pytest tests/test_home.py -k "unsummarisable_map_is_contained"`
  *(provisional)* — mount `App.run_test(size=(140, 45))` against a workspace of one loadable map plus
  one map whose load fails, and read the painted card count and the two card states.
  *(~~"a workspace of 200 generated maps of `<= 128` nodes"~~ and ~~"one map that exceeds the per-map
  work budget"~~ are **DEFERRED (`#D24`)** with thresholds 1 and 2. The `-k` selector is renamed off
  `mount_budget` in the same breath, because a selector naming a mechanism this requirement no longer
  contains is how a deferred half gets re-implemented by accident.)*

- **THE BUDGET, EXPRESSED RELATIVE TO THE SHIPPED BOUND (D19).** `MAX_RENDER_NODES = 12000` is
  adopted as a given, not re-litigated: it is declared and enforced in all three renderers —
  `mapper/views/layered.py:15` enforced at `:143`, `mapper/views/outline.py:14` at `:65`,
  `mapper/views/radial.py:28` at `:117` — with a shipped test keeping the three values in step
  (executed by `grep -rn "MAX_RENDER_NODES" mapper/` in this amendment session). **This requirement
  declares no second node-count bound.** The count dimension of "too big" has exactly one live
  definition and it is `MAX_RENDER_NODES`.

- **`MAX_RENDER_NODES` IS ONE CONCEPT WITH THREE COPIES, AND THAT IS DECLARED HERE — WITHOUT
  CLAIMING IT IS FIXED (`S-20`, §6.5 A-59).** Executed at `ea1fbf9`, the constant is a **literal in
  three separate modules** with no shared home: `mapper/views/layered.py:15` enforced at `:143`,
  `mapper/views/outline.py:14` at `:65`, `mapper/views/radial.py:28` at `:117`. `mapper/views/lane.py`
  declares **none** — three of four renderers are bounded and one is not. The only thing keeping the
  three in step is a test that reads all three module attributes and compares them; **nothing keeps
  the fourth renderer in the conversation at all.**
  - **What this requirement asserts:** the three declarations are **one concept**, and a change to
    the count dimension of "too big" shall change **one** declaration. The shipped cross-check is
    the reason the values agree today, and it is adopted, not replaced.
  - **What this requirement does NOT assert, stated flatly so nobody reads a discharge into it:**
    **the duplication is not repaired in this batch, and neither is the cost it fails to bound.**
    Three modules carry five independent stack walks between them, and `Graph.children_of`
    (`mapper/model.py:149-150`) rescans **every** edge on every call — re-measured here at
    `ea1fbf9`, per-call cost doubles as `E` doubles, confirming O(E) per call and O(N·E) through
    `Graph.focus`, which is **not a renderer** and which `MAX_RENDER_NODES` therefore does not
    guard at all. Four modules already carry the identical comment describing the workaround, which
    is the clearest possible evidence that the shared helper is missing rather than unnecessary.
  - **The bound that would fix it is DEFERRED with `#D24`** and is carried in the backlog as
    **`B-33`**, together with `S-15`. **Deferring a bound does not repair a defect** — the same
    sentence `#D24` carries, applied to the same family, and repeated here because `S-20` and `S-15`
    are the two halves a reader is most likely to assume the other closed.

- **Numeric pass threshold:**
  1. ~~**Workspace budget.** Mount completes in `< 1000 ms` for **200** maps of `<= 128` nodes
     each.~~ **DEFERRED (`#D24`)** — leaves with the budget mechanism; disposes `P2-C8`.
  2. ~~**Per-map work budget.** `WORKSPACE_CARD_BUDGET_MS = 250` per map — a **work** bound measured
     as elapsed time of that map's summarise-and-render step, **not** a node count.~~
     **DEFERRED (`#D24`)** — this is the stall-bounding half, and it is the half `S-19` shows cannot
     be distinguished from its own absence on `RadialRenderer`. Disposes security `C-3`'s subject;
     **does not** repair `S-15`.
  3. **Count ceiling, inherited not invented — LIVE.** A map of `> MAX_RENDER_NODES` nodes is
     refused by definition and needs no timing; the renderers already refuse it and this requirement
     consumes that refusal rather than restating it. **Testable with no budget mechanism**, which is
     why it survives the cut.
  4. **Containment — LIVE, re-scoped from "over budget" to "fails to load" (`#D24`).** For a
     workspace of `N` maps of which `k` fail to load, painted card count `== N`, the `k` failing maps
     carry the declared damaged-card state, and the remaining `N - k` cards carry their true values.
     The `k` maps are identified by the **load path raising or recording a load warning**, never by a
     clock. `AT-025b` drives `N = 2`, `k = 1` on a `.mmd` carrying a directed cycle, so `k > 0`
     holds by construction and the arm is not vacuous — the property `S-19` shows the *budget*
     version could not guarantee.

- **THIS IS SHIPPED DEFECT `S-15`, NOT A PRECAUTION (`PLAN.md` §14.2, §6.5 A-25).** `M-H3` is
  promoted from a named hypothetical mutant to a **measured app-killing defect on `master`**, and it
  is recorded as `S-15` so the next reader knows the mount budget exists for a measured reason.
  **Independently reproduced twice** — this lane and the orchestrator's separately written probe,
  different graph builder and different call path, agreeing to within 3 %, because a finding this
  size may not rest on one measurement. Executed in this amendment session,
  `LayeredRenderer().render(g, w=80, h=24)` over a layered DAG in which each layer is fully
  connected to the next:

  ```
  w= 4 layers=4  nodes=  17  render=       4.4 ms   allowed by MAX_RENDER_NODES: True
  w= 6 layers=4  nodes=  25  render=      17.4 ms   allowed by MAX_RENDER_NODES: True
  w= 8 layers=4  nodes=  33  render=      65.5 ms   allowed by MAX_RENDER_NODES: True
  w= 8 layers=5  nodes=  41  render=     497.4 ms   allowed by MAX_RENDER_NODES: True
  w=10 layers=5  nodes=  51  render=    1935.7 ms   allowed by MAX_RENDER_NODES: True
  w=12 layers=6  nodes=  73  render=   72476.9 ms   allowed by MAX_RENDER_NODES: True
  ```

  For contrast, on shapes whose edge count tracks their node count the same renderer is fast:
  a 12 000-node chain renders in **186.3 ms** and a `d=7 b=3` tree of 3 280 nodes in **59.7 ms**.
  **A 73-node map costs 72.5 seconds and `MAX_RENDER_NODES` waves it through**, because 73 is
  comfortably under 12 000. Node count grows linearly; **path count grows multiplicatively**, and
  the renderer's traversal is keyed on paths. This is the executed proof that the budget must bound
  **work**, and it is why threshold 2 is a millisecond figure rather than a node figure.
- **The acceptance fixture is the 51-node shape; the 73-node shape is the demonstration.** At
  ~1.9 s it is unambiguously over any sane budget while staying fast enough to run in a suite.
  **A 70-second node has no place in a gate.**
- **`MAX_RENDER_NODES` IS NOT REPLACED AND NOT RE-LITIGATED (D19) — the work bound is ADDITIONAL,
  and this sentence is the one that stops the batch shipping two definitions of "too big".** The
  count ceiling stays exactly as shipped and this requirement consumes its refusal (threshold 3);
  the work bound (threshold 2) sits beside it and bounds a different dimension. Stated explicitly
  because *"we added a bound"* read as *"we replaced the bound"* is how a second live definition
  gets created, which is the defect `D6` removed for *"hit"* and `D14` for *"coverage"*.
- **CORRECTION — `02b`'s renderer timings must not be quoted (§6.5 A-25).** `02b` S-03 measures
  *"3.4 s at n=3280, 9.1 s at n=10 000"*. Those are **pre-repair** figures; re-executed at
  `d877784` the same shapes are **59.7 ms** and well under a second. **The conclusion survives and
  the numbers do not**: the cost did not go away, it moved into a shape nobody had measured.
  Quoting the old figures would understate the live defect while appearing to cite evidence.

- **Named weaker variants, each stated at authoring time. Four of the five were reddened by
  threshold 2 alone and therefore leave with it (`#D24`) — recorded, not dropped:**

  | Mutant | Plausible because | Reddened by | Status after `#D24` |
  |---|---|---|---|
  | **M-H1** one `try/except Exception` around the whole card loop | smallest edit that stops the crash | threshold 4 — painted card count `== N` | **LIVE.** Threshold 4 survives the cut, re-scoped to load failure, and this mutant is a load-failure mutant. `02b` A5.4: 6 maps in, 0 cards out |
  | **M-H2** cap the **number** of maps | a cap looks like a bound | ~~threshold 2~~ | **DEFERRED (`#D24`)** — carried to the follow-on batch with the bound it reddens |
  | **M-H3** compute the budget from `len(graph.nodes)` | node count is the obvious size proxy | ~~threshold 2~~ | **DEFERRED (`#D24`)** — and it is the mutant `S-15` proves is a live defect, so it is carried **named**, not discarded |
  | **M-H5** reuse `MAX_RENDER_NODES` as the *whole* budget | it is the shipped bound and D19 says adopt it | ~~threshold 2~~ | **DEFERRED (`#D24`)** |
  | **M-H6** measure the budget over the **hero** map only | the hero is the expensive one on the happy path | threshold 4 — the fixture's failing map is not the hero | **LIVE**, re-scoped: the two-map fixture of `LLR-N13.1.5` puts the failure on the non-hero map |

  **The four deferred mutants are the readable proof that threshold 2 carried real discriminating
  power.** Cutting it is a scope decision, not a claim that it was worthless, and writing that down
  is what stops the follow-on batch re-deriving them from nothing.

- **Priority:** high — it gates **Inc-7** (§5.4), the increment that rewrites the recents loop.
  *(~~"it is a security blocker and it gates Inc-6"~~ is superseded twice over: `C-3`'s subject is
  deferred by `#D24`, and `Inc-6` is a **vacated** id under §5.4 — the US-N13 increment is `Inc-7`.)*
- **Acceptance:** `AT-025b`
  *(~~`AT-048`~~ — **DEFERRED (`#D24`)**. `AT-048` was created solely as the mount-budget arm
  (`QA-M-12`, §6.5 A-37) and needed a generated 200-map workspace. Its whole subject is threshold 1.
  It leaves with the mechanism rather than being retargeted at a predicate it was not written for.)*
- **Owned LLRs:** `LLR-N13.1.5` (per-map failure containment, threshold = painted card count **and**
  card-state distinguishability) and `LLR-N13.1.6` (at most one load per map per mount).
- **`LLR-N13.1.5`'s containment DOES NOT ENGAGE on the current tree, and `LLR-REPAIR.1` (§3.9) is
  what makes it engage.** Recorded here because a requirement whose guard is a no-op is the defect
  this batch has already shipped twice: measured on a phantom sidecar id, `coverage() = (2, 3)` with
  `warnings = []`, so `load_or_notice`'s warning arm at `mapper/app.py:459` never fires and no card
  ever enters the damaged state. **`Inc-REPAIR` shall land before `Inc-7`** (§5.4), or `AT-025b`
  passes over a `k` that is structurally zero.
- **`AT-025` is promoted out of the boundary catalog.** `02b` S-03's structural complaint was that
  the only error statement in 2 707 lines was a boundary-catalog line with *"no HLR and no LLR
  behind it — an acceptance test with no requirement above it is a test the next refactor deletes
  without reddening anything."* `AT-025`'s error arm now sits under `LLR-N13.1.5`, and the new
  `AT-048` carried the budget arm, which `QA-M-12` correctly says cannot be the same on-disk node
  as the happy path: it needs a different workspace and a generated fixture. *(The `AT-025`
  promotion **stands** — its error arm still sits under `LLR-N13.1.5`, which survives `#D24` whole.
  The `AT-048` half is **DEFERRED (`#D24`)** with the generated workspace it required. `QA-M-12`'s
  finding — that one on-disk node cannot carry both — is unaffected and is the reason the two ids
  can be dispositioned separately at all.)*
- ~~**Flagged `assumed — verify in Phase 3`:** the two millisecond figures.~~ **DEFERRED (`#D24`)
  with the figures themselves.** Both millisecond figures leave with thresholds 1 and 2, so **this
  requirement now carries no `assumed` figure at all** and `P2-C8`'s subject is gone. The reasoning
  travels to the follow-on batch intact: they were wall-clock figures on one machine, they needed
  re-measurement on the CI runner before pinning, and `S-19` has since shown they also needed a
  named renderer. What is **not** provisional, and is the finding the follow-on batch starts from, is
  that the budget must bound **work** rather than node count — settled by the executed table above,
  which is retained here for that reason.

---

### 3.7 · US-N14 «lente» — ask the map a question about its fields — **DEFERRED**

> ## DEFERRED — follow-on design batch (`#D23`, amendment set 3 · A-42)
>
> **Reason:** the operator re-scoped this batch. US-N14's figure-ground half is a renderer change
> riding the same A3 contract as US-N06 (§2.6 S-4 records the coupling), and its walk half is still
> waiting on Q-7, which §2.8.4 records as **NEW and blocking**. It is design work, not
> implementation work, and it is moved whole to a follow-on **design** batch rather than carried
> half-specified through a third PDR iteration.
>
> **Pointer:** the follow-on batch inherits §3.7 verbatim, together with `01b-ux-decisions.md`
> DECISION 2, DECISION 3 §3.3 (the lens vocabulary rows), and Q-6 / Q-7 in §6.1. **No text below is
> deleted** — the work is good and the successor reads it as its own input. Where it lands is
> recorded in `.dev-flow/BACKLOG.md`, whose lane owns that record; this document does not name a
> batch id it cannot verify.
>
> **What leaves with this section, enumerated so nothing is dropped silently (C-56):**
> - **HLR:** `HLR-N14.1`, `HLR-N14.2`, `HLR-N14.3`.
> - **LLR:** `LLR-N14.1.1`, `LLR-N14.1.2`, `LLR-N14.1.3`, `LLR-N14.1.4`, `LLR-N14.2.1`,
>   `LLR-N14.2.2`, `LLR-N14.2.3`, `LLR-N14.3.1`, `LLR-N14.3.2`, `LLR-N14.3.3`.
> - **AT:** `AT-032`, `AT-033`, `AT-034`, `AT-034b`, `AT-035`, `AT-036`, `AT-037`, `AT-038`,
>   `AT-039`, `AT-040`. Two of these — `AT-034b` and `AT-040` — are among the six ids `QA2-C-01`'s
>   three-way rule fails on. **They are dispositioned by leaving with the story, not by being
>   struck**, and §6.5 A-43 records that disposition against the ledger row rather than letting the
>   cut absorb it.
> - **TC:** `TC-051`, `TC-052`, `TC-053`, `TC-054`, `TC-055`, `TC-056`, `TC-057`, `TC-058`,
>   `TC-059`, `TC-060`, `TC-061`, `TC-062`, `TC-078`.
>
> **Every heading below carries `— DEFERRED (#D23)`**, so the §5.2 count derivations exclude them
> mechanically rather than by a reader remembering. The `#D23` marker is machine-readable and is the
> only thing a census needs to read.
>
> **What does NOT leave:** `LLR-N07.2.2b` (hit painting in the three remaining renderers) belongs to
> **US-N07**, not to this story, and stays in the batch with `AT-024`. `LLR-N14.2.3`'s coercion
> clause leaves with the story, but the *class* it belongs to does not — `HLR-COERCE` (§3.0) owns
> the class and is unaffected.
>
> **TWO NEWLY RAISED UX FINDINGS TRAVEL WITH THIS DEFERRAL, AND THEY ARE OWNED, NOT LOST**
> (`UX2-C-11`, `UX2-C-12`; backlog `B-31`, `B-32`; §6.5 A-73). Both were raised at the RIDER-1
> reconciliation and appear in **no** prior lens ledger, so neither has ever been through a review.
> They are recorded here rather than in a review note because **this is the deferral they leave
> with**, and a finding whose only home is a review file is a finding the next batch does not
> inherit:
> - **`UX2-C-11` (major)** — the inspector's `_commit` (`mapper/widgets/inspector.py:280`, reached
>   from both blur and submit paths) **rewrites the sidecar even when the delta is empty**. Measured
>   over nine focusables: **6 of 9 rewrote the sidecar, while only 5 of 9 changed a value** — the gap
>   is the finding, and `insp-title` / `insp-notes` rewrite on an empty delta. **The loss is durable
>   to disk.** It is joined to US-N14 because it needs the *same* confirmation-affordance ruling as
>   the data-loss family, not because it is a lens defect.
> - **`UX2-C-12` (minor)** — a damaged-map load fires the toast **twice, both with an empty title**:
>   `[('', 'no se pudo cargar roto: …'), ('', '…')]`. Verified live: `load_or_notice`'s two `notify`
>   call sites (`mapper/app.py:453`, `:460`) pass **no `title=`**, which accounts for the empty
>   titles. **The double-fire is NOT accounted for** — the failure arm is de-duplicated per name
>   within one call, so a second toast implies a second call path that nothing in the tree explains.
>   **Recorded as open and unexplained rather than as diagnosed**, which is the honest state.
> - **Neither is closed by `B-30`**, which shares one of the two strings: `B-30` removes the path
>   from the message and says nothing about how many times it fires or whether it carries a title.
>   Stated because two findings on one string is exactly where a fold drops one.

#### Acceptance (black-box) — US-N14 — **DEFERRED (`#D23`)**

- **Observable outcome:** the operator writes a field query and the map answers by shape — the
  matching nodes stay lit, everything else falls back to ground, and a line declares how many nodes
  in how many branches answered. When the query names a field the schema does not define, the
  operator is told **that**, and not "no results".
- **Shipped surface:** the lens input on `MapScreen` and the map canvas it re-tints; observed through
  the rendered text and style spans of `#map-canvas` and the count line.
- **Deliverable + observation:** a painted canvas in which every matching node carries card chrome
  and a lit tone and every non-matching node is bare dim text with no chrome; a painted count of the
  form `N nodos en M ramas`; and three distinguishable outcome states.
- **Acceptance tests:** `AT-032`, `AT-033`, `AT-034`, `AT-035`, `AT-036`, `AT-037`, `AT-038`,
  `AT-039`, `AT-040`.
- **Boundary catalog (QC-3):**
  - ☑ **empty** — `AT-033` submits `E:riesgo C:alta`, executed to return **0** nodes on the shipped
    fixture; and separately submits an empty query string.
  - ☑ **invalid** — `AT-034` submits `Z:algo` (undefined key) and `E:obsoleto Z:algo` (one valid term
    plus one undefined); `AT-040` submits a term whose value carries Rich markup.
  - ☑ **boundary** — `AT-032` submits a single term matching every node and a conjunction matching
    exactly one; `AT-038` walks past the last match.
  - ☑ **error** — `AT-034` covers the malformed-term class: a token with no colon, and a token with
    an empty key.

#### HLR-N14.1 — the lens parser is a pure function with three declared outcome classes *(the Q-6 answer)* — **DEFERRED (`#D23`)**

- **Traceability:** US-N14
- **Statement:** The search module shall provide a parse function that turns a query string into a
  value carrying its terms and the set of term keys that name neither a schema field nor a reserved
  pseudo-field, and the system shall distinguish three outcomes: a query with resolvable keys and at
  least one matching node, a query with resolvable keys and no matching node, and a query naming at
  least one unresolvable key.
- **Rationale (informative):** an unspecified empty result is the classic vacuous-acceptance trap
  (§2.6 S-4's own verdict). "No matches" and "your query was meaningless" must not paint the same.
  Putting the distinction in the **parse** result rather than in the evaluation makes it decidable
  before any node is examined, and therefore testable at Layer 0 with no event loop and no
  filesystem (risk A-10's disposition, verbatim).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_lens.py -k "parse_outcome_classes"` *(provisional)*
  — Layer-0, over a graph built in memory and over the shipped fixture.
- **Numeric pass threshold:** for each of the 9 queries executed in **M-8**, the classified outcome
  equals the recorded one: 4 `MATCH`, 3 `EMPTY`, 2 `UNDEFINED-FIELD`.
- **Priority:** high
- **Acceptance:** `AT-032`, `AT-033`, `AT-034`, `AT-035`
- **Value reconciliation (C-36):** `parse_lens` and `lens_hits` are `NEW — created in Phase 3`,
  declared in `docs/ARCHITECTURE.md` §4. The reserved pseudo-field name `state` reconciles to
  `mapper/model.py::Ficha.state` (`model.py:29`, value domain `ok | risk | late | blocked`). Schema
  keys are **derived at evaluation time** from `Graph.schema`, never enumerated in the spec —
  executed on the shipped fixture they are `['D','O','E','C','N']` (**M-8**).
- **Layer-0 justification:** the parser has cyclomatic complexity `>= 3` (a token loop with a
  key-resolution branch and a malformed-token branch) and it parses at a boundary — operator text.
  Both criteria for a Layer-0 unit are met, and `mapper/search.py` imports only `.model`
  (`docs/ARCHITECTURE.md` §3, executed), so the unit test needs no event loop and no filesystem.

##### LLR-N14.1.1 — an undefined field key is declared, not silently empty — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.1
- **Statement:** If a lens term names a key that is neither a key of the loaded graph's schema nor a
  reserved pseudo-field, then the system shall record that key in the parse result's unresolved set,
  **shall not evaluate the query at all**, shall leave the canvas exactly as it was painted before
  the query, and shall paint a declaration naming the unresolved key together with the field list
  **derived from the loaded map's schema**.
- **Touched symbols:** `mapper/search.py::parse_lens` and its result type's unresolved-key field —
  both `NEW — created in Phase 3`.
- **Validation:** `test (unit)` + `test (pilot)`
- **Executed verification:** `pytest tests/test_lens.py -k "undefined_field_is_named"`
  *(provisional)* at Layer 0, plus a pilot arm reading the painted text.
- **Numeric pass threshold:** for `Z:algo` the unresolved set equals `{"Z"}` and the painted text
  contains the substring `Z`; for `E:obsoleto Z:algo` the unresolved set equals `{"Z"}`; for
  `C:zzz` the unresolved set is **empty**. The painted text and at least one style span differ
  between the `Z:algo` case and the `C:zzz` case. All three executed at draft (**M-8**).
- **Acceptance criteria — how the distinctness is observable, strengthened at reconciliation:**
  the two zero-result queries are rendered side by side in the same test, and the assertion is not
  merely that their text differs but that **the canvas itself differs**: for the undefined-field
  query the canvas is byte-identical to its pre-query state, and for the well-formed zero-match query
  every node has fallen to ground. That is a far stronger oracle than comparing two message strings,
  and it is the one `01b-ux-decisions.md` DECISION 2 derives from the principle *an unresolvable
  query is never executed*. **The first draft of this LLR compared text and style spans only**, which
  would have passed on an implementation that dimmed the whole canvas in both cases — the exact
  pixel-identity the question exists to prevent. Audit row §6.4 D-5.
- **Normative copy (Spanish, verbatim from `01b-ux-decisions.md` §2.2 — the implementer copies it).
  THE STRINGS ARE NOW COMPLETE; the parked block truncated its own normative copy to a literal
  ellipsis (`QA-M-14`, §6.5 A-30):**
  - one unknown key —
    `el mapa no define el campo «Z» · campos: D acta · O origen · E estado · C criticidad`
  - two or more —
    `el mapa no define los campos «Z», «Q» · campos: D acta · O origen · E estado · C criticidad`
  - well-formed zero match — `0 nodos · ningún nodo tiene estado = inexistente`
  - non-zero match, for the count-line form — `5 nodos en 2 ramas · ⇥ recorrer · esc limpiar`

  **A block headed *"the implementer copies it"* that renders `· campos: …` gives the implementer a
  literal ellipsis to copy.** The parked text did exactly that for the first two strings.
- **The two line forms are reconciled, not left to collide (`QA-M-14`).** The declared count-line
  form is `N nodos en M ramas`, and the mandated zero-match line
  `0 nodos · ningún nodo tiene estado = inexistente` is **not of that form** — it substitutes a
  clause for `en M ramas`. That is deliberate: *"0 nodos en 0 ramas"* is arithmetically true and
  tells the operator nothing about **why**, which is the same distinctness argument `LLR-N07.3.2`
  makes for the empty search state. Recorded here so the difference is a decision rather than an
  inconsistency an implementer normalises away.
- **The `⇥ recorrer` fragment in the count-line form is SUPERSEDED by `#D6` (Q-7).** `⇥` is
  rejected; the walk is `n` / `N`. The hint fragment shall read the seat's own labels for
  `next_hit` / `prev_hit` rather than naming a chord in a literal — one declaration, four readers.
- **The list after `· campos:` shall be derived from `graph.schema`, never hand-listed** — a
  hand-listed vocabulary is a label that lies the moment a map has a different schema, which is
  C-31's family. The four pairs above are the **legacy fixture's** schema, shown as the worked
  example, not as the value to type.

##### LLR-N14.1.4 — the match predicate, the case rule and the bounds are declared — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.1, security condition **C-6** (`02b` S-07)
- **Statement:** A lens term shall match a node when the coerced string form of the addressed value
  **equals** the term's value under Unicode simple case folding, and shall not match on a substring;
  and the system shall refuse a query exceeding the declared term-count or query-length bound
  without evaluating it.
- **WHY THIS LLR EXISTS: the predicate was nowhere stated, and every threshold in section 3.7 was
  satisfied by two different implementations (6.5 A-38).** `02b` S-07 searched all 2 707 parked
  lines for `re.`, `regex`, `fnmatch`, `eval(`, `compile(` and found **zero occurrences**, which is
  the good news: there is no regex path and no eval-shaped path in the specified design, so
  catastrophic backtracking and code execution are out of scope **by construction**, and
  `LLR-N14.2.1` already forbids the renderer from receiving a query string or a predicate. What was
  missing is the predicate itself.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_lens.py -k "predicate_and_bounds"` *(provisional)* --
  the four arms below, plus the `search_hits` empty/whitespace arm.
- **Numeric pass threshold:** `C:alt` returns **0** nodes where `C:alta` returns **5**; `c:ALTA`
  returns the same set as `C:alta`; the empty query and a whitespace-only query each return **0**
  matches and paint a state distinct from both `MATCH` and `UNDEFINED-FIELD`; a query over the
  declared term-count or query-length bound is refused with a declared line and **0** evaluations.
- **Named weaker variants, from `02b`, each answered by one arm above:**

  | Mutant | Survives what | Reddened by |
  |---|---|---|
  | **M-Q1** `value.lower() in field.lower()` -- substring | **every threshold in section 3.7 as written**: `state:risk` still returns 3, `E:riesgo` still returns 2 | the `C:alt` to 0 arm |
  | **M-Q2** case-**sensitive** equality | every declared threshold -- schema keys are uppercase single letters in the shipped fixture, so `c:alta` never arises | the lowercase-key arm `c:ALTA` |
  | **M-Q3** treat the empty query as `UNDEFINED-FIELD` | an *"is not match-everything"* test | asserting **which** state, not merely "not all nodes" |
  | **M-Q4** split terms on any whitespace with no quoting rule | everything, until a field value contains a space | the declared term-count bound and `#D8`'s bare-word rule together |

- **Equality is chosen over substring, and the reason is the story's own distinction.** Under
  equality, `EMPTY` and `UNDEFINED-FIELD` -- the two states the story exists to tell apart -- stay
  distinguishable. Substring is defensible; **what is not defensible is shipping the batch without
  the sentence**, which is why `02b` raised it as a condition rather than a preference.
- **THE SUBSTRATE `D6` PROMOTES TO SOLE OWNER IS ITSELF WRONG -- executed (6.5 A-38).** Re-executed
  at `d877784`:

  ```
  search_hits('')   -> ['a','b']      len(nodes) -> 2       # every node matches
  search_hits(' ')  -> ['a','b']
  mapper/model.py::Graph.search_hits   q = query.lower() ... if q in hay
                                       # the empty string is a substring of every haystack
  ```

  `D6` makes `search` the single owner of *"what matches"*, and `HLR-N07.2`'s trustworthy **count**
  is taken from `search_hits`. `AT-023` asserts a whitespace query is not match-everything **for the
  lens** and leaves `search_hits` unfixed. This LLR's empty/whitespace arm therefore binds **both**
  owners -- otherwise the batch ships one owner with two behaviours, which is the defect `D6` exists
  to remove.
- **Cost is not the exposure, recorded so the bound is not mistaken for a performance fix.**
  Measured: `search_hits` over the whole graph is **0.3 ms at n=500**, **1.3 ms at n=2000**,
  **6.5 ms at n=10 000**, and **1.1 ms over a 1 MB title**. Evaluation is cheap; the exposure is the
  **undefined predicate**. The bounds exist so `LLR-N14.1.3`'s *"declared rule"* has something to
  declare, not to buy time back.
- **Acceptance:** `AT-034b`

##### LLR-N14.1.2 — the two "estado" namespaces are kept apart — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.1
- **Statement:** When a lens term names the reserved pseudo-field for node state, the system shall
  evaluate it against the node's state value and shall not evaluate it against any schema field.
- **Touched symbols:** `mapper/search.py::lens_hits` — `NEW — created in Phase 3`;
  `mapper/model.py::Ficha.state` (`model.py:29`); `mapper/model.py::Ficha.fields` (`model.py:32`).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_lens.py -k "state_and_schema_key_E_are_distinct"`
  *(provisional)* — over `fixtures/legacy_nodos.yml`, whose schema key `E` is labelled *estado*.
- **Numeric pass threshold:** `state:risk` returns exactly `['erp','rrhh','alm']` (3 nodes) and
  `E:riesgo` returns exactly `['rrhh','alm']` (2 nodes); the two result sets are **not** equal. All
  executed at draft (**M-8**).
- **Acceptance criteria:** the fixture is the shipped one and the collision is real — Spanish
  *estado* names both the node state and schema key `E`, with **different vocabularies**
  (`ok/risk/late/blocked` versus `obsoleto/estable/riesgo/atrasado/bloqueado`). The inequality
  assertion is what makes the routing provable rather than plausible.

##### LLR-N14.1.3 — malformed terms are specified — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.1
- **Statement:** If a query token contains no key separator or has an empty key, then the parse
  function shall classify that token by a declared rule and shall not raise.
- **Touched symbols:** `mapper/search.py::parse_lens` — `NEW — created in Phase 3`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_lens.py -k "malformed_terms"` *(provisional)*.
- **Numeric pass threshold:** **0** exceptions over at least 5 malformed inputs: a bare word, a
  leading colon, a trailing colon, a doubled colon, and a whitespace-only string.
- **`AT-034` IS SPLIT — one node cannot drive two requirements with different methods
  (`QA-M-13`, §6.5 A-37).** `AT-034` was claimed for `Z:algo`, `E:obsoleto Z:algo`, a token with no
  colon, and a token with an empty key — spanning `LLR-N14.1.1` (validation `test (unit)` +
  `test (pilot)`) and this LLR (`test (unit)`). Split by requirement and by method:
  - **`AT-034`** — the *undefined-key* cases (`Z:algo`, `E:obsoleto Z:algo`) under `LLR-N14.1.1`,
    driven through the shipped surface as well as the parser;
  - **`AT-034b`** — the *malformed-token* cases (bare word, leading/trailing/doubled colon, empty
    key, whitespace-only) under this LLR, a pure parser node.

  The bare word belongs to `AT-034b` under `#D8`, which classifies it as malformed rather than as an
  undefined key.
- **Acceptance:** `AT-034b`
- **Census classification of the malformed-query chip — the row `QA-B-08` says is missing.** The
  chip ` Z ? sin definir ` is painted in `ALERT #ff4f42` (`01b-ux-decisions.md` DECISION 2), and
  `01b:332-333` records the rule that *"if `ALERT` acquires a second job it must acquire a row
  here too."* **It does not acquire a second job.** `LLR-S06.3.5` declares `ALERT`'s single job as
  *failure or blockage — this item cannot proceed as it stands*, and a query naming a field the map
  does not define cannot proceed as it stands. The chip therefore enters `HLR-S06.3`'s census
  **classified**, and `AT-005` does not redden at Inc-5 for a reason nobody wrote down. The
  contrasting chip in the same DECISION — ` E estado = inexistente `, a **well-formed** query over a
  defined field that matched nothing — stays in `MUT`, for the same reason `LLR-N07.3.2`'s empty
  count line does: a finished question with an empty answer is neither outstanding nor failed.
- **Q-8 IS RULED: a bare word is a MALFORMED token, with a redirect (`PDR-…#D8`, §6.5 A-26).**
  `/` is free text; the lens is structured `key:value`. A bare word parses to the declared malformed
  class (never raising), paints in the `sin definir` chip family, and **the line reads as a
  redirect** — it teaches `campo:valor` and points at `/` for free text. The reason is structural,
  not stylistic: under `#D6` *search hits* and *lens matches* are unified into one *coincidencias*
  concept walked by one pair of chords, so if a bare word in the lens box also meant free-text
  search, **the two features would become one feature with two syntaxes and two entry points**, and
  `C-D6a`'s "only one result set is live" invariant would become much harder to reason about. One
  concept per entry point, and the error teaches the model rather than guessing at intent.
- **What would reverse it, recorded:** a ux-lens finding that operators type bare words into the lens
  box often enough that the redirect is friction rather than instruction. Nobody has made that
  observation, and it is cheap to reverse — the parse rule is one branch in `parse_lens`.
- **~~Flagged — a specification gap the requirement does NOT close~~ (superseded by `#D8` above):**
  whether a bare word (no colon)
  is a free-text term over title and notes, or a malformed token, is **not settled here**. Both are
  defensible and neither is derivable from the brief. It is a **PDR decision**, and it is recorded as
  such rather than chosen arbitrarily, because the two choices produce different products: the first
  makes the lens a superset of US-N07's search, the second keeps them separate surfaces. The probe in
  **M-8** exercised the first reading; that was a probe convenience, not a decision. **Checked
  against `01b-ux-decisions.md` at reconciliation: its DECISION 2 settles the undefined-key case and
  does not address the bare word, so Q-8 stays open rather than being quietly resolved by a sibling
  artifact.**

#### HLR-N14.2 — the answer is visible as a shape, and its size is declared — **DEFERRED (`#D23`)**

- **Traceability:** US-N14
- **Statement:** While a lens query with resolvable keys is active, the system shall paint every
  matching node with card chrome in a lit tone and every non-matching node as bare text in the
  ground-adjacent dim tone with no card chrome, and shall paint a line declaring the number of
  matching nodes and the number of branches containing them.
- **Rationale (informative):** the prototype's own copy is *"la concentración ES el hallazgo"* —
  where the matches cluster is the answer, so figure-ground is the deliverable and not a decoration.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_lens.py -k "figure_ground_and_counts"`
  *(provisional)* — submit a query on `fixtures/legacy_nodos.yml`, read `#map-canvas` text and
  style spans.
- **Numeric pass threshold:** for `C:alta`, the count line declares `5` nodes and `3` branches; every
  one of the 5 matching ids is painted with chrome and every one of the other 3 without. Both
  numerals executed at draft (**M-8**).
- **Priority:** high
- **Acceptance:** `AT-036`, `AT-037`
- **Value reconciliation (C-36):** the string `nodos en` and the word `ramas` are
  `NEW — created in Phase 3`; `grep -rn "ramas" mapper/` returns no output. The chrome glyph `▐`
  already ships (`mapper/views/layered.py:158`, and present in the **M-1** painted set). The dim tone
  reconciles to `mapper/darkside.py::MUT` (`darkside.py:16`, `#737373`).
- **`rama` is a defined term, not an adjective:** the *rama* of a matching node is its
  root-child ancestor — the child of `graph.root_id` on the path from the root to that node. Under
  that definition, executed (**M-8**): `C:alta` -> 5 nodes in 3 ramas; `state:risk` -> 3 nodes in
  2 ramas.

##### LLR-N14.2.1 — the renderer paints a set, it does not evaluate a query — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.2
- **Statement:** The renderer shall receive the lens result as a set of node ids in the view state
  and shall not receive a query string, a parsed query value or a predicate.
- **Touched symbols:** `mapper/views/state.py::ViewState.lens_matches` —
  `NEW — created in Phase 3`, declared in `docs/ARCHITECTURE.md` §4a with the domain
  `frozenset[str] | None` where `None` means no lens is active;
  `mapper/views/layered.py::LayeredRenderer.render` (`layered.py:78`).
- **Validation:** `test (unit)` + `inspection`
- **Executed verification:** `pytest tests/test_layered.py -k "lens_matches_is_a_set"`
  *(provisional)*; plus a grep asserting `mapper/views/` does not import `mapper.search`.
- **Numeric pass threshold:** **0** occurrences of an import of the search module anywhere under
  `mapper/views/`. Pre-state executed: **0** today, and the edge is the one
  `docs/ARCHITECTURE.md` §3 records as *deliberately not created* — this LLR is what keeps it so.
- **Acceptance criteria:** `frozenset` is a builtin, so passing ids adds no module edge where passing
  a parsed query would add `views -> search` (R-014, alternative (c), rejected).
- **Recorded honestly:** the pre-state of this probe is **0**, so it is a guard rather than a
  discovery. Its non-trivial arm is a positive control: the same grep run against a scratch module
  that *does* import the search module must return 1, proving the probe can see the violation it
  claims to forbid. The control runs at the same package depth as `mapper/views/` and is removed
  afterwards.

##### LLR-N14.2.2 — the three-state distinction survives to the canvas — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.2, HLR-N14.1
- **Statement:** While no lens is active, the renderer shall paint every node with its ordinary
  chrome and tone, and shall not dim any node.
- **Touched symbols:** `mapper/views/layered.py::LayeredRenderer.render` (`layered.py:78`).
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_layered.py -k "no_lens_no_dimming"` *(provisional)*
  — render with `lens_matches` set to the no-lens sentinel and compare against the current shipped
  output for the same graph.
- **Numeric pass threshold:** the rendered text equals the pre-change rendered text for the same
  graph and geometry, character for character. This is the **245-test-baseline guard**: an empty
  match set and no lens at all must not paint the same, or every existing renderer test becomes a
  test of the lens.
- **Acceptance criteria:** the sentinel distinction between "no lens" and "a lens that matched
  nothing" is exactly the distinction HLR-N14.1 makes at the parse layer, carried one layer down. If
  it collapses here, the Q-6 answer is undone in the renderer.

##### LLR-N14.2.3 — a field value reaching the canvas is coerced — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.2, risk A-7
- **Statement:** The system shall coerce **every file-derived string placed on a lens result
  surface** through the design module's plain-text coercion.
- **WIDENED from "every ficha field value" (C-5, `02b` S-06, §6.5 A-16).** `02b` S-06 found that the
  lens's undefined-field declaration echoes file-derived **schema key names** — the `campos: D acta ·
  O origen · E estado · C criticidad` list in the malformed-query chip is read from the map's own
  schema — and **no coercion LLR covered them**, because a schema key name is not a field *value*.
  The statement is therefore scoped to *every file-derived string on the surface*: field values,
  schema **key names**, the schema's human labels, the echoed query term, node titles, and branch
  names. The fixture positions are **derived from `_build_sidecar`** rather than hand-placed, so a
  key the fixture author did not think of is still covered.
- **Touched symbols:** `mapper/darkside.py::plain` (`darkside.py:276`); `mapper/store.py::_coerce_field`
  (`store.py:39`, shipped by the repair batch and applied at `:235` for attributes and `:239` for
  fields) — **the store boundary coerces field *values* to `str`, which is a type coercion, not the
  code-point coercion of §3.0**, and the two must not be confused; the lens count line, the chip and
  any echoed term in `mapper/app.py::MapScreen` — `NEW — created in Phase 3`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_lens.py -k "hostile_field_values"` *(provisional)* —
  the hostile positions are enumerated from `_build_sidecar`'s own output, not chosen.
- **Numeric pass threshold (C-4, §6.5 A-13):** measured **on the painted row** — **0** occurrences of
  any code point in `COERCION_RANGES` (§3.0); **0** Rich markup tags interpreted; row length equals
  canvas width for every hostile input; the **split-at-width arm** passes; and the count is taken
  over **every derived file-derived position**, `>= 1` of which is a schema **key name**.
- **Named weaker variant (`M-N14.2.3-a`):** coerce field values only, as the parked statement said.
  Green on every value fixture; the chip's `campos:` list still echoes an uncoerced key name. The
  *"`>= 1` of which is a schema key name"* clause is what reddens it.
- **Acceptance criteria:** ficha field values and schema key names are both file-derived text
  (`_nodos.yml`) reaching a new rendered surface — risk A-7's family, scoped to the derived sink
  census of `LLR-N06.2.3` rather than to a file.

#### HLR-N14.3 — the operator walks the answer and can recall it — **DEFERRED (`#D23`)**

- **Traceability:** US-N14
- **Statement:** When the operator presses the walk chord while a lens is active, the system shall
  move the selection to the next matching node in tree order with the ficha inspector holding focus;
  and when the operator presses a saved-lens chord, the system shall apply the query stored against
  that chord.
- **Rationale (informative):** saved lenses on number keys are separable from the query itself
  (§2.6 S-4) and are the lowest-priority half of this story. Digits are free: executed (**M-9**),
  **no** digit `0`-`9` is bound in any scope.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_lens.py -k "walk and saved_lens"` *(provisional)* —
  press the real walk chord repeatedly and record the selected id and `app.focused` after each press.
- **Numeric pass threshold:** the recorded selection sequence equals the match list in tree order,
  exactly; `app.focused` is inside the inspector region after each press; the saved-lens chord
  reproduces the same match set as typing the query.
- **Priority:** low — the walk is blocked on Q-7 and the saved lenses are separable.
- **Acceptance:** `AT-038`, `AT-039`
- **BLOCKED on Q-7, with the evidence in hand — this is the batch's largest brief-versus-tree
  contradiction.** The story asks for `⇥`. Executed (**M-10**):
  - `tests/test_keymap.py:160` asserts the seat contains **no** `tab` binding;
  - `tests/test_keymap.py:165` asserts no `Screen` subclass binds `tab` outside
    `keymap.TAB_BINDING_EXCEPTIONS = ("SettingsScreen", "EditorScreen")`, and `MapScreen` is not in
    that list;
  - `mapper/keymap.py:46-48` records the measurement behind both — *a screen-level `tab` binding was
    measured to produce 0 focus moves in 9 presses* (batch-1 LLR-N06.5);
  - `pytest tests/test_keymap.py -k tab` -> **5 passed** on `master` today;
  - and `tab` is load-bearing: 9 real presses on `MapScreen` at 140 x 45 produce **9 distinct focus
    targets and 8 transitions** — the rail, then all 8 editable inspector fields. Taking `tab` for
    the walk removes the only keyboard path to the inspector, which is the same story's other
    requirement.
- **Disposition:** this requirement is written **chord-agnostic**. PDR settles the chord, as it
  settles Q-3. Whatever is chosen carries LLR-N14.3.2 as a standing invariant.

##### LLR-N14.3.1 — the walk uses one ordering, shared with search — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.3
- **Statement:** The lens walk shall order its matches by the same pre-order tree walk the search
  walk uses.
- **Touched symbols:** the ordering helper in `mapper/search.py` shared with LLR-N07.3.1 —
  `NEW — created in Phase 3`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_lens.py -k "walk_order_matches_search_order"`
  *(provisional)* — the same graph, one query that is both a valid search and a valid lens.
- **Numeric pass threshold:** the two ordered sequences are identical; and the test's own guard
  asserts the fixture's tree order differs from its dict-insertion order (executed **M-7**: they
  differ at position 3).
- **Acceptance criteria:** one ordering, one helper. Two orderings is how the search cursor and the
  lens cursor start disagreeing about what "next" means, which is the same failure shape as the two
  definitions of "hit".

##### LLR-N14.3.2 — the walk chord does not cost the inspector its keyboard path — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.3, Q-7
- **Statement:** After the walk chord is added, pressing the focus-traversal key nine times from the
  map canvas shall still produce eight focus transitions across nine distinct targets.
- **Touched symbols:** `mapper/keymap.py::KEYMAP` (the added chord);
  `mapper/keymap.py::TAB_BINDING_EXCEPTIONS` (`keymap.py:49`) — **must not** gain an entry for
  `MapScreen`; `mapper/app.py::MapScreen.BINDINGS` (`app.py:1066`, generated from the seat).
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_key_dispatch.py -k "inspector_stays_reachable"`
  *(provisional)* — 9 real focus-traversal presses under `App.run_test(size=(140,45))`, recording
  `app.focused` after each.
- **Numeric pass threshold:** distinct focus targets `== 9`; transitions `== 8`; **and, from the
  query `Input`, pressing `escape` shall move focus out of the box, with the hint line naming that
  route.** Executed pre-state (**M-10**), on `master`: 9 and 8, in the order rail, then the 8
  inspector fields `insp-title`, `insp-state`, `insp-field-D`, `insp-field-O`, `insp-field-E`,
  `insp-field-C`, `insp-field-N`, `insp-notes`.
- **THE INVARIANT CANNOT SEE THE FAILURE IT WAS WRITTEN FOR — the escape clause is why
  (`QA-M-08`, §6.5 A-35).** `01b` DECISION 5 step 5 records the **required mitigation that did not
  land**: *"`escape` … must leave the query box, and the hint line must say so. Without that,
  `priority=True` on `tab` traps the operator in the input."* **Being trapped inside the query
  `Input` preserves 9 targets and 8 transitions** — the traversal ring is intact; the operator
  simply cannot reach it. A count-only invariant is green on exactly the outcome it exists to
  prevent, which is `C-40` limb 2 in its purest form.
- **Named weaker variant (`M-N14.3.2-a`):** ship the walk with `priority=True` and no `escape`
  route. Distinct targets `== 9`, transitions `== 8`, invariant green, inspector unreachable from
  the query box. The escape clause is the only arm that reddens it.
- **C-D6b — this LLR is RETAINED VERBATIM as the standing regression guard, and re-run after Inc-4,
  Inc-6 and Inc-9** (`PDR-2026-08-26-ui-next-batch-02#D6`). It is not a one-time gate on Inc-5.
- **Acceptance criteria — and the Q-7 ruling narrows it.** `#D6` **rejected `⇥`**, so the predicted-
  red set is now **empty**: the three shipped `tab` guards (`tests/test_keymap.py:160`, `:165`,
  `:194`) shall stay **green**, `TAB_BINDING_EXCEPTIONS` gains nothing, and `MapScreen` is not added
  to it. Under the parked chord-agnostic wording those three were the predicted-red set *if* `tab`
  was chosen; that branch is closed. **What would reverse the ruling, recorded:** the two guards
  being deliberately retired **with a replacement keyboard route to the inspector shipped in the
  same increment**. Nothing in this batch proposes that.

##### LLR-N14.3.3 — a saved lens stores a query, not a result — **DEFERRED (`#D23`)**

- **Traceability:** HLR-N14.3
- **Statement:** The system shall store against a saved-lens chord the query text, and shall
  re-evaluate it against the loaded graph each time the chord is pressed.
- **Touched symbols:** the saved-lens store on `mapper/app.py::MapScreen` —
  `NEW — created in Phase 3`; `mapper/keymap.py::KEYMAP` gains the digit chords in map scope.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_lens.py -k "saved_lens_reevaluates"` *(provisional)*
  — save a lens, mutate a node so it newly matches, press the chord, assert the new node is in the
  result.
- **Numeric pass threshold:** the recalled match set equals the freshly-typed match set after the
  mutation; the two differ from the match set at save time, so the re-evaluation is proved rather
  than assumed.
- **Acceptance criteria:** storing a result would make a saved lens a stale snapshot that lies as
  soon as the map changes — the state-lifetime failure mode. **Lifetime is declared:** saved lenses
  live on the screen instance, are not persisted, and are discarded when the screen is dismissed.
  Nothing in this batch writes them to `store`, so there is no cross-map provenance question.

---

### 3.8 · US-N16 «leyenda» — `?` explains the view you are in *(Inc-8 and Inc-9 — §5.4)*

> **Header corrected (`P2-B1`, `QA2-C-06`, §6.5 A-49).** ~~*(Inc-7)*~~ was the **stale ARQ 7-cut**
> number. The ratified cut **splits this story across two increments** — `Inc-8` (the legend panel:
> truncation and the glyph vocabulary) and `Inc-9` (help scope routing and the `KEY_SCOPE`
> declarations) — with `Inc-8` before `Inc-9` as a hard ordering. A single-increment header did not
> merely name the wrong number; **it hid the split, and the split is what makes the acceptance
> passable.** The cut is stated once, in §5.4.

> **Written quantified over a derived screen set, never over the known offenders.** Batch 1's §2.1b
> lesson is that a requirement scoped to a file gets satisfied at that file's boundary while the
> identical defect ships in its siblings — and §2.8.3 records that **P-13 itself fell into exactly
> that trap**, counting three offenders inside `app.py` while two more sit in `mapper/screens/`.

#### Acceptance (black-box) — US-N16

- **Observable outcome:** on any screen, pressing `?` opens a legend that names **that** view, lists
  exactly the keys that work there, and shows the glyph vocabulary that view paints, drawn the way
  the view draws it.
- **Shipped surface:** `HelpScreen` (`mapper/screens/help.py:17`), reached by the real
  `question_mark` chord (the seat's key name — `mapper/keymap.py:150`, executed; the seat's own
  docstring at `keymap.py:196` notes *"nobody presses a key called question_mark"*, so the glyph is
  `?` and the key name is what Textual dispatches).
- **Deliverable + observation:** a painted panel whose title names the source view, whose key rows
  are **set-equal** to the seat's bindings for the source screen's own scope, and whose glyph rows
  carry the same styles the canvas uses.
- **Acceptance tests:** `AT-041`, `AT-042`, `AT-043`, `AT-044`, `AT-053`.
- **`AT-053` is NEW at amendment set 3 pass 2** (`UX2-C-05`, §6.5 A-72): the legend declares its own
  scroll keys, asserted by pressing them. It is on `HLR-N16.4`'s `Acceptance:` line and in §5.2's
  behavioral row.
- **`AT-045` is DELETED (`QA-B-03`, §6.5 A-07)** — same padding shape as `AT-027` and `AT-028`: two
  appearances, no predicate, no `Acceptance:` line claiming it. The story claimed 5 and defined 4;
  it now enumerates 4.
- **Every `AT` above declares its Pilot size**, per `HLR-N16.1`'s oracle block. The sizes are read
  from `tests/test_repair_layout.py:45-46` (`WIDE_SIZES`, `NARROW_SIZE`) rather than re-typed.
- **Boundary catalog (QC-3):**
  - ☑ **boundary** — `AT-042` drives the screen with the largest binding set (map, 27 rows) and the
    smallest (app, 2 rows), both executed (**M-9**).
  - ☑ **invalid** — `AT-042` covers a screen that declares **no** scope, which is the executed state
    of two shipped screens and the case a naive fix silently satisfies.
  - ☑ **empty** — `AT-043` drives a view whose glyph vocabulary is empty and asserts the vocabulary
    section is omitted rather than painted blank.
  - ☑ **error** — `AT-044` presses the reserved doubled chord and asserts the declared outcome
    rather than an unhandled key.

#### HLR-N16.1 — every screen routes `?` to its own scope, and declares one

- **Traceability:** US-N16
- **Statement:** Every screen class that binds the help chord shall declare a key scope and shall
  open the legend for that declared scope; and the set of key rows the legend **presents to the
  operator** shall equal `keymap.bindings_for(source_screen.KEY_SCOPE)`, with every row reachable
  without leaving the legend.
- **The quantified set is pinned to `bindings_for`, not to `KEYMAP` (`QA-M-04`).** The two are
  **different sets** and the parked document used both. Executed at `d877784` in this amendment
  session: `len(bindings_for('map'))` is **27** while `KEYMAP` holds **25** map-scope entries —
  `bindings_for` merges 2 app-scope rows. `bindings_for('home')` is **13**, `bindings_for('app')`
  is **2**. Every count in this requirement and in every legend `AT` is
  `len(keymap.bindings_for(scope))`, evaluated at run time and never typed.
- **Rationale (informative):** the bindings half is **derivable, so it must be derived** (control
  C-31). A hand-listed key set in a legend is an unproven spec claim that drifts the first time the
  seat changes, and the legend then documents an intention.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_help_scope.py -k "every_help_route_carries_its_scope"`
  *(provisional)* — the screen set is **derived** by walking the product modules for `Screen`
  subclasses whose bindings include the help chord; for each, drive the real `question_mark` key and
  compare the painted rows against `keymap.bindings_for(source.KEY_SCOPE)`.
- **Numeric pass threshold:** derived screen count `>= 7`; screens declaring no scope `== 0`;
  screens whose `_painted_bindings` union differs from `bindings_for(source.KEY_SCOPE)` `== 0`.
  **Every address below was re-executed at `d877784` in this amendment session; the parked line
  numbers were all stale (§6.5 A-06).**

  ```
  $ python -c "... walk mapper/**/*.py for 'def action_help' ..."
    mapper/app.py:773   mapper/app.py:824   mapper/app.py:1089
    mapper/app.py:1884  mapper/app.py:2049
    mapper/screens/factory.py:486   mapper/screens/settings.py:92          -> 7 definitions
  $ ... 'HelpScreen(' construction sites ...
    app.py:774  push_screen(HelpScreen())            <- no scope
    app.py:825  push_screen(HelpScreen())            <- no scope
    app.py:1090 push_screen(HelpScreen())            <- no scope
    app.py:2050 push_screen(HelpScreen(getattr(self.screen, "KEY_SCOPE", SCOPE_APP)))
    screens/factory.py:489  push_screen(HelpScreen())   <- no scope
    screens/settings.py:95  push_screen(HelpScreen())   <- no scope   -> 5 un-scoped routes
  $ ... 'KEY_SCOPE =' declarations ...
    app.py:341 SCOPE_HOME · :711 SCOPE_IMPORT · :780 SCOPE_PLUG
    app.py:831 SCOPE_REPO · :1096 SCOPE_MAP  · :2006 SCOPE_APP
    -> FactoryScreen and SettingsScreen declare NONE                  -> pre-state 2
  ```

  Pre-states, executed: **7** definitions, **5** un-scoped routes, **2** screens with no
  `KEY_SCOPE`. P-13's verdict of 5 is re-confirmed at the new base; the repair batch did not touch
  it.
- **Priority:** medium
- **Acceptance:** `AT-041`, `AT-042`
- **~~A SECOND shipped defect: the legend does not fit.~~ SUPERSEDED — SATISFIED-EXTERNALLY at
  `d877784`.** The clipping half of this requirement is struck per `PLAN.md` §12.5 **D17**. The
  scroll container shipped in the repair batch. Executed in this amendment session:

  ```
  $ grep -n "VerticalScroll\|help-bindings\|overflow" mapper/screens/help.py
   9:from textual.containers import Vertical, VerticalScroll
  49:    #help-bindings {
  51:        overflow-y: auto;
  73:            VerticalScroll(
  74:                Static(self._render_keymap(), id="help-content"),
  75:                id="help-bindings",
  ```

  Guards on disk: `tests/test_repair_layout.py::test_tc_r24_the_bindings_region_is_scrollable`,
  `::test_at_r12_pressing_help_presents_every_map_binding`,
  `::test_tc_r36_the_dialog_height_is_governed_by_a_named_declaration`. The struck paragraph — 27
  rows into a 28-row dialog, overflowing by 10 with no scrolling container — is retained above the
  strike marker in the parked document's history and is **no longer this batch's work**.
  **The per-view legend half of US-N16 survives untouched and is still the story**: the five
  un-scoped routes, the two screens with no `KEY_SCOPE`, the glyph vocabulary, the view name in the
  title, and the `??` reservation.
- **The oracle — normative, and it now has an executable definition on disk (`QA-B-04`,
  DISCHARGED BY ARTIFACT).** `QA-B-04` blocked because *"assert the painted panel"* named no
  procedure. It names one now, and the requirement **shall reuse it rather than re-invent it**:

  | Idiom | Address at `d877784` | What it does |
  |---|---|---|
  | `_rows_in(screen, region)` | `tests/test_repair_layout.py:74-82` | clips the **composited** frame to one widget's own region, in **both** `y` and `x` |
  | `_painted_bindings(app, pilot)` | `tests/test_repair_layout.py:104-123` | unions `_rows_in(screen, dialog.region)` across **every** scroll position, failing if the pane never reaches `max_scroll_y` |

  Set equality **shall** be asserted against `_painted_bindings`'s union, never against
  `_render_keymap()`'s return value and never against a widget's own `render_lines`. The `x` clip
  is the load-bearing conjunct: `HelpScreen` is a `ModalScreen` with `background: #000000 70%`, so
  an unclipped read composites `MapScreen`'s keybar through the backdrop and counts `cobertura` as
  a legend row. `test_at_r14`'s docstring records the measurement: unclipped reports 10 missing
  where clipped reports 11 — **an unclipped oracle passes a fix that still hides a binding.**
- **Every legend `AT` shall declare its Pilot size.** `AT-041`, `AT-042`, `AT-043`, `AT-044` each
  name the `App.run_test(size=…)` they drive. The parked review measured the naive whole-screen
  oracle returning **16** at 118 x 34 and **19** at 240 x 100 for the same panel; a verdict that
  moves with the terminal is not a verdict. The sizes are the shipped constants
  `WIDE_SIZES = [(140, 45), (120, 40)]` and `NARROW_SIZE = (100, 24)`
  (`tests/test_repair_layout.py:45-46`), read from that module rather than re-typed, so the legend
  ATs and the layout guards cannot drift onto different terminals.
- **Negative control — reuse, do not duplicate.** The control `QA-B-04` demands (the oracle reports
  a known-absent label as absent, and a keybar-only label is not counted) **already exists on disk**
  as `tests/test_repair_layout.py::test_at_r14_the_oracle_is_clipped_to_the_help_dialog` (`:339`),
  whose four limbs are: rows outside the region must exist; the read is clipped in `y`; the read is
  clipped in `x`; and no row painted outside the region appears in the clipped read. Its input set
  is **derived** by `_rows_outside` (`:85-101`) rather than hand-picked — the docstring records that
  a hand-chosen sentinel (`finanzas`) was measured to sit *under* the dialog and discriminate
  nothing. **This requirement adopts `AT-R14` as its oracle's guard; writing a second one is
  forbidden**, because two guards for one oracle is the two-owners defect this batch removes
  elsewhere.
- **Named weaker variant this oracle reddens (`M-N16.1-a`):** keep `_painted_bindings` but drop the
  column slice from `_rows_in`, retaining the row band. Executed pre-fix and recorded at
  `test_at_r14:358-361`: that oracle reports **10** missing where the correct one reports **11**,
  because `cobertura` sits at `y=11` — inside the dialog's row band — and escapes only via the
  column slice. It is a plausible weakening (it looks like a simplification), it still passes
  `AT-R14` limb (b), and it ships a legend with a hidden binding. Limb (c) is what reddens it.
- **Named weaker variant (`M-N16.1-b`):** read the panel once without scrolling. Survives on any
  scope whose bindings fit one viewport (`app`, 2 rows) and fails silently on `map` (27 rows).
  `_painted_bindings`'s union across scroll positions is what reddens it.
- **The oracle, and the trap it avoids — this is the load-bearing sentence of the requirement.**
  Executed (**M-11**), the naive oracle *"painted rows equal `bindings_for(help_screen.scope)`"* is
  **TRUE on the broken screen**: `SettingsScreen` opens help with scope `app`, `bindings_for("app")`
  is 2 rows, and 2 rows are painted — a perfect match over a legend that lists 2 keys for a screen
  binding 6. The bug is in *which* scope was passed, so the oracle must key on the **source screen's
  own declared scope**. Written the naive way this acceptance is vacuous, and it would have shipped
  green.

##### LLR-N16.1.1 — the screen set is derived, never enumerated

- **Traceability:** HLR-N16.1
- **Statement:** The verification shall obtain its screen set by inspecting the product modules at
  run time and shall assert that set is non-empty before evaluating any screen.
- **Touched symbols:** the verification module — `NEW — created in Phase 3`. It follows the shape of
  the shipped derived-set tests `tests/test_keymap.py:165` and `:194` (executed green), which walk
  `mapper.app` and the six `mapper.screens` modules for `Screen` subclasses declared in that module.
- **Validation:** `test (unit)`
- **Executed verification:** the same node as HLR-N16.1, plus a mutation arm that empties the derived
  set and asserts the test turns red.
- **Numeric pass threshold:** derived screen count `>= 7`; the emptied-set mutation arm fails.
- **Acceptance criteria:** **naming the known offenders in the test is forbidden by this LLR.** A
  requirement scoped to `app.py:742`, `:793` and `:1058` is satisfied at those three lines while
  `screens/factory.py:413` and `screens/settings.py:92` keep the defect — which is not hypothetical:
  it is what P-13 did, and §2.8.3 records it.

##### LLR-N16.1.2 — the two undeclared scopes are declared

- **Traceability:** HLR-N16.1
- **Statement:** Every screen class reachable by the operator that binds the help chord shall declare
  a key scope, and the keymap seat shall offer a non-empty binding set for each declared scope.
- **Touched symbols:** `mapper/screens/factory.py::FactoryScreen.KEY_SCOPE` and
  `mapper/screens/settings.py::SettingsScreen.KEY_SCOPE` — both `NEW — created in Phase 3`;
  `mapper/keymap.py::KEYMAP` and `mapper/keymap.py::GROUP_SCOPE` (`keymap.py:52-67`) gain the
  corresponding scope constants and groups.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_help_scope.py -k "every_help_screen_declares_a_scope"`
  *(provisional)*.
- **Numeric pass threshold:** screens binding the help chord with no declared scope `== 0`;
  for each declared scope, `len(bindings_for(scope)) >= 3`, so a scope declared but left empty in the
  seat cannot pass. Pre-state executed (**M-11**): 2 screens undeclared; `FactoryScreen` hand-writes
  **12** bindings and `SettingsScreen` **6**, neither generated from the seat.
- **Acceptance criteria — and the interaction with a shipped fence:** both screens are named in
  `mapper/keymap.py::UNMIGRATED_SCREENS` (`keymap.py:39-44`), whose fence test
  `tests/test_keymap.py:294-315` asserts the list names exactly the classes that are out of the seat.
  **Migrating either screen into the seat therefore requires retiring its entry from that list in the
  same increment**, or the fence test reddens. That is the supersession census for this change,
  recorded at Phase 1 rather than discovered at the gate. `SettingsScreen` is additionally in
  `TAB_BINDING_EXCEPTIONS` (`keymap.py:49`) and binds `tab` (`settings.py:52`), so a full migration
  interacts with the Q-7 surface as well.
- **~~Scope ruling owed at PDR.~~ RULED — `PDR-2026-08-26-ui-next-batch-02#D9`: MIGRATE BOTH
  (`QA-B-10`, §6.5 A-26).** **Declare-only is not an option; it only looked like one.** This LLR's
  own threshold requires `len(bindings_for(scope)) >= 3` for every declared scope, so declaring
  `SCOPE_FACTORY` without migrating would force at least three seat rows that **duplicate**
  hand-written bindings — two declarations of the same key, the exact defect the seat exists to
  abolish. Declare-only therefore fails its own threshold or violates one-declaration-four-readers.
  Executed, the migration is cheaper than it looks: `FactoryScreen` has **12** bindings
  (`factory.py:66-77`), binds no `tab`, and is not in `TAB_BINDING_EXCEPTIONS` — a clean migration.
  `SettingsScreen` has **6** (`settings.py:49-56`), two of which bind `tab` and `shift+tab` to
  **Textual's own focus-traversal actions**: they do not take `tab` from traversal, they re-declare
  it.
- **C-D9a — the `tab` drop on `SettingsScreen` is GATED behind a probe with a WORKING POSITIVE
  CONTROL.** Before the increment removes those two bindings it shall build a probe that observes
  **at least one real focus transition** on `SettingsScreen` with the bindings present. **The PDR's
  own probe was vacuous and is recorded as such rather than banked:**

  ```
  drop_tab=False: distinct_targets=1  transitions=0   sequence: ['None'] x 9
  drop_tab=True : distinct_targets=1  transitions=0   sequence: ['None'] x 9
  ```

  Identical — but `app.focused` is `None` throughout, so the probe **cannot see a focus transition
  at all and therefore cannot fail**. *"Should be behaviour-neutral"* is not evidence. **If the
  control cannot be built, the drop does not ship**: `SettingsScreen` keeps `tab`/`shift+tab` as
  screen-local bindings, stays in `TAB_BINDING_EXCEPTIONS`, and only its other four bindings
  migrate. Both outcomes are acceptable; shipping the drop on an unfalsifiable probe is not.
- **C-D9b — `UNMIGRATED_SCREENS` shrinks to `("EditorScreen", "CoverageScreen")` in the same
  increment**, or the fence at `tests/test_keymap.py:294-315` reddens. This is the supersession
  census for the change and it belongs in that increment's packet, not in a follow-up.
- **C-D9c — `screens/factory.py:343` is NOT touched**, asserted byte-identical at DDR. Carry B-02
  neither closes nor widens in this batch.
- **Consequence for `HLR-N16.1`'s counts (`QA-M-04`).** Migrating adds seat rows, so
  `len(bindings_for(scope))` moves for the two new scopes, and `#D5b`'s three rows move
  `bindings_for('map')` again. **Every count in this requirement is evaluated at run time** and no
  literal is carried across the migration — which is why the counts were pinned to `bindings_for`
  rather than to a number (§6.5 A-06).

#### HLR-N16.2 — the legend names the view and shows its glyph vocabulary in the view's own style

- **Traceability:** US-N16
- **Statement:** When the legend is opened from a view, the system shall paint a title naming that
  view and a vocabulary section in which each glyph row is painted with the same style the view
  applies to that glyph.
- **Rationale (informative):** US-N06 and US-N14 introduce a whole new glyph vocabulary — the fold
  pill, braille dust, the overflow indicator, the lit and dim lens tones, three new hues. Shipping
  them without the legend ships an unexplained language, which is why §2.6 S-5 calls this a
  dependency of the batch and not an extra.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_help_scope.py -k "legend_names_the_view"`
  *(provisional)* — open the legend from each view and compare the painted title and the glyph rows'
  style spans against the styles the corresponding renderer produces.
- **Numeric pass threshold — the floor is DERIVED from the declared vocabulary, and the subject
  includes the screens the defect is on (`QA-M-09`, `QA-M-10`, §6.5 A-36):**
  - **Vocabulary.** For **every** member of the declared vocabulary, the legend's style string equals
    the renderer's style string for that member. The count is `len(declared_vocabulary)`, read from
    the single declaration `LLR-N16.2.1` creates — **not** a floor, and **not a literal written
    anywhere in this document**. The membership predicate is `LLR-N16.2.1`'s and is derived; see
    there.
  - **Title.** The title contains the view's name for each of the three map views **and for each
    non-map screen in the derived screen set** of `LLR-N16.1.1`.
- **~~"over at least 5 glyphs" and "declared glyph count `> 0`"~~ are superseded (`QA-M-09`).**
  **A legend shipping ONE glyph passes both floors.** A floor chosen by hand cannot be the gate on a
  deliverable whose whole content is the vocabulary; the number has to come from the declaration the
  requirement itself mandates.
- **~~"for each of the three map views"~~ is superseded (`QA-M-10`).** **The defect being fixed is on
  NON-map screens.** `LLR-N16.1.2` and P-13 both scope the work to `FactoryScreen`, `SettingsScreen`
  and the three other un-scoped routes — re-executed at `d877784`: 5 un-scoped `HelpScreen()`
  constructions, 2 screens with no `KEY_SCOPE`. A threshold quantified over the three **map** views
  excludes the subject of the change, which is `C-40` limb 1: the predicate could be fully green
  while every screen the story is about still paints the wrong title.
- **Named weaker variant (`M-N16.2-a`):** declare a one-glyph vocabulary and name the three map
  views. Both parked floors green, `AT-043` green, and the legend explains nothing on the screens
  that needed it. Reddened by the derived count and the widened screen set together.
- **Priority:** medium
- **Acceptance:** `AT-043`
- **Value reconciliation (C-36):** the legend title today is `f"atajos · {self.scope}"`
  (`mapper/screens/help.py:61`, executed) — it names the **scope**, not the **view**. The change is
  a change, not a description. The view names are `NEW — created in Phase 3`.
- **Executed constraint on the view accessor:** view family is **two mutually-exclusive booleans**
  `MapScreen.outline_mode` (`app.py:1086`) and `MapScreen.radial_mode` (`app.py:1087`), toggled at
  `:1563-1569`, with a private renderer selector `_current_renderer` at `app.py:1218-1223` and **no
  accessor returning the view's name**. The name accessor is `NEW — created in Phase 3`.

##### LLR-N16.2.1 — the vocabulary and the styles come from one declaration

- **Traceability:** HLR-N16.2
- **Statement:** The glyph vocabulary and the style applied to each glyph shall be declared once and
  read by both the renderer and the legend.
- **Touched symbols:** a glyph-vocabulary declaration in `mapper/darkside.py` —
  `NEW — created in Phase 3`; consumed by `mapper/views/layered.py` and by
  `mapper/screens/help.py::HelpScreen`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_help_scope.py -k "vocabulary_has_one_source"`
  *(provisional)* — for each declared glyph, compare the style the renderer emits against the style
  the legend emits.
- **Numeric pass threshold — DERIVED, WITH NO LITERAL COUNT (`QA-M-09`, `P2-B3`, §6.5 A-36 as
  amended by A-45):** style equality over **every** member of the declared vocabulary; and the
  declared vocabulary **equals** the derived set below, asserted as **set equality** against the
  single declaration, never as `count > 0` and never against a transcribed total. The section
  headers are, in order, `teclas de esta vista` · `vocabulario de esta vista` · `colores con empleo`.

- **THE VOCABULARY CENSUS — question, instrument, SHA. The number is not written; the derivation is.**

  > **QUESTION.** Which distinct glyph rows must the legend paint for this batch, and with which
  > style each?
  >
  > **INSTRUMENT.** Read the vocabulary tables of `01b-ux-decisions.md` DECISION 3 §3.1 through §3.4.
  > Project every row onto the triple `(glyph, label, painted-in style)`. Take the **set of distinct
  > triples**. Remove every triple whose row carries the `DEFERRED(#D7)` marker. The result is
  > `declared_vocabulary`. The colour-with-a-job rows of DECISION 3 §3.5 are a **second, separately
  > derived set** over the same instrument, and are not members of this one.
  >
  > **MEASURED AT.** `20f86de` (`master`, tree clean), the SHA this amendment executes against.
  >
  > **CARDINALITY.** Deliberately **not transcribed**, here or anywhere else in this document. The
  > test reads `len(declared_vocabulary)` from the declaration at run time.

- **WHY THE COUNT IS A DERIVATION AND NOT A CORRECTED LITERAL — this is the trap, and it is real.**
  ~~*"21 rows `V1` through `V21`"*~~ is superseded. The obvious repair — *"correct 21 to 23"* —
  **is wrong twice**, which is why the fix is structural:
  1. **The literal 21 was already stale.** DECISION 3 §3.1 adds `V4a` and `V4b` beneath its main
     table, and §3.1 through §3.4 together carry more labelled rows than the `V1`-through-`V21`
     numbering suggests. A reader counting the `V`-numbers gets one answer; a reader counting the
     table rows gets another.
  2. **And the larger literal would also be wrong**, because `V4` and `V4a` are **byte-identical in
     glyph, label and style** — both `∙ ∙ ∙` / `territorio sin explorar` / `WORDMARK`
     (`01b:277`, `01b:287`). A row-id census counts them twice; the **triple** census counts them
     once, which is what the legend actually paints. Set equality over the triple is not a
     convenience — it is the only projection under which "what the legend paints" and "what the
     declaration says" are the same kind of object.
  3. **And `#D7` removes another.** `V18` (`◍ github` / `◍ del repo`, `01b:315`) is the `◍`
     repo-provenance marker, which `PDR-2026-08-26-ui-next-batch-02#D7` rules **out of this batch**
     — *"not deferred, not ambiguous: out"*. It carries the `DEFERRED(#D7)` marker and the
     derivation removes it. A legend painting `◍ del repo` in this batch would explain a glyph the
     batch does not paint.

  **Four generations of one number in this document have been wrong** (§5.2, §6.5 A-07). A fifth
  literal — even a correct one — would be the fifth generation, correct only until the next row
  moves. `01b`'s DECISION 3 is the declaration's *source*; the declaration is the *authority*; the
  test reads the authority.

- **THE `+ 5 COLOUR ROWS` HALF IS CORRECT AND IS KEPT.** Executed at `20f86de`,
  `01b-ux-decisions.md:325-329` carries exactly five colour-with-a-job rows — `ACCENT`, `WARN`,
  `SAGE`, `TEAL`, `VIOLET` — and `01b:332-333` records that `ALERT` is deliberately absent and gains
  a row only if it gains a second job, which `LLR-S06.3.5` says it does not. **That half of the
  parked threshold was never the defect** and is retained verbatim rather than being swept into the
  correction, because striking a correct clause alongside an incorrect one is how a fold loses work.

- **A CROSS-ARTIFACT EDIT THIS DOCUMENT CANNOT MAKE — routed, not assumed (`P2-B3`, `C-44`).** The
  stale literal is live at **four** sites. Three are in this file and are amended above and at
  §6.5 A-45. **The fourth was `01b-ux-decisions.md:373`**, which read *"The vocabulary specified
  above is **21 rows** (V1–V21)"*. That file belongs to the **ux lane** and was not this document's
  to edit, so the edit was **routed** rather than assumed.

  **DISCHARGED 2026-08-27 — the routed edit LANDED.** The orchestrator applied it: the literal is
  replaced by a pointer to this threshold's derivation, carrying a `⚠` note that records *why the
  obvious repair was wrong* — the table holds **23** labels, but `V4` and `V4a` are byte-identical in
  glyph, label and style, so striking the duplicate yields **22**, and *"correct 21 to 23"* would
  have been wrong **twice**. The two artifacts no longer disagree. **This row is closed by
  re-reading the amended `01b`, not by trusting that the routing happened** — a conditional
  discharge is not an authorisation (C-44).
- **Acceptance criteria:** the legend is otherwise a **second** declaration of the visual language,
  and a second declaration drifts. This is the same one-owner argument as R-014 for matching and
  R-013 for fold, applied to the glyph vocabulary.
- **Ordering constraint, recorded (restated against §5.4, `P2-B1`):** the vocabulary half lands in
  **`Inc-8`**, late in the serial order, **because** it must render what `Inc-3` and `Inc-5` actually
  paint. A legend written before the vocabulary exists documents an intention.
  *(~~"`PLAN.md` §6 sequences Inc-7 last"~~ is superseded twice: `Inc-7` is US-N13 under the ratified
  cut, and the legend is not last — `Inc-9` is, and `Inc-8` before `Inc-9` is a hard ordering. The
  constraint itself is unchanged and is now stated against §5.4, the document's single cut.
  `Inc-5`'s contribution survives the US-N14 deferral: it is hit painting, which the legend's
  vocabulary rows describe.)*

##### LLR-N16.2.2 — an empty vocabulary omits the section

- **Traceability:** HLR-N16.2
- **Statement:** If the view opened from has no declared glyph vocabulary, then the system shall omit
  the vocabulary section and shall paint the key rows unchanged.
- **Touched symbols:** `mapper/screens/help.py::HelpScreen.compose` (`help.py:59`) and
  `HelpScreen._render_keymap` (`help.py:66`).
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_help_scope.py -k "empty_vocabulary"` *(provisional)*
  — open the legend from a screen with no canvas.
- **Numeric pass threshold:** **0** vocabulary rows painted; key row count equals
  `len(bindings_for(source.KEY_SCOPE))`.
- **Acceptance criteria:** a section header with nothing under it reads as a bug, and the screens
  with no canvas are the majority of the derived set.

##### LLR-N16.2.3 — binding labels reaching the legend are coerced

- **Traceability:** HLR-N16.2, risk A-7
- **Statement:** The system shall coerce **every file-derived string placed on the legend surface**
  through the design module's plain-text coercion.
- **WIDENED from "every binding label and every glyph-row caption" (C-5, `02b` S-06, §6.5 A-16).**
  The parked scope named the two strings the author was thinking about. The legend's vocabulary half
  carries **captions describing glyphs painted from file-derived branch names**, and the title half
  carries the view name; neither is a binding label nor a glyph-row caption as those terms were
  used. The scope is therefore every file-derived string on the surface, with fixture positions
  **derived from `_build_sidecar`**.
- **Touched symbols:** `mapper/darkside.py::plain` (`darkside.py:276`);
  `mapper/screens/help.py::HelpScreen._render_keymap` (`help.py:66-77`, executed — it assembles
  `binding.glyph` and `binding.label` directly with no coercion today); the vocabulary section and
  the title — `NEW — created in Phase 3`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_help_scope.py -k "legend_coerces_labels"`
  *(provisional)* — a synthetic seat entry and a vocabulary caption, each carrying Rich markup, a
  constructed C0 byte and a constructed `U+202E`, at positions derived from `_build_sidecar`.
- **Numeric pass threshold (C-4, §6.5 A-13):** measured **on the painted row**, read through
  `_rows_in(screen, dialog.region)` (`tests/test_repair_layout.py:74`) so a composited backdrop
  cannot contribute — **0** occurrences of any code point in `COERCION_RANGES` (§3.0); **0** Rich
  markup tags interpreted; **the painted row length equals the legend's declared row width for every
  hostile input**; and the **split-at-width arm** passes.
- **THE ROW-LENGTH CLAUSE IS NEW, AND THIS WAS THE ONE OF THE FOUR THAT HAD NONE (C-5, §6.5 A-17).**
  `02b` C-5's last sentence is *"add the missing row-length clause to `LLR-N16.2.3`."* `LLR-N06.2.3`,
  `LLR-N13.2.1` and `LLR-N14.2.3` each bounded the painted row; this one did not, so a caption that
  overflowed its column satisfied the parked threshold while breaking the panel's geometry — and the
  panel's geometry is what `HLR-N16.1`'s oracle clips to. An unbounded row here would make the
  oracle's `x` clip drop real content and read as a missing binding.
- **Named weaker variant (`M-N16.2.3-a`):** coerce the binding label, leave the vocabulary caption.
  Green today, because the vocabulary section does not exist yet, and red the moment **`Inc-8`**
  (§5.4) lands the half that carries file-derived branch names. The widened statement is what makes
  it red at authoring time rather than at the gate. *(~~Inc-7~~ — stale 7-cut number; `P2-B1`.)*
- **Acceptance criteria:** binding labels are Spanish UI strings from the seat today and are not
  file-derived, so **that half** is the lowest-risk member of the A-7 family. The vocabulary half is
  not: it describes glyphs painted from file-derived branch names, and the sink is the same one.

#### HLR-N16.4 — the legend declares every key that works inside the legend

- **Traceability:** US-N16; `UX2-C-05`
- **Statement:** The set of key rows the legend paints for its own scope shall equal the set of keys
  that have an effect while the legend is open, including the keys that scroll it.
- **Rationale (informative):** US-N16's promise is *"`?` explains **this** view — its keys and its
  glyph vocabulary"*. **The legend is a view**, and it is the one view whose keys it does not
  explain. Executed at 118 x 34 through the real `question_mark` chord:

  ```
  bindings_for('map') = 27        visible at rest = 16/27     max_scroll_y = 14
  the legend's own declared keys  : escape -> 'esc cerrar' · q -> 'q cerrar'      (2)
  real 'down'     x9  ->  scroll_y 0 -> 9    declared in help scope? False
  real 'pagedown' x9  ->  scroll_y 0 -> 14   declared in help scope? False
  real 'end'      x9  ->  scroll_y 0 -> 14   declared in help scope? False
  union over real-key scroll positions       : 27/27
  ```

  **All three scroll keys work; none is declared.** Eleven of the twenty-seven map-scope rows sit
  below the fold at rest, reachable only by a key the panel never mentions. The content is all there
  — `27/27` under the union — so this is **purely a discoverability defect**, and it lands on the one
  screen whose entire job is discoverability.
- **THE DEFECT GETS WORSE INSIDE THIS BATCH, WHICH IS WHY IT IS A REQUIREMENT AND NOT A NOTE.**
  `LLR-N16.2.1` adds the glyph vocabulary and the colour rows beneath the existing bindings, roughly
  tripling the scrollable content. **The two sections this story exists to add land furthest below
  the fold**, behind the affordance nobody is told about. Shipping US-N16 without this requirement
  ships a legend whose new content is less discoverable than the content it already had.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_help_scope.py -k "legend_declares_its_own_keys"`
  *(provisional)* — open the legend with the real chord, read `bindings_for` for the legend's own
  scope, and press each **real** scroll key.
- **Numeric pass threshold:** the set of keys with a measured effect while the legend is open
  **equals** the set the legend paints for its own scope — set equality, derived by pressing each
  real key and observing `scroll_y` or the screen stack, **never** by reading the seat alone.
- **THE ASSERTION IS A KEYSTROKE, AND THE SHIPPED GUARD SHOWS WHY.** `tests/test_repair_layout.py`
  scrolls the panel with `pane.scroll_to(...)` — **a method call, not a keystroke** — so it proves
  the container scrolls and says nothing about whether an operator can make it scroll. Neither named
  mutant of `HLR-N16.1` catches that. `C-16` applies verbatim: calling the method in place of the
  key press is not acceptance.
- **Named weaker variant (`M-N16.4-a`):** add the three scroll rows to the seat and assert the seat
  contains them. Green without pressing anything, and green if a later change makes the container
  non-focusable so the keys stop arriving. Reddened by the measured-effect side of the equality.
- **Priority:** medium
- **Acceptance:** `AT-053`
- **Owning increment:** **`Inc-8`** (§5.4), which owns `screens/help.py` and is where the vocabulary
  lands. It adds seat rows, so `Inc-8` joins `keymap.py`'s collision set and shall re-run
  `duplicate_chords()` and the whole-seat pin — ~~**and its rows count against `#D10`'s cap**, which
  §3.4 already routes to the PDR lane as arithmetically breached.~~ **STRUCK 2026-08-27 by
  `PDR-addendum-3#D25`: there is no cap for `Inc-8`'s rows to count against.** `Inc-8` owes
  `C-D25a` — its **own** declared seat diff, asserted equal to the entry/exit difference of
  `bindings_for(scope)` — and nothing else. Do not cite the bare `#D10` here; it resolves to two
  different decisions (`B-34`).
- **⚠ ROUTED — a design question this requirement deliberately does not answer.** Whether a flat
  scrolling panel of roughly forty-four rows is the right information design for the legend, versus
  a two-pane or tabbed layout, is a **ux ruling**, not a requirements edit. `01b` §3.8 already
  measured that the content does not fit and said so. **This requirement fixes the discoverability
  defect under either outcome** — whatever the container becomes, the keys that operate it are
  declared — and the orchestrator shall route the layout question to the ux lane.

#### HLR-N16.3 — the doubled chord is reserved

- **Traceability:** US-N16
- **Statement:** When the operator presses the help chord twice in succession, the system shall
  produce a declared outcome that does not open a second legend on top of the first.
- **Rationale (informative):** the guía is batch 3. Reserving the chord **now**, in writing, is what
  stops a later batch finding it taken by accident — §2.6 S-5 calls the reservation a requirement,
  not an omission.
- **Validation:** `test (pilot)`
- **Executed verification:** `pytest tests/test_help_scope.py -k "doubled_help_chord_is_reserved"`
  *(provisional)* — press the real `question_mark` chord twice from `MapScreen` and count the
  screens on the stack.
- **Numeric pass threshold:** screen-stack depth after 2 presses equals the depth after 1 press;
  **0** exceptions raised.
- **Priority:** low
- **Acceptance:** `AT-044`
- **Mechanism note — `01b-ux-decisions.md` DECISION 6 row 12, executed by the ux lens.** Textual has
  **no chord support**: a binding written as two comma-separated key names fires on the **first**
  press, because the comma means *alternatives*, not *sequence*. A real doubled chord needs a
  hand-built timer or state machine. **This requirement deliberately does not ask for one** — it asks
  only that a second press produce a declared outcome and not stack a second legend, which the
  shipped `MODAL_SCOPES` behaviour already satisfies. The chord is reserved in writing; building it
  is batch 3's problem, with 01b's transcript in hand.
- **A second reservation owed, same reason** (`01b-ux-decisions.md` §3.7): the `minus` key belongs to
  *relieve*, which the batch order places in batch 4 and `PLAN.md` §4 declares out of scope.
  Executed: `minus` arrives as itself and is bound in no scope. It **shall** be reserved in writing
  alongside the doubled help chord, so batch 4 does not find it taken by accident. Audit row §6.4
  D-7.
- **Value reconciliation (C-36):** executed (**M-9**), neither a literal `"?"` key nor a doubled
  form is bound in **any** scope; the help chord ships as `KeyBinding("question_mark", "?", "help",
  "ayuda", "app")` at `mapper/keymap.py:150`. `HelpScreen` already carries its own scope's bindings
  (`help.py:26-29`) and `MODAL_SCOPES = (SCOPE_PALETTE, SCOPE_HELP)` (`keymap.py:157`) already
  excludes app-scope bindings from modal scopes, so `bindings_for("help")` returns exactly
  `[('escape','dismiss_none'), ('q','dismiss_none')]` — which is **why a second press does not
  re-open help today**. Executed under Pilot at 140 x 45 (**M-16**): screen-stack depth is 3 before,
  **4** after one real `question_mark` press, and **4** after two. This requirement pins that as
  intentional rather than incidental.
- **Recorded honestly:** the pre-state of `AT-044` is green on `master`. Its non-trivial arm is the
  mutation that removes `SCOPE_HELP` from `MODAL_SCOPES` and must turn it red — a plausible-wrong
  implementation, not a deletion (risk R-2, verbatim).

---

### 3.9 · Two shipped defects repaired inside this batch *(Inc-REPAIR)*

> **Why these ride here and not in a follow-on batch (operator ruling, amendment set 3).** Both are
> **mechanical fixes on a shipped defect**, not design rulings: each has one measured cause, one
> observable consequence and a fix of one or two lines. Neither needs a PDR decision. They are
> `02g` §5's `S-22` and `S-23`, renamed to the batch's own defect series as **`B-29`** and **`B-30`**
> so the repair series and the security-lens series do not share a numbering space.
>
> **`B-29` is not merely adjacent to this batch — it is inside it.** `LLR-N13.1.5`'s containment
> arm, which `AT-025b` drives and which `HLR-N13.3` now leans on entirely after `#D24`, **does not
> engage on the current tree**. Shipping US-N13 without `B-29` ships a green containment test over a
> structurally empty set.

#### Acceptance (black-box) — the repair pair

- **Observable outcome:** a workspace holding a map whose sidecar names a node the `.mmd` does not
  define produces a card that **says so**, instead of a card that silently reports a coverage
  denominator larger than the map; and a map that cannot be found produces a message naming the map,
  not the operator's home directory.
- **Shipped surface:** `HomeScreen`'s recents rows and the toast raised through
  `MapperApp.load_or_notice` (`mapper/app.py:450-462`), observed through the rendered text of
  `#home-recents` and through the notification body.
- **Deliverable + observation:** a painted card in the declared damaged state for the phantom-bearing
  map and true values on every other card; and a painted toast body containing the map id and
  containing **no** path separator and **no** component of the workspace path.
- **Acceptance tests:** `AT-049`, `AT-050`.
- **Boundary catalog (QC-3):**
  - ☑ **error** — `AT-049` drives a workspace whose sidecar carries a node id matching no parsed
    `.mmd` node, and asserts the warning arm fires and the card enters the damaged state.
  - ☑ **empty** — `AT-049`'s negative arm drives the same workspace with the phantom removed and
    asserts **no** warning and a healthy card, so the positive arm is not passing on a constant.
  - ☑ **invalid** — `AT-050` requests a map id that does not exist and reads the painted toast.
  - ☑ **boundary** — `AT-050` requests a map id that is itself a path-like string, and asserts the
    message still names only the id.

#### HLR-REPAIR.1 — a map the store cannot fully parse is declared, and no message discloses the filesystem

- **Traceability:** `02g` §5 `S-22` and `S-23`; risk **A-7**; and `LLR-N13.1.5`, whose containment
  arm this HLR is the precondition for
- **Statement:** When the store cannot fully reconcile a map's sidecar against its parsed graph, the
  load shall record a warning that reaches the operator-facing surface; and no operator-facing
  message raised by the store shall contain a filesystem path.
- **Rationale (informative):** the two halves share one owner — `mapper/store.py`'s load path — one
  increment and one review. Splitting them into two HLRs would put one source file under two owners,
  which is the collision `#D5` exists to prevent. They are two LLRs under one HLR for that reason,
  not because they are one defect.
- **Validation:** `test (pilot)` + `test (unit)`
- **Executed verification:** `pytest tests/test_store.py -k "repair_pair"` *(provisional)* — see the
  two owned LLRs.
- **Numeric pass threshold:** the conjunction of `LLR-REPAIR.1` and `LLR-REPAIR.2`.
- **Priority:** high — `LLR-REPAIR.1` gates `Inc-7` (§5.4), because without it `AT-025b` is vacuous.
- **Owned LLRs:** `LLR-REPAIR.1` (`B-29`, which owns `AT-049`) and `LLR-REPAIR.2` (`B-30`, which
  owns `AT-050`). **This HLR deliberately carries no `Acceptance:` line of its own.** Each `AT` here
  observes one defect through one surface with one fixture, so claiming both at HLR level *and* at
  LLR level would put one id on two chains — the defect `QA-M-12` raised against `AT-025` and
  `AT-007`. One id, one owner.
- **Owning increment:** **`Inc-REPAIR`** (§5.4), sequenced **before `Inc-7`**.

##### LLR-REPAIR.1 — a phantom sidecar id records a load warning *(`B-29`)*

- **Traceability:** HLR-REPAIR.1
- **Statement:** When the sidecar declares a node id that the parsed `.mmd` does not define, the
  store shall append a load warning naming that id, and shall not change the meaning of the coverage
  values it returns.
- **⚠ THE THRESHOLD IS QUANTIFIED OVER **EVERY** PHANTOM ID, NOT OVER THE FIXTURE'S ONE
  (`S-24`, security lens, 2026-08-27).** The statement above already quantifies correctly — *"a node
  id"*, per id — but the **numeric threshold was written for the one-phantom fixture**, so a
  **warn-once-then-silent** implementation passes it. Measured: **10 phantoms inflate the denominator
  by 10.** Threshold, restated: for a sidecar declaring **N** phantom ids, `len(load_warnings)`
  attributable to this cause **shall equal N**, and the **set of named ids shall equal the set of
  phantoms** — set equality, not a count, so a warning naming the same id twice cannot satisfy it.
  Reddened by `M-REPAIR.1-c`: warn on the first phantom only, which is green under the old threshold
  and RED under this one.
- **Touched symbols:** `mapper/store.py` — the sidecar node-ingest branch at `store.py:400-401`,
  which today reads *"if the id is not in `graph.nodes`, add a node"*;
  `mapper/model.py::Graph.load_warnings` — **existing**, the same channel the duplicate-id and
  malformed-field records already use (`store.py:398`, `:407`).
- **Validation:** `test (unit)` + `test (pilot)`
- **Executed verification:** `pytest tests/test_store.py -k "phantom_sidecar_id_warns"`
  *(provisional)* — load a synthetic workspace whose sidecar names an id absent from the `.mmd`,
  assert `graph.load_warnings` is non-empty and names the id; then mount `HomeScreen` and assert the
  card enters the damaged state through `load_or_notice`'s warning arm.
- **Numeric pass threshold:** on the synthetic fixture, `len(graph.load_warnings) >= 1` and the
  offending id appears in one of them; `HomeScreen` paints the declared damaged card state for that
  map and true values for every other map in the workspace. **Executed pre-state, `20f86de`:**
  `coverage() = (2, 3)` with `warnings = []` — the denominator already carries the phantom and
  nothing anywhere says so.
- **THE FIX IS THE WARNING, NOT `coverage()`.** Changing `coverage()`'s semantics is **explicitly
  out of scope**: three call sites agree on its current meaning and `LLR-N13.1.3` pins one of them
  at 100. **The defect is silence, not arithmetic.** A repair that "corrects" the denominator would
  be a behaviour change riding inside a defect fix, and would redden `LLR-N13.1.3` for no stated
  reason. Recorded because *"while I was in there"* is how a one-line repair becomes a regression.
- **THE GUARD IS A NO-OP ON THE CURRENT TREE, SO THE FIXTURE IS MANDATORY, NOT OPTIONAL (`C-55`
  limb 2).** This is the load-bearing clause of the whole LLR. **No fixture in the repository carries
  a phantom sidecar id** — executed: the sidecar ingest branch at `store.py:400-401` is reachable,
  but nothing on disk reaches it. Therefore `LLR-N13.1.5`'s containment arm, `AT-025b`, and this
  requirement's own threshold are **all green over an empty set** unless a fixture is built.
  **This LLR mandates a synthetic fixture carrying exactly that case** — a `.mmd` and a
  `_nodos.yml` where the sidecar declares one id the `.mmd` does not — constructed in a
  `tempfile.mkdtemp` workspace, **never** by writing into `fixtures/`. *(The `fixtures/` prohibition
  is not stylistic: `02g` §6 records that a probe pointed at the real `fixtures/` directory
  permanently rewrote `fixtures/legacy.mmd` and `fixtures/legacy_nodos.yml` through the inspector's
  commit-on-blur.)* **Without the fixture the guard is untested however green the suite**, which is
  precisely the shape of defect this batch has shipped twice.
- **Named weaker variant (`M-REPAIR.1-a`):** append the warning, and validate it against the existing
  `legacy` fixture. Green — because `legacy` has no phantom, the warning list is empty, and an
  assertion that the list "contains no unexpected entries" passes. **The absence is admitted as
  evidence with no positive control proving the oracle can produce a non-absence.** Reddened by the
  mandated synthetic fixture and by the negative arm that removes the phantom and asserts the warning
  disappears.
- **Named weaker variant (`M-REPAIR.1-b`):** drop the phantom node instead of warning about it. The
  denominator becomes correct and the card looks healthy — and the operator is never told their
  sidecar and their map disagree, which is the datum US-N13's whole story exists to surface.
  Reddened by the damaged-card-state clause.
- **Acceptance:** `AT-049`
- **Value reconciliation (C-36):** `store.py:384-388` already **states this defect in a comment**,
  honestly and in full — *"a sidecar id matching no parsed node is still added alongside the parsed
  ones and still moves `coverage()`'s denominator. That is outside this batch's fence."* It was
  outside the **repair batch's** fence. It is inside **this** one, because US-N13 paints that bar.
  The change is a change, not a description.

##### LLR-REPAIR.2 — a store message names the map, not the path *(`B-30`)*

- **Traceability:** HLR-REPAIR.1, risk **A-7**
- **Statement:** Every exception message the store raises to an operator-facing surface shall
  identify the map by its id and shall contain no filesystem path.
- **Touched symbols:** `mapper/store.py::MapStore.load` (`store.py:456`) — the not-found raise, which
  today interpolates the constructed absolute path; rendered through `str(exc)` at
  `mapper/app.py:453` and `mapper/app.py:1181`.
- **Validation:** `test (unit)`
- **Executed verification:** `pytest tests/test_store.py -k "not_found_names_the_map"`
  *(provisional)* — request an absent map id from a store rooted at a `tempfile.mkdtemp` workspace
  whose path contains a recognisable sentinel component, and assert the sentinel does not appear in
  `str(exc)`.
- **Numeric pass threshold:** **0** occurrences of the workspace path, of any of its components, and
  of the platform path separator in the raised message; the map id appears exactly once. **The
  assertion is on the sentinel, not on the literal word "path"** — a message can disclose a home
  directory without containing any word a keyword check would look for.
- **Named weaker variant (`M-REPAIR.2-a`):** interpolate the file's **basename** instead of the full
  path. It removes the username and looks like the fix — and it still emits `<id>.mmd`, so the
  message now discloses the store's on-disk naming convention while reading as repaired. Reddened by
  the path-separator clause only if the basename carries one; **it does not**, so this variant is
  reddened instead by the *"the map id appears exactly once"* clause, which `<id>.mmd` fails on the
  id-plus-extension form. Named because it is the fix an implementer reaches for first.
- **Acceptance:** `AT-050`
- **Value reconciliation (C-36):** the raise sits **four lines above** a comment recording that this
  exact class — *"an `OSError` carried its full absolute path — username included"* — was closed by
  the repair batch's threshold 3 (`store.py:458-460`). **The comment is true about the reads it
  describes and false about the line above it.** That is the sharpest available argument for why a
  defect class needs a derived census rather than a fixed set of addresses, and it is the same
  argument `LLR-N06.2.5` makes for `notify`. Recorded here rather than in a review note, because a
  comment asserting a class is closed is more dangerous than no comment at all.
- **Byte-hygiene note:** the sentinel path component is constructed at test time and no real user
  path is written into a test file or an evidence artifact.

---

## 4. Information Flow Contract (IFC)

> **Part B applies: yes.** The TUI boundary has components a consumer addresses independently —
> a consumer selects a widget by id and indexes what it paints. Part A (Flow) is owed unconditionally.
>
> **Every `consumers` list below was DERIVED**, by grepping the declared literal address across the
> tracked product and test sources, not copied from a comment or from a prior document. The IFC
> template's own worked example records that a hand-maintained dependant list was wrong three times
> in a row; that is not a warning about carelessness, it is a fact about what such lists do.
>
> **`consumers : none` is written explicitly wherever it is true.** An omitted field is a question
> nobody asked, and the validator treats the two differently.

### 4.1 · Part A — Flows

```
FLOW: canvas_paint
  SOURCE : the loaded Graph (mapper/store.py::MapStore.load) plus the operator's key events
  NODES  :
    - fn    : MapScreen.refresh_canvas builds a ViewState
      owner : LLR-N06.1.1
      in    : graph, pan offsets, folded id set, focus owner, hit set, lens match set
      out   : ViewState (frozen, fully defaulted)
    - fn    : IRenderer.render
      owner : LLR-N07.2.2
      in    : Graph, ViewState
      out   : rich.Text
    - fn    : Canvas.rows composing cells, bits, dots and bgs
      owner : LLR-CNV.1.2
      in    : four cell layers
      out   : list[rich.Text], exactly h rows of exactly w cells
  SINK   : the #map-canvas widget, and mapper/export.py::save_svg when the operator exports
```

```
FLOW: match_set
  SOURCE : the operator's query text, typed into the #search-input widget or the lens input
  NODES  :
    - fn    : SearchIndex.query   (free text)
      owner : LLR-N07.1.2
      in    : str
      out   : list[str] of node ids, dict-insertion order
    - fn    : parse_lens          (key:value terms)
      owner : LLR-N14.1.1
      in    : str
      out   : LensQuery carrying terms and the unresolved-key set
    - fn    : lens_hits
      owner : LLR-N14.1.2
      in    : Graph, LensQuery
      out   : list[str] of node ids
    - fn    : tree-order re-ordering
      owner : LLR-N07.3.1
      in    : list[str] in dict-insertion order
      out   : list[str] in pre-order tree order
    - fn    : ViewState.hits / ViewState.lens_matches construction
      owner : LLR-N14.2.1
      in    : list[str]
      out   : frozenset[str]
  SINK   : the #map-canvas widget (tone only) and the count line
```

```
FLOW: overflow_declaration
  SOURCE : the loaded Graph and the current ViewState
  NODES  :
    - fn    : unpainted set difference (graph node set minus painted node set)
      owner : LLR-N06.3.1
      in    : Graph, the render's painted id set
      out   : int, the unpainted count
    - fn    : fold pill construction, one per painted folded branch
      owner : LLR-N06.2.3
      in    : branch id, its descendant count
      out   : rich.Text pill
  SINK   : the #map-pagination widget region and the canvas pill cells
```

```
FLOW: home_cards
  SOURCE : the workspace directory listing and each map's Graph (MapStore.load)
  NODES  :
    - fn    : HomeScreen._map_metrics
      owner : LLR-N13.1.1
      in    : Graph
      out   : dict of total, con_acta, sin_acta, vencen, coverage
    - fn    : coverage percentage, one definition
      owner : LLR-N13.1.3
      in    : (have, req) from Graph.coverage
      out   : int percent
    - fn    : darkside.microbar
      owner : LLR-N13.1.2
      in    : count, total, width
      out   : rich.Text of exactly width cells
    - fn    : darkside.plain coercion of every file-derived title
      owner : LLR-N13.2.1
      in    : str from disk
      out   : str with no code point in COERCION_RANGES and no live markup
  SINK   : the #home-recents rows and the #home-empty region
```

> **COERCION IS DECLARED ON EVERY FLOW THAT CARRIES FILE-DERIVED TEXT, NOT ON ONE (`S-21`,
> §6.5 A-60).** Executed at `ea1fbf9`, exactly **one** node in the whole of §4.1 named coercion —
> the `home_cards` node above — while `canvas_paint`, `match_set` and `legend` all carry strings
> read from disk to a painted surface and declared no coercion step at all. **A flow contract that
> declares a control on one of four paths says the other three do not need it**, which is the
> §2.1b failure this batch has now met at three different surfaces.
>
> **The coercion node is therefore a CLASS, owned by `HLR-COERCE` (§3.0), and it is declared on
> each carrying flow rather than restated per flow:**
>
> ```
> NODE (class, applies to every flow whose SOURCE includes file-derived text):
>     - fn    : darkside.plain over COERCION_RANGES, before the value reaches its sink
>       owner : HLR-COERCE  (surface thresholds: LLR-N06.2.3 canvas_paint ·
>               LLR-N13.2.1 home_cards · LLR-N16.2.3 legend)
>       in    : str from disk
>       out   : str with no code point in COERCION_RANGES and no live markup
>       where : canvas_paint, home_cards, legend
> ```
>
> **`match_set` is declared coercion-free, and that is a claim with a reason, not an omission.** Its
> SOURCE is *the operator's query text*, typed at the keyboard — not read from a file — and its
> output is a list of node **ids** used as keys, never painted directly. The strings it causes to be
> painted are painted by `canvas_paint`, which carries the class. **`consumers : none` is written
> explicitly wherever it is true** (§4's own convention), and the same rule is applied here to a
> control: *"this flow does not need coercion"* is recorded, so the next reader does not have to
> re-derive whether its absence was a decision or an oversight.
>
> **The per-flow `owner` lines are unchanged.** Each surface LLR keeps its own threshold, measured on
> its own painted row, because the row width and the clipping region differ per surface — which is
> exactly why `HLR-COERCE` owns the class and not the thresholds.

```
FLOW: legend
  SOURCE : the source screen's declared KEY_SCOPE and the glyph-vocabulary declaration
  NODES  :
    - fn    : keymap.bindings_for(scope)
      owner : LLR-N16.1.2
      in    : scope str
      out   : list[KeyBinding], a pure read of the seat
    - fn    : HelpScreen._render_keymap
      owner : LLR-N16.2.3
      in    : list[KeyBinding]
      out   : rich.Text grouped by binding group
    - fn    : glyph-vocabulary row construction, styles read from the shared declaration
      owner : LLR-N16.2.1
      in    : the declared vocabulary
      out   : rich.Text rows
  SINK   : the #help-title and #help-content widgets
```

### 4.2 · Part B — Boundary decomposition

```
COMPONENT: map_screen
  PARENT : SYSTEM
  SURFACE: map
  INPUTS : graph: Graph ; map_id: str ; terminal_size: Size ; key_events: Key
           ; cursor: str|None ; folded: frozenset[str] ; state: ViewState
           ; node_id: str|None ; query_text: str ; active_groups: Sequence[str]
  OUTPUTS:
    - id          : map_body_regions
      value       : the three side-by-side map regions
      address     : query("#map-body").children, INDEXED POSITIONALLY
      cardinality : 3
      consumers   : mapper/app.py
                    tests/test_rail.py
      owner       : LLR-S07.1.1
    - id          : rail_tree_rows
      value       : re-declared here from COMPONENT rail so containment is checkable
      address     : query_one("#map-rail")
      cardinality : 1
      consumers   : mapper/app.py
      owner       : LLR-N06.2.1
    - id          : painted_map
      value       : re-declared here from COMPONENT canvas
      address     : query_one("#map-canvas")
      cardinality : 1
      consumers   : mapper/app.py
      owner       : LLR-N06.1.1
    - id          : canvas_rows
      value       : re-declared here from COMPONENT canvas
      address     : Canvas.rows() return value, INDEXED POSITIONALLY
      cardinality : h rows of exactly w cells, both taken from ViewState
      consumers   : mapper/app.py
      owner       : LLR-CNV.1.2
    - id          : ficha_fields
      value       : re-declared here from COMPONENT inspector
      address     : query_one("#map-inspector")
      cardinality : 8 focusable descendants on the legacy fixture
      consumers   : mapper/app.py
      owner       : LLR-N14.3.2
    - id          : declared_unpainted_total
      value       : re-declared here from COMPONENT overflow_indicator
      address     : query_one("#map-pagination")
      cardinality : 1
      consumers   : mapper/app.py
      owner       : LLR-N06.3.1
    - id          : fold_pills
      value       : re-declared here from COMPONENT overflow_indicator
      address     : the pill cells inside query_one("#map-canvas")
      cardinality : one per painted folded branch, 0 when nothing is folded
      consumers   : none
      owner       : LLR-N06.2.3
    - id          : match_count_line
      value       : re-declared here from COMPONENT search_bar
      address     : query_one("#search-input"), and the count region beside it
      cardinality : 1
      consumers   : mapper/app.py
      owner       : LLR-N07.2.1
    - id          : keybar_groups
      value       : re-declared here from COMPONENT keybar
      address     : keymap.groups_for_keybar(active_groups) return value, INDEXED POSITIONALLY
      cardinality : one entry per requested group, in the requested order
      consumers   : mapper/app.py
      owner       : LLR-N16.1.2
    - id          : leaf_fold_notice
      value       : the toast raised when the operator folds a node with no descendants
      address     : App.notify, title "nada que plegar"
      cardinality : 1 per fold of a childless node, 0 otherwise
      consumers   : none
      owner       : LLR-N06.2.2
```

> **Why `map_screen` re-declares its children's inputs and outputs (§6.5 A-19, `QA-B` V12 / F-14).**
> `devflow-validate.py`'s `V12` is a **set operation**: a child component's `INPUTS` names must be a
> subset of its parent's, and its `OUTPUT` ids must appear on the parent. The parked block declared
> four inputs and one output, so the seven child components between them raised **12 blocks** — the
> child list was right and the parent's was short. Re-declaring is the correct fix rather than a
> workaround: `MapScreen` genuinely *does* own `folded` (`LLR-N06.2.1` makes that the requirement),
> genuinely *does* compose `state`, and genuinely *is* the widget whose region carries every one of
> those outputs. The child blocks below stay as the authoritative descriptions — value, consumer
> list and owner — and the rows here exist so containment is **checkable** rather than asserted.
> `leaf_fold_notice` is added by amendment for `02b` C-8; it was a text sink no contract row named.
>
> **`map_body_regions`'s owner stays `LLR-S07.1.1`, and that is a deliberate ruling (§6.5 A-01).**
> `LLR-S07.1.1` is `SUPERSEDED` with the rest of §3.1 (D16), but the three regions still exist and
> are still consumed positionally, so the contract row survives its owner's supersession. The
> **implementing** requirement is now the repair batch's `LLR-R04.1`
> (`.dev-flow/2026-08-26-repair-batch/01-requirements.md:190` — *"`#map-rail` shall declare a width
> equal to `rail.RAIL_WIDTH`"*). It is **not** written into the `owner` field, and this was measured
> rather than assumed: the validator's `V21` resolves owners against ids **declared as headings**
> (`_declared_ids`, `devflow-validate.py:587`), and the repair batch declares `LLR-R04.1` inline in a
> bullet, not as a heading. Naming it here produced a **new `V21` block that did not exist before
> this amendment** — a regression introduced while fixing `V12`, caught by re-running the validator
> and reverted rather than shipped. The corpus-resolvable owner is the superseded id; the shipped
> implementation is named in prose, where nothing has to resolve it.

```
COMPONENT: rail
  PARENT : map_screen
  SURFACE: map
  INPUTS : graph: Graph ; cursor: str|None ; folded: frozenset[str]
  OUTPUTS:
    - id          : rail_tree_rows
      value       : the outline tree with per-branch missing-field counts and fold state
      address     : query_one("#map-rail")
      cardinality : 1
      consumers   : mapper/app.py
                    tests/test_rail.py
      owner       : LLR-N06.2.1
```

```
COMPONENT: canvas
  PARENT : map_screen
  SURFACE: map
  INPUTS : graph: Graph ; state: ViewState
  OUTPUTS:
    - id          : painted_map
      value       : the rendered map picture, including fold pills and braille edges
      address     : query_one("#map-canvas")
      cardinality : 1
      consumers   : mapper/app.py
                    mapper/motion.py
                    tests/test_rail.py
      owner       : LLR-N06.1.1
    - id          : canvas_rows
      value       : the composed cell rows behind painted_map
      address     : Canvas.rows() return value, INDEXED POSITIONALLY
      cardinality : h rows of exactly w cells, both taken from ViewState
      consumers   : mapper/views/lane.py
                    mapper/views/layered.py
                    mapper/views/radial.py
      transitive observers :
                    mapper/export.py   (snapshots the SINK, never indexes rows())
      owner       : LLR-CNV.1.2
```

> **`canvas_rows` is the row this batch's second A3 is about.** Its `value` widens (two new layers
> reach the output) while its `address` and `cardinality` are unchanged — which is precisely the
> case the template's batch-79 story is the inverse of.

- **THE CONSUMER LIST IS CORRECTED IN TWO PLACES, AND IT WAS WRONG IN TWO DIFFERENT WAYS
  (`P2-C1`, `C-D4a`, §6.5 A-51).**

  > **QUESTION.** Which call expressions invoke `Canvas.rows()` and therefore index this contract
  > positionally?
  >
  > **INSTRUMENT.** An `ast` walk over `mapper/**/*.py` and `tests/**/*.py` selecting `Call` nodes
  > whose `func` is an `Attribute` named `rows` bound to a `Canvas`. **Not grep** — grep cannot
  > separate a call from a mention, which is the `C-42` rider this batch has already been bitten by.
  >
  > **MEASURED AT.** `3fe0e4b`. **Cardinality deliberately not transcribed** into a threshold; the
  > derivation is the gate.

  1. **`mapper/views/outline.py` was listed and builds NO `Canvas` at all** — executed, its
     occupancy probe returns `canvases = 0` and it calls `rows()` nowhere. It renders straight to
     `rich.Text`. **A consumer that does not consume makes the contract un-falsifiable in its own
     favour**: a change that broke every real consumer could still be reported as "3 of 4 consumers
     verified".
  2. **`mapper/export.py` was listed as a consumer and is not one.** It is a **transitive
     observer**: it snapshots the SINK — the composed `rich.Text` — and never indexes `rows()`
     positionally. Trigger **B4** fired on it correctly, because the bytes it snapshots change; but
     *"its bytes change"* and *"it holds this positional contract"* are different claims, and only
     the second belongs on a consumer list. **The observation is not lost — it is moved**, and
     `LLR-CNV.2.1` still owns it with an on-disk threshold.
- **WHY THE DISTINCTION IS LOAD-BEARING AND NOT BOOKKEEPING.** `#D4`'s stated reversal condition is
  *"a consumer outside `mapper/views/` indexing `rows()` positionally"*. With `export.py` on the
  consumer list, that condition **reads as already met**, and the A3's scope ruling looks reversed by
  its own contract table. Executed, the condition is **still not met — 0 sites outside `views`** —
  and `#D4` stands. The corrected list is what makes `#D4` checkable rather than self-contradicting.
- **The four call sites are named as EVIDENCE THAT THE SET IS NON-EMPTY, never as the specification**
  — the rule this document applies to every census (`LLR-N06.2.5`, `LLR-N06.2.1`, `LLR-COERCE.2`).
  Both prior generations of these addresses were stale: the parked list had 4 sites in 4 files and
  **every address wrong**. The gate is the walk.

```
COMPONENT: inspector
  PARENT : map_screen
  SURFACE: map
  INPUTS : graph: Graph ; node_id: str|None
  OUTPUTS:
    - id          : ficha_fields
      value       : the editable ficha field widgets
      address     : query_one("#map-inspector"), then its field children INDEXED POSITIONALLY
      cardinality : 8 focusable descendants on the legacy fixture -- title, state, D, O, E, C, N, notes
      consumers   : mapper/app.py
                    tests/test_attachments.py
                    tests/test_inspector.py
                    tests/test_rail.py
                    tests/test_worklist_safety.py
      owner       : LLR-N14.3.2
```

> **The cardinality on `ficha_fields` is measured, not declared by hope.** Executed (**M-10**), nine
> real focus-traversal presses from the canvas at 140 x 45 reach `#map-rail` then exactly eight
> inspector descendants, in the order `insp-title`, `insp-state`, `insp-field-D`, `insp-field-O`,
> `insp-field-E`, `insp-field-C`, `insp-field-N`, `insp-notes`. **It is regime-bound**: the count
> depends on the loaded map's schema (`fixtures/legacy_nodos.yml` declares 5 keys), so the number is
> `5 + 3`, and on a schema-less map it is `3`. LLR-N14.3.2's invariant is stated in terms of the
> measured regime and re-derived from the loaded schema rather than hard-coded.

```
COMPONENT: overflow_indicator
  PARENT : map_screen
  SURFACE: map
  INPUTS : graph: Graph ; state: ViewState
  OUTPUTS:
    - id          : declared_unpainted_total
      value       : the count of graph nodes not painted on the canvas
      address     : query_one("#map-pagination")
      cardinality : 1
      consumers   : mapper/app.py
      owner       : LLR-N06.3.1
    - id          : fold_pills
      value       : one pill per painted folded branch, each naming the branch and its hidden count
      address     : the pill cells inside query_one("#map-canvas")
      cardinality : one per painted folded branch, 0 when nothing is folded
      consumers   : none
      owner       : LLR-N06.2.3
```

> **A naming hazard recorded, because it is the kind that ships.** `#map-pagination` already exists
> (`mapper/app.py:1108`) and its builder `_pagination_text` (`app.py:1269`) carries the comment
> *"For now the tree is not paginated; this reserves the affordance"* — so the slot is genuinely
> reserved and US-N06's indicator can occupy it. But `#map-minimap` also already exists
> (`app.py:1097`) and it does **not** paint a viewport minimap: `_minimap_text` (`app.py:1251`)
> paints a per-branch **coverage** strip with its own legend. A story asking for "a minimap" and an
> implementer finding a widget called `map-minimap` is a collision waiting to happen, so the
> requirement set deliberately never says "minimap" and this contract names the region that actually
> carries the declaration. `fold_pills` has **no consumer today** — written as `none` rather than
> omitted, so that the first test or stylesheet that reaches those cells is a declared change.

```
COMPONENT: search_bar
  PARENT : map_screen
  SURFACE: map
  INPUTS : graph: Graph ; query_text: str
  OUTPUTS:
    - id          : match_count_line
      value       : the painted count of matching nodes over the whole graph
      address     : query_one("#search-input"), and the count region beside it
      cardinality : 1
      consumers   : mapper/app.py
      owner       : LLR-N07.2.1
```

```
COMPONENT: keybar
  PARENT : map_screen
  SURFACE: map
  INPUTS : active_groups: Sequence[str]
  OUTPUTS:
    - id          : keybar_groups
      value       : the glyph-and-label pairs for the active groups
      address     : keymap.groups_for_keybar(active_groups) return value, INDEXED POSITIONALLY
      cardinality : one entry per requested group, in the requested order
      consumers   : mapper/app.py
                    tests/test_keymap.py
      owner       : LLR-N16.1.2
```

> The keybar is listed because three increments add chords to `mapper/keymap.py` and **no single
> increment owns the seat this batch** (`docs/ARCHITECTURE.md` §4, risk A-5). Its address is a pure
> read of the seat (`keymap.py:189`), so a chord added without its group entry changes what this
> component emits without changing any line inside the component.

```
COMPONENT: home_cards
  PARENT : SYSTEM
  SURFACE: home
  INPUTS : workspace: Path ; graphs: dict[str, Graph]
  OUTPUTS:
    - id          : recents_rows
      value       : one row per map -- name, kind, node count, doc count, and the new card data
      address     : query_one("#home-recents"), columns INDEXED POSITIONALLY
      cardinality : 4 columns today -- the widening of this set is the contract change
      consumers   : mapper/app.py
      owner       : LLR-N13.1.1
    - id          : welcome_seat
      value       : the entry-action copy shown when the workspace holds no map
      address     : query_one("#home-empty")
      cardinality : 1
      consumers   : mapper/app.py
      owner       : HLR-N13.2
    - id          : hero_coverage
      value       : the hero map's coverage percentage and bar
      address     : query_one("#home-hero") and query_one("#home-microbar")
      cardinality : 2
      consumers   : mapper/app.py
                    tests/test_app.py
      owner       : LLR-N13.1.3
```

> **`recents_rows` is the batch-79 shape, and this is the line that catches it.** The table is
> created with exactly four columns today — `"▐ name"`, `"kind"`, `"nodos"`, `"docs"`
> (`mapper/app.py:516`, executed) — and rows are added positionally at `:546-552`. US-N13 adds card
> data to those rows. **Adding a fifth column changes the address by which every existing consumer
> reaches columns 1 through 4**, even though each of those four values is untouched. Declaring
> `cardinality: 4` now means the widening is a contract change with an owner rather than an accident
> discovered by a positional consumer.

```
COMPONENT: legend_panel
  PARENT : SYSTEM
  SURFACE: help
  INPUTS : scope: str ; vocabulary: the shared glyph declaration
  OUTPUTS:
    - id          : legend_title
      value       : the name of the view the legend was opened from
      address     : query_one("#help-title")
      cardinality : 1
      consumers   : mapper/screens/help.py
      owner       : HLR-N16.2
    - id          : legend_key_rows
      value       : one row per binding the source scope offers
      address     : query_one("#help-content"), rows INDEXED POSITIONALLY
      cardinality : equal to len(keymap.bindings_for(source_screen.KEY_SCOPE))
      consumers   : mapper/screens/help.py
                    tests/test_palette.py
      owner       : LLR-N16.1.1
    - id          : legend_vocabulary_rows
      value       : one row per glyph in the source view's declared vocabulary
      address     : query_one("#help-content"), the vocabulary section
      cardinality : equal to the declared vocabulary size, 0 when the view declares none
      consumers   : none
      owner       : LLR-N16.2.1
```

> **`legend_key_rows`'s cardinality is written as a derivation, not as a number**, and that is the
> whole US-N16 lesson in one field. Executed today (**M-11**): 13 rows from home, 27 from map, 2
> from a screen with no declared scope. A literal number here would be a hand-list wearing a
> contract's clothes — control C-31 — and it would also be **wrong on the defect**, since the broken
> screen's painted count matches its (wrong) scope perfectly.

### 4.3 · Balancing check

| Component | `PARENT` | `INPUTS ⊆ PARENT.INPUTS` |
|---|---|---|
| `map_screen` | SYSTEM | n/a — top level |
| `rail` | `map_screen` | `graph` ✓ ; `cursor` derived from `key_events` ✓ ; `folded` derived from `key_events` ✓ |
| `canvas` | `map_screen` | `graph` ✓ ; `state` composed from `graph`, `terminal_size`, `key_events` ✓ |
| `inspector` | `map_screen` | `graph` ✓ ; `node_id` derived from `key_events` ✓ |
| `overflow_indicator` | `map_screen` | `graph` ✓ ; `state` ✓ |
| `search_bar` | `map_screen` | `graph` ✓ ; `query_text` derived from `key_events` ✓ |
| `keybar` | `map_screen` | `active_groups` derived from `map_screen`'s `KEY_SCOPE` ✓ |
| `home_cards` | SYSTEM | n/a — top level |
| `legend_panel` | SYSTEM | n/a — top level; `scope` arrives from whichever screen pushed it |

**Recorded, not glossed:** three of the nine components declare `PARENT: SYSTEM`, so their
containment is not checkable here and the validator's `V12` will say so rather than pass. That is
the honest outcome — `HomeScreen`, `MapScreen` and the modal `HelpScreen` are siblings mounted by
`MapperApp`, and inventing a parent component to satisfy a check would be worse than the notice.

---

## 5. Validation strategy and traceability

### 5.1 Methods

- **Layer A — white-box / functional (`TC-NNN`):** `test (unit)`, `test (integration)`,
  `inspection`, `analysis`. Every `test`/`analysis` requirement above carries an **Executed
  verification** line and a **Numeric pass threshold** line.
- **Layer B — black-box / behavioral acceptance (`AT-NNN`):** Textual Pilot end-to-end via
  `App.run_test()`, or artifact-on-disk inspection for the export case. **Every `AT` drives the real
  key or the real gesture** (control C-16). `demo` is not used anywhere in this batch.

**Testing-strategy cross-check.** The labelled runtime is `pytest` with `pytest-asyncio` and
Textual's `App.run_test()` Pilot — all three are installed and in use today (27 test files under
`tests/`, 245 collected nodes, executed at Phase 0). No new test framework is introduced by any
requirement above, so no requirement is labelled against a stack the repo does not have.

### 5.2 Dual-traceability

**Behavioral chain (black-box) — per user story.** `AT` ids are enumerated individually, never as a
range (control C-56).

| US / story | Observable outcome | Shipped surface | Acceptance tests | Observed? |
|---|---|---|---|---|
| ~~S-7~~ | **SUPERSEDED — SATISFIED-EXTERNALLY at `d877784`** (§3.1, `PLAN.md` §12.5 D16) | shipped as `HLR-R04`, guarded in `tests/test_repair_layout.py` | none — `AT-001` and `AT-002` are struck | n/a |
| S-6 | three hues carry declared jobs; blue and severity keep theirs | `mapper/darkside.py` + the derived census | `AT-003`, `AT-004`, `AT-005`, `AT-006` | pending Phase 4 |
| HLR-canvas | the declared layers reach `rows()`; braille reaches `RadialRenderer`'s output **(`AT-007b` is a `PIN (radial)`, not a map-canvas gate)**; the export artifact is read back from disk; selection tone follows focus | `Canvas.rows()`, `RadialRenderer`, `export.save_svg` **on disk** | `AT-007`, `AT-007b`, `AT-008`, `AT-009`, `AT-010` | pending Phase 4 |
| US-N06 | the window moves, branches fold, and what is hidden is declared and reconciles — **in every view that declares, not only the default one**, on **both** declaring surfaces, and a declaration that BROKE is distinguishable from one that is absent | `#map-canvas`, `#map-pagination`, `#map-rail` | `AT-011`, `AT-012`, `AT-013`, `AT-014`, `AT-015`, `AT-016`, `AT-017`, `AT-046`, `AT-047`, `AT-056`, `AT-057`, `AT-058` | pending Phase 4 |
| US-N07 | the count covers the whole map and the walk follows the tree with the real `n` / `N` / `M`; the count line declares which question it answers; nothing found looks like nothing | `#search-input` and the count region | `AT-018`, `AT-019`, `AT-020`, `AT-021`, `AT-022`, `AT-023`, `AT-024`, `AT-051`, `AT-052` | pending Phase 4 |
| US-N13 | each map shows its own shape; an empty workspace shows the door; a damaged map says so on its own card and the others still paint theirs | `#home-recents`, `#home-empty` | `AT-025`, `AT-025b`, `AT-026`, `AT-029`, `AT-030`, `AT-031` | pending Phase 4 |
| ~~US-N14~~ | **DEFERRED — follow-on design batch** (§3.7, `#D23`, §6.5 A-42) | — | none live here — `AT-032`, `AT-033`, `AT-034`, `AT-034b`, `AT-035`, `AT-036`, `AT-037`, `AT-038`, `AT-039`, `AT-040` leave with the story and are enumerated in §3.7's deferral block | n/a |
| US-N16 | `?` explains **this** view, with its real keys and its real glyphs, on every screen in the derived set — **including the legend's own keys** | `HelpScreen` via the real `question_mark` chord, read through `_painted_bindings` | `AT-041`, `AT-042`, `AT-043`, `AT-044`, `AT-053` | pending Phase 4 |
| repair pair (`B-29`, `B-30`) | a map the store cannot fully parse says so on its own card; a not-found message names the map, not the filesystem | `#home-recents` and the `load_or_notice` toast | `AT-049`, `AT-050` | pending Phase 4 |
| S-3b `◍` | **not derived** — `REFINE` pending Q-5 | — | none | n/a |

**THE `AT` COUNT IS DERIVED, NEVER TYPED (`QA-B-03`, §6.5 A-07).** The parked figure —
*"**47 acceptance tests across 8 derivable stories**"* — was a hand-maintained number wearing a
derivation's clothes: `US-N13` claimed 7 and defined 5, `US-N16` claimed 5 and defined 4, and three
ids (`AT-027`, `AT-028`, `AT-045`) existed only in this table and the story lists. **No literal
total is stated here.** The batch's `AT` count is:

> the cardinality of the set of `AT-NNN` tokens that appear on an `Acceptance tests:` line of a
> story's Acceptance block **and** on an `Acceptance:` line of some HLR or LLR **and** in the
> behavioral table above — the three-way intersection, computed by grepping this document.

An id present in fewer than all three is a defect, not a test: padding fails the intersection, and
so does a predicate nobody traced. **The exact figure is a derived statement, not a literal**, and
the concurrent QA-lane census in `01d-unpark-measurements.md` is the authority on its current value;
this document deliberately does not carry a competing number. `V2` corroborates from the other side:
it reports one block per declared `AT` with no node on disk, which before implementation is exactly
the declared count.

**AMENDMENT SET 3 CHANGES THE LIVE `AT` SET, AND EVERY MOVE IS ENUMERATED (§6.5 A-42 through A-44).**
- **Deferred with US-N14 (`#D23`), not deleted:** `AT-032`, `AT-033`, `AT-034`, `AT-034b`, `AT-035`,
  `AT-036`, `AT-037`, `AT-038`, `AT-039`, `AT-040`. Two of these — `AT-034b` and `AT-040` — were
  among `QA2-C-01`'s six three-way failures; **they are dispositioned by the cut, and saying so is
  the point**, because a cut that quietly absorbs an open condition is the failure mode `02g` was
  written to detect.
- **Deferred with `HLR-N13.3`'s work budget (`#D24`), not deleted:** `AT-048`.
- **Given the `Acceptance:` owner they never had:** `AT-009` (now `LLR-CNV.2.1`), `AT-031` (now
  `LLR-N13.2.1`) — the last two of `P2-B2`'s three unowned ids; the third, `AT-040`, leaves with
  US-N14.
- **Given the story-list leg they never had:** `AT-046`, `AT-047` (US-N06's Acceptance block).
- **New and real:** `AT-049`, `AT-050`, the repair pair (§3.9).

**The three-way intersection is now satisfiable for every live id**, which is what `QA2-C-01` asks
and what `P2-C3`'s `AT`↔`TC` crossing is blocked on. No count is stated; the intersection is
computed.

**Deleted at amendment set 1:** `AT-027`, `AT-028`, `AT-045` — each appeared exactly twice and was
claimed by no requirement. **New at set 1:** `AT-048`, the `HLR-N13.3` mount-budget arm, which
`QA-M-12` correctly says cannot share `AT-025`'s on-disk node because it needs a different workspace
and a generated fixture. **Struck this amendment:** `AT-001` and `AT-002`, with §3.1 (D16).
`AT-046` and `AT-047` were added at reconciliation for `LLR-N06.2.4` — the fold auto-open, which
`01b-ux-decisions.md` names the largest gap in the design and without which `AT-022` passes on a
screen where the operator cannot see the selection. Every `AT` id in this document is enumerated
individually; no dotted range appears anywhere (control C-56).

**Functional chain (white-box) — per requirement.**

| Requirement | Method | Test cases | Notes |
|---|---|---|---|
| ~~HLR-S07.1~~ | — | ~~`TC-001`, `TC-002`~~ | **SUPERSEDED** at `d877784` (D16); shipped as `HLR-R04` |
| ~~LLR-S07.1.1~~ | — | ~~`TC-003`~~ | **SUPERSEDED**; shipped as `LLR-R04.1`, guarded by `TC-R22` |
| ~~LLR-S07.1.2~~ | — | ~~`TC-004`~~ | **SUPERSEDED**; guarded by `test_at_r10b` |
| ~~LLR-S07.1.3~~ | — | ~~`TC-005`~~ | **SUPERSEDED**; guarded by `test_at_r11`. Its lesson is re-homed in `HLR-N06.3` |
| HLR-S06.1 | test (unit) | `TC-006` | 3 constants, 3 docstring mentions |
| LLR-S06.1.1 | inspection | `TC-007` | the jobs are the deliverable |
| HLR-S06.2 | test (unit) | `TC-008` | slots 35 / 38 / 105, executed **M-2** |
| HLR-S06.3 | test (unit) + analysis | `TC-009` | derived input set |
| LLR-S06.3.1 | test (unit) | `TC-010` | file list **equals** `git ls-files`; non-empty-input mutation arm |
| LLR-S06.3.2 | test (unit) + inspection | `TC-011` | `#D10` dispositions: register size 1 after Inc-1, 0 after Inc-9 |
| LLR-S06.3.3 | test (unit) | `TC-012` | derived **set** equality, not `>= 8`; 8 hex literals |
| LLR-S06.3.4 | test (unit) | `TC-013` | derived **set** equality, not `>= 29`; re-executed **36** at `d877784` |
| LLR-S06.3.5 | test (unit) | `TC-072` | one job per token; *both* `== 0` and *neither* `== 0` |
| HLR-CNV.1 | test (unit) | `TC-014` | braille count, pre-state 0 |
| LLR-CNV.1.1 | test (unit) + inspection | `TC-015` | monkey-patch deletion asserted |
| LLR-CNV.1.2 | test (unit) | `TC-016` | layer precedence |
| LLR-CNV.1.3 | test (unit) | `TC-017` | out-of-bounds dropped |
| LLR-CNV.1.4 | test (unit) | `TC-079` | 14 malformed tones -> fallback, not silent unstyled; validated in `rows()` |
| HLR-CNV.2 | test (unit) | `TC-018` | **`PIN (radial)`** · `RadialRenderer`, M-1, 80x24 · count > 0, `len(cv.dots) == 0` on a single node, **and** `pre_set ⊆ post_set` derived at run time |
| LLR-CNV.2.1 | test (integration) | `TC-019` | **on-disk** code-point equality; positive control 12 of 12; no uniformly-styled fixture |
| HLR-CNV.3 | test (unit) | `TC-020` | focus-aware tone, B-05 |
| LLR-CNV.3.1 | test (pilot) | `TC-021` | real `tab`, never `.focus()` |
| HLR-N06.1 | test (pilot) | `TC-022`, `TC-023` | pan moves; pan is bounded |
| LLR-N06.1.1 | test (unit) | `TC-024` | offsets travel in the state |
| LLR-N06.1.2 | test (unit) | `TC-025` | clamp over 6 inputs |
| HLR-N06.2 | test (pilot) | `TC-026` | pill numeral equals descendant count; hit count when a query is live |
| LLR-N06.2.1 | test (unit) + inspection | `TC-027` | rail attributes deleted; supersession set **DERIVED** over `mapper/` **and** `tests/`, non-empty before evaluation (~~enumerated~~ — `P2-B4`); predicted-red clause names `MASTER_RAIL_DIGESTS` |
| LLR-N06.2.2 | test (pilot) | `TC-028` | folding a leaf paints no pill |
| LLR-N06.2.3 | test (unit) | `TC-029` | hostile branch titles; `COERCION_RANGES` on the **painted row**; split-at-width arm |
| LLR-N06.2.5 | test (unit) | `TC-073` | AST-derived `notify` census; markup half green, coercion half 15 sites. **Parent is `HLR-COERCE` (§3.0), not `HLR-N06.2` — re-parented by `#D21`; owning increment `Inc-9`.** The row stays in this position for line-stability; the row's *position* is not its parent |
| HLR-CNV.1 *(predicted-red arm)* | test (unit) | `TC-014` | four `RadialRenderer` keys of `MASTER_LEGACY_DIGESTS` predicted **red**; every `LayeredRenderer` and `OutlineRenderer` key predicted **green** — re-capturing a green one is a gate failure |
| LLR-N06.2.4 | test (pilot) | `TC-071` | walk opens a folded hit and announces it; no re-close |
| HLR-N06.3 | test (pilot) | `TC-030` | **three** predicates (reconcile · declared ⊆ traced · traced ⊆ declared); `legacy` named, four `(w,h,folded)` triples pinned |
| LLR-N06.3.1 | test (unit) | `TC-031` | set difference, overlap case |
| LLR-N06.3.2 | test (pilot) | `TC-032` | `anidado` fixture normative: naive 6 vs painted 4; re-run through the Pilot once Inc-3 ships fold |
| LLR-N06.3.3 | test (pilot) | `TC-033` | no indicator at zero |
| HLR-N07.1 | test (unit) + inspection | `TC-034` | predicate deleted, pre-state 4 hits |
| LLR-N07.1.1 | test (unit) + inspection | `TC-035` | injected id the old predicate rejects |
| LLR-N07.1.2 | test (unit) | `TC-036` | widening 2 -> 5, executed **M-7** |
| HLR-N07.2 | test (pilot) | `TC-037` | count identical in 4 states |
| LLR-N07.2.1 | test (pilot) | `TC-038` | query pinned `carlos`; a hit strictly inside `fin`, painted before the fold |
| LLR-N07.2.2a | test (unit) | `TC-039` | six signatures take `(graph, state)`; output byte-identical; `**kwargs` 5 -> 0 |
| LLR-N07.2.2b | test (unit) | `TC-077` | renderer set derived from the protocol; hits painted; owns `AT-024` |
| HLR-N07.3 | test (pilot) | `TC-040`, `TC-084`, `TC-085` | walk order and empty state; `TC-084` presses the real `M` (`UX2-C-07`); `TC-085` the count line declares its subject (`UX2-C-06`) |
| LLR-N07.3.1 | test (unit) | `TC-041` | self-guard: tree order != dict order |
| LLR-N07.3.2 | test (pilot) | `TC-042` | text and tone both differ |
| LLR-N07.3.3 | test (unit) | `TC-043` | blank query, pre-state all 6 |
| HLR-N13.1 | test (pilot) | `TC-044` | 6 / 8 / 8 and 0 / 3 / 3, executed |
| LLR-N13.1.1 | test (unit) | `TC-045` | one load per map in the recents loop |
| LLR-N13.1.2 | test (unit) | `TC-046` | bar length 10 at both ends |
| LLR-N13.1.3 | test (unit) | `TC-047` | **pinned** `pct(schema-less) == 100` **and** the 3 sites agree; pre-state 0 vs 100 vs 100 |
| LLR-N13.1.4 | test (unit) | `TC-048` | due and link, with their negative arms |
| LLR-N13.1.5 | test (pilot) | `TC-074` | painted card count `== N` **and** card-state distinguishability |
| LLR-N13.1.6 | test (unit) | `TC-075` | `<= 1` load per map; `<= 2` workspace globs, pre-state 14 |
| HLR-N13.3 | test (pilot) | `TC-076` | containment on **load failure**, not on a clock; thresholds 1 and 2 **DEFERRED (`#D24`)** with `AT-048` |
| HLR-N13.2 | test (pilot) | `TC-049` | 6 door labels; mutation arm |
| LLR-N13.2.1 | test (pilot) | `TC-050` | hostile map titles |
| ~~HLR-N14.1~~ | — | ~~`TC-051`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~LLR-N14.1.1~~ | — | ~~`TC-052`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~LLR-N14.1.4~~ | — | ~~`TC-078`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~LLR-N14.1.2~~ | — | ~~`TC-053`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~LLR-N14.1.3~~ | — | ~~`TC-054`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~HLR-N14.2~~ | — | ~~`TC-055`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~LLR-N14.2.1~~ | — | ~~`TC-056`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~LLR-N14.2.2~~ | — | ~~`TC-057`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~LLR-N14.2.3~~ | — | ~~`TC-058`~~ | **DEFERRED (`#D23`)** — §3.7. The coercion **class** stays: `HLR-COERCE` (§3.0) owns it |
| ~~HLR-N14.3~~ | — | ~~`TC-059`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~LLR-N14.3.1~~ | — | ~~`TC-060`~~ | **DEFERRED (`#D23`)** — §3.7 |
| ~~LLR-N14.3.2~~ | — | ~~`TC-061`~~ | **DEFERRED (`#D23`)** — §3.7. `C-D6b`'s standing re-run obligation leaves with it |
| ~~LLR-N14.3.3~~ | — | ~~`TC-062`~~ | **DEFERRED (`#D23`)** — §3.7 |
| HLR-COERCE | test (unit) | `TC-080`, `TC-081` | the declared list and the two truncators; §3.0 |
| LLR-COERCE.1 | test (unit) | `TC-080` | `COERCION_RANGES` declared once; `_CONTROL_MAP` covers it — derived, no literal |
| LLR-COERCE.2 | test (unit) | `TC-081` | `views/layered.py::_fit` coerces before truncating; split-at-width arm |
| HLR-REPAIR.1 | test (pilot) + test (unit) | `TC-082`, `TC-083` | two shipped defects, `B-29` and `B-30`; §3.9 |
| LLR-REPAIR.1 | test (unit) + test (pilot) | `TC-082` | phantom sidecar id records a load warning; **synthetic fixture mandated** |
| LLR-REPAIR.2 | test (unit) | `TC-083` | the not-found message carries `map_id` and no path component |
| HLR-N16.1 | test (pilot) | `TC-063` | oracle = `_painted_bindings` over `_rows_in`; every AT declares its Pilot size; negative control is `AT-R14` |
| LLR-N16.1.1 | test (unit) | `TC-064` | emptied-set mutation arm |
| LLR-N16.1.2 | test (unit) | `TC-065` | 0 undeclared scopes; pre-state 2; **migrate both** (`#D9`) with `C-D9a` / `C-D9b` / `C-D9c` |
| HLR-N16.2 | test (pilot) | `TC-066` | title names the view **on every screen in the derived set**; floor derived from the 21-row vocabulary |
| LLR-N16.2.1 | test (unit) | `TC-067` | one vocabulary declaration |
| LLR-N16.2.2 | test (pilot) | `TC-068` | empty vocabulary omits the section |
| LLR-N16.2.3 | test (unit) | `TC-069` | legend coerces **every file-derived string**; row-length clause added |
| HLR-N16.3 | test (pilot) | `TC-070` | stack depth 4 then 4; mutation arm |
| HLR-N16.4 | test (pilot) | `TC-086` | the legend declares its own scroll keys; asserted by real key presses, never `scroll_to` |
| LLR-N07.2.3 | test (unit) + inspection | `TC-087` | `ViewState` frozen and fully defaulted; `IRenderer` a `runtime_checkable` Protocol; signature clause reddens the vacuous `isinstance` |
| LLR-N13.1.7 | test (unit) | `TC-088` | alias bomb under the **traversed** `nodes:` key, with its un-aliased control |

**THE TWO CHAINS CROSS — `#D15`, discharged as a DERIVED JOIN rather than a third hand table
(`P2-C3`, §6.5 A-55).**

`#D15` demanded an `AT`↔`TC` mapping before Inc-1. It was graded ✗ at the first architect pass and
**41 amendments did not touch it**: the two tables above — behavioral `US → AT` and functional
`Requirement → TC` — never crossed, so no artifact answered *"which white-box case backs this
black-box outcome?"*. It is dischargeable now, and **only now**, because pass 1 gave every live `AT`
an `Acceptance:` owner; before that the join had no middle column.

> **THE JOIN.** For every live `AT`, its `TC` set is
> `{ TC : TC is in the functional row of some requirement R, where R carries that AT on its
> Acceptance: line }`.
>
> **QUESTION.** Does every live `AT` reach at least one `TC` through an owning requirement?
>
> **INSTRUMENT.** Walk this document's `####`/`#####` headings to bind each `Acceptance:` line to its
> requirement, skipping headings marked `SUPERSEDED` or `DEFERRED`; join to the functional table on
> the requirement id. **Cardinality deliberately not transcribed.**
>
> **MEASURED AT.** `ea1fbf9`. **Result: the join is TOTAL — 0 live `AT` ids reach no `TC`.**

**THE JOIN IS THE DELIVERABLE, NOT A TABLE OF ITS OUTPUT.** A transcribed third table would be a
hand-maintained artifact joining two derived ones, and this document has already shipped four wrong
generations of exactly that shape (§6.5 A-07). **A join that is stated once and computed cannot go
stale**; a table of its results goes stale on the next id that moves — and pass 1 alone moved eleven.
`V2` corroborates from the other side.

**Two apparent gaps, both checked rather than waved past.** A naive run of the join reports
`AT-025b` and `AT-048` reaching no `TC`. Executed, **neither is real**: both are owned by
`HLR-N13.3`, whose functional row **does** carry `TC-076`, and a scanner that discards rows
containing the word `DEFERRED` drops it because the row's *note* records `#D24`'s deferral of
thresholds 1 and 2. **The row is live; its note mentions a deferral.** `AT-048` is separately
deferred and is out of the live set anyway. Recorded because *"the scanner said zero"* is how a
correct artifact gets damaged to satisfy a broken oracle — and because the join's implementer will
hit the same false positive.

**Counts are DERIVED STATEMENTS, not literals (§6.5 A-07).** The parked line read
*"Counts: 21 HLR · 48 LLR · 47 `AT-NNN` · 71 `TC-NNN` — all four derived by grepping this document's
own headings and id tokens at close of draft."* The derivation was real; the **transcription into a
literal was not durable**, and `QA-B-03` measured it wrong three ids later. Each count is therefore
restated as its derivation:

- **HLR count** = number of `#### HLR-` headings marked neither `SUPERSEDED` nor `DEFERRED`.
- **LLR count** = number of `##### LLR-` headings marked neither `SUPERSEDED` nor `DEFERRED`.
- **`AT` count** = the three-way intersection defined above, taken over stories whose §5.2 behavioral
  row is neither struck nor marked `DEFERRED`.
- **`TC` count** = number of distinct `TC-NNN` tokens in the functional table whose row is neither
  struck nor marked `DEFERRED`.

**`DEFERRED` joins `SUPERSEDED` as a disqualifying marker (amendment set 3, `#D23`).** Both are
written into the **heading**, not into a banner paragraph, precisely so a heading grep answers the
question without a reader remembering which sections are live. A section-level banner is not
machine-readable; a heading suffix is. Every deferred heading carries the literal token `#D23`, so
the deferral's *reason* is recoverable from the same grep that finds it.

This amendment **struck** `HLR-S07.1`, `LLR-S07.1.1`, `LLR-S07.1.2`, `LLR-S07.1.3`, and with them
`TC-001`, `TC-002`, `TC-003`, `TC-004`, `TC-005`; **added** `LLR-S06.3.5`, `LLR-N06.2.5`,
`LLR-N13.1.5`, `LLR-N13.1.6` and `HLR-N13.3`; and **added** `TC-072`, `TC-073`, `TC-074`, `TC-075`,
`TC-076`. Every id is enumerated individually (C-56). Re-derive rather than
adjust the old literals; the concurrent QA-lane census in `01d-unpark-measurements.md` is the
authority on the resulting figures. Every HLR traces to a story in §2.6; every LLR traces to a parent
HLR; every story with a `READY` verdict except S-3b and the superseded S-7 carries at least one `AT`.

### 5.3 Batch acceptance criteria

1. Every LLR is covered by at least one `TC` with a pass result. **100 % LLR coverage.**
2. Every derivable story has at least one passing `AT` observing its outcome through the shipped
   surface, with boundary and negative evidence. **Every derivable story except S-3b (`REFINE`,
   pending Q-5) and the superseded S-7** — stated as a predicate over §5.2's behavioral table rather
   than as a literal count, for the reason §5.2 gives.
3. **0** blocker fails in validation.
4. **0** requirements without an assigned validation method, an executed verification and a numeric
   pass threshold.
5. **The escaped-bug / mutation counterfactuals below are each demonstrated RED before their fix,
   per-arm, never by a process exit code** (risk R-2). Each is a **plausible wrong implementation**,
   not a deletion:
   - ~~`AT-001` RED against `master` — the S-7 layout defect~~ — **struck with §3.1 (D16)**; the
     repair batch demonstrated it and `tests/test_repair_layout.py` carries the guard;
   - `AT-005` RED with one hex edited — the census can see a hue change;
   - `AT-005` RED with `WARN` and `ALERT` given the single job *"severity"* — `M-S06.3.5-a`, the
     *sites classifying as both* `== 0` clause;
   - `AT-007b` RED with `dots` composed at the wrong precedence — `M-CNV.2-a`, the containment arm
     (~~`AT-007`~~ — id corrected by `QA2-C-08`, §6.5 A-63: the containment arm is `AT-007b`'s
     under the A-37 split, and `AT-007` is `HLR-CNV.1`'s unit assertion on `Canvas`);
   - `AT-029` RED with `layered.py:179` and `rail.py:274` changed to match `app.py:379` —
     `M-N13.1.3-a`, the value pinned at 100;
   - `AT-030` RED with the empty-workspace branch removed — the welcome seat guard is real;
   - `AT-042` RED with the column slice dropped from `_rows_in` — `M-N16.1-a`, the two-dimensional
     clip;
   - `AT-044` RED with `SCOPE_HELP` removed from `MODAL_SCOPES` — the doubled-chord reservation is
     real;
   - ~~`AT-048` RED with the mount budget computed from `len(graph.nodes)` — `M-H3`, the 51-node /
     1 935 ms fixture~~ — **DEFERRED (`#D24`)** with `HLR-N13.3`'s thresholds 1 and 2;
   - `AT-025` RED with today's `else` arm left in place — `M-H1b`, the card-state distinguishability
     arm;
   - `AT-049` RED with the phantom-node warning omitted — `M-REPAIR.1-a` (§3.9). **This one is the
     positive control for `LLR-N13.1.5`'s whole containment arm**, which is a no-op on the current
     tree, so it is listed here rather than left to the increment;
   - `AT-050` RED with the workspace path interpolated instead of `map_id` — `M-REPAIR.2-a` (§3.9).
7. **The governing architecture document is amended, and `Inc-2` OWNS the amendment (`P2-C7`,
   §6.5 A-53).** Until this lands, **nine increments run against a governing document that forbids
   two of them** — `docs/ARCHITECTURE.md` at `3fe0e4b` still freezes both A3 subjects. Executed, the
   two stale rows are:
   - **`:70`** — declares `IRenderer.render(graph, selected_id, w, h, **kwargs) -> Text` as the
     `views` public interface. `LLR-N07.2.2a` and `LLR-N07.2.3` replace that signature.
   - **`:146`** — the `Canvas` frozen-interface row, which lists `put`, `wire`, `edge`,
     `elbow_down`, `text`, `rows() -> list[Text]` and **declares neither `dots` nor `bgs`**.
     `HLR-CNV.1` makes both reach the output.

   **Threshold:** after `Inc-2`, **0** rows in `docs/ARCHITECTURE.md` declare a renderer or canvas
   interface that the tree does not implement — derived by comparing each declared signature against
   `inspect.signature` on the live symbol, **never by reading the table**. `Inc-2` is the owner
   because it is the **later** of the two A3s, so both subjects have landed by the time it closes; a
   doc is not a source file, so this adds **nothing** to `Inc-2`'s declared breach. **One owner, not
   two** — splitting the Canvas half into `Inc-1` would put one file under two increments, which is
   the collision `#D5` exists to prevent.

   **ROUTED, NOT ASSUMED — the missing `dots`/`bgs` COMMITMENT row (`C-44`).** `docs/ARCHITECTURE.md`
   is **not this lane's to edit**. The repair batch already established the right device: `:159`
   carries a `ViewState` row marked **`COMMITTED, NOT PRESENT`**, which *"states a plan without
   asserting a falsehood"*. **The Canvas half has no such row**, so the second A3 is committed
   nowhere and reads as unplanned. **The orchestrator shall route a sibling commitment row for the
   `dots`/`bgs` widening to the lane that owns `docs/ARCHITECTURE.md`**, worded like `:159` and
   naming `Inc-1` as where it lands. This is a *commitment* row landing now; the *present-tense*
   correction of `:70` and `:146` is the Phase-6 amendment above, and the two are deliberately not
   the same edit.
8. The A3 reverse census is **derived from the code, never taken by eye**: after Inc-2, an **AST
   walk** returns 6 `render` definitions under `mapper/views/` with **0** declaring `**kwargs`, and
   resolves **23 arg-ful call sites across 10 files (3 production: `app.py:737`, `:1352`, `:1727`)**
   to the new signature. Absence of the old shape is **asserted**, not assumed (risk A-1).
   > **CORRECTED 2026-08-27 (qa lens `QA3-C-06`).** This criterion previously specified the census as
   > `grep -rn "\.render(" mapper/ tests/` — **which is `M-N07.2.2a-b`, the named weaker variant this
   > document already states can never equal the migrated set** (`:2572-2575`). An exit criterion
   > citing its own rejected mutant. A substring search cannot tell a call from a **mention**: it
   > sweeps in **25 zero-arg Textual `Widget.render()` sites** — a different protocol — and a
   > docstring mention at `mapper/widgets/rail.py:180`. That grep produced **five wrong generations**
   > of this number; only an AST separates the two protocols. `P-21` in the backlog is the standing
   > rule.
   > **⚠ There is NO criterion 6.** It existed at `ea1fbf9` and its subject was absorbed; the numbering
   > is left as `1,2,3,4,5,7,8` **deliberately**, because renumbering would break every citation of
   > criteria 7 and 8 across the batch. Recorded so the gap reads as known rather than as a drop.

---

### 5.4 The increment cut — stated ONCE, here, authority `#D5`

> **`PDR-2026-08-26-ui-next-batch-02#D5` is the SOLE authority for the increment cut.** This section
> is `#D5`'s cut **re-derived for the operator's re-scope** (amendment set 3 · A-49); it does not
> compete with `#D5` and it does not replace it. **No other place in this document states a cut.**
> Every `*(Inc-N)*` parenthetical in §3 and every increment reference in a body paragraph now points
> here, and a second cut appearing anywhere in this document is a defect, not a variant.
>
> **This section exists because `P2-B1` and `QA2-C-06` found TWO cuts live simultaneously** — the
> stale ARQ 7-cut surviving in §3.6's and §3.8's section headers (`US-N13` as `Inc-6`, `US-N16` as
> `Inc-7`) alongside the ratified 9-cut in which `US-N13` is `Inc-7` and `US-N16` is `Inc-8` plus
> `Inc-9`. The headers are restated below. **The root cause was that the cut was never stated in
> this document at all**, only referenced — so each reference drifted independently.

**What the re-scope changes, and what it deliberately does not.** US-N14 «lente» is deferred
(`#D23`), so `#D5`'s **Inc-6 has no scope left**.

**`Inc-6` IS VACATED, NOT REUSED AND NOT RENUMBERED.** Two alternatives were considered and both
rejected on executed grounds:
- **Renumbering `Inc-7` through `Inc-9` down by one** would move three ids that `PLAN.md`, `02c`,
  `02d` and `03-increments/` already carry — **four artifacts this lane may not edit**. It would
  create a cross-artifact contradiction to remove an intra-document one, which is a strictly worse
  trade and is exactly how the current two-cut defect began.
- **Reusing `Inc-6` for the repair increment** would give one id two meanings across the batch's
  history, which is the `#D6`/`#D14` two-definitions defect applied to an increment id.

The repair increment is therefore named **`Inc-REPAIR`** and not `Inc-10`. That is deliberate: any
numeric id would collide under a substring scan — `grep "Inc-1"` matches `Inc-10`, and a suffixed
form like `Inc-6r` matches `Inc-6` — and this document is corpus that an id-scanner reads. **A name
that cannot be a prefix or a suffix of another increment id is the whole reason for the choice.**

| Inc | Scope | Status under the re-scope | Source files | n |
|---|---|---|---|---:|
| **Inc-1** | S-6 paleta v2 tokens · **Canvas A3** (`HLR-CNV.1`) · **`LLR-COERCE.1`** | live | `darkside.py`, `canvas.py`, `app.py`, `views/radial.py` | 4 |
| **Inc-2** | `ViewState` + `IRenderer` A3 — signature only, behaviour-neutral | live | `views/state.py` *(new)*, `views/layered.py`, `views/lane.py`, `views/outline.py`, `views/radial.py`, `app.py` | **6 — DECLARED BREACH**, unchanged from `#D5` |
| **Inc-3** | US-N06 escala — pan, fold, overflow · **`LLR-COERCE.2`, widened to every renderer feeding an operator-visible sink (`A-89`, `B-47`)** | live | `app.py`, `widgets/rail.py`, `views/layered.py`, `keymap.py`, **`views/outline.py`**, **`views/state.py` (`A-97`)** — and `views/lane.py` only if the derivation shows it reaching a sink | **6 — DECLARED BREACH (`A-89`, widened by `A-97`)** |
| ~~**Inc-4**~~ | ~~US-N07 búsqueda + the seat rebind (`#D5b`)~~ | **STRUCK 2026-08-29 — SPLIT by `#D36` under `C-21`.** Replaced by the two rows below. Struck, not shadowed; the id `Inc-4` is retired and never reassigned, per the same rule that vacated `Inc-6` | — | — |
| **Inc-4a** | US-N07 «búsqueda» **search core** — the single owner of "what matches", the resolved `hits` set on `ViewState`, the inline-predicate deletion, the fold-pill hit tail (**`LLR-N07.1.3`**, new) and the count line on the named count region (`#D37`) | live | `search.py`, `views/state.py`, `views/layered.py`, `app.py` | 4 |
| **Inc-4b** | US-N07 **seat + walk** — the `#D5b` rebind, the `n`/`N` walk, `LLR-N06.2.4` fold auto-open, the `E1b`/`E1c` toasts, state-dependent `esc` (`#D38`), the `test_cd25a` seat repair and the settle-chase counter carry | live | `keymap.py`, `app.py` | 2 |
| **Inc-4c** | **`LLR-N07.3.4`** — one regime, not two: the count region declares an active search at **every** graph size with a suspension notice, and `esc` clears identically at every size (`#D43`) | **new 2026-08-29** | `app.py` | **1** |
| **Inc-5** | hit painting in the three remaining renderers (`LLR-N07.2.2b`, threshold corrected by `#D42`) | live — **belongs to US-N07, not to US-N14** | `views/outline.py`, `views/radial.py`, `views/lane.py` | 3 |
| ~~**Inc-6**~~ | ~~US-N14 lente~~ | **VACATED** — deferred whole by `#D23` (§3.7). The id is retired, not reassigned | — | — |
| **Inc-STRIPS** | **the 12002-node screen collapse** — `#map-minimap` renders ~668 rows over the root's 4001 children and the pagination meter prices one glyph per node, so the canvas is crushed to 1 row and the count region lands off-viewport. **BLOCKER on closing `LLR-N07.3.4`**, not a follow-up | **new 2026-08-29** | `app.py` (+ its CSS block) | **1** |
| **Inc-REPAIR** | `B-29` phantom sidecar warning · `B-30` path disclosure (§3.9) | **new** | `store.py` | **1** |
| **Inc-CONFIRM** | `B-46` — the archive-confirmation markup sink (`A-90`) | **new** | the module owning `_ConfirmScreen` | **1** |
| **Inc-7** | US-N13 sala | live | `app.py`, `darkside.py`, `store.py` | 3 |
| **Inc-8** | S-8 truncation + the glyph vocabulary (the legend panel) · adds seat rows for `HLR-N16.4` | live | `screens/help.py`, `darkside.py`, `app.py`, **`keymap.py`** | **4** ⚠ |
| **Inc-9** | help scope routing + `KEY_SCOPE` declarations + seat migration · **`LLR-N06.2.5`** re-parented in by `#D21` | live | `keymap.py`, `screens/factory.py`, `screens/settings.py`, `app.py` | 4 |

**Serial order:** `Inc-1` → `Inc-2` → `Inc-3` → **`Inc-4a`** → **`Inc-4b`** → **`Inc-4c`** → `Inc-5` → **`Inc-STRIPS`** → `Inc-REPAIR` →
**`Inc-CONFIRM`** → `Inc-7` → `Inc-8` → `Inc-9`. **Parallelism is not re-derived** and the chain
stays serial: ARQ measured 0 of 21 pairs parallelisable, `modules(A) ∩ modules(B) ⊇ {app}` without
exception. **`Inc-4a` before `Inc-4b` is HARD** — see ordering 4 below. Budget **≤ 4 SOURCE files**;
tests uncapped.

**Amended 2026-08-29 by coordinator ruling `#D36`, under `C-21`.** The trigger evidence, recorded
because `C-21` requires the cut to be re-derived rather than patched:

> `C-21` fires when a gate amendment **adds, splits or redefines** an `AT-NNN` after the increment cut
> has been set. Both happened at the `Inc-4` pre-gate. **Removed:** `AT-024`, whose owner
> `LLR-N07.2.2b` this very section places in `Inc-5` — executed over the derived renderer set, **five
> of six renderers are query-insensitive today** (`text_differs=False, spans_differ=False`), so
> `AT-024` executes RED in `Inc-4` for reasons no file in its budget can change. **Owed an id:** three
> sealed `shall` clauses that carried none — the one-time rebind declaration (§3.5), `esc limpiar`
> (`LLR-N07.3.2` / `UX-Q3-b`), and `C-D6a`. A fourth, `UX-Q3-a`, is **deferred** with a recorded carry
> because no LLR ever stated it.
>
> **Deferring the three owed ids was considered and REJECTED** (`#D36`): it would ship sealed `shall`
> clauses with no acceptance, which is the conditional-close defect `C-44` names, wearing a
> scheduling excuse. The split pays for them instead.

**A fourth HARD ordering, from the split:**
4. **`Inc-4a` before `Inc-4b`** — `Inc-4b`'s walk, its fold auto-open and its `E1b`/`E1c` toasts all
   consume the resolved hit set and the tree-ordered hit list that `Inc-4a` creates. Reversed, every
   `Inc-4b` acceptance would have to construct its own hit definition, which is the two-definitions
   defect `HLR-N07.1` exists to close.

**Amended 2026-08-28 by coordinator ruling (`A-89`, `A-90`).** `Inc-3` absorbs `B-47` and declares a
5-file breach; `Inc-CONFIRM` is inserted alongside `Inc-REPAIR` for `B-46`, before `Inc-7`, because
`Inc-7`'s sala loads every map on mount and is what makes both paths newly reachable. **This section
remains the sole statement of the cut** — the amendments record the reasoning, this table records
the commitment, and a second cut appearing anywhere is a defect, not a variant.

**Three orderings are HARD, not preference:**
1. **`Inc-8` before `Inc-9`** — carried unchanged from `#D5`. `Inc-9`'s acceptance reads the painted
   panel; `Inc-8` is what makes the panel able to paint every row. Reversed, `Inc-9` fails through
   no fault of its own and the likely repair is to weaken the oracle back to `_render_keymap()`'s
   return value, which passes today on a truncated panel. That is the exact failure `C-32` exists to
   prevent.
2. **`Inc-REPAIR` before `Inc-7`** — **new, and it is the reason `Inc-REPAIR` sits in the vacated
   slot rather than at the end.** `Inc-7` ships `LLR-N13.1.5`'s containment and `AT-025b`; both are
   vacuous until `B-29` makes `load_or_notice`'s warning arm reachable. Reversed, `Inc-7` passes a
   containment test over a structurally empty set.
3. **`Inc-1` before `Inc-9`** — `LLR-COERCE.1` widens `plain()`; `LLR-N06.2.5`'s census asserts
   routing *through* `plain()`. A dependency, not a convenience.

**`keymap.py`'s collision set — RE-DERIVED 2026-08-29, and it is FOUR, not three.** `#D5b`'s
"three-way" reading named `Inc-3`, `Inc-4` and `Inc-9`, dropping `Inc-6` as vacated. But
`PDR-addendum-3` `#D25`'s own correction had **already** derived the true set as `Inc-3`, `Inc-4`,
`Inc-8`, `Inc-9` — `Inc-8` adds seat rows for `HLR-N16.4` and this table's `Inc-8` row names
`keymap.py` explicitly. The "three-way" sentence was stale the moment `#D25` landed and is corrected
here rather than left to be re-discovered a third time.

**The set is now:** `Inc-3` (shipped) · **`Inc-4b`** (the `#D5b` rebind — `Inc-4a` does **not** touch
`keymap.py`) · `Inc-8` · `Inc-9`. Resolved by serial ordering and not by ownership: **each shall
re-run `duplicate_chords()` and the whole-seat pin on ENTRY and EXIT** (`C-D25b`), and **each shall
declare its own row diff and assert it EQUAL to the entry/exit difference of `bindings_for(scope)`**
(`C-D25a` as corrected) — a declared diff joined to no oracle is not a pin, because rebinding a fifth
row and declaring four leaves `duplicate_chords()` returning `[]`.

**Budgets after the re-scope, checked rather than asserted:** every live increment is at or under 4
source files except `Inc-2`, whose breach is **declared** and unchanged from `#D5`. `Inc-REPAIR` is
the smallest increment in the batch at one source file. **`#D21` removes a breach**: `Inc-3` returns
to 4-of-4 by moving `LLR-N06.2.5` to `Inc-9`, which absorbs it at zero added files.

### 5.4.1 · The FIXTURE budget — one line per increment (`QA2-C-07`, §6.5 A-64)

**Fixtures were counted nowhere, and three had accumulated unowned.** The source-file budget was
enforced from the first cut; the **fixture** cost of an increment was never stated, so a requirement
could mandate a new on-disk graph and no increment's budget would notice. `QA-N-08` is the case that
exposed it: `LLR-N07.1.2`'s widening arm needs a graph with attachments and distinguishing `meta`,
**and the shipped `legacy` fixture has neither** — so the arm cannot be driven on any fixture that
exists, and nothing said so.

| Inc | New fixtures it must build | Where declared |
|---|---|---|
| **Inc-1** | none — the census derives its input from the tracked tree | `LLR-S06.3.1` |
| **Inc-2** | none — byte-identity against the shipped pins | `LLR-N07.2.2a` |
| **Inc-3** | **`anidado`** — nested folds; `TC-032`'s normative naive-6-vs-painted-4 case | `LLR-N06.3.2` |
| **Inc-4a** | **a synthetic graph carrying attachments and distinguishing `meta`** (`QA-N-08`) — built by a **generator function** in `tests/inc4_support.py` into a `tmp_path` workspace, never a file under `fixtures/`. Executed on the shipped `legacy` at `5f4816c`: **0 attachments**, 4 of 8 nodes carrying no `meta` — so `LLR-N07.1.2`'s widening arm is undrivable on any fixture that exists | `LLR-N07.1.2` |
| **Inc-4b** | none — it drives `Inc-4a`'s fixture. **But the fixture is load-bearing for `LLR-N07.3.1`'s self-guard:** executed, `legacy` gives `tree_order == dict_order` under **both** of the batch's working queries (`carlos` and `riesgo`), so the self-guard would be vacuous there — `C-55` limb 2 landing on the very LLR that names it | `LLR-N07.3.1` |
| **Inc-5** | none — drives the derived renderer set over existing graphs | `LLR-N07.2.2b` |
| **Inc-REPAIR** | **a phantom-sidecar workspace** (`LLR-REPAIR.1`) · **an alias-bombed `nodes:` sidecar and its un-aliased control** (`LLR-N13.1.7`) | §3.9, `LLR-N13.1.7` |
| **Inc-7** | **a two-map workspace, one map carrying a directed cycle** (`AT-025b`) | `LLR-N13.1.5` |
| **Inc-8** | none — the legend reads the seat and the vocabulary declaration, **which `Inc-7` creates** (`A-101`) | `LLR-N16.2.1` |
| **Inc-9** | none — screen-scope migration drives shipped screens | `LLR-N16.1.2` |

**EVERY FIXTURE IS BUILT IN A `tempfile.mkdtemp` WORKSPACE, NEVER BY WRITING INTO `fixtures/`.** This
is a hard rule with an executed reason, not a style note: a probe that pointed the app at the real
`fixtures/` directory had the inspector's commit-on-blur **write through**, permanently altering
`fixtures/legacy.mmd` and `fixtures/legacy_nodos.yml` on a tracked tree. Restoration was possible
only because the damage was noticed. **A fixture that a test can damage is a fixture that will be
damaged.**

**`AT-048`'s generated 200-map workspace was the third unbudgeted fixture and is now gone** —
**DEFERRED (`#D24`)** with the mount budget it served. Recorded so the count of unbudgeted fixtures
reconciles rather than appearing to have been quietly absorbed: of the three `QA2-C-07` named,
`anidado` and `QA-N-08`'s synthetic graph are budgeted above, and the third left with its threshold.

**`QA-M-02` is restored to a ledger too, and it is DISCHARGED elsewhere** (`QA2-C-02`): the A3 blast
radius is re-derived, with its question, instrument and SHA, in `LLR-N07.2.2a`'s threshold. It is
recorded here because `QA-M-02` was marked **DROPPED** with zero occurrences in any artifact — and a
minor that is dropped without a line saying where it went is indistinguishable from one that was
lost. **That is the failure mode `QA2-C-07` names, and this section is its fix.**

---

## 6. Appendices

### 6.1 Open questions carried forward from Phase 1

| # | Question | Status | Where the evidence is |
|---|---|---|---|
| **Q-1** | `IRenderer.render` shape | **ANSWERED at ARQ** — `ViewState` frozen dataclass, `PLAN.md` §9 D4, `docs/ARCHITECTURE.md` §4a | — |
| **Q-2** | fold-state owner | **ANSWERED at ARQ** — `MapScreen`, D5 / R-013 | — |
| **Q-3** | the `n` chord collision | **RULED — `PDR-2026-08-26-ui-next-batch-02#D5b`.** Three seat rows change in Inc-4, reviewed row-by-row at DDR: `map/n -> next_hit "siguiente coincidencia" (nav)`, `map/N -> prev_hit "coincidencia anterior" (nav)`, `map/M -> next_gap "siguiente faltante" (view)`. Folded into `HLR-N07.3` and `LLR-N16.1.2` | **M-9**; 01b §1.3; PDR §4.3 |
| **Q-4** | two definitions of "hit" | **ANSWERED at ARQ** — `search` owns matching, D6 / R-014. Phase 1 adds the **magnitude**: 2 -> 5 on the **M-7** fixture, monotone | HLR-N07.1 |
| **Q-5** | repo provenance for `◍` | **RULED OUT — `PDR-2026-08-26-ui-next-batch-02#D7`. Not deferred, not ambiguous: out.** Executed basis: provenance is recorded nowhere; there is **no `maps` table** (`store.py:71-104` creates `meta`, `nodes`, `fields`, `attachments`, `edges`, and `meta` is a *global* key/value table not keyed by `map_id`); and there is **no migration machinery at all** — `CREATE TABLE IF NOT EXISTS` is the entire story, so a new *column* would silently not apply to existing databases. Admitting it here would smuggle a persistence change and a migration into a UI increment. S-3b stays `REFINE`; nothing in §3 derives from it | §2.8.6; PDR §5 |
| **Q-6** | undefined lens field | **ANSWERED at Phase 1** — three outcome classes, executed | §2.8.2, **M-8**, HLR-N14.1 |
| **Q-7** | the lens walk chord | **RULED — `PDR-2026-08-26-ui-next-batch-02#D6`. `⇥` REJECTED; the unification is ratified.** `n` / `N` walk the single active *coincidencias* set — whichever of search-hits or lens-matches is live. `priority=True` making the mechanism "work" is the problem, not the solution: it is what **takes** `tab` from focus traversal, and `tab` is the inspector's only keyboard route. Carries **C-D6a** and **C-D6b** — see `HLR-N07.3` and `LLR-N14.3.2` | §2.8.4, **M-10**, PDR §5 |
| **Q-8** | bare word in a lens query | **RULED — `PDR-2026-08-26-ui-next-batch-02#D8`. A bare word is a MALFORMED token, with a redirect.** `/` is free text; the lens is structured `key:value`. Were a bare word also free text, the two features would become one feature with two syntaxes and two entry points, and D6's "only one result set is live" invariant would become much harder to reason about. Folded into `LLR-N14.1.3` | LLR-N14.1.3; PDR §5 |
| **Q-9** | migrate or declare | **RULED — `PDR-2026-08-26-ui-next-batch-02#D9`. MIGRATE BOTH, with one gated condition.** Declare-only is not an option; it only looked like one — it fails `LLR-N16.1.2`'s own `len(bindings_for(scope)) >= 3` threshold, or satisfies it with seat rows that **duplicate** hand-written bindings, which is the exact defect the seat abolishes. Carries **C-D9a**, **C-D9b**, **C-D9c** — see `LLR-N16.1.2` | LLR-N16.1.2, **M-11**; PDR §5 |
| **Q-10** | the three census exceptions | **RULED — `PDR-2026-08-26-ui-next-batch-02#D10`, one disposition per site**, all three read and confirmed. Folded into `LLR-S06.3.2`. One correction on re-execution: the progress-`WARN` site is **`app.py:879`**, not the PDR's `:848` | LLR-S06.3.2, **M-3**; PDR §5 |

**`QA-B-10` IS DISCHARGED BY FOLDING, NOT BY RE-RULING (§6.5 A-26).** `QA-B-10`'s finding is that
five open questions gated eleven `AT`s that PDR was being asked to approve, and that *"a
chord-agnostic requirement is legitimate; a chord-agnostic acceptance test is not"*. **All five were
ruled in the sealed `PDR-2026-08-26-ui-next-batch-02.md` §5 and §4.3.** The defect was that the
rulings never reached this document, so the ATs stayed chord-agnostic and an implementer would have
had to infer the key. Every ruling is now folded into the requirement text that owns it, and every
affected `AT` drives a **real key**. **No ruling is re-made here** — where this amendment differs
from the PDR it is a re-executed address (`app.py:848` → `:879`), recorded as a correction and not
as a new decision.

### 6.2 Requirements that could NOT be made fully observable — findings, not failures

Three at draft; **one is now discharged and two are added by this amendment set.**

1. **~~LLR-N06.3.2's nested-fold negative control has no fixture.~~ DISCHARGED (§6.5 A-22).** The
   parked entry recorded the gap honestly and then deferred it to Phase 3, which `QA-B-05` correctly
   said is not a discharge. The `anidado` fixture is now **built, written through `MapStore.save`,
   reloaded through `MapStore.load`, and specified normatively in `LLR-N06.3.2`** with its measured
   disagreement `naive_sum = 6` vs `painted_sum = 4`. The shipped fixture's unfalsifiability is
   additionally now **proved by exhaustion** — all 7 non-empty fold configurations of `legacy`, 0
   disagreements — rather than argued from the nestable-candidate structure. **Residual, carried:
   the fold input has no handler today**, so the transcript is set arithmetic over
   `(graph, folded)`; `TC-032` re-runs it through the Pilot once Inc-3 ships fold.
2. **HLR-S06.2's perceptual claim is not observable at all by any test this batch can write.**
   Distinct 256-colour slot numbers were measured (35 / 38 / 105, **M-2**). Whether a human tells
   slot 33 from slot 38 on a real terminal is not something `pytest` can answer, and no assertion in
   §3 claims it. It is routed to the `ux-reviewer` lens at PDR and flagged `assumed` in the
   requirement, rather than being converted into a proxy assertion that would look like evidence.
3. **HLR-CNV.2's braille glyph *count* is deliberately unspecified beyond strict positivity.** The
   number depends on `radial.py`'s step arithmetic, which has no user-visible meaning; a pinned
   number would be brittle against a layout tweak and would then be *maintained* rather than
   *believed*. Only `> 0` where the pre-state is exactly `0` is asserted. This is a deliberate limit
   on observability, and it is stated so that a reviewer does not mistake the looseness for an
   oversight. **The containment arm added by §6.5 A-11 / A-24 is *not* subject to this limit** — it
   is a subset relation over a set derived from the same code path on both sides, so it is neither
   brittle nor hand-maintained.
4. **The map canvas's braille promise now belongs to NO requirement in this batch (§6.5 A-24).**
   `HLR-CNV.2` is relabelled `PIN (radial)` because `LayeredRenderer` — the map canvas's default
   view — measures **0 braille before and 0 after**, structurally: there are exactly two `.dots`
   sites in the tree and both are in `radial.py`, so no fix to `Canvas.rows()` can raise it above 0.
   US-N06's prose still speaks of the *map canvas*. **This is a declared gap, not a silent one**: if
   free-angle edges on the layered view are wanted, that is a separate story with its own renderer
   work, and it is not in this batch's scope.
5. **`LLR-N06.3.2`'s two rules are proved as arithmetic, not yet through the shipped surface.**
   Recorded separately from item 1 because they are different claims: item 1 is discharged (the
   fixture exists and discriminates); this is the residual that the *screen* has not been observed
   doing it, and cannot be until Inc-3 ships fold. Any reading of item 1 as "fully observable" would
   be wrong.

### 6.3 Open risks this phase adds to `PLAN.md` §8

| # | Risk | Why Phase 1 raised it |
|---|---|---|
| R-7 | **~~US-N14's walk chord may be unbuildable as briefed.~~ CLOSED by `#D6`** — `⇥` rejected, `n`/`N` walk the single active *coincidencias* set, the two `tab` guards stay green and `TAB_BINDING_EXCEPTIONS` gains nothing. **Residual risk retained:** `C-D6a`'s "only one result set is live" invariant is now load-bearing for two stories at once, and it is new mechanism. | The decision was made; the premise it rests on is a thing the batch must build and test, not a thing it inherits. |
| R-8 | **`FactoryScreen` and `SettingsScreen` sit at the intersection of three fences** — `UNMIGRATED_SCREENS`, `TAB_BINDING_EXCEPTIONS`, and the help-scope defect. Touching one fence moves the others. **`#D9` rules MIGRATE BOTH, which raises rather than lowers this risk**, and gates the riskiest part (`C-D9a`, the `tab` drop) behind a probe that must first prove it can fail. | Q-9. Discovered at draft (**M-11**), not at the **`Inc-9`** gate (§5.4; ~~Inc-7~~ was the stale 7-cut number — `P2-B1`). The gate is now explicit: **if the positive control cannot be built, the `tab` drop does not ship.** |
| R-10 | **`S-15` — `MAX_RENDER_NODES` bounds the count, not the work.** A 73-node map renders in 70 s; a 12 000-node chain in 180 ms. Shipped defect on `master`, reproduced independently twice. | Found after the PDR that produced the blocker list. `HLR-N13.3` fixes what the budget must be a bound **on**; the defect itself is recorded so the budget is not read as precautionary. |
| R-11 | **The `AT` id space moved during amendment.** Three ids deleted, two struck, five added or split (`AT-007b`, `AT-025b`, `AT-034b`, `AT-048`). Any consumer holding the parked list is stale. | `QA-B-03` plus the splits `QA-M-12` / `QA-M-13` required. §5.2 now states the count as a derivation precisely so this class of drift is detectable rather than transcribed. |
| R-9 | **P-13 was under-counted because its own census was file-scoped.** The same shape may sit under other premises this batch inherits. | §2.8.3. The correction is recorded; the generalisation is a watch-item for DDR's C-18 sweep. |

### 6.4 Phase-1 reconciliation log

**Reconciliation event R-1 — against the sibling Phase-1 artifact `01b-ux-decisions.md`
(ux lens, 682 lines, executed transcripts).** That document was authored in parallel and settles
Q-3 and Q-6 from the interaction side, specifies six empty and boundary states, and records a
cognitive walkthrough plus a 20-row C-16 interaction inventory. Seven of its findings changed §3 —
**one of them because my draft was simply wrong**, and one because a probe I wrote to verify a
requirement committed the exact error the requirement forbids.

**Body-first ordering was honoured:** every §3 edit below was written first, and each row here points
at the line that now reflects it.

| # | What changed | Parent HLR re-read? | Body edit landed? |
|---|---|---|---|
| **D-1** | LLR-N07.3.2's empty-result count line moved from `WARN` to `MUT`, and its text from `0/0 coincidencias` to `0 coincidencias`, plus a hint line. **The draft was wrong.** The ux lens's argument, which the draft had missed: `WARN` is the tone that means *a hit*, so an empty result must not borrow the hit colour. | **HLR-N07.3 re-read — no change required.** Its statement says "a state distinct in both text and tone", which is tone-agnostic and still holds; only the LLR's chosen tone changed. | LLR-N07.3.2 Statement + Touched symbols + the "Reconciled against" block |
| **D-2** | HLR-N06.1's edge behaviour changed from a silent no-op to a no-op **that declares itself** (`borde del territorio`). Blank space past the content is indistinguishable from "the map has nothing there" — the confusion US-N06 exists to remove. | **HLR-N06.1 IS the parent and it changed.** Its Statement and its Numeric pass threshold were both edited so the threshold cannot assert less than the statement promises. | HLR-N06.1 Statement, Rationale, Numeric pass threshold |
| **D-3** | LLR-N06.2.2 gained a notification on folding a leaf, matching the precedent `next_gap` already sets. | **HLR-N06.2 re-read — no change required.** The parent governs painted pills; a notification on a no-op is strictly additional and contradicts nothing in it. | LLR-N06.2.2 Statement + Numeric pass threshold |
| **D-4** | **New LLR-N06.2.4** — the walk unfolds a branch containing the target, announces it, and does not re-close. Two new `AT` ids, `AT-046` and `AT-047`. | **Two parents re-read: HLR-N06.2 and HLR-N07.3.** HLR-N06.2 changed (the pill now declares hidden hits); HLR-N07.3 required no change — its walk statement already promises the selection lands on the match, and this LLR is what makes that promise observable. | LLR-N06.2.4 (whole block); HLR-N06.2 Statement + value reconciliation; §5.2 behavioral row for US-N06 |
| **D-5** | LLR-N14.1.1's oracle strengthened from "text and style spans differ" to **"the canvas itself differs"** — unchanged for an undefined field, fully dimmed for a well-formed zero match — plus verbatim Spanish copy and a schema-derived field list. The draft's weaker oracle would have passed on an implementation that dimmed the canvas in both cases, which is the pixel-identity Q-6 exists to prevent. | **HLR-N14.1 re-read — no change required.** Its three declared outcome classes are unchanged; the LLR's observation method got stronger, not its classification. | LLR-N14.1.1 Statement, Acceptance criteria, Normative copy block |
| **D-6** | HLR-N16.1's set-equality oracle moved from the legend's *content* to **what the panel presents**, and the shipped truncation defect was recorded: content needs 38 rows, `#help-dialog` is capped at 28 (`help.py:39`), no scrolling container — 10 rows clipped at every size, and 01b budgets the full atlas legend at 54 rows against a 34-row terminal. | **HLR-N16.1 IS the parent and its Statement changed** (`the set of key rows the legend presents`). Its threshold was re-read and still holds, because the threshold counts screens with a mismatch, and the clip makes more screens mismatch, not fewer. | HLR-N16.1 Statement + the "SECOND shipped defect" block + the "Consequence for the oracle" block |
| **D-7** | HLR-N16.3 gained the executed mechanism note (Textual has no chord support; a comma-separated binding fires on the first press) and a **second reservation** for the `minus` key, owed to batch 4 for the same reason `??` is owed to batch 3. | **HLR-N16.3 re-read — no change required.** Its statement asks only for a declared outcome and no stacked second legend, which is deliberately weaker than "build a chord" and is satisfied by the shipped `MODAL_SCOPES` behaviour. | HLR-N16.3 Mechanism note + second-reservation block |

**One correction that is not in the table because it corrects a probe, not a requirement — recorded
because hiding it would be worse than the error.** My draft-time probe **M-11** measured the legend
by calling `.render()` on `#help-content`, which returns the **full** text, and reported
`MATCH=True` at 27 rows for map scope. The panel clips 10 of those rows. **A probe that reads past
the clip cannot see the clip** — which is the identical error class HLR-N16.1 exists to forbid,
committed while writing the requirement that forbids it. It was caught by reconciling against 01b,
not by re-running the probe, and re-running the probe would never have caught it. It is noted in the
body at HLR-N16.1 and in `01c-measurements.md` M-11.

**Corrections to cited line numbers**, each recorded in the body where it lands rather than only
here, per the body-first rule. Six in total: three against documents this batch inherited, and three
against citations this draft made from an offset read of `mapper/app.py`.

| What was cited | What executed | Body line that now reflects it |
|---|---|---|
| inline predicate at `views/layered.py:144-149` (brief, `PLAN.md` §9 D6) | `layered.py:144-148`, consumer at `:159` | HLR-N07.1, "Citation correction" |
| `?` routing broken in **three** screens (P-13) | **five** — plus `screens/factory.py:413`, `screens/settings.py:92` | §2.8.3 and HLR-N16.1's threshold |
| legend title at `help.py:60` | `help.py:61` | HLR-N16.2, value reconciliation |
| `HomeScreen._map_metrics` at `app.py:377` | `app.py:369` | LLR-N13.1.1 Touched symbols |
| `HomeScreen._empty_text` at `app.py:558`; recents loop at `:545-556` | `app.py:554`; loop at `:536-552`, `store.load` at `:539`, `add_columns` at `:516`, `add_row` at `:546-552` | HLR-N13.2 Rationale; LLR-N13.1.1; §4.2 `home_cards` |
| `_pagination_text` at `app.py:1257`, `_minimap_text` at `:1236` | `:1269` and `:1251` | §4.2 `overflow_indicator` naming-hazard note |

### 6.5 Requirement amendments

**Amendment set 1 — the un-park, 2026-08-27. Base moved `d6b60e6` → `d877784`.**

> **Method.** Every claim below was **re-executed against the tree at `d877784` in this amendment
> session**. The parked document was read; no claim in it is relied on without re-execution (C-43).
> **Six of them came back different, and in each case the executed result governs and the correction
> is recorded here rather than made quietly.** Amendments are `A-NN`. `PLAN.md` §12.5 **D20**
> governs the form: struck material stays readable, marked, with its evidence.
>
> Authorities: `PLAN.md` §12.5 **D16**–**D20**; `02a` §3 blockers `QA-B-02`, `QA-B-03`, `QA-B-04`,
> `QA-B-07`, `QA-B-08`, `QA-B-09`; `02b` §6 conditions **C-3** through **C-8**; validator rule
> **V12**.

---

#### A-01 · `map_body_regions`'s owner is re-pointed *(D16)*

- **Before:** §4.2 `COMPONENT: map_screen`, `owner : LLR-S07.1.1`.
- **After:** `owner : LLR-R04.1`.
- **Deleted tokens:** none. **New tokens:** `LLR-R04.1` (a reference, defined at
  `.dev-flow/2026-08-26-repair-batch/01-requirements.md:190`).
- **Parent-HLR re-read:** `HLR-S07.1` re-read in full and struck (A-02). The contract row survives
  its owner because the three regions still exist and are still consumed positionally; deleting the
  row would remove a live contract, and leaving a struck owner would make it trace to nothing.
  `V21` resolves the new id — re-run after the edit, **0 V21 blocks**.

#### A-02 · §3.1 (S-7) is struck as `SATISFIED-EXTERNALLY`, and `QA-B-02` is DISSOLVED *(D16)*

- **Before:** §3.1 declared the Acceptance block for S-7, `HLR-S07.1`, `LLR-S07.1.1`,
  `LLR-S07.1.2`, `LLR-S07.1.3`, with `AT-001`, `AT-002` and `TC-001`, `TC-002`, `TC-003`, `TC-004`,
  `TC-005` as live work in Inc-1.
- **After:** the section carries a `SUPERSEDED — SATISFIED-EXTERNALLY at d877784` banner, is
  non-normative, and is implemented by nobody in Phase 3. §5.2's behavioral row and its four
  functional rows are struck in place.
- **Deleted tokens:** `AT-001`, `AT-002`, `TC-001`, `TC-002`, `TC-003`, `TC-004`, `TC-005`
  (enumerated, never ranged — C-56). **New tokens:** none.
- **Evidence, executed:** `tests/test_repair_layout.py` carries `test_tc_r22_…` (`:130`),
  `test_at_r10_…` (`:176`), `test_at_r10b_…` (`:209`), `test_at_r11_…` (`:233`),
  `test_tc_r23_…` (`:403`), with `WIDE_SIZES = [(140, 45), (120, 40)]` and
  `NARROW_SIZE = (100, 24)` at `:45-46`.
- **Parent-HLR re-read:** `HLR-S07.1`'s parent is story S-7, which §2.6 lists as *"not in the brief
  — found at intake"*. Re-read: S-7 has **no dependent** in this batch other than the informal
  precondition note in `HLR-N06.1`'s rationale. Striking it does not orphan a child.
- **`QA-B-02` DISSOLVED, and its lesson re-homed.** `QA-B-02` attacked `AT-001` / `LLR-S07.1.3` /
  `TC-005` — *"the root-title oracle is FALSE on a correctly laid-out canvas"*. Those ids no longer
  exist here, so the finding has no subject. **The lesson is not dissolved**: it is re-homed into
  `HLR-N06.3`'s new `Painted-trace oracle` block, which is the batch's most important predicate and
  rests on the identical oracle. Executed there: a 36-character title paints as
  `▐ Un titulo bastante lar…` at 80 x 24, so a raw-title trace is false and a raw-**id** trace is
  false always.

#### A-03 · The S-8 clipping half of `HLR-N16.1` is struck; the per-view half survives *(D17)*

- **Before:** *"**A SECOND shipped defect …: the legend does not fit.** … The content overflows its
  container by **10 rows at every terminal size**, and there is no scrolling container. **US-N16
  cannot paint one flat panel**."*
- **After:** that paragraph is struck `SUPERSEDED — SATISFIED-EXTERNALLY at d877784` with the
  shipped guard named. **The per-view legend half of US-N16 is untouched and is still the story.**
- **Deleted tokens:** none — no `AT` or `TC` was owned by the clipping half alone.
  **New tokens:** none.
- **Evidence, executed:** `mapper/screens/help.py:73-75` wraps the bindings in a `VerticalScroll`
  with `#help-bindings { … overflow-y: auto }` at `:49-51`. Guarded by
  `tests/test_repair_layout.py::test_tc_r24_the_bindings_region_is_scrollable` and
  `::test_tc_r36_the_dialog_height_is_governed_by_a_named_declaration`.
- **Parent-HLR re-read:** `HLR-N16.1` re-read in full. Its statement has **two independent
  conjuncts** — *"declares a scope and opens the legend for it"* and *"every row reachable without
  leaving the legend"*. Only the second is satisfied externally. The first is the live defect: **5**
  un-scoped routes and **2** screens with no `KEY_SCOPE`, both re-executed at `d877784` (A-06). The
  HLR therefore stands, amended, rather than being struck with the paragraph.

#### A-04 · `LLR-N13.1.5` is written — and the premise it was to be written against EXECUTES FALSE *(C-3, C-2's second half)*

- **Before:** no `LLR-N13.1.5` existed. The only error statement in the document was the
  boundary-catalog line *"`AT-025` includes a map whose load raises; the card paints without the
  screen failing."*
- **After:** `LLR-N13.1.5` exists, with the declared card state `mapa dañado — ↵ ver por qué`, a
  two-clause threshold, and three named mutants.
- **Deleted tokens:** none. **New tokens:** `LLR-N13.1.5`, `TC-074`, mutants `M-H1b`, `M-H4`.
- **THE CORRECTION.** `PLAN.md` §12.4 and `02b` S-03 both state that a refusable map yields *"a
  notification and **no card at all**"*. Re-executed under `App.run_test`:

  ```
  workspace: bueno.mmd (acyclic, 3 nodes) + roto.mmd (a --> b --> c --> a)
  screen mounted without raising : True
  row_count                      : 2
     row: ['bueno', ' concept ', '3', '0']
     row: ['roto',  ' concept ', '0', '0']
  ```

  **A card IS painted.** `mapper/app.py:566-567` sets `kind, nodos, docs = "concept", "0", "0"` and
  `:568-573` adds the row unconditionally. The failure is **misdeclaration**, not omission. The hero
  (`:481-492`) and resume (`:512-531`) branches *do* vanish silently, so both modes are live.
- **Why this matters more than a footnote.** `M-H1`'s threshold as `02b` states it — *"painted card
  count, not 'the screen did not raise'"* — **is already green at `d877784`**. A requirement written
  to it alone would pass on the shipped defect. The threshold is therefore **painted card count AND
  per-card state distinguishability**, and `M-H1b` names the mutant that made the difference visible.
- **Parent-HLR re-read:** `HLR-N13.1` re-read in full. Its statement quantifies over *"each map"*
  and says nothing about maps that fail, so the new LLR **widens** the parent rather than
  contradicting it; the parent is amended only by gaining `HLR-N13.3` as a co-parent for this LLR.

#### A-05 · `HLR-N13.3` is written, and `M-H3` is confirmed as a LIVE DoS at the new base *(C-3)*

- **Before:** absent. `02b` S-03: *"Grepping 2 707 lines for `timeout`, `DoS`, `denial`, `max nodes`,
  evaluation bound, map-count cap, node-count cap or size cap returns **nothing**."*
- **After:** `HLR-N13.3` exists with a four-clause threshold, expressed **relative to the shipped
  `MAX_RENDER_NODES = 12000`** (D19) so the batch does not ship a second definition of *"too big"*.
- **Deleted tokens:** none. **New tokens:** `HLR-N13.3`, `LLR-N13.1.6`, `AT-048`, `TC-075`,
  `TC-076`, mutants `M-H5`, `M-H6`.
- **Executed evidence, and it is the most consequential measurement in this amendment set.** A
  layered DAG whose each layer is fully connected to the next, rendered by `LayeredRenderer` at
  80 x 24:

  ```
  w= 8 layers=5  nodes=  41  render=     497.4 ms   allowed by MAX_RENDER_NODES: True
  w=10 layers=5  nodes=  51  render=    1935.7 ms   allowed by MAX_RENDER_NODES: True
  w=12 layers=6  nodes=  73  render=   72476.9 ms   allowed by MAX_RENDER_NODES: True
  ```

  For contrast, a **12 000**-node chain renders in **186.3 ms** and a `d=7 b=3` tree of 3 280 nodes
  in **59.7 ms**. **A 73-node map costs 72.5 seconds and the shipped cap waves it through.**
  `MAX_RENDER_NODES` bounds the count dimension and nothing else; the budget must bound **work**.
- **A second correction, recorded.** `02b`'s renderer figures (3.4 s at n=3280, 9.1 s at n=10 000)
  were measured at the parked base. Re-executed at `d877784` the same shapes are **59.7 ms** and
  well under a second — the repair batch's traversal fix moved them by two orders of magnitude. The
  parked numbers must not be quoted as current. **The conclusion is unchanged and the reason is
  stronger**: the cost that remains is driven by the edge list, which no shipped bound touches.
- **Parent-HLR re-read:** US-N13 re-read in full, including its `INVEST` verdict in §2.6. The story
  is *"home shows each map's own shape"*; a budget on the screen that shows them is **inside** the
  story's boundary, not a scope-add. Recorded because the alternative reading — that this is a
  performance story and belongs elsewhere — is defensible and was considered and rejected: `02b`'s
  gate verdict turns on US-N13 being *"what turns 'the operator opened a hostile map' into 'the
  operator started the application'"*, which is a property of this story and no other.

#### A-06 · Every `HLR-N16.1` address re-derived; `QA-B-04` discharged by an on-disk artifact

- **Before:** *"derived screen count `>= 7` (executed: 7 `action_help` definitions — `app.py:742`,
  `:793`, `:1058`, `:1828`, `:1986`, `screens/factory.py:413`, `screens/settings.py:92`)"*.
- **After:** the same verdicts at re-derived addresses — `app.py:773`, `:824`, `:1089`, `:1884`,
  `:2049`, `screens/factory.py:486`, `screens/settings.py:92`. **Six of the seven moved.** The
  counts are unchanged: **7** definitions, **5** un-scoped routes, **2** screens with no
  `KEY_SCOPE`. P-13's corrected verdict of 5 is re-confirmed.
- **Deleted tokens:** none. **New tokens:** mutants `M-N16.1-a`, `M-N16.1-b`.
- **`QA-B-04` is discharged by citing an artifact, not by re-inventing one.** The oracle is now
  `_painted_bindings` (`tests/test_repair_layout.py:104-123`) over `_rows_in` (`:74-82`), and its
  negative control is `::test_at_r14_the_oracle_is_clipped_to_the_help_dialog` (`:339`), whose four
  limbs are exactly the control `QA-B-04` demanded. **Writing a second one is forbidden by the
  amended requirement** — two guards for one oracle is the two-owners defect this batch removes
  elsewhere. Every legend `AT` now declares its Pilot size, read from `WIDE_SIZES` / `NARROW_SIZE`.
- **`bindings_for` is pinned (`QA-M-04`).** Executed: `len(bindings_for('map')) == 27` while `KEYMAP`
  holds **25** map-scope entries. The parked document used both numbers. Every count in the
  requirement is now `len(keymap.bindings_for(scope))`, evaluated at run time.
- **Parent-HLR re-read:** US-N16 re-read in full; its Acceptance block is amended in the same edit
  (A-07) and its outcome statement is unchanged.

#### A-07 · `AT-027`, `AT-028`, `AT-045` deleted; every count becomes a derivation *(`QA-B-03`)*

- **Before:** `US-N13` — *"**Acceptance tests:** `AT-025`, `AT-026`, `AT-027`, `AT-028`, `AT-029`,
  `AT-030`, `AT-031`."* `US-N16` — *"`AT-041`, `AT-042`, `AT-043`, `AT-044`, `AT-045`."* §5.2 —
  *"**47 acceptance tests across 8 derivable stories**"* and *"**Counts: 21 HLR · 48 LLR · 47
  `AT-NNN` · 71 `TC-NNN`**"*.
- **After:** `US-N13` — `AT-025`, `AT-026`, `AT-029`, `AT-030`, `AT-031`, `AT-048`. `US-N16` —
  `AT-041`, `AT-042`, `AT-043`, `AT-044`. §5.2 states **no literal total**; it states the
  derivation — the three-way intersection of the story list, some requirement's `Acceptance:` line,
  and the behavioral table — and defers the figure to the QA lane's concurrent census in
  `01d-unpark-measurements.md`.
- **Deleted tokens:** `AT-027`, `AT-028`, `AT-045` (each appeared exactly twice and was claimed by
  no requirement), plus `AT-001`, `AT-002`, `TC-001`, `TC-002`, `TC-003`, `TC-004`, `TC-005` via
  A-02. **New tokens:** `AT-048`, `TC-072`, `TC-073`, `TC-074`, `TC-075`, `TC-076`.
- **Why a derivation rather than a corrected literal.** The parked line said the counts *were*
  derived — and they were, once, at close of draft. **The transcription into a literal is what went
  stale**, three ids later. Correcting `47` to a new number would repeat the defect with a fresher
  wrong number. `V2` corroborates from the other side: it reports one block per declared `AT` with no
  node on disk, which before implementation **is** the declared count.
- **Parent-HLR re-read:** `HLR-N13.1` and `HLR-N16.1`/`HLR-N16.2` re-read; none claimed any of the
  three deleted ids on an `Acceptance:` line, which is what made them deletable rather than
  under-specified.

#### A-08 · `LLR-N13.1.3`'s coverage value is PINNED at 100 *(`QA-B-07`)*

- **Before:** *"**Statement:** … every surface that states a coverage percentage for that map shall
  state the same value."* / *"**Numeric pass threshold:** the three computations return the identical
  value for a schema-less graph."*
- **After:** *"… shall state the value **100**, and shall state the same value as every other such
  surface."* / *"`pct(schema-less) == 100` at every consumer of `graph.coverage()`, **and** the
  consumers agree with one another. Both clauses are required."*
- **Deleted tokens:** none. **New tokens:** mutants `M-N13.1.3-a`, `M-N13.1.3-b`.
- **Executed, with re-derived addresses — every parked address for this LLR was stale:**

  ```
  Graph().coverage() -> (0, 0)
  mapper/app.py:379            int(100 * have / max(1, req))                 ->   0   <- outlier
  mapper/views/layered.py:179  round(100*have/req) if req else 100           -> 100
  mapper/widgets/rail.py:274   round(have/req*100) if req else 100           -> 100
  ```

  Parked `layered.py:119` and `rail.py:149` no longer hold. The consumer lines are `app.py:378`,
  `layered.py:178`, `rail.py:273`.
- **Why the pin and not the agreement clause alone.** The plausible weaker commit changes the two
  correct sites to match the outlier: three sites agree, the agreement clause is green, and the
  product ships *"0 % documentado"* on every schema-less map. 100 is correct on the merits — a map
  with no required field has no unmet requirement — and `max(1, req)` is the bug: it manufactures a
  denominator that is not there.
- **Parent-HLR re-read:** `HLR-N13.1` re-read. Its statement covers the thumbnail, the bar and the
  node count and does **not** mention the percentage, so pinning the value here does not contradict
  the parent. Recorded because it means the parent gives this LLR no cover: `LLR-N13.1.3` is the
  only place in the document where the number 100 is normative.

#### A-09 · `LLR-S06.3.4`'s severity-site figure is corrected

- **Before:** *"derived severity-site count `>= 29`"*, with *"executed today: **29** sites"*.
- **After:** the `>=` bound is retained but its parenthetical measurement is superseded; the
  derivation governs. Re-executed:
  `grep -rnE 'darkside\.(WARN|ALERT)' mapper --include=*.py | wc -l` gives **36**.
- **Deleted tokens:** none. **New tokens:** none.
- **Recorded rather than silently re-typed** because it makes `QA-M-03`'s point concrete: a `>=`
  bound on a *derived* count **cannot detect a census that under-derives**, and `>= 29` is now green
  with 7 sites of slack. The equality-versus-floor ruling for this and for `LLR-S06.3.3` belongs to
  the QA lane and is not made here. `LLR-S06.3.3`'s figure **does** still reproduce:
  `grep -rn '#1783ff' mapper --include=*.py | wc -l` gives **8**.
- **Parent-HLR re-read:** `HLR-S06.3` re-read in full; its threshold *"the derived site count is
  `> 0` (measured **95** today)"* re-executed — six-hex-digit literals across the 33 tracked
  `mapper/**/*.py` files: **95**, unchanged.

#### A-10 · `WARN` and `ALERT` get one job each, adjudicated from the tree *(`QA-B-08`)*

- **Before, two live and contradictory definitions:**
  - `HLR-N06.2` — *"here `WARN` is correct precisely because it **does mean a hit**, the same
    reasoning that removed it from the empty-result line."*
  - `LLR-N07.3.2` — *"**Severity is the declared job of `WARN`** (LLR-S06.3.4), and 'your query found
    nothing' is a severity, so this use is consistent with the census."*
- **After:** `LLR-S06.3.5` declares **one job per token**, and both sentences above are struck in
  place with their replacements:
  - **`WARN` `#ffd230` — *outstanding attention*: work is pending, due, at risk, or in flight, and
    nothing has failed.**
  - **`ALERT` `#ff4f42` — *failure or blockage*: this item cannot proceed as it stands.**
- **Deleted tokens:** none. **New tokens:** `LLR-S06.3.5`, `TC-072`, mutants `M-S06.3.5-a`,
  `M-S06.3.5-b`.
- **Adjudicated by derivation, and it resolves AGAINST BOTH parked definitions.** The 36-site
  listing is pasted in `LLR-S06.3.5`. **`WARN` never paints a search hit — 0 of 36** — so
  `HLR-N06.2`'s reason is FALSE against the tree. And *"severity"* is the **family** both tokens
  belong to, not a job: it cannot tell them apart and would license painting an empty result in
  either, which is precisely what D-1 forbade.
- **Both conclusions survive on corrected reasons.** The fold pill keeps `WARN` (hidden matches are
  work pending); the empty count line keeps `MUT` (a finished question with an empty answer is
  neither outstanding nor failed). **`ALERT` acquires no second job**: `01b:332-333` warns that if it
  did, it would need a census row — a malformed lens query *cannot proceed as it stands*, which is
  the declared job verbatim, so the chip enters the census **classified**. §3.7 gains that
  classification row at `LLR-N14.1.3`.
- **A consequence flagged, not absorbed.** `app.py:879` — `darkside.WARN if self.loading else INK` —
  becomes classifiable under *in flight*, so `LLR-S06.3.2`'s claim that it is *"the single site the
  severity rule does not fit"* no longer holds. **Disposition owed at PDR**: retire the register
  entry or record why it stays. Its address also moved (parked `:848`).
- **Parent-HLR re-read:** `HLR-S06.1` re-read — it declares the one-job rule for the three **new**
  tokens and states *"a token carries exactly one job"* as a general rule, so extending it to the
  two shipped severity tokens is an application of the parent, not a widening of it. `HLR-S06.3`
  re-read — its statement already fails *"if a severity hue appears at a site that does not express
  severity"*, which is unadjudicable without exactly this LLR. `LLR-S06.3.5` is therefore a
  **precondition** of the census gate, not a companion to it.

#### A-11 · The `M-1` painted-glyph list is replaced by a run-time derivation

- **Before:** *"The glyphs already in the canvas vocabulary … are `· ◆ ● ─ │ ┌ ┐ ┬ ┼ ▐ …` (**M-1**,
  the distinct painted set)."*
- **After:** the list is struck; every predicate quantifying over "the canvas vocabulary" derives the
  set at run time from the renderer under test at its declared Pilot size.
- **Deleted tokens:** none. **New tokens:** none.
- **Executed — the list does not reproduce as any single renderer's painted set.** M-1's 6-node shape
  at 80 x 24:

  ```
  RadialRenderer    distinct non-space glyphs = 22 : ABCDERaefilmnoprstz·◆●
  LayeredRenderer   distinct non-space glyphs = 31 : 6ABCDERacdefilmnoprstz·─│┌┐┴┼▐◆
  ```

  `●` occurs only in the radial set; `┬` occurs in **neither**; the layered set carries `┴`, which
  the parked list omits. **The parked list blends two renderers and names a glyph the fixture never
  paints.** This matters beyond tidiness because `QA-B-09`'s containment arm was specified *against
  that list*; had it been adopted verbatim the arm would have asserted a subset relation over a set
  the renderer does not produce, and would have failed for the wrong reason.
- **Parent-HLR re-read:** `HLR-N06.2` and `HLR-CNV.2` both re-read; neither states the glyph set
  normatively, so the correction touches only informative reconciliation prose and one acceptance
  arm.

#### A-12 · `HLR-CNV.2` gains a subject criterion and the containment arm *(`QA-B-09`)*

- **Before:** *"**HLR-CNV.2** — braille free-angle edges appear **on the map canvas**"* /
  *"**Numeric pass threshold:** count `> 0` on the 6-node graph; count `== 0` on a single-node
  graph."*
- **After:** the title is renderer-neutral — *"braille free-angle edges reach the painted output of
  the renderer that draws them"* — the statement gains a second conjunct, and the threshold gains
  `pre_set ⊆ post_set`.
- **Deleted tokens:** none. **New tokens:** mutants `M-CNV.2-a`, `M-CNV.2-b`.
- **The subject question is left OPEN with its criterion stated, deliberately.** `QA-B-09` is right
  that the title named the map canvas while the acceptance rendered through `RadialRenderer`.
  Executed here, **both** renderers are at 0 braille pre-change, so the pre-state does not decide it.
  The criterion written into the requirement: **the subject is whichever renderer the Inc-2 change
  causes to emit braille**. If radial only, this is a `PIN (radial)` and the map-canvas promise
  becomes a recorded gap in §6.2; if layered too, the subject moves and the predicate is
  parametrized. The title is written so either answer is **a label change, not a rewrite**. The QA
  lane owns the measurement; this document owns the criterion.
- **Why `> 0` had to gain a partner.** Where the pre-state is 0, `count > 0` reddens a *deletion* but
  **cannot redden a plausible wrong implementation**: composing `dots` at the wrong precedence so
  braille overwrites the node cards emits glyphs, passes, and makes the map unreadable. The
  containment arm reddens exactly that and correctly passes `M-CNV.2-b`, which draws braille only in
  already-blank cells.
- **Parent-HLR re-read:** `HLR-canvas` (§3.3) re-read in full. It is the umbrella for `HLR-CNV.1`,
  `.2` and `.3`; `.1` is a unit-level `Canvas` requirement and `.3` is the focus tone, so neither
  constrains `.2`'s subject. `QA-M-12`'s companion finding — that `AT-007` is claimed by **both**
  `HLR-CNV.1` and `HLR-CNV.2`, two different chains under one id — is **left to the QA lane**; it is
  an id-hygiene ruling, not a predicate defect, and splitting it here would collide with the
  concurrent census.

#### A-13 · *"0 control bytes"* is replaced by `COERCION_RANGES` in all four thresholds *(C-4)*

- **Before**, at `LLR-N06.2.3`, `LLR-N13.2.1`, `LLR-N14.2.3`, `LLR-N16.2.3`: *"**0** control bytes in
  the painted text; **0** Rich markup tags interpreted"*, two of them adding a row-length clause.
- **After:** a single normative list, **§3.0 `COERCION_RANGES`**, referenced by all four; each
  threshold measured **on the painted row**; each gains the split-at-width arm.
- **Deleted tokens:** none. **New tokens:** §3.0, `COERCION_RANGES`, mutants `M-COERCE-a`,
  `M-COERCE-b`, `M-N06.2.3-a`, `M-N13.2.1-a`, `M-N14.2.3-a`, `M-N16.2.3-a`.
- **Executed — the gap, measured:** of the **84** code points the list declares, `_CONTROL_MAP`
  (`darkside.py:272-273`) covers **62**; **22 pass through untouched**, including every bidi range
  the hostile fixtures drive. `U+202E` is not a control byte, so all three LLRs that drove a
  right-to-left override **asserted nothing about the input they were testing**.

#### A-14 · *"coerce before truncating"* is half satisfied already, and the other half is a second truncator *(C-4)*

- **Before:** `02b` C-4 requires *"coerce **before** truncating"*, implying the ordering is wrong.
- **After:** the ordering clause is retained, **scoped to the truncator that actually lacks it**.
- **Executed:** `darkside.fit` (`darkside.py:290-297`) **already coerces first** — its first
  statement is `s = plain(s)`, and `fit(plain(s), 10) == plain(fit(s, 10))` is `True`. **But
  `mapper/views/layered.py::_fit` (`:38`) coerces nothing:**

  ```
  >>> _fit('a' + chr(1) + 'b', 8)
  'a\x01b     '
  ```

  and it emits every card title (`:217`, `:280`), the doc line (`:237`), the meta row (`:247`), the
  diff chip (`:227`) and the removed-ghost row (`:266`). **Two truncators ship; one coerces and one
  does not.** The load-bearing half of C-4 for `darkside.fit` is the widening; the ordering clause is
  live for `layered._fit`.
- **The split-at-width arm, executed.** A source balanced at `U+202E` … `U+202C` truncated at width
  10 leaves the override **with its terminator gone** — so the override governs the remainder of the
  row. The fixture is balanced at source and split at width, and the assertion is on the painted row,
  because a fixture unbalanced at source tests the wrong thing and an assertion on the string handed
  to the sink cannot see a defect that truncation creates downstream (`M-COERCE-a`).
- **Parent-HLR re-read:** all four parents (`HLR-N06.2`, `HLR-N13.1`/`HLR-N13.2`, `HLR-N14.2`,
  `HLR-N16.2`) re-read. None states a coercion threshold itself; each delegates to its LLR, so
  §3.0 can be a single normative definition without four parents contradicting it.

#### A-15 · The sink class covers PRE-EXISTING sinks, gated by a derived census *(C-7)*

- **Before:** *"the requirement is scoped to the **sink class** — every new text sink **this batch
  creates** — not to a file"*, with *"the ~20 legacy `rich.markup.escape` sites in `app.py`
  (carry B-03) are explicitly NOT in scope … including the one the recents loop uses today at
  `app.py:547` and the resume-row pair at `:503`, `:505`."*
- **After:** *"every file-derived string painted on a surface this batch touches, whether the sink is
  new or pre-existing"*, fixed by a **derived census** that asserts its own input set is non-empty.
- **Deleted tokens:** none. **New tokens:** none beyond the mutants in A-13.
- **Re-derived addresses — the parked ones are stale:** parked `app.py:503`, `:505` are now
  **`:524`, `:526`** (resume row); parked `:547` is now **`:568`** (recents row). All three are in
  scope: `HLR-N13.1` **rewrites the very loop they sit in**.
- **They are named as evidence, not as the census.** A hand-listed set of three line numbers goes
  stale the moment the loop moves — which is exactly what happened to the parked ones. That is
  `C-31`'s argument, demonstrated on this document's own text.
- **Why this wording was a condition and not a note.** *"Every new text sink this batch creates"*
  **re-encodes batch 1's own §2.1b failure into the requirement**: a scope that stops at the new
  code's boundary while the identical defect ships beside it. Still out of scope: legacy `escape()`
  sites on **untouched** surfaces — the inspector block at `app.py:242-293`, the palette table at
  `:205`, the layered ghost at `layered.py:266`.

#### A-16 · `LLR-N14.2.3` and `LLR-N16.2.3` widened to every file-derived string *(C-5)*

- **Before:** `LLR-N14.2.3` — *"every ficha **field value** placed into a lens result surface"*.
  `LLR-N16.2.3` — *"every **binding label** and every glyph-row caption placed into the legend"*.
- **After:** both read *"every **file-derived string** placed on the surface"*, with fixture
  positions **derived from `_build_sidecar`**.
- **Deleted tokens:** none. **New tokens:** mutants `M-N14.2.3-a`, `M-N16.2.3-a`.
- **The gap the parked wording left:** `02b` S-06 found that the lens's undefined-field declaration
  echoes file-derived **schema key names** — the `campos: D acta · O origen · E estado · C
  criticidad` list is read from the map's own schema — and a schema key name is **not a field
  value**, so no coercion LLR covered it. The legend has the same shape: its vocabulary captions
  describe glyphs painted from file-derived **branch names**, which are neither binding labels nor
  glyph-row captions as those terms were used.
- **A distinction recorded so it is not conflated.** `mapper/store.py::_coerce_field` (`store.py:39`,
  shipped by the repair batch, applied at `:235` and `:239`) coerces field values **to `str`**. That
  is a **type** coercion and discharges S-02; it is **not** the code-point coercion of §3.0 and
  discharges none of C-4 or C-5.
- **Parent-HLR re-read:** `HLR-N14.2` and `HLR-N16.2` re-read; both state what is *painted*, not what
  is *coerced*, so widening the LLRs does not outrun either parent.

#### A-17 · `LLR-N16.2.3` gains the row-length clause it was missing *(C-5)*

- **Before:** *"**Numeric pass threshold:** **0** control bytes in the painted text; **0** Rich markup
  tags interpreted."* — **no row-length clause**, the only one of the four coercion thresholds
  without one.
- **After:** *"… **the painted row length equals the legend's declared row width for every hostile
  input**."*
- **Deleted tokens:** none. **New tokens:** none.
- **Why it is load-bearing here specifically.** An unbounded caption row overflows its column, and
  `HLR-N16.1`'s oracle **clips to the dialog's region in `x`**. Content pushed past that clip is read
  as a **missing binding** — so a missing row-length clause on this surface turns a cosmetic overflow
  into a false negative in the batch's most important legend predicate.

#### A-18 · The `notify` census is derived, and the parked figure of 13 executes false *(C-8)*

- **Before:** `02b` S-09 — *"thirteen `notify()` sites interpolate exception text with markup parsing
  on"*; C-8 — *"`markup=False` + `plain()` on all 13 `notify` sites."*
- **After:** `LLR-N06.2.5` states the rule as a **class with a derived census**, verified by an `ast`
  walk, with two thresholds rather than one.
- **Deleted tokens:** none. **New tokens:** `LLR-N06.2.5`, `TC-073`, `leaf_fold_notice` (§4.2),
  mutants `M-N06.2.5-a`, `M-N06.2.5-b`.
- **Re-derived at `d877784`:**

  ```
  D1 total .notify( call sites                        : 30
  D2 sites with a NON-LITERAL first argument          : 19
  D3 of D2, markup NOT disabled                       :  0     <- markup half REPAIRED
  D4 of D2, first argument not routed through plain() : 15     <- coercion half LIVE
  ```

  **The markup half of S-09 is discharged by execution** — all 19 dynamic sites pass
  `markup=False`, and the 10 sites carrying no `markup=` keyword all have **literal** first
  arguments. **The coercion half is live and larger than 13**: 15 dynamic sites interpolate a value
  without `plain()`.
- **Scoped as a class, and this is why.** The repair batch's own post-mortem records that **naming a
  defect class without landing the census cost six rediscoveries**. The 15 addresses are evidence
  that the class is non-empty, not the specification — every parked S-09 address is already stale and
  every one of these will be after Inc-3. `M-N06.2.5-b` records why the census is an AST walk and not
  a grep: `grep -c "\.notify("` returns 30 here **by coincidence**, and says nothing about the first
  argument or the keywords.
- **§4 declaration.** C-8's second clause — *"declare `LLR-N06.2.2`'s new toast in §4"* — is
  satisfied: `leaf_fold_notice` is now an output of `COMPONENT: map_screen`. A text sink that no
  contract row names is a sink the reverse census does not see.
- **Parent-HLR re-read:** `HLR-N06.2` re-read in full. It is about fold declaration, and the toast is
  its `LLR-N06.2.2` outcome — so the toast belongs there, but the **class** does not: `LLR-N06.2.5`
  quantifies over the whole product.
- **~~"a cross-cutting LLR under a story-scoped HLR is a smell, and the alternative — inventing an
  HLR for it — would have been worse."~~ SUPERSEDED by `#D21` (`P2-B6`, §6.5 A-48; edit a-3).** The
  executed reason it was **not** worse: the notify class spans `mapper/screens/factory.py`, which
  `Inc-3` does not own, so satisfying `LLR-N06.2.5` inside `HLR-N06.2`'s increment is an
  **undeclared source-budget breach**, not a stylistic cost. **Inventing the HLR was the cheaper
  option all along, and recording the imperfection instead is what let it survive two PDR passes.**
  The criterion is now written down so the next cross-cutting LLR is **tested rather than argued**:
  > **Limb 1.** If the parent story were descoped, would the child's subject be deleted with it? If
  > no, the parent is wrong.
  > **Limb 2.** Does satisfying the child require editing source files outside the parent
  > increment's declared file set? If yes, the mis-parenting makes the owning increment
  > unsatisfiable within its declared budget.

  Limb 2 is what converts a smell into something a reviewer can execute and a gate can fail on.
  Both limbs, and the discriminating control that keeps `LLR-N06.2.3` where it is, are recorded at
  `LLR-N06.2.5`'s block in §3.4.

#### A-19 · IFC Part B is balanced; `V12` goes 12 → 0 *(validator, `PLAN.md` §12.2 F-14)*

- **Before:** `COMPONENT: map_screen` declared 4 inputs and 1 output, while its 7 children between
  them consumed `cursor`, `folded`, `state`, `node_id`, `query_text`, `active_groups` and emitted 8
  ids the parent never named. **12 `V12` blocks.**
- **After:** the parent declares all 10 inputs and 9 outputs. **0 `V12` blocks**, and the validator
  reports *"balancing holds on 6 parented component(s)"* — a real check rather than a skip.
- **Deleted tokens:** none. **New tokens:** the output id `leaf_fold_notice` (also A-18).
- **Executed, before and after:**

  ```
  before:  python ~/.claude/docs/tools/devflow-validate.py .   ->  62 block · 107 notice · 12 n/a
           V12 blocks in 01-requirements.md: 12
  after :  python ~/.claude/docs/tools/devflow-validate.py .   ->  51 block · 112 notice · 13 n/a
           V12 blocks in 01-requirements.md:  0
           V12 now reports: "balancing holds on 6 parented component(s)"
  ```

- **A parser fact worth recording, because it cost a cycle.** `V12` reads `INPUTS` as a `name: type`
  list, and `_parse_ifc` treats an indented continuation line **beginning with a word and a colon**
  as a *new field*, not as a continuation. A wrapped `INPUTS` line must therefore begin its
  continuation with the separator (`; cursor: str|None …`), not with the name. Written the natural
  way, the outputs balanced and the inputs silently did not.
- **Why re-declaring is the fix and not a workaround.** `MapScreen` genuinely owns `folded`
  (`LLR-N06.2.1` makes that the requirement), genuinely composes `state`, and genuinely is the widget
  whose region carries every one of those outputs. The child blocks remain the authoritative
  descriptions — value, consumers, owner — and the parent's rows exist so containment is
  **checkable**. §4.3's note that three components declare `PARENT: SYSTEM` and are therefore
  unchecked stands unchanged and is still the honest outcome.
- **Residual blocks are correct pre-implementation, and the `V2` count needs one honest caveat.**
  After this amendment the corpus reports **48 `V2`** — every declared `AT` has no node on disk,
  which is the C-18 realisation gate and is *supposed* to be red before Phase 3 — plus **1 `V7` and
  2 `V16`** against the auxiliary `~/.claude` repo, which `PLAN.md` §12.2 dispositions as
  FOUND-not-swept (C-44) and carries to `BACKLOG.md`. **No `V12`, no `V21`.**
- **The caveat: `V2` went 47 → 48, and it will not fall to reflect the five deletions.** `V2`
  harvests **every** `AT-\d+` token in the file (`devflow-validate.py:113`) with no supersession
  awareness, so `AT-001`, `AT-002`, `AT-027`, `AT-028` and `AT-045` are still counted — they are
  named in this section and in the strike banners, which **D20 requires** them to be. `48` is
  therefore `47 + AT-048`, and it is **not** the batch's `AT` count. This is precisely why §5.2 now
  states the count as a three-way-intersection derivation rather than as a literal: the mechanical
  scanner and the requirement census answer **different questions**, and a document that lets one be
  read as the other is how `QA-B-03` happened. The QA lane's census in `01d-unpark-measurements.md`
  is the authority on the real figure.

---
**What amendment set 1 did NOT do — superseded by set 2 below.** Set 1 left `QA-B-01`, `QA-B-05`,
`QA-B-06`, `QA-B-10` and the majors `QA-M-01` through `QA-M-14` open. **All are closed in set 2.**
`C-1` and `C-2` are **discharged by execution** per D18 and A-02 / A-04; **`C-3` is discharged by
A-04 and A-05**; `C-4`, `C-5`, `C-7` and `C-8` are written into their increments by A-13 through
A-18.

---

## Amendment set 2 — the fold pass, 2026-08-27. Base unchanged at `d877784`.

> **Method, and it differs from set 1 in one way that matters.** Set 2 folds the QA measurement lane
> (`01d-unpark-measurements.md`) and the rulings sealed in `PDR-2026-08-26-ui-next-batch-02.md`.
> **Every number that becomes a normative threshold was re-executed here rather than cited** — C-43
> applies to a sibling lane's artifact exactly as it applies to a review. **That re-execution changed
> two of them (A-21, A-32)**, and those corrections are recorded rather than absorbed.
>
> **Three of the four measurements contradict the parked review's own prescribed remedy.** Where the
> review is wrong, this document does **not** implement what it asked for, and says so.

#### A-20 · `HLR-N06.3` takes THREE predicates, not the two the review prescribed *(`QA-B-01`)*

- **Before:** *"`declared_total == len(graph.nodes) - painted_node_count`, exact, over at least 4
  configurations"*, with `QA-B-01` prescribing a two-predicate replacement — return the painted set,
  then assert every declared id has a visible trace.
- **After:** `PRED-1` reconciliation · `PRED-2` `declared ⊆ traced` · `PRED-3` `traced ⊆ declared`.
  Together `PRED-2 ∧ PRED-3` is **set equality**, which is what the story promises.
- **Deleted tokens:** none. **New tokens:** `PRED-1`, `PRED-2`, `PRED-3`, mutants `MUT-1`, `MUT-3`.
- **The prescribed remedy is GREEN on the pure deletion — re-executed here on `legacy` at 40 x 12:**

  ```
  MUT-1 deletion: declared set = empty              P1=True  P2=True  P3=False
  MUT-3 weakening: declared omits ['cont','pres']   P1=True  P2=True  P3=False
  MUT-4 over-declare: adds off-canvas 'alm'         P1=True  P2=False P3=True
  ```

  `PRED-1` holds because `8 == 8 - 0`; `PRED-2` holds **vacuously** over an empty set. A renderer
  declaring nothing painted passes the batch's headline predicate — **the replacement oracle as
  specified would re-certify the very defect it was written to catch.** `PRED-3` costs nothing: the
  traced set is already computed for `PRED-2`.
- **Fixture named, seed map ruled out.** `legacy` reaches all four required configurations with the
  four `(w, h, folded)` triples pinned in the requirement. The seed map hides a node at **0 of 56**
  swept sizes and reaches 2 of 4; naming it would make `AT-015` unfalsifiable in its two most
  important arms.
- **Parent-HLR re-read:** US-N06 re-read in full. Its outcome is *"nothing is hidden without being
  declared"* — a **set** claim, not a count claim — so `PRED-3` restores the parent's own meaning
  rather than adding to it.

#### A-21 · The trace predicate is the CLIPPED-AND-VISIBLE image; a prefix is unsound at every length, and the natural reading of the fix is also wrong

- **Before (set 1):** *"the truncation-tolerant **prefix** … its first `k` display cells."*
- **After:** the `_clip` image at that width **restricted to the columns that fall inside the canvas
  width**.
- **Deleted tokens:** none. **New tokens:** none.
- **Prefixes fail on both sides, and the review's `>= 8` false-fails 69 times.** Re-executed over 31
  overflowing sizes, negative arm **129** unpainted node-observations: `L=1` gives **83** false
  positives; `L=2` gives 0/0; `L=3` through `L=5` give **12** false negatives; `L=8` gives **69**;
  `L=18` gives **77**. **A predicate whose only correct parameter is a single integer with failure on
  both sides is fixture-fitted, not an oracle.**
- **AND THE OBVIOUS READING OF THE REPLACEMENT IS ALSO WRONG — set 2's own correction.** The
  measurement lane names the predicate *"the renderer's own `_clip` image at that width"*. Read
  literally as `_clip(title, card_w - 3)`, re-executed here:

  ```
  P-A1  _clip(title, card_w-3)                    false-neg= 20  false-pos= 0
  P-A2  that image restricted to visible columns  false-neg=  0  false-pos= 0
  ```

  The 20 are nodes whose card is partly past the right edge: the full image is never painted, the
  node plainly is. **The horizontal restriction is part of the predicate, not an implementation
  detail** — writing it the short way reintroduces 20 false negatives into the batch's headline
  requirement. Recorded because the lane's own reference implementation does the right thing in code
  (`vis`) while its prose names the wrong thing, and an implementer follows prose.
- **Parent-HLR re-read:** `HLR-N06.3` re-read. `AT-015` / `AT-016` are `test (pilot)` and read the
  composited frame through `_rows_in`, **not** `render().plain`. The sweep pins the arithmetic, not
  the surface — stated in the requirement so the two are not confused.

#### A-22 · `LLR-N06.3.2`'s negative control exists and is normative *(`QA-B-05`)*

- **Before:** *"A deeper synthetic fixture … is therefore **owed at Phase 3** … without it the
  predicate is correct but unproven."*
- **After:** the `anidado` fixture is written into the LLR with its shape and both sums.
  **Inc-3 shall not open without it.**
- **Deleted tokens:** none. **New tokens:** the fixture name `anidado`.
- **Executed:** 7 nodes, depth 3, `FOLD = {ops, log}` with `log` nested inside folded `ops` —
  `naive_sum = 6`, `painted_sum = 4`, true hidden union **4**, double-counted `['alm','flo']`,
  inflation 2. Built through `MapStore.save` and reloaded through `MapStore.load`, so it exercises
  the real load path and needs no new fixture machinery.
- **The shipped fixture is PROVABLY unfalsifiable, upgrading the review's argument.** `02a` argued it
  structurally; executed exhaustively over **all 7 non-empty fold configurations** of `legacy`,
  **0** disagreements. Parked `M-6`'s three quoted rows reproduce as configurations 1, 5 and 7.
- **Declared residual:** the fold input has no handler today, so the transcript is set arithmetic
  over `(graph, folded)`. **`TC-032` re-runs it through the Pilot once Inc-3 ships fold.** §6.2 item
  1 is marked discharged and item 5 carries the residual — *"the arithmetic was proved"* is not
  *"the screen does it"*.
- **Parent-HLR re-read:** `HLR-N06.3` re-read; `LLR-N06.3.2`'s `painted_sum == |hidden union|` arm is
  what ties it to `LLR-N06.3.1`'s set-difference rule, and the fixture now demonstrates that tie
  rather than asserting it.

#### A-23 · `LLR-CNV.2.1` asserts the WRITTEN FILE, and the substring caveat carries its condition *(`QA-B-06`)*

- **Before:** *"file exists; size `> 0` bytes; the exported **text object's** braille count equals the
  on-screen text object's."*
- **After:** `disk_braille(path) == braille_count(on_screen_text.plain)`, scanning code points in the
  written bytes. `size > 0` is retained as a precondition and explicitly **not** the threshold.
- **Deleted tokens:** none. **New tokens:** mutants `M-CNV.2.1-a`, `M-CNV.2.1-b`.
- **Executed:** the real chain gives **0** braille on disk in a **19 679-byte** file — `size > 0`
  **passes on an artifact containing zero braille**; the positive control recovers **12 of 12**; the
  negative control gives 0 at 2 732 bytes and `size > 0` passes again. The in-memory equality asserts
  the producer against itself and never opens the file.
- **THE CAVEAT IS CONDITIONAL, AND THAT IS THE TRAP.** `QA-B-06` says a substring oracle *"returns
  False even for correct content"*. Measured: **True** under uniform styling (5 `<text>` spans);
  **False** under per-cell styling (16 spans, longest recoverable run **1 of 12**). Three of four
  real rendered titles are false negatives; `mapper` survives only because the header paints in one
  style. **An implementer who writes the positive control the easy way measures the uniform arm, sees
  `True`, and concludes the caveat was wrong** — so the requirement forbids validating a string
  read-back against a uniformly-styled fixture as well as requiring the code-point scan.
- **Parent-HLR re-read:** `HLR-CNV.2` re-read — it is the `PIN (radial)` after A-24, and
  `LLR-CNV.2.1` is the only requirement in the batch touching the **exported artifact**, a different
  sink with a different audience. That is why C-10's SVG coercion clause lands here (A-40) rather
  than in the on-screen thresholds.

#### A-24 · `HLR-CNV.2` is relabelled `PIN (radial)`; the containment set is derived and includes ASCII *(`QA-B-09`, superseding A-12)*

- **Before (set 1, A-12):** the title was renderer-neutral and the subject question was left open
  with a stated criterion.
- **After:** *"`PIN (radial)` · braille free-angle edges reach `RadialRenderer`'s painted output"*,
  with renderer, fixture and render size named in the statement.
- **Deleted tokens:** none. **New tokens:** `AT-007b` (the split, A-37), the label `PIN (radial)`.
- **A-12's criterion is answered, and the answer is structural.** Executed: `LayeredRenderer`
  measures **0 braille before and 0 after** on all three graphs; `grep -rn "\.dots\b" mapper/`
  returns **exactly two sites, both in `radial.py`**; `|cv.bits| = 0` for radial, so it never wires a
  box-drawing glyph. **No fix to `Canvas.rows()` can raise the map canvas above 0** — moving the
  subject would make the requirement unsatisfiable by the change under test, and would create a
  second definition of *"the canvas that draws free-angle edges"* against `D19`'s precedent.
- **The containment set fails in BOTH directions if hand-listed.** Measured on M-1 at 80 x 24: the
  **full derived set** (19 glyphs) is `⊆ POST_good` and **not** `⊆ POST_mutant` — it reddens; the
  **non-ASCII subset** (3 glyphs, `· ◆ ●`) is `⊆` both — **vacuous**; the **parked hand-list** (10
  glyphs) is `⊆` **neither** — it **false-fails the correct fix**. Independently confirmed here:
  `PARKED − PRE = ─ │ ┌ ┐ ┬ ┼ ▐`, seven `LayeredRenderer` glyphs radial never paints. **The glyphs
  the mutation destroys are ASCII letters**, so a non-ASCII set discriminates nothing.
- **`AT-007`'s empty arm was vacuous; one assertion fixes it.** `count == 0` on a single node passes
  today for **two independent reasons** — `|cv.dots| = 0` *and* `rows()` drops dots — so the arm
  cannot say which held, and after the fix it would change from passing wrongly to passing rightly
  with no observable difference. `AT-007b` asserts `len(cv.dots) == 0`.
- **Parent-HLR re-read:** `HLR-canvas` re-read in full; `HLR-CNV.1` is the unit-level `Canvas`
  requirement and `HLR-CNV.3` is the focus tone, so neither constrains `.2`'s subject. §6.2 gains
  item 4: **the map-canvas braille promise now belongs to no requirement in this batch** — a declared
  gap, per C-40's corollary that a pin must be labelled a pin.

#### A-25 · `S-15` is folded: the budget bounds WORK, `MAX_RENDER_NODES` is additional, and `02b`'s timings must not be quoted

- **Before (set 1, A-05):** the DAG measurements were presented as this lane's own finding.
- **After:** recorded as shipped defect **`S-15`** (`PLAN.md` §14.2), **independently reproduced
  twice** — this lane and the orchestrator's separately written probe, different graph builder and
  different call path, agreeing within 3 %.
- **Deleted tokens:** none. **New tokens:** `S-15`, risk `R-10`.
- **Three clauses the fold required, each now explicit in `HLR-N13.3`:** the bound is on **work**,
  not node count and not map count — a count bound is exactly what `M-H2` and `M-H3` both survive;
  **`MAX_RENDER_NODES` is not replaced or re-litigated** and the work bound is **additional**, stated
  in a sentence of its own because *"we added a bound"* read as *"we replaced the bound"* is how a
  second live definition of *"too big"* gets created; and **the 51-node shape is the acceptance
  fixture** while the 73-node shape is the demonstration, because a 70-second node has no place in a
  gate.
- **CORRECTION:** `02b`'s renderer timings (3.4 s at n=3280, 9.1 s at n=10 000) are **pre-repair**
  and are now ~60 ms. The conclusion survives; **the numbers must not be quoted** — doing so would
  understate the live defect while appearing to cite evidence.

#### A-26 · `QA-B-10` is discharged by FOLDING the five sealed rulings, not by re-ruling them

- **Before:** §6.1 carried `Q-3`, `Q-5`, `Q-7`, `Q-8`, `Q-9`, `Q-10` as **OPEN**, and `HLR-N07.3`
  read *"This requirement is written chord-agnostic; PDR settles the chord before Inc-4 starts."*
- **After:** every ruling is folded into the requirement that owns it, and every affected `AT` drives
  a **real key**.
- **Deleted tokens:** none. **New tokens:** `C-D6a`, `C-D6b`, `C-D9a`, `C-D9b`, `C-D9c`, mutants
  `M-N07.3-a`, `M-N07.3-b`, `M-N14.3.2-a`.

  | Ruling | Folded into | What it now says |
  |---|---|---|
  | `#D5b` (Q-3) | `HLR-N07.3` | three seat rows — `map/n -> next_hit` and `map/N -> prev_hit` in `nav`, `map/M -> next_gap` in `view`; DDR reviews them row-by-row; `keymap.py` is a four-way collision resolved by serial ordering |
  | `#D6` (Q-7) | `HLR-N07.3`, `LLR-N14.3.2` | `⇥` rejected; `n`/`N` walk the single active *coincidencias* set. **C-D6a** makes "only one result set is live" a tested Layer-0 invariant; **C-D6b** retains `LLR-N14.3.2` verbatim, re-run after Inc-4, Inc-6, Inc-9 |
  | `#D7` (Q-5) | §6.1 | ruled **out**, with the four things a later batch would need — a new `map_meta` table (not a column: there is no migration path), a backfill rule with *"provenance unknown"* as a distinct third state, a persist point in `RepoScreen`, and its own HLR and increment |
  | `#D8` (Q-8) | `LLR-N14.1.3` | a bare word is malformed **with a redirect**; `/` is free text, the lens is `key:value`. Otherwise the two features become one feature with two syntaxes and `C-D6a` becomes much harder to reason about |
  | `#D9` (Q-9) | `LLR-N16.1.2` | **migrate both**; declare-only fails its own `>= 3` threshold or duplicates bindings. **C-D9a** gates the `tab` drop behind a probe with a working positive control; **C-D9b** shrinks `UNMIGRATED_SCREENS` in the same increment; **C-D9c** leaves `factory.py:343` byte-identical |
  | `#D10` (Q-10) | `LLR-S06.3.2` | one disposition per site — promote `radial.py:18`'s grey to a token, assign the **busy** job to a new token and retone the progress site, register `factory.py:104` in Inc-1 and close it in Inc-9 |

- **`C-D9a` is carried with the PDR's own vacuity recorded, not banked as a green.** The PDR drove
  nine `tab` presses on `SettingsScreen` with and without the two bindings and got identical results
  — but `app.focused` was `None` throughout, so **the probe could not see a focus transition at all
  and therefore could not fail**. *"Should be behaviour-neutral"* is not evidence. If the control
  cannot be built, **the drop does not ship**.
- **A-10's flag is resolved, and resolved the OTHER way.** A-10 asked PDR to retire the `app.py:879`
  register entry or say why it stays, on the grounds that `LLR-S06.3.5`'s *"or in flight"* clause
  makes it classifiable. `#D10` had already answered: the site is **retoned**, not reclassified. A
  spinner is *busy*, not *outstanding*, and stretching `WARN` to cover it would re-create the
  two-jobs defect `QA-B-08` raised. **The busy job goes to a new token; `WARN` keeps its one job.**
- **One correction to the PDR, from re-execution:** the progress-`WARN` site is **`app.py:879`**, not
  `:848`. An address correction, **not** a new decision.
- **Parent-HLR re-read:** `HLR-N07.3`, `HLR-N14.1`, `HLR-N14.3` and `HLR-N16.1` all re-read in full
  before folding. **None needed its statement changed** — every ruling lands in a threshold, a
  condition or an acceptance line, which is the shape a ratification should have.

#### A-27 · `LLR-N07.2.1`'s threshold was weaker than its own statement *(`QA-M-01`)*

- **Before:** *"the two counts are equal, and the count is `> 0` in both states."*
- **After:** the query is pinned to **`carlos`**; counts equal; `> 0` in both states; **and at least
  one hit lies strictly inside the folded branch `fin` and is painted before the fold**.
- **Deleted tokens:** none. **New tokens:** mutant `M-N07.2.1-a`.
- **The gap was not theoretical:** `riesgo` — the batch's own working query — satisfies the parked
  threshold with `naive == correct` and is **vacuous**, because it matches nothing inside the folded
  branch, so folding cannot change the count under either implementation.
- **Parent-HLR re-read:** `HLR-N07.2` re-read; its statement is *"the count is taken over the whole
  graph"*, and the inside-the-branch clause is the only thing that makes the LLR test that.

#### A-28 · `LLR-N07.2.2` is split per `#D12`, and *"all six lose kwargs"* executes false

- **Before:** one LLR bundling the signature migration with the hit-painting capability; touched
  symbols at `layered.py:78`, `outline.py:17`, `radial.py:33`; *"All six lose `**kwargs`"*.
- **After:** `LLR-N07.2.2a` (Inc-2, output byte-identical) and `LLR-N07.2.2b` (Inc-5, paints
  `state.hits`). Addresses re-derived: `layered.py:131`, `outline.py:47`, `radial.py:107` — **three
  of six moved**; `lane.py:108`, `:171`, `:311` unchanged.
- **Deleted tokens:** `LLR-N07.2.2`. **New tokens:** `LLR-N07.2.2a`, `LLR-N07.2.2b`, `TC-077`.
- **Why the split is forced, not tidy:** **Inc-2's gate is byte-identical renderer output**, and
  painting hits destroys byte identity. One increment cannot hold both.
- **CORRECTION (`QA-N-03`):** executed, **5 of 6** declare `**kwargs`; `layered.py:131` takes an
  explicit `query: str = ""`. The reverse census greps this line, so the wrong figure would have made
  the census miss a file.
- **`AT-024` finally has an owner** — one of the five catalog-only ids, observing exactly the
  `**kwargs` swallow, now claimed on an `Acceptance:` line.

#### A-29 · The five catalog-only `AT` ids are dispositioned, not left as an unnamed third tier

- **Before:** the measurement lane found a tier the review's binary split obscured — of 47 declared
  ids, **39** had a requirement `Acceptance:` line, **5** existed only as a clause in a boundary
  catalog (`AT-002`, `AT-009`, `AT-024`, `AT-031`, `AT-040`), and **3** were fabricated.
- **After:** the three fabricated ids are deleted (A-07). Of the five: `AT-002` is **struck** with
  §3.1 (A-02); `AT-024` is **promoted** under `LLR-N07.2.2b` (A-28); `AT-009` is **promoted** under
  `LLR-CNV.2.1`, whose threshold A-23 rewrote; `AT-031` and `AT-040` remain catalog-only and are
  **recorded here as such** rather than counted as specified.
- **Deleted tokens:** none beyond A-07's. **New tokens:** none.
- **Why the tier matters:** *"a boundary-catalog clause is a coverage claim, not a predicate"* — it
  names no fixture, no size and no threshold. Reporting 44 as *"predicates"* overstates by five.
  §5.2's three-way intersection is written precisely so this tier stays visible.

#### A-30 · `LLR-N14.1.1`'s normative copy is complete, and its two line forms are reconciled *(`QA-M-14`)*

- **Before:** a block headed *"verbatim … the implementer copies it"* rendering
  `el mapa no define el campo «Z» · campos: …` — **a literal ellipsis to copy**.
- **After:** all four strings written in full, including
  `· campos: D acta · O origen · E estado · C criticidad`, plus the count-line form.
- **Deleted tokens:** none. **New tokens:** none.
- **The two forms are reconciled rather than left to collide:** the declared count-line form is
  `N nodos en M ramas`, and the zero-match line `0 nodos · ningún nodo tiene estado = inexistente` is
  deliberately **not** of that form — *"0 nodos en 0 ramas"* is true and says nothing about **why**.
  Recorded so an implementer does not normalise the difference away.
- **The `⇥ recorrer` fragment is superseded by `#D6`** and shall read the seat's own labels for
  `next_hit` / `prev_hit` rather than naming a chord in a literal.

#### A-31 · `LLR-S06.3.2`'s register size is derived from `#D10`'s dispositions, not fixed at 3

- **Before:** *"exactly 3 registered entries; 3 of 3 resolve."*
- **After:** **1** after Inc-1 (`factory.py:104` only), **0** after Inc-9 — because `radial.py:18` is
  promoted to a token and `app.py:879` is retoned.
- **Deleted tokens:** none. **New tokens:** none.
- **The parked threshold encoded the pre-ruling state and would have reddened Inc-1 for doing exactly
  what `#D10` requires.** `QA-N-05` is recorded as **verified** — all three sites confirmed on disk
  at draft and again here; the dispositions change what happens to them, not whether they exist.

#### A-32 · Floors on derived counts become set equality, and the derivation command is named *(`QA-M-03`, `QA-M-11`)*

- **Before:** `LLR-S06.3.1` *"derived file count `>= 30`"*; `LLR-S06.3.3` *"`>= 8`"*;
  `LLR-S06.3.4` *"`>= 29`"*.
- **After:** each asserts the **derived set itself**. The file list **equals** `git ls-files` over
  `mapper/` filtered to `*.py`.
- **Deleted tokens:** none. **New tokens:** none.
- **Executed:** `git ls-files` **33** · `Path('mapper').rglob('*.py')` **33** ·
  `glob.glob('mapper/*.py')` **16**. `git ls-files` is chosen over `rglob` because the two agree
  *today* and stop agreeing the moment an untracked or ignored `.py` lands under `mapper/`.
- **CORRECTION to `QA-M-11` — its number does not reproduce.** `02a` states the non-recursive `glob`
  yields **5** files; re-executed it yields **16**. The finding stands — the non-recursive form is a
  plausible weaker commit losing more than half the tree — but the number does not.
- **And the reason the floors go is subtler than "they fail".** `>= 30` **does** catch the 16-file
  glob. The problem is that catching it is an accident of the gap: a derivation losing **three**
  files sits comfortably above the floor and ships a census with holes. Asserting the set removes the
  dependence on how large the loss happens to be. `LLR-S06.3.4`'s parked **29** is separately
  superseded — re-executed, **36**, i.e. seven sites of slack.

#### A-33 · The ux lens's `shall` clauses reach a requirement *(`QA-M-05`, `QA-M-06`)*

- **Before:** `01b`'s **UX-Q3-a**, **UX-Q3-b**, **E1b** and **E1c** appeared in **no** requirement.
  §6.4 claimed *"seven of its findings changed §3"*; these four changed nothing.
- **After:** all four folded into `HLR-N07.3`'s threshold with their exact painted strings — the
  committed-vs-editing query chip; the hint line reading exactly
  `n siguiente · N anterior · esc limpiar`; and the two distinct toasts,
  `sin búsqueda activa` / `pulsa / para buscar` and
  `0 coincidencias` / `«nóm» no aparece en este mapa`.
- **Deleted tokens:** none. **New tokens:** `UX-Q3-a`, `UX-Q3-b`, `E1b`, `E1c`, mutant `M-N07.3-b`.
- **`E1b` and `E1c` are different facts** — *"you have not searched"* and *"you searched and there is
  nothing"*. `M-N07.3-b` (one toast for both) is green on any *"a toast appears"* test while telling
  an operator who never searched to go and look for a query they never typed.
- **The fold order mattered:** UX-Q3-b names `n` and `N`, which is only correct **after** `#D5b`.
  Folded before the ruling it would have named the wrong keys.

#### A-34 · `US-N06`'s empty cell claimed coverage it did not have *(`QA-M-07`)*

- **Before:** the ☑ **empty** cell was filled by *"a map that fits entirely on screen with nothing
  folded"*.
- **After:** two cases — **zero-hidden** (`AT-015` at `(50, 12, ())`) and **genuinely empty**, a
  **0-node** graph, which is `01b`'s **E3** and had no predicate anywhere.
- **Deleted tokens:** none. **New tokens:** none.
- **A zero-hidden case is not an empty case.** Executed, the 0-node case has a defined shipped
  behaviour to pin — `LayeredRenderer.render` returns `Text("(no map loaded)")` when
  `graph.root_id is None or not graph.nodes` — so this is a boundary the catalog **claimed and did
  not cover**, not new mechanism.

#### A-35 · `LLR-N14.3.2` gains the escape clause, and `#D6` empties its predicted-red set *(`QA-M-08`)*

- **Before:** *"distinct focus targets `== 9`; transitions `== 8`."*
- **After:** the same, **plus** `escape` from the query `Input` moves focus out of the box, with the
  hint line naming the route.
- **Deleted tokens:** none. **New tokens:** mutant `M-N14.3.2-a`.
- **The invariant could not see the failure it was written for.** `01b` DECISION 5 step 5 records the
  required mitigation that did not land — *"without that, `priority=True` on `tab` traps the operator
  in the input"* — and **being trapped preserves 9 targets and 8 transitions**. The traversal ring is
  intact; the operator simply cannot reach it. `C-40` limb 2 in its purest form.
- **`#D6` narrows the rest:** with `⇥` rejected the predicted-red set is **empty** — the three shipped
  `tab` guards stay green and `TAB_BINDING_EXCEPTIONS` gains nothing. The parked wording named them
  as predicted-red *if* `tab` was chosen; that branch is closed.

#### A-36 · `HLR-N16.2`'s floor is derived and its subject includes the screens the defect is on *(`QA-M-09`, `QA-M-10`)*

- **Before:** *"over at least 5 glyphs"*, *"declared glyph count `> 0`"*, and *"the title contains
  the view's name **for each of the three map views**"*.
- **After:** style equality over **every** declared glyph; the vocabulary asserted as a **set** equal
  to `01b` DECISION 3's enumeration; and the title checked for the three map views **and every
  non-map screen in `LLR-N16.1.1`'s derived set**.
- **Deleted tokens:** none. **New tokens:** mutant `M-N16.2-a`.
- **THE PARENTHETICAL THIS ROW CARRIED IS STRUCK BY AMENDMENT SET 3 (`P2-B3`, A-45 below).** A-36
  restated the vocabulary as a set — correctly — and then **transcribed a literal count into the
  same sentence**, which is the identical defect A-07 had already fixed for the `AT` total two
  amendments earlier. A set assertion whose membership is given by a hand-copied number is a
  hand-copied number. The literal is removed here and replaced by `LLR-N16.2.1`'s derivation, which
  carries its question, its instrument and its SHA. **The rest of A-36 stands unchanged** — the
  widened screen set was correct and is untouched.
- **A legend shipping ONE glyph passed both parked floors.** And the title threshold **excluded the
  subject of the change** — the defect is on `FactoryScreen`, `SettingsScreen` and the three other
  un-scoped routes, so the predicate could be fully green while every screen the story is about still
  painted the wrong title. `C-40` limb 1.

#### A-37 · Three `AT` ids that named two chains each are split *(`QA-M-12`, `QA-M-13`)*

- **Before:** `AT-025` claimed the thumbnail, the zero-documented map **and** a map whose load
  raises; `AT-007` was claimed by **both** `HLR-CNV.1` (unit, `Canvas`) and `HLR-CNV.2` (render
  chain, `RadialRenderer`); `AT-034` spanned `LLR-N14.1.1` and `LLR-N14.1.3`, two requirements with
  different validation methods.
- **After:** `AT-025` / `AT-025b`; `AT-007` / `AT-007b`; `AT-034` / `AT-034b`.
- **Deleted tokens:** none. **New tokens:** `AT-007b`, `AT-025b`, `AT-034b`.
- **One id cannot be two on-disk nodes.** The error path needs a different workspace and a poisoned
  file; the `Canvas` unit and the `RadialRenderer` render chain are different chains; and
  `LLR-N14.1.1` is `test (unit)` + `test (pilot)` while `LLR-N14.1.3` is `test (unit)`.
- **The parked error-cell justification is superseded:** *"matching the existing `except Exception`
  fallback at `app.py:551`"* — re-executed, that fallback is the recents loop's `else` arm at
  `app.py:566-567`, which produces the misdeclaring row `LLR-N13.1.5` **forbids**, not an outcome to
  match.

#### A-38 · `LLR-N14.1.4` is written: the predicate, the case rule and the bounds *(C-6)*

- **Before:** absent. The lens predicate — exact vs substring vs prefix vs case-folded — was
  **nowhere stated**, and `LLR-N14.1.2`'s thresholds were satisfied by either reading.
- **After:** equality under Unicode simple case folding, no substring matching, with declared
  term-count and query-length bounds.
- **Deleted tokens:** none. **New tokens:** `LLR-N14.1.4`, `TC-078`, mutants `M-Q1`, `M-Q2`, `M-Q3`,
  `M-Q4`.
- **The good news first, because it bounds the exposure:** `02b` searched all 2 707 parked lines for
  `re.`, `regex`, `fnmatch`, `eval(`, `compile(` — **zero occurrences**. There is no regex path and
  no eval-shaped path in the specified design, so catastrophic backtracking and code execution are
  out of scope **by construction**.
- **THE SUBSTRATE `D6` PROMOTES TO SOLE OWNER IS ITSELF WRONG — re-executed here.**
  `search_hits('')` and `search_hits(' ')` each return **every node**, because `model.py`'s
  `if q in hay` makes the empty string a substring of every haystack. `AT-023` fixes this for the
  **lens** and leaves `search_hits` — the thing `HLR-N07.2`'s trustworthy count is taken from —
  unfixed. This LLR's empty/whitespace arm binds **both** owners, or the batch ships one owner with
  two behaviours.
- **Cost is not the exposure:** measured **0.3 ms** at n=500, **1.3 ms** at n=2000, **6.5 ms** at
  n=10 000, **1.1 ms** over a 1 MB title. The bounds exist so `LLR-N14.1.3`'s *"declared rule"* has
  something to declare, not to buy time back.
- **Parent-HLR re-read:** `HLR-N14.1` re-read in full; its three declared outcome classes are exactly
  what equality preserves and substring blurs, which is why equality is chosen and why the choice is
  stated rather than left to the implementer.

#### A-39 · `LLR-CNV.1.4` is written: the layer tone is a declared token with a fallback *(C-9)*

- **Before:** `LLR-CNV.1`'s only threshold on the value was *"the background cell's style names the
  written tone"* — an assertion of **pass-through**, the opposite of a guard.
- **After:** the layer value is a token from the declared set, and `rows()` paints an unknown tone in
  a declared fallback.
- **Deleted tokens:** none. **New tokens:** `LLR-CNV.1.4`, `TC-079`, mutant `M-V1`.
- **The sink fails open, silently.** 14 malformed style strings through `Text.append` and through the
  real `Canvas.rows()`: **all 14 render OK, none raises**, while `Style.parse('not-a-colour')`
  **does** raise — Rich swallows it via `get_style(..., default="")`. A malformed tone paints
  unstyled, indistinguishable from a tone never applied.
- **`M-V1` — validate at write time — survives**, because it misses `radial.py`'s direct
  `cv.dots[...] = hue` assignment, which bypasses any setter. **Validation lives in `rows()`**, where
  all four layers converge. Closes the other half of `Q-10` without inventing a second vocabulary.

#### A-40 · `C-10`, `C-11`, `C-12` and `S-11` folded into the requirements that own them

- **C-10 (S-12) into `LLR-CNV.2.1`:** the exported SVG shall contain no code point in
  `COERCION_RANGES`. **An SVG leaves the machine; the terminal's own escaping does not travel with
  it.** `save_svg` is a declared §4 `SINK` on `canvas_rows`'s **transitive observer** line
  (~~consumer list~~ — corrected by `P2-C1`, A-51), trigger **B4** fired on
  it, and **nobody asked what text it writes**.
- **C-11 (S-13) into `LLR-N13.1.6`:** `MapStore.list_maps` shall expose a **cached** metrics read.
  Executed context: warm is faster only because the text hash matches and `_reindex` short-circuits —
  **the first mount after any edit pays full price**, so a warm measurement is not evidence the mount
  is cheap.
- **S-11 into `LLR-STO.1.1`:** B-01's family is **five** exception types, not one `KeyError` —
  `KeyError`, two `AttributeError`s, two `sqlite3.ProgrammingError`s — and `except MapStoreError`
  callers catch none of them. That is exactly the path `LLR-N13.1.5` depends on. **`M-B1`** (add a
  `.get("path","")` default) survives the first arm and leaves four.
- **C-12 (S-14) into `LLR-N13.1.6`:** `F-m4` is dispositioned **measured-and-closed** — PyYAML
  aliases share objects rather than deep-copying, peak heap **0.0 MB**, and `_graph_from_sidecar`
  reads only three keys so a bomb elsewhere is never traversed. **Carried arm:** a bomb under
  `nodes:`, which *is* traversed, belongs in `LLR-STO.1.1`'s fixture set. *"No disposition"* is what
  turns a measured non-issue into a recurring review cost.

#### A-41 · Minors folded, and one that no longer has a subject

- **`QA-N-04` into `HLR-N06.3`'s rationale.** *"121 nodes hidden (94 %)"* over-stated: the metric
  counted **full-title traces**, so truncated-but-drawn nodes were counted as hidden — the very error
  the Painted-trace oracle removes. Restated as *"121 of 129 had no full-title trace"*.
- **`QA-N-06` into `HLR-N06.3`'s verification.** The canvas header **wraps**: at 100 x 30 the count
  numeral and the word `nodos` land on different rows, so a per-row regex misses the numeral or binds
  it to the wrong label. The oracle joins region-clipped rows before parsing.
- **`QA-N-07` into `LLR-N06.2.1`.** *"0 remaining references"* named no reference, so nobody could
  check the census found them all. Enumerated: `OutlineRail.toggle` has **2** call sites, both in
  `tests/test_rail.py` (`:73`, `:77`), both predicted red.
- **`QA-N-11` into `LLR-N06.2.1`.** `mapper/search.py` confirmed **dead** — 0 imports across
  `mapper/` and `tests/` — so every `search` LLR is **new-module work** in the ledger, not
  modification.
- **`QA-N-05` into `LLR-S06.3.2`.** Recorded as **verified**, not as a defect.
- **`QA-N-09` HAS NO SUBJECT ANY MORE.** It corrected *"54 rows … short by 20"* to *"69 rows, short
  by 35"*. That sentence lived inside the S-8 paragraph **struck by A-03** (D17), so there is nothing
  left to correct. Recorded rather than silently dropped, so a reader tracking the minor does not
  hunt for a fix that is not there.
- **`QA-N-02` and `QA-N-10` are NOT this document's to fix.** Both target `PLAN.md` figures — the
  contaminated `painted=17` / `MISSING=10`, and two different `tab` measurements quoted adjacently.
  Checked: **neither figure is quoted anywhere in `01-requirements.md`**, so there is nothing to
  correct here. They stay against `PLAN.md`, whose lane owns them (C-44 — found, reported, not swept
  up).

---

**What amendment set 2 did NOT do.** `QA-N-01` (a `PLAN.md` §P-19 figure) is not this document's.
The **`AT` census figure itself** is deliberately still a derivation rather than a literal — set 2
added `AT-007b`, `AT-025b`, `AT-034b` and `AT-048`, struck `AT-001` and `AT-002`, and deleted
`AT-027`, `AT-028` and `AT-045`, so any transcribed total would already be the fourth wrong number in
this batch's history. **No requirement was added outside batch scope**: recorrido/guía,
cronoscopio/relieve, the repo-screen redesign and the blueprint language remain out, and `#D7` puts
`◍` out with them.

---

## Amendment set 3 — the third PDR fold, PASS 1. 2026-08-27. Base `20f86de` (`master`, tree clean).

> **METHOD, AND IT DIFFERS FROM SETS 1 AND 2 IN THE ONE WAY THAT CAUSED THE REJECTION.**
>
> **The instrument is `02g-lens-reconciliation.md`'s union ledger, item by item — NOT an amendment
> table.** `RIDER-1`, carried out of `2026-08-27-repair-batch-02`, is explicit: audit the fold
> against the **lenses' own condition lists**, never the amendment table, because *"that instrument
> dropped conditions twice."* This set is written to be **audited against `02g` §4 and §5**, not to
> certify itself. §6.5's own Before/After · Deleted/New convention is retained as the *container*;
> the **ledger below is the check**, and a container is not a check.
>
> **Two consequences follow, and both are deliberate.**
> 1. **Every `02g` item this pass touched has a ledger row, and every item it did NOT close has a
>    row saying so and why.** An item with no row is a defect in this amendment, not a silence.
> 2. **This is PASS 1 of the set, and it says so.** Pass 1 takes the operator's re-scope, the six
>    architect blockers, and the two shipped defects. Pass 2 takes the remainder. **The set is not
>    claimed closed** — claiming closure on a subset is precisely `C-43` at the batch level, which
>    `02g` §7 raised against the previous briefing.
>
> **Base moved `d877784` → `20f86de`.** `01-requirements.md` had not been edited since the lenses
> wrote their verdicts (`02g` §0, one commit), so every requirement-side line citation in
> `02c`/`02d`/`02e`/`02f` still resolved when this pass began. Code-side claims re-executed here are
> stated at `20f86de`.
>
> **New decisions this set records:** `#D23` (US-N14 deferred whole), `#D24` (the render work budget
> deferred, paired with `S-19`). Both are **operator re-scope rulings**, recorded here because they
> change what this document specifies; the PDR lane owns sealing them.

#### A-42 · US-N14 «lente» is DEFERRED whole to a follow-on design batch *(`#D23`, operator re-scope)*

- **Before:** §3.7 was live work in `#D5`'s `Inc-6`, carrying 3 HLR, 10 LLR, 10 `AT` and 13 `TC`.
- **After:** §3.7 carries a `DEFERRED — follow-on design batch` banner; **every heading in it carries
  `— DEFERRED (#D23)`**; §2.6 S-4 carries a deferral note with its intake retained; §5.2's US-N14
  behavioral row and all thirteen US-N14 functional rows are struck in place.
- **Deleted tokens: NONE. Nothing is deleted — the text is retained whole and the follow-on batch
  inherits it.** Deferred tokens, enumerated (C-56): `HLR-N14.1`, `HLR-N14.2`, `HLR-N14.3`;
  `LLR-N14.1.1`, `LLR-N14.1.2`, `LLR-N14.1.3`, `LLR-N14.1.4`, `LLR-N14.2.1`, `LLR-N14.2.2`,
  `LLR-N14.2.3`, `LLR-N14.3.1`, `LLR-N14.3.2`, `LLR-N14.3.3`; `AT-032`, `AT-033`, `AT-034`,
  `AT-034b`, `AT-035`, `AT-036`, `AT-037`, `AT-038`, `AT-039`, `AT-040`; `TC-051`, `TC-052`,
  `TC-053`, `TC-054`, `TC-055`, `TC-056`, `TC-057`, `TC-058`, `TC-059`, `TC-060`, `TC-061`,
  `TC-062`, `TC-078`. **New tokens:** the marker `#D23`.
- **`DEFERRED` is written into HEADINGS, not into a banner.** §5.2's count derivations now disqualify
  on `SUPERSEDED` **or** `DEFERRED`, and both are heading-level so a heading grep answers the
  question. A banner paragraph is not machine-readable; that is the whole reason for the choice.
- **Where the deferred ids went, said rather than implied.** `AT-034b` and `AT-040` are two of
  `QA2-C-01`'s **six** three-way failures. They are dispositioned **by leaving with the story**, and
  that disposition is written at three sites — §3.7's deferral block, §5.2's `AT`-movement list, and
  the ledger row below. **A cut that quietly absorbs an open condition is the exact failure `02g`
  exists to detect**, so the absorption is named in every place a reader might check.
- **Parent-story re-read:** US-N06, US-N07 and US-N16 re-read for dependencies on US-N14.
  **Three found, all handled:** `HLR-CNV.1`'s priority cited *"Inc-5's figure-ground"* (corrected —
  the live consumer is hit painting); `LLR-N16.2.1`'s ordering constraint cited what `Inc-5` paints
  (corrected, and it still holds); `keymap.py`'s collision was four-way and is now three-way.
  **`LLR-N07.2.2b` does NOT leave** — it is US-N07's, not US-N14's, and it keeps `AT-024`.

#### A-43 · The render work budget is DEFERRED, PAIRED WITH `S-19` *(`#D24`, operator re-scope)*

- **Before:** `HLR-N13.3` stated a mount budget and a per-map work budget, with thresholds 1
  (`< 1000 ms` for 200 maps) and 2 (`WORKSPACE_CARD_BUDGET_MS = 250`), four named mutants reddened by
  threshold 2, `AT-048`, and two figures flagged `assumed`.
- **After:** thresholds 1 and 2 struck `DEFERRED (#D24)`; the Statement reduced to the containment
  half; threshold 4 re-scoped from *"exceeds the per-map budget"* to *"fails to load"*; thresholds 3
  and 4 retained as the half testable **without** the budget mechanism; the `-k` selector renamed off
  `mount_budget`.
- **Deleted tokens:** none. **Deferred tokens:** `AT-048`, `TC-076`'s budget arm, mutants `M-H2`,
  `M-H3`, `M-H5`. **New tokens:** the marker `#D24`.
- **THE PAIRING IS THE RULING, AND `S-19` IS `S-18`'S PRECONDITION — NOT ITS SIBLING.** Measured on
  the 51-node / 410-edge shape: Layered **1283 ms**, Outline **337 ms**, **Radial 142 ms — under the
  250 ms budget**. So `k = 0` on Radial, threshold 4's containment quantifies over an empty set, and
  **threshold 2 cannot distinguish a correct implementation from a missing one**. The fixture as
  written never says which renderer it runs. **The follow-on batch's fixture SHALL name its
  renderer** and carry one for which `k > 0`, keeping the `k = 0` renderer as the negative control.
- **`P2-C8` is DISPOSED, not answered.** Its subject — threshold 1's un-headroomed wall-clock
  assertion — leaves with the mechanism. After this amendment `HLR-N13.3` carries **no `assumed`
  figure at all**.
- **Security `C-3` is DISPOSED on the same ground** — its subject is threshold 2. **And the limit of
  that disposal is stated in the requirement itself:** the *defect* `S-15` / `M-H3` is real, measured
  twice, and **stays on `master`** — 73 nodes cost 72.5 s and `MAX_RENDER_NODES` waves it through.
  **Deferring a bound does not repair a defect.** `M-H3` is carried **named** into the follow-on
  batch precisely so it is not rediscovered.
- **Parent-story re-read:** US-N13 re-read in full. Its outcome — *"home shows each map's own
  shape"* — survives the budget deferral intact; the budget was a bound on **how the screen is
  reached**, not on what it shows. `LLR-N13.1.5` and `LLR-N13.1.6` are untouched and still owned.

#### A-44 · Every live `AT` reaches all three legs of §5.2's intersection *(`P2-B2`, `QA2-C-01`)*

- **Before:** re-derived, **3 unowned** ids (`AT-009`, `AT-031`, `AT-040`) and **6** failing the
  three-way rule (`AT-009`, `AT-031`, `AT-034b`, `AT-040`, `AT-046`, `AT-047`).
- **After, each disposed individually:**

  | id | The missing leg | Disposition | Landed at |
  |---|---|---|---|
  | `AT-009` | no `Acceptance:` line | **owner written** — `LLR-CNV.2.1` | `LLR-CNV.2.1` `Acceptance:` |
  | `AT-031` | no `Acceptance:` line | **owner written** — `LLR-N13.2.1` | `LLR-N13.2.1` `Acceptance:` |
  | `AT-040` | no `Acceptance:` line | **leaves with US-N14** (`#D23`) | §3.7 deferral block |
  | `AT-034b` | not on the story list | **leaves with US-N14** (`#D23`) | §3.7 deferral block |
  | `AT-046` | not on the story list | **story list amended** | US-N06 Acceptance block |
  | `AT-047` | not on the story list | **story list amended** | US-N06 Acceptance block |

- **Deleted tokens:** none. **New tokens:** none — **every id already existed; what was missing was a
  leg, not an id.** That is why none of the six is struck: each has a real predicate.
- **THE `AT-009` CASE IS THE ONE WORTH READING TWICE.** §6.5 A-29 recorded that `AT-009` *"is
  **promoted** under `LLR-CNV.2.1`"* — and **the `Acceptance:` line was never written**, so the id
  stayed catalog-only through two further PDR passes while an amendment said it had moved.
  **A promotion recorded in an amendment and not written into the requirement is not a promotion.**
  This is the amendment-table failure mode in its purest form, found on the amendment table's own
  output, and it is the strongest available argument for `RIDER-1`'s instrument rule.
- **`AT-031` was honestly recorded and still wrong.** A-29 dispositioned it as *"remains catalog-only
  and is recorded here as such rather than counted as specified"*. Honest — and it left a live `AT`
  on a live story with no requirement above it, while §3.6's boundary catalog described `LLR-N13.2.1`'s
  statement word for word. **Recording a gap is not closing it.**
- **Parent-HLR re-read:** `HLR-CNV.2`, `HLR-N13.1`/`HLR-N13.2` and `HLR-N06.2` all re-read before
  each claim. **None needed its statement changed** — every claim lands on an `Acceptance:` line or a
  story list, which is the shape an ownership fix should have.

#### A-45 · The legend census becomes a derivation; the literal is removed, not corrected *(`P2-B3`)*

- **Before:** `LLR-N16.2.1` asserted set equality against *"21 rows `V1` through `V21`, plus 5 colour
  rows"*; `HLR-N16.2` repeated the literal; §6.5 A-36 transcribed it a third time.
- **After:** a derivation carrying its **QUESTION**, its **INSTRUMENT** and its **measured-at SHA**,
  over the **set of distinct `(glyph, label, style)` triples** in `01b` DECISION 3 §3.1–§3.4, minus
  every triple carrying a `DEFERRED(#D7)` marker. **No literal count is written anywhere.**
- **Deleted tokens:** none. **New tokens:** the marker `DEFERRED(#D7)` on `01b`'s `V18` row.
- **"CORRECT 21 TO 23" WOULD HAVE BEEN WRONG TWICE, WHICH IS WHY THE FIX IS STRUCTURAL:**
  1. the literal was already stale — DECISION 3 carries more labelled rows than its `V`-numbering
     suggests, because §3.1 adds rows beneath its own table;
  2. **`V4` and `V4a` are byte-identical in glyph, label and style** (`01b:277`, `01b:287`), so a
     row-id census double-counts what the legend paints once. The **triple** projection is the only
     one under which *what the legend paints* and *what the declaration says* are the same kind of
     object;
  3. **`#D7` removes `V18`** (`◍`), ruled *"not deferred, not ambiguous: out"* of this batch.
- **The `+ 5 colour rows` half IS CORRECT and is KEPT verbatim.** Executed at `20f86de`,
  `01b:325-329` carries exactly those five, and `01b:332-333` records why `ALERT` is absent.
  **Striking a correct clause alongside an incorrect one is how a fold loses work**, so it is
  retained explicitly rather than swept into the correction.
- **DISCHARGED at pass 2 — the cross-artifact edit was ROUTED, and it LANDED.** The stale literal was
  live at **four** sites. Three are in this file and were amended at pass 1. The fourth,
  `01b-ux-decisions.md:373`, belongs to the **ux lane**; pass 1 recorded it **open** and routed it
  rather than reaching across a lane boundary. The orchestrator applied it and it is now on disk.
- **THE ROW IS CLOSED BY RE-READING `01b`, NOT BY TRUSTING THE ROUTING (`C-44`).** Re-executed at
  pass 2: the line now derives the count from `LLR-N16.2.1` and writes no literal, and it carries a
  `⚠` note recording *why the obvious repair was wrong twice over* — the table holds **23** labels,
  `V4` and `V4a` are byte-identical in glyph, label and style, so striking the duplicate yields
  **22**. A `grep` for the old literal over `01b` now returns exactly one hit, inside that note,
  quoting what the line **previously** said. **A quoted historical value is not a live literal**, and
  the distinction is checked rather than assumed. The two artifacts no longer disagree.
- **Parent-HLR re-read:** `HLR-N16.2` re-read in full. Its statement is about **style equality per
  glyph**, which is unchanged; only the membership predicate moves from a literal to a derivation.

#### A-46 · The predicted-red set is DERIVED, and the supersession census covers both trees *(`P2-B4`)*

- **Before:** `LLR-N06.2.1` read *"**0** remaining references"*, amended by A-41 to an **enumeration
  of 2** call sites, both in `tests/test_rail.py`. No artifact in the batch named any digest pin.
- **After:** `LLR-N06.2.1`'s threshold is a **derivation** over `mapper/` **and** `tests/`, asserting
  its input set non-empty before evaluating it; and **both** `LLR-N06.2.1` and `HLR-CNV.1` carry a
  **predicted-red clause** naming its digest dictionary by derivation, with the re-capture rule.
- **Deleted tokens:** none. **New tokens:** none.
- **THE ENUMERATION WAS THE SAME DEFECT WITH A NUMBER ATTACHED.** A-41 answered *"a zero that names
  no reference"* with an enumeration that is a **strict subset** of the real set, and two of its
  misses are the two that matter: **a PRODUCTION site, `mapper/app.py:1259`**, and
  **`tests/test_repair_depth.py:1055` — the rail byte-identity guard itself**, parametrized over
  five fold configurations. `C-18` fires on the amendment: a premise counted at one file scope is
  under-counted tree-wide.
- **The pins, derived rather than transcribed:** `MASTER_LEGACY_DIGESTS`
  (`tests/test_repair_depth.py:93`, asserted `:815`), `MASTER_RAIL_DIGESTS` (`:113`, asserted `:1056`
  and `:1071`), `MASTER_FACTORY_TREE_DIGEST` (`:121`, asserted `:1077`). **Trigger B3 is FIRED, so
  `C-24` applies** and the set is named before the gate rather than met at it.
- **`RadialRenderer` is pinned at every `GOLDEN_SIZES` entry, so `Inc-1` reddens four keys BY
  CONSTRUCTION — an expected RE-BASELINE, not a regression.** Every `LayeredRenderer` and
  `OutlineRenderer` key is predicted **green** (`LayeredRenderer` dots `= 0`; `OutlineRenderer`
  builds no `Canvas`). **Re-capturing a predicted-green digest is a GATE FAILURE**, and each
  predicted-red re-capture is one at a time with its own recorded reason — otherwise the repair
  batch's `C-53` false-failure arm becomes a rubber stamp.
- **`MASTER_RAIL_DIGESTS` IS NAMED IN NO ARTIFACT OF THIS BATCH** — not here before this amendment,
  not in `PLAN.md`, not in the PDR. Recorded loudly: a shipped guard that no requirement names is a
  guard an implementer meets for the first time as a red test, at the gate, with no ruling in hand.
  It is parametrized on `collapsed` — **the attribute `LLR-N06.2.1` deletes**.
- **Parent-HLR re-read:** `HLR-N06.2` and `HLR-canvas` re-read. **Neither statement changed** — both
  amendments land in thresholds and in a new predicted-red clause.

#### A-47 · §3.0 is promoted to `HLR-COERCE` and gains two LLRs and an owner *(`P2-B5`, `#D21` edits a-1, a-4)*

- **Before:** §3.0 declared `COERCION_RANGES` and the `_CONTROL_MAP` widening in **normative
  language** — *"shall be declared once"*, *"shall be widened"* — with **no id, no `Acceptance:`, no
  `Touched symbols:`, no validation method, no `TC` and no increment**, while four LLRs in four
  increments asserted against it. `grep -rn COERCION_RANGES mapper/` returns nothing.
- **After:** `#### HLR-COERCE` with a full requirement block; `##### LLR-COERCE.1` (the declaration
  and the map widening); `##### LLR-COERCE.2` (the ordering clause, scoped to
  `mapper/views/layered.py::_fit`); owning increments assigned — `LLR-COERCE.1` → `Inc-1`,
  `LLR-COERCE.2` → `Inc-3`, `LLR-N06.2.5` → `Inc-9` (§5.4).
- **Deleted tokens:** none. **New tokens:** `HLR-COERCE`, `LLR-COERCE.1`, `LLR-COERCE.2`, `TC-080`,
  `TC-081`, mutants `M-COERCE.1-a`, `M-COERCE.1-b`, `M-COERCE.2-a`.
- **`HLR-COERCE` HAS NO PARENT STORY, AND THAT IS A RULING RATHER THAN AN OVERSIGHT** (`#D21`). It is
  a product-wide control whose subject survives the descoping of every story in the batch — which
  `#D23` has now **demonstrated rather than asserted**: `LLR-N14.2.3` left with US-N14 and the class
  did not move. Stated in the requirement so a later reader does not "fix" it by re-parenting.
- **It owns no `AT`, also by ruling.** The batch's coercion `AT` ids stay on their **surface-specific**
  LLRs, where the observable outcome is a painted row on a named screen. An `AT` here would observe
  *"text was coerced"* with no surface — a white-box claim in an acceptance test's clothes.
- **Why `Inc-1` and `Inc-3` and not one increment:** `darkside.py` is already in `Inc-1`'s declared
  set for the S-6 tokens; `views/layered.py` is **not**, and `Inc-3` owns it and is the increment
  that first asserts against the list. **Splitting by file ownership rather than by topic is what
  keeps both increments at budget.**
- **Parent-HLR re-read:** not applicable — this amendment *creates* the parent. The four asserting
  LLRs (`LLR-N06.2.3`, `LLR-N13.2.1`, `LLR-N16.2.3`, and the deferred `LLR-N14.2.3`) were each
  re-read: **none needs its statement changed**, because each already references §3.0's list, and
  §3.0 now has an id behind it.

#### A-48 · `LLR-N06.2.5` is re-parented to `HLR-COERCE` *(`P2-B6`, `#D21` edits a-2, a-3)*

- **Before:** `- **Traceability:** HLR-N06.2, risk A-7, security condition **C-8**` — parenting a
  product-wide class to a story about fold declaration; A-18 recorded this as *"a known imperfection
  … a smell, and the alternative — inventing an HLR for it — would have been worse."*
- **After:** `- **Traceability:** HLR-COERCE (§3.0), risk A-7, security condition **C-8**`, owning
  increment **`Inc-9`**; A-18's *"would have been worse"* sentence struck and replaced with the
  executed reason it was not; the two-limb criterion written into the document.
- **Deleted tokens:** none. **New tokens:** none.
- **IT IS AN UNDECLARED SOURCE-BUDGET BREACH, NOT A STYLISTIC SMELL — both limbs executed.**
  **Limb 1:** descope US-N06 and every census site survives — 11 in `mapper/app.py` on paths
  unrelated to the canvas, 4 in `mapper/screens/factory.py`, a screen US-N06 never touches.
  **Limb 2:** `HLR-N06.2` → US-N06 → `Inc-3`, at **4 of 4** files; satisfying the child requires
  `screens/factory.py` — a **fifth, undeclared** file and a collision with `Inc-9`, which owns it.
  Validator rule `V9` exists to catch exactly that. **`#D21` REMOVES a breach rather than creating
  one**, and `Inc-9` absorbs the census at **zero** added files.
- **The criterion discriminates — control executed.** `LLR-N06.2.3`, same parent: descope US-N06 and
  there is no fold pill (limb 1 passes); its symbols are inside `Inc-3`'s set (limb 2 passes).
  **Correctly parented, and it stays.** A criterion that moved both would be a verdict.
- **OPEN — one clause of edit a-2 is deliberately NOT performed in pass 1.** Edit a-2 also asks that
  the block be **physically moved** out of §3.4 into §3.0. **It is not moved**, and the id is
  deliberately **not** renumbered to an `LLR-COERCE.*` form. Reasons, stated rather than assumed:
  `LLR-N06.2.5` is cited by §5.2 (`TC-073`), by `02c` and by `PLAN.md`, **none of which this lane may
  edit**, so a renumber would trade an intra-document inconsistency for a cross-artifact one; and
  relocating ~60 lines of a 5 000-line document, in a fold whose two predecessors dropped conditions,
  is risk with no requirement-side payoff. **The substance of the ruling — parent, increment,
  ownership — is fully applied.** Recorded as an **open** ledger line for pass 2 to close or ratify.
- **Parent-HLR re-read:** `HLR-N06.2` re-read in full. **Its statement does not change** — it loses a
  child it never governed. `LLR-N06.2.2`'s cross-reference *"Its coercion is governed by
  `LLR-N06.2.5`"* **stays**, and is now a cross-section reference. That is correct and it is the
  point: the fold toast is governed by the class, and **the class is not owned by the toast**.

#### A-49 · The increment cut is stated ONCE, in §5.4, with `#D5` as its sole authority *(`P2-B1`, `QA2-C-06`)*

- **Before:** **two cuts live simultaneously.** §3.6's header said `Inc-6` (the stale ARQ 7-cut) while
  the ratified cut puts US-N13 at `Inc-7`; §3.8's header said `Inc-7` while the ratified cut splits
  US-N16 across `Inc-8` and `Inc-9`; `Inc-9` appeared throughout — an id that exists only in the
  9-cut. **The document never stated a cut at all**, only referenced one, so each reference drifted
  independently. That is the root cause, and §5.4 is the fix.
- **After:** **§5.4 states the cut once.** `#D5` is named as its **sole authority**; §5.4 is `#D5`
  re-derived for the operator's re-scope and does not compete with it. Both story headers are
  restated with their old numbers struck and the correction explained. **A second cut appearing
  anywhere in this document is now a defect, not a variant.**
- **Deleted tokens:** none. **New tokens:** `Inc-REPAIR`; the vacated marker on `Inc-6`.
- **`Inc-6` IS VACATED, NOT RENUMBERED — and the reason is executed, not aesthetic.** Renumbering
  `Inc-7`–`Inc-9` down by one would move three ids that `PLAN.md`, `02c`, `02d` and `03-increments/`
  already carry — **four artifacts this lane may not edit**. It would create a cross-artifact
  contradiction to remove an intra-document one. Reusing `Inc-6` for the repair increment would give
  one id two meanings across the batch's history — the two-definitions defect `#D6` removed for
  *"hit"*.
- **The repair increment is `Inc-REPAIR`, not `Inc-10`, and not `Inc-6r`.** Both numeric forms
  collide under a substring scan: `grep "Inc-1"` matches `Inc-10`, and a suffixed `Inc-6r` matches
  `Inc-6`. **This document is corpus an id-scanner reads**, so an id that cannot be a prefix or a
  suffix of another increment id is the only safe choice.
- **Body references restated against §5.4 — the brief named five; SIX were found and all six are
  fixed.** The five: the `#D6` seat-ruling row (`Inc-5` → the lens half deferred, and the `keymap.py`
  collision corrected from four-way to three-way); `HLR-N13.3`'s priority (`Inc-6` → `Inc-7`);
  `LLR-N16.2.1`'s ordering constraint (`Inc-7 last` → `Inc-8`, and the claim *"last"* was also
  false); `LLR-N16.2.3`'s mutant (`Inc-7` → `Inc-8`); risk `R-8`'s gate (`Inc-7` → `Inc-9`). **The
  sixth, found here and not in the brief:** §2.8.4's Q-7 disposition, *"a blocking question for
  Inc-5"*, where `Inc-5` meant US-N14's increment and now means hit painting — corrected, with Q-7
  recorded as travelling to the follow-on batch. A seventh, `HLR-CNV.1`'s *"Inc-5's figure-ground"*,
  is corrected under A-42.
- **Three references are LEFT AS THEY STAND, deliberately, and are named so they are not read as
  missed:** the `Inc-5` / `Inc-6` mentions inside `LLR-N14.1.3` and `LLR-N14.3.2` sit **inside
  headings already marked `DEFERRED (#D23)`** and travel with them; and §6.5 A-26's `#D6` row is a
  **historical record of a sealed ruling**, which is not restated because amending a record of what
  was decided would falsify the record.

#### A-50 · Two shipped defects get requirement stubs and an owning increment *(`B-29`, `B-30`; `02g` §5 `S-22`, `S-23`)*

- **Before:** both were `02g` §5 findings — *"newly raised, not in ANY prior ledger"* — with no
  requirement, no `AT`, no `TC` and no increment.
- **After:** §3.9 carries a first-class Acceptance block, `HLR-REPAIR.1`, `LLR-REPAIR.1` (`B-29`) and
  `LLR-REPAIR.2` (`B-30`), owned by **`Inc-REPAIR`** (§5.4), sequenced **before `Inc-7`**.
- **Deleted tokens:** none. **New tokens:** `HLR-REPAIR.1`, `LLR-REPAIR.1`, `LLR-REPAIR.2`,
  `AT-049`, `AT-050`, `TC-082`, `TC-083`, mutants `M-REPAIR.1-a`, `M-REPAIR.1-b`, `M-REPAIR.2-a`.
- **`B-29` IS INSIDE THIS BATCH'S FENCE, NOT ADJACENT TO IT.** Measured: a phantom sidecar id gives
  `coverage() = (2, 3)` with `warnings = []`, so `load_or_notice`'s warning arm (`mapper/app.py:459`)
  never fires and **`LLR-N13.1.5`'s containment NEVER ENGAGES**. US-N13 paints that bar. Shipping
  `Inc-7` without `Inc-REPAIR` ships a green containment test over a structurally empty set — which
  is why the ordering is declared hard in §5.4.
- **THE FIX IS THE WARNING, NOT `coverage()`.** Three call sites agree on `coverage()`'s current
  meaning and `LLR-N13.1.3` pins one at 100. **The defect is silence, not arithmetic**, and a
  repair that "corrected" the denominator would be a behaviour change riding inside a defect fix.
- **THE SYNTHETIC FIXTURE IS MANDATED, BECAUSE THE GUARD IS A NO-OP ON THE CURRENT TREE (`C-55`
  limb 2).** No fixture in the repository carries a phantom sidecar id, so the guard, `AT-025b` and
  `LLR-N13.1.5`'s containment are **all green over an empty set** until one is built. The fixture is
  built in a `tempfile.mkdtemp` workspace and **never** by writing into `fixtures/` — `02g` §6
  records a probe that permanently rewrote two tracked fixtures through the inspector's
  commit-on-blur. **Without the fixture the guard is untested however green the suite.**
- **`B-30` is one line, and its position is the finding.** `mapper/store.py:456` interpolates the
  full absolute path, username included, rendered through `str(exc)` at `mapper/app.py:453` and
  `:1181` — and it sits **four lines above a comment asserting that class was closed by threshold
  3**. The comment is true about the reads it describes and false about the line above it. **A
  comment asserting a class is closed is more dangerous than no comment**, and it is the sharpest
  available argument for a derived census over a fixed set of addresses.
- **Parent-story re-read:** US-N13 re-read in full. `HLR-REPAIR.1` is deliberately **not** parented
  under it: `B-30` has no US-N13 subject, and putting one source file under two story owners is the
  collision `#D5` exists to prevent. `LLR-N13.1.5`'s dependency on `LLR-REPAIR.1` is recorded at
  `HLR-N13.3` instead, where the containment arm lives.

---

### THE PASS-1 LEDGER — auditable against `02g` §4 and §5, row by row

> **Read this against `02g`, not against this document.** Every id below is an `02g` ledger id. A row
> marked **OPEN** is a deliberate non-closure with its reason; a row marked **CLOSED** claims only
> what its `Landed at` column can be checked against. **No row is self-certifying** — pass 2 and the
> lenses re-execute.

**`02g` §4.1 — architect (14 items), the six blockers this pass owns:**

| `02g` id | Before | After | Status | Landed at |
|---|---|---|---|---|
| `P2-B1` | two cuts live; `Inc-9` an id from only one of them | one cut, stated once, `#D5` sole authority; 3 headers + 6 body refs restated | **CLOSED** | §5.4; A-49 |
| `P2-B2` | 3 unowned `AT`; 6 failing the three-way rule | 2 owners written, 2 story-list legs added, 2 leave with `#D23` | **CLOSED** | A-44 table |
| `P2-B3` | literal `21` live at 4 sites | derivation over distinct `(glyph, label, style)` triples; no literal anywhere | **CLOSED — all 4 sites.** 3 amended at pass 1; `01b:373` routed at pass 1, **landed and re-read at pass 2** | A-45 |
| `P2-B4` | *"0 remaining references"* → enumeration short of the real set; 18 pins named nowhere | supersession set derived over both trees; predicted-red clause by derivation in two requirements | **CLOSED** | A-46 |
| `P2-B5` | `COERCION_RANGES` normative, orphaned | `HLR-COERCE` + `LLR-COERCE.1` + `LLR-COERCE.2`, with increments | **CLOSED** | §3.0; A-47 |
| `P2-B6` | `LLR-N06.2.5` under `HLR-N06.2` | re-parented to `HLR-COERCE`, `Inc-9` | **CLOSED for parent/increment · OPEN for a-2's physical move** | A-48 |
| `P2-C8` | un-headroomed wall-clock threshold | **subject deferred** by `#D24` | **DISPOSED, not answered** | A-43 |

**`02g` §4.2 — qa:** `QA2-C-06` **CLOSED** (same root as `P2-B1`; §5.4). `QA2-C-01` **CLOSED** for
all six ids (A-44). `QA2-C-02`, `QA2-C-03`, `QA2-C-04`, `QA2-C-05`, `QA2-C-07`, `QA2-C-08`
**NOT TOUCHED — pass 2.**

**`02g` §4.3 — security:** `C-3` **DISPOSED** with its subject (A-43), *and the underlying defect
`S-15` explicitly NOT repaired*. `S-18` **DEFERRED** (`#D24`). `S-19` **DEFERRED as `S-18`'s
precondition**, with the name-your-renderer obligation written into the deferral. `C-2b`, `S-11`,
`S-17`, `S-20`, `S-21` **NOT TOUCHED — pass 2.**

**`02g` §4.4 — ux:** `UX2-C-01` through `UX2-C-10` **NOT TOUCHED — pass 2**, except that
`UX2-C-02`'s subject is unaffected by the re-scope and its `#D10` three-row cap still needs
amending to four.

**`02g` §5 — newly raised:** `S-22` → **`B-29`, CLOSED as a requirement** (A-50). `S-23` →
**`B-30`, CLOSED as a requirement** (A-50). `UX2-C-11`, `UX2-C-12` **NOT TOUCHED — pass 2.**

**`02g` §2 — corrections the audits made to the lenses themselves:** row 2 (the rail supersession
count) is **absorbed correctly** — A-46 derives the set rather than adopting either figure. Rows 1,
3, 4 and 5 are not this document's; row 3 (`P2-C6`) is **pass 2**.

**`02g` §3 — the A3 census:** **NOT TOUCHED — pass 2** (`P2-C6`, `QA2-C-02`). `R-1`'s
question → number → instrument → measured-at-SHA form is **adopted as the house form** by this
set — every census A-45, A-46 and A-47 introduce is written in it — but `R-1` itself is not
rewritten here.

---

**WHAT AMENDMENT SET 3 PASS 1 DOES NOT DO — stated because a subset claimed as a set is `C-43`.**

Pass 2 owns, and **none of these is closed by anything in pass 1**: `P2-C1` through `P2-C7`;
`QA2-C-01`'s siblings `QA2-C-02` through `QA2-C-05`, `QA2-C-07`, `QA2-C-08`; security `C-2b`,
`S-11`, `S-17`, `S-20`, `S-21`; ux `UX2-C-01` through `UX2-C-10` and the newly raised `UX2-C-11`,
`UX2-C-12`. Two rows above are **OPEN inside items this pass otherwise closed** — `01b:373` (A-45,
routed to the ux lane) and edit a-2's physical move (A-48) — and they are listed as open rather than
folded into a closure. **`S-15` remains a live, measured, app-killing defect on `master`**; `#D24`
defers its bound and does not repair it.

*(Pass 2 follows. `01b:373` is closed there; A-48's open line stands.)*

---

## Amendment set 3 — PASS 2. 2026-08-27. Base `ea1fbf9` (`master`).

> **METHOD, unchanged from pass 1: the instrument is `02g`'s union ledger, item by item.** Pass 2
> takes the conditions pass 1 named as not-closed. Every `02g` item touched has a row in the pass-2
> ledger; every item deliberately left has a row saying so.
>
> **ONE CONDITION EXECUTED FALSE AS BRIEFED, AND THE EXECUTED RESULT GOVERNS (C-43).** `S-17` was
> briefed as *"author `LLR-STO.1.1` as a real requirement block"*. **The identifier is not phantom
> — it is defined, with thresholds and a shipped test suite, in the repair batch's document.** Doing
> as briefed would have created a **second** definition of an id that shipped code cites normatively.
> A-57 records the executed basis and the alternative taken. **This is the third time in this batch
> that a briefed premise about scope has executed false**, which is `C-43` operating exactly as
> intended rather than a failure of the brief.
>
> **New decisions this pass records:** none. Every ruling below lands in a threshold, an acceptance
> line or a routing note — the shape a fold should have.

#### A-51 · The IFC `canvas_rows` consumer list is corrected, in both directions *(`P2-C1`, `C-D4a`)*

- **Before:** consumers `views/layered.py`, `views/lane.py`, `views/outline.py`, `views/radial.py`,
  `mapper/export.py`; re-asserted in prose at two further sites.
- **After:** consumers are the three files an AST walk finds; `mapper/export.py` moves to a
  **transitive observer** line; both prose sites corrected.
- **Deleted tokens:** none. **New tokens:** the `transitive observers` field.
- **It was wrong in two different ways, and only one had been noticed.** `views/outline.py` builds
  **no `Canvas`** and calls `rows()` nowhere — a listed consumer that does not consume, which makes
  the contract un-falsifiable in its own favour. And `export.py` **snapshots the SINK** rather than
  indexing `rows()`; trigger `B4` fires on it either way, but *"its bytes change"* and *"it holds
  this positional contract"* are different claims.
- **The load-bearing consequence:** `#D4`'s stated reversal condition is *"a consumer outside
  `mapper/views/` indexing `rows()` positionally"*. With `export.py` listed, **that condition read as
  already met** and the A3 scope ruling looked reversed by its own contract table. Executed, it is
  still not met, and `#D4` stands.
- **Parent re-read:** `LLR-CNV.1.2` (the row's owner) and `LLR-CNV.2.1` (the export threshold) both
  re-read in full. **Neither statement changes** — the correction is to the contract table.

#### A-52 · `LLR-N07.2.2a` gains a call-site clause and loses its floor *(`P2-C6`, `QA2-C-02`)*

- **Before:** *"derived renderer count `>= 6`; `**kwargs` across those six `== 0`; output
  byte-identical"* — **no threshold quantified over call sites at all**.
- **After:** set equality on definitions **and** on call sites, with zero old-shape sites surviving;
  the census stated as question → instrument → SHA and adopted verbatim from `02g` §3.
- **Deleted tokens:** none. **New tokens:** mutants `M-N07.2.2a-a`, `M-N07.2.2a-b`.
- **`>= 6` was worse here than anywhere else `A-32` abolished a floor.** `grep -rn "def render"
  mapper/` returns **17**, of which **11 are Textual widgets that must not be migrated** — so a
  census that sweeps them in passes the floor comfortably while being wrong by eleven. `A-32`'s own
  argument with the sign flipped.
- **`.render` names two protocols, and five generations of this number were wrong because of it.**
  The settled AST figures are `02g` §3's; a grep returns one more, and the extra is a `renderer.render(...)`
  **mention inside a docstring**. Only a structured parse separates a value from its own encoding.
- **Parent-HLR re-read:** `HLR-N07.2` re-read. **Statement unchanged**; the amendment is a threshold.

#### A-53 · `Inc-2` owns the `docs/ARCHITECTURE.md` amendment; the Canvas commitment row is routed *(`P2-C7`)*

- **Before:** no increment owned amending the governing architecture document, so **nine increments
  would run against a document that forbids two of them**.
- **After:** §5.3 criterion 7 names **`Inc-2`** as owner, enumerates the two stale rows, and states a
  derived threshold (compare each declared signature against the live symbol).
- **Deleted tokens:** none. **New tokens:** §5.3 criterion 7.
- **`Inc-2` and not `Inc-1`, on a stated rule:** it is the **later** of the two A3s, so both subjects
  have landed by the time it closes, and a doc is not a source file so it adds nothing to `Inc-2`'s
  declared breach. Splitting the Canvas half into `Inc-1` would put one file under two increments.
- **OPEN — routed.** The **missing `dots`/`bgs` COMMITMENT row** is an edit to `docs/ARCHITECTURE.md`,
  which this lane may not touch. The repair batch already established the device — a
  `COMMITTED, NOT PRESENT` row that *"states a plan without asserting a falsehood"* — and the Canvas
  half has none, so the second A3 is committed nowhere. **Routed to the orchestrator.**

#### A-54 · `C-D4c`'s re-run obligation becomes a clause *(`P2-C2`)*

- **Before:** *"`AT-007` / `AT-009` re-run after `Inc-2`"* existed in the reviewer files and
  `PLAN.md`, and **in no requirement**.
- **After:** a standing re-run obligation in `HLR-CNV.1`, with `Inc-2` barred from closing on either
  red, plus mutant `M-CNV.1-rerun`.
- **Deleted tokens:** none. **New tokens:** mutant `M-CNV.1-rerun`.
- **A RECORDED FINDING IS NOT A CLAUSE — that is the whole of `P2-C2`.** Nothing in `Inc-2`'s gate
  would have failed if the re-run never happened, **because a gate reads requirements, not review
  notes**. Carried through three passes on that distinction alone.
- **Why the re-run is real and not ceremony:** `Inc-2`'s gate is byte-identity of a renderer against
  **itself**, and such a gate cannot see a chain that was already broken, nor one it breaks
  identically on both sides.

#### A-55 · The two traceability chains cross — `#D15` discharged as a derived join *(`P2-C3`)*

- **Before:** two tables that never crossed. `grep "D15\|AT↔TC"` → **0 hits**. Graded ✗ at the first
  architect pass and **untouched by 41 amendments**.
- **After:** the join is **stated once and computed** — for every live `AT`, its `TC` set is the `TC`s
  of the requirements carrying that `AT` on an `Acceptance:` line. Executed at `ea1fbf9`: **total, 0
  live `AT` ids reach no `TC`**.
- **Deleted tokens:** none. **New tokens:** none.
- **It was dischargeable only after pass 1.** The join's middle column is the `Acceptance:` owner,
  and until `A-44` gave `AT-009` and `AT-031` owners the join had no middle column. `P2-C3` was
  correctly blocked on `P2-B2`.
- **A JOIN, NOT A THIRD TABLE — deliberately.** A transcribed mapping would be a hand-maintained
  artifact joining two derived ones, and this document has shipped four wrong generations of that
  exact shape. Pass 1 alone moved eleven ids.
- **Two apparent gaps, both false, both recorded** so the implementer does not "fix" a correct
  artifact to satisfy a broken oracle: a scanner that drops table rows containing the word
  `DEFERRED` loses `HLR-N13.3`'s live `TC-076` row, because that row's **note** records `#D24`.

#### A-56 · `with_header`'s second roster is routed *(`P2-C4`, `#D2`)*

- **Before:** `#D2` struck `ViewState.with_header`; **half landed**. This document is clean;
  `ARCHITECTURE-proposed-at-ARQ.md` still names it and still declares it inside the dataclass.
- **After:** `LLR-N07.2.3` — the requirement that creates `ViewState` — declares the roster and
  records the collision, with the strike **routed** to the lane that owns the other artifact.
- **Deleted tokens:** none. **New tokens:** none.
- **The collision lands precisely on the new LLR**, which is why it is recorded there: an implementer
  reading the ARQ roster writes a field this LLR does not declare, and the signature clause will not
  catch it because `with_header` is a **field**, not a parameter. **OPEN, routed.**

#### A-57 · `LLR-STO.1.1` is RESOLVED as a cross-batch reference, not re-authored *(`S-17`, `QA2-C-03`, `C-2b`, `S-11`)*

- **Before:** four prose references in this document to an id with no heading here; every census over
  this document alone correctly reported it fabricated.
- **After:** a resolving reference block naming its definition site, its statement, its thresholds
  and its shipped test suite; the `S-11` half discharged **through** that reference; the over-claim
  about crash-resistance recorded.
- **Deleted tokens:** none. **New tokens:** none — **and that is the point of the amendment.**
- **THE BRIEFED FIX WOULD HAVE MADE IT WORSE, AND THIS IS THE PASS'S MOST IMPORTANT CORRECTION.**
  Executed: `grep -rn "^#\+ .*LLR-STO" .dev-flow/` finds the heading in the **repair batch's**
  document. **The diagnosis was right about the symptom and wrong about the cause**: the defect is a
  missing *reference declaration*, not a missing requirement. Authoring a second block would put two
  headings under one id **that shipped code cites normatively in six places** — three docstrings and
  three inline comments — and the code would obey whichever copy the reader found first. That is the
  two-live-definitions defect `#D6` and `#D14` removed, at higher stakes.
- **Precedent followed rather than invented:** §6.5 `A-01` already resolved `LLR-R04.1` as *"a
  reference, defined at"* the prior batch's document.
- **⚠ THIS AMENDMENT'S OWN HEADING NOW TRIPS THE REGEX THAT CAUSED THE MISDIAGNOSIS — anchor the
  census.** `grep "^#\+ .*LLR-STO"` over this document returns **one** hit, and it is the `A-57`
  heading two lines above, not a requirement. A census that reads that as *"the requirement now
  exists here"* would be wrong in the **opposite** direction to the original error, and the same
  loose pattern would produce it. **A requirement-heading census shall anchor on
  `^#{4,5} \`?(HLR|LLR)-`** — the id at the start of the heading, optionally backticked — which
  matches requirement headings and not amendment records. Recorded here because this document is
  corpus an id-scanner reads, and the one thing `S-17` proves is that the scanner's pattern is part
  of the finding.
- **A count deliberately NOT adopted:** the reconciliation's *"0 of 19 hostile inputs"*. Executed,
  **the 19 is enumerated nowhere** and appears in exactly one artifact. This document cites the
  derivation instead. Adopting an unaudited figure into a requirement is how the four wrong
  generations of the `AT` total began.
- **One property not over-claimed:** `MapStoreError` is a bare `Exception` subclass and **both real
  `load` callers catch bare `Exception`**, so the typed refusal changes the operator's **message**,
  not crash-resistance at any existing call site.

#### A-58 · The carried alias-bomb arm gets a real owner — `LLR-N13.1.7` *(`C-12`, `S-14`)*

- **Before:** *"a bomb under `nodes:` belongs in `LLR-STO.1.1`'s fixture set"* — carried across two
  batches, owned by nobody, and **uncovered by any test on any tree**.
- **After:** `LLR-N13.1.7`, owned by `Inc-REPAIR`, with an un-aliased control mandated.
- **Deleted tokens:** none. **New tokens:** `LLR-N13.1.7`, `TC-088`, mutant `M-N13.1.7-a`.
- **This is the one thing the `LLR-STO.1.1` reference does NOT discharge**, and separating the two
  is why the reference could be taken safely. Verified: `_graph_from_sidecar` reads exactly three
  keys, and the `nodes` branch walks every entry, every `fields` map and every `attachments` list —
  so the measured-and-closed disposition, which rests on *"a bomb under any other key is never
  traversed"*, **does not reach this key**.
- **The mutant is the reason the control is mandatory:** reusing the existing bomb fixture under an
  unread key is **green today and green forever**, because it measures PyYAML's alias sharing rather
  than this code path.

#### A-59 · `MAX_RENDER_NODES` is declared one concept — and explicitly NOT repaired *(`S-20`)*

- **Before:** three literals in three modules, five independent stack walks, `children_of` O(E) per
  call; no requirement said any of it.
- **After:** `HLR-N13.3` declares the three copies **one concept**, and states in the same breath
  what is **not** fixed, cross-referencing backlog `B-33`.
- **Deleted tokens:** none. **New tokens:** none.
- **THE HARD PART OF THIS AMENDMENT IS NOT OVER-CLAIMING.** The bound that would repair the cost is
  **deferred with `#D24`**. Re-measured here at `ea1fbf9`: `children_of` per-call cost doubles as `E`
  doubles — O(E) per call, O(N·E) through `Graph.focus`, which is **not a renderer** and which
  `MAX_RENDER_NODES` therefore does not guard at all. **Deferring a bound does not repair a defect**,
  and `S-20` and `S-15` are the two halves a reader is most likely to assume the other closed.
- **Evidence the shared helper is missing rather than unnecessary:** four modules carry the
  *identical* comment describing the workaround.

#### A-60 · Coercion is declared on every flow that carries file-derived text *(`S-21`)*

- **Before:** exactly **one** node in all of §4.1 named coercion, while three other flows carry
  strings from disk to a painted surface.
- **After:** the coercion node is declared as a **class** owned by `HLR-COERCE`, applied to the three
  carrying flows, with `match_set` declared coercion-free **and the reason recorded**.
- **Deleted tokens:** none. **New tokens:** the class node.
- **A flow contract that declares a control on one of four paths says the other three do not need
  it** — the §2.1b failure at a fourth surface. The per-flow `owner` lines are unchanged, because
  row width and clipping region differ per surface, which is exactly why the HLR owns the class and
  not the thresholds.
- **`consumers : none` is written explicitly wherever it is true** (§4's own convention), and the
  same rule is now applied to a **control**: *"this flow does not need coercion"* is recorded so the
  next reader need not re-derive whether the absence was a decision.

#### A-61 · `HLR-S06.3`'s threshold stops being its own child's mutant *(`QA2-C-04`)*

- **Before:** *"every `WARN`/`ALERT` site is classified **severity**"*.
- **After:** every `WARN` site classifies as **outstanding attention**, every `ALERT` site as
  **failure or blockage**, against `LLR-S06.3.5`'s single declared job per token.
- **Deleted tokens:** none. **New tokens:** none.
- **THE PARENT ASSERTED AS ITS PASS CONDITION EXACTLY THE MUTANT ITS CHILD MUST REDDEN.**
  `LLR-S06.3.5` names `M-S06.3.5-a` as *"give `WARN` and `ALERT` the single job severity"* and
  requires it RED. Two requirements demanded opposite outcomes from one census — and the parent,
  holding the `Acceptance:` line, would have won. *"Severity"* is the **family**, so it cannot tell
  the two apart and licenses painting a failure and an outstanding item identically.

#### A-62 · The census classifier is defined *(`QA2-C-05`)*

- **Before:** *"classifies as outstanding attention"* with no executable definition of *classifies*.
- **After:** a **declared per-site register** over a **derived** input set, with a **totality**
  clause: a derived site with no register row is a failure, not a skip.
- **Deleted tokens:** none. **New tokens:** mutant `M-S06.3-classifier`.
- **The split is what makes `test (unit)` honest:** the *judgement* (which job a site expresses) is
  made once and written into the artifact; the *check* (totality, and job-equality against the
  token's single declared job) is mechanical.
- **Why not the offered alternative of marking `AT-005`/`AT-006` `analysis`:** it would be honest and
  would **lose the property the story exists for** — *"a later batch cannot quietly reuse a hue"* —
  because only a totality clause evaluated at gate time catches the site a later batch adds. An
  analysis is performed once; this must fail later, on work nobody has written yet.

#### A-63 · Three stale `AT-007` ids corrected to `AT-007b` *(`QA2-C-08`)*

- **Before:** `HLR-CNV.2`'s prose said *"`AT-007`'S EMPTY ARM IS VACUOUS"* and *"the title, the §5.2
  row and `AT-007` all name `RadialRenderer`"* while its `Acceptance:` line reads `AT-007b`; §5.3
  criterion 5 named `AT-007` for the containment arm `AT-007b` owns.
- **After:** all three read `AT-007b`.
- **Deleted tokens:** none. **New tokens:** none.
- **The A-37 split was correct and its own prose was not updated with it** — the id-staleness class
  `R-11` predicted. §6.5 A-24's historical record is **left as written**, because it records what the
  split said at the time and amending a record falsifies it.

#### A-64 · Every increment gets a fixture-budget line *(`QA2-C-07`)*

- **Before:** fixtures were counted nowhere. Three had accumulated unowned, and `QA-M-02` and
  `QA-N-08` were marked **DROPPED** with zero occurrences in any artifact.
- **After:** §5.4.1, one row per increment, plus the `tempfile.mkdtemp` rule and the reconciliation
  of the three.
- **Deleted tokens:** none. **New tokens:** §5.4.1.
- **`QA-N-08` is the case that exposed the gap:** `LLR-N07.1.2`'s widening arm needs a graph with
  attachments and distinguishing `meta`, and **the shipped `legacy` fixture has neither** — so the
  arm could not be driven on any fixture that existed, and no budget noticed.
- **The three reconcile rather than appearing absorbed:** `anidado` and `QA-N-08`'s synthetic graph
  are budgeted; `AT-048`'s generated workspace **left with `#D24`**.
- **The `fixtures/` prohibition is executed, not stylistic:** a probe pointed at the real directory
  had commit-on-blur write through and permanently alter two tracked files. **A fixture a test can
  damage is a fixture that will be damaged.**
- **`QA-M-02` is restored to a ledger and discharged elsewhere** (`QA2-C-02`, A-52). Recorded because
  **a minor dropped without a line saying where it went is indistinguishable from one that was
  lost** — which is `QA2-C-07`'s whole point.

#### A-65 · The pan chord is named: `H` `J` `K` `L` *(`UX2-C-03`)*

- **Before:** *"this requirement stays written chord-agnostic; PDR ratifies the specific chords"* —
  so `AT-011` and `AT-012` pressed no named key.
- **After:** the four chords are named, both `AT`s press them for real, and the seat-pin obligation
  is stated.
- **Deleted tokens:** none. **New tokens:** none.
- **`QA-B-10`'s rule was applied to two stories and missed for the third.** A chord-agnostic
  *requirement* is legitimate; a chord-agnostic *acceptance test* is not (`C-16`).
- **The aggravator is what makes it a defect rather than an untidiness:** `AT-012` asserts the
  `borde del territorio` declaration — the clause the ux lens added **because** a silent no-op was
  ruled insufficient — **against a key nobody had named.** The most carefully argued clause in the
  requirement was unfalsifiable for want of a keystroke.
- **Executed:** all four arrive as their own `event.key`, all four free in map scope, `H` changes
  nothing on the shipped screen, `duplicate_chords()` returns `[]`.
- ~~**OPEN — routed.** Four rows breaches `#D10`'s three-row seat-diff cap … **`Inc-3` shall not
  open until the cap is ruled.**~~ — **CLOSED 2026-08-27 by `PDR-addendum-3#D25`: NO BREACH,
  `Inc-3` UNBLOCKED.** The figure is a **pin on `Inc-4`'s own diff**, not a per-increment budget;
  its carrier `PLAN.md:244` states an **equality** on that diff. `Inc-3` owes `C-D25a` instead — its
  own four-row diff, asserted equal to the entry/exit difference of `bindings_for("map")`. The bare
  `#D10` cited above is **ambiguous** and superseded by `#D5b` + `#D25` (`B-34`).

#### A-66 · `LLR-N06.2.4`'s oracle is replaced — it false-failed correct work at every width *(`UX2-C-04`)*

- **Before:** *"the selected node's id appears in the painted canvas text"*, plus a clause reading
  `MapScreen.folded`.
- **After:** `PRED-A` (painted id set, as data) · `PRED-B` (clipped-and-visible **title** trace) ·
  `PRED-C` (no fold pill on the surface) · the hint line.
- **Deleted tokens:** none. **New tokens:** `PRED-A`, `PRED-B`, `PRED-C`, mutants `M-N06.2.4-a`,
  `M-N06.2.4-b`.
- **THE CANVAS PAINTS TITLES, NEVER IDS — 0 of 8 traced at 50 x 12, 80 x 24 and 120 x 40.** `AT-046`
  **fails on a perfect implementation at every terminal size**. `C-53` prices a false-fail as high as
  passing wrong work, and this is its sharper half: **a gate that cannot be passed gets weakened, and
  the weakening ships.** This is `QA-B-02`'s root-title oracle for the **third** time; the fix reuses
  the oracle `A-21` already settled rather than inventing a fourth.
- **The second defect is the opposite failure:** `MapScreen.folded` is a **model attribute**, so
  `AT-047` could pass while the branch paints closed — a silent state change, the one thing US-N06
  forbids. `PRED-A` reads data and `PRED-C` reads the surface **deliberately**; neither substitutes
  for the other.
- **Parent-HLR re-read:** `HLR-N06.2` and `HLR-N07.3` both re-read. **Neither statement changes.**

#### A-67 · `HLR-S06.2` declares its guaranteed rung and retires an `assumed` flag *(`UX2-C-10`)*

- **Before:** *"flagged `assumed`: that slots 33 and 38 are perceptually distinguishable"*, and no
  statement of which colour rung the requirement guarantees.
- **After:** the rung is **`EIGHT_BIT` and above**; the perceptual claim is measured and retired; a
  derived CIEDE2000 floor replaces it; the 16-colour rung is a **declared known limit**.
- **Deleted tokens:** none. **New tokens:** the perceptual floor clause.
- **Slot adjacency was the wrong proxy, measured:** the minimum CIEDE2000 over semantic pairs is
  **13.99** (`ACCENT`/`VIOLET`), while the pair the flag actually worried about — `ACCENT`/`TEAL`,
  five slots apart — measures **20.18**, **further apart than the pair nobody worried about.**
- **The collisions are declared, not fixed, and the reason is stated:** the 16-colour rung is not
  auto-reachable (Textual sets `legacy_windows=False`), but it is one unpinned environment variable
  away and **the product does not pin it**. `ACCENT ≡ VIOLET` is the expensive one — blue is declared
  interactivity-only, so the link marker would read as *"you can act here."*
- **A measurement hazard is written into the verification** because it produced a plausible wrong
  answer: `Style.parse` is LRU-cached and caches `_ansi`, so a probe reusing a `Style` **returns the
  first rung's codes for every later rung** and reports no collisions anywhere.

#### A-68 · `HLR-N06.3` gains `PRED-4`: the declaration must be legible *(`UX2-C-08`)*

- **Before:** three predicates, all satisfiable on a frame the operator cannot read.
- **After:** `PRED-4` — contrast `>= 4.5 : 1` at the guaranteed rung and never equal to `GROUND` at
  any reachable rung; `V7` and `V8` move to `MUT`; `WORDMARK` keeps `V4`.
- **Deleted tokens:** none. **New tokens:** `PRED-4`, mutant `M-N06.3-legibility`.
- **`V7` carries US-N06's entire promise and is painted at 1.85 : 1** — about 40 % of the minimum, at
  **both** rungs — and on the `WINDOWS` rung `WORDMARK` collapses into `GROUND`, so the declaration
  is not dim but **absent**.
- **The parked oracle is structurally blind to this:** `AT-015`/`AT-016` assert the declaration is
  *present in the painted text*, equally true at 1.85 : 1 and at 8 : 1 **and equally true when the
  glyph is painted in the background colour**. All three prior predicates can be green while the
  story fails.
- **`V4` stays on `WORDMARK` deliberately** — barely-there is the point for unexplored territory.

#### A-69 · The damaged card gets a visual limb and the right pilot size *(`UX2-C-09`)*

- **Before:** the damaged state was a **string only**; the inequality threshold was satisfied by a
  text-only difference; the arm ran at 140 x 45.
- **After:** `PRED-VIS` requires a declared token or glyph; the arm runs at **118 x 34**, the
  declared context of use.
- **Deleted tokens:** none. **New tokens:** `PRED-VIS`.
- **Reproduced with a healthy-empty control:** `roto` and `sano_vacio` paint **byte-identically**,
  and the notice that distinguishes them is a **transient toast** while the card is **permanent**.
  The sala is scanned, not read: *"a card that differs only in text differs only to someone already
  reading it."*
- **The token is NOT silently spent.** `ALERT` fits `LLR-S06.3.5`'s declared job, **but** `01b` §3.5
  requires a second job to buy a row in `colores con empleo`, which changes `LLR-N16.2.1`'s derived
  set. The requirement demands *a* declared token and **routes the choice with the cost stated**.
- **No character count is written**, deliberately: the two available figures for the copy's length
  disagree by one, and a hand-counted total in this document would be the fifth wrong count. The test
  measures the painted row.

#### A-70 · `AT-051` presses the real `M` *(`UX2-C-07`)*

- **Before:** the clause named only `n` and `N`, so the relocated chord was guarded solely by the
  whole-seat pin and `duplicate_chords()`.
- **After:** `AT-051` presses the real `M`; `Inc-4` paints a one-time declaration on the first `n`
  press after the rebind.
- **Deleted tokens:** none. **New tokens:** `AT-051`, `TC-084`, mutant `M-N07.3-rebind`.
- **Both existing guards are DECLARATION checks.** They prove the seat *says* `M` is `next_gap`;
  neither presses it. **A seat row can be correct while the action it names is unreachable.**
- **The discoverability half is measured:** at 118 x 34 `siguiente faltante` is one of the eleven
  rows **below the fold**, behind scroll keys the legend does not declare — so an operator pressing
  `n` for the old behaviour has **no painted route** to the new one. The toast precedent is executed:
  `next_gap` with nothing missing already toasts `cobertura completa`.

#### A-71 · The count line declares its subject; `E1b`'s copy is re-derived *(`UX2-C-06`, US-N07 half)*

- **Before:** nothing painted declared which result set was live; `E1b` routed the operator to `/`.
- **After:** `AT-052` asserts the painted count line names its subject and term; `Inc-4` restates
  `E1b`'s body against the unified walk.
- **Deleted tokens:** none. **New tokens:** `AT-052`, `TC-085`.
- **The two count lines differ in form, and that difference is incidental rather than declared.** The
  named failure: `/carlos` → `3/7 coincidencias` → a lens → `5 nodos en 2 ramas`; the seven hits are
  gone, `n` still reads `siguiente coincidencia`, and **the operator believes they see an
  intersection.** Executed, submit also paints **no** mode change at all — `focused=None`, no widget
  paints a focus ring, and the query text looks exactly as it did while being typed.
- **`E1b` is `02f`'s root cause in one line — a consequence not re-derived after a decision changed.**
  It was written under Q-3, before `#D6` unified the walk. `E1c` is **unaffected** and retained
  verbatim, because it describes a completed search with an empty answer under either ruling.
- **The US-N14 half left with the story** (`#D23`) and is not carried here.

#### A-72 · `HLR-N16.4` — the legend declares its own keys *(`UX2-C-05`)*

- **Before:** the legend declared **two** keys for its own scope; `down`, `pagedown` and `end` all
  work and none was declared, with eleven of twenty-seven rows below the fold at rest.
- **After:** `HLR-N16.4`, set equality between keys-that-work and keys-declared, asserted by real
  presses; owned by `Inc-8`.
- **Deleted tokens:** none. **New tokens:** `HLR-N16.4`, `AT-053`, `TC-086`, mutant `M-N16.4-a`.
- **The legend is a view, and it is the one view whose keys it does not explain.** Content is not
  lost — the union over scroll positions is total — so this is **purely discoverability**, landing on
  the one screen whose entire job is discoverability.
- **It gets worse inside this batch:** `LLR-N16.2.1` roughly triples the scrollable content, so **the
  two sections this story adds land furthest below the fold.**
- **The assertion must be a keystroke, and the shipped guard shows why:** `tests/test_repair_layout.py`
  scrolls with `pane.scroll_to(...)` — a **method call** — proving the container scrolls and saying
  nothing about whether an operator can make it. `C-16` verbatim.
- **OPEN — routed.** Whether a flat ~44-row scroll is the right information design is a **ux ruling**.
  This requirement fixes the discoverability defect under either outcome.

#### A-73 · `UX2-C-11` and `UX2-C-12` are recorded as DEFERRED with US-N14 *(backlog `B-31`, `B-32`)*

- **Before:** raised at the RIDER-1 reconciliation, in **no** prior lens ledger, so neither had been
  through a review.
- **After:** both enumerated in §3.7's deferral block, with their evidence and their open questions.
- **Deleted tokens:** none. **New tokens:** none.
- **`UX2-C-11`:** `_commit` rewrites the sidecar on an **empty delta** — 6 of 9 focusables rewrote
  while only 5 changed a value; **the loss is durable to disk**. Joined to US-N14 because it needs
  the same confirmation-affordance ruling, not because it is a lens defect.
- **`UX2-C-12`:** the damaged-map toast fires **twice, both untitled**. Verified: neither `notify`
  call site passes `title=`, which accounts for the empty titles. **The double-fire is NOT
  accounted for** — the failure arm de-duplicates per name within one call. **Recorded as open and
  unexplained rather than as diagnosed.**
- **Neither is closed by `B-30`**, which shares one of the two strings and addresses only the path.
  Stated because two findings on one string is exactly where a fold drops one.

#### A-74 · The routed seat-diff cap is ruled: it is a PIN on `Inc-4`'s diff, not a budget *(`UX2-C-03`, `PDR-addendum-3#D25`)*

- **Before:** `A-65` recorded *"Four rows breaches `#D10`'s three-row seat-diff cap … `Inc-3` shall
  not open until the cap is ruled."*
- **After:** `PDR-addendum-3#D25` rules the figure a **regression pin on `Inc-4`'s own three-row
  diff**, in C-40's sense, binding `Inc-4` alone. **`Inc-3` is unblocked; there is no breach.**
- **Deleted tokens:** none. **New tokens:** `#D25`, conditions `C-D25a`, `C-D25b`, `C-D25c`.
- **The premise executed FALSE, and the alarm was still worth raising.** `#D5b` enumerates its own
  three rows and the *next sentence* names `Inc-3`, `Inc-6` and `Inc-9` as `keymap.py` touchers while
  imposing only `duplicate_chords()` + the whole-seat pin on them — no row budget. Reading a
  descriptive pin as a prescriptive budget is a **false-fail**, which C-53 prices as high as a false
  pass.
- **The disposition ENLARGES:** the alarm correctly noticed that **no obligation attached to `Inc-3`'s
  seat rows at all**. `C-D25a` now makes every seat-touching increment declare and pin its OWN row
  diff — a pin per diff, deliberately **not** a global cap, which would price a well-cut increment
  against an unrelated one's spending.
- ⚠ **`#D10` names two different decisions.** `PLAN.md:244` `D10` is the Q-3 seat rebind; the sealed
  `PDR-…#D10` (`:566`) is the Q-10 **hue** dispositions. The cap's real carrier is **`#D5b`**. Carried
  as `B-34`; see `PDR-addendum-3` §1.

#### A-75 · The legend scrolls; the tabbed redesign is deferred *(`UX2-C-05`, `PDR-addendum-3#D26`)*

- **Before:** `A-72` closed the discoverability defect and routed *"whether a flat ~44-row scroll is
  the right information design"*.
- **After:** `PDR-addendum-3#D26` — a **scrolling container** this batch; the two-pane/tabbed legend
  deferred as `B-35`.
- **Deleted tokens:** none. **New tokens:** `#D26`, conditions `C-D26a`, `C-D26b`, `C-D26c`.
- **The routed question was already half-answered and the routing did not say so.** `01b` §3.8
  measured the legend at **54 rows minimum against 34 available — short by 20** and ruled the flat
  panel OUT in terms: *"US-N16 cannot paint one flat panel."* The live choice was **scroll vs
  tabbed**, never flat vs scroll. `LLR-N16.2.1` widens the vocabulary further, so the shortfall is
  **larger** than 20, not smaller.
- **`C-D26a` is the load-bearing condition:** set equality asserts over the panel's **content**, never
  over what is visible — an assertion over visible rows passes on a clipped panel, which is what ships
  today.

#### A-76 · The damaged card takes a GLYPH; `ALERT` is not spent *(`UX2-C-09`, `PDR-addendum-3#D27`)*

- **Before:** `A-69` required `PRED-VIS` (a declared token **or glyph**) and routed the choice with the
  cost stated — taking `ALERT` would give it a second job and change `LLR-N16.2.1`'s derived set.
- **After:** `PDR-addendum-3#D27` — a declared **glyph** in `01b` §3.4's sala vocabulary, painted
  `MUT on PANEL`. **No colour token is spent.**
- **Deleted tokens:** none. **New tokens:** `#D27`, conditions `C-D27a`–`C-D27d`.
- **Executed: there is no unspent colour token.** `darkside.py:12-20` ships nine; `Inc-1` adds three,
  and `01b` §3.4/§3.5 already spend all three — `VIOLET` = `enlaza mapas`, `TEAL` = `procedencia
  repo`, `SAGE` = `completo / vigente`.
- **`ALERT` looks free only because the lens is CUT — and that is C-55 limb 2 by name.** `01b` §3.5
  assigns `ALERT` exactly one job, the malformed-query chip, which belongs to the **deferred** lens.
  The lens is scheduled, not cancelled: spending `ALERT` now hands the follow-on batch a token with
  two jobs, an unadjudicable `LLR-S06.3.5` census and a `colores con empleo` row this batch never
  budgeted. **Ruling on an accidental emptiness costs the next batch a defect this one cannot see.**
- **`MUT on PANEL` is reuse, not invention:** it is the sala's shipped pairing for absent information
  (V21 unlit `∙` = `sin acta`; V15 `faltan campos ░`). A map that cannot be summarised is an
  **absence of information, not an alarm** — and the sala vocabulary is glyph-led throughout (`⇄`,
  `◍`, `▲`, `█`/`░`, `∙`), with colour as the secondary carrier in every row.
- **No codepoint is fixed here (`C-D27b`)**, deliberately: it is drawn from the declared vocabulary by
  the increment that paints it and asserted by the derived-set test. `A-45` records what a
  hand-written count costs in this document — four wrong generations.

---

### THE PASS-2 LEDGER — auditable against `02g` §4 and §5

| `02g` id | Status | Landed at |
|---|---|---|
| `P2-C1` | **CLOSED** | A-51 — consumer list corrected both ways; `#D4` made checkable again |
| `P2-C2` | **CLOSED** | A-54 — `C-D4c` becomes a clause in `HLR-CNV.1` |
| `P2-C3` | **CLOSED** | A-55 — `#D15` as a derived join; executed total |
| `P2-C4` | **CLOSED here · OPEN, ROUTED for the ARQ roster** | A-56 |
| `P2-C5` | **CLOSED** | `LLR-N07.2.3` — creates `ViewState` and `IRenderer`; the `isinstance` gate **and** the signature clause that stops it being vacuous |
| `P2-C6` | **CLOSED** | A-52 — set equality both sides; `02g` §3's census adopted |
| `P2-C7` | **CLOSED for the owner · OPEN, ROUTED for the commitment row** | A-53 |
| `QA2-C-02` | **CLOSED** | A-52 |
| `QA2-C-03` | **CLOSED — subsumed by `S-17`** | A-57. It is the same defect at a different surface; a separate fix would have been a second reference |
| `QA2-C-04` | **CLOSED** | A-61 |
| `QA2-C-05` | **CLOSED** | A-62 |
| `QA2-C-07` | **CLOSED** | A-64 — §5.4.1 |
| `QA2-C-08` | **CLOSED** | A-63 |
| `C-2b`, `S-11`, `S-17` | **CLOSED** | A-57 — one reference resolves all three; `S-11`'s code half was already discharged by measurement |
| `C-12` carried arm | **CLOSED** | A-58 — `LLR-N13.1.7` |
| `S-20` | **CLOSED as a requirement · defect NOT repaired** | A-59; bound deferred with `#D24`, carried as `B-33` |
| `S-21` | **CLOSED** | A-60 |
| `UX2-C-03` | **CLOSED · OPEN, ROUTED for `#D10`'s cap** | A-65 |
| `UX2-C-04` | **CLOSED** | A-66 |
| `UX2-C-05` | **CLOSED · OPEN, ROUTED for the layout ruling** | A-72 |
| `UX2-C-06` | **CLOSED (US-N07 half); US-N14 half left with `#D23`** | A-71 |
| `UX2-C-07` | **CLOSED** | A-70 |
| `UX2-C-08` | **CLOSED** | A-68 |
| `UX2-C-09` | **CLOSED · OPEN, ROUTED for the token choice** | A-69 |
| `UX2-C-10` | **CLOSED** | A-67 |
| `UX2-C-11`, `UX2-C-12` | **DEFERRED with US-N14, owned** | A-73; `B-31`, `B-32` |

---

**WHAT AMENDMENT SET 3 PASS 2 DOES NOT DO.**

- **`UX2-C-01` and `UX2-C-02` are NOT closed here**, and they are not in pass 2's brief either.
  `UX2-C-01` is the durable-data-loss finding — a single keystroke permanently replaced an acta
  reference in a tracked file — and `UX2-C-02` proposes the `c` entry chord. **Both need design
  rulings, and both are inspector-side**, which is why they travel with the same
  confirmation-affordance question as `UX2-C-11`. **Recorded as NOT CLOSED rather than omitted**:
  pass 1's own not-closed list named `UX2-C-01` through `UX2-C-10`, and closing eight of ten without
  saying which two remain would be the drop this ledger exists to prevent.
  > **DISPOSITION 2026-08-27 — referred, not ruled.** `PDR-addendum-3` §5 puts both to PDR iteration 3
  > as an explicit question, with the recommendation to DEFER them to the follow-on design batch
  > alongside `UX2-C-11` (`B-31`/`B-32`). **The deferral is recorded as NOT cost-free:** `UX2-C-01` is a
  > live durable-data-loss defect on `master`, and the lenses are asked to rule on leaving it live
  > rather than to inherit that silently. The minimal alternative is stated there if any lens refuses
  > — gate `_commit` on a non-empty delta, one predicate, which also closes `UX2-C-11`.
- **Five items are CLOSED IN THIS DOCUMENT with an OPEN routed edit in another artifact**: `P2-B3`'s
  `01b` line (closed at pass 2 — the routed edit landed and was re-read), `P2-C4`'s ARQ roster,
  `P2-C7`'s commitment row, `UX2-C-03`'s `#D10` cap, `UX2-C-05`'s layout ruling, and `UX2-C-09`'s
  token choice. **None of these is this lane's to make**, and each is stated as routed rather than
  assumed done.
  > **DISCHARGED 2026-08-27 by the orchestrator — all six, and the count above is off by one.**
  > The sentence says *"five items"* and enumerates **six**; the sixth (`P2-B3`) was already closed
  > when it was written, which is how the miscount survived. Recorded rather than silently fixed.
  > **Two landed as edits:** `P2-C4` — `ARCHITECTURE-proposed-at-ARQ.md:275` struck, and its stale
  > `layered.py:78-87` address corrected to `:131-140`; `P2-C7` — `docs/ARCHITECTURE.md` §4 gains the
  > second A3's `COMMITTED, NOT PRESENT` row for `Canvas.dots`/`.bgs`.
  > **Three landed as rulings** in `PDR-addendum-3`: `#D25` (`A-74`), `#D26` (`A-75`), `#D27`
  > (`A-76`).
  > **`P2-B3` was re-read, not trusted** (`C-44`): `01b-ux-decisions.md:382-385` carries the derived
  > count and no stale literal. ✓
- **A-48's open line still stands** — `#D21` edit a-2's physical relocation of `LLR-N06.2.5` is still
  not performed, for the reasons pass 1 recorded and pass 2 does not revisit.
- **`S-15` and `S-20`'s cost remain live, measured defects on `master`.** `#D24` defers their bound.
  Carried as `B-33`.

---

## Amendment set 4 — INC-1 IMPLEMENTATION. 2026-08-28. Base `5d8ee0d` (`feat/ui-next-batch-02`).

> **These are Phase-3 amendments, recorded per the §6.5 Before/After rule rather than edited
> silently into the body.** Every one was forced by an *executed* result during Inc-1, not by
> preference. Byte hygiene: every code point below is written as a `U+XXXX` name, and every mutation
> is described by **position and operation** — this document is corpus an id-scanner reads, so a
> mangled token pasted here is not reverted merely because the source file was (`C-56`).

### A-77 — `#D10`'s busy-token disposition contradicted itself; the NEW-TOKEN reading governs

**The document forked inside one LLR.** `LLR-S06.3.2`'s `#D10` table row says the busy job goes to
*"one of the three tokens Inc-1 is already adding (`SAGE`/`TEAL`/`VIOLET`)"*; **fourteen lines
below**, the same LLR's `Touched symbols` line says *"the promoted grey token **and the busy
token** — both `NEW`"*, and `LLR-S06.3.5` consequence 4 says *"The busy job goes to a new token"*.
`PDR-addendum-3` §4 — sealed last — says *"all three new tokens are already spent … There is no
unspent colour token."*

**Ruled: NEW token.** Three grounds, in ascending weight. (i) Majority and latest: three sites plus
the last-sealed document. (ii) The rival reading is **not executable** — `HLR-S06.1`'s Statement is
a `shall` that fixes all three jobs, and `LLR-S06.1.1` declares the one-job rule, so handing the
busy job to any of the three creates a two-job token *in the increment that declares the rule*, and
`LLR-S06.3.5`'s census then has no oracle — `QA-B-08`'s finding, re-created. (iii) `Touched symbols`
is the machine-checkable field Phase 3 is gated against; prose can be loose, a build contract cannot.

**Before:** `LLR-S06.3.2` `#D10` row — *"Assign the busy/in-progress job to one of the three tokens
Inc-1 is already adding (`SAGE`/`TEAL`/`VIOLET`) and retone the site."*
**After:** *"Assign the busy/in-progress job to a NEW token and retone the site. The three v2 tokens
are spent by `HLR-S06.1`'s `shall` and may not take a second job."*

**New tokens (both `NEW — created in Phase 3`, as `:994` already declared):**

| Token | Value | Slot | Job |
|---|---|---|---|
| `ASH` | `#a3a3a3` | 247 | *segundo escalón legible* — the middle rung of the text ramp, one step below `INK`, where `STEP` and `WORDMARK` are too dark to read as text |
| `PULSE` | `#ff9ecb` | 218 | *trabajo en curso* — this item is being worked on right now, and nothing is pending, overdue, at risk, or failed |

**Both lenses were run and they disagreed; the disagreement is recorded rather than averaged.**
`02i-inc1-busy-token-architect.md` ruled the new token; `02i-inc1-busy-token-ux.md` ruled *no* new
hue, carrying the busy meaning on the glyph and re-ranking the ladder on the neutral ramp. The ux
reading was **not** adopted, for two reasons stated so a later reader can re-open it knowingly:
it declines `#D10`'s *"assign … the job"* clause, which is an **A3 re-open** and not a Phase-3
discharge; and its `PENDING` rung is `MUT` on `PANEL` at a measured **3.95:1**, which sealed `#D28`
forbids for readable text. Its ladder findings are carried, not discarded — see A-83.

Executed, `rich 15.0.0`, a fresh `Color` per call (`HLR-S06.2`'s LRU caching hazard honoured):
slot 218 is free; `PULSE`'s minimum CIEDE2000 to any declared token is **24.74** (nearest `INK`, a
neutral); `ASH` measures 18.35 from `MUT` and 20.14 from `INK`. **Neither moves the floor**, which
stays 13.99 at `ACCENT`/`VIOLET`.

### A-78 — `WARN`'s declared job loses *"or in flight"*, and this was a GATE BLOCKER

**Both lenses derived this independently, from opposite directions.** `LLR-S06.3.5` declares `WARN`
as *"pending, due, at risk, **or in flight**"*. Once `PULSE` owns *in progress*, `mapper/app.py:879`
classifies under **both** — and that same LLR's threshold is *"sites classifying as **both** `== 0`"*.
**The census cannot be satisfied by any implementation while the clause stands.**

**Before:** `WARN #ffd230` — *outstanding attention*: work is pending, due, at risk, **or in
flight**, and nothing has failed.
**After:** `WARN #ffd230` — *outstanding attention*: work is pending, due, **or at risk**, and
nothing has failed.

Dropping three words **narrows** `WARN`, so the one-job constraint is strengthened rather than bent.
`:1127-1130` already saw this from the other side and answered by retoning; nobody struck the clause.

**Censused cost: exactly two sites**, and the second was previously unfiled — see A-79.

### A-79 — the exception register is **2** after Inc-1, not 1, and the second entry is a new finding

`LLR-S06.3.2`'s threshold reads *"After Inc-1: **1** registered entry (`factory.py:104`)"*. Executed
over the derived severity set, narrowing `WARN` makes a **second** site unclassifiable:

```
mapper/views/lane.py:67   return Text.assemble(("<U+25D0>", darkside.WARN), (" run", darkside.WARN))
```

A **running** step painted in the severity hue — `#D10`'s defect exactly, one file over, adjacent in
the same view to `risk` and `late` which are also `WARN` (`lane.py:16-17`). An operator in the lane
view cannot tell *machine busy* from *you are late* by colour.

`mapper/views/lane.py` is **not** in Inc-1's declared file set, so it takes the mechanism `#D10`
itself established for `factory.py:104`: **registered as known-open, closed by the increment that
owns the file** — `Inc-5`, which owns `views/lane.py` at 3 of 4 source files. The stale-exception
guard reddens if `Inc-5` forgets.

**Before:** *"After Inc-1: **1** registered entry … After Inc-9: **0**."*
**After:** *"After Inc-1: **2** registered entries (`factory.py`'s tag, `lane.py`'s running step).
After Inc-5: **1**. After Inc-9: **0**."*

### A-80 — `COERCION_RANGES`' C0 row was INCOMPLETE, and adopting it verbatim NARROWED shipped coverage

**§3.0's range table is wrong, and the shipped suite caught it.** The row is labelled *"C0 except TAB
and LF"* and enumerates `U+0000`–`U+0008`, `U+000B`–`U+000C`, `U+000E`–`U+001F` — which also omits
**`U+000D CARRIAGE RETURN`**. Its own count gives it away: **29** points, where C0 minus TAB and LF
is **30**.

The shipped `_CONTROL_MAP` covered CR. Deriving the map from the declared ranges as written therefore
**removed** that coverage, and a CR in a ficha title would have reached the terminal, where it
returns the cursor to column 0 and overprints the row already painted.
`tests/test_darkside.py::test_plain_replaces_every_c0_control_except_tab_and_newline` went RED.

**Recorded because it is the more useful half:** the Phase-0 probe reported this group as `29 / 29
covered` — it agreed because it was fed **the spec's own ranges**, validating the list against
itself. The independent oracle was the shipped test, not the measurement.

**Before:** `(0x0000, 0x0008), (0x000B, 0x000C), (0x000E, 0x001F)` — 29 points; TOTAL **84**.
**After:** `(0x0000, 0x0008), (0x000B, 0x001F)` — 30 points; TOTAL **85**.
**Uncovered-at-pre-state is unchanged at 22**, because CR was already covered by the shipped map.
Verified as a strict widening: 85 declared points, **0** survivors through `plain()`, **0** shipped
points lost, **22** newly covered, `U+0009` and `U+000A` still preserved.

### A-81 — `LLR-CNV.1.4`'s tone set is INJECTED, not imported, because the module map forbids the import

`LLR-CNV.1.4` requires `rows()` to validate a layer value against *"the design module's declared
token set"*. **`docs/ARCHITECTURE.md:120` declares `canvas` with `Depends on: —`** — *"Canvas is the
lowest-level drawing primitive"* — so `canvas → design` is not an allowed edge.

**Resolution, which changes no requirement's meaning:** `Canvas.__init__` takes `tones` and
`fallback`, and `views/radial.py` — which already imports `darkside` on an allowed edge — supplies
`darkside.tone_set()`. **The guard still lives in `rows()`**, which is what the LLR actually requires
and what defeats `M-V1` (a write-time setter misses `radial.py`'s direct `cv.dots[...] = hue`
assignment). Left unset the parameter applies no policy, so every Canvas built elsewhere keeps
today's behaviour byte-for-byte.

Chosen over amending the map because `docs/ARCHITECTURE.md` already owes the un-landed `ARQ-1`
amendment (`PLAN.md` §7), and a second concurrent edit to the same row is how a cross-artifact
contradiction is created to remove an intra-document one.

### A-82 — *"semantic token pairs"* is now DECIDABLE, which `HLR-S06.2`'s addendum required and did not supply

The addendum's floor quantifies over *"all semantic token pairs"* and never defines the class.
Executed: over **all** declared tokens the minimum is **3.20** (`GROUND`/`PANEL`) — below the stated
floor of 10 — while over `{INK, MUT, ACCENT, WARN, ALERT, SAGE, TEAL, VIOLET}` it is **13.99**
(`ACCENT`/`VIOLET`) and `ACCENT`/`TEAL` is **20.18**, both reproducing the addendum's own figures
exactly. **The surfaces were never in the set**; the addendum simply never said so.

**Added:** `darkside.SURFACES = frozenset({GROUND, PANEL, STEP, WORDMARK})`, with the semantic set
derived as `tokens() - SURFACES`. **The pairs stay derived** (`C-31`); only the four-name class
boundary is written down, and it carries a measured guard — surfaces top out at `WORDMARK` 0.0423,
semantics start at `MUT` 0.1714, a 4× luminance gap with nothing in it — so a mis-filed future token
reddens rather than silently moving the floor.

### A-83 — carries opened by Inc-1

| id | Carry | Owner |
|---|---|---|
| `B-38` | `views/lane.py:67` paints a running step in `WARN` — registered exception, retone to `PULSE` | `Inc-5` |
| `B-39` | `screens/factory.py`'s `.factory-tag` blue — the pre-existing `#D10` entry | `Inc-9` |
| `B-40` | The loading ladder's `PENDING` rung is `WORDMARK` on `PANEL` = **1.65:1**, below the 3:1 non-text threshold: a three-state indicator ships as a two-state one. Found by the ux lens, out of `#D10`'s scope | design batch |
| `B-41` | `MUT` and `WORDMARK` collapse to slot 8, and `ASH` and `PULSE` to slot 7, at the 16-colour rung — a third and fourth declared collision pair beside `ACCENT`/`VIOLET` and `SAGE`/`TEAL`. Not auto-reachable; `ASH` and `PULSE` never co-occur in a view | declared limit |
| `B-42` | `PULSE` sits 25.06 from `ALERT`, closer than `WARN` does at 45.36. Judged sufficient on a lightness separation of 0.50 vs 0.27; owed a read at 118 × 34 before the batch closes | PR-level ux |

**Test-path reconciliation (rule V-5).** The census landed in
`tests/test_darkside_census.py` rather than in `tests/test_darkside.py` as the *(provisional)*
`Executed verification` lines say; the register plus the CIEDE2000 derivation is ~300 lines and does
not belong inside a 16-test primitives file. `AT-007` and `AT-008` landed in the new
`tests/test_canvas.py`, `AT-007b` in `tests/test_radial.py`, `AT-009` in `tests/test_export.py`, all
as specced.

---

## Amendment set 4, PASS 2 — the Inc-1 GATE REVIEW response. 2026-08-28.

> Forced by two independent gate reviews. `code-reviewer` returned **BLOCK** on one HIGH;
> `security-reviewer` signed off Inc-1 with one MEDIUM gated pre-merge and raised two HIGHs outside
> this increment's change set. One of these amendments **retracts A-79**, which the code review
> proved wrong.

### A-84 — `COERCION_RANGES` is the Unicode CLASSES, not a hand-picked list

**This is `A-80` recurring one layer up.** `A-80` fixed one omission (`U+000D`) in one row. The
security lens then swept the whole table against Unicode's own properties and found the
*"Zero-width and invisible"* row **stops one code point short** of `U+2061` through `U+2064` — the
same *"stops short"* shape, in the adjacent row. Executed: **19 invisible code points reached the
exported SVG** while the suite was green, including `U+00AD`, six deprecated format controls and
points of the `U+E0000` TAG block.

**The TAG block is why this is not cosmetic.** Those 96 code points render as nothing in every
browser, editor and terminal, and each maps 1:1 onto an ASCII character. A ficha title can carry an
arbitrary hidden ASCII string into a client-delivered SVG — invisible to the operator who exports
it and to the client who opens it, and trivially recoverable by anything reading the file as text.

**Before:** 12 hand-picked ranges, 85 code points, chosen row by row from a threat list.
**After:** exactly `Cc ∪ Cf ∪ Zl ∪ Zp` minus `PRESERVED_CODE_POINTS = {U+0009, U+000A}` — 24
ranges, **235** code points. The literal-range form is kept for reviewability, and a test re-derives
the set from `unicodedata` and asserts equality **in both directions**, so a range that is short and
a range that over-reaches both redden.

**Why the class rather than a longer hand-list:** hand-picking produced two measured near-misses in
one increment. *"This code point is a format or control character"* is not this project's property
to define, and taking it from `unicodedata` removes the defect class rather than its two known
instances.

### A-85 — `darkside.time_row` coerces its own inputs

**The widest input surface in the product.** `time_row` assembled `name` and `note` into a painted
`Text` with no coercion. For repo-derived graphs those come from `git` — `mapper/github.py`
populates them from a branch name and a commit subject and author. **The input author is anyone who
has landed a commit in a repository the operator opens**, where every other uncoerced sink in this
tree is fed by a file the operator owns.

**Before:** `time_row` painted its arguments as given.
**After:** `name` and `note` are coerced **inside** `time_row`, not at the call site, so the next
caller cannot forget — the shape `hint_line` and `fit` already use.

### A-86 — `A-79` IS RETRACTED: the register is 4 after Inc-1, and `lane.py:67` was never an exception

**`A-79` was wrong.** It registered `mapper/views/lane.py:67` as busy-painted-as-severity on the
strength of its label, `" run"`. **The branch is `if state == "pending"` (`lane.py:66`)** — the CI
state is literally *pending*, which is `WARN`'s declared job verbatim. The site conforms. What is
actually wrong is that its label and its half-filled glyph both say *running* for a state that is
*pending*.

**This is reader-as-oracle inside a human judgement:** the site was classified by the string it
prints rather than by the condition that selects it, and a register whose rows are judged from
labels is a register that certifies labels.

**Before (`A-79`):** *"After Inc-1: **2** registered entries… After Inc-5: 1. After Inc-9: 0."*
**After:** **4** after Inc-1, and `lane.py:67` is not among them:

| Site | Why it does not classify | Closes in |
|---|---|---|
| `screens/factory.py` `.factory-tag` | `#D10`'s original entry — `ACCENT` on a label, not an affordance | `Inc-9` |
| `views/lane.py` `_progress_bar`'s behind arm | *behind* is neither failure nor blockage; the same file paints `"late": WARN` for the same concept | `Inc-5` |
| `views/lane.py` `_behind_chip` | same concept, same file | `Inc-5` |
| `views/layered.py` removed-node ghost | a removed node is **absent information**, which the palette assigns to `MUT` | `Inc-3` |

After `Inc-3`: 3. After `Inc-5`: 1. After `Inc-9`: 0. Every row names its owning increment and the
stale-exception guard asserts it, so the handoff is mechanical rather than a promise.

**`B-38` is restated:** `lane.py:67` is a **copy and glyph** defect, not a hue defect. Retoning it to
`PULSE`, as `A-79` prescribed, would have been wrong.

### A-87 — `AT-009`'s oracle no longer validates the list against itself

`AT-009` derived its banned set from `COERCION_RANGES` — the same constant `_CONTROL_MAP` is derived
from. `leaked == []` was therefore true **for any value of that constant**, provided the coercion ran
at all: a routing test wearing an acceptance test's name. Demonstrated: green while 19 invisible code
points reached the artifact it was asserting on.

**Before:** the banned set is expanded from `darkside.COERCION_RANGES`.
**After:** the oracle is `unicodedata.category(c) in ("Cc","Cf","Zl","Zp")` minus the declared
preservations — a property this project does not define — plus a positive control proving the same
unmodified oracle can report a non-absence. Executed: clipping a declared range now reddens
`AT-009`, which was impossible before.

### A-88 — carries added by the review response

| id | Carry | Owner |
|---|---|---|
| `B-43` | `LLR-S06.3.3` quantifies over the 8 blue **literal** sites and says so, but *"blue stays interactivity-only"* is a claim about all ~50 sites, including 42 symbolic `darkside.ACCENT` references. A requirement gap, not an implementation gap | design batch |
| `B-44` | `tests/test_repair_map_truth.py` pins the `canvas` row of the module map as **prose** and imports nothing, so it cannot observe `Canvas.__init__` and did not notice the signature change. Pin against `inspect.signature` | `Inc-2` |
| `B-45` | The two truncators disagree on a second axis: `darkside.fit` measures display **cells**, `radial.py` slices **code points**, so a CJK or emoji title mis-sizes its pill background | design batch |
| **`B-46`** | **`_ConfirmScreen` renders a ficha title through a markup-parsing `Static` on the archive confirmation.** A stray closing tag raises `MarkupError` while composing the dialog that gates subtree archival; `[@click=…]` injects a live action span. Not in `S-09`'s site list. **BATCH-CLOSE BLOCKER** | **→ `Inc-CONFIRM` (A-90)** |
| **`B-47`** | **`views/outline.py` and `views/lane.py` are uncoerced, and `outline` feeds `save_svg`.** `LLR-COERCE.2` is scoped verbatim to `views/layered.py::_fit`, so these belong to **no increment**. Measured: a hostile title through outline or layered writes an SVG that is **not well-formed XML** — and layered is the **default** renderer, so `AT-009`'s guarantee holds only in radial view. **BATCH-CLOSE BLOCKER** | **→ `Inc-3` (A-89)** |

---

## Amendment set 6 — INC-2 GATE REVIEW response. 2026-08-28.

### A-94 — `LLR-CNV.3.1`'s recorded pre-state `M-10` DOES NOT REPRODUCE (`B-51`)

**The requirement's numeric threshold is unmeetable on this tree, and the acceptance test was
passing because of the defect rather than in spite of it.**

`LLR-CNV.3.1` states: *"after 1 real `tab` press from the canvas, the field reads `"rail"`; after 2,
`"inspector"`. Pre-state measured (`M-10`): press 1 focuses `OutlineRail#map-rail`, press 2 focuses
`FieldInput#insp-title`."*

Executed on this tree, deterministically over three runs:

```
owners = ['rail', '', '', '', '', '', '']
ids    = ['map-rail', None, None, None, None, None, None]
```

**The real `tab` key does not move focus on `MapScreen`; it drops it.** The first sample is taken
before any press, so all four presses in the original acceptance contributed **no positive
evidence** — and its assertion (*"the owner changed"*) was satisfied by the transition
`rail → nothing focused`. A test passing because of the defect it should catch.

**Before:** the acceptance asserts the owner changed across four real presses.
**After:** the acceptance asserts the **derivation** — that `_focus_owner()` equals an independent
recomputation from `app.focused` — which holds whether or not anything has focus; and the
requirement's real threshold is pinned separately as a **strict xfail**, so it fails loudly the day
traversal is fixed rather than being quietly forgotten.

**Related measurement:** under parallel load `app.focused` is still `None` after **5 seconds** —
`MapScreen` sometimes focuses nothing at all. Any test requiring initial focus is flaky by
construction, which is why the arm no longer waits for it.

**Carried as `B-51`, routed to `qa-reviewer`.** It is a shipped interaction defect, not an Inc-2
regression: it predates the branch and `HLR-CNV.3`'s substance (the canvas dims when another region
owns the keyboard) holds independently of it.

### A-95 — carries added by the Inc-2 review

| id | Carry | Owner |
|---|---|---|
| ~~`B-51`~~ | ~~The real `tab` key drops focus on `MapScreen`~~ — **RETRACTED IN FULL BY `A-96`. Not a defect.** It was an artifact of the default 80 x 24 Pilot size, at which the rail and inspector are correctly auto-hidden. At 118 x 34 the chain is populated and `M-10` reproduces verbatim | **withdrawn** |
| `B-52` | With a modal pushed, `MapScreen._focus_owner()` returns `""` and the canvas paints the FOCUSED tone while not holding the keyboard. Contradicts `HLR-CNV.3`'s statement; no visible harm (the canvas is occluded), and the `""`-paints-focused conflation is the declared price of byte identity | design batch |
| `B-53` | `#map-canvas` is `can_focus=False`, so the declared owner `"canvas"` is unreachable through the real wiring and the focused tone is arrived at via `""`. `B-05`'s three-region framing implies the canvas should be focusable | design batch |
| **`B-62`** | **Length-based truncators overrun a CELL budget on wide characters.** `layered._vis_width` is `len(s)` — its own docstring says "Approximate visible width (simple: length, no CJK handling)" — so `_clip`/`_fit` budget in CODE POINTS while the surfaces they paint are budgeted in CELLS. Measured against the shipped `_clip`, each ratio taken from the SAME output as its cell count: a 16-code-point CJK title at budget 20 is returned **UNCUT at 32 cells (1.60×)** — `len ≤ 20`, so no truncation fires at all; a title of **21 code points or more** at that budget emits **39 cells (1.95×)**; at budget 2, **3 cells (1.50×)**. Opened by `S-B(+C)`'s `LLR-COERCE.2` budget arm; **re-id'd from `B-53` by confirmation pass 3b (`F13`), which found that id already occupied by the `can_focus` carry one row above** | later increment (owns `layered.py`'s width model) |
| **`B-54`** | **Every Pilot-driven interaction assertion must DECLARE its terminal size.** Two of this app's three regions are size-conditional (`_apply_region_visibility`), so an interaction test at `run_test()`'s default 80 x 24 is testing a two-region app. `A-96` records what that cost. Sweep the suite for interaction arms that do not set `size=` | `qa-reviewer` |

---

## A-96 — **`A-94` IS RETRACTED IN FULL. `B-51` IS NOT A DEFECT.**

**It was an artifact of the default Pilot terminal size, and `LLR-CNV.3.1`'s threshold reproduces
exactly as written at the batch's declared context of use.**

Executed across three sizes — same graph, same real `tab` key:

```
size        focus_chain                                          owners after 4 real tabs
80 x 24     []                                                   ['', '', '', '', '']
118 x 34    ['map-rail','insp-title','insp-state','insp-notes']   ['', 'rail', 'inspector', 'inspector', 'inspector']
140 x 45    ['map-rail','insp-title','insp-state','insp-notes']   ['', 'rail', 'inspector', 'inspector', 'inspector']
```

**Index 0 is the SETTLED pre-state, and the first published version of this table was not.**
`MapScreen.on_mount` schedules `call_after_refresh(self._park_focus)`, which sets focus to `None`,
while Textual's `AUTO_FOCUS` has already focused `#map-rail`. Sampled a single `pilot.pause()` after
`push_screen`, the screen is usually still in the `AUTO_FOCUS` state — **23 runs in 25** — so this
table first published `['rail','rail','inspector',…]`, which reads as though the first `tab` did
nothing.

**The conclusion is unaffected, and the correction is the point: this is the very class the
amendment exists to name, appearing inside the amendment.** Fourth instance. The acceptance arm now
settles twice and asserts `app.focused is None` before measuring, so the published pre-state and the
asserted one are the same state.

At **118 x 34** — `C-D27c`'s declared context of use — press 1 gives `rail` and press 2 gives
`inspector`, which is **`M-10` verbatim**. The empty chain at 80 x 24 is `_apply_region_visibility`
**working**: below `MIN_CANVAS_WIDTH` it auto-hides the rail and the inspector so the canvas keeps
the terminal, and a hidden widget is correctly absent from the focus chain. There was nothing to
traverse because there was nothing displayed.

**How a phantom reached a requirement amendment, stated plainly, because the mechanism matters more
than the mistake.** Every measurement behind `A-94` was taken at `run_test()`'s default 80 x 24 and
**none of them said so**. Three passes compounded it rather than catching it: the original
acceptance passed at that size for the wrong reason; the gate review correctly showed the assertion
was vacuous, and I concluded from that the *behaviour* was broken; the confirmation pass correctly
identified `focus_chain == []` as the mechanism — **also measured only at the default size** — and I
wrote it down as a root cause. **Nobody varied the one parameter that decided the answer.** Three
independent passes agreeing is not evidence when they share an unstated premise.

**This is `P-20` inverted, inside the batch that recorded `P-20`.** There, the suite ran only at
sizes where a real defect was absent; here it ran at a size that manufactured one. Same rule, two
instances, now carried as **`B-54`**.

**Retracted:** `A-94` in full · the `B-51` row of `A-95` · the "drops it, deterministically" claim
in `mapper/app.py::_focus_owner`'s docstring · the strict xfail, replaced by an arm that asserts the
declared threshold at 118 x 34 and **passes**.

**Kept, independently true:** `B-53` (`#map-canvas` is `can_focus=False`).

---

## Amendment set 5 — COORDINATOR RULINGS, 2026-08-28

> **Provenance, stated precisely.** These three rulings came from the **coordinating agent** on
> 2026-08-28, in response to the Inc-1 close report, and they extend a scope sealed at the PDR. They
> are recorded as **coordinator rulings, not operator approval** — a different thing, and one the
> merge gate still requires: the independent security sign-off and the adversarial PR-level
> `qa-reviewer` pass over the whole diff both stand unchanged, and a HIGH still blocks the merge and
> returns to the operator.

### A-89 — `LLR-COERCE.2` widens from ONE named truncator to EVERY renderer feeding an operator-visible sink (`B-47` → `Inc-3`)

**What this closes is that the batch's security story was conditional on which view the operator
happened to be in.** `AT-009` asserts the exported SVG carries no coerced code point, and it does —
through `RadialRenderer`. But `LayeredRenderer` is the **default** renderer and `OutlineRenderer`
also reaches `export.save_svg`; measured, a hostile title through either writes an SVG that is **not
well-formed XML**. A guarantee holding in one of three views is not the guarantee the requirement
states.

**The narrowing was never in the Statement — it was in the `Touched symbols` line**, and that is the
transferable lesson: the requirement read *"Every function that truncates a string destined for a
painted surface…"*, which is already general and already correct. The scoping line beneath it named
`views/layered.py::_fit` and its six call sites, and the scoping line is what an increment builds to.

**Before — `Touched symbols`:** `mapper/views/layered.py::_fit` (`layered.py:38`) and its call sites
at `:217`, `:227`, `:237`, `:247`, `:266`, `:280`. `mapper/darkside.py::fit` unchanged.

**After — `Touched symbols`, and the threshold with it:**

> Every renderer that emits file-derived text to a surface an operator can see — the terminal **or**
> an artifact `export.save_svg` writes — shall route that text through the design module's coercion
> before it is truncated or painted. **The set of such renderers shall be DERIVED** from the tracked
> product sources, by finding every module that reads a `Ficha` field and returns a `rich.Text`
> reached by a renderer call site — never named by hand.

**Owning increment: `Inc-3`**, which already owns `views/layered.py` and `LLR-COERCE.2`. Its budget
absorbs `views/outline.py`. **`views/lane.py` enters only if the derivation shows it reaching a
sink** — which the increment shall establish rather than assume.

**The threshold is the derived renderer set, not three names.** A hand-listed set of renderers is
the same defect class as a hand-listed code-point list, and this batch has now paid for that twice
(`A-80`, `A-84`). A fourth renderer added later must enter the census automatically or the guarantee
decays the same way again.

### A-97 — `Inc-3`'s breach widens from FIVE files to SIX: `views/state.py` was owed by two sealed LLRs and named by no cut

**The breach was already arithmetically true when `A-89` was written; only the declaration was
missing.** `A-89` widened `Inc-3` to five files for the `B-47` coercion fold. It did not notice that
**three `ViewState` fields the increment cannot ship without** were already assigned to `Inc-3` by
LLRs sealed at the PDR:

- `LLR-N06.1.1:1696` — `ViewState.pan_x`, `ViewState.pan_y`, both `NEW — created in Phase 3`, and
  the Statement is explicit that the offsets travel *"as fields of the view state"*;
- `LLR-N06.2.1:1782` — `ViewState.folded`, likewise `NEW — created in Phase 3`.

**This is `#D5` §4.1(a)'s defect class exactly** — the undeclared breach that section caught on
`Inc-7` — and it is recorded here rather than discovered at the gate as a sixth file in the diff.
**An undeclared breach is what `V9` exists to catch; a declared one is a decision.**

**It is NOT an A3 and does not re-open the sealed PDR.** `mapper/views/state.py:17-20` states the
governing rule in the module's own docstring: *"ADDING A DEFAULTED FIELD BELOW IS ADDITIVE AND NEVER
RE-OPENS THE A3 … the roster is pinned here, once, and grows by default-carrying addition
thereafter. Only the first migration is an A3."* All three fields carry defaults
(`pan_x: int = 0`, `pan_y: int = 0`, `folded: frozenset[str] = frozenset()`), so `ViewState()` still
constructs with no arguments and every existing construction is untouched. `IRenderer.render`'s
signature, member set and return type are unchanged.

**Provenance:** raised as escalation 1 by the `Inc-3` architect ruling
(`02j-inc3-painted-set-architect.md`), which measured it while ruling a different question.
Recorded as an orchestrator ruling under the batch's standing autonomy grant, not as operator
approval.

### A-98 — how the renderer declares its painted set (`02j`), and the hole that ruling measured

**`HLR-N06.3` and `LLR-N06.3.1` are keyed on a `declared_painted_set` that NO requirement gave a
mechanism.** Grep at `954f8f3`: the phrase occurs only inside the predicate statements themselves
(`:2108-2114`, `:2279`). Ruled, because the mechanism decides whether trigger **A3** re-fires:

> **A module-level pure function `painted_ids(graph, state) -> frozenset[str]` in
> `mapper/views/layered.py`**, sharing one private `_geometry(graph, state)` pass with
> `LayeredRenderer.render` so the two cannot drift. `IRenderer` gains **nothing**; `MapScreen`
> imports it by name behind an explicit, greppable branch — **never** a
> `getattr(renderer, "painted_ids", None)` probe, which is a silent-skip generator.

**`LLR-N06.3.1`'s `Touched symbols` ambiguity is resolved with it:** *"consumes `MapScreen.folded`"*
means the screen puts `MapScreen.folded` into the `ViewState` it hands to `painted_ids` — **not**
that the helper takes a second set and differences it. The screen computes
`frozenset(graph.nodes) - painted` and subtracts **no fold count anywhere**, which is
`LLR-N06.3.1`'s Statement read literally.

**The three rejected candidates were rejected on executed measurements, not preference:**

| Candidate | Verdict | The measurement that killed it |
|---|---|---|
| a second **Protocol member** | **IS an A3** | `IRenderer` is `runtime_checkable` (`state.py:74`), which checks **member presence**: adding one flips **all six** shipped renderers to `isinstance -> False`, reddening `test_a3_census.py:316` over a derived class set. A defaulted member does not rescue them — the default reaches only classes that *explicitly inherit*, and all six are structural |
| a **mutable attribute** set by `render` | **measured wrong** | `MapScreen` holds one long-lived renderer (`app.py:1116`) and calls `render` from two sites at different sizes. Executed: after the canvas repaint at `30x6` the attribute holds 1 id; after one `e` export at `140x45` it holds 8 — so **one `e` press makes the indicator declare `0 hidden` on a canvas hiding 7.** It also breaks `LLR-N06.1.1`'s purity acceptance |
| the screen **re-deriving from geometry** | **is `M-N06.3-b`** | `_tree_layout` returns *placed* positions; `lines[:h]` (`:302`), `body_h` (`:173`) and `avail` (`:160`) each discard placed nodes afterwards. Executed on `legacy` at `(30,6)`: layout keys 8, visible 1 — **wrong by 7 of 8**, at `HLR-N06.3`'s own "hidden by viewport" configuration |

**MEASURED HOLE, carried under `B-55` — `outline` and `radial` hide nodes and declare nothing.**
Executed full-title traces at `30x6` on `legacy`: **outline 5/8** (3 hidden, undeclared),
**radial 2/8** (4 hidden, undeclared). `HLR-N06.3`'s promise is therefore kept in the **default**
view and silently unkept in the other two. `Inc-3` does not close it — it **declares** it and ships a
**pinned participation census** (derive the modules under `mapper/views/` exporting `painted_ids`,
assert the set non-empty *before* evaluating, assert equality with `{layered}`) so the day a second
renderer joins, the pin goes red rather than the guarantee quietly widening or quietly not. Closing
it is routed to **`Inc-5`**, the only increment that already owns all three of those files
(`#D5` row 5) and can pay for it with no budget.

**`AT-015`/`AT-016` MUST enforce all four configurations as a CARDINALITY ASSERTION, not as four
tests an implementer is trusted to run.** Executed at `(50, 12, ())` — the "nothing hidden"
configuration, and the first row of the table — **two of the three mutants are GREEN on all three
predicates**:

```
    config mutation   |declared|  |traced|  PRED-1  PRED-2  PRED-3
50x12     CORRECT             8         8   True   True   True
50x12     MUT-1               0         8   True   True   False
50x12     MUT-A               8         8   True   True   True     <- placed-not-painted SURVIVES
50x12     MUT-B               8         8   True   True   True     <- dropped column restriction SURVIVES
30x6      CORRECT             1         1   True   True   True
30x6      MUT-1               0         1   True   True   False
30x6      MUT-A               8         1   True   False  True
30x6      MUT-B               0         1   True   True   False
```

Only `(30, 6)` discriminates `MUT-A` and `MUT-B`. **The four-configuration table at `:2196-2199` is
not belt-and-braces — an `AT` that runs only its first row cannot fail on two of the three named
mutants**, so the test asserts it drove four configurations and fails if it drove fewer.

### A-90 — `B-46` gets its own increment, `Inc-CONFIRM`, sequenced with `Inc-REPAIR`

`_ConfirmScreen` renders a ficha title through a **markup-parsing** sink while composing the dialog
that **gates subtree archival**. Same newly-reachable-destructive-action class as `Inc-REPAIR`'s two
defects, and the fix is the `darkside.plain` the same function already applies seven lines above.

**Named `Inc-CONFIRM`, not a number**, for the reason §5.4 gives for `Inc-REPAIR`: a numeric id
collides under a substring scan (`grep "Inc-1"` matches `Inc-10`), and this document is corpus an
id-scanner reads.

| Inc | Scope | Source files | n |
|---|---|---|---:|
| **`Inc-CONFIRM`** | `B-46` — the archive-confirmation markup sink | the module owning `_ConfirmScreen`, established by the increment | **1** |

**Two acceptance arms, one per failure mode**, because they fail independently and one arm would let
the other ship:
1. **the crash arm** — a title carrying an unbalanced closing tag does **not raise** while the
   confirmation dialog is composed;
2. **the injection arm** — a title carrying an action directive paints **literally**, with no live
   action span in the rendered output.

**Ordering:** with `Inc-REPAIR`, before `Inc-7`. `Inc-7`'s sala loads every map on mount, which is
what makes these paths newly reachable with zero operator action.

### A-91 — PACE CALIBRATION, recorded so the post-mortem can judge it

**Full protocol** — independent review **plus** a confirmation pass on any post-fix tree, plus a
mutation battery — is retained wherever the increment touches a data path, a destructive action, the
A3 contract, or a security sink: **`Inc-2`, `Inc-3`, `Inc-REPAIR`, `Inc-CONFIRM`, `Inc-7`.**

**Lighter protocol** — a single independent review, no confirmation pass — is permitted for a
genuinely presentational increment, **and only while both conditions hold**: the review returns
**zero HIGH**, and the increment touches **no data path**. **Any HIGH restores the full protocol for
that increment.** Candidates: `Inc-8`, `Inc-9`, and `Inc-5` if its hit-painting proves purely
presentational.

**Batteries are sized to the predicates that exist and are never skipped.** The calibration trades
review passes, not evidence.

**Recorded as a decision rather than applied silently**, so the post-mortem can measure what the
lighter lane cost: the honest test is whether any defect found later would have been caught by the
confirmation pass that lane skipped. Inc-1 is the control — its confirmation pass found **7 MEDIUM
and 6 LOW**, including a fabricated measurement in production source and a "fix" that repaired
nothing, so the pass is not ceremonial and the calibration is a real trade.

## Amendment set 7 — INC-CONFIRM. 2026-09-18. Base `a552783` (`feat/ui-next-batch-02`).

### A-99 — an export encodes no transient view state: `B-68`, and its parent is `Inc-2`'s `H2`

**Parent, cited rather than asserted.** `Inc-2`'s finding `H2` ruled that `action_export_svg` pins
`focus_owner=""` **because an export is a standalone artifact that must not encode where the
keyboard was** (`03-increments/increment-002.md`, `H2`; the reviewer's form at
`increment-002-code-review.md:134`; its RED counterfactual at
`increment-002-retraction-check.md:231`). This amendment is that ruling applied to the **other**
piece of transient view state in the **same expression**, and the family relationship was
**verified in code rather than taken on trust** (`C-43`): `focus_owner=""` was normalised by a
`replace()` wrapped around the very `_view_state(max(20, size.width), max(5, size.height - 10))`
call that carried `pan_x`/`pan_y` through unreplaced. One expression; one piece of transient state
neutralised and the other riding along. **We ruled the principle and shipped half of it.**

**The defect (`B-68`).** The export read the live pan and sized the render from the **terminal**
rather than the canvas, while `layered._geometry` shrinks `card_w` at that wider width until the
tree fits — collapsing `max_pan_x` to 0. An offset perfectly legal on the canvas was therefore out
of range for the export and shifted content off the artifact's left edge. **Measured on the
`pan_graph` fixture at the declared 118×34 context: 47,263 bytes at pan (0,0) against 16,718 at the
reachable pan (49,10)** — roughly 65% of the map missing from a file handed to a third party, with
nothing declaring it, reachable with no view change (`pan to the edge, press e`). Proven
pre-existing byte-identically against a simulated pre-`S-D` clamp, so it is a **declared deviation**
from this batch's repair-only-what-is-newly-reachable rule, on the three grounds recorded at
`state.json::p3_progress.open_blocks[B-68].RULED_IN_SCOPE_2026-09-18`.

**The statement.** The artifact `mapper/export.py::save_svg` writes **shall** be a function of the
graph and the view mode alone — never of the session's scroll position or of which region held the
keyboard. Concretely: the export **shall** render the **full extent**, so that two exports of the
same map at any two pan offsets are **byte-identical**.

**Why full extent rather than a clamp.** The security reviewer drafted a two-line clamp against the
export's own geometry. It stops the content loss and **still encodes a scroll position** in a
standalone artifact, which is the thing the parent ruling forbids. Full extent **removes** the state
instead of bounding it. If an *"export what I am looking at"* mode is ever wanted, that is a
separate deliberate feature and its crop is **declared in the artifact**.

**The `S-15` hazard was named in advance and MEASURED before implementing**, because cost follows
paths rather than nodes and an unbounded extent would have refuted the direction. It does not:
`pan_extent` settles after exactly **one** growth step on every shape probed — the pan fixture,
200- and 1000-long chains, 200/500/4001-wide fanouts, and 50 nodes carrying 400-character titles.
Full-extent cost over **that probe set**: the real fixture 120×36 / **52,915 B** / 0.00 s;
`chain-1000` 120×4004 / 2.37 MB / 0.31 s; `fanout-4001` (Inc-4c's shape) 48013×35 /
**9.82 MB / 14.42 s**.

> **⚠ BOUNDARY OF THE TABLE ABOVE — read it before quoting any row.** Every figure in it is an
> honest measurement **of the shape it names**, and the set is **NOT a worst case**: it varies one
> dimension at a time and contains no map that is wide **and** deep together, which is the shape that
> actually maximises cost. The convergence claim survives that gap — one growth step on every shape,
> and the independent pass reproduced it at two — but the *cost* claim did not. The corrected worst
> case is below, and it is ~500× the largest row here.

**Acceptance.** Two arms, and neither is sufficient alone:

| Arm | What it refuses |
|---|---|
| `tests/test_pan.py::test_b68_the_export_is_invariant_under_the_operators_pan` | the state being *bounded* rather than *removed* — byte-equality across two genuinely different pans is the only predicate that separates them, and it is RED on the rejected clamp-only fix |
| `tests/test_pan.py::test_b68_the_export_carries_nodes_the_viewport_could_not_hold` | invariance satisfied by exporting *nothing* — two empty artifacts are byte-equal |

Both carry the `_pan_is_live` positive control, because on a fixture where pan cannot move,
"the two exports agree" is green by construction (`measured ≠ pinned`). Both drive the **real `e`
chord** and read the artifact **back from disk** (`C-12`). The content arm asserts the **emitted
form** (`C-42`): Rich writes one `<text>` element per style run, so a literal search for `"rama 5"`
returns **0** matches on an artifact that plainly contains it, and **8** once the runs are
reassembled per `line-N` clip path.

**Executed counterfactual.** `R1` pre-fix revert → **2 failed**; `R2` the rejected clamp-only fix →
**2 failed**; shipped fix → 2 passed; restore sha256-verified byte-identical
(`0a842a67170c2bac26dbef3f9d12f819377a322abb5bafd3cdef2b70c1954fa2`).

**⚠ THE COST FIGURE FIRST PUBLISHED IN THIS AMENDMENT WAS FALSE, AND IS STRUCK.** It read: *a
full-extent export of a 4001-way fanout costs 14.42 s of render plus 1.52 s of write.* That number is
real but it is **not the worst case**, because the probe set behind it was hand-listed and omitted the
failing member (`C-31`): it swept fanout-only and chain-only shapes and never one that was **wide AND
deep at once**. Struck rather than annotated, so this document does not assert both.

**The measured worst case, from the independent security pass.** Export cost follows the map's
**bounding-box AREA**, not its node count — `mapper/canvas.py::Canvas.rows` walks a dense `w x h`
grid. Measured end to end: **20.0 s at 601 nodes**, **75.8 s at 1,201**, **169.1 s / 363 MB at
1,801**. The worst shape inside the product's own `MAX_RENDER_NODES = 12000` is wide and deep
together (fanout 6000 + chain 5999): a 72001 x 24004 canvas, **1.73 billion cells**, extrapolating to
**~125 minutes and ~16 GB of heap** — paid synchronously on the Textual message pump, with no
progress, no cancel and no confirmation, on a map the operator may have been handed rather than built.

**This is not a carry and it is not a licence to crop.** `IF_MEASUREMENT_REFUTES_FULL_EXTENT` made
this amendment conditional on precisely this measurement, and the measurement has now arrived from an
instrument that was not the author's. The number goes back to the coordinator. A cap that **refuses**
with a named toast is not a crop and remains available; a cap that silently shrinks the artifact is
the defect `B-68` closed, and is refused.

**⚠ AND THE FIX AS WRITTEN DOES NOT YET DELIVER THIS AMENDMENT'S OWN STATEMENT.**
`mapper/export.py` builds the export console at a hard-coded `width=200`. A full extent is 241
columns at 21 nodes, so above roughly seventeen leaves Rich **folds** every row into stacked chunks in
row-major order: the artifact keeps every title, stays a well-formed SVG, and **loses the tree's
adjacency**. That is this amendment's own failure class — complete-looking, structurally lying — one
layer below the one it closed, and the acceptance arms miss it because their fixture's full extent is
120 columns, under the threshold. **`A-99` is NOT SATISFIED by the current tree.**

## Amendment set 8 — INC-CONFIRM, re-ruled. 2026-09-19. Base `a552783` (`feat/ui-next-batch-02`).

### A-100 — SUPERSEDES `A-99`'s extent clause: the export is bounded, and above the bound it REFUSES

**`A-99`'s principle stands; its DIRECTION does not.** The statement *"the artifact is a function of
the graph and the view mode alone — never of the session's scroll position"* is unchanged and is
still the acceptance. What is withdrawn is the clause that followed it — *"the export **shall**
render the **full extent**"* — which is **STRUCK, not shadowed**, on the same terms as every other
re-cut in this batch. The clause was made conditional in its own text
(`IF_MEASUREMENT_REFUTES_FULL_EXTENT`), the measurement arrived from an instrument the author did not
build, and the clause fired.

**The statement, as it now reads.** The artifact `mapper/export.py::save_svg` writes **shall** be a
function of the graph and the view mode alone. Concretely: two exports of the same map at any two pan
offsets, with any search live and the cursor anywhere, **shall** be byte-identical; the export
**shall** render every node's card inside the artifact **up to a declared area budget**; and above
that budget it **shall** write **nothing at all** and tell the operator why.

**Two grounds for refusing rather than rendering, and the second is the one that closes the
question.** *Cost*: export cost follows the map's **bounding-box AREA** — `Canvas.rows()` walks a
dense `w × h` grid — so the worst shape inside the product's own `MAX_RENDER_NODES` prices at roughly
125 minutes and 16 GB on the message pump. *Utility*: a 72001×24004 SVG is unreadable by anybody, so
"full extent always" produces something nobody wants. An off-pump render with progress and a cancel
answers only the first, buying the operator the ability to wait for and then abort a useless file;
it is rejected.

> **A REFUSAL IS NOT A CROP, and the distinction is the whole of `B-68`.** The defect is *a file that
> looks complete and is not*. Producing nothing and saying why preserves that principle exactly;
> producing a truncated, best-effort or silently-shrunk artifact reinstates it. There is no
> partial-artifact path out of `_export_view_state` — including its exhaustion branch, which refuses
> for the same reason rather than shipping whatever it had reached.

**The budget is in CELLS, and the derivation is normative — SUPERSEDED BY AMENDMENT SET 9**, which
**STRIKES** the per-cell arithmetic this clause carried and re-grounds the same constant. The text
below is the amended clause; the struck arithmetic is quoted only inside set 9, where it is named
false. `MAX_RENDER_NODES` bounds the wrong magnitude in this seam — a 1,801-node map that is wide
*and* deep carries roughly 23× the **cells** of a 4,002-node map that is only wide, and costs several
times the wall clock despite holding fewer than half the nodes — which is `S-15` recurring one seam
over. `EXPORT_MAX_CELLS = 350_000`, and **what justifies it is UTILITY — not a time guarantee.**

> ⚠ **The time claim that stood here is STRUCK by amendment set 10** — the SECOND strike of this
> constant's justification, for a different reason than the first. It read: *"what justifies it is
> the worst shape the budget ADMITS … the worst accepted shape (1,000 wide, 312,026 cells, at the
> `size.height - 10` start a 35-row terminal gives) costs 1.447 s against the 2-second target … a
> margin of about 28 %, and nothing the budget admits crosses the target"*, together with a
> *0.955–3.27 µs/cell, 3.4×* spread. **The universal is false.** The hunt behind it varied graph
> shape while holding the **start height** fixed — and the start height is `max(5, size.height - 10)`,
> set by the operator's terminal, and it is the governing variable for how much node **density** a
> fixed cell budget admits. Measured clean, the worst **admitted** shape is `1.91 s` at a 40-row
> terminal, `2.41 s` at 35 rows (the very terminal the struck sentence was measured on), `5.94 s` at
> the classic 80×24, and `17.73 s` at 11 rows. **A cells-only budget cannot express a time bound at
> all**: cost depends on `w` and `h` separately while this constant constrains only their product, so
> no value of it makes the universal true.

⚠ **This clause's own replacement sentence is STRUCK IN TURN by amendment set 11** — the THIRD false
claim of this family. It read *"at start heights of about 30 rows and up the worst admitted shape
stays under 2 s, and below that it rises monotonically as the terminal shortens."* Both halves are
false: the safe side breaches at its own boundary (4 of 9 runs over 2 s, reproduced; 7 of 9
independently), because the figure behind it was a **minimum** rather than an upper quantile; and the
curve **plateaus** rather than rising, because the start height floors at 5.

**No fourth number replaces it.** What is asserted instead is clockless and is the mechanism:
**the same map is admitted or refused depending on the operator's terminal** — a 3,645-wide fanout
fits the budget at start height 5 and is refused at 30. Heap is not the binding constraint.

**The refusal names the route, not only the number.** The toast carries the measured extent in cells,
the limit, and *"Enfoca un subárbol con `f` y exporta esa vista"*. `f` really does focus a subtree —
verified in code, not assumed — so a refused export leaves the operator with a path rather than a
dead chord.

**Acceptance — `A-99`'s two arms stand, and four more are added.**

| Arm | What it refuses |
|---|---|
| `tests/test_pan.py::test_b68_the_export_is_invariant_under_the_operators_pan` | the state being *bounded* rather than *removed* (unchanged) |
| `tests/test_pan.py::test_b68_the_export_carries_nodes_the_viewport_could_not_hold` | invariance satisfied by exporting *nothing* (unchanged) |
| `tests/test_export_state.py::test_an_oversized_map_is_REFUSED_and_no_artifact_is_written` | a budget that crops, truncates or ships a best-effort picture — the assertion is the **absence** of the artifact, which a toast-only check would not make |
| `tests/test_export_state.py::test_the_refusal_TELLS_the_operator_and_names_the_way_forward` | a refusal that is silent, or that states a number without a route |
| `tests/test_export_state.py::test_an_ordinary_map_still_exports` | the cheapest way to pass the two above: refuse everything |
| `tests/test_export_state.py::test_an_extent_that_never_settles_REFUSES_instead_of_shipping_what_it_had` | an exhausted extent shipping what it had reached, with no pan to blame |

**And the transient class is closed as a CENSUS, not as the two fields a reviewer happened to
notice.** `focus_owner`, then the pan offsets, then `selected_id` and `hits` were each found one at a
time by a different reader over three increments — a ruling about a *class* discharged as a handful
of instances. `mapper/views/state.py` now classifies **every** `ViewState` field, the export derives
its strip set from that table, and the classification is asserted **both ways** and **pinned**:
`tests/test_export_state.py::test_every_view_state_field_is_classified_for_the_export_boundary` and
`::test_the_transient_fields_are_the_ones_that_say_where_the_operator_was`. A field added to
`ViewState` without a row now fails an arm rather than inheriting its neighbour's behaviour.

**`hits` is the security half, and it is why this is not tidiness.** It is the resolution of whatever
the operator last typed into search, down to a per-branch numeral on every fold pill — information
about the **sender**, leaked to the recipient of a file. A deliberate *"export with the selection
marked"* mode is a separate feature whose inclusion is declared **in the artifact**.

**⚠ THE `width=200` DEFECT ABOVE IS CLOSED, and its threshold was reproduced independently.**
`save_svg` sizes the console from the `Text` it is handed, measured in terminal **cells**. On the
artifact: no fold at 16 leaves (197 columns), **3 of 5 rendered rows folded at 20 leaves** (245
columns) under the old constant, and **0 of 5 at every size** under the measured width. `A-100` is
satisfied by the current tree; `A-99`'s unsatisfied-warning is discharged by this amendment rather
than deleted from it.

**⚠ ONE MEDIUM REMAINS OPEN AND IS NOT CLOSED BY THIS AMENDMENT.** The export grows the canvas far
enough to include the `eliminados` diff ghost strip the screen was not showing, so a previous
revision's node titles can leave the machine in a file the operator believed showed only what they
could see. It is reachable today (`=` to diff, `e` to export, on any map taller than the canvas) and
it wants a one-line ruling — either this amendment states the inclusion as deliberate, or the strip
is suppressed for an export state. **Silence is what is not enough**, and this line is here so the
silence is not mistaken for a decision.

---

## Amendment set 9 — `A-100`'s cost derivation STRUCK. 2026-09-19. Base `f3398f4` (`feat/ui-next-batch-02`).

### `A-100.1` — the constant stands; the arithmetic that justified it does not

**Authority.** Coordinator ruling 2026-09-19, on findings raised independently by both independent
passes of increment 016 — `code-reviewer` `N4` (the symptom) and `security-reviewer` `S-F9` (the
mechanism) — and re-measured by the implementer because **the two reviewers' conclusions disagreed by
6×** and a budget cannot be ruled on from either alone.

**What is struck.** Every per-cell derivation `A-100` and `mapper/app.py` have carried. Two were
written in turn:

1. *"4.907 µs/cell, so 2.0 s / 4.907 µs = 407,616, round down to 400,000."*
2. *"A measured bracket: 315,252 cells → 1.801 s and 490,052 → 2.631 s, so 2.000 s falls at 357,156,
   round down to 350,000; cross-checked by a through-origin fit at 5.4264 µs/cell."*

**Why struck rather than annotated, and this is the load-bearing sentence.** The second was not a
faithful record taken under an undeclared condition — **it was the first defect re-run**. Both
figures came from the same harness (`sec_b68_real_cost.py`, then `b68_budget_probe.py`), which calls
`tracemalloc.start()` on the line *before* it takes `t0`, so an allocation profiler ran inside the
entire timed region and inflated every point by **5.3–5.6×**. Measured clean, that bracket's own
shape costs **0.301 s**, not 1.801 — reproduced independently at 0.321 s and 0.331 s by the two
reviewers. A requirement whose *normative* clause is false must not stand even when its conclusion is
right: a right answer resting on a false derivation invites the next reader to re-derive from the
broken premise.

**What replaces it.** ⚠ **This paragraph's own replacement was STRUCK IN TURN by amendment set 10 —
read that before relying on anything here.** It grounded the constant on *"the worst shape the budget
ADMITS (1.447 s against a 2-second target, ≈28 % margin)"* with a *0.955–3.27 µs/cell, 3.4×* spread.
That universal is **false**: the hunt behind it held the start height fixed, and the start height is
set by the terminal and governs admitted density. The constant now rests on **utility alone**, and
the time guarantee is **withdrawn rather than restated**. What survives from this paragraph is the
narrower and still-true observation that the per-cell rate varies with node density, which is *why*
the two passes disagreed: wide-and-deep is cheap per cell, wide-only is dense and expensive, and each
sampled one family. A proposed relaxation to ≈2.12 M cells is
**REFUSED** — it generalises from the cheap family and would admit wide-only maps costing many
seconds.

**`A-100`'s utility ground is untouched and stands alone.** A 72001×24004 SVG is unreadable by
anybody whatever it costs to produce, so the ruling never rested on the arithmetic — which is exactly
why striking the arithmetic costs the ruling nothing.

> **Note on the `125 minutes and 16 GB` figure in `A-100`'s *Two grounds* paragraph.** It comes from
> the same contaminated harness, so the **time** is inflated by the same 5.3–5.6× (really ≈23
> minutes); the **heap** figure is unaffected, since `tracemalloc` measures memory correctly even
> while distorting the clock it shares a region with. The ground survives either reading — ≈23
> minutes of uninterruptible freeze plus a multi-GB allocation refuses the shape just as decisively —
> so the conclusion stands and the number is corrected rather than the clause withdrawn.

### `A-100.2` — a refusal declares the stale artifact it leaves behind

**Authority.** Coordinator ruling 2026-09-19 on `N2`, raised by `code-reviewer`.

Refusing to write leaves whatever the **last** export wrote sitting at the very path the success
toast names. The operator is told the export declined; without more they are not told the file still
there is **old** — which is `B-68`'s own shape (*a file that looks current and is not*) one seam over,
and is recorded as the **sixth** instance of *the increment that closes a defect family is the
increment most likely to introduce a member of it*, **with its mitigation stated**: the operator was
told the export refused, just not that the old file persists. Partial mitigation is still an instance.

The refusal toast therefore **shall** name the path and state that the file there is from a previous
export. It **shall not** delete it: the standard is that nothing is hidden without being *declared*,
not that nothing stale exists, and deleting the operator's file on a refusal without confirmation is
the destructive act `US-N05` already rules against — silently deleting would break a standing ruling
in order to soften a lesser one. The sentence is **conditional**, because "the file there is stale"
is a claim about the world and a map's first export has no file to be stale.

**Acceptance — two arms, because the claim has two failure modes.**

| Arm | What it refuses |
|---|---|
| `tests/test_export_state.py::test_a_refusal_DECLARES_the_stale_artifact_it_leaves_behind` | a refusal that leaves an undeclared stale artifact. Its fixture **exports first**, which is the case the budget arm is structurally blind to — that arm `unlink()`s before pressing, so it runs in a world where no prior artifact ever existed |
| `tests/test_export_state.py::test_a_refusal_on_a_FIRST_export_claims_no_stale_file` | the cheapest way to pass the arm above: appending the sentence **unconditionally**, which would tell the operator something untrue |

### `A-100.3` — two instrument gaps closed, both the same shape

| Finding | What was wrong | Arm |
|---|---|---|
| `S-F10` | `save_svg` measures in terminal **cells** (`cell_len`), which is correct and was **unpinned** — substituting `len()` left 45 tests green while a CJK title folds a row at every shape. Two conjuncts of the width expression were already mutated; this was the third, and no arm could see it | `test_no_rendered_row_is_folded_in_the_artifact` gains wide-glyph parametrisations (`枝`, `分岐`) |
| `S-F11` | The AST spawn census read **positional** argv only, so the identical undeclared spawn **failed** the census written positionally and **passed** it written `subprocess.run(args=[...])`. `SEC-F6` had already taught the runtime guard this exact lesson and the census deriving its population was not told | `test_the_spawn_census_sees_an_undeclared_binary_in_EITHER_SPELLING`, parametrised over both spellings and driving the **real** census function over a synthetic tree, plus a positive control so an empty walk cannot read as clean |

Both are the batch's signature shape — **a lesson applied to an instance and not to its class** —
landing in the instrument rather than in the product.

---

## Amendment set 10 — `A-100.1`'s REPLACEMENT is struck too. 2026-09-19. Base `152ecd9`.

### `A-100.4` — the budget's time guarantee is withdrawn; the constant stands on utility alone

**Authority.** Coordinator ruling 2026-09-19 stands; this amends its *implementation*, on
`code-reviewer`'s finding `CR17-F1` (HIGH) against increment 017, **independently reproduced by the
implementer before being accepted**.

**What is struck.** The replacement clause written by amendment set 9 — *"what justifies it is the
worst shape the budget ADMITS … 1.447 s … a margin of about 28 %, and nothing the budget admits
crosses the target"*, and the *0.955–3.27 µs/cell, 3.4×* spread quoted beside it.

**Why, and the reason is not the previous reason.** Set 9 struck the *first* derivation because the
**instrument** was contaminated (`tracemalloc` inside the timed region). The instrument was fixed —
and the **search** was left holding a governing variable fixed. `_export_view_state` starts at
`h = max(5, size.height - 10)`: the start height comes from the operator's **terminal**, and it
decides how much node **density** a fixed cell budget admits. A shorter terminal gives a smaller
`h`, so `w × h ≤ 350_000` admits a far **wider** map — and width is what costs. The hunt varied
graph shape across two families at two **tall** heights and then generalised over the whole region.

**Measured clean, worst ADMITTED shape per terminal** (reproduced by the implementer; figures agree
with the reviewer's to within a few percent):

| Terminal | start `h` | worst admitted | cells | cost | vs 2 s |
|---|---|---|---|---|---|
| 118×40 | 30 | 940-wide | 349,711 | **1.91 s** | under |
| 118×35 | 25 | 1,121-wide | 349,778 | **2.41 s** | 1.2× over |
| 80×24 | 14 | 1,944-wide | 349,935 | **5.94 s** | 3.0× over |
| 118×20 | 10 | 2,651-wide | 349,943 | **10.38 s** | 5.2× over |
| 118×11 | 5 | 3,645-wide | 349,928 | **17.73 s** | 8.9× over |

It is over target at **80×24, the classic default**, and over target at **the very terminal the
struck sentence was measured on**. The reviewer additionally drove it end to end through the real
`e` chord at 80×24: a 1,945-node map is **accepted**, writes a 4.6 MB artifact, and freezes the pump
**7.5 s**.

**`C-31` AT THE SEARCH RATHER THAN THE INSTRUMENT, and it lands on the increment that minted the
corollary forbidding it.** Set 9 minted *"a correction that changes the number but keeps the
instrument has not corrected anything"*, with the corollary that *a conclusion drawn from one family
of inputs is not corrected by re-measuring that family more carefully*. Increment 017 then did
exactly that, one variable over. **Correcting how you measure does not correct what you measured
over** — and catalog entry 2 (*a newly minted control does not protect the increment that minted
it*) is proven for the second time in two increments, both times on its own minting increment.

**What replaces it.** Nothing, on the time axis: **the guarantee is withdrawn rather than restated
at a new number.** A cells-only budget **provably cannot** express a time bound, because cost
depends on `w` and `h` separately while `EXPORT_MAX_CELLS` constrains only their product — so no
value of the constant makes the universal true, and picking a smaller one would repeat the mistake a
third time. ⚠ **What was asserted instead — *"at start heights of about 30 rows and up, the worst
admitted shape stays under 2 s; below that it rises monotonically as the terminal shortens"* — is
ITSELF STRUCK by amendment set 11**, which is the third false claim of this family and the reason no
number of any kind now appears. See `A-100.6`.

**`EXPORT_MAX_CELLS = 350_000` STANDS, on the UTILITY ground**, which has been untouched through
both strikes and never depended on the arithmetic: a 72001×24004 SVG is unreadable by anybody
whatever it costs to produce. The proposal to relax the budget to ≈2.12 M cells remains **REFUSED**.

**OPEN, and routed to the coordinator rather than settled here:** whether the freeze is to be
genuinely *bounded* — which needs a different bound (a `w`-aware or time-aware check, or moving the
render off the message pump), not a different constant. That is a ruling, and the implementer
declines to choose it.

### `A-100.5` — the refusal's stale-file sentence said more than its guard established

**Authority.** `code-reviewer` finding `CR17-F2` (MEDIUM), reproduced by the implementer.

`A-100.2` required the stale-file claim be conditional *"so it can never be false"*. The guard was
`path.exists()`, which establishes **existence**; the sentence said *"ya no refleja este mapa"*,
which claims **staleness**. Those are different claims. Measured: export a map, change **nothing**
about the graph, then make the same map exceed the budget — the artifact on disk is still a faithful
export of that exact graph, and the refusal called it stale.

The sentence now says only what `exists()` licenses: *"No se escribió nada: el archivo en `{path}`
es de una exportación anterior."* Whether that file still matches the map is something the code does
not know and must not assert. **Telling the operator a current file is stale is the same category of
error as letting them believe a stale file is current** — both are the artifact misdescribing
itself, which is the family `B-68` names.

**Acceptance gains a third arm**, because the existing negative control covered only the *no-file*
mode and so could not see this:
`tests/test_export_state.py::test_a_refusal_does_not_call_a_CURRENT_artifact_stale` — the claim must
be **true** whenever it is made, not merely **absent** when there is no file.

---

## Amendment set 11 — the third strike, and the last number. 2026-09-19. Base `e6045a9`.

### `A-100.6` — no safe-side time claim; the MECHANISM is pinned instead

**Authority.** Coordinator ruling 2026-09-19 (1); `code-reviewer` finding `CR17-F6` (MEDIUM),
reproduced by the implementer before acceptance.

**What is struck.** *"At start heights of about 30 rows and up, the worst admitted shape stays under
2 s; below that it rises monotonically as the terminal shortens."*

**Both halves are false.** The safe side breaches **at its own boundary, on the very narrow-title
family it was derived from**: at start height 30, 4 of 9 runs exceeded 2 s (min 1.321, median 1.890,
max 2.139) reproduced here, and 7 of 9 with a median of 2.059 measured independently. And
"monotonically" is false because the start height **floors at 5**: terminals of 15, 12 and 11 rows
all admit the identical shape (fan 3,645), so the curve rises and then **plateaus**.

**The root cause is a STATISTIC.** The 1.91 s behind the sentence was a **minimum**.

> **Best-of-N is the correct statistic for demonstrating a BREACH and the wrong one for demonstrating
> SAFETY.** If the minimum exceeds the bound, every run does — which is why the earlier HIGH stands
> *a fortiori*. If the minimum is under it, nothing follows about the rest. A worst-case claim must be
> established on an upper quantile.

**THE FAMILY IS THREE DEEP, AND EVERY LAYER WAS A SOUND FIX OF THE ONE BEFORE IT.** Set 9 struck a
contaminated **instrument**; set 10 struck a **search** that held a governing variable fixed; set 11
strikes the **statistic**. *Correcting how you measure does not correct what you measured over — and
correcting what you measured over does not correct which tail you quoted.*

**What replaces it: nothing numeric, deliberately.** Three claims of this family have been false, so
the replacement is **clockless** and is the mechanism all three were groping at:

> **The same map is admitted or refused depending on the operator's terminal.** A 3,645-wide fanout
> fits the budget at start height 5 and is refused at 30, because the budget bounds `w × h` while the
> start height is `max(5, size.height - 10)` — chosen by the terminal. That is precisely why a
> cells-only budget cannot express a time bound.

**Acceptance.** `tests/test_export_state.py::test_the_SAME_map_is_admitted_or_refused_by_the_TERMINAL`,
parametrised over two real terminal sizes and **driving the product's own `_export_view_state`**. It
holds no clock, so it cannot flake, and it is killed from **both** directions — raising the budget
reddens the refused row, lowering it reddens the admitted row.

> A timing arm was recommended at pass 1 and **withdrawn by the reviewer who recommended it**, on its
> own new data: it would re-assert in the suite a guarantee this requirement has just withdrawn, and
> it is flaky by construction (1.978–2.146 s across nine identical runs). The withdrawal is recorded
> because it is the better judgement, and because a recommendation retracted on measurement is worth
> as much as one made on it.

### `A-100.7` — the refusal claims nothing about who wrote the file

**Authority.** `code-reviewer` finding `CR17-F4` (LOW), sharpened at pass 2.

`A-100.5` justified the stale-file sentence as saying *"only what `exists()` licenses"* — and then
asserted an **export** wrote the file, which `exists()` does not license: a directory, or a file the
operator dropped at that path, would have been called a previous export. **This increment's own
stated principle, turned on it.**

Guarded by `is_file()`, which licenses *"el archivo"*, and claiming nothing about its author:
*"No se escribió nada: el archivo en `{path}` no corresponde a esta exportación."* Both halves are
true whoever put it there. Weakening the guard back to `exists()` reddens the negative control.

### `A-100.8` — the export DECLARES its wait

**Authority.** Coordinator ruling 2026-09-19 (1).

A UI that stops responding with no indication is this batch's own defect class applied to **time**
instead of content — hidden without being declared. Above `EXPORT_DECLARE_CELLS` the export
**shall** announce itself before rendering, naming the **extent** and promising **no duration**
(cost is not a function of cells; a cells-to-seconds claim would be the fourth false universal). The
budget is checked first, so a refusal never announces a wait it will not take.

> **The ruling's estimate of the cost was wrong, and it was measured rather than argued.** A notice
> that arrives after the freeze it warns about is an apology, not a declaration. Measured, paint time
> against work time: notify-then-block paints the toast **404 ms late**; `call_after_refresh`
> **403 ms late**; an `async` action yielding with `sleep(0)` **403 ms late**. Only a real yield
> paints first (**+50 ms**). **So declaring the wait DOES need async**, and `action_export_svg` is
> now async with a 50 ms yield. That is the whole of the cost.

**Acceptance.** `test_a_large_export_DECLARES_the_wait_before_it_freezes_the_pump`, parametrised over
a large map and a trivial one — the second row refusing the cheapest cheat, announcing every export,
which is how a declaration decays into noise.

**Off-pump with progress and cancel remains the real fix and is CARRIED to the design batch**,
alongside the render work-budget work, which is the same problem. **The earlier rejection of off-pump
does not transfer**: it was rejected when it bought the ability to wait for and abort a useless 16 GB
artifact. The artifact is now bounded and useful, so what off-pump buys has changed. **A ruling's
grounds expire when the situation it ruled on does.**

---

## Amendment set 12 — the vocabulary declaration moves to `Inc-7`. 2026-09-19. Base `3bf272c`.

### `A-101` — CUT AMENDMENT: `LLR-N16.2.1`'s declaration is CREATED by `Inc-7`, CONSUMED by `Inc-8`

**Authority.** Coordinator ruling 2026-09-19, on a structural dependency surfaced while opening
`Inc-7`. This amends the ratified cut, so it is recorded with its reason rather than applied.

**The dependency.** `LLR-N13.1.5`'s `PRED-VIS RESOLVED` requires the damaged-map glyph to be *"a
member of `declared_vocabulary`, asserted at run time"*. That declaration is created by
`LLR-N16.2.1` — *"a glyph-vocabulary declaration in `mapper/darkside.py` — NEW — created in Phase
3"* — and §5.4's increment table assigns `LLR-N16.2.1` to **`Inc-8`**, which follows `Inc-7`.

**A CLAUSE CANNOT DEPEND ON A DECLARATION THE NEXT INCREMENT CREATES.** Left as written, `Inc-7` has
three bad options and no good one: assert membership against a declaration that does not exist
(impossible), paint an undeclared glyph (reinstating precisely the defect `PRED-VIS` was written to
prevent), or create the declaration anyway while `Inc-8` still nominally owns it (two homes for one
declaration, which is the defect `LLR-N16.2.1` itself exists to forbid).

**The amendment.** The declaration is **created by `Inc-7`**, the increment that first needs it, in
`mapper/darkside.py` as `LLR-N16.2.1`'s *Touched symbols* already specify. **`Inc-8` CONSUMES it**:
the legend reads the declaration and asserts style equality and set equality against it, as
`LLR-N16.2.1`'s threshold already requires. **No requirement text changes** — only which increment
performs the creation. §5.4's table row for `Inc-8` is amended from *"the legend reads the seat and
the vocabulary declaration"* to *"the legend reads the seat and the vocabulary declaration, which
`Inc-7` creates"*.

**Why this direction and not the other.** Moving `LLR-N13.1.5` after `Inc-8` was rejected: the
damaged-card defect is live and operator-visible today, and `Inc-8` is a legend increment with no
reason to precede it. Moving the *creation* costs one file's ownership; moving the *defect* costs
the operator a lying card for an extra increment.

> **NO INCREMENT MAY ASSERT SET EQUALITY AGAINST A SET THAT DOES NOT YET EXIST**, which is the
> general form and the reason this is a cut amendment rather than a note. `Inc-7` creates the full
> derived set — all **22** rows of `declared_vocabulary`, not merely the row it paints — precisely so
> that `Inc-8`'s set-equality assertion has a complete subject on the day it runs. A declaration
> seeded with one member would make `Inc-8`'s threshold pass over a set of one, which is the
> hand-chosen-floor defect `QA-M-09` already superseded once.

**Consequence for `Inc-7`'s file budget, stated so the gate is not surprised:** `Inc-7` now touches
`mapper/darkside.py` in addition to `mapper/app.py`. Both are SOURCE files and the increment remains
within the cap.

### `A-102` — `LLR-N13.1.5`'s damaged predicate covers BOTH load paths, not one

**Authority.** Coordinator ruling 2026-09-19.

`LLR-N13.1.5` identifies a damaged map by the load path **raising** *or* **recording a load
warning** — two conditions. Measured at `3bf272c`, only the first reaches the card: `load_or_notice`
returns `None` on a raise, and the recents loop's `else` branch substitutes `concept, 0, 0`; on a
**load warning** it returns the graph and notifies through a **transient toast**, so the card is
truthful but the *warning* is gone the moment the toast clears, while the card is **permanent**.

**That is half the distinguishability defect, and it is the half that vanishes when the operator
looks away.** A clause satisfied for one condition and green for the other is not satisfied. Both
paths **shall** reach the declared card state.

---

## Amendment set 13 — the projection rule, ruled. 2026-09-19. Base `7c99df6`.

### `A-103` — a row projects to ONE MEMBER PER DISTINCT TRIPLE it names

**Authority.** Coordinator ruling 2026-09-19, on the ambiguity surfaced while implementing `Inc-7`.

**The question.** `LLR-N16.2.1`'s instrument says to *"project every row onto the triple
`(glyph, label, painted-in style)`"* and take the set of distinct triples. It does not say how a row
naming **more than one** style projects, and two rows do: `V19` (*filled `SAGE` at or above 90 %
coverage, else `INK`; empty `WORDMARK`*) and `V21` (*lit `MUT on PANEL`, unlit `WORDMARK on
PANEL`*).

**The rule, and it is determined by the requirement's purpose rather than chosen.**
`LLR-N16.2.1` exists so that **every visual form the product paints is declared** — and a form *is*
a triple, not a row. So **a compound row projects to one member per distinct triple it names.**
`V19` contributes three members; `V21` contributes two.

**Consequence, derived mechanically and not hand-listed:**

> ⚠ **THE COUNT BELOW IS RETRACTED. `25` IS THE FIFTH WRONG GENERATION OF THIS NUMBER**, and
> §5.2 / `A-07` had already warned that a fifth was coming. It was derived with a row regex of
> `(V\d+)` — **digits only** — and three faults follow from that and from not reading §5.2 first:
>
> 1. **`V4a` and `V4b` were silently skipped.** A lettered row id is still a row. With them the
>    table carries **24** rows, not 22.
> 2. **`V4b` is a THIRD compound row** — *"`MUT`; the path to the selected node in `ACCENT`"* — and it
>    appeared in neither the pending list nor the ruled projection's accounting.
> 3. **Two removals the rule depends on cannot be performed as the documents describe them**, which
>    is why no replacement number is offered here. See the conflicts below.
>
> **The RULE of `A-103` stands: a compound row projects to one member per distinct triple it names.**
> Only the arithmetic is retracted. **A fifth wrong number is not repaired by a sixth**, so the count
> is left UNDERIVED until the two conflicts are ruled.

#### Two artifact conflicts, SURFACED rather than averaged

**(a) `V4` and `V4a` are NOT byte-identical, though this document says they are.** §5.2 justifies
collapsing them on byte-identity *"both `∙ ∙ ∙` / `territorio sin explorar` / `WORDMARK`
(`01b:277`, `01b:287`)"*. Measured: `V4a`'s glyph cell is ``` `∙ ∙ ∙` (scattered braille,
`U+2800`–`U+28FF`) ```. They may well be the same *painted form* — the parenthetical reads as a gloss
— but that is a **judgement**, not the byte-identity the stated reason claims, and a dedupe rule
resting on a false premise cannot be executed mechanically.

**(b) `#D7`'s removal rule has NO SUBJECT in the source document.** `LLR-N16.2.1`'s instrument says
to *"remove every triple whose row carries the `DEFERRED(#D7)` marker"*, and §5.2 says `V18` *"carries
the `DEFERRED(#D7)` marker"*. Measured over `01b`: **zero** rows carry it. The only occurrence of the
string `DEFERRED` anywhere in `01b` is inside this batch's own Amendment 1, quoting the instrument.
**So the removal step has always been inert**, and `V18`'s exclusion rests on prose in a different
document rather than on a marker the instrument can read.

**Both are for the coordinator.** Either the markers are added to `01b` and the dedupe rule is
restated on a criterion that holds, or the instrument is amended to match the artifacts. **`Inc-8`'s
set-equality assertion cannot be written until one of those happens** — it would be asserting
equality against a set whose size nobody can derive twice and get the same answer.

> **THE ROW COUNT WAS NEVER THE RIGHT UNIT.** That is why *"any threshold written against the row
> count is wrong before it is run"* is true, and why **every threshold citing 21 or 22 is
> re-derived against the triple count rather than edited.** A threshold that counts rows counts the
> document's formatting; a threshold that counts triples counts the painted forms, which is what the
> requirement is about.

### `A-104` — the assertion is LAYOUT-INDEPENDENT, stated so nobody later thinks otherwise

**How the legend LAYS OUT a compound meaning — three tones on one line under one caption, or three
separate lines — is a UX decision and is queued for the operator.** It does **not** block `Inc-8`
and it does **not** change any arm.

**The reason, stated rather than left to be rediscovered:** `LLR-N16.2.1`'s threshold is asserted
over **painted triples**, derived from what the renderer and the legend each emit. A layout choice
changes how many *lines* carry those triples; it cannot change the *set* of triples. So the arm is
independent of the layout by construction.

**This matters because the opposite belief is the expensive one.** A reader who thought the
assertion depended on layout would hold `Inc-8` for a design verdict that cannot affect it — which is
precisely the coupling this batch has already paid for once, when a *defect* and a *tone* were nearly
bundled and had to be separated explicitly.

### `A-105` — the sparkline's zero-activity floor, and it does not depend on the calendar

**Authority.** Operator-directed corrective, 2026-09-28, discharging `INC7-CR-R3-F3` (round-3 review
of `Inc-7`, recorded in `increment-020-inc7-corrective-2.md`'s "Round 3" section and
`state.json`'s `p3_progress.NEW_FINDING_ROUTED_TO_OPERATOR`). Routed to the operator rather than to a
further `Inc-7` corrective pass, because fixing it touches `app.py`, which that round did not.

**Parent.** `HLR-N13.3` (the sala paints within a declared budget, and an unsummarisable map says so
on its own card), via `LLR-N13.1.6` (the sala loads at most once per map per mount), whose
touched-symbols line already names `mapper/app.py::HomeScreen._sparkline_text`.

**The gap.** No requirement in this document states what the 14-day activity sparkline paints when
the workspace has zero activity in the window. `_sparkline_text` computes
`max_count = max(counts) if counts else 1` (`app.py:575`) — `counts` always has 14 entries, one per
day, so the `else 1` branch can never fire. When every entry is `0` — no `.mmd` in the workspace was
modified in the last 14 days — `max_count` is `0`, and the division `c / max_count` (`app.py:579`)
raises `ZeroDivisionError`, crashing `HomeScreen` for any workspace idle two weeks or more. Measured
2026-09-28: this batch's own `fixtures/` directory (newest mtime `truncado.mmd`, 2026-09-11) is
already 17 days stale and reproduces the crash today, in the main working tree, on unmodified code.

**Statement.** A workspace with zero activity in the 14-day window shall paint a sparkline with every
day at the floor bar (`bars[0]`), and `HomeScreen` shall not raise. A workspace with a map modified on
the current day shall light exactly the last bar at the maximum tier (`bars[-1]`) — the zero-activity
guard shall not flatten real activity.

**Touched symbol.** `mapper/app.py::HomeScreen._sparkline_text` (the `max_count` computation at
`app.py:575`, guarding the division at `:579`). This amendment does **not** touch, and does not
license touching, the `14 x N_maps` glob-and-stat loop above it (`app.py:565-574`) — that cost is
`LLR-N13.1.6`'s own open clause (its numeric pass threshold on `glob` calls per mount), unrelated to
this defect, and restructuring it here would be undeclared scope.

**Validation.** `test (unit)` — `tests/test_sparkline_floor.py`, driving
`HomeScreen._sparkline_text` directly against a workspace whose `.mmd` mtimes are set explicitly (to
local noon of a chosen day, via `os.utime`) relative to `date.today()` at test time, not to a fixed
calendar date. Three arms: `test_a105_a_zero_activity_workspace_paints_every_bar_at_the_floor` (the
escaped-bug regression), `test_a105_activity_today_lights_exactly_the_last_bar` (the no-flattening
control), and `test_a105_two_days_of_activity_scale_relative_to_each_other` (`INC21-CR-F1`; activity
on two distinct days, proving `max_count` is the true maximum rather than a sum or a binary tier —
see `increment-021`'s "review round" section for its mutant proof). Plus the pre-existing
`tests/test_agree_floor.py` (whose 8 arms mount `HomeScreen` incidentally and share this crash as a
symptom).

**`INC21-CR-F5` — the limit of what `test_agree_floor.py` proves, stated so it is not overclaimed.**
`tests/test_agree_floor.py` exercises the zero-activity path only INCIDENTALLY: it mounts
`HomeScreen` because `MapperApp.on_mount` pushes it before the test pushes `MapScreen` (`INC21-CR-F9`), and it happened to hit `max_count == 0` only
because its checked-in fixtures were stale enough (17 days, when this was measured) to fall outside
the 14-day window. On a fresh checkout — every fixture's mtime at or near today — none of its 8 arms
reach `max_count == 0` at all, and it exercises nothing about this defect. The screen-level "shall not
raise" clause therefore rests on `test_a105_a_zero_activity_workspace_paints_every_bar_at_the_floor`,
which builds its own zero-activity fixture on purpose and calls `_sparkline_text` directly, not on
`test_agree_floor.py`.

**Numeric pass threshold.** `0` exceptions raised, and `14`/`14` bars at the floor glyph, on a
zero-activity workspace; exactly `1`/`14` bar at the maximum-tier glyph, and the remaining `13`/`14`
at the floor glyph, on a workspace with one map modified today. **`INC21-CR-F1`, added on review:** on
a workspace with two maps modified 3 days ago and one map modified today, `bars[-4]` is the
maximum-tier glyph (index `9` of `"▁▂▂▃▃▄▅▆▇█"`, `"█"`), `bars[-1]` is index `4` of that same string
(`"▃"`), and the remaining `12`/`14` bars are at the floor glyph — this is the threshold that
distinguishes the true maximum from a sum or from a binary tier, which the single-day thresholds
above cannot.

**Date-independence, stated so nobody re-derives it by hand later.** The product behaviour this
amendment defines is independent of the date the suite runs on: `tests/test_sparkline_floor.py`'s
fixtures set each `.mmd`'s mtime to LOCAL NOON of a day computed from `date.today()` at test time
(`datetime.combine(day, time(12))`), not to a pinned calendar date — noon rather than an offset off
`time.time()` so the stamp cannot land on the wrong side of midnight near a DST transition. So the arm
reproduces the same verdict on any date. This is deliberately narrower than `tests/test_agree_floor.py`'s
own pre-existing hermeticity defect — its fixtures are checked-in `.mmd` files with fixed mtimes, so
**that suite's result depends on the date it runs on**, which is what let `INC7-CR-R3-F3` escape
undetected until those fixtures' mtimes happened to drift past 14 days. That is a defect in
`test_agree_floor.py`'s own setup, separate from the product crash this amendment fixes, and this
amendment's new arms are not permitted to share it.

**`INC21-CR-F3` — the residual race, and the choice made about it.** Any arm that uses TODAY as an
activity day still calls `date.today()` twice: once when the fixture is built, once inside
`_sparkline_text` when it runs. If the calendar date changes between those two calls (the test
straddles local midnight), the expected bars would be computed for the wrong day. Rather than state
that window as an accepted bound, `tests/test_sparkline_floor.py` REMOVES it: every such arm
re-checks `date.today()` immediately after computing the bars and skips if it has moved. No arm in
this suite accepts an unbounded or merely-documented race.

**`INC21-CR-F4` — style tiers are unpinned; carried, not fixed here.** `_sparkline_text`'s
`style = darkside.WORDMARK if idx < 4 else darkside.MUT` split (`app.py:586`) has no requirement or
arm pinning which tier a bar's *style* (as opposed to its *glyph*) falls into. Out of this amendment's
scope — carried to `qa-reviewer` for the follow-on batch, not fixed by this pass.

---

## Amendment set 14 — the Inc-8 design pass retires vocabulary ids a threshold names. 2026-09-28. Base `9136a3f`.

### `A-106` — `PRED-4`'s discharge named `V7`, `V8` and `V4`; the ids now resolve to forms the product paints

**Authority.** Operator verdict `D2` (`VERDICT-inc8-legend-2026-09-28.md`: *"derivar el vocabulario
de lo que el producto pinta hoy; 01b se reescribe desde renders reales"*), applied in the Inc-8
design pass (`03-increments/increment-022-inc8-legend.md`, section *Design pass*). `01b` DECISION 3
§3.1–§3.4 was rewritten from a catalogue of real renders. Rows that described forms no renderer
paints were retired, and a retired id is never reused. The change log above `01b` §3.1 records every
old row and what became of it.

**The threshold that names retired ids.** `HLR-N06.3`'s `PRED-4` discharge reads *"`V7` and `V8`
move off `WORDMARK` to `INK`; `WORDMARK` keeps `V4`"*, and its named weaker variant
`M-N06.3-legibility` names `V7` and `V8` again. All three ids are retired. `V7` and `V8` were
prototype captions (`plegadas: … — 41 nodos`, `minimapa · 128 nodos`) that no renderer paints. `V4`
named a braille dust field the atlas canvas never draws.

**What the discharge's subjects are now, so the threshold keeps them.**

- The overflow declaration `PRED-4` exists for is `01b` row **`V31`** (`▽ N fuera de vista`). It is
  painted in **`INK`** at every site: `views/layered.py:451-454`, `views/outline.py:334`,
  `views/radial.py:121`, `app.py:2592`. `PRED-4` holds for it as ruled.
- The minimap caption `V8` has no painted successor. The strip under the tabs is a coverage strip
  (`V36`–`V39`), and its own count of undrawn branches (`+N ramas sin mostrar`) is painted in `INK`
  by `MapScreen._minimap_text`. Among the vocabulary rows, `PRED-4`'s *"every token carrying a
  declaration role, derived from `01b` DECISION 3"* therefore quantifies over `V31`.
- `#D28`'s decorative exemption, which `V4` relied on (*"lattice dots … carry no floor"*), now covers
  **`V21b`** (`·`, `WORDMARK`), the rail's unlit territory dot. That is the lattice dot the exemption
  always described.

**No statement changes and no threshold is loosened.** Only the ids the discharge cites are
resolved. The passages in `LLR-N16.2.1`, §5.2 and `A-103` that discuss `V4`/`V4a` byte-identity
describe the pre-rewrite table. They are history, and are annotated here rather than edited.

---

## Amendment set 15 — the docked legend runs full height. 2026-09-29. Base `29781d6`.

### `A-107` — `TC-R36`'s height cap: the DOCKED legend is exempt; the modal keeps the cap

**Authority.** Operator verdict round 2, item `E1` (`VERDICT-inc8-legend-2026-09-28.md`, section
*Round 2*): *"(a) panel angosto de ~44 columnas, alto completo, vocabulario primero + la vista no se
desplaza con la leyenda acoplada"*. The record's own reading of it: *"full height (needs a dated
amendment of the sealed `TC-R36` for the DOCKED layout only)"*. Applied in Inc-8 design pass 2
(`03-increments/increment-022-inc8-legend.md`, section *Design pass 2*). `A-107` was the next free id
after a scan of all of `.dev-flow`; `A-106` was the last taken.

**What is sealed, and where.** `TC-R36` belongs to the repair batch
(`2026-08-26-repair-batch/01-requirements.md`, trace row `US-R05` → `HLR-R05` → `LLR-R05.1`,
`LLR-R05.2`). It pins WHICH of `#help-dialog`'s two height declarations governs:
`max-height: 28` at `140x45` (28 rows), and `height: 90%` at `100x24` (21 rows). It was written
because the battery arm `L5` had been retired on a false "no-op" claim (`increment-004`, finding
`F2`). When it was written the legend had one layout, a centred modal.

**Why the docked layout is exempt.** Inc-8's verdict `D4` docks the legend on the right at
`>= 118` columns, and `E1` makes that docked panel narrow (44 columns) and **full height**, so that
it covers the ficha inspector whole instead of leaving an "L" of it beside a capped panel (`UX-F9`)
and keeps most of the canvas visible (`INC8-F-UX-F1`: the 80-column panel covered 44 of the
canvas's 58 columns at 118). `140x45` is now a docked size, so the cap cannot govern there: a
full-height panel is 45 rows. Holding the cap for the docked layout would contradict the operator's
verdict. Weakening `TC-R36` silently would contradict the sealed record. This amendment does neither.

**What changes.**

1. **Modal layout (below 118 columns): unchanged.** `max-height: 28` still governs on a tall
   terminal, and `height: 90%` still governs on a short one. The cap is re-measured at `100x45`, a
   modal width with the same 45 rows, where `90%` would give 40. That keeps `L5`'s question ("does
   `max-height` govern on a tall terminal?") for the layout that still has the cap.
2. **Docked layout (118 columns and wider): `height: 100%`,** exempt from `max-height`. `TC-R36`
   gains the node `docked-full-height`: at `140x45` the dialog is 45 rows, governed by
   `height: 100%`.
3. `LLR-R05.1`'s substance, that every binding is reachable when more exist than fit, is untouched.
   It is enforced by `TC-R24` and `AT-R12` in both layouts, and they stay green.

**What is not loosened.** The modal bound is the same number, still asserted. The docked bound is a
new, exact equality (the terminal's full height), not the absence of one.

## Amendment set 16 — the dock threshold is derived. 2026-09-29. Base `00915cc`.

### `A-108` — SUPERSEDES `A-107`'s width clauses: the legend docks while the view keeps a minimum

**Authority.** Operator verdict round 3, item `F9` (`VERDICT-inc8-legend-2026-09-28.md`, section
*Round 3*): *"derivar el umbral del ancho de lienzo que queda visible junto al panel de 44 (acoplar
mientras quede un mínimo útil)"*, and the round's design principle: behaviour derives for any width,
since operators zoom the terminal. Applied in Inc-8 design pass 3
(`03-increments/increment-022-inc8-legend.md`, section *Design pass 3*). `A-108` was the next free id
after a scan of all of `.dev-flow`; `A-107` was the last taken.

**What is superseded.** `A-107` wrote its two layouts as *"below 118 columns"* (modal) and *"118
columns and wider"* (docked), after verdict `D4`. Those two width clauses are replaced; nothing else
in `A-107` changes.

**The rule now.** The legend docks while at least `LEGEND_DOCK_MIN_VIEW_CELLS` columns of the view
stay visible left of the 44-column panel (`mapper/screens/help.py::docks`), and is the modal
otherwise. The switch width is therefore derived: `44 + LEGEND_DOCK_MIN_VIEW_CELLS` plus whatever
chrome the host paints left of its view, which is the map's rail when shown. The minimum is one
declared number, proposed as `43` and put to the operator as `INC8-D3-Q1`; with it the switch is at
`87` columns for a view starting at column 0 (the home screen, or a map whose rail is auto-hidden)
and at `111` for a map showing its rail. The reference width, `118`, docks either way.

**Consequence for `TC-R36` (repair batch, sealed).** `A-107` re-measured the modal's cap at `100x45`.
At `100` columns the legend now docks, so the two modal nodes move to the widest modal width over a
map opened there, `44 + 43 - 1 = 86`, derived in the arm from the same two constants:

1. `cap-governs`: `86x45`, 28 rows, `max-height` (where `90%` would give 40).
2. `percentage-governs`: `86x24`, 21 rows, `height: 90%`.
3. `docked-full-height`: unchanged, `140x45`, 45 rows.

Each node now also asserts the layout it measures, so a threshold that moves again reddens the arm
instead of silently measuring the other layout.

**What is not loosened.** The same three expected heights, the same two declarations under test, the
same row counts. Only the width a modal is measured at moved, because the width that is modal moved.

## Amendment set 17 — while the legend is docked, the legal pan range is the visible canvas. 2026-09-29. Base `74e1e20`.

### `A-109` — `LLR-N06.1.2`'s legal pan range, while the legend is docked, is computed on the VISIBLE canvas

**Authority.** Operator verdict round 4, item `G2` (`VERDICT-inc8-legend-2026-09-28.md`, section
*Round 4*): *"enmendar LLR-N06.1.2: mientras la leyenda está acoplada, el rango legal usa el lienzo
visible"*, closing the carry `INC8-D3-F2` and its question `INC8-D3-Q2`. Applied in Inc-8 design
pass 4 (`03-increments/increment-022-inc8-legend.md`, section *Design pass 4*). A scan of all of
`.dev-flow` found no `A-109`; `A-108` was the last id taken.

**What is amended.** `LLR-N06.1.2`'s statement stands unchanged for every layout except one case:
while the legend is DOCKED, the legend's own reveal (`MapScreen._pan_revealing_selection`, verdict
`F2`) computes its legal maximum against the canvas columns VISIBLE left of the panel, not the
canvas's own full drawn width. Before this amendment, the reveal's clamp used the same span as an
ordinary pan (`geo.avail`, the full canvas), so a card whose pan was already at that OLD legal
maximum -- the map's own right edge -- could not be panned any further, and stayed partly covered by
the panel even though the panel already occupies that space on screen regardless of where the pan
sits. The docked panel's own width, `LEGEND_DOCKED_CELLS`, never changes what the canvas ITSELF
draws (`_chrome_width` does not count it); it only occupies screen columns the operator cannot see
past. The old clamp reasoned about the drawn width as if all of it were visible, which was false the
whole time the legend is docked.

**The rule now.** For the ONE call `_pan_revealing_selection` makes to `_clamp_pan`, the span is
`panel_x - canvas_x` (the columns actually visible left of the panel) instead of `geo.avail` (the
canvas's full drawn width); `extent_x` (`E`) is unchanged. `_clamp_pan` itself is untouched -- it is
still `max(0, min(offset, max(0, extent - span)))` -- and every OTHER caller (`_pan`, `_apply_region_visibility`'s repaint, the bare `LLR-N06.1.2` arms) still passes the full `(extent, span)` pair
the ordinary pan always has. Practically: an edge card that a docked panel used to leave partly
covered can now be panned fully clear of it, because the extra room the panel itself already
occupies on screen is exactly the room the widened clamp legalizes.

**The declared margin (`G5`).** The reveal aims for the card's right edge to land
`REVEAL_MARGIN_CELLS` (2) columns short of the panel, not flush against it -- a separate, smaller
declaration read by the same call, honoured whenever the (possibly widened) legal range leaves room
for it. At the map's own true right edge the widened range has no slack left to give the margin
(the card's true content boundary IS the legal maximum), so the margin there is exactly 0; this is
`LLR-N06.1.2`'s own existing "no blank space past the content" principle, not a defect in the margin.

**On close.** Unchanged. `legend_closed` keeps the pan it captured the instant the legend opened
(`_pan_before_legend`) and `on_screen_resume` restores that EXACT value -- neither reads
`_pan_revealing_selection` nor the widened clamp. The amendment governs one call, made only while
docked; the return path never calls it.

**What is not loosened.** Every `LLR-N06.1.2` arm outside the docked reveal -- the bare clamp's own
unit arms, `_pan`'s keyboard panning, the modal layout's pan-preserving path -- is unchanged and
keeps the OLD range, `[0, max(0, extent - avail)]`. The modal layout never calls the amended call at
all (`legend_docked(None)` skips `_pan_revealing_selection`), so nothing about it moves.

---

**Addendum, 2026-09-29 (closing verdict round 5, item `H3`).** The paragraph above headed *"The
declared margin (`G5`)"* read the map's own true right edge as a case where the margin is honestly
0 -- `LLR-N06.1.2`'s existing "no blank space past the content" principle, not a defect. The
operator's closing answer to `H3` (`VERDICT-inc8-legend-2026-09-28.md`, section *Round 5 — closing
questions*: *"2 columnas pintadas en todos los casos"*) withdraws that reading for this one case.
The original paragraph is left standing above, unedited, as the record of what was believed at
design pass 4; this addendum is what governs now.

**What changes.** `_pan_revealing_selection`'s clamp widens the legal maximum it hands to
`_clamp_pan` by `REVEAL_MARGIN_CELLS` (2), on top of the visible-canvas span this amendment already
substitutes for `geo.avail`. Concretely: `_clamp_pan(target, extent_x + REVEAL_MARGIN_CELLS,
visible_span)` rather than `_clamp_pan(target, extent_x, visible_span)`. This is the SAME kind of
widening the amendment above already makes for the span -- room the docked panel already occupies
on screen regardless of where the pan sits -- applied to the margin instead. At the map's own true
right edge the pan can now move `REVEAL_MARGIN_CELLS` columns past where the content itself ends,
so the card's own last painted column still lands the full margin short of the panel, the same as
every other card. `_clamp_pan` itself is still untouched, and every other caller still passes the
unwidened `(extent, span)` pair; this is the second and last thing this one call's clamp does
differently from an ordinary pan.

**The off-by-one this addendum travels with.** Design pass 4 measured the margin by comparing
`canvas_x + card_x + geo.card_w` (the box's DECLARED width) against the panel's edge, not by
counting the frame's own painted columns. A card's title row never paints that box's last column
when the row carries no change chip (`views/layered.py`: `title_w = card_w - 3`, two columns short
of the box's own right edge) -- the box is `card_w` columns wide, but only `card_w - 1` of them are
ever ink. Measured on the composited frame: the old code painted 3 blank columns between an ordinary
card's own last glyph and the panel, and only 1 at the map's true right edge (the old margin-is-0
case, above) -- neither was the declared 2. `_pan_revealing_selection` now reads the box's last
PAINTED column (`geo.card_w - 1` past the card's own left edge) rather than one past it, and the arms
in `tests/test_legend_design.py` assert the margin on the COMPOSITED FRAME -- counting blank painted
columns between the card and the panel -- rather than on the geometry the implementation itself
reads, so a future regression that only re-derives the same wrong geometry cannot pass by agreeing
with itself.

**Correction, 2026-09-29 (Inc-8 follow-ups, `INC8-FU-F4`).** The paragraph immediately above says
`_pan_revealing_selection` "now reads the box's last PAINTED column (`geo.card_w - 1` past the
card's own left edge)" -- imprecise. `right` (`canvas_x + card_x + geo.card_w - 1`, the ordinary,
no-diff-chip case) is ONE COLUMN PAST the last column this call treats as painted; the actual last
painted column is `right - 1`. The clamp still lands the declared margin, because `right` is used
consistently as a one-past boundary by the call that reads it, not as the painted column itself --
but the docstring and this addendum both named the wrong one. `INC8-FU-F1` (follow-up, non-blocking
at Inc-8's close) additionally found that "the box's own last column is declared width, not painted
ink" is a claim about the NO-DIFF-CHIP case only: a card carrying a diff chip (toggled with `=`)
DOES paint that column, WARN, so `_pan_revealing_selection` now reads `state.diff.changed.get(cursor)`
to tell the two cases apart before deciding which column `right` names.

---

## Amendment set 18 -- repo hygiene: no tracked file names the operator's real account. 2026-09-29. Base `037c733`.

### `A-110` -- no tracked file shall contain an absolute user-profile path naming a real account

**Authority.** Operator-directed hygiene corrective, 2026-09-29: *"Limpia el usuario de los
registros en un incremento propio."* Closes the identity half of backlog carry `B-22` ("Operator
identity and a Claude session UUID inside the `.dev-flow/**` battery transcripts") -- the
session-UUID half of `B-22` is untouched by this amendment and remains open.

**Parent.** None. A scan of §3's HLRs found no fit: `HLR-REPAIR.1` is the nearest candidate (it bars
a filesystem path from an operator-facing MESSAGE the product's store raises at runtime), but its
surface is the product's own runtime output to whoever opens `mapper`, not this repo's own
`.dev-flow/` process records read by whoever clones a PUBLIC repo. Different actor, different
surface, different channel -- widening `HLR-REPAIR.1` to cover it would put a repo-hygiene rule
under a product HLR, the same kind of collision `#D5` already exists to prevent for source
ownership. This is therefore a standalone hygiene requirement, carried by its own test rather than
by any HLR/LLR chain.

**The gap.** No requirement in this document governs what a tracked file may say about the identity
of whoever runs this batch. Measured 2026-09-29, before this amendment's guard test existed: the
operator's real Windows account name appears in 249 lines across 70 tracked files, almost entirely
under `.dev-flow/` (battery transcripts, review docs, increment records, `state.json`, one file
under `prototypes/`, and both root handoff files), naming the account inside an absolute
`C:\Users\<operator>\...` path. The repo is public; the operator asked for this explicitly.

**Statement.** No file tracked by `git` shall contain an absolute user-profile path (in any spelling
of drive letter, one or two backslashes or a forward slash, `Users`, a separator, then a name
segment) whose name segment is a real account. Such a path shall instead be written with a declared
placeholder (`<operator>`, or the generic `<user>` / `<USER>` / `<username>` already in use, or
`%USERPROFILE%`) or must be a declared, non-identifying test fixture. Declared exemptions, each with
its own reason, live beside the check in `tests/test_no_operator_paths.py::ALLOWED_PATH_SEGMENTS`:
`<operator>`, `<user>`, `<USER>`, `<username>`, `OP` (a reviewer-constructed probe path, not an
account), `secret]click[` / `secret` (one hostile markup-injection fixture, captured twice under
different quoting), and `%USERPROFILE%`.

**Touched files.** No product source. This amendment governs `.dev-flow/**` process records,
`BACKLOG.md`, both root handoff files, and the one affected file under `prototypes/`.

**Validation.** `test (unit)` -- `tests/test_no_operator_paths.py`, two arms:
`test_a110_no_undeclared_user_profile_path_in_any_tracked_file` (hermetic; reads only the declared
allow-list, never the environment) and `test_a110_the_real_operator_username_appears_nowhere`
(reads the real account name from `$USERNAME` at run time -- never hardcoded -- and skips cleanly
where that variable is unset). See `03-increments/increment-023-scrub-operator-paths.md` for the
RED-before counts, the scrub, and the mutation battery that proves each arm can fail.

**Numeric pass threshold.** `0` tracked lines with an undeclared user-profile path segment, and `0`
tracked files containing the real account name, once `$USERNAME` is available to check it.

**What is not claimed.** This amendment governs the working tree only. The real account name
remains in git HISTORY on the public remote (every commit already pushed to `origin`, including
`master`) -- removing it there needs a history rewrite and a force push, which the operator has not
authorized, and this amendment does not ask for one.

---

## Amendment set 19 -- ficha text is coerced at graph entry, and `store.save()` degrades to a toast (G6). 2026-09-29. Base `3611c20`.

### `A-111` -- ficha string fields are coerced at graph entry (load and mutation), and every `store.save()` call site degrades to a toast

**Authority.** Operator verdict, Round 4, `VERDICT-inc8-legend-2026-09-28.md` § "Round 4", `G6`,
verbatim: *"micro-incremento propio justo después de Inc-8: limpiar los campos de ficha al entrar al
grafo y proteger los 6 guardados."* Closes `INC8-P3-SEC-F1` (Inc-8 pass-3 security review, MEDIUM):
`mapper/store.py`'s persistence path handles raw, uncoerced strings, and 6 of 8 `store.save()` call
sites in `mapper/app.py` have no guard.

**Parent, stated honestly rather than assumed -- it does not fit in one piece.**

- **The load half widens `LLR-STO.1.1`** (external, shipped, `.dev-flow/2026-08-27-repair-batch-
  02/01-requirements.md:114`; parent `HLR-STO.1`). That LLR already requires `MapStore.load` to
  "apply the scalar-coercion ladder to every text position" `_build_sidecar` serialises -- but its
  ladder (`mapper/store.py::_coerce_field`) coerces TYPE only (scalars to `str`, containers refused).
  A lone surrogate is already a `str`: it passes threshold 1 of `LLR-STO.1.1` untouched and reaches
  `_reindex`'s sqlite3 bind, raw. This amendment widens that ladder, AT THE STORE BOUNDARY ONLY, to
  additionally route every coerced text position through `darkside.plain()`'s declared
  `COERCION_RANGES` table (`HLR-COERCE` / `LLR-COERCE.1`, this batch, §3.0) -- reusing the one
  declared list, not a second one. This is a widening of an already-shipped requirement, not a new
  one, following the precedent this document already set for `LLR-N13.1.7` (a new LLR that
  references `LLR-STO.1.1` rather than redefining it).
- **The mutation half has no existing parent, and none was forced.** `LLR-STO.1.1`'s position census
  is derived by walking `_build_sidecar`'s OUTPUT shape -- it governs `load` (and, transitively,
  anything that round-trips through `_graph_from_sidecar`, which covers `_pop_snapshot`'s undo path
  for free). It says nothing about a `Ficha` field set directly from a UI event BEFORE any
  serialisation happens, which is the surface `mapper/app.py`'s six mutation sites are. `HLR-COERCE`
  itself does not fit either: its own text rules it out by construction -- "this HLR has no parent
  story... a product-wide control whose subject survives the descoping of every story", scoped
  explicitly to a PAINTED surface ("what would reverse the no-parent-story ruling: evidence of a
  `notify` or paint site inside `mapper/views/` or `mapper/widgets/`"). `mapper/app.py`'s mutation
  sites are neither a paint site nor a `views`/`widgets` module. So the mutation half is declared
  standalone here, the same way `A-110` stood alone for repo hygiene: carried by its own test, not by
  an HLR/LLR chain.
- **The save-guard half has no parent at all, and is a different KIND of requirement.** Coercion is a
  content transform; degrading a raised exception to a toast is an availability/containment
  property, closer in spirit to `LLR-N13.1.5`'s per-map containment than to any coercion LLR -- but
  `LLR-N13.1.5` is scoped to `load_or_notice`'s warning channel, not to `MapScreen`'s six mutation
  actions. No requirement in this document or its cross-batch references covers "a `store.save()`
  raise must not escape a message handler." Declared standalone, same reasoning as `A-110`.

**The gap, measured on `3611c20` (before this amendment's RED arms existed).** (1) `_coerce_field`'s
`str` branch (`mapper/store.py`) returns the value UNCHANGED -- confirmed: a sidecar carrying the
YAML-escaped scalar `"\ud800"` decodes to a real lone surrogate, and `store.load` raises
`MapStoreError("no se pudo indexar ...: UnicodeEncodeError")` because the raw surrogate reaches
`_reindex`'s sqlite3 bind uncoerced -- the map cannot be opened, though the failure is graceful (a
typed error, not a crash). (2) None of `mapper/app.py`'s six mutation sites -- field commit,
attachment add, attachment remove, undo, add-child, archive -- coerces the text it assigns to the
graph. A surrogate typed or pasted into the title `Input` and committed reaches `node.ficha.title`
raw, and the next `store.save()` call raises an UNCAUGHT `UnicodeEncodeError` out of
`_atomic_write`'s `Path.write_text(..., encoding="utf-8")` -- this one escapes the message handler
and crashes the session, losing the edit. Files already on disk are not corrupted, because the
`.tmp` write fails before `replace()`. (3) None of the same six sites guards `store.save()` at all:
any raise from it -- a full disk, a permissions error, or the surrogate case above -- is uncaught.
Only `action_save` and the `on_mount` new-map branch already guard or otherwise cannot carry
attacker-controlled text.

**Statement.**

1. Every ficha string field -- title, notes, meta, state, schema-defined field values, the
   `document.tags`/`document.inherited` map values, and attachment kind/path/caption -- shall be
   coerced against `darkside.plain()`'s rule (the declared `COERCION_RANGES` table) at the two points
   it enters the in-memory graph: `MapStore.load`'s sidecar parse (widening `LLR-STO.1.1`'s existing
   type-coercion ladder in place, at its own site), and every `mapper/app.py` mutation that assigns
   raw UI-sourced text onto a `Ficha`/`Attachment`/`Node` before it is added to `self.graph`. The
   coercion is reused from its one declared site (`darkside.plain`); this amendment does not declare
   a second table.
2. Every `store.save()` call site in `mapper/app.py` shall guard the call the way `action_save`
   already does: on any exception, show an operator-visible toast naming the failure (`markup=False`)
   and return without proceeding to the call's own success-path steps (persisting `base_graph`,
   refreshing the canvas, or showing a success toast). No `store.save()` call site may let an
   exception escape its message handler.
3. No other behaviour changes. A field value that contains no code point in `COERCION_RANGES` is
   unaffected; a `store.save()` call that does not raise proceeds exactly as before.

**Touched files.** `mapper/store.py` (the `_coerce_field` widening) and `mapper/app.py` (the six
mutation-site coercions and the six `store.save()` guards). No change to `darkside.py`: `plain()` is
already a public, importable function: reused, not duplicated.

**Validation.** `test (unit)` + `test (pilot)` -- `tests/test_g6_store_surrogates.py`, three arms:
(a) a sidecar carrying an escaped lone surrogate title loads clean and round-trips through a save
(store-level, unit); (b) the real `FichaInspector.FieldCommitted` event, posted with a raw lone
surrogate title on a mounted `MapScreen`, does not crash the session and reloads clean (pilot); (c)
each of the 6 unguarded call sites, parametrized, forced to raise via a monkeypatched `store.save`
and driven through its own real action -- field commit, attachment add, attachment remove, undo,
add-child, archive -- asserting a toast naming the failure and a surviving `MapScreen`. See
`03-increments/increment-024-g6-store-surrogates.md` for the RED-before evidence (all 8 arms
reproduce the exact defect mechanism named above, not a fixture artefact) and the mutation battery
that proves each arm can fail.

**Numeric pass threshold.** `0` of the 8 arms in `tests/test_g6_store_surrogates.py` fail; `0`
`store.save()` call sites in `mapper/app.py` without a `try`/`except` around the call.

**What is not claimed.** This amendment does not change what happens to a container-typed field
(still refused and recorded, per `LLR-STO.1.1` threshold 2 -- untouched) or add validation for a
scenario that cannot reach the graph. It does not retry a failed save, or roll back an in-memory
mutation that a subsequent save failed to persist -- the operator is told and the session keeps
running; recovering the specific edit is a `u` (undo) away if a snapshot was pushed, same as any
other declined write. `B-67` ("lone surrogates survive `darkside.plain`") is closed for paint/export
by Inc-8 pass-3; this amendment closes its persistence half -- see `.dev-flow/BACKLOG.md` B-67.

**Appended note (G6 corrective pass, `G6-C-F1`..`F8`, closing security review `BLOCK-UNTIL
G6-C-F1, F2, F3, F8`).** The independent security review found the increment as landed (`65621f3`)
incomplete against its own statement above:

1. **`G6-C-F3` corrects a factual error in this requirement and in
   `03-increments/increment-024-g6-store-surrogates.md` §1.** Both said "every `store.save()` call
   site in `mapper/app.py` now degrades to a toast." That was false: `MapScreen.on_mount`'s
   `map_id == "new"` branch is an 8th call site, and it was unguarded. It is now routed through the
   same guard as the other seven. The false claim is corrected here rather than silently rewritten;
   see the increment record's own "Corrective pass" section for the fuller account.
2. **`G6-C-F1`** closes the same gap one level down: `mapper/screens/factory.py::_persist` --
   reached from `action_edit_doc` and `action_import_office` -- called `store.save()` with no guard
   at all, and `action_edit_doc`'s `EditorScreen` callback assigned `Document.source` raw. Both are
   now guarded/coerced the same way every `mapper/app.py` site is.
3. **`G6-C-F2`** replaces every guard's toast wording. `f"no se pudo guardar: {e}"` interpolated the
   exception's own `str()`, which for `OSError` embeds the full absolute path and, on Windows, the
   account name -- the exact leak `B-30` already closed for `store.load`'s toast (`store.py` ~594-599).
   Every guard (the pre-existing one, the six from this amendment, `G6-C-F1`'s and `G6-C-F3`'s) now
   shares ONE helper, `mapper/app.py::_save_or_toast`, whose toast names the map id and the exception
   TYPE only -- both passed through `darkside.plain()` -- never `str(e)`. The Spanish wording is
   unchanged; only the leak is removed (Inc-EN, `B-71`, still owns translating it).
4. **`G6-C-F4`** coerces the "guardar como" map name (`ImportPreviewScreen.action_save`) before it
   reaches `store.save(name, ...)` -- the one remaining mutation site this amendment's statement 1
   missed.
5. **`G6-C-F7`** fixes a REGRESSION this amendment itself introduced: `plain()` maps `\r` (U+000D) to
   U+FFFD, correct at a paint sink but not at the LOAD boundary `_coerce_field` widened to call
   `plain()` on every stored string. A note with real CRLF line endings (pasted on Windows) corrupted
   permanently on its first load, silently. `_coerce_field` now normalizes `\r\n`/`\r` to `\n` BEFORE
   calling `plain()`, at the storage-coercion site only -- `plain()` itself is unchanged, and every
   paint call site still gets the U+FFFD behaviour this amendment specified.
6. **`G6-C-F5`/`F6`** widen the coercion's OWN stated scope ("the two points [ficha string fields]
   enter the in-memory graph") to two text positions this amendment's implementation missed inside
   that same scope: `Edge.label` (set raw by `mermaid.parse`, never a sidecar text position) and an
   mmd-only ("orphan") node's `Ficha` (a node the sidecar carries no entry for at all, so it never
   entered `_graph_from_sidecar`'s per-node loop). Both are now coerced.
7. **`G6-C-F8`** is a pre-existing defect (not introduced by this amendment, not part of its
   original fence) the same security review flagged alongside it: `save()` wrote `.mmd` then
   `_nodos.yml` as two independent atomic replaces, so a failure between them left the pair torn --
   the newer file replaced, the older stale -- and the next `load()` rebuilt from the stale sidecar
   with no warning, reverting the edit silently. `save()` now writes both temp files before either
   replace, and stamps the sidecar with a fingerprint of the `.mmd` text it was saved alongside
   (`_mmd_hash`, reusing `_text_hash` -- the module's one hashing routine); `load()` compares that
   fingerprint against the `.mmd` actually on disk and appends a `load_warning` naming the map (no
   path) on a mismatch. See `.dev-flow/BACKLOG.md` for the residual window this still leaves.

**Numeric pass threshold, corrective pass.** `0` of the 20 arms in `tests/test_g6_store_surrogates.py`
(8 original + 12 corrective, one of which is the AST census) fail; `0` `store.save()`-shaped call
sites anywhere under `mapper/` without a `try` body or the shared `_save_or_toast` helper around them
(derived by AST walk, not hand-listed).


### `A-112` -- Inc-9: English chrome (key labels, key-group headers, screen headers), one name per view on the headers Inc-9 owns, and the thresholds that make both checkable

**Authority.** Operator LANGUAGE RULING, 2026-09-29 (`VERDICT-inc8-legend-2026-09-28.md` § "LANGUAGE
RULING", verbatim *"Todo en inglés, también la UI."*), which routes to Inc-9 *"key labels, key-group
headers and the other screens' own headers"*; round-1 `D5` as re-ruled in English (*"one name per
view, the same on screen and in the legend"*; `atlas` / `outline` / `mind map` / `home`, ratified
2026-09-29); carried finding `INC8-P2-UX-F4` (the atlas and radial headers paint names the legend
does not use). **The exact English wording is NOT ruled**: every string this amendment introduces
is listed, old and new, in `03-increments/increment-025-inc9.md` § "English copy table" for the
operator to correct. A correction is a copy edit; it does not reopen this amendment.

**Why an amendment and not a silent edit.** No requirement in this document names the language of
the chrome, and several sealed arms pin Spanish label VALUES (`AT-N03h`'s whole-seat table, the tab
strip, the keybar truncation marker). Re-deriving a sealed arm needs a requirement to re-derive it
against; this is that requirement. Arms that pin BEHAVIOUR (which key dispatches which action, which
scope a screen opens the legend on, priority, the collision set) are not re-derived and stay as
they are.

**Statement.**

1. **Key labels.** Every `mapper/keymap.py::KEYMAP` label, in every scope, shall be short lowercase
   English naming what the key does from the operator's side.
2. **Key-group headers.** Every `mapper/keymap.py::GROUP_SCOPE` key (it is painted, verbatim, as the
   group header in the keybar, the legend and the palette) shall be English. The two Spanish groups
   are renamed: `lista` -> `list`, `salir` -> `leave`. The rename moves no key between scopes.
3. **Hand-written key bars.** The two screens that still paint a hand-written `KeyBar` literal
   (`HomeScreen`, `RepoScreen`) shall paint English group headers and labels. They are not migrated
   into the seat by this amendment (`#D9` migrates `FactoryScreen` and `SettingsScreen` only); the
   keybar's truncation marker (`darkside.keybar`, `? todas`) is part of the key bar and moves too.
4. **Screen headers -- the set, defined so it can be DERIVED, never enumerated.** A screen header is:
   (a) a tab label painted by `darkside.tab_strip`; (b) a string literal passed as `crumb=` to
   `TabStrip` inside a `Screen` subclass; (c) the literal first argument of a `Static` or `Label`
   composed inside a `Screen` subclass whose `id` ends in `-title`, `-header` or `-label`; (d) the
   home screen's identity row name. The subject set is computed by walking every product module's
   `Screen` subclasses with `ast` at test time. Every member shall be English. **Not members**, and
   therefore `Inc-EN`'s (`BACKLOG.md` B-71): hint lines, toasts, prompt titles passed at a call site
   (`_PromptScreen("guardar como", ...)`), modal hint rows (`↵ confirmar`), sidebar hint blocks, demo
   content on the components sheet, and every string a renderer paints below its header line.
5. **One name per view, on the headers Inc-9 owns.** The home screen's identity row shall read its
   name from `darkside.VIEW_NAMES["home"]`. Every seat label that names a view (`toggle_<view>`)
   shall name it by `darkside.VIEW_NAMES[<view>]`. The tab strip and the key labels shall use one
   word per screen (`factory` on the door, the tab and the legend title; `settings` on the door, the
   crumb and the legend title).
6. **The painted-keys parser of `HLR-N16.4` shall not read a key-section row as an own-scope item**
   (`INC8-P2-CR-F9`): an own-scope item is matched only in the exact form the own-scope group paints
   it -- the seat's glyphs for one `OWN_SCOPE_COPY` word, single-spaced, then that word -- so a key
   row painting a glyph and a label under the key column's padding never matches, whatever its
   English label.
7. **`LLR-N06.2.5`'s coercion half, clarified, not widened:** a site that routes the WHOLE formatted
   message through `darkside.plain()` routes every interpolated value through it. `plain()` is
   index-preserving replacement, so coercing the assembled string and coercing each value produce
   the same painted row. The census accepts either shape; it accepts no third.
8. **`C-D9a`'s precondition, recorded.** The positive control `C-D9a` demands (a real focus
   transition on `SettingsScreen` with its `tab` bindings present) could not be built on the shipped
   screen: executed at `6fe35f5`, 9 `tab` presses give `transitions=0`, `focus_chain` length **0**.
   Root cause, measured: `settings.py::_StateRow.__init__` assigns its third column widget to
   `self.disabled`, which is Textual's own `Widget.disabled` reactive -- a truthy widget object
   disables the row and every component inside it (`_self_or_ancestors_disabled` is `True` for the
   DEFAULT column's switch). The attribute is renamed; the sheet becomes traversable (14 targets).
   **Measured on the repaired sheet, the drop is NOT neutral -- it is a repair.** Nine real `tab`
   presses make 8 transitions, each to the next member of the focus chain (the positive control:
   the probe sees a move). The pre-drop `tab`/`shift+tab` bindings, re-declared verbatim on a
   subclass, leave focus on ONE target for all nine presses -- `LLR-N06.5`'s own measurement ("a
   screen-level `tab` binding ... 0 focus moves in 9 presses") reproduced on this screen. The
   drop ships, `SettingsScreen` leaves `TAB_BINDING_EXCEPTIONS`, and the arm asserts both walks
   (`tests/test_inc9.py::test_cd9a_the_probe_sees_transitions_and_the_drop_restores_traversal`).

**Numeric pass thresholds** (every count evaluated at run time; none typed here):

- labels (statement 1), group headers (2), hand-written key-bar strings (3) and screen headers (4)
  carrying a non-ASCII LETTER (`unicodedata` category `L*`, code point > 127): `== 0`;
- words in the same subject set that are not in the declared chrome lexicon
  (`tests/test_inc9.py::CHROME_LEXICON`): `== 0`. The lexicon is a DECLARATION (a dictionary is not
  derivable from the code it judges); the SUBJECT set is derived. A new English word is added to the
  lexicon deliberately, in the same commit that paints it -- the same "changing the seat is a
  deliberate edit" rule `AT-N03h` applies to the seat;
- subject-set size `> 0` for each of the four sources, asserted BEFORE any member is judged;
- declared exceptions: each names the increment that closes it, and a stale-exception guard reddens
  when the excepted string is gone -- the `#D10` register's mechanism, reused;
- `toggle_<view>` labels not containing `VIEW_NAMES[<view>]`: `== 0`;
- the home identity row, read from the painted frame, contains `VIEW_NAMES["home"]` and not the old
  name.

**Split, recorded rather than absorbed (`INC9-F2`).** Statement 5 for the three MAP views' own
headers (`views/layered.py`: `árbol legacy` / `mapa de conceptos`; `views/radial.py`: `mapa mental`;
`views/outline.py` spells `outline` as a literal rather than reading it) and statement 4 for two
screens outside Inc-9's declared files (`screens/coverage.py` `coverage-title`, `screens/editor.py`
`editor-title`) would take Inc-9 to **8 source files against a cap of 5**. They are declared
exceptions owned by **`Inc-9b`**, carried by a strict-xfail arm and by the language census's
exception register, so the split is a mechanical handoff and not a promise. The coordinator cuts
`Inc-9b`.

**What is not claimed.** No toast, notice, prompt, hint line, inspector string or sala string moves
language here (`Inc-EN`, B-71). No renderer file is edited. The legend's own copy (`help.py`) is
Inc-8's and is untouched.

**Note, 2026-09-30 (Inc-9b, `03-increments/increment-026-inc9b.md`).** The split this amendment names in statement 5
("the headers Inc-9 owns") and in statement 4's census is now closed. Statement 5's one-name rule extends to the map
views' own headers and `_degraded` banners (`atlas` / `mind map` / `outline`, read from `darkside.VIEW_NAMES`; the atlas
header states its kind as secondary English text, assumption `INC9B-A1`), and statement 4's English rule is met by the
`coverage` and `edit document` titles. `LANGUAGE_EXCEPTIONS` is empty. No statement changed; the threshold arms are
`tests/test_inc9.py::test_inc9b_*`.

**Note, 2026-09-30 (Inc-9c, `03-increments/increment-027-inc9c.md`).** The operator's answers K1-K4
(`VERDICT-inc9-2026-09-30.md`) refine statements 2, 3 and 5; no numeric threshold is loosened.

- **Statement 2.** What a key group PAINTS is now `keymap.GROUP_HEADER[group]`, not the group id; two groups may share
  one word (`move` for `nav` on the map and `tree` in the factory). The language census judges the ids and the headers
  (`_seat_strings`). Renamed: `doors` -> `open`, `list` -> `maps`, `app` -> `global`, `plug` -> `connect repo`,
  `settings` -> `components`; new home group `exit` holds `q quit` (it is not a list action).
- **Statement 3.** `HomeScreen` and `RepoScreen` no longer paint a hand-written `KeyBar`: both are built from the seat
  (`INC9-UX-F4`), so their words are the seat's. The truncation marker reads `? all keys`.
- **Statement 5.** One word per screen: `components` (the `s` key, the door, the crumb, the legend title; the tab strip
  marks no tab) replaces `settings`; `connect repo` (tab, door, title, crumb, key-group header, legend title, read from
  the screen's name) replaces the plug screen's four names.
- **Key hints (K3), within statement 4's "not members".** The key-hint strings listed in the record moved to English;
  each key uses its seat label's word, built with `keymap.hint_pair`. Toasts and prose remain Inc-EN.
- **Numeric.** The legend's own-scope group is its title plus the FEWEST lines its four items need at the layout's row
  budget (2 modal, 3 docked), derived independently in `tests/test_help_scope.py`; the former "exactly two in both
  layouts" was the band of the old word `ends` (`INC9B-F1`).

## Amendment set 20 -- a map id typed by the operator names a file inside the workspace, and creating never overwrites. 2026-09-30. Base `fddd07d`.

### `A-113` -- map-id confinement and create-never-overwrites (`Inc-SEED`)

**Authority.** Finding `INC9BC-UX` section E, `SEED-1` and `SEED-2` (independent UX review of
`Inc-9b`/`Inc-9c`, reproduced through the real key path from home): `MapStore.create_seed`
(`mapper/store.py`, created 2026-08-23) (1) replaces an existing map, both its `.mmd` and its
`_nodos.yml`, with the seed tree, and (2) accepts `../x` and writes `x.mmd` and `x_nodos.yml` one
directory above the workspace. Both are pre-existing; neither was introduced by this batch.

**Statement.**

1. **Confinement.** A map id names a file INSIDE the workspace. The store refuses, with a
   `MapStoreError`, an id that is empty, contains a path separator (`/`, `\`), `..`, a drive letter or
   any `:`, a character invalid in a Windows file name (`< > : " | ? *`, control characters), a
   reserved Windows device name (`CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, `LPT1`-`LPT9`, case
   folded, with or without an extension), or that ends in a dot or a space. The check is ONE
   `MapStore` method and runs on every read and write of a map id (`save`, `load`), so a typed id, a
   CSV "save as" name, a template-map name and a file-derived link (`map:` field) are all covered by
   the same code. The UI also refuses the typed name early, in the construct dialog.
2. **The toast names the rule, never a path and never the typed text.** Each refusal is a short
   Spanish sentence stating which rule was broken (copy is translated by `Inc-EN`, `B-71`). No
   absolute path, no workspace path and no echo of the rejected name reaches the operator.
3. **Creation never overwrites.** Creating a map (construct, from template, CSV "save as") whose id
   already has a `.mmd` or a `_nodos.yml` is refused with a toast; nothing on disk changes. A
   dedicated `MapStore.create` enforces this; `save` stays the overwrite-by-design path for editing
   an open map.

**Policy choice, recorded.** Two options were open for statement 3: refuse with a toast, or ask for
confirmation and then overwrite. **Refusal is chosen.** It is simpler (no new modal state, no
confirmation screen to keep in step across three entry points), it matches this batch's position on
`B-36`/`B-72` that one keystroke must never overwrite, and it loses nothing: the operator who wants
the old map replaced can still pick another name. A confirm-then-overwrite gesture can be added later
as its own decision without touching the store rule.

**Trace.** Standalone, the same way `A-110` and the mutation half of `A-111` are. The nearest
parent, `HLR-STO.1` (`LLR-STO.1.1`, the load-side scalar ladder), governs what the store does with
file text, not with operator-typed ids; widening it would stretch its subject. The property is
closer in kind to `osopen`'s confinement test (`REFUSED_OUTSIDE`) than to any store LLR. Carried by
`tests/test_seed_safety.py`.

**What is not claimed.** Toast wording stays Spanish (`Inc-EN`). The check-then-write in `create`
is not atomic against a second process creating the same id between the check and the write; the
store has a single writer by construction (one TUI, one operator). No change to `save` semantics for
an existing open map.


#### `A-113` -- dated note 2026-09-30 (`Inc-SEED-2`, closes the security review of `Inc-SEED`)

The rule set of `A-113` changes in five places. Findings are named `SEED2-Fn`.

1. **Statement 2 is softened (`SEED2-F3`).** "No echo of the rejected name" becomes **no path and no
   profile**. A refusal never carries an absolute path, a workspace path or the operator's profile
   directory. The "ya existe el mapa 'X'" toast legitimately echoes `X`, because `X` is a valid id of a map
   that is already in the operator's own list; the typed text of a REFUSED name is still not echoed.
2. **The `"new"` sentinel is removed (`SEED2-F1`).** `MapScreen.on_mount` no longer treats the id `new` as
   "make a fresh map". A real map named `new` opens like any other and is never rewritten by opening it.
   Nothing produced `MapScreen("new")` (census in `increment-030-seed-2.md`).
3. **The `..` substring rule is dropped (`SEED2-F2`, `B-76`).** `v1..v2` is a legitimate id. Separators and
   `:` are refused, so `..` names the parent only when the id is made of dots; `.`, `..`, `...` and any
   dot-only id are still refused, by the existing rule that refuses an id ending in a dot or a space.
4. **Length (`SEED2-F3`).** An id longer than **100 characters** is refused with a rule message. The
   number is chosen so `<id>_nodos.yml` plus a temp suffix and the workspace path stay under `MAX_PATH`
   (260) for any workspace path up to about 140 characters.
5. **Characters and names.** A lone surrogate (U+D800 to U+DFFF) in an id is refused (`SEED2-F4`): `save`
   wrote both files before the sqlite reindex raised. `CONIN$`, `CONOUT$` and `CLOCK$` join the reserved
   device names (`SEED2-F5`).

**Trace.** Standalone, as `A-113`. Carried by `tests/test_seed2.py`; `tests/test_seed_safety.py` loses its
`a..b` refusal case (it is now valid). **What is not claimed.** The 100-character limit is a margin
against `MAX_PATH`, not a measurement on the operator's workspace; short-name spellings (`PROGRA~1`) and
alternate-data-stream spellings are not covered (`B-78`).


### `A-114` -- repository specs are data, and a failed connect is one of a fixed set (`Inc-9f`)

**Authority.** Round 3 of `VERDICT-inc9-2026-09-30.md`: the operator's answers `M1` and `M2`, and the
coordinator's Inc-9f rulings (argument injection, `R3-CR-F7`, `R3-SEC-F1`). Findings are named
`INC9F-Fn` (`increment-032-inc9f.md`).

**Statement.**

1. **A typed repository spec is data, never an option.** A URL or `owner/name` spec that starts with `-`,
   or that starts with a transport-helper prefix (`ext::`, `file::`, any `scheme::`), is refused with a
   `GitHubError` before any `git` or `gh` process starts. Every `git` call puts `--` before the URL and the
   target; a ref name that came out of a repository (a branch or tag) is handed to `git log` and
   `git rev-list` after `--end-of-options`. A local path is still accepted where it was (a directory with a
   `.git`).
2. **A failed `git` or `gh` call is reported as one fixed category:** `host not found`,
   `not found or private`, `authentication required`, `network unreachable`, `timed out`,
   `unknown (exit N)`. The category is chosen in code from stable fragments of the tool's English stderr;
   the stderr is never painted and never put in an exception message. A clone is
   `could not clone '<name>': <category>`. The clone has a timeout (120 s; a read keeps 30 s).
3. **The failure outlives the toast.** The repo screen's stage panel paints the same sentence and the way
   out (the seat's word for `home`), and no progress bar.
4. **Reconnecting a mirror fetches.** `git clone --mirror` makes a bare repository, so the cache-hit test
   is `HEAD` as a file, not `.git`.
5. **Home and the palette (`M1`, `R3-UX-F1`, `R3-UX-F7`).** The home hint is the seat's `open map` plus the
   invitation to choose a door. The palette paints its selected row, takes up/down/pageup/pagedown from the
   search box, runs the highlighted row on `enter`, and pads its label column to the seat's widest word.

**Trace.** Standalone, the same way `A-113` is: the nearest rule, `A-112` (English chrome), governs
words, not process arguments. Carried by `tests/test_inc9f.py`.

**What is not claimed.** The categories rely on git's English stderr: under another locale the text will not
match and the category is `unknown (exit N)` (a safe failure; carried). The 120 s clone timeout is a margin,
not a measurement. `ssh`-form URLs (`git@host:path`) are not parsed beyond the leading-dash and `::` rules.

### `A-115` -- the Inc-9f review defects (`Inc-9g`)

**Authority.** The independent reviews of `Inc-9f` (UX and security, then the code review), the coordinator's
rulings on defects, and the operator's answer `N1` (`VERDICT-inc9-2026-09-30.md`, Round 4). Findings are named
`INC9F-UX-F1`, `INC9F-UX-F2` (`N1`), `INC9F-SEC-F1`..`F4` and `INC9F-CR-F1`..`F6`; the record is
`increment-033-inc9g.md`. `N2` (the arrows in the palette footer) is routed to `Inc-EN`, not here.

**Statement.** Amends `A-114`.

1. **The selected palette row is legible (`INC9F-UX-F1`).** Every glyph on the highlighted row reaches a
   contrast of at least 4.5:1 against the highlight background, on every palette scope and under a relabelled
   seat. The row is painted in one ground-on-accent colour; the unselected rows keep their three.
2. **A mirror is keyed on the whole URL (`INC9F-SEC-F1`).** The cache directory is `<last segment>-<12 hex of
   the sha256 of the normalised URL>`; the normal form drops surrounding space, a trailing `/` and `.git`.
   `alice/tools` and `bob/tools` no longer share a mirror.
3. **Typed repo text is text (`INC9F-SEC-F2`).** The repo screen paints the typed repository through
   `darkside.plain()` as a `Text`; `a[/b]`, `[@click=...]` and `[link=...]` are shown literally and plant
   nothing. The crumb already painted a `Text`; an arm pins both.
4. **A cache hit that cannot be refreshed continues on the mirror and says so (`INC9F-SEC-F3`,
   `INC9F-CR-F4`).** A fetch that times out or exits non-zero does not abort the connect. The refresh gets the
   clone's 120 s budget. The connector records the fixed category it is stale for and the repo screen toasts
   `showing the cached copy: <category>` (through `plain()`, markup off).
5. **`owner/name` is validated for `gh` (`INC9F-SEC-F4`).** The owner matches `[A-Za-z0-9-]+`, the name
   `[A-Za-z0-9._-]+` and is not `.` or `..`; anything else is refused before a process starts, with a fixed
   sentence that echoes nothing.
6. **The home hint drops `↵ open map` when there is nothing to open (`N1`, `INC9F-UX-F2`).** With no recent
   map the hint is the invitation to choose a door alone; with maps it stays the seat-derived `↵ open map ·
   or choose a door`.
7. **The classifier (`INC9F-CR-F1`, `F2`, `F5`, `F6`).** The order of the four categories is pinned by
   overlapping samples; each `gh` stderr sample names its own category; only `permission denied (publickey`
   counts as authentication (a local filesystem refusal is `unknown (exit N)`); the fixed set is declared once
   (`github.CATEGORIES`, `_TIMED_OUT`).
8. **Every `git` call runs with `LC_ALL=C` and `GIT_TERMINAL_PROMPT=0`.** The category is chosen from English
   stderr, so a localised `git` no longer falls to `unknown`, and a private HTTPS repo fails instead of
   waiting on a prompt. The environment is built per call, so a test's temp `HOME` reaches git.
9. **The transport-helper refusal reads the same stripped text as the dash refusal** (`INC9F-CR`, item 14).

**Trace.** Standalone, like `A-113` and `A-114`. Carried by `tests/test_inc9g.py`; two `test_inc9f.py` arms
changed (declared in the record).

**What is not claimed.** `LC_ALL=C` is not measured against a localised `git` (no such git here). The stale
toast is a toast: the stage panel does not carry it. `gh` is not given the English environment (its stderr is
English already in the samples used). The hash is a cache key, not a security boundary: a collision needs a
second preimage of 48 bits, and is not claimed impossible.

### `A-116` -- the Inc-9g review defects (`Inc-9h`), dated 2026-10-01

**Authority.** The independent reviews of `Inc-9g` (code, UX, security) and the operator's answers `P1` and `P2`
(`VERDICT-inc9-2026-09-30.md`, Round 5). Findings are named `INC9G-CR-F1`..`F7`, `INC9G-UX-F1`..`F3`,
`INC9G-SEC-F1`..`F5`; the record is `increment-034-inc9h.md`.

**Statement.** Amends `A-115`.

1. **Row 0 is lit after every filter edit (`INC9G-CR-F1` = `INC9G-UX-F1`).** The palette awaits `ListView.clear()`
   before it rebuilds the rows, so the first row of any filtered list carries `-highlight` and is painted in the
   `A-115` st. 1 colours (at least 4.5:1); `↵` runs the row the operator can see. The rows' label list is rebuilt
   with the rows.
2. **The stale cached copy stays on the panel (`P1` = `INC9G-UX-F2` / `INC9G-SEC-F3`).** While the cached copy is
   what the repo screen shows, the stage panel paints `▲ cached copy: <category>` in INK (as `N3`), under the
   stages, after the toast has expired. A fresh connect paints no such line. The toast gains `· <way back> to retry`,
   the way back being the seat's word for the screen's `home` action (`q back`), derived as the failure panel does.
3. **One toast per connect (`P2` = `INC9G-UX-F3`).** A stale connect fires only the warning
   `showing the cached copy (N nodes): <category> · q back to retry`; the `conectado: N nodos` toast is not fired
   with it. A fresh connect is unchanged.
4. **A mirror is the remote that was asked for (`INC9G-SEC-F1`).** On a cache hit the mirror's
   `remote.origin.url` is compared with the URL as typed (stripped, a trailing `/` dropped; `.git` is NOT dropped:
   it is what separates `r` from `r.git` on a plain server). If they differ the mirror is not reused: the URL gets
   its own directory, keyed on the form as typed; if that directory holds another remote too, the connect is
   refused with one fixed sentence that names neither URL. The `A-115` st. 2 key is unchanged, so the four
   spellings of one remote (`.../tools`, `.../tools/`, `.../tools.git`, `.../tools.git/`) still key ONE directory
   (`INC9G-CR-F3`); a cost, declared: two spellings that differ in `.git` and are the same remote are cloned twice
   when both are used from one cache.
5. **The refresh prunes (`INC9G-SEC-F2`).** The refresh is `fetch --prune --all`: a branch the remote deleted is
   gone from the mirror and from the map.
6. **One fixed sentence for a malformed `owner/name` (`INC9G-SEC-F4`).** Every malformed spec, the wrong number
   of segments included, is refused with the same sentence, which echoes nothing typed. The `could not clone
   '<name>'` messages keep the readable last segment of the URL, through `darkside.plain()`.
7. **No prompt from `gh`, one environment for `git` (`INC9G-SEC-F5`).** `gh` runs with `GH_PROMPT_DISABLED=1`;
   `diff.py`'s `git show` runs in `github._git_env()` (imported: `diff.py` already depends on the package and
   `github.py` does not import it, so there is no cycle).
8. **The stale signal is typed (`INC9G-CR-F5`).** A `git` call of `_run_git` that times out raises `GitHubTimeout(GitHubError)`
   (the clone and `gh` timeouts stay plain `GitHubError`: neither has a stale path);
   `_refresh_mirror` catches that and nothing else, so a missing `git` on a cache hit is still an error and is not
   a stale mirror.
9. **Small corrections (`INC9G-CR-F2`, `F6`, `F7`).** `GitHubConnector.fetch()` resets `stale` at its top;
   `_ensure_cloned` strips the URL once at its top; `HomeScreen.compose` takes `home_hint()` and the first
   `on_mount` sets the real hint (the glob is no longer written twice). `INC9G-CR-F2` is an arm: the home hint
   follows the maps across a push and a pop.

**Trace.** Standalone, like `A-113`..`A-115`. Carried by `tests/test_inc9h.py`. Changed existing arms (declared in
the record): the `test_inc9g` stale-toast arm (new text, by `P2`) and the `_Mirror` stub in `test_inc9f.py`.

**What is not claimed.** The `LC_ALL=C` and gh-environment carries of `A-115` stand. A mirror cloned before this
change has the same directory and the same `origin`, so it is still hit. The two `.git` spellings above cost a
second clone; a user who types one spelling never pays it. A timeout inside the config read of a cache hit is an
error, not a stale mirror (only the refresh has a stale path).

### `A-117` -- the Inc-9h review defects (`Inc-9i`), dated 2026-10-01

> **Superseded in part by `A-119` (2026-10-01):** statement 5 (the credential refusal for a typed `http(s)://` URL) is replaced by the closed allow-list; `.../r@v2` is refused now. Kept as the record of what was decided then.

**Authority.** The independent reviews of `Inc-9h` (code, UX, security), the coordinator's ruling on `INC9H-UX-F1` and
`INC9H-SEC-F2`, and the operator's Round 6, Q1 (`VERDICT-inc9-2026-09-30.md`): `.../r` and `.../r.git` are distinct
remotes, a double clone is accepted, a repo is never shown under another's URL, and no spelling is locked out. Findings
are named `INC9H-*`; the record is `increment-035-inc9i.md`.

**Statement.** Amends `A-116` statement 4; adds statements 10 and 11.

1. **The fallback key is disjoint from the primary key (`INC9H-CR-F1` = `INC9H-SEC-F1`, amends `A-116` st. 4).** When
   the mirror in the primary directory (keyed on the `A-115` normal form) is not this URL's, the URL gets its own
   directory keyed on `"as-typed:" + <the URL as typed, trailing "/" dropped>`. The two key spaces never meet, so a
   URL with no `.git` (`.../tools`) no longer finds, in its fallback, the very mirror it just found foreign in its
   primary (`.../tools.git`). Consequences: in ONE cache, `r.git` then `r` and `r` then `r.git` each give two clones,
   each showing its own branches, with no refusal; a cache the base built (only the `tools.git` mirror, in the primary
   directory) accepts `tools`. The refusal ("refusing the cached copy: it belongs to another repository") remains, and
   is reachable only when BOTH the primary and the URL's own directory hold another remote: a tampered cache or a hash
   collision. The cost declared in `A-116` st. 4 stands (the two spellings are cloned twice from one cache).
2. **The origin comparison is exact (`INC9H-CR-F2`).** An origin that differs from the typed URL only by letter case is
   another remote; it is not folded. (An arm; no code changed.)
3. **No stale across reconnects (`INC9H-CR-F3`).** A stale connect, `q` back, a fresh connect: the second screen paints
   no `▲ cached copy` line and fires only `conectado: N nodos`. (An arm; no code changed.) Not claimed: the palette
   filter-edit serialisation arm (see the record, section 2).
4. **The category never breaks across lines (`INC9H-UX-F1`, coordinator ruling).** The stage panel's stale line is two
   lines: `▲ cached copy:` and, under it, the category (`unknown (exit 1)`, `authentication required`, `host not found`,
   `timed out`, ...). Wrapping before the category is the ruling's second option; a non-breaking space was measured
   to be no option (Rich's wrapper treats it as a space). The text is unchanged; only the line break moves.
5. **A credential in a typed URL is refused (`INC9H-SEC-F2`, coordinator ruling).** A typed `http(s)://` URL whose
   authority holds userinfo (`https://u:tok@host/r`, `https://tok@host/r`) is refused in `GitHubConnector.fetch`,
   before any process starts and before any directory is made, with one fixed sentence that echoes nothing typed:
   `refusing the URL: it carries a credential; use the git credential helper instead`. An scp-style `git@host:o/r`
   address and an `@` in the path (`.../r@v2`) are not userinfo and still connect.

**Trace.** Standalone, like `A-113`..`A-116`. Carried by `tests/test_inc9i.py` and one reworked arm in
`tests/test_inc9h.py` (`..._when_the_own_directory_is_foreign_too_the_connect_is_refused`: it now tampers the primary
AND the URL's own directory; the version it replaces pinned the defect as intended, in that it tampered only the
primary, which for a URL with no `.git` was also the fallback).

**What is not claimed.** `_ensure_cloned` itself still accepts a URL with userinfo when called directly (two sealed
arms in `test_inc9d` and `test_inc9f` call it with a token URL to prove the clone message leaks nothing; the typed
boundary is the connector). The non-breaking-space result (statement 4) is measured on `rich.text.Text.wrap` at 30
cells, where a text with NBSP between the words of `unknown (exit 1)` still wrapped between `(exit` and `1)`; it was not
re-measured in a Textual render.


### `A-118` -- the Inc-9i review defects (`Inc-9j`), dated 2026-10-01

> **Superseded in part by `A-119` (2026-10-01):** statements 1 and 2 (the curl-style authority read and `redact_userinfo`) are replaced by the closed allow-list and `painted_repo`; statements 3 and 4 stand. Kept as the record of what was decided then.

**Authority.** The independent reviews of `Inc-9i` (code, UX, security) and the operator's Round 7, R1
(`VERDICT-inc9-2026-09-30.md`, "Ocultar en pantalla, campo se queda"). Findings are named `INC9I-*`; the record is
`increment-036-inc9j.md`.

**Statement.** Amends `A-117` statement 5; adds statements 12 and 13.

1. **The credential refusal reads the authority the way curl does (`INC9I-SEC-F1`, amends `A-117` st. 5).** For a typed
   `http(s)://` URL every `/` and `\` after `://` is skipped and the authority ends at the first `/`, `?` or `#`. The URL
   is refused, with the same fixed sentence and nothing echoed, before any process starts, when that authority contains
   `@`, or when `urlparse(url).netloc` is empty. So `https:///tok@h/o/r`, `http:///u:tok@h/o/r`, `https:////u:p@h/o/r`
   and `https:///\u:p@h/o/r` are refused (curl treats `u:tok` as userinfo there although `urlparse` finds no netloc); a
   URL with no host at all (`https:///h/o/r`) is refused too. Still connecting: `git@host:o/r`, `https://h/o/r@v2`,
   `https://h/o/r.git`, `https://h/o/r/`, and `https://tok?@h/o/r` (the host is `tok`: the `@` is in the query, and git's
   own credential parsing agrees). An upper-case scheme (`HTTPS://`) never reaches this check: `_is_url` is
   case-sensitive and the `gh` path refuses it with its own fixed sentence.
2. **A typed URL is never painted with its userinfo (`INC9I-UX-F1`, operator R1, statement 12).** One helper,
   `github.redact_userinfo`, returns `scheme://***@host/...` (the scheme as typed, the userinfo replaced by `***`, the
   authority read as in statement 1, so the three-slash form is redacted too); a URL without userinfo comes back
   unchanged. `RepoScreen` paints the redacted form in the crumb and in `#repo-name`; `RepoScreen.repo` stays as typed
   (the connector needs it). No toast and no failure line names the URL (the refusal and `could not clone` name a fixed
   sentence and the last path segment). The connect-repo input field keeps the operator's own text after `q`, for
   correction; it is not cleared and not persisted.
3. **`_ensure_cloned` is reached from production code only through `GitHubConnector.fetch` (`INC9I-CR-F3`, statement
   13).** Its docstring says the caller has refused userinfo; a pin test fails when another production reference
   appears.
4. **Arms only (no behaviour change).** `INC9I-CR-F1`: the `▲ cached copy:` category sits on its own line for every
   category in `CATEGORIES` plus `unknown (exit 1)` and `unknown (exit 128)`. `INC9I-CR-F2`: `R/` after `r.git` then `r`
   finds the as-typed directory `r` made, with no third clone.

**Trace.** Standalone, like `A-113`..`A-117`. Carried by `tests/test_inc9j.py` and two reworked arms in
`tests/test_inc9i.py`.

**What is not claimed.** `_ensure_cloned` called directly still takes userinfo (statement 13 pins who calls it, not what
it accepts). Query-string secrets (`?token=...`) are not userinfo and are not redacted. A real clone of the three-slash
form against curl was measured by the security reviewer, not re-run here.


### `A-119` -- the closed allow-list for typed repo URLs (`Inc-9k`), dated 2026-10-01

**Authority.** The operator's Round 8, S1 (`VERDICT-inc9-2026-09-30.md`), answer "Lista cerrada". Quoted: "A typed repo URL
is accepted only as `https://host[:port]/path` or `git@host:path`, simple characters only (no `@` before the host, no
userinfo, no `?`, `#`, whitespace, backslash, extra or encoded slashes; ASCII host). Everything else is refused before any
process with one fixed sentence that echoes nothing, and every painted surface shows `(unrecognised URL)` instead of the
text. The connect field keeps the typed text (R1). The deny-list pieces (`_refuse_userinfo`, `redact_userinfo` heuristics)
become redundant and are removed or reduced to the allow-list. `owner/name` (gh path) is unchanged". Four rounds in a row
found a new odd URL form; the deny-list is replaced. The record is `increment-037-inc9k.md`.

**Statement.** Supersedes the deny-list statements of `A-117` statement 5 and of `A-118` statements 1 and 2 (they stay in
the text above, marked); `A-118` statement 3 (the `_ensure_cloned` caller pin) and statement 4 stand.

1. **The grammar (one place, `github._is_url`).** A typed URL is accepted only if the WHOLE text matches one of:
   `https://HOST[:PORT]/SEG(/SEG)*[/]` or `git@HOST:SEG(/SEG)*[/]`. `HOST` starts with an ASCII letter or digit and then
   holds ASCII letters, digits, `-` and `.` (a DNS name or an IPv4 address; no IPv6 brackets, no userinfo). `PORT` is one
   or more ASCII digits (https form only). `SEG` is one or more of `[A-Za-z0-9._~-]`, is never `.` or `..`, and never starts
   with `-`. So the path has no `?`, `#`, `%`, `@`, whitespace, backslash, empty segment (`//`) or non-ASCII character, and
   the text has no leading or trailing whitespace.
2. **`http://` is refused (decision).** A git remote over plain http is not needed; the default of the brief is taken.
3. **`https://h/o/r@v2` is refused now (declared).** The `@` in the path is outside the grammar. It connected before
   (`A-117` st. 5, `A-118` st. 1); it does not. No spelling with `@` anywhere is accepted.
4. **The refusal is one sentence.** `refusing the repository: not a supported URL, owner/name, or local folder`, before any
   process and before any directory is made, for every text that is not an accepted URL, a valid `owner/name`
   (`A-113`..: the `gh` path, unchanged) or a local git directory (unchanged). It echoes nothing. This replaces the credential
   sentence and the `gh` path's own sentence (`expected owner/name, ...`); no sealed arm required either. Kept (they name a
   rule and echo nothing, and `test_inc9g` requires the second): `refusing the repository: it may not start with '-'` and
   `...: transport helpers are not accepted`, which run first.
5. **`_ensure_cloned` applies the same check (`INC9J-SEC-F2`).** Next to `_refuse_unsafe`, on the text as given (it no longer
   strips: a padded URL is refused), so a direct call is no weaker than `GitHubConnector.fetch`. `fetch` and the new
   `painted_repo` read the same `_is_url`. `A-118` st. 3 (the AST pin) is kept: it still holds, and it keeps `fetch` the one
   typed-URL entry point.
6. **Display.** `github.painted_repo(text)` returns the text only when it is an accepted URL, a valid `owner/name` or a local
   git directory, and `(unrecognised URL)` otherwise. `RepoScreen` feeds the crumb and `#repo-name` with it; the failure
   line and the toasts carry only the fixed sentence or `plain(name)`. Accepted URLs cannot carry userinfo, so nothing is
   redacted: `redact_userinfo`, `_refuse_userinfo` and `_http_parts` are removed. `RepoScreen.repo` stays as typed and the
   connect-repo field keeps the typed text (R1).

**Trace.** Standalone, like `A-113`..`A-118`. Carried by `tests/test_inc9k.py` and the reworked sealed arms listed in
`increment-037-inc9k.md` section 2.

**What is not claimed.** An IDN host must be typed as ASCII (`xn--...`); a host is not checked as a valid DNS name beyond its
characters (`h..x` passes and fails at resolution); a LOCAL DIRECTORY is painted as typed whatever its path holds (S1 names
the local directory as displayable); no real `git clone` was run against an accepted form (stubs only); the Inc-9j security and
code review tables were not on disk, so "every form in the review tables" is covered by the forms in the Inc-9j arms and the
operator's list.

### `A-120` -- the Inc-9k review fixes and the operator's T1 (`Inc-9l`), dated 2026-10-01

**Authority.** The operator's Round 9, T1 (`VERDICT-inc9-2026-09-30.md`, answer "Decir las formas": the fixed sentence becomes
`refusing the repository: use https://host/path, git@host:path, owner/name or a local folder`, still echoing nothing), and the
coordinator's rulings for the findings of the Inc-9k code, ux and security reviews (`INC9K-SEC-F1`, `INC9K-SEC-F2`,
`INC9K-CR-F1`, `-F2`, `-F3`, `-F5`, `OBS-1`, the UNC hardening). T2 (`http://` refused) is already the behaviour of `A-119` st. 2;
T3 is routed to Inc-EN. The record is `increment-038-inc9l.md`.

**Statement.** Changes `A-119` st. 4 (the text of the sentence) and st. 6 (what is painted); the rest of `A-119` stands.

1. **The sentence (T1).** The one refusal sentence is exactly `refusing the repository: use https://host/path, git@host:path, owner/name or a local folder`. It
   echoes nothing of the typed text. Its own `@` (from `git@host:path`) is the only `@` a refusal message may hold. The two finer
   sentences (`it may not start with '-'`, `transport helpers are not accepted`) stand. Sealed arms that pinned the old text change
   by the label only (`test_inc9k::SENTENCE`, `test_inc9d`, `test_inc9h`, `test_inc9i`, `test_inc9j`); no leak assertion is weakened (the
   `"@"` entry of two leak lists becomes `message.count("@") == 1`, because the sentence now holds the one `@` of `git@host:path`).
2. **One decision (`INC9K-CR-F2`).** `github._classify(text)` is the one place a typed repo is decided: `_refuse_unsafe`, then a local
   git directory, then `_is_url` plus a usable clone name (`_repo_name_from_url`), then owner/name, else the sentence. `fetch` dispatches on it;
   `painted_repo` returns the text only when `_classify` does not raise. So `painted_repo(x) != (unrecognised URL)` if and only if `fetch(x)` reaches a
   process. The forms that were painted but refused (`git@h:r`, `https://h/...`, `https://h/o/.git`, `https://h/o/..git`, `-a/b`, a local git
   directory named `-x`) now paint `(unrecognised URL)`.
3. **`_is_local_path` is total (`INC9K-SEC-F1`).** It returns False on `RuntimeError`, `OSError` or `ValueError`: `~name...` for a user that cannot be resolved raised
   `RuntimeError` out of `expanduser`, which crashed the app (Textual's traceback prints locals, and so the typed text) and reached `fetch` as
   `error inesperado: RuntimeError`. A typed text can no longer make the predicate raise.
4. **UNC (coordinator ruling).** A typed text whose first two characters are each `/` or `\` is not a local folder and is refused BEFORE any
   filesystem call (so no SMB or NTLM lookup on the UI thread). It paints `(unrecognised URL)` and gets the sentence. This covers UNC, `\\?\` and `\\.\` device paths
   and the mixed forms `/\host` and `\/host`, which Windows also reads as UNC (a superset of the ruling: declared).
5. **The GitHub URL rewrite is case-consistent (`OBS-1`).** `PlugRepoScreen._normalize_repo("HTTPS://GITHUB.COM/o/n")` raised an `IndexError`
   (a case-insensitive check, a case-sensitive split). It now returns `o/n`; `http(s)://github.com/o/n` still returns `o/n`.
6. **API-derived names are one encoded path segment (`INC9K-SEC-F2`).** In `_fetch_gh` the default branch, each branch name and each commit sha go into a
   `gh api` path through `urllib.parse.quote(name, safe="")`, so `%2e%2e/%2e%2e/user`, `x#frag`, `{owner}` (gh expands `{owner}` and `{repo}`)
   cannot steer an authenticated request. A branch name with `/` is sent as `%2F`.

**Trace.** Standalone, like `A-113`..`A-119`. Carried by `tests/test_inc9l.py` and the reworked arms listed in `increment-038-inc9l.md` section 2.

**What is not claimed.** `%2F` for a branch with a slash in `compare/` and `commits/` was not measured against the live GitHub API (stubs only); a text with
leading whitespace before two slashes is not specially treated (the screen strips typed text; `fetch` of a padded text goes to the sentence by the
grammar); the `_normalise_url` `.strip()` is inert and left alone (`CR-F6`); `tests/test_inc9j.py` still has a stale phrase in the docstring of the upper-case pin
(`the gh path ... its own fixed sentence`), outside the brief.

### `A-121` -- a closed allow-list for typed local paths and the Inc-9l review fixes (`Inc-9m`), dated 2026-10-01

**Authority.** The operator's S1 (Round 8, closed allow-list) and T1 (Round 9, the refusal sentence), applied by the coordinator's ruling to typed LOCAL paths
("local paths get an allow-list, like URLs"), and the coordinator's rulings for the findings of the Inc-9l reviews (`INC9L-SEC-F1`..`F5`, `INC9L-CR-F1`..`F5`,
`INC9L-UX-F1`). The record is `increment-039-inc9m.md`.

**Statement.** Replaces `A-120` st. 4 (the two-slash deny-check) with an allow-list; the rest of `A-120` stands.

1. **One helper.** `osopen.safe_local_path(text) -> Path | None` is the one place a typed local path is judged; `github`, `app` and `screens/factory`
   import it, and none of them calls `expanduser` itself. Every decision is made on strings BEFORE any filesystem call; the caller may stat the
   returned path, and only then. Grammar: (1) `None` on a non-`str`, an empty text, a NUL, or a leading `-`; (2) `Path(text).expanduser()`, and `None`
   on `RuntimeError`, `OSError` or `ValueError`; (3) on `PureWindowsPath` of the expanded text, accept ONLY (a) a drive that is one ASCII letter and `:` AND
   root `\`, or (b) no drive, no root, and a typed text that does not start with `\` or `/`; everything else is `None` (UNC, `\\?\`, `\\.\`, `\??\`, `/??/`,
   root-relative `\x`, drive-relative `C:x`, a `~` that expands to UNC).
2. **`INC9L-SEC-F1` / `CR-F1`.** `github._is_local_path` reads the helper (and keeps its `RuntimeError`/`OSError`/`ValueError` catch for the stat calls).
   `fetch` resolves the folder through the helper.
3. **`INC9L-SEC-F2`.** The import-CSV and import-office prompts judge the typed path with the helper; `None` gives the existing not-found toast
   `archivo no encontrado` WITHOUT a name (the typed text is never echoed: `~nosuchuser/secret-token.csv` made `expanduser` raise and the crash
   printed the typed text). A path the helper accepts keeps `archivo no encontrado: <name>`.
4. **`INC9L-SEC-F5`.** `osopen.open_external(kind="file")` applies the same rule to `target` before `resolve()`; a refusal is the existing
   `destino inválido`. (A file target that starts with `-` is refused too: the same rule.)
5. **`INC9L-SEC-F3`.** `_fetch_gh` builds no path for an API-derived branch name or commit sha equal to `.` or `..`; a default branch equal to `.` or `..` ends the
   fetch with `unexpected response from gh repo view` before any `gh api` call.
6. **`INC9L-SEC-F4`.** A tag's date is read from `repos/{owner}/{name}/commits/{quote(sha, safe='')}` built from `tag["commit"]["sha"]`; the API's own
   `commit.url` is never handed to `gh`.
7. **`INC9L-CR-F2`.** `_repo_name_from_url` takes the path of a `git@host:path` from the allow-list match, so `git@h:r` and `git@h:project.git` (the literal form T1
   tells the user to type) are accepted and reach `git clone --mirror`. Row `c00` of the Inc-9l consistency table was "refused"; it is now accepted (declared sealed-arm change).
8. **`INC9L-CR-F3`.** `RepoScreen._source_kind` reads `github._classify`: `local` is `local`, `gh` and `url` are `github` (the wording is unchanged); a refused text is `local`.
9. **`INC9L-CR-F5`.** The encoded default branch is `qdefault`.
10. **`INC9L-CR-F4` (accepted).** The broad `OSError` catch in `_is_local_path` stays: the ruling wants a total predicate. A local folder that cannot be read may fall
    through to the `owner/name` path.
11. **`INC9L-UX-F1` (coordinator decision, no code).** The specific refusal reasons (`last segment is not a usable name`, `may not start with '-'`,
    `transport helpers are not accepted`) stay alongside the T1 sentence.

**Trace.** Standalone, like `A-113`..`A-120`. Carried by `tests/test_inc9m.py` and the sealed-arm change listed in `increment-039-inc9m.md` section 2.

**What is not claimed.** A relative text with a `:` inside (`CC:\x`) has no drive for `PureWindowsPath` and is accepted by branch (b); it is a local relative name (a stream
separator on NTFS), not a network path, and the ruling's grammar is applied as written. A leading-whitespace text is not trimmed (the screens strip typed text). The
`tests/test_inc9m.py` spies prove that no filesystem call is made for the named hostile forms; no real UNC or NT-namespace path was ever opened, and nothing was measured against
a live SMB share, a live `gh`, or a real `git clone`. `docs/ARCHITECTURE.md` section 3 bans `screens` from importing `osopen` and lists `model` as the only dependency of `github`; the coordinator's ruling
puts the helper in `osopen` and has all three import it, so the map and the code now disagree in writing until the map is updated (carried; no test enforces it).

### `A-122` -- the Inc-9m review fixes: sidecar paths, DOS devices, the refusal sentence, attachment-add (`Inc-9n`), dated 2026-10-01

**Authority.** The operator's U1 and U2 (Round 10 of `VERDICT-inc9-2026-09-30.md`), the coordinator's rulings for `INC9M-SEC-F1`..`F4` and `INC9M-CR-F1`..`F8`
(the findings of the Inc-9m reviews). The record is `increment-040-inc9n.md`.

**Statement.** Amends `A-121`; the rest of `A-121` stands.

1. **`INC9M-SEC-F1` (HIGH).** `FactoryScreen._office_path` returns `None` unless `safe_local_path(doc.path)` accepts the sidecar text, and the result is confined to the
   workspace (lexical containment first, then `resolve()` + `is_relative_to`, as `open_external` does). A sidecar `documents[].path` is not typed text: a UNC, `//`, `\??\UNC`,
   device or outside-the-workspace path is never stat'ed or read; the screen shows its existing `archivo de plantilla no encontrado`.
2. **`INC9M-SEC-F2` / `CR-F1`.** `safe_local_path` returns `None` for a DOS device name (`con`, `nul`, `conin$`, `conout$`, `com1`, `aux`, `lpt1`, `prn`...) in ANY component, in any case,
   with an extension, trailing dots or spaces (`PureWindowsPath(part).is_reserved()` per component; Python 3.13 spells it `os.path.isreserved`). Both import prompts require
   `is_file()`, and `open_external(kind="file")` requires `is_file()` before launching.
3. **`U1`.** A text refused by `safe_local_path` toasts exactly `path not supported: use C:\… or a relative path` (one sentence, a real ellipsis, naming nothing) in the CSV prompt,
   the office prompt and the attachment open. A missing accepted path keeps `archivo no encontrado: <name>` (Inc-EN translates it). The placeholders are `C:\path\to\nodes.csv` and
   `C:\path\to\template.docx`.
4. **`U2`.** Adding a `file` attachment validates with `safe_local_path` AND workspace containment at ADD time; a refusal stores nothing and toasts the U1 sentence (the undo snapshot is taken only after the check).
   URL attachments are unchanged.
5. **`INC9M-SEC-F3`.** In `_fetch_gh`, `commit` is bound to `{}` at the top of each branch iteration.
6. **`INC9M-SEC-F4` + `CR` section 1 (architecture).** `safe_local_path` stays in `osopen`. `docs/ARCHITECTURE.md` section 3: `github` and `screens` may import `osopen.safe_local_path` only;
   the inbound ban is "`open_external` is referenced only from `app`"; the `github` row now lists `design` too (pre-existing drift). `tests/test_arch_osopen_callers.py` derives it from the ASTs.
7. **`INC9M-CR-F3`.** The badge arm paints a real `RepoScreen` through a stubbed `fetch`. **`CR-F5`.** `_fetch_gh` calls `progress` before the `.`/`..` `continue`.
   **`CR-F6`.** Two unused imports removed from `tests/test_inc9m.py`. **`CR-F7`.** The `test_inc9l` arm about "single slash" is renamed (a label change).
   **`CR-F8`.** The `text[0] not in "\\/"` guard is dropped (equivalent: surviving mutants N9, N11 of `increment-039`); `github.source_kind(spec)` is public and the badge reads it; `fetch` no longer calls `.resolve()` on an Optional.

**Trace.** Standalone, like `A-113`..`A-121`. Carried by `tests/test_inc9n.py`, `tests/test_arch_osopen_callers.py` and the sealed-arm changes listed in `increment-040-inc9n.md`.

**What is not claimed.** On POSIX every absolute path is refused (`INC9M-CR-F4`, coordinator ruling: mapper is Windows-only for typed paths; nothing was run on POSIX). The device-name
test is `PureWindowsPath.is_reserved()` of Python 3.12 per component; a name it does not know is not refused. A relative text with a `:` inside (`CC:\x`) is still accepted (`A-121`). No real
UNC, `\??\UNC`, console or COM device was ever opened: spies refuse and record, and `preview_csv` is stubbed where a device name is typed. Nothing was measured against a live SMB share,
a live `gh`, a real clone, or another terminal than Textual's headless driver.

### `A-123` -- the Inc-9n review fixes: one containment helper, the document name, V1, V2, FLAKE-3 (`Inc-9o`), dated 2026-10-01

**Authority.** The operator's V1 and V2 (Round 11 of `VERDICT-inc9-2026-09-30.md`) and the coordinator's rulings for `INC9N-SEC-F1`..`F3`, `INC9N-CR-F1`..`F5`. The record is `increment-041-inc9o.md`.

**Statement.** Amends `A-122`; the rest of `A-122` stands.

1. **`confine(text, workspace) -> Path | None`** in `mapper/osopen.py` is the ONLY containment (`INC9N-CR-F2`). `open_external` (file branch), the attachment add and open checks in `app`, and `FactoryScreen._office_path` call it; the three copies
   are deleted. In order: (1) `safe_local_path`, which expands `~` for every caller (add and open now agree: `open_external` did not expand it before); (2) lexical containment with no stat, by path parts after `os.path.abspath` and a case fold
   (`ws2` is not inside `ws`; a relative workspace is judged by its absolute form, `INC9N-CR-F1`); (3) a walk from the workspace down with `os.lstat`, refusing a symlink or any reparse point before anything below it is touched
   (`INC9N-SEC-F3`); (4) only then `resolve()` and a last `is_relative_to`, `OSError` and `ValueError` caught. **Policy: a link inside the workspace is not followed.** The workspace root itself may be a link; only what lies under it is walked.
2. **`lexically_outside(text, workspace) -> bool`** (a fifth name, beside the four the ruling listed; declared): `safe_local_path` accepts the text and step (2) refuses it. It is the same step as `confine`'s, not a second rule, and it is what `V2` needs.
3. **`INC9N-SEC-F1` (HIGH).** `generate office` writes `<document name>-<node id><suffix>`; both names must pass `store.check_map_id` (no `/ \ :`, controls, reserved device, edge dot or space; `store.py` untouched), and the target goes through `confine` before any write.
   A refusal toasts the fixed `document name cannot be used as a file name` and writes nothing. The `generado:` toast names the workspace-relative result.
4. **`V1`.** `attachment must be inside the workspace: use a relative path` when `safe_local_path` accepts the text and `confine` refuses it, at add time and at open time; `U1` stays for allow-list refusals. Both sentences, `PATH_NOT_SUPPORTED` and
   `PATH_OUTSIDE_WORKSPACE`, live in `osopen.py` (`INC9N-CR-F4`); `app` and `screens` import them from there.
5. **`V2`.** When `_office_path` is None because the path lies outside the workspace by text, the factory preview and the generate toast say `template outside the workspace: import it with i`; any other None keeps `archivo de plantilla no encontrado`.
6. **`FLAKE-3` (`INC9N-CR-F3`), test hygiene.** The two palette arms poll `palette._items` (at most 20 pauses) instead of one `pilot.pause()`; the assertions are unchanged. It was a test race, not a user race.
7. **`INC9N-CR-F5`.** Sibling-prefix negative cases on `confine`. **`ARCHITECTURE.md` section 3** lists the four `screens` -> `app` back-edges that exist (`factory.py` x3, `settings.py` x1) and the names `screens` may import from `osopen`.

**Trace.** Standalone, like `A-113`..`A-122`. Carried by `tests/test_inc9o.py`, `tests/test_arch_osopen_callers.py` and the sealed-arm changes in `increment-041-inc9o.md`.

**What is not claimed.** Windows only; nothing was run on POSIX. A file under a cloud-sync folder that carries a reparse attribute (OneDrive placeholders and similar) is refused by the walk like any link; not measured. A hard link is not a reparse point
and is not detected. Between the walk and the write there is a window in which a component could be replaced by a link (a race, not closed). No real UNC, `\??\UNC`, console or COM device and no link to a network target was ever created or opened:
links are junctions or symlinks to a LOCAL directory under a temp path, and spies refuse and record before the real call.

### `A-124` -- the Inc-9o review fixes: normalised components, hard links, invisible names, `confine_reason`, W1, W2 (`Inc-9p`), dated 2026-10-01

**Authority.** The operator's W1 and W2 (Round 12 of `VERDICT-inc9-2026-09-30.md`) and the coordinator's rulings for `INC9O-SEC-F1`..`F4` and `INC9O-CR-F1`..`F6`. The record is `increment-042-inc9p.md`.

**Statement.** Amends `A-123`; the rest of `A-123` stands.

1. **`INC9O-SEC-F1` (HIGH).** `confine` refuses, on the text and before any filesystem call, any component of the expanded path other than `.` and `..` that differs from its `rstrip(" .")` (`...`, `. .`, `..  `, `d `, `d. .`). Windows normalises such a component, so the walk stopped early and `resolve()` followed a link behind it (measured with local junctions, including from the factory preview on render). The `.` exemption is unreachable (pathlib never yields it); declared.
2. **`confine_reason(text, workspace) -> tuple[Path | None, str]`** is now the rule and `confine` is `confine_reason(...)[0]`. Reasons: `ok`, `allow_list`, `outside`, `link`, `normalised`, `unreadable`. `lexically_outside` is `confine_reason(...)[1] == "outside"` (`INC9O-CR-F1`); a text refused by the allow-list or as normalised is not 'outside'.
3. **`W2`.** `path goes through a link: use a real folder inside the workspace` (`osopen.PATH_THROUGH_LINK`) for reason `link`: attachment add and open, the factory template preview and generate, and the import. Attachments: `allow_list` and `normalised` -> U1, `outside` and `unreadable` -> V1, `link` -> W2.
   **Declared deviation, factory template:** the preview and the generate toast keep `archivo de plantilla no encontrado` for `allow_list`, `normalised` and `unreadable` (the sealed Inc-9o V2 pin has UNC and `con` there, and V1 says "attachment"); `outside` -> V2, `link` -> W2. One line to change if the operator wants U1 there.
   **Import:** `link` -> W2, `allow_list` and `normalised` -> U1, the rest -> V1 (as the coordinator's text; V1 says "attachment").
4. **`W1`.** The generate refusal is `document name cannot be a file name: rename it in the map's _nodos.yml (documents)` when the document name is the cause, and `node id cannot be a file name: rename the node` when the node id is. Neither names anything typed. A composed name that `confine_reason` refuses for a link says W2; any other cause says the document sentence (declared).
5. **`INC9O-SEC-F2` (LOW).** Generate and import write a temporary sibling in the target's directory (`tempfile.mkstemp`) and `os.replace` it onto the target, removing the sibling on failure; a template or a target whose `lstat().st_nlink > 1` is refused. **The hard-link sentence `file has several hard links: use a plain file` is not operator-ruled copy** and is declared for the coordinator.
6. **`INC9O-SEC-F3` (LOW).** A document name or node id containing a Unicode category `Cf`, `Zl`, `Zp` or `Co` is refused by `factory` before the name is composed (`store.py` untouched). Includes U+200D (a `Cf`); declared.
7. **`INC9O-SEC-F4` (LOW, test oracle).** The spies (`_no_fs`, `_Walk`, `_Forms`) also patch `ntpath._getfinalpathname`, which `realpath` binds by name.
8. **`INC9O-CR-F2`.** `action_import_office` confines `./templates/<name>` and writes with the same sibling + replace; it no longer follows a `templates` junction.
9. **`INC9O-CR-F5`.** The composed generate name is passed as `./<name>`; so that this works, `safe_local_path` expands `~` only when the TEXT starts with `~` (pathlib drops a leading `./`, so `./~x` was expanded). Effect for every caller: `./~x` and `.\~x` are literal relative names; `~`, `~/x` and `~user` expand as before.
10. **`INC9O-CR-F6`.** `tests/test_palette.py` waits for and asserts a non-empty `palette._items` before it sets the empty query.
11. **`INC9O-CR-F3`, declared (no code):** a different 8.3 form of a drive-absolute path inside the workspace is judged by `resolve()` and reads as `outside` -> V1. **`INC9O-CR-F4`, declared (no code):** an unreadable component (`lstat` fails other than not-found) or a `resolve()` error reads as `unreadable` -> V1 for attachments.

**Trace.** Standalone, like `A-113`..`A-123`. Carried by `tests/test_inc9p.py` and the sealed-arm changes in `increment-042-inc9p.md`.

**What is not claimed.** Windows only; nothing was run on POSIX. A hard link is detected only on the write target and the template, not on an attachment that is opened. A race between the walk and the write is not closed. `mkstemp` creates the sibling with the default temp-file mode; permission carry-over from an overwritten target is not measured. No real UNC, `\??\UNC`, console or COM device and no link to a network target was created or opened: links are junctions or symlinks to a LOCAL directory under a temp path, and `os.link` hard links between two temp files.


### `A-125` -- the Inc-9p review fixes: stream suffix and MAX_PATH in `confine_reason`, hard links at open, the parent re-check, X1, X2, one reason mapping (`Inc-9q`), dated 2026-10-02

**Authority.** The operator's X1 and X2 (Round 13 of `VERDICT-inc9-2026-09-30.md`; both took the recommended option) and the coordinator's rulings for `INC9P-SEC-F1`..`F4`, `INC9P-CR-F1`..`F8`. The record is `increment-043-inc9q.md`.

**Statement.** Amends `A-124`; the rest of `A-124` stands.

1. **`INC9P-SEC-F1` (HIGH).** A stream-type suffix on a link component (`lnk:$I30`, `lnk::$BITMAP`, `lnk:$I30:$BITMAP`, an 8.3 form such as `JLINKN~1:$I30`) made `os.lstat` raise FileNotFoundError, the walk stopped, and `resolve()` followed the junction; an inside junction was returned `ok` and `open_external` called the launcher (measured on `55dc530` with local junctions). Step 1b of `confine_reason` now also refuses, on the text and before any filesystem call, a `:` in any component but the drive anchor, as `normalised`.
2. **Defence in depth, which also closes `INC9P-SEC-F4` (MAX_PATH).** Implemented: after the walk stops on a not-found component, only the WALKED prefix is resolved and the remaining parts are appended lexically (`walked.resolve().joinpath(*tail)`); the OS is never asked about the unwalked tail. The other offered option (resolve the whole path and compare with prefix + tail) was NOT implemented. A not-found component whose path is 260 characters or longer is `unreadable`: without long-path support `lstat` fails on such a path whether or not the component exists, so the walk could stop before a junction it never saw (measured: a 360-character path through a junction created with the `\\?\` prefix was `ok` on `55dc530`). **Declared consequence:** a legitimate path of 260 characters or more whose walk meets a missing component is refused as `unreadable` (V1 for an attachment) even where the volume supports long paths; fail closed.
3. **`INC9P-SEC-F3` (LOW).** `osopen.hard_linked(path)` (moved from `factory`, which imports it) is False only when `lstat` raises FileNotFoundError; any other `OSError` counts as linked (fail closed, so a read error also reads as 'several hard links'). `open_external` (kind `file`) returns the status `attachment has several hard links: replace it with a plain copy` (`osopen.ATTACHMENT_HARD_LINKED`, the coordinator's ruled sentence) for a target with `st_nlink > 1`; `app` shows it without appending the path.
4. **`INC9P-SEC-F2` (LOW).** In `_write_via_sibling`, right after `mkstemp` (and the close of its descriptor) the target's parent is `lstat`ed again; if it is a link or reparse point now, the write is refused with `ParentIsALink` (an `OSError`; the toast reads `no se pudo generar|importar: ParentIsALink`) and the sibling is removed. **Declared: the residual TOCTOU is narrowed, not closed**: the parent can still be swapped after this check. The target comes from `confine_reason`, i.e. resolved, so its parent is never a link unless it was swapped: a workspace whose root is a link (allowed by policy) still works (pinned; an earlier draft compared with the state before `mkstemp`, and a mutant that refused any link parent SURVIVED, which showed the comparison was dead code; removed). If the sibling was created in the folder that was then moved away, the sibling stays in the moved folder (the cleanup follows the new link); that is the attack case, observed in the test.
5. **`X1` (operator).** One hard-link sentence per site: template `template has several hard links: replace it with a plain copy`; output `output file has several hard links: delete or rename it`; import target `templates file has several hard links: delete or rename it` (constants in `factory`). Replaces `A-124` item 5's `file has several hard links: use a plain file`.
6. **`X2` (operator).** A template refused by the path rule (reason `allow_list` or `normalised`) shows U1 in the factory preview and in generate; `archivo de plantilla no encontrado` stays only for a missing or `unreadable` template. **Operator-ruled sealed-arm change:** the Inc-9o V2 pins for UNC, `//h/s` and `con` (`test_inc9o_v2_pin_every_other_missing_template_keeps_the_existing_text`) and the Inc-9n hostile-document arm (`test_inc9n_f1_a_hostile_sidecar_document_is_never_stat_ed_and_the_screen_survives`, four of its five params) now expect U1. Supersedes the declared deviation in `A-124` item 3.
7. **`INC9P-CR-F1`.** `osopen.refusal_sentence(reason, *, surface="attachment")` is the one mapping: `link` W2, `allow_list` and `normalised` U1, `outside` V1, `unreadable` V1 (attachments) and, for `surface="import"`, `templates folder could not be checked: use a real folder named templates inside the workspace` (`INC9P-CR-F3`, coordinator ruling, `osopen.PATH_TEMPLATES_UNCHECKED`). `app._path_refusal`, the import and the factory template (for `link`, `allow_list`, `normalised`) call it; `factory._import_refusal` is deleted. The factory template keeps `V2` and the not-found text in its own small mapping. The architecture allow-list for `screens` is now `safe_local_path`, `confine_reason`, `refusal_sentence`, `hard_linked`, `is_link`, `PATH_NOT_SUPPORTED`, `PATH_THROUGH_LINK` (`PATH_OUTSIDE_WORKSPACE` out; `docs/ARCHITECTURE.md` rows `screens` and `osopen` and the four back-edge lines updated).
8. **`INC9P-CR-F2`, `F4`, `F5`, `F7`, `F8`.** F2: an arm where `mapper.office.resolve` raises during generate (toast `no se pudo generar: <Type>`, tree unchanged, no `.tmp-*`). F4: `lexically_outside` deleted; its assertion stays as a `confine_reason` table in `test_inc9p` (renamed). F5: the factory preview asks `confine_reason` once (`_template` returns the tuple; `_office_path` is its `[0]`; `_missing_text` takes the reason) and the stale 'no stat' docstrings are fixed. F7: an arm pins `..\d \x.pdf` as `normalised` (step 1b before step 2). F8: `test_inc9o_v1_opening_a_file_behind_a_link_toasts_the_workspace_sentence` is renamed `..toasts_the_link_sentence` (a label change; its W2 assertion is unchanged).
9. **`INC9P-CR-F6`, declared (no code).** The atomic write (sibling + `os.replace`) drops the target's metadata: owner, ACL and file attributes of an overwritten target are not carried to the new file, which is a fresh temp file with the default mode. Not measured.

**Sealed-arm changes besides X2.** `test_inc9o_confine_judges_what_resolve_returns_as_a_last_check` now creates `a.pdf` first (a missing file is judged by the resolved walked prefix, item 2; the added counterpart `test_inc9q_sec_f4_the_resolved_walked_prefix_is_the_last_check_for_a_missing_file` covers that case); `test_darkside_census` line `self._missing_text(doc)` is now `self._missing_text(reason)`; the `test_inc9p` arms for the hard-link sentences (three) and the `lexically_outside` table follow items 5 and 8.

**Trace.** Standalone, like `A-113`..`A-124`. Carried by `tests/test_inc9q.py` and the sealed-arm changes in `increment-043-inc9q.md`.

**What is not claimed.** Windows only; nothing was run on POSIX. The 8.3 alias of a junction was not required to exist on the test volume: the 8.3 form is refused on its text. A race between the walk and the write is narrowed (item 4), not closed. A `:` in a component is refused for every caller, including a file name that is legitimate on POSIX. No real UNC, `\??\UNC`, console or COM device and no link to a network target was created or opened: links are junctions to a LOCAL directory under a temp path, and `os.link` hard links between two temp files; the long-path tree was created under a temp path with the `\\?\` prefix and removed.

### `A-126` -- the Inc-9q review fixes: the final-resolve backstop, the colon's own sentence, generate's refusal mapping, the MAX_PATH re-check in UTF-16 units, the preview's hard-link sentence (`Inc-9r`), dated 2026-10-02

**Authority.** Round 14 of `VERDICT-inc9-2026-09-30.md`: the operator's `Y1` (answer "Frase propia") and the coordinator's ruling for `INC9Q-CR-F1`; the review findings `INC9Q-CR-F1`..`F6`, `INC9Q-SEC-F1`, `F2`. The record is `increment-044-inc9r.md`.

**Statement.** Amends `A-125`; the rest of `A-125` stands.

1. **`INC9Q-CR-F1` (HIGH), the final-resolve backstop restored.** Step 4 of `confine_reason` no longer returns the walked prefix plus a lexical tail without asking the OS about the tail. It computes `resolved = walked.resolve().joinpath(*tail)` (always prefix + tail; the `if tail / else` split is folded, `INC9Q-CR-F6`) and `full = (workspace / local).resolve()` (what the consumer reaches); when `normcase(full) != normcase(resolved)` the reason is `link`; when `resolved` is not under the resolved workspace it is `outside`; an `OSError` or `ValueError` from any of the three `resolve()` calls is `unreadable`. **Supersedes `A-125` item 2's "the OS is never asked about the unwalked tail"** (the walked prefix result is kept, and the OS is now asked what the consumer will reach). Measured on `bf68d07` with `lstat` made to raise FileNotFoundError for a real junction `ws/lnk` pointing outside: `confine_reason` returned `ok` and `open_external` launched the outside file; the base `55dc530` refused it. The `A-125` arm `test_inc9q_sec_f4_the_unwalked_tail_is_appended_not_resolved` (new in Inc-9q, not sealed) asserted a proxy (the OS is never asked about `lnk`) and accepted that result; it now asserts the property: nothing behind the link is reachable (a refusal, nothing launched), for a junction pointing outside and inside, for an existing and a missing tail, plus a write arm (an import through a hidden `templates` junction creates no temporary file and no file).
2. **`Y1` (operator).** A `:` in a component other than the drive anchor is its own reason `colon` (step 1b; the trailing dot or space case stays `normalised`). `osopen.refusal_sentence("colon")` is exactly `path not supported: ":" is not allowed in a file name` (`osopen.PATH_COLON`) on every surface (attachment add and open, import, template preview, generate). Fixed, echoes nothing. The other `normalised` cases keep `U1`. The Inc-9q colon arms now expect `colon` instead of `normalised`.
3. **`INC9Q-CR-F2` (MEDIUM).** Generate's target refusal goes through `refusal_sentence(reason, surface="generate")`: `link` W2; `colon` Y1; `normalised` and `allow_list` U1; `unreadable` `output path could not be checked: move the workspace to a shorter folder` (`osopen.PATH_OUTPUT_UNCHECKED`); only a `check_map_id` failure of the document name or node id stays W1 (document / node). `outside` cannot be reached for a name that `check_map_id` accepted (it falls to V1).
4. **`INC9Q-CR-F3` (MEDIUM).** A not-found component whose path is 260 UTF-16 units or more is asked again with the `\\?\` prefix (the text is `abspath`-normalised and step 1b already refused dots, spaces and colons): the re-check finding a link is `link`; finding the component (not a link) lets the walk continue; a FileNotFoundError is a normal missing tail (the step-4 comparison backstops it); any other error is `unreadable`. **Supersedes `A-125` item 2's declared consequence** (a legitimate path of 260 or more is no longer refused for being long). Unmeasured: a UNC workspace (the prefix would be wrong, the re-check reads not-found and the step-4 comparison decides).
5. **`INC9Q-SEC-F1` (LOW).** MAX_PATH is counted in UTF-16 units (`len(text.encode("utf-16-le")) // 2`), not code points.
6. **`INC9Q-SEC-F2` (LOW).** The factory preview shows the X1 template sentence (`template has several hard links: replace it with a plain copy`) when the template is hard-linked, as generate does.
7. **`INC9Q-CR-F4` (LOW).** `STREAM_FORMS` gains a single-letter junction form. **Declared reading:** at the top level `l:$I30` is a drive-relative path to pathlib and `safe_local_path` refuses it as `allow_list` before step 1b (pinned); step 1b sees it only as a component, so the form is `sub/l:$I30` with the junction `sub/l`, and that is what the arm uses.
8. **`INC9Q-CR-F6` (LOW).** The step-4 `if tail / else` is folded (item 1). `docs/ARCHITECTURE.md`: the `osopen` row names the colon refusal, the long-path re-check and the step-4 comparison; `screens` no longer imports `PATH_THROUGH_LINK` (six names), and the back-edge line of `_PromptScreen` is 504.

**Sealed-arm changes.** `tests/test_arch_osopen_callers.py` (allowed names and the docs row check: `PATH_THROUGH_LINK` out, because generate no longer uses it); `docs/ARCHITECTURE.md` back-edge line `498` -> `504` (a line-number pin). The Inc-9q colon arms and the `A-125` tail arm are Inc-9q-new, edited in place.

**Trace.** Standalone, like `A-113`..`A-125`. Carried by `tests/test_inc9r.py`, the edited arms of `tests/test_inc9q.py` and the record.

**What is not claimed.** Windows only; nothing was run on POSIX. No real UNC, `\??\UNC`, console or COM device and no link to a network target was created or opened: links are junctions to a LOCAL directory under a temp path and `os.link` hard links between temp files; the long-path trees were created under a temp path with the `\\?\` prefix and removed. A volume or process with long paths enabled was not measured. The race between the walk and the write is still narrowed, not closed (`A-125` item 4).

### `A-127` -- a lone surrogate in a typed path is refused by the allow-list; the Inc-9r record corrections (`Inc-9s`), dated 2026-10-02

**Authority.** The Inc-9r security review `INC9R-SEC-F3` (LOW, a regression of `929a039`) and the code review `INC9R-CR-F1`, `F3`, `F4` as carried by `B-81`. The record is `increment-045-inc9s.md`.

**Statement.** Amends `A-126`; the rest of `A-126` stands.

1. **`INC9R-SEC-F3`.** `safe_local_path` returns None for any text that contains a character of Unicode category `Cs` (a lone surrogate, such as `\ud800` or `\udc80`), after the type, empty, NUL and leading `-` checks and before any `Path` is built. Cause of the defect: `_utf16_units` encoded the path with `text.encode("utf-16-le")` inside the `FileNotFoundError` handler of the walk, so the outer `except` could not catch the `UnicodeEncodeError`, and `confine_reason` and `open_external` raised for a component such as a lone `\ud800` followed by `/x.pdf`, or `docs/` + a lone `\udc80` + `.pdf` (both were `ok` at `bf68d07`). Now `confine_reason` returns `(None, "allow_list")` (the `U1` sentence) with zero filesystem calls, and `open_external` returns `REFUSED_TYPE` and does not raise. Second guard: `_utf16_units` encodes with `"utf-16-le", "surrogatepass"`, so a lone surrogate counts as one unit and never raises. An astral character (`\U0001F600`) is not category `Cs` (it is `So`), counts as 2 units and is accepted (pinned).
2. **`B-81` record corrections.** Appended to `increment-044-inc9r.md` (nothing rewritten): declared reading 5 is wrong, since an NTFS stream `ab:b.docx` can be an import source (`INC9R-CR-F3`); the mutant table names intended killers, not the first `-x` failure (`INC9R-CR-F4`); `normcase` in the step-4 comparison carries no tested load (`INC9R-CR-F1`).
3. **`INC9R-CR-F3`, the end-to-end arm.** `tests/test_inc9s.py` creates a stream file in a temp directory, imports it with real keys and asserts the Y1 toast and that nothing is written under `templates`.

**Sealed-arm changes.** None.

**Trace.** Standalone, like `A-113`..`A-126`. Carried by `tests/test_inc9s.py` and the record.

**What is not claimed.** Windows only; nothing was run on POSIX. The `Cs` refusal is on the text; whether the Windows API accepts any lone surrogate in a name is not claimed either way. `hard_linked` as a pseudo-reason in `_missing_text` (`INC9R-CR-F2`) stays in `B-81`. The other `B-79` and `B-80` residuals are untouched.

### `A-128` -- an attachment chip opens with real keys and a real click (`Inc-X3`), dated 2026-10-02

**Authority.** `VERDICT-inc9-2026-09-30.md` Round 13, **X3** ("a small increment right after the Inc-9 line closes, with a real-key test"), and the Inc-9p ux review finding `INC9P-UX-F1`. The record is `increment-046-x3.md`.

**Statement.** Standalone; amends no earlier decision.

1. **The defect (pre-existing since about `e359148`).** In the map inspector `tab` reaches an attachment chip (`insp-att-N`), but `enter`, `space` and a click did nothing: no toast, nothing opened.
2. **Cause (confirmed by reading `DsChip`, `FichaInspector` and Textual 8.2.8).** `DsChip.action_activate` posts `DsChip.Changed(selected)`, which carried no widget. `FichaInspector.on_ds_chip_changed` reads `event.control`; `textual.message.Message.control` is a property that returns `None` unless a subclass defines it, so `hasattr(event, "control")` is True and the value is `None`, `widget_id` is `""`, the `insp-att-` prefix test fails and the handler returns silently. Every earlier arm posted `FichaInspector.AttachmentActivated` by hand, which skips that hop.
3. **Fix (1 source file).** `DsChip.Changed` takes the chip, stores it as `chip`, and defines `control` to return it (the convention Textual's own messages follow). `DsChip.action_activate` posts `Changed(self, self.selected)`. `FichaInspector` is unchanged.
4. **Not changed.** The open-time path policy (`_path_refusal` / `open_external` / `confine`) is untouched; its sentences (`V1`, `U1`) and the launcher injection are as sealed. Activating a chip still toggles its `selected` flag, as before.
5. **Arms** (`tests/test_inc9x3.py`, 14 items): real `tab`/`enter`/`space`/`I` or a real click, never a posted `AttachmentActivated`; the launcher is a recording stub in every arm. At 87 columns `I` is pressed first because the inspector is hidden there.

**Sealed-arm changes.** None.

**Trace.** Standalone, like `A-113`..`A-127`. Carried by `tests/test_inc9x3.py` and the record.

**What is not claimed.** Windows only; nothing was run on POSIX. The final hop to the operating system (MAN-01) is not exercised: the launcher is stubbed. Terminal mouse input is Pilot's synthetic click, not a real terminal's.

### `A-129` -- English strings in `osopen`, `github`, the factory screen and the editor (`Inc-EN-1`), dated 2026-10-02

**Authority.** `VERDICT-inc-en-2026-10-02.md` (EN-Q1, the 7-increment plan, EN-1 first) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING ("Todo en inglés, también la UI", `B-71`). The record is `increment-047-en1.md`.

**Statement.** Standalone; amends no earlier decision and rewrites no earlier amendment. Wherever an earlier requirement or amendment quotes one of the Spanish strings below, the string it quotes is now the English one. Only the words change; every refusal sentence (`U1`, `V1`, `V2`, `W1`, `W2`, `X1`, `Y1`), every condition that selects a string and every value-echo rule is as sealed.

| Where | Old | New |
|---|---|---|
| `osopen` status words (values only; the constant names stay) | `abierto` | `opened` |
| | `tipo no abrible` | `cannot open this type` |
| | `destino inválido` | `invalid target` |
| | `esquema no permitido` | `scheme not allowed` |
| | `fuera del espacio de trabajo` | `outside the workspace` |
| | `no se pudo abrir` | `could not open` |
| `github` root meta | `ramas {n} · tags {n} · default …` | `branches {n} · tags {n} · default …` |
| `github` progress labels | `leyendo ramas` | `reading branches` |
| | `calculando métricas` | `computing metrics` |
| | `listo` | `ready` |
| factory | `archivo de plantilla no encontrado` | `template file not found` |
| | `no se puede dibujar: el mapa tiene un ciclo` | `cannot draw: the map has a cycle` |
| | `sin documento` | `no document` |
| | `documento` (default tab name) | `document` |
| | `proceso` (default process name) | `process` |
| | `(vacío)` | `(empty)` |
| | `(sin tags)` | `(no tags)` |
| | `archivo no encontrado: {name}` | `file not found: {name}` |
| | `solo .docx / .pptx / .xlsx` | `only .docx / .pptx / .xlsx` |
| | `no se pudo importar {name}: {Type}` | `could not import {name}: {Type}` |
| | `plantilla importada: {rel}` | `template imported: {rel}` |
| | `ruta del archivo office` | `office file path` |
| | `el documento actual no es office` | `the current document is not an office file` |
| | `generado: {shown}` | `generated: {shown}` |
| | `no se pudo generar: {Type}` | `could not generate: {Type}` |
| editor | `Guardar` / `Cancelar` / `Prever` | `Save` / `Cancel` / `Preview` |
| | `ctrl+s salvar · esc cancelar · tab prever` | `ctrl+s save · esc cancel · tab preview` |
| | `detectados: ` | `detected: ` |
| | `ninguno` | `none` |

**Not changed (declared).** `app.py` paints its own literals `abierto` (the attachment-open toast) and `iniciando` / `leyendo ramas` / `calculando métricas` / `listo` (the connect-repo stage list); they stay Spanish until `EN-5`. `app.py` compares the open status by the constant `OK`, not by its text, so the value change is safe there. The `progress` label that `github.py` passes is stored by the app and never painted.

**Sealed-arm changes.** Label changes only, no assertion weakened, listed in `increment-047-en1.md` section 3.

**Trace.** Standalone, like `A-113`..`A-128`. Carried by `tests/test_en1.py` (a census of the four files' non-docstring literals) and by the relabelled pins in the record.

**What is not claimed.** The census word list is explicit and finite; it does not detect Spanish in general.

### `A-129` correction note -- scope of the `archivo no encontrado` remap (`EN1-REV-F1`), dated 2026-10-02

Appended; `A-129` is not rewritten. `A-129`'s table remaps `archivo no encontrado: {name}` to `file not found: {name}` without saying where. The remap applies to the **office prompt only** (the factory screen's literal). The **CSV prompt's** sentence `archivo no encontrado: {name}` is `app.py:1044`'s own literal and **stays Spanish until `EN-5`**; the CSV pins (`test_inc9m`, `test_inc9n`) are Spanish for that reason. `A-129`'s blanket sentence ("wherever an earlier requirement or amendment quotes one of the Spanish strings below, the string it quotes is now the English one") applies **only at the sites in `A-129`'s table**, not to the same words painted by another file.

### `A-130` -- English strings in the coverage report, the components sheet, the inspector and the rail (`Inc-EN-2`), dated 2026-10-02

**Authority.** `VERDICT-inc-en-2026-10-02.md` (EN-Q1; Round 2, `Z2`) and `VERDICT-inc8-legend-2026-09-28.md` section LANGUAGE RULING (`B-71`). The record is `increment-048-en2.md`.

**Statement.** Standalone; amends no earlier decision and rewrites no earlier amendment. Wherever an earlier requirement or amendment quotes one of the Spanish strings below **as painted by the four files named in the table**, the string it quotes is now the English one; the same words painted by another file (`app.py`, `keymap.py`, `darkside.py`, `components.py`, `store.py`) stay as that file has them until its own increment (see "Not changed" below). Only the words change; no condition, geometry, style, key or row order is touched.

| Where | Old | New |
|---|---|---|
| `screens/coverage` binding labels | `Seleccionar` / `Cerrar` (two keys) | `Select` / `Close` |
| `screens/coverage` columns | `nodo` / `faltantes` / `cobertura` | `node` / `missing` / `coverage` |
| `screens/coverage` empty report | `todo completo.` / `no falta ningún campo requerido.` | `all complete.` / `no required field is missing.` |
| `screens/settings` hint | `tab recorre componentes — el foco es el bloque sólido` | `tab walks the components — focus is the solid block` |
| `screens/settings` demo values | `luna` / `marea` / `noche` | `moon` / `tide` / `night` |
| | `cargando…` / `sistema-leg` | `loading…` / `system-leg` |
| `widgets/inspector` field binding label | `salir del campo` | `leave the field` |
| `widgets/inspector` empty panel | `(selecciona un nodo)` | `(select a node)` |
| `widgets/inspector` header and row labels | `ficha` | `card` |
| | `título` / `estado` / `notas` / `adjuntos` / `cobertura` | `title` / `state` / `notes` / `attachments` / `coverage` |
| | `+ agregar adjunto` | `+ add attachment` |
| | `requerido` (after a missing required field) | `required` |
| `widgets/inspector` state segments | `ok` / `riesgo` / `tarde` / `bloq` | `ok` / `risk` / `late` / `blocked` |
| `widgets/rail` | `no se puede dibujar:` + line break + `el mapa tiene un ciclo` | `cannot draw:` + line break + `the map has a cycle` |
| | `(mapa vacío)` | `(empty map)` |
| | `mapa · {n}n · {m} faltan` | `map · {n}n · {m} missing` |
| | `territorio` / `cobertura {pct}%` | `territory` / `coverage {pct}%` |

**Quoted by an earlier requirement: none verbatim.** `01-requirements.md` was searched for every old string above. Lines that look close and were checked, not amended: the `cobertura` binding label at the `AT-R12`/`AT-R14` lines (the key bar's word, `keymap.py`, `EN-6`); `siguiente faltante` (`keymap.py`); `territorio sin explorar` at the `V4`/`V4a` lines (the legend's row copy in `darkside.py`, `EN-4`; the rail's `territorio` caption is a different string); `borde del territorio` (`app.py`, `EN-5`); `E:riesgo` and the state words `obsoleto`/`estable`/`riesgo` (query data, not copy). The Spanish text of this amendment's old column is pinned only by tests, listed in `increment-048-en2.md` section 3.

**`Z2` (`X3-REV-F3`).** While an attachment chip (`insp-att-*`) holds focus, the hint line and the key bar read `↵ open attachment` in place of the seat's `↵ open card`; on blur the seat's words are restored. Done inside `widgets/inspector` (`FichaInspector.on_descendant_focus` / `on_descendant_blur`), reading the seat's own row through `hint_pair`; `keymap.py` and `app.py` are unchanged, and the seat still says `open card`.

**Not changed (declared).** `app.py` keeps its Spanish `cobertura completa` / `no falta ningún campo requerido` toast, `cobertura {pct} %`, `adjuntos`, `riesgo` / `bloqueado` (`EN-5`); the key bar's `cobertura` (`EN-6`); `components.py`'s `cargando…` default (`EN-4`).

**Sealed-arm changes.** Label changes only, no assertion weakened, listed in `increment-048-en2.md` section 3.

**Trace.** Standalone, like `A-113`..`A-129`. Carried by `tests/test_en2.py` (a census of the four files' non-docstring literals, and the `Z2` arms) and by the relabelled pins in the record.

**What is not claimed.** The census word list is explicit and finite; it does not detect Spanish in general. `Z2` is measured on the map screen at 140 and 87 columns, not on every surface that could host the inspector.
