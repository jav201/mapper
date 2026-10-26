# Design proposal — mapper — Batch 2026-10-25-relmap-r2-batch

> **Artifact language.** Canonical **English scaffold**; generate in the batch's language.
> The normative rules below are language-independent. **Where that language is declared:**
> `state.json`'s `language` key in `core` and `full`.

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Design proposal` · `7 · Forward-applicability table` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.

> **Owed in.** `core` by trigger · `full` ✓ (PDR stands: trigger A1 fired).

> **Where this lives.** The R1 batch kept its proposal and PDR record under `.dev-flow/<batch>/design/`;
> this batch does the same, and cites decisions by id (by decision number). What binds code also lands
> in the requirement (`01-requirements.md`, AT bodies in `01b-acceptance-design.md`) or in
> `docs/ARCHITECTURE.md`.

> **The forward-applicability rule (ISO/IEC/IEEE 15288).** Every section below is named as the input of a
> later activity (§7). Status: **drafted 2026-10-25 after the P2 cross-review first pass and the P1
> amendment (census corrected by script to 20 HLR / 52 LLR; by-kind toggle SHIPPED on `k`; hook bound
> ruled at 240; the keymap seat moved into trunk Inc-2; both `assumed` seams discharged by executed
> probes — ledger `LED-2026-10-25-r2.01…11`).** Nothing here relitigates the P1 rulings (PLAN.md:141)
> or the R1 freeze (`PDR-2026-10-25-relmap-r1-batch#D1…D8`).

| Field | Value |
|---|---|
| Id | `PDR-2026-10-25-relmap-r2-batch` |
| Requirements covered | `US-RMV-001…006 · HLR-RVM.1–4, RVG.1–3, RVS.1–6, RVH.1–5, RVT.1, RVU.1 · LLR-RVM.1.1–4.2, RVG.1.1–3.1, RVS.1.1–7.1, RVH.1.1–5.2, RVT.1.1–1.3, RVU.1.1 (52) · AT-130…AT-152 (23) · TC-RM-04…TC-RM-30 (27)` (contract `01-requirements.md`, acceptance design `01b-acceptance-design.md`, ledger `LED-2026-10-25-r2.01…11` + `LED-2026-10-25-r2-census`) |
| Modules touched (from `docs/ARCHITECTURE.md`) | `screens/relmap` (new: screen host + base painters + three renderers) · `relmap` (the `text.py` presentation leaf + three re-points inside the package) · `keymap` (the additive `SCOPE_RELMAP` seat scope) · `screens/home` · `app` (routing + re-export) · `screens/help` · `screens/palette` · `reqharness` (`audit.py` only — the per-line hook bound) |
| Triggers that fired | `A1 · A2 · A3 · A4 · B1 · C6 · C8 · D1 · E1` (PLAN.md:38-56) — A4 fired: this batch forks; B1 fired: reverse census per increment; C6/C8 fired: security lens; D1 fired: `ux-reviewer` owed at the PDR |
| Author / reviewers | `software-dev` (author) · `architect` · `qa-reviewer` · `security-reviewer` (C6/C8 — owed at seal) · `ux-reviewer` (D1 — owed at seal: a whole screen and Home entries are the user-visible surface) |

---

## 1 · Objective and scope

**Objective.** Surface the R1 headless relation-map kind in the Darkside TUI: a read-only relation
screen hosts three ported views through the one `Canvas` adapter with the C10 audit hook — the
traceability matrix with its side-panel impact lens, the ranked gaps view, and the node sheet — and
the shell learns to list and open relation maps. Every layout decision is bound by the operator verdict
of round 2026-10-23 (`verdict-2026-10-24.json`; PLAN.md:20, `01-requirements.md:24-33`), and every
datum comes from the R1-frozen API (`PDR-2026-10-25-relmap-r1-batch#D3`) — R2 changes no name in it.

**Per-view verdict citations.**
- **Matrix** — `matrix-panel` (the band variant rejected: hop 2 lands on ATs, which are not columns)
  with `binds-glyphs` cells (letters rejected: initial collisions read as alphabet soup) —
  `01-requirements.md:147-150`, HLR-RVM.1/.2.
- **Gaps** — `gaps-ranked` (the microbar rejected: it duplicates the count at 8 cells of resolution),
  in Darkside casing, NOT QuickMap's Solari ALL-CAPS (operator note, 2026-10-24) —
  `01-requirements.md:156-162`, HLR-RVG.1/.2.
- **Sheet** — `sheet-direct` (columns rejected: they halve the WHAT column), `c` shows the full chain
  in stacked density — `01-requirements.md:165-173`, HLR-RVS.1–3.

**In scope (design level).** The `mapper/screens/relmap/` package (host, shared painters, three
renderers) and the host↔renderer surface it freezes; the `mapper/relmap/text.py` presentation leaf
(R1 DDR §E 10-11 inherited); the additive `SCOPE_RELMAP` keymap seat scope; the Home listing + kind
badge + open-by-kind routing; help/palette entries derived from the seat; the `--audit` hook per-line
bound of 240 (R1 DDR §E 13, B-147). Scalecheck sweep at the 118-column reference width with the
87-column check (87 checked), colour always on, English UI, Darkside only.

**Explicitly not.** Timeline (C5/R4) · metro (C6/R5) · FTS evidence search (C8/R3) · editing typed
edges (deferred past R5) · the US canon / AT→test table (B-141 — the reqharness map is the honest
HLR/LLR skeleton until it exists) · any `mapper.db` / `store` schema change (R-019) · any change to
the tree kind or to the D3 API · the `repo:` absolute-path line (B-155).

**Mapping chain → increment.** US-RMV-001 → Inc-3 (matrix) · US-RMV-002 → Inc-4 (gaps) ·
US-RMV-003 → Inc-5 (sheet) · US-RMV-004 → Inc-2 (host) + Inc-6 (shell) + 6b (help/palette) ·
US-RMV-005 → Inc-1a + Inc-1b (text leaf) · US-RMV-006 → Inc-7 (hook bound).

## 2 · Modules and boundaries

