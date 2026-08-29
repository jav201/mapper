# Inc-4 · PRE-gate measurements — orchestrator-owned

**Batch:** `2026-08-26-ui-next-batch-02` · **Increment:** Inc-4 (US-N07 «búsqueda» + the `#D5b` seat
rebind + `LLR-N06.2.4`) · **Entry commit:** `5f4816c` · **Date:** 2026-08-29
**Protocol:** FULL (A-91 — Inc-4 is a data-path + seat-rebind increment; the lighter single-review
lane is not available to it).
**SOURCE files: 5 — DECLARED BREACH** (`mapper/search.py`, `mapper/app.py`, `mapper/views/layered.py`,
`mapper/keymap.py`, `mapper/views/state.py`). Tests uncapped. Reason in §2 / P-a below.

Every number below is **executed against the entry tree**, not transcribed. Prose counts decay; this
batch has paid for that twice. Where a figure contradicts the sealed spec, the spec's figure is
recorded as the superseded one rather than quietly replaced.

---

## 1 · Entry state, verified rather than briefed

| Item | Executed value |
|---|---|
| branch / HEAD | `feat/ui-next-batch-02` @ `5f4816c`, working tree clean, pushed |
| fast lane | `801 passed, 17 deselected, 3 xfailed in 130.83s` — **exit 0**, `grep -c "^FAILED"` = **0** |
| ledger base | **821** all-markers (`801 + 3 xfailed + 17 deselected`) · **804** default lane |
| ruff, scope `mapper/ tests/` | **19 distinct `(file, rule)` pairs · 27 findings** — full set pinned below |
| seat | **52 rows**, 29 map-scope, `duplicate_chords()` → `[]`, sha256 `1e7002cb3c48c879…91eec9e5` |

**The ruff gate compares SETS, never the aggregate.** An aggregate cannot see a swap — one new
finding exactly masked by one removal reads as "no change", which is how a real F401 slipped through
Inc-3's first gate. Entry set (`(count, rule, path)`):

```
1 F401 mapper/app.py              1 F401 tests/test_darkside.py
1 F401 mapper/darkside.py         2 F401 tests/test_diff.py
1 F841 mapper/darkside.py         1 F401 tests/test_github.py
1 F401 mapper/diff.py             2 F401 tests/test_import_csv.py
1 F401 mapper/model.py            1 F841 tests/test_inspector.py
1 F841 mapper/office.py           1 F401 tests/test_legacy_fixture.py
2 F401 mapper/screens/factory.py  2 F401 tests/test_model.py
2 F401 mapper/screens/settings.py 2 F401 tests/test_rail.py
2 F401 tests/test_app.py          2 F401 tests/test_store.py
                                  1 F841 tests/test_worklist_safety.py
```

⚠ **Scope note.** The Inc-3 close records "ruff 28"; this measures **27** over `mapper/ tests/`. The
delta is **scope, not drift** — Inc-3 already recorded that the base worktree carries `prototypes/`,
which the work tree's `.gitignore` hides from ruff, and that an unequal-scope comparison was one of
its two orchestrator errors. The exit gate re-runs **this exact command** so entry and exit scopes
are identical by construction.

---

## 2 · Premises re-executed against the live tree (C-43)

The Inc-4 spec was sealed **before** Inc-2 and Inc-3 landed. Four of its premises about the tree no
longer hold. None invalidates the requirement; three change what the increment must touch.

