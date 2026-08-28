# 02h — PDR iteration 3 · UX / interaction lens · `2026-08-26-ui-next-batch-02`

> **Artifact language: English.** Quoted UI strings are **Spanish** — the project convention, correct,
> and never a finding here.
>
> **Lens:** ISO 9241-210:2019 activity 4 — evaluate the design against the requirements. `01b` §0's
> context of use is adopted unchanged: **118 × 34**, keyboard-only, legacy-system archaeology.
>
> **Base.** `git rev-parse --short HEAD` → **`94ad8d3`**, branch `docs/amendment-set-3`. My pass-2
> ledger was written against `d877784`, so **every load-bearing claim below was re-executed**; two of
> my own pass-2 numbers turned out to be wrong and are corrected here.
>
> **Evidence rule.** Command + output, or `file:line` on the current tree. **No claim rests on a
> citation of another document.** Where something could not be executed it is labelled
> *inspected, not exercised*.
>
> **Isolation.** Every probe ran against a `git archive HEAD` export in the scratchpad, with fixtures
> copied into a `tempfile.mkdtemp()` workspace **before any `MapperApp` was constructed**. No
> `MapperApp` was pointed at the repository. Incident check at §8.

---

## 1 · VERDICT

# `approved with conditions`

**Nine of my ten conditions are discharged or properly disposed. One is `PARTIAL` and carries a new
one-line blocker on `Inc-1`. `UX2-C-01` stays live and is correctly deferred — but the remedy
recorded beside the deferral does not remedy it, and I exercised that.**

**No axis is unmet at batch level. The batch should implement.**

**BLUF, three sentences.** The requirements lane did real work: `A-65`–`A-72` close eight conditions
with predicates I can execute, and `A-66`'s replacement oracle — the one I was warned might inherit
the fault — executes **8/8 true** where the parked one executes **0/8 false**. The three addendum
rulings are sound in substance; `#D25` and `#D26` I ratify outright, `#D27` I ratify with a
legibility condition its argument never measured. The one thing nobody caught is that **`A-68`
prescribes a fix that fails `A-68`'s own new predicate by arithmetic** — `PRED-4` sets a floor of
`4.5 : 1` and its DISCHARGE names a token that measures `4.00 : 1`, a number printed four lines above
the predicate in the same requirement.

### 1.1 · Condition ledger

| id | Pass-2 severity | Status at `94ad8d3` | Landed at |
|---|---|---|---|
| `UX2-C-01` | blocker | **LIVE** — deferral ACCEPTED, recorded rationale **REFUSED** | §5 |
| `UX2-C-02` | blocker | **DISCHARGED** by accepted deferral | §5 |
| `UX2-C-03` | major | **DISCHARGED** | `A-65` + `#D25` |
| `UX2-C-04` | major | **DISCHARGED** — replacement oracle verified | `A-66` |
| `UX2-C-05` | major | **DISCHARGED** | `A-72` / `HLR-N16.4` + `#D26` |
| `UX2-C-06` | major | **DISCHARGED** (US-N07 half); US-N14 half deferred with the cut story | `A-71` |
| `UX2-C-07` | major | **DISCHARGED** | `A-70` |
| `UX2-C-08` | major | **PARTIAL** — the predicate is right; its own prescribed discharge fails it | `A-68` |
| `UX2-C-09` | minor | **DISCHARGED** | `A-69` + `#D27` |
| `UX2-C-10` | minor | **DISCHARGED** — fourth collision captured | `A-67` |

### 1.2 · Newly raised

| id | Class | Gates | One line |
|---|---|---|---|
| `UX3-C-A` | **blocker** | `Inc-1` only | `PRED-4`'s floor is `4.5 : 1`; its prescribed token measures `4.00 : 1`. The fix fails the gate |
| `UX3-N-1` | ⚠ notice | `Inc-8` | `01b` §3.8's "V4/V4a are byte-identical" executes FALSE at cell level — the derived count is 22 **or** 23 |
| `UX3-N-2` | ⚠ notice | `B-35` | The legend budget is **~72 rows over a 24-row pane**, not "~44"; at rest nothing declares that sections 2 and 3 exist |
| `UX3-N-3` | ⚠ notice | DDR | Three superseded blocks are not struck in place; a top-down reader meets the stale text first |
| `UX3-N-4` | ⚠ notice | `Inc-3` | `LLR-N06.2.4` declares no Pilot size, and `PRED-B` has **no trace at all** at 50 × 12 |

### 1.3 · Two corrections to MY OWN pass-2 ledger

Recorded first, because a lens that only audits others is not auditing.

1. **`UX2-C-01` is worse than I reported.** Pass 2 said *"five of eight commit the overwrite"*.
   Re-executed with a fresh app **and** a fresh workspace per target, sampling `notes` as well as
   `fields`: **7 of 8**. Only `insp-state` is safe. My first re-run this session reported **1 of 8**
   because it reused one app across targets — the first overwrite perturbs the inspector and later
   targets stop selecting-on-focus. **Recorded because it produced a plausible wrong answer** in the
   safe direction, which is the more dangerous one for a data-loss finding.
2. **`UX2-C-05`'s row budget was understated by everyone, including me.** `01b` §3.8 compares its
   54-row minimum against the **terminal**'s 34 rows. The scrolling viewport is `#help-bindings`,
   measured at **24** rows. Derived post-US-N16 total: **72**. §4.2.

