# Increment 015 — Inc-CONFIRM (part 1) · `HERMETIC-1` and `B-68`

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` |
| Increment | `015` — Inc-CONFIRM, items 1 and 2 of 3 |
| Lane (if the batch forked) | `none — batch not forked` |
| Requirement(s) | `A-99` (new, this increment) · parent: `Inc-2` finding `H2` |
| Acceptance | `test_b68_the_export_is_invariant_under_the_operators_pan` · `test_b68_the_export_carries_nodes_the_viewport_could_not_hold` · `tests/test_hermetic.py` (5 nodes, 12 with parametrisation) |
| Agent | `software-dev` |
| Date | 2026-09-18 |

**Running order was ORDERED, not listed, and it was followed:** `HERMETIC-1` first because a gate
whose figures are taken under an undeclared condition certifies a conditional green; `B-68` second.
The third item (the routed pickups) is NOT in this increment.

---

## 1 · What changed

**The suite can now run offline, and an exported SVG no longer depends on where the operator was
looking.** Two defects, both closed, both with executed counterfactuals.

**`HERMETIC-1`.** A default-lane arm drove the real `gh` CLI against a live repository. The seam
(`mapper.app.GitHubConnector.fetch`) is mocked — the same seam the neighbouring `test_plug_repo_url_flow`
already mocked, so this is the module's own idiom applied to the arm that escaped it. **Zero source
files: the seam already existed.** Mocking the caught arm fixes the *instance*, so the axis is held
too: an autouse lane guard in `tests/conftest.py` refuses any network-reaching subprocess wherever the
new `network` marker is absent, and `tests/test_hermetic.py` carries an AST-derived census of every
executable the product can spawn, compared **both ways** against a declared classification table.

**`B-68`.** `action_export_svg` read the live pan through `_view_state` and sized the render from the
**terminal**, while `layered._geometry` shrinks `card_w` at that wider width until the tree fits —
collapsing `max_pan_x` to 0. A pan perfectly legal on the canvas was out of range for the export and
shifted content off the artifact's left edge: **47,263 bytes at pan (0,0) against 16,718 at the
reachable pan (49,10)**, roughly 65% of the map missing from a file handed to a third party. The fix
is in the **same expression** the `focus_owner=""` ruling already occupied — one `replace()` that now
neutralises `focus_owner`, `pan_x` and `pan_y` together — and the render is sized to the map's **full
extent**. The export is now **byte-identical under any pan**.

---

## 2 · Files modified

| File | Kind | Change |
|---|---|---|
| `mapper/app.py` | source | `action_export_svg` delegates to a new `MapScreen._export_view_state`; `EXPORT_EXTENT_STEPS` added |
| `pyproject.toml` | config | registers the `network` marker with its dependency declared; adds `not network` to addopts |
| `tests/conftest.py` | test | `network_reaching` classifier, `HermeticViolation`, the autouse `_hermetic_lane` guard, `pytest_plugins = ["pytester"]` |
| `tests/test_hermetic.py` | test | **new** — the spawn-site census, the classifier arms, the instrument RED-proof, the negative control, the nested-session arm, the `network`-marked bypass arm |
| `tests/test_app.py` | test | `test_repo_screen_two_pane_renders` mocks the seam and gains a painted-result assertion; `test_b50_…`'s double repaired |
| `tests/test_pan.py` | test | the two `B-68` acceptance arms, `_export_bytes`, `_svg_emitted_text`, `_squash` |
| `tests/test_search.py` | test | `_export_view_state` registered in `_PASS_FREE_READERS` with its reason |
| `tests/test_a3_census.py` | test | zero-arg pin 34 → 35; arg-ful pin 62 → 61; both itemised |
| `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md` | doc | Amendment set 7 — `A-99` |
| `.dev-flow/state.json` | doc | `HERMETIC-1` closed · `B-68` closed · `FLAKE-1` escalation recorded |

| Count | Value |
|---|---|
| **SOURCE files** | **1 / 4** (`mapper/app.py`) |
| Test files | 6 (uncapped) |
| Doc files | 3 (outside the count) |

`pyproject.toml` is counted as config rather than source; it is named here either way so the reader
does not have to take the classification on trust. Well under the cap.

---

## 3 · How to test

```bash
cd C:/Users/<operator>/Github/mapper
set PYTHONUTF8=1 && set PYTHONIOENCODING=utf-8

