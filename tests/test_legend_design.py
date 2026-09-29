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
    ADJACENT_ROWS,
    DOCKED_CLASS,
    LEGEND_DOCK_MIN_VIEW_CELLS,
    LEGEND_DOCKED_CELLS,
    LEGEND_DOCKED_ROW_CELLS,
    LEGEND_MODAL_MAX_ROWS,
    LEGEND_PANEL_CELLS,
    LEGEND_ROW_CELLS,
    HelpScreen,
    vocabulary_for,
)
from mapper.views.layered import _geometry as layered_geometry
from mapper.widgets.rail import RAIL_WIDTH

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
    """The VIEW-side comparison: fg and bold as declared, and the ground only
    when the member declares one -- a bare member is matched on any ground
    here, and the D2 arm checks separately that its view paints it on
    `GROUND` somewhere (`INC8-P2-UX-F6`).  NOT the legend-side arm's
    comparison (`tests/test_help_scope.py::_paints_as`), which requires the
    declared ground or, for a bare member, `GROUND` itself (verdict `E2`)."""
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


def adjacent_pairs(screen) -> set[tuple[str, Style | None, str, Style | None]]:
    """Verdict `Q7`: (letter, style, next glyph, style) for every LETTER the
    view paints immediately before a meaningful glyph, outside X3/X5 -- the
    form `V27`/`V28` name (a schema letter and its mark).  X1 keeps letters
    out of `harvest`'s per-cell rule, so this is the targeted sight of the
    letter's style; X1 itself is not widened."""
    out: set[tuple[str, Style | None, str, Style | None]] = set()
    for y, strip in enumerate(screen._compositor.render_strips()):  # noqa: SLF001
        cells, x = [], 0
        for seg in strip:
            for ch in seg.text:
                cells.append((x, ch, seg.style))
                x += cell_len(ch)
        for (x, a, sa), (_x, b, sb) in zip(cells, cells[1:]):
            if unicodedata.category(a)[0] == "L" and meaningful(b):
                widget, _ = screen.get_widget_at(x, y)
                if not _excluded_widget(widget, y):
                    out.add((a, sa, b, sb))
    return out


def _read_view(screen) -> tuple[set, set]:
    return harvest(screen), adjacent_pairs(screen)


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
#: `INC8-D3-F1`: the selection on a node missing its record (`rrhh1`, the
#: legacy fixture's second `rrhh` leaf).  No state above selected one, so the
#: inspector's `<field>  requerido` in `ALERT` -- painted by EVERY map view --
#: was never seen, and the census read red as the atlas's alone.  Legacy
#: only: the concept fixture has no schema, so nothing is required there.
_MISSING_RECORD = (legacy_map, "legacy_map-missing-record", ("l", "j", "l", "j"))

