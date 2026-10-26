# Increment 004 — HLR-RVG.1–3 · the ranked-gaps renderer (lane L4)

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `004` |
| Lane (if the batch forked) | L4 (gaps) — lane worktree `wt-r2-gaps`, branch `lane/r2-gaps` |
| Requirement(s) | `HLR-RVG.1/.2/.3` · `LLR-RVG.1.1–1.5, 2.1–2.3, 3.1` — over the frozen D1 surface (PDR `D1` as amended, `LED-2026-10-25-r2.18`) |
| Acceptance | `AT-135…AT-139` (gaps portions) · `TC-RM-10…14` via `tests/test_relmap_gaps_view.py` + `tests/test_relmap_scalecheck.py` (the 118/87 sweep) |
| Agent | `software-dev` (lane L4) |
| Date | `2026-10-25` |

---

## 0 · Fork preconditions F-1…F-5 (re-read at lane entry)

| Precondition | Check | Result |
|---|---|---|
| F-1 text leaf landed, R1 suite green | `mapper/relmap/text.py` present; R1 files re-pointed (Inc-1a/1b landed, `p3-inc1b-*` evidence) | ✓ |
| F-2 screen host landed, D1 sealed | `mapper/screens/relmap/{base,screen}.py` present at HEAD `6d81a3f`; the PDR seal + the Inc-2 review-pass amendment (`row_count`, per-view cursor/word) are the surface built against | ✓ |
| F-3 lane file sets disjoint — a lane needing a host change STOPS | this lane's SOURCE set is exactly `mapper/screens/relmap/gaps.py` (1 file); **no host edit was needed** — the renderer works around the host's auto-height canvas within the frozen surface (the `_DEFAULT_BODY` floor, see §1) | ✓ |
| F-4 reverse census in the lane's first increment | §Reverse census below | ✓ |
| F-5 the join — lane ATs run on the joined tree; AT-driver seams probed | lane-entry probe re-run in THIS worktree: `MapperApp(<tmp>)` + `run_test()` reaches `HomeScreen`, a pushed `RelMapScreen` derives the seeded 3-node fixture (`evidence/p3-inc004-f5-probe.txt`); the cross-view AT-137 portions (matrix window, sheet overflow) are **join-time** — they need the other lanes' renderers, absent in this tree | ✓ (probe) · ⚠ join |

## 1 · What changed

BLUF: the ranked-gaps renderer is real. `mapper/screens/relmap/gaps.py` lands
`GapsView` against the frozen D1 surface: `paint(state) -> list[Text]` renders
the host-supplied ranked gap rows **in exactly `state.gaps` order** — severity,
then reach descending, detection order on ties — never re-sorted, re-filtered
or invented (LLR-RVG.1.1; M-RVG-1 is re-sort by node id). Chrome: the header
`gaps — what the record does not say` with the right-aligned ranking note, the
always-four tally chips `high/med/low/total`, and the field band
`no gap node what reach status` (LLR-RVG.1.2). Rows: zero-padded rank, the gap
kind in Darkside casing (a case-only transform, LLR-RVG.2.1), the node id, the
WHAT sentence, the zero-padded three-digit reach count (the only reach visual —
no microbar, LLR-RVG.1.3) and the severity word; the cursor row rides
`state.cursor` (view open = row 01, the worst gap). The body window follows the
cursor with `+NN above` / `+NN more` cut markers declaring every undeclared
row; WHAT truncates with one ellipsis and drops WHOLE below its 12-cell minimum
(LLR-RVG.1.4). `k` regroups into per-kind bands in catalogue order — band head
with the kind label, `×N` and the worst severity, member rows keeping their
global ranks, the hint `same catalogue grouped by gap kind — scan for a
detector, not a severity` bottom-anchored, counted `+NN more` on overflow —
and pressing `k` again returns the ranked frame byte-identical
(LLR-RVG.1.5). Honest zeros: `000` painted as computed, never `-`; the
not-computed count is declared on the tally as `reach not computed: N` and never
fabricated (LLR-RVG.2.3). Every canon-derived string passes `darkside.plain`
and the one `base.label` sink — explicit-style `Text`, no markup-parsing sink
(LLR-RVG.3.1, C8/C-17).

**Reconciliations and declared decisions (deviations from the letter of the
contract/prototype, each a deliberate ruling):**

