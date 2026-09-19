"""The export boundary, as a CENSUS over the view state rather than a patch list.

`focus_owner`, then `pan_x`/`pan_y`, then `selected_id` and `hits` were each
noticed one at a time, by a different reader, over three increments. That is a
ruling about a CLASS being discharged as a handful of instances: the gate is
green, the fold is correct, and all of it is evidence about the instances and
none about the axis -- so the next field is left for the next reviewer to find.

These arms close the axis instead. The classification is enumerated beside the
dataclass, every field must carry a row, and the export derives its strip set
from that table rather than spelling the fields a second time.
"""
from __future__ import annotations

import re
from dataclasses import fields, replace
from html import unescape

import pytest

from mapper.export import ExportError, ExportTooLarge, save_svg
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.layered import LayeredRenderer, pan_extent
from mapper.views.state import (
    EXPORT_FIELD_KINDS,
    TRANSIENT_EXPORT_FIELDS,
    ViewState,
    export_neutralised,
)


def test_every_view_state_field_is_classified_for_the_export_boundary():
    """BOTH WAYS, so neither side can drift silently.

    A field added to `ViewState` with no row here is the failure this exists to
    catch -- it would otherwise inherit whichever behaviour its neighbour had,
    which is exactly how `selected_id` and `hits` came to ride into the artifact
    while `focus_owner` beside them was being stripped.  A row here naming a
    field that no longer exists is the mirror failure, and a one-way arm is
    blind to it.
    """
    declared = set(EXPORT_FIELD_KINDS)
    actual = {f.name for f in fields(ViewState)}

    assert actual, "ViewState parsed to no fields at all -- the walk is broken"
    assert actual - declared == set(), (
        f"unclassified ViewState field(s): {sorted(actual - declared)}. "
        "Classify each as 'transient', 'content' or 'geometry' in "
        "EXPORT_FIELD_KINDS -- an export must not inherit a field's behaviour "
        "from whichever neighbour it was declared next to."
    )
    assert declared - actual == set(), (
        f"EXPORT_FIELD_KINDS classifies {sorted(declared - actual)}, which "
        "ViewState no longer has."
    )
    assert set(EXPORT_FIELD_KINDS.values()) <= {"transient", "content", "geometry"}


def test_the_transient_fields_are_the_ones_that_say_where_the_operator_was():
    """The classification is a judgement, so it is PINNED, not merely derived.

    Without this, `EXPORT_FIELD_KINDS` could be edited to call `hits` content
    and every other arm here would stay green -- the table would be checked for
    completeness and never for correctness.
    """
    assert TRANSIENT_EXPORT_FIELDS == {
        "selected_id",
        "focus_owner",
        "hits",
        "pan_x",
        "pan_y",
    }
    assert EXPORT_FIELD_KINDS["diff"] == "content"
    assert EXPORT_FIELD_KINDS["folded"] == "content"


def test_export_neutralised_strips_every_transient_field_and_keeps_content():
    """Driven off a state where EVERY field differs from its default.

    A fixture that left any field at its default would make "stripped" and
    "unchanged" indistinguishable for that field -- the vacuous-fixture case,
    and it is the whole risk in an arm about resetting to defaults.
    """
    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title="root")))

    loud = ViewState(
        selected_id="root",
        w=200,
        h=100,
        focus_owner="inspector",
        hits=frozenset({"root"}),
        diff=object(),
        pan_x=49,
        pan_y=10,
        folded=frozenset({"root"}),
    )
    # The fixture's own precondition, asserted: every transient field is
    # non-default going in, or this arm cannot see a strip that did not happen.
    defaults = {f.name: f.default for f in fields(ViewState)}
    for name in TRANSIENT_EXPORT_FIELDS:
        assert getattr(loud, name) != defaults[name], (
            f"fixture leaves {name} at its default, so stripping it is invisible"
        )

    out = export_neutralised(loud)

    for name in TRANSIENT_EXPORT_FIELDS:
        assert getattr(out, name) == defaults[name], f"{name} survived the export boundary"
    # Content and geometry are untouched.
    assert out.diff is loud.diff
    assert out.folded == frozenset({"root"})
    assert (out.w, out.h) == (200, 100)


