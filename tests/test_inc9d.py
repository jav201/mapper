"""Inc-9d -- security and defects the Inc-9b/9c reviews found.

Authority: `.dev-flow/2026-08-26-ui-next-batch-02/VERDICT-inc9-2026-09-30.md`
(Round 2, Inc-9d).  Every arm was committed RED first, as a STRICT xfail keyed by
the step that closes it (`OPEN_STEPS`); each implementation commit deletes its own
step from that set, and an arm that then fails is a failure, not an xfail.

The operator's own words (`L4`, `INC9BC-UX-F3`) are a literal table -- the ruling
is the specification.  Everything else is derived at run time.  The user profile
is read from the environment at run time and is NEVER printed: a failure message
carries a redacted toast, not the path.  No user-profile path is typed literally
(`tests/test_no_operator_paths.py`, `A-110`).
"""
from __future__ import annotations

import dataclasses
import os
import pathlib
import subprocess
import types

import pytest
from textual.widgets import DataTable, Input, Static

from mapper import keymap
from mapper.app import HomeScreen, MapperApp, MapScreen, RepoScreen, _PromptScreen
from mapper.github import GitHubError, _ensure_cloned, _repo_name_from_url
from mapper.model import Document, Ficha, Graph, Node
from mapper.screens.factory import FactoryScreen
from mapper.store import MapStore
from mapper.widgets.chrome import HintLine
from tests.test_inc9c import PROFILE, _boom, _notify_leaks, _office_fixture
from tests.test_no_operator_paths import USER_PROFILE_PATH
from tests.test_repair_layout import _frame_rows, _rows_in, _tree

#: Steps not yet implemented.  An arm keyed to a step in this set is a strict xfail.
OPEN_STEPS: set[str] = {"github", "worker", "hint", "header", "sentinel"}


def red(step: str):
    if step not in OPEN_STEPS:
        return lambda fn: fn
    return pytest.mark.xfail(
        strict=True, reason=f"Inc-9d: committed RED; closed by the '{step}' step")


SIZE = (118, 34)
NARROW = (87, 34)

#: `L4`, the operator's ruling, verbatim.
FACTORY_HINT = "d edit document · i import office file · g generate office file"
#: `INC9BC-UX-F3`: the map's resting hint.
MAP_HINT = "j/k/h/l move · ↵ open card · / search"


def _text(widget: Static) -> str:
    content = widget.content
    return getattr(content, "plain", str(content))


def _profile() -> str:
    return os.environ.get("USERPROFILE") or str(pathlib.Path.home())


def _redact(text: str) -> str:
    """A failure message may quote a toast; it may not quote the profile."""
    profile = _profile()
    account = pathlib.Path(profile).name
    out = text.replace(profile, "<profile>")
    return out.replace(account, "<account>") if len(account) >= 3 else out


def _leaks_the_profile(joined: str) -> bool:
    profile, low = _profile().lower(), joined.lower()
    account = pathlib.Path(profile).name
    return (profile in low or USER_PROFILE_PATH.search(joined) is not None
            or (len(account) >= 3 and account in low))


def _no_profile(toasts: list[str], *extra: str) -> None:
    joined = "\n".join(toasts)
    leaked = _leaks_the_profile(joined)
    assert not leaked, f"a toast paints the user profile: {_redact(joined)!r}"
    for path in extra:
        assert path not in joined, f"a toast paints {_redact(path)!r}: {_redact(joined)!r}"
    assert PROFILE not in joined and "<operator>" not in joined


async def _open_factory(app, pilot, tmp_path):
    app.notify = lambda msg, **kw: TOASTS.append(str(msg))
    app.push_screen(_office_fixture(app, tmp_path))
    for _ in range(3):
        await pilot.pause()
    return app.screen


TOASTS: list[str] = []


@pytest.fixture(autouse=True)
def _clear_toasts():
    TOASTS.clear()
    yield
    TOASTS.clear()


