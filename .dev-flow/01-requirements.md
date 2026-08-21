# Requirements Document — mapper — Batch 2026-08-18-batch-01

## 1. Introduction

### 1.1 Purpose

This document captures the requirements for **mapper**, a terminal (TUI)
application for building and consulting concept and structure maps, derived
from the operator's prototype sessions of 2026-08-18 and the prototype
artifacts in `taskboard/prototypes/mapper/` (five rendered views + product
NOTES).

### 1.2 Scope

In scope for the MVP: the main window (consult maps / plug a repo / construct
nodes and maps), concept maps (layered trees), repo-as-map (GitHub via `gh`),
Mermaid `graph TD` round-trip, radial mind maps, the node ficha with a
per-map required-field schema, search/jump, focus, export, and the two-layer
persistence model (repo text as truth, rebuildable SQLite index).

Out of scope: real-time collaboration, web/mobile clients, diagram families
beyond the four prototyped, write access to GitHub.

### 1.3 Definitions, acronyms, abbreviations

- **Map** — a navigable structure of nodes and edges rendered in the
  terminal.
- **Ficha** — the card every node carries: title, state, meta, notes, links,
  dates, and the map's required fields. There are no mute nodes.
- **Schema** — the customizable set of required fields every node of a map
  shares; coverage is drawn per node and per map.
- **Lane** — a branch rendered as a timeline row in the repo map.
- **Lane view / radial view / layered view** — the diagram families: repo
  map (lanes), mind map (radial), concept/legacy (layered).

### 1.4 References

- `taskboard/prototypes/mapper/NOTES.md` — the product notes (features,
  wording, persistence architecture, lessons from git/github).
- `taskboard/prototypes/mapper/out/mapper.html` — the five rendered views.
- `taskboard/prototypes/mapper/proto.py` — the working render machinery the
  MVP ports from.

### 1.5 Document overview

§2 describes the product and lists the source user stories with their
Phase-0 refinement; §2.7 evaluates the premises this batch relies on. HLR /
LLR / validation strategy land in Phase 1.

## 2. Overall description

### 2.1 Product perspective

mapper is a standalone TUI (Python + Textual/Rich, the stack proven by
taskboard). It reads maps from text sources (Mermaid `graph TD` + a YAML
ficha sidecar) versioned in git, and from GitHub repositories read-only via
the authenticated `gh` CLI. It persists nothing to the repo by itself — the
text is the truth; a local SQLite index is derived and rebuildable.

### 2.2 Product functions

- Main window with three doors: consult maps, plug a repo, construct.
- Four diagram families over one node/edge machinery: layered (concept and
  legacy trees), lanes (repo map), radial (mind maps), outline (text).
- Ficha per node under a per-map required-field schema, with coverage drawn
  per node and per map; nodes may carry attachments (files, URLs, images)
  listed and openable from the ficha.
- Search/jump (`/`) over titles AND everything the ficha carries, focus
  (collapse to a subtree), export (SVG/PNG via the console-record machinery).

### 2.3 User characteristics

The operator mapping a super-legacy software system for audit (needs formal
documents per module); the developer reading their own repos; the analyst
building concept maps; the team sharing a versioned map.

### 2.4 Constraints

- Terminal-honest rendering: width-1 glyphs, palette-rationed severity,
  box-drawing edges merged by connectivity bits, braille for free angles.
- No real data in committed artifacts: synthetic fixtures only.
- Read-only GitHub access; no mutations against GitHub.
- The map must round-trip Mermaid — text and canvas never fork.

### 2.5 Assumptions and dependencies

- `gh` CLI installed and authenticated (verified this batch — §2.7 P-1).
- Python + Textual 8.2.8 + Rich 15.0.0 (verified — §2.7 P-2).
- The prototype's layout/render code is the implementation reference, to be
  ported, not imported.

### 2.6 Source user stories

> Connextra format: **"As a `<role>`, I want `<goal>`, so that `<benefit>`"**. Each US gets a unique ID `US-NNN` and must be traceable to one or more HLRs.
> **Phase 0 — Definition of Ready (INVEST):** every story is refined and classified before it can be derived into HLR (Phase 1). Only `READY` stories proceed.

