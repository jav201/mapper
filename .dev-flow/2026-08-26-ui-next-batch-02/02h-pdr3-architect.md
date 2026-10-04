# 02h — architect lens, PDR iteration 3 (FINAL)

**Date:** 2026-08-27 · **Batch:** `2026-08-26-ui-next-batch-02`
**Base audited:** branch `docs/amendment-set-3` @ `94ad8d3` (tree clean, nothing mutated by this audit)
**Instrument:** my own pass-2 ledger `02c` — `P2-B1`–`P2-B6`, `P2-C1`–`P2-C8`. **Not** the §6.5
amendment table, which dropped conditions twice (RIDER-1).
**Evidence rule applied:** every status below carries a command + output, or a `file:line` on the
tree at `94ad8d3`. **No status rests on a citation of another document.**

---

## VERDICT — `approved with conditions`

**14 of 14 of my pass-2 conditions are DISCHARGED on executed evidence.** At pass 2 all fourteen were
LIVE and I rejected. The requirements lane did the work, and — audited against my ledger rather than
against its own amendment table — it holds up. I re-derived the four censuses that have historically
been wrong here (the A3 blast radius, the `rows()` consumer set, the supersession pin set, the
`AT`↔`TC` join) with an AST or an executed join, and all four reproduce.

The three new rulings `#D25` / `#D26` / `#D27` are each **sound**. Both routed edits **landed and are
correct.**

I raise **four new items**. All are document-lag defects with named one-edit fixes; none is a design
gap and none justifies stopping the batch. **C-53 is binding in both directions**: I will not convert
a lagging paragraph into a batch-stopper when the governing decision is landed and correct. But one
of them — `ARQ-3-C1` — must be fixed **before `Inc-3` opens**, because the normative body of the
requirements still contains the sentence *"`Inc-3` shall not open until the cap is ruled."*

---

## 1 · Condition-by-condition audit (task 1)

