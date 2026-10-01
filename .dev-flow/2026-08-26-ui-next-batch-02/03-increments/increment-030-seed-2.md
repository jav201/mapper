# Increment 030 — Inc-SEED-2 · the security review of Inc-SEED, closed

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `030` — Inc-SEED-2, a micro-increment |
| Agent | `software-dev` |
| Date | 2026-09-30 |
| Authority | Security review of `increment-028-seed-safety.md` (findings named `SEED2-Fn` here) |
| Starting state | branch `feat/ui-next-batch-02` @ `a4f8b42`, clean |
| Commits | `fd37b9e` (arms, strict xfail, RED) -> `ee6c3f5` (F1) -> `6b9fc44` (F2-F5) -> docs commit (this file, `A-113` note, `BACKLOG.md`) |
| Source files | 2 (`mapper/store.py`, `mapper/app.py`); cap 4 |

---

## 1 · What changed

| Finding | Sev. | Change |
|---|---|---|
| `SEED2-F1` | MEDIUM, pre-existing, silent data loss | `MapScreen.on_mount`: the `map_id == "new"` branch is deleted (it replaced the graph with `root[nuevo mapa]` and saved). A real map named `new`, reached from the home row or a `map:` link, opens like any other. |
| `SEED2-F2` (`B-76`) | MEDIUM | `check_map_id`: the `".." in map_id` substring rule is dropped. `v1..v2` creates, saves, loads. Dot-only ids (`.`, `..`, `...`) are still refused by the existing "ends in a dot or space" rule. A separate dot-only rule would be dead code (every dot-only id ends in a dot), so none was added; a comment says why. |
| `SEED2-F3` | LOW | `MAX_MAP_ID_LEN = 100`; a longer id raises a `MapIdError` whose text names the rule and not the typed name. `A-113` gets a dated note: "no path and no profile", not "no echo of the typed name". |
| `SEED2-F4` | LOW | Lone surrogates (U+D800 to U+DFFF) are refused. |
| `SEED2-F5` | LOW | `CONIN$`, `CONOUT$`, `CLOCK$` join `_RESERVED_NAMES`. |

**Why 100.** The longest file the store writes for an id is `<id>_nodos.yml` plus a `.tmp` sibling (about 15
characters beyond the id). With `MAX_PATH` = 260 and a path separator, 100 leaves roughly 140 characters for the
workspace path, longer than a typical project path. It is a margin, not a measurement on the operator's real
workspace (`B-78`). Characters, not UTF-8 bytes, are counted, so accented names are not penalised.

**`SEED2-F4`, as reproduced.** The review said an id `a` + U+D800 passes, writes both files and then fails at the
reindex. On `a4f8b42` that is true of `store.save` and `store.create`: both `a<U+D800>.mmd` and
`a<U+D800>_nodos.yml` were left on disk, with a `UnicodeEncodeError` from the reindex. It is NOT true of
`create_seed`: there the id is also the root title, the text encoding fails before any file is created, and the
toast is the generic `no se pudo crear el mapa '...': UnicodeEncodeError`. The arms cover both (store level:
nothing left behind; construct dialog: a rule toast).

## 2 · Files modified

| File | Change |
|---|---|
| `mapper/store.py` | `MAX_MAP_ID_LEN`, length rule, surrogate rule, `..` rule dropped, three reserved names |
| `mapper/app.py` | `MapScreen.on_mount`: dead `"new"` branch deleted, the `try` block dedented |
| `tests/test_seed2.py` | new, 21 cases (not capped) |
| `tests/test_seed_safety.py` | `a..b` removed from the refusal list (it is now valid) |
| `tests/test_g6_store_surrogates.py` | `test_g6c_f3_new_map_on_mount_save_degrades_to_a_toast` removed: it drove the deleted branch |
| `.dev-flow/.../01-requirements.md` | dated note under `A-113` (the last amendment id taken stays `A-113`) |
| `.dev-flow/BACKLOG.md` | `B-76` closed; `B-78` added |
| this file | record |

