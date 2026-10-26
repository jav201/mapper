# Increment 002 — HLR-RVH.3/.4/.5 · the screen host + keymap seat (trunk)

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `002` |
| Lane (if the batch forked) | trunk · `screens/relmap` (host + base) + `keymap` (the seat scope — ARC-02, trunk-owned) |
| Requirement(s) | `HLR-RVH.3.2/.4` · `LLR-RVH.3.3, 4.1–4.3, 5.1/.5.2` · sink LLRs `RVM.4.2/RVG.3.1/RVS.5.1` (host half) — PDR `D1` (host↔renderer surface, COND-ARCH-1) and `D3` (`SCOPE_RELMAP`), both frozen here |
| Acceptance | `AT-148` host arms (view switching chrome, derive count 1→2, leave pair, hostile descriptor, out-of-view inert) · white-box `TC` via `tests/test_relmap_shell.py` · seat pins `tests/test_keymap.py` (extended) + `tests/test_key_dispatch.py` (whole-seat pin, re-run per COND-QA-2) |
| Agent | `software-dev` (trunk; orchestrator self-executed) |
| Date | `2026-10-25` |

---

## 1 · What changed

BLUF: the relation screen host is real. `RelMapScreen` (`mapper/screens/relmap/screen.py`)
hosts the three views over the D1 surface frozen at the R2 PDR: it derives the map
on open and re-derives on `r` through `derive_reqharness_map` (derive count 1 at
open, 2 after `r`, the counter WRAPPING the real function per COND-QA-4), renders
the seat-derived chrome (crumb `name / relmap / view`, keybar, notice) with every
file-derived label through the one `_row_text`/`fit` sink (COND-SEC-1), refuses a
bad descriptor or canon with the fixed `refusal_line` and stays alive (K1–K17
closed set, never `str(exc)`), and leaves on `q`/`escape`. The additive
`SCOPE_RELMAP` seat — 13 bindings, no chord twice, no `KeyBinding` moved — gates
`BINDINGS` before the lanes fork (ARC-02). `1`/`2`/`3` switch views; the
view-specific chords `enter`/`c`/`k` are inert no-ops off their home view
(COND-UX-1 — the exported frame is byte-identical and the active renderer's
`toggle` is never called). The D1 surface as built (frozen names):
`base.ViewState(relmap, notice, focus, cursor, lens, gaps, width, height)`,
`RelMapView.paint(state) -> list[Text]`, `RelMapView.toggle(kind: str) -> str`
(the one toggle-state channel, COND-ARCH-1), and the wiring convention
`build_view(name) -> RelMapView` with the absent-module `PendingView` placeholder
— lanes 3/4/5 land `matrix.py`/`gaps.py`/`sheet.py` against exactly these names,
with no host edit (fork precondition F-3).

