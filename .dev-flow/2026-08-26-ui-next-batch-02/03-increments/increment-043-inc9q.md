# Increment 043 -- Inc-9q: stream suffix and MAX_PATH (SEC-F1/F4), hard links at open (SEC-F3), parent re-check (SEC-F2), X1, X2, one reason mapping (CR-F1/F3)

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `55dc530`. Authority: `VERDICT-inc9-2026-09-30.md` Round 13 (operator X1, X2; coordinator rulings) and the review findings `INC9P-SEC-F1`..`F4`, `INC9P-CR-F1`..`F8`. Amendment: `A-125` (appended to `01-requirements.md`, dated 2026-10-02).

## 1. What changed

- `mapper/osopen.py` (source 1)
  - **Step 1b** of `confine_reason` also refuses, on the text and before any filesystem call, a `:` in any component but the drive anchor (`lnk:$I30`, `lnk::$BITMAP`, `lnk:$I30:$BITMAP`, `JLINKN~1:$I30`) as `normalised`.
  - **Defence in depth, option implemented: resolve only the walked prefix, then append the unwalked tail lexically** (`walked.resolve().joinpath(*tail)`). The other offered option (resolve the whole path, compare with prefix + tail) is NOT implemented. Plus: a not-found at 260 characters or more is `unreadable` (MAX_PATH, SEC-F4).
  - `hard_linked(path)` (moved from `factory`; False only on FileNotFoundError, any other `OSError` is True), `open_external` returns `ATTACHMENT_HARD_LINKED` for `st_nlink > 1`; `is_link` made public; `refusal_sentence(reason, *, surface="attachment")`; `PATH_TEMPLATES_UNCHECKED`; `lexically_outside` deleted.
- `mapper/app.py` (source 2): `_path_refusal` is `refusal_sentence(reason)`; the open path shows `ATTACHMENT_HARD_LINKED` as the toast (no path appended).
- `mapper/screens/factory.py` (source 3): X1 constants (`TEMPLATE_HARD_LINKED`, `OUTPUT_HARD_LINKED`, `IMPORT_HARD_LINKED`); `_template` returns the `confine_reason` tuple once, `_office_path` is its `[0]`, `_missing_text(reason)` (X2: `link`, `allow_list`, `normalised` through `refusal_sentence`; `outside` V2; the rest "not found"); the import calls `refusal_sentence(reason, surface="import")`; `_import_refusal` and `_hard_linked` deleted; `_write_via_sibling` re-`lstat`s the parent after `mkstemp` and raises `ParentIsALink` for a link (residual TOCTOU narrowed, not closed).
- Not source: `docs/ARCHITECTURE.md` (rows `screens`, `osopen`, back-edge lines 198/217/498), `01-requirements.md` (`A-125`), tests. **3 source files, within the cap (expected 3, ceiling 4).**

### `confine_reason`, as implemented

1. `safe_local_path` (closed allow-list) -> `allow_list`.
1b. text only, no filesystem call: a component (not `.`/`..`) ending in a dot or space, or any `:` in a component other than the drive anchor (`local.parts[0]` when `local.anchor`) -> `normalised`.
2. lexical containment (`abspath`, `normcase`, by parts) -> `outside`.
3. walk from the workspace root down with `os.lstat`; a symlink or reparse point -> `link`; not-found/not-a-directory: if the path text is 260 characters or longer -> `unreadable`, else stop and keep the rest as the tail; any other `OSError`/`ValueError` -> `unreadable`.
4. with a tail: `walked.resolve().joinpath(*tail)`; without: `(workspace / local).resolve()`; then `is_relative_to(workspace.resolve())` -> else `outside`; an `OSError`/`ValueError` -> `unreadable`; otherwise `(resolved, "ok")`.

### Sentences (exact)

- X1 template: `template has several hard links: replace it with a plain copy`; output: `output file has several hard links: delete or rename it`; import target: `templates file has several hard links: delete or rename it`.
- Attachment at open (SEC-F3, coordinator): `attachment has several hard links: replace it with a plain copy`.
- Import, unreadable (CR-F3, coordinator): `templates folder could not be checked: use a real folder named templates inside the workspace`.
- X2: U1 `path not supported: use C:\u2026 or a relative path` for a refused template.

## 2. Sealed-arm changes

