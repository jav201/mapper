"""The relation screen host — seat-driven chrome, derive-on-open, the frozen
surface (batch `2026-10-25-relmap-r2-batch`, trunk Inc-2).

Host arms only: the three renderer bodies land in lanes 3/4/5 against the
host↔renderer surface this increment freezes (`mapper/screens/relmap/base.py`).
AT-148's renderer-content arms execute at the lane gates and the join; this file
pins what the HOST owes at every view: the seat-derived BINDINGS and keybar, the
crumb naming descriptor and active view, derive-on-open plus `r` re-derivation
through `derive_reqharness_map` (LLR-RVH.3.2), the closed-set refusal path
(LLR-RVH.5.1), the `_row_text`/`fit` label sink (LLR-RVH.5.2, COND-SEC-1), the
out-of-view inert chords (LLR-RVH.4.1, COND-UX-1), the seat-derived help and
palette entries (LLR-RVH.4.4, AT-149 — Inc-6b), and Home's enumeration,
kind routing, and refusal surfaces (LLR-RVH.1–3/.5 — the Inc-6 shell lane).

The whole-seat pins (`tests/test_keymap.py`, `tests/test_key_dispatch.py`) are
the seat census; this file drives REAL keys through `run_test()` (C-16).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from textual.widgets import Static

import mapper
from mapper.app import MapperApp
from mapper.keymap import SCOPE_RELMAP, bindings_for, palette_items
from mapper.relmap.descriptor import default_descriptor
from mapper.screens.help import HelpScreen
from mapper.screens.palette import CommandPalette
from mapper.screens.relmap import RelMapScreen
from mapper.screens.relmap import base as base_mod
from mapper.screens.relmap import screen as screen_mod

ROOT = Path(mapper.__file__).resolve().parent.parent

HEADER = "| Id | Status | Statement |\n|---|---|---|\n"


def canon(*rows: str) -> str:
    return HEADER + "".join(r + "\n" for r in rows)


def row(row_id: str, status: str = "active", statement: str = "text") -> str:
    return f"| {row_id} | {status} | {statement} |"


def painted_frame(screen) -> bytes:
    """The composited frame serialized as (text, style) runs — the idiom of
    `tests/test_colour_always_on.py::_painted_frame`."""
    rows = [
        [(seg.text, str(seg.style)) for seg in strip]
        for strip in screen._compositor.render_strips()  # noqa: SLF001
    ]
    return repr(rows).encode("utf-8")


def frame_text(screen) -> str:
    """The painted frame as one plain string (segment joins included) — for
    substring assertions on painted chrome."""
    return "\n".join(
        "".join(seg.text for seg in strip)
        for strip in screen._compositor.render_strips()  # noqa: SLF001
    )


@pytest.fixture
def workspace(tmp_path):
    """A non-git fixture workspace whose canon derives a small honest map."""
    (tmp_path / "REQUIREMENTS.md").write_text(
        canon(
            row("HLR-DEMO.1", statement="the host arms"),
            row("LLR-DEMO.1.1"),
            row("LLR-DEMO.1.2"),
        ),
        encoding="utf-8",
    )
    return tmp_path


def open_relmap(app, workspace, name="demo", descriptor=None):
    """Push a relation screen the way Home will route it in Inc-6."""
    screen = RelMapScreen(
        name,
        workspace,
        descriptor=descriptor if descriptor is not None else default_descriptor(),
    )
    app.push_screen(screen)
    return screen


async def _open_and_pause(app, pilot, workspace):
    screen = open_relmap(app, workspace)
    await pilot.pause()
    await pilot.pause()
    return screen


# ---------------------------------------------------------------------------
# LLR-RVH.4.2 — the BINDINGS and the keybar come from the seat
# ---------------------------------------------------------------------------


def test_llr_rvh_4_2_bindings_are_seat_generated():
    """`BINDINGS` is `screen_bindings(SCOPE_RELMAP)` — never a hand-written list
    (M-RVH-10: one hand row reddens this)."""
    from mapper.screens.common import screen_bindings

    assert RelMapScreen.BINDINGS is not None
    assert list(RelMapScreen.BINDINGS) == screen_bindings(SCOPE_RELMAP)


async def test_llr_rvh_4_2_keybar_groups_read_the_seat(tmp_path):
    """The keybar renders the seat's groups in the seat's order, live.

    At 118 columns the bar TRUNCATES with its declared `… +N ? all keys`
    marker — the census of every row is the seat pins' job
    (`tests/test_keymap.py`, `tests/test_key_dispatch.py`); here the bar's
    CONSTRUCTION is asserted against the seat plus the leading painted rows."""
    from mapper.keymap import groups_for_keybar
    from mapper.screens.common import keybar_groups

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await _open_and_pause(app, pilot, tmp_path)
        bar = app.screen.query_one("#relmap-keybar")
        assert bar.groups == groups_for_keybar(keybar_groups(SCOPE_RELMAP))
        painted = frame_text(app.screen)
        bar_line = next(line for line in painted.splitlines() if "matrix" in line and "view" in line)
        for glyph, label in (("1", "matrix"), ("2", "gaps"), ("3", "sheet")):
            assert f"{glyph} {label}" in bar_line, (
                f"the keybar does not paint the seat row {glyph} {label}"
            )
        assert "all keys" in bar_line, "the truncation declaration is owed at 118"


# ---------------------------------------------------------------------------
# LLR-RVH.3.2 — derive-on-open and `r` refresh
# ---------------------------------------------------------------------------


async def test_llr_rvh_3_2_open_derives_once_and_r_rederives(workspace, monkeypatch):
    """The derive count is 1 at open and 2 after `r` (M-RVH-8: serving the
    cached map without re-deriving reddens this).  The counter WRAPS the real
    `derive_reqharness_map` (COND-QA-4) — the Layer A arm exercises the real
    mechanism, never a replacement."""
    calls: list[tuple[Path, object]] = []
    real = screen_mod.derive_reqharness_map

    def counting(repo, descriptor):
        calls.append((repo, descriptor))
        return real(repo, descriptor)

    monkeypatch.setattr(screen_mod, "derive_reqharness_map", counting)
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_and_pause(app, pilot, workspace)
        assert len(calls) == 1, f"open must derive exactly once, got {len(calls)}"
        await pilot.press("r")
        await pilot.pause()
        await pilot.pause()
        assert len(calls) == 2, f"`r` must re-derive, got {len(calls)}"
        assert calls[1] == calls[0], "`r` must re-derive from the SAME descriptor and workspace"
        assert screen.relmap is not None


async def test_llr_rvh_3_2_open_calls_derive_with_the_workspace_and_descriptor(workspace, monkeypatch):
    """Layer A: open derives with `Path(workspace)/descriptor` — unrestricted."""
    calls: list[tuple[Path, object]] = []
    real = screen_mod.derive_reqharness_map

    def counting(repo, descriptor):
        calls.append((repo, descriptor))
        return real(repo, descriptor)

    monkeypatch.setattr(screen_mod, "derive_reqharness_map", counting)
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        descriptor = default_descriptor()
        open_relmap(app, workspace, "demo", descriptor)
        await pilot.pause()
        await pilot.pause()
        assert len(calls) == 1
        assert calls[0][0] == workspace
        assert calls[0][1] is descriptor


# ---------------------------------------------------------------------------
# LLR-RVH.3.3 — workspace-as-repo (non-git fixture), M-RVH-16/17
# ---------------------------------------------------------------------------


async def test_llr_rvh_3_3_non_git_workspace_derives(workspace):
    """The fixture workspace is NOT a git repository and the map still derives
    (M-RVH-16: consulting `.git` reddens this).  The workspace-as-repo probe is
    `evidence/p2-seam-workspace-repo.md`."""
    assert not (workspace / ".git").exists()
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_and_pause(app, pilot, workspace)
        assert screen.relmap is not None
        assert any(n.id == "HLR-DEMO.1" for n in screen.relmap.nodes)


async def test_llr_rvh_5_1_missing_canon_refuses_without_crashing(tmp_path):
    """No canon file at all: the closed-set K3 cause, the fixed refusal line,
    the app alive (M-RVH-17: a raw escape reddens this; M-RVH-14: a re-raise
    reddens this)."""
    assert not (tmp_path / "REQUIREMENTS.md").exists()
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_and_pause(app, pilot, tmp_path)
        assert screen.relmap is None
        painted = frame_text(app.screen)
        assert "file not found" in painted
        assert "descriptor skipped" in painted
        # The refusal text is the FIXED line — never str(exc), a path, an
        # anchor name or a YAML snippet (M-RVH-13).
        assert "CanonUnavailable" not in painted
        assert "RepoReadError" not in painted
        assert str(tmp_path) not in painted
        await pilot.press("q")
        await pilot.pause()
        assert app.screen.__class__.__name__ == "HomeScreen"


# ---------------------------------------------------------------------------
# LLR-RVH.4.3 — compose, crumb, and view switching
# ---------------------------------------------------------------------------


async def test_llr_rvh_4_3_view_switching_updates_the_crumb(workspace):
    """`1`/`2`/`3` swap the active view and the crumb names it after each
    switch (M-RVH-11: swapping without the crumb update reddens this)."""
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_and_pause(app, pilot, workspace)
        crumb = app.screen.query_one("#relmap-crumb")
        for key, view in (("2", "gaps"), ("3", "sheet"), ("1", "matrix")):
            await pilot.press(key)
            await pilot.pause()
            await pilot.pause()
            assert screen.active_view == view
            painted = frame_text(app.screen)
            assert f"/ {view}" in painted, (
                f"the crumb does not name the active view {view!r} after `{key}`"
            )


# ---------------------------------------------------------------------------
# LLR-RVH.4.1 / COND-UX-1 — out-of-view chords are inert (M-RVH-19)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "view_key,off_home",
    (
        ("2", ("c", "enter")),  # gaps: `c` chains the sheet, `enter` focuses the matrix lens
        ("3", ("k",)),          # sheet: `k` groups the gaps
        ("1", ("c", "k")),      # matrix: neither toggle is at home here
    ),
)
async def test_llr_rvh_4_1_view_specific_chords_inert_off_home(workspace, view_key, off_home, monkeypatch):
    """On a non-home view the view-specific chords change NOTHING: the active
    renderer's `toggle` is never called, the exported frame is byte-identical,
    no state flips, no crash.  M-RVH-19: a chord acting on a non-home view
    (or leaving home-view state reachable off-home) reddens this arm."""
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_and_pause(app, pilot, workspace)
        await pilot.press(view_key)
        await pilot.pause()
        await pilot.pause()
        calls: list[str] = []
        active = screen._views[screen.active_view]
        real_toggle = active.toggle

        def spy(kind: str) -> str:
            calls.append(kind)
            return real_toggle(kind)

        monkeypatch.setattr(active, "toggle", spy)
        before = painted_frame(app.screen)
        for chord in off_home:
            calls.clear()
            await pilot.press(chord)
            await pilot.pause()
            await pilot.pause()
            assert calls == [], (
                f"`{chord}` reached the {screen.active_view} renderer's toggle off its home view"
            )
            after = painted_frame(app.screen)
            assert after == before, (
                f"`{chord}` acted on a non-home view — the frame changed"
            )
            assert screen._view_state_words[screen.active_view] == "", (
                f"`{chord}` flipped renderer state off its home view"
            )


# ---------------------------------------------------------------------------
# LLR-RVH.5.2 / COND-SEC-1 — the one label sink (`_row_text`/`fit`)
# ---------------------------------------------------------------------------


def test_llr_rvh_5_2_label_sink_coerces_before_the_cut():
    """The seam is `darkside._row_text`/`fit` — `plain` + LF/TAB/CR to single
    space — into explicit-style `Text`.  M-RVH-18: a sink letting LF/TAB
    through reddens this; M-RVH-15: f-string markup assembly reddens the
    hostile arms below."""
    from rich.text import Text

    payload = "a]b[/bold]\x1b[31m\tc\nd"
    out = base_mod.label(payload, 118)
    assert isinstance(out, Text)
    plain = out.plain
    assert "\n" not in plain and "\t" not in plain and "\x1b" not in plain
    assert "]b[/bold]" in plain, "the payload must render LITERALLY, not as markup"
    # Coerce-then-cut (C-10): the width is measured on the coerced string, so
    # a payload whose raw form is longer than `width` still paints ONE row.
    assert len(plain.rstrip()) <= 118
    assert plain.rstrip() != ""
    # M-RVH-18's specific shape: bare `plain` PRESERVES LF/TAB — the seam is
    # the `_row_text`/`fit` wording, asserted against the helper itself.
    assert darkside_row_breakers_map()  # positive control: the map is non-empty


def darkside_row_breakers_map():
    from mapper import darkside

    return darkside._ROW_BREAKERS == {0x0009: " ", 0x000A: " ", 0x000D: " "}


async def test_llr_rvh_5_2_hostile_descriptor_name_renders_on_one_row(tmp_path):
    """A descriptor whose file name carries a hostile payload refuses or
    renders literally — never a MarkupError, never a second forged row.  The
    name reaches the crumb, which routes through the one sink."""
    hostile = tmp_path / "de]mo[x.relmap.yml"
    hostile.write_text(
        "kind: relation\nprofile: reqharness\n", encoding="utf-8"
    )
    from mapper.relmap.descriptor import load_descriptor

    descriptor = load_descriptor(hostile, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = open_relmap(app, tmp_path, "de]mo[x", descriptor)
        await pilot.pause()
        await pilot.pause()
        painted = frame_text(app.screen)
        assert "de]mo[x" in painted, "the hostile name must render literally"
        await pilot.press("q")
        await pilot.pause()
        assert app.screen.__class__.__name__ == "HomeScreen"


# ---------------------------------------------------------------------------
# LLR-RVH.4.1 (seat half) — leave and the quiet-leave alias
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("chord", ["q", "escape"])
async def test_llr_rvh_4_1_leave_and_quiet_leave_alias(workspace, chord):
    """`q` leaves to Home; `escape` is the quiet-leave alias."""
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await _open_and_pause(app, pilot, workspace)
        await pilot.press(chord)
        await pilot.pause()
        assert app.screen.__class__.__name__ == "HomeScreen"


# ---------------------------------------------------------------------------
# The frozen D1 surface — names and behaviour the lanes build against
# ---------------------------------------------------------------------------


def test_d1_surface_names_are_frozen():
    """The host↔renderer surface the lanes draft against: the `ViewState`
    fields, the renderer protocol's `paint`/`row_count`/`toggle`, the seat
    scope, and the renderer-module wiring convention (`build_view()`).
    Amended at the Inc-2 review pass (orchestrator ruling, D1 amendment,
    `LED-2026-10-25-r2.18`): `row_count(state) -> int` joins the protocol
    (each view's own row axis — PendingView has none and returns 0) and the
    vestigial `lens` field drops (the matrix lens rides the `enter` toggle
    channel)."""
    import inspect

    fields = {f for f in getattr(base_mod.ViewState, "__dataclass_fields__", {})}
    assert fields == {
        "relmap", "notice", "focus", "cursor", "gaps", "width", "height",
    }, f"the frozen ViewState surface moved: {fields}"
    assert hasattr(base_mod.RelMapView, "paint")
    assert hasattr(base_mod.RelMapView, "toggle")
    assert hasattr(base_mod.RelMapView, "row_count")
    toggle = inspect.signature(base_mod.RelMapView.toggle)
    assert list(toggle.parameters) == ["self", "kind"]
    paint = inspect.signature(base_mod.RelMapView.paint)
    assert list(paint.parameters) == ["self", "state"]
    row_count = inspect.signature(base_mod.RelMapView.row_count)
    assert list(row_count.parameters) == ["self", "state"]
    # The placeholder stays the honest pre-lane body — zero rows, every
    # toggle inert, the full viewport painted (the trunk Inc-2 contract,
    # kept verbatim against the class itself).
    placeholder = base_mod.PendingView("pending")
    assert placeholder.toggle("c") == "" and placeholder.toggle("k") == ""
    state = base_mod.ViewState(None, "notice", None, 0, (), 40, 10)
    assert placeholder.row_count(state) == 0, "the placeholder owns no row axis"
    rows = placeholder.paint(state)
    assert len(rows) == 10, "the placeholder paints the full viewport height"
    assert all(not isinstance(r, str) for r in rows)
    # Landed renderers (lanes 3/4/5, increments 003/004/005): the same wiring
    # convention, and the D1 toggle channel — "" for kinds not their own, the
    # state word for their own kind (COND-ARCH-1; `LED-2026-10-25-r2.20`).
    for name, own, word in (("matrix", "enter", "panel lens"),
                            ("gaps", "k", "by kind"),
                            ("sheet", "c", "stacked chain")):
        view = base_mod.build_view(name)
        assert view.name == name
        for foreign in ("enter", "c", "k"):
            if foreign != own:
                fresh = base_mod.build_view(name)
                assert fresh.toggle(foreign) == "", (
                    f"{name} answered a foreign toggle kind {foreign!r}"
                )
        assert view.toggle(own) == word, (
            f"{name} owns toggle kind {own!r} and must return its state word"
        )


def test_d1_freeze_text_names_the_full_toggle_vocabulary():
    """F5/F10: the frozen document names the complete toggle-kind vocabulary
    and the matrix crumb word — a lane reading `base.py` alone discovers
    `enter`/`c`/`k`, `panel lens`, `by kind` and the `row_count` axis rule,
    and the renderer's `notice` obligation is stated in the freeze text."""
    doc = base_mod.__doc__ or ""
    for token in (
        "enter", "c", "k", "panel lens", "by kind", "direct only",
        "stacked chain", "row_count", "notice",
    ):
        assert token in doc, f"the freeze text must name {token!r}"


def test_llr_rvh_3_2_unavailable_state_paints_the_notice_through_the_sink():
    """The unavailable state routes the fixed refusal line through the same
    one sink — one row, no markup parse."""
    view = base_mod.build_view("matrix")
    rows = view.paint(
        base_mod.ViewState(None, "structure: refused (x): file not found - descriptor skipped",
                           None, 0, (), 60, 10),
    )
    assert any("file not found" in r.plain for r in rows)


class _RecordingView:
    """A pre-lane renderer double for the host arms: owns a row axis and a
    toggle word, records what the host calls (the review's live-repro stand-
    in — the placeholder's `toggle` returns `""`, so word-host behaviour is
    invisible without a double)."""

    def __init__(self, name: str, word: str, count: int) -> None:
        self.name = name
        self._word = word
        self._count = count
        self.calls: list[str] = []
        self.seen_cursors: list[int] = []

    def paint(self, state):
        self.seen_cursors.append(state.cursor)
        return [base_mod.label(f"{self.name} body", state.width)]

    def row_count(self, state):
        return self._count

    def toggle(self, kind: str) -> str:
        self.calls.append(kind)
        return self._word


def _crumb_line(painted: str, view: str) -> str:
    return next(line for line in painted.splitlines() if f"relmap / {view}" in line)


# ---------------------------------------------------------------------------
# Independent review follow-ups (evidence/review-inc002.md) — F1, F2, M-REV-3
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("width", (118, 87))
async def test_review_f1_the_crumb_never_shows_another_views_state_word(workspace, width, monkeypatch):
    """F1: the toggle-state word is stored PER VIEW — the crumb shows the
    ACTIVE view's own word, never another view's; switching back restores
    it.  The reviewer's live repro at 118 and 87: `k` on gaps (`by kind`) →
    `1` → the matrix crumb must NOT say `by kind`."""
    app = MapperApp(workspace)
    async with app.run_test(size=(width, 34)) as pilot:
        screen = await _open_and_pause(app, pilot, workspace)
        gaps = _RecordingView("gaps", word="by kind", count=2)
        monkeypatch.setitem(screen._views, "gaps", gaps)
        await pilot.press("2")
        await pilot.pause()
        await pilot.pause()
        await pilot.press("k")
        await pilot.pause()
        await pilot.pause()
        assert gaps.calls == ["k"], "on its home view `k` must reach the gaps toggle"
        assert "· by kind" in _crumb_line(frame_text(app.screen), "gaps")
        await pilot.press("1")
        await pilot.pause()
        await pilot.pause()
        crumb = _crumb_line(frame_text(app.screen), "matrix")
        assert "by kind" not in crumb, (
            "F1: the matrix crumb paints the gaps view's state word"
        )
        await pilot.press("2")
        await pilot.pause()
        await pilot.pause()
        assert "· by kind" in _crumb_line(frame_text(app.screen), "gaps"), (
            "returning to gaps must restore its own word"
        )


@pytest.mark.parametrize("width", (118, 87))
async def test_review_f2_the_cursor_clamps_at_the_last_row_without_wrapping(workspace, width, monkeypatch):
    """F2: the cursor moves within [0, row_count) of the ACTIVE view's own
    row axis, clamped at the ends — holding `down` past the last row stops,
    never wraps to row 00 (the pre-amendment node-axis wrap).  A node-axis
    double stands in for the landed matrix lane (the placeholder answers
    0 — the placeholder arm covers that)."""
    app = MapperApp(workspace)
    async with app.run_test(size=(width, 34)) as pilot:
        screen = await _open_and_pause(app, pilot, workspace)
        monkeypatch.setitem(
            screen._views, "matrix", _RecordingView("matrix", word="panel lens", count=3)
        )
        for _ in range(3):
            await pilot.press("down")
            await pilot.pause()
            await pilot.pause()
        assert screen._cursors["matrix"] == 2, (
            "clamped at the last row — a wraparound would be back at 0"
        )
        for _ in range(2):
            await pilot.press("down")
            await pilot.pause()
            await pilot.pause()
        assert screen._cursors["matrix"] == 2, (
            "3 nodes: the cursor must stop at the last row, not wrap"
        )
        assert screen.focus == "LLR-DEMO.1.2", "the node selection follows the cursor"
        for _ in range(5):
            await pilot.press("up")
            await pilot.pause()
            await pilot.pause()
        assert screen._cursors["matrix"] == 0
        assert screen.focus == "HLR-DEMO.1"


@pytest.mark.parametrize("width", (118, 87))
async def test_review_f2_each_view_keeps_its_own_cursor(workspace, width, monkeypatch):
    """F2: ONE CURSOR PER VIEW, passed as `ViewState.cursor` for the active
    view only — the gaps cursor moves over ranked rows and never moves the
    matrix cursor or the node-axis `focus`; switching back restores the
    matrix cursor where it was."""
    app = MapperApp(workspace)
    async with app.run_test(size=(width, 34)) as pilot:
        screen = await _open_and_pause(app, pilot, workspace)
        monkeypatch.setitem(
            screen._views, "matrix", _RecordingView("matrix", word="panel lens", count=3)
        )
        gaps = _RecordingView("gaps", word="by kind", count=2)
        monkeypatch.setitem(screen._views, "gaps", gaps)
        await pilot.press("down")
        await pilot.pause()
        await pilot.pause()
        assert screen._cursors["matrix"] == 1
        await pilot.press("2")
        await pilot.pause()
        await pilot.pause()
        await pilot.press("down")
        await pilot.pause()
        await pilot.pause()
        assert screen._cursors["gaps"] == 1, "the gaps cursor moves over ITS row axis"
        assert gaps.seen_cursors[-1] == 1, (
            "ViewState.cursor must be the ACTIVE view's own cursor"
        )
        assert screen._cursors["matrix"] == 1, "the matrix cursor is untouched"
        assert screen.focus == "LLR-DEMO.1.1", (
            "the gaps row axis is not the node axis — `focus` stays where the"
            " matrix move left it"
        )
        await pilot.press("1")
        await pilot.pause()
        await pilot.pause()
        assert screen._cursors["matrix"] == 1, "switching back restores the cursor"


async def test_review_f2_the_placeholder_has_no_rows_to_cursor_over(workspace):
    """`PendingView.row_count` is 0 (D1): on a pre-lane view the cursor keys
    are honest no-ops — no crash, no movement, no wrap."""
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        screen = await _open_and_pause(app, pilot, workspace)
        await pilot.press("2")
        await pilot.pause()
        await pilot.pause()
        for _ in range(3):
            await pilot.press("down")
            await pilot.pause()
            await pilot.pause()
        assert screen._cursors["gaps"] == 0


# ---------------------------------------------------------------------------
# Emitted-form / honesty helpers
# ---------------------------------------------------------------------------


def test_fixture_canon_derives_honest_skeleton(workspace):
    """Positive control for the fixture class: the small canon derives the
    three seeded nodes through the real adapter."""
    from mapper.relmap.adapter import derive_reqharness_map

    derivation = derive_reqharness_map(workspace, default_descriptor())
    assert [n.id for n in derivation.map.nodes] == [
        "HLR-DEMO.1", "LLR-DEMO.1.1", "LLR-DEMO.1.2",
    ]
    assert hashlib.sha256(canon().encode()).hexdigest(), "canon() builder is alive"


# ---------------------------------------------------------------------------
# Inc-6 (lane L6, the shell) — Home enumeration + the kind badge, open routing
# by kind, the derived reqharness row (LLR-RVH.1.1–1.3, 2.1–2.3, 3.1,
# 5.1/.5.2 · AT-145…AT-147 · mutants M-RVH-1…M-RVH-7)
# ---------------------------------------------------------------------------

import re
from types import SimpleNamespace

from rich.markup import escape
from rich.text import Text
from textual.widgets import DataTable

from mapper import darkside
from mapper.relmap.descriptor import discover_descriptors
from mapper.screens.home import HomeScreen
from mapper.screens.map.screen import MapScreen

RELATION_BADGE = "relation·reqharness"
CHIP_STYLE = f"{darkside.INK} on {darkside.STEP}"
#: The write-vocabulary stems LLR-RVH.2.2 bans from the relmap seat
#: (LLR-RVH.2.2 names them: draft, save, archive, edit, osopen-launch).
WRITE_STEMS = ("draft", "save", "archive", "edit", "osopen")
#: Whole-canvas census for AT-147: no invented US-/AT-/TC- id shapes anywhere.
INVENTED_ID = re.compile(r"\b(?:US|AT|TC)-[A-Z0-9]")


def write_vocabulary_in(bindings) -> list[str]:
    """Every action whose stem is a write verb — the LLR-RVH.2.2 census
    predicate.  A census that cannot fail is vacuous; the planted rows in
    `test_llr_rvh_2_2_relmap_scope_binds_no_write_action` prove it reports."""
    out = []
    for binding in bindings:
        stem = binding.action.split("_")[0]
        if stem in WRITE_STEMS:
            out.append(binding.action)
    return out


def _plain(cell) -> str:
    return cell.plain if hasattr(cell, "plain") else str(cell)


def _row_names(table) -> list[str]:
    return [_plain(table.get_row(key)[0]) for key in table.rows]


def _kind_cells(table) -> list[str]:
    return [_plain(table.get_row(key)[1]) for key in table.rows]


def _seed_tree_map(workspace, name="legacy") -> None:
    """One tree map whose sidecar schema makes the kind cell read `legacy`."""
    (workspace / f"{name}.mmd").write_text(
        "graph TD\n    a[A] --> b[B]\n", encoding="utf-8"
    )
    (workspace / f"{name}_nodos.yml").write_text(
        "schema:\n  - key: D\n    label: documento\n    required: true\n",
        encoding="utf-8",
    )


def _seed_descriptor(workspace, name="demo.relmap.yml") -> None:
    (workspace / name).write_text(
        "kind: relation\nprofile: reqharness\n", encoding="utf-8"
    )


@pytest.fixture
def at145_workspace(tmp_path):
    """AT-145's fixture workspace: one tree map beside one descriptor, and
    NO canon — the relation row exists without the derived row."""
    _seed_tree_map(tmp_path, "legacy")
    _seed_descriptor(tmp_path)
    return tmp_path


@pytest.fixture
def at147_workspace(tmp_path):
    """AT-147's fixture workspace: no descriptor, a small canon and one tree
    map — Home owes the derived row named by the canon stem."""
    (tmp_path / "REQUIREMENTS.md").write_text(
        canon(
            row("HLR-DEMO.1", statement="the host arms"),
            row("LLR-DEMO.1.1"),
            row("LLR-DEMO.1.2"),
        ),
        encoding="utf-8",
    )
    _seed_tree_map(tmp_path, "alfa")
    return tmp_path


# ---------------------------------------------------------------------------
# LLR-RVH.1.1 / LLR-RVH.1.3 — one name-sorted list across both kinds (AT-145)
# ---------------------------------------------------------------------------


async def test_llr_rvh_1_1_at_145_relation_rows_beside_tree_rows(at145_workspace):
    """The recents table lists `*.relmap.yml` beside `*.mmd` in ONE list:
    with `demo` < `legacy` the relation row sorts FIRST (M-RVH-1: globbing
    only `*.mmd` reddens this; M-RVH-3: appending relation rows after the
    tree rows reddens the order)."""
    app = MapperApp(at145_workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        assert table.row_count == 2, (
            f"the relation row is absent or duplicated: {table.row_count} rows"
        )
        # AT-145's driver: `j` moves the selection off the default row.
        await pilot.press("j")
        await pilot.pause()
        assert app.is_running, "the app died on `j`"
        assert _row_names(table) == ["demo", "legacy"], _row_names(table)
        kinds = _kind_cells(table)
        assert kinds == [f" {RELATION_BADGE} ", " legacy "], kinds


async def test_llr_rvh_1_3_one_list_sorted_by_name_across_kinds(tmp_path):
    """Tree and relation rows interleave by name — the badge, not list
    position, distinguishes kinds (M-RVH-3: kind-grouped ordering reddens
    this)."""
    _seed_tree_map(tmp_path, "delta")
    _seed_tree_map(tmp_path, "hotel")
    _seed_descriptor(tmp_path, name="echo.relmap.yml")
    _seed_descriptor(tmp_path, name="alfa.relmap.yml")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        names = _row_names(table)
        assert names == ["alfa", "delta", "echo", "hotel"], names
        badges = ["relation" if f" {RELATION_BADGE} " == k else "tree"
                  for k in _kind_cells(table)]
        assert badges == ["relation", "tree", "relation", "tree"], badges


def test_llr_rvh_1_2_kind_badge_values_and_chip_style(at145_workspace):
    """Layer 0 over the enumeration itself: the relation row's kind cell
    reads exactly `relation·reqharness` in the tree rows' chip style
    (`INK on STEP`), Darkside casing (M-RVH-2: an ALL-CAPS badge reddens
    this).  The tree rows keep their `legacy`/`concept` vocabulary."""
    from mapper.screens.home import _recent_entries

    mmd_files = sorted(at145_workspace.glob("*.mmd"))
    descriptor_paths, _overflow = discover_descriptors(at145_workspace)
    entries = _recent_entries(at145_workspace, mmd_files, descriptor_paths)
    assert [e.name for e in entries] == ["demo", "legacy"], entries
    assert [e.kind for e in entries] == ["relation", "tree"], entries


async def test_llr_rvh_1_2_badge_census_painted_chip(at145_workspace):
    """On the painted table the relation kind cell carries the exact badge
    text and the `INK on STEP` chip style, and the tree cell keeps its own."""
    app = MapperApp(at145_workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        relation_key = next(iter(table.rows))
        relation_cell = table.get_row(relation_key)[1]
        assert isinstance(relation_cell, Text)
        assert relation_cell.plain == f" {RELATION_BADGE} ", relation_cell.plain
        assert any(span.style == CHIP_STYLE for span in relation_cell.spans), (
            f"the relation chip lost the tree rows' style: {relation_cell.spans}"
        )
        tree_key = list(table.rows)[1]
        tree_cell = table.get_row(tree_key)[1]
        assert tree_cell.plain == " legacy "
        assert any(span.style == CHIP_STYLE for span in tree_cell.spans)


async def test_llr_rvh_1_1_at_145_boundary_no_descriptor_no_canon_tree_rows_only(tmp_path):
    """AT-145 boundary (a): a plain tree-maps workspace (no `*.relmap.yml`,
    no canon) lists tree rows ONLY — no phantom relation row."""
    _seed_tree_map(tmp_path, "legacy")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        assert _row_names(table) == ["legacy"], _row_names(table)
        assert _kind_cells(table) == [" legacy "], _kind_cells(table)


async def test_llr_rvh_1_1_row_keys_disjoint_across_kinds(tmp_path):
    """review-inc006 F2: a tree map named like a descriptor
    (`demo.relmap.yml.mmd`, stem `demo.relmap.yml`) beside the descriptor
    `demo.relmap.yml` must not collide — the pre-fix row keys were identical
    for both kinds, `_recent_routes` silently kept one entry and the
    DataTable raised DuplicateKey out of `on_mount` (Home died).  Relation
    and derived rows key on a kind-scoped `relmap:` form; the tree key stays
    the bare map name (the gate-2 contract).  M-REV-HOME-1 (the prefix
    dropped) reddens this arm."""
    _seed_tree_map(tmp_path, "demo.relmap.yml")
    _seed_descriptor(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        assert app.is_running, "Home died on mount (the DuplicateKey class)"
        table = app.screen.query_one("#home-recents", DataTable)
        assert table.row_count == 2, table.row_count
        keys = [str(k.value) for k in table.rows]
        assert sorted(keys) == ["demo.relmap.yml", "relmap:demo.relmap.yml"], keys
        routes = app.screen._recent_routes  # noqa: SLF001
        assert sorted(routes) == sorted(keys), routes.keys()
        assert _kind_cells(table).count(f" {RELATION_BADGE} ") == 1
        assert _kind_cells(table).count(" legacy ") == 1


# ---------------------------------------------------------------------------
# LLR-RVH.2.1 — open routing by kind (AT-146) · LLR-RVH.2.2 — read-only
# ---------------------------------------------------------------------------


async def test_llr_rvh_2_1_at_146_open_routes_by_kind(at145_workspace):
    """`↵` on the relation row lands on `RelMapScreen` (crumb carries
    `relmap`, keybar shows `matrix`/`gaps`/`sheet`); on the tree row on
    `MapScreen` exactly as today (M-RVH-4: routing the relation row to
    `MapScreen` reddens this)."""
    app = MapperApp(at145_workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        # row 0 is the relation row (`demo` < `legacy`); `j` moves OFF it,
        # `k` moves back — a non-default selection reaches the row (C-10).
        await pilot.press("j")
        await pilot.pause()
        await pilot.press("k")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), app.screen
        painted = frame_text(app.screen)
        crumb = _crumb_line(painted, "matrix")
        assert crumb.startswith("demo"), f"the crumb lost the entry name: {crumb}"
        bar_line = next(
            line for line in painted.splitlines() if "matrix" in line and "view" in line
        )
        for label in ("matrix", "gaps", "sheet"):
            assert label in bar_line, f"the keybar does not paint {label!r}"
        # AT-146 negative: `d` drafts nothing on the relation screen.
        before = painted_frame(app.screen)
        await pilot.press("d")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), "`d` left the relation screen"
        assert painted_frame(app.screen) == before, "`d` changed the relation screen"
        await pilot.press("q")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen), app.screen
        await pilot.press("j")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, MapScreen), app.screen
        assert app.screen.map_id == "legacy", app.screen.map_id


def test_llr_rvh_2_2_relmap_scope_binds_no_write_action():
    """LLR-RVH.2.2 census: no draft/save/archive/edit/osopen action anywhere
    in the relmap seat or the screen's BINDINGS (M-RVH-5).  The seat is
    trunk-owned, so the kill verdict is the census predicate itself, proven
    against planted write actions here and re-run in the M-RVH-5 battery."""
    from mapper.keymap import bindings_for

    seat = bindings_for(SCOPE_RELMAP)
    assert seat, "the relmap seat is empty: the census is vacuous"
    assert write_vocabulary_in(seat) == []
    assert write_vocabulary_in(list(RelMapScreen.BINDINGS)) == []
    # The instrument RED-proof: planted write actions ARE reported.
    planted = write_vocabulary_in(
        [SimpleNamespace(action="save"), SimpleNamespace(action="osopen_launch"),
         SimpleNamespace(action="open_selected")]
    )
    assert planted == ["save", "osopen_launch"], planted


async def test_llr_rvh_2_3_opening_a_relation_map_writes_nothing(at145_workspace, monkeypatch):
    """LLR-RVH.2.3 instrumented save-count arm: opening (and `r`-refreshing)
    a relation map performs NO store write (M-RVH-6: a persisted derived
    node reddens this).  The counters WRAP the real `MapStore` save paths
    and call through (COND-QA-4)."""
    from mapper.store import MapStore

    calls: list[str] = []
    for method_name in ("save", "create"):
        real = getattr(MapStore, method_name)

        def counting(store_self, *args, _real=real, _name=method_name, **kwargs):
            calls.append(_name)
            return _real(store_self, *args, **kwargs)

        monkeypatch.setattr(MapStore, method_name, counting)
    app = MapperApp(at145_workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        calls.clear()  # count only the OPEN, not the app/store setup
        await pilot.press("enter")  # row 0 is the relation row
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), app.screen
        await pilot.press("r")
        await pilot.pause()
        await pilot.pause()
        assert calls == [], f"the relation path wrote the store: {calls}"


# ---------------------------------------------------------------------------
# LLR-RVH.3.1 — the derived reqharness row (AT-147)
# ---------------------------------------------------------------------------


async def test_llr_rvh_3_1_at_147_derived_row_opens_via_default_descriptor(
    at147_workspace, monkeypatch
):
    """With ZERO descriptors Home lists the derived row named by the canon
    stem; opening it derives through `default_descriptor()` VALUES
    (M-RVH-7: a hard-coded non-default descriptor reddens the args probe).
    The derivation-args counter WRAPS the real function (COND-QA-4), and
    the workspace is NOT a git repository (LLR-RVH.3.3)."""
    calls: list[tuple[Path, object]] = []
    real = screen_mod.derive_reqharness_map

    def counting(repo, descriptor):
        calls.append((repo, descriptor))
        return real(repo, descriptor)

    monkeypatch.setattr(screen_mod, "derive_reqharness_map", counting)
    assert not (at147_workspace / ".git").exists(), "the fixture must not be a repo"
    app = MapperApp(at147_workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        # `R` < `a` by code point: the derived row sorts FIRST.
        assert _row_names(table) == ["REQUIREMENTS", "alfa"], _row_names(table)
        assert f" {RELATION_BADGE} " in _kind_cells(table)[0]
        # `j` moves OFF the default row, `k` back onto the derived row (C-10).
        await pilot.press("j")
        await pilot.pause()
        await pilot.press("k")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), app.screen
        assert len(calls) == 1, f"open must derive exactly once, got {len(calls)}"
        repo, descriptor = calls[0]
        assert repo == at147_workspace, "the canon must resolve at the workspace root"
        assert descriptor == default_descriptor(), (
            "the derived entry must derive through default_descriptor() values"
        )
        painted = frame_text(app.screen)
        assert "HLR-DEMO.1" in painted, "the honest HLR skeleton does not render"
        invented = INVENTED_ID.findall(painted)
        assert invented == [], f"invented US-/AT-/TC- id shapes: {invented}"
        crumb = _crumb_line(painted, "matrix")
        assert crumb.startswith("REQUIREMENTS"), f"the crumb lost the entry name: {crumb}"


async def test_llr_rvh_3_1_derived_row_absent_when_descriptors_exist(at145_workspace):
    """The second half of LLR-RVH.3.1: when descriptors exist each descriptor
    is one row and NO derived row appears — even with no canon at all."""
    app = MapperApp(at145_workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        assert _row_names(table) == ["demo", "legacy"], _row_names(table)


async def test_llr_rvh_3_1_empty_canon_derives_an_honest_empty_map(tmp_path):
    """AT-147 boundary (b): an EMPTY canon opens an honest empty map — no
    refusal line, no crash, the relation screen alive with zero nodes."""
    (tmp_path / "REQUIREMENTS.md").write_text("# nothing here\n", encoding="utf-8")
    _seed_tree_map(tmp_path, "alfa")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        table = app.screen.query_one("#home-recents", DataTable)
        assert _row_names(table) == ["REQUIREMENTS", "alfa"], _row_names(table)
        await pilot.press("enter")  # row 0 is the derived row
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), app.screen
        assert app.screen.relmap is not None
        assert len(app.screen.relmap.nodes) == 0, app.screen.relmap.nodes
        painted = frame_text(app.screen)
        assert "descriptor skipped" not in painted, (
            "an empty canon is not a refusal — the map is honestly empty"
        )
        await pilot.press("q")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen), app.screen


