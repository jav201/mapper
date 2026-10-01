"""Inc-9k -- the closed allow-list for typed repo URLs.

Authority: `A-119` and the operator's Round 8, S1 (`VERDICT-inc9-2026-09-30.md`, "Lista cerrada").
Every arm the change closes was committed RED first as a STRICT xfail keyed by the step that closes it
(`OPEN_STEPS`); an arm that is not keyed is a pin (green on the base), killed by a mutant instead.

Nothing here reaches the network, the real cache or the real `gh`: every git or gh call is stubbed,
HOME and USERPROFILE point at `tmp_path`.  Control characters and non-ASCII are `\\u`/`\\t` escapes
(this file is ASCII); no user-profile path is typed.
"""
from __future__ import annotations

import pytest
from textual.widgets import Input, Static

from mapper import github
from mapper.app import MapperApp, PlugRepoScreen
from mapper.github import GitHubConnector, GitHubError, _ensure_cloned
from tests.test_inc9f import NARROW, SIZE, _Run, hermetic  # noqa: F401
from tests.test_inc9j import _Boom, _type_and_connect
from tests.test_repair_layout import _frame_rows, _rows_in

OPEN_STEPS: set[str] = set()


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9k: committed RED; closed by the '{step}' step")
    return lambda fn: fn


SENTENCE = ("refusing the repository: use https://host/path, git@host:path, owner/name or a"
            " local folder")
UNRECOGNISED = "(unrecognised URL)"
# Kept: they name a rule, echo nothing, and the Inc-9f..9j arms for dash and `ext::` stand on them.
FINER = {"refusing the repository: it may not start with '-'",
         "refusing the repository: transport helpers are not accepted"}

# The operator's list (S1), then the forms of the Inc-9j arms (`BYPASSES`, `REDACTED`), then the
# shapes the grammar cuts by construction.  Each is refused before any process starts.
CREDENTIAL_FORMS = [
    "https://u:tok@h/o/r",
    "https:///u:tok@h/o/r",
    "https:/u:tok@h/r",
    "http:u:tok@h/r",
    "https:\\\\u:tok@h/r",
    "ssh://u:tok@h/o/r",
    "git://u:tok@h/o/r",
    "git@https://u:tok@h/r",
    "https://u:t/ok@h/o/r",
    "https://tok?@h/o/r",
    "https://h/r?access_token=x",
    "https://h/r#x",
    "https://[::1]/r",
    "https://h/%2e%2e/r",
    "https://h//r",
    "https://-h/r",
    "https://h/-r",
    "HTTPS://h/o/r",
    "https://h/o\tr",
    "https://h/o/r\r",
    "https://h/o/r\n",
    "https://h/\no/r",
    "https://h\u00e9.example/o/r",
    "http://h/o/r",
    # the Inc-9j forms
    "https:///tok@h/o/r",
    "http:///u:tok@h/o/r",
    "https:////u:p@h/o/r",
    "https:///\\u:p@h/o/r",
    "https:///h/o/r",
    "HTTPS:///u:tok@h/o/r",
    "https://user:tok@example.invalid/o/r.git",
    "https://tok@h/o/r",
    "http://u:@h/o/r",
    "HTTP://u:p@h/o/r",
    "https://a@b@h/o/r",
    "https://u:p@h/o/r@v2",
    "https://u:p@h:8443/o/r?x=1#f",
    "user:tok@example.invalid/o/r",
]
GRAMMAR_CUTS = [
    "https://h/o/r@v2",
    "https://h",
    "https://h/",
    "https://h:/o/r",
    "https://h:80:90/o/r",
    "https://h:\u0663/o/r",
    "https://h/o/./r",
    "https://h/o/../r",
    "https://h/o/r%20",
    "https://h/o r",
    "https://h/o/r ",
    "https://h/\u00e9/r",
    "https://h/o/r\\x",
    "https://.h/o/r",
    "https://u@h/r",
    "file:///etc/passwd",
    "ssh://git@h/o/r",
    "git@h:/o/r",
    "git@h:-r",
    "git@-h:o/r",
    "git@:o/r",
    "git@h:",
    "git@h:o//r",
    "git@h:o/r?x",
    "git@h:o/r#x",
    "git@h:o/r@v2",
    "git@u:tok@h:o/r",
    "git@h:o/../r",
    "git@h:8443:o/r",
    "o//r",
    "a/b/c",
    "bad owner/x",
    "o/r?x",
    "./relative",
]
REFUSED = CREDENTIAL_FORMS + GRAMMAR_CUTS

