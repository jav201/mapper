"""The four derived censuses Inc-3 gates on, plus its own seat diff.

`LLR-COERCE.2` (truncators), `A-89` / `B-47` (renderer to operator-visible
sink), `A-98` (participation in `painted_ids`), `C-D25a` (the seat diff).

EVERY ONE OF THESE DERIVES ITS INPUT SET.  A hand-listed set is the defect
class, not a shortcut past it: this batch has shipped four false oracles, two of
them hand-listed sets, and a set someone typed repairs the members that break
today and is blind to the one a later increment adds.  Each census therefore
asserts its input is non-empty BEFORE it evaluates anything, and quantifies over
what it derived.
"""
from __future__ import annotations

import ast
import importlib
import inspect
import subprocess
from pathlib import Path

import pytest

from mapper import darkside
from mapper.diff import DiffResult
from mapper.keymap import KEYMAP, bindings_for, duplicate_chords
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.views.layered import LayeredRenderer
from mapper.views.state import ViewState

REPO = Path(__file__).resolve().parents[1]

BANNED = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}


def tracked(*globs) -> list[str]:
    out = subprocess.run(["git", "ls-files", *globs], cwd=REPO,
                         capture_output=True, text=True, check=True)
    return out.stdout.split()


def hostile(tag: str) -> str:
    """Built from CODE POINTS at test time; no source file here holds one."""
    return (
        tag + chr(0x01) + chr(0x202E) + "rtl" + chr(0x202C)
        + chr(0x200B) + chr(0xE0041) + "z"
    )


# ==========================================================================
# LLR-COERCE.2 — the truncator census


def truncators() -> dict[str, object]:
    """Every `(str, int) -> str` in the tracked product sources that SHORTENS.

    Two stages, and the second is what makes it a census of truncators rather
    than of signatures: the shape is derived from the AST, then each candidate
    is EXECUTED on a string longer than the width it is given and kept only if
    it actually came back shorter.  A helper that merely has the shape is not a
    truncator, and a truncator that grew a third parameter would drop out --
    which is why the cardinality below is pinned as an equality.
    """
    found: dict[str, object] = {}
    for rel in tracked("mapper/*.py", "mapper/**/*.py"):
        module_name = rel[:-3].replace("/", ".")
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        module = importlib.import_module(module_name)
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            args = node.args.args
            if len(args) != 2 or node.args.kwonlyargs or node.args.vararg:
                continue
            annotations = [
                a.annotation.id if isinstance(a.annotation, ast.Name) else None
                for a in args
            ]
            returns = node.returns.id if isinstance(node.returns, ast.Name) else None
            if annotations != ["str", "int"] or returns != "str":
                continue
            function = getattr(module, node.name, None)
            if function is None:
                continue
            if len(function("A" * 64, 8)) < 64:
                found[f"{module_name}.{node.name}"] = function
    return found


def test_llr_coerce_2_the_truncator_set_is_derived_and_non_empty():
    """The input set, asserted before a single property is evaluated.

    Pinned as an EQUALITY, not a floor.  `A-32` abolished floors here for the
    reason this census exists: a derivation that lost a member sits comfortably
    above one, and losing `layered._fit` is exactly the loss that puts the
    override back on the canvas.
    """
    derived = truncators()
    assert derived, "the truncator derivation collapsed; every clause below is vacuous"
    assert set(derived) == {
        "mapper.darkside.fit",
        "mapper.views.layered._clip",
        "mapper.views.layered._fit",
    }, sorted(derived)
    # TWO truncators shipped and only one coerced; the census is scoped so that
    # difference is visible rather than assumed away.
    assert len(derived) == 3


@pytest.mark.parametrize("width", (1, 2, 5, 8, 13, 40))
def test_llr_coerce_2_every_truncator_coerces_before_it_truncates(width):
    """The stated threshold, quantified over the DERIVED set and 6 widths.

    ⚠ THIS PREDICATE IS WEAK ON A LENGTH-PRESERVING COERCION, and saying so is
    the honest reading rather than a hedge.  `darkside.plain` is a 1:1
    `str.translate`, so it distributes over slicing, and a truncator that slices
    by `len` satisfies this equality whether or not it coerces -- measured at
    `954f8f3`, the UNCOERCED `layered._fit` already returned `True` here.  It is
    kept because it is the requirement's stated threshold and because it is NOT
    vacuous for a truncator measuring in display cells (`darkside.fit` uses
    `Text.cell_len`, and a control character's cell width is not its length).
    The arms below are the ones that discriminate.
    """
    derived = truncators()
    assert derived
    for name, function in derived.items():
        source = hostile("t")
        assert function(darkside.plain(source), width) == darkside.plain(
            function(source, width)
        ), name


