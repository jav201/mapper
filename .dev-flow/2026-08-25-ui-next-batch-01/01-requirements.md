# 01 — Requirements · `2026-08-25-ui-next-batch-01` · variant A «taller», P1

> ISO/IEC/IEEE 29148 + EARS. Normative keyword **`shall`** appears only inside HLR/LLR statements.
> `should` inside a requirement statement is a writing error and a Phase-2 blocker.
> Artifact language **English**; the product's UI strings are **Spanish**.

---

## 1 · Purpose and scope

Recompose `MapScreen` into the round-9 variant **A «taller»** skeleton — left rail, centre canvas,
right **editable** inspector — and close five P1 stories that together move the map from a
read-only viewer to an operated instrument: in-situ editing, attachments, a trustworthy keymap,
a coverage worklist, and destructive-action safety.

**Out of scope, explicitly:** canvas pan/fold/minimap/braille edges (batch 2); the repo screen
redesign (batch 3); palette/colour-token expansion; any change to a frozen interface — in
particular `IRenderer.render(graph, selected_id, w, h, **kwargs) -> Text` is **not** extended.

## 2 · Stories, refinement and premises

### 2.6 · Definition of Ready

| Story | Valuable | Estimable | Testable (black-box) | Verdict |
|---|---|---|---|---|
| US-N01 edición in-situ | closes coverage→fill without leaving the map | path known: `Ds*` components + `MapStore.save` | edit a field, re-read the file from disk | **READY** |
| US-N02 adjuntos | attachments become usable, not just displayed | `os.startfile`/`xdg-open`/`webbrowser`; no new dependency | add/remove observed in the saved sidecar; open observed through an injected launcher | **READY** |
| US-N03 keymap único | discoverability is currently a lie: 0/33 palette entries work | generate `BINDINGS` from `KEYMAP` | conformance walk over a runtime-derived set | **READY** |
| US-N04 worklist de cobertura | turns a report into a work queue | existing `CoverageScreen` + the new inspector | `↵` lands on the node with the right field focused | **READY** |
| US-N05 seguridad | today `x` destroys a subtree with no confirmation | modal exists (`_ConfirmScreen`); undo moves to `App` | subtree survives a declined confirm; undo survives a screen round-trip | **READY** |

All five stories pass the Definition of Ready. None is `REFINE`, `SPIKE` or `OUT`.

### 2.7 · Premise table (C-43) — every premise executed against disk

Tiers: **axiom** (validated *and* verified) · **hypothesis** (introduced by this batch or inherited
from the round-9 design batch — *written down is not verified*) · **premise** (a claim about the
world). Evidence is an executed probe or a `file:line`; **citing another document is not evidence**.