def test_the_search_the_operator_ran_does_not_reach_the_artifact():
    """`hits` is the one that leaks the SENDER, not the map.

    Named separately from the sweep above because the sweep proves the mechanism
    and this proves the consequence: a reader of the export must not be able to
    recover what the operator was searching for.
    """
    state = ViewState(selected_id="secreto", hits=frozenset({"secreto", "otro"}))
    out = export_neutralised(state)
    assert out.hits == frozenset()
    assert out.selected_id is None


# --------------------------------------------------------------------------
# The budget: a refusal, never a crop


def _wide_and_deep(fan: int, depth: int) -> Graph:
    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title="root")))
    for i in range(fan):
        graph.add_node(Node(id=f"f{i}", ficha=Ficha(title=f"hoja {i}")))
        graph.add_edge(Edge("root", f"f{i}"))
    previous = "root"
    for i in range(depth):
        graph.add_node(Node(id=f"d{i}", ficha=Ficha(title=f"nivel {i}")))
        graph.add_edge(Edge(previous, f"d{i}"))
        previous = f"d{i}"
    return graph


@pytest.mark.asyncio
async def test_an_oversized_map_is_REFUSED_and_no_artifact_is_written(tmp_path):
    """The whole point of the ruling: nothing is written, and the operator is told.

    `B-68` is a file that LOOKS COMPLETE AND IS NOT.  A budget that cropped, or
    truncated, or shipped a best-effort picture would reinstate exactly that, so
    the assertion is the ABSENCE of the artifact -- the discriminating negative.
    A test that only checked the toast would pass on an implementation that
    warned and wrote a truncated file anyway.
    """
    from mapper.app import MapperApp, MapScreen

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("huge", _wide_and_deep(200, 100))
        app.push_screen(MapScreen("huge"))
        await pilot.pause()
        screen = app.screen
        path = screen.store.workspace / "huge.svg"
        if path.exists():
            path.unlink()

        # The precondition this arm rests on, asserted rather than assumed: the
        # map really is over budget.  Otherwise "no artifact" would be green for
        # the wrong reason.
        with pytest.raises(ExportTooLarge) as refused:
            screen._export_view_state(screen.size or app.size)
        assert refused.value.cells > MapScreen.EXPORT_MAX_CELLS

        await pilot.press("e")
        await pilot.pause()

        assert not path.exists(), (
            "an over-budget export wrote a file: a refusal is not a crop, and a "
            "partial artifact is the defect this whole ruling exists to refuse"
        )


_SVG_CELL = re.compile(
    r'<text[^>]*?x="([0-9.]+)"[^>]*?clip-path="url\(#[^)]*?-line-(\d+)\)"[^>]*?>(.*?)</text>',
    re.S,
)


def _emitted_rows(svg: str) -> list[str]:
    """The artifact's text layer, reassembled per line, in document order."""
    rows: dict[int, list[tuple[float, str]]] = {}
    for x, line_no, content in _SVG_CELL.findall(svg):
        rows.setdefault(int(line_no), []).append((float(x), unescape(content)))
    return ["".join(run for _, run in sorted(rows[n])) for n in sorted(rows)]


def _squash(text: str) -> str:
    return "".join(text.split())


