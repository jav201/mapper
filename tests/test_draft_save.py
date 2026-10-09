"""Data-safety batch (2026-10-08), US-001: the card draft, `ctrl+s` and the guard.

Inc-1a covers the modal alone, hosted in a minimal `App` (and once in the real
`MapperApp`).  Inc-1b (second half of this file) drives the real `MapScreen`: the
inspector draft, `ctrl+s`, a failing save, and the node-change guard.  The pilot
helpers (E-1) are shared by both halves.

C13 / AT-015: the title oracle reads the Static's SOURCE content (`Static.content`,
the string the modal handed to the sink), never the rendered cells.  A rendered-cell
scan can pass for the wrong reason: the compositor replaces or drops controls the
source still carries.  The hostile code points are built with `chr()` (C-56).

The Inc-1b black-box oracle is the pair of sha256 digests of the map's `.mmd` and
`_nodos.yml` (contract §5.1 `obs`), read before and after real key presses.
"""
from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest
from rich.style import Style
from textual.app import App
from textual.widgets import Static

from mapper import darkside, keymap
from mapper.app import MapperApp, MapScreen
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.screens.draft_guard import DraftGuardScreen
from mapper.store import MapStore
from mapper.widgets.chrome import HintLine
from mapper.widgets.inspector import STATE_VALUES, FichaInspector

ESC_BYTE = chr(0x1B)
ESC_PAYLOAD = "t" + ESC_BYTE + "[2Jx"
CLICK_PAYLOAD = "[@click=screen.save]x[/]"
SURROGATE_PAYLOAD = "a" + chr(0xD800) + "b"
REPLACEMENT = chr(0xFFFD)


class _Host(App):
    """The smallest app that can show the guard and record how it was answered."""

    def __init__(self, title: str, map_id: str = "") -> None:
        super().__init__()
        self._guard_args = (title, map_id)
        self.answers: list[str] = []

    def on_mount(self) -> None:
        self.push_screen(DraftGuardScreen(*self._guard_args), self.answers.append)


async def _answer(app, pilot, key: str) -> None:
    """E-1: assert the guard is the screen first, then answer with a real key."""
    assert isinstance(app.screen, DraftGuardScreen), type(app.screen).__name__
    await pilot.press(key)
    await pilot.pause()


def _title_source(app) -> str:
    return app.screen.query_one("#draft-guard-title", Static).content


@pytest.mark.parametrize(
    ("key", "token"), [("s", "save"), ("d", "discard"), ("escape", "stay")]
)
async def test_llr_003_1_modal_returns_the_token_for_each_key(key, token):
    """Why: the three answers decide whether the operator's edit is written,
    dropped or kept.  Each key must return its own token and no other, and the
    guard must close (an answer that left it up would stack a second one)."""
    app = _Host("raiz", "kd")
    async with app.run_test() as pilot:
        await pilot.pause()
        await _answer(app, pilot, key)
        assert app.answers == [token]
        assert not isinstance(app.screen, DraftGuardScreen)


async def test_llr_003_1_an_unbound_key_answers_nothing():
    """Why: only the three seat keys answer.  A stray key is not consent to drop
    the draft, so the guard stays up and unanswered."""
    app = _Host("raiz", "kd")
    async with app.run_test() as pilot:
        await pilot.pause()
        await _answer(app, pilot, "x")
        assert app.answers == []
        assert isinstance(app.screen, DraftGuardScreen)


async def test_llr_003_1_the_title_follows_the_ruled_wording():
    """R9: `unsaved draft on «{title}» · {map_id}`, naming the map being left."""
    app = _Host("raiz", "kd")
    async with app.run_test() as pilot:
        await pilot.pause()
        assert _title_source(app) == "unsaved draft on «raiz» · kd"


async def test_llr_003_1_an_empty_title_renders_empty_guillemets():
    """LLR-003.1 boundary "empty — no title" (Inc-1a review F1).  A node may carry
    no title; the sentence still names the map and leaves the guillemets empty
    rather than inventing a placeholder the operator would read as a real title."""
    app = _Host("", "kd")
    async with app.run_test() as pilot:
        await pilot.pause()
        assert _title_source(app) == "unsaved draft on «» · kd"


