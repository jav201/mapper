# 04 — Validation · `2026-08-26-repair-batch` (PR A) · whole-branch merge gate

> Reviewer: `qa-reviewer`, independent of `software-dev`, `code-reviewer` and `security-reviewer`.
> Base `origin/master` @ `d6b60e6b4f18b10123fffc76bbb36891473df653`. Branch `fix/shipped-defects-repair`.
> Tree state: **nothing committed, nothing staged** — the batch is entirely working-tree.
> Date 2026-08-27. Artifact language English; UI strings Spanish.

---

## 1 · BLUF

# CLEAR TO MERGE — conditional on two one-line pre-merge actions

**Zero HIGH.** Six MEDIUM, six LOW, one process defect. Every one of the five stories is
verified end to end by a node that reddens when its fix is removed — I established that by
running my own arms, not by reading the batteries. The four shipped defects are repaired and
the repairs are non-vacuously guarded.

**The two mandatory pre-merge actions**, both one line, both in files this batch already opened:

| # | Action | Why it is mandatory rather than advisory |
|---|---|---|
| **PM-1** | Add `prototypes/` to `.gitignore` — **or** stage by explicit path, never `git add -A` | `prototypes/**` is **not** ignored today. `git add -A --dry-run` stages **5 prototype files**. The plan states "never staged" three times as a scope invariant and `.gitignore` was opened *this batch* for preventive entries (`scratch/`, `out.txt`, `.env`) — this one was omitted. Decision **D13**'s ruff metric (29, not 57) is only valid while prototypes stay untracked. The merge is autonomous and the batch has four **untracked** test files to stage, which is precisely the situation that invites `git add -A`. |
| **PM-2** | Reconcile `01-requirements.md` §6 against disk | §6 asserts "**18 AT · 38 TC** … Every id is enumerated individually". Disk carries **22 AT · 48 TC**. Four ids were never registered at all (`AT-R17`, `TC-R36`, `TC-R37`, `TC-R38`). This is re-gate carry **`G5(b)` recurring** — the same table, the same omission, one increment after it was discharged. |

Neither is a defect in the repairs. Both are the batch's own declared standard, unmet at the
moment of merge, and each costs one line.

**What I did not find.** No requirement lacks a verifying node (the blocking direction of
traceability is clean: **56 of 56** registered ids resolve). No increment's guarantees were
weakened by a later one — established by reverting increment 4's source edits on an isolated
copy, not inferred from pass counts. No inert node among the ones I attacked: every arm I fired
reddened exactly the node it was aimed at, and the two that were *supposed* to stay green did.

---

## 2 · What I established independently

Everything in this section is my own execution on the tree as it stands at
`2026-08-27T15:27Z`. Commands and output are literal.

### 2.1 The numbers

```
$ PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:randomly -o addopts=
429 passed in 130.55s (0:02:10)                                       exit 0

$ python -m pytest -q -m slow
16 passed, 413 deselected in 38.80s      (run 3x: 38.80s / 39.39s / 41.16s, all green)

$ python -m ruff check mapper tests
Found 29 errors.
$ python -m ruff check .
Found 57 errors.                          57 - 29 = 28, all in untracked prototypes/ — D13 holds
```

**Ledger, reconciled on collected counts:**

```
$ pytest --collect-only -o addopts=                                          429 tests collected
$ pytest --collect-only --ignore=<all four repair files>                     245 tests collected
$ pytest --collect-only tests/test_repair_cycles.py                           25
                        tests/test_repair_depth.py                            91
                        tests/test_repair_fields.py                           51
                        tests/test_repair_layout.py                           17
                                                                    sum      184
```

**`429 = 245 − 0 + 184`.** The pre-existing count is **245**, exactly the declared base in
`PLAN.md` §2, so **D = 0** is verified rather than asserted: not one pre-existing node was
deleted. The per-increment chain (265 → 356 → 410 → 425 → 427 → 429) closes on the same
arithmetic; the final `+4` is `TC-R36` (×2 params), `TC-R37`, `TC-R38`.

Expected 429 / 16 / 29 — **all three match**.

### 2.2 Staging safety

```
$ git diff --cached --stat                                    (empty — nothing staged)
$ git check-ignore -v mapper.db prototypes/ui_next/x .env scratch/x out.txt
.gitignore:9:*.db       mapper.db
.gitignore:31:.env      .env
.gitignore:27:scratch/  scratch/x
.gitignore:28:out.txt   out.txt
                                          <- prototypes/ui_next/x: NO MATCH

$ git add -A --dry-run | grep prototype
add 'prototypes/ui_next/NOTES.md'
add 'prototypes/ui_next/generate.py'
add 'prototypes/ui_next/out/index.html'
add 'prototypes/ui_next2/NOTES.md'
add 'prototypes/ui_next2/generate.py'
```

`mapper.db` is **not staged and cannot be** ✓. `prototypes/**` is **not staged** ✓ but
**can be** ✗ — see **PM-1**. This is the one half of the brief's staging criterion I cannot
discharge as written.

### 2.3 Control-byte scan (PLAN §6)

16 touched files scanned byte-wise: **0 stray control bytes, 0 BOMs.** Clean.

### 2.4 Cross-increment regression — by construction, not by inference

