# Validation — mapper — Batch 2026-10-10-csv-safety-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label** — the reserved field names are declared in §✅ Verdict and are read literally.
> Phase 4 artifact. Content owner: `qa-reviewer`, who **EVALUATES** the results of the validation strategy fixed in Phase 1, **names who executed each one** and returns the rows; the orchestrator writes `04-validation.md` (`stations/shared-homes-roles.md` §Delegation). The ONE complete gate-suite run is the orchestrator's (`C-25`); a sub-agent consumes the result and never owns the run.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/validation-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

## ✅ Verdict (read first)

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Result` · `Layer 0` · `Evidence checklist` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.
>
> **And so are the three verdict tokens** `PASS` · `PASS-WITH-NOTES` · `FAIL`, which are VALUES and not prose.
> A Spanish batch writes `- **Result:** PASS`, not `- **Resultado:** aprobado`: the label, the tokens and the
> reviewer-identity tokens below are the machine's vocabulary.

- **Result:** PASS-WITH-NOTES
- **Layer 0:** 2 unit(s) met the criterion (`MapStore._check_round_trip`; the preview's record/precedence branch in `_ImportPreviewScreen`) · each carries a named reddening mutation, all executed RED (M1/M1b/M4/M-dump2/M-dumpwrite; M2/M2b/M2c)
- **Requirements:** 10/10 pass (HLR-CSV.1, HLR-CSV.2, HLR-CSV.3, LLR-CSV.1.1, LLR-CSV.1.2, LLR-CSV.1.3, LLR-CSV.2.1, LLR-CSV.2.2, LLR-CSV.2.3, LLR-CSV.3.1) · 0 blocker fails
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome through the shipped surface (boundary + negative)
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs/deliverables reached/observed at the surface
- **Supersession inspection (read off the P3 packets):** ✓ all surviving refs negative — the modular move oracle's `DECLARED_CHANGES` freeze was retired in increment 4 (increment-001 packet / DDR B1) and has zero surviving readers
- **Test ledger:** ✓ reconciles (`base − D + A = post` → 3136 − 0 + 24 = 3160)
- **Evidence checklist (qa-reviewer):** drafted by the worker sub-agent (Kimi, `kimi-for-coding`, unit CSVCLOSE) · 11 of 11 rows ✓ with evidence · reviewer cell PENDING — recorded by the orchestrator

> If every line is ✓, the Detail below is reference only. Any ⚠/✗ → read the matching part.

**Verdict reason (3 lines):** all 10 requirements pass with executed evidence; every AT-072/072b/072c/072d/073/074 is GREEN with an executed RED counterfactual (M1–M4 family, transcripts `evidence/inc1-red.transcript` … `inc4-red.transcript`), and the ledger reconciles (3136 − 0 + 24 = 3160 collected; gate run 2: 3156 passed / 0 failed). The P4 performance record owed by C2/R12 measures the round-trip check at 3.2 % of `MapStore.save` wall time (≤ 25 % threshold, `evidence/p4-save-cost.transcript`, sha256 `bb07e56f…8492a4`). The notes are carried minors, not new findings: LOW-2 substring coupling accepted (DDR B1) and B-115/B-116/B-117 carried to the backlog. None blocks the gate.

---

## Detail (reference)

### Layer 0 — unit

| Unit | Which criterion | Node id | Result |
|---|---|---|---|
| `MapStore._check_round_trip` (`mapper/store.py:810`) | refuses when the reparse raises, the node-id set differs, or the edge multiset differs; runs before any byte is written (LLR-CSV.1.1/1.2) | `tests/test_csv_safety_store.py` — 9 nodes | pass — M1/M1b/M4/M-dump2/M-dumpwrite all executed RED |
| `_ImportPreviewScreen.refresh_canvas` + `action_save` record/precedence branch (`mapper/screens/import_preview.py`) | collision > multi-parent > cycle painting; record-keyed refusal at the `s` keypress (LLR-CSV.2.2/2.3) | `tests/test_csv_safety_preview.py` — 12 nodes | pass — M2/M2b/M2c all executed RED |

**Measured by mutation, never by line coverage.** For each unit, name the mutation and paste the RED:

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|
| `MapStore._check_round_trip` | M1 (delete the round-trip check, keep nothing else that refuses) — reddens `test_save_refuses_multi_parent_graph` / `…_unparsable_dump` / `…_reparse_structure_mismatch` | yes — `FAILED tests/test_csv_safety_store.py::test_save_refuses_multi_parent_graph` | `evidence/inc1-red.transcript` (sha256 `44ad41e5…`, restore of `mapper/store.py` to `293c521e…7773` recorded in-file) |
| `MapStore.save` write ordering / dump-once | M1b (validation after the first temp-file replace) — reddens `test_refused_save_changes_no_workspace_byte`; M-dump2 / M-dumpwrite — redden `test_save_writes_the_bytes_dump_returned_and_dumps_once` | yes | `evidence/inc1-red.transcript` (M1b) · `evidence/inc4-red.transcript` (M-dump2/M-dumpwrite, restores sha256-checked) |
| root comparison (negative arm of LLR-CSV.1.3) | M4 (re-add the root comparison the ruling R11 removed) — reddens `test_save_accepts_legacy_forest_after_edit` | yes | `evidence/inc1-red.transcript` (M4 with its own immediate restore, completed by increment 4) |
| preview record + precedence branch | M2 (paint the graph anyway / generic message) — reddens `test_at_073_preview_names_the_colliding_rows`, `test_empty_csv_panel_renders_no_sentence`; M2b (stop appending to the collision record) — reddens `test_preview_csv_records_collisions`; M2c (remove the record-keyed refusal) — reddens AT-072/072b/072c/072d | yes | `evidence/inc2-red.transcript` (sha256 `065c581f…`) · `evidence/inc3-red.transcript` (sha256 `408847ff…`, incl. the markup-path switch mutation on `test_markup_in_id_is_painted_verbatim`) |
| `_build_sidecar` titles | M3 retargeted (drop the title from `_build_sidecar`) — reddens `test_save_load_roundtrip_valid_trees` and AT-074 | yes | `evidence/inc4-red.transcript` (sha256 `399f99f0…`, M3-effective) |

### UX walkthrough — only if trigger family D fired

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|
| not applicable — family D did not fire (no new interactive surface; the refusal panel is painted content on the existing import-preview screen, asserted through the real key flow by AT-073) | — | — | — |

**Mechanism used:** `a UI test driver — MapperApp(tmp_path) + app.run_test(size=…) + pilot.press(...)` for the acceptance layer; `none — inspected only` for the walkthrough table

| Act | What it is | Performed? |
|---|---|---|
| Automated walkthrough | the criteria above, driven through the REAL mechanism | `performed — AT-072/072b/072c/072d/073/074 drive the real import flow (`i`, path, `enter`, `s`) through `_open_import` with real keys and assert the painted toast, the panel source, the no-write oracle and the re-open equality` |
| Expert inspection | a cognitive walkthrough against declared criteria, by a reviewer and not a user | `performed — P2 architect + qa two rounds, PDR, three code reviews, DDR and the increment-4 re-reviews (all Claude models, read-only)` |
| Evaluation with users | real users of the system, doing the tasks named in the context of use | `not performed — no users: the operator authorised an autonomous batch; no PII-bearing population exists for this developer tool` |

- **Method:** trigger family D did not fire. The change's user-visible surface is the import preview: an exact refusal sentence in the existing "could not draw the preview" panel and a pinned error toast at the `s` keypress. Both are driven with real keys through the shipped app by AT-072/072b/072c/072d/073 (and the happy path AT-074), which is the real mechanism; the scripted session is `_open_import` (`tests/test_seed_safety.py:107-117`) with E-1 helpers from `tests/test_draft_save.py`.
- **Participants or population:** none — not applicable (expert review only, no users).
- **Evidence of the evaluation:** `tests/test_csv_safety_preview.py` (12 nodes, all GREEN in gate run 2) + the RED transcripts `evidence/inc2-red.transcript`, `evidence/inc3-red.transcript`.
- **Limits:** this establishes nothing about real-user comprehension of the refusal sentence; the sentence's exact wording is pinned by tests, not by user reading.

### Layer A — functional (white-box): per-requirement results
> `TC-NNN` ↔ LLR/HLR. `Result` = pass / fail. `Evidence` = command output, observed behavior, inspection note, or analysis result.
> Selector counts re-collected at HEAD `04e9740` by the worker sub-agent (unit CSVCLOSE) with `python -B -m pytest --collect-only -q -p no:cacheprovider`: `tests/test_csv_safety_store.py` → 9, `tests/test_csv_safety_preview.py` → 12, `tests/test_mod_bodies.py` → 5, whole suite → `3160/3184`. None of the cited selectors collects 0.

| Req | Method | Executed verification | Numeric threshold | Result | Evidence |
|-----|--------|-----------------------|-------------------|--------|----------|
| HLR-CSV.1 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_store.py` — 9 collected; run inside gate run 2 (`evidence/gate-run2-full-suite.transcript`, sha256 `0825717e…`) — **executed by: orchestrator** (gate), worker Kimi (unit CSVI1, per-increment RED) | exit 0; multi-parent, cycle, unparsable-dump and reparse-structure-mismatch saves refused; refused save changes no workspace byte (sha256 oracle incl. `mapper.db`/`*.tmp`); legacy forest saves after an edit | pass | `tests/test_csv_safety_store.py::test_save_refuses_multi_parent_graph` · `…_cycle_still` · `…_unparsable_dump` · `…_reparse_structure_mismatch` · `…_refused_save_changes_no_workspace_byte` · `…_accepts_legacy_forest_after_edit`; RED: M1/M1b/M4 in `evidence/inc1-red.transcript` |
| HLR-CSV.2 | test | `python -B -m pytest -q -p no:cacheprovider tests/test_csv_safety_preview.py` — 12 collected; run inside gate run 2 — **executed by: orchestrator** (gate), worker Kimi (CSVI2/CSVI3) | exit 0; the panel paints the pinned collision sentence (rows 5/6, ids `a-b`/`A B`) with the header, the exact three-way grammar (`rows 2, 3 and 4`, no Oxford comma), the neutral cycle sentence, verbatim markup ids; empty CSV paints no sentence | pass | `tests/test_csv_safety_preview.py::test_at_073_preview_names_the_colliding_rows` · `test_preview_csv_records_collisions` · `test_three_way_collision_uses_list_grammar` · `test_cycle_csv_paints_the_neutral_cycle_sentence` · `test_colliding_cyclic_csv_paints_the_collision_sentence` · `test_markup_in_id_is_painted_verbatim` · `test_empty_csv_panel_renders_no_sentence`; RED: M2/M2b in `evidence/inc2-red.transcript`, markup-path mutation in `evidence/inc3-red.transcript` |
| HLR-CSV.3 | test | the round-trip nodes of `tests/test_csv_safety_store.py` + AT-074 through the real app; run inside gate run 2 — **executed by: orchestrator** (gate), worker Kimi (CSVI4) | exit 0; save→load returns the same node-id set, edge set, root and titles for the valid multi-row CSV, the valid trees, the empty and single-node graphs | pass | `tests/test_csv_safety_store.py::test_save_load_roundtrip_valid_trees` · `…_empty_and_single_node`; AT-074 node below; RED: M3-effective in `evidence/inc4-red.transcript` |
| LLR-CSV.1.1 | test (unit) | `tests/test_csv_safety_store.py` (9 collected) — 5 refusal/dump-once nodes; gate run 2; P4 perf record | exit 0; one dump per save, the checked text IS the written text; the round-trip check adds ≤ 25 % of save wall time on a 6 000-node wide tree | pass | `test_save_refuses_*` (4) · `test_save_writes_the_bytes_dump_returned_and_dumps_once`; RED: M1 (`evidence/inc1-red.transcript`), M-dump2/M-dumpwrite (`evidence/inc4-red.transcript`); perf: `evidence/p4-save-cost.transcript` (sha256 `bb07e56f…8492a4`) — **3.2 %, PASS** |
| LLR-CSV.1.2 | test (unit) | `tests/test_csv_safety_store.py -k refused_save` — 1 node; gate run 2 | exit 0; overwrite-attempt fixture: every pre-existing workspace file byte-identical after the refused save | pass | `test_refused_save_changes_no_workspace_byte`; RED: M1b (`evidence/inc1-red.transcript`) |
| LLR-CSV.1.3 | test (unit) | `tests/test_csv_safety_store.py -k forest` — 1 node; gate run 2 | exit 0; legacy forest (`a` / `b --> c`) loads, accepts a child, saves; reloaded root may differ (B-117, never asserted) | pass | `test_save_accepts_legacy_forest_after_edit`; RED: M4 (`evidence/inc1-red.transcript`) |
| LLR-CSV.2.1 | test (unit) | `tests/test_csv_safety_preview.py -k records_collisions` — 1 node; gate run 2 | exit 0; the record names exactly the expected (line number, raw id) pairs for the CRLF perf CSV (rows 5/6), a blank-line CSV (rows 4/5), three-way, auto-id and both no-loader-violation shapes; empty for clean/single/empty | pass | `test_preview_csv_records_collisions`; RED: M2b (`evidence/inc2-red.transcript`) |
| LLR-CSV.2.2 | test (integration) | `tests/test_csv_safety_preview.py -k at073` + the sentence-grammar nodes; gate run 2 | exit 0; header and sentence asserted together; precedence collision > multi-parent > cycle; every interpolated piece through `darkside.plain` | pass | `test_at_073_preview_names_the_colliding_rows`; RED: M2 (`evidence/inc2-red.transcript`), markup-path mutation (`evidence/inc3-red.transcript`) |
| LLR-CSV.2.3 | test (e2e) | `tests/test_csv_safety_preview.py -k 'at072 or at072b or at072c or at072d'` — 4 nodes through `_open_import` (`i`, path, `enter`, `s`); gate run 2 | exit 0; refusal fires at the `s` keypress — no prompt screen, pinned toast `the CSV has colliding ids — nothing was saved; see the preview` at severity `error`, no-write oracle, preview stays open | pass | `test_at_072_refused_save_toasts_and_writes_nothing` · `test_at_072b_parentless_slug_collision_refuses_save` · `test_at_072c_mixed_parentage_slug_collision_refuses_save` · `test_at_072d_auto_id_slug_collision_refuses_save`; RED: M2c (`evidence/inc2-red.transcript`) |
| LLR-CSV.3.1 | test (unit) | `tests/test_csv_safety_store.py -k roundtrip` — 2 nodes; gate run 2 | exit 0; node-id set, edge set, root and titles identical after save→load, incl. empty and single-node | pass | `test_save_load_roundtrip_valid_trees` · `test_save_load_roundtrip_empty_and_single_node`; RED: M3-effective (`evidence/inc4-red.transcript`) |

