"""Inc-9p -- fixes for the Inc-9o reviews: a path component that Windows normalises (INC9O-SEC-F1), hard links
(F2), invisible characters in generated names (F3), the corrected test spies (F4), `confine_reason` and the
two operator sentences W1 / W2, `lexically_outside` sharing `confine`'s step 2 (INC9O-CR-F1), the import into
`templates/` (CR-F2) and a `~`/`-` document name (CR-F5).

Authority: `A-124` and `VERDICT-inc9-2026-09-30.md` Rounds 11-12.  Every arm a fix closes was committed RED
first as a STRICT xfail keyed by the step that closes it (`OPEN_STEPS`); an arm that is not keyed is a pin
(green on the base), killed by a mutant instead.

Nothing here reaches the network, a real UNC, a console or COM device.  A link is only ever created to a LOCAL
directory under `tmp_path` (a junction or a symlink, or an `os.link` hard link between two temp files); the
spies refuse and record a filesystem call BEFORE the real one is made, and they patch
`ntpath._getfinalpathname` as well as `nt._getfinalpathname` (`INC9O-SEC-F4`: `realpath` binds it by name).
The sentences are literals here on purpose.  Control and bidi characters are `\\u` escapes; this file is ASCII.
"""
from __future__ import annotations

import os
import pathlib
import unicodedata

import pytest

from mapper import app as app_module
from mapper import osopen
from mapper.app import MapperApp
from mapper.model import Attachment
from mapper.screens.factory import FactoryScreen
from mapper.store import MapStore
from tests.test_inc9f import NARROW, SIZE
from tests.test_inc9m import _env, _flat, _no_fs, _office_graph, _open_prompt
from tests.test_inc9n import U1, _add_attachment, _make_docx, _toasts
from tests.test_inc9o import (
    V1, V2, W1_DOC, W1_NODE, W2, _activate, _doc_graph, _Forms, _link, _tree,
)

# Inc-9q: the arms whose expected sentence changed (X1, X2) were committed RED first, keyed by step.
OPEN_STEPS: set[str] = set()

PKG = pathlib.Path(osopen.__file__).parent

MISSING = "archivo de plantilla no encontrado"
# Inc-9q (X1, Round 13): one hard-link sentence per site; Inc-9p had a single, non-ruled sentence.
HARD_TEMPLATE = "template has several hard links: replace it with a plain copy"
HARD_OUTPUT = "output file has several hard links: delete or rename it"
HARD_IMPORT = "templates file has several hard links: delete or rename it"


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9p: committed RED; closed by the '{step}' step")
    return lambda fn: fn


def _red_mark(step: str):
    return ([pytest.mark.xfail(strict=True, reason=f"Inc-9p: committed RED; closed by the '{step}' step")]
            if step in OPEN_STEPS else [])


# ---------------------------------------------------------------------------
# INC9O-SEC-F1: a component Windows normalises ("...", ". .", "d ", "d. .") stops the walk early

NORMALISED = [".../lnk/x", ". ./lnk/x", "..  /lnk/x", "d /lnk/x", "d. ./lnk/x"]


@red("norm")
@pytest.mark.parametrize("kind", ["junction", "symlink"])
@pytest.mark.parametrize("text", NORMALISED)
def test_inc9p_sec_f1_a_normalised_component_is_refused_before_any_filesystem_call(
        kind, text, tmp_path, monkeypatch):
    """`resolve()` follows a link behind a component the walk could not see: refuse on the TEXT, with zero
    `os.stat`, `os.lstat`, `Path.resolve`, `nt._getfinalpathname` or `ntpath._getfinalpathname` call."""
    ws = tmp_path / "ws"
    ws.mkdir()
    out = tmp_path / "outside"
    out.mkdir()
    (out / "x").write_bytes(b"1")
    _link(kind, ws / "lnk", out)
    with _no_fs(monkeypatch) as hits:
        assert osopen.confine(text, ws) is None
    assert hits == [], hits


@pytest.mark.parametrize("text", ["d/x", "d.x/y", "./x", "..\\ws\\x"])
def test_inc9p_sec_f1_pin_plain_names_are_judged_as_before(text, tmp_path):
    """A dot inside a name, a leading `./` and a `..` that returns into the workspace are not 'normalised'."""
    ws = tmp_path / "ws"
    (ws / "d").mkdir(parents=True)
    (ws / "d.x").mkdir()
    got = osopen.confine(text, ws)
    assert got is not None and got.is_relative_to(ws.resolve()), got


