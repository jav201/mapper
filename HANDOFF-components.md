# HANDOFF — mapper: the darkside component sheet + purpose-built views (next agent)

**For:** the agent implementing the component layer and the round-2 view
redesigns. **Status:** the MED/LOW batch `2026-08-24-medlow-batch` is closed
(68 tests green, repo screen variant C shipped). This handoff is NEW scope —
open a fresh batch with `/dev-flow` from this root (suggested id:
`2026-08-24-components-batch`), or implement directly if the operator says so.
Kickoff authorization (autonomous + merge authorized, decisions recorded in
`state.json.decisions_log` + the batch `PLAN.md`) is inherited from
`state.json.standing_authorization`. Artefacts in English; UI strings in
Spanish (production register).

This document turns two prototype rounds into production work. The prototypes
are RENDERED and browser-verified — treat them as the visual spec, not as a
suggestion.

## 0. Read first

- `prototypes/ui_components/out/index.html` — 7 renders. C1 is the component
  sheet (the canary); C2-C4 are round 1 (superseded where round 2 differs);
  **H2/M2/R2 are the approved view designs.**
- `prototypes/ui_components/NOTES.md` — the component mechanisms, the state
  laws, and the rulings verification produced. Read it before writing code.
- `prototypes/ui_components/generate.py` — the reference implementation of
  every component (pure rich, importable patterns). Production code should be
  a port, not a reinvention.
- `mapper/darkside.py` — the token + chrome module already in production
  (tab strip, keybar, group box, hint line, moon, step meter, kind chip).
- `HANDOFF-darkside.md` — the six laws and the token table. They still bind;
  this handoff AMENDS §3 with one ruling (see §5).

## 1. What the study changed (the why, in one paragraph)

Four reference repos (`desk`, `taskboard`, `s19_app`, `guitar-bass-lab-tui`)
were studied. The headline lessons, already applied in the prototypes:

- **Each view has a posture, and the layout declares it** — home is GLANCED
  AT, map is OPERATED+READ, repo is OPERATED.
- **The hero renders the loudest signal; it never labels it** (taskboard's
  aperture law). Supporting charts sit in the dim tier so they cannot outrank
  the metric they serve.
