# Requirements ledger — mapper — Batch 2026-10-09-hygiene-batch

> Append-only. Entries are added in chronological order and never rewritten. The live
> contract is `01-requirements.md`; this file records how it came to say what it says.
> Every entry names the requirement it amends; every requirement names its entries. `V26`
> compares the two sets of pairs both ways.

_No entries yet. The first amendment to the live contract writes the first one, in the
shape the field guide's §7 shows (`req-template.md` in the guide directory init prints), and nothing
above this line is ever edited._

### LED-2026-10-09-hygiene-batch.1 — QA-1 (major): AT-061's negative control names the real failure
- **Requirement:** HLR-001
- **Date:** 2026-10-09
- **What changed:**
  - AT-061's control now says the walk wedges: the later `ctrl+q` opens no guard. It no longer says "a second guard stacks".
  - Two Phase-3 mutants are named.
  - The docstring tagging mechanism (QA-4) and the regression set (the QA regression-checklist ✗) are stated.
- **Why:** `_guard_draft` returns silently when its guard is already open (`app.py:3474-3475`), so a second guard can never stack. The test fails at its second `_guards(app) == 1`.
- **Evidence:** 02-review.md round 1, QA-1 and QA-4; `tests/test_draft_exits.py:168-188`.

### LED-2026-10-09-hygiene-batch.2 — QA-2 / ARCH-3 (minor): the writers outside `MapScreen` are named
- **Requirement:** LLR-001.1
- **Date:** 2026-10-09
- **What changed:**
  - The reverse census names `screens/factory.py:219` and `app.py:1167` as `_save_or_toast` callers that are not `MapScreen`.
  - The write at `:299` stays, with a comment.
  - The `or "error"` fallback is kept for `None`.
  - "What would change this" is stated.
- **Why:** declaring the slot only on `MapScreen` leaves the helper's write untyped on other screens. That is harmless, because nothing reads it there. A return-value redesign is bigger than this batch.
- **Evidence:** 02-review.md round 1, QA-2 and ARCH-3; `grep -rn _save_or_toast mapper`.

### LED-2026-10-09-hygiene-batch.3 — QA-3 / ARCH-2 (minor): the structural checks assert intent and say what they miss
- **Requirement:** LLR-001.1, LLR-001.2
- **Date:** 2026-10-09
- **What changed:**
  - Each LLR now has a behaviour check: the slot is `None` on a fresh screen, and `guard_open()` follows the guard through real keys.
  - Each LLR also has an AST check over the whole `mapper/` package.
  - The `vars()`/`__dict__` blind spot is stated.
- **Why:** a source grep alone passes after a rename and does not check intent.
- **Evidence:** 02-review.md round 1, QA-3 and ARCH-2.

### LED-2026-10-09-hygiene-batch.4 — ARCH-1 (minor): F5 is unreachable, not rare
- **Requirement:** HLR-001
- **Date:** 2026-10-09
- **What changed:** the F5 reason in §6.2 now says the case is unreachable. It no longer says a hand-renamed file could cause it.
- **Why:** `store.load` and `store.save` share `check_map_id` on the same id, so a refused id never opens.
- **Evidence:** `mapper/store.py:681`, `:810` (read 2026-10-09).

### LED-2026-10-09-hygiene-batch.5 — P2 round 2 (minor A): the test-file count is stated
- **Requirement:** HLR-001
- **Date:** 2026-10-09
- **What changed:** the Tagging line now names the new fourth test file, `tests/test_draft_hygiene.py`, and states that tests are outside the source-file cap.
- **Why:** the round-2 QA confirmation noted that "touched for the tag only" read as if the batch touched only three test files.
- **Evidence:** 02-review.md round 2.
