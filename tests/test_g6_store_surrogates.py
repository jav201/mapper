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

---

The section below (`test_g6c_*`) is the G6 CORRECTIVE PASS: the independent
security review returned `BLOCK-UNTIL G6-C-F1, F2, F3, F8` against `65621f3`
(the three commits above), plus F4/F5/F6/F7 (medium/low). Each `test_g6c_*`
function names the finding it arms in its own docstring. No literal control
character or bidi mark is ever typed into this file either; every one is
built with `chr()`.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from mapper.app import MapperApp, MapScreen, _ConfirmScreen, _PromptScreen
from mapper.model import Attachment, Document, Edge, Ficha, Graph, Node
from mapper.store import MapStore
from mapper.widgets.inspector import FichaInspector

LONE_SURROGATE = chr(0xD800)
BIDI_MARK = chr(0x200E)  # LEFT-TO-RIGHT MARK, in `darkside.COERCION_RANGES`.


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


# ---------------------------------------------------------------------------
# G6 corrective pass — G6-C-F1 .. F8
# ---------------------------------------------------------------------------


async def test_g6c_f1_factory_persist_degrades_to_a_toast_and_survives(tmp_path):
    """`G6-C-F1`.  `FactoryScreen._persist` called `store.save()` with no
    guard — reached from `action_edit_doc` (via `EditorScreen`'s `on_save`)
    and `action_import_office`.  Forced to raise through the real
    `action_edit_doc` path, it must toast and the screen must survive.

    RED mutation: remove the `try`/`except` `_save_or_toast` puts around
    `_persist`'s `store.save()` call (i.e. call `store.save` directly again).
    """
    from mapper.screens.editor import EditorScreen
    from mapper.screens.factory import FactoryScreen

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="root")))
        g.documents["plantilla"] = Document(name="plantilla", source="hola")
        app.store.save("fx", g)

        screen = FactoryScreen(
            g, process_name="fx", document_name="plantilla", map_id="fx"
        )
        app.push_screen(screen)
        await pilot.pause()

        notices: list[tuple[str, dict]] = []
        app.notify = lambda msg, **kw: notices.append((str(msg), kw))

        def exploding_save(*_a, **_kw):
            raise RuntimeError("boom (forced by G6-C-F1 mutation harness)")

        app.store.save = exploding_save

        screen.action_edit_doc()
        await pilot.pause()
        assert isinstance(app.screen, EditorScreen)
        await pilot.press("ctrl+s")
        await pilot.pause()

        assert isinstance(app.screen, FactoryScreen), (
            "the forced save failure crashed the factory screen"
        )
        assert notices, "no toast was shown when store.save raised"
        assert any("no se pudo guardar" in n for n, _ in notices)