| ID | User Story | Source | DoR status |
|----|------------|--------|------------|
| US-001 | As a user, I want a main window where I can consult my maps, plug a GitHub repo, or start constructing a new map, so that every capability has one entry point. | operator ask (this batch kickoff) | READY |
| US-002 | As an analyst, I want to build and navigate a concept map as a layered tree where every node is a ficha, so that I find relevant information visually. | prototype M1 | READY |
| US-003 | As an auditor, I want every node to carry the map's required-field set (document, owner, state, criticality, notes) with its coverage visible per node and per map, so that I see which element lacks its formal record at a glance. | prototype M4 + operator ask | READY |
| US-004 | As an auditor, I want to map a super-legacy software system as a tree of modules with formal documents attached, so that the audit of an unmaintained system is a map and not a spreadsheet. | operator ask (specific interest) | READY |
| US-005 | As a writer, I want to import and edit maps in standard Mermaid notation and export back to it, so that the map is versionable, portable text. | prototype M3 + operator ask | READY |
| US-006 | As a developer, I want to read my own GitHub repo as a map — branches as lanes, releases as milestones on the timeline, ahead/behind and CI per branch — so that what is in flight, shipped, or stale reads at a glance. | prototype M2 + operator ask | READY |
| US-007 | As a planner, I want radial mind maps with branch colours and organic curved edges, so that a brainstorm reads like a real mind map. | prototype M5 + polish round | READY |
| US-008 | As a user, I want to press `/` and search across node titles AND everything the ficha carries (notes, field values, attachment names), so that any information anywhere in the map is findable. | prototype M3 + taskboard lesson + operator refinement (this gate) | READY |
| US-009 | As a team, we want the map's truth as versioned text (Mermaid + ficha sidecar) in git with a rebuildable local SQLite index, so that the team shares the repo and queries locally. | operator ask (mid-round) | READY |
| US-010 | As a writer, I want the same map as an editable indented outline, so that I can edit fast in text and see the structure. | prototype NOTES (complementary) | READY |
| US-011 | As a presenter, I want to export a map as SVG/PNG, so that it lands in decks and documents. | prototype NOTES (complementary) | READY |
| US-012 | As a reader, I want to collapse everything but a selected subtree, so that big maps read in parts. | prototype NOTES (complementary) | READY |
| US-013 | As a reader, I want to open a node's ficha in place — notes, fields, links — without leaving the map, so that reading never breaks flow. | prototype M1/M4 ficha strip | READY |
| US-014 | As a user, I want every node to be able to hold files, URLs and images as attachments, so that the node's evidence lives on the node itself. | operator refinement (this gate); taskboard precedent (Task.urls/images) | READY |

#### Refinement log (one block per story)

**US-001 — main window (three doors)**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = any role entering the app · outcome = one
  home surface listing existing maps, a "plug a repo" path, and a
  "construct" path (new map / new node) · why = the operator asked for the
  window explicitly; without it the capabilities are undiscoverable · out of
  scope = settings, theming, account management.
- **Feasibility (E, S):** implementation path = a home screen over the map
  store, the `gh` connector entry, and the constructor flow; all three have
  prototype precedents · dependencies/unknowns = none beyond P-1 · fits one
  batch? = yes.
- **Evaluability (T):** "When the app launches, the user observes the three
  doors (consult / plug / construct) with live keybinds on the key bar; when
  the user picks consult, they observe the map list of the store."
- **Open questions:** does the home show recent maps first or all maps
  alphabetically? (default: recents first)
- **Classification:** `READY` — the door set is the operator's own words.

**US-002 — concept map, layered**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = analyst · outcome = a layered tree with
  ficha cards navigable by j/k/h/l, edges that never break at crossings ·
  why = the core map · out of scope = free-form drag layout.
- **Feasibility (E, S):** the prototype's `tree_layout` + `Canvas` port ·
  unknowns = none · fits one batch? = yes.
- **Evaluability (T):** "When the user opens a concept map, they observe the
  layered tree with state-spined cards; when they move the cursor, they
  observe the selection and the ficha strip updating to the node under it."
- **Open questions:** none — the prototype fixed the geometry.
- **Classification:** `READY`.

**US-003 — required-field schema with coverage**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = auditor · outcome = a per-map schema
  (customizable required set) whose coverage reads per node (letters ✓/░),
  per map (header %), and in the ficha (n/N required) · why = the audit is a
  compliance read · out of scope = schema versioning/migration.
- **Feasibility (E, S):** prototype `_coverage` + card rows port; schema lives
  in the sidecar YAML · unknowns = none · fits one batch? = yes.
- **Evaluability (T):** "When a node lacks its document, the user observes
  `SIN ACTA` in the severity tone on its card and the map header's coverage
  dropping accordingly."
- **Open questions:** schema per map or per workspace? (default: per map)
- **Classification:** `READY`.

**US-004 — super-legacy software tree**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = auditor · outcome = the legacy system as a
  layered tree of modules, each with its formal document, creation tags and
  notes · why = the operator's specific current interest · out of scope =
  importing from real Confluence/Jira archives.
- **Feasibility (E, S):** US-002 machinery + US-003 schema; fixture exists ·
  fits one batch? = yes.
- **Evaluability (T):** "When the user opens the legacy map, they observe the
  module tree with per-card doc chips and the schema letters; when they open
  a module's ficha, they observe its document, owner, creation year and
  notes."
- **Open questions:** none.
- **Classification:** `READY` — it is US-002+US-003 instantiated, and it
  anchors the MVP's demo.

**US-005 — Mermaid round-trip**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = writer · outcome = import `.mmd`
  (`graph TD`), edit on canvas or text, export back to `.mmd` · why = the
  standard-notation ask · out of scope = sequence/state/other mermaid
  diagrams, full mermaid syntax (subgraphs, styles).
