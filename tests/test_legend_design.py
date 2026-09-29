"""Inc-8 design pass -- the legend and the view agree, mechanically (verdict D2).

`INC8-F2` / `UX-F3`: the legend proved it paints each member in its DECLARED
style, and the declaration proved it equals `01b` -- but nothing compared either
with what the VIEW paints, and six declared rows turned out to describe forms no
renderer draws.  These arms render every view over real fixtures and read the
composited frame, in both directions:

  SOUNDNESS     every member a view's legend explains is painted by that view,
                in the member's declared style;
  COMPLETENESS  every meaningful glyph the view paints belongs to some member
                of that view's vocabulary.

THE EXCLUSION RULE is written once, in `meaningful`, `_excluded_widget` and
`OVERLAY_STYLES`, and the catalogue instrument in `increment-022` IMPORTS it
from here rather than re-stating it (`INC8-F-CR-F6`):

  X1  text          letters, digits and spaces (`L*`, `N*`, `Z*`)
  X2  punctuation   ASCII punctuation and symbols, plus the three separators
                    the catalogue found painted as text: `·` `…` `—`
                    (`INC8-F-CR-F2`; any OTHER non-ASCII mark is meaningful)
  X3  app chrome    the tab strip, the hint line, the key bar and the sala's
                    identity row -- the same on every screen, and not the view
  X4  key glyphs    a character the seat uses as a key's glyph (`↵`, `↑`): the
                    legend's key section explains those
  X5  table header  a `DataTable`'s column-header row
  X6  overlays      (completeness only) a member's glyph under a selection or
                    cursor tone: `V23`'s, `V24`'s, and the rail cursor's
                    `INK on STEP` -- every other tone must be a member's own

COMPLETENESS IS PER (GLYPH, STYLE) since `INC8-F-CR-F4`: a declared glyph in a
tone no member and no overlay declares is RED, not "explained".

THE RULE'S KNOWN BLIND SPOTS, stated so nobody reads more into a green run: X2
hides `·` (`V21b`, a separator code point the rail's lattice uses as a mark),
which soundness still checks; the diff mode (`=`) is not driven -- it needs a
git history -- so its tones are seen by neither direction (carried in
`increment-022`).
"""
from __future__ import annotations

import string
import unicodedata
from datetime import date

import pytest
from rich.cells import cell_len
from rich.style import Style
from textual.widgets import DataTable

from mapper import darkside, keymap
from mapper.app import HomeScreen, MapperApp, MapScreen
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.screens.help import (
    DOCKED_CLASS,
    LEGEND_DOCK_MIN_WIDTH,
    LEGEND_PANEL_CELLS,
    LEGEND_ROW_CELLS,
    HelpScreen,
    vocabulary_for,
)

# ---------------------------------------------------------------------------
# The exclusion rule -- ONE statement of it.

CHROME_WIDGETS = frozenset({"TabStrip", "HintLine", "KeyBar", "home-identity"})
KEY_GLYPHS = frozenset(
    ch for b in keymap.KEYMAP for ch in b.glyph if not (ch.isalnum() or ch.isspace())
)


#: X2's non-ASCII half: the separators the catalogue found painted AS TEXT
#: (`mapa · 36n`, a clipped title's `…`, the sala's `—`).  Named, not a
#: category: `P*` as a whole would also have excused a `•` or a `‹` that a
#: renderer started using as a mark (`INC8-F-CR-F2`).
SEPARATORS = frozenset("·…—")


def meaningful(ch: str) -> bool:
    """X1, X2 and X4: may this painted character carry a meaning of its own?"""
    if ord(ch) < 0x80 or unicodedata.category(ch)[0] in "LNZ" or ch in SEPARATORS:
        return False
    return ch not in KEY_GLYPHS


#: X6, completeness only: the tones that paint OVER a member's glyph without
#: being that member's tone -- the selection on the canvas (`V23`), the
#: selection with the focus elsewhere (`V24`), and the rail's cursor row, which
#: paints `INK on STEP`.  Read from the declaration where a member owns the
#: style; the cursor's is the one written here.
OVERLAY_STYLES = frozenset(
    {style for vid, _g, _l, style in darkside.DECLARED_VOCABULARY if vid in ("V23", "V24")}
    | {"INK on STEP"}
)


