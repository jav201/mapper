"""Inc-9g -- fixes for the defects the Inc-9f independent reviews found.

Authority: `A-115` (`INC9F-UX-F1`, `INC9F-SEC-F1` .. `INC9F-SEC-F4`).  Every arm was
committed RED first, as a STRICT xfail keyed by the step that closes it
(`OPEN_STEPS`); each implementation commit deletes its own step from that set.

Nothing here reaches the network, the real cache or the real `gh`: every git or gh
call is stubbed, or (the one `network`-marked arm) runs against LOCAL bare
repositories under `tmp_path` with HOME and USERPROFILE pointed at it.  No
user-profile path is typed literally (`tests/test_no_operator_paths.py`).
"""
from __future__ import annotations

import pathlib
import subprocess

import pytest
from textual.widgets import Input, ListView

from mapper import keymap
from mapper.app import HomeScreen, MapperApp, RepoScreen
from mapper.model import Graph
from mapper import github
from mapper.github import (
    CATEGORIES, GitHubConnector, GitHubError, _ensure_cloned, _failure_category, _local_branches,
)
from tests.test_inc9f import (  # noqa: F401  (hermetic is a fixture)
    CATEGORIES as ORACLE_CATEGORIES, NARROW, SIZE, _Mirror, _Run, _message, _open_palette,
    _sentinel_seat, hermetic,
)
from mapper.widgets.chrome import HintLine
from tests.test_repair_layout import _frame_rows, _rows_in

#: Steps not yet implemented.  An arm keyed to a step in this set is a strict xfail.
OPEN_STEPS: set[str] = set()


def red(step: str):
    if step not in OPEN_STEPS:
        return lambda fn: fn
    return pytest.mark.xfail(
        strict=True, reason=f"Inc-9g: committed RED; closed by the '{step}' step")


# ---------------------------------------------------------------------------
# INC9F-UX-F1 -- every glyph on the highlighted palette row is legible

SELECTED_BG = "#1783ff"
ACCENT = "#1783ff"
MIN_CONTRAST = 4.5


