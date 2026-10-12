# Design review record — DDR — mapper — Batch 2026-10-11-reqharness-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.

> **Owed in.** `core` by trigger · `full` ✓
> **Source:** `/dev-flow-init` step 4's seed-by-level table, which is this fact's one home. A level marked `—` **does not owe this artifact, and its absence is not an omission**; `by trigger` means the station exists only when the `triggers` block fired, and `stations_active` in `state.json` is the authority for *this* batch. Where a SECTION or a gate row is owed more narrowly than the artifact, it says so on the row.

> **Where this lives: the VAULT + Drive.** It is **sealed** and **cited by id** from the repo.
> A record in Drive has no diff, no PR and no CI — that is a real boundary of the design, not an
> oversight. The seal is what compensates: **if this record changes after the seal it is a NEW version
> with a NEW id**, never a silent edit, and the requirement that cited the old id keeps pointing at the
> old one — which is exactly the signal you want to see.

> **Notice convention.** `⚠` yellow = notice, declare the reason and continue · `✗` red = block ·
> `✓` green = satisfied **with its evidence cited**. Without a citation an item is asserted, not satisfied.

| Field | Value |
|---|---|
| Record id | `DDR-2026-10-11-reqharness-batch` |
| Reviews | `PDR-2026-10-11-reqharness-batch` (sealed 2026-10-11, `approved with conditions`: R27 limbs a–g, implementation conditions G1–G6 / H1–H4, decisions D1–D7) / increments RH1–RH6b on one trunk; RH2 ‖ RH3 ran as parallel lanes and joined at the trunk (`03-increments/increment-002.md`, `increment-003.md`) |
| Participants | `architect` (Claude Opus) · `qa-reviewer` (Claude Sonnet) · `security-reviewer` (Claude Opus), all read-only; independent security re-check by a separate session (Kimi K3) on an exported copy; follow-up fixes authored by Kimi (`kimi-code/kimi-for-coding`) as the software-dev lane |
| Date sealed | `2026-10-11` |
| **Verdict** | `approved with conditions` → all conditions discharged. Coverage ✓ (traceability 100 %: US 3/3 · HLR 9/9 · LLR 36/36 · AT 9/9, `06-docs/traceability-matrix.md`) · Certainty ✓ (full suite `3376 passed, 0 failed` at the close, `04-validation.md`) · Evidence ✓ (RED transcripts with sha256 restores under `evidence/`). Security was `BLOCK-UNTIL F1, F2`; both discharged and the independent re-check returned `CLEARED-WITH-NITS` (nits fixed, `03-increments/increment-008-ddr-fix.md`) |

---

## A · PDR checklist — preliminary design review

Not re-litigated here: see the sealed `PDR-2026-10-11-reqharness-batch` section A (rows 1–10, approved with conditions after three P1 review rounds, rulings R1–R27).

---

## B · DDR checklist — detailed design review

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, **and why** | ✓ | git resolution walks PATH itself instead of `shutil.which` (review F4 HIGH: Python < 3.12 searches the cwd) — LLR-RH.7.3 amended, ledger entry; `--audit` runs after the UTF-8 re-wrap (LLR-RH.7.2 amended); YAML nesting bound moved from a lexical pre-scan to the libyaml event stream (security F2 HIGH: the lexical scan was bypassable); parse cache gained a stat fast path to meet LLR-RH.5.4 (5.27 s → 0.443 s, `increment-010-perf.md`, ledger `.36`); `reqharness/model.py` renamed `records.py` (historical citations of `model.py` became ambiguous) — PDR §E "DDR amendments" |
| 2 | Frozen interfaces still intact — or the work returned to the trunk and it is declared | ✓ | the headless core imports nothing beyond stdlib + PyYAML + `mapper.osopen` (architect AST census); only `screens/roles.py`, `screens/home.py` and the `--audit` dispatch import the core; the audit CLI moved into `reqharness.audit.run_cli` so `app.py` gains no def (`increment-009-gate-fix.md`) |
| 3 | **Reverse census CROSSED between lanes** | ✓ | RH2 ‖ RH3 touched disjoint files (`chain.py` vs `identity.py`); the RH4 merge conflict on `chain.py` was resolved keeping every security fix and re-proved by M-CH6 and M-PR1 (`evidence/rh4-merge-red.transcript`) |
| 4 | Every `AT-NNN` realises in **exactly one** on-disk node (C-18) | ✓ | AT-077a/b/c, AT-078…AT-083 each in one node (`tests/test_roles_screen.py`, `test_reqharness_release.py`, `test_reqharness_baseline.py`); AT-077 is an umbrella realised by 077a/b/c (stated in `01-requirements.md`) |
| 5 | Test ledger **summed** across lanes, reconciled | ✓ | full suite at the close: `3376 passed, 24 deselected, 3 xfailed` in a clean shell (`04-validation.md`); the gate run first found 8 repo-wide guard failures the per-increment subsets missed — fixed at the root (`increment-009-gate-fix.md`) |
| 6 | No lane touched another lane's file | ✓ | code and documents lanes ran concurrently on disjoint file sets (DDRFIX-A code / DDRFIX-B documents) |
| 7 | Source-file budget: any lane that reached or exceeded 4, reviewed here | ⚠ | RH4 5/4 (pending resolution belongs in the chain verifier) and RH5 5/4 (a reviewed identity nit folded in) — approved by the orchestrator under the standing authorization and recorded in each packet |
| 8 | **Every open PDR condition discharged one by one, by RE-READING the artifact** | ✓ | table below |

