# 02f — PDR pass 2 · UX / interaction lens · `2026-08-26-ui-next-batch-02`

> **Artifact language: English.** UI strings quoted below are **Spanish** — the project convention.
> That is correct and is never a finding here.
>
> **Lens:** ISO 9241-210:2019, activity 4 (evaluate the design against the requirements). This pass
> **extends `01b-ux-decisions.md`; it does not restart it.** `01b`'s context of use (§0) is adopted
> unchanged and is the context every finding below is judged against.
>
> **Evidence rule (C-43).** Every load-bearing claim was **executed against `d877784`** and its
> transcript is pasted inline. Nothing is asserted from a document. Where a claim could not be
> executed it is labelled **inspected, not exercised**.
>
> **Base verified:** `git log --oneline -1` → `d877784 chore: record the vault sync for
> 2026-08-26-repair-batch`. Tree clean apart from the untracked batch directory. **No file under
> `mapper/`, `tests/` or `prototypes/` was read-modified, staged or touched.** All probes ran from a
> scratchpad outside the repository.

---

## 1 · VERDICT

# `approved with conditions`

**Ten conditions, each named and individually dischargeable. Two are blocker-class — they block
their own increment, not the batch.** No condition requires re-opening a settled ruling.

**The headline, BLUF.** This batch's *observation* discipline is the best I have reviewed in this
project. The painted-panel oracle with the proxy explicitly banned, `LLR-N14.1.1`'s canvas
byte-identity arm, and `LLR-N13.1.5`'s distinguishability arm are three genuinely strong controls,
and `01b` did the hard work honestly. **The failures are not in what the batch observes. They are in
what it *drives*, and they cluster in one place: the `⇥ → n`/`N` unification moved the walk onto a
letter key *after* the requirements around it had been written for a Tab key**, and nothing
re-derived the consequences. Two of those consequences are severe:

- **`HLR-N14.3`'s two threshold clauses cannot both be satisfied, and the implementation that comes
  closest destroys ficha data.** Executed: with the inspector focused — the state the requirement
  *demands* — the real `n` key does not walk. It types, replaces the field, and commits on blur.
  `'ACTA-2011-034'` → `'n'`. (§5, `UX2-C-01`.)
- **US-N14 has no declared entry chord anywhere in the requirements.** The story's own front door is
  unspecified, so no acceptance can drive it. That is C-16 in its exact form. (§5, `UX2-C-02`.)

**On the question formally routed to me (§6.2 item 2), my ruling is that the routing was correct but
the premise was not: the claim IS measurable, and I measured it. It holds, with a wide margin.**
`assumed` should be retired, not preserved. (§2.)

**The axis that would make this a `fail`:** none currently. It becomes `BLOCKED` if `Inc-5` opens
against `HLR-N14.3` as written, because the increment would then be building a specified behaviour
whose specified end-state overwrites the operator's own records.

### 1.1 · Condition ledger

| id | Severity | Gates | One line |
|---|---|---|---|
| `UX2-C-01` | **blocker** | Inc-5 | `HLR-N14.3`'s "inspector focused" clause is unsatisfiable; the near-miss commits data loss |
| `UX2-C-02` | **blocker** | Inc-5 | US-N14 has no declared entry chord, so no AT can drive its real gesture |
| `UX2-C-03` | major | Inc-3 | US-N06's pan chord is still unnamed — `AT-011`/`AT-012` are chord-agnostic acceptances |
| `UX2-C-04` | major | Inc-3 | `LLR-N06.2.4`'s oracle executes FALSE at every width; `AT-046`/`AT-047` false-fail correct work |
| `UX2-C-05` | major | Inc-8 | The legend never teaches its own scroll keys, and US-N16 triples the content behind them |
| `UX2-C-06` | major | Inc-4 · Inc-5 | The mode created by `C-D6a` is invisible: nothing paints which result set is live |
| `UX2-C-07` | major | Inc-4 · Inc-8 | The `M` relocation is taught only on a row that is below the fold at 118 × 34 |
| `UX2-C-08` | major | Inc-1 | `WORDMARK` paints the declared-overflow line at **1.85 : 1** — the promise is illegible |
| `UX2-C-09` | minor | Inc-7 | The damaged card has copy but no visual treatment, and is accepted at the wrong terminal size |
| `UX2-C-10` | minor (notice) | Inc-1 | One rung below the pinned downgrade, two semantic token pairs collide outright |

---

## 2 · §6.2 item 2 — ruling on the 256-colour perceptual claim

### 2.1 · The ruling

> **`assumed` was the honest disposition for a claim nobody had measured. It is no longer the
> correct one, because the claim is measurable by machine, I measured it, and it HOLDS with a
> margin of roughly six times the discrimination threshold. Retire `assumed`; convert
> `HLR-S06.2` to a MEASURED claim with a numeric floor.**

**§6.2's framing — *"not observable at all by any test this batch can write"* — executes FALSE.** It
conflates two different questions:

1. *Can a human tell slot 35 from slot 38?* — a psychophysical question, not automatable, and
   correctly out of scope.
2. *Are the colours these tokens actually paint separated by more than the established threshold of
   human discrimination?* — a **colorimetric** question, fully deterministic, no display required,
   answerable in ~60 lines of stdlib plus `rich`.

Colorimetry is the discipline that exists precisely to stand in for question 1 with question 2. The
batch declined to answer a question it could have answered, and labelled the gap `assumed`. That is
the *safe* error rather than the vacuous one — the requirement was **not** converted into a proxy
assertion dressed as evidence, which is the failure mode that matters — so this is a correction, not
a fault. But it should be corrected.

### 2.2 · Why the measured metric was the wrong one

**M-2 measured slot *numbers*. Slot numbers are not a perceptual metric, and the requirement's own
stated worry proves it.** §2.8.1 records the concern as: *"`TEAL` at 38 sits five slots from the
shipped `ACCENT` at 33 in the same face of the colour cube."*

Executed — slot adjacency and perceptual adjacency are unrelated in the xterm-256 cube:

```
  dE00  20.18  ACCENT (slot  33) vs TEAL   (slot  38)      <- the "five slots apart" pair
  dE00  13.99  ACCENT (slot  33) vs VIOLET (slot 105)      <- 72 slots apart, and CLOSER
```

The pair the requirement worried about is the *second* most separated of the two. Distance in slot
index carries no information about distance in appearance, so no threshold could ever have been set
on it.

### 2.3 · The measurement

`rich 15.0.0`. Each token is quantised through the real path, the **RGB the slot actually paints** is
read from `EIGHT_BIT_PALETTE`, converted to CIE L\*a\*b\* (D65), and compared with **CIEDE2000**.

