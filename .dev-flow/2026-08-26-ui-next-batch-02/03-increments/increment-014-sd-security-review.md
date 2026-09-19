# Security Review — Inc-REPAIR S-D (`2026-08-26-ui-next-batch-02`)

Independent reviewer. Branch `feat/ui-next-batch-02`, base `2f78ecc`, working tree
uncommitted. Reviewed at the declared context of use (118x34) and at `run_test`'s
default (80x24), plus a narrow sweep down to 24x8.

## Verdict

**PASS WITH FINDINGS.** No HIGH. One MEDIUM, ruled **pre-existing and not
attributable to this diff** by a controlled comparison against the pre-S-D
behaviour; two LOW; two surfaces driven to a clean falsification.

Nothing here is a deploy authorization. Clearing a risk is not granting a close.

## Scope reviewed

- `mapper/views/radial.py` — `_header_line`, `header_rows`
- `mapper/app.py` — `PAN_INERT_HINT`, `_consumes_pan`, `_reclamp_pan`, `_pan`,
  `_clear_pan_hint`, `_header_rows_for`
- Reachable neighbours pulled in by the four named surfaces: `darkside.hint_line`,
  `darkside.plain`, `HintLine.set_hint`, `_canvas_size`, `_view_state`,
  `refresh_canvas`, `action_export_svg`, `_ImportPreviewScreen`.

