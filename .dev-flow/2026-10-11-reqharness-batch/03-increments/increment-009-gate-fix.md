# Increment 009 — batch gate fix · `repo-wide guard repairs for the reqharness batch`

| Field | Value |
|---|---|
| Batch | `2026-10-11-reqharness-batch` |
| Increment | `009` (gate fix — follows the full-suite gate of increment 008-ddr-fix) |
| Lane (if the batch forked) | none — trunk unit |
| Requirement(s) | LLR-MOD.1.3 · LLR-MOD.3.1 / AT-064 · LLR-N07.2.2a · HLR-S06.1–3 / LLR-S06.3.4–3.5 · LLR-MOD.4.2 / AT-065 · P-CARRY (artifact-claims guard) |
| Acceptance | the 8 gate failures at 0 failed; every fix at its ROOT per the orchestrator rulings; no guard weakened, no xfail/skip; every pin change itemised |
| Agent | `software-dev` (Kimi, kimi-code / kimi-for-coding) |
| Date | `2026-10-11` |

---

## 1 · What changed

BLUF: the full suite ran 3346 passed / 12 failed, and on re-run 8 repo-wide
guard failures remained — every one tripped by this batch's own new code
(the `--audit` CLI, the roles screen, the `mapper/reqharness/` package).
Each failure is fixed at its ROOT per the orchestrator's six rulings; no
guard logic was weakened, nothing was xfailed or skipped, and every pin or
register change carries an itemised comment (what changed, which increment,
why). One ruling (the A3 pin) was re-derived after ruling 1's move, exactly
as the unit anticipated: the pre-gate derived count was 84, the move turned
the audit dispatch's `.render` into a bare-name call the attribute-only
census does not derive, and the pin landed at 83 — the +1/-1 is itemised in
the pin comment, not netted away.

Per ruling:

1. **LLR-MOD.1.3** — `app.py` had gained `def _run_audit_cli`, which the
   spine-b checker reports as `app_extra_defs`. FIX (root): the CLI body
   MOVED into the domain core as the public
   `mapper/reqharness/audit.py::run_cli(argv) -> int` — same messages, same
   usage-error path (now returning 2 instead of raising), same catch-all,
   same exit semantics. `app.main` only dispatches `--audit` to it after the
   UTF-8 re-wrap (`raise SystemExit(reqharness_audit.run_cli(sys.argv))`);
   `app.py` holds no new def. The existing audit CLI tests
   (`tests/test_reqharness_release.py`, `tests/test_reqharness_baseline.py`)
   are unchanged — including their assertions — and pass.
2. **AT-064** — `app.py` imported `RolesScreen` (for the stylesheet selector
   and the LLR-MOD.3.1 `__all__` re-export tree) but never used it as an AST
   name. FIX (root, the convention other screens already use): the guard's
   `ALLOWED_UNUSED` records the deliberate re-export under `mapper/app.py`
   with the same reason string as the other screen re-exports, itemised.
   The guard's logic is untouched.
