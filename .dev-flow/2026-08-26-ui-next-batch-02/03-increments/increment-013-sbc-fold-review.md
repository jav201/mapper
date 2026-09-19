# Increment 013 — S-B(+C) — Independent review of the fold that closes confirmation pass 3b

**VERDICT: APPROVED WITH FINDINGS.** No HIGH. Four MEDIUM and one LOW, all in the fold's own
bookkeeping and narration; none in the requirement's logic, none in any arm's oracle, and none
touching executable behaviour.

I am the independent reviewer for the text pass 3b drafted and declined to review. I re-derived
every number the fold carries rather than inheriting it, and I built a positive control for each of
my own instruments before trusting it — including the one that turned out to need it.

---

## Scope reviewed

Working tree at base `ce294f1`, branch `feat/ui-next-batch-02`, six modified files and one untracked
document. Diff read in full (`git diff` over all six; hunks at `01-requirements.md:639-641` and
`:8819`, `state.json:824-828`, `layered.py:112-116`, `test_fold.py:396-398/400-401/411-416`,
`test_inc3_census.py:169-175/193-199`, `test_darkside_budget.py:84-92/121-132`).

Also read in full: `increment-013-sbc-confirmation-3b.md` (untracked, 330 lines); the whole of
`tests/test_darkside_budget.py`; `layered._clip`/`_fit`/`_vis_width`; `darkside.plain`/`fit`;
`test_inc3_census.truncators()`; `outline.py:205-264`; `01-requirements.md:587-665` and the `A-95`
carries table.

---

## What holds — verified, not inherited

### 1. F15's replacement measurement reproduces EXACTLY

This was the most important thing to check, because F15 was charged for stating a mechanism as a
measurement, and the fix restates a measurement.

I drove the **shipped** functions. The forbidden (truncate-then-coerce) order was obtained by
neutralising `mapper.darkside.plain` in-process for the duration of the truncation call and applying
the real `plain` afterwards — so the shipped slicing code runs and **no hand-built model of any
truncator appears in my probe**, which is the defect that reached a ratified requirement in this
batch. The four hostile sources were extracted **from the arm's own `sources` dict by AST**, not
re-typed. The truncator set came from `truncators()`, derived.

| claim in the new docstring | my re-derivation |
|---|---|
| `0 of 160` forbidden-order `_clip` outputs exceed their code-point budget | **0 of 160** ✓ |
| all 160 byte-identical to the specified order | **160 of 160 identical** ✓ |
| `darkside.fit`, held to CELLS, breaches `114 of 160` | **114 of 160** ✓ |

`layered._fit` (the third derived truncator, not cited in the docstring) also returns 0/160 and
160/160 identical, consistent with the claim's scope.

**Both controls fired before the verdicts were trusted.** `darkside.fit(U+200B + "A", 1)` → 1 cell
specified, **2 cells** forbidden. And — the control I nearly did without — a 0-of-160 result for
`_clip` is *also* what a silently failed neutralisation would print, so I proved neutralisation
reaches `_clip` specifically: coercion off, `_clip` output retains **6** `U+200B` and **0**
`U+FFFD`; coercion on, **0** and **6**. The zero is a measurement, not a no-op.

`Evidence state: executed.`

### 2. The `_metric_of` immunity property the fold added is TRUE

The new paragraph claims a coercion-ordering mutant cannot reclassify its way out. Driven under the
forbidden order: `darkside.fit` → `cells`, `layered._clip` → `codepoints`, `layered._fit` →
`codepoints` — classification unchanged, while the same harness's control shows the forbidden order
is genuinely active. The per-truncator oracle is immune as stated. `Evidence state: executed.`

### 3. Widening from the charged 3 sites to 5 was CORRECT, not overreach

I checked this hardest, as asked, and the answer is that both extra sites needed correcting.