| # | Condition left open | Discharged? | The artifact that proves it |
|---|---|---|---|
| G1–G6 · H1–H4 | PDR implementation conditions | ✓ | verified at each increment gate (`increment-001…007.md`, code-review follow-ups with RED proofs) |
| ARCH-1 | requirement text stale on git resolution / anchor pre-scan | ✓ | LLR-RH.7.3 amended + ledger; PDR §E |
| ARCH-2 | `--audit` order vs UTF-8 re-wrap | ✓ | LLR-RH.7.2 amended; PDR §E |
| ARCH-3 | `chain` ↔ `pending` import cycle | ✓ | shared pieces moved to `config.py`; `tests/test_reqharness_modgraph.py` |
| ARCH-4 | multi-event fork recovery had no backlog home | ✓ | B-126 widened (`.dev-flow/BACKLOG.md`) |
| ARCH-5 | stale ARCHITECTURE rows; private cross-module call | ✓ | `docs/ARCHITECTURE.md` rows corrected; `audit.py` uses the public `osopen` link helper |
| QA-1 | absent registry reported as `chain broken` | ✓ | named state `no registry yet` + node + RED (`increment-008-ddr-fix.md`) |
| QA-2…6 | missing REDs (M-FR3/FR4/LM1), vacuous census, untagged nodes, canon rows, mutant catalogue | ✓ | `evidence/ddrfix-red.transcript`; `04-validation.md`; PDR §E mutant list |
| SEC-F1 | terminal-escape / newline injection in `--audit` output | ✓ | one escaper on every interpolated value incl. Unicode Cc/Cf/Zl/Zp; re-check scanned all code points |
| SEC-F2 | superlinear / crashing deep-nesting parse | ✓ | depth bound on the libyaml event stream (refused at 65 before compose), re-check: 23 shapes refused ≤ 5 ms, no crash |
| SEC-F3…F5 | pending write confinement · append lock + newline · approver ≠ requester in the walk | ✓ | `increment-008-ddr-fix.md`; F5 `requested_by` label check recorded as residual |
| K3 LOW-1…4 | named depth refusal · Zs/Mn escaping · `config.yml` cap · 4 MB depth-63 cost | ✓ | fixed (1, 3, 4) with RED; LOW-2 recorded as residual (repo-write gated) |

---

## C · Verdict and what it means

`approved with conditions`, every condition above discharged and re-read; the remaining residuals are stated in the PDR threat model and §E (layer-3 repo-write trust boundary, stat fast-path in-place rewrite, roles-screen git calls on the UI thread → B-127).

## D · Ids this record binds

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| git resolved by an own PATH walk | `DDR-2026-10-11-reqharness-batch#B1` | LLR-RH.7.3 (`01-requirements.md`) + `docs/ARCHITECTURE.md` reqharness row |
| YAML depth bound on the event stream | `DDR-2026-10-11-reqharness-batch#SEC-F2` | `mapper/reqharness/config.py`; `docs/ARCHITECTURE.md` safety notes |
| parse-cache stat fast path | `DDR-2026-10-11-reqharness-batch#B1` | LLR-RH.5.4 + ledger `.36`; `docs/ARCHITECTURE.md` |
