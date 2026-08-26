"""Darkside design-system primitives (rich only, no Textual dependency)."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

# Palette ------------------------------------------------------------------
GROUND = "#000000"
PANEL = "#121212"
STEP = "#262626"
INK = "#f5f5f5"
MUT = "#737373"
ACCENT = "#1783ff"
WARN = "#ffd230"
ALERT = "#ff4f42"
WORDMARK = "#3a3a3a"

# Moon doodle --------------------------------------------------------------
_SYNODIC = 29.530588853
_NEW_MOON_2000 = date(2000, 1, 6)


def moon(d: date) -> tuple[str, str]:
    """Return (glyph, phase_name) for the given date."""
    days = (d - _NEW_MOON_2000).days
    age = days % _SYNODIC
    phase = age / _SYNODIC  # 0..1, 0=new, 0.5=full

    if phase < 0.0625 or phase >= 0.9375:
        return ("○", "new")
    if phase < 0.1875:
        return ("◔", "waxing crescent")
    if phase < 0.3125:
        return ("◑", "first quarter")
    if phase < 0.4375:
        return ("◕", "waxing gibbous")
    if phase < 0.5625:
        return ("●", "full")
    if phase < 0.6875:
        return ("◕", "waning gibbous")
    if phase < 0.8125:
        return ("◑", "last quarter")
    return ("◔", "waning crescent")


# Tab strip ----------------------------------------------------------------
def tab_strip(active: str, crumb: list[str] | None = None, width: int = 0) -> Text:
    """Render the darkside tab strip."""
    tabs: list[tuple[str, str]] = [
        ("c", "consultar"),
        ("p", "repo"),
        ("n", "construir"),
        ("f", "fábrica"),
    ]
    pieces: list[tuple[str, str]] = []
    for key, label in tabs:
        if key == active:
            pieces.append((f" {key} {label} ", f"bold {GROUND} on {ACCENT}"))
        else:
            pieces.append((f" {key} {label} ", f"{MUT} on {STEP}"))
        pieces.append(("  ", ""))
    # Drop trailing two spaces.
    if pieces:
        pieces.pop()

    # Right-side moon + wordmark.
    glyph, _ = moon(date.today())
    wordmark = f" {glyph} mapper"
    # Use the available width to push the wordmark to the right.
    left_text = Text.assemble(*pieces)
    target_width = max(width, left_text.cell_len + len(wordmark) + 2)
    spacer_width = max(1, target_width - left_text.cell_len - len(wordmark))
    pieces.append((" " * spacer_width, ""))
    pieces.append((wordmark, f"{WORDMARK}"))

    line = Text.assemble(*pieces)

    if crumb:
        rendered: list[tuple[str, str]] = []
        for i, part in enumerate(crumb):
            if i > 0:
                rendered.append((" / ", MUT))
            style = INK if i == len(crumb) - 1 else MUT
            rendered.append((escape(part), style))
        return Text.assemble(line, "\n", Text.assemble(*rendered))

    return line


# Group box ----------------------------------------------------------------
def group_box(renderable, pad_x: int = 1) -> Panel:
    """Invisible-bordered panel at panel depth."""
    return Panel(
        renderable,
        border_style=PANEL,
        style=f"on {PANEL}",
        padding=(0, pad_x),
    )


# Keybar -------------------------------------------------------------------
def keybar(
    groups: Sequence[tuple[str, Sequence[tuple[str, str]]]],
    width: int = 118,
    help_key: str = "?",
) -> Text:
    """Render grouped key hints for the footer, truncating VISIBLY.

    group names in STEP, key glyphs in ACCENT, labels in MUT.

    When the bar does not fit, a bare `…` is a lie by omission: it says something
    was cut but not that anything is missing, let alone how much or how to see it.
    This ends with `… +N  ? todas`, naming the count hidden and the key that shows
    them.  Measured before this change: the bar rendered 216 cells at a hard-coded
    118, so 9 of 17 bindings were shown and `m cobertura` — the entry point to the
    coverage flow — was simply invisible.
    """
    def _binding_parts(key: str, label: str, first: bool) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        if not first:
            out.append(("  ", ""))
        out.append((key, ACCENT))
        out.append((f" {label}", MUT))
        return out

    total = sum(len(bindings) for _, bindings in groups)
    parts: list[tuple[str, str]] = []
    for gi, (group_name, bindings) in enumerate(groups):
        if gi > 0:
            parts.append(("   ", ""))
        parts.append((f"{group_name} ", f"{STEP}"))
        for bi, (key, label) in enumerate(bindings):
            parts.extend(_binding_parts(key, label, bi == 0))

    text = Text.assemble(*parts)
    if text.cell_len <= width:
        return text

    # Re-assemble, counting how many bindings actually fit inside the budget the
    # marker leaves behind.
    marker_width = len(f" … +{total}  {help_key} todas")
    budget = max(0, width - marker_width)
    kept: list[tuple[str, str]] = []
    shown = 0
    running = Text()
    for gi, (group_name, bindings) in enumerate(groups):
        head: list[tuple[str, str]] = []
        if gi > 0:
            head.append(("   ", ""))
        head.append((f"{group_name} ", f"{STEP}"))
        for bi, (key, label) in enumerate(bindings):
            candidate = head + _binding_parts(key, label, bi == 0)
            probe = Text.assemble(*(kept + candidate))
            if probe.cell_len > budget:
                head = []
                break
            kept.extend(candidate)
            head = []
            shown += 1
            running = probe

    hidden = total - shown
    out = Text.assemble(*kept)
    out.append(f" … +{hidden}", style=WORDMARK)
    out.append(f"  {help_key}", style=ACCENT)
    out.append(" todas", style=MUT)
    return out


# Hint line ----------------------------------------------------------------
def hint_line(text: str, key: str | None = None) -> Text:
    """Render a next-step hint line."""
    parts: list[tuple[str, str]] = [("siguiente ▸ ", MUT), (plain(text), MUT)]
    if key:
        parts.append((f" {key}", INK))
    return Text.assemble(*parts)


# Step meter ---------------------------------------------------------------
def step_meter(filled: int, total: int, accent_current: bool = False) -> Text:
    """Render a step-meter as contiguous blocks."""
    if total <= 0:
        return Text("")
    parts: list[tuple[str, str]] = []
    for i in range(total):
        if i < filled:
            parts.append(("▰", INK))
        elif accent_current and i == filled:
            parts.append(("▱", INK))
        else:
            parts.append(("▱", STEP))
    return Text.assemble(*parts)


# Kind chip ----------------------------------------------------------------
def kind_chip(kind: str) -> Text:
    """Render a node-kind badge."""
    return Text.assemble((f" {escape(kind)} ", f"{INK} on {STEP}"))


# Drawn type (hero numbers) ------------------------------------------------
_DIGITS = {
    "0": ("███", "█ █", "█ █", "█ █", "███"),
    "1": (" █ ", "██ ", " █ ", " █ ", "███"),
    "2": ("███", "  █", "███", "█  ", "███"),
    "3": ("███", "  █", " ██", "  █", "███"),
    "4": ("█ █", "█ █", "███", "  █", "  █"),
    "5": ("███", "█  ", "███", "  █", "███"),
    "6": ("███", "█  ", "███", "█ █", "███"),
    "7": ("███", "  █", " █ ", " █ ", " █ "),
    "8": ("███", "█ █", "███", "█ █", "███"),
    "9": ("███", "█ █", "███", "  █", "███"),
}


def draw_number(s: str, style: str = INK) -> Text:
    """Render *s* as 3x5 block digits."""
    rows = [Text() for _ in range(5)]
    for ch in s:
        glyph = _DIGITS.get(ch)
        if glyph is None:
            continue
        for i, row in enumerate(glyph):
            rows[i].append(row + " ", style=style)
    return Text.assemble(*sum(([r, "\n"] for r in rows), [])[:-1])


def microbar(count: int, total: int, width: int = 10, fill: str = INK) -> Text:
    """Inline distribution bar: present never paints absent.

    Track uses WORDMARK because STEP is invisible on GROUND.
    """
    if total <= 0 or count <= 0:
        filled = 0
    else:
        filled = max(1, round(count / total * width))
    return Text.assemble(("█" * filled, fill), ("░" * (width - filled), WORDMARK))


def time_row(name: str, age_days: int, glyph: str, style: str, note: str,
             width: int = 48) -> Text:
    """One event on a shared *width*-day axis with a today rule.

    The today rule ``╎`` sits in the same rightmost column on every row.
    """
    cells = [" "] * (width + 1)
    cells[width] = "╎"
    col = max(0, width - 1 - round(age_days / 30 * (width - 2)))
    cells[col] = glyph
    parts: list[tuple[str, str]] = [(f"{name:<14}", MUT)]
    for c in cells:
        if c == "╎":
            parts.append((c, WORDMARK))
        elif c == glyph:
            parts.append((c, style))
        else:
            parts.append((c, ""))
    parts.append(("  ", ""))
    parts.append((note, MUT))
    return Text.assemble(*parts)


# Text helpers -------------------------------------------------------------
# Control characters other than tab and newline are replaced, not escaped: a
# terminal acts on them.  An ANSI cursor-move or an OSC-52 clipboard write inside
# a ficha title reaches the compositor verbatim, and markup escaping does nothing
# about either — measured, see 01-requirements.md §Amendment 2 S-B2.
_CONTROL_MAP = {c: "�" for c in range(0x00, 0x20) if c not in (0x09, 0x0A)}
_CONTROL_MAP.update({c: "�" for c in range(0x7F, 0xA0)})


def plain(value: object) -> str:
    """Coerce any file-derived value into a string that is safe to render.

    The single coercion helper every renderer of sidecar text must pass through.
    It deliberately does NOT call `rich.markup.escape`: these strings are placed
    into `Text` objects with explicit styles, and `Text` does not parse markup, so
    escaping there is a no-op that merely prints visible backslashes.  Safety from
    markup comes from never handing a file-derived `str` to a markup-parsing sink.
    """
    if not isinstance(value, str):
        value = "" if value is None else str(value)
    return value.translate(_CONTROL_MAP)


def fit(s: str, w: int) -> str:
    """Pad or truncate *s* to exactly *w* display cells."""
    s = plain(s)
    text = Text(s)
    if text.cell_len > w:
        text.truncate(w, overflow="ellipsis")
        return text.plain
    return text.plain + " " * (w - text.cell_len)
