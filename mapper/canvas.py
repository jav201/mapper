"""Cell canvas with box-drawing wire merging and braille free-angle edges."""
from __future__ import annotations

import re
from typing import Sequence

from rich.text import Text

_U, _D, _L, _R = 1, 2, 4, 8
_GLYPH = {
    0: " ",
    _U: "│",
    _D: "│",
    _L: "─",
    _R: "─",
    _U | _D: "│",
    _L | _R: "─",
    _U | _L: "┘",
    _U | _R: "└",
    _D | _L: "┐",
    _D | _R: "┌",
    _U | _D | _L: "┤",
    _U | _D | _R: "├",
    _U | _L | _R: "┴",
    _D | _L | _R: "┬",
    _U | _D | _L | _R: "┼",
}

# Braille sub-cell geometry.  A `dots` key is in sub-cell space: a cell holds
# 2 columns x 4 rows of dots, so (sx, sy) paints cell (sx // 2, sy // 4).
_BRAILLE_BASE = 0x2800
_DOT_BITS = ((0x01, 0x08), (0x02, 0x10), (0x04, 0x20), (0x40, 0x80))

# A style that may safely be EXTENDED with " on <bg>" by string concatenation:
# an ALLOWLIST of colour-and-attribute words, deliberately not a test for an
# existing background.
#
# A theme NAME may not be extended.  `Console.get_style` resolves a theme key
# only for a BARE name; a compound string goes to `Style.parse`, which has no
# theme and reads the name as a style attribute instead, losing whatever colour
# the theme would have given it.
#
# MEASURED ON A PLAIN CONSOLE -- which is what `export.save_svg` uses -- rather
# than on one built for the probe: this repo registers NO theme, `frame` is not
# in rich 15.0.0's DEFAULT_STYLES, and it resolves to the ECMA-48 `frame`
# ATTRIBUTE carrying no colour at all.  So composing it loses nothing TODAY and
# this guard is forward-looking, not a repair; it costs the background on a
# named style, which is the conservative direction.  It is kept because
# `views/layered.py` already computes "frame" as an edge tone and Inc-2 routes
# all four renderers through here -- the day a theme is registered, composing
# would silently drop the tone, which is the fail-open `_tone` exists to close.
#
# An earlier version of this comment asserted that `frame` resolved to a colour
# and called it measured.  The probe had constructed the theme it then observed.
# It does not resolve to a colour.
#
# An allowlist also subsumes the "does it already declare a background" case
# without a second check: `on` is not a member, so any style containing it in
# any case fails to match and keeps what it already had.  A separate
# case-insensitive background test was written first and measured INERT --
# it could not change an outcome, so it is not here.
_COMPOSABLE = re.compile(
    r"(?i)^(?:#[0-9a-f]{6}|bold|dim|italic|underline|reverse|blink|strike|\s)*$"
)


