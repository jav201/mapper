# Review — mapper — Batch 2026-10-08-data-safety-batch

> Phase 2 artifact. Reviewers (in parallel, read-only, HEAD `b74325a`): `architect` ∥ `qa-reviewer` ∥ `security-reviewer` (always in `full`; trigger C6 also fired). Consolidated by the orchestrator, which owns the dispositions (standing autonomous authorization, 2026-10-08).

## ✅ Verdict (read first)

- **Gate:** `iterate-to-refine` → Phase 1 (blockers present, and requirement-defect majors)
- **Out-of-scope findings:** 2 named and routed below (B-75, B-84 — adjacent, unchanged by this batch)
- **Findings:** 4 blocker · 10 major · 14 minor (after de-duplication across lenses)
- **shall/should check:** ✓ clean (all three lenses)
- **Two-layer (blockers):** ✗ US-002 has no §3.1 rows (QA-B1); ATs name internal symbols and no observation method (QA-B2 = ARCH-B2)
- **Census (change-first):** done — best-effort + gate-confirmed (architect C-26 table; QA supersession list)
- **Security:** ⚠ 2 major requirement defects (SEC-M1 failed-save disk/memory divergence, SEC-M2 ESC through `markup=False`) + 1 conditional
- **Evidence checklists (architect / qa / security):** ✓ all three returned complete checklists

---

## Detail (reference)

### Findings

| ID | Reviewer | Severity | Area / Req | What | Disposition (orchestrator) | Status |
|----|----------|----------|------------|------|----------------|--------|
| ARCH-B1 | architect | blocker | HLR-001/002, LLR-001.2, IFC | The draft updates only on blur/submit; `ctrl+s` reaches the screen while focus is still in the field (`Input.BINDINGS` has no `ctrl+s`, Textual 8.2.8), so "type, then `ctrl+s`" saves without the typed text; `● unsaved` hides until blur. The approved prototype drafted on every keystroke (`Input.Changed`) | The draft SHALL update on every `Input.Changed`; add an AT "type then `ctrl+s` without leaving the field" | → P1 |
| ARCH-B2 = QA-B2 | architect, qa | blocker | §3.1, HLR-004 | ATs name internals (`action_save_draft`, `on_input_submitted`, `_pop_snapshot`, `undo_stacks`) and no observation method | Re-key every AT surface to keys, screens and files; observation = Textual `run_test` pilot + sha256 of `.mmd` and `_nodos.yml` before/after; "written once" = the hash sequence changes exactly once | → P1 |
| QA-B1 | qa | blocker | US-002/US-003, §3.1 | No §3.1 rows for AT-044, AT-025b; US-003's ids have no rows | Add rows; US-003 rows declared `inspection — reconciliation` except AT-042's new arms (see ARCH-M5) | → P1 |
| SEC-M1 | security | major | HLR-004, LLR-004.2 | A raise after the replaces (`store.py:832-835`; `_reindex` `:926`) leaves new data on disk while the spec restores memory and keeps the draft → silent revert on the next structural save | Split: failure before the first replace → nothing on disk, keep draft; failure after both replaces (e.g. `_reindex`) → treat as saved, clear draft, warn; failure between the replaces (torn pair) → reload from disk and warn | → P1 |
| SEC-M2 | security | major | LLR-003.1 | `markup=False` builds `Content(text)`, which strips BEL/BS/VT/FF/CR only (`textual/content.py:56-62`); ESC passes | Guard title = `darkside.plain(<map id>)` + `darkside.plain(<node title as stored>)`, painted `markup=False`; add an ESC-payload negative | → P1 |
| SEC-M3 | security | major→minor | LLR-003.4 | If the link guard were waived, the quit walk could save a stale lower screen | R6 already rules the link guard unconditional; LLR-003.4 must stop deferring it (= ARCH-m7) | → P1 |
| ARCH-M3 | architect | major | HLR-003, LLR-003.2, 004.3 | No rule for a draft whose node a structural write removes (`action_archive`, `x`, `A`, `X`); with `a` the guard would fire after the write | Any structural write (`a`, `x`, `A`, `X`, archive) with a pending draft SHALL open the guard first; covers SEC-m3 too | → P1 |
| ARCH-M4 = QA-M4 | architect, qa | major | LLR-001.4, 003.1, §5 | Keymap symbols touched are undeclared; census misses `tests/test_keymap.py:34-44,63,87-95,298`, `tests/test_inc9.py:695-703,707` | Declare `SCOPE_DRAFT`, `GROUP_SCOPE`, `MODAL_SCOPES`, the map-scope `ctrl+s` row; list every pin as an Inc-1 obligation | → P1 |
| ARCH-M5 | architect | major | LLR-008.1 | Asks for two new nodes but is `inspection` | Split into a `test` LLR with command, threshold, negative control, target file | → P1 |
| ARCH-M6 | architect | major | §5 | ARQ D2 candidates dropped: `tests/test_en7.py:62-80,182`, `tests/test_app.py:31`, `tests/test_fold.py:1016,1253`, `tests/test_inc9d.py:124-487` (`enter` on inspector fields) | Add to the Inc-1 regression obligations | → P1 |
| QA-M1 | qa | major | AT-044 | RED is an absent node, not a counterfactual | Name the mutation it must redden on (bind `question_mark` in the help seat / drop the modal exclusion) | → P1 |
| QA-M2 | qa | major | AT-004/005, LLR-003.5 | Compound ATs; no AT for quit with a lower `MapScreen` holding a draft | One AT per exit (or parametrised, each arm RED today); add the lower-screen quit AT | → P1 |
| QA-M3 | qa | major | HLR-009, AT-008 | Single-run threshold cannot show a deflake; one committed test cannot be RED and GREEN | Threshold = the injected-delay arm GREEN, its RED recorded as an executed counterfactual (`spike/red_green_flake2.py`); AT-008 re-labelled a test-instrument check | → P1 |
| QA-M5 = ARCH-m12 | qa, architect | major | LLR-004.3, AT-009 | RED reason is hypothetical | Re-state the control against the dirty-marker re-diff after `u` | → P1 |
| SEC-m1 | security | minor | §1.2, HLR-004 | "Atomic" overstates the store (two-phase write + torn detection, no fsync) | Reword | → P1 |
| SEC-m2 | security | minor | LLR-004.3 | Failed `u` while a draft is pending is unspecified | Record as residual A-10 | → P1 |
| SEC-m3 | security | minor | — | No AT that structural writes leave draft values out of the file | Folded into ARCH-M3's AT | → P1 |
| SEC-m4 | security | minor | LLR-003.1 | Guard should name the map; a typed-ahead `d` can discard | Name the map (SEC-M2); typed-ahead discard accepted as a residual (loses a draft, never writes) | → P1 |
| ARCH-m8 | architect | minor | LLR-002.1 | "Shown value" wrong for `state` (index 0 for unknown) | Shown value of `state` = `STATE_VALUES[active]` | → P1 |
| ARCH-m9 | architect | minor | HLR-006 | Attachment chips are in the inspector but excluded (ARQ D5) | State the exclusion | → P1 |
| ARCH-m10 = QA-m3 | architect, qa | minor | LLR-001.3 | Statement does not require the 7 renames its threshold needs | Add them to the statement | → P1 |
| ARCH-m11 | architect | minor | §6.3, HLR-003 | A-11 missing; "every exit" does not exclude a killed terminal | Add A-11; exclude crash/kill explicitly (R1: loss accepted, nothing written) | → P1 |
| QA-m1 | qa | minor | §5.1 | Layer-B row omits AT-009 | Fix the range | → P1 |
| QA-m2 | qa | minor | AT-002 | Failing-store arm needs an injection method | Split; injection = monkeypatch of `app.store.save` (precedent `tests/test_g6_store_surrogates.py`) | → P1 |
| — | qa | note | `tests/test_g6_store_surrogates.py:150,176,203,331`, `tests/test_inspector.py:103,162`, `tests/test_worklist_safety.py:254` | Re-pointed tests must drive typing + `ctrl+s` through the pilot, not post messages | Inc-1 obligation | → P1 |

