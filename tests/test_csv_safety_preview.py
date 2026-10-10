"""CSV-safety increment 2: the import preview says why, before the save.

LLR-CSV.2.1 (`preview_csv` records every slug collision with its source
rows), LLR-CSV.2.2 (the refusal panel paints the pinned sentence, precedence
collision > multi-parent > cycle), LLR-CSV.2.3 (the preview save refuses at
the `s` keypress) and the e2e nodes AT-072/072b/072c/072d, AT-073, AT-074
driven through the real import flow (`_open_import` keys: `i`, path, `enter`,
`s`, then name + `enter` only for AT-074).
"""
import hashlib
from pathlib import Path

from textual.widgets import Input, Static

from mapper.app import MapperApp, _ImportPreviewScreen
from mapper.import_csv import preview_csv
from mapper.store import MapStore
from tests.test_draft_save import _capture_notices
from tests.test_seed_safety import _open_import

SIZE = (118, 34)

PINNED_TOAST = "the CSV has colliding ids — nothing was saved; see the preview"
PINNED_SENTENCE = (
    "CSV rows 5 (id 'a-b') and 6 (id 'A B') collapse into the node id 'a-b'; "
    "a map can hold only one parent per node, so rename the duplicated ids "
    "and import again."
)
COLLISION_TAIL = (
    "a map can hold only one parent per node, so rename the duplicated ids "
    "and import again."
)


def _write_csv(path: Path, text: str, crlf: bool = False) -> Path:
    """Write a CSV fixture; `crlf=True` persists CRLF line endings."""
    if crlf:
        path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
    else:
        path.write_text(text, encoding="utf-8")
    return path


def _evidence_csv(tmp_path: Path) -> Path:
    """The perf-evidence shape (LLR-CSV.2.1/2.2): colliding rows 5 and 6,
    rebuilt as a CRLF file — row 5 is also a self-parent, so the graph is
    cyclic too and the precedence (collision first) is what gets asserted."""
    return _write_csv(
        tmp_path / "evidence.csv",
        "id,title,parent\n"
        "root,Root,\n"
        "p1,First parent,root\n"
        "p2,Second parent,root\n"
        "a-b,First,a-b\n"
        "A B,Second,p2\n",
        crlf=True,
    )


def _digests(workspace: Path) -> dict[str, str]:
    """sha256 of EVERY file under the workspace, walked recursively."""
    return {
        p.relative_to(workspace).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(workspace.rglob("*"))
        if p.is_file()
    }


def _collisions(graph) -> dict[str, tuple[tuple[int, str], ...]]:
    return {
        c.slug: tuple((r.line_no, r.raw_id) for r in c.rows)
        for c in graph.csv_collisions
    }


async def _import_and_press_save(app, pilot, csv: Path) -> None:
    """`_open_import`'s first steps (tests/test_seed_safety.py:107-117):
    `i`, type the path, `enter`, `s` — no name is typed because a refusing
    import must never reach the "save as" prompt (ruling R15)."""
    await pilot.press("i")
    await pilot.pause()
    app.screen.query_one("#prompt-input", Input).value = str(csv)
    await pilot.press("enter")
    await pilot.pause()
    await pilot.press("s")
    await pilot.pause()


def _painted(app) -> str:
    return app.screen.query_one("#import-preview-canvas", Static).render().plain


async def _push_preview(app, pilot, csv: Path) -> None:
    graph = preview_csv(csv)
    app.push_screen(_ImportPreviewScreen(graph, csv))
    await pilot.pause()


# ---------------------------------------------------------------------------
# LLR-CSV.2.1 — preview_csv records every slug collision with its source rows


