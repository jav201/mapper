# 01c — Phase-1 probe transcripts · `2026-08-26-ui-next-batch-02`

> **What this file is.** Every claim in `01-requirements.md` §3/§4/§5 that names a code symbol, a
> constant, a framework behaviour, a threshold or a transform's output is either verified by a probe
> recorded here, or flagged `assumed — verify in Phase 3` in the requirement itself. This file holds
> the executed output; the requirement holds the predicate written against it.
>
> **Tree state for every probe below:** `git rev-parse HEAD` = `d6b60e6b4f18b10123fffc76bbb36891473df653`
> (`master`), working tree dirty only in `.dev-flow/**`, `docs/ARCHITECTURE.md` and untracked
> `prototypes/**`. No `mapper/**` or `tests/**` file was modified by any probe.
>
> **Toolchain:** Python 3.12.7 (Anaconda) · textual 8.2.8 · rich 15.0.0 · `PYTHONUTF8=1`.
> Probe scripts live in the session scratchpad, never in the repo.

---

## M-1 · `Canvas` layer drop — the HLR-canvas baseline (risk A-8)

**Source read.** `mapper/canvas.py:30-33` — `Canvas.__init__` declares exactly `self.w, self.h`,
`self.cells`, `self.bits`, `self._wire_tones`. **Neither `dots` nor `bgs` is declared.**
`mapper/canvas.py:67-82` — `rows()` reads `self.cells` then `self.bits` and nothing else.
`mapper/views/radial.py:47-48` — `cv.dots = {}` / `cv.bgs = {}` assigned onto the instance;
written at `:121` (braille dust) and `:135` (pill backgrounds).

**Executed** — a 6-node graph (root + 5 children), rendered at 80 x 24:

```
PROBE A1 -- node count: 6 edges: 5
PROBE A1 -- RadialRenderer 80x24 braille glyph count U+2800..U+28FF: 0
PROBE A1 -- distinct painted non-space chars: ['A', 'F', 'H', 'I', 'N', 'R', 'a', 'd', 'e', 'g',
  'i', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'z', '·', '◆', '●']
PROBE A2 -- LayeredRenderer 80x24 braille glyph count: 0
PROBE A2 -- distinct painted non-space chars: ['6', 'A', 'F', 'H', 'I', 'N', 'R', 'a', 'c', 'd',
  'e', 'g', 'i', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'z', '·', '…', '─', '│', '┌', '┐',
  '┬', '┼', '▐', '◆']
```

**Pre-state for the AT: exactly 0.** Both renderers. The pass condition is a strictly positive
count on the same input, which is why the acceptance is a count and not "braille appears".

---

## M-2 · Paleta v2 quantisation — the round-10 claim, EXECUTED (S-6)

The round-10 note that SAGE / TEAL / VIOLET *"survive rich's 256-colour quantisation chromatic
(slots 35 / 38 / 105)"* was recorded in §2.7 as a **hypothesis**. It is now executed.

Probe: `rich.color.Color.parse(hex).downgrade(ColorSystem.EIGHT_BIT).number`, rich 15.0.0.

```
rich version: 15.0.0
SAGE(new)      #2fbf71 -> EIGHT_BIT slot 35  (type=EIGHT_BIT)
TEAL(new)      #22b8cf -> EIGHT_BIT slot 38  (type=EIGHT_BIT)
VIOLET(new)    #9775fa -> EIGHT_BIT slot 105 (type=EIGHT_BIT)
ACCENT(ship)   #1783ff -> EIGHT_BIT slot 33  (type=EIGHT_BIT)
WARN(ship)     #ffd230 -> EIGHT_BIT slot 221 (type=EIGHT_BIT)
ALERT(ship)    #ff4f42 -> EIGHT_BIT slot 203 (type=EIGHT_BIT)
INK(ship)      #f5f5f5 -> EIGHT_BIT slot 255 (type=EIGHT_BIT)
MUT(ship)      #737373 -> EIGHT_BIT slot 242 (type=EIGHT_BIT)
STEP(ship)     #262626 -> EIGHT_BIT slot 235 (type=EIGHT_BIT)
PANEL(ship)    #121212 -> EIGHT_BIT slot 233 (type=EIGHT_BIT)
GROUND(ship)   #000000 -> EIGHT_BIT slot 16  (type=EIGHT_BIT)
WORDMARK       #3a3a3a -> EIGHT_BIT slot 237 (type=EIGHT_BIT)

distinct slots among the three NEW tokens: [35, 38, 105]
  SAGE(new)   slot 35 : collides with NONE
  TEAL(new)   slot 38 : collides with NONE
  VIOLET(new) slot 105: collides with NONE
```

