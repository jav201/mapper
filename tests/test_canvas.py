"""Canvas layer composition — HLR-CNV.1, LLR-CNV.1.1 through LLR-CNV.1.4.

Pre-state, executed at 5d8ee0d before any of this landed: `Canvas.__init__`
declared neither `dots` nor `bgs`, `rows()` read only `cells` and `bits`, and
`RadialRenderer` monkey-patched both layers onto the instance — so every
braille glyph and every pill background was discarded silently.  A 6-node graph
through `RadialRenderer` at 80x24 painted **0** characters in U+2800..U+28FF.
"""
import re
import subprocess
from pathlib import Path

import pytest

from mapper import darkside
from mapper.canvas import _GLYPH, Canvas

REPO = Path(__file__).resolve().parents[1]
BRAILLE = range(0x2800, 0x2900)

# `wire` masks, spelled once: up|down is a vertical bar, left|right a dash.
_UD, _LR = 1 | 2, 4 | 8

TONES = darkside.tone_set()
FALLBACK = darkside.MUT


def _canvas(w, h):
    """A canvas carrying the real declared token set and fallback."""
    return Canvas(w, h, tones=TONES, fallback=FALLBACK)


def _braille_count(rows) -> int:
    return sum(1 for row in rows for c in row.plain if ord(c) in BRAILLE)


def _style_at(row, x) -> str:
    """The style string covering column *x* of a rendered row."""
    return " ".join(str(s.style) for s in row.spans if s.start <= x < s.end)


# --------------------------------------------------------------------------
# LLR-CNV.1.1 — the layers are declared, not monkey-patched


def test_tc_cnv_1_1_layers_are_declared_on_a_bare_canvas():
    cv = Canvas(10, 10)
    assert cv.dots == {}
    assert cv.bgs == {}


_INSTANCE_ASSIGN = re.compile(r"\b\w+\.(?:dots|bgs)\s*=\s*(?!=)")


def _tracked_view_sources() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "mapper/views/*.py"],
        cwd=REPO, capture_output=True, text=True, check=True,
    )
    files = [REPO / p for p in out.stdout.split()]
    assert files, "the derived input set is empty: this census would pass vacuously"
    return files


def test_tc_cnv_1_1_no_renderer_assigns_a_layer_onto_the_canvas_instance():
    """The deletion is asserted, not assumed.

    A monkey-patch left in place beside a declared attribute is how the two
    definitions come back.  Pre-state: 2 assignments, both in `views/radial.py`.

    The positive control runs FIRST and is not decoration: an absence is only
    admissible if the probe that produced it can produce a non-absence (C-55).
    """
    assert _INSTANCE_ASSIGN.search("cv.dots = {}")
    assert _INSTANCE_ASSIGN.search("canvas.bgs = {}")
    assert not _INSTANCE_ASSIGN.search("if cv.dots == {}:")

    offenders = [
        f"{path.relative_to(REPO).as_posix()}:{n}"
        for path in _tracked_view_sources()
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if _INSTANCE_ASSIGN.search(line)
    ]
    assert offenders == []


# --------------------------------------------------------------------------
# LLR-CNV.1.2 — rows() composes the layers in a declared order


def test_tc_cnv_1_2_precedence_is_cell_over_wire_over_dot():
    """Three precedence pairs, three resolutions, all at one coordinate."""
    cell, wire, dot = "X", _GLYPH[_UD], chr(0x2800 | 0x01)

    cv = _canvas(1, 1)          # cell vs wire
    cv.put(0, 0, cell, darkside.INK)
    cv.wire(0, 0, _UD, darkside.INK)
    assert cv.rows()[0].plain == cell

    cv = _canvas(1, 1)          # cell vs dot
    cv.put(0, 0, cell, darkside.INK)
    cv.dots[(0, 0)] = darkside.INK
    assert cv.rows()[0].plain == cell

    cv = _canvas(1, 1)          # wire vs dot
    cv.wire(0, 0, _UD, darkside.INK)
    cv.dots[(0, 0)] = darkside.INK
    assert cv.rows()[0].plain == wire

    cv = _canvas(1, 1)          # and the dot paints when it is alone
    cv.dots[(0, 0)] = darkside.INK
    assert cv.rows()[0].plain == dot


