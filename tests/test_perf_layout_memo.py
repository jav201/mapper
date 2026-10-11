"""AT-075b / LLR-PERF.1.2 / LLR-PERF.1.3 (batch `2026-10-10-perf-batch`, Inc-R2, Lane R).

Lane R's second increment memoises the UNSCALED `_tree_layout` (slot cx and
level per node) on the `LayeredRenderer` INSTANCE, keyed by strong references
compared with `is` -- the `Graph` object, its `edges` list (+len), its `nodes`
dict (+len), `root_id` and the hidden (fold) set -- and re-applies the
`card_w`/`gap` scaling on every call.  The memo storage is PASSED INTO
module-level `_geometry` as an argument (ruling R12): there is no module-global
memo state.  The memo-miss spy is the named instance counter
`LayeredRenderer._layout_misses`, incremented at the hit check inside
`_geometry` (`_tree_layout` itself runs ~10x per two renders,
`evidence/perf0c-nav.transcript:44`, so invocations are not countable).

What is proven here:

* `test_memo_miss_spy` (LLR-PERF.1.2, layer 0) -- repeated renders of one
  graph cost exactly ONE real layout; every render after the first is a hit.
* `test_at_075b_memo_misses_and_golden` (AT-075b, layer B) -- the scripted
  wide-2000 session through the real app: open + five selection-only keypresses
  (`l,j,j,j,j`) cost exactly 1 miss; each painted step byte-equals the golden
  pinned at base SHA `5cde04e`; archiving a subtree with real keys costs
  exactly 1 more miss.
* `test_memo_invalidation_arms[resize|title|fold|focus|undo|add_child|round_trip]`
  (LLR-PERF.1.2) -- seven named arms.  `resize` and `title` change only the
  scaling (0 extra misses, repaint byte-identical to a fresh renderer;
  `title`'s compare is renderer-level full text because the canvas region is
  viewport-clipped and header-only for its fixture at 118x34 -- DDR qa MED-2,
  `evidence/ddr2-red.transcript`); `fold`, `focus`, `undo`, `add_child`
  change a layout input (each misses); `round_trip` (outline <-> radial <->
  layered) repaints byte-identically with no extra misses.
* `test_memo_id_reuse` (mutation M-R2d, ruling R13) -- a new `Graph` object
  always misses; with the strong-reference key the memo itself pins the old
  graph, so allocator address reuse cannot fake a hit BY CONSTRUCTION (the
  node documents that and keeps the plain check).
* `test_nodes_writer_census` + `test_nodes_writer_census_in_place_forms[...]`
  (LLR-PERF.1.2 guard, ruling R14) -- Lane R's own AST census on `Graph.nodes`
  dict writers: the declared set is `model.py` `add_node` and
  `screens/map/editing.py` wholesale; every in-place form and the alias form
  are detected (one planted-form RED arm per form, M-R2e).

Negative controls (PDR SS5): M-R2 (drop the memo) -> a miss per keypress ->
AT-075b RED.  M-R2b (never invalidate) -> `fold`/`add_child` arms RED.
M-R2c (cache the SCALED layout) -> `resize`/`title` arms RED.  M-R2d (key on
`id()`) -> `test_memo_id_reuse` RED where the allocator recycles the address.
M-R2e (a new `nodes` writer site) -> the census guard RED.
"""
from __future__ import annotations

import ast
import gc
from pathlib import Path

import pytest
from textual.widgets import Static

from mapper.app import MapperApp
from mapper.screens.prompt import _ConfirmScreen, _PromptScreen
from mapper.views.layered import LayeredRenderer
from mapper.views.state import ViewState

from tests.perf_goldens_capture import (
    GOLDEN_DIR,
    REPO_ROOT,
    _canvas_lines,
    build_fold_tree,
    build_wide,
)
from tests.test_draft_save import _open, _press
from tests.test_perf_paint_clip import _golden_blocks

TERMINAL = (118, 34)
NARROW = (87, 34)
AT075B_GOLDEN = GOLDEN_DIR / "at075_075b_wide2000_118x34.txt"

# A title longer than every other title+meta in `build_fold_tree`, so the
# `widest` scan widens `card_w` (14 -> 26) when it is saved onto the card.
# Typing lands at the end of the field's current value ("rama media"), so the
# saved title is "rama media" + WIDENING_TITLE.
WIDENING_TITLE = "titulo larguisimo que ensancha la tarjeta de verdad"
EDITED_TITLE = "rama media" + WIDENING_TITLE