1. **The not-computed count vs the frozen D1 surface.** LLR-RVG.1.1's letter
   says the renderer calls `detect_gaps` + `rank_gaps` and reads the
   not-computed count from the second tuple member; the shipped host (Inc-2,
   the D1 surface) ranks once and passes only the ranked tuple in
   `ViewState.gaps`. The count is therefore re-derived by re-issuing the SAME
   deterministic ranking call over the host-supplied rows (`reach` is memoized
   on the map, so no budget is re-spent); the painted rows always come from
   `state.gaps` in its exact order — the re-issue never re-sorts anything.
   This is the only reading that satisfies both LLR-RVG.2.3 (the marker) and
   the freeze (no host change; F-3).
2. **The mount-time viewport height.** The host's `#relmap-canvas` `Static` is
   auto-height, so on the first paint the frozen `state.height` channel
   carries the degenerate `1` (probe: `canvas size = Size(width=118,
   height=1)`). Painting a one-line body would make every AT-135 assertion
   unmeetable through the shipped host. The renderer therefore treats an
   explicit viewport height as the budget and paints an honest default body
   (24 rows = chrome 3 + body 21, inside the 34-row reference class with the
   5 host chrome rows) only while the channel carries the degenerate value.
   No host edit (F-3 holds); the window LLRs stay exactly testable because
   explicit heights are always respected.
3. **AT-135 crumb deviation.** The asserted crumb `reqharness / relmap /
   gaps · reach count` is the PROTOTYPE's scene label; the shipped host's
   crumb format is `name / relmap / view [· toggle-state word]`, and the word
   channel is the toggle state word (`""` at open). At open the crumb reads
   `reqharness / relmap / gaps`; after `k` it reads
   `reqharness / relmap / gaps · by kind` — the AT asserts exactly that and
   this packet records the deviation.