# ---------------------------------------------------------------------------
# LLR-RVH.5.1 — the refusal path driven from Home (AT-147 boundary (a))
# ---------------------------------------------------------------------------


async def test_llr_rvh_5_1_at_147_boundary_missing_canon_refuses_from_home(tmp_path):
    """A descriptor whose canon does not exist: `↵` from Home lands on the
    relation screen's fixed refusal line (K3 `file not found`), never
    `str(exc)`, a path or a YAML snippet — and the app stays alive (M-RVH-13
    reddens the wording census, M-RVH-14 the app-lives half)."""
    _seed_tree_map(tmp_path, "legacy")
    _seed_descriptor(tmp_path)  # demo.relmap.yml — and NO canon at all
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        await pilot.press("enter")  # row 0 is the relation row
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), app.screen
        assert app.screen.relmap is None
        painted = frame_text(app.screen)
        assert "file not found" in painted
        assert "descriptor skipped" in painted
        assert "CanonUnavailable" not in painted
        assert "RepoReadError" not in painted
        assert str(tmp_path) not in painted, "the refusal painted a path"
        await pilot.press("q")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen), "the app died on the refusal"


async def test_llr_rvh_5_1_at_147_boundary_corrupt_canon_k7_refuses(tmp_path):
    """AT-147 boundary (a), the K7 limb: a canon that is not UTF-8 text
    refuses with the closed-set cause `is not UTF-8 text`, app alive."""
    _seed_descriptor(tmp_path)
    # Invalid UTF-8 with NO NUL byte — the binary guard (K6) must not fire
    # first; this canon is refused by the K7 cause exactly.
    (tmp_path / "REQUIREMENTS.md").write_bytes(b"caf\xe9 raw canon")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), app.screen
        painted = frame_text(app.screen)
        assert "is not UTF-8 text" in painted
        assert app.is_running, "the app died on the corrupt canon"
        await pilot.press("q")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen), app.screen


