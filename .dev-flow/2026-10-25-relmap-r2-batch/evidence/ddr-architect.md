# DDR evidence — architect — Batch 2026-10-25-relmap-r2-batch

| Field | Value |
|---|---|
| Role | `architect` — independent reviewer at the DDR gate (A4 fork JOIN); authored none of the work under review |
| Batch | `2026-10-25-relmap-r2-batch` · worktree HEAD `d7bb95e` (branch feat/relmap-r2) |
| Date | 2026-10-26 |
| Scope | DDR §B rows 1, 2, 6, 7 · §B row 8 conditions COND-ARCH-1/2/3 only · §H id glue. No test suite run (per commission: evidence is git, file reads, greps). Rows 3/4/5 (software-dev / QA), the C-18 question and the UX walkthrough read are other reviewers'. |

---

## Findings

| # | Severity | One line | DDR row / condition touched | Evidence |
|---|---|---|---|---|
| F-1 | MAJOR | COND-ARCH-3's "discharged" claim does not survive re-reading the artifact: the three repaired citations drifted AGAIN before the lanes forked — trunk Inc-2 (`8be99a3`) legitimately inserted the relmap seat (+43 lines into `mapper/keymap.py`) and the relmap `EXPECTED_SEAT` rows (+19 lines into `tests/test_key_dispatch.py`), re-breaking two of the three repaired line citations; the structural citation census only checks "file has ≥ NNN lines", so it cannot see this class | DDR §B row 8 / COND-ARCH-3 | `01-requirements.md:255` (P6 cites `tests/test_key_dispatch.py:170` "the pin assertion" — :170 is today inside the relmap seat comment block; the pin `test_at_n03h_the_whole_seat_matches_its_specification` is at `tests/test_key_dispatch.py:189`); `01-requirements.md:813` (LLR-RVH.4.4 draft-time cites `mapper/keymap.py:432` as `palette_items` — :432 is today inside `keybar_groups`; `palette_items` is at `mapper/keymap.py:475`); `01-requirements.md:784` + `design/design-proposal.md:254` cite `duplicate_chords() :445` — the function is at `mapper/keymap.py:488`; drift proven by `git diff 867dfd7..HEAD -- tests/test_key_dispatch.py` (19 lines inserted above :170) and `git show 8be99a3 --stat` (seat +43); census blind spot: `tests/test_repair_artifact_claims.py:216-230` checks only line-count existence. Discharge path: records-only re-repair of four line numbers across two files — no code, no interface, no suite re-run (re-run the A-110 privacy guard on the staged tree per the G-002 lesson) |
| F-2 | MINOR | §H D6 (and the PDR D6 ruling annotation it quotes) labels the count sequence "as built", but the sequence is the PLAN: as built, Inc-6b shipped **0** SOURCE (derivation pre-shipped), so the as-built counts are 4/1/4/1/1/1/2/**0**/1 | DDR §H D6 · §B row 7 wording | `03-increments/increment-006b.md:49` ("SOURCE files 0/4 — no source delta"); `git show 23bce8a --stat` (tests only, zero `mapper/` files); the "2" for 6b traces to `PLAN.md:140` (`screens/help.py`, `screens/palette.py` (2) as planned). Row 7's substance is unaffected — every increment ≤ 4 |
| F-3 | MINOR | Row 6's parenthetical "the follow-up unit `fb336ed` … (review discharges, records-only/test arms)" understates the commit: it also edited three SOURCE files — each the lane's OWN review discharge, so row 6's substance holds, but the words "records-only/test arms" are imprecise | DDR §B row 6 wording | `git show fb336ed --stat`: `mapper/screens/home.py` +12 (L6's own review-inc006 F2), `mapper/screens/relmap/gaps.py` +8 (L4's own review-inc004 F1), `mapper/screens/relmap/matrix.py` +5 (L3's own review-inc003 F1/F2); each declared in the commit message body and the corresponding `evidence/review-inc00{3,4,6}.md` |

---

## Per-checklist-row disposition (the rows in my scope)

### §B row 1 — what changed against the PDR, and why — ✓ satisfied

Each §A change claim re-read against the records, not the draft's summary:

1. **D1 amendment at trunk Inc-2, before any lane forked** — verified. The independent review exists and rules what the draft says: `evidence/review-inc002.md:10` (verdict `iterate`, BLOCK-UNTIL F1/F2), F1/F2 at `:63-68`. The discharge commit is `64bc1bc`; the fork gate is `6d81a3f` ("lanes may fork") — `git log --oneline 867dfd7..HEAD` shows `64bc1bc` before `6d81a3f`, so no lane drafted against the unamended freeze. The ruling is DECLARED, not silent: the PDR gained its post-seal ruling annotation in that same window (`git log --follow -- design/PDR-2026-10-25-relmap-r2-batch.md` shows `64bc1bc` touching the PDR), the annotation text is on the sealed record (`design/PDR-2026-10-25-relmap-r2-batch.md:120-130` and the §D D1 row :158), the ledger entry `LED-2026-10-25-r2.18` exists (`01-requirements-ledger.md:380-396`), and `.dev-flow/state.json` `decisions_log` P3 entry records "D1 amended before any lane forked". Re-read ordering nuance: review → ruling + implementation in one trunk commit → packet record (`64ec4e9`) → fork — the iterate gate did not pass until the amendment, which is the flow's mechanism, not a silent edit.
2. **Inc-1a/Inc-1b split superseding the SOURCE-5 mechanism** — verified. Ruling at the PDR seal: commit `78ee993` precedes the implementation commits `968c2c0` (4 source files: text/model/descriptor/audit, `git show --stat` verified) and `01e87b5` (1 source file: adapter.py). Declared in: PDR §B COND-ARCH-2/COND-QA-1 rows and the §D D6 ruling annotation (`design/PDR-2026-10-25-relmap-r2-batch.md:163`); ledger `LED-2026-10-25-r2.16` (`01-requirements-ledger.md:346-364`); `state.json` `decisions_log` PDR entry. Recorded before the work. ✓
3. **`k` shipped on the by-kind toggle** — verified as pre-PDR, not a post-PDR change. Ruled at P2 (`state.json` `decisions_log` P2 entry: "ship the by-kind toggle on the gaps view"); ledger `LED-2026-10-25-r2.01` (`01-requirements-ledger.md:23-34`); bound in the sealed contract's LLR-RVH.4.1 Statement (`01-requirements.md:782`, "`k` to the by-kind grouping toggle") and LLR-RVG.1.5 (`01-requirements.md:552`); landed at `mapper/keymap.py:356`. PDR row 9 (:39) records SHIPPED per LED-2026-10-25-r2.01. ✓

### §B row 2 — frozen interfaces intact — ✓ satisfied

Re-read in the code at HEAD, against the PDR §D surface **as amended by the §B conditions and the two ruling annotations**:

- **D1 as amended** — `mapper/screens/relmap/base.py`: `RelMapView.row_count(state) -> int` at `:123-127`; per-view cursor/word semantics and the full kind vocabulary (`enter`/`c`/`k`, word `panel lens`) and the renderer `notice` obligation in the module docstring `:9-47` and the `toggle` contract `:25-35`; `RelMapView.toggle(kind: str) -> str` at `:129-131`; `ViewState` (`:90-105`) carries NO `lens` field (fields: relmap, notice, focus, cursor, gaps, width, height). Host side: `mapper/screens/relmap/screen.py` keeps one cursor per view (`self._cursors = {name: 0 …}` at `:93`, reset at `:142,:167`), one toggle word per view (`:98`), moves the active cursor clamped in `[0, row_count(state))` with no wrap (`:265-280`), and stores the toggle word per view for the crumb (`:299-302`). Frozen-surface files were touched only by trunk commits (`git log 867dfd7..HEAD -- mapper/screens/relmap/base.py mapper/screens/relmap/screen.py mapper/keymap.py mapper/relmap/text.py` → `968c2c0`, `8be99a3`, `64bc1bc` only).
- **D2** — one definition site, one import path: `mapper/relmap/text.py` defines `cut`/`DISPLAY_MAX`/`refusal_line`; `git diff 867dfd7..HEAD -- mapper/relmap/model.py` removes exactly the old `DISPLAY_MAX`/`cut` (8 deletions, nothing else); `mapper/relmap/audit.py:38` imports from the leaf and its `__all__` (:209-211) no longer re-exports `refusal_line`; `descriptor.py:32` and `adapter.py:31` import from the leaf; repo-wide grep for old-path readers (`model import … cut`, `.model.cut`, `descriptor import … refusal_line`) returns zero hits.
- **D3** — `SCOPE_RELMAP` seat at `mapper/keymap.py:43`, the 13-binding seat block `:342-358` including `k`→`by_kind` (`:356`), inert-off-home declared in the seat comment `:334-341`.
- **D4** — `mapper/reqharness/audit.py:88` (`HOOK_LINE_CELLS = 240`), `_cut_hook_line` at `:127-154` (cut at 239 + one ellipsis on the EMITTED escaped form, straddle back-off), the sink order in `run_cli` (:471-474) and the pinned F-SEC-3 pipeline order in the docstring (:136-137); R1 semantics intact (`HOOK_LINE_LIMIT = 1000` at :82, the fixed `STRUCTURE_NO_REPO`/`NO_REGISTRY` lines :89-90, `verdict: ` prefix rewrite untouched — the Inc-7 diff adds only the bound).
- **D5** — the shared glyph table re-read in two renderers: `mapper/screens/relmap/matrix.py:130` (the `_cell` D5 table; diagonal `▪`/no-edge `·` at :417-419) and `mapper/screens/relmap/sheet.py:54-59` (the D5 evidence-glyph table).
- **R1 frozen API** (`PDR-2026-10-25-relmap-r1-batch#D3`) untouched: `git diff 867dfd7..HEAD --stat` shows `mapper/relmap/gaps.py`, `mapper/reqharness/derive.py`, `mapper/relmap/profile.py` absent from the diff; `model.py` loses only `cut`/`DISPLAY_MAX` — never part of the frozen set (`docs/ARCHITECTURE.md:268` says so explicitly: "`cut`, `DISPLAY_MAX`, `refusal_line` were never frozen"). The one amended R1 arm (`tests/test_relmap_audit.py` AT-125) is re-pointed to the `structure_lines` seam, not deleted.

