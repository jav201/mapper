"""Inc-9q -- fixes for the Inc-9p reviews: a stream-type suffix on a link component (INC9P-SEC-F1, HIGH), the
unwalked tail and MAX_PATH (SEC-F4 closed in defence in depth), a hard-linked attachment at open time (SEC-F3),
the parent swapped for a link after `mkstemp` (SEC-F2), the operator's hard-link sentences (X1) and the path
sentence for a refused template (X2), one reason -> sentence mapping (CR-F1) and the import's unreadable
sentence (CR-F3), a failed generate (CR-F2), `lexically_outside` removed (CR-F4), one `confine_reason` call in
the preview (CR-F5) and the order of steps 1b and 2 (CR-F7).

Authority: `A-125` and `VERDICT-inc9-2026-09-30.md` Round 13.  Every arm a fix closes was committed RED first as a
STRICT xfail keyed by the step that closes it (`OPEN_STEPS`); an arm that is not keyed is a pin (green on the
base), killed by a mutant instead.

Nothing here reaches the network, a real UNC, a console or COM device.  A link is only ever created to a LOCAL
directory under `tmp_path` (a junction, or a hard link between two temp files); a spy refuses and records a
filesystem call BEFORE the real one is made.  The sentences are literals here on purpose.  Control and bidi
characters would be `\\u` escapes; this file is ASCII.
"""
from __future__ import annotations

import ast
import os
import pathlib
import shutil
import sys
import tempfile

import pytest

from mapper import app as app_module
from mapper import office as office_module
from mapper import osopen
from mapper.app import MapperApp
from mapper.model import Attachment
from mapper.screens import factory as factory_module
from mapper.screens.factory import FactoryScreen
from tests.test_inc9f import NARROW, SIZE
from tests.test_inc9m import _env, _flat, _no_fs
from tests.test_inc9n import U1, _make_docx, _toasts
from tests.test_inc9o import V1, W2, _activate, _doc_graph, _link, _tree
from tests.test_inc9p import MISSING, _generate, _import, _Replace, _ws_tree

# Inc-9r: the arms whose expectation changed (Y1 `r_colon`, CR-F1 `r_backstop`) are committed RED first, keyed by step.
OPEN_STEPS: set[str] = set()

PKG = pathlib.Path(osopen.__file__).parent

ATT_HARD = "attachment has several hard links: replace it with a plain copy"
CR_F3 = "templates folder could not be checked: use a real folder named templates inside the workspace"


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9q: committed RED; closed by the '{step}' step")
    return lambda fn: fn


def _red_mark(step: str):
    return ([pytest.mark.xfail(strict=True, reason=f"Inc-9q: committed RED; closed by the '{step}' step")]
            if step in OPEN_STEPS else [])


# ---------------------------------------------------------------------------
# INC9P-SEC-F1: `lnk:$I30` makes `os.lstat` raise FileNotFoundError, the walk stops, `resolve()` follows the link

# (the typed form, the junction it names).  The 8.3 form names a junction with a long name; whether the volume
# makes an 8.3 alias is not relied on: the refusal is on the TEXT.
STREAM_FORMS = [
    ("lnk:$I30", "lnk"),
    ("lnk::$BITMAP", "lnk"),
    ("lnk:$I30:$BITMAP", "lnk"),
    ("lnk::$DATA", "lnk"),
    ("lnk::$INDEX_ALLOCATION", "lnk"),
    ("JLINKN~1:$I30", "jlinkname"),
    # Inc-9r (CR-F4): a single-letter junction.  At the top level `l:$I30` is a drive-relative path to pathlib and
    # `safe_local_path` refuses it (`allow_list`, see the pin below); one level down it is a component, and step 1b
    # refuses it.
    ("sub/l:$I30", "sub/l"),
]


