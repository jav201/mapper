# Increment 040 -- Inc-9n: the Inc-9m review fixes (sidecar paths, DOS devices, U1, U2, `_fetch_gh`, architecture)

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `73c2670`. Authority: `VERDICT-inc9-2026-09-30.md` Round 10 (U1, U2, S1, T1) and the coordinator's rulings
for the Inc-9m reviews (`INC9M-SEC-F1`..`F4`, `INC9M-CR-F1`..`F8`). Amendment: `A-122` (appended to `01-requirements.md`, dated 2026-10-01).

## 1. What changed

- `mapper/osopen.py`: `safe_local_path` refuses a DOS device name in any component (`PureWindowsPath(part).is_reserved()` per part; 3.13 spelling noted in a comment); the redundant
  `text[0] not in "\\/"` guard is gone (`CR-F8`); `open_external(kind="file")` requires `is_file()`.
- `mapper/github.py`: `commit: dict = {}` per branch iteration (`SEC-F3`); `progress` is called before the `.`/`..` `continue` (`CR-F5`); public `source_kind(spec)` (`CR-F8`);
  `fetch` no longer calls `.resolve()` on the Optional.
- `mapper/app.py`: `PATH_NOT_SUPPORTED` (the U1 sentence, real ellipsis); the CSV prompt toasts it for a refused text, requires `is_file()`, and its placeholder is `C:\path\to\nodes.csv`;
  opening a `file` attachment whose text the helper refuses toasts it (nothing named); adding a `file` attachment is validated by `_is_workspace_file_target` (helper + workspace
  containment) BEFORE the undo snapshot, nothing stored on refusal (U2); the badge reads `github.source_kind`.
- `mapper/screens/factory.py`: `_office_path` returns `None` unless `safe_local_path` accepts the sidecar text, then lexical containment (`os.path.normpath`, no filesystem), then
  `resolve()` + `is_relative_to(workspace)` (`SEC-F1`); the office prompt toasts the U1 sentence (imported lazily from `app` beside `_PromptScreen`, because `screens` may import only
  `osopen.safe_local_path` from `osopen`), requires `is_file()`, placeholder `C:\path\to\template.docx`.
- `docs/ARCHITECTURE.md` section 3 (`SEC-F4`, `CR` section 1): `screens` and `github` may import `osopen.safe_local_path` only; the inbound ban reads "`open_external` is referenced only from
  `app`"; the `github` row lists `design` (pre-existing drift) and `osopen.safe_local_path`.
- Tests: new `tests/test_inc9n.py` (117 cases), new `tests/test_arch_osopen_callers.py` (3), `test_inc9m` edited, `test_inc9l` one label (section 2).

Source files: 4 (`osopen.py`, `github.py`, `app.py`, `screens/factory.py`), exactly the ceiling. Tests and docs uncapped. `INC9M-CR-F4` (POSIX): `A-122` "not claimed", no code.
`test_osopen_imports_nothing_from_mapper` is UNCHANGED (osopen still imports only the stdlib).

Decisions (declared):
- The lexical containment test in `_office_path` runs before `resolve()`: the brief's arm demands zero stats of `C:\outside\a.docx`, and `resolve()` stats. `resolve()` still runs for what is lexically
  inside (a junction can lead out; an arm with a real directory junction in `tmp_path` pins it).
- `_office_path` now returns the RESOLVED path (what is judged is what is read); the preview line shows it.
- Attachment OPEN for a refused text toasts U1 from `app` (before `open_external`), because `open_external` returns the same `destino inválido` word for a non-string and for a refused text.
  A `file` attachment that the helper accepts but that is outside the workspace keeps `fuera del espacio de trabajo: <text>`; a missing one keeps `no se pudo abrir: <text>` (unchanged).
- The U1 sentence is passed as `darkside.plain(PATH_NOT_SUPPORTED)` at its four notify sites: the first full lane failed `test_inc9::test_llr_n06_2_5_notify_sites_are_coerced` (a dynamic notify message must go through `plain()`), fixed in `3117b0c`; `plain` leaves the sentence unchanged (the U1 arms compare it byte for byte).
- The unreachable `if local is None: raise GitHubError(_UNSUPPORTED)` in `fetch` exists only to drop the Optional `.resolve()` (`CR-F8`); an AST arm pins that the chained form is gone.

