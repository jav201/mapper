"""Inc-9n -- fixes for the Inc-9m reviews: the factory sidecar (SEC-F1), DOS device names (F2/CR-F1),
the refusal sentence (U1), the attachment-add check (U2), and the `_fetch_gh` fixes (F3, CR-F5, CR-F8).

Authority: `A-122` and `VERDICT-inc9-2026-09-30.md` Round 10 (U1, U2).  Every arm a fix closes was
committed RED first as a STRICT xfail keyed by the step that closes it (`OPEN_STEPS`); an arm that is
not keyed is a pin (green on the base), killed by a mutant instead.

Nothing here reaches the network, a real console or COM device, a real UNC or NT-namespace path: a spy
refuses (and records) any filesystem call whose path is a hostile form BEFORE the real call is made, and
`preview_csv` is replaced by a stub that fails, so a device name never reaches an `open`.  Control and
non-ASCII characters are `\\u` escapes (this file is ASCII); no user-profile path is typed.
"""
from __future__ import annotations

import ast
import builtins
import io
import os
import pathlib
import zipfile

import pytest

from mapper import github, osopen
from mapper.app import MapperApp
from mapper.github import GitHubConnector, GitHubError
from mapper.model import Attachment, Document, Ficha, Graph, Node
from mapper.screens.factory import FactoryScreen
from mapper.store import MapStore
from mapper.widgets.inspector import FichaInspector
from tests.test_attachments import RecordingLauncher, _open, _seed
from tests.test_inc9f import NARROW, SIZE, _Run  # noqa: F401
from tests.test_inc9m import _env, _flat, _no_fs, _norm, _open_prompt, _stub_gh

# Inc-9q (X2): the hostile-document arms whose sentence changed from "not found" to U1 were committed RED first.
OPEN_STEPS: set[str] = set()

REPO_ROOT = pathlib.Path(github.__file__).parent


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9n: committed RED; closed by the '{step}' step")
    return lambda fn: fn


def _red_mark(step: str):
    return ([pytest.mark.xfail(strict=True, reason=f"Inc-9n: committed RED; closed by the '{step}' step")]
            if step in OPEN_STEPS else [])


# `U1`, with a real ellipsis (U+2026) written as an escape.
U1 = "path not supported: use C:\\\u2026 or a relative path"
# Inc-9o (`A-123`): `V1` and `V2` (Round 11) replace what these arms said for a path that is only outside.
V1 = "attachment must be inside the workspace: use a relative path"
V2 = "template outside the workspace: import it with i"

DEVICES = [
    "con", "nul", "conin$", "conout$", "com1", "aux", "lpt1", "prn", "COM\u00b9",
    "sub\\con", "con.csv", "CON.", "Com1 ", "con\\x", "C:\\con", "C:\\a\\NUL.txt", "CONOUT$ ", "x/AUX.txt/y",
    "CON  .", "lpt9.log",
]
NOT_DEVICES = ["console.csv", "icon\\x", "C:\\work\\a.csv", "nulls", "com0", "comm1", "lpt", "docs/auxiliary.txt"]


class _Devices:
    """Refuses (and records) a filesystem or `open` call for a hostile form or a DOS device name, BEFORE the
    real call is made, so the real console or SMB lookup never happens."""

    def __init__(self, monkeypatch, forms=()):
        self.hits: list[str] = []
        self.forms = [_norm(f) for f in forms]
        for name in ("is_dir", "exists", "stat", "lstat", "is_file", "resolve", "samefile",
                     "read_text", "read_bytes", "open", "iterdir"):
            monkeypatch.setattr(pathlib.Path, name, self._wrap("Path." + name, getattr(pathlib.Path, name)))
        for name in ("stat", "lstat", "scandir", "listdir"):
            monkeypatch.setattr(os, name, self._wrap("os." + name, getattr(os, name)))
        for name in ("isdir", "exists", "isfile", "realpath", "getsize", "islink", "lexists"):
            monkeypatch.setattr(os.path, name, self._wrap("os.path." + name, getattr(os.path, name)))
        monkeypatch.setattr(builtins, "open", self._wrap("open", builtins.open))
        monkeypatch.setattr(io, "open", self._wrap("io.open", io.open))
        nt = __import__("sys").modules.get("nt")
        if nt is not None and hasattr(nt, "_getfinalpathname"):
            monkeypatch.setattr(nt, "_getfinalpathname",
                                self._wrap("nt._getfinalpathname", nt._getfinalpathname))

    def _bad(self, value) -> bool:
        if not isinstance(value, (str, os.PathLike)):
            return False
        text = _norm(os.fspath(value)) if not isinstance(value, bytes) else ""
        if any(f in text for f in self.forms):
            return True
        parts = pathlib.PureWindowsPath(text).parts
        return any(pathlib.PureWindowsPath(p).is_reserved() for p in parts)

    def _wrap(self, name, real):
        def probe(first, *a, **kw):
            if self._bad(first):
                self.hits.append(f"{name}({first})")
                raise OSError("blocked: a filesystem call for a hostile text")
            return real(first, *a, **kw)
        return probe