def _excluded_widget(widget, y: int) -> bool:
    """X3 and X5, decided by the widget painted under the cell."""
    node = widget
    while node is not None:
        if type(node).__name__ in CHROME_WIDGETS or node.id in CHROME_WIDGETS:
            return True
        if isinstance(node, DataTable) and node.show_header and y == node.region.y:
            return True
        node = node.parent
    return False


def glyph_set(vid: str, sample: str) -> frozenset[str]:
    """The painted characters a member stands for: the meaningful characters of
    its sample, plus every code point of its declared ranges.  A sample with
    none stands for its own characters -- `V21b`'s `·` is a punctuation code
    point the rail uses as a mark -- and a sample that is only a numeral
    (`V35`'s rail count) stands for any numeral."""
    chars = {c for c in sample if meaningful(c)}
    for lo, hi in darkside.DECLARED_GLYPH_RANGES.get(vid, ()):
        chars |= {chr(cp) for cp in range(lo, hi + 1)}
    if not chars:
        stripped = sample.strip()
        chars = set(string.digits) if stripped.isdigit() else set(stripped) - {" "}
    return frozenset(chars)


def _hex(color) -> str | None:
    return None if color is None else color.get_truecolor().hex


def _paints_as(style: Style | None, declared: str) -> bool:
    """Same comparison the legend-side arm uses: fg, bold, and bg if declared."""
    want = Style.parse(darkside.resolve_style(declared))
    style = style or Style()
    if _hex(style.color) != _hex(want.color) or bool(style.bold) != bool(want.bold):
        return False
    return want.bgcolor is None or _hex(style.bgcolor) == _hex(want.bgcolor)


def harvest(screen) -> set[tuple[str, Style | None]]:
    """(character, style) of every non-space cell of the composited frame that
    the exclusion rule's X3/X5 leave to the view.  `x` advances by each
    character's CELL width (`INC8-F-CR-F6`): per character, a wide glyph put
    every later cell of its row under the wrong widget."""
    out: set[tuple[str, Style | None]] = set()
    for y, strip in enumerate(screen._compositor.render_strips()):  # noqa: SLF001
        x = 0
        for seg in strip:
            for ch in seg.text:
                if not ch.isspace():
                    widget, _ = screen.get_widget_at(x, y)
                    if not _excluded_widget(widget, y):
                        out.add((ch, seg.style))
                x += cell_len(ch)
    return out


# ---------------------------------------------------------------------------
# Fixtures and states: the ONE table both this arm and the catalogue
# instrument drive (`INC8-F-CR-F6`: the catalogue imports `SIZES`,
# `MAP_STATES`, `drive_map`, `drive_home` and the exclusion rule from here).

SCHEMA = [SchemaField(key="D", label="documento", required=True),
          SchemaField(key="O", label="dueno", required=True)]
BRANCHES = ["finanzas", "rrhh", "inventarios", "ventas", "compras", "logistica",
            "juridico", "ti"]


def legacy_map() -> Graph:
    """8 branches x 5 leaves.  Every third branch is complete, the others
    carry fewer actas, one leaf is due today -- so the card chips, the schema
    letters, the rail counts and every coverage glyph are all exercised."""
    g = Graph()
    g.schema = list(SCHEMA)
    g.add_node(Node(id="root", ficha=Ficha(title="erp legacy", fields={"D": "ACTA-1", "O": "ana"})))
    for bi, b in enumerate(BRANCHES):
        g.add_node(Node(id=b, ficha=Ficha(title=b, fields={"D": "a", "O": "x"})))
        g.add_edge(Edge("root", b))
        for i in range(5):
            fields = {"D": f"A-{i}", "O": "x"} if (bi % 3 == 0 or i < bi % 3) else {}
            if bi == 1 and i == 0:
                fields["due"] = date.today().isoformat()
            g.add_node(Node(id=f"{b}{i}", ficha=Ficha(title=f"{b[:4]} {i}", fields=fields)))
            g.add_edge(Edge(b, f"{b}{i}"))
    return g