@pytest.mark.parametrize("width", (1, 2, 5, 8, 13, 40))
def test_llr_coerce_2_no_truncator_emits_a_coerced_code_point(width):
    """THE DISCRIMINATING ARM — 0 occurrences in the output, per truncator.

    This is what the pre-state actually failed: executed at `954f8f3`,
    `layered._fit('a' + chr(1) + 'b', 8)` returned the control byte intact while
    the commutation arm above was already green.
    """
    derived = truncators()
    assert derived
    for name, function in derived.items():
        out = function(hostile("t"), width)
        leaked = sorted({hex(ord(c)) for c in out if ord(c) in BANNED and c not in "\t\n"})
        assert leaked == [], (name, width, leaked)


def test_llr_coerce_2_the_split_at_width_arm(tmp_path):
    """A source BALANCED at U+202E … U+202C, cut at width, leaves 0 overrides.

    The clause that makes the ordering non-vacuous: truncation MANUFACTURES the
    defect out of a source that was well-formed, so coercing afterwards cannot
    put the terminator back.
    """
    derived = truncators()
    assert derived
    source = "a" * 4 + chr(0x202E) + "b" * 30 + chr(0x202C)
    assert source.count(chr(0x202E)) == source.count(chr(0x202C)) == 1, (
        "the source is not balanced, so the arm is testing the wrong thing"
    )
    for name, function in derived.items():
        for width in (5, 6, 10, 20):
            out = function(source, width)
            assert out.count(chr(0x202E)) == 0, (name, width)
            assert out.count(chr(0x202C)) == 0, (name, width)


# ==========================================================================
# A-89 / B-47 — every renderer feeding an operator-visible sink


def renderer_classes() -> dict[str, str]:
    """Every class under `mapper/views/` defining `render` — DERIVED."""
    found: dict[str, str] = {}
    for rel in tracked("mapper/views/*.py"):
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(
                isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef))
                and b.name == "render"
                for b in node.body
            ):
                found[node.name] = rel
    return found


def reached_renderers() -> dict[str, list[str]]:
    """Renderers NAMED by a product module OUTSIDE `mapper/views/`.

    The scoping predicate is structural, not a list: `mapper/views/` is the
    renderer package, so `views/__init__.py` re-exporting a class is excluded by
    where it lives rather than by anyone remembering to exclude it.  The day
    `app.py` (or any other consumer) names `LaneRenderer`, that renderer enters
    this census automatically and has to pass the coercion clause with it.
    """
    renderers = renderer_classes()
    reached: dict[str, list[str]] = {}
    for rel in tracked("mapper/*.py", "mapper/**/*.py"):
        if rel.startswith("mapper/views/"):
            continue
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            # BOTH REFERENCE FORMS, and the second is not hypothetical: matching
            # `ast.Name` alone saw `from .views.lane import LaneRenderer` but
            # not `from .views import lane` / `lane.LaneRenderer`.  Mutation-
            # tested, the attribute wiring SURVIVED with 23 arms green --
            # including the equality pin whose stated job is to go red and force
            # the decision.  A census that a plausible wiring shape walks past
            # is not the control it claims to be.
            name = (
                node.id if isinstance(node, ast.Name)
                else node.attr if isinstance(node, ast.Attribute)
                else None
            )
            if name in renderers:
                reached.setdefault(name, []).append(f"{rel}:{node.lineno}")
    return reached


def test_a89_the_renderer_census_derives_a_non_empty_set():
    """Non-empty before anything is evaluated, on BOTH halves of the derivation."""
    renderers = renderer_classes()
    assert len(renderers) >= 6, sorted(renderers)
    reached = reached_renderers()
    assert reached, "no renderer is reached from outside views/; the clause is vacuous"


