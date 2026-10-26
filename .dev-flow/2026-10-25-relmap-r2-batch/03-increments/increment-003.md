# Increment 003 — HLR-RVM.1–4 · the traceability-matrix renderer (lane L3)

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `003` |
| Lane (if the batch forked) | L3 (matrix) · `mapper/screens/relmap/matrix.py` only — lanes L1/L2 (gaps/sheet) and the shell lane own their own files; no lane file touched |
| Requirement(s) | `HLR-RVM.1–4` · `LLR-RVM.1.1–4.2` (all ten) · premise P2 (live-skeleton invariants) — built against the frozen D1 surface (`base.py`) and the D5 glyph table |
| Acceptance | `AT-130…AT-134` · white-box `TC-RM-04…09` via `tests/test_relmap_matrix.py` |
| Agent | `software-dev` (lane L3, forked worktree `wt-r2-matrix`, branch `lane/r2-matrix`) |
| Date | `2026-10-25` |

---

## 0 · Fork preconditions F-1…F-5 — re-read at lane entry (design-proposal.md:126-135)

| Precondition | Check at this lane's entry | Result |
|---|---|---|
| F-1 trunk text-leaf landed, R1 suite green | trunk Inc-1a/1b + Inc-2 landed at `6d81a3f` before the fork; the R1 relmap suites are pinned green there | ✓ |
| F-2 trunk screen-host landed AND the PDR sealed the host↔renderer surface | `mapper/screens/relmap/{__init__,screen,base}.py` present at HEAD; the D1 surface (`ViewState(relmap, notice, focus, cursor, gaps, width, height)`, `paint`, `row_count`, `toggle`, `build_view`, `PendingView`) read in full at entry and built against verbatim | ✓ |
| F-3 lane file sets disjoint — each renderer owns exactly its file | this increment writes exactly `mapper/screens/relmap/matrix.py` (+ its own test file); `git status` shows zero modifications to any tracked file — the frozen host/base/keymap are untouched | ✓ |
| F-4 the reverse census for the lane's touched symbols runs in the lane's first increment | §Reverse census below — 5 probes run in this increment | ✓ |
| F-5 the join seam — AT-driver injection exists on trunk, probed PASS | re-verified live at this lane's entry: `MapperApp(workspace=<bare tmp with a seeded .mmd>)` + `run_test()` reaches `HomeScreen` and lists the seed (`test_f5_at_driver_injection_reaches_home`, executed probe 2026-10-25); the relation-row routing is the shell lane's Inc-6, so this lane's ATs push `RelMapScreen` directly per the trunk `tests/test_relmap_shell.py` idiom | ✓ |

## 1 · What changed

BLUF: the matrix view is real. `mapper/screens/relmap/matrix.py` (one SOURCE
file) renders the operator-chosen **matrix-panel** layout on one audited
`Canvas`: the DSM grid on the left — one row per sourced node in input order
(right-aligned row number, the id cut to an 8–12-cell field, one glyph cell
per displayed column pair, strongest edge wins with ALERT before plain, the
frozen D5 table: verifies `✓`/`!`, binds `●`/`◐`, refines `•`, covers `≡`,
diagonal `▪`, no edge `·`, the `○` row badge for a bind-capable row with no
binds edge — ALERT open / MUT closed) — and the **two-hop impact lens** in a
separate right panel (`what feeds it ←` / `a change reaches →`, `↑1`/`↑2`/
`↓1`/`↓2` markers, edge input order, each member once, hop 2 only through a
drawn hop-1 member of the same direction, overflow counted `+NN more`), the
summary `change <id> reaches N nodes` over `hop 1: n direct · hop 2: m
chained` and the WARN reach gauge against the greatest reach on the map.

Skeleton honesty (HLR-RVM.3): on the live 303-node map the body paints the
verbatim declaration `no test columns yet — the AT→test table (B-141) feeds
this view` where the column header would sit, ZERO phantom test-side cells,
and the row flap declares the window in words (`14–37 / 303` in the capture).
Row windowing keeps the selection visible, centred where the ends allow;
every undisplayed column count is `NN out of view`; the two-digit ruler sits
above the grid; the legend `✓ verifies · ! evidence missing · · no verifies
edge` closes the body.

