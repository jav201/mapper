# Increment 042 -- Inc-9p: normalised components (SEC-F1), hard links, invisible names, `confine_reason`, W1, W2

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `7ebac19`. Authority: `VERDICT-inc9-2026-09-30.md` Round 12 (W1, W2; the operator took the recommended option on both) and the coordinator's rulings for
`INC9O-SEC-F1`..`F4`, `INC9O-CR-F1`..`F6`. Amendment: `A-124` (appended to `01-requirements.md`, dated 2026-10-01).

## 1. What changed

- `mapper/osopen.py` (source 1)
  - `confine_reason(text, workspace) -> (Path | None, reason)`, reasons `ok`, `allow_list`, `outside`, `link`, `normalised`, `unreadable`; `confine` is its `[0]`; `lexically_outside` is `confine_reason(...)[1] == "outside"`.
  - New step 1b in the rule: `any(part not in (".", "..") and part != part.rstrip(" ."))` over `local.parts` -> `normalised`, before any filesystem call (SEC-F1).
  - `PATH_THROUGH_LINK` (W2).
  - `safe_local_path` expands `~` only when the text STARTS with `~` (CR-F5: pathlib drops a leading `./`).
- `mapper/app.py` (source 2): `_path_refusal` asks `confine_reason`: `link` -> W2, `allow_list`/`normalised` -> U1, the rest -> V1.
- `mapper/screens/factory.py` (source 3)
  - `_missing_text`: `link` -> W2, `outside` -> V2, else the old text.
  - Generate: `_plain_file_name` (`check_map_id` + categories Cf/Zl/Zp/Co) for the document name (W1 document sentence) and the node id (W1 node sentence), then `confine_reason("./<name>-<id><suffix>")`.
  - `_hard_linked` on the template and the target.
  - `_write_via_sibling` (mkstemp in the target's directory, `os.replace`, sibling removed on failure) for generate and import.
  - Import confines `./templates/<name>` and maps the reason (`_import_refusal`).
- Not source: `docs/ARCHITECTURE.md` (row 106, 202/221/500 line numbers, row `osopen`), `01-requirements.md` (`A-124`), tests below. **3 source files, within the cap.**

Sentences (literals, exact):

- W1 document: `document name cannot be a file name: rename it in the map's _nodos.yml (documents)`
- W1 node: `node id cannot be a file name: rename the node`
- W2: `path goes through a link: use a real folder inside the workspace`
- Hard link (NOT operator-ruled, declared): `file has several hard links: use a plain file`

## 2. Sealed-arm changes

| File | Arm | Change | Why |
|---|---|---|---|
| `tests/test_inc9m.py` | `_no_fs` | also patches `ntpath._getfinalpathname` | F4 |
| `tests/test_inc9o.py` | `_Walk`, `_Forms` | same | F4 |
| `tests/test_inc9o.py` | `NAME_NOT_USABLE` (constant + 3 arms) | replaced by `W1_DOC`, `W1_NODE`, `W2` literals; hostile document names (12 params) expect `W1_DOC`, hostile node ids (4) `W1_NODE`, the link-at-the-output arm `W2` | W1, W2 |
| `tests/test_inc9o.py` | `..opening_a_file_behind_a_link_toasts_the_workspace_sentence` | expects `W2` (was V1) | W2 |
| `tests/test_inc9o.py` | `..v2_a_template_behind_a_link_is_not_called_outside` | expects `W2` in the frame, not `MISSING` and not V2 (was `MISSING`) | W2 |
| `tests/test_inc9n.py` | `..a_junction_inside_the_workspace_that_leads_outside_is_refused` | expects the W2 sentence in the frame (was `MISSING`) | W2 |
| `tests/test_arch_osopen_callers.py` | allowed names, docs check | `factory` imports `safe_local_path`, `confine_reason`, `PATH_NOT_SUPPORTED`, `PATH_OUTSIDE_WORKSPACE`, `PATH_THROUGH_LINK` (was `confine`, `lexically_outside`) | the names changed |
| `tests/test_palette.py` | `test_palette_empty_query_dispatches_nothing` | waits for and asserts `palette._items` non-empty before the empty query | CR-F6 |

No sealed arm was weakened: every changed expectation is stricter or names a new cause. The template pins for UNC, `//h/s`, `con` and a missing file keep `archivo de plantilla no encontrado` (see A-124 item 3: deviation from the literal reason map, declared).

## 3. Arm table (RED/GREEN)

RED = `c0235dc` (the arms, strict xfail) with `--runxfail`, sources of `7ebac19`, in a separate `git worktree` under `%TEMP%` (removed): `tests/test_inc9p.py tests/test_inc9o.py tests/test_inc9n.py tests/test_arch_osopen_callers.py`,
**87 failed, 198 passed**. 87 = the 87 xfail marks, one for one (the strict xfails also passed as `87 xfailed` on the committed head). GREEN = the implementation commit, the same four files plus `test_inc9m`, `test_palette`, `test_darkside_census`, `test_attachments`: **433 passed** (`-W error::SyntaxWarning`).

| Step | Arms (RED on base) | Closed by |
|---|---|---|
| `norm` (SEC-F1) | 10 junction/symlink x 5 forms, 5 edge dot/space, 2 factory preview, 2 attachment add, 1 open = 20 | step 1b |
| `reason` | reason table 1, unreadable (lstat) 3, unreadable (resolve) 2, thin wrapper 1, sentence map 2, one home for W2 1 = 10 | `confine_reason`, `_path_refusal` |
| `w2` | add 2, open 2, factory 2 (+ 3 sealed, below) = 6 | W2 mapping |
| `equiv` (CR-F1) | 7 | `lexically_outside` over `confine_reason` |
| `hard` (SEC-F2) | target, template, sibling + replace, no leftover sibling = 4 | `_hard_linked`, `_write_via_sibling` |
| `unicode` (SEC-F3) | 6 characters x document name and node id = 12 | `_plain_file_name` |
| `import` (CR-F2) | junction, hard-linked target, sibling = 3 | import confined and atomic |
| `tilde` (CR-F5) | `~draft`, `-draft`, `./~x` = 3 | `./` + `startswith("~")` |
| sealed `w1`/`w2` in `test_inc9o` | 12 + 4 hostile names/ids, link output, V1 link open, V2 link template = 19 | W1/W2 |
| sealed in `test_inc9n`, `test_arch` | 1 + 2 | W2, names |

Pins (green on base, killed by a mutant instead): plain names `d/x`, `d.x/y`, `./x`, `..\ws\x`; an accented document name; a bare `~/` still expands; a plain import; the template pins; `_path_refusal` for `docs/a.pdf`, UNC, `con`, `..`, drive-absolute; the unreadable -> V1 reading.

**F4 re-measurement.** With the corrected spies (`_no_fs`, `_Walk`, `_Forms`) the existing `test_inc9o` / `test_inc9m` arms are all still green on `7ebac19` (the 202 passes above): the blind spot hid no existing red. The new `norm` arms use the corrected `_no_fs`. The `ntpath` patch alone was not isolated by a mutant (not measured): `realpath` and `Path.resolve` are also patched by name in the same spies.

## 4. Mutant table

Harness: `%TEMP%\inc9p-harness\mut.py` (outside the repo). Byte-level read and write in each file's own line endings (the three sources are CRLF), a sha256 pin of each file checked after every restore, the verdict printed before the restore, `-B`, `-x`.
Pins (clean head): `osopen.py e9f98fe72dd680355200e68ccd12b9fb8039fa35eab9e09e14ba21c239d9aee9`, `app.py 0ebf0074074b3c4e44ec5a272f2f41ca1ec89fd34ca9e464350837622f5066bd`, `factory.py 663464c8d00552c82f86f772d996fbff8e43d97511d2332b1e76f12b3ce01211`; unchanged after the run (re-checked).
Suites: `tests/test_inc9p.py` unless noted. **27 mutants, 27 killed, 0 survived.**

| # | Arm claimed | File: exact text -> mutant text | Killed by |
|---|---|---|---|
| M1 | F1 normalised check | osopen: `part not in (".", "..") and part != part.rstrip(" .")` -> `part not in (".", "..") and False` | `..normalised_component_is_refused..[.../lnk/x-junction]` |
| M2 | F1 dots count | osopen: `part != part.rstrip(" .")` -> `part != part.rstrip(" ")` | same |
| M3 | F1 `..` exempt (pin) | osopen: `part not in (".", "..") and part != part.rstrip(" .")` -> `part != part.rstrip(" .")` | `..pin_plain_names..[..\\ws\\x]` |
| M4 | reason `link` | osopen: `return None, "link"` -> `return None, "outside"` | `confine_reason_names_the_cause` |
| M5 | reason `unreadable` | osopen: `return None, "unreadable"\n        if _is_link` -> `return None, "outside"\n        if _is_link` | `..unreadable_when_a_component..[error0]` |
| M6 | CR-F1 string prefix | osopen: `return confine_reason(text, workspace)[1] == "outside"` -> `local = safe_local_path(text)\n    return local is not None and not os.path.abspath(Path(workspace) / local).startswith(os.path.abspath(workspace))` | `lexically_outside_is_the_outside_reason[0]` (the `ws2` sibling; the upper-cased case also differs) |
| M7 | F2 sibling + replace | factory: `os.replace(tmp, target)` -> `shutil.copyfile(tmp, target)` | `generate_writes_a_sibling_and_replaces_it` |
| M8 | F2 nlink target | factory: `return path.lstat().st_nlink > 1` -> `... > 99` | `hard_linked_target_is_refused..` |
| M9 | F3 `Co` | factory: `_INVISIBLE = {"Cf", "Zl", "Zp", "Co"}` -> `{"Cf", "Zl", "Zp"}` | `..document_name..[U+E000]` |
| M10 | F3 `Cf` | same -> `{"Zl", "Zp", "Co"}` | `..document_name..[U+202E]` |
| M11 | F3 `Zl`/`Zp` | same -> `{"Cf", "Co"}` | `..document_name..[U+2028]` |
| M12 | W1 node id checked | factory: `if not _plain_file_name(node.id):` -> `if False:` | `..node_id_writes_nothing[U+202E]` |
| M13 | W1 node sentence | factory: `darkside.plain(NODE_ID_NOT_A_FILE_NAME)` -> `darkside.plain(DOC_NAME_NOT_A_FILE_NAME)` | `test_inc9o ..hostile_node_id..[a:b]` |
| M14 | W2 template | factory: `if reason == "link":\n            return PATH_THROUGH_LINK\n        if reason == "outside":` -> `if False:` (first) | `w2_the_factory_preview_and_generate..[size0]` |
| M15 | W2 attachments | app: `if reason == "link":\n        return PATH_THROUGH_LINK` -> `if False:` | `the_attachment_sentence_follows_the_reason[link/a.pdf-..]` |
| M16 | W2 generate | factory: `sentence = PATH_THROUGH_LINK if reason == "link" else DOC_NAME_NOT_A_FILE_NAME` -> `sentence = DOC_NAME_NOT_A_FILE_NAME` | `test_inc9o ..a_link_where_the_output_would_be_written..` |
| M17 | CR-F2 confined | factory: `target, reason = confine_reason(f"./templates/{source.name}", Path(store.workspace))` -> `target, reason = Path(store.workspace) / "templates" / source.name, "ok"` | `cr_f2_importing_through_a_templates_junction..` |
| M18 | CR-F2 atomic | factory: `_write_via_sibling(target, lambda tmp: shutil.copy2(source, tmp))` -> `shutil.copy2(source, target)` | `cr_f2_pin_a_plain_import_copies_into_templates` (the `_Replace` arm too) |
| M19 | W2 import | factory: `if reason == "link":\n        return PATH_THROUGH_LINK\n    if reason in ("allow_list"` -> `if False:` | `cr_f2_importing_through_a_templates_junction..` |
| M20 | CR-F5 `./` | factory: `confine_reason(f"./{self.document_name}-...` -> `confine_reason(f"{self.document_name}-...` | `cr_f5_a_name_starting_with_a_tilde..[~draft]` |
| M21 | CR-F5 literal `./~x` | osopen: `if text.startswith("~") else Path(text)` -> `if True else Path(text)` | same (`~draft` arm, killed first with `-x`) |
| M22 | F2 sibling cleanup | factory: `tmp.unlink(missing_ok=True)` -> `pass` | `a_failed_generate_leaves_no_temporary_file` |
| M23 | F2 template nlink | factory: `if _hard_linked(path) or _hard_linked(target):` -> `if _hard_linked(target):` | `hard_linked_template_is_refused..` |
| M24 | F2 target nlink | same -> `if _hard_linked(path):` | `hard_linked_target_is_refused..` |
| M25 | reason `normalised` | osopen: `return None, "normalised"` -> `return None, "allow_list"` | `confine_reason_names_the_cause` |
| M26 | unreadable/outside -> V1 | app: `return PATH_OUTSIDE_WORKSPACE\n` -> `return PATH_NOT_SUPPORTED\n` | `..sentence_follows_the_reason[..\\a.pdf-V1]` |
| M27 | V2 | factory: `if reason == "outside":\n            return TEMPLATE_OUTSIDE` -> `if False:` | `test_inc9o ..v2_an_absolute_template_outside..[size0]` |

Not mutated (declared): the CR-F6 palette assertion is a test-only change; the `.` exemption in step 1b is unreachable (pathlib never yields `.`), an equivalent mutant. M21 was killed through the `~draft` arm because `-x` stops at the first failure; the dedicated `./~x` arm is `cr_f5_a_dot_slash_prefix_makes_a_tilde_name_literal` (RED on base).

## 5. Renders

Pilot, real keys at 118 columns, HOME and USERPROFILE in a temp dir, links are local junctions (harness `inc9p-harness\render.py`, outside the repo).

```
W2 attachment add toast:  path goes through a link: use a real folder inside the workspace
W2 attachment open toast: path goes through a link: use a real folder inside the workspace
W2 template preview:      ... proceso plantilla  path goes through a link: use a real folder inside the workspace  tags (sin tags) ...
W2 template generate:     path goes through a link: use a real folder inside the workspace
W1 document toast:        document name cannot be a file name: rename it in the map's _nodos.yml (documents)
W1 node id toast:         node id cannot be a file name: rename the node
import (templates is a junction) toast: path goes through a link: use a real folder inside the workspace
outside dir after all:    ['a.docx', 'x.pdf']   (the two files that were there before; nothing written through the links)
```

The W1 renders used `a\u202eb` as the document name and `a\u200bb` as the node id: the toast names neither. The narrow (87-column) width is covered by the `[size1]` params of the `w2` arms; not rendered separately here (the sentences are the same fixed strings).

## 6. Test results, risks, carries, next

- Ruff on a clean `7ebac19` worktree vs this tree, `ruff check mapper tests`: 26 errors on both, the set (file + code + message, line numbers ignored) identical. Ruff 0.8.4.
- Risks
  1. The hard-link sentence is new, not operator-ruled; it is a constant in `factory.py`.
  2. Factory deviation from the literal reason map (A-124 item 3): the template keeps the old text for `allow_list`, `normalised`, `unreadable`. One line to flip.
  3. `safe_local_path` now expands `~` only for a text that starts with `~`: `./~x` and `.\~x` changed meaning for every caller (add, open, factory).
  4. `lexically_outside` now walks the disk for in-workspace text (it asks `confine_reason`); it is no longer a no-stat function. Its only caller (the factory) was moved to `confine_reason`; `lexically_outside` is now unused by `mapper`, kept for the CR-F1 equivalence.
  5. Hard links on an opened attachment are not detected. The race between the walk and the write is not closed.
- Unmeasured: POSIX; permission/metadata carry-over from an overwritten target; the `ntpath` spy patch in isolation; the 87-column render of W1/W2 beyond the params.
- Next: the Inc-9p reviews (security first: the SEC-F1 form list is a closed text rule; ask whether `\\?\`-less forms such as `a:` ADS names or `d\x` with 8.3 short names behind a link remain).

## Commits

- `c0235dc` the arms, strict xfail.
- the implementation commit (below).

## Full-lane result

`2508 passed, 3 xfailed, 24 deselected, 2 failed` in 1626 s (27 min), `python -m pytest -rf -q -W error::SyntaxWarning`, uninterrupted, on `c33f680`. The 2 failures were `tests/test_no_operator_paths.py` (A-110): this record itself carried the real profile path of the mutant harness on one line (a doc defect of mine, found by the lane). The line was rewritten to `%TEMP%\...`; `test_no_operator_paths.py` was re-run alone afterwards and the lane was NOT re-run in full (only this `.md` changed). Baseline 2427/0; the delta is the new `test_inc9p.py` arms. No known flake failed in this run. The 3 xfailed are pre-existing.
