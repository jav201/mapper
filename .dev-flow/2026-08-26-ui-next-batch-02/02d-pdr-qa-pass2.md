# 02d — PDR QA / acceptance lens, SECOND PASS · `2026-08-26-ui-next-batch-02`

> **Method (C-43).** Audited against **my own 35 source findings in `02a-qa-acceptance-review.md`**
> (10 blockers · 14 majors · 11 minors), **never against §6.5's amendment table**. For each finding I
> re-read the requirement text as it stands now and marked it CARRIED / RETIRED-WITH-REASON /
> **DROPPED**. Every number below was executed against `d877784` in this session; transcripts pasted.
> **READ-ONLY**: no file under `mapper/` or `tests/` was created, modified or staged; probe scripts
> live in the session scratchpad. The full pytest suite was **not** run (C-25 — the orchestrator owns
> gate runs). Mutated ids are described by position and operation, never pasted (C-56).

---

## 1 · VERDICT

**`approved with conditions` — 8 named, individually dischargeable conditions. No blocker stands.**

**The acceptance layer is repaired.** All ten pass-1 blockers are closed on the merits, and three of
them are closed *better than I prescribed*, with my own prescribed remedy executed and shown to fail:

- `QA-B-01` — my two-predicate replacement is **green on the pure deletion**. The fold added a third
  (converse containment) and pasted the mutation table proving it. My `>= 8`-character prefix
  remedy **false-fails 69 times**; the only discriminating length is a one-value window.
- `QA-B-09` — my hand-listed containment set `· ◆ ● ─ │ ┌ ┐ ┬ ┼ ▐` is **not a subset of the
  pre-change radial render**: seven of its ten members are `LayeredRenderer` glyphs radial never
  paints. Adopting it verbatim would have **blocked the correct fix**.
- `QA-B-06` — my "a substring oracle returns False even for correct content" is **conditionally**
  true, not unconditionally; it depends on per-cell style variation, and the fold wrote the trap into
  the requirement.

That is a fold that audited its inputs rather than transcribing them.

**What stops an unconditional `approved` is four things the fold did not do, two of which it dropped
silently and one of which its own amendment table asserts as done and is not:**

1. **`QA-M-02` was DROPPED.** It appears **zero times** in `01-requirements.md` and zero times in
   `PLAN.md` under its own id. `PLAN.md` §9 C-1 carries the correction under a different label, but
   **R-1's own row still reads *"plus 7 test files"***, and the §9 correction (29 sites / 14 files)
   is itself now stale: executed at `d877784`, **48 `.render(` sites across 17 files, 15 of them test
   files**. Third generation of the same census defect, on the batch's largest declared risk.
2. **`QA-N-08` was DROPPED.** Zero occurrences in either document.
3. **Six live `AT` ids fail the document's own three-way derivation rule**, and for one of them
   (`AT-009`) amendment `A-29` states a promotion that **is not in the text**. §5.2's own words:
   *"An id present in fewer than all three is a defect, not a test."*
4. **`LLR-STO.1.1` is referenced normatively and does not exist** — no heading, no method, no
   threshold, no `AT`, no `TC`, no increment, and `LLR-N13.1.5` (security blocker `C-3`) is written
   to depend on it.

None of these makes a wrong implementation pass an acceptance test. Each is a document edit with a
named remedy and no new measurement. That is the boundary between a condition and a blocker, and
these land on the condition side of it.

### 1.1 · The eight conditions

| # | Condition | Discharge |
|---|---|---|
| **QA2-C-01** | Bring the six intersection-failing ids into the three-way rule or strike them. `AT-009` gets the `Acceptance:` line `A-29` claims; `AT-034b`, `AT-046`, `AT-047` get onto their stories' `Acceptance tests:` lines; `AT-031` and `AT-040` are either promoted or removed from the story lists and §5.2 table, since a declared-catalog-only id still counts as declared everywhere a reader looks. | §3 + §5.2 edits; re-run the intersection script in §3 below and show it empty. |
| **QA2-C-02** | Re-derive the A3 blast radius **at `d877784`** and re-size `R-1` in its own row. Executed truth below: 48 sites / 17 files / 15 test files. Correct `PLAN.md` §5 B1, §9 C-1 and §11. | Paste the grep; edit R-1. |
| **QA2-C-03** | Write `LLR-STO.1.1` as a block, or re-home the five-exception-type arm into a requirement that exists. It is currently prose inside `LLR-N13.1.6` carrying a `shall`. | One heading with method + threshold + owning increment, or a re-home. |
| **QA2-C-04** | `HLR-S06.3`'s threshold still reads *"every `WARN`/`ALERT` site is classified **severity**"* — which is exactly `M-S06.3.5-a`, the mutant `LLR-S06.3.5` names. Restate the parent against the two adjudicated jobs. | One-line edit at the parent. |
| **QA2-C-05** | Define the census **classifier**. *"Every derived `WARN` site classifies as outstanding attention"* has no executable definition — this is `QA-B-04`'s shape at a different surface. Name how a site is classified (keyword table? declared per-site register? inspection with a recorded verdict?), or mark `AT-005`/`AT-006` `analysis` rather than `test (unit)`. | Requirement edit. |
| **QA2-C-06** | Resolve the increment cut (C-21, below). `HLR-N13.3` says *"gates Inc-6"*, §3.6's header says Inc-6, `PLAN.md` §13.4 says **Inc-7**. §3's labels show only Inc-1 … Inc-7 against a **9**-increment cut. `AT-007` / `AT-007b` share one *"Inc-1 and Inc-2"* label. | Reconcile PLAN §13.4 with §3's headers; give `AT-007` and `AT-007b` one increment each. |
| **QA2-C-07** | Restore `QA-M-02` and `QA-N-08` to a ledger. `QA-N-08`: `LLR-N07.1.2`'s widening arm needs a synthetic graph (the legacy fixture has no attachments and no distinguishing `meta`) and it is in no increment's fixture budget — alongside `anidado` and `AT-048`'s generated workspace, that is now **three** unbudgeted fixtures. | Fixture budget line per increment. |
| **QA2-C-08** | Fix the `AT-007` / `AT-007b` id staleness inside the amended text: `HLR-CNV.2`'s own prose says *"the title, the §5.2 row and `AT-007` all name `RadialRenderer`"* and *"`AT-007`'S EMPTY ARM IS VACUOUS"*, but its `Acceptance:` line is `AT-007b`; §5.3 criterion 5 names `AT-007` for the containment arm `AT-007b` owns. | Three id substitutions. |