def concept_map() -> Graph:
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="plataforma", meta="core")))
    for b in BRANCHES[:6]:
        g.add_node(Node(id=b, ficha=Ficha(title=b, meta="area")))
        g.add_edge(Edge("root", b))
        for i in range(3):
            g.add_node(Node(id=f"{b}{i}", ficha=Ficha(title=f"{b[:4]} {i}", meta="mod")))
            g.add_edge(Edge(b, f"{b}{i}"))
    return g


#: `INC8-F-UX-F4`: one chain this deep.  The outline indents two cells a
#: level until the indent would pass half its render width, then paints the
#: TRUE level as `⇲N` (`views/outline.py:_indent`, row `V45`).  26 levels
#: reach past that point at both `SIZES`; the D2 arm's soundness half fails
#: at a size where no `⇲` is painted, so "deep enough" is asserted, not hoped.
DEEP_LEVELS = 26


def deep_map() -> Graph:
    g = Graph()
    g.schema = list(SCHEMA)
    g.add_node(Node(id="n0", ficha=Ficha(title="raiz", fields={"D": "a", "O": "x"})))
    for d in range(1, DEEP_LEVELS + 1):
        g.add_node(Node(id=f"n{d}", ficha=Ficha(title=f"nivel {d}", fields={"D": "a", "O": "x"})))
        g.add_edge(Edge(f"n{d - 1}", f"n{d}"))
    return g


CYCLE_MMD = "graph TD\n    a[A] --> b[B]\n    b --> a\n"

#: Both sizes the catalogue measures at.
SIZES = ((118, 34), (140, 45))

#: The walks every map view is driven through, on both fixtures, each in a
#: FRESH app so no state leaks into the next: rest, a walk, a fold (the
#: rail's `▸` and lattice show only when a folded branch is not selected or
#: the rail is short), a search, the focus on the rail (the unfocused
#: selection), and the folded root.
_WALKS = (
    ("rest", ()), ("walked", ("l", "j", "l")), ("folded", ("l", "z")),
    ("folded-walk", ("l", "z", "j")), ("search", ("slash", "f", "i", "n", "enter")),
    ("rail-focus", ("g",)), ("unfocused-selection", ("l", "g")), ("folded-root", ("z",)),
)
_ON_BOTH = [(factory, f"{factory.__name__}-{label}", keys)
            for factory in (legacy_map, concept_map) for label, keys in _WALKS]

HOME_VIEW = darkside.VIEW_NAMES["home"]
#: view -> (the keys that switch the map to it, [(fixture, label, keys)]).
MAP_STATES = {
    darkside.VIEW_NAMES["canvas"]: ((), _ON_BOTH),
    darkside.VIEW_NAMES["outline"]: (("o",), [*_ON_BOTH, (deep_map, "deep_map-rest", ())]),
    darkside.VIEW_NAMES["radial"]: (("r",), _ON_BOTH),
}


async def _settle(pilot, n: int = 3) -> None:
    # A pushed screen fades in; a frame read mid-fade carries interpolated
    # tones the product never declares (the catalogue measured `#b8b8b8`).
    await pilot.wait_for_scheduled_animations()
    for _ in range(n):
        await pilot.pause()


async def drive_map(work, view: str, size, factory, keys, read):
    """One state of one map view, in a fresh app: `read(screen)`'s result."""
    view_keys, _states = MAP_STATES[view]
    app = MapperApp(work)
    async with app.run_test(size=size) as pilot:
        app.store.save("mapa", factory())
        app.push_screen(MapScreen("mapa"))
        await _settle(pilot)
        for key in (*view_keys, *keys):
            await pilot.press(key)
            await _settle(pilot, 2)
        # The trigger is asserted, not assumed: the frame is that view's.
        assert isinstance(app.screen, MapScreen) and app.screen.legend_view == view
        return read(app.screen)


async def drive_home(work, size, read):
    app = MapperApp(work)
    async with app.run_test(size=size) as pilot:
        app.store.save("legado", legacy_map())
        app.store.save("plataforma", concept_map())
        (app.store.workspace / "roto.mmd").write_text(CYCLE_MMD, encoding="utf-8")
        app.store.record_session("legado", "rrhh0")
        app.notify = lambda *a, **k: None
        app.push_screen(HomeScreen())
        await _settle(pilot, 4)
        assert isinstance(app.screen, HomeScreen) and app.screen.legend_view == HOME_VIEW
        return read(app.screen)