def test_a89_the_reached_set_is_pinned_so_wiring_lane_up_pulls_it_in():
    """VERIFIED MECHANICALLY, not adopted from the ruling that asserted it.

    `02j` reports `views/lane.py` has zero product call sites.  Re-derived here
    over the tracked tree: `LaneRenderer`, `HybridLaneRenderer` and
    `RailTimelineRenderer` are named nowhere outside `mapper/views/`, so they
    reach no operator-visible sink today and are correctly outside the coercion
    clause below.  Pinned as an EQUALITY so that the increment which wires one
    of them up turns this red and inherits the obligation, instead of shipping a
    fourth uncoerced renderer the way `B-47` shipped two.
    """
    assert set(reached_renderers()) == {
        "LayeredRenderer", "OutlineRenderer", "RadialRenderer"
    }, sorted(reached_renderers())
    unreached = set(renderer_classes()) - set(reached_renderers()) - {"IRenderer"}
    assert unreached == {
        "LaneRenderer", "HybridLaneRenderer", "RailTimelineRenderer"
    }, sorted(unreached)


def test_a89_every_reached_renderer_coerces_what_it_paints():
    """`LLR-COERCE.2` as widened: measured on the rendered surface, per renderer.

    `AT-009` asserted the exported SVG carries no coerced code point and it did
    -- through `RadialRenderer`.  Executed at `954f8f3`, `LayeredRenderer` (the
    DEFAULT view) and `OutlineRenderer` both leaked `0x01`, `0x200b` and
    `0x202e`, so the guarantee held in one of three views.
    """
    graph = Graph()
    # `fields` CARRIES THE PAYLOAD TOO, and its absence was a measured hole
    # rather than an omission of taste: the legacy card's `◫` document chip
    # (`layered.py:459`) paints `ficha.fields["D"]`, and with no `fields` on any
    # ficha that branch painted the constant "◫ sin acta" at every size.
    # Mutation-tested, removing its `_fit` survived the entire 789-arm suite --
    # a shipped coercion with nothing standing on it.
    fields = {"D": hostile("acta"), "A": hostile("a"), "B": hostile("b")}
    graph.add_node(Node(id="root", ficha=Ficha(
        title=hostile("raiz"), meta=hostile("m"), notes=hostile("n"),
        fields=dict(fields))))
    for i in range(3):
        graph.add_node(Node(id=f"k{i}", ficha=Ficha(
            title=hostile(f"h{i}"), meta=hostile("m"), notes=hostile("n"),
            fields=dict(fields))))
        graph.add_edge(Edge(parent_id="root", child_id=f"k{i}"))
    # A NON-EMPTY SCHEMA, WITH THE HOSTILE PAYLOAD IN THE KEY, and it is the
    # correction this arm needed rather than an extra payload.  `layered.py`
    # selects the LEGACY card on `bool(graph.schema)`, so a fixture carrying
    # only title/meta/notes NEVER ENTERS the branch that paints
    # `SchemaField.key` -- and that branch was the one sink left in the DEFAULT
    # renderer writing a file-derived string to the terminal and to the exported
    # SVG uncoerced, which is `B-47`'s exact failure.  The census was blind to
    # it because the fixture could not reach it, not because the check was weak.
    # `MapStore.load` does not coerce `key`/`label` either, so a `.yml` sidecar
    # is a real path to this.
    graph.schema = [
        SchemaField(key=chr(0x01), label=hostile("uno")),
        SchemaField(key=chr(0x202E), label=hostile("dos")),
    ]
    # POSITIVE CONTROL: the fixture really does carry what we are looking for,
    # on BOTH the ficha strings and the schema the legacy branch reads.
    assert any(ord(c) in BANNED for c in graph.nodes["root"].ficha.title)
    assert any(ord(c) in BANNED for sf in graph.schema for c in sf.key), (
        "no schema key carries a banned code point; the legacy branch is "
        "entered but nothing hostile reaches its sink and this arm proves nothing"
    )
    assert any(ord(c) in BANNED for c in graph.nodes["root"].ficha.fields["D"]), (
        "no ficha field carries a banned code point; the `◫` document chip is "
        "reached but nothing hostile arrives at it"
    )

    # A `DiffResult`, AND IT IS THE SAME CLASS OF HOLE.  Two more shipped
    # coercions live behind `state.diff` -- the changed-keys chip
    # (`layered.py:449`) and the removed-node ghost titles (`layered.py:520`) --
    # and NO census fixture set `diff`, so mutants removing either survived the
    # full suite.  `changed` is keyed by node and its VALUES are schema keys;
    # `removed_titles` is keyed by a node that is no longer in the graph, which
    # is why `r0` is named here but never added to it.
    diff = DiffResult(
        added={"k0"},
        removed={"r0"},
        changed={"k1": [hostile("ck")], "root": [hostile("cr")]},
        removed_titles={"r0": hostile("ido")},
    )
    assert any(ord(c) in BANNED for v in diff.changed.values() for c in v[0])
    assert any(ord(c) in BANNED for c in diff.removed_titles["r0"])

    reached = reached_renderers()
    assert reached
    checked = 0
    for name in sorted(reached):
        module = importlib.import_module(
            renderer_classes()[name][:-3].replace("/", ".")
        )
        renderer = getattr(module, name)()
        for size in ((80, 24), (140, 45), (30, 12)):
            # BOTH DIFF STATES, because the diff-only sinks are unreachable in
            # the other one and half the renderers ignore `diff` entirely.
            for state_diff in (None, diff):
                painted = renderer.render(
                    graph, ViewState(w=size[0], h=size[1], diff=state_diff)
                ).plain
                leaked = sorted({hex(ord(c)) for c in painted
                                 if ord(c) in BANNED and c not in "\t\n"})
                assert leaked == [], (name, size, state_diff is not None, leaked)
                checked += 1
    assert checked == 18, checked

    # NON-VACUITY ON THE DIFF HALF: the diff state must actually change what the
    # DEFAULT renderer paints, or the six extra passes above are six copies of
    # the six below them.
    plain_frame = LayeredRenderer().render(graph, ViewState(w=140, h=45)).plain
    diff_frame = LayeredRenderer().render(
        graph, ViewState(w=140, h=45, diff=diff)
    ).plain
    assert plain_frame != diff_frame, (
        "the DiffResult changes nothing the renderer paints; the diff-only "
        "sinks are still outside this census"
    )
    assert "eliminados" in diff_frame, (
        "the ghost row is not painted, so `removed_titles` never reaches its sink"
    )


