# Increment 008 — DDR follow-up (DDRFIX-A, CODE lane) · reqharness hardening + architecture

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `008` (DDRFIX-A) |
| Lane | CODE lane (this unit); the documents lane edits only `01-requirements*.md`, the PDR, `docs/ARCHITECTURE.md`, `.dev-flow/BACKLOG.md`, `REQUIREMENTS.md` and increment packets 003/005/006/007 — none of them touched here |
| Requirement(s) | DDR follow-up rulings: SEC F1/F2/F3/F4/F5 · QA C1/C2/C3/C4 · ARCH C3/C5 |
| Acceptance | the new layer-0 nodes below, RED-proven per fix, plus the unchanged batch verification slice |
| Agent | `kimi-code` (Kimi, CODE lane worker) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: twelve rulings from the DDR follow-up are discharged in the four
allowed source files.  Security: the audit report now escapes every
registry-derived value (F1), a linear nesting pre-scan bounds parser work
(F2), the pending write confines-then-creates (F3), the roles.yml append
is lock-serialized and repairs a missing trailing newline (F4), and the
chain walk enforces approver != requester on pending-derived events (F5).
QA: `--audit` on a registry-less repo names the state `no registry yet`
(C1), the M-FR3/M-FR4/M-LM1 mutants are executed RED (C2), the 077c
source census gains a positive-presence arm (C3), and the LLR-RH.4.5 /
LLR-RH.5.2 traceability tags land (C4).  Architecture: the
`chain`↔`pending` import cycle is broken by moving the shared pieces into
`config.py` (C3-ARCH), and `audit.py` calls the public `osopen.is_link`
instead of `baseline._is_link` (C5).

Mechanism, per ruling:

- **SEC F1 — `audit.render` escaping.** `_visible()` escapes C0 + C1
  controls, ESC, DEL and CR/LF to `\xNN` spellings and is applied at
  EVERY interpolation in `render` (repo, chain status, per-state ids,
  warnings, reported lines, baseline names, deleted reviews, verdict) —
  one helper, every value, so a crafted object id / reviewer id / file
  name can neither inject a terminal escape nor forge a second
  `verdict:` line.
- **SEC F2 — nesting pre-scan.** `_check_nesting` runs in
  `config.load_documents` before `yaml.parse`: one linear pass tracking
  flow-collection depth (`[`/`{` outside quoted scalars, `#` comments
  honoured) and block-indentation depth, refusing depth > 64
  (`LIMIT_NESTING_DEPTH`) with the named `ValidationError`
  `nesting too deep`.  64 KB of `[` is refused in milliseconds; the
  parser-side RecursionError/ValueError ladder stays as the backstop
  (the `test_input_limits_reported_by_name` deep-nesting arms now assert
  the earlier, named refusal).
- **SEC F3 — pending confine-then-create.** `_write_pending` resolves the
  content-derived name through the one containment rule
  (`_confine`/`confine_reason`) BEFORE any write, then mkdir + exclusive
  create — exactly `reviews.record_review`'s shape.  A link/junction at
  `reqharness/pending` (or any parent component) is refused by name and
  nothing reaches through it.
- **SEC F4 — append lock + newline repair.** `_append_body` takes
  `reqharness/.roles.lock` (`O_CREAT|O_EXCL`, removed in `finally`); a
  present lock is a named refusal and is never deleted silently.  Under
  the lock the bound head is re-verified (a moved head refuses, never
  appends stale; the `resolve` path re-checks the chosen child is still a
  fork child), and a roles.yml whose last byte is not `\n` is repaired
  with a prepended newline so the new `---` document can never glue onto
  the previous line.
- **SEC F5 — requester-approver walk rule.** `_passes_approval` refuses a
  `grant`/`revoke` carrying `request_hash` whose `approved_by` equals the
  event's `requested_by` — the `approve_pending` API check is the first
  line; this is the chain-walk backstop for hand-crafted events, and it
  also makes such a fork child never-approvable, so a `resolve` naming it
  fails verify `chain broken` (R27 arm).
