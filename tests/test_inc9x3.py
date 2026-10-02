"""Inc-9 X3 -- an attachment chip opens with REAL input (INC9P-UX-F1).

Authority: `A-128` and `VERDICT-inc9-2026-09-30.md` Round 13, X3.  The defect: `FichaInspector.on_ds_chip_changed`
read `event.control`, and Textual's `Message.control` is `None` for a message that does not define it, so the
handler returned silently: `enter`, `space` and a click on a chip did nothing.  Every earlier arm posted
`FichaInspector.AttachmentActivated` by hand, which skipped exactly the hop that was broken.

Every arm here uses real keys (`tab`, `enter`, `space`, `I`) or a real click through Pilot; none posts the
message.  The OS launcher is a recording stub in every arm, so no file or URL is ever opened.  At 87 columns the
inspector is hidden until `I` is pressed, so that key is pressed first (declared, not a shortcut).

Arms keyed by `OPEN_STEPS` were committed RED first as STRICT xfail.
"""
from __future__ import annotations

import pytest

from mapper.app import MapperApp
from mapper.model import Attachment
from tests.test_attachments import RecordingLauncher, _open, _seed
from tests.test_inc9f import NARROW, SIZE
from tests.test_inc9m import _env

OPEN_STEPS: set[str] = {"chip"}

V1 = "attachment must be inside the workspace: use a relative path"
URL = "https://example.com/acta"
OUTSIDE = "C:" + chr(92) + "outside" + chr(92) + "x.pdf"


def red(step: str):
    if step in OPEN_STEPS:
        return pytest.mark.xfail(strict=True, reason=f"Inc-9 X3: committed RED; closed by the '{step}' step")
    return lambda fn: fn


async def _focus_chip(app, pilot, index, size):
    """Real keys only: `I` first when the inspector is hidden (87), then `tab` until the chip holds focus."""
    if size == NARROW:
        await pilot.press("I")
        await pilot.pause()
    want = f"insp-att-{index}"
    for _ in range(12):
        if getattr(app.focused, "id", None) == want:
            return
        await pilot.press("tab")
        await pilot.pause()
    raise AssertionError(f"tab never reached {want}: focus is {getattr(app.focused, 'id', None)}")


def _strip(screen):
    content = screen.query_one("#map-toast").content
    return getattr(content, "plain", str(content))


async def _setup(app, pilot, attachments, tmp_path):
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "x.pdf").write_bytes(b"%PDF-1.4\n")
    await pilot.pause()
    return await _open(app, pilot, _seed(app, attachments))


FILE_AND_URL = [
    Attachment(kind="file", path="docs/x.pdf", caption="plan"),
    Attachment(kind="url", path=URL, caption="acta"),
]


@red("chip")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("key", ["enter", "space"])
async def test_inc9x3_a_key_on_a_file_chip_opens_the_resolved_inside_path(key, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    launcher = RecordingLauncher()
    app.attachment_launcher = launcher
    async with app.run_test(size=size) as pilot:
        screen = await _setup(app, pilot, FILE_AND_URL, tmp_path)
        await _focus_chip(app, pilot, 0, size)
        await pilot.press(key)
        for _ in range(3):
            await pilot.pause()
        assert launcher.calls == [str((tmp_path / "docs" / "x.pdf").resolve())], launcher.calls
        assert "abierto" in _strip(screen) and "plan" in _strip(screen), _strip(screen)


@red("chip")
@pytest.mark.parametrize("size", [SIZE, NARROW])
async def test_inc9x3_a_click_on_a_file_chip_opens_the_resolved_inside_path(size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    launcher = RecordingLauncher()
    app.attachment_launcher = launcher
    async with app.run_test(size=size) as pilot:
        screen = await _setup(app, pilot, FILE_AND_URL, tmp_path)
        if size == NARROW:
            await pilot.press("I")
            await pilot.pause()
        await pilot.click("#insp-att-0")
        for _ in range(3):
            await pilot.pause()
        assert launcher.calls == [str((tmp_path / "docs" / "x.pdf").resolve())], launcher.calls
        assert "abierto" in _strip(screen), _strip(screen)


@red("chip")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("key", ["enter", "space"])
async def test_inc9x3_a_key_on_a_url_chip_reaches_the_url_launcher(key, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    launcher = RecordingLauncher()
    app.attachment_launcher = launcher
    async with app.run_test(size=size) as pilot:
        screen = await _setup(app, pilot, FILE_AND_URL, tmp_path)
        await _focus_chip(app, pilot, 1, size)
        await pilot.press(key)
        for _ in range(3):
            await pilot.pause()
        assert launcher.calls == [URL], launcher.calls
        assert "abierto" in _strip(screen), _strip(screen)


@red("chip")
@pytest.mark.parametrize("size", [SIZE, NARROW])
@pytest.mark.parametrize("how", ["enter", "click"])
async def test_inc9x3_a_refused_outside_path_toasts_v1_through_real_input_and_never_launches(
        how, size, tmp_path, monkeypatch):
    _env(monkeypatch, tmp_path)
    app = MapperApp(tmp_path)
    launcher = RecordingLauncher()
    app.attachment_launcher = launcher
    notes: list[str] = []
    async with app.run_test(size=size) as pilot:
        screen = await _setup(app, pilot, [Attachment(kind="file", path=OUTSIDE, caption="c")], tmp_path)
        screen.notify = lambda msg, **kw: notes.append(str(msg))
        if how == "enter":
            await _focus_chip(app, pilot, 0, size)
            await pilot.press("enter")
        else:
            if size == NARROW:
                await pilot.press("I")
                await pilot.pause()
            await pilot.click("#insp-att-0")
        for _ in range(3):
            await pilot.pause()
        assert notes == [V1], notes
        assert launcher.calls == [], launcher.calls
