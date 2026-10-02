# Increment 041 -- Inc-9o: one containment helper, the document name (SEC-F1), V1, V2, FLAKE-3

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `63b2de3`. Authority: `VERDICT-inc9-2026-09-30.md` Round 11 (V1, V2; the operator took the recommended option on both) and the coordinator's
rulings for the Inc-9n reviews (`INC9N-SEC-F1`..`F3`, `INC9N-CR-F1`..`F5`). Amendment: `A-123` (appended to `01-requirements.md`, dated 2026-10-01).

## 1. What changed

- `mapper/osopen.py`: `confine(text, workspace) -> Path | None`, the ONLY containment; `lexically_outside(text, workspace) -> bool` (the same lexical step, for V2); the two sentence constants `PATH_NOT_SUPPORTED` (U1) and
  `PATH_OUTSIDE_WORKSPACE` (V1); `open_external`'s file branch calls `confine` (its own `resolve()` + `is_relative_to` is gone).
- `mapper/app.py`: `_is_workspace_file_target` and the `PATH_NOT_SUPPORTED` constant are deleted; `_path_refusal(text, workspace)` returns U1 (allow-list refuses) or V1 (`confine` refuses) or None, and both the attachment add and the
  attachment open use it. Constants are imported from `osopen`.
- `mapper/screens/factory.py`: `_office_path` is `confine(doc.path, workspace)` (the lexical + `resolve()` copy is deleted); `_missing_text(doc)` gives `template outside the workspace: import it with i` (V2) for the preview and the generate
  toast when the path is lexically outside, else the old text; `action_generate_office` runs `store.check_map_id` on the document name and the node id and passes `<name>-<id><suffix>` through `confine` before `office.resolve`; a refusal toasts
  `document name cannot be used as a file name`; the `generado:` toast names the workspace-relative result. `PATH_NOT_SUPPORTED` comes from `osopen` (the lazy `from mapper.app import PATH_NOT_SUPPORTED` is gone).
- `docs/ARCHITECTURE.md` section 3: `screens` may import `osopen.safe_local_path`, `confine`, `lexically_outside`, `PATH_NOT_SUPPORTED`; the four `screens` -> `app` back-edges listed with current lines.
- Tests: new `tests/test_inc9o.py` (81 cases); `tests/test_arch_osopen_callers.py` (new allowed set, back-edge test); sealed-arm changes (section 2); `tests/test_palette.py` (FLAKE-3).

Source files: **3** (`osopen.py`, `app.py`, `screens/factory.py`), under the ceiling of 4. Tests, `ARCHITECTURE.md` and records are not source files.

### The `confine` algorithm, as implemented

```
confine(text, workspace):
  1. local = safe_local_path(text)            # closed allow-list; expands `~` for EVERY caller; None -> None
  2. joined = abspath(Path(workspace) / local)       # no stat
     inside = Path(normcase(joined)).is_relative_to(normcase(abspath(workspace)))   # by path PARTS: ws2 is not inside ws
     not inside -> None
  3. current = abspath(workspace)
     for part in parts(joined) below the workspace root:        # the root itself is NOT checked (it may be a link)
         current = current / part
         try os.lstat(current)
           FileNotFoundError / NotADirectoryError -> stop walking (nothing deeper exists)
           any other OSError / ValueError         -> None          # fails closed
         if S_ISLNK(st_mode) or st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT -> None
  4. resolved = (Path(workspace) / local).resolve()
     resolved.is_relative_to(Path(workspace).resolve()) else None   # OSError / ValueError -> None
  return resolved
```

Policy, declared: **links inside the workspace are not followed.** `lexically_outside(text, ws)` is `safe_local_path(text) is not None and step 2 refuses`. Steps 1-3 call no `stat`, `resolve` or `_getfinalpathname` (an arm records them).

### Decisions (declared)

- **`lexically_outside` is a fifth name** `screens` imports from `osopen` (the ruling listed four: `safe_local_path`, `confine` and the two constants). V2 must tell "outside by text" from every other None without touching the disk, and `confine`'s signature is fixed. `factory`
  imports `PATH_NOT_SUPPORTED` only (not `PATH_OUTSIDE_WORKSPACE`), so the architecture arm allows exactly what is imported.
