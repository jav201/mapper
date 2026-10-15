# Increment 001 — LLR-FX.1.1-1.3, LLR-FX.2.1-2.2 · `CSV import: blank parent, row-N ids, root by parentage`

> **Owed in.** `core` ✓ · `full` ✓

| Field | Value |
|---|---|
| Batch | `2026-10-11-fixes-batch` |
| Increment | `001` |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | US-FX-001/002 · HLR-FX.1, HLR-FX.2 · LLR-FX.1.1, 1.2, 1.3, 2.1, 2.2 (B-115, B-116) |
| Acceptance | AT-084 · AT-085 · white-box TC-FX-1.1, 1.2, 1.3, 2.1, 2.2, TC-FX-S1 · unit: the `test_root_*` and `test_permutation_*` nodes |
| Agent | `software-dev` |
| Date | `2026-10-15` |

---

## 1 · What changed

A blank (or whitespace-only) parent cell in an imported CSV now means "no parent", an id with no slug characters imports as the next `row-N`, and the root is the first parentless, non-parked row wherever it sits in the file. Mechanism: `slugify` returns `""` when nothing survives (no more silent `"n"`); `preview_csv` decides "has a parent" from the stripped cell before slugging, takes `row-N` from one shared counter only when the slug is empty (a title-derived id does not advance it), records parked rows in a set, and after the edges exist elects the root from the parentless list (else the first parentless, else leaves the first row) and attaches the other parentless rows under it. Shipped surface: the `i` import key, the preview frame, and `s` save then `MapStore.load`.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/mermaid.py` | source | LLR-FX.1.1 | `slugify` returns `value[:32]` (empty string when nothing survives); docstring says so |
| `mapper/import_csv.py` | source | LLR-FX.1.2, 1.3, 2.1, 2.2 | blank-first parent read; `row-N` for an empty slug; `parked` set; root by parentage; docstring |
| `tests/test_fixes_csv_import.py` | test | HLR-FX.1, HLR-FX.2 | new: 15 nodes incl. AT-084, AT-085, TC-FX-S1 and the 24-permutation node |
| `tests/test_mermaid.py` | test | LLR-FX.1.1 | pin `slugify("---") == "n"` moved to `""` + new node `test_slugify_returns_empty_when_nothing_survives` |
| `.dev-flow/2026-10-11-fixes-batch/evidence/inc001-red.transcript` | doc | | RED/restore transcript |

Pin move, itemised. What: in `tests/test_mermaid.py::test_slugify_allows_hyphens` the line `assert slugify("---") == "n"` became `== ""`. Why: LLR-FX.1.1 changes `slugify`'s empty-result value from `"n"` to `""`; it is the only existing test that fails on the patched tree (requirements premise 7). What keeps it honest: the new node asserts `""` for `""`, `"   "`, `"---"`, `"!!!"` and `"Niño" == "niño"`, and M-FX1 reddens it. No other existing test moved.

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** |
| Test files | 2 (uncapped) |
| Doc files | 1 (outside the count) |

---

## 3 · How to test

```bash
cd <worktree>
env -u NO_COLOR -u TERM python -m pytest -p no:cacheprovider tests/test_fixes_csv_import.py tests/test_mermaid.py
env -u NO_COLOR -u TERM python -m pytest -p no:cacheprovider tests/test_fixes_csv_import.py tests/test_import_csv.py tests/test_csv_safety_preview.py tests/test_csv_safety_store.py tests/test_mermaid.py tests/test_gate2.py tests/test_inc9.py tests/test_inc9c.py tests/test_inc9m.py tests/test_inc9n.py tests/test_key_dispatch.py tests/test_repair_cycles.py tests/test_repair_fields.py tests/test_perf_dump.py tests/test_model.py tests/test_seed_safety.py tests/test_requirements_canon.py tests/test_no_operator_paths.py tests/test_mod_compat.py
ruff check mapper/mermaid.py mapper/import_csv.py tests/test_fixes_csv_import.py tests/test_mermaid.py
```

---

## 4 · Test results

**GREEN line (executed):** `1 failed, 589 passed, 1 deselected in 270.99s` over the 14-file CSV/mermaid suite plus `test_seed_safety`, `test_requirements_canon`, `test_no_operator_paths`, `test_mod_compat` and the new file. `ruff check` on the two source files and the two test files: `All checks passed!`

**The 1 failure is pre-existing and not this increment's:** `tests/test_no_operator_paths.py::test_a110_no_undeclared_user_profile_path_in_any_tracked_file` reports `PLAN.md:187`. That line of the committed batch plan (commit 8b16856) writes a user-profile path pattern with an ellipsis as a prose example. PLAN.md is untouched here. It needs a one-line reword by its owner (the orchestrator); not fixed here to stay inside this increment's file set.

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `test_slugify_returns_empty_when_nothing_survives`, `test_blank_parent_cell_is_a_root_candidate_not_a_reference_to_n`, `test_punctuation_only_parent_cell_parks_the_row`, `test_id_with_no_slug_characters_becomes_row_n`, `test_root_*` (7), `test_permutation_of_rows_never_changes_the_tree`, `test_hostile_cells_yield_only_word_ids_and_survive_the_text_round_trip` (TC-FX-S1) | passed (16 new nodes in total: 15 in the new file, 1 in `test_mermaid.py`) |
| **A · white-box** TC-FX-1.1/1.2/1.3/2.1/2.2/S1 | `core` · `full` | same nodes; TC-FX-1.3 includes the `,Alpha,` then `,,` arm giving ids `{alpha, row-1}` | passed |
| **B · black-box** AT-084, AT-085 | `core` · `full` | `test_at_084_empty_parent_cells_are_roots_not_node_n`, `test_at_085_child_listed_before_root_imports_saves_and_reopens` (painted-frame assertions on `#import-preview-canvas`, C-32; AT-085 saves through `_open_import` and re-opens with `MapStore.load`) | 2 passed |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | M-FX1 to M-FX5 and M-FX2b, tabled below |
| Instrument | own Python harness kept outside the repo; restore checked by sha256 |
| Where it ran | my own worktree, one lane, no other session reading it |
| Transcript | `.dev-flow/2026-10-11-fixes-batch/evidence/inc001-red.transcript` |
| Restore proven by | sha256 returned to the pre-mutation value after every mutant (logged `equal=True`); backups taken only after the baseline block was green, deleted at the end (`== backups deleted`) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` |
| Arms resolved at baseline | 9 nodes named, 9 PASSED in the baseline block; verdicts read per node id, never from the exit code |
| Verdict granularity | per resolved node id |
| Arms that stayed GREEN | none of the named nodes in the final run (see the M-FX2 note for the first draft) |

| Mutant | Mutation (position and operation) | Nodes RED | Restore digest (equal to pre) |
|---|---|---|---|
| M-FX1 | `mermaid.py` `slugify` last line back to `value[:32] or "n"` | `test_slugify_returns_empty_when_nothing_survives`, `test_at_084_…` | `mermaid.py` 7b4d31f7b85d…6466fd0 |
| M-FX2 | `import_csv.py`: parent id = `slugify(cell)` unconditionally, "has parent" decided from the slug | `test_punctuation_only_parent_cell_parks_the_row` | `import_csv.py` 554e921e4f63…4aaa0 |
| M-FX2b | M-FX2 together with M-FX1 (the base behaviour: a blank cell slugs to `n`) | `test_blank_parent_cell_is_a_root_candidate_not_a_reference_to_n`, `test_at_084_…` | both files equal |
| M-FX3 | `import_csv.py`: delete the `if not nid:` row-N fallback | `test_id_with_no_slug_characters_becomes_row_n`, `test_hostile_cells_…` (TC-FX-S1) | `import_csv.py` equal |
| M-FX4 | `import_csv.py`: `root_id = graph.root_id` (first row stays root) | `test_root_child_listed_before_root`, `test_permutation_of_rows_never_changes_the_tree`, `test_at_085_…` | `import_csv.py` equal |
| M-FX5 | `import_csv.py`: `root_id = parentless[0]` (a parked row may be root) | `test_root_unknown_parent_row_before_the_real_root_is_not_root` | `import_csv.py` equal |

**Deviation from the requirements text, declared.** LLR-FX.1.2 names M-FX2 as "decide has-parent from the slug; the blank-cell node fails (`r` titled `? R`)". That symptom exists only while `slugify` still returns `"n"`. With the new `slugify` a blank cell slugs to `""` and a slug-based test yields the same edges. The faithful M-FX2 on the patched tree differs in one place: a punctuation-only parent cell would stop parking the row, observable only through root election when that row precedes the real root. The first draft of the punctuation node did not see it (M-FX2 SURVIVED); the node gained the `k,K,!!!` then `r,R,` arm and now kills M-FX2. M-FX2b reproduces the requirement's literal symptom and is RED on the blank-cell node.

| Field | Value |
|---|---|
| **RED counterfactual** | M-FX1 to M-FX5 (and M-FX2b) by position and operation as tabled; transcript `.dev-flow/2026-10-11-fixes-batch/evidence/inc001-red.transcript`; every restore digest equals the pre-mutation digest |

| Field | Value |
|---|---|
| **Mutation verdicts** | 6 mutants, 6 KILLED, 0 SURVIVED in the final run, 0 BAD (every anchor applied exactly once). An earlier M-FX2 draft SURVIVED the first node set (see the deviation) and was closed by a new arm, not by weakening the mutant. Transcript path as above. |

### Instrument RED-proof

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the node set (pytest) | the six mutants above, planted in the production mechanism | `FAILED` per node id in the transcript |
| the mutation harness | an anchor required to apply exactly once; the M-FX2 first draft | the harness printed `PASSED` for the M-FX2 first draft, which is how the survivor was found |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 2 instruments, each shown able to report a failure before its pass was believed |

### Emitted-form assertion

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| import preview frame (`#import-preview-canvas`, rendered plain text) | AT-084: `"▐ Alpha" in painted`, `"? Alpha" not in painted`, `"▐ ? Bang" in painted`, `"3 nodes" in painted`; AT-085: `"cycle" not in painted.lower()` | passed |
| saved `imported.mmd` re-read by `MapStore.load` | AT-085: `loaded.root_id == "root"`, edges `{("root","child")}` | passed |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against the form its producer emitted |