| File | Arm | Change | Why |
|---|---|---|---|
| `tests/test_inc9o.py` | `..v2_pin_every_other_missing_template_keeps_the_existing_text` | params UNC, `//h/s/a.docx`, `con` expect U1 (was "not found"); `docs/missing.docx` keeps it | **X2, operator-ruled sealed-arm change** |
| `tests/test_inc9n.py` | `..f1_a_hostile_sidecar_document_is_never_stat_ed_and_the_screen_survives` | UNC, `//h/s`, `\??\UNC`, `con` expect U1 (was "not found"); `C:\outside\a.docx` keeps V2 | X2, same |
| `tests/test_inc9p.py` | `..sec_f1_the_factory_preview_never_touches_a_link_behind_a_normalised_part` | expects U1 (was "not found") | X2 |
| `tests/test_inc9p.py` | `..w2_pin_the_other_template_refusals_keep_the_old_text` (renamed `..say_u1_or_not_found`) | UNC, `con`, `d /a.docx` expect U1; `docs/missing.docx` "not found" | X2 |
| `tests/test_inc9p.py` | the three hard-link arms (target, template, import) | expect the three X1 sentences (was the single Inc-9p sentence) | X1 |
| `tests/test_inc9p.py` | `..lexically_outside_is_the_outside_reason_of_confine_reason` (renamed `..confine_reason_outside_is_the_lexical_step`) | the `lexically_outside` assertion removed; the `confine_reason` table stays | CR-F4 |
| `tests/test_inc9o.py` | `..opening_a_file_behind_a_link_toasts_the_workspace_sentence` | renamed `..toasts_the_link_sentence`; assertion (W2) unchanged | **CR-F8, a label change** |
| `tests/test_inc9o.py` | `..confine_judges_what_resolve_returns_as_a_last_check` | creates `a.pdf` first (the walk then reaches the end and `resolve()` is asked about the whole path); a counterpart for a missing file is `test_inc9q_sec_f4_the_resolved_walked_prefix_is_the_last_check_for_a_missing_file` | the tail option makes `resolve()` see the prefix for a missing file; changed in the implementation commit, not RED first (green before and after) |
| `tests/test_arch_osopen_callers.py` | allowed names, docs check | `factory` imports `safe_local_path`, `confine_reason`, `refusal_sentence`, `hard_linked`, `is_link`, `PATH_NOT_SUPPORTED`, `PATH_THROUGH_LINK` (`PATH_OUTSIDE_WORKSPACE` out) | names changed |
| `tests/test_darkside_census.py` | one pinned source line | `self._missing_text(doc)` -> `self._missing_text(reason)` | `_missing_text` takes the reason (CR-F5); changed in the implementation commit |

No arm was weakened: every changed expectation names a new cause or is stricter, except the `last_check` setup (same assertion, different setup) and the two census/label changes, which are declared above.

## 3. Arm table (RED/GREEN)

RED = `40b33e6` (the arms, strict xfail; sources of `55dc530`) with `--runxfail` in a separate `git worktree` under `%TEMP%` (removed): `tests/test_inc9q.py tests/test_inc9p.py tests/test_inc9o.py tests/test_inc9n.py tests/test_arch_osopen_callers.py`, **71 failed, 273 passed**; 71 = the 71 xfail marks, one for one (they also passed as `71 xfailed` on the committed arms head, 0 XPASS). GREEN = the implementation commit, same five files plus `test_inc9m`, `test_attachments`, `test_palette`, `test_darkside_census`: 295 passed on the targeted run before the final lane (see Full-lane result for the lane).

