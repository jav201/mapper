# Increment 003 — RS2 · the review / signing screen (variant A) + the `v` door

> **Artifact language.** English.

| Field | Value |
|---|---|
| Batch | `2026-10-15-review-screen-batch` |
| Increment | `003` |
| Lane (if the batch forked) | none — one lane |
| Requirement(s) | HLR-RS.1 · HLR-RS.4 · LLR-RS.1.1–1.5 · LLR-RS.2.3 · LLR-RS.4.1 (AT-090 … AT-107 as assigned to RS2) |
| Acceptance | `AT-090` … `AT-107` (painted-frame nodes in `tests/test_review_screen.py`, 118 and 87 columns) |
| Agent | `software-dev` (DeepSeek implemented; Claude Opus finished: hang diagnosis, defects, pins, RED battery) |
| Date | `2026-10-15` |

---

## 1 · What changed

RS2 — the **screen and its seat**. `ReviewScreen` (variant A: list + detail, a "needs action"
filter preset, a fixed bottom release band, the `⁂` informative badge) opens from the home door
`v`. It paints only what the headless core hands it: ONE thread worker returns one snapshot
(identity, `verify_chain`, `load_canon`, `derive_states`, `release.evaluate`); results are applied
in `on_worker_state_changed` behind a generation + `is_attached` guard. Signing is two-key
(`b` arms with object · digest · head in ACCENT, `enter` confirms) and goes ONLY through
`signing.sign_review` on a second worker; one sign in flight; refusals paint on the hint line.
`ReviewList` is a line-based `ScrollView` whose `render_line` binds no keys and whose repaint per
cursor move is a constant window (independent of N).

Finishing work done in this session on top of the staged DeepSeek implementation (each one found
by a test that could fail, not by reading):

1. **Cursor row hidden under a horizontal scrollbar (real defect).** With ≥ window-height objects the
   list showed a horizontal scrollbar that consumed the viewport's last line, so after `down` to the
   last row the cursor row painted *under* the bar. AT-099 had passed vacuously because the detail
   pane also names the id. Fix: `overflow-x: hidden` on `ReviewList`; AT-099 now asserts the list's
   own `▸ <id>` marker.
2. **`_elide_middle` raised `AttributeError`** (`Text.slice` does not exist) whenever elision needed a
   budget > 1 cell; it was only reachable because tests ran with a mis-sized console. Rewritten cell-aware
   (`_take_cells`, `rich.cells.cell_len`).
3. **Hint width read `app.console.width`** (80 in `run_test`, whatever the terminal is live). Now
   `self.size.width` — the widget's real width — so the elision budget is the painted one.
4. **"Any other key cancels" was only true for bound keys.** `x`, `5`, `space` left the arm live and a
   later `enter` signed. One `on_key` hook now disarms before any key's own action (excluding `enter`,
   `b` (toggle in `action_sign`), `escape`/`q` (cancel in `action_home`)); the duplicate cancels in
   `_move`/`action_filter` were removed so M-RS33 has a single mechanism to kill.
5. **Armed hint at 87 columns overflowed by one cell** (`next ▸ ` + copy + 8-hex head = 88 cells even with the
   object elided to `…`), clipping the "any other key cancels" tail. The head is shown as 6 hex
   (digest stays `sha8`); AT-103 now asserts the tail in the PAINTED frame at 87.
6. **Two resting hints were copied from the roles screen but are not in §6.6** (`no repo — connect a repository …`,
   `your git identity matches no declared person — b arms nothing`). Removed (the status chip/band already say it,
   `b` answers with REFUSE-VIEWER). AT-105 is now a frozen literal census of the module, so any later
   string is a deliberate edit re-checked against §6.6.
7. `tests/test_review_screen.py` imported `signing` directly, which tripped LLR-RS.2.4's import allowlist
   (`test_sign_review_has_no_cli_or_entry_point_exposure`). The file now patches the screen's own `signing`
   binding; the allowlist is **not** widened.

## 2 · The hang (`tests/test_legend_design.py`) — not a hang

Diagnosis: the file is 60 nodes of which ~12 cost 30–47 s each (the `d2` agreement arm over atlas / mind map /
outline at two sizes, `g2`). Measured: `60 passed in 538.68 s` on the **base** tree (`git worktree add … HEAD`,
removed) and `60 passed in 538.40 s` on the RS2 tree; the slow node (`d2[atlas-140x45]`) takes 31.6 s on base
and 29.8 s on RS2. No new worker is involved: the legend harness drives `HomeScreen` and `MapScreen` only; the
`v` door is not pressed by it. The earlier "did not finish in 400 s" was the wall-clock bound of a
file whose cost is ~9 min on both trees. **Fix: none needed in product or tests.** Run it with `timeout 600`
at the very least (one file at a time), as the pin run below did.

