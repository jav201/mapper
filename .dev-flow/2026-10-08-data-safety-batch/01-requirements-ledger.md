# Requirements ledger — mapper — Batch 2026-10-08-data-safety-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

### LED-2026-10-08-data-safety-batch.1 — model C (draft + explicit save) chosen over model D
- **Requirement:** HLR-001
- **Date:** 2026-10-08
- **What changed:** HLR-001 is derived around a per-node draft plus an explicit save gesture, replacing the incumbent "every blur writes" model (D).
- **Why:** operator verdict **"C"** on the B-36 prototype round (`VERDICT-b36-prototype-2026-10-08.md`). The prototype measured sha256 of `.mmd` and `.yml` against the start state, two runs: one stray `n` then leaving the field wrote nothing, deliberate edit + `ctrl+s` wrote; today's model (D) writes after the stray key. Only an explicit save gesture closes the stray-write class B-36 names.
- **Evidence:** `mapper/widgets/inspector.py:351-365` (`on_input_blurred` → `_commit` → `FieldCommitted`); `mapper/app.py:3344-3378` (the handler writes through `_save_or_toast`; its delta gate at `:3357-3359` is invariant under a real keystroke). Prototype sha256 runs, 2026-10-08.

### LED-2026-10-08-data-safety-batch.2 — R1 draft lifetime and R2 field coverage
- **Requirement:** HLR-001, HLR-006, LLR-001.1, LLR-006.1, LLR-006.2
- **Date:** 2026-10-08
- **What changed:** the draft's lifetime is fixed as per-node, in memory, for the life of the map screen, never persisted on its own (R1); every inspector field — the `state` segment included — routes through the draft (R2).
- **Why:** R1 — one rule for every exit is easier to learn than three, and a draft written to disk would be a second save path, the very defect class being closed. R2 — a model with one exception teaches the operator that some edits are instant, which brings the stray-write back.
- **Evidence:** rulings R1/R2 in `VERDICT-b36-prototype-2026-10-08.md`; the incumbent immediate-write of `state` is `mapper/widgets/inspector.py:367-373` (`on_ds_segmented_changed` posts `FieldCommitted`).

### LED-2026-10-08-data-safety-batch.3 — R3 undo granularity and R5 undo-while-dirty
- **Requirement:** HLR-004, LLR-004.1, LLR-004.3
- **Date:** 2026-10-08
- **What changed:** one `ctrl+s` is recorded as one undo step (all fields it wrote); `u` while a draft is pending undoes the last save only and leaves the pending draft untouched.
- **Why:** R3 — undo granularity matches the save gesture the operator made. R5 — undo acts on what was written; the draft is not written yet, and `esc`/discard already govern it (architect recommendation, ARQ 2026-10-08).
- **Evidence:** rulings R3/R5 in `VERDICT-b36-prototype-2026-10-08.md`; undo stack is `mapper/app.py:3495-3533` (`_snapshots`, `_push_snapshot`, `_pop_snapshot`).

### LED-2026-10-08-data-safety-batch.4 — R1/R6 every exit asks, R4 modal keys
- **Requirement:** HLR-003, LLR-003.1, LLR-003.2, LLR-003.3, LLR-003.4, LLR-003.5
- **Date:** 2026-10-08
- **What changed:** the save · discard · stay guard is reached from every exit (node change, leaving the map screen, following a link, quitting); its keys are `s` save · `d` discard · `esc` stay.
- **Why:** R1 — one rule for every exit. R6 — following a link is the one exit R1 did not name, and it counts. R4 — as prototyped; `esc` keeps its app-wide meaning of "back out, change nothing".
- **Evidence:** rulings R1/R4/R6 in `VERDICT-b36-prototype-2026-10-08.md`; exit choke points in ARQ §D3 (`mapper/app.py:3281`, `:3566`, `:4683`, `:4719`, `:4937`).

### LED-2026-10-08-data-safety-batch.5 — R7 `↵` keeps the draft and the hint names `ctrl+s`
- **Requirement:** HLR-005, LLR-005.1, LLR-005.2
- **Date:** 2026-10-08
- **What changed:** `↵` in a field keeps the draft and leaves the field (no write); the hint `↵ save` is rewritten to name `ctrl+s`.
- **Why:** `↵` must not be a second save gesture, or the stray-write class returns through it.
- **Evidence:** ruling R7 in `VERDICT-b36-prototype-2026-10-08.md`; the incumbent hint is `mapper/app.py:4043` (`"fill in «…» · ↵ save · esc leave field"`, with the comment at `:4040`).

### LED-2026-10-08-data-safety-batch.6 — `FieldCommitted` removed, not reshaped (R-013)
- **Requirement:** LLR-001.2, LLR-001.3
- **Date:** 2026-10-08
- **What changed:** the `FichaInspector.FieldCommitted` message, its producer and its one product consumer are deleted in the same increment; `MapScreen` pulls the draft synchronously on save.
- **Why:** a posted message cannot return the save's result, yet the draft may be cleared only if the write succeeded, and the modal's `save → then leave` needs the write finished before the exit runs; a method call gives both. And a live handler is a second save path one `post_message` away — the defect class B-36 closes.
- **Evidence:** census `grep -rn "FieldCommitted\|field_committed" --include=*.py mapper tests` (2026-10-08): producer `inspector.py:68,365,372`; consumer `app.py:3344`; test consumers `test_inspector.py:103,162`, `test_g6_store_surrogates.py:133,152,176`, `test_worklist_safety.py:254`. Architect decision R-013.

