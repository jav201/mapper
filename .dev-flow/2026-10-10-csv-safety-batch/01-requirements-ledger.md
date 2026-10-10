# Requirements ledger — mapper — Batch 2026-10-10-csv-safety-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._

### LED-2026-10-10-csv-safety-batch.1 — P0/P1: initial contract authored from B-114 evidence and the orchestrator's design decisions
- **Requirement:** HLR-CSV.1, HLR-CSV.2, HLR-CSV.3, LLR-CSV.1.1, LLR-CSV.1.2, LLR-CSV.2.1, LLR-CSV.2.2, LLR-CSV.3.1
- **Date:** 2026-10-10
- **What changed:** the live contract was authored at batch open (P1). Scope fixed by the orchestrator's pre-authorised decisions: D1 — the store refuses what its loader refuses (`MapStore.save` raises `MapStoreError` before any byte, riding the existing `_save_or_toast` surface, no new UI); D2 — the preview's existing "could not draw the preview" panel paints an exact, stated sentence naming the colliding rows (original ids + 1-based line numbers) instead of drawing a graph the save will refuse; D3 — `preview_csv` records which original rows collapsed into which slug. The silently-disambiguate-ids alternative (`a-b`, `a-b-2`) was rejected: it changes the user's data without telling them and makes `parent` references ambiguous. AT numbers AT-072…AT-074 continue from the measured highest existing number AT-071 (`grep -rohE 'AT-0[0-9]+' tests/ REQUIREMENTS.md | sort -u | tail -3`).
- **Why:** defect B-114 measured on `origin/feat/perf-batch` (evidence `perf0b-slug-reach.transcript`: `small_save_error: null`, `small_load_error: MapStoreError ... (ParseError)` for ids `a-b`/`A B`) — the save leg lacked the loader's multiple-parent refusal (`mapper/mermaid.py:85`), which the cycle half already had (LLR-R01.5). The cycle evidence in the preview comment (`mapper/screens/import_preview.py:60-62`) confirmed a cyclic `parent` column reaches the preview without passing `mermaid.parse`; `MapStore.save`'s existing cycle guard covers that leg.
- **Evidence:** `.dev-flow/BACKLOG.md` B-114; `git show origin/feat/perf-batch:.dev-flow/2026-10-10-perf-batch/evidence/perf0b-slug-small.csv` and `.../perf0b-slug-reach.transcript`; `sed -n '60,130p' mapper/mermaid.py`; `sed -n '810,870p' mapper/store.py`; `sed -n '217,260p' mapper/screens/common.py`; the AT-number grep above.
