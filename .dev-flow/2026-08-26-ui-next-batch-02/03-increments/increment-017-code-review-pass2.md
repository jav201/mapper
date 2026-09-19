# Code Review — Increment 017, PASS 2 · re-read of the `CR17-F1` / `CR17-F2` fixes

| Field | Value |
|---|---|
| Reviewer | `code-reviewer` (independent; authored none of this diff) |
| Batch | `2026-08-26-ui-next-batch-02` |
| Commit reviewed | **`344db11`** (`A-100.4` / `A-100.5`). Source at `2c74347` is identical — only docs moved after |
| Pass 1 | `increment-017-code-review.md` (verdict BLOCK, 1 HIGH) |
| Date | 2026-09-19 |
| **Verdict** | **OK to advance — no HIGH open.** `CR17-F1` **CLOSED** and `CR17-F2` **CLOSED**, both verified by me on the shipped bytes. **One new MEDIUM (`CR17-F6`) opens** on the sentence that replaced the struck universal |

> **This verdict authorises nothing by itself.**

---

## 1 · Mirror and digests — every digest HELD

Fresh mirror `…\scratchpad\mirror-cr017p2`, filesystem copy, verified byte-exact against the repo:

| File | sha256 (repo == mirror) |
|---|---|
| aggregate over all 92 `.py` in `mapper/`+`tests/` | `3d90c32a931d707b37585e04334b767388d78055c817866731447778af0a81b3` |
| `mapper/app.py` | `3335d63a0ac43610ef8920f0…` |
| `mapper/export.py` | `56773345bc4731f1e009ec57…` |
| `tests/test_export_state.py` | `cbc230c2ba9e8150c814cdf0…` |

The aggregate was **unchanged after `git init`** and after the battery; all three sites restored
byte-identical with sha256 re-pinned. Trap 1 defended in every probe (`mapper.__file__` asserted and
**printed** inside the mirror). Repo `git status` clean apart from my two report files.

**Source parity established before measuring**, since HEAD had moved past the fix:
`git diff 344db11 2c74347 -- mapper/ tests/` is **empty**, so the working tree I copied *is* the fix
commit's source. I also pinned, by extracting the functions and stripping comments, that
`_export_view_state` and `_within_export_budget` are **byte-identical** across `152ecd9` and
`344db11` (`1fc22b02…`, `ed42f4b5…`) — which is what licensed me to reuse an idle earlier mirror for
the variance probe.

---

## 2 · `CR17-F1` — **CLOSED.** Verified on the shipped bytes

The remedy is the one I recommended as option (a), and it was applied in **both** places pass 1 cited
— not only the docstring:

- `mapper/app.py:3613–3672` — the universal is quoted verbatim, named `THE UNIVERSAL IS FALSE`, the
  mechanism (`max(5, size.height - 10)` as the governing variable) is stated, the five-terminal table
  is carried, and the constant is explicitly re-grounded on **utility alone**.
- `01-requirements.md` — `A-100`'s normative clause **and** amendment set 9's *"What replaces it"*
  paragraph both carry a ⚠ strike pointing forward to amendment set 10. This matters: pass 1's finding
  was against the *requirement*, and a docstring-only fix would not have closed it.
- The `0.955–3.27 µs/cell / 3.4x` span is struck too, with the qualitative claim retained and
  explicitly stated **without a figure** — the right call.

The implementer's reproduction agrees with mine to within a few percent, and the diagnosis is
recorded accurately as `C-31` at the **search** rather than the instrument. I confirm the strike is
faithful: the false sentence is removed, quoted where it is named false, and not left standing beside
its replacement for a reader to average.

## 3 · `CR17-F2` — **CLOSED.** Verified on the shipped bytes and by battery

The sentence now reads *"No se escribió nada: el archivo en {path} es de una exportación anterior."* —
the false half (*"ya no refleja este mapa"*) is gone.