```
=== M-2 reproduced, plus the RGB the slot actually paints ===
token     source hex slot  slot rgb   zone                   job
ACCENT    #1783ff      33  #0087ff   16-231 fixed 6x6x6     interactividad (donde puedes actuar)
WARN      #ffd230     221  #ffd75f   16-231 fixed 6x6x6     severidad: atencion / vence / HIT
ALERT     #ff4f42     203  #ff5f5f   16-231 fixed 6x6x6     severidad: error / consulta malformada
SAGE      #2fbf71      35  #00af5f   16-231 fixed 6x6x6     completitud / vigente
TEAL      #22b8cf      38  #00afd7   16-231 fixed 6x6x6     procedencia repo
VIOLET    #9775fa     105  #8787ff   16-231 fixed 6x6x6     relaciones / enlaces
  ... (nine shipped tokens + #a3a3a3 also measured)
  collisions: 0

=== the pairs that carry DIFFERENT SEMANTIC JOBS, ascending ===
  dE00  13.99  ACCENT  vs VIOLET      <- the MINIMUM across all 15 semantic pairs
  dE00  20.18  ACCENT  vs TEAL
  dE00  25.95  TEAL    vs VIOLET
  dE00  36.75  WARN    vs SAGE
  dE00  38.26  SAGE    vs TEAL
  ... 10 further pairs, all >= 39.50
```

**Reference points.** ΔE00 ≈ **2.3** is the classic just-noticeable difference. ΔE00 < 5 is the range
where two colours are plausibly confused at small glyph size or low ambient light. **The minimum
across every semantically-loaded pair is 13.99 — about 6× the JND and ~2.8× the confusability
band.** The three new tokens do not merely occupy distinct slots; they occupy plainly distinct
appearances, and so do all nine shipped ones.

**A second thing worth knowing, and it strengthens the claim:** all six semantic tokens quantise into
slots **16–231**, the fixed 6×6×6 cube. Unlike slots 0–15, cube slots are **not remappable by the
terminal's colour theme**, so the measured separation is not at the mercy of the operator's scheme.

**And the downgrade itself is gentle** — no token is dragged far from its designed appearance:

```
  ACCENT  #1783ff -> slot  33 #0087ff   dE00 shift =  1.74
  WARN    #ffd230 -> slot 221 #ffd75f   dE00 shift =  3.89
  SAGE    #2fbf71 -> slot  35 #00af5f   dE00 shift =  4.82
  ALERT   #ff4f42 -> slot 203 #ff5f5f   dE00 shift =  5.60
  TEAL    #22b8cf -> slot  38 #00afd7   dE00 shift =  5.88
  VIOLET  #9775fa -> slot 105 #8787ff   dE00 shift =  6.61
```

### 2.4 · The rung is live, not hypothetical — and the rung below it collides

**The 256-colour path is the one this machine actually takes.** Textual builds its `Console` with
`color_system=constants.COLOR_SYSTEM` (`'auto'`) and `legacy_windows=False`. Reproducing that exact
construction:

```
Textual App console.color_system on THIS machine = 256
```

`rich.Console._detect_color_system` on Windows returns `TRUECOLOR` if
`get_windows_console_features().truecolor` else `EIGHT_BIT`; here that probe reports
`WindowsConsoleFeatures(vt=False, truecolor=False)`. **So `HLR-S06.2` guards a path the operator
reaches, and the requirement is load-bearing rather than precautionary.** Good.

**But the batch pins one rung and does not declare the one below it.** Driven through the real
render path with uncached `Style` objects (my first attempt was contaminated by rich's `Style.parse`
LRU cache — recorded because it produced a plausible wrong answer):

```
--- EIGHT_BIT ---   (the pinned rung)
   ACCENT -> 38;5;33    SAGE -> 38;5;35    TEAL -> 38;5;38    VIOLET -> 38;5;105
   (no collisions)

--- STANDARD (16 colour) ---
   ACCENT -> 94   VIOLET -> 94     *** COLLISION
   SAGE   -> 36   TEAL   -> 36     *** COLLISION
   MUT    -> 90   WORDMARK -> 90   *** COLLISION

--- WINDOWS ---
   ACCENT -> 94   VIOLET -> 94     *** COLLISION
```

Two of those are **semantic** collisions, and one is materially worse than the other: `ACCENT ≡
VIOLET` means **blue — declared *interactivity-only*, «donde puedes actuar» — becomes
indistinguishable from the link marker `⇄`.** A marker that means *"this map is linked to another"*
would read as *"you can act here."* That is the exact class of deception the palette's one-job rule
exists to prevent.

**Honest severity: minor, a notice, not a blocker.** Because Textual sets `legacy_windows=False`,
auto-detection on Windows yields only `TRUECOLOR` or `EIGHT_BIT` — the 16-colour rung is **not**
auto-reachable. It is reachable by one environment variable (`TEXTUAL_COLOR_SYSTEM`, read at
`textual/constants.py`, which the product does not pin). So this is a declared limit, not a live
defect. → `UX2-C-10`.

### 2.5 · The finding the measurement produced that nobody was looking for

Contrast ratios on `GROUND #000000`, computed for both rungs:

```
  WORDMARK  truecolor  1.85:1   8-bit(slot 237)  1.85:1  <-- below 4.5:1
  STEP      truecolor  1.39:1   8-bit(slot 235)  1.39:1  <-- below 4.5:1
  PANEL     truecolor  1.12:1   8-bit(slot 233)  1.12:1  <-- below 4.5:1
  MUT       truecolor  4.43:1   8-bit(slot 242)  4.00:1  <-- below 4.5:1
  ACCENT    truecolor  5.73:1   8-bit(slot  33)  5.91:1
  SAGE      truecolor  8.81:1   8-bit(slot  35)  7.30:1
  TEAL      truecolor  8.83:1   8-bit(slot  38)  8.11:1
  VIOLET    truecolor  6.24:1   8-bit(slot 105)  6.94:1
```

`01b` §7 item 3 flagged `WORDMARK` on `GROUND` as *"worth measuring; not measured here."* **It is now
measured: 1.85 : 1.** The three new tokens are all comfortable. `WORDMARK` is not, and the reason it
matters is not general accessibility — it is **whose job `WORDMARK` holds**:

`01b` DECISION 3 assigns `WORDMARK` to **V7, the declared-overflow line** —
`plegadas: inventarios · ventas — 41 nodos` — and to V8, the minimap caption. **V7 is the one
sentence that carries US-N06's entire promise.** The story's stated point is *nothing clips
silently*, and the batch's answer to silent clipping is a line painted at 1.85 : 1 on black: about
40 % of the way to the minimum ratio that standard considers legible for large text.

> **A declaration nobody can read is not a declaration. `AT-015`/`AT-016` assert that the string is
> *present in the painted text*, which is true of a string at 1.85 : 1 exactly as it is of one at
> 8 : 1 — the oracle cannot see the difference, and the operator can.**