#: One harvest per (view, size) per session: the colour arm reads the frames
#: the D2 arm already drove instead of driving them a second time.
_PAINTED: dict[tuple[str, tuple[int, int]], set] = {}


async def painted_by(view: str, size, work) -> set:
    if (view, size) not in _PAINTED:
        if view == HOME_VIEW:
            painted = await drive_home(work / "home", size, harvest)
        else:
            assert view in MAP_STATES, f"{view!r} is declared but no state drives it"
            painted = set()
            for factory, label, keys in MAP_STATES[view][1]:
                painted |= await drive_map(work / label, view, size, factory, keys, harvest)
        _PAINTED[(view, size)] = painted
    return _PAINTED[(view, size)]


def _explained(members, ch: str, style) -> bool:
    """COMPLETENESS per (glyph, style) (`INC8-F-CR-F4`): a member of this view
    owns the glyph AND paints it in this tone, or X6 -- the tone is an
    overlay painting over a glyph some member owns."""
    owners = [m for m in members if ch in glyph_set(m[0], m[1])]
    return any(_paints_as(style, m[3]) for m in owners) or (
        bool(owners) and any(_paints_as(style, o) for o in OVERLAY_STYLES))


def _paint(style) -> tuple:
    style = style or Style()
    return (_hex(style.color), _hex(style.bgcolor), bool(style.bold))


def _agreement(view: str, painted: set) -> tuple[list, list]:
    members = vocabulary_for(view)
    assert members, f"{view} explains nothing; this arm would pass vacuously"
    unpainted = [
        (vid, sample, style) for vid, sample, _label, style in members
        if not any(ch in glyph_set(vid, sample) and _paints_as(st, style) for ch, st in painted)
    ]
    undeclared = sorted({
        (ch, f"U+{ord(ch):04X}", *_paint(st)) for ch, st in painted
        if meaningful(ch) and not _explained(members, ch, st)
    }, key=str)
    return unpainted, undeclared


@pytest.mark.parametrize("size", SIZES, ids=lambda s: f"{s[0]}x{s[1]}")
@pytest.mark.parametrize("view", sorted(darkside.LEGEND_VIEWS))
async def test_d2_the_legend_and_the_view_agree_in_both_directions(tmp_path, view, size):
    """`INC8-F2` / `UX-F3`, closed: what the legend explains is what the view
    paints, in the declared style, and nothing meaningful the view paints is
    left out of the view's legend -- per (glyph, style), over every state the
    catalogue drives, at both of its sizes.  Parametrized on the declaration
    itself (`INC8-F-CR-F5`), so a view added there is driven here or fails."""
    painted = await painted_by(view, size, tmp_path)
    unpainted, undeclared = _agreement(view, painted)
    assert not unpainted and not undeclared, (
        f"{view}: SOUNDNESS -- declared but not painted in its declared style: {unpainted}\n"
        f"{view}: COMPLETENESS -- painted (glyph, code point, fg, bg, bold) in no member "
        f"or overlay of this view: {undeclared}"
    )


def has_a_job(hex_value: str | None) -> bool:
    """The colour section's exclusion rule (verdict `E4`), written ONCE: a
    painted colour has a job when it is a HUE.  A grey -- `r == g == b`, the
    surfaces and the text ramp -- carries no meaning a colour row explains."""
    return bool(hex_value) and len({hex_value[1:3], hex_value[3:5], hex_value[5:7]}) > 1


async def test_e4_the_colour_rows_are_the_hues_the_views_paint(tmp_path):
    """Verdict `E4`: `01b` §3.5 derived from what is painted, both directions.
    Every declared colour is a hue some view paints (fg or bg, outside the
    app chrome); every hue a view paints is a declared colour.  Read over the
    same frames as the D2 arm, at the declared context of use (`SIZES[0]`)."""
    painted: set = set()
    for view in sorted(darkside.LEGEND_VIEWS):
        painted |= await painted_by(view, SIZES[0], tmp_path / view.replace(" ", "-"))
    hues = {c for _ch, st in painted for c in _paint(st)[:2] if has_a_job(c)}
    names = {v.lower(): n for n, v in darkside.tokens().items()}
    declared = {darkside.tokens()[tok].lower() for _s, _l, tok in darkside.DECLARED_COLOURS}
    assert declared and all(has_a_job(h) for h in declared), declared
    assert hues == declared, (
        f"painted hues with no colour row: {sorted((h, names.get(h)) for h in hues - declared)}\n"
        f"colour rows no view paints: {sorted((h, names.get(h)) for h in declared - hues)}"
    )


