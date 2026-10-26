# Acceptance design — mapper — Batch 2026-10-25-relmap-r2-batch

> Companion to `01-requirements.md` (batch convention from R1 post-mortem control C-3,
> carried as B-156): AT bodies and the AT↔requirement matrix live here; the contract keeps
> the statements. `AT-NNN` ids are provisional until Phase 3 mints the on-disk nodes (V-5);
> Layer-B (black-box) ATs drive the real TUI surface through `run_test()` pilots
> (`tests/test_colour_always_on.py:64-70` idiom), Layer-A TCs are listed per LLR in §5 of
> the contract. Every AT drives a non-default value (C-10), exercises the real mechanism
> (C-16 — no proxies), and carries boundary + negative arms.

## Driver seams (shared)

- All view ATs open the derived reqharness map through the host surface (RVH): fixture
  workspace → Home → relation row → `RelMapScreen`. The host push seam and the
  fixture-workspace injection mechanism are PROBED, not assumed (2026-10-25,
  `evidence/p2-seam-at-driver.md`, ruling `LED-2026-10-25-r2.07`): the injection point is
  the `MapperApp(workspace=…)` constructor argument (`mapper/app.py:250`) under a headless
  `run_test()` pilot (`tests/test_colour_always_on.py:64-70` idiom); the fixture workspace
  is a bare tmp dir holding only `<name>.mmd` + `<name>_nodos.yml` (`mapper/store.py:763`).
  Fork precondition F-5 stands; lanes 3–5 re-verify the injection at their entry, not only
  at the join.
- Absolute counts are asserted only on seeded fixture canons; the live worktree canon gets
  invariant/census arms (R1 rule). Live figures measured 2026-10-25 (premise P2): 303 nodes
  (85 HLR, 218 LLR), 215 `refines` edges, 7 gaps (all MED `hlr without llr`, reach 0).
- Sizes: (118, 34) reference and (87, 34) check. Frame capture for style assertions:
  `_painted_frame` idiom (`tests/test_colour_always_on.py:25-34`).
- Hostile payload vocabulary (established R1 practice): `[bold]x[/bold]`, `\x1b[31m`, U+202E,
  U+0007 (BEL), control chars; expected form per `darkside.plain` (`_CONTROL_MAP`, ESC/coerced
  controls as U+FFFD, brackets literal).

## AT-130 — matrix view opens on the honest skeleton (US-RMV-001 · RVM.3.1, RVM.1.x)
- **Observable:** the matrix body shows sourced LLR rows paged with the selection visible, zero
  phantom TC columns, the declaration `no test columns yet — the AT→test table (B-141) feeds
  this view`, and the lens head `what feeds it ←` listing the selected LLR's refining HLR as
  `↑1 refines <id>`.
- **Driver:** open the relation map; press `2` then `1` (leave and re-enter the matrix view);
  move the selection down several rows (non-default).
- **Asserted:** the declaration verbatim; `what feeds it ←`; `a change reaches →`; the
  `↑1 refines` row for the oracle-computed parent; row window `NN–NN / 303` (live figure class).
- **Boundary:** zero-node map → `no node on record`. 87-col arm: declaration and lens rows
  within the panel. **Negative:** M-RVM-8 (phantom columns) → census fails.

## AT-131 — lens summary and hop counts on the real skeleton (US-RMV-001 · RVM.2.2)
- **Observable:** with an HLR selected, `a change reaches →` lists its LLRs at `↓1` and the
  summary reads `change <id> reaches N nodes` / `hop 1: n direct · hop 2: 0 chained` with N, n
  from the in-test oracle (skeleton `down(LLR)` is empty and US is unsourced — hop 2 is
  honestly 0 today).
- **Driver:** select a known HLR (non-default position).
- **Asserted:** `change <id> reaches `, `hop 1: `, ` direct · hop 2: `, ` chained`; gauge row present;
  dimming arm (black-box promotion of LLR-RVM.2.3 per `LED-2026-10-25-r2.10`): with lens
  focus on, the painted frame (`_painted_frame`) shows FAINT style runs on the grid row/column
  labels OUTSIDE the selection's 2-neighbourhood and none inside it.