- **Feasibility (E, S):** prototype parser is minimal by design and marked so;
  the MVP parser covers `A[x] --> B[y]` plus bare ids · unknowns = mermaid
  edge labels (`-->|text|`) — small addition · fits one batch? = yes.
- **Evaluability (T):** "When the user saves a map, they observe a `.mmd`
  whose re-import renders the same tree; when they paste a `graph TD`, they
  observe it as a map."
- **Open questions:** edge labels in MVP? (default: yes, `-->|text|`)
- **Classification:** `READY`.

**US-006 — repo as map (GitHub)**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = developer · outcome = branches as lanes,
  commits as ●, releases as ◆ milestones on the timeline, per-branch
  ahead/behind chip + CI verdict, a ficha strip per branch · why = the
  operator's own repos · out of scope = write actions, PR management, issues.
- **Feasibility (E, S):** `gh api`/`gh repo view` + the prototype lane
  renderer port; `gh` verified authenticated (P-1) · unknowns = rate limits
  on big repos (bounded by a cap + `+N more` convention) · fits one batch? =
  yes.
- **Evaluability (T):** "When the user plugs a repo, they observe its main
  lane with release milestones and its feature lanes with fork/merge
  connectors; when a branch's CI fails, they observe its lane in the alert
  tone and the ✗ on its chip."
- **Open questions:** commits per lane cap for the MVP? (default: 30)
- **Classification:** `READY`.

**US-007 — radial mind maps**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = planner · outcome = the radial layout with
  per-branch hues, tapering organic edges, pill labels · why = the polished
  prototype the operator liked · out of scope = free drag positioning.
- **Feasibility (E, S):** prototype `render_mental` port · unknowns = none ·
  fits one batch? = yes.
- **Evaluability (T):** "When the user switches a map to the radial view,
  they observe the root centred-left, branches radiating in their own hues,
  and curved edges tapering outward."
- **Open questions:** none.
- **Classification:** `READY`.

**US-008 — search / jump over everything a node carries**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = any · outcome = `/` searches node titles AND
  all ficha content — notes, field values, attachment names — and
  reverse-lights matches; esc clears · why = the taskboard lesson, big maps
  need it, and the operator asked explicitly that search reach INSIDE the
  node's information, not only its name · out of scope = fuzzy ranking,
  regex, full-text inside attached binaries.
- **Feasibility (E, S):** a query over the node store incl. attachment names +
  highlight on the canvas; prototyped on M3 · unknowns = none · fits one
  batch? = yes.
- **Evaluability (T):** "When the user types `/acta`, they observe matches
  across titles, notes, field values and attachment names reverse-lit with
  the tally `N nodos`; when they press esc, they observe the full map
  restored."
- **Open questions:** none.
- **Classification:** `READY`.

**US-009 — persistence: repo text as truth, SQLite as rebuildable index**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = team · outcome = the map lives as `.mmd` +
  `nodos.yml` in git; the app rebuilds a local `mapper.db` index from the
  text on open/pull; coverage is a computed VIEW, never a stored table · why
  = the operator's persistence ask · out of scope = a shared server DB,
  merge-conflict resolution UI.
- **Feasibility (E, S):** plain file I/O + sqlite3 stdlib; the prototype
  NOTES fixed the architecture · unknowns = sidecar schema details land in
  Phase 1 · fits one batch? = yes.
- **Evaluability (T):** "When the user deletes `mapper.db` and reopens a map,
  they observe the index rebuilt and the map identical; when they inspect
  git, they observe only `.mmd` and `nodos.yml` tracked."
- **Open questions:** none blocking.
- **Classification:** `READY`.

**US-010 — outline mode**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = writer · outcome = the map as an indented,
  editable outline; editing it edits the map · why = the third view of the
  same thing · out of scope = rich-text editing.
- **Feasibility (E, S):** a linearization of the tree + a text-editing
  surface; the outline IS the Mermaid's readable face · unknowns = edit
  grammar (indent = parent/child) — lands in Phase 1 · fits one batch? = yes.
- **Evaluability (T):** "When the user switches to outline, they observe the
  map as indented text; when they re-indent a line, they observe the canvas
  re-parent accordingly."
- **Open questions:** none blocking.
- **Classification:** `READY`.

**US-011 — export SVG/PNG**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = presenter · outcome = `save_svg` of the
  current view to a shareable file · why = the prototype machinery already
  does exactly this · out of scope = print stylesheets, PDF.
- **Feasibility (E, S):** Rich `Console(record=True)` + `save_svg`; proven
  across every prototype round · unknowns = none · fits one batch? = yes.
- **Evaluability (T):** "When the user exports, they observe an SVG on disk
  that renders the current map identical to the screen."
- **Open questions:** none.
- **Classification:** `READY`.

**US-012 — focus / collapse to subtree**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = reader · outcome = collapse everything but
  the selected subtree, and back · why = big maps read in parts · out of
  scope = per-node collapse memory across sessions.
