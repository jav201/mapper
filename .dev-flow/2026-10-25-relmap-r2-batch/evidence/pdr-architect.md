# PDR evidence — architect — batch 2026-10-25-relmap-r2-batch

Independent review; I authored none of the artifact. All line numbers verified against the
worktree tree as of 2026-10-25 (commands noted per row).

## Scope reviewed

- `.dev-flow/2026-10-25-relmap-r2-batch/design/design-proposal.md` (336 lines, full read)
- Record seed `.dev-flow/2026-10-25-relmap-r2-batch/design/PDR-2026-10-25-relmap-r2-batch.md` (101 lines, full read)
- Contract `01-requirements.md` (F-1..F-5 §2.8 at :270-274; LLR-RVH.4.1-.4.4 :780-804; LLR-RVG.1.5 :548-556; LLR-RVS.3.3 :652-661; risk :1073-1076)
- `docs/ARCHITECTURE.md` rows :158, :165, :194, :197, :266, :319-322, :344-365
- R1 record `PDR-2026-10-25-relmap-r1-batch.md` (D1-D8 at :110-117; PD-2/PD-3 at :72-73)
- Code: `mapper/screens/home.py`, `mapper/keymap.py`, `mapper/app.py`, `mapper/screens/help.py`,
  `mapper/screens/palette.py`, `mapper/screens/draft_guard.py`, `mapper/relmap/{model,descriptor,audit,adapter,gaps}.py`,
  `mapper/reqharness/audit.py`, `mapper/canvas.py`, `mapper/osopen.py`
- Tests re-derived by grep (below)

## Record §A rows in my lens

| §A row | ✓/⚠/✗ | Evidence |
|---|---|---|
| 1 Proposal complete | ✓ | proposal §1-§6 present; 6 rejected alternatives + 3 honest `n/a` rows (:296-305); `n/a` rows name the deciding authority (operator verdict, R1 DDR §E, R1 D3 freeze) |
| 2 Respects ARCHITECTURE boundaries | ✓ | cited rows real: `relmap` row :158 (text-leaf commitment verified verbatim); `relmap screen` commitment row :165; `app` dependency row :194 (`screens/relmap` re-export edge) and `screens/relmap` dependency row :197 (D3-API-only reads, renderer mutual-import ban); planned-freeze row :266; R-016 :319, R-018 :321, R-019 :322. No boundary moves; divergences "none new" is consistent with what I read |
| 3 Forward applicability | ✓ | proposal §7: 6 rows, every consumer column non-empty (:309-316) |
| 4 Requirement coverage | ✓ | spot-checked the §5.1 LLR rows against contract LLRs (RVH.4.1-.4.4, RVS.3.3, RVG.1.5 all present with asserting tests named); no orphan LLR found in my families |
| 5 Tests observable + non-vacuous | ✓ | §5.1 names a RED counterfactual per new file and an M-* mutant per LLR; mutant lists match the contract §4 negative-control names I spot-checked (M-RVH-9/10/12, M-RVS-9, M-RVG-7) |
| 6 Gauntlet controls declared | ✓ | §2.1 exit checks + guard set (:112-118); both seam probe evidence files exist on disk (`evidence/p2-seam-at-driver.md`, `evidence/p2-seam-workspace-repo.md` — `ls` of the evidence dir) |
| 7 Frozen interfaces listed | ⚠ | D1-D5 listed and the "frozen set is exactly" sentence present (:191-197), **but D1 is under-specified — see F-ARCH-1** |
| 8 Lane plan disjoint + census | ⚠ | counts verified (see §2.1 below) **but the Inc-1 file set omits a live consumer — see F-ARCH-2**; three census line-citations are wrong — F-ARCH-3 |
| 9 UX lens | n/a in my lens | owed to `ux-reviewer` (D1 fired) |
| 10 Security lens | n/a in my lens | owed to `security-reviewer` (C6/C8) |

## Census re-derivation (my own greps — `git grep -n` over `mapper/` and `tests/` unless noted)