---

## 2 · The 118 × 34 pilot — transcript

`App.run_test(size=(118, 34))`, real `question_mark`, real `H`/`J`/`K`/`L`, real `down`/`pagedown`/
`end`. Export tree + `mkdtemp` workspace. Script: `p1_pilot.py`.

```
=== 0 · seat facts ===
  duplicate_chords() = []
  map-scope chords (27): ['A','I','R','X','a','ctrl+p','d','e','enter','equals_sign','escape',
                          'f','g','h','j','k','l','m','n','o','q','question_mark','r','slash','u','x','z']
    map scope, key 'H'   -> FREE          map scope, key 'K'   -> FREE
    map scope, key 'J'   -> FREE          map scope, key 'L'   -> FREE
    map scope, key 'c'   -> FREE
    key 'c' anywhere in KEYMAP -> ['doors/consult/consultar mapas']

=== 1 · boot screen at 118x34 ===   HomeScreen

=== 2 · real '?' from HOME ===
  screen=HelpScreen  scope='home'  painted title='atajos · home'

=== 4 · the four pan chords on the SHIPPED MapScreen ===
  frame hash at rest                = ab23f28e89691925
    press 'H' -> MapScreen  frame UNCHANGED (ab23f28e89691925)
    press 'J' -> MapScreen  frame UNCHANGED (ab23f28e89691925)
    press 'K' -> MapScreen  frame UNCHANGED (ab23f28e89691925)
    press 'L' -> MapScreen  frame UNCHANGED (ab23f28e89691925)
  frame hash after all four         = ab23f28e89691925  == rest

=== 5 · real '?' from MapScreen ===
  screen=HelpScreen  scope='map'
  dialog region = Region(x=19, y=3, width=80, height=28)
  pane   region = Region(x=21, y=6, width=76, height=24)   max_scroll_y = 14
  painted title = 'atajos · map'
  bindings_for('map') = 27 labels
  visible at rest (CLIPPED to #help-dialog) = 16/27
  MISSING at rest = ['alternar diff','alternar foco','alternar outline','alternar radial',
                     'cobertura','exportar svg','ir al rail','mostrar/ocultar ficha',
                     'mostrar/ocultar rail','plegar rama','siguiente faltante']

=== 6 · what the legend declares for ITSELF ===
    escape     -> cerrar
    q          -> cerrar

=== 7 · scroll keys: do they WORK, are they DECLARED ===
  focused widget = VerticalScroll(id='help-bindings')
    real 'down'     x9 -> scroll_y 0 -> 9    WORKS=True   declared in help scope? False
    real 'pagedown' x9 -> scroll_y 0 -> 14   WORKS=True   declared in help scope? False
    real 'end'      x9 -> scroll_y 0 -> 14   WORKS=True   declared in help scope? False

=== 8 · union over REAL-KEY ('pagedown') scroll positions ===
  reachable = 27/27   unreachable = []
```

**Three findings, all as the brief predicted:**

1. **`?` routes to a per-screen scope.** `home` → `atajos · home`; `map` → `atajos · map`. The
   routing works. The painted title still names the **scope**, not the **view** — US-N16 requires
   `leyenda · <vista>`; that is in scope and specified, not a finding.
2. **The scroll keys work and none is declared.** `bindings_for('help')` is exactly `escape` and `q`.
   Reachability is total (`27/27`) and undeclared. `UX2-C-05` reproduces at `94ad8d3` unchanged.
3. **The four pan chords are inert on the shipped screen and all four are free.** Frame hash
   identical before and after all four presses; `duplicate_chords()` returns `[]`.

**The clip discipline held.** `16/27`, not the `17/27` an unclipped whole-frame scan produces —
`cobertura` shows through around the dialog from `MapScreen`'s keybar. The oracle is clipped to
`#help-dialog`, per my own pass-2 correction.

---

## 3 · Audit of my ten conditions against disk

Audited against **my pass-2 ledger**, never against the amendment table. The table is honest this
time — §6.5's closing block explicitly records `UX2-C-01` and `UX2-C-02` as **NOT CLOSED** rather
than omitting them, which is the failure it fell into twice earlier. That is worth saying.

### `UX2-C-03` — **DISCHARGED**

`01-requirements.md:1648` names `H` `J` `K` `L`; `:1665` adds the threshold addendum — *"`AT-011` and
`AT-012` **shall press the real `H`, `J`, `K` and `L`**, never `action_*` directly"*, and `AT-012`'s
edge arm reads `borde del territorio` from the painted frame. Executed above: four chords free, inert,
`duplicate_chords()` `[]`. The chord-agnostic acceptance `QA-B-10` forbids is gone.

⚠ `UX3-N-3`, limb 1: `:1673`–`:1681` still carries **⚠ ROUTED … `Inc-3` shall not open until the cap
is ruled**. `A-74` rules it; the in-place block is not struck. A reader working top-down hits the
stale stop-order first.

### `UX2-C-04` — **DISCHARGED**, and the replacement is verified rather than assumed

This was flagged as the third occurrence of the trap, so I executed **both** oracles at four widths
rather than re-deriving the broken one (`p7_oracle.py`):