- **`mapper/views/layered.py:112-116` (production docstring).** `git blame` at HEAD: the paragraph
  that read *"The load-bearing property is that the output is COERCED"* was written by **`278fd36`**
  (this batch's own fold, 2026-09-11 08:57). The sentence eleven lines above it —
  *"THE ORDERING CLAUSE IS NORMATIVE AND LOAD-BEARING"* — was added later, by **`ce294f1`**
  (10:34). So the self-contradiction was **manufactured by the re-ruling commit** and left in
  production code. Correcting it is not scope creep; it is finishing `ce294f1`.
- **`tests/test_inc3_census.py:169-175` (function docstring).** Blame: `21809fd`, same batch, same
  day. *"The property that IS load-bearing is that the output is coerced"* asserts the substitution
  framing flatly, unscoped.

Neither edit reaches outside this batch's own footprint, and neither touches another batch's text.
`Evidence state: executed.`

### 4. The `B-62` judgment is RIGHT, and `C-56` cuts FOR it, not against

I re-derived the id space with my own census (`git ls-files` and `git ls-files --others` scanned
separately, `\bB-(\d+)\b` over `.md/.json/.py/.txt`):

- At **HEAD**, `B-62` appears in **zero** tracked files. Its only occurrences anywhere are the
  **two** in the untracked pass-3b document, both recommending `B-62` for this very finding.
- `B-53`'s live occupancy (`#map-canvas is can_focus=False`, `01-requirements.md:8818`) is real, so
  the re-id was owed.

The `C-56` question resolves in the fold's favour. `C-56` says an evidence transcript is corpus a
scanner reads. Precisely *because* it is corpus, `B-62` is already inscribed in the corpus meaning
"the cell-budget finding" — the same meaning the fold assigns it. Choosing `B-63` would have left a
corpus token whose only recorded meaning points at a finding that does not bear it, which is the
stale-token hazard `C-56` exists to name. Adopting `B-62` makes the corpus self-consistent. The
rejection of naive max+1 is correct reasoning.

The carries-table row is placed exactly where `F13` asked (directly under `B-53`,
`01-requirements.md:8819`). `Evidence state: executed.`

### 5. The remaining charged items are discharged

- **F14's three charged sites** — comment at `test_fold.py:400-401`, live message at `:411-416`,
  live message at `test_inc3_census.py:193-199` — all now say the fixed point is the WEAKER conjunct
  and explicitly not the ordering clause's substitute. Consistent with the ratified framing. No test
  couples to the old message text (swept `tests/` and `mapper/`; the only matches are the messages
  themselves). `executed`
- **F16** — `01-requirements.md:639-641` now past-tense and names where it is armed. The fold wrote
  *"the re-ruling recorded **below**"* where `F13`'s author suggested *"above"*; **the fold is
  right** — the RE-RULING step sits at `:655-657`, below the corrected sentence. `executed`
- **F17** — `test_fold.py` re-wrapped. Longest line in any of the four `.py` files is now **97**
  (`layered.py:659`, pre-existing); **no line over 99 in any of them**. `executed`
- **No executable delta**, re-derived independently: ASTs compared with docstrings stripped and all
  string-literal content masked — **IDENTICAL on all four `.py` files**, and the instrument
  **fired** on a known-bad injected change (`<=` → `<`, `return X` → `return not X`) in each. `executed`
- **`state.json` parses** as valid JSON (23 top-level keys). **ruff: 27 with project config, 27
  `--isolated`** — baseline unchanged. `executed`
- **Lanes.** `tests/test_darkside_budget.py + test_inc3_census.py + test_fold.py`: **59 passed, 3
  xfailed**, exit 0, 34.3 s. Full default lane: see §Lanes below. `executed`

### 6. The restraint on the WIDER id collision was RIGHT

Leaving carries-table `B-51`/`B-52` alone was the correct call, and for a stronger reason than the
one given. The operator's resume brief names `B-50`/`B-51`/`B-52` verbatim; renumbering them changes
the referent of a live instruction, which no implementer may do unilaterally. Beyond that: the two
id spaces (`state.json.open_blocks` and the `A-95` carries table) are **different registries**, and
merging them is a design decision about the batch's bookkeeping, not a defect fix. Surfacing and
stopping is what the increment boundary is for. **Agreed, without reservation.**

---

## Findings

### F18 — The new `B-62` carries-table row states a measurement no source can produce. [Severity: MEDIUM]

- **What:** the row reads *"Measured: a CJK source at budget 20 emits **32 cells (1.9×)**, at budget
  2 emits 3."* Driven against the shipped `layered._clip`:

  | CJK source length | budget 20 | ratio |
  |---|---|---|
  | 16 code points | **32 cells** (returned unchanged, `len ≤ 20`) | **1.60×** |
  | 20 code points | 40 cells | 2.00× |
  | ≥ 21 code points | **39 cells** (19 CJK + ellipsis) | **1.95×** |

  `32 cells` and `1.9×` cannot both describe one measurement. The provenance is visible: `32` comes
  from `state.json`'s pre-existing `what` field (correct for *its* source); `1.9×` comes from pass
  3b's routing section, which measured `_clip(CJK, 20) → 39 cells, 1.9×` (correct for *its*,
  different, source). The new row **fuses two measurements of two different inputs**.