I reverted **both** of increment 4's source edits on an isolated copy under the session
scratchpad (`help.py` restored to `d6b60e6`; the `#map-rail` CSS rule removed from
`MapperApp.CSS` by position) and re-ran everything else:

```
INC-4 REVERTED, all nodes except tests/test_repair_layout.py   ->  412 passed in 122.91s
INC-4 REVERTED, tests/test_repair_layout.py alone              ->  11 failed, 6 passed
```

`429 − 17 = 412`. **412 green before increment 4, the same 412 green after ⇒ 0 nodes from
increments 1–3 or from the pre-existing 245 changed verdict.** The revert bit hard (11 of 17
RED), and the 6 that stayed green are exactly the ones their construction predicts:
`AT-R10b` (the narrow-terminal negative), `AT-R14` (the oracle's own guard), `TC-R25`×2,
`TC-R26` (white-box, no compositor), `TC-R36[cap-governs]`.

**The close-out fold** touched `store.py` and `app.py` again after their batteries ran. I ran
four arms over the post-fold bytes to confirm the earlier increments' guarantees still bite:

| arm | operation (by position) | RED node-verdicts | what it proves |
|---|---|---|---|
| **X1** | `store.py`, sidecar-parse guard: typed re-raise → bare re-raise | `TC-R37` (1) | the fold's own store change is armed |
| **X2** | `app.py`, `GitHubError` handler: delete the `markup` keyword | `TC-R38` (1) | the fold's own app change is armed |
| **X3** | `store.py`, `_text_attributes`: derived tuple → hand-listed to what breaks today | `TC-R15`, `AT-R07c` (2) | **increment 3's A-7 guarantee survives the fold**, and the discriminating negative bites |
| **X4** | `app.py`, first `refresh_canvas`: `except Exception` → the batch's own two types | `TC-R08b` (1) | **increment 1's sink-class guarantee survives two later edits to the same file** |

Every restore sha256-verified back to its pre-mutation bytes. Harness lived **outside** the
repo it mutated (decision D8); `PYTHONDONTWRITEBYTECODE=1`; `__pycache__` purged per arm.

**Repo integrity:** the 16 touched files' sha256 at the end of this review are byte-identical
to their values at `15:27:16Z` (recorded in `scratchpad/BASELINE.sha256`). `git status` is
unchanged. All scratch copies deleted.

---

## 3 · Attacking the batch's own claims (brief §4)

This is the section the batch earned by making non-vacuous evidence its subject.

### 3.1 `TC-R38`'s markup census — **a hole found, then closed mid-review; a second hole remains**

I probed the census with two injected sinks carrying identical hostile content, differing only
in how they reach `notify`:

| arm | injected sink | `TC-R38` |
|---|---|---|
| **X5** | `self.notify("probe {}".format(self.map_id), severity="error")` — built by `.format()`, not an f-string | **RED** ✓ |
| **X6** | `notify = self.notify` then `notify("probe " + str(self.map_id), severity="error")` — same content, reached by a bare-name alias | **GREEN** ✗ |

**The shape dimension is genuinely closed.** X5 is exactly the `%`/`.format()`/concatenation
case the brief asks about, and the census catches it. (It did **not** before: the predicate was
`ast.JoinedStr`-only until it was widened at 09:23 today — see §7. My own wide census over the
pre-widening tree found one **live** escapee, `mapper/app.py:1055`, `self.notify(str(exc), …)`
with no `markup` keyword, carrying `GitHubError` text. That site now carries the keyword and the
widened census sees it. Both fixes verified on disk.)

**The root dimension is not closed.** The census's root is hand-picked:

```python
isinstance(node.func, ast.Attribute) and node.func.attr == "notify"
```

X6 escapes it for free. So does the sibling family the orchestrator named: `_event_toast`
(`mapper/app.py:1327`), which the pre-existing backlog item **B-07** already enumerated. I
measured `_event_toast` safe **by execution, not by reading** —

```
Text.assemble plain : ' ev[bold red]il[/]x   ev[bold red]il[/]x'   <- markup PRESERVED (safe)
from_markup plain   : 'evilx'                                       <- markup PARSED  (unsafe)
darkside.plain()    : 'ev[bold red]il[/]x'                          <- plain() is NOT a defense
```

— so there is **no live defect**. Current tree: 30 `notify` sites, 19 non-constant, **0 without
`markup=False`**, 0 bare-name calls, 0 aliases, 0 starred forwarding. The census is *correct
today*.

**But the docstring's claim is still false:** *"The site set is DERIVED by walking the AST of
every module (C-31), never hand-listed, so a new sink joins the census the moment it is
written."* A new sink written as `notify(...)` via an alias, or as a new `_event_toast`-shaped
helper, does not join it — X6 measures that. This is amendment **A-6**'s recorded lesson landing
inside the very node written to close the class: *"a derived probe with a hand-picked root is
not a derived probe — it is a hand-picked answer with a derivation wrapped around it, and it
reports an empty result with the same confidence either way."* **Fifth instance.** → finding
**M-2**.

**On the orchestrator's B-07 reading: it holds, and it is the sharper lesson.** B-07 named this
class at the batch-01 close, and three independent reviews inside *this* batch still
rediscovered it one instance at a time (`F2`, `F3`, `G1`, `M1`×2, `M3`). A backlog entry that
names a class is not a control, because nothing reads it at the moment the class is being
re-instantiated. The control is an executable census — which is why `TC-R38` is the right
answer and why its root needs widening rather than its existence defending.

### 3.2 `AT-R12` — does the scroll-union establish *presentation*, or just character presence?

`_painted_bindings` unions the dialog-clipped rows across every scroll position, joins with
`"\n"`, and tests `b.label not in painted`. So membership is **substring within one painted row
inside the dialog region** — labels contain no newline, so nothing matches across rows, and
`AT-R14` (four limbs, both clip dimensions armed) keeps the region honest.

The disclosed weakness is **exactly accurate**, which I verified rather than accepted:

```
map:  27 bindings; labels that are proper substrings of another: [('siguiente','siguiente faltante'), ('hijo','agregar hijo')]
home: 13 bindings; labels that are proper substrings of another: []
```

Precisely the two the docstring names. **The residual is not reachable by S-08's mechanism**:

```
'siguiente' at row 6 of 36  -> 30 rows after it
'hijo'      at row 9 of 36  -> 27 rows after it
```

The defect is a **tail clip** — a contiguous run off the bottom. Losing either shadowed label
requires also losing the 27–30 rows below it, which include many non-shadowed labels, so
`AT-R12` reddens loudly. Per-row omission is not a mode this container produces. **Answer: it
establishes presentation for 27 of 27 under the only failure mode the requirement is about.**
Recorded as a residual risk, not a finding.

### 3.3 `TC-R35` — is the narrowed claim now true?

Tested in **both** directions, which is the only way to answer it:

| arm | operation on `Graph.resolve_document` | result |
|---|---|---|
| **X7** | reintroduce a bounded chain walk **routed through `Graph.parent_of`** | **`TC-R35` RED** (1 failed, 141 passed) |
| **X8** | the same walk, deriving each parent by **scanning `self.edges` inline** | **142 passed, 0 RED** |

The narrowed docstring says, verbatim: *"A walk deriving each parent by scanning `self.edges`
INLINE never touches `parent_of` and leaves this node green."* **X8 confirms the disclosure is
true, and X7 confirms the gate still bites where it claims to.** `G2` is genuinely discharged —
the claim now matches the expression, and the widening is filed against `TC-R29`'s family rather
than asserted. This is the model of how an overclaim should be closed.

### 3.4 C-31 — is every quantified set derived?

Audited all 95 distinct nodes across the four files. Most are exemplary: `TC-R29`/`TC-R11`
(AST census rooted at the whole of `mapper/` and `views/`), `TC-R38` (`rglob`, no exemption
list), `AT-R14` (`_rows_outside` derived at runtime after a hand-picked sentinel was measured to
discriminate nothing), `AT-R09` (expected coverage derived from the fixture *and* cross-checked
against a literal), `TC-R30`'s indent-cap oracle (derived from the **uncapped** indent, so it is
independent of the value it gates).

