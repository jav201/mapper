# Increment 039 -- Inc-9m: local paths get an allow-list (S1 applied to paths), and the Inc-9l review fixes

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `19b2824`. Authority: the operator's S1 (Round 8) and T1 (Round 9) in
`VERDICT-inc9-2026-09-30.md`, and the coordinator's ruling "local paths get an allow-list, like URLs" (the two-slash deny-check of `A-120` st. 4 was
bypassed by `\??\UNC\host\share`, measured locally by both reviewers). Amendment: `A-121` (appended to `01-requirements.md`, dated 2026-10-01).

## 1. What changed

- `mapper/osopen.py`: new `safe_local_path(text) -> Path | None`, the ONE judge of a typed local path. `open_external` applies it to a `file` target before `resolve()`
  (`INC9L-SEC-F5`; the refusal is the existing `destino inválido`).
- `mapper/github.py` (`INC9L-SEC-F1`, `F3`, `F4`, `CR-F1`, `CR-F2`, `CR-F4`, `CR-F5`):
  - `_is_local_path` reads the helper; `fetch` resolves the local folder through it.
  - `_repo_name_from_url` takes the path of `git@host:path` from the `_SCP_URL` match (`urlparse` read `git@h:r` as a scheme plus an empty path).
  - `_fetch_gh`: a branch name or commit sha equal to `.` or `..` builds no path; a default branch equal to `.` or `..` stops the fetch (`unexpected response from gh repo view`);
    a tag's date is fetched from `repos/{owner}/{name}/commits/{quote(sha, safe='')}` built from `tag["commit"]["sha"]` (the API's `commit.url` is not followed);
    `default_branch` is renamed `qdefault`.
- `mapper/app.py`: import-CSV `on_path` judges the typed path with the helper; `None` gives the toast `archivo no encontrado` (no name). `RepoScreen._source_kind` reads
  `github._classify` (`local` is `local`; a remote is `github`; a refused text is `local`).
- `mapper/screens/factory.py`: import-office `on_path` judges the typed path with the helper; `None` gives the same name-free toast.
- Tests: new `tests/test_inc9m.py` (85 cases); one sealed-arm edit in `tests/test_inc9l.py` (section 2).

Source files: 4 (`osopen.py`, `github.py`, `app.py`, `screens/factory.py`), exactly the ceiling. Tests and docs uncapped.

### The grammar of `safe_local_path`, exactly as implemented

```
safe_local_path(text):
  1. return None if text is not a str, or text == "", or "\x00" in text, or text.startswith("-")
  2. try: expanded = Path(text).expanduser(); parsed = PureWindowsPath(str(expanded))
     except (RuntimeError, OSError, ValueError): return None
  3. if re.fullmatch("[A-Za-z]:", parsed.drive) and parsed.root == "\\":   return expanded   # (a) drive-absolute
     if not parsed.drive and not parsed.root and text[0] not in "\\/":     return expanded   # (b) relative
     return None
```

No filesystem call is made by it (`PureWindowsPath` is pure; `Path.expanduser` reads only the environment). The caller stats the returned path, and only then.
Judged on the EXPANDED text, so `~` that expands to UNC is refused. Verdicts (tests/test_inc9m.py, a spy that fails on any `os.stat`, `os.lstat`, `os.scandir`,
`os.listdir`, `os.path.exists/isdir/isfile/islink/lexists/realpath/getsize/samefile`, `Path.is_dir/exists/is_file/resolve/stat/lstat/samefile/iterdir/glob` and `nt._getfinalpathname`):

| accepted | refused |
|---|---|
| `C:\x`, `C:/x/y`, `z:\`, `o/r`, `work`, `.\x`, `..\x`, `sub dir\f.csv`, `C:\a b\c`, `~/x` with a drive-absolute home | empty, NUL, `-x`, `-a/b`, `\\h\s`, `//h/s`, `\\?\C:\x`, `\\.\pipe\x`, `\??\UNC\h\s`, `/??/UNC/h/s`, `\??\GLOBALROOT\Device\Mup\h\s`, `\??\C:\Windows`, `\single`, `/single`, `/tmp/x`, `C:x`, `C:`, `1:\x`, `\/h/s`, `/\h/s`, `~/x` when the home is `\\h\s\me`, an `expanduser` that raises |