| # | Proposition | Tier | Verdict | Executed evidence | Disposition |
|---|---|---|---|---|---|
| P-1 | Zero of the 33 keymap entries resolve to an `action_*` method on any screen, so no palette entry can dispatch. | premise | ✅ TRUE | Probe over `KEYMAP` × `{MapScreen, MapperApp, HomeScreen, RepoScreen}` computing `action_{action.replace(' ','_')}`: printed `P-1 RESULT: 0/33`. | US-N03 is the fix; the conformance AT is derived from `KEYMAP` at runtime (C-31). |
| P-2 | `HintLine` exposes no way to change its text after mount. | premise | ✅ TRUE | `mapper/widgets/chrome.py:42-49` — `__init__` calls `self.update(...)`; the class defines no setter, unlike its siblings `TabStrip.set_crumb` (`:24`) and `KeyBar.set_groups` (`:37`). | LLR-N01.6 adds `set_hint`, matching the sibling naming. |
| P-3 | `MapScreen` renders the ficha twice. | premise | ✅ TRUE | `app.py:1102` mounts `GroupBox(Static(id="map-ficha"))` and `app.py:1247` fills it from `_ficha_text`; independently `views/layered.py:225-251` appends its own "ficha strip" to the canvas `Text`. | The inspector replaces both. The strip is **removed** from `LayeredRenderer` (D4) — suppressing it would require a new `render` kwarg, i.e. a frozen-interface change. |
| P-4 | The nine `Ds*` components are used by zero production screens. | premise | ✅ TRUE | `grep -rn "Ds[A-Z]" mapper/ --include=*.py` outside `widgets/components.py` matches **only** `mapper/screens/settings.py` (the canary), lines 13-21 and 69-77. | The inspector reuses them; this batch is the first production consumer. |
| P-5 | `x` archives a non-root subtree with no confirmation. | premise | ✅ TRUE | `app.py:1520-1526`: the `_ConfirmScreen` is pushed **only** when `self.nav.cursor == self.graph.root_id`; the `else` branch calls `do_archive(True)` directly. | US-N05 makes confirmation unconditional. |
| P-6 | The undo stack is per-`MapScreen` and is lost when the screen is popped. | premise | ✅ TRUE | `app.py:1094` — `self._snapshots: list[bytes] = []` is an instance attribute of `MapScreen`, constructed fresh on every `MapScreen(...)` push (`app.py:1351`, `:589`). | US-N05 moves it to `App`, keyed by `map_id` (R6). |
| P-7 | The ficha surfaces hard-code schema key letters instead of `SchemaField.label`. | premise | ✅ TRUE | `app.py:1270-1277` hard-codes the strings `documento`/`dueño`/`creado` against `fields["D"]`/`["O"]`/`["Y"]`; `screens/coverage.py:124` returns `f.key`. | LLR-N01.2: every inspector row is labelled from `SchemaField.label`; the coverage report shows labels too. |
| P-8 | There is no add / open / remove UI for attachments. | premise | ✅ TRUE | The only reference outside `model.py`/`store.py` is the read-only render at `app.py:256-259`. | US-N02. |
| P-9 | The module map is stale: tracked files fall under no declared module. | premise | ✅ TRUE | `git ls-files mapper/` matched against §2's declared globs: **30 tracked, 10 undeclared** (`__init__.py`, `darkside.py`, `diff.py`, `import_csv.py`, `keymap.py`, `motion.py`, `office.py`, `widgets/__init__.py`, `widgets/chrome.py`, `widgets/components.py`). | ARQ fired on its own and amended `docs/ARCHITECTURE.md`; the sweep is re-run to 0 at the ARQ gate. |
| P-10 | The round-9 prototype verifies variant A's **interactions**. | hypothesis | ❌ **FALSE** | `prototypes/ui_next/generate.py` renders **static SVG** via a `Sheet` cell buffer and `console.save_svg` — it contains no Textual widget, no focus model and no key handling. | **C-16.** The prototype proves design intent only. Every `AT` drives the real mechanism (`pilot.press`), never `.focus()` or a direct `action_*` call, where the story promises a keystroke. |
| P-11 | A focused Textual `Input` suppresses the screen's single-letter bindings, so typing `j` in an edit field does not navigate the map. | hypothesis → ✅ verified | ✅ TRUE | Executed probe on textual 8.2.8: with an `Input` focused, `press("j","a")` produced `input value 'ja'` and `bindings fired: []`; with `set_focus(None)`, `press("j")` produced `fired: ['nav']`. | Risk R2 is structurally handled by Textual's focus model. LLR-N01.5 requires the inspector's edit surfaces to be real `Input` widgets, and `AT-N01d` asserts it rather than assuming it. |
| P-12 | The `LayeredRenderer` ficha strip is asserted by no existing test, so removing it orphans nothing. | premise | ✅ TRUE | Reverse census (C-26) over `tests/` for the strip's distinctive strings: `"selecciona un nodo"` → 0 hits; `"sin acta"` → 1 hit, `tests/test_app.py:138`, which asserts `"nodos sin acta"` on the **HomeScreen hero** (`app.py` `_hero_text`), a different producer. | Removal is safe; the census is re-run at the Inc-2 gate. |
| P-13 | The repository has byte-identity goldens that a source change could drift. | premise | ❌ FALSE (and that is the safe direction) | `tests/goldens` does not exist; no test in `tests/` reads a golden file. | Trigger **B3** does not fire. Recorded with its probe so "did not fire" is distinguishable from "was not evaluated" (C-48). |

**Two premises came back other than plain-true, and both changed the plan:** P-10 (FALSE) forbids
accepting any interaction on the prototype's authority, and P-12/P-13 (executed negatives) are what
make the strip removal and the absence of golden drift admissible rather than assumed.

---

## 3 · High-level requirements, with their acceptance blocks

Each story carries a first-class **Acceptance block**: the observable outcome, the shipped surface
that produces it, and the `AT` node that gates it. The `AT` roster is specified in
`01b-acceptance-design.md` and is reconciled to real collected nodes at Phase 4 (rule V-5).

### HLR-N01 — in-situ editing

> **HLR-N01.** When the operator selects a node on `MapScreen`, the system **shall** present an
> inspector panel that permits editing the node's title, state, notes and every field declared in
> the map's schema, and **shall** persist each committed edit through `MapStore.save`.

**Acceptance (black-box).** Observable outcome: after editing a field in the inspector and
committing, the value is present in the `_nodos.yml` written to disk and is returned by a fresh
`MapStore.load`. Shipped surface: the inspector panel on `MapScreen`. Gate: `AT-N01a` (schema
field, output-then-consume per **C-12**), `AT-N01b` (state, a non-default value per **C-10**),
`AT-N01c` (labels, not key letters), `AT-N01d` (typing in a field does not navigate the map),
`AT-N01e` (hostile file-derived text renders literally, per **C-17**).

