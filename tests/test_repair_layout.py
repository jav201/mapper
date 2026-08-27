"""Increment 4 — S-07 (three-region layout) and S-08 (complete legend).

`HLR-R04` / `LLR-R04.1` · `HLR-R05` / `LLR-R05.1`, `LLR-R05.2`.

Two oracle decisions are load-bearing here and both were settled by MEASUREMENT,
not by argument.  They are written down because each of the three obvious oracles
is wrong in a different direction, and the wrongness is invisible from reading:

  * `Screen.render_line(y)` renders the SCREEN's own line, never the composited
    frame.  Measured pre-fix: it reported all 27 labels absent, i.e. it
    FALSE-FAILS a correct implementation.  Unusable.
  * the CONTENT widget's own `render_lines` is region-clipped by construction and
    is nonetheless VACUOUS here: measured 0 missing at every size, pre-fix.  The
    `Static` really does render all 27 rows; the defect is that `max-height`
    clips them away with no way to scroll.  An oracle that reads the widget's own
    paint cannot see a reachability defect (C-40 limb 1 — the declared subject is
    not in the predicate's expression).
  * the composited frame clipped to the DIALOG's region is the correct oracle:
    measured 11 missing pre-fix, the whole `view` group.

An UNCLIPPED composited read measures 10, not 11, because `MapScreen`'s keybar
shows through `background: #000000 70%` and donates the word `cobertura`.  It
would therefore pass a fix that still hid a binding.  `AT-R14` is the guard that
keeps the clip honest, and it compares WHOLE ROWS rather than substrings —
`cobertura 100%` is painted outside the dialog while `cobertura` is a legitimate
binding label, so a substring comparison collides.
"""
from __future__ import annotations

import pytest

from mapper.app import MapperApp, MapScreen
from mapper.keymap import SCOPE_HOME, SCOPE_MAP, bindings_for
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.screens.help import HelpScreen
from mapper.widgets.inspector import INSPECTOR_WIDTH
from mapper.widgets.rail import RAIL_WIDTH

SCHEMA = [SchemaField(key="D", label="documento", required=True)]

# Wide enough that `_apply_region_visibility` keeps all three regions, and one
# size that is NOT — the discriminating negative.  Derived from the rule the
# screen states (`available = w - RAIL_WIDTH - INSPECTOR_WIDTH >= MIN_CANVAS_WIDTH`)
# rather than hand-picked, so a change to the rule reddens the arithmetic below.
WIDE_SIZES = [(140, 45), (120, 40)]
NARROW_SIZE = (100, 24)


def _tree(app, map_id="layout"):
    g = Graph()
    g.schema = list(SCHEMA)
    g.add_node(Node(id="root", ficha=Ficha(title="erp", fields={"D": "a"})))
    g.add_node(Node(id="fin", ficha=Ficha(title="finanzas", fields={"D": "a"})))
    g.add_edge(Edge("root", "fin"))
    app.store.save(map_id, g)
    return map_id


async def _open_map(app, pilot, map_id):
    app.push_screen(MapScreen(map_id))
    await pilot.pause()
    await pilot.pause()
    return app.screen


def _frame_rows(screen) -> list[str]:
    """Every row of the COMPOSITED frame — what the operator actually sees."""
    return [
        "".join(seg.text for seg in strip)
        for strip in screen._compositor.render_strips()  # noqa: SLF001
    ]


def _rows_in(screen, region) -> list[str]:
    """The composited frame clipped to one widget's region.

    This is the painted-result oracle.  It is deliberately NOT the widget's own
    `render_lines`: see the module docstring for why that is vacuous here.
    """
    rows = _frame_rows(screen)
    band = rows[region.y : region.y + region.height]
    return [r[region.x : region.x + region.width] for r in band]


