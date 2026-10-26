# Increment 005 — HLR-RVS.1–6 · the node-sheet renderer (lane L5, sheet)

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `005` |
| Lane (if the batch forked) | L5 · `screens/relmap` renderer — `mapper/screens/relmap/sheet.py` |
| Requirement(s) | `HLR-RVS.1–6` · `LLR-RVS.1.1–7.1` — over the frozen D1 surface (`base.py`) and the D3 (R1) query API; D5 glyph table; COND-ARCH-1 (`toggle`), COND-SEC-1 (the one sink), COND-QA-5 (the M-RVS-9 synthetic kill), COND-SEC-2 (the 100k c-chain BFS wall-clock) |
| Acceptance | `AT-140…AT-144` through the real host (`run_test()`, real keys, C-16) · `TC-RM-17` (the synthetic 3-level chain) · mutants `M-RVS-1…M-RVS-12` |
| Agent | `lane agent` (L5 · sheet) |
| Date | `2026-10-25` |

---

## 1 · What changed

BLUF: the node-sheet renderer is real. `mapper/screens/relmap/sheet.py` lands
against the frozen host↔renderer surface with **no host edit** (F-3): the
two-row header (`<id> · <title>` bold INK through the one `base.label` sink +
the `darkside.kind_chip` badge, **no** source/path segment — the D3 `Node`
exposes none, OQ-SHEET-7), the two banded sections — `feeds it`
(`RelMap.up(focused)`) and `a change reaches` (`RelMap.down(focused)`) — in
edge input order with the frozen D5 evidence-glyph column (refines none ·
verifies/covers `✓` SAGE / `!` ALERT on `evidence_missing or in_cycle` ·
binds `●` SAGE / `◐` WARN graduated; never `○`), honest declared empties
(`╌╌ none on record` in MUT immediately under every band), the focused node's
own gaps consumed **as given** from the host-supplied ranked rows
(`! <kind>  <sentence>`, kind in bold ALERT, Darkside-cased, one trailing
ellipsis), the per-direction minimum-distance-2 hop-2 cuts
(`╌╌ +NN more upstream/downstream at hop 2 — c shows the chain`,
zero-padded, omitted at zero), the `c` density toggle (rows, `next ▸` note and
crumb word flip together; words `direct only` / `stacked chain`;
`enter`/`k` return `""`), stacked density listing every distinct node by
per-direction minimum hop (`↑N`/`↓N`, unbounded, the counted `… +NN more`
viewport line as the safety valve), and width discipline enforced
structurally: every row is blitted onto a `mapper.canvas.Canvas`
(`Canvas(w, h, audit=...)` — the C10 mapping is constructor-injected, zero
`clip`/`overprint` in every sweep arm) so a row can never exceed the canvas.

Edge orients and labels are read **through the D3 query surface only**
(`up`/`down` layering, `RelMap.node`, `RelMap.edges`); the connecting edge of
a chain row is looked up in change-flow orientation (the profile's direction
bit, exactly `build_map`'s rule), so upstream-type edges (verifies/binds/
covers) name their type and glyph correctly from either section.  Every
canon-derived string is coerced through `darkside.plain` and cut through
`darkside.fit` before it is styled (the C-10 order); LF/TAB/CR become single
spaces at the seam, so a hostile payload renders byte-literal on ONE row.
Evidence names are labels only: no file-opener import, no `.render(` call
(the A3 census), no attachment (LLR-RVS.7.1).

**Fork preconditions re-read at entry (F-1…F-5, proposal §2.1):** F-1 PASS
(the text leaf landed Inc-1a+1b; `relmap/text.py` exports `cut`/`DISPLAY_MAX`/
`refusal_line`) · F-2 PASS (`base.py` carries the amended D1 surface —
`ViewState(relmap, notice, focus, cursor, gaps, width, height)`,
`row_count`, no `lens`; the freeze text names `enter`/`c`/`k`,
`direct only`/`stacked chain`) · F-3 PASS (`sheet.py` did not exist;
`matrix.py`/`gaps.py` absent from this tree; no sibling-lane or trunk file
touched) · F-4 this increment's reverse census below · F-5 PASS (the
AT-driver probe re-run in this worktree: `MapperApp(workspace=<tmp>)` +
`run_test()` reaches Home, a pushed `RelMapScreen` derives the seeded
fixture map, `q` returns — `evidence/p3-inc005-fcheck.txt`).