ACCEPTED = [
    "https://h/o/r",
    "https://h/o/r.git",
    "https://h/o/r/",
    "https://h:8443/o/r.git",
    "https://github.example.invalid/o/r",
    "git@h:o/r.git",
    "git@h:o/r/",
    "https://1.2.3.4/o/r",
    "https://h/o/some-name_v2~x.git",
]


# ---------------------------------------------------------------------------
# S1 -- the refusal: before any process, one fixed sentence that echoes nothing

@red("allow")
@pytest.mark.parametrize("url", REFUSED)
def test_inc9k_s1_a_form_outside_the_allow_list_is_refused_before_any_process(url, tmp_path, monkeypatch):
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector(url, cache_dir=tmp_path / "cache").fetch()
    assert run.calls == [], run.calls
    assert str(caught.value) == SENTENCE, str(caught.value)
    assert not (tmp_path / "cache").exists(), "no directory was made for a refused URL"


@red("allow")
@pytest.mark.parametrize("url", [
    "https://u:tok@h/o/r", "https:///u:tok@h/o/r", "https://h/o/r?access_token=x", "git@h:o/r@v2",
    "https://h/o/r\n", "HTTPS://h/o/r"])
def test_inc9k_s1_ensure_cloned_refuses_the_same_forms_by_itself(url, tmp_path, monkeypatch):
    """Defence in depth (INC9J-SEC-F2): the connector is not the only gate."""
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        _ensure_cloned(url, tmp_path / "cache")
    assert run.calls == [] and str(caught.value) == SENTENCE, (run.calls, str(caught.value))
    assert not (tmp_path / "cache").exists()


@pytest.mark.parametrize("url", ACCEPTED)
def test_inc9k_s1_an_allowed_url_reaches_the_clone_as_typed(url, tmp_path, monkeypatch):
    run = _Run(returncode=0)
    monkeypatch.setattr("subprocess.run", run)
    try:
        GitHubConnector(url, cache_dir=tmp_path / "cache").fetch()
    except GitHubError as exc:
        assert "refusing" not in str(exc), (url, str(exc))
    clones = [argv for argv, _ in run.calls if argv[:3] == ["git", "clone", "--mirror"]]
    assert len(clones) == 1 and clones[0][3] == "--" and clones[0][4] == url, (url, run.calls)


@pytest.mark.parametrize("url", ACCEPTED)
def test_inc9k_s1_the_allow_list_predicate_accepts_what_the_grammar_lists(url):
    assert github._is_url(url) is True


# The base's `_is_url` already says no to a text that does not start with `http(s)://` or `git@`.
URL_SHAPED = [u for u in REFUSED if u.startswith(("http://", "https://", "git@"))]
NOT_URL_SHAPED = [u for u in REFUSED if u not in URL_SHAPED]


@red("allow")
@pytest.mark.parametrize("url", URL_SHAPED)
def test_inc9k_s1_the_allow_list_predicate_refuses_a_url_shaped_text_outside_the_grammar(url):
    assert github._is_url(url) is False


@pytest.mark.parametrize("url", NOT_URL_SHAPED)
def test_inc9k_s1_the_allow_list_predicate_still_refuses_what_is_not_url_shaped(url):
    assert github._is_url(url) is False


@pytest.mark.parametrize("spec", ["-x", "--upload-pack=x", "ext::sh -c x", "fd::1"])
def test_inc9k_s1_the_dash_and_transport_helper_refusals_stand(spec, tmp_path, monkeypatch):
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector(spec, cache_dir=tmp_path / "cache").fetch()
    assert run.calls == [] and str(caught.value) in FINER, str(caught.value)


# ---------------------------------------------------------------------------
# S1, unchanged paths: owner/name through gh, a local directory

def test_inc9k_s1_owner_name_still_goes_through_gh(tmp_path, monkeypatch):
    run = _Run(returncode=1, stderr="gh: Could not resolve to a Repository (HTTP 404)\n")
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError):
        GitHubConnector("owner/name", cache_dir=tmp_path / "cache").fetch()
    assert run.calls and run.calls[0][0][:3] == ["gh", "repo", "view"], run.calls
    assert not any(argv[:2] == ["git", "clone"] for argv, _ in run.calls)