@red("r_colon")
@pytest.mark.parametrize("tail", ["/x.pdf", ""])
@pytest.mark.parametrize("form,junction", STREAM_FORMS)
@pytest.mark.parametrize("where", ["outside", "inside"])
def test_inc9q_sec_f1_a_stream_suffix_on_a_link_component_is_refused_before_any_filesystem_call(
        where, form, junction, tail, tmp_path, monkeypatch):
    """Measured on the base: an inside junction was returned `ok`.  Now the TEXT is refused as `colon` (Y1),
    with zero `os.stat`, `os.lstat`, `Path.resolve`, `nt._getfinalpathname` or `ntpath._getfinalpathname` call, so
    nothing reaches the link target either way."""
    ws = tmp_path / "ws"
    (ws / "real").mkdir(parents=True)
    target = tmp_path / "outside" if where == "outside" else ws / "real"
    target.mkdir(parents=True, exist_ok=True)
    (target / "x.pdf").write_bytes(b"1")
    _link("junction", ws / junction, target)
    text = form + tail
    with _no_fs(monkeypatch) as hits:
        got = osopen.confine_reason(text, ws)
        assert osopen.confine(text, ws) is None
    assert got == (None, "colon"), got
    assert hits == [], hits


@pytest.mark.parametrize("where", ["outside", pytest.param("inside", marks=_red_mark("colon"))])
def test_inc9q_sec_f1_a_stream_suffix_never_launches_through_open_external(where, tmp_path):
    """The same forms through the real entry point, on the real filesystem (the walk is not mocked).  Measured on
    the base: with an inside junction `open_external` returned `abierto` and called the launcher."""
    ws = tmp_path / "ws"
    (ws / "real").mkdir(parents=True)
    target = tmp_path / "outside" if where == "outside" else ws / "real"
    target.mkdir(parents=True, exist_ok=True)
    (target / "x.pdf").write_bytes(b"1")
    _link("junction", ws / "lnk", target)
    launched: list[str] = []
    for text in ("lnk:$I30/x.pdf", "lnk::$BITMAP/x.pdf", "lnk:$I30:$BITMAP/x.pdf"):
        status = osopen.open_external("file", text, workspace=ws, launcher=launched.append)
        assert status != osopen.OK, (text, status)
    assert launched == []


def test_inc9q_sec_f1_pin_ordinary_paths_still_work(tmp_path):
    """The drive anchor `C:\\` carries a colon and is exempt; a plain relative path, a `./` path, an absolute path
    inside the workspace and a file that does not exist yet are `ok`."""
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    (ws / "docs" / "a.pdf").write_bytes(b"1")
    inside = ws.resolve()
    for text, name in (
            (str(ws / "docs" / "a.pdf"), "a.pdf"),
            ("docs/a.pdf", "a.pdf"),
            ("docs\\a.pdf", "a.pdf"),
            ("./docs/a.pdf", "a.pdf"),
            ("docs/new.pdf", "new.pdf"),
            (str(ws / "docs" / "new.pdf"), "new.pdf")):
        got, why = osopen.confine_reason(text, ws)
        assert why == "ok" and got is not None and got.name == name and got.is_relative_to(inside), (text, got, why)
    assert osopen.confine_reason(str(tmp_path / "elsewhere" / "a.pdf"), ws) == (None, "outside")


# ---------------------------------------------------------------------------
# INC9P-SEC-F1 (b) / SEC-F4: the OS never resolves a tail the walk did not inspect