## 3 · How to test

```
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest tests/test_seed2.py tests/test_seed_safety.py -q
```

By hand: press `n` and type `v1..v2`: the map is created. Type 101 characters: a toast names the length rule.
Open a map named `new` from the home list: its content is unchanged.

## 4 · Test results

### Producer census for `"new"` (taken before deleting the branch)

| Method | Result |
|---|---|
| `grep '"new"' mapper/` | `app.py:1576` (the branch itself) and `darkside.py:118` (an unrelated status label `("○", "new")`) |
| AST walk of `mapper/**/*.py`, every `Call` to `MapScreen` | 8 calls: `app.py:930` (`last_session` id), `:949` `:958` `:978` `:1090` (`name`, typed or from a callback), `:1028` (home row key), `:3516` (`node.linked_map_id()`). No call passes a literal. |
| AST walk, every string constant `"new"` | only `app.py:1576` and `darkside.py:118` |
| `grep` in `tests/` | one consumer: `test_g6c_f3_...` (`app.push_screen(MapScreen("new"))`), the test of the dead branch |

Conclusion: no producer passes the sentinel on purpose. A name the operator types, or a link a file carries, can
still equal `new`. A typed `new` in the construct dialog did create a real map and the sentinel then rewrote it:
the same defect.

### RED before the fix (commit `fd37b9e`, on the `a4f8b42` tree)

`pytest tests/test_seed2.py -q`: **8 passed, 13 xfailed** (strict). With `--runxfail`: **13 failed, 8 passed**.
The 8 passing cases are positive controls that must hold on the base (dot-only ids refused, a 100-character id
accepted, `$`-names accepted). Failure reasons read from the run:

- F1: `assert 'nuevo mapa' == 'KEEP-ME'`.
- F2: `MapIdError: el nombre del mapa no puede contener '..'` on `v1..v2`.
- F3: `DID NOT RAISE` on 101 characters; the 300-character toast contained the typed name
  (`zzzz...': FileNotFoundError`).
- F4: `DID NOT RAISE MapIdError` for `save`; the construct toast was
  `no se pudo crear el mapa 'a\ud800': UnicodeEncodeError`.
- F5: `DID NOT RAISE` for each of the three names and their case variants.

A first draft of the F5 arm included `"CONOUT$ "` (trailing space). It XPASSed (strict) on the base, because the
trailing-space rule already refuses it, so it was removed: it was not a defect arm. A first draft of the F4 arm
used `create_seed` only and also XPASSed, which is how the `create_seed` finding above surfaced.

### GREEN after the fix

`tests/test_seed2.py`, `test_seed_safety.py`, `test_store.py`, `test_g6_store_surrogates.py`: 112 passed.

### Mutant table

Harness outside the repo (scratchpad). sha256 pin of `store.py` and `app.py` taken first, byte-level I/O in each
file's own line endings, the verdict printed BEFORE the restore, the pin re-checked after (`pin restored True`).
Kill command: `pytest tests/test_seed2.py tests/test_seed_safety.py -q -x`.

| # | Mutant | Verdict | First killer (`tests/test_seed2.py::`) |
|---|---|---|---|
| M1 | the `"new"` sentinel reinstated (`store.save("new", Graph())` before the load) | KILLED | `test_seed2_f1_opening_a_real_map_named_new_leaves_it_byte_identical` |
| M2 | `..` substring rule reinstated | KILLED | `test_seed2_f2_an_id_that_merely_contains_two_dots_creates_saves_and_loads` |
| M3 | trailing dot/space rule removed (the rule that carries dot-only ids) | KILLED | `test_seed2_f2_dot_only_ids_are_still_refused[.]` |
| M4 | length rule removed | KILLED | `test_seed2_f3_store_refuses_an_id_over_the_limit` |
| M5 | limit 100 -> 200 | KILLED | `test_seed2_f3_store_refuses_an_id_over_the_limit` |
| M5b | limit `>=` instead of `>` | KILLED | `test_seed2_f3_an_id_at_the_limit_is_accepted` |
| M6 | surrogate rule removed | KILLED | `test_seed2_f4_store_refuses_a_lone_surrogate_and_writes_nothing[a+D800]` |
| M6b | surrogate range narrowed to U+D800 | KILLED | same test, `[DFFF]` |
| M7a/b/c | `CONIN$` / `CONOUT$` / `CLOCK$` dropped, one at a time | 3 of 3 KILLED | `test_seed2_f5_console_and_clock_device_names_are_refused[<name>]` |
| M8 | `check_map_id` returns at once | KILLED | `test_seed2_f2_dot_only_ids_are_still_refused[.]` |