New arm `test_a_refusal_does_not_call_a_CURRENT_artifact_stale` isolates the condition with
`screen.EXPORT_MAX_CELLS = 1` rather than reproducing my terminal-resize route. **That is a better
choice than mine** — it holds the graph fixed and changes only the budget verdict, so the arm cannot
break if the height arithmetic changes.

### Battery — independently reproduced, 3 sites

Byte-level I/O, sha256 pinned, anchors asserted **exactly 1x**, verdict printed **before** restore,
full default lane per site. `test_fold::…INCLUDING_the_artifacts` fails in **all three including the
control** — my constant mirror artifact — so the differential is clean.

| Site | Mutation | Predicted | KILLED (differential) | Verdict |
|---|---|---|---|---|
| P2-A | restore the false staleness claim | only the new arm | `test_a_refusal_does_not_call_a_CURRENT_artifact_stale` | ✓ exact |
| P2-B | suppress the sentence (`if False`) | only the declaration arm | `test_a_refusal_DECLARES_the_stale_artifact_it_leaves_behind` | ✓ exact |
| P2-C | comment-only control | SURVIVES | nothing | ✓ survived |

Default lane at `344db11`: **1143 passed**, 20 deselected, 3 xfailed (+1 constant mirror artifact).
`FLAKE-1` did not fire in any of the four full-lane runs.

---

## 4 · `CR17-F6` — NEW. The sentence that replaced the universal is wrong on both halves [Severity: **MEDIUM**]

> This is the claim I was explicitly asked to attack, so it got the same treatment as the last one.

**The claim**, carried identically in `mapper/app.py:3660–3663` and in `01-requirements.md`'s amended
`A-100` clause:

> *"at start heights of about 30 rows and up, the worst admitted shape stays under 2 s. Below that it
> rises monotonically as the terminal shortens."*

### (a) The safe side is false at its own stated boundary — **on the claim's own title family**

I first varied the **title**, since the boundary was established on narrow-title fanouts only, and
found a breach at start height 30 with 120-character titles (2.051 s). Then I checked *how much
margin* there is, and the real finding is worse than the title effect:

At **start height 30** (terminal 118x40), max admitted fan 940, 349,711 cells — **n = 9 runs each**,
artifact hash-stable:

| Title | min | median | max | runs **over 2 s** |
|---|---|---|---|---|
| **narrow (`hoja {}`) — the claim's own family** | 1.978 | **2.059** | 2.146 | **7 / 9** |
| `latin 120` | 1.391 | **2.022** | 2.106 | **6 / 9** |

At start height 32 (terminal 118x42) it is genuinely under — 0/9 over, max 1.968 — but with only a
**2–6 % margin**.

**So the honest boundary is ~32, not ~30, and even there the margin is inside the noise.**

### (b) The methodological cause, and it generalises

My own pass-1 table reported `118x40 → 1.803 s` as *best of 3*. The increment reports `1.91 s`. Both
are **minima** — and the median at that shape is **2.06 s**. A *best-of-N* statistic is the wrong tail
for a safety claim:

> **Best-of-N is the correct statistic for demonstrating a BREACH and the wrong one for demonstrating
> SAFETY.** If the minimum exceeds the bound, every run does — so pass 1's HIGH stands *a fortiori*.
> If the minimum is under the bound, nothing follows about the others. A worst-case claim must be
> established on an upper quantile.

This is the same family of error one level further in: set 9 fixed the **instrument**, set 10 fixed
the **search**, and what is left is the **statistic**.

### (c) "Monotonically" is false — it saturates

Measured, narrow titles, worst admitted shape per terminal:

```
term 39 (start 29)  2.244 s      term 21 (start 11)   8.559 s
term 36 (start 26)  2.463 s      term 18 (start  8)  14.877 s
term 33 (start 23)  2.750 s      term 15 (start  5)  14.772 s   <- fan stops growing
term 30 (start 20)  2.807 s      term 12 (start  5)  14.798 s
term 27 (start 17)  4.431 s      term 11 (start  5)  20.038 s
```