@pytest.mark.parametrize(
    "leaves, title",
    [
        (8, "rama {}"),
        (20, "rama {}"),
        (40, "rama {}"),
        (120, "rama {}"),
        # `S-F10`: WIDE GLYPHS, and they are here because `cell_len` was
        # CORRECT AND UNPINNED.  `save_svg` measures the picture in terminal
        # CELLS, which is the only right unit for a canvas full of box-drawing
        # and CJK -- but every narrow-title case above passes identically under
        # `len()`, so substituting it left the whole suite green.  Measured: 45
        # tests green with `len()`, while a CJK title folds a row at every
        # shape through the real `e` chord.  `measured != pinned` in one line.
        #
        # Two conjuncts of the width expression were already mutated (the
        # console constant and the measured `+ 1`); this is the third, and it
        # was the one no arm could see.
        (20, "枝 {}"),
        (40, "分岐 {}"),
    ],
)
def test_no_rendered_row_is_folded_in_the_artifact(tmp_path, leaves, title):
    """`SEC-F1`: the export console must be sized to the picture it is given.

    It was built at a hard-coded `width=200`.  That was invisible while the
    caller sized its render from the terminal; once the export sized from the
    MAP, an ordinary map exceeded it and Rich folded every row past 200 into
    stacked chunks in row-major order -- every title present, file well-formed,
    tree adjacency destroyed.  A file that looks complete and is not, which is
    the defect class the export ruling exists to refuse.

    THE ORACLE IS ROW IDENTITY, NOT ROW COUNT.  A line-count ratio reported a
    uniform 1.03 at every width including 118 -- below even the old 200-column
    console, where folding is impossible -- because a trailing blank line adds
    a constant. Uniformity across heterogeneous inputs was the tell.  A fold
    means ONE rendered row arrives as TWO emitted rows, so the discriminating
    question is whether each rendered row survives WHOLE.
    """
    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title="raiz")))
    for i in range(leaves):
        graph.add_node(Node(id=f"h{i}", ficha=Ficha(title=title.format(i))))
        graph.add_edge(Edge("root", f"h{i}"))

    state = ViewState(selected_id=None, w=118, h=34)
    for _ in range(6):
        (ex, sx), (ey, sy) = pan_extent(graph, state)
        if ex <= sx and ey <= sy:
            break
        state = replace(
            state, w=state.w + max(0, ex - sx) + 2, h=state.h + max(0, ey - sy) + 1
        )

    text = LayeredRenderer().render(graph, state)
    path = tmp_path / "folded.svg"
    save_svg(text, path)

    rendered = [_squash(r) for r in text.plain.split("\n") if _squash(r)]
    emitted = [_squash(r) for r in _emitted_rows(path.read_text(encoding="utf-8")) if _squash(r)]

    assert rendered, "the render produced no non-blank rows; the fixture is broken"
    assert emitted, "the artifact's text layer reassembled to nothing; the reader is broken"

    split = [row for row in rendered if row not in emitted]
    assert not split, (
        f"{len(split)} rendered row(s) arrived split across two emitted rows -- "
        f"the console folded the picture. First: {split[0][:60]!r}"
    )


@pytest.mark.asyncio
async def test_an_extent_that_never_settles_REFUSES_instead_of_shipping_what_it_had(
    tmp_path, monkeypatch
):
    """The exhaustion branch, pinned rather than argued about.

    On every shape measured the extent settles in ONE growth step, so no input
    reaches this branch and a battery over it reports a survivor: reverting the
    refusal to `return state` leaves the whole file green.  A survivor explained
    away is still a survivor, and the axis it moves -- does a non-converging
    extent refuse, or ship whatever it had reached? -- is the ruling's own
    clause, because shipping it would toast "exportado" over a cropped artifact
    with no pan to blame.  No clause is missing; the ARM was.

    THE BRANCH IS FORCED, AND THE FORCING IS THE HONEST PART.  The budget is
    lowered to zero steps, which is the one input that makes convergence
    impossible.  That is a statement about the loop's contract, not about a map
    an operator can build, and the arm claims nothing more than that.
    """
    from mapper.app import MapperApp, MapScreen

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("necia", _wide_and_deep(6, 6))
        app.push_screen(MapScreen("necia"))
        await pilot.pause()
        screen = app.screen
        path = screen.store.workspace / "necia.svg"
        if path.exists():
            path.unlink()

        monkeypatch.setattr(MapScreen, "EXPORT_EXTENT_STEPS", 0)

        with pytest.raises(ExportError) as refused:
            screen._export_view_state(screen.size or app.size)
        # NOT `ExportTooLarge`: an extent that did not converge is a different
        # event from one that was too big, and a refusal that names the wrong
        # cause hands the operator advice that cannot help.
        assert not isinstance(refused.value, ExportTooLarge)
        assert "did not settle" in str(refused.value)

        await pilot.press("e")
        await pilot.pause()

        assert not path.exists(), (
            "an extent that never settled still wrote a file -- that is a "
            "cropped artifact with nothing to blame it on"
        )


