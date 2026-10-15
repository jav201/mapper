"""Fixes batch increment 003: B-127 (the roles screen reads git off the UI thread).

HLR-FX.4 / LLR-FX.4.1-4.4 and the acceptance node AT-087, all driven through the
real app (`MapperApp` + `run_test` + `pilot.press`) with a gated
`identity._run_git`, and asserted on the PAINTED frame (C-32): the text the four
statics and the key bar render to, never the arguments of an `update()` call.
The failure seam is a monkeypatched function on `identity` that raises the
chosen type; no production seam exists.
"""
import asyncio
import hashlib
import subprocess
import threading
from types import SimpleNamespace

import pytest
from textual.screen import Screen
from textual.worker import WorkerState

from mapper import darkside
from mapper.app import HomeScreen, MapperApp
from mapper.keymap import SCOPE_ROLES, groups_for_keybar
from mapper.reqharness import identity
from mapper.reqharness.records import ValidationError
from mapper.screens.common import keybar_groups
from mapper.screens.roles import _NO_REPO_HINT, RolesScreen
from mapper.widgets.chrome import HintLine, KeyBar
from tests.test_roles_screen import (
    SUBJECT,
    _init_repo,
    _pending_files,
    _plain,
    _render_text,
    _roles_sha,
    _seed_team,
    _set_identity,
)

SIZE = (118, 34)
#: What the composed (empty) hint line paints: the chrome with no text.
EMPTY = ("", "", "", darkside.hint_line("").plain)
SURFACES = ("roles-status", "roles-body", "roles-band")
EDIT_LABELS = ("propose change", "approve", "reject")
NAV_LABELS = ("next person", "previous person", "next role", "previous role")


class _Gate:
    """Wraps `identity._run_git`: records every call with whether it ran on the
    main thread, and blocks it on `event` (5 s guard: the base tree runs the
    first call on the main thread, which would otherwise deadlock the test)."""

    def __init__(self, real, *, closed: bool) -> None:
        self.real = real
        self.event = threading.Event()
        if not closed:
            self.event.set()
        self.calls: list[tuple[tuple[str, ...], bool]] = []

    def __call__(self, repo, tail):
        self.calls.append(
            (tuple(tail), threading.current_thread() is threading.main_thread()))
        assert self.event.wait(5), "gate never released"
        return self.real(repo, tail)


def _seed(tmp_path) -> None:
    env = _init_repo(tmp_path)
    _set_identity(tmp_path, env, SUBJECT)
    _seed_team(tmp_path, env)


def _install_gate(monkeypatch, *, closed: bool) -> _Gate:
    gate = _Gate(identity._run_git, closed=closed)
    monkeypatch.setattr(identity, "_run_git", gate)
    return gate


async def _until(predicate, what: str, limit: float = 4.0) -> None:
    for _ in range(int(limit / 0.02)):
        if predicate():
            return
        await asyncio.sleep(0.02)
    raise AssertionError(f"timed out waiting for {what}")


async def _settle(app, pilot) -> None:
    await app.workers.wait_for_complete()
    await pilot.pause()


def _painted(screen, widget) -> str:
    """The text a chrome widget (hint line, key bar) paints."""
    return screen.query_one(widget).render().plain


def _frame(screen) -> tuple[str, str, str, str]:
    status, body, band = (_render_text(screen, sid, SIZE[0]) for sid in SURFACES)
    return status, body, band, _painted(screen, HintLine)


def _bar(screen) -> str:
    return _painted(screen, KeyBar)


def _digest(root) -> tuple[str, tuple[tuple[str, str], ...]]:
    pending = tuple(
        (p.name, hashlib.sha256(p.read_bytes()).hexdigest())
        for p in _pending_files(root))
    return _roles_sha(root), pending


# ---------------------------------------------------------------------------
# AT-087 and LLR-FX.4.1 — the three git calls run off the UI thread
# ---------------------------------------------------------------------------