def _rows_outside(screen, region) -> list[str]:
    """Non-blank painted rows that lie OUTSIDE the region, derived at runtime.

    `AT-R14`'s input set.  Derived, never hand-listed (C-31): a sentinel chosen by
    hand ('finanzas') was measured to sit UNDER the dialog, absent from both the
    clipped and unclipped reads, and therefore discriminating nothing.
    """
    out: list[str] = []
    for y, row in enumerate(_frame_rows(screen)):
        if region.y <= y < region.y + region.height:
            left, right = row[: region.x], row[region.x + region.width :]
            for part in (left, right):
                if part.strip():
                    out.append(part.rstrip())
        elif row.strip():
            out.append(row.rstrip())
    return out


async def _painted_bindings(app, pilot) -> str:
    """Union of the help dialog's painted rows across EVERY scroll position.

    Scrolling is part of the assertion, not a workaround for it: `LLR-R05.1`
    promises content taller than the viewport is REACHABLE, and the only way to
    observe reachability through the shipped surface is to reach it.
    """
    dialog = app.screen.query_one("#help-dialog")
    pane = app.screen.query_one("#help-bindings")
    seen: set[str] = set()
    for _ in range(60):
        seen.update(_rows_in(app.screen, dialog.region))
        if pane.scroll_offset.y >= pane.max_scroll_y:
            break
        pane.scroll_to(y=pane.scroll_offset.y + max(1, pane.region.height - 1), animate=False)
        await pilot.pause()
        await pilot.pause()
    else:  # pragma: no cover - a scroll that never terminates is a defect
        pytest.fail("the bindings pane never reached the bottom of its scroll range")
    return "\n".join(sorted(seen))


# ---------------------------------------------------------------------------
# S-07 — HLR-R04, the three-region layout


def test_tc_r22_the_rail_css_width_equals_the_rail_width_constant():
    """LLR-R04.1 — the declared width and the constant must AGREE, and be able to disagree.

    The CSS carries a LITERAL, not an f-string interpolation of `RAIL_WIDTH`.
    That is deliberate: interpolating would make the two incapable of
    disagreeing, and this test would certify an identity instead of a
    commitment.  A predicate whose subject cannot move is not a gate (C-40).

    RED arms: change the CSS literal; change `RAIL_WIDTH`; delete the rule.

    **Reads `MapperApp.CSS`, not `MapScreen.CSS`** — amendment `A-10`.  The
    requirement names `MapScreen.CSS` as the touched symbol; `MapScreen` has no
    `CSS` attribute at all, and the sibling `#map-canvas` and `#map-inspector`
    rules live on the app.  A second stylesheet for one rule would fork the
    convention, so the rule joins its siblings and the SPEC's premise is
    corrected rather than the code bent to fit it.  This node found that by
    failing on its first run against the real tree — which is the argument for
    executing a premise instead of reading it (C-43).
    """
    import re

    # `hasattr(MapScreen, "CSS")` is TRUE and means nothing: Textual's `Screen`
    # base defines `CSS = ""`, so the name resolves to an inherited empty string.
    # That is C-15's inherited-attribute trap exactly, and it cost one run to
    # find.  The real question is whether MapScreen declares one of its OWN.
    #
    # All THREE styling entry points are checked, not just `CSS` (review finding
    # F4): Textual resolves a screen's styling from `CSS`, `DEFAULT_CSS` and
    # `CSS_PATH`, so a `#map-rail` rule arriving by either of the other two would
    # leave this guard and the `MapperApp.CSS` read below both silent.
    for attr in ("CSS", "DEFAULT_CSS", "CSS_PATH"):
        assert attr not in MapScreen.__dict__, (
            f"MapScreen has acquired its own {attr}; A-10's premise correction "
            "needs re-reading, and this rule may belong there after all"
        )
    rule = re.search(r"#map-rail\s*\{([^}]*)\}", MapperApp.CSS)
    assert rule, "MapperApp.CSS declares no #map-rail rule — S-07's actual cause"
    declared = re.search(r"\bwidth\s*:\s*(\d+)\s*;", rule.group(1))
    assert declared, f"#map-rail declares no fixed width: {rule.group(1)!r}"
    assert int(declared.group(1)) == RAIL_WIDTH, (
        f"CSS says width {declared.group(1)}, rail.RAIL_WIDTH is {RAIL_WIDTH}; "
        "a later change to one silently re-opens S-07"
    )