| Symbol | Proposal claim | What I found | Complete? |
|---|---|---|---|
| home.py enumeration | enumeration single site `home.py:209` | `mmd_files = sorted(store.workspace.glob("*.mmd"))` at :209 (grep). Second glob site at :133 is inside a different loop — same file, one edit increment, fine | ✓ |
| home.py table / rows / open route / badge | `:300` table; `:369-374` rows; `:455-458` open route; `:352-358` badge precedent | `table = self.query_one("#home-recents", DataTable)` at :300; `table.add_row(...)` at :369-374; `_open_map` → `push_screen(MapScreen(name))` at :455-457; badge `Text.assemble((f" {kind} ", INK on STEP))` at :352-358 (INK-on-STEP precedent real) | ✓ |
| `LEAK_EXCEPTIONS` line-pin | `tests/test_inc9c.py` pins `("mapper/screens/home.py", 176, "str(exc)")` | pin real at `tests/test_inc9c.py:274`; `home.py:176` is the `str(exc)` notify line (sed 172-180). Re-pin planned in same increment as the home.py edit (§2.1 Inc-6, :108; worksheet :358-360) | ✓ |
| keymap scope constants | `mapper/keymap.py:27-41` | `SCOPE_MAP` :27 through `SCOPE_REVIEW` :41 — exact. No `SCOPE_RELMAP` yet (pre-implementation, as expected) | ✓ |
| keymap "uniqueness rule :9-12" | `:9-12` | **✗ miscite** — :9-12 is docstring text; the uniqueness rule is the `LLR-N03.6` comment at :25 plus `duplicate_chords()` at :445 | citation wrong, substance real |
| `KeyBinding` shape `:139-152` | dataclass fields | exact — glyph/action/label/group/priority at :139-143, `scope` property :146-147, `KEYMAP` seat opens :152 | ✓ |
| leave precedent `:230-231` | `q`/`escape` leave rows | exact — `KeyBinding("q", ...)` :230, `escape` :231 | ✓ |
| whole-seat pin `test_key_dispatch.py:137` | pin does not move | pin real but not at :137 — :137 sits inside the hand-maintained EXPECTED table (which spans ~:52-168); the assertion is `test_at_n03h_the_whole_seat_matches_its_specification` at :170 ("the INDEPENDENT referent — the WHOLE seat" :30-49). Since Inc-2 is additive, the pin genuinely does not move | ⚠ citation imprecise, substance real |
| help surface `help.py:223` | seat-derived BINDINGS | BINDINGS comprehension over `textual_bindings(SCOPE_HELP)` at :221-224 (:223 is the comprehension line) | ✓ |
| palette surface `palette.py:36,432` | seat-derived BINDINGS | `:36` real (BINDINGS block :35-38); **`:432` does not exist — the file is 218 lines** (`wc -l`) | ✗ half the citation is phantom |
| app help/palette actions `app.py:274-296` | pushes CommandPalette / HelpScreen | exact — `action_palette` :275-291, `action_help` :293-296; help reads the screen's `KEY_SCOPE` (no app change needed, matches LLR-RVH.4.4 draft-time note) | ✓ |
| A3 census `.render(` pin | pin on ARG-FUL `.render(` count; relmap renderers add none | pin real — `test_tc_a3_the_census_cardinalities_are_PINNED` at `tests/test_a3_census.py:108`; call-site sweep is `tracked("mapper/*.py", "mapper/**/*.py", "tests/*.py", "tests/**/*.py")` at :88 and :484, so the future `mapper/screens/relmap/*.py` files ARE swept once tracked (the untracked-file hole is itself guarded, :41-58) | ✓ |
| osopen allow-list | `tests/test_arch_osopen_callers.py`; no new edge | test is AST-derived (`ALLOWED_FILES = {"osopen.py", "screens/map/opening.py"}`, :30-31) — a new launcher caller fails the test; `screens/relmap` dependency row (:197) names no osopen import; the pre-existing `relmap/model.py:30` `from mapper.osopen import MAX_EDGES, MAX_NODES` predates the batch and is the R1 allow-list entry — no amendment needed in any increment | ✓ |
| `mod_*` path censuses | `tests/test_mod_*` re-run | 7 files on disk: test_mod_{bodies,census,compat,deps,dispatch,parity,structure}.py; the package lands at the paths declared in the map row :165 | ✓ |
| R1 suite re-points | `test_relmap_model.py:17-26`, `test_relmap_descriptor.py:38`, `test_relmap_audit.py:33-35` | all exact — model import block :17-26 (`cut` :26, `DISPLAY_MAX` :18), descriptor `refusal_line` :38, audit HEADER :33 + descriptor `CAUSE, refusal_line` :34 | ✓ for tests — **but see F-ARCH-2 for the source side** |
| `cut` consumers (D2 move) | "every R1 relmap module" | my grep: `relmap/model.py:67` (def), `relmap/adapter.py:29` (`from mapper.relmap.model import Edge, Node, RelMap, build_map, cut`), `relmap/audit.py:37`, `relmap/descriptor.py:30`, `tests/test_relmap_model.py:26`. **adapter.py is a live old-path consumer and is NOT in Inc-1's SOURCE set** | ✗ see F-ARCH-2 |
| `refusal_line` consumers | double path collapses | def `descriptor.py:211`; re-export `audit.py:34` + `__all__` :209-210. My grep finds **zero** consumers of the `mapper.relmap.audit.refusal_line` path (all test imports go via `descriptor`), so dropping the re-export breaks nothing; `mapper/app.py:350` imports `relmap.audit` only for `structure_lines` | ✓ |
| `DISPLAY_MAX` consumers | moves to text.py | `model.py:34` (def), `tests/test_relmap_model.py:18` only — matches plan | ✓ |
| guard set | `test_fold.py` + `test_repair_artifact_claims.py` | both exist on disk; cited as C-1 in every targeted run (:112-114) | ✓ |
| `<name>.relmap.yml` tracked | none tracked | `git ls-files | grep relmap.yml` → empty (rc=1) | ✓ |
| `test_home*.py` | draft glob matched no file (P1 correction) | `ls tests/ | grep -i ^test_home` → empty; claim holds | ✓ |

