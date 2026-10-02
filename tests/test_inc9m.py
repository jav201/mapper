"""Inc-9m -- fixes for the Inc-9l reviews: a closed allow-list for local paths (S1 applied to paths).

Authority: `A-121` and `VERDICT-inc9-2026-09-30.md` Rounds 8 and 9 (S1 closed allow-list, T1 sentence).
Every arm a fix closes was committed RED first as a STRICT xfail keyed by the step that closes it
(`OPEN_STEPS`); an arm that is not keyed is a pin (green on the base), killed by a mutant instead.

Nothing here reaches the network, the real cache or the real `gh`: git and gh calls are stubbed, HOME and
USERPROFILE point at `tmp_path`, and NO real UNC or NT-namespace path is ever opened: a spy fails the test
(and records the hit) if a filesystem call is made for one.  Control characters are `\\u` escapes (this
file is ASCII); no user-profile path is typed.
"""
from __future__ import annotations

import ast
import contextlib
import os
import pathlib
import sys
import types

import pytest

from mapper import github, osopen
from mapper.app import MapperApp, RepoScreen, _PromptScreen
from mapper.github import GitHubConnector, GitHubError
from mapper.model import Document, Edge, Ficha, Graph, Node
from mapper.screens.factory import FactoryScreen
from tests.test_inc9f import NARROW, SIZE, _Run  # noqa: F401
from tests.test_inc9j import _Boom
from tests.test_repair_layout import _frame_rows

OPEN_STEPS: set[str] = set()

REPO_ROOT = pathlib.Path(github.__file__).parent


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9m: committed RED; closed by the '{step}' step")
    return lambda fn: fn


def _red_mark(step: str):
    return ([pytest.mark.xfail(strict=True, reason=f"Inc-9m: committed RED; closed by the '{step}' step")]
            if step in OPEN_STEPS else [])


UNRECOGNISED = "(unrecognised URL)"
# `U1` (Inc-9n): the refusal of a text outside the allow-list, with a real ellipsis written as an escape.
U1 = "path not supported: use C:\\\u2026 or a relative path"
SENTENCE = ("refusing the repository: use https://host/path, git@host:path, owner/name "
            "or a local folder")

# The forms the ruling names.  `DOUBLE` are refused by the Inc-9l two-slash rule already (pins on the
# base); the others slipped past it and are RED on the base.
DOUBLE = ["\\\\h\\s", "//h/s", "\\\\?\\C:\\x", "\\\\.\\pipe\\x"]
SLIPPED = ["\\??\\UNC\\h\\s", "/??/UNC/h/s", "\\??\\GLOBALROOT\\Device\\Mup\\h\\s", "\\??\\C:\\Windows",
           "\\single", "C:x"]
HOSTILE = DOUBLE + SLIPPED
UNC_HOME = "\\\\h\\s\\me"


def _is_double(text: str) -> bool:
    return len(text) >= 2 and text[0] in "\\/" and text[1] in "\\/"


def _norm(value) -> str:
    return str(value).replace("/", "\\")


def _flat(screen) -> str:
    return " ".join("\n".join(_frame_rows(screen)).split())


def _squash(text: str) -> str:
    return text.replace(" ", "")


# ---------------------------------------------------------------------------
# The spies.  `_no_fs` fails on ANY filesystem call (unit arms); `_Hostile` fails only for a path built
# from the typed hostile text (Pilot arms: the app itself uses the filesystem all the time).

def _nt():
    return sys.modules.get("nt")


@contextlib.contextmanager
def _no_fs(monkeypatch):
    hits: list[str] = []

    def boom(name):
        def call(*a, **kw):
            hits.append(name)
            raise AssertionError(f"a filesystem call was made: {name}")
        return call

    with monkeypatch.context() as m:
        for name in ("stat", "lstat", "scandir", "listdir"):
            m.setattr(os, name, boom("os." + name))
        for name in ("exists", "isdir", "isfile", "islink", "lexists", "realpath", "getsize", "samefile"):
            if hasattr(os.path, name):
                m.setattr(os.path, name, boom("os.path." + name))
        for name in ("is_dir", "exists", "is_file", "resolve", "stat", "lstat", "samefile", "iterdir", "glob"):
            m.setattr(pathlib.Path, name, boom("Path." + name))
        nt = _nt()
        if nt is not None and hasattr(nt, "_getfinalpathname"):
            m.setattr(nt, "_getfinalpathname", boom("nt._getfinalpathname"))
        # `INC9O-SEC-F4`: `os.path.realpath` binds `_getfinalpathname` by NAME inside `ntpath`, so patching
        # `nt` alone leaves the call unseen.
        ntp = sys.modules.get("ntpath")
        if ntp is not None and hasattr(ntp, "_getfinalpathname"):
            m.setattr(ntp, "_getfinalpathname", boom("ntpath._getfinalpathname"))
        yield hits


