# Increment 001 — HLR-R01 · `Cycle refusal`

| Field | Value |
|---|---|
| Batch | `2026-08-26-repair-batch` |
| Increment | `001` |
| Lane (if the batch forked) | not forked — serial batch, `0 of 6 pairs parallelisable` |
| Requirement(s) | `HLR-R01` / `LLR-R01.1`, `LLR-R01.2`, `LLR-R01.3`, `LLR-R01.4` |
| Acceptance | `AT-R01`, `AT-R02`, `AT-R03` · white-box `TC-R01` through `TC-R09` · unit `Graph.find_cycle` |
| Agent | `software-dev` (supervised-incremental-development) |
| Date | 2026-08-26 |

---

## 1 · What changed

**A map whose edge set contains a directed cycle is now refused at load with a Spanish message naming
the cycle path, and no renderer failure can reach the operator as a dead application.** S-01a is closed
at three planes: the detector (`Graph.find_cycle`), the refusal (`mermaid.parse` → `MapStore.load`), and
the sink (the screens that call a renderer from inside the Textual message pump).

The mechanism. `Graph.find_cycle()` is an iterative depth-first walk carrying an explicit path stack; it
returns one cycle's node ids with the entry node repeated last, or `None`. It distinguishes a *back edge*
(an edge into the currently active path — a cycle) from a *re-visit* (a node reached again down a
different branch — a diamond, which is legitimate). `mermaid.parse` consults it after building the edge
set and raises `MermaidError`, which carries the cycle list itself; `MapStore.load` restates it as
`MapStoreError("el mapa tiene un ciclo: <path>")`, the path joined by U+2192.

**Reached through the shipped surface**, the operator now sees: opening a cyclic `.mmd` on `MapScreen`
produces the Spanish notice `error cargando mapa: el mapa tiene un ciclo: a→b→c→a` and the screen stays
alive and answers keys; the sala (`HomeScreen`) names each map it could not load instead of dropping it
silently; and any renderer that throws paints `no se pudo dibujar el mapa` in the canvas rather than
killing the app.

### The sibling the reverse census found — declared, because it changes the file count

LLR-R01.4 is scoped to the **sink class**, not to the two symbols it names. Probing `refresh_canvas`
across `app.py` (§4, probe A3) resolved **two** definitions, not one:

| line | owner | guarded before this increment |
|---|---|---|
| `mapper/app.py:721` | `_ImportPreviewScreen.refresh_canvas` | **no** |
| `mapper/app.py:1307` | `MapScreen.refresh_canvas` | no |

`_ImportPreviewScreen` renders from inside its own `on_mount`, and its graph comes from
`import_csv.preview_csv` — which **never passes through `mermaid.parse`**, so the parser refusal built in
this increment cannot protect it. Reproduced, not predicted:

```
$ PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -c "..."   # 3-row CSV, circular `parent` column
preview_csv built edges: [('c', 'a'), ('a', 'b'), ('b', 'c')]
find_cycle -> ['a', 'b', 'c', 'a']
render -> RecursionError: maximum recursion depth exceeded
```

That is S-01a's crash reached through a second door. Guarding only the two named symbols would have
reproduced batch 1 §2.1b exactly — the requirement satisfied at its named cases' boundary while a sibling
keeps the defect — which is the failure LLR-R01.4's own rationale cites. The guard was added and is
certified by `TC-R08b`, whose non-vacuity is proven by its own mutation arm (§4).

---

## 2 · Files modified

**The budget counts SOURCE files only. Tests are not capped. Product docs and `.dev-flow/**` are outside the count.**

| File | Kind | Change |
|---|---|---|
| `mapper/model.py` | source | `+ Graph.find_cycle()` — iterative DFS, back-edge vs. re-visit |
| `mapper/mermaid.py` | source | `+ CYCLE_ARROW`, `+ MermaidError(ParseError)` carrying the cycle; `parse` consults `find_cycle` before picking a root; the now-dead "cycle or single self-edge" root fallback removed |
| `mapper/store.py` | source | `MapStore.load` translates `MermaidError` into `MapStoreError("el mapa tiene un ciclo: …")` |
| `mapper/app.py` | source | `MapScreen.refresh_canvas` + `_ImportPreviewScreen.refresh_canvas` guard the renderer call; `HomeScreen.on_mount`'s four silent `except Exception: pass` sites become one `load_or_notice` helper that names the map |
| `tests/test_repair_cycles.py` | test | new file, 20 collected nodes |

