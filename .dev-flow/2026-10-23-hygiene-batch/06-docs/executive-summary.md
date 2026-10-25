# Executive summary — mapper — Batch 2026-10-23-hygiene-batch

> Phase 6 artifact. Owner: `presentation-builder`. Audience: non-technical stakeholder. 1-2 pages.

## 🔑 Bottom line (read first)

- **What we delivered:** a three-part hardening of the mapper terminal app — colour output
  that can no longer be silently disabled, bounded loading of map files with clear
  refusal messages instead of crashes, and a machine-checked proof that every screen
  layout fits its grid at every supported terminal size.
- **Business outcome:** maps from outside sources (the QuickMap handoff) can no longer
  hurt the app — oversized, deeply nested, or trick-structured files are refused with a
  one-line reason the user can act on — and what the user sees is now reproducible and
  auditable, size by size, screen by screen.
- **Next step:** land the two record-only conditions at the trunk join (about a week of
  documentation wording), then pick up the UI batch — the prototype verdicts for the two
  October rounds are on record (`prototypes/round-2026-10-23/verdict-2026-10-24.json`,
  `prototypes/round-2026-10-24/verdict-2026-10-24.json`, main checkout; `prototypes/` is
  git-ignored by design, so they are not in this worktree); the relation-map port is
  unblocked — the operator approved the map-types definition on 2026-10-23 (record
  `quickmap/docs/handoff-mapper/map-types-veredicto-2026-10-23.json`, outside this repo).

---

## Context (reference)

### Context
Mapper is the terminal application that renders and navigates relation maps. This batch
is the hygiene follow-up to the QuickMap handoff (items C9/C10/C11): the handover gave
mapper a body of externally produced map content and a set of operator rulings, and this
batch made the app safe and predictable in the face of that content.

### Problem
Three gaps. (1) A standard terminal convention (`NO_COLOR`) could silently strip all
colour from the app's output, leaving users with unreadable screens and no warning.
(2) Nothing limited what a map file could demand: a hostile or broken file could be
arbitrarily large, thousands of levels deep, or structured to make the loader do
unbounded work — and the app would try anyway. (3) Nobody could prove the seven screen
layouts actually fit their grids at the five supported terminal sizes; there was no
audit trail of what had been drawn.

### Solution
- **Colour is always on.** The app no longer honours environment requests to disable
  colour; screens render identically with or without them (verified byte-for-byte).
- **Bounded loading with plain-language refusals.** Every file the app reads — maps and
  CSV imports alike — now passes through one bounded reader with fixed limits on size,
  nesting depth, node/edge counts, and file structure. Files that break the limits are
  refused with a short typed message naming the limit and the map; the app keeps
  running. Content that is not valid UTF-8 text is refused the same way.
- **A proof, not a hope, for layouts.** A sweep harness renders every layout at every
  terminal size and state combination (120 combinations) and fails on any overflow —
  no renderer code changed, because none needed to. A drawing audit hook now records
  every clipped or overwritten cell, so future rendering defects leave evidence.

### Outcomes / results
- Gate suite: **3,575 tests passed**; the single failure is a pre-existing flaky test
  unrelated to this work (reproduced on the pre-batch code; tracked in the backlog).
- 3 user stories, 6 high-level and 12 low-level requirements, 9 acceptance tests — all
  covered both in code and through the running application; the traceability matrix
  closes with zero gaps.
- Independent design review sealed the batch **approved with conditions**; both
  conditions are wording fixes in documentation, not behaviour.
- No renderer pixel changed: existing screens are byte-identical before and after.
- Cost note: on an artificially huge 12,000-node test map, the new safety pre-scan adds
  ~3.5 s to an 8.5 s load (measured). Real maps (≤ 8 nodes) are unaffected. A cheaper
  scan is a known future option.

### Next steps
1. **Trunk join (days):** apply the two record-wording conditions from the design review
   (an architecture document phrase, and a comment block in the CSV-import screen).
2. **UI batch (next sprint):** consume the approved prototype verdicts — on record as
   `prototypes/round-2026-10-23/verdict-2026-10-24.json` and
   `prototypes/round-2026-10-24/verdict-2026-10-24.json` in the main checkout (`prototypes/`
   is git-ignored by design, so they are not in this worktree); intake reads them there.
3. **Relation-map port (unblocked 2026-10-23):** the operator approved the map-types
   definition (record `quickmap/docs/handoff-mapper/map-types-veredicto-2026-10-23.json`,
   outside this repo); the port of the remaining QuickMap map types is ready to schedule (handoff §9).
4. **Backlog hygiene (ongoing):** four carried items (a deferred drawing-audit event
   kind, one pre-existing flaky test, one latent crash path no real input reaches, and a
   test-timing robustness fix) are queued with named owners.