class Canvas:
    """A cell canvas of Rich Text fragments.

    Four layers compose into `rows()`, in this declared precedence: an explicit
    cell outranks a wire, a wire outranks a braille dot, and a `bgs` background
    is applied to whichever glyph won -- UNLESS that glyph's style declares its
    own background, or is a style the background cannot be composed onto, in
    which case the glyph keeps its style and the layer background is DROPPED.
    The drop is deliberate and silent; see `_COMPOSABLE` for which styles are
    which, and why losing the background is the safe direction.

    `tones` is the set of tone values a `dots` or `bgs` write may carry, and
    `fallback` is what a value outside it paints instead.  They are passed in
    rather than imported because `canvas` is the lowest-level drawing primitive
    and depends on nothing (docs/ARCHITECTURE.md section 3); the guard still
    lives in `rows()`, which is the one place all four layers converge.  Left
    unset, no tone policy applies and every layer value passes through.
    """

    def __init__(self, w: int, h: int, tones: Sequence[str] = (),
                 fallback: str = ""):
        if tones and not fallback:
            raise ValueError(
                "a tone policy requires a fallback: an empty fallback rejects the "
                "bad tone and then paints unstyled, which is the same fail-open "
                "the policy exists to close"
            )
        self.w, self.h = w, h
        self.cells: dict[tuple[int, int], tuple[str, str]] = {}
        self.bits: dict[tuple[int, int], int] = {}
        self.dots: dict[tuple[int, int], str] = {}
        self.bgs: dict[tuple[int, int], str] = {}
        self._wire_tones: dict[tuple[int, int], str] = {}
        self._tones = frozenset(tones)
        self._fallback = fallback

    def put(self, x: int, y: int, ch: str, style: str = "") -> None:
        if 0 <= x < self.w and 0 <= y < self.h and ch:
            self.cells[(x, y)] = (ch, style)

    def wire(self, x: int, y: int, mask: int, tone: str = "frame") -> None:
        if not (0 <= x < self.w and 0 <= y < self.h):
            return
        self.bits[(x, y)] = self.bits.get((x, y), 0) | mask
        self._wire_tones.setdefault((x, y), tone)

    def edge(self, x0: int, y0: int, x1: int, y1: int, tone: str = "frame") -> None:
        """Vertical drop from (x0,y0) to (x1,y1); x0 must equal x1."""
        assert x0 == x1
        for y in range(min(y0, y1), max(y0, y1) + 1):
            self.wire(x0, y, _U | _D, tone)

    def elbow_down(self, x0: int, y0: int, x1: int, ybus: int, tone: str = "frame") -> None:
        """Parent exits down, across the bus row, child drops off the bus."""
        self.wire(x0, y0, _D, tone)
        for y in range(y0 + 1, ybus):
            self.wire(x0, y, _U | _D, tone)
        self.wire(x0, ybus, _U | (_R if x1 > x0 else _L), tone)
        xa, xb = min(x0, x1), max(x0, x1)
        for x in range(xa + 1, xb):
            self.wire(x, ybus, _L | _R, tone)
        self.wire(x1, ybus, _D | (_L if x1 > x0 else _R), tone)

    def text(self, x: int, y: int, s: str, style: str = "") -> None:
        for j, ch in enumerate(s):
            self.put(x + j, y, ch, style)

    def _tone(self, tone: str) -> str:
        """A layer value outside the declared set paints the fallback.

        The sink fails open otherwise: Rich swallows a malformed style via
        `get_style(..., default="")`, so a bad tone silently paints unstyled,
        which is indistinguishable from a tone that was never applied.
        """
        if not self._tones or tone in self._tones:
            return tone
        return self._fallback

    def _braille(self) -> tuple[dict[tuple[int, int], int], dict[tuple[int, int], str]]:
        """Fold the sub-cell dots layer into one mask and one tone per cell.

        A dot whose cell falls outside the canvas is dropped here, which is why
        `rows()` never has to guard it: the writers in `views` address dot space
        by coordinate arithmetic and do not bounds-check.

        Where two dots of different tones share one cell, THE FIRST WRITTEN TONE
        WINS.  Declared rather than left implicit: this function's whole subject
        is a composition order, and an undeclared tie-break inside it is the one
        rule a reader cannot recover from the code's intent.
        """
        masks: dict[tuple[int, int], int] = {}
        tones: dict[tuple[int, int], str] = {}
        for (sx, sy), tone in self.dots.items():
            x, y = sx // 2, sy // 4
            if not (0 <= x < self.w and 0 <= y < self.h):
                continue
            masks[(x, y)] = masks.get((x, y), 0) | _DOT_BITS[sy % 4][sx % 2]
            tones.setdefault((x, y), tone)
        return masks, tones

    def rows(self) -> list[Text]:
        dot_masks, dot_tones = self._braille()
        out: list[Text] = []
        for y in range(self.h):
            line = Text()
            for x in range(self.w):
                key = (x, y)
                style: str | None
                if key in self.cells:
                    ch, style = self.cells[key]
                elif key in self.bits:
                    ch = _GLYPH[self.bits[key]]
                    style = self._wire_tones.get(key, "frame")
                elif key in dot_masks:
                    ch = chr(_BRAILLE_BASE + dot_masks[key])
                    style = self._tone(dot_tones[key])
                else:
                    ch, style = " ", None
                if key in self.bgs:
                    bg = self._tone(self.bgs[key])
                    if style is None:
                        style = f"on {bg}"
                    elif _COMPOSABLE.fullmatch(style):
                        style = f"{style} on {bg}".strip()
                    # else: a theme NAME, or a style that already declares its
                    # own background. Keep it and drop the layer background —
                    # composing onto a name resolves it as a style attribute and
                    # loses the colour entirely.
                line.append(ch, style)
            out.append(line)
        return out
