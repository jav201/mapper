# DDR evidence — independent ux-reviewer read (trigger D1) — relmap-R2 batch

- **Role:** ux-reviewer (interaction and usability lens), dispatched at the DDR gate (A4 fork JOIN). I authored none of the work under review.
- **Batch:** `2026-10-25-relmap-r2-batch` · worktree `wt-r2`, branch `feat/relmap-r2`, HEAD `d7bb95e` (code identical to the gate tree `cdc4491`; `352063a` is records-only).
- **Date:** 2026-10-26.
- **Scope of this read:** the P4 UX walkthrough (`evidence/p4-ux-walkthrough-2026-10-26.txt`, its table in `../04-validation.md` §UX walkthrough) and the UX-relevant DDR items (§B conditions COND-UX-1/2/3, §E rows 7/8/10, §F D-1 and the prototype-drift note). DDR §B rows 1–7 are other roles' ownership and were not reviewed.

---

## Findings

| # | Severity | One line | Evidence |
|---|----------|----------|----------|
| F-1 | MINOR | COND-UX-3's repaired citation has drifted again: the contract now cites `mapper/keymap.py:432` for `palette_items`, but on this tree `palette_items` is at `mapper/keymap.py:475`; the same line cites `duplicate_chords()` at `:445`, actual `:488` — symbol names in parentheses are correct, line numbers are wrong, and no guard catches symbol-at-line drift (`tests/test_repair_artifact_claims.py:216` checks past-EOF only) | `.dev-flow/2026-10-25-relmap-r2-batch/01-requirements.md:813` vs `mapper/keymap.py:475,488`; `:785` vs `mapper/keymap.py:488` |

No BLOCKER, no MAJOR. Everything else the walkthrough and the DDR claim on the UX surface was independently reproduced by my own pilot below, including the two parked observations:

