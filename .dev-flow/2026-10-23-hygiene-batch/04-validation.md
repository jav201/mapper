# Validation — mapper — Batch 2026-10-23-hygiene-batch

> **Artifact language:** canonical English scaffold. Generate in the batch's development language (`state.json` `language`); for Spanish batches **translate the prose, never a label** — the reserved field names are declared in §✅ Verdict and are read literally.
> Phase 4 artifact. Content owner: `qa-reviewer`, who **EVALUATES** the results of the validation strategy fixed in Phase 1, **names who executed each one** and returns the rows; the orchestrator writes `04-validation.md` (`stations/shared-homes-roles.md` §Delegation). The ONE complete gate-suite run is the orchestrator's (`C-25`); a sub-agent consumes the result and never owns the run.

> **Owed in.** `core` ✓ · `full` ✓

> **Field guide:** `templates/guides/validation-template.md` explains each field below and the rules that read it. It ships with the flow and is not copied into this batch.

**`Mode`:** `validation`

## ✅ Verdict (read first)

> **Reserved field names.** The **field names and block keywords below are language-independent** — the
> validator parses them literally and they are never translated:
> `Result` · `Gate run` · `Layer 0` · `Evidence checklist` · `⏸ DEFER`
> Everything else on this page — headings, guidance, the prose in every cell — is translated with the batch.
> **One strategy, not two:** the flow ships no alias table, so a translated label is read as an ABSENT one and the rule keyed on it reports a true-sounding silence.
> **And one FLOW-WIDE reserved token, read out of this artifact by `V42` no matter which template minted it:** `⏸ DEFER`. It is a MARKER rather than a field name, which is why it is stated here *and* in `/dev-flow` §Language of artifacts rather than in a per-template list — a deferral can be written in any batch artifact, including the ones that carry no block at all.
>
> **And so are the three verdict tokens** `PASS` · `PASS-WITH-NOTES` · `FAIL`, which are VALUES and not prose.
> A Spanish batch writes `- **Result:** PASS`, not `- **Resultado:** aprobado`: the label, the tokens and the
> reviewer-identity tokens below are the machine's vocabulary.

- **Result:** PASS-WITH-NOTES
- **Gate run:** `PYTHONIOENCODING=utf-8 env -u NO_COLOR -u TERM python -m pytest -q` (the full suite; `pyproject.toml` addopts deselect the 24 slow/network-marked tests) · exit 1 — 3575 passed, 1 failed, 24 deselected, 3 xfailed, in 1858 s · run on commit `a860a27` (transcript committed as `201646c`, records only) · executed and collected by the **orchestrator** (C-25). Transcript `evidence/p4-full-suite-a860a27-2026-10-24.txt`, sha256 `00652d2c153988baa173cd3f9f9d96ccdfa4cfb23c5ece0ac136490ca94bd592` (verified against the file on disk at P4).
- **Layer 0:** 8 unit(s) met the criterion · 8 carry a named reddening mutation
- **Requirements:** 18/18 pass · 0 blocker fails
- **Black-box acceptance (Layer B):** ✓ every story's `AT` observes its outcome through the shipped surface (boundary + negative)
- **Surface-reachability (bidirectional):** ✓ all named inputs AND outputs/deliverables reached/observed at the surface · 0 gaps
- **Supersession inspection (read off the P3 packets):** ✓ all surviving refs negative — LLR-N13.1.7's partial supersession re-read (ledger `.14`); the 171-failure transcript `full-suite-after-merge-2026-10-23.txt` is SUPERSEDED (worker-shell environment artefact: `NO_COLOR`/`TERM` exported — see Detail)
- **Test ledger:** ✓ reconciles (`3546 − 0 + 33 = 3579`)
- **Evidence checklist (qa-reviewer):** qa-reviewer evaluation returned by the dev-flow worker under the standing authorization (runtime absence: no named reviewer sub-agents on this runtime — PLAN.md §Gate notices) · 10 of 10 rows ✓ with evidence

> The one failed arm is `tests/test_reqharness_cache_fastpath.py::test_changed_size_or_mtime_takes_full_path` — a PRE-EXISTING flake untouched by this batch: reproduced 1/6 runs on master `1609bbe` by the orchestrator. Disposition: BACKLOG **B-137**; per `P-05` no batch arm's verdict rests on it. Everything the batch touched passed.

---

## Detail (reference)