@pytest.mark.asyncio
async def test_the_refusal_TELLS_the_operator_and_names_the_way_forward(tmp_path):
    """The second half of the refusal, pinned by its own arm.

    "It refuses" and "AND IT SAYS SO" are two claims that fail independently: a
    change that keeps the refusal and drops the notice leaves the operator
    pressing `e` and watching nothing happen, with the arm above still green.
    An affordance that declines owes a pin per half.

    THE MESSAGE IS ACTIONABLE OR IT IS NOT A REFUSAL.  Withdrawing a capability
    and saying only "no" is a regression wearing a safeguard's clothes, so the
    assertions are the three things the operator needs to act: how big the map
    is, what the limit is, and that `f` focuses a subtree they can export.
    """
    from mapper.app import MapperApp, MapScreen

    notices: list[str] = []
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("huge", _wide_and_deep(200, 100))
        app.push_screen(MapScreen("huge"))
        await pilot.pause()
        screen = app.screen
        screen.notify = lambda msg, **kw: notices.append(str(msg))

        await pilot.press("e")
        await pilot.pause()

        assert len(notices) == 1, f"expected exactly one refusal notice, got {notices}"
        message = notices[0]

    assert "celdas" in message, f"the refusal does not say how big the map is: {message!r}"
    assert str(MapScreen.EXPORT_MAX_CELLS) in message, (
        f"the refusal does not name the limit it is enforcing: {message!r}"
    )
    # The route out, not merely the diagnosis.  `f` is the chord mapper already
    # ships for focusing a subtree, so the operator is not left without a path.
    assert " f " in message, (
        f"the refusal does not name the chord that makes the map exportable: {message!r}"
    )


@pytest.mark.asyncio
async def test_a_refusal_DECLARES_the_stale_artifact_it_leaves_behind(tmp_path):
    """`N2`: refusing to write leaves the LAST export sitting at the same path.

    THE ARM ABOVE CANNOT SEE THIS, AND THAT IS WHY THIS ONE EXISTS.
    `test_an_oversized_map_is_REFUSED_and_no_artifact_is_written` `unlink()`s
    before it presses, so it runs in a world where no prior artifact ever
    existed -- structurally blind to the only case where staleness is possible.
    The blind spot was in the SETUP, not in the assertion.

    THE HARM IS THE BATCH'S OWN FAMILY, ONE SEAM OVER.  `B-68` is *a file that
    looks current and is not*.  After a refusal the operator has been told the
    export declined -- but a file still sits at the path the success toast
    names, and nothing says it is old.  Recorded as the SIXTH instance of *the
    increment that closes a defect family is the increment most likely to
    introduce a member of it*, WITH ITS MITIGATION STATED: the operator was
    told the export refused, just not that the old file persists.  Partial
    mitigation is still an instance.

    DECLARED, NOT DELETED.  The standard is that nothing is hidden without
    being declared, not that nothing stale exists, so the fix is the sentence.
    Deleting the operator's file on a refusal without confirmation is the
    destructive act `US-N05` already rules against.
    """
    from mapper.app import MapperApp, MapScreen

    notices: list[str] = []
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        # A map that EXPORTS, so a real prior artifact exists on disk.
        app.store.save("crece", _wide_and_deep(3, 3))
        app.push_screen(MapScreen("crece"))
        await pilot.pause()
        screen = app.screen
        path = screen.store.workspace / "crece.svg"

        await pilot.press("e")
        await pilot.pause()
        assert path.exists(), "the fixture never produced a first artifact"
        first = path.read_bytes()

        # The same map grows past the budget. The operator presses `e` again.
        screen.graph = _wide_and_deep(200, 100)
        screen.notify = lambda msg, **kw: notices.append(str(msg))
        await pilot.press("e")
        await pilot.pause()

        assert len(notices) == 1, f"expected exactly one refusal notice, got {notices}"
        message = notices[0]

        # The refusal still refuses: nothing was overwritten, no partial write.
        assert path.read_bytes() == first, (
            "the refused export modified the artifact on disk -- a refusal is not a write"
        )

    # AND IT SAYS THE FILE IS THERE AND OLD. Both halves, because "a file
    # remains" and "it is stale" are separate things for the operator to know.
    assert str(path) in message, (
        f"the refusal does not name the file it left behind: {message!r}"
    )
    # The FULL PHRASE, not the bare word. `anterior` appears in seven places in
    # the product (`N anterior`, the settings rail, two keymap labels), so an
    # arm keyed on it alone would be one refactor away from passing for a
    # reason that has nothing to do with staleness.
    assert "exportación anterior" in message, (
        f"the refusal names the file but never says it is STALE, which is the "
        f"whole finding -- an undeclared old artifact at the expected path: {message!r}"
    )