AT-148's renderer-content arms (matrix/gaps/sheet bodies, the LF/TAB one-row arm
through a real renderer) execute at the lane gates and the join per COND-SEC-1's
discharge note; this increment ships the host arms and the unit sink arm.

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/relmap/__init__.py` | source | HLR-RVH.4 · LLR-RVH.4.2 | NEW — the package re-export (`RelMapScreen`), the `MapScreen` pattern |
| `mapper/screens/relmap/screen.py` | source | LLR-RVH.3.2/.3.3, 4.1–4.3, 5.1 | NEW — the host: lifecycle, derive-on-open + `r`, view switching, seat-derived chrome, cursor selection, the refusal path, the out-of-view inert rule |
| `mapper/screens/relmap/base.py` | source | LLR-RVH.5.2 · sink LLRs · COND-ARCH-1/COND-SEC-1 | NEW — the frozen D1 surface (`ViewState`, `RelMapView`, `build_view`, `PendingView`) + the one label sink (`label` through `darkside._row_text`/`fit`) |
| `mapper/keymap.py` | source | LLR-RVH.4.1 | `SCOPE_RELMAP` + 6 groups (`rview`/`rnav`/`rlens`/`rchain`/`rkind`/`rleave`) + 13 bindings — additive, no existing row moves |
| `tests/test_relmap_shell.py` | test | LLR-RVH.3.2/.3.3, 4.1–4.3, 5.1/.5.2 | NEW — 15 host arms (seat-generated BINDINGS, keybar construction, derive count + args, non-git arm, refusal + app-lives, crumb per switch, out-of-view inert ×4, sink unit + hostile name, leave pair, D1 surface pin, fixture positive control) |
| `tests/test_keymap.py` | test | LLR-RVH.4.1/.4.2 | `RelMapScreen` into `SCOPE_OWNER`; `SCOPE_RELMAP: 13` into `EXPECTED_PER_SCOPE`; `←`/`→` glyphs into the display-form map |
| `tests/test_key_dispatch.py` | test | LLR-RVH.4.1 | the 13 `relmap` rows into `EXPECTED_SEAT` (the whole-seat pin does NOT move — set equality grew, per COND-QA-2's re-run) |
| `tests/test_fold.py` | test | LLR-N06.2.1 (census collision) | `superseded_sites` allows the D1-frozen `.toggle(` entry name under `screens/relmap/` + the host arms file; the instrument and its positive control are unchanged |
| `tests/test_relmap_isolation.py` | test | HLR-RVH.4 (ARQ census) | the importers census skips the sanctioned consumer package `screens/relmap/` (the R2 ARQ §3 row) |
| `tests/test_relmap_descriptor.py` | test | HLR-RVH.5 (hygiene census) | `mine` gains `test_relmap_shell.py` (the hostile-descriptor arm seeds one `*.relmap.yml`, the documented new-suite exception) |
| `tests/test_repair_artifact_claims.py` | test | HLR-RVH.5 (citation census) | one `_CITATION_EXCEPTIONS` row: `layered.py`'s `screen.py` citation now resolves to `mapper/screens/map/screen.py` (bare basename became ambiguous) |
| `tests/test_inc9.py` | test | LLR-N16.1.1 | `OPENERS` gains `RelMapScreen` (opens on the canon-less fixture workspace — the named `unavailable` state) |
| `docs/ARCHITECTURE.md` | doc | — | the `relmap screen` row and the two §4 freeze rows become facts (paths + landed names); D1/D3 freeze text unchanged in substance |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc2-*.txt` | generated | US-RMV-004 | RED ×2, GREEN ×2, mutants — redacted, hashed |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** |
| Test files | 8 (1 new + 7 census/pin repairs; uncapped) |
| Doc files | 1 (outside the count) |

⚠ At exactly 4 source files: the increment cannot be cut smaller — the design
(§2.1, ARC-02) fixes these four as one landing: the host is unbuildable without
the seat (`BINDINGS` derives from it), the package `__init__` is the re-export
pattern, and `base.py` IS the D1 surface the freeze seals.

## 3 · How to test

```bash
PYTHONPATH=<worktree> python -c "import mapper; print(mapper.__file__)"
# targeted (host arms + the two seat pins, COND-QA-2's re-run included):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_relmap_shell.py tests/test_keymap.py tests/test_key_dispatch.py
# the guard set (as the commission lists it + the proposal-named help census):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_fold.py tests/test_repair_artifact_claims.py tests/test_no_operator_paths.py \
  tests/test_mod_bodies.py tests/test_mod_census.py tests/test_mod_compat.py tests/test_mod_deps.py \
  tests/test_mod_dispatch.py tests/test_mod_parity.py tests/test_mod_structure.py \
  tests/test_repair_map_truth.py tests/test_a3_census.py tests/test_arch_osopen_callers.py \
  tests/test_relmap_adapter.py tests/test_relmap_audit.py tests/test_relmap_descriptor.py \
  tests/test_relmap_gaps.py tests/test_relmap_isolation.py tests/test_relmap_model.py \
  tests/test_relmap_profile.py tests/test_relmap_text.py tests/test_relmap_shell.py \
  tests/test_keymap.py tests/test_key_dispatch.py tests/test_inc9c.py tests/test_help_scope.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `full` | `label` sink arm (coerce-before-cut, one row, literal payload) + `test_d1_surface_names_are_frozen` + the fixture positive control | passed (in the 188) |
| **A · white-box** `TC` ↔ LLR | `full` | `tests/test_relmap_shell.py` — 15 nodes incl. derive-count (1→2), derive-args, BINDINGS==seat, keybar construction, crumb per switch, out-of-view inert ×4, refusal closed-set + app-lives | 188 passed targeted (with both seat pins) |
| **B · black-box** `AT` ↔ story | `full` | AT-148 host arms through `run_test()` real keys (C-16): open → `2`/`3`/`1` chrome asserts → `r` derive count → `escape`/`q` → Home; 87-col class covered by the byte-identity frames at (118, 34) + the seat/keybar chrome | passed (host arms); renderer-content arms at the lanes/join per COND-SEC-1 |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (1) code-absent: the whole package + the seat scope do not exist — all three test files fail at import/collection; (2) move-aside (C-20): each of the three net-new source files renamed out of the tree in turn |
| Instrument | project code, orchestrator's hand (no stash; C-20 move-aside) |
| Where it ran | this worktree, orchestrator (no other session reading — the battery and the runs were serialized) |
| Transcript | `evidence/p3-inc2-red-code-absent.txt` — exit 2, 2 collection errors (`No module named 'mapper.screens.relmap'`), wall 1.7s; `evidence/p3-inc2-red-move-aside.txt` — `__init__`/`base`/`screen` each exit 2 at collection |
| Restore proven by | move-aside restore sha256 MATCH ×3 (printed per arm in the transcript); the code-absent state needed no restore |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` in every run (C-46) |
| Arms resolved at baseline | 4 RED arms (1 code-absent + 3 move-aside), each seen failing |
| Verdict granularity | per arm; collection errors are the expected failure shape for import-level absence |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | code-absent + 3 move-aside arms, transcripts at `evidence/p3-inc2-red-code-absent.txt` (sha256 `5966906b…0a3d6`) and `evidence/p3-inc2-red-move-aside.txt` (sha256 `cd3662bd…7250`) |

| Field | Value |
|---|---|
| **Mutation verdicts** | 11/11 KILLED, per arm, restore sha256 proven for every file: M-RVH-8 (`r` serves the cache → derive-count RED) · M-RVH-9 (chord `1` twice → `duplicate_chords` RED) · M-RVH-10 (hand-added BINDINGS rows → seat-equality RED) · M-RVH-11 (swap without the crumb → crumb assert RED) · M-RVH-13 (`str(exc)` as the notice → fixed-line census RED) · M-RVH-14 (refusal re-raises → app-lives RED) · M-RVH-15 (markup-parsing sink → literal-payload arm RED) · M-RVH-16 (derivation consults `.git` → non-git arm RED) · M-RVH-17 (refusal handler deleted → raw escape RED) · M-RVH-18 (bare `plain` sink → LF/TAB arm RED) · M-RVH-19 (chord acts off-home → toggle-spy arm RED, 3 params) · arms that stayed GREEN: none · transcript `evidence/p3-inc2-mutants.txt` (sha256 `5a30b039…286d7`), runner exit 0 |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` | the code-absent + move-aside states | exit 2 collection errors, transcripts |
| the derive counter | `action_refresh` serving the cache (M-RVH-8) | `assert len(calls) == 2` — printed in the battery transcript |
| the toggle spy | the off-home guard removed (M-RVH-19) | `` `c` reached the gaps renderer's toggle off its home view `` — 3 params |
| the mutation runner | its own `BAD` control (anchor ×0 in the first pass) | reported `M-RVH-13: BAD` and exited non-zero; anchor repaired, battery re-run clean |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the composited screen frame (crumb/keybar/canvas) | `painted_frame` — `screen._compositor.render_strips()` serialized as (text, style) runs; byte-compared across off-home chords and against the AT-146 chrome asserts | frames byte-identical after each off-home chord; crumb names `matrix`/`gaps`/`sheet` per switch |
| the keybar line | the painted 118-col bar starts `view 1 matrix  2 gaps  3 sheet  r refresh …` and ends with the declared `… +7 ? all keys` truncation | asserted in `test_llr_rvh_4_2_keybar_groups_read_the_seat` |
| the refusal notice | the painted frame contains the fixed line + the K3 cause, and never `CanonUnavailable`, `RepoReadError` or the workspace path | asserted in `test_llr_rvh_5_1_missing_canon_refuses_without_crashing` |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted on its emitted bytes |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED code-absent transcript | `…/evidence/p3-inc2-red-code-absent.txt` | `55cc4eed45d8e20a97dc5df782ce0defcacd234361f7ed8df71025efac975f66` |
| RED move-aside transcript | `…/evidence/p3-inc2-red-move-aside.txt` | `49859464bf89d173c2627ea182cb77435cd86c7a9317b4d9274c4e34aebd8b4e` |
| GREEN targeted transcript | `…/evidence/p3-inc2-green-targeted.txt` | `0624a2fd9fbb76bcbc0258b03d7475b4633a049e0f3d3cb586037bdaf23597ed` |
| GREEN guard transcript | `…/evidence/p3-inc2-green-guards.txt` | `5fc7374ab4042b12d615e7912ab7509c5e934a740bb5008d2d56cca522c7c98c` |
| mutation battery transcript | `…/evidence/p3-inc2-mutants.txt` | `5a30b039c35f7e3976e67ade7f8b6b217bd29bf13deaece7ff19d2751f3286d7` |

All transcripts redacted (account name → `<user>`) before hashing; exit codes and wall time in each header.

| Field | Value |
|---|---|
| **Evidence files** | 5 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — (a) no renderer module beside the placeholder (the D1 wiring is exercised against absence), (b) the seat's chord uniqueness |
| If the result is an ABSENCE, what made the search wide enough | (a) `build_view` imports `mapper.screens.relmap.<name>` and only `ModuleNotFoundError` with `exc.name == module_name` falls back — a landed lane's module is a real import; (b) `duplicate_chords()` quantifies over the whole seat, derived at runtime |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_d1_surface_names_are_frozen` pins the surface NAMES (a contract census); `test_no_duplicate_chord_inside_one_scope` pins a conclusion about the seat |
| Conjunctive criteria: one mutation per conjunct | M-RVH-15 kills the markup-parse conjunct, M-RVH-18 the LF/TAB conjunct of the sink; M-RVH-13/14 the two refusal conjuncts (wording / app-lives); M-RVH-16/17 the two workspace-as-repo conjuncts (no `.git` / closed-set cause) |
| Synthetic instance of the absent case | the hostile descriptor name + the LF/TAB payload arms ARE the synthetic hostile instances; M-RVH-19's spy is the synthetic off-home call |
| **Positive control for every probe that returned an ABSENCE** | the fixture positive control derives the seeded 3-node map through the real adapter (`test_fixture_canon_derives_honest_skeleton`); the missing-canon arm IS the known-present refusal case for the closed-set census; `test_duplicate_chords_actually_detects_a_duplicate` (carried) drives a synthetic collision through the same detector |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rln RelMapScreen tests/ mapper/` | `tests/test_inc9.py` (OPENERS derivation), `tests/test_keymap.py` (SCOPE_OWNER), `tests/test_relmap_shell.py` — all trunk files of this batch; `mapper/app.py` does NOT import the screen yet (Inc-6's re-export, by design) |
| B2 file moved on disk | `git log --oneline -- mapper/screens/relmap/` | net-new package — no old path exists; not fired |
| B3 byte-identical golden captures this source | `grep -rln relmap tests/goldens/` | no hits — not fired |
| B4 artifact produced here is consumed elsewhere | `grep -rln "SCOPE_RELMAP\|screens.relmap" mapper/ tests/` | the seat's consumers are the package itself + the seat/keybar readers (help/palette derive from it at 6b); zero consumers outside the expected set — the A3 row below stayed inside the owner |
| A3 interface consumed by another module changed | `grep -rn "build_view\|ViewState\|PendingView" mapper/ tests/` outside `screens/relmap/` | the only `ViewState` hits are the tree kind's pre-existing `mapper.views.state.ViewState` — a different symbol in a different module, untouched; the relmap `base.ViewState` has no external consumer yet (the lanes will import it — the freeze is what they read) |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3); B2/B3 not fired; A3 clean (name collision with the tree `ViewState` noted, different module) |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the derived help-screen census (`HELP_SCREENS`/`OPENERS`) | every `Screen` subclass whose merged bindings carry the help chord | `test_inc9.py::_help_screens(PRODUCT_MODULES)` — derived at import; the failure named `RelMapScreen` | 1 | `tests/test_inc9.py` OPENERS +1 row | none — the set equality (`test_every_derived_help_screen_has_an_opener`) enumerates the whole population |
| the fold-state supersession census (`.toggle(` calls) | every `.toggle(...)` attribute call under `mapper/**` + `tests/**` | `test_fold.py::superseded_sites` — AST census; the failure named `mapper/screens/relmap/screen.py:283` + the host arms | 2 files | `tests/test_fold.py` — a scoped allowance for the D1-frozen entry name | none — the allowance names exactly the frozen surface and its host arms; the instrument's positive control (`test_tc_032_the_supersession_instrument_can_see_a_reference`) re-runs unchanged |
| the `.relmap.yml` content census | every `tests/**` file spelling the descriptor suffix | `tests/test_relmap_descriptor.py` — content census; the failure named `test_relmap_shell.py` | 1 | `mine` +1 | none |
| the relmap-importers census | every non-`relmap/` module importing `mapper.relmap` | `tests/test_relmap_isolation.py::test_only_app_and_the_package_import_relmap` — AST census; the failure named the two new modules | 2 files | one skip clause for the ARQ-sanctioned consumer package | none — `app.py` remains the only other importer |
| the path:line citation table | every `file.py:NNN` citation in the corpus | `tests/test_repair_artifact_claims.py::test_every_path_line_citation_resolves` — the failure named `layered.py`'s `screen.py` citation | 1 | one `_CITATION_EXCEPTIONS` row | none — the companion `test_every_declared_citation_exception_is_still_needed` fences the table |

| Field | Value |
|---|---|
| **Correction population** | 5 corrections, each enumerated by its own failing census before its first site was edited (the guard run named every population member; no site was edited ahead of enumeration) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| the fold-state `.toggle(` | `grep -rn "\.toggle(" mapper/ tests/ --include="*.py"` → 3 hits, all inside the D1-frozen surface (`mapper/screens/relmap/screen.py:283`, the host arms, the doc line) | yes — the allowance names exactly those files; every other file is clean by the unchanged AST census | `tests/test_fold.py` `superseded_sites` |

### Signed-balance test ledger

`post = base − deleted + added`: targeted trio `188 = 180 − 0 + 8` (test_relmap_shell +15 nodes, keymap +13 params +1 fence cell, key_dispatch −0 +13 rows — node accounting per file in the GREEN transcripts). Guard-set totals: `1066 passed, 2 skipped, 3 xfailed` (wall 245s, exit 0) vs the Inc-1b baseline `762 passed, 2 skipped, 3 xfailed` — Δ +304 = +15 host arms +13 relmap seat params +1 scope fence +1 glyph-map arm +13 key_dispatch params +4 inc9c legend arms (the derived help-screen set grew) +~140 inc9c/help/keymap-adjacent nodes (the same derived sets) + the R1 relmap suites re-counted unchanged; every amended census reconciles per the Correction population table. The R1 relmap suite is unchanged node-for-node (adapter 40, audit 49, descriptor 90+1 amended fence, gaps, model, profile, text 15, isolation).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Kimi K2.8 session executing agents/code-reviewer.md + agents/security-reviewer.md + agents/ux-reviewer.md · iterate (BLOCK-UNTIL: F1, F2) → discharged 64bc1bc` — `evidence/review-inc002.md`; the follow-ups pass is §4c below. The orchestrator's re-check of the added arms and the Inc-2 approval are NOT recorded here. |

---

## 4c · Follow-ups after the independent review (Inc-2 review pass, 2026-10-25; ledger `LED-2026-10-25-r2.18`)

| Item | Disposition |
|---|---|
| F1 MAJOR — the renderer state word leaks across view switches (crumb shows another view's word) | FIXED: the word is stored PER VIEW (`screen._view_state_words`); the crumb shows the active view's own word; switching back restores it. Arms at 118 and 87 reproduce the reviewer's live repro (`k` on gaps → `1` → the crumb must NOT say `by kind`): `test_review_f1_the_crumb_never_shows_another_views_state_word`. RED with M-FU-2 applied (single shared word — `2 failed`, the matrix crumb painted `matrix · by kind`), restore sha256 `40ac5612…c9c5` MATCH, GREEN. LLR-RVH.4.3 amended. |
| F2 MAJOR — the frozen `cursor` channel is node-axis; the gaps contract is gap-row axis | FIXED as a declared D1 amendment (orchestrator ruling, before the lanes fork): the protocol gains `row_count(state) -> int` (ranked rows for gaps, nodes for matrix/sheet, `0` for `PendingView`); the host keeps ONE CURSOR PER VIEW, moves it within `[0, row_count)` for the active view, **clamped at the ends, no wrap**, and passes that view's cursor in `ViewState.cursor`. Arms: `test_review_f2_the_cursor_clamps_at_the_last_row_without_wrapping` (118+87; mid-sequence assertion — a wraparound is back at 0 after 3 presses), `test_review_f2_each_view_keeps_its_own_cursor` (118+87; per-view independence, `focus` untouched on the gaps axis, `ViewState.cursor` is the active view's own), `test_review_f2_the_placeholder_has_no_rows_to_cursor_over`. RVG.1.3/AT-135/AT-137 amended; AT-135's first fixture now holds 2 gaps so "row 02" exists (F9). RED before the fix: `13 failed, 12 passed` (every arm touching the amended surface, nothing else) — `evidence/p3-inc2f-red-arms.txt` (`3f51b612…7135`). |
| M-REV-3 (survived) — no arm pressed the cursor keys; gutting `_move_selection` left the trio 188/188 GREEN | FIXED: the cursor arms above press the real cursor keys through `run_test()`. M-REV-3 re-applied (`_move_selection` gutted): `4 failed` (the four cursor-arm params), restore sha256 `40ac5612…c9c5` MATCH, trio GREEN `196 passed` — `evidence/p3-inc2f-mutants.txt` (`53519f2f…7f94a`). The on-home toggle half (F7b) is pinned by the F1 arm (the spy asserts `k` reaches the gaps toggle on its home view and the word lands in the crumb). |
| F3/F4 MINOR — dead `_VIEW_KEYS`, dead `ViewState.lens` | FIXED: both deleted; the matrix lens rides the `enter` toggle channel (D1 as amended). The D1 pin arm (`test_d1_surface_names_are_frozen`) asserts the field set without `lens` and `row_count` on the protocol. |
| F5/F6/F10 MINOR — the freeze docstring named only `c`/`k`; the `notice` obligation unstated; the matrix crumb word unpinned | FIXED in the `base.py` freeze text: the kind vocabulary `enter`/`c`/`k`, the words `panel lens` (matrix), `by kind` (gaps), `direct only`/`stacked chain` (sheet), the renderer's `notice` obligation and the `row_count` axis rule are all named; pinned by `test_d1_freeze_text_names_the_full_toggle_vocabulary`. |
| F8 — `base.ViewState` vs `views.state.ViewState` collision | DECLARED (accepted): different module, different shape, loud failure on cross-import — no action, as the packet already recorded. |

Mutant battery this pass: M-REV-3 KILLED ×4 · M-FU-1 (clamp → wraparound) KILLED ×2 after the clamp arm gained its mid-sequence assertion (the first battery pass recorded the SURVIVED honestly and the arm was strengthened — the mutant was re-applied and killed) · M-FU-2 (crumb shows any view's word) KILLED ×2; every restore sha256-verified.

GREEN: targeted trio `196 passed` (188 + 8 new arm params), `evidence/p3-inc2f-green-targeted.txt` (`327f9a34…c06b`); guard set (the commission's list) `1022 passed, 2 skipped, 3 xfailed` — exit 0, only the station-expected skips/xfails — `evidence/p3-inc2f-green-guards.txt` (`80474760…2351`). RED first, per arm: `evidence/p3-inc2f-red-arms.txt`. All transcripts redacted with PYTHON (account name → `<user>`) before hashing; `PYTHONDONTWRITEBYTECODE=1` in every run.

D1 amended surface (what the lanes now build against): `ViewState(relmap, notice, focus, cursor, gaps, width, height)` — `cursor` is the active view's row index on that view's own axis; `RelMapView.paint(state) -> list[Text]` (the `notice` obligation stated); **`RelMapView.row_count(state) -> int`** (new; `PendingView` returns 0); `RelMapView.toggle(kind: str) -> str` (kinds `enter`/`c`/`k`); `build_view(name)` + `PendingView` unchanged. Recorded in the PDR record §D D1 (ruling annotation), the proposal §4, `docs/ARCHITECTURE.md` §4, the contract (LLR-RVG.1.3/LLR-RVH.4.3), `01b-acceptance-design.md` (AT-135/AT-137) and ledger `LED-2026-10-25-r2.18`.

## 5 · Risks

- The `PendingView` placeholder is visible mid-batch: if the batch stalls before lanes 3/4/5, the operator sees `matrix · <focus>` bodies. Mitigation: the batch order of merit puts the lanes next; the placeholder is the honest declaration, not a silent stub.
- `base.ViewState` shares its name with the tree kind's `mapper.views.state.ViewState` (different module, different shape). Lanes import it from `mapper.screens.relmap.base`; a cross-import would fail loudly at import time, and the A3 census above records the collision as pre-existing.
- The out-of-view inertness arms spy the placeholder's `toggle`; the lane renderers must keep the same contract (the freeze text is the contract).

## 6 · Pending items / spec deviations

- None against the contract. COND-QA-2 discharged (the whole-seat pin re-runs in this increment's guard set); COND-QA-4 discharged (both derive-count arms WRAP `derive_reqharness_map`, never replace it — Layer A args arm included); COND-ARCH-1 discharged (the `toggle(kind) -> str` channel is built and pinned); COND-UX-1 discharged at host level (lanes own their home-view halves); COND-SEC-1's LF/TAB one-row arm executes fully with lanes 3/4/5 per the PDR's discharge note — the host sink arm executes here.
- The `test_inc9.py` opener census and the fold/relmap descriptor/isolation/citation censuses were amended in this increment (test files, uncapped; each enumerated by its own failing probe — see Correction population).

## 7 · Suggested next task

Fork the lanes — F-1…F-5 re-read at each lane's entry: F-1/F-2 close with this increment (text leaf landed Inc-1a+1b; the D1 surface + seat landed here and the PDR seal freezes them); L1 matrix · L2 gaps · L3 sheet · shell Inc-6 in parallel, then 6b → 7.

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 4/4 — the §2 ⚠ states why the cut cannot be smaller |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_relmap_shell.py` new (15 nodes), both seat pins extended, run RED-before-GREEN |
| 3 | Layer 0 written where the criterion applies | `full` | ✓ | the `label` sink unit arm (branchful coercion path) + D1 surface pin + fixture control |
| 4 | RED counterfactual declared | all | ✓ | code-absent (exit 2) + 3 move-aside arms (exit 2 each), restores sha256-proven |
| 5 | Reverse census declared | all | ✓ | §Reverse census — 5 probes; B2/B3 not fired; A3 clean |
| 6 | `code-reviewer` passed | all | ⚠ | iterate (BLOCK-UNTIL: F1, F2) → both discharged at the trunk Inc-2 review pass (§4b/§4c, ledger `LED-2026-10-25-r2.18`); the re-read and the approval are the orchestrator's |
| 7 | No file from another lane touched | all | ✓ | trunk increment; lanes have not forked — `matrix.py`/`gaps.py`/`sheet.py` do not exist yet |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D2 (text leaf) untouched; D1/D3 LANDED exactly as frozen (the seal's names, no drift); D4/D5 untouched |
| 9 | Coverage claims verified on disk | all | ✓ | 188 targeted nodes collected on disk in the final run |
| 10 | Load-bearing emptiness declared | all | ✓ | §Load-bearing emptiness — positive controls named per absence |
| 11 | Mutation verdicts declared | all | ✓ | 11/11 KILLED per arm, restore digests cited, battery exit 0 |
| 12 | Instrument RED-proof declared | all | ✓ | 4 instruments each shown RED first (incl. the runner's own BAD control) |
| 13 | Correction population declared | all | ✓ | 5 corrections, each enumerated by its failing census before its first edit |
| 14 | Emitted-form assertion declared | all | ✓ | 3 artifacts asserted on emitted bytes (frame, keybar line, refusal notice) |
| 15 | Independent review names somebody | all | ✓ | `code-reviewer` (Kimi K2.8 session, code + security + UX lenses) — iterate, BLOCK-UNTIL F1/F2, both discharged at the trunk review pass (§4b/§4c) |
| 16 | Evidence files declared | all | ✓ | 5 files at `artifact_homes.evidence`, digests of stored bytes |