- **B-159 (badge clip) — confirmed, honestly dispositioned.** Stored Home kind cells carry the full values ` relation·reqharness ` / ` legacy ` while the painted frame shows `rel` / `leg` at 118×34 AND 87×34 (the transcript additionally notes the clip persists at 170 wide — the column width is fixed, not width-scaled). Paint-only; parked is right. (`mapper/screens/home.py` recents table; DDR §E row 7.)
- **B-163 (double-painted refusal) — confirmed, honestly dispositioned.** The closed-set line `structure: refused (demo): looks binary - descriptor skipped` occurs exactly **twice** on the painted refusal frame (host notice strip + renderer body); `relmap=None`; `q` returns Home alive. (DDR §E row 10.)
- **B-160 (unsignalled mid-band split) — not re-exercised; the parked wording is honest.** My fixture has exactly 1 gap, so no by-kind band ever splits across the window; the claim "no shipped fixture splits" stands on the unit oracles (`tests/test_relmap_gaps_view.py`), which I did not re-run (not my act — see limits).
- **§F D-1 (two-hatch cut line) — RATIFIED as two.** My own paint of the sheet view over the frozen surface (synthetic 3-level chain, `LLR-T` focus) shows the cut line as exactly `╌╌ +01 more upstream at hop 2 — c shows the chain` — two hatch chars, zero-padded count, em-dash, lowercase — and the empty-line grammar as `╌╌ none on record`. Never four hatch chars. The Statement-side reading is the painted reality; the DDR draft's ratification ask is confirmed.
- **Prototype-drift note (§F) — consistent with the sealed contract.** Casing: every painted chrome string in my run is Darkside-cased (`high 0   med 1   low 0   total 1`, `hlr without llr`, `next ▸ direct feeders only …`), matching the census-pinned contracts (AT-131/AT-135/AT-141 family). Keybar: seat-derived, truncating with the declared marker — painted `… +7  ? all keys` at 118 and `… +10  ? all keys` at 87 (two spaces before `?` in paint; cosmetic). Sheet header carries no source segment (LLR-RVS.1.1). Crumb format `name / relmap / view [· toggle word]` with the per-view word; the prototype's `reach count` scene label is recorded as dropped in `03-increments/increment-004.md:77-80` — the transcript's attribution of that deviation is accurate.
- **Worker's attribution — honest.** The transcript names its driver (one script under a scratch dir), mechanism (real keys through `run_test()`, frames via `screen._compositor.render_strips()` — the repo's painted-frame idiom), fixture (outside the profile, deleted), and the PNG comparison's external dependency; `../04-validation.md` marks the run `executed` by the dev-flow worker and explicitly refuses to claim the independent read. The transcript carries no profile segment (re-scanned: the only path-like strings are `#home-recents` widget ids). Its "27 checks" matches its 27 `[PASS]` markers. Two cosmetic nits only: some `observed:` lines mix the reporter's focus readout with frame text, and the run was at HEAD `352063a` (records-only commit; code identical to `cdc4491` per the validation record's ledger) — neither overstates a claim I could not reproduce.

## My own walkthrough (the independent B-act)

**Method.** A fresh scripted pilot, authored by me, driving the REAL mechanism: `MapperApp(workspace=…)` under Textual `run_test(size=(w, 34))` at **w=118 and w=87**, real key presses (`j k enter down 1 2 3 c k r q escape`), reading the PAINTED result (`screen._compositor.render_strips()` frames and the Home `DataTable` cells), fixture workspace built from scratch under the system temp area (3 HLR + 4 LLR canon, childless `HLR-DEMO.3` ⇒ exactly 1 `med` gap; `demo.relmap.yml`; one tree map), plus a non-UTF-8 canon for the refused arm, plus an inline synthetic 3-level chain painted through the sheet's real `paint` entry for the D-1 hatch question. Environment: worktree on `PYTHONPATH`, `NO_COLOR`/`TERM` unset, `PYTHONDONTWRITEBYTECODE=1`. **61 checks, 0 failed.** Scratch dir deleted after.

### Criteria table (criterion · how exercised · painted result observed · verdict)

| Criterion | How exercised (real keys / real paint) | Painted result observed | Verdict |
|---|---|---|---|
| Home lists relation + tree rows, name-sorted, kind badges | `run_test` pilot; `#home-recents` cells + painted frame, 118 and 87 | names `['demo','legacy']`; stored cells ` relation·reqharness ` / ` legacy `; painted kind column shows `rel` / `leg` (clip) | pass (B-159 observation confirmed) |
| Open routes by kind | `j k enter` (non-default selection) on the relation row | `RelMapScreen`, crumb `demo / relmap / matrix`, keybar names matrix/gaps/sheet | pass |
| Matrix skeleton: honest declaration, window, lens heads | painted frame at 118 and 87 | `no test columns yet — the AT→test table (B-141) feeds this view`; `row → col`; `what feeds it ←` / `a change reaches →` | pass |
| Lens summary + hop counts on `down` | `down` to `HLR-DEMO.2`, painted frame | `change HLR-DEMO.2 reaches 2 nodes` · `hop 1: 2 direct · hop 2: 0 chained` (at 87: `change HLR-DEMO.2 reaches …` cut with one ellipsis) | pass |
| `enter` lens toggle channel | `enter`, painted frame, `enter` back | crumb gains/loses `· panel lens`; toggle-back frame byte-identical | pass |
| Ranked gaps: header, chips, row anatomy | `2`, painted frame | `gaps — what the record does not say`; `high 0   med 1   low 0   total 1`; `01   hlr without llr  HLR-DEMO.3    …  000  med` | pass |
| `k` by-kind bands + byte-identical toggle-back | `k`, painted frame, `k` again | crumb `· by kind`; band `hlr without llr med ×1`; ranked frame byte-identical after toggle-back | pass |
| Off-home chord inert (COND-UX-1 behaviour) | `c` pressed on the gaps view | painted frame byte-identical; no state flip | pass |
| Per-view cursor restore (D1 as amended) | gaps → `1` back to matrix | lens summary again names `HLR-DEMO.2` (matrix kept its own cursor) | pass |
| Sheet direct density + honest empties | `down down 3` on matrix | crumb `demo / relmap / sheet`; `↑1 refines HLR-DEMO.1`; `╌╌ none on record` declared empties; `next ▸ direct feeders only …` | pass |
| `c` stacked chain and back | `c`, painted frame, `c` again | crumb `· stacked chain` + engine note `… come free from the engine (§3.4 C12)`; back to `· direct only` | pass |
| `r` refresh | `r` on the sheet | still `RelMapScreen`, app running | pass |
| Leave chords | `escape`; re-enter, then `q` | both land on `HomeScreen`, app running | pass |
| 87×34: declared cuts only, chrome inside the canvas | re-drive matrix/gaps/sheet at 87 | max painted line exactly 87; declaration cut with `…`; gaps view within width; keybar truncates `… +10  ? all keys` (+7 at 118); crumb inside canvas | pass |
| Unavailable/refused state | open the relation row over a non-UTF-8 canon | closed-set `structure: refused (demo): looks binary - descriptor skipped` painted **twice** (B-163 confirmed); `relmap=None`; `q` returns Home alive | pass (B-163 observation confirmed) |
| D-1: hop-2 cut line hatch count | paint the real sheet view over a synthetic 3-level chain | `╌╌ +01 more upstream at hop 2 — c shows the chain` (two hatch chars; never four); `╌╌ none on record` | pass — two-hatch ratified |

### PNG comparison side

**not-run — verdict shots not on this tree.** The round-2026-10-23 verdict PNGs live in the separate `mapper-clean` checkout; `prototypes/round-2026-10-23` is absent here, so the worker's "MATCH against the PNGs" claims were verified **indirectly**: against the sealed contract's casing/wording pins (all confirmed on this tree, above) and against my own painted frames. binds-glyphs' "not reproducible — declared scope gap B-141" claim is corroborated by the matrix's own painted declaration.

## Conditions disposition (re-read by me, never trusting the DDR's summary)

| Condition | My re-read | Disposition |
|---|---|---|
| COND-UX-1 — declare out-of-view `enter`/`c`/`k` inert | Contract `01-requirements.md:782` (LLR-RVH.4.1 Statement) declares the inert no-op explicitly; the pinned arm `tests/test_relmap_shell.py:264` parametrizes gaps/sheet/matrix × off-home chords with byte-identical frames and names M-RVH-19; I additionally exercised the behaviour live (off-home `c` byte-inert). | **discharged — honest** |
| COND-UX-2 — per-band membership oracle arm on AT-136 | `tests/test_relmap_gaps_view.py:368` exists exactly as described: per-band member ids **and order** against the oracle grouping of `rank_gaps` output, M-RVG-7 named as the reddening mutation. | **discharged — honest** |
| COND-UX-3 — repair `screens/palette.py:432` → `keymap.py:432` | The repair landed (`01-requirements.md:813` now cites `mapper/keymap.py:432` with the symbol name, and keeps `screens/palette.py:36` — verified: the palette's seat-derived `BINDINGS` block spans `mapper/screens/palette.py:34-37`) — **but on this tree `palette_items` is at `mapper/keymap.py:475` and `duplicate_chords()` at `:488`** (contract `:785` still says `:445`). The condition closed a real stale citation; the fix was not itself line-accurate anymore by the join. | **discharged at P3 — drifted since → F-1 (MINOR), proposed owner: contract-amendment pass (docs-only), BACKLOG B-166** |

## Evaluation acts (declared, keyed to what happened)

| Act | State | Method / limits |
|---|---|---|
| Automated walkthrough | **performed** | My own 61-check scripted pilot through the REAL mechanism (`MapperApp(workspace=…)` under `run_test()`, real key presses, painted frames read via the compositor), at 118×34 and 87×34, plus the refused arm and the D-1 paint. Independent of the worker's script (written fresh; the worker's script was not consulted or reused). 0 failed. Limits: one small fixture (3 HLR + 4 LLR, 1 gap); scale/breadth carried by the AT pilots per the validation record; `export_screenshot`/PNG comparison not repeated (see above). |
| Expert inspection | **performed** | This read: the worker's transcript vs its claims (counts, attribution, drift list), the contract re-reads for COND-UX-1/2/3, the §E/§F disposition checks, adjudicated against the sealed contract's casing/wording pins. |
| Evaluation with users | **not performed — one-person team; no user of this surface exists outside the operator-author** (same declaration as R1's `ddr-ux.md`). No PII involved. |

**Explicitly not covered:** the PNG pixel comparison (shots not on this tree — see above); the B-160 mid-band split (no shipped fixture splits; unit oracles only); palette/help seat surfaces (AT-149 pins, not re-walked); performance/scale at the surface (carried by the AT-137/scale-check arms).

---

## Verdict: approved with conditions

The worker's 27-check transcript and its D1–D9 drift list support every pass verdict they claim: everything asserted on the painted surface is either independently reproduced by my own 61-check pilot at both reference widths or honestly parked (B-159, B-163) / declared out of scope (B-141, B-160) / attributed to the prototype side against contract pins I re-read myself. The one condition: **F-1** — re-pin the drifted contract citations (`mapper/keymap.py:432` → `:475` for `palette_items`; `duplicate_chords()` `:445` → `:488`) in the contract's draft-time fields; docs-only, no code; owner: the contract-amendment pass of the batch that next touches `mapper/keymap.py` (proposed BACKLOG **B-166**). Discharge: re-read at the next gate that amends the contract.