→ `UX2-C-08`. The fix is a token swap, not new mechanism: `MUT` at 4.00 : 1 is the next rung and is
already the declaration register elsewhere. It is one line in `Inc-1`, which already owns
`darkside.py`.

### 2.6 · What §6.2 should say instead

Replace item 2 with two entries — one discharged, one genuinely open:

- **DISCHARGED.** The three v2 tokens are separated from every other token, and from each other,
  by a minimum CIEDE2000 of **13.99** at the pinned 8-bit rung, with zero slot collisions and all
  six semantic tokens landing in the theme-independent 16–231 cube. `HLR-S06.2` becomes a measured
  claim with a **numeric floor** — I recommend `min ΔE00 over semantic pairs >= 10`, derived over
  the declared token set so that a tenth token joins the check without anyone remembering (C-31).
  This is an ordinary Layer-0 unit test; it needs no display, no Pilot and no fixture.
- **STILL NOT OBSERVABLE, and correctly so.** Whether the operator's specific panel, ambient light
  and eyesight preserve that margin. This is small, real, and the honest residue. It is what
  `assumed` should have been reserved for.

---

## 3 · C-16 interaction-fidelity audit

D2 fired because the visual specs are **SVG renders from Python generators — nothing in them runs
Textual**. `01b` DECISION 6 scored the 20 promises. This pass audits the other direction: **does each
requirement's acceptance drive the real mechanism?**

### 3.1 · Scoreboard

One structural fact governs the whole table: **no `AT-NNN` in `01-requirements.md` carries an
individual specification.** Ids appear only on `Acceptance:` lines and in the §5.2 table; the actual
predicate is the owning requirement's *Executed verification* + *Numeric pass threshold* pair, plus
§5.1's blanket rule (`:3952`): *"Every `AT` drives the real key or the real gesture (control C-16)."*
Every classification below is by AT → owning-requirement mapping. **Where the blanket rule and the
owning requirement disagree, the owning requirement is what gets implemented.**

| Story | Drives the real mechanism | Reads the painted result | Verdict |
|---|---|---|---|
| **US-N06** | 5 of 9 real key; **2 real-key-but-chord-UNNAMED** (`AT-011`, `AT-012`); 2 inject fold as a parameter (`AT-015`, `AT-016`) | 9 of 9 painted — including the batch's strongest oracle | **conditional** — `UX2-C-03`, `UX2-C-04` |
| **US-N07** | 4 of 7 real key, and **explicitly** so: *"`AT-022` and `AT-023` shall press the real `n` and `N`"* (`:2118`); 3 unit-only | 4 painted, 3 pre-layout | **strongest chord discipline in the batch** |
| **US-N13** | real mount via `App.run_test` throughout; no keystroke is in scope for this story | 5 painted, 2 pre-layout | **conditional** — `UX2-C-09` |
| **US-N14** | `AT-038`/`AT-039` press the real walk chord; **entry chord undeclared**; `AT-036`/`AT-037` say *"submit a query"* and name no gesture | `LLR-N14.1.1`'s canvas byte-identity arm is excellent; `HLR-N14.3` reads **no painted surface at all** | **BLOCKED at Inc-5** — `UX2-C-01`, `UX2-C-02` |
| **US-N16** | `HLR-N16.1` and `HLR-N16.3` drive the real `question_mark`; **`HLR-N16.2` and `LLR-N16.2.2` say *"open the legend"* and name no key** | **painted, with the proxy explicitly banned** — the best predicate in the batch | **conditional** — `UX2-C-05` |

### 3.2 · The one place the batch got this exactly right, and it should be said

`LLR-N16.1`'s acceptance (`:3216`), verbatim:

> Set equality **shall** be asserted against `_painted_bindings`'s union, never against
> `_render_keymap()`'s return value and never against a widget's own `render_lines`.

`01b` §6 named this as the single choice that would convert the batch's most valuable control into a
vacuous one. **It was taken correctly, it is backed by an on-disk artifact
(`tests/test_repair_layout.py`), and it ships with its own negative control
(`test_at_r14_the_oracle_is_clipped_to_the_help_dialog`) and two named weaker variants.** That is the
control working as designed. `01b`'s stated `fail` axis is closed.

### 3.3 · The one gap that runs through all five stories

**Every requirement that specifies a *new painted surface* drives it with a real key. Every
requirement that specifies *what that surface says* does not.** `HLR-N16.2` (the title and the glyph
vocabulary — the entire new half of US-N16) says *"open the legend from each view."* `HLR-N14.2` says
*"submit a query."* Both are the halves this batch actually adds; both are the halves whose gesture
is unstated; both will therefore be implemented as proxies by default, because a proxy is what an
unstated drive decays into. Not separately conditioned — it is the shared root of `UX2-C-02` and
`UX2-C-05`.

---

## 4 · The `⇥` deviation (`PLAN.md` §13.2) — judged on usability

### 4.1 · Ruling

> **I RATIFY the chord change and OBJECT to the unification's user-facing half.**
>
> Dropping `⇥` for `n`/`N` is correct and I would have recommended it independently. **The premise
> the ruling rests on — *"only one result set can be active at a time"* — is not a fact about the
> operator's task. It is a constraint the batch is about to impose. Imposing it is defensible.
> Imposing it silently is not, and as specified it is silent.**

### 4.2 · Why the chord change is right

Three reasons, in order of weight:

1. **`n`/`N` is the correct chord on the merits, independent of the guards.** It is the most
   transferred keyboard convention in the terminal — vi, less, man, tmux copy-mode, every browser
   find bar. `⇥` for "next result" is transferred from *nothing*; it is a focus key everywhere else
   in computing. The guards forced a change that improves the design.
2. **The label survives honestly.** `#D6`'s defence is that *"siguiente coincidencia"* is true of
   both sets, so the whole-seat static set-equality pin is untouched. That is correct and it is the
   material difference from option (c), which `01b` DECISION 1 rejected. This is **not** that failure
   re-entering: under (c) the *action* varied behind a constant label; here one action walks one
   concept whose membership varies. The operator's model — *"`n` goes to the next thing I asked
   for"* — stays true.
3. **The alternative was worse.** Moving `TAB_BINDING_EXCEPTIONS` to admit `MapScreen` would take
   `tab`, the inspector's only keyboard route, and `01b` measured `priority=True` as the only rescue
   — which traps the operator in the query box unless `escape` is wired and announced. More
   mechanism, more risk, for a chord with no idiomatic claim.

### 4.3 · Why the premise is a mode, and the operator will meet it

