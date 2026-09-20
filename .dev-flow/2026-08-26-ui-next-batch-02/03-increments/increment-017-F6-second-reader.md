# Second reader — `CR17-F6` and the clockless arm that replaced it

| Field | Value |
|---|---|
| Reader | `qa-reviewer`, **second reader**. Authored none of the diff, none of `CR17-F6`, and none of its remedy |
| **Mode** | **`validation`** — a verdict over results. Every item below carries one of the seven evidence states and names its executor |
| Batch | `2026-08-26-ui-next-batch-02` (sealed) |
| Scope | `CR17-F6` (increment-017 pass 2 §4; `01-requirements.md` amendment set 11 / `A-100.6`) and `tests/test_export_state.py::test_the_SAME_map_is_admitted_or_refused_by_the_TERMINAL` + the `EXPORT_MAX_CELLS` docstring. Nothing wider |
| Mirror | `…\scratchpad\mirror-f6-2nd` at `479892e`. **Every digest held** (below) |
| Date | 2026-09-19 |
| **This report authorises nothing.** | I am not an approver. `software-dev` implements; the coordinator rules |

---

## 0 · Bottom line

1. **`CR17-F6`'s verdict is right; one of its two halves is right for the wrong reason.** The
   "monotonically" half I reproduced independently and **strengthened**. The "breaches at its own
   boundary" half I **could not reproduce at all**: 27 runs of the identical shape on this machine
   gave **0 over 2 s** (1.333–1.662 s). The struck sentence is not *false* on my evidence — it is
   *not a property of the code*. Strike it anyway; the reason recorded in the artifact needs correcting.
2. **The clockless arm is better, but it is half-blind and one of its two rows is a knife edge.** It is
   killed from both directions as claimed — but asymmetrically (0.03 % down vs +300 % up), and **three
   mutations of the very expression it exists to pin survive it.** A two-row boundary pin at
   terminals **17 / 18** catches two of those three and costs nothing.
3. **"Stop producing numbers" is right, and the artifact did not actually stop.** The replacement
   claim is clockless; the *strike evidence* still carries eight unattributed numbers, one group of
   which I just failed to reproduce by 44 %. Do both: keep the clockless mechanism **and** mark the
   residual figures `IRREDUCIBLY A READING`.
4. **Yes — there is a fourth false claim in that docstring, and arguably a fifth.** The heap sentence
   (*"18.9 bytes/cell … about 7 MB"*) is wrong by **14.6×** on the shape the arm itself admits, and
   the *"WHAT THAT REFUSES"* list is a property of `(map, terminal)` stated as a property of the map —
   it was measured at `118x34` undeclared, and one of its rows **inverts at terminal height 68**.
   That is this family's own lesson, unapplied twenty lines below where it is minted.

---

## 1 · Mirror, traps, digests — every digest HELD

Mirror `…\scratchpad\mirror-f6-2nd` (tracked tree at `479892e`, `git init` + one commit inside).

| Pin | Value | Before | After |
|---|---|---|---|
| aggregate sha256, all 92 `.py` under `mapper/` + `tests/` | `7e582edd2f42bdb42ebd91ef6ecd57dfefd39bd1fcce58b7561c960691e07177` | ✓ | ✓ **held** |
| `mapper/app.py` | `58443932d615b9561fad5343…` (mirror **==** repo, byte-identical) | ✓ | ✓ **held** |
| `tests/test_export_state.py` | mirror `1007ad9b…` / repo `626a0f93…` | — | — |

**I re-verified the mirror rather than trusting the brief, and the brief is wrong on one point.**
`tests/test_export_state.py` is **CRLF in the mirror** and LF in the repo — the brief lists it as LF
and says the `git archive` extraction left line endings untouched. Content is identical after
normalisation (`626a0f93…` on both sides). Across `mapper/` + `tests/`, **43 files differ by line
endings only and zero by content**; the `mapper`/`tests` file sets are identical (the 11 extra `.py`
in the repo are all under `prototypes/`). **Any multi-line anchor for this batch must be built against
the bytes of the tree it will be applied to, not against the brief's table.**