| Count | Value |
|---|---|
| **SOURCE files** | **`4` / 4** |
| Test files | `1` (uncapped) |
| Doc files | `0` (outside the count) |

- ⚠ **At exactly 4 source files.** The increment plan (§5 of `01-requirements.md`) budgets 3 —
  `model.py`, `mermaid.py`, `store.py`. The fourth, `app.py`, is **required by LLR-R01.4**, which names
  `MapScreen.refresh_canvas` and `HomeScreen.on_mount`; both live in `app.py` and there is no way to
  satisfy that LLR without it. The task brief anticipated this and declared 4 within budget. It cannot be
  cut smaller: dropping `app.py` leaves the original defect — the `RecursionError` escaping the message
  pump — entirely unrepaired, since refusing the cycle at parse time does not help any *other* renderer
  failure, nor the CSV door found in §1.
- ✗ Lane sharing: not applicable, the batch did not fork. **Serial conflict noted:** Inc-3 also owns
  `store.py`, `model.py` and `app.py`, and Inc-4 also owns `app.py`. Those increments must rebase on this
  one, per §5's "0 of 6 pairs parallelisable".

---

## 3 · How to test

```bash
cd C:\Users\jjgh8\Github\mapper

# Gate run — the summary is read from the file, because Textual's teardown
# noise ("Task was destroyed but it is pending!") buries it on the terminal.
PYTHONUTF8=1 python -m pytest -q -p no:randomly > out.txt 2>&1 ; echo "exit=$?"
grep -E "passed|failed|error" out.txt | tail -3

# Collected count for the ledger
PYTHONUTF8=1 python -m pytest -q -p no:randomly --collect-only 2>&1 | tail -1

# This increment alone
PYTHONUTF8=1 python -m pytest tests/test_repair_cycles.py -q -p no:randomly

# Lint
python -m ruff check mapper tests
```

---

## 4 · Test results

**One complete run.** Exit code and tail read from that run's own `out.txt`.

```
exit=0
265 passed in 36.42s
265 tests collected in 0.13s
```

`ruff`: **29 findings before and after** — verified by stashing the increment
(`git stash push --include-untracked -- mapper tests` → 29 → `git stash pop` → 29). This increment adds
**zero** new lint findings. The 29 are pre-existing (`F401`/`F841` across 20 files) and are not this
increment's to clean under the surgical-changes rule.

| Layer | Nodes | Result |
|---|---|---|
| **0 · unit** — `Graph.find_cycle`, cyclomatic ≥3, transforms data at a declared module boundary | `test_tc_r01_…`, `test_tc_r02_…`, `test_tc_r03_…`, `test_tc_r03b_…`, `test_tc_r04_…`, `test_tc_r04b_…`, `test_find_cycle_returns_none_for_an_empty_graph` | 7 passed |
| **A · white-box** `TC-R05` … `TC-R09` ↔ LLR-R01.2/.3/.4 | `test_tc_r05_…`, `test_tc_r05b_…`, `test_tc_r06_…`, `test_tc_r06b_…`, `test_tc_r07_…`, `test_tc_r08_…[recursion-error]`, `test_tc_r08_…[unanticipated-error]`, `test_tc_r08b_…`, `test_tc_r09_…` | 9 passed |
| **B · black-box** `AT-R01`, `AT-R02`, `AT-R03` ↔ US-R01, through the shipped surface | `test_at_r01_opening_a_cyclic_map_refuses_it_without_killing_the_app`, `test_at_r02_the_message_names_the_actual_cycle_not_a_fixed_string`, `test_at_r03_an_acyclic_map_still_loads`, `test_at_r03b_a_diamond_is_not_called_a_cycle` | 4 passed |

### RED — the shipped defect, reproduced before any code was written

