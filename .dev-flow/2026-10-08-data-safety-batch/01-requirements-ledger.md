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

### LED-2026-10-08-data-safety-batch.20 — ARCH-B1 — the draft updates on every `Input.Changed`
- **Requirement:** HLR-001, LLR-001.2
- **Date:** 2026-10-08
- **What changed:** HLR-001 and LLR-001.2 now require the draft to update on every `Input.Changed` (each keystroke), not only on blur/submit; added AT-010 (type in a field then `ctrl+s` without leaving it ⇒ the typed text is in both files).
- **Why:** `ctrl+s` reaches the screen while focus is still in the field (`Input.BINDINGS` has no `ctrl+s` under Textual 8.2.8), so a draft that updated only on blur would save without the typed text and hide `● unsaved` until blur; the approved prototype drafted on every keystroke.
- **Evidence:** `mapper/widgets/inspector.py:351-352` (`on_input_blurred` → `_commit`), `:347-349` (`on_input_submitted` → `_commit`); `mapper/keymap.py:137-263` (no `ctrl+s` seat row).

### LED-2026-10-08-data-safety-batch.21 — ARCH-B2/QA-B2 — AT surfaces re-keyed; observation stated once
- **Requirement:** HLR-004
- **Date:** 2026-10-08
- **What changed:** every §3.1 AT surface is now keys, screens and files only (no internal symbol names); the observation method is stated once in §5.1 (`obs` — Textual `App.run_test` pilot pressing real keys; sha256 of `.mmd` and `_nodos.yml` before/after; "written once" = the hash pair changes exactly once) and referenced per AT; each AT keeps a RED-today cell.
- **Why:** the AT table named internals (`action_save_draft`, `on_input_submitted`, `_pop_snapshot`, `undo_stacks`) and no observation method, so the WHAT was written against the HOW.
- **Evidence:** §3.1 table; §5.1 observation block.

### LED-2026-10-08-data-safety-batch.22 — QA-B1 — §3.1 rows for US-002/US-003
- **Requirement:** HLR-007, HLR-008
- **Date:** 2026-10-08
- **What changed:** added §3.1 rows for AT-044 and AT-025b (US-002) and for US-003's ids (AT-041, AT-042, AT-033/034/035), declared `inspection — reconciliation` except AT-042's two new arms (LLR-008.3).
- **Why:** US-002 had no §3.1 rows for AT-044/AT-025b, and US-003's ids had no rows at all.
- **Evidence:** §3.1 table; `tests/test_repair_layout.py:274,441,456`.

### LED-2026-10-08-data-safety-batch.23 — SEC-M1 — failed save resolves by where it fell
- **Requirement:** HLR-004, LLR-004.2
- **Date:** 2026-10-08
- **What changed:** the failed-save requirement is split into three cases by where the failure falls in `MapStore.save`'s two-phase write: (a) before the first replace → nothing on disk, keep the draft; (b) after both replaces (e.g. `_reindex`) → treat as saved, clear the draft, warn; (c) between the replaces (torn pair) → reload from disk and warn.
- **Why:** a raise after the replaces leaves new data on disk while the old spec restored memory and kept the draft, so the next structural save silently reverted the committed write.
- **Evidence:** `mapper/store.py:809` (`save`), `:825-836` (`dump`/`_build_sidecar`/`_text_hash`/`safe_dump`), `:846-847` (`_write_tmp`), `:848-849` (the two replaces), `:850` (`_reindex` call), `:926` (`_reindex` def).

### LED-2026-10-08-data-safety-batch.24 — SEC-M2 — guard title is `plain()`-composed, ESC negative added
- **Requirement:** LLR-003.1
- **Date:** 2026-10-08
- **What changed:** the guard title is composed of `darkside.plain(<map id>)` + `darkside.plain(<node title as stored>)`, painted `markup=False`; added the ESC-payload negative (AT-015).
- **Why:** `markup=False` builds `Content(text)`, which strips BEL/BS/VT/FF/CR only (`textual/content.py:56-62`); ESC (0x1B) passes, so a file-derived title can reach the terminal with a control effect. `plain()` strips every control code (`darkside.py:517-547`, C0 includes 0x1B).
- **Evidence:** `textual/content.py:56-62` (`_STRIP_CONTROL_CODES = [7, 8, 11, 12, 13]` — no 0x1B); `mapper/darkside.py:517-547` (`COERCION_RANGES` C0 `0x000B-0x001F`).