**Trap 1 defended in every probe.** Every script asserts *and prints* that `mapper.__file__` resolves
inside the mirror before it imports anything else; `TRAP1 OK …mirror-f6-2nd\mapper\__init__.py`
appears in every run. **Trap 2**: no scratch file is named after a stdlib module (`geom_probe.py`,
`cost_probe.py`, `view_probe.py`, `heap_probe.py`, `content_probe.py`, `mutate.py`, `mutate2.py`).

**Repo untouched.** `git status --porcelain` in `C:\Users\jjgh8\Github\mapper` is empty apart from
this report. All measurement and all mutation happened in the mirror. `app.py` in the mirror was
restored byte-identical after each of the eleven mutations, with sha256 re-asserted after every one.

---

## 2 · Q1 — Is `CR17-F6` correct? **My own counterfactual, built from the mechanism, not from theirs**

### 2.1 Method — deliberately not the finding's method

I did not re-run a shape hunt across terminals. I asked a different question: *given the finding's own
shape, how stable is the reading?* So I fixed the shape by bisection through the product, then varied
**the measurement context** — fresh process, repeated in-process, inside `pytest` alone, inside
`pytest` after the whole module had run, and the reviewer's second title family. Every run drives
`MapScreen._export_view_state` → `_current_renderer().render` → `save_svg`, which is exactly the
synchronous region `action_export_svg` freezes the pump for (`app.py:3526–3542`). No `tracemalloc`,
no profiler, nothing else inside the timed region — set 9's defect avoided by construction.

**The shape reproduces exactly.** Bisecting the product at `118x40` gives max admitted fan **940**,
`w=11281`, `h=31`, **349,711 cells** — the finding's shape to the cell. The artifact is
**byte-identical across all runs** (2,212,805 bytes), so every run below did identical work.

### 2.2 The reading does not reproduce. 27 runs, **0 over 2 s**

Executor: **me** (`qa-reviewer`), in the mirror, this session.

