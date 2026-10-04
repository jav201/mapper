# Increment 029 — Inc-9d · security and defects from the Inc-9b/9c reviews

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `029` — Inc-9d |
| Agent | `software-dev` |
| Date | 2026-09-30 |
| Authority | `VERDICT-inc9-2026-09-30.md`, "Round 2", "Split", **Inc-9d**; `increment-027-inc9c.md`; `increment-028-seed-safety.md` (`B-77a/b`) |
| Starting state | branch `feat/ui-next-batch-02` @ `efaeb71`, `git status --porcelain` = 0 |
| Commits | `a5ddf5d` arms (RED) -> `fe935ac` factory -> `147eec7` github + worker -> `c97a0ba` hint + header -> `0ae61e6` test strength -> `cf16c10` lint -> `dedcc81` two sealed arms -> docs commit (this file, `BACKLOG.md` untouched) |
| Source files | 3 (`mapper/screens/factory.py`, `mapper/github.py`, `mapper/app.py`); cap 4 |
| Amendment | none: no threshold or rule needed a new requirement; `A-113` stays the last id taken |

Findings are named `INC9D-Fn` below when this increment found them; the reviewers' ids are kept beside the fix.

---

## 1 · What changed, finding by finding

| Finding | Change |
|---|---|
| **INC9BC-SEC-F1 / B-77a** (the BLOCK) | The office import's not-found toast painted the expanded path (`~` -> the profile). It now paints the name **as typed** (`Path(path_str).name`, not the expansion). Arm: `~/zz-inc9d-missing.docx` typed through the real keys; the profile and the account name are built from `$USERPROFILE` at run time and never printed (a failure prints a redacted toast). The factory `source` entry left `LEAK_EXCEPTIONS`; a second arm holds factory.py to zero leaks without it. |
| **L4** (operator) | The factory hint is `d edit document · i import office file · g generate office file`, built by `factory_hint()` from the seat (`hint_pair`). It replaces the `_HINT` constant. One row at 118 and 87 (measured: the painted region is one row). `0` and `q` and the movement keys are not repeated: the key bar lists them. |
| **INC9BC-SEC-F4** | `mkdir` + `shutil.copy2` in the office import sit in one `try/except Exception`; a failure is a toast naming the file and the exception type, the document is not registered, the app survives. Arm drives both halves (copy fails; `templates` mkdir fails). |
| **INC9BC-SEC-F3, github** | `git clone --mirror` failure -> `GitHubError("could not clone <name>: git clone failed (exit N)")`. No stderr (which names the absolute cache path), and no URL (which can carry credentials). |
| **B-77b** | `_repo_name_from_url` refuses a last segment that is `.`, `..`, a run of dots/spaces, empty, or contains `/`, `\` or `:` (a drive colon would also escape the cache). Measured on `efaeb71`: `https://h/o/..` made the clone target the cache's parent and a stand-in clone wrote a `HEAD` file into it. Arm snapshots the parent in a temp home. |
| **INC9BC-SEC-F3, worker** | `@work(thread=True, exit_on_error=False)`; `await worker.wait()` raises `WorkerFailed` wrapping the real error, which `on_mount` unwraps (`exc.error`). The `GitHubError` toast is reachable; any other failure reads `error inesperado: <Type>`. Arm goes through the real worker and real connector; only `git clone` is stubbed (stderr names the target path). |
| **INC9BC-UX-F3** | `map_hint()` = `j/k/h/l move · ↵ open card · / search`, from the seat (`group_header('nav')` + `hint_pair`). `DEFAULT_MAP_HINT` became that function at its four sites. |
| **INC9BC-UX-F13** (pre-existing) | `table.clear(columns=True)`. On base the recents table held 24 columns after three returns. |
| **INC9BC-CR-F1 / SEC-F2** | `_site_guarded`: a `.save` CALL is guarded only inside `_save_or_toast`, or in the body of a `try` with a handler for `Exception`/`BaseException`/bare (a tuple holding one counts) that runs in the same innermost `def`/`lambda` as the call. A bare `.save` reference is guarded only inside `_save_or_toast`. `_in_try_body` is gone. 12 synthetic cases. `getattr(store, "sa"+"ve")` stays a declared residual (`INC9C-F10`). |
| **INC9BC-CR-F2** | Sentinel arm: every seat label becomes `zz-<action>` (and every group header `zz-<group>`); the factory, map, import and repo-panel hints are rebuilt and must carry the sentinel. Needs `factory_hint()` / `map_hint()`. |
| **INC9BC-CR-F5** | `test_overflow` also asserts `charged_by_w[36] == {2, 3}`. |

