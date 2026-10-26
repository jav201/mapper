# PDR evidence — ux-reviewer — batch 2026-10-25-relmap-r2-batch

## Scope reviewed

Interaction design of `.dev-flow/2026-10-25-relmap-r2-batch/design/design-proposal.md` (336 lines)
against the operator verdict of prototype round 2026-10-23 (`verdict-2026-10-24.json`, `PROTOTYPE.md`
and the captured PNGs at 118×34 and 87×34), the contract (`01-requirements.md` §3/§4) and the
acceptance design (`01b-acceptance-design.md` AT-130…AT-152). Lens per the ux-reviewer role: context
of use, observable UX criteria, real-mechanism walkthrough rules, error/empty/slow states, and the
three evaluation acts declared separately below. Trigger D1 fired (whole screen + Home entries are the
user-visible surface); the screen does not exist yet — this is a design review, not a walkthrough.

## Evaluation acts declared (automated walkthrough / expert inspection / with users)

| Act | State | Method / reason |
|---|---|---|
| Automated walkthrough through the real mechanism | **not performed — no shipped surface exists** (`mapper/screens/relmap/` is unbuilt; PDR precedes Phase 3). The walkthrough is owed at Phase 4 against the shipped screen per the validation template. | n/a at this gate |
| Expert inspection against declared criteria | **performed** — cognitive-walkthrough-style review of the proposal against the contract's observable criteria and AT assertion lists, grounded in the operator verdict JSON, `PROTOTYPE.md`, and five prototype captures read as images (`matrix-panel` 118 and 87, `gaps-ranked` 118, `gaps-by-kind` 118, `sheet-direct` 87), plus source reads of `mapper/keymap.py`, `mapper/darkside.py`, `mapper/screens/help.py:223`, `mapper/screens/palette.py`, `mapper/screens/draft_guard.py:54-67`. | this file |
| Evaluation with users | **not performed — this team is one person and no user of this surface exists outside it.** The closest act that did happen is the 2026-10-23 operator prototype round: the operator picked the four view layouts on captured screens (`verdict-2026-10-24.json`); that verdict is the fidelity oracle of this review, not a substitute for user evaluation of the shipped screen. | verdict JSON / PROTOTYPE.md |

## Record §A rows in my lens (row # | ✓/⚠/✗ | Evidence)

| # | | Evidence (UX lens only — rows 1–8, 10 carry other reviewers' primary judgments) |
|---|---|---|
| 1 | ✓ | Proposal §1–§6 complete; rejected alternatives honest (three `n/a` rows name the ruling that already decided them). |
| 2 | ✓ | Read-only posture is interaction-relevant and held: no write vocabulary in the seat (AT-146 BINDINGS census, M-RVH-5), `osopen` banned on the sheet (LLR-RVS.7.1). |
| 3 | ✓ | §7 names a consumer for every output; no empty consumer cells. |
| 4 | ✓ | 23 ATs cover the happy paths and the empty/error states (see Findings); per-view verdict citations trace to the contract :147-173. |
| 5 | ⚠ | ATs are observable and non-vacuous, but two assertion sets under-pin the interaction they guard: AT-136 (by-kind membership, F-UX-2) and AT-149 (chord subset, F-UX-6 notice). QA owns this row; my lens adds the two gaps. |
| 6 | ✓ | The two executed seam probes (AT-driver, workspace-as-repo) de-risk the AT drivers that every UX assertion rides on. |
| 7 | ✓ | Frozen set D1–D5 declared exactly; D3 freezing the seat (with BINDINGS/keybar/help/palette derived) is what makes discoverability enforceable. |
| 8 | ✓ | Lane file sets disjoint; UX-relevant seams (help/palette 6b, seat in trunk Inc-2) are correctly trunk-owned so equality cannot drift per lane. |
| 9 | ✓ | **My row.** Interaction design reviewed: verdict fidelity (table below), seat conformance, 87-column usability, casing, empty/error/slow states. Approved with 3 minor conditions — the design is usable at both widths, honest in every declared state, and every UX claim is an executable criterion. |
| 10 | n/a | Security lens — owned by the security-reviewer (C6/C8). The hostile-payload arms (AT-134/139/144/148) are also the UX trust arms; noted as adequate in my lens. |

## Verdict-fidelity cross-check

| View | Verdict picked (verdict json / PROTOTYPE.md) | Proposal binds | Drift? |
|---|---|---|---|
| Matrix + lens | `matrix-panel` (`d_matriz_lente`; band rejected — hop 2 lands on ATs, not columns; PROTOTYPE.md:30-39) | proposal:46 + contract :147-148; the 87-col capture shows the lens panel beside a clean grid | none |
| Matrix cell | `binds-glyphs` (`d_matriz_celda`; letters rejected — initial collisions read as alphabet soup) | proposal:47 + contract :149-150, glyph table frozen D5 (●/◐/○ · `·`) | none |
| Gaps | `gaps-ranked` (`d_gaps`; microbar rejected — duplicates the count at 8 cells of resolution) in Darkside casing, NOT Solari ALL-CAPS (PROTOTYPE.md:175-176 note) | proposal:49-51 + contract :156-162, HLR-RVG.2 with M-RVG-8/9 census mutants | none |
| Sheet | `sheet-direct` (`d_ficha`; columns rejected — halve the WHAT column) with `c` = full chain in stacked density (PROTOTYPE.md:60-65 recommendation) | proposal:52-53 + contract :165-173; `k` by-kind SHIPPED per LED-2026-10-25-r2.01 | none |