- **QA C1 — no-registry state.** `audit()` returns the named report
  `chain: no registry yet` / `verdict: not ready · no registry yet` (exit
  1) when the toplevel has no `reqharness/` directory at all — not the
  alarming `chain broken` (nothing is broken; nothing was created).
- **ARCH C3 — cycle break.** `config.py` (leaf) now owns `PENDING_DIR`,
  the confined event-file reader (`_confine`/`_read_text`/
  `read_event_file`), the event-name regex (`EVENT_NAME_RE`) and the
  pending schema + loader (`PendingRequest`, `validate_pending_document`,
  `load_pending`).  `chain` imports `load_pending` from `config` at
  MODULE level (the function-local import is gone); `pending` imports the
  shared pieces from `config` and holds only a `TYPE_CHECKING` import of
  `ChainReport`.  New AST census: no reqharness module imports a module
  that imports it back, at any scope.
- **ARCH C5 — public link helper.** `audit._confine_repo` calls
  `mapper.osopen.is_link` (public) instead of `baseline._is_link`
  (private); the osopen-import census allowlist gains the two new rows
  (`reqharness/audit.py` → `is_link`, `reqharness/config.py` →
  `confine_reason`) and drops chain.py's (its edge moved into the leaf).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/audit.py` | source | SEC F1 · QA C1 · ARCH C5 | `_visible` escaping at every `render` interpolation; `NO_REGISTRY`/`_no_registry_report`; `osopen.is_link` replaces `baseline._is_link` |