| id | Low-level requirement | Verification |
|---|---|---|
| LLR-N01.1 | The inspector **shall** render one row per `SchemaField` in `graph.schema`, plus rows for title, state and notes. | test (pilot) — row count equals `len(schema) + 3` |
| LLR-N01.2 | Each schema row **shall** be labelled with that field's `SchemaField.label`; the raw `key` **shall not** be the row's label. | test (pilot) — `AT-N01c` |
| LLR-N01.3 | A row whose `SchemaField.required` is true and whose value is empty **shall** be rendered in the alert tone, and **shall** be counted in the panel's coverage meter. | test (pilot) |
| LLR-N01.4 | Committing an edit **shall** call `MapStore.save` exactly once with the mutated graph. | test (unit) — call count == 1 |
| LLR-N01.5 | Edit surfaces **shall** be Textual `Input` widgets, so that a focused field consumes single-letter keys instead of triggering screen navigation bindings. | test (pilot) — `AT-N01d`; premise P-11 |
| LLR-N01.6 | `HintLine` **shall** expose a setter that replaces its text after mount. | test (unit) |
| LLR-N01.7 | `LayeredRenderer` **shall not** emit a ficha strip; the inspector is the sole ficha surface. | test (unit) + reverse census P-12 |
| LLR-N01.8 | Every inspector line carrying file-derived text **shall** be constructed with explicit styles (`Text.assemble` / `rich.markup.escape`) so markup in the data is rendered literally. | test (pilot) — `AT-N01e` |

### HLR-N02 — attachments

> **HLR-N02.** When a node is selected, the system **shall** permit the operator to add, open and
> remove attachments from the inspector, and **shall** hand `url` and `file` attachments to the
> operating system's default application without invoking a shell.

**Acceptance.** Adding an attachment makes it appear in the reloaded sidecar; removing it makes it
absent; opening it calls the launcher exactly once with the attachment's path. Gate: `AT-N02a`
(add, observed through `MapStore.load`), `AT-N02b` (remove — the discriminating negative),
`AT-N02c` (open, launcher injected and asserted), `AT-N02d` (a hostile path/scheme is refused).

| id | Low-level requirement | Verification |
|---|---|---|
| LLR-N02.1 | The inspector **shall** list the selected node's attachments and expose an "add" affordance. | test (pilot) |
| LLR-N02.2 | Adding an attachment **shall** append an `Attachment` to the node's ficha and persist it. | test (pilot) — `AT-N02a` |
| LLR-N02.3 | Removing an attachment **shall** delete exactly that entry and persist the result. | test (pilot) — `AT-N02b` |
| LLR-N02.4 | Opening **shall** dispatch through `mapper/osopen.py`, which **shall not** use a shell and **shall** accept only the `url` and `file` kinds. | test (unit) — 0 shell invocations |
| LLR-N02.5 | A `url` attachment whose scheme is not `http` or `https` **shall** be refused and reported, not launched. | test (unit) — `AT-N02d` |

### HLR-N03 — one keymap

> **HLR-N03.** The system **shall** derive every screen's key bindings, the command palette's
> entries and the help overlay's contents from a single declaration in `mapper/keymap.py`, and
> every entry the palette or help offers for the active screen **shall** resolve to an action that
> the active screen executes.

**Acceptance.** For every entry the palette shows on a screen, selecting it executes a real action;
help shows exactly the same set. Gate: `AT-N03a` (the conformance walk, replacing the vacuous
test), `AT-N03b` (an entry selected in the palette produces its observable effect),
`AT-N03c` (help and the screen's live bindings are the same set), `AT-N03d` (keybar truncation is
visible when the bar overflows).

| id | Low-level requirement | Verification |
|---|---|---|
| LLR-N03.1 | `KeyBinding` **shall** carry the action's method stem and a separate human label, so the dispatched name is never the Spanish prose. | test (unit) |
| LLR-N03.2 | Each screen's `BINDINGS` **shall** be generated from `KEYMAP` filtered by that screen's scope. | test (unit) |
| LLR-N03.3 | For every `KeyBinding` in scope `s`, the screen class owning `s` **shall** define `action_<stem>`. | test (unit) — `AT-N03a`, input set derived from `KEYMAP`, threshold: 100 % of a set whose size is asserted ≥ 30 |
| LLR-N03.4 | The palette and the help overlay **shall** list exactly the bindings in the active screen's scope. | test (pilot) — `AT-N03c` |
| LLR-N03.5 | When the keybar's content exceeds its width, it **shall** render a visible truncation marker naming the count hidden and the key that reveals the rest. | test (pilot) — `AT-N03d` |

### HLR-N04 — coverage worklist

> **HLR-N04.** When the operator selects a row in the coverage report, the system **shall** move the
> map cursor to that node and place input focus on the first required field that node is missing;
> and the system **shall** provide an action that advances to the next missing required field
> across the whole map.

