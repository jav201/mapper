# Increment 007 — HLR-RH.2 / HLR-RH.8 · `Admin a/r pending resolution on the roles screen`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `007` (RH6b — split out of the old increment 6 by round-2 ruling R25) |
| Lane (if the batch forked) | none — one lane, trunk unit RH6B |
| Requirement(s) | HLR-RH.8 · LLR-RH.8.6 (a/r pending resolution) · LLR-RH.2.2 arm (the pending file store the resolution references) · rulings R6/R25/R26 |
| Acceptance | `tests/test_roles_screen.py::test_at_082_admin_resolves_pending_with_a_and_r` (the AT-082 node named in `01-requirements.md` §3) + the RH6b boundary nodes |
| Agent | `software-dev` (Kimi, kimi-code) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: the roles screen's pending-resolution keys land. On a pending change
under the cursor, an admin (a role in force at the current head, per the
verified chain prefix) presses `a` and the screen calls the core's
`chain.approve_pending`; `r` calls `chain.reject_pending`. The screen never
writes `roles.yml` itself and never resolves its own request — the core
refuses both, and the refusal is painted. Two seat rows (`a`/`r` in the
`roles` scope) make the keybar advertise the keys; the matrix legend is
untouched (see §6).

Mechanism, per LLR:

- **LLR-RH.8.6 (R6)** — `RolesScreen.action_approve` / `action_reject`
  delegate to one `_resolve_pending(approve=...)`:
  - no repo / config refusal / read-only (tampered or forked) → inert, the
    hint line says why (R14), nothing is called;
  - non-admin viewer → the hint line paints exactly
    `a is unavailable (needs an admin)` (byte-exact per R6; the `r` arm is
    symmetric), nothing is called or written;
  - no open request under the cursor → inert, `no pending change under the
    cursor`;
  - otherwise the screen calls `chain.approve_pending` /
    `chain.reject_pending` with the request's file name and the viewer id.
    A `ValidationError` (own request, already resolved, not appendable,
    name/content mismatch) paints the core's NAMED refusal verbatim on the
    HINT LINE (a Text sink — `darkside.hint_line` coerces through
    `plain()`); the toast stays TYPE-only (`could not approve the request:
    ValidationError`, `markup=False`) under the propose path's `INC9-SEC-F1`
    rule — no census carry is declared (see §6). An `OSError` is named by
    TYPE only, same rule.
  - success → full reload from disk: the matrix, the pending cells and the
    band all re-derive (the resolution is derived from the chain per R6 —
    the pending file stays on disk).