**A worked example — text to read, never rows of your record.** It sits in a fence so that nothing has to be deleted: a row copied out of it would claim a verification nobody ran. Write your own rows in the table above.

```text
| *(example)* HLR-001 | test | `pytest … -k TC-001` | exit 0 | | |
| *(example)* LLR-001.1 | test (unit) | `…` | `…` | | |
```

### Layer B — behavioral (black-box) acceptance

| US | Acceptance test (`AT-NNN`) | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|----------------------------|----------------|---------------------------------------|----------------------------|--------|
| US-CSV-001 | AT-072 (`tests/test_csv_safety_preview.py`, 1 node) | the real app — `MapperApp(tmp_path)` + `run_test` + real keys via `_open_import` | the pinned error toast at the `s` keypress; the workspace dir byte-for-byte unchanged (sha256 oracle incl. `mapper.db`, no `*.tmp`, no `.mmd`/`_nodos.yml` appeared); the preview still open | repr: the colliding perf-evidence CSV refused with the pinned sentence · boundary: refusal fires BEFORE the save-as prompt (no name typed, ruling R15) · negative: M2c (record-keyed refusal removed) → the save lands, RED | pass |
| US-CSV-002 | AT-073 (1 node) + the LLR-CSV.2.3 nodes AT-072b/072c/072d (3 nodes) | the same real import flow | `#import-preview-canvas` Static source: the `could not draw the preview` header AND the exact collision sentence naming rows 5 (id `a-b`) and 6 (id `A B`); the three no-loader-violation collision shapes refused at the `s` keypress with the same toast | repr: original ids + 1-based line numbers from the record · boundary: empty CSV (root None) paints no sentence; three-way grammar `rows 2, 3 and 4`; root-collision fixture paints the COLLISION sentence (R13) · negative: M2/M2b (sentence/record removed) → RED | pass |
| US-CSV-003 | AT-074 (1 node) | the same real import flow + `MapStore.load` | a valid multi-row CSV saved via `s` + name; re-open returns node ids, edges, root and titles identical to the preview graph | repr: full round-trip equality through the shipped surfaces · boundary: the empty and single-node round-trips ride the LLR-CSV.3.1 unit nodes · negative: M3-effective (sidecar titles dropped) → AT-074 RED (`evidence/inc4-red.transcript`) | pass |