- **Where:** `.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md:8819`.
- **Why it matters:** this is `F15`'s species — a number presented as measurement that was assembled
  rather than driven — reintroduced by the fold in the one row the fold authored, inside the live
  requirements artifact, in the same commit that removes `F15`. It is not load-bearing for any arm,
  which is what keeps it MEDIUM; but the batch's whole thesis is that this shape returns through the
  text nobody re-measures.
- **Suggested fix:** state one measurement, or none.

  ```
  Measured against the shipped `_clip`: a 16-code-point CJK title at budget 20 is
  returned UNCUT at 32 cells (1.6x, because `_vis_width` is `len`); a title of 21
  code points or more at the same budget emits 39 cells (1.95x); at budget 2, 3
  cells (1.5x).
  ```
- **Evidence state:** `executed` — driven against `layered._clip` over CJK sources of 4, 8, 16, 20,
  24 and 40 code points at budgets 2 and 20.

### F19 — The `RE_ID` note mis-describes the corpus its own conclusion depends on. [Severity: MEDIUM]

- **What:** the note says the id was *"derived MECHANICALLY … a census of every `B-<n>` token over
  **257 tracked files**"*. The cited probe (`bid_census.py`) walks `root.rglob("*")` — **every file
  on disk**, tracked or not, minus `.git/`, `__pycache__/` and `prototypes/`. It is not a
  tracked-file census, **and it could not have been**: the pass-3b document, which holds `B-62`'s
  only two occurrences and is the entire basis of the "no rival meaning" conclusion, is **untracked**.
  Verified: a genuinely tracked-only census at HEAD returns **zero** `B-62` occurrences.

  Two undeclared narrowings, separately: the corpus is filtered to six suffixes, and `prototypes/`
  is excluded. I checked the exclusion — **no `B-<n>` token lives under `prototypes/`**, so it is
  harmless here — but the note does not say the corpus was narrowed at all.
- **Where:** `.dev-flow/state.json:828`, the `RE_ID_2026-09-18` field.
- **Why it matters:** the note is the permanent justification for an id choice, and a reader who
  checks it as written gets a *different answer than the note reports*. A mis-described instrument
  in the record of a mechanically-derived conclusion is the same failure family as a mis-described
  measurement — this batch has now catalogued it at the instrument level eight times.
- **Suggested fix:** `"a census of every `B-<n>` token over the 257 .md/.py/.json/.txt/.toml/.cfg
  files on disk — tracked AND untracked, since the pass-3b document is untracked — excluding
  `.git/`, `__pycache__/` and `prototypes/` (verified to hold no `B-<n>` token)"`.
- **Evidence state:** `executed` — read `bid_census.py`; ran it (257 files scanned); ran my own
  tracked-only and untracked-only censuses for comparison.

### F20 — The note spells `B-63` into the id registry, and the cited probe now answers differently. [Severity: MEDIUM]

