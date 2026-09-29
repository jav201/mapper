"""Inc-8 design pass -- the legend and the view agree, mechanically (verdict D2).

`INC8-F2` / `UX-F3`: the legend proved it paints each member in its DECLARED
style, and the declaration proved it equals `01b` -- but nothing compared either
with what the VIEW paints, and six declared rows turned out to describe forms no
renderer draws.  These arms render every view over real fixtures and read the
composited frame, in both directions:

  SOUNDNESS     every member a view's legend explains is painted by that view,
                in the member's declared style;
  COMPLETENESS  every meaningful glyph the view paints belongs to some member
                of that view's vocabulary.

THE EXCLUSION RULE is written once, in `meaningful` and `_excluded_widget`,
and it is the same rule the catalogue instrument in `increment-022` applied:

  X1  text          letters, digits and spaces (`L*`, `N*`, `Z*`)
  X2  punctuation   Unicode `P*`, and every ASCII symbol
  X3  app chrome    the tab strip, the hint line, the key bar and the sala's
                    identity row -- the same on every screen, and not the view
  X4  key glyphs    a character the seat uses as a key's glyph (`↵`, `↑`): the
                    legend's key section explains those
  X5  table header  a `DataTable`'s column-header row

THE RULE'S KNOWN BLIND SPOTS, stated so nobody reads more into a green run:
completeness is asserted per CHARACTER, not per style -- a declared glyph
painted in an undeclared tone is caught only if that tone is a member
(soundness), not by this arm; and X2 hides `·` (`V21b`, a punctuation code
point that the rail's lattice uses as a mark), which soundness still checks.
The diff mode (`=`) is not driven -- it needs a git history -- so its tones are
not seen by either direction (carried in `increment-022`).
"""
from __future__ import annotations

import string
import unicodedata
from datetime import date

import pytest
from rich.style import Style
from textual.widgets import DataTable

from mapper import darkside, keymap
from mapper.app import HomeScreen, MapperApp, MapScreen
from mapper.model import Edge, Ficha, Graph, Node, SchemaField
from mapper.screens.help import vocabulary_for

VIEW_SIZE = (118, 34)

# ---------------------------------------------------------------------------
# The exclusion rule -- ONE statement of it.

CHROME_WIDGETS = frozenset({"TabStrip", "HintLine", "KeyBar", "home-identity"})
KEY_GLYPHS = frozenset(
    ch for b in keymap.KEYMAP for ch in b.glyph if not (ch.isalnum() or ch.isspace())
)


def meaningful(ch: str) -> bool:
    """X1, X2 and X4: may this painted character carry a meaning of its own?"""
    if ord(ch) < 0x80 or unicodedata.category(ch)[0] in "LNZP":
        return False
    return ch not in KEY_GLYPHS


def _excluded_widget(widget, y: int) -> bool:
    """X3 and X5, decided by the widget painted under the cell."""
    node = widget
    while node is not None:
        if type(node).__name__ in CHROME_WIDGETS or node.id in CHROME_WIDGETS:
            return True
        if isinstance(node, DataTable) and node.show_header and y == node.region.y:
            return True
        node = node.parent
    return False


def glyph_set(vid: str, sample: str) -> frozenset[str]:
    """The painted characters a member stands for: the meaningful characters of
    its sample, plus every code point of its declared ranges.  A sample with
    none stands for its own characters -- `V21b`'s `·` is a punctuation code
    point the rail uses as a mark -- and a sample that is only a numeral
    (`V35`'s rail count) stands for any numeral."""
    chars = {c for c in sample if meaningful(c)}
    for lo, hi in darkside.DECLARED_GLYPH_RANGES.get(vid, ()):
        chars |= {chr(cp) for cp in range(lo, hi + 1)}
    if not chars:
        stripped = sample.strip()
        chars = set(string.digits) if stripped.isdigit() else set(stripped) - {" "}
    return frozenset(chars)


