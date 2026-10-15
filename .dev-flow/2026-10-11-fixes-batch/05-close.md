# Batch close — mapper — Batch 2026-10-11-fixes-batch

> **Artifact language.** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` —

> **Reserved field names.** `Conditional-gate discharge` · `New controls` · `Human perimeter` · `Human review ledger` · `Gated tree` · `Found before the batch` · `⏸ DEFER` are read literally by the validator; the §6 depth tokens `light` · `rigorous` · `spot-check` · `none` · `✅` · `❌` are cell values.

> **Notice convention.** `⚠` yellow = declare and continue · `✗` red = block · `✓` green = satisfied **with its citation**.

---

## 0 · Gate record — which tree this close gated

| Field | Value |
|---|---|
| Gate record | Full suite (orchestrator, clean shell, merged code `59a02d9`): `3432 passed, 24 deselected, 3 xfailed, 12 warnings in 2484.36s (0:41:24)` — 0 failed; the 24 deselected are the `slow` and `network` markers (`pyproject.toml:46`). Validator `devflow-validate.py --brief`: 2 block, both V16 on `~/.claude` (the flow's own checkout, outside this batch); 0 blocks under this batch · 2026-10-15 |
| Gated tree | tested code `59a02d9`; close edits on top of `a1c64c6986a962ae9f4c662617d72fdc0efd925f` — dirty: the records of this close only (`04-validation.md`, the DDR, packets 001-003 line fixes, `BACKLOG.md` B-133, `docs/ARCHITECTURE.md:18`). Commits after `59a02d9` are records and docs only. |
| Requirements canon | `repo:REQUIREMENTS.md` (`artifact_homes.requirements_canon`). The 19 `HLR-FX.*`/`LLR-FX.*` ids were folded into it by `devflow-init.py --fold-canon` at this close (19 folded, 0 kept, 0 refused). |

---

## 1 · What changed

**BLUF.** Four fixes shipped on `feat/fixes-batch`: a CSV import no longer invents a node `n` or refuses a child-first file as a cycle; a forest map keeps its root across save and reload; the roles screen no longer freezes on a slow git; and two test guards (`pan_extent` in the export concern, the leak-excuse key) can no longer be silently bypassed. Source touched: `mapper/import_csv.py`, `mapper/mermaid.py`, `mapper/store.py` (docstring only), `mapper/screens/roles.py`. No visible string, glyph, colour or key was added (operator ruling R4).

| Increment | What shipped | Source files | Commits |
|---|---|---|---|
| 001 (B-115, B-116) | `slugify` returns `""` when nothing survives; blank parent cell is a root candidate; id with no slug characters becomes `row-N`; CSV root chosen by parentage, orphans attached without a cycle | 2 | `d412ed0` |
| 002 (B-117) | `dump` writes the declared root first, only when text order would elect another; byte-identical for every other graph | 2 | `2d57228`, merge `2fc6087` |
| 003 (B-127) | roles git discovery on a thread worker; result applied in `on_worker_state_changed` behind a generation and `is_attached` guard; keys inert and key bar reduced until the first load | 1 | `c7c975a`, merge `59a02d9` |
| 004 (B-110, B-113) | spy node on `exporting.pan_extent` (AT-088); leak registry keyed `(file, lineno, expr)` (AT-089) | 0 (tests only) | `a7b0f54`, `b4ce603`, merge `de3c6d0` |

| Requirement | Version | Verified by | Verdict |
|---|---|---|---|
| HLR-FX.1 (LLR-FX.1.1-1.3) | v1 | AT-084 · `tests/test_fixes_csv_import.py`, `tests/test_mermaid.py` | ✅ |
| HLR-FX.2 (LLR-FX.2.1-2.2) | v1 | AT-085 · `tests/test_fixes_csv_import.py` | ✅ |
| HLR-FX.3 (LLR-FX.3.1-3.2) | v1 | AT-086 · `tests/test_fixes_forest_root.py`, goldens | ✅ |
| HLR-FX.4 (LLR-FX.4.1-4.4) | v2 (amended E1: `is_attached`) | AT-087 · `tests/test_fixes_roles_thread.py` | ✅ |
| HLR-FX.5 (LLR-FX.5.1) | v1 | AT-088 · `tests/test_export_state.py` | ✅ |
| HLR-FX.6 (LLR-FX.6.1) | v1 | AT-089 · `tests/test_inc9c.py` | ✅ |

**Review catches per station.**

| Station | Reviewer | Caught |
|---|---|---|
| ARQ | architect | F1 module map stale for `roles.py`; F2 hoist must not reorder on resave; F3a/F3b/F3c (framework cancel, doubled start, `store`→`mermaid` edge → `B-132`) |
| P2 | qa-reviewer role (DeepSeek) | 2 major (popped-screen worker lifetime; uncaught-exception seam), 5 minor (row-N discipline, depth arm, HLR/LLR key alignment, AT-085 helper, Unicode scope) — all fixed, LED .7-.11 |
| PDR | architect (Claude Opus), ux-reviewer (Claude Sonnet), qa-reviewer + light security (DeepSeek) | conditions C1-C8; `B-128`…`B-132` opened |
| 001 | code-reviewer (Claude Opus) | M-FX2 negative-control text; AT-084 id vs painted title; docstring fallback clause; BOM → `B-130` |
| 002 | code-reviewer (DeepSeek) | `store.py` docstring re-wrap; found the A3 census pin moved by 001's helper |
| 003 | code-reviewer (DeepSeek) | L1 exit-time thread residual (accepted → `B-133`); L2 `_open_roles` unbounded wait (fixed, `asyncio.wait_for(..., timeout=60)`); E1 `is_attached` vs `is_mounted` found at implementation |
| 004 | code-reviewer (Claude Sonnet) | actionable stale-key message; AT-089 picks any declared carry |
| DDR | architect (Claude Opus), qa-reviewer (Claude Sonnet) | approve with conditions, all discharged: F3b accepted with evidence, `ARCHITECTURE.md` header, L1 bound and `B-133`, `pending` replaced by the executed line, hoist scan cost declared, gate rows reconciled |

---

## 2 · New controls discovered — and where they landed (C-45)

| Control | What failure it closes | Measured origin |
|---|---|---|
| none minted | the lessons below are recorded here and in memory; no flow-side rule was written | — |

| # | Landing | Done? | SHA / path |
|---|---|---|---|
| 1 | the **command** (`commands/…`) | n/a — no control minted | — |
| 2 | its **artifact** (a template section) | n/a | — |
| 3 | the **catalog** entry (`dev-flow-lessons`) | n/a | — |
| 4 | **committed and pushed**, manifest re-hashed | n/a | — |

- **New controls:** none — the reason: the batch's lessons are about test-helper census coupling and tool limits, which the existing census and independent-review controls already own; they are recorded under §7 rather than minted as rules.

---

## 3 · Working-file reconciliation (C-44)

| File | State | Evidence |
|---|---|---|
| `mapper/import_csv.py`, `mapper/mermaid.py`, `mapper/store.py`, `mapper/screens/roles.py` | ✅ committed on `feat/fixes-batch`; merge into the trunk is the operator's (no standing authorization) | `git log 81fba65..59a02d9` |
| `tests/test_fixes_*.py`, `tests/test_export_state.py`, `tests/test_inc9c.py`, `tests/test_a3_census.py` and the moved pins | ✅ committed | DDR row 6 |
| `docs/ARCHITECTURE.md` | 📋 header line 18 amended in this close, not yet committed | this record |
| `REQUIREMENTS.md` (19 folded rows), `.dev-flow/BACKLOG.md` (B-133), `04-validation.md`, `05-close.md`, DDR seal, packets 001-003 | 📋 uncommitted at hand-back; the orchestrator commits them | `git status` |

- **Found before the batch:** `none — no tracked file was modified when the batch began` (fresh worktree; the only diff at open was this batch's own `state.json`)

### Conditional-gate discharge

- **Conditional-gate discharge:** `15 condition(s) · ✅ all discharged` (9 at the PDR: C1-C8, E1; 6 at the DDR: a-f)

| Condition | Discharged? | The artifact line that proves it |
|---|---|---|
| PDR C1-C8, E1 | ✅ | DDR §B condition table (each re-read in the artifact) |
| DDR (a) F3b accepted | ✅ | DDR row 9; `design/arq-note.md:81` |
| DDR (b) ARCHITECTURE header | ✅ | `docs/ARCHITECTURE.md:18` |
| DDR (c) L1 bound | ✅ | DDR row 10; `.dev-flow/BACKLOG.md` B-133 |
| DDR (d) `pending` replaced | ✅ | DDR rows 3, 5, 8 and §C |
| DDR (e) hoist cost | ✅ | DDR row 2 |
| DDR (f) gate rows | ✅ | DDR row 1; packets 001-003 §6 |

---

## 4 · Backlog reconciliation — the carry-over contract

| Item | Move | Reference |
|---|---|---|
| B-110, B-113, B-115, B-116, B-117, B-127 | done in this batch | increments 001-004; rows still to be struck through in `BACKLOG.md` at merge |
| B-128 | opened: prototype round for a visible loading state | PDR J5 |
| B-129 | opened: copy of the `? ` prefix on extra parentless roots | PDR J1 |
| B-130 | opened: CSV UTF-8 BOM | PDR QA review |
| B-131 | opened: CSV quoted embedded newline | PDR QA review |
| B-132 | opened: module map `store` → `mermaid` edge | ARQ F3c |
| B-133 | opened: exit-time thread residual, bound ≈ 30 s | DDR row 10 |

**Accepted residuals.**
- **L1 (→ B-133).** Quitting mid-discovery can keep the process alive until the git calls time out: 3 git calls × the 10 s `_TIMEOUT` ≈ 30 s; two parallel workers (F3b) run side by side and stay within ≈ 30 s. The app exits in 0.67 s; no data loss.
- **F3b.** Two discoveries start at push; 6 git calls at open, the same count as the old synchronous code; the generation guard makes the second win. Accepted with evidence, not coalesced.
- **The `? ` prefix on extra parentless roots** (for example `? Beta` under root `Alpha`) is the existing forest rule and intentional; this batch changed only which row is the root. Whether the copy should change is `B-129`.

**Open items for the next batch:** B-128, B-129, B-130, B-131, B-132, B-133.

---

## 5 · Batch metrics — the 13 keys of `core`

```yaml
type: dev-flow-batch
project: mapper
batch_id: 2026-10-11-fixes-batch
mode: core
verdict: pass
increments: 4
source_files_max: 2              # increments 001 and 002
notices_raised: 4                # DDR rows 1, 2, 3, 10 (⚠); validation ledger gap G-001
rework_returns: null             # not recorded by the phase checklists
triggers_fired: "A2,A3,B1,B3,B4,C1,C6,D1,E1"
tests_base_to_post: "3376 -> 3432"
new_control: none
open_items_next: 6               # B-128 … B-133
```

---

## 6 · Human review ledger — what a human audited, at what depth

| Artifact | Machine verdict (citation) | Human review | Depth | Deliberately NOT reviewed |
|---|---|---|---|---|
| `01-requirements.md` | gate §4 green; PDR sealed | ❌ | `none — read by independent model reviewers only` | |
| Test cases / ATs | six ATs in six nodes; 21 mutants RED | ❌ | `none` | |
| Code | full suite 0 failed; four independent reviews | ❌ | `none — model reviewers only` | not audited line by line by a human |
| `04-validation.md` | validator | ❌ | `none` | real-user evaluation `not performed — one-person team` |

- **Human perimeter:** whether the blank roles window is acceptable to a real operator with a genuinely slow git (the visible cue is `B-128`), and the merge decision, are the operator's; business judgement on the `? ` copy is `B-129`.
- **Human review ledger:** `none — this batch recorded no human review; every reading was by a model reviewer, named per station in §1`

---

## 7 · Lessons

- **A census pin moved by a helper the increment never ran.** Increment 001's `_render().plain` helper moved the A3 census count 37 to 38 in a test file 001 did not run; it was caught one increment later (by 002) and fixed in `74d051a`, then 003's `_painted` helper moved it to 39. A helper added to the test tree needs its reverse census run in the same increment.
- **Kimi quota exhaustion.** The Kimi runner ran out of quota mid-batch; work moved to other runners. Plan runner capacity per increment, not per batch.
- **DeepSeek runner 900 s cap.** A review that needs the long suite cannot finish inside the runner's 900 s cap; split the review or hand the full run to the orchestrator.
- **`is_mounted` vs `is_attached` in Textual 8.2.8.** `is_mounted` stays True after a screen is popped, so a guard on it never fires; the hand-back must read `is_attached` (E1, `roles.py:535-537`). Verify a framework flag against the pinned version's source, not its name.

---

## 8 · Evidence checklist (software-dev)

- [✓] Tests/type checks/lint pass — full suite `3432 passed, 24 deselected, 3 xfailed … (0:41:24)`, 0 failed (orchestrator run; not re-run by this record).
- [✓] No secrets in code or output — records only; no key, token or personal path written.
- [✓] No destructive commands run — only file edits and read-only git.
- [✓] File count within cap — source max 2 per increment; this close touches 1 source-adjacent doc line (`docs/ARCHITECTURE.md:18`) and no `mapper/` or `tests/` file.
- [✓] Review packet attached — `03-increments/increment-001..004.md`, §4b reviews recorded.
- [✗] Test ledger reconciles to the node — 1-node gap `G-001` declared in `04-validation.md`, not resolved.
- [✓] Requirements canon folded — 19 ids in `REQUIREMENTS.md` (`--fold-canon`: 19 folded, 0 refused); V22 clear.
