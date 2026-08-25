# PLAN — mapper · 2026-08-24-components-batch

## Objective

Implement the darkside component sheet and the round-2 purpose-built view
redesigns from `HANDOFF-components.md`: nine production components, a settings
canary, home GLANCE posture (H2), map OPERATED+READ posture (M2), and repo
OPERATED posture (R2). Audit and fix STEP-on-GROUND contrast violations.

## Status per phase

- **Phase 0 — story intake & refinement:** approved at kickoff. US-025..US-030 READY.
- **Phase 1 — HLR/LLR derivation:** waived (mode=core; handoff carries the spec).
- **Phase 2 — Architecture:** waived; components follow existing `mapper/widgets/chrome.py` pattern.
- **Phase 3 — Design / PDR:** waived; prototypes in `prototypes/ui_components/out/index.html` are the visual spec.
- **Phase 4 — Implementation:** complete.
- **Phase 5 — Validation:** complete. `python -m pytest tests/ -q` → 86 passed; prototype verification passed.
- **Phase 6 — Close:** in progress.

## User stories (US-025..US-030)

- **US-025** component library: the nine darkside components with the default/focused/disabled state matrix; a settings surface as the canary.
- **US-026** home hero: drawn-number documentation-debt hero + severity cap; microbar distribution line; dim-tier sparkline; archived note with its key.
- **US-027** map minimap + answering branches: one-glyph-per-branch coverage row with legend; folded branches declare `N nodos · M sin acta`.
- **US-028** map pagination + toast discipline: `‹ n/m ›` under the tree, shed counts stated; toasts only for events, word-based.
- **US-029** repo connected state: shared 30-day axis, `●`/`◆`, shared today rule column, source honesty badge, legend row.
- **US-030** contrast amendment audit: no STEP-styled readable text on GROUND; tracks/rules on GROUND use WORDMARK.

## Increments

1. Inc-1: port `generate.py` primitives into `mapper/widgets/components.py` with Static wrappers.
2. Inc-2: settings canary screen (`SettingsScreen`) demonstrating the state matrix.
3. Inc-3: rebuild `HomeScreen` for GLANCE posture (H2).
4. Inc-4: add coverage minimap, answering branches, pagination, and toast discipline to `MapScreen` (M2).
5. Inc-5: rebuild `RepoScreen` connected state with shared 30-day axis (R2).
6. Inc-6: audit STEP-on-GROUND contrast across existing screens and fix violations.
7. Inc-7: regression tests + prototype regeneration + browser verification.

## Key decisions

- 2026-08-24 · batch kickoff from `HANDOFF-components.md` in mode=core; standing
  authorization from `state.json` applies (autonomous run with merge authorized).
- 2026-08-24 · prototypes are the spec: H2/M2/R2 from `prototypes/ui_components/out/index.html`.
- 2026-08-24 · contrast amendment: STEP is invisible on GROUND; readable dim text on GROUND uses MUT, glyph tracks/rules use WORDMARK.

## Risks / watch-items

- `MapScreen` canvas is layout-sensitive; keep the tree renderer interface unchanged.
- `RepoScreen` time axis must align events vertically by age; today rule column is shared.
- Focus state on custom Static widgets requires explicit `can_focus=True` and focus styling.

## Conventions honored

Terminal honesty, Spanish UI strings, no passive ACCENT on data, status words not glyphs.
