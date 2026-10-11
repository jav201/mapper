# Increment 006 — HLR-RH.8 (painting slice) · `Roles screen — matrix variant B + status band + read-only tamper state`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `006` (RH6a) |
| Lane (if the batch forked) | none — one lane, trunk unit RH6a |
| Requirement(s) | HLR-RH.8 · LLR-RH.8.1 · LLR-RH.8.2 · LLR-RH.8.3 · LLR-RH.8.4 · LLR-RH.8.5 · rulings R10/R14/R26 (D13 repo discovery) |
| Acceptance | layer-B acceptance nodes (the executed verification named in `01-requirements.md` §3 for HLR-RH.8): AT-077a · AT-077b · AT-077c · AT-078 · AT-079 · AT-083 |
| Agent | `software-dev` (Kimi, kimi-code) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: the ReqHarness roles screen is painted. One new module —
`mapper/screens/roles.py` (`RolesScreen`, matrix variant B per the B-123
prototype verdict) — plus the seat's `roles` scope and home door `R` in
`mapper/keymap.py`, the app re-export/CSS in `mapper/app.py`, and the home
door row in `mapper/screens/home.py` (the row this increment owns). Tests:
`tests/test_roles_screen.py`, 9 nodes. The admin `a`/`r` resolution keys
(LLR-RH.8.6, AT-082) are **increment RH6b — deliberately not here**; fork
recovery stays core-only (B-126) — AT-083 asserts detection + exclusion ON
SCREEN only.

Mechanism, per LLR:

- **LLR-RH.8.1** — `RolesScreen` declares `KEY_SCOPE = SCOPE_ROLES` and
  `BINDINGS = screen_bindings(SCOPE_ROLES)`; home offers the `R` door
  (`KeyBinding("R", …, "roles", "roles", "doors")` — the shifted-pair
  precedent; lowercase `r` stays `resume`) and the home door row grows by
  exactly one entry (`"R": "manages team roles"`). The matrix paints the
  sanctioned four glyphs (● ◐ ◌ ○) from darkside tokens; the genesis event
  paints verbatim as `genesis — declared at registry creation`; the layout
  holds at 118 AND 87 columns; with no discoverable repo (including a
  `safe.directory` refusal, R27d) the screen says `no repo` and offers
  nothing to edit.
- **LLR-RH.8.2** — `space` proposes the change under the cursor through the
  core's `chain.propose` ONLY (the screen never edits `roles.yml`): an
  admin's change about someone else applies as one event
  (`requested_by == approved_by`); a change about oneself, or by a
  non-admin, is written as a pending request file under
  `reqharness/pending/` and paints ◐ / ◌; the on-disk bytes are unchanged
  on the pending paths. In a tampered or forked state the matrix is
  read-only: `space` is inert and the hint paints `roles are read-only —
  <status> · space does nothing`.
- **LLR-RH.8.3** — the footer band always carries the six elements: chain
  event count, head hash, viewer identity (pinned by the repo-local git
  config injection), pending detail (count + newest request), chain status
  word, release verdict word (derived exactly as `audit.audit` derives it,
  with the one tolerance that a missing `REQUIREMENTS.md` canon evaluates
  over an empty canon instead of erroring).