@pytest.mark.parametrize("size", WIDE_SIZES)
async def test_at_r10_the_three_regions_are_disjoint_and_on_screen(tmp_path, size):
    """AT-R10 — every region inside the terminal, the three ranges disjoint.

    Pre-fix this is RED for the reason S-07 names: `#map-rail` carried no width
    rule at all, so it took the whole terminal (measured: x=0 w=140 at 140x45)
    and pushed the canvas to width 1 and the inspector entirely off-screen
    (x=141..177).
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        screen = await _open_map(app, pilot, _tree(app))
        assert not screen.rail_hidden, "this size must keep the rail; otherwise S-07 cannot manifest"

        spans = {}
        for wid in ("#map-rail", "#map-canvas", "#map-inspector"):
            r = screen.query_one(wid).region
            spans[wid] = (r.x, r.x + r.width)
            assert r.x >= 0 and r.x + r.width <= size[0], (
                f"{wid} spans {r.x}..{r.x + r.width} outside a {size[0]}-column terminal"
            )

        ordered = sorted(spans.items(), key=lambda kv: kv[1][0])
        for (a_id, (_, a_end)), (b_id, (b_start, _)) in zip(ordered, ordered[1:]):
            assert a_end <= b_start, f"{a_id} and {b_id} overlap: {a_end} > {b_start}"

        rail = screen.query_one("#map-rail").region
        assert rail.width == RAIL_WIDTH
        canvas = screen.query_one("#map-canvas").region
        assert canvas.width == size[0] - screen._chrome_width(), (
            "the canvas must take exactly what the rail and inspector leave"
        )


async def test_at_r10b_a_terminal_too_narrow_collapses_the_rail_and_still_fits(tmp_path):
    """AT-R10's discriminating negative — the layout holds where the rail is ABSENT.

    At 100x24 `_apply_region_visibility` hides the rail on its own, so the three
    ranges already fit on the shipped tree and this test is GREEN pre-fix.  It is
    here so `AT-R10`'s RED is attributable to the rail's WIDTH and not merely to
    'some layout assertion fails somewhere' — the requirement is scoped 'when the
    rail is displayed', and this is the other half of that condition.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=NARROW_SIZE) as pilot:
        screen = await _open_map(app, pilot, _tree(app))
        assert screen.rail_hidden, (
            f"{NARROW_SIZE[0]} columns leaves "
            f"{NARROW_SIZE[0] - RAIL_WIDTH - INSPECTOR_WIDTH} for the canvas, under "
            f"MIN_CANVAS_WIDTH={MapScreen.MIN_CANVAS_WIDTH}; the rail must auto-collapse"
        )
        canvas = screen.query_one("#map-canvas").region
        inspector = screen.query_one("#map-inspector").region
        assert canvas.x == 0
        assert canvas.x + canvas.width == inspector.x
        assert inspector.x + inspector.width <= NARROW_SIZE[0]


