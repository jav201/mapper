# Executive summary — mapper — Batch 2026-10-08-data-safety-batch

> Phase 6 artifact (drafted by a Kimi `kimi-for-coding` unit; verified by the orchestrator). Audience: non-technical stakeholder. 1–2 pages.

## 🔑 Bottom line (read first)

- **What we delivered:** editing a mind-map card no longer saves anything by accident — every edit now waits for an explicit `ctrl+s`, every attempt to leave with unsaved changes asks first, and unsaved changes are always shown in red.
- **Business outcome:** the defect where a single stray keystroke permanently overwrote a map and its data file — with no confirmation and no visible trace — is closed by design, and the full quality gate passed with zero failures.
- **Next step:** merge and move on; the follow-on design batch picks up the deferred items (`B-102`/`B-103` were added to the backlog at this batch's close, `.dev-flow/BACKLOG.md:9`).

---

## Context

mapper is a terminal tool the author uses daily to build and maintain `.mmd` mind-maps, each paired with a `_nodos.yml` data file. Editing happens in an inspector card next to the map. This batch (`2026-10-08-data-safety-batch`) was scoped by the operator to one data-safety defect (B-36) plus three verification debts (B-98, B-100, B-101), in `full` mode because the change touches both persistence and UX (`.dev-flow/state.json:60-65`).

## Problem

One stray keystroke on a focused inspector field durably overwrote the map **and** its sidecar, with no confirmation and no explicit "edit" gesture. Measured before the fix: 7 of 8 focusable fields overwrote both files from one real `n` press, and the guard intended to prevent it (a non-empty-delta check) was mathematically unable to fire — the delta is genuinely non-empty after the keystroke. Two cheap remedies were tried and both failed. It had already fired once on this repository's own tracked fixtures (`.dev-flow/BACKLOG.md:165`). Separately, the test suite carried acceptance-test ids with no real test behind them (a regression could delete them silently), and one flaky test occasionally invalidated the whole-branch quality gate.

## Solution

- **Draft + explicit save.** Typing in a card field only fills an in-memory draft for that node. Nothing touches disk on blur, on Enter, or on any field — including the status selector. Pressing `ctrl+s` writes the map and its sidecar once, as a single undoable step. Leaving the field keeps the draft; the hint line always names `ctrl+s` as the save key (operator prototype verdict "C" and rulings R1–R9, `VERDICT-b36-prototype-2026-10-08.md:5-23`).
- **Red means unsaved.** The card header shows `● unsaved (N)` and every changed field carries a red `●` (the palette's alert colour, chosen by the operator: "red to alert that there is unsaved content").
- **One guard for every exit.** Changing node, pressing `q`/`esc`, following a link to another map, quitting, or adding/archiving a node or attachment all open the same three-way question first: `save · discard · stay`.
- **A failed save cannot corrupt anything.** If the write fails, the tool reloads the map from disk, keeps exactly the edits that didn't make it as still-unsaved, and says so in one clear message. Nothing on that path writes.
- **Test debt closed.** The doubled-`?` legend and damaged-map behaviours now have their declared tests; every acceptance id resolves to a real on-disk test or was formally retired; the flaky legend test was traced to its root cause (a queued screen scroll, not the product) and fixed so the gate can be trusted again.

## Outcomes / results

- **Quality gate:** 2920 tests passed, 0 failed (3 expected-fails), run time ~25 minutes on `cab8181` — later commits change records only, no product code — recorded as `PASS-WITH-NOTES` (`.dev-flow/2026-10-08-data-safety-batch/04-validation.md:9`).
- **Requirements:** all 36 (9 high-level + 27 low-level) verified; every acceptance scenario exercised through the real interface with real keystrokes (`04-validation.md:11-13`).
- **Operator hands-on check passed** in the real terminal on 2026-10-09: saving worked, the exit guard appeared on quit (`.dev-flow/2026-10-08-data-safety-batch/04-validation.md:253`).
- **All four backlog items closed:** B-36, B-98, B-100, B-101 marked DONE (`.dev-flow/BACKLOG.md:165,208,210,211`).
- Known accepted residuals (minor, recorded): a typed-ahead `d` while the guard is up can discard a draft (never writes); two rare double-failure corner cases leave the operator a clear "reopen the map" message (A-13…A-15, `04-validation.md:261-264`).

## Next steps

- Merge the batch (standing operator authorization, after the final PR-level `qa-reviewer` pass came back clean (MERGE, 2026-10-09)).
- Follow-on design batch: the deferred `US-N14` scope and the newly logged `B-102`/`B-103` items (`.dev-flow/BACKLOG.md:9`).
- Watch the first real-world usage for any hint-line or guard friction; the design keeps one rule for every exit, so adjustment is a single point of change.