@pytest.mark.asyncio
async def test_a_refusal_does_not_call_a_CURRENT_artifact_stale(tmp_path):
    """`CR17-F2`: `path.exists()` tests EXISTENCE, not STALENESS.

    The guard and the sentence were not the same claim. The sentence said the
    file "ya no refleja este mapa"; the guard established only that a file is
    there. Measured: export a map, change NOTHING about the graph, then make the
    same map exceed the budget -- the artifact on disk is still a faithful
    export of that exact graph, and the refusal called it stale anyway.

    The no-file negative control below could not see this. It covers "the claim
    is ABSENT when there is no file"; this covers "the claim is TRUE whenever it
    is made", and those are different obligations.
    """
    from mapper.app import MapperApp, MapScreen

    notices: list[str] = []
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("crece", _wide_and_deep(3, 3))
        app.push_screen(MapScreen("crece"))
        await pilot.pause()
        screen = app.screen
        path = screen.store.workspace / "crece.svg"

        await pilot.press("e")
        await pilot.pause()
        assert path.exists(), "the fixture never produced a first artifact"
        before = path.read_bytes()

        # THE GRAPH IS NOT TOUCHED. Only the budget verdict changes.
        screen.EXPORT_MAX_CELLS = 1
        screen.notify = lambda msg, **kw: notices.append(str(msg))
        await pilot.press("e")
        await pilot.pause()

        assert len(notices) == 1, f"expected exactly one refusal notice, got {notices}"
        message = notices[0]
        assert path.read_bytes() == before, "the refused export rewrote the artifact"

    # The file is a FAITHFUL export of the unchanged graph, so any sentence
    # asserting it no longer reflects the map is FALSE.
    assert "ya no refleja" not in message, (
        "the refusal calls a CURRENT artifact stale: the graph never changed, so "
        f"the file on disk still reflects it exactly. {message!r}"
    )


@pytest.mark.asyncio
async def test_a_refusal_on_a_FIRST_export_claims_no_stale_file(tmp_path):
    """The negative control for the arm above: the claim must never be FALSE.

    "the file there is stale" is a claim about the world. On a map's first
    export there is no file, so a refusal that said it anyway would be telling
    the operator something untrue -- and the cheapest way to pass the arm above
    is to append that sentence unconditionally. This is what forbids it.
    """
    from mapper.app import MapperApp, MapScreen

    notices: list[str] = []
    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("huge", _wide_and_deep(200, 100))
        app.push_screen(MapScreen("huge"))
        await pilot.pause()
        screen = app.screen
        path = screen.store.workspace / "huge.svg"
        if path.exists():
            path.unlink()
        screen.notify = lambda msg, **kw: notices.append(str(msg))

        await pilot.press("e")
        await pilot.pause()

        assert len(notices) == 1, f"expected exactly one refusal notice, got {notices}"
        message = notices[0]
        assert not path.exists(), "a refused first export wrote a file"

    assert "exportación anterior" not in message, (
        f"the refusal claims a previous export exists when none does: {message!r}"
    )


