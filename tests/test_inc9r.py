"""Inc-9r -- fixes for the Inc-9q reviews: the final-resolve backstop of `confine_reason` (INC9Q-CR-F1, HIGH),
the colon's own sentence (operator Y1), generate's refusal routed through `refusal_sentence` (CR-F2), the
MAX_PATH re-check with the `\\\\?\\` prefix (CR-F3) measured in UTF-16 units (SEC-F1), the factory preview's
hard-link sentence (SEC-F2), a single-letter junction form (CR-F4, in `test_inc9q`) and the folded step-4
`if tail / else` (CR-F6).

Authority: `A-126` and `VERDICT-inc9-2026-09-30.md` Round 14.  Every arm a fix closes was committed RED first as
a STRICT xfail keyed by the step that closes it (`OPEN_STEPS`); an arm that is not keyed is a pin (green on the
base), killed by a mutant instead.

Nothing here reaches the network, a real UNC, a console or COM device.  A link is only ever created to a LOCAL
directory under `tmp_path` (a junction, or a hard link between two temp files).  Astral characters are `\\U`
escapes; this file is ASCII.
"""
from __future__ import annotations

import os
import pathlib
import shutil
import sys
import tempfile

import pytest

from mapper import osopen
from mapper.app import MapperApp
from mapper.screens import factory as factory_module
from mapper.screens.factory import FactoryScreen
from mapper.store import MapStore
from tests.test_inc9f import NARROW, SIZE
from tests.test_inc9m import _env, _flat
from tests.test_inc9n import U1, _add_attachment, _make_docx, _toasts
from tests.test_inc9o import V1, W2, _doc_graph, _link, _tree
from tests.test_inc9p import _generate, _import, _Replace, _ws_tree
from tests.test_inc9q import _long_junction_tree

OPEN_STEPS: set[str] = {"backstop", "colon", "generate", "maxpath", "utf16", "preview"}

Y1 = 'path not supported: ":" is not allowed in a file name'
CR_F2 = "output path could not be checked: move the workspace to a shorter folder"
HARD_TEMPLATE = "template has several hard links: replace it with a plain copy"
PREFIX = chr(92) * 2 + "?" + chr(92)


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9r: committed RED; closed by the '{step}' step")
    return lambda fn: fn


def _red_mark(step: str):
    return ([pytest.mark.xfail(strict=True, reason=f"Inc-9r: committed RED; closed by the '{step}' step")]
            if step in OPEN_STEPS else [])


def _units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


# ---------------------------------------------------------------------------
# INC9Q-CR-F1 (HIGH): the final-resolve backstop.  The walk can be told "not found" about a link the OS follows.

def _lie_about(monkeypatch, name: str) -> None:
    real = os.lstat

    def lying(path, *a, **kw):
        if os.path.basename(os.fspath(path)).lower() == name:
            raise FileNotFoundError(2, "lie", os.fspath(path))
        return real(path, *a, **kw)

    monkeypatch.setattr(os, "lstat", lying)


@red("backstop")
async def test_inc9r_cr_f1_an_import_through_a_junction_that_lstat_hides_writes_nothing(tmp_path, monkeypatch):
    """The write side of the same defect: the `templates` junction points outside and `lstat` says it is not
    found.  Nothing may be created behind it: no temporary file, no replace, no file, and the link sentence."""
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    src = tmp_path / "src" / "t.docx"
    _make_docx(src, "hola")
    outside = tmp_path / "outside"
    outside.mkdir()
    _link("junction", ws / "templates", outside)
    made: list[str] = []
    real_mkstemp = tempfile.mkstemp

    def mkstemp(*a, **kw):
        made.append(str(kw.get("dir")))
        return real_mkstemp(*a, **kw)

    monkeypatch.setattr(tempfile, "mkstemp", mkstemp)
    replaced = _Replace(monkeypatch)
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _lie_about(monkeypatch, "templates")
        toasts = await _import(app, pilot, src)
    assert toasts == [W2], toasts
    assert made == [], made
    assert replaced.calls == [], replaced.calls
    assert _tree(outside) == [], _tree(outside)


@pytest.mark.parametrize("tail,expect", [
    ("x.pdf", "ok"), ("sub/new.pdf", "ok"), ("new.pdf", "ok")])
def test_inc9r_cr_f1_pin_ordinary_and_missing_tail_paths_still_work(tail, expect, tmp_path):
    """The comparison with what the consumer will reach must not refuse a plain path, an existing file or a
    missing tail under a real folder."""
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    (ws / "docs" / "x.pdf").write_bytes(b"1")
    got, why = osopen.confine_reason("docs/" + tail, ws)
    assert why == expect and got == ws.resolve() / "docs" / pathlib.Path(tail), (got, why)