# ---------------------------------------------------------------------------
# D4 -- a side panel at >= 118 columns, the modal below.

def _cells(screen, x_end: int) -> list[list[tuple]]:
    """(character, fg, bg, bold) of every cell of the composited frame left of
    `x_end` -- what the operator sees.  Not the `Style` object: two equal
    paints compare unequal as objects once they cross a compositor.  A space
    has no visible foreground, so its fg is dropped (measured: the modal
    compositor gives 109 blank cells an `INK` fg they did not carry)."""
    rows = []
    for strip in screen._compositor.render_strips():  # noqa: SLF001
        row: list[tuple] = []
        for seg in strip:
            st = seg.style or Style()
            fg = None if seg.text.isspace() else _hex(st.color)
            row.extend((ch, None if ch == " " else fg, _hex(st.bgcolor), bool(st.bold))
                       for ch in seg.text)
        rows.append(row[:x_end])
    return rows


async def _open_legend_over_map(app, pilot):
    app.store.save("mapa", legacy_map())
    app.push_screen(MapScreen("mapa"))
    await _settle(pilot)
    view = app.screen
    await pilot.press("question_mark")
    await _settle(pilot)
    assert isinstance(app.screen, HelpScreen)
    return view, app.screen


@pytest.mark.parametrize("width", [LEGEND_DOCK_MIN_WIDTH - 1, LEGEND_DOCK_MIN_WIDTH, 140])
async def test_d4_the_layout_switches_at_118_columns(tmp_path, width):
    """Docked top-right at `LEGEND_DOCK_MIN_WIDTH` and wider; the centred
    modal one column below it.  Both keep the height `TC-R36` governs."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        _view, legend = await _open_legend_over_map(app, pilot)
        dialog = legend.query_one("#help-dialog").region
        docked = width >= LEGEND_DOCK_MIN_WIDTH
        assert legend.has_class(DOCKED_CLASS) is docked
        assert dialog.width == LEGEND_PANEL_CELLS and dialog.height <= 28, dialog
        if docked:
            assert (dialog.x, dialog.right, dialog.y) == (width - LEGEND_PANEL_CELLS, width, 0), dialog
        else:
            assert abs(dialog.x - (width - dialog.right)) <= 1, f"not centred: {dialog}"
            assert dialog.y > 0, f"not centred vertically: {dialog}"


@pytest.mark.parametrize("width", [LEGEND_DOCK_MIN_WIDTH - 1, LEGEND_DOCK_MIN_WIDTH])
async def test_d4_the_view_stays_visible_and_undimmed_beside_the_docked_panel(tmp_path, width):
    """At >= 118 every cell left of the panel is the view's own cell, glyph
    AND style -- nothing covers it and nothing dims it.  One column narrower
    the modal's backdrop dims the view: the same comparison must differ there,
    which is what shows this arm can see a covered view at all."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        app.store.save("mapa", legacy_map())
        app.push_screen(MapScreen("mapa"))
        await _settle(pilot)
        panel_x = width - LEGEND_PANEL_CELLS
        before = _cells(app.screen, panel_x)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert isinstance(app.screen, HelpScreen)
        after = _cells(app.screen, panel_x)
    assert any(cell[0].strip() for row in before for cell in row), "the view painted nothing"
    same = after == before
    assert same is (width >= LEGEND_DOCK_MIN_WIDTH), (
        f"width {width}: cells left of x={panel_x} unchanged = {same}")


