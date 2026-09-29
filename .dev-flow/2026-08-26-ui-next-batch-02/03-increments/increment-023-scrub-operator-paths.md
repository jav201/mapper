# Increment 023 — Inc-SCRUB · remove the operator's real account name from every tracked file

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `023` — Inc-SCRUB: repo hygiene, no product change |
| Agent | `software-dev` |
| Date | 2026-09-29 |
| Authority | Operator, verbatim: *"Limpia el usuario de los registros en un incremento propio."* Closes the identity half of `B-22` |
| Starting state | `feat/ui-next-batch-02` @ `037c733`, `git status --porcelain` clean |

Throughout this record the real Windows account name is written `<operator>` and never spelled,
per the increment's own instructions and per the requirement it discharges.

---

## 1 · What changed

Added `A-110` (`01-requirements.md`, amendment set 18): no file tracked by `git` may contain an
absolute user-profile path whose name segment is a real account, unless that segment is a declared
placeholder or fixture. Added a permanent guard test, `tests/test_no_operator_paths.py`, with two
independent arms (a hermetic allow-list check, and a backstop that reads the real account name from
`$USERNAME` at run time and searches for it literally). Then scrubbed every tracked file that
carried the real account name, replacing every occurrence with `<operator>`, byte-for-byte, with no
other edit. No product source file is touched. `BACKLOG.md`'s `B-22` row is annotated to record
that this increment closes the identity half.

## 2 · Files modified

- `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md` — `A-110` appended (amendment set 18);
  one illustrative path in that same new text corrected from a stray `<name>` placeholder to
  `<operator>` once the guard test caught it (see §4, GREEN pass).
- `tests/test_no_operator_paths.py` — new file, the guard.
- `.dev-flow/BACKLOG.md` — one line added to `B-22`'s Note cell.
- 70 tracked files scrubbed (substring replacement only) — table in §3.

## 3 · How to test

```bash
cd C:\Users\<operator>\Github\mapper
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
python -m pytest tests/test_no_operator_paths.py -v
python -m pytest -q
python -m ruff check .
python -m pytest tests/test_fold.py -q
```

## 4 · Test results

### RED, before the scrub (guard test added first, both arms driven against the un-scrubbed tree)

```
tests/test_no_operator_paths.py::test_a110_no_undeclared_user_profile_path_in_any_tracked_file FAILED
tests/test_no_operator_paths.py::test_a110_the_real_operator_username_appears_nowhere FAILED

E   AssertionError: 249 tracked line(s) carry a user-profile path segment that is not in
    ALLOWED_PATH_SEGMENTS (A-110): ... [truncated to 25 in the message; 249 total]
E   AssertionError: the real account name (read from $USERNAME, not printed here) appears in
    70 tracked file(s): ... [truncated to 25 in the message; 70 total]

2 failed in 0.41s
```

Committed at this point with both arms marked `xfail(strict=True, reason="scrub pending")`, so the
suite stayed green while the defect was real (commit `0031570`).

### GREEN, after the scrub

```
tests/test_no_operator_paths.py::test_a110_no_undeclared_user_profile_path_in_any_tracked_file PASSED
tests/test_no_operator_paths.py::test_a110_the_real_operator_username_appears_nowhere PASSED

2 passed in 0.29s
```

One follow-up RED→fix cycle happened inside this same GREEN pass: `A-110`'s own new prose
illustrated the path pattern with a template placeholder segment, spelled literally as angle
brackets around the word "name". That segment was never declared in `ALLOWED_PATH_SEGMENTS`, so arm
1 correctly caught its own author's text (`1 tracked line(s) ... -> '<name>'`) and it was corrected
to `<operator>` rather than added to the allow-list — the amendment should use the one placeholder
this increment actually introduces, not mint a second one.

### Full default lane, after the scrub

```
1295 passed, 20 deselected, 3 xfailed in 837.80s (0:13:57)
```