### §B row 6 — no lane touched another lane's file — ✓ satisfied (with F-3 wording notice)

Proven from git, per lane and per merge:

- L3 matrix (`c38f929` / merge `3b9eada`): source = `mapper/screens/relmap/matrix.py` only; tests = its own `test_relmap_matrix.py` + a 9-line `tests/test_fold.py` allowance (the scoped `.toggle(` census, declared in `evidence/review-inc002.md:101` — a shared census file, not another lane's file).
- L4 gaps (`e2f0d90` / `ee39668`): source = `mapper/screens/relmap/gaps.py` only; own tests only.
- L5 sheet (`2d332b2` / `4a9ecf8`): source = `mapper/screens/relmap/sheet.py` only; own tests only.
- L6 shell (`996b0ca` / `7a56db7`): source = `mapper/screens/home.py` + `mapper/app.py` (2, as declared); test edits to the shared `tests/test_inc9c.py` (`LEAK_EXCEPTIONS` pin) and `tests/test_relmap_isolation.py` — both declared at the PDR (`design/PDR-2026-10-25-relmap-r2-batch.md:38` names the inc9c re-pin; the isolation amendment is enumerated in review-inc002's seat census check).
- Follow-up `fb336ed`: cross-lane BY DECLARATION; the diff shows the three source edits are each the lane's OWN review discharge (see F-3) — no lane touched another lane's source file. `2e83cf6` (the join census amendment) touches only the two shared census files `tests/test_darkside_census.py` / `tests/test_inc9.py` + records.

### §B row 7 — source-file budget (max 4 per increment) — ✓ satisfied

As-built SOURCE counts re-derived from git (`git show --stat` per increment commit) AND matched against the packets' own file tables: 1a=4 (`968c2c0`; packet `03-increments/increment-001a.md:43-55`), 1b=1 (`01e87b5`; packet 001b:33-39), 2=4 (`8be99a3`; packet 002:47-64), 3=1 (`c38f929`), 4=1 (`e2f0d90`), 5=1 (`2d332b2`), 6=2 (`996b0ca`), 6b=0 (`23bce8a` — tests only; packet 006b declares "no source delta"), 7=1 (`4853b16`). Max reached = 4, only on the two declared trunk units, each justified in its packet (001a:59, 002:68). The "Inc-1 = 5" case was never built — the 4+1 split is what exists. Wording notice: see F-2 on the "as built" count label in §H D6.

### COND-ARCH-1 (MAJOR) — ✓ satisfied

Re-read by re-reading the artifact, not the draft: the channel `toggle(kind: str) -> str` is named in the proposal's §4 D1 row (`design/design-proposal.md:189`, "a frozen renderer state-query/toggle entry `toggle(kind: str) -> str` on each renderer … called by the host's `action_*`"), in `docs/ARCHITECTURE.md:266` (the LANDED row carries both the COND-ARCH-1 amendment and the LED-2026-10-25-r2.18 amendment verbatim), and in code at `mapper/screens/relmap/base.py:25-35` + `:129-131`. The PDR's own discharge record (`design/PDR-2026-10-25-relmap-r2-batch.md:104`) names the same three artifact lines; record side at `75f9e28`, channel built at `8be99a3`, amended once more at `64bc1bc` before the fork — all confirmed in git history.

### COND-ARCH-2 (MAJOR) — ✓ satisfied

Re-read: the plan side names `mapper/relmap/adapter.py` and the split in every cited site — proposal §2.1 (`design/design-proposal.md:108-109`), §4 D2 row (:190), §5.1 (:227), §5.2 (:341-342), §6 (:207), §8 (:207, :351 "SOURCE counts 4, 1, 4, 1, 1, 1, 2, 2, 1 across Inc-1a/1b …"); the re-points exist exactly as ruled (grep-verified, row 2 above); the zero-old-path reader census arms exist (`tests/test_relmap_text.py::test_no_old_path_readers_inc_1a/.1b` per packet 001b and the P4 Layer-A table); the ruling is declared on the sealed PDR (§B COND-ARCH-2 row :105 and §D D6 :163), in ledger `LED-2026-10-25-r2.16`, and in `state.json` `decisions_log` (PDR entry). Recorded at the seal (`78ee993`) before the implementation commits.

### COND-ARCH-3 (MINOR) — ✗ as claimed; re-open, records-only (see F-1)

The DDR's discharge cell ("yes — P3 2026-10-25 by `75f9e28` … every repaired citation re-verified") was true at `75f9e28` but is NOT true at the gate tree: the repaired line citations drifted again when trunk Inc-2 legitimately edited the same files BEFORE the lanes forked, and two of the three are wrong today (evidence in F-1). The gate rule requires discharge "by RE-READING the artifact, never by trusting that the corrective pass ran" — the re-read falsifies the claim. Discharge path is records-only and minutes-long: re-repair `mapper/keymap.py:432`→`:475` (`palette_items`), `mapper/keymap.py:445`→`:488` (`duplicate_chords`), `tests/test_key_dispatch.py:170`→`:189` (the pin assertion) in `01-requirements.md:255,:784,:813` and `design-proposal.md:254-255`; re-run the A-110 privacy guard on the staged tree (G-002 control). Also worth a flow note: `test_every_path_line_citation_resolves` checks only that the cited file has ≥ NNN lines, so this class slips it entirely — a content-anchor check belongs in the backlog discussion (P5), outside my scope to demand here.

### §H — ids this record binds — ✓ satisfied (with F-2 wording notice)

Each §H row's id re-read against the PDR §D table: D1 (amended) ↔ PDR §D D1 row + its ruling annotation (:158) — text matches (row_count, per-view cursor/word, `lens` dropped, full vocabulary, notice); D2 ↔ §D D2 (:159) — the DDR's "(as built)" note correctly subordinates SOURCE-5 to the declared ruling annotation; D3 ↔ §D D3 (:160) incl. the COND-UX-1 inert-off-home amendment and SHIPPED `k`; D4 ↔ §D D4 (:161) incl. the F-SEC-3 pipeline fold; D5 ↔ §D D5 (:162); D6 ↔ §D D6 (:163) — id glue exact, F-2 on the "as built" count label only; D7 ↔ §D D7 (:164). All seven ids cite `PDR-2026-10-25-relmap-r2-batch#D<n>` exactly as the PDR's own id column names them. Each row also names its repo landing line (LLR / `docs/ARCHITECTURE.md` § / test node), and those landings re-read true for D1 (`docs/ARCHITECTURE.md:266`), D3 (`mapper/keymap.py:342-358`), D4 (`mapper/reqharness/audit.py:88,127-154`) and D2 (`mapper/relmap/text.py`).

---

## Verdict

**approved with conditions**

One condition, individually dischargeable and records-only (no code, no interface, no suite re-run beyond the A-110 staged-tree guard):

- **COND-ARCH-3-REOPEN (owner: the DDR record author / orchestrator, before the seal)** — re-repair the three drifted line citations per F-1 (`mapper/keymap.py:432`→`:475`, `:445`→`:488` in `01-requirements.md:784,:813` and `design-proposal.md:254-255`; `tests/test_key_dispatch.py:170`→`:189` in `01-requirements.md:255` and the proposal), and fold the two MINOR wording fixes (F-2 §H D6 "as built counts 4/1/4/1/1/1/2/0/1" vs the planned sequence; F-3 row 6's "records-only/test arms" parenthetical) into the same records pass.

Rationale: every §A change claim is a declared ruling recorded before its work (row 1 ✓); the frozen surface as amended is exactly what the code ships and the R1 API is untouched (row 2 ✓); lane isolation and the ≤4 budget are git-provable (rows 6, 7 ✓); COND-ARCH-1/2 re-read clean. The single falsified discharge is documentation-class, discovered only by the gate's own re-read rule — precisely what the DDR exists to catch — and does not re-open any frozen decision, so rejection (return to design) would be disproportionate.

**Verdict: approved with conditions**
