# HANDOFF — mapper × darkside implementation (next agent)

**For:** the agent implementing the mapper UI redesign. **Status:** the batch
`2026-08-18-batch-01` is at its Phase-0 gate with **19 user stories READY**
(`01-requirements.md`); the darkside directive is batch design decision D-1
(§6.2). Resume by running `/dev-flow` from this root — `state.json` says
`awaiting-gate`, present the gate, and on the operator's `approve` derive
HLR/LLR. Kickoff authorization (autonomous + merge authorized, decision
recording confirmed) is inherited from `state.json.standing_authorization`.

This document is the DESIGN-SYSTEM CONTRACT: everything the implementation
must carry so the app is recognizably darkside, including the distinctive
elements the prototype rounds did **not** show yet.

## 1. Reference renders (look at these first)

- `prototypes/ui_darkside/out/index.html` — six screens (home, home-empty,
  map, factory, editor, palette). The approved direction.
- `prototypes/ui_fidelity/out/index.html` — the chrome-system round the
  darkside round supersedes (V1 boxed chrome is ANTI-darkside: borders are
  forbidden; V3's tab strip IS the native darkside idiom and survives).
- `taskboard/taskboard/themes.py` → the `darkside` entry — the canonical
  token source this contract is ported from, with its doctrine comments.
- `prototypes/ui_darkside/NOTES.md` — this round's notes.

## 2. The six laws (each with its implementation consequence)

1. **Achromatic + KMBlue only on interactivity.** `#1783ff` appears on
   exactly: the active tab · key glyphs on the key bar and in hints · the
   solid selected row · the current step chip · a switch/knob when one
   exists · `{{tags}}` in factory (they are the editable affordance).
   NOTHING passive wears blue — a review finding is "blue on passive data".
2. **Depth is a background grey-step, never a border.** Grouping =
   `#000000 → #121212 → #262626`. **Zero borders anywhere** — if a Panel has
   a border, it wears the background's own colour (invisible).
3. **Lowercase register.** All chrome text lowercase; node titles and
   document content keep user case.
4. **Date-driven moon doodle.** Computed from the system date (synodic
   29.530588853 d from the 2000-01-06 new moon), shown beside the recessive
   wordmark. Never hardcoded.
5. **Semantic severity only.** `#ffd230` warn (coverage gap, due-soon),
   `#ff4f42` alert (SIN ACTA, CI fail, overdue). A calm state renders
   **ink** — there is no green/ok hue anywhere.
6. **Selection is a SOLID block.** Blue block, black text — never an outline.

## 3. Tokens (the whole set)

| token | hex | may be used for |
|---|---|---|
| ground | `#000000` | app background |
| panel | `#121212` | content-group depth (grey-step 1) |
| step | `#262626` | chips/badges depth (grey-step 2), rails, step-meter track |
| mut | `#737373` | labels, metas, quiet text |
| ink | `#f5f5f5` | content, calm states (calm = ink, never green) |
| accent | `#1783ff` | interactive affordances ONLY (law 1) |
| warn | `#ffd230` | semantic warn only |
| alert | `#ff4f42` | semantic alert only |
| wordmark | `#3a3a3a` | the recessive identity mark |

## 4. The distinctive elements the prototypes did NOT show — carry them

1. **THE RAIL (darkside's layout).** Every list/tree view carries a PASSIVE
   left rail (`#262626`, never blue): in the map view it is the structure
   spine the node stack hangs from (the tree's vertical guides live IN the
   rail, dimmed); in home, the recents' `▐` markers form the rail. The rail
   is structure, not data — it never interacts.
2. **THE STEP METER (`meter="step"`).** Any quantity renders as grey-step
   blocks, not digits where a meter reads better: coverage `▰▰▰▰▱` (4/5) in
   ink blocks on a step track — missing steps in `#262626`, never red unless
   the coverage itself is the alert condition (then `#ffd230` on the missing
   steps). Doc-counts, ahead/behind and step chips follow the same idiom:
   current step = blue block, future steps = `#262626`, past steps = ink.
3. **MOTION (`tempo=300, easing=in_out_cubic`).** Every transition — tab
   switch, selection move, palette open/close, step advance — animates at
   **300 ms in_out_cubic**: a slow breath, never a snap. No fade longer, no
   cut shorter. (Textual: `animate` with easing `in_out_cubic`.)
4. **THE RECESSIVE WORDMARK.** `mapper` in `#3a3a3a` beside the moon doodle,
   top-right of the tab strip — identity at ~42% opacity, deliberately
   quiet. On the HOME (and only there) it may render large as a watermark
   behind the content, same `#3a3a3a`, as the app's identity moment.
5. **THE TAB STRIP as the one interactive affordance up top.** Doors =
   tabs; active tab = blue block/black text; inactive = `#737373` on
   `#262626`. The strip also owns the mode badge when inside a mode
   (`edit`, `read-only` — as grey-step chips, blue only if the badge itself
   is a toggle).

## 5. Screen inventory (what each must carry)

- **Home**: tab strip + moon wordmark · resume row (blue chip) · recents on
  the step panel with the rail markers · recents columns: name / kind chip
  (grey-step) / nodos / docs · EMPTY STATE: four doors with keys lit + the
  first-step hint (see `ds-home-empty.svg`).
- **Map view**: breadcrumb lowercase with current node in ink · the tree
  inside the rail · selected node as solid blue block · SIN ACTA in alert ·
  ficha strip on the step panel with coverage as STEP METER · hint line +
  grouped keybar (keys blue, labels grey).
- **Factory**: step chips in step-meter idiom · process tree with selected
  node solid · preview panel (step depth) with resolved values in ink and
  missing values in alert · tags table (tags blue = editable) with
  local/inherited columns.
- **Editor**: source on step depth, `{{tags}}` highlighted blue on
  `#262626`, `detected:` line, edit keybar.
- **Palette (`ctrl+p`)**: grouped commands from the ONE keymap seat, fuzzy by
  name+key, first match solid, query row in blue. **Help (`?`)**: the same
  seat's full list. The keymap seat feeds keybar + palette + help — three
  readers, one list, no drift (taskboard keybar contract).
- **Repo view** (not prototyped yet — build on the map view's chrome): main
  lane + release ◆ milestones (ink, blue only if selectable), branch lanes
  with fork/merge connectors in the rail, ahead/behind as step chips, CI as
  warn/alert/in-progress(idle grey) — never green.

## 6. Implementation notes (landmines already paid)

- **rich 15 law:** `Console(width=..., height=...)` — `Console.size` honours
  `_width` ONLY when `_height` is also set; without it every >80-col line
  wraps in exported SVGs.
- **Badge stretch:** never build a mode badge with
  `Table.grid(expand=True)` + `on`-colour — it stretches to the cell width.
  Compose header rows as a single `Text`.
- **Panel without visible border:** `Panel(..., border_style=PANEL,
  style=f"on {PANEL}")` (rich's `box=None` raises).
- Escape all user text (`rich.markup.escape`); width-1 glyphs only; capture
  with `Console(record=True, file=StringIO())`.
- Tests: `python -m pytest tests/ -q` (16 passing at handoff — keep them
  green; new views get their own test modules).
- No real data in committed artifacts: synthetic fixtures only.

## 7. Functionality folded into the batch (already READY in
`01-requirements.md`)

US-015 empty states · US-016 `ctrl+p` palette · US-017 `?` help ·
US-018 resume-last row · US-019 `u` undo (snapshot stack like taskboard's).

## 8. Verdict placeholders (do not delete — fill at review)

- Rail applied to which views: …
- Step meter replacing which digits: …
- Motion timings verified on hardware: …