**Nothing here asks for a new measurement.** Every condition is dischargeable by editing a document
and re-running a grep already written below.

---

## 2 · Source-findings audit — one row per original finding

Legend: **CARRIED** = the finding is addressed and I re-read the text that addresses it ·
**RETIRED** = its subject no longer exists, with a reason I checked · **DROPPED** = no trace in
either document.

### 2.1 Blockers (10)

| # | Disposition | Requirement text I re-read, and what it now says |
|---|---|---|
| **QA-B-01** | **CARRIED — closed, and improved** | `HLR-N06.3` *Numeric pass threshold — THREE predicates, all three required*: `PRED-1` reconciliation, `PRED-2` `declared ⊆ traced`, `PRED-3` `traced ⊆ declared`. Executed mutation table pasted in the requirement: the pure-deletion mutant is `P1=True P2=True P3=False`; the plausible-weakening mutant likewise; the over-declare mutant is `P2=False`. Fixture **named** (`fixtures/legacy`) with four `(w,h,folded)` triples pinned in a table, and the seed map ruled out with its executed reason (hides a node at 0 of 56 swept sizes). Trace predicate is the `_clip` image **restricted to visible columns**, with `P-A1` false-neg 20 / `P-A2` false-neg 0 pasted. Two named weaker variants. **The replacement is sound and falsifiable.** |
| **QA-B-02** | **RETIRED — subject struck, lesson verified present** | §3.1 carries a `SUPERSEDED — SATISFIED-EXTERNALLY` banner (lines 472–620); `AT-001`, `AT-002`, `TC-001`…`TC-005` struck. I checked the lesson actually landed rather than being promised: `HLR-N06.3`'s *Painted-trace oracle* block reproduces it with a fresh transcript (36-char title paints as a truncated image at 80 x 24) and states *"a raw-**id** trace is false always, because the canvas paints titles and never ids."* |
| **QA-B-03** | **CARRIED-PARTIAL — the blocker closes, a weaker tier remains** | The three fabricated ids are deleted; §5.2 states no literal total and gives the three-way derivation instead. **But the derivation does not hold on the document that states it** — 6 live ids fail it (§3 below), and `A-29`'s claim that `AT-009` *"is **promoted** under `LLR-CNV.2.1`"* **executes false**: `LLR-CNV.2.1` ends with an `Acceptance criteria:` prose bullet and carries no `Acceptance:` id line. → **QA2-C-01**. |
| **QA-B-04** | **RETIRED — discharged by an on-disk artifact** | The oracle is `_painted_bindings` over `_rows_in` in `tests/test_repair_layout.py`, region-clipped, with `test_at_r14_the_oracle_is_clipped_to_the_help_dialog` as the negative control. Writing a second oracle is forbidden by the amended requirement. Pilot-size obligation landed: §3.8 reads sizes from `WIDE_SIZES` / `NARROW_SIZE` *"rather than re-typed"*. `bindings_for` pinned: every count is now `len(keymap.bindings_for(scope))`, evaluated at run time (`QA-M-04` with it). |
| **QA-B-05** | **CARRIED — honest carry, not a re-run of the defect** | This was the one I was asked to judge. **It is an honest carry.** The original defect was that the negative control *did not exist* and was discharged by an argument. Now: the `anidado` fixture is written into `LLR-N06.3.2` normatively (7 nodes, depth 3, `FOLD = {ops, log}` with `log` nested inside folded `ops`), built through `MapStore.save` and reloaded through `MapStore.load`, with `naive_sum = 6` vs `painted_sum = 4` and the double-counted pair named. The shipped fixture's unfalsifiability is upgraded from a structural argument to **exhaustion over all 7 non-empty fold configurations, 0 disagreements**. *"Inc-3 shall not open without it."* The residual is categorically different: **the falsifiability proof is discharged now**; what is deferred is the *Layer-B surface* observation, which is impossible before the increment that creates the surface — `render()` takes no `folded` argument today. And it is not absorbed: §6.2 **splits it into two items**, item 1 discharged and item 5 the residual, with *"Any reading of item 1 as 'fully observable' would be wrong."* `TC-032` is named as the Pilot re-run. That is the discipline I asked for. |
| **QA-B-06** | **CARRIED — closed** | `LLR-CNV.2.1`: `disk_braille(path) == braille_count(on_screen_text.plain)`, with the read-back function pasted as code — it **scans code points** `0x2800 ≤ ord(c) ≤ 0x28FF` in the written bytes. `size > 0` is *"retained as a precondition and explicitly not the threshold"*, with the executed proof that it passes twice on artifacts containing zero braille (19 679 bytes and 2 732 bytes). Both required clauses present: scan code points **or** parse `<text>` nodes, **and** shall not be validated against a uniformly-styled fixture. Two mutants named. **Confirmed: not a substring oracle.** |
| **QA-B-07** | **CARRIED — closed** | `LLR-N13.1.3` now reads *"shall state the value **100**, and shall state the same value as every other such surface"*, threshold `pct(schema-less) == 100` **and** consumer agreement, *"Both clauses are required."* Addresses re-derived (the parked ones were stale). `M-N13.1.3-a` is the exact weaker commit I named, and §5.3 criterion 5 lists it as a required RED. |
| **QA-B-08** | **CARRIED-PARTIAL — closed at the LLR, stale at the parent** | `LLR-S06.3.5` declares one job per token in one sentence each, adjudicated from a 36-site derived listing pasted in the requirement, and resolves **against both** parked definitions (`WARN` paints a search hit at 0 of 36 sites). `ALERT` gains no second job, with the reason. Both parked sentences checked: `LLR-N07.3.2`'s is struck in place; `HLR-N06.2`'s is gone. **But `HLR-S06.3`'s own threshold still reads *"every `WARN`/`ALERT` site is classified severity"*** — which is `M-S06.3.5-a` verbatim, the mutant its own child was written to redden. → **QA2-C-04**. And the classifier has no executable definition → **QA2-C-05**. |
| **QA-B-09** | **CARRIED — both limbs closed** | **Limb (a):** `HLR-CNV.2` is retitled *"`PIN (radial)` · braille free-angle edges reach `RadialRenderer`'s painted output"*, settled **structurally** — `grep -rn "\.dots\b" mapper/` returns exactly two sites, both in `radial.py`; `|cv.bits| = 0` for radial; so no fix to `Canvas.rows()` can raise the map canvas above 0. The gap is declared in §6.2 item 4, not hidden. **Limb (b) — the one I was asked to verify — is genuinely closed.** See §4.1 for the mutation analysis. |
| **QA-B-10** | **CARRIED — closed by folding, which was the right fix** | `A-26` folds all five sealed PDR rulings into the requirements that own them, with a per-ruling table, and every affected `AT` now drives a real key. `HLR-N07.3`'s *"written chord-agnostic; PDR settles the chord"* is gone. Three conditions carried forward (`C-D6a`, `C-D9a`, `C-D9b`), and `C-D9a` is carried **with the PDR's own probe recorded as vacuous** (`app.focused` was `None` throughout, so it could not fail) rather than banked as green. §6.1's `Q-3`, `Q-5`, `Q-7`, `Q-8`, `Q-9`, `Q-10` are no longer OPEN. |

