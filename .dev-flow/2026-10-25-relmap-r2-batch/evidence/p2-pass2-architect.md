# P2 second pass — ARCHITECT lens

- **Role:** architect reviewer (independent second pass; authored none of the artifacts)
- **Pass:** P2 pass 2 (re-review of the P1 amendment, commit daddd6d, after first-pass
  `iterate-to-refine`)
- **Date:** 2026-10-25 · **Batch:** `2026-10-25-relmap-r2-batch`
- **Inputs read:** `02-review.md` (findings ARC-01…06 + author dispositions),
  `evidence/p2-architect.md` (first-pass evidence), amendment diff `git show daddd6d`,
  amended `01-requirements.md`, `PLAN.md`, `01-requirements-ledger.md`,
  `docs/ARCHITECTURE.md`, `tests/test_relmap_model.py`, `tests/test_relmap_descriptor.py`,
  `tests/test_relmap_audit.py`, `tests/test_inc9c.py`.

## First-pass findings re-verified

| ID | First-pass severity | Disposition claimed | Verdict | Evidence |
|---|---|---|---|---|
| ARC-01 | major | fixed — census re-counted 20 HLR / 52 LLR | **verified** | Own count: `^### HLR-` + `^### LLR-` headings in `01-requirements.md` = 72 total; LLR = 52 by family (RVM 10, RVG 9, RVS 14, RVH 15 incl. new RVH.3.3, RVT 3, RVU 1), so HLR = 20. §5.2 criterion 1 (`01-requirements.md:952`) reads "All 52 LLRs (20 HLRs)". PLAN header (`PLAN.md:22-25`), "Where we are" (`:68-74`), roadmap requirements line (`:107-110`) all state 20/52. Ledger measurement `LED-2026-10-25-r2-census` present (`01-requirements-ledger.md:192`). No stale 26/51/52-mixed claim remains. |
| ARC-02 | major | fixed — `keymap.py` moved into trunk Inc-2 | **verified** | PLAN Inc-2 (`PLAN.md:115`) = `screens/relmap/{__init__,screen,base}.py` + `mapper/keymap.py` (**4** ≤ 4); Inc-6 (`:119`) = `home.py` + `app.py` (**2**). No other increment row claims `keymap.py` or the `SCOPE_RELMAP` seat (Inc-6b takes help/palette *entries from* the seat, owns help/palette files only). ARCHITECTURE §4 KEYMAP row (`docs/ARCHITECTURE.md:267`): "NO — lands whole in trunk Inc-2 … Inc-6 keeps `home.py` + `app.py` only." Fork coherence: `SCOPE_RELMAP` is created and `BINDINGS` generated in the same trunk Inc-2 (`01-requirements.md:780-797`), before any lane forks, so F-2/F-3 hold; F-3 text amended (`01-requirements.md:272` — "the keymap seat scope is TRUNK-owned (Inc-2…)"). ARCHITECTURE §6 worksheet Inc-2/Inc-6 rows amended (`docs/ARCHITECTURE.md:344,348`); intersections (`:352-354`) still empty. |
| ARC-03 | minor | fixed — `test_inc9c.py` named in Inc-6 census; bogus glob gone | **verified** | Inc-6 test ledger names "`test_inc9c.py` (LEAK_EXCEPTIONS line-pin re-pin)" (`PLAN.md:119`). ARCHITECTURE §6 reverse census (`docs/ARCHITECTURE.md:358-362`): the `test_home*.py` glob is corrected ("matched no file; corrected at the P1 return edge, ARC-03") and "`tests/test_inc9c.py` carries the `LEAK_EXCEPTIONS` line-pin `("mapper/screens/home.py", 176, "str(exc)")` which Inc-6 re-pins in the same increment". Pin verified on disk: `tests/test_inc9c.py:270-275`. |
| ARC-04 | minor | fixed — three re-pointed files enumerated; M-RVT-2 reworded | **verified** | PLAN Inc-1 (`PLAN.md:114`) enumerates `tests/test_relmap_model.py:17-26`, `tests/test_relmap_descriptor.py:38`, `tests/test_relmap_audit.py:33-35`. Disk matches: `test_relmap_model.py:17-27` imports `cut`+`DISPLAY_MAX` from `relmap.model`; `test_relmap_descriptor.py:38` imports `refusal_line`; `test_relmap_audit.py:33-35` imports `HEADER`/`format_structure` and `refusal_line` (from `descriptor`, `:34`). M-RVT-2 (`01-requirements.md:844`) now reads "one test still imports `refusal_line` from `mapper.relmap.audit` (the live old path the census names is `mapper.relmap.descriptor`…)" — the live old path. Note: the first-pass parenthetical that `test_relmap_audit.py` also imports `cut` from `model` is not accurate today (no `cut` import in that file); the enumerated line range itself is correct, so the fix stands. |
| ARC-05 | minor | fixed — shared-fixture policy declared | **verified** | PLAN `PLAN.md:127-130`: "renderer lanes build their synthetic `build_map` maps INLINE per test file (R1 style); shared fixture modules (`tests/_relmap_fixtures.py`) are trunk-only — two lanes never append to one shared fixture file, so the crossed reverse census cannot be silently violated." |
| ARC-06 | minor | fixed — `RelMapScreen` in app row EXPOSES | **verified** | `docs/ARCHITECTURE.md:166` app-row EXPOSES now ends "`ReviewScreen` *(target: `RelMapScreen` — the R2 re-export, the `MapScreen` pattern)*", matching the commitment convention used elsewhere in the map (e.g. the §3 `app` row `:194`). |

