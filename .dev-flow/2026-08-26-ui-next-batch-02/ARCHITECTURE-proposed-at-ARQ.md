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
| Last amended by | `2026-08-26-ui-next-batch-02` |
| Date | `2026-08-26` |

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
| `canvas` | `mapper/canvas.py` | Cell buffer, box-drawing wire merging, braille free-angle edges, pill backgrounds. | `Canvas(w, h)` with `put`, `wire`, `edge`, `elbow_down`, `text`, `rows`. **Un-frozen this batch** — gains declared `dots` / `bgs` layers that `rows()` actually reads (see §4 and R-016). | Layout algorithms; diagram semantics. |
| `store` | `mapper/store.py` | Two-layer persistence: text files as truth, SQLite as rebuildable index. | `MapStore(path)` with `load(map_id) -> Graph`, `save(map_id, graph)`, `create_seed`, `create_from_template`, `record_session`, `last_session`; `TEMPLATES`. *(Corrected 2026-08-26: the previous row named a three-argument `save(map_id, graph, sidecar)` and a public `reindex()`; executed, `store.py:217` is `save(self, map_id, graph)` and reindexing is private at `store.py:288`. The sidecar is built inside `save`, not passed in.)* | Rendering, network, app lifecycle. |
| `views` | `mapper/views/*.py` | Diagram-family renderers over one `Graph` + `Canvas`, **plus the parameter object that is their contract** (`mapper/views/state.py`, new this batch). **Headless: produce `rich.Text`, import no Textual.** | `ViewState` (frozen dataclass), `IRenderer` (a real `typing.Protocol`) with `render(graph: Graph, state: ViewState) -> Text`; `LayeredRenderer`, `LaneRenderer`, `HybridLaneRenderer`, `RailTimelineRenderer`, `RadialRenderer`, `OutlineRenderer`. | Persistence, network, app screens; **any Textual import**; any interactive/stateful tree — a renderer returns a picture, not a widget model. **A renderer never decides what matches** — it receives id sets (see R-014). |
| `mermaid` | `mapper/mermaid.py` | Mermaid `graph TD` round-trip. | `parse(src: str) -> Graph`, `dump(graph: Graph) -> str`, `slugify(s) -> str`. | UI, network. |
| `import_csv` | `mapper/import_csv.py` | CSV/TSV row-set → `Graph` preview; orphan rows parked at root rather than dropped. | `preview_csv(path: Path) -> Graph`. | UI, persistence writes — it returns a `Graph`, the caller decides whether to save it. |
| `office` | `mapper/office.py` | OOXML (`.docx`/`.pptx`/`.xlsx`) `{{keyword}}` ingestion and substitution over `zipfile` + `re`. | `keywords(path)`, `resolve(path, values, out)` (template fill). | Domain semantics, UI, `model` — it deals in placeholder strings, not fichas. |
| `diff` | `mapper/diff.py` | Node-level diff of the working tree against `HEAD` via the local `git` CLI. | `DiffResult` (`added`, `removed`, `changed`, `removed_titles`), `git_diff(map_id, store) -> DiffResult \| None`. | Rendering decisions — it reports *what* changed; `views` decides how to tint it. |
| `github` | `mapper/github.py` | Read-only GitHub repo-to-map adapter over the `gh` CLI. | `GitHubConnector(repo: str) -> Graph`; raises `GitHubError`. | UI, persistence writes. |
| `search` | `mapper/search.py` | **The single definition of "what matches".** Free-text hits over a `Graph`, and (new this batch) the `key:value` **lens** query language: parse, then evaluate against schema fields and node state. Pure functions over `model` — no I/O, no event loop, **Layer-0**. | `SearchIndex(graph)` with `query(q: str) -> list[str]`; `parse_lens(q) -> LensQuery`, `lens_hits(graph, q) -> list[str]`. *(Corrected 2026-08-26: the previous row said `SearchIndex(store)`; executed, `search.py:10` takes a `Graph`. **And the module is dead code as found** — `grep -rn "mapper.search\|SearchIndex" mapper/ tests/` returns nothing outside its own file. This batch resurrects it rather than deleting it; see R-014.)* | Rendering, and **deciding how a match is drawn** — it returns ids. |
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
- **`mapper/app.py` is 2009 lines and holds eleven screen classes** (`wc -l`, 2026-08-26; it was 1709 at
  the previous amendment). That is recorded here as a fact, not as an aspiration: it is the single reason
  this batch has no parallel lanes (§6), and the boundary move that would fix it is R-009.

### 2b · Coverage roots — the top-level declaration validator **V8** reads

*(Added 2026-08-26. Rationale R-015.)*

The `paths` column above is **per-file by design** and stays that way — it is the fine-grained oracle.
This block is a **second, coarser declaration** that exists for one mechanical reason: `devflow-validate.py`'s
V8 rule scans for backticked *directory-slash-star-star* tokens and, finding none, reported that the map
declares no path-glob prefixes and cannot be checked, on every run. Executed against the rule's
source (`~/.claude/docs/tools/devflow-validate.py:244-261`): **V8 computes orphans only** — every tracked
`.py`/`.ts`/`.tsx`/`.js` file must start with a declared prefix. It performs **no double-claim check**, so
the §2 objection that a coarse glob would make double-claiming vacuous does not apply to V8 and cost
nothing to satisfy.

**The glob tokens in this section are load-bearing, and only these three.** V8 harvests them by regex from
the whole document, so a glob token written anywhere else — even inside prose quoting the rule itself —
becomes a declared coverage root. That is why the sentence above spells the pattern out in words instead
of quoting it. Whoever amends this map must keep it that way, or the root count silently stops matching
the table.

| Coverage root | Status | What it means |
|---|---|---|
| `mapper/**` | product source | Every file here is additionally claimed by exactly one module row in §2. The per-file rows, not this line, are what the A-family triggers read. |
| `tests/**` | test source | Not a module. Tests are uncapped by the increment source budget and are claimed by no module row. |
| `prototypes/**` | **non-product, never staged** | Design-intent generators only. **No batch touches or stages anything under this root** — declaring it here turns that standing rule into a greppable map row instead of a convention carried in briefs. |

Executed 2026-08-26: `git ls-files | grep -E '\.(py|ts|tsx|js)$'` → 69 files, distributed
`mapper` 33 · `prototypes` 9 · `tests` 27. **Zero fall outside the three roots**, so V8 has a real (if
coarse) thing to check: a new top-level source directory appearing without a map amendment.

