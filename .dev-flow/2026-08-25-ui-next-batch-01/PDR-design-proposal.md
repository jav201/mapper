# PDR — Preliminary Design Review · `2026-08-25-ui-next-batch-01`

> **Home:** vault + Drive (carried at `/dev-flow-sync`); sealed on approval and cited by id from the
> repo. What decides code — the frozen contracts in §3 — is reflected in `01-requirements.md` and
> `docs/ARCHITECTURE.md`, which are versioned beside the code.

---

## 0 · Forward-applicability table (C-49)

Everything this PDR produces must be named as a later activity's input. **A row with an empty
consumer column means delete the output.**

| Output | Consumed by |
|---|---|
| D1 `KeyBinding` schema + scope model | Inc-1 (`mapper/keymap.py`), `AT-N03a`, `AT-N03c` |
| D2 Inspector widget contract (rows, focus order, commit protocol) | Inc-2, Inc-4, Inc-5; `AT-N01a`–`AT-N01e`, `AT-N04a` |
| D3 `osopen` contract (allowed kinds, refused schemes, no shell) | Inc-4; `AT-N02c`, `AT-N02d`; the `security-reviewer` pass |
| D4 Undo relocation (`App`-held, keyed by `map_id`) | Inc-6; `AT-N05c` |
| D5 `MapScreen` layout grid + CSS ids | Inc-2, Inc-3; every pilot that queries by id |
| D6 Frozen-interface list for this batch | every increment gate; the DDR |
| D7 Enablers: the `_schema_map` fixture + the injected launcher | every AT in `tests/test_inspector.py`, `tests/test_attachments.py` |

No output of this PDR is unconsumed.

---

## 1 · Design characteristics

### D1 · The keymap becomes a real single source

Today `KeyBinding(key, action, group)` stores Spanish prose in `action`, which is why
`MapperApp.action_palette`'s `getattr(screen, f"action_{action}")` resolves nothing (0/33, P-1).
The fix separates the **dispatched name** from the **human label** and adds a **scope**:

```python
@dataclass(frozen=True, slots=True)
class KeyBinding:
    key: str      # Textual key name: "j", "ctrl+p", "slash", "enter"
    action: str   # action method STEM: "next_sibling"  -> action_next_sibling
    label: str    # Spanish prose shown to the operator: "siguiente"
    group: str    # display grouping: nav | node | view | edit | app | doors
    scope: str    # which screen owns it: "map" | "home" | "repo" | "app"
```

- `bindings_for(scope)` returns every binding whose scope is `scope` **or `"app"`** (app-scope
  bindings are available everywhere).
- `textual_bindings(scope)` returns the `(key, action, label)` triples a screen assigns to
  `BINDINGS`, so a screen's bindings and the palette's entries cannot drift apart — they are the
  same list.
- `palette_items(query, scope)` and the help overlay both filter by the **active** screen's scope,
  which is what makes "help shows exactly the keys that work" true rather than aspirational.

**Why scope rather than one global list:** `q` means "quit" on `HomeScreen` and "home" on
`MapScreen`; a single flat list would have to lie about one of them. Alternative rejected: keep the
flat list and let each screen filter by group — groups are a *display* concern and already overlap
(`f` appears twice today, once under `doors` and once under `view`).

**Duplicate-key rule:** two bindings may share a key only if their scopes differ. A unit test
asserts this, so the `f` collision that exists today cannot be re-introduced silently.

### D2 · The inspector

A `Vertical` panel docked right on `MapScreen`, id `#map-inspector`, width 36.

- **Rows.** `title`, `state`, then one row per `SchemaField` in `graph.schema` order, then `notes`,
  then `attachments`, then the coverage meter. Every schema row's label is
  `SchemaField.label` (P-7 / LLR-N01.2).
- **Widgets.** Reuse the existing `Ds*` components (P-4 — this batch is their first production
  consumer): `DsSegmented` for `state` over `["ok", "riesgo", "tarde", "bloq"]`; `DsProgress` for
  the coverage meter; `DsChip` for each attachment. Editable values are Textual `Input`s, because
  premise **P-11** measured that a focused `Input` consumes single-letter keys and therefore
  cannot trigger the map's `j`/`k`/`a`/`x` bindings. `DsTextField` is a *Static lookalike* with no
  key handling — using it for a real edit would be a prototype-fidelity failure (C-16).