The captures I read confirm the bindings: `matrix-panel.png` (118 and 87) shows the separate right
lens panel (`what feeds it ←`, `a change reaches →`, `change LLR-REPAIR.2 → 6 nodes`, WARN reach
gauge), the window declaration `01–05 / 5`, and the bottom bar `view 1 matrix 2 gaps 3 sheet · lens
enter impact on node · app ? all keys · q quit`. `gaps-ranked.png` shows the count column and the
severity chips (and the ALL-CAPS gap sentences the casing HLR exists to kill). `gaps-by-kind.png`
shows the per-kind bands with ×N and worst severity. `sheet-direct.png` (87) shows the declared cut
`╌╌ +01 MORE UPSTREAM AT HOP 2 — c shows the chain` and Darkside-cased section headers. The proposal
binds every one of these.

## Findings

### F-UX-1 — View-specific chords are seat-static; their behaviour outside their home view is unspecified [MINOR]
- **What.** The D3 seat binds `enter` (lens focus — a matrix-view concern owned by `matrix.py`), `c`
  (chain toggle — sheet), `k` (by-kind — gaps) as scope-static rows, so the keybar, help and palette
  advertise them on all three views. The proposal never says what pressing `c` on the matrix or
  `enter` on the sheet does.
- **Where.** `design-proposal.md:82,185` (the seat); prototype bottom bar (static across all views —
  operator-approved precedent); `mapper/screens/help.py:212-217` (help's own mission statement: a key
  that does nothing here is the discoverability bug US-N03 exists to remove).
- **Why it matters.** A silent no-op key is exactly the failure mode the seat/help equality machinery
  was built to prevent; three lanes will each improvise an answer at the host's `action_*` dispatch.
- **Recommendation.** Pin one declared behaviour in the proposal/contract: view-specific chords are
  inert (no-op) outside their home view — matching the operator-approved static prototype bar — or
  the host flashes the crumb note. Any richer answer is a seat change and is trunk-owned anyway.
- **Criterion state:** planned (LLR-RVH.4.1/.4.2 arms; AT-148/AT-149 execute at Inc-2/Inc-6).
- **PDR condition:** COND-UX-1 · minor · declare the out-of-view behaviour of `enter`/`c`/`k` in the
  design narrative · owner: trunk Inc-2.

### F-UX-2 — The by-kind band/row misalignment the LLR flagged for the PDR is never answered [MINOR]
- **What.** LLR-RVG.1.5's draft-time verification records: "The prototype's by-kind PNG shows a
  possible first-band/row misalignment — the LLR pins each band over exactly its own rows; flagged
  for the PDR to confirm." The proposal does not confirm it. AT-136 asserts band order, ×N, severity,
  unchanged total rows and byte-identical toggle-back — but not per-band membership. A row painted
  under the wrong band head with correct counts and totals would pass every asserted arm.
- **Where.** `01-requirements.md` (LLR-RVG.1.5 draft-time verification); `01b-acceptance-design.md:102-110` (AT-136); `design-proposal.md:106,213` (Inc-4 exit checks name only M-RVG-7).
- **Why it matters.** Misalignment is a wrong-data-shown defect on the triage view the operator reads
  to prioritise the record; the round itself flagged it, so the PDR answering it is owed.