### Bidirectional surface-reachability matrix (extends A-5)
> Every named INPUT dimension AND every named OUTPUT/deliverable is exercised/observed through the handler — not only the service API.

| Direction | US dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|---------------------------|--------------------------|------------------------------|---------|--------|
| input | US-CSV-001/002 the colliding CSV file on disk | the typed path through `_open_import` (`i`, path, `enter`) | yes | AT-072 · AT-073 | ✓ |
| input | US-CSV-001/002/003 the `s` keystroke | `pilot.press("s")` on the import preview | yes | AT-072 · AT-072b/c/d | ✓ |
| output | US-CSV-001 the pinned error toast + an untouched workspace | `screen.notify` at the refusal site; the sha256 no-write oracle over every workspace file | yes | AT-072 | ✓ |
| output | US-CSV-002 the refusal sentence in the preview panel | `#import-preview-canvas` Static source (header + sentence together, ruling R10) | yes | AT-073 | ✓ |
| input | US-CSV-003 the valid CSV through the same flow | `_open_import` incl. the save-as prompt and the typed name | yes | AT-074 | ✓ |
| output | US-CSV-003 the persisted map re-opened equal | `MapStore.load` on the saved map id | yes | AT-074 | ✓ |
| input | US-CSV-001 (store layer) a graph whose dump does not reparse | `MapStore.save(map_id, graph)` direct, unit fixtures | yes | `test_save_refuses_*` | ✓ |
| output | US-CSV-001 (store layer) refusal before any byte | the two-phase write never starts; pre-existing bytes identical | yes | `test_refused_save_changes_no_workspace_byte` | ✓ |