@pytest.mark.parametrize(
    ("payload", "survives"),
    [
        pytest.param(ESC_PAYLOAD, "[2J", id="esc"),
        pytest.param(CLICK_PAYLOAD, CLICK_PAYLOAD, id="click-markup"),
        pytest.param(SURROGATE_PAYLOAD, "a" + REPLACEMENT + "b", id="surrogate"),
    ],
)
async def test_llr_003_1_modal_title_is_literal_and_plain(payload, survives):
    """AT-015 at modal level (Inc-1a part of C13).  `markup=False` alone leaves
    ESC in the string (Textual's content strip drops only BEL/BS/VT/FF/CR), and
    `plain` alone leaves `[@click=...]` live in a markup sink: the sink needs both.
    The oracle is the Static's source content, in the title and in the map id."""
    for title, map_id in ((payload, "kd"), ("raiz", payload)):
        app = _Host(title, map_id)
        async with app.run_test() as pilot:
            await pilot.pause()
            source = _title_source(app)
            assert ESC_BYTE not in source, ascii(source)
            assert chr(0xD800) not in source
            assert survives in source, ascii(source)
            assert source.startswith("unsaved draft on «")


async def test_llr_003_1_a_markup_payload_in_the_title_is_painted_literally():
    """SEC-H2 on the guard: a title cannot bind `screen.save` to the words the
    operator reads.  The painted visual carries the payload as plain characters
    and no span at all (a live `[@click=...]` would be consumed by the grammar,
    leaving `x` under a click span)."""
    app = _Host(CLICK_PAYLOAD, "kd")
    async with app.run_test() as pilot:
        await pilot.pause()
        visual = app.screen.query_one("#draft-guard-title", Static).visual
        assert CLICK_PAYLOAD in visual.plain, ascii(visual.plain)
        assert list(visual.spans) == []


async def test_llr_003_1_the_hint_row_is_read_from_the_draft_seat():
    """Why: the words beside the keys are the seat's words (K3), so the hint cannot
    drift from the keys that really answer."""
    app = _Host("raiz", "kd")
    async with app.run_test() as pilot:
        await pilot.pause()
        hints = app.screen.query_one("#draft-guard-hints", Static).content.plain
        wanted = [f"{b.glyph} {b.label}" for b in keymap.bindings_for(keymap.SCOPE_DRAFT)]
        assert wanted == ["s save", "d discard", "esc stay"]
        for pair in wanted:
            assert pair in hints, (pair, hints)


async def test_llr_003_1_the_hint_follows_the_seat_not_a_literal(monkeypatch):
    """Why: equal wording today does not prove the hint is READ from the seat.
    Relabel one row in the live seat and the painted hint must follow it."""
    relabelled = [
        replace(b, label="keep") if (b.scope, b.key) == (keymap.SCOPE_DRAFT, "escape") else b
        for b in keymap.KEYMAP
    ]
    monkeypatch.setattr(keymap, "KEYMAP", relabelled)
    app = _Host("raiz", "kd")
    async with app.run_test() as pilot:
        await pilot.pause()
        hints = app.screen.query_one("#draft-guard-hints", Static).content.plain
        assert "esc keep" in hints, hints
        assert "esc stay" not in hints


def test_llr_003_1_the_screen_bindings_are_generated_from_the_seat():
    """Why: `BINDINGS` is the dispatch.  If it were hand-written it could bind a key
    the seat does not declare (or the reverse) and the legend would lie."""
    bound = {(b.key, b.action) for b in DraftGuardScreen.BINDINGS}
    assert bound == {("s", "save"), ("d", "discard"), ("escape", "stay")}
    for _key, action in bound:
        assert callable(getattr(DraftGuardScreen, f"action_{action}"))


async def test_llr_003_1_app_chords_do_not_pass_through_the_guard(tmp_path):
    """Why: `?` and `ctrl+p` over a pending question would stack a legend or a
    palette on it.  In the real app both are inert while the guard is up."""
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        answers: list[str] = []
        app.push_screen(DraftGuardScreen("raiz", "kd"), answers.append)
        await pilot.pause()
        depth = len(app.screen_stack)
        for key in ("question_mark", "ctrl+p"):
            await _answer(app, pilot, key)
            assert len(app.screen_stack) == depth, key
        assert answers == []


# ===========================================================================
# Inc-1b -- the draft on the real MapScreen (E-1 / E-2 helpers below)
# ===========================================================================

SCHEMA = [SchemaField(key="D", label="documento", required=True)]
WIDE = (140, 40)


