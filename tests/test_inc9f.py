"""Inc-9f -- argument injection, the failure taxonomy, the home hint, the palette.

Authority: `.dev-flow/2026-08-26-ui-next-batch-02/VERDICT-inc9-2026-09-30.md`
(Round 3: `M1`, `M2` and the coordinator's Inc-9f rulings).  Every arm was
committed RED first, as a STRICT xfail keyed by the step that closes it
(`OPEN_STEPS`); each implementation commit deletes its own step from that set,
and an arm that then fails is a failure, not an xfail.

Nothing here touches the network or the real cache: every git call is either
stubbed or runs against a LOCAL repository created under `tmp_path`, with HOME and
USERPROFILE pointed at `tmp_path`.  The payloads are harmless: a script that only
writes a marker file inside `tmp_path`.  No user-profile path is typed literally
(`tests/test_no_operator_paths.py`, `A-110`).
"""
from __future__ import annotations

import ast
import dataclasses
import pathlib
import subprocess
import sys

import pytest
from textual.widgets import Input, ListView, Static

from mapper import github, keymap
from mapper.app import HomeScreen, MapperApp, PlugRepoScreen, RepoScreen
from mapper.github import GitHubConnector, GitHubError, _ensure_cloned
from mapper.screens.palette import CommandPalette
from mapper.widgets.chrome import HintLine, TabStrip
from tests.test_inc9c import PROFILE
from tests.test_repair_layout import _frame_rows, _rows_in

#: Steps not yet implemented.  An arm keyed to a step in this set is a strict xfail.
OPEN_STEPS: set[str] = set()


def red(step: str):
    if step not in OPEN_STEPS:
        return lambda fn: fn
    return pytest.mark.xfail(
        strict=True, reason=f"Inc-9f: committed RED; closed by the '{step}' step")


SIZE = (118, 34)
NARROW = (87, 34)
GITHUB_PY = pathlib.Path(github.__file__)

#: The operator's M2 ruling, verbatim: the fixed set, and nothing else is painted.
CATEGORIES = ("host not found", "not found or private", "authentication required",
              "network unreachable", "timed out")

#: A sample of git's (and ssh's) English stderr for each category, and the
#: category the code must name.  The sample is NEVER painted.
STDERR_SAMPLES = {
    "host not found": "fatal: unable to access 'https://x.invalid/o/w.git/': "
                      "Could not resolve host: x.invalid\n",
    "not found or private": "remote: Repository not found.\n"
                            "fatal: repository 'https://github.com/o/w.git/' not found\n",
    "authentication required": "fatal: could not read Username for 'https://github.com': "
                               "terminal prompts disabled\n",
    "network unreachable": "fatal: unable to access 'https://x.invalid/o/w.git/': "
                           "Failed to connect to x.invalid port 443: Network is unreachable\n",
}


class _Run:
    """A stand-in for `subprocess.run` that records every argv and answers the
    `git clone` the way a test asks; every other call is refused (no real git)."""

    def __init__(self, *, returncode=128, stderr="", raises=None):
        self.returncode, self.stderr, self.raises = returncode, stderr, raises
        self.calls: list[tuple[list[str], dict]] = []

    def __call__(self, argv, *a, **kw):
        self.calls.append((list(argv), kw))
        if self.raises is not None:
            raise self.raises
        return subprocess.CompletedProcess(argv, self.returncode, "", self.stderr)