HOME_VIEW = darkside.VIEW_NAMES["home"]
#: view -> (the keys that switch the map to it, [(fixture, label, keys)]).
MAP_STATES = {
    darkside.VIEW_NAMES["canvas"]: ((), [*_ON_BOTH, _MISSING_RECORD]),
    darkside.VIEW_NAMES["outline"]: (("o",), [*_ON_BOTH, _MISSING_RECORD,
                                              (deep_map, "deep_map-rest", ())]),
    darkside.VIEW_NAMES["radial"]: (("r",), [*_ON_BOTH, _MISSING_RECORD]),
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
#: the D2 arm already drove instead of driving them a second time.  Run alone,
#: each arm node drives its own (view, size) once -- one view's states, never
#: the four (`INC8-P2-CR-F3`).
_PAINTED: dict[tuple[str, tuple[int, int]], set] = {}
_PAIRS: dict[tuple[str, tuple[int, int]], set] = {}


async def painted_by(view: str, size, work) -> set:
    if (view, size) not in _PAINTED:
        painted: set = set()
        pairs: set = set()
        if view == HOME_VIEW:
            painted, pairs = await drive_home(work / "home", size, _read_view)
        else:
            assert view in MAP_STATES, f"{view!r} is declared but no state drives it"
            for factory, label, keys in MAP_STATES[view][1]:
                cells, adjacent = await drive_map(work / label, view, size, factory, keys,
                                                  _read_view)
                painted |= cells
                pairs |= adjacent
        _PAINTED[(view, size)] = painted
        _PAIRS[(view, size)] = pairs
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


def _on_ground(style) -> bool:
    bg = _hex((style or Style()).bgcolor)
    return bg is None or bg == darkside.GROUND


def _agreement(view: str, painted: set, pairs: set) -> tuple[list, list]:
    members = vocabulary_for(view)
    assert members, f"{view} explains nothing; this arm would pass vacuously"
    unpainted = [
        (vid, sample, style) for vid, sample, _label, style in members
        if not any(ch in glyph_set(vid, sample) and _paints_as(st, style) for ch, st in painted)
    ]
    # `INC8-P2-UX-F6`: a member that declares no ground is sampled on
    # `GROUND`, so its view must paint it on `GROUND` somewhere.  One painted
    # only on a card or a pill declares that ground instead.
    unpainted += [
        (vid, sample, f"{style} (on GROUND)") for vid, sample, _label, style in members
        if " on " not in f" {style} " and not any(
            ch in glyph_set(vid, sample) and _paints_as(st, style) and _on_ground(st)
            for ch, st in painted)
    ]
    # `Q7`: a row the legend paints as ADJACENT samples is painted by its view
    # as that pair of cells, each in its member's style.
    for vid in sorted(ADJACENT_ROWS & {m[0] for m in members}):
        first, second = [m for m in members if m[0] == vid]
        if not any(a == first[1] and _paints_as(sa, first[3])
                   and b == second[1] and _paints_as(sb, second[3])
                   for a, sa, b, sb in pairs):
            unpainted.append((vid, first[1] + second[1], f"{first[3]} + {second[3]} (adjacent)"))
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
    unpainted, undeclared = _agreement(view, painted, _PAIRS[(view, size)])
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


def colour_jobs(painted) -> set[tuple[str, str]]:
    """Verdict `F1`'s census rule, written ONCE: `(hue, kind)` for every hue
    with a job a view paints.  A hue in the foreground of a LETTER is painted
    on `words` (the count's `sin acta`, the inspector's `requerido`); any
    other foreground -- a glyph, a numeral -- and every background fill is
    painted on `marks`."""
    out: set[tuple[str, str]] = set()
    for ch, st in painted:
        fg, bg, _bold = _paint(st)
        if has_a_job(fg):
            out.add((fg, "words" if unicodedata.category(ch)[0] == "L" else "marks"))
        if has_a_job(bg):
            out.add((bg, "marks"))
    return out


@pytest.mark.parametrize("size", SIZES, ids=lambda s: f"{s[0]}x{s[1]}")
@pytest.mark.parametrize("view", sorted(darkside.LEGEND_VIEWS))
async def test_f1_each_legend_paints_the_colour_rows_its_view_paints(tmp_path, view, size):
    """Verdict `F1` (was `E4`, over the union of the views): PER VIEW, both
    directions.  A row is painted by this view when the view paints its hue
    on what §3.5's `Painted on` cell names; the view's declared rows are
    exactly those, and every (hue, kind) the view paints has a declared row.
    Read over the same frames as the D2 arm (`painted_by`, one drive per
    view and size), so it costs one view's states when run alone
    (`INC8-P2-CR-F3`)."""
    from tests.test_vocabulary_declaration import colour_rows

    rows = [(rid, darkside.tokens()[tok].lower(), on) for rid, _s, _l, tok, _h, on, _v
            in colour_rows()]
    assert all(has_a_job(h) for _rid, h, _on in rows), rows
    jobs = colour_jobs(await painted_by(view, size, tmp_path))
    declared = set(darkside.LEGEND_COLOURS.get(view, ()))
    painted_rows = {rid for rid, h, on in rows if any(j[0] == h and j[1] in on for j in jobs)}
    unexplained = sorted(j for j in jobs if not any(
        rid in declared and j[0] == h and j[1] in on for rid, h, on in rows))
    names = {v.lower(): n for n, v in darkside.tokens().items()}
    assert painted_rows == declared and not unexplained, (
        f"{view}: rows painted {sorted(painted_rows)}, declared {sorted(declared)}; "
        f"painted with no declared row: {[(names.get(h, h), k) for h, k in unexplained]}"
    )


# ---------------------------------------------------------------------------
# D4 / F9 -- a side panel while the view keeps its minimum beside it, the
# modal below.

#: `F9`'s switch widths, DERIVED here from the panel and the minimum rather
#: than read back from the product's `docks`.  A map opened narrower than the
#: reference width has its rail auto-hidden, so its view starts at column 0;
#: one opened at the reference width keeps its rail through a resize.
DOCK_WIDTH_BARE = LEGEND_DOCKED_CELLS + LEGEND_DOCK_MIN_VIEW_CELLS
DOCK_WIDTH_WITH_RAIL = DOCK_WIDTH_BARE + RAIL_WIDTH
REFERENCE_SIZE = (darkside.DECLARED_CONTEXT_CELLS, 34)

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


@pytest.mark.parametrize("width", [DOCK_WIDTH_BARE - 1, DOCK_WIDTH_BARE, 140])
async def test_d4_the_layout_switches_at_the_derived_width(tmp_path, width):
    """Docked at the derived width and wider (`F9`) -- verdict `E1`: the
    narrow panel, flush right, full height (`A-107`); the centred modal one
    column below it, under `TC-R36`'s cap."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        _view, legend = await _open_legend_over_map(app, pilot)
        dialog = legend.query_one("#help-dialog").region
        docked = width >= DOCK_WIDTH_BARE
        assert legend.has_class(DOCKED_CLASS) is docked
        if docked:
            assert (dialog.x, dialog.right, dialog.y, dialog.height) == (
                width - LEGEND_DOCKED_CELLS, width, 0, 34), dialog
        else:
            assert dialog.width == LEGEND_PANEL_CELLS, dialog
            assert dialog.height <= LEGEND_MODAL_MAX_ROWS, dialog
            assert abs(dialog.x - (width - dialog.right)) <= 1, f"not centred: {dialog}"
            assert dialog.y > 0, f"not centred vertically: {dialog}"


@pytest.mark.parametrize("screen,opened_at,width", [
    ("home", DOCK_WIDTH_BARE - 1, DOCK_WIDTH_BARE - 1),
    ("home", DOCK_WIDTH_BARE, DOCK_WIDTH_BARE),
    ("map", DOCK_WIDTH_BARE - 1, DOCK_WIDTH_BARE - 1),
    ("map", DOCK_WIDTH_BARE, DOCK_WIDTH_BARE),
    ("map", REFERENCE_SIZE[0], DOCK_WIDTH_WITH_RAIL - 1),
    ("map", REFERENCE_SIZE[0], DOCK_WIDTH_WITH_RAIL),
], ids=["home-below", "home-at", "map-below", "map-at", "map-rail-below", "map-rail-at"])
async def test_f9_the_legend_docks_exactly_while_the_view_keeps_its_minimum(
    tmp_path, screen, opened_at, width,
):
    """Verdict `F9`: the dock threshold is derived from the view left visible
    beside the 44-column panel.  Measured on the frame: the view's first
    column is the canvas's own left edge (the rail, when shown, sits before
    it) or the screen's, and the columns between it and where the panel's
    edge falls must be at least `LEGEND_DOCK_MIN_VIEW_CELLS`.  Each case sits
    ON the boundary -- asserted, so a wrong derivation cannot pass by
    landing elsewhere -- and the map is also resized onto it, with its rail
    shown, so a resize across it is driven too."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(opened_at, 34)) as pilot:
        if screen == "home":
            app.push_screen(HomeScreen())
            await _settle(pilot)
            view_left = app.screen.region.x
        else:
            app.store.save("mapa", legacy_map())
            app.push_screen(MapScreen("mapa"))
            await _settle(pilot)
            if width != opened_at:
                await pilot.resize_terminal(width, 34)
                await _settle(pilot)
            view_left = app.screen.query_one("#map-canvas").region.x
        visible = width - LEGEND_DOCKED_CELLS - view_left
        await pilot.press("question_mark")
        await _settle(pilot)
        assert isinstance(app.screen, HelpScreen)
        docked = app.screen.has_class(DOCKED_CLASS)
    assert visible in (LEGEND_DOCK_MIN_VIEW_CELLS - 1, LEGEND_DOCK_MIN_VIEW_CELLS), (
        f"{screen} at {width}: {visible} columns; this case is not on the boundary")
    assert docked is (visible >= LEGEND_DOCK_MIN_VIEW_CELLS), (screen, width, visible, docked)