| Module | What it owns here | What it exposes | What it must NOT reach into |
|---|---|---|---|
| `screens/relmap/screen.py` | `RelMapScreen` — the host: lifecycle, derive-on-open + `r` refresh through the D3 API (R-019 recompute-on-open), view switching on `1`/`2`/`3`, `BINDINGS` generated from the seat, crumb/keybar compose, the refusal notice path | `RelMapScreen` (via the package re-export, the `MapScreen` pattern); the host↔renderer surface (§4, D1) | any WRITE concern (no draft, save, archive, edit); `store` (the D3 API is the one door); `model` (the tree `Graph`); `reqharness`; raw file reads outside `relmap`'s readers; `osopen` launches |
| `screens/relmap/base.py` | the shared Canvas painters every renderer reuses — column cuts, evidence glyphs, the markup-safe label assembly through `darkside._row_text`/`fit` (`plain` + LF/TAB/CR → single space, `mapper/darkside.py:576-621` — the frozen seam per COND-SEC-1; bare `plain` preserves LF/TAB and is NOT the seam) into explicit-style `Text` / `markup=False` (the C8/C-17 sink, one seam for all three renderers) | the painter helpers + the label sink | kind/edge/gap literals (the glyph table arrives §4 D5); any renderer module |
| `screens/relmap/matrix.py` | the traceability-matrix renderer + side-panel impact lens (windowing, cells, rings, summary + reach gauge, neighbourhood dimming, skeleton honesty) | one paint entry over the frozen surface | `gaps.py`, `sheet.py`; anything outside the D3 API + `canvas`/`design`/`darkside` |
| `screens/relmap/gaps.py` | the ranked-gaps renderer (ranked rows, chips, count column, window + cut markers, by-kind grouping on `k`, casing census) | one paint entry over the frozen surface | the other renderers; re-ranking/filtering of the host-supplied rows (LLR-RVG.1.1) |
| `screens/relmap/sheet.py` | the node-sheet renderer (header, FEEDS IT / A CHANGE REACHES, hop-2 cut, `c` chain density, node gaps, counted overflow, read-only census) | one paint entry over the frozen surface | the other renderers; `osopen` (evidence names are labels, LLR-RVS.7.1) |
| `relmap/text.py` (new leaf) | `cut(text) -> str`, `DISPLAY_MAX = 120`, `refusal_line(base_name, cause, limit=None) -> str` — one definition site, one import path | those three names | everything in `mapper` (it is a stdlib-only leaf, ARCHITECTURE `relmap` §3 row) |
| `relmap` (re-points) | `model.py`, `descriptor.py`, `audit.py` import the three names from `text`; the `audit.__all__` re-export of `refusal_line` drops; byte-identical behaviour | unchanged public surface (R1 D1–D5 intact) | no new edges |
| `keymap` | the additive `SCOPE_RELMAP = "relmap"` scope: `1`/`2`/`3` view switch, cursor keys, `enter` lens focus, `c` chain toggle, `k` by-kind toggle (SHIPPED per `LED-2026-10-25-r2.01`), `r` refresh, `q` leave, `escape` quiet-leave alias | the seat rows — BINDINGS, keybar, palette, help all derive from it (LLR-RVH.4.2/.4.4) | any UI type (the seat is data, R-007); no existing `KeyBinding` moves |
| `screens/home.py` + `app.py` | Home enumerates `*.relmap.yml` beside `*.mmd` in one name-sorted list with the `relation·reqharness` kind badge; open routes by descriptor kind; `app` re-exports `RelMapScreen` (the `MapScreen` pattern) | the recents rows; the routed screen | the seat (the scope landed in trunk Inc-2 — ARC-02); write actions on the relation screen |
| `screens/help.py` + `screens/palette.py` | help + palette entries for the relmap scope, derived from the seat with no hand-written rows | seat-derived entries | hand-added rows (equality, not superset — AT-149) |
| `reqharness/audit.py` | the per-line bound on hook lines: after the escape pass, a line longer than 240 is cut at 239 with one ellipsis, never splitting an escape spelling, never re-exposing `verdict: `; the R1 D4 semantics (count 1,000, prefix rewrite, fixed lines, exit code) unchanged | the bounded hook path | any import from `relmap` |

- Boundaries respected as declared in `docs/ARCHITECTURE.md`: **✓** — no boundary moves. The R2 ARQ
  amendment adds the `screens/relmap` package row (`docs/ARCHITECTURE.md:165`), the `screens/relmap`
  dependency row (`:197`: the D3 API read-only + `canvas`/`design`/`keymap`/`widgets`/`screens/common`,
  renderer modules never import each other — the frozen surface is the only crossing), the `text`
  leaf inside the `relmap` row (`:158`, stdlib-only, `model`/`descriptor`/`audit` import back), and
  the new edges `app` → `screens/relmap` + `screens/home.py` → `screens/relmap` (`:194-197`). R-016
  stands: the `relmap` core stays headless — no Textual/Rich/`canvas`/`screens` imports from
  `mapper/relmap/**`.
- View-specific chords outside their home view (COND-UX-1, declared here and in LLR-RVH.4.1):
  `enter` (matrix lens), `c` (sheet density) and `k` (gaps by-kind) are bound scope-static, but
  each is an inert no-op when the active view is not its home view — or at most flashes the crumb
  note — matching the operator-approved static bar; they never act on a non-home view, and no
  lane may improvise richer behaviour (a richer answer is a seat change, trunk-owned).
- Deliberate divergences recorded in the rows: none new in R2. R-018 (views in `screens/relmap/`, not
  inside `relmap/` and not in `views/`) and R-019 (recompute-on-open, no `mapper.db` change) are the
  governing rulings, both cited in `docs/ARCHITECTURE.md:321-322`.

### 2.1 Per-increment file sets (SOURCE ≤ 4 each; tests uncapped)