```
=== 50 x 12  ===  PARKED (raw-ID trace) 0/8      A-66 PRED-B (title trace) 0/8
=== 80 x 24  ===  PARKED               0/8      A-66 PRED-B              8/8
=== 118 x 34 ===  PARKED               0/8      A-66 PRED-B              8/8
=== 120 x 40 ===  PARKED               0/8      A-66 PRED-B              8/8
     ok erp    title='Sistema ERP Legacy'   trace='Sistema'
     ok cont   title='Contabilidad'         trace='Contabi'
```

**The parked oracle is false at every width; the replacement is true at the context of use and
above.** `PRED-A` reads the renderer's painted id set as data, `PRED-C` reads the fold pill on the
surface, and `LLR-N06.2.4:2061` states plainly that *"neither substitutes for the other"* — one arm
proves the walk arrived, the other proves the operator can see that it did. Two named mutants guard
both directions. **This is a sound replacement and I ratify it.**

⚠ `UX3-N-4`: at 50 × 12 `PRED-B` has **no trace for any node**, because the canvas paints no title at
that size at all. That is correct behaviour, not a false-fail — but `LLR-N06.2.4` declares **no Pilot
size**, while `HLR-N16.1`'s oracle block requires every `AT` to declare one. An `AT-046` that swept
50 × 12 would false-fail a perfect implementation for the fourth time. One line: name the size.

### `UX2-C-05` — **DISCHARGED**

`HLR-N16.4` (`:4494`–`:4547`) reproduces my pilot's numbers exactly and its threshold is a real set
equality: *"the set of keys with a measured effect while the legend is open **equals** the set the
legend paints for its own scope … derived by pressing each real key and observing `scroll_y` or the
screen stack, **never** by reading the seat alone."* `M-N16.4-a` is the correct mutant — it names the
seat-only variant that would be green without pressing anything. Limb (c), the information-design
question, is answered by `#D26`; ruled at §4.2.

### `UX2-C-06` — **DISCHARGED** (US-N07 half)

`AT-052` (`:2720`) requires the painted count line to name its subject and term, so the two surfaces
are distinguishable **by content** rather than by an implementer's wording. `E1b`'s copy is re-derived
(`:2737`) and `E1c` correctly retained verbatim. The US-N14 half travels with the cut story — that is
legitimate, not a drop: the mode it describes cannot arise while the lens does not exist.

### `UX2-C-07` — **DISCHARGED**

`AT-051` presses the real `M` (`:2762`) — *"the only arm that distinguishes a rebind from a rename"* —
and `Inc-4` paints a one-time declaration on the first `n` press after the rebind, in the toast
register the product already executes. `M-N07.3-rebind` names the do-nothing variant that would be
**green on every existing test**. Both limbs of my finding are closed.

### `UX2-C-08` — **PARTIAL**, and this is `UX3-C-A`

`PRED-4` itself is exactly right, and it is stronger than what I asked for: contrast `>= 4.5 : 1` at
the guaranteed rung **and never equal to `GROUND` at any reachable rung** — the second clause closes
the `WINDOWS`-rung invisibility I flagged. `M-N06.3-legibility` correctly guards the `V8` half.

**But the DISCHARGE clause at `:2132` — *"`V7` and `V8` move off `WORDMARK` to `MUT`"* — does not
satisfy `PRED-4`.** Executed (`p2_colour.py`), tokens read from `mapper/darkside.py`:

```
=== PRED-4's floor is 4.5 : 1 vs GROUND at the GUARANTEED rung (EIGHT_BIT) ===
token      hex       slot   TC vs GROUND  8bit vs GROUND  PRED-4?
ACCENT     #1783ff     33          5.73:           5.91:  PASS
ALERT      #ff4f42    203          6.45:           7.05:  PASS
INK        #f5f5f5    255         19.26:          18.10:  PASS
MUT        #737373    242          4.43:           4.00:  *** FAIL ***
PANEL      #121212    233          1.12:           1.12:  *** FAIL ***
STEP       #262626    235          1.39:           1.39:  *** FAIL ***
WARN       #ffd230    221         14.51:          15.14:  PASS
WORDMARK   #3a3a3a    237          1.85:           1.85:  *** FAIL ***

=== which tokens actually CLEAR PRED-4's floor on GROUND at EIGHT_BIT ===
  ['ACCENT', 'ALERT', 'INK', 'WARN']
```

**`4.00 < 4.5`.** The requirement prints that very number at `:2119`, four lines above the predicate
that rejects it. Nobody compared the two.

This is `C-53`'s sharper half in its exact form, and it is the failure mode `A-66` had just finished
repairing in a different organ: **a gate that cannot be passed gets weakened, and the weakening
ships.** `Inc-1` cannot both follow the DISCHARGE and pass `PRED-4`.

**Only four shipped tokens clear the floor, and three are spoken for:** `ACCENT` is
interactivity-only (`01b` §3.5), `WARN` is severity, and `ALERT` is the one `#D27` has just ruled must
stay unspent. **The only free token that clears the floor is `INK`.**

**Discharge — a one-line decision, `Inc-1`'s, before it opens.** Either (a) `V7`/`V8` take `INK`
rather than `MUT`, or (b) `PRED-4`'s floor is restated at a number the palette can actually meet and
the restatement is argued rather than back-fitted to `MUT`. **I do not rule between them** — (a) costs
a hue decision that is the palette owner's, (b) costs a weakened floor. What I refuse is shipping the
contradiction, because the resolution that happens by default is (b) performed silently at
implementation time.

