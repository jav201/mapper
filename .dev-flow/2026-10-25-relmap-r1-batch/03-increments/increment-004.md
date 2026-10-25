# Increment 004 — US-RM-001 · `The read-only canon adapter, the snapshot fixture and the adapter tests`

> **Artifact language.** English (the batch language). **Owed in.** `core` ✓ · `full` ✓
> Where this lives: the repo, `.dev-flow/2026-10-25-relmap-r1-batch/03-increments/increment-004.md`. Written by the
> `software-dev` author in the batch worktree on branch `feat/relmap-r1` (base `e83e686`, Inc-1..3 approved); the transcripts it
> cites are under `.dev-flow/2026-10-25-relmap-r1-batch/evidence/`, redacted of the account name (`<user>`) before hashing.

| Field | Value |
|---|---|
| Batch | `2026-10-25-relmap-r1-batch` |
| Increment | `004` |
| Lane (if the batch forked) | none — one chain · module `relmap` |
| Requirement(s) | US-RM-001 · HLR-RMA.1 · LLR-RMA.1.1, .1.2, .1.3, .1.4 · LLR-RMG.1.2 (snapshot arm) · ledger `.4`, `.36` (snapshot pin), `.44` (cut), `.48` (Problem subjects raw), `.49` (unique pairs), `.50` · PDR conditions PD-1 (architect), D-2, D-4 (QA) |
| Acceptance | Layer B: none — AT-117, AT-119, AT-124, AT-125 run `mapper --audit` through the hook that lands in Inc-5 · Layer A stand-ins here: `test_snapshot_structure_figures` (275/196/7/3, the 7 report notes + the unlinked list), `test_snapshot_gaps` (7 gaps, qualifier on 2), `test_duplicate_and_unsafe_ids_are_counted_never_linked` (AT-124 figures) |
| Agent | `software-dev` |
| Date | 2026-10-25 |

---

## 1 · What changed