### 2.2 Majors (14)

| # | Disposition | What the text now says |
|---|---|---|
| **QA-M-01** | **CARRIED** | `LLR-N07.2.1` threshold: query pinned to **`carlos`**; counts equal; `> 0` both states; **and at least one hit strictly inside folded branch `fin`, painted before the fold**. `riesgo` named as the vacuous case with its reason. `M-N07.2.1-a` added. |
| **QA-M-02** | **DROPPED** | Zero occurrences in `01-requirements.md`; zero in `PLAN.md`. `PLAN.md` §9 C-1 records the correction under a different label, but **`R-1`'s own row (line 214) still reads *"plus 7 test files"***, and §9's replacement figure is itself stale. Executed at `d877784` — see §5.1. → **QA2-C-02**. |
| **QA-M-03** | **CARRIED** | `LLR-S06.3.1`/`.3.3`/`.3.4` floors replaced by **set equality against the derivation**, with the reason stated better than mine: `>= 30` *does* catch the 16-file glob, but *"catching it is an accident of the gap"* — a derivation losing three files sits above the floor. |
| **QA-M-04** | **CARRIED** | Every count is `len(keymap.bindings_for(scope))` evaluated at run time and never typed; the 25-vs-27 ambiguity is recorded with the executed numbers. |
| **QA-M-05** | **CARRIED** | `UX-Q3-a` and `UX-Q3-b` are in `HLR-N07.3`'s threshold table with the exact string `n siguiente · N anterior · esc limpiar`. The fold order is recorded: UX-Q3-b names `n`/`N`, correct only after `#D5b`. |
| **QA-M-06** | **CARRIED** | `E1b` (`sin búsqueda activa` / `pulsa / para buscar`) and `E1c` (`0 coincidencias` / `«nóm» no aparece en este mapa`) are both in the same table as distinct rows, with `M-N07.3-b` (one toast for both) named as the mutant. |
| **QA-M-07** | **CARRIED** | `US-N06`'s empty cell is split into **zero-hidden** (`AT-015` at `(50, 12, ())`) and **genuinely empty** (a 0-node graph, `01b`'s E3), with the shipped 0-node behaviour executed and pinned. |
| **QA-M-08** | **CARRIED** | `LLR-N14.3.2` threshold gains *"from the query `Input`, pressing `escape` shall move focus out of the box, with the hint line naming that route"*, plus `M-N14.3.2-a`: 9 targets / 8 transitions green, inspector unreachable — *"the escape clause is the only arm that reddens it."* Retained verbatim as a standing guard (`C-D6b`), re-run after Inc-4, Inc-6, Inc-9. |
| **QA-M-09** | **CARRIED** | `HLR-N16.2`'s floor is now the vocabulary asserted **as a set** equal to `01b` DECISION 3's enumeration (21 rows plus 5 colour rows), not *"at least 5 glyphs"*. |
| **QA-M-10** | **CARRIED** | The title threshold now covers the three map views **and every non-map screen in `LLR-N16.1.1`'s derived set** — the screens the defect is actually on. |
| **QA-M-11** | **CARRIED, with my number corrected** | The derivation command is named (`git ls-files` over `mapper/`, **not** `rglob`, **not** `glob`) with the reason. `A-32` corrects me: the non-recursive glob yields **16**, not the 5 I reported. I re-executed and confirm 16 — my figure was wrong; the finding stands. |
| **QA-M-12** | **CARRIED-PARTIAL** | `AT-025` split into `AT-025` / `AT-025b`, `AT-007` into `AT-007` / `AT-007b`, with the reasons. **But the same finding's `AT-009` limb is where `A-29`'s promotion claim fails**, and `AT-005` remains claimed by five requirements (`HLR-S06.3` + four `LLR-S06.3.x`) — all one method, so realisable, but not addressed. |
| **QA-M-13** | **CARRIED-PARTIAL** | `AT-034b` created and claimed on two `Acceptance:` lines (`LLR-N14.1.4` and `LLR-N14.1.3`, both `test (unit)`, so C-18-realisable). **The split was not carried into `US-N14`'s story list**, which still ends at `AT-039`, `AT-040`. → **QA2-C-01**. |
| **QA-M-14** | **CARRIED** | `LLR-N14.1.1`'s normative copy is complete — all four strings written in full including `· campos: D acta · O origen · E estado · C criticidad`. The two line forms are reconciled explicitly rather than normalised away. The `⇥ recorrer` fragment is superseded by `#D6`. |

