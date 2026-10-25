# Independent review - Increment 005 (code + security + UX lenses)

Reviewer: `code-reviewer` (independent of the author; read-only toward the diff). Commit `c6a166f`, worktree `wt-r1`.
Probe scripts live outside the repo (`ds-units/r1-review5/`). `mapper.__file__` proved inside the worktree before every run.
Tests run: `test_relmap_audit.py test_relmap_adapter.py test_reqharness_release.py test_reqharness_baseline.py` -> 106 passed, 1 skipped (executed; the skip is the ESC-in-file-name arm, `blocked` on Windows, stated).

## Verdict: approve-with-nits (no BLOCKER, no MAJOR; one MEDIUM test gap, four MINOR)

## Findings

### F1 - MEDIUM - M-RMU-9 is defined, was never run, and the tests the ledger names for it do not kill it
- Where: `01-requirements-ledger.md:244-248` (entry .59: asserting tests `test_sources_line_configured_string` + "AT-126 marker arm", mutant M-RMU-9 "print the resolved path"); `tests/test_relmap_audit.py:274-279`, `:729-762`.
- What: packet section 6 item 6 says M-RMU-9 is in no ledger entry; it is (.59). My mutant (sources line printed as the resolved absolute path in `structure_lines`) is killed ONLY by `test_at_129_every_long_value_is_cut_to_120` (by the length of the path), not by either named test: `test_sources_line_configured_string` calls `format_structure` directly (never sees `structure_lines`), and AT-126's cases configure no `us_canon`/`at_table`. `test_line_formats:195` is formatter-only too. No test asserts the `beta` descriptor's end-to-end sources line (`us_canon=docs/us.md at_table=docs/at.md`) through the CLI.
- Why it matters: the LED .59 control (no absolute repository path via the sources line) rests on an incidental kill.
- Fix: in `test_byte_stable` / AT-127 (beta descriptor, `:780`) assert `"structure: sources: canon=REQUIREMENTS.md us_canon=docs/us.md at_table=docs/at.md" in block` and that the repo path (a marker in the repo name) is absent; re-point ledger .59 to that node. Correct packet section 6 item 6 (name and run M-RMU-9) instead of dropping it.

### F2 - MINOR - `run_cli` does not itself guarantee "no hook line starts with `verdict: `"
- Where: `mapper/reqharness/audit.py` `_hook_lines` / the print loop in `run_cli`.
- What: probed with a generic hook returning `["verdict: ready", ...]`: printed verbatim, giving TWO `verdict: ` lines (`a\nverdict: z` is safe, the newline is escaped). The shipped hook cannot do it (every line it returns starts `structure`; U+2028 and newline are escaped by `_visible`; AT-122 forged-verdict arm covers it). So for today's only caller "can never" holds by construction, not by sink enforcement. The sink also has no per-line length bound (the shipped formatter bounds lines).
- Fix (defence in depth, two lines): in the print loop `if line.startswith("verdict: "): line = "structure: " + line`, plus a test with a generic hook; or document that hooks must not emit that prefix. Note for R2.

### F3 - MINOR - the K9 depth wording in the contract is ambiguous (not a code bug); see Depth verdict
- Where: `01-requirements.md:208`, `:394`, `:650` ("depth 64 loads / 65 K9"). Fix: "total collection depth 64 loads, 65 refused (= 63 loads / 64 refused nested values under a key)".

### F4 - MINOR - UX: gap rows are 210-277 characters (wrap to 3-4 rows at 80 columns); the id repeats in the sentence
- Where: gap line in `mapper/relmap/audit.py`. Seeded run: severity, kind, node id and `reach=` sit in the first ~45 characters (PDR UX MINOR-4 satisfied), but each row repeats the id (`HLR-N13.3 ... HLR-N13.3 has no LLR under it: ...`). `reach=0` is still undefined on screen (UX MINOR-5, not owned by Inc-5). Optional: cut sentence titles to 60 as UX proposed. Not blocking.

### F5 - MINOR - MAJOR-4 asked for the verdict-by-prefix note "in the packet and the README"
- `README.md` has no `--audit` text at all, so the note lives in `docs/ARCHITECTURE.md` (section 3 contract note, present) and in the on-screen header. Acceptable; say so in the DDR.

### Nit (no action)
- The "10 files" are 8 `inc5-*` + `inc4f-red-f1-mutant-c.txt` + `review-inc004.md`; all 10 re-hash equal to the packet table.

## Checks (requested list)

1. Hook and sink (executed).
   - Exit code: `return 0 if report.ready else 1` untouched; hook output is printed after `render` and cannot change the code. `test_tc_rm_02` (code equals the no-hook code, output = base + one line), AT-120/126 compare with the hook-less subprocess; the 16 existing `--audit` sites pass.
   - Every hook line goes through `_visible` (`print(_visible(line))`), the fixed lines and the truncation line included. Newline, ESC, U+2028 probed escaped.
   - Bound: `islice(..., 1001)`; `test_hook_line_bound` asserts at most 1,001 pulled, exactly-1000 prints no truncation line, 5,000 prints 1,000 + the truncation line.
   - No-repo / no-registry keyed on `report.chain_status` (hook not called); `test_fixed_lines_key_on_chain_status_not_verdict_text` rewords the verdict and still gets the fixed line.
   - Raising hook: only `type(exc).__name__` printed (message `secret C:/private/path` absent, stderr empty). `except Exception` also covers errors raised during iteration and a non-iterable return.
   - Forged `verdict: `: safe for the shipped hook; see F2 for a generic hook.