| # | Premise as sealed | Verdict | Evidence |
|---|---|---|---|
| **P-a** | Inc-4 is **4 source files**: `search.py`, `app.py`, `views/layered.py`, `keymap.py` (§5.4) | ❌ **FALSE** | `LLR-N07.1.1`'s own **Touched symbols** line names `mapper/views/state.py::ViewState.hits` — `NEW — created in Phase 3`. The cut table omits `views/state.py`. Arithmetically the increment is **5 source files**. |
| **P-b** | inline predicate at `layered.py:144-148`; `qlower` ×**4** | ❌ **FALSE — decayed** | `grep -n qlower mapper/views/` → `layered.py` lines **113,116,117,118,119,530,535,600,601** = **9** occurrences. `_matches` is now a module-level helper at `:113`; the spec's addresses predate Inc-2/Inc-3. |
| **P-c** | the inline predicate has ONE consumer (the card hit style) | ❌ **FALSE** | A **second** consumer at `layered.py:597-601` counts matching descendants for the **fold pill's `WARN` hit tail** — `hits = sum(1 for cid in _descendants(index, nid) if _matches(...)) if qlower else 0`. This is Inc-3's `HLR-N06.2` surface, written *after* this spec was sealed. |
| **P-d** | removing `ViewState.query` is contained | ✅ **TRUE** | Exactly **one** reader (`layered.py:491`) and **one** writer (`app.py:1769`), plus the declaration at `state.py:70`. Census over all of `mapper/`. |
| **P-e** | `mapper/search.py` is dead, so every search LLR is new-module work | ✅ **TRUE** | zero importers across `mapper/` and `tests/`; the file is 14 lines and `SearchIndex.query` delegates straight to `Graph.search_hits`. |

### P-a is A-97's exact recurrence, and it is declared rather than discovered at the gate

Inc-3 hit the identical defect: `views/state.py` was owed by LLRs sealed in the design review and named by no cut —
*"arithmetically true when A-89 was written; only the declaration was missing."* The same sentence
is true here, one increment later, about the same file. **Inc-4 declares a 5-source-file breach**
(`search.py`, `app.py`, `views/layered.py`, `keymap.py`, `views/state.py`) under the flow's
"exceeding 4 does not auto-block; declare the reason in §2 and let the review look at it" rule.

**Why it cannot be cut smaller:** the increment's whole subject is moving the *decision of what
matches* out of the renderer and into one owner. The hit set has to reach the renderer, and
`ViewState` is the only channel the sealed contract `IRenderer.render(graph, state)` provides. A cut
that lands the owner without the channel leaves **two definitions of "hit" live at once** — which is
precisely the defect `HLR-N07.1` exists to close, and the shape Inc-2 declared its own breach to
avoid.

### P-c is the finding that was not in anyone's brief

Deleting `_matches` per `LLR-N07.1.1` has a consequence the sealed text does not record: the fold
pill's hit tail loses its source. There are only two outcomes and both are gate events —

- re-source the pill count from the resolved hit set, which **changes the painted number** for
  existing fixtures, because `LLR-N07.1.2` *widens* the hit definition (id, subtitle, attachment
  caption/path now match, where the inline predicate matched only title / notes / field values); or
- leave `_matches` alive for the pill, which **fails `HLR-N07.1`'s zero-occurrence threshold**.

Routed to the architect lens as Question 2, with a C-26 reverse census over `tests/` for anything
pinning that pill count. **Not ruled by the orchestrator.**

---

## 3 · The seat, pinned on ENTRY (`#D25` · `C-D25a`/`C-D25b`)

`#D25` rules the three-row figure a **regression PIN on Inc-4's own diff, in C-40's exact sense — a
pin, not a gate**. `C-D25a` as corrected at the design review's third pass additionally requires the declared diff to be
**asserted EQUAL to the entry/exit difference of `bindings_for(scope)`**; a declared diff joined to
nothing is not a pin, because rebinding a fifth row and declaring four leaves `duplicate_chords()`
returning `[]` — no duplicate is created, so nothing reddens.

**Entry (executed):** 52 seat rows · 29 map-scope · `duplicate_chords()` → `[]` · whole-seat
sha256 `1e7002cb3c48c879c4b32fdbd0c916c89874326801722608216f61fe91eec9e5`.

The only map-scope rows Inc-4's diff touches, as they stand today:

```
('map', 'slash', '/', 'search',   'buscar',             'nav')
('map', 'n',     'n', 'next_gap', 'siguiente faltante', 'view')
```

**Declared exit diff — three rows, and the oracle that must confirm it:**

| Seat key | Kind | After |
|---|---|---|
| `map/n` | **rebound** | `next_hit`, label `siguiente coincidencia`, group `nav` |
| `map/N` | **added** | `prev_hit`, label `coincidencia anterior`, group `nav` |
| `map/M` | **added** | `next_gap`, label `siguiente faltante`, group `view` |

