"""Inc-9l -- fixes for the findings of the Inc-9k reviews and the operator's Round 9 (T1).

Authority: `A-120` and `VERDICT-inc9-2026-09-30.md` Rounds 8 and 9 (S1, T1, T2, T3).  Every arm a
fix closes was committed RED first as a STRICT xfail keyed by the step that closes it (`OPEN_STEPS`);
an arm that is not keyed is a pin (green on the base), killed by a mutant instead.

Nothing here reaches the network, the real cache or the real `gh`: every git or gh call is stubbed,
HOME and USERPROFILE point at `tmp_path`, and no real UNC path is ever opened: a stub fails the test
if a filesystem call is made for one.  Control characters and non-ASCII are `\\u` escapes (this file
is ASCII); no user-profile path is typed.
"""
from __future__ import annotations

import os
import pathlib
from urllib.parse import quote

import pytest
from textual.widgets import Static

from mapper import github
from mapper.app import MapperApp, PlugRepoScreen, RepoScreen
from mapper.github import GitHubConnector, GitHubError
from tests.test_inc9f import NARROW, SIZE, _Run, hermetic  # noqa: F401
from tests.test_inc9j import _Boom, _type_and_connect
from tests.test_repair_layout import _frame_rows, _rows_in

OPEN_STEPS: set[str] = {"t1", "total", "unc", "mirror", "obs1", "quote"}


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9l: committed RED; closed by the '{step}' step")
    return lambda fn: fn


SENTENCE = ("refusing the repository: use https://host/path, git@host:path, owner/name "
            "or a local folder")
UNRECOGNISED = "(unrecognised URL)"
UNC_FORMS = [
    "\\\\host\\share",
    "\\\\host\\share\\repo",
    "//host/share/repo",
    "\\\\?\\C:\\x",
    "\\\\?\\UNC\\host\\share",
    "\\\\.\\pipe\\x",
    "//./pipe/x",
    "/\\host/share",
    "\\/host/share",
]


def _flat(screen) -> str:
    return " ".join("\n".join(_frame_rows(screen)).split())


def _squash(text: str) -> str:
    return text.replace(" ", "")


# ---------------------------------------------------------------------------
# T1 -- the one fixed sentence says how to write an accepted repository

@red("t1")
@pytest.mark.parametrize("spec", ["a/b/c", "plainword", "https://u:tok@h/o/r", "http://h/o/r", "o/r?x"])
def test_inc9l_t1_the_one_sentence_names_the_accepted_forms_and_echoes_nothing(spec, tmp_path, monkeypatch):
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector(spec, cache_dir=tmp_path / "cache").fetch()
    assert str(caught.value) == SENTENCE, str(caught.value)
    assert run.calls == [] and not (tmp_path / "cache").exists()


