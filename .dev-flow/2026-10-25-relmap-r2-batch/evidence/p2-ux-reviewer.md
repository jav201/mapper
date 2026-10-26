# Phase-2 cross-review evidence — UX-REVIEWER

- **Batch:** `2026-10-25-relmap-r2-batch` · **Branch:** `feat/relmap-r2` · **Date:** 2026-10-25
- **Lens:** UX fidelity (non-overlapping) · **Artifacts reviewed:** `01-requirements.md` (full),
  `01b-acceptance-design.md` (full), `01-requirements-ledger.md` (full), PLAN references in-contract,
  the round-2026-10-23 prototype verdict (`verdict-2026-10-24.json` + `PROTOTYPE.md`, read-only).
- **Verdict:** `iterate-to-refine`

## Findings

| ID | Severity | file:line | What | Recommendation |
|---|---|---|---|---|
| F-UX-1 | MAJOR | `01-requirements.md:535`, `:755`, `:962`; `01-requirements-ledger.md:1-11` | By-kind toggle still written as CONTINGENT. The binding orchestrator ruling (by-kind toggle SHIPS: LLR-RVG.1.5 + `k` key) is not reflected: LLR-RVG.1.5 header says "drafted for the design review to rule in or out", LLR-RVH.4.1 binds `k` "ONLY IF the PDR ships LLR-RVG.1.5", §6.3 open risk repeats the contingency, and the ledger — the designated home for rulings — is empty. A Phase-3 implementer reading only the contract could lawfully drop the toggle, the `k` binding and AT-136. | Append a ledger ruling entry and de-contingent the three sites: LLR-RVG.1.5 statement/validation, the LLR-RVH.4.1 conditional clause, the §6.3 open risk. |
| F-UX-2 | MINOR | `01-requirements.md:608` vs `:523` | Tone drift risk: the ruling recorded at :523 says "WARN reserved to the matrix lens reach gauge", but LLR-RVS.2.3 paints the sheet's `◐` (tagged binds) in WARN — a WARN usage outside the lens gauge. If the ruling means severity words only, the wording at :523 overstates it; if it is literal, the sheet glyph tone conflicts. | PDR to disambiguate the ruling's scope in one clause; adjust either :523's parenthetical or LLR-RVS.2.3's tone so the two read consistently. |

No BLOCKERs. All other focus areas pass (see Evidence).

## Evidence

### 1. Prototype-verdict fidelity — PASS (except F-UX-1)
Compared against `verdict-2026-10-24.json` (`d_matriz_lente=matrix-panel`,
`d_matriz_celda=binds-glyphs`, `d_gaps=gaps-ranked`, `d_ficha=sheet-direct`) and PROTOTYPE.md §D rows.
- **Matrix = matrix-panel + side lens:** grid HLR-RVM.1 (`01-requirements.md:277-282`) and separate
  two-hop lens panel HLR-RVM.2 (`:284-289`, hop markers `↑1/↓1/↑2/↓2`, `change <id> reaches N nodes`,
  WARN reach gauge, `not computed` for None) match the PROTOTYPE.md §D-matriz row verbatim-cited at
  `:288`. Binds-glyphs cells per LLR-RVM.1.2 (`:431-437`, `●`/`◐`, `▪` diagonal, `·` empty, `○` gutter
  badge) match the verdict; letters variant explicitly rejected (M-RVM-2). Legend re-cased Darkside.
- **Gaps = gaps-ranked + count column + Darkside casing:** HLR-RVG.1 (`:305-310`) renders rank order
  from `rank_gaps` with "reach as a plain count"; LLR-RVG.1.3 (`:519-525`) pins the zero-padded
  three-digit count as "the only reach visual" (microbar rejected, matching PROTOTYPE.md §D-gaps);
  cursor on worst gap; severity chips. Casing per HLR-RVG.2 (`:312-317`) and LLR-RVG.2.1/.2.2
  (`:543-557`), matching the operator note at PROTOTYPE.md:175-176.
