# Code Review — Increment 002 (`LLR-N07.2.2a` · `LLR-N07.2.3` · `HLR-CNV.3`)

| Field | Value |
|---|---|
| Reviewer | `code-reviewer` (independent) |
| Batch | `2026-08-26-ui-next-batch-02` · branch `feat/ui-next-batch-02` |
| Scope | `4eaba35`..working tree — `mapper/ tests/ docs/`, plus staged `mapper/views/state.py` and untracked `tests/test_a3_census.py` |
| Date | 2026-08-28 |
| **Verdict** | **BLOCK — 3 HIGH findings** |

---

## Scope reviewed

922 diff lines across 17 tracked files + 1 staged new source file + 1 untracked new test file.

- Source (6): `mapper/views/state.py` (new, staged), `mapper/views/layered.py`, `mapper/views/lane.py`,
  `mapper/views/outline.py`, `mapper/views/radial.py`, `mapper/app.py`
- Tests (11): `test_a3_census.py` (new, untracked), `test_app.py`, `test_layered.py`, `test_export.py`,
  `test_lane.py`, `test_outline.py`, `test_radial.py`, `test_legacy_fixture.py`, `test_repair_depth.py`,
  `test_repair_map_truth.py`, `test_repair_perf_shape.py`
- Doc (1 in scope): `docs/ARCHITECTURE.md:159`

No file under `mapper/`, `tests/` or `docs/` was modified by this review. Working tree and
`git status --short` are byte-identical to the state I received. `fixtures/` sha256-verified
unchanged before and after every run (4 files). All app probes ran against `tempfile.mkdtemp()`.

---

## Claims I reproduced, independently — all TRUE

| Claim | Method | Result |
|---|---|---|
| fast `712 passed, 17 deselected` | `python -m pytest -q` | ✓ `712 passed, 17 deselected in 56.64s` |
| slow `17 passed` | `pytest -q -m slow` | ✓ `17 passed, 712 deselected in 23.13s` |
| ruff `mapper/ tests/` = 28 | `ruff check` | ✓ `Found 28 errors.` |
| ruff `fixtures/` clean | `ruff check fixtures/` | ✓ `All checks passed!` |
| Ledger `712 = 694 − 0 + 18` | detached worktree at `4eaba35`, collected-node-id `comm` diff | ✓ **exact**: base 694, now 712, **0 removed**, +18 = `test_a3_census` 12, `test_layered` 3, `test_app` 1, `test_repair_artifact_claims` **2 derived `[state.py]` arms** |
| **Threshold 4 — no digest re-baselined** | `git diff 4eaba35 -- tests/test_repair_depth.py` | ✓ **zero change** in the `MASTER_LEGACY_DIGESTS` literal; all 12 strings byte-identical. The earlier `sed` offset was a 1-line import shift, not an edit |
| Digests still match what renderers produce | `pytest -k c53_legacy` | ✓ `12 passed` |
| **`with_header` was dead** | `git grep -n with_header 4eaba35 -- .` over the whole tracked tree | ✓ **exactly 2 code hits at baseline**: `layered.py:138` (decl), `:182` (use). **Zero call sites** in `mapper/` or `tests/`. Removal is correct; header body is unchanged apart from dedent |
| `w` removable from `Hybrid`/`Outline` unpack | AST name-set over both `render` bodies | ✓ neither body references `w`. Safe |
| The migration itself is complete | AST census, re-derived | ✓ **all** arg-ful `.render` sites are 2-positional new shape; **0** old-shape keywords; **0** `**` splat; **0** ≥3-positional |
| `query` as a transitional field | judged against `LLR-N07.2.3`'s roster + `#D6`/`R-014` | ✓ **correct call** — see "On `query`" below |

**Threshold 1 / 2 / 3 all genuinely hold on the product.** The A3 landed. My objections below are
about what the *gate* can see, one undeclared behaviour change, and one published false number — not
about the migration being incomplete.

---

## Findings

### H1 — The inverted map-truth guard is vacuous: it passes on the exact regression it names, and it replaced a working assertion  [Severity: HIGH]

