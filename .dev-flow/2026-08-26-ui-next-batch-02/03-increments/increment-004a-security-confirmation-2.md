# Security confirmation 2 — Inc-4a round 3 (focused)

| Field | Value |
|---|---|
| Scope | **Narrow.** C1–C4 only, plus the three volunteered self-corrections. Not a re-review of the increment. |
| Branch / entry | `feat/ui-next-batch-02` @ `5f4816c`, nothing committed, 21 dirty paths |
| Method | isolated mirror (`git clone --local --no-hardlinks` + working-tree overlay of `mapper/` and `tests/`); real repo never mutated |
| Instrument | `PYTHONUTF8=1 python -m pytest`; verdicts read **per arm**, collected count asserted at 1, never a process exit code |
| Restores | every mutation restored in a `finally`, sha256 `identical=True` printed per mutation |

## S0 · BLUF

**All four confirmations DISCHARGE.** C1's two facts fail independently — I executed both
directions and neither arm can stand in for the other. C2's derived census goes RED on Inc-4b's
exact shape while the retired two-tuple goes GREEN, which is C-31 demonstrated rather than quoted.
C3's aliasing is gone by identity, not by type. C4 shows no regression.

**Two NEW findings, neither of them a blocker.**

- **NEW-4 (MEDIUM)** — I could not construct the seam the author declared, but I constructed a
  different one that is live and is the *reverse* of his. A method is classified as a pass-opener
  purely by **naming** `_open_paint_pass` anywhere in its body. It need not call it, and it need not
  call it before reading the resolution. A consumer that **defers** the opener — the house idiom,
  `call_after_refresh(...)`, shipped at `app.py:1256` and `app.py:1599` — and reads `_view_state`
  now is silently excused. I measured that shape **GREEN**. A one-line hardening turns it RED and I
  measured that too.
- **NEW-5 (MEDIUM)** — the justification for C1's silence is false as painted. The strip does **not**
  declare the overflow above the bound; at the declared context of use it is not on screen at all.
  The operator is still informed — but by the **canvas**, not the strip. The fix is discharged; the
  reason written under it is wrong, in a shipped docstring.

**Verdict: SIGN-OFF.** Neither NEW finding is HIGH, neither weakens what C1–C4 asked me to confirm,
and both are gate-strength / accuracy items rather than live defects. Mitigations are listed and
**neither should be self-cleared.**

---

## S1 · Fidelity — established before anything was measured

The fast lane in a naive mirror read **`1 failed, 821 passed`**, not `822 passed`. That is a mirror
artifact and I chased it before trusting a single verdict:

```
FAILED tests/test_a3_census.py::test_tc_a3_no_source_file_is_invisible_to_the_census
```

`tests/inc4_support.py` and `tests/test_search.py` are **new files staged but never committed**
(`A ` / `AM`), so a clone of `HEAD` does not carry them and `git ls-files` cannot see them — which
is exactly the hole `test_tc_a3_...` exists to redden. Reproducing the real repo's **index** state
(`git add -N`, mirror only) made the tracked sets identical and the lane match:

```
diff real_tracked.txt mirror_tracked.txt -> TRACKED SETS IDENTICAL
822 passed, 17 deselected, 3 xfailed in 136.16s     EXIT=0     zero FAILED
```

Entry digests, mirror vs real, all `same=YES`:

```
mapper/app.py           b960f4eff37093c9
tests/test_search.py    e22a72937b268e24
mapper/search.py        77836620bbddec54
mapper/views/state.py   0b661033b2ceff9a
mapper/views/layered.py 3e081a6c61af9a20
```

Scope pin re-measured independently: **4 source files** (`app.py`, `search.py`, `layered.py`,
`state.py`), and `mapper/keymap.py` has **0 lines changed** (`git diff --numstat` returns no row for
it; the file itself is 250 lines and untouched). Matches the brief.

---

## C1 · The false statement above the bound — **DISCHARGED**

### The two facts fail independently — executed, both directions

```
=== BASELINE (unmutated) ===
     GREEN  test_above_the_bound_the_count_line_does_not_claim_zero_matches
     GREEN  test_below_the_bound_the_count_line_still_says_zero_when_empty

### C1-a  _search_order, the bound branch -> the distinct signal replaced by an empty container
       RED  test_above_the_bound_the_count_line_does_not_claim_zero_matches
     GREEN  test_below_the_bound_the_count_line_still_says_zero_when_empty
       RED  test_the_search_obeys_the_renderers_declared_bound
    restore mapper/app.py: b960f4eff37093c9 -> b960f4eff37093c9 identical=True

### C1-b  _count_line, the empty-result branch -> the blank text used for the unanswered state
       RED  test_below_the_bound_the_count_line_still_says_zero_when_empty
     GREEN  test_above_the_bound_the_count_line_does_not_claim_zero_matches
    restore mapper/app.py: b960f4eff37093c9 -> b960f4eff37093c9 identical=True
```