def _doc_graph(path: str) -> Graph:
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="proceso")))
    g.documents["plantilla"] = Document(name="plantilla", path=path, kind="docx", template=True)
    return g


def _make_docx(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:document>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Types/>")
        zf.writestr("word/document.xml", xml)


# ---------------------------------------------------------------------------
# INC9M-SEC-F1 -- a sidecar document path is not typed text: the factory screen stats nothing hostile

HOSTILE_DOCS = ["\\\\h\\s\\a.docx", "//h/s/a.docx", "\\??\\UNC\\h\\s\\a.docx", "C:\\outside\\a.docx", "con"]


def _toasts(app):
    toasts: list[str] = []
    real = app.notify

    def notify(message, **kw):
        toasts.append(str(message))
        return real(message, **kw)

    app.notify = notify
    return toasts


_HOSTILE_FRAMES = [pytest.param(d, marks=_red_mark("f1") + (_red_mark("v2") if d == "C:\\outside\\a.docx" else _red_mark("x2")))
                   for d in HOSTILE_DOCS]


@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("doc_path", _HOSTILE_FRAMES)
async def test_inc9n_f1_a_hostile_sidecar_document_is_never_stat_ed_and_the_screen_survives(
        doc_path, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    spy = _Devices(monkeypatch, ["\\\\h\\s\\a.docx", "\\??\\UNC\\h\\s\\a.docx", "C:\\outside\\a.docx"])
    app = MapperApp(tmp_path)
    toasts = _toasts(app)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph(doc_path), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert app.is_running and app.screen is screen
        # Inc-9o (`V2`): a path outside the workspace says so.  Inc-9q (X2, operator-ruled): every other
        # hostile text is refused by the path rule and says U1, not 'not found'.
        expected = V2 if doc_path == "C:\\outside\\a.docx" else U1
        assert expected in _flat(screen), _flat(screen)
        assert screen._office_path(screen.graph.documents["plantilla"]) is None
        screen.action_generate_office()
        await pilot.pause()
        assert expected in toasts, toasts
        assert app.is_running
    assert spy.hits == [], spy.hits


@red("f1")
@pytest.mark.parametrize("doc_path", HOSTILE_DOCS)
def test_inc9n_f1_office_path_is_none_for_a_hostile_text_without_a_filesystem_call(doc_path, tmp_path, monkeypatch):
    class _App:
        store = MapStore(tmp_path)

    screen = FactoryScreen.__new__(FactoryScreen)
    monkeypatch.setattr(FactoryScreen, "app", property(lambda self: _App()))
    doc = Document(name="plantilla", path=doc_path, kind="docx", template=True)
    with _no_fs(monkeypatch) as hits:
        assert screen._office_path(doc) is None
    assert hits == []


@red("w2")
async def test_inc9n_f1_a_junction_inside_the_workspace_that_leads_outside_is_refused(tmp_path, monkeypatch):
    """`resolve()` follows a directory junction (no privilege needed): lexically inside, really outside."""
    import subprocess

    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    _make_docx(tmp_path / "outside" / "a.docx", "outside")
    made = subprocess.run(["cmd", "/c", "mklink", "/J", str(ws / "link"), str(tmp_path / "outside")],
                          capture_output=True, text=True)
    if made.returncode != 0:
        pytest.skip("a directory junction could not be created here")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("link/a.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert screen._office_path(screen.graph.documents["plantilla"]) is None
        # Inc-9p (`W2`): a link has its own sentence now.
        assert "path goes through a link: use a real folder inside the workspace" in _flat(screen), _flat(screen)


async def test_inc9n_f1_pin_a_workspace_relative_document_still_previews(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    _make_docx(tmp_path / "docs" / "a.docx", "hola {{nombre}}")
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("docs/a.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        frame = _flat(screen)
        assert "hola" in frame and "template file not found" not in frame, frame
        got = screen._office_path(screen.graph.documents["plantilla"])
        assert got is not None and got.is_file()


async def test_inc9n_f1_pin_a_drive_absolute_document_inside_the_workspace_still_previews(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    _make_docx(tmp_path / "docs" / "a.docx", "hola {{nombre}}")
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph(str(tmp_path / "docs" / "a.docx")), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert "hola" in _flat(screen), _flat(screen)


@red("v2")
async def test_inc9n_f1_a_dotdot_document_that_leaves_the_workspace_is_refused(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(tmp_path / "secret.docx", "outside")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("..\\secret.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert screen._office_path(screen.graph.documents["plantilla"]) is None
        assert V2 in _flat(screen), _flat(screen)


# ---------------------------------------------------------------------------
# INC9M-SEC-F2 / CR-F1 -- DOS device names are refused by the helper, in every component

@red("f2")
@pytest.mark.parametrize("text", DEVICES)
def test_inc9n_f2_a_dos_device_name_is_refused_by_the_helper_before_any_filesystem_call(text, monkeypatch):
    with _no_fs(monkeypatch) as hits:
        assert osopen.safe_local_path(text) is None, text
    assert hits == []


@pytest.mark.parametrize("text", NOT_DEVICES)
def test_inc9n_f2_pin_a_name_that_only_looks_like_a_device_is_accepted(text):
    assert osopen.safe_local_path(text) is not None, text


@red("f2")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("typed", ["CON", "conin$", "COM1", "sub\\con.csv"])
async def test_inc9n_f2_the_csv_prompt_with_a_device_name_returns_at_once_and_opens_nothing(
        typed, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    spy = _Devices(monkeypatch)
    calls: list = []

    def never(path):
        calls.append(path)
        raise AssertionError("preview_csv was called for a device name")

    monkeypatch.setattr("mapper.screens.home.preview_csv", never)
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", typed)
        assert app.is_running
        assert toasts == [U1], toasts
    assert calls == [] and spy.hits == [], (calls, spy.hits)


@red("f2")
async def test_inc9n_f2_the_csv_prompt_requires_a_file_not_a_directory(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    (tmp_path / "d.csv").mkdir()
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", str(tmp_path / "d.csv"))
        assert toasts == ["file not found: d.csv"], toasts


@red("f2")
async def test_inc9n_f2_the_office_prompt_requires_a_file_not_a_directory(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    (tmp_path / "t.docx").mkdir()
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.push_screen(FactoryScreen(_doc_graph("x.docx"), process_name="demo"))
        await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", str(tmp_path / "t.docx"))
        assert toasts == ["file not found: t.docx"], toasts


@red("f2")
@pytest.mark.parametrize("typed", ["CON", "nul", "sub\\COM1.docx"])
async def test_inc9n_f2_the_office_prompt_with_a_device_name_touches_nothing(typed, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    spy = _Devices(monkeypatch)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        app.push_screen(FactoryScreen(_doc_graph("x.docx"), process_name="demo"))
        await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", typed)
        assert app.is_running and toasts == [U1], toasts
    assert spy.hits == [], spy.hits


@red("f2")
def test_inc9n_f2_open_external_launches_a_regular_file_only(tmp_path, monkeypatch):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.pdf").write_bytes(b"x")
    launcher = RecordingLauncher()
    monkeypatch.setattr(pathlib.Path, "is_file", lambda self: False)
    status = osopen.open_external("file", "docs/a.pdf", workspace=tmp_path, launcher=launcher)
    assert status == osopen.REFUSED_ERROR and launcher.calls == [], (status, launcher.calls)


def test_inc9n_f2_pin_open_external_still_launches_a_regular_file(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.pdf").write_bytes(b"x")
    launcher = RecordingLauncher()
    assert osopen.open_external("file", "docs/a.pdf", workspace=tmp_path, launcher=launcher) == osopen.OK
    assert len(launcher.calls) == 1


@red("f2")
@pytest.mark.parametrize("target", ["con", "docs\\NUL.txt", "COM1"])
def test_inc9n_f2_open_external_refuses_a_device_name_before_any_filesystem_call(target, tmp_path):
    launcher = RecordingLauncher()
    status = osopen.open_external("file", target, workspace=tmp_path, launcher=launcher)
    assert status == osopen.REFUSED_TYPE and launcher.calls == [], (status, launcher.calls)


# ---------------------------------------------------------------------------
# U1 -- a refused text toasts one name-free English sentence; a missing accepted path keeps its name

@red("u1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("surface,typed", [
    ("csv", "\\\\h\\s\\x.csv"), ("csv", "/x.csv"), ("csv", "~nosuchuser/secret-token.csv"),
    ("office", "\\\\h\\s\\x.docx"), ("office", "/x.docx"), ("office", "~nosuchuser/secret-token.docx")])
async def test_inc9n_u1_a_refused_text_toasts_the_sentence_and_names_nothing(
        surface, typed, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        if surface == "office":
            app.push_screen(FactoryScreen(_doc_graph("x.docx"), process_name="demo"))
            await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", typed)
        assert app.is_running
        assert toasts == [U1], toasts
        frame = _flat(app.screen)
        assert "secret-token" not in frame and "nosuchuser" not in frame, frame


@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("surface", ["csv", "office"])
async def test_inc9n_u1_pin_a_missing_accepted_path_keeps_naming_its_file(surface, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ext = "csv" if surface == "csv" else "docx"
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        if surface == "office":
            app.push_screen(FactoryScreen(_doc_graph("x.docx"), process_name="demo"))
            await pilot.pause()
        toasts = await _open_prompt(app, pilot, "i", str(tmp_path / f"missing.{ext}"))
        # the csv prompt is `app.py`'s own sentence (EN-5); the office prompt is the factory's (EN-1)
        word = "file not found"
        assert toasts == [f"{word}: missing.{ext}"], toasts


@red("u1")
def test_inc9n_u1_the_sentence_is_written_with_a_real_ellipsis_in_one_place():
    # `2026-10-09-modular-batch` A4: the CSV door moved with `HomeScreen` to
    # `screens/home.py`, which now binds the sentence it reads — checked there,
    # not through the `mapper.app` re-export.
    from mapper.screens import home as home_mod

    assert home_mod.PATH_NOT_SUPPORTED == U1
    assert "\u2026" in U1 and "..." not in U1


@red("u1")
@pytest.mark.parametrize("surface,expected", [("csv", "C:\\path\\to\\nodes.csv"),
                                              ("office", "C:\\path\\to\\template.docx")])
async def test_inc9n_u1_the_prompt_placeholder_is_a_form_the_grammar_accepts(surface, expected, tmp_path, monkeypatch):
    from textual.widgets import Input

    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        if surface == "office":
            app.push_screen(FactoryScreen(_doc_graph("x.docx"), process_name="demo"))
            await pilot.pause()
        await pilot.press("i")
        await pilot.pause()
        placeholder = app.screen.query_one("#prompt-input", Input).placeholder
        assert placeholder == expected, placeholder
        assert osopen.safe_local_path(placeholder) is not None


async def test_inc9n_u1_pin_the_attachment_prompt_placeholder_is_accepted(tmp_path, monkeypatch):
    from textual.widgets import Input

    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        screen.query_one("#map-inspector", FichaInspector).request_add_attachment()
        await pilot.pause()
        placeholder = app.screen.query_one("#prompt-input", Input).placeholder
        assert osopen.safe_local_path(placeholder) is not None, placeholder


@red("u1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("target", ["\\\\h\\s\\x.pdf", "/x.pdf", "con", "docs\\NUL.pdf"])
async def test_inc9n_u1_opening_a_refused_file_attachment_toasts_the_sentence(target, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    spy = _Devices(monkeypatch, ["\\\\h\\s\\x.pdf"])
    app = MapperApp(tmp_path)
    launcher = RecordingLauncher()
    app.attachment_launcher = launcher
    notes: list[str] = []
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app, [Attachment(kind="file", path=target, caption="c")]))
        screen.notify = lambda msg, **kw: notes.append(str(msg))
        screen.query_one("#map-inspector", FichaInspector).post_message(FichaInspector.AttachmentActivated("nom", 0))
        await pilot.pause()
        assert notes == [U1], notes
        assert launcher.calls == []
    assert spy.hits == [], spy.hits


@red("v1")
async def test_inc9n_u1_pin_a_file_attachment_outside_the_workspace_keeps_its_own_refusal(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    app.attachment_launcher = RecordingLauncher()
    notes: list[str] = []
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app, [Attachment(kind="file", path="..\\..\\etc\\x", caption="c")]))
        screen.notify = lambda msg, **kw: notes.append(str(msg))
        screen.query_one("#map-inspector", FichaInspector).post_message(FichaInspector.AttachmentActivated("nom", 0))
        await pilot.pause()
        assert notes == [V1], notes


# ---------------------------------------------------------------------------
# U2 -- the attachment-add prompt refuses a non-local `file` target at ADD time

async def _add_attachment(app, pilot, typed):
    screen = await _open(app, pilot, _seed(app))
    toasts = _toasts(app)
    await pilot.press("A")
    await pilot.pause()
    assert app.screen.__class__.__name__ == "_PromptScreen", app.screen
    await pilot.press(*typed)
    await pilot.press("enter")
    for _ in range(6):
        await pilot.pause()
    return screen, toasts


@red("u2")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("typed", [
    "\\\\h\\s\\x.pdf", "/x.pdf", "con",
    pytest.param("C:\\outside-ws\\x.pdf", marks=_red_mark("v1")), pytest.param("..\\x.pdf", marks=_red_mark("v1"))])
async def test_inc9n_u2_adding_a_non_local_file_stores_nothing_and_toasts_the_sentence(
        typed, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, typed)
        assert app.is_running
        # Inc-9o (`V1`): a path the allow-list accepts but the workspace does not contain has its own sentence.
        expected = V1 if typed in ("C:\\outside-ws\\x.pdf", "..\\x.pdf") else U1
        assert toasts == [expected], toasts
        assert screen.graph.nodes["nom"].ficha.attachments == []
        assert MapStore(ws).load("att").nodes["nom"].ficha.attachments == []
        assert "attachment added" not in _flat(app.screen)


@pytest.mark.parametrize("typed,kind", [("docs/x.pdf", "file"), ("https://example.com/acta", "url")])
async def test_inc9n_u2_pin_a_workspace_file_and_a_url_are_stored(typed, kind, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, typed)
        assert toasts == [] or U1 not in toasts, toasts
        stored = MapStore(tmp_path).load("att").nodes["nom"].ficha.attachments
        assert [(a.kind, a.path) for a in stored] == [(kind, typed)], stored
        assert "attachment added" in _flat(app.screen)


async def test_inc9n_u2_pin_a_drive_absolute_file_inside_the_workspace_is_stored(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    inside = str(tmp_path / "docs" / "x.pdf")
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, inside)
        stored = MapStore(tmp_path).load("att").nodes["nom"].ficha.attachments
        assert [(a.kind, a.path) for a in stored] == [("file", inside)], (stored, toasts)


# ---------------------------------------------------------------------------
# INC9M-SEC-F3 / CR-F5 -- `_fetch_gh`: a failing commit lookup carries nothing over; progress reaches total

def _stub_commits(monkeypatch, *, branches, failing, dates):
    def fake_gh(self, args):
        if args[:2] == ["repo", "view"]:
            return {"name": "r", "defaultBranchRef": {"name": "main"}}
        path = args[1]
        if "/branches?" in path:
            return [{"name": b} for b in branches]
        if path.endswith("/tags?per_page=20"):
            return []
        if "/compare/" in path:
            return {"ahead_by": 0, "behind_by": 0}
        if "/check-runs" in path:
            return {"check_runs": []}
        if "/commits/" in path:
            name = path.rsplit("/", 1)[1]
            if name in failing:
                raise GitHubError("boom")
            return {"sha": "s-" + name, "commit": {"committer": {"date": dates[name]}}}
        return {}

    monkeypatch.setattr(GitHubConnector, "_gh", fake_gh)


@red("f3")
def test_inc9n_f3_a_failing_first_commit_lookup_does_not_unbind_commit(monkeypatch):
    _stub_commits(monkeypatch, branches=["a", "b"], failing={"a"},
                  dates={"b": "2026-02-03T00:00:00Z"})
    graph = GitHubConnector("o/r")._fetch_gh()
    assert graph.nodes["a"].ficha.fields["date"] == ""
    assert graph.nodes["b"].ficha.fields["date"] == "2026-02-03"


@red("f3")
def test_inc9n_f3_a_failing_later_commit_lookup_does_not_keep_the_previous_date(monkeypatch):
    _stub_commits(monkeypatch, branches=["a", "b"], failing={"b"},
                  dates={"a": "2026-01-01T00:00:00Z"})
    graph = GitHubConnector("o/r")._fetch_gh()
    assert graph.nodes["a"].ficha.fields["date"] == "2026-01-01"
    assert graph.nodes["b"].ficha.fields["date"] == ""


@red("f3")
def test_inc9n_f3_both_lookups_failing_still_fetches_with_empty_dates(monkeypatch):
    _stub_commits(monkeypatch, branches=["a", "b"], failing={"a", "b"}, dates={})
    graph = GitHubConnector("o/r")._fetch_gh()
    assert [graph.nodes[n].ficha.fields["date"] for n in ("a", "b")] == ["", ""]


@red("crf5")
@pytest.mark.parametrize("branches", [["ok", "..", "."], ["..", ".", "ok"], [".", ".."]])
def test_inc9n_cr_f5_progress_reaches_total_when_a_branch_is_skipped(branches, monkeypatch):
    _stub_gh(monkeypatch, branches=[{"name": b} for b in branches], tags=[], sha="abc")
    seen: list[tuple[int, int]] = []
    GitHubConnector("o/r")._fetch_gh(progress=lambda cur, tot, stage: seen.append((cur, tot)))
    total = len(branches)
    assert [c for c, _ in seen] == list(range(0, total + 1)), seen
    assert {t for _, t in seen} == {total}, seen


# ---------------------------------------------------------------------------
# INC9M-CR-F8 -- one public name for the source kind; no redundant guard; no `.resolve()` on an Optional

@red("crf8")
def test_inc9n_cr_f8_source_kind_is_public_and_the_badge_reads_it():
    for text in ("o/r", "https://h/o/r", "git@h:r"):
        assert github.source_kind(text) == github._classify(text), text
    with pytest.raises(GitHubError):
        github.source_kind("https://u:tok@h/o/r")
    # `2026-10-09-modular-batch` (LLR-MOD.5.2): the badge reader moved out of `app.py`
    # (A5b: `RepoScreen` -> `screens/repo.py`), so the scan covers every product module
    # but `github.py` itself -- stronger than the one file it used to read.
    used: set[str] = set()
    for path in sorted(REPO_ROOT.rglob("*.py")):
        if path.name == "github.py" and path.parent == REPO_ROOT:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        used |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)
                 and isinstance(n.value, ast.Name) and n.value.id == "github"}
    assert "source_kind" in used and "_classify" not in used, used


@red("crf8")
def test_inc9n_cr_f8_the_redundant_first_character_guard_is_gone_and_the_grammar_is_unchanged():
    tree = ast.parse((REPO_ROOT / "osopen.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "safe_local_path")
    indexed = [n for n in ast.walk(fn) if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
               and n.value.id == "text"]
    assert indexed == [], [n.lineno for n in indexed]
    for text in ("\\x", "/x", "\\/h/s", "/\\h/s", "\\\\h\\s", "//h/s"):
        assert osopen.safe_local_path(text) is None, text
    assert osopen.safe_local_path("o/r") is not None


@red("crf8")
def test_inc9n_cr_f8_fetch_does_not_call_resolve_on_an_optional():
    tree = ast.parse((REPO_ROOT / "github.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "fetch")
    chained = [n for n in ast.walk(fn) if isinstance(n, ast.Attribute) and n.attr == "resolve"
               and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
               and n.value.func.id == "safe_local_path"]
    assert chained == [], [n.lineno for n in chained]


def test_inc9n_cr_f8_pin_fetch_still_reads_a_local_git_folder(tmp_path, monkeypatch):
    (tmp_path / "work" / ".git").mkdir(parents=True)
    seen: list = []
    monkeypatch.setattr(github, "_build_graph_from_git",
                        lambda cwd, name, progress=None: seen.append((cwd, name)) or Graph())
    GitHubConnector(str(tmp_path / "work")).fetch()
    assert seen and seen[0][1] == "work", seen
