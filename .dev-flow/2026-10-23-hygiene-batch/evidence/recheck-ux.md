# UX recheck — PDR row 9 (interaction design) — Batch 2026-10-23-hygiene-batch

> Reviewer: ux-reviewer (trigger D1 fired: Q1 changes what the operator sees — colour restored
> under `NO_COLOR=1`). Lens: ISO 9241-210 mapped per `agents/ux-reviewer.md`.
> Reviewed: `design/design-proposal.md` against `01-requirements.md` (US-Q1-001 + AT-108,
> HLR-Q1.1/Q2.1/Q2.2 acceptance blocks) and the shipped code it reuses.
> Read-only review; no proposal, interface or code changed.

## Criteria table

| # | Criterion (observable form) | How exercised at PDR | Result | Verdict |
|---|---|---|---|---|
| UX-1 | Q1: the operator-facing change (colour ALWAYS on; `NO_COLOR` env override ignored) is documented as intentional, not an oversight | Expert inspection of proposal §1 ("Colour is always on… mechanism decided by ruling R3 — this design implements it, it does not re-litigate it") + §6 rejected-alternatives row ("`--no-color` opt-out… Rejected by ruling R3 + the operator ruling on question Q5: …an opt-out is a way back to the defect") + requirements HLR-Q1.1 rationale | The behaviour change and the loss of the `NO_COLOR` escape hatch are both recorded as deliberate rulings (R3, Q5), with the defect-class rationale named | ✓ |
| UX-2 | Q1: nothing the user sees changes besides colour (LLR-Q3.2.2 byte-identity; requirements §2.5 "No increment of this batch changes what any screen looks like beyond Q1 restoring colour") | Inspection of proposal §1 NOT-list ("change what any renderer paints", "re-baseline any golden"), §4 (all production `Canvas` construction sites pass nothing), §8 census (`mapper/views/outline.py:311` `no_color=True` Rich pin explicitly out of L1's edit set — flipping it would redden Outline byte-identity digests) | No other visible change is introduced; the one env-independent monochrome pin in a renderer is named and excluded | ✓ |
| UX-3 | Q1 current state check: `mapper/app.py` today carries no NO_COLOR handling (grep 2026-10-23: no `NO_COLOR`/`Monochrome` match) — Textual's default installs the Monochrome filter; the design ADDS neutralisation in `MapperApp.__init__` | Grep of `mapper/app.py` | Design premise matches code | ✓ |
| UX-4 | Q2 map-load refusal toast: limit named, map id named, never a path, session stays live — specified enough to implement without inventing wording at the keyboard | Inspection of proposal §3 `q2-map-load` refusal path ("typed MapStoreError(limit + map id, no path) → screens toast") against the real load surfaces: `mapper/screens/home.py:169-177` (`could not load {map_id}: {str(exc)}` via `darkside.plain`, map joins the broken list, home keeps working) and `mapper/screens/map/screen.py:208-215` (`error loading map: {str(e)}`, error graph established, session live) | Wording discipline lives at the store boundary (typed, path-free `MapStoreError` per C6); both existing toasts interpolate `str(exc)` through `darkside.plain`, so limit + map id reach the operator with no new wording invented; session-stays-live is structural in both handlers. AT-109…112 observable outcomes are implementable as designed | ✓ |
| UX-5 | Q2 CSV-import refusal toast: same four properties for AT-113/114 | Inspection of the real CSV error surface `mapper/screens/home.py:524-530`: on `preview_csv` raise the toast is `could not read CSV {path.name!r}: {type(e).__name__}` — **exception TYPE only, never `str(e)`** | **GAP — see F-UX-1.** A typed `MapStoreError` naming the limit renders as the bare word `MapStoreError`; the reason (size cap vs binary probe) never reaches the operator, failing AT-114's observable outcome ("the import refusal message with the reason") | ✗ |
| UX-6 | Q3 sweep/audit changes nothing the user sees (audit sink consumed by tests only; byte-identity LLR-Q3.2.2) | Inspection of proposal §4 (`audit=None` default; the 3 production construction sites `mapper/views/lane.py:199`, `layered.py:693`, `radial.py:184` pass nothing) + §1 NOT-list | Observational only; byte-identity is the oracle; no golden re-baselining | ✓ |
| UX-7 | Empty/folded/orphan/error states have their own criteria or a written out-of-scope | Inspection of `design/state-matrix.md`: `empty` short-circuit asserted as ≤2 named lines (the "(no map loaded)" text), `folded` fold-invariance for the five non-Layered renderers, `orphan` per-renderer behaviour recorded; dangling-edge OutlineRenderer KeyError (`mapper/views/outline.py:214-218`) recorded as excluded + backlog candidate; `panned`/`_degraded` deferred by ruling-style note, not silence | All non-happy-path states are either asserted or excluded in writing | ✓ |

## Findings

### F-UX-1 — ⚠ major (condition on approval): CSV refusal reason cannot reach the operator; the fix has no owner lane

- **What:** the CSV import error toast at `mapper/screens/home.py:524-530` shows
  `f"could not read CSV {path.name!r}: {type(e).__name__}"` — the exception **type name only**.
  The Q2 design raises a typed `MapStoreError` whose *message* names the limit (proposal §2/§3),
  so the painted toast would read `could not read CSV 'x.csv': MapStoreError` — the reason
  (4 MiB cap vs binary probe) is invisible. AT-114's observable outcome is "the import refusal
  message **with the reason**"; HLR-Q2.2 requires "the reason named in the error" *surfaced*.
- **Why it is a PDR problem, not a lane detail:** the map-load toasts interpolate `str(exc)`
  (path-free by C6 construction, routed through `darkside.plain`), so AT-109…112 work as
  designed — but the CSV toast does not. Fixing it means editing `mapper/screens/home.py`, which
  is in **no lane's file set** (L2 owns `store.py`, `diff.py`, `import_csv.py`, `osopen.py`;
  §8 declares file sets disjoint). As sealed, the lane cannot satisfy AT-114's observable outcome
  without violating the fork's file disjointness.