## 2. Sealed-arm changes

| arm | change | justification |
|---|---|---|
| `test_inc9m::test_inc9m_sec_f2_import_csv_survives...`, `..._import_office_survives...`, `..._a_typed_unc_path_causes_no_filesystem_call` | the toast assertion `"archivo no encontrado" in toasts` is now `U1 in toasts and "archivo no encontrado" not in toasts`; committed RED first (step `u1`) | U1 (Round 10) replaces the not-found toast for a REFUSED text; no leak assertion is weakened (the frame and toasts still never hold the typed text) |
| `test_inc9m::test_inc9m_cr_f3_the_badge_is_painted_from_classify` | rewritten: a stubbed `fetch` returns a one-branch `Graph`, the badge text is asserted in the painted frame (3 repos x 2 widths), the method-level check kept | `INC9M-CR-F3`; it is green on the base (a strengthened pin), killed by A8/A10 below |
| `tests/test_inc9m.py` | the unused `subprocess` and `textual.widgets.Static` imports removed | `INC9M-CR-F6` (ruff F401 x2, measured on the clean base) |
| `test_inc9l::test_inc9l_unc_a_single_slash_or_drive_text_is_still_probed` | renamed `..._unc_an_accepted_ordinary_path_is_still_probed`, docstring updated; body and parameters unchanged | `INC9M-CR-F7`, a LABEL change only |
| record `increment-039` | correction note appended (section 7) | `INC9M-CR-F6` |

## 3. Arm table (RED/GREEN)

Arms committed as strict xfail in `0faec7f` (no sources touched), then the RED run: the final test files copied into a detached `git worktree` of `73c2670` in `%TEMP%` (no stash), plain run
(the `OPEN_STEPS` sets are empty by then). **103 failed, 206 passed** across `test_inc9n`, `test_inc9m`, `test_inc9l`, `test_arch_osopen_callers` (the 206 passes are pins and the untouched 9m/9l arms).
GREEN on the fix commits: all of them pass. The first RED run (before the junction arm and the ellipsis step key) was 102 failed.

| arm family | cases | RED on `73c2670` | on HEAD |
|---|---|---|---|
| SEC-F1: hostile sidecar docs (`\\h\s\a.docx`, `//h/s/a.docx`, `\??\UNC\h\s\a.docx`, `C:\outside\a.docx`, `con`) mount `FactoryScreen` at 118 and 87 under a spy that refuses and records; app alive, existing missing-document text, zero hits | 10 | RED x10 | green |
| SEC-F1: `_office_path` is `None` with no filesystem call (all five) | 5 | RED x5 | green |
| SEC-F1: `..\secret.docx` and a directory junction that leaves the workspace | 2 | RED x2 | green |
| SEC-F1 pins: workspace-relative `docs/a.docx` and a drive-absolute doc inside the workspace still preview | 2 | pin x2 | green |
| F2/CR-F1: 20 device names refused by the helper under `_no_fs` (`con`, `nul`, `conin$`, `conout$`, `com1`, `aux`, `lpt1`, `prn`, `COM` + superscript 1, `sub\con`, `con.csv`, `CON.`, `Com1 `, `con\x`, `C:\con`, ...) | 20 | RED x20 | green |
| F2 pins: 8 look-alikes accepted (`console.csv`, `icon\x`, `com0`, `nulls`...) | 8 | pin x8 | green |
| F2: CSV prompt with `CON`, `conin$`, `COM1`, `sub\con.csv` returns at once with the U1 toast; `preview_csv` stubbed to fail, spy on `open`/`read_text`/stat | 8 | RED x8 | green |
| F2: office prompt with `CON`, `nul`, `sub\COM1.docx` touches nothing | 3 | RED x3 | green |
| F2: CSV and office prompts require `is_file()` (a directory named `d.csv` / `t.docx`) | 2 | RED x2 | green |
| F2: `open_external` refuses device names and requires `is_file()`; pin: a regular file still opens | 4 + 1 | RED x4, pin | green |
| U1: refused text toasts exactly the sentence and names nothing (csv and office; UNC, `/x`, `~nosuchuser`; 118 and 87) | 12 | RED x12 | green |
| U1: a missing accepted path keeps `archivo no encontrado: <name>` (118, 87; csv and office) | 4 | pin x4 | green |
| U1: placeholders `C:\path\to\nodes.csv`, `C:\path\to\template.docx` accepted by the grammar; the attachment placeholder too | 2 + 1 | RED x2, pin | green |
| U1: the constant is written with a real ellipsis | 1 | RED | green |
| U1: opening a refused `file` attachment (`\\h\s\x.pdf`, `/x.pdf`, `con`, `docs\NUL.pdf`; 118, 87) toasts the sentence, launcher and spy untouched; an outside path keeps `fuera del espacio` | 8 + 1 | RED x8, pin | green |
| U2 (real key `A`): `\\h\s\x.pdf`, `/x.pdf`, `C:\outside-ws\x.pdf`, `..\x.pdf`, `con` store nothing (graph and a fresh `MapStore`), toast the sentence (118, 87) | 10 | RED x10 | green |
| U2 pins: `docs/x.pdf`, a URL, a drive-absolute file inside the workspace are stored | 3 | pin x3 | green |
| SEC-F3: first, later, both `commits/{branch}` lookups failing (no `UnboundLocalError`, dates `''`, no carry-over) | 3 | RED x3 | green |
| CR-F5: progress reaches the total with skipped branches (3 orderings) | 3 | RED x3 | green |
| CR-F8: `github.source_kind` public and the badge reads it; the guard is gone (AST) and the grammar is unchanged; no `safe_local_path(...).resolve()` in `fetch`; a local folder still fetches | 3 + 1 | RED x3, pin | green |
| SEC-F4 (arch): the launcher names appear only in `app.py` and `osopen.py`; outside `app` only `safe_local_path` is imported from `osopen` (by `github.py`, `screens/factory.py`) | 2 | pin x2 | green |
| SEC-F4 (arch): `ARCHITECTURE.md` section 3 rows say what the code imports | 1 | RED | green |
| `test_inc9m` U1 assertion changes (section 2) | 6 | RED x6 | green |

