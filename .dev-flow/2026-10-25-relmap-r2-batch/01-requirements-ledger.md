# Requirements ledger — mapper — Batch 2026-10-25-relmap-r2-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

> Batch convention (adopted at P0 from the R1 post-mortem control C-3, carried as B-156):
> the live contract keeps the statements (US/HLR/LLR with ids, premise table, IFC); AT
> bodies and the AT↔requirement matrix live in `01b-acceptance-design.md`; this ledger
> carries amendments, rulings, mutants and measurement transcripts.


---

## P1 amendment — 2026-10-25 (P2 first-pass return edge)

Fold-back of the P2 cross-review findings (`02-review.md` + `evidence/p2-*.md`, gate
`iterate-to-refine`). Every entry names its requirement, asserting test and mutant; the
contract's `**Ledger:**` fields point back. Record-only sections (non-LED headings) carry
the measurements and probe transcripts.

### LED-2026-10-25-r2.01 — By-kind toggle SHIPS (QA-04 / F-UX-1 ruling fold-back)

- **Requirement:** LLR-RVG.1.5, LLR-RVH.4.1
- **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned) + AT-136 on the real screen;
  `tests/test_keymap.py` (additive SCOPE_RELMAP conformance, binds `k`)
- **Mutants:** M-RVG-7 (bands sorted by row count → RED); M-RVH-9 (a second binding on one
  chord in the scope → RED)

The standing orchestrator ruling (by-kind toggle ships: LLR-RVG.1.5 + `k`) is folded back
into every site that still presented it as open: the LLR-RVG.1.5 header drops
"(CONTINGENT on the PDR; drafted for the design review to rule in or out)" and its
statement names `k`; LLR-RVH.4.1 binds `k` unconditionally; AT-136 and the AT↔requirement
matrix drop the "(contingent) / dropped otherwise" wording; the IFC gaps-flow note and the
§6.3 open risk read SHIPPED. The PDR freeze is narrowed to the glyph/table details only.

### LED-2026-10-25-r2.02 — Hook per-line bound ruled at 240 + no-mid-spelling cut (QA-04 / QA-05 / SEC-1)

- **Requirement:** HLR-RVU.1, LLR-RVU.1.1
- **Asserting tests:** `tests/test_hook_line_bound.py` (planned) + AT-152; the R1 audit suite
  (`tests/test_reqharness_audit.py`) green unchanged
- **Mutants:** M-RVU-1 (cut before escaping → miscounted line); M-RVU-2 (cut re-exposes
  `verdict: ` → prefix-exclusivity arm RED); M-RVU-3 (cut inside an escape spelling instead
  of backing to its start → the AT-152 straddling-payload arm RED)

The bound value 240 and the C-42 order (cut after escaping, predicate over the EMITTED
form) are rulings, not PDR questions: HLR-RVU.1 and LLR-RVU.1.1 pin 240 with the cut at
239, and the ruling's "cut AFTER escaping so an escaped spelling is not sliced
mid-sequence" clause is stated verbatim — the cut shall back to the spelling start when the
boundary lands inside a `\xNN` or `\uXXXX` spelling. AT-152 pins the numeric oracle
(emitted line length ≤ 240) and gains the straddling-payload arm. The PDR freezes only the
ellipsis glyph.

### LED-2026-10-25-r2.03 — Workspace-as-repo canon rule (QA-03; executed probe)

- **Requirement:** LLR-RVH.3.1, LLR-RVH.3.3
- **Asserting tests:** `tests/test_relmap_shell.py` + the AT-147 workspace-as-repo arm
  (fixture workspace that is NOT a git repo; missing-canon boundary)
- **Mutants:** M-RVH-16 (make the screen derivation consult `.git` / require a repository →
  the non-repo fixture arm fails); M-RVH-17 (let the raw exception escape on a missing canon
  instead of the closed-set cause → the app-lives arm RED)

Rule adopted (probe `evidence/p2-seam-workspace-repo.md`, run 2026-10-25): the
descriptor/canon resolves RELATIVE TO THE WORKSPACE ROOT — `Path(workspace)/"REQUIREMENTS.md"`
(`mapper/relmap/adapter.py:129`), flat `os.listdir(workspace)` discovery
(`mapper/relmap/descriptor.py:200-208`) — git is never consulted on this path (a bare dir,
an empty `.git`, and a real `git init` workspace derive byte-identically), and a missing
canon yields the closed-set `CanonUnavailable` cause (K3 `file not found`) which the shell
renders as the `unavailable` refusal state — never a crash. Probe caveat recorded: the
R1-frozen `--audit` CLI hook IS git-gated (`structure: unavailable (no repository)`,
`mapper/reqharness/audit.py:378-379`, base = the git toplevel) — that is the RVU/D4 surface
and is explicitly out of this LLR's scope. LLR-RVH.3.3 is NEW (the census 51 → 52).

### LED-2026-10-25-r2.04 — LLR-RVS.7.1 re-trace (QA-08)

- **Requirement:** LLR-RVS.7.1
- **Asserting tests:** `tests/test_relmap_sheet.py` (the `osopen` AST/grep census)
- **Mutants:** M-RVS-13 — any later `osopen` import/attachment construction in
  `screens/relmap/sheet.py` (or `base.py`) turns the census RED (the census itself is the
  declared negative control)

Re-traced from HLR-RVS.2 to HLR-RVH.2 — the read-only posture substance belongs to the
shell family. Cosmetic, as the reviewer noted; the pairing is what keeps it honest.

### LED-2026-10-25-r2.05 — WARN tone scope clause (F-UX-2)

- **Requirement:** LLR-RVG.1.3, LLR-RVS.2.3
- **Asserting tests:** `tests/test_relmap_gaps_view.py`, `tests/test_relmap_sheet.py` (token
  census arms); AT-135 / AT-144 render arms
- **Mutants:** M-RVG-14 (severity token MED→WARN, or WARN on any tally word/chip → the
  token-census arm RED)

The ruling "WARN reserved to the lens gauge" is SCOPED, not dropped: WARN carries
reach/severity-attention semantics only, and exactly three signals hold it — the matrix
lens reach gauge, the `not computed` state (both LLR-RVM.2.2) and the sheet's tagged-binds
`◐` glyph (LLR-RVS.2.3). No tally word, chip or other chrome uses WARN. Both contract
sites and the PLAN OQ-G2 decision row now read consistently.

### LED-2026-10-25-r2.06 — Cut-before-coercion clause on the sink LLRs (SEC-3)