### LED-2026-10-08-data-safety-batch.25 — SEC-M3 — the link guard is unconditional
- **Requirement:** LLR-003.4
- **Date:** 2026-10-08
- **What changed:** LLR-003.4 states the link guard is unconditional (R6), never deferred; the PDR/UX deferral is removed.
- **Why:** R6 already rules the link guard unconditional; the deferral would let a quit walk save a stale lower screen.
- **Evidence:** ruling R6 in `VERDICT-b36-prototype-2026-10-08.md`; `mapper/app.py:3566` (`action_open_ficha` pushes a second `MapScreen`).

### LED-2026-10-08-data-safety-batch.26 — ARCH-M3 — structural writes open the guard first
- **Requirement:** HLR-003, LLR-003.6
- **Date:** 2026-10-08
- **What changed:** any structural write (`a` add child, `x` archive, `A` add attachment, `X` remove attachment) with a pending draft opens the guard first; new LLR-003.6 and AT-014.
- **Why:** no rule covered a draft whose node a structural write removes; with `a` the guard would fire after the write, which is too late.
- **Evidence:** `mapper/keymap.py:172,174,176,177` (the four seat rows); `mapper/app.py:4545` (`action_add_child`), `:4592` (`action_archive`), `:3487` (`action_add_attachment`), `:3490` (`action_remove_attachment`).

### LED-2026-10-08-data-safety-batch.27 — ARCH-M4/QA-M4 — keymap symbols declared, pins listed
- **Requirement:** LLR-001.4, LLR-003.1
- **Date:** 2026-10-08
- **What changed:** declared the keymap symbols touched — `SCOPE_DRAFT = "draft"`, `GROUP_SCOPE["draft"] = SCOPE_DRAFT`, `MODAL_SCOPES` widened to include `SCOPE_DRAFT`, and the map-scope `ctrl+s` row — and listed the census pins as Inc-1 obligations in §5.
- **Why:** the keymap symbols touched were undeclared, and the census missed the whole-seat and per-scope pins.
- **Evidence:** `mapper/keymap.py:60-80` (`GROUP_SCOPE`), `:269` (`MODAL_SCOPES`), `:137-263` (`KEYMAP`); pins `tests/test_keymap.py:34-44,63,87-95,298`, `tests/test_inc9.py:695-703,707`.

### LED-2026-10-08-data-safety-batch.28 — ARCH-M5 — AT-042's two arms are a test LLR
- **Requirement:** HLR-008, LLR-008.1, LLR-008.3
- **Date:** 2026-10-08
- **What changed:** LLR-008.1 is now inspection-only (AT-041 and AT-042's largest-set arm reconcile); AT-042's two missing arms moved to a new test LLR-008.3 with command, threshold, negative control and target file.
- **Why:** LLR-008.1 asked for two new nodes but was labelled `inspection`, which cannot carry a test node.
- **Evidence:** `tests/test_repair_layout.py:440-441` (`test_tc_r25` parametrised MAP/HOME only), `:456` (`test_tc_r26` foreign-scope negative).

### LED-2026-10-08-data-safety-batch.29 — ARCH-M6 — ARQ D2 candidates listed as Inc-1 obligations
- **Requirement:** LLR-001.3
- **Date:** 2026-10-08
- **What changed:** added the ARQ D2 persistence-oracle census candidates to the §5 Inc-1 regression obligations.
- **Why:** the candidates were dropped from the census, so the draft model's re-point of their `↵`-on-inspector-field oracles was invisible.
- **Evidence:** `tests/test_en7.py:62-80,182`, `tests/test_app.py:31`, `tests/test_fold.py:1016,1253`, `tests/test_inc9d.py:124-487`.

### LED-2026-10-08-data-safety-batch.30 — QA-M1 — AT-044's RED names its mutation
- **Requirement:** HLR-007
- **Date:** 2026-10-08
- **What changed:** AT-044's RED names the mutation it must redden on: binding `?` in the help seat, or letting the help legend inherit the app chord, either of which opens a second legend.
- **Why:** the RED was an absent node, not a counterfactual.
- **Evidence:** `mapper/keymap.py:269` (`MODAL_SCOPES = (SCOPE_PALETTE, SCOPE_HELP)`), `:228-238` (the help seat has no `question_mark`).

### LED-2026-10-08-data-safety-batch.31 — QA-M2 — one AT per exit; lower-screen quit AT added
- **Requirement:** HLR-003, LLR-003.5
- **Date:** 2026-10-08
- **What changed:** AT-004/005 split into one AT per exit (AT-004 node change, AT-005 leave map screen, AT-011 follow a link, AT-012 quit), and added AT-013 for quitting with a lower map screen holding a draft.
- **Why:** AT-004/005 were compound (two exits each), and no AT covered quit with a lower `MapScreen` holding a draft.
- **Evidence:** §3.1 table; `mapper/app.py:4937-4938` (`action_quit` exits immediately).

### LED-2026-10-08-data-safety-batch.32 — QA-M3 — deflake threshold re-stated; AT-008 re-labelled
- **Requirement:** HLR-009
- **Date:** 2026-10-08
- **What changed:** HLR-009's threshold is now "the injected-delay arm GREEN, its RED an executed counterfactual"; AT-008 is re-labelled a test-instrument check (the acceptance is of the instrument's determinism, not product behaviour).
- **Why:** a single-run threshold cannot show a deflake, and one committed test cannot be both RED and GREEN.
- **Evidence:** `spike/red_green_flake2.py` — RED 2/2 on the current step, GREEN 2/2 with `immediate=True` (spike, 2026-10-08).

