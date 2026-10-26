# PDR evidence — security-reviewer — batch 2026-10-25-relmap-r2-batch

Independent review at the PDR gate (triggers C6/C8 fired). Lens: the four markup sinks
(LLR-RVM.4.2 / RVG.3.1 / RVS.5.1 / RVH.5.2), the RVU.1.1 hook bound vs the R1 D4 prefix rewrite,
cap-scale render work, the read-only path, and the hostile AT arms. I authored none of the
artifact. Probe executed 2026-10-25 in the worktree with
`PYTHONPATH=<worktree> PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8`.

## Scope reviewed

- `design/design-proposal.md` (336 lines) — the artifact under review (pre-implementation design).
- Contract: `01-requirements.md` (§6.3 scan answers :1049-1072; LLR validations :306,:327,:362,:404;
  RVH.5.2 verification :827-828; premise P12 :261).
- Acceptance design: `01b-acceptance-design.md` AT-134 (:76-84), AT-139 (:138-146),
  AT-144 (:192-198), AT-148 (:236-246), AT-152 (:279-291).
- Seams it relies on: `mapper/darkside.py:498` (PRESERVED_CODE_POINTS), `:517-547` (COERCION_RANGES),
  `:550-561` (`plain`), `:564-599` (`_ROW_BREAKERS`/`_row_text`/`shown_cells`), `:602-621` (`fit`);
  `mapper/canvas.py:114-130` (`put`), `:170-172` (`text`), `:207-237` (`rows`);
  `mapper/screens/draft_guard.py:54-80`; `mapper/reqharness/audit.py:88-118` (`_visible`),
  `:372-388` (`_hook_lines`), `:429-436` (`run_cli` print path);
  `mapper/relmap/descriptor.py:37-54` (K1–K17), `:200-208`, `:211-216`;
  `mapper/relmap/adapter.py:121-131`; `mapper/relmap/model.py:34,67-71`;
  `mapper/osopen.py:92-94`.

## Record §A rows in my lens (row # | ✓/⚠/✗ | Evidence)

| # | Mark | Security-lens evidence |
|---|---|---|
| 1 | ✓ | Proposal is complete; §6 risk table names a mitigation and owner for every security-relevant risk (risks 1, 2, 6); hostile arms and mutants are named per sink. |
| 2 | ✓ | No boundary move; §6.3 C6 answer (b) (`01-requirements.md:1068-1070`): no new crossing — workspace file reads only, no network, no subprocess, no `osopen` on this screen. `screens/relmap` dependency row limits the package to the D3 read-only API + `canvas`/`design`/`darkside` (proposal §2). |
| 3 | ✓ | §7 six rows, every consumer named; the escaping seam's consumer is every renderer lane at entry. |
| 4 | ⚠ | Coverage is foreseen for the four sinks, but the hostile vocabulary (P12, `01-requirements.md:261`) and every hostile AT arm name only ESC / U+202E / brackets / BEL — **no LF or TAB payload anywhere** (grep over the batch dir: zero hits). See F-SEC-1. |
| 5 | ⚠ | Arms are observable and non-vacuous, but no named mutant or AT would redden on an LF/TAB-carrying label, because the seam as worded (`darkside.plain`) preserves both. See F-SEC-1. |
| 6 | ✓ | The two discharged seams are probed (`evidence/p2-seam-at-driver.md`, `evidence/p2-seam-workspace-repo.md`); the hook bound has the R1 golden surfaces as a tripwire (§6 risk 6). |
| 7 | ⚠ | D4 freeze semantics verified safe against the R1 prefix rewrite (see ordering audit below). But the D1-frozen seam wording in proposal §2 `base.py` row and §6 risk 2 names bare `darkside.plain` — insufficient as stated (F-SEC-1). Freeze the corrected wording, not the current one. |
| 8 | ✓ | File sets disjoint; RVU owns `reqharness/audit.py` alone (F-3); the `osopen` allow-list census (`tests/test_arch_osopen_callers.py`) and the A3 `.render(` census are re-run per lane. |
| 9 | n/a — | UX lens (D1); owned by `ux-reviewer`, not this review. |
| 10 | ⚠ | This review. One MAJOR condition (F-SEC-1) and one MINOR (F-SEC-2) owed at seal; everything else in the lens checks out (below). |

## Escaping-helper probe

Executed 2026-10-25 against `mapper.darkside.plain` (`mapper/darkside.py:550`) in the worktree.