- **Requirement:** LLR-RVM.4.2, LLR-RVG.3.1, LLR-RVS.5.1
- **Asserting tests:** the unit arms of `tests/test_relmap_matrix.py`,
  `tests/test_relmap_gaps_view.py`, `tests/test_relmap_sheet.py`; the hostile arms of
  AT-134 / AT-139 / AT-144 on the live surface
- **Mutants:** M-RVM-11 (raw canon text in a markup sink); M-RVG-12 (remove the `plain()`
  pass); M-RVG-13 (markup-parsing sink); M-RVS-1 family — all already declared, all RED

One line added to each sink LLR's draft-time verification: width cuts apply to the COERCED
string; coercion is never applied to a previously fitted label (the C-10 order). The cited
mechanisms already make desync impossible (adapter pre-cut at 120, `fit` measures
post-coercion only) — this names the order so a future renderer cannot regress it silently.

### LED-2026-10-25-r2.07 — AT-driver seam discharged (QA-02; executed probe)

- **Requirement:** US-RMV-001 (named as the representative view story; the seam serves
  AT-130…149 across US-RMV-001…004)
- **Asserting tests:** every view AT (AT-130…149) drives the real surface through the
  injection point below; the precedent idiom is `tests/test_colour_always_on.py:64-70`
- **Mutants:** C-16 is the control — an AT driving a proxy (`.focus()` instead of real
  keys, or an internal symbol instead of the rendered surface) is RED by definition

The seam once flagged `assumed — verify in Phase 2` is PROBED on today's code
(`evidence/p2-seam-at-driver.md`, 2026-10-25, exit 0): the fixture-workspace injection
point is the `MapperApp(workspace=…)` constructor argument (`mapper/app.py:250`, consumed
at `:256` into `MapStore(workspace)`), driven by a headless `run_test()` pilot; a bare tmp
workspace holding only `<name>.mmd` + `<name>_nodos.yml` (`mapper/store.py:763`) reaches
`HomeScreen` and lists the relation row in `#home-recents`. F-5 now names the injection
point and requires lanes 3–5 to re-verify it at entry, not only at the join.

### LED-2026-10-25-r2.08 — Keymap seat scope moves to trunk Inc-2 (ARC-02)

- **Requirement:** LLR-RVH.4.1, LLR-RVH.4.2
- **Asserting tests:** `tests/test_keymap.py` (new, additive SCOPE_RELMAP conformance);
  `tests/test_relmap_shell.py` (BINDINGS == seat, keybar from the seat)
- **Mutants:** M-RVH-9 (duplicate chord); M-RVH-10 (a hand-written binding on the screen
  outside the seat → seat-equality RED)

`mapper/keymap.py` moves from the parallel shell lane into trunk Inc-2: Inc-2 =
`screens/relmap/{__init__,screen,base}.py` + `keymap.py` (4 files, the ≤4 budget holds);
Inc-6 keeps `home.py` + `app.py` (2) and re-pins the `tests/test_inc9c.py` LEAK_EXCEPTIONS
line-pin in the same increment. Fork preconditions re-checked: F-2 stands (the PDR seal is
still the lane-entry condition); F-3's ownership text is amended (seat scope is trunk-owned)
and the §6 worksheet intersections stay empty — shell ∩ renderers = { } with keymap removed
from the shell lane. Rationale: `RelMapScreen` cannot generate `BINDINGS`
(`screen_bindings(SCOPE_RELMAP)`) until the scope exists, so a lane-parallel keymap voided
F-2/F-3; ARCHITECTURE §4's KEYMAP row now reads "lands whole in trunk Inc-2".

### LED-2026-10-25-r2.09 — Cap-scale arm at the shipped 100,000-node cap (SEC-2 / QA-07)

- **Requirement:** LLR-RVM.1.1, LLR-RVS.6.2
- **Asserting tests:** `tests/test_relmap_scalecheck.py` (the R2 sweep) + the AT-137
  cap-scale arm; §2.5 assumption A5 records the deliberate coverage
- **Mutants:** M-RVM-1 (drop row windowing — at cap scale the windowed-render assertion
  goes RED); M-RVS-12 (drop rows past the viewport with no counted line → RED)

One cap-scale arm (in-test `build_map` at `MAX_NODES`, `mapper/osopen.py:93-94`) asserts
the matrix row window stays declared and bounded, the sheet's counted overflow line is
present, and the open/`r` derivation completes within a bounded wall-clock budget recorded
at Phase 3 (generous bound: 10× the 303-node skeleton baseline). No new HLR: the windowing
HLRs already bound per-render work in words — this is the missing exercised arm at the cap.

### LED-2026-10-25-r2.10 — Dimming and overflow arms promoted to the real screen (QA-06)

- **Requirement:** LLR-RVM.2.3, LLR-RVS.6.2
- **Asserting tests:** AT-131 / AT-132 (FAINT census on the painted frame: dimmed labels
  outside the 2-neighbourhood, none inside); AT-141 / AT-143 (the counted `… +NN more`
  line asserted at (118, 34) and (87, 34))
- **Mutants:** M-RVM-6 (`neighbourhood` called per painted row → counting wrapper RED);
  M-RVS-12 (rows dropped silently → RED)

Both operator-visible behaviours had unit coverage only; each gains one black-box
assertion on the real Textual surface, as the reviewer recommended.

### LED-2026-10-25-r2.11 — C-26 enumeration and the M-RVT-2 path (ARC-04)

- **Requirement:** LLR-RVT.1.2
- **Asserting tests:** the three re-pointed R1 files, now named in PLAN Inc-1 —
  `tests/test_relmap_model.py:17-26` (`cut` + `DISPLAY_MAX`),
  `tests/test_relmap_descriptor.py:38` (`refusal_line`),
  `tests/test_relmap_audit.py:33-35` (`refusal_line` + `cut`); plus
  `tests/test_relmap_text.py` (planned) and the reader census
- **Mutants:** M-RVT-2 — reworded: one test still importing `refusal_line` from the live
  old path `mapper.relmap.descriptor` (the negative control previously named
  `relmap.audit`, a path no test uses) → the census RED

Enumeration gap, not a coverage hole: coverage was intact via LLR-RVT.1.2 + the reader
census; the three files are now named in the Inc-1 test ledger.

---

## P1 amendment — 2026-10-25 (P2 second-pass return edge)

