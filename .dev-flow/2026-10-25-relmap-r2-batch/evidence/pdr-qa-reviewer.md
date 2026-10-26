# PDR evidence — qa-reviewer — batch 2026-10-25-relmap-r2-batch

## Mode: plan (results are `planned`; only the probes I re-ran are `executed`, executed by me)

I am the `qa-reviewer` at the PDR gate, in **plan mode**: every test named below is `planned`.
The only `executed` items in this file are the seam-probe re-run and the guard-set runs, both
executed by me (qa-reviewer) on 2026-10-25 in the worktree. I authored none of the artifacts
under review; I edited nothing but this file.

## Scope reviewed

- `.dev-flow/2026-10-25-relmap-r2-batch/design/design-proposal.md` (336 lines) — the artifact under review.
- Contract `.dev-flow/2026-10-25-relmap-r2-batch/01-requirements.md` §4 (LLR table + M-* mutants; F-1…F-5 at :270-274).
- Acceptance design `.dev-flow/2026-10-25-relmap-r2-batch/01b-acceptance-design.md` (AT-130…AT-152, matrix at :293-319).
- `docs/ARCHITECTURE.md` guard-set / census rows (:355-368).
- Code anchors: `mapper/app.py:250,256` · `mapper/relmap/adapter.py:29,121,129,138` ·
  `mapper/relmap/descriptor.py:30,200-208,211` · `mapper/relmap/model.py:34,67-71` ·
  `mapper/relmap/audit.py:34,209-210` · `mapper/osopen.py:93-94` · `mapper/keymap.py:41` ·
  `mapper/screens/home.py:176,209,300` · `tests/test_colour_always_on.py:25-34,64-70` ·
  `tests/test_keymap.py` (R1) · `tests/test_inc9c.py:274`.