### LED-2026-10-08-data-safety-batch.33 — QA-M5/ARCH-m12 — AT-009 RED re-stated against the re-diff
- **Requirement:** HLR-004, LLR-004.3
- **Date:** 2026-10-08
- **What changed:** AT-009 and LLR-004.3's RED re-stated against the dirty-marker re-diff after `u` (markers recomputed against the restored stored values), not against the hypothetical absent draft.
- **Why:** the RED reason was hypothetical (the draft does not exist today, so "discards the draft" could not redden).
- **Evidence:** `mapper/app.py:3517-3533` (`_pop_snapshot` replaces `self.graph` wholesale, no marker re-diff).

### LED-2026-10-08-data-safety-batch.34 — SEC-m1 — "atomic" reworded
- **Requirement:** HLR-004
- **Date:** 2026-10-08
- **What changed:** "atomic" in §1.2, §2.2 and the HLR-004 title reworded to "two-phase whole-graph write with torn-pair detection" / "whole-graph write".
- **Why:** "atomic" overstates the store, which does a two-phase write with torn detection and no fsync.
- **Evidence:** `mapper/store.py:846-850` (two temp writes, then two replaces, then `_reindex`).

### LED-2026-10-08-data-safety-batch.35 — SEC-m2 — failed `u` while a draft is pending is residual A-10
- **Requirement:** LLR-004.3
- **Date:** 2026-10-08
- **What changed:** recorded a failed `u` while a draft is pending as a residual (risk A-10) in LLR-004.3's boundary catalog.
- **Why:** the case was unspecified.
- **Evidence:** `mapper/app.py:3517-3533`.

### LED-2026-10-08-data-safety-batch.36 — SEC-m3 — structural-write draft-exclusion folded into AT-014
- **Requirement:** HLR-003, LLR-003.6
- **Date:** 2026-10-08
- **What changed:** folded "structural writes leave draft values out of the file" into ARCH-M3's AT-014.
- **Why:** no AT asserted structural writes leave draft values out of the files.
- **Evidence:** AT-014 in §3.1.

### LED-2026-10-08-data-safety-batch.37 — SEC-m4 — the guard names the map
- **Requirement:** LLR-003.1
- **Date:** 2026-10-08
- **What changed:** the guard title names the map (`darkside.plain(map_id)` + `darkside.plain(node title)`); a typed-ahead `d` discard is accepted as a residual (loses a draft, never writes).
- **Why:** the guard should name the map the operator is about to leave; a typed-ahead `d` can discard.
- **Evidence:** LLR-003.1 statement.

