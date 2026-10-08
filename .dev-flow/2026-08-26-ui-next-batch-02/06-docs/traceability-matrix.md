# Traceability Matrix — mapper — Batch 2026-08-26-ui-next-batch-02

> Two chains (per the Two-layer validation rule) — a story is complete only when BOTH exist:
> - **Functional (white-box):** User Story → HLR → LLR → `TC-NNN` → File:line.
> - **Behavioral (black-box):** User Story → `AT-NNN` → observed outcome through the shipped surface.
> Every row must be complete when closing the batch (phase 6). Incomplete rows = coverage gaps and must be listed in the gaps section.

> **Counts are derived, not literal** (per `01-requirements.md` §5.2, `QA-B-03` / §6.5 A-07): HLR count = `#### HLR-` headings marked neither `SUPERSEDED` nor `DEFERRED`; LLR count = `##### LLR-` headings marked neither. Retired ids (`SUPERSEDED` S-7 / `DEFERRED` US-N14 / the split parent `LLR-N07.2.2`) are enumerated in §4 and are **not** traced below.

---

## 1. Master table — functional chain (white-box)

> One row per live LLR. `TC`/`AT` ids and `File:line` are cited from `01-requirements.md` §5.2 (functional table) and each LLR's own `Touched symbols` / `Acceptance` lines; `File:line` re-grepped at HEAD (`46e190b`). Superseded S-7 and deferred US-N14 LLRs are excluded and listed in §4.