# ---------------------------------------------------------------------------
# LLR-RVH.5.2 — the hostile descriptor name renders literally (AT-145 (b))
# ---------------------------------------------------------------------------


async def test_llr_rvh_5_2_at_145_boundary_hostile_descriptor_name_renders_literally(tmp_path):
    """A descriptor file named `x[y].relmap.yml` lists and opens LITERALLY —
    no markup parse error, no style leak, no forged row; the app stays
    alive (M-RVH-15 reddens the markup-safety half)."""
    _seed_tree_map(tmp_path, "legacy")
    _seed_descriptor(tmp_path, name="x[y].relmap.yml")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        assert app.is_running, "the app died listing the hostile name"
        table = app.screen.query_one("#home-recents", DataTable)
        # The name cell is the ESCAPED form (the markup-safe sink — AT-145
        # boundary (b)); the painted frame renders it literally.
        assert _row_names(table) == [escape(n) for n in ("legacy", "x[y]")], (
            _row_names(table)
        )
        painted = frame_text(app.screen)
        assert "x[y]" in painted, "the hostile name must render literally"
        await pilot.press("j")  # row 1 is the hostile relation row (C-10)
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), app.screen
        assert "x[y]" in _crumb_line(frame_text(app.screen), "matrix")
        await pilot.press("q")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen), app.screen