```
$ PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -c "..."
parse ACCEPTED the cycle:
  nodes = ['a', 'b', 'c']
  edges = [('a', 'b'), ('b', 'c'), ('c', 'a')]
  root_id = a
RadialRenderer -> RecursionError: maximum recursion depth exceeded
   deepest frame: \views\radial.py line 24 | _leaves
LayeredRenderer -> RecursionError: maximum recursion depth exceeded
   deepest frame: \views\layered.py line 47 | walk
```

Both renderers, not one — and `MapScreen.refresh_canvas` had no guard, so this escaped the message pump.

### RED counterfactual — executed, not predicted

| Field | Value |
|---|---|
| Where it ran | **my own tree** — no worktree, no other session reading it |
| Bytecode cache | every arm run under `PYTHONDONTWRITEBYTECODE=1`; `__pycache__` cleared before the post-battery gate run |
| Restore proven by | **sha256 returned to its pre-mutation value on every arm** — `git status` alone would be vacuous for the untracked test file |
| Arms resolved at baseline | asserted per arm against a pre-mutation baseline run: 4 / 2 / 4 / **4 from 3 selectors** — the sink set resolves 4 because `TC-R08` is parametrized ×2. See the note below |
| Verdict granularity | **per resolved node id**, never the process exit code |

**Parametrized-arm resolution.** The runner's node regex keeps the `[...]` suffix. Collapsing
`test_tc_r08_…[recursion-error]` and `…[unanticipated-error]` onto one key would have made the
narrowed-guard arm below *look* reddened while its first parameter was silently inert — the exact hazard
the template names. The baseline line `3 selectors -> 4 resolved arms` is the assertion that it did not
happen.

**Mutations are described by position and operation. No corrupted token is spelled here.**

| # | Arm | File · position | Operation | Verdict per resolved node |
|---|---|---|---|---|
| 1 | `AT-R01` **deletion** | `mermaid.py`, in `parse`, the cycle-assignment statement | call expression on the right-hand side replaced by the `None` literal, so the detector is never consulted | `test_at_r01_…` **FAILED** · `test_tc_r05_…` **FAILED** · `test_tc_r07_…` **FAILED** · `test_tc_r01_…` PASSED |
| 2 | `AT-R01` **weaker: self-loops only** | `model.py`, head of `Graph.find_cycle`'s body | an early scan comparing each edge's two endpoints, returning before the traversal runs | all 4 **FAILED** |
| 3 | `AT-R02` **deletion: fixed string** | `store.py`, the `MapStoreError` argument in `load` | f-string interpolation replaced by a constant path **equal to the first fixture's own cycle** (the strongest fixed-string mutant) | `test_at_r02_…` **FAILED** · `test_tc_r07_…` PASSED |
| 4 | `AT-R02` **weaker: first node only** | `store.py`, same argument | a one-element slice applied to the cycle list before joining | both **FAILED** |
| 5 | `AT-R03` **blanket refusal** | `model.py`, head of `Graph.find_cycle`'s body | an unconditional refusal returned whenever the edge list is non-empty | all 4 **FAILED** |
| 6 | `AT-R03` **weaker: any re-visited node** *(the false-refusal arm)* | `model.py`, the finished-node branch inside `find_cycle`'s inner loop | the branch's loop-continuation statement replaced by a refusal return, so a node re-reached down a second branch is reported as a cycle | `test_at_r03_…` **FAILED** · `test_at_r03b_…` **FAILED** · `test_tc_r03_…` **FAILED** · `test_tc_r06_…` PASSED |
| 7 | `LLR-R01.4` **deletion: MapScreen guard** | `app.py`, `MapScreen.refresh_canvas` | the guarding construct around the renderer call neutralised so the exception propagates | `test_tc_r08_…[recursion-error]` **FAILED** · `test_tc_r08_…[unanticipated-error]` **FAILED** · others PASSED |
| 8 | `LLR-R01.4` **weaker: guard narrowed to the known type** | `app.py`, `MapScreen.refresh_canvas`, the handler's exception class | widened base class replaced by the single concrete type this batch happens to produce | `test_tc_r08_…[unanticipated-error]` **FAILED** · `test_tc_r08_…[recursion-error]` **PASSED** · others PASSED |
| 9 | `LLR-R01.4` **sibling: `_ImportPreviewScreen` guard** | `app.py`, `_ImportPreviewScreen.refresh_canvas` | the guarding construct around the renderer call neutralised | `test_tc_r08b_…` **FAILED** · others PASSED |

