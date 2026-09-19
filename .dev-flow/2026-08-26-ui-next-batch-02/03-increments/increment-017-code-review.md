# Code Review — Increment 017 · `A-100.1` · `A-100.2` · `A-100.3`

| Field | Value |
|---|---|
| Reviewer | `code-reviewer` (independent; authored none of this diff; fresh session) |
| Batch | `2026-08-26-ui-next-batch-02` |
| Commit reviewed | **`046acea`** on `feat/ui-next-batch-02`, base `4800906` |
| Date | 2026-09-19 |
| **Verdict** | **BLOCK — one HIGH open (`CR17-F1`).** The `A-100.1` re-grounding is REFUTED by measurement. 2 MEDIUM + 2 LOW also raised |

> **This verdict authorises nothing by itself.** It is a reviewer's reading, not a gate decision.

---

## 1 · Mirror, digests, and what moved under me

Every mutation and probe ran in **my own mirrors**, never in the repo. The only file I wrote in
`C:\Users\jjgh8\Github\mapper` is this report.

| Mirror | Path | Purpose |
|---|---|---|
| `mirror-cr017` (provisioned) | `…/scratchpad/mirror-cr017` | lanes + the 5-site mutation battery |
| `mirror-cr017b` (mine, created mid-review) | `…/scratchpad/mirror-cr017b` | the stale-claim probe + slow/network lanes, so the battery's tree was never disturbed |

**Digest discipline — every digest HELD.** Aggregate sha256 over all 91 `.py` files in
`mapper/` + `tests/`, sorted, at `046acea`:

| Tree | Aggregate digest |
|---|---|
| repo at `046acea` | `04828ea170c744c82e31b8148f92188fbcbe7724866f0b345b5904f377545a27` |
| `mirror-cr017` | `04828ea1…` **identical** |
| `pyproject.toml` (both) | `2b3ffba9ca51b3f1a16426622f280675e78cacb7dc50969b963fa3cdb89aeebb` |

I re-asserted the aggregate digest after `git init`-ing the mirror and after each support-tree copy —
unchanged each time. All five battery sites restored **byte-identical**, sha256 re-pinned per site.

**Both declared traps were actively defended, not assumed.**

- *Trap 1 (`_editable_impl_mapper.pth` → the repo).* Every ad-hoc probe asserts
  `MIRROR in pathlib.Path(mapper.__file__).resolve().parents` and **prints the resolved path**. All
  probe output shows `…\scratchpad\mirror-cr017\mapper\__init__.py`. No probe read the repo.
- *Trap 2 (stdlib shadowing).* Probe files are named `probe_*.py`; no stdlib name was created in any
  directory I ran from.
- *Line endings.* Verified **byte-level** in the mirror, not by `grep`: `mapper/app.py` CRLF x4145 /
  bare-LF 0; `mapper/export.py`, `tests/test_hermetic.py`, `tests/test_export_state.py` CRLF 0 / LF
  73, 448, 592. The brief's map is correct. (A text-mode `grep` in the repo reported "all CRLF" for
  every file. **I discarded that reading**; anchors were built from the byte-level map, and all five
  matched exactly 1x.)

### ⚠ The tree moved under me mid-review — control 15, again

`git rev-parse HEAD` was `046acea` when I started and **`152ecd9` when I re-checked**. Two commits
landed during this review, and `mapper/app.py` changed (`+30/-2`).

- No evidence of mine was corrupted: every number below was taken in a mirror pinned to `046acea`,
  and I caught the move only because a digest I recomputed disagreed — *asserting hash-stability
  across my own run is what surfaced it*, exactly as control 15's discharge says.
- **The post-review `app.py` change is `SEC-H2`** (`_ConfirmScreen` `markup=False` + `darkside.plain`
  on the title) at lines ~276 and ~3834. **It does not touch the export seam** (3466–3620), so
  `CR17-F1` and `CR17-F2` hold against `152ecd9` as well. I have **not** reviewed `SEC-H2`.