### LED-2026-10-08-data-safety-batch.38 — ARCH-m8 — `state` shown value is `STATE_VALUES[active]`
- **Requirement:** LLR-002.1
- **Date:** 2026-10-08
- **What changed:** LLR-002.1 states the shown value of `state` is `STATE_VALUES[active]`, where `active` is the stored state's index or 0 for an unknown state.
- **Why:** "shown value = `plain(stored)`" was wrong for `state`, whose unknown value renders as index 0 (`ok`).
- **Evidence:** `mapper/widgets/inspector.py:27` (`STATE_VALUES`), `:138` (`active = STATE_VALUES.index(...) if ... else 0`).

### LED-2026-10-08-data-safety-batch.39 — ARCH-m9 — attachment chips excluded from the draft
- **Requirement:** HLR-006
- **Date:** 2026-10-08
- **What changed:** HLR-006 states attachment chips are not inspector fields (their edits route through prompts) and are excluded from the draft (ARQ D5).
- **Why:** chips are in the inspector but excluded from the draft model.
- **Evidence:** ARQ §D5; `mapper/widgets/inspector.py:169-195` (attachment chips).

### LED-2026-10-08-data-safety-batch.40 — ARCH-m10/QA-m3 — the seven renames are required
- **Requirement:** LLR-001.3
- **Date:** 2026-10-08
- **What changed:** LLR-001.3's statement now requires the seven docstring/test-name lines that mention `FieldCommitted` to be renamed in the same increment.
- **Why:** the statement did not require the renames its 0-reference threshold needs.
- **Evidence:** `tests/test_g6_store_surrogates.py:8,105,109,111,113`, `tests/test_inspector.py:61`, `mapper/app.py:3345`.

### LED-2026-10-08-data-safety-batch.41 — ARCH-m11 — A-11 added; crash/kill excluded
- **Requirement:** HLR-003
- **Date:** 2026-10-08
- **What changed:** added A-11 to §6.3 and excluded a killed terminal/crash from "every exit" in HLR-003 (R1: loss accepted, nothing written).
- **Why:** "every exit" did not exclude a killed terminal, which no guard can cover.
- **Evidence:** §6.3 A-11; HLR-003 statement.

### LED-2026-10-08-data-safety-batch.42 — QA-m1 — §5.1 Layer-B row includes AT-009
- **Requirement:** HLR-004
- **Date:** 2026-10-08
- **What changed:** the §5.1 Layer-B row for US-001 now includes AT-009 (and the new AT-010…AT-015).
- **Why:** the row stopped at AT-007 and omitted AT-009.
- **Evidence:** §5.1 table.

### LED-2026-10-08-data-safety-batch.43 — QA-m2 — AT-002's failing-store arm names its injection
- **Requirement:** HLR-004
- **Date:** 2026-10-08
- **What changed:** AT-002's failing-store arm now names its injection method — monkeypatching the screen's store `save` (precedent `tests/test_g6_store_surrogates.py`).
- **Why:** the arm needed an injection method to be executable.
- **Evidence:** `mapper/app.py:252-253` (`write = store.create if new else store.save`); precedent `tests/test_g6_store_surrogates.py`.

### LED-2026-10-08-data-safety-batch.44 — QA note — re-pointed tests drive typing + `ctrl+s`
- **Requirement:** LLR-001.3
- **Date:** 2026-10-08
- **What changed:** the re-pointed tests (`tests/test_g6_store_surrogates.py:150,176,203,331`, `tests/test_inspector.py:103,162`, `tests/test_worklist_safety.py:254`) must drive typing + `ctrl+s` through the pilot, not post messages; listed in §5.
- **Why:** a re-pointed test that posts a message bypasses the draft and would not test the shipped surface.
- **Evidence:** §5 Inc-1 obligations.

