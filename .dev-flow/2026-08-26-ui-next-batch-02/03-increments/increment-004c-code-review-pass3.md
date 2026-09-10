# Increment 4c — code review, pass 3 (narrow confirmation) · **VERDICT: PASS**

**Date:** 2026-08-29 · **Branch:** `feat/ui-next-batch-02` · **Entry:** `9ba2f26` · nothing committed.
**Conducted by:** a fresh `code-reviewer`, third pass, scoped by coordinator ruling to `H1-R` and `F-B` only.

## BLUF

**No HIGH survives on either in-scope item. `Inc-4c` may commit.**

* **`H1-R` is CLOSED.** The round-2 escape was rebuilt from scratch and the census arm goes RED naming
  both the helper and the attribute. The two-plane / two-edge-kind closure does what R3F.1 claims.
* **`F-B` is CLOSED.** The truncation mutant goes RED on the new tail assertion. It is not a general
  truncation detector, and the record should say so rather than imply otherwise.
* The fix's own **boundary statement is materially accurate** — three of the four clauses I constructed
  behave exactly as declared. One clause **understates** (it claims blindness where the derivation in
  fact sees). Understating errs safe, so it is a MEDIUM, not a blocker.
* **Two of the declared blind spots are this file's existing idiom, not hypotheticals.** That is the
  finding most worth carrying forward, and it sharpens where the sixth instance should be hunted.

Everything below rests on arms I fired myself on a byte-verified mirror. Nothing rests on reading the
round-2 or round-3 transcript.

## State verified before any claim

```
branch feat/ui-next-batch-02      HEAD 9ba2f26139cc6bf32853bef63e2a6bb5d97e2110      core.autocrlf=true
sha256 mapper/app.py        c0709eabb0453d3263e9fc80a4131c5393fd9a6e608a17569086972c79e4f21a   MATCHES declared
sha256 tests/test_search.py 6a7e736a4e7b1a22dc1a0dfe55e2da20facc5c6d94c1be5813a864244a0298fa   MATCHES declared
```

Mirror built by byte-preserving copy (not `clone`, not `archive`), **91/91 copied tracked files verified
byte-for-byte against source, 0 diverged**, re-verified after a bytecode purge and again before the last
arm. All mutation I/O in binary; every restore asserted byte-identical by sha256. Arms fired one at a
time, one writer. `PYTHONUTF8=1` throughout. **The repo tree was never written to** — final `git status`
and both digests are unchanged from entry.

## `H1-R` — the derived ban · **CLOSED**

### The escape it claims to kill, rebuilt independently

`MUT-A` — a module-level `_visible_matches(screen, ids)` reading the fold state, with
`_whole_graph_tally` routed through it. This is the round-2 mutant reconstructed from the description,
not copied from the transcript.

```
VERDICT: RED
  reddened: test_the_count_and_the_paint_share_one_resolution   tests/test_search.py:835
  AssertionError: `_visible_matches` is in the count chain and reads ['folded']
  applied 700063714bf3   restored c0709eabb045 (byte-identical)
```

The applied digest reproduces R3F.1's stated `70006371…` independently. **The fix kills the escape it
claims to kill, and names both the offending callable and the attribute.**

Derivation measured on the shipped tree: **reached = 9** methods (`_count_line`, `_query_echo`,
`_search_hits`, `_search_index`, `_search_order`, `_seat_glyph`, `_seat_row`, `_suspended_count_line`,
`_whole_graph_tally`), **zero leaks**, 96 callables in the map, helper plane = exactly 3. This confirms
`F-D` (both owners seed one closure) and R3F.2's `C-55` premise: none of the 3 module-level helpers is
in the chain, so the crossing genuinely is a no-op today.

### Is the boundary statement honest? — four clauses constructed

| Arm | Clause under test | Declared | Measured | Statement |
|---|---|---|---|---|
| `MUT-B` | a **bound-method reference** | NOT seen | **RED** — `_narrow_by_fold` named | **understates** |
| `MUT-D` | attribute reached by **`getattr`** | NOT seen | **GREEN** | accurate |
| `MUT-C2` | viewport passed as a plain **ARGUMENT** | NOT seen | **GREEN** | accurate |
| `MUT-J` | helper in **another module** | NOT seen | **GREEN** | accurate |

`MUT-B` is the one correction. A bound-method reference (`_f = self._narrow_by_fold`) is a *dotted
attribute read*, which is precisely the edge kind the closure advances on — so it is caught, and the
docstring should not list it as a blind spot. The neighbouring items in that same clause (dispatch
through a variable holding a *bare* helper name, or through a dict of callables) genuinely are blind;
only the "bound-method reference" wording is wrong.

