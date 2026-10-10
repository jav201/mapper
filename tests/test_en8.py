"""Inc-EN-8 -- operator wording rulings (E1-E3), the EN-5 copy carries, and the `darkside.plain` arms for the six
user- and file-controlled sites (`EN5-REV-F2`).

Authority: `VERDICT-inc-en-2026-10-02.md` Rounds 1-3 (E1, E2, E3 and the EN-8 routing paragraph) and `A-136`.

Two kinds of arm live here.  The wording arms (E1-E3, items 4-8) were committed `xfail(strict=True)` and measured RED on
`9198edf` (12 failed, with `--runxfail`); the source commit removed the marker.  The `plain` arms are PINS: they are green on the base because the
`darkside.plain` calls exist there, and each one exists to kill the mutant that drops that call (recorded in the
increment record).  Control and bidi characters are written as escapes only.
"""
from __future__ import annotations

import pytest
from textual.widgets import Input, Static

from mapper.app import (
    MapperApp, MapScreen, RepoScreen, _ConfirmScreen, _FichaScreen, _ImportPreviewScreen, _PromptScreen,
    _TemplateScreen,
)
from mapper.github import GitHubConnector, GitHubError
from mapper.model import Edge, Ficha, Graph, Node
from mapper.screens.coverage import CoverageScreen
from tests.inc3_support import open_map
from tests.test_export_state import _wide_and_deep
from tests.test_pan import CONTEXT_OF_USE, _hint, _open_pan_map

RLO = "\u202e"
FFFD = "\ufffd"

def _tree(*titles: str) -> Graph:
    """root -> n1 -> n2 ..., one node per title after the root."""
    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title="erp")))
    parent = "root"
    for i, title in enumerate(titles, 1):
        graph.add_node(Node(id=f"n{i}", ficha=Ficha(title=title)))
        graph.add_edge(Edge(parent, f"n{i}"))
        parent = f"n{i}"
    return graph


# -- E1: the pan-edge notice ----------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_e1_the_pan_edge_notice_reads_edge_of_the_map(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)
        await pilot.press("H")
        await pilot.pause()
        hint = _hint(screen)
        assert "edge of the map" in hint and "territory" not in hint, hint


@pytest.mark.asyncio
async def test_e1_the_unlaid_out_graph_site_says_it_too(tmp_path, monkeypatch):
    """The second site: `pan_extent` raising (a cyclic graph) answers with the same declaration."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        screen = await _open_pan_map(app, pilot)

        def boom(*args, **kwargs):
            raise ValueError("not a tree")

        monkeypatch.setattr("mapper.screens.map.screen.pan_extent", boom)
        await pilot.press("L")
        await pilot.pause()
        hint = _hint(screen)
        assert "edge of the map" in hint and "territory" not in hint, hint


# -- E2: the export stale-file sentence -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_e2_a_refused_export_says_where_the_old_file_comes_from(tmp_path):
    notices: list[str] = []
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("crece", _wide_and_deep(3, 3))
        app.push_screen(MapScreen("crece"))
        await pilot.pause()
        screen = app.screen
        await pilot.press("e")
        await pilot.pause()
        assert (screen.store.workspace / "crece.svg").is_file(), "the fixture never produced a first artifact"
        screen.graph = _wide_and_deep(200, 100)
        screen.notify = lambda msg, **kw: notices.append(str(msg))
        await pilot.press("e")
        await pilot.pause()
    assert len(notices) == 1, notices
    assert notices[0].endswith(
        " Focus a subtree with f and export that view."
        " Nothing was written; crece.svg on disk is from an earlier export."), notices[0]


# -- E3: the palette footer ----------------------------------------------------------------------------------------
@pytest.mark.parametrize("size", [(118, 34), (87, 34)])
@pytest.mark.asyncio
async def test_e3_the_footer_is_the_counts_then_the_three_pairs_joined_by_a_middle_dot(tmp_path, size):
    from mapper.screens.palette import CommandPalette

    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await pilot.pause()
        await pilot.press("ctrl+p")
        await pilot.pause()
        await pilot.pause()
        pal = app.screen
        assert isinstance(pal, CommandPalette), pal
        footer = pal.query_one("#palette-count").content.plain
    shown, total = len(pal._items), len(pal._items)  # noqa: SLF001  an empty query lists everything
    assert footer == f" {shown}/{total} actions   ↑↓ move · ↵ run · esc close", footer


# -- item 4: the ficha modal ---------------------------------------------------------------------------------------
async def _ficha_text(tmp_path, record: str | None) -> str:
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        fields = {"D": record} if record else {}
        node = Node(id="a", ficha=Ficha(title="alfa", fields=fields))
        graph = Graph()
        graph.add_node(node)
        app.push_screen(_FichaScreen(node, graph))
        await pilot.pause()
        return app.screen.query_one("#ficha-content", Static).content.plain


@pytest.mark.asyncio
async def test_item4_the_ficha_modal_labels_the_document_field_record(tmp_path):
    with_record = await _ficha_text(tmp_path, "REC-7")
    assert "record REC-7\n" in with_record and "document" not in with_record, with_record


@pytest.mark.asyncio
async def test_item4_an_empty_record_reads_like_owner_and_created_not_record_no_record(tmp_path):
    without = await _ficha_text(tmp_path, None)
    assert "record —\n" in without, without
    assert "record no record" not in without and "document" not in without, without
    assert "owner —\n" in without and "created —\n" in without, without


# -- item 5: the singular ------------------------------------------------------------------------------------------
async def _confirm_message(tmp_path, graph: Graph, cursor: str, raw_title: str | None = None) -> str:
    """`raw_title` is put on the cursor's node IN MEMORY after the map loads: the store coerces on its own way in, so a
    title saved and reloaded would never reach the confirmation raw and the source site would go unexercised."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("m", graph)
        screen = await open_map(app, pilot, "m")
        if raw_title is not None:
            screen.graph.nodes[cursor].ficha.title = raw_title
        screen.nav.cursor = cursor
        await pilot.press("x")
        await pilot.pause()
        assert isinstance(app.screen, _ConfirmScreen), app.screen
        return app.screen.message


