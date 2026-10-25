# PDR review — ARCHITECT lens — batch `2026-10-25-relmap-r1-batch`

Reviewer: `architect` (independent). Input: `design/design-proposal.md` and the record seed `design/PDR-2026-10-25-relmap-r1-batch.md` at HEAD `c1f3e01`. Rules read: `stations/p1-arq.md` (parallelisation, freeze), the PDR record's §A, the contract and ledger `.1-.28`.
Paths are worktree-relative; privacy as before.

## Verdict: approved with conditions

The design is sound: boundaries, order, file sets and the census are right, and I found no blocker. Two conditions must be discharged before the seal; four minors ride along to the owning increment.

| Condition | Finding | Discharge point |
|---|---|---|
| C-1 | PD-1 (the snapshot hash pin fails on LF checkouts) | amend D7 and add a ledger entry before Inc-4; check at Inc-4 exit |
| C-2 | PD-2 (the frozen D2/D3 set misses what R2 must call) | amend §4 before the seal |

## §A checklist rows (confirmed by the architect lens)

| # | Item | State | Evidence |
|---|---|---|---|
| 1 | Proposal complete, rejected alternatives only where a real decision exists | ✓ with PD-6 | §1-§6 present. §6 lists 5 alternatives plus one honest `n/a`. Two of the rationales are weak (PD-6). |
| 2 | Respects `docs/ARCHITECTURE.md` boundaries | ✓ with PD-4 | §2 table against ARCHITECTURE §3 rows `relmap`/`yamlscan`/osopen cells: imports and bans agree. Only the `relmap` row's "internal ordering" sentence is stale (PD-4). |
| 3 | Forward applicability: every output has a named consumer | ✓ | §7, six rows, none empty. |
| 4 | Every requirement has foreseen coverage | ✓ | §5.1 covers every LLR-bearing file with a named test and mutant. HLR-RMM.1/RMM.2/RMM.3 are carried by their LLRs. |
| 5 | Test cases observable and non-vacuous, mutant named | ✓ | §5.1 names a move-aside RED per new source file and a mutant per row. Inc-3 golden-before-move is the right ordering; `D6` follows the repo convention (`tests/test_repair_golden_census.py:5-7` pins byte identity in module-level test constants, and `tests/goldens/` holds only `perf`). |
| 6 | Gauntlet controls declared, with who pays | ✓ | §2.1 exit checks; §6 risks 1, 3, 4, 6. |
| 7 | Frozen interfaces listed | ✗ → ✓ on C-2 | §4 lists D1-D5, but D2/D3 omit symbols R2 must call, and D5 freezes test seams (PD-2, PD-3). |
| 8 | Lane plan / file sets disjoint, family-B census | ✓ | §8 no fork; §2.1 file sets disjoint. Source counts are 3, 1, 3, 1 and 3, all ≤ 4. Each allow-list and ARCHITECTURE landing sits in the increment that adds the import (re-derived below). |
| 9 | UX lens | n/a for me | `ux-reviewer` owes it. |
| 10 | Security lens | n/a for me | `security-reviewer` owes it. I confirm only that the design adds no surface beyond the contract. |

## Checks I executed