class _Hostile:
    """Records (and for stat-like calls refuses) a filesystem call whose path contains a hostile form."""

    def __init__(self, monkeypatch, forms):
        self.hits: list[str] = []
        self.forms = [_norm(f) for f in forms]
        for name in ("is_dir", "exists", "stat", "lstat", "is_file", "resolve", "samefile"):
            monkeypatch.setattr(pathlib.Path, name, self._wrap(name, getattr(pathlib.Path, name)))
        for name in ("stat", "lstat"):
            monkeypatch.setattr(os, name, self._wrap_fn("os." + name, getattr(os, name)))
        for name in ("isdir", "exists", "isfile", "realpath"):
            monkeypatch.setattr(os.path, name, self._wrap_fn("os.path." + name, getattr(os.path, name)))
        nt = _nt()
        if nt is not None and hasattr(nt, "_getfinalpathname"):
            monkeypatch.setattr(nt, "_getfinalpathname",
                                self._wrap_fn("nt._getfinalpathname", nt._getfinalpathname))

    def _bad(self, value) -> bool:
        return isinstance(value, (str, os.PathLike)) and any(f in _norm(value) for f in self.forms)

    def _wrap(self, name, real):
        def probe(path_self, *a, **kw):
            if self._bad(path_self):
                self.hits.append(f"Path.{name}({path_self})")
                raise OSError("blocked: a filesystem call for a hostile text")
            return real(path_self, *a, **kw)
        return probe

    def _wrap_fn(self, name, real):
        def probe(value, *a, **kw):
            if self._bad(value):
                self.hits.append(f"{name}({value})")
                raise OSError("blocked: a filesystem call for a hostile text")
            return real(value, *a, **kw)
        return probe


# ---------------------------------------------------------------------------
# S1 applied to paths -- the grammar of `safe_local_path`

ACCEPTED = ["C:\\x", "C:/x/y", "z:\\", "o/r", "work", ".\\x", "..\\x", "sub dir\\f.csv", "C:\\a b\\c"]
REFUSED = [
    "", "a\x00b", "-x", "-a/b", "\\\\h\\s", "//h/s", "\\\\?\\C:\\x", "\\\\.\\pipe\\x",
    "\\??\\UNC\\h\\s", "/??/UNC/h/s", "\\??\\GLOBALROOT\\Device\\Mup\\h\\s", "\\??\\C:\\Windows",
    "\\single", "/single", "/tmp/x", "C:x", "C:", "1:\\x", "\\\\h\\s\\x.pdf",
    "\\/h/s", "/\\h/s",
]


@red("s1")
@pytest.mark.parametrize("text", ACCEPTED)
def test_inc9m_s1_an_accepted_text_is_a_drive_absolute_or_a_relative_path(text):
    got = osopen.safe_local_path(text)
    assert got is not None and isinstance(got, pathlib.Path), (text, got)
    assert str(got).replace("/", "\\") == str(pathlib.PureWindowsPath(text)).replace("/", "\\"), (text, got)


@red("s1")
@pytest.mark.parametrize("text", REFUSED)
def test_inc9m_s1_every_other_text_is_refused_before_any_filesystem_call(text, monkeypatch):
    with _no_fs(monkeypatch) as hits:
        assert osopen.safe_local_path(text) is None, text
    assert hits == []


@red("s1")
def test_inc9m_s1_a_tilde_that_expands_to_unc_is_refused_without_a_filesystem_call(monkeypatch):
    monkeypatch.setenv("USERPROFILE", UNC_HOME)
    monkeypatch.setenv("HOME", UNC_HOME)
    with _no_fs(monkeypatch) as hits:
        assert osopen.safe_local_path("~/x") is None
        assert osopen.safe_local_path("~") is None
    assert hits == []


