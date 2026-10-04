"""`A-105` -- the sparkline's zero-activity floor, and `INC7-CR-R3-F3`'s regression.

`HomeScreen._sparkline_text` (`app.py:561-588`) computes
`max_count = max(counts) if counts else 1`. `counts` always has 14 entries (one
per day in the activity window), so the `else 1` branch can never fire. When
every entry is `0` -- no `.mmd` in the workspace was modified in the last 14
days -- `max_count` is `0` and `c / max_count` (`app.py:584`) raises
`ZeroDivisionError`, crashing the home screen for any workspace idle two weeks
or more.

`INC7-CR-R3-F3` (`increment-020-inc7-corrective-2.md`, round 3;
`state.json`'s `p3_progress.NEW_FINDING_ROUTED_TO_OPERATOR`) measured exactly
this crash against this repo's own `fixtures/` directory, because its newest
mtime (`truncado.mmd`, 2026-09-11) had drifted past the 14-day window by the
time the suite ran.

THIS MODULE'S FIXTURES ARE BUILT FROM `date.today()`, NOT FROM A FIXED
CALENDAR DATE. `_touch` takes a `date` and sets the mtime to LOCAL NOON on
that date (`datetime.combine(day, time(12))`) -- never an offset such as
`time.time() - N * 86400`, which can land on the wrong side of midnight near
a DST transition. That is deliberately different from
`tests/test_agree_floor.py`'s pre-existing hermeticity defect (checked-in
fixtures with a fixed mtime, which drift stale): this module's own arms are
not permitted to share that defect.

`INC21-CR-F1` (the independent review of `increment-021`) found that the
first two arms below cannot distinguish a correct `max(counts)` from a wrong
`sum(counts)`, nor from a binary "any activity -> full bar" tier, because both
of their fixtures put activity on exactly one day -- the true maximum and the
true sum are numerically identical there. The third arm,
`test_a105_two_days_of_activity_scale_relative_to_each_other`, puts activity
on two distinct days with different weights so those mutants are
distinguishable; see its docstring for the by-hand derivation of its expected
glyphs, and `increment-021`'s "review round" section for the mutant proof.

Residual race, and the choice made about it: any fixture using TODAY as an
activity day is set at local noon of `date.today()` when the test starts, but
`_sparkline_text` calls `date.today()` again when it runs. If the calendar
date changes between those two calls (a test straddling local midnight), the
day used to build the expected bars would disagree with the day the code
computed. Rather than accept and document that (vanishingly small) window,
each TODAY-dependent arm below re-checks `date.today()` right after computing
the bars and SKIPS if it moved -- the race is removed, not merely bounded.
"""
from __future__ import annotations

import os
from datetime import date, datetime, time, timedelta

import pytest

from mapper.app import HomeScreen

#: `bars = "▁▂▂▃▃▄▅▆▇█"` at `app.py:581` -- index 0 is the floor tier, index 4
#: the midpoint the third arm below lands on, index 9 the maximum tier.
FLOOR_GLYPH = "▁"  # bars[0]
MID_GLYPH = "▃"  # bars[4]
MAX_GLYPH = "█"  # bars[9]

_CAPTION = "activity 14d  "


def _touch(path, day: date) -> None:
    """Set `path`'s mtime to LOCAL NOON on `day`.

    `HomeScreen._sparkline_text` buckets activity by
    `date.fromtimestamp(mtime) == d`. Noon keeps the mtime safely inside
    `day`'s calendar date; an offset such as `time.time() - N * 86400` can
    land on the wrong side of midnight near a DST transition, which noon
    cannot.
    """
    stamp = datetime.combine(day, time(12)).timestamp()
    os.utime(path, (stamp, stamp))


def _bars(store) -> str:
    """The 14 sparkline glyphs, with the "activity 14d  " caption stripped."""
    text = HomeScreen()._sparkline_text(store)
    plain = text.plain
    assert plain.startswith(_CAPTION), plain
    bars = plain[len(_CAPTION):]
    assert len(bars) == 14, f"expected 14 bars, got {len(bars)!r} ({bars!r})"
    return bars


def test_a105_a_zero_activity_workspace_paints_every_bar_at_the_floor(tmp_store):
    """`A-105` / `INC7-CR-R3-F3` -- the escaped-bug regression.

    No `.mmd` in the workspace was modified in the 14-day window (the only
    file is 20 days old). On the unfixed code
    `max_count = max(counts) if counts else 1` leaves `max_count == 0` and
    `app.py:584` raises `ZeroDivisionError`. Fixed, the screen must not raise
    and every one of the 14 bars must sit at the floor glyph.

    `INC21-CR-F5`: `tests/test_agree_floor.py` exercises this same
    zero-activity path only INCIDENTALLY, when its checked-in fixtures happen
    to be stale enough (17 days, at the time this was written) -- on a fresh
    checkout its fixtures are all recent and it never reaches `max_count == 0`
    at all. `HomeScreen`'s "shall not raise" clause therefore rests on THIS
    arm, which builds its own zero-activity fixture and calls
    `_sparkline_text` directly rather than mounting the full screen.
    """
    idle = tmp_store.workspace / "idle.mmd"
    idle.write_text("graph TD\n  a --> b\n", encoding="utf-8")
    _touch(idle, date.today() - timedelta(days=20))

    bars = _bars(tmp_store)

    assert bars == FLOOR_GLYPH * 14, (
        f"a zero-activity workspace should paint all 14 bars at the floor "
        f"glyph {FLOOR_GLYPH!r}, got {bars!r}"
    )


