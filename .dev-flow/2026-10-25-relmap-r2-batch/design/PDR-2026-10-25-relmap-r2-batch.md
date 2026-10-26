# Design review record — PDR — mapper — Batch 2026-10-25-relmap-r2-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.

> **Owed in.** `core` by trigger · `full` ✓ (trigger A1 fired).

> **Where this lives.** Repo copy under `.dev-flow/<batch>/design/`, as the R1 batch did. It is
> **sealed** and **cited by id**; if it changes after the seal it is a NEW version with a NEW id,
> never a silent edit.

> **Notice convention.** `⚠` yellow = notice, declare the reason and continue · `✗` red = block ·
> `✓` green = satisfied **with its evidence cited**. Without a citation an item is asserted, not
> satisfied. **This record was drafted as a SEED at the PDR gate and sealed 2026-10-25 after the
> four independent reviews** (architect · QA · security — C6/C8 · UX — D1 fired); every §A row
> below was marked `at seal` in the seed and is filled here with the reviewers' marks and evidence.

| Field | Value |
|---|---|
| Record id | `PDR-2026-10-25-relmap-r2-batch` |
| Reviews | `design/design-proposal.md` (`PDR-2026-10-25-relmap-r2-batch`, drafted 2026-10-25 after the P2 first pass and the P1 amendment; revised at the PDR gate for the reviewers' conditions) · `evidence/pdr-architect.md` · `evidence/pdr-qa-reviewer.md` · `evidence/pdr-security-reviewer.md` · `evidence/pdr-ux-reviewer.md` (all 2026-10-25) |
| Participants | PDR: `architect` — Kimi K2.8 subagent executing agents/architect.md · approved with conditions · `qa-reviewer` — Kimi K2.8 subagent executing agents/qa-reviewer.md · approved with conditions · `security-reviewer` (C6/C8) — Kimi K2.8 subagent executing agents/security-reviewer.md · approved with conditions · `ux-reviewer` (D1 — owed) — Kimi K2.8 subagent executing agents/ux-reviewer.md · approved with conditions — reviews run and sealed 2026-10-25 |
| Date sealed | `2026-10-25` |
| **Verdict** | `approved with conditions` |

---

## A · PDR checklist — preliminary design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` | ✓ | proposal §1–§6; six rejected alternatives where a real decision exists and three honest `n/a` rows naming the deciding authority (:296-305); `evidence/pdr-architect.md` §A row 1 · `pdr-qa-reviewer.md` row 1 · `pdr-ux-reviewer.md` row 1 · `pdr-security-reviewer.md` row 1 |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ | proposal §2 against the `screens/relmap` rows (`docs/ARCHITECTURE.md:165,197`), the `relmap` row's `text` leaf (`:158`), the new edges (`:194-197`) and R-016/R-018/R-019 (`:319-322`) — every cited row verified real by the architect's own census; no boundary moves, divergences "none new" consistent (`evidence/pdr-architect.md` §A row 2 + §Census re-derivation) |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ | proposal §7 six rows, none empty (:309-316); `evidence/pdr-architect.md` §A row 3 · `pdr-qa-reviewer.md` row 3 · `pdr-security-reviewer.md` row 3 |
| 4 | Every requirement has foreseen coverage | ⚠ | §1 chain map + §5.1 LLR rows (52 LLRs across the six families; 20 HLRs; AT-130…AT-152 per `01b-acceptance-design.md:293-319`; TC-RM-04…30); spot-check found no orphan LLR (`evidence/pdr-qa-reviewer.md` row 4) — ⚠ the hostile coverage for the four markup sinks names no LF/TAB payload anywhere in the batch dir (grep: zero hits), so the sink gap F-SEC-1 would redden nothing (`evidence/pdr-security-reviewer.md` rows 4–5 → COND-SEC-1) |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ⚠ | §5.1 names a RED counterfactual per new source file and an M-* mutant per LLR (M-RVM-1…11, M-RVG-1…13, M-RVS-1…12, M-RVH-1…17, M-RVT-1…3, M-RVU-1…3); mutant spot-check over 14 LLRs (one+ per family): every mutant killable, one only partially — M-RVS-9's live one-hop arm is vacuous on the skeleton, the TC-RM-17 synthetic 3-level fixture arm is the required kill (F-QA-5 → COND-QA-5); UX adds two assertion gaps, AT-136 membership (F-UX-2 → COND-UX-2) and AT-149's chord list (notice F-UX-6) (`evidence/pdr-qa-reviewer.md` §Mutant spot-check · `pdr-ux-reviewer.md` row 5) |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ | proposal §2.1 (exit checks, lane fixture policy ARC-05 :115-118, guard set C-1), §3 *Resource* and §6; both seam probes executed 2026-10-25 — the qa-reviewer RE-RAN the AT-driver probe: PASS, output byte-identical to the recorded transcript (`evidence/p2-seam-at-driver.md`; `evidence/pdr-qa-reviewer.md` §Seam probe re-run); guard set + `tests/test_no_operator_paths.py` run green (196 passed 3 xfailed; 2 passed) |
| 7 | Interfaces **frozen** for the fork are listed | ⚠ | D1–D5 listed and the "frozen set is exactly" closing sentence present (:191-197) — ⚠ D1 omits the channel for renderer-owned toggle state the contract's own LLR-RVS.3.3/RVG.1.5 require (F-ARCH-1 → COND-ARCH-1); the D2/Inc-1 set omits `mapper/relmap/adapter.py:29`, a live fourth consumer of the old paths (F-ARCH-2 / F-QA-1 → COND-ARCH-2 / COND-QA-1); the frozen four-sink seam names bare `darkside.plain`, which probe-verifiably preserves LF/TAB (F-SEC-1 → COND-SEC-1) |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ⚠ | lane intersections empty (`docs/ARCHITECTURE.md:352-356` verified), SOURCE counts 4/4/1/1/1/2/2/1 as declared, §5.2 census names `tests/test_inc9c.py` (the `LEAK_EXCEPTIONS` pin, re-pinned in the same Inc-6), `tests/test_fold.py`, `tests/test_repair_artifact_claims.py`, the keymap pins — ⚠ the Inc-1 count of 4 contradicts the contract's four-module re-point statement once `adapter.py` is counted (F-ARCH-2/F-QA-1); `tests/test_keymap.py` is labeled "(new)" but exists (R1 US-N03), and `tests/test_key_dispatch.py` is missing from Inc-2's targeted run (F-QA-2 → COND-QA-2); three census citations the lanes read at entry are wrong (F-ARCH-3 → COND-ARCH-3; F-UX-3 → COND-UX-3); fork preconditions F-1…F-5 quoted verbatim from `01-requirements.md:270-274` and each mechanically checkable (`evidence/pdr-architect.md` §A row 8 + §Census re-derivation · `pdr-qa-reviewer.md` row 8) |
| 9 | UX lens applied (D1 fired): interaction design reviewed | ✓ | `ux-reviewer`: verdict fidelity with zero drift — matrix-panel + binds-glyphs, gaps-ranked + `k` by-kind (SHIPPED LED-2026-10-25-r2.01), sheet-direct + `c`, all in Darkside casing — cross-checked against `verdict-2026-10-24.json`, PROTOTYPE.md and five prototype PNGs (118+87); the D3 seat conforms to the keymap house conventions (chord uniqueness, `q`/`escape` leave precedent, seat-derived BINDINGS/keybar/help/palette); usable at 118 and 87 (declared cuts, nothing silent); every empty/unavailable state is an observable criterion — approved with 3 minor conditions (`evidence/pdr-ux-reviewer.md` §A row 9, §Verdict-fidelity cross-check, §Evaluation acts) |
| 10 | Security lens applied (C6/C8 fired) | ⚠ | `security-reviewer`: the escaping helper probe-executed — `plain` neutralises ESC/bidi/BEL but preserves LF/TAB, so the frozen seam must be the `_row_text`/`fit` wording (F-SEC-1 → COND-SEC-1); cut-after-escape verified hazard-free against the R1 D4 prefix rewrite (`mapper/reqharness/audit.py:429-436`); the canvas sink is structurally markup-immune (one char per cell, explicit styles); read-only path clean — no write vocabulary in the seat, host reach bans writes/`osopen`, refusal path renders fixed text from the closed K1–K17 set (`01-requirements.md:1049-1072`), no secrets/PII/outbound/destructive surface; cap-scale valve adequate with one budget gap (F-SEC-2 → COND-SEC-2); all four hostile AT arms concrete and observable, none crash-only — approved with conditions (`evidence/pdr-security-reviewer.md` §A row 10, §Escaping-helper probe, §Read-only path) |

**No increment starts without an approved PDR** — for this batch, concretely: no lane starts before
this record is sealed with the host↔renderer surface frozen (fork precondition F-2,
`01-requirements.md:271`). The seal is conditional: the freeze binds **as amended by the §B
conditions**, and the text amendments owned `trunk at seal` (COND-ARCH-1, COND-ARCH-3,
COND-SEC-1 wording, COND-UX-3, and the plan side of COND-ARCH-2/COND-QA-1) are the author's first
act on the proposal/contract/`docs/ARCHITECTURE.md` before trunk Inc-1 consumes the frozen set —
the §B table is the authority on what binds.

---

## Findings at the PDR gate

All findings carry their full evidence in `evidence/pdr-<role>.md`; severities are the reviewers'.
None is a BLOCKER; none re-cuts a lane or moves a boundary — every MAJOR is a text/wording-level
amendment discharged at the seal or trunk Inc-1.

| Finding | Severity | One line | Condition |
|---|---|---|---|
| F-ARCH-1 | MAJOR | D1 freezes one-way state + one paint entry only; the contract's LLR-RVS.3.3 (`01-requirements.md:652-661`) and LLR-RVG.1.5 (:548-556) assign `c` density / `k` by-kind state to the renderers while the seat puts the actions on the host — the surface needs one named toggle-state channel or L2/L3 each improvise (F-3) | COND-ARCH-1 |
| F-ARCH-2 | MAJOR | Inc-1's file set and census omit `mapper/relmap/adapter.py:29`, the fourth live consumer of the D2 old paths — as planned, Inc-1 either ImportErrors at exit or ships the two-import-path drift R1 DDR §E 10-11 rejected | COND-ARCH-2 |
| F-ARCH-3 | MINOR | three census citations the lanes read at entry are wrong: `palette.py:432` is phantom (file is 218 lines; block is :35-38), keymap "uniqueness :9-12" is really :25+:445, `test_key_dispatch.py:137` is the data table (pin assertion is :170) | COND-ARCH-3 |
| F-QA-1 | MAJOR | plan-vs-contract inconsistency on the Inc-1 re-point set / SOURCE count (the same defect as F-ARCH-2, found independently: the contract names four importing modules, the plan three) — the Inc-1 gate cannot pass its own zero-old-path census as written | COND-QA-1 |
| F-QA-2 | MINOR | `tests/test_keymap.py` exists (R1 US-N03 universal, quantifies over the seat at import) — "(new)" mislabel; `tests/test_key_dispatch.py` missing from Inc-2's targeted run | COND-QA-2 |
| F-QA-3 | MINOR | AT-137's 10× open/`r` wall-clock budget must stay a recorded packet measurement, never a committed wall-clock assert (the project's own FLAKE-2 class, `tests/test_help_scope.py:43-51`) | COND-QA-3 |
| F-QA-4 | MINOR | AT-147/AT-148 derivation instrumentation must wrap, not replace, `derive_reqharness_map` (C-16) or the Layer B arm stops exercising the real mechanism | COND-QA-4 |
| F-QA-5 | MINOR | M-RVS-9 is only half-killed by its live one-hop arm (stacked rows == direct rows on the skeleton); the TC-RM-17 synthetic 3-level fixture arm is the required kill | COND-QA-5 |
| F-QA-6 | MINOR — note only | AT-150 is a source census, not an operator-observable behavior — acceptable (its deliverable IS the on-disk artifact, C-18, surface honestly declared); recorded so the DDR does not re-litigate | — |
| F-SEC-1 | MAJOR | the one named seam for all four sinks — bare `darkside.plain` — probe-verifiably preserves LF/TAB (`plain("a\nb")` → `'a\nb'`, `darkside.py:498,550-561`), and no hostile arm/mutant/P12 vocabulary carries those bytes, so the gap would redden nothing; the freeze would institutionalise the short version | COND-SEC-1 |
| F-SEC-2 | MINOR | the `c` stacked chain is unbounded in depth (full BFS, O(V+E) ≤ ~200k ops at the shipped caps) and the only recorded budget is the derivation 10× — rendering's one unbounded computation has no number to assert against | COND-SEC-2 |
| F-SEC-3 | MINOR | pin the hook-bound pipeline order verbatim (escape → 239+ellipsis spelling-aware cut → `verdict: ` rewrite check → print) in the Inc-7 spec — AT-152 already pins it in test | — (folds into the Inc-7 packet) |
| F-UX-1 | MINOR | the seat binds `enter`/`c`/`k` scope-static but the proposal never says what they do outside their home view — three lanes would each improvise; pin inert (or crumb-note) to match the operator-approved static bar | COND-UX-1 |
| F-UX-2 | MINOR | LLR-RVG.1.5's flagged by-kind first-band/row misalignment is never answered — AT-136 asserts counts/order/toggle-back but not per-band membership, so a wrong-band row passes every asserted arm | COND-UX-2 |
| F-UX-3 | MINOR | stale citation `mapper/screens/palette.py:432` (file is 218 lines in both trees); the verified target is `mapper/keymap.py:432` (`palette_items`) — keep `screens/palette.py:36` | COND-UX-3 |
| F-UX-4…6 | ⚠ notices | lens-summary 87-cut pinned only in an AT arm, not §3 (lanes should share the rule in words); ~1 s derivation slow-state declared out of scope, accepted with a Phase-4 re-check; AT-149's asserted chord list omits `k`/`escape` (M-RVH-12 covers the general case) | — |

