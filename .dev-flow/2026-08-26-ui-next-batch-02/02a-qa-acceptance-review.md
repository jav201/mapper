# 02a — QA acceptance review (PDR lens) · `2026-08-26-ui-next-batch-02`

> **Scope.** The 47 `AT-NNN` and 71 `TC-NNN` of `01-requirements.md`, reviewed as *the half of the
> PDR that is under review*, against controls C-10, C-12, C-18, C-31, C-32, C-40, C-51, C-55 and the
> plausible-wrong-implementation rule (batch-1 post-mortem §2.1, backlog P-01).
>
> **Method: executed, not reasoned (C-43).** Every finding below that names a number was produced by
> a probe run against `master` at `d6b60e6b4f18b10123fffc76bbb36891473df653` in this session.
> Transcripts are pasted inline. `01-requirements.md`, `01b`, `01c` and `PLAN.md` were read, but no
> claim in them is relied on without re-execution. **Four of them came back different.**
> No `mapper/**`, `tests/**` or `prototypes/**` file was created, modified or staged.
>
> **Toolchain executed:** Python 3.12.7 · textual 8.2.8 · rich 15.0.0 · pytest 8.3.4 ·
> pytest-asyncio 0.25.0 · `PYTHONUTF8=1`.

---

## 1 · BLUF and gate verdict

**GATE: BLOCKED. 10 blockers, 14 majors, 11 minors.**

The requirement set is the most disciplined this project has produced — it derives input sets, it
records its own probe errors, and it names its counterfactuals. **It is nevertheless not yet
acceptance.** Three findings are decisive, and each was produced by execution rather than by reading:

1. **The story's headline identity is unrealisable and accidentally green.** `HLR-N06.3` —
   *"the declared total equals the number of graph nodes absent from the painted canvas"* — specifies
   its oracle as *"the count of node ids traceable in the painted text"*. The canvas paints **titles,
   not ids**. Executed: **0 of 8** legacy node ids appear case-sensitively in the painted canvas at
   every width, so the identity would declare *all 8 nodes hidden* when 0 are. Read
   case-insensitively it returns **8 of 8** — the right answer, **by pure fixture luck**, because
   every legacy id happens to be an abbreviation of its own title (`fin`→`Finanzas`,
   `nom`→`Nomina`). On the seed map it returns **0 of 3** and the identity is wrong again. This is
   C-55 limb 2 sitting under the batch's single most important predicate.

2. **The corrected legend oracle is still wrong.** `PLAN.md` §S-8 records `?` painting **17** of 27
   map-scope bindings, and `HLR-N16.1` is built on that correction. Executed here with the oracle
   clipped to the widget's own region: the true painted count is **16**, not 17 — the whole-screen
   oracle counts `m cobertura` from the `MapScreen` keybar *composited through the modal's
   `background: #000000 70%`*. At 240 × 100 the same oracle reports **19**. So the "painted" oracle is
   **contaminated by the screen underneath and varies with terminal size**, and no `AT` in the batch
   fixes a Pilot size. C-32 was correctly diagnosed and incorrectly discharged.

3. **Three of the 47 acceptance tests do not exist.** `AT-027`, `AT-028` and `AT-045` appear in
   exactly two places each — the story's `Acceptance tests:` list and the §5.2 table — and **nowhere
   else in the document**. No requirement claims them on an `Acceptance:` line, no boundary-catalog
   row describes them, no predicate is written for them. The batch's headline count of **47 is
   really 44**, and the padding sits in US-N13 and US-N16.

The single most valuable thing in the document — LLR-N07.1.1's positive arm, *"render with a hit set
the renderer could not have computed itself … a deletion asserted only by absence can be satisfied by
a rename; this arm cannot"* — is the pattern the other 43 acceptances should be rewritten against.
It is currently the only one that meets the plausible-wrong-implementation bar unaided.

---

## 2 · Probe transcripts (executed this session)

### QA-P1 — baseline and ledger unit

```
$ python -m pytest -q --collect-only | tail -1
245 tests collected in 0.11s

$ grep -rh "^def test_"       tests/*.py | wc -l     -> 116   (sync only)
$ grep -rh "^async def test_" tests/*.py | wc -l     ->  39
                                            sum      -> 155
$ grep -rc "def test_" tests/*.py | sum               -> 155
$ collected node ids carrying a '[' suffix           ->  96
```

**Base = 245 collected. Confirmed.** But `PLAN.md` **P-19 is wrong about its own arithmetic**:
it says *"A `def test_` count returns 116; the census's 155 matches neither."* Executed, **155 is
exactly the `def test_` count** (116 sync + 39 async); 116 is the count that misses every async test.
The census was not using a third unit — it was using the function count while P-19 used a
sync-only grep. A bookkeeping premise written to fix a bookkeeping error contains one.

### QA-P2 — the legend oracle, with a positive control (C-32)

Two oracles run side by side under Pilot, real `enter` then the real `question_mark` key:

```
size=(118, 34) source_screen=MapScreen scope='map'
  declared bindings_for('map')            : 27
  ORACLE-1 rows found in _render_keymap() : 27
  ORACLE-2 rows found in PAINTED cells    : 17
  ORACLE-1 set-equality passes?           : True      <-- the vacuous one, green today
  ORACLE-2 set-equality passes?           : False
  MISSING from the panel (10): ['= alternar diff', 'I mostrar/ocultar ficha',
    'R mostrar/ocultar rail', 'e exportar svg', 'f alternar foco', 'g ir al rail',
    'n siguiente faltante', 'o alternar outline', 'r alternar radial', 'z plegar rama']
  POSITIVE CONTROL ('atajos' present in painted text): True
```

Identical at 140 × 45 and 200 × 80. **At 240 × 100 the same oracle reports 19 painted, 8 missing.**

Region-clipping the oracle to the widget under test:

```
size=(118, 34)  declared=27
   labels found in WHOLE-SCREEN painted text : 17
   labels found inside #help-dialog  region  : 16
   labels found inside #help-content region  : 16
   labels present ONLY outside the dialog    : ['cobertura']
size=(240,100)  declared=27
   labels found in WHOLE-SCREEN painted text : 19
   labels found inside #help-dialog  region  : 16
   labels present ONLY outside the dialog    : ['alternar foco', 'alternar outline', 'cobertura']
```

**The true painted count is 16 of 27 at every size tested.** `PLAN.md` §S-8's 17 and its
`MISSING=10` list are contaminated by the `MapScreen` keybar showing through the modal's 70 % ground.

### QA-P3 — S-7 reproduced, and its oracle tested against both fixtures