@red("r_backstop")
@pytest.mark.parametrize("tail", ["x.pdf", "new.pdf"])
@pytest.mark.parametrize("where", ["outside", "inside"])
def test_inc9q_sec_f4_the_unwalked_tail_is_appended_not_resolved(where, tail, tmp_path, monkeypatch):
    """Inc-9r (INC9Q-CR-F1) replaced the Inc-9q body, which asserted a proxy (the OS is never asked about `lnk`)
    and so accepted `ok` for a link the walk had been lied to about.  The property is that nothing behind the link
    is reachable: `lstat` is made to report `lnk` as not found, and the result must still be a refusal and
    nothing may be launched."""
    ws = tmp_path / "ws"
    (ws / "real").mkdir(parents=True)
    target = tmp_path / "outside" if where == "outside" else ws / "real"
    target.mkdir(parents=True, exist_ok=True)
    (target / "x.pdf").write_bytes(b"1")
    _link("junction", ws / "lnk", target)
    real = os.lstat

    def lying(path, *a, **kw):
        if os.path.basename(os.fspath(path)).lower() == "lnk":
            raise FileNotFoundError(2, "lie", os.fspath(path))
        return real(path, *a, **kw)

    monkeypatch.setattr(os, "lstat", lying)
    text = "lnk/" + tail
    got, why = osopen.confine_reason(text, ws)
    assert got is None and why in (("link", "outside") if where == "outside" else ("link",)), (got, why)
    launched: list[str] = []
    assert osopen.open_external("file", text, workspace=ws, launcher=launched.append) != osopen.OK
    assert launched == []


def test_inc9q_sec_f4_pin_a_missing_tail_is_the_walked_prefix_plus_the_tail(tmp_path):
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    assert osopen.confine_reason("docs/sub/new.pdf", ws) == (ws.resolve() / "docs" / "sub" / "new.pdf", "ok")


def _long_junction_tree(ws: pathlib.Path, target: pathlib.Path):
    """Six 55-character folders made with the `\\\\?\\` prefix (so the 260-character limit does not stop the
    setup), then a junction `j` to a LOCAL directory.  Returns (top, junction)."""
    if sys.platform != "win32":
        pytest.skip("junctions and MAX_PATH are Windows-only")
    import _winapi

    prefix = chr(92) * 2 + "?" + chr(92)
    cur = ws
    top = None
    try:
        for _ in range(6):
            cur = cur / ("d" * 55)
            os.mkdir(prefix + str(cur))
            top = top or cur
        junction = cur / "j"
        _winapi.CreateJunction(str(target), prefix + str(junction))
    except OSError:
        pytest.skip("a long path could not be created here")
    return top, junction


@red("maxpath")
@pytest.mark.parametrize("where", ["outside", "inside"])
def test_inc9q_sec_f4_a_340_character_path_with_a_junction_is_never_ok(where, tmp_path):
    """Measured on the base: `lstat` raises FileNotFoundError past MAX_PATH (long paths are not enabled for the
    process), the walk stopped before the junction and the result was `ok`.  Now a not-found past MAX_PATH is
    `unreadable`: a not-found that cannot be trusted refuses."""
    ws = tmp_path / "ws"
    (ws / "real").mkdir(parents=True)
    target = tmp_path / "outside" if where == "outside" else ws / "real"
    target.mkdir(parents=True, exist_ok=True)
    (target / "x.pdf").write_bytes(b"1")
    top, junction = _long_junction_tree(ws, target)
    prefix = chr(92) * 2 + "?" + chr(92)
    try:
        assert os.lstat(prefix + str(junction)).st_file_attributes & 0x400, "the junction was not created"
        text = junction.relative_to(ws).as_posix() + "/x.pdf"
        assert len(text) >= 340, len(text)
        got, why = osopen.confine_reason(text, ws)
        assert got is None and why in ("unreadable", "link"), (got, why)
        launched: list[str] = []
        assert osopen.open_external("file", text, workspace=ws, launcher=launched.append) != osopen.OK
        assert launched == []
    finally:
        os.rmdir(prefix + str(junction))
        shutil.rmtree(prefix + str(top), ignore_errors=True)


# ---------------------------------------------------------------------------
# INC9P-SEC-F3: a hard-linked attachment is refused at open time and `hard_linked` fails closed