async def test_d4_the_docked_panel_paints_nothing_over_the_visible_view(tmp_path):
    """No widget of the legend reaches left of the panel's edge: the panel and
    the part of the view left visible do not overlap.

    WHAT THIS DOES NOT CLAIM, and the record says so: the view is not
    reflowed, so at 118 columns the 80-column panel still covers the right of
    the map screen -- the canvas from column 38 on and the ficha inspector.
    That is `INC8-D-Q4`, measured in `increment-022`, for the operator."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(LEGEND_DOCK_MIN_WIDTH, 34)) as pilot:
        _view, legend = await _open_legend_over_map(app, pilot)
        panel_x = LEGEND_DOCK_MIN_WIDTH - LEGEND_PANEL_CELLS
        regions = [w.region for w in legend.query("*") if w.region.width]
    assert regions, "the legend laid out nothing"
    left = [r for r in regions if r.x < panel_x]
    assert not left, f"legend widgets left of x={panel_x}: {left}"


async def test_d4_the_docked_panel_is_modal_for_keys(tmp_path):
    """DECIDED: keys never reach the view while the legend is open, docked or
    not.  A map key does nothing, a second `?` stacks nothing (`HLR-N16.3`),
    `esc` and `q` close it.  The same map key, pressed once the legend is
    closed, DOES move the view -- the trigger the arm depends on, asserted."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(LEGEND_DOCK_MIN_WIDTH, 34)) as pilot:
        view, legend = await _open_legend_over_map(app, pilot)
        assert legend.has_class(DOCKED_CLASS)
        state = (view.nav.cursor, view.outline_mode, view.radial_mode, frozenset(view.folded))
        depth = len(app.screen_stack)
        for key in ("l", "o", "r", "z", "question_mark"):
            await pilot.press(key)
            await pilot.pause()
            assert app.screen is legend, f"{key!r} closed or covered the legend"
            assert len(app.screen_stack) == depth, f"{key!r} stacked a screen"
        assert (view.nav.cursor, view.outline_mode, view.radial_mode,
                frozenset(view.folded)) == state, "a key reached the view"
        await pilot.press("escape")
        await pilot.pause()
        assert app.screen is view, "esc did not close the docked legend"
        await pilot.press("l")
        await _settle(pilot, 1)
        assert view.nav.cursor != state[0], "the trigger key does nothing on the bare view"
        await pilot.press("question_mark")
        await _settle(pilot)
        assert isinstance(app.screen, HelpScreen)
        await pilot.press("q")
        await pilot.pause()
        assert app.screen is view, "q did not close the docked legend"


@pytest.mark.parametrize("width", [100, LEGEND_DOCK_MIN_WIDTH - 1, LEGEND_DOCK_MIN_WIDTH, 140])
async def test_d4_the_row_budget_is_the_painted_pane_width_in_both_layouts(tmp_path, width):
    """`INC8-CR-F2`, in both layouts: the budget is derived from the one panel
    width, and the pane really is that wide, modal or docked."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        _view, legend = await _open_legend_over_map(app, pilot)
        pane = legend.query_one("#help-bindings")
        assert pane.scrollable_content_region.width == LEGEND_ROW_CELLS
    assert LEGEND_ROW_CELLS == LEGEND_PANEL_CELLS - 5


async def test_d4_a_resize_moves_the_open_legend_between_layouts(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 34)) as pilot:
        _view, legend = await _open_legend_over_map(app, pilot)
        assert legend.has_class(DOCKED_CLASS)
        await pilot.resize_terminal(100, 34)
        await _settle(pilot)
        assert not legend.has_class(DOCKED_CLASS)
        await pilot.resize_terminal(LEGEND_DOCK_MIN_WIDTH, 34)
        await _settle(pilot)
        assert legend.has_class(DOCKED_CLASS)


def test_d2_the_exclusion_rule_keeps_the_forms_the_catalogue_kept():
    """The rule's own arm: it must not exclude a glyph a member depends on.
    A rule that dropped `▸` or braille would make completeness vacuous for
    exactly the forms the operator asked about."""
    # `INC8-F-CR-F2`: `•` and `‹` are punctuation code points a renderer
    # could start using as marks; X2 excuses only the named separators.
    for ch in "▐▸◫✓░▰▱▽◆▾∙█▒╱▲⊘▁●↩⠀⣿⇲•‹":
        assert meaningful(ch), f"U+{ord(ch):04X} is excluded by the rule"
    for ch in "a3 ·…—/%+":
        assert not meaningful(ch), f"{ch!r} should be text or punctuation"
    assert not meaningful("↵"), "a key glyph is explained by the key section"