- **A collapsed region still answers** (gbl's BandHeader): counts, not just a
  name.
- **A one-row minimap reads the whole before anything is opened** (s19's
  memstrip).
- **Events share one time axis** (gbl): what aligns vertically happened at
  the same time; the today rule is one shared column.
- **Sources wear honesty badges** (gbl's `[REAL]/[VIZ]`): `github` vs `local`.
- **Empty states name the key that resolves them** (taskboard); status words,
  not status glyphs (`✓` failed font coverage in the SVG capture — glyph
  coverage is unverifiable).

## 2. Part A — the component library (`mapper/widgets/components.py`, new)

Port the nine components from `generate.py` into production widgets (rich
`Text` renderers inside `Static`, following `mapper/widgets/chrome.py`'s
pattern). Each MUST render three states; the state matrix is the law:

| component | mechanism (darkside, not colour) |
|---|---|
| `DsSwitch` | word flip `on`/`off`; the active word wears the blue block |
| `DsStepper` | `- value +`; the ± carry the affordance (blocks when focused) |
| `DsSlider` | track `─`, fill `━` INK, handle `▮` blue block |
| `DsSegmented` | active option is the blue block; siblings MUT on STEP |
| `DsProgress` | `darkside.step_meter` — contiguous ▰▱, INK on STEP |
| `DsSpinner` | braille cycle ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏ in ACCENT; the frame IS the motion |
| `DsTextField` | cursor `▌` ACCENT; placeholder sinks to the dim tier |
| `DsPagination` | `‹ n/m ›` — number INK, arrows ACCENT |
| `DsChip` | ` name ` on STEP; focused wears the blue block |

State laws (C1 is the canary — build a settings surface dense in components
and review it first):

- **Focus is the solid block** (black-on-blue). No outlines, no dashed boxes.
  Where a block makes no sense mid-control, the interactive CELL wears it.
- **Disabled sinks to STEP** — present, not operable, nearly silent. Never
  confusable with MUT (readable chrome).
- **Blue stays on interactivity only** — data never wears it.
- Focus order and `can_focus` are declared per widget (Textual defaults
  focus NOTHING — `can_focus=False` is the silent default).

## 3. Part B — home rebuilt for GLANCE posture (H2)

Current `HomeScreen` (`mapper/app.py:304`) keeps: the identity row, the
resume row, the recents rail, the empty state that onboards. REPLACE the
"everything equal" middle with:

1. **The hero — drawn, not labeled.** The loudest signal = documentation debt
   of the map the operator actually works: the count of nodes *sin acta*,
   drawn as 3×5 block digits (port `draw_number()` and `_DIGITS` from
   `generate.py` — or Textual's `Digits` if its look matches; the block font
   is already verified). Beside it: `nodos sin acta` / map name / the
   severity cap `▲ N vencen hoy` in WARN. Signal choice rule: the loudest
   enabled signal wins the hero; a calm board shows the count in INK with NO
   warn line.
2. **One inline distribution line** (s19's microbar, port `microbar()` with
   its floor — a present count never paints as absent):
   `con acta N ███████░░░ · sin acta M ██░░ · cobertura P %`. WARN only on
   the sin-acta segment. NOT a row of KPI tiles.
3. **The activity sparkline in the dim tier**, beside the hero — never INK,
   never ACCENT. It supports; it does not compete.
4. **The archived note names its key**: `(1 mapa archivado — u restaura)`.

## 4. Part C — map: minimap + answering branches (M2)

The map views live in `mapper/views/` (outline/lane/layered/radial). Add:

1. **Coverage minimap, one row**, above the tree (s19's memstrip): one glyph
   per top-level branch — `█` completa (INK) · `▒` media (MUT) · `░` baja
   (WARN) · `╱` sin datos (WORDMARK). `╱` is a separator, not a count. Legend
   inline on the same row, glyphs in their tones, words MUT.
2. **Collapsed branches still answer** (gbl): a folded branch renders
   `▸ nombre  N nodos · M sin acta`; the `M sin acta` segment is WARN when
   M > 0. The fold count is DECLARED — nothing disappears in silence.
3. **Pagination** `‹ n/m ›` when the tree exceeds its budget; the shed count
   is stated (`+N no mostrados`).
4. **Toast discipline**: toasts are for EVENTS (guardado, exportado) — a
   bottom strip on PANEL, status WORD bold INK + detail MUT (no `✓` glyph).
   Routine status never toasts.

## 5. Part D — repo: one shared time axis (R2) + the contrast amendment

`PlugRepoScreen` (two-pane variant C) keeps its skeleton+spinner fetch state
(C4 — that part was right). The CONNECTED state becomes:

1. **Source line with honesty badge**: `url  [ github ]  N ramas · M
   releases` — badge `github`/`local` on STEP.
2. **Branches and releases on ONE 30-day axis** (port `_time_row()`): each
   row places its event (`●` commit, `◆` release) by age; the today rule `╎`
   sits in the SAME column on every row. Notes carry age and drift
   (`hace 6 d · +4/-12`, `sin pr`).
3. **Legend row**: `● commit   ◆ release   ╎ hoy   (30 días)`.

**Amendment to HANDOFF-darkside §3 (binds everywhere):** STEP (`#262626`) is
invisible on GROUND (`#000000`) — it works only as a track over PANEL. On the
black ground the dim floor is **WORDMARK (`#3a3a3a`) for glyph tracks, rules
and legends' swatches, and MUT for words**. Three legends and the today rule
were invisible until this was fixed in the prototype. Audit existing screens
for STEP-on-GROUND text while landing this.

## 6. Suggested stories (continue numbering; add to `01-requirements.md`)

- **US-025** component library: the nine darkside components with the
  default/focused/disabled state matrix; a settings surface as the canary.
  AT: each component renders its three states; focus is a solid block;
  disabled sinks to STEP; no passive element wears ACCENT.
- **US-026** home hero: drawn-number documentation-debt hero + severity cap;
  microbar distribution line; dim-tier sparkline; archived note with its key.
  AT: calm board renders the count in INK with no WARN line; the sparkline
  never carries INK/ACCENT.
- **US-027** map minimap + answering branches: one-glyph-per-branch coverage
  row with legend; folded branches declare `N nodos · M sin acta`.
  AT: a folded branch with debt shows the count in WARN; `╱` appears only for
  branches with no data.
- **US-028** map pagination + toast discipline: `‹ n/m ›` under the tree,
  shed counts stated; toasts only for events, word-based (no status glyphs).
- **US-029** repo connected state: shared 30-day axis, `●`/`◆`, shared today
  rule column, source honesty badge, legend row.
  AT: two events at the same age align vertically; the badge matches the
  actual source (local path vs URL).
- **US-030** contrast amendment audit: no STEP-styled readable text on
  GROUND; tracks/rules on GROUND use WORDMARK; a render test sweeps the
  screens.

## 7. Verification (all required)

- `python -m pytest tests/ -q` — green (68 at handoff; add per-story tests;
  render tests should assert the state matrix and the alignment laws, not
  screenshots).
- `python prototypes/ui_components/generate.py` — regenerates the spec.
- `node prototypes/ui_components/verify.cjs` — browser check: 7 figures, no
  page errors (pattern already proven; patchright path is hardcoded inside).
- Register every decision in `state.json.decisions_log` + the batch `PLAN.md`.

## 8. Explicitly NOT in this batch (backlog, studied but not yet designed)

- desk's keybar with per-hint priorities and visible truncation (`…` when
  something sheds) — current keybar truncates silently.
- s19's per-screen legend (`k` opens a legend filtered to the active screen
  with an annotated example card).
- gbl's collision policy for dense lanes (first token wins, occluded token
  underlines).
- desk's declared field budgets per view (FIELD_ROWS/MIN/MAX allocator).
