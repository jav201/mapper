# Whole-branch gate findings — disposition

**Two independent gates ran over the whole branch.**

| Gate | Verdict | Findings |
|---|---|---|
| `security-reviewer` | **CLEARED TO MERGE** | 0 HIGH · 3 MEDIUM · 4 LOW |
| `qa-reviewer` (adversarial) | **BLOCKED** | **1 HIGH** · 5 MEDIUM · 6 LOW |

> **BLUF.** The QA HIGH is correct and is the batch's own defect class recurring one level up: the
> derived census still contained a **hand exclusion**. The security MEDIUMs are also correct, and one
> of them found a **false premise in a comment I wrote** — the third time this batch has produced
> that specific defect. All substantive findings are fixed and gated; the merge is **held for the
> operator** because a HIGH was raised.

---

## HIGH-1 — the census was short by four, by the batch's own rule *(FIXED)*

`Document.tags` and `Document.inherited` are `dict[str, str]` (`model.py:82-83`) and `_build_sidecar`
round-trips both verbatim. **`Ficha.fields` is the identical shape and was covered from the start**
as `fields.key`/`fields.value`. The exclusion rested on the reasoning that they *"are dicts by
design"* — which is equally true of `fields`. QA's executed evidence: `tags={"owner": 12345}` loaded
with `tags={'owner': 12345}` and `load_warnings=[]`, reaching `factory.py:339`
(`sorted(set(doc.tags) | ...)`) as `TypeError: '<' not supported between 'int' and 'str'`.

**`HLR-STO.1` as written was not met.** The census is **21**, not 17.

**Fix.** `_str_map_fields(cls)` derives `dict[str, str]` fields from the annotations, and
`_coerce_str_map` runs the same ladder, same sink and same collision handling on both sides. The
test census derives the four new positions the same way, and **`_KEY_POSITIONS` is now derived too**
— hand-listing it was survivable at two entries; at four it would have silently omitted the new pair,
which is HIGH-1 one level down. Gated by `Q-high1`: **8 arms**.

## F1 / F3 — threshold 3 was unmet, with a fully green suite *(FIXED)*

Two classes still escaped `load`:
- `read_text` sat **outside every net** → invalid UTF-8 in either file raised a bare
  `UnicodeDecodeError`; an `OSError` carried its **full absolute path, username included**, into the
  operator-facing sink (F3).
- The parser net caught `(yaml.YAMLError, ValueError)` but not `RecursionError` → a **4 KB** sidecar
  nested ~2000 deep exhausted the stack inside `safe_load`.

The reviewer's framing is the one that matters: *"threshold 3 is an acceptance criterion, the tests
pass, and the criterion is not met as written."* 104 tests and 19 mutants did not assert the thing
the requirement says.

**Fix.** Reads pulled inside a net raising `MapStoreError(f"...: {type(exc).__name__}")`; parser net
widened to `RecursionError`. Gated by `Q-f1a` (2 arms) and `Q-f1b` (1 arm), driven by **bytes**,
because the defect is in decoding and a `str` fixture cannot reach it. The new arms also assert the
workspace path never appears in the message, closing F3.

## F2 — a false premise in a comment I wrote *(FIXED)*

The net's comment asserted *"Every caller in the product catches `MapStoreError`."* Executed:
`grep -rn "except MapStoreError" mapper/` outside `store.py` returns **nothing**; both real callers
catch bare `Exception`. So the nets change the **message**, not crash-resistance — a genuine UX win,
but a much smaller claim than the one recorded.

**This is the third instance of this defect in this batch** (F4's phantom-node claim, the map's own
correction notes, now this). The comment now states what is true, and the masked type is carried in
the message because `mapper/` has **zero** `logging.` call sites and both sinks render `str(e)` only
— without it a genuine code defect is permanently indistinguishable from a malformed file.

## MEDIUM-4 — G4's second limb never landed *(FIXED)*

`store.py` still had the bare `_coerce_field(graph, "node", "id", ...)` while the sibling site was
indexed. Two distinct refused ids emitted two byte-identical records. Gated by `Q-med4`.

