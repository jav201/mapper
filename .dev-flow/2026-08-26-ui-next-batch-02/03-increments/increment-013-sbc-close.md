# Increment 013 — Inc-REPAIR stage S-B(+C) — CLOSE

**Stage:** Inc-REPAIR S-B(+C). **Carried verdict:** confirmation pass 3b **RATIFIED**.
**Independent review of this fold:** **APPROVED WITH FINDINGS**, no HIGH
(`increment-013-sbc-fold-review.md`).
**Close shape:** STAGE-COMMITTED per `p3_progress.close_shape`.

---

## 1. What changed

Two folds, in order: pass 3b's five findings, then the independent review's five.

### Fold 1 — confirmation pass 3b (`F13`–`F17`)

| finding | sev | disposition |
|---|---|---|
| `F13` | MED | `B-53` id collision → re-id'd `B-62`, derived mechanically |
| `F14` | MED | the seventh site — **and an eighth and ninth, found by censusing the axis** |
| `F15` | MED | a FALSE mechanism claim in the arm's own docstring — replaced, re-measured |
| `F16` | LOW | stale present-tense "currently unarmed" corrected |
| `F17` | LOW | 136-char line re-wrapped (longest line in the four `.py` files is now 97) |

**The brief named three of these; the ratified artifact names five.** Coordinator ruling
2026-09-18 (A) confirmed the artifact governs: *a summary of a record does not outrank the
record.*

### Fold 2 — the independent review (`F18`–`F22`)

All five are **narration that outran measurement, in the commit convened to stop exactly
that**. None is a defect in the requirement or in any oracle.

| finding | sev | disposition |
|---|---|---|
| `F18` | MED | the `B-62` row I authored FUSED two measurements of two different inputs — `F15`'s own species. Replaced with figures re-derived here |
| `F19` | MED | the `RE_ID` note called its census "257 tracked files"; it is an rglob over files ON DISK, and it had to be — the document holding `B-62`'s only occurrences is untracked |
| `F20` | MED | the note argued against `B-63` **by spelling it into the registry the census reads**. Literal removed; `B-63` burned |
| `F21` | MED | the axis census stopped one site short of its own criterion without recording the exclusion — see §4 |
| `F22` | LOW | an unreproducible absolute scratchpad path in a tracked artifact, replaced by a description of the probe |

### Fold 3 — coordinator rulings 2026-09-18

- **(B) The two id registries are MERGED into one space.** Four live-vs-live collisions
  (`B-49`, `B-50`, `B-51`, `B-52`) plus the already-resolved `B-53`. Older entry keeps its
  number; younger reassigns to the end; a retired number is never reused. One-time mapping
  table at `p3_progress.id_space_merge`.
- **(D) `V7` recorded as an EXTERNAL block**, explicitly not green, with its honest scope.
  `C-45` PULL deferred to a post-merge increment. Both at `p3_progress.external_blocks`.
- **The AGREE-1 floor entry was STALE** — it read "NOT DECIDED HERE" for a clause ruled and
  shipped at `fdabc8d`. Corrected to decided-and-armed with the citation.

---

## 2. Files modified

| file | kind | change |
|---|---|---|
| `mapper/views/layered.py` | **SOURCE (1)** | docstring only |
| `tests/test_fold.py` | test | comment, assertion message, re-wrap |
| `tests/test_inc3_census.py` | test | assertion message, docstring |
| `tests/test_darkside_budget.py` | test | `F15`, `B-62`, benign-source property |
| `.dev-flow/.../01-requirements.md` | doc | `F16`, `B-62` row, `F18` |
| `.dev-flow/state.json` | doc | renumber, mapping table, external blocks, AGREE-1 |

**SOURCE files: 1** (cap 4). Tests and `.dev-flow/**` outside the count per `C-47`.
**Executable delta: ZERO**, re-derived independently by the reviewer.

---

## 3. The axis census, and the site deliberately EXCLUDED (`F21`)

`F14` was applied as a census over its axis rather than as the charged instance (`C-65`).
The axis: *sentences asserting the coercion fixed point is the load-bearing property.*
Pass 3b charged **three**. The census finds **six**. Five were corrected; **one was
considered and excluded, and this section is the record of that exclusion** — its absence
from the first packet is `F21`, and an unrecorded exclusion is indistinguishable from an
oversight.

| # | site | disposition |
|---|---|---|
| 1 | `tests/test_fold.py` comment | corrected (charged) |
| 2 | `tests/test_fold.py` live assertion message | corrected (charged) |
| 3 | `tests/test_inc3_census.py` live assertion message | corrected (charged) |
| 4 | `mapper/views/layered.py` production docstring | corrected (**uncharged**) |
| 5 | `tests/test_inc3_census.py` function docstring | corrected (**uncharged**) |
| 6 | `mapper/views/outline.py:228-230` + `:244` | **EXCLUDED — see below** |