@pytest.mark.asyncio
async def test_item5_one_descendant_is_singular_for_a_branch(tmp_path):
    graph = _tree("alfa", "beta")
    message = await _confirm_message(tmp_path, graph, "n1")
    assert message == "archive «alfa» and its 1 descendant?", message


@pytest.mark.asyncio
async def test_item5_one_descendant_is_singular_for_the_root(tmp_path):
    graph = _tree("alfa")
    orphan = Node(id="z", ficha=Ficha(title="zeta"))  # outside the root's subtree, so archiving the root is allowed
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("m", graph)
        screen = await open_map(app, pilot, "m")
        screen.graph.add_node(orphan)
        screen.nav.cursor = "root"
        await pilot.press("x")
        await pilot.pause()
        assert isinstance(app.screen, _ConfirmScreen), app.screen
        message = app.screen.message
    assert message == "archive the root «erp» and its 1 descendant? this will replace the root of the map.", message


@pytest.mark.asyncio
async def test_item5_more_than_one_stays_plural(tmp_path):
    message = await _confirm_message(tmp_path, _tree("alfa", "beta", "gamma"), "n1")
    assert message == "archive «alfa» and its 2 descendants?", message


# -- item 6: binding labels are lowercase --------------------------------------------------------------------------
def test_item6_cancel_and_close_labels_are_lowercase():
    assert [b[2] for b in _PromptScreen.BINDINGS] == ["cancel"]
    assert [b[2] for b in _TemplateScreen.BINDINGS] == ["close", "close"]
    assert [b[2] for b in _FichaScreen.BINDINGS] == ["close", "close"]
    close = [b[2] for b in CoverageScreen.BINDINGS if b[1] == "dismiss"]
    assert close == ["close", "close"], close


# -- item 7: the broken declaration --------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_item7_a_broken_declaration_says_the_hidden_node_count_is_unavailable(tmp_path, monkeypatch):
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("m", _tree("alfa"))
        screen = await open_map(app, pilot, "m")

        def lost() -> None:
            raise LookupError("no declaration")

        monkeypatch.setattr(screen, "_unpainted_ids", lost)
        text = screen._pagination_text().plain  # noqa: SLF001
    assert text.endswith("hidden-node count unavailable "), text
    assert "declaration" not in text, text


# -- item 8: the door note -----------------------------------------------------------------------------------------
def test_item8_the_template_door_says_what_it_does_not_what_it_is_called():
    from mapper.app import HomeScreen

    assert HomeScreen._DOOR_NOTES["t"] == "start with preset fields"
    notes = list(HomeScreen._DOOR_NOTES.values())
    assert len(set(notes)) == len(notes)


# -- EN5-REV-F2: `darkside.plain` on the six user- and file-controlled sites ---------------------------------------
def _coerced(text: str, *, where: str) -> None:
    assert FFFD in text, f"{where}: the override was not replaced: {text!r}"
    assert RLO not in text, f"{where}: the right-to-left override reached the sink: {text!r}"