def _seed_map(app, map_id="ds", *, title_a="alfa"):
    """E-1: root -> {a, b}.  `a` is complete; `b` misses its required `D`."""
    g = Graph()
    g.schema = list(SCHEMA)
    g.add_node(Node(id="root", ficha=Ficha(title="raiz", fields={"D": "r"})))
    g.add_node(Node(id="a", ficha=Ficha(title=title_a, state="ok", notes="n", fields={"D": "acta"})))
    g.add_node(Node(id="b", ficha=Ficha(title="beta")))
    g.add_edge(Edge("root", "a"))
    g.add_edge(Edge("root", "b"))
    app.store.save(map_id, g)
    return map_id


async def _open(app, pilot, map_id, cursor="a"):
    app.push_screen(MapScreen(map_id))
    await pilot.pause()
    screen = app.screen
    screen.nav.cursor = cursor
    screen.refresh_canvas()
    await pilot.pause()
    return screen


def _hashes(tmp_path, map_id) -> tuple[str, str]:
    """The `obs` pair: sha256 of the `.mmd` and of the `_nodos.yml`."""
    return tuple(
        hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in (f"{map_id}.mmd", f"{map_id}_nodos.yml")
    )


async def _focus(pilot, screen, widget_id):
    screen.query_one(f"#{widget_id}").focus()
    await pilot.pause()


async def _type_into(pilot, screen, widget_id, text):
    """Focus the field, then one real key press per character."""
    await _focus(pilot, screen, widget_id)
    await pilot.press(*text)
    await pilot.pause()


async def _press(pilot, *keys):
    await pilot.press(*keys)
    await pilot.pause()


def _inspector(screen) -> FichaInspector:
    return screen.query_one("#map-inspector", FichaInspector)


def _header(screen) -> str:
    return _inspector(screen).query_one("#insp-header").visual.plain


def _label(screen, word) -> str:
    for label in _inspector(screen).query(".insp-label"):
        text = label.visual.plain
        if text.startswith(word):
            return text
    raise AssertionError(f"no label starts with {word!r}")


def _guards(app) -> int:
    return sum(isinstance(s, DraftGuardScreen) for s in app.screen_stack)


def _count_saves(screen) -> list[str]:
    """A counting wrapper over the real `store.save`."""
    calls: list[str] = []
    real = screen.store.save

    def counting(map_id, graph):
        calls.append(map_id)
        return real(map_id, graph)

    screen.store.save = counting
    return calls


def _failing_save(screen, *, after) -> list[str]:
    """E-2, the declared fault seam: `store.save` raises having written ZERO
    files (`after="zero"`) or after the real save wrote BOTH (`after="both"`)."""
    calls: list[str] = []
    real = screen.store.save

    def failing(map_id, graph):
        calls.append(map_id)
        if after == "both":
            real(map_id, graph)
        raise OSError("boom")

    screen.store.save = failing
    return calls


def _capture_notices(app) -> list[tuple[str, dict]]:
    notices: list[tuple[str, dict]] = []
    app.notify = lambda msg, **kw: notices.append((str(msg), kw))
    return notices


def _disk(tmp_path, map_id):
    return MapStore(tmp_path).load(map_id)


async def test_at_001_a_stray_key_then_blur_and_cursor_change_writes_nothing(tmp_path):
    """AT-001 (HLR-001): the B-36 stray write.  One stray key, leaving the field
    (the blur that used to write) and a cursor change must leave both files
    byte-identical, with the field visibly unsaved.  RED today: blur writes."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        start = _hashes(tmp_path, map_id)

        await _type_into(pilot, screen, "insp-title", "n")
        await _press(pilot, "escape")
        await _press(pilot, "j")
        assert _guards(app) == 1
        await _answer(app, pilot, "escape")

        assert _hashes(tmp_path, map_id) == start
        assert "●" in _label(screen, "title")
        assert screen.nav.cursor == "a"


async def test_at_002_ctrl_s_writes_once_and_u_restores_the_pre_save_state(tmp_path):
    """AT-002 (HLR-004): nothing is written by the edit; `ctrl+s` writes once;
    `u` puts back the pre-save state (one save = one undo step)."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        start = _hashes(tmp_path, map_id)

        await _type_into(pilot, screen, "insp-title", "x")
        assert _hashes(tmp_path, map_id) == start
        saves = _count_saves(screen)
        await _press(pilot, "ctrl+s")
        assert len(saves) == 1
        assert _hashes(tmp_path, map_id) != start
        assert _disk(tmp_path, map_id).nodes["a"].ficha.title == "alfax"

        await _press(pilot, "escape")
        await _press(pilot, "u")
        assert _hashes(tmp_path, map_id) == start


