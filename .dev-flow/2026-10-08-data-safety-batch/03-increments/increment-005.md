# Increment 005 — Inc-1c (UX-1 conditions) and Inc-2 (every other exit) — US-001

| Field | Value |
|---|---|
| Batch | `2026-10-08-data-safety-batch` |
| Increments | **Inc-1c** — UX-1 conditions M1, M2 + header colour (operator R8) + single failed-save toast · **Inc-2** — design rows 2.1–2.4 (leave, link, quit, structural writes) |
| Requirement(s) | HLR-002 · LLR-002.2 · HLR-003 · LLR-003.3 · LLR-003.4 · LLR-003.5 · LLR-003.6 · HLR-004 · LLR-004.2 · HLR-005 · LLR-005.2 · AT-005a/b · AT-011 · AT-012 · AT-013 · AT-014a–d · PDR conditions C1, C6, C10, C14 (Inc-2 parts) |
| Base | `6676585` (Inc-1b + Inc-4 integrated, reviews recorded) → `5ad158e` |
| Method | **Ten small `deepseek/deepseek-v4-pro` units** (U1–U10), each one `opencode run` in a fresh session with a 15-min watchdog, one change + one test + its own RED proof; the orchestrator (Claude Opus 5.5) verified each unit with the census files before committing it and chaining the next. Operator method ruling 2026-10-08: "partir el trabajo de deepseek en partes más pequeñas, aunque llames más instancias". |

## 1 · What changed