| Inc | Lane | SOURCE files | New tests / fixtures | Same-landing edits (not source) | Exit checks |
|---|---|---|---|---|---|
| 1a · text leaf (first half) | trunk (first) | `mapper/relmap/text.py` (new); `mapper/relmap/model.py`, `mapper/relmap/descriptor.py`, `mapper/relmap/audit.py` re-point (**4**) | `tests/test_relmap_text.py` (new) + the re-pointed R1 files enumerated — `tests/test_relmap_model.py:17-26`, `tests/test_relmap_descriptor.py:38`, `tests/test_relmap_audit.py:33-35` | none | byte-identity probe before/after; the `audit.__all__` re-export of `refusal_line` drops HERE; reader census over the re-pointed paths (`relmap.model.DISPLAY_MAX`, `relmap.descriptor.refusal_line`, `relmap.audit.refusal_line`) zero in this increment — the one remaining old-path reader, `mapper/relmap/adapter.py:29` (`cut`), is re-pointed in Inc-1b, declared |
| 1b · text leaf (second half) | trunk | `mapper/relmap/adapter.py` re-point (**1**) | none new — `tests/test_relmap_text.py` re-run + the R1 suite re-counted | none | byte-identity probe before/after; reader census over `relmap.model.cut` zero in this increment; R1 suite green; AT-150/151 |
| 2 · screen host | trunk | `mapper/screens/relmap/__init__.py`, `mapper/screens/relmap/screen.py`, `mapper/screens/relmap/base.py`, `mapper/keymap.py` (**4**) | `tests/test_relmap_shell.py` (host arms), `tests/test_keymap.py` (EXISTING — R1 US-N03 universal, extended) + `tests/test_key_dispatch.py` (the whole-seat pin, re-run) | the `docs/ARCHITECTURE.md` `screens/relmap` rows become facts (paths land) | the host↔renderer surface is frozen HERE (this PDR seals it); the AT-driver fixture-workspace injection verified HERE (probe PASS 2026-10-25, `evidence/p2-seam-at-driver.md`); seat conformance (uniqueness, BINDINGS == seat); the out-of-view inert arms (`enter`/`c`/`k` off their home view — COND-UX-1); AT-148 host arms |
| 3 · matrix | L1 ∥ L2 ∥ L3 ∥ shell | `mapper/screens/relmap/matrix.py` (**1**) | `tests/test_relmap_matrix.py` | none | geometry + windowing over synthetic `build_map` maps; C10 sweep 118/87; AT-130…134, TC-RM-04…09 |
| 4 · gaps | L1 ∥ L2 ∥ L3 ∥ shell | `mapper/screens/relmap/gaps.py` (**1**) | `tests/test_relmap_gaps_view.py`, `tests/test_relmap_scalecheck.py` (the sweep) | none | ranking rendered unchanged; casing census; audit-clean sweep; AT-135…139, TC-RM-10…14 |
| 5 · sheet | L1 ∥ L2 ∥ L3 ∥ shell | `mapper/screens/relmap/sheet.py` (**1**) | `tests/test_relmap_sheet.py` | none | row oracles vs `up`/`down`/`neighbourhood`; `c` toggle; hostile sink arm; AT-140…144, TC-RM-15…20 |
| 6 · shell | L1 ∥ L2 ∥ L3 ∥ shell | `mapper/screens/home.py`, `mapper/app.py` (**2**) | `tests/test_relmap_shell.py` (shell arms) | re-pin the `test_inc9c.py` `LEAK_EXCEPTIONS` line-pin `("mapper/screens/home.py", 176, "str(exc)")` in the same increment | home enumeration + badge census; routing pilot; AT-145…147 |
| 6b · help/palette | with/after shell | `mapper/screens/help.py`, `mapper/screens/palette.py` (**2**) | `tests/test_relmap_shell.py` (help/palette arms) | none | help == seat and palette == seat (equality); AT-149 |
| 7 · hook bound | any boundary | `mapper/reqharness/audit.py` (**1**) | `tests/test_hook_line_bound.py` (new) | none | the bound applied after escaping; D4 arms green (the R1 suite); AT-152 |