- **Ask of the author (options, author's pick):** (a) add `mapper/screens/home.py` to L2's file
  set for the one-toast edit (`str(e)` in place of `type(e).__name__` — safe only because the new
  refusal text is path-free by C6, and the pre-existing generic branch must keep the type-name
  discipline for arbitrary `OSError`s, i.e. special-case the typed refusal); or (b) specify that
  `preview_csv` refusals raise distinct typed subclasses whose *names* carry the reason; or
  (c) re-specify AT-114's surface. Option (a) matches the existing `MapIdError` precedent
  (`_refusal_toast`, `mapper/screens/common.py:205-214`: store-authored text may be shown).

### F-UX-2 — ⚠ minor (notice, not blocking): toast-consumer census names the wrong surfaces for the load path

- Proposal §5 (screen arm) and §8 (crossed census) record the `MapStoreError` consumers as
  `mapper/screens/construct.py:57` and `mapper/screens/common.py:_save_or_toast` — both are
  **save/create/id-check** surfaces. The AT-109…112 **load** refusals actually surface through
  `mapper/screens/home.py:169-177` and `mapper/screens/map/screen.py:208-215`, which catch
  generic `Exception` and are invisible to a `MapStoreError` grep. The L2 screen arms must drive
  those two load paths; the census correction should name them so the lane does not assert toasts
  at the wrong call sites.

## Explicitly not covered

- **Automated walkthrough through the real mechanism:** `not applicable at PDR` — the object
  under review is a design artifact; the headless driver arms (AT-108 `run_test()`, the
  screen-arm toasts) are Phase-3/Phase-4 work and are correctly specified as black-box.
- **Evaluation with users:** `not performed — this team is one person and no user of this
  surface exists outside it` (context of use §2.3: single-operator developer tool).
- Visual styling decisions (colour language itself) — owned elsewhere; Q1 restores an
  already-approved rendering, no prototype round owed (requirements §1.2).

## PDR record row 9 (interaction design) — Verdict

**⚠** — Q1 colour-restore is documented as a deliberate ruling with nothing else user-visible
changing (UX-1…3 ✓); map-load refusal toasts are specified against the real mechanism with no
invented wording (UX-4 ✓); Q3 is observational-only (UX-6 ✓); empty/folded/orphan states are
asserted or excluded in writing (UX-7 ✓). **But** the CSV refusal toast as shipped cannot show
the refusal reason AT-114 makes the operator-visible outcome, and the fixing file is owned by no
lane (F-UX-1, major); the toast-consumer census mislabels the load surfaces (F-UX-2, minor).

**Lens verdict: `approve with conditions`** — condition: resolve F-UX-1 (surface the CSV refusal
reason and assign the owning lane) before the fork seals; F-UX-2 correctable in the PDR record.