async def test_at_r11_the_canvas_paints_map_content_in_its_own_region(tmp_path):
    """AT-R11 — the canvas is not merely SIZED correctly, it PAINTS the map.

    A fix that gave the canvas the right region while it rendered nothing would
    pass `AT-R10` completely.  The oracle is clipped to the canvas's own region,
    so the rail's copy of the same titles cannot satisfy it.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        screen = await _open_map(app, pilot, _tree(app))
        canvas = screen.query_one("#map-canvas")
        painted = "\n".join(_rows_in(screen, canvas.region))
        assert "erp" in painted, f"the canvas region paints no node text:\n{painted}"


# ---------------------------------------------------------------------------
# S-08 — HLR-R05, the complete legend


async def test_tc_r24_the_bindings_region_is_scrollable(tmp_path):
    """LLR-R05.1 — content taller than the viewport must be REACHABLE.

    Asserted as `max_scroll_y > 0` together with the virtual height genuinely
    exceeding the viewport, so a pane that is 'scrollable' over content that
    fits cannot satisfy it vacuously.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        await _open_map(app, pilot, _tree(app))
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        pane = app.screen.query_one("#help-bindings")
        assert pane.virtual_size.height > pane.region.height, (
            "the fixture no longer produces more bindings than fit; this node "
            "would pass without testing anything"
        )
        assert pane.max_scroll_y > 0, "the bindings region cannot be scrolled"


@pytest.mark.parametrize("size", [*WIDE_SIZES, NARROW_SIZE])
async def test_at_r12_pressing_help_presents_every_map_binding(tmp_path, size):
    """AT-R12 — press the real `?`; every binding of the active scope is reachable.

    Measured pre-fix at 140x45: 11 of 27 absent, the entire `view` group, because
    `#help-dialog`'s `max-height: 28` clipped a 40-row body with no way to scroll.

    The expected set is DERIVED from `keymap`, never hand-listed (C-31 / LLR-R05.2):
    a set written by hand is only as strong as its author's memory, and the next
    binding added would not appear in it.

    **Membership here is SUBSTRING, not row-exact, and glyphs are not checked**
    (review finding `F3`).  Two `SCOPE_MAP` labels are proper substrings of
    others — `siguiente` inside `siguiente faltante`, and `hijo` inside
    `agregar hijo` — so dropping either of those two bindings alone would not
    redden this node.  That is deliberate division of labour, not an oversight:
    `TC-R25` owns exact `(glyph, label)` set equality at the white-box layer,
    where the parse is precise, and arm `L7` confirms it discriminates.  Losing a
    whole group still reddens here on the other labels.  Do not read this node as
    per-label precision.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await _open_map(app, pilot, _tree(app))
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)
        assert app.screen.scope == SCOPE_MAP, (
            f"help opened on scope {app.screen.scope!r}; the legend would be complete "
            "for the wrong screen"
        )

        expected = bindings_for(SCOPE_MAP)
        assert len(expected) >= 20, "the keymap shrank; this node's premise no longer holds"
        painted = await _painted_bindings(app, pilot)
        missing = sorted(f"{b.group}/{b.glyph} {b.label}" for b in expected if b.label not in painted)
        assert not missing, f"{len(missing)} of {len(expected)} bindings never painted: {missing}"


async def test_at_r13_the_same_holds_for_the_home_scope(tmp_path):
    """AT-R13 — the promise is not satisfied at one screen's boundary.

    Also guards a real hazard: three screens push `HelpScreen()` with NO scope,
    which would resolve to `SCOPE_APP` and show two bindings instead of the
    screen's own.  Those paths are shadowed today by the app-level priority
    binding for `?`; if that ever changes, this reddens.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        _tree(app)
        await pilot.pause()
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)
        assert app.screen.scope == SCOPE_HOME, (
            f"help on the sala opened scope {app.screen.scope!r}, not {SCOPE_HOME!r}"
        )

        expected = bindings_for(SCOPE_HOME)
        painted = await _painted_bindings(app, pilot)
        missing = sorted(b.label for b in expected if b.label not in painted)
        assert not missing, f"{len(missing)} of {len(expected)} home bindings never painted: {missing}"