Two guards of branch (b) are redundant with each other (a text that starts with a separator has a root): see N9, N11 in section 4.

## 2. Decisions and declared sealed-arm changes

- **Not-found toast for a refused text has no name.** The brief says "their existing not-found message (in its current language)"; its existing form names the file
  (`archivo no encontrado: <name>`), and the arm requires that `secret-token` never reaches the frame. So a text the helper refuses gets `archivo no encontrado` alone; a path it
  accepts keeps the name. Inc-EN translates later. This is a decision, not a ruling: flag it if the coordinator wanted the name kept.
- **`_source_kind` for a refused text.** Today's fall-through was `github` for any text holding `://` and `local` otherwise (so a refused `https://u:tok@h/o/r` showed `github`). The brief maps
  only `local`, `gh`, `url`. A refused text is now `local` (the old catch-all, and it does not claim a remote the connector will refuse). Decision, declared.
- **Default branch `.`/`..` raises** `GitHubError("unexpected response from gh repo view")` rather than being "skipped" (the brief's wording covers names and shas; a default branch is
  the base of every `compare/` path, so there is nothing to continue with). Decision, declared.
- **A `-`-leading `file` attachment target** is refused by `open_external` (the same rule). Decision, declared.
- **`INC9L-CR-F4` accepted** (record, no code): the broad `OSError` catch of `_is_local_path` stays because the ruling wants a total predicate; a local folder that cannot be read may fall through
  to the `owner/name` path.
- **`INC9L-UX-F1` coordinator decision** (record, no code): the specific refusal reasons (`last segment is not a usable name`, `may not start with '-'`, `transport helpers are not accepted`)
  stay alongside the T1 sentence.
- **Architecture.** `docs/ARCHITECTURE.md` section 3 bans `screens -> osopen` and gives `github` the one dependency `model`; the ruling puts the helper in `osopen` and has all three import it.
  Not edited here (docs outside the brief); carried. No test enforces it (`test_osopen_imports_nothing_from_mapper` still holds: `osopen` imports only the stdlib).

Sealed-arm changes (what, why; no leak assertion is weakened):

| arm | change | justification |
|---|---|---|
| `test_inc9l::test_inc9l_unc_a_single_slash_or_drive_text_is_still_probed`, parameter `/tmp/x` | the parameter is deleted (3 left: `relative/dir`, `o/r`, `C:\work\repo`) | `/tmp/x` is root-relative (`\x`): the allow-list refuses it before any probe, by the ruling. The arm kept its purpose: an accepted ordinary path is still probed |
| consistency table row `c00` (`git@h:r`) of `increment-038` section 5 and `CONSISTENCY[0]` of `test_inc9l` | was "refused (False/False)"; now accepted (True/True) | `INC9L-CR-F2`. The `test_inc9l` arm asserts only `painted iff fetch reaches a process`, so it is green unchanged; only the table's expected column in the record changes |
| `tests/test_inc9m.py` itself, between the RED commit `5b1d61d` and `594cc9e` | three `REFUSED` entries removed (`CC:\x`, `~\\h`, `~nosuchuser`) | my arm was wrong, not the code: `CC:\x` is a relative name for `PureWindowsPath` (branch (b), declared in `A-121`); `~\\h` and `~nosuchuser` expand with the REAL home of the machine that runs the test (they are covered by the tmp-HOME arms instead). The RED run in the base worktree was repeated with the final file (section 3) |

## 3. Arm table (RED/GREEN)

Arms committed as strict xfail in `5b1d61d` (88 cases; no sources touched), copied into a detached `git worktree` of `19b2824` in `%TEMP%` (no stash), `--runxfail`:
**71 failed, 17 passed**. After the three-entry trim above, the final file on the same base worktree: **68 failed, 17 passed (85 cases)**. The 17 passes are pins. GREEN: **85 passed** on
`c740ef8`, `OPEN_STEPS` empty. (`71 -> 68` is exactly the three removed entries, all three were RED.)

