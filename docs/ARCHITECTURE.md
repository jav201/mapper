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
| Last amended by | `2026-08-27-repair-batch-02` |
| Date | `2026-08-27` |

> **Amendment `2026-08-27-repair-batch-02` (`HLR-MAP.1`).** The `2026-08-26-ui-next-batch-02` ARQ was
> approved with this map amended, and **the amendment was never landed** — its `PLAN.md` §7 recorded
> as done work that did not exist on disk (C-44). This batch lands it, and in doing so found the map
> asserting **six** provably-false things about the tree, not the four the ARQ named.
>
> **Two rules were applied, and they pull in opposite directions.** Every *present-tense* claim here
> is now executed against disk. Every *forward-looking* commitment is marked as a commitment and is
> **not** written in the present tense — because the ARQ proposal declared `mapper/views/state.py`
> "new this batch" for a file that does not exist, and landing that verbatim would have traded a
> C-44 defect for a **false map**. This file is the oracle the A-family triggers read; a map that
> lies is worse than a map that is merely stale.

---

## 1 · Context — the system boundary

*(What is inside this system, what is outside it, and every service it talks to across the boundary.
This is what the security family reads: a new crossing here is a new attack surface.)*

| External actor / service | Direction | What crosses | Crossed by (only) | Notes |
|---|---|---|---|---|
| Terminal emulator | out | Rendered characters, colours, key events | `app`, `screens`, `widgets` | Width-1 glyphs only; no mouse required. |
| Local filesystem | in/out | `.mmd`, `_nodos.yml`, `mapper.db`, exported SVG/PNG | `store`, `export` | Text files are the truth; SQLite is rebuildable and never committed. |
| Local filesystem — spreadsheets | in | `.csv` / `.tsv` read for import preview | `import_csv` | Read-only; never writes back to the source file. |
| Local filesystem — OOXML | in/out | `.docx` / `.pptx` / `.xlsx` read as ZIP, placeholders substituted, re-zipped | `office` | **Archive-parsing surface.** Member names come from the archive; extraction/rewrite must never resolve outside the intended target (zip-slip). |
| `gh` CLI (GitHub) | out | Read-only API calls: repo view, branches, commits, check-runs | `github` | Authenticated as the operator; no writes to GitHub. |
| `git` CLI (local repo) | out | `git show HEAD:<path>` on the workspace, read-only, via `subprocess` | `diff` | Sub-process, `shell=False`, `check=True`, failures degrade to `None`. Never mutates the repo. |
| OS default apps | out | A URL or file path handed to the OS handler when an attachment is activated | `osopen` **only** | **Highest-risk crossing in the system.** The payload is *file-derived text*: attachment values are read out of `_nodos.yml`, which is user- or repo-supplied. Handing that to an OS handler is program execution driven by document content. Requires a scheme allowlist of `http`/`https` for `kind == "url"` **only** — local files travel as `kind == "file"` and are confined under the workspace root — and no shell. *(Narrowed by the batch-01 security review: allowing a `file:` URL would have given the URL branch an unconfined path. Narrowing is the safe direction, but the map and the design must not disagree in writing on the control the batch is gated on.)* |

- **The "Crossed by (only)" column is a ban, not a description.** A module not named on a row must not
  perform that crossing; if a second module needs it, the crossing moves behind the named module or this
  table is amended first.
- **`osopen` is the boundary, and it is one file.** It exists as its own module precisely so this crossing
  is a single-file audit surface: `grep` for the module, and you have seen every OS-handler launch in the
  product. No widget, screen or renderer may call it — see §3.

---

## 2 · Composition — the modules

**The `paths` column is the mechanical part.** It is what makes this a map and not an essay: any touched
file is classified by path prefix, so the A-family triggers can be evaluated by anyone, including a script.

