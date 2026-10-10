# Requirements ledger — mapper — Batch 2026-10-10-perf-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._

---

### LED-2026-10-10-perf-batch.1 — initial contract authored at P1

- **Requirement:** HLR-PERF.1, HLR-PERF.2, HLR-PERF.3, LLR-PERF.1.1, LLR-PERF.1.2, LLR-PERF.1.3, LLR-PERF.2.1, LLR-PERF.2.2, LLR-PERF.2.3, LLR-PERF.3.1, LLR-PERF.3.2
- **Date:** 2026-10-10
- **What changed:** initial authoring of the live contract at P1 (ARQ design + requirements unit PERFARQ, worker Kimi). Establishes the three-lane fork (R: canvas/layered span-clip + layout memo; M: private adjacency cache with `(id(edges), len(edges))` token + linear `mermaid.dump`; S: one paid render at mount with the settle pass preserved), the PERF namespacing, the AT-075…AT-077b assignment (next free after the verified maximum AT-074), the counted-operations oracle regime (no wall-clock assertions in the suite; P4 median-of-3 evidence), and the ⏸ DEFER record for the S-18 work budget and the single-visit DAG layout.
- **Why:** the batch's objective (B-33 follow-up, operator ruling 2026-10-09/10) is behaviour-preserving perf only; every threshold is indexed to the P0 baseline measurements (`spike/perf-baseline.md` §1–§7), and the byte-identity oracle (AT-065 parity goldens + `test_repair_golden_census.py`) is pinned untouched.
- **Raised by:** unit PERFARQ (orchestrator-ruled scope; PLAN.md §Triggers A1·A2·A3·A4·B1·B3·E1·F1).
- **Evidence:** premises 1–7 in `01-requirements.md` §2.7 (each with executed code/measurement evidence, including the edge-mutation census and the AT-number grep); design `design/design-proposal.md` §4 (frozen interfaces) and §8 (disjoint file sets, intersection test executed: `R∩M = R∩S = M∩S = ∅`).
