# PLAN — mapper · 2026-08-18-batch-01 (living compendium)

## Where we are

Phase 0 at its gate: 13 user stories drafted from the prototype session and
the operator's asks, refined against INVEST, all classified READY, premises
P-1..P-3 executed TRUE (gh authenticated, stack verified, prototype renders),
P-4/P-5 dispositioned in writing. Waiting for the operator's gate decision.

## Objective

Mapper MVP — a TUI for concept/structure maps: main window (consult / plug /
construct), layered concept + legacy trees with required-field fichas, GitHub
repo-as-map read-only via `gh`, Mermaid `graph TD` round-trip, radial mind
maps, search/focus/outline/export, two-layer persistence (repo text = truth,
SQLite = rebuildable index).

## Status per phase

- **Phase 0 — story intake & refinement:** at gate. 13 US, all READY.
- Phases 1-6: not started.

## Roadmap / increment plan (proposed for Phase 1 gate)

1. Inc-1: project skeleton + map store (text truth + sqlite index rebuild).
2. Inc-2: layered concept map canvas (port of `prototypes/mapper/proto.py`).
3. Inc-3: fichas + required-field schema + legacy tree fixture.
4. Inc-4: main window (three doors) + navigation + search/focus.
5. Inc-5: Mermaid round-trip + outline mode.
6. Inc-6: GitHub connector (repo-as-map).
7. Inc-7: radial mind map + export + polish.

## Key decisions (log mirrored in state.json)

- 2026-08-18 · batch kickoff: new project dir `Github/mapper/`; artifacts in
  English; mode=full; autonomous run with merge authorized (operator's words:
  "Autónomo con merge autorizado"); decision recording confirmed ("Sí,
  registrar todo").
- 2026-08-18 · persistence: text (mmd + sidecar YAML) is the only truth;
  SQLite is derived and rebuildable, never committed.
- 2026-08-18 · the legacy-tree ficha is the product's signature element.

## Risks / watch-items

- P-4: real legacy maps may want edge labels or multiple parents — edge
  labels scheduled for MVP, multiple parents out of MVP scope (in writing).
- P-5: narrow-terminal legibility swept at 68 cols for the five prototype
  views; the dense legacy tree gets the two-leftmost-levels + `+N` convention
  and is verified in Phase 4.

## Conventions honored

Terminal honesty (width-1 glyphs, palette-rationed severity), no real data in
committed artifacts, read-only GitHub, Mermaid round-trip never forks.

## Out-of-scope carries

Real-time collaboration; web/mobile; write access to GitHub; non-`graph TD`
Mermaid diagrams.

- 2026-08-18 · Phase-0 iteration 1 (operator): US-008 strengthened — search
  reaches inside the whole ficha (notes, field values, attachment names), not
  only titles; US-014 added — nodes carry files/URLs/images as attachments
  (references, never payloads). Both READY; requirements doc updated.

## Test ledger

Empty until Phase 3.

## Decision log

See Key decisions above (mirrored to `state.json.decisions_log`).