- **Feasibility (E, S):** filter the tree at the selected node · unknowns =
  none · fits one batch? = yes.
- **Evaluability (T):** "When the user focuses a node, they observe only its
  subtree with the header naming the focus; when they exit, they observe the
  full map."
- **Open questions:** none.
- **Classification:** `READY`.

**US-013 — ficha in place, never the editor**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = reader · outcome = the node's ficha opens
  over the map (notes, fields, links) and closes back · why = reading must
  not break flow · out of scope = in-place editing of the ficha (Phase-later
  candidate).
- **Feasibility (E, S):** the prototyped ficha strip, promoted to a modal or
  split · unknowns = none · fits one batch? = yes.
- **Evaluability (T):** "When the user presses ↵ on a node, they observe its
  ficha — notes with highlights, required fields, links — without leaving
  the map."
- **Open questions:** modal vs bottom strip? (prototype carried the strip;
  default: strip, modal when the ficha overflows)
- **Classification:** `READY`.

**US-014 — node attachments: files, URLs, images**
- **INVEST:** I ✓ · N ✓ · V ✓ · E ✓ · S ✓ · T ✓
- **Functionality (V, N):** user = any · outcome = every node may carry
  attachments — file paths, URLs, images — listed on its ficha and openable ·
  why = the node's evidence lives on the node; the operator asked explicitly;
  taskboard already proves the model (`Task.urls`, `Task.images`) · out of
  scope = copying/uploading binaries into git (attachments are references,
  not payloads), attachment sync across machines.
- **Feasibility (E, S):** the sidecar YAML carries them per node; the ficha
  lists them; `open_url`/`open_images` precedents exist in taskboard ·
  unknowns = none · fits one batch? = yes.
- **Evaluability (T):** "When the user opens a node's ficha, they observe its
  attachments listed by kind (file / url / image); when they activate a URL,
  they observe it handed to the OS browser; when a node references an image,
  they observe its thumbnail in the ficha."
- **Open questions:** reference vs copy? (default: reference by path; an
  optional per-map `attachments/` folder for portable assets lands in Phase 1
  if wanted)
- **Classification:** `READY`.

### 2.7 Premise evaluation (C-43) — MANDATORY, one row per premise

| # | Premise, as a truth-apt proposition | Tier | Verdict | Executed evidence (command output / `file:line` — **NOT** a citation of another document) | Disposition |
|---|---|---|---|---|---|
| P-1 | "The `gh` CLI is installed and authenticated for the operator's GitHub account with repo scope." | premise | ✅ TRUE | `gh --version` → `gh version 2.83.2`; `gh auth status` → `Logged in to github.com account jav201 (keyring)`, scopes `repo`, `workflow`, `read:org` | — |
| P-2 | "The TUI stack (Textual 8.2.8 + Rich 15.0.0) is installed and is the same one taskboard's renderer is verified against." | premise | ✅ TRUE | `python -c …` → `textual 8.2.8`, `rich 15.0.0` | — |
| P-3 | "The prototype machinery (`prototypes/mapper/proto.py`) renders the five views at 118×30 and 68×24 without errors." | premise | ✅ TRUE | `python prototypes/mapper/capture.py` → all five SVGs + txt written; browser check of `mapper.html` → `pageerrors: []` | — |
| P-4 | "Mermaid `graph TD` with `A[x] --> B[y]` + bare ids suffices for the MVP's trees." | hypothesis | ❓ UNDECIDABLE | needs a probe against the real target maps (the legacy ERP tree may want edge labels / multiple parents) | decided in Phase 1 — edge labels `-->|text|` already scheduled as default; multiple parents declared out of MVP scope in writing here |
| P-5 | "The map stays legible at 68 columns for all four families." | hypothesis | ❓ UNDECIDABLE | the prototype verified 68×24 for the five views; a denser legacy tree was not swept | dispositioned: narrow terminals get the two-leftmost levels + a `+N` overflow chip (the `_phase_window` convention); verified in Phase 4 against a swept fixture |

**Gate rule:** ❌ and ❓ both block. ❓ is dispositioned explicitly — decided, or declared out of scope **in writing**. A premise with no executed evidence is ❓, not ✅.

## 3. High-level requirements (HLR)

> Derived from the READY user stories above using EARS patterns. Each HLR cites its source US(s); traceability to LLRs and tests is in §4 and §5.

### 3.1 Main window (US-001)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-001 | When mapper launches, the system shall display a home surface with three entry paths: **Consult maps**, **Plug a repo**, and **Construct**. | US-001 |
| HLR-002 | The Consult maps path shall list existing maps from the local store, ordered by most-recently opened by default. | US-001 |
| HLR-003 | The home surface shall expose keyboard shortcuts for each door on the key bar and shall activate the selected door on `Enter`. | US-001 |