def test_preview_csv_records_collisions(tmp_path):
    # The perf evidence CSV (CRLF): rows 5 and 6, raw ids as typed.
    graph = preview_csv(_evidence_csv(tmp_path))
    assert _collisions(graph) == {"a-b": ((5, "a-b"), (6, "A B"))}

    # Blank line in the middle: `csv.DictReader.line_num` counts it, so the
    # colliding rows are 4 and 5, not 3 and 4.
    blank = _write_csv(
        tmp_path / "blank.csv",
        "id,title,parent\np1,First,\n\na-b,First,p1\nA B,Second,p1\n",
    )
    graph = preview_csv(blank)
    assert _collisions(graph) == {"a-b": ((4, "a-b"), (5, "A B"))}

    # Three-way collision on the same slug, ids as typed.
    three = _write_csv(
        tmp_path / "three.csv",
        "id,title,parent\ndup,One,\nDUP,Two,\nDup,Three,\np1,P1,dup\n",
    )
    graph = preview_csv(three)
    assert _collisions(graph) == {
        "dup": ((2, "dup"), (3, "DUP"), (4, "Dup")),
    }

    # Auto-id collision: two empty-id rows share the title slug.
    auto = _write_csv(
        tmp_path / "auto.csv",
        "id,title,parent\np1,P1,\np2,P2,\n,Same,p1\n,Same,p2\n",
    )
    graph = preview_csv(auto)
    assert _collisions(graph) == {"same": ((4, "Same"), (5, "Same"))}

    # Collisions that violate NO loader rule are still recorded (ruling R1).
    parentless = _write_csv(
        tmp_path / "parentless.csv",
        "id,title,parent\na-b,First,\nA B,Second,\n",
    )
    graph = preview_csv(parentless)
    assert _collisions(graph) == {"a-b": ((2, "a-b"), (3, "A B"))}
    assert graph.multi_parent_ids() == []

    mixed = _write_csv(
        tmp_path / "mixed.csv",
        "id,title,parent\nroot,Root,\na-b,First,\nA B,Second,root\n",
    )
    graph = preview_csv(mixed)
    assert _collisions(graph) == {"a-b": ((3, "a-b"), (4, "A B"))}
    assert graph.multi_parent_ids() == []

    # Non-colliding fixtures record nothing.
    clean = _write_csv(
        tmp_path / "clean.csv",
        "id,title,parent\nroot,Root,\nchild,Child,root\n",
    )
    assert preview_csv(clean).csv_collisions == []
    single = _write_csv(tmp_path / "single.csv", "id,title,parent\nonly,Only,\n")
    assert preview_csv(single).csv_collisions == []
    (tmp_path / "empty.csv").write_text("", encoding="utf-8")
    assert preview_csv(tmp_path / "empty.csv").csv_collisions == []


# ---------------------------------------------------------------------------
# LLR-CSV.2.2 — the refusal panel paints the exact sentence


async def test_at_073_preview_names_the_colliding_rows(tmp_path):
    csv = _evidence_csv(tmp_path)
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await pilot.press("i")
        await pilot.pause()
        app.screen.query_one("#prompt-input", Input).value = str(csv)
        await pilot.press("enter")
        await pilot.pause()

        assert isinstance(app.screen, _ImportPreviewScreen)
        painted = _painted(app)
        # Header and sentence asserted together (ruling R10).
        assert "could not draw the preview" in painted
        assert PINNED_SENTENCE in painted


async def test_empty_csv_panel_renders_no_sentence(tmp_path):
    csv = tmp_path / "empty.csv"
    csv.write_text("", encoding="utf-8")
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _push_preview(app, pilot, csv)
        painted = _painted(app)
        assert "could not draw the preview" not in painted
        assert "collapse into the node id" not in painted


async def test_cycle_csv_paints_the_neutral_cycle_sentence(tmp_path):
    csv = _write_csv(
        tmp_path / "cyclic.csv",
        "id,title,parent\na,A,c\nb,B,a\nc,C,b\n",
    )
    graph = preview_csv(csv)
    cycle = graph.find_cycle()
    assert cycle is not None
    expected = (
        f"the import builds a cycle ({' → '.join(cycle)}); a saved map must "
        "be a tree, so fix the parent references and import again."
    )
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _push_preview(app, pilot, csv)
        painted = _painted(app)
        assert "could not draw the preview" in painted
        assert expected in painted

    # Self-parent via the parent column rides the same neutral sentence.
    csv = _write_csv(tmp_path / "self.csv", "id,title,parent\na,A,a\n")
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _push_preview(app, pilot, csv)
        assert "the import builds a cycle (a → a); a saved map must be a " in _painted(app)


async def test_three_way_collision_uses_list_grammar(tmp_path):
    csv = _write_csv(
        tmp_path / "three.csv",
        "id,title,parent\ndup,One,\nDUP,Two,\nDup,Three,\np1,P1,dup\n",
    )
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _push_preview(app, pilot, csv)
        painted = _painted(app)
        assert "rows 2, 3 and 4" in painted
        assert "(ids 'dup', 'DUP' and 'Dup') collapse into the node id 'dup'" in painted
        assert COLLISION_TAIL in painted


async def test_colliding_cyclic_csv_paints_the_collision_sentence(tmp_path):
    """Precedence (ruling R3/R13): the evidence CSV's graph is cyclic AND
    records a collision — the COLLISION sentence wins at the preview."""
    csv = _evidence_csv(tmp_path)
    assert preview_csv(csv).find_cycle() is not None
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _push_preview(app, pilot, csv)
        painted = _painted(app)
        assert PINNED_SENTENCE in painted
        assert "the import builds a cycle" not in painted


