"""G6 — ficha text is coerced at graph entry, and `store.save()` degrades to a
toast instead of crashing (`INC8-P3-SEC-F1`, Round 4 verdict G6).

Three RED arms, per `.dev-flow/2026-08-26-ui-next-batch-02/03-increments/
increment-024-g6-store-surrogates.md`:

(a) a sidecar with a YAML-escaped lone surrogate loads clean (store-level).
(b) the real `FichaInspector.FieldCommitted` event with a surrogate title does
    not crash a mounted `MapScreen`.
(c) each of the 6 unguarded `store.save()` call sites degrades to a toast when
    `store.save` is forced to raise, parametrized by call site and driven
    through its real action.

Every arm reproduces the defect exactly as described: a lone surrogate
(U+D800-U+DFFF) is never typed literally into this file; it is built with
`chr()` / `json.dumps`, per the batch's control-character discipline.
"""
from __future__ import annotations

import json

import pytest

from mapper.app import MapperApp, MapScreen, _ConfirmScreen, _PromptScreen
from mapper.model import Attachment, Edge, Ficha, Graph, Node
from mapper.store import MapStore
from mapper.widgets.inspector import FichaInspector

LONE_SURROGATE = chr(0xD800)


def _seed(app, map_id="g6", *, with_attachment=False):
    """root -> a (leaf) -> nothing; `a` optionally carries one attachment."""
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="root")))
    attachments = (
        [Attachment(kind="file", path="docs/acta.pdf")] if with_attachment else []
    )
    g.add_node(Node(id="a", ficha=Ficha(title="alfa", attachments=attachments)))
    g.add_edge(Edge("root", "a"))
    app.store.save(map_id, g)
    return map_id


async def _open(app, pilot, map_id, cursor="a"):
    app.push_screen(MapScreen(map_id))
    await pilot.pause()
    screen = app.screen
    screen.nav.cursor = cursor
    screen.refresh_canvas()
    await pilot.pause()
    return screen


# ---------------------------------------------------------------------------
# (a) load-side: a sidecar carrying an escaped lone surrogate
# ---------------------------------------------------------------------------


def test_g6a_load_coerces_a_sidecar_lone_surrogate_title_instead_of_denying_the_map(
    tmp_store,
):
    """`_nodos.yml` carries `"\\ud800"` — YAML decodes it to a real lone
    surrogate.  Today `store.load` raises `MapStoreError` ("no se pudo
    indexar ...: UnicodeEncodeError") because the raw surrogate reaches
    sqlite3 uncoerced.  After the fix the map loads, the title is coerced to
    U+FFFD (the same replacement `darkside.plain()` uses), and a save
    round-trip writes valid UTF-8.

    RED mutation: remove the `plain()` coercion from `_coerce_field`'s `str`
    branch; this arm reddens with the exact `MapStoreError` above.
    """
    escaped_title = json.dumps(LONE_SURROGATE)
    assert escaped_title.isascii(), "the fixture file itself must be plain ASCII"
    (tmp_store.workspace / "demo.mmd").write_text("graph TD\n    root\n", encoding="utf-8")
    (tmp_store.workspace / "demo_nodos.yml").write_text(
        f"nodes:\n  root:\n    title: {escaped_title}\n", encoding="utf-8"
    )

    graph = tmp_store.load("demo")  # must not raise MapStoreError

    title = graph.nodes["root"].ficha.title
    assert LONE_SURROGATE not in title, "the raw surrogate must never reach the model"
    assert "�" in title, "the coercion must replace it, not silently drop it"

    # The coerced graph must round-trip through a save + reload as valid UTF-8.
    tmp_store.save("demo", graph)
    reloaded = tmp_store.load("demo")
    assert reloaded.nodes["root"].ficha.title == title


# ---------------------------------------------------------------------------
# (b) mutation-side: the real FieldCommitted event, on a mounted MapScreen
# ---------------------------------------------------------------------------