@red("norm")
@pytest.mark.parametrize("text", ["a ", "a.", "a. .", " ", "..."])
def test_inc9p_sec_f1_an_edge_dot_or_space_in_any_component_is_refused(text, tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    with _no_fs(monkeypatch) as hits:
        assert osopen.confine("docs/" + text + "/f.pdf", ws) is None
        assert osopen.confine(text, ws) is None
    assert hits == [], hits


@red("x2")
@red("norm")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9p_sec_f1_the_factory_preview_never_touches_a_link_behind_a_normalised_part(
        size, tmp_path, monkeypatch):
    """Measured on the base: the factory preview, on render, followed the junction."""
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    _make_docx(tmp_path / "outside" / "a.docx", "SECRET-OUTSIDE")
    _link("junction", ws / "lnk", tmp_path / "outside")
    spy = _Forms(monkeypatch, ["lnk"])
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("d /lnk/a.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert "SECRET-OUTSIDE" not in _flat(screen) and U1 in _flat(screen), _flat(screen)
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [U1], toasts
    assert spy.hits == [], spy.hits


@red("norm")
@pytest.mark.parametrize("typed", [". ./lnk/x.pdf", "d /lnk/x.pdf"])
async def test_inc9p_sec_f1_adding_an_attachment_behind_a_normalised_part_toasts_u1_and_stores_nothing(
        typed, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "lnk", tmp_path / "outside")
    spy = _Forms(monkeypatch, ["lnk"])
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, typed)
        assert toasts == [U1], toasts
        assert screen.graph.nodes["nom"].ficha.attachments == []
    assert spy.hits == [], spy.hits


@red("norm")
async def test_inc9p_sec_f1_opening_an_attachment_behind_a_normalised_part_toasts_u1(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "x.pdf").write_bytes(b"x")
    _link("junction", ws / "lnk", tmp_path / "outside")
    spy = _Forms(monkeypatch, ["lnk"])
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        launcher, notes = await _activate(app, pilot, [Attachment(kind="file", path="d /lnk/x.pdf", caption="c")])
        assert notes == [U1], notes
        assert launcher.calls == []
    assert spy.hits == [], spy.hits


# ---------------------------------------------------------------------------
# W2 / `confine_reason`: why `confine` refused

def _reason(text, ws):
    return osopen.confine_reason(text, ws)


@red("reason")
def test_inc9p_confine_reason_names_the_cause_of_each_refusal(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "link", tmp_path / "outside")
    ok, why = _reason("docs/a.pdf", ws)
    assert ok is not None and why == "ok", (ok, why)
    assert _reason("\\\\h\\s\\x.pdf", ws) == (None, "allow_list")
    assert _reason("con", ws) == (None, "allow_list")
    assert _reason("-x.pdf", ws) == (None, "allow_list")
    assert _reason("..\\x.pdf", ws) == (None, "outside")
    assert _reason(str(tmp_path / "ws2" / "x.pdf"), ws) == (None, "outside")
    assert _reason("link/a.pdf", ws) == (None, "link")
    assert _reason("d /x.pdf", ws) == (None, "normalised")
    assert _reason("...", ws) == (None, "normalised")


@red("reason")
@pytest.mark.parametrize("error", [PermissionError("blocked"), OSError("blocked"), ValueError("blocked")])
def test_inc9p_confine_reason_says_unreadable_when_a_component_cannot_be_inspected(error, tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    (ws / "d").mkdir(parents=True)

    def denied(path, *a, **kw):
        raise error

    monkeypatch.setattr(os, "lstat", denied)
    assert _reason("d/a.pdf", ws) == (None, "unreadable")


@red("reason")
@pytest.mark.parametrize("error", [OSError("blocked"), ValueError("blocked")])
def test_inc9p_confine_reason_says_unreadable_when_the_final_resolve_fails(error, tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()

    def boom(self, *a, **kw):
        raise error

    monkeypatch.setattr(pathlib.Path, "resolve", boom)
    assert _reason("a.pdf", ws) == (None, "unreadable")


@red("reason")
def test_inc9p_confine_is_a_thin_wrapper_over_confine_reason(tmp_path):
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "link", tmp_path / "outside")
    for text in ("docs/a.pdf", "..\\x", "link/a.pdf", "d /x", "\\\\h\\s\\x", "", "docs\\..\\docs\\a.pdf"):
        assert osopen.confine(text, ws) == _reason(text, ws)[0], text


@pytest.mark.parametrize("text,expected", [
    ("docs/a.pdf", None),
    pytest.param("link/a.pdf", W2, marks=_red_mark("reason")),
    pytest.param("d /a.pdf", U1, marks=_red_mark("reason")),
    ("\\\\h\\s\\a.pdf", U1),
    ("con", U1),
    ("..\\a.pdf", V1),
    ("C:\\elsewhere\\a.pdf", V1),
])
def test_inc9p_the_attachment_sentence_follows_the_reason(text, expected, tmp_path):
    """`allow_list` and `normalised` -> U1; `outside` -> V1; `link` -> W2 (the one place both attachment
    paths ask)."""
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "link", tmp_path / "outside")
    assert app_module._path_refusal(text, ws) == expected


def test_inc9p_an_unreadable_component_reads_as_the_workspace_sentence_for_an_attachment(tmp_path, monkeypatch):
    """`INC9O-CR-F4`, declared: no cause the operator can act on is known, so it is V1 (the declared reading)."""
    ws = tmp_path / "ws"
    (ws / "d").mkdir(parents=True)

    def denied(path, *a, **kw):
        raise PermissionError("blocked")

    monkeypatch.setattr(os, "lstat", denied)
    assert app_module._path_refusal("d/a.pdf", ws) == V1


@red("w2")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9p_w2_adding_a_file_behind_a_link_toasts_the_link_sentence(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "link", tmp_path / "outside")
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, "link/x.pdf")
        assert toasts == [W2], toasts
        assert screen.graph.nodes["nom"].ficha.attachments == []
        assert MapStore(ws).load("att").nodes["nom"].ficha.attachments == []