## 4. Mutant table

Harness `mutate9n.py` in the session scratchpad, outside the repo, on a detached `git worktree` of `3117b0c` in `%TEMP%`; sha256 pinned before (`osopen.py` `c72ace66920d45cd...`, `github.py` `faa6c3116fd4c838...`,
`app.py` `9d0bf8a457df3f58...`, `factory.py` `2ad2818fa53f048a...`, `ARCHITECTURE.md` `ea6696fb8e6cdf97...`), byte-level I/O in each file's own line ending (`github.py` LF in the checkout is handled by detection),
`old` must occur exactly once, the verdict printed before the file is restored, the pin re-checked after: **pins re-checked: OK**. `<LF>` is a line break. Run `-x`, `-k` as in the harness; arms = `test_inc9n`,
`test_inc9m`, `test_arch_osopen_callers`. Backslashes are as in the file. No mutant was run with an arm that could reach a real `resolve()` of a UNC or device path (the `A7`-style "drop the helper from the add
check" mutant was NOT run for that reason, see "Not measured").

| id | claims | file | old -> new (exact) | verdict | first arm to fail |
|---|---|---|---|---|---|
| D1 | device names are refused | osopen | `    if any(PureWindowsPath(part).is_reserved() for part in parsed.parts):` -> `    if False:` | RED | `f2_a_dos_device_name...[con]` |
| D2 | every component is asked | osopen | `for part in parsed.parts):` -> `for part in parsed.parts[-1:]):` | RED | `...[con\x]` |
| D3 | open_external needs a regular file | osopen | `    if not resolved.is_file():` -> `    if not resolved.exists() or resolved.is_dir():` | RED | `f2_open_external_launches_a_regular_file_only` |
| D4 | the redundant guard stays gone | osopen | `    if not parsed.drive and not parsed.root:<LF>        return expanded` -> `    if not parsed.drive and not parsed.root and text[0] not in "\\/":<LF>        return expanded` | RED (AST arm only: behaviourally equivalent, as N9/N11) | `cr_f8_the_redundant_first_character_guard...` |
| D5 | a root-relative path is refused | osopen | `    if not parsed.drive and not parsed.root:` -> `    if not parsed.drive:` | RED | `s1_every_other_text...[\??\UNC\h\s]` |
| G1 | `commit` bound per iteration (first lookup raising) | github | `            commit: dict = {}<LF>` -> (removed) | RED | `f3_a_failing_first_commit_lookup...` |
| G1b | no carry-over | github | `            commit: dict = {}<LF>` -> `            pass<LF>` AND `        for idx, branch in enumerate(branches, 1):<LF>            bname = branch["name"]` -> `        commit: dict = {}<LF>        for idx, ...` | RED | `f3_a_failing_later_commit_lookup...` |
| G2 | progress reaches total | github | `                if progress:<LF>                    progress(idx, total, "calculando métricas")<LF>                continue` -> `                continue` | RED | `cr_f5...[branches0]` |
| G3 | `source_kind` is the decision | github | `    return _classify(spec)<LF><LF><LF>def painted_repo` -> `    return "gh"<LF><LF><LF>def painted_repo` | RED | `cr_f8_source_kind...` |
| G4 | no `.resolve()` on an Optional | github | the four-line `local = ...; if local is None: raise ...; cwd = local.resolve()` -> `            cwd = safe_local_path(self.repo).resolve()` | RED (AST arm only: behaviourally equivalent) | `cr_f8_fetch_does_not_call_resolve_on_an_optional` |
| A1 | CSV refusal is the U1 sentence | app | `self.notify(darkside.plain(PATH_NOT_SUPPORTED), severity="error", markup=False)` -> `self.notify("archivo no encontrado", severity="error", markup=False)` | RED | `u1_a_refused_text...[csv-\\h\s\x.csv-size0]` |
| A2 | CSV prompt needs a file | app | `            if not path.is_file():` -> `            if not path.exists():` | RED | `f2_the_csv_prompt_requires_a_file_not_a_directory` |
| A3 | CSV placeholder accepted by the grammar | app | `"C:\\path\\to\\nodes.csv"` -> `"/ruta/a/nodos.csv"` | RED | `u1_the_prompt_placeholder...[csv]` |
| A4 | open: a refused text gets U1 | app | `        if att.kind == "file" and safe_local_path(att.path) is None:` -> `        if False:` | RED | `u1_opening_a_refused_file_attachment...` |
| A5 | add validates | app | `            if kind == "file" and not _is_workspace_file_target(target, self.store.workspace):` -> `            if False:` | RED | `u2_adding...[\\h\s\x.pdf-size0]` |
| A6 | add confines to the workspace | app | `        return (workspace / local).resolve().is_relative_to(Path(workspace).resolve())` -> `        return True` | RED | `u2_adding...[C:\outside-ws\x.pdf-size0]` |
| A7 | add toasts the U1 sentence | app | the add refusal `self.notify(darkside.plain(PATH_NOT_SUPPORTED), severity="warning", markup=False)<LF>                return<LF>            self._push_snapshot()` -> the same with `"archivo no encontrado"` | RED | `u2_adding...[\\h\s\x.pdf-size0]` |
| A8 | the badge of a local folder is `local` | app | `            return "local" if github.source_kind(self.repo) == "local" else "github"` -> `            return "github"` | RED | `test_inc9m::cr_f3_pin_a_local_git_directory_is_local` (the pins first; the painted arm was not reached with `-x`) |
| A9 | a real ellipsis | app | `"path not supported: use C:\\… or a relative path"` -> `"path not supported: use C:\\... or a relative path"` | RED | `u1_a_refused_text...[csv-...]` |
| A10 | the badge does not read `_classify` | app | `github.source_kind(self.repo)` -> `github._classify(self.repo)` | RED | `cr_f8_source_kind...` |
| F1 | office path judged by the helper | factory | `        local = safe_local_path(doc.path)<LF>        if local is None:<LF>            return None<LF>` -> `        local = Path(doc.path)<LF>` | RED | `f1_a_hostile_sidecar...[con-size0]` |
| F2 | lexical containment before `resolve` | factory | `        if not Path(os.path.normpath(joined)).is_relative_to(os.path.normpath(workspace)):<LF>            return None<LF>` -> (removed) | RED | `f1_a_hostile_sidecar...[C:\outside\a.docx-size0]` |
| F3 | containment after `resolve` (junction) | factory | `            if not resolved.is_relative_to(workspace.resolve()):<LF>                return None<LF>` -> `            pass<LF>` | RED | `f1_a_junction_inside_the_workspace...` |
| F4 | office prompt needs a file | factory | `            if not source.is_file():` -> `            if not source.exists():` | RED | `f2_the_office_prompt_requires_a_file_not_a_directory` |
| F5 | office refusal is the U1 sentence | factory | `self.notify(darkside.plain(PATH_NOT_SUPPORTED), severity="error", markup=False)` -> `self.notify("archivo no encontrado", severity="error", markup=False)` | RED | `u1_a_refused_text...[office-\\h\s\x.docx-size0]` |
| F6 | office placeholder accepted by the grammar | factory | `"C:\\path\\to\\template.docx"` -> `"/ruta/a/plantilla.docx"` | RED | `u1_the_prompt_placeholder...[office]` |
| R1 | only `app` references the launcher | factory | `from mapper.osopen import safe_local_path` -> `from mapper.osopen import open_external, safe_local_path` | RED | `test_the_launcher_names_appear_only_in_app_and_osopen` |
| R2 | the architecture map says the ban | ARCHITECTURE.md | `` `open_external` is referenced only from `app` `` -> `only `app` may launch an OS handler` | RED | `test_the_architecture_map_says_what_the_modules_import` |

Runs: **28 mutants, 28 RED, 0 SURVIVED.** D4 and G4 are behaviourally equivalent mutants killed only by their AST arms (their purpose). Not mutated: the spies themselves; `_office_path`'s `except (OSError, ValueError)`;
the new-file `is_file()` of `open_external` is covered by D3 only through a patched `Path.is_file` (no real device exists in the test).

## 5. Renders (Pilot, real keys, HOME and USERPROFILE in a temp dir), 118x34

U1 toast (the toast is captured by wrapping `app.notify`; it is not part of the compositor frame the helper reads). `i` on Home, typed `\\h\s\x.csv`:

```
toasts: ['path not supported: use C:\\… or a relative path']      (the repr doubles the backslash: the text is  path not supported: use C:\… or a relative path)
frame contains typed text: False
a missing accepted path: toasts: ['archivo no encontrado: missing.csv']
```

Factory screen with a hostile sidecar `documents[].path` (`\\h\s\a.docx`, and `con`; both render identically); app running; the spies recorded no hit:

```
 browse maps    connect repo    build map    factory                                                          ◕ mapper
demo / proceso
 ▱
▸ proceso                                      plantilla

                                               archivo de plantilla no encontrado

                                               tags
                                               (sin tags)

next ▸ d edit document · i import office file · g generate office file
move j next sibling  k previous sibling  h parent  l child  0 back to start   factory q back … +6  ? all keys
```

Attachment add (`A`, typed `\\h\s\x.pdf`, enter): toast `path not supported: use C:\… or a relative path`; attachments stored: `[]`. Then `docs/x.pdf`: stored `[('file', 'docs/x.pdf')]`, the bottom
strip reads `adjunto agregado   docs/x.pdf` and the inspector lists `file · docs/x.pdf`:

```
                                                                                   adjuntos
                                                                                    file · docs/x.pdf
                                                                                      → docs/x.pdf
                                                                                   + agregar adjunto
 ▰▱   1/2
 adjunto agregado   docs/x.pdf
next ▸ j/k/h/l move · ↵ open card · / search
```

Not measured: terminals other than Textual's headless driver; widths other than 118 and 87 (the arms run both); the toast as a painted widget.

## 6. Test results, risks, carries, next

| check | state |
|---|---|
| `tests/test_inc9n.py`, `test_inc9m.py`, `test_inc9l.py`, `test_arch_osopen_callers.py` | executed: GREEN on the fix commits; RED run on `73c2670` in a worktree: 103 failed, 206 passed |
| 28 mutants | executed: 28 RED (section 4), pin re-checked |
| `ruff check . --exclude prototypes --output-format concise`, set difference vs `73c2670` on a CLEAN detached worktree (no arms copied in; line and column stripped) | executed: 28 lines on the base, 26 on HEAD; new = none; gone = the two F401 of `test_inc9m` (`CR-F6`) |
| `-W error::SyntaxWarning` compile of `osopen`, `github`, `app`, `screens/factory`, `test_inc9n`, `test_inc9m`, `test_arch_osopen_callers` | executed: clean |
| Literal Cf characters in every touched file (Python scan by Unicode category) | executed: none |
| Full default lane, once, uninterrupted, `-rf`, last step | see "Full-lane result" at the end |
| Known flakes (`test_llr_cnv_3_1...`, `test_hlr_n16_4...[size2]`, `test_palette::test_at_n03b...`) | see "Full-lane result" |
| `git stash` | not used |
| Network, loopback, a real UNC / `\??\UNC` path, a real console or COM device, a real cache, a real `gh` | not-run: spies refuse and record BEFORE the real call; `preview_csv` is a failing stub where a device name is typed |
| POSIX behaviour (`CR-F4`) | not-run (Windows only); recorded in `A-122` |

- **Risks.** (1) `FactoryScreen._office_path` now refuses a sidecar document that was stored as an absolute path OUTSIDE the workspace (it painted and generated from it before); the screen says
  `archivo de plantilla no encontrado`, and importing again copies it into `templates/`. By the ruling ("sidecar text is not typed text"). (2) The lazy `from mapper.app import PATH_NOT_SUPPORTED` in
  `factory.py` is a second `screens -> app` back-edge (the first, `_PromptScreen`, is recorded in section 3); the sentence could move to a shared module when `_PromptScreen` does. (3) `is_reserved()` is
  Python 3.12's list; a future name is not refused. (4) `resolve()` of a workspace-relative path still runs on an accepted text; a junction to a UNC share is refused only AFTER the resolve (a lookup of the
  junction target); not measured. (5) The attachment-open refusal for a hostile stored text no longer shows the text (U1 names nothing); the inspector still shows the real target (`LLR-N02.10`).