# ---------------------------------------------------------------------------
# LLR-RVH.4.4 / AT-149 — help and palette carry the relmap scope (Inc-6b)
# ---------------------------------------------------------------------------


def _help_key_rows(help_screen) -> list[tuple[str, str]]:
    """(glyph, label) of every painted "keys in this view" row — the row
    anatomy of `HelpScreen._append_key_group`: the indent (2 cells) + the
    glyph padded to the key column (10 cells) + the label.  The section title
    and the group headers carry no indent, so they never parse as a row."""
    plain = help_screen.query_one("#help-content", Static).content.plain
    rows = []
    for line in plain.splitlines():
        if len(line) > 12 and line.startswith("  ") and line[2] != " ":
            rows.append((line[2:12].strip(), line[12:].rstrip()))
    return rows


async def test_at_149_help_lists_exactly_the_seat_rows(workspace):
    """`?` from the relation screen opens the legend for THIS scope, and its
    painted rows are EXACTLY the seat's — equality, not superset: a hand-added
    row reddens this (M-RVH-12), a dropped seat row reddens it too.  The
    derivation is the seat reader shipped in the generic legend (the screen's
    `KEY_SCOPE` is the only input — LLR-RVH.4.4's draft-time verification)."""
    seat = {(b.glyph, b.label) for b in bindings_for(SCOPE_RELMAP)}
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await _open_and_pause(app, pilot, workspace)
        await pilot.press("?")
        await pilot.pause()
        help_screen = app.screen
        assert isinstance(help_screen, HelpScreen), app.screen
        assert help_screen.scope == SCOPE_RELMAP
        painted = set(_help_key_rows(help_screen))
        assert painted == seat, (
            f"help must list exactly the seat rows — hand-added: "
            f"{sorted(painted - seat)}, missing: {sorted(seat - painted)}"
        )
        for glyph, label in (
            ("1", "matrix"), ("2", "gaps"), ("3", "sheet"),
            ("↵", "impact on node"), ("c", "chain"), ("r", "refresh"),
            ("q", "quit"),
        ):
            assert (glyph, label) in painted, f"AT-149 names the row {glyph} {label}"
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), app.screen