### 2.3 Minors (11)

| # | Disposition | Note |
|---|---|---|
| **QA-N-01** | **DEFLECTED, and the target was not edited in place** | Correctly *"not this document's"*. `PLAN.md` §9 C-2 records it; **§6's P-19 row still carries *"the census's 155 matches neither"***. |
| **QA-N-02** | **DEFLECTED, target partially edited** | Checked and true: neither `17` nor `MISSING=10` is quoted in `01-requirements.md`. `PLAN.md` §11 records the corrected 16/11; **§9's transcript at lines 247–248 still prints `painted=17 MISSING=10`** as raw evidence, which is honest as a transcript. |
| **QA-N-03** | **CARRIED** | `A-28`: executed, **5 of 6** declare `**kwargs`; `layered.py:131` takes an explicit `query: str = ""`. Addresses re-derived; three of six moved. |
| **QA-N-04** | **CARRIED** | Restated in `HLR-N06.3`'s rationale as *"121 of 129 had no full-title trace"*, with the conflation named. |
| **QA-N-05** | **CARRIED as verified** | Recorded as verified, not as a defect; `A-31` then derives the register size from `#D10`'s dispositions (1 after Inc-1, 0 after Inc-9) instead of the parked *"exactly 3"*, which would have reddened Inc-1 for doing what the ruling requires. |
| **QA-N-06** | **CARRIED** | In `HLR-N06.3`'s verification: *"The oracle joins the region-clipped rows before parsing."* |
| **QA-N-07** | **CARRIED** | `LLR-N06.2.1` enumerates the two `OutlineRail.toggle` call sites by file and line, both predicted red. |
| **QA-N-08** | **DROPPED** | Zero occurrences in either document. `LLR-N07.1.2`'s widening arm still needs a synthetic graph and is in no increment's fixture budget. → **QA2-C-07**. |
| **QA-N-09** | **RETIRED — no subject** | Correct and correctly recorded: the sentence lived inside the S-8 paragraph struck by `A-03`. Recorded rather than silently dropped, which is the right handling. |
| **QA-N-10** | **DEFLECTED** | Correctly not this document's. `PLAN.md` retains both adjacent measurements. |
| **QA-N-11** | **CARRIED** | `mapper/search.py` confirmed dead, 0 imports; every `search` LLR is new-module work in the ledger. |

### 2.4 Roll-up

| | Carried | Carried-partial | Retired w/ reason | Deflected | **Dropped** |
|---|---|---|---|---|---|
| Blockers (10) | 5 | 2 | 3 | 0 | **0** |
| Majors (14) | 11 | 2 | 0 | 0 | **1** |
| Minors (11) | 5 | 0 | 1 | 3 | **1** |
| **Total (35)** | **21** | **4** | **4** | **3** | **2** |

**2 of 35 dropped silently.** For calibration, the comparable audit that motivated this method
measured 20 dropped of 163. This fold is an order of magnitude cleaner. The two that fell are both
findings whose *target document was `PLAN.md`* — the fold's blind spot is the boundary between lanes,
not its own text.

---

## 3 · The derived `AT` count — three-way intersection, executed

§5.2 mandates the count be *"the cardinality of the set of `AT-NNN` tokens that appear on an
`Acceptance tests:` line of a story's Acceptance block **and** on an `Acceptance:` line of some HLR or
LLR **and** in the behavioral table — the three-way intersection, computed by grepping this
document."* Computed. Script at
`…/scratchpad/at_intersect.py`; the struck §3.1 (lines 472–620) is excluded from sets A and B, since
`A-02` makes it non-normative.

