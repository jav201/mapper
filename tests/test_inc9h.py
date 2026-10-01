"""Inc-9h -- fixes for the defects the Inc-9g reviews found.

Authority: `A-116` (`INC9G-CR-F1` .. `F7`, `INC9G-UX-F1` .. `F3`, `INC9G-SEC-F1` .. `F5`, and
the operator's `P1` / `P2`, `VERDICT-inc9-2026-09-30.md` Round 5).  Every arm that a fix
closes was committed RED first, as a STRICT xfail keyed by the step that closes it
(`OPEN_STEPS`); each implementation commit deletes its own step from that set.  An arm that
is not keyed is a pin: green on the base, killed by its mutant instead (record section 4).

Nothing here reaches the network, the real cache or the real `gh`: every git or gh call is
stubbed, or (the `network`-marked arms) runs against LOCAL bare repositories under `tmp_path`
with HOME and USERPROFILE pointed at it.  No user-profile path is typed literally
(`tests/test_no_operator_paths.py`); control and bidi characters are `\\u` escapes (`test_fold`).
"""
from __future__ import annotations

import pathlib
import subprocess

import pytest
from textual.screen import Screen
from textual.widgets import Input, ListView, Static

from mapper import github, keymap
from mapper.app import HomeScreen, MapperApp, RepoScreen
from mapper.diff import git_diff
from mapper.github import GitHubConnector, GitHubError, _ensure_cloned, _local_branches
from mapper.model import Graph
from mapper.store import MapStore
from mapper.widgets.chrome import HintLine
from tests.test_inc9f import (  # noqa: F401  (hermetic is a fixture)
    NARROW, SIZE, _Mirror, _Run, _open_palette, _sentinel_seat, hermetic,
)
from tests.test_inc9g import (
    URL_A, _assert_row_keeps_its_colours, _assert_row_legible, _bare_with_branch,
)
from tests.test_repair_layout import _frame_rows, _rows_in

#: Steps not yet implemented.  An arm keyed to a step in this set is a strict xfail.
OPEN_STEPS: set[str] = {"palette", "repo", "github", "diff", "home"}


def red(step: str):
    if step not in OPEN_STEPS:
        return lambda fn: fn
    return pytest.mark.xfail(
        strict=True, reason=f"Inc-9h: committed RED; closed by the '{step}' step")


async def _settle(pilot, n: int = 4) -> None:
    for _ in range(n):
        await pilot.pause()


# ---------------------------------------------------------------------------
# INC9G-CR-F1 = INC9G-UX-F1 -- row 0 is legible after every filter edit
#
# `_refresh_list` did not await `ListView.clear()`: `index = 0` lit a node that was being
# removed and the new first item never got `-highlight`, so `↵` ran a row painted GROUND on
# the plain row ground (1.12:1).

def _assert_first_row_is_the_lit_one(palette):
    items = list(palette.query_one("#palette-list", ListView).children)
    assert len(items) >= 2 and len(items) == len(palette._items), (len(items), len(palette._items))
    # O1: the label list is rebuilt with the rows, never grown across filters.
    assert len(palette._labels) == len(items), (len(palette._labels), len(items))
    _assert_row_legible(palette, items[0], palette._items[0])
    _assert_row_keeps_its_colours(palette, items[1], palette._items[1])


