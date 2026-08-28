"""The A3 census — LLR-N07.2.2a.

The migration's whole risk is that it HALF-lands: the six signatures change, the
suite goes green, and call sites still pass the old shape, so two contracts are
live at once.  So the gate is SET EQUALITY on both sides of the protocol, never
a floor, and never on definitions alone.

INSTRUMENT: `ast`, not `grep`.  `.render` names TWO different protocols in this
tree -- Textual's `Widget.render()`, which takes no arguments and MUST NOT be
migrated, and the map renderer, which takes arguments and must.  A line-oriented
count answers neither question.  Executed at `3fe0e4b`, a grep returned 24 sites
where the AST returned 23; the extra was a mention of `renderer.render(...)`
inside a docstring.  Only a parse separates a call from its own encoding.
"""
import ast
import inspect
import subprocess
from pathlib import Path

import pytest

from mapper.views.state import IRenderer, ViewState

REPO = Path(__file__).resolve().parents[1]


def tracked(*globs) -> list[str]:
    """`git ls-files`, which lists only TRACKED paths.

    That is a real hole and it is guarded rather than hidden: a renderer file
    that has not been `git add`ed is invisible to every census below, so a new
    renderer could escape threshold 1 entirely.  Measured -- the census working
    at all depended on `state.py` having been staged, an undeclared
    precondition.  `test_tc_a3_no_source_file_is_invisible_to_the_census`
    turns that into a red arm.
    """
    out = subprocess.run(["git", "ls-files", *globs], cwd=REPO,
                         capture_output=True, text=True, check=True)
    return out.stdout.split()


def test_tc_a3_no_source_file_is_invisible_to_the_census():
    """A census cannot be a safety net over files it cannot see.

    Sweeps `tests/` as well as `mapper/`, because threshold 3 sweeps both: an
    untracked TEST file carrying an old-shape call site was invisible while the
    mapper-only version of this arm stayed green.  The precondition was live at
    the time -- this very file was untracked.
    """
    for root in ("mapper", "tests"):
        seen = set(tracked(f"{root}/*.py", f"{root}/**/*.py"))
        on_disk = {
            p.relative_to(REPO).as_posix()
            for p in (REPO / root).rglob("*.py")
            if "__pycache__" not in p.parts
        }
        assert on_disk <= seen, (
            f"untracked {root}/ source is invisible to the A3 census: "
            f"{sorted(on_disk - seen)} -- stage it, or the gate is not a gate"
        )


def _parse(rel: str) -> ast.Module:
    return ast.parse((REPO / rel).read_text(encoding="utf-8"))


def render_definitions() -> dict[tuple[str, int], ast.FunctionDef]:
    """Every `def render` under `mapper/views/` — the migration's definition side."""
    found = {}
    for rel in tracked("mapper/views/*.py"):
        for node in ast.walk(_parse(rel)):
            # `AsyncFunctionDef` too: an `async def render` is a definition the
            # migration would have to cover and a `FunctionDef`-only walk cannot
            # see it.
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == "render"):
                found[(rel, node.lineno)] = node
    return found


def render_call_sites() -> dict[str, list[tuple[str, int]]]:
    """`.render(...)` calls, split by whether they pass arguments.

    The split IS the census: arg-ful sites invoke the map-renderer protocol and
    must migrate; zero-arg sites are Textual widgets and must not.
    """
    argful, zeroarg = [], []
    for rel in tracked("mapper/*.py", "mapper/**/*.py", "tests/*.py", "tests/**/*.py"):
        for node in ast.walk(_parse(rel)):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "render"):
                (argful if (node.args or node.keywords) else zeroarg).append(
                    (rel, node.lineno))
    return {"argful": argful, "zeroarg": zeroarg}


# --------------------------------------------------------------------------


def test_tc_a3_the_derived_sets_are_non_empty_before_anything_is_evaluated():
    """A census that passes on an empty input set is not a census."""
    assert render_definitions(), "no render definition derived"
    sites = render_call_sites()
    assert sites["argful"], "no arg-ful call site derived"
    assert sites["zeroarg"], "no zero-arg site derived -- the split cannot be exercised"