async def test_g6b_field_committed_with_a_surrogate_title_does_not_crash(tmp_path):
    """A broken paste lands a lone surrogate in the title Input; on submit the
    inspector posts the real `FieldCommitted` event with that raw value.

    Today `on_ficha_inspector_field_committed` assigns `event.value` to
    `node.ficha.title` unchanged and calls `self.store.save(...)` unguarded;
    the surrogate reaches `_atomic_write`'s `Path.write_text(...,
    encoding="utf-8")` and raises an uncaught `UnicodeEncodeError`, which
    escapes the message handler and crashes the session.

    After the fix the value is coerced before it ever reaches the graph, the
    save succeeds, and the file on disk still re-loads cleanly.

    RED mutation: drop the coercion at the `title` assignment; this arm
    reddens with an uncaught `UnicodeEncodeError` escaping `pilot.pause()`.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app)
        screen = await _open(app, pilot, map_id)
        inspector = screen.query_one("#map-inspector", FichaInspector)

        inspector.post_message(
            FichaInspector.FieldCommitted("a", "title", LONE_SURROGATE)
        )
        await pilot.pause()

        assert isinstance(app.screen, MapScreen), "the surrogate crashed the session"

        reloaded = MapStore(tmp_path).load(map_id)
        title = reloaded.nodes["a"].ficha.title
        assert LONE_SURROGATE not in title
        assert "�" in title


# ---------------------------------------------------------------------------
# (c) the 6 unguarded `store.save()` call sites degrade to a toast
# ---------------------------------------------------------------------------


async def _drive_field_commit(app, pilot, screen):
    inspector = screen.query_one("#map-inspector", FichaInspector)
    inspector.post_message(FichaInspector.FieldCommitted("a", "title", "nuevo"))
    await pilot.pause()


async def _drive_attachment_add(app, pilot, screen):
    screen.action_add_attachment()
    await pilot.pause()
    assert isinstance(app.screen, _PromptScreen)
    await pilot.press(*"docs/otro.pdf")
    await pilot.press("enter")
    await pilot.pause()


async def _drive_attachment_remove(app, pilot, screen):
    inspector = screen.query_one("#map-inspector", FichaInspector)
    inspector.post_message(FichaInspector.AttachmentRemoveRequested("a", 0))
    await pilot.pause()


async def _drive_undo(app, pilot, screen):
    # A snapshot must exist before `u` has anything to restore.  Pushed with
    # the REAL store (before the monkeypatch below installs the raising one),
    # so this setup edit itself must succeed.
    inspector = screen.query_one("#map-inspector", FichaInspector)
    inspector.post_message(FichaInspector.FieldCommitted("a", "title", "editado"))
    await pilot.pause()


async def _drive_undo_after_setup(app, pilot, screen):
    screen.action_undo()
    await pilot.pause()


async def _drive_add_child(app, pilot, screen):
    screen.action_add_child()
    await pilot.pause()
    assert isinstance(app.screen, _PromptScreen)
    await pilot.press(*"nuevo hijo")
    await pilot.press("enter")
    await pilot.pause()


async def _drive_archive(app, pilot, screen):
    screen.action_archive()
    await pilot.pause()
    assert isinstance(app.screen, _ConfirmScreen)
    await pilot.press("y")
    await pilot.pause()


SITES = {
    "field_commit": (False, _drive_field_commit),
    "attachment_add": (False, _drive_attachment_add),
    "attachment_remove": (True, _drive_attachment_remove),
    "undo": (False, _drive_undo_after_setup),
    "add_child": (False, _drive_add_child),
    "archive": (False, _drive_archive),
}


@pytest.mark.parametrize("site", sorted(SITES))
async def test_g6c_each_unguarded_save_site_degrades_to_a_toast(tmp_path, site):
    """Force `store.save` to raise at each of the 6 call sites named in
    `INC8-P3-SEC-F1` (field commit, attachment add, attachment remove, undo,
    add-child, archive).  Today none of them guards the call, so the raise
    escapes the message handler and crashes the session.

    RED mutation: remove the `try`/`except` this fix adds around any one of
    the 6 `self.store.save(...)` calls; that site's arm reddens.
    """
    with_attachment, driver = SITES[site]
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app, with_attachment=with_attachment)
        screen = await _open(app, pilot, map_id)

        if site == "undo":
            # Real, unguarded setup edit — must succeed with the real store.
            await _drive_undo(app, pilot, screen)
            assert MapStore(tmp_path).load(map_id).nodes["a"].ficha.title == "editado"

        notices: list[tuple[str, dict]] = []
        app.notify = lambda msg, **kw: notices.append((str(msg), kw))

        def exploding_save(*_a, **_kw):
            raise RuntimeError("boom (forced by G6-Fn mutation harness)")

        screen.store.save = exploding_save

        await driver(app, pilot, screen)

        assert isinstance(app.screen, MapScreen), (
            f"{site}: the forced save failure crashed the session"
        )
        assert notices, f"{site}: no toast was shown when store.save raised"
        assert any("no se pudo guardar" in n for n, _ in notices), (
            f"{site}: the toast did not name the save failure — {notices}"
        )
