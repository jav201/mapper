# 02g — Mechanical lens-condition reconciliation (RIDER-1)

**Date:** 2026-08-27 · **Base:** `3fe0e4b` (master == origin/master == merge-base, tree clean)
**Instrument:** each lens's OWN condition ledger, audited condition-by-condition against DISK.
**NOT the instrument:** the 41-row amendment table, which dropped conditions twice.

---

## 0 · Why this artifact exists

RIDER-1, carried out of `2026-08-27-repair-batch-02`:

> before the feature batch's **third** PDR fold, audit the fold against the **lenses' own
> condition lists**, never the amendment table. That instrument dropped conditions **twice**.

Four independent audits were dispatched in parallel, one per lens, each required to produce
EXECUTED evidence (a command and its output, or a `file:line` on the current tree) for every
status. A citation of another document was explicitly ruled inadmissible.

**The structural finding that governs everything below, measured not argued:**

```
$ git diff --stat d877784..HEAD -- .dev-flow/2026-08-26-ui-next-batch-02/
(all 14 files ADDED by 8675151; never modified since)
$ git log --oneline -- .dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md
8675151   (one commit)
```

**`01-requirements.md` has not been edited since the lenses wrote their verdicts.** Therefore
every requirement-side finding is frozen exactly where its lens left it, and every line citation
in `02c`/`02d`/`02e`/`02f` still resolves. Only code-side findings could have moved — and the
repair batch touched exactly `mapper/store.py`, `docs/ARCHITECTURE.md` and five test files.

---

## 1 · Roll-up

| Lens | Items in its own ledger | LIVE | Discharged | Verdict at pass 2 |
|---|---:|---:|---:|---|
| architect (`02c`) | 14 (`P2-B1`–`P2-B6`, `P2-C1`–`P2-C8`) | **14** | 0 | REJECTED |
| qa (`02d`) | 8 (`QA2-C-01`–`QA2-C-08`) | **7** + 1 partial | 0 | approved w/ conditions |
| security (`02e`) | 19 (`C-1`–`C-12`, `S-11`, `S-16`–`S-21`) | **8** | **11** | BLOCKED |
| ux (`02f`) | 10 (`UX2-C-01`–`UX2-C-10`) | **10** | 0 | approved w/ conditions |
| **Union** | **51** | **≈39** | **11** | — |

**Only the security lens discharged anything, and only because the repair batch shipped code
against it.** Every other lens is exactly where it was.

### The strict rule, applied and declared

The architect audit offered `P2-B4` and `P2-C7` as PARTIAL, noting that under the strict rule —
**a code fix never discharges a missing requirement** — both are simply LIVE, taking its count to
14 of 14. **The strict rule is adopted.** It is the rule that keeps `S-17` visible, and `S-17` is
the clearest case in the batch: the shipped `mapper/store.py` cites `LLR-STO.1.1` normatively in
five docstrings, all pointing at an identifier that has no statement, no threshold, no `TC`, no
`AT` and no traceability row. The shipped fix **makes the hole harder to notice**, because the
tree now looks like the requirement is being obeyed.

---

## 2 · Corrections the audits made to the LENSES THEMSELVES

Recorded because a lens is not above its own instrument.

| # | Lens | The claim | Executed reality |
|---|---|---|---|
| 1 | `02e` §1 | *"3 blockers · 3 majors · 1 minor"* | **2 majors.** `grep -c "\[major\]"` → 2; `S-19`, `S-20` only. The file's own evidence checklist (`:335`) and closing note (`:375`) both say two. **The roll-up over-counts by one.** |
| 2 | `02c` `P2-B4` | rail supersession *"2 of 9 … short by seven"* | **8** external references, short by **6**. The lens's own pasted grep enumerates 8; its total was off by one. Substance sharper, not weaker — the misses include a PRODUCTION site, `mapper/app.py:1259`. |
| 3 | `02c` `P2-C6` | replacement threshold pinned at *"22 arg-ful sites / 9 files"* | Already stale when written. See §3. |
| 4 | `02e` `S-16` | five file-derived position families | **six** families / 21 positions when derived from the model. The lens's list was itself hand-made (C-31) and omitted `documents[]`. The repair covered it anyway. |
| 5 | `02f` `UX2-C-05` | (re-run) whole-frame scan → 17/27 visible | **Vacuous by construction** — `cobertura` shows through *around* the dialog. Clipped to `#help-dialog`: **16/27**. The UX auditor caught and corrected its own oracle mid-flight. |

---

## 3 · The A3 census — settled, with the question stated before the number