| arm family (`test_inc9m`) | cases | RED on `19b2824` | on HEAD |
|---|---|---|---|
| S1: an accepted text returns a `Path` equal to the pure parse | 9 | RED x9 | green |
| S1: every other text is refused with a spy that fails on any filesystem call | 21 | RED x21 | green |
| S1: `~` expanding to UNC refused, `~/x` with a drive-absolute home accepted, `expanduser` failing (3 exceptions) | 5 | RED x5 | green |
| S1: one helper imported by the three callers, no `expanduser` call outside `osopen` (AST) | 1 | RED | green |
| SEC-F1: a hostile local text touches no filesystem and is refused (`painted_repo`, `fetch`) | 10 | RED x6 (the six that slipped past the two-slash rule), pin x4 | green |
| SEC-F1: `~` expanding to UNC touches no filesystem | 1 | RED | green |
| SEC-F1: drive-absolute, relative and `~/x` git folders still probed | 3 | pin x3 | green |
| SEC-F2: Pilot, real keys, `~nosuchuser/secret-token.csv` (118, 87): app alive, frame and toasts never hold it | 2 | RED x2 | green |
| SEC-F2: the same for import-office | 2 | RED x2 | green |
| SEC-F2: a typed UNC path causes no filesystem call (csv, office) | 2 | RED x2 | green |
| SEC-F2: a missing drive-absolute csv still names its file | 1 | pin | green |
| SEC-F5: a UNC / `//` / `\??\UNC` file target is refused before `resolve` | 3 | RED x3 | green |
| SEC-F5: a relative file opens; an outside drive-absolute file is still outside | 2 | pin x2 | green |
| SEC-F3: `..`/`.` branch or sha builds no path; a dot default branch is refused | 4 | RED x4 | green |
| SEC-F3: ordinary names still build their paths | 1 | pin | green |
| SEC-F4: the tag `commit.url` (`https://evil.example/x`, `-XDELETE`) is never in an argv; the sha is one encoded segment | 2 | RED x2 | green |
| CR-F5: `qdefault` (AST) | 1 | RED | green |
| CR-F2: `git@h:r`, `git@h:project.git`, `git@myserver:project.git` reach `git clone --mirror` | 3 | RED x3 | green |
| CR-F2: a bad SCP last segment is still refused | 1 | pin | green |
| CR-F3: the badge of `git@h:o/r/x`, `git@h:grp/sub/r.git`, `git@h:r` matches `_classify` (3 RED), of `https://h:8443/a/b/c`, `https://h/o/r`, `o/r` (3 pins) | 6 | RED x3, pin x3 | green |
| CR-F3: painted `RepoScreen` badge for `git@h:grp/sub/r.git` (118, 87) | 2 | RED x2 | green |
| CR-F3: a local git directory is `local`; a refused text is `local` (`plainword` pin, `https://u:tok@h/o/r` RED) | 3 | RED x1, pin x2 | green |

## 4. Mutant table

Harness `mutate9m.py` in the session scratchpad, outside the repo; run on a detached `git worktree` of `c740ef8` in `%TEMP%`; sha256 pinned before (`osopen.py` `2e77052cae3d976d...`,
`github.py` `850efdc5e39b7f9e...`, `app.py` `c772231c09035712...`, `factory.py` `4d39ee61eff5173d...`), byte-level I/O in each file's own line ending, `old` must occur exactly once, the verdict
printed before the file is restored, the pin re-checked after: **pin OK**. `<LF>` is a line break. Run `-x`; arms = `tests/test_inc9m.py` unless stated. In the texts below `\\` is the two characters
backslash backslash, as in the file.