Reconciled: baseline at `037c733` is 1293 passed, 20 deselected, 3 xfailed, 0 failed. `+2` passed
here is exactly the two new `A-110` guard nodes; every other count is unchanged, and 0 failed. The
wall clock (~14 min vs. the ~105 s the batch's baseline was measured at) is this sandbox's own
resource ceiling, not a regression — no test's own logic changed. FLAKE-1
(`test_llr_cnv_3_1_the_parent_walk_maps_a_nested_widget_to_its_region`) is a known intermittent;
not observed this run.

### `tests/test_fold.py` (explicitly requested)

```
19 passed, 3 xfailed in 30.49s
```

### `ruff check .`

```
Found 27 errors.
```

Matches the baseline (27) exactly — the new test file and the scrub introduce no new lint findings.

## 5 · Risks

- **History still carries the identity.** Stated plainly in §7 (limit).
- **`ALLOWED_PATH_SEGMENTS` is a hand-maintained allow-list.** A future contributor could widen it
  carelessly to hide a real leak — this is exactly what arm 2 (the backstop) exists to catch, and
  the mutation battery in §6 demonstrates that arm 2 still fires even when arm 1's list is widened
  to accept anything.
- **Session UUIDs (`B-22`'s other half) are untouched.** Out of scope for this increment; the
  BACKLOG note says so explicitly.

## 6 · Pending items

- `B-22`'s session-UUID half remains open.
- History scrub / force-push to `origin` is not authorized and not attempted.

## 7 · Explicit limit (stated per instructions)

**The username remains in git HISTORY on the public remote (`origin`, including `master`).**
Removing it there would need a history rewrite and a force push, which the operator has not
authorized. This increment scrubs the WORKING TREE only, as requested.

## Non-path occurrences, and how each was disposed of

The guard's path-pattern regex captures a bounded "name segment" after `Users\` / `Users/`. Twelve
of the 261 replaced occurrences did not sit inside a segment the regex's three declared spellings
recognise, but every one of them was still clearly the operator's identity, and all twelve were
scrubbed the same way (`<operator>`), never left alone:

1. **9 occurrences, 6 files** — a fourth, DASH-mangled spelling of the same path:
   `C--Users-<operator>-clde`, the literal name Claude's own scratch-directory convention gives a
   temp folder for `C:\Users\<operator>\clde` (path separators replaced with `-`). Not one of the
   three spellings `A-110`'s guard pattern matches, but unambiguously the same identity, encoded
   differently. Files: `mutation-battery-inc3.txt`, `mutation-battery-inc3-v1-prefix.txt`,
   `mutation-battery-inc4.txt`, `mutation-battery-inc4-supplement.txt`,
   `mutation-battery-inc4-supplement-2.txt`, `increment-003-security-review.md`,
   `increment-016-confirm-security-review.md`, `increment-017-ux-F7-AT058.md`.
2. **1 occurrence** — `increment-004a-security-confirmation-2.md`: a security checklist line reading
   *"Scan for `` `<operator>` ``, `` `javgranados` ``, `` `C:\Users` ``, `` `api_key` ``, ..."* — the
   account name written as a bare word naming what to grep for, not inside a path at all. Clearly
   identity; scrubbed.
3. **2 occurrences** — `increment-004a-security-review.md`: two security-review scan-result lines
   of the form *"contains `` `<operator>` ``? False"*, reporting that a rendered frame does NOT
   contain the account name. Clearly identity (the very thing being checked for); scrubbed.

Arm 2 of the guard test (the backstop) does not care whether a hit is inside a path or not — it
would have caught all twelve of these regardless of how they are classified above.

## Mutant table

Harness kept out of the repo (`C:\Users\<operator>\clde\scrub-inc023\mutation_battery.py`), driving
the REAL guard functions (`scan_user_profile_paths`, `undeclared_hits`, `tracked_files`) imported
from `tests/test_no_operator_paths.py`, over synthetic scratch git repos built in a temp directory —
never over the tracked tree.

| # | Mutant | Targets | Method | Result |
|---|---|---|---|---|
| 1 | Inject a real-looking, undeclared profile path into a scratch tracked copy (drive letter, `Users`, then the name segment `someone`, then a file) | Arm 1 (hermetic allow-list check) | Ran the unmodified `undeclared_hits` against the scratch repo | **KILLED** — flags `segment == 'someone'`; RED as required |
| 2 | Widen the allow-list to accept ANY name, simulating a future edit that neuters arm 1; plant the real username in a scratch tracked copy | Arm 2 (backstop) | Arm 1 under the widened list finds nothing wrong; arm 2 (which never reads the allow-list) still scans the same scratch repo for the literal username | **KILLED** — arm 2 still reports the offending file even though arm 1 was blinded |
| — | Negative control: a scratch repo carrying only declared placeholders | Arm 1 | Ran `undeclared_hits` against a file built from every key in `ALLOWED_PATH_SEGMENTS` | **GREEN**, correctly — no false positive on a clean tree |

Transcript (username never printed by the harness; the harness reads it from `$USERNAME` and only
ever prints filenames or the substituted segment):

```
=== MUTANT-1: undeclared real-looking path injected into a scratch tracked copy ===
undeclared_hits found: [Hit(path='note.md', line_no=1, segment='someone')]
MUTANT-1 KILLED (RED as expected): arm 1 flags the undeclared segment 'someone'
=== MUTANT-2: allow-list widened to accept ANY name; backstop still catches the real username ===
arm 1 under the WIDENED allow-list finds: []
arm 2 (ignores the allow-list entirely) finds: ['note.md']
MUTANT-2 KILLED (RED as expected): arm 2 still catches the real username even though the widened
allow-list blinded arm 1
=== NEGATIVE CONTROL: a scratch repo carrying only declared placeholders stays green ===
undeclared_hits found: []
negative control GREEN as expected: only declared placeholders present

ALL MUTANTS KILLED, NEGATIVE CONTROL GREEN.
```

## Scrub table (file → occurrences replaced; sha256 before/after, truncated to 12 hex chars)

| File | Occurrences | sha256 before | sha256 after |
|---|---|---|---|
| `.dev-flow/2026-08-18-batch-01/PLAN.md` | 1 | `2de11bcfe736...` | `5df6e8777a73...` |
| `.dev-flow/2026-08-25-ui-next-batch-01/01-requirements.md` | 1 | `91519f04e34a...` | `167e886a8efb...` |
| `.dev-flow/2026-08-25-ui-next-batch-01/02b-security-review.md` | 8 | `4b5c7f319f7a...` | `fb9a01967255...` |
| `.dev-flow/2026-08-25-ui-next-batch-01/04b-security-signoff.md` | 4 | `e612fe27703d...` | `bf6d9c958785...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/increment-001.md` | 1 | `7992f9500c3e...` | `912b871182c2...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/increment-002.md` | 2 | `9bf4ab87128b...` | `6d4310902e88...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/increment-002b.md` | 1 | `a7fb706349af...` | `b3b50a531c05...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/increment-003.md` | 1 | `d0ef3f1dd55d...` | `3bea89f0f4a9...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/increment-004.md` | 1 | `651bd1691016...` | `8423b6d9aa8e...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/mutation-battery-inc3-v1-prefix.txt` | 34 | `3faa8f3e977e...` | `ad58bbf66817...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/mutation-battery-inc3.txt` | 38 | `217c5b84c131...` | `ded7b46eee78...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/mutation-battery-inc4-supplement-2.txt` | 13 | `4257e62b479c...` | `3ee4ba74f9fb...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/mutation-battery-inc4-supplement.txt` | 13 | `f80814639365...` | `3e9b100d864f...` |
| `.dev-flow/2026-08-26-repair-batch/03-increments/mutation-battery-inc4.txt` | 8 | `b0333c98c2a8...` | `bb77e1a19626...` |
| `.dev-flow/2026-08-26-repair-batch/04-security-signoff.md` | 3 | `7689598c0660...` | `c43ec5df13e4...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md` | 2 | `2bd7212b36cf...` | `12cdff918202...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/01d-unpark-measurements.md` | 1 | `466094141ab6...` | `077adddc42bc...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/02k-inc4-viewstate-architect.md` | 1 | `f1d917d0e354...` | `28e7c945ca3a...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/02m-inc-b55-painted-ids-architect.md` | 2 | `31e753becb64...` | `c3c21a801038...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/02n-at056-at057-qa.md` | 2 | `f9b09f84f0f8...` | `671623c337e3...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/02o-b55a-mechanism-diagnostic.md` | 5 | `62a3fcbf4da6...` | `9638133e87c7...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-003-code-review-confirmation.md` | 1 | `6591863eaff9...` | `a8fb3e357a7f...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-003-code-review.md` | 1 | `50b39fa7b8ba...` | `dc4d534907a0...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-003-security-confirmation.md` | 2 | `ff89be5d41a1...` | `ada7b42a52a6...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-003-security-pass3.md` | 1 | `16b385292ae3...` | `ddd4f60a3b38...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-003-security-review.md` | 2 | `72591ccab0b5...` | `13c5561bad67...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-004a-security-confirmation-2.md` | 1 | `6a39fd69dfe0...` | `df724a9e4c5a...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-004a-security-review.md` | 3 | `5a6e35764283...` | `4e8ea2d201f6...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-004a.md` | 1 | `bb7ea76f35cd...` | `c18ee3346706...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-004b-code-review.md` | 1 | `57b15a92c7dc...` | `9eb42d92777e...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-004c-code-review-pass3.md` | 1 | `6c6cf185875e...` | `2bb097a40e40...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-005-code-review-confirmation.md` | 2 | `09a9167b9c47...` | `21f9d3a9a3d2...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-005-code-review-final.md` | 1 | `e9fdc9d47bef...` | `b19adbd08cea...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-005-code-review-pass3.md` | 1 | `85ce212a5c44...` | `5b6d90497f12...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-005-code-review-pass4.md` | 1 | `803eef0594f5...` | `735b77c06f05...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-006-w1-review.md` | 1 | `7887827420e3...` | `3b5781c81812...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-006-w1-review2.md` | 1 | `dd9fec4ef04d...` | `1ad771470101...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-007-strips-confirmation-2.md` | 1 | `d8aecce0a69a...` | `b1e81da1103b...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-008-crumb-code-review.md` | 1 | `f7bb352777fb...` | `3527c9819239...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-008-crumb-security-review.md` | 2 | `cb607bd4e8cc...` | `4b2b0522a32b...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-009-b55a-security-review.md` | 1 | `ae00614ce1d0...` | `48129031ce86...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-010-b55b-security-review.md` | 2 | `0c828d73fd60...` | `40e30fd64605...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-012-repair-se-security-review.md` | 2 | `35c4dd058218...` | `b261c38d84fb...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-012-repair-se.md` | 1 | `e2c7eb102404...` | `6567e7f5d6cc...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-013-sbc-defect2.md` | 2 | `1f5ae259de6c...` | `a539f6dbcf08...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-013-sbc-fold-review.md` | 1 | `fba4ab4f63c1...` | `9acae1261855...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-014-sd-code-review-round2.md` | 3 | `fdc272ed053f...` | `3f34218a94af...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-014-sd-code-review.md` | 10 | `cf17797fbe6a...` | `fb24b2b081f3...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-014-sd-security-review.md` | 1 | `3fb5ad85c7cc...` | `91f5caedcf0b...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-015-confirm-code-review.md` | 2 | `7e6979cdef64...` | `27f646af823a...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-015-confirm-security-review.md` | 11 | `7b6650e33721...` | `fae38a0cd209...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-015-confirm.md` | 4 | `e7046db719bf...` | `6dbf94d3a38b...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-016-confirm-code-review.md` | 2 | `6f6ff62d3b27...` | `87cbf0378a59...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-016-confirm-reruled.md` | 2 | `d5fea082f77e...` | `ccc366fc198c...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-016-confirm-security-review.md` | 4 | `af4fdf1fb272...` | `082178302432...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-017-F6-second-reader.md` | 1 | `8bbb7ca73030...` | `68124c455747...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-017-code-review.md` | 1 | `2807fbbe9fed...` | `93c7e8563dcf...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-017-qa-F3.md` | 1 | `187195a77291...` | `a63951707e78...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-017-rulings.md` | 2 | `369bae1aeeac...` | `8d06f5770c3c...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-017-ux-F7-AT058.md` | 5 | `29a3e828a5b3...` | `74f80c703c4e...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-018-item3-pickups.md` | 1 | `eea4373b7642...` | `ce5a33d19126...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/increment-022-inc8-legend.md` | 18 | `63e46aacdca1...` | `2a9aebdbd02c...` |
| `.dev-flow/2026-08-26-ui-next-batch-02/HANDOFF-2026-09-24.md` | 4 | `8c5632f98ac7...` | `4d8ee448ba05...` |
| `.dev-flow/2026-08-27-repair-batch-02/03-increments/increment-001.md` | 1 | `8a784eceec7d...` | `cce98a10cbaf...` |
| `.dev-flow/2026-08-27-repair-batch-02/04-qa-adversarial.md` | 2 | `ea66b4621473...` | `2e5dd3973543...` |
| `.dev-flow/2026-08-27-repair-batch-02/04-security-review.md` | 1 | `89e743d15cb3...` | `2bbdfb7396d8...` |
| `.dev-flow/state.json` | 5 | `bbc454df1d4b...` | `474aad5db717...` |
| `HANDOFF.md` | 1 | `9d1db7c97529...` | `a437a69ca22a...` |
| `handoff-ui-redesign.md` | 1 | `5444fb89062b...` | `003df145067d...` |
| `prototypes/ui_components/verify.cjs` | 2 | `381643446f50...` | `9fc0b015776d...` |

**Totals: 70 files, 261 occurrences replaced.** `state.json` re-checked with `json.loads` before and
after: still valid JSON, and the parsed structure is identical to the original except for the
substituted substrings (verified programmatically, not by inspection).