| Step | Arms (RED on base) | Closed by |
|---|---|---|
| `colon` (SEC-F1) | 2 targets x 6 forms x 2 tails = 24 (zero `os.stat`/`lstat`/`resolve`/`_getfinalpathname` calls, `(None, "normalised")`), + `open_external` with an inside junction (measured: returned `abierto` and called the launcher on the base) = 25 | step 1b |
| `maxpath` (SEC-F4) | 340+ character path through a junction made with `\\?\`, junction pointing outside and inside = 2 (on the base: `ok`) | not-found >= 260 is `unreadable` |
| `tail` (SEC-F1 b) | `lstat` made to lie about `lnk`; the OS must never be asked about `lnk` = 1 | prefix resolved, tail appended |
| `f3` | open toast through the app 1, `open_external` 1, `hard_linked` fails closed 3, `open_external` fails closed 1 = 6 | `hard_linked`, `ATTACHMENT_HARD_LINKED` |
| `f2` | folder swapped for a junction after `mkstemp` (import) = 1 | re-`lstat` of the parent |
| `x1` (in `test_inc9p`) | target, template, import = 3 | three constants |
| `x2` | `test_inc9p` preview at two widths 2 + 3 params, `test_inc9o` 3 params, `test_inc9n` 4 params x 2 widths = 16 | `_missing_text(reason)` |
| `cr1` | sentence map 5, import surface 1, one home 1, app shared mapping 1, import shared mapping 1, import `unreadable` toast at two widths 2 = 11 | `refusal_sentence` |
| `cr4` | `lexically_outside` removed = 1 | deleted |
| `cr5` | preview asks once: 3 params (missing, normalised, link) = 3 | `_template` |
| `arch9q` | allowed names, docs row = 2 | names, `docs/ARCHITECTURE.md` |

Total 25 + 2 + 1 + 6 + 1 + 3 + 16 + 11 + 1 + 3 + 2 = **71**, equal to the pytest count of failures on the arms commit.

Pins (green on the base, killed by a mutant instead): ordinary drive-absolute, relative, `./` and not-yet-existing paths (`sec_f1_pin_ordinary_paths_still_work`); a missing tail is prefix + tail; a workspace that is itself a link still generates; an unreadable template keeps "not found" (two widths); `office.resolve` raising during generate (CR-F2); `..\d \x.pdf` is `normalised` (CR-F7); the outside-junction `open_external` form; a missing template keeps "not found".

## 4. Mutant table

Harness: `%TEMP%\inc9q-harness\mut.py` (outside the repo). Byte-level read and write in each file's own line endings (the three sources are CRLF), a sha256 pin of each file checked after every restore, the verdict printed before the restore, `-B`, `-x`. Pins (clean implementation head): `osopen.py 4104f5a9fa02400b8d122949bfccf4fc99b8874f383ed3989273d1091e786c1d`, `app.py f86b21e9bc82b060987819fe5099123c11bc0b17b7164dd9f902994752cd0667`, `factory.py ac46d13aa5b1f71a4aafe4cc7e598f50b4a72df6ecd7461eb9636deabb0bd6bc` (the `factory.py` pin is the one AFTER the simplification below; first run pinned `f9db2f44...8096`). Pins re-checked after both runs: OK.
Suites: `tests/test_inc9q.py` unless the killing test names `inc9p:`. **24 mutants run, 23 in the table killed, 1 survived and led to a code change (below).**

**Survivor, and what it changed.** `Q11 F2 refuses a workspace that is a link` (factory: `if not was_link and is_link(target.parent.lstat()):` -> `if is_link(target.parent.lstat()):`) SURVIVED: the first draft compared the parent's state before and after `mkstemp` so as not to refuse a workspace root that is a link. The mutant showed it was dead code: `target` comes from `confine_reason` (resolved), so its parent is never a link unless swapped. The comparison (`was_link`) was removed; Q10 was re-run on the simplified code (killed).

| # | Arm claimed | File: exact text -> mutant text | Verdict: killing test |
|---|---|---|---|
| Q1 | F1 colon check dropped | osopen.py: `any(":" in part for part in components) or any(` -> `any(False for part in components) or any(` | killed: `sec_f1_a_stream_suffix_on_a_link_component_is_refused_before_any_filesystem_call[outside-lnk:$I30-lnk-/x.pdf]` |
| Q2 | F1 drive anchor not exempt | osopen.py: `components = local.parts[1:] if local.anchor else local.parts` -> `components = local.parts` | killed: `sec_f1_pin_ordinary_paths_still_work` |
| Q3 | F4 MAX_PATH guard off | osopen.py: `if len(os.fspath(current)) >= _MAX_PATH:` -> `if False:` | killed: `sec_f4_a_340_character_path_with_a_junction_is_never_ok[outside]` |
| Q4 | F4 tail resolved by the OS | osopen.py: `resolved = walked.resolve().joinpath(*tail)` -> `resolved = (Path(workspace) / local).resolve()` | killed: `sec_f4_the_unwalked_tail_is_appended_not_resolved` |
| Q5 | F4 tail dropped | osopen.py: `resolved = walked.resolve().joinpath(*tail)` -> `resolved = walked.resolve()` | killed: `sec_f1_pin_ordinary_paths_still_work` |
| Q6 | F3 hard_linked fails open | osopen.py: `except OSError:\n        return True` -> `except OSError:\n        return False` | killed: `sec_f3_hard_linked_returns_false_only_when_the_file_is_not_found[error1-True]` |
| Q7 | F3 hard_linked not-found is True | osopen.py: `except FileNotFoundError:\n        return False` -> `except FileNotFoundError:\n        return True` | killed: `sec_f3_hard_linked_returns_false_only_when_the_file_is_not_found[error0-False]` |
| Q8 | F3 open_external ignores hard links | osopen.py: `if hard_linked(resolved):` -> `if False:` | killed: `sec_f3_opening_a_hard_linked_attachment_toasts_the_sentence_and_launches_nothing` |
| Q9 | F3 app does not show the sentence | app.py: `elif status == ATTACHMENT_HARD_LINKED:` -> `elif False:` | killed: `sec_f3_opening_a_hard_linked_attachment_toasts_the_sentence_and_launches_nothing` |
| Q10 | F2 parent re-check off | factory.py: `if is_link(target.parent.lstat()):` -> `if False:` | killed: `sec_f2_a_folder_swapped_for_a_junction_after_mkstemp_is_refused` |
| Q12 | X1 template sentence | factory.py: `darkside.plain(TEMPLATE_HARD_LINKED)` -> `darkside.plain(OUTPUT_HARD_LINKED)` | killed: `inc9p:sec_f2_a_hard_linked_template_is_refused_and_nothing_is_written` |
| Q13 | X1 output sentence | factory.py: `darkside.plain(OUTPUT_HARD_LINKED)` -> `darkside.plain(TEMPLATE_HARD_LINKED)` | killed: `inc9p:sec_f2_a_hard_linked_target_is_refused_and_the_victim_is_untouched` |
| Q14 | X1 import sentence | factory.py: `darkside.plain(IMPORT_HARD_LINKED)` -> `darkside.plain(OUTPUT_HARD_LINKED)` | killed: `inc9p:cr_f2_importing_over_a_hard_linked_template_leaves_the_victim_untouched` |
| Q15 | X2 allow_list/normalised template not U1 | factory.py: `if reason in ("link", "allow_list", "normalised"):` -> `if reason == "link":` | killed: `inc9p:sec_f1_the_factory_preview_never_touches_a_link_behind_a_normalised_part[size0]` |
| Q16 | X2 missing template not 'not found' | factory.py: `return TEMPLATE_OUTSIDE\n        return TEMPLATE_MISSING` -> `return TEMPLATE_OUTSIDE\n        return refusal_sentence(reason)` | killed: `inc9p:w2_pin_the_other_template_refusals_say_u1_or_not_found[docs/missing.docx-archivo` |
| Q17 | CR-F1 normalised not U1 | osopen.py: `if reason in ("allow_list", "normalised"):\n        return PATH_NOT_SUPPORTED` -> `if reason == "allow_list":\n        return PATH_NOT_SUPPORTED` | killed: `cr_f1_refusal_sentence_maps_each_reason[normalised-path` |
| Q18 | CR-F3 import surface ignored | osopen.py: `if reason == "unreadable" and surface == "import":` -> `if False:` | killed: `cr_f3_only_the_import_surface_reads_unreadable_differently` |
| Q19 | CR-F1 app bypasses the shared mapping | app.py: `    return refusal_sentence(reason)\n` -> `    return PATH_NOT_SUPPORTED if reason in ("allow_list", "normalised") else refusal_sentence(reason)\n` | killed: `cr_f1_the_attachment_paths_use_the_shared_mapping` |
| Q20 | CR-F1 import drops its surface | factory.py: `refusal_sentence(reason, surface="import")` -> `refusal_sentence(reason)` | killed: `cr_f1_the_import_uses_the_shared_mapping_with_its_surface` |
| Q21 | CR-F5 preview asks twice | factory.py: `path, reason = self._template(doc)\n            if path is None or not path.exists():\n                return Text.assemble` -> `path, reason = self._template(doc)\n            self._template(doc)\n            if path is None or not path.exists():\n                return Text.assemble` | killed: `cr_f5_the_preview_asks_confine_reason_once[docs/missing.docx]` |
| Q22 | CR-F2 sibling not removed when resolve fails | factory.py: `tmp.unlink(missing_ok=True)` -> `pass` | killed: `cr_f2_pin_a_failing_office_resolve_toasts_the_type_and_leaves_no_temporary_file` |
| Q23 | CR-F7 step 2 before step 1b | osopen.py: `components = local.parts[1:] if local.anchor else local.parts\n    if any(":" in part for part in components) or any(\n            part not in (".", "..") and part != part.rstrip(" .") for part in local.parts):\n        return None, "normalised"\n    joined = _lexically_inside(local, workspace)\n    if joined is None:\n        return None, "outside"\n` -> `joined = _lexically_inside(local, workspace)\n    if joined is None:\n        return None, "outside"\n    components = local.parts[1:] if local.anchor else local.parts\n    if any(":" in part for part in components) or any(\n            part not in (".", "..") and part != part.rstrip(" .") for part in local.parts):\n        return None, "normalised"\n` | killed: `cr_f7_pin_the_normalised_check_runs_before_the_lexical_one` |
| Q24 | CR-F4 lexically_outside back | osopen.py: `def is_link(info: os.stat_result) -> bool:` -> `def lexically_outside(t, w):\n    return False\n\n\ndef is_link(info: os.stat_result) -> bool:` | killed: `cr_f4_lexically_outside_is_removed` |

Not mutated (declared): the stale-docstring fix (CR-F5, no behaviour); the CR-F8 label change; the CR-F6 declaration (no code); the sentence constants of the 8.3 form (`JLINKN~1:$I30` is refused on its text, same mutant as Q1).

## 5. Renders

Pilot, real screens at 118 columns, HOME and USERPROFILE in a temp dir, hard links made with `os.link` between two temp files (harness `%TEMP%\inc9q-harness\render.py`, outside the repo). Frames abbreviated to the template line.

```
X1 output hard link:    generate toast: output file has several hard links: delete or rename it
X1 template hard link:  generate toast: template has several hard links: replace it with a plain copy
X1 import hard link:    toast: templates file has several hard links: delete or rename it
F3 attachment (open):   toast: attachment has several hard links: replace it with a plain copy   (launcher calls: [])
X2 UNC template:        preview "... proceso plantilla  path not supported: use C:\u2026 or a relative path  tags (sin tags) ..."
                        generate toast: path not supported: use C:\u2026 or a relative path
X2 con template:        same preview line and same toast
X2 normalised (d /a):   same preview line and same toast
X2 pin, missing file:   preview "... archivo de plantilla no encontrado ..."; toast archivo de plantilla no encontrado
CR-F3 import unreadable (os.lstat raises for the templates folder):
                        toast: templates folder could not be checked: use a real folder named templates inside the workspace
```

The 87-column width is covered by the `NARROW` params of the CR-F3 and X2 arms, not rendered separately.

## 6. Test results, risks, carries, next

- Ruff 0.8.4, `ruff check mapper tests`, clean `55dc530` worktree under `%TEMP%` (removed) vs this tree: 26 errors on both; the 26 (file, code, message) entries are the same (compared after stripping the root prefix by eye; the script's prefix strip failed, so the programmatic set difference was not clean).
- `-W error::SyntaxWarning`: used on every targeted run and on the lane.
- Risks
  1. A `:` in any component but the drive anchor is refused for every caller (add, open, factory template, import): a name legitimate on POSIX is `normalised` here. Windows only.
  2. A not-found at 260 characters or more is `unreadable` even where long paths are enabled; fail closed, V1 for an attachment ("attachment must be inside the workspace"), which is the wrong cause for this case.
  3. `hard_linked` fails closed, so an unreadable attachment (permission error on `lstat`) reads as "several hard links". Inaccurate wording in that corner; no path leaks.
  4. With the tail option, a path whose first missing component is really a link that `lstat` mis-reports as not found would be returned `ok` lexically (the OS is never asked about it); the guard is the closed text rules (1b) and the MAX_PATH rule, not the resolve.
  5. The parent re-check narrows the window, it does not close it; after a swap the `.tmp-*` sibling stays in the moved folder (the test shows the attack case leaves it there).
  6. Atomic write drops target metadata (CR-F6, declared, not measured).
- Unmeasured: POSIX; whether the volume makes an 8.3 alias for the junction (the 8.3 form is refused on its text); behaviour with LongPathsEnabled; the 87-column render of the new sentences beyond the arm params.
- Next: the Inc-9q reviews (security first: a closed text rule for `:` still leaves other Windows path normalisations, e.g. a trailing `\` or reserved characters `<>|"?*` in a component; none was probed here); the attachment-chip open increment (X3).

## Commits

- `40b33e6` the arms, strict xfail.
- `3eb6263` the implementation (3 source files, tests, `ARCHITECTURE.md`).
- the simplification of `_write_via_sibling`, `A-125` and this record (below).