- **`~` is expanded by `safe_local_path` everywhere.** Behaviour change: `open_external` did not expand `~` before (`workspace / "~/x"` was a literal folder), so a `~/docs/x.pdf` attachment that was stored at add time could never open. They now agree (arm RED on the base).
- **The app's refusal at open is the V1 sentence** for an outside path (it was `fuera del espacio de trabajo: <text>`). `open_external` still returns `REFUSED_OUTSIDE` for other callers; the old status-word arms in `test_attachments` that call it directly are unchanged.
- **The workspace root is not walked** (only what lies under it): an operator may keep the workspace behind a link; the last `resolve()` check still compares to the resolved root.
- **Filename rules are `store.check_map_id`'s** (no `/ \ :`, controls, `<>"|?*`, surrogates, reserved device in the first dot-part, edge dot or space, length <= 100), applied to the document name and to the node id separately, without touching `store.py`
  (`screens` -> `store` is allowed by section 3). A name that passes `check_map_id` but whose `<name>-<id><suffix>` is refused by `confine` (e.g. a link standing where the file would be written) gets the same fixed toast.
- **The template check still runs first** in `action_generate_office`; a hostile name with a missing template toasts the template text. The suffix stays `Path(doc.path).suffix or ".docx"` (a suffix with a `:` cannot reach a write: `office.resolve` needs a known kind).
- The three new factory toasts go through `darkside.plain(...)`, `markup=False` (the census `test_llr_n06_2_5_notify_sites_are_coerced` caught the first form).
- FLAKE-3 is a **test-hygiene change that keeps the oracle**: the assertions are unchanged; only the wait before them is a bounded poll on `palette._items`.

## 2. Sealed-arm changes

| arm | change | justification |
|---|---|---|
| `test_inc9n::test_inc9n_f1_a_hostile_sidecar_document_is_never_stat_ed_and_the_screen_survives[C:\outside\a.docx x 2 sizes]` | expects the V2 text (frame and generate toast); the four other hostile forms keep `archivo de plantilla no encontrado`; committed RED (step `v2`) | V2 (Round 11): an absolute template outside the workspace says so. The spy assertion (zero hits) is unchanged |
| `test_inc9n::test_inc9n_f1_a_dotdot_document_that_leaves_the_workspace_is_refused` | expects V2 | V2 |
| `test_inc9n::test_inc9n_u2_adding_a_non_local_file_stores_nothing_and_toasts_the_sentence[C:\outside-ws\x.pdf, ..\x.pdf x 2 sizes]` | expects V1; `\\h\s\x.pdf`, `/x.pdf`, `con` keep U1; committed RED (step `v1`) | V1. Nothing stored, no snapshot: unchanged assertions |
| `test_inc9n::test_inc9n_u1_pin_a_file_attachment_outside_the_workspace_keeps_its_own_refusal` | `notes == [V1]` (was `REFUSED_OUTSIDE in notes[0]` and `U1 not in notes`) | V1 at open time |
| `test_attachments::test_at_n02d_a_refused_attachment_is_reported_not_silently_dropped` | `notes == [V1 sentence]` (was `REFUSED_OUTSIDE in notes[0]`); the refusal is still visible and the launcher still untouched | V1 at open time |
| `test_arch_osopen_callers`: `test_outside_app_only_safe_local_path_is_imported_from_osopen` renamed `..._only_the_allowed_names_are_imported_from_osopen`; the architecture-map arm also asks for the four names | the allowed set grew by `confine`, `lexically_outside`, `PATH_NOT_SUPPORTED` in `screens/factory.py` | `A-123` item 7; the set is still derived from the ASTs |
| `test_darkside_census::test_hue_census_every_severity_and_busy_site_is_classified` (the register key of `factory.py`) | the key `return Text.assemble(("archivo de plantilla no encontrado", darkside.ALERT))` is now `return Text.assemble((self._missing_text(doc), darkside.ALERT))`; same severity (ALERT), same job | found by the FIRST full lane (1 failed, 2426 passed): the census keys on the source text of the site, which V2 changed. No hue or severity changed |
| `test_palette::test_at_n03b...`, `test_palette_empty_query_dispatches_nothing` | `pilot.pause()` -> `_until(pilot, <predicate on palette._items>)` (<= 20 pauses); assertions unchanged | FLAKE-3, a test race |