async def test_g6c_f2_save_failure_toast_names_no_path_or_username(tmp_path):
    """`G6-C-F2`.  The save-failure toast used to interpolate `str(e)`
    directly — an `OSError`'s own message embeds the full absolute path and,
    on Windows, the account name.  The placeholder `<operator>` stands in for
    a real account name; a real one is never typed here (see
    `tests/test_no_operator_paths.py`).

    RED mutation: interpolate `{e}` again in `_save_or_toast`'s toast.
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        map_id = _seed(app)
        screen = await _open(app, pilot, map_id)

        notices: list[tuple[str, dict]] = []
        app.notify = lambda msg, **kw: notices.append((str(msg), kw))

        fake_path = r"C:\Users\<operator>\x"
        raw_message = f"[Errno 13] Permission denied: '{fake_path}'"

        def exploding_save(*_a, **_kw):
            raise OSError(raw_message)

        screen.store.save = exploding_save

        await _drive_field_commit(app, pilot, screen)

        assert notices, "no toast was shown when store.save raised"
        toast = notices[-1][0]
        assert "\\Users\\" not in toast, f"the toast leaked a path: {toast!r}"
        assert fake_path not in toast, f"the toast leaked the fake path: {toast!r}"
        assert raw_message not in toast, f"the toast leaked str(e): {toast!r}"
        assert "Permission denied" not in toast
        assert map_id in toast, f"the toast dropped the map id: {toast!r}"
        assert "OSError" in toast, f"the toast dropped the exception type: {toast!r}"


async def test_g6c_f3_new_map_on_mount_save_degrades_to_a_toast(tmp_path):
    """`G6-C-F3`.  The 8th `store.save()` call site — `MapScreen.on_mount`'s
    `map_id == "new"` branch — was unguarded.  Forced to raise, `on_mount`
    itself must not crash; the screen still mounts with the in-memory map and
    a toast names the failure.

    RED mutation: drop the `_save_or_toast` guard around this site (call
    `self.store.save(...)` directly again).
    """
    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        notices: list[tuple[str, dict]] = []
        app.notify = lambda msg, **kw: notices.append((str(msg), kw))

        def exploding_save(*_a, **_kw):
            raise RuntimeError("boom (forced by G6-C-F3 mutation harness)")

        app.store.save = exploding_save

        app.push_screen(MapScreen("new"))
        await pilot.pause()

        assert isinstance(app.screen, MapScreen), (
            "the 8th store.save() site crashed on_mount"
        )
        assert notices, "no toast was shown when the new-map save raised"
        assert any("no se pudo guardar" in n for n, _ in notices)


def _store_save_calls(tree: ast.AST) -> list[ast.AST]:
    """Every reference to a `.save` in `tree` that is not `MapStore`'s own.

    `G6-SEC-F9` (MEDIUM): this used to match a call whose receiver's last
    identifier was literally `store`, so `db = store; db.save(...)` -- or any
    other name, alias, bound method or `getattr` -- evaded the census (shown
    live).  It is now STRUCTURAL and judges by the method, not the receiver's
    spelling: every `Attribute` named `save` (a call, or a reference such as
    `go = store.save`) and every `getattr(x, "save")` is a site to judge.

    One exemption, named and narrow: `self.save(...)` inside `class MapStore`
    (its `create_seed` / `create_from_template`), which is the store calling its
    OWN method; their callers carry the `try`.  Anything else -- a receiver that
    is not provably something other than a store -- is judged by the same rule
    as `store.save`: inside `_save_or_toast`, or inside a `try` body.
    """
    parents = {child: parent for parent in ast.walk(tree)
               for child in ast.iter_child_nodes(parent)}

    def in_map_store(node: ast.AST) -> bool:
        while node in parents:
            node = parents[node]
            if isinstance(node, ast.ClassDef):
                return node.name == "MapStore"
        return False

    sites: list[ast.AST] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "save":
            own = isinstance(node.value, ast.Name) and node.value.id == "self"
            if own and in_map_store(node):
                continue
            sites.append(node)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == "getattr" and len(node.args) >= 2
              and isinstance(node.args[1], ast.Constant) and node.args[1].value == "save"):
            sites.append(node)
    return sites


def _node_contains(container: ast.AST, target: ast.AST) -> bool:
    return any(n is target for n in ast.walk(container))


def _in_try_body(tree: ast.AST, call: ast.Call) -> bool:
    """`call` sits in some `try:`'s BODY (not its `except`/`else`/`finally`)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for stmt in node.body:
                if _node_contains(stmt, call):
                    return True
    return False


def _in_function(tree: ast.AST, call: ast.Call, name: str) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            if _node_contains(node, call):
                return True
    return False


def test_g6c_f3_census_every_store_save_call_is_guarded():
    """`G6-C-F3`.  An AST walk over every `.py` file under `mapper/`: every
    `store.save(`-shaped call must sit inside `_save_or_toast` (the one
    guarded call, guarding itself) or inside a `try` body. The call LIST is
    derived from the AST, never hand-listed.

    RED mutation: add ANY new `self.store.save(...)` (or `store.save(...)`)
    call under `mapper/` with no `try` around it and not inside
    `_save_or_toast` — this test reddens without editing the test itself.
    """
    mapper_dir = Path(__file__).resolve().parents[1] / "mapper"
    py_files = sorted(mapper_dir.rglob("*.py"))
    assert py_files, "no .py files found under mapper/ — the walk itself is broken"

    total = 0
    unguarded: list[str] = []
    for path in py_files:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for call in _store_save_calls(tree):
            total += 1
            if _in_function(tree, call, "_save_or_toast"):
                continue
            if _in_try_body(tree, call):
                continue
            unguarded.append(f"{path.relative_to(mapper_dir.parent)}:{call.lineno}")

    assert total >= 1, (
        "the AST pattern matched no store.save(...) call at all — "
        "the census would be vacuously green"
    )
    assert not unguarded, f"unguarded store.save() call sites: {unguarded}"