@pytest.fixture
def hermetic(tmp_path, monkeypatch):
    """HOME and USERPROFILE in `tmp_path`: no probe reads the real cache."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("GIT_TERMINAL_PROMPT", "0")
    return tmp_path


def _message(url: str, tmp_path, run: _Run, monkeypatch) -> str:
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        _ensure_cloned(url, tmp_path / "cache")
    return str(caught.value)


def _git(*args, cwd=None):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", check=True)


def _marker_script(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    """A harmless payload: it writes one file inside `tmp_path`, nothing else."""
    marker = tmp_path / "marker.txt"
    if sys.platform == "win32":
        script = tmp_path / "payload.cmd"
        script.write_text(f'@echo ran> "{marker}"\r\n')
    else:
        script = tmp_path / "payload.sh"
        script.write_text(f'#!/bin/sh\necho ran > "{marker}"\n')
        script.chmod(0o755)
    return script, marker


# ---------------------------------------------------------------------------
# Item 1 -- argument injection

INJECTIONS = ["--upload-pack=x", "-u", "--config=core.x=1", "--template=x", "-"]


@red("github")
@pytest.mark.parametrize("url", INJECTIONS)
def test_inc9f_f1_a_dash_url_is_refused_before_any_git_runs(url, tmp_path, monkeypatch):
    run = _Run()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError):
        _ensure_cloned(url, tmp_path / "cache")
    assert run.calls == [], f"git was run on {url!r}: {run.calls}"


@red("github")
def test_inc9f_f1_the_payload_never_runs(tmp_path, hermetic):
    """The harmless payload, through the REAL git: `--upload-pack=<script>` as the
    URL.  On `532d32e` the script ran and the marker was written."""
    script, marker = _marker_script(tmp_path)
    with pytest.raises(GitHubError):
        _ensure_cloned(f"--upload-pack={script.as_posix()}", tmp_path / "cache")
    assert not marker.exists(), "the injected --upload-pack ran its payload"


@red("github")
@pytest.mark.parametrize("url", [
    "ext::sh -c touch% /tmp/x", "file::/tmp/x", "Ext::sh -c x/y",
])
def test_inc9f_f1_a_transport_helper_prefix_is_refused(url, tmp_path, monkeypatch):
    run = _Run()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError):
        _ensure_cloned(url, tmp_path / "cache")
    assert run.calls == []


@red("github")
@pytest.mark.parametrize("spec", ["--branch=a/b", "-x/y", "--jq=.x/y"])
def test_inc9f_f1_a_dash_repo_spec_never_reaches_gh(spec, monkeypatch):
    """Reachable on `532d32e` through the connect-repo entry: an `owner/name`
    spec starting with `-` went to `gh repo view` as a flag."""
    run = _Run()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError):
        GitHubConnector(spec).fetch()
    assert run.calls == [], run.calls


@red("github")
def test_inc9f_f1_the_clone_argv_ends_options_before_the_url(tmp_path, monkeypatch):
    run = _Run()
    url = "https://example.invalid/owner/widget.git"
    _message(url, tmp_path, run, monkeypatch)
    clones = [argv for argv, _ in run.calls if argv[:2] == ["git", "clone"]]
    assert len(clones) == 1, run.calls
    argv = clones[0]
    assert "--" in argv, argv
    assert argv.index("--") < argv.index(url) < len(argv), argv
    assert argv[-2] == url and pathlib.Path(argv[-1]).name.startswith("widget-"), argv


def _terminated(elements: list[ast.expr]) -> bool:
    """Is every positional (non-constant, non-option) element of this argv list
    preceded by an option terminator?"""
    seen_end = False
    for el in elements:
        if isinstance(el, ast.Constant) and el.value in ("--", "--end-of-options"):
            seen_end = True
        elif isinstance(el, ast.Starred):
            continue
        elif isinstance(el, ast.Constant):
            continue
        elif isinstance(el, ast.JoinedStr) and el.values and isinstance(
                el.values[0], ast.Constant) and str(el.values[0].value).startswith("-"):
            continue
        elif not seen_end:
            return False
    return True


def _git_argv_lists(source: str) -> list[list[ast.expr]]:
    """Every list literal that is a git argv in `github.py`: the one handed to
    `subprocess.run` whose head is `"git"`, and the `args` handed to `_run_git`."""
    out = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(
            node.func, "id", "")
        if name == "run" and isinstance(node.args[0], ast.List):
            elts = node.args[0].elts
            if elts and isinstance(elts[0], ast.Constant) and elts[0].value == "git":
                out.append(elts)
        elif name == "_run_git" and len(node.args) > 1 and isinstance(node.args[1], ast.List):
            out.append(node.args[1].elts)
    return out


_CENSUS_SAMPLES = {
    "clone with the terminator": (
        "subprocess.run(['git', 'clone', '--mirror', '--', url, str(t)])", True),
    "clone without the terminator": (
        "subprocess.run(['git', 'clone', '--mirror', url, str(t)])", False),
    "log with the terminator": (
        "_run_git(c, ['log', '-1', f'--format={f}', '--end-of-options', b])", True),
    "log without the terminator": ("_run_git(c, ['log', '-1', f'--format={f}', b])", False),
    "constants only": ("_run_git(c, ['tag', '-l'])", True),
}


@pytest.mark.parametrize("case", list(_CENSUS_SAMPLES))
def test_inc9f_f1_the_census_judges_an_argv_by_its_terminator(case):
    source, expected = _CENSUS_SAMPLES[case]
    lists = _git_argv_lists(source)
    assert len(lists) == 1, "the sample holds no git argv: the judge saw nothing"
    assert _terminated(lists[0]) is expected, case


@red("github")
def test_inc9f_f1_every_git_call_in_github_py_ends_options_before_a_positional():
    lists = _git_argv_lists(GITHUB_PY.read_text(encoding="utf-8"))
    assert len(lists) >= 8, f"the census found only {len(lists)} git calls"
    bad = [ast.unparse(ast.List(elts=e)) for e in lists if not _terminated(e)]
    assert bad == [], bad


@red("github")
def test_inc9f_f1_a_hostile_ref_name_is_not_a_git_option(tmp_path, hermetic):
    """A branch named `--output=marker.txt` in a repository the operator connects:
    its short name used to be handed to `git log` as an option, which WROTE the
    file.  Real git, local repository, harmless relative path."""
    repo = tmp_path / "hostile"
    _git("init", str(repo))
    (repo / "a").write_text("a")
    _git("-C", str(repo), "add", "a")
    _git("-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-m", "m")
    _git("-C", str(repo), "update-ref", "refs/heads/--output=marker.txt", "HEAD")
    assert "--output=marker.txt" in _git("-C", str(repo), "branch", "--format=%(refname:short)").stdout
    GitHubConnector(str(repo)).fetch()
    assert not (repo / "marker.txt").exists(), "a ref name acted as a git option"


@red("github")
async def test_inc9f_f1_a_dash_url_typed_into_connect_repo_is_a_toast(tmp_path, hermetic, monkeypatch):
    """Through the real keys: `p`, type, `↵`.  The toast names the rule; the
    typed text is not echoed; nothing is run."""
    run = _Run()
    monkeypatch.setattr("subprocess.run", run)
    toasts: list[str] = []
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.notify = lambda msg, **kw: toasts.append(str(msg))
        await pilot.press("p")
        await pilot.pause()
        assert isinstance(app.screen, PlugRepoScreen)
        app.screen.query_one("#repo-input", Input).value = "--upload-pack=x"
        await pilot.press("enter")
        for _ in range(6):
            await pilot.pause()
            if toasts:
                break
    assert run.calls == [], run.calls
    joined = "\n".join(toasts)
    assert "refus" in joined, joined
    assert "upload-pack" not in joined, joined


# ---------------------------------------------------------------------------
# Item 2 -- R3-CR-F7: reconnecting a mirror

class _Mirror(_Run):
    """`git clone --mirror` as git does it, measured on a local bare repository: the
    target is a BARE repository (`HEAD` is a file, there is no `.git`), and a second
    clone into it fails with exit 128, `destination path ... already exists and is
    not an empty directory`.  Every other call (`fetch`) succeeds."""

    def __call__(self, argv, *a, **kw):
        self.calls.append((list(argv), kw))
        if list(argv)[:2] == ["git", "clone"]:
            target = pathlib.Path(argv[-1])
            if target.exists() and any(target.iterdir()):
                return subprocess.CompletedProcess(argv, 128, "", "fatal: destination path exists\n")
            target.mkdir(parents=True)
            (target / "HEAD").write_text("ref: refs/heads/main\n")
        return subprocess.CompletedProcess(argv, 0, "", "")


@red("github")
def test_inc9f_f7_a_second_connect_fetches_instead_of_recloning(tmp_path, monkeypatch):
    mirror = _Mirror()
    monkeypatch.setattr("subprocess.run", mirror)
    cache, url = tmp_path / "cache", "https://example.invalid/owner/widget.git"
    first = _ensure_cloned(url, cache)
    assert (first / "HEAD").is_file() and not (first / ".git").exists()
    mirror.calls.clear()
    second = _ensure_cloned(url, cache)
    assert second == first
    verbs = [argv for argv, _ in mirror.calls]
    assert not any(a[:2] == ["git", "clone"] for a in verbs), verbs
    assert any("fetch" in a for a in verbs), verbs


# ---------------------------------------------------------------------------
# Items 3 and 4 -- timeout, and the fixed failure categories (M2)

@red("github")
@pytest.mark.parametrize("category", list(STDERR_SAMPLES))
def test_inc9f_m2_each_failure_is_one_fixed_category(category, tmp_path, monkeypatch):
    run = _Run(stderr=STDERR_SAMPLES[category])
    message = _message("https://example.invalid/owner/widget.git", tmp_path, run, monkeypatch)
    assert message == f"could not clone 'widget': {category}", message


@red("github")
def test_inc9f_m2_a_clone_that_times_out_is_the_timed_out_category(tmp_path, monkeypatch):
    run = _Run(raises=subprocess.TimeoutExpired(["git"], 1))
    message = _message("https://example.invalid/owner/widget.git", tmp_path, run, monkeypatch)
    assert message == "could not clone 'widget': timed out", message
    kwargs = next(kw for argv, kw in run.calls if argv[:2] == ["git", "clone"])
    assert kwargs.get("timeout"), f"the clone has no timeout: {kwargs}"


@red("github")
@pytest.mark.parametrize("code", [1, 128, 255])
def test_inc9f_m2_an_unrecognised_failure_names_only_its_exit_code(code, tmp_path, monkeypatch):
    run = _Run(returncode=code, stderr="fatal: something git has never said before\n")
    message = _message("https://example.invalid/owner/widget.git", tmp_path, run, monkeypatch)
    assert message == f"could not clone 'widget': unknown (exit {code})", message


@red("github")
def test_inc9f_m2_git_text_is_never_in_the_message(tmp_path, monkeypatch):
    """A stderr that names a profile path and a token URL: it is classified (host
    not found) and neither of them, nor any of its words, reaches the message."""
    stderr = (f"fatal: unable to access 'https://user:s3cr3t-token@example.invalid/o/w.git/': "
              f"Could not resolve host: example.invalid\nCloning into bare repository "
              f"'{PROFILE}\\.cache\\mapper\\repos\\widget'...\n")
    run = _Run(stderr=stderr)
    message = _message("https://user:s3cr3t-token@example.invalid/owner/widget.git",
                       tmp_path, run, monkeypatch)
    assert message == "could not clone 'widget': host not found", message
    for leaked in ("s3cr3t-token", "example.invalid", "<operator>", "Cloning", "\\", "user:"):
        assert leaked not in message, (leaked, message)


@red("github")
@pytest.mark.parametrize("stderr", [
    "gh: Could not resolve to a Repository with the name 'o/w'. (HTTP 404)\n",
    "error connecting to api.github.com\n",
    "To get started with GitHub CLI, please run:  gh auth login\n",
    "dial tcp: lookup api.github.com: no such host\n",
])
def test_inc9f_r3_sec_f1_gh_stderr_is_never_echoed(stderr, monkeypatch):
    leak = f"{stderr}token ghp_s3cr3t at {PROFILE}"
    err = subprocess.CalledProcessError(1, ["gh"], output="", stderr=leak)
    monkeypatch.setattr("subprocess.run", _Run(raises=err))
    with pytest.raises(GitHubError) as caught:
        GitHubConnector("owner/name").fetch()
    message = str(caught.value)
    assert any(c in message for c in CATEGORIES), message
    for leaked in ("ghp_s3cr3t", "<operator>", "api.github.com", "HTTP", "dial"):
        assert leaked not in message, (leaked, message)


@red("github")
def test_inc9f_r3_sec_f1_a_gh_timeout_is_the_timed_out_category(monkeypatch):
    monkeypatch.setattr("subprocess.run", _Run(raises=subprocess.TimeoutExpired(["gh"], 1)))
    with pytest.raises(GitHubError) as caught:
        GitHubConnector("owner/name").fetch()
    assert "timed out" in str(caught.value), str(caught.value)


# ---------------------------------------------------------------------------
# Item 5 -- the repo screen's stage panel keeps the failure after the toast

async def _failed_repo(tmp_path, monkeypatch, stderr):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr("subprocess.run", _Run(stderr=stderr))
    return MapperApp(tmp_path)


@red("repo")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9f_m2_the_stage_panel_paints_the_failure_after_the_toast_expires(
        tmp_path, monkeypatch, size):
    app = await _failed_repo(tmp_path, monkeypatch, STDERR_SAMPLES["host not found"])
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.push_screen(RepoScreen("https://example.invalid/owner/widget.git"))
        screen = None
        for _ in range(30):
            await pilot.pause()
            screen = app.screen
            if isinstance(screen, RepoScreen) and not screen.loading:
                break
        assert isinstance(screen, RepoScreen) and not screen.loading, "the worker never ended"
        app.clear_notifications()
        for _ in range(3):
            await pilot.pause()
        stages = screen.query_one("#repo-stages", Static)
        painted = " ".join("\n".join(_rows_in(screen, stages.region)).split())
        frame = "\n".join(_frame_rows(screen))
    assert "host not found" in painted, painted
    assert keymap.hint_pair(keymap.SCOPE_REPO, "home") in painted, painted
    assert "listo" not in painted, f"a failed clone still reads 'listo': {painted}"
    assert "100%" not in frame and "0%" not in frame, frame


# ---------------------------------------------------------------------------
# Items 6 and 7 -- the home hint (M1) and the strip's key (R3-CR-F3)

def _sentinel_seat(monkeypatch):
    seat = [dataclasses.replace(b, label=f"zz-{b.action}") for b in keymap.KEYMAP]
    monkeypatch.setattr(keymap, "KEYMAP", seat)
    monkeypatch.setattr(keymap, "GROUP_HEADER", {g: f"zz-{g}" for g in keymap.GROUP_HEADER})


@red("home")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9f_m1_the_home_hint_names_enter_and_invites_a_door(tmp_path, size):
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)
        hint = app.screen.query_one(HintLine)
        rows = _rows_in(app.screen, hint.region)
    derived = keymap.hint_pair(keymap.SCOPE_HOME, "open_selected")
    assert derived in hint.text, hint.text
    assert "choose a door" in hint.text, hint.text
    assert len(rows) == 1 and derived in rows[0] and "choose a door" in rows[0], rows


@red("home")
async def test_inc9f_m1_the_home_hint_follows_a_relabelled_seat(tmp_path, monkeypatch):
    """A hand-written `↵ open map` equals today's label and would pass the arm above;
    it cannot contain a word it has never heard."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _sentinel_seat(monkeypatch)
        app.push_screen(HomeScreen())
        for _ in range(3):
            await pilot.pause()
        text = app.screen.query_one(HintLine).text
    assert "zz-open_selected" in text, text