| `mapper/reqharness/config.py` | source | SEC F2 · ARCH C3 | `_check_nesting` + `LIMIT_NESTING_DEPTH` in `load_documents`; `PENDING_DIR`, `EVENT_NAME_RE`, the confined reader, `PendingRequest`/`validate_pending_document`/`load_pending` moved down from `chain`/`pending` |
| `mapper/reqharness/chain.py` | source | SEC F3 · SEC F4 · SEC F5 · ARCH C3 | `_write_pending` confine-then-create; `_append_body` lock + head re-verify + newline repair; `_passes_approval` requester-approver arm; module-level `load_pending` import; the lazy `_pending_request` wrapper is gone |
| `mapper/reqharness/pending.py` | source | ARCH C3 | the read side: re-exports the shared validator from `config`; `ChainReport` becomes a `TYPE_CHECKING` import; `list_pending`/`resolution` unchanged in behaviour |
| `tests/test_reqharness_chain.py` | test | SEC F2/F3/F4/F5 · QA C2/C4 | 3 new nodes (pending-link refusal; append lock + newline repair; requester-approver walk rule); the deep-nesting arms assert the pre-scan refusal; LLR-RH.4.5 tag on `test_head_binding_unknown_head_not_verifiable` |
| `tests/test_reqharness_config.py` | test | SEC F2 | `test_nesting_event_stream_refuses_superlinear_depth` (the DDRFIX-C rename; §8's historical text stands) (64 KB `[` refused by name < 2 s; depth-10 document loads) |
| `tests/test_reqharness_modgraph.py` | test (new) | ARCH C3 | the AST back-import census + a planted function-local back-import negative control |
| `tests/test_reqharness_release.py` | test | SEC F1 · QA C1/C2/C4 | `test_audit_render_escapes_registry_derived_text` (real console entry); `test_audit_cli_names_no_registry_state` (real console entry); the LLR-RH.5.2 retired-exclusion arm inside `test_release_rules_and_verdicts` |
| `tests/test_roles_screen.py` | test | QA C3 · SEC F5 | the 077c census gains the positive-presence arm (glyph constants defined + Text sinks exist); the crafted double-resolution fixture's event now has approver != requester (the shape SEC F5 mandates) |
| `tests/test_arch_osopen_callers.py` | test (census allowlist) | ARCH C5 | osopen allowlist rows: `audit.py`/`config.py` in, `chain.py` out |
| `.dev-flow/2026-10-11-reqharness-batch/evidence/ddrfix-red.driver.sh` + `ddrfix-red.transcript` | evidence | RED proof | the 12-arm driver and its verbatim output |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** (`audit.py`, `config.py`, `chain.py`, `pending.py`) |
| Test files | 5 modified + 1 new (uncapped) |
| Doc files | 0 — no document-lane file touched |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py tests/test_roles_screen.py tests/test_app.py tests/test_no_operator_paths.py tests/test_arch_osopen_callers.py tests/test_mod_deps.py
ruff check mapper/reqharness
```

(The unit's verification command; `NO_COLOR` unset for the run.)

## 4 · Test results

### GREEN — executed now, from the worktree root

```text
$ python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py tests/test_roles_screen.py tests/test_app.py tests/test_no_operator_paths.py tests/test_arch_osopen_callers.py tests/test_mod_deps.py
129 passed
$ ruff check mapper/reqharness
All checks passed!
```

New nodes in this increment:

- `tests/test_reqharness_chain.py::test_pending_write_refuses_link_and_writes_nothing_outside`
- `tests/test_reqharness_chain.py::test_roles_append_lock_repairs_newline_and_refuses_stale_lock`
- `tests/test_reqharness_chain.py::test_request_resolving_event_needs_alien_approver`
- `tests/test_reqharness_config.py::test_nesting_event_stream_refuses_superlinear_depth`
- `tests/test_reqharness_modgraph.py::test_no_reqharness_module_imports_a_module_that_imports_it_back`
- `tests/test_reqharness_modgraph.py::test_the_census_catches_a_planted_function_local_back_import`
- `tests/test_reqharness_release.py::test_audit_render_escapes_registry_derived_text`
- `tests/test_reqharness_release.py::test_audit_cli_names_no_registry_state`

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | 12 arms: M-F1, M-F2, M-F3, M-F4a, M-F4b, M-F5, M-C1, M-C3, M-C5 (the new fixes) + M-FR3, M-FR4, M-LM1 (the QA C2 mandated mutants) |
| Instrument | `.dev-flow/2026-10-11-reqharness-batch/evidence/ddrfix-red.driver.sh`; restore checked by sha256 per arm |
| Where it ran | **this worktree** (the batch trunk) |
| Transcript | `.dev-flow/2026-10-11-reqharness-batch/evidence/ddrfix-red.transcript` |
| Restore proven by | **file hash returned to its pre-mutation value** (sha256 before == after, printed per arm) |
| Bytecode cache | `-B` / `PYTHONDONTWRITEBYTECODE=1` on every run |
| Arms resolved at baseline | **12 / 12 — every arm RED on mutation and GREEN after restore** |
| Verdict granularity | per node id, printed per arm |

| Arm | Node it reddened | Restore (sha256 before == after) |
|---|---|---|
| M-F1 (`_visible` escapes nothing) | `test_audit_render_escapes_registry_derived_text` | byte-identical → GREEN |
| M-F2 (pre-scan a no-op) | `test_nesting_event_stream_refuses_superlinear_depth` (the DDRFIX-C rename; §8's historical text stands) | byte-identical → GREEN |
| M-F3 (pending write unconfined) | `test_pending_write_refuses_link_and_writes_nothing_outside` | byte-identical → GREEN |
| M-F4a (newline repair disabled) | `test_roles_append_lock_repairs_newline_and_refuses_stale_lock` | byte-identical → GREEN |
| M-F4b (lock not exclusive) | `test_roles_append_lock_repairs_newline_and_refuses_stale_lock` | byte-identical → GREEN |
| M-F5 (requester-approver arm removed) | `test_request_resolving_event_needs_alien_approver` | byte-identical → GREEN |
| M-C1 (no-registry state removed) | `test_audit_cli_names_no_registry_state` | byte-identical → GREEN |
| M-C3 (chain↔pending back-edge restored) | `test_no_reqharness_module_imports_a_module_that_imports_it_back` | byte-identical → GREEN |
| M-C5 (private `_is_link` restored) | `test_outside_app_only_the_allowed_names_are_imported_from_osopen` | byte-identical → GREEN |
| M-FR3 (walk by file position) | `test_verify_walks_by_prev_hash_in_order_fork_resolve` | byte-identical → GREEN |
| M-FR4 (resolve legitimizes an unapprovable child) | `test_resolve_chosen_child_must_pass_approval_rule` | byte-identical → GREEN |
| M-LM1 (size limit skipped) | `test_input_limits_reported_by_name` | byte-identical → GREEN |

QA C3 (positive presence) and QA C4 (tags) are test-only arms — no product
change exists to revert; C3's anti-vacuity is demonstrated by the census
failing on a gutted module (the `assigned`/`text_sinks` asserts), and C4's
retired arm is itself the new fixture.  Full per-arm commands, outputs and
restore digests: the transcript.

### Conditions this increment discharges

| Condition (DDR ruling) | Where discharged |
|---|---|
| SEC F1 — terminal escape / verdict spoofing via registry-derived text | `_visible` + the render census-by-construction + M-F1 |
| SEC F2 — superlinear parse on deep nesting | `_check_nesting` + M-F2 |
| SEC F3 — pending write through a link | confine-then-create + M-F3 |
| SEC F4 — append race + missing trailing newline | the lock, the under-lock head re-verify, the newline repair + M-F4a/M-F4b |
| SEC F5 — requester approves their own pending request | `_passes_approval` + M-F5 (both the head-append and the fork-resolve arms) |
| QA C1 — `--audit` with no registry names its state | `_no_registry_report` + M-C1 (real console entry) |
| QA C2 — M-FR3 / M-FR4 / M-LM1 executed RED | the three arms in the table above |
| QA C3 — 077c census positive presence | the `assigned` + `text_sinks` asserts |
| QA C4 — LLR-RH.4.5 / LLR-RH.5.2 tags | the docstring tag and the retired-exclusion arm |
| ARCH C3 — chain↔pending import cycle | the config.py leaf + module-level import + the AST census + M-C3 |
| ARCH C5 — no private `baseline._is_link` call | `osopen.is_link` + the census allowlist row + M-C5 |

### Residuals (stated, not fixed)

- The append lock is advisory within one machine (no cross-host atomicity);
  a writer with repo access can still rewrite chain + reviews consistently
  (layer 3 — B-122 strong mode remains the answer).
- The nesting pre-scan counts YAML-source depth, not parser recursion per
  se; the parser-side ladder stays as the backstop for shapes the scan
  under-counts (none known at depth ≤ 64).
- The lock file appears transiently under `reqharness/`; the audit's
  confinement sweep tolerates it (regular file, inside the toplevel) and
  every append removes it in `finally`.

## 5 · Risks

- The F4 fixture revokes the reviewer's role via the normal propose path;
  wall-clock chain times in screen tests postdate the seeded events by
  construction (the pre-existing `T_LATE` pattern) — unaffected here.
- `pending.py` re-exports `PENDING_DIR`/`PendingRequest`/`load_pending`
  from `config`; external imports of those names keep working unchanged.

## 6 · Pending items / spec deviations

- One pre-existing fixture needed a semantic repair inside the mandated
  test surface: `test_rh6b_double_resolution_refusal_is_named` crafts a
  chain event referencing a pending digest with
  `requested_by == approved_by` — exactly the shape SEC F5 now refuses.
  The fixture's intent (a chain reference that does not apply the request)
  is preserved with `requested_by="reviewer-2"`, `approved_by="subject"`,
  which is what a real approval event records.
- `test_input_limits_reported_by_name`'s deep-nesting arms now assert the
  EARLIER named refusal (`nesting too deep`, SEC F2) instead of the
  parser-side `malformed YAML`; the parser-side ladder stays covered by
  the huge-scalar ValueError arm.

## 7 · Suggested next task

Batch close-out: the documents lane finishes 003/005/006/007; P4
measurements land in `04-validation.md`.

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 4/4 — `audit.py`, `config.py`, `chain.py`, `pending.py` |
| 2 | Tests written in this same increment | ✓ | 8 new nodes + 2 census/allowlist updates |
| 3 | Layer 0 written where the criterion applies | ✓ | §4 |
| 4 | RED counterfactual declared | ✓ | 12 arms, transcript + per-arm restore digests |
| 5 | Security conditions discharged mapped to findings | ✓ | F1–F5 table, §4 |
| 6 | `code-reviewer` passed | ⚠ | PENDING — orchestrator's review unit |
| 7 | No file from another lane touched | ✓ | git status: only the 4 source + 5 test files + this packet + evidence |
| 8 | Frozen interfaces untouched | ✓ | no keymap/seat/screen-surface edit; screen tests untouched except the two mandated arms |
| 9 | Coverage claims verified on disk | ✓ | GREEN lines from runs executed now |
| 10 | Residuals stated honestly | ✓ | §4 |
| 11 | Evidence files declared | ✓ | §8 |
| 12 | Independent review names somebody | ⚠ | PENDING |

## 8 · Evidence files — bytes at a declared home, verbatim, hash-verified

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED-proof transcript (12 arms, commands + outputs + restore digests) | `.dev-flow/2026-10-11-reqharness-batch/evidence/ddrfix-red.transcript` | `b3b0fba73fa28ff41e55815499bf36f58eba3aef82bc0fc0a0a58dba1084bbe0` |
| RED-proof driver (the instrument) | `.dev-flow/2026-10-11-reqharness-batch/evidence/ddrfix-red.driver.sh` | `f0afef5c72fecd75a13965fbd85fb2d9ede6b97fb25b2664216655577762f302` |

---

## 9 · Security re-verification follow-up (DDRFIX-C)

Opus re-check of 5492378 re-opened F2 (HIGH) and two F1 nits; this section
discharges them.  SOURCE touched: `mapper/reqharness/config.py` (F2),
`mapper/reqharness/audit.py` (F1 nits); tests in
`tests/test_reqharness_config.py` / `tests/test_reqharness_release.py`.

- **SEC F2 (HIGH) — the lexical pre-scan was bypassable; the event stream is
  now the authoritative bound.**  `_check_nesting` is DELETED.  The depth
  count moved into the `yaml.parse` pass that already refuses anchors/aliases:
  `SequenceStartEvent`/`MappingStartEvent` add 1, their End events subtract 1,
  and the named `ValidationError("… nesting too deep …")` raises the moment
  depth exceeds `LIMIT_NESTING_DEPTH` (64) — BEFORE compose/construct, so the
  C composer never sees a deeper structure.  Every bypass shape is refused:
  a plain-scalar apostrophe (`n: it's`, `x#'`, `say "hi`) that swallowed the
  rest of the file into "quote state", compact block sequences (`- - - …`),
  complex keys (`? ? ? …`), a genuinely deep block nest behind an apostrophe
  line, mixed flow/block trees, and the multi-MB `[` flood.  The event
  iteration is linear and non-recursive by construction (the C parser is an
  explicit state machine; no per-level recursion), measured below: every
  refusal lands in ~1 ms because it fires after ~65 events, not after
  megabytes of parsing.
- **SEC F1 nit (MED) — the refusal path printed `audit: {exc}` raw.**
  `run_cli` now routes the named-refusal line through `_visible` like every
  other line the CLI writes; a control/bidi char in the operator's repo
  argument paints as its visible spelling on stderr.
- **SEC F1 nit (MED/LOW) — the escaper now covers Unicode Cc, Cf (bidi
  overrides U+202A–U+202E / U+2066–U+2069, zero-width U+200B–U+200F /
  U+2060 / U+FEFF) and Zl/Zp (U+2028 / U+2029).**  C0/C1/DEL keep their
  `\xNN` spellings; the added categories paint as `\uXXXX`.  A reviewer id
  carrying U+2028 can no longer forge a second `verdict:` line via
  `str.splitlines()`.
- **SEC F5 (LOW) — residual arm taken, no code change.**  `requested_by` on
  a resolving event is a label, not an authority: approval power comes from
  `approved_by` holding admin at the event's bound head, and this batch's
  walk rule already refuses a request-derived event whose approver equals its
  requester.  The event's `request_hash` binds the pending document's
  canonical digest — the true requester is inside the hashed content, so a
  mismatched `requested_by` is detectable by recomputation and grants
  nothing.  A walk-time equality check was rejected because the pending
  file's presence is a convention (R6 keeps it, nothing enforces it): with
  the file deleted the check would fail OPEN and give false assurance, and
  making chain status depend on mutable pending-dir state would break the
  walk's determinism on roles.yml + config alone.  As the ruling itself
  notes, a requester who later holds admin can grant directly — the label
  never gates anything.  Recorded here as a stated residual (R23).

New nodes (all RED-proven below):

- `tests/test_reqharness_config.py::test_nesting_event_stream_refuses_superlinear_depth`
  (renamed at DDRFIX-C from `test_nesting_prescan_refuses_superlinear_depth`; §8's historical citations of the old name stand) — same arms,
  the mechanism under test changed; §8's historical citations stand)
- `tests/test_reqharness_config.py::test_nesting_event_stream_refuses_lexically_bypassed_shapes`
- `tests/test_reqharness_config.py::test_nesting_event_stream_boundary_and_quoted_scalars`
- `tests/test_reqharness_release.py::test_audit_cli_refusal_line_escapes_control_text`
- `tests/test_reqharness_release.py::test_audit_render_escapes_bidi_and_separator_text`

### Timing table (input → size → result → seconds, in-process, this machine)

| Input | Size (bytes) | Result | Seconds |
|---|---|---|---|
| `n: it's` + 64 KB `[` flow flood | 65,547 | refused `nesting too deep` | 0.001 |
| `x#'` + 64 KB `[` flow flood | 65,546 | refused `nesting too deep` | 0.001 |
| `say "hi` + 64 KB `[` flow flood | 65,550 | refused `nesting too deep` | 0.001 |
| `- - - …` compact sequence, 1,000 deep | 3,000 | refused `nesting too deep` | 0.000 |
| `? ? ? …` complex keys, 1,000 deep | 3,000 | refused `nesting too deep` | 0.000 |
| apostrophe + 1,024-deep block nest | 1,055,674 | refused `nesting too deep` | 0.000 |
| mixed flow/block tree, 200 deep | 40,893 | refused `nesting too deep` | 0.000 |
| 4 MB `[` flow flood (`roles.yml` where) | 4,194,308 | refused `nesting too deep` | 0.001 |
| depth-64 flow document (positive) | 131 | loaded | 0.000 |
| depth-65 flow document (boundary) | 133 | refused `nesting too deep` | 0.000 |
| 63 KB of brackets inside a quoted scalar (positive) | 64,518 | loaded | 0.001 |

(The 8 attack arms also run in a SUBPROCESS in the test node — a C-stack
crash would surface as a non-zero/negative exit code there, never kill
pytest — each < 2 s including interpreter startup.)

### RED counterfactual (3 arms — executed, not predicted)

| Arm | Reverted | Node reddened | Restore (sha256 before == after) |
|---|---|---|---|
| F2 event-stream depth check | `config.py` → pre-fix snapshot | `test_nesting_event_stream_refuses_lexically_bypassed_shapes` (1 failed / 1 passed — the pre-fix loader answers `malformed YAML`, not the named refusal, on the bypass shapes) | byte-identical → GREEN |
| F1a refusal-path escaper | `audit.py` → pre-fix snapshot | `test_audit_cli_refusal_line_escapes_control_text` | byte-identical → GREEN |
| F1b extended `_visible` | `audit.py` → pre-fix snapshot | `test_audit_render_escapes_bidi_and_separator_text` + `test_audit_cli_refusal_line_escapes_control_text` (2 failed) | byte-identical → GREEN |

Transcript (commands + outputs + restore digests, paths sanitized):
`.dev-flow/2026-10-11-reqharness-batch/evidence/ddrfix-c-red.transcript` —
SHA-256 `b8dee296b37ebfadd553a4fd65b7dbb9c446de068b7eda5b13505ac5f94bd1be`.
F5 is the residual arm — no product change exists to revert; its
discharge is the stated reasoning above.

### Verification (this follow-up)

```text
$ env -u NO_COLOR python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py tests/test_roles_screen.py tests/test_app.py tests/test_no_operator_paths.py
115 passed, 1 warning in 52.96s
$ ruff check mapper/reqharness
All checks passed!
```

---

## Security nits (K3 re-check) — close-out, appended 2026-10-11

The independent security re-check (Kimi K3) returned CLEARED-WITH-NITS.
Four LOW findings, discharged here:

- **LOW-1 — the depth refusal surfaced double-prefixed.**  The SEC F2
  `nesting too deep` refusal is a `ValidationError`, and `ValidationError`
  subclasses `ValueError` — so the `except (yaml.YAMLError, ValueError,
  RecursionError)` clause in `load_documents` re-wrapped it as
  `<where>: malformed YAML (<where>: nesting too deep (depth 65 > 64))`.
  An `except ValidationError: raise` now sits between the two clauses
  (`mapper/reqharness/config.py`): the named refusal surfaces as itself,
  `<file>: nesting too deep (depth 65 > 64)`, one prefix.  The asserting
  tests were strengthened to exact-message equality —
  `tests/test_reqharness_config.py::test_nesting_event_stream_refuses_superlinear_depth`,
  `…::test_nesting_event_stream_boundary_and_quoted_scalars` and
  `tests/test_reqharness_chain.py::test_input_limits_reported_by_name`.
- **LOW-3 — `_visible` widened.**  The audit escaper now also escapes every
  Zs separator other than U+0020 (NBSP U+00A0, U+2000–U+200A, U+202F,
  U+205F, U+3000), every Mn/Me combining mark and every variation selector
  (U+FE00–U+FE0F, U+E0100–U+E01EF) as `\uXXXX` — an invisible/width-spoofing
  space, a glyph-overlaying combining sequence or an emoji-presentation swap
  can no longer ride a crafted registry value onto the terminal.  New node:
  `tests/test_reqharness_release.py::test_audit_visible_escapes_nbsp_combining_and_variation_selectors`.
- **LOW-4 — `load_config` byte cap.**  `config.yml` now loads through the
  shared `_read_text` reader with the SAME named 64 KB cap the event files
  carry (`LIMIT_EVENT_FILE_BYTES`, R9): an over-cap config is refused
  `reqharness/config.yml: file too large (<n> bytes > 65536 byte limit)`
  before any parse.  Covered by the new arms of
  `tests/test_reqharness_config.py::test_load_rejects_unknown_reviewer_role`
  (over-cap refused by name with the byte count; one byte under parses).
- **LOW-2 — residual, no code change.**  Recorded in the PDR amendments
  section (§E row): a 4 MB `roles.yml` at the LEGAL depth limit (63) costs
  ~25 s CPU to load — the event-stream depth bound refuses only depth > 64,
  not byte volume at legal depth.  Accepted: the 4 MB cap (R9) bounds the
  input, registry writes are repo-write-gated (layer 3 — only the
  operator's own commits land), the cost is paid once at load, and
  `config.yml` is now further capped at 64 KB by LOW-4.

RED proof, one arm per nit (revert → RED → byte-identical sha256 restore →
GREEN): `.dev-flow/2026-10-11-reqharness-batch/evidence/close1-red.transcript`
— SHA-256 `0e4da4c37c87cb87b91877d3391d86734ba0ccc691d31b0607266d8bb9ec06c7`.