4. **Layer split for the long asserted strings.** AT-135's `qualified rows end
   (canon rows near this id could not be parsed or linked: 2)` cannot paint at
   118 columns: the qualified sentence is 106–109 cells while the WHAT column
   at 118 is 62 (the row's fixed columns — rank, kind, node, reach, status —
   are pinned by the same LLR). The full-row anatomy and the qualifier are
   therefore pinned by a unit paint at width 170 (nothing truncates), and the
   app-level AT asserts the honest truncated form (`… 000 med`) at 118/87.
5. **No Canvas.** The gaps renderer assembles explicit-style `Text` rows
   through the one label sink; it paints no `Canvas` cells, so the C10 audit
   mapping has no sink site here. The audit-clean sweep is asserted
   directly on the emitted rows: exactly the viewport height, no row wider
   than the canvas (zero clip / zero overprint by construction), at 118 and
   87 (`_disciplined` in the sweep file). This is the honest statement of the
   AT-137 "audit sink zero clip/overprint" clause for a row-assembled view.
6. **Rank width at cap scale.** LLR-RVG.1.3 pins a zero-padded two-digit
   rank; at the 100,000-row cap the rank needs six digits, so the rank column
   widens to the longest rank (the geometry is derived, never truncated).
7. **Reference-render deltas vs the prototype PNGs** (§6 below): Darkside
   lowercase everywhere (the Solari ALL-CAPS the screenshots show was
   rejected by the operator verdict — NOT shipped); no group box / seams (the
   shipped host owns the chrome borders); the honest skeleton paints 7
   `hlr without llr` gaps all `med`/`000` (as the P2 live probe recorded);
   the tally line carries no HIGH/LOW chips when those counts are zero — the
   chips ARE painted, at `0`.

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/relmap/gaps.py` | source | HLR-RVG.1–3 · LLR-RVG.1.1–1.5, 2.1–2.3, 3.1 | NEW — `GapsView` (the ranked-gaps renderer) + `build_view()`; exactly 1 SOURCE file |
| `tests/test_relmap_gaps_view.py` | test | LLR-RVG.1.1–1.5, 2.1–2.3, 3.1 · AT-135/136/138/139 | NEW — 27 nodes: rendered-order oracle, chips/fields, row anatomy, cursor highlight, by-kind bands + the COND-UX-2 membership oracle, casing censuses (AST + painted), honest zeros + not-computed, hostile payload (unit + app), notice obligation, row axis — plus the Layer-B app arms |
| `tests/test_relmap_scalecheck.py` | test | LLR-RVG.1.4 · AT-137 | NEW — the 118/87 sweep: C10 discipline at both sizes, the WHAT drop-whole ladder, the 87-column ellipsis arm, the cursor-following window with marker arithmetic, the 100k cap-scale arm at 118 AND 87 |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc004-*.txt` | generated | US-RMV-002 | RED ×2, GREEN ×2, move-aside, mutants, F-5 probe, measurements — redacted, hashed |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** |
| Test files | 2 (new; uncapped) |
| Doc files | 0 |

## 3 · How to test

```bash
PYTHONPATH=<worktree> python -c "import mapper; print(mapper.__file__)"
# targeted (lane tests):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_relmap_gaps_view.py tests/test_relmap_scalecheck.py
# the guard set (C-1):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_fold.py tests/test_repair_artifact_claims.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `full` | casing AST census, source sink census, notice obligation, row axis | passed (in the 33) |
| **A · white-box** `TC` ↔ LLR | `full` | `tests/test_relmap_gaps_view.py` — rendered order, chips/fields, anatomy, cursor, by-kind + membership oracle, honest zeros, not-computed, hostile unit arm | 33 passed across the two files (see GREEN transcripts) |
| **B · black-box** `AT` ↔ story | `full` | AT-135 (open → `2` → chrome asserts → `down` → highlight moves, `focus` untouched), AT-136 (`k` → bands/hint/crumb → `k` byte-identical), AT-137 gaps portions (87-col window + the cap-scale unit arm), AT-138(a) empty map through the app, AT-139 hostile canon through the app — REAL keys via `run_test()` (C-16) | passed |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (1) code-absent: `gaps.py` not yet written — both lane files fail at collection; (2) move-aside (C-20): `gaps.py` renamed out of the tree |
| Instrument | project code, lane's hand (no stash; C-20 move-aside) |
| Where it ran | this worktree, lane L4 (no other session reading — the battery and the runs were serialized) |
| Transcript | `evidence/p3-inc004-red-code-absent.txt` — exit 2, 2 collection errors (`No module named 'mapper.screens.relmap.gaps'`), wall 1s; `evidence/p3-inc004-red-move-aside.txt` — exit 2, 2 collection errors, wall 1s, restore sha256 MATCH printed in the transcript |
| Restore proven by | move-aside restore sha256 MATCH `acf22007…885f445` (printed in the transcript); the code-absent state needed no restore |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` in every run (C-46) |
| Arms resolved at baseline | 2 RED arms (1 code-absent + 1 move-aside), each seen failing |
| Verdict granularity | per arm; collection errors are the expected failure shape for import-level absence |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | 2 arms (code-absent + move-aside), transcripts at `evidence/p3-inc004-red-code-absent.txt` (`670e5f1b3d1c4c63760ceb0a3c2635d6f4b4d906383b48e0fbca8f860df2b86f`) and `evidence/p3-inc004-red-move-aside.txt` (`79f982160c7411210ad56df680b79a51f9bf24280fe897fb27b583df7d1822e9`) |

| Field | Value |
|---|---|
| **Mutation verdicts** | 13/13 KILLED — M-RVG-1 (re-sort by node id) · M-RVG-2 (total chip dropped) · M-RVG-3 (unpadded reach) · M-RVG-4 (initial cursor on the last row) · M-RVG-5 (window clamped) · M-RVG-6 (WHAT truncated below minimum) · M-RVG-7 (bands by row count) · M-RVG-8 (`.upper()` restored) · M-RVG-9 (caps chrome string) · M-RVG-10 (`000` as `-`) · M-RVG-11 (not-computed marker dropped) · M-RVG-12 (coercion bypassed — the specced "plain() pass removed" shape; see the note below) · M-RVG-13 (markup-parsing sink) — per arm, restore sha256 proven for every arm, runner exit 0, transcript `evidence/p3-inc004-mutants.txt` (`07bacfacefa6d1cdb81ebb552b9db1b6ba1d8326ac12d66c98943546f63f435f`) |

M-RVG-12 note: with the one `base.label` sink doing the coercion internally,
deleting the renderer-side `darkside.plain` pass alone is unobservable (the
sink re-coerces idempotently) — the battery therefore ALSO runs the specced
shape as the disclosed `M-RVG-12-spec` arm, and it SURVIVES as expected
(recorded, restore sha256 MATCH). The KILLED M-RVG-12 arm applies the INTENT
of the mutant: the coercion chain broken at the renderer (the WHAT segment
assembled from the RAW sentence through a bare `Text(...)` slice) — that
reddens the hostile arm twice over (raw ESC/TAB/LF reach the frame; a forged
second row). Honest disclosure per the lessons catalog: a survived mutant is
either a hole in the arm or a hole in the mutant's observability — here it is
the mutant's, and the hostile fixture pins the real axis.

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` | the code-absent + move-aside states | exit 2 collection errors, transcripts |
| the mutation runner | its own `--bad-control` (anchor ×0) | `M-RVG-1: BAD (anchor found 0 times)` and exit 1 — before the real battery was believed |
| the hostile-payload arm | M-RVG-12 (raw `Text` assembly) / M-RVG-13 (`Text.from_markup`) | ESC/LF leak / brackets consumed — printed in the battery transcript per arm |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the painted rows (`view.paint(state)`) | exact squashed row equality `<rank> <kind> <node> <sentence> 000 <sev>` at width 170 (M-RVG-3/10 redden the `000`) | 7/7 rows exact |
| the composited app frame | `painted_frame` — strips serialized as (text, style) runs; byte-compared across the AT-136 toggle-back; the highlight band `on #262626` asserted row-by-row after REAL `down` presses (AT-135) | byte-identical toggle-back; highlight moved 01→02 with `focus` untouched |
| the painted hostile frame | payload literal brackets, zero raw ESC/TAB/LF, U+FFFD coercions, style vocabulary ⊆ the renderer's own tokens (AT-139, unit + app) | literal, one row, no leak |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted on its emitted bytes |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED code-absent transcript | `…/evidence/p3-inc004-red-code-absent.txt` | `670e5f1b3d1c4c63760ceb0a3c2635d6f4b4d906383b48e0fbca8f860df2b86f` |
| RED move-aside transcript | `…/evidence/p3-inc004-red-move-aside.txt` | `79f982160c7411210ad56df680b79a51f9bf24280fe897fb27b583df7d1822e9` |
| GREEN targeted transcript | `…/evidence/p3-inc004-green-targeted.txt` | `b3fae32b2e0a467c0eb8259ee7a13998471bee8f59ccad5a5f42ba5e3f552f91` |
| GREEN guard transcript | `…/evidence/p3-inc004-green-guards.txt` | `44332757df6e992e82fc08bd585cb980aaa8e7a1a5840412544c89a9f099f732` |
| mutation battery transcript | `…/evidence/p3-inc004-mutants.txt` | `07bacfacefa6d1cdb81ebb552b9db1b6ba1d8326ac12d66c98943546f63f435f` |
| AT-137 measurements + renders | `…/evidence/p3-inc004-measure.txt` | `818d8dc9b1394f06016e9e6ab598a9213e5afba9e1ee94b4d2d88cdc6493da58` |
| F-5 lane-entry probe | `…/evidence/p3-inc004-f5-probe.txt` | `6ee1749e002c70bbc7bd5e648bfb2129f61dd41f5edab7c4df6e928dc557a118` |