async def test_g6c_f4_guardar_como_name_with_lone_surrogate_saves_cleanly(tmp_path):
    """`G6-C-F4`.  The "guardar como" map name (`ImportPreviewScreen.action_save`)
    is operator-typed and reached `store.save(name, ...)` uncoerced. A lone
    surrogate typed there must not raise uncaught; it is coerced before the
    save and the resulting map is reloadable.

    RED mutation: drop the `name = darkside.plain(name)` line in `action_save`.
    """
    from mapper.app import _ImportPreviewScreen

    app = MapperApp(tmp_path)
    async with app.run_test() as pilot:
        await pilot.pause()
        g = Graph()
        g.add_node(Node(id="root", ficha=Ficha(title="root")))
        app.push_screen(_ImportPreviewScreen(g, tmp_path / "nodos.csv"))
        await pilot.pause()

        screen = app.screen
        screen.action_save()
        await pilot.pause()
        assert isinstance(app.screen, _PromptScreen)

        prompt = app.screen
        from textual.widgets import Input

        raw_name = f"mapa{LONE_SURROGATE}raro"
        prompt.query_one("#prompt-input", Input).value = raw_name
        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, MapScreen), (
            "a surrogate in the 'guardar como' name crashed the session"
        )
        saved_id = app.screen.map_id
        assert LONE_SURROGATE not in saved_id
        assert "\ufffd" in saved_id

        reloaded = MapStore(tmp_path).load(saved_id)
        assert reloaded.nodes["root"].ficha.title == "root"


def test_g6c_f5_edge_label_is_coerced():
    """`G6-C-F5`.  `Edge.label`, set raw by `mermaid.parse` straight from the
    `.mmd` text, never passed through `A-111`'s coercion (scoped to sidecar
    text positions). A bidi mark in an edge label must come out coerced.

    RED mutation: drop the `plain()` call around `_unescape_mermaid(edge_label)`
    in `mermaid.parse`.
    """
    from mapper.mermaid import parse

    mmd = f"graph TD\n    root[root] -->|nota{BIDI_MARK}| child[child]\n"
    graph = parse(mmd)
    edge = next(e for e in graph.edges if e.child_id == "child")
    assert BIDI_MARK not in edge.label
    assert "\ufffd" in edge.label


def test_g6c_f6_mmd_only_orphan_node_ficha_is_coerced(tmp_store):
    """`G6-C-F6`.  An mmd-only ("orphan") node — the sidecar carries no entry
    for it — used to skip every `A-111` coercion; its title, set raw by
    `mermaid.parse`, reached the graph (and `_reindex`'s sqlite3 bind)
    uncoerced.

    RED mutation: drop the post-loop coercion pass over nodes not in
    `seen_ids` in `_graph_from_sidecar`.
    """
    mmd = f"graph TD\n    root[root] --> orphan[orph{BIDI_MARK}an]\n"
    (tmp_store.workspace / "orph.mmd").write_text(mmd, encoding="utf-8")
    (tmp_store.workspace / "orph_nodos.yml").write_text("nodes: {}\n", encoding="utf-8")

    graph = tmp_store.load("orph")

    title = graph.nodes["orphan"].ficha.title
    assert BIDI_MARK not in title
    assert "\ufffd" in title

    # Round-trips through a save + reload as valid UTF-8, same as (a).
    tmp_store.save("orph", graph)
    reloaded = tmp_store.load("orph")
    assert reloaded.nodes["orphan"].ficha.title == title


def test_g6c_f7_crlf_notes_round_trip_as_lf_with_no_replacement_char(tmp_store):
    """`G6-C-F7` (regression `A-111` introduced).  `plain()` maps `\\r`
    (U+000D) to U+FFFD — correct at a paint sink, but `_coerce_field` runs it
    on every LOADED string, so CRLF notes pasted on Windows corrupted on the
    very first load, silently.

    RED mutation: drop `_normalize_newlines` from `_coerce_field`'s two
    branches.
    """
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="root", notes="line1\r\nline2")))
    tmp_store.save("crlf", g)

    reloaded = tmp_store.load("crlf")
    notes = reloaded.nodes["root"].ficha.notes
    assert notes == "line1\nline2"
    assert "\ufffd" not in notes


def test_g6c_f7_lone_cr_round_trips_as_lf(tmp_store):
    """`G6-C-F7`, the lone-`\\r` half (old Mac line endings)."""
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="root", notes="a\rb")))
    tmp_store.save("cr", g)

    reloaded = tmp_store.load("cr")
    assert reloaded.nodes["root"].ficha.notes == "a\nb"


def test_g6c_f7_tab_cjk_emoji_round_trip_byte_identical(tmp_store):
    """`G6-C-F7`'s negative control: TAB/CJK/emoji are untouched by the
    newline normalization and still round-trip exactly, same as before
    `A-111`.
    """
    text = "col1\tcol2 \u4e2d\u6587 \U0001F600"
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="root", notes=text)))
    tmp_store.save("mixed", g)

    reloaded = tmp_store.load("mixed")
    assert reloaded.nodes["root"].ficha.notes == text