@red("palette")
@pytest.mark.parametrize("scope", [keymap.SCOPE_HOME, keymap.SCOPE_MAP])
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9h_cr_f1_row_zero_is_legible_after_a_filter_edit_and_after_backspace(
        tmp_path, scope, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        palette, _ = await _open_palette(app, pilot, scope)
        await pilot.press("down", "down")
        await _settle(pilot)
        await pilot.press("o")
        await _settle(pilot)
        _assert_first_row_is_the_lit_one(palette)
        await pilot.press("backspace")
        await _settle(pilot)
        _assert_first_row_is_the_lit_one(palette)


@pytest.mark.parametrize("scope", [
    keymap.SCOPE_HOME,  # a pin: it was already green on the base (measured)
    pytest.param(keymap.SCOPE_MAP, marks=red("palette")),
])
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9h_cr_f1_row_zero_is_legible_after_a_no_match_filter_is_cleared(
        tmp_path, scope, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        palette, _ = await _open_palette(app, pilot, scope)
        await pilot.press(*"zzzz")
        await _settle(pilot)
        assert palette._items == [] and palette._labels == [], (palette._items, palette._labels)
        await pilot.press("backspace", "backspace", "backspace", "backspace")
        await _settle(pilot)
        _assert_first_row_is_the_lit_one(palette)


@red("palette")
async def test_inc9h_cr_f1_enter_after_a_filter_runs_the_row_the_operator_can_see(tmp_path):
    """`↵` ran row 0 while row 0 was invisible: the lit row and the run row are one."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        palette, results = await _open_palette(app, pilot)
        await pilot.press("o")
        await _settle(pilot)
        items = list(palette.query_one("#palette-list", ListView).children)
        lit = [i for i, item in enumerate(items) if item.has_class("-highlight")]
        assert lit == [0], lit
        wanted = palette._items[0].action
        await pilot.press("enter")
        await _settle(pilot)
    assert results == [wanted], results


# ---------------------------------------------------------------------------
# P1 / P2 / INC9G-UX-F2 / F3 / SEC-F3 -- the stale cached copy

class _StaleMirror(_Mirror):
    """A mirror whose refresh fails the way `mode` says once `armed`."""

    def __init__(self, mode: str):
        super().__init__()
        self.mode, self.armed = mode, False

    def __call__(self, argv, *a, **kw):
        if self.armed and "fetch" in argv:
            self.calls.append((list(argv), kw))
            if self.mode == "timeout":
                raise subprocess.TimeoutExpired(argv, 120)
            if self.mode == "host":
                return subprocess.CompletedProcess(
                    argv, 128, "", "fatal: unable to access: Could not resolve host: x\n")
            return subprocess.CompletedProcess(argv, 1, "", "fatal: something git never says\n")
        return super().__call__(argv, *a, **kw)


STALE = [("timeout", "timed out"), ("host", "host not found"), ("exit1", "unknown (exit 1)")]


def _line_colours(screen, region) -> tuple[str, list[str]]:
    """The painted text of the stage panel, and the colour of every glyph from the `▲` row
    to the end of that block (the stale line wraps at the panel's width)."""
    strips = screen._compositor.render_strips()  # noqa: SLF001
    rows = [strips[y].crop(region.x, region.right) for y in range(region.y, region.bottom)]
    out: list[str] = []
    started = False
    for strip in rows:
        segs = [s for s in strip if s.text.strip()]
        if not started and any("▲" in s.text for s in segs):
            started = True
        if started:
            if not segs:
                break
            for s in segs:
                assert s.style and s.style.color, s
                out.append("#%02x%02x%02x" % tuple(s.style.color.get_truecolor()))
    return " ".join("\n".join(_rows_in(screen, region)).split()), out


async def _connect(tmp_path, monkeypatch, mode: str, size, *, stale: bool, relabel: bool = False):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    run = _StaleMirror(mode)
    monkeypatch.setattr("subprocess.run", run)
    _ensure_cloned(URL_A, tmp_path / ".cache" / "mapper" / "repos")
    run.armed = stale
    if relabel:
        _sentinel_seat(monkeypatch)
    app = MapperApp(tmp_path)
    toasts: list[tuple[str, dict]] = []
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.notify = lambda msg, **kw: toasts.append((str(msg), kw))
        app.push_screen(RepoScreen(URL_A))
        screen = None
        for _ in range(30):
            await pilot.pause()
            screen = app.screen
            if isinstance(screen, RepoScreen) and not screen.loading:
                break
        assert isinstance(screen, RepoScreen) and not screen.loading, "the worker never ended"
        app.clear_notifications()
        await _settle(pilot, 3)
        stages = screen.query_one("#repo-stages", Static)
        painted, colours = _line_colours(screen, stages.region)
        return {"painted": painted, "colours": colours, "toasts": toasts,
                "nodes": len(screen.graph.nodes), "frame": "\n".join(_frame_rows(screen))}


@red("repo")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("mode,category", STALE)
async def test_inc9h_p1_the_stage_panel_keeps_the_cached_copy_line_after_the_toast(
        tmp_path, monkeypatch, mode, category, size):
    got = await _connect(tmp_path, monkeypatch, mode, size, stale=True)
    assert f"▲ cached copy: {category}" in got["painted"], got["painted"]
    from mapper import darkside
    assert got["colours"] and set(got["colours"]) == {darkside.INK}, got["colours"]
    assert got["nodes"] >= 1


@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9h_p1_a_fresh_connect_paints_no_cached_copy_line(tmp_path, monkeypatch, size):
    got = await _connect(tmp_path, monkeypatch, "host", size, stale=False)
    assert "cached copy" not in got["painted"] and "▲" not in got["painted"], got["painted"]
    assert "cached copy" not in got["frame"], got["frame"]
    assert "listo" in got["painted"], got["painted"]


@red("repo")
@pytest.mark.parametrize("relabel", [False, True])
@pytest.mark.parametrize("mode,category", STALE)
async def test_inc9h_p2_a_stale_connect_fires_one_warning_with_the_count_and_the_way_back(
        tmp_path, monkeypatch, mode, category, relabel):
    got = await _connect(tmp_path, monkeypatch, mode, SIZE, stale=True, relabel=relabel)
    way_back = keymap.hint_pair(keymap.SCOPE_REPO, "home")
    if relabel:
        assert "zz-home" in way_back, way_back
    expected = f"showing the cached copy ({got['nodes']} nodes): {category} · {way_back} to retry"
    assert [(m, kw.get("severity")) for m, kw in got["toasts"]] == [(expected, "warning")], got["toasts"]
    assert got["toasts"][0][1].get("markup") is False, got["toasts"]


@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9h_p2_a_fresh_connect_still_fires_only_the_connected_toast(
        tmp_path, monkeypatch, size):
    got = await _connect(tmp_path, monkeypatch, "host", size, stale=False)
    assert [m for m, _ in got["toasts"]] == [f"conectado: {got['nodes']} nodos"], got["toasts"]


# ---------------------------------------------------------------------------
# INC9G-SEC-F1 -- a cache hit never shows the copy of another remote

def _clones(run) -> list[list[str]]:
    return [argv for argv, _ in run.calls if argv[:2] == ["git", "clone"]]


@red("github")
def test_inc9h_sec_f1_c_r_and_c_r_dot_git_are_two_remotes_with_two_mirrors(tmp_path, monkeypatch):
    run = _Mirror()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    plain = "https://example.invalid/c/r"
    dotted = "https://example.invalid/c/r.git"
    first = _ensure_cloned(plain, cache)
    second = _ensure_cloned(dotted, cache)
    assert first != second, (first, second)
    assert [c[-2] for c in _clones(run)] == [plain, dotted], run.calls
    fetched = [argv[2] for argv, _ in run.calls if "fetch" in argv]
    assert fetched == [], "each remote was cloned fresh; neither was refreshed through the other"
    # and each one now hits its OWN mirror
    assert _ensure_cloned(plain, cache) == first and _ensure_cloned(dotted, cache) == second
    assert len(_clones(run)) == 2, _clones(run)


@red("github")
def test_inc9h_sec_f1_a_mirror_that_holds_another_remote_is_refused_not_reused(tmp_path, monkeypatch):
    run = _Mirror()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    target = _ensure_cloned(URL_A, cache)
    run.origin[str(target)] = "https://example.invalid/mallory/tools.git"  # a hash collision, or a tampered cache
    run.calls.clear()
    with pytest.raises(GitHubError) as caught:
        _ensure_cloned(URL_A, cache)
    message = str(caught.value)
    assert "mallory" not in message and "alice" not in message, message
    assert not any("fetch" in argv for argv, _ in run.calls), "a foreign mirror was refreshed and shown"


def test_inc9h_sec_f1_the_same_remote_in_the_four_spellings_gets_one_mirror_name_and_no_second_clone(
        tmp_path, monkeypatch):
    names = set()
    for spelling in ("https://example.invalid/c/tools", "https://example.invalid/c/tools/",
                     "https://example.invalid/c/tools.git", "https://example.invalid/c/tools.git/"):
        run = _Mirror()
        monkeypatch.setattr("subprocess.run", run)
        cache = tmp_path / f"cache-{len(names)}-{abs(hash(spelling))}"
        first = _ensure_cloned(spelling, cache)
        assert _ensure_cloned(spelling, cache) == first
        assert len(_clones(run)) == 1, (spelling, run.calls)
        names.add(first.name)
    assert len(names) == 1, names


@pytest.mark.network
@red("github")
@pytest.mark.usefixtures("hermetic")
def test_inc9h_sec_f1_real_git_c_r_and_c_r_dot_git_show_their_own_branches(tmp_path):
    def git(cwd, *args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=True)

    urls = []
    for name, branch in (("r", "plain-main"), ("r.git", "dotted-main")):
        bare = tmp_path / "c" / name
        work = tmp_path / f"work-{branch}"
        bare.mkdir(parents=True)
        work.mkdir()
        git(bare, "init", "--bare", "-b", branch)
        git(work, "init", "-b", branch)
        (work / "f.txt").write_text(name)
        git(work, "add", "f.txt")
        git(work, "commit", "-m", "c")
        git(work, "push", str(bare), branch)
        urls.append(bare.as_uri())
    cache = tmp_path / "cache"
    a = _ensure_cloned(urls[0], cache)
    b = _ensure_cloned(urls[1], cache)
    assert a != b
    assert "plain-main" in _local_branches(a) and "dotted-main" not in _local_branches(a)
    assert "dotted-main" in _local_branches(b) and "plain-main" not in _local_branches(b)
    assert _ensure_cloned(urls[0], cache) == a and _ensure_cloned(urls[1], cache) == b


# ---------------------------------------------------------------------------
# INC9G-SEC-F2 -- the refresh prunes what the remote deleted

@red("github")
def test_inc9h_sec_f2_the_refresh_is_fetch_prune_all(tmp_path, monkeypatch):
    run = _Mirror()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    _ensure_cloned(URL_A, cache)
    _ensure_cloned(URL_A, cache)
    fetches = [argv for argv, _ in run.calls if "fetch" in argv]
    assert len(fetches) == 1 and fetches[0][3:] == ["fetch", "--prune", "--all"], fetches


@pytest.mark.network
@red("github")
@pytest.mark.usefixtures("hermetic")
def test_inc9h_sec_f2_real_git_a_branch_deleted_on_the_remote_is_gone_after_a_reconnect(tmp_path):
    url = _bare_with_branch(tmp_path, "alice", "main")
    bare = tmp_path / "alice" / "tools.git"
    work = tmp_path / "alice-work"

    def git(cwd, *args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=True)

    git(work, "push", str(bare), "main:doomed")
    cache = tmp_path / "cache"
    mirror = _ensure_cloned(url, cache)
    assert "doomed" in _local_branches(mirror)
    git(bare, "branch", "-D", "doomed")
    assert _ensure_cloned(url, cache) == mirror
    assert "doomed" not in _local_branches(mirror), _local_branches(mirror)
    assert "main" in _local_branches(mirror)


# ---------------------------------------------------------------------------
# INC9G-SEC-F4 -- one fixed sentence per malformed owner/name; names pass through plain()

MALFORMED = ["zq", "zq/yw/xv", "zq/yw/xv/wu", "zq//yw", "/zq", "zq/", "../zqyw", "zq/yw?x=1",
             "zq/..", "zq/yw‮", "zq/yw\u0000", "zq/yw\u001b[31m", "zq/y w", "zq/y\u007fw"]


@red("github")
def test_inc9h_sec_f4_every_malformed_owner_name_gets_the_same_fixed_sentence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run = _Run(returncode=0)
    monkeypatch.setattr("subprocess.run", run)
    messages = set()
    for spec in MALFORMED:
        with pytest.raises(GitHubError) as caught:
            GitHubConnector(spec).fetch()
        message = str(caught.value)
        for part in spec.replace("/", " ").split():
            if len(part) > 1 and part.isalnum():
                assert part not in message, (spec, message)
        messages.add(message)
    assert run.calls == [], run.calls
    assert len(messages) == 1 and "refus" in next(iter(messages)), messages


@red("github")
@pytest.mark.parametrize("stderr,tail", [("fatal: Could not resolve host: x\n", "host not found")])
def test_inc9h_sec_f4_the_clone_message_shows_the_name_through_plain(tmp_path, monkeypatch, stderr, tail):
    hostile = "https://example.invalid/o/wi‮d\u001b[31mget.git"
    run = _Run(stderr=stderr)
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        _ensure_cloned(hostile, tmp_path / "cache")
    message = str(caught.value)
    assert message.startswith("could not clone '") and message.endswith(f"': {tail}"), message
    assert "‮" not in message and "\u001b" not in message, repr(message)
    assert "wi" in message and "get" in message, message


@red("github")
def test_inc9h_sec_f4_the_timeout_clone_message_shows_the_name_through_plain(tmp_path, monkeypatch):
    hostile = "https://example.invalid/o/wi‮dget.git"
    monkeypatch.setattr("subprocess.run", _Run(raises=subprocess.TimeoutExpired(["git"], 1)))
    with pytest.raises(GitHubError) as caught:
        _ensure_cloned(hostile, tmp_path / "cache")
    assert "‮" not in str(caught.value), repr(str(caught.value))
    assert str(caught.value).endswith(": timed out")


# ---------------------------------------------------------------------------
# INC9G-SEC-F5 -- every process this package starts is told not to prompt

@red("github")
def test_inc9h_sec_f5_gh_runs_with_its_prompts_disabled(monkeypatch):
    run = _Run(raises=subprocess.CalledProcessError(1, ["gh"], stderr="gh auth login"))
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError):
        GitHubConnector("alice/tools").fetch()
    assert run.calls and run.calls[0][0][0] == "gh", run.calls
    env = run.calls[0][1].get("env")
    assert env is not None and env["GH_PROMPT_DISABLED"] == "1", env
    assert "PATH" in env or "Path" in env, "the gh call still inherits the process environment"


@red("diff")
def test_inc9h_sec_f5_git_show_in_diff_runs_in_the_no_prompt_english_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    store = MapStore(tmp_path / "ws")
    (store.workspace / ".git").mkdir()
    run = _Run(raises=subprocess.CalledProcessError(128, ["git"], stderr="fatal"))
    monkeypatch.setattr("subprocess.run", run)
    assert git_diff("demo", store) is None
    assert run.calls and all(argv[:2] == ["git", "show"] for argv, _ in run.calls), run.calls
    for argv, kw in run.calls:
        env = kw.get("env")
        assert env is not None, argv
        assert env["LC_ALL"] == "C" and env["GIT_TERMINAL_PROMPT"] == "0", (argv, env)
        assert env["HOME"] == str(tmp_path), "built per call, not snapshotted"


# ---------------------------------------------------------------------------
# INC9G-CR-F2 -- the home hint follows the maps across a push and a pop (kills R8, O2)

async def _push_and_pop(app, pilot) -> None:
    app.push_screen(Screen())
    await _settle(pilot, 3)
    app.pop_screen()
    await _settle(pilot, 4)
    assert isinstance(app.screen, HomeScreen), app.screen


async def test_inc9h_cr_f2_the_home_hint_follows_the_maps_when_the_screen_resumes(tmp_path):
    app = MapperApp(tmp_path)
    derived = keymap.hint_pair(keymap.SCOPE_HOME, "open_selected")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)
        hint = app.screen.query_one(HintLine)
        assert derived not in hint.text and "choose a door" in hint.text, hint.text
        app.store.save("demo", Graph())
        await _push_and_pop(app, pilot)
        assert derived in app.screen.query_one(HintLine).text, app.screen.query_one(HintLine).text
        for f in list(app.store.workspace.glob("demo*")):
            f.unlink()
        assert not list(app.store.workspace.glob("*.mmd"))
        await _push_and_pop(app, pilot)
        text = app.screen.query_one(HintLine).text
        assert derived not in text and "choose a door" in text, text


# ---------------------------------------------------------------------------
# INC9G-CR-F5 -- a missing git on a cache hit is an error, never a stale mirror

class _NoGitOnFetch(_Mirror):
    def __call__(self, argv, *a, **kw):
        if "fetch" in argv:
            self.calls.append((list(argv), kw))
            raise FileNotFoundError("git")
        return super().__call__(argv, *a, **kw)


def test_inc9h_cr_f5_a_missing_git_on_a_cache_hit_raises_and_is_not_stale(tmp_path, monkeypatch):
    monkeypatch.setattr("subprocess.run", _NoGitOnFetch())
    cache = tmp_path / "cache"
    _ensure_cloned(URL_A, cache)
    seen: list[str] = []
    with pytest.raises(GitHubError, match="git CLI not found"):
        _ensure_cloned(URL_A, cache, on_stale=seen.append)
    assert seen == [], seen


@red("github")
def test_inc9h_cr_f5_the_timeout_is_a_typed_signal_not_a_message_suffix(tmp_path, monkeypatch):
    assert issubclass(github.GitHubTimeout, GitHubError)
    monkeypatch.setattr("subprocess.run", _Run(raises=subprocess.TimeoutExpired(["git"], 1)))
    with pytest.raises(github.GitHubTimeout, match="timed out"):
        github._run_git(tmp_path, ["fetch"])
    # An untyped error that happens to END in the words is an error, not a stale mirror.
    def lookalike(*a, **kw):
        raise GitHubError("git fetch failed: timed out")
    monkeypatch.setattr(github, "_run_git", lookalike)
    with pytest.raises(GitHubError):
        github._refresh_mirror(tmp_path)


@red("github")
def test_inc9h_cr_f5_a_typed_timeout_is_the_stale_category(tmp_path, monkeypatch):
    def timeout(*a, **kw):
        raise github.GitHubTimeout("git fetch failed: timed out")
    monkeypatch.setattr(github, "_run_git", timeout)
    assert github._refresh_mirror(tmp_path) == "timed out"


# ---------------------------------------------------------------------------
# INC9G-CR-F7 -- the connector forgets a stale flag, and a padded URL is stripped once

@red("github")
def test_inc9h_cr_f7_a_connector_that_connects_twice_forgets_the_first_stale_flag(tmp_path, monkeypatch):
    run = _StaleMirror("host")
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    _ensure_cloned(URL_A, cache)
    connector = GitHubConnector(URL_A, cache_dir=cache)
    run.armed = True
    connector.fetch()
    assert connector.stale == "host not found", connector.stale
    run.armed = False
    connector.fetch()
    assert connector.stale == "", connector.stale


@red("github")
def test_inc9h_cr_f7_a_padded_url_is_cloned_and_keyed_as_its_stripped_form(tmp_path, monkeypatch):
    run = _Mirror()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    padded = _ensure_cloned("  " + URL_A + "\t ", cache)
    assert [c[-2] for c in _clones(run)] == [URL_A], _clones(run)
    run.calls.clear()
    assert _ensure_cloned(URL_A, cache) == padded
    assert _clones(run) == [], "the stripped form hits the mirror the padded form made"
