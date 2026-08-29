"""HLR-N06.2 — a folded branch is declared with its hidden count.

`TC-032`, `TC-033`, `AT-013`, `AT-014`, `AT-017`, and the SUPERSESSION census
for `OutlineRail.collapsed` / `OutlineRail.toggle`.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

import pytest
from textual.dom import BadIdentifier

from mapper import darkside
from mapper.app import MapperApp
from mapper.model import Attachment, Edge, Ficha, Graph, Node, SchemaField
from mapper.views.layered import FOLD_PILL_TOKEN, LayeredRenderer, painted_ids
from mapper.views.state import ViewState
from mapper.widgets.rail import OutlineRail
from tests.inc3_support import (
    canvas_rows,
    frame_rows,
    hidden_under,
    install,
    open_map,
    rows_in,
)

REPO = Path(__file__).resolve().parents[1]
CONTEXT_OF_USE = (118, 34)
# R-013's regime: `_apply_region_visibility` auto-hides the rail below 118
# columns, which is the whole reason fold had to leave the rail.
RAIL_HIDDEN_SIZE = (80, 24)

_PILL = re.compile(re.escape(FOLD_PILL_TOKEN) + r"\s*(.*?)\s*\+(\d+)")


def pill_counts(rows: list[str]) -> list[int]:
    """Every numeral painted on a fold pill, from the frame.

    Over PAINTED pills, never over the `folded` set: a pill for a branch nested
    inside another folded branch is not painted, and summing `folded` would
    double-count its descendants.
    """
    return [int(m.group(2)) for m in _PILL.finditer(" ".join(rows))]


# --------------------------------------------------------------------------
# LLR-N06.2.1 — one owner, two readers


def test_tc_032_fold_has_one_owner_and_the_rail_only_renders_it(tmp_path):
    """The rail reflects a folded set it was HANDED and never stored one."""
    graph = install(tmp_path, "legacy")
    rail = OutlineRail()
    rail.show(graph, "fin", frozenset())
    assert [nid for nid, _ in rail.visible_rows()] == [
        "erp", "fin", "cont", "pres", "rrhh", "nom", "inv", "alm"
    ]

    rail.show(graph, "fin", frozenset({"fin"}))
    assert [nid for nid, _ in rail.visible_rows()] == [
        "erp", "fin", "rrhh", "nom", "inv", "alm"
    ]
    assert "▸" in rail.render().plain

    # Handed the empty set again it forgets: no set of its own survives.
    rail.show(graph, "fin", frozenset())
    assert len([nid for nid, _ in rail.visible_rows()]) == 8


@pytest.mark.asyncio
async def test_tc_032_the_canvas_and_the_rail_read_ONE_fold_set(tmp_path):
    """Two owners of one truth is how the rail and the canvas start disagreeing.

    Driven through the real `z`, so what is asserted is the wiring rather than
    two objects a test set by hand.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("legacy", install(tmp_path, "legacy"))
        screen = await open_map(app, pilot, "legacy")
        screen.nav.cursor = "fin"
        screen.refresh_canvas()
        await pilot.pause()

        await pilot.press("z")
        await pilot.pause()
        rail = screen.query_one("#map-rail", OutlineRail)
        assert screen.folded == frozenset({"fin"})
        assert rail.folded == screen.folded
        assert "cont" not in [nid for nid, _ in rail.visible_rows()]
        assert pill_counts(canvas_rows(screen)) == [2]

        await pilot.press("z")
        await pilot.pause()
        assert screen.folded == frozenset()
        assert rail.folded == frozenset()
        assert pill_counts(canvas_rows(screen)) == []


# --------------------------------------------------------------------------
# The SUPERSESSION census — derived over BOTH trees, never enumerated


def _tracked(*globs) -> list[str]:
    out = subprocess.run(["git", "ls-files", *globs], cwd=REPO,
                         capture_output=True, text=True, check=True)
    return out.stdout.split()


def superseded_sites(sources: dict[str, str]) -> list[tuple[str, int, str]]:
    """Every `.collapsed` attribute access and every `.toggle(...)` call.

    AST, not grep: a mention inside a docstring or a comment is not a reference,
    and this batch has already paid for a grep that counted one.
    """
    found: list[tuple[str, int, str]] = []
    for path, blob in sorted(sources.items()):
        for node in ast.walk(ast.parse(blob)):
            if isinstance(node, ast.Attribute) and node.attr == "collapsed":
                found.append((path, node.lineno, "collapsed"))
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "toggle"):
                found.append((path, node.lineno, "toggle"))
    return found