All transcripts redacted (account name → `<user>`) with a PYTHON script before
hashing; exit codes and wall time in each header.

| Field | Value |
|---|---|
| **Evidence files** | 7 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — (a) the wiring fallback: `build_view("gaps")` returns the live renderer because the module exists (the shell arm `test_d1_surface_names_are_frozen` exercises the placeholder for the OTHER two views); (b) the hostile census "no `from_markup` in the renderer source" |
| If the result is an ABSENCE, what made the search wide enough | (a) `base.build_view` imports `mapper.screens.relmap.<name>` and only `ModuleNotFoundError` with `exc.name == module_name` falls back — proven by the move-aside arm (the tests fail at collection, no silent placeholder); (b) the AST census walks every node of the parsed module |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_rvg_3_1_the_renderer_uses_no_markup_parsing_sink` pins a conclusion about the source; `test_rvg_2_1_source_census_no_upper_no_caps_kind_literal` pins the casing conclusion |
| Conjunctive criteria: one mutation per conjunct | M-RVG-12 the coercion conjunct / M-RVG-13 the markup-sink conjunct of LLR-RVG.3.1; M-RVG-3 the padding conjunct / M-RVG-10 the honest-zero conjunct of the reach column; M-RVG-8 the transform conjunct (census + rendered) |
| Synthetic instance of the absent case | the hostile fixtures ARE the synthetic hostile instances; the move-aside IS the synthetic absent module |
| **Positive control for every probe that returned an ABSENCE** | the fixture-shape positive control derives the 7-gap snapshot through the real adapter (`test_rvg_1_1_snapshot_fixture_shape`); the order arm asserts the ranked oracle `["y","x","h"]` BEFORE painting (a probe that returned an absence still saw the positive control); the runner's BAD control proves the anchor check fires |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rln "screens.relmap.gaps\|build_view(\"gaps\")" tests/ mapper/` | the two new lane files + `base.py` (the wiring); zero readers outside the expected set |
| B2 file moved on disk | `git log --oneline -- mapper/screens/relmap/gaps.py` | net-new file — no old path; not fired |
| B3 byte-identical golden captures this source | `grep -rln gaps tests/goldens/` | no hits — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "relmap.gaps import\|from mapper.screens.relmap import" mapper/ tests/` | consumers: the two lane test files only; the host reaches the renderer through `base.build_view` by name convention, never an import — the freeze holds |
| A3 interface consumed by another module changed | `grep -rn "ViewState\|RelMapView" mapper/screens/relmap/` | the D1 surface untouched (zero host edits; F-3) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3); B2/B3 not fired; B4/A3 clean |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| — none — | no census failed at lane entry: the lane adds ONE net-new source module + two net-new test files; no existing census names them (B1/B4 above enumerate the consumers after the fact; the fold/relmap-isolation/descriptor censuses scope `screens/relmap/` entries already allowed or test-file-specific, and the guard run came back green with zero edits) | the guard set + the privacy census re-run before the commit | 0 | none | none |

| Field | Value |
|---|---|
| **Correction population** | 0 corrections — the lane's file set is disjoint from every census population (enumerated by the failing-probe method at the guard run; nothing failed) |

### Signed-balance test ledger

`post = base − deleted + added`: the two lane files add **33 nodes** to the
targeted set (baseline targeted for this lane = 0 — the files are new); the
guard set re-runs unchanged (`206 passed, 3 xfailed` — the Inc-2 guard total,
unchanged node-for-node). The full-suite count and the PLAN test-ledger rows
are the orchestrator's at the join — proposed rows are in §Records to
integrate.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Kimi K2.8 subagent executing agents/code-reviewer.md + agents/security-reviewer.md + agents/ux-reviewer.md · approve-with-nits → discharged fb336ed` |
| Review record | `.dev-flow/2026-10-25-relmap-r2-batch/evidence/review-inc004.md` (sha256 `411f519c71d4ede120435d13a243d38347ffdcac472cbeb402ace7365f95752f`) |