- **Commit protocol.** `Input.Submitted` (or blur) → mutate the ficha → `MapStore.save` → refresh.
  One save per commit (LLR-N01.4). No autosave per keystroke.
- **Required-empty flagging.** A required field with an empty value renders its label in
  `darkside.ALERT`; the coverage meter counts it.
- **Markup safety (C-17).** Every line carrying file-derived text is built with `Text.assemble` and
  explicit styles, or passed through `rich.markup.escape`. This is the same discipline the existing
  code already applies at `app.py:1258` and `darkside.py:220`; the inspector must not regress it,
  because its inputs (titles, notes, field values, attachment captions) all come from `_nodos.yml`.

### D3 · `mapper/osopen.py`

```python
def open_attachment(att: Attachment, *, launcher=None) -> str:
    """Hand an attachment to the OS default application. Returns a status word."""
```

- Accepts only `kind in {"url", "file"}`; anything else is refused and reported.
- For `url`: the scheme must be `http` or `https`. `file:`, `javascript:`, `data:`, UNC paths and
  schemeless strings are **refused**, not launched (LLR-N02.5).
- For `file`: the path is resolved and must exist; it is passed as a **single argument** to
  `os.startfile` (Windows) or `subprocess.run(["xdg-open"|"open", path])` — **never** through a
  shell, and never string-interpolated into a command line.
- `launcher` is an injection seam so `AT-N02c` can assert the call without launching anything on
  the test machine. It is the **enabler** D7 names.

The boundary crossing is already declared in `docs/ARCHITECTURE.md` §1 ("OS default apps — URL/file
open requests when activating attachments"); this batch is the first code to actually use it, so
the `security-reviewer` gates it before Inc-4 merges.

### D4 · Undo moves to the App

`MapScreen._snapshots` (P-6) becomes `MapperApp.undo_stacks: dict[str, list[bytes]]`, keyed by
`map_id`. `MapScreen._push_snapshot` / `_pop_snapshot` read and write
`self.app.undo_stacks.setdefault(self.map_id, [])`. Constructing a new `MapScreen` for the same
map therefore inherits the history instead of discarding it (LLR-N05.3).

Per-map rather than one global stack (risk R6): a single stack would let an undo taken in map B
restore a snapshot of map A, which is a data-loss bug dressed as a feature.

### D5 · `MapScreen` layout

```
TabStrip                      (top, full width)
Horizontal #map-body
  ├─ #map-rail        width 24   (Inc-3)
  ├─ #map-canvas      1fr        (existing LayeredRenderer output, unchanged)
  └─ #map-inspector   width 36   (Inc-2)
#map-toast · HintLine · KeyBar  (bottom, full width)
```

`#map-ficha` / `#map-ficha-box` are **deleted** (P-3), and `LayeredRenderer`'s own ficha strip is
deleted with them (D4 of `PLAN.md`, premise P-12 shows nothing asserts it). The canvas keeps
exactly the same `render(...)` call — no kwarg is added, so `IRenderer.render` stays frozen.

---

## 2 · Proposed test cases (the other half of what is under review)

Layer 0 (unit, complexity ≥ 3 or a boundary transform), Layer A (`TC`, white-box over the LLR),
Layer B (`AT`, black-box over the story). The `AT` roster with its RED mutations is specified in
`01b-acceptance-design.md`; this section records the **enablers** those tests need:

- `_schema_map(tmp_path)` — a `MapStore` seeded with a schema of ≥2 required fields and ≥1
  optional, and a tree of ≥3 nodes with mixed coverage, so `AT-N04b` can advance between *different*
  nodes (C-10: a non-default step) and `AT-N01c` can distinguish a label from a key.
- `RecordingLauncher` — captures `(kind, target)` without launching, for `AT-N02c`.
- A hostile-text fixture: a title containing `[bold]`, notes containing an unbalanced `[`, and an
  attachment caption containing an ANSI escape — for `AT-N01e`.

---

## 3 · Frozen for this batch (D6)

`Graph` · `Canvas` · `MapStore.load/save/reindex` · **`IRenderer.render`** · `SearchIndex.query` ·
`mermaid.parse/dump` · `GitHubConnector.fetch` · `save_svg`/`save_png`.

Any increment that needs one of these to change stops and returns to the operator — that is
trigger A3, and it is out of this batch's authorization.

---

## 4 · Verdict

*(Filled by the reviewers: `architect` · `qa-reviewer` · `ux-reviewer` · `security-reviewer`.)*
