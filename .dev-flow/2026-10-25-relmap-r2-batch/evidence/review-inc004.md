# Independent review — Increment 004 (lane L4): the ranked-gaps renderer

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `004` (lane L4) — commit `e2f0d90` |
| Reviewer | independent increment reviewer — code + security + QA + UX lenses; authored none of this increment |
| Lenses | `agents/code-reviewer.md` · `agents/security-reviewer.md` · `agents/ux-reviewer.md`; record per `templates/increment-template.md` §4b |
| Scope reviewed | 1 source file `mapper/screens/relmap/gaps.py` (333 lines) + 2 lane test files `tests/test_relmap_gaps_view.py` (874) · `tests/test_relmap_scalecheck.py` (231); PDR conditions COND-QA-3 · COND-UX-2 · COND-SEC-1 |
| Verdict | **approve-with-nits** — 0 BLOCKER · 0 MAJOR · 3 MINOR |

---

## 1 · The key question: does the renderer really paint the host-ranked catalogue, honestly, at both widths?

The lane's load-bearing claims, each re-verified against code + tests + a live probe of my own:

1. **Painted order = `state.gaps` order, never re-sorted** (LLR-RVG.1.1). `gaps.py:254-275` iterates `state.gaps` directly; the only re-derivation is the not-computed count (`gaps.py:320-328`), which re-issues the same deterministic memoized `rank_gaps` call and touches no painted row. The oracle arm `test_rvg_1_1_rendered_order_is_the_ranked_order` asserts the painted node sequence `["y","x","h"]` (reach 9,5,0) BEFORE painting — a discriminating positive control, not a vacuous pass. The Inc-2 review's F2 (cursor axis) is discharged: the host now clamps the cursor on the per-view row axis (`row_count` at `gaps.py:226-230`), and a renderer-side out-of-range cursor degrades to "no highlight", never an `IndexError` (`gaps.py:269-270` compares equality).
2. **Chrome, chips, field band** (LLR-RVG.1.2). `gaps.py:118-159`; asserted literally on the real screen by AT-135 (`test_at135_the_ranked_gaps_screen`) — header, right note, `high 0 med 7 low 0 total 7`, `no gap node what reach status`. `test_rvg_1_2_total_chip_counts_the_rendered_rows` pins `total 40` against 40 rows + the exact `+32 above` marker — M-RVG-2's "tally from a different list" shape cannot pass.
3. **Row anatomy, cursor, no microbar** (LLR-RVG.1.3). Zero-padded rank/kind/node/sentence/`000`/severity assembled at `gaps.py:162-184` through the one sink; cursor highlight via `stylize("on #262626")` at `gaps.py:182-183`, ridden by `state.cursor`, verified unit-side for cursors 0/1/6 AND app-side with a REAL `down` press (highlight 01→02, `focus` untouched — the gaps axis is not the node axis). The microbar census asserts the absence of all eight block glyphs.
4. **Window, markers, WHAT drop rule, discipline** (LLR-RVG.1.4 / AT-137). `_window` (`gaps.py:101-115`) reserves one body row per marker and follows the cursor; the sweep (`test_relmap_scalecheck.py`) pins the ladder (WHAT drops whole between two ADJACENT widths, `WHAT_MIN = 12` honored), the 87-column ellipsis arm with reach/status columns byte-exact, the marker arithmetic `(first-1) + painted + (40-last) == 40`, and the 100k cap-scale window with `+NN above` declaring every undeclared row, at 118 AND 87. No clock is read anywhere in the sweep.
5. **By-kind** (LLR-RVG.1.5 / AT-136 + COND-UX-2). `_bands` (`gaps.py:187-194`) groups in catalogue (table) order over exactly its own members; the membership oracle arm compares per-band member id sets AND ORDER against an independent oracle grouping, on a fixture whose catalogue order is deliberately NOT row-count order — the flagged prototype misalignment cannot reproduce silently. Toggle-back is byte-identical on the serialized (text, style-run) frame through the real app.
6. **Honest zeros + not-computed** (LLR-RVG.2.3). `000` painted as computed (`gaps.py:175-177`); the budget-spent arm (`hub_map(50_000, 49_990)`) spends the shared visit budget the way another view would and asserts the exact `reach not computed: N` marker plus per-row reach tokens at BOTH window ends — data, not decoration.
7. **The one sink** (LLR-RVG.3.1 / AT-139 / COND-SEC-1). Every canon-derived segment passes `D.plain` + `base.label` (`gaps.py:74-77, 170, 173`); the AST census pins no `from_markup`/`markup=True`/`.upper()`; hostile arms run unit-level AND app-level. My own live probe (§3) confirms the behavior on the real screen.

