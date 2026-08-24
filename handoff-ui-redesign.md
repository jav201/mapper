# Handoff — mapper UI redesign

**Session:** `wd_kimi_089f1915c010` / `session_ceba8bf4-b51e-479b-99e7-62c870db2ae0`  
**Repo:** `C:/Users/jjgh8/Github/mapper` → `https://github.com/jav201/mapper`  
**Last commit:** `3af8488` (docs(proto): unified mapper UI architecture and prototypes)

## What this is
The operator wants to hand off the mapper UI redesign to a fresh Kimi session. The current prototypes were useful as a first pass, but the operator’s feedback is that they are still too simple: missing visual cues, clear separation of elements (Gestalt principles), and enough guidance for the user to understand the app and drive tasks intuitively.

The next session should treat this as a **proper TUI design job** using `/tui-design` and `/prototype`, and produce higher-fidelity, actionable prototypes before writing production code.

## State of the code
- `mapper/app.py` — main Textual app. `HomeScreen`, `MapScreen`, `ConstructScreen`.
- `mapper/model.py` — `Graph`, `Node`, `Ficha`, `Edge`, `Attachment`, `SchemaField`.
- `mapper/store.py` — persistence as `.mmd` + `_nodos.yml` + rebuildable SQLite index.
- `mapper/views/` — `layered.py`, `lane.py`, `outline.py`, `radial.py`.
- Last bugfix: `ConstructScreen` asks for a new map name and seeds a 3-node demo tree so `n` no longer feels frozen.
- Tests: `python -m pytest tests/ -q` → 16 passed.

## Existing prototypes (do not rebuild from scratch; iterate)
Two prototype sets already exist. Read them before designing:

- `prototypes/ui_redesign/out/index.html` — four structural directions (home, map view, focus board, document factory) as real terminal SVG renders.
- `prototypes/ui_unified/out/index.html` — unified-app proposal: four doors leading to one `MapScreen`, document inheritance model, factory mode, document editor.
- `prototypes/ui_unified/NOTES.md` — unified domain model, document inheritance rules, persistence plan, first increment scope.

## Operator feedback to address
The next prototypes must fix:

1. **Visual cues are missing.** Right now the screens look like flat text. Use focus states, hover hints, selection markers, empty-state guidance, and progress chips so the user always knows what is active and what is possible.
2. **Clear separation of elements (Gestalt).** Group related controls, use consistent proximity, align edges, and distinguish chrome from content. Avoid walls of equal-weight text.
3. **Task guidance.** Every screen should answer three questions at a glance: *Where am I? What can I do here? What is the next step?* Add breadcrumbs, contextual footer groups, inline hints, and onboarding empty states.
4. **Intuitive operation.** The four entry points (consult, plug repo, construct, document factory) must look like facets of one app, not separate tools. Use consistent headers, footers, keybindings, and a single command palette.

## Suggested next steps
1. Re-run `/tui-design` intake. Read the repo first, then confirm or refine the brief in `prototypes/ui_unified/NOTES.md`.
2. Produce **3–5 higher-fidelity UI variants** that address the operator’s feedback. Use `/prototype` and real terminal SVG renders (see `prototypes/ui_redesign/generate.py` and `prototypes/ui_unified/generate.py` for the capture pattern).
3. Pay special attention to:
   - **Home screen:** four doors + recent maps + clear kind badges + empty-state onboarding.
   - **Map view:** breadcrumb, selected-node highlight, ficha strip, document chip, context-sensitive footer.
   - **Document factory:** tag resolution preview, inheritance table, visual indication of which tags are local vs inherited vs unset.
   - **Help/palette discoverability:** `?` keymap screen and `ctrl+p` command palette groups.
4. Validate with the operator before implementing.
5. Once a direction wins, route implementation through `/dev-flow` with user stories and acceptance tests.

## Skills to load
- `/tui-design`
- `/prototype`
- `/html-visualizer` (if the operator wants an interactive/browser-readable comparison)

## Commands
- Run tests: `python -m pytest tests/ -q`
- Run app: `mapper [workspace]` or `python -m mapper.app [workspace]`
- Regenerate prototypes: `python prototypes/ui_redesign/generate.py` / `python prototypes/ui_unified/generate.py`

## Out of scope for the handoff receiver
Do not implement production code yet. The job is to raise the design fidelity and get operator approval on a unified, intuitive UI.
