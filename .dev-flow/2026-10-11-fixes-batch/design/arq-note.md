# ARQ note — mapper — Batch 2026-10-11-fixes-batch

> **Artifact language.** English (`state.json` `language: en`).
> **Station:** ARQ, activated by the P0 trigger evaluation (`PLAN.md` §Triggers: **A2** one increment touches two modules, **A3** an exposed contract changes behaviour).
> **Status:** drafted by `software-dev` for `architect` review; the operator approves the map (station gate). Nothing here edits `docs/ARCHITECTURE.md`; the amendment it asks for is listed in §1 and lands in the batch, not in this note.
> **Run late:** P1 and P2 already ran. The requirements are not reopened; this note checks them against the map and adds three findings (F1-F3) that the PDR carries.
> **Evidence base:** worktree `feat/fixes-batch` @ `7764a4e` (code identical to `master` `5a991c6`; only `.dev-flow/` differs). Every `file:line` below was read at that commit.

## 0 · Verdict in one paragraph

No module boundary moves and no dependency edge is added. **The expectation that `docs/ARCHITECTURE.md` would not change is wrong in one respect (F1):** `mapper/screens/roles.py`, which increment 003 edits, is claimed by no row of §2 — the map has been stale since the ReqHarness batch. The staleness rule makes that an ARQ finding on its own, and the fix is one path added to the `screens` row (plus a two-clause note on the `mermaid` row and the header fields). Two exposed contracts change behaviour (§2); every consumer was read and is safe. B-127 introduces the project's second Textual thread worker (§3).

## 1 · Module map impact

### 1.1 What was checked (executed)

| Check | Command / source | Result |
|---|---|---|
| Every touched source file is claimed by a §2 row | Script: parse the §2 `Paths it owns` cells, `fnmatch` every `mapper/**/*.py` against them | `unclaimed: ['mapper/screens/roles.py']` — the only unclaimed file in the tree |
| What the unclaimed file is | `ls mapper/screens` → `roles.py` present; §2 `screens` row lists 15 literal paths (`__init__`, `palette`, `help`, `coverage`, `editor`, `factory`, `settings`, `draft_guard`, `common`, `prompt`, `construct`, `repo`, `plug_repo`, `import_preview`, `home`) — no `roles.py` | stale since the ReqHarness batch added the screen; that batch's ARQ amendment added the `reqharness` module and the `screens`→`reqharness` edge but not the file |
| Touched files per increment vs rows | 001: `mapper/mermaid.py` (`mermaid`), `mapper/import_csv.py` (`import_csv`) · 002: `mapper/mermaid.py`, `mapper/store.py` (`store`, docstring only) · 003: `mapper/screens/roles.py` (**no row**) · 004: tests only | A2 fired by 001 and 002 (two modules each); 003 is the stale-map case |
| Dependency edges used by the change | `import_csv` → `mermaid` (`slugify`): exists, §3 row `import_csv`. `store` → `model` only; the `mermaid` imports in `store.py` (`:508`, `:728`, `:827`, `:861`) are function-local and already exist (the §3 `store` row says `model` only — a pre-existing gap, **not widened** by this batch, recorded in F3). `screens/roles.py` → `reqharness` (already imports `chain`, `identity`, `pending`, `release`, `config`, `records`) and → `textual` (`textual.worker` is new in this file, not a new module edge: `screens` may import Textual) | **0 new edges** |
| The map-truth test that parses §2 | `pytest -p no:cacheprovider tests/test_repair_map_truth.py` → `42 passed` (run in the worktree, before any edit). Its path arm asserts every declared path exists on disk, so adding `mapper/screens/roles.py` passes; removing nothing | safe to amend |

### 1.2 The map diff this batch owes

Not empty. The minimum, in one commit, **no later than the commit that first edits `roles.py`** (increment 003; a docs file, outside the source cap):

1. §2 `screens` row, `Paths it owns`: add `` `mapper/screens/roles.py` `` (F1). Staleness rule: the map is amended before the touched file is edited.
2. §2 `mermaid` row, `What it EXPOSES`: append, after `slugify(s) -> str`: *"(returns `""` when nothing word-like survives — F-batch 2026-10-11)"* and, after `dump(graph)`: *"(writes the declared root's declaration first when text order would otherwise elect another root)"*. This records the two contract changes of §2 where the A3 oracle reads them.
3. **Added by the PDR (architect):** the same amendment also edits `docs/ARCHITECTURE.md:113`: `roles.py` in the `screens` row's paths, "`roles.py` owns `RolesScreen`" in its ownership prose and `RolesScreen` in its exposes list; the `mermaid` row note cites the batch id `2026-10-11-fixes-batch`. It lands in increment 003 itself (a docs file, outside the source cap), not before.
4. Header: `Last amended by` → `2026-10-11-fixes-batch (ARQ)`; `Date` → the landing date.
5. A short amendment block in the file's established style: "no boundary moves, no dependency edge added; one stale path claimed; two exposed-contract changes".

