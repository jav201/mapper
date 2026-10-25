# Design review record — DDR — mapper — Batch 2026-10-23-hygiene-batch

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

> **SEALED 2026-10-24.** Drafted as-built; the three DDR reviewers re-read every row against the code and the evidence (`evidence/ddr-architect.md`, `evidence/ddr-software-dev.md`, `evidence/ddr-qa.md`). If this record changes after the seal it is a NEW version with a NEW id.

| Field | Value |
|---|---|
| Record id | `DDR-2026-10-23-hygiene-batch` |
| Reviews | `PDR-2026-10-23-hygiene-batch` + lanes **L1/L2a/L2b/L3 joined** (merge + review-findings follow-ups at `a860a27`; gate suite `evidence/p4-full-suite-a860a27-2026-10-24.txt`, sha256 `00652d2c…4bd592`) |
| Participants | PDR: `architect` + `qa-reviewer` + `ux-reviewer` (D1 fired) + `security-reviewer` (C6 fired), each a Kimi K3 subagent (evidence `evidence/recheck-{architect,qa,security,ux}.md`) · DDR: `architect — Kimi K3 subagent executing agents/architect.md · approved with conditions` · `software-dev — Kimi K3 subagent executing agents/software-dev.md · approved with conditions` · `qa-reviewer — Kimi K3 subagent executing agents/qa-reviewer.md · approved` (executed 2026-10-24; evidence `evidence/ddr-architect.md`, `evidence/ddr-software-dev.md`, `evidence/ddr-qa.md`) |
| Date sealed | `2026-10-24` |
| **Verdict** | `approved with conditions` — sealed 2026-10-24; conditions C1/C2 (§C), each individually dischargeable |

---

## A · PDR checklist — preliminary design review