`MUT-C2` was built honestly on the second attempt: my first version put the fold read inside
`_query_echo`, which **is** in the reached set, so it reddened for the wrong reason. Rebuilt with the
read in the *unreached caller* (`text.append(self._count_line(self.folded))` at the strip call site) and
the value threaded in as a plain parameter, no reached method containing a `self.folded` read at all:
**GREEN, and the whole of `tests/test_search.py` stayed green at 37 passed.**

`MUT-J` added a function to `mapper/darkside.py` reading `screen.folded`, called from
`_whole_graph_tally`: **GREEN, 37 passed.**

### The finding that matters — two blind spots are the file's existing idiom

The boundary statement is honest, but it reads as a list of exotic shapes. Two of them are not exotic:

* **viewport as a plain argument** — already written in this file:
  `mapper/app.py:1516-1517` and `:1535-1536` do `self._clamp_pan(self.pan_x, extent_x, span_x)`. A
  viewport value read in the caller and handed to a method as a positional argument is the file's own
  established habit, not a shape a future author would have to invent.
* **a helper in another module** — the count chain **already crosses that boundary today**:
  `_query_echo` is in the reached set and calls `darkside.fit(...)` and reads
  `darkside.PRESERVED_CODE_POINTS` (`mapper/app.py:1880-1883`). `app.py` makes 11 cross-module
  module-level calls and `from . import darkside` is idiomatic here.

Also worth recording: only `MapScreen` is walked, but `app.py` defines **12 classes**. "A method
resolved on a different class" covers the other 11, including `NavigationModel`, which the chain
already consumes.

**Assessment.** If there is a sixth instance, these are where it comes from — in descending order:
another module, then a plain argument, then another class. `getattr`/subscript is the least likely,
because nothing in this file reaches attributes that way. None of this is a blocker: the shapes are
*declared*, which is what the coordinator asked the docstring to do, and closing them would mean
whole-program analysis rather than one module's AST. The value is in aiming the next hunt correctly.

### Supporting checks

* **The `VIEWPORT` anchor is real (`F-C`).** `MUT-H` renamed the attribute throughout `app.py`:
  **RED** at `tests/test_search.py:792` — *"VIEWPORT ('folded', 'pan_x', 'pan_y') is stale against
  `_view_state` … the ban below is vacuous"*. Not a vacuous input set.
* **The non-vacuity floor (`F-F`).** `tests/test_search.py:829-831` is correctly described now: the
  transitive receipt (`reached - SEEDS - reads["_count_line"]`) **is** derived; `len(reached) >= 6` and
  the two-name pin are a **PIN**. The corrected sentence at `:825-828` says exactly that. `F-F` closed.

## `F-B` — coercion vs truncation · **CLOSED, with its scope stated**

| Arm | Operation | Verdict |
|---|---|---|
| `MUT-E` | echo cut at the first coerced point (the F-B mutant) | **RED** at `tests/test_search.py:1142` |
| `MUT-F` | echo drops only its **last** character | **RED** at `:1142` |
| `MUT-G` | head and tail both kept, the **middle** silently elided, no ellipsis | GREEN |

`MUT-E` reddens on the new `assert "abc" in painted` — the truncation mutant is dead. The tail token is
discriminating: neither `abc` nor `zeta` occurs anywhere else in the painted region, so both assertions
have their declared subject in their expression (`C-40`).

**Does it separate coercion from truncation in general? No — and the record should not imply it does.**
The arm is a **two-anchor containment**: it catches any truncation that reaches the head or the tail
(`MUT-E`, `MUT-F`), and is blind to an elision confined strictly *between* the anchors (`MUT-G`).

On this fixture that residue is benign: the query is head + hostile run + tail, so the only interior
span is the hostile run itself, and removing it rather than replacing it is a defensible coercion
strategy. So `MUT-G` is **not** a defect — it is the honest limit of the arm. Recommended wording: the
arm separates coercion from truncation *at the echo's boundaries*, which is where the demonstrated
defect lived.

## Out-of-scope findings — reported, NOT blockers

Per the coordinator's ruling: surfaced, not looped.

### O-1 (MEDIUM) — the crossing arm's negative control does no work on the reachability axis

`MUT-I` broke the derivation so **every** module-level helper is marked reached regardless of edges
(`reached = {...} | set(helpers)` in `_count_chain`). `test_the_count_chain_closure_crosses_the_class_boundary`
**stayed GREEN**.

Both controls assert `"_visible_matches" in reached` *positively*, so neither can see over-reach on
reachability; they discriminate only on the **read** axis (`folded` vs `graph`). R3F.2's sentence — *"so
the arm discriminates instead of flagging every helper"* — is therefore not backed as written.

The over-reach direction is *safe* (it yields false positives, never a hidden lie), which is why this is
MEDIUM and not a blocker. Minimal fix: add a third control whose helper is **not** reachable from the
seed and assert `"_orphan" not in reached`.

### O-2 (MEDIUM) — a mirror-fidelity trap that R3F.7's control does NOT catch

