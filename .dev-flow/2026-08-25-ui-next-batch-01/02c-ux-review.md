# 02c — UX review · PDR gate · `2026-08-25-ui-next-batch-01`

> Lens: `ux-reviewer`. Standard: **ISO 9241-210:2019**, human-centred design activities 1–4.
> Artifact language **English**; the product's UI strings are **Spanish** and stay Spanish.
> Scope: the design under review is `PDR-design-proposal.md` §D1–D5 against `01-requirements.md`
> HLR-N01…N05, with the round-9 variant A «taller» SVGs as the visual spec.
> **No code was changed. Nothing under `prototypes/` was written.**

**Gate verdict: `approved with conditions`.** Four blockers, five majors, four minors. Every
condition in §8 is individually dischargeable and is written as requirement text for
`01-requirements.md`.

---

## 0 · Evidence discipline

Control **C-16** applies to this whole batch: the approving prototype is a **static SVG**
(`generate.py` renders a `Sheet` cell buffer through `console.save_svg`), so it contains no focus
model, no key handling and no widget. Premise **P-10** already recorded this as FALSE. Therefore
every interaction claim below is tagged:

- **verified** — I executed something on this machine (Textual `App.run_test()` + `Pilot`, or the
  shipped `LayeredRenderer`) and read the **painted** result.
- **judgement** — I reasoned over the source and the design. Not a measurement.

Probes were throwaway scripts in the system temp scratchpad, run as
`PYTHONUTF8=1 python …` against the repo's installed **textual 8.2.8 / rich 15.0.0 / Python 3.12.7**
and the repo's own fixture map `maps/legacy` (8 nodes, 4 leaves, 5 schema fields). They are named
`P-UX1`…`P-UX6` below and were not added to the repo.

| probe | what it drove | what it read |
|---|---|---|
| `P-UX1` | `pilot.press` on a rail/canvas/inspector screen | fired actions, `app.focused`, component renders |
| `P-UX2` | same, plus `screen._compositor.render_strips()` | painted cells and their `Style.bgcolor` |
| `P-UX3` | `LayeredRenderer.render` at `w=58`; real `MapperApp` + `MapScreen("legacy")` | rendered `Text`, screen stack after `escape` |
| `P-UX4` | `LayeredRenderer` sweep 2…12 leaves; three-region layout at 6 terminal widths | painted rows, measured region widths |
| `P-UX5` | `darkside.keybar` at 3 widths | truncated plain text, cell counts |
| `P-UX6` | widget-level `escape` binding vs screen-level | which action fired, focus destination, retained value |

---

## 1 · Context of use (ISO 9241-210 activity 1)

Stated before any criterion, because a UX criterion with no context has nothing to be true about.

| dimension | statement |
|---|---|
| **User** | One operator — the repository's author. Expert in the domain and in the tool. Single user; no second cohort, no novice path to design for. |
| **Task** | *Legacy-repo archaeology*: walk a large map of an inherited system, find nodes whose required schema fields are empty, fill them in, and return to the walk **without losing the place**. The primary flow under review is US-N04 → US-N01: coverage report → node → first missing field → type → commit → next gap. |
| **Environment** | A single local terminal on Windows 11. Keyboard-only, mouse not required. Width-1 glyphs only. Reference geometry 118 × 31 cells. Dark ground (`#000000`), depth by background step, borders only on modals. |
| **Posture** | **operated + read** — long working sessions in this one screen, not glances. This is what makes focus ambiguity expensive: a wrong keystroke every few minutes across an hour is a different cost from a wrong keystroke once. |

**Consequence for the design.** In an *operated* posture the screen must answer, at all times and
without a keystroke, the question **"where does my next key go?"**. That is the axis on which this
PDR is weakest, and §3 is the answer to it.

---

## 2 · Cognitive walkthrough — US-N04 → US-N01

Six steps. At each: (a) will the operator know what to do, (b) will they see the control,
(c) will they recognise it does what they want, (d) will they understand the feedback.
**A "no" on any of the four is named.**

### Step 1 — open the coverage report

Operator presses `m`.

- (a) know what to do — **NO.** The key exists (`MapScreen.BINDINGS`, `app.py:1070`) but is not
  visible. **Verified (`P-UX5`):** the current `MapScreen` keybar is **216 cells** of content;
  `darkside.keybar` truncates it to the 118-cell width and the painted tail is
  `…  view f foco  o outline  r r…`. `m cobertura` is **cut off**. The one affordance that starts
  the batch's primary flow is not on screen.
- (b) see the control — no control; a key only.
- (c) recognise — n/a.
- (d) feedback — a modal appears. Fine.

### Step 2 — choose a row and press `↵`