def test_tc_032_the_supersession_instrument_can_see_a_reference():
    """NON-EMPTY BEFORE IT IS EVALUATED, and this is how that is established.

    A census asserting a zero over an instrument that can find nothing is a
    census that would pass on a tree where the deletion never happened.  Fed the
    shipped pre-state's own shapes -- the PRODUCTION call site `app.py:1259` and
    the byte-identity guard `test_repair_depth.py:1055`, both of which the
    earlier enumeration MISSED -- the instrument returns both.
    """
    pre_state = {
        "app.py": "self.query_one('#map-rail', OutlineRail).toggle(self.nav.cursor)\n",
        # A WRITE and a READ, because the shipped rail had both and a census that
        # only sees assignments leaves the reads behind.
        "rail.py": (
            "class R:\n"
            "    def f(self):\n"
            "        self.collapsed = set()\n"
            "    def g(self, nid):\n"
            "        return nid in self.collapsed\n"
        ),
        "guard.py": "rail.collapsed = set(collapsed)\n",
        "docstring.py": "'''mentions rail.collapsed and .toggle() in prose'''\n",
    }
    sites = superseded_sites(pre_state)
    assert len(sites) == 4, sites
    assert {p for p, _, _ in sites} == {"app.py", "rail.py", "guard.py"}
    assert sorted(kind for _, _, kind in sites) == [
        "collapsed", "collapsed", "collapsed", "toggle"
    ]
    # The control for the choice of AST over grep: prose is not a reference.
    assert "docstring.py" not in {p for p, _, _ in sites}


def test_tc_032_no_reference_to_the_deleted_fold_state_survives():
    """LLR-N06.2.1 — EMPTY AFTER, over `mapper/**` AND `tests/**`.

    Both trees, because the enumeration that stopped at `tests/test_rail.py` was
    a strict subset of the real set and the two members it missed were the two
    that mattered: a production call site, and the guard that exists to prove
    the rail did not change.
    """
    paths = _tracked("mapper/*.py", "mapper/**/*.py", "tests/*.py", "tests/**/*.py")
    assert len(paths) > 30, "the derived file set collapsed; the clause is vacuous"
    sources = {p: (REPO / p).read_text(encoding="utf-8") for p in paths}
    assert superseded_sites(sources) == []
    assert not hasattr(OutlineRail, "toggle")
    assert "collapsed" not in vars(OutlineRail())


def test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts():
    """The batch's own rule, applied to the tree that RECORDS the batch.

    Every hostile payload in this suite is built with `chr(0x…)` at test time
    precisely so no file holds one -- batch 1 shipped a literal backspace in a
    fixture and the resulting test passed on everything.  The sweep enforcing
    that covered `mapper/` and `tests/` and stopped there, and two prior-batch
    `.dev-flow` artifacts were carrying live code points: `U+202E` twice in a
    SECURITY REVIEW (unterminated, so it reorders the very text documenting the
    threat) and `U+200D` four times in a review confirmation.  Both now spell
    the code point's NAME.

    `.dev-flow` is corpus: it is synced to a vault, it is read by scanners, and
    it is the kind of artifact that ends up in a client-facing report.  The
    directory this batch writes into is the one place a rule about hostile code
    points was not being applied to itself.

    THE ARTIFACT HALF IS AN `rglob`, NOT `git ls-files`, and that is the same
    correction `test_llr_coerce_1_no_test_retypes_the_range_list` already
    records one module over: the artifacts an increment is writing RIGHT NOW are
    untracked, so a tracked-file sweep is blind exactly where new work lands —
    which is the only place this rule can still be broken.  The source half
    keeps `git ls-files`, because `LLR-S06.3.1` names that command and scopes it
    to tracked product source.

    THE MAP DATA IS IN SCOPE TOO, because the defect this rule exists for was a
    literal backspace in a FIXTURE, and until now `fixtures/` and `maps/` — the
    `.mmd` / `.yml` pairs the product actually loads — were the one place the
    docstring's own motivating example could still be planted undetected.
    Measured: `U+200B` planted in `fixtures/anidado.mmd` and in `maps/legacy.mmd`
    passed this arm before these globs were added.  `mapper.db` is untracked and
    therefore never reaches the read below, which is why `git ls-files` and not
    a glob of the directory.

    THE WIDENING IS ASSERTED STRUCTURALLY, NOT AGAINST TODAY'S TRACKING STATE.
    The first version of this clause asserted the `rglob` view was a STRICT
    superset of the `git ls-files` view -- true only while some artifact happens
    to be uncommitted, which is to say true only mid-increment.  Measured, 91
    artifacts with 84 tracked: committing the increment that introduced the
    clause makes the two sets equal and turns the guard red on its own landing,
    for a reason that has nothing to do with the rule it enforces.  The two
    clauses below say the same thing without depending on what is committed --
    the `rglob` is not NARROWER than the tracked query (the instrument
    comparison, which a commit can only strengthen), and it really does reach a
    file `git ls-files` cannot see (driven by a probe this arm creates, so the
    property is exercised rather than inferred from the day's tracking state).

    `\\t` and `\\n` are excluded exactly as every other clause in this suite
    excludes them, and this file exempts itself from nothing -- it spells no
    payload either.
    """
    banned = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}
    sources = _tracked(
        "mapper/*.py", "mapper/**/*.py", "tests/*.py", "tests/**/*.py",
        "fixtures/*", "fixtures/**/*", "maps/*", "maps/**/*",
    )
    data = [p for p in sources if not p.endswith(".py")]

    def _artifacts() -> list[str]:
        return sorted(
            str(p.relative_to(REPO)).replace("\\", "/")
            for pattern in ("*.md", "*.json")
            for p in (REPO / ".dev-flow").rglob(pattern)
        )

    # THE RGLOB REACHES UNTRACKED FILES, asserted by construction rather than by
    # noticing that some artifact happens to be uncommitted today.
    probe = REPO / ".dev-flow" / "_scan_probe.md"
    assert not probe.exists(), f"{probe} already exists; a previous run leaked it"
    probe.write_text("scan probe\n", encoding="utf-8")
    try:
        assert ".dev-flow/_scan_probe.md" in _artifacts(), (
            "the rglob does not see an untracked artifact; it is the tracked "
            "sweep wearing a different instrument"
        )
    finally:
        probe.unlink()

    artifacts = _artifacts()
    # EVERY HALF ASSERTED NON-EMPTY ON ITS OWN, because a glob that matches
    # nothing makes the widening a no-op that reads like a fix.
    assert len(artifacts) > 20, artifacts
    assert len(sources) > 30, "the source half collapsed"
    assert len(data) >= 6, f"the fixtures/maps half collapsed: {data}"
    # And the rglob is not NARROWER than the tracked view, or it is the same
    # sweep wearing a different instrument.
    missed = sorted(set(_tracked(
        ".dev-flow/*.md", ".dev-flow/**/*.md",
        ".dev-flow/*.json", ".dev-flow/**/*.json",
    )) - set(artifacts))
    assert missed == [], f"the rglob half is narrower than the tracked view: {missed}"

    offenders = []
    for rel in sources + artifacts:
        blob = (REPO / rel).read_text(encoding="utf-8")
        found = sorted({hex(ord(c)) for c in blob
                        if ord(c) in banned and c not in "\t\n"})
        if found:
            offenders.append((rel, found))
    assert offenders == [], offenders