| US | HLR | LLR | TC | File:line | Status | Notes |
|----|-----|-----|-----|-----------|--------|-------|
| HLR-COERCE | HLR-COERCE | LLR-COERCE.1 | TC-080 | `mapper/darkside.py:517` | pass | `COERCION_RANGES` declared once; `_CONTROL_MAP` covers it |
| HLR-COERCE | HLR-COERCE | LLR-COERCE.2 | TC-081 | `mapper/views/layered.py:124` | pass | `_fit` coerces before truncating (A-89 widened to every renderer) |
| HLR-COERCE | HLR-COERCE | LLR-N06.2.5 | TC-073 | `mapper/darkside.py:550` | pass | notify census; re-parented from `HLR-N06.2` by `#D21` |
| S-6 (paleta v2) | HLR-S06.1 | LLR-S06.1.1 | TC-007 | `mapper/darkside.py:62` | pass | `SAGE`/`TEAL`/`VIOLET` constants + docstring |
| S-6 (paleta v2) | HLR-S06.3 | LLR-S06.3.1 | TC-010 | `tests/test_darkside_census.py` | pass | census input set derived (no mapper symbol) |
| S-6 (paleta v2) | HLR-S06.3 | LLR-S06.3.2 | TC-011 | `tests/test_darkside_census.py` | pass | exception register named and fenced (no mapper symbol) |
| S-6 (paleta v2) | HLR-S06.3 | LLR-S06.3.3 | TC-012 | `mapper/darkside.py` | pass | blue stays interactivity-only |
| S-6 (paleta v2) | HLR-S06.3 | LLR-S06.3.4 | TC-013 | `mapper/darkside.py` | pass | severity stays `WARN`/`ALERT` |
| S-6 (paleta v2) | HLR-S06.3 | LLR-S06.3.5 | TC-072 | `mapper/darkside.py` | pass | one job per token (both `==0` and neither `==0`) |
| HLR-canvas (A3) | HLR-CNV.1 | LLR-CNV.1.1 | TC-015 | `mapper/canvas.py:86` | pass | layers declared, not monkey-patched (`Canvas.__init__`) |
| HLR-canvas (A3) | HLR-CNV.1 | LLR-CNV.1.2 | TC-016 | `mapper/canvas.py:167` | pass | `rows()` composes layers in declared order |
| HLR-canvas (A3) | HLR-CNV.1 | LLR-CNV.1.3 | TC-017 | `mapper/canvas.py:167` | pass | out-of-bounds layer writes dropped |
| HLR-canvas (A3) | HLR-CNV.1 | LLR-CNV.1.4 | TC-079 | `mapper/canvas.py:167` | pass | layer tone is a declared token with fallback |
| HLR-canvas (A3) | HLR-CNV.2 | LLR-CNV.2.1 | TC-019 | `mapper/export.py:30` | pass | `save_svg` on-disk code-point equality |
| HLR-canvas (A3) | HLR-CNV.3 | LLR-CNV.3.1 | TC-021 | `mapper/app.py:1088` | pass | `refresh_canvas` focus-aware tone (B-05) |
| US-N06 (escala) | HLR-N06.1 | LLR-N06.1.1 | TC-024 | `mapper/views/state.py:95` | pass | `ViewState.pan_x`/`pan_y` travel in state |
| US-N06 (escala) | HLR-N06.1 | LLR-N06.1.2 | TC-025 | `mapper/app.py:1750` | pass | `_clamp_pan` bound; legal range on visible canvas (A-109) |
| US-N06 (escala) | HLR-N06.2 | LLR-N06.2.1 | TC-027 | `mapper/views/state.py:101` | pass | `folded` has one owner, two readers |
| US-N06 (escala) | HLR-N06.2 | LLR-N06.2.2 | TC-028 | `mapper/app.py` | pass | folding a leaf paints no pill |
| US-N06 (escala) | HLR-N06.2 | LLR-N06.2.3 | TC-029 | `mapper/darkside.py:550` | pass | hostile branch titles coerced (`plain`) |
| US-N06 (escala) | HLR-N06.2 | LLR-N06.2.4 | TC-071 | `mapper/app.py:3800` | pass | `_walk_hits` opens a hidden fold and announces it |
| US-N06 (escala) | HLR-N06.3 | LLR-N06.3.1 | TC-031 | `mapper/app.py:2083` | pass | `_unpainted_ids` counts two hiding causes as one set |
| US-N06 (escala) | HLR-N06.3 | LLR-N06.3.2 | TC-032 | `mapper/app.py` | pass | pills reconcile with declared total (`anidado` fixture) |
| US-N06 (escala) | HLR-N06.3 | LLR-N06.3.3 | TC-033 | `mapper/views/layered.py:541` | pass | no overflow indicator at zero |
| US-N06 (escala) | HLR-N06.3 | LLR-N06.3.4 | TC-089 | `mapper/views/outline.py:368` | pass | outline declares what the cut hid (AT-056; `_fit_declared`) |
| US-N06 (escala) | HLR-N06.3 | LLR-N06.3.5 | TC-090 | `mapper/app.py:2178` | pass | both surfaces speak, agree, are right (AT-057; `_declare_after_layout`) |
| US-N06 (escala) | HLR-N06.3 | LLR-N06.3.6 | TC-091 | `mapper/app.py:2083` | pass | broken declaration ≠ absent (AT-058; `_unpainted_ids` raises) |
| US-N06 (escala) | HLR-N06.3 | LLR-N06.3.7 | TC-092 | `mapper/views/radial.py:165` | pass | radial declares under its own painted predicate (AT-059; `_paint`) |
| US-N07 (búsqueda) | HLR-N07.1 | LLR-N07.1.1 | TC-035 | `mapper/search.py:95` | pass | inline predicate deleted, deletion asserted (`SearchIndex.query`) |
| US-N07 (búsqueda) | HLR-N07.1 | LLR-N07.1.2 | TC-036 | `mapper/model.py:224` | pass | widened hit definition (`Graph.search_hits`) |
| US-N07 (búsqueda) | HLR-N07.1 | LLR-N07.1.3 | TC-026b | `mapper/views/layered.py:541` | pass | fold pill's hit count re-routed, not deleted |
| US-N07 (búsqueda) | HLR-N07.2 | LLR-N07.2.1 | TC-038 | `mapper/app.py` | pass | count invariant under fold |
| US-N07 (búsqueda) | HLR-N07.2 | LLR-N07.2.2a | TC-039 | `mapper/views/state.py:186` | pass | renderer signature migration `(graph, state)`; `**kwargs` removed |
| US-N07 (búsqueda) | HLR-N07.2 | LLR-N07.2.2b | TC-077 | `mapper/views/outline.py:456` | pass | hit painting in the derived renderer set |
| US-N07 (búsqueda) | HLR-N07.2 | LLR-N07.2.3 | TC-087 | `mapper/views/state.py:175` | pass | `ViewState` frozen; `IRenderer` a `runtime_checkable` Protocol |
| US-N07 (búsqueda) | HLR-N07.3 | LLR-N07.3.1 | TC-041 | `mapper/app.py:3111` | pass | hit order is tree order (`_search_order`) |
| US-N07 (búsqueda) | HLR-N07.3 | LLR-N07.3.2 | TC-042 | `mapper/app.py` | pass | empty result observably distinct (text + tone) |
| US-N07 (búsqueda) | HLR-N07.3 | LLR-N07.3.3 | TC-043 | `mapper/search.py:95` | pass | whitespace-only query is not match-everything |
| US-N07 (búsqueda) | HLR-N07.3 | LLR-N07.3.4 | AT-054, AT-055 | `mapper/app.py` | pass | one regime at every graph size (`#D43`, Inc-4c) |
| US-N13 (sala) | HLR-N13.1 | LLR-N13.1.1 | TC-045 | `mapper/app.py:611` | pass | card built from the loaded graph (`_map_metrics`) |
| US-N13 (sala) | HLR-N13.1 | LLR-N13.1.2 | TC-046 | `mapper/darkside.py:444` | pass | coverage bar reuses `microbar` |
| US-N13 (sala) | HLR-N13.1 | LLR-N13.1.3 | TC-047 | `mapper/app.py` | pass | one definition of coverage % (pinned 100) |
| US-N13 (sala) | HLR-N13.1 | LLR-N13.1.4 | TC-048 | `mapper/app.py:611` | pass | due badge + link marker derived, never invented |
| US-N13 (sala) | HLR-N13.1 | LLR-N13.1.5 | TC-074 | `mapper/app.py` | pass | per-map failure containment; card state is not a lie |
| US-N13 (sala) | HLR-N13.1 | LLR-N13.1.6 | TC-075 | `mapper/app.py:657` | pass | `_sparkline_text`; one load per map per mount (A-105 floor) |
| US-N13 (sala) | HLR-N13.1 | LLR-N13.1.7 | TC-088 | `mapper/store.py` | pass | alias-bomb arm on the traversed `nodes:` sidecar key |
| US-N13 (sala) | HLR-N13.2 | LLR-N13.2.1 | TC-050 | `mapper/darkside.py:550` | pass | hostile map titles coerced (`plain`) |
| US-N16 (leyenda) | HLR-N16.1 | LLR-N16.1.1 | TC-064 | `tests/test_help_scope.py` | pass | screen set derived, never enumerated (no mapper symbol) |
| US-N16 (leyenda) | HLR-N16.1 | LLR-N16.1.2 | TC-065 | `mapper/screens/factory.py:137` | pass | `FactoryScreen.KEY_SCOPE` / `SettingsScreen.KEY_SCOPE` declared |
| US-N16 (leyenda) | HLR-N16.2 | LLR-N16.2.1 | TC-067 | `mapper/darkside.py:739` | pass | one vocabulary declaration (`VIEW_NAMES`) |
| US-N16 (leyenda) | HLR-N16.2 | LLR-N16.2.2 | TC-068 | `mapper/screens/help.py:287` | pass | empty vocabulary omits the section (`HelpScreen`) |
| US-N16 (leyenda) | HLR-N16.2 | LLR-N16.2.3 | TC-069 | `mapper/darkside.py:550` | pass | binding labels reaching the legend coerced (`plain`) |
| repair pair (B-29/B-30) | HLR-REPAIR.1 | LLR-REPAIR.1 | TC-082 | `mapper/store.py` | pass | phantom sidecar id records a load warning (B-29) |
| repair pair (B-29/B-30) | HLR-REPAIR.1 | LLR-REPAIR.2 | TC-083 | `mapper/store.py:680` | pass | not-found message names `map_id`, no path (B-30; `load`) |