- (a) **NO.** `CoverageScreen` (`screens/coverage.py`) composes a title, a `DataTable` and nothing
  else — no keybar, no hint line. `↵ ir` and `esc cerrar` are bound (`:21-25`) and shown nowhere.
- (b) yes — the row cursor is a solid `#1783ff` block (`:57-60`).
- (c) plausible — a row cursor plus a modal reads as "pick one". Judgement.
- (d) the modal dismisses. **Weak:** dismissal alone does not tell the operator whether the jump
  happened or the selection was rejected. `action_select` silently `dismiss(None)`s when the cell
  key is not a node id (`:126-135`), and the *empty* state — "todos los campos requeridos están
  completos" — is added as a **selectable table row with no key** (`:91-97`), so pressing `↵` on it
  dismisses with `None` and produces **no message at all**. The operator asked a question and got
  silence. Finding **M5**.

### Step 3 — land on the node, focus the first missing field

This is LLR-N04.2 and it is where the design is not yet decidable.

- (a) n/a (system move).
- (b) **NO — this is blocker B1.** **Verified (`P-UX2`):** with focus in an inspector `Input`, the
  painted screen carries **28 background cells in `#1783ff` across 3 rows** — the canvas selection
  block (`layered.py:219`, `bold GROUND on ACCENT`), the `DsSegmented` active option, the selected
  `DsChip` — and the `Input` that actually holds focus paints **none of them**. Blue marks three
  things that are *not* live and does not mark the one that is.
- (c) **NO.** Nothing distinguishes the focused field from its siblings. LLR-N01.3 paints *every*
  required-empty label in `ALERT`; the field the operator is standing in looks exactly like the two
  below it.
- (d) **NO.** No requirement states what the operator observes on arrival.

Additional measured fact for the same step: **`DsChip` renders its focused state and its selected
state byte-identically.** **Verified (`P-UX1`):**

```
DsChip selected(unfocused) render: <text ' acta.pdf ' [] 'bold #000000 on #1783ff'>
DsChip focused(unselected) render: <text ' wiki '     [] 'bold #000000 on #1783ff'>
```

`components.py:418` is `if state == "focused" or self.selected:` — one branch, one render. The
inspector's attachment list (LLR-N02.1) is built from these chips, so "which attachment will `↵`
open" is unanswerable from the screen.

### Step 4 — type the value

- (a) yes, once focus is understood.
- (b) yes — Textual's `Input` paints its own cursor.
- (c) **NO.** Nothing on screen says the map keys are now inert. **Verified (`P-UX1`):** with an
  `Input` focused, `press("j")` yields `value='j'`, `fired=[]` — P-11 reproduced. The operator who
  types a value and then presses `j` to move on gets a `j` in their data and no navigation, with no
  explanation. `HintLine` is the natural seat for this and LLR-N01.6 already adds `set_hint`, but
  **no requirement says what it must say while a field is focused.** Finding **M4**.
- (d) — see (c).

### Step 5 — commit

- (a) **NO — three sources, three answers.** `PDR §D2` says commit on `Input.Submitted` (i.e. `↵`)
  or blur. The prototype's inspector footer (`generate.py:289-292`) says `ctrl+s guardar` ·
  `esc descartar`. `KEYMAP` says `ctrl+s → guardar` and `esc → cancelar` (`keymap.py:47-48`). The
  operator cannot hold three protocols. Finding **M3**.
- (b) the prototype paints the footer; the design does not require one.
- (c) — see (a).
- (d) **Data-loss finding, B4.** `_push_snapshot` is called at exactly three sites — `app.py:1387`
  (`toggle_focus`), `:1468` (`add_child`), `:1512` (`archive`). **No ficha-edit path pushes a
  snapshot**, and no LLR in HLR-N01 or HLR-N05 adds one. So after committing an edit to disk, `u`
  does not undo it — it pops the *previous structural* snapshot and overwrites the graph, taking
  the edit with it. HLR-N05 moves the stack to the `App` and makes this survive screen round-trips,
  which makes the wrong-restore *more* reachable, not less.

### Step 6 — ask for the next gap

- (a) **NO — blocker B3.** The prototype's worklist strip reads `⇥ ir` (`generate.py:337`) and
  `KEYMAP` binds `tab → vista previa`. **Verified (`P-UX1`):** a screen-level `tab` binding
  **disables focus traversal for the entire screen** — nine `tab` presses from no focus produced
  `focus = None` nine times and fired the bound action nine times. Binding `tab` on `MapScreen`
  makes the inspector unreachable by keyboard. Not binding it makes `⇥ ir` dead. Both cannot hold.
- (d) exhaustion feedback is required by LLR-N04.3 / `AT-N04c`, but its *observable* is unspecified
  (toast? hint line? notify?).

