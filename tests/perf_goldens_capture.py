"""Behaviour-golden capture for batch `2026-10-10-perf-batch` (trunk step PERFG0).

Run from the worktree root:

    python -B tests/perf_goldens_capture.py

Regenerates every behaviour golden the batch pins, deterministically, from the
CURRENT product, into `tests/goldens/perf/` and rewrites `MANIFEST.json` (per
golden: case id, base SHA `5cde04e`, sha256).  The golden provenance protocol
(PDR `2026-10-10-perf-batch` §7, the AT-065 precedent) requires these bytes to
be captured on the BASE product BEFORE the lanes fork; the manifest test
(`tests/test_perf_goldens_manifest.py`) turns any later drift RED.

What is pinned:

* Lane R render grid (LLR-PERF.1.3) — `LayeredRenderer.render(graph, state)`
  painted plain text over: empty, single node, deep chain 5000, wide 2000,
  wide 6000, forest, a folded subtree and a panned ViewState, each at
  118x34 and 87x34 (`render/<shape>_<w>x<h>.txt`).
* AT-075 / AT-075b (HLR-PERF.1) — the settled `#map-canvas` painted rows of a
  wide-2000 map driven through the real app (`MapperApp` + `run_test` at
  118x34, real keys only): open, five selection keypresses (`l,j,j,j,j`),
  then an archive (`x`, `y`) and one more keypress
  (`at075_075b_wide2000_118x34.txt`).  The canvas region is read from the
  screen compositor's strips — the same seam `tests/test_mod_parity.py`
  documents — so no chrome, toast or identity cell can make the pin volatile.
* Lane M dump grid (LLR-PERF.2.2) — `mermaid.dump` bytes for the three
  committed fixtures (round-tripped through `parse`), wide 6000, forest,
  empty, single node and a dangling-edge graph (`dump/*.mmd`).
* AT-076 (HLR-PERF.2) — the saved `.mmd` bytes AFTER an `a` add_child on a
  saved wide-6000 map, driven with real keys through the real app
  (`at076_saved_wide6000_after_add_child.mmd`).

This file is named so pytest never collects it (no `test_` prefix); it is a
script.  The graph builders live here, importable, so the lane tests rebuild
EXACTLY the graphs the goldens were painted from.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from textual.widgets import Static  # noqa: E402

from mapper.mermaid import dump, parse  # noqa: E402
from mapper.model import Edge, Ficha, Graph, Node  # noqa: E402
from mapper.views.layered import LayeredRenderer  # noqa: E402
from mapper.views.state import ViewState  # noqa: E402

GOLDEN_DIR = REPO_ROOT / "tests" / "goldens" / "perf"
BASE_SHA = "5cde04e"
FIXTURES = REPO_ROOT / "fixtures"

# The grid sizes the requirements name (AT-075's terminal; LLR-PERF.1.3).
GRID_SIZES = ((118, 34), (87, 34))


# ---------------------------------------------------------------------------
# Graph builders — deterministic, fixed ids/titles, no timestamps.
# ---------------------------------------------------------------------------

def build_empty() -> Graph:
    """The empty map (`root_id None`) the loader can produce."""
    return Graph()


def build_single() -> Graph:
    """One node, no edges."""
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="raiz", meta="meta raiz")))
    return g


def build_deep_chain(n: int = 5000) -> Graph:
    """A single chain `n0000 -> n0001 -> ... -> n{N-1}` (depth-N boundary)."""
    g = Graph()
    g.add_node(Node(id="n0000", ficha=Ficha(title="nodo 0000", meta="m0000")))
    for i in range(1, n):
        g.add_node(Node(id=f"n{i:04d}", ficha=Ficha(title=f"nodo {i:04d}", meta=f"m{i:04d}")))
        g.add_edge(Edge(parent_id=f"n{i - 1:04d}", child_id=f"n{i:04d}"))
    return g


def build_wide(n: int) -> Graph:
    """`root` with `n - 1` direct children `c0001 .. c{n-1}` (breadth-N)."""
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="raiz", meta="meta raiz")))
    for i in range(1, n):
        g.add_node(Node(id=f"c{i:04d}", ficha=Ficha(title=f"hijo {i:04d}", meta=f"m{i:04d}")))
        g.add_edge(Edge(parent_id="root", child_id=f"c{i:04d}"))
    return g


def build_forest() -> Graph:
    """Two parentless trees side by side (>= 2 parentless nodes)."""
    g = Graph()
    g.add_node(Node(id="raiz-a", ficha=Ficha(title="arbol a", meta="meta a")))
    g.add_node(Node(id="raiz-b", ficha=Ficha(title="arbol b", meta="meta b")))
    for i in range(3):
        g.add_node(Node(id=f"a-{i}", ficha=Ficha(title=f"hoja a{i}", meta=f"ma{i}")))
        g.add_edge(Edge(parent_id="raiz-a", child_id=f"a-{i}"))
    g.add_node(Node(id="b-0", ficha=Ficha(title="hoja b0", meta="mb0")))
    g.add_edge(Edge(parent_id="raiz-b", child_id="b-0"))
    return g


def build_fold_tree() -> Graph:
    """Root with three children; `mid` has three children of its own."""
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="raiz", meta="meta raiz")))
    for nid, title in (("left", "rama izq"), ("mid", "rama media"), ("right", "rama der")):
        g.add_node(Node(id=nid, ficha=Ficha(title=title, meta=f"meta {nid}")))
        g.add_edge(Edge(parent_id="root", child_id=nid))
    for i in range(3):
        g.add_node(Node(id=f"mid-{i}", ficha=Ficha(title=f"media {i}", meta=f"mm{i}")))
        g.add_edge(Edge(parent_id="mid", child_id=f"mid-{i}"))
    return g


def build_bush() -> Graph:
    """Root, eight children, eight grandchildren each — deep/wide enough to pan."""
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="raiz", meta="meta raiz")))
    for i in range(8):
        cid = f"br{i}"
        g.add_node(Node(id=cid, ficha=Ficha(title=f"rama {i}", meta=f"mb{i}")))
        g.add_edge(Edge(parent_id="root", child_id=cid))
        for j in range(8):
            gid = f"br{i}-{j}"
            g.add_node(Node(id=gid, ficha=Ficha(title=f"hoja {i}-{j}", meta=f"m{i}{j}")))
            g.add_edge(Edge(parent_id=cid, child_id=gid))
    return g


def build_dangling() -> Graph:
    """An edge whose child endpoint is missing from `nodes` — never written,
    but its ids still count toward dump's incident membership."""
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="raiz")))
    g.add_node(Node(id="hijo-1", ficha=Ficha(title="hijo uno")))
    g.add_edge(Edge(parent_id="root", child_id="hijo-1"))
    g.add_edge(Edge(parent_id="hijo-1", child_id="fantasma"))
    return g