| id | Grade | Status | Executed evidence at `94ad8d3` |
|---|---|---|---|
| `P2-B1` | blocker | **DISCHARGED** | §5.4 (`01-requirements.md:5548`) states the cut **once**, with authority `#D5`. `grep -n "^### 3\."` → §3.6 header now `*(Inc-7 — §5.4)*` (`:2876`), §3.8 now `*(Inc-8 and Inc-9 — §5.4)*` (`:4062`). Both stale ARQ-7-cut headers gone. `Inc-6` **vacated, not renumbered** (`:5586`), with the renumbering and the reuse alternatives each rejected on stated grounds (`:5565-5578`). Residual `Inc-6` mentions at `:4032`, `:6460` are inside DEFERRED §3.7 / verbatim `#D6` quotation. |
| `P2-B2` | blocker | **DISCHARGED** | Re-derived: 56 distinct `AT` tokens; 5 not on any `**Acceptance:**` line. Each dispositioned: `AT-009` owned at `:1517`, `AT-031` owned at `:3340`; `AT-040` leaves with DEFERRED US-N14 (`:5275`, §3.7 deferral block); `AT-027`/`AT-028`/`AT-045` **DELETED** (`:5314`, A-07); `AT-048` **DEFERRED** by `#D24` (`:5303`). Zero live unowned. |
| `P2-B3` | blocker | **DISCHARGED** | The literal is struck: `01-requirements.md:4386` `~~"21 rows V1 through V21"~~`. `LLR-N16.2.1` (`:4351`) now carries a QUESTION / INSTRUMENT / MEASURED-AT derivation over distinct `(glyph, label, style)` triples with **cardinality deliberately not transcribed** (`:4378`). Fourth site landed: `01b-ux-decisions.md:373-388` carries the derived count and no literal. Independently counted `01b` DECISION 3: **23** `V` rows (`V1`–`V6`, `V4a`, `V4b`, `V7`–`V21`); `V4` (`01b:277`) and `V4a` (`:287`) are byte-identical → **22** distinct triples. "Correct 21 → 23" would indeed have been wrong twice. |
| `P2-B4` | blocker | **DISCHARGED** | AST over `mapper/**` + `tests/**`: `.collapsed`/`.toggle` attribute sites = **12**, of which 6 external — including the PRODUCTION site `mapper/app.py:1259` and the rail guard `tests/test_repair_depth.py:1055`. Both are now named in the requirement (`:1809`, `:1812`). Pin set re-derived by AST over `tests/test_repair_depth.py`: `MASTER_LEGACY_DIGESTS` **12** + `MASTER_RAIL_DIGESTS` **5** + `MASTER_FACTORY_TREE_DIGEST` **1** = **18**. `MASTER_RAIL_DIGESTS` — named in NO artifact at pass 2 — is now named at `:1829`, with a predicted-red clause and a one-at-a-time re-capture rule (`:1838`). |
| `P2-B5` | blocker | **DISCHARGED** | `grep -E "^#{4,5} \`?(HLR\|LLR)-COERCE"` → `HLR-COERCE` `:391`, `LLR-COERCE.1` `:537`, `LLR-COERCE.2` `:578`. Owning increments declared: `LLR-COERCE.1`→Inc-1, `LLR-COERCE.2`→Inc-3, `LLR-N06.2.5`→Inc-9 (`:424-426`). `TC-080` in the functional table (`:5398`). The `Acceptance:` line is an explicit **ruling** (`:427-431`), not an omission — the `AT`s stay on surface-specific LLRs. I accept that: an `AT` on a surfaceless control class would be a white-box claim in acceptance clothing. |
| `P2-B6` | blocker | **DISCHARGED** | `LLR-N06.2.5` (`:1873`) re-parented to `HLR-COERCE`, owning increment **Inc-9**, on a two-limb criterion that is shown to *discriminate* (applied to sibling `LLR-N06.2.3`, which correctly stays). §5.4 `:5590` gives Inc-9 `screens/factory.py` already, so the re-parent removes Inc-3's undeclared 5th-file breach at **zero** added files. The one unperformed clause (physically relocating the block) is recorded as a deliberate deviation at `:1905-1911` — presentational, and I ratify leaving it. |
| `P2-C1` | condition | **DISCHARGED** | AST `Call` nodes with `func.attr == "rows"` over `mapper/**`: **4 sites / 3 files**, all in `mapper/views/` (`lane.py:216`, `:299`, `layered.py:283`, `radial.py:253`). The IFC row (`:5016`) now lists exactly those three files; `export.py` moved to `transitive observers`; `outline.py` removed. `#D4`'s reversal condition — *"a consumer outside `mapper/views/` indexing `rows()`"* — is executed **still unmet, 0 sites**, so `#D4` is checkable again instead of self-contradicting. |
| `P2-C2` | condition | **DISCHARGED** | `C-D4c` is now a **clause**, not a finding: `:1242-1249`, "STANDING RE-RUN OBLIGATION — `AT-007` and `AT-009` are RE-RUN AFTER `Inc-2` … `Inc-2` does not close with either red", with a named weaker variant (`M-CNV.1-rerun`) that is reddened by `AT-009`'s on-disk threshold. |
| `P2-C3` | condition | **DISCHARGED — and I executed the join myself, not the claim of it.** | `#D15` discharged as a **derived join** (`:5415`) rather than a third hand table. I ran the join independently at `94ad8d3`: bind each `**Acceptance:**` line to its nearest `####`/`#####` heading, skip headings marked `SUPERSEDED`/`DEFERRED`, join to the functional table on requirement id. Result: **40 live `AT` ids with an owner, 69 requirements in the functional table, 0 live `AT` reaching no `TC`.** The join is TOTAL. The two known false positives (`AT-025b`, `AT-048`) are pre-recorded at `:5438` with the reason a naive scanner drops them. |
| `P2-C4` | condition | **DISCHARGED** | See §3.1 below — routed edit verified. |
| `P2-C5` | condition | **DISCHARGED, and it defuses the `A-11` trap by name.** | `LLR-N07.2.3` (`:2603`) creates `mapper/views/state.py::ViewState` (frozen, all-defaulted) and `IRenderer` (`runtime_checkable` Protocol). Code-side premises verified: `mapper/views/state.py` **does not exist**; `IRenderer` exists as a Python type **0** times (only comments at `layered.py:288`, `rail.py:6`); AST over `mapper/views/` returns **6** `render` defs, **all** already carrying a `render` attribute. Threshold 2 (`isinstance`) would therefore be **green on master today** — the requirement says exactly this at `:2632-2639` and pairs it with **threshold 3**, a parameter-name equality derived with `inspect.signature`. Named weaker variant `M-N07.2.3-a` is the vacuous `A-11` gate, explicitly reddened by threshold 3. |
| `P2-C6` | condition | **DISCHARGED — census reproduced exactly.** | `~~>= 6~~` superseded (`:2582`); threshold is now four-part **set equality** including *"Call sites — THE CLAUSE THAT WAS MISSING ENTIRELY"* (`:2528`). I re-ran the A3 census by AST at `94ad8d3`: **ARG-FUL `.render` call sites = 23, files = 10, production = 3 → `mapper/app.py:737`, `:1352`, `:1727`; test = 20 / 9 files; ZERO-ARG `.render()` = 25.** Byte-for-byte the figure at `:2554`. Grep control returns 49 raw `.render(` lines — only the AST separates the two protocols. |
| `P2-C7` | condition | **DISCHARGED** | See §3.2 below — routed edit verified. Ownership half also closed: `Inc-2` OWNS the Phase-6 `docs/ARCHITECTURE.md` amendment (`:5514`), with a threshold derived by comparing each declared signature against `inspect.signature` on the live symbol, *"never by reading the table"* (`:5524`), and a stated reason for one owner rather than two. |
| `P2-C8` | condition | **DISCHARGED BY DISPOSITION — recorded honestly as disposed, not answered.** | `HLR-N13.3` threshold 1 is struck: `:3450` `~~"Mount completes in < 1000 ms for 200 maps"~~` **DEFERRED (`#D24`)**; threshold 2 likewise. `:3389-3392` states plainly that `P2-C8` *"is not answered; its subject is gone"* and that the follow-on batch inherits the headroom question. This is consistent with the standing re-scope (S-18 work budget CUT, S-19 its precondition), which I do not re-litigate. **Critically, the batch does not launder the defect**: `:3392-3400` and `BACKLOG.md:156` (`B-33`) both record that `S-15`/`M-H3` — a 73-node map costing 72.5 s — is **LIVE on `master`** and that deferring a bound does not repair a defect. That is the correct record. |

