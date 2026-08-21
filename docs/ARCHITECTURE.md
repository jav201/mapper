# Architecture — module map — mapper

> **Artifact language.** Canonical **English scaffold**; generate in the project's language.

> **Home: the REPO** (`docs/ARCHITECTURE.md`), versioned beside the code — **not** the vault. It is the
> **oracle** the A-family triggers read: from a document store no mechanical check could open it.
> It is a **standing project artifact**, not a per-batch one: batches amend it, they do not recreate it.

> **Distilled from IEEE 1016 by one selection rule: a viewpoint enters this map only if it FEEDS A
> TRIGGER.** In: **Composition** (A1/A2 + the source-file budget) · **Dependency** (A3 + parallelisation)
> · **Interface** (A3 + output-then-consume) · **Context** (the security family). Out — they belong in
> the design proposal, and only when they apply: Logical · Information · Patterns · Structure ·
> Interaction · State Dynamics · Algorithm · Resource. Keeping the other eight out is deliberate: a map
> that tries to describe everything stops being checkable, and a map that is not checkable is prose.

| Field | Value |
|---|---|
| Last amended by | `2026-08-18-batch-01` |
| Date | `2026-08-21` |

---

## 1 · Context — the system boundary

*(What is inside this system, what is outside it, and every service it talks to across the boundary.
This is what the security family reads: a new crossing here is a new attack surface.)*

| External actor / service | Direction | What crosses | Notes |
|---|---|---|---|
| Terminal emulator | out | Rendered characters, colours, key events | Width-1 glyphs only; no mouse required. |
| Local filesystem | in/out | `.mmd`, `_nodos.yml`, `mapper.db`, exported SVG/PNG | Text files are the truth; SQLite is rebuildable and never committed. |
| `gh` CLI (GitHub) | out | Read-only API calls: repo view, branches, commits, check-runs | Authenticated as the operator; no writes to GitHub. |
| OS default apps | out | URL/file open requests when activating attachments | Only for `url`/`file` attachment kinds. |

---

## 2 · Composition — the modules

**The `paths` column is the mechanical part.** It is what makes this a map and not an essay: any touched
file is classified by path prefix, so the A-family triggers can be evaluated by anyone, including a script.

| Module | Paths it owns | What it encapsulates | What it EXPOSES | What does NOT belong to it |
|---|---|---|---|---|
| `model` | `mapper/model.py` | The domain graph: nodes, edges, fichas, required-field schemas, attachments. | `Node`, `Edge`, `Graph`, `Ficha`, `Attachment`, `SchemaField`; immutable-ish value objects. | UI, persistence details, network calls. |
| `canvas` | `mapper/canvas.py` | Cell buffer, box-drawing wire merging, braille free-angle edges, pill backgrounds. | `Canvas(w, h)` with `put`, `wire`, `edge`, `elbow_down`, `text`, `dline`, `rows`. | Layout algorithms; diagram semantics. |
| `store` | `mapper/store.py` | Two-layer persistence: text files as truth, SQLite as rebuildable index. | `MapStore(path)` with `load(map_id)`, `save(map_id, graph, sidecar)`, `reindex()`. | Rendering, network, app lifecycle. |
| `views` | `mapper/views/*.py` | Diagram-family renderers over one `Graph` + `Canvas`. | `IRenderer.render(graph, selected_id, w, h) -> Text`; concrete renderers: `LayeredRenderer`, `LaneRenderer`, `RadialRenderer`, `OutlineRenderer`. | Persistence, network, app screens. |
| `mermaid` | `mapper/mermaid.py` | Mermaid `graph TD` round-trip. | `parse(src: str) -> Graph`, `dump(graph: Graph) -> str`. | UI, network. |
| `github` | `mapper/github.py` | Read-only GitHub repo-to-map adapter. | `GitHubConnector(repo: str) -> Graph`; raises `GitHubError`. | UI, persistence writes. |
| `search` | `mapper/search.py` | Inverted index over node titles + ficha content. | `SearchIndex(store)` with `query(q: str) -> list[str]` (node ids). | Rendering. |
| `export` | `mapper/export.py` | SVG/PNG export of the current view. | `save_svg(text: Text, path)`, `save_png(text: Text, path)`. | Network. |
| `app` | `mapper/app.py`, `mapper/screens/*.py` | Textual app, screens, widgets, key bindings, orchestration. | `MapperApp`, `HomeScreen`, `MapScreen`, `FichaModal`; binds keys and wires modules together. | Domain logic, persistence internals. |

**Staleness rule — the map checks itself.** A touched file that falls under **no** declared module means
this map is out of date: **ARQ fires on its own** and the map is amended before requirements are derived.
Silence is not an option here, because a stale map makes every A-family verdict meaningless.

- **Every path in the tree is claimed by exactly one module.** Overlapping prefixes are a defect of this
document, not an ambiguity to be resolved case by case.

---

## 3 · Dependency — who may reach whom

| Module | Depends on | Forbidden direction | Why the ban exists |
|---|---|---|---|
| `app` | `model`, `store`, `views`, `search`, `export`, `mermaid`, `github` | `model` → `app` | Domain must not know about screens or event loop. |
| `views` | `model`, `canvas` | `canvas` → `views` | Canvas is a dumb pixel buffer; it must not know about diagrams. |
| `store` | `model` | `store` → `app` / `views` | Persistence must not be coupled to UI or renderers. |
| `search` | `model`, `store` | `search` → `views` | Search returns ids; rendering decides how to highlight. |
| `mermaid` | `model` | `mermaid` → `app` / `views` | Importer/exporter are format adapters, not UI. |
| `github` | `model` | `github` → `app` / `store` | Connector produces a Graph; persistence is the caller's responsibility. |
| `export` | `views` (only through Text snapshots) | `export` → `app` | Export writes files from a Rich Text; it does not mount screens. |
| `canvas` | — | any → `canvas` except `views` | Canvas is the lowest-level drawing primitive. |
| `model` | — | any → `model` | Core domain has no outbound dependencies. |

