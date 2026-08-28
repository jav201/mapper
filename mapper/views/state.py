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
    # TRANSITIONAL.  The renderer should receive resolved id sets, never a
    # predicate it has to interpret -- there are two live definitions of "what
    # matches" in this tree today and they disagree.  Replaced by a resolved
    # `hits` set in the increment that gives that question a single owner.
    query: str = ""
    diff: DiffResult | None = None


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