§3 (dependency), §4 (frozen interfaces), §1 (context: the git crossing is unchanged, same three allow-listed calls) and §6 are untouched. **Evidence of "no boundary change" is therefore: items 1-4 are the entire diff, and `git diff -- docs/ARCHITECTURE.md` after the batch will show only them.**

## 2 · Exposed-contract changes (A3) and every consumer

### 2.1 `mermaid.slugify` — an empty result is now `""`, not `"n"`

Row: `mermaid` EXPOSES `slugify(s) -> str`. The signature does not change; the **return domain widens by one value**. Inputs that now return `""`: `""`, whitespace, and any string with no `\w` character (`"---"`, `"!!!"`). Inputs with a word character return exactly what they return today (Unicode scope unchanged: `slugify("Niño") == "niño"`, R5 / LED .11).

| Consumer (file:line, base) | Today | After | Why safe |
|---|---|---|---|
| `mapper/import_csv.py:59` `nid = slugify(raw_id)` | an unreadable id becomes node `n`, so ids with no slug characters collide on `n` and a root literally named `N` saves as a self-cycle | `""` is detected and replaced by the next `row-N` (LLR-FX.1.3); the typed text stays as `CsvRow.raw_id` and the title fallback | in-batch change, covered by AT-084 + `test_id_with_no_slug_characters_becomes_row_n`; M-FX1/M-FX3 redden it |
| `mapper/import_csv.py:70` `parent_id = slugify(parent cell)` | an **empty** parent cell is slugified to `n` and read as a reference to a node `n` — the B-115 root cause | the cell is tested blank-first, before any slugging; a non-blank cell whose slug is empty parks the row like an unknown id (LLR-FX.1.2) | in-batch change; M-FX2 reddens it |
| `mapper/screens/map/editing.py:115` `base = slugify(title) or "n"` (import at `:10`), followed by the uniqueness loop at `:117-120` | for a punctuation-only title: `slugify` returned `"n"`, `base = "n"` | `slugify` returns `""`, `or "n"` supplies `"n"`: **`base` is `"n"` in both worlds**; the loop then produces `n`, `n-1`, … identically | no behaviour change; the call site already tolerates `""`, which is why the requirements leave it untouched (premise 2) |
| `tests/test_mermaid.py:12` `assert slugify("---") == "n"` | the only pin of the old value | moves to `""` in increment 001 (LLR-FX.1.1), executed as the only existing test that fails on the patched tree (premise 7) | the pin encoded the defect |
| `tests/test_csv_safety_store.py:31` | a comment mentioning slugify, no assertion | unchanged | n/a |

Census of the symbol: `grep -rn slugify mapper` returns exactly the three production sites above plus the definition; `grep -rl slugify tests` returns the two test files above. No other module imports it (`__init__` re-exports none).

### 2.2 `mermaid.dump` — the declared root's declaration is written first when text order would elect another

Row: `mermaid` EXPOSES `dump(graph) -> str`. The signature is unchanged; the **output text changes for one class of input**: a graph whose `root_id` is a parentless node that is not the first parentless node of the text. For every other graph (single-root trees, the shipped `.mmd` fixtures, all 8 dump goldens, AT-076) the bytes are identical (premises 3-5, executed).

