# P2 cross-review evidence — QA-REVIEWER lens

- **Role:** QA-REVIEWER (Phase-2 cross-review, independent — authored none of the contract)
- **Date:** 2026-10-25
- **Batch:** 2026-10-25-relmap-r2-batch · worktree branch `feat/relmap-r2`
- **Verdict:** **iterate-to-refine** — the two-layer traceability design is sound and every
  story is black-box testable, but three documentation/deferral defects must be fixed
  before the PDR (stated totals do not match the artifact; two `assumed — verify in
  Phase 2` seams still open; orchestrator rulings not folded back into the contract).

## Findings

| ID | Severity | file:line | What | Recommendation |
|---|---|---|---|---|
| QA-01 | MAJOR | PLAN.md:21, PLAN.md:98-99, 01-requirements.md:920-921 | Stated totals "26 HLR / 52 LLR" do not match the artifact: the contract actually contains **20 HLR headings** (RVM 4, RVG 3, RVS 6, RVH 5, RVT 1, RVU 1) and **51 LLRs** (RVM 10, RVG 9, RVS 14, RVH 14, RVT 3, RVU 1). 51/51 LLRs carry an `Asserting tests` field, so nothing is untested — but one LLR and six HLRs from the claimed totals are unaccounted (lost in the swarm merge, or the counts are stale). Gate (c) cannot be certified against a wrong denominator. | Reconcile the totals: either restore the missing HLR/LLR or correct PLAN header/roadmap and the §5.2 acceptance criterion to 20/51. Re-run the P1 gate after the edit. |
| QA-02 | MAJOR | 01b-acceptance-design.md:13-16, 01-requirements.md:269, 01-requirements.md:964-967 | Seam 1 (AT-driver host push + hostile/synthetic fixture injection) is **still deferred**: every view AT (AT-130…AT-149) opens "fixture workspace → Home → relation row → RelMapScreen", and the injection mechanism remains `assumed — verify in Phase 2`. The deferral is explicit and tracked (F-5 gates the join; PLAN Inc-2 lands the host first), so it is not silently dropped — but as written, no view AT is executable until trunk Inc-2 + the PDR discharge it. | Keep the flag, but make the discharge condition concrete in F-5/PLAN Inc-2: name the fixture-workspace injection point (e.g. a `MAPPER_WORKSPACE` test seam or `MapperApp(tmp_path)` constructor path, as existing tests already do) and verify it exists before lanes 3-5 start, not only at the join. |
| QA-03 | MAJOR | 01-requirements.md:739, PLAN.md:124, 01-requirements.md:269 | Seam 2 (workspace-as-repo derivation path) is **still deferred** — `derive_reqharness_map(workspace, default_descriptor())` treats the Home workspace dir as the repo root; the contract itself flags it `assumed — verify in Phase 2`. Same class as QA-02: examined, not resolved. | PDR must prove the derivation against a fixture workspace that is not a git repo root (AT-147's fixture is exactly this shape — verify `derive_reqharness_map` accepts a bare directory). Close the flag in the ledger once probed. |
| QA-04 | MAJOR | 01-requirements.md:535, 01-requirements.md:755, 01b-acceptance-design.md:92, PLAN.md:124 | The orchestrator ruling (by-kind toggle **SHIPS**: LLR-RVG.1.5 + `k` key) is not folded back: LLR-RVG.1.5 still says "CONTINGENT on the PDR; drafted … to rule in or out", LLR-RVH.4.1 still binds `k` "ONLY IF the PDR ships", and AT-136 still says "dropped otherwise". The contract contradicts the standing ruling; an implementer following the literal text could drop the feature. The ledger — which per the batch convention records rulings — is empty (no entries at all). | Add a ledger entry recording the ruling; reword LLR-RVG.1.5 header, LLR-RVH.4.1 `k` clause and AT-136 to "shipped per ruling <date>"; keep the PDR freeze of the glyph/table details. Same staleness for the hook bound (ruling: 240, cut AFTER escaping) vs LLR-RVU.1.1's "decided at the R2 PDR (recommendation: 240)" — fold it. |
| QA-05 | MINOR | 01b-acceptance-design.md:46, 01b-acceptance-design.md:255-262, 01-requirements.md:823-828 | AT-152's numeric oracle (bound = 240) is not pinned in the AT body — it inherits "the per-line bound decided at the R2 PDR". The C-42 order (cut after escaping, predicate on the emitted form) and the D4 arms ARE pinned. | State in AT-152: bound value 240 (per ruling), assert emitted-line length ≤ 240; leave only genuinely PDR-free details to the PDR. |
| QA-06 | MINOR | 01-requirements.md:464-469, 01-requirements.md:671-677, 01b-acceptance-design.md:283 | Two visible behaviours have unit-test coverage only, no black-box arm: lens neighbourhood dimming (LLR-RVM.2.3) and the sheet's counted overflow line (LLR-RVS.6.2). Gate (a) is per-story, so this is not a violation, but both are operator-visible outcomes. | Add one assertion each to AT-131/AT-132 (dimmed rows present in the frame) and AT-141/AT-143 (`… +NN more` line at a small-height arm), or record explicitly that Layer A owns them. |
| QA-07 | MINOR | contract (scope-wide) | No AT exercises a very large map (the "100k-node" class). The contract has no node-count scale requirement; the largest surface is the 303-node live skeleton (premise P2) and the budget-spent arms (AT-132, AT-138b) cover `VISIT_BUDGET` exhaustion, not render scale. | Out of contract scope as written; if scale matters, add an HLR + AT, else note the deliberate omission in §2.5 assumptions. |
| QA-08 | MINOR | 01-requirements.md:679-685 | LLR-RVS.7.1 (read-only evidence labels, `osopen` census) traces to HLR-RVS.2 (neighbour rows) although its substance is the read-only posture of HLR-RVH.2/RVS; the link is defensible but indirect. | Re-trace to HLR-RVH.2 (or accept and note). Cosmetic. |

## Evidence

### Per-story two-layer gate (a: black-box AT · b: observable deliverable + method · c: dual traceability · d: black-box purity)

| Story | (a) | (b) | (c) US→HLR→LLR→TC / US→AT | (d) |
|---|---|---|---|---|
| US-RMV-001 matrix+lens | Y — AT-130…134, `run_test()` pilots, real keys | Y — rendered strings, `export_text()`, zero-explained-clip audit sink | 1→RVM.1-4→10 LLR→TC-RM-04…09; AT-130…134 | Y — no internal symbol; AT-132/133/134 ride the fixture-injection seam (QA-02) |
| US-RMV-002 gaps | Y — AT-135…139 | Y — literal strings/chips/rows asserted on the frame | 1→RVG.1-3→9 LLR→TC-RM-10…14; AT-135…139 (AT-136 contingent — QA-04) | Y |
| US-RMV-003 sheet | Y — AT-140…144, real `c` press | Y — verbatim crumb/note lines, oracle-compared rows | 1→RVS.1-6→14 LLR→TC-RM-15…20; AT-140…144 | Y |
| US-RMV-004 shell | Y — AT-145…149, Home table + screen stack | Y — row/cell census, active-screen assertion, seat equality | 1→RVH.1-5→14 LLR→TC-RM-21…27; AT-145…149 | Y |
| US-RMV-005 text leaf | Y — AT-150 census + AT-151 `mapper --audit` subprocess | Y — census counts 1/1/1 + zero old-path hits; byte identity vs R1 goldens | 1→RVT.1→3 LLR→TC-RM-28/29; AT-150/151 | Y — AT-151 is the black-box arm; AT-150 is white-box by design (the story's observable IS code structure, C-31) |
| US-RMV-006 hook bound | Y — AT-152 subprocess of the real entry point | Y — line ≤ bound, D4 arms named (bound numeric: QA-05) | 1→RVU.1→1 LLR→TC-RM-30; AT-152 | Y |

### Traceability counts and orphans

- **US:** 6/6 → HLR forward complete (every HLR names `Traces to` one story). **HLR:** 20 in
  artifact (26 claimed — QA-01). **LLR:** 51, all with an `Asserting tests` field; every HLR
  has ≥1 LLR. **AT:** 23 (AT-130…152), all in the matrix with a US and pinned LLRs; no
  orphan AT. **TC:** 27 (TC-RM-04…30), index at 01b:294-299 matches the family split.
- Reverse: every LLR names asserting tests (14 carry "(planned)" names — V-5 provisional,
  accepted by §5.2 criterion 1 and Phase-3 minting). Every AT/TC traces back to a US/LLR.
- Cited precedents verified on disk: `run_test()` pilot idiom
  (`tests/test_colour_always_on.py:25-34`, `:64-70` — accurate); `pilot.press` used across
  58 test files; `home.py:209` single `*.mmd` glob (accurate); R1 files
  `test_relmap_gaps.py`, `test_relmap_isolation.py`, `test_keymap.py`, `test_scalecheck.py`
  exist; planned files (`test_relmap_matrix.py`, `test_relmap_gaps_view.py`,
  `test_relmap_sheet.py`, `test_relmap_shell.py`, `test_relmap_text.py`,
  `test_hook_line_bound.py`, `test_relmap_scalecheck.py`) do not yet — consistent with
  Phase-3 minting. PLAN roadmap test names match the LLR `Asserting tests` fields 1:1
  (viability OK, including `test_keymap.py` for LLR-RVH.4.1 and the sweep file for
  LLR-RVG.1.4).

### Negative controls (absence-of-failure arms)

- **Empty map:** AT-130 boundary (zero-node → `no node on record`), AT-135 empty-canon
  arm, AT-138a, AT-140 empty-`RelMap` arm, AT-147b empty canon. ✔
- **C-17 markup safety (mandated hostile-input AT):** exists and is black-box — AT-134
  (matrix, `export_text` + no raw ESC), AT-139 (gaps, composited frame + style-run
  census), AT-144 (sheet), plus host-side hostile arms AT-145b (`x[y].relmap.yml`) and
  AT-148 (hostile descriptor). All assert literal rendering + no style leak + no raise +
  app alive — absence of failure, not just presence. ✔
- **87-col width:** AT-130/131/137/143/148 arms with the audit-clean sweep. ✔
- **Budget/scale edge:** AT-132 and AT-138b (`not computed`, honest `000`). ✔ (large-N: QA-07)
- **Refused descriptor:** AT-147a, AT-148 hostile arm, AT-151 byte-identity over a refused
  descriptor. ✔

### The two "assumed — verify in Phase 2" seams — verdicts

1. **AT-driver host push / fixture injection** — `01b-acceptance-design.md:13-16`,
   `01-requirements.md:269` (F-5), `01-requirements.md:964-967`: **STILL DEFERRED** (QA-02).
   Not resolved by the artifacts; discharge is planned (PDR freezes the host↔renderer
   surface; trunk Inc-2 lands the host) but unproven. P2 flags it; the PDR must close it.
2. **Workspace-as-repo** — `01-requirements.md:739`, PLAN.md:124: **STILL DEFERRED** (QA-03).
   Orchestrator-accepted (OQ-R2 shell #2) but the derivation-over-a-bare-directory premise
   is unprobed. P2 flags it; close at the PDR with the AT-147 fixture shape.

(A third `assumed` flag exists at `01-requirements.md:779` — KEY_SCOPE sufficiency for
help/palette, and `:715` — `RelMapScreen` path per ARQ commitment; both are of the same
"verify at PDR" class and should be closed in the same pass.)

### Viability notes

PLAN §Roadmap provisional test names ↔ LLR `Asserting tests` fields: full match (see
counts above). Orchestrator rulings vs contract text: by-kind toggle and hook bound (240,
post-escape cut) rulings predate the swarm merge but the contract text still presents both
as open PDR questions — fold before the PDR so the PDR debates only what is genuinely open
(QA-04).
