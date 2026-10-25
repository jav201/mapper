# QA second-pass re-check — batch 2026-10-23-hygiene-batch

> Reviewer: `qa-reviewer — Kimi K3 subagent executing agents/qa-reviewer.md`
> Scope: P2 re-check of F3 / m5 / m6 (author dispositions under `LED-…batch.5`–`.8`) + PDR QA-lens review of `design/design-proposal.md` (rows 3, 5, 6).
> Date: 2026-10-23. All paths repo-relative. Read-only: no requirement, test or code changed.

## 1 · Per-finding verdicts (TASK A)

### F3 — state matrix recorded and bound — **verified**

- `design/state-matrix.md` exists and is complete: |states| = 4 (`plain`/`folded`/`empty`/`orphan`), each state with a code-derived definition, source citations, and a per-renderer applicability matrix (● reacts / ○ exercised-no-op with byte-identical-to-plain invariance proof). Binding block: 6 renderers × 5 sizes × 4 states = 120 assertions; amendment = design change re-opening PDR.
- Contract binding present: HLR-Q3.1 threshold (`01-requirements.md:284`) keys on "4 recorded states … per the state matrix recorded at `design/state-matrix.md`"; LLR-Q3.1.2 statement + threshold (`:402`, `:405`) bind to the same artifact and the 120 figure. Ledger `LED-2026-10-23-hygiene-batch.7` (`01-requirements-ledger.md:54-59`) records the amendment with asserting test `test_sweep` and mutant M-Q3-1.
- Derivation evidence in ledger .7 checked line-by-line against code — all citations hold:
  - `mapper/views/layered.py:660-661` — `if graph.root_id is None or not graph.nodes: return Text("(no map loaded)")` ✓
  - `mapper/views/layered.py:158-168` — `_hidden_ids(index, folded)` ✓; `:382-387` — `state.folded` reads in `_geometry` ✓. Repo grep confirms `.folded` is read ONLY in `layered.py` across `mapper/views/` (fold-invariance premise for the other five renderers is sound).
  - `mapper/views/outline.py:147-149` — empty short-circuit "(no map loaded)" ✓; `:214-218` — `walk()` does `graph.nodes[cur]` (KeyError on a dangling child id — the matrix's excluded-state (a) claim is accurate) ✓; `:285` — `walk(graph.root_id, 0)` (orphans silently un-painted) ✓.
  - `mapper/views/radial.py:177-178` — empty short-circuit ✓; `:421` — `unpainted` declared in the header ✓.
  - `mapper/views/lane.py:117-119`, `:181-185`, `:326-328` — empty short-circuits for the three lane-family renderers ✓ (text is "(no repo loaded)" — see finding n1).
  - Roster census of six confirmed: `mapper/views/__init__.py` exports HybridLane, Lane, RailTimeline, Layered, Outline, Radial.
- Vacuous-pass judgement: a trivially small state set can no longer pass silently — |states| is pinned to a recorded artifact whose amendment re-opens the PDR, the roster guard (LLR-Q3.1.1) fails loudly on an empty/changed roster, and the threshold is 120 named assertions. The F3 defect class is closed.

### m5 — Q2 observation point (screen arm) — **confirmed-open-correctly-carried**

- `design-proposal.md` §5 carries the arm: row `tests/test_ingestion_limits.py screen arm` (Layer B, AT-109…114) — "≥ 1 arm per refusal kind driven through the running screen, asserting the toast text (review m5). Toast consumers verified by grep 2026-10-23…".
- Consumers verified independently:
  - `mapper/screens/construct.py:57` — `except MapStoreError as e:` → `_refusal_toast(self, e)` → `screen.notify(...)` ✓
  - `mapper/screens/common.py` — `_save_or_toast` (:217) guards `store.save()` and toasts; `_refusal_toast` (:205-214) toasts `MapIdError` text ✓
  - `mapper/app.py` — grep `MapStoreError`: zero hits; the carry record's "app.py does NOT consume" is correct ✓
- Carry is correctly targeted at Phase 3 / the Q2 increment gate.

### m6 — device-name arms pin location — **confirmed-open-correctly-carried** (one citation defect, finding n2)

- `tests/test_seed_safety.py:42` — `BAD_NAMES = ["../x", "..\\x", "C:\\x", "CON", "a/b", "a:b"]` (CON present) ✓; `:230-249` — `test_seed_store_refuses_every_write_door` parametrised over BAD_NAMES + `NUL.txt`/`com1`/`lpt9` etc., asserting `MapStoreError` on all four write doors (save/create/create_seed/create_from_template) with no path leak ✓.
- `tests/test_inc9n.py` — the device list sits at :59-62 but is named **`DEVICES`**, not `_RESERVED` as the proposal §5 claims; content matches (con, nul, conin$, COM¹, `sub\con`, `C:\a\NUL.txt`, …) ✓. Refusal-before-open arms at :257-283 verified: `safe_local_path` refused before any filesystem call (:259-264), CSV-prompt device arms open nothing (:272-287) ✓.
- Neighbours verified: `tests/test_en4.py:37` (`DEVICE_TOKENS = frozenset({"CON"})`, referencing `store._RESERVED_NAMES`) ✓; `tests/test_seed2.py:167` (SEED2-F5 CONIN$/CONOUT$/CLOCK$ arms) ✓.
- `tests/test_store.py` — grep `reserved|CON|NUL|check_map_id|is_reserved`: zero hits. The contract's original example was indeed wrong; the correction stands ✓.

## 2 · PDR review — QA lens (TASK B)

### Row 5 — proposed test cases observable and non-vacuous — **✓ with one ⚠ (finding n4)**

Every §5 row names its reddening mutation (the six RED-counterfactual rows justify `n/a — the counterfactual IS the mutation`). Non-vacuity guards present: roster completeness arm reddens on a dropped renderer; the empty-state sweep asserts the short-circuit rather than `h`; device-name pin reddens on dropping the osopen reserved check.

Threshold cross-check vs contract:

| Contract threshold | §5 row | Match |
|---|---|---|
| cap±1 (byte cap: stat-oversize + grow refuse; cap−1 loads) | test_byte_cap… | ⚠ refusal arms only; the cap−1-loads positive arm is not restated |
| depth 64 parses / 65 refuses | test_prescan_* | ⚠ depth-65 refuse ✓; depth-64-parses positive arm not restated |
| NUL at byte 0 / 8,191 refuse | test_csv_* | ✓ (the 8,200-not-refused probe bound is not restated — cosmetic, the contract holds it) |
| 100,001 node/edge refuse, at-cap parses | test_count_caps | ✓ |
| 10,000-deep refusal < 5 s, no RecursionError | test_prescan_* | ✓ |
| 6 × 5 × 4 = 120 | test_sweep | ✓ |

### Mutant coverage per LLR

| LLR | Asserting test (contract + §5) | Reddening mutation | Mutant breaks the clause it claims? |
|---|---|---|---|
| LLR-Q1.1.1 | `test_no_color_removed_before_super` (+ AT-108 black-box arm) | M-Q1-1 (delete neutralisation) | ✓ — var survives construction → both the unit and the byte-equal screen arm redden |
| LLR-Q2.1.1 | `test_byte_cap_refuses_and_names_limit` (AT-109) | M-Q2-2 (re-check removed) | ✓ — grow-between-stat-and-read slips through only if the re-check is gone |
| LLR-Q2.1.2 | `test_prescan_*` (AT-110/111) | M-Q2-1 (prescan bypassed) | ✓ — anchor/alias/depth arms load instead of refusing |
| LLR-Q2.1.3 | `test_count_caps` (AT-112/113) | M-Q2-4 (count check removed) | ✓ — 100,001-node/edge arms parse instead of refusing |
| LLR-Q2.2.1 | `test_csv_*` (AT-114) | M-Q2-3 (probe deleted) | ✓ — NUL-at-0/8,191 arms import instead of refusing as binary |
| LLR-Q2.3.1 | none — validation is `inspection` (PDR census, re-run at the Q2 gate) | none by design — the counterfactual IS the census re-run diff | by design (contract `:382-386`); the guarded behaviour itself is pinned by the seed-safety/inc9n arms with mutation "drop the reserved check in osopen" (§5 device-name row) |
| LLR-Q3.1.1 | `test_renderer_roster_derived` | drop one renderer from `mapper.views.__all__` | ✓ — completeness guard asserts == 6, fails loudly below it |
| LLR-Q3.1.2 | `test_sweep` (AT-115) | M-Q3-1 (renderer emits h+1 lines) | ✓ — exactly-h geometry assertion names renderer+size+state |
| LLR-Q3.2.1 | `test_events` (AT-116) | M-Q3-2 — see finding n3 | ⚠ — clause-reddening holds, but the mutant id denotes two different mutations (n3) |
| LLR-Q3.2.2 | `test_byte_identity` | M-Q3-3 (sink touches the buffer) | ✓ — rows() diverge with vs. without sink |
| LLR-Q3.2.3 | `test_sweep_audit_arm` | M-Q3-2 (swallow an audit event) | ✓ — no audited canvas records events → unexplained-event failure vanishes → arm reddens on the ≥1-audited-canvas assertion |

No LLR lacks an asserting test except LLR-Q2.3.1, which the contract deliberately classes as `inspection` with the census re-run as its own counterfactual — declared, not a gap.

### RED counterfactuals (C11) — ✓ all six deliverable files

`mapper/app.py` → `test_colour_always_on.py` + `test_help_scope.py` ambient pin; `mapper/store.py` → ingestion arms + existing load suite; `mapper/diff.py` → diff arms; `mapper/import_csv.py` → CSV arms; `mapper/osopen.py` → reader arms + `test_arch_osopen_callers.py`; `mapper/canvas.py` → audit arms + B-44 pin + golden digests. Each names the suites that go RED and the packet owning the transcript (L1/L2/L3).

### Row 3 — forward applicability (§7) — ✓

Five output rows, every one with a named consumer and reading location (Phase-3 lane gates / DDR §B checklist / traceability matrix + PDR record / PDR §B + DDR row 3). No empty consumer cells; the "none empty" self-declaration is accurate.

### Row 6 — gauntlet controls with owners — ✓

- C11 habits: RED counterfactuals declared at authoring time (§5: "Declared here, at authoring time, not at execution time"), transcripts assigned to the L1/L2/L3 increment packets — owners named.
- B-44 pin amendment discipline: same-landing, declared twice — §4 Canvas row ("B-44 pin `tests/test_a3_census.py:658-674` (amends, same landing)") and §8 L3 lane row.
- Golden no-re-baselining (LLR-Q3.2.2): §1 "will NOT re-baseline any golden"; §8 byte-pinned must-stay-green list (`test_repair_depth.py:109/:252-254`, `test_perf_paint_clip.py:172`, `test_help_scope.py:78-94/:247-274`).
- Numeric thresholds: see Row 5 table — two positive boundary arms not restated in §5 (n4).

### Empty-state claim vs renderer code — ✓ consistent

The matrix's "every renderer short-circuits to ≤ 2 named lines; 'exactly h' not applicable" holds against the code: layered returns a single `Text` (:660-661), radial a single `Text` (:177-178), outline header + 1 line (:147-149), and the three lane-family renderers header + 1 line (:117-119, :181-185, :326-328). The sweep asserting the short-circuit rather than `h` for zero-node graphs is the correct, code-derived shape.

## 3 · New findings

| ID | Severity | What | Evidence |
|---|---|---|---|
| n1 | minor | LLR-Q3.1.2's threshold names the empty-state text as "'(no map loaded)'", but the three lane-family renderers emit "(no repo loaded)"; the state matrix itself handles this correctly ("the named text present", per-renderer citations) — contract wording slack only | `01-requirements.md:405` vs `mapper/views/lane.py:118, :184, :327` |
| n2 | minor | `design-proposal.md` §5 (m6 carry) cites `tests/test_inc9n.py` "`_RESERVED` list :60-62" — the actual identifier is `DEVICES` (:59-62). Lines and content right, name wrong; a Phase-3 grep for `_RESERVED` in that file finds nothing, repeating the m6 defect class | `design-proposal.md:151` vs `tests/test_inc9n.py:59` |
| n3 | minor | Mutant id M-Q3-2 denotes two distinct mutations: the contract's "event recording/append removed" (`01-requirements.md:307`, `:417`) and §5's/ledger .8's "drop the alphanumeric gate" (the asserting mutant for the m3 second-limb clause). Both redden `test_events`, but the L3 counterfactual transcript needs both mutations applied (or a second id minted) for the amended second-limb clause to have a demonstrated reddening | `design-proposal.md:149` vs `01-requirements.md:417`; `01-requirements-ledger.md:65` |
| n4 | minor | §5's refusal-kind rows omit the positive boundary arms the contract thresholds require (cap−1 loads for the byte cap; depth-64 parses for the prescan). Refusal arms alone are vacuous against an always-refuse implementation; the contract thresholds (`:341`, `:352`) hold them, so this is a proposal-record omission, not a contract hole | `design-proposal.md:141-142` vs `01-requirements.md:341, :352` |

## 4 · Overall

All three second-pass verdicts confirm the author's dispositions (F3 verified; m5/m6 correctly carried open). The design proposal passes the QA PDR lens with four minor record-level findings (n1–n4), none blocking: the missing pieces all live in the contract's own thresholds, so the fixes are one-line record amendments, owed at the lane packets at the latest.

**Verdict:** `approve`

**Role cell:** `qa-reviewer — Kimi K3 subagent executing agents/qa-reviewer.md · approve`