One host observation, resolved renderer-side (same convention the gaps lane
landed): the host's canvas `Static` is auto-height, so the first paint
arrives with the degenerate viewport height 1. The renderer treats an
explicit height as authoritative and paints an honest default body (24 rows)
for the degenerate 1; the growing widget then reports a real height back.
No host change (F-3 holds).

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/relmap/sheet.py` | source | HLR-RVS.1–6 · LLR-RVS.1.1–7.1 | NEW — the sheet renderer (317 lines): `SheetView` over the D1 surface (`paint`/`row_count`/`toggle`), the D5 glyph table, per-direction BFS layering through `up`/`down`, change-flow edge indexing, Canvas blit with the C10 audit mapping, `build_view()` |
| `tests/test_relmap_sheet.py` | test | LLR-RVS.1.1–7.1 · AT-140…144 · TC-RM-17 · M-RVS-1…12 | NEW — 29 nodes: inline synthetic `build_map` fixtures (ARC-05; `_relmap_fixtures.py` untouched) — an asymmetric CAPS-profile map (section oracles + casing), a glyph table map (every D5 row, three foci), the synthetic 3-level chain (TC-RM-17), a per-direction hop-2 map (M-RVS-7), a hand-wired cyclic diamond (OQ-SHEET-5 / M-RVS-8 — see Load-bearing emptiness), gap/gaps-order maps, an overflow map, a hostile map; the AT-140…144 pilot arms through the real host; the C10 sweep; the read-only census; the D1 wiring pin |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc005-*.txt` | generated | US-RMV-003 | F-check, RED ×2, GREEN ×2, mutation battery + BAD control, renders, the COND-SEC-2 measurement — redacted, hashed |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** |
| Test files | 1 (new; uncapped) |
| Doc files | 0 |

## 3 · How to test

```bash
PYTHONPATH=<worktree> python -c "import mapper; print(mapper.__file__)"   # inside wt-r2-sheet
# targeted (the sheet arms):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider tests/test_relmap_sheet.py
# the guard set (as the commission lists it):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_fold.py tests/test_repair_artifact_claims.py
# pre-commit privacy gate:
python -m pytest -q -p no:cacheprovider tests/test_no_operator_paths.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `full` | the sink/emit path (branchful coercion + width budgets), the glyph table, the layering oracles — driven through `paint()` on synthetic maps | passed (in the 29) |
| **A · white-box** `TC` ↔ LLR | `full` | `tests/test_relmap_sheet.py` — section oracles on the asymmetric fixture, glyph styles, honest empties, hop-2 cuts vs the `neighbourhood(2) − neighbourhood(1)` behavioural oracle, stacked markers on the wired diamond, `c` toggle state, gaps-as-given, width/audit sweep at 118/87 × direct/stacked, counted overflow, censuses | 29 passed — `evidence/p3-inc005-green-targeted.txt` |
| **B · black-box** `AT` ↔ story | `full` | AT-140 (linked LLR: header/chip/`↑1 refines`/declared empties/no source segment), AT-141 (`c` flips crumb word + note, one-hop rows byte-identical across densities, round-trip), AT-142 (the node's own gap, bold ALERT kind, one ellipsis at 87), AT-143 (87-col width audit + the counted `… +NN more` last body line in MUT through the real host), AT-144 (hostile title byte-literal, no ACCENT/ALERT/WARN span, `q` leaves cleanly) | 29 passed (targeted); guard set 206 passed, 3 xfailed — `evidence/p3-inc005-green-guards.txt` |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (1) code-absent: `sheet.py` does not exist — the new test file fails at collection (`ImportError: cannot import name 'sheet' from 'mapper.screens.relmap'`); (2) move-aside (C-20): the landed `sheet.py` renamed out of the tree |
| Instrument | project code, lane agent's hand (no stash; C-20 move-aside) |
| Where it ran | this worktree, lane agent (no other session reading — the battery and the runs were serialized) |
| Transcript | `evidence/p3-inc005-red-code-absent.txt` — exit 2, 1 collection error, wall 0.7s; `evidence/p3-inc005-red-move-aside.txt` — exit 2, same collection error, restore sha256 `ebadfcf9…84c2` MATCH |
| Restore proven by | move-aside restore sha256 MATCH (printed in the transcript); the code-absent state needed no restore |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` in every run (C-46) |
| Arms resolved at baseline | 2 RED arms, each seen failing |
| Verdict granularity | per arm; collection errors are the expected failure shape for import-level absence |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | code-absent + 1 move-aside arm, transcripts at `evidence/p3-inc005-red-code-absent.txt` (sha256 `dd42ec81…4b8`) and `evidence/p3-inc005-red-move-aside.txt` (sha256 `3a5cac6a…f6d`) |

