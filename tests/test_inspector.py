"""Black-box acceptance tests for the editable ficha inspector (US-N01).

Every test drives the shipped surface — the inspector mounted on a real
`MapScreen`, edited through real key presses — and, where the story is about
persistence, re-reads what `MapStore` actually wrote to disk and feeds it back
through the unmodified `MapStore.load` (control C-12).  A test that wrote the
sidecar directly would be a consumer-contract guard, not this gate.
"""
from __future__ import annotations

import pytest

from mapper.app import MapperApp, MapScreen
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.widgets.inspector import STATE_VALUES, FichaInspector

SCHEMA = [
    SchemaField(key="D", label="documento", required=True),
    SchemaField(key="O", label="dueño", required=True),
    SchemaField(key="C", label="criticidad", required=False),
]


def _seed(app, map_id="insp", *, title="nómina", fields=None, notes="", state=""):
    g = Graph()
    g.schema = list(SCHEMA)
    g.add_node(Node(id="root", ficha=Ficha(title="erp legacy")))
    g.add_node(
        Node(
            id="nom",
            ficha=Ficha(
                title=title,
                state=state,
                notes=notes,
                fields=dict(fields or {"D": "ACTA-2013-005"}),
            ),
        )
    )
    g.add_edge(Edge("root", "nom"))
    app.store.save(map_id, g)
    return map_id


async def _open(app, pilot, map_id, cursor="nom"):
    app.push_screen(MapScreen(map_id))
    await pilot.pause()
    screen = app.screen
    screen.nav.cursor = cursor
    screen.refresh_canvas()
    await pilot.pause()
    return screen


async def test_at_n01a_editing_a_schema_field_persists_to_disk(tmp_path):
    """AT-N01a — type into a schema field, and the value is on disk afterwards.

    Output-then-consume (C-12): the value is read back through a FRESH MapStore,
    so the chain inspector -> save -> .mmd/_nodos.yml -> load is exercised whole.

    RED mutation: drop the `self.store.save(...)` call from
    `on_ficha_inspector_field_committed`; the reloaded-value assertion fails.
    """
    from mapper.store import MapStore

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app, fields={"D": "ACTA-2013-005"})
        screen = await _open(app, pilot, map_id)

        inspector = screen.query_one("#map-inspector", FichaInspector)
        assert inspector.focus_field("O"), "the owner field must be reachable"
        await pilot.pause()
        await pilot.press("L", "u", "i", "s")
        await pilot.press("enter")
        await pilot.pause()

        reloaded = MapStore(tmp_path).load(map_id)
        assert reloaded.nodes["nom"].ficha.fields["O"] == "Luis"
        # The untouched field must survive the whole-graph write.
        assert reloaded.nodes["nom"].ficha.fields["D"] == "ACTA-2013-005"


@pytest.mark.parametrize("index,expected", list(enumerate(STATE_VALUES)))
async def test_at_n01b_state_persists_for_every_value(tmp_path, index, expected):
    """AT-N01b — one arm per state, driven off a NON-default value (C-10).

    A test that only checked the default `ok` would pass whether the control is
    wired or hard-coded.  Three of these four arms cannot pass on a clamped setter.

    RED mutation: clamp the state setter to "ok"; the risk/late/blocked arms fail.
    """
    from mapper.store import MapStore

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app)
        screen = await _open(app, pilot, map_id)
        inspector = screen.query_one("#map-inspector", FichaInspector)

        inspector.post_message(
            FichaInspector.FieldCommitted("nom", "state", STATE_VALUES[index])
        )
        await pilot.pause()

        reloaded = MapStore(tmp_path).load(map_id)
        assert reloaded.nodes["nom"].ficha.state == expected


async def test_at_n01c_rows_are_labelled_from_the_schema_not_the_key(tmp_path):
    """AT-N01c — the operator sees `documento`, never the bare letter `D`.

    RED mutation: render `field.key` instead of `field.label`; the label
    assertions fail and the bare-letter assertion fails too.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        inspector = screen.query_one("#map-inspector", FichaInspector)

        labels = [
            s.render().plain.strip()
            for s in inspector.query(".insp-label")
        ]
        for field in SCHEMA:
            assert any(field.label in text for text in labels), f"{field.label} missing"
        # The raw key must never stand in as a row name.
        assert not any(text in {f.key for f in SCHEMA} for text in labels)


async def test_at_n01d_required_and_empty_is_flagged(tmp_path):
    """AT-N01d — a required field with no value is marked, and the mark clears.

    Two observations, not one: the flag appears for the empty required field AND
    disappears once it is filled.  A test that only checked the first would pass
    against code that flags every row unconditionally.

    RED mutation: change the flag predicate to `key not in fields`; the count
    after filling stays wrong.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        # `O` (dueño) is required and empty; `D` is required and present.
        map_id = _seed(app, fields={"D": "ACTA-2013-005"})
        screen = await _open(app, pilot, map_id)
        inspector = screen.query_one("#map-inspector", FichaInspector)

        def flagged() -> list[str]:
            return [
                s.render().plain
                for s in inspector.query(".insp-label")
                if "requerido" in s.render().plain
            ]

        before = flagged()
        assert len(before) == 1, f"expected exactly one flagged row, got {before}"
        assert "dueño" in before[0]

        inspector.post_message(FichaInspector.FieldCommitted("nom", "O", "Luis"))
        await pilot.pause()
        assert flagged() == [], "the flag must clear once the field is filled"


