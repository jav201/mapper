"""LLR-N07.2.2b — every renderer paints `state.hits` distinguishably (`AT-024`).

THE RENDERER SET IS DERIVED, NEVER HAND-LISTED (`C-31`).  A seventh renderer
added later is covered without anyone remembering to add it, and the set is
asserted non-empty BEFORE anything is evaluated -- an empty derived set would
make every arm below pass over nothing.

`Protocol` subclasses are excluded BY THE RULE, not by name (`#D42`).
`state.IRenderer` is the contract the renderers satisfy, not a participant: it
raises on instantiation, so a naive "every class with a `render` method" sweep
CRASHES rather than being wrong -- a failure mode that reads as a defect in the
code under test.  A second Protocol added later is excluded for the same reason.

THE OBSERVABLE IS STYLE SPANS, NOT RENDERED TEXT (`#D42`).  A hit is painted by
STYLE and never by adding characters, so `text_differs` is `False` even on the
renderer that already honoured the hit set.  The parked "the rendered text
differs" threshold would have FALSE-FAILED a correct implementation, which
`C-53` prices exactly as high as passing a wrong one.
"""
from __future__ import annotations

from itertools import combinations

import pytest

from mapper import darkside
from mapper.model import Edge, Ficha, Graph, Node
from mapper.views.state import ViewState

# `importlib`, `subprocess` and `Path` left with the copied derivation they
# served; the module now imports `renderer_classes` instead of re-deriving it.

# The one hit style, spelled here so the arms can name what they expect.  It is
# NOT imported from the renderers: an expected value read out of the artifact
# under verification is a mirror, not a test.
HIT_STYLE = f"{darkside.INK} on {darkside.STEP}"


# ONE derivation, imported -- not a second copy.  The first draft of this module
# copied `tracked` and `renderer_classes` out of the A3 census and justified the
# copy as independence ("this module must keep working if that census is
# re-scoped").  The independent review showed that reason was CANCELLED BY ITS
# OWN GUARD: the module also asserted set equality between the two derivations,
# so on a re-scope this module did not keep working -- the equality arm reddened.
# A copy whose stated purpose is defeated by the check that guards it is just a
# copy (`C-50`), so both it and the now-meaningless equality arm are gone.
from tests.test_a3_census import renderer_classes  # noqa: E402


def _graph():
    """FOUR branches, so a hit can be driven at the first slot and at a later one.

    The lane renderers treat `branches[0]` as the trunk and paint it through a
    DIFFERENT code path than every other branch, so a fixture whose only hit is
    the first branch leaves that second path unexercised -- the `C-10`
    policy-branch rule applied to a renderer's own internal split.  Measured:
    the first draft of this fixture had three nodes with the hit at slot 0, and
    `RailTimelineRenderer`'s per-branch label path never ran.

    The titles are deliberately NON-UNIFORM.  A fixture in which every title
    matched would make a paint-everything renderer indistinguishable from a
    correct one -- the `C-57` fixture-symmetry trap.
    """
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Raiz del mapa", meta="meta")))
    g.add_node(Node(id="first", ficha=Ficha(title="Presupuesto", meta="+1/-0")))
    g.add_node(Node(id="hit", ficha=Ficha(title="analisis de riesgo", meta="+2/-1")))
    g.add_node(Node(id="other", ficha=Ficha(title="Cronograma", meta="+0/-3")))
    for child in ("first", "hit", "other"):
        g.add_edge(Edge("root", child))
    return g


def _spans_at(cls, w, hits, selected=None):
    """The ONE render call site in this module.

    `selected` is a DEFAULTED parameter rather than a second helper, so the A3
    census's arg-ful call-site count does not move when the precedence arms
    below start driving a selection.
    """
    t = cls().render(
        _graph(),
        ViewState(w=w, h=24, hits=frozenset(hits), selected_id=selected),
    )
    return t.plain, [(s.start, s.end, str(s.style)) for s in t.spans]


def _spans(cls, hits):
    """80 columns -- `run_test`'s default, and the batch's narrowest declared
    regime.  Arms that need a node the narrow frame clips use `_spans_at`."""
    return _spans_at(cls, 80, hits)


def test_at024_the_derived_renderer_set_is_non_empty_and_excludes_the_protocol():
    """Guards every arm below: an empty set would make them all vacuous.

    Also pins the exclusion as a PROPERTY rather than a name -- `IRenderer` is
    absent because it is a Protocol, and the arm says so by checking the flag
    rather than the string.
    """
    classes = renderer_classes()
    assert classes, "the derived renderer set is EMPTY; every arm below would be vacuous"
    assert len(classes) >= 6, f"derived only {len(classes)} renderers; a floor of 6 is shipped"
    assert not any(getattr(c, "_is_protocol", False) for c in classes)
    assert "IRenderer" not in {c.__name__ for c in classes}