Follow-ups (3 MINOR, discharged in the review follow-up unit):

| Finding | Disposition | Evidence |
|---|---|---|
| F1 — `_budget` floors explicit heights 2–4 up to 4 | **fixed**: the floor now applies to the degenerate value only — `max(height if height > 1 else _DEFAULT_BODY, 1)` (`mapper/screens/relmap/gaps.py:68-75`); explicit heights 2–3 paint 2–3, the degenerate 1 still paints the honest default body 24; arm `test_rvg_1_4_explicit_heights_2_to_3_are_respected_not_floored` (RED on the unmodified source: "explicit height 2 painted 4 rows") | `evidence/p3-inc004-followup-red.txt` (sha256 `e4804305527114a999517d2a3d873ad69c6e2083753d97ff46a4acb3117a205f`) · `evidence/p3-inc004-followup-green.txt` (sha256 `46e0cbae4515988b686c269ad43f489a2c4ca227c4d6f0b7df01d17e7a6f2cad`, 34 passed) |
| F2 — the by-kind partial band take is unsignalled inside a split band | **accepted** — the split is correct and counted (`+NN more`); no shipped fixture splits (reference class and the 87 sweep); only very large single-kind catalogues hit it. BACKLOG **B-160** (a future amendment could reserve whole bands) | `.dev-flow/BACKLOG.md` B-160 |
| F3 — the not-computed re-issue costs one full ranking pass per paint | **accepted with reason** — declared in §1.1/§5 and measured at cap scale (`0.663s`/`0.701s` per paint at 100k rows); the cost is bounded, memoized, and the painted rows are never re-sorted; the D1 `gaps_not_computed` channel, if ever added, deletes the re-issue | `evidence/p3-inc004-measure.txt` |

