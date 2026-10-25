# Code Review — Increment 002 (lane L1, US-Q1-001 / AT-108)

Role: `code-reviewer` (independent Phase-3 increment gate, batch `2026-10-23-hygiene-batch`).
Reviewer did not author this increment. Read-only toward the diff; the two mutant arms below
were restored byte-exact and hash-verified.

## Scope reviewed

- Commit: `78bba97` (`feat(app): NO_COLOR neutralised in MapperApp.__init__`), full diff read.
- Source: `mapper/app.py` (+5 lines: `import os`, 3-line comment, `os.environ.pop("NO_COLOR", None)` at :254, before `super().__init__()`).
- Test: `tests/test_colour_always_on.py` (new, 2 nodes).
- Packet: `.dev-flow/2026-10-23-hygiene-batch/03-increments/increment-002.md`.
- Requirement clauses read in `01-requirements.md`: US-Q1-001 (:85, :91-114), HLR-Q1.1 (:213-227), LLR-Q1.1.1 (:323-332).

## Checks performed

### Requirement conformance

LLR-Q1.1.1 demands: remove `NO_COLOR` from the process environment before invoking the Textual
base constructor, no `--no-color` opt-out. The diff does exactly that and nothing more — one pop
with default, placed before `super().__init__()` (`mapper/app.py:254`), signature untouched, no
flag added. HLR-Q1.1's acceptance (AT-108: byte-equal rendering with/without the variable,
observed headless through `run_test()`) is realized by the black-box arm. No scope creep.

### Environment-subtlety check (assignment-specific)

Harness convention is `env -u NO_COLOR -u TERM`, which scrubs the very variable under test.
Verified the tests are NOT vacuous under it: both tests set `NO_COLOR=1` themselves via
`monkeypatch.setenv` (`tests/test_colour_always_on.py:41,55`), so the scrubbed harness env is
irrelevant. The RED transcript proves it: on the base tree the unit arm fails with `NO_COLOR`
still present in `os.environ` after construction, and the black-box arm fails with unequal
frames (`At index 38 diff: b'7' != b'1'`). Genuine neutralisation coverage.

### Reviewer-chosen mutant arms (not the packet's battery)