Fold-back of the P2 second-pass findings (`02-review.md` second-pass section +
`evidence/p2-pass2-*.md`, gate `iterate-to-refine`). Same C11 naming as the first pass; the
contract's `**Ledger:**` fields point back. The IFC syntax fix (P2V-1) and the matrix
negative-arms catch-up (P2Q-2) are record sections below — they move no requirement owner.

### LED-2026-10-25-r2.12 — `k` chord bound in LLR-RVH.4.1's normative Statement (P2Q-1 / P2U-1)

- **Requirement:** LLR-RVH.4.1
- **Asserting tests:** `tests/test_keymap.py` (additive SCOPE_RELMAP conformance, binds `k`);
  AT-136 on the real screen
- **Mutants:** M-RVH-9 (a second binding on one chord in the scope → uniqueness conformance
  RED); M-RVG-7 (bands sorted by row count instead of catalogue order → RED)

The second pass caught — by QA and UX independent convergence — that the first-pass
amendment de-contingented every by-kind site EXCEPT the normative Statement of LLR-RVH.4.1,
whose exhaustive "bind exactly" enumeration still omitted `k` (the binding lived only in the
non-normative draft-time verification). An implementer following the Statement alone would
ship a seat without `k` and AT-136 would RED at Phase 4. Fix: the Statement's chord list now
binds "`k` to the by-kind grouping toggle"; the draft-time duplicate assertion is removed
(the binding is normative now — the draft-time slot keeps only the trunk-increment / ARC-02
ownership note). The cross-references at LLR-RVG.1.5 (`:552`), §6.3 and AT-136 (`01b:105`),
which already claimed `k` is pinned here, are now true.

### LED-2026-10-25-r2.13 — RVT landing-order residual flag resolved as a decided rule (P2Q-3)

- **Requirement:** LLR-RVG.3.1
- **Asserting tests:** `tests/test_relmap_gaps_view.py` (planned); `tests/test_relmap_isolation.py`
  re-counted
- **Mutants:** M-RVG-12 (remove the `plain()` pass) — the sink's existing negative control;
  the landing order itself is fork-precondition territory (F-series), not a new mutant

The last residual `assumed — verify in Phase 2` flag (RVT text-leaf landing order,
`01-requirements.md:584`) is resolved with the decided rule already pinned at PLAN.md Inc-1:
the leaf lands in trunk Inc-1, FIRST, before any renderer lane forks, so every renderer
consumes the frozen leaf names from the start and never imports a not-yet-existing module.
The flag is replaced by the rule; its sibling flags were already discharged as executed
probes (`LED-2026-10-25-r2.03` / `-r2.07`).

---

## Amendment record — IFC FLOW NODES re-expressed in the template item form (P2V-1) + matrix negative-arms caught up (P2Q-2)

**P2V-1 (blocker, validator V10).** At station P2 the validator reported six blocks — every
IFC FLOW block "has no node parsed" (`01-requirements.md` IFC Part A) — because the NODES
lines listed transforms in arrow form (`<transform> -> LLR-x.y`) instead of the template's
`- fn : <name>` items with their own `owner : <LLR>` lines (`templates/ifc-template.md` §1).
Invisible until P2: V10's "past Phase 1" condition does not fire while `state.json` declares
`current_station: P1` (the first-pass "gate re-run 0 block" was measured there) — the same
blind spot the first pass documented for VAL-01/02. All six FLOW blocks are re-expressed:
each transform is a `- fn` item with its own `owner : <LLR>` line, and the combined owners
(`LLR-RVM.1.1/.1.3`, `LLR-RVM.2.1/.2.2`, `LLR-RVG.1.2/.1.3/.1.4`, `LLR-RVG.2.1/.2.2`,
`LLR-RVS.2.1/.2.2/.2.3`, `LLR-RVS.3.1/.3.2/.3.3`, `LLR-RVS.6.1/.6.2`, `LLR-RVH.1.1/.1.2/.1.3`,
`LLR-RVH.2.1/.2.2/.2.3`, `LLR-RVH.3.1/.3.2`, `LLR-RVH.4.1/.4.2/.4.4`, `LLR-RVT.1.1/.1.2/.1.3`)
are split one node per owner, per the template's "one owner per node" rule. No owner→LLR
mapping changed — the arrow owners are preserved verbatim, only the syntax moved. Re-run at
P2: `0 block`.

**P2Q-2 (low).** The AT↔requirement matrix negative-arms column caught up to the amended AT
bodies: the AT-152 row now names `M-RVU-1/2/3` (the body asserts the straddling-payload arm)
and the AT-137 row now names `M-RVG-5/6, M-RVM-1` (the cap-scale arm). The AT bodies remain
authoritative; both mutants already carry their own ledger entries (`-r2.02`, `-r2.09`).

---

## Measurement — requirement census re-count (ARC-01 / QA-01), id LED-2026-10-25-r2-census

Executed 2026-10-25 in the worktree, AFTER the amendment edits (the pre-amendment artifact
held 20 HLR / 51 LLR and the contract claimed 26/52 — the "lost" six HLRs and one LLR never
existed; the swarm merge carried a stale count):

```
$ grep -c '^### HLR-' .dev-flow/2026-10-25-relmap-r2-batch/01-requirements.md   -> 20
$ grep -c '^### LLR-' .dev-flow/2026-10-25-relmap-r2-batch/01-requirements.md   -> 52
$ grep -c '^#### US-'  .dev-flow/2026-10-25-relmap-r2-batch/01-requirements.md   -> 6
$ grep -c '^## AT-1'   .dev-flow/2026-10-25-relmap-r2-batch/01b-acceptance-design.md -> 23
$ for fam in RVM RVG RVS RVH RVT RVU; do grep -c "^### LLR-$fam" ...; done
  RVM 10 · RVG 9 · RVS 14 · RVH 15 · RVT 3 · RVU 1   (sum 52; RVH = 14 + new LLR-RVH.3.3)
```

