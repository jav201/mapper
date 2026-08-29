"""The renderer contract: one parameter object, and the protocol that consumes it.

`IRenderer.render` was frozen and, executed at `3fe0e4b`, existed as a Python
type **zero** times -- it survived only as prose in two comments.  This module
is its first mechanical enforcement, and the reason the batch's headline A3 is
an A3 at all.

WHY A PARAMETER OBJECT AND NOT ADDITIVE KEYWORDS.  Decided on measured evidence
rather than taste: the additive-keyword shape was already broken here.
`app.py`'s export site passed `query` without `diff` while the canvas site
passed both, so an SVG exported during a diff silently dropped its tinting; and
four of the six renderers declared `**kwargs` and dropped `query` on the floor,
which made "the hit count is right in every view" unbuildable while that swallow
lived.  Ten loose keywords would make every future capability another interface
migration.

ADDING A DEFAULTED FIELD BELOW IS ADDITIVE AND NEVER RE-OPENS THE A3.  That rule
is what keeps four later increments out of A3 territory: the roster is pinned
here, once, and grows by default-carrying addition thereafter.  Only the first
migration is an A3.

REMOVING A FIELD IS NOT THE SYMMETRIC CASE AND IS NOT EXEMPT BY CATEGORY.  The
rule above is stated for additions and it does not extend to removals by
symmetry: adding a defaulted field cannot break a reader, while removing one
breaks every reader it had.  A field may be removed without re-opening the A3
only when its product readers are ENUMERATED AND MIGRATED IN THE SAME INCREMENT.
What makes that sufficient is what the A3's subject actually is -- the signature
of `IRenderer.render`, which a roster change does not touch -- and it is
mechanically enforced by `tests/test_a3_census.py`, which pins that every field
carries a default and never which fields exist.  A census that green-lights a
removal is therefore not evidence that removals are safe; it is evidence that
this census does not look.

`query` was removed in Inc-4a under exactly that condition, and the condition was
measured rather than assumed: ONE product reader (the layered renderer), ONE
writer (`MapScreen._view_state`), ONE test reader, all three rewritten by the
increment that removed it.  A field with a fourth reader is a different question
and this paragraph is not a licence to skip asking it.

THIS MODULE IMPORTS NO TEXTUAL, AND MUST NOT.  `views` is the headless boundary:
a state model that reached for a Textual concept would put the app's state
inside it and make `export` untestable without an event loop.  `focus_owner` is
therefore a plain string, not a widget reference.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from rich.text import Text

from mapper.diff import DiffResult
from mapper.model import Graph

# The declared value domain of `ViewState.focus_owner`.  `""` means "unknown",
# which is what every renderer sees until a screen supplies the real owner, and
# it must paint what the tree painted before this field existed.
FOCUS_OWNERS = ("", "canvas", "rail", "inspector")


@dataclass(frozen=True)
class ViewState:
    """Everything a renderer needs beyond the graph itself.

    FROZEN, and EVERY FIELD CARRIES A DEFAULT.  Both properties are load-bearing
    rather than stylistic:

    * frozen, because a renderer receives a picture request and must not be able
      to mutate the caller's state while drawing;
    * fully defaulted, because `ViewState()` must construct with no arguments.
      With required fields, the increment that adds a field breaks every
      existing construction, and the natural repair is to pass the new argument
      everywhere -- which turns each later field into its own migration and
      destroys the additive property this object exists to provide.
    """

    selected_id: str | None = None
    w: int = 80
    h: int = 24
    # Which region of the screen currently holds the keyboard, so a renderer can
    # stop claiming a selection the operator's focus has left.  One of
    # FOCUS_OWNERS.
    focus_owner: str = ""
    # The RESOLVED matching ids, decided by `mapper.search` and never by a
    # renderer.  This replaced a `query: str` the renderer had to interpret for
    # itself, which is how two definitions of "hit" came to ship at once and
    # disagree by `{id, meta, attachments}`.  A `frozenset` rather than a `set`
    # for the same reason `folded` is one: this object is frozen, and a mutable
    # default would let a renderer edit the caller's hit set while drawing.
    hits: frozenset[str] = frozenset()
    diff: DiffResult | None = None
    # Where the drawing origin sits, in canvas cells.  The renderer translates
    # by these; it holds no pan state of its own, per the ARQ rule that
    # `ViewState` is a message and not a store (LLR-N06.1.1).
    pan_x: int = 0
    pan_y: int = 0
    # The node ids whose subtrees are folded away.  `MapScreen` owns this set
    # and the renderer is one of its two readers (LLR-N06.2.1); a `frozenset`
    # rather than a `set` because this object is frozen and a mutable default
    # would let a renderer edit the caller's fold state while drawing.
    folded: frozenset[str] = frozenset()


@runtime_checkable
class IRenderer(Protocol):
    """A map renderer: graph plus view state in, a picture out.

    `runtime_checkable` buys an `isinstance` check over MEMBER PRESENCE ONLY --
    it never inspects signatures.  Every renderer in this tree already had a
    `render` attribute before the migration, so `isinstance` alone is green on
    the unmigrated tree and proves nothing about the contract.  It is kept as a
    STRUCTURAL guard, catching a renderer that stops being one; the signature is
    asserted separately, and that pair is what discriminates.
    """

    def render(self, graph: Graph, state: ViewState) -> Text:
        ...