The `enter` chord owns the matrix lens (state word `panel lens`, COND-ARCH-1);
with the lens on, `neighbourhood(selection, 2)` is consulted **for the
focused node only, once per paint** and the grid row/column labels outside
the 2-neighbourhood dim (Rich `dim` — the FAINT runs of the AT-131 census).
A `None` reach (budget spent) renders `not computed` in WARN with an empty
gauge — never a fabricated number. The notice obligation paints only the
refusal line through the one sink. Every canon-derived label goes through
`base.label` / the `_row_text`/`fit` seam (coerce-then-cut, C-10); hostile
payloads (brackets, ESC, U+202E, control chars, LF/TAB) render literally on
ONE row — the AT-134 arms execute here, live.

The renderer's viewport height derives from the active terminal minus the
host's four chrome rows (the host's `#relmap-canvas` is content-sized); the
white-box arms drive it through `state.width`/`state.height` directly.

Declared readings, pinned by tests and proposed for the contract in
§Records to integrate: (a) LLR-RVM.2.1 "lens widths below 60 cells" is read
as the **viewport** width — at the shipped 118/87 sizes the lens keeps its
hop-2 rows (matching the operator-approved reference renders at both sizes)
and folds them, counted, below 60 cells; (b) the spent-budget summary keeps
the mandated words whole: ` change <id>: not computed`; (c) M-RVM-4 is
undefined in every batch artifact (a numbering gap between M-RVM-3 and
M-RVM-5) — the battery runs every defined mutant, M-RVM-1 twice (its two
registered forms).

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/relmap/matrix.py` | source | HLR-RVM.1–4 · LLR-RVM.1.1–4.2 · COND-ARCH-1 · COND-SEC-1 (the lane half) | NEW — the matrix renderer: `_window` (`:94`), `_winning_edge` (`:116`), `_cell` (`:129`), `_ring` (`:162`), `MatrixView` (`:244`) with `toggle` (`:254`), `row_count` (`:263`), `paint` (`:269`), `_viewport` (`:306`), `_paint_grid` (`:331`), `_paint_panel` (`:440`), `_ring_lines` (`:532`), `build_view` (`:570`) |
| `tests/test_relmap_matrix.py` | test | LLR-RVM.1.1–4.2 (TC-RM-04…09 · AT-130…134) | NEW — 32 nodes: 6 Layer-0 unit arms + 16 Layer-A white-box census/geometry arms + 10 Layer-B AT pilots through the real app (real keys, C-16; non-default values, C-10); synthetic maps built INLINE per ARC-05 |
| `tests/test_fold.py` | test | LLR-N06.2.1 (census collision, correction population §) | `superseded_sites` gains ONE scoped allowance — the lane arms file `tests/test_relmap_matrix.py` presses the D1-frozen `toggle(` entry (enumerated by the failing arm post-commit BEFORE this edit; the instrument and its positive control are unchanged) |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc003-*.txt` | generated | US-RMV-001 | RED ×2, GREEN ×2, the mutation battery, the render captures — redacted (account name → `<user>`, PYTHON), hashed |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 1** (exactly the lane's file) |
| Test files | 2 (1 new + 1 scoped census allowance; both uncapped) |
| Doc files | 0 |

## 3 · How to test

```bash
PYTHONPATH=<worktree> python -c "import mapper; print(mapper.__file__)"   # resolves inside wt-r2-matrix
# targeted (this lane's file):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider tests/test_relmap_matrix.py
# the guard set (C-1):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider tests/test_fold.py tests/test_repair_artifact_claims.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `full` | the branchful helpers: `_window` (centre + both clamps), `_winning_edge` (ALERT before plain, type order, empty), `_cell` (the D5 table), `_ring` (same-direction hop-2, once, input order), the `toggle` vocabulary, `row_count` axis | passed (in the 32) |
| **A · white-box** `TC` ↔ LLR | `full` | notice-obligation, empty/unknown/relates-to-nothing states, window declarations (M-RVM-1), columns out of view + ruler, skeleton honesty census (M-RVM-8), the C10 geometry sweep at (118,30)/(87,30)/(40,12) over five synthetic maps (TC-RM-09), hop-2 fold arms at 160/50, legend verbatim + cut, hostile title one-row (C8/C-17), the full cell census + badge/◐ tones, lens evidence glyphs, summary + gauge proportions, `not computed` (M-RVM-7), the neighbourhood counting wrapper (M-RVM-6) | passed (in the 32) |
| **B · black-box** `AT` ↔ story | `full` | AT-130 (118 + 87 boundary + zero-node boundary, `2`/`1` view round-trip, 25 real `down` presses onto an oracle-chosen LLR), AT-131 (118 + 87 boundary; summary/hop/gauge; `enter` → crumb `panel lens`; the FAINT dimming census on the painted frame; lens-off census), AT-132 (budget exhausted in-test; dimming unchanged), AT-133 (synthetic binds map injected in-process — the canon cannot source AT/TC — REAL keys move the selection; cell census + legend + badge tones), AT-134 (hostile canon live: literal brackets, U+FFFD coercion, zero raw ESC, no forged style, audit-clean; the LF/TAB one-row arm) | passed (in the 32) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | code-absent at the phase-2 entry: `matrix.py` never written — `build_view` falls back to `PendingView` (9 failed, 24 errors, 1 host-only pass — the F-5 probe); move-aside (C-20) with the FINAL test file: 9 failed, 22 errors, 1 passed, restore sha256 MATCH |
| Instrument | project code, the lane's hand (no stash; C-20 move-aside) |
| Where it ran | this worktree, lane L3 (no other session reading — the battery and the runs were serialized) |
| Transcript | `evidence/p3-inc003-red-tests.txt` — exit 1, wall 6s; `evidence/p3-inc003-red-move-aside.txt` — exit 1, wall 5s, restore sha256 `98f09e73…37772` → `98f09e73…37772` MATCH |
| Restore proven by | sha256 of the stored bytes before/after, printed in the transcript |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` in every run (C-46) |
| Arms resolved at baseline | 2 RED arms (phase-2 code-absent + move-aside), each seen failing |
| Verdict granularity | per arm; assertion failures (PendingView bodies) + fixture import errors are the expected failure shapes |
| Arms that stayed GREEN | none (the 1 pass in each run is the host-only F-5 probe, which owns no matrix code) |

| Field | Value |
|---|---|
| **RED counterfactual** | code-absent + move-aside arms, transcripts `evidence/p3-inc003-red-tests.txt` (sha256 `c13d8460…5f21`) and `evidence/p3-inc003-red-move-aside.txt` (sha256 `3b90f544…b05a`) |

| Field | Value |
|---|---|
| **Mutation verdicts** | 11/11 KILLED, per arm, restore sha256-proven for every arm (runner prints MATCH per arm; the file returns to `98f09e73…37772` after the battery): M-RVM-1a (drop row windowing → `test_window_declarations` RED) · M-RVM-1b (drop `NN out of view` → the ruler arm RED) · M-RVM-2 (binds letters → the cell census RED) · M-RVM-3 (◐ tone dropped WARN→MUT → the tone arm RED) · M-RVM-5 (hop-2 from the raw 2-neighbourhood → the ring oracle RED) · M-RVM-6 (`neighbourhood` per row → the counting wrapper RED) · M-RVM-7 (`None` reach coerced to `0` → `test_reach_not_computed` RED) · M-RVM-8 (phantom `·` column → the skeleton census RED) · M-RVM-9 (raise on unknown id → the unknown-focus arm RED) · M-RVM-10 (label pre-cut dropped, clipping leans on `put` → the C10 sweep records unexplained clips at 87) · M-RVM-11 (canon text in a markup-parsing sink → the AT-134 hostile arm RED) · **M-RVM-4 is undefined in every batch artifact** (numbering gap — declared here, no mutant registered) · arms that stayed GREEN: none · transcript `evidence/p3-inc003-mutants.txt` (sha256 `dc681df1…f175`), runner exit 0 |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` | code-absent + move-aside states | exit 1/2 with the transcripts above |
| the C10 audit wrapper | M-RVM-10 (pre-cut dropped) | unexplained `clip` events at (87,30) — printed in the battery transcript |
| the neighbourhood counting wrapper | M-RVM-6 (per-row calls) | `calls == ["LLR-W.1.40"]` saw 60 calls — printed in the battery transcript |
| the mutation runner | its own `CONTROL-BAD` arm (anchor count 0) | reported `CONTROL-BAD: BAD`, exit non-zero before the battery ran clean — an early runner defect (CRLF-polluted restore, mis-counted anchors) was caught by its own restore-hash checks, fixed, and the full battery re-run: every verdict above is from the clean pass |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the composited screen frame (chrome + canvas) | `_painted_runs` — `screen._compositor.render_strips()` serialized as (text, style) runs; the AT-131/132 dimming census reads the style runs; the AT-134 no-forged-style arm reads the run carrying the payload | FAINT runs exactly outside the 2-neighbourhood (lens on), none inside, none lens-off; the hostile run's style has no `bold` |
| the exported screen text (frame lines joined) | AT-130's verbatim declaration + `NN–NN / 303` window; AT-131's summary/hop fragments; AT-134's plained payload substring + zero raw ESC; the LF/TAB arm's single carrier row | all present / all absent as mandated |
| the audited canvas rows (unit) | row/cell bounds at (118,30)/(87,30)/(40,12) over five synthetic maps; zero clip/overprint in every injected sink | clean |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted on its emitted bytes |

### Render comparison — against the operator-approved reference shots

Captured through the real app at (118,34) and (87,34) (`evidence/p3-inc003-renders.txt`): the live skeleton (matrix-panel class) and the injected binds map (binds-glyphs class). Deviations, each deliberate:

1. **No US/AT/TC columns on the skeleton** — by design (HLR-RVM.3); the prototype's demo graph sourced them, the honest skeleton does not, and the body declares it in the pinned words.
2. **The panel carries a dim title line under the head band** — the prototype showed `lens · <id>` only; the title gives the operator context and is the hostile-title surface AT-134 mandates (the id alone cannot carry the ESC/U+202E payload — the R1 builder drops non-printable ids).
3. **Ring rows are single-spaced** — the prototype padded the edge type to a 10-cell field; the acceptance strings pin `↑1 refines <id>` verbatim, so padding yields to the contract.
4. **The summary reads `change <id> reaches N nodes`** per LLR-RVM.2.2 — the prototype used `→ N`.
5. **Reach counts follow the engine's full transitive flow** (`mapper/relmap/model.py:200-219`) — the same semantics the prototype's `reach` had; the lens rings still list hops 1–2 only, and `hop 2` is honestly 0 on the skeleton's `down(LLR)`.
6. At 87 the declaration and the summary cut inside their regions with the declared ellipsis — matching the 87-col reference behavior.

Everything else — grid + side-panel composition, the focus tint on the selected row, the hop markers and evidence glyphs, the WARN gauge, the legend row, the `NN–NN / N` flap — matches the reference layout.

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED phase-2 transcript (code-absent) | `…/evidence/p3-inc003-red-tests.txt` | `c13d84607a8926a33678e48319dd2d0deeda67c34103457dcaab2188985a5f21` |
| RED move-aside transcript (C-20) | `…/evidence/p3-inc003-red-move-aside.txt` | `3b90f5444ab49994438e60735351deddf41a440cfb3844bd6b34c1e18a07b05a` |
| GREEN targeted transcript | `…/evidence/p3-inc003-green-targeted.txt` | `f1c800cd52621a775d609a0da1bf08a80b8b7b157a5aaef13433224ea0b34c7a` |
| GREEN guard transcript | `…/evidence/p3-inc003-green-guards.txt` | `9ed10ffa8dd905a9e039ee37472dfcb1869d217cfb2f074888132e6e356df1e7` |
| mutation battery transcript | `…/evidence/p3-inc003-mutants.txt` | `dc681df15e00e744baafacbc2c8df1e6db3cea192e8d9725922652703049f175` |
| render captures (118/87) | `…/evidence/p3-inc003-renders.txt` | `8ac38a1ee8067d0e3e9c1a2b01a61ebccc30d72e27b066fec1b0dcdc7b7e55f7` |

All transcripts redacted (account name → `<user>`) with a PYTHON script before hashing; exit codes and wall time in each header.

| Field | Value |
|---|---|
| **Evidence files** | 6 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — (a) the skeleton sources NO test-side node (the declaration arm and the phantom census assert the emptiness), (b) the derived skeleton's live figures (303 nodes / 215 `refines` edges) are measured in-test from the copied canon, not assumed, (c) `down(LLR)` empty ⇒ hop 2 honestly 0 today (AT-131 asserts `hop 2: 0 chained` against the oracle) |
| If the result is an ABSENCE, what made the search wide enough | (a) the census sweeps EVERY grid row's cell span for every D5 glyph and the whole painted text for `US-`/`AT-`/`TC-` tokens; (b) the node/edge counts derive from `RelMap.nodes`/`edges` at run time; (c) the hop counts come from `RelMap.down`, not from the painted text |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_no_test_columns_declaration_and_skeleton_honesty` pins the conclusion "the map contains no test-side node ⇒ no phantom columns and the verbatim declaration"; the A3 census's own anti-invisibility arm (`test_tc_a3_no_source_file_is_invisible_to_the_census`) fires until `matrix.py` is tracked — a precondition the commit discharges, not a defect |
| Conjunctive criteria: one mutation per conjunct | M-RVM-1a/1b the two windowing conjuncts; M-RVM-2/3 the glyph vs tone conjuncts of the binds cell; M-RVM-13-family host-side (Inc-2); M-RVM-11 the sink conjunct of the hostile arm |
| Synthetic instance of the absent case | the AT-133 binds map IS the synthetic test-side instance (built in-process — the canon cannot source AT/TC); the hostile canon IS the synthetic hostile instance; the budget-spent arm IS the synthetic `None`-reach instance |
| **Positive control for every probe that returned an ABSENCE** | the census runs against the injected binds map in the same arm file and finds every glyph it expects (the positive control for the phantom census is the census itself on a map WITH columns); the M-RVM-8 battery arm turns the census RED by painting the phantom — the instrument is shown able to see the case it reports absent |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rln "screens.relmap.matrix\|relmap import matrix\|MatrixView" tests/ mapper/` | only the module itself and its own test file — no foreign assertions; the host reaches it through the dynamic `build_view` wiring (frozen D1), never a static import |
| B2 file moved on disk | `git log --oneline -- mapper/screens/relmap/matrix.py` | net-new file — no old path exists; not fired |
| B3 byte-identical golden captures this source | `grep -rln relmap tests/goldens/` | no hits — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "screens.relmap.matrix" mapper/ tests/` | zero consumers besides the D1 dynamic wiring — the A3 row below stayed inside the owner |
| A3 interface consumed by another module changed | `grep -rn "ViewState\|PendingView\|build_view" mapper/ tests/ --include="*.py"` outside `screens/relmap` | the tree kind's pre-existing `mapper/views/state.ViewState` (different module, untouched); the relmap surface has no external consumer besides the three lanes' future modules; this lane's renderer adds ZERO `.render(` calls (grep: 0 in `matrix.py`) — the A3 census's ARG-FUL pin is unmoved |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3); B2/B3 not fired; A3 clean |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the fold-state supersession census (`.toggle(` calls) | every `.toggle(...)` attribute call under `mapper/**` + `tests/**` | `test_fold.py::superseded_sites` — AST census; verified the `screens/relmap/` skip covers the new renderer's `def toggle` (no `.toggle(` call site is added) | 0 edits at first enumeration | `tests/test_fold.py` — one scoped allowance | one — the arm is `_tracked`-gated: it only sees the lane's files once they are TRACKED, so the post-commit re-run enumerated the real population (the failure named `tests/test_relmap_matrix.py:78`, a D1-frozen `toggle(` arm) BEFORE the allowance was edited — the allowance names exactly the lane arms file, the same shape as the host-arms allowance; the instrument's positive control re-runs unchanged |
| the relmap-importers census | every non-`relmap/` module importing `mapper.relmap` | `test_relmap_isolation.py` run targeted — the ARQ-sanctioned `screens/relmap/` skip covers `matrix.py`'s `mapper.relmap.model`/`profile` imports | 0 edits | none | none |
| the A3 `.render(` census | ARG-FUL `.render(` call sites under `mapper/views/` | `test_a3_census.py` run targeted — zero `.render(` in the new file; the anti-invisibility arm fires pre-commit by design (untracked source) and was re-run green post-commit | 0 edits | none | none |
| the `.relmap.yml` content census | every `tests/**` file spelling the descriptor suffix | `test_relmap_descriptor.py` run targeted — the new file writes no descriptor | 0 edits | none | none |
| the path:line citation table | every backticked `path.py:NN` citation in the authored artifacts + `mapper/` source | `test_repair_artifact_claims.py` in the guard set — re-run with this packet on disk (green) and post-commit | 0 edits | none | none — this packet's citations name real lines of the committed file |

| Field | Value |
|---|---|
| **Correction population** | 6 populations enumerated by their own instruments; ONE scoped census amendment (`test_fold.py`'s `superseded_sites` gains the lane arms file — test files are uncapped), enumerated by the failing arm before its first edit; the A3 anti-invisibility arm's pre-commit firing is a declared precondition, discharged by the commit and re-run green |

### Signed-balance test ledger

`post = base − deleted + added`: targeted `32 = 0 − 0 + 32` (6 Layer-0 + 16 Layer-A + 10 Layer-B; the phase-2 RED run recorded 9 failed + 24 errors + 1 host-only pass against the absent module — every one of the 32 was seen failing before the GREEN). Guard pair: `206 passed, 3 xfailed` final vs the measured HEAD baseline `204 passed, 3 xfailed` (baseline run executed with the lane's files moved aside, 42s) — Δ +2 = the citation instruments' own module/corpus collections (`tests/test_relmap_matrix.py` enters the scanned module set and the corpus reads). One tracked test file amended (`tests/test_fold.py`, one allowance row — see Correction population; the fold suite stays 19 passed + 3 xfailed, the instrument's positive control unchanged). The R1 relmap suites and the host arms are untouched. Post-commit re-verification: the tracked-file censuses (A3 anti-invisibility, fold supersession, citation) all green on the committed tree.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Kimi K2.8 subagent executing agents/code-reviewer.md + agents/security-reviewer.md + agents/ux-reviewer.md · approve-with-nits → discharged fb336ed` |
| Review record | `.dev-flow/2026-10-25-relmap-r2-batch/evidence/review-inc003.md` (sha256 `77519910b2835f8fb19a0174a1d7f699ff3edf4e6fa06c36e4367c7063dff15b`) |

Follow-ups (both MINOR, discharged in the review follow-up unit):

| Finding | Disposition | Evidence |
|---|---|---|
| F1 — the `╌╌╌ root — nothing feeds it` line was unpinned (no LLR, no oracle) | **fixed** (test-only): `test_relates_to_nothing_when_the_selection_is_isolated` gains the root limb — the line paints exactly once when the up ring is empty and the down ring is not, in MUT, and `╌╌╌ relates to nothing` stays absent | `evidence/p3-inc003-followup-red.txt` (sha256 `fcada8ddc5e17b500d81d6f1bac91e5ede0a55408315a87430d4566c6badcac0`) · `evidence/p3-inc003-followup-green.txt` (sha256 `cd329e0deb05a75560f9226d00474aa8e1a7bdee16fe36d9f875396231904e1b`) |
| F2 — the degenerate-height flap can read `01–00 / N` | **fixed**: one-line guard `max(1, row_window.stop)` on the flap (`mapper/screens/relmap/matrix.py:433`) + arm `test_degenerate_height_flap_never_reads_an_empty_window` — h=6 is the one visible degenerate height (row budget exactly 0, flap one row above the legend); RED on the unguarded source reproduced `01–00`, GREEN with the guard | same transcripts (52 passed, 3 xfailed) |

## 5 · Risks

- The two declared readings (hop-2 fold at viewport < 60; ` change <id>: not computed`) are lane interpretations pinned by unit arms on both sides; if the orchestrator rules differently, the contract text moves at the join and one renderer constant/presentation line follows — the tests name both.
- The matrix's graduated-binds `◐` holds WARN (the operator-approved prototype's tone and M-RVM-3's droppable tone); LED-2026-10-25-r2.05's "exactly three signals" names the sheet's `◐` — a clarification is proposed in §Records to integrate so the ruling covers the matrix instance explicitly.
- The panel width formula and the 4-row chrome budget derive from the landed host's composed widgets (measured 2/1/1 at both shipped sizes); a host chrome change moves the derived body height — the AT pilots pin the end-to-end result at 118/87.
- The A3 anti-invisibility arm and the fold supersession arm are `_tracked`-gated: they only see the lane's files once committed — the commit is part of the gate and both are re-run green on the committed tree (the fold arm's post-commit enumeration produced the one scoped allowance of the increment).

## 6 · Pending items / spec deviations

- None against the contract beyond the two declared readings above (both proposed as contract clarifications below; nothing applied by this lane).
- COND-SEC-1's lane arm (AT-134, incl. the LF/TAB one-row arm) executes fully here — live, hostile, audit-clean.

## Records to integrate

Proposed rows and entries — exact text for the orchestrator; nothing below is applied by this lane.

### PLAN test-ledger rows (proposed)

```
| 3 · matrix | L3 landed | US-RMV-001 | screens/relmap/matrix.py (**1**) | grid + windowing + lens + reach gauge + skeleton honesty | HLR-RVM.1–4 · LLR-RVM.* | test_relmap_matrix.py 32 nodes (6 L0 + 16 A + 10 B), AT-130…134 live, battery 11/11 KILLED |
```

### Ledger entries (proposed, C-11 naming)

**LED-2026-10-25-r2.19 — The matrix renderer lands: two presentation readings pinned (lane L3 Inc-003)**

- **Requirement:** LLR-RVM.2.1, LLR-RVM.2.2
- **Asserting tests:** `tests/test_relmap_matrix.py` — `test_hop2_rows_fold_below_the_sixty_cell_viewport`, `test_reach_not_computed_renders_honestly`, `test_at131_lens_summary_hop_counts_and_dimming`, `test_at132_budget_spent_renders_not_computed`
- **Mutants:** M-RVM-5 (orphaned hop-2), M-RVM-6 (per-row `neighbourhood`), M-RVM-7 (`None` reach fabricated) — all KILLED, restore sha256-proven (`evidence/p3-inc003-mutants.txt`)

LLR-RVM.2.1's "at lens widths below 60 cells the hop-2 columns shall fold away" is implemented and pinned as the VIEWPORT width: both shipped sizes (118/87 ≥ 60) keep the hop-2 rows, matching the operator-approved reference renders at both sizes; below 60 the rows fold with the members counted `+NN more`. Proposed contract clarification (exact text for LLR-RVM.2.1's statement, appending): "— `lens width` here means the view's viewport width (`state.width`)." LLR-RVM.2.2's spent-budget count renders on its own whole-word row, ` change <id>: not computed` in WARN with an empty gauge, because the wordy `reaches N nodes` frame cuts the mandated words at the shipped panel widths; the computed form is untouched. Proposed contract clarification (exact text, appending to LLR-RVM.2.2's statement): "When `reach` is `None` the summary row reads ` change <id>: not computed` in WARN (the whole mandated words kept on the row); the gauge is empty."

**LED-2026-10-25-r2.20 — WARN scope: the matrix's graduated-binds `◐` (clarifies LED-2026-10-25-r2.05)**

- **Requirement:** LLR-RVM.1.2, LLR-RVM.2.1 (the ◐ tone); LED-2026-10-25-r2.05 (the scope ruling it joins)
- **Asserting tests:** `tests/test_relmap_matrix.py` — `test_cell_census_on_the_synthetic_binds_map` (the ◐/● tone arm)
- **Mutants:** M-RVM-3 (the evidence tone dropped → RED)

The matrix renderer paints the tagged-binds `◐` in WARN — the operator-approved prototype's tone (round-2026-10-23, `binds-glyphs.png`) and the tone M-RVM-3 assumes. r2.05's "exactly three signals" names the sheet's `◐`; the matrix instance is the same signal family (tagged-without-evidence attention) in a second renderer. Proposed ruling text (appending to r2.05's scope sentence): "The tagged-binds `◐` glyph holds WARN in EVERY renderer that paints it (matrix cells and lens rows per LLR-RVM.1.2/2.1; the sheet per LLR-RVS.2.3) — one signal, one tone, wherever it appears."