## 3 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/review.py` | source | HLR-RS.1 · LLR-RS.1.1–1.5 · LLR-RS.2.3 | `ReviewScreen`, `ReviewList`, snapshot + sign workers, arm/confirm/cancel, filter, hint/refusal copy (§6.6), band, badge |
| `mapper/keymap.py` | source | HLR-RS.4 · LLR-RS.4.1 | `SCOPE_REVIEW`, `review` + `review-leave` groups, home door `v`, 7 review-scope rows |
| `mapper/screens/home.py` | source | HLR-RS.4 | `_DOOR_NOTES["v"]`, `action_review`, import |
| `mapper/app.py` | source | HLR-RS.4 (wiring) | `ReviewScreen` re-export + `RolesScreen, ReviewScreen { layout: vertical; }` |
| `docs/ARCHITECTURE.md` | doc | HLR-RS.4 (arq-note A5) | `screens` / `reqharness` rows + batch amendment note |
| `tests/test_review_screen.py` | test | HLR-RS.1 · HLR-RS.4 · LLR-RS.1.1 (AT-090 … AT-107) | 33 nodes (see §5) |
| `tests/test_inc9.py` · `test_inc9c.py` · `test_en5.py` · `test_keymap.py` · `test_key_dispatch.py` · `test_app_imports_used.py` · `test_darkside_census.py` · `test_mod_parity.py` | test | HLR-RS.4 · LLR-RS.4.1 (§6.3 pin list) | itemised in §4 |
| `.dev-flow/2026-10-09-modular-batch/evidence/mod_parity_118.txt` · `mod_parity_87.txt` | fixture | HLR-RS.4 | one counter line each |
| `.dev-flow/2026-10-15-review-screen-batch/evidence/rs2-red.transcript` | generated | HLR-RS.1 · HLR-RS.4 | 22-mutant RED battery |
| `.dev-flow/2026-10-15-review-screen-batch/evidence/rs2-fix-green.transcript` | generated | HLR-RS.1 · HLR-RS.4 | review follow-up GREEN line `253 passed` (sha256 `7a2e9d0fd98df0d5d6fc78f762ff1168b392b08f9c098c77a8d5aa5efed93df6`) — evidence `evidence/rs2-fix-green.transcript` (sha256 `7a2e9d0fd98df0d5d6fc78f762ff1168b392b08f9c098c77a8d5aa5efed93df6`) |
| `.dev-flow/2026-10-15-review-screen-batch/evidence/rs2-green.transcript` | generated | HLR-RS.1 · HLR-RS.4 | the final-tree GREEN gate (one line per file) |
| `.dev-flow/2026-10-15-review-screen-batch/03-increments/increment-003.md` | doc | HLR-RS.1 | this packet |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** (`review.py`, `keymap.py`, `home.py`, `app.py`) |
| Test files | 9 (uncapped) |
| Doc / fixture / generated | 5 |

## 4 · Pin moves (each also commented at its site; no assertion weakened)

| Pin | Move | Reason |
|---|---|---|
| `test_keymap.py` | `SCOPE_HOME` count 13 -> 14; `SCOPE_REVIEW: 7`; `SCOPE_REVIEW: ReviewScreen` in the scope -> screen map | the `v` door and the 7 review rows are the new seat entries |
| `test_key_dispatch.py` | `("home","v")` + 7 `("review", key)` dispatch rows | the screen's keys are dispatched through the seat |
| `test_inc9.py` | `OPENERS["ReviewScreen"]`, `CHROME_LEXICON` words (`review object sign confirm cycle filter`), `ENTRY_ROWS` rows (door + 7 review rows) | new screen + door |
| `test_inc9c.py` | home `str(exc)` line pin 175 -> 176; `doors` letter set `cpntifRv`, count 7 -> 8 | the `ReviewScreen` import above the pinned line moved it by one; the home door list gained `v` |
| `test_en5.py` | `_DOOR_NOTES`-census entry `"v": "opens the review screen"` | the door's English note |
| `test_app_imports_used.py` | `"ReviewScreen"` declared-re-export allowance | imported for the stylesheet selector and `__all__` (same convention as `RolesScreen`) |
| `test_darkside_census.py` | severity/busy sites `54 → 87`; 33 `ADJUDICATED` rows for `mapper/screens/review.py` | each of the 33 sites judged by WARN's / ALERT's declared job: refusals, not-verifiable, stale digest, unentitled, not-ready marks → ALERT (cannot proceed); `changed · review`, suspended tail, not-ready verdict → WARN (attention, nothing failed) |
| `test_mod_parity.py` + 2 goldens | home golden sha256 re-recorded (118 and 87) | the `v review` door moves the key-hint overflow counter `+9 → +10` / `+11 → +12`; verified diff = exactly that one line in each golden |

