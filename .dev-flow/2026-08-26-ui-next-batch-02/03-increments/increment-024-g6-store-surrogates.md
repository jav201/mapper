# Increment 024 — G6 · coerce ficha text at graph entry, guard the 6 unguarded `store.save()` sites

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `024` — G6, a micro-increment cut immediately after Inc-8 |
| Agent | `software-dev` |
| Date | 2026-09-29 |
| Authority | Operator verdict, Round 4, `VERDICT-inc8-legend-2026-09-28.md` § "Round 4", `G6`, verbatim: *"micro-incremento propio justo después de Inc-8: limpiar los campos de ficha al entrar al grafo y proteger los 6 guardados."* Closes `INC8-P3-SEC-F1` |
| Starting state | worktree branched from `feat/ui-next-batch-02` @ `3611c20`, clean |
| Isolation | `git worktree add %TEMP%\g6\wt -b g6-store-surrogates 3611c20`. Main tree (`C:\Users\<operator>\Github\mapper`) never touched — a separate agent was running the full lane against it |
| Commits | `1130d4c` (requirement + RED, xfail) → `c383d0a` (fix, xfail removed) |

---

## 1 · What changed

Added `A-111` (`01-requirements.md`, amendment set 19): ficha string fields — title, notes, meta,
state, schema field values, `document.tags`/`inherited` values, and attachment kind/path/caption —
are coerced against `darkside.plain()`'s rule at the two points they enter the in-memory graph:
`MapStore.load`'s sidecar parse, and every `mapper/app.py` mutation that assigns raw UI-sourced text
onto the graph. Every `store.save()` call site in `mapper/app.py` now degrades to a toast on any
exception instead of letting it escape.

> **CORRECTION (G6 corrective pass, `G6-C-F3`, see "Corrective pass" §8 below).** The sentence above
> is FALSE as written: `MapScreen.on_mount`'s `map_id == "new"` branch is an 8th `store.save()` call
> site in `mapper/app.py`, and it was NOT guarded by this increment. Left in place rather than edited
> — this note is the correction, not a rewrite of what this record originally claimed.

**`mapper/store.py`.** `_coerce_field`'s `str` branch (the one path every text position —
`Ficha`/`Attachment`/`Document`/`SchemaField` fields, `dict[str, str]` map keys/values, node ids —
funnels through) now returns `plain(value)` instead of `value` unchanged; the scalar-to-`str` branch
also routes through `plain()`. This widens `LLR-STO.1.1`'s existing type-coercion ladder, at its own
site, to additionally strip the code points `darkside.COERCION_RANGES` declares. No second table: `.
darkside.plain` is imported and reused.

**`mapper/app.py`.** Six call sites guarded with the exact pattern `action_save` already uses
(`try: self.store.save(...) / except Exception as e: self.notify(f"no se pudo guardar: {e}",
severity="error", markup=False); return`) — field commit, attachment add, attachment remove, undo
(`_pop_snapshot`), add-child, archive. Three of the six also coerce raw UI-sourced text with
`darkside.plain()` before it is assigned onto the graph, ahead of the guarded save: the field-commit
value (title/notes/state/field), the attachment-add path, and the add-child title (coerced before
`slugify`, too).

**`.dev-flow/BACKLOG.md`.** `B-67` given its own row for the first time (it existed only inline in
`HANDOFF-2026-09-24.md` and `state.json` before this), marked `~~B-67~~ **DONE**`: the paint/export
half was already closed at Inc-8 pass-3; this increment closes the persistence half.

## 2 · Files modified

- `mapper/store.py` — `_coerce_field` widened (1 import line + 2 changed lines).
- `mapper/app.py` — 6 call sites guarded, 3 of them also coerced at the mutation point.
- `tests/test_g6_store_surrogates.py` — new file, 3 RED arms (8 parametrized/individual nodes).
- `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md` — `A-111` appended (amendment set 19).
- `.dev-flow/BACKLOG.md` — `B-67` row added and closed.