@pytest.mark.parametrize("width", [DOCK_WIDTH_BARE - 1, DOCK_WIDTH_BARE])
async def test_d4_the_view_stays_visible_and_undimmed_beside_the_docked_panel(tmp_path, width):
    """Docked, every cell left of the docked panel is the view's own cell,
    glyph AND style -- nothing covers it and nothing dims it.  One column
    narrower the modal's backdrop dims the view: the same comparison must
    differ there, which is what shows this arm can see a covered view at all."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        app.store.save("mapa", legacy_map())
        app.push_screen(MapScreen("mapa"))
        await _settle(pilot)
        panel_x = width - LEGEND_DOCKED_CELLS
        before = _cells(app.screen, panel_x)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert isinstance(app.screen, HelpScreen)
        after = _cells(app.screen, panel_x)
    assert any(cell[0].strip() for row in before for cell in row), "the view painted nothing"
    same = after == before
    assert same is (width >= DOCK_WIDTH_BARE), (
        f"width {width}: cells left of x={panel_x} unchanged = {same}")


async def test_d4_the_docked_panel_paints_nothing_over_the_visible_view(tmp_path):
    """No widget of the legend reaches left of the panel's edge: the panel and
    the part of the view left visible do not overlap.  The view is not
    reflowed; what the narrow panel still covers is measured in
    `test_e1_the_docked_panel_covers_the_inspector_whole_and_little_canvas`."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=REFERENCE_SIZE) as pilot:
        _view, legend = await _open_legend_over_map(app, pilot)
        panel_x = REFERENCE_SIZE[0] - LEGEND_DOCKED_CELLS
        regions = [w.region for w in legend.query("*") if w.region.width]
    assert regions, "the legend laid out nothing"
    left = [r for r in regions if r.x < panel_x]
    assert not left, f"legend widgets left of x={panel_x}: {left}"