```
$ PYTHONUTF8=1 python at_intersect.py

section 3.1 (SUPERSEDED) = lines 472..620
section 5 starts line 3944; section 6 starts line 4141

RAW (including struck section 3.1):
  |A| story-list      = 45
  |B| requirement Acc = 44
  |C| behavioral tbl  = 48
  A n B n C           = 41

LIVE (struck section 3.1 excluded):
  |A| story-list      = 43
  |B| requirement Acc = 43
  |C| behavioral tbl  = 48
  THREE-WAY INTERSECTION = 40

UNION = 48 ; FAILING THE INTERSECTION = 8
  AT-001  membership[A,B,C]=--C   (A,B only in the struck section; C is §5.2's strike note)
  AT-002  membership[A,B,C]=--C   (idem)
  AT-009  membership[A,B,C]=A-C   A@line 957   B@none        C@line 3969
  AT-031  membership[A,B,C]=A-C   A@line 2235  B@none        C@line 3972
  AT-034b membership[A,B,C]=-BC   A@none       B@2819, 2860  C@line 3973
  AT-040  membership[A,B,C]=A-C   A@line 2670  B@none        C@line 3973
  AT-046  membership[A,B,C]=-BC   A@none       B@line 1630   C@line 3970
  AT-047  membership[A,B,C]=-BC   A@none       B@line 1630   C@line 3970
```

**Set C is inflated by two.** Its 48 includes `AT-001` and `AT-002`, which appear in §5.2's S-7 row
only inside the prose *"none — `AT-001` and `AT-002` are struck"*. Discounting those, **|C| = 46**,
which is the live union.

### 3.1 The batch's real declared count

> **40.**

**Six live ids fail the document's own rule**, and §5.2 says what that makes them: *"An id present in
fewer than all three is a defect, not a test."*

| Id | Failure | Verdict |
|---|---|---|
| `AT-009` | On the `HLR-canvas` story list and in §5.2, described in a boundary catalog, with a **complete predicate in `LLR-CNV.2.1`** — but no `Acceptance:` id line anywhere. | **`A-29` asserts this promotion happened. It did not.** The predicate is sound; the trace link is missing. One-line fix. |
| `AT-031` | Catalog-only. `A-29` dispositions it as such honestly. | Still counted in the story list and §5.2 table, so still reads as a test. |
| `AT-040` | Catalog-only. Same. | Same. |
| `AT-034b` | Created by `A-37`; claimed by `LLR-N14.1.4` and `LLR-N14.1.3` and in §5.2 — but **`US-N14`'s `Acceptance tests:` line was not updated**. | The split half-landed. |
| `AT-046` | On `LLR-N06.2.4`'s `Acceptance:` line and in §5.2 — **not on `US-N06`'s `Acceptance tests:` line.** | Pre-existing; the fold rewrote §5.2's US-N06 row to include it and never touched the story list. |
| `AT-047` | Same. | Same. |

`AT-046` / `AT-047` are a finding my **own pass 1 missed**: `QA-B-03` tested only the
"no `Acceptance:` line" direction, so ids missing from the *story list* were invisible to it. The
document's new three-way rule catches them. That is the rule working — and the reason the rule must
now be run against the document that states it.

### 3.2 Reconciliation with `V2` — and with `01d`

```
$ python -c "distinct AT tokens in 01-requirements.md"
  regex AT-\d+       -> 48 distinct
  regex AT-\d{3}b?   -> 51 distinct   (b-suffixed: AT-007b, AT-025b, AT-034b)
```

**`V2` = 51, and it reconciles exactly with the `b`-aware whole-file harvest.** Three numbers are in
play and they answer three different questions:

| Number | What it is | Status |
|---|---|---|
| **51** | `V2`'s blocks — every distinct `AT` token anywhere in the file, supersession-blind, including the five struck/deleted ids `AT-001`, `AT-002`, `AT-027`, `AT-028`, `AT-045`. **Correctly red pre-implementation** (the C-18 realisation gate). | Not the declared count. **`A-19`'s explanation of it is now stale**: it says `V2` matches `AT-\d+` and that *"48 is 47 + `AT-048`"*. `AT-\d+` yields 48 distinct here, not 51 — so `V2` is capturing the `b` suffix and set 2's three splits are what moved 48 → 51. |
| **46** | Live union — ids appearing in at least one of the three places. | The upper bound on what a reader would call "the AT set". |
| **40** | **The three-way intersection — the batch's real declared count by its own normative rule.** | **This is the figure.** |
| ~~44~~ | `01d-unpark-measurements.md` §6 — *"47 declared · 3 pure padding · 44 real"*. §5.2 names `01d` **the authority on the current value**. | **STALE by two amendment generations.** It was computed before `A-02` struck two ids and before set 2 added four and split three. **The named authority carries a number that describes none of the three sets.** Folded into QA2-C-01. |

**Naming a sibling artifact as the authority on a derived figure re-creates the defect the derivation
was written to prevent** — a number maintained in one place and consumed in another. §5.2 was right to
stop typing a literal; it should compute the intersection *in place* rather than delegating it.

---

## 4 · New-predicate vacuity sweep — C-10 / C-31 / C-40 on the clauses the fold authored

The fold wrote nine new requirement blocks (`LLR-S06.3.5`, `LLR-CNV.1.4`, `LLR-N06.2.5`,
`LLR-N13.1.5`, `LLR-N13.1.6`, `LLR-N14.1.4`, `HLR-N13.3`, `LLR-N07.2.2a`, `LLR-N07.2.2b`) plus §3.0
`COERCION_RANGES` and a large rewrite of `HLR-N06.3`, `HLR-CNV.2`, `HLR-N07.3`, `HLR-N16.2`.
`PLAN.md` §14.1 records the orchestrator authoring a fresh vacuous check this batch, so these get my
own controls, not a pass because they are new.