| id | claims | file | old -> new (exact) | verdict | first arm to fail |
|---|---|---|---|---|---|
| N1 | a NUL is refused | osopen | `or not text or "\x00" in text or text.startswith("-")` -> `or not text or text.startswith("-")` | RED | `s1_every_other_text...[a\x00b]` |
| N2 | an empty text is refused | osopen | `not isinstance(text, str) or not text or "\x00"` -> `not isinstance(text, str) or "\x00"` | RED | `...[]` |
| N3 | a leading dash is refused | osopen | ` or text.startswith("-"):<LF>        return None` -> `:<LF>        return None` | RED | `...[-x]` |
| N4 | `RuntimeError` of `expanduser` is caught | osopen | `except (RuntimeError, OSError, ValueError):<LF>        return None<LF>    if _DRIVE` -> `except (OSError, ValueError):<LF>        return None<LF>    if _DRIVE` | RED | `s1_expanduser_failing...[exc0]` |
| N5 | `OSError` is caught | osopen | same -> `except (RuntimeError, ValueError):...` | RED | `...[exc1]` |
| N6 | `ValueError` is caught | osopen | same -> `except (RuntimeError, OSError):...` | RED | `...[exc2]` |
| N7 | the drive must be one letter | osopen | `if _DRIVE.fullmatch(parsed.drive) and` -> `if parsed.drive and` | RED | `...[\\h\s]` (UNC accepted) |
| N8 | an absolute path needs a root (no `C:x`) | osopen | ` and parsed.root == "\\":<LF>        return expanded` -> `:<LF>        return expanded` | RED | `...[C:x]` |
| N9 | a relative path has no root | osopen | `if not parsed.drive and not parsed.root and text[0]` -> `if not parsed.drive and text[0]` | **SURVIVED (equivalent)** | none: `text[0] not in "\\/"` refuses every root-relative text the root test would |
| N9b | both redundant guards of (b) removed | osopen | `if not parsed.drive and not parsed.root and text[0] not in "\\/":` -> `if not parsed.drive:` | RED | `...[\??\UNC\h\s]` |
| N10 | a relative path has no drive | osopen | `if not parsed.drive and not parsed.root and text[0]` -> `if not parsed.root and text[0]` | RED | `...[C:x]` |
| N11 | the typed text has no leading separator | osopen | ` and text[0] not in "\\/":` -> `:` | **SURVIVED (equivalent)** | none: a text that starts with a separator has a root, which the root test refuses |
| N12 | `~` is expanded | osopen | `expanded = Path(text).expanduser()` -> `expanded = Path(text)` | RED | `s1_a_tilde_that_expands_to_unc...` |
| N13 | `open_external` checks a file target before `resolve` | osopen | `if kind == "file" and safe_local_path(target) is None:` -> `if False:` | RED | `sec_f5...[\\h\s\x.pdf]` |
| N14 | the F5 refusal is `destino inválido` | osopen | `safe_local_path(target) is None:<LF>        return REFUSED_TYPE` -> `...return REFUSED_OUTSIDE` | RED | `sec_f5...[\\h\s\x.pdf]` |
| G1 | `_is_local_path` reads the helper | github | `    path = safe_local_path(value)<LF>    if path is None:<LF>        return False<LF>` -> `    path = Path(value).expanduser()<LF>` | RED | `s1_one_helper...` (AST arm first); G1b with that arm deselected: RED `sec_f1_a_hostile...[\\h\s]` |
| G2 | a one-segment SCP url is named from its match | github | `path = scp.group("path") if scp else urlparse(url).path` -> `path = urlparse(url).path` | RED | `cr_f2...[git@h:r-r]` |
| G3 | `fetch` resolves a local folder through the helper | github | `cwd = safe_local_path(self.repo).resolve()` -> `cwd = Path(self.repo).expanduser().resolve()` | RED | `s1_one_helper...` only: **G3b (arm deselected) SURVIVED**, behaviourally equivalent (`_classify` already vetted the text); the AST arm is its only killer |
| G4 | a dot default branch is refused | github | `if default in (".", ".."):` -> `if False:` | RED | `sec_f3...default_branch...[.]` |
| G5 | a dot branch builds no path | github | `if bname in (".", ".."):` -> `if False:` | RED | `sec_f3_a_dot_or_dotdot_branch_or_sha...` |
| G6 | a dot sha builds no check-runs path | github | `if sha and sha not in (".", ".."):<LF>                    checks` -> `if sha:<LF>                    checks` | RED | same |
| G7 | a dot tag sha builds no path | github | `if sha and sha not in (".", ".."):<LF>                try:` -> `if sha:<LF>                try:` | RED | `sec_f4_the_tag_sha_is_one_encoded_segment` |
| G8 | the tag `commit.url` is not followed | github | `["api", f"repos/{owner}/{name}/commits/{quote(sha, safe='')}"])` -> `["api", tag.get("commit", {}).get("url", "")])` | RED | `sec_f4_the_tag_commit_url_is_never_followed` |
| G9 | the tag sha is encoded | github | `commits/{quote(sha, safe='')}"])` -> `commits/{sha}"])` | RED | `sec_f4_the_tag_sha_is_one_encoded_segment` |
| G10 | the default branch is encoded (arms 9m + 9l) | github | `qdefault = quote(default, safe="")` -> `qdefault = default` | RED | `test_inc9l::sec_f2_branch_and_default_branch_names_are_encoded...` |
| G11 | the encoded default is named `qdefault` | github | `qdefault = quote(` -> `default_branch = quote(` AND `compare/{qdefault}...` -> `compare/{default_branch}...` | RED | `cr_f5_the_encoded_default_branch_is_named_qdefault` |
| A1 | import-CSV judges the typed path with the helper | app | `path = safe_local_path(path_str)<LF>            if path is None:` -> `path = Path(path_str).expanduser()<LF>            if False:` | RED | `s1_one_helper...` first; A1b (arm deselected): RED `sec_f2_import_csv_survives...[size0]` |
| A2 | import-CSV never names a refused text | app | `self.notify("archivo no encontrado", severity="error", markup=False)` -> `self.notify(f"archivo no encontrado: {Path(path_str).name}", severity="error", markup=False)` | RED | `sec_f2_import_csv_survives...[size0]` |
| A3 | the badge of a remote is `github` | app | `== "local" else "github"` -> `== "local" else "local"` | RED | `cr_f3_the_badge_of_an_accepted_remote...[git@h:o/r/x]` |
| A4 | the badge of a local folder is `local` | app | `return "local" if github._classify(self.repo) == "local" else "github"` -> `return "github"` | RED | `cr_f3_pin_a_local_git_directory_is_local` |
| A5 | a refused text is badged `local` | app | `except GitHubError:<LF>            return "local"` -> `except GitHubError:<LF>            return "github"` | RED | `cr_f3_a_refused_text_is_badged_local...[https://u:tok@h/o/r]` |
| A6 | the badge reads `_classify` | app | the A4 old -> `return "github" if "://" in self.repo or self.repo.count("/") == 1 else "local"` (the pre-9m rule) | RED | `cr_f3_the_badge_of_an_accepted_remote...[git@h:o/r/x]` |
| F1 | import-office judges the typed path with the helper | factory | `source = safe_local_path(path_str)<LF>            if source is None:` -> `source = Path(path_str).expanduser()<LF>            if False:` | RED | `s1_one_helper...` first; F1b (arm deselected): RED `sec_f2_import_office_survives...[size0]` |
| F2 | import-office never names a refused text | factory | `self.notify("archivo no encontrado", severity="error", markup=False)<LF>                return<LF>            # \`INC9BC-SEC-F1\`` -> the same with `f"archivo no encontrado: {Path(path_str).name}"` | RED | `sec_f2_import_office_survives...[size0]` |