def test_tc_cnv_1_2_a_background_reaches_a_composable_winner():
    """Every arm here drives a COMPOSABLE style (a bare hex, or none at all).

    The name is narrow on purpose: a winner whose style already declares a
    background, or which cannot be composed onto, keeps its style and DROPS the
    layer background -- see the two arms below this one.  "reaches whichever
    glyph won" was the original name and it claimed the universal this test does
    not establish.
    """
    for write, expected in (
        (lambda cv: cv.put(0, 0, "X", darkside.INK), "X"),
        (lambda cv: cv.wire(0, 0, _LR, darkside.INK), _GLYPH[_LR]),
        (lambda cv: cv.dots.__setitem__((0, 0), darkside.INK), chr(0x2801)),
        (lambda cv: None, " "),
    ):
        cv = _canvas(1, 1)
        write(cv)
        cv.bgs[(0, 0)] = darkside.PANEL
        row = cv.rows()[0]
        assert row.plain == expected
        assert f"on {darkside.PANEL}" in _style_at(row, 0)


def test_tc_cnv_1_2_a_cell_that_declares_its_own_background_keeps_it():
    cv = _canvas(1, 1)
    cv.put(0, 0, "X", f"bold {darkside.GROUND} on {darkside.ACCENT}")
    cv.bgs[(0, 0)] = darkside.PANEL
    style = _style_at(cv.rows()[0], 0)
    assert f"on {darkside.ACCENT}" in style
    assert darkside.PANEL not in style


def test_tc_cnv_1_2_a_wire_keeps_its_tone_when_a_background_lands_on_it():
    """The default wire tone is a NAME, and a name cannot be string-composed.

    `Console.get_style` resolves a theme key only for a BARE name; a compound
    string goes to `Style.parse`, which has no theme and reads the name as a
    style attribute instead.

    MEASURED ON A PLAIN CONSOLE, not one built for the probe: this repo
    registers no theme and `frame` is not in rich 15.0.0's DEFAULT_STYLES, so it
    resolves to the ECMA-48 `frame` ATTRIBUTE and carries no colour today.
    Composing it therefore loses nothing yet -- this asserts the forward-looking
    guard, not a live repair.  It is worth pinning because `"frame"` is the
    DEFAULT of `wire`, `edge` and `elbow_down`, so it is the value the module
    hands itself, and `views/layered.py` already computes it as an edge tone.
    """
    cv = _canvas(1, 1)
    cv.wire(0, 0, _LR)                          # no tone -> the "frame" default
    cv.bgs[(0, 0)] = darkside.PANEL
    style = _style_at(cv.rows()[0], 0)
    assert "frame" in style
    assert darkside.PANEL not in style


def test_tc_cnv_1_2_an_uppercase_on_is_still_a_background():
    """`Style.parse` lowercases each word, so `ON <colour>` IS a background.

    An `"on" not in style.split()` test misses it and appends a second one;
    last-wins, which inverts the declared precedence.
    """
    cv = _canvas(1, 1)
    cv.put(0, 0, "X", f"ON {darkside.ACCENT}")
    cv.bgs[(0, 0)] = darkside.PANEL
    assert darkside.PANEL not in _style_at(cv.rows()[0], 0)


def test_tc_cnv_1_4_a_tone_policy_without_a_fallback_is_refused():
    """An empty fallback rejects the bad tone and then paints it UNSTYLED, which
    is the same fail-open the policy exists to close.  Prevention with no
    detection is not a control, so the constructor refuses the combination."""
    with pytest.raises(ValueError, match="fallback"):
        Canvas(2, 2, tones=TONES)


_LAYER_WRITE = re.compile(r"\b\w+\.(?:dots|bgs)\s*\[")