async def test_at_r14_the_oracle_is_clipped_to_the_help_dialog(tmp_path):
    """AT-R14 — the oracle's OWN guard, and the only reason to trust AT-R12.

    `HelpScreen` is a `ModalScreen` with `background: #000000 70%`, so an
    unclipped read of the frame composites `MapScreen` through the backdrop.
    Measured pre-fix: unclipped reports 10 missing where clipped reports 11 —
    the difference is the single word `cobertura`, donated by the keybar.  An
    unclipped oracle therefore PASSES a fix that still hides a binding.

    FOUR limbs, each failing a different way.  (a) and (d) are C-55's rider;
    (b) and (c) were added by review finding `F1`, which measured that the two
    limbs originally written here left the clip's more important dimension
    entirely unguarded:

      (a) rows outside the region must EXIST — otherwise the probe cannot
          produce a non-absence and every other limb is vacuous;
      (b) the read is clipped in **y** — exactly `region.height` rows;
      (c) the read is clipped in **x** — every row exactly `region.width` wide.
          THIS is the conjunct that matters.  Dropping the column clip while
          keeping the row clip makes `AT-R12` report 10 missing instead of 11,
          because `cobertura` sits at y=11 — INSIDE the dialog's row band — and
          escapes only via the column slice.  Such an oracle passes a fix that
          still hides a binding;
      (d) no row painted outside the region may appear in the clipped read.

    Whole rows, never substrings: `cobertura 100%` is painted outside the dialog
    while `cobertura` is a legitimate binding label, so a substring test collides.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        await _open_map(app, pilot, _tree(app))
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        dialog = app.screen.query_one("#help-dialog")

        outside = _rows_outside(app.screen, dialog.region)
        assert outside, (
            "no text is painted outside the help dialog, so this test cannot "
            "distinguish a clipped oracle from an unclipped one"
        )

        inside_raw = _rows_in(app.screen, dialog.region)

        # (b) and (c): the clip is TWO-dimensional and the conjuncts fail
        # differently, so each carries its own assertion and its own battery arm.
        assert len(inside_raw) == dialog.region.height, (
            f"the oracle read {len(inside_raw)} rows for a {dialog.region.height}-row "
            "dialog; it is not clipped in y"
        )
        assert all(len(r) == dialog.region.width for r in inside_raw), (
            "the oracle returned rows wider than the dialog; it is not clipped in x, "
            "and MapScreen's keybar is being counted as a legend row"
        )

        # (d).  `rstrip` BOTH sides: `_rows_outside` rstrips its fragments while
        # `_rows_in` returns width-padded slices, so a raw intersection is empty
        # by PADDING rather than by clipping — measured at 0 of 28 rows even
        # eligible to match, which made this limb vacuous as first written.
        inside = {r.rstrip() for r in inside_raw if r.strip()}
        leaked = sorted(set(outside) & inside)
        assert not leaked, f"the oracle read {len(leaked)} rows from outside the dialog: {leaked}"


async def test_tc_r23_the_declared_rail_width_is_the_width_actually_painted(tmp_path):
    """LLR-R04.1's other half — a declaration that never takes effect is not a fix.

    `TC-R22` reads the stylesheet; this reads the laid-out widget.  They fail
    independently: a rule written into the wrong selector satisfies TC-R22 and
    reddens here, and a `RAIL_WIDTH` change with the CSS left alone reddens
    TC-R22 while this one still agrees with the stylesheet.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(140, 45)) as pilot:
        screen = await _open_map(app, pilot, _tree(app))
        assert not screen.rail_hidden
        assert screen.query_one("#map-rail").region.width == RAIL_WIDTH


def _rendered_pairs(scope: str) -> set[tuple[str, str]]:
    """(glyph, label) pairs the panel's own body renders, parsed from its Text.

    Read from the rendered content rather than from painted pixels ON PURPOSE:
    this is the white-box layer, and it is the layer that can assert SET EQUALITY
    in both directions.  Painted-pixel equality cannot: `volver` and `cerrar`
    each name three different bindings in different scopes, so a foreign row is
    not always distinguishable from a wanted one once it is text on a screen.
    The black-box layer (`AT-R12`) owns reachability; this layer owns the set.
    """
    screen = HelpScreen(scope)
    pairs: set[tuple[str, str]] = set()
    for line in screen._render_keymap().plain.splitlines():  # noqa: SLF001
        if not line.startswith("  "):
            continue
        body = line[2:]
        glyph, _, label = body.partition(" ")
        if glyph and label.strip():
            pairs.add((glyph.strip(), label.strip()))
    return pairs