⚠ **Secondary, not conditioned.** `M-N06.3-legibility`'s remedy broadens `PRED-4` to *"every token
carrying a declaration role, derived from `01b` DECISION 3"*. Most of DECISION 3's vocabulary paints
`on PANEL`, not `on GROUND`, and `PRED-4` names `GROUND` as the sole background. `MUT` measures
`4.00 : 1` on `GROUND` and **`3.57 : 1` on `PANEL`**. Under the broadened quantification the predicate
would measure several rows against a background they are never painted on.

### `UX2-C-09` — **DISCHARGED**

`PRED-VIS` (`:3079`) requires the difference to be *"carried by a declared token or glyph, not by the
string alone"*, and limb 2 is closed: `:3110` — *"**This arm shall run at 118 × 34**, or at both
sizes."* The `↵`-does-two-jobs note is carried at `:3114` as I asked, without being over-conditioned.
The token choice is ruled by `#D27`; ruled at §4.3.

⚠ `UX3-N-3`, limbs 2 and 3: `:3075` still declares `App.run_test(size=(140, 45))` in the
**Executed verification** line, and `:3099` still carries *"⚠ THE TOKEN THIS WANTS IS `ALERT`"* and
routes a choice `#D27` has since made. Both are superseded later in the same requirement, so the
document is correct read whole and misleading read top-down.

### `UX2-C-10` — **DISCHARGED**

`HLR-S06.2` (`:849`–`:876`) retires `assumed`, declares the guaranteed rung as **`EIGHT_BIT` and
above**, and adds a derived perceptual floor (`min ΔE00 >= 10` over the declared token set, derived at
run time — `C-31` honoured). **The fourth collision I was told to check for is captured**, at `:869`:

```
WINDOWS   ACCENT = VIOLET = 94 · WORDMARK = GROUND
```

`WORDMARK ≡ GROUND` is recorded, and `PRED-4`'s *"never equal to `GROUND` at any rung the product can
reach"* clause converts it from a note into a predicate. **Verified at the rung, not in the abstract.**

---

## 4 · Review of the three addendum rulings

These were issued today by the orchestrator and had no independent review. All three are **sound in
substance**. Two I ratify outright; the third I ratify with a condition.

### 4.1 · `#D25` — the seat-diff figure is a pin on `Inc-4`'s diff · **SOUND — RATIFIED**

**The premise it overturns does execute FALSE, and I verified the mechanism rather than the argument.**

```
duplicate_chords() = []
map scope, key 'H' -> FREE    'J' -> FREE    'K' -> FREE    'L' -> FREE
press 'H','J','K','L' on the shipped MapScreen -> frame hash unchanged, == rest
```

`#D5b`'s reading is correct on three independent grounds and I checked each against
`PDR-…:394-398` as quoted: the sentence **enumerates its own three rows**, so the figure is a count of
a diff and not a budget chosen in advance; the **next sentence** names `Inc-3`, `Inc-6` and `Inc-9` as
`keymap.py` touchers and imposes `duplicate_chords()` plus the whole-seat pin on them **without a row
budget**; and `#D5b`'s subject is `Inc-4`'s ownership — *"alone"*. A decision that contemplated a
per-increment cap and then listed three other increments' obligations without mentioning one does not
have a per-increment cap. **There is no breach. `Inc-3` is unblocked.**

**The enlarging half is the part I most want to endorse.** `C-D25a` — every seat-touching increment
declares and pins its **own** row diff — is a better control than the thing it replaces, and its
stated reason is right: a global cap *"would price a well-cut increment against an unrelated one's
spending."* The alarm was a false-fail, `C-53` prices that as high as a false pass, **and the
disposition still left the base of truth larger than it found it.** That is how a false-fail should be
closed.

**Also correct to have recorded, and it is the finding of the three:** `#D10` resolves to two
different decisions across two registries. An id that resolves to two decisions is the glue failing.
`B-34` is the right carry.

### 4.2 · `#D26` — the legend scrolls, the tabbed redesign defers · **SOUND — RATIFIED**

**I was asked to check the `01b` §3.8 reading it leans on. The reading is correct, and it is
conservative — the real case is stronger than `#D26` states.**

§3.8's arithmetic checks out: `27 + 10 + 6 + 1 + 5 + 1 + 4 = 54` rows minimum. But **§3.8 compares
that against the terminal's 34 rows, and the terminal is not the container.** Measured in the pilot:
`#help-dialog` is **28** rows, and the scrolling viewport `#help-bindings` is **24**. Derived
mechanically from `01b`'s own tables rather than hand-counted (`p3_rows.py`):

```
=== POST-US-N16 LEGEND ROW BUDGET (derived, never hand-counted) ===
  map-scope bindings                 : 27
  group headers + blanks (01b 3.8)   : 10
  glyph-vocabulary rows + 1 header   : 23 + 1
  colour-with-a-job rows + 1 header  :  5 + 1
  panel title + `? cierra` + footer  :  4
  ----------------------------------------
  MINIMUM legend height              : 71   (with #D27's row: 72)
  01b 3.8's figure for the same sum   : 54   (it budgeted 6 prototype glyph rows)

  #help-bindings pane (pilot, 118x34): 24   <- the real scrolling viewport
  shortfall vs 24 : 48 rows            implied max_scroll_y ~48 (today, measured: 14)
  pages of content at 24 rows/page : ~3.0
```

