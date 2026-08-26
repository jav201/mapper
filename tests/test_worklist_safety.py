"""Acceptance tests for the coverage worklist (US-N04) and safety (US-N05)."""
from __future__ import annotations

from mapper.app import MapperApp, MapScreen, _ConfirmScreen
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.screens.coverage import CoverageScreen
from mapper.store import MapStore
from mapper.widgets.inspector import FichaInspector

SCHEMA = [
    SchemaField(key="D", label="documento", required=True),
    SchemaField(key="O", label="dueño", required=True),
]


def _seed(app, map_id="wl", complete=False):
    """root (complete) -> a (missing O), b (complete) -> b1 (missing D and O)."""
    g = Graph()
    g.schema = list(SCHEMA)
    full = {"D": "acta", "O": "luis"}
    g.add_node(Node(id="root", ficha=Ficha(title="erp", fields=dict(full))))
    g.add_node(Node(id="a", ficha=Ficha(title="alfa",
                                        fields=dict(full) if complete else {"D": "acta"})))
    g.add_node(Node(id="b", ficha=Ficha(title="beta", fields=dict(full))))
    g.add_node(Node(id="b1", ficha=Ficha(title="beta uno",
                                         fields=dict(full) if complete else {})))
    g.add_edge(Edge("root", "a"))
    g.add_edge(Edge("root", "b"))
    g.add_edge(Edge("b", "b1"))
    app.store.save(map_id, g)
    return map_id


async def _open(app, pilot, map_id):
    app.push_screen(MapScreen(map_id))
    await pilot.pause()
    await pilot.pause()
    return app.screen


# ---------------------------------------------------------------------------
# US-N04 — the worklist
# ---------------------------------------------------------------------------


async def test_at_n04a_enter_on_a_coverage_row_jumps_and_focuses_the_gap(tmp_path):
    """AT-N04a — the cursor moves AND focus lands on the first MISSING field.

    `a` has `D` filled and `O` empty, so the focused input must be `O` — not
    `schema[0]`.  A test that accepted `D` would pass against code that always
    focuses the first schema field.

    RED mutation: focus `schema[0]` instead of the first missing field; the
    focused-id assertion reads `insp-field-D`.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))

        screen._goto_gap("a")
        await pilot.pause()
        await pilot.pause()

        assert screen.nav.cursor == "a"
        assert app.focused is not None, "nothing was focused after the jump"
        assert app.focused.id == "insp-field-O", (
            f"focus landed on {app.focused.id}, not the first missing field"
        )


async def test_at_n04b_next_gap_advances_across_nodes_and_wraps(tmp_path):
    """AT-N04b — the worklist walks the whole map and wraps exactly once.

    Two incomplete nodes here (`a` and `b1`), so the observed sequence pins both
    the step and the wrap.  Asserting only "it moved" would pass against code that
    always jumps to the same node.

    RED mutation: `return` instead of wrapping; the fourth observation fails.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))

        observed = []
        for _ in range(4):
            screen.action_next_gap()
            await pilot.pause()
            observed.append(screen.nav.cursor)

        assert observed == ["a", "b1", "a", "b1"], observed


async def test_at_n04c_a_complete_map_reports_exhaustion_and_does_not_cycle(tmp_path):
    """AT-N04c — the boundary: nothing missing anywhere.

    RED mutation: drop the empty-order guard; `action_next_gap` raises or moves
    the cursor when it should do neither.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app, complete=True))
        before = screen.nav.cursor

        assert screen._incomplete_order() == []
        screen.action_next_gap()
        await pilot.pause()
        assert screen.nav.cursor == before, "the cursor moved on a complete map"


async def test_at_n04d_complete_map_coverage_report_is_not_a_selectable_row(tmp_path):
    """The report's empty state must read as a statement, not an empty list.

    It used to be a fake selectable row that `enter` dismissed in silence.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        await _open(app, pilot, _seed(app, complete=True))
        app.push_screen(CoverageScreen(app.screen.graph, "wl"))
        await pilot.pause()
        report = app.screen
        assert report.complete
        assert not report.query_one("#coverage-table").display
        assert "todo completo" in report.query_one("#coverage-empty").render().plain


# ---------------------------------------------------------------------------
# US-N05 — safety
# ---------------------------------------------------------------------------


