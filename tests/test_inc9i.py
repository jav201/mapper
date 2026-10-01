"""Inc-9i -- fixes for the defects the Inc-9h reviews found.

Authority: `A-117` (`INC9H-CR-F1` = `INC9H-SEC-F1`, `CR-F2`, `CR-F3`, `UX-F1`, `SEC-F2`, and
the operator's Round 6 Q1, `VERDICT-inc9-2026-09-30.md`: `.../r` and `.../r.git` are distinct
remotes, a double clone is accepted, a repo is never shown under another's URL, and no
spelling is ever locked out).  Every arm that a fix closes is committed RED first as a STRICT
xfail keyed by the step that closes it (`OPEN_STEPS`); an arm that is not keyed is a pin.

Nothing here reaches the network, the real cache or the real `gh`: every git or gh call is
stubbed, or (the `network` arm) runs against LOCAL bare repositories under `tmp_path` with
HOME and USERPROFILE pointed at it.  No user-profile path is typed literally; control and
bidi characters are `\\u` escapes (`test_fold`).
"""
from __future__ import annotations

import subprocess

import pytest
from textual.widgets import Static

from mapper.app import HomeScreen, MapperApp, RepoScreen
from mapper.github import GitHubConnector, GitHubError, _ensure_cloned, _local_branches, _mirror_dir
from tests import test_inc9h
from tests.test_inc9f import (  # noqa: F401
    CATEGORIES, NARROW, SIZE, STDERR_SAMPLES, _Mirror, _Run, hermetic,
)
from tests.test_inc9g import URL_A
from tests.test_inc9h import _StaleMirror, _clones, _connect, _settle
from tests.test_repair_layout import _rows_in

OPEN_STEPS: set[str] = set()


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9i: committed RED; closed by the '{step}' step")
    return lambda fn: fn


def red_marks(step: str) -> list:
    if step not in OPEN_STEPS:
        return []
    return [pytest.mark.xfail(
        strict=True, reason=f"Inc-9i: committed RED; closed by the '{step}' step")]


# ---------------------------------------------------------------------------
# INC9H-CR-F1 = INC9H-SEC-F1 -- `r` and `r.git` are two remotes, in either order

R = "https://example.invalid/c/r"
R_GIT = "https://example.invalid/c/r.git"


@red("github")
def test_inc9i_cr_f1_r_dot_git_then_r_in_one_cache_gives_two_clones_and_no_refusal(tmp_path, monkeypatch):
    run = _Mirror()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    dotted = _ensure_cloned(R_GIT, cache)
    plain = _ensure_cloned(R, cache)  # base: refused for good ("belongs to another repository")
    assert plain != dotted, (plain, dotted)
    assert [c[-2] for c in _clones(run)] == [R_GIT, R], run.calls
    assert run.origin[str(dotted)] == R_GIT and run.origin[str(plain)] == R, run.origin
    run.calls.clear()
    assert _ensure_cloned(R_GIT, cache) == dotted and _ensure_cloned(R, cache) == plain
    assert _clones(run) == [], "each spelling hits its own mirror"
    # `INC9I-CR-F2`: `R/` is `R`: it finds the as-typed directory `R` made, not a third clone
    assert _ensure_cloned(R + "/", cache) == plain and _clones(run) == [], _clones(run)


def test_inc9i_cr_f1_r_then_r_dot_git_in_one_cache_still_gives_two_clones(tmp_path, monkeypatch):
    run = _Mirror()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    plain = _ensure_cloned(R, cache)
    dotted = _ensure_cloned(R_GIT, cache)
    assert plain != dotted
    assert [c[-2] for c in _clones(run)] == [R, R_GIT], run.calls
    # and a round trip never clones again and never refuses
    for _ in range(2):
        assert _ensure_cloned(R, cache) == plain and _ensure_cloned(R_GIT, cache) == dotted
    assert len(_clones(run)) == 2, _clones(run)