**The flat panel is ruled out by a wider margin than `#D26` claims**, so its conclusion holds *a
fortiori*. Its four supporting reasons are all sound, and reason 3 is the one that makes the deferral
honest rather than convenient: **content is not lost** — my pilot measured `27/27` reachable by real
keys — so this is purely discoverability, and `HLR-N16.4` fixes discoverability under either layout.
Reason 4 is also right: a two-pane legend is a new information architecture with a new focus model,
and adopting it at the final PDR iteration is new scope. `C-D26a` (equality over **content**, never
over visible rows) and `C-D26b` (real keystrokes, never `scroll_to`) are both correct and both
load-bearing; `C-D26b`'s target is real and on disk at `tests/test_repair_layout.py`, whose
`_painted_bindings` helper scrolls with `pane.scroll_to(y=…)`.

⚠ **`UX3-N-2` — declared, NOT blocking, and it should ride `B-35` with a real number.** `#D26` and
`A-72` both work from "~44 rows" / "roughly tripling". The derived figure is **~72 rows over a 24-row
viewport — about three pages.** At rest the operator sees page 1 and **nothing painted declares that
pages 2 and 3 exist**: `HLR-N16.4` declares the *keys*, which closes reachability-discoverability, but
not *content*-discoverability. The two sections US-N16 exists to add are the two furthest down.
I deliberately do **not** condition on this — conditioning would import exactly the new scope `#D26`
correctly refuses — but `B-35` should inherit `72 / 24`, not `~44`.

⚠ **`UX3-N-1` — the derived count is not determined by the tables as written.** `01b` §3.8's note
(`:381`–`:387`) asserts that `V4` and `V4a` are *"byte-identical in glyph, label and style"*, so
striking the duplicate takes 23 to **22**. Executed over the tables — extracting `(glyph, label,
style)` triples mechanically — the duplicate does **not** collapse: `0` collapsed duplicates, `23`
distinct. The two rows share label and style, but the `V4a` glyph cell carries a parenthetical the
`V4` cell does not, so they are not byte-identical **as cells**. **`LLR-N16.2.1` therefore derives 22
or 23 depending on a normalisation nothing specifies.** In a document that has shipped four wrong
counts and built a derivation specifically to stop a fifth, the derivation's *input* is ambiguous.
One line in `Inc-8`: state the normalisation, or normalise the cells.

### 4.3 · `#D27` — the damaged card takes a glyph, `ALERT` is not spent · **SOUND, WITH ONE CONDITION**

**I was asked to rule on whether `MUT on PANEL` reads correctly for a DAMAGED map. My ruling: the
glyph is right, the refusal to spend `ALERT` is right, and the colour pairing is the weakest limb of
an otherwise good argument — but it is weak in a way a condition fixes, not a way that reverses the
ruling.**

**What I ratify, and it is the substance.** The scarcity argument is genuinely good and I would not
have reached it as quickly. `ALERT` is free **only because the lens is cut**, and the lens is
*scheduled, not cancelled* — spending it now hands the follow-on batch a token with two jobs, an
unadjudicable `LLR-S06.3.5` one-job census, and a `colores con empleo` row this batch never budgeted.
That is `C-55` limb 2 named correctly: **ruling on an emptiness that is an accident of today's scope
costs the next batch a defect this batch cannot see.** Verified: `mapper/darkside.py` ships nine
tokens, `Inc-1` adds three, and `01b` §3.4/§3.5 spend all three (`VIOLET` = `enlaza mapas`,
`TEAL` = `procedencia repo`, `SAGE` = `completo / vigente`). **There is no unspent colour token.**

**A glyph is also the conventional carrier in this view, not a fallback.** `01b` §3.4 is glyph-led in
every row — `⇄`, `◍`, `▲`, `█`/`░`, `∙` — with colour secondary throughout. And a glyph answers my
own complaint directly: *"a card that differs only in text differs only to someone already reading
it."* A glyph is scanned. `C-D27b`'s refusal to fix a codepoint in the ruling is also correct — that
would have been the fifth hand-listed count.

**Where the argument is weak — limb 2, and it is the limb that answers the question I was asked.**
`#D27` argues *"`MUT on PANEL` is the sala's existing pairing for absent information … a map that
cannot be summarised is an absence of information, not an alarm."* Two problems:

1. **It is the wrong semantic register.** `V21` unlit (`sin acta`) and `V15` (`faltan campos`) are
   **passive statuses** — nothing is asked of the operator. The damaged card's declared copy is
   `mapa dañado — ↵ ver por qué`: it **invites an action**. Painting a call-to-action in the register
   the vocabulary reserves for passive absence is a mismatch, and it is the mismatch the operator
   would feel rather than name.
2. **It gives the colour zero discriminating power over the exact pair the requirement exists to
   separate.** `A-69` measured `roto` and `sano_vacio` painting byte-identically. `sano_vacio` **is**
   absent information — it is the canonical `MUT on PANEL` case. Assign damage the same pairing and
   the entire discrimination rests on the glyph alone.