@pytest.mark.parametrize("scope", [SCOPE_MAP, SCOPE_HOME])
def test_tc_r25_the_presented_set_equals_the_keymap_set_in_both_directions(scope):
    """LLR-R05.2 — SET EQUALITY, derived from `keymap`, never hand-listed.

    `AT-R12` asserts nothing is MISSING.  That direction alone is satisfied by a
    panel that dumps all 48 bindings of every scope, which is a different defect
    with the same green.  This asserts the other direction too.

    The expected side is built from `bindings_for(scope)`; dropping a member from
    the keymap reddens it, and so does presenting one binding too many.
    """
    expected = {(b.glyph, b.label) for b in bindings_for(scope)}
    assert expected, f"bindings_for({scope!r}) is empty; the comparison would be vacuous"
    assert _rendered_pairs(scope) == expected


def test_tc_r26_no_foreign_scope_binding_reaches_the_panel():
    """LLR-R05.2's discriminating negative, stated as a positive control.

    `TC-R25` would also pass if `bindings_for` and the panel were BOTH wrong in
    the same direction — they share `bindings_for` as their source.  This one
    reaches past that shared source to the full `KEYMAP` and names the members
    that must NOT appear, so a panel that ignored the scope entirely reddens here
    even though it might satisfy a comparison built from the same call.
    """
    from mapper.keymap import KEYMAP

    wanted = {(b.glyph, b.label) for b in bindings_for(SCOPE_MAP)}
    foreign = {(b.glyph, b.label) for b in KEYMAP} - wanted
    assert foreign, "every binding belongs to the map scope; this node cannot fail"
    intruders = sorted(_rendered_pairs(SCOPE_MAP) & foreign)
    assert not intruders, f"the map legend presents bindings from other scopes: {intruders}"


@pytest.mark.parametrize(
    "size,expected,governed_by",
    [((140, 45), 28, "max-height"), ((100, 24), 21, "height: 90%")],
    ids=["cap-governs", "percentage-governs"],
)
async def test_tc_r36_the_dialog_height_is_governed_by_a_named_declaration(
    tmp_path, size, expected, governed_by
):
    """Which of the dialog's two height declarations governs, at each size.

    Written in response to review finding `F2`, and written this way on purpose.
    The battery arm `L5` — raise `max-height` until today's 27 bindings fit —
    produced **0 RED**, and the increment packet retired it as a "no-op
    mutation" on the claim that `height: 90%` binds first.  **That claim was
    false**: measured, `L5` grows the dialog from 28 rows to 40 at 140x45 and
    collapses the scrollable surplus from 14 rows to 2.  `max-height` governs
    there; the percentage governs only on a short terminal.

    So `L5` was a genuinely INERT arm, and C-40 is explicit that the answer to an
    inert arm is to rewrite the predicate rather than re-argue it.  This is that
    predicate.  It also discharges the ambiguity Risk 2 names — two declarations
    sharing one responsibility, with nothing asserting which one is in charge.

    Nothing here duplicates `TC-R24`: that node asserts the pane can be
    scrolled, which stays true under `L5`.  This asserts the dialog's SIZE, which
    does not.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=size) as pilot:
        await _open_map(app, pilot, _tree(app))
        await pilot.press("question_mark")
        await pilot.pause()
        await pilot.pause()
        dialog = app.screen.query_one("#help-dialog")
        assert dialog.region.height == expected, (
            f"at {size[0]}x{size[1]} the dialog is {dialog.region.height} rows, "
            f"expected {expected} governed by {governed_by}"
        )