python -m pytest -q                    # default lane
python -m pytest -q -m slow            # slow lane
python -m pytest -q -m network         # network lane (the guard's bypass)
python -m ruff check --isolated --output-format=concise mapper tests

# the two subjects, directly
python -m pytest tests/test_hermetic.py -q
python -m pytest tests/test_pan.py -q -k b68
```

---

## 4 · Test results

**One complete run per lane, exit code and tail read from that run's own output.**

| Layer | Owed in | Nodes | Result |
|---|---|---|---|
| **0 · unit** | `core` · `full` | `network_reaching` (cyclomatic ≥3, classifies a crossing argv) | 8 passed — `test_network_reaching_classifies_each_real_invocation` |
| **A · white-box** | `core` · `full` | `tests/test_hermetic.py` census + instrument arms | 12 passed, 1 deselected |
| **B · black-box** | `fast` · `core` · `full` | the two `B-68` arms through the real `e` chord | 2 passed |

| Lane | Exit | Tail |
|---|---|---|
| default | **0** | `1109 passed, 20 deselected, 3 xfailed in 332.10s` |
| slow | **0** | `19 passed, 1113 deselected in 52.62s` |
| network | **0** | `1 passed, 1131 deselected in 1.23s` |
| ruff | — | **27 findings, SETS EQUAL AT EQUAL SCOPE** against the base mirror (base 27 / head 27, added none, removed none) |

**Baseline was 1095 / 19 deselected / 3 xfailed, ruff 27.** The default lane now deselects 20 because
the `network` lane took one arm out of it.

### Signed-balance test ledger

`post = base − deleted + added` → **`1109 = 1095 − 0 + 14`** ✓ reconciles.
Added: 12 in `tests/test_hermetic.py` (of 13 nodes; one is `network`-marked and deselected) + 2 `B-68`
acceptance arms. Deselected: `19 + 1` ✓. xfailed unchanged at 3 ✓.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Mutation applied | `B-68`: the export's state expression replaced by its pre-fix form (`focus_owner` neutralised, pan riding through, render sized from the terminal); and separately by the REJECTED clamp-only fix |
| Where it ran | **my own tree**, no other session reading it |
| Transcript | `R1-pre-fix-revert exit=1 → 2 failed, 26 deselected`; `R2-rejected-clamp-only exit=1 → 2 failed, 26 deselected`; baseline `2 passed`; anchor asserted to match **exactly once** before either applied |
| Restore proven by | **SHA-256 returned to its pre-mutation value** |
| Bytecode cache | `PYTHONDONTWRITEBYTECODE=1` (C-46); post-counterfactual run green |
| Arms resolved at baseline | **2**, asserted before the run |
| Verdict granularity | per resolved node — both arms named and both RED under each mutant |
| Arms that stayed GREEN | none |

| Field | Value |
|---|---|
| **RED counterfactual** | The export's state expression reverted to its pre-fix form — both acceptance arms RED (2 failed); and the rejected clamp-only fix substituted at the same site — both arms RED again, which is the limb that proves the arms distinguish *state removed* from *state bounded*. Transcript at `C:/Users/<operator>/clde/b68_counterfactual.py`'s run output (out of repo — see **Evidence files**). Restore digest `0a842a67170c2bac26dbef3f9d12f819377a322abb5bafd3cdef2b70c1954fa2`. |

**`R2` is the load-bearing limb.** The arm's own docstring claims byte-invariance separates a fix that
REMOVES the scroll position from one that merely BOUNDS it. That is a prediction about what a test will
do, and this batch's catalog says a prediction is measured, never labelled. It was measured: the
clamp-only fix reddens both arms.

| Field | Value |
|---|---|
| **Mutation verdicts** | 6 sites over `tests/conftest.py`, fired per SITE, substitution count asserted, verdicts printed before the restore asserts. `M1` `gh` dropped from the always-remote set → **KILLED**. `M2` `fetch` dropped from the remote-git subcommands → **KILLED**. `M3` refusal no longer recorded → **KILLED**. `M4` refusal no longer raised → **KILLED**. `M5` teardown assertion defanged → **SURVIVED on the first run, KILLED on the second** after the nested-session arm was written for it. `M6` negative control (comment-only edit at the `-C` branch) → **SURVIVED, as required**. Arms that stayed green: none in the final run. Restore sha256 byte-identical, post-battery suite green. Transcript out of repo — see **Evidence files**. |

**`M5` is recorded as a survivor that was then killed, not as a clean sweep.** The teardown half of the
guard — the half that catches a violation product code has SWALLOWED — was held by nothing on the first
battery. A survivor explained away is a survivor, so the killer was built
(`test_a_swallowed_refusal_still_reddens_the_arm`, a nested `pytester` session, because no in-process
arm can watch its own teardown fail).

### Instrument RED-proof

| Instrument | Known-bad input fed to it | The FAILURE it reported |
|---|---|---|
| the lane guard (`_hermetic_lane`) | **the real defect**, not a synthetic argv: the guard installed with the seam still unmocked | `HermeticViolation: the default lane may not reach the network: gh repo view jav201/taskboard --json name,defaultBranchRef` — and independently `AssertionError: HERMETIC-1: this test reached the network`, in 0.64s |
| `network_reaching` classifier | the product's own `git -C <path> fetch --all` | RED — it returned `False`: `-C` was skipped but **not its value**, so a directory path was read as the subcommand. A real defect in the instrument, found by measurement |
| the ruff set-comparison harness | its own parse, on ANSI-coloured input | RED — `AssertionError: BASE parse produced ZERO rows — the instrument is broken, not the tree`. It had previously printed `SETS IDENTICAL` while comparing two **empty** lists |
| the SVG text reader (`_svg_emitted_text`) | the artifact, searched for the human-readable `"rama 5"` | 0 of 14 titles found on an artifact that plainly contains them; 8 `rama` + 8 `hoja` once the runs are reassembled |
| the mutation harness | an anchor that matches 0× (LF anchors against a CRLF tree) | `AssertionError: anchor matched 0x, needs exactly 1 — a mutation that never applied reads as a survivor` |
| the `b50` oracle, after its double was repaired | `diff=None` forced into the exported state | **KILLED** — the arm still bites, so repairing the double cost it no discriminating power |

| Field | Value |
|---|---|
| **Instrument RED-proof** | 6 instruments, each shown RED before any PASS from it was believed. Three of the six reported a **real defect in themselves** (the `-C` value bug, the ANSI parse, the CRLF anchor), which is the control paying for itself rather than ratifying. |

### Emitted-form assertion (C-42)

| Artifact emitted | The assertion, run against the EMITTED form | What it returned |
|---|---|---|
| the exported SVG | literal search for the node title `"rama 5"` | **0 matches** on a 52,915-byte artifact that contains it — Rich writes one `<text>` element per style run, so no title is ever a substring |
| the exported SVG | the same titles, after reassembling runs per `line-N` clip path and unescaping | `rama` **8**, `hoja` **8**, the `nivel` chain present; padding spaces are not emitted, so the arm compares with whitespace stripped from both sides |

| Field | Value |
|---|---|
| **Emitted-form assertion** | 1 artifact (the exported SVG), asserted against the form its producer emits. The first oracle was written against the rendered form and false-failed the correct implementation on all 14 off-screen titles — `C-42`'s exhibit, reproduced exactly. |

### Evidence files

| Evidence artifact | Path — under `artifact_homes.evidence` | SHA-256 |
|---|---|---|
| — | — | — |

| Field | Value |
|---|---|
| **Evidence files** | `none — this batch declares no artifact_homes.evidence`. ⚠ **This is a DECLARED GAP, not an omission.** `state.json::artifact_homes` has ten keys and `evidence` is not among them, so there is no home to write to and no digest to re-derive from a stored path. Every transcript this packet quotes was produced out of repo under `C:/Users/<operator>/clde/` — the condition the outgoing agent declared for its own probes, inherited rather than introduced here. Minting an evidence home mid-batch is a scope decision for the coordinator, so it is **surfaced in §6** rather than taken. The transcripts are quoted verbatim in this packet, which is what makes the figures checkable in the meantime. |

### Load-bearing emptiness (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | **Yes, twice.** (1) The `network` lane holds no live-`gh` arm. (2) Nothing in the suite reaches a viewer launch (`os.startfile` / `open` / `xdg-open`) |
| If the result is an ABSENCE, what made the search wide enough | The spawn census is derived by AST over `mapper/**/*.py` and matches only `subprocess.<spawn>` receivers, which is what excludes the `app.run` false positive; it is compared **both ways** against `DECLARED_SPAWNS` |
| Guard labelled as protecting a CONCLUSION, not a behaviour | `test_every_product_spawn_site_carries_a_hermeticity_classification` — its docstring says it protects the classification's completeness, and it asserts `derived` is non-empty first, so a broken walk cannot pass it |
| Conjunctive criteria: one mutation per conjunct | The guard's two conjuncts were mutated separately: `M3` (recording) and `M4` (raising), plus `M5` (the teardown assertion). All three KILLED |
| Synthetic instance of the absent case | The `network` lane's emptiness is discharged by `test_the_network_marker_lifts_the_guard`, a `network`-marked arm written so the bypass branch is exercised by something even though no live-`gh` arm exists |
| **Positive control for every probe that returned an ABSENCE** | `test_the_guard_does_not_false_fail_local_git` — the same guard, unmodified, over a known-present legal case (`git init`, `git -C … rev-parse`), returns a NON-absence: it permits them, and the six `tests/test_github.py` local-repository arms pass under it |

The viewer-launch absence is the one this increment does **not** discharge. It is classified in
`DECLARED_SPAWNS`, named in `VIEWER_LAUNCH_UNGUARDED`, and carried in §6 — declared, not closed.

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rn "action_export_svg\|_view_state\|_consumes_pan" tests/` | **HIT.** `test_b50_…` (repaired — see below), `test_search.py`'s paint-pass census (`_export_view_state` registered in `_PASS_FREE_READERS`), `test_pan.py`'s `_consumes_pan` raise arm (unaffected — still passes) |
| B2 file moved on disk | no path moved in this increment | **did not fire** — `git status --short` shows no rename; probe run and empty |
| B3 byte-identical golden captures this source | `grep -rn "export" tests/goldens/**` | **no goldens directory exists**; probe run, 0 hits |
| B4 artifact produced here is consumed elsewhere | the exported `.svg` — `grep -rn "\.svg" tests/ mapper/` | **HIT.** `AT-009` reads it back from disk; `test_b50_…` intercepts `save_svg`. Both re-validated: `AT-009` green, `b50` repaired and re-proven against its own mutant |
| A3 interface consumed by another module changed | `grep -rn "_export_view_state\|EXPORT_EXTENT_STEPS" mapper/` | **0 hits outside `mapper/app.py`** — the new method is private to `MapScreen` and has exactly one caller. No cross-module interface changed |