@pytest.mark.parametrize("size", [REFERENCE_SIZE, (140, 45)])
async def test_e1_the_docked_panel_covers_the_inspector_whole_and_little_canvas(tmp_path, size):
    """Verdict `E1` / `UX-F9` / `INC8-F-UX-F1`.  The docked panel runs the full
    height, so the ficha inspector is covered WHOLE -- no "L" of it left
    below a capped panel -- and it is narrow, so most of the canvas stays
    beside it.

    `INC8-D2-F5`: the canvas bound was first written against
    `LEGEND_DOCKED_CELLS` itself, so widening the panel back to 80 (mutant
    `MA1`) moved the bound with it and every arm stayed green.  It is now read
    from the VERDICT's number -- "panel angosto de ~44 columnas" -- with the
    verdict's own tolerance of one column: the panel may take from the canvas
    at most that width less the inspector it covers."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        view, legend = await _open_legend_over_map(app, pilot)
        dialog = legend.query_one("#help-dialog").region
        inspector = view.query_one("#map-inspector").region
        canvas = view.query_one("#map-canvas").region
    assert inspector.width and canvas.width, (inspector, canvas)
    assert dialog.height == size[1], f"the docked panel is not full height: {dialog}"
    assert dialog.x <= inspector.x and dialog.right >= inspector.right, (dialog, inspector)
    assert dialog.y <= inspector.y and dialog.bottom >= inspector.bottom, (dialog, inspector)
    covered = max(0, canvas.right - dialog.x)
    assert covered <= VERDICT_E1_PANEL_CELLS + 1 - inspector.width, (covered, canvas, dialog)


#: Verdict `E1`, round 2: "panel angosto de ~44 columnas".  The REQUIREMENT's
#: number, held by the arm on purpose -- the product's `LEGEND_DOCKED_CELLS`
#: is the implementation, and an arm that reads the implementation back cannot
#: see it drift (`INC8-D2-F5`).
VERDICT_E1_PANEL_CELLS = 44


async def test_d4_the_docked_panel_is_modal_for_keys(tmp_path):
    """DECIDED: keys never reach the view while the legend is open, docked or
    not -- the view does NOT scroll under the docked legend (verdict `E1`).
    A map key does nothing, a second `?` stacks nothing (`HLR-N16.3`), `esc`
    and `q` close it.  The same map key, pressed once the legend is closed,
    DOES move the view -- the trigger the arm depends on, asserted."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=REFERENCE_SIZE) as pilot:
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


# ---------------------------------------------------------------------------
# F2 -- docking pans the view so the selection sits left of the panel; closing
# returns it.  Measured on the ux review's atlas walk: at the reference width
# `FINA_4` leaves 2 of the selected card's 8 cells visible beside the panel.

FINA_4 = ("l", "l", "l", "j", "j", "j", "j")
#: A width the legend is modal at, for a map opened at the reference width
#: (its rail stays shown on a resize).
MODAL_WIDTH_WITH_RAIL = DOCK_WIDTH_WITH_RAIL - 1


def _selection_cells(screen, canvas) -> list[tuple[int, int]]:
    """Cells of the composited frame inside the canvas region painted with the
    canvas selection's fill (`V23`, `ACCENT`) -- where the operator sees it."""
    accent = darkside.ACCENT.lower()
    return [(x, y) for y, row in enumerate(_cells(screen, canvas.right))
            for x, cell in enumerate(row)
            if cell[2] == accent and x >= canvas.x and canvas.y <= y < canvas.bottom]


def _canvas_chars(screen, canvas) -> list[str]:
    return ["".join(cell[0] for cell in row[canvas.x:canvas.right])
            for row in _cells(screen, canvas.right)[canvas.y:canvas.bottom]]


def _canvas_cells(screen, canvas) -> list[list[tuple]]:
    """Every painted cell of the canvas region -- character, fg, bg, bold --
    not just its characters (`_canvas_chars`).  `INC8-P3-CR-F1`: the pan a
    docked legend restores on close is not the only thing that must return;
    the selection's FILL must too, and a chars-only compare cannot see a
    fill that changed colour while the text underneath stayed put."""
    return [row[canvas.x:canvas.right]
            for row in _cells(screen, canvas.right)[canvas.y:canvas.bottom]]


async def _walked_map(app, pilot, keys):
    app.store.save("mapa", legacy_map())
    app.push_screen(MapScreen("mapa"))
    await _settle(pilot)
    for key in keys:
        await pilot.press(key)
        await _settle(pilot, 2)
    view = app.screen
    return view, view.query_one("#map-canvas").region