| Input bytes | `plain()` output | Safe? |
|---|---|---|
| `[bold]` | `[bold]` (unchanged) | ✓ in a markup-free sink — the string still carries live markup syntax; safety comes from the sink, not the helper (docstring `:554-557` says so). ✗ in any markup-parsing sink (M-RVG-13's exact point). |
| `[/]` | `[/]` (unchanged) | Same as above — unchanged `[`-syntax passes through. |
| `[@click=quit()]` | `[@click=quit()]` (unchanged) | Same as above; the precedent docstring (`draft_guard.py:57-58`) names this case explicitly. |
| `ESC \x1b[31mred` | `'ESC �[31mred'` (U+001B → U+FFFD) | ✓ ESC neutralised; remaining `[31m` is inert text in a markup-free sink. |
| `bidi \u202e ereh` | `'bidi � ereh'` (U+202E → U+FFFD) | ✓ bidi override neutralised. |
| `isolate \u2066abc` | `'isolate �abc'` (U+2066 → U+FFFD) | ✓ isolate control neutralised. |
| `newline\nbreak` | `'newline\nbreak'` (**LF preserved**) | ⚠ **not row-safe as-is** — `plain` deliberately preserves LF (`PRESERVED_CODE_POINTS`, `:498`); a literal LF in a one-row `Text` fabricates a row break (documented lesson INC8-SEC-F1, `:564-575`). Needs `_row_text`/`fit` for any single-row cell. |
| `tab\there` | `'tab\there'` (**TAB preserved**) | ⚠ same — TAB reaches a real terminal as its own cursor motion past computed padding (`:570-572`). Needs `_row_text`/`fit`. |
| combined `[bold]x\x1b[31m\u202emore[/]` | `'combined [bold]x�[31m�more[/]'` | ✓ for controls/bidi; bracket syntax unchanged-inert under the sink-side guard. |
| `amp <&> \u0007 bell` | `'amp <&> � bell'` (BEL → U+FFFD) | ✓ C0 neutralised; no HTML-ish interpretation risk in Rich/Textual sinks. |

Probe verdict: `plain` is a **control/bidi coercer, not a markup escaper, and not a row normaliser**.
The dual-guard claim holds only with the sink-side half (explicit-style `Text` / `markup=False`) —
which the Canvas architecture supplies structurally: `Canvas.put` stores ONE character per cell
(`canvas.py:114-130`), `Canvas.text` iterates characters (`:170-172`), and `rows()` appends single
chars with explicit styles into a `Text` (`:207-237`) — no markup parse point exists on the canvas
path. The one gap is the row breaker: a preserved LF/TAB placed into a cell becomes a real line
break / cursor motion inside the painted row. That gap is already closed in-repo by
`_row_text` (`darkside.py:579-584`: `plain` + LF/TAB/CR → single space), used by `fit`/`shown_cells`
— but the proposal's seam names only `plain`.

## Precedent audit (draft_guard.py:54-67 — what it actually does)

Confirmed — the claimed dual-guard is real and correctly documented:

- `:60, :62` — both operator-supplied parts (`node_title`, `map_id`) pass through `darkside.plain`.
- `:67` — the sink is `Static(self.sentence(), …, markup=False)` — the sink-side half.
- `:57-58` — the docstring states the exact reason for both halves: `markup=False` alone leaves ESC
  in (it strips only BEL/BS/VT/FF/Cr); `plain` alone leaves `[@click=…]` live in a markup sink.
- `:72-80` — the hints half uses `Text.assemble` with explicit style tuples (the explicit-style sink).

Caveat: the precedent's sentence is a multi-line-capable dialog string, so its use of bare `plain`
(without `_row_text`) is fine there; canvas rows are single-row cells, so the relmap seam needs the
stronger `_row_text`/`fit` coercion, not just `plain`.

## Cut-before-escape / no-mid-spelling ordering audit (lens 2)

Read of the live print path (`mapper/reqharness/audit.py:429-436`) with the plan's rule "cut AFTER
the escape pass, at the sink" (proposal §2 `audit.py` row, §4 D4, AT-152):

- Current pipeline: `shown = _visible(line)` (escape, `:432`) → `verdict: ` prefix rewrite
  (`:433-434`) → `print(shown)`. The 240 cut slots into this loop on the escaped string.
- **No ordering hazard with the D4 prefix rewrite.** A cut truncates the tail only; it can never
  change the line start. Whether the cut runs before or after the rewrite, a line that starts
  `verdict: ` keeps that start and is rewritten; a line already rewritten to `structure: verdict: …`
  cannot be re-exposed by a tail cut. The `never re-exposes verdict: ` rule is satisfiable in either
  order; the rewrite check (`:433`) must simply keep running on the final string, as it does today.
- The one genuine hazard is the one the plan already names: cutting BEFORE escaping (M-RVU-1) would
  under-count (a 240-raw-char line escapes past 240) and could cut mid-spelling on the raw form.
  AT-152's hostile arm counts on the emitted (escaped) form and the straddling arm pins the
  spelling-boundary back-off — correct as designed.
- Scope check: the 240 bound applies to hook lines only (`_hook_lines`, `:372-388`); the report body
  incl. its own `verdict:` line (`render`, `:368`) is out of scope — the proposal's "any hook line"
  wording matches.
- MINOR recommendation (folded into F-SEC-3): pin the pipeline order
  escape → cut(239+ellipsis, spelling-aware) → rewrite check → print in the Inc-7 spec text, so a
  future edit cannot silently swap the first two steps.

## Cap-scale DoS judgment (lens 3)

Honest judgment: **the valve is adequate; one budget gap remains (F-SEC-2, MINOR).**

- Painting is bounded by construction: no unwindowed row set (M-RVM-1), counted overflow
  (M-RVS-12), windowing follows the cursor (proposal §3). At a 34-row viewport the painted work is
  O(viewport cells) regardless of N=100,000.
- `neighbourhood(focused, 2)` for dimming/hop-2 counts is depth-2-bounded (LLR-RVM.2.3, M-RVM-6) —
  the cap-scale risk of a per-row call is mutant-pinned dead.
- The residual unbounded piece is the `c` stacked chain: "every distinct node by minimum hop,
  unbounded in depth" requires a full BFS over the reachable component to produce the honest
  `… +NN more` count — O(V+E) ≤ ~200k dict ops at the shipped caps (`mapper/osopen.py:93-94`).
  That is a one-shot, operator-keypress-triggered computation, cacheable until focus or graph
  changes; worst case is a one-frame hitch (order 10² ms), not a hang, and it cannot be triggered
  remotely or per-frame. The derivation side's 10× wall-clock budget (`LED-2026-10-25-r2.09`)
  does not cover it, though. Record the number at Phase 3 (F-SEC-2).

## Read-only path (lens 4)

- **Binding list** `1/2/3/cursor/enter/c/k/r/q/escape` (proposal §4 D3): all view-switch,
  navigation, toggle, refresh, leave — **no write action**; `r` re-derives read-only through the D3
  API (R-019). BINDINGS == seat is mutant-pinned (M-RVH-10), and a write action added to the seat is
  M-RVH-5. ✓
- **Host reach**: proposal §2 `screen.py` row bans WRITE concerns, `store` (the D3 API is the one
  door), `model`, `reqharness`, raw reads outside `relmap`'s readers, and `osopen` launches; §6.3
  answer (b) confirms no network/subprocess; LLR-RVS.7.1 bans `osopen` on the sheet with the
  `test_arch_osopen_callers.py` census re-run. ✓
- **Refusal / closed set**: K1–K17 is an enumerable fixed-string table
  (`mapper/relmap/descriptor.py:37-54`, `MappingProxyType`); `refusal_line` (`:211-216`) renders
  fixed text plus `cut(base_name)` — never `str(exc)`, never a path or YAML snippet
  (`01-requirements.md:1070-1071`); the app-alive arms are AT-148 hostile + AT-145 boundary (b);
  M-RVH-13 (`str(exc)` rendered) and M-RVH-14 (re-raise) are the named mutants. ✓ — with the F-SEC-1
  note that `cut(base_name)` is a width cut only (`model.py:67-71`): the refusal line and the Home
  row name must also pass the row-text seam, since descriptor file names are operator-supplied bytes
  (AT-145's `x[y].relmap.yml` arm covers Home; extend the same bytes to the screen-level arms).

## Hostile AT arms (lens 5)

All four arms carry **concrete named bytes** and **observable assertions** — none is
absence-of-crash-only:

- AT-134 (:76-84): `[bold]`, ESC, U+202E id + bracket/control title → asserts the plained substring
  IS present in exported text, zero raw ESC bytes, no leaked style, zero unexplained audit events. ✓
- AT-139 (:138-146): `[bold]x[/bold]`, `\x1b[31m`, U+202E, U+0007 → asserts painted-frame literal
  render, zero payload-attributable style runs, row count equal to the benign fixture, no exception. ✓
- AT-144 (:192-198): `[bold]red[/]`, `\x1b[31m`, BEL, U+202E → asserts byte-literal frame, no
  unintended ACCENT/ALERT/WARN span, clean exit. ✓
- AT-148 (:236-246): `[/bold]` + ESC + U+202E + control char + anchors payload → asserts refusal
  line OR literal render, no `MarkupError`, no style bleed, app alive — the loosest of the four
  (disjunctive outcome) but still byte- and style-observable, not crash-only. ✓ with the F-SEC-1 gap:
  **no arm carries LF or TAB**, the two bytes `plain` provably preserves.

## Standard sweep

- **Secrets**: none — no credential, token, or env material anywhere in the plan or its fixtures;
  §6.3 answers the scanner's `token` flag as the Darkside colour tokens / keymap seat data
  (`01-requirements.md:1054-1055`). checked
- **PII / real-person data**: n/a — fixtures are synthetic `build_map` maps and fixture workspaces
  (`legacy.mmd`, `demo.relmap.yml`); no real names, accounts, or home paths in the plan. checked
- **Outbound connectors**: none — §6.3 C6 answer (b): no network, no subprocess, no OS handler on
  this path (`01-requirements.md:1068-1070`). checked
- **Destructive surface**: none — the screen is read-only by design (D3 seat has no write action);
  `--audit` is a read-only CLI; no rm/rename/migration anywhere in the plan; the only writes are
  test fixtures under `tests/`. checked
- **New dependencies**: none proposed. checked

## Findings

### F-SEC-1 — The named seam (`darkside.plain`) preserves LF/TAB; no hostile arm carries them [MAJOR]
- **What:** The proposal's one mitigation for all four markup sinks is "every label coerced through
  `darkside.plain` into explicit-style `Text` or `markup=False` sinks" (proposal §2 `base.py` row,
  §6 risk 2). Executed probe: `plain("a\nb")` → `'a\nb'`, `plain("a\tb")` → `'a\tb'` — both preserved
  by design (`PRESERVED_CODE_POINTS`, `mapper/darkside.py:498`). A label carrying a literal LF, painted
  as one canvas row, becomes a real line break inside the row `Text` (`Canvas.text` iterates chars,
  `canvas.py:170-172`; `rows()` appends the char, `:235`) — fabricating a row the C-10 budget never
  accounted for; TAB reaches a terminal as its own cursor motion past computed padding. This is the
  already-documented lesson `INC8-SEC-F1` (`mapper/darkside.py:564-575`), which is exactly why
  `_row_text`/`fit`/`shown_cells` (`:579-621`) exist. No hostile AT arm (AT-134/139/144/148), no
  named mutant, and the P12 hostile vocabulary (`01-requirements.md:261`) include LF or TAB — grep
  over the whole batch directory returns zero occurrences — so nothing in the plan would redden on
  this gap, and the seam wording is about to be frozen (D1) and copied into the contract's
  draft-time verification line (`01-requirements.md:827`).
- **Where:** `design/design-proposal.md:76` (base.py row), `:286` (§6 risk 2); `01-requirements.md:827`
  (LLR-RVH.5.2 verification names `mapper/darkside.py:550` (`plain`)); `mapper/darkside.py:498,
  :550-561` (helper semantics); `mapper/canvas.py:170-172, :235` (row fabrication path).
- **Why it matters:** the four-sink control is the batch's central C8 claim; as worded it is one
  payload byte short of the project's own established single-row contract, and the freeze would
  institutionalise the short version.
- **Recommendation:** (1) Reword the seam to name `_row_text` (or `fit`/`shown_cells`, which apply
  it) — "every label coerced through `darkside._row_text`/`fit` (plain + row-breaker→space) into
  explicit-style `Text` or `markup=False` sinks" — in proposal §2, §6 risk 2, and
  `01-requirements.md:827`; the order stays coerce-then-cut (`LED-2026-10-25-r2.06`, matching
  `shown_cells` measuring after coercion, `darkside.py:587-599`). (2) Add LF+TAB to the hostile
  payload vocabulary (P12) and to at least the shared/host arms (AT-134, AT-148), with the
  assertion "payload renders on ONE row" (row count equal to the benign fixture — the AT-139
  pattern already asserts exactly this, so the oracle exists). Width cuts after coercion remain
  correct and must stay that order.
- **Evidence state:** executed (probe + code read); fix `planned` (design wording + AT arms).
- **PDR condition:** `COND-SEC-1` · MAJOR · reword the frozen seam to `_row_text`/`fit` (not bare
  `plain`) in proposal §2/§6 + `01-requirements.md:827`, and add LF+TAB to the P12 vocabulary and
  the AT-134/148 hostile arms · owner: trunk at seal for the wording; lanes 3/4/5 + contract arms at
  the named ATs.

### F-SEC-2 — No wall-clock budget for the unbounded-depth `c`-chain BFS at cap scale [MINOR]
- **What:** The sheet's stacked `c` chain is "unbounded in depth" with the counted `… +NN more`
  line as the only valve (proposal §3). Producing the honest count needs minimum-hop for every
  reachable distinct node — a full BFS, O(V+E) ≤ ~200k ops at the shipped caps
  (`mapper/osopen.py:93-94`). Bounded and operator-triggered (worst case a one-frame hitch, not a
  hang; painting itself stays windowed, M-RVS-12), but the only recorded budget is the open/`r`
  derivation's 10× wall-clock (`LED-2026-10-25-r2.09`, proposal §3 Resource) — rendering's one
  unbounded computation is not covered.
- **Where:** `design/design-proposal.md:167-170` (algorithm), `:172-177` (resource), `:285` (risk 1).
- **Why it matters:** at the AT-137 cap-scale arm the Inc-5 gate needs a number to assert against,
  or "fast enough" is unverifiable.
- **Recommendation:** record the `c`-chain BFS budget at Phase 3 next to the derivation budget
  (same 10× idiom, measured on the 100,000-node synthetic map), and assert it at the AT-137 cap
  arm or the Inc-5 exit checks.
- **Evidence state:** planned (analysis executed; measurement owed at Phase 3).
- **PDR condition:** `COND-SEC-2` · MINOR · record a wall-clock budget for the `c`-chain
  neighbourhood computation at the AT-137 cap alongside the derivation 10× budget · owner Inc-5
  (sheet lane) with the Phase-3 measurement.

### F-SEC-3 — Pin the hook-bound pipeline order in the Inc-7 spec [MINOR]
- **What:** The cut-after-escape rule is correct and the D4 prefix rewrite is hazard-free in either
  cut/rewrite order (audit above: cuts only truncate the tail, so `verdict: ` can never be
  re-exposed at line start). The residual risk is a future edit swapping escape and cut — the plan
  names the rule but not the pipeline order on the already-tricky `run_cli` loop
  (`mapper/reqharness/audit.py:430-435`). M-RVU-1/AT-152 would catch it in test; a one-line spec
  pin is cheaper.
- **Where:** `design/design-proposal.md:85, :186, :217`; `mapper/reqharness/audit.py:429-436`.
- **Recommendation:** Inc-7 spec states the order verbatim: `_visible` (escape) → 239+ellipsis cut
  with spelling-boundary back-off → `verdict: ` rewrite check on the final string → print.
- **Evidence state:** executed (ordering audit); spec text `planned`.
- Not a PDR condition — fold into Inc-7's packet; AT-152 already pins the behaviour in test.

## Verdict

`approved with conditions`

Conditions (BLOCK-UNTIL at seal):
- `COND-SEC-1` · MAJOR · reword the frozen four-sink seam from bare `darkside.plain` to
  `_row_text`/`fit` (plain + LF/TAB/CR→space) in proposal §2/§6 and `01-requirements.md:827`, and
  add LF+TAB to the P12 hostile vocabulary + the AT-134/AT-148 hostile arms · owner: trunk at seal
  (wording), lanes 3/4/5 + contract (arms).
- `COND-SEC-2` · MINOR · record a Phase-3 wall-clock budget for the `c`-chain BFS at the AT-137
  100,000-node cap and assert it at the Inc-5 gate · owner Inc-5 / sheet lane.

No HIGH/BLOCKER findings: no secrets, no outbound connector, no destructive surface, no write
vocabulary, refusal path renders fixed text from the closed K1–K17 set, the D4 prefix rewrite is
verified safe against the planned cut, the canvas sink is structurally markup-immune, and all four
hostile AT arms are concrete and observable.