# ---------------------------------------------------------------------------
# Lane R render grid (LLR-PERF.1.3) — painted plain text, direct renderer.
# ---------------------------------------------------------------------------

def _grid_state(shape: str, w: int, h: int) -> ViewState:
    if shape == "fold":
        # `mid`'s whole subtree folds away: the fold pill arm of the grid.
        return ViewState(w=w, h=h, folded=frozenset({"mid"}))
    if shape == "panned":
        # A real pan off the origin over a map larger than the frame.
        return ViewState(w=w, h=h, pan_x=20, pan_y=6)
    return ViewState(w=w, h=h)


def render_grid_cases():
    """Yield `(case_id, relative_path, text)` for every render-grid golden."""
    shapes = {
        "empty": build_empty,
        "single": build_single,
        "deep5000": build_deep_chain,
        "wide2000": lambda: build_wide(2000),
        "wide6000": lambda: build_wide(6000),
        "forest": build_forest,
        "fold": build_fold_tree,
        "panned": build_bush,
    }
    renderer = LayeredRenderer()
    for shape, builder in shapes.items():
        for w, h in GRID_SIZES:
            text = renderer.render(builder(), _grid_state(shape, w, h)).plain
            yield (
                f"LLR-PERF.1.3.render-grid.{shape}@{w}x{h}",
                f"render/{shape}_{w}x{h}.txt",
                text,
            )


# ---------------------------------------------------------------------------
# Lane M dump grid (LLR-PERF.2.2) — .mmd bytes.
# ---------------------------------------------------------------------------

def dump_cases():
    """Yield `(case_id, relative_path, text)` for every dump golden."""
    for name in ("legacy", "anidado", "truncado"):
        src = (FIXTURES / f"{name}.mmd").read_text(encoding="utf-8")
        yield (
            f"LLR-PERF.2.2.dump.fixture-{name}",
            f"dump/{name}.mmd",
            dump(parse(src)),
        )
    yield ("LLR-PERF.2.2.dump.wide6000", "dump/wide6000.mmd", dump(build_wide(6000)))
    yield ("LLR-PERF.2.2.dump.forest", "dump/forest.mmd", dump(build_forest()))
    yield ("LLR-PERF.2.2.dump.empty", "dump/empty.mmd", dump(Graph()))
    yield ("LLR-PERF.2.2.dump.single", "dump/single.mmd", dump(build_single()))
    yield (
        "LLR-PERF.2.2.dump.dangling-edge",
        "dump/dangling.mmd",
        dump(build_dangling()),
    )


# ---------------------------------------------------------------------------
# App-driven captures (AT-075/075b, AT-076) — real keys, no shortcuts.
# ---------------------------------------------------------------------------