## 1b. Behavioral chain (black-box)

> Per user story: the acceptance test that observes the outcome through the shipped surface. AT ids from `01-requirements.md` §5.2 behavioral table; observed outcomes from `04-validation.md` Layer B and `VERDICT-merge-2026-10-03.md`. The superseded S-7 and deferred US-N14 carry no live AT (see §4).

| US | Acceptance test (`AT-NNN`) | Shipped surface | Observed outcome / deliverable | Status |
|----|----------------------------|-----------------|--------------------------------|--------|
| S-6 (paleta v2) | AT-003, AT-004, AT-005, AT-006 | `mapper/darkside.py` + derived hue census | three hues carry declared jobs; blue and severity keep theirs | pass |
| HLR-canvas (A3) | AT-007, AT-007b, AT-008, AT-009, AT-010 | `Canvas.rows()`, `RadialRenderer`, `export.save_svg` on disk | layers reach `rows()`; braille reaches radial output; export read back from disk; selection tone follows focus | pass |
| US-N06 (escala) | AT-011…AT-017, AT-046, AT-047, AT-056, AT-057, AT-058, AT-059 | `#map-canvas`, `#map-pagination`, `#map-rail` | the window moves, branches fold, and what is hidden is declared and reconciles on both surfaces in every declaring view | pass |
| US-N07 (búsqueda) | AT-018…AT-024, AT-051, AT-052, AT-054, AT-055 | `#search-input` and the count region | the count covers the whole map; the walk follows the tree with the real `n`/`N`/`M`; nothing found looks like nothing | pass |
| US-N13 (sala) | AT-025, AT-025b, AT-026, AT-029, AT-030, AT-031 | `#home-recents`, `#home-empty` | each map shows its own shape; an empty workspace shows the door; a damaged map says so on its own card | pass |
| US-N16 (leyenda) | AT-041, AT-042, AT-043, AT-044, AT-053 | `HelpScreen` via the real `question_mark` chord | `?` explains this view, with its real keys and glyphs, on every screen in the derived set | pass |
| repair pair (B-29/B-30) | AT-049, AT-050 | `#home-recents` and the `load_or_notice` toast | a map the store cannot fully parse says so on its own card; a not-found message names the map, not the filesystem | pass |

