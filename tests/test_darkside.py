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


def test_time_row_coerces_its_remote_derived_text():
    """`time_row`'s name and note are REMOTE-derived, not merely file-derived.

    The repo screen feeds it a git branch name and a commit subject/author, so
    the input author is anyone who has landed a commit in a repository the
    operator opens -- the widest input surface in the product.  A commit subject
    carrying an OSC-52 sequence is a clipboard write into the operator's
    terminal; a right-to-left override in a branch name reorders the row that
    reports it.

    Coercion lives INSIDE `time_row` rather than at its call site, so the next
    caller cannot forget it -- the same shape as `hint_line` and `fit`.
    """
    hostile_name = "rama" + chr(0x1B) + "]52;c;aGk=" + chr(0x07)
    hostile_note = "fix" + chr(0x202E) + "gpj.exe" + chr(0x00AD)
    row = darkside.time_row(hostile_name, 3, "●", darkside.INK, hostile_note)

    banned = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}
    leaked = sorted({ord(c) for c in row.plain if ord(c) in banned})
    assert leaked == [], f"uncoerced code points painted: {[f'U+{c:04X}' for c in leaked]}"

    # Positive control: the same oracle over the UNCOERCED input reports 4, so
    # the empty result above is a measurement rather than an accident.
    raw = hostile_name + hostile_note
    assert len({ord(c) for c in raw if ord(c) in banned}) == 4


def test_plain_coerces_non_strings_without_raising():
    """A sidecar is YAML: a bare `path:` parses to None, `path: 12345` to an int."""
    assert darkside.plain(None) == ""
    assert darkside.plain(12345) == "12345"
    assert darkside.plain(["a"]) == "['a']"


def test_plain_is_what_fit_and_hint_line_use():
    """The helper is the single owner; the two text helpers must route through it."""
    assert "�" in darkside.fit("a\x00b", 8)
    assert "\x00" not in darkside.hint_line("a\x00b").plain