sha256 restore, every arm: `mermaid.py` `6e67526db66a5364` · `model.py` `7c5df0c999966f08` ·
`store.py` `4ddff8de7be10dd7` · `app.py` `1edcfae6f1bd8f1b` — before == after on all nine.
Post-battery, `__pycache__` was deleted and the full suite re-run green (265 passed, exit 0), so no
mutant bytecode survived a same-size same-second restore.

**Arm 8 is the one that matters.** It is batch 1 §2.1b in miniature: narrowing the sink guard to the
exception type this batch knows about leaves `[recursion-error]` green and only `[unanticipated-error]`
red. A test suite written to the two types named in the defect would have certified the narrowed guard.

### Arms that stayed GREEN — named, with the reason each is sound

| Arm | Node that stayed green | Why it is not inert |
|---|---|---|
| 1 | `test_tc_r01_…` | The mutation is in `mermaid.parse`; TC-R01 exercises `Graph.find_cycle` **directly** as a Layer-0 unit. The unit is untouched, so it must stay green — wrong plane, not a hole. Arm 2 mutates the unit and TC-R01 reddens. |
| 3 | `test_tc_r07_…` | **Deliberate, and the reason `AT-R02` exists.** The mutant constant was chosen to equal TC-R07's own expected message. A single-fixture exactness test is satisfiable by a constant; `AT-R02` drives *two* cycles and reddens. This is the division of labour LLR-R01.3 and AT-R02 were written with — reported, not papered over. |
| 6 | `test_tc_r06_…` | TC-R06's acyclic fixture is a **tree**, and a tree re-visits nothing, so the widened rule never fires on it. Measured: this is exactly why a diamond fixture is mandatory. `test_at_r03_…` was **strengthened mid-increment** to carry the diamond on the AT node itself after a first battery run showed it green here. |
| 7, 9 | the other sink's nodes | `MapScreen` and `_ImportPreviewScreen` are two distinct sinks; each arm reddens its own and must leave the other alone. Each sink has its own reddening arm, so neither is uncertified. |
| 7, 8, 9 | `test_at_r01_…` | **Honest finding, reported.** `AT-R01` is carried by the parse/store refusal plus the **pre-existing** `MapScreen.on_mount` guard — the load fails before a renderer ever sees the cyclic graph, so `refresh_canvas` gets the error placeholder. The *new* renderer guards are certified by `TC-R08` and `TC-R08b`, not by `AT-R01`. Arm 1 confirms `AT-R01` does redden when its own predicate is removed. |

- ✗ No predicate stayed green under the mutation of what **it** claims to certify.

### Load-bearing emptiness — what is this resting on that is only true today? (C-55)

| Field | Value |
|---|---|
| Does any claim here rest on the tree holding NO instance of some case? | **Yes** — `mermaid.parse`'s root pick now assumes at least one parentless node exists |
| The reasoning | Acyclicity is established one statement earlier. In a finite non-empty acyclic digraph, following parent links from any node must terminate at a parentless node, so the candidate list cannot be empty. The shipped `else: root_id = next(iter(nodes))` fallback, commented "Cycle or single self-edge", became **dead** the moment the cycle raised — it was removed rather than left as a misleading branch a reader would later "fix". |
| Guard labelled as protecting a CONCLUSION | `test_tc_r06_parse_still_accepts_an_acyclic_map` (root is `root`) and `test_at_r03_an_acyclic_map_still_loads` (`graph.root_id == "root"`). Arm 5 (blanket refusal) reddens both, so the removal is not silently load-bearing. |
| Conjunctive criteria: one mutation per conjunct | `AT-R03` is conjunctive — "an acyclic map loads" **and** "a diamond is not refused". Arm 5 reddens the first conjunct; arm 6 reddens the second (and, before the mid-increment strengthening, reddened *only* the diamond sibling — which is how the weak conjunct was found). |
| Synthetic instance of the absent case | The tree contains **no** map with two parents, because `mermaid.parse` has refused that as out of MVP scope since long before this batch. `_diamond()` in `tests/test_repair_cycles.py` constructs one in memory as a `Graph`. |
| **Positive control for every probe that returned an ABSENCE** | `find_cycle()` returning `None` on the diamond is an absence. The **same unmodified** function returns a non-absent `['a','b','c','a']` on the cyclic fixture (`test_tc_r01_…`), `['a','a']` on a self-loop (`test_tc_r02_…`), and a 5002-element path on a deep chain (`test_tc_r04b_…`) — three heterogeneous non-absent outputs, so `None` on the diamond is a measurement, not a probe that never fires. |