def test_g6c_f8a_two_phase_write_leaves_both_files_unchanged_on_temp_failure(
    tmp_store, monkeypatch
):
    """`G6-C-F8`(a).  A forced failure writing the SECOND temp file must
    leave BOTH on-disk truth files exactly as they were before the save
    attempt — the previous single-phase `save()` had already replaced
    `.mmd` by the time `_nodos.yml`'s write could still fail.

    RED mutation: revert `save()` to the single-phase
    `self._atomic_write(mmd_path, ...); self._atomic_write(yml_path, ...)`.
    """
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="v1")))
    tmp_store.save("torn", g)

    mmd_path = tmp_store.workspace / "torn.mmd"
    yml_path = tmp_store.workspace / "torn_nodos.yml"
    mmd_before = mmd_path.read_bytes()
    yml_before = yml_path.read_bytes()

    g.nodes["root"].ficha.title = "v2"

    real_write_text = Path.write_text

    def failing_write_text(self, *a, **kw):
        if self.name == "torn_nodos.yml.tmp":
            raise OSError("boom (forced by G6-C-F8a mutation harness)")
        return real_write_text(self, *a, **kw)

    monkeypatch.setattr(Path, "write_text", failing_write_text)
    with pytest.raises(OSError):
        tmp_store.save("torn", g)
    monkeypatch.undo()

    assert mmd_path.read_bytes() == mmd_before, "the .mmd file was torn"
    assert yml_path.read_bytes() == yml_before, "the sidecar file was torn"


def test_g6c_f8b_failure_between_replaces_is_warned_on_next_load(
    tmp_store, monkeypatch
):
    """`G6-C-F8`(b).  A crash between the two `replace()` calls leaves `.mmd`
    replaced and the sidecar stale — the next `load()` must warn (naming the
    map, no path) rather than silently reverting the edit with no trace.

    RED mutation: drop the `_mmd_hash` mismatch check from `load()` (or drop
    writing `_mmd_hash` in `save()`).
    """
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="v1")))
    tmp_store.save("torn2", g)

    g.nodes["root"].ficha.title = "v2"

    real_replace = Path.replace
    calls = {"n": 0}

    def flaky_replace(self, target):
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("boom (forced by G6-C-F8b mutation harness, 2nd replace)")
        return real_replace(self, target)

    monkeypatch.setattr(Path, "replace", flaky_replace)
    with pytest.raises(OSError):
        tmp_store.save("torn2", g)
    monkeypatch.undo()

    reloaded = tmp_store.load("torn2")
    assert any("desincronizado" in w for w in reloaded.load_warnings), (
        f"no mismatch warning: {reloaded.load_warnings}"
    )
    assert "torn2" in "; ".join(reloaded.load_warnings)
    # The stale sidecar is what actually loaded — the edit "reverted", now WARNED.
    assert reloaded.nodes["root"].ficha.title == "v1"


# ---------------------------------------------------------------------------
# G6-SEC-F9 -- the save census is structural, not a name match (Inc-9c)

_F9_EVASIONS = {
    "alias of a parameter": "def f(store):\n    db = store\n    db.save('m', g)\n",
    "alias of an attribute": "class S:\n    def f(self):\n        db = self.store\n        db.save('m', g)\n",
    "alias of a chain": "class S:\n    def f(self):\n        s = self.app.store\n        s.save('m', g)\n",
    "bound method": "def f(store):\n    go = store.save\n    go('m', g)\n",
    "getattr": "def f(store):\n    getattr(store, 'save')('m', g)\n",
    "an unknown receiver": "def f(x):\n    x.save('m', g)\n",
}


@pytest.mark.parametrize("source", sorted(_F9_EVASIONS), ids=str)
def test_g6_sec_f9_the_save_census_sees_through_a_renamed_receiver(source):
    """`G6-SEC-F9` (MEDIUM): the census matched a receiver literally named
    `store`, so `db = store; db.save(...)` evaded it (demonstrated live).  It is
    now structural: EVERY `.save` reference in product code is a call site to
    judge, whatever the receiver is called or however it is reached."""
    tree = ast.parse(_F9_EVASIONS[source])
    assert _store_save_calls(tree), f"the census missed: {source}"


def test_g6_sec_f9_the_stores_own_internal_save_is_not_a_call_site():
    """The one exemption, named: `MapStore` calling its OWN `self.save` inside
    the class (its `create_*` methods, whose callers carry the `try`)."""
    inside = "class MapStore:\n    def create(self):\n        self.save('m', g)\n"
    outside = "class Other:\n    def create(self):\n        self.save('m', g)\n"
    assert _store_save_calls(ast.parse(inside)) == []
    assert _store_save_calls(ast.parse(outside))