| Context | n | min | median | max | **over 2 s** |
|---|---|---|---|---|---|
| fresh process, one export each | 9 | 1.342 | **1.429** | 1.617 | **0 / 9** |
| one process, 9 exports in a row | 9 | 1.333 | **1.486** | 1.577 | **0 / 9** |
| inside `pytest`, module alone | 3 | 1.408 | 1.502 | 1.508 | **0 / 3** |
| inside `pytest`, after all of `test_export_state.py` | 3 | 1.561 | 1.599 | 1.662 | **0 / 3** |
| fresh process, **120-char titles** (the reviewer's second family) | 3 | 1.363 | 1.368 | 1.379 | **0 / 3** |
| **all** | **27** | **1.333** | **1.46** | **1.662** | **0 / 27** |

Split of the freeze (3 fresh runs): extent growth **2.3–2.7 ms**, `render` **0.96–0.98 s**,
`save_svg` **0.47–0.54 s**. So no plausible disagreement about *where the timed region starts*
explains a half-second: the growth loop is 0.2 % of the cost, and excluding `save_svg` would make a
reading **lower**, not higher.

### 2.3 The disagreement you flagged — what I can and cannot explain

Three parties, one bit-identical workload:

| Party | n | min | median | over 2 s |
|---|---|---|---|---|
| implementer (reproduction) | 9 | 1.321 | 1.890 | 4 / 9 |
| `code-reviewer` (finder) | 9 | 1.978 | 2.059 | 7 / 9 |
| **this reader** | 27 | **1.333** | **1.46** | **0 / 27** |

**What I ruled out, by measurement:**

- **A different shape.** Ruled out — the bisection is deterministic and lands on 940 / 349,711, and
  the output bytes are identical run to run.
- **The title family.** Ruled out, and more strongly than expected: **titles do not affect the extent
  at all.** 120-character titles give the *same* `11281x31` — node boxes clamp at ~12 columns. The
  title-120 runs were the *cheapest* of my 27. Whatever produced the reviewer's `latin 120` row, it
  was not extra layout work.
- **In-process repetition / warm caches.** Ruled out — repetition moves the median by +4 %, not +40 %.
- **Timed-region boundaries.** Ruled out — see the split above.

**What survives, and I could not close it:** the implementer's *minimum* (1.321) sits inside my band
while their *tail* does not, and the reviewer's *entire distribution* sits above mine. That is the
signature of **machine and session state** — contention, frequency/thermal behaviour, what else the
harness was running — not of a difference in the subject. I ran one context-sensitivity experiment
(same process after a full test module: +10 %) and it is real but an order of magnitude too small.
**I am declaring this `blocked` rather than explained:** closing it needs the other two parties'
machines, and it cannot be settled from here. What matters for the ruling is that it does not need to
be settled — see below.

### 2.4 Verdict on `CR17-F6`, half by half

| Half | My verdict | Basis |
|---|---|---|
| (a) *"the safe side breaches at its own boundary — 7 of 9 over 2 s"* | **NOT REPRODUCED.** 0 / 27 on the same shape, both title families | independent measurement, §2.2 |
| (b) *"'monotonically' is false — it plateaus"* | **REPRODUCED and STRENGTHENED.** Plateau confirmed; its stated **boundary is wrong** and its stated **cause is wrong** — §4.3 | independent measurement + mutation |
| root cause: *"the figure was a MINIMUM reported as a bound"* | **CORRECT, and my data corroborates it from a second direction** | inference + measurement |
| the **conclusion** — strike the sentence, make no fourth time claim | **CORRECT, and my failure to reproduce makes the case stronger, not weaker** | §2.5 |

### 2.5 Why a failed reproduction *strengthens* the strike

The struck sentence claims the worst admitted shape stays under 2 s at start height 30. On my machine
that sentence is **true in every one of 27 trials**. On the reviewer's it is false in 7 of 9. The
sentence therefore does not describe `mapper`; it describes a machine-session. **A sentence whose
truth value flips between two idle Windows machines running identical bytes and producing
byte-identical output has no business being asserted in a ratified requirement in either direction** —
and that is a stronger ground for striking it than "it is false", because "it is false" invites a
fourth attempt at a *corrected* number, which is precisely the loop this family has been stuck in
three times.

**And it corroborates the best-of-N control.** The most reproducible statistic across the three
parties is the **minimum** (1.321 / 1.333 — 0.9 % apart). The tail is the least reproducible (1.617 vs
2.146 — 33 % apart). So quoting a minimum is wrong *twice over*: it cannot bound a maximum, **and** it
is the statistic most likely to look stable across machines, which makes a safety claim built on it
look robust exactly when it is not. That is worth adding to the control.

**Correction owed to the artifact.** `A-100.6` and the docstring both assert the breach as fact
(*"4 of 9 runs exceeded 2 s (min 1.321, median 1.890, max 2.139), and an independent pass measured
7 of 9 with a median of 2.059"*). A third pass measured 0 of 27. The sentence that should stand is
*"the claim did not survive re-measurement, and its refutation did not survive re-measurement either;
both are machine readings"* — see §5.

---

## 3 · Q2 — Is the clockless arm better, or merely different?

**Better. Not vacuous, not tautological in substance, and it is the right shape of assertion.** But it
is **half-blind on the mechanism it names**, and its admitted row is a knife edge.

### 3.1 Mutation battery — seven sites, one arm

Discipline: byte-level I/O; `sha256` pinned before and re-asserted after **every** site; substitution
count asserted **exactly 1** (the anchor `self._view_state(max(20, size.width), max(5, size.height - 10))`
is unique — note that `max(5, size.height - 10)` alone appears **twice** in `app.py`, at `:888` and
`:3859`, so the bare expression is **not** a safe anchor); verdicts printed **before** restore;
`PYTHONDONTWRITEBYTECODE=1`. Executor: **me**. Pin `58443932d615b956…`, **held at the end**.

| Site | Mutation (at `app.py:3859`, the export site) | My prediction | Measured | |
|---|---|---|---|---|
| S0 | comment only on `EXPORT_MAX_CELLS` | survives | **2 passed** | ✓ control |
| S1 | `max(5, …)` → `max(1, …)` — the floor | **miss** | **2 passed** | ✓ predicted miss |
| S2 | `max(5, size.height - 10)` → `max(5, 30)` — terminal-independence | kill `15-True` | **`15-True` FAILED** | ✓ RED-proof |
| S3 | `- 10` → `- 11` | **miss** | **2 passed** | ✓ predicted miss |
| S4 | budget `350_000` → `349_900` (**−0.03 %**) | kill `15-True` | **`15-True` FAILED** | ✓ killed from below |
| S5 | budget `350_000` → `1_400_000` (**+300 %**) | kill `40-False` | **`40-False` FAILED** | ✓ killed from above |
| S6 | `- 10` → `- 9` | kill `15-True` | **2 passed** | ✗ **my prediction was wrong** |

**S6 is the instrument correcting me, and it is the most informative row in the table.** I predicted a
kill because the mutation raises the start height; it survived because at terminal 15 the extent is
**not** terminal-bound at all (see §3.3).

### 3.2 Answers to the three attacks you named

- **Vacuous?** No. The discriminating content is the *raise / no-raise* differential across the
  parameter, and S2/S4/S5 prove it can go red.
- **Tautological?** **The two `assert` lines are, and only they.** `_within_export_budget` raises iff
  `w*h > EXPORT_MAX_CELLS`, so `assert state.w * state.h <= EXPORT_MAX_CELLS` **cannot fail once the
  call returned**, and `assert refused.value.cells > EXPORT_MAX_CELLS` cannot fail once it raised
  (`app.py:3900–3905`). They are decoration over the real oracle. Harmless — but they are also the
  reason the arm never notices *which* map it exported.
- **Killed from both directions?** **Confirmed** (S4, S5) — **and the asymmetry is four orders of
  magnitude.** The admitted row dies on a **0.03 %** budget cut; the refused row needs **+300 %**.
  Quantified on the extent instead: the admitted row holds at 349,928 cells against a 350,000 budget —
  **72 cells of margin, i.e. the layout may widen by 9 columns in total across 3,645 nodes before this
  row reddens.** One extra column per node (+8.3 % width) reddens it. That row will fail for reasons
  that have nothing to do with the terminal, and the failure will be read as "the mechanism broke".

### 3.3 The real defect: the admitted row does not exercise the mechanism

Measured extents for the arm's own fixture (fan 3,645), driving the product:

```
terminal   start h   extent           cells      verdict
118x 9        5      43741 x  8      349,928    admitted   <- identical
118x11        5      43741 x  8      349,928    admitted   <- identical
118x15        5      43741 x  8      349,928    admitted   <- the arm's row
118x16        6      43741 x  8      349,928    admitted   <- identical
118x17        7      43741 x  8      349,928    admitted   <- identical
118x18        8      43741 x  9      393,669    REFUSED    <- the flip
118x40       30      43741 x 31    1,355,971    REFUSED    <- the arm's row
```

**The extent settles at `h = max(8, start + 1)`, and 8 is the map's own content height.** At terminal
15 the start height is 5 — and *nothing in the start-height expression matters*, because the growth
loop lifts it to 8 regardless. That is why S1 (floor `5`→`1`), S3 (`−11`) and S6 (`−9`) all survive:
**the arm's admitted row is insensitive to the entire start-height expression whenever the start
height is ≤ 7.** Only the refused row tests the terminal→start-height link. The arm's own docstring —
*"the export starts at `max(5, size.height - 10)`. A short terminal gives a small `h`"* — is exactly
what the admitted row does **not** demonstrate.

**A mutant it should catch and does not:** S3 and S6 — a one-row error in the very expression the arm
and the requirement both quote. Measured consequence of S6: a map the product admits at terminal 17
today is **refused** after the mutation; of S3: a map refused at terminal 18 today is **admitted**.
Both are user-visible changes to the exact mechanism, and the arm stays green.

**Verified fix, measured rather than proposed.** A boundary pin at the flip — `(17, True), (18, False)`
on the same fixture — reddens under **both** S3 and S6. It holds no clock, costs no runtime, and is
strictly stronger than the shipped pair.

| fixture 3,645 | terminal 17 | terminal 18 | shipped arm (15/40) | boundary arm (17/18) |
|---|---|---|---|---|
| BASE | admitted 349,928 | refused 393,669 | green | green |
| S1 floor `1` | admitted 349,928 | refused 393,669 | green | green (**still blind**) |
| S3 `−11` | admitted 349,928 | **admitted** 349,928 | green — **miss** | **RED** |
| S6 `−9` | **refused** 393,669 | refused 437,410 | green — **miss** | **RED** |

**Neither arm pins the floor of 5** — S1 is invisible to both, and no other arm in the module covers
it either. The requirement leans on that floor explicitly (*"because the start height floors at 5"*),
so it is a mandate nothing reads. If the floor is to be a claim, it needs a fixture whose content
height is **below** 5 at a terminal of ≤ 15; if it is not, the sentence should go (§4.3 — it is wrong
anyway).

### 3.4 A second governing variable the arm inherits by accident: **the view**

The arm never sets the view, so it silently tests the default (`LayeredRenderer`). Measured, same map,
same terminal, driving the product's own `action_toggle_outline` / `action_toggle_radial`:

| map | terminal | view | extent | cells | verdict | export cost |
|---|---|---|---|---|---|---|
| fan 940 | 118x40 | layered | 11281 x 31 | 349,711 | admitted | **1.51 s** |
| fan 940 | 118x40 | outline | 118 x 30 | 3,540 | admitted | **0.015 s** |
| fan 940 | 118x40 | radial | 118 x 30 | 3,540 | admitted | **0.062 s** |
| fan 3,645 | 118x40 | layered | — | 1,355,971 | **REFUSED** | — |
| fan 3,645 | 118x40 | outline | 118 x 30 | 3,540 | **admitted** | — |
| fan 3,645 | 118x40 | radial | 118 x 30 | 3,540 | **admitted** | — |

**The arm's refused row is refused only because the screen happens to be in the layered view.** So
the sentence `A-100.6` ratifies — *"the same map is admitted or refused depending on the operator's
TERMINAL"* — is **incomplete in the same way the three struck sentences were incomplete**: it names
one governing variable and inherits another undeclared. The honest form is *"depending on the
operator's terminal **and the view they are in**"*. The arm should **set the view explicitly** rather
than inherit it, whichever way the ruling goes.

> **Adjacent, out of my scope, flagged not claimed.** In outline and radial the export extent is the
> **viewport** (118x30) for a map of any size, so the budget can never refuse in those views. Whether
> the resulting artifact is therefore *cropped* — which would be `B-68`'s own defect class — I did
> **not** establish: my text-matching instrument returned 0 title matches even on the layered
> artifact, so it cannot discriminate, and I am reporting it as an instrument failure rather than as a
> finding. This needs its own reader.

---

## 4 · Q4 — Does the docstring claim anything else that is false? **Yes. Two more, plus a wrong cause**

### 4.1 The heap sentence is false by 14.6× — and it is the same error on the memory axis

> *"Time is what binds, not memory: peak heap fits **18.9 bytes/cell**, so the whole budget below
> costs **about 7 MB**."* — `app.py`, the `EXPORT_MAX_CELLS` block

Measured with `tracemalloc` around `render` + `save_svg`, **in a run that reads no clock at all**
(set 9's instrument defect made impossible by construction), peak minus baseline. Executor: **me**.
Deterministic — the 3,645 row reproduced to the byte on two runs.

| shape (admitted) | cells | render peak | **total peak** | **bytes/cell** | SVG |
|---|---|---|---|---|---|
| fan 940 @ `118x40` | 349,711 | 15.0 MB | **28.5 MB** | **81.5** | 2.21 MB |
| **fan 3,645 @ `118x15`** — *the arm's own admitted fixture* | 349,928 | 51.8 MB | **102.3 MB** | **292.3** | 8.53 MB |
| fan 161 @ `118x34` | 48,325 | 2.3 MB | 4.8 MB | 99.1 | 0.38 MB |

**102.3 MB against a claimed ~7 MB, on a shape this budget admits and this very arm asserts is
admitted.** And the per-cell rate spans **81.5 → 292.3 B/cell at the same cell count** — a 3.6×
spread driven by density, which is *precisely* the reason the docstring gives, eight lines earlier,
for why no per-cell **time** rate may appear: *"cost per cell tracks NODE DENSITY, not area, so a
single rate cannot derive a cell budget in either direction."* The heap rate was left standing as the
one surviving per-cell constant in a block whose whole thesis is that per-cell constants do not exist
here. **It is the fourth claim of the same family, one axis over.**

The *qualitative* claim survives and should be kept: 102 MB is not a binding constraint, so
*"time is what binds, not memory"* stands — **without a figure**, exactly as the µs/cell span was
handled.

### 4.2 *"WHAT THAT REFUSES, stated rather than discovered"* is stated without its terminal — and one row inverts

The list reads as a property of maps. It is a property of `(map, terminal)`. Measured:

| docstring row | at `118x34` | at `118x67` | at `118x68` |
|---|---|---|---|
| *"a 500-wide fanout (**150,025**) … exports"* | admitted, **150,025 cells — matches the docstring exactly** | admitted, 348,058 | **REFUSED, 354,059** |

The exact match at `118x34` identifies the undeclared terminal the whole list was measured on. **At
terminal height 68 and above the same 500-wide fanout is refused** — and 68 rows is an unremarkable
maximised window. The chain rows (200-long, 1,000-deep) are content-bound and terminal-insensitive;
the **fanout** rows are the exposed ones, including the `161 / 201` wide-and-deep boundary the block
calls *"MEASURED rather than interpolated"*. (I did **not** reconstruct the `161`/`201` fixture — the
node counts are ambiguous between "161 total" and "161 each way", and I will not refute a claim whose
fixture I had to guess. It is stated with the same undeclared terminal and is exposed to the same
inversion; that much is structural.)

This paragraph sits **twenty lines below** the paragraph that mints the lesson. The fix is one
clause: name the terminal each row was measured on, or state the list as *"at a 34-row terminal"*.

### 4.3 The plateau is real; its stated **cause** is wrong and its stated **boundary** is wrong

> *"'Monotonically' is false because the start height **FLOORS at 5**: every terminal **at or below 15
> rows** admits the identical shape (fan 3,645, measured at 15, 12 and 11 rows)."*

Measured (§3.3): the identical shape is admitted at terminal heights **9, 11, 15, 16 and 17** — the
plateau runs to **17**, not 15 — and the reason is that the extent settles at `h = max(8, start + 1)`
where **8 is the map's own content height**. Proven by mutation: with the floor changed `5 → 1` (S1)
the shape at terminals 11 and 15 is **unchanged** (43741 x 8, 349,928). **The floor of 5 does no work
here.** The plateau would exist with any floor ≤ 7.

So the third strike's own replacement explanation misattributes the mechanism. The true sentence is
clockless, shorter, and pins something an arm can hold: *the export extent never falls below the map's
own content height, so every terminal short enough to ask for less admits the identical shape.*

### 4.4 *"the reason no number of any kind now appears"* — not accurate as written

`A-100.6` says the third strike is *"the reason no number of any kind now appears"*, and *"What
replaces it: nothing numeric, deliberately."* The **replacement claim** is indeed clockless and that
is right. But the surrounding strike carries `4 of 9`, `1.321`, `1.890`, `2.139`, `7 of 9`, `2.059`,
`18.9 s / 21.0 s / 18.9 s` — asserted as measurements, with no machine, no statistic policy and no
reviewer named, in the same document that has now been wrong about a measured number three times.
**I failed to reproduce the first group by a wide margin** (§2.2). They are evidence *for* a strike,
which is a legitimate use — but they are readings, and they should say so.

---

## 5 · Q3 — "Stop producing numbers", or `IRREDUCIBLY A READING`?

**I would have chosen both, in that order, and I think the either/or framing is the mistake.** They
answer different questions.

- **For the normative claim** — what the requirement asserts and the suite may enforce — **"stop
  producing numbers" is right, and my data is the strongest argument for it yet produced.** Three
  parties, bit-identical work, byte-identical artifacts: 0/27, 4/9, 7/9 over the threshold. The
  2-second boundary sits *inside the between-machine variance*. A number that flips its own verdict
  between two idle Windows boxes is not a property of the artifact, and no amount of statistical care
  fixes that — an upper quantile on *my* machine would have ratified the struck sentence. **Declaring
  it a reading would not have been enough**, because the docstring's readers are developers on other
  machines, and a faithfully-attributed reading from a machine you do not have is still unusable as a
  boundary. So this is **not** giving up: it is the correct scope for the claim. The clockless
  mechanism is a real assertion, it is stronger than any timing sentence could be (it is exact, and it
  is *why* no timing sentence can work), and it is enforced by an arm.
- **For the residual evidence** — the figures the strike itself carries — **`IRREDUCIBLY A READING`
  is owed and was skipped.** It costs one clause per figure. Had the finder's 7/9 been recorded as a
  reading with machine and `n` named, this second reader's 0/27 would be a second reading rather than
  a contradiction, and nothing in the artifact would need correcting now.

**Where "stop producing numbers" was applied too narrowly:** it was applied to the *time* axis only.
The heap figure (§4.1) and the terminal-scoped export list (§4.2) are numbers of exactly the same
kind, in the same docstring block, and they survived the third strike untouched. A rule that stops at
the axis where the last three defects happened to land will be defeated by the fourth.

---

## 6 · What I did NOT run

| Not run | Why | State |
|---|---|---|
| **the full default lane** | the orchestrator owns the ONE complete gate-suite run (`C-25`). I ran `tests/test_export_state.py` (**22 passed**, executed by me) and the arm under seven mutations | `not-run` |
| slow / network / lint lanes, `ruff` | out of scope; no bytes changed | `not-run` |
| the finder's own shape-hunt across terminals | deliberately — I was asked to build my own counterfactual, not to re-run theirs | `n/a — by instruction` |
| the `161`/`201` wide-and-deep boundary rows | the fixture is ambiguous in the docstring; I will not refute a claim whose fixture I guessed | `blocked` |
| whether outline/radial exports are **cropped** | my text-matching instrument returned 0 matches on the control artifact — instrument RED, so no verdict | `blocked` |
| the cause of the three-party magnitude gap | needs the other two machines | `blocked` |
| `FLAKE-1`, `.gitattributes`, `SEC-F4`, socket guard, `B-64`, `UX-F7b`/`UX-HINT1`, `SEC-H2`, `CR17-F3`/`F5`, `S-F3`/`S-F5` | out of scope, carried | `n/a — out of scope` |
| whether 350,000 is the right constant | a ruling, not a review call | `n/a — coordinator` |

---

## 7 · Recommendations — **I authorise nothing; `software-dev` implements, the coordinator rules**

Ordered by what I would do first.

1. **Correct `A-100.6`'s and the docstring's reason for striking half (a).** Not *"the safe side is
   false"* but *"the safe side is a machine reading: 0/27 under, 4/9 over and 7/9 over on three
   machines running byte-identical work."* Mark the residual figures `IRREDUCIBLY A READING` with
   machine, statistic and `n`. **The strike itself stands** — strengthened.
2. **Fix the heap sentence** (§4.1). Measured 102.3 MB / 292 B/cell on the shape the arm admits vs a
   claimed ~7 MB / 18.9 B/cell. Keep *"time is what binds, not memory"*, drop the figure, exactly as
   the µs/cell span was handled. **This is the fourth claim of the family and it is still standing.**
3. **Name the terminal on the "WHAT THAT REFUSES" list** (§4.2), or state the list as measured at
   `118x34`. One row (500-wide fanout) inverts at terminal 68.
4. **Correct the plateau's cause and boundary** (§4.3): the extent floors at the map's **content
   height** (8 here), not at the start height's floor of 5; the plateau runs to terminal **17**.
   Proven by mutation S1.
5. **Strengthen the arm to a boundary pin**: parametrise `(17, True), (18, False)` — measured to
   redden under S3 and S6, which the shipped `(15, True), (40, False)` misses. Keep the 15/40 pair if
   desired; it is the readable illustration, the 17/18 pair is the oracle.
6. **Set the view explicitly in the arm** (§3.4), and widen `A-100.6`'s mechanism sentence to name the
   view alongside the terminal.
7. **Optional, and I would not hold a gate for it:** replace the two tautological `assert`s with
   assertions that carry content — that the two rows share the same `w` and differ only in `h`, which
   is the mechanism in one line.

---

## 8 · Evidence states

| Item | State | Executor |
|---|---|---|
| mirror aggregate `7e582edd…`, pre and post | `approved` | me |
| mirror-vs-repo parity (43 files, line endings only, 0 content) | `approved` | me |
| brief's line-ending table for `test_export_state.py` | **`failed`** — mirror is CRLF, brief says LF | me |
| shape reproduction (940 / 11281x31 / 349,711 @ `118x40`) | `approved` | me |
| 27 timing runs, 5 contexts | `executed` — 0/27 over 2 s | me |
| `CR17-F6` half (a) — the boundary breach | **`failed` to reproduce** | me |
| `CR17-F6` half (b) — the plateau | **`approved`**, and its stated cause/boundary `failed` | me |
| `CR17-F6` root cause (best-of-N) | **`approved`**, corroborated from a second direction | me |
| `CR17-F6` conclusion (strike; no fourth number) | **`approved`** | me |
| 7-site mutation battery, `sha256` held, restores byte-identical | `executed` — 7/7, control survived, RED-proof at S2 | me |
| "killed from both directions" | **`approved`** — and the asymmetry quantified | me |
| boundary-arm counterfactual (17/18 under S1/S3/S6) | `executed` | me |
| view-dependence of admission and cost | `executed` | me |
| heap measurement (two shapes, reproduced) | `executed` | me |
| fourth false claim — heap figure | **`failed`** (the claim is false, by 14.6×) | me |
| fifth — terminal-scoped export list | **`failed`** (false at terminal ≥ 68) | me |
| full default lane | `not-run` — orchestrator owns it (`C-25`) | — |
| `tests/test_export_state.py` module | `executed` — 22 passed | me |
| outline/radial crop question | `blocked` — instrument RED | me |
| three-party magnitude gap | `blocked` — needs the other machines | me |

### Evidence checklist

- [x] **Mode declared** — `validation`, at the top.
- [x] Every item carries a result or one of the seven states; every executed result **names its executor**.
- [x] **No claim of personal execution of a run I consumed.** Every number in §2–§4 was produced by me in the mirror this session. I consumed nothing from the pass-2 report except the claims under audit.
- [x] Predictions treated as claims and **measured** — S6 refuted my own prediction and is reported as such.
- [x] **Instrument shown RED before a PASS was believed** — S2 and S4/S5 redden the arm; the control S0 survives; the text-matching probe was declared RED and its finding withheld.
- [x] Probes **drive the derived set** (`_export_view_state`, `_current_renderer().render`, `action_toggle_*`) — no hand-built model of the growth loop. The rewrite the brief asked me to check **did** fix that: the shipped arm calls `screen._export_view_state(size)` and replays nothing.
- [x] Digests pinned before and after; restores byte-identical; verdicts printed before restore asserts; substitution count asserted exactly 1 per site; `PYTHONDONTWRITEBYTECODE=1`.
- [x] Trap 1 asserted **and printed** in every ad-hoc probe; trap 2 respected.
- [x] No file in the repo modified except this report (`git status` clean).
- [x] No real PII, credentials or client data — all fixtures are synthetic.
- [x] Exit criteria and what I did not run are both stated.

**Independence declaration.** I authored none of the diff, none of `CR17-F6`, and none of its remedy;
I did not read the finder's counterfactual method before building mine, and my design (fix the shape,
vary the measurement context) is not theirs (vary the shape, fix the context). **I reproduced
`CR17-F6` independently, not by re-reading it** — with the result that one half reproduces and is
strengthened, one half does not reproduce at all, and the conclusion stands on better ground than the
one given. **This report authorises nothing.**