- **Allow-list mechanics.** `tests/test_arch_osopen_callers.py:132-141` walks `PKG.rglob("*.py")` and asserts exact set equality with `ALLOWED_OUTSIDE_APP` (`:89-125`), so `relmap/model.py` (Inc-1) and `yamlscan.py` + `relmap/descriptor.py` + `store.py` losing `MAX_DEPTH` (`:103`, Inc-3) must land with their code. The proposal §2.1 does exactly that. The launcher-name census (`:25`, `LAUNCH_NAMES`) will not trip on any planned relmap name. `osopen.is_link(info)` takes an `lstat` result (`mapper/osopen.py:205`), which matches the `lstat`-then-`is_link` design of `read_repo_text`.
- **Packaging.** `pyproject.toml` uses `hatchling` with no explicit package list, so `mapper/relmap/` and `mapper/yamlscan.py` are included without a packaging edit.
- **Reverse census by import** (§5.2): I re-ran the greps. `run_cli` has the single caller `mapper/app.py:352`, and `MAX_DEPTH`/`ANCHOR_NAME_DISPLAY` are used only in `store.py`. Both agree with the proposal.
- **Reverse census by fixture content:** the two suites that run `--audit` (`tests/test_reqharness_release.py`, `tests/test_reqharness_baseline.py`) assert by substring, by `startswith("verdict: ")`, and by `len(stderr lines) == 1` on the refusal path, which returns before the hook. None counts stdout lines. Complete for assertions that can break. See PD-5 for the part the census leaves out.
- **Module order.** `profile` ← `model` ← `gaps`; `descriptor` ← `adapter` ← `audit` is acyclic and matches ARCHITECTURE §3 apart from PD-4.

## Findings

| ID | Sev | Evidence | What to change |
|---|---|---|---|
| PD-1 | MAJOR | D7 pins the snapshot fixture "by sha256 to ledger .4" = `93b18472…`. That is the hash of the Windows CRLF working copy: `git ls-files --eol REQUIREMENTS.md` gives `i/lf w/crlf`, `core.autocrlf=true`, and `git show HEAD:REQUIREMENTS.md` hashes to `b093c9203f0fe75f218298f56cc723a812902a1f4979424c8c2cb931bd39a25a`. A committed fixture is stored LF, so `test_snapshot_sha256` would pass here and fail on any LF checkout. `.gitattributes` has `-text` only for `tests/goldens/**` and `.dev-flow/*/evidence/**`; no entry covers `tests/fixtures/relmap/`. | Amend D7 and add a ledger entry correcting .4. The test hashes the LF-normalised bytes (`replace(b"\r\n", b"\n")`) and pins `b093c920…`; or add `tests/fixtures/relmap/** -text` to `.gitattributes`. Either way the 275/196/7/3 figures are unaffected, because `osopen.read_capped` already normalises newlines (`osopen.py:139-146`). Discharge at the Inc-4 exit by running `test_snapshot_sha256` from a fresh LF checkout. |
| PD-2 | MAJOR | §4 D2/D3 are not complete for R2. (a) `Descriptor` has no default and no `default_descriptor()` is listed, yet `derive_reqharness_map(repo, descriptor)` needs one when `discover_descriptors` returns nothing (LLR-RML.1.2 first row); R2 cannot call the adapter without it. (b) `RelMap.nodes`/`.edges` and the return types of `up(id)`/`down(id)` are unspecified, while LLR-RMU.1.4 requires deterministic order and R2 needs ordered, id-addressable access. (c) `rank_gaps(..., limit)` does not say whether `limit=None` (a view listing all gaps) is allowed, and LLR-RMG.1.3 computes reach only for the bands needed to fill `limit`. | Add to the frozen set: `default_descriptor() -> Descriptor` (or field defaults on `Descriptor`); the concrete types (`nodes`/`edges` as ordered tuples plus an id lookup, `up`/`down` as ordered tuples of ids or `frozenset`, say which); `limit: int \| None` and what `None` means for the visit bound. Freeze what R2 will call, and say so for each. |
| PD-3 | MINOR | D5 freezes `format_structure(…, *, label, sources, unknown_status, reach_not_computed)` and `refusal_line`. Only `structure_lines(repo)` has a consumer outside the package (`app`). The other two are a test seam; freezing their keyword set means any change to the line format needs a PDR version bump. Likewise D2's `CAUSE` dict and `RepoReadError` have no consumer beyond `relmap` and its tests. | Freeze `structure_lines` (D5) and the exception classes the callers catch (`DescriptorError`, `CanonUnavailable`, `RepoReadError`, `YamlLimitError`); mark `format_structure`, `refusal_line` and `CAUSE` "stable within the batch, not frozen". |
| PD-4 | MINOR | The ARCHITECTURE `relmap` row's internal ordering ends "`audit` → `adapter`, `gaps`", while proposal §2/§3 has `audit` also importing `descriptor` (`discover_descriptors`, `refusal_line` inputs) and `model` (`cut`, `DISPLAY_MAX`). No cycle, but the map and the code would disagree. | Amend the sentence in the Inc-5 landing (or in the seal's ARCHITECTURE edit): `audit` → `adapter`, `gaps`, `descriptor`, `model`. |
| PD-5 | MINOR | The census (§5.2) lists assertions that can break but omits the existing hostile-canon arms that now cover the new block: `tests/test_reqharness_release.py:665-680` and `:755-770` assert over the whole stdout that no `\x1b`, `\x7f`, `\r`, C1 character, `U+2028`, `U+202E` or `U+200B` appears and that exactly one `verdict:` line exists, with hostile ids and statements in the canon. They pass only if the structure block is escaped and cuts unsafe ids, which is a useful free control. | Add them to the census table as consumers, and name them in the Inc-5 exit check; a failure there is a real defect in the block, not a stale test. |
| PD-6 | MINOR | Two rejected-alternative rationales are weaker than stated. (a) "`read_repo_text` in `osopen` would add a fourth source file to Inc-3": Inc-3 has 3, so 4 is within the cap. The real reasons are the cost of reopening a hygiene-batch module whose names were frozen at that batch's PDR, and that `read_repo_text` has one consumer. (b) "`tests/goldens/**` is `-text` (byte-pinned)": that is a reason for it, not against. The real reason is the repo convention in `tests/test_repair_golden_census.py:5-7` (module-level constants; `tests/goldens/` is probed to hold only `perf`). | Reword both rows. The decisions stand. |
| PD-7 | MINOR | D4 says the hook is not called for the no-repo and no-registry reports but does not say how `run_cli` tells them apart. The reports differ only in `chain_status` (`identity.NO_REPO` at `mapper/reqharness/audit.py:175`, `NO_REGISTRY` at `:196`) and in `verdict` text. Keying on verdict text would be fragile. | State the discriminator (`report.chain_status` against those two constants) in D4, and add a TC that a `--baseline` refusal (a `ValidationError` before any report is printed, `audit.py:384`) neither prints structure lines nor calls the hook. |

