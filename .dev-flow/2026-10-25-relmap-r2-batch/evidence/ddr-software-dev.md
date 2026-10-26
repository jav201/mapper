# DDR evidence — software-dev reviewer — batch 2026-10-25-relmap-r2-batch

| Field | Value |
|---|---|
| Role | `software-dev` (independent DDR reviewer; authored none of the work under review) |
| Batch | `2026-10-25-relmap-r2-batch` — the A4 fork JOIN point (joined range `3b9eada → 7a56db7`, HEAD `d7bb95e`) |
| Date | 2026-10-26 |
| Scope | DDR §B row 3 (crossed reverse census, re-derived) · frozen-interface code pins (D1-as-amended, COND-SEC-1/2, complementing the architect) · mutation control C-2 (≥2 own mutants) |
| Record under review | `design/DDR-2026-10-25-relmap-r2-batch.md` (DRAFT) |

---

## 1 · Crossed reverse census — re-derived (DDR §B row 3)

### 1a · Lane file sets disjoint across `3b9eada → 7a56db7`

Command per window: `git diff --stat <merge>^ <merge>` (each lane merged by a single merge commit; lane content = that window).

| Lane | Merge | SOURCE files in window | Test files in window | Overlap with other lanes |
|---|---|---|---|---|
| L3 matrix | `3b9eada` | `mapper/screens/relmap/matrix.py` | `tests/test_relmap_matrix.py` (new), `tests/test_fold.py` (9-line touch) | none |
| L4 gaps | `ee39668` | `mapper/screens/relmap/gaps.py` | `tests/test_relmap_gaps_view.py` (new), `tests/test_relmap_scalecheck.py` (new) | none |
| L5 sheet | `4a9ecf8` | `mapper/screens/relmap/sheet.py` | `tests/test_relmap_sheet.py` (new) | none |
| L6 shell | `7a56db7` | `mapper/screens/home.py`, `mapper/app.py` | `tests/test_relmap_shell.py` (new), `tests/test_inc9c.py` (6-line re-pin), `tests/test_relmap_isolation.py` (7-line touch) | none |

Every window's remaining entries are `.dev-flow/` packet/evidence files (per-lane artifacts). **SOURCE sets pairwise disjoint; test files pairwise disjoint.** ✓

### 1b · Shared-tests commits — declarations verified

- `fb336ed` (follow-up, declared in DDR §B row 6): touches `tests/test_relmap_{gaps_view,matrix,sheet,shell}.py`, `tests/test_inc9c.py` + small source edits in `home.py`/`gaps.py`/`matrix.py` (12/8/5 lines). The cross-lane test touch is declared (review follow-ups, records-only code arms); it lands AFTER the joined range, at the review pass — it does not violate in-window disjointness.
- `2e83cf6` (join amendment): touches only `tests/test_darkside_census.py` (+58), `tests/test_inc9.py` (+23) + contract/ledger/PLAN records. Declared as the census amendment; it is a trunk records+census commit, not a lane merge.

### 1c · Family-B guard set green on the joined tree — run by me

Command (from worktree cwd):

```
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider \
  tests/test_darkside_census.py tests/test_inc9.py tests/test_inc9c.py tests/test_fold.py \
  tests/test_keymap.py tests/test_key_dispatch.py tests/test_repair_artifact_claims.py \
  tests/test_relmap_isolation.py tests/test_en5.py tests/test_app_imports_used.py
```

Tail:

```
................................................................         [100%]
709 passed, 3 xfailed, 1 warning in 88.45s (0:01:28)
```