def test_tc_cnv_1_4_every_view_that_writes_a_layer_declares_a_tone_policy():
    """The policy is INJECTED, so it is optional; this makes it mandatory where
    it matters.

    The monkey-patch census above bans whole-attribute assignment; it does NOT
    ban the SUBSCRIPT write, which is the form the real writers use and the form
    a new renderer would copy.  Without this, the first view to write
    `cv.dots[...]` on an unpoliced canvas silently gets the pre-Inc-1 fail-open
    behaviour with a fully green suite.

    TWO DECLARED LIMITS, because the predicate is weaker than the sentence
    above and a reader should not have to discover that:

    1. It is FILE-granular, not construction-granular.  One policed `Canvas(...)`
       anywhere in a file licenses every unpoliced construction in it, so a
       SECOND canvas inside `radial.py` would pass.  Binding each layer write to
       its receiver's construction is the real fix; carried as `B-48`, and
       `radial.py` is the file `Inc-2` touches.
    2. Its scope is `mapper/views/`.  Executed: there is no `Canvas(`
       construction outside that directory today, so the sweep is complete --
       but a canvas in `screens/` or `widgets/` would be unswept.
    """
    assert _LAYER_WRITE.search("cv.dots[(0, 0)] = h")          # positive control
    assert not _LAYER_WRITE.search("if cv.dots:")              # near-miss control

    offenders = []
    for path in _tracked_view_sources():
        blob = path.read_text(encoding="utf-8")
        if _LAYER_WRITE.search(blob) and "tones=" not in blob:
            offenders.append(path.relative_to(REPO).as_posix())
    assert offenders == []


def test_tc_cnv_1_2_empty_layers_leave_the_painted_spans_byte_identical():
    """The widening must not move a renderer that writes no layers.

    Eight of the twelve `MASTER_LEGACY_DIGESTS` keys rest on this: every
    `LayeredRenderer` and `OutlineRenderer` key is predicted GREEN, and
    re-capturing a predicted-green digest is a gate failure.

    Measured while writing this, because the first version of the composition
    guarded against the wrong thing: `Text.append` tests `if style:`, so a
    no-style append, an empty-string style and `None` all record NO span and
    are indistinguishable.  The defensive branch that existed here was dead
    weight, and its explanatory comment was false.
    """
    cv = Canvas(4, 2)
    cv.put(0, 0, "A", darkside.INK)
    cv.wire(1, 0, _LR, darkside.INK)
    rows = cv.rows()
    assert [r.plain for r in rows] == ["A" + _GLYPH[_LR] + "  ", "    "]
    assert list(rows[1].spans) == []


# --------------------------------------------------------------------------
# LLR-CNV.1.3 — out-of-bounds layer writes are dropped, not raised


def test_tc_cnv_1_3_out_of_bounds_layer_writes_are_dropped_not_raised():
    """`put` guards its own bounds; the layer writers in `views` do not.

    `radial.py` addresses dot space by coordinate arithmetic with no guard, so
    the guard has to live in `rows()`.
    """
    cv = _canvas(4, 3)
    cv.bgs[(3, 2)] = darkside.PANEL       # the last addressable cell
    cv.bgs[(4, 2)] = darkside.PANEL       # one column past it
    cv.bgs[(0, 3)] = darkside.PANEL       # one row past it
    cv.bgs[(-1, 0)] = darkside.PANEL
    cv.dots[(8, 0)] = darkside.INK        # sub-cell x=8 -> cell x=4, past the edge
    cv.dots[(0, 12)] = darkside.INK       # sub-cell y=12 -> cell y=3, past the edge
    cv.dots[(-2, -4)] = darkside.INK

    rows = cv.rows()
    assert len(rows) == 3
    assert all(len(row.plain) == 4 for row in rows)
    assert _braille_count(rows) == 0
    assert f"on {darkside.PANEL}" in _style_at(rows[2], 3)

    # The guard needs its OWN observable, or it is inert: `rows()` only ever
    # LOOKS UP in-range cells, so an out-of-range entry left in the folded mask
    # would never be painted anyway and no assertion over the painted output
    # can tell the two implementations apart.  Measured -- deleting the bounds
    # check reddened nothing until this line existed.
    masks, _ = cv._braille()
    assert masks == {}, f"out-of-bounds dots survived the fold: {sorted(masks)}"
    in_range = _canvas(4, 3)
    in_range.dots[(2, 4)] = darkside.INK       # sub-cell (2,4) -> cell (1,1)
    kept, _ = in_range._braille()
    assert set(kept) == {(1, 1)}, "the positive control failed: the fold drops valid dots too"


# --------------------------------------------------------------------------
# LLR-CNV.1.4 — the layer tone is a declared token, with a fallback

# Constructed at run time, never spelled: this file contains no control byte.
MALFORMED_TONES = [
    "#zzzzzz",
    "not-a-colour",
    "on nosuchcolour",
    "color(999)",
    "rgb(300,300,300)",
    "link https://evil.example/x",
    chr(27) + "[2J",
    chr(27) + "]52;c;ZXZpbA==" + chr(7),
    "x" * 1600,
    "#12345",
    "#1783ff and then some",
    "bold underline #nothex",
    "",
    "on",
]