@red("home")
async def test_inc9f_r3_cr_f3_home_keeps_its_letters_and_active_mark_under_a_rekeyed_seat(
        tmp_path, monkeypatch):
    """`HomeScreen` passed the literal `"c"`.  Re-key the first door: the strip must
    still paint the doors' letters and mark that door active, because the key it is
    given is the seat's."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        seat = [dataclasses.replace(b, key="9", glyph="9") if (
            b.action == "consult" and b.scope == keymap.SCOPE_HOME) else b
            for b in keymap.KEYMAP]
        monkeypatch.setattr(keymap, "KEYMAP", seat)
        app.push_screen(HomeScreen())
        for _ in range(3):
            await pilot.pause()
        strip = app.screen.query_one(TabStrip)
        content = strip.content
        text = getattr(content, "plain", str(content))
    assert strip.active == "9", strip.active
    assert "9 browse maps" in text, text
    assert "p connect repo" in text, text


# ---------------------------------------------------------------------------
# Items 8 and 9 -- the palette: selection painted, arrows reach the list

SELECTED_BG = "#1783ff"


def _row_backgrounds(screen, y: int) -> set[str]:
    strip = screen._compositor.render_strips()[y]  # noqa: SLF001
    out = set()
    for seg in strip:
        bg = seg.style.bgcolor if seg.style else None
        if bg is not None:
            out.add(bg.get_truecolor().hex.lower())
    return out


async def _open_palette(app, pilot, scope=keymap.SCOPE_HOME):
    results: list = []
    app.push_screen(CommandPalette(scope), results.append)
    for _ in range(3):
        await pilot.pause()
    assert isinstance(app.screen, CommandPalette)
    assert isinstance(app.focused, Input), "the search box holds focus"
    return app.screen, results


@red("palette")
async def test_inc9f_r3_ux_f1_the_selected_row_is_painted_with_the_selection_style(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        palette, _ = await _open_palette(app, pilot)
        rows = list(palette.query_one("#palette-list", ListView).children)
        first, second = rows[0].region.y, rows[1].region.y
        assert SELECTED_BG in _row_backgrounds(palette, first)
        assert SELECTED_BG not in _row_backgrounds(palette, second)


@red("palette")
async def test_inc9f_r3_ux_f1_down_moves_the_highlight_while_the_input_holds_focus(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        palette, _ = await _open_palette(app, pilot)
        lv = palette.query_one("#palette-list", ListView)
        assert lv.index == 0
        await pilot.press("down", "down", "down")
        await pilot.pause()
        assert lv.index == 3, lv.index
        assert SELECTED_BG in _row_backgrounds(palette, list(lv.children)[3].region.y)
        assert SELECTED_BG not in _row_backgrounds(palette, list(lv.children)[0].region.y)
        await pilot.press("up")
        await pilot.pause()
        assert lv.index == 2, lv.index
        assert isinstance(app.focused, Input), "arrows must not steal the search box"


@red("palette")
async def test_inc9f_r3_ux_f1_enter_runs_the_highlighted_action_not_the_first(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        palette, results = await _open_palette(app, pilot)
        items = list(palette._items)
        assert len(items) > 3 and items[0].action != items[2].action
        await pilot.press("down", "down", "enter")
        for _ in range(3):
            await pilot.pause()
    assert results == [items[2].action], (results, items[2].action)


async def test_inc9f_r3_ux_f1_typing_still_filters_and_the_list_keeps_a_highlight(tmp_path):
    """A control, GREEN on `532d32e` and after: the fix must not break the search box."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        palette, results = await _open_palette(app, pilot)
        await pilot.press(*"fact")
        await pilot.pause()
        lv = palette.query_one("#palette-list", ListView)
        assert lv.index == 0 and palette._items
        await pilot.press("enter")
        for _ in range(3):
            await pilot.pause()
    assert results == ["factory"], results


