"""Shared screen helpers for the mapper screens — A1 of batch
`2026-10-09-modular-batch` (LLR-MOD.1.1).

Home of the helpers every screen uses: the hint-string constants, `map_hint` /
`home_hint`, `MapHintLine` (the shared hint widget — ARCH-8), the seat-derived
`screen_bindings` / `keybar_groups`, and the refusal/toast save guards.  Every
name is re-exported from `mapper.app` so historical `from mapper.app import X`
sites keep resolving (LLR-MOD.3.1); `screens/*` modules import them here
directly (the B-02 remediation, LLR-MOD.6.1).
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.screen import Screen

from mapper import darkside
from mapper.keymap import (
    SCOPE_HOME,
    SCOPE_MAP,
    bar_group_order,
    bindings_for,
    group_header,
    hint_pair,
    textual_bindings,
)
from mapper.model import Graph
from mapper.osopen import confine_reason, refusal_sentence
from mapper.store import MapIdError
from mapper.widgets.chrome import HintLine

if TYPE_CHECKING:  # `_save_or_toast` annotates its store param as "MapStore"
    from mapper.store import MapStore


# The strip the search count is painted on (`#D37`), declared ONCE.  It was
# named nowhere in the sealed text, which made a requirement that the empty
# count paint "at the same position a non-zero count occupies" a positional
# claim about an unnamed surface.  `#map-pagination` is the natural home: it
# already carries the overflow declaration, so the count joins a strip that
# exists to declare counts.  New predicates read this name rather than re-typing
# it -- `test_overflow.py` still spells the literal at 7 sites, which predate the
# constant and are recorded rather than swept into this increment's diff.
COUNT_REGION_ID = "map-pagination"

# What a pan key says in a view that does not consume pan (`PAN-1`), spelled
# ONCE so the branch that SETS it and the seam that CLEARS it cannot drift
# (`DECL-118-TWICE`: anything spelled twice will drift, derive it).
#
# IT PAIRS THE REFUSAL WITH THE NEXT MOVE, which is this strip's house pattern --
# `completa «X» · ↵ guarda · esc deja el campo`, `rail · ↵ plegar rama · esc
# volver al mapa`.  A bare refusal would be the only hint here that tells the
# operator what will not work without telling him what will, and in these two
# views the alternative is the whole point of the ruling: navigation is
# focus-based, so `j/k/h/l` is what moves.
#
# AND IT READS AS A STANDING PROPERTY, not a transient condition, which is what
# the ruling says it is.  The contrast with `borde del territorio` is
# deliberate: that one names a LOCATION and correctly reads as transient --
# move the other way and it is gone.  This one never stops being true while the
# view is on screen, and wording it as a passing state would be the `UI-AT058`
# failure (text that invites the operator to wait out a permanent condition).
PAN_INERT_HINT = "this view does not scroll · navigate with j/k/h/l"
PAN_EDGE_HINT = "edge of the map"

# WHAT the count line counts, in the operator's words, spelled ONCE.  The strip
# also paints a page numeral (`1/8`) and an off-canvas numeral, so a bare
# `5/5 coincidencias` would leave two count-shaped surfaces distinguishable only
# by an implementer's wording choice.  Naming the subject is the requirement
# (`AT-052`), and a single declaration is what makes the test a DERIVATION of
# the shipped string rather than a second copy of it that drifts.
SEARCH_COUNT_SUBJECT = "matches in the map"

# `LLR-N07.3.4` — what the count region says while a query is live, spelled ONCE
# each.  The region declares the query at EVERY graph size now, so these strings
# are read by the count line, and the notice is read by the hint line too: two
# surfaces, one declaration.
#
# THE NOTICE NAMES BOTH SUSPENDED THINGS, and the second name is not padding.
# `#D43`'s example wording is `resaltado suspendido`, but above the bound the
# WALK declines as well -- `_walk_hits` returns on `hits is None` -- so a notice
# naming only the highlighting leaves the operator to discover the other half by
# pressing `n` and getting a toast.  That is the same hidden state one surface
# over, which is the defect this clause exists to close.
SEARCH_ACTIVE_LABEL = "search"
SEARCH_SUSPENDED_NOTICE = "highlighting and walk suspended"

# THE ECHOED QUERY IS OPERATOR TEXT: unbounded in length, and the count region
# SUPERSEDED BY `Inc-STRIPS`: `#map-pagination` now carries `max-height: 3;
# overflow: hidden`, so it CLIPS rather than wraps and an over-long echo is
# dropped instead of growing the strip.  `_QUERY_ECHO_CELLS` therefore protects
# the strip's CONTENT from the clip, not `#map-body` from the strip -- a reader
# who trusts the superseded reasoning below would relax the cap and get F1's
# silent-omission failure on a second surface.
#
# HISTORICAL, from the pre-bound tree:
# WRAPS rather than clips (`#map-pagination` has no height rule, so it is
# `height: auto`).  An unbounded echo therefore does not overflow the strip -- it
# GROWS the strip and takes the rows from `#map-body`, which is `height: 1fr`.
# The cap is what stops that, and `_query_echo` records why a FIXED cap is right
# here where `_HINT_BRANCH_CELLS` had to become the row's remainder.  The echo is
# never dropped: predicate 1 requires the region to NAME THE QUERY at every
# width, so it is truncated rather than omitted.
_QUERY_ECHO_CELLS = 32

# The map's resting hint, spelled ONCE.  Three sites restore it now that `esc`
# clears a live search instead of leaving the map (`#D38`): `compose`, the field
# editor's exit, and the clear itself.  Three copies of a sentence are three
# chances for two of them to drift.  A function, not a constant: every word
# beside a key is the seat's (`K3`), and a test that relabels the seat rebuilds
# it (`INC9BC-CR-F2`).  `INC9BC-UX-F3`: `j/k/h/l move`, in the seat's word.
def map_hint() -> str:
    return (
        f"j/k/h/l {group_header('nav')} · {hint_pair(SCOPE_MAP, 'open_ficha')} · "
        f"{hint_pair(SCOPE_MAP, 'search')}"
    )


class MapHintLine(HintLine):
    """The map's hint line, able to carry the unsaved-draft prefix (R8, PDR C6).

    While the card is hidden a pending draft has no other surface, so the line
    leads with `● unsaved (N) · ctrl+s save` in ALERT (the operator's ruling).
    The prefix is part of the PAINT, not of `text`: every `set_hint` the screen
    issues for its own reasons keeps it, so the line says the draft exists for as
    long as it does.
    """

    draft_prefix = ""

    def set_hint(self, text: str, key: str | None = None) -> None:
        super().set_hint(text, key)
        self._paint_prefix()

    def set_draft_prefix(self, prefix: str) -> None:
        if prefix != self.draft_prefix:
            self.draft_prefix = prefix
            self._paint_prefix()

    def _paint_prefix(self) -> None:
        visual = darkside.hint_line(self.text, self.key)
        if self.draft_prefix:
            visual = darkside.Text.assemble((self.draft_prefix, darkside.ALERT), visual)
        self.update(visual)


# The home hint (`M1`): `↵` opens the selected map, and the doors are still the way
# to start.  The word beside `↵` is the seat's (`K3`), so a function, like `map_hint`.
# `N1`: with no recent map `↵` does nothing, so the hint does not offer it.
def home_hint(has_maps: bool = True) -> str:
    if not has_maps:
        return "choose a door"
    return f"{hint_pair(SCOPE_HOME, 'open_selected')} · or choose a door"


# The key of the home strip's first door, from the seat: `tab_strip` marks a tab
# active, and paints the doors' letters, only when handed THIS key (`R3-CR-F3`).
def _home_door_key() -> str:
    return next(
        b.key for b in bindings_for(SCOPE_HOME, include_app=False) if b.action == "consult"
    )


# The ceiling on the fold-auto-open segment of the walk's hint line.  Branch
# TITLES are file-derived: unbounded in length, and one walk can open several
# nested folds at once, so both the count and the width need a bound or the
# strip grows and `HintLine` wraps the canvas out of the frame.
#
# THE CELL BUDGET IS THE ROW'S REMAINDER, not a constant, and that was measured:
# a fixed 40 cells fits at 118 columns and WRAPS at 80, where the whole strip
# then left the painted frame -- affordances included.  `_HINT_NAME_OVERHEAD` is
# the chrome around the name: `darkside.hint_line`'s own 12-cell prefix, the
# 10-cell separator, and the closing guillemet.  Below `_HINT_NAME_MIN_CELLS`
# there is no room to say anything useful, so the announcement is DROPPED rather
# than allowed to take a row from the map: the affordances outrank it.
_HINT_BRANCHES = 3
_HINT_BRANCH_CELLS = 40
_HINT_NAME_OVERHEAD = 23
_HINT_NAME_MIN_CELLS = 8


def screen_bindings(scope: str) -> list[Binding]:
    """Generate a screen's `BINDINGS` from the one keymap seat (US-N03).

    Screens never hand-write a binding list: the seat is the single source, so the
    keys a screen binds and the keys the palette and help advertise cannot drift.
    """
    return [
        Binding(key, action, label, priority=priority)
        for key, action, label, priority in textual_bindings(scope)
    ]


def keybar_groups(scope: str) -> list[str]:
    """The keybar's group order for *scope*, derived from the seat.

    Derived rather than hand-listed: a second list naming the map's groups would
    be exactly the drift the seat exists to prevent.
    """
    return bar_group_order(scope)


def _refusal_toast(screen: Screen, exc: Exception) -> bool:
    """Toast a refused map id (`A-113`) and return `True`; any other error: `False`.

    A `MapIdError`'s text is authored by the store and names the rule, never the
    typed name or a path, so it is the one exception text that may be shown.
    """
    if not isinstance(exc, MapIdError):
        return False
    screen.notify(darkside.plain(str(exc)), severity="error", markup=False)
    return True


def _save_or_toast(
    screen: Screen,
    store: "MapStore",
    map_id: str,
    graph: Graph,
    *,
    new: bool = False,
    toast: bool = True,
) -> bool:
    """Guard a `store.save()` call: on any raise, toast and return `False`.

    `new=True` writes through `store.create`, which refuses an id that is taken
    (`A-113`); the CSV "save as" is a creation, an edit of an open map is not.

    `toast=False` suppresses both toasts; the caller then emits its own single
    notice.  `_save_draft` uses it so a failed draft save shows ONE toast
    (`could not save '<map>' (<ErrorType>) · draft kept · <save> to retry`) instead of this one plus
    a second.

    The ONE guarded call site every other `store.save()` call routes through
    (`G6-C-F2`/`G6-C-F3`) — a screen calls this instead of writing its own
    `try`/`except`, so the toast wording lives in one place, not eight.

    `G6-C-F2`: the toast names the map id and the exception TYPE only, never
    `str(e)` — an `OSError`'s own message embeds the full absolute path and,
    on Windows, the operator's account name (the leak `store.load`'s toast was
    already fixed against at `B-30`; this is the same fix for `store.save`).
    Both interpolated pieces are routed through `darkside.plain()`: `map_id`
    can be operator-typed (`ImportPreviewScreen.action_save`'s "guardar como"
    prompt, `G6-C-F4`) and a masked exception type name is always ASCII, but
    routing it too costs nothing and keeps the rule "nothing reaches this
    toast unplained" total rather than case-by-case.
    """
    try:
        write = store.create if new else store.save
        write(map_id, graph)
    except Exception as e:  # noqa: BLE001 -- deliberately generic, see A-111.
        # B-103: the slot is declared on MapScreen (read by its draft save); on
        # other screens the write is advisory and unread.
        screen._last_save_error = type(e).__name__
        if toast:
            if _refusal_toast(screen, e):
                return False
            screen.notify(
                f"could not save {darkside.plain(map_id)!r}: "
                f"{darkside.plain(type(e).__name__)}",
                severity="error",
                markup=False,
            )
        return False
    return True


def _path_refusal(text: str, workspace: Path) -> str | None:
    """The fixed sentence for a `file` attachment text that may not be stored or opened, else None: the one
    reason -> sentence mapping, `osopen.refusal_sentence` (`U1`, `Y1` for a colon, `W2`, `V1`; an unreadable
    component is V1)."""
    path, reason = confine_reason(text, workspace)
    if path is not None:
        return None
    return refusal_sentence(reason)