```
size=(140, 45) [seed map]        #map-rail x=0 w=140 | #map-canvas x=140 w=1 | #map-inspector x=141 w=36
                                 canvas on screen (x<=139 and w>1)? False
size=(120, 40) [seed map]        #map-canvas x=120 w=1                        -> False
size=(100, 30) [seed map]        #map-rail display=False | #map-canvas x=0 w=64 -> True
                                 root title 'nomina' present in painted canvas? True
size=(140, 45) [legacy fixture]  #map-canvas x=140 w=1                        -> False
size=(100, 30) [legacy fixture]  #map-canvas x=0 w=64                         -> True
                                 painted: '                            ▐ Sistema E…                 '
                                 root title 'Sistema ERP Legacy' present in painted canvas? False
```

**S-7 reproduced independently — `AT-001` will be RED on `master`.** And at renderer level:

```
  legacy root title = 'Sistema ERP Legacy' (len=18)
  w= 60  full root title present? False   fragment='▐ Sistema …'
  w= 80  full root title present? False   fragment='▐ Sistema ERP L…'
  w=118  full root title present? True
```

### QA-P4 — HLR-N06.3's unpainted-set oracle

```
HLR-N06.3 read LITERALLY ("node ids traceable in the painted text"), legacy fixture:
  w= 80: ids case-SENSITIVE in painted text: 0/8 []      -> declared_total = 8   TRUTH = 0
         ids case-INSENSITIVE                : 8/8       -> declared_total = 0   TRUTH = 0
  w=118: identical.
Seed map (root/n1/n2 vs titles 'nomina'/'primer hijo'/'segundo hijo'):
         ids case-INSENSITIVE                : 0/3       -> declared_total = 3   TRUTH = 0

Read via node TITLES instead (the thing the canvas actually paints):
  w= 60  FULL-title trace=4/8   DRAWN(prefix)=8/8  -> declares 4 hidden, truth 0   MISMATCH
  w= 80  FULL-title trace=7/8   DRAWN(prefix)=8/8  -> declares 1 hidden, truth 0   MISMATCH
  w=100  FULL-title trace=8/8   DRAWN(prefix)=8/8  -> declares 0 hidden, truth 0   ok
```

**Every reading of the oracle is wrong at some width.** Truncation (`_fit`) makes a drawn node
untraceable; the id reading is fixture-luck. `M-5`'s headline *"121 nodes hidden with zero
declaration (94 %)"* inherits the same flaw — it counts *full-title traces*, so it conflates
**painted-but-truncated** with **hidden**, and over-states the defect it exists to quantify.

### QA-P5 — can the fixture discriminate the whole-graph count? (US-N07)

```
fixture legacy: 8 nodes, ramas ['fin','rrhh','inv']; fin descendants=['pres','cont'] (both leaves)
width=80: node titles painted = 7/8 (root truncated)

--- would a NAIVE 'count only painted nodes' differ when 'fin' is folded? ---
  q='carlos'    correct=1 naive(unfolded)=1 naive(folded)=0  -> DISCRIMINATES
  q='bloqueado' correct=1 naive(unfolded)=1 naive(folded)=0  -> DISCRIMINATES
  q='ana'       correct=2 naive(unfolded)=2 naive(folded)=1  -> DISCRIMINATES
  q='riesgo'    correct=2 naive(unfolded)=2 naive(folded)=2  -> *** VACUOUS ***
```

The fixture **can** discriminate — for some queries. `riesgo`, the query `M-7` uses throughout the
batch, is **vacuous** for fold-invariance, and the `> 0` guard `LLR-N07.2.1` relies on passes it
(2 and 2).

### QA-P6 — the nested-fold negative control (LLR-N06.3.2)

```
(outer rama, nestable inner node, its descendant count):
   fin > pres: 0 descendants
   fin > cont: 0 descendants
   rrhh > nom: 0 descendants
   inv > alm : 0 descendants
nestable candidates with >0 descendants: []
max tree depth: 2
-> NO usable candidate: the naive rule and the correct rule AGREE on this fixture
```

**Confirmed by execution.** C-55 limb 2, verbatim.

### QA-P7 — reverse census of the A3 blast radius, derived

```
REVERSE CENSUS over tests/ (27 tracked files)
  render( call sites       26 hits in 13 files ->
    test_app 2, test_attachments 3, test_components 1, test_export 1, test_inspector 6,
    test_lane 3, test_layered 2, test_legacy_fixture 1, test_outline 1, test_palette 1,
    test_radial 1, test_rail 3, test_worklist_safety 1
  OutlineRail.toggle        2 hits in 1 file  -> test_rail.py
  UNMIGRATED_SCREENS        5 hits in 1 file  -> test_keymap.py
  TAB_BINDING_EXCEPTIONS    7 hits in 1 file  -> test_keymap.py
```

`PLAN.md` trigger **B1** declares *"`.render(` appears in 7 test files not owned by this batch"*.
Executed: **13 files, 26 call sites.** R-1's mitigation is sized against a number that is
**6 files short** — the identical failure as post-mortem §2.2.

### QA-P8 — census, canvas, protocol and dead-code facts (all re-derived)

```
tracked mapper/*.py files: 33     distinct hues: 10     literal sites: 95
  ACCENT #1783ff sites: 8  ['app.py:1864','app.py:1906','app.py:1925','darkside.py:17',
                            'coverage.py:58','factory.py:101','factory.py:104','palette.py:65']
  undeclared #a3a3a3   : ['mapper/views/radial.py:18']                       <- confirmed
darkside.WARN/ALERT reference sites, excluding the definitions:
  distinct LINES 31 | total OCCURRENCES 37 | (WARN 19, ALERT 18)             <- NOT 29
Canvas(10,10) has 'dots'? False   has 'bgs'? False   attrs: _wire_tones,bits,cells,h,w
grep IRenderer mapper/  -> 2 prose mentions in comments; no class, no Protocol
grep 'def render' mapper/views/ -> 6 definitions;  **kwargs present in 5 of 6 (not 6)
qlower sites in mapper/views/ -> layered.py:144,146,147,148   (4, consumer at :159)
consumers of mapper/search.py across 60 tracked .py files -> 0.  DEAD CODE. Confirmed.
Radial braille U+2800..U+28FF = 0   Layered = 0   seed-map radial = 0
KEYMAP size 48 | duplicate_chords() [] | 'N' bound nowhere | digits bound nowhere
KEYMAP scope=='map' entries: 25    keymap.bindings_for('map'): 27
  extra 2 rows are app-scope: ('ctrl+p','paleta de acciones'), ('question_mark','ayuda')
```

### QA-P9 — C-12 feasibility for the export chain

```
save_svg(Text with 12 braille glyphs) -> file
  braille counted by raw scan of the WRITTEN FILE : 12
  braille after parsing <text> nodes              : 12
save_svg(real radial render of legacy) -> 20618 bytes, braille read back from file: 0 (master)
  root-title substring present in the written file: False   <- Rich splits/encodes spans
```