Target: `mapper/app.py`, baseline sha256 `7ec4dba61dc8ec8d1ffc20dd62a3082001e6ca988e8592b723153b6b3d7c2152`
(matches the packet's restore digest). Run: `env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider --color=no tests/test_colour_always_on.py`. Baseline before mutation: 2 passed, exit 0.

| Arm | Edit | Hash after edit | Result | Restore |
|---|---|---|---|---|
| R1 (order swap) | pop moved AFTER `super().__init__()` | `4e46c510aff17a45754cc8fc7e775d7135fe601ce6bdd9ef495a743b92773ce2` | KILLED — 2 failed: unit arm RED on the `Monochrome` filter assertion (env assertion still passed — the filter check is the discriminating negative); black-box RED on unequal frames | hash back to `7ec4dba6…` — RESTORE PROVEN |
| R2 (no default) | `os.environ.pop("NO_COLOR", None)` → `os.environ.pop("NO_COLOR")` | `994982fa8d7df09c9186d891e74b7d7862b8db44813c40c707d474b7d9e27012` | KILLED — 1 failed / 1 passed: black-box arm RED with `KeyError` in the absent regime (proves the default arg is load-bearing); unit arm passed, confirming regime coverage lives in the right node | hash back to `7ec4dba6…` — RESTORE PROVEN |

Both reviewer mutants KILLED. `git status` clean afterward (only a pre-existing untracked
evidence file from another station, untouched by this review).

### Evidence digest audit

| File | Packet sha256 | Recomputed | Match |
|---|---|---|---|
| `evidence/l1-red-2026-10-23.txt` | `9486c32c…ed52` | `9486c32c6784991cff5b4d0718e81407c225f2f4091f98785478ed85bc5bed52` | ✓ |
| `evidence/l1-green-2026-10-23.txt` | `21d67a69…0a8d` | `21d67a695fdfda0b986f02dffa316479405743692191fac1319d837969ee0a8d` | ✓ |
| `evidence/l1-move-aside-2026-10-23.txt` | `e90af6ec…02f5` | `e90af6ec9965c30fa7c9d1b8e3580bf1b4350a8a158e1973f110734c98ca02f5` | ✓ |
| `evidence/l1-mutation-battery-2026-10-23.txt` | `4995c97b…e6ce` | `4995c97b09e25ad732a7e2ca3654dc3278f29f5ef0f0f72f546917de7b20e6ce` | ✓ |
| `evidence/mutate_l1.py` | `18c88416…0edbda` | `18c88416c361ee0150e2acbc85782089c3fae7d8a77426fc94a02176f00edbda` | ✓ |

Transcript reads:
- RED (`l1-red`): genuine failure — 2 failed, exit 1, assertion output consistent with the
  packet's claims (env var present post-construction; frames unequal at byte 38).
- GREEN (`l1-green`): one complete run, 2 passed, exit 0.
- Move-aside (`l1-move-aside`): rename-out-of-tree (not stash), both holding modules RED at
  collection with `ModuleNotFoundError: No module named 'mapper.app'`, exit 2; restore digest
  `7ec4dba6…` equals the current on-disk bytes of `mapper/app.py` (recomputed this review).
- Battery (`l1-mutation-battery`): 2 arms, both `RED (KILLED)`, per-arm before/after digests
  identical (`7ec4dba6…`), `arms: 2 bad: 0`, runner exit 0. Runner `mutate_l1.py` inspected:
  anchor-count self-check, edit-applied check, restore-proof check, and exit-code-to-verdict
  mapping (1=KILLED, 0=SURVIVED, else CRASH/BAD) are all sound.
- Note: the commit message of `78bba97` cites pre-redaction digests (`039113f8…` etc.); the
  later redaction commit `b202856` re-pinned every citation, and the packet carries the current
  (matching) digests. Commit messages are immutable history — not a packet defect.

### Budget and trace checks

- Source-file budget: 1 source file (`mapper/app.py`) — 1/4, clean; no ⚠ statement owed. ✓
- Reverse trace (V59): `mapper/app.py` → LLR-Q1.1.1; `tests/test_colour_always_on.py` →
  LLR-Q1.1.1, HLR-Q1.1 — all ids exist in `01-requirements.md`. ✓
- Byte-pinned must-stay-green spot check: `env -u NO_COLOR -u TERM python -m pytest -q -p no:cacheprovider --color=no tests/test_help_scope.py` → 52 passed, matching the packet claim; the ambient-NO_COLOR fixture (:84-94) and legend pin (:250-274) are present as cited.

### Lens pass (code-reviewer)

- Correctness: pop-with-default before `super()` is exception-safe in all three regimes
  (set / absent / set-empty — the pop is value-independent). Global env mutation is a real
  side effect, but it is the mandated mechanism (ruling R3) and is declared in packet §5 risks.
- Simplicity: two lines; no abstraction, no speculative generality.
- Reuse/duplication: no existing util to reuse; stdlib call is the right size.
- Convention-conformance: comment cites the LLR + ruling in the file's established comment
  idiom (cf. `mapper/app.py:243-247,258-264`); `import os` in the stdlib group; test module
  docstring names requirement ids and the reddening mutant, matching repo test conventions.
- Tests-encode-intent: both docstrings name the requirement and the failure mode; the unit
  arm carries a discriminating negative (the `Monochrome` filter assertion — proven
  discriminating by reviewer mutant R1, where the env assertion alone would have passed).

## Findings

### F1 — declared boundary regime `NO_COLOR=""` (set-empty) has no test arm  [Severity: MINOR]
- **What:** LLR-Q1.1.1's boundary catalog (`01-requirements.md:332`) declares ☑ boundary
  "var set / absent / **set-empty**", and HLR-Q1.1 (:226) declares ☑ invalid "variable set to
  empty string / arbitrary value", but no test constructs the app with `NO_COLOR=""` or an
  arbitrary value — only `"1"` and absent.
- **Where:** `tests/test_colour_always_on.py:41,55` (the only two setenv sites).
- **Why it matters:** low — the mechanism (`os.environ.pop("NO_COLOR", None)`) is value-independent,
  so the set-empty regime is behaviorally identical to set; but the declared catalog says the
  regime was considered, and an arm would cost one line and close the declared-vs-tested gap.
- **Suggested fix:** parametrize the unit arm, e.g.
  `@pytest.mark.parametrize("value", ["1", "", "anything"])` over
  `monkeypatch.setenv("NO_COLOR", value)`, keeping both existing assertions.

No other findings. The increment is otherwise clean.

## Verdict

- brief form: **approve-with-nits** (one MINOR open; nothing blocking)
- record form: **OK-with-notes**

## Evidence states

- Diff read in full: executed (`mapper/app.py:250-255`, full `git show 78bba97`).
- Correctness pass: executed (R1/R2 mutants probe ordering and default-arg edge paths).
- Simplicity pass: executed — no premature abstraction.
- Reuse/duplication pass: executed — no existing util; census in packet §4 confirms 5 NO_COLOR sites, all accounted for.
- Tests reviewed for intent: executed — discriminating negative proven live (mutant R1).
- Evidence digests: executed — 5/5 match; transcripts consistent.
- Budget/trace: executed — 1/4 source; V59 ids resolve.
- F1: MINOR, recommended (not blocking; no HIGH open, so no applied-and-verified gate owed).

## Proposed §4b `Independent review` cell text

`code-reviewer — OK-with-notes, 0 BLOCKER / 0 MAJOR / 1 MINOR · approve-with-nits: neutralisation + both arms verified by two reviewer-chosen mutants (order-swap, no-default — both KILLED, restores hash-proven), 5/5 evidence digests match, RED/move-aside/GREEN transcripts genuine; F1 MINOR — declared set-empty boundary regime has no test arm; report .dev-flow/2026-10-23-hygiene-batch/evidence/review-inc002.md`