- **What:** the `RE_ID` note argues against `B-63` by **spelling it**: *"a naive max+1 (`B-63`) would
  have orphaned that recommendation and manufactured a gap."* That sentence is in `state.json`, the
  registry the census reads. **Demonstrated, not hypothesised:** I re-ran the note's own cited probe
  against the working tree and it printed

  > `MAX occupied: B-63` … `gaps below max: []` … `next free ABOVE max: B-64`

  with `B-63`'s single occurrence being the rejection note itself. My independently written census
  reported the same max. The note's reasoning and the note's text now disagree.
- **Where:** `.dev-flow/state.json:828`.
- **Why it matters:** this is `C-56` turned on the fold's own evidence — an id spelled verbatim in a
  transcript is corpus a scanner reads. The next person who re-ids the way this one did will take
  `B-64` and leave `B-63` a phantom, which is **exactly the manufactured gap the sentence exists to
  avoid**. The reasoning defeats itself in one hop.
- **Suggested fix:** name the candidate without spelling it — *"a naive max-plus-one would have
  orphaned that recommendation and manufactured a gap."*
- **Evidence state:** `executed`.

### F21 — The census of the substitution axis stopped one site short of its own criterion. [Severity: MEDIUM]

- **What:** the fold's stated reason for widening past `F14`'s charge was a sentence naming the
  coercion property "load-bearing" sitting in the same block as "the ordering clause is normative".
  **`mapper/views/outline.py` has that adjacency and was not touched:**

  | line | text |
  |---|---|
  | `:228-230` | *"That -- the title path being coerced AT ALL -- **is the load-bearing property here**"* |
  | `:244` | *"**The ordering clause is normative.**"* |

  One comment block, production code, `git blame` → `f3c1795`, this batch, 2026-09-11. It is the only
  remaining occurrence of the phrase in `mapper/` or `tests/`; my sweep for
  `reaching for|property that IS load-bearing|load-bearing property` across both trees returns this
  and nothing else.

- **My ruling on the merits: the sentence is DEFENSIBLE and should NOT be rewritten as if it were a
  sixth substitution claim.** Its referent is a different axis — *coerced at all* versus *not coerced
  at all* (`B-47`/`A-89`: this renderer coerced nothing and wrote an SVG that is not well-formed
  XML) — and `"here"` scopes it to the routing decision, not to `LLR-COERCE.2`'s conjunct
  comparison. The fold did not miss a live defect.
- **What IS wrong:** the record. The fold reports *a census of the axis found two more sites*. A
  census of the axis finds three, and nothing in the record says the third was considered and
  excluded. The next sweep re-opens it, and the next reviewer spends the pass I just spent.
- **Why it matters:** an unrecorded exclusion is indistinguishable from an oversight, and this batch
  has already paid for that ambiguity once — `F14` exists because six docstrings were re-read and
  two messages were not.
- **Suggested fix** — either is sufficient; the first is cheaper:
  1. Record the exclusion in the fold packet: *"`outline.py:229` matches the phrase but not the
     axis — its referent is coerced-at-all (`B-47`/`A-89`), scoped by 'here'. Considered, excluded."*
  2. Or add the scope clause the batch already uses everywhere else, at `outline.py:229`:
     *"…is the load-bearing property **of this routing decision** — a different axis from
     `LLR-COERCE.2`'s two conjuncts, where the budget is the load-bearing one."*
- **Evidence state:** `executed`.

### F22 — An unreproducible absolute path in a tracked artifact. [Severity: LOW]