# --------------------------------------------------------------------------
# LLR-N06.2.3 — the pill coerces


def _hostile(prefix: str) -> str:
    """Constructed from code points at TEST TIME, never spelled into a source.

    Batch 1 shipped a literal backspace byte in a fixture and the resulting test
    passed on everything.
    """
    return (
        prefix
        + chr(0x01)                       # C0
        + chr(0x202E) + "oculto" + chr(0x202C)   # a BALANCED RTL override
        + chr(0x200B)                     # zero width
        + "[bold red]markup[/]"
    )


def _hostile_graph() -> Graph:
    """The `LLR-N06.2.3` fixture, WIDENED past the ficha strings.

    The narrow version carried titles and nothing else, so three of the four
    regions it swept painted almost nothing: no schema meant the inspector built
    no field rows, no attachments meant its attachment chip was never reached,
    and no documents meant the factory tree had nothing to draw.  Mutation-
    tested, `inspector.py:155`'s coercion could be deleted with all 789 arms
    green.  Widening the fixture is what turns those silent survivors into red
    arms.

    THE SCHEMA KEYS ARE DELIBERATELY IDENTIFIER-SAFE while the LABELS carry the
    payload, and that is a bound on this fixture rather than an oversight:
    `FichaInspector._rows` interpolates the raw key into a Textual widget id, so
    a key outside `[A-Za-z_-][A-Za-z0-9_-]*` raises `BadIdentifier` out of
    `_rebuild` and KILLS THE APP before any region can be read (finding `F-A`,
    pre-existing at `954f8f3`, routed to Inc-REPAIR).  Putting a hostile key
    here would not widen this census, it would replace it with a crash.  The
    obligation is carried instead by the strict-xfail arm below, which fails the
    moment `F-A` is fixed and forces this fixture to be widened again.
    """
    graph = Graph()
    payload = [
        Attachment(kind="url", path=_hostile("http://x/"), caption=_hostile("cap")),
        Attachment(kind="file", path=_hostile("a/b.txt"), caption=_hostile("doc")),
    ]
    fields = {"D": _hostile("acta"), "obs": _hostile("nota")}
    graph.add_node(Node(id="root", ficha=Ficha(
        title=_hostile("raiz"), meta="m", notes=_hostile("n"),
        fields=dict(fields), attachments=list(payload))))
    for i in range(3):
        graph.add_node(Node(id=f"b{i}", ficha=Ficha(
            title=_hostile(f"rama{i}"), meta="m", notes=_hostile("n"),
            fields=dict(fields), attachments=list(payload))))
        graph.add_edge(Edge(parent_id="root", child_id=f"b{i}"))
        graph.add_node(Node(id=f"h{i}", ficha=Ficha(
            title=_hostile(f"hoja{i}"), meta="m",
            fields=dict(fields), attachments=list(payload))))
        graph.add_edge(Edge(parent_id=f"b{i}", child_id=f"h{i}"))
    graph.schema = [
        SchemaField(key="D", label=_hostile("acta")),
        SchemaField(key="obs", label=_hostile("obs")),
    ]
    return graph