- **Boundary:** 87×34 — the summary line is cut inside the panel with zero unexplained audit
  events (unit-pinned by TC-RM-09). **Negative:** M-RVM-7 (None → `0`) → RED.

## AT-132 — budget-spent reach renders `not computed` (US-RMV-001 · RVM.2.2)
- **Observable:** after the shared visit budget is exhausted in-test, the lens count renders
  `not computed` in WARN with an empty gauge — no digits fabricated.
- **Driver:** open the matrix view on the prepared map; select any node.
- **Asserted:** `not computed`; absence of any `reaches \d+` pattern for that node;
  the dimming census is unchanged under the spent budget (FAINT outside the neighbourhood
  only, as in AT-131).
- **Negative:** M-RVM-7 → RED.

## AT-133 — binds/evidence cell census on a synthetic map (US-RMV-001 · RVM.1.2)
- **Observable:** on an in-test `build_map` map carrying AT/TC nodes under the REQHARNESS
  profile (possible in-process though the canon does not source them), binds cells render `●`
  with evidence and `◐` tagged without, an AT row with no binds edge bears the `○` badge
  (ALERT open / MUT closed), and verifies lens rows carry `✓`/`!` per `Edge.evidence_missing`.
- **Driver:** open the matrix on the prepared map; move the selection across a bound and an
  unbound AT row (non-default).
- **Asserted:** legend `✓ verifies · ! evidence missing · · no verifies edge`; cell census
  counts per glyph from the oracle.
- **Negative:** M-RVM-2 (letters) / M-RVM-3 (evidence tone dropped) → RED.

## AT-134 — hostile payload on the live matrix surface (US-RMV-001 · RVM.4.2, C8/C-17)
- **Observable:** a node whose id carries `[bold]`, ESC and U+202E and whose title carries
  brackets and a control char renders literally — exported screen text contains the payload's
  printable characters, zero raw ESC bytes, no leaked style, no exception, zero unexplained
  audit events; an LF/TAB arm (COND-SEC-1, P12) carries a title with an embedded LF + TAB —
  the payload renders on ONE row (both bytes coerced to single spaces by `darkside._row_text`/
  `fit`, `mapper/darkside.py:576-621`), so the hostile text cannot forge a second row.
- **Driver:** open the matrix on the prepared hostile map; select the hostile node (non-default);
  the LF/TAB arm re-opens the map with the LF/TAB payload title.
- **Asserted:** `pilot.app.export_text()` contains the plained payload substring; no `\x1b` in
  screen text; no markup exception; the LF/TAB arm additionally asserts the exported text
  contains no raw `\n`/`\t` from the payload and the payload's printable characters appear
  on a single row.
- **Negative:** M-RVM-11 (raw sink) → RED; M-RVH-18 (a sink lets LF/TAB through as row breaks)
  → the one-row assertion RED.

## AT-135 — the ranked gaps screen on the honest skeleton (US-RMV-002 · RVG.1.1–1.3, 2.x)
- **Observable:** opening the gaps view shows the ranked catalogue exactly as R1 computed it,
  Darkside-cased, cursor on the worst gap.
- **Driver:** fixture repo, canon of 3 HLRs (two childless → 2 gaps, so row 02 exists on the ranked axis — the Inc-2 review F9 reconciliation) + a second fixture matching
  the R1 snapshot shape (7 `hlr without llr` gaps, 2 qualified); open the map; press `2` after
  landing on matrix (non-default); assert; press `down` (cursor to row 02, the view's own
  ranked-row axis per the amended RVG.1.3) and assert the highlight moved.