async def test_f2_docking_pans_a_covered_selection_clear_and_closing_returns_it(tmp_path):
    """Verdict `F2`, both halves, through the real keys.  The trigger is
    asserted: before `?` the docked panel's edge would cut the selected card.
    Docked, every cell of it sits left of the panel; the fold and the cursor
    are untouched (no key reached the view).  Closed, the pan is the prior
    pan and the canvas holds the same PAINTED CELLS it held before --
    character, foreground, background and bold, not just characters.  Before
    `INC8-P3-CR-F1` this arm skipped styles: `esc` moved the focus to the
    rail (`INC8-P2-UX-F7`) and the selection's fill followed it, from blue to
    grey, so a style compare would have RED-ed on the pre-existing carry
    rather than on this pass's own regression -- crediting this arm's find to
    a finding it did not test.  `INC8-P3-CR-F1` fixed the carry too (focus,
    including a docked repaint's, now returns exactly), so the skip is gone."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=REFERENCE_SIZE) as pilot:
        view, canvas = await _walked_map(app, pilot, FINA_4)
        panel_x = REFERENCE_SIZE[0] - LEGEND_DOCKED_CELLS
        before = _selection_cells(view, canvas)
        state = (view.pan_x, view.pan_y, view.nav.cursor, view.folded)
        cells = _canvas_cells(view, canvas)
        assert before and any(x >= panel_x for x, _y in before), (panel_x, before)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen.has_class(DOCKED_CLASS)
        docked = [c for c in _selection_cells(app.screen, canvas) if c[0] < panel_x]
        assert len(docked) == len(before), f"{len(docked)} of {len(before)} visible"
        assert (view.nav.cursor, view.folded) == state[2:], "a key reached the view"
        assert view.pan_x > state[0], "the view did not move"
        await pilot.press("escape")
        await _settle(pilot)
        assert app.screen is view
        assert (view.pan_x, view.pan_y, view.nav.cursor, view.folded) == state
        assert _canvas_cells(view, canvas) == cells


@pytest.mark.parametrize("size,keys", [
    (REFERENCE_SIZE, ("l", "l", "l", "j", "j", "j", "L")), ((140, 45), (*FINA_4, "L")),
], ids=["reference-panned", "140x45-fina-4-panned"])
async def test_f2_a_selection_clear_of_the_panel_does_not_move_the_view(tmp_path, size, keys):
    """Verdict `F2`: the view moves only when the panel covers the selection.
    A selected card already left of the panel's edge keeps the view where it
    was -- `FINA_4`'s card itself, at a width whose panel does not reach it.
    The operator has panned first (`L`), and that is asserted: from pan 0 a
    wrong shift to the LEFT clamps back to 0 and looks like "no move"
    (mutant `MP3` survived the first version of this arm that way).  The
    reference case's card ends 13 columns short of the panel's edge, so a
    check that fired "close to" the panel would move it."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        view, canvas = await _walked_map(app, pilot, keys)
        panel_x = size[0] - LEGEND_DOCKED_CELLS
        before = _selection_cells(view, canvas)
        pan = (view.pan_x, view.pan_y)
        assert pan[0] > 0, "the operator's pan did not move the view; the arm has no subject"
        assert before and all(x < panel_x for x, _y in before), (panel_x, before)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen.has_class(DOCKED_CLASS)
        assert (view.pan_x, view.pan_y) == pan


async def test_f2_the_modal_layout_does_not_pan_a_selection_a_dock_would_cover(tmp_path):
    """Verdict `F2` is about docking.  Opened MODAL, over a card a docked
    panel's edge WOULD cut at this width -- asserted, so the arm has a subject
    (mutant `MP4` survived the resize arm below, whose modal width had put
    the card past the canvas edge already) -- the view keeps its pan."""
    width = DOCK_WIDTH_BARE - 1
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        view, canvas = await _walked_map(app, pilot, FINA_4)
        would_be_edge = width - LEGEND_DOCKED_CELLS
        before = _selection_cells(view, canvas)
        pan = (view.pan_x, view.pan_y)
        assert before and any(x >= would_be_edge for x, _y in before), (would_be_edge, before)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert isinstance(app.screen, HelpScreen) and not app.screen.has_class(DOCKED_CLASS)
        assert (view.pan_x, view.pan_y) == pan


