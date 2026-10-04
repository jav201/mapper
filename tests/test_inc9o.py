"""Inc-9o -- the one containment helper (`osopen.confine`), the sidecar document NAME (INC9N-SEC-F1),
the second refusal sentence (V1) and the template-outside text (V2).

Authority: `A-123` and `VERDICT-inc9-2026-09-30.md` Rounds 10-11.  Every arm a fix closes was committed RED
first as a STRICT xfail keyed by the step that closes it (`OPEN_STEPS`); an arm that is not keyed is a pin
(green on the base), killed by a mutant instead.

Nothing here reaches the network or a real UNC, console or COM device.  A link is only ever created to a
LOCAL directory under `tmp_path`; a spy refuses (and records) any filesystem call for a hostile form BEFORE
the real call is made.  The sentences are literals here on purpose, so an arm does not pass because it
imports the very constant it is checking.  Control characters would be `\\u` escapes; none is needed.
"""
from __future__ import annotations

import ast
import builtins
import io
import os
import pathlib
import subprocess
import sys

import pytest

from mapper import osopen
from mapper.app import MapperApp
from mapper.model import Attachment, Document, Ficha, Graph, Node
from mapper.screens.factory import FactoryScreen
from mapper.store import MapStore
from mapper.widgets.inspector import FichaInspector
from tests.test_attachments import RecordingLauncher, _open, _seed
from tests.test_inc9f import NARROW, SIZE
from tests.test_inc9m import _env, _flat, _no_fs, _norm
from tests.test_inc9n import U1, _add_attachment, _make_docx, _toasts

# Inc-9p: the arms whose expected sentence changed (`W1`, `W2`) were committed RED first, keyed by step.
# Inc-9q (X2): the three sealed V2 pins whose sentence changed to U1 were committed RED first.
OPEN_STEPS: set[str] = set()

PKG = pathlib.Path(osopen.__file__).parent

V1 = "attachment must be inside the workspace: use a relative path"
V2 = "template outside the workspace: import it with i"
# Inc-9p (`W1`, `W2`): the three sentences are literals here, so an arm does not pass because it imports them.
W1_DOC = "document name cannot be a file name: rename it in the map's _nodos.yml (documents)"
W1_NODE = "node id cannot be a file name: rename the node"
W2 = "path goes through a link: use a real folder inside the workspace"
MISSING = "template file not found"


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9o: committed RED; closed by the '{step}' step")
    return lambda fn: fn


def _red_mark(step: str):
    return ([pytest.mark.xfail(strict=True, reason=f"Inc-9o: committed RED; closed by the '{step}' step")]
            if step in OPEN_STEPS else [])


def _confine(text, workspace):
    return osopen.confine(text, workspace)


# ---------------------------------------------------------------------------
# `confine` itself: lexical containment (no stat), sibling prefix, relative workspace, `~`

ACCEPTED = [
    ("relative", lambda ws, o: "docs/a.pdf"),
    ("bare name", lambda ws, o: "a.pdf"),
    ("dot-dot that stays inside", lambda ws, o: "docs\\..\\docs\\a.pdf"),
    ("drive-absolute inside", lambda ws, o: str(ws / "docs" / "a.pdf")),
    ("drive-absolute, upper-cased (Windows is case-insensitive)", lambda ws, o: str(ws).upper() + "\\docs\\a.pdf"),
]