---

## 3 · Dependency — who may reach whom

| Module | Depends on | Forbidden direction | Why the ban exists |
|---|---|---|---|
| `app` | `model`, `store`, `views`, `search`, `export`, `mermaid`, `import_csv`, `github`, `diff`, `keymap`, `design`, `widgets`, `screens`, `osopen` | `model` → `app` | Domain must not know about screens or event loop. |
| `screens` | `model`, `store`, `design`, `widgets`, `keymap`, `office` | **`screens` → `app`** | A screen is mounted *by* the app; importing back up is a cycle. **Known violation, recorded not waived:** `mapper/screens/factory.py:343` does a deferred `from mapper.app import _PromptScreen` — a function-local import used precisely to dodge the cycle at module load. Remediation: move `_PromptScreen` to `mapper/screens/prompt.py`. Not authorised in this batch; see §6 risk note. |
| `widgets` | `design`, `model` (read-only value objects), `keymap` | `widgets` → `store` / `views` / `screens` / `app` / `osopen` | A widget renders state and emits a `Message`; it does not persist, navigate, or execute. **This is the ban that shapes the editable inspector**: the inspector cannot save a ficha and cannot open an attachment — it says *what the user did* and `app` decides what that costs. |
| `views` | `model`, `canvas`, `design`, `diff` (the `DiffResult` value shape only) | `canvas` → `views`; **`views` → textual**; `views` → `store` / `app` | Canvas is a dumb pixel buffer. Renderers stay headless so `export` can snapshot them and so a renderer is testable without an event loop. |
| `store` | `model` | `store` → `app` / `views` | Persistence must not be coupled to UI or renderers. |
| `search` | `model` **only** | `search` → `views` / `store` / `app` | Search returns ids; rendering decides how to *draw* them but never re-decides *which*. **Corrected 2026-08-26:** the previous row declared a dependency on `store` that does not exist — executed, `mapper/search.py` imports `from .model import Graph` and nothing else. Keeping `search` free of `store` is what makes it Layer-0 and lets the lens parser be unit-tested with no filesystem. |
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

**Two edges in the `app` row are declared but do NOT exist in the code (executed 2026-08-26).**
`grep -n "^from\|^import" mapper/app.py` (lines 1-46) shows imports of `darkside`, `diff`, `export`,
`github`, `import_csv`, `keymap`, `mermaid`, `model`, `motion`, `osopen`, `screens`, `store`,
`views.layered`, `views.outline`, `views.radial`, `widgets.*` — **and no `search`**. The `app → search`
edge is therefore an *intent*, not a fact, and `mapper/search.py` currently has zero consumers anywhere in
`mapper/` or `tests/`. This batch makes the edge real (R-014). Recording it as a gap rather than deleting
the row is deliberate: a dependency table that describes hopes is exactly as untrustworthy as one that
describes bans nobody enforces.

**The edge this batch deliberately did NOT create: `views → search`.** The figure-ground lens and the
search highlight both need "which nodes matched". Passing a *predicate* or a parsed `LensQuery` into the
renderer would have added `views → search`; passing a `frozenset[str]` of ids adds nothing, because
`frozenset` is a builtin. The renderer paints a set; it never evaluates a query. See R-014.

**Verified at this amendment (`grep` over the tree, 2026-08-25):** `views/`, `darkside.py`, `export.py`,
`canvas.py`, `keymap.py`, `office.py`, `import_csv.py` and `diff.py` contain **no** Textual import. The
headless bans above describe the tree as it is, not as it is hoped to be. The one edge that contradicts
its ban is the `screens → app` back-edge named in the table.

**One smell recorded, not fixed.** `views/layered.py:9` imports `DiffResult` from `diff`, and `diff`
imports `store` — so there is a transitive `views → store` path in the import graph even though
`layered.py` uses `DiffResult` only as a read-only value shape. The clean fix is to move the `DiffResult`
dataclass into `model` and leave `diff.py` as the git adapter. That touches `views/layered.py`.

**R-011 re-open check, 2026-08-26: condition NOT met, so it stays deferred a second batch.** R-011 re-opens
"at the start of any batch that does not touch `views/layered.py`". This batch touches `views/layered.py`
in **four** of its seven increments (§6: Inc-2, Inc-3, Inc-4, Inc-5) — it is the most contended file in the
tree after `app.py`. `ViewState` will carry `diff: DiffResult | None`, so `views/state.py` takes the same
`views → diff` import `layered.py:9` already has; **no new edge, and the transitive `views → diff → store`
path is neither widened nor closed.** Re-open at the first batch whose cut leaves `views/layered.py`
untouched.

---

## 4 · Interfaces — the contracts between modules

