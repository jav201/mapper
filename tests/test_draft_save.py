"""Data-safety batch (2026-10-08), US-001: the draft guard modal (Inc-1a).

Inc-1a covers the modal alone, hosted in a minimal `App` (and once in the real
`MapperApp`): nothing pushes the guard yet.  Inc-1b adds the inspector draft and the
wiring to this file, and the pilot helpers below (E-1) are shared with it.

C13 / AT-015: the title oracle reads the Static's SOURCE content (`Static.content`,
the string the modal handed to the sink), never the rendered cells.  A rendered-cell
scan can pass for the wrong reason: the compositor replaces or drops controls the
source still carries.  The hostile code points are built with `chr()` (C-56).
"""
from __future__ import annotations

from dataclasses import replace

import pytest
from textual.app import App
from textual.widgets import Static

from mapper import keymap
from mapper.app import MapperApp
from mapper.screens.draft_guard import DraftGuardScreen

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