| Module | Paths it owns | What it encapsulates | What it EXPOSES | What does NOT belong to it |
|---|---|---|---|---|
| `package` | `mapper/__init__.py` | Package identity only. | `__version__`. | **Everything else.** Any import or logic added here is a defect: it would make the package root a hidden dependency of every module. |
| `model` | `mapper/model.py` | The domain graph: nodes, edges, fichas, required-field schemas, attachments. | `Node`, `Edge`, `Graph`, `Ficha`, `Document`, `Attachment`, `SchemaField`; immutable-ish value objects. | UI, persistence details, network calls. |
| `canvas` | `mapper/canvas.py` | Cell buffer, box-drawing wire merging, braille free-angle edges, pill backgrounds. | `Canvas(w, h)` with `put`, `wire`, `edge`, `elbow_down`, `text`, `rows`. *(Corrected `2026-08-27-repair-batch-02`: the previous row also listed `dline`. Executed — `hasattr(Canvas, "dline")` is `False` and `grep -rn "dline" mapper/` returns nothing. It does not exist.)* | Layout algorithms; diagram semantics. |
| `store` | `mapper/store.py` | Two-layer persistence: text files as truth, SQLite as rebuildable index. | `MapStore(path)` with `load(map_id) -> Graph`, `save(map_id, graph)`, `create_seed`, `create_from_template`, `record_session`, `last_session`; `TEMPLATES`. *(Corrected `2026-08-27-repair-batch-02`: the previous row named a three-argument `save(map_id, graph, sidecar)` and a **public `reindex()`**. Executed — `store.py:452` is `save(self, map_id, graph)`, the sidecar is built inside `save` rather than passed in, and reindexing is **private** at `store.py:533`. The row also omitted four real public methods.)* | Rendering, network, app lifecycle. |
| `views` | `mapper/views/*.py` | Diagram-family renderers over one `Graph` + `Canvas`. **Headless: produce `rich.Text`, import no Textual.** | `IRenderer.render(graph, selected_id, w, h, **kwargs) -> Text`; `LayeredRenderer`, `LaneRenderer`, `HybridLaneRenderer`, `RailTimelineRenderer`, `RadialRenderer`, `OutlineRenderer`. | Persistence, network, app screens; **any Textual import**; any interactive/stateful tree — a renderer returns a picture, not a widget model. |
| `mermaid` | `mapper/mermaid.py` | Mermaid `graph TD` round-trip. | `parse(src: str) -> Graph`, `dump(graph: Graph) -> str`, `slugify(s) -> str`. | UI, network. |
| `import_csv` | `mapper/import_csv.py` | CSV/TSV row-set → `Graph` preview; orphan rows parked at root rather than dropped. | `preview_csv(path: Path) -> Graph`. | UI, persistence writes — it returns a `Graph`, the caller decides whether to save it. |
| `office` | `mapper/office.py` | OOXML (`.docx`/`.pptx`/`.xlsx`) `{{keyword}}` ingestion and substitution over `zipfile` + `re`. | `keywords(path)`, `resolve(path, values, out)` (template fill). | Domain semantics, UI, `model` — it deals in placeholder strings, not fichas. |
| `diff` | `mapper/diff.py` | Node-level diff of the working tree against `HEAD` via the local `git` CLI. | `DiffResult` (`added`, `removed`, `changed`, `removed_titles`), `git_diff(map_id, store) -> DiffResult \| None`. | Rendering decisions — it reports *what* changed; `views` decides how to tint it. |
| `github` | `mapper/github.py` | Read-only GitHub repo-to-map adapter over the `gh` CLI. | `GitHubConnector(repo: str) -> Graph`; raises `GitHubError`. | UI, persistence writes. |
| `search` | `mapper/search.py` | Inverted index over node titles + ficha content. | `SearchIndex(graph)` with `query(q: str) -> list[str]` (node ids). *(Corrected `2026-08-27-repair-batch-02`: the previous row gave the constructor's parameter as the store rather than the graph; executed, `search.py:7` takes a `Graph`. **And the module is dead code as found** — an AST walk of `mapper/app.py` shows it imports no `search` module, and `grep -rn "SearchIndex" mapper/ tests/` matches only its own definition. It is described here as what it is, not as what a consumer would need it to be.)* | Rendering. |
| `export` | `mapper/export.py` | SVG/PNG export of a rendered `rich.Text` snapshot. | `save_svg(text: Text, path)`, `save_png(text: Text, path)`. | Network; mounting screens. |
| `osopen` | `mapper/osopen.py` | **The OS-handler boundary.** Validates an attachment target and hands it to the platform opener. | `open_external(kind: str, target: str, *, workspace: Path, launcher=None) -> str`; returns a status word, never raises for input reachable from `yaml.safe_load`. | **Strict.** No `model`, no `store`, no `app`, no Textual, no Rich, no reading of `_nodos.yml`, no attachment *discovery*, no UI feedback, and no `shell=True`. It receives one already-extracted string plus the workspace root, validates it, opens it or raises. Deciding *which* attachment to open is `app`'s job; deciding *how to report the failure* is `app`'s job. |
| `keymap` | `mapper/keymap.py` | **The single seat for key chords.** One table, read by three consumers. | `KeyBinding(key, action, group)`, `KEYMAP: list[KeyBinding]`, `groups_for_keybar(...)`, `palette_items(query)`. | **Zero dependencies — not even Rich or Textual.** No styling, no widget, no `Binding` objects, no dispatch. It is data; the readers (keybar, palette, help, screen `BINDINGS`) do the shaping. |
| `design` | `mapper/darkside.py` | Darkside design system: palette tokens, glyph vocabulary, and **Rich-only** renderable builders (tab strip, keybar, panels). | `GROUND`/`PANEL`/`INK`/`ACCENT`/… tokens; `tab_strip`, `keybar`, `moon`, panel builders returning `rich.Text` / `rich.Panel`. | **Any Textual import** (that ban is the reason this is not merged into `widgets` — see R-006); `model`, `store`, app state. |
| `widgets` | `mapper/widgets/*.py`, `mapper/motion.py` | Textual widgets built on `design`: chrome (`TabStrip`, `KeyBar`, `HintLine`, `GroupBox`), the nine `Ds*` interaction components, the editable ficha inspector, the outline rail, and shared motion helpers. | `TabStrip`, `KeyBar`, `HintLine`, `GroupBox`, `Ds*` components, `FichaInspector`, `OutlineRail`; state changes leave as Textual `Message`s. | **Persistence and orchestration.** A widget never imports `store`, `views`, `screens`, `app` or `osopen`; it never saves a ficha and never launches an OS handler. It emits a message and `app` decides. |
| `screens` | `mapper/screens/*.py` | Full-screen and modal Textual screens that compose widgets into a task: palette, help, coverage, editor, factory, settings. | `CommandPalette`, `HelpScreen`, `CoverageScreen`, `EditorScreen`, `FactoryScreen`, `SettingsScreen`. | The `App` object and its lifecycle; domain logic; persistence internals. **`screens` must not import `app`** — see the recorded violation in §3. |
| `app` | `mapper/app.py` | The `App` object, the top-level screens still living in it (`HomeScreen`, `MapScreen`, `RepoScreen`, `PlugRepoScreen`, `_ImportPreviewScreen`) and their modals, plus all cross-module orchestration and persistence calls. | `MapperApp`, `HomeScreen`, `MapScreen`, `RepoScreen`; wires every module together. | Domain logic, persistence internals, drawing. |

**Staleness rule — the map checks itself.** A touched file that falls under **no** declared module means
this map is out of date: **ARQ fires on its own** and the map is amended before requirements are derived.
Silence is not an option here, because a stale map makes every A-family verdict meaningless.

- **Every path in the tree is claimed by exactly one module.** Overlapping prefixes are a defect of this
document, not an ambiguity to be resolved case by case.
- **No `mapper/*.py` wildcard is declared, deliberately.** Under `fnmatch` semantics `*` also matches `/`,
  so a single `mapper/*.py` glob would silently swallow `views/`, `screens/` and `widgets/` and every
  double-claim check would pass vacuously. Top-level files are therefore each named literally, and only
  the three package directories use a glob. Changing this is how the check stops working.
- **`mapper/app.py` is 1709 lines and holds eleven screen classes.** That is recorded here as a fact, not
  as an aspiration: it is the single reason this batch has no parallel lanes (§6), and the boundary move
  that would fix it is R-009.

---

## 3 · Dependency — who may reach whom

| Module | Depends on | Forbidden direction | Why the ban exists |
|---|---|---|---|
| `app` | `model`, `store`, `views`, `search`, `export`, `mermaid`, `import_csv`, `github`, `diff`, `keymap`, `design`, `widgets`, `screens`, `osopen` | `model` → `app` | Domain must not know about screens or event loop. |
| `screens` | `model`, `store`, `design`, `widgets`, `keymap`, `office` | **`screens` → `app`** | A screen is mounted *by* the app; importing back up is a cycle. **Known violation, recorded not waived:** `mapper/screens/factory.py:343` does a deferred `from mapper.app import _PromptScreen` — a function-local import used precisely to dodge the cycle at module load. Remediation: move `_PromptScreen` to `mapper/screens/prompt.py`. Not authorised in this batch; see §6 risk note. |
| `widgets` | `design`, `model` (read-only value objects), `keymap` | `widgets` → `store` / `views` / `screens` / `app` / `osopen` | A widget renders state and emits a `Message`; it does not persist, navigate, or execute. **This is the ban that shapes the editable inspector**: the inspector cannot save a ficha and cannot open an attachment — it says *what the user did* and `app` decides what that costs. |
| `views` | `model`, `canvas`, `design`, `diff` (the `DiffResult` value shape only) | `canvas` → `views`; **`views` → textual**; `views` → `store` / `app` | Canvas is a dumb pixel buffer. Renderers stay headless so `export` can snapshot them and so a renderer is testable without an event loop. |
| `store` | `model` | `store` → `app` / `views` | Persistence must not be coupled to UI or renderers. |
| `search` | `model`, `store` | `search` → `views` | Search returns ids; rendering decides how to highlight. |
| `mermaid` | `model` | `mermaid` → `app` / `views` | Importer/exporter are format adapters, not UI. |
| `import_csv` | `model`, `mermaid` (`slugify`) | `import_csv` → `app` / `store` | Preview builds a `Graph`; committing it is the caller's decision. |
| `office` | — (stdlib `zipfile` + `re`) | `office` → `model` / `app` | Template filling is string substitution over OOXML; it must not learn the domain. |
| `diff` | `model`, `store`, local `git` CLI | `diff` → `app` / `views` | Diff reports facts; presentation is downstream. |
| `github` | `model` | `github` → `app` / `store` | Connector produces a Graph; persistence is the caller's responsibility. |
| `export` | `views` (only through Text snapshots) | `export` → `app` | Export writes files from a Rich Text; it does not mount screens. |
| `osopen` | — (stdlib only) | `osopen` → anything in `mapper`; **`widgets` / `views` / `screens` → `osopen`** | Two bans, both load-bearing. Inbound: only `app` may launch an OS handler, so the call site is countable. Outbound: `osopen` importing `model` or `store` would let it discover its own targets, and the audit surface would stop being one file. |
| `design` | — (Rich + stdlib) | **`design` → textual**; `design` → `model` / `store` / `app` | `views` and `export` consume `design`; if `design` could import Textual, the headless-renderer ban above would become unenforceable by path prefix. See R-006. |
| `keymap` | — (stdlib only) | `keymap` → anything, including Rich and Textual | It is the seat three readers share. The moment it imports a UI type it stops being data and starts being one reader's opinion. |
| `canvas` | — | any → `canvas` except `views` | Canvas is the lowest-level drawing primitive. |
| `model` | — | any → `model` | Core domain has no outbound dependencies. |
| `package` | — | `package` → anything | `mapper/__init__.py` re-exporting anything makes the package root an implicit edge into every module. |

*(The forbidden directions are the load-bearing part: they are what stops the graph becoming a mesh, and
they are what makes lanes parallelisable at all.)*

**Verified at this amendment (`grep` over the tree, 2026-08-25):** `views/`, `darkside.py`, `export.py`,
`canvas.py`, `keymap.py`, `office.py`, `import_csv.py` and `diff.py` contain **no** Textual import. The
headless bans above describe the tree as it is, not as it is hoped to be. The one edge that contradicts
its ban is the `screens → app` back-edge named in the table.

**One smell recorded, not fixed.** `views/layered.py:9` imports `DiffResult` from `diff`, and `diff`
imports `store` — so there is a transitive `views → store` path in the import graph even though
`layered.py` uses `DiffResult` only as a read-only value shape. The clean fix is to move the `DiffResult`
dataclass into `model` and leave `diff.py` as the git adapter. That touches `views/layered.py`, which is
inside Inc-2's file set this batch, so doing it opportunistically would silently widen a lane. Deferred
deliberately — see R-011.

---

## 4 · Interfaces — the contracts between modules

| Interface | Owner module | Consumers | Shape | Frozen? |
|---|---|---|---|---|
| `Graph` value object | `model` | `store`, `views`, `search`, `mermaid`, `github`, `app` | `nodes: dict[str, Node]`; `edges: list[Edge]`; `root_id: str`; `focus(node_id) -> Graph` | yes for MVP |
| `Canvas` drawing buffer | `canvas` | `views` | `put(x,y,ch,tone)`, `wire(x,y,mask,tone)`, `edge(...)`, `elbow_down(...)`, `text(...)`, `rows() -> list[Text]` *(corrected `2026-08-27-repair-batch-02`: the previous row said `list[str]`; executed, `Canvas.rows` is annotated and returns `list[Text]`)* | yes for MVP |
| `MapStore` persistence | `store` | `app` | `load(map_id) -> Graph`, `save(map_id, graph)`, and the private `_reindex(...)` *(corrected `2026-08-27-repair-batch-02`: the previous row declared `load` returning a `(Graph, Sidecar)` tuple and a public `reindex()`; neither exists)* | yes for MVP |
| `IRenderer.render` | `views` | `app` | `render(graph, selected_id, w, h, **kwargs) -> Text` — **prose, not a Python type.** `grep -rn "IRenderer" mapper/` finds two mentions in comments and **no class and no `Protocol`**: the contract is enforced by convention among the renderer modules, not by the interpreter. | **yes.** *Not extended in `2026-08-25-ui-next-batch-01`, and still frozen here.* See the commitment row below. |
| `SearchIndex.query` | `search` | — **none** | `query(q) -> list[str]` (node ids) *(corrected `2026-08-27-repair-batch-02`: the consumer column said `app`. Executed, `app` does not import `search`; the module has zero consumers in the tree.)* | yes for MVP |
| `MermaidImporter/Exporter` | `mermaid` | `app` | `parse(src) -> Graph`, `dump(graph) -> str` | yes for MVP |
| `GitHubConnector.fetch` | `github` | `app` | `fetch(repo_slug) -> Graph` | yes for MVP |
| `save_svg` / `save_png` | `export` | `app` | `save_svg(text, path)`, `save_png(text, path)` | yes for MVP |
| `DiffResult` value shape | `diff` | `views`, `app` | `added`, `removed`, `changed`, `removed_titles` | yes for this batch (see R-011) |
| `preview_csv` | `import_csv` | `app` | `preview_csv(path) -> Graph` | yes for this batch |
| Darkside tokens + renderables | `design` | `views`, `screens`, `widgets`, `app` | Colour tokens; builders returning `rich.Text` / `rich.Panel` | yes for this batch — four consumers, no lane owns it |
| `Ds*` interaction components | `widgets` | `screens`, `widgets` (inspector) | Nine `Static`-based components, three states each, changes emitted as `Message` | **yes for this batch.** Inc-2 builds the inspector *from* them; it must not change their signatures. |
| `KeyBar` / `HintLine` / `TabStrip` chrome | `widgets` | `screens`, `app` | `set_groups(...)`, `set_crumb(...)`, (new) `HintLine` setter | **NO — Inc-2 owns it.** HintLine gains a setter and the keybar gains visible truncation. No other lane edits `widgets/chrome.py`. |
| `KEYMAP` seat | `keymap` | `screens`, `widgets`, `app` | `KEYMAP: list[KeyBinding]`, `groups_for_keybar(...)`, `palette_items(q)` | **NO — Inc-1 owns it.** It becomes the single source from which screens generate `BINDINGS`. No other lane edits `mapper/keymap.py`. |
| **`ViewState` parameter object** · **COMMITTED, NOT PRESENT** | `views` | `app` | Frozen dataclass carrying the renderer's whole parameter surface; `IRenderer` promoted to a real `typing.Protocol` with `render(self, graph: Graph, state: ViewState) -> Text` | **⚠ NOT YET IN THE TREE.** Committed at the `2026-08-26-ui-next-batch-02` PDR (pre-authorised trigger A3), **lands in that batch's Inc-2**. `mapper/views/state.py` **does not exist today** — verified by path check. Recorded here as a commitment so the map states a plan without asserting a falsehood; the row becomes present-tense only when the file lands. |
| **`Canvas` `dots` / `bgs` layers** · **COMMITTED, NOT PRESENT** | `canvas` | `views` | `Canvas.__init__` declares `dots` and `bgs` as empty mappings; `rows()` composes them into the painted output in a declared order; out-of-bounds writes are dropped, not raised | **⚠ NOT YET IN THE TREE.** This is the batch's **second** A3, distinct from the `ViewState` row above. Committed at the `2026-08-26-ui-next-batch-02` PDR, **lands in that batch's Inc-1**. Verified 2026-08-27: `mapper/canvas.py` declares neither attribute — today `RadialRenderer` **monkey-patches** `cv.dots = {}` / `cv.bgs = {}` onto the instance, and `rows()` drops both layers. Recorded here so the second A3 is committed somewhere; the row becomes present-tense only when `canvas.py` declares them. |
| `open_external` | `osopen` | `app` **only** | `open_external(kind, target, *, workspace, launcher=None) -> str`; returns a status word | **NO — new, Inc-4 owns it.** Security-reviewed before Inc-4 signs off. |

- **Changing one of these is trigger A3** — it fires ARQ, PDR *and* DDR, and it is never done inside a lane.
- A **frozen** interface is one the current batch committed to at PDR: no lane touches it; the work returns
to the trunk instead.
- An interface marked **"NO — Inc-N owns it"** is the inverse case: it is deliberately in motion this
batch, and exactly one increment may move it. A second lane editing it is the same collision as breaking
a freeze, just harder to see.

### `IRenderer.render` is frozen this batch — stated plainly

`render(graph, selected_id, w, h, **kwargs) -> Text` **is not extended in
`2026-08-25-ui-next-batch-01`.** Canvas pan, fold, minimap and braille work is **batch 2 and out of
scope**. Two consequences the requirements phase must honour, because both are easy to violate by
accident:

1. **The «taller» recompose is a width change, nothing more.** The centre canvas gets a smaller `w`
   because the rail and the inspector take columns either side. `LayeredRenderer` already accepts that;
   no signature moves. If a story needs the renderer to know *about* the rail or the inspector, the story
   is out of scope.
2. **The rail must be built from `Graph`, not from a renderer.** `render` returns `rich.Text` — a
   picture. A collapsible outline tree with per-branch missing-field counts is a *structure*, and no
   amount of `**kwargs` extracts structure back out of a `Text`. Reusing `OutlineRenderer` for the rail
   would force `render` to return something other than `Text`, which is an A3 change and returns to the
   trunk. `widgets` → `model` is allowed (§3) precisely so the rail can compute its own tree.

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
| R-006 | **`design` (`darkside.py`, Rich-only) and `widgets` (Textual) are two modules, not one `ui` module.** | Merge them into a single `ui` module owning `darkside.py` + `widgets/*.py`. | If `darkside` ever genuinely needs a Textual concept (a reactive, a DOM query), or if `views` stops consuming `darkside` — then the ban has nothing left to protect and merging is free. |
| R-007 | **`keymap` is its own zero-dependency module**, not a file inside `app` or `design`. | Keep the key table next to the screens that bind it (inside `app`). | If the keybar stops reading the keymap — i.e. if `widgets` no longer needs it — the seat could fold into `app` without creating a cycle. |
| R-008 | **`osopen` is its own single-file module** for the OS-handler crossing. | A helper function inside `app.py`, next to the attachment action. | Nothing plausible. This one is close to a one-way door in the good direction: the whole value is that the crossing is greppable by path. Re-open only if the product stops opening attachments at all. |
| R-009 | **`screens` is split from `app` in the map, but `mapper/app.py` is NOT split in this batch.** | Extract `MapScreen` (and the four sibling screens and five modals) out of the 1709-line `app.py` into `mapper/screens/*.py` now, as an Inc-0. | Cost/benefit. The extraction is the *only* move that would give this batch file-level lanes (§6), but it is a large, purely-structural diff across every increment's blast radius, landing before any of them can start, with no user-visible outcome and no acceptance test of its own. **Re-open it when:** a batch has ≥3 increments that touch `app.py` for genuinely unrelated reasons *and* the batch has slack for a no-outcome increment — or when a merge conflict in `app.py` actually costs more than the extraction would. Both are plausible by batch 3. |
| R-010 | **`IRenderer.render` stays frozen through this batch**; the rail computes its own tree from `Graph`. | Extend `render` to return a structured tree (or add a `render_tree`) so the rail can reuse `OutlineRenderer`'s layout logic. | Batch 2 (pan/fold/minimap/braille) already has to reopen the renderer contract. Bundling the rail's needs into *that* conversation is cheap; bundling it into *this* batch is an A3 change mid-flight. Some tree-walk duplication between the rail and `OutlineRenderer` is the accepted price for one batch. |
| R-011 | **`DiffResult` stays in `diff`**, keeping the transitive `views → diff → store` import path, for one more batch. | Move the `DiffResult` dataclass to `model` and leave `diff.py` as the pure git adapter. | The fix is small and correct, but its file (`views/layered.py`) sits inside Inc-2's lane this batch, so taking it now widens a lane for an unrelated reason. Re-open at the start of any batch that does not touch `views/layered.py` — it should be a standalone two-file increment. |

---

## 6 · Parallelisation worksheet *(filled per batch, at ARQ)*

Two increments are parallelisable when **`modules(A) ∩ modules(B) = { }`**, **or** when they touch the
same domain on **different layers** (UI/UX vs functional) *and* the interface between them is frozen and
neither lane touches it.

### Current batch — `2026-08-25-ui-next-batch-01` (variant A «taller», five P1 stories)

*(The `2026-08-18-batch-01` worksheet is superseded and removed; it described a module cut that no longer
matches the tree.)*

| Lane | Modules | Layer | Files it owns | Disjoint from the others? |
|---|---|---|---|---|
| Inc-1 · US-N03 keymap seat + executing palette + scoped help | `keymap`, `screens`, `app` | UI/UX | `mapper/keymap.py`, `mapper/screens/palette.py`, `mapper/screens/help.py`, `mapper/app.py` | **No** — `app` |
| Inc-2 · US-N01 taller recompose + editable inspector | `widgets`, `views`, `app` | UI/UX | `mapper/widgets/inspector.py` *(new)*, `mapper/widgets/chrome.py`, `mapper/views/layered.py`, `mapper/app.py` | **No** — `app` |
| Inc-3 · rail + coverage lattice | `widgets`, `app` | UI/UX | `mapper/widgets/rail.py` *(new)*, `mapper/app.py` | **No** — `app`, `widgets` |
| Inc-4 · US-N02 attachments | `osopen`, `widgets`, `app` | functional + UI/UX | `mapper/osopen.py` *(new)*, `mapper/widgets/inspector.py`, `mapper/app.py` | **No** — `app`, `widgets` |
| Inc-5 · US-N04 coverage worklist | `screens`, `widgets`, `app` | UI/UX | `mapper/screens/coverage.py`, `mapper/widgets/inspector.py`, `mapper/app.py` | **No** — `app`, `widgets`, `screens` |
| Inc-6 · US-N05 confirm-before-destroy + app-level undo | `app` | functional + UI/UX | `mapper/app.py` | **No** — `app` |

**Verdict: 0 of the 15 pairs are parallelisable. `modules(A) ∩ modules(B) ⊇ {app}` for every pair,
without exception.** There is no lane to manufacture here and the worksheet does not pretend otherwise.

| Pair | Intersection | Parallel? |
|---|---|---|
| 1–2 | `{app}` | no |
| 1–3 | `{app}` | no |
| 1–4 | `{app}` | no |
| 1–5 | `{app, screens}` | no |
| 1–6 | `{app}` | no |
| 2–3 | `{app, widgets}` | no |
| 2–4 | `{app, widgets}` | no — **plus a file collision on `widgets/inspector.py`** |
| 2–5 | `{app, widgets}` | no — **plus a file collision on `widgets/inspector.py`** |
| 2–6 | `{app}` | no |
| 3–4 | `{app, widgets}` | no |
| 3–5 | `{app, widgets}` | no |
| 3–6 | `{app}` | no |
| 4–5 | `{app, widgets}` | no — **plus a file collision on `widgets/inspector.py`** |
| 4–6 | `{app}` | no |
| 5–6 | `{app}` | no |

**Two of these are ordering dependencies, not merely conflicts.** `mapper/widgets/inspector.py` does not
exist yet: Inc-2 creates it, Inc-4 and Inc-5 extend it. Inc-4 and Inc-5 therefore **cannot start** before
Inc-2 lands — re-cutting cannot fix that, only sequencing can. Likewise Inc-1 must land first: once
`keymap` is the single source from which every screen generates `BINDINGS`, any increment that adds a key
(Inc-3's rail toggle, Inc-4's open-attachment, Inc-5's jump-to-node, Inc-6's confirm) is editing the seat
Inc-1 owns.

**Recommended execution: one serial chain, `Inc-1 → Inc-2 → Inc-3 → Inc-4 → Inc-5 → Inc-6`.** Inc-6 is
the only lane whose module set is a strict singleton (`{app}`) and whose diff is small and self-contained;
it is the one that could be resequenced freely if a gate stalls.

**What would change the verdict — and what would not.** Splitting `screens` out of `app` in *this
document* changed nothing, because the binding constraint is a single 1709-line **file**, not a module
label: `mapper/app.py` holds `MapperApp`, `HomeScreen`, `MapScreen`, `RepoScreen`, `PlugRepoScreen`,
`_ImportPreviewScreen` and five modals. Every increment above reaches into it.

- **Extracting `MapScreen` and its siblings into `mapper/screens/*.py` (R-009)** would give the lanes
  *distinct files* — a real reduction in merge pain. It would **not** make them parallel under the stated
  rule, because they would then all intersect on `screens` instead of on `app`. Honest framing: it buys
  conflict-freedom, not concurrency.
- **The only move that yields true module-level disjointness** is making the rail and the inspector
  self-contained widgets that own their own state and communicate with the app purely through Textual
  `Message`s — which §3 already mandates. Even then `app.py` must mount them, so the lanes converge on a
  handful of lines. At this size that is a serial chain wearing a costume.

Recording it this way is the point: the worksheet's job is to tell the truth about whether lanes exist,
and this batch's truth is that they do not.

If the intersection is **not** empty there are exactly two exits, and both are explicit decisions:

1. **re-cut the increments**, or
2. **move the module boundary — here, in this document**.

The second is the one that actually prevents spaghetti; the first only routes around it for one batch.

- ⚠ Same-domain lanes with an interface that is **not** frozen: that is not parallelism, it is a collision
with a delay — both lanes advance and meet the conflict at integration, the most expensive moment.
- **This orders the CODE.** The order of *merit* — what goes first — still comes from the intake risk estimate.

### Architectural risks this cut hands to the requirements phase

*(Recorded here because each one is a boundary question that a story can violate by accident, and three of
them would force a frozen-interface change if a story is written carelessly.)*

| # | Risk | Where it bites | What requirements must settle |
|---|---|---|---|
| A-1 | **Rail built from a renderer instead of from `Graph`.** `IRenderer.render -> Text` cannot yield a collapsible tree with per-branch counts. | Inc-3 | Write the rail story against `Graph`, never against `OutlineRenderer`. A story phrased "the rail reuses the outline view" is an **A3 frozen-interface change and out of scope** — it returns to the trunk. |
| A-2 | **Missing-field computation duplicated** across the rail's coverage lattice (Inc-3) and the coverage worklist (Inc-5); `screens/coverage.py` already computes it from `Graph` + `SchemaField`. | Inc-3, Inc-5 | Name one owner for a `missing_fields(node, schema)` helper in `model`. Adding a function to `model` is **additive, not a frozen-interface change** — but two lanes writing it independently is how the two views drift apart and disagree about what "complete" means. |
| A-3 | **The editable inspector has no write path of its own** — §3 bans `widgets → store`. Persistence is `MapStore.save(map_id, graph, sidecar)`, a **whole-graph** write over the frozen interface. | Inc-2 | Define the commit point explicitly (on field blur / on confirm / on explicit save). Per-keystroke saving rewrites `.mmd` + `_nodos.yml` on every character. **Do not add `save_field` to `MapStore`** — that is A3. If the answer needs a partial write, it comes back to the trunk. |
| A-4 | **`osopen` receives untrusted, file-derived text.** Attachment targets come out of `_nodos.yml`, which is user- or repo-supplied. Launching an OS handler on it is program execution driven by document content. | Inc-4 | Acceptance criteria must cover the *rejections*, not only the happy path: scheme allowlist (`http`/`https` for `url` only), `file` targets confined under the workspace root **whether or not they exist**, no shell invocation, and a visible non-fatal error for anything rejected. **`security-reviewer` signs off before Inc-4 closes.** This is the batch's real attack surface. |
| A-5 | **The seat already depends on an unwritten scoping rule.** `mapper/keymap.py` binds five chords twice: `f` → `fábrica[doors]` / `alternar foco[view]`; `j`,`k`,`↵`,`esc` → a `nav`/`edit` action *and* a `palette` action. Four are clearly deliberate (the `palette` group is a modal scope), which is exactly the problem: **the group→scope mapping that makes them safe is nowhere declared.** Harmless while the keybar only *displays* the table; a silent shadowing bug the moment screens generate `BINDINGS` from it. `f` is the one that is not obviously safe — `doors` and `view` are both non-modal. | Inc-1 | Write the group→scope mapping down, and state the collision rule: a duplicate chord *within one active scope* is an error, not last-wins. Resolve `f` explicitly (confirm `doors` and `view` are never co-active, or rebind one). A test should assert the seat has no intra-scope duplicates — otherwise this recurs every time a lane adds a key. |
| A-6 | **App-level undo changes where undo state lives.** `MapScreen.action_undo` exists today at screen level (`mapper/app.py:1544`); "app-level" means the state moves to `MapperApp` to survive screen pops. | Inc-6 | Settle whether undo is an in-memory `Graph` snapshot or a store-level revert, and whether it must undo a destroy that already reached `store.save`. Also settle the depth (single-step vs stack) — the story says "undo", which is not a specification. |
| A-7 | **Known `screens → app` back-edge** at `mapper/screens/factory.py:343`. Inc-1 touches both modules, so it is the tempting place to fix it. | Inc-1 | Fixing it (move `_PromptScreen` to `mapper/screens/prompt.py`) is **scope-add** and needs approval; leaving it is acceptable for this batch. What is not acceptable is fixing it silently inside a US-N03 increment. |