No assertion that a refusal leaks the typed text was weakened; V1 and V2 name nothing typed.

## 3. Arm table (RED/GREEN)

The arms were committed as strict xfail in `e781be2` (no source touched), the keys corrected in `b518c09` after the first RED measurement (below), then RED measured on a detached `git worktree` of `63b2de3` in `%TEMP%` (no stash) with the final test files copied in and
`--runxfail`: **80 failed, 151 passed** across `test_inc9o` (81 cases: 68 RED, 13 pins), `test_inc9n` (8 RED), `test_attachments` (1 RED), `test_arch_osopen_callers` (3 RED). The same files in plain mode on the base: 13 passed, 68 xfailed for `test_inc9o`.
The first RED measurement showed four wrong keys: two pins keyed RED that pass on the base (`v1` UNC open x2, `v2` template behind a link), a parameter that passes on the base because `resolve()` caught it (`open_external` through a junction that leads out), and one RED arm that was not keyed
(the `~` at open: `open_external` never expanded it). Corrected before the fix. GREEN: all of them pass on `e56662d` (271 passed over the five files incl. `test_inc9.py`).

| arm family | cases | on `63b2de3` | on HEAD |
|---|---|---|---|
| `confine` accepts: relative, bare name, `..` that stays inside, drive-absolute inside, upper-cased drive-absolute | 5 | RED x5 (no `confine`) | green |
| `confine` refuses with NO filesystem call (`_no_fs`): `..`, `..\ws2\x`, `ws2` absolute, `ws2` itself, `ws-extra` string prefix, the parent, `C:\outside`, deep `..`, UNC, `\??\UNC`, DOS device, empty, leading dash (CR-F5 sibling cases included) | 13 | RED x13 | green |
| relative workspace (`chdir` + `Path("ws")`): `confine`, and the real factory screen with an absolute template inside | 2 | RED x2 | green |
| `~` the same for every caller (`confine`; add and open through the app, home inside and outside the workspace) | 1 + 2 | RED x3 | green |
| walk (junction AND symlink x first/last/nested component): `None`, spies on `os.stat`, `Path.resolve`, `os.path.realpath`, `nt._getfinalpathname`, `Path.stat/exists/is_file` record NOTHING; `lstat` is the allowed call and stops at the link | 6 | RED x6 | green |
| walk: a junction that stays INSIDE the workspace is refused (policy); prefixes checked in order and the walk stops at the link; fails closed on an uninspectable component | 3 | RED x3 | green |
| final `resolve()` check kept (`resolve` monkeypatched to return an outside path; raising `OSError` / `ValueError` -> None) | 3 | RED x3 | green |
| `open_external`: a junction inside the workspace is refused (both: leads out, stays in); relative workspace; pins: real directories / a missing file / a workspace that is itself a link | 2 + 1 + 2 | RED x3 (leads-out passes on the base), pin | green |
| one containment, one home: no `is_relative_to`/`normpath`/`abspath` and no sentence text in `app`/`factory`; constants equal the literals | 1 | RED | green |
| V1 at add (real keys, 118 and 87): `C:\outside\x.pdf`, `..\x.pdf` -> V1, nothing stored; `\\h\s\x.pdf` -> U1 (a `resolve` spy: zero hits); `docs/x.pdf` stored | 4 RED + 2 + 1 pins | RED x4 | green |
| V1 at open (118, 87): `C:\outside\x.pdf`, `..\..\etc\x.pdf`, a path behind a link -> V1; UNC -> U1; launcher untouched | 4 + 1 RED, 2 pin | RED x5 | green |
| V2: absolute existing template outside, 118 and 87, **zero stats of that path** (a spy that refuses), frame and generate toast; `..\secret.docx`; pins: UNC, `//h/s`, `con`, a missing in-workspace template keep the old text; a template behind a link keeps the old text | 2 + 1 RED, 5 pins | RED x3 | green |
| SEC-F1 name arms (118 and 87): `..\..\ESCAPED`, `\\h\s\x`, `C:\Windows\Temp\x`, `con`, `a/b`, `x:y`: fixed toast, the workspace tree identical before and after, spies with the hostile forms record zero | 12 | RED x12 | green |
| SEC-F1: node ids `a:b`, `con`, `x.`, `a b `; a link standing where the output would be written | 4 + 1 | RED x5 | green |
| SEC-F1 pin: a normal name still writes `plantilla-root.docx` inside the workspace and toasts `generado: plantilla-root.docx` | 1 | pin | green |
| arch: the allowed names, the four back-edges (derived from the ASTs) listed in the map with their lines, the map names the four imports | 3 | RED x3 | green |
| sealed arms changed (section 2; the census key was found by the first full lane, not by an arm) | 9 | RED x9 | green |