Four genuine violations, and I settled the most serious one by execution:

**`RENDERERS` hand-lists 3 of 6 exported renderers.** `mapper/views/__init__.py` exports six;
the tuple names `radial`, `layered`, `outline`. `lane.py` declares **no `MAX_RENDER_NODES` at
all**. So `TC-R14`'s *"the renderers declare one shared bound"* iterates three modules it already
names and is structurally incapable of reporting the missing fourth.

I refused to infer the consequence and executed HLR-R02's normative promise instead:

```
--- acyclic chain, depth 5000 (5000 nodes), recursion limit 1000 ---
  LayeredRenderer          OK     0.07s        OutlineRenderer      OK     0.13s
  LaneRenderer             OK     0.00s        HybridLaneRenderer   OK     0.00s
  RailTimelineRenderer     OK     0.00s        RadialRenderer       OK     0.07s
  radial.MAX_RENDER_NODES : 12000     lane.MAX_RENDER_NODES : ABSENT
```

**HLR-R02 holds for all six.** The guarantee is carried by `TC-R11`/`TC-R29`'s AST census, whose
root *is* derived (`MAPPER_DIR` = all of `mapper/`) and therefore does cover `lane.py`. The three
lane renderers are also unreachable from the shipped UI — `_current_renderer` returns only
three, and nothing else in `mapper/` references them. So the gap is **`LLR-R02.3`'s degradation
contract, absent on unreachable code**: latent, not live. Wiring a lane view into
`_current_renderer` re-opens it with a fully green suite. → **M-5**, MEDIUM, not HIGH.

**`TC-R25`/`TC-R26` assert set equality for 2 of 6 reachable help scopes.** `KEYMAP` declares 8
scopes; `app.py:2050` opens help as `HelpScreen(getattr(self.screen, "KEY_SCOPE", SCOPE_APP))`
and six screens declare a `KEY_SCOPE` (`app, home, import, map, plug, repo`). The parametrize
list is `[SCOPE_MAP, SCOPE_HOME]`, hand-listed, where `sorted({b.scope for b in KEYMAP})` was one
expression away — and `TC-R26` in the same file already reaches for `KEYMAP`. Mitigating: the
render path has **no per-scope branching**, and `map` (27 bindings) is the tallest scope, so the
height-clip defect cannot manifest on `import` (4), `plug` (3) or `repo` (5). → **M-6**.