def test_tc_a3_the_census_cardinalities_are_PINNED():
    """EQUALITY, not a floor -- and the numbers live here, not only in prose.

    `LLR-N07.2.2a` states its thresholds as set equality "never a floor", and
    `A-32` abolished floors for exactly this reason: a derivation that gains or
    loses members sits comfortably above one.

    These figures were published as 27 and 6 in the increment packet AND in the
    module map, and both were wrong -- measured before this increment's own
    AT-010 arms added five more call sites, then asserted as the post-state.
    Unpinned, nothing in the suite could contradict them; pinned, a drift is a
    red arm instead of a stale sentence nobody re-derives.

    The pin earned itself immediately, and has now caught the same drift THREE
    times: written at 32, red within the minute when the export-focus fix added
    two sites; red again at 34 when the diff-coverage arm added one.  Every one
    of those would have been a silently stale number in a document.  That is the
    whole argument for pinning a count rather than narrating it.
    """
    sites = render_call_sites()
    assert len(sites["argful"]) == 35, (
        f"derived {len(sites['argful'])} arg-ful call sites against a pinned 35; "
        "update the pin AND the module map together, or one of them is stale"
    )
    assert len(sites["zeroarg"]) == 25, (
        f"derived {len(sites['zeroarg'])} zero-arg Textual sites against a pinned "
        "25; a DROP means widget sites were wrongly swept into the A3"
    )
    assert len(render_definitions()) == 7, (
        f"derived {len(render_definitions())} definitions against a pinned 7 = "
        "six renderers plus `IRenderer.render` itself, which lives under "
        "mapper/views/ and is correctly swept in: the Protocol must satisfy the "
        "shape it declares"
    )


def test_tc_a3_the_instrument_can_tell_a_call_from_a_mention_of_a_call():
    """The positive control for the choice of AST over grep.

    A docstring naming `renderer.render(...)` is text, not a call, and a grep
    counts it.  This asserts the instrument does not -- which is the property
    the whole census rests on.
    """
    src = 'def f():\n    """calls renderer.render(graph, state) internally."""\n    return 1\n'
    calls = [n for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "render"]
    assert calls == []
    assert "renderer.render(" in src, "the fixture must contain the text a grep would match"

    real = "renderer.render(graph, state)\n"
    calls = [n for n in ast.walk(ast.parse(real))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "render"]
    assert len(calls) == 1, "the instrument must still see a real call"


def test_llr_n07_2_2a_every_definition_takes_graph_and_state():
    """Threshold 1: the migrated set EQUALS the derived definition set.

    Not `>= 6`.  The naive `grep -rn "def render" mapper/` returns 17, of which
    11 are Textual widgets that must NOT be migrated -- so a census that swept
    them in would pass a floor comfortably while being wrong by eleven.
    """
    defs = render_definitions()
    unmigrated = {
        f"{rel}:{ln}": [a.arg for a in node.args.args]
        for (rel, ln), node in defs.items()
        if [a.arg for a in node.args.args] != ["self", "graph", "state"]
    }
    assert unmigrated == {}


def test_llr_n07_2_2a_no_definition_keeps_kwargs_or_the_explicit_query():
    """Threshold 2: `**kwargs` == 0 across the set, and `query` left with them.

    Five of the six declared `**kwargs` and silently dropped `query` on the
    floor; the sixth took `query` explicitly.  Both shapes are gone.
    """
    offenders = {}
    for (rel, ln), node in render_definitions().items():
        if node.args.kwarg is not None:
            offenders[f"{rel}:{ln}"] = f"**{node.args.kwarg.arg}"
        stale = {a.arg for a in node.args.args} & {"query", "with_header", "diff",
                                                   "selected_id", "w", "h"}
        if stale:
            offenders[f"{rel}:{ln}"] = f"stale parameters {sorted(stale)}"
    assert offenders == {}