### LED-2026-10-08-data-safety-batch.7 — US-002/US-003 reconciliations are traceability acts, not new nodes
- **Requirement:** HLR-007, HLR-008, LLR-007.1, LLR-007.2, LLR-008.1, LLR-008.2
- **Date:** 2026-10-08
- **What changed:** US-002/003 are derived as "write one new node (AT-044) and reconcile already-declared ids to already-existing nodes", not as new test work.
- **Why:** an id that names an on-disk node guarding the behaviour it declares is a traceability reconciliation — matching the record to the suite — not new code. AT-025b's behaviour is already tested under `LLR-N13.1.5`; AT-041/042 are realised under other names; AT-033/034/035 belong to the deferred US-N14 and are retired, not realised. Minting dedicated nodes for those would duplicate arms and re-open C-18's drift.
- **Evidence:** `tests/test_repair_cycles.py:501,543,575,624,664` (LLR-N13.1.5); `tests/test_repair_layout.py:274,441,456` (AT-041/042); the canonical attribution `AT-033/034/035 → US-N14` (`#D23`, deferred) settled at the P0 gate, `.dev-flow/BACKLOG.md`.

### LED-2026-10-08-data-safety-batch.8 — B1 — R4's modal keys named in LLR-003.1 and HLR-003
- **Requirement:** HLR-003, LLR-003.1
- **Date:** 2026-10-08
- **What changed:** LLR-003.1's statement and HLR-003's observable outcome now name the guard's keys — `s` save, `d` discard, `esc` stay — bound from the `draft` modal scope.
- **Why:** ruling R4 fixed the keys, but LLR-003.1 named only the three outcome tokens and HLR-003's observable outcome named only the outcomes; a reviewer could not read WHICH key produced WHICH answer. Finding B1 (R4 missing).
- **Evidence:** ruling R4 in `VERDICT-b36-prototype-2026-10-08.md`; the `draft` modal scope.

### LED-2026-10-08-data-safety-batch.9 — M1 — FieldCommitted census is 17 lines, not 10 references
- **Requirement:** LLR-001.3
- **Date:** 2026-10-08
- **What changed:** the LLR-001.3 pre-state census is restated as 17 grep lines (10 code sites + 7 docstring/test-name lines); the docstrings, the comment and the test name `test_g6b_field_committed_...` must be renamed in the same increment.
- **Why:** the earlier "10 references" listed only code sites; the grep returns 17 lines, so the 0-line post-state threshold is unmet unless the 7 non-code matches are renamed too. Finding M1.
- **Evidence:** `grep -rn "FieldCommitted\|field_committed" --include=*.py mapper tests` (2026-10-08): 17 lines.

### LED-2026-10-08-data-safety-batch.10 — M2 — §3.1 AT table added; AT-004/005 split by exit
- **Requirement:** §3 (HLR-001…009 acceptance layer)
- **Date:** 2026-10-08
- **What changed:** added the §3.1 AT table (id·story·surface·stimulus·assertion·RED today); AT-004/005 each name their exits (node change / leave map screen vs quit / follow a link); AT-002 asserts files-unchanged-before-`ctrl+s` AND written-once-after; AT-008 states its injected-delay predicate; AT ids declared batch-local.
- **Why:** the acceptance ids had no single view of stimulus/assertion/RED side, and AT-004/005 did not say which exits each covered. Finding M2.
- **Evidence:** each HLR's observable outcome and negative control.