**2 source files** (`mapper/store.py`, `mapper/app.py`) — within the batch's file cap. `darkside.py`
was not touched: `plain()` is already public and importable, so no export was needed.

## 3 · How to test

```bash
cd %TEMP%\g6\wt
python -c "import mapper; print(mapper.__file__)"   # confirms the editable install resolves here
python -m pytest tests/test_g6_store_surrogates.py -v
python -m pytest -q
python -m ruff check mapper tests
python -m pytest tests/test_no_operator_paths.py tests/test_fold.py -q
```

## 4 · Test results

### RED, before the fix (commit `1130d4c`, driven with `--runxfail` to see the real failure)

```
FAILED test_g6a_load_coerces_a_sidecar_lone_surrogate_title_instead_of_denying_the_map
  - mapper.store.MapStoreError: no se pudo indexar demo: UnicodeEncodeError
FAILED test_g6b_field_committed_with_a_surrogate_title_does_not_crash
  - UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 0: surrogates not allowed
    (raised inside mapper\app.py:3217 on_ficha_inspector_field_committed -> self.store.save(...),
    escaping the message handler and propagating out of app.run_test())
FAILED test_g6c_each_unguarded_save_site_degrades_to_a_toast[add_child]      - RuntimeError: boom (forced)
FAILED test_g6c_each_unguarded_save_site_degrades_to_a_toast[archive]       - RuntimeError: boom (forced)
FAILED test_g6c_each_unguarded_save_site_degrades_to_a_toast[attachment_add] - RuntimeError: boom (forced)
FAILED test_g6c_each_unguarded_save_site_degrades_to_a_toast[attachment_remove] - RuntimeError: boom (forced)
FAILED test_g6c_each_unguarded_save_site_degrades_to_a_toast[field_commit]   - RuntimeError: boom (forced)
FAILED test_g6c_each_unguarded_save_site_degrades_to_a_toast[undo]          - RuntimeError: boom (forced)

8 failed in 5.19s
```

All 8 reproduce the exact mechanism `INC8-P3-SEC-F1` names: arm (a) the typed `MapStoreError`
wrapping a `UnicodeEncodeError` from `_reindex`'s sqlite3 bind; arm (b) the same `UnicodeEncodeError`
this time uncaught, out of `_atomic_write`'s `Path.write_text(..., encoding="utf-8")`, escaping the
message handler; arm (c) the forced `RuntimeError` escaping uncaught at each of the 6 named call
sites in turn. None is a fixture artefact — each is the real production code path.

Recorded as `xfail(strict=True, reason="G6 fix pending")` at commit `1130d4c`, so the suite stayed
green with the defect live in the code.

### GREEN, after the fix (commit `c383d0a`, xfail markers removed)

```
tests/test_g6_store_surrogates.py: 8 passed in 3.25-3.40s
```

### Related suites (no regression)

```
tests/test_store.py tests/test_repair_store_boundary.py tests/test_inspector.py
tests/test_worklist_safety.py tests/test_app.py tests/test_g6_store_surrogates.py
150 passed in 19.00s
```

### Full default lane, once, after the fix

```
1308 passed, 20 deselected, 3 xfailed in 897.45s (0:14:57)
```

Reconciled by `--collect-only` (1311 collected, 20 deselected = 1331 total) against the diff: this
increment's only test-count change is the 8 new nodes in `tests/test_g6_store_surrogates.py` (no
other test file touched). `1308 passed + 3 xfailed = 1311` matches the collected count exactly, and
`1308 - 8 = 1300` reconciles against the batch's stated baseline ("about 1295+ passed, 0 failed" at
`3611c20`) within that stated margin. **0 failed.** The 3 xfailed are pre-existing and unrelated to
this increment. FLAKE-1
(`test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region`) was **not observed** this
run; FLAKE-2 candidate also not observed. Wall clock (~15 min) is this sandbox's own resource
ceiling — no test's own logic changed, and every prior increment in this batch that reports a wall
clock in this environment reports a similar multiple over the batch's original ~105 s measurement.

### `ruff check mapper tests`

