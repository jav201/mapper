# Independent review — Increment 002 (trunk): screen host + SCOPE_RELMAP seat

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `002` (trunk) — commit `8be99a3` |
| Reviewer | independent increment reviewer — code + security + UX lenses; authored none of this increment |
| Lenses | `agents/code-reviewer.md` · `agents/security-reviewer.md` · `agents/ux-reviewer.md`; record per `templates/increment-template.md` §4b |
| Scope reviewed | 4 source files: `mapper/screens/relmap/__init__.py` (14 lines), `mapper/screens/relmap/base.py` (147), `mapper/screens/relmap/screen.py` (284), `mapper/keymap.py` (+43, the `relmap` seat block) + the 8 amended test files |
| Verdict | **iterate** — 0 BLOCKER · 2 MAJOR (F1, F2 — both trunk-owned, both cheapest to discharge NOW, before lanes 3/4/5 fork) · 9 MINOR |

---

## 1 · The key question: is the frozen D1 surface sufficient for the three lanes?

Frozen surface (pinned by `test_d1_surface_names_are_frozen`, `tests/test_relmap_shell.py:374-400`):
`ViewState(relmap, notice, focus, cursor, lens, gaps, width, height)` (`base.py:75-86`),
`RelMapView.paint(state) -> list[Text]` (`base.py:94-96`),
`RelMapView.toggle(kind: str) -> str` (`base.py:98-100`, COND-ARCH-1),
`build_view(name)` + `PendingView` (`base.py:103-147`).

### Lane L1 — matrix + side lens (lane 3, `LLR-RVM.*`) — **YES, sufficient**

Every RVM need has a channel on the surface, verified line-by-line against the contract (`01-requirements.md:432-510`):

- Rows/cells in `RelMap.nodes`/edge input order, windowing centred on the selection → `state.relmap` (`model.py:135-136,200-206`), `state.focus`/`state.cursor`, `state.width/height` for the viewport and the <60-cell lens fold (RVM.1.1/.1.3, RVM.2.1).
- Lens rings, `reach` gauge, `neighbourhood(.,2)` dimming → all D3 queries on `state.relmap` for `state.focus` (RVM.2.1/.2.2/.2.3) — no host involvement needed.
- Lens focus on/off → the COND-ARCH-1 channel: the host's `enter` chord reaches the active renderer's `toggle("enter")` (`screen.py:267-268,276-283`), state stays renderer-side, the returned word feeds the crumb slot. The channel exists and works.
- Markup-safe labels → the one sink `base.label` (`base.py:50-61`, RVM.4.2); C10 audit → the renderer builds its own `Canvas` (RVM.4.1, renderer-internal).