Because the start height **floors at 5**, every terminal of height ≤ 15 admits the *same* shape
(fan 3,645, 349,928 cells). The curve rises steeply and then **plateaus**; it does not rise
monotonically. Note also the spread across three runs of an *identical* shape — 14.77 / 14.80 / 20.04 s
— which is the variance point again.

### Why I am **not** calling this HIGH

Pass 1's `CR17-F1` was HIGH because the false universal was the constant's *only* justification and
therefore disarmed the gate it was routed to. That is no longer true: the constant rests on utility,
the time guarantee is withdrawn in terms, and the document explicitly routes the real fix forward
(*"needs a different bound, and that is a ruling rather than a constant"*). Nothing now decides on
this sentence. It is a false descriptive aside in a ratified requirement — worth correcting before the
whole-branch gate, not worth blocking the increment.

### Suggested fix

Delete the two-sentence boundary claim, or restate it with its statistic and its shape:

```
#: WHAT IS TRUE, WITH ITS BOUNDARY AND ITS STATISTIC: measured as a MEDIAN over
#: 9 runs (a minimum cannot support a safety claim), the worst admitted shape is
#: over 2 s at start height 30 and under it from about 32 up, with a margin of
#: only 2-6% there.  As the terminal shortens the cost rises steeply and then
#: PLATEAUS, because the start height floors at 5: every terminal of height <= 15
#: admits the same 3,645-wide shape.  These figures are one machine's readings.
```

---

## 5 · Answer to the direct question — is recommendation (c) owed before merge?

**Not as a timing arm. I withdraw that half of my own pass-1 recommendation, and my new data is why.**

An arm asserting *"the worst admitted shape stays under 2 s"* would be wrong on three counts:

1. It would assert a property the code **explicitly no longer promises**. The time guarantee is
   withdrawn; an arm re-asserting it would put the guarantee back in the suite after the requirement
   removed it — the suite and the requirement would then disagree.
2. It would be **flaky by construction**. At the boundary I measured 1.978–2.146 s across 9 runs of
   identical work on one idle machine. Any threshold arm there fails intermittently; on shared CI,
   worse.
3. It would pin a **machine-dependent** number, which the batch already lists as a carried concern.

**What I do consider owed is something clockless**, because the docstring still carries a measured
table and a boundary sentence that nothing mechanical reads — and this claim family has now been wrong
three times (`VIGILANCE IS NOT A CONTROL`; *a mandate nothing reads is a paragraph*). Two options,
either of which discharges it:

- **(i) The mechanised half — pin the MECHANISM, not the clock.** Deterministic, no timing:

  ```python
  def test_the_cell_budget_admits_unbounded_width_as_the_start_height_FLOORS():
      """`CR17-F6`: why a cells-only budget cannot bound the freeze.

      The budget constrains w*h; the start height is `max(5, size.height - 10)`
      and is set by the TERMINAL.  So the shorter the terminal, the WIDER the map
      the same constant admits -- and width is what costs.  Pinned with no clock,
      so it cannot flake and cannot rot into a machine-dependent threshold.
      """
      # the same 3,645-wide fanout: ADMITTED at start height 5, REFUSED at 30
  ```

  This fails the moment someone adds a second bound — which is exactly when you want to be told, and
  it is the arm that would have caught `CR17-F1` before it shipped.

- **(ii) Or declare the sentence `IRREDUCIBLY A READING`** in the batch's own second category, with the
  machine, the statistic and `n` named, and a declared reviewer. That is honest and costs nothing.

**I would not hold merge for (i)** — but I would hold the *whole-branch gate* for one of (i) or (ii)
plus the `CR17-F6` wording fix, because an uncorrected false sentence in a ratified requirement is
precisely what the STRIKE control exists to prevent.

---

## 6 · Carried from pass 1 — surfaced, not fixed, as the implementer stated