@pytest.mark.parametrize("cls", renderer_classes(), ids=lambda c: f"{c.__module__.split('.')[-1]}.{c.__name__}")
def test_llr_n07_2_2b_every_renderer_paints_hits(cls):
    """THE SEALED THRESHOLD (`#D42`): the spans move when the hit set is non-empty.

    Executed pre-fix over the derived set, this arm was RED on five of six --
    `layered` was the only compliant renderer.
    """
    _, without = _spans(cls, set())
    _, with_hit = _spans(cls, {"hit"})
    assert with_hit != without, (
        f"{cls.__name__} paints the same spans with and without a hit: "
        "the hit set reaches no style decision in this renderer"
    )


@pytest.mark.parametrize("cls", renderer_classes(), ids=lambda c: f"{c.__module__.split('.')[-1]}.{c.__name__}")
def test_llr_n07_2_2b_a_hit_is_painted_by_style_and_never_by_adding_characters(cls):
    """`#D42`'s own finding, pinned so it cannot regress into the parked wording.

    If a renderer ever starts marking hits by inserting a glyph, the sealed
    threshold above still passes while every width budget in the batch silently
    shifts.  This arm is the reason the threshold is spans and not text.
    """
    text_without, _ = _spans(cls, set())
    text_with, _ = _spans(cls, {"hit"})
    assert text_with == text_without, (
        f"{cls.__name__} changed the RENDERED TEXT for a hit; a hit is painted "
        "by style only"
    )


@pytest.mark.parametrize("cls", renderer_classes(), ids=lambda c: f"{c.__module__.split('.')[-1]}.{c.__name__}")
def test_llr_n07_2_2b_the_paint_is_keyed_on_WHICH_node_is_a_hit(cls):
    """THE DISCRIMINATING NEGATIVE, and the sealed threshold does not have it.

    A renderer that painted EVERY node whenever the hit set is non-empty
    satisfies `#D42`'s threshold in full: its spans do move.  It is also wrong,
    because the Statement says hits are painted "distinguishably from NON-HIT
    nodes".

    Rendering two DIFFERENT single-element hit sets separates the two: a correct
    renderer paints a different picture for each, a paint-everything renderer
    paints the identical picture for both.  Executed against a deliberate
    paint-everything mutant, this arm is the only one of the four that reddens.
    """
    _, hit_first = _spans(cls, {"first"})
    _, hit_other = _spans(cls, {"hit"})
    assert hit_first != hit_other, (
        f"{cls.__name__} paints the same picture whichever node is the hit: "
        "the paint is keyed on the hit set being non-empty, not on membership"
    )


@pytest.mark.parametrize("cls", renderer_classes(), ids=lambda c: f"{c.__module__.split('.')[-1]}.{c.__name__}")
def test_llr_n07_2_2b_a_hit_outside_the_first_branch_is_painted_too(cls):
    """The lane renderers paint `branches[0]` through a different path.

    `LaneRenderer` and `HybridLaneRenderer` iterate every branch uniformly, but
    `RailTimelineRenderer` splits the trunk (`main_style`) from the rest
    (`label_style`), so a hit at slot 0 and a hit at slot 2 exercise DIFFERENT
    code.  Without this arm the second path ships unobserved.

    WIDTH 120, AND THE WIDTH IS MEASURED RATHER THAN ASSUMED.  The first draft
    of this arm drove 80 columns and FAILED on `RailTimelineRenderer` -- not
    because the paint was missing but because at 80 columns that renderer never
    draws the third branch at all: `max_label` clips it to nothing and the title
    is absent from the rendered text.  Measured across widths, slot 2 is painted
    from 100 columns upward and invisible below.  Asserting a style over a node
    the renderer never drew is measuring the clip, not the paint.

    THE PRECONDITION IS ASSERTED BEFORE THE BEHAVIOUR, so this arm fails loudly
    if it ever stops measuring what it claims to: if a later change clips the
    third branch again at 120, the precondition reddens with a message that says
    so, instead of the style assertion failing and reading as a paint defect.
    """
    title = "Cronograma"
    plain, _ = _spans_at(cls, 120, set())
    # AN ASSERT, NOT A SKIP.  This clause read `pytest.skip` in the first draft,
    # while this docstring and the packet both claimed it "reddens with a message
    # that says so".  It did not -- the run stayed green and exit 0, and the
    # pinned ledger carries no skip count, so a silent conversion from assertion
    # to skip would have surfaced NOWHERE.  All six renderers draw the third
    # branch at 120 columns today, so there is no reason to hold a green escape
    # hatch open; if that stops being true this must be a decision, not a skip.
    assert title in plain, (
        f"{cls.__name__} no longer draws the third branch at 120 columns, so "
        "this arm has stopped measuring the paint and is measuring the clip. "
        "See B-55: a clipped hit is an UNDECLARED hit"
    )
    _, without = _spans_at(cls, 120, set())
    _, with_late = _spans_at(cls, 120, {"other"})
    assert with_late != without, (
        f"{cls.__name__} draws the third branch at 120 columns but does not "
        "paint it when it is a hit"
    )