| Consumer (file:line, base) | What it does with the text | Effect of the change | Why safe |
|---|---|---|---|
| `mapper/store.py:873` `mmd_text = dump(graph)` in `MapStore.save` (import `:861`) | the text is the persisted `.mmd` (`_write_tmp(mmd_path, mmd_text)` at `:899`) | a forest map's `.mmd` lists the root's line first; its **sidecar is unchanged** | writer-side fix; AT-086; on-disk consequence in F2 |
| `mapper/store.py:878` `_check_round_trip(graph, mmd_text)` → `parse` at `:827` | refuses a save whose text re-parses to different node ids or edge multiset | node set and edge multiset of the new text are the same as the old text's (a declaration line moves, none is added or dropped); **no root comparison is added** (R3) | the three refusal arms of `tests/test_csv_safety_store.py` pass unchanged (15 passed in the premise-3 run); the docstring that claimed a forest's root drifts is corrected in 002 (LLR-FX.3.2) |
| `mapper/store.py:508` `parse` in `_graph_from_sidecar`, reached by `MapStore.load` | reads the `.mmd` | `parse` is **unchanged**; it now elects the declared root because the text names it first | the codec rule "first parentless node in text order" (`mermaid.py` `parse`, last statements) is the reader contract and is not touched |
| `mapper/screens/map/undo.py:10,42` `dump_mermaid(graph)` in `_push_snapshot` → `:59` `_pop_snapshot` → `store._graph_from_sidecar(...)` → `parse` | an undo snapshot is `dump` + sidecar, restored through `parse` | **a consumer the requirements did not list:** undoing on a forest map used to restore a different root for the same reason as B-117; it now restores the root. This is a beneficiary, not a risk | no AT covers it. The PDR proposes one extra, test-only case (`TC-FX-3.3`, §5 there) so the benefit is pinned, not assumed |
| `mapper/diff.py:51-66` reads the **HEAD** `.mmd` text through `store._graph_from_sidecar` and compares node-level | old text, old ordering | `parse` unchanged, so old files parse exactly as before; the comparison is node-level (`_compare_graphs`), not root-level | no effect |
| `tests/perf_goldens_capture.py` (writes the goldens) and `tests/test_perf_dump.py` (reads them); 17 test files call `dump(` (`grep -rl "dump(" tests/*.py`) | pin bytes | 8/8 dump goldens + AT-076 identical (B3 census, PLAN §Triggers); the one inline arm that builds a forest (`orphan-order`) needs a fixture line, bytes unchanged (premise 4) | the pin that moves is named in LLR-FX.3.2 |

Reverse census (B1, re-run at this note): `grep -rl slugify tests/` → 2 files; `grep -rl preview_csv tests/` → 8 files (`test_csv_safety_preview`, `test_gate2`, `test_import_csv`, `test_inc9c`, `test_inc9n`, `test_mod_compat`, `test_repair_cycles`, `test_repair_fields`); `grep -rl "dump(" tests/` → 17 files; `grep -rl "_open_roles" tests/` → `test_roles_screen.py`; importers of `RolesScreen`: `mapper/app.py:37`, `mapper/screens/home.py:45`, `tests/test_keymap.py:30`, `tests/test_roles_screen.py`. B4 (output-then-consume): `dump` → `parse` is AT-086; `preview_csv` → `MapStore.save` → `MapStore.load` is AT-084/AT-085. All already exist; none is added by this note.

## 3 · B-127 — the threading change (increment 003)

This is a **runtime** change, not a structural one: no module or edge moves, but `RolesScreen` becomes the second place in the tree that runs code off the UI thread (the first is `mapper/screens/repo.py:259` `@work(thread=True, exit_on_error=False)` with `call_from_thread` at `:263`). Pinned framework: `pyproject.toml:11` `textual==8.2.8`.