@red("confine")
@pytest.mark.parametrize("label,make", ACCEPTED, ids=[a[0] for a in ACCEPTED])
def test_inc9o_confine_accepts_a_path_inside_the_workspace(label, make, tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    got = _confine(make(ws, tmp_path), ws)
    assert got is not None, label
    assert got.is_relative_to(ws.resolve()), got


REFUSED_LEXICALLY = [
    ("dot-dot out", lambda ws, o: "..\\x.pdf"),
    ("dot-dot into the sibling `ws2` (a string prefix of the workspace)", lambda ws, o: "..\\ws2\\x.pdf"),
    ("the sibling `ws2` by absolute path", lambda ws, o: str(o / "ws2" / "x.pdf")),
    ("the sibling `ws2` itself", lambda ws, o: str(o / "ws2")),
    ("a sibling that shares the workspace's whole name as a prefix", lambda ws, o: str(ws) + "-extra\\x.pdf"),
    ("the parent", lambda ws, o: str(o)),
    ("drive-absolute outside", lambda ws, o: "C:\\outside\\x.pdf"),
    ("a deep dot-dot", lambda ws, o: "docs\\..\\..\\x.pdf"),
    ("UNC", lambda ws, o: "\\\\h\\s\\x.pdf"),
    ("an NT-namespace UNC", lambda ws, o: "\\??\\UNC\\h\\s\\x.pdf"),
    ("a DOS device", lambda ws, o: "con"),
    ("an empty text", lambda ws, o: ""),
    ("a leading dash", lambda ws, o: "-x.pdf"),
]


@red("confine")
@pytest.mark.parametrize("label,make", REFUSED_LEXICALLY, ids=[a[0] for a in REFUSED_LEXICALLY])
def test_inc9o_confine_refuses_without_touching_the_disk(label, make, tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    (tmp_path / "ws2").mkdir()
    text = make(ws, tmp_path)
    with _no_fs(monkeypatch) as hits:
        assert _confine(text, ws) is None, label
    assert hits == [], hits


@red("confine")
def test_inc9o_confine_judges_a_relative_workspace_by_its_absolute_form(tmp_path, monkeypatch):
    """`INC9N-CR-F1`: `Path("ws")` against an absolute document inside it (the old test mixed relative
    and absolute forms and refused it)."""
    (tmp_path / "ws" / "docs").mkdir(parents=True)
    (tmp_path / "ws2").mkdir()
    monkeypatch.chdir(tmp_path)
    inside = _confine(str(tmp_path / "ws" / "docs" / "a.pdf"), pathlib.Path("ws"))
    assert inside is not None and inside.is_relative_to((tmp_path / "ws").resolve())
    assert _confine("docs/a.pdf", pathlib.Path("ws")) is not None
    assert _confine(str(tmp_path / "ws2" / "a.pdf"), pathlib.Path("ws")) is None
    assert _confine("..\\ws2\\a.pdf", pathlib.Path("ws")) is None


@red("confine")
def test_inc9o_confine_expands_a_tilde_the_same_way_for_every_caller(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    _env(monkeypatch, ws)
    assert _confine("~/docs/a.pdf", ws) is not None
    _env(monkeypatch, tmp_path)
    assert _confine("~/docs/a.pdf", ws) is None
    assert _confine("~nosuchuser/a.pdf", ws) is None


# ---------------------------------------------------------------------------
# `SEC-F3`: a link under the workspace is refused BEFORE anything below it is touched

def _link(kind: str, link: pathlib.Path, target: pathlib.Path) -> None:
    """A junction or a symlink to a LOCAL directory; never a network target."""
    assert target.is_dir() and not str(target).startswith("\\\\")
    link.parent.mkdir(parents=True, exist_ok=True)
    if kind == "junction":
        if sys.platform != "win32":
            pytest.skip("junctions are Windows-only")
        made = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                              capture_output=True, text=True)
        if made.returncode != 0:
            pytest.skip("a directory junction could not be created here")
    else:
        try:
            os.symlink(target, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            pytest.skip("a symlink could not be created here")


class _Walk:
    """Records the calls a link component must never cause (`stat`, `resolve`, the final-path lookup), and
    the `os.lstat` calls the walk makes (the allowed ones), wrapping the real functions."""

    def __init__(self, monkeypatch):
        self.forbidden: list[str] = []
        self.lstat: list[str] = []
        real_lstat = os.lstat

        def lstat(path, *a, **kw):
            self.lstat.append(_norm(os.fspath(path)))
            return real_lstat(path, *a, **kw)

        monkeypatch.setattr(os, "lstat", lstat)
        for owner, name in ((os, "stat"), (pathlib.Path, "resolve"), (os.path, "realpath"),
                            (pathlib.Path, "stat"), (pathlib.Path, "exists"), (pathlib.Path, "is_file")):
            monkeypatch.setattr(owner, name, self._wrap(f"{owner.__name__}.{name}", getattr(owner, name)))
        nt = sys.modules.get("nt")
        if nt is not None and hasattr(nt, "_getfinalpathname"):
            monkeypatch.setattr(nt, "_getfinalpathname",
                                self._wrap("nt._getfinalpathname", nt._getfinalpathname))
        ntp = sys.modules.get("ntpath")
        if ntp is not None and hasattr(ntp, "_getfinalpathname"):
            # `INC9O-SEC-F4`: `realpath` binds the name inside `ntpath`; patching `nt` alone is blind to it.
            monkeypatch.setattr(ntp, "_getfinalpathname",
                                self._wrap("ntpath._getfinalpathname", ntp._getfinalpathname))

    def _wrap(self, name, real):
        def probe(*a, **kw):
            self.forbidden.append(name)
            return real(*a, **kw)
        return probe


LINK_SHAPES = [
    ("the link is the first component", "link/a.docx"),
    ("the link is the last component", "link"),
    ("a link under a real directory", "d/link/sub/a.docx"),
]


@red("walk")
@pytest.mark.parametrize("kind", ["junction", "symlink"])
@pytest.mark.parametrize("label,text", LINK_SHAPES, ids=[s[0] for s in LINK_SHAPES])
def test_inc9o_confine_refuses_a_link_before_any_stat_resolve_or_final_path_lookup(
        kind, label, text, tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    (ws / "d").mkdir(parents=True)
    out = tmp_path / "outside"
    (out / "sub").mkdir(parents=True)
    _link(kind, ws / ("d/link" if text.startswith("d/") else "link"), out)
    spy = _Walk(monkeypatch)
    assert _confine(text, ws) is None
    assert spy.forbidden == [], spy.forbidden
    assert spy.lstat, "the walk made no lstat call: the link was never looked at"
    linked = "\\ws\\d\\link" if text.startswith("d/") else "\\ws\\link"
    assert spy.lstat[-1].lower().endswith(linked), spy.lstat
    assert not any("sub" in call.lower() or "a.docx" in call.lower() for call in spy.lstat), spy.lstat


@red("walk")
def test_inc9o_confine_does_not_follow_a_junction_that_stays_inside_the_workspace(tmp_path, monkeypatch):
    """Policy: links inside the workspace are not followed, even when they lead nowhere dangerous."""
    ws = tmp_path / "ws"
    (ws / "real").mkdir(parents=True)
    _link("junction", ws / "alias", ws / "real")
    spy = _Walk(monkeypatch)
    assert _confine("alias/a.docx", ws) is None
    assert spy.forbidden == [], spy.forbidden


@red("walk")
def test_inc9o_confine_checks_each_prefix_in_order_and_stops_at_the_link(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    (ws / "d").mkdir(parents=True)
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "d" / "link", tmp_path / "outside")
    spy = _Walk(monkeypatch)
    assert _confine("d/link/deeper/a.docx", ws) is None
    got = [c.lower().rsplit("\\ws\\", 1)[-1] for c in spy.lstat]
    assert got == ["d", "d\\link"], got


@red("confine")
def test_inc9o_pin_confine_accepts_real_directories_and_a_missing_file(tmp_path):
    ws = tmp_path / "ws"
    (ws / "d" / "e").mkdir(parents=True)
    assert _confine("d/e/missing.docx", ws) is not None
    assert _confine("d/not/yet/there.docx", ws) is not None
    (ws / "d" / "e" / "a.docx").write_bytes(b"x")
    got = _confine("d/e/a.docx", ws)
    assert got is not None and got.is_file()


@red("confine")
def test_inc9o_pin_a_workspace_that_is_itself_a_link_still_works(tmp_path):
    """Only what lies UNDER the workspace is walked: the operator may keep the workspace behind a link."""
    real = tmp_path / "real"
    (real / "docs").mkdir(parents=True)
    _link("junction", tmp_path / "ws", real)
    got = _confine("docs/a.docx", tmp_path / "ws")
    assert got is not None and got.is_relative_to(real.resolve())


@red("confine")
@pytest.mark.parametrize("error", [OSError("blocked"), ValueError("blocked")])
def test_inc9o_confine_refuses_when_the_final_resolve_fails(error, tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()

    def boom(self, *a, **kw):
        raise error

    monkeypatch.setattr(pathlib.Path, "resolve", boom)
    assert _confine("a.pdf", ws) is None


@red("confine")
def test_inc9o_confine_judges_what_resolve_returns_as_a_last_check(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    # Inc-9q: the file exists, so the walk reaches the end and `resolve()` is asked about the whole path.  (A
    # missing file is judged by the resolved WALKED prefix plus a lexical tail: `test_inc9q`.)
    (ws / "a.pdf").write_bytes(b"1")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    real = pathlib.Path.resolve
    monkeypatch.setattr(pathlib.Path, "resolve",
                        lambda self, *a, **kw: elsewhere / "a.pdf" if self.name == "a.pdf" else real(self, *a, **kw))
    assert _confine("a.pdf", ws) is None


@red("walk")
def test_inc9o_confine_fails_closed_when_a_component_cannot_be_inspected(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    (ws / "d").mkdir(parents=True)

    def denied(path, *a, **kw):
        raise PermissionError("blocked")

    monkeypatch.setattr(os, "lstat", denied)
    assert _confine("d/a.pdf", ws) is None


# ---------------------------------------------------------------------------
# `open_external` and the factory use the same rule (the three copies are gone)

@pytest.mark.parametrize("leads_out", [True, pytest.param(False, marks=_red_mark("walk"))])
def test_inc9o_open_external_refuses_a_link_inside_the_workspace(leads_out, tmp_path):
    """Whether the link leads outside (the old `resolve()` caught it) or stays inside (only the walk does)."""
    ws = tmp_path / "ws"
    (ws / "real").mkdir(parents=True)
    (tmp_path / "outside").mkdir()
    for folder in (tmp_path / "outside", ws / "real"):
        (folder / "a.pdf").write_bytes(b"x")
    _link("junction", ws / "link", tmp_path / "outside" if leads_out else ws / "real")
    launcher = RecordingLauncher()
    assert osopen.open_external("file", "link/a.pdf", workspace=ws, launcher=launcher) == osopen.REFUSED_OUTSIDE
    assert launcher.calls == []


def test_inc9o_open_external_judges_a_relative_workspace(tmp_path, monkeypatch):
    (tmp_path / "ws").mkdir()
    (tmp_path / "ws" / "a.pdf").write_bytes(b"x")
    monkeypatch.chdir(tmp_path)
    launcher = RecordingLauncher()
    got = osopen.open_external("file", str(tmp_path / "ws" / "a.pdf"), workspace=pathlib.Path("ws"),
                               launcher=launcher)
    assert got == osopen.OK and len(launcher.calls) == 1


@red("confine")
def test_inc9o_there_is_one_containment_and_one_home_for_the_sentences():
    """No other module owns an `is_relative_to`, a `normpath`, or the sentences' text (`INC9N-CR-F2/F4`)."""
    sources = {rel: (PKG / rel).read_text(encoding="utf-8") for rel in ("app.py", "screens/factory.py", "osopen.py")}
    for rel in ("app.py", "screens/factory.py"):
        tree = ast.parse(sources[rel])
        attrs = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        assert not attrs & {"is_relative_to", "normpath", "abspath"}, (rel, attrs & {"is_relative_to", "normpath"})
        strings = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        assert U1 not in strings and V1 not in strings, rel
    assert not hasattr(sys.modules["mapper.app"], "_is_workspace_file_target")
    assert osopen.PATH_NOT_SUPPORTED == U1 and osopen.PATH_OUTSIDE_WORKSPACE == V1
    factory_tree = ast.parse(sources["screens/factory.py"])
    from_app = [n for n in ast.walk(factory_tree) if isinstance(n, ast.ImportFrom) and n.module == "mapper.app"]
    assert all(a.name != "PATH_NOT_SUPPORTED" for n in from_app for a in n.names)


# ---------------------------------------------------------------------------
# V1: the second sentence, at add and at open (real keys at 118 and 87)

@red("v1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("typed", ["C:\\outside\\x.pdf", "..\\x.pdf"])
async def test_inc9o_v1_adding_an_outside_file_toasts_the_workspace_sentence(typed, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, typed)
        assert toasts == [V1], toasts
        assert screen.graph.nodes["nom"].ficha.attachments == []
        assert MapStore(ws).load("att").nodes["nom"].ficha.attachments == []


@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9o_v1_adding_a_unc_file_still_toasts_the_allow_list_sentence(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    forms = ["\\\\h\\s\\x.pdf"]
    hits: list[str] = []
    real = pathlib.Path.resolve

    def resolve(self, *a, **kw):
        if any(f in _norm(self) for f in forms):
            hits.append(str(self))
            raise OSError("blocked")
        return real(self, *a, **kw)

    monkeypatch.setattr(pathlib.Path, "resolve", resolve)
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, "\\\\h\\s\\x.pdf")
        assert toasts == [U1], toasts
        assert screen.graph.nodes["nom"].ficha.attachments == []
    assert hits == []


async def test_inc9o_v1_pin_a_relative_workspace_file_is_stored(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, "docs/x.pdf")
        assert toasts == [] or (U1 not in toasts and V1 not in toasts), toasts
        stored = MapStore(tmp_path).load("att").nodes["nom"].ficha.attachments
        assert [(a.kind, a.path) for a in stored] == [("file", "docs/x.pdf")]
        assert "attachment added" in _flat(app.screen)


async def _activate(app, pilot, attachments, size=SIZE):
    launcher = RecordingLauncher()
    app.attachment_launcher = launcher
    notes: list[str] = []
    screen = await _open(app, pilot, _seed(app, attachments))
    screen.notify = lambda msg, **kw: notes.append(str(msg))
    screen.query_one("#map-inspector", FichaInspector).post_message(FichaInspector.AttachmentActivated("nom", 0))
    for _ in range(3):
        await pilot.pause()
    return launcher, notes


@red("v1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("target", ["C:\\outside\\x.pdf", "..\\..\\etc\\x.pdf"])
async def test_inc9o_v1_opening_an_outside_file_toasts_the_workspace_sentence(target, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        launcher, notes = await _activate(app, pilot, [Attachment(kind="file", path=target, caption="c")])
        assert notes == [V1], notes
        assert launcher.calls == []


@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9o_v1_opening_a_unc_file_keeps_the_allow_list_sentence(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        launcher, notes = await _activate(app, pilot, [Attachment(kind="file", path="\\\\h\\s\\x.pdf", caption="c")])
        assert notes == [U1], notes
        assert launcher.calls == []


@red("w2")
async def test_inc9o_v1_opening_a_file_behind_a_link_toasts_the_link_sentence(tmp_path, monkeypatch):
    """Inc-9p (`W2`): a path through a link has its own sentence, no longer V1.  Inc-9q (`INC9P-CR-F8`): the
    test name said 'workspace sentence' for a W2 assertion; a label change only."""
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "a.pdf").write_bytes(b"x")
    _link("junction", ws / "link", tmp_path / "outside")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        launcher, notes = await _activate(app, pilot, [Attachment(kind="file", path="link/a.pdf", caption="c")])
        assert notes == [W2], notes
        assert launcher.calls == []


@pytest.mark.parametrize("home_inside", [pytest.param(True, marks=_red_mark("confine")),
                                         pytest.param(False, marks=_red_mark("v1"))])
async def test_inc9o_a_tilde_is_judged_the_same_at_add_and_at_open(home_inside, tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    (ws / "docs" / "x.pdf").write_bytes(b"x")
    _env(monkeypatch, ws if home_inside else tmp_path)
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, "~/docs/x.pdf")
        stored = MapStore(ws).load("att").nodes["nom"].ficha.attachments
        if home_inside:
            assert [(a.kind, a.path) for a in stored] == [("file", "~/docs/x.pdf")], (stored, toasts)
        else:
            assert stored == [] and toasts == [V1], (stored, toasts)
        launcher, notes = await _activate(app, pilot, [Attachment(kind="file", path="~/docs/x.pdf", caption="c")])
        if home_inside:
            assert notes == [] and len(launcher.calls) == 1, (notes, launcher.calls)
        else:
            assert notes == [V1] and launcher.calls == [], (notes, launcher.calls)


# ---------------------------------------------------------------------------
# V2: the factory says WHY a template outside the workspace is not previewed, decided by text

def _doc_graph(path: str, name: str = "plantilla", node_id: str = "root") -> Graph:
    g = Graph()
    g.add_node(Node(id=node_id, ficha=Ficha(title="proceso")))
    g.documents[name] = Document(name=name, path=path, kind="docx", template=True)
    return g


class _Forms:
    """Refuses (and records) a filesystem call whose path mentions one of `forms`, BEFORE the real call."""

    def __init__(self, monkeypatch, forms):
        self.hits: list[str] = []
        self.forms = [_norm(f).lower() for f in forms]
        for owner, names in (
                (pathlib.Path, ("mkdir", "open", "stat", "lstat", "resolve", "exists", "is_file", "is_dir",
                                "read_bytes", "read_text", "write_bytes", "samefile")),
                (os, ("stat", "lstat", "mkdir", "scandir", "listdir")),
                (os.path, ("exists", "isfile", "isdir", "realpath", "getsize", "lexists", "islink")),
                (builtins, ("open",)), (io, ("open",))):
            for name in names:
                monkeypatch.setattr(owner, name, self._wrap(f"{owner.__name__}.{name}", getattr(owner, name)))
        nt = sys.modules.get("nt")
        if nt is not None and hasattr(nt, "_getfinalpathname"):
            monkeypatch.setattr(nt, "_getfinalpathname", self._wrap("nt._getfinalpathname", nt._getfinalpathname))
        ntp = sys.modules.get("ntpath")
        if ntp is not None and hasattr(ntp, "_getfinalpathname"):
            monkeypatch.setattr(ntp, "_getfinalpathname", self._wrap("ntpath._getfinalpathname", ntp._getfinalpathname))

    def _bad(self, value) -> bool:
        if not isinstance(value, (str, os.PathLike)):
            return False
        text = _norm(os.fspath(value))
        if not isinstance(text, str):
            return False
        text = text.lower()
        if any(f in text for f in self.forms):
            return True
        return any(pathlib.PureWindowsPath(p).is_reserved() for p in pathlib.PureWindowsPath(text).parts)

    def _wrap(self, name, real):
        def probe(first, *a, **kw):
            if self._bad(first):
                self.hits.append(f"{name}({first})")
                raise OSError("blocked: a filesystem call for a hostile form")
            return real(first, *a, **kw)
        return probe


@red("v2")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9o_v2_an_absolute_template_outside_the_workspace_says_so_without_a_stat(
        size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    outside = tmp_path / "elsewhere" / "t.docx"
    _make_docx(outside, "hola")
    spy = _Forms(monkeypatch, [str(outside)])
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph(str(outside)), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        frame = _flat(screen)
        assert V2 in frame and MISSING not in frame and "hola" not in frame, frame
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [V2], toasts
    assert spy.hits == [], spy.hits


@red("v2")
async def test_inc9o_v2_a_dot_dot_template_outside_the_workspace_says_so(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    _make_docx(tmp_path / "secret.docx", "hola")
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("..\\secret.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert V2 in _flat(screen), _flat(screen)


@pytest.mark.parametrize("doc_path,expected", [
    pytest.param("\\\\h\\s\\a.docx", U1, marks=_red_mark("x2")),
    pytest.param("//h/s/a.docx", U1, marks=_red_mark("x2")),
    pytest.param("con", U1, marks=_red_mark("x2")),
    ("docs/missing.docx", MISSING),
])
async def test_inc9o_v2_pin_every_other_missing_template_keeps_the_existing_text(
        doc_path, expected, tmp_path, monkeypatch):
    """Inc-9q (X2, operator-ruled sealed-arm change): UNC, `//h/s` and `con` expect U1 now (the path rule
    refused them: 'not found' was a lie); only a template that is missing keeps `MISSING`."""
    _env(monkeypatch, tmp_path)
    spy = _Forms(monkeypatch, ["\\\\h\\s\\a.docx", "//h/s/a.docx"])
    app = MapperApp(tmp_path)
    toasts = _toasts(app)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph(doc_path), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert expected in _flat(screen) and V2 not in _flat(screen), _flat(screen)
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [expected], toasts
    assert spy.hits == [], spy.hits


@red("w2")
async def test_inc9o_v2_a_template_behind_a_link_is_not_called_outside(tmp_path, monkeypatch):
    """Not decided by text: a link is refused by the walk, so V2 ('outside') is not said.  Inc-9p (`W2`): it
    says its own sentence for a link instead of the old 'not found'."""
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    _make_docx(tmp_path / "outside" / "a.docx", "hola")
    _link("junction", ws / "link", tmp_path / "outside")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("link/a.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert W2 in _flat(screen) and MISSING not in _flat(screen) and V2 not in _flat(screen), _flat(screen)


@red("confine")
async def test_inc9o_a_relative_workspace_previews_an_absolute_document_inside_it(tmp_path, monkeypatch):
    """`INC9N-CR-F1`, through the real screen: `MapperApp(Path("ws"))` and a drive-absolute template."""
    _env(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    _make_docx(tmp_path / "ws" / "docs" / "a.docx", "hola {{nombre}}")
    app = MapperApp(pathlib.Path("ws"))
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph(str(tmp_path / "ws" / "docs" / "a.docx")), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert "hola" in _flat(screen) and MISSING not in _flat(screen), _flat(screen)


# ---------------------------------------------------------------------------
# INC9N-SEC-F1: the document NAME and the node id are the output file name

HOSTILE_NAMES = ["..\\..\\ESCAPED", "\\\\h\\s\\x", "C:\\Windows\\Temp\\x", "con", "a/b", "x:y"]


def _tree(root: pathlib.Path) -> list[str]:
    return sorted(str(p.relative_to(root)) for p in root.rglob("*"))


@red("w1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("name", HOSTILE_NAMES)
async def test_inc9o_sec_f1_a_hostile_document_name_writes_nothing_and_touches_nothing_outside(
        name, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "w1" / "w2" / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")
    spy = _Forms(monkeypatch, ["ESCAPED", "\\\\h\\s", "Windows\\Temp"])
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        before = _tree(tmp_path)
        screen = FactoryScreen(_doc_graph("docs/t.docx", name=name), process_name="demo", document_name=name)
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        screen.action_generate_office()
        await pilot.pause()
        assert app.is_running
        assert toasts == [W1_DOC], toasts
        assert _tree(tmp_path) == before, set(_tree(tmp_path)) ^ set(before)
    assert spy.hits == [], spy.hits


@red("w1")
@pytest.mark.parametrize("node_id", ["a:b", "con", "x.", "a b "])
async def test_inc9o_sec_f1_a_hostile_node_id_writes_nothing(node_id, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        before = _tree(tmp_path)
        screen = FactoryScreen(_doc_graph("docs/t.docx", node_id=node_id), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [W1_NODE], toasts
        assert _tree(tmp_path) == before


async def test_inc9o_sec_f1_pin_a_normal_name_still_generates_inside_the_workspace(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola {{nombre}}")
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("docs/t.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == ["generated: plantilla-root.docx"], toasts
    assert (ws / "plantilla-root.docx").is_file()


@red("w2")
async def test_inc9o_sec_f1_a_link_where_the_output_would_be_written_is_refused(tmp_path, monkeypatch):
    """The name is plain, but `ws/plantilla-root.docx` is a link: nothing may be written through it."""
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "plantilla-root.docx", tmp_path / "outside")
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("docs/t.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [W2], toasts
    assert _tree(tmp_path / "outside") == []