Simplicity: the module is one straight-line assembler (helpers + 3 frame builders); no premature abstraction, no dead params, no reuse violations (the host's `base.label` is used, not re-implemented). Conventions match the sibling renderers and the house casing/vocabulary.

## 2 · Findings

### BLOCKER — none.

### MAJOR — none.

### MINOR

**F1 · MAJOR-adjacent edge only — `_budget` floors explicit heights 2–4 up to 4** · `mapper/screens/relmap/gaps.py:68-71`. `max(height if height > 1 else _DEFAULT_BODY, 4)` means an explicit viewport height of 2 or 3 paints 4 rows — one or two rows more than the channel names. Today the shipped host never sends 2–4 (mount-time sends the degenerate `1`, thereafter ≥ the real auto-height canvas at the reference class), and the declared mount-floor reconciliation (packet §1.2) is honest for `height == 1`. This is defensive code creating a theoretical overprint the LLR's "explicit heights are always respected" sentence does not quite cover. Recommend (not blocking): floor only the degenerate value, e.g. `height if height > 1 else _DEFAULT_BODY`, letting 2–3 paint 2–3.

**F2 · by-kind partial band takes are honest but unsignalled inside a band** · `mapper/screens/relmap/gaps.py:299-306`. When the band area overflows mid-band, the head + `take` members paint and the rest count into `+NN more` — correct and counted, but the split band gives no in-band declaration that its own members continue past the marker. At the reference class and the 87 sweep (4-gap fixture, 7-gap snapshot) no band ever splits; only very large single-kind catalogues hit it. Acceptable as shipped; a future amendment could reserve whole bands.

**F3 · the not-computed re-issue costs one full ranking pass per paint** · `mapper/screens/relmap/gaps.py:320-328`. Declared in packet §1.1/§5 and measured at cap scale (`0.663s`/`0.701s` per paint at 100k rows, `evidence/p3-inc004-measure.txt`) — the cost is real but bounded, memoized, and the painted rows are never re-sorted. Recorded so the join and the trunk know the D1 `gaps_not_computed` channel (if ever added) deletes this.

## 3 · Controls the reviewer re-ran (evidence states: executed)

| Control | Method | Result |
|---|---|---|
| Import provenance | `python -c "import mapper; print(mapper.__file__)"` with `PYTHONPATH=<worktree>` | resolves inside the worktree ✓ |
| Lane suite (commission's exact command) | `pytest -q -p no:cacheprovider tests/test_relmap_gaps_view.py tests/test_relmap_scalecheck.py` | **33 passed** (11.9s), matching the packet's 33 (27 + 6) ✓ |
| Evidence re-hash (C-59) | `sha256sum` of the 7 lane transcripts | all 7 MATCH the packet's declared digests (see §7) ✓ |
| COND-SEC-1 live hostile probe (reviewer-authored, `$TMP/r2-revl-l4/probe.py`) | `MapperApp(<tmp>)` + `run_test(size=(118,34))`, canon row whose id carries `HLR-[bold]x[/]` and whose title carries `[@click=app.quit]`, TAB, ESC (U+001B), U+202E; press `2`; read the composited canvas strips | `01   hlr without llr  HLR-[bold]x…  HLR-[bold]x[/] has no LLR under it: [@click=app.quit] t��[bold]…  000      med` — brackets literal PASS · click-hijack literal PASS · no raw ESC PASS · no raw TAB PASS · U+FFFD coercions present PASS · exactly one gap row PASS · no forged row PASS · no foreign style on the payload runs PASS — **ALL PASS** |
| Verdict-fidelity renders (reviewer-authored) | same probe, snapshot canon (7 gaps, 2 qualified), `run_test(size=(118,34))` and `(87,34)`, ranked + `k` by-kind, canvas export | byte-for-byte the same body the packet's `p3-inc004-measure.txt` renders show, at both widths and both modes ✓ |
| COND-QA-3 measurement basis | read of `evidence/p3-inc004-measure.txt` + grep of both lane test files for clock reads | transcript carries real timings (median 0.005s over 5 runs, recorded 10× budget 0.048s, in-app derive calls 0.005/0.004s, cap-scale build/detect/rank/paint timings); NO `time`/`perf_counter`/`monotonic` import or assert in either committed test — the budget is packet-recorded only ✓ |
| Source-file count | `git show --stat e2f0d90` | 1 source file (`gaps.py`), 2 lane test files, packet + 7 evidence files — within the ≤4 budget ✓ |
| Author's mutation battery cross-check | read of `evidence/p3-inc004-mutants.txt` | 13 KILLED + the disclosed `M-RVG-12-spec` SURVIVED (honest: the specced plain()-removal is unobservable against the one idempotent sink; the killable M-RVG-12 variant guards the real axis) + the runner's own BAD control first; per-arm restore sha256 MATCH ✓ |
| Lane tree cleanliness | `git status --porcelain` on the lane files | lane files unmodified at review end; baseline sha256 `1f44a238…6c82` restored ✓ |

UX walkthrough declaration: the walkthrough above is an **automated walkthrough through the real mechanism** (Textual headless driver, real key presses `2`/`k`/`down`, painted frames read from the compositor) — `performed`, at both reference widths and both modes. **Expert inspection** against the prototype chrome — see §5. **Evaluation with users:** *not performed — this team is one person and no user of this surface exists outside it.*

## 4 · PDR conditions this lane owns

### COND-SEC-1 (MAJOR at seal; lanes own the arms) — **DISCHARGED**

Definition: hostile canon text pushed through the REAL screen renders literally, on one row, markup inert, no injection, no row splitting — with LF+TAB in the payload vocabulary. Verification: the lane's AT-139 app arm (`test_at139_hostile_canon_through_the_app`) drives the real app with a canon-carried payload (`[bold]x[/bold]` id; ESC/U+202E/U+0007 title) and asserts literal brackets, no raw ESC, U+FFFD coercions, one gap row like the benign twin, and a style census on the payload segment. My independent probe (§3) goes further on the commission's exact vocabulary — `[@click=app.quit]` (a live binding-injection attempt), raw TAB and LF, the `[/]`-closed bracket form — and all eight checks PASS on the painted frame. What would falsify: a raw `\x1b`/`\t` in the exported strips, a second forged row, a payload-attributable style run, or the click string consumed as markup. None observed.

### COND-QA-3 (MINOR): the 10× budget is a measurement, never an assertion — **DISCHARGED**

Definition: AT-137's open/`r` wall-clock budget stays a recorded Phase-3 measurement; the committed tests assert only deterministic arms. Verification: `evidence/p3-inc004-measure.txt` records a real 5-run median baseline (`0.005s`), derives the 10× budget (`0.048s`), measures the derivation inside the app (`derive_calls=[0.005s, 0.004s]` — ~10× under), and records the cap-scale timings; the committed sweep contains zero clock reads (grep-verified) and asserts only census arms (discipline, window arithmetic, drop-whole ladder, cap-scale row counts). The numbers support the threshold: measured derivation ≈ 0.004–0.005s vs the 0.048s recorded budget. What would falsify: a `time` import/assert in a committed test (absent), or a claim with no measured number behind it (all packet claims trace to the transcript).

### COND-UX-2 (MINOR): per-band membership oracle in AT-136 — **DISCHARGED**

Definition: add a per-band membership arm so the flagged band/row misalignment cannot ship. Verification: `test_rvg_1_5_by_kind_bands_match_the_membership_oracle` parses the painted by-kind frame back into (kind, member (kind,node) list, count, worst-severity) and compares it, band by band and IN ORDER, against an independently computed oracle grouping of the ranked catalogue — on a fixture whose catalogue order (`us without at ×1, llr not verified ×2, hlr without llr ×1`) is deliberately not row-count order. A row painted under the wrong band head with correct counts would fail the member-list half. What would falsify: deleting the member comparison and asserting counts only (the pre-COND-UX-2 shape); the arm as written cannot pass under misalignment.

## 5 · Verdict fidelity vs the prototype (`prototypes/round-2026-10-23/`)

Prototype references read: `PROTOTYPE.md` (D-gaps: `gaps-ranked`/`gaps-microbar`/`gaps-by-kind` variants), `verdict-2026-10-24.json` (operator chose `gaps-ranked` + by-kind toggle; rejected the microbar — matching LLR-RVG.1.3's "count column is the only reach visual"), and the verdict PNGs `shots/png{,87}/gaps-ranked.png` + `gaps-by-kind.png`. My own live renders (§3) are the comparison target.

Per-width fidelity (ranked + by-kind, both driven live):

| Width | Result |
|---|---|
| 118×34 | **declared-deviation-accepted** — every delta against the PNG is one the packet declares in §6: Darkside lowercase vs the rejected Solari ALL-CAPS (operator verdict 2026-10-24, pinned by HLR-RVG.2); no group box/seam rules (host owns chrome); the honest 7-gap `med`/`000` skeleton vs the prototype's 8-gap fictional catalogue; space-separated chips with bold `total` and no WARN on chrome; the hint bottom-anchored in the body (no host hint channel); the crumb in the shipped host format. No undeclared deviation found. |
| 87×34 | **declared-deviation-accepted** — same declared deltas; WHAT values truncate with the single ellipsis at the swept width (the PNG shows the same behavior), `reach`/`status` columns intact, every cut declared. No undeclared deviation found. |

The declared deviations are honest — declared where they exist, absent where behavior matches (row anatomy, marker vocabulary, ellipsis behavior, chip content all match the PNG intent), and each is UX-acceptable: the casing deviation IS the operator's own verdict, the skeleton deviation is the honesty the whole batch is built around, and the chrome deviations belong to the frozen host, not this lane.

## 6 · Reviewer mutation battery (control C-2 — mutants of my own, not the author's 13)

Every arm: applied → run (the commission's exact lane command) → restored from my own saved byte copy → **restore sha256 verified against the pre-review digest** (`1f44a238…6c82`).

| Id | Site | Change (the plausible shortcut) | Verdict |
|---|---|---|---|
| M-REV-1 | `mapper/screens/relmap/gaps.py:108` | the window clamped to the first page (`at - slot // 2` → `0`) | **KILLED** (rc=1) — 5 failures: `test_at137_the_window_follows_the_cursor_at_87` · `test_at137_window_follows_the_cursor_and_declares_every_cut_row` · `test_at137_cap_scale_100k_map_renders_at_118_and_87` · `test_rvg_1_2_total_chip_counts_the_rendered_rows` · `test_rvg_1_5_toggle_word_hint_and_byte_identical_toggle_back`. Restore MATCH |
| M-REV-2 | `mapper/screens/relmap/gaps.py:328` | `_not_computed` short-circuited to `return 0` (skip the re-issue) | **KILLED** (rc=1) — `test_rvg_2_3_budget_spent_declares_not_computed`. Restore MATCH |
| M-REV-3 | `mapper/screens/relmap/gaps.py:175` | computed-zero reach rendered as `-` | **KILLED** (rc=1) — 7 failures across the `000` literal arms (`test_rvg_2_3_zero_reach_is_painted_as_computed_never_a_dash`, `test_rvg_1_3_row_anatomy_at_full_width`, the AT-135/AT-137 app arms, the sweep arms). Restore MATCH |
| M-REV-4 · bad control | — | a mutation intentionally NOT applied (anchor exists 0 times; the edit was refused, sha256 unchanged) | **SURVIVED** (rc=0, 33 passed) — the harness cannot fabricate kills; a never-applied mutation reads as SURVIVED, never KILLED |

No mutant of mine survived, so no missing-intent finding arises. The author's 13/13 + disclosed `M-RVG-12-spec` SURVIVED re-read consistently with the arms on disk.

## 7 · Traceability — evidence re-hash (C-59)

| Transcript | Declared in packet | Recomputed | Match |
|---|---|---|---|
| `evidence/p3-inc004-red-code-absent.txt` | `670e5f1b…f860df2b86f` | `670e5f1b…f860df2b86f` | ✓ |
| `evidence/p3-inc004-red-move-aside.txt` | `79f98216…7d1822e9` | `79f98216…7d1822e9` | ✓ |
| `evidence/p3-inc004-green-targeted.txt` | `b3fae32b…e3f552f91` | `b3fae32b…e3f552f91` | ✓ |
| `evidence/p3-inc004-green-guards.txt` | `44332757…9f099f732` | `44332757…9f099f732` | ✓ |
| `evidence/p3-inc004-measure.txt` | `818d8dc9…cdc6493da58` | `818d8dc9…cdc6493da58` | ✓ |
| `evidence/p3-inc004-f5-probe.txt` | `6ee1749e…dc557a118` | `6ee1749e…dc557a118` | ✓ |
| `evidence/p3-inc004-mutants.txt` | `07bacfac…f63f435f` | `07bacfac…f63f435f` | ✓ |

7/7 MATCH. RED transcripts show exit-2 collection errors at the lane files (the honest absence shape); GREEN targeted shows 33 passed; GREEN guards shows the unchanged guard set (`206 passed, 3 xfailed` per the packet; out-of-lane, not re-run here). LLR → AT → test → code traces verified per row in §1.

Out-of-lane observation (not a lane finding): at review time `tests/test_relmap_shell.py` shows as modified in `git status` and an untracked `_scratch/` exists — neither is mine; a concurrent session owns the tree outside this lane's files.

## 8 · Verdict

**approve-with-nits** — 0 BLOCKER · 0 MAJOR · 3 MINOR (F1 the `_budget` 2–4 floor, F2 mid-band split signalling, F3 the re-issue cost — all recorded, none blocking; F1 is a one-line tighten the lane or the join can take).

The renderer implements every LLR it owns with executable, discriminating oracles; the three owned PDR conditions are genuinely discharged (live-proven for COND-SEC-1 with the commission's full payload vocabulary); the packet's declared prototype deviations are honest and UX-acceptable at both widths; the evidence chain re-hashes clean; and the lane's own plus my independent mutation batteries leave no surviving shortcut.

| Lens | State |
|---|---|
| code | 3 MINOR open — approve-with-nits |
| security | no findings — the one sink held the full hostile payload through the real screen (executed probe, §3/§4) |
| qa | COND-QA-3 discharged — measurement-based, clock-free committed tests (executed, §4) |
| ux | COND-UX-2 discharged; walkthrough passed at 118 + 87, ranked + by-kind; deviations all declared and operator-backed; user evaluation not performed — one-person team, no external user of this surface |
