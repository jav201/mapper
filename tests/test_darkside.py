"""Tests for darkside design-system primitives."""
from datetime import date, timedelta

import pytest

from mapper import darkside


def test_moon_phases():
    # Known new moon on 2000-01-06.
    glyph, name = darkside.moon(date(2000, 1, 6))
    assert name == "new"
    # Full moon is about half a synodic month later.
    full = date(2000, 1, 6) + timedelta(days=14.765)
    glyph, name = darkside.moon(full)
    assert name == "full"


def test_step_meter_basic():
    text = darkside.step_meter(4, 5)
    assert text.plain == "▰▰▰▰▱"


def test_step_meter_complete():
    text = darkside.step_meter(5, 5)
    assert text.plain == "▰▰▰▰▰"


def test_step_meter_zero():
    text = darkside.step_meter(0, 3)
    assert text.plain == "▱▱▱"


def test_tab_strip_has_tabs():
    text = darkside.tab_strip("c")
    plain = text.plain
    assert "consultar" in plain
    assert "repo" in plain
    assert "construir" in plain
    assert "fábrica" in plain
    assert "mapper" in plain


def test_tab_strip_crumb():
    text = darkside.tab_strip("c", crumb=["sistema-legacy", "auth"])
    plain = text.plain
    assert "sistema-legacy" in plain
    assert "auth" in plain


def test_keybar_renders_groups():
    groups = [("nav", [("j", "down"), ("k", "up")]), ("app", [("q", "quit")])]
    text = darkside.keybar(groups)
    plain = text.plain
    assert "nav" in plain
    assert "j" in plain
    assert "down" in plain
    assert "app" in plain
    assert "q" in plain


def test_draw_number_renders_block_digits():
    text = darkside.draw_number("12")
    assert "1" not in text.plain
    assert "2" not in text.plain
    assert text.plain.count("█") > 0


def test_microbar_floor_never_zero_when_present():
    text = darkside.microbar(1, 100)
    plain = text.plain
    assert "█" in plain
    # Track uses WORDMARK glyph.
    assert "░" in plain


def test_time_row_has_today_rule_column():
    text = darkside.time_row("main", 0, "●", darkside.INK, "hoy")
    assert "main" in text.plain
    assert "╎" in text.plain
    assert "●" in text.plain


def test_time_row_older_event_placed_left_of_today():
    text = darkside.time_row("old", 15, "●", darkside.INK, "hace 15 d")
    today_idx = text.plain.index("╎")
    event_idx = text.plain.index("●")
    assert event_idx < today_idx


# ---------------------------------------------------------------------------
# darkside.plain() — the single coercion helper for file-derived text.
#
# It had NO direct tests. Its only exercise was AT-N01e, whose control payload is
# a single ESC, so narrowing the whole map to `{0x1B: "�"}` left the suite at
# 210 passed while NUL, BEL and the C1 introducers passed through verbatim to the
# terminal. The range is now asserted as a range.
# ---------------------------------------------------------------------------


def test_plain_replaces_every_c0_control_except_tab_and_newline():
    """Derived from the RULE (the C0 range), not from the bytes the code handles."""
    for code in range(0x00, 0x20):
        ch = chr(code)
        out = darkside.plain(f"a{ch}b")
        if code in (0x09, 0x0A):
            assert out == f"a{ch}b", f"U+{code:04X} must be preserved"
        else:
            assert out == "a�b", f"U+{code:04X} reached the terminal"


def test_plain_replaces_del_and_every_c1_control():
    """DEL and the C1 block include the 8-bit CSI and OSC introducers."""
    for code in range(0x7F, 0xA0):
        ch = chr(code)
        assert darkside.plain(f"a{ch}b") == "a�b", f"U+{code:04X} reached the terminal"


def test_plain_leaves_ordinary_text_and_markup_untouched():
    """Markup is preserved LITERALLY: safety comes from never using a markup sink."""
    assert darkside.plain("acta-2013 · nómina") == "acta-2013 · nómina"
    assert darkside.plain("[bold red]PWN[/]") == "[bold red]PWN[/]"
    assert darkside.plain("") == ""


def test_plain_coerces_non_strings_without_raising():
    """A sidecar is YAML: a bare `path:` parses to None, `path: 12345` to an int."""
    assert darkside.plain(None) == ""
    assert darkside.plain(12345) == "12345"
    assert darkside.plain(["a"]) == "['a']"


def test_plain_is_what_fit_and_hint_line_use():
    """The helper is the single owner; the two text helpers must route through it."""
    assert "�" in darkside.fit("a\x00b", 8)
    assert "\x00" not in darkside.hint_line("a\x00b").plain