@red("w2")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9p_w2_opening_a_file_behind_a_link_toasts_the_link_sentence(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "a.pdf").write_bytes(b"x")
    _link("junction", ws / "link", tmp_path / "outside")
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        launcher, notes = await _activate(app, pilot, [Attachment(kind="file", path="link/a.pdf", caption="c")])
        assert notes == [W2], notes
        assert launcher.calls == []


@red("w2")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9p_w2_the_factory_preview_and_generate_say_the_link_sentence(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    _make_docx(tmp_path / "outside" / "a.docx", "hola")
    _link("junction", ws / "link", tmp_path / "outside")
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("link/a.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert W2 in _flat(screen) and MISSING not in _flat(screen) and V2 not in _flat(screen), _flat(screen)
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [W2], toasts
    assert _tree(tmp_path / "outside") == ["a.docx"]


@pytest.mark.parametrize("doc_path,expected", [
    pytest.param("\\\\h\\s\\a.docx", U1, marks=_red_mark("x2")),
    pytest.param("con", U1, marks=_red_mark("x2")),
    pytest.param("d /a.docx", U1, marks=_red_mark("x2")),
    ("docs/missing.docx", MISSING),
])
async def test_inc9p_w2_pin_the_other_template_refusals_say_u1_or_not_found(doc_path, expected, tmp_path, monkeypatch):
    """Inc-9q (X2): a template the path rule refuses (allow-list, normalised) says U1; only a missing template
    keeps `archivo de plantilla no encontrado`.  (Inc-9p declared the old text for all of them.)"""
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    toasts = _toasts(app)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph(doc_path), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert expected in _flat(screen) and W2 not in _flat(screen), _flat(screen)
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [expected], toasts


@red("reason")
def test_inc9p_the_link_sentence_has_one_home_and_the_exact_text():
    import ast

    assert osopen.PATH_THROUGH_LINK == W2
    for rel in ("app.py", "screens/factory.py"):
        tree = ast.parse((PKG / rel).read_text(encoding="utf-8"))
        strings = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
        assert W2 not in strings, rel


# ---------------------------------------------------------------------------
# INC9O-CR-F1: `lexically_outside` is `confine`'s step 2, not a second rule

def _equivalence_cases(ws: pathlib.Path, o: pathlib.Path):
    return [
        ("the sibling ws2, relative", "..\\ws2\\x.pdf", True),
        ("the sibling ws2, absolute", str(o / "ws2" / "x.pdf"), True),
        ("an upper-cased path inside", str(ws).upper() + "\\docs\\a.pdf", False),
        ("dot-dot out", "..\\x.pdf", True),
        ("UNC", "\\\\h\\s\\x.pdf", False),
        ("a plain relative path", "docs/a.pdf", False),
        ("a name Windows normalises", "d /x.pdf", False),
    ]


@pytest.mark.parametrize("index", range(7))
def test_inc9p_confine_reason_outside_is_the_lexical_step(index, tmp_path):
    """Inc-9q (`INC9P-CR-F4`): `lexically_outside` is gone; its second assertion stays as a table over the one
    rule: a text is `outside` exactly when its lexical test says so, and a text refused earlier is not."""
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    (tmp_path / "ws2").mkdir()
    label, text, expected = _equivalence_cases(ws, tmp_path)[index]
    assert (osopen.confine_reason(text, ws)[1] == "outside") is expected, label


# ---------------------------------------------------------------------------
# INC9O-SEC-F2: hard links.  Generate writes a sibling and `os.replace`s it; a hard-linked target or template
# is refused.

def _ws_tree(ws: pathlib.Path) -> list[str]:
    """The workspace's files, without the app's own `.mapper` folder."""
    return [t for t in _tree(ws) if not t.startswith(".mapper")]


class _Replace:
    def __init__(self, monkeypatch):
        self.calls: list[tuple[str, str]] = []
        real = os.replace

        def replace(src, dst, *a, **kw):
            self.calls.append((os.fspath(src), os.fspath(dst)))
            return real(src, dst, *a, **kw)

        monkeypatch.setattr(os, "replace", replace)


async def _generate(app, pilot, graph):
    toasts = _toasts(app)
    screen = FactoryScreen(graph, process_name="demo")
    app.push_screen(screen)
    for _ in range(4):
        await pilot.pause()
    screen.action_generate_office()
    await pilot.pause()
    return screen, toasts


@red("x1")
@red("hard")
async def test_inc9p_sec_f2_a_hard_linked_target_is_refused_and_the_victim_is_untouched(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")
    victim = tmp_path / "outside" / "victim.docx"
    _make_docx(victim, "VICTIM")
    before = victim.read_bytes()
    os.link(victim, ws / "plantilla-root.docx")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _, toasts = await _generate(app, pilot, _doc_graph("docs/t.docx"))
        assert toasts == [HARD_OUTPUT], toasts
    assert victim.read_bytes() == before
    assert (ws / "plantilla-root.docx").read_bytes() == before


@red("x1")
@red("hard")
async def test_inc9p_sec_f2_a_hard_linked_template_is_refused_and_nothing_is_written(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    original = tmp_path / "outside" / "orig.docx"
    _make_docx(original, "hola")
    (ws / "docs").mkdir(parents=True)
    os.link(original, ws / "docs" / "t.docx")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _, toasts = await _generate(app, pilot, _doc_graph("docs/t.docx"))
        assert toasts == [HARD_TEMPLATE], toasts
    assert not (ws / "plantilla-root.docx").exists()


@red("hard")
async def test_inc9p_sec_f2_generate_writes_a_sibling_and_replaces_it_onto_the_target(tmp_path, monkeypatch):
    """The write that cannot go through a hard link: a temporary file in the SAME directory, then replace."""
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola {{nombre}}")
    (ws / "plantilla-root.docx").write_bytes(b"OLD")
    spy = _Replace(monkeypatch)
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _, toasts = await _generate(app, pilot, _doc_graph("docs/t.docx"))
        assert toasts == ["generado: plantilla-root.docx"], toasts
    assert len(spy.calls) == 1, spy.calls
    src, dst = spy.calls[0]
    assert pathlib.Path(dst).name == "plantilla-root.docx" and src != dst
    assert pathlib.Path(src).parent == pathlib.Path(dst).parent
    assert (ws / "plantilla-root.docx").read_bytes() != b"OLD"
    assert _ws_tree(ws) == ["docs", "docs\\t.docx", "plantilla-root.docx"], _ws_tree(ws)


@red("hard")
async def test_inc9p_sec_f2_a_failed_generate_leaves_no_temporary_file(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")

    def boom(*a, **kw):
        raise OSError("blocked")

    monkeypatch.setattr(os, "replace", boom)
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _, toasts = await _generate(app, pilot, _doc_graph("docs/t.docx"))
        assert toasts == ["no se pudo generar: OSError"], toasts
    assert _ws_tree(ws) == ["docs", "docs\\t.docx"], _ws_tree(ws)


# ---------------------------------------------------------------------------
# INC9O-SEC-F3: invisible characters in a generated name (Cf, Zl, Zp, Co)

INVISIBLE = [("U+202E", "a\u202eb"), ("U+200B", "a\u200bb"), ("U+2028", "a\u2028b"),
             ("U+2029", "a\u2029b"), ("U+E000", "a\ue000b"), ("U+FEFF", "a\ufeffb")]


def test_inc9p_the_invisible_characters_belong_to_the_four_categories():
    assert {unicodedata.category(c[1][1]) for c in INVISIBLE} == {"Cf", "Zl", "Zp", "Co"}


@red("unicode")
@pytest.mark.parametrize("label,name", INVISIBLE, ids=[i[0] for i in INVISIBLE])
async def test_inc9p_sec_f3_an_invisible_character_in_the_document_name_writes_nothing(
        label, name, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        before = _tree(tmp_path)
        screen = FactoryScreen(_doc_graph("docs/t.docx", name=name), process_name="demo", document_name=name)
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [W1_DOC], toasts
        assert _tree(tmp_path) == before


@red("unicode")
@pytest.mark.parametrize("label,node_id", INVISIBLE, ids=[i[0] for i in INVISIBLE])
async def test_inc9p_sec_f3_an_invisible_character_in_the_node_id_writes_nothing(
        label, node_id, tmp_path, monkeypatch):
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


async def test_inc9p_sec_f3_pin_an_accented_name_still_generates(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")
    name = "informe-\u00f1and\u00fa"
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("docs/t.docx", name=name), process_name="demo", document_name=name)
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [f"generado: {name}-root.docx"], toasts
    assert (ws / f"{name}-root.docx").is_file()


# ---------------------------------------------------------------------------
# INC9O-CR-F2: `action_import_office` writes into `templates/` through `confine` and a sibling + replace

async def _import(app, pilot, source):
    app.push_screen(FactoryScreen(_office_graph(), process_name="demo"))
    await pilot.pause()
    return await _open_prompt(app, pilot, "i", str(source))


@red("import")
async def test_inc9p_cr_f2_importing_through_a_templates_junction_writes_nothing_through_it(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
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
        assert toasts == [W2], toasts
    assert _tree(tmp_path / "outside") == []


@red("x1")
@red("import")
async def test_inc9p_cr_f2_importing_over_a_hard_linked_template_leaves_the_victim_untouched(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    (ws / "templates").mkdir(parents=True)
    src = tmp_path / "src" / "t.docx"
    _make_docx(src, "hola")
    victim = tmp_path / "outside" / "victim.docx"
    _make_docx(victim, "VICTIM")
    before = victim.read_bytes()
    os.link(victim, ws / "templates" / "t.docx")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        toasts = await _import(app, pilot, src)
        assert toasts == [HARD_IMPORT], toasts
    assert victim.read_bytes() == before


async def test_inc9p_cr_f2_pin_a_plain_import_copies_into_templates(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    src = tmp_path / "src" / "t.docx"
    _make_docx(src, "hola")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        toasts = await _import(app, pilot, src)
        assert "plantilla importada: templates/t.docx" in toasts, toasts
    assert (ws / "templates" / "t.docx").read_bytes() == src.read_bytes()
    assert _ws_tree(ws) == ["templates", "templates\\t.docx"], _ws_tree(ws)


@red("import")
async def test_inc9p_cr_f2_the_import_writes_a_sibling_and_replaces_it(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    src = tmp_path / "src" / "t.docx"
    _make_docx(src, "hola")
    spy = _Replace(monkeypatch)
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _import(app, pilot, src)
    assert len(spy.calls) == 1, spy.calls
    tmp_name, dst = spy.calls[0]
    assert pathlib.Path(dst).name == "t.docx" and tmp_name != dst
    assert pathlib.Path(tmp_name).parent == pathlib.Path(dst).parent


# ---------------------------------------------------------------------------
# INC9O-CR-F5: a document name starting with `~` or `-` is a plain relative name

@red("tilde")
@pytest.mark.parametrize("name", ["~draft", "-draft"])
async def test_inc9p_cr_f5_a_name_starting_with_a_tilde_or_dash_generates_inside_the_workspace(
        name, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("docs/t.docx", name=name), process_name="demo", document_name=name)
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [f"generado: {name}-root.docx"], toasts
    assert (ws / f"{name}-root.docx").is_file()


@red("tilde")
def test_inc9p_cr_f5_a_dot_slash_prefix_makes_a_tilde_name_literal(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    _env(monkeypatch, tmp_path / "elsewhere")
    got = osopen.confine("./~x.pdf", ws)
    assert got is not None and got.name == "~x.pdf" and got.is_relative_to(ws.resolve()), got
    got = osopen.confine(".\\~x.pdf", ws)
    assert got is not None and got.name == "~x.pdf", got


def test_inc9p_cr_f5_pin_a_bare_tilde_path_still_expands(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    _env(monkeypatch, ws)
    got = osopen.confine("~/a.pdf", ws)
    assert got is not None and got.is_relative_to(ws.resolve()), got
    _env(monkeypatch, tmp_path)
    assert osopen.confine("~/a.pdf", ws) is None