All probes ran from my own scratchpad
(`C:\Users\jjgh8\clde\mapper-ui-next3\out\sd-sec\`), byte-level, with
`PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`, `__pycache__` purged.
**Repo integrity proven by hash, before and after every probe:**

| file | sha256 (before == after) |
|---|---|
| `mapper/app.py` | `02892b7450f8c92bd53d5b83fdabef32443f1a0290a351f12a1ae67318e0174a` |
| `mapper/views/radial.py` | `df3512af876b9ff4ac2be130e77cbdb65a30a28eb16570590f01723ccf00e920` |

Tree is CRLF throughout (`app.py`: 3900 CRLF == 3900 LF). Nothing was edited.

Lanes re-run by me, not taken on report: default **1095 passed / 19 deselected /
3 xfailed** in 337 s, exit 0 — matches the declared figure exactly. Ruff **27
errors == baseline 27**. `HERMETIC-1` did not fire (full-lane run).

---

## Surface 1 — the new operator-visible string · **CLEAN, falsified not assumed**

`PAN_INERT_HINT` reaches the strip through
`HintLine.set_hint` → `darkside.hint_line` → `Text.assemble` → `Static.update(Text)`.

I did not take `darkside.plain`'s docstring claim ("safety comes from never
handing a file-derived `str` to a markup-parsing sink"). I drove the widget and
carried a positive control.

**Positive control — FIRED at all three sizes.** The same payload through
`HintLine.update(str)` (the inherited `Static` door, which Textual *does* parse):
`"[red]BOOM[/red] [bold]X[/bold]"` painted as `BOOM X`. Markup was consumed. The
instrument can see a parsing sink.

**The seam under review — does not parse.** Same payload through `set_hint`
painted verbatim: `siguiente ▸ [red]BOOM[/red] [bold]X[/bold]`. A second payload
chosen to *change the frame* if parsed (`a[on red]b`, a background repaint)
survived literally too. `hint_line` composes into `Text.assemble`, which is a
styled-span constructor, not a markup parser. `rich.markup.escape` would be a
no-op here and would print visible backslashes — the module's stated position is
correct, and is now measured.

The constant itself: a module literal, no file input, no `[`/`]`, one non-ASCII
codepoint (`U+00B7`). Live path driven end to end — `r` then `L` in radial paints
the declaration.

Evidence state: **executed**.

*Note (cosmetic, not a finding):* at 40x14 the hint wraps mid-string
(`…no se desplaza ·  navega con…`). Below the declared context; recorded only.

## Surface 2 — worst-case charge on operator data · **CLEAN, bounded by measurement**

`header_rows` charges `_header_line(len(graph.nodes))` and renders it through a
`Console(width=max(1, wrap_w))`.

**The charged line's length is O(log n), not O(n).** `overflow_phrase` embeds the
count as decimal digits, so the line is 42 cells at n=1, 46 at n=12000, and **60
cells at n=10^18**. The structural ceiling of `rows` at `wrap_w=1` is **57**.
There is no input that makes this line long.

Swept `n ∈ {1, 12, 3000, 12000, 12001}` × `wrap_w ∈ {0,1,2,24,30,58,118,400}`:
worst case **14.9 ms / 448 KB peak** (a cold first call), steady state ~1.4 ms /
55 KB. `MAX_RENDER_NODES` is not load-bearing here — exceeding it changes the
charge by one digit.

**Positive control — FIRED.** The same timer/allocator pointed at a line whose
length is *linear* in n (the `outline._indent` shape): 200 000 chars → **5.6 s,
74 MB**. The instrument can see this batch's recorded cost-defect family. It saw
nothing in `header_rows`.

**The availability question the change actually raises, and its answer.**
`_canvas_size` has a cliff: `if region.height <= rows: return w, 1` (nothing
painted). So a charge that *grew* would blank the canvas. Swept **every width
1–200** for `n ∈ {1, 8, 12000}`: the number of widths where the new charge
exceeds the old is **0**. It is equal at 11–17 widths and *smaller* at 183–189.
Driven through the real app at seven terminal sizes down to 24x8: the radial
canvas paints at every one, and `charge_new ≤ charge_old` throughout. The change
only ever gives the region back rows.

Evidence state: **executed**.

## Surface 3 — the unguarded raise in the message pump · **RULING SURVIVES ATTACK**

I attacked the ruling on its own terms and it holds. Both halves are measured.

**The stated cost is real, and my first control was blind.** My initial probe
installed the "fourth renderer" as `screen.renderer = LayeredRenderer()` — which
rebinds the very attribute the identity test reads, so `renderer is self.renderer`
stayed True and nothing was ever unregistered. It reported CLEAN on a known-bad
input. **That reading was void and is discarded.** Repaired by injecting the
foreign object at `_current_renderer` instead, leaving `self.renderer` intact:

- **`_pan` seam — control FIRED.** `LookupError` propagated
  `action_pan_right` → `_pan` → `_consumes_pan` → `app._process_messages_loop`
  and killed the app. The docstring's stated cost ("the first pan press takes the
  app down") is confirmed, not asserted.
- **`_reclamp_pan` seam — degrades.** Caught by `refresh_canvas`'s `try`; canvas
  paints `no se pudo dibujar el mapa` / `no pan consumption registered for …`,
  `app.is_running` stays True. The asymmetry the docstring claims is real.

**The reachability claim holds.** Instrumenting `_current_renderer` and driving a
26-key battery at two sizes: the **derived set is exactly 3 objects** —
`self.renderer`, `self.outline_renderer`, `self.radial_renderer`. No other object
ever returned. `_current_renderer` is a pure function of two booleans, and those
booleans are written in exactly three places (`__init__` and the two toggles).

**The specific worry about `app.py:844` is falsified.** The import preview's
second `LayeredRenderer()` lives on `_ImportPreviewScreen`, which has **none** of
`_pan`, `_reclamp_pan`, `_consumes_pan`, `action_pan_left`, `pan_x`
(`hasattr` probe returned `[]`). With the preview pushed on top and MapScreen's
pan deliberately set **non-zero** (`(49, 0)` — my first run had it at `(0,0)`,
where "unchanged" proves nothing), all eight pan chords were pressed: pan
unchanged at `(49, 0)`, no exception, app alive. Textual resolves actions against
focused-widget → screen → app; MapScreen is not in that chain. The second
instance cannot reach the seams.

Evidence state: **executed**. The ruling stands on measured grounds.

## Surface 4 — pan held across a view excursion · **CLEAN for this diff**

I instrumented `_view_state` — the sole constructor of the renderer parameter
surface and the sole pan reader outside `_pan`/`_reclamp_pan` — so the audit
records *whoever actually calls*, rather than a hand-listed set of call sites.
At each call it compares the live offsets against what `_reclamp_pan` would have
produced at that geometry.

**Held offsets are inert in the artifact — measured, not argued.** Sequence
`radial → fold → export from radial`: pan `(49,10)` under S-D vs `(0,0)` under
the simulated pre-S-D clamp, and the exported SVG is **byte-identical**
(`sha 5d1fd213…`, 92 605 bytes). The non-consumer ignores the offsets exactly as
claimed.

**Returning to layered always reclamps.** `radial → fold → back → export` and
`outline → fold → back → export` both land at `(0,0)` and produce identical
artifacts under both behaviours. The code reviewer's finding is confirmed
independently.

**Not persisted.** `MapStore.save(map_id, graph)` takes only a graph; `pan` appears
nowhere in `store.py`, `export.py` or `mermaid.py`. There is no persisted-session
surface for a stale offset to survive into. Evidence state: **n/a — pan is
memory-only**.

**Where S-D changes the exported artifact, it changes it in the right direction.**
`radial excursion → back → export` differs (S-D `(49,10)` / `sha a138a38d…` vs
pre-S-D `(49,9)` / `sha afd194a3…`). That is S-D *preserving* a pan the operator
legally set in layered — proven by the post-excursion reclamp leaving `(49,10)`
untouched, i.e. it is in range there — where the pre-S-D code silently shaved it
to `(49,9)` by clamping a layered offset against radial's geometry. That is the
defect `PAN-1` exists to close, visible in the artifact.

Evidence state: **executed**.

---

## Findings

### F1 — Exported SVG is rendered from an unclamped pan at a geometry the canvas never used  [Severity: MEDIUM]  ·  **pre-existing, NOT attributable to S-D**

- **What:** `action_export_svg` reads `pan_x`/`pan_y` through `_view_state`
  **without** calling `_reclamp_pan`, and sizes the render from the **terminal**
  (`max(20, size.width), max(5, size.height - 10)`) rather than from
  `_canvas_size()`. At 118x34 that is 118x24 against a canvas of 58x27. Layered's
  `_geometry` shrinks `card_w` at the wider width until the tree fits, collapsing
  `max_pan_x` to 0 — so an offset that is perfectly legal on the canvas is out of
  range for the export, and shifts content off the artifact's left edge.
- **Where:** `mapper/app.py:3466` `action_export_svg`, via `_view_state` at
  `mapper/app.py:3489`.
- **Why it matters:** the loss is silent and large. Exporting the same map at
  pan `(0,0)` yields **47 263 bytes**; at the reachable pan `(49,10)` it yields
  **16 718 bytes** — roughly 65 % of the map missing from a file the operator
  will hand to someone else, with no declaration anywhere. This is the batch's own
  "declares nothing / asserts a smaller map than the one it has" family, on a
  shipped artifact rather than a frame.
- **Attribution (this is why it does not block S-D):** reproduced with **zero
  excursion** — sequence `layered → export`, pan `(49,10)`, `sha a138a38d…` — and
  the run against a simulated pre-S-D `_reclamp_pan` (unconditional clamp, the
  shipped behaviour before this diff, installed on the class in-process and
  restored) produces the **identical artifact**. The defect predates S-D and is
  untouched by it.
- **Recommendation:** either clamp at the export site against the export's own
  geometry, or export from the canvas geometry. Smallest honest fix, for
  `software-dev` to apply — not me:
  ```python
  # in action_export_svg, before building the state
  w, h = max(20, size.width), max(5, size.height - 10)
  self._reclamp_pan(w, h)          # clamp against the geometry being exported
  ```
  Note this call now goes through `_consumes_pan`, so it will also correctly
  decline for outline/radial.
- **Evidence state:** `executed` (defect and attribution both). **Carry to the
  whole-branch gate** alongside `B-62`/`B-64`/`B-65`/`B-66`/`B-67`; suggested id
  `B-68`. Not owed by S-D.

### F2 — `LookupError` message paints `repr(renderer)`, including a heap address, to the canvas  [Severity: LOW]

- **What:** `raise LookupError(f"no pan consumption registered for {renderer!r}")`
  is caught by `refresh_canvas` and rendered through `darkside.plain(str(exc))`.
  Driven, the canvas reads:
  `no pan consumption registered for <mapper.views.layered.LayeredRenderer object at 0x…>`
  — a live heap address on an operator-visible surface, and in anything that
  captures the frame (screenshot, `e` export of a subsequent frame, a bug report).
- **Where:** `mapper/app.py:1701`.
- **Why it matters:** low blast radius for a local single-user TUI — it is an
  ASLR-relevant address disclosure with no remote reader and no privilege
  boundary to cross. It is also not operator-legible Spanish, unlike every other
  degraded message in this module.
- **Recommendation:** this is a **conformance** observation, not a deviation.
  `_header_rows_for` (`app.py:1578`) and `_painted_ids_for` (`app.py:1877`) use
  the same `{renderer!r}` spelling; the new site matches its siblings, which is
  the right call for this diff. If it is ever changed, change all three together
  (`{type(renderer).__name__}`), as one item, not inside S-D.
- **Evidence state:** `executed`. Recommend recording as a batch-level hygiene
  item; **does not block**.

### F3 — Pan hint clears only at the two view toggles  [Severity: LOW]  ·  **verified sufficient**

- **What:** `_clear_pan_hint` is called from `action_toggle_outline` and
  `action_toggle_radial` only. The concern is a latch on some *third* path that
  changes the view.
- **Verification:** `outline_mode` and `radial_mode` are written in exactly three
  places — `__init__` (both `False`) and the two toggle actions, both of which
  clear. There is no third writer, so there is no unguarded transition. The
  scoped compare (`hint.text == PAN_INERT_HINT`) correctly declines to swallow a
  hint another handler set. Reading `HintLine.text` rather than rendering keeps
  the `A3` census population unchanged, as the docstring claims.
- **Evidence state:** `executed` (grep-derived writer set + driven toggle round
  trips in P1/P7, app alive, hint cleared). **No action.**

### F4 — Hint strip is not a markup-parsing sink  [Severity: n/a — falsified]

Driven with a fired positive control. See Surface 1. **No action.**

### F5 — No secrets, no new dependency, no destructive surface  [Severity: n/a]

- Secret scan over the full diff (`api_key|secret|token|passwd|password|PRIVATE KEY|aws_|bearer|ghp_|sk-…`):
  two hits, both the word "token" used in the lexical sense inside docstrings.
  No credential material. No secret value appears anywhere in this report.
- `.gitignore` covers `*.svg` (exports), `*.db`, `.mapper/`, `__pycache__/`.
- **No new dependency.** `from rich.console import Console` — `rich==15.0.0` is
  already pinned in `pyproject.toml:12` and `Console` is already imported by
  `mapper/export.py`, `views/layered.py` and `views/outline.py`. Same version,
  same import, no lockfile change, no supply-chain surface.
- No external tool / MCP / Composio / n8n connector, no network call, no auth
  flow, no outbound action, no destructive command, no deploy step in this diff.
  No client data leaves the system; LFPDPPP is not engaged. Evidence state:
  **n/a — no such surface in the diff**.

---

## Boundary statement

**What I saw.** The four named surfaces, each driven rather than reasoned about,
each carrying a positive control that I report the firing of. Both source files
read in full at the diff and at every reachable neighbour named above. The
default lane and ruff re-run by me. Repo integrity proven by sha256 before and
after.

**A blind spot I constructed, then closed.** My surface-4 instrument hooks
`_view_state`, which has six call sites. Reviewing my own output, **two were never
observed**, so "clean" covered less than it appeared to:

1. `_pan` (`app.py:1750`) — my harness cleared its record buffer *after* panning,
   so no sequence pressed a pan key while recording.
2. `refresh_canvas`'s `except` branch (`app.py:2688`) — nothing raised in any
   sequence, so the degraded path's pan read was never seen.

Both were then driven. (1): 74 recorded calls across a mixed pan/toggle battery at
both sizes, `_pan` observed, zero out-of-range reads. (2): reached by installing a
renderer that raises; the except branch reads a **clamped** pan and `_rendered_for`
records `(49,10)`/`(27,21)` — the same offsets the guarded path had, so the
degraded frame does not desync. App alive. Both clean.

**A blind spot I created and must report.** My first surface-3 control was blind:
it rebound `self.renderer`, so the identity test still matched and the probe
reported the app surviving an "unregistered" renderer that was in fact registered.
Had I stopped there I would have reported the ruling's stated cost as wrong. The
repaired control fired. Any conclusion from the first probe is withdrawn.

**What I could not see.**

- **The 80x24 arm of my first pan-read sweep truncated** after 2 of 8 cases (the
  process exited 0 mid-battery). The declared context 118x34 ran the full battery,
  and the two 80x24 cases that did complete agree with it. The remaining six
  sequences at 80x24 are **not-run**; I rely on the 118x34 battery plus the
  separate two-size runs in P6/P7 for that geometry.
- **`_declare_after_layout`'s settle pass** appeared in my records as a pan
  *reader* and was clean at every observation, but I did not drive its
  `_rendered_for`-mismatch branch (`app.py:1937`) under a concurrent geometry
  change. State: `not-run`.
- **`HERMETIC-1`** did not fire for me because I ran the full lane, not isolation.
  I did not re-open it; it is ruled to Inc-CONFIRM.
- **`B-62`, `B-64`, `B-65`, `B-66`, `B-67`** were not re-opened, per instruction.
  I did observe that F1's export defect belongs to the same "shipped artifact
  declares less than it holds" family that the whole-branch gate is already
  holding carries for, and recommend it join them rather than be repaired here.
- **Non-Windows behaviour, real terminal emulators, and terminal sizes above 118
  or below 24 columns** were not exercised.

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — F1–F5 above.
- [x] Each finding has a severity rating — MEDIUM ×1, LOW ×2, n/a ×2.
- [x] No secret values appear in this output — scan run, no credential material
      in the diff; nothing quoted.
- [x] Verdict explicit — **PASS WITH FINDINGS**; **no HIGH present**, so no
      applied-and-verified mitigation is owed and no `BLOCK-UNTIL` is raised.
- [x] New tool/integration scope and blast radius — **n/a, none added.** No MCP,
      Composio, n8n, network call, or external action surface in this diff; the
      only new import is an already-pinned, already-used stdlib-adjacent symbol
      (`rich.console.Console`, `rich==15.0.0`).
- [x] Tree left unmodified, proven by sha256 (table above); `__pycache__` purged;
      all harnesses confined to my scratchpad.
