# Batch close — mapper — Batch 2026-10-10-csv-safety-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language — the **prose**,
> and never a label.

> **Owed in.** `core` ✓ · `full` —

> **Field guide:** `templates/guides/close-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

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
| Gate record | `python devflow-validate.py .` from the project root · exit 0, **0 block** · 2026-10-10. The third full-suite gate run (the increment-4 tree, test-only, `53807c4`): **3157 passed / 3 xfailed / 0 failed** (`evidence/gate-run3-full-suite.transcript`). Runs 1–3 of the gate suite and the increment-1 gate are recorded in `04-validation.md` §Signed-balance test ledger. |
| Gated tree | `63095f24a023e5f653f3e73fca7067424587aba0` · dirty — `.dev-flow/2026-10-10-csv-safety-batch/04-validation.md`, `05-close.md`, `docs/ARCHITECTURE.md` (the §4 amendment owed by ruling R10), `evidence/p4-save-cost.transcript`, `spike/p4_save_cost.py` (the close record itself excluded) — **later commits change no code:** `git diff 53807c4 HEAD -- mapper tests` is empty (re-checked by the final qa-reviewer at `581c21a`); gate run 3 at `53807c4` is the gating suite run |
| Requirements canon | `REQUIREMENTS.md`. Every id this batch declares as a heading (`HLR-CSV.1`, `HLR-CSV.2`, `HLR-CSV.3`, `LLR-CSV.1.1`, `LLR-CSV.1.2`, `LLR-CSV.1.3`, `LLR-CSV.2.1`, `LLR-CSV.2.2`, `LLR-CSV.2.3`, `LLR-CSV.3.1`) is folded into it at this close — **the orchestrator runs the fold**; at the drafting of this record the canon holds 0 CSV rows (`grep -c 'HLR-CSV\|LLR-CSV' REQUIREMENTS.md` → 0). |

- **The gate runs that stand behind this close** (`04-validation.md` owns the citations): P0 base `a36f63e` — 3133 passed / 3 xfailed (modular close); increment-1 gate at `d4941ea` — 4 failed / 3139 passed (the model-field totality guard caught the new unclassified CSV fields; fixed in `6763852`); final run 1 — 3 failed / 3153 passed (modular move oracle + A3 pin, both follow-ups); final run 2 at `1537985` — **3156 passed / 0 failed**; final run 3 (increment 4, test-only) — 3157 passed / 3 xfailed / 0 failed at `53807c4` (run 3).
- **The P4 performance record** (C2/R12): `MapStore.save` on a 6 000-node wide tree, median of 3, tmp workspace — with the round-trip check 2.774 s vs 2.687 s skipped → added 0.087 s = **3.2 %** of save wall time, threshold ≤ 25 % — `evidence/p4-save-cost.transcript` (sha256 `bb07e56fe3c4c237…8492a4`).

---

## 1 · What changed

**A CSV import that cannot be re-opened is now refused before any byte is written — and the operator is told why before they press save.** B-114 reproduced it: two rows whose ids slugify to the same id (`a-b` / `A B`) collapsed into one node with two parents, saved with `save_error: null`, and failed re-open with a `ParseError`-derived `MapStoreError`. Now: `MapStore.save` round-trips the exact `.mmd` text it is about to write through its own loader and refuses — before the two-phase write begins — any graph whose saved form would not load back as the same node-id set and edge set (one `dump` per save; the root is not compared, ruling R11); the import preview records every slug collision with its source rows (`Graph.csv_collisions`, build-time provenance, never persisted) and paints the exact refusal sentence naming the colliding rows' line numbers and raw ids, precedence collision > multi-parent > cycle; and the preview refuses at the `s` keypress — no name asked, pinned error toast, nothing written. A valid CSV imports, saves and re-opens unchanged (AT-074).

| Requirement | Version | Verified by | Verdict |
|---|---|---|---|
| `HLR-CSV.1` | `v1` | `AT-072` · `test_save_refuses_*` · M1/M1b killed | pass |
| `HLR-CSV.2` | `v1` | `AT-073` · `AT-072b/c/d` · M2/M2b/M2c killed | pass |
| `HLR-CSV.3` | `v1` | `AT-074` · round-trip nodes · M3 killed | pass |
| `LLR-CSV.1.1` | `v1` | 4 refusal nodes + dump-once pin · M1 · M-dump2/M-dumpwrite · P4 3.2 % ≤ 25 % | pass |
| `LLR-CSV.1.2` | `v1` | `test_refused_save_changes_no_workspace_byte` · M1b | pass |
| `LLR-CSV.1.3` | `v1` | `test_save_accepts_legacy_forest_after_edit` · M4 | pass |
| `LLR-CSV.2.1` | `v1` | `test_preview_csv_records_collisions` · M2b | pass |
| `LLR-CSV.2.2` | `v1` | `AT-073` + grammar/markup/cycle nodes · M2 | pass |
| `LLR-CSV.2.3` | `v1` | `AT-072b/c/d` · M2c | pass |
| `LLR-CSV.3.1` | `v1` | round-trip equality nodes · `AT-074` · M3 | pass |

- **Reviews that stand behind the table:** P2 architect + qa-reviewer, **two rounds** (round 1 → `iterate-to-refine`, 5 blockers; round 2 → `approve-with-conditions`, rulings R11–R16); **PDR** sealed; **three code reviews** (`code-reviewer`, Claude, read-only — increments 1 and 2 APPROVE-WITH-NITS, 0 HIGH; nits closed in increment 3); **DDR** (drafted by the worker Kimi, conditions discharged in increment 4, sealed approved at `63095f2`); and the increment **re-reviews**. All reviewers were Claude models, read-only; the worker was Kimi (`kimi-code/kimi-for-coding`, units CSVI1–CSVI4, CSVCLOSE).
- **Decisions:** D1 (the store refuses what its loader refuses, riding `_save_or_toast`'s surface at the store layer), D2 (the preview tells the operator why, in the panel they are looking at), D3 (`preview_csv` records which original rows collapsed into which slug); the rejected alternative — silently disambiguating ids (`a-b`, `a-b-2`) — changes the user's data without telling them. Orchestrator rulings R1–R16 and the 11 ledger entries (`LED-2026-10-10-csv-safety-batch.1`…`.11`) record the two review rounds.

### Process lessons (measured origins — fed to the flow's own backlog, §2)

1. **A move oracle must not outlive its batch as a freeze.** The modular batch's `test_llr_mod_4_3_bodies_match_baseline` carried a `DECLARED_CHANGES` freeze on every moved body; this batch's two preview bodies tripped it at gate run 1 (3 failed / 3153 passed), and the freeze had to be **retired** (increment 4, DDR architect MED-1): a permanent freeze taxes every later batch, and per-batch declarations become permanent exemptions. The retirement shipped **with** a new loss-arm negative control — a deleted moved method must redden `missing` — so loss detection did not go down with the freeze.
2. **A guard that classifies every model field caught a new field at the gate — a control that worked.** The increment-1 gate failed 4 on `test_at_p02i_every_model_field_is_classified[Graph]`: `Graph.csv_collisions` / `CsvRow` / `CsvCollision` arrived unclassified (no sidecar writer, no text/non-text verdict). Fixed in the same gate loop (`6763852`). Totality guards earn their keep exactly at moments like this.
3. **A vacuous mutation must be retargeted, not celebrated.** M3's original wording ("make `mermaid.dump` omit node titles") could never redden anything — `dump` never wrote titles (they live in the `_nodos.yml` sidecar) — and no transcript had ever run it (DDR qa MED-2, `LED-…-batch.11`). The retargeted M3 (drop the title from `_build_sidecar`) is executed RED in increment 4.
4. **A store-side mutation is not a preview-layer acceptance's control.** AT-072's CSV carries a non-empty collision record, so the preview refuses at the `s` keypress before the store is reached; per-layer controls (ruling R14) keep each layer honest at its own nodes.

---

## 2 · New controls discovered — and where they landed (C-45)

| Control | What failure it closes | Measured origin |
|---|---|---|
| *(existing in-repo guard, proven at this batch's gate)* **model-field totality guard** (`test_at_p02i_every_model_field_is_classified`) | a new model field/dataclass arriving without a text/non-text + sidecar-writer classification | increment-1 gate, 4 failed at `d4941ea` → fixed `6763852` |
| *(lesson for the flow)* **a move oracle must not outlive its batch as a freeze** | a permanent changed-freeze taxing every later batch; per-batch declarations becoming permanent exemptions | gate run 1, 3 failed → retired with a loss arm in increment 4 |
| *(lesson for the flow)* **a mutation must be shown effective before it is cited** | vacuous negative controls that never redden anything (M3's original wording) | DDR qa MED-2, `LED-…-batch.11` |

**The four landings — record which ones actually happened. Command-but-not-template is *half-encoded*, and the missing half is the enforceable one:**

| # | Landing | Done? | SHA / path |
|---|---|---|---|
| 1 | the **command** (`commands/…`) — the rule itself | ❌ | flow-side, not landed: the flow bundle is owned by the operator (B-106's premise); the batch feeds the lessons to the flow backlog |
| 2 | its **artifact** (a template section) | ❌ | same reason |
| 3 | the **catalog** entry (`dev-flow-lessons`) with its measured origin | ❌ | same reason — the measured origins are recorded above and in `04-validation.md` |
| 4 | **committed and pushed**, manifest re-hashed and bumped | ❌ | same reason; nothing pushed from this batch (no `origin` premise) |

- **New controls:** 0 minted in the flow — the flow-side landing is the operator's, and the measured origins above are the catalog material. In-repo, the batch left permanent guards behind: the dump-once pin (`test_save_writes_the_bytes_dump_returned_and_dumps_once`), the no-write sha256 oracle, the LLR-CSV.1.3 forest pin and the retired-freeze loss arm.

---

## 3 · Working-file reconciliation (C-44)

| File | State | Evidence |
|---|---|---|
| `mapper/model.py`, `mapper/store.py`, `mapper/import_csv.py`, `mapper/screens/import_preview.py` | ✅ committed and landed (increments 1–2; the model-field classification follow-up `6763852`; merge `53807c4` lineage on this branch) | the increment packets' §2 tables; gate run 2 green at `1537985` |
| `tests/test_csv_safety_store.py`, `tests/test_csv_safety_preview.py` (new) · `tests/test_mod_bodies.py`, `tests/test_repair_store_boundary.py`, `tests/test_a3_census.py` (modified) | ✅ committed, same lineage | `git diff a36f63e HEAD --stat -- tests` — 5 files, +744/−12 |
| `docs/ARCHITECTURE.md` | 📋 left on purpose, path + remaining work in the backlog of this close — the §4 `Graph`/`MapStore` row amendment of this unit (worker CSVCLOSE) rides the orchestrator's close commit | the amended rows carry `*(amended 2026-10-10-csv-safety-batch: …)*` |
| `.dev-flow/2026-10-10-csv-safety-batch/**` (requirements, ledger, review, PDR, DDR, 4 increment packets, this close, `04-validation.md`, `evidence/p4-save-cost.transcript`, `spike/p4_save_cost.py`) | 📋 left on purpose — the orchestrator's close commit | the batch tree |

- **Found before the batch:** `none — no tracked file was modified when the batch began` (the tree was clean at intake; B-114's evidence lives on the perf-batch branch, not in this tree)

### Conditional-gate discharge

- **Conditional-gate discharge:** none — no gate closed conditionally

---

## 4 · Backlog reconciliation — the carry-over contract

| Item | Move | Reference |
|---|---|---|
| B-114 | **DONE** — a CSV import can no longer save a map that cannot be re-opened: store round-trip refusal + preview collision record/sentence + `s`-keypress refusal | AT-072/072b/072c/072d/073/074; `test_save_refuses_*`; M1–M4 transcripts |
| B-115 | **CARRIED** (untouched, pre-existing) — the `slugify("") == "n"` empty-slug family; routed out of this batch at P2 round 1 (ruling R4) | `.dev-flow/BACKLOG.md` B-115; `mapper/mermaid.py:51`, `mapper/import_csv.py:61` |
| B-116 | **CARRIED** (untouched, pre-existing) — a CSV listing a child before its root is refused as a cycle (row-order contract undefined) | `.dev-flow/BACKLOG.md` B-116; `mapper/import_csv.py:97-102` |
| B-117 | **RECORDED this batch, CARRIED** — a forest's root drifts on reload (`dump` writes edges before parentless nodes); the round trip deliberately does not compare the root (ruling R11), and LLR-CSV.1.3 + M4 pin the exclusion — fixing the drift is the carry | `.dev-flow/BACKLOG.md` B-117; `LED-…-batch.5`; `test_save_accepts_legacy_forest_after_edit` |
| the perf batch (`2026-10-10-perf-batch`) | **RESUMES** — B-33 territory: `dump`'s parentless-node loop is O(N·E) (`mapper/mermaid.py:152-153`), measured and explicitly NOT fixed here (ruling R12); the csv-safety check adds only one `parse` of the already-dumped text (3.2 % of save wall time) | `evidence/p4-save-cost.transcript` |
| the canon fold | **THE ORCHESTRATOR RUNS IT** — the ten `HLR-CSV.*`/`LLR-CSV.*` ids fold into `REQUIREMENTS.md` at this close | §0 Requirements canon |

---

## 5 · Batch metrics — the 13 keys of `core`

Extract, do not invent: a key the artifacts did not record goes `null`, and the key is never dropped.

```yaml
type: dev-flow-batch
project: mapper
batch_id: 2026-10-10-csv-safety-batch
mode: core
verdict: pass
increments: 4
source_files_max: 2          # increments 1 and 2 each touched 2 source files (model+store / import_csv+import_preview); increments 3 and 4 are test- and doc-only
notices_raised: 34           # P2 round 1: 24 findings (5 blocker/11 major/8 minor); round 2: 10 findings — both rounds declared in 02-review.md
rework_returns: 2            # P2 round 1 -> iterate-to-refine -> round 2; gate run 1 (3 failed) -> follow-up commit 1537985 (the increment-1 gate failure -> 6763852 happened inside increment 1's own gate loop)
triggers_fired: "A2,A3,B1,B4,C6,C8,D1,E1,F1"
tests_base_to_post: "3136 -> 3160"
new_control: none            # flow-side; measured origins recorded in §2. In-repo guards: dump-once pin, no-write oracle, forest pin, retired-freeze loss arm
open_items_next: 3           # B-115, B-116, B-117
```

---

## 6 · Human review ledger — what a human audited, at what depth

| Artifact | Machine verdict (citation) | Human review | Depth | Deliberately NOT reviewed |
|---|---|---|---|---|
| `01-requirements.md` + ledger | P2 architect + qa-reviewer, two rounds; PDR sealed; 11 ledger entries | ❌ | `none` | the whole contract |
| Product code + tests | three code reviews APPROVE-WITH-NITS, 0 HIGH; nits closed in increment 3; M1–M4 executed RED | ❌ | `none` | — |
| `04-validation.md` | gate run 3 (`53807c4`): 3157 passed / 3 xfailed / 0 failed; ledger reconciles 3136 − 0 + 24 = 3160; P4 perf 3.2 % ≤ 25 % | ❌ | `none` | — |
| DDR + increment packets | sealed approved at `63095f2`; six conditions discharged in increment 4 | ❌ | `none` | — |

- **Human perimeter:** the operator owns the flow-side rulings this batch surfaced (the move-oracle-freeze and vacuous-mutation lessons, §2), the carried backlog dispositions (B-115/B-116/B-117) and the canon fold. Whether the flow should adopt the lessons as encoded controls is the operator's decision, not this batch's.
- **Human review ledger:** no human audited any artifact of this batch (`none`, every row above). The operator authorized an autonomous batch ("Batch corto antes (Recomendado)", 2026-10-10); every reviewer seat was a read-only Claude model (architect Opus, qa-reviewer and code-reviewer Sonnet) and the single worker was Kimi (`kimi-code/kimi-for-coding`). The operator's review surface is the PR and this close.