### 3.2 Concept map — layered tree (US-002)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-004 | When the user opens a concept map, the system shall render it as a layered tree where every node is drawn as a ficha card. | US-002 |
| HLR-005 | While the map view is active, the system shall support keyboard navigation (`j`/`k` next/previous sibling, `h`/`l` parent/child) with a visible cursor. | US-002 |
| HLR-006 | The layered tree shall draw box-drawing edges between parent and child cards without visual breaks at cell crossings. | US-002 |

### 3.3 Required-field schema and coverage (US-003)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-007 | Each map shall declare a per-map required-field schema in its `nodos.yml` sidecar. | US-003 |
| HLR-008 | The system shall render per-node coverage of the required fields as letter badges (e.g. `D✓`/`D░` for document present/missing). | US-003 |
| HLR-009 | The system shall display a per-map coverage summary in the view header, computed from the current node set. | US-003 |

### 3.4 Super-legacy software tree (US-004)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-010 | The system shall load and render a super-legacy software system as a layered tree of module fichas. | US-004 |
| HLR-011 | Each legacy module card shall display its document chip, schema coverage letters, and creation tags. | US-004 |
| HLR-012 | The legacy tree shall reuse the same layered-tree renderer and navigation model as concept maps. | US-004 |

### 3.5 Mermaid round-trip (US-005)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-013 | The system shall import a map from a `.mmd` file written in `graph TD` syntax. | US-005 |
| HLR-014 | When the user saves a map, the system shall export it back to `.mmd` preserving node identifiers, labels, and parent/child edges. | US-005 |
| HLR-015 | The MVP parser shall support bare node ids, labelled nodes `A[label]`, directed edges `-->`, and edge labels `-->|text|`. | US-005 |

### 3.6 Repo as map — GitHub (US-006)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-016 | When the user plugs a GitHub repo, the system shall read it read-only via the authenticated `gh` CLI and render it as a lane map. | US-006 |
| HLR-017 | The lane map shall render branches as horizontal lanes, releases as diamond milestones, and commits as dots on a timeline. | US-006 |
| HLR-018 | For each branch lane the system shall display an ahead/behind chip and a CI verdict icon (`✓`/`✗`/`·`). | US-006 |

### 3.7 Radial mind maps (US-007)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-019 | When the user switches a map to radial view, the system shall render the root node centred-left and branch nodes radiating outward. | US-007 |
| HLR-020 | The radial view shall draw organic tapered Bézier edges and shall assign a distinct hue per top-level branch. | US-007 |

### 3.8 Search / jump (US-008)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-021 | When the user presses `/`, the system shall open a search prompt that matches node titles and all ficha content (notes, field values, attachment names). | US-008 |
| HLR-022 | While search results are active, the system shall reverse-light matched nodes on the canvas and display a tally of matching nodes. | US-008 |

### 3.9 Persistence — text truth + SQLite index (US-009)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-023 | The system shall persist every map as a pair of text files: `map.mmd` and `map_nodos.yml`. | US-009 |
| HLR-024 | When mapper opens a map, the system shall derive a local SQLite index from the text files and shall never commit that index to git. | US-009 |
| HLR-025 | If the SQLite index is deleted, the system shall rebuild an identical index the next time the map is opened. | US-009 |

### 3.10 Outline mode (US-010)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-026 | The system shall render the current map as an editable indented outline where indentation encodes parent/child relationships. | US-010 |
| HLR-027 | When the user re-indents a line in outline mode, the system shall re-parent the corresponding node in the map. | US-010 |

### 3.11 Export SVG/PNG (US-011)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-028 | When the user triggers export, the system shall write the current view to an SVG file. | US-011 |
| HLR-029 | When the user triggers export, the system shall write the current view to a PNG file. | US-011 |

### 3.12 Focus / collapse to subtree (US-012)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-030 | When the user focuses a node, the system shall hide all nodes outside the selected subtree and shall name the focus in the header. | US-012 |
| HLR-031 | When the user exits focus, the system shall restore the full map view. | US-012 |

### 3.13 Ficha in place (US-013)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-032 | When the user presses `Enter` on a node, the system shall display the node's ficha without leaving the map view. | US-013 |
| HLR-033 | The ficha shall display the node's notes, required-field values, links, and attachments. | US-013 |

### 3.14 Node attachments (US-014)

| ID | Requirement (EARS) | Source US |
|---|---|---|
| HLR-034 | Each node shall support zero or more attachments of kind `file`, `url`, or `image`, stored as references in the sidecar. | US-014 |
| HLR-035 | The ficha shall list attachments grouped by kind and shall open a URL or file path in the OS default application when activated. | US-014 |

## 4. Low-level requirements (LLR)

> Each LLR is a concrete design/implementation statement derived from one HLR. File references are `NEW` until implementation lands; they will be updated during Phase 3.

### 4.1 Main window (HLR-001..003)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-001.1 | The home screen shall be implemented as a Textual `Screen` with three `Button`/`ListView` widgets labelled Consult, Plug, Construct. | HLR-001 |
| LLR-001.2 | On `App.mount`, the system shall push `HomeScreen` as the initial screen. | HLR-001 |
| LLR-002.1 | The map store shall maintain a `last_opened` timestamp per map in the SQLite index and return maps ordered by it. | HLR-002 |
| LLR-003.1 | `HomeScreen` shall bind `q` to quit, `c` to focus Consult, `p` to focus Plug, `n` to focus Construct, and `Enter` to activate the focused door. | HLR-003 |

