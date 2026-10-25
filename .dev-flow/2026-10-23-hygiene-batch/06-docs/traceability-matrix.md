# Traceability Matrix — mapper — Batch 2026-10-23-hygiene-batch

> **Artifact language:** canonical English scaffold. Generate the artifact in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label**. This document mints no field a rule keys on — its ids (`US-`/`HLR-`/`LLR-`/`AT-`/`TC-`/`R-`) are read by the Atlas id-scanner and are not words in any language — so it carries no reserved-field block; what it must not do is order the translation of somebody else's.

> **Owed in.** `core` — · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-level table, which is this fact's one home. A level marked `—` **does not owe this artifact, and its absence is not an omission**; `by trigger` means the station exists only when the `triggers` block fired, and `stations_active` in `state.json` is the authority for *this* batch. Where a SECTION or a gate row is owed more narrowly than the artifact, it says so on the row. ⚠ **This template is seeded by a BULLET under that table rather than by a row**, because `06-docs/` exists only in `full` — the same fact `V39`'s `_V39_OWED_IN["P6"]` carries.

> Two chains (per the Two-layer validation rule) — a story is complete only when BOTH exist:
> - **Functional (white-box):** User Story → HLR → LLR → `TC-NNN` → File:line.
> - **Behavioral (black-box):** User Story → `AT-NNN` → observed outcome through the shipped surface.
> Every row must be complete when closing the batch (phase 6). Incomplete rows = coverage gaps and must be listed in the gaps section.

---

## 1. Master table — functional chain (white-box)

| US | HLR | LLR | TC | File:line | Status | Notes |
|----|-----|-----|-----|-----------|--------|-------|
| US-Q1-001 | HLR-Q1.1 | LLR-Q1.1.1 | `test_no_color_removed_before_super` | `mapper/app.py:254` | pass | unit arm; mutant M-Q1-1; black-box sibling below |
| US-Q2-001 | HLR-Q2.1 | LLR-Q2.1.1 | `test_at_109_byte_cap_stat_refuses_and_names_limit_and_map` · `test_at_109_byte_cap_grow_between_stat_and_read_refuses` · `test_at_109_text_map_at_byte_cap_minus_1_loads` | `mapper/store.py` (capped read + re-check; byte re-check per LLR-Q2.1.1) | pass | mutant M-Q2-2; stat limb is the fast path (inc003-F3 wording) |
| US-Q2-001 | HLR-Q2.1 | LLR-Q2.1.2 | `test_at_111_anchor_refused_names_anchor_and_map` · `test_at_111_alias_refused` · `test_at_111_anchor_name_in_refusal_is_bounded` · `test_at_110_depth_64_parses` · `test_at_110_depth_65_refuses_naming_depth_limit` · `test_at_110_deep_10000_refuses_fast_without_recursion_error` | `mapper/store.py:712` (`_prescan_sidecar`) | pass | mutants M-Q2-1 / M-Q2-1-XB14; anchor-name bound `ANCHOR_NAME_DISPLAY = 40` (inc003-F1) |
| US-Q2-001 | HLR-Q2.1 | LLR-Q2.1.3 | `test_at_112_node_count_cap_plus_1_refuses` · `test_at_113_edge_count_cap_plus_1_refuses` · `test_count_caps_exactly_at_cap_pass` | `mapper/store.py:91-93` (count caps) | pass | caps 100,000/100,000 (ruling R1, re-derived ledger `.5`); mutant M-Q2-4 |
| US-Q2-001 | HLR-Q2.1 | LLR-Q2.1.2 (diff-side, via the store edge) | `test_diff_side_oversize_head_yields_none` · `test_diff_side_anchor_head_yields_none` · `test_diff_side_clean_head_still_diffs` · `test_git_diff_undecodable_head_object_returns_none_quietly` | `mapper/diff.py:33` (`_show`, bounded capture — S1 BOUND) | pass | `None`-on-error contract survives the shared caps (inc004-F1) |
| US-Q2-001 | HLR-Q2.2 | LLR-Q2.2.1 | `test_csv_at_file_cap_plus_1_refuses` · `test_csv_at_file_cap_minus_1_loads` · `test_csv_nul_at_byte_0_refuses_as_binary` · `test_csv_nul_at_last_probe_byte_refuses_as_binary` · `test_csv_nul_past_probe_window_is_not_refused_by_the_probe` · `test_csv_non_utf8_refuses_typed_naming_the_reason` | `mapper/osopen.py:110` (`read_capped`) consumed at `mapper/import_csv.py:47` | pass | mutants M-Q2-3 / inc004-F2; typed `ContentReadError` (R-015 family note, increment-003 §6) |
| US-Q2-001 | HLR-Q2.3 | LLR-Q2.3.1 | census record + existing refusal suite | `design/design-proposal.md` §5 census; `mapper/store.py:28-31` · `mapper/osopen.py:104-107` | pass | inspection method; pins: `tests/test_seed_safety.py` `BAD_NAMES` · `tests/test_inc9n.py` `DEVICES` |
| US-Q3-001 | HLR-Q3.1 | LLR-Q3.1.1 | `test_renderer_roster_derived` | `tests/test_scalecheck.py:68` (roster from `mapper/views.__all__`) | pass | completeness guard — no vacuous pass |
| US-Q3-001 | HLR-Q3.1 | LLR-Q3.1.2 | `test_sweep` | `mapper/views/*` renderers (sweep only — no renderer byte changed; ruling R10 corrected the oracle, ledger `.11`) | pass | 6 × 5 × 4 = 120 per `design/state-matrix.md`; mutant M-Q3-1 |
| US-Q3-001 | HLR-Q3.2 | LLR-Q3.2.1 | `test_events` (+ `test_text_and_wire_paths_share_put_and_default_sink_is_none`) | `mapper/canvas.py:97-129` (`audit=None` param; `put` records clip/overprint) | pass | mutants M-Q3-2 (event set) / M-Q3-4 (alphanumeric gate, second limb) |
| US-Q3-001 | HLR-Q3.2 | LLR-Q3.2.2 | `test_byte_identity` + unchanged digest/golden suites | `mapper/canvas.py` (observational hook) | pass | mutant M-Q3-3; `test_repair_depth.py` digests · `test_perf_paint_clip.py` goldens · B-44 pin all green in the gate run |
| US-Q3-001 | HLR-Q3.2 | LLR-Q3.2.3 | `test_sweep_audit_arm` | `mapper/canvas.py` construction sites (`mapper/views/layered.py` · `radial.py` · `lane.py` ×1 each) | pass | per-renderer construction census (ledger `.12`/`.13`); sweep-arm negative control = the M-Q3-1 class |

