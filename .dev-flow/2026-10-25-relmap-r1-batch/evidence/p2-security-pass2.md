# P2 security review, second pass (trigger C6) — relmap-r1 batch

Reviewer: security-reviewer (independent). Read-only; no edits other than this file. Scope: amended `01-requirements.md` (LLR-RML.1.1/1.2/1.3/1.5/1.6, RMA.1.1, RMG.1.3, RMM.2.2, RMU.1.1-1.4, IFC), `01-requirements-ledger.md` LED .5-.9 and .12-.13, last two `decisions_log` entries, against the code they call (`mapper/osopen.py`, `mapper/reqharness/derive.py`, `mapper/reqharness/audit.py`). Evidence state of all verifications: `planned` (requirement text; no code exists yet) — each is to be re-verified at its increment gate.

## Verdict: approve

All eight first-pass findings are closed at the contract level. No BLOCKER or MAJOR new finding. Three MINOR items (N1-N3) are carried into Phase 3 as named notes, with owning increments below.

## Per-finding table

| # | First-pass finding | Status | Evidence |
|---|---|---|---|
| F1 | Canon read uncapped, follows links | **verified** | LLR-RML.1.5: `read_repo_text` = `os.lstat`, refuse `osopen.is_link` and non-regular BEFORE any open, then `osopen.read_capped` (stat + capped re-read + NUL probe, `osopen.py:110-149`); cap for canon = `LIMIT_ROLES_YML_BYTES` (4 MiB, same as `load_canon` enforced). LLR-RMA.1.1 no longer calls `load_canon`; `parse_canon` still the single parser. Arms: link, directory, FIFO (where `mkfifo`), cap±1, NUL, non-UTF-8; mutants M-RML-7/8. §6.3(a) now true. |
| F2 | Canon-problem line could print OS error text / path | **verified** | LLR-RMU.1.2 row `structure: unavailable (canon: <cause K1-K7>)`; K1-K7 are fixed strings classified from the `ContentReadError` prefix, any other `OSError` is K4 (LLR-RML.1.5). AT-126(c) places a marker string in the repo path and asserts it never appears in stdout. |
| F3 | Discovery: links/special files/unbounded count | **verified** | LLR-RML.1.6: sorted, max 8 evaluated, one overflow line, link/dir/non-regular -> K1/K2 by base name, canon derived once (`test_canon_derived_once`, parse_canon count 1 across 3 descriptors); census arms 0/1/2/8/9 + dir + link; M-RML-9/13. |
| F4 | Values escaped but unbounded | **verified** | LLR-RMU.1.2: every repository-derived value cut to 120 chars (`…`) BEFORE escaping; notes <=10 + overflow, unlinked ids first 5, gaps <=20; ignored keys `str()`-coerced and cut; AT-129 + M-RMU-5; numeric threshold 121 -> 120+`…`. Escaper re-checked: `_visible` (`audit.py:81-107`) unchanged; every hook line prefixed `structure…`, so no forged `verdict:` (LLR-RMU.1.3 asserts exactly one such line). |
| F5 | YAML failure text could carry a snippet | **verified** | LLR-RML.1.1: every `safe_load` failure (`YAMLError` incl. `ConstructorError`/`ComposerError`, `ValueError` big int, `RecursionError`) is K10 `not valid YAML`; message = fixed cause + base name only; arms with hostile snippet and 5,000-digit integer; M-RML-10. |
| F6 | Reach/ranking unbounded | **verified** | LLR-RMG.1.3 / ledger .8: iterative BFS, result cached per node and per cycle component, computed only for the severity bands needed to fill `limit`, hard bound 2,000,000 visits; uncomputed gaps rank reach 0 and are returned as `reach_not_computed`. Arms: 100k chain, hub shape (50,000 gaps sharing one 50,000-node reach) under a 30 s ceiling, 100k sinks; M-RMM-8, M-RMG-5. Degradation reviewed in N4 below: safe. |
| F7 | Builder problems never surfaced | **verified** | LLR-RMU.1.2 count line `structure: notes excluded=<T> (<kind>=<n>,…) unknown_status=<u> reach_not_computed=<r>`: counts only, kind names from the closed six, never a value; AT-124 (`nodes + excluded = parsed rows`); M-RMU-7. |
| F8 | UNC/hostile path must not touch the filesystem | **verified** | LLR-RML.1.3: `confine_reason` before any filesystem call; refusal K17 with `<reason>` from the closed set; threshold "0 opens and 0 `stat` calls for a UNC string" (monkeypatched `open`/`os.stat` raise). R1 never opens `us_canon`/`at_table`. See N2 for the resolved-path print. |

## New-surface check of the amendments

- **Visit-bound degradation (N4, clean):** severity is the primary sort key and reach only breaks ties inside a band, so uncomputed gaps never hide a HIGH behind a MED; the total `gaps:` line counts all gaps independent of reach; the loss is visible as `reach_not_computed=<r>` on the count line. Failure mode is a mis-ordered tie-break, not a hang or a silent drop. 2,000,000 visits of pure-Python BFS is seconds, within the 30 s ceiling arm.
- **Count line / notes content (clean):** counts and closed-set names only; values printed in notes (unlinked ids, ignored keys, configured paths, reported-row text) are cut and escaped; no value reaches the count line.
- **No-repo / no-registry lines (clean):** LLR-RMU.1.1 prints the fixed lines `structure: unavailable (no repository)` / `(no registry)` from `run_cli` without calling the hook (0 calls, M-RMU-4); no path or exception text; exit code unchanged. A raising hook prints only the exception TYPE name.
- **Hook injection surface (clean):** unchanged from pass 1 — `extra_lines` is a code parameter set only by `app.py`; `report.repo` is the root `audit` resolved; no shell, eval or subprocess; ARCHITECTURE bans `subprocess`/network/writes in `relmap`.
- **Refused descriptor yields only its refusal line:** no partial map is printed from a refused file; the canon block is not duplicated per descriptor (derived once).

## New findings (all MINOR / LOW, none gating)

- **N1 — LOW — lstat-then-open race in `read_repo_text` (owner: Inc-3).** Between `os.lstat` and `osopen.read_capped`'s `os.stat`/`open` a path can be swapped for a link or FIFO. Needs write access to the audited repository and the read stays read-only and capped, so impact is bounded to one capped read; acceptable. Optional hardening: after `read_capped`'s open, compare `os.fstat` identity with the lstat result, or state the residual in §6.3 as accepted.
- **N2 — LOW — print the descriptor string, never the resolved path (owner: Inc-3/Inc-5).** `safe_local_path` expands `~` and `confine_reason` returns a resolved `Path`. LLR-RMU.1.2 prints `us_canon=<path>`; state that the printed value is the configured string (cut and escaped), not the resolved `Path`, otherwise a `~/…` entry prints the operator's home path. Add one arm: `us_canon: ~/x` prints `~/x`.
- **N3 — LOW — wording of "memoised" reach (owner: Inc-1).** The visit bound makes cached BFS safe; do NOT implement the memo as per-node reach SETS (O(n²) memory on a 100,000 chain). LLR-RMM.2.2 should say "result count cached", and `test_reach_chain_at_cap` should also bound peak memory or assert no per-node set is retained.

## Gate

Approve. Carried to Phase 3: N1, N2, N3 as named notes with their increments. Each first-pass mitigation was verified at the contract level only; the clean verdict for shipping still requires the executed arms named above (F1/F3/F8 at Inc-3, F2/F4/F7 at Inc-5, F5 at Inc-3, F6 at Inc-2) to be run and re-verified at each increment gate.