- Recorded because the batch's own control says a violation that lands clean is the one most likely
  to be repeated. Writes to the shared tree continued while an independent review was in flight.

### One provisioning note

The mirror's 91 `.py` files were complete and correct for `046acea`. But `mapper/` + `tests/` +
`pyproject.toml` **cannot run the suite**: collection needs `docs/`, `fixtures/`, `maps/`,
`.dev-flow/` and a git repo (`git ls-files`). I copied those in myself and re-verified the source
digest after each. Worth folding into the mirror recipe.

---

## 2 · Scope reviewed

`git diff 4800906 046acea` **read in full** — 7 files, 650 insertions / 44 deletions.

| File | Lines read |
|---|---|
| `mapper/app.py` | `3480–3519` (the `ExportTooLarge` handler) and `3541–3616` (the `EXPORT_MAX_CELLS` docstring), plus `3466–3520` and `3690–3745` for context |
| `tests/test_export_state.py` | `201–246` (fold params), `366–475` (the two new refusal arms) |
| `tests/test_hermetic.py` | `89–145`, `168–175`, `393–448` |
| `.dev-flow/…/01-requirements.md` | amendment set 9 in full |
| `.dev-flow/state.json`, `increment-017-rulings.md` | the added entries |

I judged the implementation, not the rulings.

---

## 3 · What I reproduced (and what I refuted)

| Claim | My result |
|---|---|
| default lane `1140 passed / 20 deselected / 3 xfailed` | **1138 passed + 2 failed = 1140 total.** The 2 are mirror-provenance, not real: `test_fold::…INCLUDING_the_artifacts` dies on a binary file my own `git add -A` tracked, and `test_app::test_llr_cnv_3_1…` **passes 3/3 standalone** — order-dependent, i.e. carried `FLAKE-1`. Consistent with the claim |
| slow lane `19` | **19 passed** ✓ |
| network lane `1` | **1 passed** ✓ |
| signed balance `1140 = 1133 − 0 + 7` | **the `+7` itemises exactly** against the diff: 2 CJK fold params + 2 refusal arms + 2 census params + 1 census positive control. I did not run the base lane at `4800906` |
| 5-site battery, 4 kills + 1 survivor, granular | **REPRODUCED, all five** — table below |
| `A-100.1`: "nothing the budget admits crosses the target", ≈28 % margin, 0.955–3.27 µs/cell | **REFUTED.** `CR17-F1` |

### Mutation battery — independently reproduced

Byte-level I/O, sha256 pinned pre/post, anchor occurrences asserted **exactly 1** per site, verdict
printed **before** the restore assert, `PYTHONDONTWRITEBYTECODE=1`, full default lane per site.

`test_fold::…INCLUDING_the_artifacts` fails in **all five runs including the control** — it is my
constant mirror artifact, so the *differential* below is clean.

| Site | Mutation | Predicted | KILLED (differential) | Verdict |
|---|---|---|---|---|
| A | `cell_len` → `len` in `save_svg` | only the 2 CJK params | `…folded_in_the_artifact[20-枝 {}]`, `[40-分岐 {}]` — **the four narrow-title params stayed GREEN** | ✓ exact |
| B | stale sentence suppressed (`if False`) | only the declaration arm | `test_a_refusal_DECLARES_the_stale_artifact_it_leaves_behind` | ✓ exact |
| C | stale sentence unconditional (`if True`) | only the negative control | `test_a_refusal_on_a_FIRST_export_claims_no_stale_file` | ✓ exact |
| D | census reverted to positional argv | only the keyword-argv param | `…EITHER_SPELLING[keyword-argv-…]` — **the positional param stayed GREEN** | ✓ exact |
| E | comment-only control | SURVIVES | nothing | ✓ survived |

**The granularity claim is sound, and it is the strongest thing in this increment.** Site A in
particular demonstrates precisely what the `S-F10` docstring asserts: the narrow-title params cannot
see `cell_len`, so the new CJK params are load-bearing rather than decorative. B and C genuinely pin
*"it says a stale file is there"* and *"it never says so falsely"* **separately**. That is good test
design and I want it recorded as such.

