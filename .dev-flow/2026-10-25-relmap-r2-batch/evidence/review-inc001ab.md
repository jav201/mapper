# Independent Review — Increments 001a + 001b (trunk, text leaf)

| Field | Value |
|---|---|
| Reviewer | code-reviewer + security-reviewer lenses (independent; authored none of it) |
| Batch / commits | `2026-10-25-relmap-r2-batch` · Inc-1a `968c2c0` · Inc-1b `01e87b5` |
| Packets | `03-increments/increment-001a.md`, `-001b.md` |
| Scope (SOURCE) | Inc-1a: `mapper/relmap/text.py` (new), `model.py`, `descriptor.py`, `audit.py` (4/4) · Inc-1b: `mapper/relmap/adapter.py` (1/4) |
| Verdict | **approve-with-nits** |

## Verdict

**approve-with-nits** — no BLOCKER, no MAJOR. Two MINOR recommendations (below); both are
hardening notes, not corrections of anything wrong in the increments. Every claim the
packets make that I could re-execute, I re-executed, and it held.

## What I re-ran myself (not the author's word)

1. **Commissioned test command** (after proving `mapper.__file__` resolves inside the
   worktree — it did): `tests/test_relmap_*.py tests/test_prescan_refusal_goldens.py`
   → **417 passed, 2 skipped, 0 failed**.
2. **Byte-identity probe (LLR-RVT.1.3 / AT-151)** — the probe script is not committed, so
   I reconstructed it in a scratch dir outside the worktree from the recorded dump spec
   (`cut` over empty/119/120/121/1M/accent/newline inputs, `refusal_line` over K1/K3/K5
   ±limit/long/accent names, the K2 descriptor refusal over a fixture, and the
   `structure_lines` surface over an empty fixture repo), then ran the *same* script with
   `PYTHONPATH` pointed at (a) the current Inc-1b tree and (b) the base commit `7649f85`
   (Inc-1a parent, extracted via `git archive`). Both dumps were **byte-identical** to the
   recorded transcript and both hash to the base hash
   `b7ff2e38aeb79a0629bcf36bc09cc7c231fa25110fe32d59b14991575d2d5a07`. The probe hash is
   content-derived: any wording drift moves it.
3. **Evidence re-hash** — all 13 `p3-inc1a-*`/`p3-inc1b-*` transcripts re-hash to the
   digests cited in the packets (spot-verified every line of the tables; transcript
   totals match: 155/672/103/762-passed guard lines, M-RVT KILLED lines with restore
   digests, RED exit codes).
4. **Author restore digests match the tree** — `model.py` `f49ca449…ed40a`,
   `adapter.py` `e163a9fa…36756`, `test_relmap_descriptor.py` `7b8e03a6…579c9`,
   `text.py` `88c81769…cc2` (also my own restore target, below).
5. **Single definition site, stdlib-only leaf** — `grep` over `mapper/` finds `def cut` /
   `DISPLAY_MAX =` / `def refusal_line` only in `mapper/relmap/text.py`; zero old-path
   import readers anywhere in `mapper/`; `text.py` imports nothing but `__future__`
   (confirmed by reading the file and by the AST arm
   `test_the_leaf_imports_nothing`).
6. **Privacy scan** — no account name, home path, email, or handle in any Inc-1
   transcript (redaction to `<user>` held).

## Reviewer-owned mutants (post-mortem control C-2)

Three mutants of my own, applied to `mapper/relmap/text.py` only, each run → restored →
sha256-verified against the pre-mutation digest `88c81769…cc2` (MATCH after every restore;
no other file touched; Inc-2 files untouched):

| Mutant | Change | Result | Restore |
|---|---|---|---|
| R-1 (reviewer) | `K5_CAUSE` reworded to `"over the byte limit"` (simulates a future K5 reword in the cause table without touching the leaf — the B-151 risk) | `test_refusal_line_reproduces_the_r1_contract` RED — the limit render silently degrades to the plain cause text. KILLED: the R1 contract guard fires, and it fires at the exact drift the packets' risk section predicts | sha256 MATCH |
| R-2 (reviewer) | `DISPLAY_MAX` 120 → 121 (boundary off-by-one) | `test_cut_reproduces_the_r1_contract` RED (KILLED) | sha256 MATCH |
| R-3 (reviewer) | `refusal_line` renders the base name uncut (`{base_name}` instead of `{cut(base_name)}`) | 6 nodes RED across `test_relmap_text.py`, `test_relmap_audit.py::test_refusal_line_hostile_name`, and the R1 `test_relmap_descriptor.py` hostile-base-name arms — the emitted bytes moved, which is exactly what LLR-RVT.1.3 guards. KILLED | sha256 MATCH |