**Point 2 is not fatal, and this is why I ratify.** `PRED-VIS` reads the **painted row**, and a
distinct glyph makes the rows differ, so the predicate is satisfiable and `C-D27d`'s retained
healthy-empty control is what keeps it honest. But the ruling should **say** that the glyph carries
the whole load, rather than implying the colour helps.

**The condition — because `#D27` never measured its own pairing.** Executed:

```
=== #D27's pairing: MUT on PANEL (the damaged sala card) ===
  MUT on GROUND  truecolor  4.43:1   EIGHT_BIT (slot 242 on 16)   4.00:1
  MUT on PANEL   truecolor  3.95:1   EIGHT_BIT (slot 242 on 233)  3.57:1
```

**`3.57 : 1` at the guaranteed rung.** In the same batch, on the same question — *is this declaration
legible?* — `A-68` sets a floor of `4.5 : 1` and `#D27` names a pairing measuring `3.57 : 1`, and
neither ruling knows about the other. The damaged-map declaration is the one card state whose whole
purpose is to be caught while **scanning** a sala.

> **`C-D27e` (mine, added):** the damaged card's glyph limb carries a **legibility arm measured the
> way `PRED-4` measures**, against the background it is actually painted on (`PANEL`, not `GROUND`),
> at 118 × 34. If the chosen pairing cannot clear the floor the batch sets elsewhere, that is a
> statement worth making in writing — not one to discover after `Inc-7` ships.

This costs no token, no design ruling and no new surface. It is the same arm `A-69` already requires,
with its background corrected and its floor named.

---

## 5 · `UX2-C-01` and `UX2-C-02` — my explicit ruling

The disposition was referred to me. I split it, because `PDR-addendum-3` §5 states the cost of the
deferral honestly and then attaches a remedy that does not remedy.

### 5.1 · `UX2-C-02` — **DEFERRAL ACCEPTED**

Clean, and I accept it without reservation. The lens is cut, `c` has no consumer, and naming an entry
chord for a feature nobody is building is speculative — it would be a seat row added to satisfy a
condition rather than a user. It carries no data-loss limb. **Defer to `B-31`/`B-32`.**

**One datum to carry, measured today, because it changes the mnemonic argument my pass 2 made:**

```
  map scope, key 'c'          -> FREE
  key 'c' anywhere in KEYMAP  -> ['doors/consult/consultar mapas']
```

`c` is free in **map** scope, so there is no collision — but it is **taken in `doors`** as
`consultar mapas`. Adopting `c` for `consultar campos` gives one letter two jobs on two screens. It is
defensible (both are "consultar"), and it is a better argument than my pass 2 made, since the
transfer is real. But it is now a **ruling** rather than a free pick, and it should be made with the
feature. `B-31` should inherit that.

### 5.2 · `UX2-C-01` — **deferral of the DESIGN RULING accepted; the recorded RATIONALE refused**

**First, the defect, re-executed at `94ad8d3` in a temp workspace, fresh app per target
(`p5_commit_fresh.py`):**

```
=== FRESH MapperApp + FRESH temp workspace per target, 118x34 ===
=== real pilot.press('n'), then blur ===
  insp-title      'Sistema ERP Legacy'         -> 'n'   DISK REWRITTEN  delta={'title': (…, 'n')}
  insp-state      None                         -> None  disk unchanged  delta={}
  insp-field-D    'ACTA-2011-034'              -> 'n'   DISK REWRITTEN  delta={'D': (…, 'n')}
  insp-field-O    'Juan Perez'                 -> 'n'   DISK REWRITTEN  delta={'O': (…, 'n')}
  insp-field-E    'obsoleto'                   -> 'n'   DISK REWRITTEN  delta={'E': (…, 'n')}
  insp-field-C    'alta'                       -> 'n'   DISK REWRITTEN  delta={'C': (…, 'n')}
  insp-field-N    'migracion planeada 2027'    -> 'n'   DISK REWRITTEN  delta={'N': (…, 'n')}
  insp-notes      'Sin mantenimiento formal…'  -> 'n'   DISK REWRITTEN  delta={'notes': (…, 'n')}

  of 8 focusables:  OVERWROTE a ficha value : 7    REWROTE the sidecar to disk : 7
```

**Seven of eight. Both `.mmd` and the `_nodos.yml` sidecar rewritten, from one keystroke, with no
confirmation and no explicit edit gesture.** Only `insp-state` — the one non-`Input` focusable — is
safe. The mechanism is on disk in ten lines: `mapper/widgets/inspector.py:277-291`, where
`on_input_blurred` calls `_commit`, and `_commit` ends

```python
self.post_message(self.FieldCommitted(self.node.id, field, widget.value))
```

with no comparison against the stored value anywhere above it.

**Second — I exercised the remedy §5 records, and it does not close this condition.**

> §5: *"the minimal alternative is stated: gate `_commit` on a non-empty delta, which also closes
> `UX2-C-11` and is one predicate, no new surface, no design ruling."*

A non-empty-delta gate asks *is `widget.value` different from the stored value?* Every overwrite
measured above answers **yes** — `'ACTA-2011-034'` versus `'n'` is a non-empty delta. **The gate
passes and the commit fires.** That gate closes `UX2-C-11`, whose rewrites have an *empty* delta, and
it closes nothing in `UX2-C-01`.