Not claimed by the arms: a hostile name on the BASE was spied (refuse and record BEFORE the real call), so the RED run itself touched nothing outside `tmp_path`; no real UNC, console or COM device, and no link to a network target was created.

## 4. Mutant table

Harness `mutate9o.py` in the session scratchpad, outside the repo, on a detached `git worktree` of `e56662d` in `%TEMP%`; sha256 pinned before (`osopen.py` `51f526fb0996d198`, `app.py` `0939a1625ac1ced7`, `factory.py` `43e88c6f98384727`,
`ARCHITECTURE.md` `80841ab214ccc44e`), byte-level I/O in each file's own line ending (CRLF here), `old` must occur exactly once, the verdict printed before the file is restored, the pin re-checked after each restore and at the end: **pins re-checked: OK**.
Run `-x` on `tests/test_inc9o.py` (the arch mutants on `tests/test_arch_osopen_callers.py`). `<LF>` is a line break; backslashes are as in the file. **33 mutants: 31 RED, 2 SURVIVED (both behaviourally equivalent on Windows, see below).**

| id | claims | file | old -> new (exact) | verdict | first arm to fail |
|---|---|---|---|---|---|
| W1 | the reparse-point walk | osopen | `    for part in Path(joined).parts[len(root.parts):]:` -> `    for part in ():` | RED | `refuses_a_link_before_any_stat...[the link is the first component-junction]` |
| L1 | the lexical step | osopen | `    joined = _lexically_inside(local, workspace)<LF>    if joined is None:<LF>        return None<LF>    root = ` -> `    joined = os.path.abspath(Path(workspace) / local)<LF>    root = ` | RED | `refuses_without_touching_the_disk[dot-dot out]` |
| S1 | a sibling prefix is not inside | osopen | `    if Path(os.path.normcase(joined)).is_relative_to(os.path.normcase(root)):` -> `    if os.path.normcase(joined).startswith(os.path.normcase(root)):` | RED | `...[dot-dot into the sibling ws2 ...]` |
| C1 | case folding | osopen | the same line -> `    if Path(joined).is_relative_to(root):` | **SURVIVED, equivalent**: `WindowsPath` compares case-insensitively; the arm with an upper-cased workspace is a pin of that, not of `normcase` | - |
| P1 | a junction (reparse point) is a link | osopen | `    return stat.S_ISLNK(info.st_mode) or bool(<LF>        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)` -> `    return stat.S_ISLNK(info.st_mode)` | RED | `refuses_a_link...[the link is the first component-junction]` |
| P2 | a symlink is a link | osopen | the same two lines -> `    return bool(getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)` | **SURVIVED, equivalent on Windows**: a symlink carries the reparse attribute there (the symlink arms run and pass); `S_ISLNK` matters on POSIX, not measured | - |
| R1 | the last `resolve()` containment | osopen | `        if not resolved.is_relative_to(Path(workspace).resolve()):<LF>            return None<LF>` -> `        pass<LF>` | RED | `judges_what_resolve_returns_as_a_last_check` |
| R2 | `OSError` from `resolve()` | osopen | `    except (OSError, ValueError):<LF>        return None<LF>    return resolved` -> `    except ValueError:<LF>        return None<LF>    return resolved` | RED | `refuses_when_the_final_resolve_fails[error0]` |
| R3 | an uninspectable component fails closed | osopen | `        except (OSError, ValueError):<LF>            return None<LF>        if _is_link(info):` -> `        except (OSError, ValueError):<LF>            break<LF>        if _is_link(info):` | RED | `fails_closed_when_a_component_cannot_be_inspected` |
| N1 | a missing component is not an error | osopen | `        except (FileNotFoundError, NotADirectoryError):<LF>            break` -> `        except (FileNotFoundError, NotADirectoryError):<LF>            return None` | RED | `accepts_a_path_inside_the_workspace[relative]` |
| A0 | `confine` applies the allow-list | osopen | `    local = safe_local_path(text)<LF>    if local is None:<LF>        return None<LF>    joined = ` -> `    local = Path(text)<LF>    joined = ` | RED | `refuses_without_touching_the_disk[a DOS device]` |
| O1 | `open_external` uses `confine` | osopen | `    resolved = confine(target, Path(workspace))<LF>    if resolved is None:<LF>        return REFUSED_OUTSIDE` -> `    resolved = (Path(workspace) / target).resolve()<LF>    if not resolved.is_relative_to(Path(workspace).resolve()):<LF>        return REFUSED_OUTSIDE` | RED | `open_external_refuses_a_link_inside_the_workspace[False]` |
| X1 | V2 fires | osopen | `    return local is not None and _lexically_inside(local, workspace) is None` -> `    return False` | RED | `v2_an_absolute_template_outside...[size0]` |
| X2 | a refused text is not "outside" | osopen | the same line -> `    return local is None or _lexically_inside(local, workspace) is None` | RED | `v2_pin_every_other_missing_template...[\\h\s\a.docx]` |
| T1 | the V1 text | osopen | `PATH_OUTSIDE_WORKSPACE = "attachment must be inside the workspace: use a relative path"` -> the same with a final `.` | RED | `there_is_one_containment_and_one_home_for_the_sentences` |
| A1 | a refused text gets U1 | app | `    if safe_local_path(text) is None:<LF>        return PATH_NOT_SUPPORTED` -> `    if safe_local_path(text) is None:<LF>        return PATH_OUTSIDE_WORKSPACE` | RED | `v1_adding_a_unc_file_still_toasts_the_allow_list_sentence[size0]` |
| A2 | an outside path gets V1 | app | `    if confine(text, workspace) is None:<LF>        return PATH_OUTSIDE_WORKSPACE` -> `    if confine(text, workspace) is None:<LF>        return PATH_NOT_SUPPORTED` | RED | `v1_adding_an_outside_file...[C:\outside\x.pdf-size0]` |
| A3 | the helper asks `confine` | app | the same two lines -> `    if False:<LF>        return PATH_OUTSIDE_WORKSPACE` | RED | same |
| A4 | add validates | app | `            refusal = _path_refusal(target, self.store.workspace) if kind == "file" else None` -> `            refusal = None` | RED | same |
| A5 | open validates | app | `        refusal = _path_refusal(att.path, self.store.workspace) if att.kind == "file" else None` -> `        refusal = None` | RED | `v1_opening_an_outside_file...[C:\outside\x.pdf-size0]` |
| F1 | the office path is confined | factory | `        return confine(doc.path, Path(self.app.store.workspace))  # type: ignore[attr-defined]` -> `        return Path(self.app.store.workspace) / doc.path  # type: ignore[attr-defined]` | RED | `v2_an_absolute_template_outside...[size0]` |
| F2 | V2 | factory | `        if doc.path and lexically_outside(doc.path, Path(self.app.store.workspace)):  # type: ignore[attr-defined]` -> `        if False:  # type: ignore[attr-defined]` | RED | same |
| F3 | V2 in the preview | factory | `                return Text.assemble((self._missing_text(doc), darkside.ALERT))` -> `                return Text.assemble((TEMPLATE_MISSING, darkside.ALERT))` | RED | same |
| F4 | V2 in the generate toast | factory | `self.notify(darkside.plain(self._missing_text(doc)), severity="error", markup=False)` -> `self.notify(darkside.plain(TEMPLATE_MISSING), severity="error", markup=False)` | RED | same |
| F5 | the filename check (both names) | factory | `            check_map_id(self.document_name)<LF>            check_map_id(node.id)` -> `            pass` | RED | `sec_f1_a_hostile_document_name...[con-size0]` |
| F5b | the node id check | factory | `            check_map_id(node.id)` -> `            pass` | RED | `sec_f1_a_hostile_node_id_writes_nothing[a:b]` |
| F5c | the document name check | factory | `            check_map_id(self.document_name)<LF>` -> `            pass<LF>` | RED | `...[con-size0]` |
| F6 | the output target is confined | factory | `        target = confine(f"{self.document_name}-{node.id}{suffix}", Path(store.workspace))<LF>        if target is None:` -> `        target = Path(store.workspace) / f"{self.document_name}-{node.id}{suffix}"<LF>        if target is None:` | RED | `sec_f1_a_link_where_the_output_would_be_written_is_refused` |
| F7 | the fixed refusal text | factory | `NAME_NOT_USABLE = "document name cannot be used as a file name"` -> the same with a final `.` | RED | `sec_f1_...[..\..\ESCAPED-size0]` |
| F8 | `screens` do not import the launcher | factory | `from mapper.osopen import PATH_NOT_SUPPORTED, confine, lexically_outside, safe_local_path` -> the same with `open_external, ` added | RED | `test_the_launcher_names_appear_only_in_app_and_osopen` |
| F9 | no private copy of the U1 sentence | factory | the same import -> `from mapper.osopen import confine, lexically_outside, safe_local_path<LF>PATH_NOT_SUPPORTED = "path not supported: use C:\\\u2026 or a relative path"` | RED | `there_is_one_containment_and_one_home_for_the_sentences` |
| D1 | the map lists `confine` | ARCHITECTURE.md | `` `osopen.confine`, `` -> (removed) | RED | `test_the_architecture_map_says_what_the_modules_import` |
| D2 | the map's back-edge lines are current | ARCHITECTURE.md | `` `mapper/screens/factory.py:146` (`keybar_groups`) `` -> `...:343` | RED | `test_the_four_known_back_edges_are_exactly_the_ones_the_map_lists` |