- **Recommendation.** Add one arm to AT-136 (or a TC-RM-11…14 unit): per-band membership equals the
  oracle grouping of `rank_gaps` output (each band's member node ids), not just its count.
- **Criterion state:** planned (AT-136 at Inc-4).
- **PDR condition:** COND-UX-2 · minor · add a per-band membership oracle arm to AT-136 so the
  flagged misalignment cannot ship · owner: Inc-4 (gaps lane).

### F-UX-3 — Stale citation `mapper/screens/palette.py:432` [MINOR]
- **What.** LLR-RVH.4.4's draft-time verification and proposal §5.2 cite `mapper/screens/palette.py:36,432`.
  Line 36 verifies (the palette's own BINDINGS derive from the seat); line 432 does not exist — the
  file is 218 lines in both trees. The intended target is `mapper/keymap.py:432` (`palette_items`),
  verified, which is also the function that makes "palette offers the relmap actions" true.
- **Where.** `01-requirements.md` (LLR-RVH.4.4); `design-proposal.md:238`; verified against
  `mapper/screens/palette.py:34-37,141` and `mapper/keymap.py:432`.
- **Why it matters.** A citation that resolves to nothing is an asserted-not-satisfied row under the
  record's own notice convention; cheap to fix at seal while the contract is being amended.
- **Recommendation.** Re-point to `mapper/keymap.py:432` (keep `screens/palette.py:36`).
- **Criterion state:** executed for the verification itself (this read); the fix is documentation.
- **PDR condition:** COND-UX-3 · minor · fix the palette citation at seal · owner: trunk (contract
  amendment at seal).

### F-UX-4 — The 87-column lens-summary cut is pinned only in an AT boundary arm, not in the design narrative [⚠ notice, not blocking]
- The proposal's §3 *declared cuts* paragraph names the gaps window, the WHAT 12-cell drop, the sheet
  hop-2 cut and the counted overflow — but not the matrix lens summary, which the 87-col capture shows
  truncating (`change … → 6 …`, `hop 2:…`). AT-131's boundary arm pins "the summary line is cut inside
  the panel with zero unexplained audit events", so honesty is enforced at test time; the design story
  the lanes read should say it in words too, so three lanes share one rule.

### F-UX-5 — Slow state during derivation [⚠ notice — declared out of scope, accepted]
- Open/`r` re-derivation costs ~1 s on the real canon and up to a 10× recorded budget at cap scale,
  with no busy/deriving criterion. The proposal declares "the open absorbs" it
  (`design-proposal.md:301`) and the cap-scale budget is recorded at Phase 3. Per my role's rule 5 I
  accept this as the written out-of-scope declaration for the ~1 s real case; the Phase 4 walkthrough
  should re-check perceived latency on the real canon before the DDR calls it done.

### F-UX-6 — AT-149's asserted chord list omits `k` and `escape` [⚠ notice, not blocking]
- AT-149 asserts help lists the seat labels for `1`/`2`/`3`/`enter`/`c`/`r`/`q`. The M-RVH-12
  equality negative arm covers the general case, but `k` is this batch's newest operator-facing toggle
  and is worth naming in the equality assertion so a dropped `k` row reddens AT-149 directly.

## What I verified and found sound (no finding needed)

- **Seat conventions** (`mapper/keymap.py`): the nine chord families are unique inside the scope
  (rule :9-12); the `q`-leave + `escape`-alias pair copies the house leave precedent (:230-231, review
  :314-315, roles :303-304); cursor-key navigation copies the review scope (:309-310) rather than the
  tree's `hjkl`; digits are an accepted chord class (review `4` :311, factory `0` :278) and
  `1`/`2`/`3` direct view switch is exactly what the operator-approved prototype bar shows; the
  additive `SCOPE_REVIEW` precedent (:41) supports the additive seat; mnemonics (`c` chain, `k` kind,
  `r` refresh) are true in every state, keeping the seat static and the whole-seat pin unmoved.
  Cross-scope chord reuse (`k`, `q`, `r`, `c`) is the documented norm (:22-25), not a conflict.
- **Derivation surfaces:** `help.py:223` and `palette.py:34-37` both generate from the seat, and the
  app reads the screen's `KEY_SCOPE` (LLR-RVH.4.4 draft-time note) — help/palette/BINDINGS/keybar
  cannot drift from the seat by construction; M-RVH-9/10/12 + TC-RM-25 + AT-149 make any drift red.
- **Casing:** HLR-RVG.2 is enforced twice — an AST census over the renderer source with a set derived
  from the shipped catalogue (C-31) and rendered-string assertions on the real screen (AT-135/137/142:
  `hlr without llr`, `high/med/low` chips); M-RVG-8 (restore `.upper()` / hard-coded caps literal) and
  M-RVG-9 (one caps chrome string) are named reddening mutants. This holds the casing.
- **Empty/error states are observable criteria, not hand-waves:** refusal path (fixed `refusal_line`,
  closed cause set K1–K17, app alive — AT-147 boundary, AT-148 hostile arm); zero-descriptor derived
  Home row (AT-147); declared-empty sheet sections (AT-140, `╌╌ none on record`); honest skeleton
  (`no test columns yet` declaration verbatim in AT-130, `000` reach in AT-135/138, `not computed`
  in WARN never a fabricated number in AT-132/138 with M-RVM-7/M-RVG-10/11); empty/unknown selection
  (LLR-RVM.3.2: `no node on record`, `╌╌╌ relates to nothing`, M-RVM-9); empty gaps (`no gaps on
  record`, AT-135/136 boundary).
- **87-column usability:** the declared cuts keep the operator whole at 87 — matrix keeps grid +
  windowed rows + lens panel (capture confirms), gaps keeps `no`/`gap`/`node`/`reach`/`status` and
  drops WHAT whole below its 12-cell minimum instead of mangling it, sheet keeps both sections with
  `fit` ellipsis and the counted overflow line. AT-131/137/143 pin all three at 87×34 with the C10
  audit sink as the zero-silent-truncation guard. Every truncation is declared in words or pinned by
  an asserted ellipsis; none is silent.

## Verdict

`approved with conditions` — COND-UX-1 (minor, trunk Inc-2) · COND-UX-2 (minor, Inc-4) · COND-UX-3
(minor, trunk at seal). No blockers; all three are wording/arms-level fixes, none re-opens a frozen
decision or a layout pick.