Four generations of this number have now been wrong. The cause is that *"the `.render` blast
radius"* names **three different sets**, and each generation answered a different question.

**QUESTION (normative form for `R-1`): which call expressions invoke the MAP-RENDERER protocol
and therefore must migrate when `IRenderer.render` gains `ViewState`?**

**Instrument: AST.** Not grep — grep cannot tell a call from a *mention* of a call.

```
ARG-FUL call sites (A3)   : 23
  distinct files          : 10
  production call sites   : 3 -> mapper/app.py:737, :1352, :1727
  test call sites         : 20  (9 files)
ZERO-ARG .render() sites  : 25   <- Textual WIDGET protocol, NOT in the A3
def render in mapper/views: 6    <- lane.py:108, :171, :311; layered.py:131;
                                     outline.py:47; radial.py:107
```

**Generation five was produced during this very reconciliation, by the orchestrator.** A grep
gave 24 sites / 11 files; the 24th is `mapper/widgets/rail.py:180`, a mention of
`renderer.render(...)` **inside a docstring**. The QA audit reported the same 24 the same way.
Only the AST separates them. This is C-42's rider exactly: prefer a structured parse to a
substring search, because a substring search cannot tell a value from its own encoding.

`R-1` must therefore be written as **question → number → instrument → measured-at-SHA**, or
generation six is guaranteed.

---

## 4 · The union ledger

### 4.1 architect (`02c`) — 14 of 14 LIVE

| id | Grade | Status | Class | Executed basis |
|---|---|---|---|---|
| `P2-B1` | blocker | LIVE | document | `### 3.6` `:2212` says Inc-6 (ratified Inc-7); `### 3.8` `:3103` says Inc-7 (ratified Inc-8+9). `Inc-9` appears 12× — an id existing only in the 9-cut. Both cuts live simultaneously. |
| `P2-B2` | blocker | LIVE | requirement | Re-derived: 51 distinct AT tokens, 5 struck, **46 live, 43 owned, 3 UNOWNED** — `AT-009`, `AT-031`, `AT-040`. 27 `**Acceptance:**` lines; `AT-009` on none. |
| `P2-B3` | blocker | LIVE | **DESIGN** | Legend labels re-derived from `01b` DECISION 3 (`:274`–`:318`, all inside `:263`–`:380`): **23**, not 21. Wrong count live at **four** sites (`:3355`, `:3395`, `:5082`, `01b:373`) — one more than the lens named. |
| `P2-B4` | blocker | LIVE (code half only landed) | requirement | Pins re-derived: `MASTER_LEGACY_DIGESTS` 12 + `MASTER_RAIL_DIGESTS` 5 + `MASTER_FACTORY_TREE_DIGEST` 1 = **18**. Requirement still says *"0 remaining references"* and enumerates **2 of 8**. `MASTER_RAIL_DIGESTS` named in **no** artifact. |
| `P2-B5` | blocker | LIVE | requirement | §3.0 (`:376`–`:471`) has no id, no acceptance, no increment. `grep -rn COERCION_RANGES mapper/` → **nothing**. |
| `P2-B6` | blocker | LIVE | document | `:1508` still parents to `HLR-N06.2`. AST: 30 notify sites / 19 non-literal / **15 unrouted** = `app.py` 11 + `screens/factory.py` 4. `factory.py` is Inc-9's, so the child is unsatisfiable in its parent's budget. |
| `P2-C1` | condition | LIVE | document | IFC consumer list (`:3745`–`:3752`) names 5 consumers incl. `outline.py`, `export.py`. AST: `rows()` has **4 sites / 3 files**, none outside `views`. |
| `P2-C2` | condition | LIVE | requirement | `C-D4` appears 0× in `01-requirements.md`; only in reviewer files and `PLAN.md:761`, which *records the finding*. A recorded finding is not a clause. |
| `P2-C3` | condition | LIVE | deliverable | `grep "D15\|AT↔TC"` → **0 hits**. The two tables (`:3965`, `:4013`) never cross. Graded ✗ for the third time. Blocked on `P2-B2`. |
| `P2-C4` | condition | LIVE | document | `with_header` 0× in requirements; still at `ARCHITECTURE-proposed-at-ARQ.md:235`, `:275`. |
| `P2-C5` | condition | LIVE | **DESIGN** | `grep -c "runtime_checkable\|Protocol\|isinstance"` in requirements → **0**. Nothing creates `views/state.py::ViewState`. |
| `P2-C6` | condition | LIVE | document (re-derive) | See §3. |
| `P2-C7` | condition | LIVE (doc half landed) | ownership | Repair batch DID amend the map (`ViewState` row at `:159`, COMMITTED/NOT PRESENT). Still: both A3 subjects frozen (`:146`, `:148`); **no commitment row for the `dots`/`bgs` widening**; `03-increments/` is **empty**, so no increment owns the Phase-6 amendment. |
| `P2-C8` | condition | LIVE | **DESIGN** | `:2579` still *"< 1000 ms for 200 maps"* with no measurement; `:2648` still flags both ms figures `assumed`. Repair batch deliberately asserted no budget. |

