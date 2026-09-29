"""The legend: the keys that work on the active screen, and the glyphs its view paints.

US-N16 «leyenda».  `?` explains THIS view -- its keys (`HLR-N16.1`), its glyph
vocabulary drawn in the view's own styles (`HLR-N16.2`), and the keys that work
inside the legend itself (`HLR-N16.4`).
"""
from __future__ import annotations

from itertools import groupby

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from mapper import darkside
from mapper.keymap import SCOPE_APP, SCOPE_HELP, bindings_for, textual_bindings

# The legend panel's two widths (Inc-8 verdicts `D4` and `E1`): a centred
# modal, and -- while the view keeps its minimum beside it (`F9`, `docks`) --
# a NARROW panel docked full height on the right -- the round-10 prototype's
# proportion (`prototypes/ui_next2/generate.py:leyenda`, a 43-column panel on
# a 118-column sheet), so the view keeps the canvas beside it.  The CSS below
# is built from both.
LEGEND_PANEL_CELLS = 80
LEGEND_DOCKED_CELLS = 44
_PAD_X = 2
_SCROLLBAR_CELLS = 1


def _row_cells(panel_cells: int) -> int:
    """`LLR-N16.2.3`'s row-length clause: every painted row of the scrolling
    body is exactly this many cells -- the panel less its left and right
    padding and the scrollbar.  A row wider than the pane would wrap, and the
    wrapped half would read as a row of its own.  `INC8-CR-F2`:
    `tests/test_legend_design.py` pins each budget against the real widget's
    `scrollable_content_region` in its own layout."""
    return panel_cells - 2 * _PAD_X - _SCROLLBAR_CELLS


LEGEND_ROW_CELLS = _row_cells(LEGEND_PANEL_CELLS)
LEGEND_DOCKED_ROW_CELLS = _row_cells(LEGEND_DOCKED_CELLS)
# The modal's height cap, which `TC-R36` (`LLR-R05`, a sealed prior batch)
# pins as governing on a tall terminal.  The docked panel is exempt and runs
# full height: amendment `A-107`, verdict `E1`.
LEGEND_MODAL_MAX_ROWS = 28
# Verdict `F9`: the legend docks while at least this many columns of the view
# stay visible left of the docked panel, and is a modal below that -- at any
# terminal width, since operators zoom (the width principle of round 3).
# WHY 43: the atlas's unit of meaning is a card and the wire that joins it to
# its sibling.  The widest card is 26 columns (`views/layered.py:335`), the
# gap to the next card 3 (`:329`), and the wire lands on that card's centre,
# 13 columns in (`:639-640`): 26 + 3 + 13 + 1 = 43.  Operator question
# `INC8-D3-Q1`.  The switch width is derived, never written: it is
# `LEGEND_DOCKED_CELLS + LEGEND_DOCK_MIN_VIEW_CELLS` plus whatever chrome the
# host paints left of its view (the map's rail, when shown).
LEGEND_DOCK_MIN_VIEW_CELLS = 43
DOCKED_CLASS = "-docked"
_KEY_CELLS = 10
# The sample column, one per layout.  A sample as wide as its column or wider
# takes its own line.  DOCKED, eight cells, so the docked label budget
# (`LEGEND_DOCKED_ROW_CELLS - len(_INDENT) - 8` = 29) holds the longest ruled
# labels, `V35`'s "pending fields here and below" and `V37`'s "branch: half
# or more recorded", on one row.  MODAL, twelve (round-3 copy verdict), so the
# atlas samples up to eleven cells (`▐ ▸ inv +23`, `◫ sin acta`) share their
# label's row.  Both are widths inside a panel of fixed width, not terminal
# widths, so the round-3 width principle leaves them declared.
_SAMPLE_CELLS_DOCKED = 8
_SAMPLE_CELLS_MODAL = 12
_INDENT = "  "
# Verdict `Q7`: rows whose members the view paints in ADJACENT cells -- a
# schema letter and its mark (`views/layered.py:628-631`) -- so the legend
# paints their samples with no space between them, each in its own style.
ADJACENT_ROWS = frozenset({"V27", "V28"})