**The brief's own task statement is what defeats it.** `01b` §0 fixes the task as *"legacy-system
archaeology… find the parts that are undocumented or at risk, walk them"* — **repeated survey, not
one-shot lookup.** The single most natural move in that task is **refinement**: *"find every mention
of `carlos` — now, of those, which are `obsoleto`?"* Search finds the term; the lens filters by
field. They are not alternatives. They are stages of one question, and the operator holds both in
mind because the whole point of the second is the first.

`C-D6a` makes them exclusive at Layer 0: *"submitting a lens shall clear search hits, and submitting
a search shall clear lens matches."* **Executed check of what the operator sees when that happens:
nothing.** Nothing in any painted-string specification declares which result set is live, and nothing
announces the clearing. The two count lines differ in *form* — `3/7 coincidencias` versus
`5 nodos en 2 ramas` — but that difference is incidental, not declared, and neither line says the
other set was just discarded.

**The concrete failure, naming user · task · consequence:**

> **User:** the operator, mid-survey on a 128-node inherited map.
> **Task:** narrow «every node mentioning `carlos`» down to «…and marked `obsoleto`».
> **Sequence:** `/carlos` → `3/7 coincidencias` → open the lens → `E:obsoleto` → `5 nodos en 2 ramas`.
> **Observable consequence:** the seven search hits are gone. The operator believes they are looking
> at the intersection; they are looking at the lens result over the **whole map**. `n` still reads
> `siguiente coincidencia`, so nothing contradicts them. **They draw a conclusion about which
> `carlos` records are obsolete from a set that was never filtered by `carlos`.**

That is a wrong answer produced confidently by a correct implementation — the same shape as the
damaged-map card, in a different organ.

**A second, cheaper instance of the same root.** `HLR-N07.3`'s `E1b` toast (`:2091`) reads title
`sin búsqueda activa`, body `pulsa / para buscar`. That copy was written under Q-3, **before** Q-7
unified the walk. Under `#D6`, `n` is no longer a search chord — it walks *coincidencias*, search or
lens. An operator working in the lens who presses `n` with nothing live is told to press `/`, which
opens the **wrong surface**. No amendment revisits it.

### 4.4 · What discharges the objection

Not a re-ruling. The chord stands. Three small painted commitments, all inside increments that
already own the surface:

1. **The count line declares its subject.** It already differs in form; make the difference
   *declared* rather than incidental — the line names which question it is answering (search vs
   lens, and the term). One string per surface.
2. **The clearing is announced.** When submitting a lens discards live search hits — or the reverse
   — the hint line says so. This is the same register `01b` DECISION 4 already established for
   `next_gap`'s empty state, and the product already has the precedent executed:
   `toasts: [('cobertura completa', 'no falta ningún campo requerido')]`.
3. **`E1b`'s copy is re-derived from the unified concept**, so it does not send a lens user to `/`.

→ `UX2-C-06`. With those three, `#D6` is not merely the buildable option — it is the better one, and
I would defend it against `⇥` on a project with no guards at all.

---

## 5 · Per-story interaction findings

Each names **user · task · observable consequence.** Severity is assigned on that consequence, not on
how hard it is to fix.

---

### `UX2-C-01` · **BLOCKER** · US-N14 · the walk chord types into the inspector and commits over the operator's records

**Gates Inc-5.**

`HLR-N14.3` (`:3003`) requires the walk chord to move the selection **with the ficha inspector
holding focus**, threshold: *"`app.focused` is inside the inspector region after each press."* Under
`#D6` the walk chord is `n` — a printable letter.

**Executed** against `d877784`, fresh app per target, real `pilot.press("n")`, shipped seat:

```
focusable widgets on MapScreen:
   map-rail               OutlineRail      Input=False
   insp-title             FieldInput       Input=True
   insp-state             DsSegmented      Input=False
   insp-field-D           FieldInput       Input=True
   insp-field-O           FieldInput       Input=True
   insp-field-E           FieldInput       Input=True
   insp-field-C           FieldInput       Input=True
   insp-field-N           FieldInput       Input=True
   insp-notes             FieldInput       Input=True

=== press the REAL walk chord 'n' with each inspector widget focused ===
   insp-title    Input=True  value 'Sistema ERP Legacy'      -> 'n'   ficha delta after blur: {}
   insp-state    Input=False value None                      -> None  ficha delta after blur: {}
   insp-field-D  Input=True  value 'ACTA-2011-034'           -> 'n'   ficha delta: {'D': ('ACTA-2011-034', 'n')}
   insp-field-O  Input=True  value 'Juan Perez'              -> 'n'   ficha delta: {'O': ('Juan Perez', 'n')}
   insp-field-E  Input=True  value 'obsoleto'                -> 'n'   ficha delta: {'E': ('obsoleto', 'n')}
   insp-field-C  Input=True  value 'alta'                    -> 'n'   ficha delta: {'C': ('alta', 'n')}
   insp-field-N  Input=True  value 'migracion planeada 2027' -> 'n'   ficha delta: {'N': ('migracion planeada 2027', 'n')}
   insp-notes    Input=True  value 'Sin mantenimiento…'      -> 'n'   ficha delta after blur: {}
```

**Eight focusable widgets; six are `FieldInput`; five commit the overwrite into the graph.** Textual
selects-on-focus, so the keystroke does not append — it **replaces the whole value**, and
`Inspector._commit` fires on blur (`mapper/widgets/inspector.py`), writing it through.

- **User:** the operator, walking lens results with the inspector open — the state `HLR-N14.3`
  specifies as the *normal outcome of every press*.
- **Task:** step through matches reading each node's ficha.
- **Observable consequence:** the selection does not move. The field under the cursor is replaced by
  the single character `n` and committed. `'ACTA-2011-034'` — an acta reference in a legacy-archaeology
  workflow, i.e. exactly the artifact the entire product exists to preserve — becomes `'n'`.

**Only `insp-state` (`DsSegmented`, the one non-`Input` focusable) lets `n` through.** So the *only*
implementation satisfying both threshold clauses parks focus on `insp-state` after every press — an
arbitrary state toggle the operator did not ask for, on the one widget that exists only while a node
is selected. Both readings are defects; the requirement admits no third.

**Honest scoping.** The hazard exists on `master` today: the shipped seat already binds `n` in map
scope. **What this batch adds is a requirement that puts the operator in that state routinely and by
design.** `01b` DECISION 1 §1.4 measured this exact mechanism for the search `Input` — *"while the
search `Input` holds focus, every letter key types"* — and derived `UX-Q3-a`/`UX-Q3-b` from it. That
lesson was not carried to the inspector, because when it was written the walk chord was `⇥`.

**Discharge.** `HLR-N14.3`'s threshold is rewritten before Inc-5 opens. The story's promise — *the
inspector follows the selection* — does **not** require the inspector to hold **focus**; it requires
it to **update**. Those were the same thing under `⇥` and are opposites under `n`. Recommended
threshold: *the map canvas retains focus across the walk; after each press the inspector's painted
content corresponds to the newly selected node* — read painted, which `HLR-N14.3` currently does not
do at all.