- Pre-implementation state confirmed: `mapper/screens/relmap/` does not exist; none of
  `tests/test_relmap_text.py`, `test_relmap_matrix.py`, `test_relmap_gaps_view.py`,
  `test_relmap_sheet.py`, `test_relmap_shell.py`, `test_relmap_scalecheck.py`,
  `test_hook_line_bound.py` exist on disk (consistent with the plan's "(planned)" marks).

## Record §A rows in my lens

| row # | ✓/⚠/✗ | Evidence |
|---|---|---|
| 1 Proposal complete | ✓ | §1-§6 present; six rejected alternatives + three honest `n/a` rows (proposal :294-305); no empty consumer rows in §7 (:307-318) |
| 2 Respects ARCHITECTURE boundaries | ✓ | `screens/relmap` package row, dependency row, edges and R-016/R-018/R-019 all present at the cited lines (`docs/ARCHITECTURE.md` relmap/relmap-screen rows, R-016 :319, R-018 :321, R-019 :322 as cited); no boundary moves proposed |
| 3 Forward applicability | ✓ | §7 six rows, each with a named downstream (:309-316) |
| 4 Every requirement has foreseen coverage | ✓ | §5.1 names asserting tests for all 52 LLRs across the six families; AT-130…152 in `01b:293-319`; chain map §1 (:67-69). Spot-check found no orphaned LLR |
| 5 Test cases observable + non-vacuous | ⚠ | Mutant named per LLR and feasible in every family I checked (table below), **except** the M-RVS-9 live-arm caveat (F-QA-5) |
| 6 Gauntlet controls declared | ✓ | §2.1 exit checks + guard set C-1 (:112-114), lane fixture policy ARC-05 (:115-118), §3 Resource (:172-177), §6 risks; both seam probes executed — probe (a) re-run by me below, PASS |
| 7 Interfaces frozen listed | ⚠ | D1-D5 declared (:191-197), but the D2/`text.py` freeze set omits `adapter.py`, a live fourth consumer of the moved names (F-QA-1) |
| 8 Lane plan disjoint, family-B census per lane | ⚠ | Lane intersections empty and SOURCE counts 4/4/1/1/1/2/2/1 as declared (:332-333) — **but** the Inc-1 count of 4 is inconsistent with the contract's four-module re-point statement once `adapter.py` is counted (F-QA-1), and Inc-2's `test_keymap.py` is labeled "(new)" though it exists (F-QA-2) |
| 9 UX lens (D1) | n/a — ux-reviewer's row, owed at seal | — |
| 10 Security lens (C6/C8) | n/a — security-reviewer's row, owed at seal | I note only that the hostile-payload arms (AT-134/139/144/148) are present and drive the real surface |

## Mutant spot-check

All R2 asserting tests are `planned` (files do not exist). Judgments are feasibility reads of
the AT/unit arms in `01b-acceptance-design.md` against the contract §4 mutant descriptions.
No mutant I checked is unkillable; one is only partially killed by its live arm (RVT.3.3/M-RVS-9).

| LLR | mutant | named test | exists? | would the mutant turn it RED? | state |
|---|---|---|---|---|---|
| RVM.1.1 | M-RVM-1 (drop row windowing) | `test_relmap_matrix.py` window-census arms + AT-137 cap-scale arm | no (planned) | yes — unwindowed rows at the 100,000-node cap (`mapper/osopen.py:93-94`) leave undeclared rows / audit clip events; deterministic counters, no clock | planned |
| RVM.2.2 | M-RVM-7 (None reach coerced to 0) | `test_lens_reach_not_computed` / AT-132 budget-spent arm | no (planned) | yes — `not computed` + absence of `reaches \d+`; the spend-budget mechanism exists (`mapper/relmap/model.py:193-214`, visit budget) | planned |
| RVM.4.2 | M-RVM-11 (raw canon text in markup sink) | AT-134 hostile arm (live Textual surface) | no (planned) | yes — parse error or leaked style on the shipped surface; payload vocabulary established (`01b:27-29`) | planned |
| RVG.1.1 | M-RVG-1 (re-sort by node id / skip `rank_gaps`) | `test_relmap_gaps_view.py` rendered-order arm | no (planned); R1 oracle `test_relmap_gaps.py::test_ranking` exists | yes — order differs from the ranked oracle on any multi-gap fixture | planned |
| RVG.2.1 | M-RVG-8 (`.upper()` restored / caps literal) | AST casing census + rendered `us without at` assertion | no (planned); census idiom exists (`tests/test_relmap_isolation.py`) | yes — both arms redden (rendered string + derived-set census, C-31) | planned |
| RVG.3.1 | M-RVG-13 (markup-parsing sink) | AT-139 composited-frame arm | no (planned) | yes — `_painted_frame` (`tests/test_colour_always_on.py:25-34`) records style runs; a `[bold]` leak is a payload-attributable span | planned |
| RVS.3.1 | M-RVS-7 (both-direction hop-2 count) | TC-RM-17 independent up-only oracle, synthetic 3-level fixture | no (planned) | yes — asymmetric up/down hop-2 counts disagree with the oracle | planned |
| RVS.3.3 | M-RVS-9 (note flips, row set does not) | AT-141 `c` toggle arm + TC-RM-17 fixture arm | no (planned) | **partial on the live arm** — on the one-hop skeleton stacked rows == direct rows, so "rows unchanged" cannot see the row-set half of the mutant; the kill rests on the TC-RM-17 synthetic 3-level fixture arm (named in `01b:167-168`). Gate must require that arm, not only the live assertion (F-QA-5) | planned |
| RVS.6.2 | M-RVS-12 (rows dropped past viewport, no counted line) | AT-141/AT-143 counted-overflow arm | no (planned) | yes — last-line `… +NN more` assertion is deterministic; cap-scale arm (`01b:119-124`) exercises it at 100k nodes | planned |
| RVH.1.3 | M-RVH-3 (relation rows appended after tree rows) | AT-145 order arm | no (planned) | yes — asserted name sequence (`demo, legacy` with `demo` < `legacy`) breaks under append-after (`01b:204-207`) | planned |
| RVH.3.2 | M-RVH-8 (`r` re-renders from cache) | AT-148 derive count (1 at open, 2 after `r`) | no (planned) | yes **if** the counter wraps `derive_reqharness_map` rather than replacing it (C-16, F-QA-4) | planned |
| RVH.3.3 | M-RVH-16 / M-RVH-17 (git consulted / raw exception escapes) | AT-147 non-git fixture arm + app-lives arm | no (planned); derivation seam probed | yes — probe (b) verified today's path is git-free and closed-set (`evidence/p2-seam-workspace-repo.md`; I re-verified the code anchors, below) | planned |
| RVT.1.1 | M-RVT-1 (second `def cut` left in `model.py`) | `test_relmap_text.py` definition-site census (counts 1/1/1) | no (planned) | yes — AST census reads 2 (C-31 derived set) | planned |
| RVT.1.3 | M-RVT-3 (moved `cut` drops the ellipsis) | byte-identity probe + R1 goldens | no (planned); R1 suite + `tests/test_prescan_refusal_goldens.py` exist | yes — `mapper/relmap/model.py:67-71` pins the ellipsis contract; R1 snapshot arms unchanged | planned |
| RVU.1.1 | M-RVU-1/2/3 (cut before escape / re-exposed `verdict: ` / mid-spelling cut) | `test_hook_line_bound.py` + AT-152 | no (planned) | yes — emitted-length ≤ 240, prefix-exclusivity and straddling-spelling arms are deterministic string oracles over the escaped form (`01b:279-291`) | planned |

RED counterfactual (§5.1 column 2): feasible and honest for every new/edited file — each
increment names the test files written in the same increment (§2.1), and §5.1's header states
the move-aside discipline. Two corrections: `tests/test_keymap.py` exists today (R1), so Inc-2's
RED story is "existing + new conformance arms fail", not a new file (F-QA-2); and the Inc-1
RED story is incomplete without `adapter.py` (F-QA-1).

## Seam probe re-run (executed by me, qa-reviewer)

Re-created the recorded script from `evidence/p2-seam-at-driver.md` (verbatim, including its
neutral synthetic fixture), ran it from the worktree root with the recorded environment.
Script and temp workspaces lived in a scratch dir outside the repo and were deleted after the run.

Command:

```
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 \
  PYTHONIOENCODING=utf-8 python <scratch>/probe_seam_at_driver.py
```

**PASS (exit 0)** — output tail:

```
[probe] recents table rows: [['svc_probe', ' legacy ', '3', '0']]
[probe] relation-map row observed (name/kind/nodes): OK
[probe] store.load('svc_probe'): 3 nodes, 2 schema fields: OK
[probe] home hero carries the map name: OK
[probe] exited cleanly: OK
PROBE-RESULT: PASS
```

Byte-identical to the recorded transcript (`evidence/p2-seam-at-driver.md:144-153`). The seam
is viable on today's code; AT-130…149 are drivable through the shipped surface.

`evidence/p2-seam-workspace-repo.md` sanity check against the code (inspection, by me):

- `mapper/relmap/adapter.py:129` — `text = read_repo_text(Path(repo) / descriptor.canon, LIMIT_ROLES_YML_BYTES)` ✓ matches the claim.
- `mapper/relmap/descriptor.py:200-208` — `discover_descriptors` is a flat `os.listdir(repo)` filtered by `.relmap.yml`, capped at 8 ✓.
- "No git anywhere in `mapper/relmap/`" — I ran the grep myself: **zero hits** for `git|rev-parse|.git` over the package ✓.
- The wrapper nuance (the `--audit` CLI hook IS git-gated via `identity.repo_root`; a bare dir sees `structure: unavailable (no repository)`) is accurately recorded and correctly scoped OUT of LLR-RVH.3.3 (`01-requirements.md:776`).

## Guard-set run (executed by me, qa-reviewer)

```
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider tests/test_fold.py tests/test_repair_artifact_claims.py
```
**196 passed, 3 xfailed in 41.48s** — green. (One pre-existing `SyntaxWarning: invalid escape sequence '\d'`, not a failure.)

```
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider tests/test_no_operator_paths.py
```
**2 passed in 0.82s** — green.

Runtime budget (§2.1 footer + C-1 + C-25): per-increment targeted run + guard set is honest
and bounded (guard set alone measured 41.5s here; targeted files add seconds-to-minutes, and
AT-137's cap-scale arm is the only heavy arm, deterministic); the ONE full-suite run is owned
by the orchestrator. Story holds.

Cap-scale arms (AT-137): deterministic counters only — windowing census, counted overflow,
audit-sink zero clip/overprint. The single time element is the open/`r` budget, and its wording
must stay a recorded measurement (F-QA-3). No wall-clock assertion should be committed.

## Findings

### F-QA-1 — Inc-1 omits `adapter.py` from the `text.py` re-point set [MAJOR]

- **What.** The contract's LLR-RVT.1.1 statement names FOUR importing modules — "`model.py`, `descriptor.py`, `adapter.py` and `audit.py` shall import these names from `text`" (`01-requirements.md:832`). But `mapper/relmap/adapter.py:29` today does `from mapper.relmap.model import Edge, Node, RelMap, build_map, cut` and calls `cut` at `:138`. The proposal's Inc-1 row lists only three re-points (`design-proposal.md:103`: `model.py`, `descriptor.py`, `audit.py`), as does the §4 D2 row (`:184`) and §5.2 (`:242`).
- **Why it bites.** Inc-1's own exit check requires "reader census over the old import paths (`relmap.model.cut`, …) zero in the same increment" (`:103`) and LLR-RVT.1.2's census requires zero `relmap.model.cut` references (`01-requirements.md:840`) — with `adapter.py:29` unre-pointed, **both censuses fail at the Inc-1 gate**. The alternative — including `adapter.py` — makes Inc-1's SOURCE count 5 (text.py + 4 re-points), contradicting the declared ≤4 (`design-proposal.md:99`) and the record's §B row 7 "planned maximum is 4, on trunk Inc-1 and Inc-2 only".
- **Recommendation.** Amend the proposal (§2.1 Inc-1 row, §4 D2, §5.1, §5.2, §8 counts) to name `mapper/relmap/adapter.py` in the re-point set and declare Inc-1's SOURCE count as 5 with a one-line justification (trunk-only, behaviour-preserving import re-point), OR re-cut Inc-1. The tests themselves are fine — this is a plan-vs-contract inconsistency the increment gate would hit on day one.
- **Proposed condition:** COND-QA-1 · MAJOR · name `adapter.py` in the text-leaf re-point set and re-declare Inc-1's SOURCE count (5) with justification, in proposal §2.1/§4/§5.1/§8 · owner: design fix at seal, verification at trunk Inc-1 gate.

### F-QA-2 — `tests/test_keymap.py` is labeled "(new)" but exists (R1); the Inc-2 census story needs it explicitly [MINOR]

- **What.** `tests/test_keymap.py` is on disk — the R1 US-N03 universal whose binding set is *derived from `KEYMAP` at import* (`tests/test_keymap.py:1-16`), so it will begin quantifying over `SCOPE_RELMAP` the moment the seat lands. Proposal §2.1 lists it under "New tests" for Inc-2 (`design-proposal.md:104`). Separately, §5.2 names `tests/test_key_dispatch.py:137` as part of the Inc-2 census (`:237`) but the Inc-2 exit-checks cell and §2.1 targeted-run story do not list it.
- **Why.** The RED move-aside for `mapper/keymap.py` is actually *stronger* than claimed (the existing universal fails on import), but the plan as written mis-describes the file, and a seat addition can require new rows in the whole-seat dispatch table — if Inc-2's targeted run omits `test_key_dispatch.py`, a drift there surfaces late (at the join, F-5, or the DDR).
- **Recommendation.** Correct "(new)" to "extended (R1 US-N03 universal)" and add `tests/test_key_dispatch.py` to Inc-2's targeted run / exit checks.
- **Proposed condition:** COND-QA-2 · MINOR · fix the `test_keymap.py` "(new)" label and add `test_key_dispatch.py` to the Inc-2 targeted run · owner: trunk Inc-2 gate.

### F-QA-3 — AT-137's open/`r` wall-clock budget wording must stay a measurement, never a test assertion [MINOR]

- **What.** AT-137's cap-scale arm says the derivation "completes within a bounded wall-clock budget recorded at Phase 3 (generous bound: 10× the 303-node skeleton baseline)" (`01b-acceptance-design.md:122-124`). The proposal's §3 Resource reads it as "recorded at Phase 3" (`design-proposal.md:176`), but the AT body can be read as a test assertion.
- **Why.** A committed 10× wall-clock assert over a 100,000-node in-test derivation is a flake seed on a loaded machine (the project's own FLAKE-2 history in `tests/test_help_scope.py:43-51` is exactly this class), and the gauntlet's cap-scale discipline is determinism — census and counted overflow, no clocks.
- **Recommendation.** Pin the wording: the budget is recorded in the increment packet / AT results as a measurement; the committed test asserts only the deterministic arms (windowing census, counted overflow, audit emptiness).
- **Proposed condition:** COND-QA-3 · MINOR · amend AT-137 / the Inc-4 packet so the 10× budget is a recorded measurement with no wall-clock assert in a committed test · owner: L2 (Inc-4) gate.

### F-QA-4 — AT-147/AT-148 derivation-args and derive-count instrumentation must wrap, not replace (C-16) [MINOR]

- **What.** AT-147 asserts "derivation received `default_descriptor()` values" (`01b:227-228`) and AT-148 asserts "derive call count 1 at open, 2 after `r`" (`01b:237-238`) — both on Layer B (pilot-driven) ATs.
- **Why.** If implemented as a `monkeypatch` replacement of `derive_reqharness_map`, the Layer B arm stops exercising the real mechanism — a C-16 proxy in an AT id. A wrapping counter/spy (real function executes, args and count observed) preserves both the observation and the mechanism; the unit arms (RVH.3.2's monkeypatched derive-count, `01-requirements.md:769`) are Layer A and unrestricted.
- **Recommendation.** Record at Phase 3, in the Inc-2/Inc-6 packets, that the Layer B instrumentation wraps `mapper/relmap/adapter.derive_reqharness_map`.
- **Proposed condition:** COND-QA-4 · MINOR · document that AT-147/AT-148 derivation observation wraps rather than replaces the derive entry point · owner: trunk Inc-2 / shell Inc-6 gates.

### F-QA-5 — M-RVS-9 is only partially killed by its live arm; the TC-RM-17 synthetic arm must be the gate requirement [MINOR]

- **What.** LLR-RVS.3.3's mutant M-RVS-9 flips the note/tag but not the row set. On today's one-hop skeleton, stacked rows are byte-identical to direct rows, so AT-141's live "rows unchanged on today's one-hop chains (asserted, not assumed)" arm (`01b:162`) **cannot observe the row-set half of the mutant** — the live arm alone is vacuous against M-RVS-9.
- **Why.** The kill exists in the plan — the TC-RM-17 renderer-level fixture arm on a synthetic 3-level chain (`01b:167-168`) — but §5.1's RVS.3.3 row cites "`c` toggle + crumb arms (AT-141)" without naming the synthetic arm as the load-bearing kill for M-RVS-9.
- **Recommendation.** Make the Inc-5 gate text require the TC-RM-17 synthetic 3-level fixture arm for M-RVS-9 (the live arm covers only the note/crumb half).
- **Proposed condition:** COND-QA-5 · MINOR · require the TC-RM-17 synthetic fixture arm (not the live one-hop assertion) as the M-RVS-9 kill at the Inc-5 gate · owner: L3 (Inc-5) gate.

### F-QA-6 — AT-150 is a source census, not an operator-observable behavior [MINOR — note only, no condition]

- **What.** AT-150 (one site / one import path) is realized as an AST/grep census (`01b:259-266`, surface column says "AST/grep census" at `:317`).
- **Why it is acceptable.** The deliverable of US-RMV-005 IS the on-disk artifact ("the artifact on disk — whichever the surface is" per the Layer-B checklist), the matrix declares the surface honestly, and C-18 gives it exactly one on-disk node. AT-151's byte-identity arm runs the shipped `--audit` CLI (`01b:268-277`), a true shipped-surface check. No condition; recorded so the DDR does not re-litigate it.

## Verdict

`approved with conditions` — COND-QA-1 (MAJOR, must land in the proposal/record before or at seal;
the rest discharge at their named increment gates):

- COND-QA-1 · MAJOR · name `adapter.py` in the `text.py` re-point set and re-declare Inc-1's SOURCE count (5) with justification (proposal §2.1/§4/§5.1/§8) · owner: design fix at seal, verified at trunk Inc-1 gate
- COND-QA-2 · MINOR · correct `test_keymap.py` "(new)" → existing R1 file extended; add `tests/test_key_dispatch.py` to the Inc-2 targeted run · owner: trunk Inc-2 gate
- COND-QA-3 · MINOR · AT-137's 10× open/`r` budget is a recorded measurement in the packet, never a wall-clock assert in a committed test · owner: L2 (Inc-4) gate
- COND-QA-4 · MINOR · AT-147/AT-148 derivation observation must wrap, not replace, `derive_reqharness_map` (C-16) · owner: trunk Inc-2 / shell Inc-6 gates
- COND-QA-5 · MINOR · the M-RVS-9 kill at the Inc-5 gate is the TC-RM-17 synthetic 3-level fixture arm, not the vacuous live one-hop row-unchanged assertion · owner: L3 (Inc-5) gate