Every increment runs only its targeted tests (`env -u NO_COLOR -u TERM`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONIOENCODING=utf-8`, `PYTHONPATH=<worktree>`, `mapper.__file__` probed inside the worktree) plus
the guard set `tests/test_fold.py` + `tests/test_repair_artifact_claims.py` (C-1); the orchestrator
schedules the one full run. Lane fixture policy (P1 amendment, ARC-05): renderer lanes build their
synthetic `build_map` maps INLINE per test file (R1 style); shared fixture modules
(`tests/_relmap_fixtures.py`) are trunk-only — two lanes never append to one shared fixture file, so
the crossed reverse census cannot be silently violated (PLAN.md:127-130).

**Fork preconditions F-1…F-5** (quoted from `01-requirements.md:270-274`; each lane's gate re-reads
them): **F-1** the trunk's text-leaf increment has landed and the R1 suite is green (checked at the
Inc-2 gate entry) · **F-2** the trunk's screen-host increment has landed AND the PDR has SEALED the
host↔renderer surface (checked at each lane's entry) · **F-3** lane file sets are disjoint — each
renderer owns exactly its file, the shell owns home/app (+6b help/palette), the keymap seat scope is
TRUNK-owned (Inc-2, `LED-2026-10-25-r2.08`), RVU owns `reqharness/audit.py`; a lane needing a host
change STOPS and re-cuts · **F-4** the reverse census for each lane's touched symbols runs in the
lane's first increment (B1 census table per lane) · **F-5** the join — every lane's ATs run on the
joined tree before the DDR; the AT-driver seams exist on trunk, probed PASS 2026-10-25
(`evidence/p2-seam-at-driver.md`, `LED-2026-10-25-r2.07`).

## 3 · Diagrams

**Structure (import order — the only crossings are the frozen surface and the declared edges).**

```
relmap (D3 API, frozen R1 — read-only) ◄──────────── screens/relmap (screen.py host + base.py painters)
darkside / design / canvas / widgets / keymap ◄────── screens/relmap (the same surface screens/map has)
keymap (SCOPE_RELMAP seat, data only) ◄────────────── screen.py (BINDINGS) · keybar · palette · help
mapper/relmap/text.py (stdlib-only leaf) ◄─────────── model.py · descriptor.py · audit.py · adapter.py · the R2 renderers' value cuts
app ─► screens/relmap (re-export) · screens/home.py ─► screens/relmap (sibling-open, the MapScreen pattern)
reqharness/audit.py ── per-line cut at the sink ──► stdout (D4 semantics unchanged)
the three renderers NEVER import each other — the host↔renderer surface (D1) is the only crossing
```

**Interaction — open a relation map from Home (the AT-driver path).**

```
MapperApp(workspace=<fixture dir>)            (mapper/app.py:250; MapStore(workspace) at :256)
   └─ run_test() pilot ──► HomeScreen
        Home recents: sorted(glob("*.mmd")) + sorted(glob("*.relmap.yml")) (+ derived row at zero descriptors)
        enter on a relation row ──► RelMapScreen(descriptor | derived entry)
             derive_reqharness_map(Path(workspace)/canon, descriptor)   (workspace-as-repo, LED-2026-10-25-r2.03)
             CanonUnavailable / DescriptorError ──► fixed refusal_line ──► app alive (K1–K17 closed set)
             1/2/3 swap renderer over the frozen surface; r re-derives; q / escape leave quietly
r-renderers: each builds Canvas rows(w, h) with the C10 audit mapping injected; zero unexplained clip/overprint
```

**Algorithm — matrix windowing and the lens.** Rows window to keep the selection visible (centred
where the ends allow), every undisplayed row/column declared in words (`NN–NN / N`, `NN out of view`);
the lens rings list `up`/`down` members once, in edge input order, `↑1`/`↑2`/`↓1`/`↓2` markers, hop 2
only through a drawn hop-1 member of the same direction; the summary takes `reach` (`None` →
`not computed` in WARN, never a fabricated number); neighbourhood dimming calls
`RelMap.neighbourhood(selection, 2)` for the focused node only (LLR-RVM.2.3).

**Algorithm — the declared cuts.** The gaps window follows the cursor with `+NN above` / `+NN more`
markers and drops the WHAT column whole below its 12-cell minimum; the sheet declares hop-2 counts as
`╌╌ +NN more upstream/downstream at hop 2 — c shows the chain` (zero-padded, omitted at zero, counted
via `neighbourhood(focused, 2) − neighbourhood(focused, 1)` filtered per direction); stacked density
lists every distinct node by minimum hop (`↑N`/`↓N`), unbounded in depth with the counted
`… +NN more` line as the safety valve.

**Resource.** The only very-large-map arm is the cap-scale arm of AT-137: a 100,000-node map at the
shipped `MAX_NODES` cap (`mapper/osopen.py:93-94`, `LED-2026-10-25-r2.09`). The windowing LLRs bound
per-render work by construction — there is no per-row `neighbourhood` call (M-RVM-6), no unwindowed
row set (M-RVM-1), no silent overflow (M-RVS-12) — and the open/`r` derivation gets a generous
wall-clock budget of 10× the 303-node skeleton baseline, recorded at Phase 3. No other AT exercises
maps past the 303-node live skeleton class (`01-requirements.md:129-132`).

## 4 · Interfaces that change — and which ones FREEZE

| Interface | Current | After | Consumers | **Frozen for the fork?** |
|---|---|---|---|---|
| **The host↔renderer surface** — `RelMapScreen` (host) ↔ the three view renderers: the focused state the renderers receive (the derived `RelMap`, the focus/selection, the viewport `(w, h)`, the lens target, the cursor row, the host-supplied gap rows, the host-owned key/crumb slots) and the one paint entry each renderer exposes; renderers never import each other (ARCHITECTURE §4 planned-freeze row, `docs/ARCHITECTURE.md:266`; LLR-RVH.4.3). **COND-ARCH-1 (amended at the seal): the surface names the one toggle-state channel for renderer-owned `c`/`k` state — a frozen renderer state-query/toggle entry `toggle(kind: str) -> str` on each renderer (the renderer owns its density/grouping/lens state per LLR-RVS.3.3/RVG.1.5; the entry flips it and returns the state word for the host's crumb/note slot); the host's `action_*` handlers call the ACTIVE renderer's entry and repaint — one mechanism, the same for all three lanes**; **amended at the trunk Inc-2 review pass (orchestrator ruling, `LED-2026-10-25-r2.18`, lanes not yet forked): the renderer protocol gains `row_count(state) -> int` — each view's own cursor axis (ranked-gap rows for gaps, the node list for matrix/sheet), `0` for the placeholder; the host keeps ONE CURSOR PER VIEW, moves it within `[0, row_count)` clamped at the ends (no wrap), and passes the active view's cursor in `ViewState.cursor`; the toggle-state word is stored per view so the crumb shows the active view's own word (switching never shows another view's word; returning restores it); the vestigial `lens` field drops — the matrix lens rides the `enter` toggle channel; the freeze text names the full kind vocabulary (`enter`/`c`/`k`, the matrix word `panel lens`) and the renderer's `notice` obligation** | none — the package does not exist; the surface is an ARQ commitment | NEW, lands in trunk Inc-2 | the three renderer lanes, the shell lane, every view AT (AT-130…144 open through the host) | **FREEZE (D1)** — sealed at this PDR; fork precondition F-2 |
| `relmap/text.py`: `cut(text: str) -> str`, `DISPLAY_MAX = 120`, `refusal_line(base_name: str, cause: str, limit: int \| None = None) -> str` — one definition site, one import path (the `audit.__all__` re-export drops). **COND-ARCH-2/COND-QA-1 + the orchestrator ruling at the seal: the re-point set names the fourth live consumer `mapper/relmap/adapter.py:29` (imports `cut` from `model`), and instead of a 5-file Inc-1 the move splits into two trunk increments, each ≤ 4 SOURCE and byte-identical at every step — Inc-1a: the leaf + the `model`/`descriptor`/`audit` re-points (4); Inc-1b: the `adapter` re-point (1)** | `cut`/`DISPLAY_MAX` in `mapper/relmap/model.py:34,67-71`; `refusal_line` in `mapper/relmap/descriptor.py:211` + the second path `mapper/relmap/audit.py:34,209-210` | NEW leaf; `model`, `descriptor`, `audit` re-point in Inc-1a; `adapter` re-points in Inc-1b; zero references to the old paths in the increment that re-points each reader | every R1 relmap module; the R2 renderers' value cuts | **FREEZE (D2)** |
| `keymap`: `SCOPE_RELMAP = "relmap"` registered in `GROUP_SCOPE`/`GROUP_HEADER`, binding exactly `1`/`2`/`3` (view switch), cursor keys (selection), `enter` (lens focus), `c` (chain toggle), `k` (by-kind grouping toggle — SHIPPED per `LED-2026-10-25-r2.01`), `r` (refresh), `q` (leave), `escape` (quiet-leave alias); no chord bound twice inside the scope (LLR-RVH.4.1) | none (precedent: the additive `SCOPE_REVIEW`, `mapper/keymap.py:41`) | NEW additive scope; the seat stays single (R-007), no existing `KeyBinding` moves | `RelMapScreen.BINDINGS`, the keybar, the palette, the help overlay — all generated from the seat (LLR-RVH.4.2/.4.4) | **FREEZE (D3)** — lands whole in trunk Inc-2 (ARC-02, `LED-2026-10-25-r2.08`) |
| The `--audit` hook per-line bound: after the report escaper, any hook line longer than **240** characters is cut at **239** with one trailing ellipsis; the cut never splits an escape spelling (a `\xNN`/`\uXXXX` spelling straddling byte 240 backs to the spelling start) and never re-exposes `verdict: ` to line start; the R1 D4 semantics (the 1,000-line count bound, the `structure: verdict: …` prefix rewrite, the fixed no-repo/no-registry lines keyed on `chain_status`, the exit code) are unchanged (`LED-2026-10-25-r2.02`; LLR-RVU.1.1) | none — `HOOK_LINE_LIMIT = 1000` exists (`mapper/reqharness/audit.py:82`), no per-line bound | per-line cut at the sink (`mapper/reqharness/audit.py` print path, `:372-383` + `:430-431`) | `mapper --audit` output readers; the R1 audit suite stays green | **FREEZE (D4)** — the bound value 240 and the cut semantics; only the ellipsis glyph is the frozen presentation detail |
| The reqharness glyph/table details: verifies `✓` · binds `●` (bound) / `◐` (tagged) / `○` (none — the row badge) · refines `•` · covers `≡` · diagonal `▪` · no edge `·` (OQ-M3, orchestrator-accepted; LLR-RVM.1.2) | none (the mechanism — strongest edge wins, ALERT before plain — is independent of the table) | NEW, pinned in the renderer + legend | the matrix cells and legend; the lens/sheet evidence glyph column | **FREEZE (D5)** — frozen at this PDR so the lanes share one table |
| Home enumeration + kind badge; open routing by descriptor kind; `app` re-export of `RelMapScreen` | Home globs only `*.mmd` (`mapper/screens/home.py:209`); opens only `MapScreen` | `*.relmap.yml` beside `*.mmd` in one name-sorted list; badge `relation·reqharness` (INK on STEP); the derived row at zero descriptors; routing pushes `RelMapScreen` for relation rows | the operator; AT-145…147 | not frozen — it is a lane-owned surface (shell), and the freeze set above is what the lanes share |
| Help + palette relmap entries | none | derived from the seat, no hand-written rows | the operator; AT-149 | not frozen — 6b surface |

**A frozen interface is not touched inside a lane.** A lane that needs to change D1–D5 STOPS and
re-cuts, or moves the boundary at a new ARQ (fork precondition F-3). **The frozen set is exactly:**
D1 the host↔renderer surface — including the named toggle-state channel (COND-ARCH-1): the frozen
renderer state-query/toggle entry `toggle(kind: str) -> str` per renderer, the renderer owning the
`c` density / `k` by-kind state, the host's `action_*` calling the active renderer's entry — and,
per the trunk Inc-2 review-pass amendment (orchestrator ruling, `LED-2026-10-25-r2.18`): the
`row_count(state) -> int` cursor-axis entry (one host cursor per view, clamped within
`[0, row_count)`, no wrap), the per-view toggle-state word in the crumb, and the dropped `lens`
field; D2
`text.py` (`cut`, `DISPLAY_MAX`, `refusal_line` — one site, one path; the re-point set names
`adapter.py`, landed as trunk Inc-1a + Inc-1b per the orchestrator ruling, each step byte-identical);
D3 `SCOPE_RELMAP` (the nine binding families above, uniqueness, seat-derived BINDINGS/keybar/
help/palette — the view-specific chords `enter`/`c`/`k` inert off their home view per COND-UX-1);
D4 the hook per-line bound 240 / cut at 239 after escaping / no mid-spelling cut / D4
semantics unchanged; D5 the reqharness glyph/table. Everything else in this batch is a lane-owned
surface over the frozen D3 (R1) API. The four-sink seam is `darkside._row_text`/`fit` (COND-SEC-1)
— `plain` + LF/TAB/CR → single space (`mapper/darkside.py:576-621`); bare `plain` preserves
LF/TAB and is not the seam.

## 5 · Proposed test cases

### 5.1 Per deliverable file — RED counterfactual and mutants per LLR

*RED counterfactual for every new source file:* move the file aside and run its tests — they must
fail at import or assertion, then pass when restored. *Mutants:* the named negative control per LLR
in the contract (`01-requirements.md` §4) and the per-AT negative arms in
`01b-acceptance-design.md:293-319`; each row's mutant turns the listed test RED.

| New / edited file | Move-aside RED (what fails) | LLR → asserting test (layer) → mutant that turns it RED |
|---|---|---|
| `relmap/text.py` + the four re-points (Inc-1a: `model`/`descriptor`/`audit`; Inc-1b: `adapter`) | `test_relmap_text.py` import error; the re-pointed R1 files fail at the old import paths | RVT.1.1 → definition-site census 1/1/1 (`test_relmap_text.py`, A) → M-RVT-1 (a second `def cut` left in `model.py`); RVT.1.2 → one-path census per increment over the re-pointed reader paths (`test_relmap_text.py`, A) → M-RVT-2 (one test still imports `refusal_line` from `mapper.relmap.descriptor`); RVT.1.3 → byte-identity probe at EVERY step — after Inc-1a and after Inc-1b — + R1 golden surfaces (`test_relmap_text.py`, A) → M-RVT-3 (the moved `cut` drops the ellipsis) |
| `screens/relmap/__init__.py` + `screen.py` + `base.py` + `keymap.py` | `test_relmap_shell.py` host arms fail (no `RelMapScreen`); `test_keymap.py` fails (no scope) | RVH.3.2 → derive-count arms (open = 1, after `r` = 2, `test_relmap_shell.py`, A/B) → M-RVH-8 (`r` re-renders from the cache); RVH.3.3 → workspace-as-repo non-git fixture arm (A/B) → M-RVH-16 (derivation consults `.git`), M-RVH-17 (raw exception escapes on a missing canon); RVH.4.1 → seat uniqueness/conformance (`test_keymap.py`, A) → M-RVH-9 (a second binding on one chord); RVH.4.2 → BINDINGS == seat census (`test_relmap_shell.py`, A) → M-RVH-10 (a hand-written binding on the screen); RVH.4.3 → view-switch + crumb arms (A/B) → M-RVH-11 (`2` swaps the canvas without updating the crumb); RVH.5.1 → closed-set refusal census + app-lives arms (A/B) → M-RVH-13 (`str(exc)` rendered), M-RVH-14 (re-raise); RVM.4.2/RVG.3.1/RVS.5.1/RVH.5.2 → the four-sink hostile arms (unit + AT-134/139/144/148 hostile) → M-RVM-11, M-RVG-12, M-RVG-13, M-RVS-1 family, M-RVH-15 |
| `screens/relmap/matrix.py` | `test_relmap_matrix.py` import error | RVM.1.1 → row/window census arms → M-RVM-1 (drop row windowing — the cap-scale arm of AT-137 also dies); RVM.1.2 → cell census over the synthetic binds map (AT-133) → M-RVM-2 (letters — the rejected variant), M-RVM-3 (evidence tone dropped); RVM.1.3 → declaration + ruler + legend arms → M-RVM-1 (`NN out of view` dropped); RVM.2.1 → ring/hop oracle arms → M-RVM-5 (orphaned hop-2 rows); RVM.2.2 → summary/gauge arms + AT-131/132 → M-RVM-7 (`None` reach coerced to `0`); RVM.2.3 → dimming census (`neighbourhood` counting wrapper, AT-131 black-box arm per `LED-2026-10-25-r2.10`) → M-RVM-6 (per-row `neighbourhood`); RVM.3.1 → skeleton-honesty census (AT-130) → M-RVM-8 (phantom columns); RVM.3.2 → empty/unknown-selection arms → M-RVM-9 (raise on unknown id); RVM.4.1 → geometry + C10 sweep arms → M-RVM-10 (lean on clipping) |
| `screens/relmap/gaps.py` | `test_relmap_gaps_view.py` + `test_relmap_scalecheck.py` import error | RVG.1.1 → rendered-order == `rank_gaps` order arm → M-RVG-1 (re-sort by node id); RVG.1.2 → chips/tally arms (AT-135) → M-RVG-2 (`total` chip dropped); RVG.1.3 → row anatomy + cursor arms (AT-135) → M-RVG-3 (unpadded reach / a bar glyph), M-RVG-4 (initial cursor on the last row); RVG.1.4 → window/cut-marker arms + the 87-col WHAT-drop (AT-137) → M-RVG-5 (window clamped), M-RVG-6 (WHAT truncated below minimum); RVG.1.5 → by-kind bands (AT-136) → M-RVG-7 (bands sorted by row count instead of catalogue order); RVG.2.1 → casing census over the renderer source (A) → M-RVG-8 (`.upper()` restored / a hard-coded caps literal); RVG.2.2 → chrome-casing arm → M-RVG-9 (one caps chrome string); RVG.2.3 → honest-zero + not-computed arms (AT-138) → M-RVG-10 (`000` rendered as `-`), M-RVG-11 (not-computed marker dropped); RVG.3.1 → hostile frame arm (AT-139) → M-RVG-12 (`plain()` pass removed), M-RVG-13 (markup-parsing sink) |
| `screens/relmap/sheet.py` | `test_relmap_sheet.py` import error | RVS.1.1 → header rows over `RelMap.node` (AT-140) → M-RVS-1 (header into a markup sink without `plain`); RVS.1.2 → Darkside-casing census → M-RVS-2 (kind/type verbatim caps); RVS.2.1/.2.2 → FEEDS IT / A CHANGE REACHES row oracles on an asymmetric fixture → M-RVS-3 (edge looked up in the wrong direction), M-RVS-4 (sections swapped); RVS.2.3 → evidence-glyph table arm → M-RVS-5 (glyph keyed on the neighbour's kind); RVS.2.4 → declared-empty arms (AT-140) → M-RVS-6 (empty section skipped); RVS.3.1 → hop-2 cut count vs the independent up-only oracle (TC-RM-17) → M-RVS-7 (both-direction count); RVS.3.2 → stacked hop-marker oracle on a diamond fixture → M-RVS-8 (BFS depth through both directions); RVS.3.3 → `c` toggle + crumb/note declarations (AT-141) → M-RVS-9 (note flips, rows do not); RVS.4.1 → node-gaps filter arm (AT-142) → M-RVS-10 (filtered by severity); RVS.5.1 → hostile frame arm (AT-144) → the M-RVS-1 family; RVS.6.1 → width discipline at 118/87 (AT-143) → M-RVS-11 (raw title painted); RVS.6.2 → counted-overflow arm (AT-141/143 black-box) → M-RVS-12 (rows dropped past the viewport); RVS.7.1 → `osopen` absence census (A) → the census itself reddens on any later import |
| `screens/home.py` + `app.py` | `test_relmap_shell.py` shell arms fail | RVH.1.1 → enumeration arm (AT-145) → M-RVH-1 (only `*.mmd` globbed); RVH.1.2 → badge census `relation·reqharness` (TC-RM-22) → M-RVH-2 (caps badge); RVH.1.3 → one-list order arm → M-RVH-3 (relation rows appended after tree rows); RVH.2.1 → routing pilot (AT-146) → M-RVH-4 (relation row routed to `MapScreen`); RVH.2.2 → BINDINGS census (no write vocabulary in the scope) → M-RVH-5 (a write action added); RVH.2.3 → instrumented save-count arm → M-RVH-6 (open persists derived nodes); RVH.3.1 → derived-row + derivation-args probe (AT-147) → M-RVH-7 (hard-coded non-default descriptor) |
| `screens/help.py` + `screens/palette.py` | help/palette arms of `test_relmap_shell.py` fail | RVH.4.4 → help == seat and palette == seat (AT-149) → M-RVH-12 (a hand-added help row) |
| `reqharness/audit.py` (per-line bound) | `test_hook_line_bound.py` fails; the sink arms of AT-152 fail | RVU.1.1 → emitted-length ≤ 240 arms + the straddling-spelling arm (AT-152) → M-RVU-1 (cut before escaping), M-RVU-2 (cut re-exposes `verdict: `), M-RVU-3 (mid-spelling cut); the D4 behaviours are pinned by the unchanged R1 suite (TC-RM-02/03) |

**Acceptance tests (Layer B).** AT-130…AT-152 per `01b-acceptance-design.md:31-291` and the
AT↔requirement matrix at `:293-319`: every view AT opens the derived reqharness map through the host
surface (fixture workspace → Home → relation row → `RelMapScreen`) and drives REAL keys (C-16 — no
`.focus()` proxies), every AT moves a non-default value (C-10), with boundary + negative arms.
Layer A (TC-RM-04…30) applies per the contract §4 `Asserting tests` fields; Layer 0 applies where a
unit has cyclomatic complexity ≥ 3 or transforms data crossing a declared boundary. Absolute counts
are asserted only on seeded fixture canons; the live worktree canon gets invariant/census arms
(303 nodes, 215 `refines` edges, 7 gaps — premise P2).

### 5.2 Reverse census — by import AND by fixture content (family B — owed per increment)

By **import / symbol** (`git grep` over `mapper/` and `tests/`; per-increment census runs in the
lane's first increment — F-4):

| Symbol touched | Hits | Consequence |
|---|---|---|
| `home.py` map enumeration + open route | enumeration single site `mapper/screens/home.py:209`; table `:300`; rows `:369-374`; tree open route `:455-458`; badge precedent `:352-358` | one edit site; AT-145/146 pilot arms pin the rendered rows and the routed screen |
| `LEAK_EXCEPTIONS` line-pin | `tests/test_inc9c.py` pins `("mapper/screens/home.py", 176, "str(exc)")` (ARCHITECTURE §6 census, `docs/ARCHITECTURE.md:360-362`) | Inc-6 re-pins the line number in the SAME increment it inserts code above the pinned line |
| `keymap` seat | `mapper/keymap.py` scope constants `:27-41`, uniqueness rule `:25` + `duplicate_chords()` `:488`, `KeyBinding` shape `:139-152`, leave precedent `:230-231`; whole-seat pin `tests/test_key_dispatch.py:189` (COND-ARCH-3 citations repaired at the seal; re-repaired per COND-DDR-1 at the P5 records pass, `LED-2026-10-25-r2.32`) | a scope is data — the whole-seat pin does NOT move; both pins are the Inc-2 census (`tests/test_keymap.py`, `tests/test_key_dispatch.py`) |
| help / palette surfaces | `mapper/screens/help.py:223`; `mapper/screens/palette.py:36`; `mapper/keymap.py:475` (`palette_items` — the phantom `screens/palette.py:432` repaired per COND-UX-3; re-repaired per COND-DDR-1 at the P5 records pass, `LED-2026-10-25-r2.32`); app help/palette actions `mapper/app.py:274-296` | 6b adds seat-derived entries only; `tests/test_help_scope.py` + palette-adjacent tests re-run |
| A3 census | `tests/test_a3_census.py` pins the ARG-FUL `.render(` count | relation renderers add no `.render(` call — they paint Canvas cells directly (ARCHITECTURE §6 census, `docs/ARCHITECTURE.md:364-365`) |
| `osopen` allow-list | `tests/test_arch_osopen_callers.py` | no new `osopen` edge from `screens/relmap` (LLR-RVS.7.1 bans it on the sheet) |
| `mod_*` path censuses | `tests/test_mod_*` | the package lands at the declared paths; censuses re-run |
| the R1 relmap suite | `tests/test_relmap_*.py` — re-pointed files `test_relmap_model.py:17-26`, `test_relmap_descriptor.py:38`, `test_relmap_audit.py:33-35` | Inc-1a/1b re-count them; the golden surfaces stay byte-identical at every step (AT-151) |
| guard set | `tests/test_fold.py`, `tests/test_repair_artifact_claims.py` (C-1); pre-commit adds `tests/test_no_operator_paths.py` | every targeted run includes the guard set |

By **fixture content** (tests whose fixtures the new code reads):

| Fixture class | Tests | Consequence |
|---|---|---|
| the `--audit` surface over fixture repos | the R1 suite's 16 `--audit` sites (`tests/test_reqharness_release.py`, `tests/test_reqharness_baseline.py`) | Inc-7 adds the per-line cut at the sink; the R1 suite must stay green unchanged — a failure is a defect in the cut, not a stale test |
| the live `REQUIREMENTS.md` derived map | premise P2: 303 nodes (85 HLR, 218 LLR), 215 `refines` edges, 7 gaps, reach flat 0 | AT-147/AT-130 census arms pin the honest skeleton; the views never invent US/AT/TC content (B-141) |
| hostile-payload vocabulary | R1 AT-122 arm 3 practice; R2 adds **LF + TAB** per COND-SEC-1 (the P12 premise, `01-requirements.md:261`); dual-guard precedent `mapper/screens/draft_guard.py:54-67` | AT-134/139/144/148 hostile arms + the four-sink unit arms render the payload literally ON ONE row — LF/TAB coerced to single spaces by `_row_text`/`fit` (`mapper/darkside.py:576-621`), so a payload cannot forge a second row — free regression arms for the new labels |
| `<name>.relmap.yml` descriptors at the workspace root | none tracked (`git ls-files` finds none); discovery is `discover_descriptors` (≤ 8, sorted) | the input class is new to the TUI; the D2-frozen reader governs every byte |

Census is best-effort; the increment gates confirm completeness, and the DDR runs the census CROSSED
between lanes — the one check impossible from inside a lane.

### 5.3 The two discharged seams, and the PDR conditions' homes

*AT driver (F-5).* The injection point is the `MapperApp(workspace=…)` constructor argument
(`mapper/app.py:250`), consumed into `MapStore(workspace)` (`mapper/app.py:256`) — no env var, no
monkeypatch, no cwd games — driven by a headless `run_test()` pilot
(`tests/test_colour_always_on.py:64-70` idiom). Probe PASS 2026-10-25
(`evidence/p2-seam-at-driver.md`, ruling `LED-2026-10-25-r2.07`): the pilot reaches Home, lists the
fixture row and exits cleanly; lanes 3–5 re-verify the injection at their entry, not only at the join.

*Workspace-as-repo.* The canon resolves at the workspace root as `Path(workspace)/descriptor.canon`
(`mapper/relmap/adapter.py:129`) and descriptors by flat `os.listdir(workspace)`
(`mapper/relmap/descriptor.py:200-208`) — git is never consulted on this path; a missing/unreadable
canon yields the closed-set `CanonUnavailable` cause (K3 `file not found`, K7 `is not UTF-8 text`)
rendered as the fixed refusal line, never a crash. Probe PASS 2026-10-25
(`evidence/p2-seam-workspace-repo.md`, ruling `LED-2026-10-25-r2.03`), pinned in LLR-RVH.3.3. Scope
note: the R1-frozen `--audit` CLI hook's own git gating is the RVU/D4 surface, NOT governed by this
rule.

*Where each PDR condition is discharged* is tabulated in the PDR record §A at seal time; the
design-level ones land in this proposal and in the contract now, the test-level ones at the named
increment gate.

## 6 · Risks and rejected alternatives

**Top risks.**

| # | Risk | Mitigation / owner |
|---|---|---|
| 1 | Cap-scale rendering — the shipped 100,000-node `MAX_NODES` cap reaches the screen; windowing must stay declared and bounded | the windowing LLRs bound per-render work by construction (M-RVM-1 at the AT-137 cap-scale arm, M-RVS-12 on the counted overflow line); the neighbourhood is computed for the focused node only (M-RVM-6); a generous 10× wall-clock budget is recorded at Phase 3 (`LED-2026-10-25-r2.09`) |
| 2 | Markup injection at the FOUR sinks — canon/descriptor text (hostile ids, titles, gap sentences) reaching markup-parsing sinks | one assembly seam: every label coerced through `darkside._row_text`/`fit` (`plain` + LF/TAB/CR → single space, `mapper/darkside.py:576-621` — bare `plain` preserves LF/TAB, which is why it is not the seam) into explicit-style `Text` or `markup=False` sinks (`mapper/screens/draft_guard.py:54-67` precedent); width cuts apply to the COERCED string, never the reverse (the C-10 order, `LED-2026-10-25-r2.06`); the hostile vocabulary carries LF + TAB (COND-SEC-1, `LED-2026-10-25-r2.14`) with a payload-renders-on-ONE-row assertion; hostile-payload AT arms per view (AT-134/139/144/148) + the four-sink mutants M-RVM-11, M-RVG-12/13, M-RVS-1 family, M-RVH-15/18 |
| 3 | Keymap census pins drift — `SCOPE_RELMAP` chord uniqueness, BINDINGS == seat, help/palette derived from the seat | the seat lands whole in trunk Inc-2 before any lane forks (ARC-02); `tests/test_keymap.py` conformance + the BINDINGS/help/palette equality censuses (M-RVH-9/10/12, TC-RM-25); the whole-seat pin `tests/test_key_dispatch.py:189` does not move (re-repaired per COND-DDR-1 at the P5 records pass, `LED-2026-10-25-r2.32`) |
| 4 | The 87-column sweep is where the lens panel and the matrix grid fight for width | the prototype proved the cuts at 87; the ATs pin them (`test_relmap_scalecheck.py`, AT-131/137/143 87×34 arms) with zero unexplained C10 events as the gate |
| 5 | The host↔renderer surface slips while three lanes draft against it | F-2 makes this PDR's seal the condition of any lane starting; slippage re-serializes the lanes, it does not silently break them (`01-requirements.md:1073-1076`) |
| 6 | The hook bound false-fails long refusal/canon lines | the bound 240 was measured against the R1 worst-case line (refusal line cut at 120, report ≤ about 298 lines — premises P10/P11); the R1 golden surfaces catch a wrong bound at the Inc-7 gate; D4 semantics stay pinned by the unchanged R1 suite |
| 7 | Skeleton honesty — the R1 map is the HLR/LLR skeleton only (7 gaps, flat reach 0, no US/AT/TC nodes) | the views are specified to render it honestly (the `no test columns yet` declaration, `000` reach, declared empties); richer arms run on in-test synthetic maps; nothing invents US/AT/TC content (M-RVM-8 census) |
| 8 | B-137/B-139 known flakes | a red in `test_reqharness_cache_fastpath.py` or the AT-113/AT-114 arms is not automatically a regression (P-05, PLAN.md:149-150) |

**Rejected alternatives — only where a real decision exists.**

| Alternative considered | Why it was rejected |
|---|---|
| The keymap seat scope in the shell lane (Inc-6), parallel to the renderer lanes | `RelMapScreen` cannot generate `BINDINGS` until the scope exists, so a lane-parallel keymap voided F-2 (the host unbuildable without it) and F-3 (a lane-owned seat every lane reads). Moved into trunk Inc-2 by ruling ARC-02 / `LED-2026-10-25-r2.08` |
| Renderer lanes forking before the screen host lands | The renderers draft against a host↔renderer surface that exists only as an ARQ commitment until Inc-2 lands; F-2 makes this PDR's seal the entry condition of every lane |
| Two presentation printers (`cut`/`DISPLAY_MAX`/`refusal_line` kept per-module, or a renderer-local copy of the cut) | Already decided against in R1 DDR §E 10-11 (B-153): wording can drift between two printers; one `relmap/text.py` leaf, one definition site, one import path. The renderers consume the frozen leaf names from the start — never a not-yet-existing module |
| `mapper.db` caching of derived nodes | R-019 (MAP-TYPES OQ6 recommendation): recompute-on-open + explicit refresh; the derivation costs about a second on the real canon, which the open absorbs; no schema migration, no second truth |
| Hand-written help/palette entries beside the seat | HLR-RVH.4.4: entries derive from the single seat (equality, not superset) — a hand row is M-RVH-12 |
| `n/a` — consuming anything beyond the R1 frozen API | Not a real decision: `PDR-2026-10-25-relmap-r1-batch#D3` froze the R2-consumable surface at R1's PDR; R2 changes none of it (the `text`-leaf move touches only tested seams that were never frozen) |
| `n/a` — the four view layouts | Not a real decision: the operator verdict of round 2026-10-23 (`verdict-2026-10-24.json`) binds matrix-panel, binds-glyphs, gaps-ranked and sheet-direct; the PDR freezes details, it does not re-pick layouts |
| `n/a` — the by-kind grouping toggle | Already ruled: SHIPPED per `LED-2026-10-25-r2.01` (LLR-RVG.1.5 + `k` + AT-136); the PDR freezes only the glyph/table details |

## 7 · Forward-applicability table — **the section that makes this document honest**

| Output of this PDR | Named consumer downstream | Where the consumer will read it |
|---|---|---|
| design characteristics (§2 boundaries, §3 algorithms, the per-view renderer cuts, the frozen surface D1) | the renderer lanes 3/4/5 and the shell lane 6, read at each lane's entry | this proposal §2.1, §4 + each lane packet's §2 |
| enablers: the `text.py` leaf (Inc-1a + Inc-1b, first), the host↔renderer surface + the keymap seat (trunk Inc-2), the AT-driver injection + the workspace-as-repo rule (probed 2026-10-25) | Phase 3 lanes and Phase 4 validation (AT-130…AT-152) | `mapper/relmap/text.py`, `mapper/screens/relmap/{screen,base}.py`, `mapper/keymap.py`; `evidence/p2-seam-at-driver.md`, `evidence/p2-seam-workspace-repo.md` |
| proposed test cases and mutants (§5.1) | layers 0/A/B, the RED battery per increment, and the DDR | each increment packet's RED section + `01b-acceptance-design.md` matrix |
| design → requirement traceability (§1 chain map, §5.1 LLR rows) | the traceability matrix and the DDR | batch `06-docs/traceability-matrix.md` + `PDR-2026-10-25-relmap-r2-batch.md` §A row 4 |
| reverse census (§5.2) | each increment's exit check and the DDR crossed census (F-4) | the PDR record §A row 8 + DDR row 3 |
| frozen-interface list (§4, D1–D5) | `docs/ARCHITECTURE.md` §4 (after the seal — the two PLANNED rows become frozen rows) and the R3/R4/R5 batches (timeline, metro, FTS consume the same screen) | `docs/ARCHITECTURE.md:266-267`; the later rounds' PDRs |

- ⚠ Any row whose consumer column is empty: none.

## 8 · Parallelisation plan *(A4 fired: ONE trunk, then FOUR lanes, then the join)*

| Lane | Modules / layer | Files it owns | Agent |
|---|---|---|---|
| trunk Inc-1a · text leaf (first half) | `relmap` (data layer) | `mapper/relmap/text.py` + the `model`/`descriptor`/`audit` re-points | `software-dev` (trunk) |
| trunk Inc-1b · text leaf (second half) | `relmap` (data layer) | `mapper/relmap/adapter.py` re-point | `software-dev` (trunk) |
| trunk Inc-2 · screen host | `screens/relmap` (host + base) + `keymap` | `mapper/screens/relmap/{__init__,screen,base}.py`, `mapper/keymap.py` | `software-dev` (trunk) |
| L1 · matrix | `screens/relmap` renderer | `mapper/screens/relmap/matrix.py` + `tests/test_relmap_matrix.py` | lane agent |
| L2 · gaps | `screens/relmap` renderer | `mapper/screens/relmap/gaps.py` + `tests/test_relmap_gaps_view.py`, `tests/test_relmap_scalecheck.py` | lane agent |
| L3 · sheet | `screens/relmap` renderer | `mapper/screens/relmap/sheet.py` + `tests/test_relmap_sheet.py` | lane agent |
| shell · Inc-6 + 6b | `screens/home`, `app`, `screens/help`, `screens/palette` | `mapper/screens/home.py`, `mapper/app.py`, `mapper/screens/help.py`, `mapper/screens/palette.py` | lane agent |
| any boundary · Inc-7 | `reqharness` | `mapper/reqharness/audit.py` + `tests/test_hook_line_bound.py` | lane agent |

- `modules(lane_i) ∩ modules(lane_j) = { }` — or same domain / different layers with the interface frozen: **✓** (the lane worksheet intersections stay empty, `docs/ARCHITECTURE.md:352-356`: one renderer file each; shell ∩ renderers = { }; text leaf ∩ everything = { }; hook bound ∩ everything = { }).
- **File sets are disjoint** (not just modules — two lanes may not edit the same file, not even different regions): **✓** (SOURCE counts 4, 1, 4, 1, 1, 1, 2, 2, 1 across Inc-1a/1b, Inc-2, lanes 3/4/5, shell, 6b, Inc-7 — ≤ 4 each; the Inc-1 → Inc-1a + Inc-1b split is the orchestrator ruling at the PDR seal answering COND-ARCH-2/COND-QA-1; the `test_inc9c.py` line-pin re-pin is a test edit inside Inc-6, not a source file).
- Family-B reverse census run **per lane and shared** before forking: **✓** (§5.2 per increment, F-4; the DDR runs it crossed).
- Trunk-only artifacts (requirements · traceability · backlog · SPEC) are written **only** by the trunk: **✓**.
- The fork preconditions F-1…F-5 (`01-requirements.md:270-274`) gate every lane's entry, with F-2 — this PDR's seal — as the hard one; the join (F-5) runs every lane's ATs on the joined tree before the DDR.