## What I checked and found sound

- **D1** (`yamlscan`): complete and minimal. Its consumers are exactly the two `store` sites and `descriptor`; `YamlLimitError(Exception)` closes the `ValueError`-net trap I raised in pass 1.
- **D4**: `run_cli(argv, extra_lines=None)` is additive; the sole caller is `app.py:352` and no test calls it in-process, so the freeze cannot break an existing consumer. `None` is byte-identical to today.
- **D6**: inline byte constants captured on the base before the move match repo practice (see row 5).
- **D8**: five sequential increments, 3/1/3/1/3 source files, allow-list entries in the increment that adds each import (re-derived above). The reverse census by import and by fixture content is otherwise complete, including the check that no `*.relmap.yml` is tracked and that the sidecar-anchor fixtures reach the prescan only through `MapStore`.
- **Risks** (§6): the eight listed are real. The Windows symlink arm reporting `blocked` rather than skipping is the right treatment.

## Evidence checklist (architect)

| Item | State | Evidence |
|---|---|---|
| Constraints stated | ✓ | §1, §6; unchanged from the P2 passes |
| 2+ alternatives where a real decision exists | ✓ (PD-6 wording) | §6 table |
| Recommendation tied to constraints | ✓ | §2, §3 |
| Risks listed | ✓ | §6 |
| Diagram for non-trivial flow | ✓ | §3 |
| What would change the recommendation | ✓ | R-016/R-017 last column; §4 "returns to the trunk with a ledger entry" |
| Two-layer requirements | ✓ | contract §5.3-§5.4; TC-RM-01/02 carry the Layer-A-only claims |