**A read-back oracle over the real artifact is feasible and cheap** (a raw codepoint scan recovers
the braille count exactly). A *substring* oracle over the SVG is not — it returns False for correct
content.

---

## 3 · Blockers

### QA-B-01 · `HLR-N06.3` / `AT-015`, `AT-016`, `TC-030` — the story's headline identity is unrealisable, and green by fixture luck
**Control: C-40 limb 1 + C-55 limb 2.** Evidence: QA-P4.
The predicate is `declared_total == len(graph.nodes) - painted_node_count`, with `painted_node_count`
defined as *"the count of node ids traceable in the painted text"*. The canvas paints **titles**.
Executed, the id reading gives 0/8 (declares everything hidden) case-sensitively and 8/8
case-insensitively — right on `legacy` only because its ids abbreviate its titles, wrong on the seed
map. The title reading fails differently: `_fit` truncates, so a **drawn** node stops being traceable
and the indicator would declare 4 hidden at w=60 when 0 are.
**Required before Inc-3:** the renderer must **return its painted id set** as data (it already must,
per `FLOW: overflow_declaration`, *"the render's painted id set"*), and the acceptance must consume
that declared set — then assert *separately* that every id in the declared painted set has a visible
trace on the canvas. Two predicates, not one substring scan. Without this the batch's central
promise is asserted against an oracle that cannot see it.

