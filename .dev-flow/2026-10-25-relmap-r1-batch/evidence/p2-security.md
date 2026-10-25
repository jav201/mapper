# P2 security review — relmap-r1 batch (trigger C6)

Reviewer: security-reviewer (independent; authored none of the batch). Read-only: no code, requirement or state edits.
Scope: `PLAN.md`, `01-requirements.md` (HLR-RML/RMA/RMU/RMM/RMG, LLR-RML.1.1-4, RMA.1.1-4, RMU.1.1-3, RMM.1.2-3, RMM.2.2, IFC flows, §6.3), `docs/ARCHITECTURE.md` rows `relmap`/`yamlscan`/R-016/R-017, the last `decisions_log` entry, and the existing code the contract reuses: `mapper/osopen.py`, `mapper/store.py::_prescan_sidecar`, `mapper/reqharness/derive.py::load_canon/parse_canon`, `mapper/reqharness/audit.py::_visible/run_cli`.
Severity map: HIGH=BLOCKER, MED=MAJOR, LOW=MINOR. Evidence state of every finding: `planned` (no code exists yet; this reviews the contract against the code it will call).

## Verdict: iterate-to-refine

No BLOCKER. Three MAJOR requirement defects (F1-F3) — the contract's security answer (§6.3 (a)/(c)) claims bounds that the cited readers do not give. Each is a small P1 amendment; none changes the design.

## Findings

### F1 — MAJOR — the canon read is not a capped read (claim in §6.3(a) is false for the canon)
- **Where:** `mapper/reqharness/derive.py:199-215` (`load_canon`: `path.read_bytes()` then a size check AFTER the full read; limit `LIMIT_ROLES_YML_BYTES` = 4 MiB, `config.py:64`); contract LLR-RMA.1.1 (adapter "shall obtain the canon from `load_canon`"), §6.3 (a) ("bounded by `MAX_MAP_BYTES`, the NUL/UTF-8 checks"), LLR-RMA.1.4 "one canon reader".
- **What:** `load_canon` reads the whole file before checking size, does no NUL probe, no link/reparse/special-file check. `<repo>/REQUIREMENTS.md` in an untrusted clone can be a symlink/junction (read of an arbitrary target), a FIFO/device (hang), or a huge/growing file (full allocation before refusal). The descriptor gets `osopen.read_capped` (stat + capped re-read + NUL probe, `osopen.py:110-149`); the other new input does not. The task premise "every new read path goes through the capped readers" does not hold for the canon.
- **Fix (amend LLR-RMA.1.1 and §6.3(a)):** the adapter reads the canon through `osopen.read_capped(path, MAX_MAP_BYTES)` after an `lstat` that refuses a link (`osopen.is_link`) or non-regular file, then calls `parse_canon(text)` (still the one parser; M-RMA-2 counts `parse_canon`, so it still holds). If instead `load_canon` itself is hardened it touches `reqharness` (existing consumers + a source file in Inc-4/5 budget) — state which. Add arms: symlinked canon, FIFO/dir named `REQUIREMENTS.md`, cap±1, NUL.

### F2 — MAJOR — `structure: unavailable (canon: <ValidationError text>)` can print a path
- **Where:** LLR-RMU.1.2 row "canon problem"; `derive.py:205-206` (`cannot read ({exc})` — an `OSError` string carries the absolute path) and `:213-214` (`not valid UTF-8 ({exc})`, a `UnicodeDecodeError` text with byte offsets/values).
- **What:** violates the contract's own rule (§6.3(c), LLR-RML.1.1: refusals name causes, never paths) and the batch privacy rule (home path in terminal output / pasted evidence). The pre-existing audit already prints such text on its stderr failure path; R1 must not widen it onto stdout.
- **Fix:** the line prints a fixed cause from a closed set (`file not found`, `cannot read`, `not UTF-8 text`, `exceeds the byte limit`, `looks binary`, `is a link`) — map from `ContentReadError`/exception TYPE, never `str(exc)`. AT-122/121 arm: a repo path containing a marker string must not appear in stdout.

### F3 — MAJOR — discovery of `<repo>/*.relmap.yml` is unspecified for links, special files and count
- **Where:** LLR-RML.1.2 (discovery sentence), LLR-RML.1.1 (`read_capped`: `os.stat` and `open` follow links, `osopen.py:127-130`; a FIFO stats as size 0 and `open` blocks).
- **What:** (1) a matching entry may be a symlink/junction/reparse point, a directory, a FIFO/device or a hard-linked file; the contract confines only the descriptor's INNER paths (LLR-RML.1.3), not the descriptor file. (2) No cap on the number of descriptors: N files x up to 8 MiB parse x one block each (and, as written, one canon derivation per block). Many-files DoS and unbounded output.
- **Fix:** per match: `os.lstat`; refuse (`structure: refused (<base name>): link`/`not a regular file`) when `osopen.is_link` or not `S_ISREG` (hard-link check optional, read-only so LOW); cap descriptors evaluated (suggest 8, then one `structure: refused: more descriptors than the limit (8)` line); derive the canon map ONCE and reuse for every block. Add arms: symlink, directory named `x.relmap.yml`, 9 files.