Every count statement now reads 20 HLR / 52 LLR / 23 AT / 27 TC: contract §5.2 criterion 1
(cited above), PLAN header + roadmap. §5.2 criterion 1 ("All 52 LLRs carry at least one
asserting on-disk test") is now satisfiable as written — 52/52 LLRs carry `Asserting tests`.

## Amendment record — IFC FLOW syntax (VAL-01 / VAL-02)

All six IFC Part A openers carried the missing colon (`FLOW rm-…` vs the template's
`FLOW: <id>`); the validator surfaced two as blocks past Phase 1 (`01-requirements.md:843,
851` at review time). All six are normalized to `FLOW: <id>` (the `(matrix)` / `(shell)` /
`(RVT)` / `(RVU)` parentheticals are retained after the id). Re-run: `0 block` — see the
P1 gate record in PLAN §Gate notices.

## Record — seam probe transcripts

- `evidence/p2-seam-at-driver.md` — AT-driver host push + fixture-workspace injection
  (QA-02 / LED-2026-10-25-r2.07): PASS on today's code; paths sanitized; neutral fixture
  names.
- `evidence/p2-seam-workspace-repo.md` — workspace-as-repo canon derivation (QA-03 /
  LED-2026-10-25-r2.03): rule verified, caveat (the `--audit` hook's git gating) recorded;
  paths sanitized.

## Record — lane fixture policy (ARC-05)

Declared in PLAN §Roadmap: renderer lanes build synthetic `build_map` maps INLINE per test
file (R1 style); shared fixture modules (`tests/_relmap_fixtures.py`) are trunk-only — two
lanes never append to one shared fixture file, so the crossed reverse census cannot be
silently violated.

---

## PDR seal amendments — 2026-10-25 (station P3, author-artifact conditions)

The PDR sealed `approved with conditions` (`design/PDR-2026-10-25-relmap-r2-batch.md`, §B
table); the conditions whose amendment lands in the author artifacts at the seal are applied
in this records-only unit. Same C11 naming; the contract's `**Ledger:**` fields point back.

### LED-2026-10-25-r2.14 — The frozen seam is `_row_text`/`fit`; LF + TAB join P12 (F-SEC-1 / COND-SEC-1)

- **Requirement:** LLR-RVH.5.2 (the seam wording); premise P12 (the hostile vocabulary);
  AT-134 / AT-148 hostile arms (`01b-acceptance-design.md`)
- **Asserting tests:** the AT-134 LF/TAB one-row arm; the AT-148 hostile arm (LF/TAB payload)
  — both planned, executed with lanes 3/4/5 per the condition
- **Mutants:** M-RVH-18 (a sink lets LF/TAB through as row breaks instead of single spaces →
  the one-row assertion RED) — NEW, registered in LLR-RVH.5.2's negative control and the
  AT-134/AT-148 matrix rows

The security reviewer's probe showed bare `darkside.plain` preserves LF/TAB by design
(`mapper/darkside.py:550-561`), so naming `plain` as the one seam would institutionalise a
gap the hostile arms could not redden. The frozen seam is reworded everywhere it is named as
the assembly point: proposal §2 `base.py` row + §6 risk 2 + §4 frozen-set paragraph, the
`docs/ARCHITECTURE.md` `relmap screen` row, and the contract LLR-RVH.5.2 draft-time field —
as `_row_text`/`fit` (`plain` + LF/TAB/CR → single space, `mapper/darkside.py:576-621`).
LF + TAB join the P12 hostile vocabulary, and the AT-134/AT-148 arms gain the payload with
an embedded LF + TAB plus a "renders on ONE row" assertion. Coerce-then-cut order unchanged
(`LED-2026-10-25-r2.06`); `_row_text` composes `plain`, so the sink LLRs' `plain` wording
remains literally true as the first pass — what froze is the seam NAME, not a new mechanism.

### LED-2026-10-25-r2.15 — View-specific chords inert off their home view (F-UX-1 / COND-UX-1)

- **Requirement:** LLR-RVH.4.1 (Statement + negative control); the AT-148 out-of-view arm
- **Asserting tests:** the AT-148 out-of-view arm (off-home `enter`/`c`/`k` against a freshly
  painted frame) — planned, executed at the trunk Inc-2 gate
- **Mutants:** M-RVH-19 (a view-specific chord acting on a non-home view, or off-home state
  reachable) → the out-of-view arm RED — NEW, registered in LLR-RVH.4.1's negative control
  and the AT-148 matrix row

The seat binds `enter`/`c`/`k` scope-static; the design narrative never said what they do
outside their home view, and three lanes would each improvise. Declared (matching the
operator-approved static bar): inert no-op when the active view is not the chord's home
view — or at most a crumb-note flash — never acting on a non-home view; any richer answer is
a seat change and trunk-owned. Lands in the proposal §2 narrative, LLR-RVH.4.1's Statement
and the AT-148 arm.

### LED-2026-10-25-r2.16 — Inc-1 splits into Inc-1a + Inc-1b (F-ARCH-2 / F-QA-1 / COND-ARCH-2 / COND-QA-1, orchestrator ruling)

- **Requirement:** LLR-RVT.1.1, LLR-RVT.1.2 (draft-time/statement); PLAN.md, the proposal
  §2.1/§4/§5.1/§8 and `docs/ARCHITECTURE.md` §6 worksheet (the plan side)
- **Asserting tests:** `tests/test_relmap_text.py` (planned) + the reader census per
  increment; the byte-identity probe runs at EVERY step (AT-151 idiom)
- **Mutants:** M-RVT-1/2/3 (already registered) — the split changes WHO re-points WHEN, not
  the controls

Orchestrator ruling at the PDR seal (state.json decisions_log, station PDR, 2026-10-25):
with `mapper/relmap/adapter.py:29` counted, Inc-1 would hold 5 SOURCE files against the ≤4
budget, so it splits into Inc-1a — `text.py` (new) + the `model`/`descriptor`/`audit`
re-points (4) — and Inc-1b — the `adapter.py` re-point (1). Both trunk, before Inc-2. The
cut/`refusal_line` single-site move stays byte-identical at each step: after Inc-1a every
old path still resolves except the one declared reader (`adapter.py:29` importing `cut`
from `model`, re-pointed in Inc-1b); the per-increment reader census is zero over the paths
each increment re-points. The sealed record's "SOURCE becomes 5" resolution is SUPERSEDED
by this ruling (recorded in the PDR record §B/§D as a declared ruling annotation, not a
silent edit).

### LED-2026-10-25-r2.17 — The three census citations repaired (F-ARCH-3 / COND-ARCH-3, F-UX-3 / COND-UX-3)

- **Requirement:** LLR-RVH.4.1, LLR-RVH.4.4 (draft-time fields); premise P6 (carried the same
  stale `test_key_dispatch.py:137`); proposal §5.2 + §6 risk 3
- **Asserting tests:** none new — a citation repair; the pinned tests are unchanged
- **Mutants:** n/a (record-only repair)

Repaired, each verified against the files on disk 2026-10-25: `mapper/screens/palette.py:432`
(phantom — the file is 218 lines) → `mapper/keymap.py:432` (`palette_items`), keeping
`mapper/screens/palette.py:36`; keymap "uniqueness rule `:9-12`" → the rule comment `:25` +
`duplicate_chords()` `:445`; `tests/test_key_dispatch.py:137` (inside the EXPECTED data
table) → the whole-seat pin assertion `:170` (`test_at_n03h_the_whole_seat_matches_its_specification`).


### LED-2026-10-25-r2.18 — D1 amended at the trunk Inc-2 review pass: per-view cursor axis + per-view crumb word (independent review F1/F2, orchestrator ruling)

- **Requirement:** LLR-RVG.1.3, LLR-RVH.4.3; PDR `PDR-2026-10-25-relmap-r2-batch#D1`; AT-135/AT-137
- **Asserting tests:** `tests/test_relmap_shell.py` — the Inc-2 review arms
  (`test_review_f1_the_crumb_never_shows_another_views_state_word` at 118 and 87,
  `test_review_f2_the_cursor_clamps_at_the_last_row_without_wrapping`,
  `test_review_f2_each_view_keeps_its_own_cursor`,
  `test_review_f2_the_placeholder_has_no_rows_to_cursor_over`,
  `test_d1_freeze_text_names_the_full_toggle_vocabulary`) + the amended
  `test_d1_surface_names_are_frozen`
- **Mutants:** M-REV-3 (`_move_selection` gutted — survived the pre-review trio, KILLED ×4 by the
  new cursor arms) · M-FU-1 (clamp → wraparound, KILLED ×2 after the arm gained its
  mid-sequence assertion) · M-FU-2 (crumb shows any view's word, KILLED ×2); every restore
  sha256-verified (`evidence/p3-inc2f-mutants.txt`)

The independent review of trunk Inc-2 (`evidence/review-inc002.md`, verdict `iterate`,
BLOCK-UNTIL F1/F2) ruled two MAJORs trunk-owned and cheapest to discharge before lanes 3/4/5
fork. The orchestrator ruled the frozen D1 surface MAY be amended at trunk now (a declared D1
amendment, not a silent edit — recorded in the PDR record's §D D1 row as a ruling annotation,
per the D6 precedent):

- **F2 — the cursor axis.** The pre-amendment host moved one node-axis cursor with wraparound;
  the gaps lane's contract (RVG.1.3) is gap-row axis. Amended: the renderer protocol gains
  `row_count(state) -> int` — each view's own row axis (ranked-gap rows for gaps, the node list
  for matrix/sheet), `0` for `PendingView`; the host keeps ONE CURSOR PER VIEW, moves it within
  `[0, row_count)` for the ACTIVE view, **clamped at the ends, no wrap** (holding `down` stops
  at the last row), and passes that view's cursor in `ViewState.cursor`. RVG.1.3's statement now
  names the per-view axis and the clamp; AT-135's first fixture holds 3 HLRs with **two**
  childless (→ 2 gaps) so its driver's "cursor to row 02" exists (review F9); AT-137's driver
  names the clamp.
- **F1 — the crumb word.** The toggle-state word is stored PER VIEW; the crumb shows the ACTIVE
  view's own word — switching views never shows another view's word, and returning restores it.
  LLR-RVH.4.3's statement now pins the rule; arms reproduce the reviewer's live repro at 118
  and 87 (`k` on gaps → `1` → the crumb must NOT say `by kind`).
- **Minors in the same pass (review F3–F7, F10):** the dead `_VIEW_KEYS` constant and the dead
  `ViewState.lens` field drop (the matrix lens rides the `enter` toggle channel; the matrix
  crumb word is pinned as `panel lens`); the freeze docstring names the full kind vocabulary
  (`enter`/`c`/`k`, `by kind`, `direct only`/`stacked chain`, `panel lens`) and states the
  renderer's `notice` obligation. The `ViewState` name collision with the tree kind stays
  declared (review F8, accepted — no action).

### LED-2026-10-25-r2.19 — The mount-time canvas height is degenerate; renderers floor it with a default body (lanes L4/L5, increments 004/005)

- **Requirement:** LLR-RVG.1.4, LLR-RVS.6.1/.6.2 (the viewport budgets); the AT-130…144 driver bodies
- **Asserting tests:** `tests/test_relmap_gaps_view.py`, `tests/test_relmap_sheet.py`, `tests/test_relmap_scalecheck.py`
- **Mutants:** none (a renderer-side convention)

The shipped host's `#relmap-canvas` `Static` is auto-height, so the mount-time `ViewState.height`
is the degenerate 1. The renderer lanes treat an explicit `ViewState.height` as the budget and
paint an honest default body (24 rows) for the degenerate 1; a host stylesheet height is a trunk
candidate, not a lane change (F-3 held — zero host edits). Both lanes converged on the convention
independently; the joined sweep re-runs it at (118,34) and (87,34).

### LED-2026-10-25-r2.20 — The first-open crumb is wordless; the toggle word lands after the first home toggle (lanes L3/L4/L5; AT-135/140/141 amended at the join)

- **Requirement:** LLR-RVS.3.3, LLR-RVG.1.5, LLR-RVH.4.3; AT-135, AT-140, AT-141
- **Asserting tests:** `tests/test_relmap_gaps_view.py` (AT-136), `tests/test_relmap_sheet.py` (AT-140/141), `tests/test_relmap_matrix.py` (AT-131)
- **Mutants:** M-RVS-9 (the note/rows conjunct — KILLED), M-RVG-7 (KILLED)

The host stores the per-view toggle-state word only AFTER a toggle, so the first-open crumb reads
`name / relmap / view` and the word (`panel lens` / `by kind` / `direct only` / `stacked chain`)
lands after the first home-view toggle; the density IS declared on first open by each renderer's
own note/hint line. AT-140's Observable first sentence and AT-135's asserted crumb phrase were
amended at the join to the shipped channel (this unit) — the prototype's `gaps · reach count`
scene label is not the shipped crumb form.

### LED-2026-10-25-r2.21 — Matrix lens readings pinned: `lens width` = viewport width; the spent-budget row is the whole-word ` change <id>: not computed` (lane L3, increment 003; contract amended)

- **Requirement:** LLR-RVM.2.1, LLR-RVM.2.2
- **Asserting tests:** `tests/test_relmap_matrix.py` — `test_hop2_rows_fold_below_the_sixty_cell_viewport`, `test_reach_not_computed_renders_honestly`, the AT-131/AT-132 nodes
- **Mutants:** M-RVM-5, M-RVM-6, M-RVM-7 — all KILLED, restore sha256-proven (`evidence/p3-inc003-mutants.txt`)

LLR-RVM.2.1's "at lens widths below 60 cells" is pinned as the VIEWPORT width (`state.width`):
both shipped sizes (118/87 ≥ 60) keep the hop-2 rows, matching the operator-approved reference
renders; below 60 the rows fold with members counted `+NN more`. LLR-RVM.2.2's spent-budget
count renders on its own whole-word row ` change <id>: not computed` in WARN with an empty gauge
(the wordy `reaches N nodes` frame cuts the mandated words at the shipped panel widths); the
computed form is untouched. Both statements carry the appended clarification text (applied at the
join, this unit).

### LED-2026-10-25-r2.22 — WARN scope: the tagged-binds `◐` holds WARN in EVERY renderer (lane L3, increment 003; clarifies LED-2026-10-25-r2.05)

- **Requirement:** LLR-RVM.1.2, LLR-RVM.2.1 (the `◐` tone); LLR-RVS.2.3; LED-2026-10-25-r2.05
- **Asserting tests:** `tests/test_relmap_matrix.py` — the `◐`/`●` tone arm; `tests/test_relmap_sheet.py` — the evidence-glyph arm
- **Mutants:** M-RVM-3 (the evidence tone dropped — KILLED)

The matrix renderer paints the tagged-binds `◐` in WARN — the operator-approved prototype's tone
(`binds-glyphs.png`) and the tone M-RVM-3 assumes. r2.05's "exactly three signals" named the
sheet's `◐`; the ruling now covers every renderer that paints the glyph — one signal, one tone,
wherever it appears.

### LED-2026-10-25-r2.23 — M-RVM-4 numbering gap (record-only)

- **Requirement:** LLR-RVM.2.1 (the mutant-registry row the gap belongs to)
- **Asserting tests:** none
- **Mutants:** n/a

The matrix mutant row names M-RVM-1…M-RVM-11 but no batch artifact defines an M-RVM-4 (grep over
`.dev-flow/2026-10-25-relmap-r2-batch/`: zero hits). The L3 battery ran all ten defined mutants,
M-RVM-1 in both registered forms (windowing drop, declaration drop). A future batch may register
an M-RVM-4 or renumber M-RVM-5…11; the battery transcript records which arms ran.

### LED-2026-10-25-r2.24 — The gaps renderer re-issues the host ranking only for the not-computed count; painted order is `state.gaps` (lane L4, increment 004; contract annotated)

- **Requirement:** LLR-RVG.1.1
- **Asserting tests:** `tests/test_relmap_gaps_view.py` — the rendered-order arm
- **Mutants:** M-RVG-1 (re-sort by node id — KILLED)

LLR-RVG.1.1's "the gaps renderer shall obtain its rows by calling `detect_gaps` and `rank_gaps`"
predates the D1 freeze, under which the HOST ranks once and hands the ranked tuple via
`state.gaps`. The shipped renderer paints `state.gaps` order unchanged (never re-sorts — M-RVG-1
KILLED) and re-issues the host's own deterministic memoized ranking call solely to derive the
not-computed count the tuple does not carry. LLR-RVG.1.1 carries the non-normative annotation
(applied at the join, this unit).

### LED-2026-10-25-r2.25 — The reqharness change-flow graph is a DAG; cyclic arms run on hand-wired fixtures (lane L5, increment 005)

- **Requirement:** LLR-RVS.3.1, LLR-RVS.3.2; OQ-SHEET-5; M-RVS-8
- **Asserting tests:** `tests/test_relmap_sheet.py` — the diamond/cyclic stacked-marker arms
- **Mutants:** M-RVS-8 (BFS depth through both directions — KILLED)

`build_map`'s orientation (`mapper/relmap/model.py:293-301`) makes every profile-valid reqharness
map a DAG: up-reachable and down-reachable sets are disjoint, so OQ-SHEET-5's both-sections row
and the mixed-hop stacked marker cannot arise from `build_map` fixtures. The arms exercise
hand-wired cyclic `RelMap` objects (the `RelMap` constructor accepts arbitrary edges). The shipped
renderer honours both directions on any map; the fixtures, not the code, are DAG-bound.

### LED-2026-10-25-r2.26 — Inc-6 landed: Home lists relation maps beside tree maps; routing by kind; `app` re-exports `RelMapScreen` (lane L6, increment 006)

- **Requirement:** LLR-RVH.1.1, LLR-RVH.2.1, LLR-RVH.3.1, LLR-RVH.5.1, LLR-RVH.5.2 (the Inc-6 LLR set; the full family in the text below)
- **Asserting tests:** `tests/test_relmap_shell.py` — the 14 shell arms (AT-145/146/147 + boundaries)
- **Mutants:** M-RVH-1…M-RVH-7 — all KILLED, restore sha256-proven (`evidence/p3-inc006-mutants.txt`)

Home enumerates `*.relmap.yml` via `descriptor.discover_descriptors` beside `*.mmd` in one
name-sorted list; relation rows carry the `relation·reqharness` badge (`INK on STEP`); `↵` routes
by kind (`MapScreen` | `RelMapScreen`); the derived reqharness row appears at ZERO descriptors
while the default canon file is present (`LED-2026-10-25-r2.29`); `app` re-exports `RelMapScreen`
(the `MapScreen` pattern). COND-QA-4's shell half is discharged: the derivation-args/count
instrumentation WRAPS `derive_reqharness_map`, never replaces it.

### LED-2026-10-25-r2.27 — The relmap-importers census allows `screens/home.py` (lane L6, increment 006)

- **Requirement:** LLR-RVH.1.1 (the discovery door serves the Home enumeration)
- **Asserting tests:** `tests/test_relmap_isolation.py`
- **Mutants:** n/a

Home's enumeration reaches the D3 discovery door (`mapper.relmap.descriptor`'s read-only
`discover_descriptors` / `default_descriptor` / `DESCRIPTOR_SUFFIX`); the importers census now
allows `screens/home.py` beside `app.py`, enumerated by the failing census before its edit (the
packet's Correction population). `docs/ARCHITECTURE.md` §3 records the edge (amendment applied at
the join, this unit).

### LED-2026-10-25-r2.28 — The `test_inc9c.py` `LEAK_EXCEPTIONS` pin re-pinned 176 → 240 in the same increment (lane L6, increment 006)

- **Requirement:** LLR-RVH.5.1 (the refusal-path wording the leak census guards)
- **Asserting tests:** `tests/test_inc9c.py`
- **Mutants:** n/a

Inc-6 inserted code above the pinned `str(exc)` site in `mapper/screens/home.py`; the pin moved
176 → 240 and was re-pinned in the same increment, the comment updated, B-113 kept.

### LED-2026-10-25-r2.29 — The derived row requires the default canon present (lane L6, increment 006; contract clarified)

- **Requirement:** LLR-RVH.3.1; AT-145 boundary (a), AT-147 boundary (a)
- **Asserting tests:** `tests/test_relmap_shell.py` — the boundary arms
- **Mutants:** n/a

LLR-RVH.3.1 read literally would list a derived row in a workspace with no descriptor and no
canon — a row that can only refuse. The shipped Home lists the derived row only while the default
canon's file is present at the workspace root; a descriptor-less canon-less workspace lists tree
rows only. The contract statement and AT-147 boundary (a) carry the appended clarification
(applied at the join, this unit).

### LED-2026-10-25-r2.30 — Inc-7 gate amendment: the R1 snapshot's two over-bound gap lines are cut at the sink; content authority moves to the D5 `structure_lines` seam (trunk, increment 007)

- **Requirement:** LLR-RVU.1.1 (the amended arms — AT-125's snapshot limb and
  the R1 suite's `test_snapshot_run` — assert the LLR-RMU.1.2 sink surface;
  no LLR-RMU.1.2 pairing is claimed: r2.30 amends LLR-RVU.1.1 alone)
- **Asserting tests:** `tests/test_relmap_audit.py` — `test_at_125…` and `test_snapshot_run`, both re-derived in place (49 → 49 nodes); `tests/test_hook_line_bound.py` (7 nodes — AT-152, TC-RM-30)
- **Mutants:** M-RVU-1 (cut the RAW line before escaping → the escaped-form arm RED) · M-RVU-2 (the verdict rewrite moved BEFORE the cut → the F-SEC-3 order arm RED) · M-RVU-3 (the spelling back-off removed → the straddling arms RED) — all KILLED, restore sha256-proven (`evidence/p3-inc7-mutants.txt`)

The Inc-7 gate amendment (the PDR's risk-#6 contingency, executed): the R1
snapshot carries two gap lines of 271/277 cells whose tails the frozen
per-line bound 240 (`LED-2026-10-25-r2.02`) must cut; the R1 golden surfaces
fired exactly as the risk table predicted, and the premise check (P10/P11)
did not cover the longest `structure_lines` sentence.

**Before:** AT-125's snapshot limb and `test_snapshot_run` asserted the
qualifier content (`canon rows near this id could not be parsed or linked: N`)
on the emitted `--audit` lines.

**After:** the qualifier content is asserted on the D5 `structure_lines` seam
(unescaped by contract, unbounded by design); the emitted form is asserted
bounded (every `structure gap:` line ≤ 240 cells); block order and figures
unchanged.

**Deleted:** the whole-text reads of the two over-bound lines.

**New:** the seam reads + the ≤ 240 pins.

The re-derivation does not weaken either arm: the content assertions moved to
the layer that owns content, and the sink gained a bound assertion the arms
never had. The suite is green through the amended arms (48 passed, 1
skipped). The P10/P11 premise note in LLR-RVU.1.1's draft-time verification
is superseded in its measurement scope (it covered the refusal line (120) and
the report length (≈298 lines), not the longest `structure_lines` sentence —
the PDR's risk #6 carried exactly this contingency).

### LED-2026-10-25-r2.31 — P3 census amendment (C11 naming): the three whole-corpus census failures the closing full-suite run surfaced, repaired test-side (increments 003/005/002 retrospective)

- **Requirement:** HLR-RVM.1, HLR-RVS.1, HLR-RVH.4 (the requirements whose shipped renderer sites, sheet words and seat rows the three censuses now classify — each paired back in the live contract; the census requirements the amended tests assert — the hue-census totality family sealed in `2026-08-26-ui-next-batch-02` and the chrome/seat census nodes sealed in the Inc-9 record — are named here in prose only, so the pairing names nothing sealed)
- **Asserting tests:** `tests/test_darkside_census.py` — `test_hue_census_every_severity_and_busy_site_is_classified` (pin 82 → 94, the 12 new sites registered with per-site judgements); `tests/test_inc9.py` — `test_a112_the_chrome_is_english[seat]` (`CHROME_LEXICON` extended) and `test_cd25a_the_seat_diff_is_exactly_what_inc9_declares` (the 13 `relmap` rows declared in `DECLARED_ADDED`)
- **Mutants:** none — records-only unit; no product code touched, no test logic weakened (the census derives its input set from the tracked tree and the judgements are itemised in the register comment)

The orchestrator's clean full-suite run at the close of Phase 3 (`4223 passed, 3 failed`) surfaced three failures in whole-corpus census tests that no increment's guard set named — the same escape class the R1 batch recorded (its post-mortem's top "didn't": two whole-corpus guards sat outside every increment's targeted run, and R1's new control added `test_fold.py` + `tests/test_repair_artifact_claims.py` to the guard set). This batch repeated the escape with the NEXT layer of whole-corpus tests: `tests/test_darkside_census.py` and `tests/test_inc9.py`.

**Amendment 1 (the hue census, 82 → 94):** the 12 new severity/busy sites derive from `mapper/screens/relmap/{matrix,sheet}.py` (increments 003/005). Each is classified individually in the register, and each judgement is pinned by the batch's own requirement tests: the `!` verifies-missing-or-in-cycle glyph names ALERT (`_cell` + `_evidence_glyph` in matrix.py, the D5 table in sheet.py — three sites, two register keys); the `◐` binds-missing glyph names WARN (three sites, two keys); the open-node `○` gutter badge names ALERT (it cannot be bound shut as it stands; the closed sister branch is MUT, unadjudicated); the `╌╌╌ relates to nothing` lens hatch names ALERT (LLR-RVM.3.2, pinned by `test_relates_to_nothing_when_the_selection_is_isolated`); the two `not computed` reach words and the reach-gauge microbar fill name WARN (LLR-RVM.2.2, pinned by `test_reach_not_computed_renders_honestly`; outstanding attention with a quantity, the fold-pill count's precedent); the sheet's `! <kind> <sentence>` gap head names ALERT (a gap is a record that cannot proceed as it stands — the review screen's refusals' family). The pin moved to the derived value 94 in the same edit.

**Amendment 2 (A-112, the chrome lexicon):** the relmap seat's painted labels add ten English words — `by, chain, gaps, impact, kind, lens, matrix, on, refresh, sheet` (`impact on node`, `by kind`) — and the seat census also judges the six `r`-prefixed group handles (`rview, rnav, rlens, rchain, rkind, rleave`) whose prefix exists only to keep each group id claimable by exactly one scope (`mapper/keymap.py`); the unprefixed roots are all lexicon words already.

**Amendment 3 (CD-25a, the seat diff):** the 13 `relmap` scope rows are declared in `DECLARED_ADDED` — (`relmap`,`1`,`matrix`), (`relmap`,`2`,`gaps`), (`relmap`,`3`,`sheet`), (`relmap`,`r`,`refresh`), (`relmap`,`up`,`move_up`), (`relmap`,`down`,`move_down`), (`relmap`,`left`,`move_left`), (`relmap`,`right`,`move_right`), (`relmap`,`enter`,`lens`), (`relmap`,`c`,`chain`), (`relmap`,`k`,`by_kind`), (`relmap`,`q`,`leave`), (`relmap`,`escape`,`leave`) — per `mapper/keymap.py`; no home door (the screen is reached from the glob, not a door row).

**The lesson (control, adopted in this unit):** every increment's guard set must name the whole-corpus censuses, not only the fold/repair pair — `tests/test_darkside_census.py` and `tests/test_inc9.py` join `tests/test_fold.py` + `tests/test_repair_artifact_claims.py` in the PLAN's guard-set definition, and the post-mortem note for P5 is seeded in `05-postmortem.md`. A census that only the closing full-suite run can see fails three increments after the site it should have caught was painted.

### LED-2026-10-25-r2.32 — P5 records pass (C11 naming): COND-DDR-1 discharged — the drifted census citations re-repaired a third time, by content match

- **Requirement:** LLR-RVH.4.1, LLR-RVH.4.4 (the draft-time verification fields whose citation lines drifted — record-side repair only, no requirement Statement touched)
- **Asserting tests:** `tests/test_no_operator_paths.py` (the A-110 backstop, re-run on the STAGED tree after the edit per the adopted control) · `tests/test_repair_artifact_claims.py` (every cited path:line resolves)
- **Mutants:** none — records-only unit; no product or test code touched

The DDR re-opened COND-ARCH-3/COND-UX-3 as COND-DDR-1 (the P3 repair `75f9e28` drifted again before the lanes forked — trunk Inc-2 `8be99a3` shifted the cited lines). Discharge at the P5 close records pass, per the DDR §G disposition: every named site re-repaired BY CONTENT MATCH, each new line number re-read against the symbol it cites on this tree before the edit landed — `mapper/keymap.py:475` is `def palette_items`, `:488` is `def duplicate_chords()`, `tests/test_key_dispatch.py:189` is `def test_at_n03h_the_whole_seat_matches_its_specification` (the whole-seat pin). Sites (cited at their FINAL positions — the story `**Statement:**` lines the canon fold required inserted above the first three in the same records pass): `01-requirements.md:282` (premise P6; was `:255`, `:170` → `:189`), `01-requirements.md:812` (LLR-RVH.4.1 draft-time; was `:785`, `:445` → `:488`), `01-requirements.md:840` (LLR-RVH.4.4 draft-time; was `:813`, `:432` → `:475`); `design-proposal.md:254` (`:445` → `:488`, `:170` → `:189`), `:255` (`:432` → `:475`), and the same-drift site the DDR finding did not name, `design-proposal.md:304` (`:170` → `:189`, the §6 risk-3 row) — the extra site is recorded here so the repair is complete, not just compliant. The sealed PDR's condition text and the `LED-…-r2.17` entry keep their historical line numbers (a record of the repair as written then, not a live citation). Folded in the same pass per the DDR F-2/F-3 dispositions: §B rows 6/7 and §H D6 of the DDR now carry the as-built lane counts `4/1/4/1/1/1/2/0/1` (Inc-6b shipped 0 SOURCE) and the discharged wording-notice markers. The citation census's missing content anchor — the reason this is the THIRD hand repair of the same class — is recorded as BACKLOG **B-166** rather than a fourth hand pass over the `darkside.py:576-621` ranges.

### LED-2026-10-25-r2.33 — P5 records pass (C11 naming): COND-DDR-2 discharged — the two escaped-regression pre-fix REDs captured and stored

- **Requirement:** HLR-RVM.1, HLR-RVS.1, HLR-RVH.4 (the requirements whose shipped renderer sites, sheet words and seat rows the escaped census failures tripped — the evidence stored here is the pre-fix RED for their escaped-bug-regression rows in `04-validation.md`; the A-110 arm names no R2 requirement — it is the standing privacy control)
- **Asserting tests:** `evidence/p5-cond-ddr2-census-prefix-red-2026-10-26.txt` (the three census nodes on the pre-fix tree) · `evidence/p5-cond-ddr2-a110-prefix-red-2026-10-26.txt` (the A-110 privacy guard on the pre-redaction tree)
- **Mutants:** none — records-only unit; the captured runs are reproductions, no code touched

Discharge at the P5 close, per the DDR §G disposition (capture the two pre-fix REDs or record the accepted gap — the capture path was taken). Both runs executed on DETACHED SCRATCH CHECKOUTS created and removed under the unit's scratch directory outside the repository (no worktree state disturbed): ① the three census nodes — `tests/test_darkside_census.py::test_hue_census_every_severity_and_busy_site_is_classified`, `tests/test_inc9.py::test_a112_the_chrome_is_english[seat]`, `tests/test_inc9.py::test_cd25a_the_seat_diff_is_exactly_what_inc9_declares` — run at `2e83cf6^` (`1b3b151`, the tree before the census amendment): exactly the 3 named nodes fail (12 unclassified severity/busy sites; the seat words absent from `CHROME_LEXICON`; the 13 `relmap` rows absent from `DECLARED_ADDED`), 69 passed across the two census files; ② `tests/test_no_operator_paths.py` run at `cdc4491^` (`2e83cf6`, the tree whose committed census transcript still carried the account profile segment): the A-110 backstop fails on that transcript. Both transcripts were sanitized AT AUTHORING TIME by a Python filter that refuses to write on any account-profile segment (account name → `<user>`, the adopted control of G-002/B-164, never `sed`), re-scanned clean, and only then staged. The scratch checkouts were deleted after the captures; no stray file remains.