def test_inc9k_s1_a_local_git_directory_still_connects_without_a_clone(tmp_path, monkeypatch):
    repo = tmp_path / "work"
    (repo / ".git").mkdir(parents=True)
    run = _Run(returncode=0)
    monkeypatch.setattr("subprocess.run", run)
    GitHubConnector(str(repo), cache_dir=tmp_path / "cache").fetch()
    assert run.calls and all(argv[:2] == ["git", "-C"] for argv, _ in run.calls), run.calls
    assert not any("clone" in argv for argv, _ in run.calls)


@red("allow")
@pytest.mark.parametrize("spec", ["a/b/c", "bad owner/x", "o/r?x", "./relative", "plainword"])
def test_inc9k_s1_a_malformed_owner_name_gets_the_one_sentence(spec, tmp_path, monkeypatch):
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector(spec, cache_dir=tmp_path / "cache").fetch()
    assert run.calls == [] and str(caught.value) == SENTENCE, str(caught.value)


# ---------------------------------------------------------------------------
# S1 display (R1 + S1) -- the helper every painted surface reads

@red("allow")
@pytest.mark.parametrize("url", REFUSED)
def test_inc9k_s1_display_a_refused_text_is_never_painted(url):
    assert github.painted_repo(url) == UNRECOGNISED


@red("allow")
@pytest.mark.parametrize("typed", ACCEPTED + ["o/r", "owner/some.name-1"])
def test_inc9k_s1_display_an_accepted_text_is_painted_as_typed(typed):
    assert github.painted_repo(typed) == typed


@red("allow")
def test_inc9k_s1_display_a_local_directory_is_painted_as_typed(tmp_path):
    repo = tmp_path / "work"
    (repo / ".git").mkdir(parents=True)
    assert github.painted_repo(str(repo)) == str(repo)


@red("allow")
@pytest.mark.parametrize("gone", ["redact_userinfo", "_refuse_userinfo", "_http_parts"])
def test_inc9k_s1_the_deny_list_pieces_are_gone(gone):
    assert not hasattr(github, gone), gone


# ---------------------------------------------------------------------------
# S1 display, in the painted frame (Pilot, real keys, 118 and 87)

REFUSED_TYPED = [
    "https://user:tok@example.invalid/o/r.git",
    "https:///user:tok@example.invalid/o/r.git",
    "ssh://user:tok@example.invalid/o/r",
    "user:tok@example.invalid/o/r",
]


@red("allow")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("typed", REFUSED_TYPED)
async def test_inc9k_s1_a_refused_credential_is_painted_nowhere_but_in_the_field(
        tmp_path, monkeypatch, typed, size):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr("subprocess.run", _Boom())
    app = MapperApp(tmp_path)
    toasts: list[str] = []
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        app.notify = lambda msg, **kw: toasts.append(str(msg))
        await _type_and_connect(app, pilot, typed)
        screen = app.screen
        flat = " ".join("\n".join(_frame_rows(screen)).split())
        assert "tok" not in flat and "user:" not in flat and "***" not in flat, flat
        assert UNRECOGNISED.replace(" ", "") in flat.replace(" ", ""), flat
        name = screen.query_one("#repo-name", Static)
        shown = "".join("\n".join(_rows_in(screen, name.region)).split())
        assert shown == UNRECOGNISED.replace(" ", ""), shown
        assert screen.repo == typed, "the connector still gets the text as typed"
        assert [t for t in toasts if "tok" in t or "user:" in t] == [], toasts
        assert "refusing the repository" in flat, flat
        await pilot.press("q")
        for _ in range(4):
            await pilot.pause()
        assert isinstance(app.screen, PlugRepoScreen), app.screen
        field = app.screen.query_one("#repo-input", Input)
        assert field.value == typed, "the field keeps the operator's own text for correction"


@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9k_s1_an_allowed_url_is_painted_as_typed(tmp_path, monkeypatch, size):
    typed = "https://example.invalid/o/r.git"
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setattr("subprocess.run", _Run(returncode=128, stderr="Could not resolve host\n"))
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await _type_and_connect(app, pilot, typed)
        screen = app.screen
        name = screen.query_one("#repo-name", Static)
        shown = "".join("\n".join(_rows_in(screen, name.region)).split())
        assert shown == typed, shown
        assert UNRECOGNISED.replace(" ", "") not in "".join("\n".join(_frame_rows(screen)).split())