- **Where:** `tests/test_repair_map_truth.py:155`
- **What:** The guard rewritten in this increment reads

  ```python
  assert "COMMITTED, NOT PRESENT" not in text.split("state.py")[1][:400]
  ```

  `text.split("state.py")[1]` splits on the **first** occurrence of `state.py` in
  `docs/ARCHITECTURE.md`. Measured: that first occurrence is at **char 1836, line 28** — inside the
  file's prose preamble ("*the ARQ proposal declared `mapper/views/state.py` "new this batch"…*"),
  **131 lines before** the `ViewState` row at `:159`. The 400-char window therefore inspects the
  preamble and never reaches the row.

- **Proof it repairs nothing** — I ran the new assertion against the **baseline**
  `docs/ARCHITECTURE.md` at `4eaba35`, i.e. the exact state the docstring says it now forbids
  ("*it now asserts the row is NOT still marked as a forward commitment*"):

  ```
  --- BASELINE 4eaba35 (row still COMMITTED, NOT PRESENT) <-- the regression ---
    first 'state.py' at char 1836
    'COMMITTED, NOT PRESENT' present anywhere in doc? True
    ... inside the 400-char window after first 'state.py'? False
    GUARD VERDICT: PASSES (does not catch it)
    marker at char 21615; marker is AFTER the split point
  ```

- **Why it matters:** This is a net **loss** of coverage disguised as a discharge. The guard at
  `4eaba35` was live and load-bearing — `assert not (REPO/"mapper"/"views"/"state.py").exists()` is
  what would have fired the moment `state.py` landed, and it is what forced the promotion. The
  increment deleted a working assertion and installed one that cannot fail, while the docstring
  claims it is "kept and INVERTED rather than deleted". `docs/ARCHITECTURE.md` is declared in-tree as
  "the oracle the A-family triggers read", so a dead guard on it is exactly the `C-44` class this
  batch exists to prevent. The §8 battery never probed it: there is no mutant for this guard, which
  is why it passed a FULL protocol.
- **Suggested fix** — anchor on the row, not on a global split:

  ```python
  row = next(l for l in text.splitlines() if l.startswith("| **`ViewState` parameter object**"))
  assert "COMMITTED, NOT PRESENT" not in row, (...)
  assert "PRESENT" in row
  ```

  and add the missing mutant (`revert the row to COMMITTED, NOT PRESENT` → must go RED) to the
  battery before re-claiming the discharge.

---

### H2 — The export site now leaks live keyboard focus into exported SVGs: a second, undeclared behaviour change with zero coverage  [Severity: HIGH]

- **Where:** `mapper/app.py:1770-1773` (export) consuming `mapper/app.py:1376-1382` (`_view_state`,
  which sets `focus_owner=self._focus_owner()`)
- **What:** §1 and §6 (`B-50`) declare **one** behaviour change at the export site — that `diff` is
  now carried. But `_view_state()` also carries `focus_owner`, which the export path never had. An
  exported SVG's selected-node tone now depends on where the keyboard happened to be at the instant
  the operator pressed the export key.
- **Measured**, live app, `tempfile.mkdtemp()` workspace, freshly-opened `MapScreen`:

  ```
  app.focused id : map-rail
  _view_state() -> focus_owner = 'rail'

  selection style in export AFTER Inc-2 : #f5f5f5 on #262626
  selection style in export BEFORE Inc-2: bold #000000 on #1783ff
  EXPORTED SELECTION TONE CHANGED BY INC-2: True
  ```

  The rail holds focus on mount (verified), so this is the **default** path, not a corner case: a
  routine export now writes the *inactive* tone for the node that is in fact the selection.
- **Why it matters:** An exported SVG is a standalone artifact; "which screen region owns the
  keyboard" is meaningless inside it, and `B-05`'s fix has no business reaching it. Three separate
  controls miss it: the byte-identity digests call renderers directly with a default `ViewState`;
  the `AT-009` export tests construct `ViewState` by hand rather than through `_view_state()`; and
  §6 enumerates the increment's deviations and this one is absent. An increment whose central claim
  is "behaviour-neutral except one declared change" shipped a second one that its own gate cannot
  see — the precise failure mode the A3 ceremony exists to catch.