def _canvas_lines(screen) -> list[str]:
    """The settled `#map-canvas` region as painted plain rows.

    Read from the screen compositor's strips (the seam `tests/test_mod_parity.py`
    documents), clipped to the canvas widget's region: chrome, toasts, the rail
    identity row and the pagination strip cannot leak into the pin.
    """
    region = screen.query_one("#map-canvas", Static).region
    strips = screen._compositor.render_strips()  # noqa: SLF001
    lines = []
    for strip in strips[region.y : region.y + region.height]:
        row = "".join(seg.text for seg in strip)
        lines.append(row[region.x : region.x + region.width].rstrip())
    return lines


async def capture_at075_075b(workspace: Path) -> str:
    """AT-075/AT-075b: wide-2000 at 118x34 through `MapperApp`, real keys.

    One canvas capture per step: settled open, each of the five selection
    keypresses (`l,j,j,j,j`), then archive (`x`, `y`) and one more keypress.
    """
    from mapper.app import MapperApp
    from mapper.screens.prompt import _ConfirmScreen
    from tests.test_draft_save import _open, _press

    app = MapperApp(workspace)
    blocks: list[tuple[str, list[str]]] = []
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("perf2000", build_wide(2000))
        screen = await _open(app, pilot, "perf2000", cursor="root")
        blocks.append((f"step: open (cursor {screen.nav.cursor})", _canvas_lines(screen)))
        for key in ("l", "j", "j", "j", "j"):
            await _press(pilot, key)
            blocks.append(
                (f"step: {key} (cursor {screen.nav.cursor})", _canvas_lines(screen))
            )
        await _press(pilot, "x")
        assert isinstance(app.screen, _ConfirmScreen), type(app.screen).__name__
        await _press(pilot, "y")
        await _press(pilot, "l")
        blocks.append(
            (f"step: archive x y then l (cursor {screen.nav.cursor})",
             _canvas_lines(screen)),
        )
    out: list[str] = []
    for title, lines in blocks:
        out.append(f"=== {title} ===")
        out.extend(lines)
    return "\n".join(out) + "\n"


async def capture_at076(workspace: Path) -> bytes:
    """AT-076: the saved `.mmd` bytes after an `a` add_child on a saved wide-6000
    map — a real persisting gesture through `MapperApp`, real keys only."""
    from mapper.app import MapperApp
    from mapper.screens.prompt import _PromptScreen
    from tests.test_draft_save import _open, _press

    app = MapperApp(workspace)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("perf6000", build_wide(6000))
        await _open(app, pilot, "perf6000", cursor="root")
        await _press(pilot, "a")
        assert isinstance(app.screen, _PromptScreen), type(app.screen).__name__
        await pilot.press(*"hijoperf")
        await pilot.press("enter")
        await pilot.pause()
        return (workspace / "perf6000.mmd").read_bytes()


# ---------------------------------------------------------------------------
# Capture driver.
# ---------------------------------------------------------------------------

def _write(relative: str, content: str | bytes) -> None:
    path = GOLDEN_DIR / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8", newline="\n")


def main() -> None:
    cases: list[tuple[str, str]] = []  # (case id, relative path)
    for case_id, relative, text in render_grid_cases():
        _write(relative, text)
        cases.append((case_id, relative))
        print(f"captured {relative}")
    for case_id, relative, text in dump_cases():
        _write(relative, text)
        cases.append((case_id, relative))
        print(f"captured {relative}")

    with tempfile.TemporaryDirectory(dir=REPO_ROOT) as tmp:
        workspace = Path(tmp)
        at075 = asyncio.run(capture_at075_075b(workspace))
        _write("at075_075b_wide2000_118x34.txt", at075)
        cases.append(("AT-075+AT-075b.keypress-wide2000@118x34",
                      "at075_075b_wide2000_118x34.txt"))
        print("captured at075_075b_wide2000_118x34.txt")

        at076 = asyncio.run(capture_at076(workspace))
        _write("at076_saved_wide6000_after_add_child.mmd", at076)
        cases.append(("AT-076.saved-wide6000-after-add-child",
                      "at076_saved_wide6000_after_add_child.mmd"))
        print("captured at076_saved_wide6000_after_add_child.mmd")

    manifest = {
        "base_sha": BASE_SHA,
        "captured_by": "tests/perf_goldens_capture.py",
        "goldens": [
            {
                "case": case_id,
                "file": relative,
                "base_sha": BASE_SHA,
                "sha256": hashlib.sha256((GOLDEN_DIR / relative).read_bytes()).hexdigest(),
            }
            for case_id, relative in cases
        ],
    }
    (GOLDEN_DIR / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nwrote {GOLDEN_DIR.relative_to(REPO_ROOT)}/MANIFEST.json "
          f"({len(cases)} goldens, base {BASE_SHA})")


if __name__ == "__main__":
    main()