| New clause | C-10 drives a non-default value? | C-31 quantified set derived? | C-40 subject present in the expression? | Verdict |
|---|---|---|---|---|
| `HLR-N06.3` `PRED-1/2/3` | ✓ — three mutants executed, each moving a different predicate | ✓ — `traced_set` and `declared_painted_set` both computed at run time from the renderer's own geometry; `card_w` and `cx` *"taken from the renderer's own geometry at run time and never typed"* | ✓ — the subject is the painted frame, read through `_rows_in`, explicitly **not** `render().plain` and explicitly not `_tree_layout`'s keys (`M-N06.3-b`) | **sound** |
| `HLR-CNV.2` containment arm | ✓ — see §4.1 | ✓ — `pre_set = {c for c in painted_text if not c.isspace()}` captured at run time; the hand-list is shown failing in both directions | ✓ — `RadialRenderer`, fixture and 80 x 24 named in the statement | **sound** |
| `LLR-CNV.2.1` disk read-back | ✓ — pre-state 0, positive control 12 of 12, negative control 0 | ✓ — count computed from the bytes, no literal | ✓ — the subject is the file on disk, and `size > 0` is explicitly demoted from threshold to precondition | **sound** |
| `LLR-N06.3.2` `anidado` | ✓ — `naive_sum = 6` vs `painted_sum = 4` | ✓ — exhaustive over all 7 fold configurations of `legacy` | ✓ — but the **surface** is not yet the subject; §6.2 item 5 declares it | **sound, residual declared** |
| `LLR-CNV.1.4` | ✓ — 14 malformed style strings, all 14 must paint the fallback | ✓ — token set is `LLR-S06.1.1`'s declared set plus `#D10`'s promotion, *"no new bound is invented"* | ✓ — validation placed in `rows()` because `M-V1` (write-time validation) is shown to miss `radial.py`'s direct assignment | **sound** |
| `LLR-N06.2.5` notify census | ✓ — 15 dynamic sites lacking `plain()` | ✓ — **AST walk, not a grep**, with the reason: `grep -c "\.notify("` returns 30 *"by coincidence"* | ✓ | **sound** |
| `HLR-N13.3` budget | ✓ — 51-node / 1 935 ms fixture is over budget while 12 000 nodes is not | ✓ — the DAG table is executed and reproduced independently by two lanes within 3 % | ✓ — five mutants (`M-H1`, `M-H2`, `M-H3`, `M-H5`, `M-H6`), each mapped to the threshold that reddens it | **sound**; ms figures honestly flagged `assumed — verify in Phase 3` |
| `LLR-N13.1.5` | ✓ — threshold is painted card count **AND** per-card state distinguishability, because §14.1 executed that card count alone is *already green on the shipped defect* | ✓ | ✓ | **sound — and this is the model correction of the batch** |
| `LLR-N14.1.4` | ✓ — `search_hits('')` returns every node today; the arm binds both owners | ✓ — bounds measured at n=500/2000/10 000 | ✓ | **sound** |
| `LLR-S06.3.5` jobs | ✓ — `M-S06.3.5-a`/`-b` each reddened by a named clause | ✓ — 36 sites derived and listed | **✗ — the classifier is undefined.** *"Every derived `WARN` site classifies as outstanding attention"* names no computable function. *"The classifier keys on the two declared jobs, read from the design module's own prose"* is not an oracle. | **C-40 gap → QA2-C-05** |
| `HLR-S06.3` (parent, unamended) | — | ✓ | **✗ — threshold still reads *"classified severity"***, which is exactly the single-job mutant its own child names | **→ QA2-C-04** |
| `LLR-S06.3.1/.3.3/.3.4` set equality | ✓ | ✓ — `git ls-files` named over `rglob` and `glob`, with the reason they stop agreeing | ✓ | **sound** |
| `HLR-N07.3` UX strings | ✓ — `M-N07.3-b` (one toast for both states) named | ✓ | ✓ — exact painted strings | **sound** |
| `HLR-N16.2` | ✓ — *"a legend shipping ONE glyph passed both parked floors"* | ✓ — vocabulary as a set against `01b`'s single declaration | ✓ — subject widened to the screens the defect is on | **sound** |

**One vacuity found in fourteen**, and it is an inherited parent rather than a fresh authoring. The
fold did not repeat `PLAN.md` §14.1's pattern.

### 4.1 `QA-B-09` limb (b) — C-40, answered directly

**The mutation:** compose the `dots` layer at the **wrong precedence** in `Canvas.rows()`, so braille
is written over cells the node cards already own. Plausible because precedence is one argument order
in one composite call, and the layer genuinely *is* drawn — this is not a deletion. Named
`M-CNV.2-a` in the requirement.

**Can the predicate go RED under it? Yes — and only the containment arm can.** The requirement's own
executed table:

| Candidate set | `\|S\|` | `S ⊆ POST_good` | `S ⊆ POST_mutant` | reddens? |
|---|---|---|---|---|
| full distinct non-space set, **derived at run time** | **19** | True | **False** | **yes** |
| non-ASCII subset only | 3 | True | True | no — vacuous |
| the set I hand-listed in pass 1 | 10 | **False** | False | no — **false-fails the correct fix** |

The mechanism is stated and it is the right one: **the glyphs the mutation destroys are ASCII
letters** contributed by pill titles, so a non-ASCII set discriminates nothing, and the pre-change
radial set is `abcdefilmnoprstz·◆●` — only three of nineteen non-ASCII. `count > 0` passes the mutant
(glyphs are emitted); `pre_set ⊆ post_set` fails it (card glyphs vanish). The complementary mutant
`M-CNV.2-b` (braille only in already-blank cells) passes **correctly**, which is the control that
stops the arm being merely strict.

