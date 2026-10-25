# Security re-check — mapper — Batch 2026-10-23-hygiene-batch (second P2 pass)

> Reviewer: `security-reviewer — Kimi K3 subagent executing agents/security-reviewer.md · approve with conditions`
> Date: 2026-10-23. All probes run as `env -u NO_COLOR -u TERM <cmd>`. Scope: `design/design-proposal.md` (PDR-2026-10-23-hygiene-batch), `design/PDR-2026-10-23-hygiene-batch.md` row 10, and the current code the design cites: `mapper/osopen.py` (full read), `mapper/store.py:660-780`, `mapper/diff.py` (full), `mapper/import_csv.py` (full), `tests/test_arch_osopen_callers.py` (full), `tests/test_attachments.py:240-300`.
> Privacy (A-110): this report names repo-relative paths only; no operator profile path, no real person's name.

## TASK A — m4 re-check (LOW; author disposition: adopted into the PDR design proposal)

**Verdict: VERIFIED.**

The author's claim is accurate, in all three places the claim must hold:

1. **§6 note 4** (`design-proposal.md:172`): *"the bounded reader reads at most cap+1 bytes — `f.read(MAX + 1)`, refuse on overflow — the oracle's capped shape at `qm:src/quickmap/model.py:498-505`. **Never** a full read before the re-check; LLR-Q2.1.1's 're-checked on the read bytes' is implemented as this capped re-read."* — exactly the oracle's capped-read shape; the full-read-before-re-check shape of current `mapper/store.py:697-699` (`read_text(encoding="utf-8")` on both files, no cap) is what the design replaces.
2. **§2 store row** (`design-proposal.md:67`): "Byte cap (`MAX_MAP_BYTES`, stat + re-check on the read bytes)… Reads file content **only** through the osopen bounded reader (D2); no direct `open()`." Read together with §6 note 4 — which §6 explicitly says exists "so the DDR checks the reader against this shape, not against a full-read assumption" — the contract phrase "re-checked on the read bytes" is bound to the capped re-read, not to a full read.
3. **§3 flows** (`design-proposal.md:94, :105`): q2-map-load names "stat ≤ MAX_MAP_BYTES → re-check on read bytes **(capped re-read)**"; q2-csv-import names "size ≤ MAX_FILE_BYTES · binary probe ≤ BINARY_PROBE_BYTES". Every file read in the design goes through the D2 reader.

**No uncapped read reintroduced:** `grep -n "read_text\|\.read(" design/design-proposal.md` returns exactly one hit — line 172, the m4 adoption note itself (`f.read(MAX + 1)`). No other `read_text()`/`read()` on operator-supplied content appears anywhere in the design.

Oracle-line verification (`qm:src/quickmap/model.py:498-505`): relied upon from the first pass (`02-review.md:85` records a line-by-line verification of the oracle constants and capped-read shape); the second-pass question was what the *design* mandates, which is settled above.

## TASK B — PDR security lens (PDR checklist row 10)

**Row-10 verdict: ✓** — PDR row 10 (`PDR-2026-10-23-hygiene-batch.md:40`) claims: C6 fired; refusals name limit + map id, never a path; capped reads only; capped-read shape adopted from m4. Every claim independently verified below.

### Bounded readers

- **D2 reader in `mapper/osopen.py`, stdlib-only, no model/store imports:** current `mapper/osopen.py:19-29` imports only `__future__`, `os`, `re`, `stat`, `subprocess`, `sys`, `unicodedata`, `pathlib`, `typing`, `urllib.parse` — all stdlib; the module docstring (:14-17) records the no-`mapper`-import ban. The ban is not just prose: `tests/test_attachments.py` `test_osopen_imports_nothing_from_mapper` (AST-derived, asserts no `mapper*` import into osopen) and `test_osopen_never_uses_a_shell` (no `shell=True`, no `os.system`) pin it. Adding the D2 reader to osopen inherits both pins.
- **Only file-content door for store + import_csv:** design §2 store row (:67) "Reads file content only through the osopen bounded reader (D2); no direct `open()`"; import_csv row (:69) routes its cap+probe through "the same reader". Current uncapped sites confirmed as the ones being replaced: `store.py:697-699`, `import_csv.py:39`.
- **`osopen.py:95-113` / device-name check :104-107:** verified — `if any(PureWindowsPath(part).is_reserved() for part in parsed.parts): return None` (:107), per-component (not last-component-only), with the 3.12/3.13 spelling note (:104-106). The review's m6 correction (the pin lives in `tests/test_seed_safety.py` + `tests/test_inc9n.py`, not `test_store.py`) is recorded in proposal §5 (:151).
- **`store.py:680-740` refusal messages never name a path:** verified — `:690` `map does not exist: {map_id!r}` (map id only, with the B-30 comment recording why the path was removed); `:703` `could not read {map_id}: {type(exc).__name__}` (id + exception type, path deliberately not interpolated per :764); `:726` names `yml_path.name` (file NAME, not path). The design's "names the limit and the map id, never a path" extends this existing discipline; it does not weaken it.
- **`diff.py:40-66`:** verified as cited — `git show` via subprocess with the confined `_git_env()` (:37-46), `safe_load` catching only `YAMLError` (:57-59), `_graph_from_sidecar` under a bare `Exception` net (:61-64). `None`-on-error contract survives in the design: §2 diff row (:68) "`None`-on-error contract survives"; §6 risk row (:174) "a capped-out diff-side load must still yield `None`, not a raise — asserted in the L2 suite" (planned). See new finding S1 below for the one gap on this path.
- **Depth prescan iterative/non-recursive:** verified, with one precision — the normative word lives in the contract the design implements, and the design's test arm enforces it: LLR-Q2.1.2 (`01-requirements.md:348`) "the scan shall be iterative and shall never recurse" (also `:24` "an iterative event-stream scan over YAML parse events (never recursive)", rationale `:349` citing `qm:model.py:461-475`); the design's §5 prescan arm (:142) asserts "a 10,000-deep graph refuses in < 5 s **without RecursionError**" — a recursive prescan at that depth cannot pass this arm, so the enforcement bites even though the proposal prose itself does not repeat the word "iterative". Not a defect; recorded for the DDR's attention.
- **NUL/binary probe bounded:** verified — §1 (:45) "8 KiB binary probe"; §3 q2-csv-import (:105) "binary probe ≤ BINARY_PROBE_BYTES"; §5 CSV arm (:144) tests NUL at byte 0 and byte 8,191 (the probe boundaries).