**Verdict: the round-10 claim is CONFIRMED as stated** — slots 35 / 38 / 105 exactly, three distinct
slots, and no collision with any of the nine shipped tokens.

**One thing the probe does NOT establish, recorded so nobody reads the confirmation too widely.**
Distinct slot numbers are not perceptual distinguishability. `TEAL` lands at 38 and the shipped
`ACCENT` blue at 33 — both inside the cyan/blue face of the 6x6x6 cube, five slots apart. The
requirement asserts only what was measured (distinct slots, no collision). Whether 33 and 38 are
tellable apart on a real 256-colour terminal is `assumed — verify with the ux lens at PDR`.

---

## M-3 · Colour-literal census, input set DERIVED from the tree (S-6, control C-31)

Input set is `git ls-files 'mapper/*.py' 'mapper/**/*.py'` = **33 files**; hues harvested by regex
over those files, never hand-listed. `__pycache__` excluded by using the git file list.

```
--- hue histogram (10 distinct hues, 95 literal sites) ---
    19  #f5f5f5     (INK)
    18  #121212     (PANEL)
    17  #000000     (GROUND)
    16  #737373     (MUT)
    12  #262626     (STEP)
     8  #1783ff     (ACCENT -- the blue)
     2  #ff4f42     (ALERT)
     1  #ffd230     (WARN)
     1  #a3a3a3     (UNDECLARED -- not a darkside token)
     1  #3a3a3a     (WORDMARK)
```

Two findings the census produced that a hand-list would not have:

**(a) One undeclared hue ships.** `mapper/views/radial.py:18` — `"#a3a3a3"` sits inside `_GREYS`
between `darkside.INK` and `darkside.MUT`, with the comment *"Achromatic branch tints"*. It is a
literal, not a token. The census requirement must account for it or it becomes an eleventh hue
nobody owns.

**(b) Blue-is-interactivity-only holds today, and the census can prove it.** All 8 `#1783ff` sites,
7 of them outside `darkside.py`:

```
mapper/app.py:1864               background: #1783ff;                      (focus)
mapper/app.py:1906               #map-inspector Input:focus { background: #1783ff; ... }
mapper/app.py:1925               #template-table > .datatable--cursor { background: #1783ff; ... }
mapper/screens/coverage.py:58    background: #1783ff;                      (cursor)
mapper/screens/factory.py:101    background: #1783ff;                      (cursor)
mapper/screens/factory.py:104    .factory-tag { color: #1783ff; }
mapper/screens/palette.py:65     background: #1783ff;                      (cursor)
mapper/darkside.py:17            ACCENT = "#1783ff"                        (the definition)
```

Every non-definition site is a focus ring, a table cursor or a tag affordance. **`factory-tag` is the
one that needs a ruling** — a tag is a label, not an affordance, so it is either interactivity
(tags are clickable/filterable) or a violation. Recorded as an open item on the S-6 census
requirement, not silently counted as a pass.

**(c) WARN / ALERT sites, derived.** 29 sites across `app.py`, `screens/{coverage,factory}.py`,
`views/{lane,layered,outline}.py`, `widgets/{inspector,rail}.py`. Every one expresses severity —
node `state` in `risk`/`late`/`blocked`, a missing required field, an overdue count, a failed check —
**with one exception that must be dispositioned**: `mapper/app.py:848`,
`darkside.WARN if self.loading else darkside.INK`, which paints *progress*, not severity.

---

## M-4 · S-7 layout defect and its remedy, both under Pilot (risk A-9)

Probe: `MapperApp(workspace=tmp).run_test(size=...)`, press the real `enter` from Home to reach
`MapScreen`, read post-layout `widget.region` (authoritative, not CSS).

### As found on `master` — the RED

```
size=(140, 45) screen=MapScreen
   #map-rail        (x=0,   y=3, w=140, h=10, display=True)
   #map-canvas      (x=140, y=3, w=1,   h=38, display=True)
   #map-inspector   (x=141, y=3, w=36,  h=38, display=True)
   canvas addressable & wider than 1 col? False
size=(120, 40) screen=MapScreen
   #map-rail        (x=0,   y=3, w=120, h=10, display=True)
   #map-canvas      (x=120, y=3, w=1,   h=33, display=True)
   #map-inspector   (x=121, y=3, w=36,  h=33, display=True)
   canvas addressable & wider than 1 col? False
size=(100, 30) screen=MapScreen
   #map-rail        (x=0, y=0, w=0,  h=0,  display=False)   <- auto-hidden
   #map-canvas      (x=0, y=3, w=64, h=22, display=True)
   canvas addressable & wider than 1 col? True
size=(80, 24) screen=MapScreen
   #map-rail        (x=0, y=0, w=0,  h=0,  display=False)   <- auto-hidden
   #map-canvas      (x=0, y=4, w=80, h=15, display=True)
   canvas addressable & wider than 1 col? True
```