**My prescription in pass 1 was wrong and would have blocked the correct fix.** The fold caught it by
execution. Limb (b) is closed.

---

## 5 · C-18 and C-21

### 5.1 C-21 — the cut against the changed `AT` set

Set 2 added `AT-048` and split out `AT-007b`, `AT-025b`, `AT-034b`. C-21: a cut written before the
`AT` set changed is stale. Executed mapping of every `Acceptance:` line to its §3 section header:

```
AT-003 AT-004 AT-005 AT-006                          -> §3.2  Inc-1
AT-007 AT-007b AT-008 AT-010                         -> §3.3  "Inc-1 and Inc-2"   <-- ambiguous
AT-011 AT-012 AT-013 AT-014 AT-015 AT-016 AT-017
AT-046 AT-047                                        -> §3.4  Inc-3
AT-018 AT-019 AT-020 AT-021 AT-022 AT-023 AT-024     -> §3.5  Inc-4
AT-025 AT-025b AT-026 AT-029 AT-030 AT-048           -> §3.6  Inc-6
AT-032 AT-033 AT-034 AT-034b AT-035 AT-036 AT-037
AT-038 AT-039                                        -> §3.7  Inc-5
AT-041 AT-042 AT-043 AT-044                          -> §3.8  Inc-7
AT-009 AT-031 AT-040                                 -> NO OWNING REQUIREMENT, NO INCREMENT
```

**Four C-21 findings:**

1. **Three ids have no owning increment** because they have no owning requirement — `AT-009`,
   `AT-031`, `AT-040`. Folded into QA2-C-01.
2. **`AT-048` / `HLR-N13.3`: the two documents disagree.** `HLR-N13.3`'s own text says *"it is a
   security blocker and **it gates Inc-6**"*, and §3.6's header is Inc-6. **`PLAN.md` §13.4's table
   says Inc **7** gains S-03 — `HLR-N13.3` and `LLR-N13.1.5`.** §13.4 predates set 2. The
   requirements are internally consistent; the cut is the outlier.
