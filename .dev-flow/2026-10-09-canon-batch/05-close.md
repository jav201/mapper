# Batch close — mapper — Batch 2026-10-09-canon-batch

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
| Gate record | `python devflow-validate.py .` from the project root · exit 1 · 1 block · 381 notice · 2026-10-09 |
| Gated tree | `4b1a4d04f5b01edc152131d46b63906f231866d2` · dirty — .dev-flow/BACKLOG.md (the close record itself excluded) |
| Requirements canon | `REQUIREMENTS.md`. Every id this batch declares as a heading (`HLR-CAN.1`, `HLR-CAN.2`, `LLR-CAN.1.1`, `LLR-CAN.1.2`, `LLR-CAN.2.1`) is a token in it, folded at this close (`5 folded`). The hygiene batch's five requirements are now present as `HLR-HYG.*` / `LLR-HYG.*` (AT-063). |

- **Cosmetic, the fold's own normalisation:** the folded statement of `LLR-CAN.1.2` reads correctly. The folded statement of `LLR-CAN.1.1` lost the literal backtick and `**` tokens it quotes ("drop backticks and ;"). That is because the fold drops them by rule 1, the very rule the row describes. The contract (`01-requirements.md`) keeps the exact wording.
- **The one block is `V7`, which is external:** the installed flow bundle's `SKILL.md` hash differs from its manifest. This batch does not modify `~/.claude` (F1). Every other rule is green or a notice.

---

## 1 · What changed

**The canon now holds the hygiene batch's requirements under collision-free ids (B-105, project side), and `mapper/app.py` has no unused import (B-104).**

| Requirement | Version | Verified by | Verdict |
|---|---|---|---|
| `HLR-CAN.1` | `v1` | `AT-063` · `test_llr_can_1_2_*` · C0–C3 killed | pass |
| `LLR-CAN.1.1` | `v1` | `AT-063`, `test_llr_can_1_1_normaliser_pins_the_fold_rules` | pass |
| `LLR-CAN.1.2` | `v1` | `test_llr_can_1_2_canon_ids_are_unique_and_the_table_is_not_empty` | pass |
| `HLR-CAN.2` | `v1` | `AT-064` · `ruff` corroboration · A1 killed | pass |
| `LLR-CAN.2.1` | `v1` | `test_llr_can_2_1_checker_arms` (13) | pass |

- **Gate suite on `791decb`:** 2941 passed, 3 xfailed, 0 failed (`evidence/p4-full-suite.transcript`).
- **P4 verdict:** `PASS-WITH-NOTES`.

---

## 2 · New controls discovered — and where they landed (C-45)

| Control | What failure it closes | Measured origin |
|---|---|---|
| (project convention, not a flow control) **namespaced requirement ids per batch** (`CAN` here) | a plain `HLR-001` collides in the canon, and the fold keeps the old row | B-105 (`2026-10-09-hygiene-batch` close §2) |

| # | Landing | Done? | SHA / path |
|---|---|---|---|
| 1 | the **command** — the rule itself | ❌ | flow-side, not landed: the bundle is owned by the rev101 session (B-106) |
| 2 | its **artifact** (a template section) | ❌ | same reason (the template seeds `HLR-001`) |
| 3 | the **catalog** entry (`dev-flow-lessons`) | ❌ | same reason |
| 4 | committed and pushed, manifest re-hashed | ❌ | same reason |

- **New controls:** none minted in the flow. The project applies the convention from this batch on, and the flow-side fix is carried as B-106 for the operator's ruling.

---

## 3 · Working-file reconciliation (C-44)

| File | State | Evidence |
|---|---|---|
| `REQUIREMENTS.md`, `mapper/app.py`, `tests/test_requirements_canon.py`, `tests/test_app_imports_used.py` | ✅ committed (`791decb`, plus the canon fold at close), landed through the PR of `feat/canon-batch` | `git log feat/canon-batch` |
| `.dev-flow/2026-10-09-canon-batch/**`, `.dev-flow/state.json`, the hygiene archive (`decisions-log.json`, `state-snapshot-at-close.json`) | ✅ committed, landed through the same PR | the batch commits |
| `.dev-flow/BACKLOG.md` | ✅ close commit, same PR | §4 |
| worktrees `%TEMP%/ds-units/wt-can1`, `wt-can2`, `wt-val2` (branches `unit/*`) | 📋 worker scratch outside the repo tree, never pushed | removed after the merge (scratch rule) |

- **Found before the batch:** `none — no tracked file was modified when the batch began`

### Conditional-gate discharge

- **Conditional-gate discharge:** none — no gate closed conditionally

---

## 4 · Backlog reconciliation — the carry-over contract

| Item | Move | Reference |
|---|---|---|
| B-104 | DONE | AT-064; `ruff check mapper/app.py` → `All checks passed!` |
| B-105 | DONE (project side): the 5 hygiene rows appended; ids namespaced from this batch on | AT-063; increment-001 |
| B-106 | NEW: the flow-side fix (the requirements template seeds a plain `HLR-001`; `--fold-canon` cannot alias; there is no rename path under `V26` + the append-only ledger). Operator ruling, flow backlog | §2 |
| G-001 (`04-validation.md`) | carried inside B-106: B-105's failure mode is not detectable in the repo | `04-validation.md` |
| B-102 | untouched | — |

---

## 5 · Batch metrics — the 13 keys of `core`

```yaml
type: dev-flow-batch
project: mapper
batch_id: 2026-10-09-canon-batch
mode: core
verdict: pass
increments: 1
source_files_max: 1
notices_raised: 3            # checklist ⚠: intake 7 (V7), req 8 (absence premises); the reviewer row-count error caught (LED .5)
rework_returns: 2            # P2 round 1 -> P1 (ARCH-1, QA-2, QA-1); P4 qa-reviewer fixes
triggers_fired: "B4,F1"
tests_base_to_post: "2927 -> 2944"
new_control: none            # project convention adopted; the flow-side fix is B-106
open_items_next: 1           # B-106
```

---

## 6 · Human review ledger — what a human audited, at what depth

| Artifact | Machine verdict (citation) | Human review | Depth | Deliberately NOT reviewed |
|---|---|---|---|---|
| `01-requirements.md` + ledger | P2 architect + qa-reviewer, 2 rounds; `V26` paired | ❌ | `none` | the whole contract |
| `REQUIREMENTS.md` rows + code | `code-reviewer` APPROVE-WITH-NITS, 0 HIGH; C0–C3 and A1 killed | ❌ | `none` | — |
| `04-validation.md` | qa-reviewer pass, fixes applied | ❌ | `none` | — |

- **Human perimeter:** B-106. Whether the flow should namespace requirement ids (in the template seed and the fold) is a flow-governance decision for the operator.
- **Human review ledger:** none. The operator authorized an autonomous batch with merge («core + autónomo + merge (Recomendado)», 2026-10-09), and owes a later reading.