Collapsing the bound back into an empty order reddens the above-bound arm and leaves the empty-state
arm **GREEN**. Deleting the empty-state wording does the exact opposite. **Neither arm can stand in
for the other; the pair really is two facts.** The author's MR3-1a / MR3-1b reproduce exactly.

### The behaviour itself, mounted, at the declared context of use (118×34)

```
--- MOUNTED, ABOVE THE BOUND ---
N = 12002  real matches = 6001
order          -> None
count_line     -> ''
```

No false statement is painted. `_search_order` returns `None`, distinct from `[]`, and `_count_line`
paints nothing. **That is the defect, and it is fixed.**

### But the stated reason for the silence is false — NEW-5

The author's S1 says: *"The strip's own `N fuera de vista` declaration is what tells the operator
why, so nothing is lost by the silence."* The shipped `_count_line` docstring says the same at
`mapper/app.py:1726-1728`. Measured, mounted:

```
STRIP AS PAINTED        -> ''
strip declares overflow -> False
strip overflow token    -> False
```

The strip is **blank**. Diagnosed rather than asserted:

```
_pagination_text() len   = 12038   'fuera de vista' in it -> True
_unpainted_ids()         = 12002
count region             -> Region(x=0, y=42, width=116, height=104)
```

The declaration **is** in the `Text` object — and is painted at row 42 of a 34-row terminal, i.e.
entirely below the viewport, because `_pagination_text` prices its reserved pagination meter at
`per_page = max(1, total)` and `darkside.step_meter` emits one glyph per unit, wrapping the strip to
104 rows. Control, same app, same session, a graph below the bound:

```
strip -> ' ▰▱▱▱…▱   1/40  1/20 coincidencias en el mapa  ▽ 26 fuera de vista '
```

**The meter blowup is pre-existing**, at `HEAD:mapper/app.py:1681,1685`, untouched by this
increment — so it is a carry, not a regression.

**The operator is nonetheless not left uninformed**, which is what the brief asked me to confirm.
The canvas declares the overflow in plain Spanish, unambiguously:

```
CANVAS AS PAINTED -> '◆ mapper · mapa de conceptos\n\nmapa de 12002 nodos: supera el límite de
                      12000 nodos. Se omitió el dibujo del árbol completo (fichas, aristas y
                      cobertura).'
```

So: **C1 DISCHARGED.** The operator-safety conclusion holds. The *mechanism named in the shipped
docstring* is the wrong one.

---

## C2 · The open-pass pin is derived — **DISCHARGED**

### Baseline census internals, re-derived independently on the shipped tree

```
methods parsed = 76   openers = 2 ['_declare_after_layout', 'refresh_canvas']
pass-free readers derived = 15
 GREEN  derived census
 GREEN  [control] RETIRED hand-written two-tuple
```

76 / 2 / 15 — the author's numbers reproduce exactly.

### The decisive test: Inc-4b's exact shape

```
### C2-a  MapScreen -> a keypress-bound consumer reaching `_view_state`, NO pass opened
    methods=77  openers=2  reaching=16
       RED  derived census
     GREEN  memo-lifetime arm
     GREEN  [control] RETIRED hand-written two-tuple
    restore mapper/app.py: b960f4eff37093c9 -> b960f4eff37093c9 identical=True
```

**The derived census goes RED; the retired two-tuple stays GREEN under the identical mutation.**
That is C-31 demonstrated on this file, not quoted at it. The retired predicate is reconstructed
from the census docstring (it iterated `refresh_canvas` / `_declare_after_layout` and asserted each
opens a pass) — it is insensitive to a new consumer by construction, and measurement agrees.

### The author's own declared seam — I could not construct it

He warns that *"a future opener under a different name would stop propagation for the wrong
reason."* I built it: a `_begin_frame` that clears the memo directly, plus a consumer calling it and
then reading `_view_state`.

```
### C2-b  [SEAM A, author's own] a future opener under a DIFFERENT NAME clearing the memo directly
       RED  derived census
```

**RED — it fails loud.** Any method touching `self._search_memo` is *seeded* into `reaching` by
`test_search.py:1040`, so an alternative opener is caught as unexplained rather than silently
trusted. His self-critique was more pessimistic than his mechanism. Good.