3. **§3's labels describe seven increments against a nine-increment cut.** `PLAN.md` §13.4 keeps
   Inc-8 (*"reduced to the glyph vocabulary only"* = `HLR-N16.2` / `AT-043`) and Inc-9 (*"closes
   `factory.py:104`"* = `LLR-S06.3.2`). Those requirements sit under §3.8 *(Inc-7)* and §3.2
   *(Inc-1)* respectively. **No `AT` in the document resolves to Inc-8 or Inc-9.**
4. **`AT-007` and `AT-007b` share one *"Inc-1 and Inc-2"* label** — the split that `A-37` made
   precisely because they are two different chains has not produced two different increments.

**Every new and split `AT` does have an owning increment** — the answer to the question as put is
yes for `AT-007b`, `AT-025b`, `AT-034b` and `AT-048`. But the mapping is derived from section
headers, not declared per `AT`, and it disagrees with the cut in two places. → **QA2-C-06**.

### 5.2 C-18 — realisable as exactly ONE on-disk node?

| `AT` | Concern | Verdict |
|---|---|---|
| `AT-025` / `AT-025b` | Split: happy path vs a poisoned workspace | **resolved** by `A-37` |
| `AT-007` / `AT-007b` | Split: `Canvas` unit vs `RadialRenderer` render chain | **resolved**; increment label still shared |
| `AT-034` / `AT-034b` | Split: two LLRs, two methods | **resolved**; `AT-034b` now spans `LLR-N14.1.4` and `LLR-N14.1.3`, **both `test (unit)`** — one node is realisable |
| `AT-005` / `AT-006` | Claimed by `HLR-S06.3` **and** `LLR-S06.3.1`, `.3.3`, `.3.4`, `.3.5` — five requirements | **realisable** (all one derived census, one `test (unit)` node) but **not addressed**; recorded, not raised |
| `AT-009`, `AT-031`, `AT-040` | No requirement, no method, no increment | **not realisable as declared** → QA2-C-01 |
| `AT-041` … `AT-044` | Legend ATs | **resolved** — Pilot sizes read from `WIDE_SIZES` / `NARROW_SIZE` rather than re-typed |
| **`LLR-STO.1.1`** | **A requirement id, not an `AT`** — referenced normatively (*"`LLR-STO.1.1` **shall** carry the five-exception-type arm"*, and *"a bomb under `nodes:` … belongs in `LLR-STO.1.1`'s fixture set"*) with **no heading anywhere in the document**. Four occurrences, all prose. `LLR-N13.1.5` — the `C-3` security containment — is written to depend on it. | **DANGLING** → QA2-C-03. Note the document itself records that `V21` resolves owners against **headings** only, so a bullet-declared id resolves to nothing — the fold learned this for `LLR-R04.1` and then reproduced it here. |

### 5.3 The A3 blast radius, re-derived at `d877784` (QA2-C-02)

```
$ grep -rn "\.render(" tests/ mapper/ --include=*.py | wc -l      -> 48
$ grep -rln "\.render(" tests/ mapper/ --include=*.py | wc -l     -> 17
$ grep -rln "\.render(" tests/ --include=*.py | wc -l             -> 15

tests/  test_app 2 · test_attachments 3 · test_components 1 · test_export 1 · test_inspector 6 ·
        test_lane 3 · test_layered 2 · test_legacy_fixture 1 · test_outline 1 · test_palette 1 ·
        test_radial 1 · test_rail 3 · test_repair_cycles 2 · test_repair_depth 16 ·
        test_worklist_safety 1                                    -> 44 sites / 15 files
mapper/ app.py 3 · widgets/rail.py 1                              ->  4 sites /  2 files
```

**Three generations of the same number:** `PLAN.md` §5 B1 says **7 test files**; §9 C-1 corrects it to
**29 sites / 14 files** (measured at the parked base); executed now, **48 sites / 17 files, 15 test
files**. The repair batch added `test_repair_depth.py` (16 sites) and `test_repair_cycles.py` (2),
which nobody re-counted. `R-1`'s row — *"Extending `render` across 6 definitions and 3 call sites plus
7 test files is the batch's largest blast radius"* — is unchanged and now understates by 8 files.
This matters because **Inc-2's gate is byte-identical renderer output** across exactly these sites.

---

## 6 · Evidence checklist

| | Item | Evidence (re-runnable) |
|---|---|---|
| ✗ | Acceptance criteria use Given/When/Then | **By design, and accepted** — the batch uses EARS (`While … the system shall …`), the ISO 29148 register this project standardised on. Recorded rather than waved through, as in pass 1. |
| ✓ | Test cases have explicit Expected, not vague "works" | 79 `TC` rows in §5.2's functional table, each with a method and a numeric threshold; verified by the script in §3 (`TC in body but not in 5.2 table: []`). The eight thresholds pass 1 called weaker than their statement are individually closed (`QA-B-01`, `QA-B-02`, `QA-B-06`, `QA-B-07`, `QA-M-01`, `QA-M-03`, `QA-M-08`). |
| ✓ | Edge cases include empty, boundary, invalid, error | `US-N06`'s empty cell split into zero-hidden and 0-node (`A-34`, re-read at §3.4's catalog); `LLR-N13.1.5` supplies the error case; `LLR-N14.1.4` the empty/whitespace query; `§3.0 COERCION_RANGES` the invalid input across four thresholds. |
| ✓ | Regression checklist exists | `LLR-N14.3.2` retained verbatim as a standing guard re-run after Inc-4/6/9 (`C-D6b`); `LLR-N06.2.1` enumerates the two predicted-red `toggle` call sites by line; §5.3 criterion 6 asserts the A3 census. **Its sizing is stale** → QA2-C-02. |
| ✓ | Exit criteria stated | §5.3, six criteria; criterion 5's counterfactual list grew from 4 to **10**, each a plausible wrong implementation with a named mutant. **One stale id**: it names `AT-007` for the containment arm `AT-007b` owns → QA2-C-08. |
| ✓ | No real PII / secrets | Fixtures only (`anidado` node names are Spanish common nouns; `legacy` names were already tracked in `fixtures/legacy_nodos.yml`). No credentials in any probe. Working tree confirmed clean under `mapper/` and `tests/`. |
| ✓ | Test results left blank for the human | §5.2 reads `pending Phase 4` in every behavioral row; nothing in this review marks an unrun test as passed. The 51 `V2` blocks are correctly red pre-implementation and are reported as such, not as failures. |
| ✓ | **Layer B (black-box) through the shipped surface** | The three pass-1 failures are closed: the export artifact is now read **from disk** by code-point scan (`LLR-CNV.2.1`); the legend panel is read through the region-clipped `_painted_bindings` with a negative control; the overflow declaration is read from the **composited frame** via `_rows_in`, explicitly not `render().plain` and explicitly not the layout map. **One declared residual**: `LLR-N06.3.2`'s arithmetic is not yet observed through the screen, and §6.2 item 5 says so in those words. |
| ✓ | **Bidirectional surface-reachability** | Input side: every affected `AT` now drives a real key after `A-26` folds the five rulings; `HLR-N07.3`'s chord-agnostic sentence is gone. Output side: both pass-1 proxies (export artifact, legend panel) are now observed through the shipped surface. **Trace-link gap**: `AT-009` — the export deliverable — reaches no `Acceptance:` line, so the output is observable but not traceable → QA2-C-01. |
| ✗ | **No unfilled template** | The phase ran — there are no `<...>` placeholders and no empty required rows; every `TC` has a method and a threshold. **But the document's own derivation does not hold on itself**: 6 live ids fail the three-way intersection §5.2 mandates, and `A-29` asserts one promotion that is not in the text. → QA2-C-01. |
| ✓ | No control bytes written | This file byte-scanned before write; probe scripts in the session scratchpad only; `git status` shows only `.dev-flow/state.json` modified plus the untracked batch directory; nothing under `mapper/` or `tests/` touched. |

---

## 7 · What PDR should note

**The three things worth carrying out of this pass, in order of consequence:**

1. **The fold's blind spot is the lane boundary, not its own text.** Both dropped findings
   (`QA-M-02`, `QA-N-08`) target `PLAN.md`. `A-41` explicitly deflects three more minors to
   `PLAN.md`'s lane under C-44 — which is correct handling — but nothing then closes the loop, and
   `PLAN.md`'s own corrections were recorded in §9 without editing the rows a reader hits first
   (B1, P-19, R-1). **A finding deflected to another lane needs a receipt from that lane.**
2. **A derived count delegated to a sibling artifact is a typed count with extra steps.** §5.2 was
   right to stop typing `47`; naming `01d` as the authority reintroduced exactly the staleness the
   derivation removes, and `01d`'s `44` now matches none of the three sets. Compute it in place.
3. **The batch's own new rule found a defect class my pass 1 could not see.** `AT-046` and `AT-047`
   fail the intersection from the story-list side, a direction `QA-B-03` never tested. The rule is
   good; it now has to be run.

**Nothing in this pass asks for a new test.** All eight conditions are document edits, and every
number they need is already executed above.