---

### `UX2-C-02` · **BLOCKER** · US-N14 · the story has no declared front door

**Gates Inc-5.**

The chord that **opens the lens** is never settled anywhere in `01-requirements.md`. `01b` DECISION 5
step 4 left it explicitly open — *"`*` requires `shift+8`… `c` has a mnemonic in Spanish and one
keystroke. Offered as an alternative; **the decision is the operator's**"* — and the `#D5b` seat-delta
table adds only `n`, `N`, `M`; `LLR-N14.3.3` adds the digits. **No row opens the lens.**

- **User:** the operator wanting to ask the map a field question.
- **Task:** open the lens.
- **Observable consequence:** undefined. And downstream: `AT-036`/`AT-037` say *"submit a query"*
  with no gesture behind it, so they will be implemented as *set the value, call the handler* — the
  proxy class this batch exists to refuse. **A chord that never fires and a chord that is absent fail
  identically**, which is `01b`'s own warning about `∗` versus `asterisk`, one level up.

Note the interaction with `D10`'s three-row seat-diff cap: the cap reserves no row for a lens-open
chord, so the increment that adds one **breaches its own review rule** unless the cap is amended in
the same breath.

**Discharge.** PDR names the chord and adds the row, amending `D10`'s cap from three rows to four.
`01b`'s ergonomic notice stands: `*` costs `shift+8`; nine lowercase chords are free
(`b c i p s t v w y`), and `c` («consultar/campos») has a Spanish mnemonic and one keystroke. **This
is the operator's call, and it is a one-line decision — but it must be made before Inc-5, not during
it.**

---

### `UX2-C-03` · major · US-N06 · the pan chord is the one ruling nobody made

**Gates Inc-3.**

`QA-B-10` established that *"a chord-agnostic requirement is legitimate; a chord-agnostic acceptance
test is not."* The fix was applied to US-N07 (`n`/`N`/`M`) and US-N14 (`#D6`). **It was missed for
US-N06.** `HLR-N06.1` still reads (`:1367`): *"This requirement stays written chord-agnostic; PDR
ratifies the specific chords with 01b's transcript in hand."* No `shift+`, no `H`/`J`/`K`/`L`, no
named pan key appears anywhere in §3.4, and §6.1 carries no pan question.

The chords are available — `01b` DECISION 6 row 2 verified `H J K L` arrive as themselves and all
four are free — so this is an unmade decision, not a blocked one.

- **User:** the operator on a 128-node map larger than the screen.
- **Task:** move the window over the territory.
- **Observable consequence:** `AT-011` and `AT-012` are precisely the chord-agnostic acceptances
  `QA-B-10` declared illegitimate. They will be implemented by whatever the implementer picks, and
  `AT-012`'s `borde del territorio` declaration — the `E5` state, adopted specifically because
  *"this requirement's first draft specified a **silent** no-op at the edge, which the ux lens rules
  insufficient"* (`:1348`) — is asserted against a key nobody has named.

**Discharge.** PDR ratifies `⇧hjkl` (the prototype's promise, and the pan idiom that pairs with the
shipped `hjkl` navigation), adds the four rows, and §3.4's thresholds name the keys.

---

### `UX2-C-04` · major · US-N06 · the anti-vacuity requirement's own oracle executes FALSE

**Gates Inc-3.**

`LLR-N06.2.4` is the requirement `01b` DECISION 5 step 3 demanded, added so `AT-022` is **not**
vacuous — so the walk does not land the cursor on a node the operator cannot see. Its statement is
right. Its threshold (`:1621`) is:

> the selected node's id appears in the painted canvas text after the walk press

**The same document proves that predicate false** (§6.5 A-21, `:1746`): *"a raw-**id** trace is false
always, because the canvas paints titles and never ids."* Re-executed independently at three widths:

```
ids: ['alm','cont','erp','fin','inv','nom','pres','rrhh']
50x12:  raw-ID trace present for 0/8 -> []
80x24:  raw-ID trace present for 0/8 -> []
120x40: raw-ID trace present for 0/8 -> []
```

- **User:** the implementer, then the operator.
- **Task:** land the walk on a node inside a folded branch and be able to see it.
- **Observable consequence:** **`AT-046` false-fails a correct implementation at every width.** This
  batch has already paid to learn that *"a rule which false-fails correct work costs as much as one
  that passes wrong work"* — and the cost lands specifically on the control that exists to stop
  `AT-022` passing on a screen where the operator cannot see the selection. `AT-047`'s second clause
  is a separate problem: it reads `MapScreen.folded`, a **model attribute**, so it can pass while the
  branch is painted closed.

**Two further structural defects on the same pair, both executed:**

```
story-line ids : 45   req Acceptance : 44   behavioral table : 48
THREE-WAY INTERSECTION = 40
in table+req but NOT on any story Acceptance-tests line: ['AT-034b','AT-039','AT-046','AT-047']
```

§5.2 (`:3985`) states its own rule: *"An id present in fewer than all three is a defect, not a
test."* **`AT-046` and `AT-047` fail it** — US-N06's live story line (`:1313`) reads exactly
`AT-011 … AT-017`.

**Discharge.** Adopt the document's own already-solved oracle: `QA-B-01`'s replacement — the renderer
returns its painted id set as data, and a **truncation-tolerant** trace is asserted separately.
`AT-047`'s clause moves from `folded` to the painted pill. Both ids are added to US-N06's story line.

---

### `UX2-C-05` · major · US-N16 · the legend does not teach the keys that operate the legend

**Gates Inc-8.**

The repair batch shipped the scroll container (`mapper/screens/help.py:73`, `#help-bindings {
overflow-y: auto }`), and `01b` §3.8's fit problem is correctly struck as `SATISFIED-EXTERNALLY`.
**That closed clipping. It did not close discoverability of reachability — and this is the batch that
makes the distinction matter.**

**Executed at 118 × 34 — the reference size `01b` §0 fixes — driving the real `question_mark`:**

```
after real '?': HelpScreen scope= map
  dialog   Region(x=19, y=3, width=80, height=28)
  pane     Region(x=21, y=6, width=76, height=24)  max_scroll_y= 14
  title painted: 'atajos · map'
  bindings_for('map') = 27
  visible at rest: 16/27
  MISSING at rest: ['alternar diff', 'alternar foco', 'alternar outline', 'alternar radial',
                    'cobertura', 'exportar svg', 'ir al rail', 'mostrar/ocultar ficha',
                    'mostrar/ocultar rail', 'plegar rama', 'siguiente faltante']

=== THE LEGEND'S OWN SCOPE: what keys does it say work here? ===
    escape -> esc cerrar
    q      -> q   cerrar

=== do the scroll keys work, and are any of them declared? ===
   real 'down'     x9 -> scroll_y 0 -> 9    declared in help scope? False
   real 'pagedown' x9 -> scroll_y 0 -> 14   declared in help scope? False
   real 'end'      x9 -> scroll_y 0 -> 14   declared in help scope? False
   focused widget: VerticalScroll(id='help-bindings')
   union over real-key scroll positions: 27/27
```