async def test_f2_the_modal_layout_does_not_pan_and_a_resize_re_derives_the_pan(tmp_path):
    """Verdict `F2` is about docking: in the modal layout the view keeps its
    pan.  Opened docked at the reference width the view pans; resized to the
    modal layout the prior pan returns; resized back it pans again, to the
    same place."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=REFERENCE_SIZE) as pilot:
        view, _canvas = await _walked_map(app, pilot, FINA_4)
        prior = (view.pan_x, view.pan_y)
        await pilot.press("question_mark")
        await _settle(pilot)
        legend = app.screen
        assert legend.has_class(DOCKED_CLASS) and view.pan_x > prior[0]
        docked_pan = (view.pan_x, view.pan_y)
        await pilot.resize_terminal(MODAL_WIDTH_WITH_RAIL, REFERENCE_SIZE[1])
        await _settle(pilot)
        assert not legend.has_class(DOCKED_CLASS)
        assert (view.pan_x, view.pan_y) == prior, "the modal layout panned the view"
        await pilot.resize_terminal(*REFERENCE_SIZE)
        await _settle(pilot)
        assert legend.has_class(DOCKED_CLASS)
        assert (view.pan_x, view.pan_y) == docked_pan


# ---------------------------------------------------------------------------
# `A-109`, Inc-8 design pass 4, verdict `G2`.  Amends `LLR-N06.1.2`: while the
# legend is docked, the reveal's legal pan range is computed on the VISIBLE
# canvas -- left of the panel -- not the canvas's own full drawn width, so a
# card at the map's own right edge (`INC8-D3-F2`'s carry) can be revealed
# whole instead of staying clamped to a range that assumed the panel was not
# there.

#: The legacy fixture's last leaf of its last branch (`BRANCHES[-1]`, `"ti"`,
#: leaf index 4) -- the map's own right edge, walked with the real keys: into
#: the first branch, seven siblings across to the last, into its first leaf,
#: four siblings down to the last.
TI_4 = ("l", "j", "j", "j", "j", "j", "j", "j", "l", "j", "j", "j", "j")


async def _panned_to_the_old_legal_max(pilot) -> None:
    """Press the real `L` past any fixture's legal range -- `HLR-N06.1`'s
    unwanted-behaviour clause makes every press beyond the clamp a documented
    no-op, so this cannot overshoot into a state `_clamp_pan` would not
    allow."""
    for _ in range(80):
        await pilot.press("L")
        await pilot.pause()


async def test_g2_a_card_at_the_maps_right_edge_is_revealed_whole_and_closing_returns_it(
    tmp_path,
):
    """`A-109`, verdict `G2`.  `ti4` sits at the map's own right edge: walked
    there and panned to the OLD range's legal maximum with the real `L`, its
    card is still cut by the panel once docked under the OLD clamp -- exactly
    the carry `INC8-D3-F2` described (measured before this fix: pan 421,
    card cut by 6 of its 9 columns).  Docked under the amended clamp, every
    cell of it sits left of the panel; closed, the pan is the EXACT pre-legend
    value the operator had at the edge, not a widened one left behind."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=REFERENCE_SIZE) as pilot:
        view, canvas = await _walked_map(app, pilot, TI_4)
        await _panned_to_the_old_legal_max(pilot)
        panel_x = REFERENCE_SIZE[0] - LEGEND_DOCKED_CELLS
        pre_pan = (view.pan_x, view.pan_y)
        before = _selection_cells(view, canvas)
        assert before and any(x >= panel_x for x, _y in before), (panel_x, before)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen.has_class(DOCKED_CLASS)
        # Filtered to `x < panel_x` as the F2 arm above does: an unfiltered
        # scan over the canvas region's own x-range also catches the docked
        # panel's OWN sample row for `V23` ("|> erp", painted ACCENT to
        # illustrate the style), which sits inside that same x-range once the
        # panel is docked.
        docked = [c for c in _selection_cells(app.screen, canvas) if c[0] < panel_x]
        assert len(docked) == len(before), f"{len(docked)} of {len(before)} visible"
        assert view.pan_x > pre_pan[0], "the amended clamp did not widen the range"
        await pilot.press("escape")
        await _settle(pilot)
        assert app.screen is view
        assert (view.pan_x, view.pan_y) == pre_pan, (
            "the closed pan is not the exact pre-legend value"
        )


async def test_g2_the_modal_layout_does_not_widen_the_range_for_an_edge_card(tmp_path):
    """`G2` amends the DOCKED reveal only.  Opened modal, one column below the
    derived threshold, over the same edge card panned to its legal maximum,
    the view keeps its pan: `legend_docked(None)` never calls
    `_pan_revealing_selection`, so the widened clamp never runs here."""
    width = DOCK_WIDTH_BARE - 1
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        view, _canvas = await _walked_map(app, pilot, TI_4)
        await _panned_to_the_old_legal_max(pilot)
        pan = (view.pan_x, view.pan_y)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert isinstance(app.screen, HelpScreen) and not app.screen.has_class(DOCKED_CLASS)
        assert (view.pan_x, view.pan_y) == pan


# ---------------------------------------------------------------------------
# `G5`: the revealed card keeps a declared `REVEAL_MARGIN_CELLS`-column margin
# from the panel's left edge, honoured whenever `G2`'s (possibly widened)
# legal range leaves room for it.

