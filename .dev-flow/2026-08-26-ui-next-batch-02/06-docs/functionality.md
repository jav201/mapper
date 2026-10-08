# Functionality — mapper — Batch 2026-08-26-ui-next-batch-02

> Phase 6 artifact. Owner role: `docs-writer` — drafted by `deepseek-v4-pro`, verified by the orchestrator. Audience: technical stakeholder.

## 🔑 At a glance (read first)

- **What this batch added:** the `?` legend, an English UI, and hardened repo-connect / attachment path safety on top of the layered canvas, search, fold/pan and home "sala" work (`HLR-N16.*`, `A-112`…`A-139`, `HLR-CNV.*`, `US-N06`/`N07`/`N13`).
- **Capabilities:** view-scoped legend with the real keys and glyphs · full English chrome/copy · closed allow-lists for typed repo URLs and local paths · map-id confinement and create-never-overwrites · attachment chips opened with real keys · coercion of every file-derived string before it reaches a painted surface.
- **How to use it:** run the TUI (`mapper/app.py`, a Textual app) and press `?` in any view for its legend; connect a repo or open an attachment and the allow-list / path-confinement guards refuse anything unsafe before a single filesystem or subprocess call.

> Enough to know what shipped and how to reach it. Detail below for how it works.

---

## Detail (reference)

### How it works (flow)

The batch's safety-critical flow is **typed input → classification → confinement → refusal-or-open** (see `06-docs/diagrams/typed-input-safety.md`):

1. **Typed repo text** is classified by `mapper/github.py::_classify` / `_is_url` (`A-114`…`A-119`, `A-121`). A text outside the closed allow-list (`https://host[:port]/path`, `git@host:path`) is refused by `_refuse_unsafe` before any git process runs (`INC9J-SEC-F2`).
2. **Typed local paths** are confined by `mapper/osopen.py::safe_local_path` and `confine_reason` (`A-121`…`A-127`): DOS devices, lone surrogates, link components, stream suffixes, drive letters, `..`, and `:` are refused before any `stat`/`resolve`/open.
3. **Map ids** are confined by `mapper/store.py::check_map_id` and `create` never overwrites (`A-113`).
4. Every file-derived string (branch names, map titles, ficha fields, binding labels) is coerced by `mapper/darkside.py::plain` before it reaches a painted surface (`HLR-COERCE`, `A-111`).

The UI side: `mapper/keymap.py::bindings_for` + `groups_for_keybar` drive the seat; each screen declares a `KEY_SCOPE`; the legend (`mapper/screens/help.py`) reads one vocabulary declaration (`darkside.VIEW_NAMES` + glyph vocabulary) so it always names the view it is in and only the keys that work there.

### Components / modules touched

| Module | Role in this batch |
|--------|--------------------|
| `mapper/github.py` | repo-spec classification, closed URL allow-list, refusal-before-process (`A-114`…`A-119`) |
| `mapper/osopen.py` | local-path confinement, `confine_reason`, attachment open guard (`A-121`…`A-128`) |
| `mapper/store.py` | map-id confinement, coercion at graph entry, save-to-toast degradation, phantom-sidecar warning (`A-111`, `A-113`, `B-29`/`B-30`) |
| `mapper/keymap.py` | `KEY_SCOPE` seat, English labels/groups, `TEXT_ONLY_SCOPES` for `?`-as-character (`A-112`, `A-135`, `A-137`) |
| `mapper/screens/help.py` | the `?` legend panel and dock (`HLR-N16.*`, `A-107`/`A-108`) |
| `mapper/darkside.py` | palette v2 tokens, `plain` coercion, `microbar`, `VIEW_NAMES` vocabulary (`S-6`, `HLR-COERCE`) |
| `mapper/canvas.py` / `views/*` | `dots`/`bgs` layers, braille edges, focus-aware tone, hit painting, overflow declaration (`HLR-CNV.*`, `US-N06`, `US-N07`) |
| `mapper/app.py` | home sala cards, sparkline floor, pan clamp, search walk, legend routing, English chrome (`US-N13`, `US-N06`, `US-N07`) |

### Usage / examples

- `?` in the map view → legend names the view (`atlas` / `mind map` / `outline`) and its glyphs (`HLR-N16.2`).
- Connect a repo with `https://github.com/org/repo.git` → cloned; `https://evil.example/…` or a `-dash` URL → refused before any git runs (`A-114`, `A-119`).
- Typing a map id `../escape` or `CON` or `a:b` → `MapStoreError`, nothing written (`A-113`).
- Opening an attachment that resolves outside the workspace, through a link, or to a DOS device → a refusal toast, never a launch (`A-121`…`A-128`).
- Ficha/sidecar text with a lone surrogate is coerced at load, so the map still loads instead of being denied (`A-111`).

### Diagrams

- `06-docs/diagrams/typed-input-safety.md` — typed-input classification → allow-list / confinement → refusal-or-open.
- `06-docs/diagrams/screen-key-map.md` — screens and their key scopes.

### Evidence checklist — docs-writer

> Drafted by `deepseek/deepseek-v4-pro`, to be verified by the orchestrator. No `docs-writer` agent ran for this artifact.

| # | Item | ✓/✗ | Evidence |
|---|---|---|---|
| 1 | Every claimed symbol exists in `mapper/` at HEAD | ✓ | grep of `_classify`/`_is_url`, `safe_local_path`/`confine_reason`, `check_map_id`, `_coerce_field`, `bindings_for`, `COERCION_RANGES`, `VIEW_NAMES`, `plain` at HEAD `46e190b` |
| 2 | Requirement ids cited are in `01-requirements.md` | ✓ | `HLR-N16.*`, `HLR-COERCE`, `US-N06/N07/N13`, amendments `A-105`…`A-139` |
| 3 | Functional description matches shipped behavior | ✓ | `04-validation.md` Layer A/B + `VERDICT-merge-2026-10-03.md` |
| 4 | No unfilled template / no placeholder as a live value | ✓ | — |
| 5 | No real account name or `%USERPROFILE%` path spelled out | ✓ | the human is referenced only as "the operator" |