**Acceptance.** After `↵` on a coverage row, the cursor is that node and the focused widget is the
input bound to its first missing field. Gate: `AT-N04a` (jump + focus), `AT-N04b` (the worklist
advances to a *different* node's field, per **C-10** — a non-default step), `AT-N04c` (a fully
covered map reports "nothing missing" rather than cycling forever).

| id | Low-level requirement | Verification |
|---|---|---|
| LLR-N04.1 | Selecting a coverage row **shall** set `nav.cursor` to that node id. | test (pilot) |
| LLR-N04.2 | After the jump, focus **shall** be on the input for the first `SchemaField` that is required and empty for that node, in schema order. | test (pilot) — `AT-N04a` |
| LLR-N04.3 | The "next missing field" action **shall** traverse nodes in the coverage report's order and wrap once, and **shall** report exhaustion when no required field is missing anywhere. | test (pilot) — `AT-N04b`, `AT-N04c` |

### HLR-N05 — destructive-action safety

> **HLR-N05.** Before removing or archiving any subtree the system **shall** obtain explicit
> confirmation from the operator; and the undo history **shall** be held by the application so
> that it survives leaving and re-entering a map within one session.

**Acceptance.** Declining the confirmation leaves the map on disk unchanged; accepting removes the
subtree; leaving a map and returning still permits undoing the last change. Gate: `AT-N05a`
(declining preserves the subtree — the discriminating negative), `AT-N05b` (accepting removes it),
`AT-N05c` (undo survives a screen round-trip), `AT-N05d` (undo on an empty stack reports, does not
raise).

| id | Low-level requirement | Verification |
|---|---|---|
| LLR-N05.1 | `action_archive` **shall** push the confirmation modal for every node, including non-root nodes. | test (pilot) — `AT-N05a` |
| LLR-N05.2 | A declined confirmation **shall** leave the graph and both on-disk text files byte-unchanged. | test (pilot) — `AT-N05a` |
| LLR-N05.3 | The undo stack **shall** live on the `App`, keyed by `map_id`, and **shall not** be reset when a `MapScreen` is constructed. | test (pilot) — `AT-N05c` |
| LLR-N05.4 | Undo with an empty stack **shall** notify and return without raising. | test (unit) — `AT-N05d` |

---

## 4 · Constraints

| # | Constraint |
|---|---|
| CON-1 | No frozen interface changes: `Graph`, `Canvas`, `MapStore`, `IRenderer.render`, `SearchIndex.query`, the mermaid round-trip, `GitHubConnector.fetch`, `save_svg`/`save_png`. Asserted at every increment gate by re-reading the signatures. |
| CON-2 | No new third-party dependency. `os.startfile` / `xdg-open` / `webbrowser` are stdlib. |
| CON-3 | ≤4 **source** files per increment; tests uncapped. |
| CON-4 | darkside visual language: depth by background step, borders only on modals, `#1783ff` only on interactivity, selection is a solid block, lowercase chrome. |
| CON-5 | Text files remain the truth; `mapper.db` is never committed and stays rebuildable. |
| CON-6 | Nothing under `prototypes/` is modified or staged. |

## 5 · Traceability

### 5.2 · Dual traceability

A requirement is complete only when **both** chains exist: behavioural `US → AT → observed
outcome`, and functional `US → HLR → LLR → TC`. The matrix is maintained in
`06-docs/traceability-matrix.md` and reconciled at Phase 4.

| US | HLR | LLRs | AT ids |
|---|---|---|---|
| US-N01 | HLR-N01 | LLR-N01.1 … LLR-N01.8 | `AT-N01a`, `AT-N01b`, `AT-N01c`, `AT-N01d`, `AT-N01e` |
| US-N02 | HLR-N02 | LLR-N02.1 … LLR-N02.5 | `AT-N02a`, `AT-N02b`, `AT-N02c`, `AT-N02d` |
| US-N03 | HLR-N03 | LLR-N03.1 … LLR-N03.5 | `AT-N03a`, `AT-N03b`, `AT-N03c`, `AT-N03d` |
| US-N04 | HLR-N04 | LLR-N04.1 … LLR-N04.3 | `AT-N04a`, `AT-N04b`, `AT-N04c` |
| US-N05 | HLR-N05 | LLR-N05.1 … LLR-N05.4 | `AT-N05a`, `AT-N05b`, `AT-N05c`, `AT-N05d` |

## 6 · Amendment record

### 6.5 · Requirement amendments

#### Amendment 1 — 2026-08-25, folded from the ARQ station and the Phase-1 `qa-reviewer` pass

Nine changes. Each was forced by an **executed** finding, not by a reviewer's opinion.

**A1 · `KeyBinding` must separate the Textual key name from the display glyph.**
*Measured:* `KEYMAP.key` currently holds display glyphs (`↵`, `esc`, `/`) while Textual `BINDINGS`
need key names (`enter`, `escape`, `slash`). 11 keymap keys are absent from the live `BINDINGS`
and 3 exist the other way round. Generating `BINDINGS` from today's `key` field would bind
literally nothing.

