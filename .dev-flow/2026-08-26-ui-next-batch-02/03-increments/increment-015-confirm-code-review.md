# Code Review — Increment 015 · Inc-CONFIRM (part 1) · `HERMETIC-1` + `B-68`

| Field | Value |
|---|---|
| Reviewer | `code-reviewer` (independent; authored none of this diff) |
| Batch | `2026-08-26-ui-next-batch-02` · FULL protocol per `D35` |
| Base | `a552783` |
| Date | 2026-09-19 |
| **Verdict** | **BLOCK — 1 HIGH** |

---

## Scope reviewed

`git diff a552783` in full, plus the staged-untracked `tests/test_hermetic.py`:

- `mapper/app.py` — `action_export_svg` (3469–3479), `EXPORT_EXTENT_STEPS` (3486), `_export_view_state` (3488–3557)
- `pyproject.toml` — 33–50 (`addopts`, `markers`)
- `tests/conftest.py` — 1–147 (all new below line 14)
- `tests/test_hermetic.py` — 1–253 (new)
- `tests/test_app.py` — 79–124 (`test_repo_screen_two_pane_renders`), 449–520 (`test_b50_…`)
- `tests/test_pan.py` — 677–823 (new `B-68` block)
- `tests/test_search.py` — 1482–1491 (`_PASS_FREE_READERS`)
- `tests/test_a3_census.py` — 219–244, 282–302, 400–418 (pin moves)

Read in support, not under review: `mapper/github.py:44–58,137–156,245–263`, `mapper/diff.py:24–47`,
`mapper/osopen.py` (whole), `mapper/views/layered.py:300–416`, `mapper/app.py:1636–1770,2667–2730`,
`.dev-flow/state.json` (`controls_for_engineering_rules`, 40 entries; `hermetic_defects[0]`; `B-68`),
`01-requirements.md` amendment set 7 / `A-99`.

All measurements below were taken on a **copy of the tree outside the repo**
(`C:/Users/<operator>/cr_mapper`). **No file in `C:/Users/<operator>/Github/mapper` was modified by this review**
except this report.

---

## Findings

### F1 — the `B-68` invariance arm passes on a totally broken export  [Severity: **HIGH**]

- **What:** `_export_bytes` presses `e` and then reads the artifact **off disk without proving the
  press wrote anything**. `action_export_svg` swallows every exception into a toast
  (`mapper/app.py:3477–3478`), so an export that fails at the panned position leaves the file from the
  *first* press in place, and `at_edge == at_origin` is then a comparison of a file **against itself**.
  The arm's own docstring calls byte-equality "the only predicate that distinguishes *the state was
  removed* from *the state was bounded*" — it does not distinguish either from *the export did not run*.
- **Where:** `tests/test_pan.py:683–694` (`_export_bytes`), consumed at `tests/test_pan.py:763` and
  `:777` by `test_b68_the_export_is_invariant_under_the_operators_pan`.
- **Why it matters:** this is the acceptance node for `A-99`. **Measured, not argued** — MUTANT B, applied
  to the scratch copy at `mapper/app.py:3472`:

  ```python
  if self.pan_x or self.pan_y:
      raise RuntimeError("MUTANT B: export explodes when panned")
  text = renderer.render(self.graph, self._export_view_state(size))
  ```

  ```
  python -m pytest tests/test_pan.py -q -k b68 -p no:randomly
  2 passed, 26 deselected in 9.04s
  ```

  The export is **completely dead at every non-zero pan** — the exact condition `B-68` is about — and
  **both** acceptance arms stay green. Arm 2 cannot compensate: it never pans, so it exports only at
  the origin. This is the batch's dominant defect class landing on the increment that closes it, which
  the catalog already names (*THE INCREMENT THAT CLOSES A DEFECT FAMILY IS THE INCREMENT MOST LIKELY TO
  INTRODUCE A MEMBER OF IT*), and it violates *TRIGGER-INDEPENDENCE IS NOT DISCRIMINATING POWER — an
  invariant arm must ASSERT THE TRIGGER ACTUALLY OCCURRED before asserting the invariant.* The arm
  asserts one trigger (the pan moved, `:773`) and not the other (an artifact was produced at that pan).