- **Suggested fix** — export is not a focus-bearing surface, so pin it explicitly:

  ```python
  # An export is a standalone artifact: it must not encode where the keyboard
  # happened to be.  `focus_owner=""` is the tone the canvas paints when focused.
  state = dataclasses.replace(
      self._view_state(max(20, size.width), max(5, size.height - 10)), focus_owner="")
  text = renderer.render(self.graph, state)
  ```

  plus one arm in `tests/test_export.py` asserting the exported selection tone is independent of
  `focus_owner` — which is the assertion that would have caught this.

---

### H3 — "27 arg-ful call sites" is false; the executed figure is 32, and it is published into the module map  [Severity: HIGH]

- **Where:** `docs/ARCHITECTURE.md:159`; `increment-002.md` §1, §4 (census table, threshold 3)
- **What:** Re-derived with the census's own instrument and its own `tracked()` glob set:

  ```
  === CALL SITES === argful=32 zeroarg=25
  ```

  `zeroarg=25` matches. `argful` is **32**, not 27. All 32 are genuine map-renderer calls and all 32
  are correctly migrated — the *migration* is right; the *number* is wrong.
- **Provenance of the error, derived:** `tests/test_layered.py` gained 5 new arg-ful call sites in
  this increment (`:62, :64, :83, :84, :98` — the `AT-010` focus-tone arms). `32 − 5 = 27`. The
  figure was measured **before** the author wrote their own new tests and was then published as the
  post-state fact.
- **Why it matters:** This is the Inc-1 failure class repeating — a stale measurement asserted as a
  current fact — and this time it is written into `docs/ARCHITECTURE.md`, the artifact this repo
  treats as an oracle and guards with `test_repair_map_truth.py` and
  `test_repair_artifact_claims.py`. It is **unfalsifiable by the suite**: no test pins the
  cardinality. The codebase already has the correct convention for exactly this —
  `tests/test_darkside_census.py:279` (`assert len(sites) == 36`) and `:302` — and the new census
  departed from it, asserting only non-emptiness (`test_a3_census.py:70`).
- **Suggested fix:** correct both figures to **32**, and pin them so they cannot rot:

  ```python
  def test_llr_n07_2_2a_the_census_cardinality_is_pinned():
      sites = render_call_sites()
      assert len(sites["argful"]) == 32, f"derived {len(sites['argful'])}, map says 32"
      assert len(sites["zeroarg"]) == 25
  ```

  Also correct "6 render definitions" (see L1).

---

### M1 — The flaky focus test is NOT fixed; it is load-sensitive and still fails  [Severity: MEDIUM]

- **Where:** `tests/test_app.py:150-162`
- **What:** §8 claims "*Verified stable across 8 consecutive runs.*" Measured over **62 runs**:

  | Condition | Runs | Failures |
  |---|---:|---:|
  | idle machine | 32 | **0** |
  | concurrent load (6-way parallel pytest, and one overlapping probe) | 30 | **3** (~10%) |

  Failing runs take **1.51-1.56 s** against **0.75-0.84 s** for passing ones — the failure tracks
  wall-clock contention, not order. The failing assertion is the author's own new guard:

  ```
  >   assert app.focused is not None, "no widget ever took focus on MapScreen"
  E   AssertionError: no widget ever took focus on MapScreen
  tests\test_app.py:162: AssertionError
  ```

- **Why it matters:** Answering the question directly — **it is merely less flaky, not stable.** The
  bound is on *iterations* (`for _ in range(50)`), not on *wall-clock*. `pilot.pause()` yields the
  event loop once; under contention 50 yields can elapse in far less real time than the app needs to
  mount and focus, so the bound does not do the job the comment says it does. The author's 8-run
  verification was performed on an idle machine and does not establish the property. CI under load
  will hit this.