## Freeze-set D1-D5 judgment (my lens)

Completeness/minimality of the freeze set itself: **D2, D3, D4, D5 are right-sized** — D2 is
consumed by every renderer (value cuts) plus the three re-points; D3 gates BINDINGS before any
lane forks (the ARC-02 reasoning is sound and matches the seat rule "every action is an
`action_*` method on the screen that owns the binding's scope", `keymap.py:148-149`); D4 is a
single-owner interface where freezing only pins the value 240 against drift; D5 is shared by
exactly the three lanes. Nothing over-frozen. D1 as drafted is **under-specified** (F-ARCH-1).

## Findings

### F-ARCH-1 — D1 omits the channel for renderer-owned toggle state (the `c` / `k` gap) [MAJOR]

- **What.** D1 freezes "the focused state the renderers receive (the derived `RelMap`, the
  focus/selection, the viewport `(w, h)`, the lens target, the cursor row, the host-supplied gap
  rows, the host-owned key/crumb slots) and the one paint entry each renderer exposes"
  (proposal §4 :183; record §D :91; map row :266). One-way state + one paint entry, nothing else.
- **Where.** The contract contradicts this shape in two places: LLR-RVS.3.3
  (`01-requirements.md:652-661`) — "The key binding and crumb slot are host-owned (RVH), the
  density state and note text are renderer-owned (RVS), split per the host↔renderer surface
  frozen at the R2 design review"; and LLR-RVG.1.5 (:548-556) — "When the operator presses `k`
  … the renderer shall regroup". But the seat rule puts the `c` and `k` actions on
  `RelMapScreen` (host), and the crumb (host-owned) must name the resulting mode
  (`sheet · direct only` ↔ `stacked chain`, RVS.3.3). So the host must reach renderer-owned
  state, and the renderer must publish it back to the host-owned crumb — through a surface D1
  does not describe.
- **Why it matters.** L2 (gaps) and L3 (sheet) hit this on day one. If D1 seals as-is, each lane
  improvises a different mechanism (options dict on paint, a second frozen entry, or host-owned
  state contrary to the LLR) — the exact mid-lane discovery that fork precondition F-3 makes a
  stop-and-re-cut, and the freeze exists precisely to prevent three lanes drifting apart.
- **Recommendation.** Amend D1 (proposal §4, record §D row D1, and the map's planned-freeze row
  :266) to name one shared mechanism: either the paint entry takes a view-state argument that
  includes the toggle flags with the host holding them, or each renderer exposes a frozen
  state-query/toggle entry the host's `action_*` calls — one mechanism, same for all three lanes.
  This is a text amendment at seal; it changes no file set.
- **Condition:** `COND-ARCH-1 · MAJOR · D1 must name the host↔renderer channel for renderer-owned toggle state (c density, k by-kind) before the seal · owner: trunk at seal (proposal §4 / record §D D1 / docs/ARCHITECTURE.md:266)`

### F-ARCH-2 — Inc-1's file set omits `mapper/relmap/adapter.py`, the fourth live consumer of the D2 old paths [MAJOR]

- **What.** The D2 freeze demands "one definition site, one import path" and Inc-1's exit check
  requires the reader census over the old paths (`relmap.model.cut`, `relmap.model.DISPLAY_MAX`,
  `relmap.descriptor.refusal_line`, `relmap.audit.refusal_line`) to be zero in the same increment
  (proposal :103, :184). My grep finds `mapper/relmap/adapter.py:29`:
  `from mapper.relmap.model import Edge, Node, RelMap, build_map, cut`.
- **Where.** `adapter.py` is in **neither** Inc-1's SOURCE set (text.py + model/descriptor/audit
  re-points = 4, :103) **nor** its census enumeration (:103 names only the three re-pointed
  test files). If `model.py` drops `cut`, adapter.py:29 ImportErrors; if `model.py` keeps a
  re-export so adapter survives, the old path stays live and the "zero references" exit check
  and the one-import-path freeze both fail. The only clean exit is adapter.py re-pointing to
  `mapper.relmap.text` — making Inc-1 SOURCE **5**, not 4.