- **What:** the `RE_ID` note cites `C:\\Users\\jjgh8\\clde\\bid_census.py`. That file is outside the
  repo, in a session scratchpad; no future reader can resolve it. Pass 3b redacted the same path
  shape to `C:\Users\<operator>\clde\`. Not a secrets issue and not a first — the username already
  appears in ten-plus tracked `.dev-flow` artifacts, so this is convention drift, not a leak.
- **Where:** `.dev-flow/state.json:828`.
- **Suggested fix:** describe the probe rather than pointing at it — *"probe: an `rglob` census of
  `\bB-(\d{1,3})\b` over the six text suffixes, run from the repo root passed as `argv[1]`"* — which
  is also the only form a reader can re-run.
- **Evidence state:** `executed`.

---

## Findings I looked for and did NOT raise

Stated so the next pass does not re-derive them.

- **Overreach in the widening.** Checked by blame; both extra sites are this batch's own text and
  one was made self-contradictory by `ce294f1` itself. Not overreach. `n/a — checked, not a finding.`
- **A test coupled to the rewritten assertion messages.** Swept `tests/` and `mapper/`; nothing
  matches the old or new message text outside the two assertions. `n/a — checked, not a finding.`
- **Behavioural change smuggled into a narration fold.** AST delta identical on all four files with
  a fired negative control. `n/a — checked, not a finding.`
- **`F16`'s "below" vs pass-3b's suggested "above".** The fold's direction is the correct one.
  `n/a — checked, the fold improved on the recommendation.`
- **`B-51`/`B-52` left uncorrected.** Correct restraint; see §6. `n/a — reviewed, endorsed.`
- **`test_fold.py:412`'s "an unterminated override survived the cut"** — pass 3b noted it and did not
  charge it; the fold did not act. I agree: it names an outcome, not a mechanism, and the outcome is
  what the assertion checks. `n/a — reviewed, not a finding.`

---

## Boundary statement

**What this review saw.** The complete working-tree diff, read line by line; the pass-3b document in
full; every file the diff touches, read around and beyond the hunks; the id space re-derived by two
independently written censuses; the `F15` measurement re-derived end to end against the shipped
functions with the arm's own AST-extracted sources; the `_metric_of` immunity claim driven under a
live forbidden-order harness; the executable delta re-derived with a fired negative control; ruff at
both scopes; three test modules and the full default lane.

**What it could not see — constructed, not asserted.** I built the blind spot and watched it open.

1. **The instrument that certifies this fold is blind to everything the fold changed.** I took
   `tests/test_fold.py`, rewrote the new assertion message from *"This is the **WEAKER** conjunct"*
   to *"This is the **LOAD-BEARING** conjunct"* — i.e. injected back the exact refuted framing the
   fold exists to remove — and ran my executable-delta instrument on it. It reported **IDENTICAL**.
   The same instrument reports DIFFERENT on `<=` → `<`. So the AST delta (mine, and `fold_delta.py`
   by the same design) proves the fold is *behaviourally inert* and proves **nothing whatever** about
   whether its sentences are true. Every semantic verdict above rests on reading, by one reviewer,
   and is exactly as strong as that reading. This is the load-bearing limit of the whole pass.
2. **A zero that could have been a no-op.** My `_clip` result — 0 breaches of 160, 160/160
   byte-identical — is bit-for-bit what a silently failed coercion-neutralisation would also print.
   I closed this one (coercion off → 6 `U+200B` survive; on → 6 `U+FFFD`), so it is *not* a live
   blind spot. I record it because the fold's `F15` docstring now asserts a zero, and a reader
   re-deriving it without that control will not know whether they measured or misfired.
3. **Not reviewed at all:** the security lane; `F1`–`F12` from passes 1–3; the `-m slow` lane's
   content (I did not run it — inherited from the operator, not verified); the substance of `B-62`
   as a defect (routed, and I reviewed only its id and its summary row); the other 267 tracked files
   beyond the id census; the UI at any terminal size — **I drove no UI in this pass**, and the
   118×34 / 80×24 discipline therefore did not apply to anything I did.
4. **Could not determine:** whether `bid_census.py` as run by the fold was run against the same tree
   state I ran it against. I re-ran it myself and report my own result; the fold's transcript number
   (257 files) reproduces, but the occupied-set it reports does not, for the reason in `F20`.

---

## Evidence checklist

- [x] **Diff read in full** — all six files, all hunks, cited above by line. `executed`
- [x] **Correctness pass** — `F15` re-derived (0/160, 160/160, 114/160) with two fired controls;
  `_metric_of` immunity driven; AST delta with fired negative control; JSON validity; line widths;
  message-consumer sweep. `executed`
- [x] **Simplicity pass** — no production code changed; no abstraction added; the fold is narration
  only. `n/a — no executable change in this fold.`
- [x] **Reuse / duplication** — my probe reuses `truncators()` and the arm's own `sources` literal
  rather than re-deriving either; the fold introduces no new helper. `executed`
- [x] **Tests reviewed for intent** — the three rewritten messages now state WHY the weaker conjunct
  is kept (a banned-point-to-banned-point remap) and why it cannot substitute; that is intent, not
  behaviour. `executed`
- [x] **Verdict explicit** — **APPROVED WITH FINDINGS**. **No HIGH is present**, so there is no
  applied-and-verified evidence owed. `executed`

## Lanes

| lane | result |
|---|---|
| `test_darkside_budget.py` + `test_inc3_census.py` + `test_fold.py` | **59 passed, 3 xfailed**, exit 0, 34.3 s |
| full default lane | **1080 passed, 19 deselected, 3 xfailed**, exit 0, **302.33 s** — run by me, not inherited; reproduces the operator's counts exactly. `FLAKE-1` did not fire |
| `-m slow` | `not-run` — inherited from the operator, not verified by me |
| ruff (project config) | **27** |
| ruff (`--isolated`) | **27** |

## Tree discipline

**I wrote nothing to the repository.** Every probe lives in my own scratchpad
(`rev_fold_probe.py`, `rev_ast_delta.py`), byte-level/read-only against the repo, with
`PYTHONDONTWRITEBYTECODE=1` set on every run that imported `mapper`. The forbidden order was
obtained by in-process attribute substitution, so **no source file was ever mutated on disk** and no
restore was required. `git status --porcelain` at the end of my pass shows the **same six modified
files, byte-identical to how I found them** (hashes below), plus **two** untracked documents — the
pass-3b document that was already there, and this review, which is my deliverable. I modified
nothing that existed when I started.

| file | sha256 (first 16, at end of my pass) |
|---|---|
| `01-requirements.md` | `3b387d7e3ac2b520` |
| `state.json` | `683d35bc5a0a8ec1` |
| `mapper/views/layered.py` | `dca00aade523db8e` |
| `tests/test_darkside_budget.py` | `e1ddc758ef90140f` |
| `tests/test_fold.py` | `9c52621fcea264cd` |
| `tests/test_inc3_census.py` | `40d7ac0bdd82ea7b` |

## Verdict

- [x] **APPROVED WITH FINDINGS** — no HIGH; `F18`–`F21` MEDIUM, `F22` LOW.
- [ ] `BLOCK-UNTIL:` — not invoked.
- [ ] Blocked — not invoked.

The fold does what it claims. Its three charged corrections land, its two uncharged ones were owed
and are inside its own footprint, its replacement measurement reproduces exactly under an
independent instrument with its controls fired, and it moved nothing executable. The re-id judgment
is right and `C-56` supports it rather than cutting against it.

What the four MEDIUMs share is that **the fold's narration outran its measurement in precisely the
places the fold was convened to stop that happening** — a fused ratio in the row it added, a census
described as narrower than it was, a rejected id spelled into the registry that the census reads,
and an axis swept without recording what was deliberately left. None of them is a defect in the
requirement or in an oracle. All four are cheap to fix and all four are in text that a later pass
will otherwise take as measured.

**I wrote no production code and no test code.** The snippets in `F18`–`F22` are recommendations;
whoever applies them is their author and owes them a reviewer who is not me.

**Handoffs.** `qa-reviewer`: pass 3b's `stays_within_its_budget[1]` observation is untouched by this
fold and still stands — width-1 coverage rests on one named arm. `security-reviewer`: `B-62`'s
substance is unchanged by the re-id; only its number moved.