- **Suggested fix** — bound in time, not in yields:

  ```python
  import time
  deadline = time.monotonic() + 5.0
  while app.focused is None and time.monotonic() < deadline:
      await pilot.pause()
      await asyncio.sleep(0.01)
  assert app.focused is not None, "no widget took focus on MapScreen within 5s"
  ```

---

### M2 — The `LLR-CNV.3.1` acceptance test does not verify the requirement's threshold, and passes because focus is *lost*  [Severity: MEDIUM]

- **Where:** `tests/test_app.py:170-172`
- **What:** `LLR-CNV.3.1`'s numeric pass threshold is explicit: *"after 1 real `tab` press from the
  canvas, the field reads `"rail"`; after 2, `"inspector"`"* (pre-state `M-10`). The test asserts
  something strictly weaker: `all(owner in FOCUS_OWNERS)` and `len(set(seen)) > 1`.
- **Measured** by reproducing the test body verbatim, 4 independent runs, deterministic:

  ```
  seen=['rail', '', '', '', '']
  focused ids=['map-rail', None, None, None, None]
  test's assertions: domain=True changed=True -> TEST PASS
  LLR-CNV.3.1 threshold (press1=='rail' and press2=='inspector'): False
  ```

- **Why it matters:** `seen[0]` is sampled **before** any key press and is the only non-empty value;
  `app.focused` goes to `None` on the first real `tab` and never returns. So the four `pilot.press("tab")`
  calls contribute **no positive evidence at all** — the test passes because focus is *lost*,
  which satisfies `len(set(seen)) > 1` via the degenerate transition `rail → unknown`. The docstring's
  own standard ("*Driven with the REAL `tab` key… a proxy that bypasses the real mechanism would
  verify the proxy*") is not met: the real mechanism is exercised and produces nothing, and the
  assertion is loose enough not to notice. `M-FOCUSWIRE` (constant owner) going RED is consistent
  with this — a constant fails `len(set)>1` too — so the battery does not distinguish the two.
  Note also `all(owner in FOCUS_OWNERS)` is near-tautological: `_focus_owner()` can only return
  `""` or a `_FOCUS_REGIONS` value by construction. Its real (and worthwhile) job is catching drift
  between `_FOCUS_REGIONS` and `FOCUS_OWNERS`.
- **Suggested fix:** assert the declared transition and treat focus loss as a failure, not as
  evidence:

  ```python
  assert seen[0] == "rail"                       # rail holds focus on mount (measured)
  assert "inspector" in seen[1:], f"tab never reached the inspector: {seen}"
  assert "" not in seen[1:], f"focus was LOST rather than moved: {focused_ids}"
  ```

  If that arm goes red — and on today's tree it will — the underlying tab-chain behaviour is a real
  defect worth a `B-` carry, and `M-10`'s recorded pre-state no longer reproduces. Route to
  `qa-reviewer`; it is a coverage/behaviour question, not a code-quality one.

---

### M3 — Threshold 3 is not total: blind to `**` splat, to ≥3 positional arguments, and to untracked files  [Severity: MEDIUM]

- **Where:** `tests/test_a3_census.py:128-143` (threshold 3), `:27-30` (`tracked()`), `:37-44`
  (`render_definitions`)
- **What:** Three escape routes, each verified to be *currently empty* but none of them closed:
  1. **`**kwargs` splat.** `{k.arg for k in node.keywords}` yields `{None}` for `render(g, **opts)`;
     the intersection with `old_shape` is empty, so it is not an offender. Measured today: **0 splat
     sites** — but the §4 claim "`**kwargs` = 0" at call sites is a *measurement*, not an *assertion*.
  2. **Positional old shape.** `render(g, sel, w, h)` carries no keywords, so threshold 3 sees
     nothing. Measured today: **0 sites with ≥3 positional args**.
  3. **Untracked files — the sharp one.** `tracked()` is `git ls-files`, which lists only tracked
     paths. My probe found exactly one `.py` file under `mapper/`+`tests/` that the census cannot
     see: **`tests/test_a3_census.py` itself.** The increment's own new test file is invisible to
     its own census. More seriously, `render_definitions()` uses `tracked("mapper/views/*.py")`, so
     **a new renderer file that has not been `git add`ed escapes threshold 1 entirely.** That the
     census works at all today depends on `state.py` having been staged — an undocumented,
     load-bearing precondition.

  Also `render_definitions()` matches `ast.FunctionDef` only; an `async def render` is invisible.
- **Why it matters:** The gate's stated property is "*zero call sites of the old shape survive*".
  As implemented it is "zero call sites pass an old-shape **keyword**, among **tracked** files".
  Threshold 1 makes any surviving old-shape call a `TypeError` *if executed* — so the residual risk
  is confined to unexecuted call sites and to new/unstaged files, which is precisely where a census
  is supposed to be the safety net.
- **Suggested fix:**

  ```python
  # in threshold 3
  and ({k.arg for k in node.keywords} & old_shape
       or any(k.arg is None for k in node.keywords)      # **splat: unauditable, ban it
       or len(node.args) > 2)                            # positional old shape
  ```

  and make `tracked()` fail loud on drift rather than silently under-sweeping:

  ```python
  seen = set(tracked(...))
  on_disk = {p.relative_to(REPO).as_posix() for p in (REPO/"mapper").rglob("*.py")}
  assert on_disk <= seen, f"untracked source invisible to the census: {sorted(on_disk - seen)}"
  ```

  and add `ast.AsyncFunctionDef` to `render_definitions()`.

---

### M4 — `len(zeroarg) >= 20` is a floor, in the one requirement that abolished floors  [Severity: MEDIUM]

- **Where:** `tests/test_a3_census.py:153`
- **What:** `LLR-N07.2.2a` states its thresholds as "**SET EQUALITY** on both sides of the protocol,
  **never a floor** (`P2-C6`, `QA2-C-02`, §6.5 `A-52`)", and `A-32`'s argument is quoted at length in
  the requirement. This arm asserts `>= 20` against an actual **25**, so five Textual `Widget.render()`
  sites could be wrongly migrated and the arm stays green — the same "comfortably above a floor while
  being wrong" shape `A-32` abolished, with the sign flipped.
- **Why it matters:** Convention/requirement conformance, and it is the *only* guard on the
  false-failure side of the split.
- **Suggested fix:** `assert len(zeroarg) == 25` (with the count pinned as in H3), so a wrongly-swept
  widget site is a red arm rather than slack.

---

### M5 — The frozen-ness test can pass for the wrong reason  [Severity: MEDIUM]

- **Where:** `tests/test_a3_census.py:205-207`

  ```python
  def test_llr_n07_2_3_view_state_is_frozen():
      with pytest.raises(Exception):
          ViewState().selected_id = "x"
  ```

- **What:** `ViewState()` is *constructed inside* the `pytest.raises` block. Make any field required
  and the `TypeError` from construction satisfies the assertion — the test goes green while proving
  nothing about frozen-ness. `Exception` is also broader than the property.
- **Why it matters:** Answering the question directly — **frozen and all-defaulted ARE genuinely
  enforced**, not merely asserted: `test_llr_n07_2_3_view_state_constructs_with_no_arguments:197-202`
  derives `without_default` from `dataclasses.fields` and asserts it empty, which is real and
  discriminating, and it independently reddens `M-N07.2.3-b`. So the roster property holds. This
  finding is that *this particular arm* is not the guard it looks like.
- **Suggested fix:**

  ```python
  state = ViewState()                      # outside the raises block
  with pytest.raises(dataclasses.FrozenInstanceError):
      state.selected_id = "x"
  ```

---

### M6 — `("#map-canvas", "canvas")` is an unreachable branch: the canvas cannot take focus  [Severity: MEDIUM]

- **Where:** `mapper/app.py:1346`
- **Measured**, live app: `#map-canvas exists. can_focus = False`. Enumerating every focusable
  widget on `MapScreen` and mapping each through `_focus_owner()`:

  ```
  map-rail        OutlineRail    -> 'rail'
  insp-title      FieldInput     -> 'inspector'
  insp-state      DsSegmented    -> 'inspector'
  insp-notes      FieldInput     -> 'inspector'
  search-input    Input          -> 'inspector'
  ```

  `"canvas"` is **never** produced by the real wiring. The full-strength tone is reached only via the
  `""` fallback.
- **Why it matters:** `test_at_010_every_declared_focus_owner_is_accepted` exercises `"canvas"`
  synthetically and therefore reports a domain that the app cannot generate, and
  `test_at_010_an_unknown_focus_owner_paints_what_the_tree_painted_before` pins `"" == "canvas"`,
  which makes the dead branch invisible. Not a bug today — `HLR-CNV.3`'s substance (the canvas dims
  when rail/inspector owns the keyboard) does hold — but the declared value domain overstates the
  mechanism, and a future reader will assume `"canvas"` is live.