And the dialog exactly as the operator meets it:

```
    1|  atajos · map|
    4|  app|
    5|    ctrl+p  paleta de acciones|
    6|    ?       ayuda|
    8|  nav|
    9|    j       siguiente|
   ...
   18|    d       documentos                                                       ▆|
   ...
   24|  salir|
   25|    q       inicio|
   26|    esc     volver|
```

- **User:** the operator who pressed `?` to look up `z plegar rama` — the chord the whole fold story
  rests on.
- **Task:** find out what a key does.
- **Observable consequence:** four groups, none containing it, and a one-cell `▆`. The screen whose
  stated job is *"lists exactly the keys that work there"* (`:3113`) declares **two** keys and omits
  the three that operate it. Reachability is real — `27/27` by real keys — but it is undeclared, so
  the operator's route to it is guessing.

**Two aggravations, both created by this batch:**

1. **US-N16 triples the content behind that undeclared key.** `LLR-N16.2.1` mandates the full
   21-row `V1`–`V21` vocabulary plus 5 colour rows plus 3 section headers — roughly +30 rows, taking
   `max_scroll_y` from 14 to ~44. **The `vocabulario de esta vista` and `colores con empleo`
   sections — the entire new deliverable — land about two full pages below the fold.**
2. **The oracle scrolls with a proxy, so the affordance is unguarded.**
   `tests/test_repair_layout.py:104-123` calls `pane.scroll_to(...)` — a method call, not a
   keystroke. Its docstring claims *"the only way to observe reachability through the shipped
   surface is to reach it"*; the code reaches it **as the program, not as the operator**. Today
   `can_focus=True` and the pane auto-focuses, so the real route works — but nothing asserts it.
   Set `can_focus=False`, or land a filter box in the legend that takes focus, and
   `_painted_bindings` stays green while the `view` group becomes unreachable. Neither named mutant
   (`M-N16.1-a`, `M-N16.1-b`) catches that: they weaken the **oracle**, not the **affordance**.

**Discharge, three parts, all inside Inc-8's own surface:** (a) `SCOPE_HELP` gains rows for the
scroll keys that already work, so the legend obeys its own rule; (b) one `AT` drives a **real**
scroll key and asserts the union, so the affordance is guarded and not only the content; (c) with a
~44-row scroll range, PDR should decide whether a flat scroll is still the right information design
or whether the three sections want to be reachable directly — this is `01b` §3.8's question
returning at three times the size, and the strike answered the clipping half of it only.

**Also noted, no separate condition:** the painted title is `atajos · map` — it names the **scope**,
not the **view**, and §3.8 records this honestly at `:3376`. US-N16 requires `leyenda · <vista>`. It
is in scope and specified; I flag only that `HLR-N16.2`'s drive never names the real key (§3.3).

---

### `UX2-C-06` · major · US-N07 + US-N14 · the mode is real and nothing paints it

**Gates Inc-4 and Inc-5.** Full argument at §4.3. Restated for the ledger:

- **User:** the operator refining a search with a lens.
- **Task:** «of the nodes mentioning `carlos`, which are `obsoleto`?»
- **Observable consequence:** the search set is discarded silently; `n` still reads `siguiente
  coincidencia`; the operator reads a lens-over-the-whole-map result as an intersection and
  concludes wrongly about which records are obsolete.

`C-D6a` is **correct as a mechanism** and correctly placed at Layer 0 — *"not inferred from the walk
behaving correctly"* is exactly right. The gap is that it has **no painted consequence**, and it is
this lens's job to say that a sound state machine the operator cannot see is not a finished design.
Discharge = the three painted commitments in §4.4.

---

### `UX2-C-07` · major · US-N07 + US-N16 · the relocated chord is taught only below the fold

**Gates Inc-4 and Inc-8.** This one is a compound of two findings that are individually minor and
together are not.

`#D5b` relocates `next_gap` from `n` to `M`. Two executed facts:

1. **No AT presses the real `M`.** The explicit clause (`:2118`) names only `n` and `N`. The
   relocation is guarded solely by the whole-seat set-equality pin and `duplicate_chords()` — both of
   which are *declaration* checks, not *behaviour* checks. §3.5 records the consequence itself
   (`:2136`): between Inc-4 and Inc-8 the relocated chord is undiscoverable through `?`, *"found by a
   user, not by a suite."*
2. **`siguiente faltante` is one of the 11 labels below the fold at 118 × 34** — see the `MISSING at
   rest` list in `UX2-C-05`, measured, not inferred.

- **User:** the operator who has used `n` for `siguiente faltante` since the feature shipped.
- **Task:** resume the documentation session — the long, repetitive gap-walk that `01b` §1.3
  identifies as one of the two sessions this seat serves.
- **Observable consequence:** `n` now does something else. They press `?` to find where it went. At
  their terminal size the answer is 11 rows below the fold, behind a scroll key the panel does not
  declare (`UX2-C-05`). **The batch takes a chord away and puts its replacement in the one place the
  operator cannot reach without already knowing how.**

I want to be clear that `M` is the **right** target — `01b` §1.3's mnemonic argument (`m` =
cobertura, `M` = walk what `m` shows) is genuinely good, and better than what `n` had. The finding is
not the chord. It is that a rebind's entire cost lands on discoverability, and discoverability is the
thing this batch measured as broken.

**Discharge:** one `AT` presses the real `M` and reads the painted result; and Inc-4 ships a one-time
declaration on first `n` press after the rebind (the toast register `01b` DECISION 4 already
establishes and the product already executes). The second half is cheap and closes the window
`:2136` names.

---

### `UX2-C-08` · major · US-N06 · the overflow declaration is painted at 1.85 : 1

**Gates Inc-1.** Full measurement at §2.5.

- **User:** the operator on a map larger than the screen.
- **Task:** know that something is hidden — the entire promise of US-N06, *nothing clips silently*.
- **Observable consequence:** `plegadas: inventarios · ventas — 41 nodos` is painted in `WORDMARK`
  `#3a3a3a` on `GROUND` `#000000` at **1.85 : 1** — about 40 % of the minimum ratio considered
  legible for large text. `AT-015`/`AT-016` assert the string is *present in the painted text*, which
  is equally true at 1.85 : 1 and at 8 : 1. **The oracle cannot see the difference; the operator
  can.**

