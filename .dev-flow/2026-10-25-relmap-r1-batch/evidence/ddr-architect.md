# DDR review - architect lens - relmap-r1 batch

Reviewer: `architect` (independent; authored none of the batch). Tree: worktree HEAD `e6dc5c5`, diff `194f885..HEAD -- mapper/`. Read: DDR draft, sealed PDR, design-proposal, `docs/ARCHITECTURE.md` rows 138/139/173/179/187/189/190 and R-016/R-017, `mapper/relmap/*.py`, `mapper/yamlscan.py`, the `store`/`app`/`reqharness/audit`/`search` diffs, `tests/test_relmap_isolation.py`, `tests/test_arch_osopen_callers.py`. State of evidence: **inspected (code and tests read, import lines grepped); not re-executed.** I did not re-run the suite; the DDR's 4017-pass transcript is the orchestrator's and I take it as cited, not as mine.

## Verdict: approved with conditions

No BLOCKER. The module boundaries, the frozen set and S1 hold as built. Three small conditions (C-1..C-3 below) are record or documentation fixes, none a code change.

## As-built vs PDR - what I checked

| Check | State | Evidence |
|---|---|---|
| Module boundaries (no boundary moves outside the package) | ok | `git diff 194f885..HEAD --stat -- mapper/` touches only `relmap/*` (new), `yamlscan.py` (new), `store.py`, `app.py`, `reqharness/audit.py`, `search.py` (comment). No other module changed. |
| S1 containment: tree `Graph` untouched | ok | `mapper/model.py` and `mapper/mermaid.py` are absent from the diff stat. A grep for `Graph` / `mapper.model` in `mapper/relmap/*.py` hits only the `model.py:3` docstring. The census arm `tests/test_relmap_isolation.py:116` fails any `mapper.model` / `..model` import (planted cases at `:125-135`). |
| Import census, relmap -> mapper | ok | Actual imports: `osopen` (`MAX_EDGES`, `MAX_NODES` at `model.py:30`; the five reader/containment names at `descriptor.py:23`), `yamlscan` (`descriptor.py:32`), `reqharness.derive` (`parse_canon`, `LIMIT_ROLES_YML_BYTES` at `adapter.py:31`, plus `CanonObject`), intra-package. Equals `ALLOWED_OSOPEN` / `ALLOWED_DERIVE` (`test_relmap_isolation.py:23-26`) and `ARCHITECTURE.md:189`. `from mapper.reqharness import x` and `import mapper.reqharness.derive` fall to the checker's `else` branch and are flagged, so a wider import cannot hide. |
| Reverse edges | ok | `reqharness/audit.py` imports nothing from `relmap` (import block, lines 30-63, read); `app.py:350` is the only outside importer (`test_only_app_and_the_package_import_relmap`, `:157`). The hook is injected, so the core stays upstream. |
| `yamlscan` leaf | ok | Imports only `yaml` and `.osopen.MAX_DEPTH`; `store.py` no longer imports `MAX_DEPTH` and delegates (`store.py:703-726`), keeping its own wording; `ARCHITECTURE.md:179,190` and `test_arch_osopen_callers.py:129-136` agree. |
| D1 | intact | `prescan(text)`, `YamlLimitError(kind, shown, limit)`, `ANCHOR_NAME_DISPLAY = 40` (`yamlscan.py:21-39`). |
| D2 | intact + one addition | see OP-3. |
| D3 | intact | signatures read against the DDR list; `RelMap` accessors `model.py:169-248`; `VISIT_BUDGET` `model.py:33`. |
| D4 | intact + one addition | see OP-4. The `extra_lines=None` path is a no-op (`if extra_lines is not None`). |
| D5 | intact | `structure_lines(repo) -> list[str]` at `relmap/audit.py:173`, unescaped, header first. |
| Python floor / stdlib bans | ok (proxy) | `test_py310_floor`, `test_stdlib_bans` exist; the real 3.10 run is `not-run` (OP-8, not mine). |

## Findings

| Id | Sev | Where | Finding |
|---|---|---|---|
| F-1 | MINOR | `docs/ARCHITECTURE.md:189` (relmap row, contract notes) | The D4 sink refinement (a hook line starting `verdict: ` is rewritten `structure: verdict: ...`, `reqharness/audit.py:431-434`) is in no module-map row. The row documents the prefix rule for the CI reader and the 1,000-line bound, not this guard. The PDR's own closing rule says a decision that fixes an interface lands in the module map beside the code. Add one clause. |
| F-2 | MINOR | `design/design-proposal.md:118` | The post-seal annotation pass (ledger .56/.57, commit `f02dbbd`, after the seal commit `7932297`) updated `refusal_line` and the `model -> descriptor` edge but left the `format_structure` signature as sealed; as built it also takes `unlinked` and `ignored` (`relmap/audit.py:118`, call at `:199-205`). Harmless (tested seam, PD-3), but the proposal now claims as-built status while stale on one row. Fix the row or keep it listed in the DDR delta table (it already is, DDR section B row 1(d)). |
| F-3 | MINOR | `mapper/relmap/audit.py` `__all__` | `refusal_line` is re-exported from `audit` though defined in `descriptor.py:211`. Not a defect (the proposal records it so), but the name has two import paths and nothing pins which one tests use. Drop it from `audit.__all__` or accept. |
| F-4 | MINOR | `mapper/relmap/descriptor.py:211-216` | `refusal_line` formats the operator-facing `structure: refused (...)` text inside the loader, so the loader knows the audit line grammar. Same family as OP-11: a second presentation function in a data layer. Tolerable for R1; fold into the OP-11 follow-up. |
| F-5 | MINOR | `mapper/relmap/audit.py:177-183` | `structure_lines` derives the map from `default_descriptor()` once and varies only `us_canon` / `at_table` / `ignored` per descriptor, so `Descriptor.canon` and `.profile` are carried but never consulted at derive time. Correct while R1 has one profile and one canon name; it is the seam R5 (`lineage`) will have to widen. Note it beside B-146; no change now. |
| F-6 | NOTE | DDR section B rows 1(i), 6 | The closing-gate fixes touch `mapper/search.py` (comment only) outside any increment's file set; declared, tied to ledger .70. Accept. |