@pytest.mark.parametrize("after", ["zero", "both"], ids=["zero_files", "both_files"])
async def test_at_002a_failed_save_reloads_from_disk(tmp_path, after):
    """AT-002a (LLR-004.2, seam E-2): after a failed save, disk is the truth.
    Zero files written: both fields stay drafted.  Both written: the reload shows
    the edit, so the draft re-diffs to empty.  Either way the failure handling
    writes nothing and the undo stack is as it was."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        start = _hashes(tmp_path, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        await _type_into(pilot, screen, "insp-field-D", "y")
        depth = len(app.undo_stacks.get(map_id, []))
        calls = _failing_save(screen, after=after)

        await _press(pilot, "ctrl+s")

        inspector = _inspector(screen)
        assert len(calls) == 1, "the failure path wrote (or retried) the map"
        assert len(app.undo_stacks.get(map_id, [])) == depth
        if after == "zero":
            assert _hashes(tmp_path, map_id) == start
            assert inspector.draft_values() == {"title": "alfax", "D": "actay"}
            assert "● unsaved (2)" in _header(screen)
            assert "●" in _label(screen, "title") and "●" in _label(screen, "documento")
        else:
            assert _hashes(tmp_path, map_id) != start
            ficha = _disk(tmp_path, map_id).nodes["a"].ficha
            assert (ficha.title, ficha.fields["D"]) == ("alfax", "actay")
            assert not inspector.has_draft()
            assert "unsaved" not in _header(screen)
            assert "●" not in _label(screen, "title")


async def test_llr_004_2_a_reload_that_carries_the_drafted_state_turns_it_clean(tmp_path):
    """AT-002a [both files], state arm (LLR-004.2, design 1b.8).  A drafted `state`
    that reached disk before the save raised must turn clean on the reload.  The
    re-diff in `show()` is the only thing that cleans it: a remounted text input
    re-posts its value (and so re-diffs itself), the state segment does not, so a
    title-only oracle cannot tell whether `show()` re-diffs at all."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _focus(pilot, screen, "insp-state")
        await _press(pilot, "right")
        assert _inspector(screen).draft_values() == {"state": STATE_VALUES[1]}
        calls = _failing_save(screen, after="both")

        await _press(pilot, "ctrl+s")

        assert len(calls) == 1
        assert _disk(tmp_path, map_id).nodes["a"].ficha.state == STATE_VALUES[1]
        assert not _inspector(screen).has_draft()
        assert "unsaved" not in _header(screen)
        assert "●" not in _label(screen, "state")


async def test_at_003_header_counts_unsaved_fields_and_marks_each(tmp_path):
    """AT-003 (HLR-002): `● unsaved (N)` counts the dirty fields, up AND down."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed_map(app))
        assert "unsaved" not in _header(screen)

        await _type_into(pilot, screen, "insp-title", "x")
        assert "● unsaved (1)" in _header(screen)
        assert "●" in _label(screen, "title")
        assert "●" not in _label(screen, "documento")

        await _type_into(pilot, screen, "insp-field-D", "y")
        assert "● unsaved (2)" in _header(screen)

        await _focus(pilot, screen, "insp-title")
        await _press(pilot, "backspace")
        assert "● unsaved (1)" in _header(screen)
        assert "●" not in _label(screen, "title")
        assert "●" in _label(screen, "documento")


@pytest.mark.parametrize(("key", "answer"), [("s", "save"), ("d", "discard"), ("escape", "stay")])
async def test_at_004_node_change_with_a_draft_presents_the_guard(tmp_path, key, answer):
    """AT-004 (HLR-003, LLR-003.2): `j` with a draft asks once; `save` writes and
    moves, `discard` drops and moves, `stay` keeps the cursor and the draft."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        start = _hashes(tmp_path, map_id)
        saves = _count_saves(screen)

        await _press(pilot, "j")
        assert _guards(app) == 1
        await _answer(app, pilot, key)

        assert _guards(app) == 0
        inspector = _inspector(screen)
        if answer == "save":
            assert len(saves) == 1
            assert _hashes(tmp_path, map_id) != start
            assert _disk(tmp_path, map_id).nodes["a"].ficha.title == "alfax"
            assert screen.nav.cursor == "b"
        elif answer == "discard":
            assert saves == []
            assert _hashes(tmp_path, map_id) == start
            assert screen.nav.cursor == "b"
            assert not inspector.has_draft()
            assert screen.query_one("#insp-title").value == "beta"
        else:
            assert saves == []
            assert screen.nav.cursor == "a"
            assert inspector.draft_values() == {"title": "alfax"}
            assert screen.query_one("#insp-title").value == "alfax"
            assert "●" in _label(screen, "title")