## 1b. Behavioral chain (black-box)

> Per user story: the acceptance test that observes the outcome through the shipped surface. A story with a complete functional chain but no behavioral row is INCOMPLETE.

| US | Acceptance test (`AT-NNN`) | Shipped surface | Observed outcome / deliverable | Status |
|----|----------------------------|-----------------|--------------------------------|--------|
| US-Q1-001 | AT-108 | the running app (`MapperApp` headless via `run_test()`) | painted screens byte-equal with vs. without `NO_COLOR=1`; 0 desaturated segments | pass |
| US-Q2-001 | AT-109 · AT-110 · AT-111 · AT-112 · AT-113 | `MapStore.load` → the app's refusal toasts | a typed refusal naming the limit (bytes / depth / anchor+map / nodes / edges); the session continues | pass |
| US-Q2-001 | AT-114 | the home screen's CSV-import toast (`mapper/screens/home.py:524-541`) | the toast shows the authored refusal reason (`str(e)`, path-free per C6); the generic `OSError` branch keeps `type(e).__name__` (ruling R7) | pass |
| US-Q3-001 | AT-115 | the shipped renderer roster (`mapper.views`), as screens and export consume it | the 120-combo sweep fits the geometry budget; a misfit names renderer+size+state | pass |
| US-Q3-001 | AT-116 | `Canvas` as consumed by the renderers (+ unit write corpus) | injected clip/overprint defects recorded with `(x, y)`; `rows()` byte-identical with vs. without the sink | pass |

---

## 2. Coverage summary

| Metric | Value |
|--------|-------|
| Total user stories | 3 |
| Covered user stories | 3 (100%) |
| Total HLR | 6 |
| Implemented HLR | 6 (100%) |
| Total LLR | 12 |
| Implemented LLR | 12 (100%) |
| Test cases | 36 (33 new collected items + the 3 amended cross-batch arms; counted on disk, not by hand — P-18) |
| TC pass | 36 |
| TC fail | 0 batch arms (1 pre-existing flake outside the contract — B-137) |
| TC pending | 0 |

---

## 3. Detected gaps

> Incomplete rows, requirements without TC, or TCs without code mapping.

| ID | Type | Description | Proposed action |
|----|------|-------------|-----------------|
| G-001 | flake (pre-existing) | `tests/test_reqharness_cache_fastpath.py::test_changed_size_or_mtime_takes_full_path` flaked once in the gate run; reproduced 1/6 on master `b5dba72`; untouched by this batch | BACKLOG B-137 — investigate order/load dependence |
| G-002 | crash (pre-existing, derivation-found) | dangling-edge graphs crash `OutlineRenderer` (`mapper/views/outline.py:214-218`, KeyError) | BACKLOG B-138 — refusal vs. tolerance, in a batch owning `mapper/views/outline.py` |
| G-003 | transient flakes (environment) | inc003-F4 (AT-114 screen arm) / inc004-F3 (`test_at_113_edge_count_cap_plus_1_refuses`, `test_at_110_depth_64_parses`) failed once each under review runs, unreproduced with zero source change | BACKLOG B-139 — poll-with-deadline robustness for the AT-114 arm; re-derive only on recurrence |
| G-004 | scope deferral (ruled) | dim-text audit events out of the v1 event set | BACKLOG B-136 (open, ruled R4) |