Predicted exit: **54 rows**, 31 map-scope, `duplicate_chords()` → `[]`. `C-D25a` is satisfied only
when the packet's declared diff is asserted equal to the computed entry/exit difference of
`bindings_for("map")` — not merely stated beside it. `bindings_for` exists at `keymap.py:169`, so
the oracle binds two existing artifacts rather than building a third.

---

## 4 · Carries entering Inc-4's PRE-gate scope

**The settle-chase termination counter (Inc-3 pass4 F1) IS in scope.** The recorded ruling: it enters
its owner increment's PRE-gate scope *if that increment touches the file*. The owner is
`mapper/app.py:1572-1574` (`_declare_after_layout` re-scheduling itself while
`region != self._declared_for`), and **Inc-4 touches `app.py`**. So the three-line pass counter is
Inc-4's, taken *inside* the increment and reviewed by its gates — deliberately not applied after a
passing gate, which is the self-clearing pattern this batch forbids.

Its today-state is *measured, not asserted*: termination was observed over 943 configurations at max
5 passes, with storms and a forced oscillation both terminating. The fix converts a measurement into
a guarantee over a live `height: auto` feedback path.

---

## 4b · Reverse census (C-26) — one hit, and it is not in anyone's brief

`LLR-N07.1.1` changes `mapper/views/layered.py` at the fold-pill hit tail. Reverse-grepping that
symbol across the WHOLE `tests/` tree — independent of which requirement owns the test, which is the
entire point of C-26 — returns a test belonging to a **different story and a different increment**:

```
tests/test_darkside_census.py:212
  ("mapper/views/layered.py", "cv.text(cx + 2 + len(core), y + card_h, tail, darkside.WARN)")
```

That row is a member of `CONFORMING_SEVERITY` in Inc-1's hue census (`HLR-S06.3` / `LLR-S06.3.4` /
`LLR-S06.3.5`). Two arms consume it, and both can break:

- `test_hue_census_every_severity_and_busy_site_is_classified` asserts `len(sites) == 38`, a figure
  its own comment records as having moved **36 → 38 in Inc-3** precisely because the fold pill's
  `WARN` bar and its `WARN` hit count were added;
- membership is keyed on the **literal source text** of the line, so a restructure that preserves
  behaviour still moves it.

**Consequence for Inc-4:** re-sourcing the pill's hit count is not a local edit inside one renderer.
It is a change to a site a closed increment's census pins by text. The implementer shall declare this
symbol in the increment's touched-symbols and sweep the census deliberately — a drift here is
legitimate and expected, but it must be **named in advance**, not discovered as a surprise red at the
gate. This is the C-24 / C-26 shape exactly.

---

## 4d · The architect lens corrected ME, and a fourth site entered the budget

`02k-inc4-viewstate-architect.md` returned **A3 does NOT fire** (census 15/15 green on the removed
tree; `render`'s signature byte-identical; the standing pre-authorization is *unspent*, because it
authorises **extending** `render` and no extension occurs). Its ruling is adopted.

It also **falsified my own P-d census**, which is the whole reason the lens is independent:

> There is a **fourth** site. `tests/test_app.py:448` reads `state.query`
> (`assert seen["state"].query == "hij"`). It is the sole causal break.

Verified by the orchestrator against the tree — **confirmed**. My census swept `mapper/` and stopped
there; the reader in `tests/` was outside the glob. Recorded as an orchestrator error rather than
quietly folded in, per this batch's standing practice. The correct break set is **one test, one
line**, and it is now budgeted.

Two further corrections, both verified here: `Graph.search_hits` is at **`model.py:224`**, not the
spec's `169-184`; and `TC-026` resolves to **no node on disk** (`grep -rn 'TC-026' tests/` → empty),
so its *"hit count when a query is live"* clause was never implemented. That is an **inherited Inc-3
gap**, not one Inc-4 creates — but Inc-4 is where it becomes dangerous, because the pill's painted
number changes on a fully green suite. The architect's non-negotiable condition is `TC-026b`.

### ⚠ A stale row in the module map that nearly cost a wrong obligation

Reading `docs/ARCHITECTURE.md:159` for the `ViewState` row, the **adjacent** row states:

> `open_external` … **NO — new, Inc-4 owns it.** Security-reviewed before Inc-4 signs off.