# ---------------------------------------------------------------------------
# INC9BC-SEC-F1 / B-77a -- the not-found toast paints the file NAME only

@red("factory")
async def test_inc9d_sec_f1_a_missing_tilde_path_paints_no_profile_path(tmp_path):
    """Typed through the real keys: `~` expands to the profile, and the toast used
    to echo the expansion.  Built from `$USERPROFILE` at run time, never printed."""
    typed = "~/zz-inc9d-missing.docx"
    if pathlib.Path(typed).expanduser().exists():
        pytest.skip("the probe file exists in this profile")
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _open_factory(app, pilot, tmp_path)
        await pilot.press("i")
        await pilot.pause()
        assert isinstance(app.screen, _PromptScreen)
        await pilot.press(*typed)
        await pilot.press("enter")
        for _ in range(3):
            await pilot.pause()
    assert TOASTS, "the import path fired no toast -- the driver proves nothing"
    _no_profile(TOASTS, str(tmp_path))
    assert "zz-inc9d-missing.docx" in "\n".join(TOASTS), _redact("\n".join(TOASTS))


@red("factory")
def test_inc9d_sec_f1_no_factory_notify_interpolates_a_bare_path():
    """The census: `LEAK_EXCEPTIONS` no longer excuses `source` in factory.py."""
    leaks, dynamic = _notify_leaks()
    assert dynamic > 10
    factory = [(n, e) for p, n, e in leaks if p == "mapper/screens/factory.py"]
    assert factory == [], factory


# ---------------------------------------------------------------------------
# INC9BC-UX-F6 / L4 -- the factory hint is the three actions, on one row

