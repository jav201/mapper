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

- **Phase 0 — story intake & refinement:** approved at gate (2026-08-21). 14 US, all READY.
- **Phase 1 — HLR/LLR derivation (EARS, dual traceability):** approved at gate (2026-08-21). 35 HLR, 47 LLR, 28 TC, 14 AT.
- **Phase 2 — Architecture (ARQ):** approved at gate (2026-08-21). Module map, dependencies, frozen interfaces recorded in `docs/ARCHITECTURE.md`.
- **Phase 3 — Design / PDR:** approved at gate (2026-08-21). Interfaces frozen per ARCHITECTURE.md §4.
- **Phase 4 — Implementation:** complete. 7 increments delivered.
- **Phase 5 — Validation:** complete. `python -m pytest tests/ -q` → 16 passed.
- **Phase 6 — Close:** complete. Postmortem and traceability matrix sealed; merged to `master`.

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

## Design / PDR (Phase 3)

Frozen interfaces for the fork (see `docs/ARCHITECTURE.md` §4):

| Interface | Shape |
|---|---|
| `Graph` | `nodes: dict[str, Node]`; `edges: list[Edge]`; `root_id: str`; `focus(node_id) -> Graph`. |
| `Canvas` | `put`, `wire`, `edge`, `elbow_down`, `text`, `dline`, `rows`. |
| `MapStore` | `load(map_id) -> (Graph, Sidecar)`, `save(map_id, graph, sidecar)`, `reindex()`. |
| `IRenderer.render` | `render(graph, selected_id, w, h, **kwargs) -> Text`. |
| `SearchIndex.query` | `query(q) -> list[str]` (node ids). |
| `MermaidImporter/Exporter` | `parse(src) -> Graph`, `dump(graph) -> str`. |
| `GitHubConnector.fetch` | `fetch(repo_slug) -> Graph`. |
| `save_svg` / `save_png` | `save_svg(text, path)`, `save_png(text, path)`. |

Increment execution order (risk-driven, dependencies first):
1. Inc-1: skeleton + store
2. Inc-2: layered canvas
3. Inc-3: fichas + schema + legacy fixture
4. Inc-4: main window + nav + search/focus
5. Inc-5: Mermaid + outline
6. Inc-6: GitHub connector
7. Inc-7: radial + export + polish

## Out-of-scope carries

Real-time collaboration; web/mobile; write access to GitHub; non-`graph TD`
Mermaid diagrams.

- 2026-08-18 · Phase-0 iteration 1 (operator): US-008 strengthened — search
  reaches inside the whole ficha (notes, field values, attachment names), not
  only titles; US-014 added — nodes carry files/URLs/images as attachments
  (references, never payloads). Both READY; requirements doc updated.
- 2026-08-21 · Phase-0 gate approved on operator instruction
  "Vamos a implementar desde aquí: C:/Users/jjgh8/Github/mapper/HANDOFF.md";
  all 14 user stories remain READY; batch proceeds to Phase 1 (HLR/LLR).
- 2026-08-21 · Phase 1 derivation complete: 35 HLRs, 47 LLRs, 28 TC, 14 AT;
  traceability matrix populated; awaiting Phase-1 gate approval to enter
  Phase 2 (architecture / ARQ).
- 2026-08-21 · Phase-1 gate approved on operator instruction
  "aprobado, sigue hasta commit push y merge"; batch proceeds to Phase 2
  (architecture) and onward through implementation/validation/close.
- 2026-08-21 · Phase 2 architecture approved: module map, dependency bans,
  frozen interfaces, and parallelisation worksheet recorded in
  `docs/ARCHITECTURE.md`; proceeding to Phase 3 (PDR).
- 2026-08-21 · Phase 3 PDR complete: frozen interfaces listed in PLAN.md;
  increment order confirmed; proceeding to Phase 4 (implementation).
- 2026-08-21 · Phase 4 implementation complete: 7 increments delivered.
- 2026-08-21 · Phase 5 validation complete: `python -m pytest tests/ -q` →
  16 passed.
- 2026-08-21 · Phase 6 close complete: postmortem and traceability matrix
  sealed; batch merged to `master`.

- 2026-08-18 · darkside round (operator): the UI speaks DARKSIDE — achromatic,
  KMBlue only on interactive affordances, depth by grey-steps never borders,
  lowercase, computed moon doodle, semantic severity only, solid selection
  (design decision D-1). Added US-015 empty states · US-016 ctrl+p palette ·
  US-017 help surface · US-018 resume-last · US-019 undo — all READY, 19 US total.

- 2026-08-18 · improvements round (operator, "implementar todas"): D-A radial
  darkside render; US-020..023 READY (23 US total); HANDOFF-improvements.md.
  Note: another session already implemented the darkside redesign into
  production (`mapper/darkside.py`, `mapper/keymap.py`, screens) — commit
  4cda8a9; the prototypes now read from those shared modules.

- 2026-08-18 · design triplet (operator): D-A radial active-path + D-B motion
  flipbook + D-C home identity, all rendered into prototypes/ui_darkside/out/;
  the design part now lives in HANDOFF-improvements.md.

- 2026-08-18 · operator: repo connector simplified to local-path-or-URL
  (plain git first, gh as enrichment) — US-006 refined; US-024 office-format
  template ingestion added READY with P-6 probed TRUE (stdlib zipfile+regex
  parses docx tags); renders ds-repo-plug.svg + ds-factory-office.svg.

- 2026-08-18 · ui_welcome round: five views rendered for appeal + welcoming
  entry (desk/s19_app/taskboard lessons applied, darkside kept). Prototypes
  read the REAL mapper.darkside + mapper.keymap modules so prototype and app
  cannot drift.

- 2026-08-24 · ui_components round (operator: "more elements"; source is
  tui-design's COMPONENTS.md, no external skill needed): the darkside
  component sheet — 9 interaction components (switch, stepper, slider,
  segmented, progress, braille spinner, text field, pagination, tag chip) in
  a default/focused/disabled state matrix, then applied to home (KPI tiles +
  sparkline), map (accordion with declared fold counts, pagination, save
  toast) and repo plug (skeleton + spinner fetch state). Verification
  rulings: status words not glyphs (✓ failed font coverage), MUT is the
  floor for readable chrome, grid prefix columns sized to the prefix.
  prototypes/ui_components/{generate.py,NOTES.md,out/}.

- 2026-08-24 · ui_components round 2 (operator: elements exist but not used
  for their PURPOSE; reference repos desk/taskboard/s19_app/gbl studied via
  agent swarm): home rebuilt as GLANCE posture — one drawn-number hero (the
  loudest signal: nodos sin acta + severity cap), KPI tiles collapsed to one
  s19 microbar distribution line, sparkline demoted to dim tier; map gained
  a coverage minimap (s19 memstrip) and collapsed branches that still answer
  (gbl BandHeader: "5 nodos · 2 sin acta"); repo gained one shared 30-day
  time axis for branches+releases with a shared today rule and a source
  honesty badge. New ruling: STEP is invisible on GROUND — dim floor there is
  WORDMARK for glyph tracks/rules, MUT for words.

## Test ledger

Empty until Phase 3.

## Decision log

See Key decisions above (mirrored to `state.json.decisions_log`).