@red("f3")
async def test_inc9q_sec_f3_opening_a_hard_linked_attachment_toasts_the_sentence_and_launches_nothing(
        tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    victim = tmp_path / "outside" / "victim.pdf"
    victim.parent.mkdir()
    victim.write_bytes(b"VICTIM")
    os.link(victim, ws / "docs" / "a.pdf")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        launcher, notes = await _activate(app, pilot, [Attachment(kind="file", path="docs/a.pdf", caption="c")])
        assert notes == [ATT_HARD], notes
        assert launcher.calls == []


@red("f3")
def test_inc9q_sec_f3_open_external_refuses_a_target_with_several_names(tmp_path):
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    (tmp_path / "other.pdf").write_bytes(b"1")
    os.link(tmp_path / "other.pdf", ws / "docs" / "a.pdf")
    (ws / "docs" / "b.pdf").write_bytes(b"1")
    launched: list[str] = []
    assert osopen.open_external("file", "docs/a.pdf", workspace=ws, launcher=launched.append) == ATT_HARD
    assert launched == []
    assert osopen.open_external("file", "docs/b.pdf", workspace=ws, launcher=launched.append) == osopen.OK
    assert len(launched) == 1 and launched[0].endswith("b.pdf"), launched


@red("f3")
@pytest.mark.parametrize("error,expected", [
    (FileNotFoundError("gone"), False), (PermissionError("denied"), True), (OSError("other"), True)])
def test_inc9q_sec_f3_hard_linked_returns_false_only_when_the_file_is_not_found(error, expected, tmp_path, monkeypatch):
    path = tmp_path / "a.pdf"
    path.write_bytes(b"1")

    def boom(self, *a, **kw):
        raise error

    monkeypatch.setattr(pathlib.Path, "lstat", boom)
    assert osopen.hard_linked(path) is expected


@red("f3")
def test_inc9q_sec_f3_open_external_fails_closed_when_the_link_count_cannot_be_read(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    (ws / "a.pdf").write_bytes(b"1")
    real = pathlib.Path.lstat

    def denied(self, *a, **kw):
        if self.name == "a.pdf":
            raise PermissionError("denied")
        return real(self, *a, **kw)

    monkeypatch.setattr(pathlib.Path, "lstat", denied)
    launched: list[str] = []
    assert osopen.open_external("file", "a.pdf", workspace=ws, launcher=launched.append) == ATT_HARD
    assert launched == []


# ---------------------------------------------------------------------------
# INC9P-SEC-F2: the parent is re-checked after `mkstemp`; the residual TOCTOU is narrowed, not closed

class _SwapAfterMkstemp:
    """After the real `mkstemp` and the factory's own `os.close` of its descriptor (a directory with an open file
    cannot be renamed on Windows), replace *folder* by a junction to *outside*, once."""

    def __init__(self, monkeypatch, folder: pathlib.Path, outside: pathlib.Path):
        self.swapped = False
        self.fd = None
        real_mkstemp, real_close = tempfile.mkstemp, os.close

        def mkstemp(*a, **kw):
            fd, name = real_mkstemp(*a, **kw)
            self.fd = fd
            return fd, name

        def close(fd):
            real_close(fd)
            if fd == self.fd and not self.swapped:
                self.swapped = True
                os.rename(folder, folder.with_name(folder.name + "-moved"))
                _link("junction", folder, outside)

        monkeypatch.setattr(tempfile, "mkstemp", mkstemp)
        monkeypatch.setattr(os, "close", close)


@red("f2")
async def test_inc9q_sec_f2_a_folder_swapped_for_a_junction_after_mkstemp_is_refused(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    (ws / "templates").mkdir(parents=True)
    src = tmp_path / "src" / "t.docx"
    _make_docx(src, "hola")
    outside = tmp_path / "outside"
    outside.mkdir()
    swap = _SwapAfterMkstemp(monkeypatch, ws / "templates", outside)
    replaced = _Replace(monkeypatch)
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        toasts = await _import(app, pilot, src)
    assert swap.swapped
    assert len(toasts) == 1 and toasts[0].startswith("could not import t.docx: "), toasts
    assert _tree(outside) == [], _tree(outside)
    assert replaced.calls == [], replaced.calls
    assert not (ws / "templates-moved" / "t.docx").exists()


async def test_inc9q_sec_f2_pin_a_workspace_that_is_itself_a_link_still_generates(tmp_path, monkeypatch):
    """The policy says the workspace ROOT may be a link; the re-check must not refuse every write under it."""
    _env(monkeypatch, tmp_path)
    real = tmp_path / "realws"
    _make_docx(real / "docs" / "t.docx", "hola")
    ws = tmp_path / "ws"
    _link("junction", ws, real)
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _, toasts = await _generate(app, pilot, _doc_graph("docs/t.docx"))
        assert toasts == ["generated: plantilla-root.docx"], toasts
    assert (real / "plantilla-root.docx").is_file()


# ---------------------------------------------------------------------------
# CR-F1: ONE reason -> sentence mapping (`osopen.refusal_sentence`), CR-F3: the import's unreadable sentence

@red("cr1")
@pytest.mark.parametrize("reason,expected", [
    ("link", W2), ("allow_list", U1), ("normalised", U1), ("outside", V1), ("unreadable", V1)])
def test_inc9q_cr_f1_refusal_sentence_maps_each_reason(reason, expected):
    assert osopen.refusal_sentence(reason) == expected
    assert osopen.refusal_sentence(reason, surface="attachment") == expected


@red("cr1")
def test_inc9q_cr_f3_only_the_import_surface_reads_unreadable_differently():
    assert osopen.refusal_sentence("unreadable", surface="import") == CR_F3
    for reason, expected in (("link", W2), ("allow_list", U1), ("normalised", U1), ("outside", V1)):
        assert osopen.refusal_sentence(reason, surface="import") == expected, reason


@red("cr1")
def test_inc9q_cr_f1_the_new_sentences_have_one_home():
    def strings(rel):
        tree = ast.parse((PKG / rel).read_text(encoding="utf-8"))
        return {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}

    home = strings("osopen.py")
    assert CR_F3 in home and ATT_HARD in home
    for rel in ("app.py", "screens/factory.py"):
        found = strings(rel)
        assert CR_F3 not in found and ATT_HARD not in found, rel


@red("cr1")
def test_inc9q_cr_f1_the_attachment_paths_use_the_shared_mapping(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "refusal_sentence", lambda reason, **kw: f"S:{reason}")
    ws = tmp_path / "ws"
    ws.mkdir()
    assert app_module._path_refusal("d /x.pdf", ws) == "S:normalised"
    assert app_module._path_refusal("..\\x.pdf", ws) == "S:outside"


@red("cr1")
async def test_inc9q_cr_f1_the_import_uses_the_shared_mapping_with_its_surface(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    monkeypatch.setattr(factory_module, "refusal_sentence", lambda reason, **kw: f"S:{reason}:{kw.get('surface')}")
    ws = tmp_path / "ws"
    ws.mkdir()
    src = tmp_path / "src" / "t.docx"
    _make_docx(src, "hola")
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "templates", tmp_path / "outside")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        toasts = await _import(app, pilot, src)
        assert toasts == ["S:link:import"], toasts


@red("cr1")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9q_cr_f3_an_unreadable_templates_folder_toasts_the_import_sentence(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    (ws / "templates").mkdir(parents=True)
    src = tmp_path / "src" / "t.docx"
    _make_docx(src, "hola")
    real = os.lstat

    def denied(path, *a, **kw):
        if os.path.basename(os.fspath(path)).lower() == "templates":
            raise PermissionError("denied")
        return real(path, *a, **kw)

    monkeypatch.setattr(os, "lstat", denied)
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        toasts = await _import(app, pilot, src)
        assert toasts == [CR_F3], toasts
    assert _ws_tree(ws) == ["templates"], _ws_tree(ws)


# ---------------------------------------------------------------------------
# X2: a refused template says U1; only a missing or unreadable one says "not found"

@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9q_x2_pin_an_unreadable_template_keeps_not_found(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "a.docx", "hola")
    real = os.lstat

    def denied(path, *a, **kw):
        if os.path.basename(os.fspath(path)).lower() == "docs":
            raise PermissionError("denied")
        return real(path, *a, **kw)

    monkeypatch.setattr(os, "lstat", denied)
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("docs/a.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert MISSING in _flat(screen) and U1 not in _flat(screen), _flat(screen)
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [MISSING], toasts


# ---------------------------------------------------------------------------
# CR-F2 (pin): `office.resolve` raising during generate leaves nothing behind

async def test_inc9q_cr_f2_pin_a_failing_office_resolve_toasts_the_type_and_leaves_no_temporary_file(
        tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")

    def boom(*a, **kw):
        raise RuntimeError("blocked: " + str(tmp_path))

    monkeypatch.setattr(office_module, "resolve", boom)
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        before = _ws_tree(ws)
        _, toasts = await _generate(app, pilot, _doc_graph("docs/t.docx"))
        assert toasts == ["could not generate: RuntimeError"], toasts
    assert _ws_tree(ws) == before == ["docs", "docs\\t.docx"], _ws_tree(ws)
    assert not [t for t in _tree(ws) if ".tmp-" in t]


# ---------------------------------------------------------------------------
# CR-F4: `lexically_outside` is gone (the table over `confine_reason` lives in test_inc9p)

@red("cr4")
def test_inc9q_cr_f4_lexically_outside_is_removed():
    assert not hasattr(osopen, "lexically_outside")


# ---------------------------------------------------------------------------
# CR-F5: the factory preview asks `confine_reason` once and passes the tuple through

@pytest.mark.parametrize("doc_path", [
    pytest.param("docs/missing.docx", marks=_red_mark("cr5")),
    pytest.param("d /a.docx", marks=_red_mark("cr5")),
    pytest.param("link/a.docx", marks=_red_mark("cr5")),
    "docs/a.docx",
])
async def test_inc9q_cr_f5_the_preview_asks_confine_reason_once(doc_path, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "a.docx", "hola")
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "link", tmp_path / "outside")
    calls: list[str] = []
    real = factory_module.confine_reason

    def counting(text, workspace):
        calls.append(text)
        return real(text, workspace)

    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph(doc_path), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        monkeypatch.setattr(factory_module, "confine_reason", counting)
        screen._preview()
        assert calls == [doc_path], calls


# ---------------------------------------------------------------------------
# CR-F7 (pin): step 1b runs before step 2, so `..\d \x.pdf` is `normalised`, not `outside`

def test_inc9q_cr_f7_pin_the_normalised_check_runs_before_the_lexical_one(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    assert osopen.confine_reason("..\\d \\x.pdf", ws) == (None, "normalised")
    assert osopen.confine_reason("..\\x.pdf", ws) == (None, "outside")


def test_inc9q_sec_f4_the_resolved_walked_prefix_is_the_last_check_for_a_missing_file(tmp_path, monkeypatch):
    """Counterpart of the sealed `test_inc9o_confine_judges_what_resolve_returns_as_a_last_check` for a file that
    does not exist: the walked prefix is what `resolve()` is asked about, and a prefix that resolves outside the
    workspace is refused."""
    ws = tmp_path / "ws"
    ws.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    real = pathlib.Path.resolve
    calls: list[str] = []

    def resolve(self, *a, **kw):
        calls.append(self.name)
        return elsewhere if len(calls) == 1 else real(self, *a, **kw)

    monkeypatch.setattr(pathlib.Path, "resolve", resolve)
    assert osopen.confine_reason("a.pdf", ws) == (None, "outside")
    assert calls[0] == "ws", calls
