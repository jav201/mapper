# ARQ note — mapper — Batch 2026-10-15-review-screen-batch

> **Artifact language.** English (`state.json` `language: en`).
> **Station:** ARQ, activated by the P0 trigger evaluation (`PLAN.md` §Triggers: **A2** the batch touches two or more modules, **A3** an exposed contract changes — the keymap seat's scope set grows).
> **Status:** drafted for `architect` review; the operator approves the map (station gate). Nothing here edits `docs/ARCHITECTURE.md`; the amendment it asks for is listed in §1.2 and lands in the owning increments (RS2 for the `screens`/`app`/`keymap` rows), not in this note.
> **Evidence base:** worktree `feat/review-screen-batch`; the ReqHarness core on `master` (`3a70ff8`) was read at `mapper/reqharness/{config,chain,reviews,derive,release,identity,records}.py`. Every `file:line` below was read at that commit.

## 0 · Verdict in one paragraph

No module boundary moves and no dependency edge is added. **One §2 row amendment is owed (F1):** `mapper/screens/review.py` (new, RS2) is claimed by the `screens` row — which names its files *literally*, so a second new screen file is unclaimed until the row gains it (the same stale-map shape as `roles.py` in the fixes batch). `mapper/reqharness/signing.py` (new, RS1) needs **no** §2 change: the `reqharness` row already owns `mapper/reqharness/*.py` by glob. `screens/review.py` imports `reqharness` and Textual — both edges already exist on the `screens` row. The one exposed contract that changes (A3) is the **keymap seat**: a new `review` scope and a home door key, both additive; every consumer was read and is safe (§2).

## 1 · Module map impact

### 1.1 What was checked (executed)

| Check | Command / source | Result |
|---|---|---|
| New product files | `ls mapper/screens/review.py mapper/reqharness/signing.py` | neither exists — both are new this batch |
| `signing.py` claimed by a §2 row | §2 `reqharness` row `Paths it owns` = `mapper/reqharness/*.py` | claimed (glob) — no §2 change |
| `review.py` claimed by a §2 row | §2 `screens` row lists 16 literal paths (…`home.py`, `roles.py`) — no `review.py` | **unclaimed — F1, the amendment below** |
| Dependency edges used by the change | `signing.py` imports `config`, `chain`, `derive`, `reviews` (all inside `reqharness`, already a leaf of each — `derive` already imports `reviews`, and `signing` imports both, so no cycle); `screens/review.py` imports `reqharness` (the one `screens` → core edge, already granted for `roles.py` in §3) and Textual (the `screens` row already imports Textual) | **0 new edges** |
| The map-truth test that parses §2 | `tests/test_repair_map_truth.py:43` parses the `Paths it owns` table; its path arm asserts every declared path exists on disk | adding `mapper/screens/review.py` passes; the file must not be created before the row names it |

### 1.2 The map diff this batch owes

Not empty. The minimum, one commit each, **no later than the commit that first creates each file** (docs files, outside the source cap):

1. **RS2 owns it:** §2 `screens` row, `Paths it owns`: append `` `mapper/screens/review.py` `` (F1), and in the ownership prose after the `roles.py` clause add *"`review.py` owns `ReviewScreen`"*, and `ReviewScreen` to its exposes list.
2. **RS2 owns it:** §2 `app` row `What it EXPOSES` — add `ReviewScreen` to the re-export list (it already names `RolesScreen`; `app.py` re-exports `ReviewScreen` under LLR-MOD.3.1). §4 `KEYMAP` seat row: note the new `review` scope + door key (the row already declares `KEYMAP: list[KeyBinding]`; the note records the additive change for the A3 oracle).
3. **RS2 owns it (A5):** §3 dependency rows — the `screens` row's dependency list gains `reqharness` for `review.py` (naming `screens/review.py` as allowed to import `reqharness`), and the `reqharness` row's exposes list gains `entitled_to_sign`, `sign_review` and the `authors` schema, with the prose "only `screens/review.py` imports `signing`".
4. Header: `Last amended by` → `2026-10-15-review-screen-batch (ARQ)`; `Date` → the landing date.
5. A short amendment block in the file's established style: "no boundary moves, no dependency edge added; one new screen file claimed on the existing `screens` row; one additive seat change (a new `review` scope and a home door key); the `reqharness` row's glob already covers the new `signing.py`."

**Evidence of "no boundary change" is therefore: items 1–5 are the entire diff, and `git diff -- docs/ARCHITECTURE.md` after the batch will show only them.**

## 2 · Exposed-contract change (A3) and every consumer

The seat's scope set grows: `SCOPE_REVIEW = "review"` (and the `review-leave` leave group), plus one home door key. The rows are **additive** — no existing `KeyBinding` key, glyph, action or label changes, so no existing screen's `BINDINGS`, key bar or legend moves.

| Consumer (file:line) | What it reads | Effect | Why safe |
|---|---|---|---|
| `mapper/keymap.py` `GROUP_SCOPE` / `GROUP_HEADER` | the `review` group → scope + header | two new entries | additive; `bar_group_order` and `groups_for_keybar` derive from the dict, so the new group paints only on the review scope |
| every screen via `screen_bindings(scope)` → `textual_bindings` | the scope's rows | the new scope is read only by `ReviewScreen`; no other screen names it | a scope nobody reads is inert; no dispatch change |
| `mapper/screens/home.py` `_empty_text` / `_DOOR_NOTES` | the home door list | one new door row | the door list is built from `bindings_for(SCOPE_HOME)`, filtered by `_DOOR_NOTES`; the new key must be added to `_DOOR_NOTES` in the same increment (RS2) or the door would not paint |
| `tests/test_key_dispatch.py:177-179` | `len(actual) == len(keymap.KEYMAP)` | the whole-seat count pin moves by the number of new rows | re-baselined in RS2 (the pin is a tautology-guard, not a behaviour assertion) |
| `tests/test_keymap.py::test_at_n03a_every_binding_resolves_to_a_real_action` (line 123) and `test_at_n03f_bound_keys_match_the_seat_exactly` (line 148) | every action has a method; per-scope keys match | the new `review` scope's actions must resolve on `ReviewScreen` | satisfied in RS2, where the screen and the seat land together |
| `tests/test_inc3_census.py`, `tests/test_inc4_census.py`, `tests/test_inc9c.py` | key/keybar censuses | new rows enter the censuses | additive; re-baselined in RS2 |

Census of the new key chords: `v` (home door), and in the new `review` scope `up`/`down`/`4`/`b`/`enter` (confirm) with `q`/`escape` in `review-leave`. `grep -nE '"v"|"b"|"4"' mapper/keymap.py` → no hits today; `enter` exists only in `list`/`nav`/`palette` scopes (lines 165/173/240), never in a scope the review screen inherits. The door key `v` is free in the home scope (home owns `c p n t i f r R s j k enter q`).

## 3 · The signing core (RS1a) — a headless leaf, no cycle

`mapper/reqharness/signing.py` exposes `entitled_to_sign(repo, object_id, identity_email) -> (bool, reason)` and `sign_review(repo, object_id, identity_email, *, confirm_digest, confirm_head) -> Path`. It sits at the *leaf* of the `derive`/`reviews` subgraph: it imports `config` (`load_config`, `config_digest`), `chain` (`verify_chain`, `effective_roles`), `derive` (`load_canon`, `object_digests`), `reviews` (`record_review`, `next_seq`), `identity` (the email → person resolution), and `records` (`ValidationError`). `derive` imports `reviews`; `signing` imports both and nothing imports `signing` except the screen and the tests — so there is no cycle, and the module stays headless (stdlib + PyYAML + `osopen` via the `reviews`/`config` write paths, no Textual, no Rich). **A3:** `signing` itself takes the git identity EMAIL, hashes it and resolves to exactly one declared person (zero/several → a named refusal) — the screen no longer resolves the person first. This records the R1 override of the P0 spike's draft signature (`sign_review(repo, *, object_id, class_id, verdict, reviewer, kind, note, now=None)`): R1 drops `class_id` (from the object id prefix), `verdict`/`kind`/`note` (fixed: `verdict="reviewed"`, `kind="human"`, `note=""`), and gains the two TOCTOU confirm parameters; the PDR (A3) re-points `viewer` to `identity_email`.

## 4 · Findings carried to the PDR

- **F1 (map stale).** `review.py` unclaimed until the §1.2 amendment; owner RS2 (the file's increment), lands before the file is created.
- **F2 (ordering).** The seat's new `review`-scope rows must land *after* `ReviewScreen`'s `action_*` methods exist, or `test_at_n03a_every_binding_resolves_to_a_real_action` fails mid-batch; the increment order RS1a → RS1b → RS2 already yields this.
- **F3 (a model review is never written).** `sign_review` always writes `kind="human"`; `derive` keeps treating `kind="model"` as pre-review (LLR-RH.4.3). The screen never offers a model sign-off; a model review can only enter via a hand-authored file, and derive already downgrades it.

## 5 · Gate

Approve the map as amended in §1.2, or iterate with the named gap. No code, test, `state.json` or `docs/ARCHITECTURE.md` edit was made to produce this note.
