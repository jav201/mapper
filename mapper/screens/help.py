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

# The legend panel's width, ONE constant for both layouts (Inc-8 verdict `D4`):
# a modal below `LEGEND_DOCK_MIN_WIDTH` columns, docked on the right at or above
# it.  The CSS below is built from it.
LEGEND_PANEL_CELLS = 80
_PAD_X = 2
_SCROLLBAR_CELLS = 1
# `LLR-N16.2.3`'s row-length clause: every painted row of the scrolling body is
# exactly this many cells -- the panel less its left and right padding and the
# scrollbar.  A row wider than the pane would wrap, and the wrapped half would
# read as a row of its own.  `INC8-CR-F2`:
# `test_llr_n16_2_3_legend_coerces_and_bounds_every_string` in
# `tests/test_help_scope.py` pins this against the real widget's
# `scrollable_content_region` in BOTH layouts.
LEGEND_ROW_CELLS = LEGEND_PANEL_CELLS - 2 * _PAD_X - _SCROLLBAR_CELLS
# `D4`: at this terminal width and wider the legend docks beside the view
# instead of covering it.  The panel stays modal for keys in both layouts: a
# key pressed while the legend is open never reaches the view under it.
# The operator's "118 columns" is the batch's declared context of use, the
# width every render of this batch is drawn at, so it is read from its one
# home (`test_crumb.py::test_decl_118_is_spelled_ONCE`).  It is NOT the map
# screen's auto-hide threshold, which equals it by arithmetic (`INC8-D-Q7`).
LEGEND_DOCK_MIN_WIDTH = darkside.DECLARED_CONTEXT_CELLS
DOCKED_CLASS = "-docked"
_KEY_CELLS = 10
_SAMPLE_CELLS = 12
_INDENT = "  "

# `INC8-CR-F1` / `INC8-UX-F1` / `UX-F10`.  `HLR-N16.4`'s threshold is "the keys
# that have an effect equal the set the legend PAINTS for its own scope" --
# and until this corrective pass the legend never painted its own six scroll
# keys (or `q cerrar`) at all: only `esc cerrar`, in the title.  This group
# paints `bindings_for(SCOPE_HELP)` -- the legend's own scope -- as its own
# always-visible widget (`_render_own_scope_keys`), OUTSIDE the scrollable
# pane and outside `_render_keymap` -- `LLR-R05.2` (`TC-R25`/`TC-R26`, a prior
# batch's sealed requirement) pins `_render_keymap`'s presented set to EXACTLY
# `bindings_for(self.scope)`, with no foreign-scope row, so `SCOPE_HELP`'s own
# rows cannot be folded into that method without breaking it.
#
# `A5`, queued for the operator (see the corrective-pass record): `01b` §3.6
# does not name this group, so its title is an Inc-8 constant pending
# ratification, in the same class as Q3's un-ratified label prose.  Placement
# is behind its own flag rather than hard-coded into `compose`, so the
# operator can move it without touching the painting logic -- it sits OUTSIDE
# the scrollable pane either way, so it stays reachable with no scrolling
# regardless of the flag.
LEGEND_OWN_SCOPE_GROUP = "en esta leyenda"
LEGEND_OWN_SCOPE_FIRST = True

# `A-104` -- ASSUMPTION, queued for the operator: a compound row (one `01b` row
# naming several styles, e.g. `V19`) paints ALL its samples on ONE line, each
# in its own style, under ONE caption.  `False` paints one line per member,
# repeating the caption.  No arm depends on this: they assert over painted
# (glyph, style) pairs, not over lines.
COMPOUND_ON_ONE_LINE = True

# `01b` §3.6, verbatim.
SECTION_KEYS = "teclas de esta vista"
SECTION_VOCABULARY = "vocabulario de esta vista"
SECTION_COLOURS = "colores con empleo"
FOOTER_LINES = ("cada vista tiene SU leyenda — ", "misma tecla, contenido de la vista")


# `INC8-CR-F9`: this module had its own copy of `darkside._cells`. One
# implementation, read from its one owner.
_cells = darkside._cells


def _trimmed(text: Text) -> Text:
    """Drop the last row's newline, which would paint an empty row under it."""
    if text.plain.endswith("\n"):
        text.right_crop(1)
    return text