### 4.2 Concept map layered tree (HLR-004..006)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-004.1 | The layered tree layout shall compute `(x, y)` coordinates for each node with children placed below their parent and siblings spaced horizontally. | HLR-004 |
| LLR-004.2 | Each node shall be rendered as a `Canvas` cell region with a pill background, title line, and optional state chip. | HLR-004 |
| LLR-005.1 | The navigation model shall maintain a cursor node id and expose `next_sibling()`, `prev_sibling()`, `parent()`, `first_child()`. | HLR-005 |
| LLR-005.2 | The canvas shall redraw the selection highlight on every cursor move and shall scroll to keep the cursor visible. | HLR-005 |
| LLR-006.1 | The canvas shall merge box-drawing characters using connectivity bits (up/down/left/right) before writing to the terminal buffer. | HLR-006 |

### 4.3 Required-field schema and coverage (HLR-007..009)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-007.1 | The sidecar YAML shall contain a top-level `schema` list of field objects with `id`, `label`, `required`, and `kind`. | HLR-007 |
| LLR-007.2 | The parser shall reject a node whose required fields are missing from the schema definition. | HLR-007 |
| LLR-008.1 | Per-node coverage shall be rendered as a row of badge pairs `FIELD_SYMBOL+STATE` inside the card footer. | HLR-008 |
| LLR-009.1 | The header widget shall compute coverage as `sum(present_fields) / sum(required_fields)` across all nodes and display it as a percentage. | HLR-009 |

### 4.4 Super-legacy software tree (HLR-010..012)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-010.1 | A synthetic legacy fixture shall ship in `fixtures/legacy.mmd` and `fixtures/legacy_nodos.yml`. | HLR-010 |
| LLR-011.1 | Legacy module cards shall append a document chip (`ACTA-NNNN` or `SIN ACTA`) derived from the node's `document` field. | HLR-011 |
| LLR-012.1 | The legacy map shall be opened through the same `LayeredTreeScreen` class used for concept maps, with the fixture loaded into the store. | HLR-012 |

### 4.5 Mermaid round-trip (HLR-013..015)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-013.1 | `MermaidImporter.parse(text: str) -> Graph` shall recognise `graph TD`, lines matching `A --> B` and `A[label] --> B[label]`. | HLR-013 |
| LLR-013.2 | Edge labels `-->|text|` shall be parsed into the `GraphEdge.label` field. | HLR-013 |
| LLR-014.1 | `MermaidExporter.dump(graph: Graph) -> str` shall emit lines in `graph TD` form preserving node labels and edge labels. | HLR-014 |
| LLR-015.1 | The parser shall raise `ParseError` with line number on unknown syntax, and the MVP shall reject subgraphs and multiple parents. | HLR-015 |

### 4.6 Repo as map — GitHub (HLR-016..018)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-016.1 | `GitHubConnector(repo: str)` shall call `gh repo view` and `gh api repos/{owner}/{repo}/branches` and cache results for the session. | HLR-016 |
| LLR-016.2 | The connector shall cap fetched branches at 20 and commits per branch at 30, emitting `+N more` chips when exceeded. | HLR-016 |
| LLR-017.1 | `RepoLaneRenderer` shall map each branch to a horizontal lane row, releases to `◆` cells, and commits to `●` cells on a left-to-right time axis. | HLR-017 |
| LLR-018.1 | Each branch lane shall query `gh api repos/{owner}/{repo}/commits/{branch}` for ahead/behind against `HEAD` and query check-runs for the CI verdict. | HLR-018 |

### 4.7 Radial mind maps (HLR-019..020)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-019.1 | `RadialRenderer` shall place the root at `(cx, cy)`, distribute children across angular sectors, and recurse outward by depth. | HLR-019 |
| LLR-020.1 | Edges shall be drawn as quadratic Bézier curves whose stroke width tapers from root to leaf. | HLR-020 |
| LLR-020.2 | Each top-level branch shall receive a distinct hue from a fixed 8-colour severity-rationed palette. | HLR-020 |

### 4.8 Search / jump (HLR-021..022)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-021.1 | `SearchIndex` shall tokenise node titles, notes, field values, and attachment names into a SQLite `SEARCH` virtual table or equivalent inverted index. | HLR-021 |
| LLR-021.2 | The `/` key shall mount a modal `Input` bound to `SearchIndex.query(q)`. | HLR-021 |
| LLR-022.1 | Matching node ids shall be collected; the canvas shall paint matched cards with a reverse-video highlight and a footer tally `N nodos`. | HLR-022 |