async def test_markup_in_id_is_painted_verbatim(tmp_path):
    """C8: a markup-shaped id is painted as plain text, not interpreted."""
    csv = _write_csv(
        tmp_path / "markup.csv",
        "id,title,parent\n[bold]x[/bold],One,\n[BOLD]X[/BOLD],Two,\n",
    )
    graph = preview_csv(csv)
    assert _collisions(graph) == {
        "bold-x-bold": ((2, "[bold]x[/bold]"), (3, "[BOLD]X[/BOLD]"))
    }
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _push_preview(app, pilot, csv)
        painted = _painted(app)
        assert "id '[bold]x[/bold]'" in painted
        assert "id '[BOLD]X[/BOLD]'" in painted


# ---------------------------------------------------------------------------
# LLR-CSV.2.3 — the preview save refuses a colliding import at the `s` keypress


async def test_at_072_refused_save_toasts_and_writes_nothing(tmp_path):
    csv = _evidence_csv(tmp_path)
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        notices = _capture_notices(app)
        await pilot.press("i")
        await pilot.pause()
        app.screen.query_one("#prompt-input", Input).value = str(csv)
        await pilot.press("enter")
        await pilot.pause()
        before = _digests(app.store.workspace)
        await pilot.press("s")
        await pilot.pause()

        assert isinstance(app.screen, _ImportPreviewScreen)
        hits = [n for n, kw in notices if n == PINNED_TOAST]
        assert hits, notices
        kw = next(kw for n, kw in notices if n == PINNED_TOAST)
        assert kw.get("severity") == "error"
        assert kw.get("markup") is False
        after = _digests(app.store.workspace)
        assert after == before, "a refused save changed the workspace"
        assert not [n for n in after if n.endswith((".mmd", "_nodos.yml"))]


async def test_at_072b_parentless_slug_collision_refuses_save(tmp_path):
    """Two parentless rows sharing one slug — violates NO loader rule; the
    record-keyed refusal still fires at the `s` keypress (ruling R1)."""
    csv = _write_csv(
        tmp_path / "parentless.csv",
        "id,title,parent\na-b,First,\nA B,Second,\n",
    )
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        notices = _capture_notices(app)
        before = _digests(app.store.workspace)
        await _import_and_press_save(app, pilot, csv)

        assert isinstance(app.screen, _ImportPreviewScreen)
        assert any(n == PINNED_TOAST for n, _ in notices), notices
        assert _digests(app.store.workspace) == before


async def test_at_072c_mixed_parentage_slug_collision_refuses_save(tmp_path):
    """One parented row + one parentless row sharing one slug."""
    csv = _write_csv(
        tmp_path / "mixed.csv",
        "id,title,parent\nroot,Root,\na-b,First,\nA B,Second,root\n",
    )
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        notices = _capture_notices(app)
        before = _digests(app.store.workspace)
        await _import_and_press_save(app, pilot, csv)

        assert isinstance(app.screen, _ImportPreviewScreen)
        assert any(n == PINNED_TOAST for n, _ in notices), notices
        assert _digests(app.store.workspace) == before


async def test_at_072d_auto_id_slug_collision_refuses_save(tmp_path):
    """Two empty-id rows with the same title (auto-id collision)."""
    csv = _write_csv(
        tmp_path / "auto.csv",
        "id,title,parent\np1,P1,\np2,P2,\n,Same,p1\n,Same,p2\n",
    )
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        notices = _capture_notices(app)
        before = _digests(app.store.workspace)
        await _import_and_press_save(app, pilot, csv)

        assert isinstance(app.screen, _ImportPreviewScreen)
        assert any(n == PINNED_TOAST for n, _ in notices), notices
        assert _digests(app.store.workspace) == before


# ---------------------------------------------------------------------------
# HLR-CSV.3 / LLR-CSV.3.1 — the working path is untouched (AT-074)


async def test_at_074_valid_csv_saves_and_reopens_identical(tmp_path):
    csv = _write_csv(
        tmp_path / "valid.csv",
        "id,title,parent\nroot,Root,\nmid,Middle,root\nleaf,Leaf,mid\n",
    )
    ws = tmp_path / "ws"
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        notices = _capture_notices(app)
        await _open_import(app, pilot, "imported", csv)
        await pilot.pause()

        assert (ws / "imported.mmd").is_file()
        assert (ws / "imported_nodos.yml").is_file()
        assert not any(n == PINNED_TOAST for n, _ in notices), notices

    expected = preview_csv(csv)
    loaded = MapStore(ws).load("imported")
    assert set(loaded.nodes) == set(expected.nodes)
    assert {(e.parent_id, e.child_id) for e in loaded.edges} == {
        (e.parent_id, e.child_id) for e in expected.edges
    }
    assert loaded.root_id == expected.root_id
    assert {nid: n.ficha.title for nid, n in loaded.nodes.items()} == {
        nid: n.ficha.title for nid, n in expected.nodes.items()
    }