def _channel(v: int) -> float:
    s = v / 255
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def _luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_channel(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    hi, lo = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _row_cells(screen, item) -> list[tuple[str, tuple | None, tuple | None]]:
    """(text, fg, bg) of every composited segment of one palette row, cropped to the row."""
    region = item.region
    strip = screen._compositor.render_strips()[region.y].crop(region.x, region.right)  # noqa: SLF001
    out = []
    for seg in strip:
        style = seg.style
        fg = style.color.get_truecolor() if style and style.color else None
        bg = style.bgcolor.get_truecolor() if style and style.bgcolor else None
        out.append((seg.text, tuple(fg) if fg else None, tuple(bg) if bg else None))
    return out


def _hex(rgb) -> str:
    return "#%02x%02x%02x" % tuple(rgb)


def _assert_row_legible(screen, item, binding):
    cells = _row_cells(screen, item)
    lit = [(t, fg, bg) for t, fg, bg in cells if t.strip()]
    assert lit and any(binding.glyph in t for t, _, _ in lit), (binding.glyph, lit)
    for text, fg, bg in lit:
        assert bg is not None and _hex(bg) == SELECTED_BG, (text, bg)
        assert fg is not None, (text, "no foreground")
        ratio = contrast(fg, bg)
        assert ratio >= MIN_CONTRAST, (text, _hex(fg), _hex(bg), round(ratio, 2))


def _assert_row_keeps_its_colours(screen, item, binding):
    cells = _row_cells(screen, item)
    # The key is the row's last painted segment (a short glyph also occurs in words).
    lit = [(t, fg) for t, fg, _ in cells if t.strip()]
    assert lit[-1][0].strip() == binding.glyph, (binding.glyph, lit)
    assert _hex(lit[-1][1]) == ACCENT, (binding.glyph, lit)
    assert all(bg is None or _hex(bg) != SELECTED_BG for _, _, bg in cells), cells


@red("palette")
@pytest.mark.parametrize("scope", [keymap.SCOPE_HOME, keymap.SCOPE_MAP])
@pytest.mark.parametrize("relabel", [False, True])
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9g_ux_f1_every_glyph_on_the_selected_row_is_legible(
        tmp_path, monkeypatch, scope, relabel, size):
    if relabel:
        _sentinel_seat(monkeypatch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        palette, _ = await _open_palette(app, pilot, scope)
        items = list(palette.query_one("#palette-list", ListView).children)
        _assert_row_legible(palette, items[0], palette._items[0])
        _assert_row_keeps_its_colours(palette, items[1], palette._items[1])


@red("palette")
async def test_inc9g_ux_f1_the_highlight_moves_the_legible_paint_with_it(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        palette, _ = await _open_palette(app, pilot)
        items = list(palette.query_one("#palette-list", ListView).children)
        await pilot.press("down", "down", "down")
        for _ in range(3):
            await pilot.pause()
        _assert_row_legible(palette, items[3], palette._items[3])
        _assert_row_keeps_its_colours(palette, items[0], palette._items[0])
        await pilot.press("up", "up", "up")
        for _ in range(3):
            await pilot.pause()
        _assert_row_legible(palette, items[0], palette._items[0])
        _assert_row_keeps_its_colours(palette, items[3], palette._items[3])


# ---------------------------------------------------------------------------
# INC9F-SEC-F1 -- the mirror is keyed on the whole URL, not its last segment

URL_A = "https://example.invalid/alice/tools.git"
URL_B = "https://example.invalid/bob/tools.git"


@red("github")
def test_inc9g_sec_f1_two_remotes_with_one_last_segment_get_two_mirrors(tmp_path, monkeypatch):
    mirror = _Mirror()
    monkeypatch.setattr("subprocess.run", mirror)
    cache = tmp_path / "cache"
    a = _ensure_cloned(URL_A, cache)
    b = _ensure_cloned(URL_B, cache)
    assert a != b, (a, b)
    clones = [argv for argv, _ in mirror.calls if argv[:2] == ["git", "clone"]]
    assert len(clones) == 2, mirror.calls
    assert [c[-2] for c in clones] == [URL_A, URL_B]


def test_inc9g_sec_f1_the_same_url_still_hits_its_own_mirror(tmp_path, monkeypatch):
    mirror = _Mirror()
    monkeypatch.setattr("subprocess.run", mirror)
    cache = tmp_path / "cache"
    first = _ensure_cloned(URL_A, cache)
    mirror.calls.clear()
    assert _ensure_cloned(URL_A, cache) == first
    assert not any(a[:2] == ["git", "clone"] for a, _ in mirror.calls)


@red("github")
def test_inc9g_sec_f1_the_directory_keeps_the_readable_name(tmp_path, monkeypatch):
    monkeypatch.setattr("subprocess.run", _Mirror())
    target = _ensure_cloned(URL_A, tmp_path / "cache")
    assert target.name.startswith("tools-"), target.name
    assert target.parent == tmp_path / "cache"


def _bare_with_branch(root: pathlib.Path, owner: str, branch: str) -> str:
    bare = root / owner / "tools.git"
    work = root / f"{owner}-work"
    bare.mkdir(parents=True)
    work.mkdir()

    def git(cwd, *args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=True)

    git(bare, "init", "--bare", "-b", branch)
    git(work, "init", "-b", branch)
    (work / "f.txt").write_text(owner)
    git(work, "add", "f.txt")
    git(work, "commit", "-m", "c")
    git(work, "push", str(bare), branch)
    return bare.as_uri()


@pytest.mark.network
@red("github")
@pytest.mark.usefixtures("hermetic")
def test_inc9g_sec_f1_real_git_two_local_remotes_show_their_own_branches(tmp_path):
    url_a = _bare_with_branch(tmp_path, "alice", "alice-main")
    url_b = _bare_with_branch(tmp_path, "bob", "bob-main")
    cache = tmp_path / "cache"
    a = _ensure_cloned(url_a, cache)
    b = _ensure_cloned(url_b, cache)
    assert a != b
    assert "alice-main" in _local_branches(a) and "bob-main" not in _local_branches(a)
    assert "bob-main" in _local_branches(b) and "alice-main" not in _local_branches(b)
    assert _ensure_cloned(url_a, cache) == a


# ---------------------------------------------------------------------------
# INC9F-SEC-F3 -- a fetch timeout on a cache hit continues on the stale mirror

class _TimingOutFetch(_Mirror):
    def __call__(self, argv, *a, **kw):
        if "fetch" in argv:
            self.calls.append((list(argv), kw))
            raise subprocess.TimeoutExpired(argv, 30)
        return super().__call__(argv, *a, **kw)


@red("github")
def test_inc9g_sec_f3_a_fetch_timeout_on_a_cache_hit_uses_the_stale_mirror(tmp_path, monkeypatch):
    run = _TimingOutFetch()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    first = _ensure_cloned(URL_A, cache)
    second = _ensure_cloned(URL_A, cache)
    assert second == first
    assert any("fetch" in argv for argv, _ in run.calls), run.calls


def test_inc9g_sec_f3_a_clone_timeout_is_still_an_error(tmp_path, monkeypatch):
    monkeypatch.setattr("subprocess.run", _Run(raises=subprocess.TimeoutExpired(["git"], 1)))
    with pytest.raises(GitHubError, match="timed out"):
        _ensure_cloned(URL_A, tmp_path / "cache")


# ---------------------------------------------------------------------------
# INC9F-SEC-F4 -- owner/name is validated before it reaches a `gh api` path

@red("github")
@pytest.mark.parametrize("spec", [
    "../user", "o/n?x=1", "o/..", "./n", "o/.", "o/n#frag", "o%2f/n", "o/n x", "o_x/n",
    "o/n\u202e", "o/n\u0000",
])
def test_inc9g_sec_f4_a_malformed_owner_name_never_reaches_gh(spec, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # a relative spec like `o/..` is a LOCAL path when it names a repo
    run = _Run(returncode=0)
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector(spec).fetch()
    assert run.calls == [], run.calls
    assert "refus" in str(caught.value)
    assert "\u202e" not in str(caught.value) and "\x00" not in str(caught.value)


@pytest.mark.parametrize("spec", ["alice/tools", "my-org/a_b.js", "A1/.github", "o/n-1.2_3"])
def test_inc9g_sec_f4_a_well_formed_owner_name_reaches_gh(spec, monkeypatch):
    run = _Run(raises=subprocess.CalledProcessError(1, ["gh"], stderr="gh auth login"))
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError, match="authentication required"):
        GitHubConnector(spec).fetch()
    assert run.calls and run.calls[0][0][:3] == ["gh", "repo", "view"], run.calls


# ---------------------------------------------------------------------------
# INC9F-SEC-F2 -- typed repo text is painted as text, never parsed as markup

HOSTILE = ["a[/b]", "[@click=app.quit]q[/]", "[link=file:///x]a[/link]"]


@red("app")
@pytest.mark.parametrize("typed", HOSTILE)
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9g_sec_f2_typed_repo_text_is_shown_literally(tmp_path, monkeypatch, typed, size):
    def fetch(self, progress=None):
        raise GitHubError("could not query 'x': timed out")
    monkeypatch.setattr(GitHubConnector, "fetch", fetch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.push_screen(RepoScreen(typed))
        for _ in range(5):
            await pilot.pause()
        screen = app.screen
        assert isinstance(screen, RepoScreen), screen
        name_region = screen.query_one("#repo-name").region
        rows = _frame_rows(screen)
        assert typed in rows[name_region.y], (typed, rows[name_region.y])
        # The crumb paints the same text; it too must be literal.
        assert any(typed in r or typed[:12] in r for r in rows[:3]), rows[:3]
        strips = screen._compositor.render_strips()  # noqa: SLF001
        for strip in strips:
            for seg in strip:
                style = seg.style
                assert style is None or style.link is None, (seg.text, style.link)
                # Textual stamps every cell with its own `offset`; a planted action is any other key.
                planted = set(style.meta) - {"offset"} if style and style.meta else set()
                assert not planted, (seg.text, style.meta)


# ---------------------------------------------------------------------------
# N1 / INC9F-UX-F2 -- with nothing to open, the home hint does not offer `↵ open map`

async def _home_hint(tmp_path, size, *, maps: bool, relabel: bool = False, monkeypatch=None):
    app = MapperApp(tmp_path)
    if maps:
        app.store.save("demo", Graph())
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        if relabel:
            _sentinel_seat(monkeypatch)
            app.push_screen(HomeScreen())
            for _ in range(3):
                await pilot.pause()
        assert isinstance(app.screen, HomeScreen)
        hint = app.screen.query_one(HintLine)
        return hint.text, _rows_in(app.screen, hint.region)


@red("home")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9g_n1_no_recent_maps_the_hint_only_invites_a_door(tmp_path, size):
    text, rows = await _home_hint(tmp_path, size, maps=False)
    derived = keymap.hint_pair(keymap.SCOPE_HOME, "open_selected")
    assert derived not in text and "↵" not in text, text
    assert len(rows) == 1 and "choose a door" in rows[0], rows
    assert derived not in rows[0] and "↵" not in rows[0], rows


@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9g_n1_with_recent_maps_the_hint_still_names_enter(tmp_path, size):
    text, rows = await _home_hint(tmp_path, size, maps=True)
    derived = keymap.hint_pair(keymap.SCOPE_HOME, "open_selected")
    assert derived in text and "choose a door" in text, text
    assert len(rows) == 1 and derived in rows[0] and "choose a door" in rows[0], rows


@red("home")
async def test_inc9g_n1_the_relabelled_seat_word_is_gone_without_maps_and_present_with(
        tmp_path, monkeypatch):
    (tmp_path / "a").mkdir()
    without, _ = await _home_hint(tmp_path / "a", SIZE, maps=False, relabel=True, monkeypatch=monkeypatch)
    assert "zz-open_selected" not in without and "choose a door" in without, without
    (tmp_path / "b").mkdir()
    withmaps, _ = await _home_hint(tmp_path / "b", SIZE, maps=True, relabel=True, monkeypatch=monkeypatch)
    assert "zz-open_selected" in withmaps, withmaps


# ---------------------------------------------------------------------------
# INC9F-CR-F1 -- the classifier's precedence is pinned, pair by pair

OVERLAPS = [
    ("host not found", "authentication required",
     "fatal: Could not resolve host: x\nfatal: Authentication failed for 'https://x/'\n"),
    ("host not found", "not found or private",
     "dial tcp: lookup x: no such host\nfatal: repository 'https://x/o/w.git/' not found\n"),
    ("host not found", "network unreachable",
     "dial tcp: lookup x: no such host\nerror connecting to x\n"),
    ("authentication required", "not found or private",
     "remote: Repository not found.\nfatal: Authentication failed for 'https://x/'\n"),
    ("authentication required", "network unreachable",
     "fatal: Failed to connect to x port 443\nfatal: could not read Username for 'https://x'\n"),
    ("not found or private", "network unreachable",
     "fatal: Failed to connect to x port 443\nfatal: repository 'https://x/o/w.git/' does not exist\n"),
]


@pytest.mark.parametrize("winner,loser,stderr", OVERLAPS)
def test_inc9g_cr_f1_when_two_categories_match_the_earlier_one_wins(winner, loser, stderr):
    assert _failure_category(stderr, 1) == winner, (winner, loser)


@pytest.mark.parametrize("winner,loser,stderr", OVERLAPS)
def test_inc9g_cr_f1_the_clone_message_names_the_winner_exactly(
        winner, loser, stderr, tmp_path, monkeypatch):
    message = _message("https://example.invalid/owner/widget.git", tmp_path,
                       _Run(stderr=stderr), monkeypatch)
    assert message == f"could not clone 'widget': {winner}", message


# ---------------------------------------------------------------------------
# INC9F-CR-F2 -- every gh sample names its own category, exactly

GH_SAMPLES = [
    ("not found or private", "gh: Not Found (HTTP 404)\n"),
    ("network unreachable", "error connecting to api.github.com\n"),
    ("authentication required", "To get started with GitHub CLI, please run:  gh auth login\n"),
    ("host not found", "dial tcp: lookup api.github.com: no such host\n"),
]


@pytest.mark.parametrize("category,stderr", GH_SAMPLES)
def test_inc9g_cr_f2_a_gh_failure_is_its_own_category_exactly(category, stderr, monkeypatch):
    monkeypatch.setattr("subprocess.run", _Run(
        raises=subprocess.CalledProcessError(1, ["gh"], stderr=stderr)))
    with pytest.raises(GitHubError) as caught:
        GitHubConnector("owner/name").fetch()
    assert str(caught.value) == f"could not query 'owner/name': {category}", str(caught.value)


# ---------------------------------------------------------------------------
# INC9F-CR-F3 -- the search box keeps its editing keys

async def test_inc9g_cr_f3_editing_keys_edit_the_search_box(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        palette, _ = await _open_palette(app, pilot)
        box = palette.query_one("#palette-input", Input)
        await pilot.press(*"fact", "left", "left", "x", "home", "y")
        await pilot.pause()
        assert box.value == "yfaxct", box.value
        await pilot.press("end", "z")
        await pilot.pause()
        assert box.value == "yfaxctz", box.value


# ---------------------------------------------------------------------------
# INC9F-CR-F4 -- a cache hit that cannot be refreshed shows the cached copy, and says so

class _StaleFetch(_Mirror):
    """A mirror whose `fetch` times out (`timeout=True`) or exits non-zero."""

    def __init__(self, *, timeout: bool):
        super().__init__()
        self.timeout = timeout
        self.armed = False

    def __call__(self, argv, *a, **kw):
        if self.armed and "fetch" in argv:
            self.calls.append((list(argv), kw))
            if self.timeout:
                raise subprocess.TimeoutExpired(argv, 120)
            return subprocess.CompletedProcess(
                argv, 128, "", "fatal: unable to access: Could not resolve host: x\n")
        return super().__call__(argv, *a, **kw)


@pytest.mark.parametrize("timeout,category", [(True, "timed out"), (False, "host not found")])
def test_inc9g_cr_f4_the_connector_flags_a_stale_mirror(tmp_path, monkeypatch, timeout, category):
    run = _StaleFetch(timeout=timeout)
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    _ensure_cloned(URL_A, cache)
    run.armed = True
    seen: list[str] = []
    assert _ensure_cloned(URL_A, cache, on_stale=seen.append).is_dir()
    assert seen == [category], seen
    fetches = [kw for argv, kw in run.calls if "fetch" in argv]
    assert [kw["timeout"] for kw in fetches] == [github._CLONE_TIMEOUT], fetches


def test_inc9g_cr_f4_a_fresh_mirror_is_not_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr("subprocess.run", _Mirror())
    cache = tmp_path / "cache"
    _ensure_cloned(URL_A, cache)
    seen: list[str] = []
    _ensure_cloned(URL_A, cache, on_stale=seen.append)
    assert seen == []


@pytest.mark.parametrize("timeout,category", [(True, "timed out"), (False, "host not found")])
@pytest.mark.usefixtures("hermetic")
async def test_inc9g_cr_f4_the_repo_screen_loads_the_cached_copy_and_toasts(
        tmp_path, monkeypatch, timeout, category):
    run = _StaleFetch(timeout=timeout)
    monkeypatch.setattr("subprocess.run", run)
    _ensure_cloned(URL_A, tmp_path / ".cache" / "mapper" / "repos")
    run.armed = True
    app = MapperApp(tmp_path)
    toasts: list[str] = []
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.notify = lambda msg, **kw: toasts.append(str(msg))
        app.push_screen(RepoScreen(URL_A))
        screen = None
        for _ in range(30):
            await pilot.pause()
            screen = app.screen
            if isinstance(screen, RepoScreen) and not screen.loading:
                break
        assert isinstance(screen, RepoScreen) and not screen.loading, "the worker never ended"
        assert screen.failure == "" and len(screen.graph.nodes) >= 1, (screen.failure, screen.graph)
    assert f"showing the cached copy: {category}" in toasts, toasts


@pytest.mark.usefixtures("hermetic")
async def test_inc9g_cr_f4_a_fresh_connect_does_not_toast_a_stale_copy(tmp_path, monkeypatch):
    monkeypatch.setattr("subprocess.run", _Mirror())
    _ensure_cloned(URL_A, tmp_path / ".cache" / "mapper" / "repos")
    app = MapperApp(tmp_path)
    toasts: list[str] = []
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.notify = lambda msg, **kw: toasts.append(str(msg))
        app.push_screen(RepoScreen(URL_A))
        for _ in range(30):
            await pilot.pause()
            if isinstance(app.screen, RepoScreen) and not app.screen.loading:
                break
    assert toasts and not any("cached copy" in t for t in toasts), toasts


# ---------------------------------------------------------------------------
# INC9F-CR-F5 -- only an ssh key refusal is an authentication failure

def test_inc9g_cr_f5_a_local_permission_denied_is_not_an_authentication_failure(tmp_path, monkeypatch):
    run = _Run(stderr="fatal: could not create work tree dir 'x': Permission denied\n")
    message = _message("https://example.invalid/owner/widget.git", tmp_path, run, monkeypatch)
    assert message == "could not clone 'widget': unknown (exit 128)", message


def test_inc9g_cr_f5_an_ssh_key_refusal_is_still_an_authentication_failure(tmp_path, monkeypatch):
    run = _Run(stderr="git@example.invalid: Permission denied (publickey).\n")
    message = _message("https://example.invalid/owner/widget.git", tmp_path, run, monkeypatch)
    assert message == "could not clone 'widget': authentication required", message


# ---------------------------------------------------------------------------
# INC9F-CR-F6 -- the fixed category set is declared once

def test_inc9g_cr_f6_the_declared_set_is_the_set_the_operator_ruled():
    assert set(CATEGORIES) == set(ORACLE_CATEGORIES), CATEGORIES


def test_inc9g_cr_f6_the_timeout_category_is_spelled_once():
    source = pathlib.Path(github.__file__).read_text(encoding="utf-8")
    # the definition, and the stderr marker `connection timed out`
    assert source.count("timed out") == 2, source.count("timed out")


# ---------------------------------------------------------------------------
# Item 13 -- every git call carries the English, no-prompt environment

@pytest.mark.usefixtures("hermetic")
def test_inc9g_env_every_git_call_runs_in_a_no_prompt_english_environment(tmp_path, monkeypatch):
    run = _Mirror()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / ".cache" / "mapper" / "repos"
    _ensure_cloned(URL_A, cache)
    GitHubConnector(URL_A).fetch()  # a cache hit: fetch, then every read
    gits = [(argv, kw) for argv, kw in run.calls if argv[0] == "git"]
    assert len(gits) > 4, gits
    for argv, kw in gits:
        env = kw.get("env")
        assert env is not None, argv
        assert env["LC_ALL"] == "C" and env["GIT_TERMINAL_PROMPT"] == "0", (argv, env)
        assert env["HOME"] == str(tmp_path), "the env is built per call, not snapshotted at import"


# ---------------------------------------------------------------------------
# Item 14 -- the transport-helper rule reads the same stripped text as the dash rule

@pytest.mark.parametrize("spec", ["  ext::sh x", "\text::sh x", " file::x"])
def test_inc9g_refuse_a_padded_transport_helper(spec, tmp_path, monkeypatch):
    run = _Run()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError, match="transport helpers"):
        _ensure_cloned(spec, tmp_path / "cache")
    with pytest.raises(GitHubError, match="transport helpers"):
        GitHubConnector(spec).fetch()
    assert run.calls == [], run.calls