# `HLR-N16.4`'s threshold is "the keys that have an effect equal the set the
# legend PAINTS for its own scope".  This group paints `bindings_for(SCOPE_HELP)`
# -- the legend's own scope -- as its own always-visible widget
# (`_render_own_scope_keys`), OUTSIDE the scrollable pane and outside
# `_render_keymap`: `LLR-R05.2` (`TC-R25`/`TC-R26`, a prior batch's sealed
# requirement) pins `_render_keymap`'s presented set to EXACTLY
# `bindings_for(self.scope)`, with no foreign-scope row.
#
# Verdict `E3` ratified the group and its title (`A5`) and compressed it to two
# lines.  Its words are the legend's own English copy, one word per ACTION,
# the key glyphs read from the seat: `esc q close · ↑ ↓ scroll` /
# `pageup pagedown page · home end ends`.  Since round 3 it is the ONE place
# the close hint is painted; the title no longer repeats it.  The seat's own labels stay as they
# are until Inc-9 (key labels are Inc-9's), which is why the words live here.
# `01b` §3.6 lists them, and an arm pins that every `SCOPE_HELP` action has one.
LEGEND_OWN_SCOPE_GROUP = "in this legend"
LEGEND_OWN_SCOPE_FIRST = True
OWN_SCOPE_COPY: tuple[tuple[tuple[str, ...], str], ...] = (
    (("dismiss_none",), "close"),
    (("legend_up", "legend_down"), "scroll"),
    (("legend_page_up", "legend_page_down"), "page"),
    (("legend_home", "legend_end"), "ends"),
)
OWN_SCOPE_ITEMS_PER_LINE = 2
_ITEM_SEP = " · "

# `A-104` -- ASSUMPTION, queued for the operator: a compound row (one `01b` row
# naming several styles, e.g. `V19`) paints ALL its samples on ONE line, each
# in its own style, under ONE caption.  `False` paints one line per member,
# repeating the caption.  No arm depends on this: they assert over painted
# (glyph, style) pairs, not over lines.
COMPOUND_ON_ONE_LINE = True

# `01b` §3.6, verbatim -- in English since the 2026-09-29 language ruling.
# The sections are painted in this order (verdict `E1`: the vocabulary first).
LEGEND_TITLE = "legend"
SECTION_VOCABULARY = "what this view paints"
SECTION_COLOURS = "what the colours mean"
SECTION_KEYS = "keys in this view"
#: `H1` (closing verdict, round 5): the old wording over-promised -- `?` typed
#: into a focused text FIELD types a literal `?` there (select-all on focus
#: replaces the title with it and saves it, `B-36`/`B-72`, a later batch's
#: fix), it does not open the legend.  Two lines because the honest sentence
#: no longer fits the docked row's budget (`LEGEND_DOCKED_ROW_CELLS`) on one.
FOOTER_LINES = ("? explains the view you are in,", "outside text fields")


# `INC8-CR-F9`: this module had its own copy of `darkside._cells`. One
# implementation, read from its one owner.
_cells = darkside._cells

_ON_GROUND = f"on {darkside.GROUND}"


def _sample_style(declared: str) -> str:
    """Verdict `E2`: a sample is painted on GROUND, the view's own ground, so
    it reads as it does in the view -- a tone sitting on `PANEL` is a
    different tone.  A member that declares its own ground (`INK on PANEL`,
    `INC8-P2-UX-F6`: the ones its view paints only on a card or a pill) keeps
    it; the label beside the sample stays on `PANEL`."""
    resolved = darkside.resolve_style(declared)
    return resolved if " on " in f" {resolved} " else f"{resolved} {_ON_GROUND}"


def _ground(style: str) -> str:
    """The ground a painted sample style sits on."""
    return style.split(" on ", 1)[1]