async def test_at_006_enter_keeps_the_draft_leaves_the_field_and_the_hint_names_ctrl_s(tmp_path):
    """AT-006 (HLR-005): `↵` in a dirty field writes nothing, leaves the field and
    keeps the marker; the fill-in hint names the seat's save key, not `↵ save`."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id, cursor="root")
        start = _hashes(tmp_path, map_id)

        await _press(pilot, "M")
        hint = screen.query_one(HintLine).text
        assert "ctrl+s save" in hint, hint
        assert "↵ save" not in hint
        field = app.focused
        assert field is not None and field.id == "insp-field-D"

        await _press(pilot, "z")
        await _press(pilot, "enter")

        assert _hashes(tmp_path, map_id) == start
        assert app.focused is not field
        assert _inspector(screen).draft_values() == {"D": "z"}
        assert "●" in _label(screen, "documento")


async def test_at_007_state_segment_routes_through_the_draft(tmp_path):
    """AT-007 (HLR-006): a `state` change is drafted like any field, written
    only by `ctrl+s`.  RED today: the segment saves on the spot."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        start = _hashes(tmp_path, map_id)

        await _focus(pilot, screen, "insp-state")
        await _press(pilot, "right")
        assert _hashes(tmp_path, map_id) == start
        assert "●" in _label(screen, "state")

        await _press(pilot, "ctrl+s")
        assert _disk(tmp_path, map_id).nodes["a"].ficha.state == STATE_VALUES[1]


async def test_at_009_undo_leaves_the_draft_and_recomputes_the_markers(tmp_path):
    """AT-009 (LLR-004.3; stimulus per PDR Q-3): save (alfa->alfab, n->nm); draft
    again (title back to its pre-save `alfa`, notes `np`); `esc`, `u`.  Disk is
    back to (alfa, n); the title re-diffs CLEAN against the restored value, the
    notes stay dirty, and the draft's values are untouched."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "b")
        await _type_into(pilot, screen, "insp-notes", "m")
        await _press(pilot, "ctrl+s")
        assert _disk(tmp_path, map_id).nodes["a"].ficha.title == "alfab"

        await _focus(pilot, screen, "insp-title")
        await _press(pilot, "backspace")
        await _focus(pilot, screen, "insp-notes")
        await _press(pilot, "backspace", "p")
        assert "● unsaved (2)" in _header(screen)
        await _press(pilot, "escape")
        await _press(pilot, "u")

        ficha = _disk(tmp_path, map_id).nodes["a"].ficha
        assert (ficha.title, ficha.notes) == ("alfa", "n")
        assert "● unsaved (1)" in _header(screen)
        assert "●" not in _label(screen, "title")
        assert "●" in _label(screen, "notes")
        assert screen.query_one("#insp-notes").value == "np"


async def test_at_010_ctrl_s_inside_the_field_saves_the_typed_text(tmp_path):
    """AT-010 (HLR-001): `ctrl+s` from INSIDE the field saves what was typed --
    the draft follows every keystroke, not only blur or `↵`."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "xyz")
        assert app.focused is not None and app.focused.id == "insp-title"
        await _press(pilot, "ctrl+s")

        for name in (f"{map_id}.mmd", f"{map_id}_nodos.yml"):
            assert "alfaxyz" in (tmp_path / name).read_text(encoding="utf-8"), name


async def test_c7_focus_returns_to_the_edited_field_after_ctrl_s(tmp_path):
    """PDR C7: after `ctrl+s` from inside a field the operator keeps typing there."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-notes", "x")
        await _press(pilot, "ctrl+s")
        await pilot.pause()
        assert app.focused is not None and app.focused.id == "insp-notes"
        await _press(pilot, "y")
        assert _inspector(screen).draft_values() == {"notes": "nxy"}
        assert _disk(tmp_path, map_id).nodes["a"].ficha.notes == "nx"


@pytest.mark.parametrize(
    ("payload", "survives"),
    [pytest.param(ESC_PAYLOAD, "[2J", id="esc"), pytest.param(CLICK_PAYLOAD, CLICK_PAYLOAD, id="click-markup")],
)
async def test_at_015_guard_title_carries_no_escape_byte(tmp_path, payload, survives):
    """AT-015 through `j` (PDR C13): the guard the screen pushes names the hostile
    node title with no ESC and with markup as literal text."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app, title_a=payload)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-field-D", "y")
        await _press(pilot, "escape")
        await _press(pilot, "j")
        assert _guards(app) == 1

        source = _title_source(app)
        assert ESC_BYTE not in source, ascii(source)
        assert survives in source, ascii(source)
        assert source.endswith(f"» · {map_id}")
        await _answer(app, pilot, "escape")