### New attack surface in the design

- `grep -niE "eval\(|exec\(|shell=True|requests|urllib\.request|socket|http\.client|pip install|new dependenc" design/design-proposal.md` → **zero hits**. No eval/exec, no shell-out added (the osopen launcher is pre-existing, never through a shell, pinned by `test_osopen_never_uses_a_shell`), no new dependencies (D2 row: "Stays stdlib-only"), no network, no secrets, no destructive ops. The Q1 lane touches only `os.environ.pop("NO_COLOR")`; Q3 adds a passive audit sink.
- **Attachments uncapped-by-design (ruling R2) — stated, not silent:** `design-proposal.md:57-58` "This design will NOT: … cap OS-handed attachments (ruling R2)". ✓ Explicit.

### §2 "What it must NOT reach into" enforceability

The osopen row's three limbs are all machine-enforced after the scheduled same-landing amendment:

- "no other module gains an osopen edge" → `tests/test_arch_osopen_callers.py::test_outside_app_only_the_allowed_names_are_imported_from_osopen` (:118-129): AST-derived importer census asserted equal to `ALLOWED_OUTSIDE_APP`; the design schedules adding `store.py` + `import_csv.py` to that set in the same landing (proposal :74-75, §4 D2 row :126, §8 :196, PDR §C :81). Any further edge fails the test.
- "stdlib-only; no `model`/`store` imports" → `tests/test_attachments.py::test_osopen_imports_nothing_from_mapper` (AST-derived).
- Launcher reach → `test_the_launcher_names_appear_only_in_osopen_and_opening` (:65-70): `open_external`/`_default_launcher`/`startfile` confined to `osopen.py` + `screens/map/opening.py`, so the new store/import_csv edges cannot smuggle a launch call.

### A-110 (no secrets/PII in new tests or refusal messages)

✓ — The design's §5 test rows reference fixtures and repo-relative paths only; refusal texts are mandated path-free ("names the limit and the map id, never a path", :47, :67, :98, :107); no operator profile path or person's name appears anywhere in the design, the PDR record, or this report.

## Findings

### S1 — diff-side `git show` capture is a full in-memory read before any cap  [Severity: LOW]
- **What:** `mapper/diff.py:35-49` loads the HEAD-side `.mmd`/`_nodos.yml` via `subprocess.run(["git", "show", ...], capture_output=True)` — the whole blob lands in memory before the byte cap can be re-checked. The m4-adopted capped-read shape (`read(MAX + 1)`) reaches the file-content door (store, import_csv) but cannot reach this subprocess door as designed; §2's diff row (:68) says "Applies the same caps to diff-side map loads" without a mechanism note for the capture itself.
- **Where:** `mapper/diff.py:35-49`; design `design-proposal.md:68` (diff row) and :172 (m4 note's scope).
- **Why it matters:** the same local-memory-exhaustion class m4 closed on the file door survives on the diff door — a multi-GB blob in a cloned/shared repo's history is fully captured before refusal. LOW for the same reason m4 was LOW: single-operator local tool, content from the operator's own repository, no remote surface.
- **Recommendation:** at the L2 lane, either bound the capture (stream `git show` stdout, abort after `MAX_MAP_BYTES + 1`) or record an explicit design note that diff-side caps are post-capture with the rationale. A one-line note in the L2 increment packet suffices if the lane rules it accepted; do not let it pass silently.

### Prior finding re-checked

- **m4 (LOW, byte re-check after full read):** VERIFIED-ADOPTED — see TASK A. Evidence state of the mitigation: `planned` (Phase 3 implements; the DDR checks the reader against the capped shape per :172). No HIGH, no MEDIUM in scope.

## Verdict

- Gate token: **OK to ship from the security lens, with one LOW condition** — S1 owed an explicit disposition at the L2 gate. No HIGH, so no `BLOCK-UNTIL` is owed; m4's adoption is verified as designed.
- Overall: `approve with conditions` (condition = S1 disposition recorded at the L2 increment gate).

## Evidence checklist (security-reviewer)

- [x] Each finding has what · where · why · recommendation — S1; m4 re-check in TASK A.
- [x] Each finding has a severity — S1 = LOW; m4 = LOW (unchanged).
- [x] No secret values in this output — none present; none exist in scope; A-110 honoured (repo-relative paths only).
- [x] Verdict explicit — OK to ship with one LOW condition; zero HIGH, so no `BLOCK-UNTIL` owed.
- [x] New tool/integration scope — n/a, none added (confirmed by the zero-hit probe above and the D2 stdlib-only pin).

`security-reviewer — Kimi K3 subagent executing agents/security-reviewer.md · approve with conditions`