Not mutated: the spies themselves; the `os.path.abspath` call (equivalent to `normpath` of an absolute path); `confine`'s `except ValueError` clause of the walk (`os.lstat` raises it for a NUL, which `safe_local_path` refuses first); the A7-style mutant that drops
`safe_local_path` from the add check was NOT run with a UNC arm (the arms spy `resolve`, but no mutant was run that lets one through). The `generado:` toast's relative name equals `target.name` at the workspace root, so a mutant on it would be equivalent.

## 5. Renders (Pilot, real keys, HOME and USERPROFILE in a temp dir; the harness is `render9o.py` in the scratchpad)

Toasts are captured by wrapping `notify` (they are not part of the compositor frame). At 118 columns, the same at 87:

```
add  C:\outside\x.pdf   toasts=['attachment must be inside the workspace: use a relative path']   stored=[]          (V1)
add  \\h\s\x.pdf        toasts=['path not supported: use C:\… or a relative path']                stored=[]          (U1)
add  docs/x.pdf         toasts=[]                                                                  stored=[('file', 'docs/x.pdf')]
open C:\outside\x.pdf   notes=['attachment must be inside the workspace: use a relative path']     launched=[]        (V1)
```

V2, the factory preview of an absolute existing template outside the workspace (118x34), then the generate toast `['template outside the workspace: import it with i']`:

```
 browse maps    connect repo    build map    factory                                                          ◕ mapper
demo / proceso
 ▱
▸ proceso                                      plantilla

                                               template outside the workspace: import it with i

                                               tags
                                               (sin tags)

next ▸ d edit document · i import office file · g generate office file
move j next sibling  k previous sibling  h parent  l child  0 back to start   factory q back … +6  ? all keys
```

At 87x34 the text is identical (the right pane starts at column 34; `… +8` in the key bar). The generate refusal and a normal generate, same session:

```
generate name='..\\..\\ESCAPED' : toasts=['document name cannot be used as a file name']
generate name='plantilla'       : toasts=['generado: plantilla-root.docx']
files under the workspace afterwards: .mapper\state.json, att.mmd, att_nodos.yml, docs\t.docx, mapper.db, plantilla-root.docx
a file named ESCAPED* anywhere under the temp root: none
```

Not measured: terminals other than Textual's headless driver; widths other than 118 and 87; the toast as a painted widget.

## 6. Test results, risks, carries, next

| check | state |
|---|---|
| `tests/test_inc9o.py` (81), `test_inc9n`, `test_attachments`, `test_arch_osopen_callers`, `test_inc9` | executed: 271 passed on `e56662d`; RED run on `63b2de3` in a worktree: 80 failed, 151 passed |
| 33 mutants | executed: 31 RED, 2 SURVIVED (C1, P2: equivalent on Windows), pins re-checked OK |
| FLAKE-3: the two palette arms, 30 runs each on HEAD after the fix | executed: `test_at_n03b...` **30/30**, `test_palette_empty_query_dispatches_nothing` **30/30**, each in its own process; the whole `tests/test_palette.py` **30/30**. Isolated runs under-measure a race seen under the full lane's load; the full-lane result below is the real test |
| `ruff check . --exclude prototypes --output-format concise`, set difference vs `63b2de3` on a CLEAN detached worktree (line and column stripped) | executed: 26 on the base, 26 on HEAD; new = none; gone = none |
| `-W error::SyntaxWarning` compile of `osopen`, `app`, `screens/factory`, `test_inc9o`, `test_inc9n`, `test_arch_osopen_callers`, `test_palette`, `test_attachments` | executed: clean |
| Literal Cf characters in every touched file and `01-requirements.md` (Python scan by Unicode category) | executed: none |
| Full default lane, once, uninterrupted, `-rf`, last step | see "Full-lane result" at the end |
| `git stash` | not used |
| Network, loopback, a real UNC / `\??\UNC` path, a real console or COM device, a link to a network target, a real cache, a real `gh`, a real profile path | not-run: spies refuse and record BEFORE the real call; links are junctions/symlinks to a LOCAL temp directory |
| POSIX behaviour | not-run (Windows only) |