@pytest.mark.parametrize("cls", renderer_classes(), ids=lambda c: f"{c.__module__.split('.')[-1]}.{c.__name__}")
def test_llr_n07_2_2b_a_hit_on_the_FIRST_branch_is_painted_too(cls):
    """The trunk. ADDED BECAUSE A MUTANT SURVIVED, not because it looked missing.

    `RailTimelineRenderer` paints `branches[0]` through `main_style` and every
    other branch through `label_style`.  The first battery fired a mutant that
    stops the TRUNK being painted and it **SURVIVED all 27 arms**: the
    which-node-is-a-hit arm compares hit-on-first against hit-on-other, and
    those two still DIFFER when only the trunk's paint is dead -- one of them
    simply paints nothing.  So a whole shipped code path was unobserved while
    every arm was green.

    This arm pins the trunk directly, against the no-hit render.
    """
    _, without = _spans(cls, set())
    _, trunk_hit = _spans(cls, {"first"})
    assert trunk_hit != without, (
        f"{cls.__name__} does not paint a hit on the FIRST branch"
    )


@pytest.mark.parametrize("cls", renderer_classes(), ids=lambda c: f"{c.__module__.split('.')[-1]}.{c.__name__}")
def test_llr_n07_2_2b_EVERY_member_of_the_hit_set_is_painted(cls):
    """THE PLURAL. Added after an independent review found the gate blind to it.

    The Statement is plural -- "shall paint the NODES carried in `state.hits`"
    -- and every other arm in this file drives a hit set of size 0 or 1.  A
    renderer that paints only ONE member and ignores the rest therefore
    satisfied the entire file: three mutants reducing each renderer's paint to
    the lowest-sorted member of the hit set SURVIVED all 33 arms.

    That is precisely the error class `AT-024` is catalogued against -- a view
    reporting a count it does not paint.  A count line declaring N while the
    canvas paints 1 is that defect exactly, and until this arm existed the gate
    closing `AT-024` could not see it.

    ROUND 3 -- THE AXIS, NOT THE INSTANCE.  The first version of this arm fixed
    the mutant that had been NAMED (paint only the LOWEST-sorted member) and left
    its MIRROR standing: it compared the two-member picture against `{"first"}`
    alone, so a renderer dropping the FIRST member and painting the last was
    still green.  Executed by the confirmation pass, that shape survived on
    SEVEN of seven renderers and across a 199-arm run.  Two rounds in a row this
    increment produced a correct fix to the exact mutant named, so the rule is
    now stated over the whole class instead of over one representative.

    THE ASSERTION IS AN EQUALITY OVER DERIVED SETS, QUANTIFIED OVER EVERY
    SUBSET the fixture can express.  For each subset of size 2 and 3, the
    hit-styled spans of that render must equal the UNION of the hit-styled spans
    of its members' single-member renders.  Dropping any member loses spans;
    painting a non-member gains them; both directions close at every cardinality
    the fixture reaches, not only at the one pair a previous revision named.

    SOUNDNESS PREMISE, and it is a property of this FIXTURE rather than of the
    renderers: span offsets are comparable across renders only because the
    rendered TEXT is invariant under the hit set.  `..._painted_by_style_...`
    pins that, though at a different width.  `layered` DOES append a per-branch
    hit tally to a folded pill's text, so a future fixture with a folded branch
    would break the invariance and silently make this comparison unsound. If
    that arm ever reddens, this one stops meaning what it says.
    """
    def hit_spans(spans):
        return {s for s in spans if s[2] == HIT_STYLE}

    # THE DOMAIN IS DERIVED PER RENDERER, NOT NAMED.  Four rounds of this arm
    # were blocked by one defect migrating outward a quantifier at a time:
    # the assertion's members -> the mutant population's SITES -> the
    # assertion's CARDINALITY -> the DOMAIN it quantifies over.  The previous
    # revision hard-coded ("first", "hit", "other") and justified excluding
    # `root` on the lane family's behalf -- true there, and BLIND for the other
    # three: `outline`, `radial` and `layered` all DRAW the root and DO paint it
    # as a hit (measured: 1, 13 and 20 hit-styled spans), and a renderer that
    # dropped `root` survived all 50 arms AND the whole 904-arm default lane at
    # `outline.py:130`, `radial.py:232` and `layered.py:528`.  The root is
    # operator-reachable -- `SearchIndex.hits("raiz")` returns it.
    #
    # A domain that names its members is the same defect as an assertion that
    # names its inputs, one level down.
    ALL = ("root", "first", "hit", "other")
    singles = {m: hit_spans(_spans_at(cls, 120, {m})[1]) for m in ALL}
    hittable = tuple(m for m in ALL if singles[m])

    # NON-VACUITY, and it is a FLOOR rather than a filter: `hittable` is read
    # off the paint, so without this the domain could shrink to nothing and
    # every union below would pass for free.
    assert len(hittable) >= 3, (
        f"{cls.__name__} paints a hit-styled span for only {hittable}; the "
        "unions below would be vacuous"
    )

    # THE `B-55` BOUNDARY IS ASSERTED, NOT ASSUMED, and it is the load-bearing
    # half: a bare derivation would silently ABSORB the defect, because a
    # renderer that stopped painting root hits would simply drop `root` out of
    # `hittable` and the unions would pass.  A node this renderer DRAWS and the
    # state DECLARES as a hit must be painted.  The three lane renderers iterate
    # branches and never draw the root, so a root hit is declared-but-unpaintable
    # there (`B-55`) -- and that is read off the RENDERED TEXT rather than off a
    # list of class names, so it stays true if a renderer changes family.
    drawn, _ = _spans_at(cls, 120, set())
    assert ("root" in hittable) == ("Raiz del mapa" in drawn), (
        f"{cls.__name__} draws the root ({'Raiz del mapa' in drawn}) but paints "
        f"a root hit ({'root' in hittable}); a DRAWN node that is a declared hit "
        "must be painted -- see B-55"
    )

    _, none = _spans_at(cls, 120, set())
    for k in range(2, len(hittable) + 1):
        for combo in combinations(hittable, k):
            _, painted = _spans_at(cls, 120, set(combo))
            assert painted != none, f"{cls.__name__} paints nothing for {combo}"
            expected = set().union(*(singles[m] for m in combo))
            dropped = sorted(m for m in combo if not (singles[m] <= hit_spans(painted)))
            assert hit_spans(painted) == expected, (
                f"{cls.__name__} hits={combo}: the painting is not the union of "
                f"the single-member paintings; dropped={dropped}"
            )