> **LLR-N03.1 — Before:** *"`KeyBinding` shall carry the action's method stem and a separate human
> label, so the dispatched name is never the Spanish prose."*
> **After:** *"`KeyBinding` **shall** carry four separable fields — `key` (the Textual key name),
> `glyph` (the display form shown to the operator), `action` (the `action_*` method stem) and
> `label` (Spanish prose) — so that the bound name, the dispatched name and the displayed name are
> never the same string by accident."*
> **New tokens:** `glyph`. **Deleted:** none.

**A2 · The group → scope mapping must be written down before `BINDINGS` are generated from it.**
*Measured:* `KEYMAP` contains **five** duplicate chords, not the one assumed — `f`, `j`, `k`, `↵`,
`esc`. Four are deliberate modal overrides belonging to the `palette` group; `f`
(`fábrica`[doors] vs `alternar foco`[view]) is a genuine collision in one scope.

> **New — LLR-N03.6.** *"Every `group` **shall** map to exactly one declared scope, and two
> bindings **shall** share a key only when their scopes differ. A duplicate chord within one scope
> **shall** fail a unit test at import time."*

**A3 · The inspector must not write to the store — the dependency ban forbids it.**
*Evidence:* `docs/ARCHITECTURE.md` §3 bans `widgets → store`. The inspector is a `widgets` module.

> **LLR-N01.4 — Before:** *"Committing an edit shall call `MapStore.save` exactly once with the
> mutated graph."*
> **After:** *"Committing an edit **shall** post a message from the inspector to the owning screen;
> the screen — never the widget — **shall** call `MapStore.save` exactly once per commit. The
> inspector **shall not** import `mapper.store`."*
> **Rationale:** honours the `widgets ⇸ store` ban, and keeps the whole-graph write on the one
> object that owns the graph. Per-keystroke saving is excluded: it would rewrite both text files on
> every character.

**A4 · "Which required fields are missing" gets exactly one owner.**
*Risk closed (ARQ A-2):* the rail lattice (Inc-3) and the worklist (Inc-5) would each compute it,
and the two views would drift on what "complete" means.

> **New — LLR-N01.9.** *"`mapper/model.py` **shall** expose a single function returning a node's
> missing required `SchemaField`s in schema order; the inspector, the rail and the coverage
> worklist **shall** all consume it and **shall not** re-derive it."*
> **Note:** additive to `model`; it does not alter the frozen `Graph` shape, so it is not A3.

**A5 · The markup-safety prescription was wrong in the requirement and is corrected here.**
*Measured — the current code is wrong in **both** directions:* `app.py:1258` calls
`rich.markup.escape` inside a `Text.append` path, which does **not** parse markup, so the escape's
backslash leaks to the screen (rendered plain measured as `▸ \[bold red]PWN\[/] …`, `has
backslash-bracket: True`, `has ESC: True`). Meanwhile `Static("[bold red]PWN[/]")` **does** parse
(`plain='PWN'`, `spans=[Span(0,3,'bold red')]`).

> **LLR-N01.8 — Before:** *"…shall be constructed with explicit styles (`Text.assemble` /
> `rich.markup.escape`) so markup in the data is rendered literally."*
> **After:** *"Every inspector line carrying file-derived text **shall** be constructed as
> `Text.assemble((plain(value), style))`, where `plain()` strips C0/C1 control characters and
> **shall not** call `rich.markup.escape`. The inspector **shall not** pass a bare `str` to
> `Static`, because `Static` parses markup while `Text.append` does not."*
> **Deleted tokens:** `rich.markup.escape` as a prescribed remedy. **New:** `plain()`.

**A6 · Undo is specified, not merely relocated.** (ARQ A-6: *"undo" is not a specification.*)

> **New — LLR-N05.5.** *"The undo history **shall** be snapshot-based (the existing mermaid +
> sidecar capture), held per `map_id`, capped at 20 entries per map, and **shall** revert a
> destructive action even after it has been persisted by `MapStore.save`."*

**A7 · The OS-launch seam is named once.** ARQ declared the module `mapper/osopen.py` in the module
map; the `qa-reviewer` specified the call shape its acceptance test asserts. Reconciled (a
**C-15 sweep-back**: the superseded name `mapper/open_external.py` appears nowhere else and is
retired here):

> **LLR-N02.4 — After:** *"Opening **shall** dispatch through `mapper/osopen.py`, which **shall**
> expose `open_external(target: str, kind: str) -> str`, **shall not** use a shell, and **shall**
> accept only the `url` and `file` kinds."*

**A8 · AT roster reconciled to the acceptance design, plus two gaps it did not cover.**
The authoritative roster is `01b-acceptance-design.md`. Two requirements had no `AT` in it and now
do — recorded here rather than left to be discovered at Phase 4 (this is the **C-21** re-cut: the
increment plan is re-derived below because the AT set changed).

