# Unified mapper UI — prototype notes

## Problem
The home screen currently routes three actions into different screens that feel like separate apps:
- Consult maps → `MapScreen`
- Plug repo → `RepoScreen`
- Construct → `MapScreen("new")`
There is no place for documents/templates, and a newly created map is empty.

## Proposal: one model, one viewer, four doors
All four user actions open the same `MapScreen` but parameterized by source and mode:

| Door | What it loads | Mode |
|---|---|---|
| Consult maps | local `.mmd` + `_nodos.yml` | browse |
| Plug repo | GitHub repo fetched into a Graph | repo / read-only |
| Construct | new seeded graph | edit |
| Document factory | process map whose nodes carry documents | factory |

## New domain concept: Document
A `Document` lives inside a `Node`. It has a `name` and a `source` string containing `{{tags}}`.

When a child node is created from a parent:
1. The parent's document source is copied to the child.
2. The child's `Ficha.fields` start empty for any key used as a `{{tag}}`.
3. At render/export, tags resolve by walking up ancestors:
   - local value first,
   - then parent, grandparent, ... root,
   - leave placeholder untouched if no ancestor has it.

This is "drag the document forward, reset the placeholders".

## Persistence
Documents live in the sidecar (`<map>_nodos.yml`) under each node's `document:` block.
`.mmd` stays structure-only, preserving the Mermaid round-trip rule.

Backward compat: a legacy node with a `D` field but no `document` block is treated as a one-line document on load and migrated on save.

## UI consequences
- Home has four doors instead of three.
- Recent maps show a `kind` badge (concept / legacy / factory / repo).
- `MapScreen` footer is context-sensitive: nav, view, node, map/repo.
- `d` opens the document editor for the selected node.
- `a` adds a child and copies the document.
- Factory mode shows a preview panel with resolved output + tag inheritance table.

## First increment
1. Add `Document` to the model.
2. Implement child creation with document copy and tag resolution.
3. Extend `MapStore` sidecar read/write.
4. Collapse `RepoScreen` into `MapScreen` with mode flags.
5. Add the fourth door and factory UI.
6. Ship a `contratacion` demo map.

## Out of scope
- External reusable template library across maps.
- Export to `.md`/`.pdf`.
- Rich template syntax beyond `{{tag}}`.
- Multi-parent graphs.