---

## 4 · Findings

### `CR17-F1` — `A-100.1`'s re-grounding is false: admitted shapes exceed the 2 s target by up to 9.3x [Severity: **HIGH**]

- **What.** `A-100`'s amended normative clause and the `EXPORT_MAX_CELLS` docstring both state,
  flatly, that the worst shape the budget admits costs **1.447 s** against a 2-second target — *"a
  margin of about 28 %, and nothing the budget admits crosses the target"* — and that cost spans
  **0.955–3.27 µs/cell, a 3.4x spread**. Measured clean in my mirror, **all three figures are wrong**,
  and the direction of the error is the dangerous one.
- **Where.** `mapper/app.py:3599–3609` (the *WHAT ACTUALLY JUSTIFIES 350,000* paragraph);
  `.dev-flow/…/01-requirements.md` amendment set 9 → `A-100.1` *"What replaces it"*, and the amended
  `A-100` clause.
- **The mechanism the hunt missed.** `_export_view_state` starts at
  `h = max(5, size.height - 10)` — **the start height is a free variable set by the terminal**, and it
  is the variable that decides how much *node density* a fixed cell budget admits. A **shorter**
  terminal gives a smaller `h`, so `w × h ≤ 350_000` admits a far **wider** (denser, more expensive)
  map. The hunt varied graph shape across two families while holding terminal height at two **tall**
  values, then generalised over the whole admitted region.
- **Measured** (extent + `render` + `save_svg` + write, no profiler; best of 3; artifact sha256
  asserted stable across reps; `mapper.__file__` asserted inside the mirror):

  | Terminal | worst ADMITTED shape | cells (budget 350,000) | **cost** | vs 2 s |
  |---|---|---|---|---|
  | 118x11 | 3,645-wide fanout | 349,928 | **18.557 s** | **9.3x over** |
  | 118x20 | 2,651-wide | 349,943 | **10.738 s** | 5.4x over |
  | **80x24** (classic default) | 1,944-wide | 349,935 | **5.391 s** | 2.7x over |
  | 118x35 (**the docstring's own cited terminal**) | 1,121-wide | 349,778 | **2.254 s** | over |
  | 118x40 | 940-wide | 349,711 | 1.803 s | under |

- **Driven end-to-end through the real `e` chord**, not only through the internals — at **80x24** a
  1,945-node map is **ACCEPTED** (`artifact written: True`, `REFUSED: False`, 4.6 MB SVG) and freezes
  the message pump for **7.493 s**. At the docstring's own 35-row terminal: 2.735 s.
- **Why it matters.** Four compounding reasons; the third is what makes this HIGH rather than MEDIUM.
  1. **It is a real user-facing defect**, not a documentation error. The budget exists to cap an
     uninterruptible freeze at 2 s, and on a standard 80x24 terminal it admits a 7.5 s one.
  2. **It is now the constant's only derivational support.** Every prior derivation was struck this
     increment; this claim is what replaced them.
  3. **The batch's own control names this exact failure**: *"A FALSE WORST CASE DISARMS THE GATE IT
     WAS ROUTED TO, which is worse than no figure, because a coordinator deciding on it believes a
     question has been answered."* And the corollary minted **in this same increment** — *"a
     conclusion drawn from ONE family of inputs is not corrected by re-measuring that family more
     carefully"* — is the precise shape of the error: the hunt corrected the *instrument* (removed
     `tracemalloc`) but kept a **search that held the governing variable fixed**. `A NEWLY MINTED
     CONTROL DOES NOT PROTECT THE INCREMENT THAT MINTED IT`, for the second time in two increments.
  4. The `0.955–3.27 µs/cell` "3.4x spread" is likewise understated: the h=11 point is
     **≈53 µs/cell**, a spread of ≈**55x**.