### Layer 0 — unit

| Unit | Which criterion | Node id | Result |
|---|---|---|---|
| `NO_COLOR` neutralised at construction | env removed before the Textual base constructor; no Monochrome filter after construction with the var set | `tests/test_colour_always_on.py::test_no_color_removed_before_super` | pass |
| Byte cap on map files (stat + re-read) | both the stat path and the grow-between-stat-and-read path refuse naming the byte limit and the map id; cap−1 loads | `tests/test_ingestion_limits.py::test_at_109_byte_cap_stat_refuses_and_names_limit_and_map` · `::test_at_109_byte_cap_grow_between_stat_and_read_refuses` · `::test_at_109_text_map_at_byte_cap_minus_1_loads` | pass |
| Prescan refuses anchors/aliases/depth, iteratively | depth-64 parses; anchor, alias and depth-65 refuse naming the cause; 10,000-deep refuses < 5 s without `RecursionError`; anchor name in the message bounded (`ANCHOR_NAME_DISPLAY = 40`) | `tests/test_ingestion_limits.py::test_at_111_anchor_refused_names_anchor_and_map` · `::test_at_111_alias_refused` · `::test_at_111_anchor_name_in_refusal_is_bounded` · `::test_at_110_depth_64_parses` · `::test_at_110_depth_65_refuses_naming_depth_limit` · `::test_at_110_deep_10000_refuses_fast_without_recursion_error` | pass |
| Node/edge count caps | 100,001 nodes / 100,001 edges refuse naming the count; exactly-at-cap parses | `tests/test_ingestion_limits.py::test_at_112_node_count_cap_plus_1_refuses` · `::test_at_113_edge_count_cap_plus_1_refuses` · `::test_count_caps_exactly_at_cap_pass` | pass |
| Bounded content read (byte cap + NUL probe + UTF-8) | CSV at 4 MiB±1; NUL at byte 0 and at byte 8,191 refuse as binary; NUL past the 8 KiB probe window is NOT refused by the probe (documented bound); non-UTF-8 refuses typed naming the reason | `tests/test_ingestion_limits.py::test_csv_*` (7 arms) | pass |
| Diff-side bounded capture | a `git show` object past `MAX_MAP_BYTES + 1`, or carrying an anchor, degrades to `None` (no unbounded in-memory read) | `tests/test_ingestion_limits.py::test_diff_side_oversize_head_yields_none` · `::test_diff_side_anchor_head_yields_none` · `::test_diff_side_clean_head_still_diffs` · `tests/test_diff.py::test_git_diff_undecodable_head_object_returns_none_quietly` | pass |
| Renderer roster derived from code | the sweep's subject set resolves from `mapper.views.__all__` to exactly 6; the completeness guard fails loudly on an empty/short roster | `tests/test_scalecheck.py::test_renderer_roster_derived` | pass |
| Canvas audit hook (events + byte identity) | injected clip/overprint recorded with exact `(x, y)`; space-writes and old-alnum→space record nothing; `rows()` byte-identical with vs. without the sink | `tests/test_canvas_audit.py::test_events` · `::test_byte_identity` · `::test_text_and_wire_paths_share_put_and_default_sink_is_none` | pass |

**Measured by mutation, never by line coverage.** For each unit, name the mutation and paste the RED:

| Unit | Mutation applied | RED observed? | Transcript |
|---|---|---|---|
| Q1 unit + black-box | M-Q1-1 — the `NO_COLOR` neutralisation deleted | ✓ (`test_colour_always_on.py` arms RED; painted segments desaturated in the black-box arm) | `evidence/l1-red-2026-10-23.txt` · `evidence/l1-mutation-battery-2026-10-23.txt` · move-aside `evidence/l1-move-aside-2026-10-23.txt` |
| Byte cap | M-Q2-2 — the capped re-read re-check removed | ✓ (grow-between-stat-and-read arm RED) | `evidence/l2a-mutation-battery-2026-10-23.txt` |
| Prescan | M-Q2-1 — the prescan bypassed | ✓ (anchor/alias arms RED; diff-side anchor arm RED) | `evidence/l2a-mutation-battery-2026-10-23.txt` |
| Count caps | M-Q2-4 — the count check removed | ✓ (asserting mutant for ledger `.1`/`.5`) | `evidence/l2a-mutation-battery-2026-10-23.txt` |
| Content read | M-Q2-3 — the NUL probe removed | ✓ | `evidence/l2b-mutation-battery-2026-10-23.txt` |
| CSV toast | M-Q2-5 — the toast reverts to type-name-only | ✓ (AT-114 screen arm RED — the reason no longer reaches the operator) | `evidence/l2b-mutation-battery-2026-10-23.txt` |
| Cross-batch prescan consumer | M-Q2-1-XB14 — the anchor-refusal block in `_prescan_sidecar` replaced by `pass` | ✓ (the three amended `LLR-N13.1.7` arms RED on the old repair path) | `evidence/xbatch14-mutant-2026-10-24.txt` |
| Sweep geometry | M-Q3-1 — a renderer taught to emit h+1 lines | ✓ (the sweep names renderer+size) | `evidence/l3-mutation-battery-2026-10-23.txt` |
| Audit events | M-Q3-2 — event append removed · M-Q3-4 — the alphanumeric gate dropped | ✓ (event-set / second-limb arms RED) | `evidence/l3-mutation-battery-2026-10-23.txt` |
| Byte identity | M-Q3-3 — the sink allowed to touch the buffer | ✓ | `evidence/l3-mutation-battery-2026-10-23.txt` |
| Follow-up fixes | inc003-F1 anchor-name truncation reverted · inc004-F1 decode guard dropped · inc004-F2 typed-UTF-8-refusal dropped | ✓ each (restore hash-proven) | `evidence/fu-inc003-f1-anchor-bound-{red,green,mutant}-2026-10-24.txt` · `evidence/fu-inc004-f1-decode-guard-{red,green,mutant}-2026-10-24.txt` · `evidence/fu-inc004-f2-utf8-refusal-{red,green,mutant}-2026-10-24.txt` |

### UX walkthrough — only if trigger family D fired

Family **D fired (D1)** — the ux lens stood at the PDR (`evidence/recheck-ux.md`) and at the L2b increment gate (UX lens on AT-114, `evidence/review-inc004.md`).

| Criterion (when the user does X, they observe Y) | Driven with the REAL mechanism | Painted result asserted | Verdict |
|---|---|---|---|
| The shell exports `NO_COLOR=1` (or sets it empty / to an arbitrary value) and the operator opens any screen → the screen paints with the same colour styles as a run without the variable, byte-equal | the running `MapperApp` headless through Textual's `run_test()` Pilot — the same surface the operator watches | painted-segment styles harvested from the probed screens; byte-equality with the no-var rendering asserted (AT-108) | pass |
| The operator picks a CSV that is over the cap / binary / not UTF-8 → the home screen's import refusal toast shows the authored reason (not just the exception type name), path-free, and the session continues | the running home screen driven by Pilot; `preview_csv` invoked through the real key path | the toast text asserts the refusal's own message (`str(e)` for typed refusals; the generic `OSError` branch keeps `type(e).__name__` per ruling R7) | pass |

**Mechanism used:** a UI test driver (Textual Pilot headless through `run_test()`)

| Act | What it is | Performed? |
|---|---|---|
| Automated walkthrough | the criteria above, driven through the REAL mechanism | performed — AT-108 arm (`tests/test_colour_always_on.py::test_painted_screen_byte_identical_with_and_without_no_color`) and the AT-114 screen arm (`tests/test_ingestion_limits.py::test_at_114_csv_refusal_toast_shows_the_reason`); transcripts `evidence/l1-green-2026-10-23.txt`, `evidence/l2b-green-2026-10-23.txt` |
| Expert inspection | a cognitive walkthrough against declared criteria, by a reviewer and not a user | performed — ux-reviewer lens at the PDR (`evidence/recheck-ux.md`, F-UX-1/F-UX-2 discharged by rulings R7/R8) and the increment-004 UX lens on the AT-114 toast |
| Evaluation with users | real users of the system, doing the tasks named in the context of use | not performed — no user population beyond the operator-author (a one-person team on a developer tool); recorded as a limit, not a silence |

- **Method:** scripted Pilot drives at 118×34 through the real app constructor and the real home-screen import path; painted frames captured after `pilot.wait_for_scheduled_animations()` so stable pixels are compared, not a time-varying blend.
- **Participants or population:** none beyond the authoring operator — no PII recorded.
- **Evidence of the evaluation:** `evidence/l1-green-2026-10-23.txt` · `evidence/l2b-green-2026-10-23.txt` · `evidence/recheck-ux.md` · `evidence/review-inc004.md`.
- **Limits:** two criteria, one terminal size, one driver; no real users; the operator wrote the tasks. What it establishes: the shipped surface renders colour under `NO_COLOR` and carries the refusal reason to the operator. What it does NOT: multi-size visual judgement, learnability, any user other than the author.