**Discharge:** V7 (and V8, the minimap caption) move off `WORDMARK`. `MUT` at 4.00 : 1 is the next
rung and is already the declaration register elsewhere in the vocabulary. One line in `darkside.py`
usage; Inc-1 already owns the file. `WORDMARK` keeps its legitimate job — V4, the *unexplored
territory* dust, where being barely-there is the point.

---

### `UX2-C-09` · minor · US-N13 · the damaged card is distinguishable only to a reader who is reading

**Gates Inc-7.**

I reproduced the shipped misdeclaration `PLAN.md` §14.1 records, with a healthy-empty control beside
it. Workspace: one damaged map (a cycle), one healthy **empty** concept map, one healthy map.

```
DataTable home-recents rows = 3
 row: ['roto',       ' concept ', '0', '0']
 row: ['sano',       ' concept ', '2', '0']
 row: ['sano_vacio', ' concept ', '0', '0']

=== PAINTED home, 118x34 ===
  18| ▐ name      kind       nodos  docs |
  19| roto         concept   0      0|
  20| sano         concept   2      0|
  21| sano_vacio   concept   0      0|
```

**`roto` and `sano_vacio` are byte-identical as painted.** Confirmed; and the notice is a transient
toast while the card is permanent, so after the toast clears there is no trace at all.

`LLR-N13.1.5` fixes this correctly — the threshold is *"painted card count AND per-card state
distinguishability"*, the inequality arm is explicitly load-bearing, and mutant `M-H1b` is named for
it. **That is right.** Two residual gaps, both about whether the fix works *at a glance*:

1. **The copy has no visual treatment.** `mapa dañado — ↵ ver por qué` is declared as a *string*;
   no token, colour or glyph is assigned in `LLR-N13.1.5`, `HLR-N13.3`, or `01b`'s V17–V21. Every
   other state in the batch carries one. **The sala's entire purpose is choosing where to work
   *without opening anything*** — a scan, not a read. A card that differs only in text differs only
   to someone already reading it. The inequality threshold is satisfied by a text-only difference.
   Recommended: `ALERT` — `LLR-S06.3.5` declares its single job as *failure or blockage; this item
   cannot proceed as it stands*, and a map that will not load is exactly that. **Note this gives
   `ALERT` a second job and therefore requires a row in `colores con empleo`**, per `01b` §3.5's own
   rule.
2. **It is accepted at a terminal size the operator does not use.** `LLR-N13.1.5` and `HLR-N13.3`
   both declare `App.run_test(size=(140, 45))`. The context of use is **118 × 34**. The copy is 26
   characters before any card chrome; whether it survives at 118 columns — or truncates into
   something indistinguishable from a healthy card — is not measured by any declared arm. **The
   load-bearing half of the requirement is asserted only at the size where it is easiest to
   satisfy.** Re-declare the pilot size as 118 × 34, or run both.

**On the copy itself, judged as Spanish in context: it is good.** «mapa dañado» is plain, correct,
and carries no jargon; «— ↵ ver por qué» offers the next action with the glyph the seat already uses
for `abrir ficha`, so it transfers. My only note is that `↵` on this card means *"explain the
failure"* while `↵` everywhere else on the home means *"open the map"* — a second job for one glyph
on the same screen. It is defensible (both are "go in and look"), and I do not condition on it, but
`LLR-N13.1.5` should say which one fires so the implementer does not choose by accident.

---

### `UX2-C-10` · minor (notice) · palette · one rung down, two semantic pairs collide

**Gates Inc-1.** Full measurement at §2.4. Declared, not blocking: the 16-colour rung is not
auto-reachable under Textual's `legacy_windows=False`, but is one environment variable away and the
product pins nothing.

**Discharge:** `HLR-S06.2` states the rung it guarantees (`eight_bit` and above) and declares the
16-colour behaviour as a known limit, rather than leaving a later reader to discover that
`ACCENT ≡ VIOLET` there. If the operator wants the guarantee unconditional, pinning
`TEXTUAL_COLOR_SYSTEM` is one line — but that is a scope decision, not mine.

---

## 6 · Evidence checklist

Every row re-runnable against `d877784`. Probe scripts are in this session's scratchpad, outside the
repository; each is self-contained and imports nothing from `tests/`.

