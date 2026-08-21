# HANDOFF — mapper (next session implements)

## Where this stands

**Batch `2026-08-18-batch-01` is at its Phase-0 gate, awaiting the operator's
decision** (`approve` / `iterate` / `cancel`). Everything up to the gate is
done and recorded:

- `.dev-flow/state.json` — `current_phase: 0`, `phase_status:
  awaiting-gate`, kickoff authorization recorded verbatim in
  `standing_authorization`, decision log up to date (incl. Phase-0
  iteration 1).
- `.dev-flow/01-requirements.md` — **14 user stories, all READY**, refined
  per INVEST with one block each, and the C-43 premise table with executed
  evidence (P-1/P-2/P-3 TRUE; P-4/P-5 dispositioned in writing).
- `.dev-flow/2026-08-18-batch-01/PLAN.md` — the living compendium: objective,
  roadmap of 7 proposed increments, risks, conventions, out-of-scope carries.

**To resume:** run `/dev-flow` from this project root. The flow reads
`state.json`, sees `awaiting-gate`, and must present the Phase-0 artifact +
pending decision WITHOUT regenerating work. On `approve`, derive the 14
stories into HLR/LLR (EARS, dual traceability) per Phase 1.

## The product in one paragraph

**mapper** — a TUI (Python + Textual 8.2.8 + Rich 15.0.0) for concept and
structure maps where *every node is a ficha*. Main window with three doors
(consult maps / plug a GitHub repo / construct nodes & maps). Four diagram
families over one node/edge machinery: layered trees (concept + the
super-legacy software tree with required-field schema coverage), lanes (repo
map), radial (mind maps), outline. Search `/` over everything a node carries,
focus/collapse, export SVG/PNG. Persistence: the text (`.mmd` + `nodos.yml`
sidecar) is the only truth and lives in git; a local SQLite index is derived
and rebuildable, never committed.

## The visual source of truth (prototypes — read these before designing)

In `C:/Users/jjgh8/Github/taskboard/prototypes/mapper/`:

- `out/mapper.html` — the five rendered views (concept, repo, mermaid,
  legacy, mental), each at 118×30 and 68×24. **This is what the user already
  approved visually.**
- `proto.py` — the working render machinery to PORT (not import): the layered
  tree layout, the Canvas (cells + box-drawing wires via connectivity bits +
  free-angle braille edges + pill backgrounds), the lane repo map, the
  minimal `graph TD` parser, the radial bezier mind map.
- `NOTES.md` — the product spec: refined feature wording, complementary
  features, git/github lessons, the persistence architecture, and the
  polish round.

## Constraints that are law here

- **Terminal honesty**: width-1 glyphs, palette-rationed severity (colour
  judges, never decorates), markers outrank wires in their cell, cards shed
  width before anything scrolls.
- **No real data in committed artifacts** — synthetic fixtures only, always
  (the `prototypes/capture.py` law). The GitHub connector reads through `gh`
  (authenticated as `jav201`, scopes repo/workflow/read:org — verified
  2026-08-18); read-only, never mutates GitHub.
- **Mermaid round-trip never forks** — canvas and text are two views of one
  thing. MVP parser scope: `graph TD`, `A[x] --> B[y]`, bare ids, edge labels
  `-->|text|`. Multiple parents are OUT of MVP scope (recorded in P-4).
- **Narrow terminals**: 68-column legibility per family; dense trees get the
  two-leftmost-levels + `+N` overflow chip (P-5, verified at Phase 4).
- **Attachments are references**, never payloads (US-014); a per-map
  `attachments/` folder is an open Phase-1 decision.

## Standing authorization (inherited by this batch)

Autonomous end-to-end run AND merge authorized ("Autónomo con merge
autorizado"), with the flow's own gate: one final independent PR-level
qa-reviewer pass over the whole diff must come back clean before merging.
Every autonomous decision is recorded in PLAN.md + state.json + postmortem +
vault at `/dev-flow-sync` (operator confirmed).

## State of the wider workspace (taskboard, the sibling project)

Uncommitted there, all the operator's to commit: `handoff-lanes-grid.md`
(the G2 grid Lanes view, ready for its own implementation agent),
`handoff-next-level.md`, `prototypes/lanes_gauge/` (G2 source),
`prototypes/lanes_load/`, `prototypes/city/` (in the drawer per the
operator), `prototypes/vista/` (in the drawer per the operator).
