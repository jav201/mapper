"""`A-105` -- the sparkline's zero-activity floor, and `INC7-CR-R3-F3`'s regression.

`HomeScreen._sparkline_text` (`app.py:561-583`) computes
`max_count = max(counts) if counts else 1`. `counts` always has 14 entries (one
per day in the activity window), so the `else 1` branch can never fire. When
every entry is `0` -- no `.mmd` in the workspace was modified in the last 14
days -- `max_count` is `0` and `c / max_count` (`app.py:579`) raises
`ZeroDivisionError`, crashing the home screen for any workspace idle two weeks
or more.

`INC7-CR-R3-F3` (`increment-020-inc7-corrective-2.md`, round 3;
`state.json`'s `p3_progress.NEW_FINDING_ROUTED_TO_OPERATOR`) measured exactly
this crash against this repo's own `fixtures/` directory, because its newest
mtime (`truncado.mmd`, 2026-09-11) had drifted past the 14-day window by the
time the suite ran.

THIS MODULE'S FIXTURES ARE BUILT FROM `date.today()`, NOT FROM A FIXED
CALENDAR DATE -- `os.utime` sets each `.mmd`'s mtime relative to *now*, so the
verdict here does not depend on which day the suite runs. That is deliberately
different from `tests/test_agree_floor.py`'s pre-existing hermeticity defect
(checked-in fixtures with a fixed mtime, which drift stale): this module's own
arms are not permitted to share that defect.
"""
from __future__ import annotations

import os
import time

from mapper.app import HomeScreen

#: `bars = "▁▂▂▃▃▄▅▆▇█"`
#: at `app.py:576` -- index 0 is the floor tier, index -1 the maximum tier.
FLOOR_GLYPH = "▁"  # "▁"
MAX_GLYPH = "█"  # "█"

_CAPTION = "actividad 14d  "


def _touch(path, days_ago: float) -> None:
    """Set `path`'s mtime to `days_ago` days before *now* -- deterministic on any date."""
    stamp = time.time() - days_ago * 86400
    os.utime(path, (stamp, stamp))


def _bars(store) -> str:
    """The 14 sparkline glyphs, with the "actividad 14d  " caption stripped."""
    text = HomeScreen()._sparkline_text(store)
    plain = text.plain
    assert plain.startswith(_CAPTION), plain
    bars = plain[len(_CAPTION):]
    assert len(bars) == 14, f"expected 14 bars, got {len(bars)!r} ({bars!r})"
    return bars


def test_a105_a_zero_activity_workspace_paints_every_bar_at_the_floor(tmp_store):
    """`A-105` / `INC7-CR-R3-F3` -- the escaped-bug regression.

    No `.mmd` in the workspace was modified in the 14-day window (the only
    file is 20 days old, set relative to `date.today()`). On the unfixed code
    `max_count = max(counts) if counts else 1` leaves `max_count == 0` and
    `app.py:579` raises `ZeroDivisionError`. Fixed, the screen must not raise
    and every one of the 14 bars must sit at the floor glyph.
    """
    idle = tmp_store.workspace / "idle.mmd"
    idle.write_text("graph TD\n  a --> b\n", encoding="utf-8")
    _touch(idle, days_ago=20)

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
    """
    idle = tmp_store.workspace / "idle.mmd"
    idle.write_text("graph TD\n  a --> b\n", encoding="utf-8")
    _touch(idle, days_ago=20)

    fresh = tmp_store.workspace / "fresh.mmd"
    fresh.write_text("graph TD\n  a --> b\n", encoding="utf-8")
    _touch(fresh, days_ago=0)

    bars = _bars(tmp_store)

    assert bars == FLOOR_GLYPH * 13 + MAX_GLYPH, (
        f"one map modified today should light exactly the last bar at the max "
        f"tier {MAX_GLYPH!r}, with the other 13 at the floor {FLOOR_GLYPH!r}; "
        f"got {bars!r}"
    )