Runs: 34 mutant ids (N1-N14 with N9b, G1-G11, A1-A6, F1-F2) + 4 deselected variants (G1b, G3b, A1b, F1b) = 38 runs; **35 RED, 3 SURVIVED**: N9 and N11 are each equivalent (the two guards cover each other; N9b removes both and is RED), and G3b is
behaviourally equivalent (killed only by the AST "one helper" arm, which is its purpose). The first harness run was on `594cc9e`, whose `osopen.py` had a one-backslash escape (`"\/"`, the same runtime value, a
`SyntaxWarning`); the fix `c740ef8` spells `"\\/"` and the whole harness was run again on it (the table above is that run). Not mutated: the spy helpers themselves; the pins' counterparts N9/N11 above.

## 5. Renders (Pilot, real keys, HOME and USERPROFILE in a temp dir; `i` on Home, typed `~nosuchuser/secret-token.csv`), 118x34

Blank lines condensed. The toast is not part of the compositor frame the helper reads, so the toast text is captured by wrapping `app.notify`.

```
 c browse maps    p connect repo    n build map    f factory                                                  ◕ mapper
                                                   ◕ mapper   home
c browse maps   abre un mapa reciente
p connect repo  conecta un repositorio
n build map     crea un nuevo mapa
t from template mapa desde plantilla
i import csv    CSV / TSV de nodos
f factory       documentos de proceso
                                                  ruta del CSV / TSV
                                     ~nosuchuser/secret-token.csv
                                                ↵ confirm   esc cancel
next ▸ choose a door
open c browse maps  p connect repo  n build map  t from template  i import csv  f factory … +8  ? all keys
```