### Layer A — functional (white-box): per-requirement results
> `TC-NNN` ↔ LLR/HLR. `Result` = pass / fail. `Evidence` = command output, observed behavior, inspection note, or analysis result.
> Executors: **orchestrator** = the one gate-suite run (transcript cited per row as `p4-full-suite`); **lane workers** = the targeted increment-gate runs; **reviewers** = the independent review subagents named in the increment packets.

| Req | Method | Executed verification | Numeric threshold | Result | Evidence |
|-----|--------|-----------------------|-------------------|--------|----------|
| HLR-Q1.1 | test | `tests/test_colour_always_on.py` (unit + painted-screen arms), orchestrator's gate run + `evidence/l1-green-2026-10-23.txt` | `NO_COLOR=1` set → 0 desaturated painted segments on the probed screens; rendered styles byte-equal to the no-var run | pass | p4-full-suite (3575 passed) · `l1-green` · mutant M-Q1-1 RED in `l1-mutation-battery` |
| HLR-Q2.1 | test | `tests/test_ingestion_limits.py` load arms (bytes, depth, anchors/aliases, counts) + `tests/test_diff.py` | 5 refusal kinds each refuse naming the limit; 0 crashes/hangs (10,000-deep attempt refuses, never `RecursionError`); under-cap fixtures load unchanged | pass | p4-full-suite · `l2a-green-2026-10-23.txt` · batteries RED per mutation |
| HLR-Q2.2 | test | `tests/test_ingestion_limits.py::test_csv_*` (7 arms) through `preview_csv` | oversize CSV refused naming the cap; NUL-bearing refused as binary; cap−1 imports unchanged; non-UTF-8 refused typed | pass | p4-full-suite · `l2b-green-2026-10-23.txt` · `fu-inc004-f2-utf8-refusal-green` |
| HLR-Q2.3 | inspection + test | PDR id→file census re-run at the Q2 gate (site list in `design/design-proposal.md` §5); existing refusal arms in the gate run | 0 unguarded id→file sites; `BAD_NAMES`/`DEVICES` refusal arms green | pass | p4-full-suite (`test_seed_safety.py`, `test_inc9n.py`, `test_en4.py`, `test_seed2.py` arms) · census record proposal §5 |
| HLR-Q3.1 | test | `tests/test_scalecheck.py::test_sweep` + roster guard | 6 renderers × 5 sizes × 4 recorded states = 120 assertions, 0 misfits; failures name renderer+size+state | pass | p4-full-suite · `l3-green-2026-10-23.txt` · measurement probe `l3-sweep-measurement-probe` |
| HLR-Q3.2 | test | `tests/test_canvas_audit.py` + `tests/test_scalecheck.py::test_sweep_audit_arm` | clip/overprint recorded with exact `(x, y)`; `rows()` identical with vs. without the sink; 0 unexplained events on the 120-combo matrix | pass | p4-full-suite · `l3-green` · batteries |
| LLR-Q1.1.1 | test (unit) | `tests/test_colour_always_on.py::test_no_color_removed_before_super` (parametrized set / set-empty / arbitrary) | after construction with the var set: `"NO_COLOR" not in os.environ`; no Monochrome filter | pass | p4-full-suite · `l1-green` · M-Q1-1 |
| LLR-Q2.1.1 | test (unit) | `tests/test_ingestion_limits.py::test_at_109_*` (3 arms) | stat-oversize and grow-between refuse; cap−1 loads | pass | p4-full-suite · `l2a-green` · M-Q2-2 |
| LLR-Q2.1.2 | test (unit) | `tests/test_ingestion_limits.py::test_at_111_*` · `test_at_110_*` (6 arms) | anchor/alias/depth-65 refuse naming the cause; depth-64 parses; 10,000-deep refuses < 5 s; anchor name in the message ≤ 40 chars + ellipsis | pass | p4-full-suite · `l2a-green` · `fu-inc003-f1-anchor-bound-green` · M-Q2-1 / M-Q2-1-XB14 |
| LLR-Q2.1.3 | test (unit) | `tests/test_ingestion_limits.py::test_at_112_*` · `test_at_113_*` · `test_count_caps_exactly_at_cap_pass` | 100,001/100,001 refuse naming the count; at-cap parses | pass | p4-full-suite · `l2a-green` · M-Q2-4 |
| LLR-Q2.2.1 | test (unit) | `tests/test_ingestion_limits.py::test_csv_*` | cap±1; NUL at byte 0 and byte 8,191 refuse; documented probe-window bound; typed UTF-8 refusal | pass | p4-full-suite · `l2b-green` · `fu-inc004-f2` · M-Q2-3 |
| LLR-Q2.3.1 | inspection | census record `design/design-proposal.md` §5 (grep-derived site list, each with its guard); re-run + diffed at the Q2 gate | 0 unguarded sites; list derived from code, not memory | pass | proposal §5 census row; `l2a-green` / `l2b-green` |
| LLR-Q3.1.1 | test (unit) | `tests/test_scalecheck.py::test_renderer_roster_derived` | derived roster == 6; empty/<6 fails the guard (no vacuous pass) | pass | p4-full-suite · `l3-green` |
| LLR-Q3.1.2 | test (integration) | `tests/test_scalecheck.py::test_sweep` | 120 assertions per the recorded state matrix; line bound 1..h; width ≤ w per line with Layered's header meter spill asserted exactly `(w−2)+cell_len('{n} nodes')`; empty state asserts the documented short-circuit | pass | p4-full-suite · `l3-green` · probe `l3-sweep-measurement-probe` · ruling R10 (ledger `.11`) |
| LLR-Q3.2.1 | test (unit) | `tests/test_canvas_audit.py::test_events` (+ `test_text_and_wire_paths…`) | clip at `(w, 0)` recorded once; overprint recorded; space-writes record nothing; second limb: the written char must be alphanumeric (M-Q3-4) | pass | p4-full-suite · `l3-green` · M-Q3-2 / M-Q3-4 |
| LLR-Q3.2.2 | test (unit) | `tests/test_canvas_audit.py::test_byte_identity` + the unchanged golden/digest suites in the gate run | identity over the fixed write corpus; 0 golden/digest failures attributable to the hook | pass | p4-full-suite (`test_repair_depth.py` digests, `test_perf_paint_clip.py` goldens, `test_a3_census.py` B-44 pin) · M-Q3-3 |
| LLR-Q3.2.3 | test (integration) | `tests/test_scalecheck.py::test_sweep_audit_arm` | ≥1 audited canvas per non-empty render for the 3 constructing renderers; zero-construction asserted for the 3 direct-composition renderers AND the empty short-circuit; 0 unexplained events | pass | p4-full-suite · `l3-green` · census per ledger `.12`/`.13` |