- **Sheet = sheet-direct + `c` full chain:** HLR-RVS.3 (`:340-345`) and LLR-RVS.3.1/.3.2/.3.3
  (`:623-645`): hop-1 direct neighbours default, declared `+NN more … — c shows the chain` cut,
  `c` toggles to stacked full chain with `↑N`/`↓N` minimum-hop markers, declared in crumb + `next ▸`
  note. Matches `d_ficha=sheet-direct` and the §D-ficha row.
- **Ruling incorporations:** glyph table ✓/●/◐/•/≡ at `:435`; MED→INK with WARN reserved to the lens
  gauge at `:523` (but see F-UX-2); `escape` quiet leave alias at `:390`, `:752`; by-kind toggle NOT
  de-contingented (F-UX-1).

### 2. Keys through the keymap single seat — PASS
`mapper/keymap.py` exists on disk (23.7 KB). Every new key is routed through the seat LLR-RVH.4.1
(`01-requirements.md:751-757`): `1`/`2`/`3`, cursor keys, `enter`, `c`, `r`, `q`, `escape` alias,
and `k` (contingent — F-UX-1). No chord bound twice (M-RVH-9). LLR-RVH.4.2 (`:759-765`) requires
`BINDINGS = screen_bindings(SCOPE_RELMAP)` and keybar from `keybar_groups(SCOPE_RELMAP)`;
M-RVH-10 declares any hand-written screen binding RED — the no-hard-coding control exists and is test-asserted.
AT-148 drives all of `1`/`2`/`3`/`r`/`escape`/`q` as real keys (`01b-acceptance-design.md:211-221`).

### 3. Help/palette entries — PASS
LLR-RVH.4.4 (`01-requirements.md:775-781`) is a mandatory `shall`: help overlay renders
`SCOPE_RELMAP` entries and the palette offers relmap actions, "both derived from the seat with no
hand-written entries". AT-149 (`01b-acceptance-design.md:223-232`) asserts seat-equality (not
superset) for help and palette with a real `?` / `ctrl+p` pilot and a negative arm (M-RVH-12)
for any hand-added row. MAP-TYPES §6.2 cited. Nothing left optional.

### 4. Widths: 118 reference / 87 checked — PASS
Both widths are pinned wherever it matters: contract LLR-RVM.4.1 (`01-requirements.md:487-493`,
"118×34 reference and the 87×34 check", zero unexplained clip/overprint, negative M-RVM-10),
LLR-RVG.1.4 (`:527-533`, dedicated sweep `tests/test_relmap_scalecheck.py` at both sizes),
LLR-RVS.6.1 (`:663-669`, fit + audit-clean at both sizes), HLR-RVS.6 (`:361-366`). AT side:
shared driver sizes (`01b-acceptance-design.md:20-21`); matrix 87-col arms AT-130 `:35` and
AT-131 `:45-46` (summary cut inside the lens panel — the exact 87-col fight named in the review
brief); gaps sweep AT-137 `:102-109` (cursor-to-last-row at 87×34, width ladder, WHAT drop-whole);
sheet AT-143 `:164-169`; shell AT-148 `:216-220` (87×34 keybar/crumb C10 arm).

### 5. Darkside casing, no Solari ALL-CAPS — PASS
HLR-RVG.2 (`01-requirements.md:312-317`) bans Solari ALL-CAPS catalogue-side; LLR-RVG.2.1
(`:543-549`) pins a case-only lowercase transform with a rendered-string + AST census (derived set,
C-31) and negative M-RVG-8 (`.upper()` or any caps literal → RED); LLR-RVG.2.2 (`:551-557`) covers
all chrome; LLR-RVS.1.2 (`:583-589`) covers sheet edge-type/gap-kind labels with fixed copy authored
lowercase; LLR-RVH.1.2 (`:695-701`) pins the `relation·reqharness` badge casing with M-RVH-2.
AT-135 asserts `hlr without llr` on the real screen (`01b-acceptance-design.md:86`). Grep of the
contract finds no requirement mandating ALL-CAPS anywhere; the only caps strings are quoted
prototype evidence explicitly marked as rejected/not-portable.

## Notes
- Ledger being empty at Phase 2 is expected for a fresh batch, but the by-kind ruling predates this
  review and belongs there — F-UX-1 is the single gate for flipping this review to `approve`.
- Reviewed contract as of worktree state 2026-10-25; no files other than this evidence file were touched.