**Roll-up: 14 DISCHARGED · 0 PARTIAL · 0 LIVE.**

---

## 2 · Adversarial review of the three new rulings (task 2)

### 2.0 · §1's registry-collision finding — **VERIFIED TRUE**

Read directly, all three:

- `PLAN.md:244` — `D10` = **Q-3 answered, option (a)**: search takes `n`/`N`, `next_gap` moves `n → M`, three new seat rows.
- `PDR-2026-08-26-ui-next-batch-02.md:566` — `#D10` = **Q-10, the three census exceptions**: `#a3a3a3`, the progress `WARN`, `.factory-tag`. Three **hue** dispositions.
- PDR prose using bare `D10` means **PLAN's**: `:372` *"US-N07 búsqueda + **the seat rebind (D10)**"*; `:484-486` *"the state-dependent chord D10 rejected … D10 rejected option (c)"*.

One id grammar, two registries, and the PDR's own prose crosses between them. The finding stands and
`B-34` is the right carry — subject to `ARQ-3-C3` below.

### 2.1 · `#D25` — **SOUND. Conclusion correct; I found the evidence the ruling did not.**

`#D5b` is quoted **verbatim and accurately** — I checked it character by character against
`PDR-2026-08-26-ui-next-batch-02.md:394-398`.

`#D25` searched only the sealed PDR (*"Searched: `seat-diff`, `three-row`, `cap`"*). I widened the
search to `PLAN.md` — the artifact `#D25`'s own §1 identifies as the true carrier of `D10` — and the
question settles outright. `PLAN.md:244`, `D10`'s closing clause:

> **Condition:** the seat-spec diff is **exactly one changed row plus two added rows**, reviewed
> row-by-row at DDR.

Restated at `PLAN.md:491`: *"**Exactly one changed row plus two added rows**, reviewed row-by-row at
DDR."*

**"Exactly one changed + two added" is an equality on `D10`'s own diff, not an upper bound on anyone
else's.** The sealed PDR's *"`D10`'s three-row seat-diff cap"* is a compressed reference to precisely
that clause. The pin reading is not merely the better construction — it is the only one the carrier
supports. `#D25`'s conclusion is **over-determined**, and the enlarging half (`C-D25a`: a pin per
diff, no global cap) is the right structural response to a real gap.

Three supporting observations of my own:

1. The budget reading makes `#D5b` **incoherent**: it would state a cap and then, in the very next
   sentence, name three further increments under that cap while declining to quantify any of them.
   The pin reading makes it coherent. Charity resolves to the pin.
2. `#D5b`'s own subject is *"Inc-4 … **alone**"*. Its quantifier is one increment.
3. Executed basis reproduces at `94ad8d3`: `duplicate_chords()` → `[]`; `len(KEYMAP)` = 48; `H`, `J`,
   `K`, `L` all absent from the 25 map-scope keys. No collision exists to adjudicate.

**But `#D25` carries two defects, both in its condition text rather than its reasoning.** See
`ARQ-3-C1` and `ARQ-3-C2`.

### 2.2 · `#D26` — **SOUND.** Every premise verified on disk.

- The measurement is real: `01b-ux-decisions.md:368-371` — `MINIMUM legend height: 54 rows` /
  `walkthrough terminal: 34 rows` / `DOES NOT FIT — short by 20 rows`. The flat panel was already
  ruled out, so the live choice really is **scroll vs tabbed**, and the routing did not say so.
- `C-D26b`'s premise is executed: `tests/test_repair_layout.py:118` scrolls with
  `pane.scroll_to(y=…, animate=False)` — **a method call**. It proves the container scrolls and says
  nothing about whether an operator can make it.
- The fix is landed, not promised: `HLR-N16.4` (`:4494`) with threshold = set equality between keys
  with a **measured effect** and keys painted, *"derived by pressing each real key … never by reading
  the seat alone"*; `AT-053` on its `Acceptance:` line (`:4537`); `TC-086` in the functional table
  (`:5411`); named weaker variant `M-N16.4-a` (assert the seat only) explicitly reddened.
- The deferral is honest rather than convenient: the defect actually raised is **discoverability**
  (`down`/`pagedown`/`end` all work, none declared — `:4506-4511`), the union over scroll positions
  is `27/27`, and `HLR-N16.4` closes it under either layout. Adopting a tabbed information
  architecture at the final PDR iteration would be new scope on the one screen whose job is
  discoverability.

**One defect:** `C-D26c` is **unmet today** — see `ARQ-3-C3`.

**One observation, raised but deliberately NOT made a condition.** `C-D26a` moves set equality onto
panel *content*, and `HLR-N16.4`'s threshold binds the *key set*. Neither clause binds **row
reachability** — a container that scrolls one row and stops satisfies both. In practice the rationale
already measures `union over real-key scroll positions : 27/27` and `end` reaches `max_scroll_y`, so
the property is evidenced even though it is not thresholded. I flag it for `Inc-8`'s implementer
rather than gating on it; manufacturing a condition here would be the false-fail C-53 prices.

### 2.3 · `#D27` — **SOUND. The strongest of the three.** Every premise verified.

- `mapper/darkside.py:12-20` ships **exactly nine** tokens: `GROUND`, `PANEL`, `STEP`, `INK`, `MUT`,
  `ACCENT`, `WARN`, `ALERT`, `WORDMARK`. Verbatim correct.
- `01b-ux-decisions.md:332-333` matches the quotation verbatim: *"`ALERT #ff4f42` is **deliberately
  absent** … If ALERT acquires a second job it must acquire a row here too."*
