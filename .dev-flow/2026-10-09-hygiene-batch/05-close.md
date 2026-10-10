# Batch close — mapper — Batch 2026-10-09-hygiene-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language — the **prose**,
> and never a label.

> **Owed in.** `core` ✓ · `full` —

> **Field guide:** `templates/docs/close-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Conditional-gate discharge` · `New controls` · `Human perimeter` · `Human review ledger` · `Gated tree` · `Found before the batch` · `⏸ DEFER`
> **And the §6 DEPTH tokens — cell VALUES rather than field names, reserved for the same reason:**
> `light` · `rigorous` · `spot-check` · `none` · `✅` · `❌`. A CLOSED set, declared closed by the first
> revision that ships it — so the vocabulary a later promotion of `V54` to BLOCK will need already exists,
> instead of being introduced over a free-text field that six authors have by then written six ways.
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.

> **Notice convention.** `⚠` yellow = declare and continue · `✗` red = block · `✓` green = satisfied
> **with its citation**.

---

## 0 · Gate record — which tree this close gated

| Field | Value |
|---|---|
| Gate record | `python devflow-validate.py .` from the project root · exit 1 · 1 block · 380 notice · 2026-10-09 |
| Gated tree | `ca3c81127dca66ee25306fc52141fe169002e683` · dirty — .dev-flow/BACKLOG.md (the close record itself excluded) |
| Requirements canon | `REQUIREMENTS.md`. **⚠ Read §2 before trusting this row.** Every id this batch declares as a heading (`HLR-001`, `HLR-002`, `LLR-001.1`, `LLR-001.2`, `LLR-002.1`) is a token in the canon, but each token belongs to `2026-10-08-data-safety-batch`. `--fold-canon` printed `0 folded, 5 kept`. This batch's own statements are NOT in the canon (B-105). |

- **The one block is `V7`, and it is external:** the installed flow bundle's `SKILL.md` hash differs from its manifest (`29e9c490927538a7 != a2751ce96e24b120`). The bundle was changed outside this project by the session that owns rev101. This batch does not modify `~/.claude` (trigger F1, PLAN.md). Every other rule is green or a notice.

---

## 1 · What changed

**B-103 closed:** the draft-save path reads declared, public members, with no visible change. **B-99 closed:** an executed kill on master confirms the `INC9G-R8` debt was already paid.

| Requirement | Version | Verified by | Verdict |
|---|---|---|---|
| `HLR-001` | `v1` | `AT-060` · `AT-061` · `tests/test_draft_hygiene.py` | pass |
| `LLR-001.1` | `v1` | `test_llr_001_1_*` (2 nodes), RED on base | pass |
| `LLR-001.2` | `v1` (selector amended, LED .6) | `test_llr_001_2_*` (2 nodes), RED on base; M2, M3 killed | pass |
| `HLR-002` | `v1` | `AT-062` | pass |
| `LLR-002.1` | `v1` | `HOME-1` killed (`evidence/b99-home1-mutation.transcript`) | pass |

The gate suite ran on `092875e`: 2924 passed, 3 xfailed, 0 failed (`evidence/p4-full-suite.transcript`). P4 verdict: `PASS-WITH-NOTES`.

---

## 2 · New controls discovered — and where they landed (C-45)

| Control | What failure it closes | Measured origin |
|---|---|---|
| (candidate, not minted) **requirement ids are namespaced per batch** — e.g. `HLR-HYG.1` — so that the canon fold cannot collide | `--fold-canon` keeps an existing id and never rewrites it. A batch reusing a plain `HLR-001` is never folded, and `V22` passes vacuously on another batch's row | this close: `0 folded, 5 kept`. The canon holds `HLR-001`…`LLR-002.1` from `2026-10-08-data-safety-batch` (`REQUIREMENTS.md:100-122`). The flow's `req-template.md` seeds a plain `HLR-001` |

| # | Landing | Done? | SHA / path |
|---|---|---|---|
| 1 | the **command** — the rule itself | ❌ | not landed: the flow bundle (`~/.claude`) is owned by another session (rev101), and this batch does not modify it |
| 2 | its **artifact** (a template section) | ❌ | same reason |
| 3 | the **catalog** entry (`dev-flow-lessons`) | ❌ | same reason |
| 4 | committed and pushed, manifest re-hashed | ❌ | same reason |

