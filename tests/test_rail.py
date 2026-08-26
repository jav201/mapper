"""Acceptance tests for the rail, the region layout and the keybar (Inc-3)."""
from __future__ import annotations

from mapper import darkside
from mapper.app import MapperApp, MapScreen
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.widgets.chrome import HintLine, KeyBar
from mapper.widgets.inspector import FichaInspector
from mapper.widgets.rail import RAIL_WIDTH, OutlineRail

SCHEMA = [
    SchemaField(key="D", label="documento", required=True),
    SchemaField(key="O", label="dueño", required=True),
]


def _tree(app, map_id="rail"):
    """root -> (fin -> cont), rrhh.  `cont` and `rrhh` each miss one field."""
    g = Graph()
    g.schema = list(SCHEMA)
    g.add_node(Node(id="root", ficha=Ficha(title="erp", fields={"D": "a", "O": "b"})))
    g.add_node(Node(id="fin", ficha=Ficha(title="finanzas", fields={"D": "a", "O": "b"})))
    g.add_node(Node(id="cont", ficha=Ficha(title="contabilidad", fields={"D": "a"})))
    g.add_node(Node(id="rrhh", ficha=Ficha(title="rrhh", fields={"D": "a"})))
    g.add_edge(Edge("root", "fin"))
    g.add_edge(Edge("fin", "cont"))
    g.add_edge(Edge("root", "rrhh"))
    app.store.save(map_id, g)
    return map_id


async def _open(app, pilot, map_id):
    app.push_screen(MapScreen(map_id))
    # Two pauses: the screen parks focus after its first refresh, because the rail
    # and the inspector's fields are focusable and mount after `on_mount` runs.
    await pilot.pause()
    await pilot.pause()
    return app.screen


async def test_rail_lists_the_tree_and_counts_missing_per_branch(tmp_path):
    """The rail's per-branch count is the SUBTREE's, not the node's own.

    `fin` itself is complete; its child `cont` is missing one.  A count that only
    looked at the node would read 0 and hide the gap behind a collapsed branch —
    which is precisely what the count exists to prevent.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _tree(app))
        rail = screen.query_one("#map-rail", OutlineRail)

        assert [nid for nid, _ in rail.visible_rows()] == ["root", "fin", "cont", "rrhh"]
        assert rail.subtree_missing("cont") == 1
        assert rail.subtree_missing("fin") == 1, "the child's gap must surface on the parent"
        assert rail.subtree_missing("rrhh") == 1
        assert rail.subtree_missing("root") == 2, "the whole map's gaps"

        rendered = rail.render().plain
        for title in ("erp", "finanzas", "contabilidad", "rrhh"):
            assert title in rendered


async def test_rail_collapses_a_branch(tmp_path):
    """Collapsing hides descendants but keeps the branch's count visible."""
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _tree(app))
        rail = screen.query_one("#map-rail", OutlineRail)

        rail.toggle("fin")
        assert [nid for nid, _ in rail.visible_rows()] == ["root", "fin", "rrhh"]
        # The hidden child's gap is still counted on the collapsed parent.
        assert rail.subtree_missing("fin") == 1
        rail.toggle("fin")
        assert [nid for nid, _ in rail.visible_rows()] == ["root", "fin", "cont", "rrhh"]