@pytest.mark.parametrize("cls", renderer_classes(), ids=lambda c: f"{c.__module__.split('.')[-1]}.{c.__name__}")
@pytest.mark.parametrize("node", ["first", "hit"], ids=["trunk", "branch"])
def test_llr_n07_2_2b_selection_is_painted_ON_TOP_of_a_hit(cls, node):
    """The precedence, which NO arm in the repository observed before this one.

    Every arm here and in every other test file left `selected_id` at `None`,
    so five newly-authored branch orderings shipped unobserved -- two mutants
    inverting the precedence survived a 185-arm run across twelve test files.

    The rule is the one `layered` already uses (`layered.py:628`, "selection
    highlight on top"): a selected node keeps its selection styling whether or
    not it is also a hit.  Losing your place is worse than losing one highlight.

    BOTH SLOTS, and the second one exists because the first version of this arm
    only ever selected `branches[1]`.  `RailTimelineRenderer` routes
    `branches[0]` through `main_style`, a separate statement this increment
    rewrote, so its inversion survived all 44 arms while the other five died.
    That is this file's OWN trunk-versus-branch lesson recurring inside the arm
    written to close the previous finding -- which is why the slot is now a
    parameter rather than a fixed id.
    """
    _, sel_only = _spans_at(cls, 120, set(), selected=node)
    _, sel_and_hit = _spans_at(cls, 120, {node}, selected=node)
    assert sel_and_hit == sel_only, (
        f"{cls.__name__} lets the hit style win over the selection on the "
        f"selected node ({node}); selection is painted ON TOP of a hit"
    )


def test_llr_n07_2_2b_every_renderer_uses_THE_SAME_hit_style():
    """The six call sites spell the style inline; this is what stops them drifting.

    `C-50` says a copy means one of them is false and nobody knows which. The
    remedy chosen here is NOT a shared constant -- `layered` already spelled this
    style inline before the increment, and `darkside` spells it inline too, so a
    new constant would have created a SECOND home rather than one.  Instead the
    equality is made OBSERVABLE: whatever style a hit introduces, every renderer
    must introduce the same one, derived from rendering rather than read out of
    the source.

    Guarded in both directions -- the introduced set must be exactly one style,
    and that style must be the one named here.
    """
    introduced = {}
    for cls in renderer_classes():
        _, without = _spans(cls, set())
        _, with_hit = _spans(cls, {"hit"})
        new_styles = {st for _, _, st in with_hit} - {st for _, _, st in without}
        introduced[cls.__name__] = new_styles

    assert all(introduced.values()), (
        f"a renderer introduced NO new style for a hit: {introduced}"
    )
    every = set().union(*introduced.values())
    assert every == {HIT_STYLE}, (
        f"the renderers do not agree on one hit style: {introduced}"
    )