- **In fairness, and this matters.** `increment-017-rulings.md` §5 *declares* the weakness honestly:
  *"re-grounds the constant on a hunt, not a proof … A third family could exceed 2 s while staying
  under 350,000 cells."* **That declaration is correct and it is to the implementer's credit.** The
  finding is that the *normative* clause in `A-100` and the docstring carry **no such hedge** — they
  assert the universal flatly. A declared risk in an increment note does not license an unhedged
  normative claim in a requirement, and the hedged version would not have survived the gate as
  "nothing the budget admits crosses the target".
- **Suggested fix — three options, cheapest first. I recommend (a), and (a) alone unblocks.**

  **(a) STRIKE the universal, keep the constant.** This is the batch's own STRIKE remedy, and the
  amendment already supplies the ground that survives: *"`A-100`'s utility ground is untouched and
  stands alone."* Remove from both `A-100` and the docstring the sentences *"nothing the budget
  admits crosses the target"*, *"a margin of about 28 %"*, the `1.447 s` worst-accepted figure and the
  `0.955–3.27 µs/cell` span; replace with a stated, measured fact plus its limit, e.g.:

  ```
  #: WHAT JUSTIFIES 350,000 IS THE UTILITY GROUND, NOT A COST BOUND.  A budget in
  #: cells cannot bound the freeze, because cost tracks NODE DENSITY and the
  #: admitted density depends on the START HEIGHT (`max(5, size.height - 10)`),
  #: which the TERMINAL sets.  Measured: at an 80x24 terminal a 1,944-wide fanout
  #: is ADMITTED at 349,935 cells and costs 5.39 s; at 118x11, 18.56 s.  The
  #: 2-second target is therefore NOT met by this constant on short terminals, and
  #: that is recorded rather than implied.  <route to a follow-up finding>
  ```

  **(b)** If the 2 s target is to be *held*, the bound must include the free variable — e.g. refuse on
  `cells` **and** on a node-count-for-export cap, or fold the start height into the admitted region. A
  cells-only budget provably cannot express the constraint. This is a ruling, not a review call.

  **(c)** Add an arm that pins the claim so it cannot rot again: assert that the **worst admitted
  shape at the minimum start height** stays under target. Absent such an arm nothing mechanical checks
  this number — `VIGILANCE IS NOT A CONTROL`.
- **State:** `failed` (measured and refuted).

---

### `CR17-F2` — the stale sentence CAN be false, which is the one thing `A-100.2` forbids [Severity: **MEDIUM**]

- **What.** `A-100.2` requires the claim be conditional *"so it can never be false"*. The implemented
  guard is `if path.exists()` — which tests **existence**, not **staleness**. The sentence asserts more
  than existence: *"…es de una exportación anterior **y ya no refleja este mapa**."* I found a
  reachable case where the file is **byte-identical to an export of that very, unmutated graph**.
- **Where.** `mapper/app.py:3524–3530`.
- **Measured** (mirror-cr017b, provenance asserted):
  1. terminal **80x24**, map = 600-wide fanout → press `e` → **exports**, artifact `sha256 864e8fcd…`,
     1,412,837 bytes.
  2. **the graph is never mutated.** Same map at terminal **80x60** → press `e` → **REFUSED**
     (367,251 cells), artifact still `sha256 864e8fcd…`, `unchanged=True`, and the toast says:
     > `…límite 350000. Enfoca un subárbol con f y exporta esa vista. El archivo en …\mapa.svg es de una exportación anterior y ya no refleja este mapa.`

  The file reflects this map exactly. **The claim is false.**
- **Why it matters.** It is the batch's own defect family (*a statement that looks true and is not*)
  landing in the sentence written to close that family — and the negative control was written
  specifically to make this impossible. It covers only the **no-file** falsity mode; the
  **file-exists-and-is-current** mode is unguarded and untested. Site C's kill therefore certifies less
  than it appears to.
- **Root cause is shared with `CR17-F1`**: cell count depends on terminal height, so *the same
  unchanged map exports at one terminal size and is refused at another*. The increment did not model
  that, in either seam.