### F4 — MAJOR — repository-derived values are escaped but not length-bounded
- **Where:** LLR-RMU.1.2/1.3; `derive.py:74` (`_ROW_ID_RE = ^(HLR|LLR)-\S+$` — id length unbounded, up to the 4 MiB canon); `sources` line prints `us_canon`/`at_table` text; "any other top-level key is kept as a note" (LLR-RML.1.2) with non-string/arbitrary keys; descriptor base name.
- **What:** `_visible` (`audit.py:81-107`) is correct for control/bidi/zero-width/combining (verified: C0/C1/DEL/CR/LF/Cf/Zl/Zp/Mn/Me/Zs/variation selectors; every returned line is prefixed `structure…`, so a forged `verdict:` line is not reachable) but expands a character to up to 6, and nothing caps a line. An unlinked LLR id (note lists the first 5 ids) or a descriptor string can print megabytes. The 20-gap cap bounds count, not size.
- **Fix:** truncate every interpolated repository value to N characters (suggest 120, `…`) BEFORE escaping; cap note lines (e.g. 5 + overflow) including unknown-key notes, `str()`-coerce and escape non-string keys; arm: 1 MiB id, 1 MiB `us_canon`.

### F5 — MED (MAJOR) — YAML parse-failure text must be a constant
- **Where:** LLR-RML.1.1 ("parse failure" is one of the 7 causes, no wording rule); `store.py:711-760` lets `yaml.YAMLError` propagate to the caller, and a `MarkedYAMLError` string embeds a source snippet and line/column.
- **What:** if the descriptor path formats `str(exc)` the operator-controlled snippet reaches the line (escaped, but content and length unbounded).
- **Fix:** add to LLR-RML.1.1: parse failure prints the constant `not valid YAML` only; arm with a hostile snippet. Also catch `ConstructorError`/unhashable-key errors from `safe_load` under the same cause.

### F6 — MED (MAJOR) — reach/ranking has no work bound at the cap
- **Where:** LLR-RMM.2.2 (`reach` = distinct reachable count, no memoisation stated), LLR-RMG.1.3 (rank by severity then reach), LLR-RMG.1.1 (cycle gap reach = max over members), LLR-RMM.1.3 (caps checked after the input lists already exist).
- **What:** one BFS per gap candidate is O(gaps x (V+E)); at the 100,000 caps with many gaps or a large cycle ≈ 10^10 steps — a hang, not a refusal. Harmless on today's canon (depth-2 forest, premise 14) but `build_map`/`reach` are the public API R2 consumes, and a 4 MiB canon can hold ≫ 7 gaps.
- **Fix (R1-sized):** compute reach lazily only for the gaps that will be printed after a severity-first sort, or memoise per-node; add one arm at the cap (100,000 nodes, 100,000 HLR-without-LLR gaps) with a wall-clock bound; for cycles bound the per-member work. If deferred, carry as a named constraint on R2 (owner: R2 PDR) and say so in §6.3.

### F7 — LOW (MINOR) — build problems are never surfaced
- **Where:** LLR-RMM.1.2 (duplicate id, unsafe id, … are collected as `Problem`) vs the LLR-RMU.1.2 line table (no line for them).
- **What:** a hostile or duplicated canon row is silently dropped from the graph; the summary counts differ from the canon with no explanation (fail-quiet).
- **Fix:** one `structure note: <n> rows excluded (<kind>=<k>, …)` line, count only, no values.

### F8 — LOW (MINOR) — descriptor/`us_canon` strings: confirm confinement runs before any filesystem call
- **Where:** LLR-RML.1.3; `osopen.confine_reason` doc order (allow-list and lexical checks precede `lstat`; UNC/device/drive forms refused first).
- **What:** read from the docstring only (not executed): the order is right and R1 does not open the paths (arm: monkeypatched `open` raises). Keep the arm that asserts a UNC string causes zero stat calls, so a hostile descriptor cannot trigger a network lookup.

## Checked and clean (named so a reader sees what was examined)
- **Read-only adapter:** LLR-RMA.1.4 forbids writes/processes/extra opens and has a tree-hash arm plus an isolation census (no `subprocess` import, ARCH row bans network and any write). The one gap is F1 (the canon open itself).
- **`run_cli` hook surface:** `extra_lines` is a code parameter supplied only by `app.py`; `argv` handling is untouched (`audit.py:363-394`); no shell, eval or subprocess; hook failure is caught as `Exception` and prints only the exception TYPE name (LLR-RMU.1.1), exit code unchanged. No injection path found. Residual: no time bound on the hook (covered by F3/F6 bounds).
- **Terminal-escape injection:** per-value `_visible` plus the `structure…` prefix on every line closes ESC, bidi, U+2028/2029 and forged-verdict vectors (F4 is about size, not escaping). The AT-122 arms (control, bidi, U+2028 in id, statement cell, descriptor base name) are the right set.
- **Prescan reuse (R-017):** the extraction keeps one definition of anchor/alias/depth refusal; iterative event scan, no `RecursionError`; byte-identity gated by the unchanged `tests/test_ingestion_limits.py`. Anchor name stays truncated. Risk is behavioural drift of `store` messages — mitigated by the stated gate, no security finding.
- **YAML loader:** `safe_load` only, behind the prescan (`tests/test_reqharness_yaml_census.py` pinned).
- **Descriptor size:** 8 MiB via `read_capped` with TOCTOU-safe capped re-read; empty, binary and non-UTF-8 arms present. Depth 64/65 arms present.

## Owed to close (for the re-review)
F1, F2, F3 amended in P1 with their arms; F4 and F5 amended or named `open` with the owning increment; F6 either bounded in R1 or carried as a named R2 PDR constraint; F7/F8 may ride as Phase 3 notes. A clean verdict needs the amendments APPLIED in the contract and then each mitigation verified at its increment gate.
