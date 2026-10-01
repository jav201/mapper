# Increment 032 -- Inc-9f: argument injection, fixed failure categories, home hint, palette

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `532d32e`. Authority:
`VERDICT-inc9-2026-09-30.md` section "Round 3" (`M1`, `M2` and the coordinator's Inc-9f rulings).
Amendment: `A-114` (appended to `01-requirements.md`). Findings are named `INC9F-Fn`.

## 1. What changed (per finding)

| id | Source id | Change | Evidence state |
|---|---|---|---|
| `INC9F-F1` | argument injection | `_ensure_cloned` refuses a spec starting with `-` or a `scheme::` transport helper before any process starts; the clone argv is `git clone --mirror -- <url> <target>` | executed (stub argv + real git, local) |
| `INC9F-F2` | same, `gh` side | `GitHubConnector.fetch` refuses a `-`-prefixed spec before `gh`; on `532d32e` it reached `gh repo view --branch=a/b` | executed (argv stub) |
| `INC9F-F3` | same, ref names (found while measuring) | `git log` and `git rev-list` take the ref after `--end-of-options`; a branch named `--output=marker.txt` made `git log` write that file | executed (real git, local) |
| `INC9F-F4` | `R3-CR-F7` | cache hit is `target/HEAD` as a file (a mirror is bare), then `fetch --all`; a second connect no longer re-clones | executed (real git out of lane; stub in lane) |
| `INC9F-F5` | `R3-SEC-F1` | clone has `timeout=120` (reads keep 30 s); `TimeoutExpired` is the `timed out` category, unchained (its argv holds the URL) | executed |
| `INC9F-F6` | `R3-SEC-F1`, `M2` | `_gh` and `_run_git` no longer echo stderr; one fixed category; `_run_git` also maps `CalledProcessError`, which used to escape as an unexpected error | executed |
| `INC9F-F7` | `M2` | repo screen's stage panel paints `▲ failed`, the same sentence the toast carries, and the seat's `home` hint; no progress bar after a failure | executed |
| `INC9F-F8` | `M1` | `home_hint()`: `↵ open map · or choose a door`, `open map` read from the seat | executed |
| `INC9F-F9` | `R3-CR-F3` | `HomeScreen` hands `TabStrip` the seat's `consult` key (`_home_door_key()`) | executed |
| `INC9F-F10` | `R3-UX-F1` | palette selector `-highlight`; up/down/pageup/pagedown typed in the search box move the list; `↵` runs the highlighted row | executed (real keys) |
| `INC9F-F11` | `R3-UX-F7`, `R3-CR-F2` | label column padded to the seat's widest label: keys form one column; header width stays derived, pinned under a relabelled seat | executed |
| `INC9F-F12` | `R3-CR-F1` | `_catches_exception`: a handler whose body raises does not guard; `ast.GeneratorExp` is a scope; cases X3, X3b, X4 | executed |
| `INC9F-F13` | `R3-CR-F5` | `_screen_headers`: the stale `assert tabs` message names `_TAB_ACTIONS` | executed |
| `INC9F-F14` | `R3-CR-F6` | note appended to `increment-030-seed-2.md`: "8 calls" is 7 | n/a (docs) |

## 2. Argument-injection reachability on `532d32e` (measured, local, HOME and USERPROFILE in a temp dir)

| path | result on `532d32e` |
|---|---|
| Through the connect-repo entry, `-`-prefixed text to the clone | NOT reachable: `_normalize_repo` passes it through unchanged, but `_is_url` needs `http(s)://` or `git@`, so it never reaches `_ensure_cloned` |
| Through the same entry, to `gh` | REACHABLE: `--branch=a/b` and `-x/y` give `gh repo view --branch=a/b --json ...` (argv recorded by a stub; no `gh` ran). Effect measured: a flag from typed text. Impact beyond that: not measured |
| `_ensure_cloned("--upload-pack=<harmless script>")` called directly | EXECUTED: the script ran and wrote its marker file in the temp dir. The clone failed afterwards (exit 128) |
| A branch named `--output=marker.txt` in a repository the operator connects (local path) | EXECUTED: `git log` wrote `marker.txt` in that repository. A hostile remote reaches this through the mirror clone: not run (no network); `git update-ref` accepts the name locally; `git fetch` from a hostile server was not measured |

After the fix: no marker file in any of the three, and no `git`/`gh` process for the first two.

## 3. Category table (`M2`)

| category | stderr fragments (English, lower-cased) | arm |
|---|---|---|
| `host not found` | could not resolve host; name or service not known; no such host; temporary failure in name resolution; unknown host | stub sample |
| `authentication required` | could not read username/password; authentication failed; terminal prompts disabled; permission denied; invalid username or password; http 401/403; error: 401/403; gh auth login | stub sample |
| `not found or private` | repository not found; `' not found`; does not exist; http 404; error: 404; could not resolve to a repository; does not appear to be a git repository | stub sample |
| `network unreachable` | network is unreachable; failed to connect; connection refused/timed out/reset; no route to host; couldn't connect; unable to connect; error connecting to | stub sample |
| `timed out` | `TimeoutExpired`, not stderr | stub raises |
| `unknown (exit N)` | none matched | N = 1, 128, 255 |

Order is the table's: first match wins. A stderr naming a fake profile path, a token URL and `Cloning into`
gives `could not clone 'widget': host not found` and none of those words. Not measured: git under a non-English
locale (it falls to `unknown (exit N)`; carried).

## 4. Mutant table (harness outside the repo; sha256 pinned, byte-level, verdict printed before restore, pin re-checked: OK every time)

| mutant | verdict | killed by |
|---|---|---|
| drop `--` before the clone URL | RED | `the_clone_argv_ends_options_before_the_url` |
| drop the dash refusal / drop it from `_ensure_cloned` | RED | `a_dash_url_is_refused_before_any_git_runs` |
| drop the transport-helper refusal | RED | `a_transport_helper_prefix_is_refused` |
| drop the refusal from `fetch` (the `gh` flag) | RED | `a_dash_repo_spec_never_reaches_gh` |
| drop `--end-of-options` on `log` | RED | argv census, and `a_hostile_ref_name_is_not_a_git_option` run alone |
| drop `--end-of-options` on `rev-list` | RED | argv census |
| revert the cache hit to the `.git` check | RED | `a_second_connect_fetches_instead_of_recloning` |
| drop the clone `timeout=` | RED | `a_clone_that_times_out...` |
| a timeout reported as another category | RED | same |
| echo git stderr in the clone message / echo `gh` stderr | RED | `each_failure_is_one_fixed_category`, `gh_stderr_is_never_echoed` |
| remove the `host not found` marker | RED | `each_failure_is_one_fixed_category[host not found]` |
| drop the exit code from `unknown` | RED | `an_unrecognised_failure_names_only_its_exit_code` |
| hand-written `↵ open map` in the home hint | RED | `the_home_hint_follows_a_relabelled_seat` (sentinel relabel) |
| drop the invitation | RED | `the_home_hint_names_enter_and_invites_a_door` |
| literal `"c"` back in `HomeScreen` | RED | `home_keeps_its_letters_and_active_mark_under_a_rekeyed_seat` |
| stage panel ignores the failure / failure not stored / progress bar kept / hand-written back hint | RED x4 | the stage-panel arm (the not-stored one by the toast arm first) |
| selector back to `--highlight` | RED | `the_selected_row_is_painted_with_the_selection_style` |
| arrows not forwarded / down moves two rows | RED x2 | `down_moves_the_highlight...` |
| `↵` runs the first row | RED | `enter_runs_the_highlighted_action_not_the_first` |
| label not padded | RED | `the_keys_are_one_column` |
| header width hand-written | RED | `the_label_column_starts_at_one_cell_under_any_seat[True]` |
| re-raising handler counts again / only a bare `raise` counts / generator not a scope | RED x3 | census cases X3, X3b, X4 |

## 5. Test results

| check | state |
|---|---|
| Arms committed RED first (`7834fec`), `--runxfail` on `532d32e`: 41 failed, 8 passed | executed. The 8 are controls that are green by construction: 5 argv-census judge samples, the palette-typing control, and the two `R3-CR-F2` pin params (the header width was already derived; the arm pins it and is killed by the hand-written-width mutant). The 3 census cases were RED too |
| Full lane at `3a7fa8d` (docs commit adds no code): **1610 passed, 3 xfailed, 20 deselected, 0 failed**, 21:16 | executed. Reconciled with 1558: +49 tests in `test_inc9f.py` +3 census cases = +52 |
| `ruff check .` against `532d32e`, set difference (line numbers stripped) | executed: new = none, gone = none |
| `test_fold`, `test_no_operator_paths` before this commit | executed: green |
| Real-git, local bare repository, out of lane (the lane guard refuses `git clone/fetch/push` outside the `network` marker) | executed: reconnect succeeds on the second connect; `--output=marker.txt` not written; payload not run |

Changed sealed arms (only the pins of a message value): `test_inc9d.py::test_inc9d_sec_f3_a_failed_clone_message_carries_no_local_path`
pinned `"128" in message`; the ruling `M2` replaces the exit-code wording with a category, so it pins
`"host not found"` (its stub's stderr is `Could not resolve host`). No other sealed arm changed.

## 6. Decisions and deviations (declared)

- **Clone timeout 120 s, not 30 s.** The brief says "consistent with the other git calls". A mirror clone moves
  a whole history; 30 s would fail legitimate clones that work today. The reads keep 30 s. Flip it if you disagree.
- **`--end-of-options` on `log`/`rev-list` (F3)** goes beyond "`--` before URL and target"; it is the same class,
  measured reachable, and needs git 2.24 or newer (this machine: 2.49).
- **`▲ failed` is painted with `INK`**, not `WARN`: a new `WARN` site makes `test_darkside_census` demand an
  adjudication, and the glyph and sentence carry the meaning without a hue.
- **Real-git arms stay out of the lane** because of the hermetic guard; the in-lane arms use a stub that models
  git as measured (bare mirror, second clone exits 128).
- **`timed out`** is in the fixed set because the implementer brief added it to the operator's five names.
- File count: 3 source files (`github.py`, `app.py`, `screens/palette.py`), within the cap; tests and docs uncapped.

## 7. Risks, carries, next

- **Carries.** (1) Git under a non-English locale classifies as `unknown (exit N)`; running git with `LC_ALL=C`
  would fix it (not done: scope). (2) `RepoScreen` paints the typed repo in `Static(self.repo)`, which parses
  markup (pre-existing; not measured here). (3) `fetch --all` on a cache hit still raises on timeout instead of
  using the stale mirror. (4) The palette footer does not advertise the arrows (the seat is not in this
  increment's files). (5) `ssh` URLs get only the leading-dash and `::` rules. (6) Spanish strings remain on the
  repo screen (`conectando…`, the stage names): `Inc-EN`. (7) `git fetch` from a hostile remote creating a
  `--`-named ref was not measured.
- **Next.** Review of Inc-9f; then `Inc-EN` (not started).

## Commits

`7834fec` arms (RED) · `1127242` items 1-4 · `7f37c61` items 5-7 · `f405105` items 8-9 · `3a7fa8d` items 10-11 · docs commit (this record, `A-114`, the `increment-030` note).

## Renders (outside the repo, text frames of the composited screen)

`%TEMP%\claude\...\scratchpad\inc9f\renders\` (the session scratchpad): `home-118x34.txt`, `home-87x34.txt`,
`repo-failed-118x34.txt`, `repo-failed-87x34.txt`, `palette-moved-118x34.txt`, `palette-moved-87x34.txt`.
Text frames show layout, not colour; the selection style is asserted on the composited cells by the arms.