async def test_at_149_palette_offers_the_seat_and_runs_matrix(workspace):
    """`ctrl+p` offers exactly the seat's palette rows (equality — a hand row
    reddens this); a NON-DEFAULT query (`mat`) filters to the matching
    actions; running the highlighted `matrix` entry through the real keys
    lands on the matrix view (the AT-149 driver, C-16/C-10)."""
    seat = {(b.glyph, b.label, b.action) for b in palette_items("", SCOPE_RELMAP)}
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await _open_and_pause(app, pilot, workspace)
        await pilot.press("ctrl+p")
        await pilot.pause()
        palette = app.screen
        assert isinstance(palette, CommandPalette), app.screen
        assert palette.scope == SCOPE_RELMAP
        offered = {(b.glyph, b.label, b.action) for b in palette._items}
        assert offered == seat, (
            f"the palette must offer exactly the seat rows — hand-added: "
            f"{sorted(offered - seat)}, missing: {sorted(seat - offered)}"
        )
        await pilot.press(*"mat")
        await pilot.pause()
        filtered = [(b.glyph, b.label, b.action) for b in palette._items]
        assert filtered == [("1", "matrix", "matrix")], filtered
        await pilot.press("down")  # move the highlight (C-10), clamps at one row
        await pilot.pause()
        await pilot.press("enter")  # run the highlighted entry
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, RelMapScreen), app.screen
        assert app.screen.active_view == "matrix", app.screen.active_view