`TRAVERSAL_FILES` and `DEEP_TARGETS` are hand-picked roots/subject-sets, mitigated by `TC-R29`'s
whole-tree census. → **L-6**.

---

## 4 · Dual traceability

### 4.1 US → AT → on-disk node (black-box chain)

Every row verified to resolve to a real collected node, and **every row GREEN** in the
429-pass run.

| US | AT | node driving the whole chain (C-18) | file |
|---|---|---|---|
| **US-R01** | AT-R01 | `test_at_r01_opening_a_cyclic_map_refuses_it_without_killing_the_app` | cycles |
| | AT-R02 | `test_at_r02_the_message_names_the_actual_cycle_not_a_fixed_string` | cycles |
| | AT-R03 | `test_at_r03_an_acyclic_map_still_loads` (+ `AT-R03b` diamond, A-4's 2nd conjunct) | cycles |
| | AT-R15 *(A-2)* | `test_at_r15_a_well_formed_graph_still_saves_and_reloads` | fields |
| **US-R02** | AT-R04 | `test_at_r04_a_deep_acyclic_chain_renders_through_the_shipped_surface` — parses via shipped parser, renders all 3 wired renderers at DEEP, asserts output + bound | depth |
| | AT-R05 | `test_at_r05_a_3000_node_tree_renders_within_the_declared_bound` | depth |
| | AT-R16 *(A-6)* | `test_at_r16_the_rail_survives_a_depth_5000_map_through_the_composed_screen` — the composed screen, not a direct call, as A-6 requires | depth |
| **US-R03** | AT-R06 | `test_at_r06_a_scalar_field_loads_and_every_consumer_survives` | fields |
| | AT-R07 | `test_at_r07_a_container_field_loads_and_coverage_calls_it_missing` | fields |
| | AT-R07b *(A-7)* | `test_at_r07b_a_non_string_title_loads_and_search_hits_survives` | fields |
| | AT-R07c *(A-7)* | `test_at_r07c_a_non_string_state_also_survives_every_consumer` — the discriminating negative; **reddens under X3** | fields |
| | AT-R08 | `test_at_r08_the_operator_is_told_which_node_and_which_field` | fields |
| | AT-R09 | `test_at_r09_a_well_formed_maps_coverage_is_unchanged` | fields |
| **US-R04** | AT-R10 | `test_at_r10_the_three_regions_are_disjoint_and_on_screen` — both wide sizes, disjointness, on-screen, **and** `canvas.width == w − _chrome_width()`, one node | layout |
| | AT-R11 | `test_at_r11_the_canvas_paints_map_content_in_its_own_region` | layout |
| **US-R05** | AT-R12 | `test_at_r12_pressing_help_presents_every_map_binding` — 3 sizes, derived expected set | layout |
| | AT-R13 | `test_at_r13_the_same_holds_for_the_home_scope` | layout |
| | AT-R14 | `test_at_r14_the_oracle_is_clipped_to_the_help_dialog` — 4 limbs, both clip dimensions armed | layout |

**C-18 · "exactly one node driving the whole named chain".** Two ATs resolve to more than one
node — `AT-R04` (3) and `AT-R16` (6). Both **satisfy C-18**: in each case one node drives the
entire named chain and the siblings are supplementary probes (recursion-limit neutralisation,
call-depth ceiling, edge-list scan counts). Neither AT is "covered in parts". **No AT is
UNREALIZED.**

### 4.2 HLR → LLR → TC → on-disk node

Reconciled mechanically against `pytest --collect-only`:

```
A. REQUIREMENT WITHOUT A VERIFYING NODE  (the blocking direction)
   NONE — all 18 registered AT ids and all 38 registered TC ids resolve to a node on disk  ✓
```

The mid-batch renumbering is clean: `TC-R22`/`TC-R23` are back with `LLR-R04.1` in
`test_repair_layout.py` (`test_tc_r22_…`, `test_tc_r23_…`), and increment 3's displaced nodes
live as `TC-R33`, `TC-R33b`, `TC-R34`, with `TC-R35` as A-3's gate — all four present in §6's
US-R03 row. **`G5(a)` and the renumbering half of `G5(b)` are discharged.**

### 4.3 The gap — orphan nodes (**M-1**)

```
B. ORPHAN NODE (id on disk with no §6 registry row) — 14
   AT-R03b  AT-R10b  AT-R16b  AT-R17
   TC-R03b  TC-R04b  TC-R05b  TC-R06b  TC-R08b  TC-R09b  TC-R16b
   TC-R36   TC-R37   TC-R38
D. NODES CARRYING NO at_/tc_ id at all — 7
   test_find_cycle_returns_none_for_an_empty_graph
   test_c53_* (x4)                 test_coverage_* (x2)
```

Ten of the fourteen are `b`-suffixed siblings that strengthen a registered chain and remain
traceable through their parent id. **Four are ids that were never registered: `AT-R17`,
`TC-R36`, `TC-R37`, `TC-R38`** — A-3's pin and the three nodes added by increment 4 and the
close-out fold. The seven unattributed nodes are legitimate control-named nodes (`C-53`
false-refusal arms; A-9's coverage guards, one of which the re-gate called "the strongest node
in the increment").

No requirement is left unverified. What is false is §6's own sentence. → **PM-2 / M-1**.

---

## 5 · Carry discharge — every carry, its claim, and what is on disk

Checked by **re-reading the artifact and the tree**, never by trusting that a corrective pass
ran. ✓ = verified discharged · ⚠ = discharged with a residual · ✗ = still open.

### Increment 3 review · C1–C6

| # | Claim | On disk |
|---|---|---|
| **C1** (HIGH) | dead walk resolved via fix A; `TC-R35` reddenable | ✓ `model.py:128` `resolve_document` has no walk; **my arm X7 reddens `TC-R35`**, X8 confirms the disclosed limit. Positive control ("the call counter is not wired") present at `test_repair_fields.py:570`. |
| **C2** | declined — declare, don't widen (`F-M5` fenced out) | ✓ declined **with reason** recorded (`increment-003.md:29`), all four shapes tabulated in Risk 7 per `G4` |
| **C3** | assert `markup=False` at a notice node + arm | ✓ `TC-R20`, `TC-R20c` armed; independence measured (`M19`/`M20` redden one each) |
| **C4** | correct Risk 2 / pending 2 to the real residual | ✓ rewritten |
| **C5** | renumber `TC-R22`/`TC-R23` before increment 4 | ✓ zero occurrences in `test_repair_fields.py`; ids returned to `LLR-R04.1` |
| **C6** | LOW nits at discretion; `F11` → security | ✓ `F6`/`F10` applied; **`F7`, `F9` declined with reason** (`store.py:226`, `store.py:31` — both verified still present, both reasoned in D16); `F8` not applied and **now disclosed** |

### Increment 3 re-gate · G1–G6

| # | Claim | On disk |
|---|---|---|
| **G1** | arm the third `notify` sink | ✓ `test_repair_cycles.py:318-327` — stub captures kwargs, **`assert hits` precedes `all(...)`** (the exact `all([])` vacuity trap the security pass named), then asserts `markup is False`. Also covered as a class by `TC-R38`. |
| **G2** | narrow `TC-R35`'s docstring or widen the gate | ✓ narrowed, and **the narrowed claim is TRUE in both directions** — §3.3 |
| **G3** | fast-lane row `393 → 394` | ✓ `increment-003.md:204` reads `394 selected, 16 deselected · 394 passed` |
| **G4** | list all four measured malformed shapes | ✓ tabulated in Risk 7, moved out of §6 |
| **G5** | (a) §2 record `F6` applied / `F8` not; (b) §6 record the new ids | ✓ (a) `increment-003.md:136,139` tabulate all five with dispositions · ⚠ **(b) partially** — `TC-R33/33b/34/35` recorded, `AT-R17`/`TC-R36/37/38` never were → **M-1** |
| **G6** | mark the v1 transcript superseded | ✓ header present and explicit: *"SUPERSEDED BY mutation-battery-inc3.txt. NOT EVIDENCE FOR ANY GATE… the hashes in its FINAL block are the PRE-FIX values"* |

### Increment 4 review · F1–F5 — **the review returned BLOCKED; there is no re-gate artifact**

`increment-004-review.md` blocks on `F1` (HIGH) and no `increment-004-regate.md` exists. I
therefore discharged `F1` and `F2` myself against the transcripts and the tree.

| # | Claim | On disk |
|---|---|---|
| **F1** (HIGH) | `AT-R14` must guard the **column** clip; split `L8` into `L8a`/`L8b`, each with its own arm | ✓ **DISCHARGED.** `AT-R14` now carries four limbs (`test_repair_layout.py:375-400`); `mutation-battery-inc4-supplement-2.txt` records `L8a` (column clip alone) → **1 RED `AT-R14`** and `L8b` (row clip alone) → **1 RED `AT-R14`**. Each conjunct carries its own arm; item 7's ✓ is earned. |
| **F2** | `L5` is a genuine inert arm — accept it or collapse the two height declarations | ✓ **DISCHARGED by the stronger option**: a new predicate `TC-R36` was written instead of re-arguing, and `L5r` re-run against it → **1 RED `TC-R36[cap-governs]`**. C-40's prescribed response to an inert arm, correctly applied. |
| **F3** (LOW) | disclose `AT-R12`'s substring membership and the two shadowed labels | ✓ disclosed verbatim in the docstring; **claim measured exactly correct** — §3.2 |
| **F4** (LOW) | widen `TC-R22`'s `__dict__` guard to `DEFAULT_CSS` and `CSS_PATH` | ✓ `test_repair_layout.py:160` iterates all three |
| **F5** (LOW) | restate pending item 1: `01-requirements.md:188` still names `MapScreen.CSS` | ✗ **STILL OPEN.** `HLR-R04`'s touched-symbols line reads *"`mapper/app.py` `MapScreen.CSS` `#map-rail`"*. A-10 records the correction at §7; the body was never edited. → **L-1** |

### Security sign-off · M1–M5 / L1–L5

| # | Claim | On disk |
|---|---|---|
| **M1** | two unasserted `markup=False` keywords | ✓ closed **as a class** by `TC-R38`; **X2 confirms it reddens** at a real site |
| **M2** | hostile sidecar scalar denies the map with a bare `ValueError` | ✓ fixed as a **typed** refusal, attribution corrected (the proposed `_coerce_field` guard was measured unreachable — PyYAML raises inside `safe_load`); guarded by `TC-R37`, **X1 confirms it reddens**; `TC-R37` carries its own discriminating negative (one digit under the limit loads normally) |
| **M3** | fourth file-derived sink at `app.py:760` | ✓ `markup=False` present; in the census |
| **M4** | `MAX_RENDER_NODES = 12000` admits ~50 s of frozen UI | ⚠ **accepted knowingly**, recorded as backlog. Net improvement over master (measured 5.23 s vs 7.17 s at n=4000). Legitimate decline. |
| **M5** | `-m 'not slow'` deselects the batch's own acceptance; no CI | ⚠ declined to backlog with a manual pre-merge step. **I ran it: 16 passed, three times.** Discharged for this merge; the CI gap is real and carried. |
| **L1** | `.env` not gitignored | ✓ `.gitignore:31-32` — `.env`, `.env.*`, plus `scratch/`, `out.txt` |
| **L2** | operator paths + a session UUID in `.dev-flow/**` transcripts | ⚠ accepted for a private repo; **correctly flagged as a blocker for any public push.** Still true — the four `mutation-battery*.txt` files carry them. |
| **L3** | `app.py:1055/1058` interpolate remote-derived `GitHubError` text | ✓ **now closed** — `:1055` gained `markup=False` at 09:23 (§7) and both sites are in the widened census |
| **L4**, **L5** | `_text_attributes` hoist; `_pop_snapshot` unguarded | ⚠ backlog, both reasoned |

### Carried from increment 1, never discharged

| # | Claim | On disk |
|---|---|---|
| **`CYCLE_ARROW` separator** | increment 3's `F11` note: *"`CYCLE_ARROW` is `chr(0x2192)` with no surrounding spaces, so the message reads `a→b→a` while `LLR-R01.3` specifies the path joined by `" → "`… worth a one-line correction to `LLR-R01.3` at batch close."* | ✗ **STILL OPEN at batch close.** Executed: `parse('graph TD\n a --> b\n b --> a\n')` → `'the map has a cycle: a→b→a'`. `LLR-R01.2` and `LLR-R01.3` both still say `" → "`. And `TC-R05b` pins `ord(CYCLE_ARROW) == 0x2192` — the **implemented** codepoint, not the **specified** spacing, so the test set encodes the deviation rather than catching it. → **M-3** |

---

## 6 · Findings by severity

### HIGH — none

### MEDIUM

**M-1 · §6's traceability registry is false against disk; `G5(b)` recurring.**
`01-requirements.md` §6 asserts "**18 AT · 38 TC** … Every id is enumerated individually".
Disk: **22 AT · 48 TC**. `AT-R17`, `TC-R36`, `TC-R37`, `TC-R38` have no registry row. The
re-gate raised exactly this defect for increment 3's ids, it was discharged, and increment 4
plus the close-out fold reintroduced it. No requirement is unverified — this is a claim about
evidence that disagrees with disk, which is the defect this batch exists to stop.
*Fix: one table edit. →* **PM-2**.

**M-2 · `TC-R38`'s class-closure claim is root-bounded; fifth instance of A-6's pattern.**
The shape dimension is closed (X5 RED). The root dimension is not: X6 — an alias/bare-name
sink with identical hostile content — measures **GREEN**, and the `_event_toast` family
(backlog `B-07`) is outside the root entirely. No live defect: 0 offenders, 0 aliases on the
current tree, `_event_toast` measured markup-safe by construction. The docstring's "a new sink
joins the census the moment it is written" is nonetheless false.
*Fix: derive the callee set, or add a sibling assertion that `_event_toast` renders through
`Text.assemble`. Backlog unless the successor batch adds a sink.*

**M-3 · `LLR-R01.2`/`LLR-R01.3` specify a separator the code does not emit.**
Both LLRs use the normative **shall** and specify the cycle path *"joined by `" → "`"*. The
code joins with a bare `chr(0x2192)`; measured message `'the map has a cycle: a→b→a'`. Flagged
at increment 3 with "one-line correction at batch close"; the batch close is now and it is not
done. `TC-R05b` guards the implemented form, so nothing in the tree can catch the drift.
*Fix: one character in `mermaid.py:25`, or the two LLR lines. Pick one.*

**M-4 · `prototypes/**` is not ignored and `git add -A` stages it.** → **PM-1**. See §2.2.

**M-5 · `RENDERERS` hand-lists 3 of 6; `lane.py` has no declared degradation bound.**
`LLR-R02.3`'s contract is absent for `LaneRenderer`, `HybridLaneRenderer`,
`RailTimelineRenderer`, and `TC-R14` ("the renderers declare one shared bound") iterates a
3-element hand-list that cannot report the missing fourth. **HLR-R02 itself verified TRUE by
execution for all six at depth 5000**, and the lane renderers are unreachable from
`_current_renderer`, so this is latent. Wiring a lane view re-opens `LLR-R02.3` with a green
suite. *Fix: `[(n, getattr(views, n)) for n in views.__all__]`.*

**M-6 · `TC-R25`/`TC-R26` assert set equality for 2 of 6 reachable help scopes.**
`HLR-R05` quantifies over "the active scope"; six screens declare a `KEY_SCOPE` that reaches
`app.py:2050`. `import`, `plug`, `repo` and `app` get no assertion in either direction.
Mitigating: the render path has no per-scope branching and the tallest scope is covered.
*Fix: `sorted({b.scope for b in KEYMAP})` — one expression, and `TC-R26` already reaches for
`KEYMAP`.*

### LOW

- **L-1 · Increment 4 `F5` open.** `01-requirements.md:188` still names `MapScreen.CSS` as
  `HLR-R04`'s touched symbol. A-10 records the correction; the body was not edited.
- **L-2 · A battery transcript closes non-green with no re-verification.**
  `mutation-battery-inc4-supplement-2.txt:69` records the post-battery suite as `exit=1` with
  `test_at_r16b_…` FAILED. The same harness applies a **solo, bounded re-run** to exactly this
  node in `mutation-battery-inc3.txt:224/244` (*"the arm does NOT redden this node"*) and did
  not here. `AT-R16b` asserts a wall-clock bound (`FACTORY_TREE_BOUND_SECONDS = 8.0`) and is
  load-sensitive — the file's own comment records one earlier flake at a 2.0 s bound. I could
  not reproduce it (slow lane 3/3 green; 15/15 green under a 4-process CPU load), and the
  restore is independently proven by my 429-green run on those exact bytes. **The finding is
  the missing annotation, not the code.** By C-46 that transcript's restore proof is unmet as
  written.
- **L-3 · `PLAN.md` carry 3 undercounts.** It says *"Three screens push `HelpScreen()` with no
  scope"*; disk has **five** (`app.py:774, 825, 1090`, `factory.py:489`, `settings.py:95`).
- **L-4 · `AT-R13` lacks the vacuity guard its sibling has.** `AT-R12` asserts
  `len(expected) >= 20`; `AT-R13` asserts nothing about `expected`. If `bindings_for(SCOPE_HOME)`
  ever returned empty, `missing` is `[]` and the node passes having tested nothing.
- **L-5 · A comment claims a derivation that does not exist.** `test_repair_layout.py:43-44`
  says `WIDE_SIZES`/`NARROW_SIZE` are *"Derived from the rule the screen states … rather than
  hand-picked"*. They are literals; the arithmetic is only narrated. Failure is loud
  (`assert not screen.rail_hidden`), so no member is silently untested — but a comment claiming
  derivation is worse than one admitting a sample, because it stops the next reader checking.
- **L-6 · Two more hand-picked roots.** `TRAVERSAL_FILES` (2 files) roots `TC-R32`'s
  cyclic-termination census; `DEEP_TARGETS` hand-lists 6 callables where
  `graph_touching_methods()` exists in the same file. Both mitigated by `TC-R29`'s whole-tree
  recursion census.

### PROCESS

**P-1 · The tree was edited while this gate was running.** Three edits landed at 09:17–09:23 on
2026-08-27, after this review began: `app.py:1055` gained `markup=False`, `TC-R38`'s predicate
was widened from f-string-only to non-constant, and `.gitignore` gained four entries. The
orchestrator disclosed this unprompted, named it as its own process defect, and invited me to
record it rather than absorb it. **Every measurement I had taken before 15:27:16Z was voided and
re-taken**; the full suite, the ruff figures, the collection counts, the notify census and all
eight mutation arms in this document are against the post-edit tree, pinned by
`scratchpad/BASELINE.sha256`. The edits are correct and I verified both by execution (X2, X5).
Recording it because a gate that measures a moving tree cannot say what it measured — the
disclosure is what made this recoverable, and it is the same failure family as the unlanded-v2
transcript incident in `PLAN.md` §Session 5.

---

## 7 · Residual risks (accepted, not findings)

1. **`AT-R12` cannot distinguish two of 27 labels individually** — `siguiente` and `hijo` are
   proper substrings of siblings. Measured unreachable by the tail-clip mechanism (§3.2);
   `TC-R25` owns exact `(glyph, label)` equality at the white-box layer. Disclosed accurately.
2. **Wall-clock assertions inside the battery's verdict surface.** `AT-R16b`, `AT-R04`,
   `AT-R05` and `TC-R14` bound elapsed time. A false RED under load is indistinguishable from a
   real one unless the harness re-runs solo — which it does, but did not once (L-2). The
   *requirement* is pinned by load-independent scan counts (`MAX_EDGE_LIST_SCANS = 4`, measured
   0), so this is a harness-trust risk, not a coverage risk.
3. **`M4` — a 12000-node map can freeze the UI ~50 s.** Knowingly accepted; still an
   improvement on master.
4. **`M5` — no CI; the slow lane is a manual pre-merge step.** Discharged for *this* merge by my
   three green runs. The next merge inherits the same manual obligation.
5. **`L2` — operator paths and a session UUID in the four `mutation-battery*.txt` files.**
   Acceptable for a private repo; **a blocker for any public push**, and that condition
   survives this merge.
6. **`F-M5` remains fenced out.** A container-valued field is repaired; a non-`dict` node entry,
   a list `nodes` block, a non-list `attachments` and an attachment missing `kind` still deny the
   map. Declared in Risk 7, correctly declined.
7. **`F7`/`F9` declined** (`store.py:226` recomputation, `store.py:31` unreachable `str`). Both
   verified still present, both reasoned in D16, neither changes a value.

---

## 8 · Evidence checklist

| # | Item | | Evidence |
|---|---|---|---|
| 1 | Acceptance criteria in Given/When/Then form | ✓ | `01-requirements.md` §2 — each story states Given/When/Then and names its ATs |
| 2 | Test cases have explicit Expected, not vague "works" | ✓ | e.g. `AT-R09` derives expected coverage from the fixture *and* pins `== (4, 4)`; `TC-R36` asserts `dialog.region.height == 28` / `21` with the governing declaration named |
| 3 | Edge cases: empty · boundary · invalid · error | ✓ | empty `test_find_cycle_returns_none_for_an_empty_graph`; boundary `TC-R14` at and past the bound, `TC-R37` at `int_max_str_digits ± 1`; invalid `TC-R17` containers, `TC-R18` non-`dict`; error `TC-R08` any renderer exception, `TC-R09b` over five exception types |
| 4 | Regression checklist exists | ✓ | §2.4 — inc-4 revert (412/412 unchanged) + arms X1–X4 over the post-fold bytes |
| 5 | Exit criteria stated | ✓ | §1 — CLEAR TO MERGE conditional on PM-1 and PM-2; zero HIGH is the gate |
| 6 | No real PII / secrets in this artifact | ✓ | no credentials, no tokens; operator paths not reproduced here (L-2 references them by filename only) |
| 7 | Results section blank unless actually run | ✓ | every number in §2 and §3 is from my own execution; §5's discharge column distinguishes what I re-ran from what I re-read |
| 8 | **Layer B (black-box):** every output-producing story observed through the SHIPPED surface, with boundary + negative evidence | ✓ | US-R01 `AT-R01` through `MapStore.load` + the Textual pilot, negative `AT-R03`/`AT-R03b`; US-R02 `AT-R04` through `mermaid.parse` + `renderer.render`, boundary `TC-R14`; US-R03 `AT-R06`–`AT-R09` through the loader, negative `AT-R09` (coverage unchanged) and `AT-R07c` (`state`); US-R04 `AT-R10`/`AT-R11` through the compositor, negative `AT-R10b`; US-R05 `AT-R12`/`AT-R13` through a real `?` keypress at three sizes, negative `TC-R26` |
| 9 | **Bidirectional surface-reachability:** every named input AND every named output exercised through the handler | ✓ | inputs: cyclic `.mmd` via `parse`, cyclic CSV via `preview_csv` (`TC-R08b` — the door that bypasses the parser), malformed sidecar via `MapStore.load`, hostile sidecar scalar via `yaml.safe_load` (`TC-R37`); outputs: the Spanish notice observed at the `notify` sink (`TC-R20`/`TC-R20c`/`TC-R09b` capture kwargs), the canvas observed region-clipped (`AT-R11`), the legend observed on the composited frame across every scroll position (`AT-R12`), the saved file observed by reload (`AT-R15`) and by absence (`TC-R28`) |
| 10 | **No unfilled template** — no `<...>`, no `TC-NNN`, no empty required rows | ✓ | grepped all nine batch artifacts; the only `placeholder` occurrences are inside `PLAN.md`'s retained *record* of the increment-2b block, quoting what was rejected |
| 11 | Ledger reconciles | ✓ | `429 = 245 − 0 + 184`, base independently re-measured at 245 (§2.1) |
| 12 | Repo unmutated by this review | ✓ | 16 files sha256-identical to `scratchpad/BASELINE.sha256`; all mutation work on copies under `%TEMP%\claude\...\scratchpad\xreg`; every arm's restore hash-verified; `git status` unchanged |

---

## 9 · Verdict

```
[x] CLEAR TO MERGE — conditional on PM-1 and PM-2
[ ] BLOCKED
```

**0 HIGH · 6 MEDIUM · 6 LOW · 1 process defect.**

The four shipped defects are repaired, and — the part that matters for a batch whose subject is
non-vacuous evidence — **the repairs are guarded by nodes that measurably fail without them.**
Eight independent mutation arms, every one reddening exactly its target, including two aimed at
the earlier increments' guarantees across files that were edited twice more afterwards.
Increment 4's HIGH is discharged with per-conjunct arms. `G2`'s overclaim is closed and I
verified the narrowed claim in both directions. The one hole I found in the batch's central
self-claim — `TC-R38`'s f-string-shaped census — was closed mid-review and I confirmed the fix
by execution.

The two conditions are bookkeeping the batch already owes itself: an ignore rule for the
directory its own scope fence names three times, and a traceability table that matches the tree
it describes. Neither is a defect in the code. Both should land before the branch does.

*Reviewed by `qa-reviewer`. Nothing in this validation was taken on the word of another
artifact; where I cite a transcript I say so, and where I ran it myself the command and its
output are in §2 and §3.*