I also exercised the obvious second candidate, since the root cause is that Textual's `Input` selects
its whole value on focus (`select_on_focus: bool = True`, and the handler is gated on
`if self.select_on_focus and not event.from_app_focus`). Clearing it (`p6_remedy.py`):

```
=== R2 -- select_on_focus cleared -- real press 'n', then blur ===
   insp-field-D   'ACTA-2011-034'  -> 'ACTA-2011-034n'   DISK REWRITTEN  delta=YES
   insp-title     'Sistema ERP…'   -> 'Sistema ERP Legacyn'  DISK REWRITTEN  delta=YES
   --> values destroyed 7/7 · sidecar rewritten 7/7
```

**R2 converts destruction into corruption and does not close it either.** The value is still committed
and still written to disk from one keystroke; it is merely *recoverable*, because the operator can see
the stray character. Materially better, not a fix.

**Third — the ruling.**

> **I ACCEPT the deferral of the design ruling.** Both obvious one-predicate fixes were exercised and
> neither closes the condition. The reason is structural: **there is no edit mode.** Focus *is*
> editing, and `_commit` fires on blur unconditionally, so every printable key reaching a focused
> field is an edit the operator never declared. Closing that requires ruling what gesture means *"I
> intend to edit"* and what blur means — **which is precisely the confirmation-affordance question
> `UX2-C-11` raises.** The addendum's instinct to travel them together is right, and the honest
> conclusion is stronger than the one it drew: this is not a cheap fix being postponed, it is a
> **design ruling with no cheap fix**, and `B-31`/`B-32` is where it belongs.
>
> **I REFUSE the recorded rationale.** §5's minimal alternative must be struck or re-scoped to
> `UX2-C-11`, where it is correct. **A deferral that carries a false remedy is worse than one that
> carries none**, because the follow-on batch inherits a belief that the fix is one predicate away and
> will size the work against that belief. If any single line of this review must land, it is this one.

**Fourth — what I require of THIS batch, and it is one line, not a fix.**

`Inc-4` is in scope and gives `n` to the search walk. It does **not** create the hazard — map scope
already binds `n` today — but it **multiplies the exposure**, moving `n` from `siguiente faltante`
(occasional) to `siguiente coincidencia`, the most repeated chord in the survey session `01b` §1.3
names, on the screen where the inspector sits in the focus chain at boot (measured, §5.2's first
transcript). Because `HLR-N14.3` is deferred with the lens, **nothing in the requirement text now
records this hazard against `Inc-4` at all** — the condition left with the story, and the mechanism
stayed.

> **`C-UX3a` (mine):** `Inc-4`'s packet declares the `n`-into-a-focused-field hazard as a **known
> limit with its measured extent** (7 of 8 focusables, durable to disk), and it is carried on the same
> backlog row as `UX2-C-01`. **A declaration, not a repair** — the register `A-67` used for the
> 16-colour rung and `A-59` used for `S-20`. It costs one line and it stops the exposure increasing
> silently, which is the only part of this that is this batch's to own.

---

## 6 · What I did NOT evaluate, in writing

`01b` §7 and `02f` §7 are adopted in full. Extending them:

1. **Evaluation with real users was NOT performed.** ISO 9241-210 activity 4 asks for it. The team is
   one person; no user session was run. What was performed is **inspection against declared criteria**
   — a cognitive walkthrough over `01b` §0's task — **plus an automated walkthrough through the real
   mechanism** under `Pilot`. **A Pilot run is not a user.** Every judgement here about what the
   operator *would* feel — most load-bearingly §4.3's claim that `MUT on PANEL` reads as passive
   absence rather than as damage — is this reviewer's inference from the stated context of use, **not
   an observation of the operator.** §4.3 is the single judgement I would most want a real session to
   settle, and it would take ten minutes to settle.
2. **Colour was measured colorimetrically, never on a terminal.** WCAG relative luminance and
   CIEDE2000 over the RGB `rich` emits. No frame was displayed, no photometer used. WCAG's thresholds
   were set for web text, not terminal glyphs at cell size; I apply them as the best available proxy
   and say so. `UX3-C-A` is arithmetic against the batch's own declared floor — that part does not
   depend on the proxy being right, only on the floor being the one the batch chose.
3. **No behaviour of the four in-scope stories was exercised, because none exists at `94ad8d3`.**
   Every §3 finding is about how an acceptance is *specified to be driven*. Whether the implementation
   honours it is DDR's and validation's question.
4. **`#D27`'s glyph was not evaluated, because `C-D27b` deliberately does not name a codepoint.**
   I ruled on the **pairing** and on the register. The glyph itself is unreviewed by construction, and
   `C-D27a`'s derived-set route is what will surface it.
5. **Mouse, hover and click remain inspected, not exercised.** The context of use declares
   keyboard-only — a declared scope limit, not an omission.
6. **Screen-reader and non-visual access are out of scope entirely**, and several deliverables here —
   the glyph vocabulary, figure-ground dimming — are visual-only by construction.
7. **Only two of the six `KEY_SCOPE`-declaring screens were driven** (`home`, `map`). The others are
   *inspected, not exercised*; `HLR-N16.1` already carries their executed counts.
8. **I did not run the pytest suite.** The orchestrator owns gate runs. Every transcript here is a
   standalone scratchpad probe importing nothing from `tests/`.

---