def docks(width: int, view_left: int) -> bool:
    """Verdict `F9`: at terminal `width`, with the view starting at column
    `view_left`, the docked panel still leaves the view its minimum."""
    return width - LEGEND_DOCKED_CELLS - view_left >= LEGEND_DOCK_MIN_VIEW_CELLS


def own_scope_word(action: str) -> str | None:
    """The own-scope group's word for a `SCOPE_HELP` action, or `None`."""
    return next((word for actions, word in OWN_SCOPE_COPY if action in actions), None)


def vocabulary_for(view: str, rail_shown: bool = True) -> list[tuple[str, str, str, str]]:
    """`LLR-N16.2.1`: the members `view`'s legend paints, in declaration order,
    read from the ONE declaration -- never a copy of it.

    `H4` (closing verdict, round 5): while `rail_shown` is `False`, the rows
    the rail alone paints (`darkside.RAIL_VOCABULARY`) are dropped too --
    there is nothing on screen left for them to explain.  Every other row
    stays, coverage strip and meter included: their source is not the rail
    widget (see `RAIL_VOCABULARY`'s own docstring)."""
    wanted = set(darkside.LEGEND_VIEWS.get(view, ()))
    members = [m for m in darkside.DECLARED_VOCABULARY if m[0] in wanted]
    if rail_shown:
        return members
    return [m for m in members if m[0] not in darkside.RAIL_VOCABULARY]


def colours_for(view: str) -> list[tuple[str, str, str, str]]:
    """Verdict `F1`: the colour rows `view`'s legend paints -- only the ones
    its own view paints -- in declaration order, read from the ONE
    declaration."""
    wanted = set(darkside.LEGEND_COLOURS.get(view, ()))
    return [c for c in darkside.DECLARED_COLOURS if c[0] in wanted]


def _trimmed(text: Text) -> Text:
    """Drop the last row's newline, which would paint an empty row under it."""
    if text.plain.endswith("\n"):
        text.right_crop(1)
    return text


def _bounded_run(pieces: list[tuple[str, str]], budget: int) -> list[tuple[str, str]]:
    """Each piece coerced and fit into the ROOM LEFT after the ones before it,
    so the run as a whole never exceeds `budget` cells (`INC8-CR-F7`'s rule,
    for a row made of several strings)."""
    out: list[tuple[str, str]] = []
    used = 0
    for text, style in pieces:
        room = budget - used
        if room <= 0:
            break
        shown = darkside.fit(text, min(darkside.shown_cells(text), room))
        out.append((shown, style))
        used += _cells(shown)
    return out


