# Increment 045 -- Inc-9s: a lone surrogate is refused by the allow-list (INC9R-SEC-F3) and the Inc-9r record corrections (B-81)

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `4a79baa`. Authority: `A-127` (appended to `01-requirements.md`, dated 2026-10-02). Micro-fix; 1 source file.

## 1. What changed

- `mapper/osopen.py` (source 1, the whole cap)
  - `safe_local_path` returns None for any text containing a character of category `Cs` (a lone surrogate), placed after the type / empty / NUL / leading `-` checks and BEFORE any `Path` is built, so it precedes every filesystem call. It becomes `allow_list` / `U1` in `confine_reason` and `REFUSED_TYPE` in `open_external` (whose own `safe_local_path` pre-check now refuses it). Import `unicodedata` added; the docstring names the new refusal.
  - `_utf16_units` encodes with `"utf-16-le", "surrogatepass"` (second guard; a lone surrogate counts as 1 unit and cannot raise).
  - Cause of the defect: `_utf16_units` ran inside the `FileNotFoundError` handler of the walk, so the outer `except (OSError, ValueError)` never saw its `UnicodeEncodeError`.
- Records (docs, not source): `increment-044-inc9r.md` gets an appended `## Corrections, 2026-10-02` section (the three `B-81` corrections: reading 5 wrong, mutant table = intended killers, `normcase` not load-bearing; nothing above it rewritten); `01-requirements.md` gets `A-127`; this record.
- Tests: `tests/test_inc9s.py` (new, ASCII, 13 test items). Item 3 (the optional `INC9R-CR-F3` Pilot arm) is IN: it was not fiddly.

## 2. Files modified

Source: `mapper/osopen.py`. Tests: `tests/test_inc9s.py` (new). Docs: `increment-044-inc9r.md` (append), `01-requirements.md` (append `A-127`), `increment-045-inc9s.md` (new). **1 source file, within the cap.** Sealed arms changed: none. `BACKLOG.md` and `state.json` not touched (B-81 stays open for `INC9R-CR-F2`; the coordinator closes the rest).

## 3. Arm table (RED/GREEN)

RED = `f372ea2` (the arms as strict xfail; source identical to `4a79baa`) with `--runxfail`, in a separate `git worktree` under `%TEMP%` (removed): `tests/test_inc9s.py` **11 failed, 2 passed**. The committed arms head itself reports `2 passed, 11 xfailed` (0 XPASS). GREEN = `2459fd6`: 13 passed; the neighbouring suites in section 5 pass (498).