def _hex(color) -> str | None:
    return None if color is None else color.get_truecolor().hex


def _paints_as(style: Style | None, declared: str) -> bool:
    """Same comparison the legend-side arm uses: fg, bold, and bg if declared."""
    want = Style.parse(darkside.resolve_style(declared))
    style = style or Style()
    if _hex(style.color) != _hex(want.color) or bool(style.bold) != bool(want.bold):
        return False
    return want.bgcolor is None or _hex(style.bgcolor) == _hex(want.bgcolor)


def harvest(screen) -> set[tuple[str, Style | None]]:
    """(character, style) of every non-space cell of the composited frame that
    the exclusion rule's X3/X5 leave to the view."""
    out: set[tuple[str, Style | None]] = set()
    for y, strip in enumerate(screen._compositor.render_strips()):  # noqa: SLF001
        x = 0
        for seg in strip:
            for ch in seg.text:
                if not ch.isspace():
                    widget, _ = screen.get_widget_at(x, y)
                    if not _excluded_widget(widget, y):
                        out.add((ch, seg.style))
                x += 1
    return out


# ---------------------------------------------------------------------------
# Fixtures: the maps the catalogue instrument drove.

SCHEMA = [SchemaField(key="D", label="documento", required=True),
          SchemaField(key="O", label="dueno", required=True)]
BRANCHES = ["finanzas", "rrhh", "inventarios", "ventas", "compras", "logistica",
            "juridico", "ti"]


def legacy_map() -> Graph:
    """8 branches x 5 leaves.  Every third branch is complete, the others
    carry fewer actas, one leaf is due today -- so the card chips, the schema
    letters, the rail counts and every coverage glyph are all exercised."""
    g = Graph()
    g.schema = list(SCHEMA)
    g.add_node(Node(id="root", ficha=Ficha(title="erp legacy", fields={"D": "ACTA-1", "O": "ana"})))
    for bi, b in enumerate(BRANCHES):
        g.add_node(Node(id=b, ficha=Ficha(title=b, fields={"D": "a", "O": "x"})))
        g.add_edge(Edge("root", b))
        for i in range(5):
            fields = {"D": f"A-{i}", "O": "x"} if (bi % 3 == 0 or i < bi % 3) else {}
            if bi == 1 and i == 0:
                fields["due"] = date.today().isoformat()
            g.add_node(Node(id=f"{b}{i}", ficha=Ficha(title=f"{b[:4]} {i}", fields=fields)))
            g.add_edge(Edge(b, f"{b}{i}"))
    return g


def concept_map() -> Graph:
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="plataforma", meta="core")))
    for b in BRANCHES[:6]:
        g.add_node(Node(id=b, ficha=Ficha(title=b, meta="area")))
        g.add_edge(Edge("root", b))
        for i in range(3):
            g.add_node(Node(id=f"{b}{i}", ficha=Ficha(title=f"{b[:4]} {i}", meta="mod")))
            g.add_edge(Edge(b, f"{b}{i}"))
    return g


CYCLE_MMD = "graph TD\n    a[A] --> b[B]\n    b --> a\n"

# (fixture, keys) per state; each state runs in a FRESH app so none leaks into
# the next.  The keys walk, fold (the lattice and the rail's `▸` show only when
# the rail is short or a folded branch is not selected), search, and move the
# focus to the rail (the unfocused selection).
MAP_STATES = {
    "atlas": ((), [(legacy_map, ()), (legacy_map, ("l", "z", "j")),
                   (legacy_map, ("slash", "f", "i", "n", "enter")),
                   (legacy_map, ("l", "g")), (legacy_map, ("z",)), (concept_map, ())]),
    "esquema": (("o",), [(legacy_map, ()), (legacy_map, ("l", "z", "j")),
                         (legacy_map, ("z",)), (concept_map, ())]),
    "mapa mental": (("r",), [(legacy_map, ()), (legacy_map, ("l", "j", "l")),
                             (legacy_map, ("l", "z", "j")), (legacy_map, ("z",)),
                             (concept_map, ())]),
}