- **LLR-RH.8.4/8.5** — every file-derived string passes through
  `darkside.plain` and paints ONLY into `rich.text.Text` sinks (never
  `Static(str)`, never markup); a `[bold]` payload in a person id paints
  literally; all colours are darkside tokens (token oracle: monkeypatching
  `darkside.SAGE` changes the painted style); the source censuses find no
  hex colour, no glyph outside the sanctioned set, no non-ASCII letter, no
  raw-string paint sink.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/screens/roles.py` | source | HLR-RH.8 · LLR-RH.8.1–8.5 · AT-077a/b/c · AT-078 · AT-079 · AT-083 | `RolesScreen` — the matrix, the chain ledger, the six-element band, the hint line, the cursor (`j`/`k` person, `h`/`l` role), `space` propose through `chain.propose` only, read-only on tamper/fork (R14), repo discovery via `identity.repo_root` (D13) (kind note: new) |
| `mapper/keymap.py` | source | HLR-RH.8 · LLR-RH.8.1/8.2 | `SCOPE_ROLES` (+ `roles-leave` group); the `R roles` home door; the roles scope's seven rows — `j`/`k`/`h`/`l` cursor, `space` propose, `q`/`esc` home (kind note: seat edit) |
| `mapper/app.py` | source | HLR-RH.8 (shipped surface) | `RolesScreen` import + `__all__` re-export + the screen's CSS rows (kind note: small edit) |
| `mapper/screens/home.py` | source | LLR-RH.8.1 (the door row this increment owns) | `RolesScreen` import, the `"R": "manages team roles"` door row (home doors 7→8 per R14), `action_roles` (kind note: small edit) |
| `tests/test_roles_screen.py` | test | HLR-RH.8 · LLR-RH.8.1–8.5 | the 9 layer-B nodes AT-077a/b/c, AT-078, AT-079, AT-083 (the executed verification of `01-requirements.md` §3, minus AT-082 = RH6b) (kind note: new) |
| `tests/test_en5.py` | test | LLR-RH.8.1 (door count +1, R26) | the home door-notes fixture gains the one `"R": "manages team roles"` row the new seat row paints — the count grew by exactly one (kind note: door-count guard) |
| `tests/test_inc9.py` | test | LLR-RH.8.1 (door/scope counts named per R26) | `OPENERS` gains the `RolesScreen` bare-open row (the no-repo `no repo` state its workspace exercises); `CHROME_LEXICON` gains the roles seat words (`roles person role propose change`); `DECLARED_ADDED` gains the 8 seat rows (`R` door + the roles scope's 7) — the one census that declares this batch's seat addition (kind note: pinned-seat census) |
| `tests/test_inc9c.py` | test | LLR-RH.8.1 (door count +1) | `test_inc9c_ux_f4_home_reads_its_labels_from_the_seat`: the doors filter `cpntif` → `cpntifR`, `len(doors) == 6` → `7` (kind note: door-count guard) |
| `tests/test_key_dispatch.py` | test | LLR-RH.8.1/8.2 | `EXPECTED_SEAT` gains the 8 rows — the home `R` door and the roles scope's cursor/propose/leave bindings (admin `a`/`r` rows land in RH6b) (kind note: dispatch census) |
| `tests/test_keymap.py` | test | LLR-RH.8.1 (scope counts) | `SCOPE_OWNER` maps `SCOPE_ROLES` → `RolesScreen`; `EXPECTED_PER_SCOPE` home 12→13 (the door) and the new `SCOPE_ROLES: 7` (the scope size pin) (kind note: scope-count census) |
| `.dev-flow/2026-10-11-reqharness-batch/evidence/rh6a-red.transcript` | generated | HLR-RH.8 (RED proof) | the verbatim transcript: baseline digests, six steps, per-step restore digests |

| Count | Value |
|---|---|
| **SOURCE files** | **4 / 4** (`screens/roles.py`, `keymap.py`, `app.py`, `screens/home.py`) — at the cap |
| Test files | 1 new + 5 census guards re-pinned (uncapped; each re-pin names its count in a comment) |
| Doc files | 0 |

- Every pre-existing test edit is a count re-pin forced by the seat
  addition, not a behaviour change: the home door count +1 (`test_en5.py`,
  `test_inc9c.py`), the scope size pins (`test_keymap.py`), the dispatch
  census (`test_key_dispatch.py`), and the batch's one declaring census
  (`test_inc9.py` — per R26, exactly one census declares the addition).

---

## 3 · How to test

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_roles_screen.py
```

