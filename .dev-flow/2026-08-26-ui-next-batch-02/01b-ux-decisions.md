# 01b — UX decisions · `2026-08-26-ui-next-batch-02`

> **Artifact language: English.** Every string presented as UI copy is **Spanish**, verbatim, and is
> normative — the implementer copies it, does not paraphrase it.
>
> **Lens:** interaction design (ISO 9241-210:2019, activities 1 and 2 — context of use, and user
> requirements stated as observable criteria). This document settles **Q-3** and **Q-6**, fixes the
> glyph vocabulary US-N16 must publish, specifies every empty and boundary state in scope, and
> records a cognitive walkthrough of the primary flow.
>
> **Evidence rule (C-43).** Nothing here is asserted from a document. Every load-bearing claim was
> executed — over `KEYMAP`, or under `App.run_test()` driving the real key and reading the painted
> result. Transcripts are pasted inline. Where a claim could not be executed, it is labelled
> **inspected, not exercised**.

---

## 0 · Context of use (ISO 9241-210 activity 1)

Stated before any criterion, because a UX criterion has nothing to be true *about* without it.

| Element | Value |
|---|---|
| **User** | One operator — Javier. Expert in the domain, expert in terminals, vi-idiomatic. Population size **1**; there is no second user whose retraining cost must be amortised. This is what makes a rebind cheap here and would not make it cheap elsewhere. |
| **Task** | Legacy-system archaeology. Open an inherited 128-node map, find the parts that are undocumented or at risk, walk them, and record what is known. The task is *repeated survey*, not one-shot lookup: the same map is reopened across days. |
| **Environment** | Windows 11, `PYTHONUTF8=1`, a **118-column × 34-row** terminal as the reference size (the size the batch's own story text names). Keyboard-only in practice. No pointing device is assumed by any criterion below. Textual 8.2.8 (executed: `textual version: 8.2.8`). |
| **Constraint that shapes everything** | The map is **larger than the screen**, permanently. Every decision below is judged first on: *does the operator ever lose something without being told?* |

**The limit, declared up front:** ISO 9241-210 asks for evaluation with **real users**. This team is
one person and no user session was run. What was performed is **inspection with declared criteria**
(a cognitive walkthrough over the task above) **plus an automated walkthrough through the real
mechanism** under Pilot. See §7.

---

## DECISION 1 — Q-3, the `n` chord collision · **BLOCKING**

### 1.1 · The seat as it actually is (executed, not recalled)

```
=== duplicate_chords() on the seat as shipped ===
[]

=== map scope: bound chords (25) ===
  A              -> add_attachment       agregar adjunto            [node]
  I              -> toggle_inspector     mostrar/ocultar ficha      [view]
  R              -> toggle_rail          mostrar/ocultar rail       [view]
  X              -> remove_attachment    quitar adjunto             [node]
  a              -> add_child            agregar hijo               [node]
  d              -> open_documents       documentos                 [node]
  e              -> export_svg           exportar svg               [view]
  enter          -> open_ficha           abrir ficha                [nav]
  equals_sign    -> toggle_diff          alternar diff              [view]
  escape         -> back_or_home         volver                     [salir]
  f              -> toggle_focus         alternar foco              [view]
  g              -> focus_rail           ir al rail                 [view]
  h              -> parent               padre                      [nav]
  j              -> next_sibling         siguiente                  [nav]
  k              -> prev_sibling         anterior                   [nav]
  l              -> child                hijo                       [nav]
  m              -> coverage             cobertura                  [view]
  n              -> next_gap             siguiente faltante         [view]
  o              -> toggle_outline       alternar outline           [view]
  q              -> home                 inicio                     [salir]
  r              -> toggle_radial        alternar radial            [view]
  slash          -> search               buscar                     [nav]
  u              -> undo                 deshacer                   [node]
  x              -> archive              archivar                   [node]
  z              -> collapse_branch      plegar rama                [view]

=== app scope: bound chords, reachable from map (2) ===
  ctrl+p         -> palette              paleta de acciones
  question_mark  -> help                 ayuda

=== single-letter chords FREE in map scope ===
  lowercase free (9): b c i p s t v w y
  lowercase taken (17): a d e f g h j k l m n o q r u x z
  UPPERCASE free (22): B C D E F G H J K L M N O P Q S T U V W Y Z
  UPPERCASE taken (4): A I R X
```

**The free set is wide.** The collision is not a scarcity problem — it is a semantics problem, and it
must be decided as one.

Two further executed facts that the options must survive:

```
pressed                | event.key        | character  | event.name
h                      | h                | 'h'        | h
H                      | H                | 'H'        | upper_h
n                      | n                | 'n'        | n
N                      | N                | 'N'        | upper_n
```

`N` and every shifted letter are genuine, distinct, bindable Textual keys. There is no toolkit
obstacle to any of the three options.

### 1.2 · The three candidates, judged on four axes

#### (c) One chord, state-dependent action, derived label — **REJECTED, and it is the interesting one**

It is the option that looks clever. It does not survive the last test, and the reason is exactly the
lesson batch 1 paid for three times.

**It breaks the static set-equality pin — structurally, not incidentally.** The whole-seat
conformance specification is `{(scope, key): (action, label, glyph, priority, group)}` compared by
**set equality**, hand-maintained and deliberately not derived (postmortem §2.4c). Under (c), the
row for `map/n` has no constant `label`: the displayed string is `siguiente coincidencia` sometimes
and `siguiente faltante` other times. Only two resolutions exist and both are losses:

1. Pin a placeholder label. Then the specification **no longer pins the displayed string** — which is
   verbatim narrowing #2 from §2.4c ("`key -> action` only — left the LABEL free"), the narrowing
   under which swapping the labels of `u` and `z` kept all 245 tests green and the operator read
   "u plegar rama" and performed an undo. The pin's own history says this is where the defect lives.
2. Make the spec a function of state. Then it is not set equality and not hand-maintained, and it
   becomes derived from the thing it checks — narrowing #1, the tautology.

**It breaks the one-declaration-four-readers architecture.** `groups_for_keybar` returns
`(binding.glyph, binding.label)` straight out of `KEYMAP` (`keymap.py:198-205`), and
`HelpScreen._render_keymap` reads `bindings_for(scope)` (`screens/help.py:66-69`). For the keybar to
tell the truth under (c), it must stop reading the seat and start asking the screen — so the seat
ceases to be the single source of the displayed name, which is the property the module's own
docstring exists to protect.

**And it fails the operator, not only the test.** "When a query is active" has **no painted
definition today.** Measured: after submitting a search the query text remains in the box and focus
goes nowhere.

```
4. press '/'  : focused=Input  input.value=''
   then 'n','o','m' -> input.value='nom'  cursor 'root' -> 'root'
   after enter : focused=None  input.value='nom'
```

So "active" is ambiguous at the moment of the keypress: the text is still there, the box is not
focused, and nothing on screen distinguishes the two. Under (c) the operator presses `n` and cannot
predict which of two actions fires. **A key whose effect the operator cannot predict from the screen
is the deception §2.4d names, moved from the label field into the action field.**

**Verdict: reject (c) plainly.** It is not a near miss; it is the failure mode the seat was built
against.

#### (b) Search gets different chords, `next_gap` keeps `n` — viable, second-best

Costs nothing in the seat and costs the story its idiom. `n`/`N` for *next/previous match* is the
most transferred keyboard convention in the terminal — vi, less, man, tmux copy-mode, every browser
find bar. US-N07's entire stated value is **trust**: "so that I can trust that what I see is all
there is". Making the operator learn a bespoke chord for the single most conventional verb in the
batch spends discoverability on precisely the story whose payload is confidence. The free lowercase
set (`b c i p s t v w y`) contains no candidate with a mnemonic in either Spanish or English.

#### (a) Rebind `next_gap`, give `n`/`N` to search — **RECOMMENDED**

### 1.3 · Recommendation

**Adopt (a), with `next_gap` moved to `M`.** Resulting seat delta — one changed row, two added rows:

| scope | key | glyph | action | label | group | priority |
|---|---|---|---|---|---|---|
| map | `n` | `n` | `next_hit` | `siguiente coincidencia` | `nav` | false |
| map | `N` | `N` | `prev_hit` | `coincidencia anterior` | `nav` | false |
| map | `M` | `M` | `next_gap` | `siguiente faltante` | `view` | false |

**Why `M` and not one of the nine free lowercase keys.** `m` is already `coverage` /
`"cobertura"`, and `next_gap` is *the walker of that very report* — `_incomplete_order()`'s own
docstring says it "walks the tree the same way `CoverageScreen` does, so 'next' in the worklist means
the same thing as 'next row' in the report" (`app.py:1601-1607`). Pairing them as `m` / `M` makes the
shift key mean "advance through what `m` shows", which is a rule the operator learns once. The seat
already contains two genuine shift-pairs of this kind — `a`/`A` (agregar hijo / agregar adjunto),
`x`/`X` (archivar / quitar adjunto). `M` is confirmed free by execution.

**Defence, against each axis the question named:**

- **Task flow.** The two verbs live in different sessions. Gap-walking is the *documentation* session
  — long, repetitive, no query in flight. Hit-walking is a *burst* immediately after `/`, then
  abandoned. Neither is interrupted by the other, so there is no cost to separating them and no
  benefit to fusing them. Fusing them was (c)'s only real argument and the sessions do not overlap.
- **Discoverability.** Three constant labels, each describing exactly one action. The search overlay
  teaches its own chords in place — the prototype already paints
  `2/7 coincidencias · n sig · N ant · esc` — so `n`/`N` are learned at the moment of use and never
  need to be looked up. `M` is the only thing relearned, and it gains a mnemonic (`m` = cobertura) it
  did not have before: `n` for "siguiente faltante" had no mnemonic in Spanish at all.
- **Can the keybar/legend tell the truth about what the key does right now?** Yes, trivially and
  always. Every label is a constant. There is no "right now".
- **Does the static set-equality pin survive?** Yes, unchanged in shape. The spec stays
  `{(scope, key): (action, label, glyph, priority, group)}`, hand-maintained, compared by set
  equality, and it gains two rows and changes one.

**⚠ Condition attached to the recommendation (this is where a rebind goes wrong).** The whole-seat
specification is hand-maintained *by design*. A rebind means the implementer edits the pin in the
same increment that changes the behaviour the pin exists to catch — which is exactly the situation
in which a pin stops being evidence. Therefore:

> The seat-spec diff for this batch **shall** be reviewed row-by-row at DDR and **shall** consist of
> exactly one changed row (`map/n`, whose `key` becomes `M` and whose `group` is unchanged) plus two
> added rows (`map/n`, `map/N`). If the diff is larger than three rows, something else drifted and
> the increment does not pass.

### 1.4 · The Q-3 finding that survives every option

Measured, and none of (a)/(b)/(c) escapes it:

```
   then 'n','o','m' -> input.value='nom'  cursor 'root' -> 'root'
   => while the search Input holds focus, 'n' TYPES; it does not navigate.
```

**While the search `Input` holds focus, every letter key types.** Hit-walking is therefore only
reachable *after* submit. Two requirements follow, and they are not optional decoration:

- **UX-Q3-a.** After submit, focus leaves the `Input` (measured: `focused=None`) and the query chip
  **shall** repaint in a committed style visibly distinct from its editing style, so the operator can
  see that letter keys now navigate rather than type. Painted difference is the criterion; the
  mechanism is the implementer's.
- **UX-Q3-b.** The hint line after submit **shall** read exactly
  `n siguiente · N anterior · esc limpiar`.

---

## DECISION 2 — Q-6, a lens term naming an undefined schema field

**Principle: an unresolvable query is never executed.** If `Z:algo` were evaluated, it would match
nothing, figure-ground would dim the whole canvas, and the screen would be pixel-identical to a
well-formed query with zero matches. That identity is the vacuous acceptance the question exists to
prevent, so the two states are separated *before* evaluation, not after.

### 2.1 · Exact observable difference

| | `Z:algo` — **undefined field** | `E:inexistente` — **defined field, 0 matches** |
|---|---|---|
| Is the query evaluated? | **No** | Yes |
| Canvas | **Unchanged.** Figure-ground is **not** applied; the map stays exactly as it was painted before the query. | Figure-ground **is** applied; every node falls to ground (bare dim text, no card chrome). |
| Query chip | ` Z ? sin definir ` painted in **ALERT** `#ff4f42` | ` E estado = inexistente ` painted in **MUT** `#737373` |
| Declaration line | `el mapa no define el campo «Z» · campos: D acta · O origen · E estado · C criticidad` | `0 nodos · ningún nodo tiene estado = inexistente` |
| Query text | **Retained**, cursor placed at the offending term so it can be corrected, not retyped | Retained |
| Escape offered | `esc limpiar` | `esc limpiar` |

### 2.2 · Normative copy

- One unknown key:
  `el mapa no define el campo «Z» · campos: D acta · O origen · E estado · C criticidad`
- Two or more unknown keys:
  `el mapa no define los campos «Z», «Q» · campos: D acta · O origen · E estado · C criticidad`
- Zero matches, query well-formed:
  `0 nodos · ningún nodo tiene estado = inexistente`
- Matches found (for contrast; the prototype's own string):
  `5 nodos en 2 ramas · ⇥ recorrer · esc limpiar`

**The field list after `· campos:` shall be derived from the map's schema, never hand-listed.** The
list above shows the shape using the prototype's field codes; the painted list is whatever
`graph.schema` actually defines for *this* map. A hand-listed vocabulary is a label that lies the
moment a map has a different schema — C-31's family.

### 2.3 · The acceptance criterion this yields

> When the operator submits `Z:algo` and then submits `E:inexistente` on the same map, the two
> painted declaration lines differ in text **and** the two chips differ in token, **and** the canvas
> is unchanged in the first case and fully dimmed in the second. Asserted on the painted result, not
> on the parser's return value.

---

## DECISION 3 — the glyph vocabulary (US-N16's legend content)

Complete and exact. Strings marked **(proto)** are reused verbatim from the generators; the citation
is the source of record. Tokens are the names in `mapper/darkside.py` (`GROUND #000000`,
`PANEL #121212`, `STEP #262626`, `INK #f5f5f5`, `MUT #737373`, `ACCENT #1783ff`, `WARN #ffd230`,
`ALERT #ff4f42`, `WORDMARK #3a3a3a`) plus the three that land in this batch.

### 3.1 · Canvas vocabulary — the atlas view

| # | Glyph, exactly | Spanish label, exactly | Painted in | Source |
|---|---|---|---|---|
| V1 | ` rrhh ` (node title, leading and trailing space, on a card) | `rama abierta` | `INK on PANEL` | **(proto)** `ui_next2/generate.py:610-611` |
| V2 | ` nómina ` (node title on a card) | `coincidencia de búsqueda` | `bold GROUND on WARN` | **(proto)** `:612-613` |
| V3 | `▸ <rama> +N` — e.g. `▸ inv +23` | `rama plegada (23 dentro)` | `MUT on PANEL` | **(proto)** `:614-615` |
| V4 | `∙ ∙ ∙` | `territorio sin explorar` | `WORDMARK` | **(proto)** `:616-617` |
| V5 | `▔▔▔▔` (under the selected node, its full width) | `nodo seleccionado` | `ACCENT` | **(proto)** `:618-619`, `ui_next/generate.py:430` |
| V6 | `┌─┐` | `minimapa: tu ventana en el todo` | `ACCENT` | **(proto)** `:620-621` |

**Braille edge dust — the one item the prototype legend does not itemise.** The generators paint two
distinct braille populations and the legend collapses them into V4, which under-declares. Specified
here as two rows, because they mean different things:

| # | Glyph, exactly | Spanish label, exactly | Painted in | Source |
|---|---|---|---|---|
| V4a | `∙ ∙ ∙` (scattered braille, `U+2800`–`U+28FF`) | `territorio sin explorar` | `WORDMARK` | `ui_next/generate.py:406-411` |
| V4b | braille run tracing a path between two cards | `enlace entre nodos` | `MUT`; the path to the selected node in `ACCENT` | `ui_next/generate.py:412-416`, edge styles `MUT` / `ACCENT` at `:394-401` |

### 3.2 · Declared-overflow and viewport indicators

| # | Glyph / line, exactly | Spanish label, exactly | Painted in | Source |
|---|---|---|---|---|
| V7 | `plegadas: inventarios · ventas — 41 nodos` | overflow declaration; the `N` **shall** reconcile with the sum of the `+N` in every painted pill | `WORDMARK` | **(proto)** `ui_next/generate.py:485` |
| V8 | `minimapa · 128 nodos` | minimap caption; `N` = total nodes in the graph | `WORDMARK` | **(proto)** `:449` |
| V9 | `┌──┐ │ │ └──┘` rectangle inside the minimap | viewport — the part of the territory now on screen | `ACCENT on PANEL` | **(proto)** `:442-448` |
| V10 | `▓` `▒` `░` density cells inside the minimap | territory density | `WORDMARK on PANEL` | **(proto)** `:437-441` |

### 3.3 · Lens vocabulary — figure-ground

| # | Glyph, exactly | Spanish label, exactly | Painted in | Source |
|---|---|---|---|---|
| V11 | `▐` (left bar of a matched card) | `coincide con la lente` | `WARN on PANEL` | **(proto)** `ui_next2/generate.py:341` |
| V12 | bare title, no card, no chrome | `fuera de la lente` | `WORDMARK` | **(proto)** `:348` |
| V13 | `╎` | `enlace atenuado` | `STEP` | **(proto)** `:333-336` |
| V14 | `ficha completa ✓` | `sin campos pendientes` | `SAGE on PANEL` | **(proto)** `:345-346` |
| V15 | `faltan campos ░` | `ficha incompleta` | `MUT on PANEL` | **(proto)** `:345-346` |
| V16 | `∗` | `lente de campos` | `ACCENT` | **(proto)** `:312` |

### 3.4 · Sala (home) vocabulary

| # | Glyph, exactly | Spanish label, exactly | Painted in | Source |
|---|---|---|---|---|
| V17 | `⇄ N` and legend chip `⇄ enlazado` | `enlaza mapas` | `VIOLET on PANEL` | **(proto)** `ui_next2/generate.py:134`, `:145` |
| V18 | `◍ github` and legend chip `◍ del repo` | `procedencia repo` | `TEAL on PANEL` | **(proto)** `:136`, `:146` |
| V19 | `█` filled cells / `░` empty cells, 10 wide | coverage microbar | filled `SAGE` when coverage ≥ 90 %, else `INK`; empty `WORDMARK` | **(proto)** `:126-128`; legend chip `█ cerrada` at `:147` |
| V20 | `▲ N vencen` and legend chip `▲ vence` | `actas vencidas` | `WARN on PANEL` | **(proto)** `:132`, `:148` |
| V21 | `∙` in the card thumbnail | lit `= nodo con acta`, unlit `= sin acta` | lit `MUT on PANEL`, unlit `WORDMARK on PANEL` | **(proto)** `:100-101` |

### 3.5 · Colours with a job — the palette-v2 rows

Verbatim from `ui_next2/generate.py:623-630`. Each row is a `█` swatch plus the label.

| Swatch | Spanish label, exactly | Token | Hex |
|---|---|---|---|
| `█` | `azul — donde puedes actuar` | `ACCENT` | `#1783ff` |
| `█` | `ámbar — atención / vence` | `WARN` | `#ffd230` |
| `█` | `sage — completo / vigente` | **`SAGE`** | `#2fbf71` |
| `█` | `teal — vino del repo` | **`TEAL`** | `#22b8cf` |
| `█` | `violeta — enlaza mapas` | **`VIOLET`** | `#9775fa` |

`ALERT #ff4f42` is **deliberately absent** from this list and is the only token DECISION 2 assigns to
the malformed-query chip. If ALERT acquires a second job it must acquire a row here too.

### 3.6 · Legend framing copy

Verbatim, `ui_next2/generate.py:599-634`:

- Panel title: `leyenda · atlas` — the second word is the **view name**, not a constant.
- Top-right: `? cierra`
- Section headers, in order: `teclas de esta vista` · `vocabulario de esta vista` · `colores con empleo`
- Footer, two lines: `cada vista tiene SU leyenda — ` / `misma tecla, contenido de la vista`
- Reserved chord line: `??` + `abre la guía de campo completa`

### 3.7 · ⚠ Two conflicts between the prototype legend and the shipped seat

Neither is a blocker; both must be resolved *in the seat*, not in the legend.

1. **`e editar` is not available.** The prototype legend paints `↵ ficha (peek) · e editar`
   (`:604`). In map scope `e` is `export_svg` / `"exportar svg"` (executed). The legend must not
   invent a chord. Either the peek editor gets a free chord, or the row drops.
2. **`- subir al relieve`** (`:604`) belongs to *relieve*, which the batch order places in **batch 4**
   and the PLAN declares out of scope. The row does not ship in this batch. `minus` is free and
   **should be reserved in writing**, the way `??` is, so batch 4 does not find it taken.

### 3.8 · ⚠ The legend does not fit — measured

This constrains DECISION 3's deliverable directly, so it is stated here as well as in the walkthrough.

```
=== ROW BUDGET for the US-N16 atlas legend ===
  map-scope bindings (set equality is REQUIRED): 27 rows
  group headers + blank line between groups    : 10 rows
  glyph-vocabulary rows (prototype n6_leyenda) :  6 rows + 1 header
  colour-with-a-job rows (prototype n6_leyenda):  5 rows + 1 header
  panel title + `?` cierra + ?? footer         :  4 rows
  ---------------------------------------------
  MINIMUM legend height                        : 54 rows
  walkthrough terminal height                  : 34 rows
  VERDICT: DOES NOT FIT — short by 20 rows
```

The vocabulary specified above is **substantially larger than the prototype's 6** — the exact row
count is DERIVED from the table above by `LLR-N16.2.1`, never written as a literal here (amendment
`A-45`; see the note below) — which makes the shortfall larger than the number above, not smaller.
**US-N16 cannot paint one flat panel.** It needs
a scrolling container or a two-pane/tabbed legend, and whichever is chosen, the set-equality
criterion must assert over the panel's **content**, not over what happens to be visible — otherwise
the assertion passes on a clipped panel, which is what ships today (§5, step 6).

> **⚠ Why no literal count appears here (amendment `A-45`, routed from the RIDER-1 reconciliation).**
> This line previously read *"**21 rows** (V1–V21)"*. It was the **fourth** live site of a stale
> literal, and the correction is not the obvious one: the table above carries **23** labels, but `V4`
> and `V4a` are byte-identical in glyph, label and style, so striking the duplicate takes it to
> **22**. *"Correct 21 to 23"* would therefore have been wrong **twice**. The count is now derived by
> `LLR-N16.2.1` over distinct `(glyph, label, style)` triples, and no literal is maintained by hand
> anywhere — a hand-maintained census is a defect, including in a requirements table (`P-18`).

---

## DECISION 4 — empty and boundary states

Six states. Each is specified as *what is painted*, because an unspecified empty state is where
vacuous acceptances come from.

**Precedent, executed:** the product already does this correctly in one place, and the new states
should match its register rather than invent one.

```
(a) 'n' with nothing missing -> toasts: [('cobertura completa', 'no falta ningún campo requerido')]
    => `n` ALREADY declares its empty state. Precedent exists in the product.
```

| # | State | What is painted, exactly |
|---|---|---|
| **E1** | **Search, 0 hits** | Count line reads `0 coincidencias` — the same line and the same position as a hit count, so the operator's eye lands where it always lands. The query chip repaints in `MUT` (never WARN — WARN means *a hit*, and an empty result must not borrow the hit colour). **No node on the canvas carries the V2 hit style.** Hint line: `sin coincidencias · esc limpiar`. |
| **E1b** | **`n` / `N` pressed with no search ever submitted** | Toast, matching the `next_gap` precedent: title `sin búsqueda activa`, body `pulsa / para buscar`. **Not** a silent no-op. |
| **E1c** | **`n` pressed with a submitted query that has 0 hits** | Toast: title `0 coincidencias`, body `«nóm» no aparece en este mapa`. Distinct from E1b — "you have not searched" and "you searched and there is nothing" are different facts. |
| **E2** | **Lens, 0 matches (query well-formed)** | Figure-ground **is** applied — every node to ground. Line reads `0 nodos · ningún nodo tiene estado = inexistente`. Hint: `esc limpiar`. Contrast with DECISION 2's undefined-field state is the acceptance criterion. |
| **E3** | **Map with 0 nodes** | The canvas paints the door, never a blank rectangle. Copy: `este mapa está vacío` / `a agrega el primer nodo`. The overflow indicator (V7) is **absent**, not `— 0 nodos`: nothing is hidden, so nothing is declared. The minimap (V6/V8/V9) is absent for the same reason. |
| **E4** | **Empty workspace (US-N13 welcome seat)** | Verbatim from `ui_next2/generate.py:139-143`: chord `n` + `construir un mapa`; body two lines `un mapa nuevo empieza con una` / `sola pregunta — el resto crece`; footer `t desde template · i importar csv`. The hue legend row (V17–V20) is **suppressed** when the workspace is empty — a legend for markers no card is showing is noise. |
| **E5** | **Pan at the edge of the territory** | The pan is a no-op **and says so**: the minimap viewport rectangle (V9) is flush against that side of the minimap frame, and the hint line reads `borde del territorio`. The canvas **shall not** scroll past the content and then present blank space — blank space is indistinguishable from "the map has nothing there", which is the exact confusion US-N06 exists to remove. |
| **E6** | **Fold pill for a branch with 0 hidden descendants** | **No pill is painted.** A leaf has nothing to hide, so `▸ hoja +0` is a promise of hidden content that does not exist. Folding a leaf is a no-op; if `z` is pressed on one, toast: title `nada que plegar`, body `este nodo no tiene descendientes`. Additionally: `+N` **shall** be the count of *hidden descendants*, so a pill whose `N` is 0 is by construction unpaintable, and V7's total reconciles by arithmetic rather than by convention. |

---

## DECISION 5 — cognitive walkthrough of the primary flow

**The flow.** *Operator opens a 128-node legacy map on a 118-column terminal, searches for a term
whose matches are inside a folded branch, navigates to one, opens the lens to narrow further, then
presses `?` to understand a glyph.*

Driven under `App.run_test(size=(118, 34))` against the **shipped** app with a real 128-node graph,
pressing real keys and reading the compositor's painted strips. Seven steps; **six break**.

### Step 0 — open the map · **BREAKS, totally**

```
screen: MapScreen | KEY_SCOPE = map
graph nodes: 128
   #map-rail       region=Region(x=0, y=4, width=118, height=147) display=True
   #map-canvas     region=Region(x=118, y=4, width=1, height=25) display=True
   #map-inspector  region=Region(x=119, y=4, width=36, height=25) display=True

(b) PAINTED rows at 118 x 34 (compositor output, post-layout):
    row 5   ||
    row 8   |      finanzas-hoja…|
    row 12  |      finanzas-hoja…|
    row 16  |      finanzas-hoja…|
    non-blank column range across rows 4-29: 0..117
    canvas is laid out at x=118; terminal last addressable column = 117
```

- **Must know:** nothing — this is the entry.
- **Screen tells them:** the rail, filling all 118 columns, and nothing else. **The map is not on
  screen.** The canvas is laid out at `x=118` on a terminal whose last addressable column is 117.
- **Break:** this is P-20 / S-7, and it is reproduced here at *exactly the size the story names*.
  The requirements say the rail auto-hides "below ~118 columns"; at 118 it does not, so **the
  reference environment is precisely a broken one**. Every step below is evaluated as if S-7 has
  already landed — it must land first or none of the rest is observable.
- **⚠ New, not in P-20:** the rail's region is `height=147` on a 34-row terminal. P-20's table
  measured widths only. The vertical overflow is a separate symptom of the same missing rule and
  should be measured when S-7 is fixed, not assumed fixed by it.

### Step 1 — press `/` and type `nóm` · **breaks (minor)**

```
4. press '/'  : focused=Input  input.value=''
   then 'n','o','m' -> input.value='nom'  cursor 'root' -> 'root'
```

- **Must know:** that `/` opens search. The keybar says so (`/ buscar`). Fine.
- **Screen tells them:** the query text.
- **Break:** no count while typing. The operator types blind until submit. The prototype paints the
  count on the line below the query (`2/7 coincidencias …`) and nothing prevents it updating live.
  **Not blocking, but specify it either way** — "count appears on submit" and "count is live" are
  different products and the implementer will otherwise choose by accident.

### Step 2 — submit · **BREAKS**

```
   after enter : focused=None  input.value='nom'
```

- **Must know:** that letter keys now navigate rather than type.
- **Screen tells them:** *nothing.* Focus is `None` — it is not on the input and not on the canvas,
  so **no widget paints a focus ring at all**. The query text is still sitting in the box, looking
  exactly as it did while it was accepting characters.
- **Break, and it is the one that makes DECISION 1 land or not.** Covered by UX-Q3-a and UX-Q3-b.

### Step 3 — the matches are inside a folded branch · **BREAKS — the largest gap in the design**

- **Must know:** that hits exist which are not painted.
- **Screen tells them:** the count (`2/7`) versus the number of highlighted cards visible. The
  operator is expected to do that subtraction **by eye**.
- **Break — three sub-questions the prototypes do not answer, and the implementer must not settle:**
  1. **Does a folded pill declare that it contains hits?** Specified here: **yes, it must.** A pill
     hiding a match while a count says 7 is the defect US-N07 exists to close, reintroduced by
     US-N06. Required painted form: `▸ inventarios +23 · 4` with the trailing hit count in `WARN`,
     and the pill's left bar in `WARN`.
  2. **Does pressing `n` onto a hit inside a folded branch auto-open the fold?** Specified: **yes**,
     and the fold-open is announced — hint line `abierta: inventarios`. Landing the cursor on an
     invisible node is a silent state change, which is the thing the story forbids.
  3. **Does the fold re-close when the operator walks past it?** Specified: **no.** Auto-closing
     would undo the operator's own now-visible context behind their back. Folds opened by `n` stay
     open until `z`.
- Without these three written down, the acceptance test "when the operator advances, the selection
  lands on the next matching node in tree order" **passes on a screen where the operator cannot see
  the selection.** That is a vacuous acceptance by construction.

### Step 4 — open the lens · **breaks (mechanism)**

```
asterisk               | asterisk         | '*'        | asterisk
```

- **Must know:** which key opens the lens.
- **Screen tells them:** the prototype paints `∗` (`U+2217`, ASTERISK OPERATOR). **That character is
  not a key.** The real key is `asterisk`, whose character is `*` (`U+002A`).
- **Not a blocker — the seat is already built for exactly this**: `key` binds, `glyph` displays. Bind
  `key="asterisk"`, `glyph="∗"`. Recorded because a naive implementer will try to bind `"∗"` and get
  a chord that never fires, and a chord that never fires and a chord that is absent fail identically.
- **⚠ Ergonomic notice, inspected not exercised:** `*` requires `shift+8` on the operator's layout.
  Nine lowercase chords are free (`b c i p s t v w y`) — `c` (consultar/campos) has a mnemonic in
  Spanish and one keystroke. Offered as an alternative; the decision is the operator's.

### Step 5 — walk the lens results with `⇥` · **BREAKS**

```
A. screen-level `tab` binding vs focus traversal
   focus before        : b1
   after tab #1 -> focus=b2   action_walk fired=0
   after tab #2 -> focus=b3   action_walk fired=0
   after tab #3 -> focus=b1   action_walk fired=0
   after tab #4 -> focus=b2   action_walk fired=0
   VERDICT: action_walk fired 0 times in 4 tab presses
```

- A plain screen-level `tab` binding fires **0 times in 4 presses**. Focus traversal eats it. This
  reproduces LLR-N06.5 independently.
- **It is rescuable, and this was measured too:**

```
-- can priority=True rescue `tab`? --
   priority=True: action_walk fired 3 times in 3 presses; focus b1 -> b1
```

- **So `⇥ recorrer` is buildable — but only with `priority=True`, and the cost must be stated:** the
  lens screen carries an `Input`. Stealing `tab` removes the only keyboard route between the query
  box and the canvas. **Required mitigation:** `escape` (already bound, `"volver"` in `salir`) must
  leave the query box, and the hint line must say so. Without that, `priority=True` on `tab` traps
  the operator in the input.

### Step 6 — press `?` to understand a glyph · **BREAKS — and it is a shipped defect**

```
(b) '?' -> HelpScreen scope='map'
    keymap.bindings_for('map') = 27 bindings
    labels from the seat NOT painted by the help panel: 10
      ['alternar foco', 'alternar outline', 'alternar radial', 'exportar svg',
       'alternar diff', 'siguiente faltante', 'mostrar/ocultar rail',
       'mostrar/ocultar ficha', 'ir al rail', 'plegar rama']
    glyph-vocabulary terms present today:
      {'rama plegada': False, 'territorio sin explorar': False,
       'nodo seleccionado': False, 'minimapa': False, 'coincidencia': False}
```

Measured at four terminal sizes:

```
terminal (118, 34) -> 34 painted rows; 17/27 map-scope seat labels present
    widget help-dialog        region=Region(x=19, y=3,  width=80, height=28)
    widget help-content       region=Region(x=21, y=6,  width=76, height=38)
terminal (118, 50) -> 50 painted rows; 17/27 map-scope seat labels present
    widget help-dialog        region=Region(x=19, y=11, width=80, height=28)
    widget help-content       region=Region(x=21, y=14, width=76, height=38)
terminal (140, 60) -> 60 painted rows; 17/27 map-scope seat labels present
terminal (200, 80) -> 80 painted rows; 17/27 map-scope seat labels present
```

- **Root cause, executed:** `mapper/screens/help.py:36-42` sets `#help-dialog { max-height: 28 }`,
  and `compose()` (`:59-64`) wraps the content in a plain `Vertical`, **not** a `VerticalScroll`.
  The content needs 38 rows. Ten rows are silently truncated.
- **The cap is absolute, so resizing does not help.** `17/27` at 118×34 and `17/27` at 200×80.
- **What the operator loses:** the entire `view` group — `alternar foco`, `alternar outline`,
  `alternar radial`, `exportar svg`, `alternar diff`, `siguiente faltante`, `mostrar/ocultar rail`,
  `mostrar/ocultar ficha`, `ir al rail`, `plegar rama`. Ten of the eleven keys that operate the
  *view* are below the cut, on the screen whose job is to explain the view. `z plegar rama` — the
  chord the whole fold story rests on — is one of them.
- **The walkthrough terminates here.** The operator pressed `?` to look up a glyph. There is no glyph
  vocabulary at all today (all five probes `False`), and a third of the keys are missing **without
  the panel saying anything is missing.** This is §2.4d's lesson in a different organ: a help panel
  that silently omits what it claims to enumerate is a label that lies.
- **Requirement:** US-N16's set-equality criterion **shall** be asserted against the painted result,
  and the panel **shall** be scrollable or paginated. Asserting against `_render_keymap()`'s return
  value would pass today, on a panel that shows 17 of 27.

**⚠ One more, from the same run — P-13 confirmed by execution, and it costs the legend its subject:**

```
5. '?' on MapScreen -> HelpScreen  scope='map'
6. '?' on RepoScreen -> HelpScreen  scope='app'
```

`RepoScreen` routes `?` with **no scope**, so it falls back to `SCOPE_APP` and the operator gets a
two-row panel (`ctrl+p`, `?`) instead of the repo's own keys. US-N16's title is `leyenda · <vista>`;
on three screens that title would name the wrong view.

### Walkthrough verdict

| Step | Verdict |
|---|---|
| 0 · open the map at 118 cols | **BREAKS** — the canvas is off-screen (S-7) |
| 1 · `/` and type | breaks (minor) — no count until submit; specify which |
| 2 · submit | **BREAKS** — nothing paints the mode change; focus is nowhere |
| 3 · hits inside a folded branch | **BREAKS** — three behaviours unspecified; the AT is vacuous without them |
| 4 · open the lens | breaks (mechanism) — `∗` is a glyph, `asterisk` is the key |
| 5 · `⇥` to walk | **BREAKS** — 0/4 without `priority=True`; 3/3 with it, at a stated cost |
| 6 · `?` for a glyph | **BREAKS** — 17/27 keys painted at every size; 0 glyph vocabulary |

---

## DECISION 6 — the C-16 interaction inventory

The visual specs are **SVG renders from Python generators; nothing in them runs Textual**. Every
promise those frames make, and whether Textual gives it. **Verified** rows carry a Pilot transcript
in §5 or below; **inspected** rows are marked as such and were not exercised.

| # | Promise the prototype makes | Frame | Free from Textual? | Evidence |
|---|---|---|---|---|
| 1 | `hjkl` moves between nodes | b1 | **free** — shipped | seat: `h/j/k/l -> parent/next_sibling/prev_sibling/child` |
| 2 | `⇧hjkl` pans the territory | b1, b2 | **must be built**; the keys are available | **verified** — `H J K L` arrive as `event.key` `'H' 'J' 'K' 'L'`; all four free in map scope; `H` pressed on the shipped MapScreen changes nothing |
| 3 | `z` folds / opens a branch | b1 | **partly free** — `z -> collapse_branch` is shipped; canvas-side fold is new | seat + D5 (fold ownership moves to `MapScreen`) |
| 4 | `/` opens search | b1 | **free** — shipped | **verified** — `press('/')` → `focused=Input` |
| 5 | `n` / `N` walk search hits | b1, n6 | **must be built**; `n` collides, `N` is free | **verified** — see DECISION 1 |
| 6 | letter keys navigate right after typing a query | b1 | **NO — actively false** | **verified** — `'n','o','m'` → `input.value='nom'`, cursor unmoved |
| 7 | `⇥` walks lens results | n4 | **must be built, and needs `priority=True`** | **verified** — 0 fires in 4 presses plain; 3 in 3 with `priority=True` |
| 8 | `∗` opens the lens | n4 | **must be built**; `∗` is not a key | **verified** — key is `asterisk`, character `'*'` |
| 9 | number keys `1`–`4` recall saved lenses | n4 | **must be built**; all four free | **verified** — `1 2 3 4` arrive as themselves; unbound in map scope |
| 10 | `v` saves a lens as a view | n4 | **must be built**; `v` free | **verified** — free in map scope |
| 11 | `?` opens the current view's legend | n6 | **partly free, and broken** — scope-aware for one screen of four; panel truncates | **verified** — §5 step 6; `RepoScreen` → `scope='app'` |
| 12 | `??` opens the guía | n6 | **must be built — Textual has no chord support** | **verified** — `Binding("question_mark,question_mark", …)` fires on the **first** press: comma means *alternatives*, not *sequence*. A `??` chord needs a hand-built timer/state machine. |
| 13 | `e` edits in the peek card | n6 | **must be built, and the chord is taken** | seat: map `e -> export_svg` |
| 14 | `-` goes up to relieve | n6 | out of scope (batch 4); `minus` free — **reserve it** | **verified** — `minus` arrives as itself, unbound |
| 15 | arrow keys move focus spatially on the canvas | all | **NO — Textual does no spatial arrow focus** | **verified** — 2×2 grid, `right`/`down`/`left` from `nw` all leave focus on `nw` |
| 16 | clicking a node on the canvas selects it | b1, b2 | **must be built** — the canvas is a bare `Static` (P-16) with no per-node hit regions; one widget, one click target | **inspected, not exercised** |
| 17 | hovering a fold pill previews it | b2 | **must be built**; same reason as 16 | **inspected, not exercised** |
| 18 | the minimap viewport tracks the pan | b1 | **must be built** — render-only, no mechanism exists | **inspected, not exercised** |
| 19 | braille edges reach the screen | b1, b2 | **NO — actively broken today** | P-1, executed: `Canvas.rows()` drops `dots`/`bgs`; 0 glyphs in `U+2800`–`U+28FF` |
| 20 | the three-region layout is visible at all | all | **NO — actively broken** | **verified** — §5 step 0, at 118 columns |

**Score: of 20 promises, 3 are free, 3 are partly free, 10 must be built, and 4 are actively false
today.** P-10 / C-16 is confirmed a second time: reading these frames as an interaction spec would
have shipped four broken promises.

---

## 6 · Verdict

**`pass-with-notices`, conditional on DECISION 1 being ratified at PDR.**

- **DECISION 1** is a recommendation with a defence; it is **blocking** and PDR ratifies it.
- **DECISION 2, 3, 4** are specifications and are complete as written.
- **DECISION 5** found **six breaks in seven steps**. Two of them (step 0, step 6) are **shipped
  defects on `master`**, not design gaps: the off-screen canvas at 118 columns, and the help panel
  that paints 17 of 27 bindings at every terminal size. Step 3's three unspecified behaviours are the
  one place where an acceptance test would otherwise pass vacuously, and are specified above.
- **DECISION 6** confirms C-16 by measurement.

**The axis that would make this a `fail`:** if US-N16 ships its set-equality criterion asserted
against `_render_keymap()`'s return value rather than the painted panel, the criterion passes today
on a panel showing 17 of 27 keys. That single choice would convert the batch's most valuable control
into a vacuous one.

---

## 7 · Explicitly not covered

Stated in writing rather than left to inference.

1. **Evaluation with real users was not performed.** ISO 9241-210 activity 4 asks for it; the team is
   one person and no user session was run. What was performed is inspection with declared criteria
   plus an automated walkthrough through the real mechanism. **A Pilot run is not a user.** Every
   judgement in DECISION 5 about what the operator *must know* is the reviewer's inference from the
   context of use in §0, not an observation of the operator.
2. **Colour rendering was not verified.** The round-10 claim that SAGE / TEAL / VIOLET survive rich's
   256-colour quantisation at slots 35 / 38 / 105 remains a **hypothesis**, as `01-requirements.md`
   §2.7 already declares. This review executed no colour probe. The exact hexes in DECISION 3 are the
   declared tokens, not measured terminal output.
3. **Contrast and accessibility were not assessed.** No contrast-ratio measurement was taken for any
   token pair. `WORDMARK #3a3a3a` on `GROUND #000000` is used for V4/V7/V8 — the "territory" and
   "declared overflow" rows — and it is the lowest-contrast pair in the vocabulary. Flagged as worth
   measuring; **not measured here.**
4. **Mouse and hover interactions (rows 16, 17, 18) were inspected, not exercised.** The reasoning
   from P-16 is sound but no click was driven under Pilot.
5. **Screen-reader and non-visual access are out of scope entirely** and no criterion above addresses
   them.
6. **Q-1, Q-2, Q-4 and Q-5 are not this document's to answer.** Q-1/Q-2/Q-4 are settled in `PLAN.md`
   §9 (D4, D5, D6). Q-5 (`◍` provenance) is a scope decision for PDR; DECISION 3 specifies what `◍`
   looks like **if** it ships, and that specification is inert if Q-5 rules it out.
7. **No product code was written or modified.** `mapper/**`, `tests/**` and `prototypes/**` are
   untouched. All probes ran from a scratchpad directory outside the repository.
