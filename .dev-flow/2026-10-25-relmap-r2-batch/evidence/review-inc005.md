# Independent review — Increment 005 (lane L5): the node-sheet renderer

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `005` (lane L5) — lane commit `2d332b2`, reviewed at HEAD `da6f10b` |
| Reviewer | independent increment reviewer — code + security + UX lenses; authored none of this increment |
| Lenses | `agents/code-reviewer.md` · `agents/security-reviewer.md` · `agents/ux-reviewer.md`; record per `templates/increment-template.md` §4b |
| Scope reviewed | `mapper/screens/relmap/sheet.py` (317 lines, the only lane source file) + `tests/test_relmap_sheet.py` (1075 lines, 29 nodes) + the 9 evidence transcripts; `git show --stat 2d332b2` = 1 source + 1 test + packet/evidence |
| Verdict | **iterate** — 0 BLOCKER · 2 MAJOR (F1, F2 — both test-only gaps: the behavior is correct and probe-verified, but two reviewer mutants SURVIVED, which the commission's scale classes as MAJOR missing test intent) · 2 MINOR |

---

## 1 · The key question: does the sheet actually implement LLR-RVS.1.1–7.1 with executable oracles?

Read of `mapper/screens/relmap/sheet.py` in full against `01-requirements.md:588-701` and `01b-acceptance-design.md:156-209`. Every LLR has at least one non-vacuous oracle; traces verified LLR → AT → test → code line:

| LLR | AT | Test (tests/test_relmap_sheet.py) | Code (mapper/screens/relmap/sheet.py) |
|---|---|---|---|
| RVS.1.1 header | AT-140 | `:309` (rows/spans/no-source at 118/87/40) + `:895` pilot | `:222-229` |
| RVS.1.2 casing | AT-140/142 | `:326` (CAPS-profile disagreeing producer) + `:346` source census | `:211`, `:288` |
| RVS.2.1/2.2 sections | AT-140 | `:360` asymmetric fixture, wrong-direction mutant finds nothing | `:201-216` |
| RVS.2.3 glyph table | — | `:380` three foci, every D5 row + style assertions + wired in-cycle arm | `:58-68` |
| RVS.2.4 honest empties | AT-140 | `:459`, `:479` (MUT style, immediately under band) | `:196-197`, `:214-215` |
| RVS.3.1 hop-2 cuts | TC-RM-17 | `:510` incl. independent `neighbourhood(2)−neighbourhood(1)` per-direction oracle | `:173-174`, `:178-191` |
| RVS.3.2 stacked chain | AT-141 | `:557` synthetic 3-level + hand-wired diamond (both-sections row, `↑2`) | `:71-90`, `:205` |
| RVS.3.3 `c` toggle | AT-141 | `:593` (word+note+rows flip together) + `:930` real-key pilot | `:160-166`, `:198`, `:306-312` |
| RVS.4.1 gaps as given | AT-142 | `:620` (order-as-given, other-node empty) + `:651` (one ellipsis) + `:964` pilot | `:192-197`, `:283-303` |
| RVS.5.1 markup sink | AT-144 | `:668` (LF/TAB hostile fixture, one-row, no payload span) + `:1039` pilot | `:220-256` |
| RVS.6.1 width/audit | AT-143 | `:720` 8-arm sweep 118/87 × direct/stacked, audit injected | `:134-151`, `:241-256` |
| RVS.6.2 counted overflow | AT-143 | `:756` + black-box `:1004` (MUT style on real screen) | `:145-148` |
| RVS.7.1 read-only census | — | `:783` AST census (no osopen import/call, no `.render(`) | whole module |

Correctness pass highlights (edge/None/error paths): the notice branch paints only row 0 and returns a full blank canvas (`:137-139`, pinned by `:497`); the no-node branch paints the declared `╌╌ no nodes on record` (`:140-143`, pinned by `:488`); overflow replaces the tail with ONE counted line at `h−1` (`:145-148`, pinned at unit and black-box level); the `_render_chain` degenerate-width fallback drops the id before it ever overruns (`:266-270`); `toggle` returns `""` for `enter`/`k` (`:160-166`, pinned by `:593` and `:803`). The change-flow edge orientation (`_edge_index`/`_edge_for`, `:99-118`) re-derives the profile direction bit exactly as `build_map` does — the asymmetric fixture (VERIFIES edges stored TC→HLR) is built so a wrong-direction lookup finds nothing, and the glyph fixture covers every edge type. Nothing over-engineered; the one abstraction (`_layers`) is used by both densities and both sections.

## 2 · Findings

### BLOCKER — none.

### MAJOR

**F1 — The degenerate-height default body (`_budget`) is unpinned, and the packet claims it is pinned.**
- What: reviewer mutant M-REV-1 (delete the `height > 1 else _DEFAULT_BODY` floor, `mapper/screens/relmap/sheet.py:96`) leaves the full 29-node suite GREEN. No arm — unit or pilot — drives `h=1`; the AT pilots read the frame only after the auto-height canvas has grown, so the mount-time degenerate paint is invisible to every oracle (the closest other-lane arm, `tests/test_relmap_matrix.py:528`, pins a degenerate *narrow width*, not height 1).
- Why it matters: the packet's Load-bearing-emptiness table names "the degenerate-height convention" as a guard "pinned by the AT arms rendering the full body through the host" — that pin does not exist. The behavior itself is correct (an explicit height is always respected; the default body 24 matches the LED-2026-10-25-r2.19 convention), and the host measurement (`canvas.size.height == 1`) was recorded in the packet — but a claimed pin that a trivial one-line mutation defeats is exactly the false-confidence pattern this gate exists to catch.
- Fix (test-only): one unit arm — `paint(view_state(m, focus, h=1))` asserts 24 body rows; optionally a host arm asserting the first painted frame is non-empty. No source change.

**F2 — The stacked hop≥2 id gradation (`INK`→`MUT`) is unpinned.**
- What: reviewer mutant M-REV-2 (flatten `darkside.INK if hop == 1 else darkside.MUT` to plain INK at `mapper/screens/relmap/sheet.py:275`) leaves the full suite GREEN. `test_llr_rvs_3_2` asserts stacked row TEXT only; no style oracle covers chain-row ids.
- Why it matters: the prototype shows the dimming (`prototypes/round-2026-10-23/shots/png/sheet-stacked.png`: `↑2 REFINES HLR-N16.1` in the muted tone) and the code implements it, but nothing would redden if it were flattened — a fidelity-relevant intent with no executable encoding. No LLR statement pins the color, so this is fidelity-level, not contract-level.
- Fix (test-only): one style assertion in `test_llr_rvs_3_2` (stacked `↑2` row id carries MUT, hop-1 id carries INK).

### MINOR

**F3 — Cut-line hatch count: contract self-inconsistency, lane resolved undeclared.** LLR-RVS.3.1's Statement (`01-requirements.md:636-641`) says the cut line opens with **two** hatch chars; its own draft-time verification line cites the PNG's **four** hatch chars as governing. The lane paints two (`sheet.py:181-183,189-191`), matching the normative Statement and LLR-RVS.2.4's empty-line grammar — a defensible read, but the packet's §6 deviation list does not mention it. The DDR should ratify two (the Statement) so the ambiguity does not resurface at the join.

**F4 — AT-144's real-screen hostile arm does not carry LF/TAB.** The lane's renderer-level hostile fixture does (`tests/test_relmap_sheet.py:285-301` — TAB in a title, LF in an id/title, asserted one-row, no raw bytes), and my probe proves the shipped canon path *structurally cannot* carry them (`parse_canon` line-splits before cell parsing, `mapper/reqharness/derive.py:145`; `_collapse` normalises TAB to space, `:128-131` — probe evidence in §3). So COND-SEC-1 is discharged with evidence, but the PDR's "add LF+TAB to the hostile arms" intent for lanes 3/4/5 is only half-realised at pilot level; a one-cell comment in the AT-144 arm pointing at the renderer arm would close the traceability gap.

## 3 · Controls the reviewer re-ran (evidence states: executed)

| Control | Method | Result |
|---|---|---|
| Import provenance | `python -c "import mapper; print(mapper.__file__)"` with `PYTHONPATH=<worktree>` | resolves inside the worktree ✓ |
| Lane suite (commission's exact command) | `pytest -q -p no:cacheprovider tests/test_relmap_sheet.py` | **29 passed** (3.7s) |
| Evidence re-hash (C-59) | `sha256sum` of all 9 lane transcripts | **9/9 MATCH** the packet's declared digests (see §6) |
| Source-file count | `git show --stat 2d332b2` | 1 source file (`sheet.py`) + 1 test file + packet + 7 evidence files — within ≤4 ✓ |
| Read-only census (LLR-RVS.7.1) | grep over the lane module + the AST census arm | no `osopen`/`.render(`/store/write vocabulary; census test passes ✓ |

### COND-SEC-1 — hostile canon text through the REAL screen (reviewer probe, `$TMP/r2-revl-l5/probe_sec1.py`)

Workspace canon carried, in node labels: `[bold]x[/]`, `[@click=app.quit]`, a raw ESC byte, U+202E, BEL, and TAB; driven through `MapperApp(workspace=…)` + `run_test(size=(118,34))`, real `3` key to the sheet, frame read from the compositor. Probe output (trimmed):

```
PASS frame is 34 rows (got 34)
PASS '[bold]x[/]' literal, intact, on >=1 row
PASS '[@click=app.quit]' literal, intact, on >=1 row
PASS '[31mred' literal, intact, on >=1 row      (ESC coerced, remainder literal)
PASS 'LLR-HOST.1.[bold]X' literal, intact, on >=1 row   (hostile id, reaches row)
PASS no raw ESC byte in frame / no raw U+202E / no raw BEL / no raw TAB
PASS coerced controls visible as U+FFFD
PASS no payload-attributable ACCENT/ALERT/WARN span
PASS q leaves to Home
probe-exit=0
```

Structural LF/TAB evidence (the probe derives the map and prints title reprs): `TAB\tinside` arrives as `TAB inside` (parser-level normalisation) and LF can never reach a label (`splitlines` precedes cell parsing) — so on the shipped input surface the sheet's row seam is exercised for every byte an operator can actually type, and LF/TAB coverage lives at the renderer seam via the lane's hostile fixture, the only place they can enter. Frame row count equals the benign frame's (34) — no fabricated rows.

### COND-QA-5 — the M-RVS-9 kill is the synthetic arm, not the live one

Read-verified: `test_llr_rvs_3_3_c_toggle_flips_rows_note_and_word_together` (`:593-612`) asserts the `↑2` row appears EXACTLY when the note/word flip, on the synthetic 3-level chain; the live AT-141 arm (`:930`) additionally pins the real `c` key, crumb word, and note round-trip on the one-hop canon map (where rows are legitimately identical across densities — asserted, and the packet declares this honestly in §6 and Load-bearing emptiness). The transcript's M-RVS-9 KILLED row names exactly these two arms. What would falsify: a note-only flip passing — it cannot, the `↑2`-presence assertion is conjunctive with the note assertion on a map where stacked ≠ direct.

### COND-SEC-2 — measurement-based, reproduced

The transcript (`p3-inc005-sec2-bfs.txt`) records a real timing harness at the shipped cap: 100,000 nodes / 99,999 edges via inline `build_map`, stacked paint 0.164s vs a ~10s budget idiom, last frame line `… +99974 more`, and explicitly "never a committed wall-clock assert". I re-ran the measurement independently (same shape: inline reflexive-chain profile, 100k/99,999): `build_map 1.089s; stacked paint 0.277s; last content line '… +99974 more'; 10s-budget headroom ~36×`. The harness measures exactly what the claim says (the full-depth per-direction BFS through the D3 `up`/`down` surface + the counted overflow line), the numbers support the threshold, and no committed test asserts wall time (the sweep arms assert structural width/audit properties only). One caution surfaced for the record: `build_map` silently drops profile-invalid edges into `problems` — my first reproduction attempt produced an edgeless 100k map in 0.008s; the transcript's `+99974` line proves the lane's chain was real, but a measurement harness should assert `len(m.edges) == 99,999` before timing. Falsifier: a wall-clock assert in a committed test — absent.

## 4 · Verdict fidelity vs the prototype (real app at both widths)

Prototype baseline: `prototypes/round-2026-10-23/` — `PROTOTYPE.md`, `verdict-2026-10-24.json` (`d_ficha` → `sheet-direct`), `shots/png{,87}/sheet-{direct,stacked}.png`. Real app: `MapperApp(workspace=$TMP/r2-revl-l5/ws-ficha)` + `run_test(size=(118,34))` and `(87,34)`, real keys, frames captured from the compositor (`$TMP/r2-revl-l5/probe_fidelity.py`, frames under `$TMP/r2-revl-l5/out/`, deleted with the workspace).

Per-width result: **118 = match modulo declared deviations (all accepted) · 87 = match modulo declared deviations (all accepted) · no undeclared deviation found at either width.**

What the real frames show, against the packet's declared deviation list (§6) — every item observed and honest:

- Row 1 is the kind chip only (` LLR ` on STEP) — no `TC · tests/…` source segment (OQ-SHEET-7) ✓ declared.
- Section rows sit immediately under their band; no blank spacers, no seam line ✓ declared.
- Labels Darkside-lowercase (`↑1 refines …`) vs the PNG's caps and 10-cell type field; single-space row grammar ✓ declared.
- The `next ▸` note lives as the last sheet-body row (renderer-owned) with the verbatim strings ✓ declared.
- First-open crumb reads `ficha / relmap / sheet` (no word); after the real `c`, `sheet · stacked chain` + the stacked note, round-trip restores `direct only` (LED-2026-10-25-r2.20) ✓ declared, live-verified.
- The `+NN` cut and the crumb word are conditional (omitted at zero) ✓ declared; the canon's max reachable depth is two (HLR↔LLR only), so the `+01` cut/`↑2` rows are reachable solely on the synthetic 3-level fixture (TC-RM-17) — the packet's "Live-skeleton honesty" note is accurate, and my attempt to force a 3-level chain through the canon confirmed it cannot exist there (up-edges only from LLR id-parenting).
- Empty sections declare `╌╌ none on record` where the QuickMap prototype omitted them (OQ-SHEET-3) ✓ declared.
- Gap row grammar `! hlr without llr  <sentence>` with kind in bold ALERT; the long statement cuts with ONE trailing `…` at 87 (header `…` and gap-row `…` both visible) — matches the PNG's 87-col ellipsis behaviour; keybar truncation `… +7` (118) / `… +10` (87) matches the host behavior recorded in review-inc002.
- Honest note: the prototype's demo ficha is a TC with verifies/binds chains and a `VERIFIES WITHOUT EVIDENCE` gap; the real canon sources HLR/LLR only, so those exact rows cannot appear on a live map — a profile constraint, not a renderer deviation.

UX walkthrough declaration: automated walkthrough through the real mechanism (Textual headless driver, real keys, compositor-painted frames) — **performed** at both widths. Expert inspection against the prototype chrome — performed (structure matches modulo the declared, accepted deviations above). Evaluation with users — *not performed: this team is one person and no user of this surface exists outside it.*

## 5 · Reviewer mutation battery (control C-2 — mutants of my own, not the author's 12)

Every arm: original bytes saved to `$TMP/r2-revl-l5/orig/sheet.py.orig` (pre-review baseline `1ff155ee…d767` = current-HEAD bytes; the packet's `ebadfcf9…84c2` was the lane-worktree baseline pre-merge), applied → run → restored from the byte copy (never git) → restore sha256 verified.

| Id | Site | Change | Verdict |
|---|---|---|---|
| M-REV-1 | `mapper/screens/relmap/sheet.py:96` | `_budget` floor removed: `max(height if height > 1 else _DEFAULT_BODY, 1)` → `max(height, 1)` | **SURVIVED — 29/29 GREEN** → finding F1. Restore `1ff155ee…` MATCH |
| M-REV-2 | `mapper/screens/relmap/sheet.py:275` | chain id gradation flattened: `INK if hop == 1 else MUT` → `INK` | **SURVIVED — 29/29 GREEN** → finding F2. Restore MATCH |
| M-REV-3 | `mapper/screens/relmap/sheet.py:193` | gap node-scope filter dropped: `[g for g in gaps if g.node == focus]` → `[g for g in gaps]` | **KILLED** — `test_llr_rvs_4_1_only_the_focused_nodes_gaps_as_given` + `test_at_140_sheet_on_a_linked_llr`. Restore MATCH |
| M-REV-BC (bad control) | (same edit as M-REV-1, intentionally NOT applied) | — | **SURVIVED, rc=0, 29 passed** — the harness cannot fabricate kills; a never-applied mutation reads GREEN exactly as it must |

Author's battery cross-check: the packet's 12/12 KILLED claims re-read consistently with the arms on disk (each M-RVS-n maps to a named failing arm in `p3-inc005-mutants.txt`); the runner's own BAD control reported `M-RVS-1: rc=0 SURVIVED` + runner exit 1, and the battery re-hash matches (§6).

## 6 · Traceability — evidence transcript re-hash (C-59)

| File | Declared (packet §4) | Recomputed | Match |
|---|---|---|---|
| p3-inc005-fcheck.txt | `5b049ee7…5b87` | `5b049ee7bc246d8b70c62bed1f1f651d9795fd5037cb7a53557235fe8b725b87` | ✓ |
| p3-inc005-red-code-absent.txt | `dd42ec81…4b8` | `dd42ec813a4bd9ca386c12a0fef8a575fa9c54cde1fac27bf9522397472124b8` | ✓ |
| p3-inc005-red-move-aside.txt | `3a5cac6a…f6d` | `3a5cac6ab9c23fc5c576c40f944441a9751bd08fcd777523c42cc2331f9aff6d` | ✓ |
| p3-inc005-green-targeted.txt | `fd27e1c3…755` | `fd27e1c3d19ff99c7a3328e90e8506430caa68c2476b88c9445f3ba785947755` | ✓ |
| p3-inc005-green-guards.txt | `95c9f0a7…364` | `95c9f0a7e6d70f9f5d4b54011bda8a6e3b545da81b9ce02f44a8661180a14364` | ✓ |
| p3-inc005-mutants.txt | `fef5784d…c75` | `fef5784d5688cafd56571b340ff8bdc590fc7caa16dc408b24e911776ed58c75` | ✓ |
| p3-inc005-mutants-badcontrol.txt | `b52eba45…bc8` | `b52eba45424755d269b820e0bdb9641be02fead789f827fb675f1c0aabf1ebc8` | ✓ |
| p3-inc005-renders.txt | `2397f022…6e` | `2397f02203f2186c48ede8b35f398ed443353fa58584fd7d5e12643c8dc39d6e` | ✓ |
| p3-inc005-sec2-bfs.txt | `a10375b5…fba` | `a10375b515b1db7bf6e41d1d2a8c5df7dcd63af2ac9254b9546f573b9ee8cfba` | ✓ |

**9/9 MATCH, 0 mismatch.** Transcripts are `<user>`-redacted; excerpts above carry no identity strings.

## 7 · Verdict

Per the commission's scale: **iterate** — blocking findings **F1, F2**.

Both are test-only gaps, cheapest to discharge in this lane before the join: the behaviors are correct and probe-verified (degenerate-height default body 24; stacked hop≥2 MUT id gradation), but each of my two load-bearing mutants SURVIVED the 29-node suite, and F1's convention is explicitly *claimed* as pinned in the packet's Load-bearing-emptiness table when no oracle can see it die. Each fix is a couple of lines in `tests/test_relmap_sheet.py`; no source change is required, and nothing found questions the sheet's behavior on any LLR. The increment's evidence discipline — 9/9 re-hashable transcripts, RED counterfactuals with restore proofs, a self-BAD-controlled mutation runner, emitted-form assertions, an honest deviation list I verified pixel-class by pixel-class at both widths, and a COND-SEC-2 measurement I independently reproduced — verifies clean.

| Lens | State |
|---|---|
| code | 2 MAJOR (F1, F2 — missing test intent, fixes test-only) + 2 MINOR (F3, F4) — iterate |
| security | COND-SEC-1 executed through the real screen (13/13 probe checks, incl. structural LF/TAB evidence); COND-SEC-2 reproduced at the cap; read-only census clean — no security findings |
| ux | real-mechanism walkthrough passed at 118 and 87 modulo declared, accepted deviations; none undeclared; user evaluation not performed — one-person team, no external user of this surface |

Post-review integrity: `mapper/screens/relmap/sheet.py` restored byte-identical (sha256 `1ff155ee59ac0a0f570c75033a0bdb532610422020f7c055dd159db61d4ad767` = pre-review baseline); the tmp workspace `$TMP/r2-revl-l5` was deleted; no other repo file was written.