### Layer B — behavioral (black-box) acceptance

| US | Acceptance test (`AT-NNN`) | Surface driven | Deliverable observed (path / element) | repr · boundary · negative | Result |
|----|----------------------------|----------------|---------------------------------------|----------------------------|--------|
| US-Q1-001 | AT-108 | the running app (`MapperApp` via `run_test()`), headless | painted-screen style capture; byte-equal with vs. without `NO_COLOR=1` | repr: normal screen paints · boundary: var set / set-empty / arbitrary value (parametrized) · negative: M-Q1-1 → every segment desaturated | pass |
| US-Q2-001 | AT-109 | `MapStore.load` → typed refusal | `MapStoreError` naming the byte limit and the map id; session continues | boundary: cap−1 loads / cap refuses · negative: grow-between-stat-and-read refuses | pass |
| US-Q2-001 | AT-110 | `MapStore.load` → typed refusal | refusal naming the depth limit | boundary: depth 64 parses / 65 refuses · negative: 10,000-deep refuses < 5 s, no `RecursionError` | pass |
| US-Q2-001 | AT-111 (cited, not declared — realized as two on-disk nodes whose lowercase `at_111` names the V2 tokenizer cannot harvest; declaring a bare `AT-111` would mint an id no disk token resolves) | `MapStore.load` → typed refusal | refusal naming the anchor and the map id, never the amplified value; alias refused; anchor name bounded | boundary: anchor/alias refused · negative: 5,000-char anchor name truncated to 40 + `…` (value bounded) | pass |
| US-Q2-001 | AT-112 | `MapStore.load` → typed refusal | refusal naming the node count | boundary: exactly-at-cap parses / cap+1 refuses | pass |
| US-Q2-001 | AT-113 | `MapStore.load` → typed refusal | refusal naming the edge count | boundary: exactly-at-cap parses / cap+1 refuses | pass |
| US-Q2-001 | AT-114 | the home screen's CSV-import toast (`mapper/screens/home.py`) driven by Pilot through `preview_csv` | the toast shows the authored refusal reason (`str(e)` — path-free per C6) for typed refusals; the generic `OSError` branch keeps `type(e).__name__` | repr: a valid CSV imports · boundary: cap±1 · negative: NUL/binary and non-UTF-8 refuse with the reason named | pass |
| US-Q3-001 | AT-115 | the shipped renderer roster (`mapper.views`), exercised exactly as screens and export consume it | the sweep result: 6 × 5 × 4 = 120 combos fit the budget; on failure the renderer+size+state is named | boundary: min 80×24 / max 200×50 sizes × plain/folded/empty/orphan states · negative: M-Q3-1 names the broken renderer | pass |
| US-Q3-001 | AT-116 | `Canvas` as consumed by the renderers + the sweep's audited render | audit mapping holding the injected `(x, y)` defects; `rows()` byte-identical to a sinkless run | boundary: `(w−1, h−1)` writes / `(w, h)` clips; space-overwrite is NOT an overprint · negative: M-Q3-2 / M-Q3-3 redden the arms | pass |