def test_tc_cnv_1_4_the_malformed_tone_set_is_the_size_the_threshold_names():
    assert len(MALFORMED_TONES) == 14
    assert not (set(MALFORMED_TONES) & TONES)


@pytest.mark.parametrize("tone", MALFORMED_TONES)
def test_tc_cnv_1_4_a_tone_outside_the_declared_set_paints_the_fallback(tone):
    """The style sink fails OPEN, which is why this guard exists.

    Rich swallows a malformed style through `get_style(..., default="")`, so a
    bad tone does not crash a render — it silently paints unstyled, which is
    indistinguishable from a tone that was never applied.  All 14 of these
    render fine today; none raises.  The guard is what makes them observable.

    The comparison is an EQUALITY, not a substring absence: two of these tones
    are `""` and `"on"`, both of which are substrings of the fallback's own
    rendered form `on #737373`, so a `tone not in style` oracle reports a
    correct implementation as broken.  A substring search cannot tell a value
    from its own encoding.
    """
    for layer, expected in (("dots", FALLBACK), ("bgs", f"on {FALLBACK}")):
        cv = _canvas(1, 1)
        getattr(cv, layer)[(0, 0)] = tone
        assert _style_at(cv.rows()[0], 0) == expected


def test_tc_cnv_1_4_a_tone_inside_the_declared_set_is_kept():
    for tone in (darkside.INK, darkside.ACCENT, darkside.PANEL):
        cv = _canvas(1, 1)
        cv.dots[(0, 0)] = tone
        assert tone in _style_at(cv.rows()[0], 0)


def test_tc_cnv_1_4_the_declared_token_set_is_derived_and_non_empty():
    """The set comes from the design module's own globals, never a literal list.

    A hand-listed set is an unproven claim (C-31): it cannot contain the token
    nobody typed, and this guard is only as strong as the set it quantifies over.
    """
    assert TONES, "the derived token set is empty: every guard over it is vacuous"
    assert darkside.tokens()["INK"] == darkside.INK
    assert set(darkside.tokens()) >= {
        "GROUND", "PANEL", "STEP", "INK", "MUT", "ACCENT",
        "WARN", "ALERT", "WORDMARK", "SAGE", "TEAL", "VIOLET",
    }
    assert all(re.fullmatch(r"#[0-9a-fA-F]{6}", v) for v in TONES)


def test_tc_cnv_1_4_an_unset_tone_policy_passes_every_value_through():
    """A canvas built without a policy keeps today's behaviour exactly."""
    cv = Canvas(1, 1)
    cv.dots[(0, 0)] = "not-a-colour"
    assert "not-a-colour" in _style_at(cv.rows()[0], 0)


# --------------------------------------------------------------------------
# AT-007 — the declared layers reach the rendered output


def test_at_007_a_layer_write_reaches_the_painted_output():
    """Pre-state on this exact input was 0 braille characters and no background.

    The threshold is a COUNT, not "braille appears": a count has a measured
    pre-state of exactly 0 and a mutation that can move it; an adjective has
    neither.
    """
    cv = _canvas(4, 2)
    for sx in range(8):
        cv.dots[(sx, 0)] = darkside.INK
    cv.bgs[(0, 1)] = darkside.PANEL

    rows = cv.rows()
    assert _braille_count(rows) > 0
    assert f"on {darkside.PANEL}" in _style_at(rows[1], 0)


# AT-008 — boundary, and the invalid coordinate, through the same surface


def test_at_008_a_background_at_the_last_cell_paints_and_one_past_it_does_not():
    cv = _canvas(3, 1)
    cv.bgs[(2, 0)] = darkside.PANEL
    cv.bgs[(3, 0)] = darkside.ALERT
    row = cv.rows()[0]
    assert len(row.plain) == 3
    assert f"on {darkside.PANEL}" in _style_at(row, 2)
    assert darkside.ALERT not in " ".join(str(s.style) for s in row.spans)


def test_at_008_an_invalid_dot_coordinate_paints_nothing_and_raises_nothing():
    cv = _canvas(2, 1)
    cv.dots[(400, 400)] = darkside.INK
    cv.dots[(-1, -1)] = darkside.INK
    rows = cv.rows()
    assert _braille_count(rows) == 0
    assert rows[0].plain == "  "