### LED-2026-10-08-data-safety-batch.45 — R2-N1 — failed save classifies by disk state, not by exception
- **Requirement:** HLR-001, HLR-003, HLR-004, LLR-001.4, LLR-003.2, LLR-003.3, LLR-003.4, LLR-003.6, LLR-004.1, LLR-004.2
- **Date:** 2026-10-08
- **What changed:** the failed-save resolution (LLR-004.2) is re-classified by DISK state, not by which phase of `MapStore.save` raised: the sha256 of `.mmd` and `_nodos.yml` is taken before the save and re-taken on failure, and the three cases are (a) both unchanged → restore the graph, pop the snapshot, keep the draft, guard `stay`, error toast; (b) both changed → committed: keep the snapshot, clear the draft, warning toast, guard proceeds as `save`; (c) exactly one changed → reload from disk, keep the draft re-diffed against the reloaded values, keep the snapshot, guard `stay`, warning toast naming `ctrl+s` to repair, and if the reload raises, keep the in-memory graph and draft and refuse structural writes until a successful `ctrl+s`. LLR-001.4 stops mandating `_save_or_toast` for the draft save (its bool cannot distinguish the three cases). Reconciled HLR-004's acceptance and boundary, AT-002 (split into AT-002a/002b/002c), LLR-004.1's boundary and statement, the `save`-that-fails boundary rows of LLR-003.2–003.6, and the same wording in HLR-001's and HLR-003's boundary catalogs.
- **Why:** `save()` raises raw exceptions from every phase and `_save_or_toast` returns a bool (`app.py:229-258`), so no caller can tell "nothing on disk" from "committed" from "torn pair"; several places still said every failure keeps the draft and leaves no undo step. Disk state is the ground truth a caller can measure.
- **Evidence:** `mapper/store.py:809` (`save`), `:846-847` (`_write_tmp`), `:848-849` (the two replaces), `:850`/`:926` (`_reindex`); `mapper/app.py:229-258` (`_save_or_toast`); `docs/ARCHITECTURE.md` R-013 rationale amended.

### LED-2026-10-08-data-safety-batch.46 — R2-N2 — `mmd_tmp.replace` raising is case (a)
- **Requirement:** LLR-004.2
- **Date:** 2026-10-08
- **What changed:** a raise from `mmd_tmp.replace` (`store.py:848-849` — an antivirus or sync client holding the file on Windows) fits no phase of the old classification; under the disk rule it is case (a), because neither original changed.
- **Why:** the old "before the first replace" phrasing covered only failures before `_write_tmp`; a replace itself raising leaves both originals untouched and must resolve the same as any other nothing-on-disk failure.
- **Evidence:** `mapper/store.py:848-849`.

### LED-2026-10-08-data-safety-batch.47 — R2-QA-M1 — AT-010/AT-015 RED name their mutations
- **Requirement:** HLR-001, HLR-003
- **Date:** 2026-10-08
- **What changed:** AT-010's RED is restated against "draft updated on blur/submit only" (that mutation would save without the typed text), and AT-015's RED is restated against "title built without `plain()`" (that mutation lets ESC through), replacing the unbound-key / raw-ESC descriptions that were not discriminating counterfactuals.
- **Why:** a RED that names an unbound key or the shipped `markup=False` behaviour is a state, not a counterfactual the test can redden on.
- **Evidence:** §3.1 AT-010, AT-015 rows.

### LED-2026-10-08-data-safety-batch.48 — R2-QA-M2 — AT-013 is a Layer-A injection test; AT-005/014 one row per key
- **Requirement:** HLR-003, LLR-003.5
- **Date:** 2026-10-08
- **What changed:** AT-013 is re-declared a Layer-A injection test of LLR-003.5's defensive invariant (the lower `MapScreen`'s draft is reachable only by injecting it once R6 guards links, so it is not a black-box surface test); AT-005 is split into AT-005a (`q`) and AT-005b (`esc`), and AT-014 into AT-014a–AT-014d (`a`/`x`/`A`/`X`), each with its own RED.
- **Why:** a compound AT (two/four keys) is several tests wearing one id; a precondition unreachable through the shipped surface cannot be an acceptance test of that surface.
- **Evidence:** §3.1 AT-005a/005b, AT-013, AT-014a–014d rows; `mapper/app.py:4937-4938` (`action_quit`), `:3566` (`action_open_ficha`).

### LED-2026-10-08-data-safety-batch.49 — R2-QA-M3 — AT-015 listed under HLR-003; US-004's Layer-B exception declared
- **Requirement:** HLR-003, HLR-009
- **Date:** 2026-10-08
- **What changed:** AT-015 is listed in HLR-003's acceptance line (it was orphaned — defined in §3.1 but claimed by no HLR); §5.1 declares US-004's Layer-B exception (AT-008 accepts the determinism of the test instrument, not product behaviour) beside US-003's.
- **Why:** an acceptance id no HLR claims is invisible to the two-layer trace; US-004's exception was undeclared where US-003's was.
- **Evidence:** HLR-003 acceptance line; §5.1 Layer-B note.