async def test_g5_the_revealed_card_keeps_its_declared_margin_from_the_panel(tmp_path):
    """`G5`: the revealed card ends `REVEAL_MARGIN_CELLS` columns short of the
    panel's left edge, not flush against it.  `FINA_4`'s card has pan room to
    spare at the reference width -- it is not the map's own right edge,
    `ti4` is (the `G2` arms above) -- so the margin is fully honoured rather
    than eaten by `LLR-N06.1.2`'s legal range.  Read from the SAME painted
    layout `_pan_revealing_selection` reads (`layered._geometry`), through
    the real `?` key rather than a direct call, so this is the product's own
    geometry, not a re-derivation of it."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=REFERENCE_SIZE) as pilot:
        view, canvas = await _walked_map(app, pilot, FINA_4)
        panel_x = REFERENCE_SIZE[0] - LEGEND_DOCKED_CELLS
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen.has_class(DOCKED_CLASS)
        _renderer, state = view._rendered_for
        geo = layered_geometry(view.graph, state)
        card_x, _card_y = geo.place(view.nav.cursor)
        right = canvas.x + card_x + geo.card_w
        assert panel_x - right == view.REVEAL_MARGIN_CELLS, (
            panel_x, right, view.REVEAL_MARGIN_CELLS
        )


# ---------------------------------------------------------------------------
# Pass-3 corrective: `INC8-P3-CR-F1` (blocking) / `INC8-P3-UX-F1`, carried
# `INC8-P2-UX-F7`.  Opening the legend must not move the keyboard's focus.
# `legend_docked` called `refresh_canvas` on every layout apply -- modal
# included -- which rebuilds the ficha inspector (`FichaInspector._rebuild`'s
# `remove_children`) and destroys a focused field; and even where nothing was
# destroyed, Textual's own post-resume auto-focus (`AUTO_FOCUS = "*"`) grabs
# the rail the moment this screen resumes with `focused` at `None`.  Closing
# the legend must restore the EXACT pre-legend focus, `None` included, and
# the canvas must not visibly repaint to show a different one -- checked on
# every painted cell (`_canvas_cells`), not just its characters.

INSPECTOR_FOCUS_ID = "insp-state"
#: `86x34`: one below `DOCK_WIDTH_BARE` (`87`), so the legend is modal and a
#: docked pan never fires -- the loss this pins is not about panning at all.
MODAL_SIZE = (DOCK_WIDTH_BARE - 1, 34)


@pytest.mark.parametrize("size,docked", [
    (REFERENCE_SIZE, True), (MODAL_SIZE, False),
], ids=["118x34-docked", "86x34-modal"])
async def test_cr_f1_closing_the_legend_restores_the_focused_field(tmp_path, size, docked):
    """Measured regression: `#insp-state` focused, `?` then `esc`, left focus
    on `map-rail` -- at BOTH widths, so the loss was never about the docked
    pan alone.  The canvas's own painted cells must also return unchanged: a
    repaint that only recolours the selection's fill would pass a
    characters-only compare and still be the bug."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        view, canvas = await _walked_map(app, pilot, FINA_4)
        field = view.query_one(f"#{INSPECTOR_FOCUS_ID}")
        view.set_focus(field)
        # `H4`'s sibling verdict `H2` (closing pass, round 5) made this
        # repaint itself: `MapScreen.on_descendant_focus` now redraws the
        # canvas on every focus change, so setup no longer needs the manual
        # `_declare_after_layout()` call this line used to carry -- and no
        # longer risks the defect it existed to dodge, since `set_focus`
        # itself is what now repaints.
        await _settle(pilot)
        assert view.focused is field
        cells = _canvas_cells(view, canvas)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen.has_class(DOCKED_CLASS) is docked
        await pilot.press("escape")
        await _settle(pilot)
        assert app.screen is view
        assert view.focused is not None and view.focused.id == INSPECTOR_FOCUS_ID
        assert _canvas_cells(view, canvas) == cells


@pytest.mark.parametrize("size,docked", [
    (REFERENCE_SIZE, True), (MODAL_SIZE, False),
], ids=["118x34-docked", "86x34-modal"])
async def test_cr_f1_closing_the_legend_with_no_prior_focus_stays_unfocused(tmp_path, size, docked):
    """`INC8-P3-UX-F1`, carried `INC8-P2-UX-F7`: with nothing focused before
    `?`, `esc` used to leave the rail focused -- `Screen._update_auto_focus`
    grabs the first focusable widget whenever this screen resumes with
    `focused is None`, regardless of whether a docked pan ever repainted
    anything.  The operator-facing requirement is exact: `None` returns
    `None`, and the selection's fill does not flash from blue to grey to
    show a focus the operator never asked for."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        view, canvas = await _walked_map(app, pilot, FINA_4)
        view.set_focus(None)
        await _settle(pilot)
        assert view.focused is None
        cells = _canvas_cells(view, canvas)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen.has_class(DOCKED_CLASS) is docked
        await pilot.press("escape")
        await _settle(pilot)
        assert app.screen is view
        assert view.focused is None
        assert _canvas_cells(view, canvas) == cells


async def test_cr_f2_reopening_after_a_pan_keeps_the_new_pan(tmp_path):
    """`INC8-P3-CR-F2`: closing the legend must clear `_pan_before_legend`,
    or a pan the operator makes AFTER closing is discarded the next time they
    open the legend -- the second `legend_docked` would find a STALE "kept"
    pan from the first open (`0`) and revert to it instead of re-deriving a
    reveal over the operator's own choice.  Walked through `FINA_4` at the
    reference width: open reveals (0,0)->(9,0) (`A-109`, `G5`: the reveal now
    leaves `REVEAL_MARGIN_CELLS` clear of the panel, 2 columns more than the
    flush target design pass 3 pinned here); close returns (9,0)->(0,0);
    three `L` presses are the operator's own pan, (0,0)->(24,0) -- past the
    reveal's OWN target, so a bug reusing the stale `0` would show a
    DIFFERENT, distinguishable number here, not the same one by coincidence.
    A second open must keep it exactly (the card is already clear, margin
    included), and a second close must not move it."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=REFERENCE_SIZE) as pilot:
        view, _canvas = await _walked_map(app, pilot, FINA_4)
        assert (view.pan_x, view.pan_y) == (0, 0)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert app.screen.has_class(DOCKED_CLASS)
        assert (view.pan_x, view.pan_y) == (9, 0)
        await pilot.press("escape")
        await _settle(pilot)
        assert (view.pan_x, view.pan_y) == (0, 0)
        await pilot.press("L")
        await pilot.press("L")
        await pilot.press("L")
        await _settle(pilot)
        assert (view.pan_x, view.pan_y) == (24, 0)
        await pilot.press("question_mark")
        await _settle(pilot)
        assert (view.pan_x, view.pan_y) == (24, 0)
        await pilot.press("escape")
        await _settle(pilot)
        assert (view.pan_x, view.pan_y) == (24, 0)


