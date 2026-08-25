# Prototype notes — ui_components (the darkside component sheet)

**Question.** The operator asked for "more elements" on the views and whether
external design skills were needed. Answer: no — the operative source is
`/tui-design`'s own [COMPONENTS.md]: a language is a component library, and the
interaction layer (switches, sliders, tabs, spinners) is where a language
actually differs. This round renders the darkside component sheet and wires
the new components into three real views.

**Location.** `prototypes/ui_components/out/index.html` — four real renders.
Regenerate: `python prototypes/ui_components/generate.py`. Verify:
`node prototypes/ui_components/verify.cjs` (patchright, screenshots + page
errors; the browser-skill `--script` path fails on Windows drive schemes).

## The sheet (C1 — the settings-screen canary)

Every component in three states: **default / focused / disabled**. The state
matrix is the law: a component that cannot render its three states is not part
of the language.

| component | darkside mechanism |
|---|---|
| switch | word flip `on`/`off` — the active word wears the blue block |
| stepper | `- value +` — the ± carry the affordance (blue; blocks when focused) |
| slider | track `─` STEP, fill `━` INK, handle `▮` a blue block |
| segmented | the tab strip's little sibling — active option is the blue block |
| progress | `step_meter` — contiguous ▰▱ blocks, INK on STEP |
| spinner | braille cycle ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ in blue — the frame IS the motion |
| text field | cursor `▌` blue; placeholder sinks to STEP |
| pagination | `‹ n/m ›` — number INK, arrows blue |
| tag chip | ` name ` on STEP; focused wears the blue block |

State laws that held across all nine:

- **Focus is the solid block.** No outlines, no dashed boxes — the affordance
  inverts to black-on-blue. Where a block makes no sense mid-control (slider
  handle, stepper keys), the *interactive cell* wears the block.
- **Disabled sinks to STEP** (`#262626`) — present, not operable, nearly
  silent. It must never be confused with the dim tier (MUT), which is
  readable chrome.
- **Blue stays on interactivity only.** Data (sparkline bars, KPI values,
  node counts) never wears it.

## The three applied views

- **C2 · home** — KPI tiles (value bold INK, label MUT, delta MUT, WARN for
  severity) on STEP grounds, an activity sparkline (14d, recency gradient
  STEP→MUT→INK), the resume row, and the recents rail with kind chips.
- **C3 · map** — accordion disclosure `▾ 3` / `▸ 5` with the folded count
  declared (blue gutter glyphs, VS Code-gutter style), pagination `‹ 1/2 ›`
  under the tree, and a save toast: a bottom strip on PANEL, `guardado` bold
  INK + detail MUT.
- **C4 · repo plug** — the fetch state: skeleton bars (STEP blocks holding
  the shape of coming content) + the braille spinner with the verb it is
  doing (`leyendo refs del repo…`).

## What verification caught (and the rulings)

1. **`✓` did not survive the font.** The toast's check rendered as `v` in the
   captured SVG. Glyph coverage is unverifiable (CEILINGS.md), so the toast
   carries the word (`guardado`, bold INK) instead of a check glyph. Ruling:
   **status words, not status glyphs**, unless the glyph is in the language's
   own verified set (blocks, arrows ‹›, disclosure ▸▾, braille).
2. **STEP-on-PANEL is too dim for anything meant to be read.** Timestamps and
   KPI deltas at `#262626` on `#121212` were illegible in the capture. Ruling:
   **MUT is the floor for readable chrome**; STEP is for tracks, borders,
   placeholders, disabled — things you locate, not things you read.
3. **A `Table.grid` prefix column must be sized to the prefix** (~10 cells
   for tree guides), not to the row — an over-wide first column squeezes the
   value column into ellipsized fragments.

## Round 2 — components matched to PURPOSE (desk / taskboard / s19 / gbl)

The operator's verdict on round 1: the elements exist but are not used for
the purposes the views pursue. Four reference repos were studied (swarm of
explore agents) and their lessons applied:

**H2 · home is GLANCE posture — one hero, not four equal tiles.** The hero is
the loudest signal (taskboard's aperture law): the documentation debt of the
tree being worked, as a **drawn number** (3×5 block digits — it renders, it
does not label), with the severity cap `▲ 3 vencen hoy` next to it. The
activity sparkline was demoted to the dim tier beside it — a chart must never
outrank the metric it serves (taskboard measured this). The round-1 KPI tile
row collapsed into ONE inline distribution line (s19's microbar):
`con acta 34 ███████░░░ · sin acta 12 ██░░ · cobertura 74 %`.

**M2 · map is OPERATED+READ — collapsed branches still answer** (gbl's
BandHeader): `▸ frontend  5 nodos · 2 sin acta`, the count in WARN because
debt is the reason the tree exists. A one-row **coverage minimap** (s19's
memstrip) reads the whole tree before any node is opened: one glyph per
branch, `╱` for sin datos — a separator, not a count.

**R2 · repo is OPERATED — one shared time axis.** Branches and releases are
events on the same 30-day axis (gbl: what aligns vertically happened at the
same time), the today rule `╎` sits in the same column on every row, and the
source wears an honesty badge (`github` chip — gbl's [REAL]/[VIZ] law:
estimated vs real is always declared).

**The ruling round 2 added to the sheet:** STEP (`#262626`) is invisible on
the GROUND — it only works as a track over PANEL. On black, the dim floor for
glyph tracks and rules is WORDMARK (`#3a3a3a`), and for words it is MUT.
Three legends and the today rule were invisible until this was fixed.
