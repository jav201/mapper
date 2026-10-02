# Increment 044 -- Inc-9r: the final-resolve backstop (CR-F1), the colon's own sentence (Y1), generate's refusal mapping (CR-F2), the MAX_PATH re-check in UTF-16 units (CR-F3, SEC-F1), the preview's hard-link sentence (SEC-F2)

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `bf68d07`. Authority: `VERDICT-inc9-2026-09-30.md` Round 14 (operator Y1, coordinator ruling for CR-F1) and the review findings `INC9Q-CR-F1`..`F6`, `INC9Q-SEC-F1`, `F2`. Amendment: `A-126` (appended to `01-requirements.md`, dated 2026-10-02).

## 1. What changed

- `mapper/osopen.py` (source 1)
  - **CR-F1.** Step 4 asks the OS what the consumer will reach and compares: `resolved = walked.resolve().joinpath(*tail)` against `full = (workspace / local).resolve()`; they differ -> `link`; `resolved` not under the resolved workspace -> `outside`; an `OSError`/`ValueError` from any of the three `resolve()` calls -> `unreadable`. The `if tail / else` split is folded (CR-F6).
  - **Y1.** Step 1b splits: a `:` in a component other than the drive anchor -> reason `colon`; a trailing dot or space stays `normalised`. `PATH_COLON = 'path not supported: ":" is not allowed in a file name'`; `refusal_sentence("colon")` returns it for every surface.
  - **CR-F2 (mapping half).** `PATH_OUTPUT_UNCHECKED = "output path could not be checked: move the workspace to a shorter folder"`; `refusal_sentence("unreadable", surface="generate")` returns it.
  - **CR-F3 / SEC-F1.** The MAX_PATH threshold is measured by `_utf16_units(text) = len(text.encode("utf-16-le")) // 2`. At 260 units or more a not-found is asked again with the `\\?\` prefix (`_LONG_PREFIX`): a link found -> `link`; the component found (not a link) -> the walk continues; FileNotFoundError -> a normal missing tail (step 4 backstops it); any other error -> `unreadable`.
- `mapper/screens/factory.py` (source 2): generate's target refusal is `refusal_sentence(reason, surface="generate")` (the inline `link` -> W2 else W1 is gone, so `PATH_THROUGH_LINK` is no longer imported); `_missing_text` maps `colon` and a new internal reason `hard_linked`; the office preview turns a hard-linked template into the `hard_linked` reason, so it shows `TEMPLATE_HARD_LINKED` through the same single severity site (a second `ALERT` site would have changed the hue census, `test_darkside_census`).
- `mapper/app.py` (source 3): a docstring only (`_path_refusal` already routed every reason through `refusal_sentence`, so the colon sentence reaches the attachment add and open surfaces with no code change). **3 source files, within the cap (expected 3, ceiling 4).**
- Not source: `docs/ARCHITECTURE.md` (rows `screens` and `osopen`, back-edge line 498 -> 504), `01-requirements.md` (`A-126`), tests.

### `confine_reason`, as implemented

```python
def confine_reason(text: str, workspace: Path) -> tuple[Path | None, str]:
    local = safe_local_path(text)
    if local is None:
        return None, "allow_list"
    components = local.parts[1:] if local.anchor else local.parts
    if any(":" in part for part in components):
        return None, "colon"
    if any(part not in (".", "..") and part != part.rstrip(" .") for part in local.parts):
        return None, "normalised"
    joined = _lexically_inside(local, workspace)
    if joined is None:
        return None, "outside"
    root = Path(os.path.abspath(workspace))
    parts = Path(joined).parts[len(root.parts):]
    walked = root
    tail: tuple[str, ...] = ()
    for index, part in enumerate(parts):
        current = walked / part
        try:
            info = os.lstat(current)
        except (FileNotFoundError, NotADirectoryError):
            if _utf16_units(os.fspath(current)) < _MAX_PATH:
                tail = parts[index:]
                break
            try:
                info = os.lstat(_LONG_PREFIX + os.fspath(current))
            except FileNotFoundError:
                tail = parts[index:]
                break
            except (OSError, ValueError):
                return None, "unreadable"
        except (OSError, ValueError):
            return None, "unreadable"
        if is_link(info):
            return None, "link"
        walked = current
    try:
        ws_real = Path(workspace).resolve()
        resolved = walked.resolve().joinpath(*tail)
        full = (Path(workspace) / local).resolve()
    except (OSError, ValueError):
        return None, "unreadable"
    if os.path.normcase(full) != os.path.normcase(resolved):
        return None, "link"
    if not resolved.is_relative_to(ws_real):
        return None, "outside"
    return resolved, "ok"