## F7 — a security control no test would notice the removal of *(FIXED)*

Deleting the `isinstance(sidecar, dict)` guard left **all arms green**, because the generic net
catches the resulting `AttributeError` and re-raises the same *type*. A broad net making a specific
control untestable. The guard raises **without** `from` and every net arm raises `from exc`, so
`__cause__ is None` distinguishes them exactly. Gated by `Q-f7`.

---

## Carried, not fixed — with the reason

| # | Finding | Why carried |
|---|---|---|
| MEDIUM-1 | `_CORRECTED_FALSEHOODS` holds 5 entries while two prose sites say six | Documentation-count defect. **Recorded as a carry rather than papered over**: the sixth falsehood (`SearchIndex.query`'s consumer) genuinely lacks an arm. |
| MEDIUM-2 | `TC-P02`/`P03`/`P04` have **zero on-disk nodes** — comment banners only | Real traceability gap. The `AT-` chain is complete and clean (QA verified one distinct driving node each, no orphans); the `TC-` layer is the one that is nominal. |
| MEDIUM-3 | Three phantom node citations, one inside F4's own disposition row | Evidence-hygiene defect, C-56's family. |
| MEDIUM-5 | Commit `8675151` carries 13.3k undeclared lines of the **feature** batch's PDR artifacts, and `state.json` never mentions this batch | **Pre-existing on the branch before this session** and the most consequential carry: on merge, master's state pointer names a rejected, parked batch with a stale `tests_collected: 429`. Fixing it is a `state.json` rewrite that belongs to the batch close, not to an increment. |
| F4 (sec) | Warning amplification — `load_warnings` is unbounded | A million malformed entries produce a million strings. Local-file TUI; the reviewer rated it MEDIUM and noted the fix changes a record format **18 tests pin**. |
| F5, F6 (sec) | `_mappings` rationale does not reproduce at the stated base; two map citations imprecise | Documentation accuracy. |
| LOW ×6 | Stale 66-vs-70 counts; no `campo ilegible` negative control **in this batch's file**; ungated silent default for missing attachment `kind`/`path`; `M-STO-a` measured 21 vs claimed 20; `M-RR2` naming collision; a self-quotation appearing nowhere | Each real, none affecting behaviour. The missing negative control is the notable one: a mutant emitting `campo ilegible` unconditionally survives all this file's arms — the 32 red arms are in **other** batches' files, the same cross-file dependency C2 fixed for the owner coordinate. |

---

## What the gates settled that the batch had left open

- **The slow-lane flake predates `d877784` — CONFIRMED.** The batch recorded this as UNVERIFIED,
  correctly. QA checked it in a worktree at the base ref: 6/6 clean unloaded, clean under two
  concurrent runs, and under 16 CPU-load processes it **failed `test_at_r16b…composed`** — the exact
  node this batch named, with **zero branch code present**. The observation is upgraded from
  unverified to measured, and the attribution to pre-existing code is now evidenced rather than argued.
- **The pre-fix measurement reproduces.** The unmodified boundary file against base: **43 failed / 27
  passed**, with `test_at_p01` red on exactly **12 of 17** and `test_at_p03` red on exactly **4** —
  independently confirming the figures this batch's requirements were derived from.
- **Every number reconciles.** Fast/slow/collect/ledger/ruff all re-derived by QA with no numeric
  finding, and the perf fixture reproduced at 2.3187s against the packet's 2.3066s.
- **The operator rider is honoured.** No budget, deadline or abort anywhere in the diff; `elapsed`
  appears only inside `print()`.

## Post-fix state

| Measure | Value |
|---|---|
| fast lane | **531 passed, 17 deselected**, exit 0 |
| slow lane | **17 passed, 531 deselected**, exit 0 |
| collected | **548** = 429 base + 119 |
| ruff | **29** whole-tree (= base); clean on all five touched files |
| mutation battery | **24 mutants, every one reddening a named arm** |

**The merge is held.** A HIGH was raised; under the standing authorization that returns to the
operator rather than being self-cleared, even though the HIGH is fixed and gated. Neither reviewer
has seen the post-fix tree.
