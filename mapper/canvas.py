"""Cell canvas with box-drawing wire merging and braille free-angle edges."""
from __future__ import annotations

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


class Canvas:
    """A cell canvas of Rich Text fragments."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.cells: dict[tuple[int, int], tuple[str, str]] = {}
        self.bits: dict[tuple[int, int], int] = {}
        self._wire_tones: dict[tuple[int, int], str] = {}

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

    def rows(self) -> list[Text]:
        out: list[Text] = []
        for y in range(self.h):
            line = Text()
            for x in range(self.w):
                if (x, y) in self.cells:
                    ch, style = self.cells[(x, y)]
                    line.append(ch, style)
                elif (x, y) in self.bits:
                    mask = self.bits[(x, y)]
                    tone = self._wire_tones.get((x, y), "frame")
                    line.append(_GLYPH[mask], tone)
                else:
                    line.append(" ")
            out.append(line)
        return out