def test_tc_033_the_fold_pill_coerces_a_hostile_branch_title(tmp_path):
    """Measured ON THE PAINTED ROW, never on the string handed to the sink."""
    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title=_hostile("rama"), meta="m")))
    for i in range(3):
        graph.add_node(Node(id=f"k{i}", ficha=Ficha(title=_hostile(f"h{i}"), meta="m")))
        graph.add_edge(Edge(parent_id="root", child_id=f"k{i}"))

    banned = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}
    assert {0x01, 0x202E, 0x202C, 0x200B} <= banned, (
        "the hostile input is not in COERCION_RANGES; this arm proves nothing"
    )

    painted = LayeredRenderer().render(
        graph, ViewState(w=80, h=24, folded=frozenset({"root"}))
    ).plain
    assert FOLD_PILL_TOKEN in painted, "no pill painted; the arm would be vacuous"
    leaked = sorted({hex(ord(c)) for c in painted
                     if ord(c) in banned and c not in "\t\n"})
    assert leaked == []

    # Rich markup is not INTERPRETED: `Text` does not parse it, so the literal
    # survives as text rather than becoming a style.  Asserted on its own short
    # title, because in the hostile title above the markup is past `card_w` and
    # is clipped away -- which would make this a test of truncation, not of
    # markup handling.
    marked = Graph()
    marked.add_node(Node(id="root", ficha=Ficha(title="[bold red]x[/]", meta="m")))
    marked.add_node(Node(id="kid", ficha=Ficha(title="hijo", meta="m")))
    marked.add_edge(Edge(parent_id="root", child_id="kid"))
    shown = LayeredRenderer().render(
        marked, ViewState(w=140, h=45, folded=frozenset({"root"}))
    ).plain
    assert "[bold red]x[/]" in shown

    # The SPLIT-AT-WIDTH arm.  Truncation MANUFACTURES the defect out of a
    # source that was balanced, so the ordering clause is not vacuous.
    from mapper.views.layered import _fit
    source = "a" * 4 + chr(0x202E) + "b" * 20 + chr(0x202C)
    assert source.count(chr(0x202E)) == source.count(chr(0x202C)) == 1
    cut = _fit(source, 10)
    assert len(cut) == 10
    assert cut.count(chr(0x202E)) == 0, "an unterminated override survived the cut"