| Aspect | Design | Evidence / reason |
|---|---|---|
| What runs off-thread | `identity.repo_root(workspace)` then, if a repo was found, `identity.read(top)` — the three allow-listed read-only git calls, nothing else. File reads (chain, pending, config, verdict) stay on the UI thread, fed from the returned facts `(top, who)` | `roles.py:178` and `:222` today; the git calls are the only slow, unbounded step (10 s timeout each, `identity.py:_TIMEOUT`) |
| Mechanism | one `@work(thread=True)` method on `RolesScreen`, started from `on_mount` and `on_screen_resume`; the worker RETURNS the facts and `on_worker_state_changed` (SUCCESS) applies them on the UI thread after the generation and `is_attached` checks; **no `call_from_thread`** (architect ruling R7: avoids the exit-time hang) | `repo.py:259` for the worker decorator only (premise 6) |
| Generation guard | `self._gen` incremented per start; `_apply_facts` ignores any result whose generation is not the latest (LLR-FX.4.2, M-FX11) | "latest discovery wins" |
| **Exact catch set** | in the worker: `try: … except (OSError, ValueError, subprocess.SubprocessError, ValidationError): facts = (identity.NO_REPO, None)`. `ValidationError` = `mapper.reqharness.records.ValidationError` (already imported at `roles.py:69`). Nothing broader. Any other exception propagates out of the worker; `exit_on_error` is left at Textual's default (`True`), so an unexpected defect ends the app loudly rather than leaving a blank screen | R5 / LED .8. A bare `except Exception` was rejected: it would hide defects. Note the contrast with `repo.py:259`, which sets `exit_on_error=False` for a network worker whose failures are expected; here they are not |
| Why those four | `identity._run_git` already converts `OSError`/`SubprocessError` from `subprocess.run` into `None` (`identity.py:201`), and raises `ValueError` for an off-allowlist call; `repo_root`/`read` therefore do not raise for git failures today. The catch set is the defence for what the helper layers *could* raise (path resolution `OSError`, the allowlist `ValueError`, a record-layer `ValidationError`) — each maps onto the existing `no repo` state with its existing copy | the four types are the ones the P2 review named; no new copy is added |
| Cancellation on unmount | **already provided by the pinned framework:** `textual/widget.py:4851` `Widget._on_unmount` calls `self.workers.cancel_node(self)`, and `Screen` is a `Widget`. A thread worker cannot be interrupted, only flagged, so cancellation alone is not enough: the worker checks `get_current_worker().is_cancelled` before handing back, and `_apply_facts` checks `self.is_attached` and the generation before touching any widget. The result of a discovery that finishes after the screen was popped is discarded: no paint, no notification, no exception (LLR-FX.4.1) | **Finding F3a for the reviewers:** an explicit `on_unmount: self.workers.cancel_node(self)` would duplicate the framework (surgical-changes rule, and a dead line no mutant can redden). The PDR therefore specifies the **hand-back guard** as the owned behaviour; M-FX13 is "remove the cancelled/`is_attached` check in the hand-back". If the architect prefers the explicit call as documentation of intent, it costs one line and changes no behaviour |
| Thread safety | the worker touches no widget and no screen attribute; it receives `workspace` as an argument and returns plain values. `identity` keeps one module-level dict, `_GIT_CACHE` (`identity.py:73`), written at `:105`: with the mount and resume workers possibly running together the two can write the same key with the same resolved path — an idempotent write of a `dict`, atomic under the GIL, so benign. `identity.py` is **not** touched (the screen caches the facts instead) | stated so the reviewer does not have to find it |
| Doubled start (observed) | at push, both `on_mount` and `on_screen_resume` fire, so two discoveries start concurrently (6 git calls at open — **the same 6 the synchronous code makes today**, measured in the scratch copy: 6 calls before the base `press R` returns, 6 recorded by the workers after). The generation guard makes the second win. Not new cost, not specified away; recorded so the DDR can decide whether to coalesce | F3b |
| Keypress-time reloads | `space`, `a`, `r` call `_reload()` which re-reads disk from the cached facts and runs **0** git calls (today each keypress re-runs 3 — measured: 9 calls in the base run vs 6 in the worker run, the extra 3 being the `space` press). The cache lives in the screen (`self._facts`) | LLR-FX.4.4, M-FX10 |
| `_load` signature | `_load(workspace)` → `_load(facts)`. Its only caller is `RolesScreen._reload` (`roles.py:483`); no test or module calls `_load` (`grep -rn "_load(" mapper/screens/roles.py tests/test_roles_screen.py tests/test_keymap.py`). The `workspace` parameter would be dead after the change | consumer census: 1 |
| Test seam | monkeypatch `identity.repo_root` / `identity.read` (or `identity._run_git` for the thread assertion). No production seam is added | R5 |

**What does not change:** `identity.py`, `release.py`, `chain.py`, the hardened git allow-list (§1 of the map), the four Static ids, the key scope, every string on the screen.

## 4 · Findings carried to the PDR

- **F1 (map stale).** `roles.py` unclaimed; fix in §1.2. Owner: architect to approve, lands with increment 003.
- **F2 (on-disk effect of `dump`) — CORRECTED at the PDR (architect, R7).** A map loaded from disk takes its root from `parse` (the first parentless node in text order), so on resave the declared root is already the text-first parentless node, the hoist does not fire, and the bytes stay the same: there is no one-time reorder. The hoist fires only when the root was set in-session (CSV import; `editing.py:221` after a root delete). B-117 stops future drift; it cannot repair a map that already drifted, because the declared root was never stored. The sidecar and every node/edge are unchanged. (The first draft of this finding said the next save reorders the file; that was wrong.)
- **F3 (smaller).** (a) Cancellation on unmount is the framework's; the owned behaviour is the hand-back guard (§3). (b) Mount and resume both start a discovery (§3). (c) The §3 map row for `store` lists `model` only while `store.py` imports `mermaid` function-locally at four sites — a pre-existing gap outside this batch's scope, **not** fixed here, flagged for the backlog (B-132: the `store` → `mermaid` map gap, F3c). F3b (the doubled discovery start) is carried to the DDR as an item, not a PDR condition.

## 5 · Gate

Approve the map as amended in §1.2, or iterate with the named gap. No code, test, `state.json` or `docs/ARCHITECTURE.md` edit was made to produce this note; the scratch copy used to measure §3 lives outside the repository.