```

(Docstring omitted here; it is rewritten for the new steps. `_MAX_PATH = 260`, `_LONG_PREFIX = "\\\\?\\"`.)

### Sentences (exact)

- Y1: `path not supported: ":" is not allowed in a file name` (every surface: attachment add and open, import, template preview, generate).
- CR-F2: `output path could not be checked: move the workspace to a shorter folder`.
- SEC-F2: the preview shows `template has several hard links: replace it with a plain copy` (the X1 template sentence), as generate does.

### Declared readings and deviations

1. **CR-F4: the form is `sub/l:$I30`, not a top-level `l:$I30`.** At the top level pathlib reads `l:$I30` as a drive-relative path (drive `l:`), and `safe_local_path` refuses it as `allow_list` BEFORE step 1b, which cannot be changed without moving the colon check ahead of the allow-list (and so changing `C:x`, which is U1 today). The new `STREAM_FORMS` entry is therefore `("sub/l:$I30", "sub/l")`, a single-letter junction one level down, where it is a component and step 1b refuses it; the top-level form is pinned as `allow_list` (never `ok`).
2. **The `resolve()` order.** The ruling lists `ws_real` first; it is computed first inside the `try`, as written.
3. **`outside` for generate** falls to V1; it cannot be reached for a name `check_map_id` accepted.
4. **A UNC workspace (unmeasured):** the `\\?\` prefix would be wrong for it; the re-check would read not-found and the step-4 comparison decides.
5. **Import, Y1:** the import surface is covered by the mapping table (`refusal_sentence("colon", surface="import")`) and by the existing shared-mapping arm; an import SOURCE with a colon cannot be made to exist (a colon in a Windows file name is a stream), so there is no Pilot arm for it. Declared, not measured end to end.

## 2. Sealed-arm changes

| File | Arm | Change | Why |
|---|---|---|---|
| `tests/test_arch_osopen_callers.py` | allowed names for `screens/factory.py`; the docs row check | `PATH_THROUGH_LINK` removed from both (and the module docstring) | generate no longer uses it (CR-F2); an unused import would be a ruff error |
| `docs/ARCHITECTURE.md` | `screens` row, back-edge line | `factory.py:498` -> `factory.py:504` | `test_the_four_known_back_edges...` pins the line number; six lines were added above `_PromptScreen` |
| `tests/test_inc9q.py` | `..sec_f1_a_stream_suffix_on_a_link_component_is_refused_before_any_filesystem_call` (28 params) | expects `(None, "colon")` (was `normalised`); `STREAM_FORMS` gains `sub/l:$I30` | Y1; CR-F4. New in Inc-9q, edited in place |
| `tests/test_inc9q.py` | `..sec_f4_the_unwalked_tail_is_appended_not_resolved` | body replaced: it asserted a proxy (the OS is never asked about `lnk`) and accepted `ok`; it now asserts the property (refusal, nothing launched) for outside and inside, an existing and a missing tail. `_Reach` and the `_nt` import removed | CR-F1. New in Inc-9q, not sealed; named in the task |
| `tests/test_inc9r.py` | param `a:b/x.pdf` -> `ab:c/x.pdf` | the single-letter form is a drive to pathlib (`allow_list`), a mistake in my arm found on the first GREEN run | declared; the RED run used the original param (it failed either way) |

No other sealed arm changed. No arm was weakened: the changed expectations are stricter or name a new cause.

## 3. Arm table (RED/GREEN)

RED = `b2fa9aa` (the arms as strict xfail; sources of `bf68d07`) with `--runxfail` in a separate `git worktree` under `%TEMP%` (removed): `tests/test_inc9r.py tests/test_inc9q.py`, **57 failed, 54 passed**; 57 = the 57 xfail marks, one for one (they also passed as `57 xfailed` on the committed arms head, 0 XPASS; on a first pass seven marks XPASSed on the base (three generate-table params that were already green, three failed-re-check params, and one old Inc-9q open-external mark that my new step name had re-activated), and were un-keyed or renamed before the commit). GREEN = the implementation: the same two files, 111 passed (after the OPEN_STEPS were emptied), then the lane.

| Step | Arms (RED on base) | Count | Closed by |
|---|---|---|---|
| `colon` (Y1, CR-F4) | `test_inc9q` stream forms 7 forms x 2 tails x 2 places (now `colon`; includes `sub/l:$I30`) = 28; `test_inc9r` sentence on 4 surfaces 4, reason for 4 component texts 4, attachment prompt at 118 and 87 = 2, template preview + generate at 118 and 87 = 2, generate table `colon` 1 | 41 | step 1b `colon`, `PATH_COLON`, `refusal_sentence`, `_missing_text` |
| `backstop` (CR-F1) | the fixed Inc-9q tail arm (outside/inside x existing/missing tail) = 4; an import through a junction that `lstat` hides = 1 | 5 | step 4 comparison |
| `generate` (CR-F2) | table `unreadable` 1; shared mapping with its surface 1; 297-character unreadable target at 118 and 87 = 2 | 4 | `refusal_sentence(..., surface="generate")` |
| `maxpath` (CR-F3) | exactly 260 units re-asked 1; junction beyond MAX_PATH is `link` (outside, inside) 2 | 3 | the `\\?\` re-check |
| `utf16` (SEC-F1) | astral path (outside, inside) | 2 | `_utf16_units` |
| `preview` (SEC-F2) | hard-linked template preview at 118 and 87 | 2 | `hard_linked` in `_preview` |

Total 41 + 5 + 4 + 3 + 2 + 2 = **57**.

Pins (green on the base, killed by a mutant instead): ordinary, existing and missing-tail paths; a workspace that is itself a link; the `normalised` cases keep U1; the top-level `l:$I30` is `allow_list`; `unreadable` is V1 off the generate surface; 259 units is a plain missing tail (no re-check); the plain-template preview; a re-check that fails for another reason is `unreadable` (3 error types).

The astral arm builds two folders of `n` astral characters under the workspace (chosen from the temp path length) so that the path to the second folder is under 260 code points and at least 260 UTF-16 units, with a junction `j` below; the numbers of the run are asserted in the arm (the brief's 168/262 example is for a different workspace length).

## 4. Mutant table

Harness: `%TEMP%\inc9r-harness\mut.py` (outside the repo). Byte-level read and write in each file's own line endings (the three sources are CRLF), a sha256 pin checked before each mutation and after each restore, the verdict printed before the restore, `-B`, `-x`, `-W error::SyntaxWarning`. Pins (clean implementation head): `osopen.py d0d5212ce1633410ee92b1d3acc2c5e0b62606e502026ce3956b981da0d932c5`, `app.py df9839393c334ab516c774644813a63d1d23923b8389854925ba231d72628df2`, `factory.py 6abd3862bd017274dca7cd13413cd537df949b0ef7ba5bdf8126632007210feb`. Pins re-checked after the run: OK. **16 mutants run, 16 killed, 0 survived.** The suites are named per mutant (the intended killing arm).

| # | Arm claimed | File: exact text -> mutant text | Verdict: killing test |
|---|---|---|---|
| R1 | CR-F1 step-4 comparison removed | osopen.py: `if os.path.normcase(full) != os.path.normcase(resolved):` -> `if False:` | killed: `inc9q: sec_f4_the_unwalked_tail_is_appended_not_resolved[outside-x.pdf]` |
| R2 | CR-F3 the `\\?\` re-lstat removed | osopen.py: `info = os.lstat(_LONG_PREFIX + os.fspath(current))` -> `raise FileNotFoundError(2, 'x')` | killed: `inc9r: cr_f3_a_junction_beyond_max_path_is_the_link_reason[outside]` |
| R3 | SEC-F1 code points instead of UTF-16 units | osopen.py: `return len(text.encode("utf-16-le")) // 2` -> `return len(text)` | killed: `inc9r: sec_f1_an_astral_path_under_260_code_points_over_260_units_with_a_junction_is_the_link_reason[outside]` |
| R4 | Y1 the colon reason folded back into U1 | osopen.py: `return None, "colon"` -> `return None, "normalised"` | killed: `inc9r: y1_a_colon_in_a_component_is_the_colon_reason[notes: draft.pdf]` |
| R5 | CR-F3 boundary `>=` -> `>` (exactly 260 is not re-asked) | osopen.py: `if _utf16_units(os.fspath(current)) < _MAX_PATH:` -> `if _utf16_units(os.fspath(current)) <= _MAX_PATH:` | killed: `inc9r: cr_f3_a_not_found_at_exactly_260_units_is_re_asked_with_the_prefix_and_continues` |
| R6 | CR-F3 boundary one lower (259 is re-asked) | osopen.py: `if _utf16_units(os.fspath(current)) < _MAX_PATH:` -> `if _utf16_units(os.fspath(current)) < _MAX_PATH - 1:` | killed: `inc9r: cr_f3_pin_a_not_found_at_259_units_is_a_plain_missing_tail` |
| R7 | CR-F3 a failed re-check continues instead of `unreadable` | osopen.py: `            except (OSError, ValueError):\n                return None, "unreadable"\n        except (OSError, ValueError):` -> `            except (OSError, ValueError):\n                tail = parts[index:]\n                break\n        except (OSError, ValueError):` | killed: `inc9r: cr_f3_a_re_check_that_fails_for_another_reason_is_unreadable[error0]` |
| R8 | CR-F1 the `outside` check removed | osopen.py: `if not resolved.is_relative_to(ws_real):` -> `if False:` | killed: `inc9q: sec_f4_the_resolved_walked_prefix_is_the_last_check_for_a_missing_file` |
| R9 | Y1 `refusal_sentence` colon -> U1 | osopen.py: `        return PATH_COLON` -> `        return PATH_NOT_SUPPORTED` | killed: `inc9r: y1_the_colon_reason_has_one_sentence_on_every_surface[None]` |
| R10 | CR-F2 generate/unreadable branch off | osopen.py: `if reason == "unreadable" and surface == "generate":` -> `if False:` | killed: `inc9r: cr_f2_refusal_sentence_maps_each_generate_reason[unreadable-...]` |
| R11 | CR-F2 generate bypasses the shared mapping | factory.py: `refusal_sentence(reason, surface="generate")` -> `DOC_NAME_NOT_A_FILE_NAME if reason != "link" else refusal_sentence(reason)` | killed: `inc9r: cr_f2_generate_uses_the_shared_mapping_with_its_surface` |
| R12 | SEC-F2 the preview hard-link check removed | factory.py: `if path is not None and hard_linked(path):` -> `if False:` | killed: `inc9r: sec_f2_the_preview_of_a_hard_linked_template_shows_the_template_sentence[size0]` |
| R13 | Y1 the factory template mapping drops `colon` | factory.py: `if reason in ("link", "colon", "allow_list", "normalised"):` -> `if reason in ("link", "allow_list", "normalised"):` | killed: `inc9r: y1_a_template_with_a_colon_shows_the_colon_sentence_in_preview_and_generate[size0]` |
| R14 | CR-F4 step 1b colon check on the first component only | osopen.py: `if any(":" in part for part in components):` -> `if any(":" in part for part in components[:1]):` | killed (only the one-level-down form can kill it): `inc9q: sec_f1_a_stream_suffix_on_a_link_component_is_refused_before_any_filesystem_call[outside-sub/l:$I30-sub/l-/x.pdf]` |
| R15 | SEC-F2 the `hard_linked` reason gives the missing text | factory.py: `        if reason == "hard_linked":\n            return TEMPLATE_HARD_LINKED` -> `        if reason == "hard_linked":\n            return TEMPLATE_MISSING` | killed: `inc9r: sec_f2_the_preview_of_a_hard_linked_template_shows_the_template_sentence[size0]` |
| R16 | Y1 the attachment path bypasses the shared mapping for `colon` | app.py: `    return refusal_sentence(reason)\n` -> `    return PATH_NOT_SUPPORTED if reason == "colon" else refusal_sentence(reason)\n` | killed: `inc9r: y1_the_attachment_prompt_toasts_the_colon_sentence[size0]` |