# ==========================================================================
# A-98 — the participation census for `painted_ids`


def painted_ids_exporters() -> set[str]:
    """Modules under `mapper/views/` exporting a module-level `painted_ids`."""
    found = set()
    for rel in tracked("mapper/views/*.py"):
        module_name = rel[:-3].replace("/", ".")
        module = importlib.import_module(module_name)
        function = getattr(module, "painted_ids", None)
        if function is not None and getattr(function, "__module__", "") == module_name:
            found.add(module_name)
    return found


def test_a98_the_participation_census_input_is_non_empty():
    """The modules swept, before the equality below is evaluated."""
    swept = set(tracked("mapper/views/*.py"))
    assert len(swept) >= 5, sorted(swept)
    assert painted_ids_exporters(), (
        "no module exports painted_ids; the equality below would pin an empty set"
    )


def test_a98_exactly_one_renderer_declares_its_painted_set():
    """EQUALITY with `{layered}`, and that is the point of it being an equality.

    `outline` and `radial` also hide nodes and declare nothing -- measured at
    30x6 on `legacy`, 5 of 8 and 2 of 8 traced.  `HLR-N06.3`'s promise is
    therefore kept in the DEFAULT view and silently unkept in the other two.
    Inc-3 does not close that; it declares it (carry `B-55`, routed to Inc-5)
    and pins it here, so the day a second renderer joins, this goes red and
    forces the decision rather than letting the guarantee quietly widen -- or
    quietly not.
    """
    assert painted_ids_exporters() == {"mapper.views.layered"}


def test_a98_the_screen_imports_painted_ids_by_name_never_by_getattr():
    """`02j`'s ruling, asserted mechanically.

    A `getattr(renderer, "painted_ids", None)` probe is a silent-skip generator
    of exactly the kind this batch keeps catching: it answers "this view
    declares nothing" and "this view's declaration is broken" with the same
    `None`.  The branch is a static import and an identity comparison, which is
    greppable, AST-visible and type-checkable.
    """
    source = (REPO / "mapper" / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and (node.module or "").endswith("layered")
        for alias in node.names
    }
    assert "painted_ids" in imported

    probes = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name) and node.func.id == "getattr"
        and len(node.args) >= 2
        and isinstance(node.args[1], ast.Constant)
        and node.args[1].value in ("painted_ids", "pan_extent")
    ]
    assert probes == []