**Why sites 4 and 5 were owed.** `git blame`: site 4's paragraph was written by `278fd36`
(this batch's fold) and the contradicting sentence eleven lines above it by `ce294f1` (the
re-ruling) — **the re-ruling commit manufactured the self-contradiction and left it in
production code.** Correcting it finishes `ce294f1` rather than widening scope. Site 5 is
`21809fd`, same batch, same day. Neither edit leaves this batch's own footprint.

**Why site 6 is EXCLUDED, on the merits.** `outline.py:229` reads *"That — the title path
being coerced AT ALL — is the load-bearing property here"*, and `:244` in the same block
reads *"The ordering clause is normative."* That is the adjacency the criterion names, so
the census must account for it. It is **not** a sixth substitution claim: its referent is a
**different axis** — *coerced at all* vs *not coerced at all*, the `B-47`/`A-89` finding
that this renderer coerced nothing and wrote non-well-formed XML — and `"here"` scopes it to
the routing decision, not to `LLR-COERCE.2`'s two conjuncts. Rewriting it would assert
something false about what that comment is for. **Excluded deliberately; not missed.**
The independent reviewer reached the same ruling on the merits independently.

---

## 4. Evidence — every figure `executed`

| gate | result |
|---|---|
| default lane | **1080 passed, 19 deselected, 3 xfailed**, exit 0, 309.55 s |
| slow lane | **19 passed, 1083 deselected**, exit 0, 54.07 s |
| ruff, project config | **27** — baseline 27, unchanged |
| ruff, `--isolated` | **27** |
| ruff SET, `--isolated` both sides, HEAD vs now, per file | **unchanged on all four `.py` files** |
| signed-balance ledger | `1080 − 0 + 0 = 1080`; observed **1080**. MATCH |
| `state.json` parse guard | OK after every write |

`FLAKE-1` did not fire. The reviewer independently reproduced 1080/19/3 at 302.33 s and
27/27.

### Instrument RED-proof (`C-57`) — no verdict above rests on an unfired instrument

| instrument | known-bad input | reported |
|---|---|---|
| executable-delta AST | `== 10` → `== 11` in an assert | **DETECTED** |
| ruff SET comparator | injected unused local | **DETECTED** |
| `F15` re-derivation | `darkside.fit` forbidden-order twin | **114/160 breaches** |
| `F18` CJK measure | ASCII of equal length | **ratio ≤ 1.0, never breaches** |
| radial AGREE-1 sweep | outline, the known-present case | **52 disagreements** |
| PAN-1 probe | layered at (40,20) | **picture moves** |
| collision census | runs both directions | intersection + each exclusive set |

**Three of my own probes failed their controls first and their results were discarded, not
reported:** the `F15` twin post-composed `plain` over a function that already coerces; the
first PAN-1 probe used lowercase keys; the first radial grid started at width 24 and
structurally excluded its own subject.

### `F15` and `F18` re-derived, never inherited

`F15`: **0 of 160** forbidden-order `_clip` outputs breach their code-point budget, all 160
byte-identical; `darkside.fit` breaches **114 of 160**. Denominator 160 (4 hostile sources ×
widths 1..40), not pass 3b's 120 — the docstring carries the number actually measured here.
The reviewer reproduced 0/160, 160/160 and 114/160 exactly, by a different mechanism
(in-process neutralisation of `plain`), with a control proving the neutralisation reached
`_clip`.

`F18`: driven against the shipped `_clip`, each ratio from the same output as its cell count
— 16 code points at budget 20 → **32 cells, 1.60×, uncut**; ≥21 → **39 cells, 1.95×**;
budget 2 → **3 cells, 1.50×**. The row's old "32 cells (1.9×)" fused the first figure with
the second's ratio.

---

## 5. What this close does NOT claim

- **`V7` is not green.** The validator exits 1. Recorded as an external block with its
  honest scope: the bundle's file-table integrity PASSED; only its revision label is
  inconsistent. It cannot move a measurement taken under the pinned `rev46+` baseline.
- **The executable-delta instrument is blind to everything this fold changed.** The reviewer
  constructed the blind spot rather than asserting it: rewriting a new assertion message
  from "WEAKER conjunct" to "LOAD-BEARING conjunct" — injecting back the exact refuted
  framing — was reported **IDENTICAL**. So the AST delta proves this fold is *behaviourally
  inert* and proves **nothing** about whether its sentences are true. Every semantic verdict
  here rests on reading, and is exactly as strong as that reading. That is why `F18`–`F22`
  are all findings no instrument could have produced.
- **Not reviewed:** the security lane; `F1`–`F12` from passes 1–3; the slow lane's content
  (`not-run` by the reviewer, inherited); `B-62`'s substance as a defect; the UI at any
  terminal size — **no UI was driven in this fold**, so the 118×34 / 80×24 discipline
  applied to nothing in it.
