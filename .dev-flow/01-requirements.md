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

> Lands in Phase 1, derived from the READY stories above (EARS patterns, two-level HLR/LLR, dual traceability).

## 4. Low-level requirements (LLR)

> Lands in Phase 1.

## 5. Validation strategy

> Lands in Phase 1 (Layer A `TC-NNN` ↔ LLR/HLR, Layer B `AT-NNN` ↔ US).

## 6. Appendices (optional)

### 6.2 Relevant design decisions

- The four diagram families share one node/edge machinery (prototypes prove
  it); new families are plug-ins.
- Persistence is two-layer with ONE truth: the text in git; SQLite is a
  derived, rebuildable index and is never committed.
- The legacy-tree ficha is the signature element the product is remembered
  by (tui-design): the required-field coverage drawn per node.