- **New controls:** none minted. One candidate is reported to the operator for the flow's backlog, and the project-side carry is B-105.
- **Rename attempted and reverted at this close.** The ids were renamed to `HLR-HYG.*`, and the fold then folded 5. But `V26` BLOCKed, because the append-only ledger entries .1–.6 name the old ids, and the flow has no rename path. Two flow rules conflict here: append-only ledger + `V26` pairing on one side, the canon fold's id identity on the other. The ledger law was kept, because it is the more fundamental rule and is BLOCK-enforced. The canon gap is recorded instead (CLAUDE.md rule 7: pick one, explain, flag the other).

---

## 3 · Working-file reconciliation (C-44)

| File | State | Evidence |
|---|---|---|
| `mapper/app.py`, `tests/test_draft_hygiene.py`, `tests/test_draft_save.py`, `tests/test_draft_exits.py`, `tests/test_inc9h.py` | ✅ committed (`092875e`) and landed through the PR of `feat/hygiene-batch` | `git log feat/hygiene-batch` |
| `.dev-flow/2026-10-09-hygiene-batch/**`, `.dev-flow/state.json`, `.dev-flow/2026-10-08-data-safety-batch/{decisions-log,state-snapshot-at-close}.json` | ✅ committed and landed through the same PR | `c10afef`, `1579e1e`, `f6c6141`, P4 commit, close commits |
| `.dev-flow/BACKLOG.md` | ✅ committed in the close commit, landed through the same PR | §4 |
| worktrees `%TEMP%/ds-units/wt-hyg1`, `wt-b99`, `wt-val` (branches `unit/hyg1`, `unit/b99`, `unit/val`) | 📋 left on purpose: worker scratch, outside the repo tree, never pushed | removed after the merge (scratch rule: the evidence is committed and nothing is running) |

- **Found before the batch:** `none — no tracked file was modified when the batch began`

### Conditional-gate discharge

- **Conditional-gate discharge:** none — no gate closed conditionally

---

## 4 · Backlog reconciliation — the carry-over contract

| Item | Move | Reference |
|---|---|---|
| B-99 | DONE — re-verified, already paid by Inc-9h | `evidence/b99-home1-mutation.transcript`; AT-062 |
| B-103 | DONE — all three LOWs (F5 ruled no change: unreachable) | increment-001; `01-requirements.md` §6.2 |
| B-104 | NEW — pre-existing `ruff F401` (`re` unused) at `mapper/app.py:7` | `04-validation.md` G-002 |
| B-105 | NEW — this batch's requirement ids collide with the canon, so its requirements are not folded | §2 above |
| G-001 (`test_c6_*` under load) | not carried: it did not fail in the gate suite and was not reproduced | `04-validation.md` G-001 |
| B-102 | untouched (out of scope) | — |

---

## 5 · Batch metrics — the 13 keys of `core`

```yaml
type: dev-flow-batch
project: mapper
batch_id: 2026-10-09-hygiene-batch
mode: core
verdict: pass
increments: 1
source_files_max: 1
notices_raised: 4            # checklist ⚠: intake 6 (US-002 already shipped), intake 7 (V7), req 8 (absence premise); close §0 canon
rework_returns: 2            # P2 round 1 -> P1 (QA-1 major); P4 qa-reviewer fixes (LED .6)
triggers_fired: "F1"
tests_base_to_post: "2923 -> 2927"
new_control: none            # one candidate reported, not minted (§2)
open_items_next: 2           # B-104, B-105
```

---

## 6 · Human review ledger — what a human audited, at what depth

| Artifact | Machine verdict (citation) | Human review | Depth | Deliberately NOT reviewed |
|---|---|---|---|---|
| `01-requirements.md` + ledger | P2: architect + qa-reviewer, 2 rounds; `V26` paired | ❌ | `none` | the whole contract (operator reads later) |
| Code (`mapper/app.py` diff) | `code-reviewer` APPROVE-WITH-NITS, 0 HIGH | ❌ | `none` | — |
| Test cases / ATs | RED 4/4 on base; M1–M3 + HOME-1 KILLED | ❌ | `none` | — |
| `04-validation.md` | qa-reviewer ACCEPT-WITH-FIXES, fixes applied | ❌ | `none` | — |

- **Human perimeter:** whether B-105 (the namespacing of requirement ids) should be fixed in the flow (template seed + fold) or in the project (renaming the data-safety and hygiene ids). That is a flow-governance decision, and it belongs to the operator.
- **Human review ledger:** none. The operator authorized an autonomous batch with merge («core + autónomo + merge (Recomendado)», 2026-10-09). No artifact was reviewed by a human before the merge, and the operator owes a later reading.