R3F.7 requires byte-for-byte verification. **That is necessary and not sufficient, and it bit this
review.** Two independent mechanisms:

1. **The repo is pip-installed editable.** `_editable_impl_mapper.pth` in site-packages puts
   `C:\Users\jjgh8\Github\mapper` permanently on `sys.path`, and `tests/` is a **package**
   (`tests/__init__.py`). A mirror run guarded only on `mapper.__file__` — the guard constraint 4 asks
   for — happily executes the **repo's** `tests/test_search.py` against the **mirror's** source. My
   first `MUT-A` run did exactly that.
2. **`cp -r` copies `__pycache__`.** The reused `.pyc` carries the repo's baked-in `co_filename`, so
   tracebacks name repo paths even when the mirror module is the one executing.

In both cases **the bytes are identical**, so R3F.7's whole-tree digest check passes and detects
nothing. **Control to add:** assert the resolved `__file__` of the *test module* as well as of `mapper`,
and purge `__pycache__` / `.pytest_cache` from every mirror before firing. I re-fired the entire `H1-R`
battery after fixing both; all verdicts were unchanged, and the reported paths became mirror-relative.

### O-3 (LOW) — `len(helper_plane) >= 3` sits exactly on today's value

`app.py` has exactly three module-level defs (`screen_bindings`, `keybar_groups`, `main`), so the floor
at `tests/test_search.py:816` is tight: deleting any one of them reddens the census arm for a reason
unrelated to the property it guards. Suggest `>= 1` with the intent in the message, or derive the floor.

## What I could NOT verify — stated explicitly

1. **The suite ledger `854 passed, 17 deselected, 3 xfailed` and the `+1` delta.** My mirror was scoped
   to source and tests (91 of 236 tracked files) and omits `.dev-flow/`, `prototypes/` and the handoff
   documents. The default lane on that mirror reports **46 failed, 792 passed** — every failure in
   `test_inc3_census.py`, `test_repair_artifact_claims.py` or `test_repair_golden_census.py`, all of
   which read the `.dev-flow` corpus the mirror does not contain. **These are mirror-scope artifacts,
   not defects**, but they mean I did not independently reproduce the declared figures. I did not run
   the suite in the repo, because that writes caches into a tree I was told to leave read-only and
   would have been a second writer.
2. **R3F.4's `+1` specifically**, since the round-2 tree is not preserved anywhere I can reach. For the
   record, `git diff HEAD -- tests/test_search.py` over the whole increment shows **+5 / -1** test
   functions, which is the increment's net, not round 3's.
3. **The ruff SET claim** (base 27 / work 27) — not re-run; out of scope for this pass.
4. **That `MUT-C2` produces an operator-visible wrong number.** Structurally the ban is blind to it and
   37/37 arms pass, which is what the finding rests on. My behavioural probe called `_count_line()`
   directly and took the default argument, so it showed 12002 either way; the lying path is the strip
   call site, which the unit harness bypasses. I did not build a composited-frame probe for it.
5. **Anything outside `H1-R` and `F-B`** — H2, S1/S1b, R2-E, R2-G, F-C beyond its anchor, F-D beyond the
   9-method measurement, F-E, F-F beyond its corrected sentence. Confirmed by the prior pass; not re-run.

## Evidence checklist

- [x] **Diff read in full** — `tests/test_search.py:545-903` (`_app_source`, `_count_chain`, the crossing
      arm, the census arm) and `:1086-1142` (the coercion arm); `mapper/app.py:1759-1883`.
- [x] **Correctness pass** — 9 mutants fired; edge/None/error paths of the closure exercised via the
      collide assert, the helper-plane floor and the non-vacuity floor.
- [x] **Simplicity pass** — `_count_chain` is ~45 lines of AST walk with no speculative generality; the
      two-plane split is required by the demonstrated escape, not invented.
- [x] **Reuse / duplication** — `F-D` correctly folds the separate `_search_hits` ban into one closure;
      `F-E` removes the `PRESERVED_CODE_POINTS` duplicate at `mapper/app.py:1881`.
- [x] **Tests reviewed for intent** — `MUT-I` shows one control is weaker than its docstring claims
      (O-1); the `F-B` arm's true scope is stated above.
- [x] **Verdict explicit** — PASS.
- [x] **Repo tree unmodified** — both digests unchanged; `git status` identical to entry; no hostile
      code point spelled verbatim in this file.

## Verdict

**PASS.** `H1-R` and `F-B` are both closed on evidence I generated myself. `Inc-4c` may commit.

Recommended before commit, all one-liners and none blocking: correct the "bound-method reference"
clause in `_count_chain`'s docstring (it is seen), soften the `F-B` claim to "at the echo's boundaries",
and adjust R3F.2's sentence about the negative control. O-1 through O-3 belong in the batch backlog.