The compositor is 140 columns wide, so the last addressable column is 139 and a canvas at `x=140`
is off-screen entirely. **P-20 reproduced independently.**

### With the remedy applied — the GREEN

Applied as a subclass CSS override (`MapperApp.CSS` plus one rail width rule); `mapper/**` was not
edited.

```
size=(140, 45) #map-rail=(x0 w24)  #map-canvas=(x24 w80)  #map-inspector=(x104 w36)
        canvas first non-blank rows:
          '◆ mapper · mapa de conceptos                                     3 nodos'
          '         ▐ nomina                                                       '
size=(120, 40) #map-rail=(x0 w24)  #map-canvas=(x24 w60)  #map-inspector=(x84 w36)
        canvas first non-blank rows:
          '◆ mapper · mapa de conceptos                    3 nodos'
          '         ▐ nomina                                       '
size=(100, 30) #map-rail=(x0 w0 hidden)  #map-canvas=(x0 w64)  #map-inspector=(x64 w36)
size=( 80, 24) #map-rail=(x0 w0 hidden)  #map-canvas=(x0 w80)  #map-inspector=(x0 w0 hidden)
```

`140 - (24 + 36) = 80` and `120 - (24 + 36) = 60` — the geometry `MapScreen._chrome_width()`
(`app.py:1166-1170`) already assumes, reproduced exactly. Constants read from source:
`RAIL_WIDTH = 24` (`mapper/widgets/rail.py:18`), `INSPECTOR_WIDTH = 36`,
`MIN_CANVAS_WIDTH = 58` (`app.py:1164`).

**Regime note (environmental-measurement citation rule).** The two failing sizes lie above the
auto-hide transition; `_apply_region_visibility` (`app.py:1172-1186`) hides the rail when
`width - 24 - 36 < 58`, i.e. below 118 columns. The measurements above hold **only in the
band width >= 118 with the rail displayed and not pinned**. Applying them below 118 is out of regime.

---

## M-5 · US-N06 RED — silent clipping, quantified (control C-39)

Probe: `LayeredRenderer().render(graph, selected_id="root", w=80, h=24)` over synthetic
root-plus-N-leaves graphs; a node "leaves a full trace" iff its whole title substring appears in
`Text.plain`.

```
leaves= 10 total= 11  nodes leaving a FULL title trace:   7  -> NO trace:   3  (30%)
leaves= 21 total= 22  nodes leaving a FULL title trace:   7  -> NO trace:  14  (66%)
leaves= 40 total= 41  nodes leaving a FULL title trace:   7  -> NO trace:  33  (82%)
leaves= 61 total= 62  nodes leaving a FULL title trace:   7  -> NO trace:  54  (88%)
leaves=128 total=129  nodes leaving a FULL title trace:   7  -> NO trace: 121  (94%)
```

Header text at 129 nodes ends `'   129 nodos'`. Overflow indicator painted: **none** — the strings
`ocult`, `mas` and a `+N` pill are all absent from the output at every size.

**The number the requirement is keyed on: 7.** On an 80-column terminal the layered canvas paints a
readable title for at most 7 nodes regardless of graph size, declares the full node count in its
header, and says nothing about the remainder. At 129 nodes that is **121 nodes hidden with zero
declaration**. That is the story's defect, measured, not asserted.

---

## M-6 · US-N06 fold reconciliation arithmetic, over the REAL fixture

Fixture: `fixtures/legacy.mmd` + `fixtures/legacy_nodos.yml`, loaded through `MapStore.load`.

```
root: erp   total nodes: 8
edges: [('erp','fin'), ('erp','rrhh'), ('erp','inv'),
        ('fin','cont'), ('fin','pres'), ('rrhh','nom'), ('inv','alm')]

ramas (children of root): ['fin', 'rrhh', 'inv']
  rama fin : descendants=['cont','pres']  +N=2
  rama rrhh: descendants=['nom']          +N=1
  rama inv : descendants=['alm']          +N=1

folded=[]                     pills={}                            sum=0  hidden=0  visible=8  OK
folded=['fin']                pills={'fin':2}                     sum=2  hidden=2  visible=6  OK
folded=['fin','rrhh']         pills={'fin':2,'rrhh':1}            sum=3  hidden=3  visible=5  OK
folded=['fin','rrhh','inv']   pills={'fin':2,'rrhh':1,'inv':1}    sum=4  hidden=4  visible=4  OK
```