async def test_at_087_roles_screen_git_reads_run_off_the_ui_thread(
        tmp_path, monkeypatch):
    _seed(tmp_path)
    gate = _install_gate(monkeypatch, closed=True)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("R")
        await pilot.pause()  # control returns while git is gated
        assert isinstance(app.screen, RolesScreen)
        await _until(lambda: len(gate.calls) >= 1, "a git call")
        assert all(not on_main for _, on_main in gate.calls), gate.calls
        blank = _frame(app.screen)
        assert blank == EMPTY, blank  # blank while git is read

        gate.event.set()
        await _settle(app, pilot)
        status, body, band, hint = _frame(app.screen)

    assert "chain" in status and "viewer subject" in status, status
    assert "✓ verified" in status, status
    assert "reviewer-2" in body, body
    assert "release ready" in band, band
    assert "space" in hint, hint
    assert {tail for tail, _ in gate.calls} == {
        ("rev-parse", "--show-toplevel"),
        ("config", "--get", "user.name"),
        ("config", "--get", "user.email"),
    }
    assert all(not on_main for _, on_main in gate.calls), gate.calls


@pytest.mark.parametrize("target", ["repo_root", "read"])
@pytest.mark.parametrize("exc", [
    OSError("x"), ValueError("x"), subprocess.SubprocessError("x"),
    ValidationError("x"),
], ids=lambda e: type(e).__name__)
async def test_roles_discovery_failure_degrades_to_no_repo(
        tmp_path, monkeypatch, target, exc):
    _seed(tmp_path)

    def boom(*_a, **_k):
        raise exc

    monkeypatch.setattr(identity, target, boom)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("R")
        await _settle(app, pilot)
        status, body, band, hint = _frame(app.screen)

    assert "no repo" in status, status
    assert _NO_REPO_HINT in body, body
    assert "no repo" in band, band
    assert hint == darkside.hint_line(_NO_REPO_HINT).plain, hint


async def test_roles_unexpected_discovery_exception_is_not_swallowed(
        tmp_path, monkeypatch):
    _seed(tmp_path)

    def boom(*_a, **_k):
        raise RuntimeError("a defect")

    monkeypatch.setattr(identity, "repo_root", boom)
    app = MapperApp(tmp_path)
    with pytest.raises(Exception) as caught:
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            await pilot.press("R")
            await _settle(app, pilot)
            await pilot.pause()

    chain = []
    err = caught.value
    while err is not None:
        chain.append(err)
        err = err.__cause__ or err.__context__
    # Textual wraps a worker's exception in `WorkerFailed` (default exit_on_error)
    assert any("RuntimeError" in str(e) and "a defect" in str(e) for e in chain), chain


async def test_roles_popped_screen_discards_late_discovery(tmp_path, monkeypatch):
    _seed(tmp_path)
    gate = _install_gate(monkeypatch, closed=True)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("R")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, RolesScreen)
        await _until(lambda: len(gate.calls) >= 1, "a git call")
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)

        gate.event.set()
        await _settle(app, pilot)
        await pilot.pause()
        assert list(app._notifications) == []
        assert screen._facts is None  # nothing was applied to the dead screen
        # Textual cancels the dead screen's workers, so the framework alone
        # never delivers the late result.  The hand-back's own guard is the
        # owned behaviour: hand the dead screen a SUCCESS for its latest
        # generation and it must drop it (no paint, no exception).
        late = SimpleNamespace(
            state=WorkerState.SUCCESS,
            worker=SimpleNamespace(result=(screen._gen, (str(tmp_path), None))))
        screen.on_worker_state_changed(late)
        assert screen._facts is None
        assert isinstance(app.screen, HomeScreen)
        await pilot.press("R")  # the app still answers a following key
        await _settle(app, pilot)
        assert isinstance(app.screen, RolesScreen)
        assert "✓ verified" in _plain(app.screen, "roles-status")


# ---------------------------------------------------------------------------
# LLR-FX.4.2 — nothing wrong is painted while loading; the latest result wins
# ---------------------------------------------------------------------------


async def test_roles_paints_nothing_until_discovery_returns(tmp_path, monkeypatch):
    _seed(tmp_path)
    gate = _install_gate(monkeypatch, closed=True)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("R")
        await pilot.pause()
        await _until(lambda: len(gate.calls) >= 1, "a git call")
        before = _frame(app.screen)
        assert before == EMPTY, before
        gate.event.set()
        await _settle(app, pilot)
        after = _frame(app.screen)
    assert all(after), after