@red("s1")
def test_inc9m_s1_a_tilde_with_a_drive_absolute_home_is_accepted(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    got = osopen.safe_local_path("~/x")
    assert got is not None and _norm(got) == _norm(tmp_path / "x"), got


@red("s1")
@pytest.mark.parametrize("exc", [RuntimeError("no home"), OSError("boom"), ValueError("nul")])
def test_inc9m_s1_expanduser_failing_is_a_refusal_not_an_exception(exc, monkeypatch):
    def expanduser(path_self):
        raise exc

    monkeypatch.setattr(pathlib.Path, "expanduser", expanduser)
    assert osopen.safe_local_path("~nosuchuser/x") is None


@red("one")
def test_inc9m_s1_one_helper_is_imported_by_the_three_callers():
    from mapper import app as app_mod
    from mapper.screens import factory as factory_mod

    for mod in (github, app_mod, factory_mod):
        assert getattr(mod, "safe_local_path", None) is osopen.safe_local_path, mod.__name__
    for rel in ("github.py", "app.py", "screens/factory.py"):
        tree = ast.parse((REPO_ROOT / rel).read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr == "expanduser"]
        assert calls == [], (rel, [c.lineno for c in calls])


# ---------------------------------------------------------------------------
# INC9L-SEC-F1 / CR-F1 -- `_is_local_path` uses the helper: no filesystem call for a hostile text

def _predicate_params():
    return [pytest.param(t, marks=([] if _is_double(t) else _red_mark("s1"))) for t in HOSTILE]


@pytest.mark.parametrize("typed", _predicate_params())
def test_inc9m_sec_f1_a_hostile_local_text_touches_no_filesystem_and_is_refused(typed, tmp_path, monkeypatch):
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    cache = str(tmp_path / "cache")
    with _no_fs(monkeypatch) as hits:
        assert github._is_local_path(typed) is False
        assert github.painted_repo(typed) == UNRECOGNISED
        with pytest.raises(GitHubError) as caught:
            GitHubConnector(typed, cache_dir=cache).fetch()
    assert hits == [] and run.calls == [], (hits, run.calls)
    assert str(caught.value) == SENTENCE, str(caught.value)


@red("s1")
def test_inc9m_sec_f1_a_tilde_expanding_to_unc_touches_no_filesystem(tmp_path, monkeypatch):
    monkeypatch.setenv("USERPROFILE", UNC_HOME)
    monkeypatch.setenv("HOME", UNC_HOME)
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    cache = str(tmp_path / "cache")
    with _no_fs(monkeypatch) as hits:
        assert github._is_local_path("~/x") is False
        assert github.painted_repo("~/x") == UNRECOGNISED
        with pytest.raises(GitHubError):
            GitHubConnector("~/x", cache_dir=cache).fetch()
    assert hits == [] and run.calls == [], (hits, run.calls)


def test_inc9m_sec_f1_pin_a_drive_absolute_path_is_probed(tmp_path):
    (tmp_path / "work" / ".git").mkdir(parents=True)
    assert github._is_local_path(str(tmp_path / "work")) is True
    assert github._is_local_path(str(tmp_path / "work").replace("\\", "/")) is True
    assert github._is_local_path(str(tmp_path / "missing")) is False


def test_inc9m_sec_f1_pin_a_relative_git_directory_is_probed(tmp_path, monkeypatch):
    (tmp_path / "o" / "r" / ".git").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    assert github._is_local_path("o/r") is True
    assert github._is_local_path("o\\r") is True


def test_inc9m_sec_f1_pin_a_tilde_with_a_drive_absolute_home_is_probed(tmp_path, monkeypatch):
    (tmp_path / "x" / ".git").mkdir(parents=True)
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path))
    assert github._is_local_path("~/x") is True
    assert github.painted_repo("~/x") == "~/x"


# ---------------------------------------------------------------------------
# INC9L-SEC-F2 -- the import prompts survive `~nosuchuser...` and echo nothing

async def _open_prompt(app, pilot, key, typed):
    toasts: list[str] = []
    real_notify = app.notify

    def notify(message, **kw):
        toasts.append(str(message))
        return real_notify(message, **kw)

    app.notify = notify
    await pilot.press(key)
    await pilot.pause()
    assert isinstance(app.screen, _PromptScreen), app.screen
    await pilot.press(*typed)
    await pilot.press("enter")
    for _ in range(6):
        await pilot.pause()
    return toasts


def _office_graph():
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="proceso")))
    g.documents["plantilla"] = Document(name="plantilla", path="x.docx", kind="docx", template=True)
    return g