| ✓/✗ | Claim | How to re-run |
|---|---|---|
| ✓ | Base is `d877784`; tree clean apart from the untracked batch dir | `git log --oneline -1` · `git status --porcelain` |
| ✓ | `rich 15.0.0`; M-2 reproduced — SAGE/TEAL/VIOLET → slots 35 / 38 / 105, **0 collisions** | `Color.parse(h).downgrade(ColorSystem.EIGHT_BIT).number` over the 13 tokens |
| ✓ | Minimum CIEDE2000 over semantic pairs = **13.99** (`ACCENT` vs `VIOLET`), ≈ 6× the JND | `EIGHT_BIT_PALETTE[n]` → CIE L\*a\*b\* (D65) → CIEDE2000, all pairs |
| ✓ | `ACCENT` slot 33 vs `TEAL` slot 38 = **20.18 ΔE00** — "five slots apart" is not a perceptual metric | same probe |
| ✓ | All six semantic tokens land in slots 16–231, the theme-independent cube | zone column of the same probe |
| ✓ | Textual's own `Console` construction reports `color_system = 256` on this machine | rebuild `Console(color_system=constants.COLOR_SYSTEM, legacy_windows=False, force_terminal=True, …)` |
| ✓ | `WindowsConsoleFeatures(vt=False, truecolor=False)` here, so `_detect_color_system` → `EIGHT_BIT` | `rich._windows.get_windows_console_features()` |
| ✓ | 16-colour rung: `ACCENT ≡ VIOLET` (SGR 94), `SAGE ≡ TEAL` (SGR 36), `MUT ≡ WORDMARK` (SGR 90) | `Style(color=Color.parse(h)).render('x', color_system=ColorSystem.STANDARD)` — **use a fresh `Style` per call; `Style.parse` is LRU-cached and caches `_ansi`, which silently returns the first rung's codes for every later rung** |
| ✓ | `WORDMARK` on `GROUND` = **1.85 : 1**; `MUT` = 4.43 : 1 truecolor, **4.00 : 1** at 8-bit | WCAG relative luminance over the same token set |
| ✓ | At 118 × 34, real `?` on `MapScreen` paints **16 of 27** seat labels at rest; 11 missing incl. `plegar rama` and `siguiente faltante` | `App.run_test(size=(118,34))` → `press("question_mark")` → `_rows_in(screen, dialog.region)` (the shipped oracle from `tests/test_repair_layout.py`) |
| ✓ | Real `down`/`pagedown`/`end` DO scroll the pane; **none is declared** — `bindings_for('help')` returns exactly `escape` and `q` | same probe + `keymap.bindings_for("help")` |
| ✓ | Union over real-key scroll positions = **27/27** — reachability is genuine but unguarded | same probe |
| ✓ | Painted legend title is `atajos · map` — the **scope**, not the view | `_rows_in(screen, title.region)` |
| ✓ | Real `n` with any `FieldInput` focused **replaces the value and commits on blur**; `'ACTA-2011-034'` → `'n'` on 5 of 8 focusables | `App.run_test` → `MapScreen("legacy")` → focus each of `screen.focus_chain` → `press("n")` → blur → diff `graph.nodes[cursor].ficha.fields` |
| ✓ | Only `insp-state` (`DsSegmented`) passes `n` through to the screen | same probe, `Input=False` column |
| ✓ | Home paints `roto` and `sano_vacio` **byte-identically**: `['…', ' concept ', '0', '0']` | `App.run_test` on a 3-map temp workspace (cycle · empty · healthy), read `DataTable#home-recents` + composited frame |
| ✓ | The repair batch's scroll container did ship | `mapper/screens/help.py:73` `VerticalScroll(...)`, CSS `#help-bindings { overflow-y: auto }` at `:49-51` |
| ✓ | `#a3a3a3` is live in `_GREYS` and is a legitimate ramp step | `mapper/views/radial.py:16-18`, used at `:165`, `:179`, `:189` |
| ✓ | `TAB_BINDING_EXCEPTIONS = ("SettingsScreen", "EditorScreen")`; `MapScreen` absent — `#D6`'s premise holds | `mapper/keymap.py:49`; guards at `tests/test_keymap.py:189`, `:207`, `:217` |
| ✓ | `FactoryScreen` and `SettingsScreen` declare no `KEY_SCOPE`; 6 declarations exist | `grep -rn 'KEY_SCOPE' mapper/` |
| ✓ | `LLR-N06.2.4`'s raw-id oracle is FALSE at 50×12, 80×24 and 120×40 (0/8 ids traced) | render `legacy` at each size, scan painted text for each node id |
| ✓ | AT three-way intersection = 40; `AT-046`, `AT-047` absent from US-N06's story line | mechanical id extraction over `01-requirements.md` |
| ✓ | `▸` already carries three jobs in shipped code | `grep -rn "▸" mapper/` → `darkside.py:177`, `screens/factory.py:244`, `views/lane.py:150`, `widgets/rail.py:228` |
| ✗ | **Not executed:** whether `mapa dañado — ↵ ver por qué` survives at 118 columns | requires the card layout, which does not exist until Inc-7. This is `UX2-C-09` limb 2, and it is *why* the pilot size must change |
| ✗ | **Not executed:** pan, fold, lens, legend vocabulary as behaviours | none exists at `d877784`. Every finding above is about the **specification** of their acceptance, which is what a PDR pass can observe |

---

## 7 · Explicitly not covered

Stated in writing rather than left to inference. `01b` §7 is adopted in full; this extends it.

1. **Evaluation with real users was not performed.** ISO 9241-210 activity 4 asks for it. The team
   is one person and no user session was run. What was performed is **inspection with declared
   criteria** — a cognitive walkthrough over the task in `01b` §0 — **plus an automated walkthrough
   through the real mechanism** under Pilot. **A Pilot run is not a user.** Every judgement above
   about what the operator *would* do — most load-bearingly §4.3's claim that they hold a search and
   a lens in mind together — is this reviewer's inference from the stated context of use, **not an
   observation of the operator.** It is the kind of claim a single user session would settle in ten
   minutes, and it is the one I would most want settled.
2. **Colour was measured colorimetrically, never on a terminal.** §2 is CIEDE2000 over the RGB rich
   emits. No frame was displayed and no photometer was used. Display gamut, ambient light and the
   operator's own colour vision are unmeasured, and a ΔE00 of 13.99 is a wide margin under *typical*
   viewing, not a guarantee under all.
3. **Contrast was measured; readability was not.** §2.5's ratios are WCAG relative-luminance
   arithmetic. WCAG's thresholds were set for web text, not for terminal glyphs at cell size, and I
   apply them as the best available proxy while noting they are a proxy.
4. **Mouse, hover and click remain inspected, not exercised** — `01b` DECISION 6 rows 16, 17, 18. No
   click was driven under Pilot in this pass either. The context of use declares keyboard-only, so
   this is a declared scope limit, not an omission.
5. **Screen-reader and non-visual access are out of scope entirely.** No criterion here addresses
   them, and several — the whole glyph vocabulary, figure-ground dimming, the constellation
   thumbnail — are visual-only by construction.
6. **No behaviour of the five stories was exercised, because none exists at `d877784`.** Everything
   in §3 and §5 is a judgement about how the acceptance is *specified to be driven*. Whether the
   implementation honours it is DDR's and validation's question, not this gate's.
7. **`Q-5` (the `◍` provenance marker) is out of scope and nothing above depends on it.** `01b`
   DECISION 3 V18 specifies its appearance conditionally and remains inert.
8. **I did not run the pytest suite.** The orchestrator owns gate runs. Every transcript above comes
   from a standalone probe in a scratchpad directory.
9. **No file in the repository was modified.** `mapper/`, `tests/` and `prototypes/` are untouched
   and unstaged; this artifact is the only file written.

---

## 8 · Closing note to the gate

Two things I want on the record, because a review that only lists faults misreports the batch.

**First: the controls worked.** `01b` §6 named one specific choice — asserting US-N16's set equality
against `_render_keymap()`'s return value — as the thing that would convert the batch's most valuable
control into a vacuous one. The requirements took the other branch, wrote the ban into the
requirement text, and backed it with an on-disk oracle and a negative control. **The most likely
failure was predicted and then prevented.** Similarly, `PLAN.md` §14.1 records the orchestrator
catching its own claim executing false, and `C-D9a` records an architect declaring their own probe
vacuous rather than banking a green. That is the discipline this project has paid for, applied.

**Second: the findings have one shape, and it is worth naming rather than listing.** Almost
everything above is a **consequence that was not re-derived after a decision changed.** `#D6` moved
the walk from a Tab key to a letter key — and `HLR-N14.3`'s focus clause, `E1b`'s toast copy, and the
absence of a mode indicator are all the same un-re-derived consequence in three places. `#D5b` moved
`next_gap` to `M` — and its discoverability landing below the fold is that one. `QA-B-10`'s
chord-agnostic fix was applied to three stories and not the fourth.

**The generalisable control, offered for the post-mortem:** when a ruling changes a *mechanism*, the
fold must re-derive every requirement that was written against the old one — not merely amend the
requirement the ruling names. Every blocker in this review lives in a requirement that `#D6` never
mentioned.