@pytest.mark.asyncio
async def test_llr_n06_2_3_every_repainted_region_coerces_what_it_paints(tmp_path):
    """The census `LLR-N06.2.3` SCOPES, driven over the regions themselves.

    The clause is "every file-derived string painted on a surface this batch
    touches, WHETHER ITS SINK IS NEW OR PRE-EXISTING", and the previous arm
    covered only the new one (the fold pill).  `refresh_canvas` is what this
    increment restructured, so its scope is the regions `refresh_canvas`
    repaints -- which is how `_minimap_text` was missed: it interpolated
    `ficha.title` with no `darkside.plain`, and nine hostile code points reached
    the composited frame, including a `U+202E` that displays one branch's
    coverage under a neighbour's name.  That is the one widget whose entire job
    is telling the operator WHICH branch is at risk.

    So the regions are enumerated from the widget ids `refresh_canvas` writes to
    and each is read off the COMPOSITED FRAME, not off the `Text` handed to the
    sink.  Terminal-only: the minimap is not part of the export, which is why
    `save_svg` is the sibling arm's subject and not this one's.
    """
    graph = _hostile_graph()

    banned = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}
    # POSITIVE CONTROL on the payload, before any region is read.
    assert any(ord(c) in banned for c in graph.nodes["b0"].ficha.title)
    # AND ON THE SHAPES THE FIXTURE DID NOT USED TO CARRY.  It had no schema, no
    # attachments and no documents, which is why the inspector region was swept
    # while rendering almost nothing: `insp-field-*` rows and the attachment
    # chip were never constructed at all, so `inspector.py:155`'s coercion had
    # nothing standing on it (mutation-tested: removing it survived all 789
    # arms).  A census that reads "no leak" off a region that never rendered is
    # reporting nothing.
    assert graph.schema, "no schema; the inspector paints no field rows"
    assert graph.nodes["b0"].ficha.attachments, "no attachments; the chip is unreached"
    assert any(
        ord(c) in banned for a in graph.nodes["b0"].ficha.attachments
        for c in a.caption + a.path + a.kind
    )
    assert any(ord(c) in banned for sf in graph.schema for c in sf.label)

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("hostil", graph)
        screen = await open_map(app, pilot, "hostil")
        screen.refresh_canvas()
        await pilot.pause()
        # The graph really did survive the round trip; without this the sweep
        # below runs on `MapScreen`'s one-node "error" fallback and is green on
        # a map that carries nothing hostile at all.
        assert len(screen.graph.nodes) == 7, sorted(screen.graph.nodes)
        # THE APP IS STILL RUNNING, asserted BEFORE anything is read.  A census
        # that looks only for banned code points in painted rows answers "no
        # leak" identically for a clean screen and for a screen that never
        # rendered -- and `F-A` is exactly that: a schema key outside Textual's
        # identifier grammar raises out of the inspector rebuild, scheduled by
        # `call_next` from `refresh_canvas`, outside every guard, and the frame
        # the sweep then reads belongs to a dead application.
        assert app.is_running, (
            "the app died before the census could read a region; every leak "
            "assertion below would be vacuously green"
        )
        assert graph.schema and screen.graph.schema, (
            "the schema did not survive the store round trip, so the inspector "
            "builds no field rows and this census cannot see them"
        )

        # DERIVED from the ids `refresh_canvas` writes to, so a region this
        # increment starts repainting joins the census by being repainted.
        # By AST, not by splitting on the method name: `_ImportPreviewScreen`
        # has a `refresh_canvas` of its own, and a textual split picks whichever
        # one comes first -- which is how this census first ran against the
        # import preview's single widget and asserted nothing about the map.
        source = (REPO / "mapper" / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        method = next(
            item
            for cls in ast.walk(tree)
            if isinstance(cls, ast.ClassDef) and cls.name == "MapScreen"
            for item in cls.body
            if isinstance(item, ast.FunctionDef) and item.name == "refresh_canvas"
        )
        regions = sorted({
            call.args[0].value.lstrip("#")
            for call in ast.walk(method)
            if isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and call.func.attr == "query_one"
            and call.args and isinstance(call.args[0], ast.Constant)
            and isinstance(call.args[0].value, str)
            and call.args[0].value.startswith("#")
        })
        assert "map-minimap" in regions, regions
        assert len(regions) >= 4, regions

        checked = 0
        for region_id in regions:
            rows = rows_in(screen, screen.query_one(f"#{region_id}").region)
            leaked = sorted({hex(ord(c)) for row in rows for c in row
                             if ord(c) in banned and c not in "\t\n"})
            assert leaked == [], (region_id, leaked)
            checked += 1
        assert checked == len(regions)

        # And the whole composited frame, which is what the operator sees.  THIS
        # HALF FOUND A DEFECT THE OTHER HALF COULD NOT: `refresh_canvas` queries
        # `TabStrip` BY TYPE, so the breadcrumb has no id for the id-derived
        # sweep above to enumerate, and it was painting an uncoerced
        # `ficha.title` into the composited frame -- the same `U+202E` class as
        # the minimap, on a surface neither review named.  A census keyed on how
        # a widget is LOOKED UP inherits that lookup's blind spots; the frame
        # has none.
        frame_leak = sorted({hex(ord(c)) for row in frame_rows(screen) for c in row
                             if ord(c) in banned and c not in "\t\n"})
        assert frame_leak == [], frame_leak
        assert app.is_running, "the app died during the region sweep"


@pytest.mark.asyncio
async def test_the_factory_tree_coerces_the_titles_it_paints(tmp_path):
    """`FactoryScreen` joins the frame sweep — the fifth silent survivor.

    `factory.py:252` coerces the ficha title it paints into the document tree,
    and NOTHING in the suite drove that screen with a hostile title, so a mutant
    deleting the coercion passed all 789 arms.  `d` from the map is one keypress
    away from the same file-derived strings the map paints.

    SCOPED TO `#factory-tree`, AND THE SCOPE IS A FINDING RATHER THAN A
    SHORTCUT.  Measured on this screen with this fixture, the composited FRAME
    leaks `['0x1', '0x200b', '0x202c', '0x202e']` while all four addressable
    regions -- `factory-steps`, `factory-body`, `factory-tree`,
    `factory-preview` -- are clean, so the leak is in the screen's chrome, not
    its tree.  `FactoryScreen`'s preview, tag table and crumb paint file-derived
    text through `rich.markup.escape` ONLY -- markup escaping, not code-point
    coercion -- while the tree in the same file coerces and carries a comment
    explaining why `escape` is wrong.  That is finding `F-C`, it is
    PRE-EXISTING, `mapper/screens/factory.py` is outside this increment's
    declared source set, and it is routed to Inc-REPAIR beside `F-A` and `F-B`.

    So this arm pins the coercion that SHIPS and does not assert the one that
    does not: a frame-level sweep here would be red on the shipped tree and
    would have to be deleted rather than fixed.  Widen it to the frame in the
    increment that closes `F-C`.
    """
    graph = _hostile_graph()
    banned = {cp for lo, hi in darkside.COERCION_RANGES for cp in range(lo, hi + 1)}

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("hostil", graph)
        screen = await open_map(app, pilot, "hostil")
        await pilot.pause()
        assert len(screen.graph.nodes) == 7

        await pilot.press("d")
        await pilot.pause()
        await pilot.pause()
        factory = app.screen
        assert type(factory).__name__ == "FactoryScreen", type(factory).__name__
        assert app.is_running

        rows = rows_in(factory, factory.query_one("#factory-tree").region)
        # NON-VACUITY: the tree must actually have painted a node title, or the
        # sweep below is reading an empty panel.
        assert any(row.strip() for row in rows), "the factory tree painted nothing"
        assert any("raiz" in row or "rama" in row for row in rows), (
            "no ficha title reached the factory tree; the sink is unreached and "
            "this arm cannot see its coercion"
        )
        leaked = sorted({hex(ord(c)) for row in rows for c in row
                         if ord(c) in banned and c not in "\t\n"})
        assert leaked == [], leaked
        # THE F-C RESIDUAL, MEASURED HERE RATHER THAN LEFT TO BE REDISCOVERED.
        # This is not an assertion that the leak is acceptable; it is the
        # increment recording where the boundary of its own claim is.
        frame_leak = sorted({hex(ord(c)) for row in frame_rows(factory) for c in row
                             if ord(c) in banned and c not in "\t\n"})
        assert frame_leak, (
            "the FactoryScreen chrome no longer leaks -- F-C looks closed. "
            "Re-scope this arm to the whole frame and delete this clause."
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key",
    # `año` FIRST, because it is the case the routing argument rests on: an
    # ordinary Spanish field name in a hand-written `.yml` sidecar. The three
    # are parametrised rather than looped -- a loop fails on its first
    # iteration, so the other two were asserted and never driven, and the
    # Spanish-first case is the whole reason `F-A` outranks `SEC-F1`.
    ("a" + chr(0xF1) + "o", "fecha limite", chr(0x01)),
    ids=("ano", "fecha_limite", "c0"),
)
@pytest.mark.xfail(
    strict=True,
    raises=BadIdentifier,
    reason="F-A: SchemaField.key is interpolated into a Textual widget id "
           "(mapper/widgets/inspector.py:137-140), so BadIdentifier is raised "
           "out of FichaInspector._rebuild -- scheduled by call_next from "
           "MapScreen.refresh_canvas, outside every guard -- and the app dies "
           "on map open. Pre-existing at 954f8f3, reproduced there. The fix is "
           "in inspector.py, which is outside this increment's declared source "
           "set, and is routed to Inc-REPAIR beside store.py's "
           "_coerce_text_fields. STRICT so that the increment which fixes it "
           "turns this XPASS -> failure and has to delete this marker, and "
           "`raises` so the marker guarantees it fails for THIS reason rather "
           "than for any reason at all.",
)
async def test_f_a_a_map_whose_schema_keys_are_not_identifiers_still_opens(
    tmp_path, key
):
    """`F-A` — the obligation, landed as a RED ARM so it cannot be lost.

    Textual rejects any widget id outside `[A-Za-z_-][A-Za-z0-9_-]*`.
    `FichaInspector._rows` builds one out of `SchemaField.key`, which is
    file-derived and which `MapStore.load` does not coerce.  Measured, 6 of 6
    keys take `app.is_running` to `False` at context exit, with the operator's
    unsaved edits in the session; the three below are driven here, one app per
    key, and the other three live in the security pass's transcript.

    AND THE KEYS ARE NOT ALL ADVERSARIAL.  `año` and `fecha limite` are ordinary
    Spanish field names -- the happy path for a hand-written `.yml` sidecar in a
    Spanish-first product -- and each kills the app on its own.  That is why this
    is filed as a defect rather than as hardening.  It also SUBSUMES the attack
    `SEC-F1` closed at the renderer: a hostile key can never reach the exported
    SVG, because the session is already gone.

    `raises=BadIdentifier` RATHER THAN A BARE XFAIL.  Without it the marker
    guarantees only that this arm fails, not that it fails for `F-A`'s reason:
    an import error, a renamed fixture or a broken `open_map` would satisfy it
    silently, and Inc-REPAIR would inherit a marker that no longer proves
    anything.  The oracle inside the block stays `app.is_running`, which is the
    operator-visible consequence; `BadIdentifier` is what leaves the context
    manager when the app has already died on it.

    Built from code points at test time, never spelled into this file.
    """
    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title="raiz", meta="m")))
    graph.add_node(Node(id="k0", ficha=Ficha(title="hijo", meta="m")))
    graph.add_edge(Edge(parent_id="root", child_id="k0"))
    graph.schema = [SchemaField(key=key, label="campo")]

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("fa", graph)
        screen = await open_map(app, pilot, "fa")
        await pilot.pause()
        await pilot.pause()
        assert len(screen.graph.nodes) == 2
        assert app.is_running, (
            f"a schema key of {[hex(ord(c)) for c in key]} killed the "
            f"application on map open"
        )