No host edit required. Caveats that ride along: F5 (the frozen docstring names only `c`/`k` as toggle kinds — a lane reading `base.py` alone cannot discover `enter`) and F6 (the renderer's obligation to paint `state.notice` is unstated in the freeze text).

### Lane L2 — ranked gaps + `k` by-kind (lane 4, `LLR-RVG.*`) — **NO, not as frozen — the `cursor` channel's semantics are the wrong axis**

Everything else the gaps lane needs is on the surface: `state.gaps` is the host-ranked catalogue ranked ONCE by the host (`screen.py:150-156`, satisfying RVG.1.1's "no renderer re-ranks"), `toggle("k")` is the by-kind channel (RVG.1.5), the sink and viewport are there. But:

- The contract (`01-requirements.md:528-538`, RVG.1.3) says the renderer shall "highlight **exactly the row whose index the host passes as the cursor**" — the index is into the ranked-gaps row list.
- The host moves the cursor over the **node list**, with wraparound: `self.cursor = (self.cursor + step) % len(self.relmap.nodes)` (`screen.py:257-265`), "A single list axis … over the node list" (`screen.py:258-260`).
- On every real map `len(nodes) ≠ len(gaps)` (live probe below: 3 nodes / 0 gaps on the shell fixture; AT-135's own fixture "3 HLRs (one childless → 1 gap)"). An exact-index renderer therefore receives `cursor ≥ len(gaps)` the moment the operator holds `down` past the last gap row — `IndexError` on the real screen — while a clamping renderer contradicts the LLR's "exactly" wording.
- The acceptance drivers are written gap-axis too: AT-135 "press `down` (cursor to row 02) and assert the highlight moved" (`01b-acceptance-design.md:92-98`), AT-137 "move the cursor to the last row … `+NN above`" (`01b-acceptance-design.md:118-124`). Worse, AT-135's first fixture has **1 gap row** and its driver says "cursor to row 02" — impossible on any axis (F9).
- The freeze makes this a fork hazard, not a lane detail: proposal §4 "A frozen interface is not touched inside a lane. A lane that needs to change D1–D5 STOPS" (`design/design-proposal.md:197-199`). If the gaps lane meets this at its gate, the batch pays a mid-lane trunk amendment.

Discharge paths (trunk's choice, before the fork): (a) host amendment — the cursor axis is per-view data (nodes for matrix/sheet, ranked rows for gaps); or (b) contract re-wording of RVG.1.3/AT-135/137 to the node axis plus a renderer-side mapping. Either is small now; both violate F-3 if discovered inside lane 4.

### Lane L3 — sheet + `c` full chain (lane 5, `LLR-RVS.*`) — **YES, sufficient**

- `state.focus` + `state.relmap` cover the header, FEEDS IT / A CHANGE REACHES rows, hop-2 counts and the stacked chain — all D3 queries (`node`/`up`/`down`/`neighbourhood`), with computation "for the focused node only" as RVS.3.2 demands.
- `state.gaps` is exactly RVS.4.1's "host-supplied gap rows … consumed as given".
- RVS.3.3's host/renderer split is honoured: binding + crumb slot host-owned, density state + note text renderer-owned — the `toggle("c") -> str` channel carries the word (`direct only` ↔ `stacked chain`) to the crumb.
- Width/height discipline at 118 and 87 (RVS.6.1) and the counted-line valve (RVS.6.2) are pure functions of `state.width/height`.
- Read-only census (RVS.7.1): no `osopen`/`store`/write vocabulary anywhere in the package (grep-verified; only the docstring negations at `screen.py:11`).

`cursor` and `lens` are unused by this lane — harmless.

---

## 2 · Findings

### BLOCKER — none.

### MAJOR

**F1 — The renderer state word leaks across view switches (crumb shows another view's state).**
- **What:** `_switch` changes `active_view` and repaints but never resets `_view_state_word` (`screen.py:230-234`); the word is set only by `_toggle` (`screen.py:283`) and consumed by the crumb tail (`screen.py:173-175`). After `k` on gaps ("by kind") and a switch to matrix, the crumb paints `matrix · by kind` although the matrix renderer's `toggle` was never called.
- **Evidence:** live-proven on the real screen at **both** 118 and 87 columns (reviewer probe, synthetic gaps renderer standing in for the landed lane — the placeholder's `toggle` returns `""` so the defect is invisible until lanes land): crumb `demo / relmap / gaps · by kind` → press `1` → `demo / relmap / matrix · by kind`.
- **Why it matters:** visible wrong chrome on all three lanes the moment any renderer returns a non-empty word; COND-ARCH-1's channel is host-owned, so the fix is host-side. One line now (`self._view_state_word = ""` in `_switch`); after the fork it is a frozen-host edit inside every lane's blast radius. It also sat in a test blind spot — no arm exercises an on-home toggle (F7b).

**F2 — The frozen `cursor` channel is node-axis; the gaps lane's contract is gap-row axis.** Full analysis in §1 L2. Where: `screen.py:245-265` vs `01-requirements.md:528-538` and `01b-acceptance-design.md:92-98,118-124`. Crash-or-divergence at the gaps lane gate unless discharged at trunk before the fork.

### MINOR

**F3 — dead code: `_VIEW_KEYS` (`screen.py:46`).** Defined, never read — `action_matrix/gaps/sheet` call `_switch` directly (`screen.py:221-227`). M-RVH-19 territory: it suggests a dispatch path that does not exist. Delete or use.

**F4 — dead field: `ViewState.lens` is always `None`.** The host sets `self.lens = None` at init, after every derive, and in the unavailable state (`screen.py:86,137,162`) and nothing else ever assigns it; it is passed into every `ViewState` (`screen.py:202`). The D1 proposal row lists "the lens target" as surface (`design/design-proposal.md:189`), but the landed channel makes it vestigial — lens on/off is renderer-owned state via `toggle("enter")`. Either populate it or drop it from the frozen dataclass **before** a lane drafts against it; as frozen dead surface it invites a lane to read meaning that is never there.

**F5 — the frozen surface's docstring names only two toggle kinds.** `base.py:16-18` documents `c` and `k`; the host's third kind `enter` (matrix lens) appears only in host code (`screen.py:49,267-268`). The lane reading the freeze text cannot discover the full kind vocabulary. Word the freeze `enter`/`c`/`k` — a doc edit, but it IS the frozen document.

**F6 — the renderer's `notice` obligation is unstated in the freeze text.** `PendingView` models "paint the fixed refusal `notice` when there is one" (`base.py:104-110`), but no frozen sentence obliges a landed renderer to honour `state.notice`; a lane could paint an empty body in the unavailable state and pass its own arms (the shell's refusal arms only exercise the placeholder). Pin it per lane at the lane gates (AT-145..148 already route through each view).

**F7 — host-arm coverage gaps, proven by a surviving mutant:**
- (a) **No arm presses the cursor keys.** Gutting `_move_selection` (reviewer mutant M-REV-3) leaves the full 188-node trio GREEN. The four `rnav` seat chords, the host-owned selection, and the `focus`/`cursor` D1 channel are unpinned at host level.
- (b) **No arm exercises an on-home toggle.** The COND-ARCH-1 channel is pinned only for its off-home inert half plus the placeholder's `""` return; nothing asserts that a renderer's returned word reaches the crumb. F1 lived exactly in this blind spot.

**F8 — `base.ViewState` vs `views.state.ViewState` (the commission's question): low risk, already declared.** Different module, different symbol, different shape: the tree kind is an all-default dataclass pinned by the A3 census (`mapper/views/state.py`, `FOCUS_OWNERS` at `:55-58`), the relmap kind is positional-required (`base.py:75-86`). A mistaken cross-import inside `screens/relmap` would fail loudly at paint time (`TypeError` on the required kwargs), not silently corrupt — and any lane test catches it. The packet's §5 declares it; keep the A3 census note when the lanes import the relmap name. No action beyond awareness.

**F9 — contract-level friction the gaps fix must also reconcile:** AT-135's first fixture ("3 HLRs (one childless → 1 gap)") has one gap row while its driver says "press `down` (cursor to row 02)" — unsatisfiable on any cursor axis. Whoever discharges F2 should re-check the AT-135 fixture/driver pair (`01b-acceptance-design.md:92-98`) in the same motion.

**F10 — `enter`-word vocabulary unpinned for the matrix crumb.** RVS.3.3 freezes the sheet's words (`direct only`/`stacked chain`) and RVG.1.5 the gaps hint, but no RVM row pins the matrix lens word for the crumb slot (prototype shows `panel lens`). The lane will invent it; harmless, but the crumb examples in the acceptance design are the only source — name it when F5 is worded.

---

## 3 · Controls the reviewer re-ran (evidence states: executed)

| Control | Method | Result |
|---|---|---|
| Import provenance | `python -c "import mapper; print(mapper.__file__)"` with `PYTHONPATH=<worktree>` | resolves inside the worktree ✓ |
| Targeted suite (commission's command) | `pytest -q -p no:cacheprovider tests/test_relmap_shell.py tests/test_keymap.py tests/test_key_dispatch.py tests/test_relmap_*.py` | **617 passed, 2 skipped** (83s) — includes the concurrently-edited `test_relmap_text.py`, green at run time; trio alone 188 passed |
| Evidence re-hash (C-59) | `sha256sum` of the packet's 5 evidence files | all 5 digests MATCH the packet's declared hashes (red-code-absent `55cc4eed…`, red-move-aside `49859464…`, green-targeted `0624a2fd…`, green-guards `5fc7374a…`, mutants `5a30b039…`) |
| The one label sink vs hostile text (LLR-RVH.5.2 / COND-SEC-1) | reviewer probe through `base.label` | `[bold]x[/]` literal ✓ · `[@click=app.quit]` literal ✓ · ESC coerced to U+FFFD, no `\x1b` ✓ · U+202E → U+FFFD, one cell ✓ · LF/TAB → single space, ONE row, width exact, zero spans ✓ · explicit style arg = exactly one span ✓ |
| Real screen at 118×34 and 87×34 | `MapperApp(<tmp workspace>)` + `run_test()` on a non-git tmp workspace (deleted after) | both sizes: derive count 1→2 with identical args (wrap, COND-QA-4) ✓ · crumb per switch ✓ · off-home `c`/`k`/`enter` frame byte-identical ✓ · keybar truncates `… +7 ? all keys` (115 cells @118) / `… +10 ? all keys` (76 cells @87) ✓ · refusal line `structure: refused (demo): file not found - descriptor skipped`, no path leak, app lives, `q`/`escape` → HomeScreen ✓ · cursor moves on the node axis, wraps at node count (the F2 evidence) ✓ · **stale-word defect live at both sizes** (F1) |
| Seat conventions + census pins | read of `keymap.py:334-358` vs every other scope; the 7 amended test files at `8be99a3` | `KeyBinding` shape, `esc` display form, group-header mapping, `r`-prefix group ids all match house convention; no chord twice in scope (13 unique); pins consistent — `EXPECTED_PER_SCOPE: 13`, 13 `EXPECTED_SEAT` rows, `←`/`→` glyph-map arm, `test_fold.py`'s scoped `.toggle(` allowance names exactly the two declared files with its positive control untouched, isolation/descriptor/citation/inc9 amendments each enumerated-by-failure as claimed |
| Read-only posture | grep over `mapper/screens/relmap/` | no `osopen`/`store`/write vocabulary; `str(exc)` appears only in the "never" docstring (`screen.py:113`) |
| Source-file count | `git show 8be99a3 --stat` | 4 source files, matching the §2 ⚠ (the seat, package `__init__`, host, and the D1 surface as one landing) |

UX walkthrough note (the limit I must declare): the walkthrough above is an **automated walkthrough through the real mechanism** (Textual's headless driver, real keys, painted frames read via the compositor) — `performed`. **Expert inspection** against the prototype chrome (`prototypes/round-2026-10-23/`: crumb `reqharness / relmap / matrix · panel lens`, all-lowercase bar) — the painted chrome matches the static bar; the `+7`/`+10` truncation declarations are honest at both widths. **Evaluation with users:** *not performed — this team is one person and no user of this surface exists outside it.*

---

## 4 · Reviewer mutation battery (control C-2 — mutants of my own, not the author's 11)

Every mutant: applied → run → restored → **restore sha256 verified against the pre-mutant digest**.

| Id | Site | Change | Instruments run | Verdict |
|---|---|---|---|---|
| M-REV-1 | `mapper/keymap.py:347` | seat `r` action `refresh` → `reload` | `test_relmap_shell.py` + `test_key_dispatch.py` (51 nodes) | **KILLED ×2** — `test_at_n03h_the_whole_seat_matches_its_specification` (the whole-seat pin caught the row) AND `test_llr_rvh_3_2_open_derives_once_and_r_rederives` (the binding no longer re-derives). Restore `319877a5…a247` MATCH |
| M-REV-2 | `mapper/screens/relmap/screen.py:281-282` | the out-of-view guard (`if _TOGGLE_HOME[kind] != self.active_view: return`) deleted | `test_relmap_shell.py -k inert` | **KILLED ×3** — all three inert-arm params RED; the toggle spy saw the off-home call. Restore `706db3ee…d2bd` MATCH |
| M-REV-3 | `mapper/screens/relmap/screen.py:257-265` | `_move_selection` gutted (body → bare `return`) | the full trio (188 nodes) | **SURVIVED — 188/188 GREEN.** No instrument can see the cursor keys die: direct evidence for F7(a). Restore MATCH |

Author's battery cross-check: the packet's 11/11 KILLED claims re-read consistently with the arms on disk (each mutant maps to a named arm; the transcripts hash-match per the re-hash table). The author's M-RVH-19 and my M-REV-2 target the same rule through different edits — agreeing verdicts, independent application.

---

## 5 · Verdict

Per the commission's scale: **iterate**.

Per the role rules' tokens: **BLOCK-UNTIL: F1, F2** — the conditional verdict; it authorises nothing. Both MAJORs are trunk-owned, both are cheapest to discharge now (before lanes 3/4/5 fork against the freeze), and neither requires touching the frozen names — F1 is one line in `_switch`; F2 is a host/contract decision about the `cursor` axis plus its AT-135 fixture reconciliation (F9). All other findings are MINOR recommendations that can fold into the same trunk pass (F3-F7, F10). The increment's evidence discipline — RED counterfactuals, re-hashable transcripts, emitted-form assertions, correction populations — verifies clean, and the D1 surface is genuinely sufficient for the matrix and sheet lanes; the gaps lane is the one that must not fork first.

| Lens | State |
|---|---|
| code | 2 MAJOR (F1, F2) + 6 MINOR open — iterate |
| security | no findings — the one sink held every hostile payload; the refusal path leaks nothing; the seat carries no write vocabulary (executed probes, §3) |
| ux | the real-mechanism walkthrough passed at both widths except the F1 chrome defect (live-proven); user evaluation not performed — one-person team, no external user of this surface |