@pytest.mark.parametrize("width", [100, DOCK_WIDTH_BARE - 1, DOCK_WIDTH_BARE, 140])
async def test_d4_the_row_budget_is_the_painted_pane_width_in_both_layouts(tmp_path, width):
    """`INC8-CR-F2`, in both layouts (`E1`: two widths, each derived): the
    budget the rows are painted to is the pane's real usable width, modal or
    docked -- measured on the widget, never re-derived here."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        _view, legend = await _open_legend_over_map(app, pilot)
        pane = legend.query_one("#help-bindings")
        want = LEGEND_DOCKED_ROW_CELLS if width >= DOCK_WIDTH_BARE else LEGEND_ROW_CELLS
        assert legend.row_cells == want
        assert pane.scrollable_content_region.width == want


#: Round 3, the copy verdict: "12-cell sample column in the modal"; the docked
#: layout keeps design pass 2's eight.  The REQUIREMENT's numbers, held by
#: the arm on purpose, as `VERDICT_E1_PANEL_CELLS` is (`INC8-D2-F5`).
VERDICT_SAMPLE_CELLS = {"modal": 12, "docked": 8}


async def test_d4_a_resize_moves_the_open_legend_between_layouts(tmp_path):
    """A resize across the threshold moves the open legend AND repaints what
    it paints for the new layout.  Read off the COMPOSITED FRAME: the first
    vocabulary row's label starts after the indent and the layout's sample
    column (12 modal, 8 docked), so a legend that moved without repainting
    leaves the label at the OLD column.  (Until round 3 this read the title's
    close hint, which the title no longer paints.  Not the widget's
    `render()`: `tests/test_a3_census.py` pins every zero-arg `.render()`
    site.)"""
    app = MapperApp(tmp_path)
    label = vocabulary_for(darkside.VIEW_NAMES["canvas"])[0][2]

    def sample_column(legend) -> int:
        region = legend.query_one("#help-vocabulary").region
        rows = ["".join(seg.text for seg in strip)
                for strip in legend._compositor.render_strips()]  # noqa: SLF001
        row = next(r for r in rows[region.y:region.bottom] if label in r)
        return row.index(label) - region.x - 2

    async with app.run_test(size=(140, 34)) as pilot:
        _view, legend = await _open_legend_over_map(app, pilot)
        assert legend.has_class(DOCKED_CLASS)
        assert sample_column(legend) == VERDICT_SAMPLE_CELLS["docked"]
        await pilot.resize_terminal(DOCK_WIDTH_WITH_RAIL - 1, 34)
        await _settle(pilot)
        assert not legend.has_class(DOCKED_CLASS)
        assert sample_column(legend) == VERDICT_SAMPLE_CELLS["modal"]
        await pilot.resize_terminal(DOCK_WIDTH_WITH_RAIL, 34)
        await _settle(pilot)
        assert legend.has_class(DOCKED_CLASS)
        assert sample_column(legend) == VERDICT_SAMPLE_CELLS["docked"]


async def test_cr_f6_the_harvest_advances_by_cell_width():
    """`INC8-F-CR-F6`: `harvest` walks `x` by each character's CELL width.
    No view paints a wide glyph today, so the D2 arm alone could not tell;
    this frame can.  Two wide characters fill a 4-cell widget, and a `\u25b2`
    follows in a `HintLine` (X3, excluded).  Advancing per CHARACTER puts the
    `\u25b2` at x=2 -- inside the first widget -- and harvests chrome as view."""
    from textual.app import App
    from textual.containers import Horizontal
    from textual.widgets import Static

    class Frame(App):
        CSS = "Static { width: 4; height: 1; }"

        def compose(self):
            yield Horizontal(Static("\u6f22\u6f22", id="view"), Static("\u25b2", id="HintLine"))

    app = Frame()
    async with app.run_test(size=(20, 3)) as pilot:
        await pilot.pause()
        painted = {ch for ch, _st in harvest(app.screen)}
    assert "\u6f22" in painted, "the arm's own view cell was not harvested"
    assert "\u25b2" not in painted, "a chrome cell after a wide glyph was read as the view's"


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