- **Suggested fix** — make the artifact's freshness part of the read. **I verified this remedy kills
  MUTANT B** (applied on top of it: `1 failed, 1 passed`, failing on
  `AssertionError: the `e` chord produced no artifact -- the export failed`):

  ```python
  async def _export_bytes(screen, pilot) -> bytes:
      path = screen.store.workspace / f"{screen.map_id}.svg"
      # A STALE ARTIFACT MUST NOT BE READABLE AS A FRESH ONE.  `action_export_svg`
      # swallows every failure into a toast, so without this the second press can
      # do nothing at all and the invariance assertion compares a file to itself.
      if path.exists():
          path.unlink()
      await pilot.press("e")
      await pilot.pause()
      assert path.exists(), "the `e` chord produced no artifact -- the export failed"
      return path.read_bytes()
  ```

  A mtime/size check is **not** an acceptable substitute (Windows mtime granularity, and a correct
  re-write is byte-identical by construction here). Unlinking is the only form that fails closed.
  Re-run the R1/R2 counterfactuals afterwards so the strengthened arm carries its own RED proof.

---

### F2 — the extent loop's exhaustion path silently re-ships the defect  [Severity: MEDIUM]

- **What:** `for _ in range(self.EXPORT_EXTENT_STEPS)` returns the last grown `state` **without
  re-checking that it fits** (`mapper/app.py:3540–3557`). On exhaustion the export proceeds and
  `action_export_svg` toasts `"exportado"` over a cropped artifact — `B-68`'s harm shape exactly
  (*a file that looks complete to both parties and is not*), now with no pan to blame. Nothing tests
  the branch.
- **Where:** `mapper/app.py:3540` (loop) and `:3557` (unverified return).
- **Why it matters:** I could not reach it, so it is currently defensive rather than live — but the
  failure it degrades to is the defect, and it degrades **silently**. The `EXPORT_EXTENT_STEPS = 6`
  docstring claim is **TRUE and I reproduced it**: simulating the loop over six shapes (200-, 1000-
  and 4001-wide fanouts, a 60-deep chain, 300 leaves with 40-char titles, a 40×2 grid) it converges in
  **exactly one step in every case**, e.g. `fan-4000: step0 extent_x=47997 span_x=118 → step1
  w=48001 span_x=47999 FITS`. So `6` is honest headroom, not cargo, and the constant is justified.
- **Suggested fix:** one line after the loop, so the failure is loud and lands in the handler that
  already exists:

  ```python
      raise RuntimeError(
          f"the export extent did not settle in {self.EXPORT_EXTENT_STEPS} steps; "
          "a cropped artifact is B-68, so refuse rather than ship one"
      )
  ```

  `action_export_svg`'s `except` then toasts `exportación fallida: …` instead of `exportado`.

---

### F3 — "full extent" is geometric only; wide maps still lose their titles  [Severity: MEDIUM]

- **What:** the loop grows the canvas until the **laid-out extent** fits, but `layered._geometry`
  computes that extent at the **floor** card width. Measured on the scratch copy: 300 leaves with
  40-character titles converges at `w=3601`, and at that width
  `_geometry(...).card_w == 9`, `title_width("root") == 6`. A 40-character title is emitted as 6
  characters. The artifact is geometrically complete and textually truncated.
- **Where:** `mapper/app.py:3552–3556` (the growth step) against `mapper/views/layered.py:337–340`
  (`card_w = max(9, (avail - (n_leaves - 1) * gap) // n_leaves)`).
- **Why it matters:** it is **not a regression** — the canvas clamps identically, and `B-68`'s measured
  65 % loss is genuinely closed. But the packet §1 ("the render is sized to the map's **full extent**")
  and the docstring's "the recipient wants the MAP" will be read as *nothing is lost*, and acceptance
  arm 2's fixture has short titles so nothing covers it. Per the catalog's *H1, REFINED* and
  *DISTRUST IS NOT A DIRECTION — every replacement measurement carries its own boundary statement*,
  this needs its boundary stated.
- **Suggested fix:** no code change. Add to §6 beside pending item 5, and one sentence in the
  `_export_view_state` docstring: *the extent is measured at the geometry's clamped `card_w`, so on a
  map wide enough to drive `card_w` to its floor the export carries every node at a truncated title
  width — the crop moved from the frame to the card, and closing that is a separate ruling.*

---

### F4 — the git subcommand table bans two offline operations, and is one-way  [Severity: MEDIUM]

- **What:** `_REMOTE_GIT_SUBCOMMANDS` contains `remote` and `submodule`. `git remote -v`,
  `git remote add origin <path>`, `git remote get-url` and `git submodule status` contact nothing.
  The module's own header argues for per-invocation classification precisely so local git stays legal
  ("*a ban that broad gets routed around*") — and then bans two local readers.