async def test_llr_001_4_one_ctrl_s_is_one_store_save(tmp_path):
    """LLR-001.4: a three-field draft is ONE `store.save`; no draft is none."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        saves = _count_saves(screen)
        await _press(pilot, "ctrl+s")
        assert saves == []

        await _type_into(pilot, screen, "insp-title", "x")
        await _type_into(pilot, screen, "insp-field-D", "y")
        await _type_into(pilot, screen, "insp-notes", "z")
        await _press(pilot, "ctrl+s")
        assert len(saves) == 1
        ficha = _disk(tmp_path, map_id).nodes["a"].ficha
        assert (ficha.title, ficha.fields["D"], ficha.notes) == ("alfax", "actay", "nz")


async def test_llr_003_2_node_change_guard_holds_the_inspector_on_the_draft_node(tmp_path):
    """LLR-003.2: while the guard is up the inspector still shows the draft node
    with its draft value, and the cursor is back on it -- nothing re-pointed."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed_map(app))
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        await _press(pilot, "j")
        assert _guards(app) == 1

        assert screen.nav.cursor == "a"
        assert _inspector(screen).node.id == "a"
        assert screen.query_one("#insp-title").value == "alfax"
        await _answer(app, pilot, "escape")


async def test_llr_003_2_a_second_mover_while_the_guard_is_up_stacks_no_second_guard(tmp_path):
    """LLR-004.2 "no second guard while one is held": a cursor move arriving with
    the guard already up (the canvas repainted again) asks nothing more."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed_map(app))
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        await _press(pilot, "j")
        screen.nav.cursor = "b"
        screen.refresh_canvas()
        await pilot.pause()
        assert _guards(app) == 1
        assert screen.nav.cursor == "a"
        await _answer(app, pilot, "escape")


async def test_llr_003_2_a_move_onto_the_same_node_needs_no_guard(tmp_path):
    """LLR-003.2 boundary (PDR C14 arm): a repaint that leaves the cursor on the
    draft's node is not a node change, so nothing asks."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed_map(app))
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        await _press(pilot, "o")
        assert _guards(app) == 0
        assert _inspector(screen).draft_values() == {"title": "alfax"}


async def test_llr_004_1_one_snapshot_and_one_write_per_multi_field_save(tmp_path):
    """LLR-004.1: a two-field save is ONE undo step and ONE write."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        await _type_into(pilot, screen, "insp-field-D", "y")
        depth = len(app.undo_stacks.get(map_id, []))
        saves = _count_saves(screen)
        await _press(pilot, "ctrl+s")
        assert len(app.undo_stacks[map_id]) == depth + 1
        assert len(saves) == 1


async def test_llr_004_2_failure_restores_the_undo_stack_exactly_at_depth(tmp_path):
    """LLR-004.2: at `UNDO_DEPTH` the pushed snapshot evicts the oldest entry, so
    a failure must restore the stack WHOLE (content and order), not pop it."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        app.undo_stacks[map_id] = [f"blob-{i}".encode() for i in range(MapScreen.UNDO_DEPTH)]
        before = list(app.undo_stacks[map_id])
        await _type_into(pilot, screen, "insp-title", "x")
        _failing_save(screen, after="zero")
        await _press(pilot, "ctrl+s")
        assert app.undo_stacks[map_id] == before