def _env(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))


@red("u1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9m_sec_f2_import_csv_survives_a_tilde_nosuchuser_and_paints_nothing_typed(
        tmp_path, monkeypatch, size):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", "~nosuchuser/secret-token.csv")
        assert app.is_running
        frame = _flat(app.screen)
        assert "secret-token" not in frame and "nosuchuser" not in frame, frame
        assert not any("secret-token" in t or "nosuchuser" in t for t in toasts), toasts
        assert U1 in toasts and "archivo no encontrado" not in toasts, toasts


@red("u1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9m_sec_f2_import_office_survives_a_tilde_nosuchuser_and_paints_nothing_typed(
        tmp_path, monkeypatch, size):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.push_screen(FactoryScreen(_office_graph(), process_name="demo"))
        await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", "~nosuchuser/secret-token.docx")
        assert app.is_running
        frame = _flat(app.screen)
        assert "secret-token" not in frame and "nosuchuser" not in frame, frame
        assert not any("secret-token" in t or "nosuchuser" in t for t in toasts), toasts
        assert U1 in toasts and "archivo no encontrado" not in toasts, toasts


@red("u1")
@pytest.mark.parametrize("surface", ["csv", "office"])
async def test_inc9m_sec_f2_a_typed_unc_path_causes_no_filesystem_call(tmp_path, monkeypatch, surface):
    _env(monkeypatch, tmp_path)
    spy = _Hostile(monkeypatch, ["\\\\h\\s\\x"])
    ext = "csv" if surface == "csv" else "docx"
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        if surface == "office":
            app.push_screen(FactoryScreen(_office_graph(), process_name="demo"))
            await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", f"\\\\h\\s\\x.{ext}")
        assert app.is_running
        assert U1 in toasts and "archivo no encontrado" not in toasts, toasts
        assert not any("x." + ext in t for t in toasts), toasts
    assert spy.hits == [], spy.hits