Not mutated (declared): the docstring rewrites; the `ARCHITECTURE.md` text (covered by the sealed arch test); the `app.py` docstring.

## 5. Renders

Pilot, real screens, HOME and USERPROFILE in a temp dir, local files only (harness `%TEMP%\inc9r-harness\render.py`, outside the repo). The attachment prompt is the real `A` key then the typed characters.

```
=== 118 columns
Y1 attachment prompt, typed 'notes: draft.pdf' -> toast: path not supported: ":" is not allowed in a file name
Y1 template 'notes: draft.docx' preview row:          path not supported: ":" is not allowed in a file name
Y1 template generate toast:                            path not supported: ":" is not allowed in a file name
CR-F2 297-char target, long-path re-check fails:       output path could not be checked: move the workspace to a shorter folder
SEC-F2 hard-linked template preview row:               template has several hard links: replace it with a plain copy
=== 87 columns
Y1 attachment prompt, typed 'notes: draft.pdf' -> toast: path not supported: ":" is not allowed in a file name
Y1 template 'notes: draft.docx' preview row:          path not supported: ":" is not allowed in a file name
Y1 template generate toast:                            path not supported: ":" is not allowed in a file name
CR-F2 297-char target, long-path re-check fails:       output path could not be checked: move the workspace to a shorter folder
SEC-F2 hard-linked template preview rows:              template has several hard links: replace it with a   /   plain copy   (wraps in two rows at 87)
```