---

## 2. Coverage summary

| Metric | Value |
|--------|-------|
| Total user stories | 7 |
| Covered user stories | 7 (100%) |
| Total HLR | 21 |
| Implemented HLR | 21 (19 with an on-disk test; HLR-N13.3 and HLR-N16.3 without one — G-2, G-3) |
| Total LLR | 54 |
| Implemented LLR | 54 (100%) |
| Test cases | 75 (53 traced row-level in §1; 22 not traced row-level — G-5) |
| TC pass | 75 |
| TC fail | 0 |
| TC pending | 0 |

> **Derivation (no literal counts — §5.2 / A-07).** 7 derivable live stories (S-6, HLR-canvas, US-N06, US-N07, US-N13, US-N16, repair pair); superseded S-7 and deferred US-N14 excluded. 21 `#### HLR-` headings and 54 live LLRs (58 `##### LLR-` headings marked neither `SUPERSEDED` nor `DEFERRED`, minus the 3 `LLR-S07.1.x` under the superseded `HLR-S07.1`, minus the split parent `LLR-N07.2.2`) (the split parent `LLR-N07.2.2` counted once as its two halves 2a/2b). TC = 88 distinct `TC-NNN` in the §5.2 functional table − 5 struck (TC-001…005) − 13 deferred (TC-051…062, TC-078) + 5 amendment-added (TC-026b, TC-089…092) = **75**. All pass on the one complete gate run: **2797 passed / 0 failed / 3 xfailed** (`gate-run-master-tree.txt`, orchestrator, squash tree `46e190b`).