> Rows carried sealed from `PDR-2026-10-23-hygiene-batch` §A (2026-10-23) and re-read at this join; the PDR record is the one home of the reviewers' original evidence, cited per row.

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | Proposal complete: objective · modules and boundaries · diagrams · interfaces that change · **proposed test cases** · risks · rejected alternatives **where a real decision exists**, otherwise `n/a — <the decision already made, and by what>` | ✓ (carried sealed) | `PDR-2026-10-23-hygiene-batch` §A row 1 — `evidence/recheck-architect.md` Row 1 · `evidence/recheck-qa.md` §2 |
| 2 | Respects the boundaries of `docs/ARCHITECTURE.md` | ✓ (carried sealed) | PDR §A row 2 — boundaries respected; N3 discharged at the seal by ruling R8 (re-read at this join: the `diff → osopen` import is barred, pinned by `tests/test_arch_osopen_callers.py`) |
| 3 | **Forward applicability:** every output has a NAMED downstream consumer | ✓ (carried sealed) | PDR §A row 3 — five output rows, every one with a named consumer |
| 4 | Every requirement has foreseen coverage | ✓ (carried sealed) | PDR §A row 4 — 3 US / 6 HLR / 11-12 LLR (m1 corrected 12→11 at P2, then `.7` bound LLR-Q3.1.2's matrix — the live contract holds 12 LLR ids) |
| 5 | Proposed test cases are observable **and non-vacuous** — the reddening mutation is named for each | ✓ (carried sealed) | PDR §A row 5 — every §5 row names its reddening mutation or the move-aside counterfactual; the two n4 positive boundary arms restated at the seal |
| 6 | The gauntlet controls that apply are declared, with who pays for them | ✓ (carried sealed) | PDR §A row 6 — C11 RED counterfactuals declared at authoring time with packet owners |
| 7 | Interfaces **frozen** for the fork are listed | ✓ (carried sealed) | PDR §A row 7 — D1/D2 (§D below), re-verified intact at this join (§B row 2) |
| 8 | Lane plan: file sets disjoint, family-B census run per lane | ✓ (carried sealed, census RE-RUN at this join) | PDR §A row 8 — sets forked L1/L2a/L2b/L3 per ruling R7; the re-run found the B1 miss (§B row 3) |
| 9 | UX lens applied (if family D fired): interaction design reviewed | ✓ (carried sealed) | PDR §A row 9 — F-UX-1 discharged by ruling R7; F-UX-2 fixed at the seal; the AT-114 toast verified live through the running screen at the L2b gate (review m5, `evidence/review-inc004.md`) |
| 10 | Security lens applied (if family C fired) | ✓ (carried sealed) | PDR §A row 10 — S1 was the seal's one carried condition; discharged BOUND at the L2a gate, revised onto the pinned seam at the L2b gate (§B row 8, condition 4) |

**No increment starts without an approved PDR.** *(Held: the PDR was sealed before any lane forked.)*

---

## B · DDR checklist — detailed design review · **and the JOIN point when the batch forked**

| # | Item | ✓/⚠/✗ | Evidence |
|---|---|---|---|
| 1 | What changed against the PDR, **and why** | ✓ | As-built deltas, each ruled: (a) L2 forked into L2a {store, diff, osopen} + L2b {import_csv, screens/home}, `screens/home.py` joining the Q2 lane — ruling R7 answering F-UX-1 (ledger `.9`); (b) R10 measured-truth amendments at the L3 gates — LLR-Q3.1.2's oracle corrected to the 1..h line bound + the exact Layered header-meter spill (`.11`), LLR-Q3.2.3's canvas threshold replaced by the measured per-renderer construction census and the empty-state zero-construction assertion (`.12`/`.13`), the sweep-arm negative control re-named to the M-Q3-1 class; (c) L2a review follow-up — the prescan's anchor name bounded to `ANCHOR_NAME_DISPLAY = 40` (inc003-F1); (d) cross-batch amendment — the three sealed `LLR-N13.1.7` arms re-aimed at the typed refusal (`.14`, ruling R10); (e) L2b review follow-ups — the `_show` decode guard restored behind the pinned seam (inc004-F1) and the non-UTF-8 CSV refusal typed (inc004-F2). No renderer byte changed; no golden re-baselined (LLR-Q3.2.2 held) |
| 2 | Frozen interfaces still intact — or the work returned to the trunk and it is declared | ✓ | **D1** — `Canvas(w, h, tones=(), fallback="", audit=None)` is the shipped signature; the B-44 pin (`tests/test_a3_census.py:658-674`) was amended in the SAME landing as the first audited construction; the three construction sites (`mapper/views/layered.py`, `radial.py`, `lane.py`) pass no sink in production; every byte-pinned digest and the 16 perf render goldens are green in the gate run. **D2** — the osopen bounded reader's name + constants are exactly what `store` and `import_csv` import; the derived allow-list (`tests/test_arch_osopen_callers.py`) was amended in the same landing as the first reader import and now records `import_csv.py` + `screens/home.py`. ⚠ ruled at the DDR (2026-10-24): `store.py` imports SIX osopen names (reader, error, four constants) vs the ARQ commitment's "ONE name" phrasing — the reviewers ruled the derived allow-list is the binding record; the ARQ prose amendment is condition C1 (finding A-DDR-1; §E residual 2) |
| 3 | **Reverse census CROSSED between lanes** (the one check impossible from inside a lane) | ⚠ re-verified, ONE miss found and discharged | Re-run at the seal over the forked sets (proposal §8): crossed matrix ∅ for write hazards; read-only presences named (MapStoreError consumed by `screens/construct.py:57` + `screens/common.py:_save_or_toast`, NOT `app.py`; the load refusals surface through `screens/home.py:169-181` + `screens/map/screen.py:208-215`; `outline.py:311` `no_color=True` is a deliberate renderer pin). **The miss:** the merged lanes' census scoped consumer tests by IMPORT SURFACE and never re-derived by FIXTURE CONTENT — three `tests/test_repair_sidecar.py` arms feed anchor-bearing sidecars through `load`, exactly the class LLR-Q2.1.2 now refuses before compose. Caught by the orchestrator's post-merge full-suite run (3 failed / 3568 passed); discharged by ruling R10 + ledger `.14` + mutant M-Q2-1-XB14. Lesson recorded in increment-003 §Cross-batch follow-up: a rule refusing an input class must re-derive its consumer tests by fixture content |
| 4 | Every `AT-NNN` realises in **exactly one** on-disk node (C-18) | ✓ | AT-108 → `tests/test_colour_always_on.py::test_painted_screen_byte_identical_with_and_without_no_color` · AT-109/110/112/113 → the `test_at_10x_*` arms of `tests/test_ingestion_limits.py` · AT-111 → `::test_at_111_anchor_refused_names_anchor_and_map` + `::test_at_111_alias_refused` (two nodes; the contract declares AT-111 "cited, not declared" because the lowercase `at_111` names sit below the V2 tokenizer — declaring a bare `AT-111` would mint an id no disk token resolves) · AT-114 → `::test_at_114_csv_refusal_toast_shows_the_reason` · AT-115 → `tests/test_scalecheck.py::test_sweep` (roster guard `test_renderer_roster_derived` is its layer-0 unit, not a second realization) · AT-116 → `tests/test_canvas_audit.py::test_events` + `::test_byte_identity` with `::test_sweep_audit_arm` as the live-render arm (one chain, three nodes — the sweep arm asserts the live half, the unit arms the hook half; reconciled in `04-validation.md` Layer B). No AT is satisfied only "in parts" without its named chain |
| 5 | Test ledger **summed** across lanes, reconciled | ✓ | `3546 − 0 + 33 = 3579` — base re-derived on a clean `1609bbe` worktree (3546 collected = 3543 passed + 3 xfailed); D=0 verified at function level (`git diff 1609bbe..a860a27 -- tests/ | grep '^-.*def test_'` → 0); A=33 (31 new defs + 2 parametrized expansions); actual collected 3579 re-verified by collect-only on the gate tree; the gate run passed 3575 with the single failure = the pre-existing flake B-137. Full ledger: `04-validation.md` §Signed-balance |
| 6 | No lane touched another lane's file | ✓ | Per-lane worktrees from the fork; each packet's contamination check clean (`git status` = own files only). The one incident — an unidentified concurrent process edited `tests/test_scalecheck.py` mid-L3-gate (2026-10-23) — is declared in increment-001 §5: the foreign test was removed, all L3 evidence re-captured after the removal, and the trunk commit landed immediately to freeze state. Post-merge review follow-ups (inc003-F1 store.py; inc004-F1/F2 diff.py + osopen.py) ran on the JOINED tree as trunk work, not lane work — the lane disjointness rule binds the fork, and the follow-ups each stayed ≤4 files with the reason declared in the packet |
| 7 | Source-file budget: any lane that reached or exceeded 4, reviewed here | ✓ | At the fork every lane was AT budget, none over: L1 = 1 (`app.py`), L2a = 3 (store, diff, osopen), L2b = 2 (import_csv, screens/home), L3 = 1 (`canvas.py`). **Over-budget landing reviewed:** the L2b increment's commit touched 5 source files — its own 2 plus the declared L2a-revision 3 (`diff.py`, `store.py`, `osopen.py`) — the lane union equals the C-52 L2 set exactly; the over-4 reason (L2a deliverables revised at the L2b gate by pre-existing pins: the S1 mechanism moved onto the `subprocess.run` seam pinned by `tests/test_inc9h.py`, and the reader's universal-newline parity fix) is declared in increment-004 §2/§5 and accepted at its gate |
| 8 | **Every open PDR condition discharged one by one, by RE-READING the artifact** | ✓ | See the conditions table below — each discharged by reading the artifact that was supposed to change, never by trusting the corrective pass |

