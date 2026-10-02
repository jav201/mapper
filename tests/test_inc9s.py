r"""Inc-9s -- INC9R-SEC-F3 (LOW, a regression of `929a039`): a lone surrogate in a typed path made `confine_reason`
and `open_external` raise `UnicodeEncodeError` (`_utf16_units` encoded it inside the `FileNotFoundError` handler),
and INC9R-CR-F3: the Y1 sentence on an import SOURCE that is an NTFS stream.

Authority: `A-127`.  The arms keyed by `OPEN_STEPS` were committed RED first as STRICT xfail; the others are pins
(green on the base) killed by a mutant instead.

Nothing here reaches the network, a real UNC, a console or a device.  The stream file is created under `tmp_path`.
Surrogates are `\ud800` / `\udc80` escapes and the astral character is a `\U` escape; this file is ASCII.
"""
from __future__ import annotations

import pytest

from mapper import osopen
from mapper.app import MapperApp
from tests.test_inc9f import SIZE
from tests.test_inc9m import _env, _no_fs
from tests.test_inc9n import _make_docx
from tests.test_inc9o import _tree
from tests.test_inc9p import _import

OPEN_STEPS: set[str] = set()

Y1 = 'path not supported: ":" is not allowed in a file name'


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(
            strict=True, reason=f"Inc-9s: committed RED; closed by the '{step}' step")
    return lambda fn: fn


LONE = [
    "\ud800/x.pdf",
    "docs/\udc80.pdf",
    "docs/a\udbffb.pdf",
    "\udfff",
    "docs/" + "\ud83d" + "\ude00" + ".pdf",
]


@red("surrogate")
@pytest.mark.parametrize("text", LONE)
def test_inc9s_sec_f3_a_lone_surrogate_is_refused_by_the_allow_list_with_no_filesystem_call(text, tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    with _no_fs(monkeypatch) as hits:
        assert osopen.safe_local_path(text) is None
        assert osopen.confine_reason(text, ws) == (None, "allow_list")
        assert osopen.confine(text, ws) is None
    assert hits == [], hits


@red("surrogate")
@pytest.mark.parametrize("text", LONE)
def test_inc9s_sec_f3_open_external_refuses_a_lone_surrogate_and_does_not_raise(text, tmp_path):
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    launched: list[str] = []
    status = osopen.open_external("file", text, workspace=ws, launcher=launched.append)
    assert status == osopen.REFUSED_TYPE, status
    assert launched == []


@red("surrogate")
def test_inc9s_sec_f3_the_unit_count_is_a_second_guard_and_does_not_raise_on_a_lone_surrogate():
    assert osopen._utf16_units("\ud800") == 1
    assert osopen._utf16_units("a\udc80b") == 3


def test_inc9s_sec_f3_pin_an_astral_character_counts_as_two_units_and_is_accepted(tmp_path):
    ws = tmp_path / "ws"
    (ws / "docs").mkdir(parents=True)
    target = ws / "docs" / "\U0001F600.pdf"
    target.write_bytes(b"1")
    assert osopen._utf16_units("\U0001F600") == 2
    assert osopen._utf16_units("a\U0001F600") == 3
    got, why = osopen.confine_reason("docs/\U0001F600.pdf", ws)
    assert (got, why) == (ws.resolve() / "docs" / "\U0001F600.pdf", "ok"), (got, why)
    launched: list[str] = []
    status = osopen.open_external("file", "docs/\U0001F600.pdf", workspace=ws, launcher=launched.append)
    assert status == osopen.OK and launched == [str(got)], (status, launched)


# ---------------------------------------------------------------------------
# INC9R-CR-F3: an NTFS stream CAN be an import source; its name carries a colon, so the target is Y1.

async def test_inc9s_cr_f3_importing_a_stream_source_toasts_y1_and_writes_nothing_under_templates(tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    ws = tmp_path / "ws"
    ws.mkdir()
    srcdir = tmp_path / "src"
    srcdir.mkdir()
    stream = str(srcdir) + chr(92) + "ab:b.docx"
    _make_docx(srcdir / "plain.docx", "hola")
    with open(stream, "wb") as fh:
        fh.write((srcdir / "plain.docx").read_bytes())
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        toasts = await _import(app, pilot, stream)
    assert toasts == [Y1], toasts
    assert _tree(ws / "templates") == [], _tree(ws / "templates")