```
Found 27 errors.
```

Matches the declared baseline (27) exactly — this increment introduces no new lint findings.

### Guards

```
tests/test_no_operator_paths.py: 2 passed
tests/test_fold.py: 19 passed, 3 xfailed
```

## 5 · Risks

- **The guard is generic, not surrogate-specific.** `except Exception` at each of the 6 sites catches
  *any* raise from `store.save()` — a full disk, a permissions error, or the coercion-related class
  this increment closes. That is the point (`INC8-P3-SEC-F1` asked for the sites to be guarded, not
  only the surrogate case), but it means a genuine bug inside `store.save()` for an unrelated reason
  now also degrades to a toast rather than surfacing as a crash during development. Existing
  precedent: `action_save` has done exactly this since before this batch.
- **No rollback of the in-memory mutation when a guarded save fails.** Stated in `A-111`'s "What is
  not claimed": the operator is told and the session keeps running; the mutation stays in memory
  until either a later save succeeds or `u` (undo) reverts it. This matches every other declined
  write in this codebase — there is no broader rollback mechanism to reuse.
  `tests/test_g6_store_surrogates.py`'s arm (c) asserts the toast and the surviving session; it does
  not assert a specific rollback behaviour, because none was specified.
  `mapper/app.py:_pop_snapshot`'s `self.graph`/`self.base_graph` are assigned to the restored graph
  *before* the guarded save — if that save fails, the in-memory undo still "succeeded" from the
  operator's point of view even though the disk state is stale until the next successful save. This
  is a pre-existing property of `_pop_snapshot`'s ordering, unchanged by this increment; carried as
  the item below rather than silently fixed.
- **`plain()` is idempotent but this fix calls it more than once on some values in the same
  request** (e.g. attachment-add coerces `target` once for the mutation and once again for the
  toast). Cosmetic — `plain()` replacing an already-clean or already-`\ufffd` string with itself
  costs one extra `translate()` pass, no behaviour change.

## 6 · Pending items

- **Carry, not fixed here:** `_pop_snapshot`'s `self.graph`/`self.base_graph` reassignment happens
  before the now-guarded `store.save()` call, so a failed undo-save still leaves the in-memory undo
  "applied." Out of `INC8-P3-SEC-F1`'s ask (guard the crash, not reorder the undo transaction) and
  not attempted here to keep the increment to its cut. Named `G6-F1` if a future pass wants it.
- `B-67` is now fully closed (both halves) — no further carry.

## 7 · Suggested next task

Inc-9 (key labels and screen headers moving to English) is next in the batch's own sequence; this
micro-increment does not touch that surface and does not block it.

---

## Mutant table

Harness kept **outside the repo**
(`%TEMP%\g6\mutate_harness.py`), one mutant per RED arm, each applied as a byte-level substitution in
the target file's own CRLF line endings, sha256-pinned before mutating, the pytest verdict printed
**before** restoring, and the pin re-checked after restore.

| # | Mutant | File | Targets arm | Result | pin before == after |
|---|---|---|---|---|---|
| 1 | `load-coercion` — revert `_coerce_field`'s `str` branch to `return value` (drop `plain()`) | `mapper/store.py` | (a) sidecar load | **KILLED** — `MapStoreError: no se pudo indexar demo: UnicodeEncodeError` | `cff031a4...` == `cff031a4...` |
| 2 | `mutation-coercion` — revert field-commit's `value = darkside.plain(event.value)` to `value = event.value` | `mapper/app.py` | (b) `FieldCommitted` mutation | **KILLED** — the reconstructed pytest AssertionError / uncaught `UnicodeEncodeError` path fires | `c1b472bf...` == `c1b472bf...` |
| 3 | `unguard-field_commit` — remove the `try`/`except` around field-commit's `store.save()` | `mapper/app.py` | (c)[field_commit] | **KILLED** — forced `RuntimeError` escapes uncaught | `c1b472bf...` == `c1b472bf...` |
| 4 | `unguard-attachment_add` — remove the `try`/`except` around attachment-add's `store.save()` | `mapper/app.py` | (c)[attachment_add] | **KILLED** | `c1b472bf...` == `c1b472bf...` |
| 5 | `unguard-attachment_remove` — remove the `try`/`except` around attachment-remove's `store.save()` | `mapper/app.py` | (c)[attachment_remove] | **KILLED** | `c1b472bf...` == `c1b472bf...` |
| 6 | `unguard-undo` — remove the `try`/`except` around `_pop_snapshot`'s `store.save()` | `mapper/app.py` | (c)[undo] | **KILLED** | `c1b472bf...` == `c1b472bf...` |
| 7 | `unguard-add_child` — remove the `try`/`except` around add-child's `store.save()` | `mapper/app.py` | (c)[add_child] | **KILLED** | `c1b472bf...` == `c1b472bf...` |
| 8 | `unguard-archive` — remove the `try`/`except` around archive's `store.save()` | `mapper/app.py` | (c)[archive] | **KILLED** | `c1b472bf...` == `c1b472bf...` |