| Arm | RED on `4a79baa` (measured) | GREEN |
|---|---|---|
| `safe_local_path` / `confine_reason` / `confine` refuse a lone surrogate, zero filesystem calls (5 texts: `\ud800/x.pdf`, `docs/\udc80.pdf`, `docs/a\udbffb.pdf`, `\udfff`, and `docs/` + two adjacent lone-surrogate escapes + `.pdf`) | 5 failed: `safe_local_path` returned a path, not None. Direct probe: `confine_reason` RAISES `UnicodeEncodeError` for the first 4; for the adjacent-pair text it returns `ok` (CPython's utf-16 encoder accepts a high surrogate followed by a low one, so nothing raised) | pass |
| `open_external` refuses with `REFUSED_TYPE`, no raise, launcher not called (same 5 texts) | 5 failed: 4 `UnicodeEncodeError` ('utf-16-le' codec can't encode, surrogates not allowed); the adjacent-pair text returned `no se pudo abrir` | pass |
| `_utf16_units("\ud800") == 1`, `("a\udc80b") == 3` | 1 failed: `UnicodeEncodeError` | pass |
| Pin: `\U0001F600` is 2 units (`a` + it: 3), `confine_reason` returns `ok` for `docs/\U0001F600.pdf`, `open_external` returns `abierto` and launches the resolved path | passes on the base (a pin) | pass |
| `INC9R-CR-F3` Pilot: import of a stream source (`<tmp>\src` + a separator + `ab:b.docx`, created with `open(..., "wb")`), real keys at the `i` prompt, the toast is exactly Y1, `templates` holds nothing | passes on the base (a pin: the colon reason exists since Inc-9r) | pass |

Surrogates are written as escapes and the test file is ASCII (checked: 0 characters above 127 and 0 control characters in `tests/test_inc9s.py`).

## 4. Mutant table

Harness `%TEMP%\inc9s-harness\mut.py` (outside the repo): byte-level read and write of `osopen.py` (CRLF; every mutated text is single-line, so line endings are untouched), a sha256 pin checked before each mutation and after each restore, verdict printed before the restore, `-B`, `-x`, `-W error::SyntaxWarning`, suite `tests/test_inc9s.py`. Pin (the `2459fd6` file): `osopen.py 357cc17ed34060da4ed53c51e2d7f58ef2c9dd1c809e0eaffceae342991e1b5d`. Pin re-checked after the run: OK. **6 mutants run, 6 killed, 0 survived.** The last column is what the harness printed (`-x`): the first failing item in file order, which is not always the arm the mutant was written for (see the `044` correction).

| # | Arm claimed | Exact text -> mutant text (osopen.py) | Killed by (first failure printed) |
|---|---|---|---|
| S1 | the refusal itself | `    if any(unicodedata.category(ch) == "Cs" for ch in text):` -> `    if False:` | `..a_lone_surrogate_is_refused_by_the_allow_list_with_no_filesystem_call[\ud800/x.pdf]`; the `open_external` items alone against S1 (`-k open_external`, measured separately): 5 failed |
| S2 | both halves of the range, not only high surrogates | `unicodedata.category(ch) == "Cs"` -> `unicodedata.category(ch) == "Cs" and ord(ch) < 0xDC00` | `..refused_by_the_allow_list..[docs/\udc80.pdf]` |
| S3 | the `_utf16_units` second guard | `"utf-16-le", "surrogatepass"` -> `"utf-16-le"` | `..the_unit_count_is_a_second_guard_and_does_not_raise_on_a_lone_surrogate` |
| S4 | the astral pin | `unicodedata.category(ch) == "Cs"` -> `ord(ch) > 0xFFFF or unicodedata.category(ch) == "Cs"` | `..pin_an_astral_character_counts_as_two_units_and_is_accepted` |
| S5 | the whole text is scanned | `for ch in text)` -> `for ch in text[:1])` | `..refused_by_the_allow_list..[docs/\udc80.pdf]` |
| S6 | the Pilot arm (Y1 on a stream-source import) | `return None, "colon"` -> `return None, "normalised"` | `..cr_f3_importing_a_stream_source_toasts_y1_and_writes_nothing_under_templates` |

Not mutated (declared): the "nothing is written under `templates`" half of the Pilot arm (no mutation of `osopen.py` alone changes what `factory.py` writes; that half is an assertion, not a measured guard); the docstring. The S1 `-k open_external` run was done inline, not by the harness file; it restored the file and re-checked the pin.

## 5. Test results

- `tests/test_inc9s.py tests/test_inc9r.py tests/test_inc9q.py tests/test_inc9p.py tests/test_inc9o.py tests/test_inc9n.py tests/test_inc9m.py tests/test_arch_osopen_callers.py`: **498 passed** in 235 s (`-W error::SyntaxWarning`, temp HOME).
- Ruff 0.8.4, `ruff check mapper tests --output-format json`, clean `4a79baa` worktree under `%TEMP%` (removed) vs this tree, a programmatic set difference on (file relative to its root, code, message): **26 entries on each side, both differences empty.**
- Environment: temp HOME and USERPROFILE, git identity from environment variables, no network, loopback, UNC, device or real cache; the stream file was created under pytest's `tmp_path`; the pytest rootdir was the repo or the scratch worktree only; scratch worktrees removed.

## 6. Risks, unmeasured, next

- Risks: (1) the `Cs` refusal applies to every typed path (add, open, import, generate, template). A real file whose name is a lone surrogate (possible on NTFS) can no longer be attached; a UTF-8 sidecar cannot carry one, so the loss is theoretical. (2) The adjacent-pair text was `ok` on the base and is now refused; it has no legitimate form in a `yaml.safe_load` sidecar.
- Unmeasured: POSIX; whether Windows accepts a lone surrogate in a name (the base walk said not-found for the ones tried); a Pilot toast for a lone surrogate (the attachment prompt cannot type one; the sentence is `U1` through `refusal_sentence("allow_list")`, covered by existing arms).
- Suggested next task: the coordinator closes `B-81` except `INC9R-CR-F2` and decides on `B-79` / `B-80`.

## Commits

- `f372ea2` the arms, strict xfail.
- `2459fd6` the fix (1 source file; `OPEN_STEPS` emptied).
- the records (`044` corrections, `A-127`, this file).

## Full-lane result

`2634 passed, 24 deselected, 3 xfailed` (0 failed) in 1356 s (22 min), `python -m pytest -rf -q -W error::SyntaxWarning`, uninterrupted, on `f252606`, with a temp HOME and a git identity from the environment, run as the last step. Baseline 2621/0; the delta is the 13 new `test_inc9s.py` items. The 3 xfailed are pre-existing. After this section was appended only this `.md` changed; the lane was NOT re-run.