---

## 3. Detected gaps

> Incomplete rows, requirements without TC, or TCs without code mapping.

| ID | Type | Description | Proposed action |
|----|------|-------------|-----------------|
| G-1 | HLR without LLR | `HLR-S06.2` (256-colour downgrade) has no LLR heading; validated at HLR level by `AT-004` (`tests/test_darkside_census.py:465`) | none — HLR-level validation |
| G-2 | HLR without test | `HLR-N13.3` (unsummarisable map declared on its own card): no LLR, no AT/TC id, no test found by name; its work-budget half was cut to the follow-on design batch (`#D24`, A-43) | B-100: locate or write the node |
| G-3 | AT unrealised | `HLR-N16.3` (doubled help chord reserved) names `AT-044` and `pytest -k doubled_help_chord_is_reserved` *(provisional)*; no such node exists on disk | B-100: realise `AT-044` |
| G-4 | HLR without LLR | `HLR-N16.4` (legend declares its own keys) has no LLR heading; validated by `tests/test_help_scope.py:328` `test_hlr_n16_4_legend_declares_its_own_keys` (the FLAKE-2 test, B-98) | none — HLR-level validation |
| G-5 | TC not traced row-level | 75 TCs counted in §5.2, 53 appear in §1; the other 22 are not mapped to an LLR row here | next batch: map or retire |

> **Not gaps (recorded to forestall a broken-oracle false positive).** (1) `LLR-N07.3.4` carries `AT-054`/`AT-055` (pilot) rather than a `TC-NNN`; both are real on-disk nodes and pass (`04-validation.md`). (2) Three LLRs (`S06.3.1`, `S06.3.2`, `N16.1.1`) are verified by test-module symbols with no `mapper/` symbol — that is the requirement's own shape, not an unmapped row.

---

## 4. Changes from previous batch

| Type | Item | Detail |
|------|------|--------|
| new | 21 HLR + 54 LLR | Derived in Phase 1 from 6 READY stories + palette v2 + HLR-canvas + the repair pair. Amendment sets 1–3 added `HLR-N13.3`, `HLR-N16.4`, `LLR-S06.3.5`, `LLR-N06.2.5`, `LLR-N13.1.5`, `LLR-N13.1.6`, `LLR-N13.1.7` (§5.2 note, A-58, A-72); later Phase-3 rulings added `LLR-N07.1.3` (`#D36`) and `LLR-N07.3.4` (`#D43`) |
| new | 35 amendments A-105…A-139 | Legend dock/pan, repo hygiene, ficha coercion, English chrome, map-id confinement, repo/path allow-lists, attachment chip, English UI, gate fixes. Each carries a named passing node (`04-validation.md` Layer A) |
| retired | `HLR-S07.1`, `LLR-S07.1.1/2/3` | Struck at `d877784` (D16); shipped as `HLR-R04`, guarded by `tests/test_repair_layout.py` |
| deferred | US-N14 (3 HLR + 10 LLR), `AT-032`…`AT-040` (incl. `AT-034b`), `TC-051`…`TC-062`, `TC-078` | Deferred whole to a follow-on design batch (`#D23`) |
| split | `LLR-N07.2.2` | Split into `LLR-N07.2.2a` (Inc-2) / `LLR-N07.2.2b` (Inc-5) per `PDR-… #D12` |

---

## 5. Quick bidirectional mapping

### 5.1 By user story

