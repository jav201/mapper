# Increment 057 -- Gate-2: the pre-merge fixes of the whole-branch gates

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `0133cfb`. Authority: `A-139` (appended to `01-requirements.md`, dated 2026-10-03) and `VERDICT-merge-2026-10-03.md` ruling `M1` (the blocker plus the MEDIUM findings; LOW to `BACKLOG.md`). Source files: 4 (`mapper/app.py`, `mapper/github.py`, `mapper/screens/factory.py`, `mapper/import_csv.py`; cap 4, no overage). Everything else is tests and docs. `state.json` was not touched. No push.

## 1. What changed

- **PR-QA-F1 (HIGH, blocker).** `HomeScreen.action_table_down` / `action_table_up` called `DataTable.cursor_down` / `cursor_up`, which do not exist in Textual 8.2.8 (`action_cursor_down` / `action_cursor_up` do). The first `j` or `k` with one map or more raised `AttributeError` and stopped the app. They call the actions now. A census over `mapper/` finds no other `.cursor_down(` / `.cursor_up(` (the other `cursor_` uses are `cursor_row` / `cursor_coordinate` reads).
- **PR-QA-F3 (MEDIUM, new on the branch).** `_pan` set the hint to `""` after a good pan, and `_clear_pan_hint` replaced only the inert hint, so `edge of the map` survived `o` / `r` / `R`. New `_resting_hint()` (the live search's hint while a query is live, else `map_hint()`); `_pan` and `_clear_pan_hint` restore it; `_clear_pan_hint` now matches both pan hints (`PAN_INERT_HINT`, and the new constant `PAN_EDGE_HINT` for the literal that appeared twice) and also runs in `action_toggle_rail`. A hint another handler declared is left alone (pinned).
- **BRANCH-SEC-F3 (MEDIUM, pre-existing).** `_run_git` puts `-c log.showSignature=false -c core.fsmonitor=false` (`_GIT_PINS`) before every subcommand, and `_last_commit_info` passes `--no-show-signature` to `git log`. `_git_env` is unchanged. Assessed (comment above `_GIT_PINS`): `diff.external` and `core.pager` are not reachable (no `diff`, no pager, no TTY); `core.sshCommand` and `remote.<n>.uploadpack` are not pinned (a local repo has no remote operation; the mirror fetch needs the operator's own ssh, and the mirror is made by this module) -> `B-94`. `tag -l`, `branch`, `rev-list`, `config --get` run no program from repo config.
- **BRANCH-SEC-F4 / PR-QA-F4 (MEDIUM).** `FactoryScreen._preview` paints the workspace-relative path (`path.relative_to(workspace.resolve()).as_posix()`, as generate does) and coerces each extracted docx line with `darkside.plain` (the existing `escape` kept, so bracket text paints as before).
- **PR-QA-F5.** `import_csv.py`: `fila-N` -> `row-N` (code and docstring). No test pinned `fila-`. The `? ` orphan prefix is untouched (`B-93`).
- **Backlog.** `B-84`..`B-94` appended after `B-83`: F5, F6, PR-QA-F6, F7, F8, F9, F10, F11, F12, the CSV root row `? Root`, and the unpinned mirror keys.

## 2. Files modified

Source (4): `mapper/app.py`, `mapper/github.py`, `mapper/screens/factory.py`, `mapper/import_csv.py`. Tests (1, new): `tests/test_gate2.py` (28 items). Docs (3): `.dev-flow/BACKLOG.md`, `01-requirements.md` (`A-139`), this record. Not staged or touched: `prototypes/`, `mapper.db`, `fixtures/.mapper/`, `fixtures/mapper.db`, `state.json`. Commits: `9f9c2a9` (arms, strict xfail), `111f775` (helper byte I/O), `a63922b` (fixes, `OPEN_STEPS` emptied, docs), then this record. Identity `gate2 <gate2@example.invalid>`; every message ends with the Co-Authored-By line; index line endings LF (`git ls-files --eol`: `i/lf` for all touched files; two files are `w/crlf` in the working tree, as before, and `autocrlf` normalises them).

## 3. How to test

`python -B -W error::SyntaxWarning -m pytest -q -rf tests/test_gate2.py` (temp HOME and USERPROFILE, git identity from environment variables, default basetemp). Manual: home with maps, `j` `j` `k`, then `↵`; open a wide map, `L` (118) or `J` (87), read the hint; `J` to `edge of the map`, then `o`.

## 4. Arms, RED/GREEN, mutants

**Arms first.** Committed as `xfail(strict=True)` keyed by `OPEN_STEPS` (the repo's convention) in `9f9c2a9`: 2 passed (pins), 26 xfailed. RED on the base: `git worktree add --detach %TEMP%/g2base 0133cfb`, the test file copied in, `--runxfail`: **26 failed, 2 passed** (the 2 passes are pins, below). Reasons read, not assumed: `AttributeError: 'DataTable' object has no attribute 'cursor_down'` / "the app stopped on 'j'"; `'' == 'j/k/h/l move ...'` after a pan; `'edge of the map' == 'j/k/h/l ...'` after `o`/`r`/`R`; `'' == 'n next ...'` in a live search; the forged-signature repo: **the trap is armed (plain `git log -1` wrote the marker) and `fetch()` wrote it too: "fetch() ran the repository's gpg.program"**; preview `'[docx] C:\...'` with no relative path; U+FFFD absent from the preview (hostile text unchanged); `['fila-1', 'fila-2', 'root']`. One helper defect was found on the way (text-mode `input=` turned the forged commit's LF into CRLF, `hash-object` refused it): fixed in `111f775`, RED re-run after. GREEN: all 28 pass on the fixed tree (`--runxfail` and plain).

| Item | Arms (real keys, 118 and 87) |
|---|---|
| F1 | 3 maps: `j` `j` `k` -> cursor 0,1,2,1, app running, `↵` opens the row under the cursor; 1 map: `j` `k` `j` `k` clamp at 0, `↵` opens it; census of `cursor_down(` / `cursor_up(` |
| F3 | after `L` (118) / `J` (87) the hint is `map_hint()` (stored and painted); `J` to the edge then `o` / `r` / `R` -> `map_hint()`; `o` then `J` (inert) then `o` / `r` -> `map_hint()`; with a live search, a pan and an edge+`o` keep the SEARCH hint; a hint another handler set survives `o` (pin) |
| SEC-F3 | local repo, `log.showSignature=true`, `gpg.program` = marker-writing script, forged `gpgsig` commit: `fetch()` makes no marker (control: the plain command does); argv pin: `-c log.showSignature=false`, `-c core.fsmonitor=false` before the subcommand, `--no-show-signature` before `--end-of-options` |
| F4 | template under the workspace: preview has `templates/plantilla.docx`, no drive colon-backslash, no colon-slash, no `Users`, not the tmp path (stored text and painted frame); a docx paragraph holding U+202E, U+009B and U+E0041 between letters paints each as U+FFFD, and none of the three is in the text or the frame (the test file writes them only as escapes) |
| F5 | CSV rows with neither id nor title -> `row-1`, `row-2`, none starting `fila` |

**Mutants** (harness outside the repo; bytes in, bytes out; sha256 of the four source files recorded before and re-checked after: all four matched; the verdict is printed before each restore):

| # | Mutant | Verdict |
|---|---|---|
| M1 / M1b | `action_cursor_down()` -> `cursor_down()`; `action_cursor_up()` -> `cursor_up()` | KILLED (f1 arms) |
| M2 | pan success sets `""` again | KILLED |
| M2b | `_clear_pan_hint` matches only `PAN_INERT_HINT` | KILLED |
| M2c | `_resting_hint` ignores a live search | KILLED |
| M2d | `action_toggle_rail` does not clear | KILLED |
| M3 | `_GIT_PINS = []` | KILLED by the argv pin only; the behavioural arm SURVIVES it, because `--no-show-signature` alone also stops `git log` (belt and braces, declared) |
| M3b / M3c | drop the `showSignature` pin / the `fsmonitor` pin | KILLED (argv pin) |
| M3d | drop `--no-show-signature` | KILLED (argv pin) |
| M3e | drop BOTH `showSignature` controls | KILLED by the behavioural arm (the marker appears) and by the pin |
| M4 / M4b | absolute path painted again / lines not coerced | KILLED |
| M5 | `row-` back to `fila-` | KILLED |

`core.fsmonitor` has no behavioural arm: `git log`, `branch`, `tag` and `rev-list` do not refresh the index, so no repo exercises it; the pin is held by the argv arm and M3c, and that limit is declared.

## 5. Renders

Home cursor (row with the cursor background marked `>>`; measured at 118x34, the same rows at 87x34; the text frame carries the cursor as a style, so the marker comes from the strip styles):

```
after start (cursor_row=0):   >> alfa   |  beta   |  gamma
after j     (cursor_row=1):      alfa   | >> beta |  gamma
after j     (cursor_row=2):      alfa   |  beta   | >> gamma
after k     (cursor_row=1):      alfa   | >> beta |  gamma     (app.is_running True at every step)
```

Map hint on the `pan` fixture (painted, from the composited frame; the `next >` prefix is the line's own glyph):

```
118x34, after L : 'next > j/k/h/l move · ↵ open card · / search'
118x34, at edge : 'next > edge of the map'
118x34, after o : 'next > j/k/h/l move · ↵ open card · / search'
87x34,  after J : 'next > j/k/h/l move · ↵ open card · / search'   (same at the edge and after o)
```

On the base the first line was blank and the third still read `edge of the map`.

## 6. Test results, risks, unmeasured, next

- Ruff: `ruff check .` base `0133cfb` 27, head 27; programmatic multiset difference over (path, code, message) EMPTY (both directions).
- `-W error::SyntaxWarning`: the four source files and the test file compile clean.
- Full default lane x2 (sequential, uninterrupted, `-rf`, the last step): section 7.
- Risks: `_pan` now restores `map_hint()` where it blanked, so a status hint another handler set before a pan is replaced on the first good pan (it was blanked before; same loss, better text). `action_toggle_rail` now clears a pan hint; `action_toggle_inspector` does not (the verdict named `R`; the inspector has the same width effect: not changed, say if wanted).
- Not measured: POSIX (the marker script is `sh`, which Git for Windows runs; `git init -b` needs git 2.28 or later); a real `gpg` binary; `core.fsmonitor` behaviourally; `remote.<n>.uploadpack` (`B-94`); the F3 arms on a terminal narrower than 87.
- Suggested next: the squash merge (`M2`); the remote branch is left alone (`M3`).

## 7. Full default lane x2 (last step)

(appended below)