async def test_at_n06a_rail_selection_marks_focus_and_the_hint_names_the_region(tmp_path):
    """AT-N06a — the live region is distinguishable, and named in words.

    Asserted on the rail only.  The canvas's selection block is drawn by a frozen
    renderer that cannot know where focus is, so a global "one ACCENT run"
    assertion would false-fail correct code (Amendment 3).

    RED mutation: make the rail's selected row use the focused style
    unconditionally; the unfocused-style assertion fails.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _tree(app))
        rail = screen.query_one("#map-rail", OutlineRail)

        def selected_styles() -> set[str]:
            """Every span on the rail whose style paints the interactivity blue."""
            return {
                str(span.style)
                for span in rail.render().spans
                if darkside.ACCENT in str(span.style)
            }

        assert not rail.has_focus
        assert selected_styles() == set(), "the rail paints ACCENT while it is not the live region"

        screen.action_focus_rail()
        await pilot.pause()
        assert rail.has_focus
        assert selected_styles(), "the rail must mark its selection once it holds focus"

        hint = screen.query_one(HintLine).render().plain
        assert "rail" in hint, "the hint line must name the region that holds focus"


async def test_at_n06d_regions_collapse_by_key_and_by_width(tmp_path):
    """AT-N06d — the rail and inspector can be hidden, and yield when it is narrow.

    Below the measured threshold the canvas clips a card's coverage row mid-field,
    making a present field indistinguishable from a clipped one.

    RED mutation: make `_apply_region_visibility` a no-op; both arms fail.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _tree(app))
        rail = screen.query_one("#map-rail", OutlineRail)
        inspector = screen.query_one("#map-inspector", FichaInspector)

        # Wide terminal: both regions are shown.
        assert rail.display and inspector.display

        # Explicit toggles, driven by the real keys.
        await pilot.press("R")
        await pilot.pause()
        assert not rail.display, "R must hide the rail"
        await pilot.press("R")
        await pilot.pause()
        assert rail.display

        await pilot.press("I")
        await pilot.pause()
        assert not inspector.display, "I must hide the inspector"


async def test_at_n06d_narrow_terminal_auto_collapses_the_rail(tmp_path):
    """The width half of AT-N06d, on a terminal too narrow for three regions."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _tree(app))
        # 100 - 24 (rail) - 36 (inspector) = 40 columns of canvas, below the
        # measured 58-column floor, so the rail yields.
        assert screen.rail_hidden, "the rail must yield before the canvas misreports coverage"
        assert screen.query_one("#map-canvas").size.width >= 40


def test_at_n03e_keybar_truncation_names_what_is_hidden():
    """AT-N03e — a bare `…` is a lie by omission; the marker must be countable.

    RED mutation: revert `keybar` to `text.truncate(width, overflow="ellipsis")`;
    the count and the help-key assertions fail.
    """
    groups = [
        ("nav", [("j", "siguiente"), ("k", "anterior"), ("h", "padre"), ("l", "hijo")]),
        ("node", [("a", "agregar hijo"), ("d", "documentos"), ("x", "archivar")]),
        ("view", [("f", "alternar foco"), ("m", "cobertura")]),
    ]
    total = sum(len(b) for _, b in groups)

    wide = darkside.keybar(groups, width=400)
    assert "…" not in wide.plain, "nothing is hidden, so nothing should claim to be"
    assert "cobertura" in wide.plain

    narrow = darkside.keybar(groups, width=40)
    assert narrow.cell_len <= 40, "the bar must fit the width it was given"
    assert "?" in narrow.plain and "todas" in narrow.plain

    # The count must be REAL: hidden + shown == total.
    marker = narrow.plain.split("… +")[1]
    hidden = int(marker.split()[0])
    shown = sum(1 for _, bindings in groups for key, _ in bindings if f"{key} " in narrow.plain)
    assert hidden > 0
    assert hidden + shown == total, f"marker claims {hidden} hidden, but {shown} of {total} shown"


def test_keybar_renders_at_the_width_it_is_given():
    """The bar used to render at a hard-coded 118 regardless of the terminal.

    Measured before the fix: 216 cells of content at a fixed 118, so 9 of 17
    bindings were shown and `m cobertura` was invisible.
    """
    groups = [("view", [(chr(97 + i), f"accion-{i}") for i in range(12)])]
    for width in (30, 60, 120):
        bar = darkside.keybar(groups, width=width)
        assert bar.cell_len <= width, f"overflowed a {width}-cell bar"
