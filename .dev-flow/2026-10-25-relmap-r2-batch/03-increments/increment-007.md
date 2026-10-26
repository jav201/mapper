# Increment 007 — LLR-RVU.1.1 · the `--audit` hook per-line bound 240 (AT-152)

> **Artifact language.** Canonical **English scaffold**; generated in the batch's language.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r2-batch` |
| Increment | `007` |
| Lane (if the batch forked) | trunk, after the join · any boundary |
| Requirement(s) | `HLR-RVU.1` · `LLR-RVU.1.1` (ruling `LED-2026-10-25-r2.02`) |
| Acceptance | `AT-152` (the per-line bound over the emitted form + the straddling arm + the F-SEC-3 order) · white-box `TC-RM-30` (the cut's boundaries and spelling back-off) · unit: `_cut_hook_line` (cyclomatic ≥ 3 — the length branch + the `\x`/`\u` spelling branches + the straddle loop) |
| Agent | `software-dev` |
| Date | `2026-10-25` |

---

## 1 · What changed

BLUF: the `run_cli` hook print path gains the frozen per-line bound. The
pipeline order pinned verbatim by F-SEC-3 (`PDR-2026-10-25-relmap-r2-batch#D4`)
lands as written: **escape → 239+ellipsis spelling-aware cut → `verdict: `
rewrite check → print**. After `_visible` escapes a hook line, the new
`_cut_hook_line` keeps the first 239 cells and one trailing ellipsis (240
emitted cells) of any line longer than `HOOK_LINE_CELLS = 240`; when the
boundary lands inside a `\xNN` / `\uXXXX` spelling the cut backs to the
spelling's start (adjacent spellings re-check their own new tail), so the
emitted line never ends mid-spelling; the `verdict: ` rewrite then runs on the
CUT line — a hook line cut short cannot re-expose `verdict: ` to line start,
and a `verdict:`-starting line emits `structure: ` + the 240-cell cut form.
The R1 D4 semantics are untouched: the 1,000-line count bound, the prefix
rewrite, the fixed no-repo/no-registry lines and the exit code — the whole R1
audit suite is green (48 passed), including TC-RM-02/03.

What the operator reaches: `mapper --audit` over any repo whose structure
lines exceed 240 cells (a long gap sentence, a hostile payload) now emits
bounded lines — one ellipsis, whole escape spellings only — instead of
arbitrarily long rows.

**Inc-7 gate amendment (the risk-#6 contingency, executed):** the R1 snapshot
carries two gap lines of 271/277 cells whose tails the frozen bound must cut.
The PDR's risk table predicted exactly this ("the R1 golden surfaces catch a
wrong bound at the Inc-7 gate") — the surfaces fired, the premise check (P10/
P11) did not cover the longest `structure_lines` sentence, and the two R1 arms
pinning whole-text content of those two lines were re-derived: **content
authority moves to the D5-frozen `structure_lines` seam; the bound is asserted
on the emitted form.** Enumerated in Correction population; recorded as a
ledger amendment in §6.

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/reqharness/audit.py` | source | LLR-RVU.1.1 | EDIT — `HOOK_LINE_CELLS = 240` beside `HOOK_LINE_LIMIT`; the new `_cut_hook_line` (239+ellipsis, spelling-aware back-off) after `_visible`; the print loop re-ordered to the F-SEC-3 pipeline with the cut between escape and rewrite; `_hook_lines`' docstring updated; the sink comment pins the order verbatim |
| `tests/test_hook_line_bound.py` | test | LLR-RVU.1.1 · AT-152 · TC-RM-30 | NEW — 7 nodes: 2 unit arms (240/241 boundary, cut shape, `\xNN`/`\uXXXX`/adjacent back-off, the cut never rewriting a verdict prefix) + 5 AT-152 arms through `run_cli` (the basic bound, the escaped-form predicate, the straddling arm, the F-SEC-3 order observable end to end, the under-the-bound passthrough) |
| `tests/test_relmap_audit.py` | test | LLR-RVU.1.1 (the gate amendment) · AT-125 · LLR-RMU.1.2 | 2 arms re-derived, node count unchanged (49 → 49) — `test_at_125…` (snapshot half: qualifier content asserted on the `structure_lines` seam; the emitted gap lines pinned ≤ 240) and `test_snapshot_run` (qualified-count asserted on the seam; emitted gap lines pinned ≤ 240) — see Correction population |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p3-inc7-*.txt` | generated | US-RMV-006 | RED, GREEN ×2, mutants, guards — redacted, hashed |
| `.dev-flow/2026-10-25-relmap-r2-batch/05-postmortem.md` | doc | the P5 close (`LED-2026-10-25-r2.32/.33`) | COMPLETED — the P5 post-mortem; no code, declared in PLAN §Gate notices |
| `.dev-flow/2026-10-25-relmap-r2-batch/06-docs/executive-summary.md` | doc | the P6 close | NEW — the executive summary |
| `.dev-flow/2026-10-25-relmap-r2-batch/06-docs/functionality.md` | doc | the P6 close | NEW — the functionality doc (the screens, how-to-read and keys) |
| `.dev-flow/2026-10-25-relmap-r2-batch/06-docs/traceability-matrix.md` | doc | the P6 close | sign-off finalized |
| `.dev-flow/2026-10-25-relmap-r2-batch/design/DDR-2026-10-25-relmap-r2-batch.md` | doc | COND-DDR-1/2 (`LED-2026-10-25-r2.32/.33`) | the declared COND-DDR-1 records-pass amendment — the seal stands, the amendment is declared in the record's status block |
| `.dev-flow/2026-10-25-relmap-r2-batch/01-requirements.md` | doc | COND-DDR-1 (`LED-2026-10-25-r2.32`) · the canon fold | citation re-repair by content match + the 6 story Statements the fold required |
| `.dev-flow/2026-10-25-relmap-r2-batch/01-requirements-ledger.md` | doc | COND-DDR-1/2 (`LED-2026-10-25-r2.32/.33`) | the ledger entries .32/.33 |
| `.dev-flow/2026-10-25-relmap-r2-batch/design/design-proposal.md` | doc | COND-DDR-1 (`LED-2026-10-25-r2.32`) | citation re-repair by content match |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p5-cond-ddr2-a110-prefix-red-2026-10-26.txt` | generated | HLR-RVM.1 · HLR-RVS.1 · HLR-RVH.4 | COND-DDR-2 capture 2 — the A-110 pre-fix RED at `cdc4491^`, sanitized at authoring |
| `.dev-flow/2026-10-25-relmap-r2-batch/evidence/p5-cond-ddr2-census-prefix-red-2026-10-26.txt` | generated | HLR-RVM.1 · HLR-RVS.1 · HLR-RVH.4 | COND-DDR-2 capture 1 — the three census pre-fix REDs at `2e83cf6^`, sanitized at authoring |
| `.dev-flow/BACKLOG.md` | doc | the batch close | B-166 (the content-anchor citation census) |
| `.dev-flow/state.json` | doc | the batch close | station P6 · `phase_status: awaiting-sync` |
| `.dev-flow/2026-10-25-relmap-r2-batch/PLAN.md` | doc | the batch close | Last updated + the P5/P6 gate-notices entry |
| `REQUIREMENTS.md` | doc | the batch close | the canon fold (78 ids) |
| `mapper/relmap/text.py` | source | HLR-RVT.1 · LLR-RVT.1.1 | V59 close-limb row — the Inc-1a leaf; increment-001a's own §2 row is not enumerated by the packet reader (`increment-\d+.md` only), so the close limb re-names the file here |
| `mapper/relmap/model.py` | source | HLR-RVT.1 · LLR-RVT.1.1 | V59 close-limb row — the Inc-1a re-point (`DISPLAY_MAX`/`cut` removed) |
| `mapper/relmap/descriptor.py` | source | HLR-RVT.1 · LLR-RVT.1.2 | V59 close-limb row — the Inc-1a re-point (`refusal_line` import) |
| `mapper/relmap/audit.py` | source | HLR-RVT.1 · LLR-RVT.1.2 | V59 close-limb row — Inc-1a drops the `audit.__all__` re-export |
| `mapper/relmap/adapter.py` | source | HLR-RVT.1 · LLR-RVT.1.2 | V59 close-limb row — the Inc-1b re-point (`cut` from the leaf) |
| `tests/test_relmap_text.py` | test | HLR-RVT.1 · AT-150 · AT-151 | V59 close-limb row — the Inc-1a/1b new file (increment-001a/b not enumerated) |
| `tests/test_relmap_model.py` | test | LLR-RVT.1.1 | V59 close-limb row — the Inc-1a re-pointed import block (`:17-26`) |
| `tests/test_darkside_census.py` | test | HLR-RVM.1 · HLR-RVS.1 | V59 close-limb row — the P3 census amendment (pin 82 → 94, `LED-2026-10-25-r2.31`), a records/test-side unit with no digit-named packet |
| `tests/test_app_imports_used.py` | test | HLR-RVH.4 · HLR-RVT.1 | V59 close-limb row — the +6 re-export allowance nodes (increment-006b not enumerated) |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 1** — exactly the PLAN Inc-7 row |
| Test files | 2 (1 new + 1 amended; uncapped) |
| Doc files | 0 |

## 3 · How to test

```bash
PYTHONPATH=<worktree> python -c "import mapper; print(mapper.__file__)"
# the new file (unit + AT-152):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider tests/test_hook_line_bound.py
# the R1 audit suite (D4 pins):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider tests/test_relmap_audit.py
# the commission's guard set (the packet's §4 transcript):
PYTHONPATH=<worktree> env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 \
  python -m pytest -q -p no:cacheprovider \
  tests/test_fold.py tests/test_repair_artifact_claims.py tests/test_no_operator_paths.py \
  tests/test_mod_*.py tests/test_repair_map_truth.py tests/test_a3_census.py \
  tests/test_relmap_*.py tests/test_keymap.py tests/test_key_dispatch.py \
  tests/test_inc9c.py tests/test_help*.py tests/test_palette*.py \
  tests/test_reqharness_release.py tests/test_reqharness_baseline.py \
  tests/test_hook_line_bound.py
```

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `full` | `_cut_hook_line` — boundaries (240 untouched / 241 cut / 500 cut / emitted 240), the spelling back-off (`\xNN` straddle, `\uXXXX` straddle, adjacent spellings, spelling ending exactly at the boundary kept whole), the cut leaving a `verdict: ` prefix alone | passed (2 nodes) |
| **A · white-box** `TC` ↔ LLR | `full` | TC-RM-30 — the cut's exact emitted strings per class of input | passed (inside the 7) |
| **B · black-box** `AT` ↔ story | `full` | AT-152 — `run_cli` over a registry repo (the R1 idiom): the 240+N cut with one ellipsis, the escaped-form predicate (60 raw controls MUST cut), the straddling `\xNN`/`\uXXXX` arms, the F-SEC-3 order observable (`structure: ` + the 240-cell cut form = 251 cells, `verdict: ` exclusivity census), the under-the-bound passthrough byte-for-byte | passed (5 nodes) |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | none needed — the sink pre-exists without the bound; the 7 new nodes run against the unmodified `audit.py` and FAIL on the missing feature |
| Instrument | project code — `pytest` over the new file, the tree untouched |
| Where it ran | this worktree (wt-r2) |
| Transcript | `evidence/p3-inc7-red.txt` — `6 failed, 1 passed`, exit 1, wall 4s; the 2 unit arms failed on `module 'mapper.reqharness.audit' has no attribute '_cut_hook_line'`, the 4 bound-relevant AT arms failed on emitted-length/equality, the under-the-bound passthrough arm passed **by design** (D4-unchanged behaviour on a short line) |
| Restore proven by | nothing to restore (no source edit in the RED pass) |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` in every run (C-46) |
| Arms resolved at baseline | 7 — the 6 RED arms each seen failing; the 1 by-design GREEN arm named |
| Verdict granularity | per node id |
| Arms that stayed GREEN | `test_at_152_hook_line_under_the_bound_passes_through_untouched` — BY DESIGN: it pins the D4-unchanged passthrough, which holds with and without the increment |

| Field | Value |
|---|---|
| **RED counterfactual** | 6 RED arms on the unmodified sink, transcript `evidence/p3-inc7-red.txt` (sha256 `6ba3bc8c…ccd03e`, exit 1) |

| Field | Value |
|---|---|
| **Mutation verdicts** | 3/3 KILLED, restore sha256 proven per arm (`cd73899e…733ff` before = after on every arm): **M-RVU-1** (cut the RAW line before escaping — `_visible(_cut_hook_line(line))` → the escaped-form arm RED: all 60 spellings emitted, 242 cells) · **M-RVU-2** (the verdict rewrite moved BEFORE the cut — the F-SEC-3 order swap → the order arm RED: emitted 240 cells instead of `structure: ` + the 240-cell cut form) · **M-RVU-3** (the spelling back-off removed — a plain 239+ellipsis cut → the spelling unit arm RED, plus the straddling and escaped-form arms) · arms that stayed GREEN: none across the battery (M-RVU-1 left the pure-plain-lines arms green by construction — the 280-char payload has no escapes; the escaped-form arm is its kill) · runner's own BAD control shown BAD before the battery was believed · transcript `evidence/p3-inc7-mutants.txt` (sha256 `b3f5955a…32870b`), runner exit 0 |

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| `pytest` (the 7 new nodes) | the unmodified sink | `6 failed` — `evidence/p3-inc7-red.txt` |
| the R1 golden surfaces (risk #6's declared catcher) | the first bound implementation at the R1 worst case | `test_snapshot_run` + `test_at_125…` failed — the false-fail the PDR predicted; transcript in the first (superseded) `p3-inc7-green-audit.txt` pass, resolution in Correction population |
| the mutation runner | its own BAD control (anchor ×0) | BAD, battery stopped — control PASS, in `evidence/p3-inc7-mutants.txt` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 3 instruments, each shown RED (or the declared catcher) before its PASS was believed |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the hook lines of `mapper --audit` (stdout after the report) | per arm: `emitted == ["a"*240, "b"*239+"…", "c"*239+"…"]`; `emitted == ["ab" + "\\x01"*59 + "…"]` (239 cells); the straddling pair `== ["x"*237+"…", "y"*235+"…"]`; the order arm `hook_line == "structure: " + "verdict: " + "v"*230 + "…"` (251 cells — the 11-cell `structure: ` prefix + the 240-cell cut form; amended per review-inc006b7 F1) and exactly one `verdict: `-prefixed line in the whole output | all held — `evidence/p3-inc7-green-targeted.txt` |
| the R1 snapshot surface after the amendment | every emitted `structure gap:` line `<= 240` cells; block order and figures byte-equal to the R1 pins | held — `evidence/p3-inc7-green-audit.txt` |
| the seam (what `structure_lines` yields, pre-sink) | the two qualified carrier lines keep their full 271/277-cell text with the qualifier tails | held (the D5 seam is unbounded by design) |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 3 artifacts, each asserted on its emitted form (sink bytes, bounded snapshot surface, unbounded seam) |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| RED transcript | `…/evidence/p3-inc7-red.txt` | `6ba3bc8cd514e9a22da33f8ef6ca3aa1a878815552b5e4c0c355953e70ccd03e` |
| GREEN targeted transcript | `…/evidence/p3-inc7-green-targeted.txt` | `3cbfdd7e7147cbc0a97a95c6987da14e9339d68356963380be93db0fdb4afa17` |
| GREEN R1-audit transcript | `…/evidence/p3-inc7-green-audit.txt` | `1605f75d3aba91964a9c7ed815465f270ec3c91b4fabe64ac49276c2aabd8f2d` |
| mutation battery transcript | `…/evidence/p3-inc7-mutants.txt` | `b3f5955a9aab887d2f4c81745110cd06a5c00ccf00e8b1adf1561522d132870b` |
| GREEN guard transcript | `…/evidence/p3-inc7-green-guards.txt` | `4137bd3a963eab60a53b64ad80f04de7a141a7deb487352914500b3de5ad8150` |

All transcripts redacted with a PYTHON script (`_scratch/redact_7.py`, account
name → `<user>`) before hashing; exit code and wall time in each transcript.

| Field | Value |
|---|---|
| **Evidence files** | 5 artifacts, each at the declared home, cited with the digest of its stored bytes |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes — "no hook line over 240 cells reaches the terminal" is an absence claim at the sink |
| If the result is an ABSENCE, what made the search wide enough | the bound applies to EVERY hook line by construction (the only print door for hook lines), and the arms vary the input class: plain long lines, escaped-near-bound payloads, straddling `\xNN` and `\uXXXX`, a `verdict:`-prefixed long line, an under-the-bound line |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_at_152_hook_line_longer_than_240_is_cut_with_one_ellipsis` pins the conclusion "the emitted hook surface respects the bound", with the boundary arm (240 untouched / 241 cut) proving the predicate's edge is alive |
| Conjunctive criteria: one mutation per conjunct | M-RVU-1 the emitted-form conjunct · M-RVU-2 the order conjunct · M-RVU-3 the spelling-integrity conjunct · the count-bound/exit-code conjuncts are pinned by the unamended R1 arms (TC-RM-02/03, the 1,000-line arm, the fixed-lines arm — all green) |
| Synthetic instance of the absent case | every AT-152 fixture line IS a synthetic over-bound instance (280/242/241/309 cells); the R1 snapshot's 271/277-cell lines are the natural instance, pinned ≤ 240 after the amendment |
| **Positive control for every probe that returned an ABSENCE** | the under-the-bound passthrough arm asserts a line IS emitted whole (byte-for-byte, escapes included) — the same run_cli surface emitting the bounded lines, so presence and absence are measured by one mechanism |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `grep -rn "run_cli\|_hook_lines" mapper/` + `grep -rln "run_cli\|_hook_lines" tests/` | the consumers are `mapper/app.py:357` (the CLI dispatch — unchanged), `mapper/relmap/audit.py` + `descriptor.py` (doc references to the sink contract — unchanged), `tests/test_relmap_audit.py` (re-run green), `tests/_relmap_fixtures.py`, `tests/test_a3_census.py` (the A3 census — green in the guard set) |
| B2 file moved on disk | n/a — `audit.py` edited in place; not fired |
| B3 byte-identical golden captures this source | the R1 goldens pin the REFUSAL bytes (`test_prescan_refusal_goldens.py`) and report surfaces, not the hook lines — none captures a hook line over 240 cells (the two 271/277-cell lines are the longest shipped, and the amendment pins them ≤ 240 on the emitted form); the refusal line is cut at 120 by the RVT leaf, untouched here |
| B4 artifact produced here is consumed elsewhere | the emitted stdout is read by operators and the R1/R2 suites; the seam `structure_lines` (D5) is consumed read-only by `app.py`'s hook injection — its contract is unchanged |
| A3 interface consumed by another module changed | `run_cli(argv, extra_lines=None)` — the R1-frozen signature — is unchanged (the diff adds a constant, one function and re-orders the print loop body); the A3 census (`tests/test_a3_census.py`) is green |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run (B1 · B2 · B3 · B4 · A3); B1 fired with the expected consumer set, all re-validated green; B2 not fired; B3/B4 inspected; A3 green |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| the R1 arms pinning whole-text content of hook lines the frozen bound must cut | every R1 audit-suite arm asserting content of an over-240-cell hook line | the R1-suite run itself (`pytest tests/test_relmap_audit.py`) — it named exactly `test_at_125…` and `test_snapshot_run`; the other 46 arms passed unamended | 2 arms | `tests/test_relmap_audit.py` — both arms re-derived: qualifier/content assertions onto the D5 `structure_lines` seam, the bound (`<= 240`) onto the emitted form; node count unchanged (49 → 49) | every other qualifier-text consumer asserts on the seam or a short line — `tests/test_relmap_adapter.py:156`, `tests/test_relmap_gaps.py:193`, `tests/test_relmap_gaps_view.py:84,273` — left untouched, green in the guard set |

The enumeration ran BEFORE the first edit (the failing suite pass IS the
enumeration); the superseded first `p3-inc7-green-audit.txt` pass recorded the
population failing. The re-derivation does not weaken either arm: the content
assertions moved to the layer that owns content (the D5 seam, unescaped by
contract), and the sink gained a bound assertion the arms never had.

| Field | Value |
|---|---|
| **Correction population** | 1 correction, enumerated by its own failing run before its first edit — 2 arms re-derived, no silent stretch |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| the unamended qualified-count assertions | `grep -n "canon rows near this id" tests/test_relmap_audit.py` | yes — the two surviving whole-text reads are the seam-based re-derivations (`test_at_125…` :740-742, `test_snapshot_run` :866-867) | the seam rows are the only whole-text reads left on the emitted snapshot surface |

### Signed-balance test ledger

`post = base − deleted + added` → new file `7 = 0 − 0 + 7`
(`tests/test_hook_line_bound.py`); amended file unchanged `49 = 49 − 0 + 0`
(`tests/test_relmap_audit.py` — two arms re-derived in place). Targeted runs:
7 passed (wall 4s) and 48 passed, 1 skipped (wall 44s, the R1 suite). Guard
set (31 files): `1218 passed, 2 skipped, 3 xfailed` (wall 323s, exit 0) — the
first pass's single failure was the A3 census's "untracked source is
invisible" gate over the then-unstaged new test file; the commission's answer
is staging itself (the census demands it), and the re-run on the staged,
uncommitted increment is the transcript above.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Kimi K2.8 session executing agents/code-reviewer.md + agents/security-reviewer.md + agents/ux-reviewer.md · approve-with-nits → nits dispositioned in the review-close unit (this commit)` |
| Review record | `.dev-flow/2026-10-25-relmap-r2-batch/evidence/review-inc006b7.md` (sha256 `3c464589cd211d9d295b7047075440294851e039461fa1537e749c728ef56194`) |

Follow-ups (2 MINOR, dispositioned in the review-close unit):

| Finding | Disposition | Evidence |
|---|---|---|
| F1 — the packet prose under-measures the `verdict:` corner by one cell ("250 cells" / "the 10-cell `structure: ` rewrite"; the shipped corner emits 251 cells — the 11-cell prefix + the 240-cell cut form, as the order arm asserts verbatim) | **fixed** (docs-only): the packet's §4 layer-B row, the emitted-form table and the §5 risk bullet now say **251 cells / the 11-cell `structure: `**; the code and the test were already correct (the order arm asserts the exact 251-cell string) | this packet §4/§5, amended · review §3 F1 (the reviewer's live probe measured 251) |
| F2 — the bound counts code points, not display cells; a wide-glyph line can paint ~2× the bound (contract says "characters", ruling r2.02) | **declared + recorded for the DDR**: §5 now carries the explicit DDR note (code-point counting, reviewer-measured `"漢"*300` → ~480 display cells, MINOR as shipped; MAJOR only if a later contract re-reads "characters" as "cells") and the display-width bound is parked as **BACKLOG B-161** | this packet §5 · `.dev-flow/BACKLOG.md` B-161 · review §3 F2 |

## 5 · Risks

- The two R1 snapshot gap lines (271/277 cells) are now cut at the sink; an
  operator reading `--audit` output on the snapshot fixture sees the bounded
  form. The full text remains available through the D5 seam (`structure_lines`)
  and in the R1 test pins. This is the frozen trade the ruling (r2.02) made;
  the risk row #6 note in the proposal carries the background.
- **DDR note (review-inc006b7 F2, recorded):** the bound counts
  CHARACTERS (code points), not display cells: a line of
  wide (CJK) glyphs escapes unchanged and may paint wider than 240 cells
  (measured: `"漢"*300` → 239 code points + ellipsis, ~480 display cells).
  The contract's wording is "characters" (`LLR-RVU.1.1`, ruling
  `LED-2026-10-25-r2.02`), and the hostile
  vocabulary the escaper re-spells (Cf/Zl/Zp/Mn/Me/Zs/controls) is the
  width-spoofing class — a deliberate spelling bounds the width risk; no AT
  asserts cells. **Residual severity:** MINOR as shipped (contract-conformant);
  it becomes MAJOR only if a later contract re-reads "characters" as "cells" —
  carried to the DDR as **BACKLOG B-161** (a display-width bound).