@red("github")
def test_inc9i_cr_f1_a_cache_the_base_built_with_only_the_dot_git_mirror_accepts_the_plain_url(
        tmp_path, monkeypatch):
    """The base keyed `tools.git` on the normal form, in the primary directory: a cache already
    on a user's disk.  Connecting the plain spelling to it must work, not lock it out."""
    run = _Mirror()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    plain = "https://example.invalid/alice/tools"
    dotted = plain + ".git"
    primary = _mirror_dir(cache, "tools", plain)  # what the base wrote for `tools.git`
    primary.mkdir(parents=True)
    (primary / "HEAD").write_text("ref: refs/heads/main\n")
    run.origin[str(primary)] = dotted
    got = _ensure_cloned(plain, cache)
    assert got != primary, got
    assert [c[-2] for c in _clones(run)] == [plain], run.calls
    assert _ensure_cloned(dotted, cache) == primary and len(_clones(run)) == 1
    assert _ensure_cloned(plain, cache) == got and len(_clones(run)) == 1


@pytest.mark.network
@red("github")
@pytest.mark.usefixtures("hermetic")
def test_inc9i_cr_f1_real_git_r_dot_git_then_r_shows_each_repos_own_branches(tmp_path):
    def git(cwd, *args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
            cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=True)

    urls = {}
    for name, branch in (("r.git", "dotted-main"), ("r", "plain-main")):
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
        urls[name] = bare.as_uri()
    cache = tmp_path / "cache"
    dotted = _ensure_cloned(urls["r.git"], cache)
    plain = _ensure_cloned(urls["r"], cache)  # base: GitHubError "refusing the cached copy"
    assert dotted != plain
    assert "dotted-main" in _local_branches(dotted) and "plain-main" not in _local_branches(dotted)
    assert "plain-main" in _local_branches(plain) and "dotted-main" not in _local_branches(plain)
    assert _ensure_cloned(urls["r.git"], cache) == dotted and _ensure_cloned(urls["r"], cache) == plain


# ---------------------------------------------------------------------------
# INC9H-CR-F2 -- the origin comparison is exact: a case difference is another remote

def test_inc9i_cr_f2_an_origin_that_differs_only_by_case_is_not_this_url(tmp_path, monkeypatch):
    run = _Mirror()
    monkeypatch.setattr("subprocess.run", run)
    cache = tmp_path / "cache"
    foreign = _ensure_cloned(URL_A, cache)
    run.origin[str(foreign)] = URL_A.replace("alice", "Alice")
    assert run.origin[str(foreign)] != URL_A and run.origin[str(foreign)].lower() == URL_A.lower()
    run.calls.clear()
    mine = _ensure_cloned(URL_A, cache)
    assert mine != foreign, "the case-different origin was reused"
    assert [c[-2] for c in _clones(run)] == [URL_A], run.calls
    assert not any(argv[:3] == ["git", "-C", str(foreign)] and "fetch" in argv
                   for argv, _ in run.calls), "the other-case mirror was refreshed and shown"


# ---------------------------------------------------------------------------
# INC9H-CR-F3 -- a stale connect, `q`, a fresh connect: the second paints no cached-copy line

async def _open_repo(app, pilot):
    app.push_screen(RepoScreen(URL_A))
    for _ in range(30):
        await pilot.pause()
        screen = app.screen
        if isinstance(screen, RepoScreen) and not screen.loading:
            break
    assert isinstance(screen, RepoScreen) and not screen.loading, "the worker never ended"
    app.clear_notifications()
    await _settle(pilot, 3)
    return screen


def _panel(screen) -> str:
    region = screen.query_one("#repo-stages", Static).region
    return " ".join("\n".join(_rows_in(screen, region)).split())