---

## 4. Changes from previous batch

| Type | Item | Detail |
|------|------|--------|
| new | US-Q1-001 / HLR-Q1.1 / LLR-Q1.1.1 | colour always on under `NO_COLOR` (Q1, lane L1) |
| new | US-Q2-001 / HLR-Q2.1…Q2.3 / LLR-Q2.1.1…Q2.3.1 | ingestion limits: byte cap, prescan (anchors/aliases/depth), count caps, bounded content read, device-name census (Q2, lanes L2a/L2b) |
| new | US-Q3-001 / HLR-Q3.1…Q3.2 / LLR-Q3.1.1…Q3.2.3 | scalecheck sweep + Canvas audit hook (Q3, lane L3; D1 froze the new constructor signature) |
| new | AT-108…AT-116 | one acceptance test per story branch (AT-111 realized as two lowercase-named nodes — see 04-validation.md Layer B) |
| modified | sealed-batch arms (3) | `tests/test_repair_sidecar.py` `LLR-N13.1.7` arms amended to the typed prescan refusal — ruling R10, ledger `LED-2026-10-23-hygiene-batch.14`; owning batch sealed, not edited |
| modified | pin amendments (same-landing) | `tests/test_a3_census.py:658-674` B-44 pin (L3) · `tests/test_arch_osopen_callers.py` allow-list (L2a) |
| amended | LLR-Q2.1.3 · LLR-Q3.1.2 · LLR-Q3.2.1 · LLR-Q3.2.3 | ledger `.1`/`.5` (caps + re-measurement) · `.7` (state matrix bound) · `.8`/`.10` (overprint second limb + M-Q3-4) · `.11`-`.13` (R10 measured-truth corrections) |
| closed | G-rows of this batch | none open at P4 — all gaps dispositioned to BACKLOG (B-136 kept; B-137…B-139 added at P4) |

---

## 5. Quick bidirectional mapping

### 5.1 By user story
- **US-Q1-001** → HLR-Q1.1 → LLR-Q1.1.1 → `test_no_color_removed_before_super` (+ AT-108 black-box arm) → TC: `tests/test_colour_always_on.py` · AT-108
- **US-Q2-001** → HLR-Q2.1, HLR-Q2.2, HLR-Q2.3 → LLR-Q2.1.1, LLR-Q2.1.2, LLR-Q2.1.3, LLR-Q2.2.1, LLR-Q2.3.1 → TC: `tests/test_ingestion_limits.py`, `tests/test_diff.py` · AT-109…AT-114
- **US-Q3-001** → HLR-Q3.1, HLR-Q3.2 → LLR-Q3.1.1, LLR-Q3.1.2, LLR-Q3.2.1, LLR-Q3.2.2, LLR-Q3.2.3 → TC: `tests/test_scalecheck.py`, `tests/test_canvas_audit.py` · AT-115, AT-116

### 5.2 By code file
- `mapper/app.py` → LLR-Q1.1.1 → TC: `tests/test_colour_always_on.py` · AT-108
- `mapper/store.py` → LLR-Q2.1.1, LLR-Q2.1.2, LLR-Q2.1.3 → TC: `tests/test_ingestion_limits.py` load arms · AT-109…AT-113
- `mapper/diff.py` → LLR-Q2.1.2 (diff-side) → TC: `test_diff_side_*`, `test_git_diff_undecodable_head_object_returns_none_quietly`
- `mapper/osopen.py` → LLR-Q2.2.1 → TC: `test_csv_*` · AT-114 (with `mapper/import_csv.py` + `mapper/screens/home.py`)
- `mapper/canvas.py` → LLR-Q3.2.1, LLR-Q3.2.2, LLR-Q3.2.3 → TC: `tests/test_canvas_audit.py`, `test_sweep_audit_arm` · AT-116
- `mapper/views/*` (swept, unchanged) → LLR-Q3.1.2 → TC: `tests/test_scalecheck.py::test_sweep` · AT-115

---

## 6. Batch sign-off

| Field | Value |
|-------|-------|
| Batch ID | `2026-10-23-hygiene-batch` |
| Closing date | 2026-10-24 — DDR sealed `approved with conditions` (reviewer swarm evidence `evidence/ddr-{architect,software-dev,qa}.md`); P5 post-mortem and P6 docs written this unit; state at P6 `awaiting-sync` |
| Total iterations (sum of phases) | recorded 0 per station (`state.json iterations_per_station`); the postmortem's counter-honesty finding notes P1's repaired first-pass BLOCKs and P2's formal `iterate-to-refine` pass are uncounted |
| Validation passed | yes — PASS-WITH-NOTES (04-validation.md; the single gate failure is the pre-existing flake B-137; two DDR conditions C1/C2 remain record work owed at the trunk join) |
| Synced to Obsidian | no — awaiting-sync; `/dev-flow-sync` after the trunk join/merge |