- **Suggested fix.** Either weaken the sentence to what `path.exists()` actually licenses — e.g.
  `f" Queda un archivo anterior en {path}; esta exportación no lo actualizó."` (true in every case, and
  still discharges `A-100.2`'s operator-facing purpose) — or make the condition match the claim by
  comparing against what was last exported. **I recommend the first**: it is smaller, it cannot be
  false, and it adds no state. Then extend
  `test_a_refusal_on_a_FIRST_export_claims_no_stale_file` with a third arm — *refused after a
  successful export of the identical graph* — so the new falsity mode is pinned.
- **State:** `failed` (measured).

---

### `CR17-F3` — the export path is spelled three times and nothing pins that they agree [Severity: **MEDIUM**]

- **What.** `self.store.workspace / f"{self.map_id}.svg"` appears at **`mapper/app.py:3492`** (the
  success path that writes) and again at **`:3524`** (the refusal path that declares). The whole point
  of `A-100.2` is that the declaration names *"the very path the success toast names"* — but that
  agreement is maintained by hand. The recomputation itself is *necessary* (the `try`-block binding is
  unreachable in the handler, since `ExportTooLarge` is raised before the assignment), so this is a
  reuse finding, not a bug today.
- **And no arm catches a drift.** `test_a_refusal_DECLARES_…` hand-builds
  `screen.store.workspace / "crece.svg"` (`tests/test_export_state.py:404`) rather than deriving it
  from the product. Change the success path's naming and the refusal could name a file that is never
  written, with the suite green. (`tests/test_pan.py:692` *does* derive it —
  `screen.store.workspace / f"{screen.map_id}.svg"` — so the convention exists and is simply not used
  here.)
- **Suggested fix.** Lift one accessor and use it in both branches, e.g.
  `def _export_path(self) -> Path: return self.store.workspace / f"{self.map_id}.svg"`, and have the
  declaration arm assert against `screen._export_path()` rather than a hand-built literal. Single-use
  abstractions are usually over-engineering — this one is not, because the two call sites are required
  to agree and nothing checks that they do.
- **State:** `executed` (read; no measurement owed).

---

### `CR17-F4` — `path.exists()` also answers True for a directory or a foreign file [Severity: **LOW**]

- **What.** Any entry at `<map_id>.svg` — a directory, or a file the operator put there — is described
  as *"de una exportación anterior"*. Narrow, and largely subsumed by `CR17-F2`'s fix.
- **Where.** `mapper/app.py:3525`.
- **Suggested fix.** Covered by `CR17-F2`'s recommended wording; otherwise `path.is_file()`.
- **State:** `executed`.

### `CR17-F5` — redundant `Path` wrapping in `_derived_spawn_executables` [Severity: **LOW**]

- **What.** `root = pathlib.Path(root or pathlib.Path(__file__).resolve().parent.parent / "mapper")`
  re-wraps a `Path` in the default branch, and `or` conflates "not given" with "falsy".
- **Where.** `tests/test_hermetic.py:117`.
- **Suggested fix.**
  `root = pathlib.Path(root) if root is not None else pathlib.Path(__file__).resolve().parent.parent / "mapper"`.
- **State:** `executed`.

---

## 5 · What is GOOD here, stated explicitly

Not padding — these are the parts I tried to break and could not.

- **The `root=` seam on `_derived_spawn_executables` is the right call.** The arm drives the *real*
  census over a synthetic tree instead of re-implementing the walk. Site D proves it discriminates.
- **`_spawn_argv` as one reader for both spellings** is the correct shape for `S-F11` — it fixes the
  class, and reusing it at `:171` incidentally removes a latent `IndexError` on `call.args[0]` for a
  keyword-only call.
- **The positive control** (`…returns_a_NON_absence`) is exactly the guard a `not in` census needs.
- **B/C splitting the two failure modes** of the stale claim is textbook, and the only reason
  `CR17-F2` is a gap rather than a hole is that C exists at all.
- **`markup=False` retained** on the lengthened notify — a Windows path containing `[` would otherwise
  be parsed as markup.
- **The struck harnesses do not ship**: `sec_b68_real_cost.py` / `b68_budget_probe.py` are absent from
  the tree, tracked and untracked, and the only `tracemalloc` occurrence left is the docstring naming
  it as the defect. A defective instrument left lying around is how it gets re-run.

---

## 6 · What I did NOT run — stated, not implied

| Not run | Why |
|---|---|
| **ruff** (`--isolated`, 27, set-equality vs `a552783`) | not executed at all. That claim is **unverified by me** |
| base lane at `4800906` (`1133`) | not run; I checked the `+7` itemisation against the diff arithmetically only |
| `mapper/app.py` `SEC-H2` change at `152ecd9` | outside the reviewed commit |
| security lens (`SEC-*`), suite/functional adequacy | `security-reviewer` / `qa-reviewer` |
| `FLAKE-1` root cause | carried. It did **not** fire in any of the 5 battery lanes; it fired once in my first full lane and passed 3/3 standalone |
| `.gitattributes`/`autocrlf`, socket-level guard, `N3`, `SEC-F4`, `S-F12`/`S-F15`/`N5`/`N6`, validator pre-existing blocks | carried, out of scope |
| whether 350,000 is the *right* number | that is a ruling. I measured only that the stated justification for it is false |

---

## 7 · Verdict

- [ ] OK to advance
- [ ] `BLOCK-UNTIL: …`
- [x] **Block — HIGH finding open**

**`CR17-F1` is HIGH and OPEN.** No fix has been applied, so there is nothing for me to verify; a
recommended fix does not close a HIGH. The increment does not advance on this verdict, and a standing
batch authorization does not reach it — a HIGH blocks regardless.

`CR17-F2` (MEDIUM) shares `CR17-F1`'s root cause and I recommend they be ruled together.
`CR17-F3`–`F5` are recommendations and block nothing.

**When a fix lands I will re-read the shipped bytes and re-measure**; I will not discharge this from a
report that a corrective pass ran. **I authored none of the fixes recommended above**, and if I am
asked to verify a fix that adopts my snippet wholesale, my independence on that line is structurally
weaker — the evidence that should discharge it is an arm I did not write (`CR17-F1(c)`).

### Evidence states

| Item | State |
|---|---|
| diff read in full (`4800906..046acea`) | `executed` |
| mirror digests (`04828ea1…`), pre/post | `approved` |
| default lane | `executed` — 1140 total, 2 mirror-provenance failures explained |
| slow / network lanes | `executed` — 19 / 1 ✓ |
| 5-site mutation battery | `executed` — 5/5 reproduced, restores byte-identical |
| `A-100.1` re-grounding | **`failed`** — refuted, `CR17-F1` |
| `A-100.2` never-false property | **`failed`** — refuted, `CR17-F2` |
| `A-100.3` (`S-F10`, `S-F11`) | `approved` — sites A and D discriminate exactly |
| ruff set-equality | `not-run` |
| security / QA lenses | `n/a — other reviewers` |

### Evidence checklist

- [x] Diff read in full — `mapper/app.py:3480–3519`, `3541–3616`; `tests/test_export_state.py:201–246`, `366–475`; `tests/test_hermetic.py:89–145`, `168–175`, `393–448`
- [x] Correctness pass — `CR17-F1` (budget admits a 7.5 s freeze at 80x24), `CR17-F2` (false claim), `CR17-F4`
- [x] Simplicity pass — `CR17-F5`; no premature abstraction found otherwise
- [x] Reuse / duplication — `CR17-F3` (export path x3; `tests/test_pan.py:692` shows the derived convention)
- [x] Tests reviewed for intent — battery confirms A/B/C/D each discriminate; `CR17-F2` records the one falsity mode the negative control does not cover
- [x] Verdict explicit — **Block**; `CR17-F1` is present, open, and carries no applied-and-verified evidence
