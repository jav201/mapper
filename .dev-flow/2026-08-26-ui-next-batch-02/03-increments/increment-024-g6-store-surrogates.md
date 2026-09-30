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

## Traceability

- `A-111` (`01-requirements.md`, amendment set 19) — the requirement this increment discharges.
- `INC8-P3-SEC-F1` — the finding this increment closes (Inc-8 pass-3 security review,
  `.dev-flow/state.json` → `p3_progress.INC-8_ROUND_4_2026-09-29.pass_3_reviews.security`).
- `VERDICT-inc8-legend-2026-09-28.md` § Round 4, `G6` — the operator authority.
- `LLR-STO.1.1` (external, `.dev-flow/2026-08-27-repair-batch-02/01-requirements.md:114`) — widened,
  not redefined.
- `HLR-COERCE` / `LLR-COERCE.1` (this batch, `01-requirements.md` §3.0) — the coercion table reused.
- `.dev-flow/BACKLOG.md` `B-67` — both halves now closed.