async def test_roles_resume_keeps_previous_paint(tmp_path, monkeypatch):
    _seed(tmp_path)
    gate = _install_gate(monkeypatch, closed=False)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("R")
        await _settle(app, pilot)
        painted = _frame(app.screen)
        assert "✓ verified" in painted[0]

        roles = app.screen
        await app.push_screen(Screen())
        await pilot.pause()
        gate.event.clear()
        n = len(gate.calls)
        app.pop_screen()
        await pilot.pause()
        assert app.screen is roles
        await _until(lambda: len(gate.calls) > n, "the resume discovery")
        assert _frame(roles) == painted  # the previous paint stays
        gate.event.set()
        await _settle(app, pilot)
        assert _frame(roles) == painted


async def test_roles_latest_discovery_wins(tmp_path, monkeypatch):
    _seed(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("R")
        await _settle(app, pilot)
        screen = app.screen
        assert "✓ verified" in _plain(screen, "roles-status")

        real = identity.repo_root
        events = [threading.Event(), threading.Event()]
        entered: list[int] = []

        def fake(repo):
            index = len(entered)
            entered.append(index)
            assert events[index].wait(5), "gate never released"
            return real(repo) if index == 0 else identity.NO_REPO

        monkeypatch.setattr(identity, "repo_root", fake)
        screen._start_discovery()  # the first discovery (stale once the next starts)
        await _until(lambda: len(entered) == 1, "the first discovery")
        screen._start_discovery()  # the second discovery (latest)
        await _until(lambda: len(entered) == 2, "the second discovery")

        events[1].set()  # the latest returns first: `no repo`
        await _until(lambda: "no repo" in _plain(screen, "roles-status"),
                     "the latest result to paint")
        events[0].set()  # the stale one returns later: verified, must be ignored
        await _settle(app, pilot)
        await pilot.pause()
        status = _plain(screen, "roles-status")

    assert "no repo" in status and "verified" not in status, status


# ---------------------------------------------------------------------------
# LLR-FX.4.3 — keys before the first load are inert; the key bar says so
# ---------------------------------------------------------------------------


async def test_roles_keys_before_first_load_are_inert(tmp_path, monkeypatch):
    _seed(tmp_path)
    gate = _install_gate(monkeypatch, closed=True)
    digests = _digest(tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("R")
        await pilot.pause()
        screen = app.screen
        await _until(lambda: len(gate.calls) >= 1, "a git call")
        before = _frame(screen)
        gated_bar = _bar(screen)
        for key in ("j", "space", "a", "r"):
            await pilot.press(key)
            await pilot.pause()
        assert _frame(screen) == before
        assert list(app._notifications) == []
        assert _digest(tmp_path) == digests  # 0 bytes written

        # the key bar advertises navigation and `Esc` only
        for label in NAV_LABELS:
            assert label in gated_bar, gated_bar
        assert "esc back" in gated_bar, gated_bar
        for label in EDIT_LABELS:
            assert label not in gated_bar, gated_bar

        gate.event.set()
        await _settle(app, pilot)
        released_bar = _bar(screen)

    expected = darkside.keybar(
        groups_for_keybar(keybar_groups(SCOPE_ROLES)), width=SIZE[0]).plain
    assert released_bar == expected, (released_bar, expected)
    assert "space propose change" in released_bar
    assert "esc back" not in released_bar  # folded into the overflow count


async def test_roles_escape_pops_while_gated(tmp_path, monkeypatch):
    _seed(tmp_path)
    gate = _install_gate(monkeypatch, closed=True)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("R")
        await pilot.pause()
        await _until(lambda: len(gate.calls) >= 1, "a git call")
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)
        gate.event.set()
        await _settle(app, pilot)


# ---------------------------------------------------------------------------
# LLR-FX.4.4 — keypress-time reloads read disk and run no git
# ---------------------------------------------------------------------------


async def test_roles_keypress_reload_runs_no_git(tmp_path, monkeypatch):
    _seed(tmp_path)
    gate = _install_gate(monkeypatch, closed=False)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("R")
        await _settle(app, pilot)
        before = len(gate.calls)
        assert before >= 3
        for key in ("space", "a", "r"):
            await pilot.press(key)
            await pilot.pause()
        assert len(gate.calls) == before, gate.calls[before:]
        # the reload still re-read the disk: the proposal landed as a chain event
        assert "applied" in _frame(app.screen)[3] or _pending_files(tmp_path)
