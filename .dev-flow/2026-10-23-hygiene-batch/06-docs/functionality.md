# Functionality — mapper — Batch 2026-10-23-hygiene-batch

> Phase 6 artifact. Owner: `docs-writer`. Audience: technical stakeholder.

## 🔑 At a glance (read first)

- **What this batch added:** NO_COLOR neutralisation (Q1) · bounded map/CSV loading with
  typed refusals (Q2) · the scalecheck render sweep + a `Canvas.put` audit hook (Q3).
- **Capabilities:** colour always on · capped byte/depth/node/edge/anchor/NUL/non-UTF-8
  input with typed `ContentReadError`/`MapStoreError` refusals · 120-combination
  geometry sweep (7 renderers × 5 sizes × 4 states) · clip/overprint audit events.
- **How to use it:** nothing to invoke — the limits are active on every
  `MapStore.load` / CSV import; the sweep runs as `tests/test_scalecheck.py`; the audit
  hook is opt-in per construction site (`Canvas(w, h, tones, fallback, audit=sink)`).

> Enough to know what shipped and how to reach it. Detail below for how it works.

---

## Detail (reference)

### How it works (flow)
1. **Q1 — colour always on (lane L1, `mapper/app.py`).** `MapperApp.__init__` removes
   `NO_COLOR` from the environment before the terminal backend initialises, so colour
   cannot be disabled from outside; painted screens are byte-equal with and without
   `NO_COLOR=1` (AT-108).
2. **Q2 — bounded loading (lanes L2a/L2b).** One frozen reader surface
   (`mapper/osopen.py`, ruling D2) exposes `read_capped` and the `MAX_*` constants.
   `MapStore.load` re-checks the byte cap after a fast stat, then a prescan
   (`store._prescan_sidecar`) validates depth (≤ 64), refuses YAML anchors/aliases with
   a coordinate-and-map-id message whose anchor display is capped
   (`ANCHOR_NAME_DISPLAY = 40`), and enforces node/edge caps (100,000/100,000, ruling
   R1). Diff-side content goes through the same caps over the pinned
   `subprocess.run(["git", "show", …])` seam and degrades to `None` on any refusal,
   including undecodable output (decode guard). CSV import consumes `read_capped`
   (per-file byte cap + NUL probe + typed non-UTF-8 refusal); the home screen surfaces
   the refusal's own message — never the path — in the import toast (AT-114).
   Windows device-name ids are refused by census record (existing refusal suite).
3. **Q3 — proof of fit + audit trail (lane L3, frozen D1 interface).**
   `tests/test_scalecheck.py` derives the renderer roster from `mapper/views.__all__`
   (no hand-maintained list), renders every renderer at 80×24, 90×30, 118×34, 160×45,
   200×50 across 4 states (120 combinations), and fails on any line/cell overflow — the
   sweep is a harness, so no renderer byte changed (ruling R10 corrected the oracle to
   measured truth). `Canvas` gained an `audit` sink parameter: `put` records clip and
   overprint events with coordinates; `rows()` output is byte-identical with or without
   a sink, and existing digest/golden suites pin that no observable behaviour moved.

### Components / modules touched
| Module | Role in this batch |
|--------|--------------------|
| `mapper/app.py` | Q1: `NO_COLOR` removed before super-init (L1) |
| `mapper/osopen.py` | D2 reader surface: `read_capped`, `MAX_*` caps, typed `ContentReadError` (incl. non-UTF-8) |
| `mapper/store.py` | byte-cap stat+re-check, `_prescan_sidecar` (depth/anchors/count caps), diff-side cap, `ANCHOR_NAME_DISPLAY` bound |
| `mapper/diff.py` | seam-pinned bounded `git show` capture + UnicodeDecodeError guard; `None`-on-error for every caller |
| `mapper/import_csv.py` | capped read + typed refusal propagation |
| `mapper/screens/home.py` | CSV refusal toast shows the authored reason, path-free (F-UX-1, ruling R7) |
| `mapper/canvas.py` | D1-frozen `audit` hook: clip/overprint events from `put` |
| `mapper/views/*` | swept by the scalecheck harness only — zero byte changes (verified by scoped diff) |
| `tests/test_scalecheck.py` · `test_canvas_audit.py` · `test_colour_always_on.py` · `test_ingestion_limits.py` | the batch's test surface (+ 3 amended `LLR-N13.1.7` arms in `test_repair_sidecar.py`, ruling R10) |

### Usage / examples
- Limits are automatic: `MapStore.load(path)` raises `MapStoreError` naming the limit,
  the coordinate (for anchors), and the map id; `git_diff(…)` returns `None` on any
  diff-side refusal; the CSV toast shows `could not read CSV '<name>': <reason>`.
- Audit hook: `Canvas(w, h, tones=…, fallback=…, audit=sink)` where `sink` receives
  `("clip", x, y, ch)` / `("overprint", x, y, old, new)` events; default `audit=None`
  adds zero overhead to the shipped path.
- Sweep: `env -u NO_COLOR -u TERM python -m pytest tests/test_scalecheck.py -q` — the
  roster, sizes, and states are all derived, so a new renderer or size fails the sweep
  until it fits.
- Gate convention (this batch): every verdict-bearing run uses
  `PYTHONIOENCODING=utf-8 env -u NO_COLOR -u TERM python -m pytest …` — a worker shell
  exporting `NO_COLOR`/`TERM` once produced a false 171-failure run
  (see `05-postmortem.md` Incident 3).

### Diagrams
No new architecture this batch (two new import edges into the frozen D2 reader only, as
the ARQ amendment licensed; `canvas` stays dependency-free by constructor injection).
The module map remains `docs/ARCHITECTURE.md`; `06-docs/diagrams/` is intentionally
empty for this batch.

### Evidence checklist — docs-writer
| Item | ✓/✗ | Evidence |
|---|---|---|
| Every claim traceable to the matrix / validation record | ✓ | `06-docs/traceability-matrix.md` §1/§1b rows; `04-validation.md` Layers A/B |
| Module roles match the shipped diff | ✓ | scoped diff `b5dba72..a860a27 -- mapper/` = the 7 modules above; renderers/views zero-byte |
| Usage snippets executable as written | ✓ | the sweep command and audit signature re-read from `tests/test_scalecheck.py:68` and `mapper/canvas.py:96-97` |
| Batch process conventions disclosed | ✓ | clean-env + `<user>` redaction conventions in the Usage section and postmortem Incidents 2-3 |