- **S-6** → HLR-S06.1, HLR-S06.2, HLR-S06.3 → LLR-S06.1.1, LLR-S06.3.1…5 → TC-007, TC-010…013, TC-072 → AT-003…006
- **HLR-canvas** → HLR-CNV.1…3 → LLR-CNV.1.1…4, LLR-CNV.2.1, LLR-CNV.3.1 → TC-015…017, TC-079, TC-019, TC-021 → AT-007, AT-007b, AT-008…010
- **US-N06** → HLR-N06.1…3 → LLR-N06.1.1/2, LLR-N06.2.1…5, LLR-N06.3.1…7 → TC-024/025, TC-027…029, TC-071, TC-073, TC-031…033, TC-089…092 → AT-011…017, AT-046/047, AT-056…059
- **US-N07** → HLR-N07.1…3 → LLR-N07.1.1…3, LLR-N07.2.1/2a/2b/3, LLR-N07.3.1…4 → TC-035/036, TC-026b, TC-038/039/077/087, TC-041…043 → AT-018…024, AT-051/052, AT-054/055
- **US-N13** → HLR-N13.1…3 → LLR-N13.1.1…7, LLR-N13.2.1 → TC-045…048, TC-074/075/088, TC-050 → AT-025, AT-025b, AT-026, AT-029…031
- **US-N16** → HLR-N16.1…4 → LLR-N16.1.1/2, LLR-N16.2.1…3 → TC-064/065, TC-067…069 → AT-041…044, AT-053
- **repair pair** → HLR-REPAIR.1 → LLR-REPAIR.1/2 → TC-082/083 → AT-049/050
- **HLR-COERCE (cross-cutting)** → HLR-COERCE → LLR-COERCE.1/2, LLR-N06.2.5 → TC-080/081, TC-073

### 5.2 By code file

- `mapper/darkside.py` — LLR-COERCE.1, LLR-N06.2.5, LLR-S06.1.1, LLR-N06.2.3, LLR-N13.2.1, LLR-N16.2.3, LLR-N16.2.1 (coercion, palette tokens, `microbar`, `VIEW_NAMES`)
- `mapper/canvas.py` — LLR-CNV.1.1…4
- `mapper/export.py` — LLR-CNV.2.1
- `mapper/app.py` — LLR-CNV.3.1, LLR-N06.1.2, LLR-N06.2.2/4, LLR-N06.3.1/2/5/6, LLR-N07.2.1, LLR-N07.3.2/4, LLR-N13.1.1/3/4/5/6
- `mapper/views/state.py` — LLR-N06.1.1, LLR-N06.2.1, LLR-N07.2.2a/3
- `mapper/views/layered.py` — LLR-COERCE.2, LLR-N06.3.3, LLR-N07.1.3
- `mapper/views/outline.py` — LLR-N06.3.4, LLR-N07.2.2b
- `mapper/views/radial.py` — LLR-N06.3.7
- `mapper/search.py` — LLR-N07.1.1, LLR-N07.3.1/3
- `mapper/model.py` — LLR-N07.1.2
- `mapper/store.py` — LLR-N13.1.7, LLR-REPAIR.1/2
- `mapper/screens/factory.py`, `mapper/screens/settings.py`, `mapper/screens/help.py` — LLR-N16.1.2, LLR-N16.2.2

---

## 6. Batch sign-off

| Field | Value |
|-------|-------|
| Batch ID | `2026-08-26-ui-next-batch-02` |
| Closing date | `2026-10-03` |
| Total iterations (sum of phases) | 7 (`state.json` `iterations_per_station`: P0=2, ARQ=1, P1=1, PDR=3; P3 tracked as increments `increment-001`…`increment-057` under `03-increments/`, not in that field) |
| Validation passed | yes (`PASS-WITH-NOTES`, `04-validation.md`) |
| Synced to Obsidian | no |

---

*Gap rows G-1…G-5 added by the orchestrator after a `qa-reviewer` pass found the draft's "None at close" untrue. Drafted by `deepseek/deepseek-v4-pro` (via `opencode run`), to be verified by the orchestrator. All ids and counts derived by grepping `01-requirements.md` (§5.2); every `File:line` re-grepped at HEAD `46e190b`. Nothing was re-run for this artifact; the single gate run cited is the orchestrator's (`gate-run-master-tree.txt`).*