- `verdict:`-starting hook lines longer than 240 emit 251 cells (the 11-cell
  `structure: ` rewrite lands after the cut, per the pinned order — measured
  live by the reviewer and amended per review-inc006b7 F1; the packet's earlier
  "250 cells / 10-cell" phrasing under-measured the corner by one). The
  exclusivity census (exactly one `verdict: ` line) and the emitted form are
  pinned; the 251-cell corner is the order's direct consequence, asserted
  verbatim by the order arm.

## 6 · Pending items / spec deviations

- **Ledger amendment (proposed, exact text)** —
  `LED-2026-10-25-r2.30`: Inc-7 gate amendment (LLR-RVU.1.1): the R1 snapshot's
  two qualified gap lines measure 271/277 cells — over the frozen per-line
  bound — so the shipped surface now cuts their tails. **Before:** AT-125's
  snapshot limb and `test_snapshot_run` asserted the qualifier content
  (`canon rows near this id could not be parsed or linked: N`) on the emitted
  `--audit` lines. **After:** the qualifier content is asserted on the D5
  `structure_lines` seam (unescaped by contract, unbounded by design); the
  emitted form is asserted bounded (every `structure gap:` line ≤ 240 cells);
  block order and figures unchanged. **Deleted:** the whole-text reads of the
  two over-bound lines. **New:** the seam reads + the ≤ 240 pins.
  Requirement: LLR-RVU.1.1 (asserting-tests line updated: the "existing suite
  green" is realized through the amended arms — the suite is green, 48 passed).
  The premise note (P10/P11) in LLR-RVU.1.1's draft-time verification is
  superseded in its measurement scope: it covered the refusal line (120) and
  the report length (298 lines), not the longest `structure_lines` sentence —
  the PDR's risk #6 carried exactly this contingency.
- COND-QA-3/4/5, SEC-2, UX-2 (the PDR conditions owned by earlier increments)
  are discharged at their owners; nothing new surfaced here.
- PROPOSED for the trunk (Records to integrate): the PLAN test-ledger rows
  (new file +7; amended file 49 → 49; the guard-set counts) and the ledger
  entry above.

## 7 · Suggested next task

The batch gate (`devflow-validate.py --brief`) — 0 BLOCK expected: every
AT-130…152 now has its on-disk node (AT-149 minted at Inc-6b, AT-152 here).
Then Phase 4 validation on the joined tree (the all-lane AT run, F-5) and the
records-integration pass (this packet's §6 + the PLAN Last updated). The
orchestrator schedules this increment's independent review (§4b).

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1/1 — exactly the PLAN Inc-7 row (`mapper/reqharness/audit.py`) |
| 2 | Tests written in this same increment | all | ✓ | 7 nodes new + 2 arms amended; RED-before-GREEN (6 RED on the unmodified sink) |
| 3 | Layer 0 written where the criterion applies | `full` | ✓ | `_cut_hook_line` — cyclomatic ≥ 3 (length branch + `\x`/`\u`/lone branches + the straddle loop), boundary data |
| 4 | RED counterfactual declared | all | ✓ | 6 RED arms on the unmodified sink, transcript `evidence/p3-inc7-red.txt` (sha256 `6ba3bc8c…ccd03e`, exit 1); the 1 by-design GREEN arm named |
| 5 | Reverse census declared | all | ✓ | §Reverse census — B1 fired (expected consumers, all green), B2 not fired, B3/B4 inspected, A3 green |
| 6 | `code-reviewer` passed | all | ⚠ | `pending — orchestrator schedules` (§4b) |
| 7 | No file from another lane touched | all | ✓ | only `audit.py` + the two named test files + this increment's evidence; no renderer/home/app/keymap edits |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D4 (`run_cli` signature, count bound, rewrite, fixed lines, exit code) intact — the R1 suite is green; D5 (`structure_lines`) untouched; the F-SEC-3 order pinned verbatim at the sink |
| 9 | Coverage claims verified on disk | all | ✓ | 7 + 49 + guard-set nodes collected on disk in the final runs |
| 10 | Load-bearing emptiness declared | all | ✓ | §Load-bearing emptiness — synthetic over-bound instances per class; the passthrough arm is the positive control |
| 11 | Mutation verdicts declared | all | ✓ | 3/3 KILLED per arm (M-RVU-1/2/3), restore digests cited, BAD control PASS, runner exit 0 |
| 12 | Instrument RED-proof declared | all | ✓ | 3 instruments — pytest RED, the R1 golden surfaces fired as risk #6 declared, the runner's BAD control |
| 13 | Correction population declared | all | ✓ | 1 correction, enumerated by its own failing run before its first edit — 2 arms re-derived onto the D5 seam |
| 14 | Emitted-form assertion declared | all | ✓ | 3 artifacts asserted on emitted bytes (hook lines, bounded snapshot surface, the unbounded seam) |
| 15 | Independent review names somebody | all | ✓ | `pending — orchestrator schedules` (§4b) |
| 16 | Evidence files declared | all | ✓ | 5 files at `artifact_homes.evidence`, digests of stored bytes |