**Inc-1c (source: `mapper/app.py`, `mapper/widgets/inspector.py`)**
- U1 (UX-1 M1): the hidden-card prefix `● unsaved (N) · ctrl+s save` repaints as soon as the card hides again (`M` → edit → `↵`).
- U2 (UX-1 M2): a focused inspector text field puts `type to draft · ctrl+s save · esc leave field` on the hint line (glyph and label read from the seat); leaving the field hands the resting hint back.
- U3 (operator R8): the unsaved state — header `● unsaved (N)` and each field `●` — is painted `darkside.ALERT`; the hue census registers `UNSAVED_STYLE = darkside.ALERT` with the ruling as its reason.
- U4 (UX-1 minor): a failed draft save shows ONE error toast, `could not save '<map>' (<ErrorType>) · draft kept · ctrl+s to retry` — the map id and the exception TYPE, never `str(e)` (keeps `G6-C-F2`'s oracle intact). `_save_or_toast(..., toast=False)` records the type on the screen for the caller.
- Z2 fix (found by the first full lane): leaving a field re-announces an attachment chip's `open attachment`, because the chip swap works inside the resting hint the U2 field hint had replaced.

**Inc-2 (source: `mapper/app.py`)**
- U5: `q` / `esc` (the pop branch) leave the map only through `_guard_draft` (LLR-003.3).
- U6: following a link to another map is guarded before the push (LLR-003.4, R6).
- U7: `MapperApp.action_quit` walks every `MapScreen` with a draft, top first, guarding each; a second `ctrl+q` starts no second walk; **PDR C1** — if a guard is already open on a screen the walk ends and clears `_quit_walk_open`, so `ctrl+q` never wedges; `MapScreen.has_pending_draft()` added (I-4).
- U8: `a` / `x` move their bodies into `_add_child` / `_archive` behind `_guard_draft` (LLR-003.6).
- U9: add/remove attachment move into `_add_attachment(node_id)` / `_remove_attachment(node_id, index)` behind `_guard_draft`, values taken from the message before guarding.
- U10: AT-013, a declared Layer-A injection test (a lower map screen holds the draft).

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | HLR-002, LLR-002.2, HLR-003, LLR-003.3, LLR-003.4, LLR-003.5, LLR-003.6, HLR-004, LLR-004.2, HLR-005, LLR-005.2 | U1, U2, U4, Z2 fix, U5–U9 |
| `mapper/widgets/inspector.py` | source | HLR-002, LLR-002.2 | U3 (`UNSAVED_STYLE = darkside.ALERT`) |
| `tests/test_inc1c_ux.py` | test | LLR-002.2, LLR-004.2, LLR-005.2 | new, 4 nodes (U1–U4) |
| `tests/test_draft_exits.py` | test | LLR-003.3, LLR-003.4, LLR-003.5, LLR-003.6, AT-005a, AT-005b, AT-011, AT-012, AT-013, AT-014a, AT-014b, AT-014c, AT-014d | new, 19 nodes (U5–U10) |
| `tests/test_draft_save.py` | test | LLR-004.2 | the failed-save toast assertion now pins the ONE toast (U4) |
| `tests/test_darkside_census.py` | test | HLR-002 | `UNSAVED_STYLE` re-registered as ALERT (R8) |
| `tests/test_search.py` | test | LLR-005.2 | `on_descendant_blur` registered as a pass-free reader (restores the resting hint) |
| `tests/test_en2.py` | test | LLR-005.2 | two `Z2` scope arms: `open attachment` stays chip-only; a focused text field may name `ctrl+s` |
| `.dev-flow/2026-10-08-data-safety-batch/evidence/inc1c-inc2-*.transcript` | doc | n/a — evidence | lanes and unit reports, profile path scrubbed |

Source files: **2** (Inc-1c: `app.py`, `inspector.py`; Inc-2: `app.py`) — under the cap.

## 3 · RED counterfactual and mutation verdicts (executed)

Every unit reverted ONLY its product change, ran its new nodes, recorded the failure, restored byte-identically (sha256 before = after) and re-ran GREEN (`evidence/inc1c-inc2-units.transcript`).

| Unit | Mutation | Verdict |
|---|---|---|
| U1 | drop the repaint call | killed (`next ▸ j/k/h/l move …` instead of the prefix) |
| U2 | drop the field hint (orchestrator, `pass`) | killed (1 failed) |
| U3 | header back to WARN | killed (`#ffd230 != #ff4f42`) |
| U4 | `toast=True` at the draft-save call site (orchestrator; a first attempt hit a docstring and is recorded as void) | killed (1 failed) |
| U5 | revert the two pops | killed (6 failed, `0 == 1` guards) |
| U6 | revert the link push guard | killed (3 failed) |
| U7 | revert `action_quit` / revert only the C1 branch | killed (4 failed) / killed (C1 test) |
| U8 | revert the `a`/`x` guards | killed (2 failed) |
| U9 | revert the attachment guards | killed (2 failed) |
| U10 | walk only `[self.screen]` | killed (1 failed) |
| Z2 fix | no chip re-announce | killed (`test_z2_…hands_back[size0/1]`, observed in the first lane) |

## 4 · Test results
- Per unit (orchestrator): the unit's files plus `tests/test_search.py` and `tests/*census*.py` — 175 → 226 passed across the units.
- **Full default lane 1:** `3 failed, 2907 passed` — the `Z2` arms (`evidence/inc1c-inc2-default-lane-1-z2.transcript`); fixed in `5ad158e`.
- **Full default lane 2 (orchestrator):** `python -B -W error::SyntaxWarning -m pytest -q -rf -p no:cacheprovider` → `2910 passed, 24 deselected, 3 xfailed in 1472.93s`, `EXIT_CODE=0` (`evidence/inc1c-inc2-default-lane.transcript`).
- **Ledger:** 2890 collected (Inc-1b + Inc-4) − 0 + 23 (4 + 19) = 2913 = 2910 passed + 3 xfailed. ✓ (rewrite-in-place: `test_draft_save.py`, `test_en2.py` ×2, `test_darkside_census.py`, `test_search.py` registry — counts unchanged.)

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| Default lane 2 (green) | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc1c-inc2-default-lane.transcript` | `f8b53dd1ecd86ac45fd3aa9304e1f3e6a2741e47d391aaab20ed69e081573d14` |
| Default lane 1 (`Z2` failures) | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc1c-inc2-default-lane-1-z2.transcript` | `eeda2a1274a98c97d67a5f6e5b3e9f270f5c394bfcf8ae3c248da5f99c2c65f3` |
| Unit reports U1–U10 (RED, sha256 restores) | `.dev-flow/2026-10-08-data-safety-batch/evidence/inc1c-inc2-units.transcript` | `8eba2049f9262ef87c7594f67c579fa5d19eef218e0a7a23dbce10ce34fb4b65` |

## 4b · Independent review
⚠ owed — `code-reviewer` over `6676585..HEAD`.

## 5 · Risks
- U2's hint borrow and the chip's `Z2` borrow now coordinate through the screen's blur handler; a future third borrower of the hint line must follow the same hand-back rule.
- PDR C1 is met by ending the walk; the operator answers the open node guard first, then presses `ctrl+q` again.

## 6 · Pending items / deviations
- **C14:** the operator's real-terminal `ctrl+s` / `ctrl+q` smoke is still owed.
- Deviation: `test_en2.py`'s two `Z2` arms were rescoped (intent kept: `open attachment` is chip-only; the chip hands back what it borrowed).
- U2 hit the 15-min watchdog while debugging; its debug prints were removed and its RED proven by the orchestrator.

## 7 · Suggested next task
`code-reviewer` on this increment, then the DDR and the final PR-level `qa-reviewer` pass over the whole branch.