| Field | Value |
|---|---|
| **Reverse census** | 5 probes run — B1 · B2 · B3 · B4 · A3. **3 fired** (B1, B4, A3-negative), 2 did not (B2, B3), each with its command and verdict recorded above. Every hit re-validated: the `b50` hit was a **real regression this increment introduced**, measured against the pristine base (12/12 green there, intermittent on mine) and closed by making the test double faithful rather than by softening the arm — its `diff=None` mutant is still KILLED. The A3 probe returned zero hits, which is the intended answer, not a skipped probe. |

### Correction population

| Field | Value |
|---|---|
| **Correction population** | `none — no correction`. This increment corrects no claim that appears in more than one artifact. The two A3 census pins moved, but they are a **derived count**, not a restated claim: both are re-derived mechanically from the same AST walk, and the arm asserts them together so a change to one without the other is red by construction. |

---

## 4b · Independent review

| Field | Value |
|---|---|
| **Independent review** | `code-reviewer` · **BLOCK — BLOCK-UNTIL: CR-F1** (1 HIGH) · NOT resolved. `security-reviewer` · **BLOCK — BLOCK-UNTIL: SEC-F1, SEC-F2** (2 HIGH) · NOT resolved. Verdicts at `increment-015-confirm-code-review.md` and `increment-015-confirm-security-review.md`. |

