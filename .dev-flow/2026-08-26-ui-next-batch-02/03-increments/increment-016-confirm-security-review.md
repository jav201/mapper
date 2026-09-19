# Security Review — Increment 016 · `Inc-CONFIRM` re-ruled · `A-100` · `B-68`

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` (sealed) · FULL protocol per ruling `D35` |
| Reviewer | `security-reviewer`, independent — authored none of this diff, fresh pass |
| Commit | `f3398f4` on `feat/ui-next-batch-02`, base `a552783` |
| Date | 2026-09-19 |
| **Verdict** | **OK from the security lens — 0 HIGH open.** `SEC-F1`, `SEC-F2`, `SEC-F3`, `SEC-F6` measured CLOSED by this pass. 5 MEDIUM + 4 LOW recorded, none blocking. **This authorises nothing** — see *Verdict*. |

> **No HIGH was cleared on the corrective pass's own report.** Every closure below
> rests on a measurement I took myself, on the shipped tree, with the instrument
> first shown able to report FAILURE. Where my measurement disagrees with the
> packet, mine is stated and the packet's is named.

---

## Mirror, and hash-stability of what was measured

Per the coordinator's mid-task correction (catalog entry 15 — *reviews are serial
by default; parallel review requires one isolated, digest-verified mirror per
reviewer*), all probing, mutation and lane work ran **outside the repo**, in a
mirror that is mine alone:

`C:\Users\jjgh8\AppData\Local\Temp\claude\C--Users-jjgh8-clde\5fba800c-287a-459a-b7c8-dd44777ea077\scratchpad\sec016`

| Item | Result |
|---|---|
| Mirror created | before the correction arrived, by `tar` from the repo working tree — I had **already** chosen an isolated mirror, so nothing was measured in the shared tree |
| Verified against source | all 91 census-relevant tracked files (`mapper/**`, `tests/**`) **byte-identical**; the five subject files match the shipped digests |
| Tree-wide digest | `2959ddb4f523ab2f1b0d9d12e1c4b467…` over 299 tracked files — **equals the coordinator's quoted value** |
| Digests re-asserted at end | **ALL HELD.** Tree digest unchanged; `app.py` `914afcb8b0a364a6`, `export.py` `56773345bc4731f1`, `state.py` `bf239adef8e1c159`, `test_pan.py` `e65128c51866fa05`, `conftest.py` `c1acf140b03d3301`, `github.py` `d9bd9853e5214855` |
| Written in the repo by me | **this file only.** `HEAD` still `f3398f4`; no tracked file moved |

**Two process facts found while doing this, both reported under `S-F13`/`S-F14`:**
another writer was creating files in the "frozen" repo tree during my read, and
the editable install defeats mirror isolation by default.

---

## Scope reviewed

`git diff a552783 f3398f4` — 17 files, +3312/−63.

- **Source:** `mapper/app.py`, `mapper/export.py`, `mapper/views/state.py`
- **Config:** `pyproject.toml`
- **Tests:** `tests/conftest.py`, `tests/test_export_state.py` (new), `tests/test_hermetic.py` (new), `tests/test_pan.py`, `tests/test_app.py`, `tests/test_search.py`, `tests/test_a3_census.py`
- **Blast radius read, not diffed:** `mapper/views/layered.py`, `mapper/canvas.py`, `mapper/osopen.py`, `mapper/github.py`, `mapper/store.py`
- **Records read first:** `state.json` (41-entry control catalog, `coordinator_rulings`, `open_blocks`, `hermetic_defects`), `increment-015-confirm{,-code-review,-security-review}.md`, `increment-016-confirm-reruled.md`, `01-requirements.md` amendment sets 7–8 (`A-99`, `A-100`)

**Lanes and ruff, re-run by me in the mirror — all four reproduce the packet exactly:**

| Lane | My run | Packet |
|---|---|---|
| default | `1133 passed, 20 deselected, 3 xfailed in 347.02s` | `1133 passed, 20 deselected, 3 xfailed` ✓ |
| slow | `19 passed, 1137 deselected` | `19 passed` ✓ |
| network | `1 passed, 1155 deselected` | `1 passed` ✓ |
| ruff `--isolated` | **27** | 27 ✓ |

---

## Findings

### `SEC-F1` — the artifact was folded at 200 columns  [Severity: HIGH] → **CLOSED**

- **What was owed:** `save_svg` must size the export console from the `Text` it is handed, in terminal **cells**, so no rendered row arrives split.
- **Where:** `mapper/export.py:57` — `width = max(20, max((cell_len(line) for line in lines), default=20)) + 1`.
- **Measured, by me, through the real `e` chord** (not a replica of the growth loop): I drove `MapperApp` → `_export_view_state` → the product's own renderer → `save_svg`, then reassembled the emitted SVG per `line-N` clip path ordered by `x`, and asked whether each **rendered row survives whole**:

  | leaves | export `w×h` | widest row | split rows, shipped | split rows, `width=200` | split rows, `+1` dropped |
  |---|---|---|---|---|---|
  | 8 | 118×24 | 121 | **0** | 0 | 1 |
  | 12 | 145×25 | 149 | **0** | 0 | 1 |
  | 16 | 193×25 | 197 | **0** | 0 | 1 |
  | 20 | 241×25 | 245 | **0** | **3** | 1 |
  | 40 | 481×25 | 485 | **0** | **3** | 1 |
  | 120 | 1441×25 | 1446 | **0** | **3** | 1 |

- **Instrument RED-proof:** my first run of this probe reported *0 split rows under `width=200`* — a false green. Cause: `sys.path[0]` for a script is the **script's** directory, so the probe imported `mapper` from the real repo via the editable `.pth` while I mutated the mirror. I caught it by the counterfactual refusing to fire, added an assertion that `mapper.__file__` is under the mirror, and re-ran. Every figure above is from the guarded probe. Reported in full under `S-F14` because it is a trap anyone repeating this work will hit.
- **Independent reproduction of the predecessor's threshold:** no fold at 16 leaves, folding from 20 — the ~17-leaf threshold, reached from my own fixture.
- **Verdict:** **CLOSED.** The fix is correct and is measured correct on the shipped tree. The `+ 1` is load-bearing exactly as documented: dropping it splits one row at *every* size, including the smallest.

### `SEC-F2` — export cost follows bounding-box AREA, paid on the message pump  [Severity: HIGH] → **CLOSED on the hazard; its derivation is re-opened as `S-F9`**

- **What was owed:** the unbounded synchronous freeze (~125 min / ~16 GB inside `MAX_RENDER_NODES`) must be gone, via a cell budget with a stated derivation and a **refusal that is not a crop**.
- **Where:** `mapper/app.py::MapScreen.EXPORT_MAX_CELLS` / `_within_export_budget` / `_export_view_state`; `mapper/export.py::ExportTooLarge`.
- **Measured, by me — is the hazard gone on EVERY export path?** This is the question the budget alone does not answer, because the budget is checked *after* `pan_extent` and is *vacuous* for renderers that decline the resize. I drove all three renderers at the product's own node cap:

  | renderer | nodes | consumes pan | export cells | cost |
  |---|---|---|---|---|
  | `OutlineRenderer` | 11,999 | no | 2,832 (terminal-sized) | **0.17–0.20 s** |
  | `RadialRenderer` | 11,999 | no | 2,832 (terminal-sized) | **0.18–0.35 s** |
  | `LayeredRenderer` | 11,999 | yes | — | **REFUSED in 0.12 s**, nothing written |

- **And is the refusal itself cheap?** Yes — the budget check sits downstream of `pan_extent`, so I timed the refusal:

  | nodes | verdict | `_export_view_state` | whole `e` chord | wrote a file? |
  |---|---|---|---|---|
  | 301 | REFUSED | 0.001 s | 0.229 s | **no** |
  | 1,501 | REFUSED | 0.005 s | 0.451 s | **no** |
  | 4,501 | REFUSED | 0.017 s | 0.106 s | **no** |
  | 11,999 | REFUSED | 0.121 s | 0.126 s | **no** |
  | 11,901 | REFUSED | 0.124 s | 1.200 s | **no** |

- **And the worst ACCEPTED export:** 350,000 cells at my measured 0.94–1.37 µs/cell ⇒ **≈0.33–0.48 s**.
- **Refusal driven end to end** (real `e` chord, 301-node map): no artifact written; notice reads
  `mapa demasiado grande para exportar: 974852 celdas, límite 350000. Enfoca un subárbol con f y exporta esa vista.` — extent ✓, limit ✓, route ✓, `severity=warning`, `markup=False` ✓.
- **Verdict:** **CLOSED.** On every path reachable through `action_export_svg`, the export either renders cheaply, or refuses cheaply and writes nothing. The multi-minute uninterruptible freeze is not reachable. **A refusal is not a crop** holds: I found no partial-artifact path, and the exhaustion branch raises `ExportError` with its own reason rather than shipping what it had.
- **What does NOT survive:** the *derivation* of `350_000`. See `S-F9` — it does not change the verdict here, because the error is in the conservative direction.

### `SEC-F3` — `selected_id` and `hits` rode into the artifact; owed a CENSUS  [Severity: MEDIUM, escalated] → **CLOSED**

- **Where:** `mapper/views/state.py::EXPORT_FIELD_KINDS` / `TRANSIENT_EXPORT_FIELDS` / `export_neutralised`; consumed at `mapper/app.py::_export_view_state`.
- **Measured (completeness, both ways):** `fields(ViewState)` = `EXPORT_FIELD_KINDS` keys exactly — 9/9, zero either side. Kinds ⊆ {`transient`,`content`,`geometry`}. Transient set = `{selected_id, focus_owner, hits, pan_x, pan_y}`; `diff` and `folded` are `content` with stated in-band reasons; `w`/`h` are `geometry`.
- **Measured (the classification is ASSERTED, not inherited):** I added an unclassified field `last_query: str = ""` to `ViewState` in my mirror. `test_every_view_state_field_is_classified_for_the_export_boundary` went **RED** (`Extra items in the left set: 'last_query'`), 1 failed / 12 passed. A new field cannot inherit its neighbour's behaviour silently. Restored byte-identical (`bf239adef8e1c159`).
- **Measured (the leak itself, end to end):** built a map containing a node titled `CONTRATO-ACME-CONFIDENCIAL 7`, exported at rest, then ran a **live search** resolving to that node, moved the cursor onto it, and panned to `(20,3)` — then exported again:

  | | sha256 (16) | bytes |
  |---|---|---|
  | at rest | `6aa11adb3e42df4b` | 74,770 |
  | live search + cursor + pan | `6aa11adb3e42df4b` | 74,770 |

  **Byte-identical.** The state handed to the renderer carried `hits=frozenset()`, `selected_id=None`, `pan=(0,0)`. The precondition was asserted first (`_search_hits() == {'h7'}`), so this is not vacuously green.
- **Verdict:** **CLOSED.** The sender-side leak — *what the operator was searching for* — does not reach the artifact. One residual, LOW, recorded as `S-F12`.

### `SEC-F6` — `guarded_run` raised `TypeError` on `subprocess.run(args=[...])`  [Severity: LOW] → **CLOSED**

Measured in the bypass matrix below: `subprocess.run(args=["gh","--version"])` is **REFUSED by the guard**, not a `TypeError`. `tests/conftest.py::_argv_of` reads the keyword form. The positive control (`test_the_guard_does_not_false_fail_local_git`) is present and green.

### `SEC-F4` — the `eliminados` diff ghost strip rides into the export  [Severity: MEDIUM] — **OPEN, disposition ADEQUATE**

- **Where:** `mapper/views/layered.py:672-681` — the strip prints `removed_titles` for each `removed_id`, gated on `diff`.
- **Read, not widened:** `diff` is classified `content` **with its reason asserted in the table**, so the inclusion is now a declared decision rather than an oversight, and the strip is labelled `eliminados` **in the artifact**, so the recipient can see what they are looking at. The party surprised is the **sender**, whose previous-revision node titles travel in a file they believed showed only what was on screen — and the export *grows the canvas*, so the strip can be in the artifact when it was not on the screen.
- **Why the disposition is adequate for this increment:** pre-existing, not raised by this round, declared in three places (packet §5, §6.1 and `A-100`'s closing ⚠), and bounded to the operator's own map data. It wants a one-line ruling, not code.
- **I did not widen into it**, per the brief.

### `SEC-F5` — lane-guard bypass matrix  [Severity: MEDIUM] — **cheap half CLOSED; axis recorded PARTIALLY HELD, never held**

Measured by me on the shipped tree, inside a real pytest run so the autouse guard was installed:

| form | verdict |
|---|---|
| `subprocess.run(argv)` | **REFUSED** ✓ |
| `subprocess.run(args=argv)` | **REFUSED** ✓ (`SEC-F6`) |
| `subprocess.Popen(argv)` | **REFUSED** ✓ |
| `subprocess.run("gh --version", shell=True)` | **REFUSED** ✓ |
| `os.system("gh --version")` | **REFUSED** ✓ |
| `subprocess.check_output(argv)` / `call(argv)` | **REFUSED** ✓ |
| `from subprocess import run` | **REFUSED** ✓ (via the patched `Popen` underneath) |
| **`from subprocess import Popen`** | **SILENT BYPASS** ✗ — the process really spawned |
| in-process HTTP (`urllib.request`) / raw socket | **structurally invisible** ✗ |

- **Record the axis as PARTIALLY HELD, never held.** Confirmed.
- **Two corrections to the packet's own residual statement, in the direction of accuracy:**
  1. The packet's §5 says "`curl`/`wget`/`ssh` **via a shell string** … walk past it." **They do not** — a `str`/`bytes` argv is refused outright and `os.system` is patched. The measured residual is narrower than declared: early-bound `Popen`, plus any in-process client.
  2. The sharp half is stated as "`mapper/github.py` already imports `urllib`." It imports **`urllib.parse`** (line 17), which performs no I/O. The *risk* is real and unchanged — a subprocess-level guard cannot see an in-process HTTP client — but the cited evidence does not itself demonstrate an HTTP capability. Worth fixing in the record so the carry rests on the argument rather than on an import that does not bear it.
- Socket-level guard remains its own increment. **CARRY, not closed.**

### `SEC-F7` — viewer launches unguarded  [Severity: LOW — NOTE] — **declaration ADEQUATE**

`mapper/osopen.py` is untouched by this diff and its product-side control is strong and present: kind allowlist, scheme allowlist (`http`/`https` only, `file:` deliberately excluded), userinfo rejection, C0/C1 control-character rejection, workspace confinement checked **before** the launcher, and no shell. The lane guard does not patch `os.startfile`, which is a **declared** gap pinned by `test_the_viewer_launch_class_is_complete_and_still_unguarded` — derived by AST, so it reddens if the class changes. Adequate.

### `SEC-F8` — secrets  [Severity: LOW — NOTE] — **clean, re-run by me**

Scanned the **full** diff (`a552783..f3398f4`, all 17 files) for `api_key`/`secret`/`token`/`password`/`Bearer`/`ghp_`/`gho_`/`github_pat_`/`xox[baprs]-`/`sk-…`/`AKIA…`/`-----BEGIN … PRIVATE KEY`. **Zero credential values.** Hits are prose, the word "token" in `git` sub-command parsing, and one test fixture string `"secreto"` (`tests/test_export_state.py:2731` of the diff) used as a node title to prove the export strips it — a fixture, not a credential. No secret value appears anywhere in this report.

**Supply chain:** the `pyproject.toml` diff touches `[tool.pytest.ini_options]` only — **no new dependency, no version change, no install script**. Clean.

---

### New findings from this pass

### `S-F9` — the `EXPORT_MAX_CELLS` derivation is measured under an allocation profiler and overstates real cost by ≈5.4×  [Severity: MEDIUM]

- **What:** `A-100` calls the derivation **normative**, and `mapper/app.py::EXPORT_MAX_CELLS` states it as a measured bracket: *315,252 cells → 1.801 s*, *490,052 cells → 2.631 s*, cross-checked at *5.4264 µs/cell*, against a **2-second** freeze target. Re-measured on the shipped tree, driving the product's own path, the rate is **0.9448 µs/cell**.
- **Where:** `mapper/app.py:3505-3545` (the `EXPORT_MAX_CELLS` docstring) and `01-requirements.md::A-100` ("The budget is in CELLS, and the derivation is normative").
- **Measured — the cause, isolated by A/B on identical points, back to back under identical load:**

  | nodes | cells | profiler OFF | profiler ON | ratio |
  |---|---|---|---|---|
  | 181 | 354,532 | **0.370 s** | 2.086 s | 5.64× |
  | 242 | 630,180 | **0.660 s** | 3.485 s | 5.28× |
  | 301 | 974,852 | **0.919 s** | 4.977 s | 5.42× |
  | 361 | 1,400,212 | **1.286 s** | 7.050 s | 5.48× |

  | arm | through-origin rate | 2.000 s falls at | 350,000 cells costs |
  |---|---|---|---|
  | **OFF** (what an operator pays) | **0.9448 µs/cell** | **≈2,116,951 cells** | **0.331 s** |
  | **ON** (the harness) | 5.1430 µs/cell | 388,882 cells | 1.800 s |

  The ON arm reproduces the packet's own figures. **The cause is in the harness, read from source, not inferred:** `C:\Users\jjgh8\clde\b68_budget_probe.py:68-75` runs `tracemalloc.start()` **immediately before** `t0 = time.time()` and stops it after the render and `save_svg` — the allocation profiler is live inside the timed region, and this render is allocation-bound. The predecessor's `sec_b68_real_cost.py:55-57` has the identical shape, so **both** the struck 4.907 µs/cell and its 5.4264 µs/cell replacement come from the same contaminated instrument.
- **Why it matters:** by the batch's own **STRIKE-OR-ANNOTATE** control (catalog entry 0 — *was the number a faithful record of what was measured, or a false claim about the world?*), the replacement is a faithful record **taken under an undeclared condition**, and the conclusion drawn from it — *350,000 cells ≈ 2 s of operator-visible freeze* — is a claim about the world that re-measurement contradicts by 5.4×. The correction changed the number and kept the instrument. The control fired on the correction it minted.
- **Reachable today:** yes, as lost capability rather than as a hazard. A 301-node map costing **0.92 s** is refused (I drove it: `974852 celdas, límite 350000`). The budget is roughly **6× tighter** than its own stated target.
- **Direction, stated plainly:** the error is **conservative** — the product refuses earlier than it needs to. Nothing is unsafe, which is why this does not re-open `SEC-F2`.
- **Recommendation:** re-measure with `tracemalloc` outside the timed region (or with `time.perf_counter` around a profiler-free run), then either move the constant or re-justify it. **`A-100`'s UTILITY ground is untouched and stands on its own** — a 48,013-column SVG is unreadable regardless of cost — so the honest fix may be to keep `350_000` and re-ground it on utility, striking the cost arithmetic rather than the constant. What must not survive is a *normative* derivation that a clean re-measurement contradicts.

### `S-F10` — `cell_len` is correct and UNPINNED: the suite stays green with `len()`, while wide glyphs fold  [Severity: MEDIUM]

- **What:** `mapper/export.py:57` argues at length for `cell_len`, never `len`. The argument is right — but nothing in the suite can fail if it is reverted.
- **Measured:** substituting `len()` for `cell_len()` and running `tests/test_export_state.py tests/test_export.py tests/test_pan.py` → **45 passed**. The same substitution, driven through the real `e` chord on a map whose titles are CJK/kana (`概念地图ノード`, `len`=7, `cell_len`=14):

  | leaves | max `len` | max `cell_len` | split rows, `cell_len` | split rows, `len` |
  |---|---|---|---|---|
  | 8 | 121 | 172 | **0** | **1** |
  | 20 | 245 | 339 | **0** | **1** |
  | 40 | 485 | 679 | **0** | **1** |

- **Why it matters:** the `M3`/`M4` battery mutates *the constant* and *the `+ 1`*, but never `cell_len`→`len`. The guard has three conjuncts and two are pinned. The defect the third prevents is exactly `SEC-F1`'s class — an artifact that looks complete and is not — and it is reachable by any operator whose node titles contain CJK, kana or emoji. **Every new guard owes a control showing it can still fail**; this conjunct has none.
- **Recommendation:** one parametrisation of `test_no_rendered_row_is_folded_in_the_artifact` with a wide-glyph title. The existing oracle catches it unchanged — I verified that by measurement.

### `S-F11` — the AST spawn census is blind to the keyword argv form, the very form `SEC-F6` just fixed in the guard  [Severity: MEDIUM]

- **What:** `state.json::hermetic_defects` records the census as *"A new spawn site with no hermeticity verdict reddens."* It does not, for `subprocess.run(args=[...])`.
- **Where:** `tests/test_hermetic.py:112` — `if not node.args: continue`, then `argv = node.args[0]`. Positional only.
- **Measured, discriminating pair** — I injected the same new spawn of an **undeclared** executable into `mapper/github.py` twice:

  | form injected into product code | `test_every_product_spawn_site_carries_a_hermeticity_classification` |
  |---|---|
  | `subprocess.run(["curl", "-s", url])` | **FAILED** ✓ (the census works) |
  | `subprocess.run(args=["curl", "-s", url])` | **passed** ✗ (invisible) |

  Restored byte-identical (`d9bd9853e5214855`).
- **Why it matters:** `SEC-F6` taught this increment that `args=` is a legal form a real caller uses; the lesson was applied to the runtime guard and not to the AST census that derives the population. The census's whole purpose is to catch the site **no test exercises** — precisely the case where the runtime guard cannot help.
- **Mitigating:** defence in depth holds — if such a site is ever *executed* in the default lane, the runtime guard now refuses it. This is a completeness gap in the declaration, not an open network path.
- **Recommendation:** in `_derived_spawn_executables`, read `node.keywords` for `args=` alongside `node.args[0]` — the same two lines `_argv_of` already uses.

### `S-F12` — `export_neutralised` fails OPEN at runtime for an unclassified field  [Severity: LOW]

- **Measured:** with `last_query` added and unclassified, `export_neutralised(ViewState(last_query='CONTRATO-ACME'))` returns `last_query='CONTRATO-ACME'` — the field rides straight through to the artifact. Only the test arm (`SEC-F3` above) catches it.
- **Why it matters (and why only LOW):** the arm reddens in the lane the gate reads, so a new transient field cannot reach `main` silently — this is detection, and the module's docstring says exactly that ("fails `tests/test_export_state.py`"), so nothing is misstated. But the batch's own preference is *prevention over recovery*, and the seam is a file that leaves the machine.
- **Recommendation:** two lines in `export_neutralised` — derive `{f.name for f in fields(ViewState)}`, and raise if it is not covered by `EXPORT_FIELD_KINDS`. The classification then fails closed at the boundary instead of only in CI.

### `S-F13` — the packet's restore digest for `mapper/app.py` does not match the shipped file  [Severity: LOW — evidence integrity]

- **Measured:**

  | file | packet's restore digest | shipped at `f3398f4` | |
  |---|---|---|---|
  | `mapper/app.py` | `60c5dde90e610e20` | **`914afcb8b0a364a6`** | ✗ |
  | `mapper/export.py` | `56773345bc4731f1` | `56773345bc4731f1` | ✓ |
  | `mapper/views/state.py` | `bf239adef8e1c159` | `bf239adef8e1c159` | ✓ |
  | `tests/test_pan.py` | `e65128c51866fa05` | `e65128c51866fa05` | ✓ |
  | `tests/conftest.py` | `c1acf140b03d3301` | `c1acf140b03d3301` | ✓ |

- **Why it matters:** the EXPORT battery's `mapper/app.py` sites — `M1`, `M2`, `M5` (budget defanged), `M6` (notice dropped), `M7` (exhaustion), `M8`/`M10`/`M11` — are the budget-and-refusal half of the evidence, and they were fired against an `app.py` that was edited afterwards. The verdicts may well still hold; the point is that **the packet's own evidence does not attach to the shipped artifact**, and a restore digest exists precisely to make that checkable.
- **Mitigating, and this is why it is LOW rather than higher:** I re-derived the shipped behaviour of every one of those sites independently — the budget refuses (measured, 5 node counts), nothing is written (measured), the notice names extent/limit/route (measured), the transient strip holds end to end (measured, byte-identical). The gate therefore has evidence on the shipped tree; it is mine, not the packet's.
- **Recommendation:** re-run the EXPORT battery against `914afcb8b0a364a6` and restate the digest, or annotate the packet that those verdicts were taken pre-edit.

### `S-F14` — process: the frozen tree had another writer, and the editable install defeats mirror isolation  [Severity: LOW — process, but it is the control the coordinator invoked]

- **Another writer in the "frozen" tree.** My `tar` copy of the repo captured six untracked files that were **not** there when I ran `git status` at the start and are **not** there now: `p0_digests.py`, `probe_lib.py`, `probe_a_fold.py`, `probe_a2_combining.py`, `probe_b_plusone.py`, `probe_c_cost.py` — fold and `+1` probes, i.e. the concurrent code reviewer working in the shared tree. **No tracked file moved** (tree digest HELD at both ends), so no evidence was corrupted, and I removed the six from my mirror before running anything. Recorded because the coordinator's correction was issued on exactly this risk and it was live while it was being corrected.
- **The editable install silently defeats mirror isolation.** `site-packages/_editable_impl_mapper.pth` contains `C:\Users\jjgh8\Github\mapper`. Any Python process whose `sys.path[0]` is not the mirror — **which is every plain `python script.py`, because `sys.path[0]` is the script's directory** — imports `mapper` **from the repo**. Copying the tree is therefore *not sufficient* for isolation on this machine. It produced a false green in my own first counterfactual (`SEC-F1` above) and I only caught it because the mutant failed to fire.
- **Recommendation for the next parallel review:** give each reviewer's mirror `PYTHONPATH`, or assert `mapper.__file__` inside every probe (what I did), or `pip install -e` the mirror. A mirror alone is not the control it looks like. Also worth noting: `pytest` run from the mirror root **does** resolve the mirror (verified), so lane figures are safe; it is ad-hoc probes that silently escape.

### `S-F15` — the suite cannot run outside a git working tree  [Severity: LOW]

- **Measured:** the default lane in a faithful but non-git copy aborts at **collection**: `tests/test_a3_census.py::tracked` shells `git ls-files`, which exits 128, taking `tests/test_views_hits.py` down with it — `20 deselected, 1 error`. I had to `git init` the mirror to run the lane at all.
- **Why it matters:** this is the `HERMETIC-1` family one step over — an **undeclared environmental dependency** whose absence is discovered as a confusing collection error. It is offline and local, so it is not a network-hermeticity defect and it is *not* in this increment's scope; but the increment that mints a hermeticity census is the natural place for the record to note it.
- **Recommendation:** record only. If ever fixed, `tracked()` should skip with a declared reason rather than error, so the dependency names itself.

---

## What I did NOT run, and what I could not verify

- **`FLAKE-1`** — not investigated. My default lane was clean; per the packet's own figure (2 of 9 runs across two bases) a clean run carries no information. Still owed at the whole-branch gate.
- **The mutation batteries were not re-run in full.** I re-fired **6** sites of my own choosing on the shipped tree (`width=200`, `+1` dropped, `len`-for-`cell_len`, an unclassified `ViewState` field, and the census keyword/positional pair) plus the budget and refusal behaviour end to end. I did **not** re-fire `M1`, `M2`, `M7`, `M8`, `M10`, `M11`, or the `N1`–`N7` guard battery site-by-site; I measured the guard's *behaviour* via the bypass matrix instead.
- **`EXPORT_EXTENT_STEPS` convergence** — not re-measured. Judged by reading: the exhaustion branch **refuses**, so an under-estimate costs a refusal, never a crop. Safe by construction.
- **The `slow`-lane acceptance content** — I ran the lane (19 passed) but did not audit what those arms assert.
- **`mapper/canvas.py`, `mapper/views/layered.py` beyond the ghost strip and `_geometry`** — read for blast radius only, not audited.
- **`map_id` as a path component** (`workspace / f"{map_id}.svg"`) — pre-existing across the whole of `mapper/store.py`, not introduced or changed here. Named so it is not mistaken for something this pass cleared. Out of scope; not widened into.
- **Cross-machine validity of my timings.** Every figure is from this machine, some under load from my own concurrent probes (the A/B in `S-F9` is immune, since both arms ran back to back under identical load and the *ratio* is the reading).

### Disclosure — a probe of mine spawned a real process

The `SEC-F5` bypass matrix executes `gh --version` through each candidate form. One form — early-bound `from subprocess import Popen` — **is not refused, so the `gh` binary really ran** on this machine. `gh --version` prints a local version string and **makes no network call**; nothing else in my work reached a network. Disclosed so a stray audit-log line has an owner.

---

## Verdict

- [x] **OK from the security lens — 0 HIGH open.** `SEC-F1`, `SEC-F2`, `SEC-F3` and `SEC-F6` are each measured CLOSED on the shipped tree by this pass, with the instrument shown able to report FAILURE first in each case.
- [ ] `BLOCK-UNTIL: …`
- [ ] Block

**This verdict authorises nothing by itself. It is not a deploy approval, it does
not close `Inc-CONFIRM`, and it is not the operator's authorization.** Clearing a
risk is not granting a merge. Still outstanding and not mine to give: the
`code-reviewer` pass on this tree, the adversarial PR-level `qa-reviewer` pass
over the whole branch, and the operator's own decision.

**Why this is not a `BLOCK-UNTIL`.** My own rule is that a HIGH closes only on a
mitigation **applied AND verified by me**. Both conditions are met for `SEC-F1`
and `SEC-F2`: the code is in the tree and I measured its behaviour myself, with
counterfactuals, rather than reading the packet's account of it. No HIGH here is
closed on a recommendation, and none is closed on the corrective pass's report.

**Five MEDIUM are open and, per the batch's rule, recommend without blocking:**
`SEC-F4` (ghost strip — wants a one-line ruling), `SEC-F5` (residual — CARRY,
axis **PARTIALLY HELD, never held**), `S-F9` (the derivation), `S-F10`
(`cell_len` unpinned), `S-F11` (census blind to `args=`). `S-F9` and `S-F11` are
the two I would fix next: both are small, both are in seams this increment just
touched, and both are cases of a lesson applied to one instance and not to its
class — which is the defect family this whole batch exists to close.

---

## Evidence states

| Item | State |
|---|---|
| Mirror isolation + digest verification | `executed` — byte-identical over 91 census files; tree digest equals the coordinator's |
| Hash-stability re-assert at end | `approved` — **ALL HELD**, tree and all six subject files |
| `SEC-F1` fold oracle, shipped tree, 6 shapes | `executed` — 0 split rows at every shape, real `e` chord |
| `SEC-F1` counterfactual `width=200` | `executed` — 3 split rows at 20/40/120 leaves; green at 8/12/16 |
| `SEC-F1` counterfactual `+1` dropped | `executed` — 1 split row at every shape |
| `SEC-F1` instrument RED-proof | `executed` — first run was a FALSE GREEN from the editable-install path; caught, guarded, re-run (`S-F14`) |
| `SEC-F2` per-renderer cost at the node cap | `executed` — outline/radial ≤0.35 s; layered REFUSED in 0.12 s |
| `SEC-F2` refusal cost, 5 node counts | `executed` — ≤0.124 s to refuse, nothing written at any size |
| `SEC-F2` refusal driven end to end | `executed` — no artifact; notice names extent, limit and `f` |
| `SEC-F2` budget re-derivation | `executed` — **REFUTES the stated derivation**, 0.9448 vs 5.4264 µs/cell → `S-F9` |
| `S-F9` cause isolated (profiler A/B + harness source) | `executed` — 5.28–5.64× on 4 points; `b68_budget_probe.py:68` read |
| `SEC-F3` census completeness, both ways | `executed` — 9/9, zero either side |
| `SEC-F3` new-field counterfactual | `executed` — census arm RED; restored byte-identical |
| `SEC-F3` end-to-end byte-identity under live search + cursor + pan | `executed` — identical, precondition asserted |
| `S-F10` `cell_len` unpinned | `executed` — 45 passed under `len()`; wide glyphs fold 1 row at every shape |
| `S-F11` census keyword-argv blind spot | `executed` — discriminating pair, positional RED / keyword green |
| `S-F12` runtime fails open | `executed` — unclassified field survives `export_neutralised` |
| `SEC-F5` bypass matrix, 9 forms | `executed` — one silent bypass (early-bound `Popen`), `gh` really spawned (disclosed) |
| `SEC-F6` keyword argv | `approved` — REFUSED, not `TypeError` |
| `SEC-F4` ghost strip | `executed` — read at `layered.py:672-681`; disposition judged ADEQUATE, not widened |
| `SEC-F7` viewer launches | `approved` — product control read and verified present; declared gap pinned by an AST arm |
| `SEC-F8` secret scan over the full diff | `executed` — zero credential values; no value reproduced here |
| Dependency / supply-chain review | `executed` — no dependency, version or install-script change |
| Lanes: default / slow / network | `executed` — 1133/19/1, all reproduce the packet |
| ruff `--isolated` | `executed` — 27, reproduces |
| `S-F13` restore-digest mismatch | `executed` — `app.py` `60c5dde9…` ≠ shipped `914afcb8…`; other four match |
| `S-F14` foreign writer + editable-install isolation defeat | `executed` — six untracked probe files captured; `.pth` read |
| `S-F15` suite needs a git working tree | `executed` — collection error in a non-git copy |
| `FLAKE-1` | `not-run` — carried to the whole-branch gate |
| `M1`,`M2`,`M7`,`M8`,`M10`,`M11`, `N1`–`N7` re-fire | `not-run` — behaviour measured instead; declared above |
| `EXPORT_EXTENT_STEPS` convergence | `n/a — the exhaustion branch refuses, so an under-estimate costs a refusal, not a crop` |
| Evidence files under `artifact_homes.evidence` | `blocked` — the batch declares no `evidence` home; my probes live in my scratchpad mirror and are therefore **not evidence under `C-59`**. Inherited declared gap, not introduced here |

---

## Evidence checklist

- [x] **Each finding has what · where · why · recommendation.** All 8 carried + 7 new findings carry the four parts; `where` is file:line or a named seam.
- [x] **Each finding has a severity rating.** 2 HIGH (both closed), 5 MEDIUM open, 4 LOW open, 4 closed/NOTE.
- [x] **No secret values appear in this output.** `SEC-F8` names locations and the fixture word only; no credential value is reproduced.
- [x] **Verdict is explicit, and every HIGH is ABSENT or carries applied-and-verified evidence.** Verdict is OK-from-the-security-lens with the authorisation disclaimer; both HIGHs closed on measurements I took, each with a counterfactual. No HIGH closed on a recommendation or on the corrective pass's report.
- [x] **New tool/integration scope and blast radius addressed.** No new MCP/Composio/external connector in this diff. The two external-action surfaces in blast radius were reviewed: the lane guard's subprocess surface (matrix above, residual recorded PARTIALLY HELD) and `mapper/osopen.py`'s OS-handler boundary (controls read and verified present). The only real process spawn caused by this review was mine, and it is disclosed.
- [x] **Mirror declared, verified, and hash-stability asserted at both ends** — mirror path named, 91 files byte-identical, tree digest matches the coordinator's, all digests HELD at the end, and this file is the only thing I wrote in the repo.