- **Keymap** — the `roles` scope gains `a → approve` and `r → reject`
  (labels `approve`/`reject`, the prototype keybar's words). The keybar
  advertises them automatically; the band legend gains NO a/r hint because
  the prototype's variant-B legend (`prototypes/roles_screen/proto.py`)
  carries none — the legend copy stays verbatim (§6).
- **AT-082 arms** — approve lands ONE chain event referencing the request's
  sha256 (`requested_by` = the requester, `approved_by` = the admin; the
  pending file remains on disk); `r` lands an empty `resolution` event
  referencing the digest, glyph cleared; the non-admin message is
  byte-exact; the resolutions survive closing and reopening the app (the
  restart arm re-opens `MapperApp(tmp_path)` and observes the derived
  glyphs and `pending 0`).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/roles.py` | source | HLR-RH.8 · LLR-RH.8.6 · AT-082 | `_Snapshot.open_requests` (the pending-derived open requests kept from the load pass); `action_approve`/`action_reject` → `_resolve_pending` through `chain.approve_pending`/`chain.reject_pending` only; the refusal/hint constants; module docstring (kind note: edit) |
| `mapper/keymap.py` | source | LLR-RH.8.6 · R25 | the `roles` scope gains `a → approve` and `r → reject` (the scope's 7 → 9 rows) (kind note: seat edit) |
| `tests/test_roles_screen.py` | test | HLR-RH.8 · LLR-RH.8.6 | AT-082 (approve/reject/non-admin/restart arms) + 5 RH6b boundary nodes: own-request refusal, non-admin inert (a AND r), tampered inert, double-resolution named (the H1 guard through the screen — the fixture crafts a verified chain event that references the request's digest without applying it, so the request still derives `pending` while the chain references it), resolution-writer OSError |
| `tests/test_keymap.py` | test | LLR-RH.8.1 (scope counts) | `EXPECTED_PER_SCOPE[SCOPE_ROLES]` 7 → 9 — the two new seat rows change the scope size the fence pins; updated in the same edit as the seat rows (kind note: scope-count census) |
| `tests/test_key_dispatch.py` | test | LLR-RH.8.1/8.6 | `EXPECTED_SEAT` gains the `("roles", "a")` / `("roles", "r")` full-tuple rows — the whole-seat pin reddens on any added/removed binding, so the two new rows must be declared (kind note: dispatch census) |
| `tests/test_inc9.py` | test | LLR-RH.8.1 · R26 · A-112 | `DECLARED_ADDED` gains the two seat rows (the one census that declares this batch's seat addition); `CHROME_LEXICON` gains `approve reject` (the A-112 English census judges every seat label — a deliberate edit in the commit that paints the words) (kind note: pinned-seat census + A-112 lexicon) |

| Count | Value |
|---|---|
| **SOURCE files** | **2 / 4** (`mapper/screens/roles.py`, `mapper/keymap.py`) |
| Test files | 1 extended + 3 census edits (uncapped) |
| Doc files | 1 (this packet) |

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_roles_screen.py
```

Full slice verification (the unit's command):

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_roles_screen.py tests/test_reqharness_*.py tests/test_en5.py tests/test_inc9.py tests/test_inc9c.py tests/test_key_dispatch.py tests/test_keymap.py tests/test_help_scope.py tests/test_no_operator_paths.py tests/test_app.py
ruff check mapper/screens/roles.py mapper/keymap.py tests/test_roles_screen.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **B (acceptance)** | `full` | `test_at_082_admin_resolves_pending_with_a_and_r` (AT-082) · `test_rh6b_admin_resolving_own_request_is_refused_and_named` · `test_rh6b_non_admin_resolution_keys_inert` · `test_rh6b_tampered_chain_resolution_keys_inert` · `test_rh6b_double_resolution_refusal_is_named` · `test_rh6b_resolution_writer_oserror_notifies_exception_type` | 6 passed (18 in the file) |

### GREEN — executed now, from the worktree root

```bash

$ python -B -m pytest -q -p no:cacheprovider tests/test_roles_screen.py tests/test_reqharness_*.py tests/test_en5.py tests/test_inc9.py tests/test_inc9c.py tests/test_key_dispatch.py tests/test_keymap.py tests/test_help_scope.py tests/test_no_operator_paths.py tests/test_app.py
437 passed, 1 warning in 139.49s
$ ruff check mapper/screens/roles.py mapper/keymap.py tests/test_roles_screen.py tests/test_keymap.py tests/test_key_dispatch.py tests/test_inc9.py tests/test_inc9c.py
All checks passed!
```
(CLOSE1 close-out, appended: the slice was re-run after the security-nit fixes; the claimed count above is backed by the close-out transcript `.dev-flow/2026-10-11-reqharness-batch/evidence/rh7-green-close1.transcript`, cited in the evidence table below.)

(437 = the 6 new nodes + every previously-green node in the unit's
verification surface; the pre-existing warning is the
`PytestDeprecationWarning` the suite has always emitted.)

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutations applied | ARM 1: the whole RH6b product change reverted to HEAD (both files); ARM 2: M-PR1 screen limb — the non-admin guard in `_resolve_pending` deleted; ARM 3: the read-only guard in `_resolve_pending` deleted |
| Instrument | inline commands from the worktree root, no absolute paths; GREEN backups kept at `evidence/rh6b-backup/` |
| Where it ran | **my own worktree** |
| Transcript | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh6b-red.transcript` |
| Restore proven by | **sha256 returned to the pre-mutation value on every arm** (printed per arm) |
| Bytecode cache | `-B` / `PYTHONDONTWRITEBYTECODE=1` on every run |
| Arms resolved at baseline | 3 / 3 (each arm reddened ≥1 named node) |

| Arm | RED evidence (transcript) | Node(s) reddened | Restore digest (sha256, before == after) |
|---|---|---|---|
| 1 — full revert | `5 failed, 1 passed` — the 6-node run | AT-082, own-request, non-admin, double-resolution, OSError | `roles.py c10ab9f9…a2d121`, `keymap.py ee3262a3…686112d` byte-identical → 6 passed |
| 2 — M-PR1 (screen limb) | `2 failed` — the non-admin guard deleted | AT-082 (non-admin arm), `test_rh6b_non_admin_resolution_keys_inert` | `c10ab9f9…a2d121` byte-identical → 6 passed |
| 3 — read-only guard | `1 failed` — `a` reaches the core on a tampered chain | `test_rh6b_tampered_chain_resolution_keys_inert` | `c10ab9f9…a2d121` byte-identical → 6 passed |

- Arm-1 granularity note: `test_rh6b_tampered_chain_resolution_keys_inert`
  stays GREEN on the FULL revert by construction — with the binding reverted
  the `a` key does not exist at all, which is observationally inert on that
  arm. Its RED comes from Arm 3, where the binding exists and the read-only
  guard is the only thing keeping it inert (the core still refuses the
  append; the assertion that reddens is the read-only message itself).

Full digests at every restore point: `mapper/screens/roles.py`
`c10ab9f977f2f2c15d0acd5cf49283465f98c8e93c44c06290dc9e7f67a2d121`,
`mapper/keymap.py`
`ee3262a3a6cf7b4a2ef9fd96fe7c6114dc7369424602b006552b050eb686112d`.

### Conditions this increment discharges

| Condition (review finding) | Ruling | Where discharged here |
|---|---|---|
| Round-1 qa QH2 (no approve/reject keys or AT) | R6 | the seat rows + LLR-RH.8.6 + AT-082 |
| Round-1 architect H5 + qa QH1 (pending resolution; restart arm) | R6 | AT-082 arms 1–4 (approve/reject/non-admin/restart) — the derivation survives the app close/reopen |
| Own-request resolution refused | R6 | `test_rh6b_admin_resolving_own_request_is_refused_and_named` (a AND r) |
| Double resolution refused (H1) | R6/RHFIX4-H1 | `test_rh6b_double_resolution_refusal_is_named` — the core's `request already resolved` reaches the screen through a crafted referencing event |
| Non-admin `a` unavailability, byte-exact | R6 | AT-082 arm 3 + `test_rh6b_non_admin_resolution_keys_inert` |
| Read-only tamper state covers the new keys | R14 | `test_rh6b_tampered_chain_resolution_keys_inert` |
| `ValidationError`/`OSError` never crash the screen | the unit's contract | the refusal/OSError arms |

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | reviewed by `code-reviewer` (Claude Sonnet) — APPROVE-WITH-NITS; every nit was discharged as follow-up RHFIX6B (§8 below), each fix RED-proved and restored byte-identical |

---

## 5 · Risks

- The screen resolves the pending request under the CURSOR (person x role
  cell), matching the prototype's interaction (`a`/`r` act on the selected
  cell). Two open requests can never share one cell — the propose path
  already refuses a duplicate pending change on the same cell
  (`_PENDING_ALREADY_HINT`).
- The double-resolution guard (H1) is unreachable through the screen's own
  load pass (a request the chain references no longer derives `pending`, so
  it never appears under the cursor); the arm reaches it through a crafted
  chain event, exactly the TOCTOU shape the guard defends against.
- A name/content-mismatched or malformed pending file is refused by name at
  LOAD time (R22, core-side, already covered by RH4's nodes); at press time
  the screen only ever hands the core a file that validated in its own load
  pass.
- **Residual risk (DDR): the roles screen runs `identity.repo_root` + two
  `git config --get` sequentially on the UI thread at mount** — worst case ≈
  30 s freeze if git hangs (10 s timeout each). Backlogged as **B-127** ("roles
  screen git calls off the UI thread").

## 6 · Pending items / spec deviations

- **Band legend: deliberately NO a/r hint.** The unit allows the legend to
  gain the hint only if the prototype or spec shows one. The prototype's
  variant-B legend (`prototypes/roles_screen/proto.py`) carries only the
  `space` wording, copied verbatim by RH6a; the a/r hint exists only in the
  prototype's hand-written demo keybar, which the real keybar replaces. The
  seat rows make the real keybar advertise `a`/`r` — no copy invented.
- **The named refusal paints on the hint line; the toast stays type-only.**
  The unit asks for a named notification on the refusal arms; the toast
  names the refusal TYPE (`…: ValidationError`, `markup=False`), and the
  core's verbatim refusal text paints on the hint line (a `Text` sink via
  `darkside.plain`). This keeps `tests/test_inc9c.py`'s SEC-F1 toast census
  untouched — no `LEAK_EXCEPTIONS` carry is declared — consistent with the
  propose path's `INC9-SEC-F1` precedent (toast text an exception could
  embed stays type-only; only core-authored, path-free words reach a paint
  sink).
- Fork recovery stays core-only (B-126) — unchanged from RH6a; AT-083 is
  not re-lit here.
- `test_at_077a`'s keybar arms hold unchanged at both widths (118 AND 87):
  the two new keybar rows fold into the bar's `… +N` overflow without
  evicting the pinned rows.

## 7 · Suggested next task

The batch's build increments are done through RH6b. Remaining per
`PLAN.md`: the DDR full-suite re-run + the P2/P4 gates (`--audit` goldens,
perf), then validation/postmortem. Follow-up batches (review/signing
screen, baseline/release view) start from their prototype rounds.

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 2/4 — `mapper/screens/roles.py`, `mapper/keymap.py` |
| 2 | Tests written in this same increment | ✓ | `tests/test_roles_screen.py` (6 new nodes) |
| 3 | Layer B written where the criterion applies | ✓ | AT-082 + 5 boundary nodes, §4 |
| 4 | RED counterfactual declared | ✓ | 3 arms, transcript + restore digests, §4 |
| 5 | Security conditions discharged mapped to findings | ✓ | QH1/QH2/R6/R14/H1 table, §4 |
| 6 | `code-reviewer` passed | ✓ | RHFIX6B: APPROVE-WITH-NITS → every nit fixed and RED-proved (§8) |
| 7 | No file from another lane touched | ✓ | one lane; only this increment's files |
| 8 | Frozen interfaces untouched | ✓ | no ARQ §4 row changed; the keymap seat edit is this increment's declared act |
| 9 | Coverage claims verified on disk | ✓ | GREEN line from a run executed now; claims cite the transcript |
| 10 | Residuals stated honestly | ✓ | §5/§6 (cursor-targeted resolution, H1 reachability, legend ruling, toast rule) |
| 11 | Evidence files declared | ✓ | transcript, sha256 below |
| 12 | Independent review names somebody | ✓ | §4b — `code-reviewer` (Claude Sonnet), APPROVE-WITH-NITS, follow-up RHFIX6B |

---

## Evidence files

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| CLOSE1 close-out GREEN re-run (V56: the claimed count sits in a cited transcript) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh7-green-close1.transcript` | `52dd25745e50608d3dcbec8fce6cf4d2683a04f51f2e551f50d1ad1cfa5043d2` |

_Re-pinned after a personal-path scrub of the transcript (orchestrator, 2026-10-11)._
| RED-proof transcript (account name redacted to `<profile>` per A-110) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh6b-red.transcript` | `a80521e3f3865d592802dd92e676eb197d339ca6c794ac1f14a56150d4b168ca` |
| GREEN backups of the two product files | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh6b-backup/{roles.py,keymap.py}` | `roles.py` `c10ab9f977f2f2c15d0acd5cf49283465f98c8e93c44c06290dc9e7f67a2d121` · `keymap.py` `ee3262a3a6cf7b4a2ef9fd96fe7c6114dc7369424602b006552b050eb686112d` |

---

## Code-review follow-up (RHFIX6B, Claude Sonnet APPROVE-WITH-NITS)

Source touched: `mapper/screens/roles.py` ONLY. Tests: `tests/test_roles_screen.py`
(4 new `test_rhfix6b_*` nodes; AT-082 arms 1/2 now assert the success hints
exactly).

- **MED — several pending on one cell.** `_resolve_pending` collected the
  open requests for the cursor cell with `next(...)`, silently picking the
  oldest. Now: more than one open request on the cell refuses with the named
  hint `several pending requests on this cell — resolve them from the core
  (B-126 follow-up)` and writes nothing (`a` AND `r`). Covered by
  `test_rhfix6b_several_pending_on_one_cell_refuses_a_and_r` (chain bytes
  unchanged, hint byte-exact, no notification).
- **LOW — stale authority.** `_resolve_pending` calls `_reload()` at the
  START of the action, so the admin pre-filter and the selected request
  reflect DISK at keypress time (the core stays the authority). Covered by
  `test_rhfix6b_admin_revoked_on_disk_refuses_a_at_keypress` (mid-session
  revoke → `a` refused, named hint, nothing written) and
  `test_rhfix6b_admin_granted_on_disk_allows_a_at_keypress` (mid-session
  grant → `a` lands one event in place; the on-disk grant uses a chain time
  before wall clock so the screen's own approval still postdates it).
- **LOW — success hints name the request.** `approved: <person> +<role>
  (requested by <requester>)` / `rejected: …`, with the matrix's grant/revoke
  sign (`+`/`-`) and every file-derived part coerced through
  `darkside.plain`. The hint line is a `Text` sink via
  `darkside.hint_line` (`Text.assemble((plain(text), MUT))`), which never
  parses markup — so painting through `HintLine.set_hint` IS painting as
  `Text`.
- **LOW — non-pending cursor cell.**
  `test_rhfix6b_cursor_on_non_pending_cell_shows_no_pending_hint` pins the
  named `_NO_PENDING_HINT` and that nothing is written.
- **Markup finding (verbatim `str(exc)` on the hint line).** READ
  `mapper/darkside.py`: `hint_line` builds the line with
  `Text.assemble((plain(text), MUT))`, and `plain()`'s own docstring states
  `Text` does not parse markup — safety comes from never handing a
  file-derived `str` to a markup-parsing sink. Conclusion: the verbatim
  `str(exc)` refusal cannot render markup on the hint line; NO change
  needed. (`[bold]` inside a core refusal would paint literally.)

RED proof: 3 of the 4 new nodes fail against the reverted product
(`git show HEAD:mapper/screens/roles.py`; restore verified byte-identical,
sha256 `50b7c523…`); the non-pending node pins pre-existing behaviour and is
RED-immune by construction. Transcript appended to
`.dev-flow/2026-10-11-reqharness-batch/evidence/rh6b-red.transcript`.