Inc-CONFIRM is classified **FULL protocol** by ruling `D35`, so both passes are owed. The tree was
frozen for the duration of both reads, and **no fix has been applied since** — a HIGH is never
self-cleared, and all three are open.

**THREE HIGH FINDINGS, NONE RESOLVED. THIS INCREMENT DOES NOT GATE.** The soft cap is 3 blocks per
increment, so it is surfaced to the coordinator rather than worked around.

| Id | Reviewer | Finding | Status |
|---|---|---|---|
| `CR-F1` | `code-reviewer` | **The `B-68` invariance arm passes on a totally broken export.** `_export_bytes` presses `e` and reads the file off disk without proving the press wrote anything; `action_export_svg` swallows failures into a toast, so the second read can return the FIRST press's file and the arm compares a file against itself. Measured: a mutant making the export raise at every non-zero pan — the exact condition `B-68` is about — leaves **both** acceptance arms GREEN. | OPEN. Remedy known and reviewer-verified (unlink before the press, assert the artifact exists after). Not applied. |
| `SEC-F1` | `security-reviewer` | **The fix scrambles the artifact above ~17 leaves.** `mapper/export.py:17` builds the export console at a hard-coded `width=200`. Full extent is 241 columns for a 21-node map and 48,013 for the fanout shape, and Rich FOLDS every row past 200 into stacked chunks in row-major order — adjacency destroyed, file still well-formed and complete-looking. `B-68`'s own failure class one layer down, **introduced by this fix**. Both arms miss it because `pan_graph`'s full extent is 120 columns, below the fold threshold. | OPEN. Needs a second source file and changes every outgoing artifact. Not applied. |
| `SEC-F2` | `security-reviewer` | **The declared worst case was wrong — 12x at an ordinary map, ~500x at the product's cap.** Export cost follows BOUNDING-BOX AREA (`Canvas.rows()` is a dense `w x h` walk), not node count. Measured 169.1 s / 363 MB at 1,801 nodes; the worst shape within `MAX_RENDER_NODES = 12000` is wide AND deep at once, extrapolating to ~125 min and ~16 GB on the synchronous message pump. | OPEN. **The false figure is corrected in §5/§6 below.** The disposition is a coordinator ruling. |