- **Suggested fix:** keep the entry (it is correct if the canvas ever becomes focusable) and record
  the measurement in the docstring at `mapper/app.py:1355`: *"`#map-canvas` is `can_focus=False`
  today, so `"canvas"` is currently unreachable and the focused tone is reached through `""`."*
  Alternatively raise a carry to make the canvas focusable, which is what `B-05`'s three-region
  framing implies.

---

### L1 — `render_definitions()` derives **7**, not 6  [Severity: LOW]

`mapper/views/state.py:86` — `IRenderer.render` — lives in `mapper/views/*.py` and is swept in:

```
=== DEFINITIONS in mapper/views (incl async) === 7
  lane.py:109 / :166 / :300, layered.py:131, outline.py:48, radial.py:108, state.py:86
```

All 7 are `(self, graph, state)`, so threshold 1 passes and is arguably *stronger* this way. But §4
and `docs/ARCHITECTURE.md:159` both say "**6**", and `renderer_classes()` (which correctly excludes
the Protocol via `_is_protocol`, `:180`) returns 6. Two derivations of "the definition set" disagree
by one member and the doc quotes the smaller. **Fix:** state 7 (or exclude the Protocol in
`render_definitions()` too, and say 6) — pick one and make both derivations agree.

### L2 — Fake CSS selectors compared as strings  [Severity: LOW]