> **New — `AT-N03e`** gates LLR-N03.5 (visible keybar truncation): when the keybar's content
> exceeds its width, the rendered bar shows a marker naming the hidden count and the key that
> reveals the rest. Owning increment: **Inc-3**.
> **New — `AT-N04c`** gates the exhaustion branch of LLR-N04.3: on a map with no missing required
> field, the worklist reports exhaustion and does not cycle. Owning increment: **Inc-5**.

**A9 · One acceptance is downgraded from `test` to `inspection`, in writing.**
The `qa-reviewer` judged the final hop of US-N02 — the operating system actually opening the
application — to have no honest black-box oracle short of launching a real program, and declined to
invent one. That judgement is accepted.

> **MAN-01.** The hop from `open_external(...)` to the OS handler is verified by **inspection**,
> not by test. `AT-N02b` gates everything up to and including the call to the seam, with the
> launcher injected. **A green `AT-N02b` is explicitly NOT sign-off for MAN-01**, and the Phase-4
> validation artifact must say so rather than counting it as covered.

#### Re-cut forced by Amendment 1 (C-21)

Adding `AT-N03e` and `AT-N04c`, and adding `mapper/model.py` to the story of "one owner for missing
fields" (A4), makes the Phase-0 increment cut stale. Re-derived:

| Inc | Story | Source files | Count | Owns these ATs |
|---|---|---|---|---|
| 1 | US-N03 | `keymap.py`, `screens/palette.py`, `screens/help.py`, `app.py` | ⚠ 4 | `AT-N03a`, `AT-N03b`, `AT-N03c`, `AT-N03d` |
| 2 | US-N01 | `widgets/inspector.py` (new), `model.py`, `app.py`, `views/layered.py` | ⚠ 4 | `AT-N01a`, `AT-N01b`, `AT-N01c`, `AT-N01d`, `AT-N01e` |
| 3 | «taller» rail + chrome | `widgets/rail.py` (new), `widgets/chrome.py`, `app.py` | 3 | `AT-N03e` |
| 4 | US-N02 | `osopen.py` (new), `widgets/inspector.py`, `app.py` | 3 | `AT-N02a`, `AT-N02b`, `AT-N02c`, `AT-N02d` |
| 5 | US-N04 | `screens/coverage.py`, `widgets/inspector.py`, `app.py` | 3 | `AT-N04a`, `AT-N04b`, `AT-N04c` |
| 6 | US-N05 | `app.py` | 1 | `AT-N05a`, `AT-N05b`, `AT-N05c`, `AT-N05d`, `AT-N05e` |

`chrome.py` moves from Inc-2 to Inc-3 so that Inc-2 can absorb `model.py` without exceeding the
four-source-file budget. **Strictly serial** — the ARQ measured `modules(A) ∩ modules(B) ⊇ {app}`
for all 15 pairs, and increments 2, 4 and 5 additionally collide on the *file*
`widgets/inspector.py`, which is an ordering dependency no re-cut can remove.

---

#### Amendment 2 — 2026-08-25, folded from the PDR `security-reviewer` and `ux-reviewer` lenses

Both lenses returned **`approved with conditions`**. Every condition below was produced by an
**executed** probe, not by reasoning, and each is individually dischargeable.

##### Security conditions (2 blockers, 6 majors)

**S-B1 · `kind == "file"` currently launches anything on disk.** *Measured:* a `..` traversal target
**launched** `C:\Users\jjgh8\.gitconfig`; `calc.exe` and `powershell.exe` **launched**.
`os.startfile.__doc__` — *"acts like double-clicking the file in Explorer"*. The confinement the
module map mandates was structurally absent because the proposed signature had no `workspace` to
put it in.

> **New — LLR-N02.6.** *"`mapper/osopen.py` **shall** expose
> `open_external(kind: str, target: str, *, workspace: Path, launcher=None) -> str`, taking kind and
> target as plain strings, and **shall not** import any module from the `mapper` package."*
> **New — LLR-N02.7.** *"For `kind == "file"` the module **shall** resolve the target with
> `Path(target).resolve()` and **shall** refuse any target for which
> `resolved.is_relative_to(workspace.resolve())` is false, **before** any launcher is called.
> Refusal **shall** apply irrespective of whether the target exists; **existence shall not be
> treated as an authorisation**."*
> **New — LLR-N02.8.** *"The module **shall** refuse, without calling the launcher, any target that
> is not a non-empty `str`, and **shall not** raise for any input reachable from a
> `yaml.safe_load` of `_nodos.yml`."*
> **New — LLR-N02.9.** *"Every refusal **shall** be reported to the operator as a visible
> non-fatal message; a dropped return value **shall not** be a silent no-op."*
> **Supersedes** LLR-N02.4's signature (`open_attachment(att: Attachment, …)`), which forced
> `osopen → mapper.model`, a dependency the module map bans twice (finding F-M1).