## Open-point opinions

- **OP-1 (post-seal annotations to the proposal): rule (a), with a condition.** The annotations record facts already true in the code (a name's home module, one extra import edge); no decision was made by editing the proposal. A `#v2` id would add a record without adding a review, because this DDR is exactly that review. The PDR record itself (last touched `7932297`) is unedited, which is what the seal rule protects. Condition C-1.
- **OP-3 (`DescriptorError.limit`): accept as compatible; record it in the DDR section D as an additive D2 revision, no new PDR id.** It is a trailing keyword argument with default `None` (`descriptor.py:78`); `RepoReadError` already carried the same field; no existing catch or `.cause` / `.name` reader changes. The sealed rule "a later increment that needs to change a frozen name returns to the trunk with a PDR version bump" is aimed at a signature break, and this is not one. But that sentence is unqualified, so the DDR must say in one line that an additive change with a default is not a freeze breach; otherwise the next batch cannot tell. Part of C-2.
- **OP-4 (`verdict: ` prefix in `run_cli`): accept as a D4 refinement; document it.** It narrows what the hook can print (closes a forge path), leaves `extra_lines=None` byte-identical, does not touch the exit code, and sits at the one escaper site the contract already named. That is the safe direction for a frozen interface to move. Limit to state: the guard is a prefix test after `_visible`, so it protects the documented reading (`grep '^verdict: '`) and nothing more, which is the contract. Condition: F-1, in C-2.
- **OP-5:** not my lens; no architecture objection (transcription of code points with no hash citing the records is not a design change).
- **OP-6:** not my lens; one architecture remark. A declared, self-expiring table keeps the resolver's meaning stable for every sealed record, which is what matters across batches; changing the resolver to prefer the non-package hit changes what every old bare citation means. Keep the table.
- **OP-11 (`cut` lives in `model.py`): keep for R1, schedule the move, do not move now.** Evidence it is a smell: `descriptor` (`descriptor.py:30,195,216`) and `adapter` (`adapter.py:29,138`) import presentation (`cut`, the 120-character rule) from the read model, and the `descriptor -> model` edge exists only for that. Evidence it is harmless now: `cut` is a pure four-line function, the edge is acyclic and covered by the import census, and `DISPLAY_MAX` is also used by `model` itself for `Node.title`. Moving it now re-opens `model`, `descriptor`, `adapter` and `audit` after D3 froze `model`'s names, for no behaviour gain. Recommendation: move `cut` / `DISPLAY_MAX` (and consider `refusal_line`, F-4) to a leaf `relmap/text.py` in the R2 PDR, before R2 adds a second printer; `cut` is not in the frozen-set sentence, so the move is not a freeze breach. What would change my answer: R2 views needing `cut` from a module that must not import `model`.

OP-2, OP-7, OP-8, OP-9 are qa / software-dev lens and not ruled here. OP-10: my architecture view is that BACKLOG suffices while the shipped behaviour is what the fixed-text tests pin (12/12 ATs per the DDR; not re-run by me).

## Conditions

- **C-1** DDR section B row 1 / OP-1: state that the PDR file is the sealed meaning, that the annotated proposal is read at this DDR, and that F-2 is fixed or listed.
- **C-2** DDR section D: add the two additive-revision lines (D2 `DescriptorError.limit`, D4 sink prefix guard) with the rule "additive with a default is not a freeze breach"; add the sink-guard clause to `docs/ARCHITECTURE.md:189` (F-1).
- **C-3** DDR section E: add a residual-risk line for OP-11 / F-4 / F-5 (presentation in the read model and loader; the single-descriptor derive seam), owner the R2 PDR.

Nothing here requires a code change or returns the batch to implementation.

## Evidence checklist

- [x] Constraints stated: scope = as-built conformance to the PDR; cost / latency / privacy `n/a - conformance review of a headless read-only module, no new runtime cost or data flow beyond the PDR's`.
- [x] Alternatives: `n/a - the decisions were made by the sealed PDR (S1, R-016, R-017)`; the OP-1 and OP-11 options are weighed above.
- [x] Recommendation tied to constraints: OP rulings above.
- [x] Risks listed: F-1..F-5, C-3.
- [x] What would change the recommendation: stated under OP-11 and OP-3.
- [x] The "no boundary change" claim is backed by the diff stat, import greps, isolation test and ARCHITECTURE rows (table above). State: inspected, not re-executed.