**Walkthrough result: 8 "no" answers across 6 steps, 5 of them on step 3 and 5.**

---

## 3 · The focus model — the question the SVG could not answer

**Short answer: a solid blue block is not sufficient, and the design as written has no focus
signal at all.**

### 3.1 · What is measured

| observation | evidence | tag |
|---|---|---|
| Tab traversal across three regions works and is stable — `ListView#map-rail → Canvas#map-canvas → Input → DsSegmented → DsChip → wraps to rail` | `P-UX2`, six `tab` presses on a rail/canvas/inspector screen with **no** `tab` binding | verified |
| A screen-level `tab` binding kills that traversal completely | `P-UX1`, nine presses, zero focus moves | verified |
| `shift+tab` from a focused `Input` moves focus out (no screen binding claims it) | `P-UX1` | verified |
| With focus in an inspector `Input`, **28 cells of `#1783ff` background** are painted, none of them on the focused widget | `P-UX2` compositor strips | verified |
| `DsChip` focused ≡ `DsChip` selected, character for character and style for style | `P-UX1` | verified |
| `DsSegmented` *does* carry a focus mark: a 1-cell `▐` in `ACCENT`, prepended | `P-UX1` — focused `'▐ ok   riesgo …'` vs blurred `' ok   riesgo …'` | verified |
| That focus mark **shifts the whole control one column right** when it gains focus | same renders, plain strings differ by one leading cell | verified |
| A plain `Static` canvas takes focus (`has_focus == True`) but paints no change unless its own `render()` reacts | `P-UX1`, `P-UX6` | verified |
| Textual's *default* `ListView` CSS does distinguish focused (`on #0178d4`) from blurred (`on #153854`) — but those are Textual's colours, not darkside's, and the prototype's rail (`a_rail`, `generate.py:224`) fills the selected row with `on ACCENT` flat, discarding the distinction | `P-UX2` row-0 strips | verified |

### 3.2 · The diagnosis

`darkside` has exactly **two** background channels available: the grey step
(`GROUND → PANEL → STEP`) for depth, and `ACCENT` for interactivity. The design currently spends
`ACCENT` on **selection** in three different regions simultaneously, and spends nothing on
**focus**. The two concepts are not the same and the operator needs both at once: *which node am I
working on* (selection, must persist while I am typing in the inspector) and *where does my next
key go* (focus, changes constantly). One channel cannot carry two orthogonal states.

Borders are unavailable — CON-4 reserves them for modals — which is correct and is why the answer
must be a background, not a frame.

### 3.3 · Recommended model (judgement, built on the measurements above)

Three rules, all observable through the shipped surface:

1. **Focus is the region's background step.** The live region's container lifts one step
   (`GROUND → PANEL`, or `PANEL → STEP`); the two dead regions stay at their base. This is
   depth-by-background — the design system's own primary mechanism — and it is legible as a large
   area rather than a glyph, which is what an *operated* posture needs.
2. **Selection stays the blue block, but only in the live region.** A selection in a dead region
   paints `STEP`, not `ACCENT`. This satisfies CON-4 literally: blue is reserved for
   *interactivity*, and a selection you cannot currently act on is not interactive. It also makes
   **at most one `ACCENT` block on screen at any time** — a property a pilot can assert by counting
   painted cells, exactly as `P-UX2` did.
3. **Focus is also named in words.** The hint line states the live region (`rail` · `mapa` ·
   `ficha`) and, inside a field, what the escape key is. This is the accessible fallback, and it is
   the part a pilot can assert without reading colours.

Within the inspector, the focused *row* additionally gets the `▐` accent caret that `DsSegmented`
already implements — extended to `Input` rows and to `DsChip`, and painted in a **reserved gutter
column** so gaining focus does not shift the control sideways (fixing the measured 1-column jitter).

Region movement is `tab` / `shift+tab` — which works out of the box and is measured — plus
`h`/`l`-style direct keys if the operator wants them, **provided no `MapScreen`-scope binding
claims `tab`**.

---

## 4 · The escape hatch

**The key is `escape`, and today it is wired to the worst possible thing.**

**Verified (`P-UX3`), driven against the real shipped `MapperApp` + `MapScreen("legacy")` through
`pilot.press`, not a proxy:**

```
after '/': focused = Input search-input
typed 'acta': input value = 'acta'
after ESC: screen stack = ['Screen', 'HomeScreen'] | focused = DataTable
```

Pressing `escape` while typing in an `Input` on `MapScreen` **pops the whole map screen and returns
the operator to `HomeScreen`, discarding the typed text.** The cause is `app.py:1072` —
`("escape", "back_or_home")` — combined with a measured Textual fact: **a screen-level `escape`
binding fires even while an `Input` has focus** (`P-UX1`: `fired=['esc']`, focus stayed on the
`Input`). Textual's `Input` does not claim `escape`, and does not blur on it.