- **Asserted:** crumb `reqharness / relmap / gaps` (wordless at open — `LED-2026-10-25-r2.20`; the
  prototype's `gaps · reach count` was its scene label); header `gaps — what the record
  does not say` + right-aligned `ranked by severity, then reach ↓`; chips `high 0`, `med 7`,
  `low 0`, `total 7` (snapshot fixture); field band `no gap node what reach status`; row 1 =
  `01` + `hlr without llr` + node id + sentence + `000` + `med`; qualified rows end
  `(canon rows near this id could not be parsed or linked: 2)`; every reach cell `000`; keybar
  shows `2 gaps` among `view 1 matrix 2 gaps 3 sheet`.
- **Boundary:** empty-canon fixture → chips `high 0 med 0 low 0 total 0` + `no gaps on record`.
  **Negative:** M-RVG-1/2/4 → RED.

## AT-136 — by-kind toggle on `k` (SHIPPED per ruling `LED-2026-10-25-r2.01`; LLR-RVG.1.5, LLR-RVH.4.1)
- **Observable:** one key (`k`) regroups the same catalogue into per-kind bands with counts
  and worst severity; pressing again returns the ranked frame byte-identical.
- **Driver:** on the snapshot fixture press `k` (bound per LLR-RVH.4.1); assert;
  press again.
- **Asserted:** band heads in catalogue order with `×N` and severity; hint `same catalogue
  grouped by gap kind — scan for a detector, not a severity`; total painted rows unchanged;
  ranked frame byte-identical on toggle-back.
- **Boundary:** toggle on an empty map keeps `no gaps on record`. **Negative:** M-RVG-7 → RED.

## AT-137 — scale, truncation and the audit-clean sweep (US-RMV-002 · RVG.1.4)
- **Observable:** at 118 and 87 the view stays complete, declared and audit-clean; the window
  follows the cursor.
- **Driver:** at 87×34 move the cursor to the last row (non-default; the gaps view's own
  ranked-row axis, host-clamped at the ends — no wrap per the amended RVG.1.3); step a width
  ladder downward; assert WHAT drops whole at its minimum.
- **Asserted:** 87×34 WHAT values end `…` with `reach`/`status` intact; cursor-on-last-row
  shows `+NN above`; audit sink zero `clip`/`overprint` at both sizes.
- **Cap-scale arm (SEC-2 / `LED-2026-10-25-r2.09`):** an in-test `build_map` map at the
  shipped cap (100,000 nodes, `MAX_NODES`, `mapper/osopen.py:93-94`) renders through the
  matrix row window with every undisplayed row declared in words, and the sheet's counted
  overflow line (`… +NN more`) is present; the open/`r` derivation completes within a bounded
  wall-clock budget recorded at Phase 3 (generous bound: 10× the 303-node skeleton
  baseline); the audit sink records zero unexplained `clip`/`overprint` events at both sizes.
- **Negative:** M-RVG-5/M-RVG-6 → RED; M-RVM-1 (windowing dropped) at cap scale → the
  cap-scale arm RED.

## AT-138 — honesty arms: empty map, budget-spent reach, qualified sentences (US-RMV-002 · RVG.2.3)
- **Observable:** the view never fudges honest zeros, declares uncomputed reach, survives an
  exhausted visit budget.
- **Driver:** (a) no-HLR canon fixture; (b) budget-spent synthetic map fixture; (c) snapshot
  fixture with the cursor off row 1 (non-default).
- **Asserted:** (a) zero chips + `no gaps on record`; (b) every reach cell `000` + the tally
  marker carrying the exact not-computed count; (c) the qualifier on exactly `HLR-CAN.1` and
  `HLR-REPAIR.1`.
- **Negative:** M-RVG-10/M-RVG-11 → RED.

## AT-139 — hostile canon text renders literally on the gaps canvas (US-RMV-002 · RVG.3.1, C8/C-17)
- **Observable:** markup brackets, ESC and control chars in canon-derived ids/titles reach the
  screen literally, no style leak, no parse error.
- **Driver:** canon whose gap-bearing HLR id/title carry `[bold]x[/bold]`, `\x1b[31m`, U+202E,
  U+0007; open the map and the gaps view; move the cursor onto that row (non-default).
- **Asserted:** composited frame (`_painted_frame`) shows the payload literally (ESC/coerced
  controls as U+FFFD, brackets visible), zero payload-attributable style runs, row count equal
  to the benign fixture's, no exception.
- **Negative:** M-RVG-12/M-RVG-13 → RED.

## AT-140 — sheet on a linked LLR, honest empties (US-RMV-003 · RVS.1–2)
- **Observable:** the crumb reads `name / relmap / sheet` and the density note reads
  `next ▸ direct feeders only — the chain is one key away, and the cut is declared`; after one
  `c` round-trip the crumb carries `sheet · direct only` (and `sheet · stacked chain` mid-trip)
  — `LED-2026-10-25-r2.20`; header row 0 = `id · title` bold, row 1
  = kind chip; `feeds it` lists exactly the oracle's `up` rows (`↑1 refines <HLR id>`, no glyph);
  `a change reaches` shows the declared empty line `╌╌ none on record`; `gaps on this node`
  shows its declared empty line.
- **Driver:** open the map (matrix default), move the cursor onto an LLR with a parent HLR
  (non-default), press `3`.
- **Asserted:** the strings above; no source/path segment in the header.
- **Boundary:** empty-`RelMap` painter arm → declared empty sheet, no crash. **Negative:**
  M-RVS-4/M-RVS-6 → RED.

## AT-141 — the `c` chain density on an HLR (US-RMV-003 · RVS.3)
- **Observable:** direct density shows reaches rows (`↓1 refines <LLR id>`); `c` flips the tag to
  `stacked chain`, the note to `next ▸ feeds it and a change reaches come free from the engine
  (§3.4 C12)`; rows unchanged on today's one-hop chains (asserted, not assumed); `c` again
  returns `direct only` + `next ▸ direct feeders only — the chain is one key away, and the cut
  is declared`.
- **Driver:** cursor onto an HLR with LLRs, press `3`, assert; press `c` (real key); assert;
  press `c` again; assert.
- **Asserted:** crumb tags and both note lines verbatim; renderer-level fixture arm (TC-RM-17):
  a synthetic 3-level chain renders `↑2` rows and the `+01 more upstream at hop 2` cut in
  direct mode; overflow arm (black-box promotion of LLR-RVS.6.2 per `LED-2026-10-25-r2.10`):
  at a small viewport height (h < chain rows) the frame's last line is the counted
  `… +NN more` in MUT.
- **Negative:** M-RVS-9 → RED.

## AT-142 — the node's own gaps (US-RMV-003 · RVS.4.1)
- **Observable:** the `gaps on this node` band lists exactly the oracle rows for the focused
  node — kind in bold ALERT, Darkside-cased (`hlr without llr`), sentence cut to width — and no
  other node's gap appears.
- **Driver:** cursor onto a gap-carrying HLR (oracle ids from `detect_gaps` over the live
  derived map), press `3`, scroll if needed.
- **Asserted:** row form `! <kind>  <sentence>`; empty arm → declared empty gaps line.
- **Negative:** M-RVS-10 → RED.

## AT-143 — 87-column check, clean audit (US-RMV-003 · RVS.6.1)
- **Observable:** at (87, 34) no row exceeds 87 cells; the long-statement ellipsis matches
  `fit` (one trailing `…`, e.g. the gap sentence ending `EV file…`); nothing wraps; the C10
  audit mapping has zero `clip`/`overprint`.
- **Driver:** same focus as AT-140 at (87, 34).
- **Asserted:** width bounds + audit emptiness; the counted overflow line `… +NN more` is
  asserted on the real screen at (87, 34) as well (LLR-RVS.6.2 black-box promotion per
  `LED-2026-10-25-r2.10`). **Negative:** M-RVS-11 → RED.

## AT-144 — hostile payload on the sheet (US-RMV-003 · RVS.5.1, C8/C-17)
- **Observable:** a focused-node title (and a neighbour id / gap sentence via the fixture
  mechanism) carrying `[bold]red[/]`, `\x1b[31m`, BEL and U+202E renders byte-literal; no
  unintended ACCENT/ALERT/WARN span; no raise; `q` leaves cleanly.
- **Driver:** open the hostile map, focus the node, press `3`.
- **Asserted:** painted frame contains the payload byte-literal; no payload style span; clean exit.
- **Negative:** M-RVS-1-family mutations → RED.

## AT-145 — Home lists relation maps beside tree maps (US-RMV-004 · RVH.1)
- **Observable:** the recents table shows tree and relation rows interleaved by name; kind cells
  read `legacy`/`concept` (tree) or `relation·reqharness` (relation), both `INK on STEP`.
- **Shipped surface:** `#home-recents` DataTable (`mapper/screens/home.py:300`).
- **Driver:** fixture workspace with `legacy.mmd` and `demo.relmap.yml`; open Home; press `j`
  (selection off the default row — with `demo` < `legacy`, row 0 is the relation row).
- **Asserted:** row count = 2; names `demo`, `legacy`; kind cells exact; chip styles from
  `darkside.py:48-57`.
- **Boundary:** (a) no `*.relmap.yml` → tree rows only; (b) hostile name `x[y].relmap.yml` →
  literal render, no markup error, app alive. **Negative:** M-RVH-1/2/3 → RED.

## AT-146 — open routes by kind; read-only (US-RMV-004 · RVH.2)
- **Observable:** `↵` on a relation row lands on `RelMapScreen`; on a tree row on `MapScreen`;
  the relation screen binds no write action.
- **Driver:** on the AT-145 workspace, `j`/`k` to the relation row, `↵`; assert; `q` home; tree
  row, `↵`; assert.
- **Asserted:** active screen class per row; the relation crumb carries `relmap`; keybar shows
  `matrix`, `gaps`, `sheet`.
- **Negative:** BINDINGS census — no write-vocabulary action in SCOPE_RELMAP; `d` triggers
  nothing. M-RVH-4/5 → RED.

## AT-147 — the derived reqharness map opens, honest skeleton (US-RMV-004 · RVH.3, RVH.3.3)
- **Observable:** with no `*.relmap.yml`, Home lists the derived row (canon-stem name); opening
  derives via `default_descriptor()` and renders the HLR/LLR skeleton without invented US/AT/TC
  content; the workspace need not be a git repository.
- **Driver:** fixture workspace with only a small `REQUIREMENTS.md` (HLR/LLR tables) and one
  `*.mmd`; open Home; cursor onto the derived row (non-default), `↵`.
- **Asserted:** derivation received `default_descriptor()` values; rendered text contains an
  `HLR-` id from the fixture; a whole-screen census finds no `US-`/`AT-`/`TC-` id shapes;
  workspace-as-repo arm (LLR-RVH.3.3 / `LED-2026-10-25-r2.03`): the fixture workspace is NOT
  a git repo (no `.git`) and the derived row still opens, with the canon resolved at the
  workspace root (probe `evidence/p2-seam-workspace-repo.md`).
- **Boundary:** (a) missing/corrupt canon → the closed-set `unavailable` refusal line (K3
  `file not found` / K7 `is not UTF-8 text`), app alive — driven through a descriptor row when no
  descriptor exists to list (`LED-2026-10-25-r2.29`); (b) empty canon →
  honest empty map. **Negative:** M-RVH-7 → RED.

## AT-148 — view switching, refresh, leave, hostile descriptor (US-RMV-004 · RVH.3.2, 4.1–4.3, 5)
- **Observable:** `1`/`2`/`3` swap views through the frozen surface; `r` re-derives (derive call
  count 1 at open, 2 after `r`); `escape` and `q` leave to Home; a hostile descriptor never
  crashes and never leaks markup; the view-specific chords are inert off their home view
  (COND-UX-1).
- **Driver:** open a relation screen; press `2`, `3`, `1` asserting chrome per view; `r`; then
  `escape` → Home; reopen, `q` → Home. 87×34 arm. Hostile-descriptor arm (string field with
  `[/bold]` + ESC + U+202E + control char + **LF + TAB** (COND-SEC-1, P12), plus an anchors
  payload). Out-of-view arm (COND-UX-1): on the gaps view press `c` and `enter`; on the sheet
  view press `k`; on the matrix view press `c`/`k` — each against a freshly painted frame.
- **Asserted:** crumb names the active view after each switch; derive count; 87×34 keybar/crumb
  inside the canvas (C10 arm); hostile arm → refusal line or literal render, no `MarkupError`,
  no style bleed, app alive — the LF/TAB payload additionally renders on ONE row (no raw
  `\n`/`\t` from the payload in the exported text); the out-of-view arm → the exported frame
  is byte-identical after each off-home chord (or shows only the declared crumb note), no
  state flips, no crash.
- **Negative:** M-RVH-8/11/13/14/15 → RED; M-RVH-18 (LF/TAB through a sink) → the one-row
  assertion RED; M-RVH-19 (a view-specific chord acting off its home view) → the out-of-view
  arm RED.

## AT-149 — help and palette discoverability (US-RMV-004 · RVH.4.4)
- **Observable:** `?` from the relation screen shows the relmap scope entries; the palette
  offers the relmap actions; both read the seat (equality, not superset).
- **Driver:** press `?`; assert; dismiss; `ctrl+p`, type `mat` (non-default query), move, run
  the highlighted entry.
- **Asserted:** help lists the seat labels for `1`/`2`/`3`/`enter`/`c`/`r`/`q`; palette items
  include the relmap actions with seat glyph+label pairs; running the `matrix` entry lands on
  the matrix view.
- **Negative:** a seat row missing from the help render → RED (equality); duplicate chord →
  TC-RM-25 RED.

## AT-150 — the presentation census: one site, one path (US-RMV-005 · RVT.1.1/.1.2)
- **Observable:** a census over `mapper/relmap/**` finds exactly one definition site for `cut`,
  `DISPLAY_MAX` and `refusal_line` (in `text.py`), exactly one import path for `refusal_line`,
  and zero references to the old paths (`relmap.model.cut`, `relmap.model.DISPLAY_MAX`,
  `relmap.descriptor.refusal_line`, `relmap.audit.refusal_line`).
- **Driver:** run the census (derived from the ASTs, C-31) on the increment's tree.
- **Asserted:** counts 1/1/1, zero old-path hits, `audit.__all__` free of `refusal_line`.
- **Negative:** M-RVT-1/M-RVT-2 → RED.

## AT-151 — the move changes no rendered byte (US-RMV-005 · RVT.1.3)
- **Observable (C-12 output-then-consume):** the shipped `--audit` surface over a refused
  descriptor emits the same refusal bytes after the move as the R1 golden records; the R1
  suite is green unchanged.
- **Driver:** run `mapper --audit` (subprocess, the R1 AT idiom) over a fixture repo with a
  refused descriptor; compare against the R1-captured refusal strings byte-for-byte; run the
  R1 relmap suite.
- **Asserted:** byte identity; `tests/test_relmap_*.py` + `test_prescan_refusal_goldens.py`
  counts equal to the pre-move run.
- **Negative:** M-RVT-3 → RED.

## AT-152 — hook lines respect the per-line bound 240 (US-RMV-006 · RVU.1.1)
- **Observable:** `mapper --audit` over a repo whose structure lines include a line of
  240 + N characters emits that line cut at 239 with one ellipsis, after escaping; the
  emitted line length is ≤ 240; the D4 behaviours are intact.
- **Driver:** subprocess `mapper --audit` over a fixture repo; assert the emitted line's
  length ≤ 240 (bound 240 per ruling `LED-2026-10-25-r2.02`); assert the 1,000-line count
  bound, the `structure: verdict: …` rewrite, the fixed no-repo/no-registry lines and the
  exit code per the R1 pins (TC-RM-02/03 unchanged); hostile arm: a line carrying escapes
  near the boundary is counted on the EMITTED (escaped) form; straddling arm (SEC-1 /
  M-RVU-3): a payload whose `\xNN` or `\uXXXX` escape spelling straddles byte 240 is cut at
  a spelling boundary — the emitted line never ends mid-spelling.
- **Asserted:** cut semantics + emitted-length ≤ 240 + D4 arms green. **Negative:** M-RVU-1
  (cut before escape) / M-RVU-2 (cut re-exposes `verdict: `) / M-RVU-3 (mid-spelling cut) → RED.

## AT↔requirement matrix

| AT | US | LLRs pinned (primary) | Surface | Negative arms |
|---|---|---|---|---|
| AT-130 | US-RMV-001 | RVM.3.1, RVM.1.1/.1.3 | pilot 118/87 | M-RVM-8 |
| AT-131 | US-RMV-001 | RVM.2.2 | pilot 118/87 | M-RVM-7 |
| AT-132 | US-RMV-001 | RVM.2.2 | pilot + spent budget | M-RVM-7 |
| AT-133 | US-RMV-001 | RVM.1.2, RVM.2.1 | pilot, synthetic map | M-RVM-2/3 |
| AT-134 | US-RMV-001 | RVM.4.2 | pilot, hostile fixture (incl. LF/TAB one-row arm) | M-RVM-11, M-RVH-18 |
| AT-135 | US-RMV-002 | RVG.1.1–1.3, RVG.2.x | pilot 118 | M-RVG-1/2/4 |
| AT-136 | US-RMV-002 | RVG.1.5 (shipped, key `k`) | pilot | M-RVG-7 |
| AT-137 | US-RMV-002 | RVG.1.4 | pilot + sweep | M-RVG-5/6, M-RVM-1 |
| AT-138 | US-RMV-002 | RVG.2.3 | pilot, 3 fixtures | M-RVG-10/11 |
| AT-139 | US-RMV-002 | RVG.3.1 | pilot, hostile canon | M-RVG-12/13 |
| AT-140 | US-RMV-003 | RVS.1.1, RVS.2.x | pilot | M-RVS-4/6 |
| AT-141 | US-RMV-003 | RVS.3.1–3.3 | pilot, real `c` | M-RVS-9 |
| AT-142 | US-RMV-003 | RVS.4.1 | pilot | M-RVS-10 |
| AT-143 | US-RMV-003 | RVS.6.1 | pilot 87 | M-RVS-11 |
| AT-144 | US-RMV-003 | RVS.5.1 | pilot, hostile fixture | M-RVS-1 family |
| AT-145 | US-RMV-004 | RVH.1.1–1.3 | pilot, home table | M-RVH-1/2/3 |
| AT-146 | US-RMV-004 | RVH.2.1/.2.2 | pilot, screen stack | M-RVH-4/5 |
| AT-147 | US-RMV-004 | RVH.3.1/.3.3 | pilot, fixture workspace (non-git) | M-RVH-7 |
| AT-148 | US-RMV-004 | RVH.3.2, 4.1–4.3, 5.x | pilot 118/87 + hostile (LF/TAB) + out-of-view | M-RVH-8/11/13/14/15/18/19 |
| AT-149 | US-RMV-004 | RVH.4.4 | pilot, help/palette | M-RVH-12 |
| AT-150 | US-RMV-005 | RVT.1.1/.1.2 | AST/grep census | M-RVT-1/2 |
| AT-151 | US-RMV-005 | RVT.1.3 | `mapper --audit` subprocess | M-RVT-3 |
| AT-152 | US-RMV-006 | RVU.1.1 | `mapper --audit` subprocess | M-RVU-1/2/3 |

**TC index (Layer A):** TC-RM-04…09 (matrix → `tests/test_relmap_matrix.py`) · TC-RM-10…14
(gaps → `tests/test_relmap_gaps_view.py` + the sweep) · TC-RM-15…20 (sheet →
`tests/test_relmap_sheet.py`) · TC-RM-21…27 (shell → `tests/test_relmap_shell.py` +
`tests/test_keymap.py`) · TC-RM-28…29 (text leaf → `tests/test_relmap_text.py`) · TC-RM-30
(hook bound → `tests/test_hook_line_bound.py`). Full per-LLR mapping lives in the contract §4
`Asserting test(s)` fields.
