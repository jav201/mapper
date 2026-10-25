# DDR review — qa-reviewer — 2026-10-23-hygiene-batch

Mode: validation
Role cell: qa-reviewer — Kimi K3 subagent executing agents/qa-reviewer.md · **approved**

## Findings

| Id | Severity (BLOCKER/MAJOR/MINOR) | file:line | One line |
|---|---|---|---|
| QA-DDR-1 | MINOR | `.dev-flow/2026-10-23-hygiene-batch/01-requirements-ledger.md:107` | Ledger `.14` names the M-Q2-1-XB14 surplus RED arms as "AT-111/112"; the transcript shows the surplus is AT-111×2 + `test_diff_side_anchor_head_yields_none` (6 failed / 32 passed) — wording nit only; the catch on the three amended arms is proven |

No BLOCKER/MAJOR. All other assigned rows verified clean.

## Checklist rows re-read

| Row | ✓/⚠/✗ | Evidence (file:line / command / hash) |
|---|---|---|
| §B row 3 — crossed census B1 miss discharge | ✓ executed | `evidence/xbatch14-red-2026-10-24.txt` tail: 3 failed (the three named `test_llr_n13_1_7_*` arms) · `xbatch14-green-…`: 38 passed · `xbatch14-mutant-…`: 6 failed incl. all three amended arms RED. sha256 prefixes match increment-003:333-335 (`6441d9c3…` / `269e1474…` / `07bde202…`). Ledger `.14` present (01-requirements-ledger.md:107). Fixture-content re-derivation below — class closed |
| §B row 4 — AT-NNN → exactly one node (C-18) | ✓ executed | grep `def <name>`: all 15 named nodes exist in the four named files (`test_colour_always_on.py`, `test_ingestion_limits.py`, `test_scalecheck.py`, `test_canvas_audit.py`); `test_sweep`/`test_events`/`test_byte_identity`/`test_painted_screen_byte_identical…` unique suite-wide. AT-111 "cited, not declared" — honest: declared in the contract itself (01-requirements.md:241, V2-tokenizer rationale), realized as two lowercase-named nodes; AT-116 one-chain-three-nodes reconciled in 04-validation.md Layer B :128. Declared exceptions, not C-18 violations |
| §B row 5 — ledger 3546 − 0 + 33 = 3579 | ✓ executed (partial) | D=0 executed: `git diff b5dba72..a860a27 -- tests/ | grep -c '^-.*def test_'` → 0. A: `grep -c '^+.*def test_'` → 31 executed; "+2 parametrized expansions" by inspection — `tests/test_colour_always_on.py:37` parametrizes one def over 3 values. "Actual collected 3579" not-run (full-suite collect outside my mandate); gate-run count 3575 passed consumed from the hash-verified transcript |
| Conditions 5 + 6 | ✓ executed | Cond 5 spot-checks: n3 → M-Q3-4 minted at 01-requirements-ledger.md:75-79 (ledger `.10`); F-UX-2 load surfaces named at design-proposal.md:147 and :215 and the sites exist on disk (`mapper/screens/home.py:169-181` generic-Exception catch; `mapper/screens/map/screen.py:208-215`). Cond 6: expected-RED declaration at increment-003.md:12 and :48/:64 ("4 authored, expected RED until L2b"); gate transcript contains no FAILED for `test_at_114_csv_refusal_toast_shows_the_reason` → green post-merge |
| Gate transcript hash + tail | ✓ executed | `sha256sum evidence/p4-full-suite-a860a27-2026-10-24.txt` = `00652d2c153988baa173cd3f9f9d96ccdfa4cfb23c5ece0ac136490ca94bd592` — exact match. Line 119: `1 failed, 3575 passed, 24 deselected, 3 xfailed … in 1858.48s`; tail ends `__SUITE_DONE__ rc=1`; line 118 FAILED is exactly `tests/test_reqharness_cache_fastpath.py::test_changed_size_or_mtime_takes_full_path` (B-137) and no other FAILED line exists |
| 04-validation.md internal consistency | ✓ executed | 18/18 Layer A rows pass with method + threshold + result; Layer B rows AT-108…116 each name surface + deliverable + boundary/negative (:120-128); 15-row bidirectional matrix :135-149 has 0 gaps. Citations spot-verified on disk (≥4): p4 transcript hash ✓; `xbatch14-{red,green,mutant}` ✓; `fu-inc004-f1-decode-guard-{red,green,mutant}` ✓; `evidence/review-inc004.md` ✓; `l3-mutation-battery-2026-10-23.txt` ✓. Every ⚠/gap lands in BACKLOG: B-136 (:247), B-137 (:257), B-138 (:258), B-139 (:259) all present in `.dev-flow/BACKLOG.md` |