**A conditional verdict is not an authorisation.** Each condition below is discharged by reading the
artifact that was supposed to change — not by trusting that the corrective pass ran.

| # | Condition left open at PDR | Discharged? | The artifact line that proves it |
|---|---|---|---|
| 1 | C-52 condition 3 — crossed reverse census per lane and shared, before the fork | yes — and re-read here with the B1 miss recorded (§B row 3) | proposal §8 census block (executed 2026-10-23, verdict "lanes may fork after the seal"); the miss discharged via `LED-2026-10-23-hygiene-batch.14` + `evidence/xbatch14-{red,green,mutant}-2026-10-24.txt`; the fixture-content lesson recorded in increment-003 §Cross-batch follow-up |
| 2 | N3 (architect, minor) — proposal §2 `diff` row readable as licensing a third `diff → osopen` edge | yes — re-read: the row bars the import; capped reads reach `diff` only through `store`'s `_prescan_sidecar` over the existing `diff → store` edge (`mapper/diff.py:11`); pinned by `tests/test_arch_osopen_callers.py` (ruling R8) | proposal §2 `diff` row; `mapper/diff.py:11`; the gate run keeps the pin green |
| 3 | F-UX-1 (ux, major) — the CSV refusal toast showed only `type(e).__name__`, and the fixing file (`mapper/screens/home.py`) was owned by no lane | yes — re-read: ruling R7 joined `screens/home.py` to the Q2 lane and forked L2; the typed branch now shows the refusal's own `str(e)` (path-free per C6) at `mapper/screens/home.py:524-541`, the generic branch keeps `type(e).__name__`; AT-114 observed through the running screen (review m5); mutant M-Q2-5 reddens the arm | `mapper/screens/home.py:524-541`; `tests/test_ingestion_limits.py::test_at_114_csv_refusal_toast_shows_the_reason`; `evidence/l2b-mutation-battery-2026-10-23.txt`; ledger `.9` |
| 4 | S1 (security, LOW) — the diff-side `git show` capture was a full in-memory read before any cap | yes — re-read, decision **BOUND**, and the mechanism revised once: at the L2a gate (ruling R9) the capture became a streamed read aborting past `MAX_MAP_BYTES + 1` → `None` (increment-003 §5); at the L2b gate the mechanism moved onto the `subprocess.run` seam pinned by `tests/test_inc9h.py` — the captured text now passes the byte-length refusal inside `store._capped_side_graph` (increment-004 §5) — after the seam pin was found to forbid the Popen form. Both forms degrade an oversize/hostile HEAD object to "no diff" (`None`) with zero interface change; the revision was forced by a pre-existing pin, declared, and the seam re-verified green | increment-003 §5 · increment-004 §5; `tests/test_ingestion_limits.py::test_diff_side_oversize_head_yields_none`; `tests/test_diff.py::test_git_diff_undecodable_head_object_returns_none_quietly`; `evidence/fu-inc004-f1-decode-guard-{red,green,mutant}-2026-10-24.txt` |
| 5 | N1, N2 (architect) · n1–n4 (qa) · F-UX-2 (ux) — second-pass record drift | yes — fixed in the trunk records at the seal (2026-10-23); re-read here: N1 prescan figure, N2 premise-5 citation, n1/n2 threshold texts, n3 → M-Q3-4 minted (ledger `.10`), n4 positive arms restated, F-UX-2 load surfaces named | the artifact lines cited in the PDR §B row 5; the gate run keeps every cited pin green |
| 6 | L2a/L2b test sequencing — `tests/test_ingestion_limits.py` (L2a-owned) carries the AT-114 screen arm, which asserts L2b's toast wording | yes — re-read: the arm was expected-RED through the fork and turned green only after L2b landed; the gate run (post-merge) keeps it green; L2b owns no test file by design | increment-003 §5 expected-RED declaration; increment-004 gate; `evidence/p4-full-suite-a860a27-2026-10-24.txt` |