@pytest.mark.asyncio
async def test_a_live_search_and_a_moved_cursor_do_not_reach_the_artifact(tmp_path):
    """The axis, driven END TO END through the real chords.

    The arms above assert `export_neutralised` in isolation, which proves the
    HELPER and says nothing about whether the export calls it -- an arm that
    builds its own subject cannot see the call site change.  This one runs the
    operator's real sequence: `/` to search, `n` to move the cursor onto a hit,
    `e` to export.

    `hits` is the sharp one.  It is the resolution of whatever the operator last
    typed into search, so an artifact that carries it tells the recipient what
    the SENDER was looking for -- information about the sender, not about the
    map, in a file that leaves the machine.

    THE ORACLE IS BYTE-INVARIANCE ACROSS A CHANGE THAT DEMONSTRABLY MOVES THE
    PICTURE.  Invariance alone would be green if the session state were inert,
    so the positive control below asserts the on-screen canvas really does
    change between the two exports; only then does an unchanged artifact mean
    the boundary held rather than that nothing happened.
    """
    from mapper.app import MapperApp, MapScreen

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("sesion", _wide_and_deep(6, 6))
        app.push_screen(MapScreen("sesion"))
        await pilot.pause()
        screen = app.screen
        path = screen.store.workspace / "sesion.svg"

        def painted():
            """What the CANVAS draws right now, session state and all."""
            text = screen._current_renderer().render(
                screen.graph, screen._view_state(*screen._canvas_size())
            )
            return text.plain, [(s.start, s.end, str(s.style)) for s in text.spans]

        before_screen = painted()

        if path.exists():
            path.unlink()
        await pilot.press("e")
        await pilot.pause()
        assert path.exists(), "the `e` chord produced no artifact at rest"
        at_rest = path.read_bytes()

        # The operator searches, and then steps onto a hit.
        await pilot.press("slash")
        await pilot.pause()
        for ch in "hoja":
            await pilot.press(ch)
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("n")
        await pilot.pause()

        # TRIGGERS ASSERTED BEFORE THE INVARIANT.  Both of them: the search
        # resolved to something, and the cursor is somewhere the export could
        # encode.
        hits = screen._search_hits()
        assert hits, "the search matched nothing, so 'the search does not leak' is vacuous"
        assert screen.nav.cursor is not None, "no cursor to leak"

        # POSITIVE CONTROL.  If the session state does not move the picture on
        # screen, byte-equality of the two artifacts is true for a reason that
        # has nothing to do with the export boundary.
        assert painted() != before_screen, (
            "the live search and cursor move changed nothing on the canvas, so "
            "an unchanged export proves nothing about what the export strips"
        )

        path.unlink()
        await pilot.press("e")
        await pilot.pause()
        assert path.exists(), "the `e` chord produced no artifact after the search"
        with_session = path.read_bytes()
        searched_for = sorted(hits)

    assert with_session == at_rest, (
        "the exported SVG changed once the operator searched and moved the "
        f"cursor: {len(at_rest)} bytes at rest against {len(with_session)} with "
        f"{len(searched_for)} hits live. An export must not tell its recipient "
        "what the sender was looking for."
    )


@pytest.mark.asyncio
async def test_an_ordinary_map_still_exports(tmp_path):
    """The negative control for the budget.

    A rule that false-fails correct work is as expensive as one that passes
    wrong work, and the cheapest way to pass the arm above is to refuse
    everything.  This is the arm that makes that cheat visible.
    """
    from mapper.app import MapperApp, MapScreen

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("ordinaria", _wide_and_deep(6, 6))
        app.push_screen(MapScreen("ordinaria"))
        await pilot.pause()
        screen = app.screen
        path = screen.store.workspace / "ordinaria.svg"
        if path.exists():
            path.unlink()

        state = screen._export_view_state(screen.size or app.size)
        assert state.w * state.h <= MapScreen.EXPORT_MAX_CELLS

        await pilot.press("e")
        await pilot.pause()

    assert path.exists(), "an ordinary map was refused; the budget is too tight"
    assert path.stat().st_size > 0