| Interface | Owner module | Consumers | Shape | Frozen? |
|---|---|---|---|---|
| `Graph` value object | `model` | `store`, `views`, `search`, `mermaid`, `github`, `app` | `nodes: dict[str, Node]`; `edges: list[Edge]`; `root_id: str`; `focus(node_id) -> Graph` | yes for MVP |
| `Canvas` drawing buffer | `canvas` | `views` | `put(x,y,ch,tone)`, `wire(x,y,mask,tone)`, `edge(...)`, `elbow_down(...)`, `text(...)`, `rows() -> list[Text]` — **plus the `dots` and `bgs` layers, declared in `__init__` and read by `rows()`** | **NO — Inc-1 owns it.** See R-016. *(The previous row also listed a `dline` method: executed, `grep -rn "dline" mapper/ tests/` returns nothing. It does not exist and has been removed from §2.)* |
| `MapStore` persistence | `store` | `app` | `load(map_id) -> Graph`, `save(map_id, graph)`, `create_seed`, `create_from_template`, `record_session`, `last_session` | yes — **and this batch must not add a partial-write method.** Corrected 2026-08-26 to the signatures on disk (`store.py:199`, `:217`); the previous row described a sidecar-passing API that never shipped. |
| `IRenderer.render` | `views` | `app` | **`render(self, graph: Graph, state: ViewState) -> Text`** — see the committed contract below | **NO — Inc-2 owns it, and Inc-2 alone.** Trigger A3, pre-authorised for `2026-08-26-ui-next-batch-02`. Supersedes R-010; recorded as R-012. |
| `ViewState` parameter object | `views` (`mapper/views/state.py`) | `app` | Frozen dataclass; every field defaulted; the *whole* parameter surface of every renderer | **NO — new, Inc-2 owns it.** Adding a defaulted field afterwards is **additive and not A3**; that is the entire point of choosing it. |
| `SearchIndex.query` + lens | `search` | `app` | `query(q) -> list[str]`; `parse_lens(q) -> LensQuery`; `lens_hits(graph, q) -> list[str]` | **NO — Inc-4 owns `query`, Inc-5 owns the lens.** The module has zero consumers today, so there is nothing to break; it is a resurrection, not a migration. R-014. |
| `MermaidImporter/Exporter` | `mermaid` | `app` | `parse(src) -> Graph`, `dump(graph) -> str` | yes for MVP |
| `GitHubConnector.fetch` | `github` | `app` | `fetch(repo_slug) -> Graph` | yes for MVP |
| `save_svg` / `save_png` | `export` | `app` | `save_svg(text, path)`, `save_png(text, path)` | yes for MVP |
| `DiffResult` value shape | `diff` | `views`, `app` | `added`, `removed`, `changed`, `removed_titles` | yes for this batch (see R-011) |
| `preview_csv` | `import_csv` | `app` | `preview_csv(path) -> Graph` | yes for this batch |
| Darkside tokens + renderables | `design` | `views`, `screens`, `widgets`, `app` | Colour tokens; builders returning `rich.Text` / `rich.Panel` | yes for this batch — four consumers, no lane owns it |
| `Ds*` interaction components | `widgets` | `screens`, `widgets` (inspector) | Nine `Static`-based components, three states each, changes emitted as `Message` | **yes for this batch** — shipped in batch 01, no story here touches them. |
| `KeyBar` / `HintLine` / `TabStrip` chrome | `widgets` | `screens`, `app` | `set_groups(...)`, `set_crumb(...)`, `HintLine.set_hint(...)` | **yes for this batch** — shipped in batch 01; re-frozen 2026-08-26. |
| `OutlineRail.show` | `widgets` | `app` | **`show(graph, cursor, folded: frozenset[str])`** — the rail *renders* fold, it no longer *owns* it; `OutlineRail.toggle` and `OutlineRail.collapsed` are removed | **NO — Inc-3 owns it.** This is the Q-2 answer; see R-013. |
| `KEYMAP` seat | `keymap` | `screens`, `widgets`, `app` | `KEYMAP: list[KeyBinding]`, `bindings_for(scope)`, `textual_bindings(...)`, `groups_for_keybar(...)`, `palette_items(q)`, `duplicate_chords()` | **NO — Inc-3, Inc-4 and Inc-5 each add chords, so no single lane owns it.** That is a departure from the batch-01 rule and it is a *known* collision: §6 records `mapper/keymap.py` as a three-way file collision resolved by serial ordering, not by ownership. `bindings_for(scope)` (`keymap.py:160`, executed) is what US-N16 derives its legend from — it must stay a pure read. |
| `open_external` | `osopen` | `app` **only** | `open_external(kind, target, *, workspace, launcher=None) -> str`; returns a status word | **yes for this batch** — shipped and security-reviewed in batch 01; not touched here. Re-frozen 2026-08-26. |

- **Changing one of these is trigger A3** — it fires ARQ, PDR *and* DDR, and it is never done inside a lane.
- A **frozen** interface is one the current batch committed to at PDR: no lane touches it; the work returns
to the trunk instead.
- An interface marked **"NO — Inc-N owns it"** is the inverse case: it is deliberately in motion this
batch, and exactly one increment may move it. A second lane editing it is the same collision as breaking
a freeze, just harder to see.

### 4a · The new committed `IRenderer.render` contract *(amended `2026-08-26-ui-next-batch-02`)*

**This section replaces the batch-01 freeze statement. R-010 predicted this re-opening and this is it.**

#### The measured surface the change has to cross

Executed 2026-08-26, not cited:

| Thing | Count | Probe |
|---|---|---|
| `def render` definitions in `views` | **6** in 4 files | `grep -rn "def render" mapper/views/` → `lane.py:108,171,311`, `layered.py:78`, `outline.py:17`, `radial.py:33` |
| production call sites | **3** | `grep -rn "\.render(" mapper/` → `app.py:711`, `:1301`, `:1671` |
| test files that drive a view renderer | **6** | `grep -rln "mapper.views" tests/` → `test_export`, `test_lane`, `test_layered`, `test_legacy_fixture`, `test_outline`, `test_radial` |
| …plus one that reaches a renderer through a screen | **1** | `tests/test_app.py:74` — `screen.renderer.render(g, selected_id="root", w=60, h=20)` |
| `IRenderer` as an actual Python type | **0** | `grep -rn "IRenderer" mapper/` → two prose mentions in comments (`views/layered.py:228`, `widgets/rail.py:6`) and **no class, no Protocol** |

The last row is the finding that shapes the decision. **The "frozen interface" has been enforced by a
markdown table and nothing else.** Six independent methods that happen to look alike is not an interface.

#### The two defects the current shape has already produced

Both executed, both are arguments *from evidence* rather than from taste:

1. **The call sites have already drifted.** `app.py:1301` passes `query=` **and** `diff=`;
   `app.py:1671` passes `query=` **only** — so an SVG exported while a diff is active silently loses the
   diff tinting. Nothing catches it, because the parameter list is positional-plus-kwargs with no shared
   declaration.
2. **`**kwargs` silently swallows.** `LayeredRenderer.render` (`layered.py:131-140` — *address
   corrected 2026-08-27; the row previously said `:78-87`, which no longer resolves. The claim
   itself re-executes TRUE*) declares
   `query`, `with_header`, `diff` by name; `outline.py:17` and `radial.py:33` and all three of
   `lane.py`'s renderers declare `**kwargs` and **drop `query` on the floor**. US-N07 requires a hit
   count and navigation **in every view**. That requirement is *unbuildable* while the swallow survives:
   the outline and radial views would report hits they do not paint.

#### The committed signature — verbatim