The PDR proposes an inspector full of `Input`s on this same screen and says nothing about `escape`.
Shipped as designed, the operator's habitual "get me out of this field" gesture throws away their
work and their place — in a task whose whole point is *not losing your place*. **Blocker B2.**

### The fix, verified

A widget-level binding on the field input claims `escape` before the screen's. **Verified
(`P-UX6`):**

```
escape with FieldInput focused: LOG = ['leave_field'] | focus now = Canvas | value kept = 'acta'
escape with canvas focused:     LOG = ['leave_screen'] | focus now = Canvas
```

One key, two meanings, disambiguated by focus and nothing else: **`esc` leaves the field; `esc`
again leaves the map.** That is a stack, which is what the operator's mental model of `esc` already
is. The typed value survives the first `esc` (measured) — leaving the field is not discarding it.

### What makes it *discoverable*, not merely documented

Documentation in `?` does not count; the operator must not have to ask. Three shipped signals:

1. **The hint line changes while a field holds focus** — `set_hint` (LLR-N01.6) exists for exactly
   this. Spanish, e.g. `editando «estado» · esc salir del campo · ctrl+s guardar · j/k inactivos`.
   This is one line of painted text a pilot can read back.
2. **The inspector footer names it persistently** — the prototype already draws
   `ctrl+s guardar` · `esc descartar` at `generate.py:289-292`. Keep the seat, fix the verb:
   `esc` must mean *salir del campo*, not *descartar*, or the operator will avoid pressing it.
3. **The keybar's group swaps to `editar` when focus enters the inspector**, so `esc` is on the bar
   at the moment it is needed — which is also the only way the truncated bar (§5) can stay honest.

---

## 5 · Discoverability — is `… +6  ? todas` honest and sufficient?

**The marker is the right idea and is currently unimplementable by the shipped code.**

**Verified (`P-UX5`):**

| measurement | value |
|---|---|
| natural length of `MapScreen`'s keybar content | **216 cells** |
| painted at width 118 | 118 cells, ending `…  view f foco  o outline  r r…` |
| bindings named in the bar's own group list | 17 |
| bindings actually visible at 118 | **9** — 8 are cut, including `m cobertura`, the entry point of the primary flow |
| `KEYMAP` entries never on the bar at all | **16 of 33** |
| duplicate keys in `KEYMAP` | `f` (doors:fábrica / view:alternar foco), `j`, `k`, `↵`, `esc` |

Two independent defects:

1. **The count does not exist.** `darkside.keybar` ends with
   `text.truncate(width, overflow="ellipsis")` (`darkside.py:122`) — a bare `…`, mid-word, with no
   number and no key. The prototype's `… +6  ? todas` is **hand-drawn in the prototype only**
   (`generate.py:303-305`, appended after `darkside.keybar` returns). LLR-N03.5 requires a marker
   "naming the count hidden and the key that reveals the rest" and **no code produces it**; nothing
   in the PDR assigns that work. The count must also be *true* — a `…` that hides 8 while claiming
   `+6` is worse than no marker, because it converts an obvious omission into a specific false
   statement.
2. **The width is a lie.** `KeyBar.set_groups` calls `darkside.keybar(self.groups)` with the
   **default `width=118`** (`chrome.py:37-39`), ignoring `self.size.width`. `TabStrip` gets this
   right — it re-renders `on_resize` with the real width (`chrome.py:21-22`). On any terminal that
   is not exactly 118 wide the bar either overflows its widget or truncates at the wrong column,
   and the count derived from it is wrong by construction.