- `LLR-S06.3.5` exists (`:1079`) — *"`WARN` and `ALERT` each carry exactly one job, adjudicated from
  the tree"*. The constraint is real.
- `PRED-VIS` (`:3082`) does admit *"a declared token **or glyph**"*, and the finding's own complaint
  is reproduced at `:3090-3095`: `roto` and `sano_vacio` paint **byte-identically**.
- The sala vocabulary is glyph-led (`01b:314-318`: `⇄`, `◍`, `█`/`░`, `▲`, `∙`), so a glyph is the
  conventional choice in this view, not a fallback.

**The C-55 limb-2 reasoning is correct and it is the conservative call.** Spending `ALERT` on an
emptiness that is an accident of today's scope would hand the follow-on batch a token with two jobs
and a one-job census that can no longer adjudicate it.

**One tension I tested and cleared.** `LLR-N16.2.1`'s derivation **removes `V18`** (`◍ del repo`)
because `#D7` rules it out of this batch (`:4402-4407`). So `TEAL`'s job is *also* deferred, and
`#D27` nonetheless counts `TEAL` as spent. That is not an inconsistency — it is the **same** rule
applied twice: a scheduled-but-not-now job still spends its token. `#D27` is internally consistent,
and its ruling spends no colour either way, so the wrinkle strengthens rather than weakens it.

`C-D27b` (do not fix the codepoint here) is exactly right — a codepoint chosen in the ruling would be
the fifth hand-listed count in a document that has already shipped four.

---

## 3 · The two routed edits (task 3) — **both landed, both correct**

### 3.1 · `ARCHITECTURE-proposed-at-ARQ.md` — `with_header` struck from the dataclass ✓

`git diff 20f86de..HEAD` on that file shows the strike is **inside the committed `ViewState`
dataclass**, exactly where `#D2` needed it. `with_header: bool = True` is **removed** at `:277` and
replaced by a comment recording `#D2`, the pass-1 landing in `01-requirements.md`, the `P2-C4` /
`A-56` closure, and a do-not-reinstate note whose reason is correct: `LLR-N07.2.3`'s signature clause
checks **parameters**, so it cannot catch a stray **field**.

**The surviving mention at `:237` is correctly left intact, and I verified it is a true statement
about the current tree.** `mapper/views/layered.py:131-140` reads:

```
def render(self, graph, selected_id=None, w=80, h=24,
           query: str = "", with_header: bool = True, diff=None) -> Text:
```

The stale address `:78-87` was corrected to `:131-140` in the same edit, with the correction dated
and the claim re-executed. That is the right treatment: the sentence describes today's defect, not
tomorrow's roster.

**Minor, not a condition.** `with_header` survives at a **third** site, `:348`, inside the `R-012`
row's **rejected** additive-kwarg alternative. It is correct in context (a quotation of the shape
that was rejected) but carries no annotation, so an id-scanner grepping this file gets three hits and
only one is marked. Worth a word if the file is touched again.

### 3.2 · `docs/ARCHITECTURE.md` §4 — the `dots`/`bgs` commitment row ✓

The row landed (one-line diff at `docs/ARCHITECTURE.md:160`), is worded like the `ViewState` sibling
at `:159`, marks itself **COMMITTED, NOT PRESENT**, names the batch's **second** A3 explicitly as
distinct from the first, and names `Inc-1` as where it lands.

Both of its factual claims verified at `94ad8d3`:

- **`mapper/canvas.py` declares neither attribute.** `grep -n "dots\|bgs" mapper/canvas.py` → **zero
  occurrences**. `Canvas.__init__` (`canvas.py:30-33`) declares `w`, `h`, `cells`, `bits`,
  `_wire_tones` and nothing else.
- **`RadialRenderer` monkey-patches them.** `mapper/views/radial.py:123-124` — `cv.dots = {}` /
  `cv.bgs = {}` onto the instance — then writes at `:209` and `:224`. A repo-wide search finds **no
  other** module touching `.dots`/`.bgs`.

The row states a plan without asserting a falsehood, which is the device the repair batch established.
Correct.

---

## 4 · Newly raised