```python
# mapper/views/state.py  (new file; inside the existing `mapper/views/*.py` module glob)
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from rich.text import Text
from mapper.diff import DiffResult
from mapper.model import Graph


@dataclass(frozen=True, slots=True)
class ViewState:
    """Everything a renderer is allowed to know beyond the Graph itself.

    Frozen and fully defaulted: `app` builds a fresh one per repaint.  It is a
    message, not a store — no renderer and no widget may retain one.
    """
    # -- geometry ------------------------------------------------------
    w: int = 80
    h: int = 24
    pan_x: int = 0
    pan_y: int = 0
    # -- selection & focus ---------------------------------------------
    selected_id: str | None = None
    focus_owner: str = ""          # "" | "canvas" | "rail" | "inspector"  (closes B-05)
    # -- structure ------------------------------------------------------
    folded: frozenset[str] = frozenset()
    # -- matching (ids only — the renderer never evaluates a query) -----
    hits: frozenset[str] = frozenset()
    lens_matches: frozenset[str] | None = None     # None = no lens active
    # -- provenance & chrome --------------------------------------------
    diff: DiffResult | None = None
    # `with_header` was STRUCK by `PDR-2026-08-26-ui-next-batch-02#D2` (0 requirement
    # hits, 0 call sites).  The strike landed in `01-requirements.md` at pass 1 and is
    # landed HERE 2026-08-27, closing `P2-C4` / amendment `A-56`.  Do not reinstate it:
    # `LLR-N07.2.3`'s signature clause cannot catch a stray FIELD, only a parameter.


@runtime_checkable
class IRenderer(Protocol):
    def render(self, graph: Graph, state: ViewState) -> Text: ...
```

and every one of the six definitions becomes, verbatim:

```python
    def render(self, graph: Graph, state: ViewState) -> Text:
```

**`**kwargs` is abolished from all six.** A renderer that does not use a field ignores it by not reading
it — which is visible in the source — rather than by absorbing it into a dict, which is not.

#### Rules the shape carries

1. **`state` has no default.** Every call site declares its state. A default would reintroduce exactly the
   drift that produced defect (1) above, in a new costume.
2. **`graph` stays a separate positional argument.** The graph is the *subject*; `ViewState` is the *how*.
   Folding the graph into the state object would make every repaint copy a reference into a frozen
   dataclass for no gain and would blur what the renderer is rendering.
3. **Adding a field to `ViewState` later is additive, not A3** — provided it is defaulted and no existing
   field changes meaning. That is the whole reason this shape was chosen over additive kwargs: it makes
   the *next* capability cheap. Removing a field, or changing one's meaning, is still A3.
4. **The renderer receives ids, never predicates.** `hits` and `lens_matches` are `frozenset[str]`.
   See R-014 and the §3 note on the `views → search` edge that was deliberately not created.
5. **`focus_owner` is a string, not a widget.** `views` may not import Textual (§3); a plain string keeps
   the ban intact while giving the renderer the truth it needs to stop painting an ACCENT selection block
   in a region that does not have focus — carry **B-05**, closed as a field rather than as a mechanism.
6. **The whole migration is one increment (§6 Inc-2), and it is over the 4-source-file budget on purpose.**
   Six source files: `views/state.py`, `views/layered.py`, `views/lane.py`, `views/outline.py`,
   `views/radial.py`, `app.py`. Splitting it is the failure mode the batch's own R-1 risk exists to
   prevent; the budget breach is declared, not discovered.
7. **`views/state.py` must be its own file, not `views/__init__.py`.** `views/__init__.py` imports
   `layered`, and `layered` imports `ViewState` — putting the dataclass in `__init__` creates an import
   cycle. This is a mechanical constraint, not a style preference.

#### What survives from the batch-01 statement

**The rail is still built from `Graph`, not from a renderer.** `render` still returns `rich.Text` — a
picture. A collapsible outline tree with per-branch missing-field counts is a *structure*, and no
parameter object extracts structure back out of a `Text`. `ViewState` widens what goes **in**; it does not
change what comes **out**. `widgets` → `model` remains the edge that lets the rail compute its own tree.

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
| R-009 | **`screens` is split from `app` in the map, but `mapper/app.py` is NOT split — re-evaluated and again DEFERRED at `2026-08-26-ui-next-batch-02`.** | Extract `HomeScreen`, `MapScreen`, `RepoScreen`, `PlugRepoScreen`, `_ImportPreviewScreen` and the five modals out of the now-**2009**-line `app.py` into `mapper/screens/*.py` as an Inc-0. | **Re-open condition, restated: ≥3 increments touch `app.py` for genuinely unrelated reasons AND the batch has slack.** Evaluated 2026-08-26 — see the ruling block below the table. Limb 1 is now **permanently met**; limb 2 is the only thing still holding the decision, and the first batch that has slack must take it. |
| R-010 | **SUPERSEDED by R-012 on 2026-08-26**, exactly as this row predicted. `IRenderer.render` stayed frozen through `2026-08-25-ui-next-batch-01`; the rail computed its own tree from `Graph` and still does. | *(historical)* Extend `render` to return a structured tree so the rail could reuse `OutlineRenderer`. | Closed. The re-open it named — "batch 2 already has to reopen the renderer contract" — happened on schedule. The rejected alternative was **not** adopted: `render` still returns `Text`, and the rail still walks the `Graph` itself. Only the **input** side widened. |
| R-011 | **`DiffResult` stays in `diff`**, keeping the transitive `views → diff → store` import path, for one more batch. | Move the `DiffResult` dataclass to `model` and leave `diff.py` as the pure git adapter. | The fix is small and correct, but its file (`views/layered.py`) sits inside Inc-2's lane this batch, so taking it now widens a lane for an unrelated reason. Re-open at the start of any batch that does not touch `views/layered.py` — it should be a standalone two-file increment. **Re-checked 2026-08-26: not met** (four increments touch it); deferred a second batch. |
| R-012 | **`IRenderer.render` becomes `render(self, graph: Graph, state: ViewState) -> Text`**, with `ViewState` a frozen, fully-defaulted dataclass in `mapper/views/state.py`, and `IRenderer` promoted from prose to a real `typing.Protocol`. `**kwargs` is abolished from all six definitions. | **Additive keyword arguments** — `render(graph, selected_id, w, h, *, pan_x=0, pan_y=0, folded=frozenset(), hits=frozenset(), lens_matches=None, query="", diff=None, with_header=True)`. Rejected on measured evidence, not preference: the additive-kwarg shape is *the shape that is already broken here*. `app.py:1301` passes `query`+`diff` while `app.py:1671` passes `query` alone (executed), so an SVG exported during a diff silently drops the tinting — and `outline.py`/`radial.py`/`lane.py` absorb `query` into `**kwargs` and never paint it, which makes US-N07's "hit count in every view" unbuildable. Ten defaulted kwargs with no shared declaration would multiply both failures, and every future capability would be another A3-shaped argument about whether a new kwarg is a break. With a parameter object, **adding a defaulted field is additive and never A3** — that is the entire payoff, and it is why the larger one-time migration is worth it. | **Removing** a `ViewState` field, changing a field's meaning, or changing the **return** type away from `rich.Text`. Adding a defaulted field does **not** re-open this and does **not** fire A3. If `views` ever needs to hand structure back to a widget, that is a return-type change and returns to the trunk. |
| R-013 | **`MapScreen` owns fold state** as `folded: set[str]`; `OutlineRail` receives it via `show(graph, cursor, folded)` and **renders** it. `OutlineRail.collapsed` and `OutlineRail.toggle` are removed. `app` puts `frozenset(self.folded)` into `ViewState.folded`, so the rail and the canvas read one truth. **This is the Q-2 answer.** | **Leave `collapsed` inside `OutlineRail`** (`rail.py:35`, executed) and have `MapScreen.refresh_canvas` read it back with `query_one("#map-rail", OutlineRail).collapsed`. This *works* — a widget with `display = False` stays mounted and keeps its attributes — so the honest framing is that the alternative is functional, not broken. Rejected on **ownership lifetime**: `_apply_region_visibility` (`app.py:1172-1186`) auto-hides the rail whenever the canvas would fall below `MIN_CANVAS_WIDTH = 58`, and `action_toggle_rail` hides it on demand — so on an 80-column terminal US-N06's fold must work while the owning widget is not displayed at all. State whose consumers outlive its holder's visibility does not belong to the holder. Also rejected: a **third** owner inside `ViewState` — that object is frozen and rebuilt per repaint; it is a message, not a store. | If the rail becomes the only surface that folds — i.e. the canvas stops honouring fold — the state could move back down into the widget. Also re-open if fold must **persist** across sessions, which makes `store` the owner and is a different decision entirely. |
| R-014 | **`search` is the single owner of "what matches"**, for free-text hits *and* for the new `key:value` lens. Renderers receive `frozenset[str]` id sets in `ViewState` and **never evaluate a query**. The inline predicate at `views/layered.py:144-149` is deleted. | **(a) Leave matching in the renderer** — rejected: it is the live defect. Two definitions of "hit" ship today (`layered.py:144-149` matches title + notes + field values; `model.py:169-184` also matches node id, `ficha.meta` and attachment captions/paths), so a count taken from one and a highlight taken from the other disagree *on screen* — precisely what US-N07 exists to prevent. **(b) Delete `search` and put the lens in `model`** — tempting, because `search.py` is **dead code as found** (zero consumers in `mapper/` or `tests/`, executed) and `Graph.search_hits` already lives in `model`. Rejected because a query *language* (parse → evaluate → saved lenses) has a different change rate from the domain value objects, and because deleting a module now means an A1 module-creation trigger to recreate it later; filling an existing module is additive and reversible. **(c) Pass a `LensQuery` or a predicate into the renderer** — rejected: it creates a `views → search` edge for no benefit, where a `frozenset[str]` creates none. | If the lens stops being a pure function over `Graph` + schema — e.g. it needs an index built at save time — the parser stays in `search` but the index moves to `store`, and `search` gains a `store` dependency it does not have today. |
| R-015 | **Coverage roots are declared in §2b** (`mapper/**`, `tests/**`, `prototypes/**`) so validator **V8** can run, while the per-file `paths` column in §2 stays per-file and remains the real oracle. | **Reasoned non-adoption** — record that V8 cannot check this map and leave the `[!]` notice standing forever. Rejected for two reasons. First, executed against the rule's source (`devflow-validate.py:244-261`), **V8 computes orphans only and performs no double-claim check**, so §2's objection — that a coarse glob makes double-claiming vacuous — is aimed at a check V8 does not run, and satisfying V8 costs the per-file discipline nothing. Second, a permanent notice trains the reader to skip the line, which is how a real V8 finding gets missed later. | If V8 ever gains a claim-resolution rule reading the same tokens, the roots block must be re-examined: at that point a coarse `mapper/**` really would swallow the subpackages, and the roots would need a form V8's regex does not see. |
| R-016 | **`Canvas` is un-frozen for this batch** (Inc-1): `dots` and `bgs` become declared attributes in `Canvas.__init__` and `rows()` reads them. | Leave `RadialRenderer` monkey-patching `cv.dots = {}` / `cv.bgs = {}` onto the instance (`radial.py:47-48`, executed) and paint braille some other way. Rejected: executed, `Canvas.__init__` declares neither attribute and `rows()` (`canvas.py:67-82`) reads only `self.cells` and `self.bits`, so every braille glyph and every pill background written by `radial.py:121` and `:135` is **discarded silently** — a 6-node graph at 80×24 renders **0** glyphs in `U+2800–U+28FF`. The map declared `Canvas` frozen ("yes for MVP"), so honouring the layers is formally a **second A3 that the brief did not name**; recording it as a widening freeze move is the honest disposition. It is additive — nothing that works today stops working — but it changes `rows()` output bytes, which `export.save_svg` consumes: trigger **B4**, already fired. | Nothing plausible inside this batch. After Inc-1 the layers are part of the contract and `Canvas` re-freezes. |

---

### R-009 ruling for `2026-08-26-ui-next-batch-02` — **NO, do not extract**

*(Required by the batch brief. The condition is evaluated against the §6 cut, not against intuition.)*

| Limb | Verdict | Evidence |
|---|---|---|
| ≥3 increments touch `app.py` | **MET, 7 of 7** | Every increment in the §6 cut lists `mapper/app.py`. |
| …for **genuinely unrelated** reasons | **MET** | Four demonstrably disjoint regions of one file: Inc-1 edits a CSS string (`app.py:1890`); Inc-2 migrates three renderer call sites (`:711`, `:1301`, `:1671`); Inc-6 edits `HomeScreen.on_mount` (`:439`); Inc-7 edits three `push_screen(HelpScreen())` lines sitting in **three different screen classes** (`:743` `_ImportPreviewScreen`, `:794` `PlugRepoScreen`, `:1059` `RepoScreen`). |
| the batch has **slack** | **NOT MET** | The batch already carries a pre-authorised A3 across 6 source files that may not be split; a **second** freeze move on `Canvas` the brief did not anticipate; five stories plus tokens; and a shipped total-functionality-loss defect (S-7). |

**Ruling: NO.** Cost, stated rather than hand-waved: `app.py` lines **338-1831 = 1494 lines** relocate
(`HomeScreen` at `:338` through the last line before `MapperApp` at `:1832`) into ≥5 new files, plus the
`screens/factory.py:343` back-edge (carry B-02), plus **8 test files** that import `mapper.app`
(`test_app`, `test_attachments`, `test_inspector`, `test_keymap`, `test_key_dispatch`, `test_palette`,
`test_rail`, `test_worklist_safety` — executed). It lands as an Inc-0 gate before any story can start,
with no user-visible outcome and no acceptance test of its own.

**The decisive argument is sequencing, not size.** The extraction moves every `.render(` call site, and
the batch's largest declared risk (`PLAN.md` §8 R-1, "the A3 migration half-lands") is controlled by a
reverse census of exactly those call sites. Taking that census against a file that has just changed
identity — where every line number in this document and in `PLAN.md` §6 is stale — converts a countable
check into a judgement call, at the one moment the batch can least afford it.

**Carried forward, and it should be scheduled.** Limb 1 is now met permanently and by a wide margin. The
extraction belongs as **batch 3's Inc-0**, budgeted as a no-outcome increment with its own gate, and it
should be entered on `.dev-flow/BACKLOG.md` at this batch's close. Deferring it a third time *without*
scheduling it is how R-009 becomes a decision nobody ever makes.

---

## 6 · Parallelisation worksheet *(filled per batch, at ARQ)*

Two increments are parallelisable when **`modules(A) ∩ modules(B) = { }`**, **or** when they touch the
same domain on **different layers** (UI/UX vs functional) *and* the interface between them is frozen and
neither lane touches it.

### Current batch — `2026-08-26-ui-next-batch-02` (variant B «atlas» + round-10, five stories + tokens + one folded-in defect)

*(The `2026-08-25-ui-next-batch-01` worksheet is superseded and removed. Its headline finding — 0 of 15
pairs, all colliding on `mapper/app.py` — is re-derived below rather than inherited, per trigger A4.)*

**Nothing about the verdict is assumed from last batch.** `mapper/app.py` has grown from 1709 to **2009**
lines (`wc -l`, executed), and the batch's own intake hoped that US-N13 «sala» would be the one disjoint
lane (`01-requirements.md` §2.6 S-3: *"Its module set is `{app, design, store?}` … It is the one story
that could run as a parallel lane — decided at ARQ"*). **That hope is measured false below**, and the
reason is one line of evidence: `HomeScreen` is declared at `mapper/app.py:338`. Sala cannot be disjoint
from anything while the home screen lives inside the file every other increment edits.

#### The proposed cut

Budget: **≤4 SOURCE files per increment**, tests uncapped. One increment breaches it, declared.

| Lane | Story | Modules | Layer | SOURCE files it owns | n |
|---|---|---|---|---|---|
| **Inc-1** | S-6 tokens + S-7 layout defect + `Canvas` layers (HLR-canvas part 1) | `design`, `canvas`, `app` | functional + UI/UX | `mapper/darkside.py`, `mapper/canvas.py`, `mapper/app.py` | 3 |
| **Inc-2** | **the A3 migration** — `ViewState` + `IRenderer` Protocol + all six `render` defs + all three call sites | `views`, `app` | functional | `mapper/views/state.py` *(new)*, `mapper/views/layered.py`, `mapper/views/lane.py`, `mapper/views/outline.py`, `mapper/views/radial.py`, `mapper/app.py` | **6 — declared over budget** |
| **Inc-3** | US-N06 escala — pan, fold, declared overflow; braille edges on the map canvas | `app`, `widgets`, `views`, `keymap` | UI/UX | `mapper/app.py`, `mapper/widgets/rail.py`, `mapper/views/layered.py`, `mapper/keymap.py` | 4 |
| **Inc-4** | US-N07 búsqueda — hit count, `n`/`N` navigation, distinct empty state, WARN pills | `search`, `app`, `views`, `keymap` | functional + UI/UX | `mapper/search.py`, `mapper/app.py`, `mapper/views/layered.py`, `mapper/keymap.py` | 4 |
| **Inc-5** | US-N14 lente — `key:value` parser, figure-ground, `⇥` walk, saved lenses, declared counts | `search`, `app`, `views`, `keymap` | functional + UI/UX | `mapper/search.py`, `mapper/app.py`, `mapper/views/layered.py`, `mapper/keymap.py` | 4 |
| **Inc-6** | US-N13 sala — thumbnail, coverage microbar, due badge, `⇄` marker, welcome seat | `app`, `design`, `store` | UI/UX | `mapper/app.py`, `mapper/darkside.py`, `mapper/store.py` | 3 |
| **Inc-7** | US-N16 leyenda — per-view legend, `?` scope routing on **every** screen, `??` reserved | `screens`, `app`, `design` | UI/UX | `mapper/screens/help.py`, `mapper/app.py`, `mapper/darkside.py` | 3 |

**Inc-2's budget breach is a decision, not an overrun.** Six is the floor, not a convenience: the four
view files each hold a `def render`, `app.py` holds all three call sites, and `views/state.py` cannot be
folded into `views/__init__.py` because `__init__` imports `layered` and `layered` imports `ViewState` —
an import cycle. Splitting the migration across two increments is precisely the failure `PLAN.md` §8 R-1
exists to prevent: between the halves, the old signature and the new one would both be live and the suite
would be green on a contract nobody holds. **V9 requires the count to be declared in the packet; it is
declared here in advance so no reviewer meets it as a surprise.**

**`◍` (repo provenance) is NOT in Inc-6.** It is `REFINE` pending Q-5 (`01-requirements.md` §2.6 S-3b) and
needs new persisted state with a migration answer. If PDR admits it, it is a **separate** increment
touching `mapper/store.py` + `mapper/app.py`, not a widening of Inc-6.

#### The intersection arithmetic — all 21 pairs

`C(7,2) = 21`. Two increments are parallelisable when `modules(A) ∩ modules(B) = { }`.

| Pair | `modules(A) ∩ modules(B)` | Parallel? | File collisions beyond `app.py` |
|---|---|---|---|
| 1–2 | `{app}` | no | — |
| 1–3 | `{app}` | no | — |
| 1–4 | `{app}` | no | — |
| 1–5 | `{app}` | no | — |
| 1–6 | `{app, design}` | no | `darkside.py` |
| 1–7 | `{app, design}` | no | `darkside.py` |
| 2–3 | `{app, views}` | no | `views/layered.py` — **plus an ordering dependency**: Inc-3 cannot compile before `ViewState` exists |
| 2–4 | `{app, views}` | no | `views/layered.py` — same ordering dependency |
| 2–5 | `{app, views}` | no | `views/layered.py` — same ordering dependency |
| 2–6 | `{app}` | no | — |
| 2–7 | `{app}` | no | — |
| 3–4 | `{app, views, keymap}` | no | `views/layered.py`, `keymap.py` |
| 3–5 | `{app, views, keymap}` | no | `views/layered.py`, `keymap.py` |
| 3–6 | `{app}` | no | — |
| 3–7 | `{app}` | no | — |
| 4–5 | `{app, search, views, keymap}` | no | `search.py`, `views/layered.py`, `keymap.py` — **the worst pair in the batch** |
| 4–6 | `{app}` | no | — |
| 4–7 | `{app}` | no | — |
| 5–6 | `{app}` | no | — |
| 5–7 | `{app}` | no | — |
| 6–7 | `{app, design}` | no | `darkside.py` |

**Verdict: 0 of 21 pairs are parallelisable. `modules(A) ∩ modules(B) ⊇ {app}` for every pair, without
exception — the same result batch 1 measured over 15 pairs, on a file that has since grown by 300 lines.**
No lane exists and the worksheet does not manufacture one.

**On the sala hypothesis specifically.** Inc-6's module set is `{app, design, store}`. It is the *only*
increment touching `store`, and it touches no renderer — both true, and both were the reason to hope. But
it intersects Inc-1 and Inc-7 on `{app, design}` and everything else on `{app}`. The story is
**resequenceable**, which is genuinely useful, but it is not **parallel**. Recording the difference
matters: resequenceable buys schedule freedom when a gate stalls; parallel would have bought wall-clock
time, and this batch has none to buy.

#### File-level contention census (derived from the cut, not by eye)

| File | Increments that own it | Note |
|---|---|---|
| `mapper/app.py` | 1, 2, 3, 4, 5, 6, 7 — **all seven** | The binding constraint. R-009's limb 1. |
| `mapper/views/layered.py` | 2, 3, 4, 5 | Most contended file after `app.py`; this is why R-011 stays deferred. |
| `mapper/darkside.py` | 1, 6, 7 | Inc-1 defines the tokens; Inc-6 and Inc-7 only consume + add builders. |
| `mapper/keymap.py` | 3, 4, 5 | **No single increment owns the seat this batch** (§4). Three lanes add chords; serial ordering is the only control, and Q-3's `n` collision is settled at PDR *before* Inc-4. |
| `mapper/search.py` | 4, 5 | Inc-4 makes it live; Inc-5 adds the lens on top. |
| `mapper/canvas.py` | 1 | Sole owner. |
| `mapper/widgets/rail.py` | 3 | Sole owner (R-013's `show(graph, cursor, folded)`). |
| `mapper/store.py` | 6 | Sole owner. |
| `mapper/screens/help.py` | 7 | Sole owner. |
| `mapper/views/{state,lane,outline,radial}.py` | 2 | Sole owner. |

#### Recommended execution — one serial chain

**`Inc-1 → Inc-2 → Inc-3 → Inc-4 → Inc-5 → Inc-6 → Inc-7`**

The ordering is forced, edge by edge:

- **Inc-1 first** — S-6 tokens are a stated dependency of S-3 and S-4; S-7's missing `#map-rail { width: 24 }`
  is a precondition of every canvas story (pan, fold and an overflow indicator on an off-screen canvas are
  not a deliverable); and `Canvas`'s `dots`/`bgs` layers must be honoured before any braille edge can be
  asserted to reach the screen.
- **Inc-2 second** — nothing that touches a renderer can start before the contract moves. **This increment
  owns the A3 migration in full and alone.**
- **Inc-3, then Inc-4, then Inc-5** — Inc-4's hit count must be computed over folded branches, so it
  consumes Inc-3's fold state; Inc-5's figure-ground rides the same `ViewState` fields and the same
  `views/layered.py` region as Inc-4, and both add chords to `keymap.py`.
- **Inc-6** is the **resequenceable** one: its only upstream is Inc-1's tokens. If any gate from Inc-2
  onward stalls, Inc-6 is the increment to pull forward.
- **Inc-7 last, and it must be last** — its bindings half is derivable from `keymap.bindings_for(scope)`
  (`keymap.py:160`, executed) and could run early, but its **glyph-vocabulary half must render the real
  style of glyphs Inc-3 and Inc-5 paint**. A legend written before the vocabulary exists is a legend that
  documents an intention.

**What would change the verdict — and what would not.** Nothing in this cut. Re-cutting cannot dissolve
`{app}`, because the intersection is a single 2009-line **file**, not a module label: `mapper/app.py`
holds `MapperApp` and eleven screen classes, and every story in the batch reaches into one of them. The
boundary move that would change it is R-009, ruled **NO** for this batch with its cost stated in §5.
Extracting the screens would trade `{app}` for `{screens}` — it buys conflict-freedom, not concurrency,
and this worksheet has said so twice now.

If the intersection is **not** empty there are exactly two exits, and both are explicit decisions:

1. **re-cut the increments**, or
2. **move the module boundary — here, in this document**.

The second is the one that actually prevents spaghetti; the first only routes around it for one batch.

- ⚠ Same-domain lanes with an interface that is **not** frozen: that is not parallelism, it is a collision
  with a delay — both lanes advance and meet the conflict at integration, the most expensive moment.
- **This orders the CODE.** The order of *merit* — what goes first — still comes from the intake risk estimate.

### Architectural risks this cut hands to the requirements phase

*(Recorded here because each one is a boundary question that a story can violate by accident. A-1 and A-2
would force a frozen-interface change if a story is written carelessly; A-3 and A-4 are the ones a story
can satisfy at one file's boundary while the identical defect ships in that file's siblings.)*

| # | Risk | Where it bites | What requirements must settle |
|---|---|---|---|
| A-1 | **The A3 migration half-lands.** Six `def render`, three call sites, seven test files. The old signature surviving *anywhere* means two contracts are live and the suite is green on neither. | Inc-2 | **The reverse census is derived from the code, never taken by eye** (`grep -rn "def render" mapper/views/`, `grep -rn "\.render(" mapper/ tests/`). A test must assert that **no** `render` accepts `**kwargs` and that `IRenderer` is satisfied by all six classes — `@runtime_checkable` makes that a one-line assertion per renderer. Absence of the old shape must be **asserted**, not assumed. |
| A-2 | **A story asks the renderer to return structure.** Fold pills, an overflow count and a lens count are all things `app` wants to *know*, and the tempting shortcut is to have `render` hand back a tuple or a dict. | Inc-3, Inc-4, Inc-5 | `render` returns `rich.Text` and **only** `rich.Text` (R-012). Counts are computed by `app`/`search` **before** the call and travel *in* via `ViewState`, or they are painted by the renderer and never read back. A story phrased "the renderer reports how many nodes are off-screen" is a **return-type change, therefore A3, therefore out of scope** and returns to the trunk. |
| A-3 | **Two definitions of "hit" ship today** and the batch adds a third surface that needs one. `views/layered.py:144-149` matches title + notes + field values; `Graph.search_hits` (`model.py:169-184`) also matches node id, `ficha.meta` and attachment captions/paths. A count from one and a highlight from the other disagree **on screen**. | Inc-4, Inc-5 | R-014 names `search` the owner. Requirements must state the **behaviour change this causes**: highlighting will begin matching node ids, `meta` and attachment text, which it does not today. That is a user-visible widening and needs an AT, not a silent side effect. **The inline predicate must be deleted, and its deletion asserted** — leaving it dead-but-present is how the second definition comes back. |
| A-4 | **`?` scope routing is broken in three screens, not one** (P-13, executed: `app.py:743`, `:794`, `:1059` all call `push_screen(HelpScreen())` with no scope; only `MapScreen:1828` delegates to the scope-aware `MapperApp.action_help:1987`). A requirement scoped to a *file* gets satisfied at that file's boundary while the identical defect ships in its siblings — batch 1's §2.1b lesson. | Inc-7 | The requirement is quantified **over the screen set**, not over the three known offenders: *every* screen that routes `?` routes it with its own `KEY_SCOPE`. The AT enumerates screens **derived** from the source (e.g. every `Screen` subclass declaring `KEY_SCOPE`), never a hand-list. |
| A-5 | **Three increments add chords to `keymap.py` and no single increment owns the seat** — a departure from batch 1's one-owner rule, recorded in §4. Q-3 is live: `n` is already `next_gap` in map scope and `N` is bound in no scope (P-11, executed), and `duplicate_chords()` + `test_no_duplicate_chord_inside_one_scope` will reject a second map-scope `n`. | Inc-3, Inc-4, Inc-5 | **Q-3 is settled at PDR before Inc-4 starts**, not by the implementer. Whatever is chosen, the whole-seat conformance spec `{(scope,key): (action,label,glyph,priority,group)}` is updated in the **same** increment that adds the chord (carry P-06: three partial pins each passed review-breaking mutations). Inc-7's legend derives from `bindings_for(scope)`, so a seat that is wrong makes the legend wrong too — silently. |
| A-6 | **Fold state has one owner and three readers.** R-013 puts it on `MapScreen`; the rail renders it, the canvas renders it, and US-N07's hit count must be computed **including folded branches**. The classic defect is a count taken over `visible_rows()`. | Inc-3, Inc-4 | State plainly that hit and lens counts are computed over the **whole graph**, never over what is painted. An AT must fold a branch containing a known match and assert the count is unchanged — that is the assertion that distinguishes this story from the defect it exists to close. |
| A-7 | **New file-derived text reaches four new rendered surfaces**: map titles into home thumbnails (Inc-6), ficha field values into lens results (Inc-5), glyph vocabulary and binding labels into the legend (Inc-7), and fold-pill branch names into the canvas (Inc-3). `darkside.plain()` exists as the coercion (`darkside.py:276`) and carry **B-03** records ~20 legacy `rich.markup.escape` sites in `app.py` that emit **visible backslashes** in a `Text` path. | Inc-3, Inc-5, Inc-6, Inc-7 | Requirements are scoped to the **sink class**, not to a file — every new text sink coerces through `darkside.plain()`, with hostile-input ATs (markup, control bytes, `U+202E`). `security-reviewer` is a live lens. Do **not** opportunistically fix B-03's twenty legacy sites inside a story increment; that is a scope-add needing its own decision. |
| A-8 | **`Canvas` is the batch's second, unnamed A3** (R-016). The brief pre-authorised `IRenderer.render`; it did not mention `Canvas`, which §4 declared frozen. Honouring `dots`/`bgs` changes `rows()` output bytes, and `export.save_svg` consumes them (trigger B4). | Inc-1 | **PDR must approve the `Canvas` freeze move explicitly**, alongside the renderer one. The AT is not "braille appears" but a count: a rendered graph must yield **> 0** glyphs in `U+2800–U+28FF` where it yields exactly 0 on `master`. Export output changes too — say whether that is asserted or merely permitted. |
| A-9 | **S-7's regression test is blind at the sizes the suite uses.** `_apply_region_visibility` (`app.py:1172-1186`) hides the rail below ~118 columns, so 245 green tests exercise only the widths at which the bug is absent (C-55 limb 2). | Inc-1 | The AT **drives a wide Pilot size** (≥120 columns) and asserts post-layout `widget.region`, not merely that a widget exists. It owes an escaped-bug counterfactual: **RED against `master` before the fix**. A test that passes on `master` is not a regression test for this defect. |
| A-10 | **`mapper/search.py` is dead code being resurrected** — zero consumers in `mapper/` or `tests/` (executed). A module with no callers has no tests, so nothing currently constrains its behaviour, and "it already existed" is not evidence that it works. | Inc-4 | Treat `search` as **new code with a legacy filename**. It gets its own Layer-0 test file with no event loop and no filesystem. Q-6 (a lens term naming an undefined schema field) is answered **there**, as a declared outcome — "no matches" and "your query was meaningless" must not paint the same, and that distinction is testable at layer 0 before any UI exists. |