**Verdict on honesty:** the marker is honest *in intent* and the intent should be kept, on one
condition — the count must be computed from the same measurement that did the truncating, at the
widget's real rendered width, and it must name the revealing key (`?`). Anything less is a vacuous
discoverability claim: `AT-N03d` as currently worded ("truncation is visible when the bar
overflows") passes on a bare `…`, which is precisely the check the control catalog would call
vacuous. It must assert the **number** and the **key**, and it must assert the number equals the
count actually dropped.

`?` and the palette also have to survive the scope model: the five duplicate keys above mean
"help shows exactly the keys that work" is only true once every `KEYMAP` entry is assigned a scope
that resolves them. `f` is the awkward one — `doors:fábrica` and `view:alternar foco` both plausibly
live on `MapScreen`, and the PDR's rule ("two bindings may share a key only if their scopes differ")
does not by itself save it if `doors` is app-scope.

---

## 6 · Observable UX acceptance criteria

Form: *when the operator does X, they observe Y on the rendered screen*. `test` = drivable through
the real mechanism (`App.run_test()` + `Pilot.press`, reading painted `Strip`s or widget renders —
never `.focus()` in place of a keystroke, never a direct `action_*` call where the story promises a
key). `inspection` = a judgement about feel with no shipped observable; declared, not automated.

| id | criterion | mechanism | kind | ties to |
|---|---|---|---|---|
| **UX-01** | With focus anywhere on `MapScreen`, exactly **one** contiguous run of `#1783ff` background is painted in the whole compositor output. | `pilot.press` to each region; count `bgcolor` cells in `screen._compositor.render_strips()` | **test** | B1 |
| **UX-02** | After `tab`, the region whose container background changed step is the region containing `app.focused`. | `pilot.press("tab")`; compare painted container background against `app.focused`'s ancestry | **test** | B1 |
| **UX-03** | `DsChip(selected=True, focused=False).render()` **!=** `DsChip(selected=False, focused=True).render()`. | render both, compare `Text` and spans | **test** | B1 |
| **UX-04** | Focusing `DsSegmented` does not change the column at which its first option is painted. | render focused and blurred, compare the offset of the first option | **test** | minor m1 |
| **UX-05** | The hint line names the live region in Spanish (`rail` \| `mapa` \| `ficha`) and its text changes when focus crosses a region boundary. | `pilot.press("tab")`; read `HintLine` rendered text | **test** | B1 |
| **UX-06** | `escape` with an inspector field focused: `MapScreen` is still the top of `app.screen_stack`, focus is on the canvas, and the field's value is unchanged. | `pilot.press` to focus, type, `press("escape")`; read screen stack + `app.focused` + value | **test** | B2 |
| **UX-07** | `escape` with the canvas focused pops `MapScreen`. | `press("escape")`; read screen stack | **test** | B2 |
| **UX-08** | While a field holds focus, the painted hint line contains the escape key **and** states that the single-letter map keys are inactive. | read `HintLine` text | **test** | M4 |
| **UX-09** | `tab` pressed 5× from the canvas visits rail, canvas and inspector and returns to the start; no screen action fires. | `pilot.press("tab")` ×5; record `app.focused` and an action spy | **test** | B3 |
| **UX-10** | Typing `j` in a focused field produces `j` in the field and moves the map cursor zero nodes. | `press("j")`; read field value and `nav.cursor` | **test** | LLR-N01.5 / `AT-N01d` |
| **UX-11** | After `↵` on a coverage row, the painted inspector shows a focus caret on the row whose label equals the `SchemaField.label` of the node's first required-empty field — asserted against the label, not the key letter. | `press("m")`, `press("enter")`; read inspector rows | **test** | LLR-N04.2 / `AT-N04a` |
| **UX-12** | The keybar's truncation marker names an integer **equal** to the number of bindings dropped at the widget's rendered width, and names `?`. | render the bar at 3 widths; compare the marker's integer to `len(all) - len(shown)` | **test** | M1 |
| **UX-13** | Every key named on the painted keybar fires a real action on the active screen. | for each key parsed off the painted bar, `pilot.press` it and assert an action fired | **test** | `AT-N03a` |
| **UX-14** | Committing an inspector edit then pressing `u` restores the field's previous value, observed through a fresh `MapStore.load`. | `press` to edit, commit, `press("u")`, reload from disk | **test** | B4 |
| **UX-15** | Coverage with nothing missing: the operator sees a message and the report has zero selectable rows. | `press("m")` on a complete map; read `DataTable.row_count` and the painted message | **test** | M5 |
| **UX-16** | Opening a refused attachment (`javascript:`, `file:`, UNC) paints a message naming the refusal; the launcher is not called. | `press` the open key with a `RecordingLauncher`; read the toast and call count | **test** | LLR-N02.5 / `AT-N02d` |
| **UX-17** | The event toast clears itself; it does not persist across an unrelated action. | perform an action, then another, read `#map-toast` | **test** | minor m3 |
| **UX-18** | The screen at 118 × 31 reads as one instrument rather than three competing panels; the eye lands on the live region first. | operator inspection against the round-9 SVG | **inspection** | — |
| **UX-19** | The rail's constellation lattice reads as *territory* rather than decoration at real map sizes. | operator inspection; `a_rail` uses a seeded random field, which does not exist in the product | **inspection** | — |
| **UX-20** | Save latency on `MapStore.save` per commit is not perceptible in a long session. | not measured this batch; see §7 | **inspection** | — |

---

## 7 · The whole user experience — errors, empty and slow states

ISO 9241-210 principle *"the design addresses the whole user experience"*. What the PDR covers and
what it does not:

| state | covered? |
|---|---|
| Required field empty | yes — LLR-N01.3, alert tone + meter |
| Hostile file-derived text | yes — LLR-N01.8, `AT-N01e`, C-17 |
| Refused attachment scheme | partly — LLR-N02.5 says "refused and reported"; **where** the report is painted is unspecified (UX-16) |
| Coverage complete | partly — LLR-N04.3 requires exhaustion reporting for the *worklist action*; the *report screen's* empty state is an unlabelled selectable row (M5) |
| Declined destructive confirm | yes — LLR-N05.2, byte-unchanged files |
| Undo on empty stack | yes — LLR-N05.4 |
| **Undo of a field edit** | **no — B4** |
| **Save failure** (disk full, file locked, permission) | **no requirement.** Every commit writes to disk; nothing states what the operator observes when the write fails. The current `_event_toast` has no error path. |
| **Save latency** | **no requirement.** One save per commit is right (LLR-N01.4), but nothing bounds or acknowledges the pause. `DsSpinner` exists unused. |
| **Map too large for the canvas** | **no — M2**, see §8 C6 |
| Empty map / node with no schema | **not covered.** `LayeredRenderer` returns `Text("(no map loaded)")`; the inspector's behaviour on a schema-less graph is unstated. |

**Declared out of scope for this batch, in writing:** save-failure messaging and save-latency
feedback. They are real gaps; I am not making them conditions because neither is on the primary
flow and both are one small increment each. They belong in the batch's Pending items.

---

## 8 · Findings and conditions

Each condition is individually dischargeable. The requirement text is paste-ready for
`01-requirements.md`; ids continue the existing series and introduce **HLR-N06 (focus and
navigation model)**, which the batch currently lacks entirely.

### Blockers

| # | finding | evidence |
|---|---|---|
| **B1** | No focus signal exists. Three regions; `#1783ff` marks selection in all three at once and never marks focus. `DsChip` focused ≡ selected. | verified `P-UX1`, `P-UX2` |
| **B2** | `escape` while typing pops `MapScreen` and discards the text — measured on the shipped app today, carried forward unchanged by the design. | verified `P-UX3` |
| **B3** | `tab` is claimed by `KEYMAP` and by the prototype's worklist (`⇥ ir`); a screen `tab` binding disables focus traversal entirely, making the inspector keyboard-unreachable. | verified `P-UX1` |
| **B4** | Committing a field edit pushes no undo snapshot; `u` will restore an older structural snapshot and destroy the edit. | verified (call-site census: `app.py:1387`, `:1468`, `:1512` only) |

### Majors

| # | finding | evidence |
|---|---|---|
| **M1** | The keybar truncation marker does not exist in code (bare `…`), and `KeyBar` renders at a hard-coded 118 instead of its real width. `m cobertura` — the entry to the primary flow — is currently cut off. | verified `P-UX5`, `chrome.py:37-39` |
| **M2** | Density: at a 58-column canvas the layered renderer supports **3 leaves per level**. The repo's own 4-leaf fixture already merges adjacent cards, and at ≥5 leaves the coverage-letters row is clipped mid-field — which **misreports coverage on the exact task this batch exists to serve**. | verified `P-UX3`, `P-UX4` — see §9 |
| **M3** | Three contradictory commit protocols (PDR `↵`/blur · prototype `ctrl+s`/`esc` · `KEYMAP` `ctrl+s`/`esc`). | judgement over the three sources |
| **M4** | No requirement for edit-mode feedback; the operator is not told map keys are suppressed. | verified `P-UX1` (behaviour), judgement (absence of a requirement) |
| **M5** | `CoverageScreen` has no keybar/hint line, and its "todo completo" empty state is a selectable row that `↵` dismisses in silence. | `screens/coverage.py:68-97`, `:126-135` |

### Minors

| # | finding |
|---|---|
| **m1** | `DsSegmented`'s focus mark shifts the control one column right (verified `P-UX1`). Reserve a gutter. |
| **m2** | `LayeredRenderer`'s header line computes **69 cells** at a 58-column canvas (verified `P-UX3`); its two spacers are both derived from `avail`. |
| **m3** | `_event_toast` never clears; the prototype's comment says "single toast seat, auto-clearing" (`generate.py:318`). |
| **m4** | Five duplicate keys in `KEYMAP` (`f`, `j`, `k`, `↵`, `esc`, verified `P-UX5`). The PDR's scope rule resolves four; `f` (doors vs view) needs an explicit decision because `doors` is app-scope. |

### Conditions for approval

> **C1 (B1) — new HLR-N06 + LLRs.**
> **HLR-N06.** The system **shall** make the region that receives keyboard input observable on the
> rendered screen at all times, distinctly from the region that holds the selection.
> - **LLR-N06.1** `MapScreen` **shall** render exactly one region as *live*, and the live region
>   **shall** be distinguishable on the rendered screen from the other two by its container
>   background step, independently of any selection block.
> - **LLR-N06.2** A selection in a region that is not live **shall not** be painted in
>   `darkside.ACCENT`. At most one `ACCENT` background run **shall** be painted on `MapScreen` at
>   any time.
> - **LLR-N06.3** `DsChip` **shall** render its focused state distinguishably from its selected
>   state; the two renders **shall not** be equal.
> - **LLR-N06.4** The hint line **shall** name the live region in Spanish, so the live region is
>   observable as plain text.

> **C2 (B2) — the escape hatch.**
> - **LLR-N06.5** `escape` pressed while an inspector edit surface holds focus **shall** move focus
>   to the canvas and **shall not** pop `MapScreen`; the field's value **shall** be preserved.
>   `escape` **shall** pop `MapScreen` only when focus is on the canvas or the rail.
> - **LLR-N06.6** While an inspector edit surface holds focus, the key that leaves the field
>   **shall** be named on the rendered screen, not only in the help overlay.

> **C3 (B3) — `tab` is the region key.**
> - **LLR-N06.7** No `map`-scope binding **shall** claim `tab` or `shift+tab`. The `KEYMAP` entry
>   `tab → vista previa` **shall** be re-scoped away from `map`, and the coverage-worklist advance
>   action **shall** be bound to a key that is not `tab`.
> - **LLR-N06.8** Pressing `tab` repeatedly **shall** visit rail, canvas and inspector in a stable
>   order and wrap, with no screen action firing.

> **C4 (B4) — an edit is undoable.**
> - **LLR-N05.5** Committing an inspector edit **shall** push an undo snapshot before
>   `MapStore.save`, so that `u` restores the value the field held before the commit, observed
>   through a fresh `MapStore.load`.

> **C5 (M1) — the truncation marker tells the truth.**
> - **LLR-N03.5 (amended)** When the keybar's content exceeds its **rendered** width, it **shall**
>   render a marker naming the exact number of bindings hidden and the key that reveals them, and
>   `KeyBar` **shall** recompute from `self.size.width` on resize. `AT-N03d` **shall** assert that
>   the integer in the marker equals the number of bindings actually dropped.

> **C6 (M2) — the canvas gets room, or says it cannot.**
> - **LLR-N06.9** The rail and the inspector **shall** each be collapsible by a named key, and the
>   canvas **shall** receive their columns when collapsed.
> - **LLR-N06.10** When a card is too narrow to render its schema-letters row in full, the renderer
>   **shall** render a summary that cannot be mistaken for a complete row (e.g. `3/5`), and
>   **shall not** render a truncated letters run.

> **C7 (M3) — one commit protocol.**
> - **LLR-N01.9** Exactly one commit key and one leave key **shall** be defined for an inspector
>   field, named identically in `KEYMAP`, in the inspector footer and in the help overlay.

> **C8 (M4) — edit mode announces itself.**
> - **LLR-N01.10** While an inspector edit surface holds focus, the hint line **shall** state that
>   the single-letter map keys are inactive and **shall** name the key that leaves the field.

> **C9 (M5) — the report's empty state is an empty state.**
> - **LLR-N04.4** When no required field is missing anywhere, the coverage report **shall** render
>   an empty state that is not a selectable row, and the worklist action **shall** report
>   exhaustion on the rendered screen.

**Minors m1–m4 are notices, not conditions** — declared, not blocking.

---

## 9 · Density and the width budget

**The number: at a 58-column canvas the layered renderer supports 3 leaves per level. The
repository's own smallest legacy fixture — 4 leaves — already fails.**

### How I got it (verified, `P-UX3` + `P-UX4`)

The constraint is in `views/layered.py:99-107`. `avail = w - 2`; `card_w` starts at
`min(26, max(14, widest))` and, when the leaf row does not fit, collapses to
`max(9, (avail - (n-1)*gap) // n)` with `gap = 3`. Independently, the legacy card body writes a
schema-letters row at `xx += 3` per field (`:180-185`). The fixture schema has **5 fields**, so that
row needs **15 columns** inside a card whose content starts at `cx + 1`. **A card narrower than 15
cannot hold its own coverage row.** Solving `n*(15+3) - 3 ≤ w - 2`:

| leaves | canvas columns needed | terminal columns needed (canvas + rail 24 + inspector 36) |
|---|---|---|
| 2 | 35 | 95 |
| 3 | **53** | **113** |
| 4 | 71 | 131 |
| 6 | 107 | 167 |
| 8 | 143 | 203 |

At the design's 118 × 31 the canvas is **58** (measured, not assumed: a `1fr` canvas between a
width-24 rail and a width-36 inspector measured `58` at terminal 118). 58 ≥ 53, so **3 leaves fit.
4 do not.**

