# Increment 038 -- Inc-9l: the Inc-9k review fixes and the operator's T1

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `606a13a`. Authority: the operator's Round 9, T1
(`VERDICT-inc9-2026-09-30.md`, "Decir las formas") and the coordinator's rulings for the Inc-9k code, ux and security findings.
Amendment: `A-120` (appended to `01-requirements.md`, dated 2026-10-01).

## 1. What changed

- `mapper/github.py` (the only source file with real logic; `app.py` has a one-line fix):
  - `_UNSUPPORTED` is exactly `refusing the repository: use https://host/path, git@host:path, owner/name or a local folder` (T1; echoes nothing).
  - `_is_local_path` is total (`RuntimeError`, `OSError`, `ValueError` give False) and refuses a text that starts with two characters
    each `/` or `\` BEFORE any filesystem call (UNC, `\\?\`, `\\.\`, `/\host`, `\/host`).
  - New `_classify(text)`: `_refuse_unsafe`, then local git directory, then `_is_url` plus `_repo_name_from_url`, then owner/name, else the
    sentence. `GitHubConnector.fetch` dispatches on it and `painted_repo` returns the text only if `_classify` does not raise.
  - `_fetch_gh`: the default branch, each branch name and each sha go through `urllib.parse.quote(name, safe="")` before a `gh api` path.
- `mapper/app.py`: `PlugRepoScreen._normalize_repo` takes the path of a `http(s)://github.com/` URL with `value.split("/", 3)[3]` (the check is
  case-insensitive, the old split was not: `IndexError`).
- Tests: new `tests/test_inc9l.py` (101 cases); label-only and tidy edits to `test_inc9d/g/h/i/j/k` (section 2).

## 2. Decisions and declared sealed-arm changes

Source files: 2 (`github.py`, `app.py`), as expected. Tests and docs uncapped.

Decisions:
- **`_classify` carries the clone-name check.** The six measured painted-but-refused forms were refused by `_refuse_unsafe` (`-a/b`, `-x`) or
  by `_repo_name_from_url` (`git@h:r`, `https://h/...`, `https://h/o/.git`, `https://h/o/..git`). Both are inside `_classify`, so `painted_repo` and `fetch`
  cannot drift (section 5).
- **The UNC rule is a superset of the ruling:** two leading characters each in `/\`, so `/\host` and `\/host` (which Windows reads as UNC) are refused too. A
  single leading slash or a drive path is probed as before (a pin).
- **The sha is quoted too** (`commits/{sha}/check-runs`): it is API-derived like the names. `_fetch_gh`'s `raw` commit URL for tags is not
  a name and is untouched (outside the brief).
- **`_fetch_gh` keeps its own owner/name check** (redundant with `_classify`; unchanged).
- **`CR-F6`** (the inert `.strip()` of `_normalise_url`) is left alone, as ruled.
- **Stale phrase left:** `test_inc9j.py` docstring of the upper-case-scheme pin still says the `gh` path refuses "with its own fixed sentence". Outside the brief.

Sealed-arm changes (what, why; no leak assertion is weakened):

| arm | change | justification |
|---|---|---|
| `test_inc9k::SENTENCE` (used by ~90 arms), `test_inc9d::sec_f3_s1_a_token_url...`, `test_inc9h::sec_f4_..._shows_the_name_through_plain` x2, `test_inc9i::sec_f2_userinfo...` x3, `test_inc9j::sec_f1_extra_slashes` x4 and `no_host_at_all` | the pinned sentence text -> the T1 text. LABEL ONLY | T1 |
| `test_inc9d::sec_f3_s1...`, `test_inc9i::sec_f2...` leak lists | the `"@"` entry becomes `message.count("@") == 1  # only the sentence's own git@host:path`; every other entry kept | the T1 sentence holds one `@` (from `git@host:path`) by the operator's wording; the arms already assert `message ==` the whole sentence |
| `test_inc9h::sec_f4_the_timeout_clone_message...` | `startswith("refusing the repository: ")` -> `== <the sentence>` (CR-F5) | strengthens |
| `test_inc9j::sec_f1_a_url_with_no_host_at_all...` | `startswith("refusing the repository")` -> `== <the sentence>` (CR-F5) | strengthens |
| `test_inc9h::cr_f7_a_padded_url...` | the duplicated assertion `[c[-2] for c in _clones(run)] == []` deleted (CR-F5); it repeated `_clones(run) == []` one line above | duplicate |
| `test_inc9j` docstring of `cr_f3_...` | reworded: `fetch` is the one production entry point; `_ensure_cloned` also refuses by itself (A-119 st. 5) (CR-F3) | stale text |
| the 4 `network` arms (`test_inc9g::sec_f1`, `test_inc9h::sec_f1`, `sec_f2`, `test_inc9i::cr_f1`) | `lambda _v: True` -> `lambda v: v.startswith("file://") or real_is_url(v)` | the lift accepts only the `file://` bare repos these arms clone; every other text still meets the real allow-list |