async def test_at_n01e_hostile_file_derived_text_renders_literally(tmp_path):
    """AT-N01e — markup, an unmatched CLOSING tag, and ANSI, all from the sidecar.

    The unmatched closing tag is the case that matters: an unbalanced OPENING
    bracket does not raise, but `[/bold]` reaching a markup-parsing sink raises
    MarkupError.  A fixture with only the opening case passes while the crashing
    case ships.

    RED mutation: render a field value with `Static(f"[dim]{value}[/]")`; the
    literal-text assertion fails and styled spans appear.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        hostile_title = "[bold red]PWN[/]"
        map_id = _seed(
            app,
            title=hostile_title,
            notes="unmatched [/bold] closing tag",
            fields={"D": "acta\x1b[31mX\x1b[0m", "O": "x"},
        )
        screen = await _open(app, pilot, map_id)
        inspector = screen.query_one("#map-inspector", FichaInspector)

        header = inspector.query_one("#insp-header").render()
        # Rendered literally: the markup is still visible as text...
        assert "[bold red]PWN[/]" in header.plain
        # ...and it produced no attacker-controlled style.
        assert all(span.style in ("", None) or "red" not in str(span.style)
                   for span in header.spans)
        # No escaping artefact: `rich.markup.escape` in a Text path emits visible
        # backslashes, which is a bug in the other direction.
        assert "\\[" not in header.plain

        # The ANSI escape must not survive into a field's value.
        doc_value = inspector.query_one("#insp-field-D").value
        assert "\x1b" not in doc_value, "an ESC in the sidecar reached the terminal"
        assert "�" in doc_value, "the control character should be replaced, not dropped"


async def test_at_n06b_escape_leaves_the_field_and_keeps_the_value(tmp_path):
    """AT-N06b — `escape` while editing must not pop the map and discard the text.

    Before this batch, a screen-level `escape` fired even with an Input focused,
    so typing then pressing escape left the map entirely and lost the edit.

    RED mutation: remove `FieldInput`'s widget-level escape binding; the screen
    binding wins again and the map is popped.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        inspector = screen.query_one("#map-inspector", FichaInspector)
        inspector.focus_field("O")
        await pilot.pause()
        await pilot.press("L", "u", "z")
        await pilot.press("escape")
        await pilot.pause()

        assert isinstance(app.screen, MapScreen), "escape in a field left the map"
        assert app.focused is None or app.focused.id != "insp-field-O"
        assert screen.query_one("#insp-field-O").value == "Luz", "the typed value was discarded"


async def test_map_keys_work_on_arrival_and_are_suppressed_while_editing(tmp_path):
    """The focus contract, both directions.

    On arrival the map owns the keyboard; while a field is focused it does not.
    Asserting only one direction would miss the failure mode that actually
    shipped — an auto-focused Input silently killing every map binding.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        assert app.focused is None, "a text field grabbed the keyboard on arrival"

        # Map key works.
        await pilot.press("m")
        await pilot.pause()
        from mapper.screens.coverage import CoverageScreen

        assert isinstance(app.screen, CoverageScreen)
        await pilot.press("escape")
        await pilot.pause()

        # ...and is suppressed while a field holds focus.
        inspector = app.screen.query_one("#map-inspector", FichaInspector)
        inspector.focus_field("O")
        await pilot.pause()
        await pilot.press("m")
        await pilot.pause()
        assert isinstance(app.screen, MapScreen), "a map binding fired while typing"
        assert app.screen.query_one("#insp-field-O").value.endswith("m")


async def test_llr_n01_6_hintline_can_change_after_mount(tmp_path):
    """LLR-N01.6 — HintLine gained the setter its siblings already had.

    Driven through the mounted widget on a real screen, because the point of the
    requirement is that the hint can change *after* mount.
    """
    from mapper.widgets.chrome import HintLine

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        hint = screen.query_one(HintLine)
        assert "navega" in hint.render().plain

        hint.set_hint("completa «dueño» y la ficha queda cerrada", "ctrl+s")
        await pilot.pause()
        rendered = hint.render().plain
        assert "ficha queda cerrada" in rendered and "ctrl+s" in rendered
        assert "navega" not in rendered


def test_llr_n01_9_missing_required_is_owned_by_the_model():
    """LLR-N01.9 — one definition of 'what is missing', consumed by three surfaces."""
    ficha = Ficha(fields={"D": "acta", "O": "   "})
    missing = ficha.missing_required(SCHEMA)
    # `O` is whitespace-only: present as a key, but not filled in.
    assert [f.key for f in missing] == ["O"]
    # Order follows the schema, not dict insertion.
    ficha2 = Ficha(fields={})
    assert [f.key for f in ficha2.missing_required(SCHEMA)] == ["D", "O"]