### What the failure actually looks like — painted, at `w = 58`

The canvas clips at `avail`, so nothing "overflows" and no error is raised. It **degrades
silently**:

```
3 leaves   | D✓ O✓ E✓ C✓ N✓     D✓ O✓ E✓ C✓ N✓     D✓ O✓ E✓ C✓ N✓|   clean
4 leaves   | D✓ O✓ E✓ C✓ N✓D✓ O✓ E✓ C✓ N✓D✓ O✓ E✓ C✓ N✓D✓ O✓ E✓ C✓ N|   cards merged, last field cut
6 leaves   | D✓ O✓ E✓ C✓ D✓ O✓ E✓ C✓ D✓ O✓ E✓ C✓ D✓ O✓ E✓ C✓ D✓ O✓ E|   N never shown at all
```

with titles collapsing to `▐ subsist…` (8 chars) at 4 leaves and `▐ subsi…` (6 chars) at 6.

**This is the finding, and it is worse than a legibility complaint.** At 6 leaves the `N` field is
not painted for any card. On this screen a field that is *present* and a field that is *clipped*
look identical — there is no marker. The operator's entire task is deciding which fields are
missing. The canvas, at the width this layout gives it, **silently misreports the answer to the
question the batch exists to answer.**

### Answer to "must the rail/inspector widths be adjustable?"

