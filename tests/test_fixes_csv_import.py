"""Fixes batch increment 001: B-115 (blank parent / empty slug) and B-116 (root by parentage).

LLR-FX.1.2 (blank-first parent read), LLR-FX.1.3 (`row-N` for an id with no slug
characters), LLR-FX.2.1 (root chosen by parentage), LLR-FX.2.2 (no cycle from the
attach step, any row order), TC-FX-S1 (hostile cells), and the acceptance nodes
AT-084 / AT-085 driven through the real import keys and asserted on the painted
preview frame (C-32), never on the arguments of an `update()` call.
"""
import itertools
import re
from pathlib import Path

from textual.widgets import Input, Static

from mapper.app import MapperApp
from mapper.import_csv import preview_csv
from mapper.mermaid import dump, parse
from mapper.store import MapStore
from tests.test_seed_safety import _open_import

SIZE = (118, 34)


def _csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "in.csv"
    path.write_text(text, encoding="utf-8")
    return path


def _edges(graph) -> set[tuple[str, str]]:
    return {(e.parent_id, e.child_id) for e in graph.edges}


def _titles(graph) -> dict[str, str]:
    return {nid: n.ficha.title for nid, n in graph.nodes.items()}


def _painted(app) -> str:
    return app.screen.query_one("#import-preview-canvas", Static).render().plain


async def _open_preview(app, pilot, csv: Path) -> None:
    await pilot.press("i")
    await pilot.pause()
    app.screen.query_one("#prompt-input", Input).value = str(csv)
    await pilot.press("enter")
    await pilot.pause()


# ---------------------------------------------------------------------------
# LLR-FX.1.2 — the parent cell is read blank-first


def test_blank_parent_cell_is_a_root_candidate_not_a_reference_to_n(tmp_path):
    # whitespace-only cell: no parent, no park prefix, edge r -> k only
    g = preview_csv(_csv(tmp_path, "id,title,parent\nr,R,   \nk,K,r\n"))
    assert set(g.nodes) == {"r", "k"}
    assert _edges(g) == {("r", "k")}
    assert _titles(g)["r"] == "R"

    # a root literally named N is no longer a self-cycle with its child
    g = preview_csv(_csv(tmp_path, "id,title,parent\nN,N,\nk,K,n\n"))
    assert _edges(g) == {("n", "k")}
    assert g.find_cycle() is None

    # empty cells: three top-level rows, none attached to a phantom `n`
    g = preview_csv(_csv(tmp_path, "id,title,parent\na,A,\nb,B,\nc,C,\n"))
    assert "n" not in g.nodes
    assert all("n" not in (e.parent_id, e.child_id) for e in g.edges)


def test_punctuation_only_parent_cell_parks_the_row(tmp_path):
    g = preview_csv(_csv(tmp_path, "id,title,parent\nr,R,\nk,K,!!!\n"))
    assert _titles(g)["k"] == "? K"
    assert _edges(g) == {("r", "k")}
    assert "n" not in g.nodes

    # listed BEFORE the real root: an unreadable parent still parks the row, so
    # it cannot be elected root (it is not "no parent", it is a missing parent)
    g = preview_csv(_csv(tmp_path, "id,title,parent\nk,K,!!!\nr,R,\n"))
    assert g.root_id == "r"
    assert _edges(g) == {("r", "k")}
    assert _titles(g)["k"] == "? K"


# ---------------------------------------------------------------------------
# LLR-FX.1.3 — an id with no slug characters imports as row-N


def test_id_with_no_slug_characters_becomes_row_n(tmp_path):
    g = preview_csv(_csv(tmp_path, "id,title,parent\n!!!,Bang,\n"))
    assert set(g.nodes) == {"row-1"}
    assert _titles(g)["row-1"] == "Bang"

    # no title: titled by the typed text; two such rows, no collision
    g = preview_csv(_csv(tmp_path, "id,title,parent\n!!!,,\n!!!,,\n"))
    assert set(g.nodes) == {"row-1", "row-2"}
    assert _titles(g)["row-1"] == "!!!"
    assert g.csv_collisions == []

    # empty id + punctuation-only title
    g = preview_csv(_csv(tmp_path, "id,title,parent\n,!!!,\n"))
    assert set(g.nodes) == {"row-1"}
    assert _titles(g)["row-1"] == "!!!"

    # empty-slug row followed by an empty-id, empty-title row
    g = preview_csv(_csv(tmp_path, "id,title,parent\n!!!,Bang,\n,,\n"))
    assert set(g.nodes) == {"row-1", "row-2"}

    # a title-derived id does not advance the shared counter
    g = preview_csv(_csv(tmp_path, "id,title,parent\n,Alpha,\n,,\n"))
    assert set(g.nodes) == {"alpha", "row-1"}

    # an operator-typed row-1 after an auto row-1 is a recorded collision
    g = preview_csv(_csv(tmp_path, "id,title,parent\n!!!,Bang,\nrow-1,Typed,\n"))
    assert [
        (c.slug, [(r.line_no, r.raw_id) for r in c.rows]) for c in g.csv_collisions
    ] == [("row-1", [(2, "!!!"), (3, "row-1")])]


# ---------------------------------------------------------------------------
# LLR-FX.2.1 / FX.2.2 — root by parentage, never by row order


def test_root_child_listed_before_root(tmp_path):
    g = preview_csv(_csv(tmp_path, "id,title,parent\nchild,Child,root\nroot,Root,\n"))
    assert g.root_id == "root"
    assert _edges(g) == {("root", "child")}
    assert g.find_cycle() is None
    assert _titles(g)["root"] == "Root"