# --------------------------------------------------------------------------
# AT-013 / AT-014 / AT-017


@pytest.mark.asyncio
async def test_at_013_folding_a_leaf_is_refused_out_loud(tmp_path):
    """AT-013 — the ☑ invalid case.  0 pills, 1 notification, canvas unchanged.

    Without this LLR the natural implementation paints a pill reading `+0`,
    which declares a hidden count of zero and is worse than nothing.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("legacy", install(tmp_path, "legacy"))
        screen = await open_map(app, pilot, "legacy")
        # The fixture's leaves, DERIVED from the graph rather than typed.
        leaves = sorted(
            nid for nid in screen.graph.nodes
            if not screen.graph.children_of(nid)
        )
        assert leaves == ["alm", "cont", "nom", "pres"]

        for leaf in leaves:
            screen.nav.cursor = leaf
            screen.refresh_canvas()
            await pilot.pause()
            before = canvas_rows(screen)
            notices_before = len(app._notifications)

            await pilot.press("z")
            await pilot.pause()

            assert screen.folded == frozenset(), leaf
            assert canvas_rows(screen) == before, leaf
            assert pill_counts(canvas_rows(screen)) == [], leaf
            notices = list(app._notifications)
            assert len(notices) == notices_before + 1, leaf
            assert notices[-1].title == "nada que plegar"
            assert notices[-1].message == "este nodo no tiene descendientes"


@pytest.mark.asyncio
async def test_at_014_the_fold_pill_declares_its_hidden_count(tmp_path):
    """AT-014 — the numeral equals the branch's descendant count, per rama.

    Executed counts (M-6): `fin -> 2`, `rrhh -> 1`, `inv -> 1`.  Derived here
    from the graph so the arm cannot pass on a stale transcript, and asserted
    against those three so a derivation that collapsed would still fail.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        app.store.save("legacy", install(tmp_path, "legacy"))
        screen = await open_map(app, pilot, "legacy")

        expected = {
            nid: len(hidden_under(screen.graph, frozenset({nid})))
            for nid in ("fin", "rrhh", "inv")
        }
        assert expected == {"fin": 2, "rrhh": 1, "inv": 1}

        for branch, count in expected.items():
            screen.nav.cursor = branch
            screen.refresh_canvas()
            await pilot.pause()
            await pilot.press("z")
            await pilot.pause()

            rows = canvas_rows(screen)
            assert pill_counts(rows) == [count], (branch, rows)
            title = screen.graph.nodes[branch].ficha.title
            assert any(title[:6] in row for row in rows), (branch, title)

            await pilot.press("z")
            await pilot.pause()
            assert pill_counts(canvas_rows(screen)) == []

        # LLR-N06.3.2 — the painted pills reconcile with the declared total.
        screen.folded = frozenset({"fin", "rrhh", "inv"})
        screen.refresh_canvas()
        await pilot.pause()
        rows = canvas_rows(screen)
        assert sorted(pill_counts(rows)) == [1, 1, 2]
        w, h = screen._canvas_size()
        unpainted = len(screen.graph.nodes) - len(
            painted_ids(screen.graph, screen._view_state(w, h))
        )
        assert sum(pill_counts(rows)) == unpainted == 4