@red("factory")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9d_l4_the_factory_hint_is_the_three_actions_on_one_row(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open_factory(app, pilot, tmp_path)
        hint = screen.query_one(HintLine)
        rows = _rows_in(screen, hint.region)
    assert hint.text == FACTORY_HINT, hint.text
    assert len(rows) == 1, rows
    assert FACTORY_HINT in rows[0], rows
    derived = " · ".join(keymap.hint_pair(keymap.SCOPE_FACTORY, a)
                         for a in ("edit_doc", "import_office", "generate_office"))
    assert derived == FACTORY_HINT, derived


# ---------------------------------------------------------------------------
# INC9BC-SEC-F4 -- the office import's copy degrades to a toast

@red("factory")
async def test_inc9d_sec_f4_a_failing_copy_is_a_toast_not_a_crash(tmp_path, monkeypatch):
    source = tmp_path / "elsewhere" / "plantilla-nueva.docx"
    source.parent.mkdir()
    source.write_bytes(b"x")
    monkeypatch.setattr("shutil.copy2", _boom)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = await _open_factory(app, pilot, tmp_path)
        before = dict(screen.graph.documents)
        await pilot.press("i")
        await pilot.pause()
        app.screen.query_one("#prompt-input", Input).value = str(source)
        await pilot.press("enter")
        for _ in range(3):
            await pilot.pause()
        assert app.is_running and isinstance(app.screen, FactoryScreen)
        assert screen.graph.documents == before, "a failed import still registered a document"
    assert TOASTS, "the failed copy fired no toast"
    _no_profile(TOASTS, str(tmp_path), str(source))
    joined = "\n".join(TOASTS)
    assert "plantilla-nueva.docx" in joined and "OSError" in joined, _redact(joined)


# ---------------------------------------------------------------------------
# INC9BC-SEC-F3 -- a failed clone names the repo and the class, never a local path

class _GitRun:
    """A `subprocess.run` that answers `git clone` the way git does: failing, with
    a stderr that names the absolute target."""

    def __init__(self, real, *, returncode=128):
        self.real, self.returncode, self.calls = real, returncode, []

    def __call__(self, argv, *a, **kw):
        if list(argv)[:3] == ["git", "clone", "--mirror"]:
            self.calls.append(list(argv))
            target = argv[-1]
            return subprocess.CompletedProcess(
                argv, self.returncode, "",
                f"Cloning into bare repository '{target}'...\n"
                f"fatal: unable to access '{argv[-2]}': Could not resolve host\n")
        return self.real(argv, *a, **kw)


@red("github")
def test_inc9d_sec_f3_a_failed_clone_message_carries_no_local_path(tmp_path, monkeypatch):
    cache = tmp_path / "home" / ".cache" / "mapper" / "repos"
    monkeypatch.setattr("subprocess.run", _GitRun(subprocess.run))
    with pytest.raises(GitHubError) as caught:
        _ensure_cloned("https://example.invalid/owner/widget.git", cache)
    message = str(caught.value)
    assert "widget" in message, message
    assert str(cache) not in message and str(tmp_path) not in message, _redact(message)
    assert "Cloning into" not in message and "128" in message, _redact(message)
    assert not _leaks_the_profile(message), "the message paints the user profile"


# ---------------------------------------------------------------------------
# B-77b -- a URL's last segment may not leave the cache

@red("github")
@pytest.mark.parametrize("url", [
    "https://example.invalid/owner/..",
    "https://example.invalid/owner/../",
    "https://example.invalid/owner/.",
    "https://example.invalid/owner/..git",
    "https://example.invalid/",
    "https://example.invalid/owner/...",
    "https://example.invalid/owner/C:evil",
    "https://example.invalid/owner/a\\b",
    "git@example.invalid:owner/..",
])
def test_inc9d_b77b_a_dot_or_separator_segment_is_refused(url):
    with pytest.raises(GitHubError):
        _repo_name_from_url(url)


def test_inc9d_b77b_an_ordinary_url_still_names_its_repo():
    assert _repo_name_from_url("https://example.invalid/owner/widget.git") == "widget"
    assert _repo_name_from_url("https://example.invalid/owner/widget/") == "widget"
    assert _repo_name_from_url("git@example.invalid:owner/widget.git") == "widget"


@red("github")
@pytest.mark.parametrize("tail", ["..", "../", "."])
def test_inc9d_b77b_the_cache_parent_is_unchanged_after_a_dotdot_attempt(
        tmp_path, monkeypatch, tail):
    """A stand-in for `git clone --mirror` that, like git, fills its target.  On a
    `..` segment the target IS the cache's parent, so a run that reaches the clone
    changes the parent; a refusal leaves it byte-identical.  Temp home only."""
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    cache = tmp_path / ".cache" / "mapper" / "repos"
    cache.mkdir(parents=True)
    parent = cache.parent
    (parent / "keep.txt").write_text("keep", encoding="utf-8")

    def snapshot():
        return sorted((str(p.relative_to(parent)), p.stat().st_size)
                      for p in parent.rglob("*"))

    real = subprocess.run

    def fake(argv, *a, **kw):
        if list(argv)[:3] == ["git", "clone", "--mirror"]:
            target = pathlib.Path(argv[-1])
            target.mkdir(parents=True, exist_ok=True)
            (target / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
            return subprocess.CompletedProcess(argv, 0, "", "")
        return real(argv, *a, **kw)

    monkeypatch.setattr("subprocess.run", fake)
    before = snapshot()
    refused = False
    try:
        _ensure_cloned(f"https://example.invalid/owner/{tail}", cache)
    except GitHubError:
        refused = True
    assert snapshot() == before, "the clone wrote into the cache's parent"
    assert refused, "the dot segment was not refused"


# ---------------------------------------------------------------------------
# INC9BC-SEC-F3, second half -- the repo worker's failure is the intended toast

@red("worker")
async def test_inc9d_sec_f3_a_failing_fetch_is_a_toast_and_the_app_stays_up(
        tmp_path, monkeypatch):
    """Through the REAL `@work(thread=True)` worker and the real connector: only
    the `git clone` is stubbed, with a stderr that names the target path."""
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("subprocess.run", _GitRun(subprocess.run))
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.notify = lambda msg, **kw: TOASTS.append(str(msg))
        app.push_screen(RepoScreen("https://example.invalid/owner/widget.git"))
        for _ in range(12):
            await pilot.pause()
            if TOASTS:
                break
        await pilot.pause()
        assert app.is_running, "the worker failure exited the app"
        assert isinstance(app.screen, RepoScreen)
    assert TOASTS, "the failed fetch fired no toast"
    _no_profile(TOASTS, str(tmp_path))
    assert "widget" in "\n".join(TOASTS), _redact("\n".join(TOASTS))


# ---------------------------------------------------------------------------
# INC9BC-UX-F3 -- the map's resting hint

@red("hint")
async def test_inc9d_ux_f3_the_map_rests_on_the_english_move_hint(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.push_screen(MapScreen(_tree(app)))
        for _ in range(3):
            await pilot.pause()
        hint = app.screen.query_one(HintLine)
    assert hint.text == MAP_HINT, hint.text


# ---------------------------------------------------------------------------
# INC9BC-UX-F13 -- the recents header is painted once, however often home returns

@red("header")
async def test_inc9d_ux_f13_the_recents_header_is_one_row_after_three_returns(tmp_path):
    _tree(types.SimpleNamespace(store=MapStore(tmp_path)))
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)
        for _ in range(3):
            await pilot.press("enter")
            for _ in range(2):
                await pilot.pause()
            assert isinstance(app.screen, MapScreen)
            await pilot.press("q")
            for _ in range(2):
                await pilot.pause()
            assert isinstance(app.screen, HomeScreen)
        table = app.screen.query_one("#home-recents", DataTable)
        labels = [c.label.plain for c in table.columns.values()]
        painted = "\n".join(_frame_rows(app.screen))
    assert labels == ["▐ name", "kind", "nodos", "docs"], labels
    assert painted.count("▐ name") == 1, painted.count("▐ name")


# ---------------------------------------------------------------------------
# INC9BC-CR-F2 -- K3: the hints FOLLOW the seat (a sentinel, not the current value)

def _sentinel_seat(monkeypatch):
    seat = [dataclasses.replace(b, label=f"zz-{b.action}") for b in keymap.KEYMAP]
    monkeypatch.setattr(keymap, "KEYMAP", seat)
    return seat


@red("sentinel")
async def test_inc9d_cr_f2_every_k3_hint_follows_a_relabelled_seat(tmp_path, monkeypatch):
    """The K3 arms compare a hint with the seat's CURRENT value, so a hand-written
    copy that equals today's label passes them.  Relabel every seat row to
    `zz-<action>`, rebuild each hint, and require the sentinel inside it: a
    hand-written copy cannot contain a word it has never heard."""
    from mapper.app import _ImportPreviewScreen, map_hint
    from mapper.screens.factory import factory_hint

    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        graph = app.store.load(_tree(app))
        _sentinel_seat(monkeypatch)
        hints = {
            "factory": (factory_hint(), [("factory", a) for a in
                                         ("edit_doc", "import_office", "generate_office")]),
            "map": (map_hint(), [("map", "open_ficha"), ("map", "search")]),
        }
        imp = _ImportPreviewScreen(graph, pathlib.Path("nodos.csv"))
        app.push_screen(imp)
        await pilot.pause()
        hints["import"] = (imp.query_one(HintLine).text,
                           [("import", "save"), ("import", "home")])
        app.pop_screen()
        repo = RepoScreen("owner/name")
        hints["repo panel"] = (repo._sidebar_hints(), [
            ("repo", "next_sibling"), ("repo", "prev_sibling"), ("repo", "home"),
            ("app", "help")])
        for name, (text, pairs) in hints.items():
            assert pairs
            for scope, action in pairs:
                assert keymap.hint_pair(scope, action) in text, (name, scope, action, text)
                assert f"zz-{action}" in text, (name, action, text)