after `enter` (app running = True; toasts = `['archivo no encontrado']`; "frame contains secret-token: False"):

```
 c browse maps    p connect repo    n build map    f factory                                                  ◕ mapper
                                                   ◕ mapper   home
c browse maps   abre un mapa reciente
p connect repo  conecta un repositorio
n build map     crea un nuevo mapa
t from template mapa desde plantilla
i import csv    CSV / TSV de nodos
f factory       documentos de proceso
next ▸ choose a door
open c browse maps  p connect repo  n build map  t from template  i import csv  f factory … +8  ? all keys
```

On the base, the same keys crash the app (`RuntimeError: Could not determine home directory.`, the arms are RED). Not measured: terminals other than Textual's headless driver; widths other than 118 and 87 (the arms run both);
the toast as a painted widget.

## 6. Test results, risks, carries, next

| check | state |
|---|---|
| `tests/test_inc9m.py` | executed: 85 passed on `c740ef8`; RED run on `19b2824` in a worktree: 68 failed, 17 passed |
| `test_inc9d/g/h/i/j/k/l`, `test_inc9`, `test_inc9c`, `test_inc9e`, `test_inc9f`, `test_github`, `test_attachments`, `test_g6_store_surrogates` with `test_inc9m` | executed: 874 passed, 4 deselected (`network`) on `594cc9e` (before the one-character escape fix); `test_inc9m` + `test_attachments` re-run on `c740ef8`: 114 passed with `-W error::SyntaxWarning`; the whole lane covers the rest |
| `ruff check . --exclude prototypes --output-format concise`, set difference vs `19b2824` (a detached worktree; line and column stripped) | executed: 30 lines each side, new = none, gone = none |
| Literal Cf characters in every touched file (Python scan by Unicode category) | executed: none |
| Full default lane, once, uninterrupted, last step | see "Full-lane result" at the end of this record |
| Known flakes (`test_llr_cnv_3_1...`, `test_hlr_n16_4...[size2]`, `test_palette::test_at_n03b...`) | see "Full-lane result" |
| `git stash` | not used |
| Real remote, real `gh`, real cache, network, loopback, a real UNC or `\??\UNC` path | not-run (stubs; HOME and USERPROFILE in `tmp_path`; the spies refuse and record any filesystem call for the hostile text) |
| A real `git clone` of `git@h:r` | not-run (stub; the argv `git clone --mirror -- git@h:r <cache dir>` is asserted) |

- **Risks.** (1) The allow-list refuses a root-relative typed path (`/ruta/a/nodos.csv`, the CSV prompt's own placeholder, and `/tmp/x`): by the ruling, but the placeholder text now suggests a form the prompt refuses
  (Inc-EN or a later copy fix). (2) `CC:\x` passes as a relative name (branch (b), `A-121` "not claimed"). (3) A `file` attachment target starting with `-` is refused. (4) A refused `RepoScreen` source badge is `local`.
  (5) `github` and `screens/factory` now import `osopen`, against `docs/ARCHITECTURE.md` section 3 (carried). (6) The ban spies patch `os.stat` and `Path` methods process-wide inside a `with`; they restore on exit.
- **Found, not fixed (outside the brief).** In `_fetch_gh`, `commit` is read after the `try` that assigns it: if the first `gh api .../commits/{branch}` raises `GitHubError`, `commit` is unbound
  (a `NameError`, or the previous branch's value on a later iteration). Pre-existing.
- **Not measured.** A real SMB share, a real `gh`, a real clone; `%2F` against the live API (carried from 038); terminals below 87 columns.
- **Carries.** `Inc-EN` (T3 `?` in text fields, copy, the CSV prompt's placeholder); the `ARCHITECTURE.md` section 3 update; orphaned pre-`A-115` mirrors; the stale `test_inc9j` docstring phrase.
- **Next.** The independent reviews of `Inc-9m`, then `Inc-EN` on the operator's order.

## Commits

`5b1d61d` arms (strict xfail) · `594cc9e` four sources + the sealed-arm edit + `OPEN_STEPS` emptied · `c740ef8` the escape fix in `osopen.py` · docs commit (this record, `A-121`) · docs commit (the full-lane result).
No push; `state.json` untouched.
