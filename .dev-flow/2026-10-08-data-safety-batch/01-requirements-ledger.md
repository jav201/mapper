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