Executed: `mapper/osopen.py:57` **already ships** `open_external`, and the requirement that owns it
lives in `.dev-flow/2026-08-25-ui-next-batch-01/01-requirements.md:277` — **the previous batch**. The
row means *that* batch's `Inc-4`. This batch also has an `Inc-4`.

**This is `#D25` §1's finding generalised from `Dn` ids to increment ids: a bare `Inc-N` does not
resolve without a batch.** The cost is not hypothetical — the orchestrator read that row while
verifying something else, and had to execute two probes to establish that Inc-4 does **not** owe a
security review of `osopen.py`. Swept into the architect's `ARCHITECTURE.md` refresh, since it is the
same table and the same staleness class, at one line. Backlog `B-34` already carries the `Dn` half;
this extends it to increment ids.

---

## 4c · A BLOCK the validator raises that is NOT Inc-4's, recorded rather than swept up

`devflow-validate.py` returns **45 BLOCK** over the project. Scoped and triaged:

| Class | Count | Verdict |
|---|---|---|
| `V2` — AT id with no node on disk, belonging to **Inc-4 or a later increment** | 26 | **Expected.** These are what the remaining increments build. Inc-4 owns eleven of them. |
| `V2` — ids that are **struck / deleted / deferred** (`AT-001`, `AT-002` under §3.1 `SATISFIED-EXTERNALLY`; `AT-027`, `AT-028` deleted by `QA-B-03`; `AT-048` deferred by `#D24`) | 5 | **False-fail.** The rule scans corpus for `AT-` tokens and cannot see a struck section. C-53 prices this exactly as high as a false pass. Carry, not a fix. |
| `V2` — **`AT-005` and `AT-006`** | 2 | ⚠ **REAL, and against a CLOSED increment.** See below. |
| `V16` — `~/.claude` and `~/.claude/skills` carry uncommitted changes | 2 | **Reported as found, never swept up** (C-44 forbids committing another session's work in progress in a shared config repo). |

### ⚠ `AT-005` / `AT-006` — Inc-1's packet claims them "all passed" and no node carries the id

Executed. The project realizes acceptance nodes two ways, and a census of both finds neither id:

```
$ grep -rhoE "def test_at_[0-9]+[a-z]?_" tests/ | sort -u
AT-003 AT-004 AT-007 AT-007b AT-008 AT-009 AT-010 AT-011 … AT-017     # no 005, no 006
$ grep -rn "AT-005|AT-006" tests/                                      # no output
```

`increment-001.md:113` lists `AT-005`, `AT-006` under *"B · black-box AT ↔ story … all passed"*.
Their substance is very probably carried by `test_hue_census_no_undeclared_hue_ships` and
`test_hue_census_every_severity_and_busy_site_is_classified` — but those nodes are labelled with the
**functional** ids (`HLR-S06.3 / LLR-S06.3.4 / LLR-S06.3.5`), so the behavioural id → node edge does
not exist on disk and **C-18 is unverifiable for both**.

**Disposition: NOT fixed inside Inc-4.** Re-opening a committed increment to relabel its tests is
scope creep, and `#D26` is explicit that a code fix never discharges a missing requirement. It is
recorded here, added to the carry list, and **routed to the whole-branch adversarial QA pass**, whose
stated remit is "dual traceability intact" — which is precisely the question this raises. That gate,
not this increment, rules on whether it blocks the merge.

---

## 5 · What is NOT re-litigated

`#D25`–`#D28`, the A-91 pace calibration, the `#D5` cut's authority, `#D5b`'s three rows, `#D6`'s
rejection of `⇥`, and the US-N14 / S-18 / S-19 / UX2-C-01 cuts. This artifact records measurements
and routes two questions; it issues no design ruling.

---

## 6 · Open at the time of writing

1. **Architect ruling** (`02k-inc4-viewstate-architect.md`) — does removing `ViewState.query` re-fire
   trigger A3 and re-open the sealed PDR; and who owns the fold pill's hit count.
2. **QA predicate design** (`02l-inc4-qa-predicates.md`) — the eleven acceptance predicates with
   their C-40 discharge, the killed weaker variants, and the `QA-N-08` fixture shape.

**Implementation does not start until both return.**