## 7 · Evidence checklist

| ✓/✗ | Claim | Probe |
|---|---|---|
| ✓ | Base `94ad8d3`, branch `docs/amendment-set-3`; `fixtures/` clean before and after | `git rev-parse`, `git status --short` |
| ✓ | `?` routes per screen: `home` → `atajos · home`, `map` → `atajos · map` | `p1_pilot.py` §2, §5 |
| ✓ | 118 × 34: dialog 28 rows, pane **24** rows, `max_scroll_y` 14, **16/27** clipped to `#help-dialog` | `p1_pilot.py` §5 |
| ✓ | `down`/`pagedown`/`end` all scroll; `bindings_for('help')` is exactly `escape`, `q` | `p1_pilot.py` §6, §7 |
| ✓ | Union over **real-key** scroll positions = `27/27` — reachable, undeclared | `p1_pilot.py` §8 |
| ✓ | `H`/`J`/`K`/`L` free in map scope, inert on the shipped screen, frame hash unchanged | `p1_pilot.py` §0, §4 |
| ✓ | `duplicate_chords()` returns `[]` | `p1_pilot.py` §0 |
| ✓ | `c` FREE in map scope; taken in `doors` as `consultar mapas` | `p1_pilot.py` §0 |
| ✓ | `MUT` on `GROUND` = **4.00 : 1** at `EIGHT_BIT`, below `PRED-4`'s 4.5 floor | `p2_colour.py` |
| ✓ | Only `ACCENT`, `ALERT`, `INK`, `WARN` clear the floor at `EIGHT_BIT` | `p2_colour.py` |
| ✓ | `MUT on PANEL` = **3.57 : 1** at `EIGHT_BIT`, 3.95 : 1 truecolor | `p2_colour.py` |
| ✓ | Derived legend budget **72 rows** vs a **24-row** pane; 23 distinct triples, **0** collapsed | `p3_rows.py` |
| ✓ | `n` + blur overwrites **7 of 8** focusables, rewriting both files, fresh app per target | `p5_commit_fresh.py` |
| ✓ | The non-empty-delta gate does **not** close `UX2-C-01`; every overwrite has a non-empty delta | `p6_remedy.py`, reasoned on `inspector.py:291` |
| ✓ | Clearing `select_on_focus` yields corruption, not safety — still 7/7 written to disk | `p6_remedy.py` R2 |
| ✓ | Parked raw-id oracle **0/8** at four widths; `A-66`'s `PRED-B` **8/8** at 80×24, 118×34, 120×40 | `p7_oracle.py` |
| ✓ | `PRED-B` traces **0/8** at 50 × 12 — correct behaviour, but no Pilot size is declared | `p7_oracle.py` |
| ✓ | `_commit` posts unconditionally; no delta comparison exists | `mapper/widgets/inspector.py:277-291` |
| ✓ | The shipped guard scrolls by method call, not keystroke | `tests/test_repair_layout.py`, `_painted_bindings` |
| ✗ | **Not executed:** whether `MUT on PANEL` *reads* as damage to a human | requires a user session — §6 item 1 |
| ✗ | **Not executed:** any behaviour of US-N06/N07/N13/N16 | none exists at `94ad8d3` |

---

## 8 · Incident check (RIDER-1, `02g` §6)

Every `MapperApp` in this pass was constructed on a `tempfile.mkdtemp()` workspace, with fixtures
copied there from a `git archive HEAD` export **before** the app existed. The repository was never the
workspace.

```
$ git status --short
?? .dev-flow/2026-08-26-ui-next-batch-02/02h-pdr3-architect.md

$ git status --short fixtures/
[empty]

$ git diff --stat -- fixtures/
[empty]

$ grep -c "erp\[Sistema ERP Legacy\]" fixtures/legacy.mmd
1
```

**`fixtures/` shows no modification.** The `erp` node's label — the string the RIDER-1 audit replaced
with the walk chord's single character — is intact. The one untracked file is the architect lens's own
concurrent artifact, not mine. This document is the only file I wrote.

---

## 9 · Closing note to the gate

**The batch should implement.** Eight conditions were closed with predicates I could execute, and the
one I was warned would be the third repeat of a false-oracle trap was closed *correctly* — `A-66`
reused the oracle the document had already settled instead of inventing a fourth, and I verified the
replacement runs true rather than taking its word.

**The one thing worth carrying into the post-mortem is the shape of `UX3-C-A`.** `A-68` was written to
close *my* condition. It introduced a new predicate, printed the measurement, prescribed a fix — and
the fix fails the predicate by `0.5`, with both numbers on the same screen four lines apart. Nobody
compared them because **the amendment's author was checking that the predicate was right, not that the
discharge satisfied it.** That is a different check from any this batch runs, and it generalises:
*when an amendment adds a predicate and prescribes a discharge in the same breath, something must
execute the discharge against the predicate.* It is one arithmetic comparison and it would have been
caught by asking the question once.

**And the shape of `UX2-C-01` is worth carrying too, for the opposite reason.** The deferral is
right — I tried to break it and could not; both cheap fixes fail. But the *record* of the deferral
carried a remedy nobody had run. A deferral is a promise to a future batch, and a promise that names a
fix which does not fix is more expensive than a promise that admits it does not know. **The refusal in
§5.2 is the finding I would least like dropped.**
