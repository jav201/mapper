# Increment 028 — Inc-SEED · a typed map id stays inside the workspace, and creating never overwrites

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `028` — Inc-SEED, a micro-increment |
| Agent | `software-dev` |
| Date | 2026-09-30 |
| Authority | Finding `INC9BC-UX` section E, `SEED-1` and `SEED-2` (independent UX review of Inc-9b/9c, reproduced through the real key path) |
| Starting state | branch `feat/ui-next-batch-02` @ `fddd07d`, clean |
| Commits | `7521ac9` (requirement `A-113` + RED arms, strict xfail) -> `597b7fa` (fix, xfail set emptied) -> docs commit (this file, `BACKLOG.md`) |
| Source files | 2 (`mapper/store.py`, `mapper/app.py`); cap 4 |

---

## 1 · What changed

**Requirement.** `A-113` (`01-requirements.md`, amendment set 20), standalone (no store HLR fits: `HLR-STO.1`
governs file text, not operator-typed ids). A map id names a file inside the workspace; creating never
overwrites. Policy: **refuse with a toast**, not confirm-and-overwrite (simpler, no new modal state across three
entry points, and it is the batch's own position on `B-36`/`B-72`).

**SEED-2 (path traversal).** `mapper/store.py` gains `check_map_id(map_id)`, the one place the rule lives, and
`MapIdError(MapStoreError)` whose authored message names the rule and never the typed name or a path. It refuses:
empty; `/`, `\`, `:` (separators and drive letters); `..`; `< > " | ? *` and control characters; Windows device
names `CON PRN AUX NUL COM1-9 LPT1-9` (case folded, any extension, superscript digits included); a leading space or a
trailing dot or space. `MapStore.save` and `MapStore.load` call it first, so every write door and the read door (a
file-derived `map:` link) share it.

**SEED-1 (silent overwrite).** `MapStore.create(map_id, graph)` = `check_new_map_id` (the rule, plus "neither
`<id>.mmd` nor `<id>_nodos.yml` exists") + `save`. `create_seed` and `create_from_template` call `create`. `save`
keeps replacing by design (editing an open map).

**UI (`mapper/app.py`).** `_refusal_toast` shows a `MapIdError`'s rule text (the one exception text allowed
through). `_save_or_toast(..., new=True)` routes the CSV "save as" through `store.create`. The construct dialog
(`ConstructScreen`) asks `store.check_new_map_id` before it dismisses, so a refused name toasts and **the dialog
stays open**; the store refuses again by itself. `action_construct`/`action_template` use `_refusal_toast` ahead of
their generic toast. Toast copy is Spanish (Inc-EN will translate).

## 2 · Files modified

| File | Change |
|---|---|
| `mapper/store.py` | `MapIdError`, `_RESERVED_NAMES`, `check_map_id`; `load`/`save` validate; `check_new_map_id`, `create`; `create_seed`/`create_from_template` call `create` |
| `mapper/app.py` | `_refusal_toast`; `_save_or_toast(new=)`; `ConstructScreen` early check; two toast sites; CSV save-as `new=True`; import line |
| `tests/test_seed_safety.py` | new, 47 cases (not capped) |
| `.dev-flow/.../01-requirements.md` | `A-113` appended |
| `.dev-flow/BACKLOG.md` | `B-74`..`B-77` |
| this file | record |

## 3 · How to test

```
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest tests/test_seed_safety.py -q
```

By hand, from home: `n`, type `layout` (an existing map), `↵`: a toast says it exists and the dialog stays open;
type `../x`: a toast names the rule; type `ok-name`: the map is created.

## 4 · Test results

### Entry-point census (every place operator text becomes a map id or a file name)

Method: grep of `write_text|write_bytes|open(|mkdir|save_svg|shutil|.replace(|unlink` over `mapper/`, plus every
`store.save/load/create*` and `MapScreen(` call site; the AST-shaped census test
(`test_g6_store_surrogates.py`, unguarded `store.save()` sites) still passes.

| # | Entry point | Source of the text | Reaches | Verdict |
|---|---|---|---|---|
| 1 | `n` construct -> `ConstructScreen` -> `action_construct` -> `create_seed` | typed | `.mmd` + `_nodos.yml` write | **defect on base (both)**; fixed; real-key arms |
| 2 | `t` template -> `_PromptScreen` -> `action_template` -> `create_from_template` | typed | write | **defect on base (both)**; fixed; real-key arms |
| 3 | `i` CSV -> `_ImportPreviewScreen.action_save` ("guardar como") -> `store.save` | typed | write | **defect on base (both)**; now `store.create`; real-key arms |
| 4 | `MapStore.save` (every other caller: field commit, attachments, undo, add-child, archive, `on_mount` "new") | `map_id` of the open map | write | covered by `check_map_id` in `save`; ids there come from `load`/create |
| 5 | `MapStore.load` via `MapScreen(linked)` (`action_open_ficha`, `Node.linked_map_id()`), `last_session()` (`.mapper/state.json`), home recents | FILE-derived (`map:` field, state file) | read | **read-side traversal on base**; `check_map_id` in `load`; store-level arm |
| 6 | SVG export `{map_id}.svg` (`app.py` ~4038, ~4057) | open map's id | write | safe once 4/5 hold (id validated at load/create); no separate check |
| 7 | `diff.git_diff` -> `git show HEAD:{map_id}.mmd` | open map's id | read via git | same as 6 |
| 8 | `osopen.open_target` attachment path | file-derived | launch | already confined (`REFUSED_OUTSIDE`); not touched |
| 9 | CSV source path (`action_import_csv`) | typed | READ of an operator-chosen file | by design a file picker, not workspace-confined; not touched |
| 10 | `factory.action_import_office` (`templates/<source.name>`) | typed | copy | basename only; toast leaks the expanded path -> `B-77`(a), not fixed |
| 11 | `github._ensure_cloned` (`cache_dir / name` from a URL's last segment) | typed | clone target | not a map id; `..` segment unchecked -> `B-77`(b), not reproduced |
| 12 | `store.record_session` / `.mapper/state.json` | internal | write | fixed name; no operator text |

Not driven with real keys: 4-7 (they need a loaded map or a hand-edited file); covered by the store-level arms and
the mutant M4.

### RED before the fix (commit `7521ac9`, run on the `fddd07d` tree)

`pytest tests/test_seed_safety.py -q`: **4 passed, 43 xfailed** (strict xfail: any accidental pass would fail the
run). Driven again with `--runxfail` to read the real failures:

- existing name, all three entries: `assert {'layout.mmd': ...} == {...}` differs, sha256 of both files changed
  (`an existing map was overwritten`); the `LAYOUT` spelling too (NTFS is case-insensitive).
- `C:\x` and `a:b`: `assert not [WindowsPath('C:/x.mmd')]` / `[WindowsPath('a:b.mmd')]` (a write outside the
  workspace was attempted; the harness's write guard recorded it and refused to perform it, so the RED run never
  touched a drive root).
- `../x`, `..\x`: the tree snapshot of the workspace's parent changed (files appeared one level up, inside the
  sandbox).
- `a/b`: toast was `no se pudo crear el mapa 'a/b': FileNotFoundError` -- it echoed the typed text.
- store level: `DID NOT RAISE MapStoreError` for every bad name and for an existing id.

Positive controls that pass on the base and must keep passing: a valid new name creates the map through all three
entries; ordinary names (`mi mapa`, `a.b`, `ñandú`, `concept`, `console`) are accepted.

### GREEN after the fix (commit `597b7fa`)

`tests/test_seed_safety.py`: **47 passed**. Related suites (`test_store`, `test_g6_store_surrogates`,
`test_inc9c`, `test_fold`, `test_no_operator_paths`, `test_import_csv`, `test_legacy_fixture`): **118 passed,
3 xfailed** (the 3 xfailed are pre-existing).

### Mutant table

Harness outside the repo (scratchpad); sha256 pin of `store.py` and `app.py` taken first; byte-level I/O in the
files' own CRLF; the verdict printed BEFORE the restore; pin re-checked after (both `True`). Kill command:
`pytest tests/test_seed_safety.py -q -x`.

| # | Mutant | Verdict | First killer |
|---|---|---|---|
| M1 | existence check removed (`if False:`) | KILLED | `test_seed1_existing_map_is_left_byte_identical[construct-layout]` |
| M1b | existence check ignores the sidecar | KILLED | `test_seed_store_refuses_when_only_the_sidecar_exists` |
| M2 | the `..` check removed | KILLED | `test_seed_store_refuses_every_write_door[a..b]` |
| M3 | validate only in the UI (store calls removed; dialog calls `check_map_id` directly) | KILLED | `test_seed2_bad_name_writes_nothing_and_toasts[import-../x]` |
| M4 | `load` does not validate | KILLED | `test_seed_store_load_refuses_a_link_that_leaves_the_workspace` |
| M5 | CSV save-as calls `save` instead of `create` | KILLED | `test_seed1_existing_map_is_left_byte_identical[import-layout]` |

Honest note on M2: a first version of the existence mutant (`if False and A or B`) SURVIVED because of operator
precedence (`B` still ran); it was a bad mutant, not a weak test, and was replaced by M1/M1b. M2's only
distinguishing input is a name like `a..b`, because `../x` is already refused by the separator rule (`B-76`).

### Lane, ruff, guards

- **Full default lane, once, after the fix** (run on the tree at `597b7fa`): `1485 passed, 20 deselected, 3 xfailed
  in 985.94s`. Reconciliation: baseline `1438 passed, 3 xfailed, 20 deselected` + the 47 new cases = 1485; the 3
  xfailed and 20 deselected are unchanged; 0 failed.
- **Guards** (`tests/test_fold.py`, `tests/test_no_operator_paths.py`), run again before the docs commit:
  `21 passed, 3 xfailed` (the 3 are pre-existing).
- **`ruff check mapper tests/test_seed_safety.py`:** 9 errors, all in files this increment did not touch or in
  lines it did not add (`app.py:6` `import re` unused, `darkside.py`, `diff.py`, `model.py`, `office.py`,
  `screens/factory.py`, `screens/settings.py`); none in `store.py`, none in the new test file. Not measured on the
  base for a before/after count; the listed lines are not in this diff.
- **Byte scan** of each staged diff and of each commit message for Cc/Cf/Zl/Zp/Cs and for the account name: clean.

## 5 · Risks

- `load` now validates, so a pre-existing map whose id is a Windows-reserved name or ends in a dot/space would
  stop loading. Such a file cannot be created or listed normally on Windows; none exists in `maps/`, `fixtures/` or
  the suite. Not measured on the operator's real workspace.
- The construct dialog now needs `app.store`; any other host of `ConstructScreen` without a store would raise
  (none exists).
- Check-then-write is not atomic (`B-75`).
- Toast text is Spanish and unreviewed by the operator; Inc-EN translates it.

## 6 · Pending items

- `B-74`..`B-77` (new). `B-77` holds two findings outside the map-id rule that were read, not reproduced.
- The security review that follows this increment.

## 7 · Suggested next task

Security review of `check_map_id` (Windows name coverage: short names `PROGRA~1`, trailing-stream spellings, names
over `MAX_PATH`) and of `B-77`; then the next planned increment.

---

## Findings

| Id | Status |
|---|---|
| `SEED-F1` (`B-74`) | decision recorded, not a defect |
| `SEED-F2` (`B-75`) | carry |
| `SEED-F3` (`B-76`) | carry |
| `SEED-F4` (`B-77`) | carry, two sites |