| id | Sev | Finding | Executed evidence |
|---|---|---|---|
| **`ARQ-3-N1`** | condition | **`#D25` is landed in the amendment ledger but NOT in the normative body — and the body still blocks `Inc-3`.** `A-74` (`:7513`) records the ruling correctly. But `01-requirements.md:1673-1682` still reads *"⚠ ROUTED — `#D10`'s SEAT-DIFF CAP IS NOW ARITHMETICALLY BREACHED … **`Inc-3` shall not open until the cap is ruled**"*, and `:4540` still says `Inc-8`'s rows *"count against `#D10`'s cap, which §3.4 already routes to the PDR lane as arithmetically breached."* An implementer reads §3.4, not §6.5. **This is the exact failure mode RIDER-1 exists for**, one fold later. | `sed -n '1668,1685p'`, `sed -n '4538,4541p'` |
| **`ARQ-3-N2`** | condition | **The `keymap.py` collision roster is wrong in three artifacts, in two different directions.** `#D25`'s `C-D25a`/`C-D25c` name **`Inc-3`, `Inc-4`, `Inc-6`, `Inc-9`** and *"DDR reviews the **four** diffs"* — but `Inc-6` is **VACATED** (`:5586`). `01-requirements.md:5611` and `:1671` say the collision is **three-way** (`Inc-3`, `Inc-4`, `Inc-9`) — but `HLR-N16.4:4538-4540` puts seat rows in **`Inc-8`**, added the same day. **The true set at `94ad8d3` is four: `Inc-3`, `Inc-4`, `Inc-8`, `Inc-9`.** And §5.4's `Inc-8` row (`:5588`) lists `screens/help.py`, `darkside.py`, `app.py` — **`keymap.py` is not declared**, which is the undeclared-source class validator rule `V9` exists to catch. `#D25` imported `#D5b`'s stale roster verbatim without reconciling it against `A-49`. | `:5586`, `:5588`, `:5611`, `:1671`, `:4538-4540`; `PDR-addendum-3.md:92,98` |
| **`ARQ-3-N3`** | condition | **`C-D26c` is unmet: `B-34` and `B-35` do not exist.** Both are cited four times across two artifacts as landed carries. `.dev-flow/BACKLOG.md` tops out at **`B-33`**. `C-D26c` reads *"deferral is recorded as a carry, not dropped"* — today it is dropped. | `grep -oE "B-[0-9]+" .dev-flow/BACKLOG.md \| sort -uV \| tail` → `…B-31 B-32 B-33` |
| **`ARQ-3-N4`** | record correction | **`PDR-addendum-3` §5's "minimal alternative" does not close `UX2-C-01`.** `mapper/widgets/inspector.py:280` — `_commit` posts `FieldCommitted(node.id, field, widget.value)` unconditionally from `on_input_blurred`. Under `UX2-C-01`'s reproduction, pressing `n` **types the character into the focused `Input`**, so `'ACTA-2011-034' → 'n'` is a **genuinely non-empty delta**. A non-empty-delta predicate closes `UX2-C-11` / `B-31` and **nothing of `UX2-C-01`**. §5 does not literally claim otherwise, but it offers the gate as the alternative to refusing the `UX2-C-01` deferral, which reads as if it did. | `mapper/widgets/inspector.py:277-296`; `02g` §4.4 transcript |

**One finding in the batch's favour, which the addendum did not make and which materially supports
its own recommendation:** `mapper/widgets/inspector.py` appears in **no increment's declared source
set** in §5.4 (`:5583-5591`). **This batch neither touches nor worsens `UX2-C-01`.** That is the
strongest available argument for deferring it, and it is stronger than anything §5 offers.

---

## 5 · Ruling on `UX2-C-01` / `UX2-C-02` (task 4) — **ACCEPT the deferral, with the record corrected**

**Accepted**, on three grounds, in order of weight:

1. **`UX2-C-02` is unbuildable.** Its chord `c` enters the lens; the lens is CUT. A chord with no
   consumer cannot be specified, only guessed at.