def test_llr_n07_2_2a_zero_call_sites_of_the_old_shape_survive():
    """Threshold 3 — THE CLAUSE THAT WAS MISSING ENTIRELY.

    Gating on definitions only is the named weaker variant: all six signatures
    change, the suite is green, and every call site still passes the old shape.
    The migration half-lands and two contracts are live at once.
    """
    old_shape = {"selected_id", "w", "h", "query", "with_header", "diff"}
    offenders = []
    for rel in tracked("mapper/*.py", "mapper/**/*.py", "tests/*.py", "tests/**/*.py"):
        for node in ast.walk(_parse(rel)):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "render"):
                continue
            names = {k.arg for k in node.keywords}
            if names & old_shape:
                offenders.append(f"{rel}:{node.lineno} old-shape keyword")
            elif None in names:
                # `render(g, **opts)` -- the keyword names are not statically
                # knowable, so this site is UNAUDITABLE by this census and is
                # banned rather than silently passed over.
                offenders.append(f"{rel}:{node.lineno} ** splat is unauditable")
            elif any(isinstance(a, ast.Starred) for a in node.args):
                # `render(*opts)` -- the same argument on the positional side:
                # the arity is not statically knowable either.
                offenders.append(f"{rel}:{node.lineno} * splat is unauditable")
            elif len(node.args) > 2:
                # `render(g, sel, w, h)` carries no keywords at all, so a
                # keyword-only check sees nothing.
                offenders.append(f"{rel}:{node.lineno} positional old shape")
    assert offenders == []


def test_llr_n07_2_2a_the_widget_protocol_was_not_swept_into_the_migration():
    """The false-failure arm: Textual's zero-arg `render()` must be untouched.

    A census that migrated these would break every widget in the app, and a
    floor-based gate could not tell the difference.
    """
    zeroarg = render_call_sites()["zeroarg"]
    assert len(zeroarg) == 25, (
        f"derived {len(zeroarg)} zero-arg sites against a pinned 25. A floor was "
        "used here first, in the one requirement that abolished floors: at `>= 20` "
        "five widget sites could be wrongly migrated with the arm still green"
    )


# --------------------------------------------------------------------------
# LLR-N07.2.3 — the two new types, and the interface's first mechanical guard


def renderer_classes():
    """Every class in `mapper/views/` that defines `render` — DERIVED.

    Iterating the protocol's satisfiers rather than a hand-listed roster is what
    makes a seventh renderer covered without anyone remembering to add it.
    """
    import importlib
    found = []
    for rel in tracked("mapper/views/*.py"):
        mod_name = rel[:-3].replace("/", ".")
        mod = importlib.import_module(mod_name)
        for name in dir(mod):
            obj = getattr(mod, name)
            if (isinstance(obj, type) and obj.__module__ == mod_name
                    and hasattr(obj, "render")
                    # The Protocol itself defines `render` and cannot be
                    # instantiated; it is the contract, not a satisfier of it.
                    and not getattr(obj, "_is_protocol", False)):
                found.append(obj)
    return found


def test_llr_n07_2_3_view_state_constructs_with_no_arguments():
    """Threshold 1. Reddens `M-N07.2.3-b`: required fields.

    With required fields every current test passes, and the NEXT increment
    adding a field breaks every existing construction -- whose natural repair is
    to pass the argument everywhere, converting the additive property into an
    A3 per field.
    """
    import dataclasses

    state = ViewState()
    assert state.selected_id is None and state.w == 80 and state.h == 24
    without_default = [
        f.name for f in dataclasses.fields(ViewState)
        if f.default is dataclasses.MISSING
        and f.default_factory is dataclasses.MISSING
    ]
    assert without_default == []


def test_llr_n07_2_3_view_state_is_frozen():
    """Constructed OUTSIDE the raises block, and the exception type is exact.

    Built inside it, making any field required would satisfy the assertion with
    the `TypeError` from CONSTRUCTION -- the arm would go green while proving
    nothing about frozen-ness. `Exception` is likewise broader than the property.
    """
    import dataclasses

    state = ViewState()
    with pytest.raises(dataclasses.FrozenInstanceError):
        state.selected_id = "x"