- **Why it matters.** As planned, Inc-1 either breaks the build at exit or ships the two-import-
  path drift R1 DDR §E 10-11 explicitly rejected (proposal :300). The ≤4 count in §2.1, §8 and
  record §D row D6 would be wrong on the record's face.
- **Recommendation.** Either (a) add `mapper/relmap/adapter.py` to Inc-1 SOURCE (count 5 —
  permitted with the DDR row-7 review the record already carries, but the plan must say so), or
  (b) amend the D2 freeze text to state an explicit intra-package re-export policy — and in both
  cases name adapter.py in the §5.2 census and the Inc-1 exit check. My recommendation is (a);
  a permanent second import path is the worse inheritance.
- **Condition:** `COND-ARCH-2 · MAJOR · Inc-1 must own the adapter.py re-point (SOURCE becomes 5) or the D2 freeze text must explicitly permit intra-package re-export; census and §2.1 must name adapter.py either way · owner: trunk Inc-1 (plan + record amend at/before seal)`

### F-ARCH-3 — Three census citations the lanes will read at entry are wrong [MINOR]

- **`mapper/screens/palette.py:432`** (proposal §5.2 :238; contract LLR-RVH.4.4 draft-time
  :799) — the file is 218 lines; the seat-derived BINDINGS block is :35-38. Phantom pin.
- **keymap "uniqueness rule :9-12"** (§5.2 :237; LLR-RVH.4.1 draft-time :784) — :9-12 is
  docstring; the rule is the `LLR-N03.6` comment at `mapper/keymap.py:25` with the enforcement
  function `duplicate_chords()` at :445.
- **`tests/test_key_dispatch.py:137`** (§5.2 :237) — :137 is inside the EXPECTED data table;
  the whole-seat pin assertion is `test_at_n03h_the_whole_seat_matches_its_specification` at
  :170 (table header comment :30-49).
- **Why it matters.** F-4 makes these pins the lanes' entry reading; a lane agent chasing a
  phantom line burns a round trip, and the §5.2 census is the one artifact the crossed census
  is re-derived from.
- **Condition:** `COND-ARCH-3 · MINOR · repair the three census citations (palette.py:35-38; keymap.py:25+:445; test_key_dispatch.py:170) in the contract draft-time fields and proposal §5.2 · owner: trunk at seal`

## Verified-true highlights (no finding, evidence for the merge)

- F-1..F-5 as quoted (`01-requirements.md:270-274`) match the proposal's §2.8 quotation
  verbatim (:120-129); each is mechanically checkable at the named gate (F-1: LLR census +
  re-count; F-2: the :266 row flips PLANNED→frozen at seal; F-3: the §6 worksheet
  intersections, :352-356; F-4: the §5.2 table per lane packet; F-5: the two probe files exist
  and lanes 3-5 re-verify at entry).
- The rejected keymap-in-shell-lane alternative (:298) is correctly reasoned: `RelMapScreen`
  cannot generate BINDINGS without the seat, so the ARC-02 trunk move is the only F-2/F-3-
  compatible home for it.
- R1's PD-3 (:73, :114) left `refusal_line`/`format_structure` as tested seams, not frozen — so
  R2's D2 freeze relitigates nothing from R1.
- The `osopen.py:93-94` citation for the 100,000-node cap is correct *and* non-obvious:
  `mapper/relmap/model.py:30` imports `MAX_NODES`/`MAX_EDGES` from `mapper.osopen`.
- AT-driver seam: `MapperApp.__init__(workspace=…)` at `app.py:250`, `MapStore(workspace)` at
  :256 (grep -n exact); `run_test()` pilot idiom at `tests/test_colour_always_on.py:64`.
- Over-freezing: none found. Under-freezing beyond F-ARCH-1: none — renderers may import
  `canvas`/`design`/`widgets` directly per the :197 dependency row, so no token/theme channel
  needs the host.

## Verdict

approved with conditions — COND-ARCH-1 (MAJOR, D1 toggle-state channel, trunk at seal) ·
COND-ARCH-2 (MAJOR, Inc-1 owns adapter.py re-point / D2 re-export policy, trunk Inc-1) ·
COND-ARCH-3 (MINOR, three census citation repairs, trunk at seal). All three are text-level
discharges: none re-cuts a lane or moves a boundary. Re-review = re-read the amended D1 row,
the Inc-1 SOURCE row, and the three citations; no code exists yet to re-run.