async def test_inc9i_cr_f3_a_fresh_connect_after_a_stale_one_paints_no_cached_copy_line(
        tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    run = _StaleMirror("host")
    monkeypatch.setattr("subprocess.run", run)
    _ensure_cloned(URL_A, tmp_path / ".cache" / "mapper" / "repos")
    run.armed = True
    app = MapperApp(tmp_path)
    toasts: list[str] = []
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.notify = lambda msg, **kw: toasts.append(str(msg))
        first = await _open_repo(app, pilot)
        assert first.stale == "host not found" and "▲ cached copy: host not found" in _panel(first)
        await pilot.press("q")
        await _settle(pilot, 4)
        assert isinstance(app.screen, HomeScreen), app.screen
        run.armed = False
        toasts.clear()
        second = await _open_repo(app, pilot)
        assert second is not first
        panel = _panel(second)
        assert second.stale == "", second.stale
        assert "cached copy" not in panel and "▲" not in panel and "listo" in panel, panel
        assert [t for t in toasts if "cached copy" in t] == [], toasts
        assert any(t.startswith("conectado: ") for t in toasts), toasts


# ---------------------------------------------------------------------------
# INC9H-UX-F1 -- the category on the `▲ cached copy:` line never breaks across lines

_JUNK_STDERR = "fatal: something git never says\n"
UNKNOWN_EXITS = ("unknown (exit 1)", "unknown (exit 128)")


class _CategoryMirror(_StaleMirror):
    """The refresh fails the way the CATEGORY named by `mode` says: the stderr that
    `_failure_category` maps to it, a timeout, or stderr git never says with that exit code."""

    def __call__(self, argv, *a, **kw):
        if self.armed and "fetch" in argv:
            self.calls.append((list(argv), kw))
            if self.mode == "timed out":
                raise subprocess.TimeoutExpired(argv, 120)
            if self.mode.startswith("unknown (exit "):
                return subprocess.CompletedProcess(argv, int(self.mode[14:-1]), "", _JUNK_STDERR)
            return subprocess.CompletedProcess(argv, 128, "", STDERR_SAMPLES[self.mode])
        return super(_StaleMirror, self).__call__(argv, *a, **kw)


@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("category", [*CATEGORIES, *UNKNOWN_EXITS])
async def test_inc9i_ux_f1_the_stale_category_is_never_split_across_lines(
        tmp_path, monkeypatch, category, size):
    """`INC9I-CR-F1`: every category the panel can name, on its own line under the label.
    At 30 cells `▲ cached copy: host not found` would fit on one row, so the 'own line'
    claim is asserted on the row, not only on the category being present."""
    monkeypatch.setattr(test_inc9h, "_StaleMirror", _CategoryMirror)
    got = await _connect(tmp_path, monkeypatch, category, size, stale=True)
    rows = [" ".join(r.split()) for r in got["frame"].split("\n")]
    assert any(category in row for row in rows), (category, [r for r in rows if r][:14])
    label_rows = [r for r in rows if "▲ cached copy:" in r]
    assert len(label_rows) == 1 and category not in label_rows[0], (category, label_rows)
    assert "▲ cached copy:" in got["painted"] and category in got["painted"], got["painted"]


# ---------------------------------------------------------------------------
# INC9H-SEC-F2 -- a credential typed in the URL is refused before any process starts

CREDENTIALED = ["https://u:tok3n-x@example.invalid/o/r", "https://tok3n-x@example.invalid/o/r.git",
                "http://u:@example.invalid/o/r"]


@red("creds")
@pytest.mark.parametrize("url", CREDENTIALED)
def test_inc9i_sec_f2_userinfo_in_a_typed_url_is_refused_before_any_process(url, tmp_path, monkeypatch):
    run = _Run(returncode=0)
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector(url, cache_dir=tmp_path / "cache").fetch()
    message = str(caught.value)
    assert run.calls == [], run.calls
    assert "credential helper" in message and message.startswith("refusing"), message
    for typed in ("tok3n", "u:", "example", "@", "o/r"):
        assert typed not in message, (typed, message)
    assert not (tmp_path / "cache").exists(), "no directory was made for a refused URL"


def test_inc9i_sec_f2_a_url_without_userinfo_and_an_scp_style_address_still_connect(tmp_path, monkeypatch):
    for url in ("https://example.invalid/o/r.git", "https://example.invalid/o/r@v2",
                "git@example.invalid:o/r.git"):
        run = _Run(returncode=0)
        monkeypatch.setattr("subprocess.run", run)
        try:
            GitHubConnector(url, cache_dir=tmp_path / "cache").fetch()
        except GitHubError as exc:
            assert "credential" not in str(exc), (url, str(exc))
        assert any(argv[:3] == ["git", "clone", "--mirror"] for argv, _ in run.calls), (url, run.calls)