**S-B2 · Terminal control characters reach the terminal; C-17 covers markup only.** *Measured:*
`raw ANSI reaches the compositor segment stream: True`; Rich emitted
`'acta\x1b[6A\x1b[40Dmapper  guardado ✓'` and an OSC-52 clipboard-write sequence verbatim. Markup
escaping does nothing about either.

> **New — LLR-N01.10.** *"Every value the inspector renders that originates in `_nodos.yml` or the
> `.mmd` source **shall** pass through one coercion helper that converts non-`str` to `str` and
> replaces every C0/C1 control character other than `\n` and `\t` with U+FFFD, before it reaches any
> renderable or an `Input.value`."*
> **New — LLR-N01.11.** *"No inspector code path **shall** pass a file-derived `str` to a
> markup-parsing sink — `Static.update(str)`, `Label(str)`, `Text.from_markup`, `Console.print(str)`."*

**S-M3 · The file-derived inventory is larger than the design listed.** It also includes
`SchemaField.label`, `Ficha.state`, `Ficha.meta`, `Attachment.path` and `node.id` — and LLR-N01.2
deliberately routes schema *labels* into a new render site. LLR-N01.10 is therefore written over
"every value originating in the sidecar", not over an enumerated list.

**S-M4 · URL target/display mismatch.** The inspector shows `caption` while the launcher opens
`path`; `user:pass@evil…`, `example.com@evil…`, a Cyrillic homograph and a U+202E override all
**launched**.

> **New — LLR-N02.10.** *"The inspector **shall** display the target that would actually be opened,
> not only its caption."*

**S-M5 · A malformed sidecar denies the whole map.** A node missing `path:` raises `KeyError` from
`MapStore.load`; `path: 12345` raises `AttributeError` from inside a function contracted to return
a status word. Closed by LLR-N02.8 on the `osopen` side; the `store.py:193` half is recorded as a
**carry**, not fixed here — it is outside this batch's file budget and is not a new defect.