---

## B · DDR checklist — detailed design review · **and the JOIN point when the batch forked**

Forked (A4 fired): the rows below are filled at the DDR, after the join — every lane's ATs run on the
joined tree first (F-5).

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, **and why** | | filled at the DDR |
| 2 | Frozen interfaces still intact — or the work returned to the trunk and it is declared | | filled at the DDR (D1–D5 re-read against the sealed surface **as amended by the conditions below**) |
| 3 | **Reverse census CROSSED between lanes** (the one check impossible from inside a lane) | | proposal §5.2 re-run crossed at the join; F-4 per-lane censuses attached to each lane packet |
| 4 | Every `AT-NNN` realises in **exactly one** on-disk node (C-18) | | filled at the DDR |
| 5 | Test ledger **summed** across lanes, reconciled | | filled at the DDR |
| 6 | No lane touched another lane's file | | filled at the DDR (the §8 file-set disjointness is the plan; the DDR proves it) |
| 7 | Source-file budget: any lane that reached or exceeded 4, reviewed here | | filled at the DDR (planned maximum is 4, on trunk Inc-1 and Inc-2 only; Inc-1 becomes **5** per COND-ARCH-2/COND-QA-1, justified there — SUPERSEDED at P3 2026-10-25 by the orchestrator ruling: Inc-1a (4) + Inc-1b (1), each ≤ 4 — the DDR reviews the split instead) |
| 8 | **Every open PDR condition discharged one by one, by RE-READING the artifact** | | the table below, filled at the seal with the reviewers' conditions; the DDR re-reads all of them |