## 5 · Test results

Nodes in `tests/test_review_screen.py` (33): AT-090 (×2 widths) · AT-091 · AT-092 · AT-093 (digest/head + sign;
any-other-key cancel ×4; `b`,`down`,`enter`) · AT-094 (×2) · AT-095 (×2) · AT-096 (×2 widths, incl. ESC / U+202E / U+200B / NEL / CJK /
combining / `[bold]x[/]`) · AT-097 · AT-098 · AT-099 (2 000-object scroll; `render_line` count constant across N) ·
AT-100 · AT-101 (middle + last row) · AT-102 · AT-103 (87-col elision, 118-col painted elision, cell-budget unit) ·
AT-104 (painted ACCENT hint/row, painted ALERT refusal, token unit) · AT-105 (copy table byte-exact + frozen literal census) ·
AT-106 · AT-107 (thread recorders for chain/canon/derive/evaluate/sign; late SUCCESS on a popped screen).

GREEN lines — executed one file at a time, `env -u NO_COLOR -u TERM`, `timeout 600`, final tree:

| File | Result |
|---|---|
| `test_review_screen.py` | 33 passed (≈147 s; AT-099's 1 997 presses ≈ 110 s, constant 50 ms/press at N = 100 and N = 2 000) |
| `test_roles_screen.py` · `test_fixes_roles_thread.py` | 22 · 17 passed |
| `test_keymap.py` · `test_key_dispatch.py` · `test_help_scope.py` | 123 · 34 · 52 passed |
| `test_inc9.py` · `inc9c` · `inc9e` | 44 · 61 · 17 passed |
| `test_en5.py` · `test_en8.py` | 39 · 20 passed |
| `test_legend_design.py` | 60 passed (578.8 s in the final-tree gate; 538.4 s on the earlier RS2 tree; 538.7 s on base) |
| `test_mod_parity.py` · `darkside_census` · `app_imports_used` | 3 · 26 · 44 passed |
| `test_a3_census.py` · `repair_map_truth` · `mod_structure` · `mod_compat` | 15 · 44 · 10 · 32 passed |
| `test_no_operator_paths.py` · `mod_deps` · `arch_osopen_callers` · `requirements_canon` | 2 · 13 · 5 · 3 passed |
| `test_reqharness_*.py` (10 files) | 6 · 5 · 21 · 11 · 11 · 2 · 26 · 14 · 18 · 2 passed |

The per-file summary lines are stored as `evidence/rs2-green.transcript` (below). `ruff check` on every touched Python file → `All checks passed!`. `devflow-validate --brief` → see gate row 9.
No full suite was run (instructed).

### RED counterfactual — executed, not predicted

Every mutant: mutate → node(s) RED → restore → sha256 equal → GREEN. Transcript
`evidence/rs2-red.transcript` (sha256 `5b87d3e57995f969c8283592acfb83f476a784947a4e502c63635ed905ea1b8e`; re-pinned `2026-10-16` after the DDR C2/Q2 RED append); 22/22 restores sha256-equal.

| Mutant | RED node (all in `tests/test_review_screen.py`) |
|---|---|
| M-RS1 states recomputed in the screen | `test_at_090_…paints_the_registry` (state word on each id's own row) |
| M-RS2 preset omits `pre-reviewed` | `test_at_091_needs_action_filter_preset_…` |
| M-RS3 file string not `darkside.plain`ed | `test_at_096_…text_sinks_only` |
| M-RS4 `b` signs directly | `test_at_093_b_shows_digest_and_head_and_enter_signs…` |
| M-RS9 stale digest painted ✓ · M-RS10 band verdict hard-coded | `test_at_092_detail_pane_…` |
| M-RS11 detail pane as markup `Static(str)` | `test_at_096_…text_sinks_only` (painted detail columns, both widths) |
| M-RS12 discovery on the UI thread | `test_at_107_worker_runs_all_disk_and_git_work_off_thread` |
| M-RS13 generation / `is_attached` guard dropped | `test_at_107_late_snapshot_on_a_popped_screen_is_dropped` |
| M-RS15 cold `enter` signs | `test_at_098_cold_enter_does_nothing` |
| M-RS16 `v` row dropped from the seat | `test_at_097_review_scope_binds_through_the_seat…` |
| M-RS17 `review` group missing from `GROUP_SCOPE` | same node — RED as a collection **ERROR** (`KeyError: 'review'` at import), exit 4 |
| M-RS20 follow-the-cursor scroll removed | `test_at_099_two_thousand_objects_scroll_…` |
| M-RS21 armed `escape`/`q` leaves | `test_at_100_…` |
| M-RS25 cursor resets to row 0 after a sign | `test_at_101_…` |
| M-RS26 `ReviewList` binds `enter` | `test_at_098_cold_enter_does_nothing` |
| M-RS27 `render_line` work grows with N | `test_at_099_render_line_count_constant_across_n` |
| M-RS28 disarm-before-worker removed | `test_at_106_second_enter_while_the_sign_worker_runs_is_inert` |
| M-RS30 a string outside §6.6 ∪ prototype | `test_at_105_…` (literal census) |
| M-RS31 elision cuts the tail | `test_at_103_the_painted_armed_hint_…` + `…_elide_middle_keeps_both_ends…` (+ the 87-col node) |
| M-RS32 armed hint without ACCENT | `test_at_104_the_painted_armed_hint_and_row_carry_the_accent_token` |
| M-RS33 armed `down` does not cancel | `test_at_093_b_down_enter_writes_nothing` |

Not re-proven here (core, already RED in RS1b): M-RS5–8, M-RS14, M-RS19, M-RS22, M-RS23, M-RS29. M-RS18 / M-RS24 are RS1a.
Several first-run mutants were **GREEN** (M-RS1, 11, 13, 20, 28, 30, 31, 32, 33) — each exposed a test that could not fail; each
test was strengthened (state word per row, painted detail columns, real late-SUCCESS, list-only cursor marker, started-worker
count, literal census, painted tokens) and re-run RED.

### Reverse census — trigger family B, and A3

| Probe | Result |
|---|---|
| B1 symbols asserted by other tests | `ReviewScreen`/`SCOPE_REVIEW` appear in `test_app_imports_used`, `test_darkside_census`, `test_inc9`, `test_inc9c`, `test_keymap`, `test_reqharness_signing` (allowlist, unchanged), `test_review_screen` — all re-run GREEN above |
| B2 file moved on disk | none |
| B3 goldens capturing `home.py` | `test_mod_parity` (+2 evidence goldens, re-recorded), `test_en5`, `test_en8`, `test_inc9`, `test_inc9c` — all GREEN |
| B4 artifact consumed elsewhere | `ReviewScreen` consumed by `home.py` (door), `app.py` (re-export/CSS) only; `signing` imported by `screens/review.py` only |
| A3 interface consumed by another module | keymap additions are additive (no existing `KeyBinding` moved); `test_a3_census` GREEN |

### Evidence files

| Evidence artifact | Path | SHA-256 |
|---|---|---|
| final-tree GREEN gate (one summary line per test file, then `ruff`) | `.dev-flow/2026-10-15-review-screen-batch/evidence/rs2-green.transcript` | `bde7970f7b559d0c07691ae99d7b3cbfc42102b8107ca4f6f7727dc3e79c1dfa` |
| RED battery, 22 mutants (re-pinned `2026-10-16` after the DDR C2/Q2 RED append) | `.dev-flow/2026-10-15-review-screen-batch/evidence/rs2-red.transcript` | `5b87d3e57995f969c8283592acfb83f476a784947a4e502c63635ed905ea1b8e` |
| Review follow-up GREEN (`253 passed`) | `.dev-flow/2026-10-15-review-screen-batch/evidence/rs2-fix-green.transcript` | `7a2e9d0fd98df0d5d6fc78f762ff1168b392b08f9c098c77a8d5aa5efed93df6` |

| Field | Value |
|---|---|
| **Evidence files** | `evidence/rs2-green.transcript`, `evidence/rs2-red.transcript` |
| **Independent review** | code-reviewer — PENDING (independent of the author; verdict to be recorded here) |

## 6 · Risks

- **`test_legend_design.py` costs ~9 min per run** on both trees; a 400 s bound will always look like a hang.
- **AT-099 costs ~110 s** (1 997 real key presses at ~50 ms each; constant in N, so framework/pilot overhead, not the screen).
- **Head shown as 6 hex** in the armed hint (decision 5). If the operator wants 8, the hint needs a second line or a shorter prefix at 87.
- The roles screen still reads `app.console.width` (80 under `run_test`); the review screen deliberately does not. Not touched (convention conflict surfaced, not averaged).
- Working-tree files are CRLF (`core.autocrlf=true`); recorded shas in this packet are working-tree shas.

## 7 · Pending items / spec deviations

- Resting hints for no-repo / undeclared viewer are empty (the §6.6 table has no such copy); the status chip, band and the REFUSE-* line carry the information. Deviation from the roles-screen precedent, by §6.6.
- Independent code review of RS2 — **PENDING** (below).

## 8 · Suggested next task

Independent `code-reviewer` pass on RS2 at the commit; then P4 validation (AT-090 … AT-107 end-to-end at 118 and 87) and batch close.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 4 / 4 (§3) |
| 2 | Tests written in this same increment | ✓ | 33 nodes in `test_review_screen.py` + the pin moves |
| 3 | Layer 0 written | ✓ | `_elide_middle`, `_take_cells`, `_list_row_text`, `_hint_text` unit nodes; core layer-0 in RS1a/b |
| 4 | RED counterfactual | ✓ | 22 mutants, `evidence/rs2-red.transcript` |
| 5 | Reverse census | ✓ | B1–B4 / A3 above |
| 6 | code-reviewer passed | ⚠ | **Independent review PENDING** |
| 7 | No file from another lane touched | ✓ | one lane |
| 8 | Frozen interfaces untouched | ✓ | `signing`, `release`, `derive`, `reviews`, `chain` unchanged in this increment |
| 9 | Coverage verified on disk | ✓ | GREEN table in §5; `devflow-validate --brief` run at commit |
| 10 | Load-bearing emptiness | ✓ | AT-105 literal census; AT-093 `b,down,enter` writes 0 files; allowlist test still passes with `signing` imported only by the screen |
| 11 | Mutation verdicts | ✓ | 22 KILLED (RED), each restored sha256-equal; 9 initially-GREEN mutants drove test strengthening |
| 12 | Instrument RED-proof | ✓ | pytest nodes shown failing before passing |
| 13 | Correction population | — none |
| 14 | Emitted-form assertion | — none beyond the transcript |
| 15 | Independent review names somebody | ⚠ | PENDING |
| 16 | Evidence files | ✓ | `evidence/rs2-red.transcript` (22/22 sha256-equal restores) |

---

## 9 · Code-review follow-up (Claude Opus REQUEST-CHANGES, BLOCK-UNTIL F1/F2) — resolved

Two MED (F1, F2) and four LOW (F3–F6) findings, all fixed in `mapper/screens/review.py`
and `tests/test_darkside_census.py` / `tests/test_review_screen.py`.

| ID | Sev | Fix |
|---|---|---|
| F1 | MED | The sign worker now carries its **own token** (`_sign_gen`), the sign result is detected BEFORE the load-generation guard so a result is never dropped after a resume, and `_finish_sign` **always clears `_signing`**; a successful sign re-runs the snapshot. Reproduced: `b`, `enter`, `ctrl+p`, `escape` (bumps `_gen`), release → file written, `_signing` clears, `b`/`enter` live again. |
| F2 | MED | `exit_on_error=False` on BOTH workers (precedent `repo.py:~259`); `WorkerState.ERROR` is handled (`_handle_worker_error`) — clears `_signing`, paints REFUSE-CHAIN with the core `chain broken` status (§6.6 copy, no new string); `_sign_worker` catches `OSError` → refusal. Tests: `record_review`→`PermissionError` → refusal painted, `_signing` False, app alive; same for the snapshot worker (`load_reviews`→`PermissionError`). |
| F3 | LOW | Applying a snapshot sets `self._armed = None` (re-discovery cancels the arm). Tested via push/pop resume. |
| F4 | LOW | `test_darkside_census.py` bare `darkside.ALERT,` / `darkside.WARN,` keys replaced with distinctive per-line text (the six refusals share one `_paint_templated` line; the unentitled line and the suspended tail now carry their own text). Comment states the counts: **28 derived sites, 27 distinct keys** (the two `(" chain ", …)` lines are one concept/one key); tree total 87 → 82. |
| F5 | LOW | Refusals are built from the `_REFUSE_*` constants (`_refusal_parts` + `_paint_templated`/`_paint_chain_refusal`), not re-spelled inline; deleted unused `_filtered_rows` and `_SignIntent.viewer_id`/`role`. AT-105's frozen census updated (10 fragment literals removed, `object`/`objects`/`{role}` added). |
| F6 | LOW | `test_review_screen.py` `test_at_099_render_line_count_constant_across_n` now asserts `counts["small"] > 0` (the counter really counted). |

## 10 · UX follow-up (Claude Sonnet APPROVED WITH CONDITIONS) — resolved

| ID | Fix |
|---|---|
| U1 | A long object id truncates with `…` in the list (cell-width aware) at both widths; the selected/armed row keeps the `▸ HLR-` prefix and stays readable. |
| U2 | The list cell is ellipsized to the list column width minus a 1-cell gap, so a row never runs into the detail pane (`_list_column_width`, `_cap_line`). |
| U3 | `↵` (enter) appears ONLY while armed (then `enter sign · any other key cancel`); not armed `b` is labelled `mark reviewed` (seat label changed in `keymap.py`); `b` and `↵` hidden while signing/read-only. |
| U4 | The loading state paints the release band with the prototype heading `release readiness` and no verdict line. |
| U5 | The armed hint's head hash yields first (6 hex → 1) so a short object id stays intact at 87; only a genuinely long id elides its middle with the `enter confirms` tail intact. |

**Notices fixed:** the legend stays on one row at 87 (ellipsized tail); `registry 1 object` is singular; `b` on an empty canon is inert (no refusal with a missing name). **Not changed (operator decision later):** no success message after signing (would be new copy) — noted for the operator.

## 11 · Verification

One file at a time, `env -u NO_COLOR -u TERM`, `timeout 900`:

| File | Result |
|---|---|
| `tests/test_review_screen.py` | 48 passed (33 AT + 15 follow-up) |
| `tests/test_darkside_census.py` | 26 passed |
| `tests/test_keymap.py` · `test_key_dispatch.py` · `test_inc9c.py` · `test_a3_census.py` · `test_reqharness_signing.py` · `test_no_operator_paths.py` | 253 passed |
| `tests/test_inc9.py` · `test_help_scope.py` | 96 passed |
| `ruff check mapper/screens/review.py mapper/keymap.py tests/test_review_screen.py tests/test_darkside_census.py tests/test_key_dispatch.py tests/test_inc9.py` | All checks passed |

RED counterfactual: 9 product fixes each proven RED → restore sha256-equal → GREEN
(transcript appended to `evidence/rs2-red.transcript`; green sha256
`review.py a2e6f7c4…`, `keymap.py 99ca5738…`). F4/F6 are test-only pins (no product revert).

Files changed: `mapper/screens/review.py`, `mapper/keymap.py` (source) ·
`tests/test_review_screen.py`, `tests/test_darkside_census.py`, `tests/test_key_dispatch.py`,
`tests/test_inc9.py` (test + pin moves).

## Independent review — re-check (Claude Opus, code-reviewer)

OK to advance; BLOCK-UNTIL F1, F2 LIFTED (both repros re-run and passing; 7 key sequences tried to sign without `b` → `enter`, all wrote 0 files). LOW N1/N2 fixed by the orchestrator: the sign result is applied only for the latest sign token (N1); a worker ERROR clears `_signing` only when it is the in-flight sign worker, the current load worker paints only when no sign is in flight, stale workers are ignored (N2) — node `test_n2_a_stale_worker_error_does_not_clear_an_in_flight_sign`, RED with the guard replaced by `True`, restore sha256 equal, `tests/test_review_screen.py` 49 passed.

## Full-suite gate follow-up (orchestrator)

The first full suite after RS2 read `20 failed, 3513 passed, 24 deselected, 3 xfailed` (36 min, clean shell): every failure was in the truncator censuses (`tests/test_inc3_census.py`, `tests/test_darkside_budget.py`, LLR-COERCE.2) — RS2's `_elide_middle` and `_take_cells` are truncators and did not coerce before cutting. Fix: both coerce first through `darkside`'s one row coercion via the public `fit` at the coerced width (`_coerced`); the census set pin moves 3 → 5, itemised at its site. RED: `_coerced` returning the raw value → `19 failed, 21 passed`; restore sha256 equal; GREEN `tests/test_review_screen.py tests/test_inc3_census.py tests/test_darkside_budget.py` 89 passed. Lesson: the RS2 per-file verification list did not include the truncator censuses; the full-suite gate caught them.
