# HANDOFF — mapper improvements (next agent implements ALL of these)

**For:** the implementation agent, after the darkside redesign
(`HANDOFF-darkside.md` is the design-system contract — read it first).
**Status:** the batch is at its Phase-0 gate with **23 user stories READY**
(`.dev-flow/01-requirements.md`); this handoff covers the improvements round
(US-020…US-023 + the D-A design answer) with per-feature implementation notes.

## What this round added

0. **The design triplet (D-A · D-B · D-C)** — rendered and verified:
   - **D-A · radial darkside** (`ds-mental.svg`): grey steps everywhere, ONLY
     the active path (root → selected node) in KMBlue, selected node solid.
     Fixes the production violation: `views/radial.py`'s `tag()` propagates
     branch hues — port the active-path treatment into `RadialRenderer`
     (grey steps by level + the `on_path` set in accent + selected solid).
   - **D-B · motion** (`ds-motion-f0..f5.svg` + the flipbook section in
     `index.html`): six frames of a 300 ms selection move (`auth` → `db`) on
     the real keymap, the solid block cross-fading through the in_out_cubic
     curve — slow at the ends, fast in the middle, exactly the tempo law.
     Production note: Textual `animate(..., duration=0.3,
     easing="in_out_cubic")` on the selection's background; the same breath
     applies to palette open/close and step-chip advance. Never a snap.
   - **D-C · home identity moment** (`ds-home-identity.svg`): the big
     recessive wordmark (a tiny 4×5 block font, `#3a3a3a`) beside the
     computed moon + "mapas vivos", with the recents rail left. The wordmark
     is deliberately quiet — identity at ~42% opacity.

2. **US-020 · Coverage report** — the auditor's worklist: every node missing
   required fields, ordered by subtree, naming what's missing; activating a
   row selects that node on the map. One pass over the node store against the
   map's schema (the ficha already computes per-node coverage — the report is
   the same check, collected). Render it as a darkside report view: rail +
   step-meter coverage per row, alert only where a required field is missing.

3. **US-021 · Map diff vs last commit** — the payoff of "truth lives in git".
   `git show HEAD:<map>.mmd` (+ sidecar) against the working tree; node-level
   set-diff by id, field-level diff by key; paint on the map: added (blue
   block edge — it IS new interactive content), removed (alert ghost with
   strikethrough-title), renamed/field-changed (warn chip naming the field).
   Rename heuristic: same id = same node; title change = renamed. Toggle with
   a key (suggest `=` or a palette command "diff vs HEAD"). Scope: no
   three-way merge, no binary attachment diffs.

4. **US-022 · CSV/TSV import** — the Excel migration path. One row = one
   node; parenting by a `parent` column (id reference) OR an indent/depth
   column; headers map to ficha fields by name. Rows with a missing parent
   park at the root with a marker (never dropped silently — the taskboard
   law). csv stdlib only; .xlsx is out of scope. Suggested flow:
   `construct → import csv → preview tree → save`.

5. **US-023 · Templates + linked maps** — templates are seed graphs in the
   store (ship `legacy-audit`: schema = documento/dueño/estado/criticidad/
   notas with the first three required). A node field `map: <id>` makes it a
   link: opening it lands on the target map with a breadcrumb back
   (`mapper / sistema-legacy / auth → linked: <target>`; esc returns).
   Templates and links are both data in the sidecar, never code.

## Order suggested (value first)

1. D-A port into `RadialRenderer` (closes the language).
2. US-020 coverage report (the audit workflow's second half).
3. US-021 diff vs HEAD (the unique-to-mapper feature).
4. US-022 CSV import (the migration path).
5. US-023 templates + linked maps (structure reuse).

## Repo connector: local path or URL (operator's simplification, US-006 refined)

Plain `git` FIRST: a local path is read in place (`git -C <path> branch -a`,
`git log`, `git tag` — no auth, no API, offline-friendly); a URL clones to a
local cache and reads identically. The `gh` layer (CI verdicts, PR numbers)
is an OPTIONAL enrichment when authenticated. Rendered:
`prototypes/ui_darkside/out/ds-repo-plug.svg` — one input, auto-detected
source, stats preview (ramas · tags · último commit · autor principal).
Implementation: `mapper/github.py` gains a `local` backend; the GitHub one
becomes the enrichment. Releases = git tags.

## Office-format templates (US-024 — the factory's real files)

The template IS the company's real office file: `.docx` / `.pptx` / `.xlsx`
with `{{keywords}}` written inside it, ingested by mapper directly.

- **OOXML = a zip of XML.** Read: `zipfile` + `re` for `{{...}}` — probed
  this round with an in-memory .docx (tags found: puesto, depto, salario).
  NO external parser dependency. (`python-docx`/`python-pptx`/`openpyxl` are
  optional sugar, not required.)
- **Write-back:** string-replace the resolved values inside the XML and
  rezip — the generated document opens in the same office app.
- **The one real hazard:** office editors split text across XML *runs*, so a
  tag may arrive fragmented (`{{pue` + `sto}}`). Mitigation: at ingest,
  concatenate runs per paragraph before matching; strip inner markup inside
  `{{...}}`.
- **Out of scope (in writing):** legacy binary `.doc`/`.xls` (convert to
  OOXML first), charts/images inside templates, password-protected files.
- Render: `prototypes/ui_darkside/out/ds-factory-office.svg` — the template
  row shows the real file, the tags table reads "tag (del docx)".

## Landmines already paid (recap from the darkside handoff)

rich-15 width+height law · badge-stretch (compose headers as one Text) ·
Panel without visible border (`border_style=PANEL, style=on PANEL`) · escape
user text · width-1 glyphs · synthetic fixtures only · `gh` read-only ·
the keymap seat feeds keybar + `?` + palette · selection is solid, motion is
300 ms in_out_cubic, nothing passive is blue.

## Verdict placeholders (filled at review)

- D-A active-path applied to radial: `mapper/views/radial.py` uses `_GREYS` for branches and `darkside.ACCENT` only for the active path + selected node.
- Diff rename heuristic observed on a real map: same id = same node; title change reported as `title` in `DiffResult.changed`; field changes reported by schema key.
- CSV parent-column convention chosen: `parent` column is the id reference; `depth` column is the indentation level; missing parents park at root with `? ` prefix.
- Local-git/URL connector implemented: `mapper/github.py` detects local path, URL (clones to `~/.cache/mapper/repos`), and `owner/name` (uses `gh`); branches/tags rendered with ahead/behind from plain git.
- Office-format templates implemented: `mapper/office.py` reads `.docx/.pptx/.xlsx` via `zipfile`+`re`, handles fragmented tags, and writes resolved OOXML; `FactoryScreen` binds `i` (import) and `g` (generate).