**8 of 8 mutants killed.** Every pin matched before and after every mutation (full 64-hex sha256
recorded in the harness's own transcript, kept out of the repo). No negative control was run
separately: arms (a) and (b) already served as their own negative controls — the harness's baseline
(unmutated) run of every arm, captured in §4's GREEN section, is green precisely because the fix is
present and nothing else was touched.

---

## Corrective pass (2026-09-29, same day)

The independent security review returned **`BLOCK-UNTIL G6-C-F1, F2, F3, F8`** against `65621f3`
(this increment's own three commits), plus `G6-C-F4`/`F5`/`F6`/`F7` (medium/low). All eight are fixed
here. `G6-F1` (`_pop_snapshot` assigns before the guarded save) is carried, not fixed — unchanged
from §6 above.

| Finding | Severity | Disposition |
|---|---|---|
| `G6-C-F1` | HIGH | Fixed. `mapper/screens/factory.py::_persist` was reached from `action_edit_doc`/`action_import_office` with no guard at all. Routed through the new shared helper (see F2); `action_edit_doc`'s `EditorScreen` callback now coerces `Document.source`, and `action_import_office`'s `rel` (built from operator-typed path text) is coerced before it reaches the graph. |
| `G6-C-F2` | HIGH | Fixed. Every guard (the pre-existing one, this increment's six, `G6-C-F1`'s and `G6-C-F3`'s) interpolated `str(e)` into an operator-facing toast — an `OSError`'s own message embeds the full path and, on Windows, the account name, exactly the leak `B-30` already closed for `store.load` (`store.py` ~594-599). All eight now share one helper, `mapper/app.py::_save_or_toast`, whose toast names the map id and the exception TYPE only, both through `darkside.plain()`. Spanish wording unchanged (Inc-EN/`B-71` still owns translating it). |
| `G6-C-F3` | HIGH | Fixed, and this record's §1 corrected in place (a note appended above the false sentence, not a rewrite). `MapScreen.on_mount`'s `map_id == "new"` branch was an 8th, unguarded `store.save()` call site this increment's own "every ... call site" claim missed. Guarded via the shared helper. A census test (`ast`-derived, walks `mapper/` for every `store.save(`-shaped call and asserts each sits in the helper or a `try`) now guards the invariant going forward — it found exactly this site and `G6-C-F1`'s, unguarded, when run against `65621f3`. |
| `G6-C-F4` | MEDIUM | Fixed. `ImportPreviewScreen.action_save`'s "guardar como" name reached `store.save(name, ...)` uncoerced — the one mutation site `A-111`'s statement 1 missed. Coerced with `darkside.plain()` before the guarded save. |
| `G6-C-F5` | LOW | Fixed. `Edge.label`, set raw by `mermaid.parse` straight from the `.mmd` text, never passed through `A-111`'s ladder (scoped to sidecar text positions). Coerced at the same site, in `mermaid.parse` itself. |
| `G6-C-F6` | LOW | Fixed. An mmd-only ("orphan") node — the sidecar carries no entry for it at all — never entered `_graph_from_sidecar`'s per-node loop, so its `Ficha` (title set raw by `mermaid.parse`) skipped every coercion. A post-loop pass now coerces every node not already covered by the sidecar loop. |
| `G6-C-F7` | MEDIUM (regression this increment introduced) | Fixed. `plain()` maps `\r` (U+000D) to U+FFFD — correct at a paint sink, but this increment made `_coerce_field` call `plain()` on every LOADED string, so a note with real CRLF line endings (pasted on Windows) corrupted permanently on its first load, silently. `_coerce_field` now normalizes `\r\n`/`\r` to `\n` before calling `plain()`, at the storage-coercion boundary only; `plain()` itself is unchanged, so every paint call site keeps its U+FFFD behaviour. |
| `G6-C-F8` | HIGH (pre-existing, not introduced here) | Fixed, both halves. `save()` wrote `.mmd` then `_nodos.yml` as two independent atomic replaces; a failure between them left the pair torn, and the next `load()` rebuilt from the stale sidecar with no warning, reverting the edit silently. (a) `save()` now writes both temp files before either replace. (b) `save()` stamps the sidecar with a fingerprint of the paired `.mmd` text (`_mmd_hash`, reusing `_text_hash` rather than a second hash routine); `load()` compares it against the `.mmd` actually on disk and appends a `load_warning` naming the map (no path) on a mismatch. Residual window recorded in `.dev-flow/BACKLOG.md`. |
| `G6-F1` | — | Carried, not fixed (unchanged from §6 above; out of this pass's fence). |

### Commits

- `943e808` — `G6-C-F1`/`F2`/`F3`/`F4`: shared `_save_or_toast` helper, guard the 8th call site,
  coerce the "guardar como" name. Touches `mapper/app.py`, `mapper/screens/factory.py`, and 5 of the
  12 new test arms (F1, F2, F3×2, F4).
- `3db2216` — `G6-C-F5`/`F6`: coerce `Edge.label` and mmd-only orphan node fichas. Touches
  `mapper/mermaid.py`, one hunk of `mapper/store.py` (the post-loop coercion), and 2 more arms.
- `6c205d6` — `G6-C-F7`/`F8`: CRLF regression fix and the two-phase write + mismatch check. Touches
  the remaining hunks of `mapper/store.py`, and the last 5 arms.

Consolidated from the requested seven-point sequence (F2+F3, then F1, F4, F7, F8, then F5/F6, then
docs) into three code commits plus this docs commit: `app.py`'s diff interleaves F2 (the helper),
F3 (the 8th site) and F4 (the name coercion) inside the same few functions closely enough that a
clean per-finding split would have meant hand-editing hunks rather than a real `git add -p`
boundary, and `F1` depends on `F2`'s helper existing in `mapper/app.py` to import — landing it in a
separate, earlier commit would leave that commit non-self-contained. `F5`/`F6` and `F7`/`F8` DID
split cleanly along real `git add -p` hunk boundaries in `mapper/store.py` and were split. Declared
here rather than claimed as the full seven-commit sequence.

### RED-before evidence

All 12 new arms were run against `65621f3` (source files reverted via `git stash`, keeping only the
new test file) before any fix landed:

```
FAILED test_g6c_f1_factory_persist_degrades_to_a_toast_and_survives - RuntimeError: boom (forced)
FAILED test_g6c_f2_save_failure_toast_names_no_path_or_username - AssertionError: the toast leaked a path
FAILED test_g6c_f3_new_map_on_mount_save_degrades_to_a_toast - RuntimeError: boom (forced)
FAILED test_g6c_f3_census_every_store_save_call_is_guarded - AssertionError: unguarded store.save()
  call sites: ['mapper\\app.py:1468', 'mapper\\screens\\factory.py:153']
FAILED test_g6c_f4_guardar_como_name_with_lone_surrogate_saves_cleanly - AssertionError: crashed
FAILED test_g6c_f5_edge_label_is_coerced - AssertionError: '\u200e' not in 'nota\u200e'
FAILED test_g6c_f6_mmd_only_orphan_node_ficha_is_coerced - AssertionError: '\u200e' not in 'orph\u200ean'
FAILED test_g6c_f7_crlf_notes_round_trip_as_lf_with_no_replacement_char - assert 'line1\ufffd\nline2' == ...
FAILED test_g6c_f7_lone_cr_round_trips_as_lf - assert 'a\ufffdb' == 'a\nb'
FAILED test_g6c_f8a_two_phase_write_leaves_both_files_unchanged_on_temp_failure - the .mmd file was torn
FAILED test_g6c_f8b_failure_between_replaces_is_warned_on_next_load - no mismatch warning: []

11 failed, 9 passed in 6.10s
```

(11 failed, not 12: `test_g6c_f7_tab_cjk_emoji_round_trip_byte_identical`, the negative control, was
already green against `65621f3` — it asserts nothing the fix changes.) The census's own failure list
is the exact defect population: `mapper\app.py:1468` (`G6-C-F3`) and `mapper\screens\factory.py:153`
(`G6-C-F1`), not a fixture artefact.

After the fix (working tree restored via `git stash pop`): `tests/test_g6_store_surrogates.py`, all
20 arms (8 original + 12 corrective), pass. Related suites unaffected:

```
tests/test_store.py tests/test_repair_store_boundary.py tests/test_inspector.py
tests/test_worklist_safety.py tests/test_app.py tests/test_repair_depth.py
tests/test_g6_store_surrogates.py
238 passed, 15 deselected in 33.51s
```

### Mutant table, corrective pass

Harness kept **outside the repo** (`%TEMP%\g6c\mutate_harness.py`), one mutant per RED arm (or per
group of arms a single code change kills), each a byte-level substitution in the target file's own
CRLF line endings, sha256-pinned before mutating, the pytest verdict printed **before** restoring,
the pin re-checked after restore.

| # | Mutant | File | Targets | Result | pin before == after |
|---|---|---|---|---|---|
| 1 | `F1-unguard-factory-persist` — revert `_persist` to a raw `store.save(...)` call | `mapper/screens/factory.py` | `G6-C-F1` | **KILLED** | `11b55214...` == `11b55214...` |
| 2 | `F2-leak-str-e-in-toast` — revert `_save_or_toast`'s toast to `f"no se pudo guardar: {e}"` | `mapper/app.py` | `G6-C-F2` | **KILLED** | `d9b48236...` == `d9b48236...` |
| 3 | `F3-unguard-new-map-site` — revert the 8th call site to a raw `self.store.save(...)` | `mapper/app.py` | `G6-C-F3` (both the pilot arm and the census) | **KILLED** (2 tests) | `d9b48236...` == `d9b48236...` |
| 4 | `F4-drop-name-coercion` — drop `name = darkside.plain(name)` in `action_save` | `mapper/app.py` | `G6-C-F4` | **KILLED** | `d9b48236...` == `d9b48236...` |
| 5 | `F5-drop-edge-label-coercion` — drop `plain()` around the edge label | `mapper/mermaid.py` | `G6-C-F5` | **KILLED** | `5c3c0c6b...` == `5c3c0c6b...` |
| 6 | `F6-drop-orphan-node-coercion` — drop the post-loop coercion pass | `mapper/store.py` | `G6-C-F6` | **KILLED** | `aa3b72b9...` == `aa3b72b9...` |
| 7 | `F7-drop-newline-normalization` — revert `_coerce_field` to call `plain()` with no normalization | `mapper/store.py` | `G6-C-F7` (both CRLF and lone-CR arms) | **KILLED** (2 tests) | `aa3b72b9...` == `aa3b72b9...` |
| 8 | `F8a-single-phase-write` — revert `save()` to write-then-immediately-replace per file | `mapper/store.py` | `G6-C-F8`(a) | **KILLED** | `aa3b72b9...` == `aa3b72b9...` |
| 9 | `F8b-drop-mismatch-check` — drop the `_mmd_hash` comparison in `load()` | `mapper/store.py` | `G6-C-F8`(b) | **KILLED** | `aa3b72b9...` == `aa3b72b9...` |

**9 mutants, 11 arms killed (8 mutants map 1:1, 2 mutants each kill a pair of arms), 0 survivors.**
Every pin matched before and after every mutation (full 64-hex sha256 in the harness's own
transcript, kept out of the repo). The 12th arm (`test_g6c_f7_tab_cjk_emoji_round_trip_byte_identical`)
is its own negative control, same role as arms (a)/(b) in the original mutant table above.

### Lane, ruff, guards (corrective pass)

```bash
cd C:\Users\<operator>\Github\mapper
python -m pytest tests/test_g6_store_surrogates.py -v          # 20 passed
python -m pytest -q                                             # full lane, see below
python -m ruff check mapper tests
python -m pytest tests/test_no_operator_paths.py tests/test_fold.py -q
```

**Full default lane, once, after the corrective pass:**

```
1320 passed, 20 deselected, 3 xfailed in 967.37s (0:16:07)
```

Reconciled against the batch's stated baseline at `65621f3` (**1308 passed, 20 deselected, 3
xfailed, 0 failed**): this pass adds exactly 12 new nodes (`tests/test_g6_store_surrogates.py`'s
`test_g6c_*` functions) and touches no other test file, so `1308 + 12 = 1320` reconciles exactly, not
approximately. **0 failed.** Neither `FLAKE-1`
(`test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region`) nor the `FLAKE-2` candidate
(`test_hlr_n16_4_legend_declares_its_own_keys[size2]`) fired in this run (absent from the log).

**A first full-lane run, before this run, caught a real defect in this record itself.** The first
pass (`1318 passed, 2 failed` — everything else identical) failed
`tests/test_no_operator_paths.py::test_a110_no_undeclared_user_profile_path_in_any_tracked_file` and
`::test_a110_the_real_operator_username_appears_nowhere`, both against this very file: an earlier
draft of the "How to test" block above wrote the real account name in a `cd` line instead of
`<operator>`. Fixed in place (the line now reads `cd C:\Users\<operator>\Github\mapper`, above) and
the guard re-run clean (`2 passed`) before this second, reported full-lane run. Left in the record
rather than quietly corrected, per this pass's own discipline about not hiding what happened.

**`ruff check mapper tests`:** `Found 27 errors` — matches the declared baseline exactly (all
pre-existing; the corrective pass's own files, checked in isolation, add zero new findings).

**Guards, final:**

```
tests/test_no_operator_paths.py: 2 passed
tests/test_fold.py: 19 passed, 3 xfailed
```

## Traceability

- `A-111` (`01-requirements.md`, amendment set 19) — the requirement this increment discharges.
- `INC8-P3-SEC-F1` — the finding this increment closes (Inc-8 pass-3 security review,
  `.dev-flow/state.json` → `p3_progress.INC-8_ROUND_4_2026-09-29.pass_3_reviews.security`).
- `VERDICT-inc8-legend-2026-09-28.md` § Round 4, `G6` — the operator authority.
- `LLR-STO.1.1` (external, `.dev-flow/2026-08-27-repair-batch-02/01-requirements.md:114`) — widened,
  not redefined.
- `HLR-COERCE` / `LLR-COERCE.1` (this batch, `01-requirements.md` §3.0) — the coercion table reused.
- `.dev-flow/BACKLOG.md` `B-67` — both halves now closed.
- `A-111`'s appended note (`01-requirements.md`) — the corrective pass's own requirement-level record,
  including the `G6-C-F3` correction of this document's §1 false claim.
- `G6-C-F1`..`F8` — the independent security review's findings this corrective pass closes
  (`BLOCK-UNTIL G6-C-F1, F2, F3, F8`, plus `F4`/`F5`/`F6`/`F7`).
- `G6-F1` — carried, not fixed (unchanged).
- Commits `943e808`, `3db2216`, `6c205d6` — the corrective pass itself.