### The seam that *is* live — NEW-5's sibling, NEW-4

The classifier at `tests/test_search.py:1036` is:

```python
openers = {name for name, r in reads.items() if "_open_paint_pass" in r}
```

That is a **name mention**, not a call, and carries no ordering. Two constructions, both measured:

```
### C2-c  [SEAM B] a consumer that DEFERS the opener (call_after_refresh) then reads NOW
    methods=77  openers=3  reaching=15
     GREEN  derived census

### C2-d  [SEAM C] a consumer that only NAMES the opener in a guard, never calls it
    methods=77  openers=3  reaching=15
     GREEN  derived census
```

Both **GREEN**. Both read the resolution from the previous frame's memo with no pass open. Seam B is
not contrived: `self.call_after_refresh(self._declare_after_layout)` is the shipped house idiom at
`mapper/app.py:1256` and `mapper/app.py:1599`. An Inc-4b consumer that follows the local pattern —
schedule the repaint, read the order now — is excused by the very arm landed to catch it.

The census's own guard is a **subset** check (`{"refresh_canvas", "_declare_after_layout"} <=
openers`, `test_search.py:1037`), so `openers` growing from 2 to 3 is invisible.

**Tested mitigation.** Two changes, measured on all three shapes:

```
  shipped tree (no mutation)
    openers by NAME-mention : ['_declare_after_layout', 'refresh_canvas']
    openers that CALL it    : ['_declare_after_layout', 'refresh_canvas']
    exact-set guard passes  : True

  SEAM B  deferred opener (call_after_refresh), reads NOW
    openers by NAME-mention : ['_declare_after_layout', 'action_deferred_open', 'refresh_canvas']
    openers that CALL it    : ['_declare_after_layout', 'refresh_canvas']
    exact-set guard passes  : False   <- RED

  SEAM C  opener only NAMED in a guard, never called
    openers by NAME-mention : ['_declare_after_layout', 'action_named_not_called', 'refresh_canvas']
    openers that CALL it    : ['_declare_after_layout', 'refresh_canvas']
    exact-set guard passes  : False   <- RED
```

Recommended (for `software-dev` to apply, not me) at `tests/test_search.py:1037`:

```python
    # EXACT, not a subset: `openers` is a name-mention census, so a method that
    # merely NAMES the opener -- deferring it via `call_after_refresh`, the house
    # idiom -- would otherwise be excused from the walk while reading the
    # PREVIOUS frame's memo.  A new opener is a deliberate act; make it declared.
    assert openers == {"refresh_canvas", "_declare_after_layout"}, sorted(openers)
```

Optionally also require the opener be *called as a statement*, which distinguishes a real opener
from a deferred one even if the exact set is later widened on purpose.

### The three exemptions are genuinely exempt, not quietly excused

- **`_reclamp_pan`** — structurally exempt. `refresh_canvas` opens the pass as its **first
  statement** (`mapper/app.py:1933`) and calls `_reclamp_pan` inside its own `try`
  (`mapper/app.py:1944`). Not a judgement call at all.
- **`_pan`** (`mapper/app.py:1463`) and **`action_export_svg`** (`mapper/app.py:2344`) — both reach
  `_view_state` with no pass open. What protects them is stronger than the stated reason, and I
  measured which:

```
  baseline order len = 30
  QUERY changed, NO new pass  -> memo re-resolved (not stale): True
  GRAPH object swapped, NO new pass -> re-resolved: True
  GRAPH mutated IN PLACE, NO new pass -> STALE served: True (served 30, truth 31)