# ==========================================================================
# C-D25a — Inc-3's OWN four-row seat diff


# The `map`-scope seat as it stood at `954f8f3`, the increment's base.  This is
# the ENTRY side of the diff and nothing else; it is not a second copy of the
# whole-seat specification, which `tests/test_key_dispatch.py` already pins.
ENTRY_MAP_SEAT = frozenset({
    ("j", "next_sibling"), ("k", "prev_sibling"), ("h", "parent"), ("l", "child"),
    ("enter", "open_ficha"), ("slash", "search"),
    ("a", "add_child"), ("d", "open_documents"), ("x", "archive"), ("u", "undo"),
    ("A", "add_attachment"), ("X", "remove_attachment"),
    ("f", "toggle_focus"), ("o", "toggle_outline"), ("r", "toggle_radial"),
    ("e", "export_svg"), ("equals_sign", "toggle_diff"), ("m", "coverage"),
    ("n", "next_gap"), ("R", "toggle_rail"), ("I", "toggle_inspector"),
    ("g", "focus_rail"), ("z", "collapse_branch"),
    ("q", "home"), ("escape", "back_or_home"),
    ("ctrl+p", "palette"), ("question_mark", "help"),
})

# The rows this increment claims.  Declared here, and asserted EQUAL to the
# entry/exit difference below -- a pin per diff, never a global cap.  There is
# no row budget on Inc-3: `PLAN.md:244`'s "exactly one changed row plus two
# added rows" is an equality on `D10`'s OWN diff, and the sealed `#D5b` names
# Inc-3 as a `keymap.py` toucher while imposing only `duplicate_chords()` and
# the whole-seat pin on it.
DECLARED_DIFF = frozenset({
    ("H", "pan_left"), ("J", "pan_down"), ("K", "pan_up"), ("L", "pan_right"),
})


def test_cd25a_the_seat_diff_is_exactly_the_four_rows_inc3_declares():
    """The declared diff EQUALS the entry/exit difference of `bindings_for('map')`."""
    exit_seat = frozenset((b.key, b.action) for b in bindings_for("map"))
    assert len(ENTRY_MAP_SEAT) == 27, len(ENTRY_MAP_SEAT)
    assert exit_seat - ENTRY_MAP_SEAT == DECLARED_DIFF
    assert ENTRY_MAP_SEAT - exit_seat == frozenset(), (
        "a row LEFT the map seat; this increment declared no removal"
    )
    assert len(exit_seat) == 31


def test_cd25a_no_chord_collides_on_entry_or_on_exit():
    """`duplicate_chords()` -> `[]` on BOTH sides, over the same instrument.

    The entry side is reconstructed by removing this increment's own four rows
    from the live seat rather than by quoting a transcript: a transcript records
    what someone ran, and this records what the shipped detector says.
    """
    assert duplicate_chords() == []

    entry_keymap = [b for b in KEYMAP if (b.key, b.action) not in DECLARED_DIFF]
    assert len(entry_keymap) == len(KEYMAP) - 4
    seen, clashes = set(), []
    for binding in entry_keymap:
        pair = (binding.scope, binding.key)
        if pair in seen:
            clashes.append(pair)
        seen.add(pair)
    app_keys = {b.key for b in entry_keymap if b.scope == "app"}
    for binding in entry_keymap:
        if binding.scope != "app" and binding.key in app_keys:
            clashes.append((binding.scope, binding.key))
    assert sorted(set(clashes)) == []


def test_cd25a_every_new_chord_dispatches_to_a_method_that_exists():
    """A seat row naming a method the screen does not define is a silent no-op.

    The precedent is in this tree: the help overlay borrowed the palette's
    `enter -> run_selected`, a method `HelpScreen` never defined.
    """
    from mapper.app import MapScreen

    for key, action in sorted(DECLARED_DIFF):
        method = getattr(MapScreen, f"action_{action}", None)
        assert callable(method), (key, action)
        assert list(inspect.signature(method).parameters) == ["self"], action