**`SEC-F2` is a defect in MY OWN measurement, and it is `C-31` exactly.** I probed fanout-only and
chain-only shapes from a hand-listed set; the failing member — wide and deep *together* — was omitted.
The arithmetic was right and the domain was wrong, which is that control's precise shape, and it is the
one control I had already cited in this very packet. The 14.42 s figure first written into §6, `A-99`
and `state.json` is **false and has been replaced rather than annotated**, because a correction that
adds the true statement without removing the false one leaves the document asserting both.

**A gap in my own reverse census, surfaced by `SEC-F1`.** The `B4` probe above asked *who consumes the
artifact* and answered correctly — but never asked *what the consumer assumes about it*.
`mapper/export.py::save_svg` consumes the rendered `Text` under a hard-coded 200-column assumption that
my change invalidates, and no probe keyed on consumption alone could see that. Recorded here because
the census was run honestly and still missed it.

---

## 5 · Risks

- **`action_export_svg` is synchronous and its wall clock is unbounded in map shape — and the figure
  first recorded here was FALSE.** I wrote *14.42 s worst case*, measured on a 4001-way fanout. The
  independent security pass measured the shape I omitted — wide AND deep at once — and found cost
  follows the **bounding-box area**, because `Canvas.rows()` walks a dense `w x h` grid: **169.1 s and
  363 MB at 1,801 nodes**, extrapolating to **~125 minutes and ~16 GB** at the product's own
  `MAX_RENDER_NODES = 12000`, paid on the message pump with no progress, no cancel and no
  confirmation. The superseded 14.42 s figure is **struck, not annotated**. No cap was added, because
  a silent cap reintroduces an undeclared crop — which is the defect — and because the ruling that
  authorised full extent says to bring the number back rather than implement around it.