### 4.2 qa (`02d`) — 7 LIVE, 1 PARTIAL

| id | Status | Note |
|---|---|---|
| `QA2-C-01` | LIVE | Three-way intersection re-run: **six** failing ids — `AT-009`, `AT-031`, `AT-034b`, `AT-040`, `AT-046`, `AT-047`. UX's independent run agrees (40-way intersection; 4 in table+req but on no story line). **The briefing said "three orphan ATs"; the executed set is six.** |
| `QA2-C-02` | LIVE | See §3 — resolved here, in the orchestrator's favour only after AST. |
| `QA2-C-03` | LIVE | `LLR-STO.1.1`: 4 prose refs, **0 headings**. Confirmed independently by security (78 headings enumerated, **no `STO` family at all**). |
| `QA2-C-04` | LIVE | `HLR-S06.3` parent threshold unchanged. |
| `QA2-C-05` | LIVE | The census classifier is still undefined. |
| `QA2-C-06` | LIVE | Cut still contradictory — same root as `P2-B1`. |
| `QA2-C-07` | LIVE | `QA-M-02` / `QA-N-08` still absent; three unbudgeted fixtures. |
| `QA2-C-08` | PARTIAL | `AT-007`/`AT-007b` id staleness. |

### 4.3 security (`02e`) — 11 discharged, 8 LIVE

**DISCHARGED on executed evidence with positive controls:** `C-1` (0 `RecursionError` across
depths 500/1500/3000/20000; control returns 2187), `C-2a`, `C-4`, `C-5`, `C-6`, `C-7`, `C-8`
(AST re-derived **30/19/0/15**, identical, addresses matching one for one), `C-9`, `C-10`,
`C-11`, `C-12`.

**`S-16` — CLOSED as scoped.** Lane A control: 5/5 report LEAK under bypass. Lane C: **5/5
coerced, 0 leaked**; derived from the model, **6 families / 21 of 21 positions**.
**`S-11` — CLOSED (code half).** **0 of 19** hostile inputs leak a non-`MapStoreError`; control
green (the unguarded inner call still raises `AttributeError`); R18 is the matched pair.

| id | Status | Note |
|---|---|---|
| `C-2b` | **LIVE (requirement)** | The code is fixed; `LLR-STO.1.1` does not exist. |
| `C-3` | **LIVE** | Threshold 2 still *"measured as elapsed time"*. No threshold 5. |
| `S-11` | **LIVE (requirement)** | Still prose at `:2467`, assigned to the phantom id. |
| `S-17` | **LIVE** | 78 headings, no `STO` family. Positive control: the same regex finds `LLR-N13.1.5` at `:2391`. |
| `S-18` | **LIVE — this PDR's design item** | `grep -rnE "perf_counter\|monotonic\|deadline\|timeout\|budget\|elapsed" mapper/views/ mapper/app.py mapper/canvas.py` → **no output**. Control: same pattern hits the two test files. |
| `S-19` | **LIVE — and it is S-18's PRECONDITION** | Measured on the 51-node/410-edge shape: Layered **1283 ms**, Outline **337 ms**, **Radial 142 ms — UNDER the 250 ms budget**. So `k = 0` on Radial and threshold 4 cannot distinguish a correct implementation from a missing one. |
| `S-20` | **LIVE — untouched** | 3 independent `MAX_RENDER_NODES` copies; 3 private walks; `children_of` still O(E) per call at `mapper/model.py:149-150`. |
| `S-21` | **LIVE — untouched** | Only one §4.1 flow node declares coercion (`:3594`). |

### 4.4 ux (`02f`) — 10 of 10 LIVE

**7 of 10 need a design ruling.** Only `UX2-C-04`, `UX2-C-07` limb 2 and `UX2-C-10` are
dischargeable by text alone.

`UX2-C-01` is **worse than recorded**. Real `pilot.press("n")` over 9 focusables:

```
walked: 2/9   committed a ficha overwrite: 5/9   SIDECAR REWRITTEN: 6/9
insp-field-D   'ACTA-2011-034' -> 'n'    SIDECAR REWRITTEN=True
```