@pytest.mark.asyncio
async def test_at_017_fold_works_while_the_rail_is_auto_hidden(tmp_path):
    """AT-017 — the ☑ error case, and R-013's whole reason for existing.

    Below 118 columns `_apply_region_visibility` auto-hides the rail, so fold
    has to keep working while the widget that USED to own it is not displayed.
    That is the regime the ownership move was made for, stated as a test rather
    than as a rationale.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=RAIL_HIDDEN_SIZE) as pilot:
        await pilot.pause()
        app.store.save("legacy", install(tmp_path, "legacy"))
        screen = await open_map(app, pilot, "legacy")
        rail = screen.query_one("#map-rail", OutlineRail)
        assert screen.rail_hidden and not rail.display, (
            "the rail is displayed at this size; the case under test does not exist"
        )
        assert rows_in(screen, rail.region) == [] or not rail.display

        screen.nav.cursor = "fin"
        screen.refresh_canvas()
        await pilot.pause()
        await pilot.press("z")
        await pilot.pause()

        assert screen.folded == frozenset({"fin"})
        assert pill_counts(canvas_rows(screen)) == [2], (
            "fold stopped working once its old owner was off screen"
        )


# --------------------------------------------------------------------------
# LLR-N07.1.3 / TC-026b — the fold pill's hit tail is the RESOLVED hit set


def _pill_tails(rows: list[str]) -> list[tuple[int, int | None]]:
    """Every painted pill as `(hidden_count, hit_tail_or_None)`.

    `pill_counts` above reads only the `+N` hidden count, and BOTH shipped
    `_PILL` regexes stop there.  That is exactly why this file needed a second
    reader: `TC-026`'s second clause -- "hit count when a query is live" --
    existed only as a row in the traceability matrix and was implemented
    NOWHERE, so the tail was unreachable by the whole suite and its value could
    change for every fixture on a fully green run.
    """
    pattern = re.compile(
        re.escape(FOLD_PILL_TOKEN) + r"\s*(?:.*?)\s*\+(\d+)(?:\s+(\d+))?"
    )
    return [
        (int(m.group(1)), int(m.group(2)) if m.group(2) else None)
        for m in pattern.finditer(" ".join(rows))
    ]


@pytest.mark.asyncio
async def test_tc_026b_the_fold_pill_hit_tail_counts_the_resolved_hits(tmp_path):
    """TC-026b — the pill's tail is `|descendants ∩ hits|`, read from the FRAME.

    THIS IS A DECLARED BEHAVIOUR CHANGE AND NOT A REFACTOR.  `LLR-N07.1.2`
    widens the hit definition by `{id, meta, attachments}`, so the pill's number
    MOVES for existing maps.  Measured on this fixture with the descendant count
    held constant so the tail is isolated: branch `b` goes `+2 1` -> `+2 2` and
    the root goes `+5 2` -> `+5 4`.  The delta is asserted below rather than
    described, so a re-narrowing of the definition reddens here.

    The descendant set is re-derived by the test's OWN walk over `graph.edges`
    and never obtained from the renderer, and the pill is read off the composited
    frame rather than from `MapScreen.folded` -- a model attribute asserts what
    the application believes, and this arm has to fail when the branch paints
    something else.
    """
    from tests.inc4_support import (
        MAP_ID,
        QUERY,
        build_adjuntos,
        descendants_of,
        narrow_hits,
    )
    from tests.test_search import submit

    app = MapperApp(tmp_path)
    async with app.run_test(size=CONTEXT_OF_USE) as pilot:
        await pilot.pause()
        build_adjuntos(tmp_path)
        screen = await open_map(app, pilot, MAP_ID)
        assert screen.query_one("#map-rail").display is True

        graph = screen.graph
        wide = set(graph.search_hits(QUERY))
        narrow = set(narrow_hits(graph, QUERY))

        # WITH NO QUERY LIVE the tail is absent — the counterfactual that proves
        # the value is query-driven and not a constant the pill always paints.
        screen.nav.cursor = "b"
        screen.refresh_canvas()
        await pilot.pause()
        await pilot.press("z")
        await pilot.pause()
        assert screen.folded == frozenset({"b"})
        quiet = _pill_tails(canvas_rows(screen))
        assert quiet == [(2, None)], quiet

        await submit(pilot, QUERY)

        for branch in ("b", "riesgo-root"):
            screen.nav.cursor = branch
            screen.refresh_canvas()
            await pilot.pause()
            if branch not in screen.folded:
                await pilot.press("z")
                await pilot.pause()
            assert branch in screen.folded

            kids = descendants_of(graph, branch)
            expected = len(kids & wide)
            was = len(kids & narrow)
            assert expected > 0, (
                f"{branch} hides no hit; a zero tail cannot demonstrate the count"
            )
            assert expected != was, (
                f"{branch}'s tail does not MOVE under the widening "
                f"({was} -> {expected}); this arm cannot see the change it gates"
            )

            tails = _pill_tails(canvas_rows(screen))
            assert len(tails) == 1, (branch, tails)
            hidden, tail = tails[0]
            assert hidden == len(kids), (branch, hidden, sorted(kids))
            assert tail == expected, (branch, tail, expected, sorted(kids & wide))

            await pilot.press("z")
            await pilot.pause()
            assert branch not in screen.folded


def test_tc_026b_the_tail_reads_the_state_and_could_not_have_computed_it(tmp_path):
    """TC-026b's rename arm — the tail counts ids no predicate would elect.

    `LLR-N07.1.1`'s deletion is satisfied by a rename as far as any absence
    census can tell.  This hands the renderer a hit set containing `f`, which
    BOTH the old and the new definition reject for this query, and asserts the
    pill counts it: a renderer still deciding for itself paints no tail at all.
    """
    from tests.inc4_support import QUERY, build_adjuntos, descendants_of, narrow_hits

    graph = build_adjuntos(tmp_path)
    assert "f" not in graph.search_hits(QUERY)
    assert "f" not in narrow_hits(graph, QUERY)
    assert "f" in descendants_of(graph, "c")

    renderer = LayeredRenderer()
    rows = renderer.render(graph, ViewState(
        selected_id=graph.root_id, w=58, h=26,
        folded=frozenset({"c"}), hits=frozenset({"f"}),
    )).plain.splitlines()
    assert _pill_tails(rows) == [(1, 1)], rows

    # And with the same fold and an EMPTY hit set, no tail.
    rows_quiet = renderer.render(graph, ViewState(
        selected_id=graph.root_id, w=58, h=26,
        folded=frozenset({"c"}),
    )).plain.splitlines()
    assert _pill_tails(rows_quiet) == [(1, None)], rows_quiet