`mapper/app.py:1362`: `if f"#{getattr(node, 'id', None)}" == selector:` synthesises a `#`-prefixed
string purely to compare against another string that only looks like a selector. Nothing here is a
selector — it is an id equality test with a decorative prefix, and it silently compares `"#None"` for
unnamed widgets. **Fix:** store bare ids in `_FOCUS_REGIONS` and write `if getattr(node, "id", None) == name:`.

### L3 — `FOCUS_OWNERS` is production-dead; the domain is duplicated  [Severity: LOW]

`mapper/views/state.py:40` declares the value domain, but the only production reference is a
*docstring mention* at `mapper/app.py:1350`. `_FOCUS_REGIONS` (`:1343-1347`) re-types the same domain
independently. Only `tests/test_app.py:170` links them. **Fix:** derive the owner names from
`FOCUS_OWNERS` in `app.py`, or assert `{o for _, o in _FOCUS_REGIONS} <= set(FOCUS_OWNERS)` in the
census so the two rosters cannot drift.

### L4 — A modal screen makes the canvas paint the *focused* tone  [Severity: LOW]

Measured: with `HelpScreen` pushed, `app.focused = help-bindings/VerticalScroll` and
`MapScreen._focus_owner()` returns `""` → full-strength selection, while the canvas region
demonstrably does not hold the keyboard. Strictly this contradicts `HLR-CNV.3`'s statement. The
canvas is occluded by the modal, so there is no visible harm today, and the `""`-paints-focused
conflation is the deliberate, documented price of byte identity (`state.py:37-40`). Recording it as a
known edge rather than asking for a change.

---

## On the two judgement calls you asked me to make