`test_inc9i` gains `from mapper import github` for the tightened patch.

## 3. Arm table (RED/GREEN)

RED: `tests/test_inc9l.py` committed as strict xfail (`b64026b`), copied into a detached `git worktree` of `606a13a` in `%TEMP%` (no stash),
`--runxfail`: **40 failed, 61 passed** (101 cases). The 61 passes are pins (green on the base). GREEN: **101 passed** on `910cba3`, `OPEN_STEPS` empty.

| arm family (`test_inc9l`) | cases | RED on `606a13a` | on HEAD |
|---|---|---|---|
| T1: the one sentence names the accepted forms and echoes nothing (5 texts) | 5 | RED x5 | green |
| T1: the refusal screen paints the sentence (118, 87) | 2 | RED x2 | green |
| SEC-F1: the predicate never raises (`RuntimeError`, `OSError`, `ValueError`) | 3 | RED x3 | green |
| SEC-F1: `fetch` refuses with the sentence, not `error inesperado` | 1 | RED | green |
| SEC-F1: typed `~nosuchuser:tok@h/o/r` with real keys reaches `RepoScreen`, app alive (real and stubbed `expanduser`, 118, 87) | 4 | RED x4 | green |
| UNC: a double-slash text touches no filesystem and is refused (9 forms, spy that blocks) | 9 | RED x9 | green |
| UNC: typed `\\host\share` with real keys paints `(unrecognised URL)` and the sentence (118, 87) | 2 | RED x2 | green |
| UNC: single slash / drive text is still probed | 4 | green (pin) | green |
| CR-F2: consistency table (section 5), painted iff `fetch` reaches a process | 52 | RED x7 | green |
| CR-F2: the table has at least 40 distinct inputs | 1 | green (pin) | green |
| CR-F1: plain directory / missing absolute / missing relative with a credential are not painted | 3 | green (pin) | green |
| OBS-1: the rewrite is case-consistent (4 forms) | 4 | RED x4 | green |
| OBS-1: lower-case forms still rewrite | 6 | green (pin) | green |
| OBS-1: `HTTPS://GITHUB.COM/o/n` typed with real keys survives (118, 87) | 2 | RED x2 | green |
| SEC-F2: branch, default branch and sha are encoded in `gh api` paths | 1 | RED | green |
| SEC-F2: a plain branch name is unchanged | 1 | green (pin) | green |
| SEC-F1: a text with a null byte is not a folder | 1 | green (pin) | green |

Reworked arms on `606a13a` (the reworked `test_inc9d/g/h/i/j/k` copied into the same worktree): **94 cases fail** (label-only: `test_inc9k` 72 + 5 + 6, `test_inc9d` 1,
`test_inc9h` 2, `test_inc9i` 3, `test_inc9j` 5); every other arm of those files is green on the base.

## 4. Mutant table

Harness `mutate9l.py` in the session scratchpad, outside the repo; run on a detached `git worktree` of `910cba3` in `%TEMP%`;
sha256 pinned before (`github.py` `32f51c5316bccf59...`, `app.py` `0f20d6b0f081e2d2...`), byte-level I/O in the file's own line ending, the verdict
printed before the file is restored, the pin re-checked after: **pin OK**, both runs. `old` occurs exactly once. `<LF>` is a line break. Run `-x`.
"arms" = `tests/test_inc9l.py` unless stated.