Zero failures. (This is a re-derivation on the joined tree at HEAD `d7bb95e`; the DDR draft's per-lane guard claims — the `206 passed` pairs and the shell `337 passed` — are the lanes' own packets', consistent with this green.)

### 1d · Join amendment `2e83cf6` — claims verified against the pins

- **12 new severity/busy sites**: `tests/test_darkside_census.py:316-341` itemises them per site (matrix `!`/`◐`/ALERT/WARN sites :353-362, sheet sites :363-365); the count pin reads `assert len(sites) == 94` at `:516` with the comment trail `54 -> 82 -> 94` (`:504-516`). 94 − 82 = 12. ✓
- **+10 lexicon words**: `tests/test_inc9.py:392-414` `CHROME_LEXICON` carries the block `matrix gaps sheet refresh impact on lens chain by kind` (10 seat words) + the six `r`-prefixed group handles (`rview rnav rlens rchain rkind rleave`), per the comment at `:383-391`. ✓
- **13 seat rows**: `tests/test_inc9.py:727-731` `DECLARED_ADDED` lists exactly 13 `relmap` rows (`1/2/3/r/up/down/left/right/enter/c/k/q/escape`). ✓
- Amendment evidence `evidence/p3-census-amendment-green.txt`: tail `836 passed, 2 skipped, 3 xfailed … in 144.53s` — green, and the transcript is redacted (`<user>`), consistent with escaped-defect row D-2's redaction claim at the visible level. ✓

---

## 2 · Frozen-interface code pins — spot re-read (complementing the architect)

- **D1 as amended** — `mapper/screens/relmap/base.py`: module docstring (:9-47) names the amended protocol; `ViewState` (:90-105) has per-view-axis `cursor` and NO `lens` field; `RelMapView` Protocol (:108-131) carries `paint`, `row_count`, `toggle`; `PendingView` answers `row_count → 0` and `toggle → ""` (:161-162, :158-159). The one label sink `label` (:65-76) routes through `darkside.fit` (which applies `_row_text` coercion at `mapper/darkside.py:617` BEFORE `truncate` at :618-619 — coerce-then-cut, the C-10 order).
- **Per-view cursor/toggle word in the host** — `mapper/screens/relmap/screen.py`: `self._cursors = {name: 0 for name in base.VIEW_NAMES}` (:93, reset :142/:167), `self._view_state_words` per-view dict (:98), clamped move within `[0, row_count)` (:266-280, `min(max(... +step, 0), count - 1)`, no wrap), crumb reads the ACTIVE view's word (:179), `_toggle` stores per view (:302) and is inert off the chord's home view (:299-300). Matches the PDR §D D1 ruling annotation text.
- **Renderer seam census (COND-SEC-1)** — grep over the three renderers: every assembled string routes through `base.label` (matrix.py :276-561, gaps.py :122-154+, sheet.py :138-295); the only direct `darkside.fit`/`plain` uses size ids/kinds already coerced at their own row sink (:565, :270, :292-295). No renderer hands a raw descriptor string to a markup-parsing sink.
- **COND-SEC-2 posture** — `grep -n "time\.\|import time" mapper/screens/relmap/*.py` → zero matches (exit 1): no committed clock asserts anywhere in the relmap screen package. The counted-overflow mechanism is the `… +NN more` marker (`sheet.py:148`, gaps/matrix equivalents) — an honest count, not a wall clock.

---

## 3 · Mutation control C-2 — own mutants

Protocol per mutant: sha256 BEFORE (pristine copy kept in a scratch dir outside the repo, deleted after) → apply → run `tests/test_relmap_*.py` (expected RED; a GREEN mutant would be a MAJOR vacuous-arm finding) → restore from pristine copy → sha256 AFTER equal to BEFORE. Never ran the full suite; no git mutations.

| # | Mutant (frozen-surface arm it attacks) | File:line | Result | RED node ids | Restored sha256 == BEFORE? |
|---|---|---|---|---|---|
| M-SD-1 | The one label sink bypasses `fit`/`_row_text` coercion (`label` builds `Text(darkside.plain(...))` — LF/TAB survive, no width cut) — the COND-SEC-1 seam / M-RVH-15/18 arms | `mapper/screens/relmap/base.py:73` | RED — `29 failed, 523 passed` | `test_relmap_shell.py::test_llr_rvh_5_2_label_sink_coerces_before_the_cut`, `test_relmap_shell.py::test_at134_lf_tab_payload_renders_on_one_row`, `test_relmap_matrix.py::test_at134_hostile_payload_on_the_live_surface`, `test_relmap_gaps_view.py::test_rvg_3_1_hostile_payload_renders_literally_on_one_row`, + 25 width/geometry arms | YES (`e529783a…4868`) |
| M-SD-2 | Per-view toggle-word store → broadcast (one toggle writes its word into ALL views' slots) — D1-as-amended "crumb never shows another view's word" | `mapper/screens/relmap/screen.py:302` | RED — `2 failed, 550 passed` | `test_relmap_shell.py::test_review_f1_the_crumb_never_shows_another_views_state_word[118]`, `…[87]` | YES (`40ac5612…9c5c`) |
| M-SD-3 | Counted overflow dropped (viewport overflow silently truncates, `rows = shown`) — the M-RVS-12 / AT-143 counted-overflow arm | `mapper/screens/relmap/sheet.py:148` | RED — `2 failed, 550 passed` | `test_relmap_sheet.py::test_llr_rvs_6_2_overflow_is_counted_never_silent`, `test_relmap_sheet.py::test_at_143_87_column_check_and_counted_overflow` | YES (`1ff155ee…4767`) |

All three mutants RED, each killed by exactly the arm family the proposal/DDR names for that surface. No vacuous arm observed. After-restore pristine confirmation: `tests/test_relmap_text.py` → `15 passed in 2.33s` (green). `git status` clean apart from this evidence file and the two other reviewers' pre-existing untracked files.

---

## 4 · COND-SEC-1 / COND-SEC-2 dispositions (re-read the artifacts, not the DDR's summary)

- **COND-SEC-1 (MAJOR) — DISCHARGED, verified.** The seam wording `_row_text`/`fit` is the live code path: `_row_text` (`mapper/darkside.py:579-584`) maps LF/TAB/CR → single space; `fit` (:602-621) applies it before the cut (:617-619); the frozen seam text is in `base.py:42-47` and LLR-RVH.5.2's draft-time field (`01-requirements.md:827-834`, re-read); LF+TAB is in the P12 hostile vocabulary (`01-requirements.md:261` region, premise P12, re-read). The one-row arms exist and kill M-SD-1 (§3 above) — including the AT-134 LF/TAB arm the condition names. Mutant M-RVH-18's recorded kill is consistent with what my M-SD-1 demonstrates independently.
- **COND-SEC-2 (MINOR) — DISCHARGED, verified.** Packet `03-increments/increment-005.md` §COND-SEC-2 records the 100k-cap measurement (stacked BFS paint 0.164 s, ~60× inside a 10 s-class budget, "never a committed wall-clock assert"); `evidence/p3-inc005-sec2-bfs.txt:1-11` carries the measured numbers and the `… +99974 more` counted-overflow line; my grep proves no `time.` assert exists in the relmap package, and M-SD-3 proves the counted overflow (the deterministic stand-in the condition's idiom requires) is genuinely asserted.

---

## 5 · Findings

No BLOCKER. No MAJOR. One MINOR:

- **MINOR-1** — `mapper/screens/relmap/base.py:44` cites the coercion helper as ``darkside._row_text``/``fit`` at ``mapper/darkside.py:576-621``; on the current tree `_row_text` is defined at `:579` (`:576` is the `_ROW_BREAKERS` table). The same 1-3-line drift appears in the COND-SEC-1 contract citation (`01-requirements.md:827` region, "`mapper/darkside.py:576-621`"). Cosmetic citation drift only — the code path is correct and pinned by tests. Owner: next batch that touches `darkside.py` (or a records-pass). Not gate-blocking.

---

## 6 · Verdict

**`approved`** — DDR §B row 3 (crossed reverse census) re-derived green: lane file sets disjoint across `3b9eada → 7a56db7`, both shared-tests commits verified as declared, the family-B guard set (709 passed, 0 failed) run by me on the joined tree, and the join amendment `2e83cf6`'s three claims (12 sites / 94-pin, +10 lexicon words + 6 handles, 13 seat rows) verified against the committed pins. D1-as-amended, the per-view cursor/toggle store, the `_row_text`/`fit` seam and the COND-SEC-2 posture re-read in code and matching the PDR text. Three own mutants (C-2) all RED under the named arm families, all restores byte-identical. COND-SEC-1 and COND-SEC-2 discharged by my own re-read. One cosmetic MINOR (citation line drift) recorded above; it does not condition the verdict.
