"""`SEC-H2`: a ficha title must not be able to act on the confirmation dialog.

THE DEFECT, as the S-E security pass fired it. `_ConfirmScreen` takes a `str`
and `compose` hands it to `Static`, which renders it through **Textual's**
markup grammar -- a different and wider grammar than Rich's, and one this batch
had not modelled. Textual markup accepts `[@click=<action>]`, which binds a
runnable action to a span. The confirmation message interpolates the node's own
ficha title raw (`app.py`'s archive action), and a sidecar title is untrusted
input, so a title could bind `screen.confirm` to the very words the operator
reads -- ONE CLICK ON THE NODE NAME ARCHIVES THE SUBTREE WITHOUT `y`.

WHY IT IS A SECURITY DEFECT AND NOT A RENDERING ONE: the rendered sentence is
IDENTICAL to the benign one. The payload is not in the text the operator reads,
so the system stops enforcing the human-in-the-loop and the human cannot see
that it stopped. `[conceal]` hides the rest of the sentence; an unclosed tag
kills the app out of the compositor's own reflow, where the caller cannot catch
it.

TWO HAZARDS, TWO FIXES, AND THEY ARE NOT THE SAME HAZARD.

* MARKUP is neutralised AT THE SINK, by `Static(..., markup=False)` -- Textual's
  own switch for "do not run the grammar over this", and the same idiom this
  module already uses on every `notify`. Fixing the sink covers every caller,
  present and future; escaping at the one call site would be the instance fix
  for a class defect, which is the failure this batch exists to close.
  `A COERCION IDIOM IS CORRECT ONLY RELATIVE TO ITS SINK, SO A CENSUS MUST
  CLASSIFY THE SINK, NOT THE CALL.`
* HOSTILE CODE POINTS are coerced AT THE SOURCE, by `darkside.plain`, and this
  is a DIFFERENT hazard: `markup=False` stops the title ACTING on the dialog, it
  does not stop the title REORDERING the sentence, because a bidi override is
  faithful text that every renderer paints faithfully. The archive action's own
  toast eight lines above already called `darkside.plain` on the identical
  value; the confirmation built it again, raw.

Hostile code points are NAMED, never pasted (`C-56`): U+202E RIGHT-TO-LEFT
OVERRIDE, U+200D ZERO WIDTH JOINER.
"""
from __future__ import annotations

import pytest
from rich.text import Text
from textual.widgets import Static

from mapper import darkside
from mapper.app import _ConfirmScreen

# Built with `chr(0x…)` at test time, never spelled in the file: `C-56`, and the
# tree enforces it (`test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts`).
# Batch 1 shipped a literal in a fixture and the resulting test passed on
# everything; and an unterminated override inside a file reorders the very text
# documenting the threat.
RLO = chr(0x202E)  # U+202E RIGHT-TO-LEFT OVERRIDE
ZWJ = chr(0x200D)  # U+200D ZERO WIDTH JOINER
REPLACEMENT = chr(0xFFFD)  # what `darkside.plain` maps the banned ranges to
CLICK_PAYLOAD = "[@click=screen.confirm]Acta[/]"


def _label_of(screen: _ConfirmScreen) -> Static:
    return screen.query_one("#confirm-label", Static)


def _painted(widget: Static) -> str:
    """What the widget actually PAINTS, read off the frame.

    THE FRAME IS THE ORACLE. Reading the widget's stored content would not
    distinguish the two states at all -- both hold a `Content` -- because the
    grammar runs on the way to the screen. Measured on this Textual (8.2.8) with
    a `[@click=...]` payload: `markup=True` paints `'xActay'`, the tags consumed
    and an action bound; `markup=False` paints the tags literally. That
    difference is the whole finding, and it is only visible here.
    """
    out = []
    for y in range(widget.size.height or 1):
        try:
            out.append("".join(seg.text for seg in widget.render_line(y)))
        except Exception:  # past the rendered region
            break
    return "\n".join(out)


@pytest.mark.asyncio
async def test_sec_h2_a_message_cannot_bind_a_clickable_action(tmp_path):
    """The sink must not PARSE what it is handed.

    The oracle is what is PAINTED, not what is stored: both states hold a
    `Content`, and the grammar runs on the way to the screen. If the markup is
    parsed the tags are GONE from the painted row -- consumed, with a runnable
    action bound in their place. If it is not, they appear literally.
    """
    from mapper.app import MapperApp

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.push_screen(_ConfirmScreen(f"¿archivar «{CLICK_PAYLOAD}»?"))
        await pilot.pause()
        painted = _painted(_label_of(app.screen))

        # Positive control first: the arm is looking at the right widget.
        assert "archivar" in painted, (
            f"the arm is not reading the confirmation label at all: {painted!r}"
        )
        assert "[@click=screen.confirm]" in painted, (
            "Textual's markup grammar consumed the payload instead of painting it "
            "literally, so an untrusted ficha title can bind a runnable action to "
            f"the words the operator reads -- one click confirms: {painted!r}"
        )


@pytest.mark.asyncio
async def test_sec_h2_the_archive_confirmation_coerces_the_title_it_quotes(tmp_path):
    """The SOURCE half: a `Text` carries U+202E faithfully, so coerce first.

    Driven through the REAL `x` chord rather than by calling the helper, because
    the defect is that this particular call site built the value raw while its
    own neighbour two lines above coerced it.
    """
    from mapper.app import MapperApp, MapScreen
    from mapper.model import Edge, Ficha, Graph, Node

    graph = Graph()
    graph.add_node(Node(id="root", ficha=Ficha(title="repo", meta="", notes="")))
    graph.add_node(Node(id="malo", ficha=Ficha(title=f"acta{RLO}{ZWJ}firmada",
                                               meta="", notes="")))
    graph.add_edge(Edge("root", "malo"))
    graph.root_id = "root"

    app = MapperApp(tmp_path)
    async with app.run_test(size=(118, 34)) as pilot:
        await pilot.pause()
        app.store.save("m", graph)
        app.push_screen(MapScreen("m"))
        await pilot.pause()
        screen = app.screen
        screen.nav.cursor = "malo"
        await pilot.press("x")
        await pilot.pause()

        assert isinstance(app.screen, _ConfirmScreen), (
            "the `x` chord did not raise the confirmation; the arm never reached "
            "its subject"
        )
        shown = _painted(_label_of(app.screen))

        # The positive control: the arm really is looking at the quoted title.
        assert "acta" in shown and "firmada" in shown, (
            f"the confirmation does not quote the node title at all: {shown!r}"
        )
        for raw, name in ((RLO, "U+202E"), (ZWJ, "U+200D")):
            assert raw not in shown, (
                f"{name} reached the confirmation dialog raw -- the title can "
                f"reorder the sentence the operator is approving: {shown!r}"
            )
        assert REPLACEMENT in shown, (
            "nothing was coerced, so the absence above is the arm missing its "
            "subject rather than the sink being clean"
        )


def test_sec_h2_the_oracle_can_tell_the_two_forms_apart():
    """Instrument RED-proof: the oracle must distinguish parsed from literal.

    Without this, both assertions above could be true of an oracle that never
    looks at markup at all.
    """
    assert "[@click=screen.confirm]" in Text(f"x{CLICK_PAYLOAD}y").plain
    assert darkside.plain(f"acta{RLO}firmada").count(REPLACEMENT) == 1
    assert RLO not in darkside.plain(f"acta{RLO}firmada")