def test_root_grandchild_listed_first(tmp_path):
    g = preview_csv(_csv(tmp_path, "id,title,parent\nc,C,b\nb,B,a\na,A,\n"))
    assert g.root_id == "a"
    assert _edges(g) == {("b", "c"), ("a", "b")}


def test_root_unknown_parent_row_before_the_real_root_is_not_root(tmp_path):
    # `p` is parked (its parent is unknown) and listed first: it must not win
    g = preview_csv(_csv(tmp_path, "id,title,parent\np,P,ghost\nr,R,\n"))
    assert g.root_id == "r"
    assert _edges(g) == {("r", "p")}
    assert _titles(g)["p"] == "? P"


def test_root_second_parentless_row_is_attached_and_parked(tmp_path):
    g = preview_csv(_csv(tmp_path, "id,title,parent\nx,X,\nk,K,y\ny,Y,\n"))
    assert g.root_id == "x"
    assert _edges(g) == {("y", "k"), ("x", "y")}
    assert _titles(g)["y"] == "? Y"


def test_root_all_parents_unknown_keeps_first_row_parked(tmp_path):
    g = preview_csv(_csv(tmp_path, "id,title,parent\na,A,ghost\nb,B,ghost\n"))
    assert g.root_id == "a"
    assert _titles(g)["a"] == "? A"
    assert _edges(g) == {("a", "b")}


def test_root_ring_leaves_first_row_and_names_the_cycle(tmp_path):
    g = preview_csv(_csv(tmp_path, "id,title,parent\na,A,c\nb,B,a\nc,C,b\n"))
    assert g.root_id == "a"
    assert g.find_cycle() == ["a", "b", "c", "a"]


def test_root_ring_beside_a_root(tmp_path):
    g = preview_csv(_csv(tmp_path, "id,title,parent\na,A,c\nr,R,\nc,C,a\n"))
    assert g.root_id == "r"
    assert g.find_cycle() == ["a", "c", "a"]


def test_root_from_depth_column_alone(tmp_path):
    g = preview_csv(
        _csv(tmp_path, "id,title,parent,depth\na,A,,0\nb,B,,1\nc,C,,2\n")
    )
    assert g.root_id == "a"
    assert _edges(g) == {("a", "b"), ("b", "c")}
    assert not any(t.startswith("? ") for t in _titles(g).values())


def test_permutation_of_rows_never_changes_the_tree(tmp_path):
    rows = ["r,R,", "a,A,r", "b,B,r", "c,C,a"]
    seen = set()
    for perm in itertools.permutations(rows):
        g = preview_csv(_csv(tmp_path, "id,title,parent\n" + "\n".join(perm) + "\n"))
        assert g.find_cycle() is None, perm
        seen.add((frozenset(g.nodes), frozenset(_edges(g)), g.root_id))
    assert seen == {
        (frozenset("rabc"), frozenset({("r", "a"), ("r", "b"), ("a", "c")}), "r")
    }


# ---------------------------------------------------------------------------
# TC-FX-S1 — hostile cells never reach the graph as an empty or unsafe id


def test_hostile_cells_yield_only_word_ids_and_survive_the_text_round_trip(tmp_path):
    hostile = ["]|x", "--> y", "#93;", "]", "", "a" * 5000]
    lines = ["id,title,parent"]
    for i, cell in enumerate(hostile):
        lines.append(f'"{cell}",T{i},')
    g = preview_csv(_csv(tmp_path, "\n".join(lines) + "\n"))
    assert g.nodes
    assert all(re.fullmatch(r"[\w-]+", nid) for nid in g.nodes)
    again = parse(dump(g))
    assert set(again.nodes) == set(g.nodes)


# ---------------------------------------------------------------------------
# AT-084 / AT-085 — through the real import keys


async def test_at_084_empty_parent_cells_are_roots_not_node_n(tmp_path):
    """AT-084: the import preview of the empty-parent CSV paints no node `n`, the first
    row is the root with no `? ` prefix, the unreadable id imports as `row-1`."""
    csv = _csv(tmp_path, "id,title,parent\nalpha,Alpha,\nbeta,Beta,\n!!!,Bang,\n")
    app = MapperApp(tmp_path / "ws")
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _open_preview(app, pilot, csv)
        painted = _painted(app)
        assert "3 nodes" in painted
        assert "▐ Alpha" in painted and "? Alpha" not in painted
        assert "▐ ? Beta" in painted and "▐ ? Bang" in painted
        assert "▐ n" not in painted and "? n" not in painted
    g = preview_csv(csv)
    assert set(g.nodes) == {"alpha", "beta", "row-1"}
    assert g.root_id == "alpha"
    assert all("n" not in (e.parent_id, e.child_id) for e in g.edges)

    # the non-ASCII arm: exactly what slugify does on the base tree
    uni = _csv(tmp_path, "id,title,parent\nniño,Niño,\n")
    assert set(preview_csv(uni).nodes) == {"niño"}


async def test_at_085_child_listed_before_root_imports_saves_and_reopens(tmp_path):
    """AT-085: the child-first CSV shows no cycle sentence, saves under a typed name
    and re-opens as a two-node tree rooted at `root`."""
    csv = _csv(tmp_path, "id,title,parent\nchild,Child,root\nroot,Root,\n")
    ws = tmp_path / "ws"
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _open_preview(app, pilot, csv)
        painted = _painted(app)
        assert "cycle" not in painted.lower()
        assert "▐ Root" in painted and "? Root" not in painted
        assert "▐ Child" in painted
    app = MapperApp(ws)
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        await _open_import(app, pilot, "imported", csv)
        await pilot.pause()
    assert (ws / "imported.mmd").is_file()
    loaded = MapStore(ws).load("imported")
    assert loaded.root_id == "root"
    assert set(loaded.nodes) == {"root", "child"}
    assert _edges(loaded) == {("root", "child")}