def test_inc9r_cr_f1_pin_a_workspace_that_is_itself_a_link_is_not_a_link_reason(tmp_path):
    real = tmp_path / "realws"
    (real / "docs").mkdir(parents=True)
    ws = tmp_path / "ws"
    _link("junction", ws, real)
    got, why = osopen.confine_reason("docs/new.pdf", ws)
    assert why == "ok" and got == real.resolve() / "docs" / "new.pdf", (got, why)
    got, why = osopen.confine_reason("new.pdf", ws)
    assert why == "ok" and got == real.resolve() / "new.pdf", (got, why)


# ---------------------------------------------------------------------------
# Y1 (operator): a `:` in a file name has its own reason and its own sentence on every surface

@red("colon")
@pytest.mark.parametrize("surface", [None, "attachment", "import", "generate"])
def test_inc9r_y1_the_colon_reason_has_one_sentence_on_every_surface(surface):
    kw = {} if surface is None else {"surface": surface}
    assert osopen.refusal_sentence("colon", **kw) == Y1


@red("colon")
@pytest.mark.parametrize("text", ["notes: draft.pdf", "a:b/x.pdf", "docs/notes: draft.pdf", "lnk::$DATA"])
def test_inc9r_y1_a_colon_in_a_component_is_the_colon_reason(text, tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    assert osopen.confine_reason(text, ws) == (None, "colon")


@pytest.mark.parametrize("text", ["d /x.pdf", "...", "docs/d. ./x.pdf"])
def test_inc9r_y1_pin_the_other_normalised_cases_keep_u1(text, tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    assert osopen.confine_reason(text, ws) == (None, "normalised")
    assert osopen.refusal_sentence("normalised") == U1
    assert osopen.refusal_sentence("allow_list") == U1


def test_inc9r_y1_pin_a_drive_relative_single_letter_form_is_refused_by_the_allow_list(tmp_path):
    """`l:$I30` at the top level is a drive-relative path to pathlib, refused by `safe_local_path` before step
    1b.  The single-letter junction arm of `test_inc9q` therefore puts the junction one level down, where it is
    a component."""
    ws = tmp_path / "ws"
    ws.mkdir()
    assert osopen.confine_reason("l:$I30/x.pdf", ws) == (None, "allow_list")


@red("colon")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9r_y1_the_attachment_prompt_toasts_the_colon_sentence(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen, toasts = await _add_attachment(app, pilot, "notes: draft.pdf")
        assert toasts == [Y1], toasts
        assert screen.graph.nodes["nom"].ficha.attachments == []
        assert MapStore(ws).load("att").nodes["nom"].ficha.attachments == []


@red("colon")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9r_y1_a_template_with_a_colon_shows_the_colon_sentence_in_preview_and_generate(
        size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen, toasts = await _generate(app, pilot, _doc_graph("notes: draft.docx"))
        assert Y1 in _flat(screen) and U1 not in _flat(screen), _flat(screen)
        assert toasts == [Y1], toasts
    assert _ws_tree(ws) == ["docs", "docs\\t.docx"], _ws_tree(ws)


# ---------------------------------------------------------------------------
# INC9Q-CR-F2: generate's target refusal goes through `refusal_sentence` (surface "generate")

@pytest.mark.parametrize("reason,expected", [
    ("link", W2), ("normalised", U1), ("allow_list", U1),
    pytest.param("colon", Y1, marks=_red_mark("colon")),
    pytest.param("unreadable", CR_F2, marks=_red_mark("generate"))])
def test_inc9r_cr_f2_refusal_sentence_maps_each_generate_reason(reason, expected):
    assert osopen.refusal_sentence(reason, surface="generate") == expected


def test_inc9r_cr_f2_pin_only_the_generate_surface_reads_unreadable_as_the_output_path():
    for surface in (None, "attachment"):
        kw = {} if surface is None else {"surface": surface}
        assert osopen.refusal_sentence("unreadable", **kw) == V1
    assert osopen.refusal_sentence("unreadable", surface="import") != CR_F2


@red("generate")
async def test_inc9r_cr_f2_generate_uses_the_shared_mapping_with_its_surface(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    monkeypatch.setattr(factory_module, "refusal_sentence",
                        lambda reason, **kw: f"S:{reason}:{kw.get('surface')}")
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola")
    (tmp_path / "outside").mkdir()
    _link("junction", ws / "plantilla-root.docx", tmp_path / "outside")
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        _, toasts = await _generate(app, pilot, _doc_graph("docs/t.docx"))
        assert toasts == ["S:link:generate"], toasts


@red("generate")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9r_cr_f2_an_unreadable_297_character_target_says_the_output_path_could_not_be_checked(
        size, tmp_path, monkeypatch):
    """Not the document name: a long target whose `\\\\?\\` re-check fails is `unreadable`, and W1 would blame a
    name that is a perfectly good file name.  Only a `check_map_id` failure is W1 (pinned in `test_inc9o`)."""
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    # the output name is `<doc>-<node><suffix>`; pad the doc and node names to make the whole path 297 characters
    name_len = 297 - len(str(ws)) - 1
    assert 12 <= name_len <= 206, name_len
    both = name_len - len(".docx") - 1
    doc_len, node_len = both - both // 2, both // 2
    assert doc_len <= 100 and node_len <= 100, (doc_len, node_len)
    doc_name, node_id = "d" * doc_len, "n" * node_len
    _make_docx(ws / "docs" / "t.docx", "hola")
    real = os.lstat

    def denied(path, *a, **kw):
        if os.fspath(path).startswith(PREFIX):
            raise PermissionError("denied")
        return real(path, *a, **kw)

    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        before = _ws_tree(ws)
        monkeypatch.setattr(os, "lstat", denied)
        _, toasts = await _generate(app, pilot, _doc_graph("docs/t.docx", name=doc_name, node_id=node_id))
        assert len(str(ws / f"{doc_name}-{node_id}.docx")) == 297
        assert toasts == [CR_F2], toasts
        monkeypatch.setattr(os, "lstat", real)
    assert _ws_tree(ws) == before, _ws_tree(ws)


# ---------------------------------------------------------------------------
# INC9Q-CR-F3: a not-found at MAX_PATH is re-asked with the `\\?\` prefix instead of refused outright

def _name_of_units(ws: pathlib.Path, total: int) -> str:
    return "a" * (total - _units(str(ws)) - 1)


class _Lstat:
    """Records every `os.lstat` path and lets the real call through, or raises *error* for a `\\\\?\\` path."""

    def __init__(self, monkeypatch, error=None):
        self.seen: list[str] = []
        real = os.lstat

        def spy(path, *a, **kw):
            text = os.fspath(path)
            self.seen.append(text)
            if error is not None and text.startswith(PREFIX):
                raise error
            return real(path, *a, **kw)

        monkeypatch.setattr(os, "lstat", spy)

    @property
    def prefixed(self) -> list[str]:
        return [p for p in self.seen if p.startswith(PREFIX)]


@red("maxpath")
def test_inc9r_cr_f3_a_not_found_at_exactly_260_units_is_re_asked_with_the_prefix_and_continues(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    name = _name_of_units(ws, 260)
    assert _units(str(ws / name)) == 260
    spy = _Lstat(monkeypatch)
    got, why = osopen.confine_reason(name, ws)
    assert spy.prefixed == [PREFIX + str(ws / name)], spy.prefixed
    assert (got, why) == (ws.resolve() / name, "ok"), (got, why)


def test_inc9r_cr_f3_pin_a_not_found_at_259_units_is_a_plain_missing_tail(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    name = _name_of_units(ws, 259)
    assert _units(str(ws / name)) == 259
    spy = _Lstat(monkeypatch)
    got, why = osopen.confine_reason(name, ws)
    assert spy.prefixed == [], spy.prefixed
    assert (got, why) == (ws.resolve() / name, "ok"), (got, why)


@pytest.mark.parametrize("error", [PermissionError("denied"), OSError("other"), NotADirectoryError("nad")])
def test_inc9r_cr_f3_a_re_check_that_fails_for_another_reason_is_unreadable(error, tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    name = _name_of_units(ws, 260)
    _Lstat(monkeypatch, error)
    assert osopen.confine_reason(name, ws) == (None, "unreadable")


@red("maxpath")
@pytest.mark.parametrize("where", ["outside", "inside"])
def test_inc9r_cr_f3_a_junction_beyond_max_path_is_the_link_reason(where, tmp_path):
    """Made with the `\\\\?\\` prefix, so the process cannot see it without the same prefix.  Measured on the
    base: `unreadable` (Inc-9q), which is a refusal but the wrong cause; now the re-check finds the link."""
    ws = tmp_path / "ws"
    (ws / "real").mkdir(parents=True)
    target = tmp_path / "outside" if where == "outside" else ws / "real"
    target.mkdir(parents=True, exist_ok=True)
    (target / "x.pdf").write_bytes(b"1")
    top, junction = _long_junction_tree(ws, target)
    try:
        text = junction.relative_to(ws).as_posix() + "/x.pdf"
        assert _units(str(ws / text)) >= 340
        assert osopen.confine_reason(text, ws) == (None, "link")
        launched: list[str] = []
        assert osopen.open_external("file", text, workspace=ws, launcher=launched.append) != osopen.OK
        assert launched == []
    finally:
        os.rmdir(PREFIX + str(junction))
        shutil.rmtree(PREFIX + str(top), ignore_errors=True)


# ---------------------------------------------------------------------------
# INC9Q-SEC-F1: MAX_PATH is counted in UTF-16 units, not code points

@red("utf16")
@pytest.mark.parametrize("where", ["outside", "inside"])
def test_inc9r_sec_f1_an_astral_path_under_260_code_points_over_260_units_with_a_junction_is_the_link_reason(
        where, tmp_path):
    """Two astral folders (`\\U0001F600` is ONE code point and TWO UTF-16 units) and a junction `j` below them.
    The path to the second folder is under 260 code points and over 260 units, so `lstat` cannot see it: counted
    in code points the walk treated the not-found as a missing tail and never reached `j`."""
    if sys.platform != "win32":
        pytest.skip("junctions and MAX_PATH are Windows-only")
    import _winapi

    ws = tmp_path / "ws"
    (ws / "real").mkdir(parents=True)
    target = tmp_path / "outside" if where == "outside" else ws / "real"
    target.mkdir(parents=True, exist_ok=True)
    (target / "x.pdf").write_bytes(b"1")
    base = len(str(ws))
    n = -(-(260 - base - 2) // 4) + 2
    face = "\U0001F600"
    first, second = face * n, face * n
    second_path = ws / first / second
    assert len(str(second_path)) < 260 <= _units(str(second_path)), (len(str(second_path)), _units(str(second_path)))
    assert _units(str(ws / first)) < 260
    try:
        os.mkdir(PREFIX + str(ws / first))
        os.mkdir(PREFIX + str(second_path))
        _winapi.CreateJunction(str(target), PREFIX + str(second_path / "j"))
    except OSError:
        shutil.rmtree(PREFIX + str(ws / first), ignore_errors=True)
        pytest.skip("a long path could not be created here")
    try:
        text = pathlib.PurePath(first, second, "j", "x.pdf").as_posix()
        assert osopen.confine_reason(text, ws) == (None, "link")
        launched: list[str] = []
        assert osopen.open_external("file", text, workspace=ws, launcher=launched.append) != osopen.OK
        assert launched == []
    finally:
        os.rmdir(PREFIX + str(second_path / "j"))
        shutil.rmtree(PREFIX + str(ws / first), ignore_errors=True)


def test_inc9r_sec_f1_pin_the_units_of_the_test_helper_count_an_astral_character_twice():
    assert _units("\U0001F600") == 2 and len("\U0001F600") == 1 and _units("ab") == 2


# ---------------------------------------------------------------------------
# INC9Q-SEC-F2: the factory preview shows the X1 template sentence for a hard-linked template, as generate does

@red("preview")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9r_sec_f2_the_preview_of_a_hard_linked_template_shows_the_template_sentence(
        size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    victim = tmp_path / "outside" / "victim.docx"
    _make_docx(victim, "VICTIM")
    (ws / "docs").mkdir(parents=True)
    os.link(victim, ws / "docs" / "t.docx")
    app = MapperApp(ws)
    toasts = _toasts(app)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("docs/t.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert HARD_TEMPLATE in _flat(screen), _flat(screen)
        assert "VICTIM" not in _flat(screen)
        screen.action_generate_office()
        await pilot.pause()
        assert toasts == [HARD_TEMPLATE], toasts


@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9r_sec_f2_pin_the_preview_of_a_plain_template_still_shows_its_text(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    _make_docx(ws / "docs" / "t.docx", "hola mundo")
    app = MapperApp(ws)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        screen = FactoryScreen(_doc_graph("docs/t.docx"), process_name="demo")
        app.push_screen(screen)
        for _ in range(4):
            await pilot.pause()
        assert "hola mundo" in _flat(screen) and HARD_TEMPLATE not in _flat(screen), _flat(screen)