# ---------------------------------------------------------------------------
# Layer 0: the miss spy on the renderer instance.
# ---------------------------------------------------------------------------

def test_memo_miss_spy():
    """LLR-PERF.1.2: five repeated renders of one graph cost exactly ONE real
    layout computation -- the memo hits on the strong-reference key and only
    the scaling is re-derived per call.  Every render stays byte-identical."""
    graph = build_wide(2000)
    state = ViewState(w=118, h=34)
    renderer = LayeredRenderer()
    texts = {renderer.render(graph, state).plain for _ in range(5)}
    assert renderer._layout_misses == 1, (
        f"5 repeated renders cost {renderer._layout_misses} misses, want 1"
    )
    assert len(texts) == 1, "repeated renders of one state must be byte-identical"

    # A fresh renderer (the import preview builds one per paint) simply misses.
    fresh = LayeredRenderer()
    fresh.render(graph, state)
    assert fresh._layout_misses == 1


# ---------------------------------------------------------------------------
# AT-075b (layer B): the real-app session, miss count + golden bytes.
# ---------------------------------------------------------------------------

async def test_at_075b_memo_misses_and_golden(tmp_path):
    """AT-075b (LLR-PERF.1.2): open + five selection-only keypresses on
    wide-2000 at 118x34 cost exactly 1 memo miss; every painted step byte-equals
    the golden pinned at base SHA `5cde04e`; archiving a subtree with real keys
    (`x`, `y`) and one more keypress costs exactly 1 more miss."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("perf2000", build_wide(2000))
        screen = await _open(app, pilot, "perf2000", cursor="root")
        renderer = screen.renderer
        painted: list[tuple[str, list[str]]] = [
            (f"open (cursor {screen.nav.cursor})", _canvas_lines(screen)),
        ]
        assert renderer._layout_misses == 1, (
            f"open cost {renderer._layout_misses} misses, want exactly 1"
        )
        for key in ("l", "j", "j", "j", "j"):
            await _press(pilot, key)
            painted.append((f"{key} (cursor {screen.nav.cursor})", _canvas_lines(screen)))
        print(f"\nAT-075b memo misses after open + l,j,j,j,j: {renderer._layout_misses}")
        assert renderer._layout_misses == 1, (
            f"five selection-only keypresses cost {renderer._layout_misses} "
            "misses in total, want exactly 1"
        )

        await _press(pilot, "x")
        assert isinstance(app.screen, _ConfirmScreen), type(app.screen).__name__
        await _press(pilot, "y")
        await _press(pilot, "l")
        painted.append(
            (f"archive x y then l (cursor {screen.nav.cursor})", _canvas_lines(screen))
        )
        print(f"AT-075b memo misses after archive + l: {renderer._layout_misses}")
        assert renderer._layout_misses == 2, (
            f"the archive must miss exactly once, got {renderer._layout_misses} "
            "in total, want 2"
        )

    blocks = _golden_blocks(AT075B_GOLDEN.read_text(encoding="utf-8"))
    for title, lines in painted:
        assert blocks.get(title) == lines, (
            f"canvas after {title!r} drifted from the base golden "
            f"{AT075B_GOLDEN.name}"
        )


# ---------------------------------------------------------------------------
# LLR-PERF.1.2: the seven invalidation arms.
# ---------------------------------------------------------------------------

async def _settle_unfocused(app, pilot) -> None:
    """Wait for `_park_focus` so `tab` traversal starts from a settled state
    (the AUTO_FOCUS transient focuses the rail one turn after mount)."""
    for _ in range(40):
        if app.focused is None:
            return
        await pilot.pause()
    raise AssertionError("focus never parked")


async def _arm_resize(tmp_path):
    """`resize`: a window resize changes only the scaling, never the slots.

    App level: `pilot.resize_terminal` fires the real `on_resize` re-render
    through the memo -- 0 extra misses.  (No byte comparison at the app level:
    region visibility is applied at mount, so a post-resize layout need not
    byte-match a fresh mount at the target size -- that behaviour predates this
    increment and is out of Lane R's file set.)  Renderer level: rendering the
    same graph at a second size costs 0 extra misses and byte-equals a fresh
    renderer's paint -- the scaling re-applied per call."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("rs", build_wide(8))
        screen = await _open(app, pilot, "rs", cursor="root")
        before = screen.renderer._layout_misses
        await pilot.resize_terminal(*NARROW)
        await pilot.pause()
        await pilot.pause()
        assert screen.renderer._layout_misses == before, (
            "a resize re-applies the scaling; the unscaled memo must not miss"
        )

    graph = build_wide(8)
    wide_state = ViewState(w=118, h=34)
    narrow_state = ViewState(w=87, h=34)
    renderer = LayeredRenderer()
    renderer.render(graph, wide_state)
    assert renderer._layout_misses == 1
    narrowed = renderer.render(graph, narrow_state).plain
    assert renderer._layout_misses == 1, (
        "a resize re-applies the scaling; the unscaled memo must not miss"
    )
    fresh = LayeredRenderer().render(graph, narrow_state).plain
    assert narrowed == fresh, (
        "the resized render must byte-equal a fresh renderer's paint"
    )


async def _arm_title(tmp_path):
    """`title`: a ficha title edit that widens `widest` changes only the
    scaling -- 0 extra misses -- and the repaint byte-equals a fresh
    renderer's paint of the saved (post-edit) map.  The byte compare runs at
    RENDERER level (full `render().plain` text at the app's own view state):
    the canvas-region compare is viewport-clipped and, measured at 118x34,
    header-only for this fixture -- blind to exactly the geometry drift M-R2c
    would cause (`evidence/r2-red.transcript` §5, `evidence/ddr2-red.transcript`)."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("tt", build_fold_tree())
        screen = await _open(app, pilot, "tt", cursor="mid")
        await _settle_unfocused(app, pilot)
        before = screen.renderer._layout_misses
        # Real keys only: the focus chain at 118x34 is
        # [map-rail, insp-title, insp-state, insp-notes] (measured,
        # `tests/test_app.py::test_llr_cnv_3_1_focus_owner_tracks_the_real_focus`).
        await _press(pilot, "tab")
        await _press(pilot, "tab")
        assert app.focused is not None and app.focused.id == "insp-title", (
            "two tabs must land on the title field"
        )
        await pilot.press(*WIDENING_TITLE)
        await pilot.pause()
        await _press(pilot, "ctrl+s")
        await _press(pilot, "escape")
        edited = _canvas_lines(screen)
        assert screen.renderer._layout_misses == before, (
            "a widening title edit re-applies the scaling; the unscaled memo "
            "must not miss"
        )
        # Renderer-level pin: the region-clipped canvas compare below is blind
        # to geometry that never reaches the viewport -- measured, at 118x34
        # this fixture's canvas is header-only, so M-R2c (cache the SCALED
        # layout) stayed green here while reddening `resize`
        # (`evidence/r2-red.transcript` §5).  The widening must re-apply the
        # scaling on the cached UNSCALED slots, so the long-lived renderer's
        # render of the saved graph byte-equals a fresh renderer's full-text
        # paint at the app's own view state.
        region = screen.query_one("#map-canvas", Static).region
        state = screen._view_state(region.width, region.height)  # noqa: SLF001
        assert screen.renderer.render(screen.graph, state).plain == (
            LayeredRenderer().render(screen.graph, state).plain
        ), (
            "a widening title re-applies the scaling on the cached unscaled "
            "slots; caching the SCALED layout (M-R2c) reuses stale geometry "
            "and must fail this full-text compare"
        )

    fresh = MapperApp(tmp_path)
    async with fresh.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        graph = build_fold_tree()
        graph.nodes["mid"].ficha.title = EDITED_TITLE
        fresh.store.save("tt2", graph)
        screen2 = await _open(fresh, pilot, "tt2", cursor="mid")
        assert _canvas_lines(screen2) == edited, (
            "the widened-title repaint must byte-equal a fresh renderer's paint"
        )


async def _arm_fold(tmp_path):
    """`fold`: fold/unfold changes the hidden set -- a layout input -- so each
    toggle misses exactly once, and unfolding repaints byte-identically to the
    unfolded map."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("fd", build_fold_tree())
        screen = await _open(app, pilot, "fd", cursor="mid")
        before = screen.renderer._layout_misses
        flat = _canvas_lines(screen)
        await _press(pilot, "z")
        assert screen.renderer._layout_misses == before + 1, (
            "folding a branch must miss exactly once"
        )
        assert _canvas_lines(screen) != flat, "a fold must change the paint"
        await _press(pilot, "z")
        assert screen.renderer._layout_misses == before + 2, (
            "unfolding must miss exactly once"
        )
        assert _canvas_lines(screen) == flat, (
            "unfolding must repaint byte-identically to the unfolded map"
        )


async def _arm_focus(tmp_path):
    """`focus`: each `f` toggle swaps the graph -- focus-on for a NEW focused
    subgraph, focus-off for the restored base graph -- and a single-entry memo
    can hold only the latest layout, so each toggle misses exactly once."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("fc", build_fold_tree())
        screen = await _open(app, pilot, "fc", cursor="mid")
        before = screen.renderer._layout_misses
        whole = _canvas_lines(screen)
        await _press(pilot, "f")
        assert screen.focus_active
        assert screen.renderer._layout_misses == before + 1, (
            "focusing a new subgraph must miss exactly once"
        )
        await _press(pilot, "f")
        assert not screen.focus_active
        assert screen.renderer._layout_misses == before + 2, (
            "the restored base graph is not the cached entry; it must miss"
        )
        assert _canvas_lines(screen) == whole, (
            "the focus round trip must repaint byte-identically"
        )


async def _add_child_via_keys(app, pilot) -> None:
    """The `a` gesture through real keys: prompt, title, enter, persisted."""
    await _press(pilot, "a")
    assert isinstance(app.screen, _PromptScreen), type(app.screen).__name__
    await pilot.press(*"hijoextra")
    await _press(pilot, "enter")


async def _arm_undo(tmp_path):
    """`undo`: `u` rebuilds the graph from the undo snapshot as a NEW `Graph`
    object -- never `is` the cached one -- so it misses.  (The allocator-reuse
    exercise is M-R2d's dedicated node, ruling R13.)"""
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("un", build_fold_tree())
        screen = await _open(app, pilot, "un", cursor="mid")
        before = screen.renderer._layout_misses
        await _add_child_via_keys(app, pilot)
        assert screen.renderer._layout_misses == before + 1, (
            "adding a child must miss exactly once"
        )
        await _press(pilot, "u")
        assert screen.renderer._layout_misses == before + 2, (
            "undo builds a NEW Graph; it must miss exactly once"
        )
        assert "hijoextra" not in screen.graph.nodes, "undo must restore the map"


async def _arm_add_child(tmp_path):
    """`add_child`: the persisted `a` gesture mutates the nodes dict (+1 len)
    and the edges list (+1 len) IN PLACE -- same objects, new lengths -- so
    the length conjunct of the key misses exactly once."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("ac", build_fold_tree())
        screen = await _open(app, pilot, "ac", cursor="mid")
        before = screen.renderer._layout_misses
        await _add_child_via_keys(app, pilot)
        assert screen.renderer._layout_misses == before + 1, (
            "adding a child must miss exactly once"
        )
        assert "hijoextra" in screen.graph.nodes


async def _arm_round_trip(tmp_path):
    """`round_trip`: outline <-> radial <-> layered switches repaint the
    layered canvas byte-identically, and the layout memo is untouched by the
    other renderers (0 extra misses)."""
    app = MapperApp(tmp_path)
    async with app.run_test(size=TERMINAL) as pilot:
        await pilot.pause()
        app.store.save("rt", build_fold_tree())
        screen = await _open(app, pilot, "rt", cursor="mid")
        before = screen.renderer._layout_misses
        layered = _canvas_lines(screen)
        await _press(pilot, "o")
        await _press(pilot, "o")
        assert _canvas_lines(screen) == layered, (
            "outline and back must repaint the layered canvas byte-identically"
        )
        await _press(pilot, "r")
        await _press(pilot, "r")
        assert _canvas_lines(screen) == layered, (
            "radial and back must repaint the layered canvas byte-identically"
        )
        assert screen.renderer._layout_misses == before, (
            "the view round trip must not miss"
        )


_ARMS = {
    "resize": _arm_resize,
    "title": _arm_title,
    "fold": _arm_fold,
    "focus": _arm_focus,
    "undo": _arm_undo,
    "add_child": _arm_add_child,
    "round_trip": _arm_round_trip,
}


@pytest.mark.parametrize("arm", _ARMS)
async def test_memo_invalidation_arms(tmp_path, arm):
    """LLR-PERF.1.2, the seven named invalidation arms (requirements SS5.2).
    M-R2c (cache the SCALED layout) reddens `resize`/`title`; M-R2b (never
    invalidate) reddens `fold`/`add_child`."""
    await _ARMS[arm](tmp_path)


# ---------------------------------------------------------------------------
# M-R2d (ruling R13): object-identity reuse after garbage collection.
# ---------------------------------------------------------------------------

def test_memo_id_reuse():
    """M-R2d / ruling R13: a same-shape graph allocated after the old one was
    dropped ALWAYS misses.

    WHY THE FORCED-REUSE ARM IS STATED, NOT EXERCISED: the memo key holds the
    old graph by STRONG reference, so while the entry lives the old object
    cannot be freed and its address cannot be recycled -- address reuse is
    un-forceable by construction, which is exactly the soundness the
    strong-reference key buys over an `id()` key.  The node therefore keeps
    the plain "new Graph object misses" assertion (deterministic on every
    interpreter); the id()-keyed mutant is demonstrated RED in
    `evidence/r2-red.transcript` on this interpreter, where the freed object's
    address IS recycled once nothing pins it.
    """
    renderer = LayeredRenderer()
    state = ViewState(w=118, h=34)

    g1 = build_fold_tree()
    renderer.render(g1, state)
    assert renderer._layout_misses == 1

    del g1
    gc.collect()
    g2 = build_fold_tree()
    renderer.render(g2, state)
    assert renderer._layout_misses == 2, (
        "a new Graph object is never `is` the cached one; it must miss even "
        "if the allocator recycled the freed address"
    )


# ---------------------------------------------------------------------------
# Ruling R14: the `Graph.nodes` writer census (Lane R's tripwire, M-R2e).
# ---------------------------------------------------------------------------

_NODES_MUTATING_METHODS = frozenset({"update", "setdefault", "pop", "popitem", "clear"})
_NODES_AUG_OPS = {ast.BitOr: "ior", ast.Add: "iadd", ast.Mult: "imul"}

#: The declared post-construction writers of `Graph.nodes` (ruling R14):
#: `model.py` `add_node` and `screens/map/editing.py` wholesale.  Any new
#: writer site reddens `test_nodes_writer_census` (mutation M-R2e).
_NODES_WRITER_CENSUS = frozenset({
    ("mapper/model.py", "add_node", "setitem"),
    ("mapper/screens/map/editing.py", "_remove_subtree", "assign"),
})


def _scan_scope_for_nodes_writers(scope: ast.AST, func_name: str) -> set[tuple[str, str]]:
    """Flag every write to a `.nodes` attribute (or an alias of one) inside
    *scope*.  Returns `{(form, func_name)}`.

    FORMS FLAGGED: wholesale assignment (`x.nodes = ...`), subscript store
    (`x.nodes[k] = v`), slice store, `del x.nodes[k]`, augmented assignment,
    the mutating methods (`update`/`setdefault`/`pop`/`popitem`/`clear`), and
    the ALIAS form (`n = x.nodes` then a store/mutation through `n`) collected
    per function scope.

    DOCUMENTED LIMITS (the alias form, stated): aliasing through function
    arguments, container elements, or attributes on other objects is NOT
    detected; only a name bound DIRECTLY from a `.nodes` load inside the same
    function is treated as an alias.  Construction (`Graph(nodes=...)`) is not
    a post-construction writer and is not flagged.
    """
    def _own_nodes(scope: ast.AST):
        """Yield every node in *scope* EXCEPT nested function bodies -- each
        nested function is scanned as its own scope, so descending into it
        here would attribute its stores to the enclosing scope too."""
        stack = list(ast.iter_child_nodes(scope))
        while stack:
            node = stack.pop()
            yield node
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            stack.extend(ast.iter_child_nodes(node))

    aliases: set[str] = set()
    own_nodes = list(_own_nodes(scope))
    for node in own_nodes:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Attribute):
            if node.value.attr == "nodes":
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        aliases.add(target.id)
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == "nodes"
            and isinstance(node.target, ast.Name)
        ):
            aliases.add(node.target.id)

    def base_form(value: ast.AST) -> str | None:
        if isinstance(value, ast.Attribute) and value.attr == "nodes":
            return "direct"
        if isinstance(value, ast.Name) and value.id in aliases:
            return "alias"
        return None

    found: set[tuple[str, str]] = set()
    for node in own_nodes:
        if isinstance(node, ast.Assign):
            targets = node.targets
            for target in targets:
                stack = list(target.elts) if isinstance(target, (ast.Tuple, ast.List)) else [target]
                for t in stack:
                    if isinstance(t, ast.Attribute) and t.attr == "nodes":
                        found.add(("assign", func_name))
                    elif isinstance(t, ast.Subscript):
                        kind = base_form(t.value)
                        if kind == "direct":
                            form = ("slice-setitem" if isinstance(t.slice, ast.Slice)
                                    else "setitem")
                            found.add((form, func_name))
                        elif kind == "alias":
                            found.add(("alias-setitem", func_name))
        elif isinstance(node, ast.AugAssign):
            kind = base_form(node.target)
            if kind == "direct":
                op = _NODES_AUG_OPS.get(type(node.op), "augassign")
                found.add((op, func_name))
            elif kind == "alias":
                found.add(("alias-augassign", func_name))
        elif isinstance(node, ast.Delete):
            for target in node.targets:
                if isinstance(target, ast.Subscript):
                    kind = base_form(target.value)
                    if kind == "direct":
                        found.add(("del", func_name))
                    elif kind == "alias":
                        found.add(("alias-del", func_name))
                elif isinstance(target, ast.Attribute) and target.attr == "nodes":
                    found.add(("del-attr", func_name))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _NODES_MUTATING_METHODS:
                kind = base_form(node.func.value)
                if kind == "direct":
                    found.add((f"call-{node.func.attr}", func_name))
                elif kind == "alias":
                    found.add((f"alias-call-{node.func.attr}", func_name))
    return found


def _nodes_writer_sites(root: Path) -> set[tuple[str, str, str]]:
    """Every `(relative file, function, form)` that writes a `.nodes` dict in
    the package rooted at *root* (AST-derived; mirrors Lane M's `edges` guard
    so the lanes stay independent)."""
    sites: set[tuple[str, str, str]] = set()
    for path in sorted(root.rglob("*.py")):
        try:
            rel = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = path.name  # a planted tree outside the repo (the form arms)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        scopes: list[tuple[ast.AST, str]] = [(tree, "<module>")]
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scopes.append((node, node.name))
        for scope, name in scopes:
            for form, func_name in _scan_scope_for_nodes_writers(scope, name):
                sites.add((rel, func_name, form))
    return sites


def test_nodes_writer_census():
    """Ruling R14 / M-R2e: the set of post-construction `Graph.nodes` writers
    is exactly the declared two; any new writer site (a third file, a new
    function, or a new form in a declared function) reddens this guard."""
    sites = _nodes_writer_sites(REPO_ROOT / "mapper")
    assert sites == _NODES_WRITER_CENSUS, (
        f"Graph.nodes writer census drifted: {sorted(sites - _NODES_WRITER_CENSUS)} "
        f"new, {sorted(_NODES_WRITER_CENSUS - sites)} missing"
    )


#: One planted banned form per arm (M-R2e): each must be DETECTED when planted
#: in a scanned tree.  `g` stands for any graph object; the census is an AST
#: scan, so the snippets are never executed.
_PLANTED_FORMS = {
    "setitem": "def mutate(g):\n    g.nodes['x'] = None\n",
    "slice-setitem": "def mutate(g):\n    g.nodes['a':'b'] = {}\n",
    "del": "def mutate(g):\n    del g.nodes['x']\n",
    "ior": "def mutate(g):\n    g.nodes |= {'x': 1}\n",
    "iadd": "def mutate(g):\n    g.nodes += {'x': 1}\n",
    "imul": "def mutate(g):\n    g.nodes *= 2\n",
    "call-update": "def mutate(g):\n    g.nodes.update({'x': 1})\n",
    "call-setdefault": "def mutate(g):\n    g.nodes.setdefault('x', None)\n",
    "call-pop": "def mutate(g):\n    g.nodes.pop('x')\n",
    "call-popitem": "def mutate(g):\n    g.nodes.popitem()\n",
    "call-clear": "def mutate(g):\n    g.nodes.clear()\n",
    "assign": "def mutate(g):\n    g.nodes = {}\n",
    "alias-setitem": "def mutate(g):\n    n = g.nodes\n    n['x'] = None\n",
    "alias-call-update": "def mutate(g):\n    n = g.nodes\n    n.update({'x': 1})\n",
    "alias-del": "def mutate(g):\n    n = g.nodes\n    del n['x']\n",
}


@pytest.mark.parametrize("form", sorted(_PLANTED_FORMS))
def test_nodes_writer_census_in_place_forms(tmp_path, form):
    """M-R2e's detector arms: every in-place and alias form is flagged when
    planted, so a real new writer site cannot pass the census."""
    planted = tmp_path / "planted"
    planted.mkdir()
    (planted / "planted_mod.py").write_text(_PLANTED_FORMS[form], encoding="utf-8")
    sites = _nodes_writer_sites(planted)
    assert ("planted_mod.py", "mutate", form) in sites, (
        f"the census failed to flag the planted {form!r} form"
    )