- **`SEC-F1`: the fix as it stands degrades the deliverable above ~17 leaves.** Until `export.py`'s
  200-column console is resolved, a full-extent export of any non-trivial map is structurally
  scrambled. This is not a residual risk; it is an open HIGH.
- **The lane guard patches `subprocess.run`/`Popen` for every test.** It **delegates** for everything
  not network-reaching, so the blast radius is limited to refusals — and the six local-git arms are
  the standing negative control. But a future test that spawns a remote-reaching process *through a
  path the classifier does not model* (a shell string rather than an argv list) would pass unseen:
  `network_reaching` returns `False` for a `str` argv by design, because it cannot tokenise reliably.
  Declared here rather than guessed at.
- **Full-extent export changes what every downstream consumer of the `.svg` receives** — the file is
  now larger and framed differently. `AT-009` and the `b50` arm both still pass, but any human
  expectation of "the export looks like my screen" is deliberately broken. That is the ruling.
- **`FLAKE-1` fired during this increment** and is not closed. A green lane containing it is a weaker
  green, as the batch already records.

---

## 6 · Pending items / spec deviations

1. **`action_export_svg` responsiveness — OPEN HIGH (`SEC-F2`), not a carry.** The worst case is
   **169.1 s / 363 MB measured at 1,801 nodes**, extrapolating to ~125 min and ~16 GB at
   `MAX_RENDER_NODES`. Cost follows bounding-box AREA, not node count. **This supersedes the 14.42 s
   figure I first recorded, which was false.** It is no longer a question routed to the whole-branch
   gate: it goes back to the coordinator now, because the ruling that authorised full extent made
   itself conditional on exactly this measurement (`S-15`: *cost follows paths, not nodes*).
2. **Viewer launches are unguarded** (`mapper/osopen.py`: `os.startfile` / `open` / `xdg-open`).
   Offline, so outside `HERMETIC-1`'s ruled axis, but still external side effects with nothing
   stopping them. Classified and named; **not closed**.
3. **`artifact_homes.evidence` is not declared for this batch**, so no transcript in this increment
   can be evidence under `C-59`. Surfaced for a coordinator decision rather than minted mid-batch.
4. **`FLAKE-1` fired again** — escalation clause triggered and its read-only investigation performed
   (12/12 isolated, 3/3 module scope, no reproduction below full-lane scope; rate now 2 in 9 full-lane
   runs across two bases). **Still owed at the whole-branch gate.** The next step is capturing the
   FAILING ORDER, not more isolated reruns.
5. **Outline/radial export truncation** — a sibling of `B-68` that this ruling did not cover and this
   increment did not widen into. An outline export is still sized from the terminal.
6. **Inc-CONFIRM item 3 is not started**: `F3`→qa-reviewer, `F7`→ux-reviewer, `SEC-H2`, `UI-AT058`
   (plus `PAN_INERT_HINT` / `"esta vista no se desplaza"`), the `B-64` driven sweep.
7. **The validator still exits 1**, as `external_blocks` records. My run measured **15 blocks**
   against the recorded **16**; the delta is stated rather than reconciled — `V7` did not appear in my
   run, consistent with the bundle's revision label having been repaired upstream. All 15 are
   pre-existing `V53` anchor findings in sealed records.

---

## 7 · Suggested next task

**Inc-CONFIRM item 3** — the routed pickups, once the two reviews above return. `F3` and `F7` are
independent-lens items and can be dispatched in parallel; `SEC-H2` and the `UI-AT058` register check
are reads; the `B-64` driven sweep has its probe at `C:/Users/<operator>/clde/b49_probe.py` and must DRIVE
the derived set rather than a hand-built model of it.