### LED-2026-10-08-data-safety-batch.50 — R2-ARCH-NEW-2 — markers update without remounting; draft entries keyed to the sending node
- **Requirement:** LLR-001.2, LLR-002.2
- **Date:** 2026-10-08
- **What changed:** LLR-002.2 requires the dirty markers and the header to update without remounting the focused field (a per-keystroke `show()` → `_rebuild` remount destroys the focused `Input` and leaves a stale `Input.Changed`); LLR-001.2 requires each draft entry to be keyed to the node of the input that sent the change, never the re-pointed node.
- **Why:** a per-keystroke draft painted through a full remount would drop focus on every key, and a stale `Input.Changed` arriving after a re-point could write another node's draft.
- **Evidence:** `mapper/widgets/inspector.py` `_rows` overlay (LLR-002.1); the `Input.Changed` producer (ARCH-B1).

### LED-2026-10-08-data-safety-batch.51 — R2-ARCH-NEW-3 — the no-scope arm's expected set is stated and probed
- **Requirement:** LLR-008.3
- **Date:** 2026-10-08
- **What changed:** LLR-008.3 states the no-scope screen's expected set: it falls through the `HelpScreen` default (`scope=SCOPE_APP`, `mapper/screens/help.py:288`), so it presents `bindings_for(SCOPE_APP)` — 2 rows (`ctrl+p` palette, `?` legend), identical to the smallest-set arm; the two arms differ only by constructor path, not by expected set.
- **Why:** "a screen that declares no scope" was ambiguous about what it presents.
- **Evidence:** probe `python -c "from mapper.keymap import bindings_for, SCOPE_APP; print(bindings_for(SCOPE_APP))"` → 2 rows, `[('ctrl+p','palette'), ('?','legend')]` (2026-10-08); `mapper/screens/help.py:288`.

### LED-2026-10-08-data-safety-batch.52 — R2-N3/N4/N5 — draft/snapshot in (c), pop scoped to (a), stale `.tmp` residual
- **Requirement:** LLR-004.2
- **Date:** 2026-10-08
- **What changed:** the draft and snapshot are kept in case (c) and the snapshot pop is scoped to case (a), folded into R2-N1's disk classification; the stale `.tmp` file left by a failed `_write_tmp` is recorded as a residual (overwritten by the next save).
- **Why:** these three minor findings are all consequences of the same re-classification and needed no separate rule.
- **Evidence:** LLR-004.2's table and residual note; `mapper/store.py:805-807` (`_write_tmp`).

### LED-2026-10-08-data-safety-batch.53 — R2-minors — shipped-surface keys, RED mutations, §6.3 wording, residual
- **Requirement:** HLR-003, HLR-004, HLR-005, HLR-006, LLR-003.1, LLR-007.1, LLR-009.2
- **Date:** 2026-10-08
- **What changed:** HLR-004/005/006 "Shipped surface" lines re-keyed to keys, screens and files (no `action_save_draft`/`undo_stacks`/`on_input_submitted`/`DsSegmented`); LLR-007.1's control names the mutation it reddens on (binding `?` in the help seat) instead of "absent node"; LLR-009.2's threshold drops "RED before, GREEN after" for one node (the committed arm is GREEN, its RED is the counterfactual); AT-009 gains focus-out and the `● unsaved (N)` observable; AT-011 names the link key (`↵`); AT-012/013 name the exit outcome; AT-015's observation is a scan of the rendered title for 0x1B; §6.3 "atomic" reworded; the typed-ahead `d` residual stated (§6.3 A-13); `plain` re-cited at `darkside.py:550`.
- **Why:** surfaces still named internals; a control that says "absent node" names no counterfactual; one committed node cannot be both RED and GREEN; and the remaining minors were stale citations and wording.
- **Evidence:** `mapper/darkside.py:550` (`def plain`); `mapper/keymap.py:269` (`MODAL_SCOPES`); `spike/red_green_flake2.py`.