async def test_llr_004_2_reload_raises_restores_the_pre_save_graph_without_a_write(tmp_path):
    """LLR-004.2 + PDR C8: save AND reload both fail.  The pre-save map comes back
    from memory (it was never mutated), nothing is written, the draft is kept,
    and the toast states what leaving now costs."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        start = _hashes(tmp_path, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        notices = _capture_notices(app)
        calls = _failing_save(screen, after="zero")

        def failing_load(_map_id):
            raise OSError("reload boom")

        screen.store.load = failing_load
        await _press(pilot, "ctrl+s")

        assert len(calls) == 1
        assert _hashes(tmp_path, map_id) == start
        assert screen.base_graph.nodes["a"].ficha.title == "alfa"
        assert screen.graph is screen.base_graph
        assert _inspector(screen).draft_values() == {"title": "alfax"}
        assert "could not reload · draft kept · leaving needs d (discard)" in [n for n, _ in notices]


async def test_llr_004_2_a_save_failure_names_ctrl_s_to_retry(tmp_path):
    """LLR-004.2: a failed save that reloaded tells the operator the draft is
    kept and which key retries, after the store's own path-free toast."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        notices = _capture_notices(app)
        _failing_save(screen, after="zero")
        await _press(pilot, "ctrl+s")
        messages = [n for n, _ in notices]
        # Inc-1c U4: ONE toast -- map id and error type, never str(e); names the retry key.
        assert messages[-1] == f"could not save {map_id!r} (OSError) · draft kept · ctrl+s to retry", messages
        assert sum(1 for n in messages if n.startswith("could not save")) == 1, messages
        assert notices[-1][1].get("severity") == "error"


async def test_llr_004_2_a_draft_on_a_vanished_node_is_dropped_with_a_warning(tmp_path):
    """LLR-004.2 boundary (PDR C14, E-2 third mode): the save reached disk, then
    the map was rewritten without the node.  The draft cannot be guarded or saved,
    so it is dropped with a warning naming the field, the cursor goes to the root,
    and no guard opens for a node that no longer exists."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        notices = _capture_notices(app)
        real = screen.store.save

        def save_then_lose_the_node(mid, graph):
            real(mid, graph)
            g = Graph()
            g.schema = list(SCHEMA)
            g.add_node(Node(id="root", ficha=Ficha(title="raiz", fields={"D": "r"})))
            g.add_node(Node(id="b", ficha=Ficha(title="beta")))
            g.add_edge(Edge("root", "b"))
            real(mid, g)
            raise OSError("boom")

        screen.store.save = save_then_lose_the_node
        await _press(pilot, "ctrl+s")

        assert not _inspector(screen).has_draft()
        assert screen.nav.cursor == "root"
        assert _guards(app) == 0
        warnings = [n for n, kw in notices if kw.get("severity") == "warning"]
        assert any("title" in n and "dropped" in n for n in warnings), notices


async def test_llr_004_2_failure_clears_focus_and_rebuilds_nav(tmp_path):
    """LLR-004.2: the reload re-establishes the view as opening the map does --
    focus mode cleared, a fresh navigation over the reloaded graph."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _press(pilot, "f")
        assert screen.focus_active
        await _type_into(pilot, screen, "insp-title", "x")
        _failing_save(screen, after="zero")
        await _press(pilot, "ctrl+s")

        assert not screen.focus_active
        assert screen.graph is screen.base_graph
        assert screen.nav.graph is screen.graph
        assert set(screen.graph.nodes) == {"root", "a", "b"}
        assert screen.nav.cursor == "a"


async def test_llr_004_3_undo_with_an_empty_stack_keeps_the_draft(tmp_path):
    """LLR-004.3 boundary: `u` with nothing to undo says so and leaves the draft
    and its markers exactly as they were (R5)."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "escape")
        notices = _capture_notices(app)
        await _press(pilot, "u")

        assert any("nothing to undo" in n for n, _ in notices)
        assert _inspector(screen).draft_values() == {"title": "alfax"}
        assert "● unsaved (1)" in _header(screen)
        assert "●" in _label(screen, "title")


async def test_llr_004_4_ctrl_s_under_focus_writes_the_whole_map(tmp_path):
    """LLR-004.4 / R-1: under focus (`f`) the graph on show is a subtree; the save
    still writes the whole map, and `u` restores the whole map."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        await _press(pilot, "f")
        assert screen.focus_active and set(screen.graph.nodes) == {"a"}
        await _type_into(pilot, screen, "insp-title", "x")
        await _press(pilot, "ctrl+s")

        disk = _disk(tmp_path, map_id)
        assert set(disk.nodes) == {"root", "a", "b"}
        assert disk.nodes["a"].ficha.title == "alfax"

        await _press(pilot, "escape")
        await _press(pilot, "u")
        disk = _disk(tmp_path, map_id)
        assert set(disk.nodes) == {"root", "a", "b"}
        assert disk.nodes["a"].ficha.title == "alfa"


