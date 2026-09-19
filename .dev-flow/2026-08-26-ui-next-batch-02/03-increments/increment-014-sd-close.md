# Increment 014 — Inc-REPAIR stage S-D — CLOSE

**Stage:** Inc-REPAIR **S-D**, the last stage. **On this close, Inc-REPAIR is COMPLETE.**
**Cut:** AMENDED by ruling to `mapper/views/radial.py` + `mapper/app.py` (2 SOURCE).
**Gates:** code review **APPROVED WITH FINDINGS** after two rounds (`BLOCK-UNTIL: F1, F2`
discharged by re-read); security **PASS WITH FINDINGS**, no HIGH.

---

## 1. What changed

### Workstream 1 — the declared header residue (CLOSED)
`radial.header_rows` did not exist and `app.py::_header_rows_for` charged radial with
`layered.header_rows` as an explicit, arm-pinned residue. Now: `_header_line(unpainted)`
factored out of `_paint` so the CHARGE and the PAINT have one source; `radial.header_rows`
added — rendered not divided (`B-61`), worst case charged, signature identical to its two
siblings; dispatch registered.

Measured on the arm's own fixture: layered's charge exceeded radial's own first line at
**7 of 10** widths. Radial's new charge equals its own first line at **10 of 10**.

### Workstream 2 — AGREE-1 (VERIFY-AND-RECORD)
Radial's recorded empty-frame floor **no longer reproduces**: 0 disagreements against
outline's 52 on the same instrument, confirmed positively at the two sizes recorded as
failures. Pinned by new arms over a grid reaching width 14, with outline as the
known-present control (`C-55`'s rider).

### Workstream 3 — PAN-1 (RULED, then implemented, then twice corrected)
`_consumes_pan` identity dispatch; `_pan` inert-and-declared; `_reclamp_pan` holds the
offsets for non-consumers. Radial does not want pan — focus-based, polar layout, so a
viewport is a category error (coordinator ruling).

---

## 2. What the gates caught, stated plainly

**This increment was BLOCKED once, on two HIGH findings, both mine.**

- **`F1`** — the first fix ZEROED the pan offsets instead of declining to clamp, so a mere
  excursion into outline or radial discarded the operator's pan: measured (48,0) → (0,0) with
  **no key pressed**. PAN-1 exists to close *"the app held a pan the picture never
  reflected"*; I shipped *"the app discarded a pan the operator set, without saying so"*.
  **Same family, one seam over, in the commit that closes the family.**
- **`F2`** — the whole workstream shipped **unpinned**. A single-edit mutant reverted both
  behavioural halves and **survived the full lane at 1096 passed, exit 0** — a true statement
  about the increment carrying no information about a third of it.

Four LOW findings followed in round 2. `R2-1` is the one that matters: `measured != pinned`
**recurred inside the increment that minted it**, one round later, in a branch I had just
corrected. Nothing executed the rule, so the rule caught nothing.

---

## 3. Files modified

| file | kind |
|---|---|
| `mapper/views/radial.py` | **SOURCE 1** |
| `mapper/app.py` | **SOURCE 2** |
| `tests/test_pan.py` | test — six PAN-1 arms |
| `tests/test_canvas_header_charge.py` | test — two pins rewritten, one deleted |
| `tests/test_agree_floor.py` | test — radial arms + outline control |
| `tests/test_a3_census.py` | test — two census pins 32 → 34 |
| `.dev-flow/state.json` | doc |

**SOURCE: 2** of 4. Nothing staged from `prototypes/`, `mapper.db` or scratch.

---

## 4. Evidence

| gate | result |
|---|---|
| default lane | **1095 passed, 19 deselected, 3 xfailed**, exit 0 |
| slow lane | **19 passed, 1098 deselected**, exit 0 |
| ruff project / `--isolated` | **27 / 27**, baseline 27 |
| ledger | 1080 + 14 + 1 = **1095**, derived per module and re-derived from the base by the reviewer |
| `state.json` parse guard | OK after every write |

### Mutation battery — all KILLED, with per-arm attribution

| mutant | verdict | what it proves |
|---|---|---|
| `M-CR-PAN-A` / `M1` | **KILLED 4** | the round-1 survivor is dead |
| `M-F1-ZERO` / `M2` | **KILLED 2** | fires the excursion arm **and nothing else** |
| `M-F3-LATCH` / `M3` | **KILLED 1** | fires the latch arm alone |
| `M4` (inert but SILENT) | **KILLED 3** | the declaration half is pinned **separately** |
| `M5-RAISE-DEGRADES` | **KILLED 1** | `R2-1`'s gap closed |

`M4` is the shape to copy: an inert-and-declared affordance owns a pair of pins, so a change
that keeps the inertness and drops the notice now reddens.

### Instruments that failed their own controls first — all discarded, none reported

1. My radial AGREE-1 grid began at width 24 and **excluded its own subject**.
2. My `F15`-style `fit` twin post-composed `plain` over a function that already coerces.
3. My first PAN-1 probe used lowercase keys.
4. The code reviewer's graph-changes probe: held pan 320, post-mutation max never below 459.
5. The security reviewer's unregistered-renderer control **rebound `self.renderer` itself**,
   so the identity test still matched.

Five instruments, five authors catching their own, five readings withdrawn. **The instrument
is not exempt from the defect it hunts.**

---

## 5. Carried, not fixed here

**`B-68` (MEDIUM)** — the exported SVG renders from an **unclamped** pan at a geometry the
canvas never used: 47,263 bytes at pan (0,0) against **16,718** at a reachable pan, roughly
**65 % of the map missing** from a file the operator hands to someone else, with no
declaration. Reachable today with no excursion at all (*pan to the edge, press `e`*).

Ruled out of S-D because it was **proven** pre-existing — reproduced with zero excursion, and
a run against a simulated pre-S-D clamp produces the byte-identical artifact — **not because
it is small.** Carried to the whole-branch gate.

**`HERMETIC-1`** — the suite is not hermetic; fixed first in Inc-CONFIRM, before the gate.

---

## 6. What this close does not claim

- **No merge authorization.** The security reviewer states it and it is recorded: clearing a
  risk is not granting a close. The whole-branch security sign-off and the adversarial PR-level
  QA pass both still stand.
- **Every lane figure carries the `HERMETIC-1` qualification** — taken with network available
  and `gh` succeeding. The numbers are left exactly as measured.
- **The code reviewer declared its own independence weaker on `F1`**, because the line in the
  tree is the snippet it prescribed. What discharges `F1` is evidence it did not author: the
  excursion arm, and `M2`'s kill firing that arm and nothing else.
- **Not run:** six of eight sequences in one 80×24 pan-read sweep; `_declare_after_layout`'s
  mismatch branch under a concurrent geometry change; non-Windows behaviour and terminal sizes
  outside 24–118 columns.