**`query` as a transitional field — this is the right call, keep it.** `#D6`/`R-014` says renderers
must receive resolved id sets, and `query` is a predicate. But `LLR-N07.2.3`'s roster paragraph
assigns `hits` to **Inc-4** by name, and the roster it *does* enumerate for Inc-2 is
`focus_owner` only — the rest of `ViewState` is a faithful carry of parameters that already existed on
`layered.py:131`. Dropping `query` now would delete the layered search highlight inside an increment
gated on byte identity; inventing `hits` now would land the resolution question (`P-18`: two live
definitions of "what matches") without its owner. Carrying it, flagged **TRANSITIONAL** in code
(`state.py:66-69`), in §5.1, and in the module map, is the option that keeps the debt visible. The
supporting fact is also true and worth keeping: §5.2's "zero coverage on the search surface" is
confirmed — no test anywhere passes a non-default `query`, which is exactly why the carry is safe.

**`frozen=True` + all-defaults are enforced, not merely asserted** — via
`dataclasses.fields`/`without_default == []` at `test_a3_census.py:197-202`. See **M5** for the one
arm that is weaker than it looks.

---

## Evidence checklist

- [✓] **Diff read in full** — `git diff 4eaba35 -- mapper/ tests/ docs/` (922 lines) plus staged
      `mapper/views/state.py:1-88` and untracked `tests/test_a3_census.py:1-291`, read entire.
- [✓] **Correctness pass (edge / None / error paths)** — `_focus_owner()` walked against every
      focusable widget on `MapScreen`, against `app.focused is None`, and against a pushed modal
      screen; export path traced end to end (**H2**).
- [✓] **Simplicity pass** — no premature abstraction found; `_view_state()` is the right shape and
      the six-file breach is correctly argued in §2. Nits only: **L2**, **L3**.
- [✓] **Reuse / duplication checked** — `_FOCUS_REGIONS` vs `FOCUS_OWNERS` (**L3**);
      `render_definitions()` vs `renderer_classes()` (**L1**); census cardinality vs the repo's own
      established convention at `test_darkside_census.py:279` (**H3**).
- [✓] **Tests reviewed for intent** — **H1**, **M1**, **M2**, **M3**, **M4**, **M5** are all
      test-intent findings; the ledger, the digests and the `with_header` census were re-derived
      rather than accepted.
- [✓] **Verdict explicit** — below.

---

## Verdict

- [ ] OK to advance
- [ ] OK with the listed fixes applied first
- [x] **Block — must fix HIGH findings before advancing**

**The A3 itself is sound and I want that on the record:** all six renderer definitions and all 32
call sites carry the new shape, no old shape survives, `**kwargs` is gone, `with_header` was genuinely
dead and its removal is behaviour-preserving, the twelve byte-identity digests are untouched and still
match, and the test ledger reconciles to the node id. That is a clean, complete migration and the
hardest part of the batch.

It is blocked on three things that the increment's own gate could not see:

1. **H1** — a guard rewritten in this increment cannot fail for the reason it names, and it replaced
   one that could. Proven against the baseline document.
2. **H2** — a second, undeclared behaviour change: exported SVGs now encode transient keyboard focus,
   measured on the default path, with no test covering it.
3. **H3** — a false measurement (`27` for `32`) published into `docs/ARCHITECTURE.md`, unfalsifiable
   by the suite, and departing from the repo's own count-pinning convention.

H1 and H3 are the Inc-1 failure classes recurring — a "fix" that repairs nothing, and a stale
measurement asserted as fact. All three fixes are small and local; none of them requires re-opening
the migration.

**Recommended before re-review:** apply H1/H2/H3; add the two missing mutants (the map-row regression,
and export tone independent of `focus_owner`) so the battery covers what it missed; then apply M1-M5.
**M2** should additionally be routed to `qa-reviewer` — the measured `seen=['rail','','','','']` says
the real tab chain loses focus on `MapScreen`, which is a behaviour question beyond this increment's
scope and invalidates the `M-10` pre-state recorded in `LLR-CNV.3.1`.