### Evidence files

| Evidence artifact | Path | SHA-256 |
|---|---|---|
| RED/restore transcript | `.dev-flow/2026-10-11-fixes-batch/evidence/inc001-red.transcript` | `f6081116aa3bdd0b0e4f2e8fbe3fe654ca56b52465453919219c8823c1195b43` |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "no node named `n`" in AT-084 rests on the fixture having no row whose id is `n` |
| Synthetic instance of the absent case | the `N,N,` then `k,K,n` CSV (a root literally named `N`) in `test_blank_parent_cell_…` |
| Positive control for every probe that returned an ABSENCE | the same unmodified `preview_csv` returns node `n` and edge `n -> k` on the `N,N,` file |

### Reverse census — trigger family B (re-run at the increment cut)

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rl slugify tests/` and `grep -rl preview_csv tests/` | slugify: `test_csv_safety_store`, `test_mermaid`, new file. preview_csv: `test_csv_safety_preview`, `test_gate2`, `test_import_csv`, `test_inc9c`, `test_inc9n`, `test_mod_compat`, `test_repair_cycles`, `test_repair_fields`, new file. All in the 589-passed run; none moved |
| B2 file moved on disk | `git diff --name-status --diff-filter=RD HEAD -- mapper tests` | empty |
| B3 golden captures this source | `grep -rl "slugify\|preview_csv\|import_csv" tests/goldens` | no hits; `test_perf_dump` (8 goldens) passes |
| B4 artifact produced here consumed elsewhere | `grep -rln "slugify\|import_csv\|preview_csv" mapper` | `keymap.py`, `model.py`, `screens/home.py` (feeds the preview screen and `MapStore.save`, exercised by AT-084/085 and the csv-safety suite), `screens/map/editing.py` (keeps `slugify(title) or "n"`, unchanged) |
| A3 interface consumed by another module | same grep | `slugify` empty-result value widened; its one other caller already tolerates `""` |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes (B1-B4, A3) run with commands; 0 regressions; hits re-validated by the suite run above |

### Correction population

| Field | Value |
|---|---|
| **Correction population** | none — no claim corrected across sites (the one pin move is itemised in §2) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence |
|---|---|---|---|
| `slugify("---") == "n"` | 0 hits in `tests/` | yes | `grep -rn '"---") == "n"' tests/` |

### Signed-balance test ledger

`post = base − deleted + added`: 16 added (15 in the new file, 1 in `test_mermaid.py`), 0 deleted, 0 changed in count. Executed total of this run: 589 passed + 1 pre-existing failure; the 14-file base was 490 passed (requirements premise 7) before adding `test_seed_safety`, `test_requirements_canon`, `test_no_operator_paths`, `test_mod_compat` and the 16 new nodes.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (Claude Opus) — APPROVE-WITH-NITS, 0 HIGH / 0 MED; F1 (M-FX2 negative-control text) and F2 (AT-084 id vs painted title) amended in `01-requirements.md`; F4 docstring fallback clause added to `mapper/import_csv.py`; F3 (UTF-8 BOM, pre-existing) is backlog B-130. A DeepSeek review attempt timed out (900 s runner limit) and produced no verdict. |

---

## 5 · Risks

- The `? ` prefix disappears from the single chosen root (certain, visible, ruled in the PDR); other top-level rows keep it (B-129 backlog).
- Operator-typed `row-N` ids share the namespace with generated ones: recorded as a collision, never renumbered (LLR-FX.1.3).
- `slugify` returning `""` is safe for its callers (the importer handles it; `editing.py` has `or "n"`).

## 6 · Pending items / spec deviations

- Spec deviation on M-FX2 declared in §4 (the requirement's symptom needs M-FX2b).
- Pre-existing `test_no_operator_paths` failure from `PLAN.md:187` (owner: orchestrator; one-line reword).
- Independent review: recorded in §4b (APPROVE-WITH-NITS, 0 HIGH / 0 MED); reconciled at the DDR seal 2026-10-15.

## 7 · Suggested next task

Increment 002 (B-117: `dump` hoists the declared root; `store.py` docstring).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 2 source files (§2) |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_fixes_csv_import.py`, `tests/test_mermaid.py` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | §4 layer 0 row |
| 4 | RED counterfactual declared | `core` · `full` | ✓ | §4, transcript sha256 cited |
| 5 | Reverse census declared | `core` · `full` | ✓ | §4 reverse census |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b: code-reviewer (Claude Opus) APPROVE-WITH-NITS, 0 HIGH / 0 MED |
| 7 | No file from another lane touched | all | ✓ | `tests/test_export_state.py`, `tests/test_inc9c.py` not edited (`git status`) |
| 8 | Frozen interfaces untouched | all | ✓ | `preview_csv` signature, `CsvRow`, `csv_collisions` shape unchanged |
| 9 | Coverage claims verified on disk | all | ✓ | node names resolved by the baseline run |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 table |
| 11 | Mutation verdicts declared per arm | all | ✓ | §4 table |
| 12 | Instrument RED-proof declared | all | ✓ | §4 |
| 13 | Correction population declared | all | ✓ | none |
| 14 | Emitted-form assertion declared | all | ✓ | §4 |
| 15 | Independent review names somebody | all | ✓ | §4b: Claude Opus (code-reviewer), independent of the author |
| 16 | Evidence files declared | all | ✓ | §4, sha256 |