### 4.9 Persistence (HLR-023..025)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-023.1 | `MapStore.save(map_id, graph, sidecar)` shall write `<map_id>.mmd` and `<map_id>_nodos.yml` to the workspace directory. | HLR-023 |
| LLR-024.1 | On open, `MapStore.open(map_id)` shall parse the text files and populate SQLite tables `nodes`, `edges`, `attachments`, `schema_fields`. | HLR-024 |
| LLR-024.2 | `mapper.db` shall be listed in `.gitignore` and the README shall state it is rebuildable and must not be committed. | HLR-024 |
| LLR-025.1 | A rebuild routine shall compare a hash of the text files against a stored hash; on mismatch or absence it shall re-create the index deterministically. | HLR-025 |

### 4.10 Outline mode (HLR-026..027)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-026.1 | `OutlineScreen` shall render the tree as indented text lines using two spaces per depth level. | HLR-026 |
| LLR-027.1 | On save in the outline editor, the parser shall compute parent from indentation and rebuild the `Graph` edges accordingly. | HLR-027 |
| LLR-027.2 | Re-parenting shall preserve node ids, ficha content, and attachments. | HLR-027 |

### 4.11 Export SVG/PNG (HLR-028..029)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-028.1 | Export shall use Rich `Console(record=True)` to capture the current view and call `console.save_svg(path, title=...)` for SVG output. | HLR-028 |
| LLR-029.1 | PNG export shall render the SVG to a raster via an available helper (e.g. `cairosvg` or `pillow`) and shall degrade gracefully if unavailable. | HLR-029 |

### 4.12 Focus / collapse (HLR-030..031)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-030.1 | `Graph.focus(node_id)` shall return a filtered graph containing only the selected node and its descendants. | HLR-030 |
| LLR-030.2 | The view header shall display `Focus: <node title>` while focus is active. | HLR-030 |
| LLR-031.1 | Pressing `Esc` or selecting "Unfocus" shall restore the unfiltered graph and clear the focus header. | HLR-031 |

### 4.13 Ficha in place (HLR-032..033)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-032.1 | Pressing `Enter` on a node shall open a `FichaModal` or bottom `FichaStrip` over the map without replacing the screen stack. | HLR-032 |
| LLR-033.1 | The ficha widget shall render sections: Title, State, Required fields, Notes, Links, Attachments. | HLR-033 |
| LLR-033.2 | If the ficha content exceeds the allocated strip height, the system shall promote it to a modal with scrollable content. | HLR-033 |

### 4.14 Node attachments (HLR-034..035)

| ID | LLR | Parent HLR |
|---|---|---|
| LLR-034.1 | The sidecar shall support an `attachments` list per node with fields `kind ∈ {file,url,image}`, `path`, and optional `caption`. | HLR-034 |
| LLR-035.1 | The ficha shall group attachments by kind and render `file` as `📎 path`, `url` as `🌐 caption`, `image` as `🖼️ path` (with Rich pixelation thumbnail when feasible). | HLR-035 |
| LLR-035.2 | Activating a URL attachment shall call `webbrowser.open`; activating a file attachment shall call `os.startfile` / `xdg-open` by platform. | HLR-035 |

## 5. Validation strategy

> Two-layer validation per dev-flow: Layer A (white-box) ties test cases `TC-NNN` to LLRs; Layer B (black-box) ties acceptance tests `AT-NNN` to user stories. All tests are automated unless marked manual.

### 5.1 Layer A — white-box test cases (`TC-NNN`)