@pytest.mark.asyncio
async def test_plain_site_1_the_archive_confirmation_name(tmp_path):
    message = await _confirm_message(tmp_path, _tree("alfa"), "n1", raw_title="a" + RLO + "b")
    _coerced(message, where="archive confirmation")
    assert message == f"archive «a{FFFD}b»?", message


@pytest.mark.asyncio
async def test_plain_site_2_a_typed_child_title_is_stored_coerced(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("m", _tree())
        screen = await open_map(app, pilot, "m")
        screen.nav.cursor = "root"
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, _PromptScreen), app.screen
        app.screen.query_one("#prompt-input", Input).value = "a" + RLO + "b"
        await pilot.press("enter")
        await pilot.pause()
        titles = [n.ficha.title for n in screen.graph.nodes.values() if n.id != "root"]
    assert len(titles) == 1, titles
    _coerced(titles[0], where="stored Ficha.title")
    assert titles == [f"a{FFFD}b"], titles


@pytest.mark.asyncio
async def test_plain_site_3_a_typed_attachment_target_is_stored_coerced(tmp_path):
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("m", _tree("alfa"))
        screen = await open_map(app, pilot, "m")
        assert screen.nav.cursor == "root"  # the inspector follows the cursor the map opened on
        await pilot.press("A")
        await pilot.pause()
        assert isinstance(app.screen, _PromptScreen), app.screen
        app.screen.query_one("#prompt-input", Input).value = "https://example.invalid/a" + RLO + "b"
        await pilot.press("enter")
        await pilot.pause()
        stored = [a.path for a in screen.graph.nodes["root"].ficha.attachments]
    assert len(stored) == 1, stored
    _coerced(stored[0], where="stored attachment path")
    assert stored == [f"https://example.invalid/a{FFFD}b"], stored


def _stub_fetch(monkeypatch, message: str) -> None:
    def fetch(self, progress=None):
        raise GitHubError(message)

    monkeypatch.setattr(GitHubConnector, "fetch", fetch)


@pytest.mark.asyncio
async def test_plain_site_4_the_repo_name_of_an_accepted_local_path(tmp_path, monkeypatch):
    _stub_fetch(monkeypatch, "stub")
    repo = tmp_path / ("a" + RLO + "b")
    (repo / ".git").mkdir(parents=True)
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        screen = RepoScreen(str(repo))
        assert str(repo) in screen.shown, "the fixture must be an accepted local path, painted as typed"
        app.push_screen(screen)
        await pilot.pause()
        await pilot.pause()
        name = app.screen.query_one("#repo-name", Static).content.plain
    _coerced(name, where="repo name")


def _boom(self, *args, **kwargs):
    raise ValueError("x" + RLO + "y")


@pytest.mark.asyncio
async def test_plain_site_5a_the_map_canvas_failure_text(tmp_path, monkeypatch):
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("m", _tree("alfa"))
        screen = await open_map(app, pilot, "m")
        # The real renderer, failing inside `render` (a stand-in renderer fails earlier, in `_reclamp_pan`, with a
        # message that carries no text of ours).
        monkeypatch.setattr(type(screen._current_renderer()), "render", _boom)  # noqa: SLF001
        screen.refresh_canvas()
        await pilot.pause()
        painted = screen.query_one("#map-canvas", Static).content.plain
    assert "could not draw the map" in painted, painted
    _coerced(painted, where="map canvas")


@pytest.mark.asyncio
async def test_plain_site_5b_the_preview_canvas_failure_text(tmp_path, monkeypatch):
    class Boom:
        render = _boom

    monkeypatch.setattr("mapper.app.LayeredRenderer", Boom)
    csv_path = tmp_path / "p.csv"
    csv_path.write_text("id,title,parent\na,A,\n", encoding="utf-8")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.push_screen(_ImportPreviewScreen(_tree("alfa"), csv_path))
        await pilot.pause()
        painted = app.screen.query_one("#import-preview-canvas", Static).content.plain
    assert "could not draw the preview" in painted, painted
    _coerced(painted, where="preview canvas")


@pytest.mark.asyncio
async def test_plain_site_6_a_github_error_in_the_stages_panel(tmp_path, monkeypatch):
    _stub_fetch(monkeypatch, "boom" + RLO + "bang")
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.push_screen(RepoScreen("o/n"))
        for _ in range(6):
            await pilot.pause()
        screen = app.screen
        assert screen.failure, "the stubbed fetch never failed"
        stages = screen.query_one("#repo-stages", Static).content.plain
    assert "boom" in stages, stages
    _coerced(stages, where="stages panel")