async def test_at_n05a_archiving_a_subtree_asks_first_and_a_refusal_preserves_it(tmp_path):
    """AT-N05a — the discriminating negative: declining changes NOTHING on disk.

    Before this batch a non-root subtree was destroyed with no prompt at all.

    RED mutation: restore the `do_archive(True)` fast path for non-root nodes;
    both the modal assertion and the on-disk assertion fail.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app)
        screen = await _open(app, pilot, map_id)
        screen.nav.cursor = "b"
        before = (tmp_path / f"{map_id}.mmd").read_bytes(), \
                 (tmp_path / f"{map_id}_nodos.yml").read_bytes()

        await pilot.press("x")
        await pilot.pause()
        assert isinstance(app.screen, _ConfirmScreen), "x destroyed a subtree unconfirmed"
        # The message must say how much goes: `b` takes `b1` with it.
        assert "descendiente" in app.screen.message

        await pilot.press("n")
        await pilot.pause()
        after = (tmp_path / f"{map_id}.mmd").read_bytes(), \
                (tmp_path / f"{map_id}_nodos.yml").read_bytes()
        assert after == before, "declining the confirmation still changed the map on disk"
        assert set(MapStore(tmp_path).load(map_id).nodes) == {"root", "a", "b", "b1"}


async def test_at_n05b_accepting_removes_exactly_that_subtree(tmp_path):
    """AT-N05b — the whole subtree goes, and nothing else does.

    Pins the surviving set exactly: code that spared descendants would leave an
    orphaned `b1`, and code that removed too much would drop `a`.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app)
        screen = await _open(app, pilot, map_id)
        screen.nav.cursor = "b"

        await pilot.press("x")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()

        assert set(MapStore(tmp_path).load(map_id).nodes) == {"root", "a"}


async def test_at_n05c_undo_survives_leaving_and_re_entering_the_map(tmp_path):
    """AT-N05c — the history is the App's, so a new screen inherits it.

    Before this batch `_snapshots` was a MapScreen instance attribute, so leaving
    the map discarded the history and an archived subtree became unrecoverable.

    RED mutation: move the stack back onto `MapScreen.__init__`; the restored-set
    assertion fails.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app)
        screen = await _open(app, pilot, map_id)
        screen.nav.cursor = "b"
        await pilot.press("x")
        await pilot.pause()
        await pilot.press("y")
        await pilot.pause()
        assert set(MapStore(tmp_path).load(map_id).nodes) == {"root", "a"}

        # Leave the map entirely, then come back on a NEW screen instance.
        await pilot.press("q")
        await pilot.pause()
        screen2 = await _open(app, pilot, map_id)
        assert screen2 is not screen, "the test did not actually re-enter on a new screen"

        screen2.action_undo()
        await pilot.pause()
        restored = MapStore(tmp_path).load(map_id)
        assert set(restored.nodes) == {"root", "a", "b", "b1"}
        assert restored.nodes["b1"].ficha.title == "beta uno", "the ficha came back too"


async def test_at_n05d_undo_on_an_empty_stack_reports_and_does_not_raise(tmp_path):
    """AT-N05d — the boundary case, and it must not corrupt the map."""
    app = MapperApp(tmp_path)
    notes: list[str] = []
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app)
        screen = await _open(app, pilot, map_id)
        screen.notify = lambda msg, **kw: notes.append(str(msg))
        before = (tmp_path / f"{map_id}.mmd").read_bytes()

        screen.action_undo()
        await pilot.pause()

        assert notes and "nada que deshacer" in notes[0]
        assert (tmp_path / f"{map_id}.mmd").read_bytes() == before


async def test_llr_n05_6_an_edit_is_undoable_and_undo_is_per_map(tmp_path):
    """Two properties in one place because they share a fixture.

    (a) LLR-N05.6 — committing a field edit pushes a snapshot, so `u` reverts the
    EDIT rather than an unrelated earlier structural change.
    (b) LLR-N05.3 — the stacks are keyed by map, so an undo in one map cannot
    restore a snapshot of another.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app)
        screen = await _open(app, pilot, map_id)
        inspector = screen.query_one("#map-inspector", FichaInspector)

        inspector.post_message(FichaInspector.FieldCommitted("a", "O", "carmen"))
        await pilot.pause()
        assert MapStore(tmp_path).load(map_id).nodes["a"].ficha.fields["O"] == "carmen"

        screen.action_undo()
        await pilot.pause()
        assert MapStore(tmp_path).load(map_id).nodes["a"].ficha.fields.get("O", "") == "", (
            "undo did not revert the field edit"
        )

        # (b) the stacks are per map.
        other = _seed(app, map_id="wl2")
        assert set(app.undo_stacks) <= {map_id, "wl2"}
        assert app.undo_stacks.get("wl2", []) == [], "a second map inherited another map's history"