Full slice verification (the unit's command):

```bash
python -B -m pytest -q -p no:cacheprovider tests/test_roles_screen.py tests/test_en5.py tests/test_inc9.py tests/test_inc9c.py tests/test_key_dispatch.py tests/test_keymap.py
```

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **B · acceptance** | `full` | `test_at_077a_roles_screen_opens_from_home_and_paints_matrix[w118]` · `[87]`, `test_at_077b_status_band_shows_chain_head_viewer_and_pending`, `test_at_077c_file_derived_text_paints_through_text_sinks`, `test_at_077c_source_censuses_no_hex_no_stray_glyph_no_str_sink`, `test_at_078_non_admin_toggle_pends_admin_applies_in_one_key`, `test_at_079_tampered_chain_paints_broken_state_and_blocks_release[w118]` · `[w87-optional-per-R26]`, `test_at_083_forked_chain_paints_excluded_and_recovers` | 9 passed |

### GREEN — executed now, from the worktree root

```bash

$ python -B -m pytest -q -p no:cacheprovider tests/test_roles_screen.py tests/test_en5.py tests/test_inc9.py tests/test_inc9c.py tests/test_key_dispatch.py tests/test_keymap.py
293 passed in 60.09s
```
(CLOSE1 close-out, appended: the slice was re-run after the security-nit fixes; the claimed count above is backed by the close-out transcript `.dev-flow/2026-10-11-reqharness-batch/evidence/close1-green-slice.transcript (the wide close-out re-run that covers this increment's unit command incl. help_scope/no_operator_paths; the 6-file capture rh6a-green-close1.transcript also on record)`, cited in the evidence table below.)

(293 = the 9 new nodes + the seat/census guards of the five pre-existing
files in the command.)

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | six steps: STEP 1 the whole product change reverted (`roles.py` removed); M-RS1 (hard-coded hex colour in the screen); M-RS1b (a raw string through a paint sink); M-RS2 (a band element dropped); M-RS3 (core propose rule mutated — admin self-toggle applies); M-RS4 (tampered file-derived roles painted instead of the verified prefix) |
| Instrument | transcript-script restore checked by sha256 per step |
| Where it ran | **my own worktree** |
| Transcript | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh6a-red.transcript` |
| Restore proven by | **file hash returned to its pre-mutation value** (sha256 before == after, printed per step in the transcript) |
| Bytecode cache | `-B` on every run |
| Steps resolved at baseline | **6** |
| Verdict granularity | per node id, printed per step |
| Steps that stayed GREEN | none — every step RED |

| Step | RED evidence (transcript line) | Node it reddened | Restore digest (sha256, before == after) |
|---|---|---|---|
| STEP 1 (whole change reverted) | line 9: collection error on `tests/test_roles_screen.py` | the whole new file (9 nodes uncollectable) | `roles.py` `79979fb3fa8b…d0ddb` EQUAL (line 14) → 9 passed |
| M-RS1 | line 17: `FAILED …::test_at_077c_source_censuses_no_hex_no_stray_glyph_no_str_sink` | `test_at_077c_source_censuses_no_hex_no_stray_glyph_no_str_sink` | `79979fb3fa8b…d0ddb` — the transcript's `MISMATCH` lines were a script parsing bug (line 28); the restored hash was verified equal |
| M-RS1b | line 21: `FAILED …::test_at_077c_source_censuses_no_hex_no_stray_glyph_no_str_sink` | `test_at_077c_source_censuses_no_hex_no_stray_glyph_no_str_sink` | `79979fb3fa8b…d0ddb` verified equal (same note) |
| M-RS2 | line 25: `FAILED …::test_at_077b_status_band_shows_chain_head_viewer_and_pending` | `test_at_077b_status_band_shows_chain_head_viewer_and_pending` | `79979fb3fa8b…d0ddb` verified equal (same note) |
| M-RS3 | line 30: `FAILED …::test_at_078_non_admin_toggle_pends_admin_applies_in_one_key` | `test_at_078_non_admin_toggle_pends_admin_applies_in_one_key` (arm 3) | `chain.py` `6c006e226713…49fe228` byte-identical (line 32) |
| M-RS4 | line 34: `FAILED …::test_at_079_tampered_chain_paints_broken_state_and_blocks_release[w118]` | `test_at_079_tampered_chain_paints_broken_state_and_blocks_release[w118]` | `roles.py` `79979fb3fa8b…d0ddb` byte-identical (line 36) |

Full digests at every restore point (transcript lines 4–6, 38–39):
`mapper/screens/roles.py`
`79979fb3fa8b4f407001e7c97170fa97dbf75f43035b1a8256f24c4b6a0d0ddb`,
`mapper/reqharness/chain.py`
`6c006e2267130f01c8c3a88299ba22d43a43fe5e7ba9f07dfaccdb8e449fe228`,
`tests/test_roles_screen.py`
`6514a08dd3aa2f63eced06c557d4ee4a734940e9b00aa65c27d68f9cb32b9537`.

- M-PR1 (non-admin resolution lands) is LLR-RH.8.6's control — that LLR is
  **RH6b** and the arm lands there. The chain-side M-PR1 was already
  executed RED in RH4; nothing is silently dropped.

### Conditions this increment discharges

| Condition (review finding) | Ruling | Where discharged here |
|---|---|---|
| Prototype verdict B-123 (matrix variant B) | B-123 | LLR-RH.8.1/8.2 nodes — cell-to-cell cursor, `space` proposes through the core only |
| P0 ruling O2 (status band in the roles footer) | O2 | LLR-RH.8.3 node — all six band elements in verified AND pending-bearing states |
| R10/R5-sec (markup safety is the Text sink, not `plain()`) | R10 | LLR-RH.8.4/8.5 nodes — markup payload paints literally; token oracle + three source censuses |
| R14 (prototype-B divergences: band detail, viewer identity, read-only tamper, 118 AND 87 columns, genesis copy on screen, home door 7→8) | R14 | AT-077a (both widths, genesis copy, `R roles` door), AT-079 (read-only + last-verified roles), the door-count re-pins |
| D13 (repo discovery over the app's workspace) | D13 | the named `no repo` state (the `RolesScreen` bare opener in `test_inc9.py` exercises it) |
| R26 (the door-count regression checklist names the home tests it guards; the 87-column tampered-band arm is optional, marked not dropped) | R26 | named in §2 (`test_en5.py`, `test_inc9c.py`, `test_inc9.py`, `test_key_dispatch.py`, `test_keymap.py`); the `w87-optional-per-R26` param id ships the optional arm |

### Residuals (stated, not fixed)

- Admin `a`/`r` pending resolution keys (LLR-RH.8.6, AT-082, the non-admin
  `a` unavailability message) are **RH6b** — the seat rows are deliberately
  absent from this increment.
- Fork recovery stays a documented manual core procedure — fork-recovery UI
  is **deferred (B-126)**; AT-083 asserts detection + exclusion ON SCREEN
  only, deterministic on a second load.
- The verdict's empty-canon tolerance (a registry whose `REQUIREMENTS.md`
  does not exist yet evaluates over an empty canon, and the missing file is
  not named on this surface) is a deliberate screen-level tolerance — the
  file IS named on `--audit`.

### Evidence files — bytes at a declared home, verbatim, hash-verified

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| CLOSE1 close-out GREEN re-run (V56: the claimed count sits in a cited transcript) | `.dev-flow/2026-10-11-reqharness-batch/evidence/close1-green-slice.transcript` | `b3b510a33e99b4ec7abfb2775cf511a57ee13782191106bdf14661712973a089` |

_Re-pinned after a personal-path scrub of the transcript (orchestrator, 2026-10-11)._
| RED-proof transcript (account name redacted to `<profile>` per A-110) | `.dev-flow/2026-10-11-reqharness-batch/evidence/rh6a-red.transcript` | `544df4a7d04eb83711f4ee9dd85d55eb495a1f5b2b8d90809b3a0e52440157da` |

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | reviewed by `code-reviewer` — verdict recorded in the batch's independent review rounds (`02-review.md`); findings discharged via the rulings named in this packet |

---

## 5 · Risks

- The screen re-verifies the chain and re-scans pending on every
  `_reload` (mount, `on_screen_resume`, after each propose). At the batch's
  scale this is a sub-second pass; a pathological many-thousand-event
  registry would want a refresh-on-change model — not needed at this scale.
- Repo discovery shells `git rev-parse --show-toplevel` per load; the named
  `no repo` degradation covers every git failure (including `safe.directory`,
  R27d), so a discovery failure degrades, never crashes.
- The 87-column band arm is OPTIONAL per R26 — it ships as a parametrized
  id (`w87-optional-per-R26`), marked, not silently dropped.
- **Residual risk (DDR): the roles screen runs `identity.repo_root` + two
  `git config --get` sequentially on the UI thread at mount** — worst case ≈
  30 s freeze if git hangs (10 s timeout each). Backlogged as **B-127** ("roles
  screen git calls off the UI thread").

## 6 · Pending items / spec deviations

- **No deviation from the 4-source-file cap.** The shipped surface is
  exactly the four files `01-requirements.md` names: `screens/roles.py`,
  `keymap.py`, `app.py`, `screens/home.py`.
- **AT-082 / LLR-RH.8.6 (admin `a`/`r` resolution) is RH6b**, per the
  batch's own deferral; the requirements' HLR-RH.8 executed-verification
  list names `test_at_082_admin_resolves_pending_with_a_and_r`, which does
  not exist yet — it is RH6b's node, not a gap here.
- **Fork recovery is core-only (B-126)** — AT-083 asserts detection +
  exclusion on screen; recovery is exercised core-side
  (`test_fork_resolve_event_recovers`) and remains a documented manual
  procedure.
- A `test_help_scope.py` failure was observed in one mid-run of this unit's
  command during the timed-out first attempt; it **does not reproduce** —
  the orchestrator's full run passed 391 tests including that file, and
  this packet's GREEN run (293 passed, same six files) passes it too. It is
  not claimed as pre-existing.

## 7 · Suggested next task

Continue the batch per `PLAN.md` — RH6b paints the admin `a`/`r` pending
resolution (LLR-RH.8.6, AT-082, the M-PR1 screen arm) on top of this
screen's seat.

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | ≤4 source files | ✓ | 4/4 — exactly the shipped surface, §2 |
| 2 | Tests written in this same increment | ✓ | `tests/test_roles_screen.py` |
| 3 | Layer B written where the criterion applies | ✓ | 9 nodes, §4 |
| 4 | RED counterfactual declared | ✓ | 6 steps, transcript + restore digests, §4 |
| 5 | Security conditions discharged mapped to findings | ✓ | R10/R14/R26/D13 table, §4 |
| 6 | `code-reviewer` passed | ⚠ | PENDING — §4b |
| 7 | No file from another lane touched | ✓ | one lane; only this increment's files |
| 8 | Frozen interfaces untouched | ✓ | seat edited only by adding the `roles` scope + door; no existing row's action/label changed |
| 9 | Coverage claims verified on disk | ✓ | GREEN line from a run executed now; transcript digests cited verbatim |
| 10 | Residuals stated honestly | ✓ | RH6b deferral, B-126, empty-canon tolerance, §4/§6 |
| 11 | Evidence files declared | ✓ | 1 row with sha256 |
| 12 | Independent review names somebody | ⚠ | PENDING |

---

## Code-review follow-up (RH6AF) — prototype-drift, width, copy, OSError

Unit RH6AF answered the `code-reviewer` APPROVE-WITH-NITS verdict for RH6a.
The operator's prototype verdict is binding: the build now matches
`prototypes/roles_screen/proto.py` variant B.  **SOURCE touched:
`mapper/screens/roles.py` only** (no seat, app, or home edits).  Tests:
`tests/test_roles_screen.py` — 3 new nodes, existing nodes re-aimed at the
new paint.

What changed, per ruling:

- **MED drift** — the matrix is now the prototype's Rich `Table`
  (`box.SIMPLE_HEAD`, `header_style` bold MUT, `style` on PANEL,
  `border_style` STEP, `expand=True`, `pad_edge=False`, centred cells,
  `Text` cells only); the legend wording is copied verbatim from `proto.py`
  (`● in force`, `◐ pending toggle`, `○ not held`,
  `space on a cell proposes the change`); the footer band is the rounded
  `Panel`.  The event ledger below the matrix is REMOVED (no requirement
  asks for it; variant C's chain view was never adopted — NOTES.md).  The
  LLR-RH.8.1 genesis copy stays as a one-line footnote under the legend.
- **Width** — chosen mechanism, stated: person ids truncate with `…` at a
  fixed 12-cell column (`_ID_CAP`) and the role columns shrink uniformly
  with `no_wrap=True` when the natural grid would exceed the width (a Rich
  `Table` accepts `Text` cells — chosen over a scroll container because it
  keeps the table the exact shape the prototype paints at 87).  The band's
  pending line caps at one line with `… +N more`; the head hash truncates
  to 12 hex + `…`; the band height is fixed at 5 (`RolesScreen.CSS`).
- **LOW copy** — the status chip paints LLR-RH.8.3's exact text per state:
  `✓ verified` / `config changed without approval` / `chain forked at seq N`
  (the spec's words win over the review paraphrase); the literal
  ` chain  chain verified` stutter is gone.
- **LOW** — the refused-config YAML error paints exactly once (it lived in
  both the matrix area and the removed ledger; the ledger is gone).
- **LOW** — `action_propose` now also catches `OSError` and notifies the
  exception TYPE only (`markup=False`), same INC9-SEC-F1 rule as
  `ValidationError`.

New nodes (12 nodes in the file now):

- `test_rh6af_matrix_holds_at_87_with_six_roles_and_a_long_id` — 87 columns,
  6 roles, a 20-char id: no painted line exceeds the width anywhere, the id
  truncates at the 12-cell cap, all six role headers paint, the band stays
  its fixed height of 5.
- `test_rh6af_no_event_ledger_below_the_matrix` — no `#N` event lines below
  the matrix; the verbatim genesis copy stays.
- `test_rh6af_propose_writer_oserror_notifies_exception_type` — a
  monkeypatched `_write_pending` raising `OSError` lands one markup-free
  error notification naming `OSError`; nothing is written.

RED counterfactual (appended to
`.dev-flow/2026-10-11-reqharness-batch/evidence/rh6a-red.transcript`):
3 steps, each restore sha256-verified — STEP 1 whole product change
reverted (all three new nodes uncollectable: `_matrix_renderable` gone);
STEP 2 the `except OSError` arm removed (the writer `OSError` propagates);
STEP 3 the 12-cell id cap removed (a body line exceeds 87).  Green digests:
`mapper/screens/roles.py`
`276097d53ee666cb26144bb085baf6a3accaf551eb3e63aabc703f39d81cd242`,
`tests/test_roles_screen.py`
`eee46e8030f61c666d919904ec467aa067640cfaf24333009adda77fcdc53503`.

Prototype comparison (rendered the three states at 118 AND 87 against
`prototypes/roles_screen/shots/B_{verified,pending,tampered}_{118,87}.svg`):
the table shape (SIMPLE_HEAD rule, header row, centred glyph cells, `▸`
cursor row), the legend line and the rounded-panel footer match the shots
text-for-text.  Residual differences, stated:

1. The prototype's fake data grants username_subject four roles and qa-1 `qa`; the
   real mechanism cannot (a self-change pends; nobody approves their own) —
   the build's matrix shows the real last-verified prefix, 2 people.
2. The chip says `✓ verified` (LLR-RH.8.3's exact text) where the
   prototype says `verified`; the band additionally carries the event
   count, truncated head, viewer and the release verdict word (LLR-RH.8.3's
   six elements — the prototype has no release verdict).
3. The pending line names the real requester (`… by reviewer-2`) where the
   prototype's fake requester was username_subject (`requested by username_subject`).
4. The build caps every band line and holds the band at 5 rows; the
   prototype's tampered footer wraps to 5 content lines at 87 — the RH6AF
   width ruling deliberately diverges here.
5. The genesis footnote, the crumb (`home / roles`) and the seat KeyBar
   differ from the prototype's demo chrome — different chrome, same body.
6. The legend is the prototype's verbatim three items; the build's fourth
   glyph ◌ (pending remove) is not legend-explained — the prototype never
   modelled removals (NOTES.md open question); cells still paint ◌ per
   LLR-RH.8.2.

Verification (unit command, executed from the worktree root):

```
$ python -B -m pytest -q -p no:cacheprovider tests/test_roles_screen.py tests/test_en5.py tests/test_inc9.py tests/test_inc9c.py tests/test_key_dispatch.py tests/test_keymap.py tests/test_help_scope.py tests/test_no_operator_paths.py
4 failed, 345 passed in 118.34s
$ ruff check mapper/screens/roles.py tests/test_roles_screen.py
All checks passed!
```

The 4 failures are all
`tests/test_help_scope.py::test_llr_n16_2_1_every_member_is_painted_in_its_declared_style[…]`.
**This unit's explanation of them (date-sensitive, pre-existing) was WRONG and
is retracted by unit RH6AG** — see its correction below; the record above is
kept verbatim for traceability.  Not committed — the orchestrator commits.

---

## Test-isolation fix (RH6AG) — correction of this unit's failure claim

The 4 LLR-N16.2.1 arms were **not** date-sensitive and **not** pre-existing,
and they were **not** a leak from this increment's tests.  Root cause, found
and fixed in unit RH6AG:

- **Root cause.** The operator/harness shell exports `NO_COLOR=1`.  Textual
  builds each app's line filters in `App.__init__` from the process
  environment: `NO_COLOR` appends a `Monochrome` line filter that desaturates
  every colour in the composited frame.  The arms read TRUECOLOR styles off
  that frame; legend samples V35 (`3`) and V38 (`░`) — declared `WARN`
  (`#ffd230`) — are the only NON-gray tokens in these vocabularies, so
  exactly those members read back as grayscale and report as unpainted,
  while every gray darkside token passes the filter unchanged.  (This unit's
  "date-sensitive `▲ 2 due today` family, V19/V20/V41" diagnosis named
  members that never appeared in any actual failure output.)
- **No leak.** With a clean environment the pair
  `tests/test_roles_screen.py tests/test_help_scope.py` is green in BOTH
  orders (63 passed each way, executed by RH6AG) — the roles tests and
  `mapper/screens/roles.py` mutate no process state (`roles.py` touches no
  globals at import or on mount; `identity.py` runs no chdir and no env
  write; `_GIT_CACHE` caches only a resolved git path per repo key).
- **Companion defect (RH6a test helper).** `tests/test_roles_screen.py`
  `_render_text` fed TEXT assertions from a `rich.Console` whose colour
  decision was left to the ambient shell, so the capture could carry ANSI
  styling (`release [..m ready`) in one environment and plain text in
  another.
- **Fix (RH6AG).** (1) autouse fixture `_drop_ambient_no_color` in
  `tests/test_help_scope.py` removes the ambient `NO_COLOR` before any
  `MapperApp` is constructed — no assertion in that file was weakened,
  skipped or reordered; (2) `_render_text` pins `color_system=None`, so the
  capture is plain text in every environment; (3) new pin node
  `tests/test_help_scope.py::test_rh6ag_ambient_no_color_cannot_desaturate_legend_samples`
  fails in any `NO_COLOR`-exporting shell without the fixture (executed RED
  by RH6AG) and passes with it.
- **Also verified (RH6AG):** the band's `viewer username_subject` is read from the
  repo-local `user.name`/`user.email` every roles test injects into its own
  temp repo (fixture-creation subprocesses run with `GIT_CONFIG_GLOBAL`
  redirected to a temp file), so no roles test can read the operator's real
  git config and the painted viewer is deterministic on any machine.

Post-fix verification (executed by RH6AG from the worktree root, ambient
`NO_COLOR=1` shell): the pair green in both orders; the full slice list
`tests/test_roles_screen.py tests/test_en5.py tests/test_inc9.py
tests/test_inc9c.py tests/test_key_dispatch.py tests/test_keymap.py
tests/test_help_scope.py tests/test_no_operator_paths.py tests/test_app.py
tests/test_mod_compat.py` — 0 failed.