**Nested-fold check.** With `folded = {fin, pres}` where `pres` is a descendant of `fin`:

```
naive pills            : {'pres': 0, 'fin': 2}   sum = 2
|actually hidden|      : 2  -> ['cont','pres']
outermost folded set   : ['fin']   (a pill inside a folded branch is not painted)
pills (outermost only) : {'fin': 2}  sum = 2
```

The shipped fixture cannot exhibit the double-count failure because `pres` is a leaf (0 descendants),
so both rules agree here. **The reconciliation predicate must therefore be written over PAINTED
pills, not over the `folded` set** — that form is correct by construction for nested folds and is
also the only form observable through the shipped surface. A synthetic deeper fixture is owed at
Phase 3 as the negative control; flagged in LLR-N06.3.2.

---

## M-7 · US-N07 — the two definitions of "hit", both run over one graph (C-35 / C-42)

Definition 1 is the inline renderer predicate, transcribed from `mapper/views/layered.py:145-148`.
Definition 2 is `Graph.search_hits`, `mapper/model.py:169-184`. Query `"riesgo"` over a 6-node
graph carrying a matching node id, a matching `ficha.meta` and a matching attachment caption.

```
query: 'riesgo'
D1 renderer-inline predicate  -> ['b', 'd']
D2 Graph.search_hits          -> ['riesgo-root', 'b', 'c', 'd', 'e']
D2 minus D1 (highlighting GAINS): ['riesgo-root', 'c', 'e']
D1 minus D2 (highlighting LOSES): []
counts: |D1| = 2   |D2| = 5

--- reason per gained node ---
  riesgo-root: matched via ['node.id']
  c          : matched via ['ficha.meta']
  e          : matched via ['attachment']
```

**The widening is 2 -> 5 on this input, and it is monotone** (nothing is lost). Naming `search` the
owner (R-014 / D6) therefore causes a **user-visible change**: node ids, `ficha.meta` and attachment
captions/paths begin to highlight where they do not today. That change gets its own acceptance test.

### P-17 hit order, executed

```
search_hits order (dict-insertion) : ['riesgo-root', 'b', 'c', 'd', 'e']
tree order of all nodes            : ['riesgo-root', 'b', 'd', 'e', 'c', 'f']
hits in TREE order                 : ['riesgo-root', 'b', 'd', 'e', 'c']
identical to dict order?           : False
```

The two orders differ at position 3 on this fixture, so a tree-order requirement has a
non-vacuous pre-state. Tree order is produced by the idiom already in the tree,
`MapScreen._incomplete_order` (`mapper/app.py:1601-1623`) — pre-order DFS over
`graph.children_of`, `reversed` onto a stack.

---

## M-8 · US-N14 lens semantics, executed over the REAL shipped fixture (Q-6)

Loaded `fixtures/legacy_nodos.yml` through `MapStore.load`. **Schema keys derived from the file,
not assumed:**

```
nodes: 8   root: erp
schema keys (derived): ['D', 'O', 'E', 'C', 'N']
  D=documento  O=dueno  E=estado  C=criticidad  N=notas

id     | state    | D                | O              | E         | C      | N
erp    | risk     | ACTA-2011-034    | Juan Perez     | obsoleto  | alta   | migracion planeada 2027
fin    | ok       | ACTA-2012-011    | Ana Ruiz       | estable   | alta   | -
rrhh   | risk     | ACTA-2013-005    | Luis Gomez     | riesgo    | media  | -
inv    | late     | -                | Maria Solis    | atrasado  | alta   | -
cont   | ok       | ACTA-2012-015    | Ana Ruiz       | estable   | media  | -
pres   | blocked  | ACTA-2014-003    | Carlos Vargas  | bloqueado | alta   | -
nom    | ok       | ACTA-2013-008    | Luis Gomez     | estable   | alta   | -
alm    | risk     | -                | Maria Solis    | riesgo    | media  | -
```

Candidate parse/evaluate run — AND of `key:value` terms, `state` / `title` / `id` reserved as
pseudo-fields, everything else resolved against the derived schema key set:

```
E:riesgo C:alta        -> EMPTY            hits=[]                          n=0 ramas=0  unknown=[]
E:obsoleto             -> MATCH            hits=['erp']                     n=1 ramas=1  unknown=[]
C:alta                 -> MATCH            hits=['erp','fin','inv','pres','nom'] n=5 ramas=3 unknown=[]
E:obsoleto C:alta      -> MATCH            hits=['erp']                     n=1 ramas=1  unknown=[]
state:risk             -> MATCH            hits=['erp','rrhh','alm']        n=3 ramas=2  unknown=[]
state:risk C:alta      -> MATCH            hits=['erp']                     n=1 ramas=1  unknown=[]
Z:algo                 -> UNDEFINED-FIELD  hits=[]                          n=0 ramas=0  unknown=['Z']
E:obsoleto Z:algo      -> UNDEFINED-FIELD  hits=[]                          n=0 ramas=0  unknown=['Z']
C:zzz                  -> EMPTY            hits=[]                          n=0 ramas=0  unknown=[]
```

Four things this transcript settles, none of which could have been settled by reading:

1. **Three outcome classes exist and are separable on real data**: `MATCH`, `EMPTY` (every key is
   defined, no node satisfies the conjunction), `UNDEFINED-FIELD` (some key is in neither the schema
   nor the reserved set). That is the Q-6 answer, demonstrated rather than asserted.
2. **The story's own example query is an `EMPTY`, not a `MATCH`.** `E:riesgo C:alta` returns zero on
   the shipped fixture: `E:riesgo` alone matches `rrhh` and `alm`, `C:alta` alone matches five, and
   the conjunction is empty. A requirement whose only worked example returns nothing needs the
   distinction of item 1 or its acceptance is vacuous.
3. **`state:` and `E:` are different namespaces carrying different vocabularies.** `state` takes
   `ok` / `risk` / `late` / `blocked` (`mapper/model.py:29`); schema key `E` ("estado") takes
   `obsoleto` / `estable` / `riesgo` / `atrasado` / `bloqueado`. `state:risk` returns 3 nodes;
   `E:riesgo` returns 2, and they are not the same 2. The parser must route by namespace, and the
   collision of the Spanish word "estado" across both is exactly the kind of thing that is settled
   in a spec or discovered in production.
4. **`ramas` is a defined count, not an adjective.** Values above use *rama = the root-child ancestor
   of the match*. `C:alta` -> 5 nodes in 3 ramas.

---

## M-9 · Keymap seat state — Q-3, US-N14's walk chord, US-N16's derived input

```
KEYMAP size: 48        duplicate_chords(): []
scopes: ['app','help','home','import','map','palette','plug','repo']
  app     n= 2  ['ctrl+p','question_mark']
  help    n= 2  ['escape','q']
  home    n=11  ['c','f','i','j','k','n','p','q','r','s','t']
  import  n= 2  ['escape','s']
  map     n=25  ['A','I','R','X','a','d','e','enter','equals_sign','escape','f','g','h','j','k',
                 'l','m','n','o','q','r','slash','u','x','z']
  palette n= 2  ['enter','escape']
  plug    n= 1  ['escape']
  repo    n= 3  ['j','k','q']

bindings_for('home')  -> 13 rows      bindings_for('map')  -> 27 rows
bindings_for('repo')  ->  5 rows      bindings_for('app')  ->  2 rows
bindings_for('plug')  ->  3 rows      bindings_for('import') -> 4 rows
bindings_for('palette') -> 2 rows     bindings_for('help') -> 2 rows
```

**Q-3, re-executed.** `map 'n' -> next_gap 'siguiente faltante'`. `N` is bound in no scope.
`shift+n` is bound in no scope. Confirms P-11.

**`z` is already `collapse_branch` ("plegar rama") in map scope.** US-N06's fold has a chord today.

**The seat's key names are not the glyphs.** `?` is stored as `key="question_mark"`,
`/` as `"slash"`, `=` as `"equals_sign"`; `groups_for_keybar`'s own docstring
(`mapper/keymap.py:196`) says *"nobody presses a key called question_mark"*. **Every acceptance test
that "drives the real key" must press the seat's key name**, which is what Textual dispatches on.
Verified below in M-11.

**Digits 0-9 are bound in no scope** — US-N14's saved lenses on number keys are free.

---

## M-10 · The `tab` finding — US-N14's walk chord is blocked by two GREEN guards

**This is the largest contradiction Phase 1 found between the brief and the tree.**

US-N14 as briefed: *"`⇥` walks results with the inspector focused."* Executed against the tree:

```
mapper/keymap.py:49   TAB_BINDING_EXCEPTIONS = ("SettingsScreen", "EditorScreen")
mapper/keymap.py:46-48  comment: "tab belongs to focus traversal: a screen-level tab binding was
                        measured to produce 0 focus moves in 9 presses (LLR-N06.5)."

tests/test_keymap.py:160  test_no_seat_entry_binds_tab
                          asserts [b for b in KEYMAP if b.key == "tab"] == []
tests/test_keymap.py:165  test_llr_n06_5_no_screen_binds_tab_outside_the_recorded_exceptions
                          asserts no Screen subclass binds "tab" unless named in the exception list
tests/test_keymap.py:194  test_tab_binding_exceptions_are_still_real   (fences the exception list)
```

Executed, both guards and their fences are green today:

```
$ pytest tests/test_keymap.py -q -k "tab"
.....                                                             [100%]
5 passed, 63 deselected in 0.07s
```

`MapScreen` is **not** in `TAB_BINDING_EXCEPTIONS`. Binding `tab` in the seat reddens the first
guard; binding it on `MapScreen` reddens the second.

**And `tab` is load-bearing today.** Nine real `tab` presses under Pilot on `MapScreen` at 140 x 45:

```
press 1: OutlineRail#map-rail
press 2: FieldInput#insp-title
press 3: DsSegmented#insp-state
press 4: FieldInput#insp-field-D
press 5: FieldInput#insp-field-O
press 6: FieldInput#insp-field-E
press 7: FieldInput#insp-field-C
press 8: FieldInput#insp-field-N
press 9: FieldInput#insp-notes
distinct focus targets: 9        focus transitions: 8
```

**`tab` is how the inspector is keyboard-reachable at all.** Taking it for a lens walk removes the
only path to eight editable fields. This is raised as **Q-7** in `01-requirements.md` and the
walk requirement is written chord-agnostic, with the eight measured transitions as a standing
invariant the chosen chord must not reduce.

---

## M-11 · US-N16 — the `?` scope defect, driven through the real key (P-13 is under-counted)

### The routing census, derived rather than cited

```
$ grep -rn "def action_help" <git ls-files mapper>
mapper/app.py:742             (_ImportPreviewScreen)   -> push_screen(HelpScreen())     NO SCOPE
mapper/app.py:793             (PlugRepoScreen)         -> push_screen(HelpScreen())     NO SCOPE
mapper/app.py:1058            (RepoScreen)             -> push_screen(HelpScreen())     NO SCOPE
mapper/app.py:1828            (MapScreen)              -> delegates to app.action_help  ok
mapper/app.py:1986            (MapperApp)              -> HelpScreen(getattr(screen,"KEY_SCOPE",SCOPE_APP))
mapper/screens/factory.py:413 (FactoryScreen)          -> push_screen(HelpScreen())     NO SCOPE
mapper/screens/settings.py:92 (SettingsScreen)         -> push_screen(HelpScreen())     NO SCOPE
```

**P-13 recorded three scope-dropping routes. Executed, there are five.** The census that produced
P-13 was itself scoped to `mapper/app.py` — the identical failure shape P-13's own disposition was
written to prevent, one level up. `FactoryScreen` and `SettingsScreen` are named in
`keymap.UNMIGRATED_SCREENS`, but that list fences **seat membership**, not help-scope routing, so it
does not disposition them here.

### A second defect underneath the first

```
$ grep -rn "KEY_SCOPE" <git ls-files mapper>
app.py:341  HomeScreen           = SCOPE_HOME
app.py:690  _ImportPreviewScreen = SCOPE_IMPORT
app.py:749  PlugRepoScreen       = SCOPE_PLUG
app.py:800  RepoScreen           = SCOPE_REPO
app.py:1065 MapScreen            = SCOPE_MAP
app.py:1943 MapperApp            = SCOPE_APP
```

`FactoryScreen` and `SettingsScreen` declare **no `KEY_SCOPE` at all**, and both hand-write
`BINDINGS` rather than generating them from the seat. Repairing only the route on those two screens
would resolve `getattr(self, "KEY_SCOPE", SCOPE_APP)` to `SCOPE_APP` and the legend would still be
wrong — a fix that passes its own test. **The requirement must therefore quantify over the derived
screen set on BOTH limbs: routes with its own scope, and declares one.**

### Observed through the real key, on the shipped surface

Pressed `question_mark` under Pilot at 140 x 45 and read the rendered legend rows:

```
HomeScreen      KEY_SCOPE='home'            help.scope='home'  title='atajos · home'
                rows painted= 13   bindings_for('home')= 13   MATCH=True
MapScreen       KEY_SCOPE='map'             help.scope='map'   title='atajos · map'
                rows painted= 27   bindings_for('map')= 27    MATCH=True
SettingsScreen  KEY_SCOPE=<NONE DECLARED>   help.scope='app'   title='atajos · app'
                rows painted=  2   bindings_for('app')=  2    MATCH=True
```

**The defect, stated as an observable:** reached through the real `?` on `SettingsScreen`, the legend
paints **2** key rows for a screen that binds **6** (`q`, `escape`, `tab`, `shift+tab`, `ctrl+p`,
`?` — `mapper/screens/settings.py:49-55`).

**And the oracle trap, which matters more than the defect.** The naive set-equality oracle
"painted rows == `bindings_for(help_screen.scope)`" is **TRUE on all three rows above, including the
broken one** — because the bug is in *which* scope was passed, not in the derivation from it. Written
that way the acceptance is vacuous. The oracle must key on the **source screen's own declared
scope**: painted rows == `bindings_for(source_screen.KEY_SCOPE)`. That is the form specified in
AT-041 / AT-042.

Legend title today is `"atajos · <scope>"` — it names the **scope**, not the **view**. US-N16 asks
for the view; that is a change, not a description.

`?` and `??` in the seat: `[]` for both as a literal `"?"` key. `?` ships as `question_mark`;
`??` is bound nowhere, in any scope.

---

## M-12 · US-N13 — every card datum derived from data `HomeScreen` already discards

`HomeScreen.on_mount` (`mapper/app.py:439`) calls `store.load(map_name)` once per `.mmd`
(`app.py:547`) and keeps only `kind`, `nodos`, `docs` for the recents `DataTable`. Everything the
story asks for is computable from the `Graph` it already has and throws away:

```
map='legacy'
   total=8  con_acta=6  sin_acta=2  vencen=0  coverage=91%
   microbar(count=6, total=8, width=10) -> '████████░░'    len=10
   thumbnail lit-dot string (8 cells)   -> '●●●·●●●·'      lit=6
   linked nodes (Node.linked_map_id)    -> []              marker='⇄ 0'
   schema keys                          -> ['D','O','E','C','N']
map='nomina'    (created by MapStore.create_seed, no schema)
   total=3  con_acta=0  sin_acta=3  vencen=0  coverage=0%
   microbar(count=0, total=3, width=10) -> '░░░░░░░░░░'    len=10
   thumbnail lit-dot string (3 cells)   -> '···'           lit=0
   linked nodes                         -> []              marker='⇄ 0'
   schema keys                          -> []
```

Symbols confirmed on disk: `darkside.microbar` at `mapper/darkside.py:232` (signature
`microbar(count, total, width=10, fill=INK) -> Text`, output length always `width`);
`Node.linked_map_id()` at `mapper/model.py:57-60` reading `ficha.fields["map"]`;
`HomeScreen._map_metrics` at `mapper/app.py:377` ("acta" is `fields["D"]`, "vence" is
`fields["due"] == today.isoformat()`); `_empty_text` at `mapper/app.py:558`.

### A contradiction the probe surfaced: THREE coverage percentages, TWO answers

```
mapper/app.py:379         pct = int(100 * have / max(1, req))              -> 0   when req == 0
mapper/views/layered.py:119  pct = round(100*have/req) if req else 100     -> 100 when req == 0
mapper/widgets/rail.py:149   pct = round(have/req*100) if req else 100     -> 100 when req == 0
```

On a schema-less concept map the home hero says **0 %** while the canvas header and the rail both
say **100 %**, for the same graph, in the same session. Two of three agree; `app.py:379` is the
outlier. US-N13's coverage microbar would inherit whichever it copies. Settled in LLR-N13.1.3.

### The welcome seat is PARTLY SHIPPED

`_empty_text()` already paints the six-door copy (`c consult`, `p repo`, `n construct`,
`t template`, `i import`, `f factory`) and `on_mount` already displays `#home-empty` and hides the
recents table when the workspace holds no `.mmd`. The story reads as if the seat were new; it is
not. What US-N13 adds is the per-map card content, and the seat requirement is therefore written as
a **regression guard on shipped behaviour**, not as a new deliverable. Recorded so nobody counts a
pre-existing pass as this batch's contribution.

---

## M-13 · Text sinks and the coercion (risk A-7)

