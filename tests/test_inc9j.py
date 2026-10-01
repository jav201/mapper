"""Inc-9j -- fixes for the defects the Inc-9i reviews found.

Authority: `A-118` (`INC9I-SEC-F1`, `INC9I-UX-F1` = the operator's Round 7 R1,
`VERDICT-inc9-2026-09-30.md`, `INC9I-CR-F1` .. `F3`).  Every arm that a fix closes was committed RED
first as a STRICT xfail keyed by the step that closes it (`OPEN_STEPS`); an arm that is not keyed
is a pin, killed by a mutant instead (record section 4).

Nothing here reaches the network, the real cache or the real `gh`: every git or gh call is
stubbed, HOME and USERPROFILE point at `tmp_path`.  No user-profile path is typed literally;
control and bidi characters are `\\u` escapes (`test_fold`).
"""
from __future__ import annotations

import ast
import pathlib

import pytest
from textual.widgets import Input, Static

from mapper import github
from mapper.app import MapperApp, PlugRepoScreen, RepoScreen
from mapper.github import GitHubConnector, GitHubError
from tests.test_inc9f import NARROW, SIZE, _Run, hermetic  # noqa: F401
from tests.test_repair_layout import _frame_rows, _rows_in

OPEN_STEPS: set[str] = set()


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9j: committed RED; closed by the '{step}' step")
    return lambda fn: fn


class _Boom:
    """A `subprocess.run` that fails the test on ANY call: a refused URL starts no process."""

    def __init__(self):
        self.calls: list = []

    def __call__(self, argv, *a, **kw):
        self.calls.append(list(argv))
        raise AssertionError(f"a process was started for a refused URL: {argv}")


# ---------------------------------------------------------------------------
# INC9I-SEC-F1 -- the credential refusal reads the authority the way curl does

BYPASSES = [
    "https:///tok@h/o/r",
    "http:///u:tok@h/o/r",
    "https:////u:p@h/o/r",
    "https:///\\u:p@h/o/r",
]


@red("creds")
@pytest.mark.parametrize("url", BYPASSES)
def test_inc9j_sec_f1_extra_slashes_do_not_hide_userinfo_from_the_refusal(url, tmp_path, monkeypatch):
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector(url, cache_dir=tmp_path / "cache").fetch()
    message = str(caught.value)
    assert run.calls == [], run.calls
    # `S1` rework: the one fixed sentence of the allow-list replaces the credential sentence.
    assert message == (
        "refusing the repository: use https://host/path, git@host:path, owner/name or a"
        " local folder"), message
    assert not (tmp_path / "cache").exists(), "no directory was made for a refused URL"


def test_inc9j_sec_f1_an_upper_case_scheme_is_not_a_url_here_and_starts_no_process(tmp_path, monkeypatch):
    """`_is_url` is case-sensitive, so `HTTPS://...` goes to the `gh` path, which refuses a
    spec that is not owner/name with its own fixed sentence (it echoes nothing).  A pin."""
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector("HTTPS:///u:tok@h/o/r", cache_dir=tmp_path / "cache").fetch()
    assert "tok" not in str(caught.value) and run.calls == [], (str(caught.value), run.calls)


@red("creds")
def test_inc9j_sec_f1_a_url_with_no_host_at_all_is_refused_before_any_process(tmp_path, monkeypatch):
    """The second clause: an empty `netloc` is never a URL git can clone from."""
    run = _Boom()
    monkeypatch.setattr("subprocess.run", run)
    with pytest.raises(GitHubError) as caught:
        GitHubConnector("https:///h/o/r", cache_dir=tmp_path / "cache").fetch()
    assert str(caught.value) == (
        "refusing the repository: use https://host/path, git@host:path, owner/name or a"
        " local folder") and run.calls == []