**Yes — measured, not judged.**

| terminal | rail | canvas | inspector |
|---|---|---|---|
| 140 | 24 | 80 | 36 |
| 118 | 24 | **58** | 36 |
| 100 | 24 | 40 | 36 |
| 80 | 24 | **20** | 36 |
| 60 | 24 | **1** | 36 |

The layout carries **60 columns of fixed chrome**. At 80 columns — an entirely ordinary terminal —
the canvas is 20 cells and holds a single 17-cell card. Below 60 the canvas is one column wide. The
widths must be collapsible (condition **C6**), and the clipped-coverage row must announce itself
rather than lie (**LLR-N06.10**).

Canvas pan / fold / minimap is explicitly batch 2 and I am **not** asking for it here. C6 is the
minimum that keeps batch 1 from shipping a screen that misstates coverage: give the canvas the
columns back on demand, and never paint a truncated letters run as if it were a whole one.

---

## 10 · What was NOT evaluated, and why

Stated in writing, per the discipline this lens owes.

- **Evaluation with real users was not performed.** ISO 9241-210 activity 4 asks for user-based
  evaluation. This team is one person, who is also the author of the design under review. What was
  performed instead is **inspection with declared criteria** — a cognitive walkthrough over the
  task named in §1 — plus automated walkthroughs driving the real Textual mechanism. A `Pilot`
  press is evidence about the *mechanism*; it is not evidence about a *person*. No finding here
  should be read as "an operator was observed doing this".
