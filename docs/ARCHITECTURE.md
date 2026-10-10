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
| Last amended by | `2026-10-09-modular-batch` (ARQ) |
| Date | `2026-10-09` |

> **Amendment `2026-10-08-data-safety-batch` (ARQ, US-001 ← B-36, model C "draft + explicit save").**
> **No module boundary moves and no dependency edge is added** (§3 is unchanged). What moves is one
> **interface** (trigger A3): the inspector stops posting `FichaInspector.FieldCommitted` and instead
> holds a per-node draft that `MapScreen` reads and persists on `ctrl+s` or on the `save` answer of a
> new `save · discard · stay` modal. Every row below that describes that surface is written as a
> **commitment** (*planned, Inc-N*), not in the present tense, because none of it exists on disk at
> this amendment. §6 carries this batch's worksheet; the `2026-08-25-ui-next-batch-01` worksheet it
> replaces is superseded and lives in git history.

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
>
> **Amendment `2026-10-09-modular-batch` (ARQ — proposal `.dev-flow/2026-10-09-modular-batch/spike/arq-proposal-kimi-k3.md`,
> corrected by the orchestrator's MRO spike `evidence/arq-mro-spike.transcript`).** R-009's re-open condition
> ("≥3 increments touching `app.py` for unrelated reasons") is met, so this amendment maps the split of
> `mapper/app.py`: §2's `screens` row names its top-level files literally and a new **`map screen`** module
> row owns `mapper/screens/map/*.py`; §3 gains the `screens/map`, `screens/common` + `screens/prompt` and
> `osopen` dependency rules; §4 gains the MapScreen freeze (F1–F5) with the Textual 8.2.8 spike rules;
> §6 carries this batch's worksheet. **Everything this amendment adds is a TARGET, not a fact:** none of the
> named files exists on disk until the batch's increments move the code (Inc-0, Spine A A1–A3 + A5a, B0,
> A5b, A6–A7, A4, Spine B
> B1–B11, B12 — see §6), so rows describing the moved code are written as commitments, and B-02 closes at
> increment A2, not before.

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
| `canvas` | `mapper/canvas.py` | Cell buffer, box-drawing wire merging, braille free-angle edges, pill backgrounds. | `Canvas(w, h, tones=(), fallback="")` with `put`, `wire`, `edge`, `elbow_down`, `text`, `rows`. *(Corrected `2026-08-27-repair-batch-02`: the previous row also listed `dline`. Executed — `hasattr(Canvas, "dline")` is `False` and `grep -rn "dline" mapper/` returns nothing. It does not exist. Corrected again `2026-08-26-ui-next-batch-02` Inc-1: the signature gained the two tone-policy parameters, and this row is the SECOND place the constructor is described — see §4. `tests/test_repair_map_truth.py` pins this row as prose and imports nothing, so it cannot observe `Canvas.__init__` and did not notice; carried as `B-44` to pin it against `inspect.signature` instead.)* | Layout algorithms; diagram semantics. |
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
| `widgets` | `mapper/widgets/*.py`, `mapper/motion.py` | Textual widgets built on `design`: chrome (`TabStrip`, `KeyBar`, `HintLine`, `GroupBox`), the nine `Ds*` interaction components, the editable ficha inspector, the outline rail, and shared motion helpers. | `TabStrip`, `KeyBar`, `HintLine`, `GroupBox`, `Ds*` components, `FichaInspector`, `OutlineRail`; state changes leave as Textual `Message`s. *(Planned, `2026-10-08-data-safety-batch` Inc-1: `FichaInspector` also holds the **per-node draft** of unsaved ficha edits and exposes it read-only — see §4. That is the one sanctioned exception to "changes leave as messages": the screen PULLS the draft at the moment it saves, because only the save's result may clear it.)* | **Persistence and orchestration.** A widget never imports `store`, `views`, `screens`, `app` or `osopen`; it never saves a ficha and never launches an OS handler. It emits a message and `app` decides. **Holding a draft is not persisting one:** the inspector never writes it, never snapshots it for undo, never decides when an exit must ask about it, and never puts it on disk on its own (ruling R1). |
| `screens` | `mapper/screens/__init__.py`, `mapper/screens/palette.py`, `mapper/screens/help.py`, `mapper/screens/coverage.py`, `mapper/screens/editor.py`, `mapper/screens/factory.py`, `mapper/screens/settings.py`, `mapper/screens/draft_guard.py`, `mapper/screens/common.py`, `mapper/screens/prompt.py` | Full-screen and modal Textual screens that compose widgets into a task. *(The fnmatch rule in the notes below applies in reverse here: a `mapper/screens/*.py` glob would also match the `screens/map/` package, double-claiming it — so the top-level files are named literally, and only `map/` keeps a glob.)* **`palette.py`** owns `CommandPalette`; **`help.py`** owns `HelpScreen`; **`coverage.py`** owns `CoverageScreen`; **`editor.py`** owns `EditorScreen`; **`factory.py`** owns `FactoryScreen`; **`settings.py`** owns `SettingsScreen`; **`draft_guard.py`** owns `DraftGuardScreen`. *(`common.py` owns the shared screen helpers — `screen_bindings`, `keybar_groups`, `map_hint`, `home_hint`, the refusal/toast helpers, the hint-string constants, and `MapHintLine` *(ARCH-8: it moves at A1 into `common.py` — a shared hint widget, not part of the map hints concern, so it does not wait for B1; §6)*; `prompt.py` owns the four literal modals `_PromptScreen`, `_ConfirmScreen`, `_TemplateScreen`, `_FichaScreen`; `construct.py` owns `ConstructScreen`; `home.py` owns `HomeScreen`; `repo.py` owns `RepoScreen`; `plug_repo.py` owns `PlugRepoScreen`; `import_preview.py` owns `_ImportPreviewScreen`. All seven are commitments — until Spine A moves them they still live in `mapper/app.py`; see the `app` row and §6.)* **TARGET of `2026-10-09-modular-batch` (files not yet on disk; each joins this row's paths with the increment that creates it):** mapper/screens/common.py, mapper/screens/prompt.py, mapper/screens/construct.py, mapper/screens/home.py, mapper/screens/repo.py, mapper/screens/plug_repo.py, mapper/screens/import_preview.py | `CommandPalette`, `HelpScreen`, `CoverageScreen`, `EditorScreen`, `FactoryScreen`, `SettingsScreen`, `DraftGuardScreen`; *(target: `HomeScreen`, `RepoScreen`, `PlugRepoScreen`, `ConstructScreen`, `_ImportPreviewScreen`, the four prompt modals, and the `common.py` helpers incl. `MapHintLine`)*. | The `App` object and its lifecycle; domain logic; persistence internals; **any `MapScreen` concern** — those belong to `map screen` below. **`screens` must not import `app`** — see the recorded violation in §3. |
| `app` | `mapper/app.py` | The `App` object and all cross-module orchestration and persistence calls. **TARGET of `2026-10-09-modular-batch`:** after its increments land, `app.py` holds only `MapperApp`, `main`, the `CSS` block, and re-exports of every moved name (so `from mapper.app import X` keeps working). The F4 patch surface does NOT live here: each of the seven module-global test-patched names (`save_svg`, `pan_extent`, `LayeredRenderer`, `preview_csv`, `refusal_sentence`, `SearchIndex`, `MAX_RENDER_NODES`) stays bound in, and read from, the module that owns its reader, and `GitHubConnector.fetch` — the eighth — is a class-attribute patch that survives re-export (§4), so `app` keeps no patch back-edge. Until then the top-level screens still live here: `HomeScreen`, `MapScreen`, `RepoScreen`, `PlugRepoScreen`, `_ImportPreviewScreen` and their modals. | `MapperApp`, `HomeScreen`, `MapScreen`, `RepoScreen`; wires every module together. | Domain logic, persistence internals, drawing. **After the batch:** any `Screen` subclass other than `MapperApp` and any MapScreen concern method — those have homes in `screens` / `map screen` above. |

**Target rows of `2026-10-09-modular-batch`** — not part of the table above, because `tests/test_repair_map_truth.py` requires every path the table declares to exist on disk. Each row (or path) moves into the table in the increment that creates its first file.

| Module | Target paths (not yet on disk) | What it will encapsulate | What it will EXPOSE | What will NOT belong to it |
|---|---|---|---|---|
| `map screen` | `mapper/screens/map/*.py` | **TARGET of `2026-10-09-modular-batch`:** the `MapScreen` home — one package, one concern per module, composed by mechanism A (plain mixins on the core class). **`__init__.py`** — re-export of `MapScreen` only; no logic (same rule as the root `package` row). **`screen.py`** — the core class: the lifecycle concern (`__init__` with all 30 attribute slots, `compose`, `on_mount`, region visibility, focus parking, resize/focus/resume handlers) and **every class constant plus `BINDINGS`** (spike rule: bindings live only here — §3/§4). **`painting.py`** — views concern: `refresh_canvas`, view state, header/canvas sizing, minimap, legend docking, fold/render-mode/diff toggles. **`searching.py`** — search concern: search order/hits, count, pagination, echo, hit & gap walking. **`panning.py`** — pan concern: clamp/consume/reclamp, `_pan`, pan-revealing selection, step actions. **`hints.py`** — hints concern: the `_seat_*`/`_hint_*`/`_toast` helpers *(ARCH-8: `MapHintLine` is NOT here — it moves at A1 into `screens/common.py`; §6)*. **`navigation.py`** — `NavigationModel` **plus** the nav concern: cursor actions, `_repoint`, crumb, open-ficha/home/back. **`drafts.py`** — draft concern: `_guard_draft` (the funnel), `guard_open`, `has_pending_draft`, `_save_draft`, field focus. **`editing.py`** — edits concern: attachments, add-child, archive, subtree removal. **`undo.py`** — undo concern: the snapshot stack and `action_undo`. **`focus_mode.py`** — focus concern: `action_toggle_focus`. **`opening.py`** — open concern: the attachment-activated handler and `action_open_documents` (the one sanctioned `open_external` call site — §3). **`exporting.py`** — export concern: `action_export_svg` and the export-budget helpers. Until B0/B1–B11 land, all of this is still `MapScreen` inside `mapper/app.py`. | `MapScreen` (via the package re-export only), `NavigationModel`. | Anything outside `MapScreen`: no other screen class, no widget, no persistence logic. Method names — `on_*` handlers above all — must be pairwise-disjoint across the 12 modules (spike rule, §3/§4; guarded by a test). |

**Staleness rule — the map checks itself.** A touched file that falls under **no** declared module means
this map is out of date: **ARQ fires on its own** and the map is amended before requirements are derived.
Silence is not an option here, because a stale map makes every A-family verdict meaningless.

- **Every path in the tree is claimed by exactly one module.** Overlapping prefixes are a defect of this
document, not an ambiguity to be resolved case by case.
- **No `mapper/*.py` wildcard is declared, deliberately.** Under `fnmatch` semantics `*` also matches `/`,
  so a single `mapper/*.py` glob would silently swallow `views/`, `screens/` and `widgets/` and every
  double-claim check would pass vacuously. Top-level files are therefore each named literally, and only
  the three package directories use a glob. Changing this is how the check stops working.
- **`mapper/app.py` is 5255 lines and holds ten `*Screen` classes; `MapScreen` alone spans 3454 of them** *(re-executed at P0 of `2026-10-09-modular-batch` (`d8cf942`): `wc -l mapper/app.py` → 5255; `class MapScreen` at line 1536 through line 4989 → 3454 lines. The previous figure, 4957 lines, was measured `2026-10-08` and had gone stale)*. That is recorded here as a fact, not
  as an aspiration: it is the single reason most batches have no parallel product lanes (§6), and the
  boundary move that fixes it is `2026-10-09-modular-batch` itself (§6) — the re-open condition of R-009
  is now met.
- **Paths outside `mapper/` are not modules and are classified by FILE, not by prefix.** `tests/`,
  `docs/`, `.dev-flow/`, `fixtures/` and `prototypes/` carry no module row on purpose: they own no
  runtime boundary, so the staleness rule above does not fire on them. The parallelisation rule (§6)
  still applies to them at file granularity — two lanes editing the same test file collide exactly as
  two lanes editing the same source file do.

---

## 3 · Dependency — who may reach whom

| Module | Depends on | Forbidden direction | Why the ban exists |
|---|---|---|---|
| `app` | `model`, `store`, `views`, `search`, `export`, `mermaid`, `import_csv`, `github`, `diff`, `keymap`, `design`, `widgets`, `screens`, `screens/map` *(amended `2026-10-09-modular-batch`: `app` additionally depends on `screens/map` — the `MapScreen` re-export)*, `osopen` | `model` → `app`; **no module may import `screens/map` except `mapper.app` and the sibling screen modules `screens/home.py`, `screens/import_preview.py` and `screens/repo.py`, which MAY import `MapScreen` / `NavigationModel` from `mapper.screens.map` — never from `mapper.app`** *(amended `2026-10-09-modular-batch`; the sibling exception is ordered in §6 — `home.py` lands last of the siblings because it uses `plug_repo` / `import_preview` / `MapScreen`)* | Domain must not know about screens or event loop. |
| `screens` | `model`, `store`, `design`, `widgets`, `keymap`, `office`, `osopen.safe_local_path`, `osopen.confine_reason`, `osopen.refusal_sentence`, `osopen.hard_linked`, `osopen.is_link` and `osopen.PATH_NOT_SUPPORTED` (only those six names; *amended Inc-9q, `A-125`: `PATH_OUTSIDE_WORKSPACE` is reached through `refusal_sentence`; amended Inc-9r, `A-126`: `PATH_THROUGH_LINK` is too, generate maps its refusals through `refusal_sentence` with `surface="generate"`*) | **`screens` → `app`** | A screen is mounted *by* the app; importing back up is a cycle. **B-02 — CLOSED at `2026-10-09-modular-batch` increment A2.** The four function-local imports that dodged the cycle at module load are gone: A1 moved the three helper back-edges (`factory.py:198`, `factory.py:217`, `settings.py:89`) to module-level imports of `mapper/screens/common.py`; A2 moved the last one (`factory.py:504`, `_PromptScreen`) to a module-level import of `mapper/screens/prompt.py`, whose four modals `mapper/app.py` re-exports (LLR-MOD.3.1). `tests/test_arch_osopen_callers.py` derives the absence from the ASTs — zero `screens` → `app` back-edges. *(Amended Inc-9o, `A-123`: the row once named one site at a stale line; the code had four.)* See the `screens/common` + `screens/prompt` and `screens/map` rows below and the batch worksheet in §6. |
| `screens/map` | `model`, `store`, `views`, `search`, `export`, `mermaid`, `diff`, `keymap`, `design`, `widgets`, `screens/common`, `screens/prompt`, `osopen` (see the `osopen` row) | Any import of `mapper.app`, module-level or function-local — a cycle through the re-export; **imports between concern modules or of sibling `screens/*` modules** — with the one declared exception that `screens/map/screen.py` MAY import its 11 concern modules, because it composes `MapScreen` from them; the concern modules never import each other and concerns communicate through `self` on the composed class, never through each other's modules; a mixin declaring `BINDINGS` or shadowing a core class constant. There is **no** function-local escape hatch: the F4 patch names are read by the modules that own their readers, so `app` keeps no back-edges (§4). *(Textual 8.2.8 spike rules, measured `2026-10-09` in `evidence/arq-mro-spike.transcript`: the trio `@on`, `DEFAULT_CSS` and `BINDINGS` declared in a plain mixin is silently IGNORED — banned in `screens/map` mixins, asserted by an AST guard, living only on the core `MapScreen` class; and `on_*` handlers run from EVERY class in the MRO that defines them — method names, handlers above all, must be pairwise-disjoint across the 12 modules, guarded by a derived AST test.)* |
| `screens/common` + `screens/prompt` | the same surface `screens` already has (`design`, `keymap`, `model`, `office`, the sanctioned `osopen` names) | Importable by any `screens/*` module and by `app`; they never import `app`, and never import `widgets` internals beyond what `screens` already may. They are the remediation this table has long prescribed for B-02: after `2026-10-09-modular-batch` increments A1/A2 land, the "known violations" note in the `screens` row above is deleted. |
| `widgets` | `design`, `model` (read-only value objects), `keymap` | `widgets` → `store` / `views` / `screens` / `app` / `osopen` | A widget renders state and emits a `Message`; it does not persist, navigate, or execute. **This is the ban that shapes the editable inspector**: the inspector cannot save a ficha and cannot open an attachment — it says *what the user did* and `app` decides what that costs. |
| `views` | `model`, `canvas`, `design`, `diff` (the `DiffResult` value shape only) | `canvas` → `views`; **`views` → textual**; `views` → `store` / `app` | Canvas is a dumb pixel buffer. Renderers stay headless so `export` can snapshot them and so a renderer is testable without an event loop. |
| `store` | `model` | `store` → `app` / `views` | Persistence must not be coupled to UI or renderers. |
| `search` | `model`, `store` | `search` → `views` | Search returns ids; rendering decides how to highlight. |
| `mermaid` | `model` | `mermaid` → `app` / `views` | Importer/exporter are format adapters, not UI. |
| `import_csv` | `model`, `mermaid` (`slugify`) | `import_csv` → `app` / `store` | Preview builds a `Graph`; committing it is the caller's decision. |
| `office` | — (stdlib `zipfile` + `re`) | `office` → `model` / `app` | Template filling is string substitution over OOXML; it must not learn the domain. |
| `diff` | `model`, `store`, local `git` CLI | `diff` → `app` / `views` | Diff reports facts; presentation is downstream. |
| `github` | `model`, `design` (`darkside.plain`, to coerce what it reports), `osopen.safe_local_path` (only that name) | `github` → `app` / `store` | Connector produces a Graph; persistence is the caller's responsibility. *(Amended `2026-08-26-ui-next-batch-02` Inc-9n, `A-122`: the row said `model` only, but `github.py` has imported `darkside` since the connector landed and `osopen.safe_local_path` since Inc-9m; the code was right and the map was stale.)* |
| `export` | `views` (only through Text snapshots) | `export` → `app` | Export writes files from a Rich Text; it does not mount screens. |
| `osopen` | — (stdlib only) | `osopen` → anything in `mapper`; **any module but `app` and `screens/map/opening` → `open_external`** *(amended `2026-10-09-modular-batch`: the one non-`app` call site moves from `app.py` to `mapper/screens/map/opening.py`, and the AST-derived allow-list in `tests/test_arch_osopen_callers.py` is updated in the same increment, Inc-B3)*; `widgets` / `views` → `osopen` | Two bans, both load-bearing. Inbound: `open_external` is referenced only from `app` *(amended `2026-10-09-modular-batch`: plus `screens/map/opening` after Inc-B3; until then this describes the tree as it is)* (and so is its launcher), so the call site is countable; `github` may import the one name `osopen.safe_local_path`, and `screens` that name plus `confine_reason`, `refusal_sentence`, `hard_linked`, `is_link` and the sentence constant `PATH_NOT_SUPPORTED`: none of them launches anything, and `confine_reason` (with `confine`, its thin wrapper) is the ONE containment rule (allow-list, a refusal of a colon or a normalised component on the text, lexical test, a no-link walk that asks again with the long-path prefix at MAX_PATH, then `resolve()` compared with the walked prefix plus the tail, *amended Inc-9r, `A-126`*), so every typed or sidecar path is decided by one function (`tests/test_arch_osopen_callers.py` derives both facts from the ASTs). Outbound: `osopen` importing `model` or `store` would let it discover its own targets, and the audit surface would stop being one file. |
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
| `KEYMAP` seat | `keymap` | `screens`, `widgets`, `app` | `KEYMAP: list[KeyBinding]`, `groups_for_keybar(...)`, `palette_items(q)` | **NO — Inc-1 owns it.** It becomes the single source from which screens generate `BINDINGS`. No other lane edits `mapper/keymap.py`. *(`2026-10-08-data-safety-batch`: in motion again, **Inc-1 owns it** — planned rows: `ctrl+s` → `save_draft` in the map scope, and a new modal scope `draft` (`s` save · `d` discard · `escape` stay, ruling R4) added to `MODAL_SCOPES` so the guard does not inherit `ctrl+p` / `?`. The whole-seat pin `tests/test_key_dispatch.py:137` moves with it.)* |
| **`ViewState` parameter object** · **PRESENT** | `views` | `app` | `mapper/views/state.py` declares `ViewState`, a **frozen** dataclass in which **every field carries a default**, plus `FOCUS_OWNERS`; and `IRenderer` as a `runtime_checkable` Protocol with `render(self, graph: Graph, state: ViewState) -> Text`. Initial roster: `selected_id`, `w`, `h`, `focus_owner`, `query`, `diff` | **LANDED 2026-08-28 in `2026-08-26-ui-next-batch-02` Inc-2** — the batch's headline A3, pre-authorised at intake. Every `render` definition under `mapper/views/` and every arg-ful call site migrated in one increment; `**kwargs` occurrences across the definition set are **0**. **The cardinalities are PINNED in `tests/test_a3_census.py`, deliberately not narrated here** — they were first published as 27 and 6, both measured before the increment had finished writing its own tests, and both wrong. A number in this row cannot be contradicted by the suite; a pinned one can. **Adding a defaulted field here is additive and never re-opens the A3** — only the first migration was one, which is what keeps four later increments out of A3 territory. `with_header` is deliberately NOT a field: it was a parameter no caller ever passed, so it is now unconditional in code. `query` is **transitional** and is replaced by a resolved `hits` set in Inc-4, where "what matches" gains a single owner. The module imports no Textual, so `views` stays headless and `export` stays testable without an event loop. |
| **`Canvas` `dots` / `bgs` layers** · **PRESENT** | `canvas` | `views` | `Canvas(w, h, tones=(), fallback="")` declares `dots` and `bgs` as empty mappings; `rows()` composes both in the declared precedence — an explicit cell outranks a wire, a wire outranks a braille dot, and a `bgs` background applies to whichever glyph won **unless that glyph's style declares its own background or is one the background cannot be composed onto — then the glyph keeps its style and the layer background is dropped**; out-of-bounds writes are dropped, not raised; a layer value outside `tones` paints `fallback` | **LANDED 2026-08-28 in `2026-08-26-ui-next-batch-02` Inc-1** — the batch's **second** A3, distinct from the `ViewState` row above. `RadialRenderer`'s two instance monkey-patches are deleted, asserted gone by a derived census. **`canvas` still depends on nothing:** the tone policy is INJECTED at construction rather than imported, because §3 declares this module's dependencies as `—`; the guard itself lives in `rows()`, the one place all four layers converge, which is what defeats a write-time setter (that would miss `radial.py`'s direct `cv.dots[...] = hue` assignment). Trigger **B4**'s consequence is asserted on the written artifact: `export.save_svg`'s bytes now carry the braille, and the four `RadialRenderer` byte-identity pins were re-baselined one at a time while all eight `Layered`/`Outline` pins held. |
| `open_external` | `osopen` | `app` **only** | `open_external(kind, target, *, workspace, launcher=None) -> str`; returns a status word | **NO — new, Inc-4 owns it.** Security-reviewed before Inc-4 signs off. |
| `FichaInspector.FieldCommitted` · **REMOVED** (data-safety Inc-1b) | `widgets` | `app` (`MapScreen.on_ficha_inspector_field_committed`, `mapper/app.py:3344`) and three test files (`tests/test_inspector.py:103,162`, `tests/test_g6_store_surrogates.py:133,152,176`, `tests/test_worklist_safety.py:254`) — census `grep -rn "FieldCommitted\|field_committed" --include=*.py mapper tests`, 2026-10-08 | `FieldCommitted(node_id, field, value)`, posted on blur, on `↵`, and on every `state` segment change (`mapper/widgets/inspector.py:347-373`) | **NO — `2026-10-08-data-safety-batch` Inc-1 removes it**, producer and consumer in the same increment. It is the immediate-write path B-36 is about; leaving the class or its handler alive leaves a second save path one `post_message` away. The three test files are re-pointed to the draft + `ctrl+s` path (trigger B1). |
| **`FichaInspector` draft surface** · **PRESENT** (data-safety Inc-1b) | `widgets` | `app` (`MapScreen`) **only** | Read-only to the consumer: `draft_node_id -> str \| None`, `draft_values() -> dict[str, str]` (a copy; keys are schema keys or the pseudo-keys `title` / `notes` / `state`), `has_draft() -> bool`, `clear_draft() -> None`. One node's draft at a time, in memory, for the life of the widget (= the life of its `MapScreen`). A field is dirty iff its value differs from the value the form SHOWED for it (`darkside.plain(stored)`), so opening a node never makes it dirty by itself. Every field goes through it, `state` included (ruling R2). | **YES — frozen at the PDR seal (I-1).** Built in Inc-1b; Inc-2 consumes it read-only. |
| **`DraftGuardScreen`** · **PRESENT** (data-safety Inc-1a) | `screens` | `app` (`MapScreen`, `MapperApp`) | `DraftGuardScreen(title: str, map_id: str = "")` → `ModalScreen[str]` (map id added at Inc-1a for R9), dismissed with exactly one of `"save"`, `"discard"`, `"stay"`; keys from the `draft` seat scope. Renders the node title with `markup=False` (the `SEC-H2` sink rule `_ConfirmScreen` already follows, `mapper/screens/prompt.py` *(moved from `app.py` at A2)*). Imports `design` and `keymap` only. | **NO — new, Inc-1 owns it.** |

| **MapScreen state roster (F1)** · **TARGET** | `screens/map` (core `screen.py`) | all 11 concern mixins | The 30 attributes, declared only in `MapScreen.__init__`, with the writer matrix as the discipline: no attribute gains a writer concern and no new cross-concern attribute is added without amending the census. (`_last_save_error`'s external writer is `_save_or_toast` via its `screen` parameter — that signature is part of the freeze.) | **YES — frozen by `2026-10-09-modular-batch` PDR** *(commitment: the package does not exist until B0)*. |
| **Cross-concern method surface (F2)** · **TARGET** | `screens/map` | `screens/map` (the mixins among themselves) | Every method with an in-edge from another concern: from painting `refresh_canvas`, `_view_state`, `_current_renderer`, `_canvas_size`, `_canvas_width`, `_header_rows`, `_unpainted_ids`, `_open_paint_pass`, `_declare_after_layout`, `_pagination_text`, `_minimap_text`; from panning `_clamp_pan`, `_consumes_pan`, `_reclamp_pan`, `_move_pan`, `_pan_revealing_selection`; from searching `_search_order`, `_search_hits`, `_search_is_live`, `_search_index`, `_count_line`, `_query_echo`, `_branch_name`, `_unfold_onto`, `_incomplete_order`, `_goto_gap`; from hints `_event_toast`, `_seat_glyph`, `_seat_label`, `_field_hint`, `_search_hint`, `_resting_hint`, `_declare_rebind`, `_walk_toast`, `_hint_with_opened`, `_clear_pan_hint`; from drafts `_guard_draft`, `guard_open`, `has_pending_draft`, `_save_draft`, `_drop_orphan_draft`, `_paint_draft_hint`, `_apply_field`, `_focused_field_id`, `_refocus_field`; from editing `_guard_focus_mutation`, `_subtree_size`, `_remove_subtree`; from undo `_push_snapshot`, `_pop_snapshot`, `_snapshots`; from navigation `_repoint`, `_current_crumb`; from the core `_establish_graph`, `_apply_region_visibility`, `_focus_owner`, `_chrome_width`. Names and signatures frozen; a concern module never calls a method of another concern that is not on this list. | **YES — frozen by PDR** *(commitment)*. |
| **Core class surface (F3)** · **TARGET** | `screens/map` (core `screen.py`) | the mixins, `app` | `MapScreen` keeps inheriting `textual.Screen`; `KEY_SCOPE`, `PAN_STEP_X/Y`, `MIN_CANVAS_WIDTH`, `_FOCUS_REGIONS`, `REVEAL_MARGIN_CELLS`, `METER_STEPS`, `_TOAST_CHROME_CELLS`, `UNDO_DEPTH`, `EXPORT_*`, `_MINIMAP_*` and `BINDINGS` stay class attributes of the core — mixins never shadow them. *Spike rules (Textual 8.2.8, measured `2026-10-09`): the trio `@on`, `DEFAULT_CSS` and `BINDINGS` declared in a plain mixin is silently IGNORED — all three are banned in `screens/map` mixins, and an AST guard over the package asserts their absence; they live only on the core class (`BINDINGS` among the class constants above). A core binding does dispatch to a mixin `action_*`, so actions may live in mixins.* | **YES — frozen by PDR** *(commitment)*. |
| **F4 patch surface** · **TARGET** | the module that reads each name (never `app`) | `tests` | Every monkeypatch target in the suite — **eight names**, from the census `grep -rnE "monkeypatch.setattr(|mock.patch(|app_module.[A-Za-z_]+ *=" tests` — is **repointed to the module that reads it** in the increment that moves the reader, and stays bound there. **Seven of the eight are module-global repoints** (ARCH-10/11), listed with the module each patch must target — i.e. the module that READS the name at call time: `save_svg` → `export.py` (`test_app.py`); `pan_extent` → the pan reader it moves with, `screens/map/panning.py` (`test_en8.py`); `LayeredRenderer` → `views/layered.py` (`test_en8.py`) — with the reading module named per patch path (ARCH-10/11): a patch travelling the CSV-import path targets `screens/import_preview.py` (executed, `_ImportPreviewScreen` builds `LayeredRenderer()` at `mapper/app.py:1137`, so that path's repoint lands at A7); `preview_csv` → `screens/home.py` (`test_inc9c.py:114`, `test_inc9n.py:285` — read by `HomeScreen` at `mapper/app.py:1090`, NOT by `_ImportPreviewScreen`, so the repoint lands at A4); `refusal_sentence` → `osopen.py` (`test_inc9q.py`); `SearchIndex` → `search.py` (`test_search.py`); `MAX_RENDER_NODES` → `screens/map/searching.py` (`test_search.py`, at B9). **`GitHubConnector.fetch` is the eighth name and is deliberately NOT repointed** (ARCH-10/11): every patch site reaches it as a **class attribute** — `monkeypatch.setattr(GitHubConnector, "fetch", ...)` (`test_en8.py:286`, `test_en9.py:48`, `test_inc9c.py:666,724`) or the string form `monkeypatch.setattr("mapper.app.GitHubConnector.fetch", ...)` (`test_app.py:22,110`, `test_inc9.py:151`, `test_inc9c.py:488`) — which mutates the class object itself, so the patch **survives a re-export**: setting the attribute on the class reached through `mapper.app` still patches the single class the repo screen reads. An **AST guard asserts each patched name is read by the module the patch targets**, landing in the same increment as the repoint. The "lazy read through `mapper.app`" shape (function-local `import mapper.app` + attribute access) is **banned**: it made `app` a silent back-edge, and it is deleted from §3 with it — `app` keeps no patch surface and no back-edges, and none of the seven module-global names is re-exported through `app` (`GitHubConnector` the class may be re-exported freely — the patch rides the class object, not the module attribute). | **YES — frozen by PDR** *(commitment)*. |
| **App↔screen surface (F5)** · **TARGET** | `screens/map` | `app`, `widgets` | `MapperApp` relies on `has_pending_draft()`, `guard_open()`, `_guard_draft(proceed, on_hold)` and `isinstance(s, MapScreen)`; widgets rely on the `on_*` handler names (`FichaInspector.*`, `Input.*`, descendant-focus events). None may be renamed. *Spike rule: `on_*` handlers run from EVERY class in the MRO that defines them — handler names must be disjoint across the mixins, and the pairwise-disjoint guard test (AST-walk the 12 modules) keeps them that way.* | **YES — frozen by PDR** *(commitment)*. |

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
| R-012 | **The per-node draft of model C lives in `FichaInspector`** (`widgets`), not in `MapScreen` and not in a new module. *(`2026-10-08-data-safety-batch`.)* | (a) `MapScreen` owns the draft and the inspector posts a message per keystroke — doubles the traffic, changes `show()`'s signature, splits "what is dirty" from "how dirty is painted" across two modules, and grows a 4957-line file. (b) A new pure module (`mapper/draft.py`) — a ~30-line dict with a node id does not earn a module, an A1 boundary or a source file out of a 4-file budget. | A second surface needs the same draft (the documents editor, a second inspector, a draft that must outlive the screen) — then the value object moves out of the widget into `model` or its own module, and that is an A1. |
| R-013 | **`FieldCommitted` is removed, not reshaped; `MapScreen` pulls the draft synchronously on save.** *(`2026-10-08-data-safety-batch`.)* | Reshape it into a `SaveRequested(node_id, values)` message. A posted message is fire-and-forget: it cannot carry the save's result back, yet after a failed save the screen must reload the map from disk and re-diff the draft against it before anything else happens (LLR-004.2), and the modal's `save → then leave` needs the save finished before the exit runs. A message would need a second message back and an ordering argument; a method call needs neither. | Textual gains a request/response message primitive, or the save becomes asynchronous (then both paths need the same completion handshake anyway). |
| R-014 | **The `save · discard · stay` modal is a new file in `screens`** (`mapper/screens/draft_guard.py`), binding its keys from the seat, not another literal-`BINDINGS` modal inside `app.py`. *(`2026-10-08-data-safety-batch`.)* | Add it next to `_ConfirmScreen` in `app.py` — zero new files, but it grows the file R-009 wants smaller, and a literal `BINDINGS` list is a key the legend and the seat pins cannot see (`#D9` migrated factory and settings off literal lists for that reason). | The 4-source-file budget for Inc-1 cannot absorb the new file — then it moves into `app.py` and this row is reversed with that reason. |

---

## 6 · Parallelisation worksheet *(filled per batch, at ARQ)*

Two increments are parallelisable when **`modules(A) ∩ modules(B) = { }`**, **or** when they touch the
same domain on **different layers** (UI/UX vs functional) *and* the interface between them is frozen and
neither lane touches it.

### Current batch — `2026-10-09-modular-batch` (split `mapper/app.py` — R-009 re-opened)

*(Cut from the accepted ARQ proposal §6: `modules(A) ∩ modules(B) = ∅` at file granularity. Honest
consequence: every increment that deletes lines from `app.py` collides with every other on that file, so
the extraction spine is serial. Parallelism exists (a) inside Inc-0, (b) between test-only follow-ups and
the spine, and — the deliverable — (c) between product lanes after Inc-B11.)*

**Increment cut** (each extraction increment ≤ 4 source files; every moved name is re-exported from `app.py` for compatibility, except the eight F4 patch targets, which are deliberately NOT re-exported — §4):

| Lane | Files it owns (source) | Moves |
|---|---|---|
| Inc-0 · test generalisation (0 source) | the six source-reading test files of proposal §5c (`test_draft_hygiene`, `test_darkside_census`, `test_keymap`, `test_en5`, `test_en7`, `test_app_imports_used` — mutually disjoint → parallel sub-lanes) | none — generalises the pins BEFORE any move, so no extraction increment ever runs red against a stale pin |
| **Spine A — `app.py` shrink, serial, helpers first:** | | |
| A1 | `screens/common.py` *(new)*, `app.py`, `screens/factory.py`, `screens/settings.py` | the common helpers + `MapHintLine` (ARCH-8 — a shared hint widget owned by `common.py`, not by the map hints concern, so it moves here at A1, not at B1); B-02 helper imports repointed |
| A2 | `screens/prompt.py` *(new)*, `app.py`, `screens/factory.py` | the four prompt modals; `factory.py`'s `_PromptScreen` import repointed — **B-02 closed** |
| A3 | `screens/construct.py` *(new)*, `app.py` | `ConstructScreen` |
| A5a | `screens/map/navigation.py` *(new, `NavigationModel` only)*, `app.py` | the nav model — split out of the old A5 and moved BEFORE B0, because `screens/map` owns it and B0/B8 read it; `screens/repo.py` no longer moves here (it is A5b, after B0) |
| B0 · MapScreen wholesale move (after A1–A3 + A5a — its imports need their homes) | `screens/map/__init__.py` *(new)*, `screens/map/screen.py` *(new)*, `app.py` | the whole class body, unchanged; `app.py` is now ~350 lines (imports/re-exports, `MapperApp`, `main`) |
| A5b | `screens/repo.py` *(new)*, `app.py` | `RepoScreen` — imports `MapScreen` / `NavigationModel` from `mapper.screens.map` (never `mapper.app`; §3); split out of the old A5 — after B0 so `MapScreen` exists, and before A6 because `PlugRepoScreen` pushes `RepoScreen` (`mapper/app.py:1207`) |
| A6 | `screens/plug_repo.py` *(new)*, `app.py` | `PlugRepoScreen` — imports `RepoScreen` from `mapper.screens.repo` (never `mapper.app`; §3) *(ARCH-9 correction, executed: `mapper/app.py:1184-1233` references only `RepoScreen`, pushed at `:1207` — it never touches `MapScreen`)* |
| A7 | `screens/import_preview.py` *(new)*, `app.py` | `_ImportPreviewScreen` — imports `MapScreen` from `mapper.screens.map` (never `mapper.app`; §3) |
| A4 | `screens/home.py` *(new)*, `app.py` | `HomeScreen` — **last of the siblings**: it uses `plug_repo` (A6), `import_preview` (A7) and `MapScreen` (B0), so it lands after all of them (needs A1 helpers + A2 modals too) |
| **Spine B — one concern per increment, serial on `screen.py`, 2 source files each (order = risk: smallest/cleanest first, the spike first of all, the 686-line painting concern last):** | | |
| B1 | `screens/map/hints.py` *(new)* | hints mixin (ARCH-8: `MapHintLine` already moved at A1 — it is not part of this concern) — **the spike**: proves, with a pilot-driven hint test, that `action_*` and `on_*` dispatch through a mixin while BINDINGS stay on the core class (the ARQ spike, `evidence/arq-mro-spike.transcript`) before anything coupled moves |
| B2 | `screens/map/exporting.py` | export concern (3 shared attrs, 0 calls in) |
| B3 | `screens/map/opening.py` (+ `tests/test_arch_osopen_callers.py` allow-list) | open concern; carries the osopen §3 amendment |
| B4 | `screens/map/undo.py` | undo concern (calls in only from drafts/edits/focus) |
| B5 | `screens/map/focus_mode.py` | focus concern — rewrites `graph`/`nav` wholesale, so it moves early and freezes the multi-writer set under F1 |
| B6 | `screens/map/editing.py` | edits concern — funnel consumer of `_guard_draft` |
| B7 | `screens/map/drafts.py` | the `_guard_draft` funnel itself, after its consumers |
| B8 | `screens/map/navigation.py` gains the nav mixin | cursor actions, `_repoint`, crumb, open-ficha/home/back — file exists since A5a, so only `screen.py` + `navigation.py` are touched |
| B9 | `screens/map/searching.py` | search concern; the F4 `MAX_RENDER_NODES` repoint lands here — the test patch moves off `mapper.app` onto the module that reads it (§4) |
| B10 | `screens/map/panning.py` | pan concern — shares 21 attrs with painting, kept adjacent to it |
| B11 | `screens/map/painting.py` | views concern incl. `refresh_canvas` (25 call sites in 9 concerns) — moves last so `screen.py` remains the integration point throughout |
| B12 | this document + tests (0 source) | map amendment (§2/§3 per §1c/§4, landed above as TARGET) is validated; the F1/F2 freeze is made mechanical (census-diff test over the package) |

**Order constraints:** Inc-0 ∥ anything → Spine A (serial: A1 → A2 → A3 → A5a → B0 → A5b → A6 → A7 → A4; ARCH-9: A5b lands before A6 because `PlugRepoScreen` pushes `RepoScreen` (`mapper/app.py:1207`); A4 is last of the siblings because it uses `plug_repo`, `import_preview` and `MapScreen`, so it lands only after A6/A7 and B0) → Spine B (serial on
`screen.py`) → B12. Test-only follow-ups (inc9p/9q arm extension, en5 FILES if not package-scanned) ride
their extraction increment or run parallel to the spine afterwards.

**Payoff after B11:** `searching.py`, `editing.py`, `painting.py`, `exporting.py`, `drafts.py`,
`home.py`, `repo.py`… are disjoint files — two feature workers never share a file. That is the payoff
the batch exists for: parallelism is its output, not its method.

### Previous batch — `2026-10-08-data-safety-batch` (B-36 model C + acceptance debt + FLAKE-2)

*(The `2026-08-25-ui-next-batch-01` worksheet is superseded and removed; it is in git history. Its
risks A-3 — "define the commit point explicitly; do not add `save_field` to `MapStore`" — and A-6 —
"where undo state lives" — are the two this batch answers: the commit point is `ctrl+s` or the modal's
`save`, the write stays the whole-graph `MapStore.save(map_id, graph)`, and undo stays the per-map stack
on `MapperApp.undo_stacks` (`mapper/app.py:3503`, `:4902`).)*

| Lane | Story | Modules | Layer | Files it owns (source · tests) | Source files |
|---|---|---|---|---|---|
| Inc-1a · draft guard scaffolding | US-001 | `keymap`, `screens` | UI/UX | `mapper/keymap.py` (the `draft` scope), `mapper/screens/draft_guard.py` *(new)*, `mapper/screens/__init__.py` (export, `:4-11`) | **3** |
| Inc-1b · draft + `ctrl+s` + node-change guard | US-001 | `widgets`, `keymap`, `app` | functional + UI/UX | `mapper/widgets/inspector.py`, `mapper/app.py`, `mapper/keymap.py` (the `ctrl+s` row) · `tests/test_inspector.py`, `tests/test_g6_store_surrogates.py`, `tests/test_worklist_safety.py` and the Inc-1 regression obligations | **3** |
| Inc-1c · UX-1 conditions (unplanned; created by the Inc-1b UX-1 review) | US-001 | `app`, `widgets` | UI/UX | `mapper/app.py`, `mapper/widgets/inspector.py` · `tests/test_inc1c_ux.py` | **2** |
| Inc-2 · leave-screen and quit guards | US-001 | `app` | functional + UI/UX | `mapper/app.py` · the new draft-save test file | **1** |
| Inc-3 · FLAKE-2 deflake | US-004 | — (tests only) | test | `tests/test_help_scope.py` (`:93`, `:365`), `tests/test_en7.py` (`:246`), `tests/test_repair_layout.py` (`:118`) | 0 |
| Inc-4 · AT-044 node + AT reconciliation | US-002, US-003 | — (tests + records) | test / traceability | a NEW test file for AT-044 (not `tests/test_help_scope.py` — see the re-cut below); the batch ledger and `.dev-flow/BACKLOG.md` for AT-025b, AT-041/042 (reconciled) and AT-033/034/035 (retired) | 0 |

| Pair | Intersection | Parallel? |
|---|---|---|
| 1–2 | `{app}` + file `mapper/app.py` + the draft-save test file | **no** — and Inc-2 consumes the draft surface Inc-1 creates: an ordering dependency, not just a conflict |
| 1–3 | `{}` by module; files disjoint **if** Inc-1's census finds no inspector-commit oracle in `tests/test_help_scope.py`, `tests/test_en7.py` or `tests/test_repair_layout.py` (`planned` at PDR) | yes, conditionally |
| 1–4 | `{}`; files disjoint | yes |
| 2–3 | `{}`; files disjoint | yes |
| 2–4 | `{}`; files disjoint | yes |
| 3–4 | `{}` by module; **file collision on `tests/test_help_scope.py` as the stories are written** (US-002 places the AT-044 node there; US-004 edits `:93` and `:365`) | **yes, only after the re-cut**: AT-044 goes in its own test file and US-003's reconciliation is written to the ledger, not into test docstrings |

**Verdict: the product lane is one serial chain, Inc-1 → Inc-2; the two test-only lanes are disjoint
from it and from each other after one re-cut.** Merit order still decides what goes first, and it says
**Inc-3 first**: FLAKE-2 sits in the help-scope file the whole-branch gate runs, and a poisoned
instrument invalidates every gate that follows it, Inc-1's included (P-05).

**Why US-001 is two increments and not one.** All four source files are needed for the first safe
state — the draft, the key that saves it, and the guard that stops a node change from walking away from
it — so Inc-1 sits at the cap. The other two exits (leaving the map screen; quitting) touch only
`mapper/app.py` and reuse the modal unchanged, so they cut cleanly into Inc-2. The intermediate state
between the two never writes a stray keystroke to disk (B-36 is closed at Inc-1); what it can still do
is drop an unsaved draft on `q` / `esc` / `ctrl+q` without asking, which Inc-2 closes before merge.

If the intersection is **not** empty there are exactly two exits, and both are explicit decisions:

1. **re-cut the increments**, or
2. **move the module boundary — here, in this document**.

The second is the one that actually prevents spaghetti; the first only routes around it for one batch.

- ⚠ Same-domain lanes with an interface that is **not** frozen: that is not parallelism, it is a collision
with a delay — both lanes advance and meet the conflict at integration, the most expensive moment.
- **This orders the CODE.** The order of *merit* — what goes first — still comes from the intake risk estimate.

### Architectural risks this cut hands to the requirements phase

| # | Risk | Where it bites | What requirements must settle |
|---|---|---|---|
| A-8 | **Textual 8.2.8 dispatches every `on_*` handler across the MRO** (measured by the B-36 prototype, which had to neutralise `FichaInspector.on_input_blurred` / `on_input_submitted` and `MapScreen.on_ficha_inspector_field_committed` to stop double commits). A subclass override does not replace a base handler; both run. | Inc-1 | The change is made **in place** in `FichaInspector` and `MapScreen`; no subclass, no monkey-patch. An AT asserts the blur path writes nothing (sha256 of `.mmd` + `_nodos.yml` before/after), so a surviving base handler reddens it. |
| A-9 | **`refresh_canvas` re-points and rebuilds the inspector on every refresh** (`mapper/app.py:3281`, the only `.show(` call on it). A draft held only in widget values is wiped by the next repaint. | Inc-1 | The draft is overlaid when rows are BUILT (`_rows`), not re-applied after a rebuild; the node-change guard sits at that one re-pointing site, before `show()` is called, so every cursor move (j/k/h/l, rail, `n`/`N`, `M`, worklist jump, add child) is guarded by construction rather than by enumeration. |
| A-10 | **A failed save must not leave the draft in the in-memory graph.** Today's handler mutates `self.graph` before `_save_or_toast`; on failure the mutation stays, and the next structural save (`a`, `x`, `A`, `X`, `u`) would write it — a second save path, the defect class itself. | Inc-1 | On a failed save the map is reloaded by the screen's own load path and the draft keeps exactly the fields that did not reach disk; failure handling writes no map file; the modal's `save` then behaves as `stay` (LLR-004.2). One `_push_snapshot()` per successful save, so `u` undoes one `ctrl+s` (ruling R3). |
| A-11 | **Exits that are not on the ruling's list.** `ctrl+q` is live on every screen (`MapperApp._merge_bindings()` → `ctrl+c`, `ctrl+p`, `ctrl+q`, `question_mark`; Textual's `ctrl+q` is `priority=True`); following a link pushes a second `MapScreen` (`mapper/app.py:3566`); `u` replaces the graph under a pending draft; a terminal kill cannot ask anything. | Inc-1, Inc-2 | Quit guards every `MapScreen` on `screen_stack`, not only the top one, and is not re-entrant (a second `ctrl+q` while the guard is up does not stack a second modal). Link-follow is guarded unconditionally (R6) and `u` leaves the draft alone (R5). A killed terminal loses the draft by design (R1). |
| A-12 | **The modal paints a file-derived title.** | Inc-1 | `markup=False` at the sink, as `_ConfirmScreen` does (`SEC-H2`); the `security-reviewer` lens at PDR covers it with the write path (`01-requirements.md` §6.3). |
| A-13 … A-15 | Residuals accepted at P2 (typed-ahead `d` discards a draft; a save on disk without an undo step; a double index failure). Their one home is `.dev-flow/2026-10-08-data-safety-batch/01-requirements.md` §6.3 | — | Recorded, not mitigated (operator ruling at the P1 cap). |