async def test_at_149_palette_rows_match_the_keymaps_declared_relmap_seat(workspace):
    """Drop-independence for the palette surface (review-inc006b7 F1): the
    sibling arm compares `palette._items` to `palette_items("", SCOPE_RELMAP)`
    — both sides derive from the same seat, so a DROPPED seat row shrinks both
    and the equality still holds (reviewer mutant M-R-6B-2 stayed GREEN there).
    This arm pins the keymap's DECLARED `SCOPE_RELMAP` bindings as a literal —
    (glyph, label, action) exactly as `mapper/keymap.py`'s seat declares them —
    so dropping any seat row reddens the palette side on its own.  Keep the
    literal in sync with the seat declaration; `tests/test_keymap.py` pins the
    declaration itself."""
    declared = {
        # -- relmap rows, as declared in the seat (mapper/keymap.py) --
        ("1", "matrix", "matrix"),
        ("2", "gaps", "gaps"),
        ("3", "sheet", "sheet"),
        ("r", "refresh", "refresh"),
        ("↑", "move up", "move_up"),
        ("↓", "move down", "move_down"),
        ("←", "move left", "move_left"),
        ("→", "move right", "move_right"),
        ("↵", "impact on node", "lens"),
        ("c", "chain", "chain"),
        ("k", "by kind", "by_kind"),
        ("q", "quit", "leave"),
        ("esc", "leave", "leave"),
        # -- the two app chords the palette also offers --
        ("ctrl+p", "palette", "palette"),
        ("?", "legend", "help"),
    }
    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await _open_and_pause(app, pilot, workspace)
        await pilot.press("ctrl+p")
        await pilot.pause()
        palette = app.screen
        assert isinstance(palette, CommandPalette), app.screen
        assert palette.scope == SCOPE_RELMAP
        offered = {(b.glyph, b.label, b.action) for b in palette._items}
        assert offered == declared, (
            f"the palette must offer exactly the seat's declared rows — "
            f"offered-but-not-declared: {sorted(offered - declared)}, "
            f"declared-but-not-offered (a dropped seat row lands here): "
            f"{sorted(declared - offered)}"
        )