### Bidirectional surface-reachability matrix (extends A-5)
> Every named INPUT dimension AND every named OUTPUT/deliverable is exercised/observed through the handler — not only the service API.

| Direction | US dimension / deliverable | Service param / producer | Reached/observed at surface? | TC / AT | Status |
|-----------|---------------------------|--------------------------|------------------------------|---------|--------|
| input | `NO_COLOR` env var (set / set-empty / arbitrary) | `MapperApp.__init__` env removal | yes — through the running app | AT-108 · `test_no_color_removed_before_super` | ✓ |
| input | map-file bytes (stat + content) | `MapStore.load` capped read | yes — through `load` and the diff-side `_show` | AT-109 · `test_at_109_*` · `test_diff_side_*` | ✓ |
| input | YAML nesting depth | prescan event stream | yes — depth 64/65 and 10,000-deep | AT-110 · `test_at_110_*` | ✓ |
| input | YAML anchors / aliases | prescan first-event refusal | yes — anchor, alias, bounded anchor name | AT-111 · `test_at_111_*` | ✓ |
| input | node / edge counts | post-parse graph census | yes — cap and cap+1 both ways | AT-112 · AT-113 | ✓ |
| input | CSV bytes / NUL probe / UTF-8 validity | `read_capped` via `preview_csv` | yes — through the operator's import path | AT-114 · `test_csv_*` | ✓ |
| input | Windows device-name ids | `check_map_id` / `osopen.safe_local_path` | yes — existing `BAD_NAMES`/`DEVICES` arms in the gate run | HLR-Q2.3 census · `test_seed_safety.py` · `test_inc9n.py` | ✓ |
| input | renderer graph × state × size | the derived roster over SIZES × the recorded state matrix | yes — the sweep drives all six renderers | AT-115 · `test_sweep` | ✓ |
| input | canvas write sequences (in-bounds, out-of-bounds, overprint, space) | `Canvas.put` with an injected sink | yes — unit corpus + live sweep render | AT-116 · `test_events` | ✓ |
| output | painted screens carrying colour | `MapperApp` render | yes — painted-segment harvest, byte-equal regimes | AT-108 | ✓ |
| output | load-refusal toast naming limit + map id | `MapStoreError` handling in the screens (`mapper/screens/home.py:169-181`, `mapper/screens/map/screen.py:208-215`) | yes — refusal text asserted; path-free per C6 | AT-109…AT-113 | ✓ |
| output | CSV refusal toast with the reason | `mapper/screens/home.py:524-541` | yes — toast text asserted through the running screen | AT-114 | ✓ |
| output | rendered text within the geometry budget | each renderer's `render` | yes — 120-combo sweep, 0 misfits | AT-115 | ✓ |
| output | audit event records (clip / overprint) | the injected sink | yes — events observed in unit corpus and sweep arm | AT-116 | ✓ |
| output | degraded diff on hostile HEAD objects (`None`, no crash) | `mapper/diff.py::_show` | yes — oversize / anchor / undecodable arms | `test_diff_side_*` · `test_git_diff_undecodable_head_object_returns_none_quietly` | ✓ |