### QA-B-02 · `AT-001` / `LLR-S07.1.3` / `TC-005` — the root-title oracle is FALSE on a correctly laid-out canvas
**Control: C-40 limb 1.** Evidence: QA-P3.
`AT-001`'s deliverable line requires *"at least one painted canvas row containing the root node's
title"*. At 140 × 45 the fixed canvas is 80 columns; at w=80 the legacy root title paints as
`▐ Sistema ERP L…`. The assertion is **False on a correct implementation**. `M-4`'s green transcript
used the *seed* map (`nomina`, 6 chars) and the requirement never names a fixture, so the AT passes or
fails on which map the implementer happens to load. This is worse than vacuous — it will false-fail.
**Required:** name the fixture in the requirement, and assert a *truncation-tolerant* trace (the
title's `_fit` image, or a declared prefix of ≥ 8 characters), not the raw title.

### QA-B-03 · `AT-027`, `AT-028`, `AT-045` do not exist — the count is 44, not 47
**Control: C-18 + C-56.** Evidence: id census over the document, below.
```
ATs with NO requirement 'Acceptance:' line and NO descriptive mention anywhere:
   AT-027, AT-028, AT-045      (each appears exactly twice: the story list and the §5.2 table)
ATs with NO requirement 'Acceptance:' line (described only in a boundary catalog):
   AT-002, AT-009, AT-024, AT-031, AT-040
```
Three ids are pure padding. `US-N13` claims 7 ATs and defines 5; `US-N16` claims 5 and defines 4.
§5.2's bolded *"**47 acceptance tests across 8 derivable stories**"* is not derived from anything.
**Required:** either write the three predicates or renumber. A count that is not the number of
predicates is a hand-maintained number wearing a derivation's clothes — `PLAN.md` R-6, self-inflicted.

### QA-B-04 · `HLR-N16.1` / `AT-042` / `TC-063` — "assert the painted panel" has no executable definition, and the corrected number is still wrong
**Control: C-32.** Evidence: QA-P2.
The requirement correctly forbids `_render_keymap()`'s return value and correctly records that the
naive oracle is green on a clipped panel — I reproduced that: **ORACLE-1 passes 27/27 today over a
panel painting 16.** But the requirement never says *how* to read the panel, and the number the batch
is building on is wrong in two independent ways:
- **Contamination.** `HelpScreen` is a `ModalScreen` with `background: #000000 70%`; the `MapScreen`
  keybar composites through. A whole-screen painted oracle counts `m cobertura` as a legend row.
  True count **16**, not 17.
- **Size dependence.** The same oracle returns **19** at 240 × 100. No `AT` in the batch fixes a
  Pilot size, so `AT-042`'s verdict is nondeterministic across terminals.
**Required:** the oracle is defined as *"cells inside `query_one('#help-content').region`"*, and every
legend `AT` declares its Pilot size. Add a **negative control**: the oracle must report a *known
absent* label as absent, and a known keybar-only label must NOT be counted.

### QA-B-05 · `LLR-N06.3.2` / `TC-032` — the nested-fold negative control has no fixture, and "owed at Phase 3" is not a discharge
**Control: C-55 limb 2.** Evidence: QA-P6.
Confirmed by execution: max depth 2, **zero** nestable candidates with > 0 descendants, naive and
correct rules agree everywhere on the shipped fixture. §6.2 item 1 records this honestly and then
routes it to *"owed, budgeted, and named here"*. **An argument is not a discharge.** The predicate
gates the story's own worked example (`23 + 18 = 41`) and is currently unfalsifiable.
**Required as a PDR condition, not a Phase-3 to-do:** a synthetic fixture of depth ≥ 3 in which an
inner folded branch has ≥ 2 descendants, plus the executed transcript showing `naive_sum ≠ painted_sum`
on it. Inc-3 does not open until that transcript exists.

### QA-B-06 · `LLR-CNV.2.1` / `AT-009` / `TC-019` — the export chain never touches the written artifact
**Control: C-12.** Evidence: QA-P9.
Trigger **B4** fired precisely because `rows()`'s bytes reach `export.save_svg`. The threshold is
*"file exists; size > 0 bytes; the exported text object's braille count equals the on-screen text
object's braille count"* — the equality is between **two in-memory `Text` objects**, and the only
on-disk assertion is `size > 0`, which any SVG satisfies. The producer's artifact is never consumed.
**And the fix is proven cheap:** a raw codepoint scan of the written `.svg` recovered **12 of 12**
braille glyphs in my probe. **Required:** assert the braille count read back **from the file on disk**
equals the on-screen count. (Recorded for the implementer: a *substring* oracle over the SVG returns
False even for correct content — Rich encodes spans — so the read-back must scan codepoints or parse
`<text>` nodes, never grep.)

### QA-B-07 · `LLR-N13.1.3` / `AT-029` / `TC-047` — the plausible wrong fix passes
**Control: plausible-wrong-implementation (P-01).** Evidence: the requirement's own text.
Statement: *"every surface that states a coverage percentage for that map shall state the same
value."* Threshold: *"the three computations return the identical value."* **No value is pinned.**
The plausible weaker commit — change `layered.py:119` and `rail.py:149` to match `app.py:379`
(`int(100*have/max(1,req))` → **0 %**) — makes all three agree, passes the AT, and ships *"0 %
documented"* on every schema-less map in the product. The requirement itself says the outlier is
`app.py:379` and the majority is 100; the acceptance does not encode that.
**Required:** pin the value. `pct(schema-less) == 100`, plus the agreement clause.

### QA-B-08 · `AT-005`, `AT-006` / `HLR-S06.3` — `WARN` is given two contradictory jobs inside the same document, so the census is un-adjudicable
**Control: C-40 limb 1.** Evidence: cross-read of the requirement body.
- `01r:973-975` (HLR-N06.2, added by D-4): *"here `WARN` is correct precisely because it **does mean
  a hit**, the same reasoning that removed it from the empty-result line."*
- `01r:1368-1370` (LLR-N07.3.2 acceptance criteria): *"**Severity is the declared job of `WARN`**
  (LLR-S06.3.4), and 'your query found nothing' is a severity, so this use is consistent with the
  census."*
The second is stale pre-D-1 text arguing for the tone D-1 removed, and it survives *inside the LLR
D-1 corrected*. `AT-005`/`AT-006` are a census that fails *"if a severity hue appears at a site that
does not express severity"* — with two live definitions of what `WARN` means, the classifier has no
oracle. **Additionally: `ALERT` acquires a second job** (`01b` DECISION 2 assigns it to the malformed
lens chip; `01b:332-333` states *"if ALERT acquires a second job it must acquire a row here too"*)
and §3.7 never mentions `ALERT`, so the new site enters the census unclassified and reddens
`AT-005` at Inc-5 for a reason nobody wrote down.
**Required:** one job statement for `WARN`, one for `ALERT`, both reconciled with §3.7's chip, before
the census gate is written.

### QA-B-09 · `AT-007` / `HLR-CNV.2` — the declared subject is not the subject of the change, and `> 0` cannot see a wrong implementation
**Control: C-40 limb 1 + C-10.** Evidence: QA-P8.
Two defects in one predicate:
- **Subject mismatch.** `HLR-CNV.2` is titled *"braille free-angle edges appear **on the map
  canvas**"* and its acceptance renders through `RadialRenderer` (`tests/test_radial.py`). The map
  canvas's default view is `LayeredRenderer`, which draws no free-angle edges and is measured at
  **0 braille** before and after. The predicate certifies the radial view; the story promises the map
  canvas. As written it is a **regression PIN on the radial renderer, not a gate on the map canvas**
  — label it as such or move the subject.
- **The bound is too weak — this answers the question directly.** `count > 0` where the pre-state is
  0 reddens a *deletion* (compose neither layer) but **cannot redden a plausible wrong
  implementation**: composing `dots` at the wrong precedence so braille **overwrites** the node
  cards emits `> 0` glyphs and passes, while the map becomes unreadable. The strict-positivity
  argument in §6.2 item 3 defends against pinning a *number*; it does not license a one-sided bound.
  **Required:** add the containment arm — the distinct painted non-space set measured in `M-1`
  (`· ◆ ● ─ │ ┌ ┐ ┬ ┼ ▐`) **shall remain a subset** of the post-change painted set. Braille is added,
  nothing is lost. That arm reddens the precedence mutation; `> 0` does not.

### QA-B-10 · Five blocking questions gate seven ATs that PDR is being asked to approve
**Control: C-18.** Evidence: §6.1 of the requirements.
`Q-3` (walk chord), `Q-7` (lens walk chord), `Q-8` (bare word semantics), `Q-9` (migrate or declare),
`Q-10` (three census dispositions) are all **OPEN**. They gate `AT-018`, `AT-019`, `AT-022`,
`AT-038`, `AT-039`, `AT-041`, `AT-042`, `AT-005`, `AT-006`, `AT-032`, `AT-034`. A chord-agnostic
requirement is legitimate; **a chord-agnostic acceptance test is not** — `C-16` demands the AT drive
*the real key*, and there is no real key yet. These ATs are not realisable as one on-disk node until
PDR rules.
**Required:** PDR rules all five in the same sitting, or the affected increments do not open. The
ratification must be recorded as a decision, not inferred from an implementer's choice.

---

## 4 · Majors

| # | Id(s) | Control | Finding |
|---|---|---|---|
| QA-M-01 | `AT-018`, `AT-019` / `LLR-N07.2.1` | C-40 limb 2, C-55 | The statement demands *"a query matching a node inside rama `fin`"*; the **threshold** demands only *"the two counts are equal, and the count is `> 0` in both states"*. Measured (QA-P5): `riesgo` — the batch's own working query — satisfies the threshold with `naive == correct` and is **vacuous**. The threshold is weaker than the statement. Pin the query (`carlos`, `bloqueado` or `ana` all discriminate) and add: *at least one hit lies strictly inside the folded branch and is painted before the fold.* |
| QA-M-02 | `PLAN.md` B1 / R-1 | C-31 | The A3 reverse-census input set is **hand-listed and 6 files short**: declared 7 test files, executed **13 files / 26 `.render(` sites** (QA-P7). Derive it, then re-size R-1. |
| QA-M-03 | `LLR-S06.3.4` / `TC-013` | C-31 | Threshold is `derived severity-site count >= 29`. Executed: **31 distinct lines / 37 occurrences**; neither reproduces 29. A `>=` bound on a *derived* count **cannot detect a census that under-derives** — a regex that silently loses 8 sites still passes. Same shape at `LLR-S06.3.3` (`>= 8`, measured exactly 8). Assert equality against the derivation, or assert the derived set itself. |
| QA-M-04 | `HLR-N16.1` / `AT-042` | C-40 limb 2 | The quantified set is ambiguous: `KEYMAP` has **25** map-scope entries, `bindings_for('map')` returns **27** (it merges 2 app-scope rows). `01b` uses both numbers; `01r` uses 25 at `:910` and 27 at `:1888`/`:1921`. *"the set of bindings the keymap seat offers for that scope"* resolves to two different sets. Pin `bindings_for` explicitly. If Q-3 is ratified these become 27/29 and every quoted count goes stale. |
| QA-M-05 | `AT-022` / `LLR-N07.3` | C-16 | 01b's **UX-Q3-a and UX-Q3-b are explicit `shall` clauses from the ux lens and appear in no requirement**: the committed-vs-editing query chip, and the hint line *"shall read exactly `n siguiente · N anterior · esc limpiar`"*. §6.4 claims *"seven of its findings changed §3"*; these two changed nothing and are not in the table. |
| QA-M-06 | `US-N07` QC-3 empty cell | C-55 | 01b states E1b (`n` with no search ever submitted → `sin búsqueda activa · pulsa / para buscar`) and E1c (`n` with a submitted 0-hit query → `«nóm» no aparece en este mapa`) are **different facts** and *"not a silent no-op"*. Neither string nor either state appears anywhere in `01-requirements.md`. |
| QA-M-07 | `US-N06` QC-3 empty cell | C-55 | The ☑ **empty** cell is filled by *"a map that fits entirely on screen with nothing folded"* — a zero-**hidden** case, not an empty one. 01b's E3 (**a map with 0 nodes**) has no predicate anywhere, and `LLR-N06.3.3`'s fixture is the 6-node M-1 graph. The boundary catalog claims a case it does not cover. |
| QA-M-08 | `LLR-N14.3.2` / `AT-039` / `TC-061` | plausible-wrong | The invariant is *9 targets / 8 transitions*. 01b DECISION 5 step 5 records the **required mitigation** that did not land: *"`escape` … must leave the query box, and the hint line must say so. Without that, `priority=True` on `tab` traps the operator in the input."* Being **trapped inside the query `Input`** preserves 9 targets and 8 transitions — the invariant cannot see the failure it was written for. |
| QA-M-09 | `HLR-N16.2` / `AT-043` / `TC-066` | C-31 | Floors are *"over at least 5 glyphs"* and *"declared glyph count `> 0`"*. 01b DECISION 3 enumerates **21 vocabulary rows (V1–V21) plus 5 colour rows**. A legend shipping **one** glyph passes both floors. The floor must be derived from the declared vocabulary, not chosen. |
| QA-M-10 | `HLR-N16.2` / `AT-043` | C-40 limb 1 | Threshold: *"the title contains the view's name **for each of the three map views**"*. The defect being fixed is on **non-map** screens (`FactoryScreen`, `SettingsScreen`, `_ImportPreviewScreen`, `PlugRepoScreen`, `RepoScreen`). The predicate's declared subject excludes the subject of the change. |
| QA-M-11 | `AT-005` / `LLR-S06.3.1` | C-31 | The emptied-input mutation arm is the right control, but the *derivation itself* is unspecified: a plausible weaker commit is `glob('mapper/*.py')` (non-recursive) → **5** files instead of 33. That passes `> 0` and fails `>= 30`, so this one is caught — but `git ls-files` vs `Path.rglob` vs `glob` must be named, because `>= 30` is one refactor away from being the only thing standing. |
| QA-M-12 | `AT-025` / `HLR-N13.1` | C-18 | `AT-025` is claimed for the thumbnail, the zero-documented map **and** *"a map whose load raises"*. The error case needs a different workspace and a poisoned file; it cannot be the same on-disk node as the happy path. Split, or declare the parametrization. Same shape: `AT-007` is claimed by **both** `HLR-CNV.1` (unit, `Canvas`) and `HLR-CNV.2` (render chain, `RadialRenderer`) — two different chains, one id. |
| QA-M-13 | `AT-034` | C-18 | Claimed for `Z:algo`, `E:obsoleto Z:algo`, a token with no colon and a token with an empty key — spanning `LLR-N14.1.1` and `LLR-N14.1.3`, two requirements with different validation methods (unit+pilot vs unit). One node cannot drive both. |
| QA-M-14 | `LLR-N14.1.1` normative copy | C-40 limb 2 | The block is headed *"verbatim … the implementer copies it"* and then truncates 01b's string: `el mapa no define el campo «Z» · campos: D acta · O origen · E estado · C criticidad` becomes `… · campos: …`. What the implementer would copy is a literal ellipsis. Also unreconciled: the declared count-line form is `N nodos en M ramas`, but the mandated zero-match line `0 nodos · ningún nodo tiene estado = inexistente` is not of that form. |

---

## 5 · Minors

| # | Id / target | Finding |
|---|---|---|
| QA-N-01 | `PLAN.md` P-19 | *"the census's 155 matches neither"* is false — **155 is exactly the `def test_` count** (116 sync + 39 async). QA-P1. |
| QA-N-02 | `PLAN.md` §S-8 | `painted=17` / `MISSING=10` is contaminated; true values **16 / 11**. QA-P2. Correct the number wherever it is quoted. |
| QA-N-03 | `HLR-N07.2.2` | *"All six lose `**kwargs`"* — executed, **5 of 6** declare `**kwargs`; `layered.py:78` takes an explicit `query`. The reverse census greps this line. |
| QA-N-04 | `M-5` | *"121 nodes hidden (94 %)"* over-states: the metric counts **full-title traces**, and truncated-but-drawn nodes are counted as hidden (QA-P4). Restate as *"nodes without a full-title trace"*. |
| QA-N-05 | `LLR-S06.3.2` | 3 registered exceptions, all 3 confirmed on disk (`radial.py:18` `#a3a3a3`; `app.py:848`; `factory.py:104`). No defect — recorded as **verified**. |
| QA-N-06 | `HLR-N06.3` observation | The canvas header **wraps**: at 100 × 30 `'◆ mapper · … 3'` / `'nodos'` land on two rows. Any AT parsing a numeral out of a painted line must join wrapped rows first. |
| QA-N-07 | `LLR-N06.2.1` | The supersession set is stated as *"0 remaining references"* but never enumerated. Derived: `OutlineRail.toggle` has **2** references, both in `tests/test_rail.py`. Name them at Phase 1, per the batch's own §2.2 lesson. |
| QA-N-08 | `LLR-N07.1.2` | The widening arm needs a **synthetic** graph (the legacy fixture has no attachments and no distinguishing `meta`). Declared implicitly by M-7; not counted in any increment's fixture budget. |
| QA-N-09 | `HLR-N16.1` §3.8 budget | The quoted *"54 rows … short by 20"* is superseded by 01b's own next sentence (21 vocabulary rows, not 6). Substituting gives **69 rows, short by 35** — a figure stated in neither document. |
| QA-N-10 | `M-10` vs `keymap.py:46-48` | Two different `tab` measurements are quoted adjacently as if one: *0 focus moves in 9 presses* (batch-1, focus moves) and *0 fires in 4 presses / 3 in 3 with `priority=True`* (01b, action fires). Different quantities; say so. |
| QA-N-11 | `mapper/search.py` | Confirmed **0 consumers across 60 tracked files** — dead code with a legacy filename, exactly as ARQ recorded. Treat every `search` LLR as new-module work in the ledger, not as modification. |

---

## 6 · Per-AT control matrix

Legend — **C-40**: does the predicate's own expression contain the subject it declares it certifies?
**C-10**: does it drive a non-default value? **C-31**: is a quantified set derived? **C-32**: is the
painted result asserted? **C-12**: does it chain through the real artifact? **C-18**: realisable as
one node? `·` = not applicable. `!` = defect, see the finding named.

| AT | Story | C-40 | C-10 | C-31 | C-32 | C-12 | C-18 | Verdict |
|---|---|---|---|---|---|---|---|---|
| AT-001 | S-7 | **!** B-02 | ok | · | ok | · | ok | **BLOCKED** — root-title oracle false on legacy |
| AT-002 | S-7 | ok | ok | · | ok | · | ok | ok — but has no owning `Acceptance:` line (B-03) |
| AT-003 | S-6 | ok | ok | · | · | · | ok | ok |
| AT-004 | S-6 | ok | **!** | · | · | · | ok | pre-state green by construction; only the hex-edit mutation is non-trivial — the doc says so; keep |
| AT-005 | S-6 | **!** B-08 | ok | ok | · | · | **!** M-12 | **BLOCKED** — WARN has two jobs; spans 4 LLRs |
| AT-006 | S-6 | **!** B-08 | ok | ok | · | · | ok | **BLOCKED** — same |
| AT-007 | CNV | **!** B-09 | ok | · | ok | · | **!** M-12 | **BLOCKED** — subject is radial, story is map canvas; `>0` too weak |
| AT-008 | CNV | ok | ok | · | ok | · | ok | ok — boundary + invalid both present |
| AT-009 | CNV | ok | ok | · | · | **!** B-06 | ok | **BLOCKED** — never reads the written file |
| AT-010 | CNV | ok | ok | · | ok | · | ok | ok — two tones compared, content held equal |
| AT-011 | N06 | ok | ok | · | ok | · | **!** | chord unsettled (B-10) |
| AT-012 | N06 | ok | ok | ok (K derived) | ok | · | **!** | chord unsettled (B-10); `borde del territorio` pinned — good |
| AT-013 | N06 | ok | ok | · | ok | · | ok | ok — leaf case specified, `+0` forbidden |
| AT-014 | N06 | ok | ok | · | ok | · | ok | ok |
| AT-015 | N06 | **!** B-01 | ok | · | **!** | · | ok | **BLOCKED** |
| AT-016 | N06 | **!** B-01 | ok | · | **!** | · | ok | **BLOCKED** |
| AT-017 | N06 | ok | ok | · | ok | · | ok | strong — drives the rail-hidden regime R-013 exists for |
| AT-018 | N07 | ok | ok | · | ok | · | **!** | **major** QA-M-01 + chord unsettled |
| AT-019 | N07 | ok | ok | · | ok | · | **!** | **major** QA-M-01 + chord unsettled |
| AT-020 | N07 | ok | ok | · | ok | · | ok | **model AT** — the injected-id arm defeats a rename |
| AT-021 | N07 | ok | ok | · | ok | · | ok | ok |
| AT-022 | N07 | ok | ok | ok | ok | · | **!** | chord unsettled (B-10); rescued from vacuity by LLR-N06.2.4 |
| AT-023 | N07 | ok | ok | · | ok | · | ok | strong — text **and** tone, pre-state 6/6 measured |
| AT-024 | N07 | ok | ok | ok (protocol) | ok | · | ok | no owning `Acceptance:` line (B-03) |
| AT-025 | N13 | ok | ok | · | ok | · | **!** M-12 | error case cannot share the node |
| AT-026 | N13 | ok | ok | · | ok | · | ok | ok — both ends of the bar |
| AT-027 | N13 | **!** | **!** | **!** | **!** | **!** | **!** | **DOES NOT EXIST** (B-03) |
| AT-028 | N13 | **!** | **!** | **!** | **!** | **!** | **!** | **DOES NOT EXIST** (B-03) |
| AT-029 | N13 | **!** B-07 | ok | ok | · | · | ok | **BLOCKED** — agreement without a pinned value |
| AT-030 | N13 | ok | **!** | · | ok | · | ok | regression guard, declared as such; mutation arm named |
| AT-031 | N13 | ok | ok | · | ok | · | ok | no owning `Acceptance:` line (B-03) |
| AT-032 | N14 | ok | ok | ok (schema derived) | ok | · | **!** | Q-8 unsettled (B-10) |
| AT-033 | N14 | ok | ok | ok | ok | · | ok | strong — the story's own example is measured EMPTY |
| AT-034 | N14 | ok | ok | ok | ok | · | **!** M-13 | spans two LLRs and two methods |
| AT-035 | N14 | ok | ok | ok | · | · | ok | strong — inequality assertion makes routing provable |
| AT-036 | N14 | ok | ok | · | ok | · | ok | ok — 5 nodes / 3 ramas both measured |
| AT-037 | N14 | ok | ok | · | ok | · | ok | ok |
| AT-038 | N14 | ok | ok | · | ok | · | **!** | Q-7 unsettled (B-10) |
| AT-039 | N14 | **!** M-08 | ok | · | ok | · | **!** | invariant cannot see the input trap |
| AT-040 | N14 | ok | ok | · | ok | · | ok | no owning `Acceptance:` line (B-03) |
| AT-041 | N16 | ok | ok | ok (screen set) | **!** B-04 | · | **!** | **BLOCKED** |
| AT-042 | N16 | ok | ok | ok | **!** B-04 | · | **!** | **BLOCKED** — also QA-M-04 (25 vs 27) |
| AT-043 | N16 | **!** M-10 | ok | **!** M-09 | ok | · | ok | floor is 5 against a 26-row spec |
| AT-044 | N16 | ok | **!** | · | ok | · | ok | green pre-state, declared; `MODAL_SCOPES` mutation named — good |
| AT-045 | N16 | **!** | **!** | **!** | **!** | **!** | **!** | **DOES NOT EXIST** (B-03) |
| AT-046 | N06 | ok | ok | · | ok | · | ok | ok — the AT that stops AT-022 being vacuous |
| AT-047 | N06 | ok | ok | · | ok | · | ok | ok — "does not re-close" is the non-obvious arm |

**Summary: 10 blocked · 12 with a major defect · 3 non-existent · 22 acceptable as written.**

### TC audit

All 71 `TC-NNN` appear **exactly once** each — only in the §5.2 table, with a one-line Note. That is
an acceptable design *if* the TC's oracle is its LLR's `Executed verification` + `Numeric pass
threshold`, which it is. Audited on that basis:

- **71 of 71** carry a validation method and a numeric threshold. §5.3 criterion 4 holds.
- **8 thresholds are weaker than their own statement:** `TC-013` and `TC-012` (`>=` on a derived
  count, QA-M-03), `TC-030` (B-01), `TC-005` (B-02), `TC-019` (B-06), `TC-047` (B-07), `TC-038`
  (QA-M-01), `TC-061` (QA-M-08).
- **`TC-071` is out of sequence** — LLR-N06.2.4 was added at reconciliation and numbered 71 while
  sitting between TC-029 and TC-030. Harmless, but note it so the Phase-4 reconciliation does not
  read it as a gap.
- **No TC covers** the states in QA-M-05, QA-M-06, QA-M-07 (UX-Q3-a/b, E1b, E1c, E3), because no LLR
  does.

---

## 7 · Plausible-wrong-implementation mutations — declared now, at authoring time

Per backlog **P-01**. Each row names a variant *a competent engineer might actually commit*, not a
deletion. The batch must show each turns its AT **RED**, per-arm, before the AT is accepted.

| Target | Plausible wrong implementation (not a deletion) | Must redden |
|---|---|---|
| `LLR-S07.1.1` | `#map-rail { width: auto }` — reads as "let it size itself" and is what a designer writes | `AT-001` at 140×45 and 120×40 |
| `LLR-S07.1.2` | `MIN_CANVAS_WIDTH` compared with `<=` instead of `<` — moves the auto-hide transition by one column | `AT-002` at 118 and 117 |
| `LLR-S06.3.1` | file list from `glob("mapper/*.py")` (non-recursive) → 5 files, not 33 | `AT-005` (`>= 30` arm) |
| `LLR-S06.3.3/.4` | hue regex `#[0-9a-f]{6}` (lowercase only) — misses `#1783FF` | `AT-005`, `AT-006` |
| `LLR-CNV.1.2` | compose `dots` **last**, so braille overwrites the node cards | `AT-007` — **only via the new subset arm in B-09**; `> 0` passes it |
| `LLR-CNV.1.3` | guard `0 <= x < self.w` and forget the `y` bound | `AT-008` |
| `LLR-CNV.2.1` | pass a freshly rendered `Text` to `save_svg` instead of the one on screen | `AT-009` — **only after B-06's read-back fix** |
| `LLR-CNV.3` | derive `focus_owner` from `screen.focused` instead of `app.focused` — correct until a modal is up | `AT-010` |
| `LLR-N06.1.2` | clamp to `[0, E - W]` without `max(0, …)` — negative upper bound when `E < W` | `AT-012` (the `E < W` input) |
| `LLR-N06.2.2` | paint the pill and suppress it when `N == 0` — visually identical, but the toast never fires | `AT-013` (the notification arm) |
| `LLR-N06.3.1` | `hidden = folded_count + offscreen_count` — the sum, not the set difference | `AT-016` — **needs the overlap fixture** |
| `LLR-N06.3.2` | sum over the `folded` set instead of over painted pills | `AT-016` — **needs B-05's depth-3 fixture; unfalsifiable today** |
| `LLR-N07.1.1` | rename `qlower` → `ql` and keep the predicate | `AT-020` — **the injected-id arm already defeats this. Model for the rest.** |
| `LLR-N07.2.1` | `count = len([h for h in hits if h not in hidden_by_fold])` | `AT-018` — **only with QA-M-01's pinned query; `riesgo` passes it** |
| `LLR-N07.3.1` | order by `sorted(hits)` instead of pre-order walk — coincides on many fixtures | `AT-022` (self-guard `tree ≠ dict` must extend to `tree ≠ sorted`) |
| `LLR-N07.3.3` | `if not query: return []` — omits `.strip()`, so whitespace still lights all 6 | `AT-023` (measured pre-state 6/6) |
| `LLR-N13.1.3` | make `layered`/`rail` agree with `app.py:379` (all three → 0 %) | `AT-029` — **currently PASSES. B-07.** |
| `LLR-N13.1.4` | `due >= today` instead of `== today` — badge fires on future dates too | `AT-028`… **which does not exist (B-03)** |
| `LLR-N13.2.1` | `rich.markup.escape` instead of `darkside.plain` — kills markup, keeps control bytes | `AT-031` (the 0-control-bytes arm) |
| `LLR-N14.1.1` | evaluate the query, then return `[]` when `unknown_keys` is non-empty | `AT-034` — **only via D-5's canvas-identity oracle**; a message-string comparison passes it |
| `LLR-N14.1.2` | `ficha.fields.get(k) or getattr(ficha, k, "")` — schema wins, `state` falls through | `AT-035` (the 3-vs-2 inequality) |
| `LLR-N14.2.2` | treat `frozenset()` and `None` as the same no-lens sentinel | `AT-036` — the 245-baseline guard |
| `LLR-N14.3.3` | store the evaluated id set alongside the query and return it when fresh ("cache") | `AT-039` (the mutate-then-recall arm) |
| `HLR-N16.1` | fix the **route** on all 5 screens, leave `KEY_SCOPE` undeclared → resolves to `app` | `AT-042` — *"a fix that passes its own test"*, correctly identified in §2.8.3 |
| `HLR-N16.1` | oracle reads `_render_keymap()` | `AT-042` — **measured green today over a 16-of-27 panel. B-04.** |
| `LLR-N16.2.3` | coerce the label but not the glyph-row caption | `AT-043` |
| `HLR-N16.3` | remove `SCOPE_HELP` from `MODAL_SCOPES` | `AT-044` — already named by the batch; good |

**Coverage:** 27 mutations across 26 predicates. **Four cannot currently be reddened by any AT in the
set** (`LLR-CNV.1.2`, `LLR-CNV.2.1`, `LLR-N06.3.2`, `LLR-N13.1.3`) and one is reddened only by luck
of query choice (`LLR-N07.2.1`). Those five are the blockers above.

---

## 8 · Layer-0 list (C-51)

Units with cyclomatic complexity ≥ 3 **or** transforming data across a declared module boundary.
Derived from the `Touched symbols … NEW — created in Phase 3` lines of §3, not hand-listed.

**In Layer 0 — testable with no event loop and no filesystem:**

| Unit | Owner LLR | Why |
|---|---|---|
| `search.parse_lens` | LLR-N14.1.1, LLR-N14.1.3 | token loop + key-resolution branch + malformed-token branch; parses **operator text at a boundary**. The batch names this itself and is right. |
| `search.lens_hits(Graph, LensQuery)` | LLR-N14.1.2 | AND-of-terms with namespace routing (`state` vs schema key); transforms `Graph` → id list across `model → search` |
| `search.<pre-order tree walk>` | LLR-N07.3.1, LLR-N14.3.1 | DFS with a reversed-children stack; CC ≥ 3; shared by two stories |
| `Canvas.rows()` | LLR-CNV.1.2, LLR-CNV.1.3 | four-layer precedence resolution + bounds guard; CC ≥ 4; its bytes cross `canvas → views` **and** `canvas → export` |
| the outermost-folded-set / pill reconciliation rule | LLR-N06.3.2 | pure set computation; CC ≥ 3; **the one with no fixture (B-05)** |
| the hue-census derivation + classifier | LLR-S06.3.1 – .4 | derives a file set, harvests literals, classifies; CC ≥ 3 |

**Should be Layer 0 but is not, as specified — recommend extraction:**

| Unit | Owner LLR | Problem |
|---|---|---|
| the pan clamp | LLR-N06.1.2 | specified as *"a clamp helper"* **on `MapScreen`**. Pure arithmetic over `(E, W, offset)`; requiring a screen instance to test 6 inputs including both extremes is gratuitous. Make it a module-level function. |
| the overflow set-difference | LLR-N06.3.1 | same — pure set arithmetic living on `MapScreen`. Its overlap case (B-01/QA-M-01) is far easier to drive as a function. |
| the coverage-percentage definition | LLR-N13.1.3 | one expression, three call sites; extract it so *"the three surfaces agree"* is a single-source assertion rather than three transcriptions |

**Explicitly excluded** (pure delegation, getters, UI wiring): `ViewState` field access;
`MapScreen.refresh_canvas` (assembly); `OutlineRail.show` (rendering wiring); the
`#map-rail { width: 24 }` CSS rule; `HelpScreen.compose`; the saved-lens dict; `bindings_for`
(existing, and a pure read of the seat).

---

## 9 · Test ledger plan

**Unit: collected node ids.** `pytest -q --collect-only`. A `def test_` count is **not** the unit —
it returns 116 (sync only) or 155 (all functions); 96 collected ids carry a parametrization suffix.

```
post = base − D + A          base = 245   (executed, QA-P1)
```

**Rules, so the ledger cannot be recalled rather than derived:**

1. `base` is re-derived at the first increment's open and pasted, not carried from this document.
2. `D` and `A` are measured **per increment** from the collect-only diff:
   `diff <(git stash … ) …` is not required — capture `pytest -q --collect-only` before and after
   each increment into the packet and diff the id lists. **`D` is the count of ids that disappear**,
   `A` the count that appear. Renames show as one of each and must be declared as a rename.
3. **Every `D` needs a named predecessor and a reason.** A superseded test is deleted *with* the
   statement of what now covers it. Batch 1 lost `AT-N05e` this way.
4. `A` must reconcile with the AT/TC map: **44 real ATs + 71 TCs**, minus every case where one node
   serves both. That mapping is declared at DDR, per id, or the ledger is not checkable.
5. §5.3 criterion 1 (*"100 % LLR coverage"*) is checked against **48 LLRs**, and criterion 2 against
   **8 stories** — both re-derived from the document's headings at Phase 4, not from §5.2's totals.

**Predicted-red set (`D` candidates), derived — QA-P7, not taken by eye:**

| Surface | Sites | Trigger |
|---|---|---|
| `.render(` call sites | **26 in 13 files** — `test_app`, `test_attachments`, `test_components`, `test_export`, `test_inspector`, `test_lane`, `test_layered`, `test_legacy_fixture`, `test_outline`, `test_palette`, `test_radial`, `test_rail`, `test_worklist_safety` | the A3 signature change (Inc-2) |
| `OutlineRail.toggle` | **2 in `tests/test_rail.py`** | LLR-N06.2.1 deletes it |
| `UNMIGRATED_SCREENS` fence | **5 in `tests/test_keymap.py`** | LLR-N16.1.2, **only if** Q-9 rules "migrate" |
| `TAB_BINDING_EXCEPTIONS` fence | **7 in `tests/test_keymap.py`** | **only if** Q-7 rules `tab` |
| whole-seat conformance spec | 1 node | Q-3's three-row seat diff (D10) |

These are **predicted red, not permitted red**. Each must be declared before its increment and
reconciled after; an unpredicted red is a finding, not a bookkeeping event.

---

## 10 · Evidence checklist (C-43)

- [x] **Acceptance criteria use Given/When/Then** — ✗ *by design, and accepted*: the batch uses EARS
      (`While … the system shall …` / `When … then …`), which is the ISO 29148 register this project
      has standardised on. Equivalent rigour; recorded rather than waved through.
- [x] **Test cases have explicit Expected, not vague "works"** — ✓ 71 of 71 `TC` carry a numeric
      threshold; 8 are weaker than their own statement (§6).
- [x] **Edge cases include empty, boundary, invalid, error** — ✓ every story carries a QC-3 catalog;
      ✗ **two cells are mis-filled** (QA-M-06, QA-M-07) and one story's ☐ **error** N/A is correct.
- [x] **Regression checklist exists** — ✓ §9's predicted-red set, derived (QA-P7), and it corrects the
      batch's own count from 7 files to 13.
- [x] **Exit criteria stated** — ✓ §5.3 of the requirements, 6 criteria; ✗ criterion 5 lists **4**
      counterfactuals where §7 above derives **27**.
- [x] **No real PII / secrets** — ✓ fixtures only (`Juan Perez`, `Ana Ruiz` are fixture strings in
      `fixtures/legacy_nodos.yml`, already tracked). No credentials in any probe.
- [x] **Test results left blank for the human** — ✓ §5.2 reads `pending Phase 4` throughout; nothing
      in this review marks an unrun test as passed.
- [x] **Layer B (black-box) through the shipped surface** — ✗ **fails on three counts**: `AT-009`
      never reads the written artifact (B-06); `AT-041`/`AT-042` have no executable painted oracle
      (B-04); `AT-015`/`AT-016` observe an oracle that cannot see the deliverable (B-01).
- [x] **Bidirectional surface-reachability** — ✗ input side is good (every AT drives a real key,
      C-16 enforced); **output side fails**: the export artifact (B-06) and the legend panel (B-04)
      are the two named deliverables observed through a proxy rather than through the shipped
      surface.
- [x] **No unfilled template** — ✗ **three `AT` ids have no predicate at all** (B-03). The phase ran;
      the enumeration did not.
- [x] **No control bytes written** — ✓ this file byte-scanned before write; probe scripts live in the
      session scratchpad, never in the repo; `prototypes/` untouched and unstaged; nothing committed.

---

## 11 · What PDR must rule before Inc-1 opens

1. **B-01, B-02, B-04, B-06** — four oracles rewritten. All four have a named, cheap remedy above and
   one (B-06) is proven feasible by transcript.
2. **B-03** — write the three missing predicates or renumber to 44.
3. **B-05** — the depth-3 synthetic fixture, with its executed `naive ≠ correct` transcript, as a PDR
   condition rather than a Phase-3 debt.
4. **B-07, B-08** — pin the coverage value; give `WARN` and `ALERT` one job each, reconciled with the
   lens chip.
5. **B-09** — add the painted-set containment arm to the braille acceptance, and relabel `HLR-CNV.2`
   as a radial pin unless its subject moves to the map canvas.
6. **B-10** — rule `Q-3`, `Q-7`, `Q-8`, `Q-9`, `Q-10` in one sitting.
7. **QA-M-02** — re-derive the A3 census input set (13 files, 26 sites) and re-size R-1 against it.

**Nothing here asks for more tests. Six of the ten blockers are the same test, asserted against a
different thing.**