2. Layer B nodes are real subprocesses: `run_audit` = `python -c "from mapper.app import main; main()" --audit ...` with `PYTHONPATH=ROOT`, `cwd=ROOT`; the baseline `run_audit_nohook` is `run_cli(argv)` without the hook. `test_child_runs_this_checkout` compares the child's `mapper.__file__` with the test process's (GREEN; both resolve into the worktree).
   Mutants of my own (restore hash-verified each time; `git status` clean after):

   | # | File | Mutant | Result | Killed by |
   |---|---|---|---|---|
   | 1 | `relmap/audit.py` | swap `us_canon` / `at_table` unpack | KILLED | `test_line_formats`, `test_sources_line_configured_string`, `test_format_structure_cuts_inside`, Layer B `test_at_129_...` |
   | 2 | `relmap/audit.py` | unlinked ids shown `[:5]` -> `[:6]` | KILLED | `test_notes_come_in_the_stated_order_and_the_unlinked_line_shows_five_ids` (Layer A) |
   | 3 | `reqharness/audit.py` | truncate at `len(lines) >= LIMIT` instead of `>` | KILLED | `test_hook_line_bound` |
   | 4 | `relmap/audit.py` | M-RMU-9: sources printed as the resolved path | KILLED only by `test_at_129_...` (incidental) | see F1 |

   sha256 prefixes before = after: `relmap/audit.py afcd78363a0f`, `reqharness/audit.py 0a0f78f67dc2`.
3. Depth boundary: see below.
4. UX (executed on a seeded tmp repo: the repository's own `REQUIREMENTS.md`, one descriptor with an unknown key, one invalid descriptor; real `mapper --audit` subprocess, exit 1).
   - The line right after `verdict: ` is `structure: informational - does not change the verdict or the exit code` (MAJOR-1; also carries MAJOR-4 on screen).
   - Count line `structure: skipped N canon rows (...); unknown status=..; reach not computed=..` only when nonzero and distinct from `structure note:` rows (MAJOR-2). Overflow lines `structure: gaps shown X of Y (...)` / `structure: notes shown X of Y (...)` (MAJOR-3; unit-tested at 21 gaps / 11 notes).
   - Refusal: `structure: refused (bad.relmap.yml): not valid YAML - descriptor skipped` (no snippet, no path); descriptors in code-point order. Qualified gaps end `(canon rows near this id could not be parsed or linked: 2)` (MINOR-3). `structure: unavailable (internal error: <Type>)` (MINOR-2). No repository path in any block line.
   - Width: F4. The pre-existing report lines are already 83-157 characters, so wrapping at 80 is existing behaviour.
5. Evidence: all 10 files re-hashed (`sha256sum`) and equal to the packet table. SOURCE files 3 / 4 (`relmap/audit.py`, `reqharness/audit.py`, `app.py` +3/-1; the hook import is lazy inside the `--audit` branch). Traces: AT-117..AT-122, AT-124..AT-129, TC-RM-02/03 each have a named node; AT-123 is retired by the contract (line 631), not missing. The one-line edit to `tests/test_relmap_descriptor.py` (allow-list gains `test_relmap_audit.py`) is justified: that census asserts by content which test files may name `.relmap.yml`, and the new Layer B suite writes such files; declared in packet section 6 item 8. No account name, email or handle in the commit diff (0 hits); the gate transcript uses `<user>`.
6. Opinions on packet section 6:
   1. AT-126(c) symlink: agree. The node asserts stdout empty, stderr `refused (link)`, exit 1; amend the contract and keep the K1 text at Layer A (Inc-4 `test_canon_causes`).
   2. "marker never in stdout": agree, reword to "in the structure block" (the `repo:` line prints the path by design).
   3. K9 numbers: the author's measurement is right; see Depth verdict (wording fix only).
   4. Open wordings: agree, add to the LLR-RMU.1.2 table (unlinked note, ignored key, 400-character sentence cap).
   5. `exc.limit`: fine (equals the canon byte limit; no new import).
   6. M-RMU-9: disagree with the premise. It exists (ledger .59); name it in the packet and run it (F1).

## Depth verdict (K9, AT-121)

The code is right; the R1 contract text is imprecise. There is no off-by-one.
- `mapper/yamlscan.py:50-55` counts every Sequence/Mapping START event, so a descriptor's top-level mapping is depth 1, and `depth > MAX_DEPTH (64)` raises. Hygiene LLR-Q2.1.2 (`2026-10-23-hygiene-batch/01-requirements.md:351,355`) says exactly that: "refuse when collection nesting exceeds 64"; "depth-65 arms refuse; depth-64 parses". Its pinned test (`tests/test_ingestion_limits.py:142-154`) states "total collection depth 64 (top-level mapping + 63 nested) is the last accepted level".
- Probe (executed, `r1-review5/depth.py`): total collection depth 64 loads, 65 refused, 66 refused, for a flow-sequence chain and for a top mapping with nested flow mappings. For `x: {k: {k: ...}}` the count of nested values under the key is therefore 63 loads / 64 refused, which is what the author measured and what `_nested_flow(63)` / `(64)` and the AT-121 `ok-depth` control use.
- R1's "depth 64 loads / 65 K9" is correct as TOTAL collection depth (the hygiene meaning); the author's "64 refused / 63 loads" counts nested values under a key. Same boundary. Fix the contract wording (F3); the nodes already pin both sides of the exact boundary.

## Evidence states
Hook and sink checks, Layer B subprocess runs, mutants, UX run, depth probe, hashes: `executed`. Python 3.10 run: `not-run` (operator-owned). Full suite: `not-run` (by instruction).