def vocabulary_for(view: str) -> list[tuple[str, str, str, str]]:
    """`LLR-N16.2.1`: the members `view`'s legend paints, in declaration order,
    read from the ONE declaration -- never a copy of it."""
    wanted = set(darkside.LEGEND_VIEWS.get(view, ()))
    return [m for m in darkside.DECLARED_VOCABULARY if m[0] in wanted]


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
        max-height: 28;
        background: #121212;
        padding: 1 {_PAD_X};
    }}
    /* `D4`, docked: the view stays visible and undimmed on the left; the
       panel sits top-right.  Depth is the one grey step from the view's ground
       to PANEL -- no border.  The panel keeps the modal's height rules:
       `TC-R36` (`LLR-R05`, a sealed prior batch) pins `max-height` as what
       governs at 140x45, so a full-height dock is an operator question, not
       a CSS line. */
    HelpScreen.{DOCKED_CLASS} {{
        align: right top;
        background: #000000 0%;
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
    #help-title {{
        margin-bottom: 1;
    }}
    #help-own-scope {{
        margin-bottom: 1;
    }}
    """

    def __init__(self, scope: str = SCOPE_APP, view: str | None = None) -> None:
        super().__init__()
        self.scope = scope
        # HLR-N16.2: the title names the VIEW; a screen that declares none is
        # named by its scope.
        self.view = view or scope

    # -- layout (`D4`) -----------------------------------------------------

    def _apply_layout(self, width: int) -> None:
        self.set_class(width >= LEGEND_DOCK_MIN_WIDTH, DOCKED_CLASS)

    def on_mount(self) -> None:
        self._apply_layout(self.app.size.width)

    def on_resize(self, event) -> None:
        self._apply_layout(event.size.width)

    def compose(self) -> ComposeResult:
        body = [Static(self._render_keymap(), id="help-content")]
        vocabulary = vocabulary_for(self.view)
        # LLR-N16.2.2: an empty vocabulary omits its section -- and the colour
        # rows, which exist to explain the vocabulary's hues.
        if vocabulary:
            body.append(Static(self._render_vocabulary(vocabulary), id="help-vocabulary"))
            body.append(Static(self._render_colours(), id="help-colours"))
        body.append(Static(self._render_footer(), id="help-footer"))
        title = Static(self._render_title(), id="help-title")
        own_scope = Static(self._render_own_scope_keys(), id="help-own-scope")
        pane = VerticalScroll(*body, id="help-bindings")
        # `A5` (`INC8-CR-F1`/`INC8-UX-F1`/`UX-F10`): the legend's own keys sit
        # OUTSIDE the scrollable pane either way -- always painted, not merely
        # "at rest" -- so `LEGEND_OWN_SCOPE_FIRST` only chooses which side of
        # the scrollable body they sit on, never whether they are reachable.
        children = [title, own_scope, pane] if LEGEND_OWN_SCOPE_FIRST else [title, pane, own_scope]
        yield Vertical(*children, id="help-dialog")

    # -- painting ----------------------------------------------------------
    # LLR-N16.2.3: every string reaches the surface through `darkside.fit`,
    # which coerces with `darkside.plain` and bounds the row in cells.  Nothing
    # here is handed to a markup-parsing sink: `Text.assemble` of `(str, style)`
    # pairs parses none, which is why the title is a `Text` and not a `str`.

    def _render_title(self) -> Text:
        # `INC8-SEC-F3`.  `close.label` is a seat value: normally six letters,
        # but nothing upstream bounds it, and an unbounded hint here painted a
        # 95-cell row from a 75-cell budget.  Every width below is CLAMPED so
        # `title + gap + glyph + " " + label` can never exceed `LEGEND_ROW_CELLS`,
        # however wide the seat's label gets.
        close = next(b for b in bindings_for(SCOPE_HELP) if b.action == "dismiss_none")
        hint = f"{close.glyph} {close.label}"
        hint_cells = min(_cells(hint), LEGEND_ROW_CELLS)
        glyph_cells = min(_cells(close.glyph), hint_cells)
        label_cells = max(0, hint_cells - glyph_cells - 1)
        title_cells = max(0, LEGEND_ROW_CELLS - hint_cells)
        title = darkside.fit(f"leyenda · {self.view}", title_cells).rstrip()
        gap = max(0, LEGEND_ROW_CELLS - _cells(title) - hint_cells)
        return Text.assemble(
            (title, f"bold {darkside.INK}"),
            (" " * gap, ""),
            (darkside.fit(close.glyph, glyph_cells), darkside.ACCENT),
            (" " + darkside.fit(close.label, label_cells), darkside.ASH),
        )

    def _append_key_group(
        self, parts: list[tuple[str, str]], title: str,
        bindings: list, label_cells: int, *, leading_blank: bool = True,
    ) -> None:
        prefix = "\n" if leading_blank else ""
        parts.append((f"{prefix}{darkside.fit(title, LEGEND_ROW_CELLS).rstrip()}\n", darkside.ASH))
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
        label_cells = LEGEND_ROW_CELLS - len(_INDENT) - _KEY_CELLS
        parts: list[tuple[str, str]] = [(SECTION_KEYS + "\n", f"bold {darkside.ASH}")]
        entries = bindings_for(self.scope)
        for group, bindings in groupby(
            sorted(entries, key=lambda b: b.group), key=lambda b: b.group
        ):
            self._append_key_group(parts, group, list(bindings), label_cells)
        return _trimmed(Text.assemble(*parts))

    def _render_own_scope_keys(self) -> Text:
        """`INC8-CR-F1` / `INC8-UX-F1` / `UX-F10` / `HLR-N16.4`.

        The legend's own scope (`SCOPE_HELP`), painted as its own always-shown
        group -- see `compose`'s comment for why it is a SEPARATE widget from
        `_render_keymap`, not a group folded into it.
        """
        label_cells = LEGEND_ROW_CELLS - len(_INDENT) - _KEY_CELLS
        parts: list[tuple[str, str]] = []
        self._append_key_group(
            parts, LEGEND_OWN_SCOPE_GROUP, bindings_for(SCOPE_HELP), label_cells,
            leading_blank=False,
        )
        return _trimmed(Text.assemble(*parts))

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
        text = Text.assemble((f"\n{SECTION_VOCABULARY}\n\n", f"bold {darkside.ASH}"))
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
        budget = LEGEND_ROW_CELLS - len(_INDENT)
        samples: list[tuple[str, str]] = []
        width = 0
        for _row_id, glyph, _label, style in members:
            if not glyph:
                continue
            sep = 1 if samples else 0
            room = budget - width - sep
            if room <= 0:
                break
            shown = darkside.fit(glyph, min(_cells(glyph), room))
            if samples:
                samples.append((" ", ""))
                width += 1
            samples.append((shown, darkside.resolve_style(style)))
            width += _cells(shown)
        label = members[0][2]
        label_cells = LEGEND_ROW_CELLS - len(_INDENT) - _SAMPLE_CELLS
        text.append(_INDENT)
        for sample, style in samples:
            text.append(sample, style=style)
        if width >= _SAMPLE_CELLS:
            # A sample wider than its column keeps its own line rather than
            # being cut: a truncated glyph misdescribes the form it stands for.
            text.append(" " * max(0, LEGEND_ROW_CELLS - len(_INDENT) - width) + "\n")
            text.append(_INDENT + " " * _SAMPLE_CELLS)
        else:
            text.append(" " * (_SAMPLE_CELLS - width))
        text.append(darkside.fit(label, label_cells) + "\n", style=darkside.INK)

    def _render_colours(self) -> Text:
        label_cells = LEGEND_ROW_CELLS - len(_INDENT) - 3
        parts: list[tuple[str, str]] = [(f"\n{SECTION_COLOURS}\n\n", f"bold {darkside.ASH}")]
        for swatch, label, token in darkside.DECLARED_COLOURS:
            parts.append((_INDENT, ""))
            parts.append((darkside.fit(swatch, 1), darkside.resolve_style(token)))
            parts.append(("  ", ""))
            parts.append((darkside.fit(label, label_cells) + "\n", darkside.INK))
        return _trimmed(Text.assemble(*parts))

    def _render_footer(self) -> Text:
        return Text.assemble(
            ("\n" + "\n".join(darkside.fit(line, LEGEND_ROW_CELLS) for line in FOOTER_LINES),
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
        self.dismiss(None)