`darkside.plain` at `mapper/darkside.py:276`; `_CONTROL_MAP` at `:272` maps every C0 byte except
tab and newline to the replacement character. The home recents table currently uses
`rich.markup.escape` instead (`mapper/app.py:549` and the resume row at `:503`, `:505`) — that is
carry **B-03**'s visible-backslash family, ~20 legacy sites in `app.py`. Per risk A-7 those legacy
sites are **not** opportunistically fixed here; the requirement binds only the **new** sinks this
batch creates.

---

## M-14 · Provisional identifiers

Per the provisional-identifier scope rule (V-5), every `AT-NNN` / `TC-NNN` id, every test file path
and every `-k` selector named in `01-requirements.md` §3/§5 is **provisional until Phase 3** and is
reconciled against the real tree at Phase 4. The probes above are not provisional: they were
executed at draft time and their outputs are the pre-state the acceptances are written against.

---

## M-15 · A blank query lights the whole map today

Probe: `Graph.search_hits` (`mapper/model.py:169-184`) over a 6-node in-memory graph.

```
nodes: ['root', 'n1', 'n2', 'n3', 'n4', 'n5']
search_hits("")    -> ['root', 'n1', 'n2', 'n3', 'n4', 'n5']
search_hits("   ") -> ['root', 'n1', 'n2', 'n3', 'n4', 'n5']
count for the empty query: 6 of 6
```

`model.py:183` is `if q in hay`, and the empty string is a substring of every haystack. **Six of six
is the current behaviour**, so LLR-N07.3.3's threshold of 0 has a real, non-trivial pre-state.

---

## M-16 · The doubled help chord does not stack a second legend today

Probe: `App.run_test(size=(140,45))`, real `enter` to reach `MapScreen`, then the real
`question_mark` chord twice, reading `app.screen_stack`.

```
depth before      : 3   ['Screen', 'HomeScreen', 'MapScreen']
after 1 press     : 4   ['Screen', 'HomeScreen', 'MapScreen', 'HelpScreen']
after 2 presses   : 4   ['Screen', 'HomeScreen', 'MapScreen', 'HelpScreen']
```

The cause is on disk and is not accidental: `MODAL_SCOPES = (SCOPE_PALETTE, SCOPE_HELP)`
(`mapper/keymap.py:157`) excludes app-scope bindings from modal scopes, so
`bindings_for("help")` returns exactly `[('escape','dismiss_none'), ('q','dismiss_none')]` —
the help chord is not reachable from inside help. HLR-N16.3 pins this as intentional; its
non-trivial arm is the mutation that removes `SCOPE_HELP` from that tuple.

---

## M-17 · The legend is clipped — and M-11 could not see it

**This entry corrects M-11 and is the more important of the two.**

M-11 measured the legend by calling `.render()` on the `#help-content` widget, which returns the
**full** text, and reported `MATCH=True` at 27 rows for map scope. Re-measured against the
containers:

```
size=(118, 34)  scope='map'   bindings_for('map') = 27
   content rows emitted by _render_keymap()  : 27
   #help-content region                      : Region(x=21, y=6,  w=76, h=38)
   #help-dialog  region                      : Region(x=19, y=3,  w=80, h=28)
size=(140, 45)  scope='map'   bindings_for('map') = 27
   content rows emitted by _render_keymap()  : 27
   #help-content region                      : Region(x=32, y=11, w=76, h=38)
   #help-dialog  region                      : Region(x=30, y=8,  w=80, h=28)
```

The content needs **38** rows; `#help-dialog` is capped at **28** by `max-height: 28`
(`mapper/screens/help.py:39`); there is no scrolling container. **Ten rows are clipped, at every
terminal size**, including the smaller one where the clip is not caused by the terminal at all.

**A probe that reads past the clip cannot see the clip.** M-11's `MATCH=True` was true of the text
the widget emits and false of the panel the operator reads — which is exactly the error class
HLR-N16.1 exists to forbid, committed while drafting the requirement that forbids it. It was found
by reconciling against `01b-ux-decisions.md` §3.8, not by re-running the probe; re-running the probe
would have reproduced the same wrong answer every time. That is the practical argument for
cross-reading a sibling artifact rather than trusting one's own instrument.

Consequence, recorded in HLR-N16.1: the set-equality oracle asserts over **what the panel presents**,
never over `_render_keymap()`'s return value. `01b-ux-decisions.md` §3.8 budgets the full atlas
legend at **54 rows minimum against a 34-row reference terminal**, so the fix is a scrolling or
paged container, not a smaller font of words.