class HelpScreen(ModalScreen[None]):
    """Modal legend for one scope and one view.

    Help is scoped, not global: showing a key that does nothing here is the
    discoverability bug this batch exists to remove (US-N03).
    """

    # Its own scope.  Borrowing the palette's meant binding `enter -> run_selected`,
    # a method this screen does not define, which was a silent no-op.
    BINDINGS = [
        Binding(key, action, label, priority=priority)
        for key, action, label, priority in textual_bindings(SCOPE_HELP)
    ]

    CSS = f"""
    HelpScreen {{
        align: center middle;
        background: #000000 70%;
    }}
    #help-dialog {{
        width: {LEGEND_PANEL_CELLS};
        height: 90%;
        max-height: {LEGEND_MODAL_MAX_ROWS};
        background: #121212;
        padding: 1 {_PAD_X};
    }}
    /* `D4` / `E1`, docked: the view stays visible and undimmed on the left; a
       narrow panel runs the full height of the right edge, so it covers the
       ficha inspector whole instead of leaving an "L" of it (`UX-F9`).
       Depth is the one grey step from the view's ground to PANEL -- no
       border.  Full height is `A-107`'s docked-only exemption from `TC-R36`'s
       height cap; the modal keeps the cap. */
    HelpScreen.{DOCKED_CLASS} {{
        align: right top;
        background: #000000 0%;
    }}
    HelpScreen.{DOCKED_CLASS} #help-dialog {{
        width: {LEGEND_DOCKED_CELLS};
        height: 100%;
        max-height: 100%;
    }}
    /* S-08 (LLR-R05.1).  The map scope carries 27 bindings in 5 groups, which the
       body renders as 40 rows — more than `max-height` shows at any terminal
       size.  Before this rule the surplus was clipped away with no way to reach
       it, and the whole 11-member `view` group fell off the bottom in silence.
       The BINDINGS scroll while the title does not: the title is the one row
       that tells the operator which view they are reading. */
    #help-bindings {{
        height: 1fr;
        overflow-y: auto;
        scrollbar-size-vertical: 1;
        /* `INC8-UX-F11`: Textual's own default (unstyled) thumb measured
           1.55:1 against this pane's track -- under WCAG 1.4.11's 3:1 floor
           for a non-text UI component.  `ASH` on `PANEL` measures 7.43:1
           (`test_inc8_ux_f11_...` derives the ratio from the token hexes).
           Not `ACCENT`: `LLR-S06.3.3` seals the blue LITERAL at exactly 8
           sites (`B-43`), and this pane is not one of them. */
        scrollbar-color: #a3a3a3;
        scrollbar-background: #121212;
    }}
    /* One blank row between sections, none above the first. */
    #help-bindings > Static {{
        margin-top: 1;
    }}
    #help-bindings > Static:first-child {{
        margin-top: 0;
    }}
    #help-title {{
        margin-bottom: 1;
    }}
    #help-own-scope {{
        margin-bottom: 1;
    }}
    """

    def __init__(
        self, scope: str = SCOPE_APP, view: str | None = None, host: object | None = None,
    ) -> None:
        super().__init__()
        self.scope = scope
        # HLR-N16.2: the title names the VIEW; a screen that declares none is
        # named by its scope.
        self.view = view or scope
        # The screen the legend explains.  Verdict `F2`: a host that offers
        # `legend_docked` / `legend_closed` (the map screen) is told where the
        # docked panel's edge is, so it can keep its selection in sight.
        self.host = host
        # Which layout the painted rows are budgeted for.  An unmounted screen
        # (the white-box arms) renders for the modal.
        self.docked = False
        # `H4`: the rail state the vocabulary was LAST painted for.  `None`
        # so the very first `_apply_layout` call always agrees with whatever
        # `compose` already painted, and never repaints on a false mismatch.
        self._rail_shown_painted: bool | None = None

    @property
    def row_cells(self) -> int:
        """The row budget of the layout the legend is in (`E1`)."""
        return LEGEND_DOCKED_ROW_CELLS if self.docked else LEGEND_ROW_CELLS

    @property
    def sample_cells(self) -> int:
        """The sample column of the layout the legend is in (round 3)."""
        return _SAMPLE_CELLS_DOCKED if self.docked else _SAMPLE_CELLS_MODAL

    # -- layout (`D4`, `E1`) -------------------------------------------------

    def _view_left(self) -> int:
        """The first column of the view this legend explains: the host's own
        answer (the map screen: its rail, when shown), else the left edge."""
        return getattr(self.host, "legend_view_left", 0)

    def _rail_shown(self) -> bool:
        """`H4`: whether the host's rail is visible right now, read live from
        the host rather than cached -- a screen that declares no rail (the
        sala) is always `True`, the vacuous case `vocabulary_for` already
        handles by never dropping a row.  Keys are modal while the legend is
        open, so a hand toggle (`R`) cannot fire; a resize across the host's
        own auto-hide width is the only way this can change under an open
        legend, which is why `_apply_layout` -- the resize path -- is what
        reads it again, not just `compose`."""
        return not getattr(self.host, "rail_hidden", False)

    def _apply_layout(self, width: int) -> None:
        docked = docks(width, self._view_left())
        self.set_class(docked, DOCKED_CLASS)
        rail_shown = self._rail_shown()
        # `H4`: a resize can flip the host's rail without flipping `docked`
        # (the two thresholds are derived independently) -- the old guard,
        # keyed on `docked` alone, would leave a rail row painted after the
        # rail it explains had already gone, or vice versa.
        repaint = docked != self.docked or rail_shown != self._rail_shown_painted
        self.docked = docked
        self._rail_shown_painted = rail_shown
        if repaint and self.is_mounted:
            self._repaint()
        # Verdict `F2`: the view moves only because of docking -- keys never
        # reach it (`E1`).  The panel is flush right, so its edge is here.
        dock = getattr(self.host, "legend_docked", None)
        if dock is not None:
            dock(width - LEGEND_DOCKED_CELLS if docked else None)

    def on_mount(self) -> None:
        self._apply_layout(self.app.size.width)

    def on_resize(self, event) -> None:
        self._apply_layout(event.size.width)

    def _sections(self) -> list[tuple[str, Text]]:
        """(widget id, text) of the scrolling body, in `01b` §3.6's order:
        the vocabulary first (verdict `E1`).  LLR-N16.2.2: an empty
        vocabulary omits its section -- and the colour rows, which exist to
        explain the vocabulary's hues.  A view that paints no colour row
        (`F1`) omits the colour section too."""
        out: list[tuple[str, Text]] = []
        vocabulary = vocabulary_for(self.view, self._rail_shown())
        if vocabulary:
            out.append(("help-vocabulary", self._render_vocabulary(vocabulary)))
            if colours_for(self.view):
                out.append(("help-colours", self._render_colours()))
        out.append(("help-content", self._render_keymap()))
        out.append(("help-footer", self._render_footer()))
        return out

    def _repaint(self) -> None:
        """A resize across the dock threshold re-budgets every painted row."""
        self.query_one("#help-title", Static).update(self._render_title())
        self.query_one("#help-own-scope", Static).update(self._render_own_scope_keys())
        for widget_id, text in self._sections():
            self.query_one(f"#{widget_id}", Static).update(text)

    def compose(self) -> ComposeResult:
        self.docked = docks(self.app.size.width, self._view_left())
        self._rail_shown_painted = self._rail_shown()
        body = [Static(text, id=widget_id) for widget_id, text in self._sections()]
        title = Static(self._render_title(), id="help-title")
        own_scope = Static(self._render_own_scope_keys(), id="help-own-scope")
        pane = VerticalScroll(*body, id="help-bindings")
        # `E3` / `INC8-F-CR-F1`: the legend's own keys sit OUTSIDE the
        # scrollable pane either way -- visible at rest AND at the end of the
        # scroll range, pinned by `test_e3_the_own_keys_are_visible_at_rest_and_at_the_end`
        # -- so `LEGEND_OWN_SCOPE_FIRST` only chooses which side of the body
        # they sit on, never whether they are reachable.
        children = [title, own_scope, pane] if LEGEND_OWN_SCOPE_FIRST else [title, pane, own_scope]
        yield Vertical(*children, id="help-dialog")

    # -- painting ----------------------------------------------------------
    # LLR-N16.2.3: every string reaches the surface through `darkside.fit`,
    # which coerces with `darkside.plain` and bounds the row in cells.  Nothing
    # here is handed to a markup-parsing sink: `Text.assemble` of `(str, style)`
    # pairs parses none, which is why the title is a `Text` and not a `str`.

    def _render_title(self) -> Text:
        # Round 3: the close hint is painted once, in the own-scope group, so
        # the title is the view's name alone -- bounded to the row like every
        # other painted string (`INC8-SEC-F3`'s clamp now lives in that group).
        return Text.assemble(
            (darkside.fit(f"{LEGEND_TITLE} · {self.view}", self.row_cells).rstrip(),
             f"bold {darkside.INK}"),
        )

    def _append_key_group(
        self, parts: list[tuple[str, str]], title: str,
        bindings: list, label_cells: int, *, leading_blank: bool = True,
    ) -> None:
        prefix = "\n" if leading_blank else ""
        parts.append((f"{prefix}{darkside.fit(title, self.row_cells).rstrip()}\n", darkside.ASH))
        for binding in bindings:
            parts.append((_INDENT, ""))
            parts.append((darkside.fit(binding.glyph, _KEY_CELLS), darkside.ACCENT))
            parts.append((darkside.fit(binding.label, label_cells) + "\n", darkside.INK))

    def _render_keymap(self) -> Text:
        # `LLR-R05.2` (`TC-R25`/`TC-R26`, a prior batch's sealed requirement):
        # this method's presented set is EXACTLY `bindings_for(self.scope)`,
        # with no foreign-scope row -- `tests/test_repair_layout.py` parses
        # this exact method and asserts it. `HLR-N16.4`'s own keys are a
        # DIFFERENT scope (`SCOPE_HELP`) by construction, so they are painted
        # by `_render_own_scope_keys` instead, never folded in here.
        label_cells = self.row_cells - len(_INDENT) - _KEY_CELLS
        parts: list[tuple[str, str]] = [(SECTION_KEYS + "\n", f"bold {darkside.ASH}")]
        entries = bindings_for(self.scope)
        for group, bindings in groupby(
            sorted(entries, key=lambda b: b.group), key=lambda b: b.group
        ):
            self._append_key_group(parts, group, list(bindings), label_cells)
        return _trimmed(Text.assemble(*parts))

    def _render_own_scope_keys(self) -> Text:
        """`HLR-N16.4` / verdict `E3`: the legend's own scope (`SCOPE_HELP`)
        in two lines under its title -- each item the seat's key glyphs for
        one word of `OWN_SCOPE_COPY`.  See `compose` for why it is a SEPARATE
        widget from `_render_keymap`, outside the scrolling pane."""
        seat = bindings_for(SCOPE_HELP)
        items = []
        for actions, word in OWN_SCOPE_COPY:
            glyphs = [b.glyph for b in seat if b.action in actions]
            if glyphs:
                items.append((glyphs, word))
        budget = self.row_cells - len(_INDENT)
        parts: list[tuple[str, str]] = [
            (darkside.fit(LEGEND_OWN_SCOPE_GROUP, self.row_cells).rstrip(), darkside.ASH)]
        for start in range(0, len(items), OWN_SCOPE_ITEMS_PER_LINE):
            pieces: list[tuple[str, str]] = []
            for glyphs, word in items[start:start + OWN_SCOPE_ITEMS_PER_LINE]:
                if pieces:
                    pieces.append((_ITEM_SEP, darkside.ASH))
                for i, glyph in enumerate(glyphs):
                    pieces.append(((" " if i else "") + glyph, darkside.ACCENT))
                pieces.append((" " + word, darkside.INK))
            parts.append(("\n" + _INDENT, ""))
            parts.extend(_bounded_run(pieces, budget))
        return Text.assemble(*parts)

    def _render_vocabulary(self, members: list[tuple[str, str, str, str]]) -> Text:
        """LLR-N16.2.1 / HLR-N16.2: each sample painted in its declared style.

        `INC8-CR-F7`: grouped by a dict keyed on row id, not `itertools.groupby`.
        `groupby` only merges RUNS of equal keys, so it silently SPLIT a row's
        members the moment a different id sat between them in declaration
        order -- true today only because `DECLARED_VOCABULARY` happens to keep
        every row's members adjacent, a fact this function has no business
        depending on.  A dict keyed by row id groups by IDENTITY regardless of
        position, and still preserves first-seen order (`dict` since 3.7).
        """
        text = Text.assemble((f"{SECTION_VOCABULARY}\n\n", f"bold {darkside.ASH}"))
        rows: dict[str, list[tuple[str, str, str, str]]] = {}
        for member in members:
            rows.setdefault(member[0], []).append(member)
        for group in rows.values():
            lines = [group] if COMPOUND_ON_ONE_LINE else [[m] for m in group]
            for line in lines:
                self._vocabulary_line(text, line)
        return _trimmed(text)

    def _vocabulary_line(self, text: Text, members: list[tuple[str, str, str, str]]) -> None:
        # `INC8-CR-F7`: each sample is fit into the ROOM LEFT after the ones
        # before it, not just clamped against the row's total budget in
        # isolation.  Clamping each sample alone bounded no ROW: several
        # samples each individually under budget could still SUM past it, and
        # the pad below went negative (`" " * negative` is silently `""`,
        # never an error) while the row it padded stayed over width.
        row = self.row_cells
        column = self.sample_cells
        budget = row - len(_INDENT)
        # `Q7`: a letter and its mark are painted in adjacent cells, as the
        # view paints them; any other compound row keeps one space between.
        gap = 0 if members[0][0] in ADJACENT_ROWS else 1
        samples: list[tuple[str, str]] = []
        width = 0
        for _row_id, glyph, _label, style in members:
            if not glyph:
                continue
            sep = gap if samples else 0
            room = budget - width - sep
            if room <= 0:
                break
            shown = darkside.fit(glyph, min(darkside.shown_cells(glyph), room))
            if sep:
                # On the ground of the sample before it (`INC8-P2-UX-F6`), so
                # a row painted on `PANEL` is not split by a strip of `GROUND`.
                samples.append((" ", f"on {_ground(samples[-1][1])}"))
                width += sep
            samples.append((shown, _sample_style(style)))
            width += _cells(shown)
        label = members[0][2]
        label_cells = row - len(_INDENT) - column
        text.append(_INDENT)
        for sample, style in samples:
            text.append(sample, style=style)
        if width >= column:
            # A sample wider than its column keeps its own line rather than
            # being cut: a truncated glyph misdescribes the form it stands for.
            text.append(" " * max(0, row - len(_INDENT) - width) + "\n")
            text.append(_INDENT + " " * column)
        else:
            text.append(" " * (column - width))
        text.append(darkside.fit(label, label_cells) + "\n", style=darkside.INK)

    def _render_colours(self) -> Text:
        label_cells = self.row_cells - len(_INDENT) - 3
        parts: list[tuple[str, str]] = [(f"{SECTION_COLOURS}\n\n", f"bold {darkside.ASH}")]
        for _rid, swatch, label, token in colours_for(self.view):
            parts.append((_INDENT, ""))
            parts.append((darkside.fit(swatch, 1), darkside.resolve_style(token)))
            parts.append(("  ", ""))
            parts.append((darkside.fit(label, label_cells) + "\n", darkside.INK))
        return _trimmed(Text.assemble(*parts))

    def _render_footer(self) -> Text:
        return Text.assemble(
            ("\n".join(darkside.fit(line, self.row_cells) for line in FOOTER_LINES),
             darkside.ASH)
        )

    # -- actions -----------------------------------------------------------
    # HLR-N16.4: the legend's own keys.  They act on the pane whether or not it
    # holds focus, so the seat rows are true in every focus state.

    def _pane(self) -> VerticalScroll:
        return self.query_one("#help-bindings", VerticalScroll)

    def action_legend_up(self) -> None:
        self._pane().scroll_up(animate=False)

    def action_legend_down(self) -> None:
        self._pane().scroll_down(animate=False)

    def action_legend_page_up(self) -> None:
        self._pane().scroll_page_up(animate=False)

    def action_legend_page_down(self) -> None:
        self._pane().scroll_page_down(animate=False)

    def action_legend_home(self) -> None:
        self._pane().scroll_home(animate=False)

    def action_legend_end(self) -> None:
        self._pane().scroll_end(animate=False)

    def action_dismiss_none(self) -> None:
        closed = getattr(self.host, "legend_closed", None)
        if closed is not None:
            closed()
        self.dismiss(None)