**LED-2026-10-25-r2.21 — M-RVM-4 numbering gap (record-only)**

- **Requirement:** none (mutant registry hygiene)
- **Asserting tests:** none
- **Mutants:** n/a

The matrix mutant row names M-RVM-1…M-RVM-11, but every batch artifact defines no M-RVM-4 (grep over `.dev-flow/2026-10-25-relmap-r2-batch/`: zero hits). The lane battery ran all ten defined mutants, M-RVM-1 in both registered forms (windowing drop, declaration drop). Proposed: either register a M-RVM-4 (the orchestrator's choice of negative control) or renumber the M-RVM-5…11 rows at the join; the battery transcript records which arms ran.

### Contract / ARCHITECTURE / census amendments (proposed exact text; nothing applied)

- `01-requirements.md` LLR-RVM.2.1 statement: append "— `lens width` here means the view's viewport width (`state.width`)." (per LED-2026-10-25-r2.19.)
- `01-requirements.md` LLR-RVM.2.2 statement: append "When `reach` is `None` the summary row reads ` change <id>: not computed` in WARN; the gauge is empty." (per LED-2026-10-25-r2.19.)
- `01-requirements-ledger.md`: the three LED entries above, verbatim.
- `docs/ARCHITECTURE.md`: the `screens/relmap` planned row becomes a fact for `matrix.py` (path lands; one paint entry over the frozen D1 surface; never imports a sibling renderer), the same edit shape Inc-2 used for the host — deferred to the join so one ARCHITECTURE edit lands all three renderers.
- Censuses: NO amendment needed — `test_fold.py` (screens/relmap skip), `test_relmap_isolation.py` (sanctioned package skip), `test_a3_census.py` (zero `.render(` added; the anti-invisibility arm discharges at the commit), `test_relmap_descriptor.py` (no descriptor suffix in the new file), `test_repair_artifact_claims.py` (this packet's citations resolve; re-run after commit).

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1/1 — exactly the lane's file (`git status`: zero modified tracked files) |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_relmap_matrix.py` new (32 nodes), run RED-before-GREEN (`p3-inc003-red-*.txt` → `p3-inc003-green-targeted.txt`) |
| 3 | Layer 0 written where the criterion applies | `full` | ✓ | 6 unit arms over the branchful helpers (`_window`, `_winning_edge`, `_cell`, `_ring`, the toggle vocabulary, `row_count`) |
| 4 | RED counterfactual declared | all | ✓ | code-absent (exit 1) + move-aside (exit 1, restore sha256 MATCH), transcripts cited |
| 5 | Reverse census declared | all | ✓ | §Reverse census — 5 probes; B2/B3 not fired; A3 clean |
| 6 | `code-reviewer` passed | all | ⚠ | `pending — orchestrator schedules` (§4b) |
| 7 | No file from another lane touched | all | ✓ | `git status`: only `matrix.py`, this test file and this lane's evidence/packet — `gaps.py`/`sheet.py`/`home.py`/`app.py`/`keymap.py` untouched |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D1 (`base.py`/`screen.py`) byte-untouched — `git diff` empty; D2/D3/D4 untouched; D5 table implemented verbatim; no `.render(` added |
| 9 | Coverage claims verified on disk | all | ✓ | 32 targeted nodes collected on disk in the final GREEN run |
| 10 | Load-bearing emptiness declared | all | ✓ | §Load-bearing emptiness — positive controls named per absence (the injected binds map, the hostile canon, the M-RVM-8 arm) |
| 11 | Mutation verdicts declared | all | ✓ | 11/11 KILLED per arm, restore digests cited, battery exit 0; M-RVM-4 gap declared (LED-…-r2.21 proposed) |
| 12 | Instrument RED-proof declared | all | ✓ | 4 instruments each shown RED first (incl. the runner's CONTROL-BAD and its own restore-hash catch) |
| 13 | Correction population declared | all | ✓ | 6 populations enumerated by their own instruments; ONE scoped census amendment (enumerated by the failing arm before its edit) — §Correction population |
| 14 | Emitted-form assertion declared | all | ✓ | 3 artifacts asserted on emitted bytes (frame runs, exported text, audited canvas rows) |
| 15 | Independent review names somebody | all | ✓ | §4b names the pending pass owner: the orchestrator schedules the `code-reviewer` (lane gates ship evidence; review at the join per F-5) |
| 16 | Evidence files declared | all | ✓ | 6 files at `artifact_homes.evidence`, digests of stored bytes |