## Fixture-content re-derivation (open point 1)

Independent sweep: `grep '&[A-Za-z_][A-Za-z0-9_-]*'` over `tests/` (plus `<<:` merge keys — zero hits). Anchor/alias-bearing YAML fixtures in the suite:

1. `tests/test_ingestion_limits.py:106,116,249` — the batch's own AT-111 / diff-side refusal arms; assert the typed refusal; green in the gate run. In-class, covered.
2. `tests/test_repair_sidecar.py:59-62, 346-348, 421-423` — exactly the three `LLR-N13.1.7` arms; amended to assert the prescan refusal (names unchanged, size bounds kept); green in `xbatch14-green`, RED under M-Q2-1-XB14. In-class, covered.
3. `tests/test_reqharness_chain.py:722` + `tests/test_reqharness_config.py:97,102` — anchor fixtures fed to the **reqharness's own loaders** (`verify_chain`, `load_config`), not `MapStore.load`; both already assert refusal ("anchors and aliases are not allowed"). Different component, already in the refused class.
4. `tests/test_office.py:95` — `&amp;` HTML entity, false positive, not YAML.

**Ruling: the fixture-content class is closed.** Every anchor-bearing fixture that reaches `MapStore.load` with post-compose expectations was re-checked; no other consumer of that class exists in the suite. The DDR row-3 ⚠ ("ONE miss found and discharged") is the honest marker — the miss is real and the discharge is evidenced end-to-end (red → amended green → asserting mutant RED, hashes pinned in increment-003:333-335). I endorse the §C-1 sub-question: the C-52 condition-3 census template should mandate the fixture-content pass by template text — that amendment is a flow-authoring decision above this station, recorded here as support, not as a condition.

## Rulings on residual risks (open point 5)

| §E risk | Ruling | One line of evidence |
|---|---|---|
| 1. Prescan +3.54 s on 12,000-node shape | accept | measured, not speculative (`evidence/l2a-prescan-cost-2026-10-23.txt` exists); real maps ≤8 nodes pay ~0; revisit trigger stated |
| 2. Six osopen names vs ARQ "ONE name" | amend | the derived allow-list (`tests/test_arch_osopen_callers.py`) is the binding measured record; the ARQ row's phrasing should be re-worded to it — record fix, not code fix |
| 3. AT-114 fixed `pilot.pause()` cadence | accept | carried as B-139 (BACKLOG.md:259) with the poll-with-deadline remedy named; deliberate mid-batch non-application declared in increment-003:360-361 |
| 4. Gate-run single failure | accept | hash-verified transcript: the one failure is exactly B-137, reproduced 1/6 on master `b5dba72` per BACKLOG.md:257; no batch arm rests on it (P-05) |
| 5. OutlineRenderer dangling-edge crash | accept | B-138 (BACKLOG.md:258); no shipped parser route reaches it (`mermaid.parse` materialises both endpoints); owned by a future batch touching `mapper/views/outline.py` |
| 6. Dim-text audit events deferred | accept | B-136 kept open (BACKLOG.md:247); `put`-path inheritance means a later `dim` kind lands with no interface change (ruling R4) |

## Verdict

**approved** — Every assigned DDR row re-verified against on-disk, hash-pinned evidence: the B1 census miss is discharged with a complete red/green/mutant chain whose sha256 prefixes match the ledger, and my independent fixture-content re-derivation confirms the anchor-bearing class is closed (the only other anchor fixtures feed a different component's loader and already assert refusal). C-18 holds with two honestly-declared exceptions (AT-111, AT-116) that are written into the contract itself, not discovered gaps. The test ledger reconciles at function level (D=0, +31 defs, +2 parametrized items — the full-suite collect itself was not-run under my mandate). The gate transcript hash and tail match exactly, with the single failure being the declared pre-existing flake B-137. The one MINOR finding (ledger `.14` misnaming the mutant's surplus RED arms) is a wording nit that does not touch any verdict.