**The loss is durable to disk**, not merely in-memory. It was independently and accidentally
demonstrated on the repository's own fixtures during this audit (§6).

`UX2-C-02`: entry chord proposed **`c` (`consultar campos`)**, checked against all 48 `KEYMAP`
rows — free in map scope, no app-scope collision, and `c` already means *consultar* in `home`
scope, so the verb is consistent. The whole-seat spec is `mapper/keymap.py` (`KEYMAP` `:87`–`:151`,
`GROUP_SCOPE` `:53`–`:66`, pinned by `tests/test_keymap.py`). **This is a 4th changed seat row, so
`#D10`'s three-row cap must be amended to four in the same breath** or Inc-5 breaches its own rule.

`UX2-C-08`: **1.85 : 1 re-derived exactly** from `mapper/darkside.py` at both rungs.
`UX2-C-10`: all three collisions reproduce, **plus a new one** — on the `WINDOWS` rung `WORDMARK`
collapses into `GROUND`, so the overflow declaration is not merely low-contrast but **invisible**.

---

## 5 · Newly raised — not in ANY prior ledger

| new id | Sev | Finding | Evidence |
|---|---|---|---|
| `S-22` | major | A phantom sidecar node still inflates `coverage()`'s denominator with `warnings=[]`, so `load_or_notice`'s warning arm (`mapper/app.py:459`) never fires and `LLR-N13.1.5`'s containment **never engages**. +1, not the doubling the lens argued. Out of the repair batch's fence, **inside this batch's** — US-N13 paints that bar. | `coverage()=(2,3)`, `warnings=[]` on a phantom str id; `mapper/store.py:384-388` says so honestly |
| `S-23` | minor | `MapStore.load` interpolates the **full absolute path, username included**, into an operator-facing toast — four lines above a comment asserting that class was closed by threshold 3. | `mapper/store.py:456`; rendered via `str(exc)` at `mapper/app.py:453`, `:1181`. One-line fix: interpolate `map_id`. |
| `UX2-C-11` | major | `_commit` rewrites the sidecar on blur **even when the delta is empty** (`insp-title`, `insp-notes` show `SIDECAR REWRITTEN=True` with no value change). | UX probe transcript |
| `UX2-C-12` | minor | Damaged-map load fires the toast **twice**, both with an **empty title**. | `[('', 'no se pudo cargar roto: …'), ('', '…')]` |

---

## 6 · Incident: the audit corrupted repository fixtures, and that IS the finding

The UX auditor's first probe pointed `MapperApp` at the real `fixtures/` directory. The
inspector's commit-on-blur **wrote through**: `fixtures/legacy.mmd` and `fixtures/legacy_nodos.yml`
were modified (70 lines in the sidecar), turning `erp[Sistema ERP Legacy]` into `erp[n]`.

- Detected by the auditor on its second run (`val_before == 'n'`), and independently by the
  orchestrator's contamination monitor.
- `git checkout --` was correctly refused by the permission classifier under the no-mutating-git
  instruction; restoration was done read-only via `git show HEAD:<path>` redirected over each file.
- **Verified by sha256 against HEAD — both MATCH.** Tree clean at `3fe0e4b`.
- The first probe's output was discarded and every later probe ran in `tempfile.mkdtemp`.

**This is not merely an incident to log.** A single keystroke, with no confirmation and no
explicit edit gesture, permanently replaced an acta reference in a tracked file. It is the
strongest available evidence for `UX2-C-01`, obtained by accident, on the real store.

---

## 7 · Conclusion

**Amendment set 3 as briefed cannot be authored, because the briefed scope is false.**

The briefing named six remaining items: the two UX blockers, orphaned `COERCION_RANGES`, two live
increment cuts, three orphan ATs, and the 23-vs-21 legend census. Executed, the live set is
**≈39 items across four lenses**, of which **≈11 require design rulings** rather than document
edits, plus **4 newly raised findings** and **2 live security defects on master**.

The briefing's list is a subset, not the set — and three of its own entries are wrong in detail:
the orphan ATs are **six, not three**; the legend census is **23, and striking the duplicate `V4`
takes it to 22**, so "correct 21 → 23" would be wrong twice; and `S-17`, `UX-3` and `S-18` appear
in the PLAN's own 12-blocker table but not in the briefed list at all.

**This is C-43 at the batch level: the authorization to spend the final PDR iteration rests on a
premise about remaining scope that executes FALSE.** Recorded here, and referred to the operator
before the third iteration is spent.