### Signed-balance test ledger
> `post = base − D + A`. State counts in collected / passed-lean / passed-full form.

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| 3136 = 3133 passed + 3 xfailed (P0 base `a36f63e`, the modular close — `evidence` of `.dev-flow/2026-10-09-modular-batch/evidence/p4-gate-full-suite.transcript`: **3133 passed, 24 deselected, 3 xfailed**, sha256 `eb263fb1…`, exit=0) | 0 — `git diff -U0 a36f63e HEAD -- tests \| grep '^-.*def test_'` prints **nothing**: no test function was deleted (`DECLARED_CHANGES` was a module-level constant added at `1537985` and removed in increment 4 — not a test function; no test FILE deleted either) | 24 = **22 new test functions** (`git diff a36f63e HEAD -- tests \| grep -c '^+.*def test_'` → 22; `git grep -c 'def test_'` 1315 → 1337; the 22 are named in the §6.1 fixture list of the contract) **+ 2 new parametrised arms** `test_at_p02i_every_model_field_is_classified[CsvRow]` / `[CsvCollision]` — the model-field totality guard derives its arms from `mapper.model`, so the two new CSV dataclasses add 2 collected items with no new `def` | = 3160 | 3160 (`3160/3184 tests collected (24 deselected)` at HEAD `04e9740`, re-collected by this sub-agent) | — / gate run 2 at `1537985` (the tree one test-only commit before HEAD): **3156 passed, 24 deselected, 3 xfailed in 1718.54s, exit=0**, sha256 `0825717e…`; the HEAD tree adds exactly increment 4's one node (`test_llr_mod_4_3_red_a_deleted_moved_method_reddens_missing`), collected 3160 | yes |

