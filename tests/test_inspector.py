"""Black-box acceptance tests for the editable ficha inspector (US-N01).

Every test drives the shipped surface — the inspector mounted on a real
`MapScreen`, edited through real key presses — and, where the story is about
persistence, re-reads what `MapStore` actually wrote to disk and feeds it back
through the unmodified `MapStore.load` (control C-12).  A test that wrote the
sidecar directly would be a consumer-contract guard, not this gate.
"""
from __future__ import annotations

import pytest

from mapper import darkside
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

    Data-safety batch (2026-10-08) Inc-1b: the value is persisted by `ctrl+s`
    (the draft's save gesture), no longer by `↵`, which now keeps the draft.

    RED mutation: drop the `_save_or_toast(...)` call from `MapScreen._save_draft`;
    the reloaded-value assertion fails.
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
        await pilot.press("ctrl+s")
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

    Data-safety batch (2026-10-08) Inc-1b: driven through the real segment and
    `ctrl+s` instead of a posted message.  Each arm starts from the state AFTER its
    target and steps back once, so every arm, `ok` included, is a real change (a
    draft equal to the shown value is not dirty and would write nothing).
    """
    from mapper.store import MapStore

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app, state=STATE_VALUES[(index + 1) % len(STATE_VALUES)])
        screen = await _open(app, pilot, map_id)

        screen.query_one("#insp-state").focus()
        await pilot.pause()
        await pilot.press("left")
        await pilot.press("ctrl+s")
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
                if "required" in s.render().plain
            ]

        before = flagged()
        assert len(before) == 1, f"expected exactly one flagged row, got {before}"
        assert "dueño" in before[0]

        # Inc-1b: filled through the real field and saved with `ctrl+s`; the flag
        # is read from the rows rebuilt after the save.
        inspector.focus_field("O")
        await pilot.pause()
        await pilot.press("L", "u", "i", "s", "ctrl+s")
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
        assert "j/k/h/l move" in hint.render().plain

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


# ---------------------------------------------------------------------------
# Data-safety batch (2026-10-08) Inc-1b, US-001 -- the inspector's draft.
# The black-box ATs are in `tests/test_draft_save.py`; these are the unit and
# white-box nodes over the draft surface (I-1) and its handlers.
# ---------------------------------------------------------------------------


def _count_saves(screen) -> list[str]:
    calls: list[str] = []
    real = screen.store.save

    def counting(map_id, graph):
        calls.append(map_id)
        return real(map_id, graph)

    screen.store.save = counting
    return calls


def _inspector(screen) -> FichaInspector:
    return screen.query_one("#map-inspector", FichaInspector)


def _header(screen) -> str:
    return _inspector(screen).query_one("#insp-header").visual.plain


async def test_llr_001_1_draft_surface_is_a_copy_and_clears(tmp_path):
    """TC-001.1: `draft_values()` hands out a COPY (a caller cannot edit the draft
    behind the inspector's back), and `clear_draft()` empties it completely."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        inspector = _inspector(screen)
        assert not inspector.has_draft() and inspector.draft_node_id is None

        screen.query_one("#insp-title").focus()
        await pilot.pause()
        await pilot.press("x")
        await pilot.pause()
        values = inspector.draft_values()
        assert values == {"title": "nóminax"} and inspector.draft_node_id == "nom"
        values.clear()
        assert inspector.has_draft()
        assert inspector.draft_values() == {"title": "nóminax"}

        inspector.clear_draft()
        assert not inspector.has_draft()
        assert inspector.draft_values() == {}
        assert inspector.draft_node_id is None


class _PostTap:
    """E-6 (PDR C11): records every message type that reaches the SCREEN."""

    def __init__(self, screen):
        self.types: list[type] = []
        real = screen.post_message

        def tap(message):
            self.types.append(type(message))
            return real(message)

        screen.post_message = tap


# Messages whose `MapScreen` handler writes the map.  A blur or `↵` must reach
# the screen as none of these (C11: a denylist of save-bearing paths).
SAVE_BEARING = (FichaInspector.AttachmentAddRequested, FichaInspector.AttachmentRemoveRequested)


async def test_llr_001_2_draft_updates_on_every_keystroke_and_posts_no_save(tmp_path):
    """TC-001.2a: after EACH key the draft holds the text so far; leaving the
    field by blur or by `↵` saves nothing (0 `store.save` calls, files unchanged)
    and reaches the screen as no save-bearing message.  The primary oracle is the
    save count and the bytes; the message tap is the C11 denylist."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        map_id = _seed(app, fields={"D": "ACTA"})
        screen = await _open(app, pilot, map_id)
        inspector = _inspector(screen)
        before = (tmp_path / f"{map_id}.mmd").read_bytes(), (tmp_path / f"{map_id}_nodos.yml").read_bytes()
        saves = _count_saves(screen)
        tap = _PostTap(screen)
        drafted = []
        screen._save_draft = lambda: drafted.append(1) or True

        inspector.focus_field("O")
        await pilot.pause()
        typed = ""
        for ch in "Luis":
            await pilot.press(ch)
            await pilot.pause()
            typed += ch
            assert inspector.draft_values()["O"] == typed
        await pilot.press("enter")
        await pilot.pause()
        inspector.focus_field("D")
        await pilot.pause()
        await pilot.press("z")
        screen.query_one("#map-canvas").focus()
        await pilot.pause()

        assert saves == [] and drafted == []
        after = (tmp_path / f"{map_id}.mmd").read_bytes(), (tmp_path / f"{map_id}_nodos.yml").read_bytes()
        assert after == before
        assert not [t for t in tap.types if issubclass(t, SAVE_BEARING)], tap.types
        assert inspector.draft_values() == {"O": "Luis", "D": "ACTAz"}


async def test_llr_001_2_a_stale_change_from_a_re_pointed_input_is_dropped(tmp_path):
    """TC-001.2b: a change from an input built for ANOTHER node (the inspector
    re-pointed before it was handled) never lands in this node's draft."""
    from textual.widgets import Input

    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        inspector = _inspector(screen)
        old_input = screen.query_one("#insp-title")
        assert old_input.node_id == "nom"

        screen.nav.cursor = "root"
        screen.refresh_canvas()
        await pilot.pause()
        assert inspector.node.id == "root"
        inspector.post_message(Input.Changed(old_input, "zz"))
        await pilot.pause()

        assert not inspector.has_draft()


async def test_llr_002_1_dirty_is_against_the_shown_value_plain_alters_title(tmp_path):
    """TC-002.1 [plain alters the title]: a stored title with a control character
    is SHOWN coerced.  Editing away and back to what is shown is clean -- dirty is
    measured against the shown value, not the raw stored one."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app, title="a" + chr(0x07) + "b"))
        inspector = _inspector(screen)
        assert not inspector.has_draft()
        screen.query_one("#insp-title").focus()
        await pilot.pause()
        await pilot.press("x", "backspace")
        await pilot.pause()
        assert not inspector.has_draft()
        assert "unsaved" not in _header(screen)


async def test_llr_002_1_dirty_is_measured_against_plain_not_the_raw_title(tmp_path):
    """TC-002.1 [plain alters the title], Layer 0.  `store.load` already passes a
    title through `plain`, so through the real load path raw == shown and the
    test above cannot tell them apart.  A node held in memory that never crossed
    the load boundary can carry a raw control character: the form shows it
    coerced, so the shown value -- not the raw one -- must count as clean."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        inspector = _inspector(screen)
        raw = "a" + chr(0x07) + "b"
        node = screen.graph.nodes["nom"]
        node.ficha.title = raw
        inspector.show(node, screen.graph)
        await pilot.pause()
        assert screen.query_one("#insp-title").value == darkside.plain(raw) != raw
        inspector._put_draft("nom", "title", darkside.plain(raw))
        assert not inspector.has_draft()


async def test_llr_002_1_dirty_is_against_the_shown_value_unknown_state(tmp_path):
    """TC-002.1 [unknown state]: a stored state `weird` is shown as `ok`; moving
    right then left lands on what is shown, which is clean."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app, state="weird"))
        inspector = _inspector(screen)
        screen.query_one("#insp-state").focus()
        await pilot.pause()
        await pilot.press("right")
        await pilot.pause()
        assert inspector.draft_values() == {"state": "risk"}
        await pilot.press("left")
        await pilot.pause()
        assert not inspector.has_draft()


async def test_llr_002_2_markers_update_without_remounting_the_focused_field(tmp_path):
    """TC-002.2: the count repaints on every key while the SAME field keeps the
    focus -- a remount per key would destroy the field being typed in."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        screen.query_one("#insp-notes").focus()
        await pilot.pause()
        field = app.focused
        for ch in "abc":
            await pilot.press(ch)
            await pilot.pause()
            assert app.focused is field
            assert "● unsaved (1)" in _header(screen)
        assert field.value == "abc"


async def test_llr_005_1_enter_leaves_the_field_and_keeps_the_draft(tmp_path):
    """TC-005.1: `↵` leaves the field, keeps the draft, writes nothing (R7)."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        inspector = _inspector(screen)
        saves = _count_saves(screen)
        inspector.focus_field("O")
        await pilot.pause()
        await pilot.press("L", "u", "z", "enter")
        await pilot.pause()

        assert app.focused is None or app.focused.id != "insp-field-O"
        assert isinstance(app.screen, MapScreen)
        assert inspector.draft_values() == {"O": "Luz"}
        assert saves == []


async def test_llr_006_1_state_change_updates_the_draft_and_writes_nothing(tmp_path):
    """TC-006.1: the segment drafts `risk` and nothing reaches the store (R2)."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app, state="ok"))
        saves = _count_saves(screen)
        screen.query_one("#insp-state").focus()
        await pilot.pause()
        await pilot.press("right")
        await pilot.pause()
        assert _inspector(screen).draft_values() == {"state": "risk"}
        assert saves == []


@pytest.mark.parametrize(
    ("widget_id", "keys", "key"),
    [
        ("insp-title", ("x",), "title"),
        ("insp-notes", ("x",), "notes"),
        ("insp-field-D", ("x",), "D"),
        ("insp-state", ("right",), "state"),
    ],
    ids=["title", "notes", "D", "state"],
)
async def test_llr_006_2_every_editable_surface_has_a_draft_key(tmp_path, widget_id, keys, key):
    """TC-006.2 (aid to the inspection LLR): each editable surface drafts under its
    own key -- schema keys plus the pseudo-keys `title` / `notes` / `state`."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app, state="ok"))
        screen.query_one(f"#{widget_id}").focus()
        await pilot.pause()
        await pilot.press(*keys)
        await pilot.pause()
        assert set(_inspector(screen).draft_values()) == {key}


@pytest.mark.parametrize("branch", ["stale", "equal_to_shown", "set"])
async def test_layer0_put_draft_branches(tmp_path, branch):
    """TC-L0-1: the three branches of the draft's one mutator (seam E-3)."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 40)) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        inspector = _inspector(screen)
        inspector._put_draft("nom", "notes", "kept")
        if branch == "stale":
            inspector._put_draft("root", "title", "zz")
            assert inspector.draft_values() == {"notes": "kept"}
        elif branch == "equal_to_shown":
            inspector._put_draft("nom", "notes", "")
            assert inspector.draft_values() == {}
            assert inspector.draft_node_id is None
            return
        else:
            inspector._put_draft("nom", "title", "otro")
            assert inspector.draft_values() == {"notes": "kept", "title": "otro"}
        assert inspector.draft_node_id == "nom"