### Signed-balance test ledger
> `post = base − D + A`. State counts in collected / passed-lean / passed-full form.

| base | − D | + A | = post | actual collected | passed-lean / full | reconciles? |
|------|-----|-----|--------|------------------|--------------------|-------------|
| 3546 | 0 | 33 | 3579 | 3579 | 3576 / 3575 | yes |

> Base and post counted with the gate command's own selection (`pyproject.toml` addopts deselect 24 slow/network tests). **Base 3546** on master `1609bbe` = 3543 passed + 3 xfailed — the collect-only count was re-derived on a clean `1609bbe` worktree at P4, so the brief's 3543 is the passed-full form of the same base. **A = 33**: 31 new test defs (`git diff 1609bbe..a860a27 -- tests/ | grep -c '^+.*def test_'`) + 2 extra parametrized items (the `NO_COLOR` boundary arm runs at 3 values). **D = 0**, verified at function level (`git diff … | grep '^-.*def test_'` → 0 hits — the B-112 lesson-3 check). **Actual collected 3579** re-verified by collect-only on the gate tree (HEAD `201646c` is records-only over `a860a27`). **passed-full 3575** = strict passes in the gate run; **passed-lean 3576** discounts the single failed arm, the pre-existing flake B-137 (reproduced 1/6 on master). Both sides carry 3 xfailed.