| id | claims | file | old -> new (exact) | verdict | first arm to fail |
|---|---|---|---|---|---|
| M1 | the sentence reads as ruled | github | `or a local folder")` -> `or a local dir")` | RED | `t1_the_one_sentence...[a/b/c]` |
| M2 | `RuntimeError` is caught | github | `except (RuntimeError, OSError, ValueError):` -> `except (OSError, ValueError):` | RED | `sec_f1_the_local_path_predicate_never_raises[exc0]` |
| M3 | `OSError` is caught | github | same -> `except (RuntimeError, ValueError):` | RED | `...never_raises[exc1]` |
| M4 | `ValueError` is caught | github | same -> `except (RuntimeError, OSError):` | RED | `...never_raises[exc2]` |
| M5 | the UNC refusal exists | github | `if len(value) >= 2 and value[0] in "\\/" and value[1] in "\\/":` (the file's text) -> `if False:` | RED | `unc_..._is_refused[\\\\host\\share]` |
| M6 | a leading `/` counts | github | `value[0] in "\\/"` -> `value[0] in "\\"` | RED | `unc_..._is_refused[//host/share/repo]` |
| M7 | both leading characters are required | github | `and value[1] in "\\/":` -> `or value[1] in "\\/":` | RED | `unc_a_single_slash_or_drive_text_is_still_probed[o/r]` |
| M8 | `_classify` checks the clone name | github | `    if _is_url(spec):<LF>        _repo_name_from_url(spec)<LF>        return "url"` -> `    if _is_url(spec):<LF>        return "url"` | RED | `cr_f2_...[c00]` |
| M9 | `painted_repo` reads `_classify` | github | `    try:<LF>        _classify(spec)<LF>    except GitHubError:<LF>        return UNRECOGNISED<LF>    return spec` -> `    if _is_url(spec) or _is_owner_name(spec) or _is_local_path(spec):<LF>        return spec<LF>    return UNRECOGNISED` | RED | `cr_f2_...[c00]` |
| M10 | `_classify` refuses a dash first (arms: `test_inc9k` + `test_inc9l`) | github | `    _refuse_unsafe(spec)<LF>    if _is_local_path(spec):<LF>        return "local"` -> `    if _is_local_path(spec):<LF>        return "local"` | RED | `test_inc9k::...dash_and_transport_helper_refusals_stand[-x]` (the consistency table cannot see it: both sides drift together) |
| M11 | `_classify` accepts owner/name (arms: `test_inc9k` + `test_inc9l`) | github | `    if _is_owner_name(spec):<LF>        return "gh"<LF>    raise GitHubError(_UNSUPPORTED)` -> `    raise GitHubError(_UNSUPPORTED)` | RED | `test_inc9k::owner_name_still_goes_through_gh` |
| M12 | a folder needs `.git` | github | `return p.is_dir() and (p / ".git").is_dir()` -> `return p.is_dir()` | RED | `cr_f1_a_plain_directory_without_dot_git_is_not_painted` |
| M13 | a missing path is not a folder (broad) | github | same old -> `return not p.exists() or (p.is_dir() and (p / ".git").is_dir())` | RED | `t1_...[a/b/c]` (a T1 arm fires first; M21-M22 isolate CR-F1) |
| M14 | the rewrite is case-consistent | app | `path = value.split("/", 3)[3]` -> `path = value.split("github.com/", 1)[1]` | RED | `obs1_the_github_rewrite_is_case_consistent[HTTPS://GITHUB.COM/o/n-o/n]` |
| M15 | the rewrite keeps owner/name | app | same old -> `path = value.split("/", 2)[2]` | RED | same |
| M16 | the default branch is encoded | github | `quote(repo_info.get("defaultBranchRef", {}).get("name", "main"), safe="")` -> `repo_info.get("defaultBranchRef", {}).get("name", "main")` | RED | `sec_f2_branch_and_default_branch_names_are_encoded_in_gh_api_paths` |
| M17 | the branch is encoded in `compare` | github | `compare/{default_branch}...{qname}"` -> `compare/{default_branch}...{bname}"` | RED | same |
| M18 | the branch is encoded in `commits` | github | `commits/{qname}",` -> `commits/{bname}",` | RED | same |
| M19 | the sha is encoded | github | `commits/{quote(sha, safe='')}/check-runs"` -> `commits/{sha}/check-runs"` | RED | same |
| M20 | `/` is encoded too (`safe=""`) | github | `qname = quote(bname, safe="")` -> `qname = quote(bname)` | RED | same |
| M21 | CR-F1: a missing ABSOLUTE path is not painted (runs `-k cr_f1_a_missing_absolute`) | github | the M12 old -> `return p.is_absolute() or (p.is_dir() and (p / ".git").is_dir())` | RED | `cr_f1_a_missing_absolute_path_is_not_painted` |
| M22 | CR-F1: a missing RELATIVE path with a credential is not painted (`-k cr_f1`) | github | the M12 old -> `return (not p.is_absolute() and not p.exists()) or (p.is_dir() and (p / ".git").is_dir())` | RED | `cr_f1_a_missing_relative_path_with_a_credential_is_not_painted` |
| M23 | CR-F1: any existing directory is not painted (`-k cr_f1`) | github | the M12 old -> `return p.is_dir()` | RED | `cr_f1_a_plain_directory_without_dot_git_is_not_painted` |

23 runs, 23 RED, 0 SURVIVED. M5-M7 show the file text of the slash set (`"\\/"` is the two characters `\` and `/` in Python source, backslash escaped).
Not mutated: the null-byte pin, the lower-case rewrite pins (M15 touches them), the SEC-F2 plain-name pin, the table-size pin, the test-only edits of
section 2 (the tightened `_is_url` patch has no production mutant: it is a test lift). The `test_inc9l` spy blocks the real call for a double-slash text, so no
real UNC path is ever opened, including under mutant M5.

## 5. The consistency table

`painted_repo(x) != (unrecognised URL)` iff `fetch(x)` reaches a process (`subprocess.run` stub that answers rc 128), 52 inputs, `<T>` is the temp directory
(a folder `work` with `.git`, a folder `plain`, a `-x` with `.git`, and `dashdir/-x` with `.git`; the cwd is the temp directory). Measured on `910cba3` (HEAD) and on
`606a13a` (base): **0 mismatches on HEAD, 7 on the base** (c00-c05 and c46).

| id | input | painted (HEAD) | reaches a process (HEAD) | painted (base) | base |
|---|---|---|---|---|---|
| c00 | `git@h:r` | False | False | True | MISMATCH |
| c01 | `https://h/...` | False | False | True | MISMATCH |
| c02 | `https://h/o/.git` | False | False | True | MISMATCH |
| c03 | `https://h/o/..git` | False | False | True | MISMATCH |
| c04 | `-a/b` | False | False | True | MISMATCH |
| c05 | `-x` | False | False | True | MISMATCH |
| c06 | `https://h/o/r` | True | True | True | ok |
| c07 | `https://h/o/r.git` | True | True | True | ok |
| c08 | `https://h/o/r/` | True | True | True | ok |
| c09 | `https://h:8443/o/r.git` | True | True | True | ok |
| c10 | `https://github.example.invalid/o/r` | True | True | True | ok |
| c11 | `git@h:o/r.git` | True | True | True | ok |
| c12 | `git@h:o/r/` | True | True | True | ok |
| c13 | `https://1.2.3.4/o/r` | True | True | True | ok |
| c14 | `https://h/o/some-name_v2~x.git` | True | True | True | ok |
| c15 | `git@h:o/r` | True | True | True | ok |
| c16 | `https://u:tok@h/o/r` | False | False | False | ok |
| c17 | `http://h/o/r` | False | False | False | ok |
| c18 | `https://h/o/r?x=1` | False | False | False | ok |
| c19 | `https://h/o/r#f` | False | False | False | ok |
| c20 | `HTTPS://h/o/r` | False | False | False | ok |
| c21 | `https://h/o/./r` | False | False | False | ok |
| c22 | `https://h/o/../r` | False | False | False | ok |
| c23 | `https://h//r` | False | False | False | ok |
| c24 | `git@h:/o/r` | False | False | False | ok |
| c25 | `git@h:o/../r` | False | False | False | ok |
| c26 | `https://h/..` | False | False | False | ok |
| c27 | `https://h/o/r` + LF (the text ends in a line feed) | False | False | False | ok |
| c28 | `ssh://git@h/o/r` | False | False | False | ok |
| c29 | `file:///etc/passwd` | False | False | False | ok |
| c30 | `o/r` | True | True | True | ok |
| c31 | `owner/some.name-1` | True | True | True | ok |
| c32 | `a/b/c` | False | False | False | ok |
| c33 | `o/..` | False | False | False | ok |
| c34 | `bad owner/x` | False | False | False | ok |
| c35 | `plainword` | False | False | False | ok |
| c36 | `ext::sh -c x` | False | False | False | ok |
| c37 | `--upload-pack=x` | False | False | False | ok |
| c38 | `<T>/work` | True | True | True | ok |
| c39 | `work` | True | True | True | ok |
| c40 | `<T>/plain` | False | False | False | ok |
| c41 | `<T>/missing` | False | False | False | ok |
| c42 | `missing/dir` | True | True | True | ok |
| c43 | `./user:tok@missing/dir` | False | False | False | ok |
| c44 | `<T>/-x` | True | True | True | ok |
| c45 | `dashdir/-x` | True | True | True | ok |
| c46 | `~nosuchuser:tok@h/o/r` | False | False | CRASH RuntimeError | MISMATCH |
| c47 | `\\host\share` | False | False | False | ok |
| c48 | `//host/share/repo` | False | False | False | ok |
| c49 | `\\?\C:\x` | False | False | False | ok |
| c50 | `` | False | False | False | ok |
| c51 | `   ` | False | False | False | ok |

## 6. Renders (Pilot, real keys, stub that fails on any process; typed `https://user:tok@example.invalid/o/r.git`, then enter)

`RepoScreen`, 118x34 and 87x34 (blank lines condensed; the frames are identical in the lines that matter, and the T1 sentence wraps at the same words at both):

```
 browse maps    connect repo    build map    factory                                                          ◕ mapper
(unrecognised URL)
                               (no hay ramas cargadas)
 (unrecognised URL)

 ▲ failed
 refusing the repository: use
 https://host/path,
 git@host:path, owner/name or
 a local folder
 q back

 j next branch
 k previous branch
 q back
 ? legend

repo j next branch  k previous branch  q back   global ctrl+p palette  ? legend
```

At 87 the header row is shorter (the `◕ mapper` mark moves left); every other line is the same. Not measured: any terminal other than Textual's headless driver; widths other than 118 and 87.

## 7. Test results, risks, carries, next

| check | state |
|---|---|
| `tests/test_inc9l.py` + `test_inc9d/f/g/h/i/j/k`, `test_github`, `test_inc9`, `test_inc9c`, `test_inc9e` | executed: 720 passed, 4 deselected (the `network` arms) on `910cba3` |
| the 4 `network` arms with the tightened patch (`-m network`, local bare repos only, temp HOME, git identity from env) | executed: 4 passed |
| `ruff check . --exclude prototypes --output-format concise`, set difference vs `606a13a` (a detached worktree; line and column stripped) | executed: 28 lines each side, new = none, gone = none |
| Literal Cf/Cc characters in every touched file | executed: none (control and bidi are `\u` escapes) |
| Full default lane, once, uninterrupted, last step | see "Full-lane result" at the end of this record |
| Known flakes (`test_llr_cnv_3_1...`, `test_hlr_n16_4...[size2]`, `test_palette::test_at_n03b...`) | see "Full-lane result" |
| `git stash` | not used |
| Real remote, real `gh`, real cache, network, loopback, a real UNC path | not-run (stubs; HOME and USERPROFILE in `tmp_path`; the spy blocks a double-slash filesystem call) |
| A real `git clone` of an accepted URL form | not-run |


- **Risks.** (1) `%2F` for a branch with a slash in `gh api .../compare/` and `.../commits/` is the ruled encoding; not measured against the live API (stubs only). (2) The UNC rule also
  refuses `/\host` and `\/host` (superset, declared). (3) A leading-whitespace text before two slashes is not specially treated (the screen strips typed text). (4) The refusal
  message now holds one `@` by design (`git@host:path`); two leak lists check for exactly one. (5) `painted_repo` now runs `_refuse_unsafe`, `_is_local_path`, `_is_url`
  and `_repo_name_from_url` on the UI thread: pure string work plus one `is_dir` pair, as `_is_local_path` already did (no network).
- **Not measured.** A real `git clone`; a real UNC path (deliberately never opened: a stub proves no call); the real GitHub API with encoded names; terminals below 87 columns.
- **Carries.** `Inc-EN` (not started; T3 `?` in a text field with B-36 / B-72); `LC_ALL=C` on a localised git; orphaned pre-`A-115` mirrors (`INC9I-CR-F4`); the stale phrase in the `test_inc9j` docstring.
- **Next.** The independent reviews of `Inc-9l`, then `Inc-EN` on the operator's order.

## Commits

`b64026b` arms (strict xfail) · `910cba3` `github.py` + `app.py` + sealed-arm edits + `OPEN_STEPS` emptied · docs commit (this record, `A-120`) · docs commit (the full-lane result).
No push; `state.json` untouched.