---

## 5 · Risks

- The mount-time viewport-height floor (§1.2) is the load-bearing
  workaround: if the trunk ever gives `#relmap-canvas` a stylesheet height,
  the floor becomes dead code but harmless (explicit heights always win).
  Flagged for the shell lane (Inc-6) as a candidate host improvement — a
  HOST change, so not made here (F-3).
- The not-computed re-issue (§1.1) costs one extra deterministic ranking
  pass per paint (memoized reach; at the 100k cap ≈ the same sort cost the
  host already paid — measured in `p3-inc004-measure.txt`). If a future D1
  amendment adds a `gaps_not_computed` channel, the re-issue drops out.
- M-RVG-12's specced shape is unobservable against the one sink (see the
  battery note); the killable variant guards the real axis. If a future
  renderer assembles canon text outside `base.label`, the specced mutant
  regains its teeth.

## 6 · Renders vs the prototype references (honest deltas)

Rendered at (118,34) and (87,34) through the real app, ranked + by-kind —
`evidence/p3-inc004-measure.txt`. Deltas against
`prototypes/round-2026-10-23/shots/png{,87}/gaps-{ranked,by-kind}.png`, all
deliberate:

1. Casing: the shipped view is Darkside lowercase (`hlr without llr`, `med`,
   `high 0 …`); the PNGs show the rejected Solari ALL-CAPS (operator verdict
   2026-10-24 — NOT the shipped direction; HLR-RVG.2 exists precisely to
   pin this).
2. No group box or seam rules: the shipped host owns the chrome (tab strip,
   crumb, notice, keybar); the renderer paints the body plain, per the D1
   paint contract.
3. The honest skeleton paints 7 `hlr without llr` gaps, all `med`, reach
   `000` (the P2 live probe: 7 gaps, reach 0, not-computed 0) — not the
   prototype's 8-gap fictional catalogue.
4. Chips are space-separated (`high 0   med 7   low 0   total 7`) without
   the prototype's seam rows; the `total` chip is bold, no WARN tone on
   chrome (ruling `LED-2026-10-25-r2.05`).
5. The by-kind hint is bottom-anchored on the canvas (the prototype's hint
   was a host `HintLine`; the shipped host has no hint channel).
6. The crumb names the shipped host format (`reqharness / relmap / gaps`,
   `· by kind` after `k`) — see §1.3.

## 7 · AT-137 measurements (COND-QA-3 — packet-recorded, never committed asserts)

Recorded in `evidence/p3-inc004-measure.txt`:

- `303-node skeleton derivation baseline (median of 5, warm): `0.005s` (runs 0.013/0.003/0.004/0.005/0.006) — **recorded 10× budget: `0.048s`** (proposal §3 Resource; `LED-2026-10-25-r2.09`)`
- `app-level 303-node open/`r` through the real host: `open_wall=0.050s`, `r_wall=0.110s`, with the derivation itself instrumented inside the app: `derive_calls=[0.005s, 0.004s]` — the derivation is ~10× UNDER the recorded budget (the wall figures are dominated by pilot/event-loop pause overhead, not derivation)`
- `cap-scale 100k map (`MAX_NODES`): build `0.257s`, detect `0.224s`, rank `0.361s` (100,000 gaps, not-computed 0); gaps-window paint with the cursor on the last row: `0.663s` at 118, `0.701s` at 87 — the window bounds the work; the assertions (declared cuts, discipline census, cap-scale row count) are committed in `tests/test_relmap_scalecheck.py`, clock-free per COND-QA-3`
- AT-137's cross-view portions (the matrix row-window and the sheet
  overflow line at cap scale) are **join-time (F-5)**: they need the other
  lanes' renderers, absent in this tree. The gaps portions (the window, the
  declarations, the discipline census) run here at 118 AND 87, including
  the cap-scale window over 100,000 ranked rows.

## 8 · Pending items / spec deviations

- None against the contract beyond the six declared reconciliations in §1
  (each is a ruling this packet records for the PDR/contract annotation —
  see §Records to integrate).