@pytest.mark.parametrize("url", [
    "git@example.invalid:o/r.git", "https://example.invalid/o/r.git",
    "https://example.invalid/o/r/",
    # `S1` rework: `.../r@v2` and `https://tok?@h/o/r` hold `@` outside the allow-list; both are
    # refused now (`test_inc9k`), so they no longer belong to this no-false-refusal list.
])
def test_inc9j_sec_f1_no_false_refusal(url, tmp_path, monkeypatch):
    run = _Run(returncode=0)
    monkeypatch.setattr("subprocess.run", run)
    try:
        GitHubConnector(url, cache_dir=tmp_path / "cache").fetch()
    except GitHubError as exc:
        assert "credential" not in str(exc), (url, str(exc))
    assert any(argv[:3] == ["git", "clone", "--mirror"] for argv, _ in run.calls), (url, run.calls)


# ---------------------------------------------------------------------------
# INC9I-UX-F1 (operator R1) -- every surface that paints a typed URL redacts userinfo

# `S1` (Inc-9k): the redaction helper is gone; the display rule is `github.painted_repo`
# (`tests/test_inc9k.py`).  The arms of the helper were deleted with it.

TYPED = "https://user:tok@example.invalid/o/r.git"
THREE_SLASH = "https:///user:tok@example.invalid/o/r.git"


async def _type_and_connect(app, pilot, text: str) -> None:
    app.push_screen(PlugRepoScreen())
    await pilot.pause()
    app.screen.query_one("#repo-input", Input).focus()
    await pilot.pause()
    await pilot.press(*text)
    await pilot.press("enter")
    for _ in range(30):
        await pilot.pause()
        if isinstance(app.screen, RepoScreen) and not app.screen.loading:
            break
    assert isinstance(app.screen, RepoScreen) and not app.screen.loading, app.screen
    for _ in range(3):
        await pilot.pause()


@red("redact")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("typed", [TYPED, THREE_SLASH])
async def test_inc9j_ux_f1_a_typed_credential_is_painted_nowhere_but_in_the_field(
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
        # `S1` rework: a credential form is not painted at all; the text is `(unrecognised URL)`.
        assert "tok" not in flat and "user:" not in flat and "***" not in flat, flat
        name = screen.query_one("#repo-name", Static)
        shown = " ".join("\n".join(_rows_in(screen, name.region)).split())
        assert shown == "(unrecognised URL)", shown
        assert screen.repo == typed, "the connector still gets the URL as typed"
        assert [t for t in toasts if "tok" in t or "user:" in t] == [], toasts
        await pilot.press("q")
        for _ in range(4):
            await pilot.pause()
        assert isinstance(app.screen, PlugRepoScreen), app.screen
        field = app.screen.query_one("#repo-input", Input)
        assert field.value == typed, "the field keeps the operator's own text for correction"
        assert "tok" in " ".join("\n".join(_frame_rows(app.screen)).split()), "the field paints it"


# ---------------------------------------------------------------------------
# INC9I-CR-F3 -- `_ensure_cloned` is reached from production code only through the connector

def _references_to_ensure_cloned() -> list[tuple[str, str]]:
    root = pathlib.Path(github.__file__).parent
    found: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        parents: dict[ast.AST, ast.AST] = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_ensure_cloned":
                found.append((path.name, "<definition>"))
                continue
            hit = (
                (isinstance(node, ast.Name) and node.id == "_ensure_cloned")
                or (isinstance(node, ast.Attribute) and node.attr == "_ensure_cloned")
                or (isinstance(node, ast.alias) and node.name == "_ensure_cloned")
            )
            if not hit:
                continue
            owner = "<module>"
            up = parents.get(node)
            while up is not None:
                if isinstance(up, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    owner = up.name
                    cls = parents.get(up)
                    if isinstance(cls, ast.ClassDef):
                        owner = f"{cls.name}.{up.name}"
                    break
                up = parents.get(up)
            found.append((path.name, owner))
    return found


def test_inc9j_cr_f3_ensure_cloned_is_referenced_in_production_only_from_the_connector_fetch():
    """`fetch` is the one production entry point for a typed URL; `_ensure_cloned` also refuses a
    text outside the allow-list by itself (A-119 st. 5), so a direct call is no weaker."""
    found = _references_to_ensure_cloned()
    assert ("github.py", "<definition>") in found, found
    others = [f for f in found if f != ("github.py", "<definition>")]
    assert others == [("github.py", "GitHubConnector.fetch")], others