## Task 2 — amendment sweep (architect lens)

- **Lane file sets pairwise disjoint after the keymap move:** verified — Inc-1
  {relmap/text,model,descriptor,audit} ∩ Inc-2 {screens/relmap ×3, keymap} ∩ lanes 3-5
  {matrix|gaps|sheet} ∩ Inc-6 {home, app} ∩ 6b {help, palette} ∩ 7 {reqharness/audit.py}
  all empty (`PLAN.md:114-121`, `docs/ARCHITECTURE.md:343-350`); the two `audit.py` paths
  (`relmap/` vs `reqharness/`) are distinct modules. Test files: `test_keymap.py` claimed
  only by Inc-2 now; `test_relmap_shell.py` shared only by sequential increments
  (Inc-2 → Inc-6/6b), as before.
- **Fork preconditions F-1…F-5 as amended:** F-1 unchanged; F-2 intact (PDR seal before
  lanes); F-3 amended text coherent with the move; F-4's "home/keymap/help/palette/a3-census
  pins named in §6" matches the amended §6 census; F-5 names the executed injection probe
  and the entry-time re-verification (QA-02's fix) — no contradiction with the architect
  plan.
- **New LLR-RVH.3.3:** properly derived — `Traces to: HLR-RVH.3` (`01-requirements.md:774`)
  whose substance is the derive-on-open/no-descriptor derivation (`:387-389`); traced to
  US-RMV-004 through HLR-RVH.3; names validation method, asserting tests
  (`test_relmap_shell.py` + AT-147 arm), executed-probe draft-time verification, two
  negative controls, ledger entry; counted in the 52.
- **Full amendment diff scan** (`git show daddd6d`, all nine files): no new contradiction,
  ambiguity, or broken US→HLR→LLR derivation found. Ruling fold-backs (by-kind SHIPS,
  240 bound, WARN scope, cut-before-coercion, RVS.7.1 re-trace) are internally consistent
  between the contract, PLAN rows, ledger entries, and IFC blocks. The six IFC `FLOW:`
  openers are normalized.

## New findings

None.

## Verdict

`approve` — all six first-pass architect findings verified fixed in the amended contract;
the amendment opens no new defect in the architect lens (lane disjointness, fork
preconditions, and the new LLR's derivation/trace/count all re-verified).