*(The forbidden directions are the load-bearing part: they are what stops the graph becoming a mesh, and
they are what makes lanes parallelisable at all.)*

---

## 4 · Interfaces — the contracts between modules

| Interface | Owner module | Consumers | Shape | Frozen? |
|---|---|---|---|---|
| `Graph` value object | `model` | `store`, `views`, `search`, `mermaid`, `github`, `app` | `nodes: dict[str, Node]`; `edges: list[Edge]`; `root_id: str`; `focus(node_id) -> Graph` | yes for MVP |
| `Canvas` drawing buffer | `canvas` | `views` | `put(x,y,ch,tone)`, `wire(x,y,mask,tone)`, `elbow_down(...)`, `rows() -> list[str]` | yes for MVP |
| `MapStore` persistence | `store` | `app` | `load(map_id) -> (Graph, Sidecar)`, `save(map_id, graph, sidecar)`, `reindex()` | yes for MVP |
| `IRenderer.render` | `views` | `app` | `render(graph, selected_id, w, h, **kwargs) -> Text` | yes for MVP |
| `SearchIndex.query` | `search` | `app` | `query(q) -> list[str]` (node ids) | yes for MVP |
| `MermaidImporter/Exporter` | `mermaid` | `app` | `parse(src) -> Graph`, `dump(graph) -> str` | yes for MVP |
| `GitHubConnector.fetch` | `github` | `app` | `fetch(repo_slug) -> Graph` | yes for MVP |
| `save_svg` / `save_png` | `export` | `app` | `save_svg(text, path)`, `save_png(text, path)` | yes for MVP |

- **Changing one of these is trigger A3** — it fires ARQ, PDR *and* DDR, and it is never done inside a lane.
- A **frozen** interface is one the current batch committed to at PDR: no lane touches it; the work returns
to the trunk instead.

---

## 5 · Rationale — the decisions, and why

IEEE 1016 requires this section, and it earns its place for one practical reason: **it is what stops a
boundary being re-litigated every batch.** Record the decision, the alternative rejected, and what would
have to become true for the decision to be re-opened.

| # | Decision | Alternative rejected | What would re-open it |
|---|---|---|---|
| R-001 | Text files (`.mmd` + `_nodos.yml`) are the single source of truth; SQLite is a rebuildable index. | SQLite as primary store with export to text. | Need for real-time multi-user sync, or sub-second writes on maps >10k nodes. |
| R-002 | `model` has zero outbound dependencies. | Allow `model` to import `store` for lazy loading. | Need for lazy streams or ORM-style entities; current maps fit in memory. |
| R-003 | Diagram families are renderers over one `Graph`; no family-specific node types. | Separate node models per diagram family. | A family needs semantics that cannot be expressed as layout over generic nodes/edges. |
| R-004 | `gh` CLI is the only GitHub integration path; read-only. | Use PyGithub or REST directly. | `gh` becomes unavailable or the operator needs write access (out of MVP scope). |
| R-005 | Canvas merges box-drawing wires by connectivity bits; markers outrank wires. | Draw wires as simple character sequences without merge. | Prototype proved crossings break without merge; would only reopen if switching to a different rendering backend. |

---

## 6 · Parallelisation worksheet *(filled per batch, at ARQ)*

Two increments are parallelisable when **`modules(A) ∩ modules(B) = { }`**, **or** when they touch the
same domain on **different layers** (UI/UX vs functional) *and* the interface between them is frozen and
neither lane touches it.

| Lane | Modules | Layer | Files it owns | Disjoint from the others? |
|---|---|---|---|---|
| Inc-1 skeleton + store | `model`, `store` | functional | `mapper/model.py`, `mapper/store.py` | yes — no UI/render |
| Inc-2 layered canvas | `canvas`, `views` | functional | `mapper/canvas.py`, `mapper/views/layered.py` | touches `model` only through frozen Graph; disjoint file sets from Inc-1 |
| Inc-3 fichas + schema + legacy | `model` (schema), `views` | functional | `mapper/model.py` (schema), `mapper/views/layered.py`, fixtures | touches `model` and `views`; file overlap with Inc-2 on `views/layered.py` — **not parallel** |
| Inc-4 main window + nav + search | `app`, `search` | UI/UX + functional | `mapper/app.py`, `mapper/screens/*.py`, `mapper/search.py` | disjoint from Inc-1/2 files; depends on frozen interfaces |
| Inc-5 mermaid + outline | `mermaid`, `views` | functional | `mapper/mermaid.py`, `mapper/views/outline.py` | disjoint from Inc-4; touches `views` (outline) but distinct file from layered/radial |
| Inc-6 GitHub connector | `github` | functional | `mapper/github.py` | fully disjoint |
| Inc-7 radial + export + polish | `views`, `export` | functional + UI | `mapper/views/radial.py`, `mapper/export.py` | disjoint from Inc-5/6 except both in `views`; distinct file from outline |

If the intersection is **not** empty there are exactly two exits, and both are explicit decisions:

1. **re-cut the increments**, or
2. **move the module boundary — here, in this document**.

The second is the one that actually prevents spaghetti; the first only routes around it for one batch.

- ⚠ Same-domain lanes with an interface that is **not** frozen: that is not parallelism, it is a collision
with a delay — both lanes advance and meet the conflict at integration, the most expensive moment.
- **This orders the CODE.** The order of *merit* — what goes first — still comes from the intake risk estimate.