async def test_inc9m_sec_f2_pin_a_missing_drive_absolute_csv_still_names_its_file(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", str(tmp_path / "missing.csv"))
        assert app.is_running and "archivo no encontrado: missing.csv" in toasts, toasts


# ---------------------------------------------------------------------------
# INC9L-SEC-F5 -- `open_external` checks a file target before `resolve()`

class _Launcher:
    def __init__(self):
        self.calls: list[str] = []

    def __call__(self, target):
        self.calls.append(target)


@red("f5")
@pytest.mark.parametrize("target", ["\\\\h\\s\\x.pdf", "//h/s/x.pdf", "\\??\\UNC\\h\\s\\x.pdf"])
def test_inc9m_sec_f5_a_hostile_file_target_is_refused_before_resolve(target, tmp_path, monkeypatch):
    spy = _Hostile(monkeypatch, ["\\\\h\\s\\x.pdf", "\\??\\UNC\\h\\s\\x.pdf"])
    launcher = _Launcher()
    status = osopen.open_external("file", target, workspace=tmp_path, launcher=launcher)
    assert status == osopen.REFUSED_TYPE, status
    assert launcher.calls == [] and spy.hits == [], (launcher.calls, spy.hits)


def test_inc9m_sec_f5_pin_a_relative_file_inside_the_workspace_still_opens(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.pdf").write_bytes(b"x")
    launcher = _Launcher()
    assert osopen.open_external("file", "docs/a.pdf", workspace=tmp_path, launcher=launcher) == osopen.OK
    assert len(launcher.calls) == 1


def test_inc9m_sec_f5_pin_a_drive_absolute_file_outside_is_still_outside(tmp_path):
    outside = tmp_path.parent / "elsewhere.pdf"
    launcher = _Launcher()
    status = osopen.open_external("file", str(outside), workspace=tmp_path, launcher=launcher)
    assert status == osopen.REFUSED_OUTSIDE and launcher.calls == []


# ---------------------------------------------------------------------------
# INC9L-SEC-F3 / F4 / CR-F5 -- API-derived data in `gh api` paths

def _stub_gh(monkeypatch, *, branches, tags, sha, default="main", tag_commit_date="2026-02-03T00:00:00Z"):
    api: list[list[str]] = []

    def fake_gh(self, args):
        api.append(list(args))
        if args[:2] == ["repo", "view"]:
            return {"name": "r", "defaultBranchRef": {"name": default}}
        path = args[1]
        if "/branches?" in path:
            return branches
        if path.endswith("/tags?per_page=20"):
            return tags
        if "/compare/" in path:
            return {"ahead_by": 0, "behind_by": 0}
        if "/check-runs" in path:
            return {"check_runs": []}
        if "/commits/" in path:
            return {"sha": sha, "commit": {"committer": {"date": tag_commit_date}}}
        return {}

    monkeypatch.setattr(GitHubConnector, "_gh", fake_gh)
    return api


def _segments(argv: list[str]) -> list[str]:
    out: list[str] = []
    for item in argv:
        out.extend(item.split("?")[0].split("/"))
    return out


@red("f3")
def test_inc9m_sec_f3_a_dot_or_dotdot_branch_or_sha_builds_no_path(monkeypatch):
    api = _stub_gh(monkeypatch, branches=[{"name": ".."}, {"name": "."}, {"name": "ok"}], tags=[], sha=".")
    graph = GitHubConnector("o/r")._fetch_gh()
    for argv in api:
        assert all(seg not in (".", "..") for seg in _segments(argv)), argv
    assert "ok" in graph.nodes and ".." not in graph.nodes and "." not in graph.nodes
    assert not any("/check-runs" in a[1] for a in api if len(a) > 1), api


@red("f3")
def test_inc9m_sec_f3_a_dotdot_sha_is_not_a_path_either(monkeypatch):
    api = _stub_gh(monkeypatch, branches=[{"name": "ok"}], tags=[], sha="..")
    GitHubConnector("o/r")._fetch_gh()
    for argv in api:
        assert all(seg not in (".", "..") for seg in _segments(argv)), argv


@red("f3")
@pytest.mark.parametrize("default", [".", ".."])
def test_inc9m_sec_f3_a_dot_default_branch_is_refused_before_any_path(default, monkeypatch):
    api = _stub_gh(monkeypatch, branches=[{"name": "ok"}], tags=[], sha="abc", default=default)
    with pytest.raises(GitHubError):
        GitHubConnector("o/r")._fetch_gh()
    assert [a for a in api if a[0] == "api"] == [], api


def test_inc9m_sec_f3_pin_ordinary_names_still_build_their_paths(monkeypatch):
    api = _stub_gh(monkeypatch, branches=[{"name": "dev-1.x"}], tags=[], sha="abc")
    GitHubConnector("o/r")._fetch_gh()
    paths = [a[1] for a in api if a[0] == "api"]
    assert "repos/o/r/compare/main...dev-1.x" in paths and "repos/o/r/commits/dev-1.x" in paths, paths
    assert "repos/o/r/commits/abc/check-runs" in paths, paths


@red("f4")
def test_inc9m_sec_f4_the_tag_commit_url_is_never_followed(monkeypatch):
    tags = [{"name": "v1", "commit": {"sha": "abc123", "url": "https://evil.example/x"}},
            {"name": "v2", "commit": {"sha": "def456", "url": "-XDELETE"}}]
    api = _stub_gh(monkeypatch, branches=[], tags=tags, sha="zzz")
    graph = GitHubConnector("o/r")._fetch_gh()
    flat = [part for argv in api for part in argv]
    assert not any("evil.example" in p or "XDELETE" in p for p in flat), api
    paths = [a[1] for a in api if a[0] == "api"]
    assert "repos/o/r/commits/abc123" in paths and "repos/o/r/commits/def456" in paths, paths
    assert graph.nodes["release:v1"].ficha.fields["date"] == "2026-02-03"


@red("f4")
def test_inc9m_sec_f4_the_tag_sha_is_one_encoded_segment(monkeypatch):
    tags = [{"name": "v1", "commit": {"sha": "a/../b#c"}},
            {"name": "v2", "commit": {"sha": ".."}},
            {"name": "v3", "commit": {"url": "https://evil.example/x"}}]
    api = _stub_gh(monkeypatch, branches=[], tags=tags, sha="zzz")
    graph = GitHubConnector("o/r")._fetch_gh()
    paths = [a[1] for a in api if a[0] == "api"]
    assert "repos/o/r/commits/a%2F..%2Fb%23c" in paths, paths
    for argv in api:
        assert all(seg not in (".", "..") for seg in _segments(argv)), argv
        assert not any("evil.example" in p for p in argv), argv
    assert graph.nodes["release:v3"].ficha.fields["date"] == ""


@red("crf5")
def test_inc9m_cr_f5_the_encoded_default_branch_is_named_qdefault():
    tree = ast.parse((REPO_ROOT / "github.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_fetch_gh")
    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    assert "qdefault" in names and "default_branch" not in names, names


# ---------------------------------------------------------------------------
# INC9L-CR-F2 -- a one-segment `git@host:path` is accepted (T1 tells the user to type it)

@red("crf2")
@pytest.mark.parametrize("typed,name", [("git@h:r", "r"), ("git@h:project.git", "project"),
                                        ("git@myserver:project.git", "project")])
def test_inc9m_cr_f2_a_one_segment_scp_url_reaches_the_clone(typed, name, tmp_path, monkeypatch):
    run = _Run(returncode=128, stderr="fatal: Could not resolve host: x\n")
    monkeypatch.setattr("subprocess.run", run)
    assert github._repo_name_from_url(typed) == name
    assert github.painted_repo(typed) == typed
    with pytest.raises(GitHubError):
        GitHubConnector(typed, cache_dir=tmp_path / "cache").fetch()
    clones = [argv for argv, _ in run.calls if argv[:3] == ["git", "clone", "--mirror"]]
    assert len(clones) == 1 and clones[0][3:5] == ["--", typed], run.calls


def test_inc9m_cr_f2_pin_a_scp_url_with_a_bad_last_segment_is_still_refused():
    for typed in ("git@h:..", "git@h:...", "git@h:o/.git", "git@h:o/.."):
        with pytest.raises(GitHubError):
            github._repo_name_from_url(typed)


# ---------------------------------------------------------------------------
# INC9L-CR-F3 -- the source badge reads `_classify`

def _badge(text: str) -> str:
    return RepoScreen._source_kind(types.SimpleNamespace(repo=text))


@pytest.mark.parametrize("text", [
    pytest.param("git@h:o/r/x", marks=_red_mark("crf3")),
    pytest.param("git@h:grp/sub/r.git", marks=_red_mark("crf3")),
    pytest.param("git@h:r", marks=_red_mark("crf3")),
    "https://h:8443/a/b/c", "https://h/o/r", "o/r"])
def test_inc9m_cr_f3_the_badge_of_an_accepted_remote_matches_classify(text):
    assert github._classify(text) in ("url", "gh"), text
    assert _badge(text) == "github", (text, _badge(text))


def test_inc9m_cr_f3_pin_a_local_git_directory_is_local(tmp_path, monkeypatch):
    (tmp_path / "work" / ".git").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    for text in (str(tmp_path / "work"), "work"):
        assert github._classify(text) == "local" and _badge(text) == "local", text


@pytest.mark.parametrize("text", [pytest.param("https://u:tok@h/o/r", marks=_red_mark("crf3")), "plainword"])
def test_inc9m_cr_f3_a_refused_text_is_badged_local_not_as_a_remote(text):
    with pytest.raises(GitHubError):
        github._classify(text)
    assert _badge(text) == "local", text


@red("crf3")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("repo,badge", [("git@h:grp/sub/r.git", "github"), ("o/r", "github"), ("work", "local")])
async def test_inc9m_cr_f3_the_badge_is_painted_from_classify(tmp_path, monkeypatch, size, repo, badge):
    """`INC9M-CR-F3` (Inc-9n): the screen really connects through a stubbed `fetch` that returns a one-branch
    `Graph`, and the badge text is in the PAINTED frame; the method-level check stays as a second assertion."""
    _env(monkeypatch, tmp_path)
    (tmp_path / "work" / ".git").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    graph = Graph()
    graph.add_node(Node(id=repo, ficha=Ficha(title=repo, meta="repo")))
    graph.add_node(Node(id="main", ficha=Ficha(title="main", meta="+0/-0", state="ok",
                                               fields={"kind": "branch", "date": "2026-01-01"})))
    graph.add_edge(Edge(parent_id=repo, child_id="main"))
    monkeypatch.setattr(GitHubConnector, "fetch", lambda self, progress=None: graph)
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = RepoScreen(repo)
        app.push_screen(screen)
        for _ in range(10):
            await pilot.pause()
        frame = _flat(screen)
        assert screen.graph is graph and "main" in frame, frame
        other = "local" if badge == "github" else "github"
        assert f" {badge} " in frame and f" {other} " not in frame, frame
        assert screen._source_badge().plain.strip() == badge
