"""Darkside design-system primitives (rich only, no Textual dependency).

Every colour token carries EXACTLY ONE job.  A hue with two jobs cannot be
adjudicated by the census in `tests/test_darkside.py`, and it licenses painting
two different things identically -- which is the whole failure the census
exists to catch.  The jobs, one sentence each:

  GROUND    the page behind everything.
  PANEL     a raised surface sitting on GROUND.
  STEP      a divider or an inert track on a surface.
  INK       readable body text.
  ASH       segundo escalon legible: the middle rung of the text ramp on the
            black ground, one step below INK, where STEP and WORDMARK are too
            dark to be read as text at all.
  MUT       secondary or dimmed text, and absent information.
  WORDMARK  the quietest mark on the page; present but not to be read.
  ACCENT    interactivity ONLY -- "donde puedes actuar".  Never a label.
  WARN      outstanding attention: work is pending, due, or at risk, and
            nothing has failed.
  ALERT     failure or blockage: this item cannot proceed as it stands.
  PULSE     trabajo en curso: this item is being worked on right now, and
            nothing is pending, overdue, at risk, or failed.
  SAGE      completitud / vigente.
  TEAL      procedencia repo.
  VIOLET    relaciones / enlaces.

WARN's job deliberately does NOT read "or in flight".  Work the machine is
doing and work the operator owes demand opposite things -- patience versus
action -- so one token spanning both has a job that cannot be scanned, and a
census over it cannot tell the two apart.  PULSE owns "in progress"; WARN owns
the obligation.  Narrowing WARN is what keeps `sites classifying as both == 0`
satisfiable at all.
"""
from __future__ import annotations

import re
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
ASH = "#a3a3a3"
MUT = "#737373"
ACCENT = "#1783ff"
WARN = "#ffd230"
ALERT = "#ff4f42"
PULSE = "#ff9ecb"
WORDMARK = "#3a3a3a"

# Paleta v2 -- three hues with declared jobs, so a later batch cannot quietly
# reuse one for a second meaning.  Blue stays interactivity-only and severity
# stays WARN/ALERT; these three carry meanings neither of those families owns.
SAGE = "#2fbf71"
TEAL = "#22b8cf"
VIOLET = "#9775fa"

_TOKEN_VALUE = re.compile(r"^#[0-9a-fA-F]{6}$")

# The tokens that are a SURFACE to paint on rather than a mark to paint with.
# Declared, because "semantic token pairs" has to be decidable before the
# contrast floor can quantify over it -- and the two classes separate by a wide
# measured margin: surfaces top out at WORDMARK, semantics start at MUT, with a
# 4x luminance gap and nothing in between.  The PAIRS stay derived; only the
# four-name class boundary is written down.
SURFACES = frozenset({GROUND, PANEL, STEP, WORDMARK})


def tokens() -> dict[str, str]:
    """Every declared colour token, name -> value, DERIVED from this module.

    Derived rather than listed because a hand-written set is an unproven claim:
    a token added above would be invisible to the hue census, to `Canvas`'s
    tone guard and to the contrast floor, each of which reads this one function.
    """
    return {
        name: value
        for name, value in globals().items()
        if not name.startswith("_")
        and name.isupper()
        and isinstance(value, str)
        and _TOKEN_VALUE.match(value)
    }


def tone_set() -> frozenset[str]:
    """The declared token values, for consumers that validate a tone."""
    return frozenset(tokens().values())


def semantic_tokens() -> dict[str, str]:
    """The tokens that carry a meaning, as opposed to the surfaces beneath them.

    The contrast floor quantifies over these pairs; including the surfaces
    drops it to the GROUND/PANEL distance, which measures the page and not the
    palette.
    """
    return {n: v for n, v in tokens().items() if v not in SURFACES}

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
    # `name` and `note` are file- OR REMOTE-derived: the repo screen feeds this
    # a git branch name and a commit subject/author, so the input author is
    # anyone who has landed a commit in a repository the operator opens.  Coerce
    # here rather than at the call site, so the next caller cannot forget --
    # `hint_line` and `fit` already work this way.
    name, note = plain(name), plain(note)
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
#
# THE single list of code points that may not reach a painted surface.  Declared
# once, here: `_CONTROL_MAP` is derived from it and every threshold and every
# test reads it rather than restating it, because two copies of a list like this
# agree on the day they are written and drift the first time one is edited.
#
# PRESERVED, each with its reason: TAB and LF are the only two code points in
# the classes below that the layout depends on.
PRESERVED_CODE_POINTS = frozenset({0x0009, 0x000A})

# The list is exactly Unicode's Cc (control), Cf (format), Zl (line separator)
# and Zp (paragraph separator) classes, MINUS PRESERVED_CODE_POINTS.  It is
# spelled out as literal ranges so a reviewer can read it, and
# `tests/test_darkside_census.py` re-derives it from `unicodedata` and asserts
# equality.  That derivation is the point: an oracle built FROM this list can
# never detect that the list is short, and twice it was.
#
# Hand-picking produced both near-misses.  A row labelled "C0 except TAB and LF"
# also omitted U+000D; a row labelled "zero-width and invisible" stopped one
# code point short of U+2061..U+2064.  The U+E0020..U+E007F TAG block is why it
# matters most: those points render as nothing everywhere, map 1:1 onto ASCII,
# and reach an exported SVG as a payload the operator cannot see and any later
# reader recovers trivially.
#
# Ranges are inclusive on both ends.  Every entry is written as a number, never
# as the character itself, so this file contains no control byte.
COERCION_RANGES: tuple[tuple[int, int], ...] = (
    (0x0000, 0x0008), (0x000B, 0x001F),       # C0 except TAB and LF
    (0x007F, 0x009F),                         # DEL and C1
    (0x00AD, 0x00AD),                         # soft hyphen
    (0x0600, 0x0605), (0x06DD, 0x06DD),       # Arabic number/sign format controls
    (0x061C, 0x061C),                         # Arabic letter mark
    (0x070F, 0x070F),                         # Syriac abbreviation mark
    (0x0890, 0x0891), (0x08E2, 0x08E2),       # Arabic number signs
    (0x180E, 0x180E),                         # Mongolian vowel separator
    (0x200B, 0x200F),                         # zero-width, and the bidi marks
    (0x2028, 0x202E),                         # line/para seps, bidi embed/override
    (0x2060, 0x2064),                         # word joiner, invisible operators
    (0x2066, 0x206F),                         # bidi isolates, deprecated controls
    (0xFEFF, 0xFEFF),                         # byte-order mark
    (0xFFF9, 0xFFFB),                         # interlinear annotation
    (0x110BD, 0x110BD), (0x110CD, 0x110CD),   # Kaithi number signs
    (0x13430, 0x1343F),                       # Egyptian hieroglyph format controls
    (0x1BCA0, 0x1BCA3),                       # shorthand format controls
    (0x1D173, 0x1D17A),                       # musical symbol beams and slurs
    (0xE0001, 0xE0001), (0xE0020, 0xE007F),   # language tag, and the TAG block
)

_CONTROL_MAP = {
    cp: "�"
    for lo, hi in COERCION_RANGES
    for cp in range(lo, hi + 1)
}


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
