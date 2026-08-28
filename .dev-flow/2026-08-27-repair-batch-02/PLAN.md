# PLAN — `2026-08-27-repair-batch-02` (living compendium)

> **BLUF.** This batch repairs exactly four shipped defects that the `2026-08-26-ui-next-batch-02`
> PDR second pass found on `master`. None of them is a requirement defect, so no amount of
> requirements folding fixes them. The feature batch stays PARKED and is commissioned separately
> after this merges.

**Mode:** `full` (inherited: client-grade V-model, merge authority granted).
**Language:** artifacts and code English; UI strings Spanish.
**Branch:** `fix/repair-batch-02`. **Base ref (RC-1):** `d877784` = `origin/master` = merge-base.
**Flow revision:** rev46 (recorded at the feature batch's un-park; unchanged this session).

---

## 1 · Where we are

| Station | Status | Note |
|---|---|---|
| P0 intake | ✅ approved | four defects lifted from the feature batch's PDR pass 2 |
| P1 requirements | ✅ approved | `01-requirements.md`, 8 premises executed, 17-position derived census |
| PDR | — not applicable | this batch moves no boundary; it *lands* the boundary the feature batch's ARQ already approved |
| P3 Inc-1 | ✅ **PASS** | store boundary. Three independent review rounds: BLOCKED (9 findings) → OK WITH FIXES (4) → PASS (2 folded). 70 arms, 19 mutants |
| P3 Inc-2 | ✅ complete | `docs/ARCHITECTURE.md` amendment landed. **Six** false claims corrected, not the four the ARQ named. 26 arms, 4 mutants |
| P3 Inc-3 | ✅ complete | derived pin census (12, not 18) · `B3` correction pinned · 51-node fixture, no budget. 9 arms, 5 mutants |
| P4/P5/P6 | 🔄 in progress | whole-branch `security-reviewer` + adversarial `qa-reviewer` dispatched as merge gates |

**Session-death recovery note (interruption protocol).** The prior session checkpointed
code-complete on Inc-1 and died awaiting the blast-radius gate. Per the resume rule the on-disk
tree was **re-verified, not trusted**: `git status` shows exactly `mapper/store.py` modified plus
the untracked `tests/test_repair_store_boundary.py`, and the suite re-collects **479** = the
recorded baseline 429 + the 50 nodes the checkpoint claimed. Nothing was regenerated.

---

## 2 · Objective

Four shipped defects, decided by the operator's delegate as **option B** at the feature batch's PDR:

1. **`S-02` live** — coercion extended to every derived text family (`HLR-STO.1`, Inc-1).
2. **`LLR-STO.1.1` phantom** — the requirement 24 prose citations depended on, written for real with
   executable predicates (part of Inc-1's requirements record).
3. **`ARQ-1`** — the `docs/ARCHITECTURE.md` amendment the feature batch's PLAN §7 recorded as
   approved was never landed (Inc-2). C-44: work that never landed.
4. **`GOLD-1` / `B3-FALSE`** — the byte-identity pin census is **12**, not the 18 the architect lens
   carried; `RadialRenderer`'s four pins redden by construction at the feature batch's Inc-1; and
   trigger `B3`'s "not fired" record is false (Inc-3).

---

## 3 · Out of scope, by operator rider

**`S-18` (the render work-budget / deadline mechanism) is PARKED for the feature batch's PDR.**
This batch may land the honest 51-node measurement fixture and **nothing more** — no budget, no
deadline, no abort. A fixture that asserted a budget would be the bolted-in mechanism the rider
forbids, patched into three private copies of the walk instead of designed once.

---

## 4 · Riders this batch must carry forward

**RIDER-1 (audit instrument).** Before the feature batch's **third** PDR fold, the fold must be
audited against **the lenses' own condition lists**, never against the amendment table. That
instrument has dropped conditions **twice** (the qa pass-2 lens had 2 of its own source findings
dropped by the fold). An amendment table is a container; a green amendment count cannot see what
the fold dropped.

**RIDER-2.** `S-18` returns as a design item at the feature batch's PDR, together with the
pre-authorised A3 renderer-contract change.

---

## 5 · Trigger evaluation (id · verdict · probe)

Evaluated at resume against the batch diff, per C-48 — non-activation carries its probe too.

| id | Verdict | Probe |
|---|---|---|
| **B1** | **FIRED** | `grep -rl "_text_attributes\|_coerce_field" tests/` → `test_repair_depth.py`, `test_store_*` own assertions on the touched symbols. Turns on the reverse census (C-26). |
| **B2** | not fired | no file changes location; `git diff --stat` lists renames = 0 |
| **B3** | **FIRED** | `tests/test_repair_depth.py:93 MASTER_LEGACY_DIGESTS` — 12 derived pins. **This batch's Inc-3 corrects the false non-activation record.** |
| **B4** | not fired | `store.load` produces a `Graph` consumed in-process, no new on-disk artifact; `git diff` adds no writer |
| **A1–A4** | not fired | no module created, no boundary moved, no interface signature changed. Inc-2 *documents* an interface; it does not change one. |
| **C** (security) | **FIRED** | the diff touches the untrusted-file load path; `store.py` parses `yaml.safe_load` output. Whole-branch `security-reviewer` sign-off retained as a merge gate. |
| **D** | not fired | no user-visible surface changes; UI strings added are error text on an existing path |
| **E1** | **FIRED** | 3 planned increments |
| **F** | not fired | flow revision rev46 unchanged since the feature batch's un-park |

---

## 6 · Increment plan

| Inc | Content | Source files | Status |
|---|---|---|---|
| **1** | `HLR-STO.1` / `LLR-STO.1.1` — derived-set coercion + typed refusal | **1** (`mapper/store.py`) | ✅ PASS |
| **2** | `HLR-MAP.1` — land the ARQ amendment, forward-looking rows marked as commitments | **0** source | ✅ done |
| **3** | `HLR-GOLD.1` + `LLR-PERF.1` — derived pin census, `B3` correction, 51-node fixture | **0** source | ✅ done |

Serial. **Inc-1 owns the only source change in the batch** — 1 of the 4-file budget.

---

## 7 · Test ledger

`post = base − D + A`. Base **429** (measured at `d877784`, `pytest -q --collect-only
-p no:randomly -o addopts=`).

| Inc | D | A | Expected post | Observed |
|---|---|---|---|---|
| 1 · resumed checkpoint | 0 | 50 | 479 | **479** — superseded |
| 1 · after the self-found inert-net gap | 0 | 57 | 486 | **486** — superseded |
| 1 · after review pass 1 (9 findings) | 0 | 66 | 495 | **495** — superseded |
| 1 · after review pass 2 (G1–G4) | 0 | 70 | 499 | **499** ✅ (fast 483 + 16 deselected) |
| 2 | 0 | 26 | 525 | **525** — superseded |
| 3 | 0 | 9 | 534 | **534** ✅ (fast 517 + 17 deselected) |

Superseded rows are kept, not overwritten: each was true when measured, and the sequence is the
record of what the four counterfactual passes actually bought — 50 arms at the resumed checkpoint,
70 once every clause the requirement states had a mutant that reddens it.

---

## 8 · Risks and watch-items

- **The outer exception net in `load` is a net, not the repair.** It converts any unforeseen escape
  into a typed `MapStoreError`. Risk: it can mask a genuine programming error as a user-facing
  "ilegible" notice. Mitigated by `raise ... from exc` preserving the chain, and by the coercion
  ladder making the known shapes unreachable before the net is consulted.
- **`_text_attributes()` is retained as a shim** over `_text_fields(Ficha)` because shipped tests
  use that name. Watch-item, not a defect: it is a one-line delegation, not a compat layer.
- **Inc-2 must not land the ARQ proposal verbatim.** The proposal declares
  `mapper/views/state.py` "new this batch" for a file that does not exist. Landing it would trade a
  C-44 defect for a false map — and the map is the oracle the A-family triggers read.
- **⚠ THE SLOW LANE IS KNOWN-FLAKY, ~10%, AND IT IS PRE-EXISTING.** `test_repair_depth.py` asserts
  WALL CLOCK on a shared machine, through two independent mechanisms: an explicit
  `FACTORY_TREE_BOUND_SECONDS = 8.0` budget, and Textual Pilot's own screen timeout. Measured this
  session: 1 failure in 10 slow-lane runs (`test_at_r16b…composed`, `WaitForScreenTimeout`), and
  `test_at_r16…factory_tree` forced to **10.360s against the 8.0s bound** under deliberate CPU load,
  passing at 3.97s and 3.56s once it eased. Unloaded headroom is only 2.4–3.0×.
  **Operational consequence for the rest of this batch: a slow-lane result taken while any other
  suite is running is not evidence.** Not fixed here — outside the four-defect fence; carried to the
  backlog with the recipe and the recommendation to make the bounds load-tolerant, not larger.
  **UNVERIFIED BY EITHER PARTY: whether the flake predates `d877784`.** Neither I nor the reviewer
  ran the slow lane at the base ref. It is *believed* pre-existing because nothing in this diff
  touches `test_repair_depth.py` or the render path it times — but that is an argument, not a
  measurement, and it is recorded as such rather than claimed.

---

## 9 · Decision log (autonomous decisions, recorded not silent)

| # | Date | Decision | Why |
|---|---|---|---|
| D-R1 | 2026-08-27 | Resume Inc-1 from disk rather than re-derive | Interruption protocol: the checkpoint was coherent and the tree re-verified (479 collected = 429 + 50). |
| D-R2 | 2026-08-27 | `PLAN.md` created at resume, not at open | The prior session died before writing it. Recorded as a process gap in the postmortem rather than backdated. |
| D-R3 | 2026-08-27 | The threshold for `HLR-STO.1` is **type-at-the-boundary**, not consumer behaviour | Premise P-8: `search_hits` joins `caption or path`, so a consumer-keyed predicate is invariant under the change it gates for half its input space (C-40 limb 1). |
| D-R4 | 2026-08-27 | `S-02`'s `SATISFIED-EXTERNALLY` strike (feature-batch `D18`) is **withdrawn**, in writing | An axiom re-opens on an executed counterexample. The disposition enlarges the requirement set rather than deleting it (C-43). |
| D-R5 | 2026-08-27 | The typed-refusal nets are gated by **synthetic** cases (shape poisons + a `_reindex` fault injection), not by the position census | The battery found both net mutants INERT: once the ladder covers every position, no container poison reaches a net. C-55 limb 2 — construct the case the tree cannot contain; "there are none today" is why the guard is needed, not a reason to skip it. |
| D-R6 | 2026-08-27 | `_mappings` is scoped to **attachments only**, not to `schema`/`documents` | My first F1 fix routed all three through it, which stopped three `_MALFORMED_SHAPES` arms raising — an unrequested behaviour change that also removed three arms from the net's counterfactual. Schema/document malformed items were never *silently* dropped; they escape to the net, which is loud. Put back to the reviewer for a ruling rather than settled unilaterally. |
| D-R7 | 2026-08-27 | Two `duplicado` records (`campo duplicado:`, `nodo duplicado:`) added beyond the literal findings | F3 and F4 are the same silent-data-loss class; the reviewer proved both destroy operator data on the next save. Recording the collision is the same one-line shape as the existing `campo ilegible:` sink. Flagged to the reviewer as possible scope creep rather than assumed in-fence. |
| D-R8 | 2026-08-27 | The superseded measurement rows in §7 are **kept**, not overwritten | Each was true when measured. Overwriting them would hide what the counterfactual passes bought, which is the only evidence the gate did work rather than rubber-stamped. |
| D-R9 | 2026-08-27 | `_mappings` stays **attachments-only** | Reviewer's Q1 ruling, measured: schema/document item-scalars are DENIED typed; only attachments carried the silent-loss class. Loud denial is already a report; silent discard is not. Asymmetry stated in observable terms in the docstring, per their condition. |
| D-R10 | 2026-08-27 | `documento duplicado` is **kept and declared out-of-fence** | It fires for a coercion collision (in-fence) AND for two plainly identical names (not). Same silent-data-loss class as F3/F4, one line. Declared at the call site and in the packet rather than reverted or smuggled. |
| D-R11 | 2026-08-27 | The slow-lane flake is **identified and recorded, not fixed** | Reproduced with positive and negative controls; pre-existing, in `test_repair_depth.py`, outside the four-defect fence. Fixing wall-clock bounds is a separate piece of work; raising the constant only moves the threshold where the same class reappears. |
| D-R12 | 2026-08-27 | A **negative control** was added that no finding asked for | Every collision arm asserts a record is PRESENT, so an unconditionally-firing guard would pass all of them. `test_at_p02f` + `M-STO-o` close that. Recorded because it is scope I added on my own judgement. |
| D-R13 | 2026-08-27 | The map's forward-looking rows land as **COMMITMENTS**, never present tense | The ARQ proposal declares `mapper/views/state.py` "new this batch" for a file that does not exist. Landing it verbatim would trade a C-44 defect for a **false map** — in the one file the A-family triggers read as an oracle. A map that lies is worse than one that is stale. |
| D-R14 | 2026-08-27 | `AT-P04` reads the composition table's **owned-paths column**, not every path-like string in the map | A naive check reddens on `mapper/screens/prompt.py` (a proposed remediation target) and on the `state.py` commitment — both correct as written. False-failing correct work costs as much as passing wrong work (C-53). |
| D-R15 | 2026-08-27 | Both mutation harnesses converted to **byte I/O** mid-batch | The Inc-3 counterfactual failed its own restore assertion: text-mode round-trip rewrites line endings, and `.dev-flow/state.json` is LF while `mapper/store.py` is CRLF. A sha256-verified restore only proves what the harness actually wrote. Inc-1's battery was re-run under byte I/O and reproduced all 19 verdicts identically. |
| D-R16 | 2026-08-27 | A correction note in the map may **describe** a superseded claim but must not **spell it verbatim** | My first `search` correction note quoted the old signature and reddened its own regression pin: a scanner cannot tell a token being reported from one being declared. C-56, and its own remedy applied. Recorded in the test file so the next amender does not rediscover it. |