```

The memo is **self-invalidating on its own key** (`memo[0] is self.graph and memo[1] ==
self.query_text`, `mapper/app.py:1884`). A stale read is only reachable through **in-place mutation
of the graph object** followed by a pass-free read. Neither `_pan` nor `action_export_svg` mutates
the graph, so both are genuinely exempt today. The author's S8 hedge ("ordering luck; nothing
enforces that ordering") **understates his own guarantee** — the key enforces it, not the ordering.
The residual exposure is narrower than he says, and is the shape NEW-4 cannot see.

**C2 DISCHARGED.**

---

## C3 · The memo returns a `tuple` — **DISCHARGED**

Direct observation, not type-checking:

```
type(_search_order()) -> tuple
same object across reads in one pass: a is b -> True; b is c -> True
memo slot holds the SAME object handed out: True
mutable? hasattr(append) -> False
mutation attempt raised AttributeError -- immutable (tuple)
re-read after mutation attempt unchanged: True
'intruder' not in re-read: True
```

And the pass boundary still drops it, so immutability did not accidentally buy a longer lifetime:

```
new pass returns a DIFFERENT object: True  (equal content: True)
```

The aliasing is gone, and the memoised object is the **same immutable object** across every read in
a pass. The arm asserts the property rather than the type (`test_search.py:1096-1103`), so a later
defensive-copy shape would still be gated.

---

## C4 · No regression on what was already cleared — **DISCHARGED**

Scoped to the **whole working diff vs `HEAD`**, a superset of round 3 (the round-2 exit tree is not
recoverable — nothing is committed — so I checked more, not less).

| Item | Evidence |
|---|---|
| No new sink for file-derived text | Sink scan over all 142 added `app.py` lines + all added `tests/` lines: 3 hits, all in tests, all AST censuses reading the repo's **own source** (`tests/test_search.py:587` `inspect.getfile(MapScreen)`; two in `tests/` over `mapper/views`). No new user-text, network, subprocess, `eval`/`exec` or path sink. |
| `ViewState.hits` membership-only | `mapper/views/state.py:90` — `hits: frozenset[str] = frozenset()`. Unchanged, and structurally non-indexable. |
| Blank-query rule at the owner | `mapper/search.py:91` — `if not q.strip(): return frozenset()` in `hits`. `query` delegates (`mapper/search.py:115` `found = self.hits(q)`), so the rule is enforced **once, at the owner**, and both entry points inherit it. |
| No secret / path / username added | Scan for `jjgh8`, `javgranados`, `C:\Users`, `api_key`, `secret`, `token=`, `Bearer`, `ghp_`, `AKIA`, private-key headers over every added line in `mapper/` and `tests/`: **zero hits**. |
| No hostile code point | Census over the 5 changed source files + the round-3 record for bidi / zero-width / control code points: **0 total**. Nothing spelled verbatim here. |

Perf discharge (F1/F1a/F1b) not re-measured, per the brief.

---

## The three volunteered self-corrections — all three confirmed

**1 · The export-toast anchor resolves.** Both mirror and real repo:

```
mapper/app.py:2373:            self._event_toast("exportado", str(path))
```

The durable anchor is correct and the line number is current. The item was already routed
(`increment-004a-security-review.md:286`, recorded then at `:2296`), so Inc-REPAIR inherits a
resolvable address. Recording the call alongside the numeral is the right correction — this address
has now moved twice.

**2 · The ledger reconciles, and the "retired fifth arm" really did not exist.** Measured at
`HEAD 5f4816c` in a pristine clone:

```
baseline: 801 passed, 17 deselected, 3 xfailed   ->  804 collected
current:  822 passed, 17 deselected, 3 xfailed   ->  825 collected
tests/test_search.py: 18 test functions (matches the claimed 14 -> 18)
```

804 → 825 reconciles exactly. And `test_one_paint_pass_resolves_exactly_once` **still collects** —
what R3-3 retired is an assertion inside it, not a test function, exactly as the correction says.
The self-correction is accurate and the original claim was not.

**3 · Ruff set identity holds; the pair count is instrument-dependent.**

```
entry pin (5f4816c):  Found 27 errors   19 distinct file|rule pairs
current:              Found 27 errors   19 distinct file|rule pairs
diff entry vs now  -> EMPTY -- SETS IDENTICAL
distinct rules: F401 F841
```

My instrument reproduces the brief's **19**, not the author's 21. The gate — finding count and set
identity — holds on every instrument. **Declining to adopt a number he could not reproduce was the
correct call**, and it cost nothing, because the pair count is not the gate.

---

## Findings

### NEW-4 — the pass-opener classifier trusts a name mention, not a call  [Severity: MEDIUM]

- **What:** `openers` is derived by testing whether a method's source *mentions* `_open_paint_pass`.
  A method that defers the opener (`call_after_refresh`) or merely names it is classified as an
  opener, removed from `reaching`, and excused — while reading the previous frame's memo. The guard
  on the opener set is a subset check, so growth from 2 to 3 is invisible.
- **Where:** `tests/test_search.py:1036` (the classifier) and `tests/test_search.py:1037` (the
  subset guard).
- **Why it matters:** the deferred-repaint shape is this codebase's own idiom
  (`mapper/app.py:1256`, `mapper/app.py:1599`). The arm was landed **specifically** to force Inc-4b
  to open a pass or declare an exemption; a consumer written in the house style bypasses it
  silently. Measured GREEN on two constructions. Not a live defect — no shipped method has this
  shape (openers is exactly 2, both calling synchronously).
- **Recommendation:** replace the subset guard with an exact-set assertion (snippet in C2 above).
  Measured: turns both seam shapes RED and leaves the shipped tree GREEN. `software-dev` to apply.

### NEW-5 — the silence above the bound is justified on a declaration that is not on screen  [Severity: MEDIUM]

- **What:** the fix is correct, but the reason written under it is false. The strip's `N fuera de
  vista` is cited as what informs the operator; measured mounted at 118×34, the strip paints nothing
  at all above the bound. The pagination meter is priced at `per_page = total`, wrapping the count
  region to 104 rows at `y=42`, off-viewport. The operator is informed by the **canvas**, not the
  strip.
- **Where:** `mapper/app.py:1726-1728` (the shipped docstring claim) and
  `increment-004a.md:809-810` (S1). Underlying meter: `mapper/app.py:1755` /
  `mapper/app.py:1759` — **pre-existing at `HEAD`, not a regression**.
- **Why it matters:** a false rationale in a shipped docstring is the same failure class this round
  was convened to repair. The next reader will trust "the strip declares it" and it does not. It
  also means the strip is unreadable at large graphs generally, not only above the bound.
- **Recommendation:** (a) correct the docstring and S1 to name the **canvas** overflow declaration
  as the surface that informs the operator; (b) carry the unbounded pagination meter as a separate
  finding to Inc-REPAIR — do not fix it under this gate, it is out of scope and behavioural.

### NEW-6 — S5's pre-digest is mislabelled  [Severity: LOW]

- **What:** S5 labels `app.py b960f4eff37093c9` as the "(round-2 exit state)". `b960…` is the state
  **after** the round-3 repairs — it is the tree I measured all four discharges on, and the round-3
  header itself declares the round-2 entry as `a2b621256c22e533`.
- **Where:** `increment-004a.md:901`.
- **Why it matters:** a reader reconciling digests across rounds will conclude the mutation battery
  ran on the pre-repair tree. It did not; the verdicts are sound. Bookkeeping only.
- **Recommendation:** relabel as the round-3 post-repair state.

### Carry (not new) — operator username in a `.dev-flow` artifact  [Severity: LOW]

`increment-004a.md:122` contains an absolute path carrying the operator's Windows account name, and
S7 (`increment-004a.md:971`) claims *"no fixture, path, token or username entered this file or the
diff."* True for the round-3 addition (lines 774-991 are clean); false for the file as a whole.
`/dev-flow-sync` pushes `.dev-flow/` to the shared Obsidian vault, so this leaves the machine.
Same class as the already-routed export-toast leak. Recommend redacting to a repo-relative path and
softening the S7 wording to "no … entered this round's addition".

---

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — NEW-4, NEW-5, NEW-6, carry.
- [x] Each finding has a severity — MEDIUM, MEDIUM, LOW, LOW.
- [x] No secret value appears in this output — locations referenced, values never reproduced;
      hostile code points named as `U+XXXX` only, and the census found **0**.
- [x] Verdict explicit — SIGN-OFF, below.
- [x] No new tool/integration in this round — nothing to scope-review.
- [x] Per-arm verdicts, never a process exit code — every table above.
- [x] Real repo never mutated — post-run digests identical to entry (`app.py b960f4eff37093c9`,
      `test_search.py e22a72937b268e24`, `search.py 77836620bbddec54`,
      `state.py 0b661033b2ceff9a`, `layered.py 3e081a6c61af9a20`), `HEAD` still
      `5f4816c1fe1e407d33058eb6f5c3b06e39c39b4d`, 21 dirty paths — unchanged from entry.
- [x] Every mutation restored, `identical=True` printed per mutation; mirror carries no residue —
      full lane re-run **after** the whole battery: `822 passed, 17 deselected, 3 xfailed`, exit 0.
- [x] Mutations described by position and operation; no mutated token spelled.

---

## Verdict

- [ ] Block
- [x] **SIGN-OFF** — C1, C2, C3, C4 all **DISCHARGED**

**With two mitigations attached. Neither should be self-cleared.**

1. **NEW-4** — apply the exact-set opener guard at `tests/test_search.py:1037` before Inc-4b lands.
   The whole argument for landing this arm *before* Inc-4b is that it forces the next consumer to
   declare itself; in the house idiom it currently does not. The fix is one line and I measured it
   working.
2. **NEW-5** — correct the docstring at `mapper/app.py:1726-1728` and S1 to name the canvas
   declaration. Route the unbounded pagination meter to Inc-REPAIR as a separate carry.

Neither blocks the increment: the four things I was asked to confirm are confirmed, on executed
evidence, in both directions where the brief asked for both.