- COND-UX-2 discharged: the per-band membership oracle arm runs in
  `test_rvg_1_5_by_kind_bands_match_the_membership_oracle` (per-band id sets
  AND order vs the oracle grouping of the ranked catalogue).
- COND-QA-3 discharged: the 10× budget is a recorded packet measurement
  (`§7`); no committed test reads a clock.
- COND-SEC-1 discharged for the gaps view: the hostile arm runs unit-level
  (full payload incl. raw LF/TAB through `build_map`) and app-level (canon-
  carried payload through the real derivation).

## 9 · Suggested next task

Lane L4 is done; the join (F-5) runs every lane's ATs on the joined tree —
AT-137's cap-scale matrix/sheet portions and the full AT-135…139 battery
across the three landed renderers.

## Records to integrate (proposed — nothing applied by this lane)

1. **PLAN test-ledger rows** (orchestrator fills at the join): +33 nodes
   (`tests/test_relmap_gaps_view.py` 27 + `tests/test_relmap_scalecheck.py`
   6 — counted from the GREEN transcript); guard set unchanged
   (`206 passed, 3 xfailed`).
2. **Ledger entries** (for `01-requirements-ledger.md`):
   - `LED-2026-10-25-r2.19` — LLR-RVG.1.1 reconciliation: the not-computed
     count rides the frozen D1 surface as a re-issue of the host's own
     deterministic ranking call (memoized reach); the painted order is
     `state.gaps`, never re-sorted (increments 002/004).
   - `LED-2026-10-25-r2.20` — the relmap canvas `#relmap-canvas` mount-time
     height is degenerate (auto-height `Static`, first paint `height=1`);
     renderers treat explicit `ViewState.height` as the budget and may floor
     the degenerate value; a host stylesheet height is a trunk (shell-lane)
     candidate, not a lane change (F-3).
   - `LED-2026-10-25-r2.21` — AT-135 crumb ruling: the asserted
     `gaps · reach count` is the prototype scene label; the shipped crumb
     word channel is the toggle state word only — at open
     `name / relmap / gaps`, after `k` `name / relmap / gaps · by kind`.
3. **Contract annotation** (`01-requirements.md` LLR-RVG.1.1, non-normative
   note): the renderer-side count derivation of §1.1 above.
4. **No `docs/ARCHITECTURE.md` amendment**: `screens/relmap/gaps.py` is the
   lane-owned renderer the §4 freeze row already names; the freeze text is
   untouched (D1 unchanged — zero host edits).

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1/4 — exactly the one lane-owned renderer |
| 2 | Tests written in this same increment | all | ✓ | both test files new, run RED-before-GREEN |
| 3 | Layer 0 written where the criterion applies | `full` | ✓ | casing/sink AST censuses + notice obligation + fixture positive control |
| 4 | RED counterfactual declared | all | ✓ | code-absent (exit 2) + move-aside (exit 2), restore sha256-proven |
| 5 | Reverse census declared | all | ✓ | §Reverse census — 5 probes; B2/B3 not fired; B4/A3 clean |
| 6 | `code-reviewer` passed | all | ⚠ | `pending — orchestrator schedules` (§4b) |
| 7 | No file from another lane touched | all | ✓ | SOURCE = `gaps.py` only; sibling worktrees untouched; tests are lane-new |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D1–D5 untouched — zero host edits; the renderer reads the surface as amended |
| 9 | Coverage claims verified on disk | all | ✓ | 33 targeted nodes collected on disk in the final run |
| 10 | Load-bearing emptiness declared | all | ✓ | §Load-bearing emptiness — positive controls named per absence |
| 11 | Mutation verdicts declared | all | ✓ | 13/13 KILLED per arm, restore digests cited, battery exit 0 |
| 12 | Instrument RED-proof declared | all | ✓ | 3 instruments each shown RED first (incl. the runner's own BAD control) |
| 13 | Correction population declared | all | ✓ | 0 corrections — enumerated by the green guard run (no census failed) |
| 14 | Emitted-form assertion declared | all | ✓ | 3 artifacts asserted on emitted bytes (rows, composited frame, hostile frame) |
| 15 | Independent review names somebody | all | ✓ | `pending — orchestrator schedules` (§4b) |
| 16 | Evidence files declared | all | ✓ | 7 files at `artifact_homes.evidence`, digests of stored bytes |