All three mutants stayed inside the Inc-1 file set; the tree was left at the committed
state (`git status` shows only the concurrent Inc-2 session's in-progress files).

## Findings

### N-1 — K5 literal: pin it directly, not only through rendered bytes  [MINOR]
- **What:** `mapper/relmap/text.py:17` duplicates the `CAUSE["K5"]` value
  (`mapper/relmap/descriptor.py:39`). No assertion anywhere states
  `K5_CAUSE == CAUSE["K5"]`; the only guards are the rendered-bytes tests.
- **Where:** `mapper/relmap/text.py:17`, `mapper/relmap/descriptor.py:39`,
  `tests/test_relmap_text.py:217-224`.
- **Why it matters:** the packets themselves name this as the carried risk (Inc-1a §5,
  Inc-1b §5, cure B-151), and my mutant R-1 confirms the failure mode is real. The
  rendered-bytes tests do catch it — so this is not a false-confidence gap — but when it
  fires, the failure points at the output, one derivation removed from the drifted
  literal. A one-line `assert K5_CAUSE == CAUSE["K5"]` inside
  `test_refusal_line_reproduces_the_r1_contract` would fail at the drift site and make
  the carried risk fully closed at unit cost.
- **Suggested fix:** add the equality assertion above (one line; the test module already
  imports `CAUSE`).
- **Evidence state:** executed (mutant R-1) — recommendation, not blocking.

### N-2 — definition census is scoped to `mapper/relmap/*.py`  [MINOR]
- **What:** `_definitions` (`tests/test_relmap_text.py:45-61`) searches only the relmap
  package for a second definition site. A from-scratch redefinition of `cut` (with local
  use, so no old-path import) elsewhere in `mapper/` would evade the census.
- **Where:** `tests/test_relmap_text.py:45-61`.
- **Why it matters:** the packet's load-bearing-emptiness section claims the definition
  census walks the tree; it walks the package. The LLR text scopes the obligation to the
  four named modules (`01-requirements.md` LLR-RVT.1.1), so the increment is within
  contract — but the claim's width should match the search's width, or the search should
  widen to `mapper/**` (cheap: same AST walk the reader census already does).
- **Suggested fix:** either widen `_relmap_sources` to `PKG.rglob("*.py")` or annotate the
  census docstring that the scope is the relmap package per LLR-RVT.1.1's module list.
- **Evidence state:** executed — recommendation, not blocking.

### OBS-1 — concurrent Inc-2 file trips an R1 hygiene arm (NOT an Inc-1 defect)
- **What:** during this review the other session's in-progress `tests/test_relmap_shell.py`
  (untracked; not part of Inc-1a/1b) caused
  `tests/test_relmap_descriptor.py::test_the_input_class_is_new_no_test_fixture_or_tracked_file_carries_it`
  to fail once — that arm scans `tests/` for the `.relmap.yml` literal and its `mine`
  allow-list (`tests/test_relmap_descriptor.py:737-738`) does not yet name the new file.
  At commit `01e87b5` (and in my baseline commissioned run, executed before the Inc-2 file
  appeared) the arm passes.
- **Why it matters:** the Inc-2 increment must extend the `mine` set (or keep shell
  fixtures free of the literal), or its own gate will fail this R1 arm.
- **Evidence state:** executed (fail observed with the Inc-2 file present; green without).

## Security lens

Clean. The diff adds no dependency, no IO, no network, no secrets, no destructive
surface. `text.py` is pure functions over strings; the refusal lines remain UNESCAPED by
frozen R1 contract with the escaping obligation documented at the sink (unchanged). No
secrets or PII appear in the evidence transcripts. Nothing to route.

## Code-review checklist (per role file)

- [x] Diff read in full — commits `968c2c0`, `01e87b5` (source + test + packet diffs).
- [x] Correctness pass — moved definitions verbatim (diff shows no logic change);
      K5/limit branch preserved; `__all__` re-export dropped exactly as LLR-RVT.1.2 names.
- [x] Simplicity — one 34-line leaf; no premature abstraction.
- [x] Reuse/duplication — the point of the increment; the only duplication left is the
      declared K5 literal (N-1).
- [x] Tests verify intent — census arms carry planted-violation positive controls
      (real, read at `tests/test_relmap_text.py:101-122,188-202`); R1 suites re-pointed
      with no assertion change.
- [x] Verdict explicit — approve-with-nits; no HIGH finding open.
- [x] Privacy — no real name/account/email/home path written here; transcripts redacted.