@red("t1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9l_t1_the_refusal_screen_paints_the_sentence(tmp_path, monkeypatch, size):
    typed = "https://user:tok@example.invalid/o/r.git"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr("subprocess.run", _Boom())
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await _type_and_connect(app, pilot, typed)
        flat = _flat(app.screen)
        assert _squash(SENTENCE) in _squash(flat), flat
        assert "tok" not in flat and "user:" not in flat, flat


# ---------------------------------------------------------------------------
# INC9K-SEC-F1 -- `_is_local_path` is total: no text makes it raise

class _Unresolvable:
    def __init__(self, exc):
        self.exc = exc

    def __call__(self, path_self):
        raise self.exc


@red("total")
@pytest.mark.parametrize("exc", [RuntimeError("Could not determine home directory."),
                                 OSError("boom"), ValueError("embedded null byte")])
def test_inc9l_sec_f1_the_local_path_predicate_never_raises(exc, monkeypatch):
    monkeypatch.setattr(pathlib.Path, "expanduser", _Unresolvable(exc))
    assert github._is_local_path("~nosuchuser:tok@h/o/r") is False
    assert github.painted_repo("~nosuchuser:tok@h/o/r") == UNRECOGNISED


@red("total")
def test_inc9l_sec_f1_fetch_refuses_with_the_fixed_sentence_not_an_unexpected_error(tmp_path, monkeypatch):
    monkeypatch.setattr(pathlib.Path, "expanduser", _Unresolvable(RuntimeError("x")))
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector("~nosuchuser:tok@h/o/r", cache_dir=tmp_path / "cache").fetch()
    assert str(caught.value) == SENTENCE and run.calls == [], (str(caught.value), run.calls)


def test_inc9l_sec_f1_a_text_that_embeds_a_null_byte_is_not_a_folder():
    assert github._is_local_path("a\x00b") is False


@red("total")
@pytest.mark.parametrize("stubbed", [False, True])
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9l_sec_f1_a_typed_tilde_user_reaches_the_screen_and_the_app_survives(
        tmp_path, monkeypatch, size, stubbed):
    typed = "~nosuchuser:tok@h/o/r"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr("subprocess.run", _Boom())
    if stubbed:
        real = pathlib.Path.expanduser

        def expanduser(path_self):
            if str(path_self).startswith("~nosuchuser"):
                raise RuntimeError("Could not determine home directory.")
            return real(path_self)

        monkeypatch.setattr(pathlib.Path, "expanduser", expanduser)
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await _type_and_connect(app, pilot, typed)
        assert isinstance(app.screen, RepoScreen) and app.is_running
        flat = _flat(app.screen)
        assert _squash(UNRECOGNISED) in _squash(flat), flat
        assert "tok" not in flat and "nosuchuser" not in flat, flat
        assert "unexpected" not in flat and "RuntimeError" not in flat, flat
        if stubbed:
            assert _squash(SENTENCE) in _squash(flat), flat


# ---------------------------------------------------------------------------
# UNC hardening -- a text starting with two slashes is not a local folder and touches no filesystem

class _FsSpy:
    """Wraps the `Path`/`os.path` probes; records a call made for a text that starts with two slashes."""

    def __init__(self, monkeypatch):
        self.hits: list[str] = []
        for name in ("is_dir", "exists", "stat", "lstat", "is_file", "resolve", "samefile"):
            real = getattr(pathlib.Path, name)
            monkeypatch.setattr(pathlib.Path, name, self._wrap(name, real))
        for name in ("isdir", "exists", "isfile", "realpath"):
            real = getattr(os.path, name)
            monkeypatch.setattr(os.path, name, self._wrap_os(name, real))

    def _note(self, name, value):
        self.hits.append(f"{name}({value})")

    @staticmethod
    def _is_double_slash(value) -> bool:
        return str(value).replace("/", "\\").startswith("\\\\")

    def _wrap(self, name, real):
        def probe(path_self, *a, **kw):
            if self._is_double_slash(path_self):
                self._note(name, path_self)
                if name in ("stat", "lstat"):
                    raise OSError("blocked: no filesystem call for a double-slash text")
                return path_self if name == "resolve" else False
            return real(path_self, *a, **kw)
        return probe

    def _wrap_os(self, name, real):
        def probe(value, *a, **kw):
            if self._is_double_slash(value):
                self._note("os.path." + name, value)
                return value if name == "realpath" else False
            return real(value, *a, **kw)
        return probe


@red("unc")
@pytest.mark.parametrize("typed", UNC_FORMS)
def test_inc9l_unc_a_double_slash_text_touches_no_filesystem_and_is_refused(typed, tmp_path, monkeypatch):
    spy = _FsSpy(monkeypatch)
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    assert github._is_local_path(typed) is False
    assert github.painted_repo(typed) == UNRECOGNISED
    assert spy.hits == [], spy.hits
    with pytest.raises(GitHubError) as caught:
        GitHubConnector(typed, cache_dir=tmp_path / "cache").fetch()
    assert spy.hits == [] and run.calls == [], (spy.hits, run.calls)
    assert str(caught.value) == SENTENCE, str(caught.value)


@pytest.mark.parametrize("typed", ["relative/dir", "o/r", "C:\\work\\repo", "/tmp/x"])
def test_inc9l_unc_a_single_slash_or_drive_text_is_still_probed(typed, monkeypatch):
    """The refusal is for two leading slashes only: an ordinary path is still looked at."""
    seen: list[str] = []
    real = pathlib.Path.is_dir

    def is_dir(path_self):
        seen.append(str(path_self))
        return real(path_self)

    monkeypatch.setattr(pathlib.Path, "is_dir", is_dir)
    github._is_local_path(typed)
    assert seen, typed


@red("unc")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9l_unc_a_typed_unc_path_paints_unrecognised_with_the_sentence(tmp_path, monkeypatch, size):
    spy = _FsSpy(monkeypatch)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr("subprocess.run", _Boom())
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await _type_and_connect(app, pilot, "\\\\host\\share")
        flat = _flat(app.screen)
        assert _squash(UNRECOGNISED) in _squash(flat), flat
        assert _squash(SENTENCE) in _squash(flat), flat
        assert "share" not in flat, flat
    assert spy.hits == [], spy.hits


# ---------------------------------------------------------------------------
# INC9K-CR-F2 -- `painted_repo` mirrors `fetch` exactly

CONSISTENCY = [
    # the six measured painted-but-refused forms
    "git@h:r", "https://h/...", "https://h/o/.git", "https://h/o/..git", "-a/b", "-x",
    # accepted URLs
    "https://h/o/r", "https://h/o/r.git", "https://h/o/r/", "https://h:8443/o/r.git",
    "https://github.example.invalid/o/r", "git@h:o/r.git", "git@h:o/r/", "https://1.2.3.4/o/r",
    "https://h/o/some-name_v2~x.git", "git@h:o/r",
    # url-shaped and refused
    "https://u:tok@h/o/r", "http://h/o/r", "https://h/o/r?x=1", "https://h/o/r#f", "HTTPS://h/o/r",
    "https://h/o/./r", "https://h/o/../r", "https://h//r", "git@h:/o/r", "git@h:o/../r",
    "https://h/..", "https://h/o/r\n", "ssh://git@h/o/r", "file:///etc/passwd",
    # owner/name
    "o/r", "owner/some.name-1", "a/b/c", "o/..", "bad owner/x", "plainword",
    # transport helpers and dashes
    "ext::sh -c x", "--upload-pack=x",
    # local folders ({T} is the temp dir)
    "{T}/work", "work", "{T}/plain", "{T}/missing", "missing/dir", "./user:tok@missing/dir",
    "{T}/-x", "dashdir/-x",
    # not a folder, whatever the platform
    "~nosuchuser:tok@h/o/r", "\\\\host\\share", "//host/share/repo", "\\\\?\\C:\\x", "",
    "   ",
]


def _tree(tmp_path):
    for rel in ("work/.git", "plain", "-x/.git", "dashdir/-x/.git"):
        (tmp_path / rel).mkdir(parents=True)


def test_inc9l_cr_f2_the_consistency_table_is_at_least_forty_inputs():
    assert len(CONSISTENCY) >= 40 and len(set(CONSISTENCY)) == len(CONSISTENCY)


# Measured RED on the base (the six painted-but-refused forms, and the `~user` crash); the rest are pins.
_RED_ON_BASE = set(CONSISTENCY[:6]) | {"~nosuchuser:tok@h/o/r"}


def _consistency_params():
    out = []
    for i, raw in enumerate(CONSISTENCY):
        marks = []
        if raw in _RED_ON_BASE and "mirror" in OPEN_STEPS:
            marks.append(pytest.mark.xfail(
                strict=True, reason="Inc-9l: committed RED; closed by the 'mirror' step"))
        out.append(pytest.param(raw, id=f"c{i:02d}", marks=marks))
    return out


@pytest.mark.parametrize("raw", _consistency_params())
def test_inc9l_cr_f2_painted_repo_is_painted_exactly_when_fetch_reaches_a_process(raw, tmp_path, monkeypatch):
    _tree(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    typed = raw.replace("{T}", str(tmp_path))
    run = _Run(returncode=128, stderr="fatal: Could not resolve host: x\n")
    monkeypatch.setattr("subprocess.run", run)
    try:
        GitHubConnector(typed, cache_dir=tmp_path / "cache").fetch()
    except GitHubError:
        pass
    painted = github.painted_repo(typed)
    assert (painted != UNRECOGNISED) == bool(run.calls), (typed, painted, run.calls)
    if painted != UNRECOGNISED:
        assert painted == typed


# ---------------------------------------------------------------------------
# INC9K-CR-F1 -- a text that is not a git folder is never painted (pins, killed by mutants)

def test_inc9l_cr_f1_a_plain_directory_without_dot_git_is_not_painted(tmp_path):
    (tmp_path / "plain").mkdir()
    assert github.painted_repo(str(tmp_path / "plain")) == UNRECOGNISED


def test_inc9l_cr_f1_a_missing_absolute_path_is_not_painted(tmp_path):
    assert github.painted_repo(str(tmp_path / "does" / "not" / "exist")) == UNRECOGNISED


def test_inc9l_cr_f1_a_missing_relative_path_with_a_credential_is_not_painted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for typed in ("./user:tok@missing/dir", "..\\user:tok@missing", "sub/user:tok@host/o/r"):
        assert github.painted_repo(typed) == UNRECOGNISED, typed


# ---------------------------------------------------------------------------
# OBS-1 -- an upper-case github URL does not crash the connect screen

@red("obs1")
@pytest.mark.parametrize("typed,expected", [
    ("HTTPS://GITHUB.COM/o/n", "o/n"),
    ("Https://GitHub.com/o/n.git", "o/n"),
    ("HTTP://GITHUB.COM/o/n", "o/n"),
    ("https://GITHUB.com/o/n/", "o/n"),
])
def test_inc9l_obs1_the_github_rewrite_is_case_consistent(typed, expected):
    assert PlugRepoScreen._normalize_repo(typed) == expected


@pytest.mark.parametrize("typed,expected", [
    ("https://github.com/o/n", "o/n"),
    ("http://github.com/o/n.git", "o/n"),
    ("git@github.com:o/n.git", "o/n"),
    ("o/n", "o/n"),
    ("https://example.invalid/o/n", "https://example.invalid/o/n"),
    ("  ", ""),
])
def test_inc9l_obs1_the_lower_case_forms_still_rewrite(typed, expected):
    assert PlugRepoScreen._normalize_repo(typed) == expected


@red("obs1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9l_obs1_an_upper_case_github_url_typed_with_real_keys_survives(tmp_path, monkeypatch, size):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr(
        "subprocess.run", _Run(returncode=1, stderr="gh: Could not resolve to a Repository (HTTP 404)\n"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await _type_and_connect(app, pilot, "HTTPS://GITHUB.COM/o/n")
        assert app.is_running and isinstance(app.screen, RepoScreen)
        assert app.screen.repo == "o/n", app.screen.repo
        name = app.screen.query_one("#repo-name", Static)
        shown = "".join("\n".join(_rows_in(app.screen, name.region)).split())
        assert shown == "o/n", shown


# ---------------------------------------------------------------------------
# INC9K-SEC-F2 -- an API-derived name is one path segment of a `gh api` path

HOSTILE_BRANCHES = ["%2e%2e/%2e%2e/user", "x#frag", "{owner}", "feature/x", "a?b=c", "../up"]


@red("quote")
def test_inc9l_sec_f2_branch_and_default_branch_names_are_encoded_in_gh_api_paths(monkeypatch):
    api: list[str] = []
    default = "{repo}/../d#e"
    sha = "a/../b{x}"

    def fake_gh(self, args):
        if args[:2] == ["repo", "view"]:
            return {"name": "r", "defaultBranchRef": {"name": default}}
        path = args[1]
        api.append(path)
        if "/branches?" in path:
            return [{"name": b} for b in HOSTILE_BRANCHES]
        if path.endswith("/tags?per_page=20"):
            return []
        if "/compare/" in path:
            return {"ahead_by": 0, "behind_by": 0}
        if "/check-runs" in path:
            return {"check_runs": []}
        return {"sha": sha, "commit": {"committer": {"date": "2026-01-01T00:00:00Z"}}}

    monkeypatch.setattr(GitHubConnector, "_gh", fake_gh)
    GitHubConnector("o/r")._fetch_gh()

    def enc(name):
        return quote(name, safe="")

    for b in HOSTILE_BRANCHES:
        assert f"repos/o/r/compare/{enc(default)}...{enc(b)}" in api, (b, api)
        assert f"repos/o/r/commits/{enc(b)}" in api, (b, api)
    assert f"repos/o/r/commits/{enc(sha)}/check-runs" in api, api
    for path in api:
        if "/compare/" in path or "/commits/" in path:
            assert "{" not in path and "#" not in path and "?" not in path, path
            assert ".." not in path.replace("...", "", 1).split("/"), path


def test_inc9l_sec_f2_a_plain_branch_name_is_unchanged(monkeypatch):
    api: list[str] = []

    def fake_gh(self, args):
        if args[:2] == ["repo", "view"]:
            return {"name": "r", "defaultBranchRef": {"name": "main"}}
        api.append(args[1])
        if "/branches?" in args[1]:
            return [{"name": "dev-1.x"}]
        if "/tags?" in args[1]:
            return []
        if "/compare/" in args[1]:
            return {"ahead_by": 1, "behind_by": 2}
        return {}

    monkeypatch.setattr(GitHubConnector, "_gh", fake_gh)
    graph = GitHubConnector("o/r")._fetch_gh()
    assert "repos/o/r/compare/main...dev-1.x" in api and "repos/o/r/commits/dev-1.x" in api, api
    assert graph.nodes["dev-1.x"].ficha.meta == "+1/-2"