- **Where:** `tests/conftest.py:46–48`.
- **Why it matters:** no product code and no test issues these today (I checked every
  `subprocess.` site under `mapper/` and `tests/`), so nothing is red now. The cost is future: the
  first arm that sets up a fixture remote gets a refusal naming "contacts a remote" for something that
  does not. It is also asymmetric with the increment's own best idea — the **executable** census is
  compared *both ways* (`tests/test_hermetic.py:119–131`), while the **subcommand** table is compared
  in neither direction: 5 of its 7 entries (`pull`, `push`, `ls-remote`, `remote`, `submodule`) have
  no product invocation and no arm. That is *ANYTHING SPELLED TWICE WILL DRIFT* one level down.
- **Suggested fix:** narrow to `{"clone", "fetch", "pull", "push", "ls-remote"}`; if the two
  update-style cases are wanted, classify on the **second** token (`remote update`, `submodule update`)
  rather than the first. Then add the negative arms to the parametrisation at
  `tests/test_hermetic.py:137–150`:

  ```python
  (["git", "remote", "-v"], False),
  (["git", "-C", "/tmp/x", "submodule", "status"], False),
  ```

---

### F5 — `_resolve_indirect_argv`'s docstring misdescribes its own scope  [Severity: LOW]

- **What:** the comment at `tests/test_hermetic.py:87–88` says the argv is "resolved by reading the
  assignment **in the same function**"; the implementation `ast.walk`s the **whole module tree** and
  matches any `Assign` to that name (`:98–99`). It happens to be right for `_gh`'s `cmd`, but a
  module with two functions binding the same local name would cross-contaminate.
- **Where:** `tests/test_hermetic.py:87–88` vs `:98–99`.
- **Why it matters:** the catalog names this exact shape — *the comment saying "DERIVED" is itself a
  spelling, and the declaration of derivation must be audited against the code that does it*.
- **Suggested fix:** either scope the walk to the enclosing `FunctionDef`, or change the comment to
  "…by reading every assignment to that name **in the module**, which over-approximates".

---

### F6 — `VIEWER_LAUNCH_UNGUARDED` is a constant nothing reads  [Severity: LOW]

- **What:** defined at `tests/test_hermetic.py:49`, referenced by zero code in `tests/` or `mapper/`
  (grepped). `open` and `xdg-open` *are* derived and both-ways checked via `DECLARED_SPAWNS`, but
  `os.startfile` and the path `mapper/osopen.py` are spelled in a free-text string that will go stale
  without anything noticing.
- **Where:** `tests/test_hermetic.py:41–49`.
- **Why it matters:** the gap itself is honestly declared in §6 item 2, so this is about the
  *mechanism*, not the honesty. Per *VIGILANCE IS NOT A CONTROL*, the string is documentation wearing
  a constant's clothes.
- **Suggested fix:** derive it — one extra AST predicate for `os.startfile` (an `ast.Attribute` with
  `value.id == "os"`, `attr == "startfile"`) folded into the same census, classified
  `"viewer-launch"`. Or drop the constant and leave the paragraph as a comment, so it is not mistaken
  for a check.

---

### F7 — the `except Exception` fallback's comment states the wrong prior behaviour  [Severity: LOW]

- **What:** `mapper/app.py:3543–3548` says "the terminal-sized state is what shipped before this
  method, so the fallback is the old behaviour rather than no export". The old behaviour was
  terminal-sized **carrying the live pan**; this fallback is terminal-sized with the pan zeroed. The
  scoping itself is **correct and conventional** — it wraps `pan_extent` only, exactly as
  `_pan` does (`mapper/app.py:1748–1761`), and sits inside `action_export_svg`'s sink guard the way
  `_reclamp_pan` sits inside `refresh_canvas`'s (`:2678–2686`). I also believe the branch is
  unreachable: the only raiser is `_tree_layout` on a non-tree, and `renderer.render` raises on the
  same graph two lines later, landing in the outer handler.
- **Where:** `mapper/app.py:3545–3548`.
- **Suggested fix:** "the terminal-sized state, pan already neutralised — the old *size* rather than
  the old *state*, and better than no export."

---

## Claims I was asked to verify — measured, not taken

