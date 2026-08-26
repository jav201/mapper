"""Acceptance tests for attachments and the OS-handler boundary (US-N02).

The launcher is injected everywhere, so nothing is ever actually launched by the
suite.  The refusal cases below are not hypothetical: before the confinement rule
existed, a `..` traversal target, `calc.exe` and `powershell.exe` all really
launched on this machine.
"""
from __future__ import annotations

import pytest

from mapper import osopen
from mapper.app import MapperApp, MapScreen
from mapper.model import Attachment, Edge, Ficha, Graph, Node, SchemaField
from mapper.widgets.inspector import FichaInspector


class RecordingLauncher:
    """Captures what would have been launched, and launches nothing."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, target: str) -> None:
        self.calls.append(target)


# ---------------------------------------------------------------------------
# The boundary itself
# ---------------------------------------------------------------------------


def test_llr_n02_7_file_outside_the_workspace_is_refused(tmp_path):
    """A traversal target is refused BEFORE the launcher is reached.

    RED mutation: drop the `is_relative_to` check; `calls` becomes non-empty.
    """
    ws = tmp_path / "maps"
    ws.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("x", encoding="utf-8")

    launcher = RecordingLauncher()
    status = osopen.open_external(
        "file", "../secret.txt", workspace=ws, launcher=launcher
    )
    assert status == osopen.REFUSED_OUTSIDE
    assert launcher.calls == [], "a target outside the workspace reached the launcher"


def test_llr_n02_7_existence_is_not_an_authorisation(tmp_path):
    """Confinement is checked whether or not the target exists.

    Existence answers "will this fail?", not "should this open?".  A check ordered
    the other way round would let an existing outside file through.

    RED mutation: return early when the path does not exist, before the
    containment test; the absent-outside case then reports the wrong status.
    """
    ws = tmp_path / "maps"
    ws.mkdir()
    launcher = RecordingLauncher()

    absent_outside = osopen.open_external(
        "file", "../does-not-exist.txt", workspace=ws, launcher=launcher
    )
    assert absent_outside == osopen.REFUSED_OUTSIDE, (
        "a non-existent outside path must be refused for being OUTSIDE, "
        "not merely for being absent"
    )
    assert launcher.calls == []


@pytest.mark.parametrize(
    "target",
    [
        "file:///etc/passwd",
        "javascript:alert(1)",
        "data:text/html,<script>x</script>",
        "ftp://example.com/x",
        "example.com/no-scheme",
    ],
)
def test_llr_n02_5_only_http_and_https_urls_open(tmp_path, target):
    """One arm per refused scheme, each driven off a NON-default value (C-10).

    `file:` is in this list deliberately: allowing it would give the url branch an
    unconfined path and route around the workspace check entirely.

    RED mutation: widen ALLOWED_SCHEMES to include the scheme under test; that arm
    goes green while the others still fail — which is why there is one arm each.
    """
    launcher = RecordingLauncher()
    status = osopen.open_external("url", target, workspace=tmp_path, launcher=launcher)
    assert status == osopen.REFUSED_SCHEME
    assert launcher.calls == []


def test_an_allowed_url_does_reach_the_launcher(tmp_path):
    """The positive control.

    Without it, a module that refused EVERYTHING would pass every test above.
    """
    launcher = RecordingLauncher()
    status = osopen.open_external(
        "url", "https://example.com/acta", workspace=tmp_path, launcher=launcher
    )
    assert status == osopen.OK
    assert launcher.calls == ["https://example.com/acta"]


def test_a_confined_file_does_reach_the_launcher(tmp_path):
    """The positive control for the file branch."""
    ws = tmp_path / "maps"
    ws.mkdir()
    (ws / "acta.pdf").write_text("x", encoding="utf-8")
    launcher = RecordingLauncher()
    status = osopen.open_external("file", "acta.pdf", workspace=ws, launcher=launcher)
    assert status == osopen.OK
    assert launcher.calls and launcher.calls[0].endswith("acta.pdf")


@pytest.mark.parametrize("target", [12345, None, "", "   ", ["a"], {"k": "v"}])
def test_llr_n02_8_non_string_targets_are_refused_without_raising(tmp_path, target):
    """A sidecar is YAML: `path: 12345` parses to an int and `path:` to None.

    Neither may reach a launcher, and — this is the half that bit — neither may
    RAISE out of a function contracted to return a status word.

    RED mutation: remove the isinstance guard; the int and list arms raise.
    """
    launcher = RecordingLauncher()
    status = osopen.open_external("file", target, workspace=tmp_path, launcher=launcher)
    assert status in (osopen.REFUSED_TYPE, osopen.REFUSED_OUTSIDE, osopen.REFUSED_ERROR)
    assert launcher.calls == []


def test_unopenable_kinds_are_refused(tmp_path):
    launcher = RecordingLauncher()
    assert osopen.open_external(
        "image", "x.png", workspace=tmp_path, launcher=launcher
    ) == osopen.REFUSED_KIND
    assert launcher.calls == []


def test_osopen_imports_nothing_from_mapper():
    """The dependency ban that keeps the audit surface one file.

    Derived from the module's own AST, not from a hand-listed expectation.
    """
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path(osopen.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert imported, "the AST walk found no imports at all — the probe is broken"
    assert not any(name.startswith("mapper") for name in imported), imported


def test_osopen_never_uses_a_shell():
    import pathlib

    source = pathlib.Path(osopen.__file__).read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "os.system" not in source


# ---------------------------------------------------------------------------
# Through the shipped surface
# ---------------------------------------------------------------------------

SCHEMA = [SchemaField(key="D", label="documento", required=True)]


def _seed(app, attachments=None):
    g = Graph()
    g.schema = list(SCHEMA)
    g.add_node(Node(id="root", ficha=Ficha(title="erp")))
    g.add_node(
        Node(
            id="nom",
            ficha=Ficha(title="nómina", fields={"D": "a"},
                        attachments=list(attachments or [])),
        )
    )
    g.add_edge(Edge("root", "nom"))
    app.store.save("att", g)
    return "att"


async def _open(app, pilot, map_id):
    app.push_screen(MapScreen(map_id))
    await pilot.pause()
    await pilot.pause()
    screen = app.screen
    screen.nav.cursor = "nom"
    screen.refresh_canvas()
    await pilot.pause()
    return screen


async def test_at_n02a_adding_an_attachment_persists(tmp_path):
    """AT-N02a — add through the inspector, observe it via a FRESH MapStore (C-12).

    RED mutation: drop the `store.save` from the add handler; the reload fails.
    """
    from mapper.store import MapStore

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        screen = await _open(app, pilot, _seed(app))
        screen.query_one("#map-inspector", FichaInspector).request_add_attachment()
        await pilot.pause()
        prompt = app.screen
        prompt.query_one("#prompt-input").value = "https://example.com/acta"
        await pilot.press("enter")
        await pilot.pause()

        reloaded = MapStore(tmp_path).load("att")
        atts = reloaded.nodes["nom"].ficha.attachments
        assert [(a.kind, a.path) for a in atts] == [("url", "https://example.com/acta")]


async def test_at_n02c_removing_deletes_exactly_that_one(tmp_path):
    """AT-N02c — the discriminating negative: the OTHER attachments survive.

    A test that only checked "one fewer" would pass against code that removes the
    wrong element.  This pins the surviving list, in order.

    RED mutation: `attachments.pop()` with no index; the wrong element goes.
    """
    from mapper.store import MapStore

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        seeded = [
            Attachment(kind="url", path="https://a.example/1", caption="uno"),
            Attachment(kind="url", path="https://b.example/2", caption="dos"),
            Attachment(kind="url", path="https://c.example/3", caption="tres"),
        ]
        screen = await _open(app, pilot, _seed(app, seeded))
        inspector = screen.query_one("#map-inspector", FichaInspector)

        inspector.post_message(
            FichaInspector.AttachmentRemoveRequested("nom", 1)
        )
        await pilot.pause()

        reloaded = MapStore(tmp_path).load("att")
        remaining = [a.path for a in reloaded.nodes["nom"].ficha.attachments]
        assert remaining == ["https://a.example/1", "https://c.example/3"]


async def test_at_n02b_activating_an_attachment_reaches_the_boundary(tmp_path):
    """AT-N02b — the chain inspector -> screen -> osopen -> launcher, with the
    launcher injected so nothing is really opened.

    NOTE: this does NOT sign off the final hop to the operating system. That hop
    is MAN-01, verified by inspection; a green result here is not evidence that
    the OS opened anything.

    RED mutation: have the screen ignore the AttachmentActivated message; `calls`
    stays empty.
    """
    app = MapperApp(tmp_path)
    launcher = RecordingLauncher()
    app.attachment_launcher = launcher
    async with app.run_test() as pilot:
        await pilot.pause()
        seeded = [Attachment(kind="url", path="https://example.com/acta", caption="acta")]
        screen = await _open(app, pilot, _seed(app, seeded))
        inspector = screen.query_one("#map-inspector", FichaInspector)

        inspector.post_message(FichaInspector.AttachmentActivated("nom", 0))
        await pilot.pause()
        assert launcher.calls == ["https://example.com/acta"]


async def test_at_n02d_a_refused_attachment_is_reported_not_silently_dropped(tmp_path):
    """AT-N02d — a refusal must be visible; a dropped status word is a silent no-op.

    RED mutation: ignore `open_external`'s return value; no notification appears.
    """
    app = MapperApp(tmp_path)
    launcher = RecordingLauncher()
    app.attachment_launcher = launcher
    notes: list[str] = []
    async with app.run_test() as pilot:
        await pilot.pause()
        seeded = [Attachment(kind="file", path="../../etc/passwd", caption="inocente")]
        screen = await _open(app, pilot, _seed(app, seeded))
        screen.notify = lambda msg, **kw: notes.append(str(msg))
        inspector = screen.query_one("#map-inspector", FichaInspector)

        inspector.post_message(FichaInspector.AttachmentActivated("nom", 0))
        await pilot.pause()

        assert launcher.calls == [], "a traversal target reached the launcher"
        assert notes, "the refusal was silent"
        assert osopen.REFUSED_OUTSIDE in notes[0]


async def test_llr_n02_10_the_inspector_shows_the_real_target(tmp_path):
    """A friendly caption must not be the only thing shown for a hostile target."""
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        seeded = [Attachment(kind="url", path="https://evil.example/x", caption="acta oficial")]
        screen = await _open(app, pilot, _seed(app, seeded))
        inspector = screen.query_one("#map-inspector", FichaInspector)
        shown = " ".join(
            s.render().plain for s in inspector.query(".insp-att-target")
        )
        assert "evil.example" in shown, "the inspector showed only the caption"


def test_llr_n06_3_dschip_focused_and_selected_are_distinguishable():
    """LLR-N06.3 — they used to render byte-identically.

    One `if focused or selected` branch painted both the same, so "which chip does
    ↵ act on" was unanswerable from the screen.

    RED mutation: restore the combined branch; the two renders become equal again.
    """
    from mapper.widgets.components import DsChip

    chip = DsChip(label="acta")
    selected_render = None
    focused_render = None

    chip.selected = True
    selected_render = chip.render()
    chip.selected = False

    # Simulate focus without an app by overriding the state probe.
    chip._state = lambda: "focused"
    focused_render = chip.render()

    assert selected_render.plain != focused_render.plain, (
        "focused and selected render identically"
    )