| Finding | State | Note |
|---|---|---|
| `CR17-F3` export path spelled twice (`app.py:3504`, `:3548`), agreement unpinned | open, MEDIUM | unchanged; still no arm catches a drift |
| `CR17-F4` `path.exists()` | open, LOW — **sharpened** | see below |
| `CR17-F5` `pathlib.Path(root or …)` (`test_hermetic.py:118`) | open, LOW | unchanged |

**`CR17-F4`, sharpened.** The fix's stated principle is that the sentence *"now says only what
`exists()` licenses"*. Strictly it does not: `exists()` licenses *"there is something at this path"*,
while the sentence still asserts *"es de una **exportación** anterior"* — that an export wrote it. A
directory, or a file the operator placed there, is described as a previous export. This is the same
guard-vs-sentence category as `CR17-F2`, two orders of magnitude smaller in consequence, and I raise
it only because the fix invoked that exact principle. **It does not block and I would not spend a
round on it**; if it is ever touched, *"hay un archivo en {path} de una exportación anterior"* → *"hay
un archivo en {path}"* closes it.

**Nit (not a finding).** *"No se escribió nada"* is unconditionally true on this path but is only
emitted when a file exists — so on a first export the operator is never told nothing was written.
Harmless; noted only so the asymmetry is a decision rather than an accident.

---

## 7 · What I did NOT run

| Not run | Why |
|---|---|
| **ruff** | not executed in either pass. Still unverified by me |
| slow / network lanes at `344db11` | ran at `152ecd9` in pass 1 (19 / 1 ✓); the fix touches no code they reach |
| `SEC-H2` (`_ConfirmScreen markup=False`, `darkside.plain`) and `tests/test_confirm_markup.py` | **never reviewed by me, in either pass.** It rode in on the same commit range and is squarely `security-reviewer`'s lane |
| base-lane arithmetic at `4800906` | unchanged from pass 1 |
| `CR17-F3`/`F4`/`F5` fixes | none were made; nothing to verify |
| whether 350,000 is the right constant | a ruling, not a review call |

---

## 8 · Verdict

- [x] **OK to advance** — no HIGH open. `CR17-F1` and `CR17-F2` are **CLOSED, applied AND verified by
      me on the shipped bytes**, not from a report that a corrective pass ran
- [ ] `BLOCK-UNTIL: …`
- [ ] Block

`CR17-F6` (MEDIUM, new) + `CR17-F3` (MEDIUM) + `CR17-F4`/`F5` (LOW) remain open and block nothing. I
recommend `CR17-F6`'s wording fix plus one of §5(i)/(ii) **before the whole-branch gate**, not before
this merge.

**Independence declaration.** The `CR17-F1` remedy is option (a) from my own pass-1 report, so my
independence on *that line* is structurally weaker — I am reviewing a change shaped by my own
recommendation. What discharges it is evidence I did not author: the **strike is verifiable as a
textual fact** (the universal is absent and quoted-as-false in both locations, which I checked
directly), and the `CR17-F2` closure rests on a battery whose arm the implementer wrote and whose
mutation I chose. For `CR17-F6` I am the sole finder, so it owes a second reader before it is
actioned — I am not the right person to also ratify my own §5 recommendation.

### Evidence states

| Item | State |
|---|---|
| fix diff read in full (`046acea..344db11`) | `executed` |
| mirror digests (`3d90c32a…`), pre/post | `approved` |
| source parity `344db11` == `2c74347` | `approved` |
| default lane at `344db11` | `executed` — 1143 passed |
| 3-site battery | `executed` — 3/3, restores byte-identical |
| `CR17-F1` closure | **`approved`** — verified on shipped bytes, both locations |
| `CR17-F2` closure | **`approved`** — verified on shipped bytes + battery |
| new boundary claim | **`failed`** — `CR17-F6`, refuted on both halves |
| recommendation (c) | `n/a — withdrawn as a timing arm; replaced by §5(i)/(ii)` |
| ruff | `not-run` |
| `SEC-H2` | `n/a — security-reviewer` |