| Claim in the packet | My measurement | Verdict |
|---|---|---|
| `b50`'s repaired double still kills the `diff=None` mutant | added `diff=None` to the `replace()` at `mapper/app.py:3534–3538` in the scratch copy → `1 failed`, `AssertionError: the export dropped the active diff` | **TRUE** |
| `b50`'s assertions are unchanged | diffed base vs head bodies: only the double's construction changed (`_current_renderer` factory → `monkeypatch.setattr(screen.renderer, "render", …)`); all seven asserts byte-identical, and `assert "state" in seen` still fails loudly if the spy never fires | **TRUE — not a weakening** |
| `test_repo_screen_two_pane_renders` is not weakened by mocking the seam | MUTANT C (`self.graph = Graph()` after `worker.wait()` at `mapper/app.py:1166`) → `1 failed`. The **base** arm (`assert table is not None`) would have passed it | **TRUE — strictly strengthened** |
| A3 zero-arg `34 → 35`, itemised as `test_app.py`'s `table.render().plain` | derived `render_call_sites()` at `a552783` and at head: base 34 / head 35. Delta = `+('tests/test_app.py', 123)` (the new `table.render().plain`) and `477 → 519`, a pure line shift of the pre-existing `hero.render().plain` | **TRUE** |
| A3 arg-ful `62 → 61`, and the decrease hides no removed renderer-protocol call site | base 62 / head 61. Per-file net: `mapper/app.py` **0**, `tests/test_pan.py` **0**, `tests/test_search.py` **0**, `tests/test_app.py` **−1**. The removed site is base `tests/test_app.py:427` = `return renderer.render(graph, state)` **inside the anonymous `Spy`**. No product call site moved | **TRUE — the decrease is legitimate** |
| the `R1` pre-fix counterfactual reddens both arms at 47,263 bytes | reproduced accidentally-then-deliberately on the scratch copy with `mapper/app.py` at `a552783`: `2 failed`, message `…47263 bytes at the origin against…`, and arm 2 `dropped 3 of 14 nodes` | **TRUE** |
| the lane guard's `network_reaching` models every argv the product really builds | read the five real sites myself: `github.py:46` `["git","-C",str(cwd)]+args`, `:145` `["git","clone","--mirror",…]`, `:248` `cmd = ["gh"]+args`, `diff.py:36` `["git","show",…]`, `osopen.py:52,54` `["open"/"xdg-open", target]`. Derived executable set `{git, gh, open, xdg-open}` == `DECLARED_SPAWNS` | **TRUE** |
| the guard's delegation is correct / blast radius is refusals only | every `subprocess.*` call site in `mapper/` and `tests/` passes argv **positionally** — no `args=` keyword anywhere — so `guarded_run(argv, *args, **kwargs)` cannot `TypeError`. Ran every subprocess-spawning module under the guard: `tests/{test_github,test_diff,test_canvas,test_darkside_census,test_fold,test_inc3_census,test_repair_artifact_claims}.py` → **195 passed, 3 xfailed in 37.00s**, zero false refusals | **TRUE** |
| (bonus, better than claimed) the guard covers only `run`/`Popen` | it covers **more**: `subprocess.run`, `call`, `check_call` and `check_output` all resolve `Popen` from the module globals, so a probe placed inside `tests/` had **all three** of `check_output` / `call` / `run` refused and recorded (3 violations at teardown). Worth saying in the packet — the coverage is wider than §5 claims | **UNDERSTATED, in the safe direction** |
| `_export_view_state` earns its `_PASS_FREE_READERS` exemption | the loop uses `replace(state, w=…, h=…)` and **never re-calls `_view_state`**, so `hits` is resolved exactly once at `mapper/app.py:3534`. The stated reason ("keyed on graph+query, which growing the canvas cannot change") is true of the code as written | **TRUE** |
| the loop cannot hang or return a degenerate size | bounded by `range()`, so termination is structural; `w`/`h` are monotonically non-decreasing (`max(0, …)` guards both terms) and floored at `max(20, …)` / `max(5, …)`; `pan_extent` returns a non-raising tuple when `_geometry` is `None` (empty graph, `>MAX_RENDER_NODES`), which converges on step 0 | **TRUE** (but see **F2** for the exhaustion return) |
| `EXPORT_EXTENT_STEPS = 6` is measured headroom, not cargo | reproduced: one step on all six shapes I simulated | **TRUE** |
| ruff sets equal at equal scope | `ruff check --isolated` over the eight changed files: 3 findings, all pre-existing (`mapper/app.py:5` F401 `re`; `tests/test_app.py:2,12` F401). **Zero** in `conftest.py`, `test_hermetic.py`, `test_pan.py` | **TRUE** |
| signed-balance ledger `1109 = 1095 − 0 + 14` | `--collect-only` at head: `1112/1132 tests collected (20 deselected)`; `1109 passed + 3 xfailed = 1112` reconciles | **TRUE at collection** |

Two things I checked because they would have been cheap to get wrong and were not:
`pytest_plugins = ["pytester"]` in the non-rootdir `tests/conftest.py` is accepted on pytest 8.3.4
under `pytest`, `pytest .` and nodeid invocations (initial-conftest exemption) — no portability
finding; and `pytester.runpytest_subprocess` spawns `sys.executable`, which `_executable` classifies
as `python` and the guard lets through.

