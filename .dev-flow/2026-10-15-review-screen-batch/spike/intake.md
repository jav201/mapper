# Intake spike — ReqHarness REVIEW / SIGNING screen (B-134)

> P0 intake for `2026-10-15-review-screen-batch`. Read-only spike; no product or test change.
> The verdict that binds this batch is `prototypes/review_screen/NOTES.md` §Verdict (2026-10-15):
> **variant A (list + detail)** adopted; variant C's queue becomes a **filter preset** of A ("needs action");
> signing asks a **second confirmation key** (`b` shows digest + head, a second key confirms); release
> readiness lives in a **fixed bottom band**; the informative change stays a **mark on the object** (`⁂`
> badge in the detail pane), not a filter pseudo-state.

## Objective

Implement the B-134 verdict end to end: a review/signing screen reached from home by one key that shows every
canon object with its derived state and, for the selected object, who reviewed what at which head and digest —
and lets an entitled reviewer sign an object through the existing `reviews.record_review` API, with the
two-key confirmation, the "needs action" filter preset, the bottom release band, and the informative-change
badge.

## Scope

**IN**

- The review/signing screen (variant A list + detail) — `mapper/screens/review.py`.
- Its home door + keymap seat (new `review` scope + home door key).
- The signing write path through the existing `reviews` API — realised as a new headless `sign_review`
  orchestration (see "core gaps" below).
- The "needs action" queue filter preset.
- The bottom release band (mandatory rules + verdict).
- The informative-change badge (`⁂`) in the detail pane.

**OUT** (later batches, each with a prototype round first unless the verdict is already given)

- Baseline/release VIEW screen — follow-up, prototype round first.
- US canon + AT → test-node extraction; generated MD/HTML views — follow-up.
- B-124 (committer-vs-reviewer email warning): the screen signs; it does not diff commit-vs-reviewer. OUT.
- B-125 (baseline `reactivated` + review-state progression): no baseline view here. OUT.
- B-126 (fork-recovery UI): the screen is read-only under tamper/fork; recovery stays core-only. OUT.

## What the core already provides vs what is missing (the core-gap census)

Read against `mapper/reqharness/` on `master` (`a5fd158`). Anything missing becomes the RS1 core increment.

| Need | Provided? | Evidence (file:line) |
|---|---|---|
| Review WRITE API (low-level) | PRESENT | `reviews.record_review` (`reviews.py:142`) — content-named + exclusive create; `next_seq` (`reviews.py:206`). But it is a raw primitive: the caller supplies `head`, `seq`, both digests, verdict, reviewer, kind, note. |
| Signer identity | PRESENT | `identity.read(repo) -> Identity` (`identity.py:221`); `email_sha256` (`config.py:370`) matches git email to a `Person`. |
| Content digest at sign time | PARTIAL — caller-computed | `derive.object_digests(cls, fields)` (`derive.py:178`) computes normative/informative digests; `load_canon`/`parse_canon` (`derive.py:155/110`) yield the object fields. No single "sign this object" call wires them. |
| Head binding at sign time | PARTIAL — caller-fetched | `verify_chain(repo).head` (`chain.py:144-150`) gives `(roles_seq, roles_hash)`; `record_review` records it. No orchestrator binds it automatically. |
| Role-entitlement check (pre-flight) | MISSING as a callable | `derive._role_in_force` (`derive.py:190`) checks at DERIVE time (an unentitled signer's review derives `pre-reviewed`); there is no exposed "may this person sign this class" predicate the screen can run BEFORE writing. The prototype requires `b` to REFUSE before writing, not write-then-derive-pre-review. |

**The one core gap → RS1:** a headless `mapper/reqharness/signing.py` exposing
`entitled_to_sign(config, report, person, class_id) -> (bool, str)` and
`sign_review(repo, *, object_id, class_id, verdict, reviewer, kind, note, now=None) -> Path`, orchestrating
`load_config` → `verify_chain` (refuse on `status != STATUS_VERIFIED`) → `load_canon` → resolve the object →
`object_digests` → the entitlement pre-flight (the signer holds the class's `reviewer_role` in
`effective_roles(report)` at the current head) → `next_seq` → `record_review` with the bound head. Named
refusals: chain not verifiable · object id unknown · signer not entitled · unparseable canon row. It must be a
NEW module, not an addition to `reviews.py` — it imports `derive`, and `derive` imports `reviews` (a cycle).

## Risks

- **Immutability** — a review record is immutable once written (content-named, exclusive create; a correction
  is a NEW event). The confirmation key is the only guard between a keystroke and a permanent record; it must
  be implemented exactly and driven by the AT.
- **Self-signing rules** — the canon object carries no author field, so there is no self-review rule; the
  core's no-self-approval applies to ROLE changes only (`chain._passes_approval`, `chain.py:304`). A signer
  need only hold the class's reviewer role. Residual flagged, out of scope.
- **Signing on a tampered/forked chain** — `sign_review` refuses when `verify_chain` is not `STATUS_VERIFIED`;
  the screen paints read-only. Core-enforced; low likelihood.
- **Concurrent signers** — review files have no append lock; exclusive create turns an identical-content
  collision into a named refusal, and two different reviews of one object are two distinct content-named files
  resolved by the R5 precedence at derive. One TUI; low likelihood.
- **A model review counting only as pre-review** — `kind` is self-declared; `derive` already treats
  `kind: model` as pre-review (`LLR-RH.4.3`). The screen surfaces the kind honestly and never lets a model
  review close a state.

## Draft increment plan (≤ 4 source files each)

1. **RS1 — signing core** — `mapper/reqharness/signing.py` + `tests/test_reqharness_signing.py` (1 source file).
2. **RS2 — review screen** — `mapper/screens/review.py` + `tests/test_review_screen.py` (1 source file).
3. **RS3 — seat + home + app** — `mapper/keymap.py` · `mapper/screens/home.py` · `mapper/app.py` (3 source files,
   one owner increment) + door-count regression re-pin.

Total: 5 source files across 3 increments; tests uncapped.