**Gate runs (the orchestrator's; this sub-agent consumes, never owns):**

| Run | Tree | Result | Evidence (sha256) |
|-----|------|--------|-------------------|
| P0 base | `a36f63e` | 3133 passed / 3 xfailed / 0 failed (modular close) | `.dev-flow/2026-10-09-modular-batch/evidence/p4-gate-full-suite.transcript` (`eb263fb1b150c871…`) |
| increment-1 gate | `d4941ea` | **4 failed / 3139 passed** — the model-field totality guard caught the new unclassified `Graph.csv_collisions` / `CsvRow` / `CsvCollision` fields; fixed in `6763852` (the follow-up classification) | `evidence/inc1-gate-full-suite.transcript` (`3877a5b4…`) |
| final run 1 | increment-3 commit | **3 failed / 3153 passed** — the modular move oracle (`test_llr_mod_4_3_bodies_match_baseline`) and the A3 census pin, both gate follow-ups | `evidence/gate-run1-full-suite.transcript` (`4ad7dc3d…`) |
| final run 2 | `1537985` | **3156 passed / 0 failed** (after the gate follow-ups; before increment 4, which is test-only) | `evidence/gate-run2-full-suite.transcript` (`0825717e…`) |
| final run 3 | HEAD (after increment 4, test-only) | **3157 passed / 24 deselected / 3 xfailed / 0 failed**, exit 0 — 3157 + 3 = 3160 = collected | `evidence/gate-run3-full-suite.transcript` sha256 `a70ebc27befe3f8557994057db38daa1e42073bb07eef061c6c91dcc1e6ef3f9` |

- Arithmetic: 3136 − 0 + 24 = 3160 (collected) — reconciles. Passed-full form: 3133 − 0 + 23 = 3156 at the run-2 tree (22 new functions + 2 new param arms − 1 xfailed-invariant… none; the 22nd function and both arms are the +23 passed over base at run 2: 3156 − 3133 = 23 = 21 store/preview functions (9 + 12) + 2 param arms, with `test_mod_bodies`' +1 landing after run 2) — both forms stated, both reconcile.
- P4 performance record (C2/R12, a measurement not a suite assertion): median of 3 of `MapStore.save` on a 6 000-node wide tree in a tmp workspace — with check 2.774 s vs check skipped 2.687 s → added 0.087 s = **3.2 %** of save wall time ≤ 25 % threshold — `evidence/p4-save-cost.transcript` (sha256 `bb07e56fe3c4c237…8492a4`), spike script `.dev-flow/2026-10-10-csv-safety-batch/spike/p4_save_cost.py` (monkeypatches `_check_round_trip` to a no-op inside the script only; no product file touched).

### Gaps detected
| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| G-001 | LLR-CSV.1.1 | LOW-2 (accepted, recorded in DDR B1): the refusal sentence substring-couples to the loader's parse-error wording (`mapper/store.py:832`) — a loader message reword would silently weaken the store's user-facing reason | minor | carried as an accepted coupling (DDR B1, optional fix); decouple when `mapper/mermaid.py` messages next move |
| G-002 | carried backlog (not batch gaps) | B-115 (`slugify("") == "n"` empty-slug family), B-116 (child-before-root row-order refusal), B-117 (forest root drift on reload — the round trip deliberately does not compare the root, ruling R11) | minor (all pre-existing) | backlog — the next batch touching `mapper/mermaid.py` / `mapper/import_csv.py` owns each per its BACKLOG.md entry |

### Escaped-bug regression (if a defect escaped the suite)

| Regression id (`AT-NNN` / `TC-NNN`) | Pre-fix run (evidence it FAILED) | Pre-fix RED kind (value / shape) | Post-fix value-discriminating? (QC-2) | Post-fix result | Reconciled node |
|-------------------------------------|----------------------------------|----------------------------------|----------------------------------------|-----------------|-----------------|
| none — no defect escaped the suite in this batch | — | — | — | — | — |

*(The inc-1 gate failure was caught at the gate, not escaped: the model-field totality guard refused the unclassified new fields before any close — see the gate-runs table.)*

### Evidence checklist — qa-reviewer (full)
> Attach `qa-reviewer`'s completed evidence checklist (items in `agents/qa-reviewer.md`), each marked ✓/✗ with one-line evidence. An unchecked or evidence-less item blocks the gate.

**Who executed what:**
- **The orchestrator (Claude Opus 5.5)** owns the gate suite runs (C-25): the increment-1 gate, final runs 1–3. It also ran the P2 architect/qa reviews (two rounds), the PDR, the three code reviews, the DDR and the increment-4 re-reviews — all Claude models, read-only; the worker was Kimi (`kimi-code/kimi-for-coding`).
- **Workers (Kimi, units CSVI1–CSVI4)** authored the product change and the guard/AT tests across the 4 increments; each increment's RED transcript is the worker's (`evidence/inc1-red.transcript` … `inc4-red.transcript`, `gate-followup-red.transcript` for the `DECLARED_CHANGES` arms).
- **The sub-agent (Kimi, unit CSVCLOSE)** ran the P4 performance measurement (`evidence/p4-save-cost.transcript`), re-collected every selector count at HEAD `04e9740`, ran the function-level deleted-test check and the ledger arithmetic, and drafted this file.
- **The `qa-reviewer`** ran nothing and read the transcripts; its review happened as the P2 rounds/PDR/DDR.

| # | Item | ✓/✗ | Evidence |
|---|---|---|---|
| 1 | Acceptance criteria as outcomes | ✓ | AT-072/072b/072c/072d/073/074 observed in Layer B through the shipped app |
| 2 | Explicit Expected | ✓ | exit 0; pinned toast text and severity; exact sentence; no-write sha256 oracle; round-trip equality |
| 3 | Edge cases | ✓ | empty CSV, blank-line/CRLF counting, three-way grammar, auto-id collision, root-collision precedence (R13), forest after edit, newline/arrow titles, duplicate edges, overwrite-attempt |
| 4 | Regression checklist | ✓ | gate run 2: 3156 passed / 3 xfailed / 0 failed; P4 perf record 3.2 % ≤ 25 %; M1–M4 mutation transcripts |
| 5 | Exit criteria | ✓ | 10/10 requirements pass; every AT GREEN with an executed RED; 0 failed at gate run 2 |
| 6 | No PII / secrets | ✓ | no operator paths, no home paths, no account names in this artifact or the cited transcripts (guard A-110 stays green) |
| 7 | Mode + executor per result | ✓ | "executed by: orchestrator" on the gate rows; worker/sub-agent rows marked |
| 8 | Layer B with boundary + negative | ✓ | three story rows, each repr/boundary/negative |
| 9 | Bidirectional reachability | ✓ | 4 inputs + 4 outputs, all ✓ |
| 10 | Ledger | ✓ | 3136 − 0 + 24 = 3160; 22 functions + 2 param arms; deleted-function check prints nothing |
| 11 | No unfilled template | ✓ | this checklist pasted; example rows left fenced, not copied |

**Reviewer cell:** PENDING — recorded by the orchestrator (the qa-reviewer identity, verdict confirmation and any conditions replace this marker).