⚠ **`test_at_r03b_a_diamond_is_not_called_a_cycle` cannot drive the store.** A diamond cannot round-trip:
`mermaid.dump` emits it faithfully, and `parse` then refuses it with the pre-existing multiple-parents
`ParseError`. The node therefore asserts the strongest available statement — `find_cycle` returns `None`,
**and** the parser's refusal is still `ParseError` and specifically **not** `MermaidError`, so this
increment's cycle rule has not widened into a false cycle claim. Declared here because the requirement's
§4 text ("confirm it still loads") is not literally satisfiable against today's parser.

### Reverse census — trigger family B

| Probe | Command | Result |
|---|---|---|
| B1 symbols asserted by **other** tests | `grep -rl "find_cycle" tests/ mapper/` | Only `tests/test_repair_cycles.py` (this increment's own) plus the two sources that define/use it. **Did not fire:** no pre-existing test asserts on `find_cycle` — it is new. |
| B1 | `grep -rn "MermaidError\|CYCLE_ARROW" mapper/ tests/` | `mermaid.py` (definition), `store.py` (consumer), `test_repair_cycles.py`. No other reader. **New symbols, no incumbents.** |
| B2 file moved on disk | `ls mapper/model.py mapper/mermaid.py mapper/store.py mapper/app.py` | All four still at their original paths — nothing moved, nothing renamed. **Did not fire.** |
| B3 byte-identical golden captures this source | `ls tests/goldens` | **No `tests/goldens` directory exists.** Probe ran and found nothing to break. |
| B4 artifact produced here is consumed elsewhere | who reads `MapStoreError` text / the `.mmd` format | `MapStoreError` message text is consumed only by `app.py`'s notice sinks (`f"error cargando mapa: …"`). `.mmd` on-disk format **unchanged** — this increment only refuses a subset that previously crashed. |
| **A3** interface consumed by another module changed | `grep -rn "from .mermaid import\|mermaid.parse" mapper/ tests/` | **FIRED.** `mermaid.parse` now raises where it previously returned. Callers: `store.py:155` (`_graph_from_sidecar`, handled at `store.py:207`); `tests/test_mermaid.py` (green — no fixture there is cyclic). `app.py:35` and `import_csv.py:7` import only `dump`/`slugify`, **not** `parse` — unaffected. |
| **A3** | `grep -rn "refresh_canvas" mapper/ tests/` | **FIRED, and this is §1's finding.** Two definitions, not one: `app.py:721` (`_ImportPreviewScreen`) and `app.py:1307` (`MapScreen`). The requirement names only the second. |
| **A3** | `grep -rn "ParseError" mapper/ tests/` | Defined and raised only inside `mermaid.py`. `MermaidError` **subclasses** it, so every existing `except ParseError` still catches the new refusal — no caller is bypassed. |

- ✗ **Frozen interfaces:** `IRenderer.render` and `Canvas` are **untouched** — confirmed, `git status`
  lists neither `mapper/canvas.py` nor any file under `mapper/views/`. The scope fence in
  `01-requirements.md` §0 holds.

### Byte-scan — every file touched

```
mapper/model.py             sha256=7c5df0c999966f08 utf8=OK NUL=0 BS=0 ESC=0 DEL=0 stray-control=none U+2192-literal=0
mapper/mermaid.py           sha256=6e67526db66a5364 utf8=OK NUL=0 BS=0 ESC=0 DEL=0 stray-control=none U+2192-literal=0
mapper/store.py             sha256=4ddff8de7be10dd7 utf8=OK NUL=0 BS=0 ESC=0 DEL=0 stray-control=none U+2192-literal=0
mapper/app.py               sha256=1edcfae6f1bd8f1b utf8=OK NUL=0 BS=0 ESC=0 DEL=0 stray-control=none U+2192-literal=0
tests/test_repair_cycles.py sha256=8ba50c624e7d5e2c utf8=OK NUL=0 BS=0 ESC=0 DEL=0 stray-control=none U+2192-literal=0
```

`stray-control` scans every codepoint below `0x20` other than CR/LF/TAB **and** the `0x7F`–`0x9F` range —
none present in any file. `U+2192-literal=0` on all five: the arrow is **never spelled into source**. It
exists once, as `CYCLE_ARROW = chr(0x2192)` in `mermaid.py`, and the test pins it by codepoint
(`ord(CYCLE_ARROW) == 0x2192`) so a look-alike separator cannot pass. `model.py` and `mermaid.py` are
pure ASCII; the non-ASCII in `store.py` (2 chars) and `app.py` is pre-existing Spanish and box-drawing
glyphs. All files are CRLF, matching the repo's existing convention.

### Signed-balance test ledger

`post = base − deleted + added` → **`265 = 245 − 0 + 20`**  ✓ reconciles

On **collected** counts (`pytest --collect-only`): base 245, post 265. `D = 0` as §5 expected — this
increment adds behaviour and removes none, and no pre-existing node was deleted or renamed. `A = 20` is
`tests/test_repair_cycles.py`: 19 test functions, one of which (`TC-R08`) is parametrized ×2.

---

## 5 · Risks

1. **A previously-loadable map now refuses to load.** Any workspace `.mmd` containing a cycle loaded
   before this change — it just crashed a renderer afterwards. It now raises at `MapStore.load`. That is
   the intended repair, but it is a **behaviour change on existing data**, and an operator with such a
   file will see a refusal where they previously saw a crash. `HomeScreen` degrades gracefully (the map
   is listed with `0` nodes and a notice); `MapScreen` shows the error placeholder.
2. **`_leaves` and `walk` are still recursive.** This increment removes the *cycle* route to
   `RecursionError`. **S-01b — a depth-500 acyclic chain — is untouched and still crashes**, by design:
   it is Inc-2's (`HLR-R02`). Until Inc-2 lands, the new sink guards are what stand between that crash
   and a dead app; they convert it to a Spanish notice rather than preventing it.
3. **`MermaidError`'s constructor takes a cycle, not a message.** If a future refusal in `parse` is not a
   cycle, it needs its own type or a widened constructor. Deliberate — no speculative generality — but a
   reader may assume `MermaidError` is the general mermaid error. The docstring says otherwise.
4. **Serial dependency.** Inc-3 (`store.py`, `model.py`, `app.py`) and Inc-4 (`app.py`) overlap this
   increment's file set. They must rebase, not merge in parallel.
5. **`HomeScreen`'s notice can be noisy.** A workspace with many broken maps emits one notification per
   distinct map (deduplicated by name). Bounded by the map count; not bounded to a small number.

---

## 6 · Pending items / spec deviations

| # | Item |
|---|---|
| D-1 | **Source-file count is 4, not the 3 planned in §5.** Declared in §2 with the reason: LLR-R01.4's two named symbols both live in `app.py`. |
| D-2 | **`AT-R03`'s diamond cannot "still load"** through the store — `mermaid.parse` refuses two parents (pre-existing MVP tree constraint, `mermaid.py:84`). The AT was realised as the strongest available statement; see §4. If the batch wants the literal wording, the MVP tree constraint has to be lifted first, which is not this batch's scope. |
| D-3 | **A fifth sink guard was added beyond the requirement's letter** (`_ImportPreviewScreen.refresh_canvas`), justified by LLR-R01.4's sink-class scoping and a reproduced crash. **This should be written back into `01-requirements.md` LLR-R01.4** so the next reader does not see an unexplained guard. |
| D-4 | **A cyclic CSV import is still *accepted*, only no longer fatal.** `import_csv.preview_csv` has no cycle check; the guard catches the render failure but the operator gets a notice instead of a preview. Refusing at import time — symmetric with `mermaid.parse` — is a candidate backlog item, out of scope here. |
| D-5 | 29 pre-existing `ruff` findings (`F401`/`F841`) across 20 files, unchanged by this increment and not cleaned under the surgical-changes rule. |
| D-6 | `TC-R07` alone is satisfiable by a hard-coded constant (arm 3). Sound as split — `AT-R02` covers it — but noted so no future refactor removes `AT-R02` believing `TC-R07` is sufficient. |

---

## 7 · Suggested next task

**Increment 2 — `HLR-R02` depth safety (`AT-R04`, `AT-R05`).** It is the natural successor: risk 2 above
says the recursive `_leaves` / `walk` are still live, and the RED transcript in §4 names both frames
(`views/radial.py:24 _leaves`, `views/layered.py:47 walk`) — the same two functions LLR-R02.1 and
LLR-R02.2 target. Its file set (`views/radial.py`, `views/outline.py`, `views/layered.py`) is **disjoint**
from this increment's, so it needs no rebase, unlike Inc-3 and Inc-4.

Note for Inc-2: `LLR-R02.1` requires the traversal set be derived by an **AST walk** over `mapper/views/`,
not hand-listed. `mapper/views/lane.py` is in that package and was not named in `HLR-R02`'s touched
symbols — the AST walk will decide whether it belongs.

---

## Increment gate checklist

| # | Item | ✓/⚠/✗ | Evidence (node id · command output · file:line) |
|---|---|---|---|
| 1 | ≤4 source files, or reason declared | ⚠ | Exactly 4. Reason declared in §2: LLR-R01.4 names two symbols that both live in `mapper/app.py`. Plan budgeted 3; task brief pre-authorised 4. |
| 2 | Tests written in this same increment | ✓ | `tests/test_repair_cycles.py`, new file, 20 collected nodes, `265 − 245 = 20` |
| 3 | Layer 0 written where the criterion applies | ✓ | `Graph.find_cycle` (`mapper/model.py:140`) unit-tested directly by 7 nodes, `test_tc_r01_…` through `test_find_cycle_returns_none_for_an_empty_graph` |
| 4 | RED counterfactual captured **and restored by hash** | ✓ | §4: shipped-defect RED transcript + 9 arms; sha256 before == after on all four sources; post-battery suite green after `__pycache__` deletion |
| 5 | Reverse census run on every touched symbol | ✓ | §4 census table — A3 fired **twice** (`mermaid.parse` raises where it returned; two `refresh_canvas` definitions). B2/B3 recorded as did-not-fire **with their probes**. |
| 6 | `code-reviewer` passed — a HIGH blocks | ✗ | **Not run.** Increment is not committed; independent review is the gate owner's call. |
| 7 | No file from another lane touched | ✓ | Batch did not fork. Serial overlap with Inc-3/Inc-4 on `store.py`/`model.py`/`app.py` declared in §5 risk 4. |
| 8 | Frozen interfaces untouched | ✓ | `git status` lists no `mapper/canvas.py` and no file under `mapper/views/`; `IRenderer.render` and `Canvas` byte-identical to `master` |
| 9 | Coverage claims verified **on disk**, not from intent | ✓ | Every count read from a command's own output: `265 passed`, `265 tests collected`, ruff `29` before and after via stash/pop, byte-scan sha256 per file |
| 10 | Load-bearing emptiness declared, with its synthetic instance (C-55) | ✓ | §4: the removed root fallback + its guards; `_diamond()` as the synthetic instance of a shape the tree cannot hold; three heterogeneous positive controls for the `None` probe |
| 11 | Mutation verdicts recorded **per arm**, inert arms named (C-40 rider) | ✓ | §4: 9 arms, per-resolved-node-id verdicts, parametrized suffixes preserved (`3 selectors -> 4 resolved arms`), 5 green groups named with the reason each is sound |