**`mapper/relmap/adapter.py`** (D3 names, frozen): `derive_reqharness_map(repo, descriptor) -> Derivation`, `Derivation(map, reported, unlinked, unknown_status)`
and `CanonUnavailable(cause, limit)`. The canon is read ONCE through `descriptor.read_repo_text(<repo>/<descriptor.canon>, LIMIT_ROLES_YML_BYTES)` (a `RepoReadError`
becomes `CanonUnavailable` carrying the same fixed K1–K7 text and cap) and parsed ONCE with `reqharness.derive.parse_canon`. One `Node` per returned object (`kind` = class,
`title` = the statement cut with `model.cut`, `status` = first word of the Status cell lower-cased, `open=False`, canon order); `sourced = {HLR, LLR}` (US/AT/TC unsourced, so
`gaps.detect_gaps` keeps every row that needs them silent). **Rule D-1:** an LLR's candidate is `HLR-` + its id minus the last dotted segment; a `refines` edge is drawn only when the
candidate is an HLR node, else the LLR is listed in `unlinked` (canon order), never attached to a shorter prefix. **Reported rows:** each `parse_canon` report becomes one printed note
(`unparsed row <id>`, the id read back from the report's `{id!r}` with `ast.literal_eval`; `unparsed canon line` when the report names no id); no node, no edge. **`Node.unparsed`** of an
HLR = the orphan LLR ids (reported LLR rows + unlinked LLRs) near it, counted in one pass by the two disjoint relations of LLR-RMA.1.3 (starts-with and sibling-stem). A status word outside
{active, deferred, superseded, withdrawn, split} keeps the node and is counted in `unknown_status`. `build_map` is called twice: first with no edges to learn which nodes the builder keeps
(a duplicate or unsafe id is excluded there), so an edge is never drawn to or from an excluded node (which would add an `unknown endpoint` problem and break AT-124's counts); then with the
final nodes (`unparsed` filled) and edges. Read-only: no write, no subprocess, no open but the canon; `us_canon` / `at_table` are never opened.

**Snapshot and pin.** `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` is `git show HEAD:REQUIREMENTS.md` (LF bytes, 0 CR). `test_snapshot_sha256` pins the LF-normalised sha256
`b093c920…a25a` (authoritative, ledger `.36`); `test_snapshot_sha256_crlf_arm` hashes a CRLF-rewritten copy and must give the same value;
`test_snapshot_pin_matches_the_ledger_while_the_batch_folder_exists` cross-checks the constant against the ledger entry `.36` text; `.gitattributes` gains
`tests/fixtures/relmap/** -text` (CRLF line, like its neighbours); `test_gitattributes_keeps_the_fixture_bytes` asserts the line.

**Figures derived from the snapshot (all as the contract states, no difference):** 275 nodes (76 HLR, 199 LLR) · 196 edges (all `refines`) · 7 reported rows (`LLR-HYG.1.1`, `LLR-CAN.1.1`,
`LLR-CAN.1.2`, `HLR-RH.6`, `LLR-RH.6.1`, `LLR-RH.7.3`, `LLR-Q3.1.2`, canon order) · 3 unlinked (`LLR-REPAIR.1`, `LLR-REPAIR.2`, `LLR-RH.6.2`) · 0 problems, 0 cycles, 0 unknown status · 7 gaps, all
`HLR WITHOUT LLR`, the qualifier `(canon rows near this id could not be parsed or linked: 2)` on `HLR-CAN.1` and `HLR-REPAIR.1` only. Live canon at this commit (evidence, not asserted): the same
275/76/199/196/7/3/7 (the worktree canon equals the snapshot today).

**Same-landing amendment:** `docs/ARCHITECTURE.md` §2 `relmap` row gains `mapper/relmap/adapter.py` ("as built Inc-1 to Inc-4"; the audit path stays planned for Inc-5). The §3 row already
named `adapter` and the isolation allow-list already admits `parse_canon`/`LIMIT_ROLES_YML_BYTES`; no allow-list change was needed (the adapter imports no `osopen` name).

---

## 2 · Files modified

| File | Kind | Traces to | Change |
|---|---|---|---|
| `mapper/relmap/adapter.py` | source | LLR-RMA.1.1–.1.4 (D3) | NEW (~160 lines) |
| `tests/test_relmap_adapter.py` | test | LLR-RMA.1.1–.1.4, LLR-RMG.1.2 | NEW: 38 nodes |
| `tests/fixtures/relmap/REQUIREMENTS.snapshot.md` | fixture | LLR-RMA.1.1, ledger `.36` | NEW: LF bytes, sha256 `b093c920…` |
| `.gitattributes` | config | PD-1 (LLR-RMA.1.1) | one line `tests/fixtures/relmap/** -text` |
| `docs/ARCHITECTURE.md` | doc | R-016 | §2 `relmap` row: adapter path |
| this packet and `evidence/inc4-*` | doc | | 8 redacted transcripts |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** (`relmap/adapter.py`) |
| Test files | 1 new (uncapped) + 1 fixture |
| Doc / config files | 2 (outside the count) |

`tests/_relmap_fixtures.py` is NOT created: the proposal assigns it to Inc-5 (§2.1 row 5). Commits: `f3cded2` (code, tests, fixture, evidence) · the packet commit follows it.

---

## 3 · How to test

```bash
cd <worktree>   # C:/Users/<user>/AppData/Local/Temp/ds-units/wt-r1
export PYTHONPATH=<worktree>
env -u NO_COLOR -u TERM python -c "import mapper; print(mapper.__file__)"      # must resolve inside the worktree
git add mapper/relmap tests                                                   # the A3 census needs new files staged
env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_relmap_adapter.py tests/test_relmap_isolation.py tests/test_relmap_gaps.py
env -u NO_COLOR -u TERM PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/test_relmap_*.py tests/test_mod_*.py tests/test_repair_map_truth.py tests/test_arch_osopen_callers.py tests/test_a3_census.py tests/test_no_operator_paths.py tests/test_prescan_refusal_goldens.py tests/test_yamlscan.py tests/test_reqharness_registry.py
```

Targeted files only; never the full suite. `mapper.__file__` printed `C:\Users\<user>\AppData\Local\Temp\ds-units\wt-r1\mapper\__init__.py` (executed, before the first run).

---

## 4 · Test results

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** (status words, rule D-1, orphan counts, report-id reader) | `core` · `full` | `test_relmap_adapter.py` (38) | executed: GREEN |
| **A · white-box** `TC-NNN` ↔ LLR; Layer A stand-ins for AT-117/119/124/125 | `core` · `full` | same file; `test_relmap_isolation.py` census covers `adapter.py` (imports, floor, no-write bans) | executed: GREEN |
| **B · black-box** `AT-NNN` through the shipped surface | `core` · `full` | n/a — AT-117, -119, -124, -125 first realise at Inc-5 (the hook) | n/a — Layer B starts at Inc-5 |

Adapter file alone: **38 passed**, exit 0, 1.3 s (`evidence/inc4-green-first.txt`; see §6 item 8 for the one test-source fix before this run). Final run, adapter + isolation + gaps: **187 passed**, exit 0, 7.5 s
(`evidence/inc4-green-final.txt`). Guard run — `test_relmap_*` ×6, `test_mod_*` ×7, `test_repair_map_truth`, `test_arch_osopen_callers`, `test_a3_census`, `test_no_operator_paths`,
`test_prescan_refusal_goldens`, `test_yamlscan`, `test_reqharness_registry` (the `parse_canon` consumer): **538 passed, 1 skipped** (FIFO arm, `n/a - Windows has no mkfifo`), exit 0, 64.7 s
(`evidence/inc4-guards.txt`); the A3 pin 86 did not move. `test_no_operator_paths` re-run alone just before the commit: 68 passed with the A3 and map-truth files. **Measured wall time:** nothing heavy;
the slowest nodes are the 4 MiB cap±1 reads (`test_canon_causes[K5]`, `test_canon_at_the_cap_loads`), under 0.2 s each. No elapsed-time assertion anywhere.

**Fresh checkout (PD-1).** After the commit, two clones of the branch: `core.autocrlf=false` (LF) and `core.autocrlf=true` (CRLF). In both, the fixture has 0 CR bytes and raw sha256 `b093c920…` (`-text` held: `git ls-files --eol` shows
`attr/-text w/lf` for the fixture while `adapter.py` is `w/crlf` in the autocrlf clone); `test_snapshot_sha256`, `_crlf_arm`, `test_snapshot_census`, `test_snapshot_gaps`, `test_gitattributes_keeps_the_fixture_bytes`:
5 passed in each (`evidence/inc4-fresh-checkout.txt`). The clones were deleted afterwards.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | (1) code-absent: `adapter.py` moved out of the tree, tests present; (2) move-aside of `adapter.py` with hash check; (3) 19 mutants (next table) |
| Instrument | `mutants.py` and `run.sh` (scratch outside the repo): hash before, one edit, the targeted pytest run, restore from bytes, hash after, one verdict per mutant |
| Where it ran | the batch worktree, by the `software-dev` author; deterministic, the orchestrator may re-run |
| Transcript | `evidence/inc4-red-code-absent.txt`, `inc4-red-moveaside.txt`, `inc4-red-mutants-battery.txt` |
| Restore proven by | sha256 after every arm equals the one before: `adapter.py` `cd58d797…`, `gaps.py` `dd180acf…`, test file `c658f3ee…`, fixture `b093c920…` |
| Bytecode cache | `-p no:cacheprovider`, `PYTHONDONTWRITEBYTECODE=1`; each arm its own process |
| Arms resolved at baseline | the adapter file GREEN (38 passed) before the battery |
| Verdict granularity | per mutant, by failing node ids |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | (1) code-absent: `ImportError: cannot import name 'adapter' from 'mapper.relmap'` at collection (exit 2); (2) move-aside: the same error, exit 2, `adapter.py` sha256 equal before and after (`cd58d797…`) |

| Field | Value |
|---|---|
| **Mutation verdicts** | 19 mutants, **19 KILLED, 0 SURVIVED**, every restore hash-equal. Contract mutants: **M-RMA-1** (nearest HLR prefix) → `test_an_unlinked_llr_is_never_attached_to_a_prefix` · **M-RMA-2** (second parse) → `test_canon_is_read_once_through_read_repo_text` · **M-RMA-3** (re-parse a pipe row by splitting on 4 pipes) → 7 (census, figures, gaps, live, D-1 row) · **M-RMA-4** (opens `us_canon`) → `test_readonly` · **M-RMA-5** (starts-with branch only) → `test_snapshot_unparsed_counts`, `test_snapshot_gaps`, `test_unparsed_counts` · **M-RMA-6** (skip the last row) → 20 incl. `test_live_invariants` · **M-RMA-7** (append a byte to the fixture) → `test_snapshot_sha256` and its CRLF arm · **M-RMA-8** (id regex) → 8 (tripwire shape + every count) · **M-RMA-9** (hash raw bytes) → `test_snapshot_sha256_crlf_arm` only · **M-RMG-3** (gaps ignore `sourced`, in `gaps.py`) → 13 (`test_snapshot_gaps`, `test_unsourced_kinds_…`, the Inc-2 gaps tests). Extra, mine: M-RMG-3b (adapter sources all five kinds) 4 · M-RMA-10 (`unknown_status` never counted) 2 · M-RMA-11 (status keeps case) 1 · M-RMA-12 (title not cut) 1 · M-RMA-13 (edges from every parsed node: duplicate or unsafe id) 1 · M-RMA-14 (cap is not the derive limit) 9 · M-RMA-15 (id-less report dropped) 1 · M-RMA-16 (HLR rows counted as orphans) 1 · M-RMA-17 (unlinked not in canon order) 1 · M-RMA-18 (no first pass: an unsafe LLR stays in `unlinked`) 1. The numbers M-RMA-10…18 are not contract ids; they are this packet's. |

M-RMA-9 mutates the test helper `lf_sha256` (the adapter holds no hash), as the contract's wording implies; M-RMA-7 also reddens the CRLF arm because both hash the same bytes.

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| independent line counter (`_counted_rows`) | `test_live_invariants_see_a_dropped_row`: the counter's total minus one derived node must NOT satisfy the equation | passes only because the equation breaks off by one; M-RMA-6 on the real adapter → `test_live_invariants` RED |
| open / process tally in `test_readonly` (patched `os.open`, `builtins.open`, `io.open`, `subprocess.*`, `os.system`) | M-RMA-4: the adapter opens `us.md` | RED (the recorded names include `us.md`) |
| report-id reader tripwire | `parse_canon` over pipe-bearing rows incl. an id with a quote and a backslash, a header-only report, a trailing-text variant | M-RMA-8 → RED; the id-less and trailing-text arms return `None` |
| hash helper | the CRLF arm hashes a CRLF-rewritten copy, asserted different from the LF bytes first | M-RMA-9 → RED |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 4 instruments, each shown RED by a mutated or known-bad input |

### Emitted-form assertion — assert the bytes the producer EMITS (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the derivation notes (`Derivation.reported`, `.unlinked`) | compared to the exact strings AT-119 prints (`unparsed row <id>` ×7 in canon order; the three unlinked ids) | GREEN on the snapshot |
| the gap sentence with the qualifier (through `detect_gaps`) | `sentence.endswith("(canon rows near this id could not be parsed or linked: 2)")` | GREEN |
| `CanonUnavailable` text | `str(err) == CAUSE[Kn]` for K1–K7, `.limit == LIMIT_ROLES_YML_BYTES` (no path, no exception text) | 7 arms GREEN |
| the fixture bytes on a fresh checkout | raw sha256 and CR count in LF and CRLF clones | `b093c920…`, 0 CR, both |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 4 artifacts, each asserted against the form its producer wrote |

### Evidence files — bytes at a declared home, verbatim, hash-verified (C-59)

| Evidence artifact | Path — under `artifact_homes.evidence` (`.dev-flow/2026-10-25-relmap-r1-batch/evidence/`) | SHA-256 |
|---|---|---|
| RED, code-absent (exit 2) | `inc4-red-code-absent.txt` | `c363028975fc4dde7797b3b16ad2656c407159eb291c78b3f469c8487fb9e1e9` |
| RED, move-aside (exit 2, restore hash equal) | `inc4-red-moveaside.txt` | `4ac769149da5acba43b62ef233510d310cc69538c9f15913a3f3402466522c85` |
| GREEN, adapter file (38 passed, 1.3 s) | `inc4-green-first.txt` | `d1ed29d9958b66ce97653b81fdbb879f2d909632c695e163173ba71e55e04baa` |
| GREEN, adapter + isolation + gaps (187 passed, 7.5 s) | `inc4-green-final.txt` | `2882d2046af1fffd12d64c52679ec50869ac36de9d066e226ef223f0e196575e` |
| Guard suites (538 passed, 1 skipped, 64.7 s) | `inc4-guards.txt` | `b7f4a0a5f250189a78903d2d9f0ca8744a9ec5c1a79c6ada5f46fce46e3f9628` |
| 19-mutant battery | `inc4-red-mutants-battery.txt` | `b3a12d70d6a9d6cd54a5beda1afaa8ea92aca8e72287a5e4ac20d87d13a196e9` |
| Fresh LF and CRLF checkout (5 passed each) | `inc4-fresh-checkout.txt` | `516151a65b8a03bf545bc9d9ab125e1709885bf2625a9df5c5e69ac522f188bb` |
| Gate (`devflow-validate --brief .`, exit 1, blocks only) | `inc4-gate.txt` | `5672b8eac6bbb8733940dcd39fad1633721f74c84942d2913be3c1af047d9517` |

| Field | Value |
|---|---|
| **Evidence files** | 8 artifacts at the declared home, each with its digest prefix; every transcript is redacted (`<user>`) before hashing and records its exit code and wall time (the battery records per-arm wall time) |

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | yes: (a) "the snapshot has no duplicate, unsafe or unknown-status rows" (0 problems, 0 unknown); (b) "no US/AT/TC node exists, so those gap rows are silent"; (c) "the adapter opens nothing but the canon" |
| If the result is an ABSENCE, what made the search wide enough | (a) asserted on the derived map, not by grep (`m.problems == ()`, `unknown_status == 0`); (b) the same test feeds a synthetic canon and an adapter that sources all five kinds (M-RMG-3b) and goes RED; (c) every open door a derivation can use (`os.open`, `builtins.open`, `io.open`) is recorded while it runs |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_live_invariants_see_a_dropped_row` protects `test_live_invariants`; `test_readonly`'s tally is proven by M-RMA-4 |
| Conjunctive criteria: one mutation per conjunct | the orphan relation has two branches: M-RMA-5 removes the sibling branch, the starts-with branch is covered by `HLR-CAN.1`/`HLR-M.1`; the class filter is M-RMA-16 |
| Synthetic instance of the absent case | `test_duplicate_and_unsafe_ids_…` (duplicate, U+202E, U+200B, NBSP, `Done`), `test_status_words`, the five-row D-1 table |
| **Positive control for every probe that returned an ABSENCE** | the snapshot arm for (a) is paired with the synthetic arm that DOES produce problems and unknown status; for (c) M-RMA-4 makes the tally non-empty of `us.md` |

### Reverse census — trigger family B, and A3

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by other tests | `git grep -n "derive_reqharness_map\|CanonUnavailable\|relmap.adapter" -- mapper tests docs` | only the new module, its test and the ARCHITECTURE row/`internal order` sentence; no earlier test references them |
| B2 file moved on disk | none moved | no readers to find |
| B3 byte-identical golden captures this source | `git grep -il "relmap" -- tests/goldens` | 0 hits |
| B4 artifact produced here is consumed elsewhere | the fixture and the adapter | consumer: `test_relmap_adapter.py` now; `relmap.audit` and `tests/_relmap_fixtures.py` at Inc-5 (the 16 `--audit` canon fixtures there write their own canon; the snapshot is the AT-117/119/125 input) |
| B5 fixture content (a NEW input class: a committed copy of the canon) | `git ls-files tests/fixtures` and the content scan of `tests/**/*.py` for `REQUIREMENTS.snapshot` | only `tests/test_relmap_adapter.py` names it; the fixture is not a tracked canon for any existing test |
| A3 interface consumed by another module changed | `test_mod_*`, `test_repair_map_truth`, `test_arch_osopen_callers`, `test_a3_census` | all in the 538-pass guard run; the A3 pin 86 unmoved; `derive.py` untouched |

| Field | Value |
|---|---|
| **Reverse census** | 6 probes run, each with its command and verdict; B2 did not fire |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| ARCHITECTURE §2 `relmap` paths: "the adapter and audit modules are planned for Inc-4 and Inc-5" → adapter built | statements that the adapter path is planned | `grep -n "adapter.py\|planned for Inc-4" docs/ARCHITECTURE.md` (the edit script asserted the old sentence occurs exactly once) | 1 | 1 | `audit` stays "planned for Inc-5"; the §3 row already named `adapter` |

| Field | Value |
|---|---|
| **Correction population** | 1 correction family, 1 sentence, matched exactly once before replacement |

#### Supersession-completeness inspection (V-3)

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|-------------------|-------------|------------------------------|----------------------|
| `adapter and audit modules are planned for Inc-4 and Inc-5` | `grep -c` over `docs/ARCHITECTURE.md` → 0 | yes | `docs/ARCHITECTURE.md` §2 `relmap` |

### Signed-balance test ledger

`post = base − deleted + added` → `38 = 0 − 0 + 38` for `test_relmap_adapter.py` (collected with `--collect-only`); no other test file changed.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer — Claude Sonnet subagent executing agents/code-reviewer.md + agents/security-reviewer.md · approve-with-nits` · no BLOCKER, no MAJOR; F1 (surviving reviewer mutant C: the `"." in s` guard at `adapter.py:114`), F2 (raw uncut ids in `Derivation.reported`, owed by Inc-5), F3 (`RelMapLimitError` from the first `build_map`, owed by Inc-5), F4 (ledger cross-check indexing) · `evidence/review-inc004.md` |

**Follow-ups recorded after the review (done with Inc-5, commit below):** **F1** — `tests/test_relmap_adapter.py::test_unparsed_count_of_a_dotless_hlr_is_not_doubled` (`HLR-X` with a reported `LLR-X.1` has `unparsed == 1`); reviewer mutant C re-run for real: RED on that node only, restore hash-equal (`evidence/inc4f-red-f1-mutant-c.txt`). **F4** — `test_snapshot_pin_matches_the_ledger_while_the_batch_folder_exists` asserts the ledger heading is present before it indexes it. **F2, F3** — discharged in Inc-5 (`increment-005.md` §6).

---

## 5 · Risks

- **A canon with more than 100,000 HLR/LLR rows** (possible inside the 4 MiB cap) makes `build_map` raise `RelMapLimitError`; the adapter lets it propagate (the contract gives no cause for it). Inc-5's hook must turn it into a refusal line, not an uncaught error; its "internal error: <Type>" branch covers it only as a fallback.
- **Two `build_map` calls** per derivation (the first to learn which nodes the builder keeps): 2× the O(V+E) build on the canon; acceptable at the cap, and the only way found to avoid drawing edges to excluded nodes without duplicating the builder's unsafe-id predicate.
- **The id of a reported row is read from `parse_canon`'s report TEXT.** A rewording in `derive.py` would zero every `unparsed` count; the tripwire `test_report_line_shape_yields_id` fails loudly first (M-RMA-8).
- **`test_live_invariants` reads the repository's own `REQUIREMENTS.md`.** It asserts relations, never counts, so it survives canon edits; it fails if the canon gains a table the counter and `parse_canon` read differently (the counter shares the first-`Id`-header rule on purpose).
- **The ledger cross-check skips when the batch folder is absent** (a consumer checkout), by design; the constant itself is still asserted.
- **A symlink to the canon is `unavailable (canon: is a link)`** here while the review report may still count it (security F1, by design, recorded in ARCHITECTURE). The K1 arm patches `is_link` rather than creating a link (the descriptor suite already proves the real symlink and junction paths).

---

## 6 · Pending items / spec deviations

Nothing is deferred silently. Contract issues for the orchestrator (no ledger edit was made):

1. **LLR-RMA.1.3 says "the full report text stays on the map for Layer A".** The frozen `RelMap` has no field for it and `Derivation` is `(map, reported, unlinked, unknown_status)`. I put the PRINTED note text in `reported` (`unparsed row <id>` / `unparsed canon line`); the full report text is not retained (Layer A obtains it from `parse_canon` directly; the tripwire covers the wording). Amend the sentence or add a field in a PDR version bump.
2. **LLR-RMA.1.4 says the adapter "shall add one note per configured `us_canon`/`at_table` reading `configured, not derivable in R1`".** The frozen `Derivation` has nowhere to carry it, and the audit's `format_structure(..., sources=(None, None))` already renders configured sources (Inc-5 `test_sources_line_configured_string`). The adapter therefore ignores both fields (proved: `test_readonly` shows they are never opened) and emits no such note; the sentence reads as describing the audit's sources line. Suggested amendment: move the sentence to LLR-RMU.1.2.
3. **The orphan relation is defined for `LLR-` ids only** (LLR-RMA.1.3: "`LLR-<t>` is related to `HLR-<s>` when…"). A reported `HLR-` row (`HLR-RH.6`) is a note and relates to nothing; the snapshot figures (2 / 2 / 0 on the other gap HLRs) confirm this reading. `test_unparsed_counts_ignore_unrelated_ids_and_hlr_rows` and M-RMA-16 pin it.
4. **`unknown_status` counts only nodes the builder kept** (a duplicate or unsafe id is a `Problem`, not a node). AT-124's `unknown status=1` and `nodes + skipped = parsed rows` are consistent with that; the contract text does not say it.
5. **The edge for a duplicate LLR id is drawn once** (from the node the builder kept), consistent with ledger `.49` (unique pairs); `test_duplicate_and_unsafe_ids_…` asserts it. An LLR with an unsafe id is neither linked nor listed in `unlinked` (it is a `Problem`, counted on the skipped line).
6. **Gate (`devflow-validate --brief .`):** 7 blocks, `evidence/inc4-gate.txt`: `V2` ×7 — `AT-118`, `-120`, `-122`, `-123`, `-126`, `-128`, `-129` have no node on disk (the station-expected Layer B reds minted at Inc-5). **AT-117, AT-119, AT-124 and AT-125 stopped blocking only because `test_relmap_adapter.py` NAMES them** (docstring and test names as Layer A stand-ins), not because a Layer B node exists; the real nodes are Inc-5's. The environmental `V15` ×2 / `V16` ×2 blocks seen at Inc-3 did not appear in this run (no `__pycache__` in the bundle: `PYTHONDONTWRITEBYTECODE=1`).
7. **`tests/_relmap_fixtures.py` is not created here:** proposal §2.1 row 5 assigns it to Inc-5, and no Inc-4 test needs a git repo or the release-test helpers (the tests write a canon into `tmp_path`).
8. **One test-source fix before the recorded GREEN:** my first draft of `test_duplicate_and_unsafe_ids_…` asserted 5 parsed rows where the fixture has 6 (HLR, three `LLR-E.1.1`/`.5`/duplicate, two unsafe); the adapter was right, the arithmetic wrong. The first red run was not kept; `inc4-green-first.txt` is the corrected run (38 passed). The code-absent RED was regenerated afterwards on the final test file.

---

## 7 · Suggested next task

Inc-5 (`mapper/relmap/audit.py`, `mapper/reqharness/audit.py`, `mapper/app.py`, 3 source files): `structure_lines`, `format_structure` (cut inside, notes from `Derivation.reported` and `.unlinked`, sources line for configured `us_canon`/`at_table`, the qualifier already in the gap sentence), the `run_cli(argv, extra_lines=…)` hook and `tests/test_relmap_audit.py` with `tests/_relmap_fixtures.py`; it must also catch `RelMapLimitError` from `derive_reqharness_map` (§5). Before it starts: the orchestrator's independent review of this diff and a decision on §6 items 1 and 2.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 1 / 4: `relmap/adapter.py` (§2) |
| 2 | Tests written in this same increment | all | ✓ | 38 new nodes; 38 passed (`evidence/inc4-green-first.txt`), 187 with isolation and gaps |
| 3 | Layer 0 written where the criterion applies | `core` · `full` | ✓ | rule D-1, status words, the orphan relation and the report-id reader are branching logic; 38 nodes, 19/19 mutants killed |
| 4 | **RED counterfactual** declared | `core` · `full` | ✓ | code-absent and move-aside `ImportError`, exit 2 (`evidence/inc4-red-*`) |
| 5 | **Reverse census** declared | `core` · `full` | ✓ | six probes with commands in §4 |
| 6 | `code-reviewer` passed | `core` · `full` | ✓ | `code-reviewer` approve-with-nits (§4b), nits F1/F4 closed with Inc-5, F2/F3 discharged in Inc-5 |
| 7 | No file from another lane touched | all | ✓ | no lane; file set is proposal §2.1 row 4 (+ `.gitattributes`, ARCHITECTURE) |
| 8 | Frozen interfaces untouched (or returned to the trunk) | all | ✓ | D3 `CanonUnavailable(cause, limit)`, `Derivation(map, reported, unlinked, unknown_status)`, `derive_reqharness_map(repo, descriptor)` match proposal §4 exactly; no other frozen name touched (§6 items 1–2 are contract wording, not a shape change) |
| 9 | Coverage claims verified **on disk**, not from intent | all | ✓ | every node named in §4 exists and was collected (38) |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | all | ✓ | §4 *Load-bearing emptiness* |
| 11 | **Mutation verdicts** declared — per arm | all | ✓ | 19 mutants, 19 KILLED, per mutant and node in §4 |
| 12 | **Instrument RED-proof** declared | all | ✓ | 4 instruments, §4 |
| 13 | **Correction population** declared | all | ✓ | §4: 1 sentence, matched exactly once |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4: 4 artifacts |
| 15 | **Independent review** names somebody | all | ✓ | `code-reviewer` + security lens (Claude Sonnet subagent), approve-with-nits (§4b) |
| 16 | **Evidence files** declared | all | ✓ | §4: 8 artifacts with SHA-256 prefixes |