- **Risks.** (1) The walk refuses any reparse point under the workspace. A workspace under a cloud-sync folder whose placeholder files carry a reparse attribute (OneDrive and similar) would have those files refused, at add, open, preview and generate; **not measured**. (2) A time-of-check
  window remains between the walk and the write (a component swapped for a link): not closed, declared in `A-123`. (3) A hard link is not detected. (4) `check_map_id` also refuses a document name or node id over 100 characters or with `<>"|?*`: a sidecar with such an id can no longer generate (the toast says so, nothing is written).
  (5) `~` now opens (it did not before); an operator whose home is not under the workspace gets V1 at add, as intended. (6) `screens/factory.py` now imports `mapper.store` (allowed by section 3). (7) The lazy `from mapper.app import ...` back-edges are four, not one; unchanged in number by this increment (`PATH_NOT_SUPPORTED` left the third site).
- **Not measured.** A real SMB share, a real console device, a real `gh`, a real clone, OneDrive/cloud placeholders, POSIX, terminals below 87 columns, a workspace that is itself a link on a network drive.
- **Carries.** `Inc-EN` (translate `archivo no encontrado`, `archivo de plantilla no encontrado`, `generado:`, `no se pudo generar`, the new English strings are already English); moving `_PromptScreen` and the two helpers out of `app` (the four back-edges); the TOCTOU window.
- **Next.** The independent reviews of `Inc-9o`, then `Inc-EN` on the operator's order.

## Commits

`e781be2` arms (strict xfail) · `b518c09` four RED keys corrected · `e56662d` three sources + `ARCHITECTURE.md` + test files with `OPEN_STEPS` emptied + FLAKE-3 · docs commit (`A-123`, this record, the full-lane result).
No push; `state.json` untouched.