| ID | Target LLR | Description | Oracles / reddening mutation |
|---|---|---|---|
| TC-001 | LLR-001.1 | `HomeScreen` mounts with three door widgets. | Remove a door → screen fails to mount. |
| TC-002 | LLR-003.1 | Pressing `c` focuses Consult; `Enter` pushes map-list screen. | Unbind `c` → focus does not move. |
| TC-003 | LLR-004.1, LLR-004.2 | A two-node graph renders parent above child with visible cards. | Swap y-coordinates → parent appears below child. |
| TC-004 | LLR-005.1 | Cursor moves from parent to first child on `l`. | Remove `first_child()` → cursor stays. |
| TC-005 | LLR-006.1 | A parent with two children renders a continuous `├─`/`└─` wire. | Clear connectivity bits → wires break into orphan segments. |
| TC-006 | LLR-007.1 | Parse a sidecar with schema `[document, owner, state]` and read field labels. | Omit `schema` key → parser raises. |
| TC-007 | LLR-008.1 | A node missing `document` renders `D░`; a complete node renders `D✓`. | Hard-code `D✓` → missing-field node appears complete. |
| TC-008 | LLR-009.1 | Header shows 50% when one of two nodes is complete. | Return 0% always → header lies. |
| TC-009 | LLR-010.1 | Fixture files exist and parse without error. | Delete fixture → load fails. |
| TC-010 | LLR-013.1, LLR-013.2 | Parse `graph TD\nA[x] -->|uses| B[y]` into two nodes and one labelled edge. | Drop edge-label regex → label lost. |
| TC-011 | LLR-014.1 | Export the parsed graph and re-parse; structure is identical. | Drop node labels → round-trip changes titles. |
| TC-012 | LLR-015.1 | Multiple-parent input `A --> C; B --> C` raises `ParseError`. | Allow multiple parents → tree invariant broken. |
| TC-013 | LLR-016.1 | `GitHubConnector` returns branch list for a public repo via `gh`. | Stub `gh` to fail → connector raises `GitHubError`. |
| TC-014 | LLR-016.2, LLR-017.1 | Repo map renders at least one lane row for `main`; when branches exceed the cap it renders `+N more`. | Empty branch list → no lanes rendered; remove cap → overflow not indicated. |
| TC-015 | LLR-018.1 | CI-failing branch renders `✗` chip. | Ignore check-runs → failing branch shows `·`. |
| TC-016 | LLR-019.1 | Radial renderer produces non-overlapping coordinates for a 3-node star. | Place all children at angle 0 → overlap. |
| TC-017 | LLR-020.2 | Two top-level branches receive different hues. | Use single colour → branches indistinguishable. |
| TC-018 | LLR-021.1 | Search query `acta` matches node with `document: acta-2024`. | Index only titles → match missed. |
| TC-019 | LLR-022.1 | A matched node is highlighted and tally reads `1 nodo`. | Disable highlighting → no visual feedback. |
| TC-020 | LLR-023.1 | Save writes both `.mmd` and `_nodos.yml`. | Skip sidecar write → only one file exists. |
| TC-021 | LLR-024.1, LLR-025.1 | Delete `mapper.db`; reopen rebuilds identical node count. | Corrupt hash → rebuild skipped, data missing. |
| TC-022 | LLR-026.1 | Outline screen renders root and child as indented lines. | Flatten indentation → hierarchy lost. |
| TC-023 | LLR-027.1 | Indent a line in outline and save; child becomes descendant. | Ignore indentation change → parent unchanged. |
| TC-024 | LLR-028.1 | Export SVG creates a file with `<svg>` root. | Record=False → empty/no SVG written. |
| TC-025 | LLR-030.1 | Focus on leaf returns graph with one node. | Focus includes siblings → subtree violated. |
| TC-026 | LLR-032.1 | `Enter` on node opens ficha widget without replacing screen. | Push full-screen editor → map view lost. |
| TC-027 | LLR-033.1 | Ficha widget contains attachment section when node has attachments. | Omit attachments section → US-014 invisible. |
| TC-028 | LLR-034.1, LLR-035.2 | Node with `url` attachment opens browser when activated. | Kind mismatch → file opener called for URL. |

### 5.2 Layer B — black-box acceptance tests (`AT-NNN`)

| ID | Source US | Shipped surface | Observable outcome / deliverable |
|---|---|---|---|
| AT-001 | US-001 | Home screen | User sees Consult / Plug / Construct doors with live keybinds. |
| AT-002 | US-002 | Concept map view | User sees layered tree with state-spined cards; cursor moves with j/k/h/l. |
| AT-003 | US-003 | Concept map header + cards | Missing-document node shows `SIN ACTA`; header coverage updates. |
| AT-004 | US-004 | Legacy fixture view | User sees module tree with document chips and schema letters; ficha shows owner/year. |
| AT-005 | US-005 | `.mmd` file on disk | Saving and re-importing produces the same tree. |
| AT-006 | US-006 | Repo lane view | User sees main lane with releases and feature lanes with CI chips. |
| AT-007 | US-007 | Radial view toggle | User sees root centred-left, coloured branches, curved edges. |
| AT-008 | US-008 | Search overlay | Typing `/acta` highlights matches and shows node tally. |
| AT-009 | US-009 | Workspace files | Only `.mmd` and `_nodos.yml` tracked; deleting `mapper.db` rebuilds map. |
| AT-010 | US-010 | Outline screen | User sees indented outline; re-indenting re-parents node. |
| AT-011 | US-011 | Export dialog | User receives SVG and PNG files matching the screen. |
| AT-012 | US-012 | Focus command | User sees only the focused subtree; unfocus restores full map. |
| AT-013 | US-013 | Ficha overlay | User sees notes/fields/links without leaving the map. |
| AT-014 | US-014 | Node ficha | User sees file/url/image attachments and can open a URL. |

### 5.3 Coverage summary

- **User stories:** 14 READY; each has at least one HLR, one LLR, one TC, and one AT.
- **HLR:** 35 (HLR-001..HLR-035).
- **LLR:** 47 (LLR-001.1..LLR-035.2).
- **TC:** 28 planned; implementation and pass/fail recorded in Phase 3.
- **AT:** 14 planned; execution recorded in Phase 4.

## 6. Appendices (optional)

### 6.2 Relevant design decisions

- The four diagram families share one node/edge machinery (prototypes prove
  it); new families are plug-ins.
- Persistence is two-layer with ONE truth: the text in git; SQLite is a
  derived, rebuildable index and is never committed.
- The legacy-tree ficha is the signature element the product is remembered
  by (tui-design): the required-field coverage drawn per node.
