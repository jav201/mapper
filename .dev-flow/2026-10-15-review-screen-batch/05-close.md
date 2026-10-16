# Batch close — mapper — Batch 2026-10-15-review-screen-batch

> **Artifact language.** English (`state.json` `language: en`).

> **Owed in.** `core` ✓ · `full` —

> **Reserved field names.** `Conditional-gate discharge` · `New controls` · `Human perimeter` · `Human review ledger` · `Gated tree` · `Found before the batch` · `⏸ DEFER` are read literally by the validator; the §6 depth tokens `light` · `rigorous` · `spot-check` · `none` · `✅` · `❌` are cell values.

> **Notice convention.** `⚠` yellow = declare and continue · `✗` red = block · `✓` green = satisfied **with its citation**.

---

## 0 · Gate record — which tree this close gated

| Field | Value |
|---|---|
| Gate record | Full suite (orchestrator, clean shell, merged code): ``3543 passed, 24 deselected, 3 xfailed, 13 warnings in 2029.79s (0:33:49)` — 0 failed; clean shell, code at ff6262f (847231b + gate record); the 24 deselected are the `slow` and `network` markers`. Validator `devflow-validate.py --brief`: 2 block, both V16 on `~/.claude` (the flow's own checkout, outside this batch); 0 blocks under this batch · 2026-10-16 |
| Gated tree | tested code at the merged head; close edits on top of it — dirty: the records of this close only (`04-validation.md`, `05-close.md`, the `REQUIREMENTS.md` fold, `.dev-flow/BACKLOG.md`). |
| Requirements canon | `repo:REQUIREMENTS.md` (`artifact_homes.requirements_canon`). The 17 `HLR-RS.*`/`LLR-RS.*` ids were folded into it by `devflow-init.py --fold-canon` at this close (17 folded, 0 kept, 0 refused). |

---

## 1 · What changed

**BLUF.** The ReqHarness REVIEW / SIGNING screen ships on `feat/review-screen-batch`: a reviewer opens it from home with `v`, sees every canon object with its derived state and a "needs action" filter preset, reads an object's full review history (digest ✓/✗, unentitled flagged apart, the `⁂` badge explained) and the release verdict in a fixed bottom band, and signs with two keys — `b` arms showing the digest + head to be signed, `enter` confirms through the new headless `sign_review`, which refuses with a named reason on a broken/tampered/forked chain, an unknown/ambiguous/undeclared viewer, a missing role at the current head, a retired or class-undeclared object, or an author signing their own batch. Self-review is forbidden twice: at the sign pre-flight (`entitled_to_sign`) and authoritatively in `derive` (a hand-written record cannot bypass the screen). All UI copy English; colours from `darkside`, keys from the keymap seat.

| Increment | What shipped | Source files | Commits |
|---|---|---|---|
| 001 (RS1a) | the **data layer**: the review record's optional `owning_batch` field (F1), `SigningRefused` + stable reason codes in `records.py`, the config `authors` map (validated against `people`, part of `config_hash`), `derive`'s `unentitled` (role · author · owning-batch mismatch) + `CanonObject.owning_batch` | 4 | `05c516a`, `b009a4b`, `4f6f8bf` |
| 002 (RS1b) | the **logic**: `mapper/reqharness/signing.py` (`entitled_to_sign` 10-arm truth table, `sign_review` orchestration + TOCTOU + `unapproved_config`) and `release.py`'s `authors_declared` rule + the one-line `config.py` seed (R18) | 2 (+1-line seed) | `6299970`, `98d11a8` (merge), `b59446f`, `eccc13c`, `b907571`, `7eec95a` |
| 003 (RS2) | the **screen + seat**: `mapper/screens/review.py` (variant A), `mapper/keymap.py` (`review` scope + `v` door), `mapper/screens/home.py` (`_DOOR_NOTES["v"]` + `action_review`), `mapper/app.py` (re-export) | 4 | `f890ae7`, `ae394cf`, `a8873e8`, `b549ca5`, `b9e7fa7` |

| Requirement | Version | Verified by | Verdict |
|---|---|---|---|
| HLR-RS.1 (LLR-RS.1.1-1.5) | v1 | AT-090/091/092/096/099 · `tests/test_review_screen.py` | ✅ |
| HLR-RS.2 (LLR-RS.2.1-2.4) | v2 (F3: `confirm_owning_batch` required keyword) | AT-093/098/100/101 · `tests/test_reqharness_signing.py` | ✅ |
| HLR-RS.3 | v1 | AT-094/095/102 · `tests/test_reqharness_signing.py` | ✅ |
| HLR-RS.4 (LLR-RS.4.1) | v1 | AT-097 · `tests/test_keymap.py`, `tests/test_key_dispatch.py` | ✅ |
| HLR-RS.5 (LLR-RS.5.1-5.2) | v2 (H1/M2/L1/L2 security follow-up) | AT-102 · `tests/test_reqharness_registry.py` | ✅ |

**Review catches per station.**

| Station | Reviewer | Caught |
|---|---|---|
| ARQ | architect | F1: the `screens` row must gain `mapper/screens/review.py`; `signing.py` auto-claimed by the `reqharness` glob; 0 new edges |
| P2 | qa-reviewer role (DeepSeek) | iterate → resolved: QA BLOCKER (the seat must merge into RS2, RS3 dropped), MAJOR-1…6 (active + class-declared object; exactly one identity match; the 2 000-object scale; one worker; disarm-before-worker; typed refusals), the copy table + any-key-cancels rule |
| PDR | ux-reviewer (Claude Sonnet), security-reviewer (Claude Opus), architect (Claude Opus), qa-reviewer (Claude Sonnet) | conditions U1–U4, F1–F6 (F1 BLOCK-UNTIL before RS1), A1–A8, Q1–Q9; B-135 opened |
| RS1a | security-reviewer (Claude Opus) | F1 still OPEN → REQUEST-CHANGES: H1/M2/L1/L2 fixes + M1 residual; **re-verified twice** → F1 CLOSED 10/10 probes |
| RS1b | code-reviewer (Claude Opus) | REQUEST-CHANGES BLOCK-UNTIL F1/F2 → six fixes (pure `_entitlement`/one snapshot, the full exposure census, required `confirm_owning_batch`, TOCTOU precedence, two signers, typed refusals); F2 re-opened then closed |
| RS2 | code-reviewer (Claude Opus) + ux-reviewer (Claude Sonnet) | F1/F2 blocks (sign worker's own token, `exit_on_error=False` + ERROR handling) + U1–U5; N1/N2 fixed by the orchestrator |
| full-suite | orchestrator | the truncator-census catch: `_elide_middle`/`_take_cells` cut before coercing → 20 failed at `b549ca5`, fixed at `b9e7fa7` (census 3→5) |
| DDR | architect (Claude Opus) + qa-reviewer (Claude Sonnet) | approve with conditions C1–C4, Q1–Q3, all discharged |

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

- **New controls:** none — the batch's lessons are about runner timeouts, per-increment verification-list coverage and the privacy grep, which the existing census/independent-review/privacy controls already own; they are recorded under §7 rather than minted as rules.

---

## 3 · Working-file reconciliation (C-44)

| File | State | Evidence |
|---|---|---|
| `mapper/reqharness/{reviews,records,config,derive,signing,release}.py`, `mapper/screens/review.py`, `mapper/screens/home.py`, `mapper/keymap.py`, `mapper/app.py` | ✅ committed on `feat/review-screen-batch`; merge into the trunk is the operator's (no standing authorization) | `git log 6121987..HEAD` |
| `tests/test_reqharness_registry.py`, `tests/test_reqharness_signing.py`, `tests/test_reqharness_release.py`, `tests/test_review_screen.py` + the moved census/seat pins (`test_inc9*.py`, `test_keymap.py`, `test_key_dispatch.py`, `test_darkside_census.py`, `test_mod_parity.py` + the two goldens, `test_en5.py`, `test_app_imports_used.py`, `test_a3_census.py`, `test_repair_map_truth.py`) | ✅ committed | DDR row 5/6 |
| `docs/ARCHITECTURE.md` | ✅ committed (RS2's A5/F1 amendment) | `increment-003.md:75` |
| `REQUIREMENTS.md` (17 folded rows), `.dev-flow/BACKLOG.md` (B-133 extended, B-135), `04-validation.md`, `05-close.md`, PDR/DDR seals | 📋 uncommitted at hand-back; the orchestrator commits them | `git status` |

- **Found before the batch:** `none — no tracked file was modified when the batch began` (fresh worktree; the only diff at open was this batch's own `state.json`)

### Conditional-gate discharge

- **Conditional-gate discharge:** `18 condition(s) · ✅ all discharged` (18 at the PDR: C-1…C-18; 4 at the DDR: C1–C4; 3 at the DDR: Q1–Q3 — all re-read in the artifact, none on trust)

| Condition | Discharged? | The artifact line that proves it |
|---|---|---|
| PDR C-1…C-18, D1–D5 | ✅ | `design/DDR-2026-10-15-review-screen-batch.md` §B condition table (each re-read in the artifact) |
| PDR §E (F1 re-verification) | ✅ | H1/M2/L1/L2 fixes; M1 residual; F1 CLOSED 10/10 (`increment-001.md:168-170`) |
| DDR C1 (public `entitlement`/`chain_reason`) | ✅ | `signing.py` `__all__`; `review.py:958-976`; `docs/ARCHITECTURE.md:119` |
| DDR C2 (`entitled_to_sign` agrees with `sign_review`) | ✅ | shared `_unapproved_config` first arm; new node RED-proven |
| DDR C3 (DDR text corrections) | ✅ | C-17 four causes; row 2 fail-closed declaration |
| DDR C4 (exit-time residual stated + B-133) | ✅ | DDR §C open notices; `.dev-flow/BACKLOG.md` B-133 |
| DDR Q1–Q3 (width parametrisation, hostile hint, digest block) | ✅ | `tests/test_review_screen.py` `WIDTHS`; Q2 node; `evidence/rs1a-red.transcript` digest block |

---

## 4 · Backlog reconciliation — the carry-over contract

| Item | Move | Reference |
|---|---|---|
| B-134 | done in this batch (the review/signing screen) | increments 001–003; row still to be struck through in `BACKLOG.md` at merge |
| B-133 | extended (the review screen inherits the exit-time thread residual; plus a confirmed sign can finish writing after pop/quit) | DDR C4 |
| B-135 | opened: an `authors` change needs a second admin (F3); M1 residual (cell moved before signing) | PDR F3; security re-verification |
| B-124, B-125, B-126 | stay OUT (deferred — the screen signs and browses, it does not diff commit-vs-reviewer / show baselines / recover forks) | PLAN R5 |
| B-128, B-129, B-130, B-131, B-132 | carried, untouched (loading cue, `? ` copy, CSV BOM, CSV quoted newline, module-map edge) | previous batch |

**Accepted residuals.**

- **M1.** An author who can edit the canon can move an object's `Owning batch` cell to a batch they are not listed for before signing; the digest does not stop it (the author signs after the move). Mitigations: canon edits are git/PR-reviewed; `authors_declared` requires every batch declared; full closure needs per-object authorship (operator chose per-batch, R6).
- **F3 (→ B-135).** An admin-author can approve their own `authors` change (self-approved policy).
- **F4.** One human declared twice with two emails.
- **Agent-driven signing.** `sign_review` cannot prove a human pressed the key — an agent in the operator's shell inherits the operator's git identity; the two-key confirm guards only the TUI.
- **Impersonation.** git identity is self-claimed; the chain proves integrity and approval, not authorship. B-122 strong mode remains the named follow-up.
- **Confinement race.** The inherited `confine_reason` → `mkdir` → `open` race is an accepted core residual.
- **Exit-time thread (B-133, extended).** Quitting mid-load/mid-sign keeps the process alive up to the same ≈ 30 s bound; PLUS a confirmed sign can finish writing its review file AFTER pop/quit with no UI confirmation.

**Open items for the next batch:** B-124, B-125, B-126, B-128, B-129, B-130, B-131, B-132, B-133 (extended), B-135 — plus the **success-message decision** (the screen currently signs silently; whether a success message is owed is the operator's call, and any new copy needs a prototype verdict).

---

## 5 · Batch metrics — the 13 keys of `core`

```yaml
type: dev-flow-batch
project: mapper
batch_id: 2026-10-15-review-screen-batch
mode: core
verdict: pass
increments: 3
source_files_max: 4              # RS1a (4) and RS2 (4)
notices_raised: 4                # DDR §B rows 1, 2, 3, 5 (⚠)
rework_returns: null             # not recorded by the phase checklists
triggers_fired: "A2,A3,B4,C1,C8,D1,E1,F1"
tests_base_to_post: "3432 -> 3533"
new_control: none
open_items_next: 10              # B-124, B-125, B-126, B-128, B-129, B-130, B-131, B-132, B-133, B-135
```

---

## 6 · Human review ledger — what a human audited, at what depth

| Artifact | Machine verdict (citation) | Human review | Depth | Deliberately NOT reviewed |
|---|---|---|---|---|
| `01-requirements.md` | gate §4 green; PDR sealed | ❌ | `none — read by independent model reviewers only` | |
| Test cases / ATs | 18 ATs in 18 nodes; 33 mutants RED | ❌ | `none` | |
| Code | full suite 0 failed; four independent reviews + DDR | ❌ | `none — model reviewers only` | not audited line by line by a human |
| `04-validation.md` | validator | ❌ | `none` | real-user evaluation `not performed — one-person team` |

- **Human perimeter:** whether a silent sign (no success message) is acceptable to a real operator — and the merge decision — are the operator's; the self-approval business judgement is B-135.
- **Human review ledger:** `none — this batch recorded no human review; every reading was by a model reviewer, named per station in §1` (the §6.6 copy verdict `Aprobado` was an operator *decision*, not an artifact review)

---

## 7 · Lessons

- **Worker 2-hour timeout on a large UI increment.** DeepSeek staged the whole RS2 screen and timed out after 2 hours; Claude Opus finished the hang diagnosis, the seven defects, the census pins and the RED battery. A UI increment the size of RS2 (a new screen + seat + 18 painted-frame ATs) is too large for one worker under a 2-hour cap — split UI increments smaller, or plan a hand-off point.
- **Per-increment verification lists missed the truncator censuses.** RS2's `_elide_middle`/`_take_cells` are truncators and did not coerce before cutting; the RS2 per-file list did not include `test_inc3_census.py` / `test_darkside_budget.py` (LLR-COERCE.2), so the full-suite gate caught 20 failures the increment gate missed. A screen that adds a truncator must run the coercion-census files in its own gate list.
- **A personal path reached a committed transcript twice.** Check the privacy grep (`tests/test_no_operator_paths.py` / the A-110 guard) BEFORE chaining a commit, not after — the operator path leaked into a committed transcript on two occasions this batch and had to be scrubbed.
- **DeepSeek runner timeout made configurable.** The runner's fixed cap forced the hand-off in lesson 1; the cap is now a tunable parameter so a long review/suite can complete instead of dying mid-run.

---

## 8 · Evidence checklist (software-dev)

- [✓] Tests/type checks/lint pass — full suite ``3543 passed, 24 deselected, 3 xfailed, 13 warnings in 2029.79s (0:33:49)` — 0 failed; clean shell, code at ff6262f (847231b + gate record); the 24 deselected are the `slow` and `network` markers` (orchestrator run; not re-run by this record).
- [✓] No secrets in code or output — records only; no key, token or personal path written (the privacy grep is green).
- [✓] No destructive commands run — only file edits and read-only git.
- [✓] File count within cap — source max 4 per increment; this close touches no `mapper/` or `tests/` file.
- [✓] Review packet attached — `03-increments/increment-001..003.md`, §4b reviews recorded.
- [✓] Test ledger reconciles to the node — `+101 / −0` measured at the DDR, follow-ups declared (§04).
- [✓] Requirements canon folded — 17 ids in `REQUIREMENTS.md` (`--fold-canon`); V22 clear.

---

## §fold — ids this batch adds to `REQUIREMENTS.md`

`HLR-RS.1` · `HLR-RS.2` · `HLR-RS.3` · `HLR-RS.4` · `HLR-RS.5` · `LLR-RS.1.1` · `LLR-RS.1.2` · `LLR-RS.1.3` · `LLR-RS.1.4` · `LLR-RS.1.5` · `LLR-RS.2.1` · `LLR-RS.2.2` · `LLR-RS.2.3` · `LLR-RS.2.4` · `LLR-RS.4.1` · `LLR-RS.5.1` · `LLR-RS.5.2` — 17 ids.