### LED-2026-10-08-data-safety-batch.11 — M3 — R5 undo-while-dirty stated as AT-009; LLR-004.3 wording
- **Requirement:** HLR-004, LLR-004.3
- **Date:** 2026-10-08
- **What changed:** added AT-009 (with a pending draft, `u` undoes the last save and the draft's values remain); LLR-004.3 now says the draft's values are untouched, only the dirty markers recomputed against the restored stored values.
- **Why:** R5 says undo acts on what was written, not on the draft; the earlier wording ("re-diffing it against the restored values") implied the draft itself was re-diffed. Finding M3 (R5).
- **Evidence:** ruling R5 in `VERDICT-b36-prototype-2026-10-08.md`; `mapper/app.py:3517-3533` (`_pop_snapshot`).

### LED-2026-10-08-data-safety-batch.12 — M4 — §2.1–2.5 real content replaces the template guidance
- **Requirement:** HLR-001, HLR-007, HLR-008, HLR-009
- **Date:** 2026-10-08
- **What changed:** §2.1–2.5 now carry real content (product perspective, functions, single-operator users, constraints Textual 8.2.8 / Windows / 4-source-file cap / English UI, assumptions).
- **Why:** the fields held only italic template guidance; the constraints (Textual 8.2.8 `immediate=False`, Windows, the 4-source-file cap) are load-bearing for US-004 and were unstated. Finding M4.
- **Evidence:** P-6, P-7; ARQ increments Inc-1…Inc-4.

### LED-2026-10-08-data-safety-batch.13 — M4b — AT-041 reconciled; AT-042 partially realised
- **Requirement:** HLR-008, LLR-008.1
- **Date:** 2026-10-08
- **What changed:** AT-041 is reconciled to `tests/test_repair_layout.py:274` (`test_at_r12_pressing_help_presents_every_map_binding`); AT-042 is recorded PARTIALLY realised — its largest-set arm via `test_tc_r25` (`:441`, parametrised MAP/HOME), with the smallest-set (`app`) and no-scope-screen arms owed as new nodes in this batch; the wrong `tests/test_help_scope.py:139,147` citation is removed from §2.6 US-003.
- **Why:** `test_tc_r25` is parametrised `SCOPE_MAP`/`SCOPE_HOME` only, so it never drives `app` (2 rows); `test_tc_r26` is the foreign-scope negative, so AT-042's smallest-set and no-scope arms have no on-disk node; lines 139/147 are view-naming nodes, not AT-041/042 realisations. Finding M4b.
- **Evidence:** `tests/test_repair_layout.py:440-441,456`; AT-042's predicates at `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:4900-4904`.

### LED-2026-10-08-data-safety-batch.14 — m1 — `US-N14 (DEFERRED)` label
- **Requirement:** HLR-008
- **Date:** 2026-10-08
- **What changed:** `~~US-N14~~` → `US-N14 (DEFERRED)`.
- **Why:** the struck-id form `~~US-N14~~` is the deferral marker, not the live label; the live contract uses `US-N14 (DEFERRED)`. Finding m1.
- **Evidence:** canonical traceability table `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:6090`.

### LED-2026-10-08-data-safety-batch.15 — m2 — ledger seed line removed
- **Requirement:** HLR-001, HLR-007, HLR-008, HLR-009
- **Date:** 2026-10-08
- **What changed:** removed the "_No entries yet._" seed line from §7's fence.
- **Why:** the ledger now carries entries (LED-…1…7), so the seed line is stale and misleading. Finding m2.
- **Evidence:** `01-requirements-ledger.md` (LED-…1…7).

### LED-2026-10-08-data-safety-batch.16 — m3 — US-004 feasibility rewritten to the measured mechanism
- **Requirement:** HLR-009
- **Date:** 2026-10-08
- **What changed:** the feasibility block is rewritten from the refuted reflow hypothesis to the measured mechanism (`scroll_to` default `immediate=False` at `tests/test_help_scope.py:365`; fix `immediate=True` + settle assertion; four sites), and E ✗ → E ✓.
- **Why:** the intake's reflow hypothesis was refuted by the spike, yet the feasibility still stated it and left E ✗. Finding m3.
- **Evidence:** `spike/FLAKE-2-spike.md`; P-6, P-7; `tests/test_help_scope.py:365,367,371`.

### LED-2026-10-08-data-safety-batch.17 — m5 — scan note records both P0 and P1 flags
- **Requirement:** HLR-004
- **Date:** 2026-10-08
- **What changed:** the scan note now records both the P0 flag (`escape`) and the P1 flags (`token`, `form`, `escape`), all ordinary vocabulary, recorded anyway.
- **Why:** the note had collapsed to the P1 result and dropped the P0 `escape` flag. Finding m5.
- **Evidence:** scan runs 2026-10-08.

### LED-2026-10-08-data-safety-batch.18 — m6 — Inc-1 regression obligations noted in §5
- **Requirement:** LLR-001.3
- **Date:** 2026-10-08
- **What changed:** added an out-of-LLR note in §5: the reverse-census re-point of the three test files that post `FieldCommitted` (`tests/test_inspector.py`, `tests/test_g6_store_surrogates.py`, `tests/test_worklist_safety.py`) and the whole-seat pin `tests/test_key_dispatch.py:137` are owed in Inc-1.
- **Why:** those test-side re-points are regression obligations of the A3 removal and the seat change, but they are not LLRs, so they were invisible to the validation strategy. Finding m6.
- **Evidence:** `tests/test_inspector.py:103,162`, `tests/test_g6_store_surrogates.py:133,152,176`, `tests/test_worklist_safety.py:254`, `tests/test_key_dispatch.py:137`.

### LED-2026-10-08-data-safety-batch.19 — pre-gate correction of ledger pairings (validator V26)
- **Requirement:** HLR-001
- **Date:** 2026-10-08
- **What changed:** the **Requirement** field of entries .12–.18 was re-pointed from section names (§2, §5, §6.3, the ledger itself) and story rows (US-003, US-004 are table rows, not headings) to the HLR/LLR headings that carry them, and each of those requirements now lists the entry in its **Ledger** field.
- **Why:** V26 pairs requirement HEADINGS with entries in both directions; an entry naming a section pairs with nothing. Done the same day, before the P1 gate closed, by the orchestrator; no entry's content changed.
- **Evidence:** `devflow-validate.py --brief` V26 before (2 BLOCK) and after.