def test_a105_activity_today_lights_exactly_the_last_bar(tmp_store):
    """`A-105`'s complementary arm -- the zero-activity guard must not flatten real activity.

    One map modified TODAY, one idle for 20 days. Only the last (today's) bar
    should reach the maximum tier; the other 13 stay at the floor. This is
    what distinguishes a correct minimal guard from an over-broad one that
    also floors genuine activity.

    `INC21-CR-F1`: this fixture alone cannot distinguish `max(counts)` from
    `sum(counts)` or from a binary "any activity -> full bar" tier -- both
    those wrong quantities equal `1` here, same as the true maximum. See
    `test_a105_two_days_of_activity_scale_relative_to_each_other`, below, for
    the arm that does distinguish them.
    """
    today = date.today()

    idle = tmp_store.workspace / "idle.mmd"
    idle.write_text("graph TD\n  a --> b\n", encoding="utf-8")
    _touch(idle, today - timedelta(days=20))

    fresh = tmp_store.workspace / "fresh.mmd"
    fresh.write_text("graph TD\n  a --> b\n", encoding="utf-8")
    _touch(fresh, today)

    bars = _bars(tmp_store)

    if date.today() != today:
        pytest.skip("the calendar date changed between setup and assertion (midnight race)")

    assert bars == FLOOR_GLYPH * 13 + MAX_GLYPH, (
        f"one map modified today should light exactly the last bar at the max "
        f"tier {MAX_GLYPH!r}, with the other 13 at the floor {FLOOR_GLYPH!r}; "
        f"got {bars!r}"
    )


def test_a105_two_days_of_activity_scale_relative_to_each_other(tmp_store):
    """`A-105` / `INC21-CR-F1` -- max_count must be the true maximum, not the sum.

    The two arms above each put activity on exactly one day, where the real
    maximum and the real sum are numerically identical -- so neither catches
    `max_count = max(1, sum(counts))` (`M6`), nor a binary tier
    `idx = 9 if c else 0` (`M7`). This arm puts activity on TWO distinct days
    with different weights, so a wrong denominator or a wrong tiering scheme
    paints a different bar than the correct one.

    Setup: two maps modified 3 days ago (count 2 that day), one map modified
    today (count 1). Correct `max_count = max(counts) = 2`.

    Expected, computed by hand against `bars = "▁▂▂▃▃▄▅▆▇█"` (`app.py:581`)
    and `idx = min(9, int(c / max_count * 9))` (`app.py:584`), not copied from
    any reviewer figure:
      - today:      c=1, max_count=2 -> idx = int(1 / 2 * 9) = int(4.5) = 4
                    -> bars[4] = "▃" (`MID_GLYPH`)
      - 3 days ago: c=2, max_count=2 -> idx = int(2 / 2 * 9) = int(9.0) = 9
                    -> bars[9] = "█" (`MAX_GLYPH`)
      - every other day: c=0 -> idx = 0 -> bars[0] = "▁" (`FLOOR_GLYPH`)

    In the 14-character output today is the LAST character (index `-1`), and
    3 days ago is 3 positions before it (index `-4`).
    """
    today = date.today()

    old1 = tmp_store.workspace / "old1.mmd"
    old1.write_text("graph TD\n  a --> b\n", encoding="utf-8")
    _touch(old1, today - timedelta(days=3))

    old2 = tmp_store.workspace / "old2.mmd"
    old2.write_text("graph TD\n  a --> b\n", encoding="utf-8")
    _touch(old2, today - timedelta(days=3))

    fresh = tmp_store.workspace / "fresh.mmd"
    fresh.write_text("graph TD\n  a --> b\n", encoding="utf-8")
    _touch(fresh, today)

    bars = _bars(tmp_store)

    if date.today() != today:
        pytest.skip("the calendar date changed between setup and assertion (midnight race)")

    expected_chars = list(FLOOR_GLYPH * 14)
    expected_chars[-4] = MAX_GLYPH
    expected_chars[-1] = MID_GLYPH
    expected = "".join(expected_chars)

    assert bars == expected, (
        f"two maps 3 days ago (the true max) and one map today (half that) "
        f"should give bars[-4]={MAX_GLYPH!r} and bars[-1]={MID_GLYPH!r}, with "
        f"the other 12 at the floor {FLOOR_GLYPH!r}; got {bars!r}"
    )