| Field | Value |
|---|---|
| **Mutation verdicts** | **12/12 KILLED**, per arm, restore sha256 proven for every arm (baseline `ebadfcf9…84c2` MATCH ×12), runner exit 0 · M-RVS-1 (header into a markup-parsing sink → the hostile arm + the header arm RED) · M-RVS-2 (`e.type`/`g.kind` verbatim caps → the casing census + oracles RED) · M-RVS-3 (edge looked up in the wrong direction → the asymmetric section oracles RED) · M-RVS-4 (sections swapped → both section oracles RED) · M-RVS-5 (glyph keyed on the neighbour's kind → the glyph table RED) · M-RVS-6 (empty section skipped → the honest-empty arms RED) · M-RVS-7 (both-direction hop-2 count → the TC-RM-17 cut-count arm RED: `+03` painted where the oracle says `+01` / omitted) · M-RVS-8 (BFS depth through both directions → the wired-diamond stacked markers RED: `↑1` painted where the per-direction minimum is `↑2`) · M-RVS-9 (note flips, rows do not — COND-QA-5: killed by the SYNTHETIC 3-level arm: `↑2` row + note flip together; the live-skeleton rows-unchanged arm is asserted at AT-141 and is NOT the kill) · M-RVS-10 (gaps filtered by severity → the node's-own-gaps arm + AT-142 RED) · M-RVS-11 (raw title painted → the 87-col width/audit sweep RED) · M-RVS-12 (rows dropped past the viewport with no counted line → the overflow arm + the AT-143 black-box arm RED) · arms that stayed GREEN: none · transcript `evidence/p3-inc005-mutants.txt` (sha256 `fef5784d…75`) |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` | the code-absent + move-aside states | exit 2 collection errors, both transcripts |
| the mutation runner | its own `--bad-control` (M-RVS-1's application no-opped — the anchor applied zero times) | `M-RVS-1: rc=0 SURVIVED — 29 passed`, `RESULT 11/12 killed`, runner exit 1 — `evidence/p3-inc005-mutants-badcontrol.txt` |
| the runner's anchor assertion | M-RVS-4's colliding anchor in the first BAD-control pass (a real instrument defect, caught before the real battery) | `M-RVS-4: BAD-INSTRUMENT anchor occurs 2 times` — runner stopped; the anchor was disambiguated and the battery re-run clean |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the painted rows (`paint()` → `Canvas.rows()`) | every row `cell_len == w` at (118,34) and (87,34), direct + stacked, with the C10 audit mapping injected: `clip`/`overprint` empty | 8/8 sweep params clean; `evidence/p3-inc005-green-targeted.txt` |
| the composited screen frame (AT arms) | `frame_text`/`frame_runs` over `screen._compositor.render_strips()` — merged same-style runs — asserting the exact section rows, the crumb words after `c`, the bold ALERT gap kind, the MUT counted line | the asserted strings, byte-exact (modulo fit padding the canvas width owns) |
| the rendered hostile payload | the painted frame contains `[bold]red[/]` byte-literal, no `\x1b`/BEL/U+202E, and no ACCENT/ALERT/WARN run carries payload text | literal on one row; `q` leaves to Home |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted on its emitted bytes |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| lane-entry F-check + AT-driver probe | `…/evidence/p3-inc005-fcheck.txt` | `5b049ee7bc246d8b70c62bed1f1f651d9795fd5037cb7a53557235fe8b725b87` |
| RED code-absent transcript | `…/evidence/p3-inc005-red-code-absent.txt` | `dd42ec813a4bd9ca386c12a0fef8a575fa9c54cde1fac27bf9522397472124b8` |
| RED move-aside transcript | `…/evidence/p3-inc005-red-move-aside.txt` | `3a5cac6ab9c23fc5c576c40f944441a9751bd08fcd777523c42cc2331f9aff6d` |
| GREEN targeted transcript | `…/evidence/p3-inc005-green-targeted.txt` | `fd27e1c3d19ff99c7a3328e90e8506430caa68c2476b88c9445f3ba785947755` |
| GREEN guard transcript | `…/evidence/p3-inc005-green-guards.txt` | `95c9f0a7e6d70f9f5d4b54011bda8a6e3b545da81b9ce02f44a8661180a14364` |
| mutation battery transcript | `…/evidence/p3-inc005-mutants.txt` | `fef5784d5688cafd56571b340ff8bdc590fc7caa16dc408b24e911776ed58c75` |
| mutation battery BAD control | `…/evidence/p3-inc005-mutants-badcontrol.txt` | `b52eba45424755d269b820e0bdb9641be02fead789f827fb675f1c0aabf1ebc8` |
| render captures (118/87 × direct/stacked) | `…/evidence/p3-inc005-renders.txt` | `2397f02203f2186c48ede8b35f398ed443353fa58584fd7d5e12643c8dc39d6e` |
| COND-SEC-2 100k BFS measurement | `…/evidence/p3-inc005-sec2-bfs.txt` | `a10375b515b1db7bf6e41d1d2a8c5df7dcd63af2ac9254b9546f573b9ee8cfba` |

All transcripts redacted (account name → `<user>`) with a PYTHON script before hashing; exit codes and wall time in each header; `PYTHONDONTWRITEBYTECODE=1` in every run.

| Field | Value |
|---|---|
| **Evidence files** | 9 artifacts, each at the declared home, cited with the digest of its stored bytes |

### COND-SEC-2 — the c-chain BFS at the 100,000-node cap

| Field | Value |
|---|---|
| Measurement | 100,000 nodes / 99,999 edges (the shipped `MAX_NODES` cap), built INLINE via `build_map` (ARC-05); stacked-density `paint` of the root focus = **0.164 s** (direct density 0.185 s; `build_map` itself 0.756 s) — the full-chain BFS + counted overflow (`… +99974 more`) at the cap |
| Budget | the 10× derivation idiom: ~10 s class — the measurement sits ~60× inside; **never a committed wall-clock assert** |
| Recorded at | Phase 3 — `evidence/p3-inc005-sec2-bfs.txt` |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — (a) the reqharness change-flow graph is a **DAG** (every profile edge type orients US/HLR/LLR → … → AT/TC sinks; up-reachable and down-reachable sets can never intersect), so OQ-SHEET-5's both-sections row and M-RVS-8's mixed-depth marker are **unreachable on a profile-valid `build_map` map**; (b) the shipped host's canvas `Static` is auto-height (the degenerate first-paint height 1); (c) the host stores the toggle-state word only after a toggle (the first-open crumb carries no word) |
| If the result is an ABSENCE, what made the search wide enough | (a) the orientation rule was re-derived from `build_map` (`mapper/relmap/model.py:293-301`) and exercised over every edge type in the glyph fixture — the up/down sets are disjoint on every profile-valid map by construction, so the both-sections/mixed-depth arms run on a **hand-wired cyclic `RelMap`** (the same wiring idiom as the in-cycle glyph arm) — a synthetic instance of the absent case, not a vacuous skip; (b)/(c) measured on the real host: `canvas.size.height == 1` after settle; crumb `demo / relmap / sheet` on first open |
| Guard labelled as protecting a CONCLUSION, not a behaviour | the wired-diamond arm asserts the per-direction markers (`↑2`) against the mixed-depth mutant directly; **corrected per review-inc005 F1:** the degenerate-height convention was NOT pinned at packet time — the AT pilots read the frame only after the auto-height canvas has grown, so the mount-time degenerate paint was invisible to every oracle (the original sentence here claimed the AT arms pinned it; that claim was false). The pin is the follow-up unit arm `test_llr_rvs_6_1_degenerate_height_paints_the_honest_default_body` (discharged in the §4b follow-ups) |
| Conjunctive criteria: one mutation per conjunct | M-RVS-7 (the count) and M-RVS-8 (the marker) are distinct conjuncts of the per-direction layering; M-RVS-1/M-RVS-11 the two header conjuncts (sink vs fit); M-RVS-5 the glyph-key conjunct |
| Synthetic instance of the absent case | the wired LLR-F → TC-C → HLR-A → LLR-F cycle (both-sections row + `↑2` marker); the hostile fixtures (title/id/sentence with `[bold]`, ESC, BEL, TAB, LF, U+202E) are the synthetic hostile instances |
| **Positive control for every probe that returned an ABSENCE** | the fixture positive control derives the seeded 4-node map through the real adapter (`test_fixture_canon_derives_through_the_real_adapter`); the AT-driver probe derives the same map through the pushed screen (`p3-inc005-fcheck.txt`); the wired maps carry the in-cycle flag the profile cannot build (the `!` ALERT arm) |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rln "screens.relmap.sheet\|relmap import sheet" tests/ mapper/` | one reader — `tests/test_relmap_sheet.py` (this lane's file); `base.build_view` resolves the module by name convention (`mapper/screens/relmap/base.py:176`), no import edge |
| B2 file moved on disk | `git log --oneline -- mapper/screens/relmap/sheet.py` | net-new file — no old path exists; not fired |
| B3 byte-identical golden captures this source | `grep -rln sheet tests/goldens/` | no hits — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rn "SheetView\|_WORD_STACKED\|_FEEDS_BAND" mapper/ tests/` outside the module | zero consumers outside the sheet module and its test file — the lane owns exactly its file |
| A3 interface consumed by another module changed | `grep -rn "\.render(" mapper/screens/relmap/` + `tests/test_a3_census.py`'s pinned count + `tests/test_arch_osopen_callers.py` | the sheet paints Canvas cells directly — **no** `.render(` call; **no** `osopen` edge from `screens/relmap`; both censuses pass unchanged in the guard-adjacent runs (`test_no_operator_paths.py` green before the commit) |
| the fold-state `.toggle(` census | `tests/test_fold.py` (in the guard set) | the sheet DEFINES `toggle` and never CALLS `.toggle(` — no allowance needed; the guard passes unamended |

| Field | Value |
|---|---|
| **Reverse census** | 6 probes run (B1 · B2 · B3 · B4 · A3 · fold); B2/B3 not fired; B4/A3/fold clean with no census amended |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| — none — | no existing census names the new module | the guard set (`tests/test_fold.py`, `tests/test_repair_artifact_claims.py`) + the privacy/A3/osopen censuses were run against the tree BEFORE the first edit and after landing; none failed | 0 | none | n/a — a net-new source file plus its own test file, exactly the lane's declared file set (proposal §2.1, Inc-5) |

| Field | Value |
|---|---|
| **Correction population** | 0 corrections — every guard and census in the commission's list passes unamended with the new files present (the guard run before the first edit is the enumeration: nothing failed, nothing to amend) |

### Signed-balance test ledger

`post = base − deleted + added`: targeted `29 = 0 − 0 + 29` (one new test file, 29 nodes; nothing deleted, no existing file touched). Guard pair unchanged node-for-node: `206 passed, 3 xfailed` before and after (the two guard files are untouched; the tally is the pair's own, run standalone). COND-SEC-2 is a recorded measurement, not a ledger row. Proposed PLAN test-ledger rows are in Records to integrate (nothing applied by this lane).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Kimi K2.8 subagent executing agents/code-reviewer.md + agents/security-reviewer.md + agents/ux-reviewer.md · iterate → discharged fb336ed` |
| Review record | `.dev-flow/2026-10-25-relmap-r2-batch/evidence/review-inc005.md` (sha256 `a139c81c0a8c20e4783ca67f3776049e0dc34888407119be59db95a0462d9199`) |

Follow-ups (2 MAJOR test-only + 2 MINOR, all discharged in the review follow-up unit):

| Finding | Disposition | Evidence |
|---|---|---|
| F1 — the degenerate-height default body (`_budget`) was unpinned, and the packet's Load-bearing-emptiness table claimed a pin that did not exist | **fixed** (test-only, no source change): arm `test_llr_rvs_6_1_degenerate_height_paints_the_honest_default_body` — `h=1` paints the honest default body of 24 rows header included, explicit heights (2, 17, 34) are respected as-is; the reviewer's surviving mutant **M-REV-1** (floor flattened to `max(height, 1)`) is now **KILLED**, restore sha256 MATCH; the packet's Load-bearing-emptiness claim is corrected in place (the AT pilots read the frame only after the auto-height canvas has grown — the original sentence claimed the AT arms pinned the mount-time paint; that claim was false) | `evidence/p3-inc005-followup-mutants.txt` (sha256 `5dd5e23a6eb7ff47c804e6f2b588664f68b44733ec5c3ff8319cf556c5dd67dd` — M-REV-BAD control PASS, M-REV-1/2 KILLED, restores `1ff155ee…d767` MATCH) · `evidence/p3-inc005-followup-green.txt` (sha256 `514675a358f5a4b5fc678a2ecf26136c451aeb492b17876b0b3d3e633e58dcb1`, 30 passed) |
| F2 — the stacked hop≥2 id gradation (`INK`→`MUT`) was unpinned | **fixed** (test-only): `test_llr_rvs_3_2_stacked_lists_every_node_by_minimum_hop` gains the id-style oracle — the hop-1 id carries INK, the hop-2 ids carry MUT (both sections); the reviewer's surviving mutant **M-REV-2** (gradation flattened to plain INK) is now **KILLED** | same battery transcripts |
| F3 — cut-line hatch count: the Statement says two hatch chars, the draft-time verification cites the PNG's four | **recorded for the DDR** — the lane paints two (`sheet.py:181-183,189-191`), matching the normative Statement and LLR-RVS.2.4's empty-line grammar; the DDR is asked to ratify **two (the Statement wins)** so the ambiguity does not resurface at the join; no document edit applied | packet §6 (this section) |
| F4 — AT-144's real-screen hostile arm carries no LF/TAB | **noted, traceability closed** — the canon parser structurally excludes LF/TAB before any label exists (`parse_canon` line-splits before cell parsing, `mapper/reqharness/derive.py:145`; `_collapse` normalises TAB to space, `:128-131`), so the hostile bytes an operator can type are covered by the pilot; LF/TAB coverage lives at the renderer seam — the lane's hostile fixture (`tests/test_relmap_sheet.py:285-301`, TAB in a title, LF in an id/title, one-row, no raw bytes) is the only place they can enter; a pointer comment now sits in the AT-144 pilot arm | `tests/test_relmap_sheet.py` (`test_at_144_hostile_payload_on_the_sheet`) |

---

## 5 · Risks

- The crumb carries no toggle word on first open (the host stores the word only after a toggle) — AT-140's `sheet · direct only` crumb reading is discharged as `name / relmap / sheet` + the note line on first open, both words asserted after the real `c` round-trip (AT-141). Same convention as the gaps lane (`by kind`). A contract clarification is proposed in Records to integrate.
- The degenerate mount-time viewport height (host canvas auto-height) is absorbed renderer-side (default body 24). If the trunk later gives the canvas a fixed height, the convention is a no-op (explicit heights are always respected).
- The reqharness flow DAG makes the both-sections / mixed-hop cases reachable only on wired synthetic maps; the arms are honest about it (Load-bearing emptiness) and the DDR's crossed census can re-verify the claim from `model.py`.

## 6 · Pending items / spec deviations

- **AT-140 crumb (declared):** first-open crumb reads `demo / relmap / sheet`; the density word lands after the first `c`. The note line declares the density from the first paint. Amendment text proposed in Records to integrate.
- **AT driver order in the lane tree (declared):** the joined AT moves the cursor on the landed matrix, then presses `3`. In this worktree the matrix is still the `PendingView` placeholder (its cursor is an honest no-op, pinned by the trunk's own arms), so the lane's pilot switches with `3` first and moves on the SHEET's own node axis — the same end state the AT asserts.
- **Prototype-PNG deviations (all ruled):** row 1 is the kind chip only (no `TC · tests/…` segment — OQ-SHEET-7; the D3 `Node` exposes none); section rows sit immediately under the band (LLR-RVS.2.4), no blank spacers or seam line; labels are Darkside-lowercase (OQ-SHEET-1) where the PNG caps them; the row grammar is `↑1 <type> <id><glyph>` with single spaces (LLR-RVS.2.1's statement form), not the prototype's 10-cell type field; the note lives inside the sheet body (renderer-owned) rather than in a separate hint widget; the crumb word and the `+NN` cut exist only when non-default/the count is non-zero.
- **Live-skeleton honesty:** the fixture canon's one-hop `refines` chains render the cut line omitted at zero and both sections' hop-1 rows; the prototype's 3-level demo chains do not exist on the live-class map (the synthetic 3-level arm of AT-141/TC-RM-17 covers them; the `+01` PNG cut line is reproduced there).
- Nothing else against the contract. COND-QA-5 discharged (the M-RVS-9 kill is the synthetic 3-level arm; the note/rows flip is asserted together). COND-SEC-2 discharged (recorded, never asserted).
- **Cut-line hatch count (review-inc005 F3 — recorded for the DDR):** LLR-RVS.3.1's Statement (`01-requirements.md:636-641`) says the cut line opens with TWO hatch chars (`╌╌`); its own draft-time verification line cites the prototype PNG's FOUR hatch chars as governing. The lane paints two (`sheet.py:181-183,189-191`), matching the normative Statement and LLR-RVS.2.4's empty-line grammar. **The DDR is asked to ratify two (the Statement wins)** so the ambiguity does not resurface at the join; no document edit applied by this follow-up.
- **LF/TAB at the AT-144 pilot (review-inc005 F4 — noted):** the canon parser structurally excludes LF/TAB before any label exists (`parse_canon` line-splits before cell parsing, `mapper/reqharness/derive.py:145`; `_collapse` normalises TAB to space, `:128-131`), so the hostile bytes an operator can actually type through a canon file are covered by the pilot arm; LF/TAB coverage lives at the renderer seam, where the lane's hostile fixture (`tests/test_relmap_sheet.py:285-301` — TAB in a title, LF in an id/title, asserted one-row, no raw bytes) is the only place they can enter. A pointer comment now sits in the AT-144 pilot arm.

## 7 · Suggested next task

The matrix lane (L1) and the shell lane (Inc-6) continue in their own worktrees; the join (F-5) runs every lane's ATs on the joined tree before the DDR. The Records to integrate below are for the orchestrator: nothing in them is applied by this lane.

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1/4 — a single renderer file, exactly the lane's declared set (proposal §2.1 Inc-5) |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_relmap_sheet.py` new (29 nodes), run RED-before-GREEN |
| 3 | Layer 0 written where the criterion applies | `full` | ✓ | the coercion/width-budget emit path (branchful), the glyph table, the layering oracles — unit arms in the 29 |
| 4 | RED counterfactual declared | all | ✓ | code-absent (exit 2) + 1 move-aside arm (exit 2), restore sha256-proven |
| 5 | Reverse census declared | all | ✓ | §Reverse census — 6 probes; B2/B3 not fired; B4/A3/fold clean, no census amended |
| 6 | `code-reviewer` passed | all | ⚠ | `pending — orchestrator schedules` (§4b) |
| 7 | No file from another lane touched | all | ✓ | one new source file + its own test file + this packet + evidence; `git status` clean of stray files at the commit |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D1 consumed, not edited (no host change — the degenerate viewport is absorbed renderer-side); D2/D3/D4/D5 untouched |
| 9 | Coverage claims verified on disk | all | ✓ | 29 targeted nodes collected on disk in the final run; AT-140…144 each with a named node |
| 10 | Load-bearing emptiness declared | all | ✓ | §Load-bearing emptiness — the flow-DAG fact, the degenerate height, the crumb word; synthetic wired instances per absence |
| 11 | Mutation verdicts declared | all | ✓ | 12/12 KILLED per arm, restore digests cited, battery exit 0, BAD control on file |
| 12 | Instrument RED-proof declared | all | ✓ | 3 instruments each shown RED first (incl. the runner's own BAD control and its anchor assertion catching a real instrument defect pre-battery) |
| 13 | Correction population declared | all | ✓ | 0 corrections — the guard run before the first edit enumerated the population (nothing failed, nothing amended) |
| 14 | Emitted-form assertion declared | all | ✓ | 3 artifacts asserted on emitted bytes (paint rows + C10 audit, composited frame, hostile payload) |
| 15 | Independent review names somebody | all | ⚠ | `pending — orchestrator schedules` (§4b) |
| 16 | Evidence files declared | all | ✓ | 9 files at `artifact_homes.evidence`, digests of stored bytes |

## Records to integrate

Proposed by this lane for the orchestrator — **nothing below is applied by this
lane** (exact text; ledger numbers continue after `LED-2026-10-25-r2.18`).

**1 · PLAN test-ledger row (proposed):**

```
| `tests/test_relmap_sheet.py` | lane L5 Inc-005 | 29 = 0 − 0 + 29 | HLR-RVS.1–6 · LLR-RVS.1.1–7.1 · AT-140…144 · TC-RM-17 · M-RVS-1…12 |
```

**2 · Ledger entries (proposed, with requirement pairing):**

```
LED-2026-10-25-r2.19 — the shipped host's canvas Static is auto-height: the
  mount-time viewport height is the degenerate 1; renderer lanes treat an
  explicit ViewState.height as authoritative and paint an honest default body
  (gaps: 24; sheet: 24) for the degenerate 1. Pairs: LLR-RVG.1.4's sweep
  contract, LLR-RVS.6.1/6.2 (the sheet viewport), the AT-130…144 driver's
  real-height bodies. Consumer: the three renderer lanes + the host, if the
  trunk later fixes the canvas height.
LED-2026-10-25-r2.20 — the host stores the per-view toggle-state word only
  after a toggle: the first-open crumb reads `name / relmap / view` and the
  word (`panel lens` / `by kind` / `direct only`) lands after the first home
  toggle. AT-140's and AT-135's first-open crumb readings are amended to the
  wordless form; the density IS declared on first open by each renderer's own
  note/hint line. Pairs: LLR-RVS.3.3, LLR-RVG.1.5, AT-140, AT-135, AT-141.
LED-2026-10-25-r2.21 — the reqharness change-flow graph is a DAG (orientation
  per build_map, model.py:293-301): up-reachable and down-reachable node sets
  are disjoint on every profile-valid map, so OQ-SHEET-5's both-sections row
  and M-RVS-8's mixed-hop marker are exercised on hand-wired cyclic RelMap
  fixtures, not build_map maps. Pairs: LLR-RVS.3.2, OQ-SHEET-5, M-RVS-8.
```

**3 · Contract / ARCHITECTURE amendment (proposed, exact text):**

```
01b-acceptance-design.md AT-140, Observable, first sentence:
  "crumb carries `sheet · direct only`" ->
  "the crumb reads `name / relmap / sheet` and the density note reads
  `next ▸ direct feeders only — the chain is one key away, and the cut is
  declared`; after one `c` round-trip the crumb carries `sheet · direct only`
  (and `sheet · stacked chain` mid-trip) — LED-2026-10-25-r2.20"
```

**4 · Deviation notes for the DDR (no document edit proposed):** the
prototype-PNG deviation list in §6 (chip-only row 1, no spacers/seam,
lowercase labels, single-space row grammar, in-body note, PNG ruled details)
is the comparison baseline the DDR should cite when adjudicating render
fidelity against `shots/png{,87}/sheet-{direct,stacked}.png`.
