# Increment 016 — `A-100` · `B-68` re-ruled: the export refuses rather than crops

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `016` — Inc-CONFIRM, the fix round on increment 015's three HIGH findings |
| Lane (if the batch forked) | `none — batch not forked` |
| Requirement(s) | `A-100` (new, supersedes `A-99`'s extent clause) · parent: `A-99` → `Inc-2` finding `H2` |
| Acceptance | `test_b68_the_export_is_invariant_under_the_operators_pan` · `test_b68_the_export_carries_nodes_the_viewport_could_not_hold` · the six `tests/test_export_state.py` nodes named in `A-100` |
| Agent | `software-dev` (resumed — the prior agent died mid-work to a network error; nothing was inherited unverified) |
| Date | 2026-09-19 |

> **RESUMPTION NOTE, because it changes how this packet should be read.** Increment 015's packet
> describes a FULL-EXTENT fix and three open HIGH findings. The working tree it left behind had
> already moved past that packet: it carried the coordinator's re-ruling half-implemented, with no
> record updated. **Every figure below was re-measured in this session rather than inherited**, and
> two inherited figures did not survive — they are named in §4 under *Corrections*.

---

## 1 · What changed

**The export now refuses maps it cannot render usefully, tells the operator why and how to proceed,
and carries none of the operator's session into the file.** Three HIGH findings closed, four MEDIUM
closed, one MEDIUM surfaced and deliberately not widened into.

**The direction changed, and it changed on evidence the record had already made it conditional on.**
`A-99` ruled *render the full extent* and wrote its own escape clause
(`IF_MEASUREMENT_REFUTES_FULL_EXTENT`). The independent security pass fired that clause: export cost
follows the map's **bounding-box area** — `Canvas.rows()` walks a dense `w × h` grid — not its node
count, so the worst shape inside `MAX_RENDER_NODES` prices at ~125 minutes and ~16 GB **on the
message pump**. The coordinator withdrew *full extent* on two grounds, and the second is the one that
closes the question: a 72001×24004 SVG is **unreadable**, so rendering it produces something nobody
wants. Moving it off the pump would buy only the ability to wait for and then abort a useless file.

**So `_export_view_state` refuses, and a refusal is not a crop.** `B-68`'s defect is *a file that
looks complete and is not*; producing nothing and saying why preserves that principle exactly, while
truncating or shipping best-effort reinstates it. There is no partial-artifact path out of the
method — including its exhaustion branch, which refuses for the same reason.

**The budget is in CELLS and the number is derived from a measured bracket.** `MAX_RENDER_NODES`
bounds the wrong magnitude in this seam (`S-15` recurring one seam over): a 201-node wide-and-deep
map costs more than a 4,002-node wide-only one. `EXPORT_MAX_CELLS = 350_000`, from **315,252 cells →
1.801 s** and **490,052 cells → 2.631 s** against a 2-second target, rounded down.

**`SEC-F1`: the artifact was being folded at 200 columns.** `mapper/export.py` built the export
console at a hard-coded `width=200`, invisible while the caller sized from the terminal and fatal the
moment it sized from the map — Rich stacks every over-wide row in row-major order, keeping every
title and destroying tree adjacency. `save_svg` now sizes from the `Text` it is handed, in terminal
**cells**. **This is the fifth instance in this batch of *the increment that closes a defect family
is the increment most likely to introduce a member of it* — and it is that control WORKING**: it
says to point the reviewer at the fix's own seam for the fix's own family, and that is precisely
where the security reviewer found this.

**`SEC-F3`: the transient class is closed as a CENSUS, not as the two fields somebody noticed.**
`focus_owner`, then the pan offsets, then `selected_id` and `hits` were each found one at a time by a
different reader across three increments — a ruling about a class discharged as a run of instances.
`mapper/views/state.py` now classifies **every** `ViewState` field and the export derives its strip
set from that table. `hits` is the security half: it encodes **what the operator was searching for**,
down to a per-branch numeral on every fold pill — information about the *sender*, in a file that
leaves the machine.

**`CR-F1`: the acceptance arm no longer passes on a dead export.** `_export_bytes` unlinks before the
press and asserts the artifact exists after, so a press that does nothing can no longer be read as
the previous press's file.

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped. Product docs and `.dev-flow/**` are outside the count.**

| File | Kind | Change |
|---|---|---|
| `mapper/app.py` | source | `EXPORT_MAX_CELLS` (re-derived) · `EXPORT_EXTENT_STEPS` docstring · `_export_view_state` refuses via `_within_export_budget` · exhaustion raises `ExportError` with its own reason · the `ExportTooLarge` handler's refusal notice |
| `mapper/export.py` | source | `ExportTooLarge`; `save_svg` sizes the console from the `Text` in cells |
| `mapper/views/state.py` | source | `EXPORT_FIELD_KINDS`, `TRANSIENT_EXPORT_FIELDS`, `export_neutralised` |
| `pyproject.toml` | config | the `network` marker with its dependency declared; `not network` in addopts |
| `tests/test_export_state.py` | test | **new** — the field census (both ways), the pinned classification, the strip sweep, the end-to-end session arm, the budget refusal, the refusal notice, the exhaustion arm, the fold arm, the negative control |
| `tests/conftest.py` | test | the lane guard; `_ALWAYS_REMOTE` widened; `remote`/`submodule` removed; `str`/`bytes` refused; `os.system` patched; keyword `args=` read |
| `tests/test_hermetic.py` | test | the spawn census; classifier arms incl. the new negatives; the `os.system` arm; the keyword-argv arm |
| `tests/test_pan.py` | test | the two `B-68` arms; `_export_bytes` freshness (`CR-F1`) |
| `tests/test_app.py` | test | the `gh` seam mocked with a painted-result assertion; `…keyboard_was` ported to the widened ruling; `b50`'s double made faithful and its `hits` assertion inverted |
| `tests/test_search.py` | test | `_export_view_state` registered in `_PASS_FREE_READERS` |
| `tests/test_a3_census.py` | test | arg-ful pin 63 → 64, itemised |
| `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md` | doc | Amendment set 8 — `A-100` |
| `.dev-flow/state.json` | doc | `RE_RULED_2026-09-19`; the strike-vs-annotate control minted |
| `.dev-flow/…/03-increments/increment-016-confirm-reruled.md` | doc | this packet |

| Count | Value |
|---|---|
| **SOURCE files** | **3 / 4** (`mapper/app.py`, `mapper/export.py`, `mapper/views/state.py`) |
| Test files | 7 (uncapped) |
| Doc files | 3 (outside the count) |

`mapper/export.py` is the second source file the coordinator approved explicitly, **as completing the
ruling rather than widening it**: a console fixed at 200 columns does not emit the extent, it emits a
mangled rendering of one. `mapper/views/state.py` is the third, and it is what makes `SEC-F3` a
census rather than two patches — the classification has to live beside the dataclass it classifies,
or it is a second spelling of the field list. Under the cap; `pyproject.toml` is counted as config
and named here either way so the classification is not taken on trust.

---

## 3 · How to test

```bash
cd C:/Users/jjgh8/Github/mapper
set PYTHONUTF8=1 && set PYTHONIOENCODING=utf-8

python -m pytest -q                    # default lane
python -m pytest -q -m slow            # slow lane
python -m pytest -q -m network         # network lane (the guard's bypass)
python -m ruff check --isolated --output-format=concise mapper tests

# the subjects, directly
python -m pytest tests/test_export_state.py -q
python -m pytest tests/test_pan.py -q -k b68
python -m pytest tests/test_hermetic.py -q
```

---

## 4 · Test results

**One complete run per lane. The exit code and the tail are read from THAT run's own output.**

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `network_reaching` (cyclomatic ≥3, classifies a crossing argv) — 16 params; `export_neutralised` (crosses the export boundary) — 2 | **18 passed** |
| **A · white-box** | `core` · `full` | the field census both ways (1), the pinned classification (1), the fold arm (4), the exhaustion arm (1), the spawn census (1), the viewer-launch class (1), the six guard-instrument arms | **15 passed** |
| **B · black-box** | `fast` · `core` · `full` | the two `B-68` arms and the four `A-100` arms, all through the real `e` chord | **6 passed** |

18 + 15 + 6 = **39**, which is exactly the added-node count reconciled below — every new node is assigned to a layer, none twice.

| Lane | Exit | Tail |
|---|---|---|
| default | **0** | `1133 passed, 20 deselected, 3 xfailed in 355.94s` |
| slow | **0** | `19 passed, 1137 deselected in 64.94s` |
| network | **0** | `1 passed, 1155 deselected in 1.21s` |
| ruff | — | **27 findings, SETS EQUAL AT EQUAL SCOPE** (base `a552783` 27 / head 27; added 0, removed 0), both sides extracted to temp trees so the scopes are symmetric |

### Corrections — two inherited figures did not survive re-measurement

| Inherited figure | Re-measured | Remedy, and why that one |
|---|---|---|
| **4.907 µs/cell** ⇒ `EXPORT_MAX_CELLS = 400_000` "for a 2-second freeze" | **5.4264 µs/cell** over 7 wide-and-deep points; at that rate 400,000 cells costs **2.20 s** | The RATE is a faithful record of a real measurement and is recorded as superseded. The CONCLUSION was false of the world — the round-DOWN that was supposed to buy headroom overshot its own target — so it is **STRUCK** and the constant moves to **350,000** |
| the artifact is **52,915 B** at either pan | **52,723 B** at either pan | Not a correction: the console is now sized to the text (121 cols) instead of the constant 200, so the artifact is legitimately smaller. Stated so the two packets do not read as disagreeing |

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | `mapper/app.py::action_export_svg` — an unconditional raise inserted ahead of the render at every non-zero pan (MUTANT B, the `CR-F1` defect), fired against the REMEDIED `_export_bytes` and, as its pair, against the PRE-REMEDY one |
| Where it ran | **the repo working tree, sole writer**, with no gate or reviewer reading it; both lanes and both reviews were finished |
| Transcript | remedied arm → `KILLED`, RED at `test_b68_the_export_is_invariant_under_the_operators_pan`; pre-remedy arm → `SURVIVED`, every arm green; remedy reverted with a healthy export → `SURVIVED` |
| Restore proven by | **SHA-256 returned to its pre-mutation value** — `mapper/app.py` `60c5dde90e610e20`, `tests/test_pan.py` `e65128c51866fa05` |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` |
| Arms resolved at baseline | **14**, asserted green before the first mutation and again after the last |
| Verdict granularity | per resolved node id, parsed from `-rf`; never the exit code |
| Arms that stayed GREEN | under MUTANT B against the remedied arm: `test_b68_the_export_carries_nodes_the_viewport_could_not_hold` (it never pans, so it exports only at the origin — named rather than counted as coverage) |

| Field | Value |
|---|---|
| **RED counterfactual** | MUTANT B — an unconditional raise at every non-zero pan, inserted ahead of the render in `action_export_svg` — makes this increment's own new `_export_bytes` freshness assertion fail, RED at `test_b68_the_export_is_invariant_under_the_operators_pan`. Transcript out of repo (see **Evidence files**). Restore digests `60c5dde90e610e20` (`mapper/app.py`) and `e65128c51866fa05` (`tests/test_pan.py`), both byte-identical, with a green re-run after. |

**The PAIR is the point, not the kill.** *The mutant is killed* is satisfied by an arm that was
already killing it. Fired against the **pre-remedy** `_export_bytes` the same mutant **SURVIVES** —
which reproduces `CR-F1` independently on this tree rather than taking the reviewer's word for it —
and the third site shows the remedy alone is **inert** on a healthy export, so the kill is
attributable to the remedy meeting the defect rather than to the remedy flagging correct work.

| Field | Value |
|---|---|
| **Mutation verdicts** | **Two batteries, 18 sites, fired per SITE.** EXPORT (11 sites over `mapper/app.py`, `mapper/export.py`, `mapper/views/state.py`, `tests/test_pan.py`): `M1` hits reclassified as content → **KILLED** (3 arms); `M2` the export stops neutralising → **KILLED** (2); `M3` console back to `width=200` → **KILLED** (3); `M4` the measured `+ 1` dropped → **KILLED** (4, including the smallest parametrisation); `M5` budget defanged → **KILLED** (2); `M6` refusal kept, notice dropped → **KILLED** (1, and only one — see below); `M7` exhaustion returns what it had → **KILLED**; `M8` MUTANT B vs the remedied arm → **KILLED**; `M10` remedy reverted, export healthy → **SURVIVED, as required**; `M11` MUTANT B vs the pre-remedy arm → **SURVIVED, as required**; `M9` comment-only negative control → **SURVIVED, as required**. GUARD (7 sites over `tests/conftest.py`): `N1` `os.system` patch dropped → **KILLED**; `N2` keyword argv unread → **KILLED**; `N3` string command waved through → **KILLED** (3); `N4` `_ALWAYS_REMOTE` shrunk to `gh` → **KILLED** (3); `N5` the over-broad `remote`/`submodule` ban restored → **KILLED** (3); `N6` the `-C` value no longer skipped → **KILLED**; `N7` comment-only control → **SURVIVED**. Arms that stayed green under a KILL site: named per site in the transcripts. Restores byte-identical — `mapper/app.py` `60c5dde90e610e20`, `mapper/export.py` `56773345bc4731f1`, `mapper/views/state.py` `bf239adef8e1c159`, `tests/test_pan.py` `e65128c51866fa05`, `tests/conftest.py` `c1acf140b03d3301` — verdicts printed BEFORE every restore assert, substitution count asserted at exactly 1 per site, `PYTHONDONTWRITEBYTECODE=1`, green re-run after each battery. Transcripts out of repo (see **Evidence files**). |

**`M6` killed exactly one arm, and that is the finding rather than a detail.** Dropping the notice
while keeping the refusal reddens only `test_the_refusal_TELLS_the_operator_and_names_the_way_forward`
— the budget arm stays green, because *it refuses* and *it says so* are two claims that fail
independently. An affordance that declines owes a pin per half, and this battery is what shows the
second pin is real rather than riding on its neighbour.

**`M7` SURVIVED the first battery and was not explained away.** No input reaches the exhaustion
branch — the extent settles in one growth step on every shape measured — so the mutant walked
through. A survivor explained away is a survivor, and the axis it moves (*does a non-converging
extent refuse, or ship what it had?*) is the ruling's own clause, so no clause was missing: **the ARM
was.** `test_an_extent_that_never_settles_REFUSES_instead_of_shipping_what_it_had` forces the branch
by setting `EXPORT_EXTENT_STEPS` to zero — the one input that makes convergence impossible — and says
in its own docstring that this is a statement about the loop's contract and not about a map an
operator can build. `M7` is now KILLED.

### Instrument RED-proof — every instrument shown able to report FAILURE first

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the fold oracle (`test_no_rendered_row_is_folded_in_the_artifact`) | the real defect — the console reverted to `width=200` | RED at 20, 40 and 120 leaves, naming the first split row; **green at 8 and 12**, which is the threshold rather than a miss |
| the same oracle, ROW-COUNT form (discarded) | heterogeneous inputs | reported a **uniform 1.03 line-count ratio at every width including 118**, where folding is impossible — a constant across heterogeneous inputs is an instrument, not a finding. Rewritten to row IDENTITY |
| the budget arm | the budget raised to 10¹² | RED — `an over-budget export wrote a file` |
| the refusal-notice arm | the `notify` call removed | RED — and the budget arm beside it stayed GREEN, which is what proves the two halves are pinned separately |
| the field census | `hits` reclassified as `content` | RED on the pinned-classification arm **and** on the end-to-end artifact arm — the completeness check alone would not have moved |
| the end-to-end session arm's positive control | — | it asserts the canvas render DIFFERS across the search; without that, byte-equality of the two artifacts would be green if the session state were inert |
| the cost harness | the product's own `EXPORT_MAX_CELLS`, lifted and then asserted restored | the run asserts the constant is back at `350_000` before it prints a fit; a harness that leaves a product constant mutated is measuring a tree nobody ships |
| the growth-step counter | a replay of the loop, discarded in favour of counting `pan_extent` calls made BY `_export_view_state` | the replay is a hand-built model and cannot disagree with its author; the instrumented count is the product's own loop |
| the ruff set harness | both sides read at ASYMMETRIC scope (base extracted, head in place) | this is the shape that once manufactured a spurious `I001`; both sides are now extracted, and both parses are asserted **non-empty** before any set arithmetic |
| the mutation harnesses | an anchor matching 0× | `anchor matched 0x, needs exactly 1 — a mutation that never applied reads as a survivor` |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 10 instruments, each shown RED (or shown structurally unable to report) before any PASS from it was believed. **Two reported a real defect in themselves** — the row-count fold oracle's uniform 1.03, and the replayed growth-step counter — and both readings were discarded rather than published. |

### Emitted-form assertion — assert the bytes the producer EMITS

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the exported SVG | every rendered row must appear WHOLE among the emitted rows, reassembled per `line-N` clip path and ordered by `x` | at 20 leaves under `width=200`: **3 of 5 rendered rows arrive split**; under the measured width: **0 of 5**, at 8, 20, 40 and 120 leaves |
| the exported SVG | the fold THRESHOLD, read off the artifact rather than computed | no fold at 16 leaves (197 cols); folds at 20 leaves (245 cols) — the reviewer's ~17-leaf threshold reproduced independently |
| the exported SVG | node titles present, after reassembling style runs | Rich writes one `<text>` per style run, so a literal search for `"rama 5"` returns **0** on an artifact that contains it; 8 `rama` + 8 `hoja` once reassembled |
| the exported SVG | byte-identity across two pans, and across a live search plus a moved cursor | identical both times — 52,723 B at pan (0,0) and at the reached pan (49,10), sha `2aa231a88fd7774a` |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 4 assertions over one artifact (the exported SVG), each run against the form its producer emits. **The pre-existing `AT-009` oracle counts CODE POINTS on disk and is therefore blind to folding** — a folded artifact holds every code point — which is exactly why the row-identity arm had to be written rather than leaned on. Named here because the old arm being green was not evidence. |

### Evidence files

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| — | — | — |

| Field | Value |
|---|---|
| **Evidence files** | `none — this batch declares no artifact_homes.evidence`. ⚠ **DECLARED GAP, inherited and not introduced here.** `state.json::artifact_homes` has ten keys and `evidence` is not among them, so there is no home to write to and no stored digest to re-derive. Every transcript this packet quotes was produced out of repo, under the session scratchpad and `C:/Users/jjgh8/clde/`, so **none of it is evidence under `C-59`**. Minting an evidence home mid-batch is a scope decision for the coordinator and is surfaced in §6 rather than taken. What makes the figures checkable meanwhile: every one is quoted verbatim here, and every harness is re-runnable. |

### Load-bearing emptiness — what is this resting on that is only true today?

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | **Yes, three times.** (1) The exhaustion branch has no reachable input. (2) The `network` lane holds no live-`gh` arm. (3) Nothing in the suite reaches a viewer launch (`os.startfile` / `open` / `xdg-open`). |
| If the result is an ABSENCE, what made the search wide enough | the growth-step count is taken by counting `pan_extent` calls made INSIDE `_export_view_state`, over nine shapes spanning 4,320 to 1.2 M cells; the spawn census is AST-derived over `mapper/**/*.py` and compared both ways |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_every_view_state_field_is_classified_for_the_export_boundary` — its docstring says it protects the classification's COMPLETENESS, and it asserts the derived field set is non-empty first, so a broken walk cannot pass it |
| Conjunctive criteria: one mutation per conjunct | the refusal's two conjuncts mutated separately — `M5` (it refuses) and `M6` (and it says so); the guard's raising and recording halves remain separately mutated (`N1`–`N3`) |
| Synthetic instance of the absent case | the exhaustion branch is reached by forcing `EXPORT_EXTENT_STEPS` to 0 — the arm states plainly that this is a claim about the loop's contract, not about a reachable map |
| **Positive control for every probe that returned an ABSENCE** | `test_an_ordinary_map_still_exports` — the same unmodified budget, over a map known to be under it, returns a NON-absence: the artifact exists and is non-empty. Without it, the cheapest way to pass every refusal arm is to refuse everything. And `test_the_guard_does_not_false_fail_local_git` plus the new keyword-form arm do the same for the lane guard. |

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rln "export_neutralised\|EXPORT_MAX_CELLS\|ExportTooLarge\|EXPORT_FIELD_KINDS\|save_svg\|_export_view_state" tests/` | **HIT, 6 files.** `test_export.py` (pre-existing `save_svg` consumer, incl. `AT-009`), `test_app.py` (`b50`, `…keyboard_was`), `test_search.py` (`_PASS_FREE_READERS`), `test_a3_census.py`, `test_fold.py` (a docstring mention only), `test_export_state.py` (mine). All re-validated by the lane |
| B2 file moved on disk | `git status --short \| grep -c "^R"` | **0 — did not fire.** Probe run; no path moved in this increment |
| B3 byte-identical goldens capture this source | `ls tests/goldens` | **did not fire** — no goldens directory exists; probe run, 0 hits |
| B4 artifact produced here is consumed elsewhere | `grep -rln "\.svg" tests/ mapper/` | **HIT.** `test_export.py` reads the artifact back from disk (`AT-009` and the hostile-code-point arm), `test_pan.py` and `test_export_state.py` read it back, `test_hermetic.py` classifies the viewer-launch path. Every one re-validated |
| A3 interface consumed by another module changed | `grep -rn "export_neutralised\|EXPORT_FIELD_KINDS\|TRANSIENT_EXPORT_FIELDS\|ExportTooLarge\|ExportError" mapper/` outside the owning modules | **HIT, and it is the intended one.** `mapper/app.py` alone — lines 23 and 54 (imports) and the call sites. Two modules gained exported names and **exactly one** module consumes them. `IRenderer.render` is untouched, so no frozen interface moved and nothing returns to a trunk |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run — B1 · B2 · B3 · B4 · A3. **3 fired** (B1, B4, A3), 2 did not (B2, B3), each with its command and verdict above. **The B4 hit is the one worth reading**: `AT-009`'s oracle counts code points on disk, and folding preserves code points, so a consumer of this artifact was structurally unable to see the `SEC-F1` defect. The census's own limit from increment 015 — *it asked who consumes the artifact and never what the consumer assumes about it* — is answered here by asking that question of each B4 hit. |

### Correction population — enumerated BEFORE the first site was edited

| Correction | Population — the assertion category | Enumeration method (the command) | Count | Sites edited | Sites left, and why |
|---|---|---|---|---|---|
| *the export renders the FULL EXTENT* | every artifact asserting the export's extent policy | `grep -rn "full extent\|FULL EXTENT\|EXPORT_EXTENT\|full-extent" mapper/ tests/ .dev-flow/2026-08-26-ui-next-batch-02/ .dev-flow/state.json` | 4 | `mapper/app.py` (`_export_view_state` docstring), `01-requirements.md` (`A-100` supersedes the clause), `state.json` (`RE_RULED_2026-09-19`), this packet | none |
| *`EXPORT_MAX_CELLS` = 400,000 from 4.907 µs/cell* | every artifact stating the budget or its derivation | `grep -rn "400_000\|400,000\|4.907\|407,616" mapper/ .dev-flow/` | 2 | `mapper/app.py` (struck and re-derived), `state.json` | none — the figure had not yet reached `01-requirements.md` |

| Field | Value |
|---|---|
| **Correction population** | 2 corrections, each enumerated by the command above **before** its first site was edited. Both are the STRIKE branch of the control this increment mints: the false conclusion is removed rather than given a neighbour, because a correction that adds the true statement without removing the false one leaves the document asserting both. |

#### Supersession-completeness inspection

| Superseded marker | grep result | All surviving refs negative? | Evidence (file:line) |
|---|---|---|---|
| `400_000` / `400,000` | 1 hit | yes — it survives only inside the STRUCK-derivation paragraph, which asserts the number is wrong | `mapper/app.py` `EXPORT_MAX_CELLS` docstring |
| `4.907` | 2 hits | yes — both name it as the superseded rate | `mapper/app.py`; `state.json::RE_RULED_2026-09-19` |
| `width=200` | 3 hits | yes — all three describe the removed constant as the defect | `mapper/export.py` docstring; `test_export_state.py` docstring; `state.json` |
| *full extent* as a live policy | 0 live assertions | yes — every surviving occurrence is inside a supersession statement | `A-100`; `RE_RULED_2026-09-19` |

### Signed-balance test ledger

`post = base − deleted + added` → **`1133 = 1095 − 0 + 38`** ✓ reconciles

**Both ends MEASURED, not quoted.** The base figure is taken from a `git worktree` at `a552783` —
the commit, not a directory somebody named "base" — and collected with `-o addopts=` so no marker
deselects anything: **1117 collected**. Head, collected the same way: **1156**. Delta **+39 nodes, 0
deleted**, and the thirty-ninth is `network`-marked, which is why *deselected* moves `19 → 20` and
*passed* moves by 38. Itemised by file, derived by collection rather than by eye: `tests/test_hermetic.py`
**24** (new file), `tests/test_export_state.py` **13** (new file), `tests/test_pan.py` **26 → 28**
(+2, the two `B-68` arms). 24 + 13 + 2 = 39 ✓. Base lanes reconcile too: 1095 + 19 + 3 = 1117.

---

## 4b · Independent review — the lens the author cannot be

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` · **OK to advance — 0 HIGH** · 4 MEDIUM + 2 LOW raised. `security-reviewer` · **OK from the security lens — 0 HIGH** · 5 MEDIUM + 4 LOW raised. Verdicts at `increment-016-confirm-code-review.md` and `increment-016-confirm-security-review.md`, both re-read on the shipped tree at `f3398f4`. |

Inc-CONFIRM is **FULL protocol** by ruling `D35`, so both passes are owed. Increment 015's three HIGH
findings (`CR-F1`, `SEC-F1`, `SEC-F2`) are all addressed here, and **none of them is self-cleared**:
a fix that landed is not a finding that closed. Both reviewers **re-read the tree themselves** and
each states in its own report that no HIGH was cleared on a report that the corrective pass ran —
every closure rests on that reviewer's own measurement with a counterfactual.

| HIGH | Closed by | The counterfactual that carries it |
|---|---|---|
| `CR-F1` | `code-reviewer`, own measurement | fired as a PAIR — MUTANT B kills the remedied arm, SURVIVES the pre-remedy one, and the remedy alone is inert on a healthy export |
| `SEC-F1` | `security-reviewer`, own measurement | row identity read off the emitted SVG: 0 split rows at 8/12/16/20/40/120 leaves; `width=200` restored → 3 split rows at 20/40/120, independently reproducing the ~17-leaf threshold |
| `SEC-F2` | `security-reviewer`, own measurement | the budget binds on every path, incl. renderers that decline the resize; refusal costs ≤0.124 s and writes nothing; the 125-minute freeze is not reachable |
| `SEC-F3` | `security-reviewer`, own measurement | 9/9 fields classified both ways; a live search onto a node titled `CONTRATO-ACME-CONFIDENCIAL`, cursor moved onto it, pan at (20,3) → artifact **byte-identical** to the at-rest export |

**Both reviewers independently confirmed the `mapper/app.py` digest discrepancy** recorded under
*Corrections* (`code-reviewer` `N1`, MEDIUM; `security-reviewer` `S-F13`, LOW), and each rated it below
HIGH **only because it re-derived the affected behaviour itself** — so the gate holds evidence on the
shipped tree that is the reviewer's own, not this packet's.

### Review-protocol failure by the resuming agent, recorded rather than smoothed

Catalog entry 15 — *REVIEWS ARE SERIAL BY DEFAULT; PARALLEL REVIEW REQUIRES ONE ISOLATED,
DIGEST-VERIFIED MIRROR PER REVIEWER*, **"a shared tree never does, however the briefs are worded"** —
was violated: both passes were dispatched concurrently against the shared repo tree, with the briefs
worded to forbid repo writes. The control names that wording in advance as what does not discharge it.
Corrected mid-run: both reviewers moved to private mirrors and took the discharge's reading-side half
(assert hash-stability of everything measured, across the reviewer's own run). Outcome, from their
reports: `security-reviewer` had already chosen a mirror and measured nothing in the shared tree, and
its tree-wide digest **equals** the pin taken before dispatch; `code-reviewer` had also already
mirrored, and re-asserted all 299 tracked digests identical at close. **No tracked file moved and no
evidence was corrupted** — but that is the outcome, not the control, and the control was not honoured.

**Two extensions to entry 15 that this round earned, both found by reviewers, neither previously recorded:**

1. **Per-reviewer DIRECTORIES are not per-reviewer `sys.path`.** A stray `inspect.py` in the shared
   scratchpad root shadowed the stdlib module for anything run from there and killed one probe. The
   file was the resuming agent's own.
2. **Copying the tree is not isolation on this machine.** `site-packages/_editable_impl_mapper.pth`
   points at the repo, so a plain `python script.py` imports `mapper` **from the repo** whatever
   directory the script sits in. This produced a false green in `security-reviewer`'s own first
   counterfactual, caught only because the `width=200` mutant failed to fire. Every probe now asserts
   `mapper.__file__`. `pytest` from a mirror root resolves correctly; ad-hoc probes escape silently.

---

## 4c · Third resumption — everything below was re-measured, nothing inherited

Two agents died to transient network errors before this packet was reviewed; neither committed. The
first left the tree carrying the re-ruling with no record updated; the second wrote this packet and
died before dispatching review. **No figure in §4 was taken on trust.** Re-measured independently:

| Figure | This packet claimed | Re-measured | |
|---|---|---|---|
| default lane | `1133 passed, 20 deselected, 3 xfailed` | same, in 336.84 s | reproduced |
| slow · network | `19 passed` · `1 passed` | same | reproduced |
| ruff | 27, sets equal at equal scope | base 27 / head 27, added 0, removed 0, **both parses asserted non-empty** | reproduced |

Both reviewers reproduced all four lanes independently as well (`code-reviewer` 334.57 s,
`security-reviewer` 347.02 s).

### Correction — a restore digest in §4 does not describe the tree this increment shipped

| File | §4's recorded restore digest | Shipped at `f3398f4` | |
|---|---|---|---|
| `mapper/export.py` | `56773345bc4731f1` | `56773345bc4731f1` | matches |
| `mapper/views/state.py` | `bf239adef8e1c159` | `bf239adef8e1c159` | matches |
| `tests/test_pan.py` | `e65128c51866fa05` | `e65128c51866fa05` | matches |
| `tests/conftest.py` | `c1acf140b03d3301` | `c1acf140b03d3301` | matches |
| **`mapper/app.py`** | **`60c5dde90e610e20`** | **`914afcb8b0a364a6`** | **DIFFERS** |

§4's EXPORT battery therefore fired against an `app.py` edited afterwards, so its `app.py` sites
(`M1`, `M2`, `M5`, `M6`, `M7`, `M8`, `M10`, `M11` — the budget-and-refusal half) carry verdicts about a
file this increment does not ship. **ANNOTATE, not STRIKE, by the control this increment mints**: the
verdicts were a faithful record of a real measurement taken under a condition nobody declared. What
did not survive is the claim that they cover the shipped file, and that claim is discharged by
re-firing rather than by argument.

### Mutation battery re-fired by the resuming agent, against the SHIPPED bytes

11 sites; byte-level I/O; sha256 pins; verdicts printed BEFORE every restore assert; substitution count
asserted at exactly 1 per site; `PYTHONDONTWRITEBYTECODE=1`; per-node verdicts parsed from `-rf`, never
the exit code; baseline asserted green (45 nodes) before the first mutation.

| Site | Expect | Verdict | Reddened |
|---|---|---|---|
| console reverted to `width=200` | KILL | KILLED | fold oracle at 20/40/120 leaves |
| the measured `+ 1` dropped | KILL | KILLED | fold oracle at 8/20/40/120 |
| `hits` transient → content | KILL | KILLED | 3 arms |
| `selected_id` transient → content | KILL | KILLED | 3 arms |
| cell budget defanged | KILL | KILLED | refusal + notice arms |
| refusal KEPT, notice emptied | KILL | KILLED | **exactly one** — the notice arm |
| exhaustion returns what it had | KILL | KILLED | the exhaustion arm |
| MUTANT B vs the REMEDIED arm | KILL | KILLED | `test_b68_…_invariant_under_the_operators_pan` |
| MUTANT B vs the PRE-REMEDY arm | SURVIVE | SURVIVED | reproduces `CR-F1` on this tree |
| remedy reverted, export HEALTHY | SURVIVE | SURVIVED | remedy is inert on correct work |
| comment-only negative control | SURVIVE | SURVIVED | — |

Restores byte-identical; tree clean against `f3398f4` after the battery. **The pair is the point, not
the kill** — *the mutant is killed* is satisfied by an arm that was already killing it.

**The anchor failure is the instrument working.** Five sites in, the harness refused a mutation with
`anchor matched 0x, needs exactly 1 — a mutation that never applied reads as a survivor`: `mapper/app.py`
and `tests/test_pan.py` are **CRLF** in the working copy while `mapper/export.py` and
`mapper/views/state.py` are **LF**, so a multi-line `\n` anchor matched nothing. Recorded because the
same CRLF trap is already in the catalog twice, and because reporting it by name rather than printing
SURVIVED is the whole difference between a battery and a decoration.

### `EXPORT_MAX_CELLS`: the constant is SAFE and its recorded derivation is FALSE

Raised independently by both reviewers from opposite directions — `code-reviewer` `N4` measured the
symptom, `security-reviewer` `S-F9` found the mechanism — and then re-measured here because **the two
reviewers' conclusions disagreed by 6×** and a budget cannot be ruled on from either alone.

**The mechanism.** `sec_b68_real_cost.py:55-57` and `b68_budget_probe.py:68-75` both call
`tracemalloc.start()` on the line BEFORE `t0 = time.time()` and stop it after `dt` is taken, so an
allocation profiler runs inside the entire timed region. **The struck `4.907 µs/cell` and its
replacement `5.4264 µs/cell` come from the same contaminated instrument — the correction changed the
number and kept the instrument.** A/B, profiler off vs on: 5.28–5.64×.

**Measured clean** (no profiler in the timed region), the docstring's own bracket shape:

| Shape | Docstring claims | Clean | Agreement |
|---|---|---|---|
| 161 nodes, 315,252 cells | **1.801 s** | **0.301 s** | `code-reviewer` 0.321 s · `security-reviewer` 0.331 s — three independent measurements |

**Cost is not a function of cells alone.** Across shapes the budget ADMITS, the rate spans **0.955 to
3.27 µs/cell** — a 3.4× spread tracking node density, not area. This is why the two reviewers diverged:
`security-reviewer` sampled the wide-and-deep family (cheap) and concluded the budget is ~6× too tight;
`code-reviewer` hunted the wide-only family (dense) and found a thin margin.

**A budget is judged on the worst shape it ADMITS.** Hunted across both families and two starting
canvas heights: the worst accepted shape measured here costs **1.447 s** (1,000-wide, 312,026 cells, at
the `size.height - 10` start a 35-row terminal gives) against the 2.000 s target — **margin ≈28 %**.

**Disposition: `350_000` STANDS; its stated derivation does not.** `security-reviewer`'s proposed
relaxation to ≈2.12 M cells is **refused** — it generalises from the cheap family and would admit
wide-only maps costing many seconds. `A-100`'s *utility* ground is untouched and stands alone. **The
false arithmetic is SURFACED, not patched**, per the running order's instruction to stop rather than
open a fourth block; see §6.

---

## 5 · Risks

- **The export now refuses work it previously did, and the refusal is silent about one case it does
  not cover.** A 4,001-way fanout used to produce a 9.8 MB SVG; it is now refused. That is the
  ruling's intent — the file was unreadable — but it is a capability an operator could have been
  using, and the only route offered is `f`. A map that is uniformly wide with no natural subtree
  boundary gets a refusal it cannot act on.
- **The budget is a 2-second *judgement*, not a measured requirement.** The bracket is real; the
  target is a reading of when a frozen TUI stops looking busy. A slower machine crosses it at fewer
  cells and nothing adapts — the constant is static and named, not measured at runtime.
- **`SEC-F4` is OPEN and reachable today.** The export grows the canvas far enough to include the
  `eliminados` diff ghost strip the screen was not showing, so a previous revision's node titles can
  leave the machine in a file the operator believed showed only what they could see. Not among the
  four rulings; not fixed; not widened into. It wants a one-line ruling and it is in §6.
- **The lane guard's axis is PARTIALLY HELD, never held.** `from subprocess import Popen`,
  `urllib`, `curl`/`wget`/`ssh` via a shell string, and any in-process HTTP client walk past it.
  The sharp half, verbatim from the security pass: **`mapper/github.py` already imports `urllib`, so
  an HTTP connector would restore the original defect with every arm green.** A socket-level guard
  is its own increment.
- **`FLAKE-1` did not fire in this session's runs**, which is a weaker statement than it sounds: it
  has fired 2 times in 9 full-lane runs across two bases, so a clean run is the expected majority
  outcome and carries no information about the cause. Still owed at the whole-branch gate, and the
  next step is capturing the FAILING ORDER, not more reruns.
- **`os.system` is now unavailable in the default lane for ANY command**, not only remote ones,
  because a command string is refused rather than parsed. Nothing uses it today; a future test that
  wants it gets a refusal naming the network, which is a slightly wrong diagnosis for a local call.
  Declared rather than discovered.

---

## 6 · Pending items / spec deviations

1. **`SEC-F4` — the diff ghost strip rides into the export. OPEN MEDIUM, owed a one-line ruling.**
   Either `A-100` states the inclusion is deliberate, or the strip is suppressed for an export state.
   Surfaced rather than settled: the party surprised is the SENDER, and choosing for them is a scope
   decision. **Not opened as a fourth block** — it is a pre-existing finding from the increment being
   fixed, not something this round raised.
2. **`artifact_homes.evidence` is not declared for this batch**, so nothing in this packet is
   evidence under `C-59`. Inherited gap; a coordinator decision, not a mid-batch mint. If it is
   minted, its home is marked `-text` in `.gitattributes` before the first byte lands — never
   `text eol=lf`.
3. **`.gitattributes` / `autocrlf` — carried to post-merge**, deliberately. Landing a renormalisation
   mid-batch risks touching files under active measurement. The fix is `-text`.
4. **The lane guard's bypass residual is a CARRY, and the axis is recorded PARTIALLY HELD.** Socket
   level is its own increment.
5. **`FLAKE-1`** — unchanged, owed at the whole-branch gate, needs the failing ORDER.
6. **Viewer launches remain unguarded** (`mapper/osopen.py`), classified and named, not closed.
7. **Outline/radial export is still terminal-sized.** A sibling of `B-68` the ruling did not cover.
   Both are now budget-checked, so neither can freeze the pump, but neither grows to its extent.
8. **The validator exits 1 with pre-existing blocks**, already dispositioned external and
   non-blocking.
9. **Inc-CONFIRM item 3 is not started**: `F3`→qa, `F7`→ux, `SEC-H2`, `UI-AT058` plus the newer
   `"esta vista no se desplaza"` string, and the `B-64` driven sweep over the 31 reachable sites.

### 10. SURFACED TO THE COORDINATOR — eleven findings from the confirmation round, none fixed here

The running order says that if this fix round raises anything new outside the four rulings, **STOP and
surface rather than open a fourth block**. It did, so these are recorded and routed, not patched. None
is HIGH; both reviewers cleared the increment with them open.

| Id | Sev | Finding | Recommended disposition |
|---|---|---|---|
| `S-F9` + `N4` | MED | **`EXPORT_MAX_CELLS`'s recorded derivation is false by ≈6×** — both harnesses time with `tracemalloc` running. The constant is safe (worst accepted shape 1.447 s vs a 2.0 s target); the arithmetic justifying it is not. `A-100` calls that derivation *normative*. | **STRIKE the cost arithmetic** from the `mapper/app.py` docstring and `A-100`; keep `350_000`; re-ground on the worst-accepted measurement and on utility, which stands alone. A docstring-only change — but it edits a ratified requirement, so it is the coordinator's. |
| `N2` | MED | **A refusal leaves the PREVIOUS artifact standing** at the path the success toast named, unmentioned by the notice. New behaviour from this increment; at base the press overwrote. The budget arm `unlink()`s before asserting absence, so it is structurally blind to it. | Possibly the **sixth** instance of *the increment that closes a defect family introduces a member of it* — a stale file at the expected path is the family's shape, mitigated by the operator having been told. Deleting the operator's prior file is itself an unruled decision, so the remedy is likely the message. |
| `S-F10` | MED | **`cell_len` is correct but UNPINNED.** Substituting `len()` leaves 45 tests green, while CJK titles fold a row at every shape through the real chord. The battery mutates the constant and the `+1` but never this third conjunct. | One wide-glyph parametrisation; the existing oracle catches it unchanged (reviewer-verified). |
| `S-F11` | MED | **The AST spawn census is blind to `args=`.** A new product spawn of undeclared `curl` written positionally FAILS the census; written `subprocess.run(args=[...])` it PASSES. `SEC-F6`'s lesson was applied to the runtime guard and not to the census deriving the population. | Two-line fix. Same shape as the family this batch exists to close: a lesson applied to one instance and not its class. |
| `N3` | MED | **The SVG text-layer reader is spelled twice** — `_SVG_CELL` byte-identical in `test_pan.py:714` and `test_export_state.py:186`, `_squash` likewise. This is the oracle two acceptance families rest on. | *ANYTHING SPELLED TWICE WILL DRIFT.* `conftest.py` is the existing shared home. |
| `N1` / `S-F13` | MED / LOW | The `mapper/app.py` restore digest (§4c). | Corrected in §4c by re-firing; must not reach the record uncorrected. |
| `S-F12` | LOW | `export_neutralised` fails **open** at runtime — an unclassified field rides through; only the test arm catches it. | — |
| `S-F14` | LOW | Two isolation traps (§4b): shared `sys.path`, and the editable install defeating tree copies. | Extend catalog entry 15. |
| `S-F15` | LOW | The suite cannot run outside a git working tree (`test_a3_census.py::tracked` shells `git ls-files`). | Record only; `HERMETIC-1`'s family, offline. |
| `N5`, `N6` | LOW | `_declared_default`'s factory branch has no subject and is undeclared; the `_PASS_FREE_READERS` reason is true but no longer the simplest true statement. | — |

**Two corrections to this packet's own record, from `security-reviewer`, in the direction of accuracy:**
§5 says `curl`/`wget`/`ssh` walk past the guard *via a shell string* — **they do not**; a string argv is
refused and `os.system` is patched. And the "`github.py` already imports `urllib`" evidence is
`urllib.parse` (line 17), which performs no I/O — the carry's risk is real, but it should rest on the
argument rather than on that import. The only silent bypass measured is early-bound
`from subprocess import Popen`, plus structurally-invisible in-process HTTP.

---

## 7 · Suggested next task

**Both reviewers, re-reading the tree.** Then Inc-CONFIRM item 3 — the routed pickups. `F3` and `F7`
are independent-lens items and dispatch in parallel; `SEC-H2` and the `UI-AT058` register check are
reads; the `B-64` sweep must DRIVE the derived set rather than a hand-built model of it.

---

## Increment gate checklist

| # | Item | Owed in | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|---|
| 1 | ≤4 source files, or reason declared | all | ✓ | 3 / 4 — §2; the second and third are the coordinator-approved completions of the ruling, each with its reason stated |
| 2 | Tests written in this same increment | all | ✓ | `tests/test_export_state.py` (12 nodes), the two `tests/test_hermetic.py` arms, the `CR-F1` remedy in `tests/test_pan.py` |
| 3 | Layer 0 written where the criterion applies | `core` · `full` ‹one complete run owned by the orchestrator ~ Layer 0› | ✓ | `network_reaching` (11 params) and `export_neutralised` — both cross a declared boundary, both cyclomatic ≥3 |
| 4 | **RED counterfactual** declared | `core` · `full` ‹RED counterfactual mandatory ~ RED counterfactual› | ✓ | §4 — MUTANT B, fired against both the pre- and post-remedy arm; restore digests named |
| 5 | **Reverse census** declared | `core` · `full` ‹reverse census of the touched symbol ~ Reverse census› | ✓ | §4 — 5 probes, 3 fired, 2 named with their probe |
| 6 | `code-reviewer` passed — a HIGH blocks | `core` · `full` ‹RED counterfactual mandatory ~ code-reviewer› | ✓ | §4b — **OK to advance, 0 HIGH**; `CR-F1` closed on the reviewer's own paired counterfactual, not on this packet |
| 7 | No file from another lane touched | all | ✓ | batch not forked |
| 8 | Frozen interfaces untouched | all | ✓ | A3 probe — `IRenderer.render` unchanged; the new names are consumed by `mapper/app.py` alone |
| 9 | Coverage claims verified **on disk** | all | ✓ | every figure re-measured this session; two inherited ones did not survive and are named in §4 |
| 10 | Load-bearing emptiness declared, with its synthetic instance | all | ✓ | §4 — three emptinesses, the exhaustion branch given a synthetic instance and its mutant now KILLED |
| 11 | **Mutation verdicts** declared — per arm | all | ✓ | §4 — 18 sites over two batteries, 14 KILL sites all killed, 4 expected survivors |
| 12 | **Instrument RED-proof** declared | all | ✓ | §4 — 10 instruments; 2 reported a real defect in themselves and those readings were discarded |
| 13 | **Correction population** declared | all | ✓ | §4 — 2 corrections, each enumerated before its first site was edited |
| 14 | **Emitted-form assertion** declared | all | ✓ | §4 — 4 assertions over the exported SVG; `AT-009`'s blindness to folding named |
| 15 | **Independent review** names somebody | all | ✓ | §4b — `code-reviewer` and `security-reviewer`, each re-reading the shipped tree at `f3398f4`; ⚠ dispatched in violation of catalog entry 15 and corrected mid-run, recorded in §4b |
| 16 | **Evidence files** declared | all | ⚠ | `none — this batch declares no artifact_homes.evidence`; declared gap, inherited, surfaced in §6 item 2 |