---

## C · Verdict and what it means

- **Verdict: `approved with conditions` — sealed 2026-10-24.** architect · approved with conditions; software-dev · approved with conditions; qa-reviewer · approved (evidence `evidence/ddr-architect.md`, `evidence/ddr-software-dev.md`, `evidence/ddr-qa.md`). Four findings, all MINOR — none touches behaviour or a frozen interface:

  | Id | Severity | Where | Finding |
  |---|---|---|---|
  | A-DDR-1 | MINOR | `docs/ARCHITECTURE.md:65,:162,:165,:170` | the ARQ prose "each importing ONE name" is falsified as-built — `mapper/store.py:16-23` imports SIX osopen names; the AST-derived allow-list binds, the prose needs a record amendment |
  | A-DDR-2 | MINOR | `tests/test_arch_osopen_callers.py:101` vs `:114` | duplicate `"screens/home.py"` key in the `ALLOWED_OUTSIDE_APP` literal; the first entry is dead (silently overwritten) |
  | F-SD-1 | MINOR | `mapper/screens/home.py:533-534` | the comment promises a `LEAK_EXCEPTIONS` registry entry "owed at the trunk join", but the entry is impossible by construction (`tests/test_inc9c.py:315-322` reddens any key the census doesn't produce); the inline declaration is the only valid carry |
  | QA-DDR-1 | MINOR | `01-requirements-ledger.md:107` | ledger `.14` names the M-Q2-1-XB14 surplus RED arms "AT-111/112"; the transcript's surplus is AT-111×2 + `test_diff_side_anchor_head_yields_none` — wording nit; the catch on the three amended arms is proven |

- **Conditions (each individually dischargeable, re-read at the next gate):**
  - **C1** (from A-DDR-1): ✅ **DISCHARGED at the trunk join — commit `78d51a2`** (local `feat/hygiene-batch`, never pushed). `docs/ARCHITECTURE.md:65` and the §3 `store` / `import_csv` / `osopen` rows now state the measured as-built sets (`store`: six names; `import_csv`: two); the derived allow-list remains the binding record. Record amendment only — no code change.
  - **C2** (from F-SD-1): ✅ **DISCHARGED at the trunk join — commit `78d51a2`.** The carry is recorded as the inline declaration and the `mapper/screens/home.py` comment is reworded to state why a registry entry is impossible by construction: `_leaky` never flags `refusal`, so the census never yields the key and the staleness check would redden on arrival. Comment-only.
  - A-DDR-2's duplicate-key cleanup: ✅ DONE in commit `78d51a2` (the dead `"screens/home.py"` key removed; the live entry keeps the union). QA-DDR-1: ✅ corrected in the same commit — ledger `.14` now names the actual M-Q2-1-XB14 surplus arms (AT-111 ×2 + `test_diff_side_anchor_head_yields_none`, 6 failed / 32 passed).
- **Rulings on the open points the draft handed the reviewers:**
  1. **The B1 census miss (§B row 3)** — qa-reviewer re-derived the class by fixture content: **closed**; the only other anchor-bearing fixtures feed the reqharness's own loaders, not `MapStore.load`, and already assert refusal (`evidence/ddr-qa.md` §Fixture-content re-derivation). Whether C-52 condition 3's template text should mandate the fixture-content pass is a post-mortem lesson candidate, not a batch condition.
  2. **The osopen import-name census (§B row 2 / §E residual 2)** — ruled: **the derived allow-list is the record that binds**; the ARQ prose amendment rides as C1.
  3. **The S1 mechanism revision (condition 4)** — confirmed: the seam-pinned `subprocess.run` form is the accepted one (the inc9h pin forbids the Popen form); `None`-on-error covers every pre-existing caller (sole production caller `painting.py:731-734` handles it). D3 seals as written.
  4. **The `LEAK_EXCEPTIONS` carry (increment-004 §6)** — ruled: **inline declaration**, not a registry entry (the entry would be self-reddening); C2 carries the comment rewording.
  5. **The residual risks (§E)** — qa-reviewer: accept risks 1, 3, 4, 5, 6 as recorded; risk 2 is amended by the open-point-2 ruling.
- The seal binds §D below; the batch proceeds to P5/P6 on the strength of the P4 record (`04-validation.md`, PASS-WITH-NOTES).

## D · Ids this record binds *(the glue of the repo ↔ vault split)*

| This record's decision | Id | Where it lands in the **repo** |
|---|---|---|
| D1 — frozen interface (carried from the PDR, verified intact): `Canvas(w, h, tones=(), fallback="", audit=None)`; `put` audits `clip` and `overprint` (both cells alphanumeric and different — ruling R4); 3 construction sites pass nothing | `PDR-2026-10-23-hygiene-batch#D1` | `docs/ARCHITECTURE.md` §4 canvas rows + the B-44 pin at `tests/test_a3_census.py:658-674` (LLR-Q3.2.1, ledger `.4`/`.8`/`.10`) |
| D2 — frozen interface (carried from the PDR, verified intact): the osopen bounded content reader's public name + constants (`MAX_MAP_BYTES`, `MAX_DEPTH`, `MAX_NODES`, `MAX_EDGES`, `MAX_FILE_BYTES`, `BINARY_PROBE_BYTES`); imported by `store` + `import_csv` (+ `screens/home.py`'s existing osopen entry) only | `PDR-2026-10-23-hygiene-batch#D2` | `docs/ARCHITECTURE.md` §3 osopen row + R-015's freeze note + the derived allow-list at `tests/test_arch_osopen_callers.py` (HLR-Q2.2 / LLR-Q2.2.1, ledger `.2`/`.6`/`.9`) |
| D3 — S1 BOUND, seam-pinned form: the diff-side `git show` capture is capped (`MAX_MAP_BYTES + 1`) on the `subprocess.run` seam pinned by `tests/test_inc9h.py`; oversize/hostile/undecodable HEAD objects degrade to `None` | `DDR-2026-10-23-hygiene-batch#D3` | `mapper/diff.py:33` (`_show`) + the byte-length refusal in `store._capped_side_graph`; asserted by `tests/test_ingestion_limits.py::test_diff_side_*` and `tests/test_diff.py::test_git_diff_undecodable_head_object_returns_none_quietly` |
| D4 — LLR-N13.1.7 SUPERSEDED IN PART by LLR-Q2.1.2's typed early refusal (ruling R10, 2026-10-24): the intent "nothing amplified is ever materialised; the message names coordinates, never values" is discharged at the prescan; the rest of N13.1.7 (non-anchor repair-path records) is untouched and stays owned by the sealed batch `2026-08-26-ui-next-batch-02`; its three B1 arms are amended in place, names unchanged, value-leak bounds kept as message-size negatives | `DDR-2026-10-23-hygiene-batch#D4` | ledger `LED-2026-10-23-hygiene-batch.14`; `tests/test_repair_sidecar.py` (three amended arms); mutant M-Q2-1-XB14 |