- **Nothing was evaluated against the implemented batch**, because it does not exist yet. All
  probes ran against (a) the shipped `MapScreen` / `LayeredRenderer` / `darkside` / `Ds*` as they
  are today, and (b) synthetic three-region screens built to the PDR's §D5 geometry. §D2's
  inspector, §D1's scoped keymap and §D3's `osopen` are **judgement** except where a probe drove
  existing code.
- **Colour rendering, contrast and terminal emulator variance** were not evaluated. All colour
  claims are about the *style values* in the painted strips, not about what a given terminal shows.
- **Non-Latin / wide (CJK) glyph handling** was not evaluated. `layered._vis_width` is
  `len(s)` with an explicit "no CJK handling" comment (`:22-24`); the environment declares
  width-1 glyphs only, so this is consistent — but it is untested, not proven.
- **Save latency and save-failure messaging** — declared out of scope in §7.
- **The `repo` and `home` screens** were not walked; this batch's trigger-D surface is `MapScreen`,
  `CoverageScreen`, the palette and the help overlay.
- **`prototypes/` was read only.** No file under it was created, modified or staged (CON-6).

---

## 11 · Verdict

**`approved with conditions`** — conditions **C1 – C9** in §8.

The skeleton is right: rail + canvas + editable inspector closes coverage → fill without leaving
the map, which is exactly the task in §1, and the operator's cross-pollination verdict is sound.
What the static SVG could not carry — and therefore what this PDR does not yet contain — is the
**focus model**, the **escape hatch**, and the **width budget**. Those three are not polish; they
are the difference between an instrument and a screen that looks like one. All three are measurable
and all three are now measured.

The axis that is unmet is **ISO 9241-210 activity 2**: the batch specifies what the system shall
*do* and does not yet specify what the operator shall *observe* about where their next key goes.
HLR-N06 (C1–C3) closes it.