2. **The batch does not touch the defective file.** `widgets/inspector.py` is in no increment
   (§5.4). `UX2-C-01` is a **pre-existing `master` defect that this batch does not worsen** — which
   is a materially different thing from a defect the batch introduces and defers.
3. **The affordance design is genuinely new scope** at the final PDR iteration, and it shares one
   confirmation-affordance question with `UX2-C-11`. Splitting that question across two batches would
   produce two half-answers.

**Refused: the framing.** `ARQ-3-N4` above. The record must say that the non-empty-delta gate closes
`UX2-C-11`/`B-31` and **not** `UX2-C-01`, and that `UX2-C-01` carries as a **live durable-data-loss
defect on `master`** — one keystroke, no confirmation, no explicit edit gesture, permanent overwrite
of a tracked file, demonstrated by accident on the repository's own fixtures — not as a design gap.
§5 already says this in its own ⚠ paragraph; the carry in `BACKLOG.md` must say it too.

**I do not require the minimal gate. I offer it, costed.** If the operator wants `B-31` closed inside
this batch: `Inc-REPAIR` is at **1 of 4** source files (`store.py`), it is the increment that already
owns the two live `master` defects, and it is the thematically correct home. Adding
`widgets/inspector.py` takes it to **2 of 4** — no breach, no new increment, no design ruling, one
predicate. That is the cheapest slot in the batch. It closes `B-31` only; `UX2-C-01` still carries.

---

## 6 · Conditions on this approval

All four are individually dischargeable, none requires a design ruling, and each has a named edit.

| id | When | Condition |
|---|---|---|
| **`ARQ-3-C1`** | **BEFORE `Inc-3` OPENS** | Strike the routed-breach block at `01-requirements.md:1673-1682` and replace it with `#D25`'s pin reading; correct `:4540`'s *"count against `#D10`'s cap … arithmetically breached"*. **`Inc-3` is textually still blocked in the normative body**, and `A-74` in §6.5 does not reach an implementer reading §3.4. |
| **`ARQ-3-C2`** | before `Inc-3` opens | Correct the `keymap.py` collision roster to **`Inc-3`, `Inc-4`, `Inc-8`, `Inc-9`** in `C-D25a`, `C-D25c`, `01-requirements.md:1671` and `:5611`; strike `Inc-6` (vacated). Add `keymap.py` to §5.4's `Inc-8` row (`:5588`), taking it 3 → **4, at budget, no breach** — an undeclared source file is the class `V9` catches. |
| **`ARQ-3-C3`** | before batch close | Land `B-34` (bare-`Dn` ambiguity) and `B-35` (tabbed legend) in `.dev-flow/BACKLOG.md`. `C-D26c` is a condition of a ruling being approved here and is **unmet at the moment of approval**. |
| **`ARQ-3-C4`** | with `ARQ-3-C3` | Correct the `UX2-C-01` record per §5 above: the delta gate closes `UX2-C-11`/`B-31` only; `UX2-C-01` carries as a live durable-data-loss defect on `master`, with the fact that no increment touches `widgets/inspector.py` recorded as the reason deferral is defensible. |

**Not conditions, noted for implementers:** the unannotated third `with_header` at
`ARCHITECTURE-proposed-at-ARQ.md:348` (inside the *rejected* alternative — correct in context); and
`HLR-N16.4`'s threshold binding the key set but not row **reachability** (evidenced at `27/27` in its
own rationale, just not thresholded).

---

## 7 · False oracles — checked, not propagated

- **`UX2-C-04`'s raw-id trace.** Not used. The canvas paints node **titles**, not raw ids; an oracle
  searching for the id false-fails a perfect implementation. `A-66` replaced it and I did not
  re-derive anything from the old form.
- **`A-11`'s `isinstance` gate.** Confirmed vacuous on the current tree by AST — all six
  `mapper/views/` renderers already carry a `render` attribute, so `runtime_checkable` member-presence
  passes **before any migration**. `LLR-N07.2.3` threshold 3 is what makes the pair discriminating. I
  graded `P2-C5` on the pair, never on the `isinstance` clause alone.