### LED-2026-10-08-data-safety-batch.54 — R3-SAVE — one failure rule replaces the three-case disk table
- **Requirement:** HLR-004, LLR-004.1, LLR-004.2, LLR-001.4
- **Date:** 2026-10-08
- **What changed:** LLR-004.2 now reloads the map from disk on any failed save, keeps the draft re-diffed against the reloaded values, discards the pushed snapshot in memory and never writes; a raising reload restores the pre-save graph in memory. HLR-004, LLR-004.1, LLR-001.4 and A-10 reconciled; the guard rows of LLR-003.2–003.6 now read "reload, then `stay`".
- **Why:** Round 3 found the disk-hash classification unsound (identical-byte `.mmd` rewrites, external edits, a pop that writes, a lock with no exit); the operator ruled "Simplificar y seguir (Recomendado)" at the P1 soft cap.
- **Evidence:** `mapper/app.py:1623` (`store.load` entry), `mapper/store.py:698-700` (missing sidecar), `mapper/mermaid.py:131-155` (dump writes edges and titles only), `mapper/app.py:3530` (`_pop_snapshot` writes).


### LED-2026-10-08-data-safety-batch.55 — R3-SAVE (guard rows) — every guard's failing `save` reloads, then `stay`
- **Requirement:** HLR-003, LLR-003.2, LLR-003.3, LLR-003.4, LLR-003.5, LLR-003.6
- **Date:** 2026-10-08
- **What changed:** The error boxes of LLR-003.2/.3/.4/.6 and the previously unchecked one of LLR-003.5 now apply LLR-004.2's single rule.
- **Why:** R3-SAVE removed the "committed" case the old wording depended on; LLR-003.5's failing save at quit was unspecified (ARCH-R3-3).
- **Evidence:** 02-review.md Round 3.


### LED-2026-10-08-data-safety-batch.56 — R3-QA-M1 — the fault-injection ATs collapse into one declared Layer-A arm
- **Requirement:** HLR-004
- **Date:** 2026-10-08
- **What changed:** AT-002a/b/c become one AT-002a, declared a Layer-A fault-injection test with two arms (zero files written, both files written) and two named mutations; AT-002b and AT-002c are retired with the three-case table.
- **Why:** The rows named internal store symbols (blocker (d)) and the cases they encoded no longer exist.
- **Evidence:** 02-review.md Round 3.


### LED-2026-10-08-data-safety-batch.57 — R3-QA-M2 / R3-minors — one named mutation per guard AT; observations; surfaces
- **Requirement:** HLR-002, HLR-003, HLR-007
- **Date:** 2026-10-08
- **What changed:** AT-004, AT-005a/b, AT-011, AT-012, AT-014a–d name the mutation that reddens them; AT-005 observes `len(app.screen_stack)`, AT-012 `app.is_running`; §5.1 lists AT-002a/AT-013 as Layer-A; HLR-002 and HLR-007 surfaces no longer name internal classes.
- **Why:** "Feature absent" is not a counterfactual (C-40); surfaces must name keys, screens and files.
- **Evidence:** 02-review.md Round 3.

### LED-2026-10-08-data-safety-batch.58 — R4 (operator: 'Aplicar y verificar ligero') — reload re-establishes the view; wording; residuals A-14/A-15
- **Requirement:** LLR-004.2
- **Date:** 2026-10-08
- **What changed:** LLR-004.2's reload re-establishes the view by the screen's own load path (nav rebuilt, load warnings surfaced, focus cleared, cursor kept or moved to root), drops a draft entry whose node is gone with a warning, and scopes "no write" to the map files (the index rebuild is a cache refresh); §5.1's obs paragraph names AT-002a's two arms; AT-011 observes stack depth; AT-009 names its mutation; AT-013 leaves the Layer-B list; residuals A-14 and A-15 recorded.
- **Why:** P2 round 4 (architect and security majors converged: swapping `self.graph` alone leaves `NavigationModel`, focus and load warnings stale; qa major: stale three-case text). Applied by the orchestrator under the operator's ruling at the cap.
- **Evidence:** `mapper/app.py:1622-1636`, `:270-271`, `:3528-3529`, `:3912-3914`; `mapper/store.py:783`, `:926-965`.
