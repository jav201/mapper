# Increment 006b — LLR-RVH.4.4 · help + palette carry the relmap scope (AT-149)

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `006b` |
| Lane (if the batch forked) | trunk, after the lanes joined · the shell's second half |
| Requirement(s) | `HLR-RVH.4` · `LLR-RVH.4.4` |
| Acceptance | `AT-149` (help + palette discoverability, equality not superset) · white-box `TC-RM-27` family (the shell's seat-equality census rows live in `tests/test_relmap_shell.py`) · no new unit (no new source unit — see §2) |
| Agent | `software-dev` |
| Date | `2026-10-25` |

---

## 1 · What changed

BLUF: **no source delta.** The relation screen's help and palette entries were
already derived from the single keymap seat by the generic machinery this
increment asserts: `RelMapScreen.KEY_SCOPE = SCOPE_RELMAP` (trunk Inc-2) is
the only input `app.action_help` / `app.action_palette` read, and the legend's
"keys in this view" section renders `bindings_for(self.scope)` while the
palette offers `palette_items(query, self.scope)` — the contract's own
draft-time verification of LLR-RVH.4.4 states it exactly: "a `KEY_SCOPE` is
sufficient, no app change required; **closed when Inc-2 lands the host and 6b
asserts it, AT-149**". Inc-6b is that assertion: two pilot-driven arms press
the REAL keys on the REAL surface (C-16) and pin seat equality in both
directions — a hand-added row reddens the set equality (M-RVH-12), a dropped
seat row reddens it too, and running the `matrix` palette entry through a
non-default query lands on the matrix view.

What the operator reaches: `?` on the relation screen lists exactly the
relmap seat rows (`1 matrix · 2 gaps · 3 sheet · r refresh · ↑↓←→ move · ↵
impact on node · c chain · k by kind · q quit · esc leave`, plus the two app
chords `ctrl+p palette · ? legend`); `ctrl+p` offers the same rows as actions;
typing `mat` filters to the `matrix` action; `↵` runs it and lands on the
matrix view.

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `tests/test_relmap_shell.py` | test | LLR-RVH.4.4 · AT-149 | APPENDED — 2 arms: `test_at_149_help_lists_exactly_the_seat_rows` (the `?` pilot + the painted `#help-content` rows equal the seat as a SET, plus AT-149's seven named chords) and `test_at_149_palette_offers_the_seat_and_runs_matrix` (the `ctrl+p` pilot, palette-items seat equality, the non-default `mat` query, a highlight move (C-10), and running the entry lands on the matrix view); the module docstring + imports updated |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc006b-*.txt` | generated | US-RMV-004 | RED, GREEN, mutants, guards — redacted, hashed |

| Count | Value |
|---|---|
| **SOURCE files** | **0 / 4** — the derivation pre-ships (§1); forcing an edit into `help.py`/`palette.py` would be a hand-row by another name, which M-RVH-12 exists to catch |
| Test files | 1 (appended; uncapped) |
| Doc files | 0 |

## 3 · How to test

```bash
PYTHONPATH=<worktree> python -c "import mapper; print(mapper.__file__)"
# the two AT-149 arms:
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_relmap_shell.py -k "at_149"
# the commission's guard set (see the packet's §4 transcript):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_fold.py tests/test_repair_artifact_claims.py tests/test_no_operator_paths.py \
  tests/test_mod_*.py tests/test_repair_map_truth.py tests/test_a3_census.py \
  tests/test_relmap_*.py tests/test_keymap.py tests/test_key_dispatch.py \
  tests/test_inc9c.py tests/test_help*.py tests/test_palette*.py \
  tests/test_reqharness_release.py tests/test_reqharness_baseline.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `full` | none — no new source unit (no branchful code added; the equality predicate itself is the assertion, killed by mutation, not by a copied oracle) | n/a |
| **A · white-box** `TC` ↔ LLR | `full` | the seat-equality census inside both arms (rendered rows parsed from the emitted `#help-content` text; the palette's offered items read live) | passed |
| **B · black-box** `AT` ↔ story | `full` | AT-149 through `run_test()` REAL keys (C-16): `?` → seat-equal legend → dismiss; `ctrl+p` → seat-equal palette → `mat` → move → `↵` → matrix view | passed |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | M-RVH-12, the proposal's declared RED-maker for these arms: a hand-written row appended to the legend render in `mapper/screens/help.py` (`_render_keymap`, between the seat-driven group loop and the return) |
| Instrument | project code — `_scratch/battery_6b.py` (python), hash-guarded edit, run, restore, re-hash |
| Where it ran | this worktree (wt-r2), the orchestrator's own run — serialized with the battery |
| Transcript | `evidence/p3-inc006b-red-mutant.txt` — `PYTEST_EXIT=1 WALL=3.0s`, both AT-149 arms failed on the set equality (`hand-added: [('zz', 'hand added')]`), restore hash `17011f2f…` back in place |
| Restore proven by | sha256 of `help.py` identical before/after (`17011f2f…e8ed093a`), printed in the transcript |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` in every run (C-46) |
| Arms resolved at baseline | 2 (both new nodes), plus the 39 carried nodes in the GREEN run |
| Verdict granularity | per node id |
| Arms that stayed GREEN | during the help-side mutation the palette node stayed GREEN **by design** (the mutation is help-scoped; the palette equality is exercised by the battery's second arm); at the RED pass no unrelated arm was expected to move — none did |

| Field | Value |
|---|---|
| **RED counterfactual** | M-RVH-12 (hand-added help row) → both new arms RED, transcript `evidence/p3-inc006b-red-mutant.txt` (sha256 `78c414d2…f60885`, runner exit 0), restore digest `17011f2f…e8ed093a` |

| Field | Value |
|---|---|
| **Mutation verdicts** | 2/2 KILLED, restore sha256 proven per arm: **M-RVH-12** (hand-added help row in `_render_keymap` → the help arm's set equality RED — `hand-added: [('zz', 'hand added')]`) · **M-RVH-12-palette** (hand-added row appended beside the seat read in `CommandPalette._refresh_list` → the palette arm's equality RED) · arms that stayed GREEN: none across the battery (each arm mutates its own surface; the sibling node passing under a single-surface mutation is named above, not counted as a kill) · runner's own BAD control shown BAD before the battery was believed · transcript `evidence/p3-inc006b-mutants.txt` (sha256 `d1cb9363…85a2ea`), runner exit 0 |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` (the two new nodes) | M-RVH-12 applied (hand row) | `2 failed` on the set equality — `evidence/p3-inc006b-red-mutant.txt` |
| the mutation runner | its own BAD control (anchor ×0) | `M-RVH-0-BAD: BAD -- anchor count 0 (expected 1)` and the battery stopped — control PASS, in `evidence/p3-inc006b-mutants.txt` |
| the row parser (`_help_key_rows`) | the M-RVH-12 hand row | the parse produced `('zz', 'hand added')` — the assertion diff printed it; the parser reads the PAINTED widget text, never the seat |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the legend's "keys in this view" body (the `#help-content` Static's text — what the legend paints) | `set(_help_key_rows(help_screen)) == {(b.glyph, b.label) for b in bindings_for(SCOPE_RELMAP)}` over the widget's stored text | equality held; 15 rows (13 relmap + 2 app chords) — `evidence/p3-inc006b-green-targeted.txt` |
| the palette's offered items (the live `_items` after the refresh) | `{(glyph, label, action)} == seat`, then after typing `mat`: `[('1', 'matrix', 'matrix')]` | equality held; the filtered list was exactly the matrix action |
| the frame after running the entry | `isinstance(app.screen, RelMapScreen) and app.screen.active_view == 'matrix'` | matrix |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted on its emitted form |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED mutant transcript | `…/evidence/p3-inc006b-red-mutant.txt` | `78c414d27bee91135b6afd18e066541966c95a24bc48f5f2c7a132b2cbf60885` |
| GREEN targeted transcript | `…/evidence/p3-inc006b-green-targeted.txt` | `e92e22edf33bdf3c92ed82316d29b1f690dd72854e77d21c4c67b3a573a06185` |
| mutation battery transcript | `…/evidence/p3-inc006b-mutants.txt` | `d1cb936399f09fb1ae27e42ab6f9f351248240f934dd1e523a18a564b885a2ea` |
| GREEN guard transcript | `…/evidence/p3-inc006b-green-guards.txt` | `45fa28160a28051cbf69a214a32177b2b2f3b10883500981e4cbe5e21f1b3696` |

All transcripts redacted with a PYTHON script (`_scratch/redact_6b.py`, account
name → `<user>`) before hashing; exit code and wall time in each transcript.

| Field | Value |
|---|---|
| **Evidence files** | 4 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "no hand-written help/palette row beside the seat" is an absence claim |
| If the result is an ABSENCE, what made the search wide enough | the equality is a SET comparison over every painted row, not a substring scan for known-bad strings — any hand row of any spelling enlarges the painted set |
| Guard labelled as protecting a CONCLUSION, not a behaviour | the two AT-149 nodes pin the conclusion "the relmap scope's help/palette entries are exactly the seat's" — a census, with its planted-violation proofs (the two battery mutants) |
| Conjunctive criteria: one mutation per conjunct | M-RVH-12 kills the help conjunct (hand row); M-RVH-12-palette kills the palette conjunct (hand row); the run-lands-on-matrix limb is killed by no mutant in this battery — it is the AT driver's dispatch limb, pinned by the carried Inc-2 view-switch arms |
| Synthetic instance of the absent case | the battery's two planted hand rows ARE the synthetic instances — each produced exactly the RED the absence claim predicts |
| **Positive control for every probe that returned an ABSENCE** | the seat rows themselves: the same parse returns all 15 seat rows present (the equality holds both directions — `hand-added: []` AND `missing: []` in the GREEN run), so the probe measures presence and absence with one mechanism |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rln "HelpScreen\|CommandPalette" tests/ mapper/` + `grep -rln "bindings_for\|palette_items" tests/ mapper/` | many PRE-EXISTING readers (app/keymap/screens/help/screens/palette/`test_help_scope.py`/`test_palette.py`/…) — all owned by earlier batches; this increment adds NO source symbol, and its arms re-run beside the pre-existing help/palette suites in the guard set (green) |
| B2 file moved on disk | n/a — no file moved; not fired |
| B3 byte-identical golden captures this source | `grep -rln "help\|palette" tests/goldens/` | no goldens dir covers these sources; not fired |
| B4 artifact produced here is consumed elsewhere | n/a — no artifact produced; not fired |
| A3 interface consumed by another module changed | n/a — no interface changed (no source touched); not fired |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes declared; B1 fired with the expected pre-existing population; B2/B3/B4/A3 not fired — this increment touches no code symbol or shared surface |

### Correction population — enumerated BEFORE the first site was edited

| Field | Value |
|---|---|
| **Correction population** | none — no correction (no source edit; the only edit sites are the appended test arms) |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| — (no supersession: no `.toggle(`/`.render(`/module-shape moves in this increment) | `git diff` names one test file + evidence only | yes | n/a — recorded to show the inspection ran |

### Signed-balance test ledger

`post = base − deleted + added` → `41 = 39 − 0 + 2`
(`tests/test_relmap_shell.py` 39 → 41 nodes). Guard set (30 files):
`1207 passed, 2 skipped, 3 xfailed` + the one sanctioned re-run — the first
guard run carried 4 failures inside the concurrent reviewers' mutation window
(`test_mod_parity` ×2, one `test_inc9c` home-routing arm, one carried shell
boundary arm); each passed on the single re-run the commission allows
(`exit=0`, appended to the transcript). No other guard file amended.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Kimi K2.8 session executing agents/code-reviewer.md + agents/security-reviewer.md + agents/ux-reviewer.md · approve-with-nits → nits dispositioned in the review-close unit (this commit)` |
| Review record | `.dev-flow/2026-10-25-relmap-r2-batch/evidence/review-inc006b7.md` (sha256 `3c464589cd211d9d295b7047075440294851e039461fa1537e749c728ef56194`) |

Follow-ups (2 MINOR, dispositioned in the review-close unit):

| Finding | Disposition | Evidence |
|---|---|---|
| F1 — the palette arm alone is blind to a DROPPED seat row: its oracle `palette_items("", SCOPE_RELMAP)` derives from the same seat, so the drop shrinks both sides and the equality still holds (the reviewer's seat-drop mutant M-R-6B-2 stayed GREEN on the palette arm) | **fixed**: new arm `test_at_149_palette_rows_match_the_keymaps_declared_relmap_seat` pins the keymap's DECLARED `SCOPE_RELMAP` bindings as a literal — a dropped seat row now reddens the palette side independently; the reviewer's M-R-6B-2 mutant applied → the new arm RED (`declared-but-not-offered (a dropped seat row lands here): [('c', 'chain', 'chain')]`), restore sha256 `319877a5…012a247` MATCH, arm re-run GREEN | `evidence/p3-inc006b7-review-red.txt` (sha256 `039d73632720b36ccd63c053f36fd2c44b0f035c483741a2673a90666bae2f3d`) · `evidence/p3-inc006b7-review-green.txt` (sha256 `33788f551b0ad5723e6fde3c7bd28ed9c2ada44acc2fa8170604c21e6848c6aa`) |
| F2 — `_help_key_rows` bakes the legend row anatomy (2-cell indent + 10-cell glyph column) into the test | **declared** — already declared in this packet's §5 risks; the reviewer's 87-width pilot confirms the anatomy holds at the narrow width (the equality is layout-relative but width-insensitive over 87…118), and an anatomy change fails the set equality loudly, not vacuously (an empty parse ≠ seat); recorded so the DDR does not re-litigate | packet §5 · review §2 F2 |

## 5 · Risks

- The seat-equality arms read the live widget internals (`#help-content`
  text, `_items`) — the row anatomy they parse (`_INDENT` + 10-cell glyph
  column + label) is a rendering detail of `help.py`; a legend layout redesign
  would have to update the parser with it. The arms deliberately do NOT parse
  group headers or the section title, so group renames are invisible to them.
- `?`-opens-help depends on the app binding reading `KEY_SCOPE`; a screen that
  forgets `KEY_SCOPE` would silently get the app-scope legend. That is the
  pre-existing generic contract (asserted for the map screen by
  `test_help_scope.py`), not a relmap-specific surface.

## 6 · Pending items / spec deviations

- None against the contract. The PLAN row names `screens/help.py` +
  `screens/palette.py` as this increment's two source files; the deviation is
  declared in §1/§2 — **0 SOURCE files** — because the derivation was closed
  generically at trunk Inc-2 and the contract's own draft-time verification
  names 6b as the ASSERTION increment ("closed when Inc-2 lands the host and
  6b asserts it, AT-149"). Writing source anyway would itself be the
  M-RVH-12 defect.
- Records proposed for the trunk: none needed beyond the PLAN test-ledger row
  (`tests/test_relmap_shell.py` +2 nodes; guard set as measured above).

## 7 · Suggested next task

Inc-7 — the hook per-line bound (`mapper/reqharness/audit.py`): RED
`tests/test_hook_line_bound.py`, the 240/239 spelling-aware cut in the
F-SEC-3 order, the M-RVU-1/2/3 battery, the R1 audit suite green, then the
batch gate (0 BLOCK expected — every AT minted). The orchestrator schedules
this increment's independent review (§4b).

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 0/4 — reason declared §1/§2 (assert-only increment; the contract names 6b as the assertion of the Inc-2-closed derivation) |
| 2 | Tests written in this same increment | all | ✓ | 2 AT-149 arms appended; RED-before-GREEN via the declared M-RVH-12 mutation |
| 3 | Layer 0 written where the criterion applies | `full` | ✓ | n/a — no new source unit; the criterion does not fire on zero source edits (assertion-by-mutation instead, arms 2/2 killed) |
| 4 | RED counterfactual declared | all | ✓ | M-RVH-12 hand row → both arms RED, transcript `evidence/p3-inc006b-red-mutant.txt` (sha256 `78c414d2…f60885`), restore digest `17011f2f…` |
| 5 | Reverse census declared | all | ✓ | §Reverse census — B1 fired (pre-existing population), B2/B3/B4/A3 not fired |
| 6 | `code-reviewer` passed | all | ⚠ | `pending — orchestrator schedules` (§4b) |
| 7 | No file from another lane touched | all | ✓ | only `tests/test_relmap_shell.py` + this increment's evidence; no renderer/home/app/keymap edits |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D1/D3/D4 and the seat untouched — this increment edits no source at all |
| 9 | Coverage claims verified on disk | all | ✓ | 41 targeted nodes + 1212 guard nodes collected on disk in the final runs |
| 10 | Load-bearing emptiness declared | all | ✓ | §Load-bearing emptiness — planted hand rows are the synthetic instances; positive controls named |
| 11 | Mutation verdicts declared | all | ✓ | 2/2 KILLED per arm, restore digests cited, BAD control PASS, runner exit 0 |
| 12 | Instrument RED-proof declared | all | ✓ | 3 instruments each shown RED first (pytest, the runner's BAD control, the row parser via the mutation diff) |
| 13 | Correction population declared | all | ✓ | none — no correction |
| 14 | Emitted-form assertion declared | all | ✓ | 3 artifacts asserted on emitted bytes (legend text, palette items, the landed view) |
| 15 | Independent review names somebody | all | ✓ | `pending — orchestrator schedules` (§4b) |
| 16 | Evidence files declared | all | ✓ | 4 files at `artifact_homes.evidence`, digests of stored bytes |
