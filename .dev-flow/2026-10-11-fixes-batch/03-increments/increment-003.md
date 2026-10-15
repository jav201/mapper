# Increment 003 — LLR-FX.4.1-4.4 · `The roles screen reads git on a worker thread` (B-127)

> **Owed in.** `core` ✓ · `full` ✓

| Field | Value |
|---|---|
| Batch | `2026-10-11-fixes-batch` |
| Increment | `003` |
| Lane (if the batch forked) | n/a — one lane |
| Requirement(s) | US-FX-004 · HLR-FX.4 · LLR-FX.4.1, 4.2, 4.3, 4.4 (B-127); PDR condition C3 (architecture map) |
| Acceptance | AT-087 · white-box TC-FX-4.1, 4.1b, 4.2, 4.3, 4.4 |
| Agent | `software-dev` |
| Date | `2026-10-15` |

---

## 1 · What changed

Opening the roles screen (`R`) no longer runs git on the UI thread. The three read-only git calls (`rev-parse --show-toplevel`, `config --get user.name`, `config --get user.email`) run in a Textual thread worker started at mount and at resume. The worker returns `(generation, (top, who))`; `on_worker_state_changed` (SUCCESS) applies it on the UI thread when the generation is the latest and the screen is still attached, then reads chain, pending requests and config from disk (`_load`) and paints. Until the first facts arrive the four surfaces stay as composed (empty), the cursor keys, `space`, `a` and `r` do nothing, and the key bar omits the three edit rows (subtraction; no new string). On resume the previous paint stays until the new facts arrive. Keypress-time reloads reuse the cached facts and run no git. The worker catches exactly `(OSError, ValueError, subprocess.SubprocessError, ValidationError)` and hands back the existing `no repo` facts; any other exception propagates (Textual's default `exit_on_error`). `docs/ARCHITECTURE.md` now lists `roles.py` in the `screens` row (paths, ownership, exposes) and the `mermaid` row cites this batch for the A3 contract changes.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/roles.py` | source | LLR-FX.4.1, LLR-FX.4.2, LLR-FX.4.3, LLR-FX.4.4 | `_discover` (worker body, narrow catch); `_load(top, who)` (no git); `_facts` / `_gen`; `_start_discovery`, `_discover_worker`, `on_worker_state_changed`; key guards; `_bar_groups`; module docstring |
| `docs/ARCHITECTURE.md` | doc | PDR C3 | `screens` row paths, ownership prose, exposes list; `mermaid` row amendment note |
| `tests/test_fixes_roles_thread.py` | test | HLR-FX.4 | new: 17 nodes (AT-087, 8 degradation arms, `RuntimeError` propagation, popped screen, paints-nothing, resume, latest-wins, inert keys, Esc, no-git reload) |
| `tests/test_roles_screen.py` | test | LLR-FX.4.4 | `_open_roles` waits for workers (4 lines) |
| `tests/test_a3_census.py` | test | LLR-FX.4.3 | zero-arg Textual sites 38 to 39 (below) |
| `.dev-flow/2026-10-11-fixes-batch/evidence/inc003-red.transcript` | doc | | RED/restore transcript |

Pin moves, itemised. (1) `tests/test_roles_screen.py::_open_roles` gained `await app.workers.wait_for_complete(); await pilot.pause()` (requirements premise 8: without it 6 and 12 of 22 nodes fail by timing). No assertion in that file changed. (2) `tests/test_a3_census.py`, zero-arg Textual sites, pinned 38 to 39 at both assertion sites (`test_tc_a3_the_census_cardinalities_are_PINNED` and `test_llr_n07_2_2a_the_widget_protocol_was_not_swept_into_the_migration`), with a comment block in the file naming the cause. Why: `tests/test_fixes_roles_thread.py::_painted` is ONE zero-arg `render()` of a chrome widget (hint line / key bar), a Textual widget render correctly outside the A3, shared by every node (a first draft with two inline calls derived 40; folded into one helper to move the pin by one). What keeps it honest: the census still derives the set from the tracked tree, the pin moves by exactly the one site, and the same file's untracked-source guard forced the new test file to be staged. (3) No other census moved: `test_darkside_census` (54 severity sites), `test_keymap`, `test_help_scope`, `test_mod_structure`, `test_mod_compat`, `test_no_operator_paths` pass unchanged (the new lines add no severity/busy token, no glyph, no string, no `notify`, no `str(exc)`).

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** (`mapper/reqharness/identity.py` not needed) |
| Test files | 3 (uncapped) |
| Doc files | 2 (outside the count) |

---

## 3 · How to test

```bash
cd <worktree>
env -u NO_COLOR -u TERM python -m pytest -p no:cacheprovider tests/test_fixes_roles_thread.py tests/test_roles_screen.py
env -u NO_COLOR -u TERM python -m pytest -p no:cacheprovider tests/test_roles_screen.py tests/test_fixes_roles_thread.py tests/test_reqharness_*.py tests/test_keymap.py tests/test_key_dispatch.py tests/test_help_scope.py tests/test_inc9*.py tests/test_en5.py tests/test_app.py tests/test_mod_structure.py tests/test_mod_compat.py tests/test_a3_census.py tests/test_darkside_census.py tests/test_no_operator_paths.py tests/test_repair_map_truth.py
ruff check mapper/screens/roles.py tests/test_fixes_roles_thread.py tests/test_roles_screen.py
```

---

## 4 · Test results

**GREEN line (executed):** `1731 passed, 4 deselected in 765.58s` over `test_roles_screen`, the new file, `test_reqharness_*`, `test_keymap`, `test_key_dispatch`, `test_help_scope`, `test_inc9*`, `test_en5`, `test_app`, `test_mod_structure`, `test_mod_compat`, `test_a3_census`, `test_darkside_census`, `test_no_operator_paths`, `test_repair_map_truth`; the earlier full-suite failure of `test_no_operator_paths` (increment 001) is absent on this tree. `ruff check` on the three touched Python files: `All checks passed!`

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `test_roles_discovery_failure_degrades_to_no_repo` (4 exception types x 2 seams = 8 arms), `test_roles_unexpected_discovery_exception_is_not_swallowed` (`RuntimeError` surfaces, wrapped by Textual in `WorkerFailed`), `test_roles_keypress_reload_runs_no_git`, `test_roles_escape_pops_while_gated` | passed |
| **A · white-box** TC-FX-4.1 / 4.1b / 4.2 / 4.3 / 4.4 | `core` · `full` | `test_at_087_…` (3 git tails, all off the main thread), `test_roles_popped_screen_discards_late_discovery`, `test_roles_paints_nothing_until_discovery_returns`, `test_roles_resume_keeps_previous_paint`, `test_roles_latest_discovery_wins`, `test_roles_keys_before_first_load_are_inert`, `test_roles_keypress_reload_runs_no_git` | passed |
| **B · black-box** AT-087 | `core` · `full` | `test_at_087_roles_screen_git_reads_run_off_the_ui_thread`: `R` from home with a gated `identity._run_git`; the screen is blank (status, body, band, hint line = the composed empty chrome) while git is gated; after release `chain`, `✓ verified`, `viewer subject`, the matrix and `release ready` are painted. Painted-frame assertions (C-32): the widgets' rendered text, never an `update()` argument | passed |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | M-FX8, M-FX9, M-FX10, M-FX11, M-FX13, M-FX13b, M-FX14, M-FX17, tabled below |
| Instrument | own Python harness kept outside the repo; restore checked by sha256 |
| Where it ran | my own worktree, one lane |
| Transcript | `.dev-flow/2026-10-11-fixes-batch/evidence/inc003-red.transcript` |
| Restore proven by | sha256 of `mapper/screens/roles.py` returned to the pre-mutation value after every mutant (logged `equal=True`); backup taken only after the baseline block was green (17 of 17 passed), deleted at the end (`== backups deleted`) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` |
| Arms resolved at baseline | 17 nodes named, 17 PASSED in the baseline block; verdicts read per node id, never from the exit code |
| Verdict granularity | per resolved node id |
| Arms that stayed GREEN | none of the named mutants survived |

| Mutant | Mutation (position and operation) | Nodes RED |
|---|---|---|
| M-FX8 | `on_mount` runs `_discover` synchronously on the UI thread | `test_at_087_…`, `…escape_pops_while_gated`, `…keys_before_first_load_are_inert`, `…paints_nothing_until…`, `…popped_screen_discards…`, `…unexpected_discovery_exception…` (6) |
| M-FX9 | the six `if self._facts is None: return` key guards removed | `test_roles_keys_before_first_load_are_inert` |
| M-FX10 | `_reload` re-runs `_discover` | `test_roles_keypress_reload_runs_no_git`, `test_at_087_…`, `test_roles_latest_discovery_wins` |
| M-FX11 | generation check dropped from the hand-back | `test_roles_latest_discovery_wins` |
| M-FX13 | generation and attached checks both dropped | `test_roles_popped_screen_discards_late_discovery`, `test_roles_latest_discovery_wins` |
| M-FX13b | only the attached check dropped | `test_roles_popped_screen_discards_late_discovery` |
| M-FX14 | the `try/except` removed from `_discover` | the 8 degradation arms |
| M-FX17 | `_bar_groups` always returns the full groups | `test_roles_keys_before_first_load_are_inert` |

**Deviation 1 from the requirements text, declared: `is_mounted` is replaced by `is_attached`.** LLR-FX.4.1 and the PDR name `is_mounted` as the dead-screen check. Measured on Textual 8.2.8 after `Esc` pops the screen: `is_mounted True`, `is_attached False`, `is_running False` (`Widget._is_mounted` is never reset). A guard on `is_mounted` can never fire. The hand-back checks `is_attached`; the code carries a two-line comment saying why.

**Deviation 2, declared: the popped-screen node needs a direct arm.** Textual cancels a screen's workers on unmount, so the framework alone never delivers the late SUCCESS: with M-FX13 applied and only the real flow driven, the popped-screen node stayed GREEN (first run: M-FX13 reddened only the latest-wins node). The node now also hands the dead screen a SUCCESS for its latest generation and asserts it is dropped; with that arm M-FX13 and M-FX13b both redden it. The guard in the hand-back is therefore the owned, tested behaviour, as the architect note says.

**Deviation 3, declared: the hint-line "empty" surface.** `HintLine("")` paints the chrome `next ▸ ` with no text, so "empty" is asserted against the composed empty line (`darkside.hint_line("")`), not against `""`. `HintLine.text == ""` is what the requirement means.

**Deviation 4, declared: key-bar assertion at 118 columns.** At 118 the full bar already folds `a`/`r` into `+6`, so "no `approve`/`reject` label" is true both gated and released. The gated bar is distinguished by what it does show: `esc back` (folded into the overflow when released) and the absence of `space propose change`; released it equals `darkside.keybar` over the seat's groups exactly. M-FX17 reddens the node.

| Field | Value |
|---|---|
| **RED counterfactual** | M-FX8, 9, 10, 11, 13, 13b, 14, 17 by position and operation as tabled; transcript `.dev-flow/2026-10-11-fixes-batch/evidence/inc003-red.transcript`; every restore digest equals the pre-mutation digest |

| Field | Value |
|---|---|
| **Mutation verdicts** | 8 mutants, 8 KILLED, 0 SURVIVED in the final run, 0 BAD (every anchor applied exactly once). M-FX13 SURVIVED the popped-screen node in the first run (Deviation 2) and was closed by a new arm, not by weakening the mutant. |

### Instrument RED-proof

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the node set (pytest) | the eight mutants above, planted in the production mechanism | `FAILED` per node id in the transcript |
| the gate (`_Gate`, 5 s guard) | M-FX8: the first git call lands on the main thread | `AssertionError: gate never released` after the guard (the node set fails instead of hanging) |
| the mutation harness | the first M-FX13 run | printed the popped-screen node as PASSED under M-FX13, which is how Deviation 2 was found |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown able to report a failure before its pass was believed |

### Emitted-form assertion

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the roles screen's four surfaces (`#roles-status`, `#roles-body`, `#roles-band`, hint line) rendered to text | AT-087: blank while gated; `chain`, `✓ verified`, `viewer subject`, `release ready` after release; degradation arms: `no repo` in status, body, band and hint | passed |
| the key bar (`KeyBar.render().plain`) | gated: four navigation labels and `esc back`, no `propose change`; released: equal to `darkside.keybar(groups_for_keybar(keybar_groups(SCOPE_ROLES)), width=118).plain` | passed |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 2 artifacts, each asserted against the form its producer emitted |

### Evidence files

| Evidence artifact | Path | SHA-256 |
|---|---|---|
| RED/restore transcript | `.dev-flow/2026-10-11-fixes-batch/evidence/inc003-red.transcript` | `8e09eb6497d48d9e410ec303fb141472b547140bb1662fc978fb1e5a8079a3ac` |
| review follow-up (39 passed) transcript | `.dev-flow/2026-10-11-fixes-batch/evidence/inc003-review-green.transcript` | `209aee11f601071672fa394673631abb155845592226da4c2f62e2c2027b0a5b` |

| Field | Value |
|---|---|
| **Evidence files** | 1 artifact at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: "0 bytes written, 0 notifications" while gated rests on the gated run holding no write |
| Synthetic instance of the absent case | the same keys (`space`, `a`, `r`) after release: `test_roles_keypress_reload_runs_no_git` presses them and the reload still happens (the hint reads `applied` or a pending file exists) |
| Positive control for every probe that returned an ABSENCE | `_digest` of `roles.yml` and `reqharness/pending/` is taken from the same seeded repo that does change when `space` lands after release |

### Reverse census — trigger family B (re-run at the increment cut)

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rlE "screens\.roles\|RolesScreen" tests` | `test_roles_screen` (22 nodes, green), `test_app_imports_used`, `test_inc9`, `test_keymap`, new file; none moved |
| B2 file moved on disk | `git diff --name-status --diff-filter=RD HEAD -- mapper tests` | empty |
| B3 golden captures this source | `grep -rl roles tests/goldens` | no hits |
| B4 artifact produced here consumed elsewhere | `grep -rn "screens.roles\|RolesScreen" mapper` | `app.py:37` (re-export, CSS selector), `screens/home.py:45,446` (`push_screen(RolesScreen())`): constructor unchanged |
| A3 interface consumed by another module | same grep | `RolesScreen()` signature and the four Static ids unchanged; `_load` signature changed, one caller (the screen itself), no test calls it |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes (B1-B4, A3) run with commands; 0 regressions; hits re-validated by the suite run above |

### Correction population

| Field | Value |
|---|---|
| **Correction population** | one claim corrected across sites: "`is_mounted` detects a popped screen" (requirements LLR-FX.4.1, PDR, design proposal, arq-note §3). Sites left for the orchestrator to amend: `01-requirements.md` LLR-FX.4.1 statement and negative control; `design/design-proposal.md` §3; `design/arq-note.md` §3. The code and tests are corrected here. |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence |
|---|---|---|---|
| `is_mounted` as the dead-screen guard in `roles.py` | one hit, inside the explanatory comment that says it does not work | yes | `grep -n is_mounted mapper/screens/roles.py` |

### Signed-balance test ledger

`post = base − deleted + added`: 17 added (new file), 0 deleted, 0 changed in count (`test_roles_screen.py` keeps 22 nodes).

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` (DeepSeek, independent of the author) — APPROVE-WITH-NITS, 0 HIGH / 0 MED; verified `is_attached` and the no-widget-from-thread rule against the installed Textual 8.2.8 source. L1 (the default executor's non-daemon thread keeps the PROCESS alive until the git timeout, ≤ ~30 s, after quitting mid-discovery; the app itself exits in 0.67 s) ACCEPTED as a stated residual by the orchestrator — bounded, no data loss, unreachable before B-127. L2 (`_open_roles` waited without a deadline) FIXED: `asyncio.wait_for(..., timeout=60)`; 39 passed. |

---

## 5 · Risks

- `is_attached` is False while the app is exiting, so a result arriving during shutdown is dropped; that is the intended behaviour.
- At push both `on_mount` and `on_screen_resume` start a discovery (6 git calls at open, the same 6 the synchronous code made); the generation guard makes the second win. Recorded as design item F3b, not coalesced here.
- The `_GIT_CACHE` dict in `identity.py` can be written by two concurrent discoveries with the same value: benign under the GIL; `identity.py` untouched.
- Deviation 1 means three batch documents still say `is_mounted` (see Correction population).

## 6 · Pending items / spec deviations

- Deviations 1 to 4 declared in §4.
- Independent review: recorded in §4b (APPROVE-WITH-NITS, 0 HIGH / 0 MED); reconciled at the DDR seal 2026-10-15.
- Not done, by design: no loading chrome (R4; B-128), no explicit `on_unmount` cancel (the framework does it).

## 7 · Suggested next task

Merge 003 into the fixes batch; then the batch's remaining gates (validation, close).

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1 source file (§2) |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_fixes_roles_thread.py`, `tests/test_roles_screen.py`, `tests/test_a3_census.py` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | §4 layer 0 row |
| 4 | RED counterfactual declared | `core` · `full` | ✓ | §4, transcript sha256 cited |
| 5 | Reverse census declared | `core` · `full` | ✓ | §4 reverse census |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | §4b: code-reviewer (DeepSeek) APPROVE-WITH-NITS, 0 HIGH / 0 MED |
| 7 | No file from another lane touched | all | ✓ | `git status`: roles source, ARCHITECTURE, three test files, this record, the transcript |
| 8 | Frozen interfaces untouched | all | ✓ | `RolesScreen` class name, Static ids, `SCOPE_ROLES` unchanged |
| 9 | Coverage claims verified on disk | all | ✓ | node names resolved by the baseline run (17 of 17) |
| 10 | Load-bearing emptiness declared | all | ✓ | §4 table |
| 11 | Mutation verdicts declared per arm | all | ✓ | §4 table |
| 12 | Instrument RED-proof declared | all | ✓ | §4 |
| 13 | Correction population declared | all | ✓ | §4 |
| 14 | Emitted-form assertion declared | all | ✓ | §4 |
| 15 | Independent review names somebody | all | ✓ | §4b: DeepSeek (code-reviewer), independent of the author |
| 16 | Evidence files declared | all | ✓ | §4, sha256 |