def test_llr_n07_2_3_every_renderer_satisfies_the_protocol():
    """Threshold 2 — a STRUCTURAL guard, and vacuous on its own.

    `runtime_checkable` makes `isinstance` check MEMBER PRESENCE ONLY, never
    signatures.  All six renderers had a `render` attribute before the
    migration, so this assertion is green on the unmigrated tree and proves
    nothing about the contract.  It catches a renderer that stops being one;
    the signature clause below is what makes the pair discriminating.
    """
    classes = renderer_classes()
    assert classes, "the derived renderer set is empty; the clause would be vacuous"
    assert all(isinstance(cls(), IRenderer) for cls in classes)


def test_llr_n07_2_3_every_renderer_signature_equals_graph_and_state():
    """Threshold 3 — the clause that reddens `M-N07.2.3-a`.

    Shipping the `isinstance` assertion alone is green on `master` with zero
    code changed.  This is derived with `inspect.signature`, not by eye.
    """
    classes = renderer_classes()
    assert classes
    wrong = {
        cls.__name__: list(inspect.signature(cls.render).parameters)
        for cls in classes
        if list(inspect.signature(cls.render).parameters) != ["self", "graph", "state"]
    }
    assert wrong == {}


def test_llr_cnv_3_1_the_two_focus_owner_rosters_cannot_drift():
    """`FOCUS_OWNERS` declares the domain; `_FOCUS_REGIONS` re-types it.

    Two independent lists of the same vocabulary is the shape that agrees on the
    day it is written and drifts the first time one is edited.  `FOCUS_OWNERS`
    has no production reader, so nothing else links them.
    """
    from mapper.app import MapScreen
    from mapper.views.state import FOCUS_OWNERS

    declared = set(FOCUS_OWNERS)
    used = {owner for _, owner in MapScreen._FOCUS_REGIONS}
    assert used <= declared, f"regions name owners outside the domain: {used - declared}"
    assert "" in declared, "the unknown owner must be a declared value"


def test_llr_n07_2_3_the_headless_boundary_still_holds():
    """A `ViewState` importing Textual would put the app's state model inside
    the headless boundary and make `export` untestable without an event loop.

    The check is over IMPORT NODES, not a substring.  A substring search matches
    this module's own docstring saying it imports no Textual -- measured, it
    false-failed on exactly that -- because a substring cannot tell a value from
    a mention of it.  The positive control below is what says the AST form can
    still see a real import.
    """
    def imports_textual(rel: str) -> bool:
        for node in ast.walk(_parse(rel)):
            if isinstance(node, ast.Import):
                if any(a.name.split(".")[0] == "textual" for a in node.names):
                    return True
            elif isinstance(node, ast.ImportFrom):
                if (node.module or "").split(".")[0] == "textual":
                    return True
        return False

    # Positive control: the probe must be able to report a non-absence.
    probe = ast.parse("from textual.widgets import Static\n")
    assert any(isinstance(n, ast.ImportFrom) and (n.module or "").startswith("textual")
               for n in ast.walk(probe))
    # Negative control: prose naming textual is not an import.
    assert not any(
        isinstance(n, (ast.Import, ast.ImportFrom))
        for n in ast.walk(ast.parse('"""imports no textual."""\n'))
    )

    offenders = [rel for rel in tracked("mapper/views/*.py") if imports_textual(rel)]
    assert offenders == []


def test_b44_the_module_map_pins_the_canvas_signature_against_the_real_one():
    """`B-44`: the map row was prose, and prose cannot observe a signature.

    `test_repair_map_truth.py` pins the `canvas` row as a substring and imports
    nothing, so it stayed green while the constructor gained two parameters.
    This asserts the row against `inspect.signature` instead.
    """
    from mapper.canvas import Canvas

    params = list(inspect.signature(Canvas.__init__).parameters)
    assert params == ["self", "w", "h", "tones", "fallback"]
    row = next(
        line for line in (REPO / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("| `canvas` |")
    )
    for name in params[1:]:
        assert name in row, f"the map's canvas row does not mention {name!r}"