### Gaps detected
| ID | Requirement | Gap | Severity | Proposed action |
|----|-------------|-----|----------|-----------------|
| G-001 | — (pre-existing, outside this batch's contract) | `tests/test_reqharness_cache_fastpath.py::test_changed_size_or_mtime_takes_full_path` flaked once in the gate run (mtime/size ordering); reproduced 1/6 on master `1609bbe` by the orchestrator; untouched by this batch | minor | BACKLOG **B-137** — investigate order/load dependence; per `P-05` no batch arm's verdict rests on it |
| G-002 | — (found at P2 review F3, derivation-discovered) | a dangling-edge graph (edge whose child id ∉ `graph.nodes`) crashes `OutlineRenderer` (`mapper/views/outline.py:214-218`, KeyError); out of the sweep's declared scope (direct-construction only) | minor | BACKLOG **B-138** — decide refusal vs. tolerance in a batch touching `mapper/views/outline.py` |
| G-003 | — (review-environment transience) | inc003-F4 (the AT-114 screen arm) and inc004-F3 (`test_at_113_edge_count_cap_plus_1_refuses`, `test_at_110_depth_64_parses`) each failed once under review runs, unreproduced with zero source change between occurrences — consistent with environment noise (Windows AV/locking) | minor | BACKLOG **B-139** — poll-with-deadline robustness for the AT-114 arm; re-derive only on recurrence |
| — | HLR-Q3.2 scope | dim-text audit events deferred from v1 by orchestrator ruling R4 | minor (ruled) | BACKLOG **B-136** (kept open) |

### Escaped-bug regression (a defect escaped the suite: the crossed census missed a B1 consumer of the prescan)

| Regression id (`AT-NNN` / `TC-NNN`) | Pre-fix run (evidence it FAILED) | Pre-fix RED kind (value / shape) | Post-fix value-discriminating? (QC-2) | Post-fix result | Reconciled node |
|-------------------------------------|----------------------------------|----------------------------------|----------------------------------------|-----------------|-----------------|
| The three `LLR-N13.1.7` arms in `tests/test_repair_sidecar.py` (`test_llr_n13_1_7_refusal_warnings_carry_coordinates_not_values` · `::test_llr_n13_1_7_a_huge_scalar_origin_is_bounded_too` · `::test_llr_n13_1_7_a_coordinate_that_carries_a_value_is_bounded_too`) — amended, names unchanged | `evidence/xbatch14-red-2026-10-24.txt` (3 failed at `85cf081`; first caught by the orchestrator's post-merge full-suite run, 3 failed / 3568 passed — NOTE: the `full-suite-after-merge-2026-10-23.txt` transcript's 171-failure headline was a WORKER-SHELL ENVIRONMENT ARTEFACT, `NO_COLOR`/`TERM` exported, SUPERSEDED by the orchestrator's clean run; it is not the regression record) | shape+value: `load("m")` now raises `MapStoreError` at the prescan before the repair path exists, so the post-compose warning records the arms asserted can never appear | yes — each amended arm asserts the typed refusal (`MapStoreError`; message names the anchor `l0`/`big`/`bad` and the map id `card of m`; the huge scalar value absent) and keeps its original value-leak bound verbatim as a message-size negative (2,000 / 200,000 / 200,000 chars) | pass — `evidence/xbatch14-green-2026-10-24.txt` (38 passed); asserting mutant M-Q2-1-XB14 → all three RED (`evidence/xbatch14-mutant-2026-10-24.txt`) | the three named test nodes in `tests/test_repair_sidecar.py` (amended in place; owning batch `2026-08-26-ui-next-batch-02` sealed, not edited; amendment recorded as ledger `LED-2026-10-23-hygiene-batch.14`, ruling R10) |

### Evidence checklist — qa-reviewer (full)
> Attach `qa-reviewer`'s completed evidence checklist (items in `agents/qa-reviewer.md`), each marked ✓/✗ with one-line evidence. An unchecked or evidence-less item blocks the gate.

Executor attribution per row: **orchestrator** = the one gate-suite run at `a860a27`; **lane workers** = the increment-gate targeted runs; **reviewers** = the independent review subagents named in the increment packets; **dev-flow worker** = this evaluation (runtime absence of named reviewer sub-agents recorded in PLAN.md §Gate notices).

| # | Check | ✓/✗ | Evidence |
|---|-------|-----|----------|
| 1 | The ONE gate run is the orchestrator's, launched and collected by the orchestrator (C-25); the transcript hash-verified against disk | ✓ | `evidence/p4-full-suite-a860a27-2026-10-24.txt`, sha256 `00652d2c…4bd592` verified at P4; `__SUITE_DONE__ rc=1` tail; commit `a860a27` |
| 2 | Layer A: every HLR/LLR row carries an executed verification, a numeric threshold and a result | ✓ | 18/18 rows above; all pass in the gate run |
| 3 | Layer B: every story's `AT` observes its deliverable through the shipped surface, with representative + boundary + negative inputs | ✓ | AT-108…AT-116 rows; the UX walkthrough drove the real app and the real home screen |
| 4 | Spec-AT realization (C-18): every `§3 AT-NNN` reconciles to exactly ONE on-disk node | ✓ | AT-108 → `test_painted_screen_byte_identical_with_and_without_no_color`; AT-109…113 → the `test_at_10x_*` arms of `tests/test_ingestion_limits.py`; AT-111's two lowercase-named nodes documented (V2 tokenizer note, contract §3 HLR-Q2.1); AT-114 → `test_at_114_csv_refusal_toast_shows_the_reason`; AT-115 → `tests/test_scalecheck.py::test_sweep`; AT-116 → `tests/test_canvas_audit.py` + `::test_sweep_audit_arm` |
| 5 | Bidirectional surface-reachability: every named input dimension AND output/deliverable reached at the surface | ✓ | 15-row matrix above, 0 gaps |
| 6 | Signed test ledger reconciles: `base − D + A = post`, verified against an actual collect on the gate tree | ✓ | `3546 − 0 + 33 = 3579`; collect-only re-run at P4 gave 3579/3603 (24 deselected) |
| 7 | Supersession inspection read off the P3 packets: LLR-N13.1.7 partial supersession; surviving refs negative | ✓ | ledger `.14`; the three amended arms pass; the rest of N13.1.7 (non-anchor repair records) untouched and owned by the sealed batch; the 171-failure transcript superseded as an env artefact |
| 8 | Escaped-bug regression: pre-fix failing run captured, post-fix value-discriminating, mutant demonstrates the catch | ✓ | `xbatch14-red` / `-green` / `-mutant` (sha256-pinned in increment-003 §Cross-batch follow-up) |
| 9 | Every row names WHO executed it — an attribution, never a claimed run | ✓ | executor column in Layer A; gate run by the orchestrator; increment gates by lane workers; reviews by the named review subagents |
| 10 | Gaps dispositioned: every ⚠/✗ row lands in BACKLOG with an id and a severity | ✓ | B-137 (gate flake), B-138 (outline dangling-edge crash), B-139 (transient review flakes); B-136 kept open (dim-text, ruled R4) |