3. **LLR-N07.2.2a** — the arg-ful call-site pin 82 derived 84 pre-gate. The
   two new sites are the batch's `--audit` entry; after ruling 1 re-derived
   the count, the pin moved 82 → 83: `+1` the R27d arm's attribute call
   `audit_mod.render(report)` in `tests/test_reqharness_release.py` (the
   rendered text is the arm's subject), `+1/-1` the dispatch site that
   entered as `reqharness_audit.render(report)` in `app.py` and left the
   census's sight (bare-name `render(report)`) when ruling 1 moved it into
   `audit.py::run_cli`. Itemised in the pin comment.
4. **HLR-S06 census** — the roles screen added 14 severity/busy sites
   (40 → 54), all in `mapper/screens/roles.py`. FIX (root): every site is
   classified in `CONFORMING_SEVERITY` with a concrete path, judged line by
   line against WARN's and ALERT's declared jobs — the unverifiable chain
   state (no repo / tampered / forked) paints ALERT, every recovery notice,
   pending toggle and not-ready verdict paints WARN; the register block
   carries the per-site judgements and the 40 → 54 move is itemised at the
   pin. The guard's classification table and logic are untouched, and the
   one-job census (`LLR-S06.3.5`) still sees exactly one job per site.
5. **LLR-MOD.4.2 / AT-065** — RH6a's `R roles` door moved the home key-hint
   overflow counter +8 → +9 (118 cols) and +10 → +11 (87 cols). Intended
   change: the two goldens were regenerated with the repo's documented
   command (`MOD_PARITY_UPDATE=1 python -m pytest -q -p no:cacheprovider
   "tests/test_mod_parity.py::test_at065_parity_matches_golden[118]"
   "tests/test_mod_parity.py::test_at065_parity_matches_golden[87]"`), the
   verified diff was EXACTLY that one counter line in each golden, and the
   `GOLDEN_SHA256` record was re-pinned with an itemised comment. The repo
   keeps no MANIFEST; the regen is recorded here and in the `GOLDEN_SHA256`
   comment beside the hashes. The mutant-copy RED arm is untouched and
   passes.
6. **P-CARRY / artifact claims** — historical records cite
   `model.py:<line>`; the batch's `mapper/reqharness/model.py` made the
   basename ambiguous (`_resolve` reports "unresolvable or ambiguous" for
   `04-gate-findings-disposition.md` and `search.py`). Historical records
   are NOT rewritten. FIX (root): `mapper/reqharness/model.py` RENAMED to
   `mapper/reqharness/records.py` with `git mv` (history follows), every
   import inside `mapper/reqharness/` and the tests updated, the two batch
   increment packets that cite `reqharness/model.py` updated as text
   references (with a note recording the rename). `docs/ARCHITECTURE.md`
   names no `reqharness/model.py` row (the §2 row uses the `*.py` glob), so
   no map row changed. Evidence transcripts naming
   `mapper.reqharness.model.ValidationError` are historical run records and
   stand unedited.

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/app.py` | source | ruling 1 · LLR-MOD.1.3 | `_run_audit_cli` removed; `main` dispatches `--audit` to `reqharness.audit.run_cli` after the UTF-8 re-wrap |
| `mapper/reqharness/audit.py` | source | ruling 1 · HLR-RH.7 | new public `run_cli(argv) -> int` (the moved CLI body; `sys` import; `__all__` gains `run_cli`; module docstring's exit-semantics line updated) + ruling 6 import re-point |
| `mapper/reqharness/model.py` → `mapper/reqharness/records.py` | source (rename, `git mv`) | ruling 6 · P-CARRY | the value-object module renamed so historical `model.py:<line>` citations stay unambiguous; counts as ONE move |
| `mapper/reqharness/records.py` | source | ruling 6 · P-CARRY | the rename DESTINATION named on its own row so the close-gate reverse trace (which parses only `increment-NNN.md` packet names and one path per `File` cell) resolves the path — the move itself is recorded in the row above; CLOSE3 addition |
| `mapper/reqharness/{baseline,cache,chain,config,derive,pending,release,reviews}.py` | source (import re-point) | ruling 6 (inside the one move) | `from mapper.reqharness.model import …` → `… records import …` |
| `mapper/screens/roles.py` | source (import re-point) | ruling 6 (inside the one move) | same one-line import re-point |
| `tests/test_app_imports_used.py` | test (allowance row) | ruling 2 · AT-064 | `RolesScreen` recorded as a declared `app.py` re-export (LLR-MOD.3.1), itemised; guard logic untouched |
| `tests/test_a3_census.py` | test (pin) | ruling 3 · LLR-N07.2.2a | arg-ful pin 82 → 83, itemised (+1 R27d arm; +1/-1 the dispatch site that ruling 1 moved out of the census's sight) |
| `tests/test_darkside_census.py` | test (register) | ruling 4 · HLR-S06 | 14 `CONFORMING_SEVERITY` rows for `mapper/screens/roles.py`, judged per site; pin 40 → 54 itemised |
| `tests/test_mod_parity.py` | test (golden record) | ruling 5 · LLR-MOD.4.2 | `GOLDEN_SHA256` re-pinned for both widths with the itemised regen note |
| `.dev-flow/2026-10-09-modular-batch/evidence/mod_parity_{118,87}.txt` | golden | ruling 5 · AT-065 | regenerated; verified diff = exactly the one overflow-counter line in each (`+8 → +9` / `+10 → +11`, the RH6a `R roles` door) — the closed 2026-10-09 batch's evidence home is where AT-065 reads its goldens from, so the intended change lands there and is recorded here |
| `tests/test_reqharness_{baseline,config,chain,release,registry}.py` | test (import re-point) | ruling 6 (inside the one move) | `from mapper.reqharness.model import …` → `… records import …` |
| `03-increments/increment-001.md`, `increment-002.md` | packet (text ref) | ruling 6 | the `mapper/reqharness/model.py` source rows now name `records.py` with a note recording the gate-fix rename |

| Count | Value |
|---|---|
| **SOURCE files** | **3 touched + 1 rename**: `app.py`, `audit.py`, the `model.py → records.py` move (one), and the import re-points inside the move. The rename is the one sanctioned source move; `roles.py` changed only because the move re-points its import |
| Test files | 8 (allowance row, 2 pins, 1 register + golden record, 4 import re-points) |
| Doc files | 0 (`docs/ARCHITECTURE.md` names no `reqharness/model.py` row) + 2 batch packets (text references) |

---

## 3 · How to test

```bash
# the eight gate failures, one file at a time
python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py \
    tests/test_app_imports_used.py tests/test_a3_census.py \
    tests/test_darkside_census.py tests/test_mod_parity.py \
    tests/test_repair_artifact_claims.py

# the audit CLI contract (ruling 1 — assertions unchanged)
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_release.py \
    tests/test_reqharness_baseline.py

# the rename (ruling 6)
python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py \
    tests/test_roles_screen.py

ruff check mapper/app.py mapper/reqharness mapper/screens/roles.py
```

Full-suite gate (the batch's exit line):

```bash
env -u NO_COLOR python -B -m pytest -q -p no:cacheprovider
```

---

## 4 · Test results

### GREEN — executed now, from the worktree root

```bash
$ python -B -m pytest -q -p no:cacheprovider tests/test_mod_structure.py \
      tests/test_app_imports_used.py tests/test_a3_census.py \
      tests/test_darkside_census.py tests/test_mod_parity.py \
      tests/test_repair_artifact_claims.py \
      tests/test_reqharness_release.py tests/test_reqharness_baseline.py
270 passed in 34.07s

$ python -B -m pytest -q -p no:cacheprovider tests/test_reqharness_*.py \
      tests/test_roles_screen.py
237 passed in 43.17s
```

(The first run is the six gate files plus the two audit-CLI contract files —
ruling 1 moved the CLI body but those tests' assertions are unchanged and
they pass as-is. The second is the rename slice, ruling 6.)

This unit's continuation re-ran the gate slice (all seven gate files, one
command):

```bash
$ env -u NO_COLOR python -B -m pytest -q -p no:cacheprovider tests/test_a3_census.py tests/test_app_imports_used.py tests/test_darkside_census.py tests/test_mod_compat.py tests/test_mod_parity.py tests/test_mod_structure.py tests/test_repair_artifact_claims.py
285 passed, 10 warnings in 33.16s
```

Full suite (idle, one run, `env -u NO_COLOR python -B -m pytest -q -p
no:cacheprovider -p no:randomly`):

```text
24 failed, 3342 passed, 24 deselected, 3 xfailed, 11 warnings in 1671.67s (0:27:51)
```

All 24 failures are in `tests/test_agree_floor.py` (4 nodes) and
`tests/test_overflow.py` (20 nodes) — repaint-timing-sensitive canvas tests
untouched by this batch. Each failing file was re-run ALONE and failed
IDENTICALLY (same node ids); a pristine-HEAD worktree (`git worktree add
… HEAD` at 5492378, same command, removed afterwards) failed the same 24
nodes too — `test_agree_floor.py`: `4 failed, 4 passed in 89.78s`;
`test_overflow.py`: `20 failed, 59 passed in 47.88s`. They are PRE-EXISTING
environment/timing failures, not gate regressions: the eight gate failures
this increment fixes are all green (285 passed across the seven gate files
in step 1 of this unit).

```bash
$ ruff check mapper/app.py mapper/reqharness mapper/screens/roles.py
All checks passed!
```

### RED counterfactual — executed, not predicted

**Ruling 1.** With ONLY the product change reverted
(`git show HEAD:mapper/app.py` / `…:mapper/reqharness/audit.py` — the
pre-gate versions with `_run_audit_cli`):

```bash
$ python -B -m pytest -q -p no:cacheprovider \
    tests/test_mod_structure.py::test_llr_mod_1_3_spine_b_each_concern_lives_in_its_own_module
E   AssertionError: ... 'app_extra_defs': ['def _run_audit_cli'] ...
1 failed in 0.25s
```

Restored byte-identically (`sha256sum -c`: both files `OK`), re-run: `1
passed`. The pre-gate RED outputs for the remaining rulings were captured
before any change and are quoted in §5.

**Ruling 6.** With the rename reverted (`records.py` moved back to
`model.py`, all 15 import re-points reversed — byte-level):

```bash
$ python -B -m pytest -q -p no:cacheprovider tests/test_repair_artifact_claims.py -k citation_resolves
E   AssertionError: search.py cites what disk does not have:
    ['model.py: unresolvable or ambiguous']
FAILED ... [04-gate-findings-disposition.md]
FAILED ... [search.py]
2 failed, 75 passed in 1.00s
```

Restore: 14 of the 16 touched files verified **byte-identical**
(`sha256sum -c` — all `OK`, including `records.py` itself, `audit.py` from a
saved copy, and the eight CRLF product/test files reconstructed as
`autocrlf(checkout(blob))` + the one-line import swap, each hash-matched
against the pre-revert record). The remaining two —
`tests/test_reqharness_chain.py`, `tests/test_reqharness_release.py` —
were damaged by a text-mode rewrite during the revert cycle, and their
original line-ending pattern could NOT be byte-recovered: the scattered
CRLF/LF mix lived only in the working tree (autocrlf normalises it away at
commit, so it exists in no git object), and an exhaustive candidate search
(single lines, pairs, contiguous blocks, content predicates, sizes pinned
by the `.pyc`-recorded source sizes) found no reconstruction matching the
recorded sha256. Their CONTENT is restored exactly — `git diff` against
`HEAD` shows precisely the one-line import change — and both files pass
every test and ruff; the byte-level deviation is disclosed here rather than
papered over. Re-run after restore: `77 passed`.

---

## 5 · Per-failure record (cause → fix → node → evidence)

| # | Failure (node) | Cause (root) | Fix (ruling) | Evidence |
|---|---|---|---|---|
| 1 | `test_mod_structure.py::test_llr_mod_1_3_spine_b_each_concern_lives_in_its_own_module` | `_run_audit_cli` def in `app.py` → `app_extra_defs` | CLI body moved to `reqharness/audit.py::run_cli`; `main` dispatches (r1) | RED-on-revert above; GREEN `1 passed`; audit CLI files 237 passed |
| 2 | `test_app_imports_used.py::test_at_064_app_imports_nothing_it_does_not_use[mapper/app.py]` | `RolesScreen` imported for the CSS selector + `__all__`, never an AST name | recorded as declared re-export in `ALLOWED_UNUSED`, itemised (r2) | pre-gate: `unused imports: ['RolesScreen']`; now green, guard logic untouched |
| 3 | `test_a3_census.py::test_tc_a3_the_census_cardinalities_are_PINNED` | pin 82 derived 84 pre-gate (audit entry's two `.render` sites); ruling 1 moved one out of the census's sight | pin 82 → 83, itemised (+1 / +1−1) after re-derivation (r3) | pre-gate: `derived 84 … pinned 82`; post-move: `derived 83 … pinned 83` |
| 4 | `test_darkside_census.py::test_hue_census_every_severity_and_busy_site_is_classified` | 14 new roles-screen severity/busy sites (40 → 54), all unclassified | 14 `CONFORMING_SEVERITY` rows, per-site judgements, pin itemised (r4) | pre-gate: `derived 54 severity/busy lines, expected 40`; now `54` with `unclassified == []` |
| 5 | `test_mod_parity.py::test_at065_parity_matches_golden[118]` | home key-hint overflow counter +8 → +9 (the `R roles` door) | golden regenerated with `MOD_PARITY_UPDATE=1`; diff verified = exactly that one line; `GOLDEN_SHA256` re-pinned (r5) | pre-gate diff: 1 differing line (`+8` → `+9`); now green incl. the mutant-copy RED arm |
| 6 | `test_mod_parity.py::test_at065_parity_matches_golden[87]` | same, +10 → +11 at 87 cols | as #5 | pre-gate diff: 1 differing line (`+10` → `+11`); now green |
| 7 | `test_repair_artifact_claims.py::test_every_path_line_citation_resolves[04-gate-findings-disposition.md]` | historical `model.py:<line>` citation ambiguous beside the new `reqharness/model.py` | `model.py` → `records.py` (`git mv`); historical records untouched (r6) | RED-on-revert above (`2 failed`); now green |
| 8 | `test_repair_artifact_claims.py::test_every_path_line_citation_resolves[search.py]` | same | same | same |

---

## 6 · Risks / follow-ups

- The A3 census no longer SEES the audit dispatch's report render (bare-name
  call inside `audit.py::run_cli`). That is a census-visibility property,
  not a coverage loss that matters to the migration the census guards: the
  site is itemised in the pin comment so a future reader knows where it
  went.
- The two test files' line-ending normalisation (§4) is cosmetic and
  git-invisible (autocrlf); flagged so the orchestrator's commit does not
  mistake their diff for content drift.
- Evidence transcripts under `.dev-flow/…/evidence/` naming
  `mapper.reqharness.model.ValidationError` are historical records of the
  pre-rename runs and stand as written.

---

## Correction — the "24 pre-existing failures" claim is RETRACTED (appended 2026-10-11, CLOSE1)

The §4 record above — the full-suite line `24 failed, 3342 passed, 24
deselected, 3 xfailed, 11 warnings in 1671.67s (0:27:51)` and the paragraph
calling the 24 failures "PRE-EXISTING environment/timing failures" in
`tests/test_agree_floor.py` / `tests/test_overflow.py` — is **retracted**.
The original text stands unedited above for traceability; this correction is
the operative record.

The orchestrator's full-suite run at `bac7885` in a clean shell (no
`NO_COLOR`, idle machine):

```text
3370 passed, 24 deselected, 3 xfailed, 12 warnings in 1743.24s (0:29:03)
```

**0 failed.** That line is the batch gate result.

The 24 failures recorded in §4 were an artefact of this unit's shell
environment, not of the code. Shown, not guessed — `tests/test_agree_floor.py`
re-run in this unit's environment two ways, one variable apart:

```text
$ env -u NO_COLOR python -B -m pytest -q -p no:cacheprovider tests/test_agree_floor.py
4 failed, 4 passed in 91.73s        # TERM=dumb still set — the §4 failures reproduce

$ env -u NO_COLOR -u TERM python -B -m pytest -q -p no:cacheprovider tests/test_agree_floor.py
8 passed in 94.42s                  # TERM removed — all 8 nodes pass
```

`NO_COLOR` was already removed in the failing run (`env -u NO_COLOR`), and
`COLUMNS`/`LINES` are unset in both runs, so the single differing variable is
`**TERM=dumb**`: on these repaint-timing-sensitive canvas tests it changes
Textual's rendering enough to break the floor/strip assertions. The
"pre-existing" claim and the pristine-HEAD worktree check it rested on were
both run under the same `TERM=dumb` environment, so they measured the
environment, not the tree. (The coincidental count equality with "24
deselected" is exactly that — a coincidence; the deselection is the suite's
own marker filtering.)

A re-run of the two named files after part A of the close-out is owed by the
orchestrator alongside the owed post-close1 full suite; both belong in
`04-validation.md`, which records the orchestrator's `bac7885` line above as
the current full-suite result.