def _palette_rows(palette) -> list[tuple[str, keymap.KeyBinding]]:
    rows = _frame_rows(palette)
    out = []
    for item, binding in zip(palette.query_one("#palette-list", ListView).children,
                             palette._items):
        out.append((rows[item.region.y].rstrip(), binding))
    return out


@red("palette")
async def test_inc9f_r3_ux_f7_the_keys_are_one_column(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        palette, _ = await _open_palette(app, pilot)
        rows = _palette_rows(palette)
    assert len(rows) > 5
    assert all(text.endswith(b.glyph) for text, b in rows), rows
    starts = {len(text) - len(b.glyph) for text, b in rows}
    assert len(starts) == 1, starts


@pytest.mark.parametrize("relabel", [False, True])
async def test_inc9f_r3_cr_f2_the_label_column_starts_at_one_cell_under_any_seat(
        tmp_path, monkeypatch, relabel):
    """The header column's width is DERIVED from the seat.  A literal width fits
    today's words and is wrong the moment a header is longer, so the same arm runs
    on the seat's own words and on a relabelled seat (`zz-<group>`, `zz-<action>`)."""
    if relabel:
        _sentinel_seat(monkeypatch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        palette, _ = await _open_palette(app, pilot)
        rows = _palette_rows(palette)
    assert len(rows) > 5
    head_cells = max(len(keymap.group_header(g)) for g in keymap.bar_group_order(palette.scope))
    cols = set()
    for text, binding in rows:
        head = keymap.group_header(binding.group)
        start = text.index(head)
        assert text[start + head_cells + 2:].startswith(binding.label), (text, head_cells)
        cols.add(start + head_cells + 2)
    assert len(cols) == 1, cols