The requested mutant "remove the dot-only rule -> RED on `..`" would be an equivalent mutant: no separate
dot-only rule exists, because the trailing-dot rule already refuses every dot-only id. M3 is its honest form, and
it is killed.

### Lane, ruff, guards

- **Full default lane, once, after the last code commit** (`6b9fc44`; the docs commit changes no code): `1541 passed, 20 deselected, 3 xfailed in 1223.51s`, 0 failed. Reconciliation against the baseline `1522 passed, 3 xfailed, 20 deselected`: +21 new cases in `test_seed2.py`, -1 `test_g6c_f3_...` removed, -1 case `a..b` removed from `test_seed_safety.py` = 1541. The 3 xfailed and 20 deselected are unchanged (the new file's strict xfails are all closed).

- **Ruff.** `ruff check .` at the repo root, on `a4f8b42` (a `git archive` copy outside the repo) and on HEAD,
  issues compared as `file: code message` without line numbers: **26 and 26, set difference empty** (all in files
  this increment did not touch: `app.py:6` unused `import re`, `darkside.py`, `diff.py`, `model.py`,
  `office.py`, `screens/*`). The archive copy also reports 18 issues under `prototypes/`, which the working tree
  does not lint; they are in neither count and untouched.
- **Guards** (`tests/test_fold.py`, `tests/test_no_operator_paths.py`): `21 passed, 3 xfailed` (the 3 are pre-existing), run before the docs commit.
- **Byte scan** of each staged diff and each commit message for Cc/Cf/Zl/Zp/Cs and the account name: clean for
  the first three commits (the docs commit is scanned before it is made). The surrogate strings in the tests are
  built with `chr()`.

## 5 · Risks

- Any pre-existing map named `new` now loads its real content (the intended fix). A caller that wanted a scratch
  map by pushing `MapScreen("new")` would now get `error cargando mapa`; none exists.
- Dropping `..` widens what is accepted. It is safe on the stated argument (no separator, so no traversal) and
  covered by the `v1..v2` arm and the dot-only arms; it was not independently reviewed.
- The 100-character limit can refuse an existing legacy map with a longer id on load. None exists in `maps/`,
  `fixtures/` or the suite; not measured on the operator's real workspace.
- Removing `test_g6c_f3_...` removes the only test of the first-save toast on that screen; the branch it tested no
  longer exists, and the AST census of unguarded `store.save()` sites still passes.

## 6 · Pending items

- `B-78` (new): the limit is not measured on a real workspace; short-name and stream spellings undriven;
  `COM0`/`LPT0` unmeasured.
- `B-74`, `B-75`, `B-77` from `Inc-SEED` stay open.
- `Inc-9e` not started.

## 7 · Suggested next task

`Inc-9e`, as planned. If the security reviewer wants it, a short measurement of `B-78` (a long workspace path,
`COM0`) is a half-hour task.

---

## Findings

| Id | Status |
|---|---|
| `SEED2-F1` | closed |
| `SEED2-F2` (`B-76`) | closed |
| `SEED2-F3` | closed (limit justified above; `A-113` wording softened) |
| `SEED2-F4` | closed (reproduced on `save`/`create`, not on `create_seed`) |
| `SEED2-F5` | closed |
| `SEED2-F6` (`B-78`) | carry |