The CR-F2 toast is the render of a simulated failure (`os.lstat` raising `PermissionError` for the `\\?\` re-check): a real unreadable long path was not produced.

## 6. Test results, risks, carries, next

- Ruff 0.8.4, `ruff check mapper tests --output-format json`, clean `bf68d07` worktree under `%TEMP%` (removed) vs this tree, a programmatic set difference on (file relative to its root, code, message): **26 entries on each side, both differences empty.**
- `-W error::SyntaxWarning`: used on every targeted run and on the lane.
- Targeted: `tests/test_inc9r.py tests/test_inc9q.py tests/test_arch_osopen_callers.py tests/test_darkside_census.py` 140 passed; `test_inc9m/n/o/p`, `test_attachments`, `test_darkside_census`, `test_arch_osopen_callers` 425 passed before the two sealed pins above were fixed (3 failed then: two arch pins and the hue census; the census failed because a first draft added a second `ALERT` site to the preview, which was folded into the existing one).
- Risks
  1. **A new `link` verdict where the OS and the walk disagree for a benign reason** (for example a workspace on a path whose resolved case or 8.3 form differs only in a component the tail holds): `normcase` is applied to both sides, 8.3 aliases of missing components cannot exist; the ordinary, missing-tail and linked-workspace pins pass. Not measured on a volume with 8.3 names disabled or on a `subst` drive.
  2. **The step-4 comparison asks the OS about the tail** (`full`): for a path of 260 units or more in a process without long-path support, `Path.resolve()` did not raise in the measurement (a 259, 260 and 297 character missing path), so the comparison holds; a Python or Windows version where it raises would make such paths `unreadable` (fail closed).
  3. A re-check by a path that is not drive-absolute (UNC workspace) would read not-found; the step-4 comparison decides (unmeasured).
  4. A `:` is still refused for every caller; the sentence now names the cause.
  5. The race between the walk and the write is narrowed, not closed (`A-125` item 4).
- Unmeasured: POSIX; a volume or process with long paths enabled; a UNC workspace; the import surface end to end for Y1 (no source can carry a colon); a real (not simulated) unreadable long path.
- Next: the Inc-9r reviews (security: whether the `\\?\` re-check is complete for components that are links but whose parents are long; code: the step-4 order of `resolve()` calls).

## Commits

- `b2fa9aa` the arms, strict xfail.
- the implementation (3 source files, tests, `ARCHITECTURE.md`), then `A-126` and this record.

## Full-lane result

`2621 passed, 24 deselected, 3 xfailed` (0 failed) in 1334 s (22 min), `python -m pytest -rf -q -W error::SyntaxWarning`, uninterrupted, on `857cf0b`, run AFTER the record was final except this section, with a temp HOME and a git identity from the environment. Baseline 2570/0; the delta is the new `test_inc9r.py` arms and the added `sub/l:$I30` params. The 3 xfailed are pre-existing. **A first lane run on the same head failed 5 `test_github` tests** (`git commit` exit 128, "Author identity unknown"): my own environment error (a temp HOME with no git identity), not code; the lane was re-run in full with the identity variables and is the result above. After this section was appended only this `.md` changed; the lane was NOT re-run.

## Corrections, 2026-10-02 (appended by Inc-9s, `A-127`; nothing above is rewritten)

Three statements in this record were wrong or overstated. They are corrected here, not edited in place (`B-81`).

1. **Declared reading 5 is wrong (`INC9R-CR-F3`).** It says an import SOURCE with a colon cannot be made to exist, so there is no Pilot arm. An NTFS alternate data stream can be one: creating `<dir>\ab:b.docx` with `open(..., "wb")` makes the file `ab` carrying the stream `b.docx`, and typing that path at the import prompt passes `safe_local_path`, `is_file()` and the `.docx` suffix check, then reaches the target `./templates/ab:b.docx`, which is the `colon` reason. Y1 on import is therefore testable end to end; `tests/test_inc9s.py` does it (a Pilot arm with real keys, asserting the Y1 toast and an empty `templates`).
2. **The mutant table names intended killers (`INC9R-CR-F4`).** The "Verdict: killing test" column of section 4 is the arm each mutant was written to be killed by, not the first `-x` failure the harness printed; the first failure can be an earlier arm of the suite run. The count (16 run, 16 killed, 0 survived) stands; the attribution column is intent.
3. **`normcase` in the step-4 comparison is not load-bearing (`INC9R-CR-F1`).** Section 4 and the code present `os.path.normcase(full) != os.path.normcase(resolved)` as guarding a case difference. The code reviewer measured that it carries no tested load (no arm depends on it). It is belt-and-braces, not a control. No mutant of it was claimed or run, and none is claimed now.

Not corrected here: `hard_linked` as a pseudo-reason in `_missing_text` (`INC9R-CR-F2`) stays in `B-81`.