---

## Verdict

- [ ] OK to advance
- [ ] `BLOCK-UNTIL: …`
- [x] **Block — 1 HIGH finding open (`F1`)**

**`F1` blocks.** The increment's own acceptance arm for `A-99` passes while the export is dead at
every non-zero pan — measured, MUTANT B, `2 passed`. Nothing about this is a style preference: it is a
test that gives false confidence about the exact behaviour the increment was opened to fix. The fix is
five lines in a test helper and I have verified it kills the mutant; once `software-dev` applies it and
re-runs the `R1`/`R2` counterfactuals against the strengthened arm, **I must re-read the diff and
verify it on the tree** before this moves — a recommended fix does not close a HIGH, and I will not
mark this OK on a report that the corrective pass ran.

`F2`–`F7` are recommendations and do not block. `F2` and `F3` are the two I would most want taken
before the whole-branch gate, because both are silent-content-loss shapes in a batch whose whole
subject is silent content loss.

**Everything else in this diff is sound, and the two riskiest claims in it are true.** The `b50`
double repair is a genuine strengthening rather than a softening, the arg-ful census decrease is
legitimate and hides nothing, and the lane guard's blast radius is smaller than feared and its
coverage wider than declared. The increment is close.

---

## Evidence checklist

| Item | ✓/✗ | Evidence |
|---|---|---|
| Diff read in full | ✓ | all 8 changed files + the untracked `tests/test_hermetic.py:1–253`; ranges listed under **Scope reviewed** |
| Correctness pass (edge / None / error paths) | ✓ | loop termination, monotonicity and the `_geometry is None` path traced at `mapper/app.py:3540–3557` vs `mapper/views/layered.py:401–415`; `except Exception` scoping compared against `_pan` (`:1748`) and `refresh_canvas` (`:2678`) — **F2**, **F7** |
| Simplicity pass (no premature abstraction) | ✓ | `EXPORT_EXTENT_STEPS = 6` simulated over six graph shapes — converges in 1, headroom justified, not cargo. `_export_view_state` is one `replace()` + one bounded loop; not over-built |
| Reuse / duplication checked | ✓ | the `_consumes_pan` decline reuses `_reclamp_pan`'s seam (`:1727`) rather than re-deriving; `pan_extent` is the shared exported helper, not a second geometry; the mocked seam is the one `test_plug_repo_url_flow` already used |
| Tests reviewed for intent, not just behavior | ✗ | **F1** — `tests/test_pan.py:683–694` asserts an invariant over an artifact it never proves was produced; MUTANT B green |
| Verdict explicit, and every HIGH absent or applied-and-verified | ✓ | **Block — 1 HIGH (`F1`)**; fix is RECOMMENDED and its kill verified, **not applied**, so the HIGH stays open |

## Evidence states

| Item | State |
|---|---|
| `F1` (HIGH, vacuous invariance arm) | `executed` — mutant applied, arms green, remedy's kill verified; **fix `planned`, not applied** |
| `F2` (loop exhaustion silent) | `executed` — convergence simulated on 6 shapes; exhaustion branch `not-run` (unreachable on measured shapes) |
| `F3` (title truncation at floor `card_w`) | `executed` — `card_w == 9`, `title_width == 6` at convergence, 300×40-char fixture |
| `F4` (over-broad git subcommands) | `executed` — full `subprocess.` census of `mapper/` and `tests/`; no live false-fail today |
| `F5`, `F6`, `F7` | `executed` — read against the code they describe |
| `b50` non-weakening | `approved` — mutant KILLED |
| `repo_screen_two_pane` non-weakening | `approved` — MUTANT C KILLED; base arm would have survived |
| A3 census pins (both) | `approved` — both sets derived at base and head and diffed per file |
| `R1` pre-fix counterfactual | `approved` — independently reproduced |
| lane-guard blast radius | `approved` — 195 passed / 3 xfailed across every spawning module |
| ruff set equality | `approved` — 3 findings, all pre-existing |
| full default lane (1109/20/3) | `not-run` — I started a full `-q -p no:randomly` run and **cancelled it before it returned**, so I confirm the packet's tail figure with nothing. Stated rather than implied. What I did run is the 195-node subprocess-module sweep and the 1112-node collection reconciliation above; the lane tail itself is `n/a — qa-reviewer's lane` |
| security lens (`SEC-H2`, `gh` credential surface, `osopen` launch policy) | `n/a — security-reviewer's lane`; routed, not duplicated here |
| `FLAKE-1` | `blocked` — pre-existing, owed at the whole-branch gate; a green lane containing it is a weaker green and that does not change with this increment |