async def test_llr_005_2_fill_in_hint_reads_the_save_glyph_from_the_seat(tmp_path, monkeypatch):
    """LLR-005.2: the hint's save key is READ from the seat.  Relabel the
    `save_draft` row and the painted hint must follow it."""
    relabelled = [
        replace(b, label="write") if b.action == "save_draft" else b for b in keymap.KEYMAP
    ]
    monkeypatch.setattr(keymap, "KEYMAP", relabelled)
    row = next(b for b in keymap.bindings_for(keymap.SCOPE_MAP) if b.action == "save_draft")
    app = MapperApp(tmp_path)
    async with app.run_test(size=WIDE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed_map(app), cursor="root")
        await _press(pilot, "M")
        hint = screen.query_one(HintLine).text
        assert f"{row.glyph} {row.label}" == "ctrl+s write"
        assert "ctrl+s write" in hint, hint
        assert "↵" not in hint


@pytest.mark.parametrize("field", ["title", "notes", "state", "D"])
def test_layer0_apply_field_coerces_and_routes(field):
    """TC-L0-2: each key lands on its own attribute, coerced by `plain` (A-111)."""
    ficha = Ficha(title="t", notes="n", state="ok", fields={"D": "d"})
    value = "a" + chr(0xD800) + "b"
    MapScreen._apply_field(ficha, field, value)
    got = {"title": ficha.title, "notes": ficha.notes, "state": ficha.state, "D": ficha.fields["D"]}
    assert got[field] == darkside.plain(value) == "a" + REPLACEMENT + "b"
    untouched = {"title": "t", "notes": "n", "state": "ok", "D": "d"}
    for other, before in untouched.items():
        if other != field:
            assert got[other] == before, other


def _hint_text_and_prefix_style(screen) -> tuple[str, Style | None]:
    """The hint line as COMPOSITED (what the operator sees), and the style the
    `●` of its prefix is painted in."""
    region = screen.query_one(HintLine).region
    strips = screen._compositor.render_strips()  # noqa: SLF001
    text, mark_style = "", None
    for strip in strips[region.y: region.y + region.height]:
        x = 0
        for seg in strip:
            if region.x <= x < region.x + region.width:
                text += seg.text
                if "●" in seg.text and mark_style is None:
                    mark_style = seg.style
            x += len(seg.text)
    return text, mark_style


@pytest.mark.parametrize("width", [87, 118, 140])
async def test_c6_a_hidden_card_hands_the_draft_to_the_hint_line_in_alert(tmp_path, width):
    """PDR C6 / R8: with the card hidden (auto at 87, `I` elsewhere) the hint line
    leads with `● unsaved (N) · ctrl+s save`, painted ALERT, and keeps it across
    a hint the screen rewrites for its own reasons; saving removes it."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(width, 34)) as pilot:
        await pilot.pause()
        map_id = _seed_map(app)
        screen = await _open(app, pilot, map_id)
        assert screen.inspector_hidden == (width == 87)
        if screen.inspector_hidden:
            await _press(pilot, "I")
        await _type_into(pilot, screen, "insp-title", "x")
        await _type_into(pilot, screen, "insp-field-D", "y")
        await _press(pilot, "escape")
        prefix = "● unsaved (2) · ctrl+s save · "
        assert prefix not in _hint_text_and_prefix_style(screen)[0]

        await _press(pilot, "I")
        assert screen.inspector_hidden
        text, style = _hint_text_and_prefix_style(screen)
        assert text.lstrip().startswith(prefix), text
        assert style is not None and style.color.get_truecolor().hex.lower() == darkside.ALERT.lower()

        hint_before = screen.query_one(HintLine).text
        await _press(pilot, "H")
        assert screen.query_one(HintLine).text != hint_before, "the pan did not rewrite the hint"
        assert _hint_text_and_prefix_style(screen)[0].lstrip().startswith(prefix)

        # Card shown again: it carries the draft itself, so the repaint drops the prefix.
        await _press(pilot, "I")
        assert not screen.inspector_hidden
        assert "unsaved" not in _hint_text_and_prefix_style(screen)[0]
        await _press(pilot, "I")
        assert _hint_text_and_prefix_style(screen)[0].lstrip().startswith(prefix)

        await _press(pilot, "ctrl+s")
        assert "unsaved" not in _hint_text_and_prefix_style(screen)[0]