### Out of scope (routed)

| ID | Item | Routed to |
|---|---|---|
| OOS-1 | B-84 `.tmp` hard-link write-through (`store.py:806-807`) — unchanged by this batch | `.dev-flow/BACKLOG.md` B-84 (already open) |
| OOS-2 | B-75 check-then-write on `create` (`store.py:839-855`) — not on the edit path | `.dev-flow/BACKLOG.md` B-75 (already open) |

### Confirmed, no finding

- `ctrl+s` is not XOFF under Textual's drivers: Linux/macOS raw mode clears `IXON|IXOFF` (`textual/drivers/linux_driver.py:343-350`, applied `:267-268`, `tcsetattr` `:278`; inline driver `:272-279`); Windows sets `ENABLE_VIRTUAL_TERMINAL_INPUT` only (`win32.py:179`). Residual: flow control in outer layers (serial, tmux/screen with `ixon`) is out of scope.
- The `FieldCommitted` census (17 lines, 10 code sites) and the four `scroll_to` sites are correct.
- All HLR/LLR statements use `shall`; derivation US→HLR→LLR is complete.

### Evidence checklists

- **architect:** ✓ derivation, ✓ keywords, ✓ reverse census (C-26) table, ✓ requirement-defect classification per finding.
- **qa-reviewer:** ✓ testability, ✗ two-layer (QA-B1/B2), ✓ supersession census, ✓ falsifiability per AT.
- **security-reviewer:** ✓ what/where/why/fix per finding, ✓ severity, ✓ no secrets or user paths, ✓ explicit verdict, n/a new tools.