**Conditions left open at the seal.** Each condition below lands in the contract, the proposal or
`docs/ARCHITECTURE.md` — the **author's** amendment, not the reviewers' (the four reviews changed no
artifact). Where a condition also amends this record's own freeze text (§D), the record side is
**discharged at this seal** and the `Discharged?` cell says so; the rest of the amendment stays open
until its named gate re-reads it. Nothing in this batch is `executed` by the seal: every test is
`planned` until its increment.

| # | Condition left open at PDR | Discharged? | The artifact line that proves it |
|---|---|---|---|
| COND-ARCH-1 (MAJOR) | D1 must name the host↔renderer channel for renderer-owned toggle state (`c` density per LLR-RVS.3.3, `k` by-kind per LLR-RVG.1.5) — one shared mechanism for all three lanes (paint-entry view-state argument, or a frozen renderer state-query/toggle entry the host's `action_*` calls) | **record side discharged at this seal** — §D D1 below carries the amended text — **and DISCHARGED at P3 2026-10-25 by commit `75f9e28`**: the proposal §4 D1 row + `docs/ARCHITECTURE.md:266` amendment landed, naming the channel — a frozen renderer state-query/toggle entry `toggle(kind: str) -> str` per renderer (the renderer owns the state), called by the host's `action_*`; re-read at trunk Inc-2 before any lane forks (F-2) | this record §D D1; proposal §4 D1 row; `docs/ARCHITECTURE.md:266`; `evidence/pdr-architect.md` F-ARCH-1; contract `01-requirements.md:548-556,652-661` |
| COND-ARCH-2 (MAJOR) | Inc-1 must own the `mapper/relmap/adapter.py` re-point — SOURCE becomes **5** (text.py + 4 re-points) with a one-line justification — or the D2 freeze text explicitly permits intra-package re-export; the §2.1/§5.1/§5.2/§8 sets and the Inc-1 exit-check census name `adapter.py` either way | **record side discharged at this seal** — §D D2/D6 below name `adapter.py` and the count 5 — **and DISCHARGED at P3 2026-10-25 by commit `75f9e28` under the orchestrator ruling at the seal (state.json decisions_log, station PDR, 2026-10-25; ruling commit `78ee993`)**: the "SOURCE becomes 5" mechanism is SUPERSEDED — Inc-1 splits into Inc-1a (text.py + the `model`/`descriptor`/`audit` re-points, 4 SOURCE) and Inc-1b (the `adapter.py` re-point, 1 SOURCE), both trunk before Inc-2, each step byte-identical; the proposal §2.1/§4/§5.1/§5.2/§8 amendment + the PLAN/worksheet side landed; the re-points themselves land at trunk Inc-1a/1b (the increment gate re-reads this condition; one discharge closes COND-QA-1 too) | this record §D D2/D6; `evidence/pdr-architect.md` F-ARCH-2 (`adapter.py:29` grep-verified); contract `01-requirements.md:832,840`; ledger `LED-2026-10-25-r2.16` |
| COND-ARCH-3 (MINOR) | repair the three census citations: `mapper/screens/palette.py:432` → the seat-derived block `:35-38`; keymap "uniqueness rule :9-12" → `:25` + `duplicate_chords()` `:445`; `tests/test_key_dispatch.py:137` → the whole-seat pin assertion `:170` | **DISCHARGED at P3 2026-10-25 by commit `75f9e28`** — landed in proposal §5.2 (+ §6 risk 3, which carried the same stale `:137`) + the contract draft-time fields (LLR-RVH.4.1/.4.4, premise P6); every repaired citation re-verified against the files on disk (one pass also closes COND-UX-3); ledger `LED-2026-10-25-r2.17` | `evidence/pdr-architect.md` F-ARCH-3; ledger `LED-2026-10-25-r2.17` |
| COND-QA-1 (MAJOR) | name `adapter.py` in the `text.py` re-point set and re-declare Inc-1's SOURCE count (5) with justification — the plan side of COND-ARCH-2, from the QA lens (plan-vs-contract inconsistency) | **record side discharged at this seal** (with COND-ARCH-2) — §D D2/D6 below — **and DISCHARGED at P3 2026-10-25 by commit `75f9e28` under the same orchestrator ruling as COND-ARCH-2**: the plan/contract amendment landed with the Inc-1a + Inc-1b split (the "count 5" declaration superseded by 4 + 1, each ≤ 4 — `LED-2026-10-25-r2.16`); a single discharge re-read closes both | this record §D D2/D6; `evidence/pdr-qa-reviewer.md` F-QA-1; ledger `LED-2026-10-25-r2.16` |
| COND-QA-2 (MINOR) | correct `tests/test_keymap.py` "(new)" → existing R1 file extended (US-N03 universal); add `tests/test_key_dispatch.py` to Inc-2's targeted run / exit checks | **DISCHARGED at P3 2026-10-25 by commit `75f9e28`** — landed in proposal §2.1 Inc-2 row + PLAN Inc-2 row (EXISTING relabelled, `test_key_dispatch.py` added to the run and the exit checks); re-read at the trunk Inc-2 gate | `evidence/pdr-qa-reviewer.md` F-QA-2 |
| COND-QA-3 (MINOR) | AT-137's 10× open/`r` budget is a recorded packet measurement, never a wall-clock assert in a committed test (deterministic arms only: windowing census, counted overflow, audit emptiness) | open — lands in `01b-acceptance-design.md` AT-137 + the Inc-4 packet; re-read at the L2 (Inc-4) gate | `evidence/pdr-qa-reviewer.md` F-QA-3 |
| COND-QA-4 (MINOR) | AT-147/AT-148 derivation observation (args, derive count) must WRAP, not replace, `derive_reqharness_map` (C-16) — Layer A unit arms stay unrestricted | open — lands in the Inc-2/Inc-6 packet specs; re-read at the trunk Inc-2 and shell Inc-6 gates | `evidence/pdr-qa-reviewer.md` F-QA-4 |
| COND-QA-5 (MINOR) | the M-RVS-9 kill at the Inc-5 gate is the TC-RM-17 synthetic 3-level fixture arm (row-set half), not the vacuous live one-hop "rows unchanged" assertion (note/crumb half only) | open — lands in the Inc-5 gate text + proposal §5.1 RVS.3.3 row; re-read at the L3 (Inc-5) gate | `evidence/pdr-qa-reviewer.md` F-QA-5 |
| COND-SEC-1 (MAJOR) | reword the frozen four-sink seam from bare `darkside.plain` to `_row_text`/`fit` (plain + LF/TAB/CR→space, `darkside.py:579-621`) in proposal §2 `base.py` row + §6 risk 2 + `01-requirements.md:827`; add LF+TAB to the P12 hostile vocabulary (`01-requirements.md:261`) and to the AT-134/AT-148 hostile arms with a "payload renders on ONE row" assertion; coerce-then-cut order unchanged | **DISCHARGED at P3 2026-10-25 by commit `75f9e28`** — the wording landed trunk at this seal (proposal §2 `base.py` row + §4 frozen-set + §6 risk 2, `docs/ARCHITECTURE.md` `relmap screen` row, contract `01-requirements.md:827`/LLR-RVH.5.2); LF+TAB joined P12 (`01-requirements.md:261`) and the AT-134/AT-148 arms carry the one-row assertion (contract arms; the AT bodies in `01b-acceptance-design.md`); the arms EXECUTE with lanes 3/4/5 + the trunk Inc-2 gate — re-read there; ledger `LED-2026-10-25-r2.14` (mutant M-RVH-18) | `evidence/pdr-security-reviewer.md` F-SEC-1 (probe-executed: `plain` preserves LF/TAB by design); ledger `LED-2026-10-25-r2.14` |
| COND-SEC-2 (MINOR) | record a Phase-3 wall-clock budget for the `c`-chain BFS at the AT-137 100,000-node cap (same 10× idiom as the derivation budget) and assert it at the Inc-5 exit checks | open — lands in the Phase-3 measurements + Inc-5 packet; re-read at the Inc-5 gate | `evidence/pdr-security-reviewer.md` F-SEC-2 |
| COND-UX-1 (MINOR) | declare the out-of-view behaviour of `enter`/`c`/`k` (inert no-op per the operator-approved static prototype bar, or a crumb note) in the design narrative — any richer answer is a seat change and trunk-owned | **record side discharged at this seal** — §D D3 below carries the declared behaviour — **and DISCHARGED at P3 2026-10-25 by commit `75f9e28`**: the proposal §2 narrative + LLR-RVH.4.1 Statement amendment landed (inert off the home view, or a crumb-note flash) + the AT-148 out-of-view arm; re-read at the trunk Inc-2 gate; ledger `LED-2026-10-25-r2.15` (mutant M-RVH-19) | this record §D D3; `evidence/pdr-ux-reviewer.md` F-UX-1; ledger `LED-2026-10-25-r2.15` |
| COND-UX-2 (MINOR) | add a per-band membership oracle arm to AT-136 (each band's member node ids equal the oracle grouping of `rank_gaps` output), answering the LLR-RVG.1.5 misalignment the round flagged | open — lands in `01b-acceptance-design.md` AT-136 (+ proposal §5.1 RVG.1.5 row); re-read at the Inc-4 (gaps lane) gate | `evidence/pdr-ux-reviewer.md` F-UX-2 |
| COND-UX-3 (MINOR) | fix the stale citation `mapper/screens/palette.py:432` → `mapper/keymap.py:432` (keep `screens/palette.py:36`) in the contract draft-time field and proposal §5.2 | **DISCHARGED at P3 2026-10-25 by commit `75f9e28`** — landed with COND-ARCH-3's citation pass (contract LLR-RVH.4.4 draft-time + proposal §5.2; `screens/palette.py:36` kept); ledger `LED-2026-10-25-r2.17` | `evidence/pdr-ux-reviewer.md` F-UX-3; ledger `LED-2026-10-25-r2.17` |

---

### Post-seal ruling annotation — the D1 surface amendment (trunk Inc-2 review pass, 2026-10-25)

The independent review of trunk Inc-2 (`evidence/review-inc002.md`, verdict `iterate`,
BLOCK-UNTIL F1/F2) found the frozen cursor channel node-axis while the gaps lane's contract is
gap-row axis, and the crumb leaking one view's toggle word across a switch. The orchestrator
ruled the amendment lands at trunk before lanes 3/4/5 fork (F-3 would otherwise fire inside a
lane): D1 gains `row_count(state) -> int`, the host keeps one clamped cursor per view, the
toggle-state word is per view, and the dead `lens` field drops. Recorded per the D6 ruling-
annotation precedent — a declared annotation, not a silent edit; the full text is in the §D D1
row, the contract (LLR-RVG.1.3/LLR-RVH.4.3), `01b-acceptance-design.md` (AT-135/AT-137), the
proposal §4 and `docs/ARCHITECTURE.md` §4, with ledger `LED-2026-10-25-r2.18`.

---

## C · Verdict and what it means

- **Verdict: `approved with conditions` — sealed 2026-10-25.** All four independent reviews
  returned `approved with conditions`; no BLOCKER was found by any lens. Thirteen conditions are
  open at the seal — three MAJOR (COND-ARCH-1, COND-ARCH-2/COND-QA-1 one amendment, COND-SEC-1)
  and ten MINOR — each individually dischargeable and re-read at its named gate, and the DDR
  re-reads all of them (§B row 8). The sealed verdict binds the D1–D5 freeze across trunk Inc-1/
  Inc-2 and lanes L1/L2/L3/shell **as amended by the §B conditions** — D1 gains the named
  toggle-state channel, D2/the Inc-1 set name `adapter.py` (SOURCE 5 — superseded at P3 2026-10-25
  by the orchestrator ruling: Inc-1a + Inc-1b, 4 + 1), the four-sink seam is the
  `_row_text`/`fit` wording — and makes the per-increment file sets of proposal §2.1 the plan with
  that one count corrected.
- A conditional verdict is not an authorisation of the unexecuted: every test named here is
  `planned`; each increment gate re-reads the conditions it owns, the join re-runs every lane's
  ATs (F-5), and the DDR re-reads all of them. The text amendments owned `trunk at seal` are the
  author's first act before trunk Inc-1 consumes the frozen set.
- `rejected` would return the batch to DESIGN, not to implementation — not the case here: the
  design is sound on all three axes (Coverage · Certainty · Evidence); the conditions are
  wording/arms-level, none re-opens a frozen decision, a layout pick, or a lane cut.

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| D1 — frozen interface: the **host↔renderer surface** — the focused state `RelMapScreen` passes the three renderers (the derived `RelMap`, focus/selection, viewport `(w,h)`, lens target, cursor row, host-supplied gap rows, host-owned key/crumb slots) and the one paint entry each renderer exposes; renderers never import each other; sealed at this PDR so lanes 3/4/5 fork safely (F-2). **Amended per COND-ARCH-1: the surface also names the one channel for renderer-owned toggle state (`c` density, `k` by-kind) — host-held flags in the paint entry's view-state, or a frozen renderer state-query/toggle entry; one mechanism, same for all three lanes.** **Ruling annotation, declared at the trunk Inc-2 review pass 2026-10-25 (orchestrator ruling; independent review `evidence/review-inc002.md` F1/F2; `LED-2026-10-25-r2.18`): D1 is amended once more before the lanes fork — the renderer protocol gains `row_count(state) -> int`, each view's own cursor axis (ranked-gap rows for gaps, the node list for matrix/sheet; `0` for the placeholder), the host keeping ONE CURSOR PER VIEW, moved within `[0, row_count)` clamped at the ends (no wrap), the active view's cursor passed in `ViewState.cursor`; the toggle-state word is stored PER VIEW and the crumb shows the active view's own word (switching never shows another view's word; returning restores it); the vestigial `lens` field drops (the matrix lens rides the `enter` toggle channel); the freeze text names the full kind vocabulary (`enter`/`c`/`k`, the matrix crumb word `panel lens`) and the renderer's `notice` obligation. The amendment lands in the contract (LLR-RVG.1.3/LLR-RVH.4.3), `01b-acceptance-design.md` (AT-135's fixture holds ≥2 gaps so "row 02" exists; AT-137's driver names the clamp), proposal §4, and `docs/ARCHITECTURE.md` §4 — the lanes read D1 as amended.** | `PDR-2026-10-25-relmap-r2-batch#D1` | LLR-RVH.4.3; `docs/ARCHITECTURE.md` §4 row "RelMap screen host ↔ renderer surface" (PLANNED → frozen at the seal) |
| D2 — frozen interface: `mapper/relmap/text.py` — `cut(text)`, `DISPLAY_MAX = 120`, `refusal_line(base_name, cause, limit=None)`, one definition site and one import path (the `audit.__all__` re-export drops; zero old-path references in the same increment). **Amended per COND-ARCH-2/COND-QA-1: the re-point set names `mapper/relmap/adapter.py` (fourth live consumer, `adapter.py:29`); Inc-1 SOURCE count becomes 5 with justification.** | `PDR-2026-10-25-relmap-r2-batch#D2` | LLR-RVT.1.1–.1.3; `docs/ARCHITECTURE.md` `relmap` row (the `text` leaf commitment) |
| D3 — frozen interface: the `SCOPE_RELMAP` keymap seat scope — `1`/`2`/`3` view switch, cursor keys, `enter` lens focus, `c` chain toggle, `k` by-kind grouping toggle (SHIPPED per `LED-2026-10-25-r2.01`), `r` refresh, `q` leave, `escape` quiet-leave alias; chord uniqueness inside the scope; BINDINGS/keybar/help/palette all generated from the seat; lands whole in trunk Inc-2 (ARC-02, `LED-2026-10-25-r2.08`). **Amended per COND-UX-1: view-specific chords (`enter`/`c`/`k`) are inert outside their home view (or flash the crumb note) — declared in the design narrative.** | `PDR-2026-10-25-relmap-r2-batch#D3` | LLR-RVH.4.1/.4.2/.4.4; `docs/ARCHITECTURE.md` §4 row "KEYMAP `relmap` scope" |
| D4 — frozen interface: the `--audit` hook per-line bound — after the escape pass, lines longer than 240 cut at 239 with one ellipsis, never splitting an escape spelling, never re-exposing `verdict: `; the R1 `PDR-2026-10-25-relmap-r1-batch#D4` semantics (count bound 1,000, prefix rewrite, fixed no-repo/no-registry lines, exit code) unchanged. **Per F-SEC-3 (folded into the Inc-7 packet, no condition): the Inc-7 spec pins the pipeline order verbatim — escape → cut → rewrite check → print.** | `PDR-2026-10-25-relmap-r2-batch#D4` | LLR-RVU.1.1; `mapper/reqharness/audit.py` (the sink) |
| D5 — frozen detail: the reqharness glyph/table — verifies `✓`, binds `●`/`◐` (`○` the row badge), refines `•`, covers `≡`, diagonal `▪`, no edge `·` (OQ-M3) — so the three renderer lanes share one table | `PDR-2026-10-25-relmap-r2-batch#D5` | LLR-RVM.1.2; the renderer legend lines |
| D6 — the lane plan: trunk Inc-1 (text leaf) → trunk Inc-2 (screen host + seat) → lanes L1 matrix / L2 gaps / L3 sheet / shell (Inc-6 + 6b) → Inc-7 (hook bound, any boundary); SOURCE counts 4/**5**/1/1/1/2/2/1 (Inc-1 = 5 per COND-ARCH-2/COND-QA-1, DDR row 7 reviews it); file sets disjoint; the join runs every lane's ATs before the DDR (F-5). **Ruling annotation, declared at P3 2026-10-25 (orchestrator ruling at the seal, `78ee993`; `LED-2026-10-25-r2.16`): the "Inc-1 = 5" mechanism is superseded — Inc-1 splits into Inc-1a (4) + Inc-1b (1), both trunk before Inc-2; the counts read 4/1/4/1/1/1/2/2/1.** | `PDR-2026-10-25-relmap-r2-batch#D6` | PLAN.md:112-125; `docs/ARCHITECTURE.md` §6 current-batch worksheet |
| D7 — the AT-driver seams, probed 2026-10-25: fixture injection through `MapperApp(workspace=…)` (`mapper/app.py:250` → `MapStore(workspace)` at `:256`) under a headless `run_test()` pilot (`evidence/p2-seam-at-driver.md`, F-5; the qa-reviewer's PDR re-run reproduced the recorded transcript byte-identically), and the workspace-as-repo canon rule — `Path(workspace)/canon` (`mapper/relmap/adapter.py:129`), flat `os.listdir(workspace)` discovery (`mapper/relmap/descriptor.py:200-208`), git never consulted, closed-set `unavailable` cause (`evidence/p2-seam-workspace-repo.md`) | `PDR-2026-10-25-relmap-r2-batch#D7` | `01b-acceptance-design.md` "Driver seams (shared)"; LLR-RVH.3.3 |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
design record: it is reflected in the requirement or in the module map, which are versioned beside
the code. The §B conditions name the requirement/module-map lines each amendment lands in.