async def _settle(pilot, n: int = 3) -> None:
    # A pushed screen fades in; a frame read mid-fade carries interpolated
    # tones the product never declares (the catalogue measured `#b8b8b8`).
    await pilot.wait_for_scheduled_animations()
    for _ in range(n):
        await pilot.pause()


async def _map_harvest(tmp_path, view: str) -> set:
    view_keys, states = MAP_STATES[view]
    painted: set = set()
    for i, (factory, keys) in enumerate(states):
        app = MapperApp(tmp_path / f"s{i}")
        async with app.run_test(size=VIEW_SIZE) as pilot:
            app.store.save("mapa", factory())
            app.push_screen(MapScreen("mapa"))
            await _settle(pilot)
            for key in (*view_keys, *keys):
                await pilot.press(key)
                await _settle(pilot, 2)
            # The trigger is asserted, not assumed: the frame is that view's.
            assert isinstance(app.screen, MapScreen) and app.screen.legend_view == view
            painted |= harvest(app.screen)
    return painted


async def _sala_harvest(tmp_path) -> set:
    app = MapperApp(tmp_path)
    async with app.run_test(size=VIEW_SIZE) as pilot:
        app.store.save("legado", legacy_map())
        app.store.save("plataforma", concept_map())
        (app.store.workspace / "roto.mmd").write_text(CYCLE_MMD, encoding="utf-8")
        app.store.record_session("legado", "rrhh0")
        app.notify = lambda *a, **k: None
        app.push_screen(HomeScreen())
        await _settle(pilot, 4)
        assert isinstance(app.screen, HomeScreen) and app.screen.legend_view == "sala"
        return harvest(app.screen)


def _agreement(view: str, painted: set) -> tuple[list, list]:
    members = vocabulary_for(view)
    assert members, f"{view} explains nothing; this arm would pass vacuously"
    unpainted = [
        (vid, sample, style) for vid, sample, _label, style in members
        if not any(ch in glyph_set(vid, sample) and _paints_as(st, style) for ch, st in painted)
    ]
    explained = frozenset().union(*(glyph_set(vid, sample) for vid, sample, _l, _s in members))
    undeclared = sorted({ch for ch, _st in painted if meaningful(ch) and ch not in explained})
    return unpainted, undeclared


@pytest.mark.parametrize("view", ["atlas", "esquema", "mapa mental", "sala"])
async def test_d2_the_legend_and_the_view_agree_in_both_directions(tmp_path, view):
    """`INC8-F2` / `UX-F3`, closed: what the legend explains is what the view
    paints, in the declared style, and nothing meaningful the view paints is
    left out of the view's legend."""
    painted = await (_sala_harvest(tmp_path) if view == "sala" else _map_harvest(tmp_path, view))
    unpainted, undeclared = _agreement(view, painted)
    assert not unpainted and not undeclared, (
        f"{view}: SOUNDNESS -- declared but not painted in its declared style: {unpainted}\n"
        f"{view}: COMPLETENESS -- painted but in no member of this view: "
        f"{[(c, f'U+{ord(c):04X}') for c in undeclared]}"
    )


def test_d2_the_exclusion_rule_keeps_the_forms_the_catalogue_kept():
    """The rule's own arm: it must not exclude a glyph a member depends on.
    A rule that dropped `▸` or braille would make completeness vacuous for
    exactly the forms the operator asked about."""
    for ch in "▐▸◫✓░▰▱▽◆▾∙█▒╱▲⊘▁●↩⠀⣿":
        assert meaningful(ch), f"U+{ord(ch):04X} is excluded by the rule"
    for ch in "a3 ·…—/%+":
        assert not meaningful(ch), f"{ch!r} should be text or punctuation"
    assert not meaningful("↵"), "a key glyph is explained by the key section"