**S-M6 · Oracle conflict, reconciled.** `docs/ARCHITECTURE.md` §1 listed the allowlist as
`http`/`https`/**`file`**; this batch narrows `url` to `http`/`https` and routes local files through
`kind == "file"`. That is a narrowing — the safe direction — but the map and the design must not
disagree in writing on the control the batch is gated on. **`docs/ARCHITECTURE.md` is amended to
match.**

**Explicitly recorded as NOT a finding:** the nine `Ds*` components are clean. `DsChip`,
`DsTextField` and `DsSegmented` all build through the `Text(...)` constructor, which does not parse
markup — `DsChip(label="[bold red on white]OWNED[/]").render()` yields
`.plain=' [bold red on white]OWNED[/] '`, `.spans=[]`. No component interpolates a caller string
into a markup-parsed path. Reusing them is safe.

**A fixture correction that matters more than it looks.** An unbalanced **opening** bracket does
*not* raise; an unmatched **closing** tag (`Static.update('[/bold]saldo')`) raises `MarkupError`.
The PDR's hostile fixture contained only the open case, so it would have passed while the crashing
case shipped. `AT-N01e`'s fixture **shall** contain both.

##### UX conditions (4 blockers, 5 majors)

**U-B1 · There is no focus signal, and blue currently marks three dead things.** *Measured:* with
focus in an inspector `Input`, the screen paints **28 cells of `#1783ff` across 3 rows** — canvas
selection, `DsSegmented` active option, selected `DsChip` — **none of which is the focused widget**.
`DsChip` focused and `DsChip` selected render **byte-identically** (`components.py:418` is a single
`if state == "focused" or self.selected` branch), so "which attachment does `↵` open" cannot be
answered from the screen.

This batch has no requirement covering focus at all. Adding one:

> **New — HLR-N06.** *"When `MapScreen` presents more than one interactive region, the system
> **shall** make the region that holds keyboard focus distinguishable from the regions that do not,
> and **shall** name the focused region in words on the hint line."*
> **LLR-N06.1.** *"The live region **shall** be marked by its container's background step —
> darkside's own depth mechanism — because CON-4 reserves borders for modals."*
> **LLR-N06.2.** *"A selection inside a region that does not hold focus **shall** render in `STEP`,
> not in `ACCENT`, so that at most one ACCENT run is painted on screen at a time."* *(This is the
> assertable invariant the pilot checks.)*
> **LLR-N06.3.** *"`DsChip` **shall** render focused and selected distinguishably."*

**U-B2 · `escape` while typing pops the whole map and discards the text.** *Measured against the
shipped app:* after `/`, typing `acta`, then `ESC` → `screen stack = ['Screen', 'HomeScreen']`; the
text is gone. A screen-level `escape` binding fires even with an `Input` focused, because Textual's
`Input` neither claims `escape` nor blurs on it.

> **New — LLR-N06.4.** *"A focused edit field **shall** claim `escape` at the widget level: the
> first `escape` **shall** leave the field, keeping the typed value, and return focus to the canvas;
> only a subsequent `escape`, with no field focused, **shall** leave the map."*
> *Verified fix:* a widget-level binding produced `LOG=['leave_field']`, focus moved to the canvas
> and `value kept = 'acta'`.

**U-B3 · A screen-level `tab` binding disables focus traversal entirely** — 9 presses produced 0
focus moves. The old `KEYMAP` bound `tab → vista previa` and the prototype draws the worklist key as
`⇥ ir`. Either the inspector becomes keyboard-unreachable or the worklist key is dead.

> **New — LLR-N06.5.** *"No screen **shall** bind `tab`; `tab` belongs to focus traversal. The
> worklist action **shall** use a key that is not `tab`."*
> **Discharged in Inc-1 by construction:** the rewritten seat contains no `tab` binding. A unit test
> asserts `tab` is absent from `KEYMAP`, so it cannot be reintroduced silently.

**U-B4 · Committing a field edit pushes no undo snapshot.** `_push_snapshot` is called only at
`app.py:1387`, `:1468` and `:1512` — all structural mutations. So `u` after an edit restores an
older structural snapshot and **destroys the edit**.

> **New — LLR-N05.6.** *"Committing an inspector edit **shall** push an undo snapshot before
> mutating the ficha, so that `u` reverts the edit and not an unrelated earlier structural change."*

**U-M1 · The keybar truncation marker does not exist in code.** `darkside.py:122` emits a bare `…`;
the `… +6  ? todas` in the prototype is hand-drawn. `KeyBar` renders at a hard-coded width of 118,
ignoring its real width — the bar measures 216 cells and shows **9 of 17** bindings. **`m cobertura`,
the entry point to the primary flow, is currently cut off.**

> **LLR-N03.5 — After:** *"`KeyBar` **shall** render at its measured width, and when its content
> exceeds that width it **shall** end with a marker naming the number of bindings hidden and the key
> that reveals them."* Gated by `AT-N03e`.

**U-M2 · Density: 58 columns supports 3 leaves, and the failure is silent.** Derivation: the legacy
schema has 5 fields; the coverage-letters row advances `xx += 3` per field, so a card needs
`card_w ≥ 15`. Solving `n*18 - 3 ≤ w - 2` at the canvas width left by a 24-column rail and a
36-column inspector (58) gives **3 leaves**; 4 leaves need a 131-column terminal. At an 80-column
terminal the canvas measures **20 cells**; at 60, **1 cell**. Beyond 3 leaves the letters row is
clipped mid-field, so **a present field and a clipped field look identical** — the canvas silently
misreports coverage, which is precisely what this batch exists to make trustworthy.

> **New — LLR-N06.6.** *"The rail and the inspector **shall** each be collapsible by a key binding,
> and **shall** collapse automatically when the terminal is too narrow to leave the canvas a usable
> width."*
> **Scope ruling (recorded):** this is the *minimal* discharge — two toggles and a width threshold.
> It is **not** batch 2's pan/fold/minimap work, which stays out.

**U-M3 · Three contradictory commit protocols** — the PDR says `↵`/blur, the prototype draws
`ctrl+s guardar · esc descartar`, and the old `KEYMAP` had `ctrl+s`. **Ruling: `↵`/blur commits**
(LLR-N01.4 as amended), and the inspector footer is corrected to read `esc` = *salir del campo*, not
*descartar* — the verb in the prototype describes behaviour the amended LLR-N06.4 no longer has.

**U-M5 · `CoverageScreen`'s "todo completo" empty state is a selectable row** that `↵` dismisses in
silence. Folded into `AT-N04c`, which already gates the exhaustion branch.

##### What these amendments do to the plan

- **HLR-N06 is new** and owns `AT-N06a` (focus signal / one-ACCENT-run invariant), `AT-N06b`
  (`escape` leaves the field, keeps the value), `AT-N06c` (`tab` traverses; no screen binds it),
  `AT-N06d` (rail and inspector collapse). Owning increments: Inc-2 (`AT-N06b`), Inc-3
  (`AT-N06a`, `AT-N06d`), Inc-1 (`AT-N06c`).
- Two majors are recorded as **carries, not fixed here**, because they fall outside the batch's file
  budget and are not new defects: `MapStore.load`'s `KeyError` on a malformed sidecar (S-M5), and
  the `screens → app` back-edge at `mapper/screens/factory.py:343` (ARQ A-7). Fixing the latter
  silently was explicitly rejected.
- `docs/ARCHITECTURE.md` §1 is amended for the allowlist narrowing (S-M6).