**What decides code lands in the repo.** A decision that fixes an interface does not stay only in the
vault: it is reflected in the requirement or in the module map, which are versioned beside the code.

## E · Residual risks recorded at the join

1. **Prescan cost +3.54 s on the 12,000-node perf shape** (measured at the L2a gate: median full load 8,509 ms, prescan pass 3,540 ms = 41.6%; real maps ≤ 8 nodes pay ~0). Backlog candidate (CSafeLoader / scanner-only prescan) if a real map ever approaches the perf shapes — deliberately not a B-row yet per the increment's own threshold; revisit at the first real-map complaint.
2. **`store.py` imports six osopen names** where the ARQ commitment anticipated one — ruled at the DDR (2026-10-24): the derived allow-list is the binding record; the ARQ prose amendment rides as condition C1 (finding A-DDR-1).
3. **The AT-114 screen arm's fixed `pilot.pause()` cadence** — the poll-with-deadline robustness fix was deliberately not applied mid-batch; carried as B-139 with the two transient flakes.
4. **The gate run's single failure** — `test_changed_size_or_mtime_takes_full_path`, a pre-existing flake reproduced 1/6 on master; B-137. No batch arm's verdict rests on it (P-05), but the next batch's counterfactuals touching that file must re-derive per B-137's note.
5. **`OutlineRenderer`'s dangling-edge crash** (`mapper/views/outline.py:214-218`) — latent, no shipped parser route reaches it; B-138.
6. **Dim-text audit events** — out of the v1 event set by ruling R4; B-136. The `put`-path inheritance means a later `dim` kind lands without an interface change.