- **Not measured.** A real SMB share, a real console device, a real `gh`, a real clone; POSIX; terminals below 87 columns; the A7-style mutant (drop the helper from the attachment-add check) was not run
  because its arms type `\\h\s\x.pdf`, which the mutated code would `resolve()` against the network.
- **Carries.** `Inc-EN` (translate `archivo no encontrado`, T3, copy); moving `_PromptScreen` out of `app`; orphaned pre-`A-115` mirrors.
- **Next.** The independent reviews of `Inc-9n`, then `Inc-EN` on the operator's order.

## 7. Correction to record 039 (`INC9M-CR-F6`)

`increment-039` section 6 says `ruff ... set difference vs 19b2824 ... new = none`. That measurement is wrong as a claim about the tree: the base worktree it used had the new arms copied in, so the two
unused imports of `tests/test_inc9m.py` (`subprocess`, `textual.widgets.Static`) were in the "base" side as well, and the difference hid them. Measured here on a CLEAN base worktree: `tests/test_inc9m.py`
carried two F401 at `73c2670`; they are removed in `0faec7f`.

## Commits

`0faec7f` arms (strict xfail) · `effe32e` four sources + `ARCHITECTURE.md` + `A-122` + `OPEN_STEPS` emptied · `f06f6b6` junction arm + `A-122` wording · `6471156` this record + the correction note on 039 · `3117b0c` the U1 sentence through `darkside.plain` (census fix) · docs commit (the full-lane result).
No push; `state.json` untouched.

## Full-lane result

1 failed, 2344 passed, 24 deselected, 3 xfailed in 1570.52s (26:10), `-rf`, on `3117b0c`'s tree (the record and the lane result are docs commits after it; `test_no_operator_paths` reads `.dev-flow`).
Baseline 2221/0 plus 117 (`test_inc9n`) + 3 (`test_arch_osopen_callers`) + 4 (the painted-badge arm of `test_inc9m` grew from 2 to 6 cases) = 2345 run = 2344 passed + the 1 flake below. The 3 xfailed are the pre-existing ones.

- The one failure is the known flake FLAKE-3, `tests/test_palette.py::test_at_n03b_selecting_a_palette_entry_executes_it`: it passed 3 of 3 in isolation straight after (1.4 s each). It is not touched by this increment.
- This is the SECOND full-lane run, not a retry of a flake: the FIRST (on `6471156`, 2344 passed, 1 failed in 1527.91s) failed for real on `test_inc9.py::test_llr_n06_2_5_notify_sites_are_coerced` (see Decisions); that was fixed in `3117b0c`, the 28 mutants and the ruff difference were re-run on it
  (28 RED, ruff new = none), and the lane was run again from the start, uninterrupted.