- **The heading census anchor.** Used `^#{4,5} \`?(HLR|LLR)-` exactly. Live at `94ad8d3`: **25 HLR /
  62 LLR** headings total, matching the briefed figure (21/52 after `DEFERRED`/`SUPERSEDED`). No
  drift; `S-17`'s misdiagnosis not repeated.
- **AST over grep, everywhere it mattered.** Four censuses re-derived by `ast`, never by substring:
  the A3 blast radius (23, vs grep's 49 raw lines), `rows()` consumers (4/3), `.collapsed`/`.toggle`
  (12/6-external), and the digest pin dictionaries (12/5/1).

---

## 8 · Evidence checklist

| Item | | Evidence |
|---|---|---|
| Constraints stated explicitly | ✓ | Standing re-scope A honoured (US-N14 and S-18/S-19 CUT, not re-litigated); ≤4 source files per increment checked against §5.4 `:5583-5591`; final-iteration scope constraint applied to `#D26` and to `UX2-C-01` |
| At least 2 alternatives considered | ✓ | `#D25` tested under **both** the budget and the pin reading, and resolved from `PLAN.md:244`'s carrier rather than by preference; `UX2-C-01` weighed accept-deferral vs require-gate, with the gate costed into `Inc-REPAIR` |
| Recommendation tied to constraints | ✓ | §5 grounds 1–3; §6 conditions each name a file:line and a slot |
| Risks listed | ✓ | §4 `ARQ-3-N1`–`N4`; `Inc-3` textually blocked; undeclared `keymap.py` in `Inc-8`; two live `master` defects verified still live at `store.py:456` and `store.py:384-388` |
| Cost / latency estimated where relevant | ✓ | No model calls, no network. Cost is source-file budget: `Inc-REPAIR` 1→2 of 4 for the optional gate; `Inc-8` 3→4 of 4 for the declared `keymap.py`. `P2-C8`'s wall-clock budget deferred with its subject; `S-15`'s 72.5 s / 73-node measurement recorded as LIVE, not disposed |
| Diagram included when flow is non-trivial | n/a | The flow at issue is a condition ledger and three text rulings; §5.4's table is the cut and it is already tabular |
| What would change the recommendation | ✓ | §9 |
| **Two-layer requirements: Acceptance block + `AT-NNN`, BOTH chains** | **✓ — first time in this batch** | Behavioral `US→AT` at `:5266`; functional `US→HLR→LLR→TC` at `:5340`. **They now cross**, via `#D15`'s derived join (`:5415`), which **I executed independently at `94ad8d3`: 0 live `AT` ids reach no `TC`.** Graded ✗ at both prior passes |

---

## 9 · What would reverse this verdict

- **A budget reading of the seat cap surviving anywhere.** I searched `PDR` **and** `PLAN.md` for
  `seat-diff`, `three-row`, `cap`, `budget.*seat`, `seat.*budget`. The only carrier is `PLAN.md:244`'s
  *"exactly one changed row plus two added rows"* — an equality on `D10`'s own diff. A cross-increment
  budget found anywhere would re-block `Inc-3` and reverse `#D25`.
- **`ARQ-3-C1` not landed before `Inc-3` opens.** An increment opening against a normative body that
  says it shall not open is a gate failure on the first commit, and the likely repair — weakening the
  clause under time pressure — is worse than the delay.
- **Any of the 14 discharges failing to reproduce.** Each is a named command; all are re-runnable at
  `94ad8d3`.
- **A fifth generation of any census transcribed as a literal.** Every threshold that had one now
  carries a QUESTION / INSTRUMENT / MEASURED-AT derivation instead. A literal reappearing is a
  regression to the defect that cost this batch five generations of one number.

---

**Architect verdict for PDR iteration 3: `approved with conditions`.**
14 of 14 architect conditions discharged · `#D25`, `#D26`, `#D27` all sound · both routed edits landed
and verified · 4 new conditions, all document-lag with named one-edit fixes · `UX2-C-01`/`UX2-C-02`
deferral **accepted** with the record corrected. **The batch should seal and implement, with
`ARQ-3-C1` landed before `Inc-3` opens.**