### Found by this increment

| id | Finding | Disposition |
|---|---|---|
| `INC9D-F1` | The first full lane after the hint change failed two sealed arms: `test_inspector` (`"navega" in hint`) and the `test_overflow` paint-site arm (50x16: the 54-cell hint wrapped at 50 columns; the 49-cell one does not, so the arm's canvas height needs 50x15). | Fixed in `dedcc81`; re-swept widths 44-52 x heights 14-18. |
| `INC9D-F2` | Not fixed (not in scope, declared): `FactoryScreen._preview` paints `str(path)` of an office document in the preview panel (not a toast, but a painted path that is absolute when the document path is). | Carry. |
| `INC9D-F3` | Not fixed: `PAN_INERT_HINT` still reads `esta vista no se desplaza · navega con j/k/h/l` (a key hint in Spanish, `K3`). | Carry, with `Inc-EN`. |
| `INC9D-F4` | Not fixed: `git clone --mirror` has no timeout (the other git calls do); `GitHubConnector._gh` still passes `gh`'s stderr into the message. | Carry. |
| `INC9D-F5` | Consequence of B-77b, declared: an scp-style URL with no slash (`git@host:repo.git`) names `git@host:repo` and is now refused (the colon). With a slash it is unchanged. | Declared. |

## 2 · Files modified

| File | Change |
|---|---|
| `mapper/screens/factory.py` | `factory_hint()`; not-found toast; guarded copy; `group_header` import dropped |
| `mapper/github.py` | `_repo_name_from_url` refusals; clone error message |
| `mapper/app.py` | `map_hint()` + four sites; `exit_on_error=False` + `WorkerFailed` unwrap; `clear(columns=True)`; imports |
| `tests/test_inc9d.py` | new, 25 cases |
| `tests/test_g6_store_surrogates.py` | `_site_guarded`, 12 synthetic cases; `_in_try_body` removed |
| `tests/test_inc9c.py`, `tests/test_inspector.py`, `tests/test_overflow.py` | the changed-sealed-arm list below |
| this file | record |

Tests are uncapped; source is 3 of 4.

### Changed sealed arms (with justification)

| Arm | Change | Why |
|---|---|---|
| `test_inc9c.py` `LEAK_EXCEPTIONS` | the factory `source` entry removed | its purpose was the leak this increment closes; the census now holds factory.py with no excuse (stronger) |
| `test_inc9c.py::test_inc9c_k3_the_factory_import_and_map_hints_use_the_seat_word` | factory: the three actions present, `0 back to start` absent (was: also `0` and `q`); map: reads `map_hint()`, `navega` absent | `L4` ruling; `DEFAULT_MAP_HINT` is gone (builder). Net: stricter on the map word |
| `test_inspector.py::test_llr_n01_6_hintline_can_change_after_mount` | `"navega"` -> `"j/k/h/l move"` | `INC9BC-UX-F3` ruling; the arm's subject (a hint that changes after mount) is untouched |
| `test_overflow.py` paint-site PARTIAL-overlap arm | 50x16 -> 50x15, docstring re-derived | the hint is one cell-row shorter at 50 columns; same canvas height, re-swept. Not a loosened bound |
| `test_overflow.py` charge band | + `charged_by_w[36] == {2, 3}` | `INC9BC-CR-F5` (stricter) |
| `test_g6_store_surrogates.py` census | `_in_try_body` -> `_site_guarded` | `INC9BC-CR-F1` (stricter; the product tree still passes, no site needed fixing) |

## 3 · How to test

```
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest tests/test_inc9d.py tests/test_g6_store_surrogates.py -q
```

By hand: factory (`f` from home), `i`, type `~/nothing.docx`, `↵`: the toast names `nothing.docx` only. Open a map, go back
(`q`) three times: the recents header is one row. Plug a repo URL that cannot be cloned: a toast, no crash.

## 4 · Test results

### Arms first (`executed`)

`a5ddf5d` committed 27 strict-xfail arms (22 in `test_inc9d.py`, 5 census cases; its message says 23, one too many: the ordinary-URL
control passes by design). `--runxfail` on that tree (= `efaeb71` source), 27 failed / 8 passed, each for the stated reason: the tilde toast
paints the profile; the factory census holds `source`; the hint is the five-part line; `copy2` raises through the app (the
`OSError` reaches the test); the clone message carries `Cloning into bare repository '<path>'`; nine `..`-style URLs "DID
NOT RAISE"; three parent-snapshot arms show the parent gained a `HEAD`; the worker failure is `WorkerFailed` out of the app;
the map hint is `navega con ...`; the recents header has 24 columns; the sentinel arm cannot import the builders; five
census cases are accepted by the lexical rule. Output kept at `%TEMP%\inc9d\red_base.txt` (redacted).
Honest limit: the sentinel arm is RED on base for a missing builder, not for a hand-written copy; its discriminating power is
shown by mutants K3a/K3b/K3c/L4b/U2, which slip past every pre-existing arm.

### Mutants (`executed`)

Harness outside the repo (`%TEMP%\inc9d\mutants9d.py`): per mutant a sha256 pin of every touched file, byte-level edits in
each file's own line endings, the killing tests, the verdict **printed before** the restore, the pins re-checked. **37 of 37
KILLED; 37 of 37 pins matched after restore; the tree was clean afterwards.** Run on `0ae61e6`.

| # | Mutant | File | Killing arm(s) | Verdict |
|---|---|---|---|---|
| F1a | not-found toast back to the expansion | `factory.py` | `sec_f1_a_missing_tilde…`, `sec_f1_no_factory_notify…` | **KILLED** 2 |
| F1b | name taken from the expansion | `factory.py` | `sec_f1_a_missing_tilde…` | **KILLED** |
| L4a | hint repeats `0 back to start` | `factory.py` | `l4_…` x2 sizes | **KILLED** 2 |
| L4b | hint hand-written, equal to the seat today | `factory.py` | sentinel | **KILLED** — the L4 arm and the Inc-9c arm SLIP PAST |
| F4a | copy guard narrowed to `KeyError` | `factory.py` | `sec_f4…` x2 | **KILLED** 2 |
| F4b | failure toast back to `{exc}` | `factory.py` | `sec_f4…` x2 | **KILLED** 2 |
| F4c | `mkdir` moved out of the guard | `factory.py` | `sec_f4…[mkdir]` | **KILLED** |
| F4d | a failed copy still registers the document | `factory.py` | `sec_f4…` x2 | **KILLED** 2 |
| G1a | clone error carries git stderr again | `github.py` | `sec_f3_a_failed_clone…`, `…failing_fetch…` | **KILLED** 2 |
| G1b | clone error names the URL (credentials) | `github.py` | `sec_f3_a_failed_clone…` | **KILLED** |
| G1c | clone error drops the failure class | `github.py` | `sec_f3_a_failed_clone…` | **KILLED** |
| B1a | only `..` refused | `github.py` | `b77b_…refused` x5, … | **KILLED** 5 |
| B1b | dots allowed, empty refused | `github.py` | `b77b_…refused`, `…parent_unchanged` | **KILLED** 9 |
| B1c | backslash not a separator | `github.py` | `b77b_…refused[a\b]` | **KILLED** |
| B1d | drive colon not a separator | `github.py` | `b77b_…refused[C:evil]` | **KILLED** |
| W1 | worker exits the app again | `app.py` | `sec_f3_a_failing_fetch…` | **KILLED** |
| W2 | `WorkerFailed` not unwrapped | `app.py` | `sec_f3_a_failing_fetch…` | **KILLED** |
| W3 | unexpected-error toast back to `{exc}` | `app.py` | `test_inc9c…sec_f1_no_toast…`, census | **KILLED** 2 |
| U1 | map hint back to `navega con` | `app.py` | `ux_f3_the_map_rests…`, sentinel | **KILLED** |
| U2 | `move` hand-typed | `app.py` | sentinel (headers) | **KILLED** — the F3 arm SLIPS PAST |
| U3a/b/c | each of the three restore sites writes the old literal | `app.py` | `ux_f3_every_restore…` | **KILLED** 3 of 3 |
| H1 | recents `clear()` without `columns=True` | `app.py` | `ux_f13…` | **KILLED** |
| K3a | import hint hand-written (`s save map · esc back`) | `app.py` | sentinel | **KILLED** — the Inc-9c arm SLIPS PAST |
| K3b | repo panel hand-written | `app.py` | sentinel | **KILLED** — the Inc-9c arm SLIPS PAST |
| K3c | map hint hand-written | `app.py` | sentinel | **KILLED** — F3 + Inc-9c arms SLIP PAST |
| E1 | `.save` reference taken in a `try`, called after it | `app.py` | `test_g6c_f3_census…` | **KILLED** — the pre-Inc-9d census SURVIVES |
| E2 | lambda to `call_later` inside a `try` | `app.py` | census | **KILLED** — old SURVIVES |
| E3 | `try/finally`, no `except` | `app.py` | census | **KILLED** — old SURVIVES |
| E4 | handler for `OSError` alone | `app.py` | census | **KILLED** — old SURVIVES |
| E5 | def nested in the `try` body | `app.py` | census | **KILLED** — old SURVIVES |
| J1..J4 | the judge drops: same-scope, reference rule, handler kind, tuple handler | `test_g6…` | `cr_f1_the_census_judges…` | **KILLED** 4 of 4 |
| F5 | legacy header one cell shorter | `layered.py` | `test_llr_n06_3_1_the_charge_band…` (the new line) | **KILLED** — old SURVIVES |

"The old arm SURVIVES" was measured: `efaeb71`'s `test_g6_store_surrogates.py` and `test_overflow.py` run against E1-E5 and F5 as
scratch copies (deleted afterwards): `SURVIVED` 6 of 6. `E1`/`E2` are the Inc-9b/9c reviews' shapes as the task names them
(a reference called after the `try`; a `call_later` lambda); the review files are not in the repo, so that reading is mine.

### Lane, ruff, guards

- Baseline: **1485 passed, 3 xfailed, 20 deselected, 0 failed** (at `597b7fa`).
- Lane 1 (after `0ae61e6`/`cf16c10`), six sequential chunks: 1 failed in `test_inspector`, 1 in `test_overflow` — `INC9D-F1`,
  fixed in `dedcc81`; both files re-run: 91 passed.
- Lane 2 (final code tree, `dedcc81`), six sequential chunks: **1522 passed, 3 xfailed, 20 deselected, 0 failed**. Reconciliation: 1485 + 25
  (`test_inc9d.py`) + 12 (census cases) = 1522; xfailed and deselected unchanged.
- `ruff check .` at the repo root, same command, base = a local clone at `efaeb71` (26 findings; the archive without `.git`
  reads 44 because it does not honour `.gitignore`, so it was not used) vs `HEAD`: **26 and 26**; multiset difference **empty both
  ways** (the 4 `F401` in my new module were found and removed in `cf16c10`).
- `tests/test_fold.py` + `tests/test_no_operator_paths.py`: 21 passed, 3 xfailed (the pre-existing marked ones), before this commit.

## Renders (`executed`; saved OUTSIDE the repo)

`%TEMP%\claude\<project-slug>\<session>\scratchpad\renders-inc9d\` (harness `%TEMP%\inc9d\render9d.py`), SVG + text dump:
`factory_screen_{118x34,87x34}` and `home_after_three_returns_{118x34,87x34}`. Read from the dumps:

```
factory hint row, both sizes:   siguiente ▸ d edit document · i import office file · g generate office file   (one row)
home, after enter/q x3:         '▐ name' painted once at 118 and at 87
```

## 5 · Risks

- The clone message lost git's diagnosis: an operator with a bad URL sees only `exit 128`. Declared trade (the stderr names a
  local path and the URL can hold a token); a path-free classification of the failure is a later increment.
- `exit_on_error=False` applies to this worker only; any other `@work` still exits the app on failure.
- `B-77b` also refuses an scp URL with no slash (`INC9D-F5`).
- Test strength: the sentinel covers four hints; the prompt/confirm/construct footers stay literal by design (one arm each).
  The census judge does not read `except*` (`TryStar`) and not `getattr` with a computed name (`INC9C-F10`).
- Working-tree line endings are CRLF with an LF index (`core.autocrlf=true`); two files were seen flipping to LF mid-session
  (cause not found) and were normalised back; the commits themselves are LF-clean.

## 6 · Pending items

`INC9D-F2` (factory preview path), `INC9D-F3` (`PAN_INERT_HINT`), `INC9D-F4` (clone timeout, `gh` stderr), the Spanish toasts
(`Inc-EN`, `B-71`). Not started: Inc-9e.

## 7 · Suggested next task

Inc-9e (`darkside.py` L1/L2/CR-F6, `keymap.py` L3, `screens/palette.py` INC9C-F2/UX-F4), after the three reviews of Inc-9d.
