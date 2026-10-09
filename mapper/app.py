"""Textual TUI app for mapper — darkside UI."""
from __future__ import annotations

import asyncio
import copy
import json
import re
from dataclasses import replace
from datetime import date, datetime, timedelta
from pathlib import Path

from rich.markup import escape
from rich.text import Text
from textual import events, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.geometry import Region
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Input, Label, Static
from textual.worker import WorkerFailed

from . import darkside, github
from .diff import DiffResult, git_diff
from .export import ExportError, ExportTooLarge, save_svg
from .github import GitHubConnector, GitHubError, painted_repo
from .import_csv import preview_csv
from .keymap import (
    SCOPE_APP,
    SCOPE_DRAFT,
    SCOPE_HOME,
    SCOPE_IMPORT,
    SCOPE_MAP,
    SCOPE_PLUG,
    SCOPE_REPO,
    KeyBinding,
    bar_group_order,
    bindings_for,
    group_header,
    groups_for_keybar,
    hint_pair,
    label_for,
    textual_bindings,
)
from .mermaid import dump as dump_mermaid, slugify
from .model import Attachment, Document, Edge, Ficha, Graph, Node
from .motion import pulse_cursor
from .osopen import (
    ATTACHMENT_HARD_LINKED, OK as OSOPEN_OK, PATH_NOT_SUPPORTED, confine_reason, open_external, refusal_sentence,
    safe_local_path,
)
from .screens import (
    CommandPalette, CoverageScreen, DraftGuardScreen, FactoryScreen, HelpScreen, SettingsScreen,
)
from .search import SearchIndex
from .store import TEMPLATES, MapIdError, MapStore, MapStoreError
from .views.layered import (
    MAX_RENDER_NODES,
    overflow_phrase,
    LayeredRenderer,
    _geometry as layered_geometry,
    header_rows,
    pan_extent,
    painted_ids,
)
from .views.state import ViewState, export_neutralised
from .views.outline import (
    OutlineRenderer,
    header_rows as outline_header_rows,
    painted_ids as outline_painted_ids,
)
from .views.radial import (
    RadialRenderer,
    header_rows as radial_header_rows,
    painted_ids as radial_painted_ids,
)
from .widgets.chrome import GroupBox, HintLine, KeyBar, TabStrip
from .widgets.inspector import INSPECTOR_WIDTH, FieldInput, FichaInspector
from .widgets.rail import RAIL_WIDTH, OutlineRail


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


class NavigationModel:
    """Cursor navigation over a tree graph."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self.cursor = graph.root_id

    def children(self, nid: str | None = None) -> list[str]:
        nid = nid or self.cursor
        return self.graph.children_of(nid) if nid else []

    def parent(self) -> str | None:
        return self.graph.parent_of(self.cursor) if self.cursor else None

    def next_sibling(self) -> str | None:
        p = self.parent()
        if p is None:
            return None
        sibs = self.children(p)
        if self.cursor not in sibs:
            return None
        idx = sibs.index(self.cursor)
        return sibs[idx + 1] if idx + 1 < len(sibs) else None

    def prev_sibling(self) -> str | None:
        p = self.parent()
        if p is None:
            return None
        sibs = self.children(p)
        if self.cursor not in sibs:
            return None
        idx = sibs.index(self.cursor)
        return sibs[idx - 1] if idx > 0 else None

    def first_child(self) -> str | None:
        ch = self.children()
        return ch[0] if ch else None


# ---------------------------------------------------------------------------
# Modal helpers
# ---------------------------------------------------------------------------


def _path_refusal(text: str, workspace: Path) -> str | None:
    """The fixed sentence for a `file` attachment text that may not be stored or opened, else None: the one
    reason -> sentence mapping, `osopen.refusal_sentence` (`U1`, `Y1` for a colon, `W2`, `V1`; an unreadable
    component is V1)."""
    path, reason = confine_reason(text, workspace)
    if path is not None:
        return None
    return refusal_sentence(reason)


class _PromptScreen(ModalScreen[str | None]):
    """Simple darkside modal that returns a single text value."""

    BINDINGS = [("escape", "cancel", "cancel")]

    def __init__(self, title: str, placeholder: str = "") -> None:
        super().__init__()
        self.title = title
        self.placeholder = placeholder

    def compose(self) -> ComposeResult:
        # `S-F2`, and it is `SEC-H2`'s own lesson applied to the instance that
        # fix missed.  `SEC-H2` was fixed AT THE SINK precisely so the CLASS
        # would be closed rather than one call site -- and then only
        # `_ConfirmScreen` got the switch, leaving its structural twin here with
        # the grammar still on.  Every caller passes a literal today (all seven
        # derived, and an independent census over the whole suite confirmed it),
        # so nothing is exploitable; the point is that `self.title` is a `str`
        # PARAMETER, and the next caller to route a node title through it would
        # reopen the defect with every arm green.
        #
        # A class fix applied to one member of the class is an instance fix
        # wearing a class fix's clothes.
        yield Vertical(
            Static(self.title, id="prompt-label", markup=False),
            Input(placeholder=self.placeholder, id="prompt-input"),
            Static("", id="prompt-hints"),
            id="prompt-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#prompt-input", Input).focus()
        hints = Text.assemble(
            ("↵", darkside.INK),
            (" confirm   ", darkside.MUT),
            ("esc", darkside.INK),
            (" cancel", darkside.MUT),
        )
        self.query_one("#prompt-hints", Static).update(hints)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss(value if value else None)


class _ConfirmScreen(ModalScreen[bool]):
    """Simple yes/no confirmation modal."""

    BINDINGS = [
        ("y", "confirm", "yes"),
        ("n", "dismiss", "no"),
        ("escape", "dismiss", "no"),
        ("q", "dismiss", "no"),
    ]

    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        # `SEC-H2`: `markup=False` IS THE SECURITY CONTROL, not a formatting
        # preference.  `Static` renders a `str` through TEXTUAL's markup grammar
        # -- wider than Rich's, and it accepts `[@click=<action>]`, which binds a
        # runnable action to a span.  This message interpolates the node's ficha
        # title, and a sidecar title is untrusted input, so a title can bind
        # `screen.confirm` to the very words being read and archive a subtree on
        # ONE CLICK, with no `y`.  Measured on the unfixed tree: the payload
        # `[@click=screen.confirm]Acta[/]` painted as `¿archivar «Acta»?` -- a
        # sentence IDENTICAL to the benign one.  That is what makes it a security
        # defect rather than a rendering bug: the human-in-the-loop stops being
        # enforced and the human cannot see that it stopped.  `[conceal]` hides
        # the rest of the sentence, and an unclosed tag kills the app out of the
        # compositor's own reflow, where no caller can catch it.
        #
        # FIXED AT THE SINK, DELIBERATELY.  Escaping at the one call site would
        # be the instance fix for a class defect, and the next message built here
        # would inherit the hazard.  A coercion idiom is correct only relative to
        # its SINK -- and `markup=False` is the idiom this module already uses on
        # every `notify`.
        yield Vertical(
            Static(self.message, id="confirm-label", markup=False),
            Static("", id="confirm-hints"),
            id="confirm-dialog",
        )

    def on_mount(self) -> None:
        hints = Text.assemble(
            ("y", darkside.INK),
            (" yes   ", darkside.MUT),
            ("n", darkside.INK),
            (" no", darkside.MUT),
        )
        self.query_one("#confirm-hints", Static).update(hints)

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_dismiss(self) -> None:
        self.dismiss(False)


class _TemplateScreen(ModalScreen[str | None]):
    """Modal that lets the user pick a map template."""

    BINDINGS = [("escape", "dismiss", "close"), ("q", "dismiss", "close")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("choose template", id="template-title"),
            DataTable(id="template-table", cursor_type="row"),
            id="template-dialog",
        )

    def on_mount(self) -> None:
        table = self.query_one("#template-table", DataTable)
        table.clear()
        table.add_columns("▐ template", "description")
        for key, data in TEMPLATES.items():
            desc = data.get("seed_title", key)
            table.add_row(escape(key), escape(desc), key=key)
        if table.row_count == 0:
            table.add_row("(no templates)", "", key="")

    def action_dismiss(self) -> None:
        self.dismiss(None)

    def action_select(self) -> None:
        table = self.query_one("#template-table", DataTable)
        if table.cursor_row is None:
            self.dismiss(None)
            return
        key = table.coordinate_to_cell_key(table.cursor_coordinate)
        value = str(key.value) if key else ""
        self.dismiss(value if value else None)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        value = str(event.row_key.value)
        self.dismiss(value if value else None)


class _FichaScreen(ModalScreen[None]):
    """Modal that shows the selected node's ficha details."""

    BINDINGS = [("escape", "dismiss", "close"), ("q", "dismiss", "close")]

    def __init__(self, node: Node, graph: Graph) -> None:
        super().__init__()
        self.node = node
        self.graph = graph

    def compose(self) -> ComposeResult:
        yield Vertical(Static(id="ficha-content"), id="ficha-dialog")

    def on_mount(self) -> None:
        ficha = self.node.ficha
        text = Text()
        text.append(escape(ficha.title or self.node.id), style=f"bold {darkside.INK}")
        text.append("\n")
        if ficha.meta:
            text.append(escape(ficha.meta), style=darkside.MUT)
            text.append("\n")
        if ficha.state:
            text.append("state ", style=darkside.MUT)
            text.append(escape(ficha.state), style=darkside.INK)
            text.append("\n")

        have, req = ficha.required_coverage(self.graph.schema)
        if req:
            text.append("coverage ", style=darkside.MUT)
            text.append_text(darkside.step_meter(have, req))
            text.append("\n")

        doc = ficha.fields.get("D", "")
        text.append("record ", style=darkside.MUT)
        text.append(escape(doc) if doc else "—",
                    style=darkside.INK if doc else darkside.ALERT)
        text.append("\n")
        text.append("owner ", style=darkside.MUT)
        text.append(escape(ficha.fields.get("O") or "—"), style=darkside.INK)
        text.append("\n")
        text.append("created ", style=darkside.MUT)
        text.append(escape(ficha.fields.get("Y") or "—"), style=darkside.INK)
        text.append("\n")

        linked = self.node.linked_map_id()
        if linked:
            text.append("link ", style=darkside.MUT)
            text.append(escape(linked), style=darkside.ACCENT)
            text.append("  (↵ opens the map)", style=darkside.MUT)
            text.append("\n")

        if ficha.notes:
            text.append("\nnotes\n", style=darkside.MUT)
            text.append(escape(ficha.notes), style=darkside.INK)

        if ficha.fields:
            text.append("\nfields\n", style=darkside.MUT)
            for key, value in ficha.fields.items():
                if key in {"D", "O", "Y", "map"}:
                    continue
                text.append(f"  {escape(key)} ", style=darkside.MUT)
                text.append(escape(value), style=darkside.INK)
                text.append("\n")

        if ficha.attachments:
            text.append("\nattachments\n", style=darkside.MUT)
            for att in ficha.attachments:
                text.append(f"  {escape(att.caption or att.path)}\n", style=darkside.INK)

        self.query_one("#ficha-content", Static).update(text)

    def action_dismiss(self) -> None:
        self.dismiss(None)


class ConstructScreen(ModalScreen[str | None]):
    """Ask for a new map name and return it."""

    BINDINGS = [("escape", "cancel", "cancel")]

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("new map", id="construct-label"),
            Input(placeholder="my-new-map", id="construct-input"),
            Static("", id="construct-hints"),
            id="construct-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#construct-input", Input).focus()
        hints = Text.assemble(
            ("↵", darkside.INK),
            (" create   ", darkside.MUT),
            ("esc", darkside.INK),
            (" cancel", darkside.MUT),
        )
        self.query_one("#construct-hints", Static).update(hints)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.value.strip().replace(" ", "-")
        if not name:
            return
        # `A-113`: refuse here too, so the dialog stays open and the name can be
        # fixed; the store refuses again by itself (it is the boundary).
        try:
            self.app.store.check_new_map_id(name)  # type: ignore[attr-defined]
        except MapStoreError as e:
            if _refusal_toast(self, e):
                return
            raise
        self.dismiss(name)


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------


class HomeScreen(Screen):
    """Home screen with GLANCE posture: one hero, everything else available."""

    KEY_SCOPE = SCOPE_HOME
    # HLR-N16.2: the view name the legend's title carries (`darkside.VIEW_NAMES`).
    legend_view = darkside.VIEW_NAMES["home"]
    BINDINGS = screen_bindings(SCOPE_HOME)

    def compose(self) -> ComposeResult:
        yield TabStrip(_home_door_key())
        yield Static("", id="home-identity")
        yield GroupBox(Static(id="home-hero"), id="home-hero-box")
        yield Static("", id="home-microbar")
        yield GroupBox(Static(id="home-resume"), id="home-resume-box")
        yield GroupBox(
            Vertical(
                Static("", id="home-empty"),
                DataTable(id="home-recents", cursor_type="row"),
                id="home-recents-inner",
            ),
            id="home-recents-box",
        )
        yield Static("", id="home-archived")
        yield HintLine(home_hint())
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    def _map_metrics(self, graph: Graph) -> dict[str, int]:
        total = len(graph.nodes)
        with_record = sum(1 for n in graph.nodes.values() if n.ficha.fields.get("D", "").strip())
        no_record = total - with_record
        today = date.today().isoformat()
        due = sum(
            1 for n in graph.nodes.values()
            if n.ficha.fields.get("due", "").strip() == today
        )
        have, req = graph.coverage()
        pct = int(100 * have / max(1, req))
        return {
            "total": total,
            "with_record": with_record,
            "no_record": no_record,
            "due": due,
            "coverage": pct,
        }

    def _hero_text(self, map_name: str, metrics: dict[str, int]) -> Text:
        sin_acta = metrics["no_record"]
        vencen = metrics["due"]
        # calm board: count in INK with no WARN line
        number_style = darkside.INK if sin_acta == 0 and vencen == 0 else darkside.WARN
        lines = Text()
        lines.append(darkside.draw_number(str(sin_acta), number_style))
        lines.append("\n", "")
        lines.append("nodes with no record\n", darkside.MUT)
        lines.append(escape(map_name) + "\n", darkside.INK)
        if vencen > 0:
            lines.append(f"▲ {vencen} due today", darkside.WARN)
        return lines

    def _microbar_text(self, metrics: dict[str, int]) -> Text:
        total = max(1, metrics["total"])
        con = metrics["with_record"]
        sin = metrics["no_record"]
        pct = metrics["coverage"]
        return Text.assemble(
            ("  with record ", darkside.MUT), (f"{con} ", darkside.MUT),
            darkside.microbar(con, total), ("    ", ""),
            ("no record ", darkside.WARN), (f"{sin} ", darkside.WARN),
            darkside.microbar(sin, total, fill=darkside.WARN), ("    ", ""),
            (f"coverage {pct} %", darkside.INK),
        )

    def _sparkline_text(self, store: MapStore) -> Text:
        today = date.today()
        days = [today - timedelta(days=i) for i in range(13, -1, -1)]
        counts: list[int] = []
        for d in days:
            day_count = 0
            for mmd in store.workspace.glob("*.mmd"):
                try:
                    mtime = date.fromtimestamp(mmd.stat().st_mtime)
                    if mtime == d:
                        day_count += 1
                except Exception:
                    pass
            counts.append(day_count)
        max_count = max(counts) if counts else 1
        # `A-105` / `INC7-CR-R3-F3` -- `counts` always has 14 entries, so the
        # `else 1` branch above never fires; when every entry is 0 (no `.mmd`
        # modified in the 14-day window) `max_count` is 0, and `c / max_count`
        # below must not divide by it.
        max_count = max_count or 1
        bars = "▁▂▂▃▃▄▅▆▇█"
        parts: list[tuple[str, str]] = [("activity 14d  ", darkside.MUT)]
        for c in counts:
            idx = min(len(bars) - 1, int(c / max_count * (len(bars) - 1)))
            # sparkline stays in the dim tier — never INK or ACCENT
            style = darkside.WORDMARK if idx < 4 else darkside.MUT
            parts.append((bars[idx], style))
        return darkside.Text.assemble(*parts)

    def on_mount(self) -> None:
        store: MapStore = self.app.store  # type: ignore[attr-defined]

        # The sala loads every map in the workspace, so one refusable map must
        # cost a notice rather than the screen.  Scoped to the sink: any
        # exception from a load, not only the types this batch knows about.
        broken: list[str] = []
        # `LLR-N13.1.5` identifies a damaged map by the load path RAISING or
        # RECORDING A LOAD WARNING.  Both land here, so the card state is
        # decided by one set rather than by whichever branch a reader happens
        # to be looking at.
        damaged: set[str] = set()

        def load_or_notice(name: str) -> Graph | None:
            try:
                graph = store.load(name)
            except Exception as exc:
                if name not in broken:
                    broken.append(name)
                    damaged.add(name)
                    self.notify(
                        f"could not load {darkside.plain(name)}: {darkside.plain(str(exc))}",
                        severity="error",
                        markup=False,
                    )
                return None
            if graph.load_warnings:
                # `A-102`: A LOAD WARNING IS A DAMAGED MAP TOO.  `LLR-N13.1.5`
                # names TWO conditions -- the load path RAISING or RECORDING A
                # LOAD WARNING -- and only the raise used to reach the card.
                # This path returned the graph and notified, so the card was
                # truthful while the WARNING was a TRANSIENT toast and the card
                # is PERMANENT: the moment the toast cleared there was no trace
                # at all.  That is half the distinguishability defect, and it is
                # the half that vanishes when the operator looks away.
                damaged.add(name)
                self.notify(
                    f"{darkside.plain(name)}: {darkside.plain('; '.join(graph.load_warnings))}",
                    severity="warning",
                    markup=False,
                )
            return graph

        # Identity row
        identity = self.query_one("#home-identity", Static)
        glyph, _ = darkside.moon(date.today())
        identity_text = Text()
        identity_text.append(glyph, style=darkside.WORDMARK)
        identity_text.append(" mapper", style=darkside.WORDMARK)
        # `A-112` st. 5: the view's one name, the legend title's (`D5`).
        identity_text.append(f"   {darkside.VIEW_NAMES['home']}", style=darkside.MUT)
        identity.update(identity_text)

        mmd_files = sorted(store.workspace.glob("*.mmd"))
        self.query_one(HintLine).set_hint(home_hint(bool(mmd_files)))
        hero_map: str | None = None
        hero_metrics: dict[str, int] | None = None

        # Prefer the last session map for the hero; fall back to most recent mmd.
        last_map, _ = store.last_session()
        if last_map:
            graph = load_or_notice(last_map)
            # `A-102` reaches here too: a map that LOADED but recorded a load
            # warning returns a graph, so `graph is not None` alone would hand
            # the hero to a damaged map.
            if graph is not None and last_map not in damaged:
                hero_map = last_map
                hero_metrics = self._map_metrics(graph)

        if hero_map is None and mmd_files:
            hero_map = mmd_files[0].stem
            graph = load_or_notice(hero_map)
            if graph is not None and hero_map not in damaged:
                hero_metrics = self._map_metrics(graph)
            else:
                # `INC7-CR-F2`: THE ALL-ZERO SUBSTITUTION WAS THE CARD'S LIE, ONE WIDGET
                # OVER.  A map the system could not READ was given a hero
                # showing `0 nodos` in `INK` -- the CALM tone -- and measured
                # BYTE-IDENTICAL to a healthy EMPTY map's hero.  The recents
                # loop was fixed and this was not, which is exactly what
                # `LLR-N13.1.5` means by naming the hero and resume branches in
                # its Touched symbols: the clause is about the SCREEN, not about
                # whichever widget the implementer happened to be looking at.
                #
                # THERE IS NO HONEST HERO FOR AN UNREADABLE MAP, so it does not
                # get one.  The card already declares the damage; a second
                # surface inventing metrics for it would be a second lie, and
                # `A-102`'s load-warning path would otherwise have the same map
                # declaring two different truths at once.
                hero_map = None
                hero_metrics = None

        hero_box = self.query_one("#home-hero-box", GroupBox)
        hero = self.query_one("#home-hero", Static)
        microbar = self.query_one("#home-microbar", Static)
        if hero_map and hero_metrics:
            hero.update(self._hero_text(hero_map, hero_metrics))
            microbar.update(self._microbar_text(hero_metrics))
            # Add the dim-tier sparkline beside the hero text inside the same box.
            spark = self._sparkline_text(store)
            hero.update(Text.assemble(
                self._hero_text(hero_map, hero_metrics), ("\n", ""), spark,
            ))
            hero_box.display = True
            microbar.display = True
        else:
            hero_box.display = False
            microbar.display = False

        # Resume row
        resume = self.query_one("#home-resume", Static)
        map_id, node_id = store.last_session()
        # `INC7-CR-F2`, the third surface: `retomar` invites the operator straight back
        # into a map the system could not read, naming a node it never loaded.
        # Same clause, same reason -- `LLR-N13.1.5` names this branch too.
        # `INC7-SEC-F1` again, and it is the SAME SHAPE the security pass named
        # one branch up: the first draft here split the load from the guard that
        # protects its use, so the two were safe only by sharing a condition
        # prefix.  One block, one condition, and the load is still performed for
        # every session map because its NOTICE is owed whether or not a resume
        # row is painted.
        resume_graph = load_or_notice(map_id) if (map_id and node_id) else None
        if map_id and node_id and map_id not in damaged and resume_graph is not None:
            node = resume_graph.nodes.get(node_id)
            node_name = node.ficha.title if node else node_id
            resume.update(
                Text.assemble(
                    (" ↩ resume ", f"bold {darkside.GROUND} on {darkside.ACCENT}"),
                    (" ", ""),
                    (escape(map_id), darkside.INK),
                    (" / ", darkside.MUT),
                    (escape(node_name), darkside.MUT),
                    ("   last session", darkside.MUT),
                )
            )
            self.query_one("#home-resume-box", GroupBox).display = True
        else:
            self.query_one("#home-resume-box", GroupBox).display = False

        # Recents table
        table = self.query_one("#home-recents", DataTable)
        # `INC9BC-UX-F13`: `clear()` keeps the columns, so each return to home
        # added the four again (24 after three returns).
        table.clear(columns=True)
        table.add_columns("▐ name", "kind", "nodes", "docs")

        archived = self.query_one("#home-archived", Static)
        if not mmd_files:
            table.display = False
            self.query_one("#home-empty", Static).update(self._empty_text())
            self.query_one("#home-empty", Static).display = True
            archived.display = False
            return

        table.display = True
        self.query_one("#home-empty", Static).display = False
        archived_count = 0  # placeholder until archive feature lands
        if archived_count:
            archived.update(
                Text.assemble((f"  ({archived_count} archived map — u restores)", darkside.MUT))
            )
            archived.display = True
        else:
            archived.display = False

        for mmd in mmd_files:
            map_name = mmd.stem
            graph = load_or_notice(map_name)
            # `INC7-SEC-F1`: guarded on `graph is None` DIRECTLY as well as on
            # the `damaged` set.  The two are coupled today -- `damaged.add`
            # sits under the same guard as `broken.append` and nothing else
            # writes either -- but NOTHING ENFORCES that coupling, and the
            # measured blast radius of it breaking is not one wrong card: an
            # `AttributeError` here PROPAGATES OUT OF `on_mount` AND KILLS THE
            # APP, which is the containment this whole clause exists to keep.
            if map_name in damaged or graph is None:
                # `LLR-N13.1.5` / `PRED-VIS`: A CARD THAT IS NOT A LIE.
                #
                # This branch used to substitute `concept, 0, 0`, which made a
                # broken map paint BYTE-IDENTICALLY to a healthy EMPTY one --
                # reproduced in the requirement itself, `roto` and `sano_vacio`
                # both painting `['', ' concept ', '0', '0']`.  The only thing
                # separating them was a TRANSIENT toast against a PERMANENT
                # card.
                #
                # THE GLYPH IS THE SIGNAL, NOT THE STRING.  The sala is SCANNED,
                # not read -- its whole purpose is choosing where to work
                # without opening anything -- and a card that differs only in
                # text differs only to someone already reading it.  `⊘` is
                # `01b` section 3.4's `V22`, drawn from the declared vocabulary
                # rather than invented here, which is what stops this painting
                # a bare `!` that no arm can see.
                # `INC7-CR-F1`: THE DECLARED CARD STATE, NOT A THIRD STRING.  This
                # first shipped ` ⊘ dañado `, which appears in neither `01b`
                # nor the LLR -- and that had a consequence beyond tidiness:
                # `#D28` escalates this seat from `MUT` to `INK` precisely
                # BECAUSE the copy INVITES AN ACTION (`↵ ver por qué`), so a
                # card carrying no invitation took the escalated style while
                # deleting its own justification.  `PRED-VIS` adds the glyph
                # limb ON TOP OF the string; shipping the glyph alone inverted
                # it.
                kind_cell = Text.assemble(
                    (f" {darkside.DAMAGED_MAP_GLYPH} {darkside.DAMAGED_MAP_STATE} ",
                     f"{darkside.INK} on {darkside.PANEL}"),
                )
                nodos = docs = "—"
            else:
                kind = "legacy" if graph.schema else "concept"
                kind_cell = Text.assemble(
                    (f" {kind} ", f"{darkside.INK} on {darkside.STEP}"),
                )
                nodos = str(len(graph.nodes))
                docs = str(len(graph.documents))
            table.add_row(
                escape(map_name),
                kind_cell,
                nodos,
                docs,
                key=map_name,
            )

    #: What each door does, in prose (Inc-EN's); the KEY and its NAME come from the seat.
    _DOOR_NOTES = {
        "c": "opens a recent map",
        "p": "connects a repository",
        "n": "creates a new map",
        "t": "start with preset fields",
        "i": "CSV / TSV of nodes",
        "f": "process documents",
    }

    def _empty_text(self) -> Text:
        """The door list: each door's key and name are the SEAT's (`INC9-UX-F4`)."""
        doors = [b for b in bindings_for(SCOPE_HOME)
                 if b.group == "doors" and b.key in self._DOOR_NOTES]
        width = max(len(b.label) for b in doors) + 1
        parts: list[tuple[str, str]] = []
        for b in doors:
            parts += [
                (b.glyph, darkside.ACCENT),
                (f" {b.label:<{width}}", darkside.INK),
                (self._DOOR_NOTES[b.key] + "\n", darkside.MUT),
            ]
        return Text.assemble(*parts)

    def action_consult(self) -> None:
        table = self.query_one("#home-recents", DataTable)
        if table.display:
            table.focus()

    def action_open_selected(self) -> None:
        """`↵` on home: open the map under the recents cursor, whatever has focus."""
        table = self.query_one("#home-recents", DataTable)
        if table.display and table.row_count:
            row = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
            self._open_map(str(row.value))

    def action_table_down(self) -> None:
        table = self.query_one("#home-recents", DataTable)
        if table.display and table.cursor_row is not None:
            table.action_cursor_down()

    def action_table_up(self) -> None:
        table = self.query_one("#home-recents", DataTable)
        if table.display and table.cursor_row is not None:
            table.action_cursor_up()

    def action_resume(self) -> None:
        store: MapStore = self.app.store  # type: ignore[attr-defined]
        map_id, node_id = store.last_session()
        if map_id and node_id:
            self.app.push_screen(MapScreen(map_id))

    def action_plug(self) -> None:
        self.app.push_screen(PlugRepoScreen())

    def action_factory(self) -> None:
        demo = Graph()
        demo.add_node(Node(id="root", ficha=Ficha(title="demo process")))
        demo.add_node(Node(id="n1", ficha=Ficha(title="step one")))
        demo.add_edge(Edge("root", "n1"))
        demo.documents["template"] = Document(name="template", source="hello {{name}}")
        self.app.push_screen(FactoryScreen(demo, process_name="demo"))

    def action_settings(self) -> None:
        self.app.push_screen(SettingsScreen())

    def _open_map(self, name: str | None) -> None:
        if not name:
            return
        self.app.push_screen(MapScreen(name))

    def action_construct(self) -> None:
        def on_name(name: str | None) -> None:
            if not name:
                return
            store: MapStore = self.app.store  # type: ignore[attr-defined]
            try:
                store.create_seed(name)
                self.app.push_screen(MapScreen(name))
            except Exception as e:
                if _refusal_toast(self, e):
                    return
                # `INC9-SEC-F1`: the map's name and the exception TYPE, never
                # `str(e)` -- an `OSError` embeds the absolute path (`_save_or_toast`).
                self.notify(
                    darkside.plain(f"could not create the map {name!r}: {type(e).__name__}"),
                    severity="error", markup=False)

        self.app.push_screen(ConstructScreen(), callback=on_name)

    def action_template(self) -> None:
        def on_pick(result: tuple[str, str] | None) -> None:
            if result is None:
                return
            name, template_id = result
            store: MapStore = self.app.store  # type: ignore[attr-defined]
            try:
                store.create_from_template(name, template_id)
                self.app.push_screen(MapScreen(name))
            except Exception as e:
                if _refusal_toast(self, e):
                    return
                self.notify(
                    darkside.plain(f"could not create the map {name!r}: {type(e).__name__}"),
                    severity="error", markup=False)

        def on_template(template_id: str | None) -> None:
            if template_id is None:
                return
            self.app.push_screen(
                _PromptScreen("map name", f"{template_id}-map"),
                callback=lambda name: on_pick((name, template_id)) if name else None,
            )

        if not TEMPLATES:
            self.notify("no templates available")
            return
        self.app.push_screen(_TemplateScreen(), callback=on_template)

    def action_import_csv(self) -> None:
        def on_path(path_str: str | None) -> None:
            if path_str is None:
                return
            path = safe_local_path(path_str)
            if path is None:
                # `INC9L-SEC-F2`: a text outside the allow-list is never looked at, and never named:
                # `~nosuchuser...` made `expanduser` raise and the traceback printed the typed text.
                # `U1`: it says what is accepted, in one fixed sentence.
                self.notify(darkside.plain(PATH_NOT_SUPPORTED), severity="error", markup=False)
                return
            if not path.is_file():
                # `INC9-SEC-F1`: the file's name, never the path the operator's
                # `~` expanded to.
                self.notify(darkside.plain(f"file not found: {path.name}"), severity="error", markup=False)
                return
            try:
                preview = preview_csv(path)
            except Exception as e:
                self.notify(
                    darkside.plain(f"could not read CSV {path.name!r}: {type(e).__name__}"),
                    severity="error", markup=False)
                return
            self.app.push_screen(_ImportPreviewScreen(preview, path))

        self.app.push_screen(
            _PromptScreen("CSV / TSV path", "C:\\path\\to\\nodes.csv"),
            callback=on_path,
        )

    def action_quit(self) -> None:
        self.app.exit()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        map_id = str(event.row_key.value)
        self.app.push_screen(MapScreen(map_id))

    def on_screen_resume(self) -> None:
        """Refresh the home surface when returning."""
        self.on_mount()


class _ImportPreviewScreen(Screen):
    """Preview a CSV import before saving it as a named map."""

    KEY_SCOPE = SCOPE_IMPORT
    BINDINGS = screen_bindings(SCOPE_IMPORT)

    def __init__(self, preview_graph: Graph, source_path: Path) -> None:
        super().__init__()
        self.preview_graph = preview_graph
        self.source_path = source_path

    def compose(self) -> ComposeResult:
        yield TabStrip("i", crumb=["import", self.source_path.name])
        yield Static("", id="import-preview-canvas")
        yield HintLine(f"{hint_pair(SCOPE_IMPORT, 'save')} · {hint_pair(SCOPE_IMPORT, 'home')}")
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    def on_mount(self) -> None:
        self.refresh_canvas()

    def refresh_canvas(self) -> None:
        canvas = self.query_one("#import-preview-canvas", Static)
        renderer = LayeredRenderer()
        size = self.size or self.app.size
        # Same sink class as MapScreen.refresh_canvas, and a live second door:
        # a CSV whose `parent` column is circular builds a cyclic graph without
        # ever passing through `mermaid.parse`, so the parser's refusal cannot
        # reach it.  Measured — see increment-001 §1.
        try:
            text = renderer.render(
                self.preview_graph,
                ViewState(
                    selected_id=self.preview_graph.root_id,
                    w=max(20, size.width),
                    h=max(5, size.height - 10),
                ),
            )
        except Exception as exc:
            text = darkside.Text.assemble(
                (" could not draw the preview\n\n", f"bold {darkside.INK}"),
                (f" {darkside.plain(str(exc))}", darkside.MUT),
            )
        canvas.update(text)
        pulse_cursor(canvas)

    def action_save(self) -> None:
        def on_name(name: str | None) -> None:
            if not name:
                return
            # `G6-C-F4`: the "guardar como" name is operator-typed and reaches
            # `store.save(name, ...)` as the map id, uncoerced until now.
            name = darkside.plain(name)
            store: MapStore = self.app.store  # type: ignore[attr-defined]
            if not _save_or_toast(self, store, name, self.preview_graph, new=True):
                return
            self.app.push_screen(MapScreen(name))

        self.app.push_screen(
            _PromptScreen("save as", self.source_path.stem),
            callback=on_name,
        )

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()


class PlugRepoScreen(Screen):
    """Input screen for plugging a GitHub repo."""

    KEY_SCOPE = SCOPE_PLUG
    # `K4`: the legend's title reads the SCREEN's name, not the scope id.
    legend_view = "connect repo"
    BINDINGS = screen_bindings(SCOPE_PLUG)

    def compose(self) -> ComposeResult:
        yield TabStrip("p", crumb=["connect repo"])
        yield Vertical(
            Label("connect repo", id="repo-title"),
            Input(placeholder="owner/name or github URL", id="repo-input"),
            id="repo-dialog",
        )
        yield HintLine("enter owner/name, a URL or a local path and press ↵", "↵")
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "repo-input":
            raw = event.value.strip()
            repo = self._normalize_repo(raw)
            if repo:
                self.app.push_screen(RepoScreen(repo))

    @staticmethod
    def _normalize_repo(value: str) -> str:
        """Accept owner/name, full GitHub URL, or local path."""
        value = value.strip().rstrip("/")
        if not value:
            return ""
        # Strip scheme and trailing .git from GitHub URLs.
        lowered = value.lower()
        if lowered.startswith("https://github.com/") or lowered.startswith("http://github.com/"):
            path = value.split("/", 3)[3]  # the check above is case-insensitive, so is this
            path = path.removesuffix(".git")
            return path  # owner/name
        if ":" in value and "git@github.com" in lowered:
            path = value.split(":", 1)[1]
            path = path.removesuffix(".git")
            return path
        return value

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()


class RepoScreen(Screen):
    """A GitHub repo rendered as a two-pane branch dashboard (variant C)."""

    KEY_SCOPE = SCOPE_REPO
    BINDINGS = screen_bindings(SCOPE_REPO)

    progress_current: reactive[int] = reactive(0)
    progress_total: reactive[int] = reactive(1)
    progress_stage: reactive[str] = reactive("")
    loading: reactive[bool] = reactive(True)

    def __init__(self, repo: str):
        super().__init__()
        self.repo = repo
        # `S1`: what is painted; `self.repo` stays as typed for the connector.
        self.shown = painted_repo(repo)
        self.graph = Graph()
        self.nav = NavigationModel(self.graph)
        self.selected_index = 0
        self.failure = ""
        self.stale = ""

    def compose(self) -> ComposeResult:
        yield TabStrip("p", crumb=[self.shown])
        with Horizontal(id="repo-dashboard"):
            with Vertical(id="repo-sidebar"):
                # `INC9F-SEC-F2`: typed text, painted as text: `Static(str)` parses markup.
                yield Static(Text(darkside.plain(self.shown)), id="repo-name")
                yield Static(self._stages_text(), id="repo-stages")
                yield Static(self._progress_text(), id="repo-progress")
                yield Static(self._sidebar_hints(), id="repo-sidebar-hints")
            yield Static(self._render_table(), id="repo-table", expand=True)
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    @staticmethod
    def _sidebar_hints() -> str:
        """The body panel's key hints, read from the seat (`K3`).  No `↵` line:
        this screen binds no enter and no handler answers it (`INC9C-F1`)."""
        pairs = [hint_pair(SCOPE_REPO, a) for a in ("next_sibling", "prev_sibling", "home")]
        return "\n".join([*pairs, hint_pair(SCOPE_APP, "help")])

    def _stages_text(self) -> Text:
        if self.failure:
            # `M2`: the toast expires; the panel is what stays.  The same fixed
            # sentence the toast carries, and the way out in the seat's word.
            return Text.assemble(
                ("▲ failed\n", darkside.INK),
                (self.failure + "\n", darkside.INK),
                (hint_pair(SCOPE_REPO, "home"), darkside.MUT),
            )
        stages = ["starting", "reading branches", "computing metrics", "ready"]
        if self.loading:
            current = min(2, int(3 * self.progress_current / max(1, self.progress_total)))
        else:
            current = 3
        text = Text()
        for i, stage in enumerate(stages):
            if i > 0:
                text.append("\n", "")
            if i < current:
                text.append(f"● {stage}", darkside.INK)
            elif i == current:
                marker = "◐" if self.loading else "●"
                text.append(f"{marker} {stage}", darkside.PULSE if self.loading else darkside.INK)
            else:
                text.append(f"○ {stage}", darkside.WORDMARK)
        if self.stale and not self.loading:
            # `P1`: the toast expires and `listo` would read as a fresh connect; the line
            # stays for as long as the cached copy is what the screen shows.
            # `INC9H-UX-F1`: the category goes on its own line, so the 30-cell sidebar never
            # breaks it (`unknown (exit` / `1)`).
            text.append("\n", "")
            text.append(darkside.plain(f"▲ cached copy:\n{self.stale}"), darkside.INK)
        return text

    def _progress_text(self) -> Text:
        if self.failure:
            return Text("")
        pct = min(100, int(100 * self.progress_current / max(1, self.progress_total)))
        width = 22
        filled = int(width * pct / 100)
        return Text.assemble(
            ("▰" * filled, darkside.INK),
            ("▱" * (width - filled), darkside.WORDMARK),
            (f" {pct}%", darkside.MUT),
        )

    def watch_progress_current(self) -> None:
        self._refresh_sidebar()

    def watch_progress_total(self) -> None:
        self._refresh_sidebar()

    def watch_loading(self) -> None:
        self._refresh_sidebar()

    def _refresh_sidebar(self) -> None:
        try:
            stages = self.query_one("#repo-stages", Static)
            progress = self.query_one("#repo-progress", Static)
        except Exception:
            return
        stages.update(self._stages_text())
        progress.update(self._progress_text())

    def _branch_kind(self, name: str) -> str:
        lowered = name.lower()
        if lowered in {"main", "master"} or lowered.startswith("release/"):
            return "release"
        if lowered.startswith("hotfix/"):
            return "hotfix"
        return "branch"

    def _state_indicator(self, state: str) -> Text:
        if state == "blocked":
            return Text.assemble(("● ", darkside.ALERT), ("blocked", darkside.ALERT))
        if state == "risk":
            return Text.assemble(("● ", darkside.WARN), ("risk", darkside.WARN))
        return Text.assemble(("● ", darkside.INK), ("ok", darkside.MUT))

    def _source_kind(self) -> str:
        # `INC9L-CR-F3`: the one decision `fetch` and `painted_repo` already read; a remote
        # (`gh` or a URL) keeps the `github` badge, and a refused text is not a remote.
        try:
            return "local" if github.source_kind(self.repo) == "local" else "github"
        except GitHubError:
            return "local"

    def _source_badge(self) -> Text:
        kind = self._source_kind()
        return darkside.Text.assemble(
            (f" {kind} ", f"{darkside.INK} on {darkside.STEP}"),
        )

    def _age_days(self, date_str: str) -> int:
        if not date_str:
            return -1
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            return (date.today() - dt).days
        except ValueError:
            return -1

    def _time_row(self, name: str, age_days: int, glyph: str, style: str, note: str) -> Text:
        return darkside.time_row(name, age_days, glyph, style, note)

    def _render_table(self) -> Text:
        if not self.graph.nodes:
            return Text("(no branches loaded)", style=darkside.MUT)

        root_id = self.graph.root_id or ""
        items: list[tuple[str, Node]] = []
        for nid, node in self.graph.nodes.items():
            if nid == root_id:
                continue
            items.append((nid, node))

        branches = [(nid, n) for nid, n in items if n.ficha.fields.get("kind") != "release"]
        releases = [(nid, n) for nid, n in items if n.ficha.fields.get("kind") == "release"]

        lines = Text()
        # Source honesty badge + counts
        lines.append("  ")
        lines.append_text(self._source_badge())
        lines.append(f"   {len(branches)} branches · {len(releases)} releases\n", darkside.MUT)
        lines.append("\n", "")

        def render_group(title: str, nodes: list[tuple[str, Node]], glyph: str,
                         style: str) -> None:
            if not nodes:
                return
            lines.append(f"  {title}\n", darkside.MUT)
            for idx, (nid, node) in enumerate(nodes):
                name = node.ficha.title or nid
                if name.startswith("release:"):
                    name = name[len("release:"):]
                age = self._age_days(node.ficha.fields.get("date", ""))
                note_parts: list[str] = []
                if age >= 0:
                    if age == 0:
                        note_parts.append("today")
                    elif age == 1:
                        note_parts.append("yesterday")
                    elif age < 7:
                        note_parts.append(f"{age} d ago")
                    elif age < 30:
                        note_parts.append(f"{age // 7} wk ago")
                    else:
                        note_parts.append(f"{age // 30} mo ago")
                meta = node.ficha.meta or ""
                if meta and meta != "release":
                    note_parts.append(meta)
                if node.ficha.notes and node.ficha.notes != "CI: unknown":
                    note_parts.append(node.ficha.notes)
                note = " · ".join(note_parts) or "no data"
                row = self._time_row(name, max(0, age), glyph, style, note)
                # selection marker
                marker = "▶ " if idx == self.selected_index else "  "
                lines.append(marker, darkside.ACCENT if idx == self.selected_index else "")
                lines.append_text(row)
                lines.append("\n", "")
            lines.append("\n", "")

        order = {"release": 0, "hotfix": 1, "branch": 2}
        branches.sort(key=lambda item: (order.get(self._branch_kind(item[0]), 2), item[0]))
        render_group("branches", branches, "●", darkside.INK)
        render_group("releases", releases, "◆", darkside.INK)

        lines.append("  ")
        lines.append("●", darkside.INK)
        lines.append(" commit   ", darkside.MUT)
        lines.append("◆", darkside.INK)
        lines.append(" release   ", darkside.MUT)
        lines.append("╎", darkside.WORDMARK)
        lines.append(" today   (30 days)\n", darkside.MUT)
        return lines

    def _refresh_table(self) -> None:
        table = self.query_one("#repo-table", Static)
        table.update(self._render_table())

    @work(thread=True, exit_on_error=False)
    def fetch_graph(self) -> Graph:
        def on_progress(current: int, total: int, stage: str) -> None:
            try:
                self.app.call_from_thread(self._update_progress, current, total, stage)
            except Exception:
                pass
        connector = GitHubConnector(self.repo)
        graph = connector.fetch(progress=on_progress)
        self.stale = connector.stale
        return graph

    def _update_progress(self, current: int, total: int, stage: str) -> None:
        try:
            self.progress_current = current
            self.progress_total = total
            self.progress_stage = stage
        except Exception:
            pass

    async def on_mount(self) -> None:
        self.loading = True
        self._refresh_sidebar()
        table = self.query_one("#repo-table", Static)
        table.update(Text("  connecting… this may take a few seconds", style=darkside.MUT))
        try:
            worker = self.fetch_graph()
            self.graph = await worker.wait()
            count = len(self.graph.nodes)
            if self.stale:
                # `INC9F-CR-F4`: the refresh failed; what is painted is the cached copy.
                # `P2`: this is the ONE toast of a stale connect (`conectado` would
                # contradict it); `P1` pairs it with the panel line.  The way back is the seat's.
                self.notify(
                    darkside.plain(
                        f"showing the cached copy ({count} nodes): {self.stale} · "
                        f"{hint_pair(SCOPE_REPO, 'home')} to retry"),
                    severity="warning", markup=False)
            else:
                self.notify(darkside.plain(f"connected: {count} nodes"), markup=False)
        except Exception as exc:
            # `INC9BC-SEC-F3`: the worker does not exit the app (`exit_on_error`),
            # so its failure arrives here wrapped, and `GitHubError` is reachable.
            if isinstance(exc, WorkerFailed):
                exc = exc.error
            if isinstance(exc, GitHubError):
                self.failure = darkside.plain(str(exc))
            else:
                self.failure = darkside.plain(f"unexpected error: {type(exc).__name__}")
            self.notify(darkside.plain(self.failure), severity="error", markup=False)
            self.graph = Graph()
        self.loading = False
        self.nav = NavigationModel(self.graph)
        self.selected_index = 0
        self._refresh_sidebar()
        self._refresh_table()
        pulse_cursor(table)

    def action_next_sibling(self) -> None:
        root_id = self.graph.root_id or ""
        count = sum(1 for n in self.graph.nodes if n != root_id)
        if count == 0:
            return
        self.selected_index = (self.selected_index + 1) % count
        self._refresh_table()

    def action_prev_sibling(self) -> None:
        root_id = self.graph.root_id or ""
        count = sum(1 for n in self.graph.nodes if n != root_id)
        if count == 0:
            return
        self.selected_index = (self.selected_index - 1) % count
        self._refresh_table()

    def action_home(self) -> None:
        self.app.pop_screen()

    def action_palette(self) -> None:
        self.app.action_palette()


class MapScreen(Screen):
    """A map rendered as a layered tree."""

    KEY_SCOPE = SCOPE_MAP
    BINDINGS = screen_bindings(SCOPE_MAP)
    # The inspector's fields mount after this screen does, and Textual would
    # auto-focus the first of them — which silently disables every single-letter
    # map binding, because a focused Input consumes printable keys.  The map, not
    # a text field, owns the keyboard on arrival.
    AUTO_FOCUS = None

    def __init__(self, map_id: str, source_crumb: list[str] | None = None) -> None:
        super().__init__()
        self.map_id = map_id
        self.source_crumb = source_crumb
        self.store: MapStore | None = None
        self.graph: Graph = Graph()
        self.base_graph: Graph = Graph()
        self.nav: NavigationModel = NavigationModel(self.graph)
        self.renderer = LayeredRenderer()
        self.outline_renderer = OutlineRenderer()
        self.radial_renderer = RadialRenderer()
        self.query_text = ""
        self.focus_active = False
        self.outline_mode = False
        self.radial_mode = False
        self.diff_active = False
        self.diff: DiffResult | None = None
        self.rail_hidden = False
        self.inspector_hidden = False
        self._regions_pinned = False
        # US-N06.  The screen owns fold and pan; the rail and the renderer are
        # readers.  `folded` lived on `OutlineRail` until Inc-3, where a region
        # the layout auto-hides below 118 columns owned state the canvas needed.
        self.folded: frozenset[str] = frozenset()
        self.pan_x = 0
        self.pan_y = 0
        # The pan the operator had when a docked legend moved the view, kept
        # until the legend closes (`legend_docked`, Inc-8 verdict `F2`).
        self._pan_before_legend: tuple[int, int] | None = None
        # The focused widget's id (or `None`) at that same moment -- captured
        # alongside the pan, restored alongside it (`INC8-P3-CR-F1`).  Valid
        # only while `_pan_before_legend` is not `None`; the two are set and
        # cleared together.
        self._focus_before_legend: str | None = None
        # Set by `legend_closed`, consumed by `on_screen_resume`: the pan and
        # focus to restore once THIS screen is active again.  Restoring from
        # `legend_closed` itself is too early -- it runs before the legend's
        # own `dismiss()` even pops this screen back on, and Textual's own
        # `AUTO_FOCUS` grabs the rail during that pop whenever nothing is
        # focused (`INC8-P3-CR-F1`, carried `UX-F7`).  `on_screen_resume`
        # answers the same `ScreenResume` that auto-focus does.
        self._legend_restore_pending: tuple[int, int, str | None] | None = None
        # The canvas region `_declare_after_layout` last painted a numeral for.
        # `None` means "never", which is why the first pass always re-schedules.
        self._declared_for: Region | None = None
        # EVERYTHING the canvas's current content was produced FROM: the
        # renderer and the whole `ViewState`.  `P1` says content and geometry
        # agree at rest, and the settle pass may skip a re-render it knows would
        # be byte-identical.  Measured: without that skip, one settle pass on an
        # 11999-node graph in outline costs 0.33 s at 118x34 -- a full re-render
        # -- and doubles a repaint that already costs 0.36 s.
        #
        # THIS HELD ONLY `(w, h)` AND THAT WAS A DEFECT THE SECURITY REVIEW
        # FIRED.  Content is a function of the renderer plus NINE `ViewState`
        # fields; geometry is two of them.  A guard keyed on two inputs is a
        # PROJECTION of `P1`, not `P1`, so any other input changing without an
        # intervening `refresh_canvas` let the settle declare the frame
        # reconciled and skip -- while the strip repainted from the new state
        # against a canvas holding the old one.  Demonstrated: the canvas header
        # declaring 7 in layered beside a strip declaring 5 in outline, at one
        # unchanged geometry.  That is `B-60` reintroduced through the mechanism
        # built to prevent it.
        #
        # `ViewState` is a frozen dataclass, so `==` is total over its fields and
        # costs O(fields) -- it cannot give back the 0.33 s the skip exists to
        # save.  Now the predicate really is the invariant rather than a shadow
        # of it, which is what the comment below already claimed.
        self._rendered_for: tuple[object, ViewState] | None = None
        # ONE FRAME'S resolution, held only for the duration of that frame.
        # See `_search_order`; `_open_paint_pass` is what bounds its lifetime.
        self._search_memo: tuple[Graph, str, tuple[str, ...]] | None = None
        # `#D5b` took `n` from `next_gap` and gave it to the walk, and the
        # relocated chord is undiscoverable through `?` until Inc-8.  The first
        # `n` press on this screen says so.  Per SCREEN and not per process:
        # a process-wide flag is class state shared by every map the operator
        # opens and by every test in a run, and the acceptance reads the frame
        # twice rather than reading this field.
        self._rebind_declared = False
        # US-001 (LLR-003.2): set while a draft guard this screen pushed is up,
        # so a second exit never stacks a second guard.
        self._draft_guard_open = False

    def compose(self) -> ComposeResult:
        crumb_prefix = self.source_crumb or [self.map_id]
        yield TabStrip("c", crumb=crumb_prefix + [""])
        yield Static("", id="map-minimap")
        # Variant A «taller»: rail | canvas | inspector.  The inspector is the ONE
        # ficha surface — it replaces both the old `#map-ficha` GroupBox and the
        # LayeredRenderer's own ficha strip, which rendered the same card twice.
        yield Horizontal(
            OutlineRail(id="map-rail"),
            Static("", id="map-canvas"),
            FichaInspector(id="map-inspector"),
            id="map-body",
        )
        yield Input(placeholder="/search", id="search-input")
        yield Static("", id=COUNT_REGION_ID)
        yield Static("", id="map-toast")
        yield MapHintLine(map_hint())
        # The keybar reads the same seat the bindings are generated from, so it
        # cannot advertise a key the screen does not bind (US-N03).
        yield KeyBar(groups_for_keybar(keybar_groups(self.KEY_SCOPE)))

    def _notice_load_warnings(self, graph: Graph) -> None:
        """Tell the operator which node and which field were unreadable.

        LLR-R03.4.  The map still loaded (LLR-R03.5), so this is a notice and not
        an error path; `darkside.plain` because the node id and the key both come
        out of a file.
        """
        if not graph.load_warnings:
            return
        self.notify(
            darkside.plain("; ".join(graph.load_warnings)),
            severity="warning",
            markup=False,
        )

    def _establish_graph(self, graph: Graph, *, cursor: str | None) -> None:
        """Make *graph* the screen's map: the ONE load path (design 1b.9).

        `on_mount` and a failed save's reload both come through here, so the
        reload re-establishes the view exactly as opening the map does
        (LLR-004.2): the whole map, focus cleared (a focused view is a subgraph),
        load warnings surfaced, a fresh navigation, the cursor kept if its node
        still exists and the root otherwise.
        """
        self.base_graph = self.graph = graph
        self.focus_active = False
        self._notice_load_warnings(graph)
        self.nav = NavigationModel(graph)
        self.nav.cursor = cursor if cursor in graph.nodes else graph.root_id

    def on_mount(self) -> None:
        self.store = self.app.store  # type: ignore[attr-defined]
        search = self.query_one("#search-input", Input)
        search.display = False
        search.disabled = True
        self.focus()

        try:
            self._establish_graph(self.store.load(self.map_id), cursor=None)
        except Exception as e:
            error_graph = Graph()
            error_graph.add_node(Node(id="root", ficha=Ficha(title="error")))
            self._establish_graph(error_graph, cursor=None)
            self.notify(
                f"error loading map: {darkside.plain(str(e))}",
                severity="error",
                markup=False,
            )

        # Resume cursor from last session if it points into this map.
        if self.store is not None:
            last_map, last_node = self.store.last_session()
            if last_map == self.map_id and last_node in self.graph.nodes:
                self.nav.cursor = last_node
            self.store.record_session(self.map_id, self.nav.cursor)

        self._apply_region_visibility()
        self.refresh_canvas()
        # Keep focus off the side regions on arrival: a focused Input eats every
        # single-letter key, so the map's own navigation would be dead until the
        # operator blurred it by hand.  Scheduled after the refresh because the
        # rail and the inspector's fields are focusable and mount after this runs.
        self.call_after_refresh(self._park_focus)
        # `B-56` AND `B-60`, both CLOSED rather than carried.  The carry they
        # replace was recorded on measurements that were wrong twice over: the
        # declaration was ABSENT at ordinary sizes rather than merely stale, and
        # ordinary navigation did not clear it.  See `_declare_after_layout`,
        # which repaints the two surfaces that DECLARE -- the canvas and the
        # strip -- and nothing that focuses, so `LLR-CNV.3.1` and `B-50` are
        # untouched.
        self.call_after_refresh(self._declare_after_layout)

    # -- region layout (LLR-N06.6) -----------------------------------------
    # Below this width the canvas cannot show a card's coverage row without
    # clipping it mid-field, and a clipped field is indistinguishable from a
    # present one — the canvas would silently misreport coverage.  Measured by
    # the UX lens: a 5-field schema needs card_w >= 15, so n*18-3 <= w-2.
    MIN_CANVAS_WIDTH = 58

    def _chrome_width(self) -> int:
        """Columns taken by the rail and inspector at the current setting."""
        return (0 if self.rail_hidden else RAIL_WIDTH) + (
            0 if self.inspector_hidden else INSPECTOR_WIDTH
        )

    def _apply_region_visibility(self) -> None:
        """Collapse the side regions when the terminal cannot afford them.

        Auto-collapse is width-driven, but an explicit toggle wins: once the
        operator has hidden or shown a region by hand, we stop second-guessing.
        """
        size = self.size or self.app.size
        if not self._regions_pinned:
            available = size.width - RAIL_WIDTH - INSPECTOR_WIDTH
            if available < self.MIN_CANVAS_WIDTH:
                self.rail_hidden = True
            if size.width - INSPECTOR_WIDTH < self.MIN_CANVAS_WIDTH:
                self.inspector_hidden = True
        self.query_one("#map-rail", OutlineRail).display = not self.rail_hidden
        self.query_one("#map-inspector", FichaInspector).display = not self.inspector_hidden

    def action_toggle_rail(self) -> None:
        self._regions_pinned = True
        self.rail_hidden = not self.rail_hidden
        self._apply_region_visibility()
        self._clear_pan_hint()
        self.refresh_canvas()

    def action_toggle_inspector(self) -> None:
        self._regions_pinned = True
        self.inspector_hidden = not self.inspector_hidden
        self._apply_region_visibility()
        self.refresh_canvas()

    def action_focus_rail(self) -> None:
        """Move keyboard focus to the rail, and say so on the hint line."""
        rail = self.query_one("#map-rail", OutlineRail)
        if self.rail_hidden:
            self.action_toggle_rail()
        rail.focus()
        self.query_one(HintLine).set_hint(
            f"rail · ↵ {label_for(SCOPE_MAP, 'collapse_branch')} · "
            f"esc {label_for(SCOPE_MAP, 'back_or_home')}", "esc"
        )
        self.refresh_canvas()

    def action_collapse_branch(self) -> None:
        """Fold or unfold the branch under the cursor — LLR-N06.2.1, LLR-N06.2.2.

        The rail used to own this and mutate its own `collapsed` set, so the
        canvas never learned about a fold at all.
        """
        nid = self.nav.cursor
        if nid is None:
            return
        if nid not in self.folded and not self.graph.children_of(nid):
            # LLR-N06.2.2.  The natural implementation paints a pill reading
            # `+0`, which declares a hidden count of zero and is worse than
            # nothing; the product already answers "nothing to do" out loud
            # elsewhere (`next_gap` toasts `cobertura completa`).
            self.notify(
                "this node has no descendants",
                title="nothing to fold",
                severity="information",
                markup=False,
            )
            return
        self.folded = (
            self.folded - {nid} if nid in self.folded else self.folded | {nid}
        )
        self.refresh_canvas()

    # -- pan (HLR-N06.1) ---------------------------------------------------
    # One press moves the window by this many cells.  A single cell makes the
    # chord feel dead on a map that overflows by 60 columns; a whole viewport
    # loses the operator's place.  Vertical is smaller because a card row is
    # 4-5 cells tall and a page-sized jump skips whole levels.
    PAN_STEP_X = 8
    PAN_STEP_Y = 4

    @staticmethod
    def _clamp_pan(offset: int, extent: int, span: int) -> int:
        """LLR-N06.1.2 — the legal range is `[0, max(0, E - W)]`, always.

        The `E < W` case is why the outer `max(0, ...)` is there rather than a
        bare `extent - span`: a map smaller than the canvas has a legal pan
        range of exactly one position, and a negative upper bound would let
        `min` return it and slide the map off screen on a small graph.
        """
        return max(0, min(offset, max(0, extent - span)))

    # `HEADER_ROWS = 2` USED TO LIVE HERE, AND IT WAS FALSE.  The note argued
    # the header's length is always `avail + 5` or `2 * avail - 43`, hence
    # always between `avail` and `2 * avail`, hence exactly two physical rows.
    # Both of its paddings are CLAMPED AT 0, so below `avail = 48` neither
    # formula applies: the line is a fixed core plus the `▽ N fuera de vista`
    # declaration, and on `legacy` that is 55 cells at EVERY narrow width.
    # Measured, it wraps to THREE physical rows at canvas width 21..34 and FOUR
    # at 20 -- and `_canvas_size` floors `w` at 20, so the band is one resize
    # away.  Charging 2 there left the screen believing one or two more body
    # rows survived than the region could show, and `painted_ids` declared nodes
    # that leave no trace: at terminal (28,17) it declared `erp` on a frame with
    # zero card marks while the strip read 7 against a truth of 8.  That is
    # `CR-F1`'s defect verbatim, one width band over (`B-61`).
    #
    # The number is now MEASURED per call by `layered.header_rows`, off the same
    # `_header_line` helper `render` paints from, so there is no second copy of
    # the header's shape to drift.

    def _header_rows(self, wrap_w: int) -> int:
        """The header's measured physical height for the frame about to be sized.

        WRAPPED AT THE WIDGET'S CONTENT WIDTH, WHICH IS NOT `w - 2`.  An earlier
        revision wrapped at `w - 2` and justified it as "the canvas widget's
        content width".  Measured across a 943-configuration terminal sweep on
        `legacy`, it is not: `#map-canvas` is `width: 1fr; height: 100%` with no
        padding and no border, so its content width equals its REGION width, and
        that region is `_canvas_width()` at 724 of the 943 and `_canvas_width()
        - 2` at the other 219.  At terminal (28,17) the content width is 28, not
        26, and the frame shows three rows because Rich WORD-WRAPS a 55-cell
        line at 28 -- not because of a two-column inset.  The old reading reached
        the right row count through the wrong mechanism, which is why it was
        compensating rather than causing.  So the measured width is passed in.

        `wrap_w` comes from the same `content_size` read `_canvas_size` uses to
        price the body, so the guard and the subtraction cannot disagree about
        which frame they are describing.

        THE CHARGE IS PER RENDERER, AND IT USED TO BE LAYERED'S IN EVERY VIEW.
        `_canvas_size` has no renderer branch while `refresh_canvas` picks the
        renderer separately, so outline and radial were priced with layered's
        header.  MEASURED over a ten-width sweep from 20 to 118, with layered's
        own first line as the positive control -- `layered.header_rows` agrees
        with it at ALL TEN widths, which is what makes the other two columns a
        finding rather than instrument error:

            w    charged   layered   outline   radial
            20      3         3         1        3
            24      3         3         1        2
            28      3         3         1        2
            34      2         2         1        2
            40      2         2         1        2
            50+     2         2         1        1

        Outline is overcharged at EVERY width in the sweep; each overcharged row
        is a body row the region could have shown and the renderer was never
        told about.
        THE DISPATCH IS STRICT AND THIS CALL SITE IS NOT, AND THE ASYMMETRY IS
        DELIBERATE.  `_painted_ids_for` raises for an unregistered renderer and
        lets that raise escape, because `frozenset()` is a legitimate declaration
        and a BROKEN one must not present as an ABSENT one.  I copied that shape
        here and it was wrong: the CONSEQUENCE does not transfer.  A declaration
        that raises costs a numeral; a CHARGE that raises means the canvas cannot
        be sized at all, and `_canvas_size` runs BEFORE `refresh_canvas`'s guard,
        so the raise escaped the one path `LLR-R01.4` ratifies as survive-
        anything.

        FIRED, AND IT IS WHAT CAUGHT THIS.  `TC-R08` installs a renderer that is
        not one of the three and asserts the app still paints "no se pudo dibujar
        el mapa" rather than dying; both of its parameter cases failed against the
        strict version.  So strictness stays where it can be ACTED on -- the
        dispatch, pinned by its own arm -- and the drawing path DEGRADES to
        layered's charge, which is a wrong row budget on a frame that is about to
        paint a failure notice anyway.
        """
        try:
            charge = self._header_rows_for(self._current_renderer())
        except LookupError:
            charge = header_rows
        return charge(self.graph, self._canvas_width(), wrap_w)

    def _header_rows_for(self, renderer):
        """The function this renderer's header charge comes from.

        IDENTITY, NEVER `getattr`, matching `_painted_ids_for` and for the same
        reason (`A-98`, ruling `02j`): a probe answers "this view has no header"
        and "this view's charge is broken" with the same silence.

        THE RADIAL RESIDUE IS CLOSED (`S-D`).  Until this stage radial was an
        EXPLICIT fallback to `layered.header_rows` -- stated here and pinned by
        an arm so the fix would redden the arm rather than close the hole
        silently, which is this batch's `AT-058` doctrine applied to a CHARGE.
        The residue was real and it was measured, not suspected: on the arm's own
        fixture, layered's charge EXCEEDED radial's own first line at SEVEN of
        the ten swept widths -- 24, 28, and every width from 50 up -- and each
        overcharged row is a body row the region could have shown and the
        renderer was never told about.  `radial.header_rows` now equals radial's
        own first line at TEN of ten, which is the equality form the other two
        entries hold to.

        An unregistered renderer RAISES.  A future view that genuinely has no
        header gets an explicit entry returning a charge of one, exactly as
        `outline` and `radial` got explicit entries in `_painted_ids_for`.
        """
        if renderer is self.renderer:
            return header_rows
        if renderer is self.outline_renderer:
            return outline_header_rows
        if renderer is self.radial_renderer:
            return radial_header_rows
        raise LookupError(f"no header charge registered for {renderer!r}")

    def _canvas_width(self) -> int:
        """Columns the canvas renderer is given.  Floors at 20 (`B-61`'s band)."""
        size = self.size or self.app.size
        # The canvas no longer owns the full width: the inspector takes a fixed
        # column beside it, so render to what is actually left.
        return max(20, size.width - self._chrome_width())

    def _canvas_size(self) -> tuple[int, int]:
        """The `(w, h)` the canvas renderer is given, in ONE place.

        `refresh_canvas`, the pan clamp and the overflow helper must all price
        the same frame; three inline copies of this arithmetic is how they start
        disagreeing about which nodes were on screen.

        `h` COMES FROM THE WIDGET'S REGION, not from `size.height - 8`, and that
        is a defect fix US-N06 forced into the open.  Measured on `legacy`: at a
        50x20 terminal the shipped arithmetic asked for 12 rows into a region
        that holds 8, so four nodes were drawn into a void -- hidden, with
        nothing declaring them, which is the story's promise inverted.  Across a
        nine-size sweep the shipped `h` made the declared painted set disagree
        with the composited frame at five sizes; the region-derived `h` agrees at
        all nine.

        THE THREE BRANCHES ARE THREE DIFFERENT FRAMES, and an earlier revision
        collapsed the middle one into the last.  `region.height == 0` is the
        genuinely pre-layout case, and only there is `size.height - 8` an honest
        guess.  A region that is REAL but no taller than the header is not
        pre-layout at all -- it is a short terminal, and the header has eaten the
        whole region.  Returning `region.height` there left `row_limit = h - 1`
        believing canvas row 0 survived, so `painted_ids` declared a node painted
        that leaves no trace: measured on `legacy` at (31,18), (50,14) and
        (100,10), all 8 nodes hidden and the indicator declaring 7.  Returning 1
        makes `row_limit` 0, which is the truth -- no body row is paintable.

        BOTH USES OF THE HEADER'S HEIGHT TAKE THE MEASURED VALUE, and they have
        to move together: the guard asks "has the header eaten the whole
        region", the subtraction asks "how many body rows are left".  Charging a
        constant 2 in either place is `B-61`.  `render` emits `1 + (h - 1)`
        LOGICAL lines and the widget spends `rows` PHYSICAL rows on the first of
        them, so the frame shows `region.height - rows` body rows and the
        renderer must be told `h - 1 = region.height - rows`.
        """
        w = self._canvas_width()
        canvas = self.query_one("#map-canvas", Static)
        region = canvas.region
        if not region.height:                    # genuinely pre-layout
            size = self.size or self.app.size
            return w, max(5, size.height - 8)
        # The header is priced AFTER the region is known to be real, because the
        # width it wraps at is that region's content width -- there is no honest
        # value for it above this line.
        rows = self._header_rows(canvas.content_size.width or region.width)
        if region.height <= rows:                # real, but the header fills it
            return w, 1                          # row_limit == 0 -> nothing painted
        return w, region.height - (rows - 1)

    def _consumes_pan(self, renderer) -> bool:
        """Does THIS renderer read the pan offsets it would be given?

        IDENTITY, NEVER `getattr`, matching `_header_rows_for` and
        `_painted_ids_for` for the same reason (`A-98`, ruling `02j`): a probe
        must not answer "this view has no pan" and "this view's pan is broken"
        with the same silence.

        MEASURED, NOT INFERRED (`PAN-1`).  `views/outline.py` and
        `views/radial.py` hold ZERO code references to `pan_x`/`pan_y` -- the one
        textual match in outline is prose inside a docstring -- while
        `views/layered.py` consumes both.  Driven end to end with pan set
        DIRECTLY, so no keypress side effect could be mistaken for the thing:
        layered's picture moves, outline's and radial's never do, at any size.

        AND THE MANIFESTATION WAS WORSE THAN A WRONG NUMBER.  The screen computed
        a LAYERED extent for every view and clamped `pan_x`/`pan_y` against it,
        so in the two views that ignore pan the operator's keys moved nothing
        while internal state advanced -- the app held a pan the picture never
        reflected.  A lying affordance of the MOTION kind, the same family as the
        `esc` rulings `#D38`/`#D43`: an affordance that teaches a rule which
        silently stops holding.

        RADIAL DOES NOT WANT PAN, and that is a ruling rather than an omission
        (coordinator 2026-09-18).  Its navigation is focus-based and its layout
        is polar around the selected node, so a viewport is a category error
        rather than a missing feature.  The fix is therefore NOT "give radial
        pan" but "stop advertising and advancing pan on behalf of a view that
        does not consume it".  Reversible if a later measurement shows radial
        genuinely wants a viewport.

        EVERY RENDERER IS ENUMERATED AND AN UNREGISTERED ONE RAISES, exactly as
        `_header_rows_for` and `_painted_ids_for` do.  The first version of this
        method fell through to `False`, which is the defect its own citation of
        `02j` forbids: a fourth renderer added tomorrow would be SILENTLY
        classified as non-panning, with nothing anywhere saying so.  `False` is
        a LEGITIMATE answer here, which is exactly why it may not double as the
        answer for "I have never heard of this renderer".

        THE RAISE IS UNGUARDED ON THE PAN PATH, AND THAT IS A DECISION RATHER
        THAN AN ACCIDENT.  Of the three dispatches this one alone is called from
        `_pan` BEFORE its `try`, so an unregistered renderer plus one pan
        keypress would escape into the message pump -- the sink that `except`
        exists for.  The sibling `_header_rows_for` MEASURED ITS WAY TO THE
        OPPOSITE ANSWER and softens its raise in the drawing path, on the
        argument that "a declaration that raises costs a numeral; a charge that
        raises costs the whole picture".  That argument does not transfer: a
        charge is needed to paint EVERY frame, so degrading keeps the map on
        screen, whereas pan consumption is consulted only when the operator
        presses a pan key -- and degrading it would silently reinstate exactly
        the defect this raise was added to remove.  A view whose pan class is
        unknown must not be guessed at on the operator's behalf.

        WHAT THAT COSTS, stated here rather than discovered later: if a fourth
        renderer is ever constructed without an entry here, the first pan press
        takes the app down.  That is a code defect failing loudly the moment it
        is first exercised, which is this batch's stated preference, and it is
        unreachable in a shipped build -- `app.py` constructs exactly three
        renderers and an arm pins that an unregistered one raises.
        """
        if renderer is self.renderer:
            return True
        if renderer is self.outline_renderer or renderer is self.radial_renderer:
            # RULED, not absent: focus-based / polar navigation (2026-09-18).
            return False
        raise LookupError(f"no pan consumption registered for {renderer!r}")

    def _reclamp_pan(self, w: int, h: int) -> None:
        """Pull both offsets back into range for the frame about to be drawn.

        A resize or a fold shrinks the extent under a pan that was legal a
        moment ago, and `LLR-N06.1.2` says the system shall not ACCEPT an offset
        outside the range -- not merely that it shall not produce one.

        A VIEW THAT DOES NOT CONSUME PAN DECLINES TO CLAMP, and HOLDS the
        offsets (`PAN-1`).  Clamping against `layered`'s extent here would be the
        same renderer-independent application of a layered-specific helper that
        defect 2 was, one seam over -- so the branch exists.  But declining to
        clamp is the whole of what it needs to do.

        IT MUST NOT ZERO THEM, AND THE FIRST VERSION OF THIS BRANCH DID.
        `refresh_canvas` calls this on every repaint, so zeroing here threw the
        operator's pan away on a mere excursion into outline or radial -- no key
        pressed, nothing declared, offsets gone, measured `(48, 0)` -> `(0, 0)`
        on a round trip.  That is the SAME FAMILY this increment exists to
        close, one seam over: `PAN-1`'s charge is "the app held a pan the
        picture never reflected", and zeroing shipped "the app discarded a pan
        the operator set, without saying so".  The non-consumer ignores the
        offsets while it is on screen, and this method clamps them honestly on
        the way back.
        """
        if not self._consumes_pan(self._current_renderer()):
            return
        (extent_x, span_x), (extent_y, span_y) = pan_extent(
            self.graph, self._view_state(w, h)
        )
        self.pan_x = self._clamp_pan(self.pan_x, extent_x, span_x)
        self.pan_y = self._clamp_pan(self.pan_y, extent_y, span_y)

    def _pan(self, dx: int, dy: int) -> None:
        # INERT AND DECLARED, never inert and silent (`PAN-1`, ruling 2026-09-18).
        # Before this, a pan key in outline or radial advanced `pan_x`/`pan_y`
        # against a LAYERED extent and repainted a picture that consumes
        # neither, so the operator got no movement, no message, and a hidden
        # offset that outlived the view.  Saying so is the whole fix: a key that
        # does nothing and explains why is an honest affordance; one that does
        # nothing quietly is indistinguishable from a broken keyboard, which is
        # the confusion `US-N06` exists to remove.
        if not self._consumes_pan(self._current_renderer()):
            self.query_one(HintLine).set_hint(PAN_INERT_HINT)
            return
        w, h = self._canvas_size()
        try:
            (extent_x, span_x), (extent_y, span_y) = pan_extent(
                self.graph, self._view_state(w, h)
            )
        except Exception:
            # Same argument as `refresh_canvas`'s guard, and the same sink-scoped
            # shape: this runs inside the message pump, `_tree_layout` raises by
            # design on a graph that is not a tree, and an escape here kills the
            # app with the operator's unsaved edits in it.  Measured on a cyclic
            # graph before this guard: one `L` press and `app.is_running` went
            # False.  A frame that cannot be laid out cannot be panned, so the
            # answer is the one the edge already has a declaration for.
            self.query_one(HintLine).set_hint(PAN_EDGE_HINT)
            return
        nx = self._clamp_pan(self.pan_x + dx * self.PAN_STEP_X, extent_x, span_x)
        ny = self._clamp_pan(self.pan_y + dy * self.PAN_STEP_Y, extent_y, span_y)
        if (nx, ny) == (self.pan_x, self.pan_y):
            # HLR-N06.1's unwanted-behaviour clause.  A silent no-op at the edge
            # is indistinguishable from a keyboard that stopped working, and
            # blank space past the content is indistinguishable from "the map
            # has nothing there" -- the exact confusion US-N06 exists to remove.
            self.query_one(HintLine).set_hint(PAN_EDGE_HINT)
            return
        self.pan_x, self.pan_y = nx, ny
        # CLEARED ON SUCCESS, and the omission was a real misdescription rather
        # than untidiness: the hint is set on a no-op and nothing ever unset it,
        # so on the shipped maps -- where `H`/`L` are no-ops at every width but
        # one -- it latched on the first sideways press and then sat there
        # describing every LIVE `J`/`K` as an edge the operator had not reached.
        self.query_one(HintLine).set_hint(self._resting_hint())
        self.refresh_canvas()

    def action_pan_left(self) -> None:
        self._pan(-1, 0)

    def action_pan_right(self) -> None:
        self._pan(1, 0)

    def action_pan_up(self) -> None:
        self._pan(0, -1)

    def action_pan_down(self) -> None:
        self._pan(0, 1)

    def _unpainted_ids(self) -> frozenset[str] | None:
        """The graph's nodes minus the ones the current render actually painted.

        LLR-N06.3.1 read literally: ONE set difference, and no fold count is
        added to a viewport count anywhere.  Summing the two double-counts every
        node that is both folded and off-screen, and the indicator then declares
        more hidden nodes than the graph contains.

        `None` -- not an empty set -- when the operator is in a view that
        declares nothing.

        THAT STATE NOW HAS NO OCCUPANT, and this docstring described the old one
        long after it was gone: it said `painted_ids` lived on `views/layered.py`
        ONLY, that `outline` and `radial` hide nodes without declaring them, and
        that the hole was carried as `B-55`.  All three were true when written
        and all three are false now -- `B-55` closed across `layered` (Inc-3),
        `outline` (`Inc-B55a`) and `radial` (`Inc-B55b`), so every view the
        screen builds declares.

        The `None` branch is kept rather than deleted because it is the CONTRACT,
        not a description of today's view set: a future view that declares
        nothing by design gets an explicit `None` entry in `_painted_ids_for`,
        exactly as `outline` and `radial` had.  Answering that with a `getattr`
        probe would still convert a declared gap into a silent skip, which is why
        the dispatch is by identity.

        `None` ALSO when the layout itself failed.  `painted_ids` shares
        `_geometry` with `render`, so it raises on exactly the frames the canvas
        cannot draw -- and this helper is called from `refresh_canvas`, inside
        the message pump.  Letting that escape turns a contained, declared
        degradation ("no se pudo dibujar el mapa") into a dead app.  `None` is
        the value this helper already has for "this view declares nothing",
        which is the truthful answer for a frame that was never laid out.

        RESOLUTION HAPPENS OUTSIDE THE GUARD, AND THAT IS LOAD-BEARING
        (`AT-058`).  The `except` below is TOTAL, so a renderer with no entry in
        `_painted_ids_for` would be caught here and answered `None` -- and
        `None` means "this view declares nothing", which `LLR-N06.3.3` makes
        mean "nothing is hidden".  A BROKEN declaration would present as an
        ABSENT one.  `Inc-B55` is what makes this seam reachable by more than
        one renderer, so the two are separated BEFORE anything is wired through
        it: an unregistered renderer RAISES, and only a layout failure degrades
        to `None`.
        """
        declare = self._painted_ids_for(self._current_renderer())
        if declare is None:
            return None
        w, h = self._canvas_size()
        try:
            painted = declare(self.graph, self._view_state(w, h))
        except Exception:
            return None
        return frozenset(self.graph.nodes) - painted

    def _painted_ids_for(self, renderer):
        """The function this renderer declares its painted set through.

        IDENTITY, NEVER `getattr` (`A-98`, ruling `02j`): a probe answers "this
        view declares nothing" and "this view's declaration is broken" with the
        same `None`, which is the silent skip this batch keeps catching.

        `None` here means DECLARES NOTHING BY DESIGN, and it is an EXPLICIT
        entry rather than an absence -- `outline` and `radial` are the `B-55`
        hole, stated rather than omitted.  A renderer ABSENT from this mapping
        is a CODE DEFECT and raises, because `frozenset()` is a LEGITIMATE
        return for this helper's caller -- both degraded render paths produce
        one -- so an unregistered renderer answering with it would be a lie the
        strip paints as "nothing hidden".
        """
        if renderer is self.renderer:
            return painted_ids
        if renderer is self.outline_renderer:
            return outline_painted_ids
        if renderer is self.radial_renderer:
            # DECLARES SINCE `Inc-B55b`, through a cell-ownership replay rather
            # than a filter over `place()`: the canvas is last-write-wins and
            # records no owner, so deriving from placement over-declares
            # (`M-N06.3-b`).  The declared set was checked against the
            # composited frame and equalled it at every combination driven -- by
            # a SCRATCH PROBE at 16, and by the suite's own arms, which are 13
            # (10 `AT-059` plus 3 `AT-057`, the latter on `legacy` only). The
            # "16" belongs to the probe and is not reproducible from the tree,
            # which is why both numbers are given rather than the flattering
            # one.
            return radial_painted_ids
        raise LookupError(
            f"no painted_ids declared for {type(renderer).__name__}; add an "
            "explicit entry -- absence is a code defect, not a view with "
            "nothing to say"
        )

    def _park_focus(self) -> None:
        """Hand the keyboard back to the map itself."""
        self.set_focus(None)

    def _declare_after_layout(self) -> None:
        """Repaint BOTH declaring surfaces once layout is real — B-56 and B-60.

        `on_mount` paints before the compositor has given the canvas its region,
        so the declaration computed there describes a frame that does not exist.
        Measured on `legacy`, that is not a stale numeral but an ABSENT one: at
        50x20 and 60x20 -- ordinary sizes -- half the map was off screen and the
        strip said nothing at all, which `LLR-N06.3.3` makes mean "nothing is
        hidden".

        AND ORDINARY NAVIGATION DOES NOT HEAL IT.  Measured over nine keys, only
        `l` and `o` reconcile the surfaces; `j`, `k`, `h`, the arrow keys and
        `tab` do not -- at the root `j` is a no-op, so nothing repaints.  A
        reader who only LOOKS at the map, which is US-N06's whole use case,
        would otherwise keep two contradicting indicators indefinitely.  An
        earlier revision recomputed only the STRIP and carried the canvas
        header's own numeral as `B-60` on the claim that "any repaint at all
        reconciles them"; that claim was measured and is false, so the residual
        is closed here instead of narrated.

        A full `refresh_canvas` would also close it and would also re-`show` the
        rail and the inspector, moving the keyboard after `LLR-CNV.3.1` and
        `B-50` placed it -- measured, `call_after_refresh(refresh_canvas)`
        reddens the focus arm with `assert 'rail' == 'inspector'`.  So this
        repaints exactly the two surfaces that DECLARE and nothing that focuses.
        No `pulse_cursor`: this is a declaration repaint, not a cursor move, and
        a second breath on mount is motion the operator did not cause.
        """
        self._open_paint_pass()
        canvas = self.query_one("#map-canvas", Static)
        region = canvas.region
        w, h = self._canvas_size()
        # THE GUARD IS `P1` ITSELF, not a second mechanism.  `P1` says content
        # and geometry agree at rest; if they ALREADY agree, this re-render is
        # byte-identical and there is nothing to reconcile.  That is why it is
        # safe in a way "re-render only when the strip changed" would not be:
        # the predicate skipped on is the property the invariant asserts, so the
        # guard cannot drift from what it protects.
        #
        # AND IT IS THE WHOLE INPUT, NOT A PROJECTION OF IT.  Keyed on `(w, h)`
        # alone this sentence was FALSE and the security review fired it: content
        # depends on the renderer and every `ViewState` field, so a view switch
        # at one unchanged geometry let this skip while the strip repainted --
        # canvas declaring 7 in layered beside a strip declaring 5 in outline.
        #
        # It is not an optimisation looking for a problem.  MEASURED on an
        # 11999-node graph -- the largest `outline` will render -- one unguarded
        # settle pass costs 0.33 s at 118x34 and 0.28 s at 80x24, roughly
        # DOUBLING a repaint that already costs 0.36 s.  Arming the settle from
        # `refresh_canvas` without this would have shipped that.
        state = self._view_state(w, h)
        renderer = self._current_renderer()
        if (renderer, state) != self._rendered_for:
            try:
                text = renderer.render(self.graph, state)
            except Exception:
                # `refresh_canvas` has already painted its declared "no se pudo
                # dibujar el mapa" for this frame; overwriting it from here would
                # replace a stated degradation with a second copy of itself.
                pass
            else:
                canvas.update(text)
                self._rendered_for = (renderer, state)
        self.query_one(f"#{COUNT_REGION_ID}", Static).update(self._pagination_text())
        # ONE PASS IS NOT ENOUGH, AND THAT WAS `B-60`'s RESIDUAL.  This runs on
        # the first `call_after_refresh`, and at narrow terminals the region is
        # still reflowing then: instrumented at (31,16) the three passes saw
        # 31x1, then 29x2, and the region SETTLED at 31x3 afterwards, so both
        # declaring surfaces kept a numeral computed for a frame that no longer
        # existed -- the strip read 8 against a truth of 7.  So the declaration
        # follows the region until it stops moving, which is the condition it
        # actually needs and one a one-shot callback cannot express.  It
        # terminates because it re-schedules only while the region CHANGED, so
        # a settled layout costs exactly one extra no-op pass.
        if region != self._declared_for:
            self._declared_for = region
            self.call_after_refresh(self._declare_after_layout)

    def on_resize(self, event: events.Resize) -> None:
        """Re-declare when the layout actually settles — `B-60`, closed properly.

        `on_mount` schedules `_declare_after_layout` on the FIRST
        `call_after_refresh`, and at narrow terminals that callback runs while
        `_apply_region_visibility`'s show/hide is still reflowing the row.
        Instrumented at (31,16): the callback saw a 29x2 canvas region, so
        `_canvas_size` took the short-region branch, returned `h = 1` and
        declared nothing painted; the region then settled to 31x3.  With no
        resize handler nothing recomputed, so BOTH declaring surfaces kept a
        numeral computed for a frame that no longer existed -- the strip said 8
        while 7 were hidden.  Reproduced at (31,16), (32,16), (34,15), (35,14)
        on `legacy` and independently on `anidado`, so it is not a fixture
        quirk.

        A one-shot post-mount callback cannot see the settle; the resize can.
        This repaints the same two surfaces `_declare_after_layout` does and
        nothing that focuses, so `LLR-CNV.3.1` and `B-50` stay where they are.

        THIS HANDLER ALONE DOES NOT CLOSE IT, and the measurement says why: a
        SCREEN resize is not a CANVAS resize.  Traced at (31,16), this fires
        once with the terminal's own 31x16 -- BEFORE the row reflows -- and the
        canvas region moves twice more afterwards without any further screen
        resize.  So this covers the case that had no handler at all, an operator
        resizing the terminal after mount, and `_declare_after_layout` chases
        the region to its settle from wherever it is entered.
        """
        self._declared_for = None
        self._declare_after_layout()

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        """`H2` (closing verdict, round 5): repaint on every focus change, so
        the selection's tone always matches the real focus owner --
        `_view_state`'s `focus_owner` already decides blue (`V23`, on the
        canvas) versus grey (`V24`, focus elsewhere); nothing here decides
        the tone, it only asks for the repaint that reads it.

        MEASURED DEFECT: `tab` alone never repainted anything on this
        screen, so a card stayed painted blue after the keyboard had already
        left the canvas -- and closing the legend after such a `tab`
        inherited exactly that stale paint (`esc` restores the FOCUS
        correctly, `_restore_after_legend` already does that, but nothing
        told the canvas the tone underneath it was wrong before `?` was ever
        pressed).

        The canvas-only path (`_declare_after_layout`), never
        `refresh_canvas`: this must not rebuild the inspector or move focus
        itself, only redraw what the CURRENT focus already is.  Cheap when
        the change stays inside the canvas: `_declare_after_layout` no-ops
        whenever the `ViewState` it would paint -- `focus_owner` included --
        already equals the one last painted (`P1`)."""
        self._declare_after_layout()
        if isinstance(event.widget, FieldInput):
            # U2: while a field holds the keyboard, typing drafts and `j` types,
            # so the map-navigation hint lies.  Name the save key instead.
            self.query_one(HintLine).set_hint(self._field_hint(), self._seat_glyph("save_draft"))

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        """The other half of `H2`: a field can blur to NOTHING (the
        inspector's own `escape`, `FichaInspector.action_leave_field` ->
        `set_focus(None)`) with no `DescendantFocus` to follow it. Without
        this the tone would stay on "focus elsewhere" after the keyboard had
        already left every region."""
        self._declare_after_layout()
        if isinstance(event.widget, FieldInput):
            self.query_one(HintLine).set_hint(self._resting_hint())

    def _current_renderer(self):
        if self.outline_mode:
            return self.outline_renderer
        if self.radial_mode:
            return self.radial_renderer
        return self.renderer

    @property
    def legend_view(self) -> str:
        """HLR-N16.2: the name of the view `?` explains, read from the same
        two booleans `_current_renderer` reads.  One name per view, the one
        the legend title carries (Inc-8 verdict `D5`, in English per the
        2026-09-29 language ruling), read from `darkside.VIEW_NAMES`; this
        screen's own headers keep their words until Inc-9."""
        if self.outline_mode:
            return darkside.VIEW_NAMES["outline"]
        if self.radial_mode:
            return darkside.VIEW_NAMES["radial"]
        return darkside.VIEW_NAMES["canvas"]

    # -- the docked legend (Inc-8 verdicts `F2`, `F9`, `G2`, `G5`) ----------
    # The legend reads `legend_view_left` and calls the two methods below;
    # nothing else does.  They move the view only through this screen's own
    # pan state and its clamp, never a renderer.

    #: `G5`: the revealed card keeps this many columns clear of the docked
    #: panel's left edge, so it does not sit flush against it.  Declared once
    #: here; `_pan_revealing_selection` is the only reader.
    REVEAL_MARGIN_CELLS = 2

    @property
    def legend_view_left(self) -> int:
        """`F9`: the first column of the view, so the legend docks only while
        the canvas keeps its minimum beside the panel.  The rail is the only
        region left of the canvas (`_chrome_width` counts it the same way)."""
        return 0 if self.rail_hidden else RAIL_WIDTH

    def legend_docked(self, panel_x: int | None) -> None:
        """The legend is docked with its left edge at screen column `panel_x`,
        or is open but not docked (`None`, the modal layout).

        The pan the operator had when the legend opened is kept, and every
        call starts from it: a resize re-derives the reveal instead of
        stacking one on another, and the modal layout gets the kept pan back
        exactly.  Docked, the view pans right just enough for the selected
        card to sit wholly left of the panel -- only when the panel is what
        covers it.  A card already clear of the panel, or already past the
        canvas's right edge before the legend opened, does not move the view.
        The pan stays in `LLR-N06.1.2`'s legal range, so a card at the map's
        own right edge can stay partly covered (`INC8-D3-F2`).

        Both steps go through `_move_pan` (`INC8-P3-CR-F1` fix `a`+`b`),
        which repaints through `_declare_after_layout`'s canvas-only path --
        never the rail or the inspector, so the keyboard's focus is never at
        risk from opening the legend -- and which itself no-ops when nothing
        actually needs repainting.  The reveal is read from the state the
        reset-to-kept-pan step recorded (`_rendered_for`), so this path
        never reads the search resolution outside a paint pass
        (`test_search.py`'s census)."""
        if self._pan_before_legend is None:
            self._pan_before_legend = (self.pan_x, self.pan_y)
            focused = self.focused
            self._focus_before_legend = focused.id if focused is not None else None
        kept_x, kept_y = self._pan_before_legend
        self._move_pan(kept_x, kept_y)
        if panel_x is not None:
            self._move_pan(self._pan_revealing_selection(panel_x), kept_y)

    def legend_closed(self) -> None:
        """The legend closed: the pan and the focus it held return exactly
        (`F2`, `INC8-P3-CR-F1`).

        This runs from `HelpScreen.action_dismiss_none`, BEFORE its own
        `dismiss()` pops this screen back onto the stack -- the pop's
        `ScreenResume` has not even been posted yet, and Textual's own
        `AUTO_FOCUS` answers exactly that message by grabbing the rail
        whenever nothing is focused here (carried `UX-F7`, measured on the
        base tree, no code of this batch's).  Restoring here would just be
        overwritten a moment later, so the restore itself waits for
        `on_screen_resume`, which answers the very same message."""
        if self._pan_before_legend is None:
            return
        self._legend_restore_pending = (*self._pan_before_legend, self._focus_before_legend)
        self._pan_before_legend = None
        self._focus_before_legend = None

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        """Undo Textual's own post-resume auto-focus once the legend that
        just closed left a restore pending (`INC8-P3-CR-F1` fix `c`).

        `Screen._update_auto_focus` answers this SAME `ScreenResume` and
        focuses the first focusable widget the instant `self.focused` is
        `None` at resume -- regardless of what was focused before `?` was
        pressed.  This handler is dispatched BEFORE that framework pass
        (Textual walks the MRO for a `ScreenResume` handler and this
        screen's own `on_screen_resume` sits ahead of `Screen`'s internal
        `_on_screen_resume` in it), so restoring inline here would still
        lose to the auto-focus that runs right after.  `call_after_refresh`
        posts a fresh message instead, which this screen's queue processes
        only once the `ScreenResume` already being handled -- auto-focus
        included -- is done with."""
        if self._legend_restore_pending is not None:
            pan_x, pan_y, focus_id = self._legend_restore_pending
            self._legend_restore_pending = None
            self.call_after_refresh(self._restore_after_legend, pan_x, pan_y, focus_id)

    def _restore_after_legend(self, pan_x: int, pan_y: int, focus_id: str | None) -> None:
        """The pre-legend focus wins over the auto-focus grab -- restored
        FIRST, so the one repaint that follows reads the real owner through
        `_focus_owner` instead of the transient one.  That ordering is what
        the operator saw as the selection card flashing from blue to grey on
        `esc` (`INC8-P3-UX-F1`, carried `UX-F7`).

        `INC8-CL-CR-F1`: the pan is re-clamped AFTER the restore, on the
        canvas's CURRENT size -- a resize while the legend was open (docked
        or modal; the legend keeps the operator's kept pan through either)
        can shrink the extent under `pan_x`.  At an unchanged size this is a
        no-op: the kept pan is already legal, so `A-109`'s "closing still
        restores the kept pan exactly" is unaffected.

        `INC8-FU-F6` (follow-up, non-blocking at Inc-8's close): this used to
        set the pan through `_move_pan`, which repaints on its own, and then
        repaint AGAIN below to show what `_reclamp_pan` had just clamped --
        two calls to `_declare_after_layout` for one restore, the second
        cheap only because it usually has nothing left to change.  The pan is
        set directly here instead (the same assignment `_move_pan` makes,
        without its repaint), clamped, and declared exactly once, over the
        FINAL value either step could have produced.

        `_reclamp_pan` reaches `_view_state`, which is `_PASS_FREE_READERS`'
        business, not this method's -- see that dict's own entry for why a
        stale search memo cannot corrupt what `_reclamp_pan` computes here
        (`test_search.py`)."""
        widget = None
        if focus_id is not None:
            matches = self.query(f"#{focus_id}")
            if len(matches):
                widget = matches.first()
        self.set_focus(widget)
        self.pan_x, self.pan_y = pan_x, pan_y
        self._reclamp_pan(*self._canvas_size())
        self._declare_after_layout()

    def _move_pan(self, pan_x: int, pan_y: int) -> None:
        """Move the pan and repaint through `_declare_after_layout`'s
        canvas-only render path rather than `refresh_canvas`
        (`INC8-P3-CR-F1` fix `a`+`b`).  A legend-driven pan move never
        changes the selected node, the fold or the graph, so the rail and
        the inspector have nothing to re-show; `refresh_canvas`'s own
        rebuild of the inspector (`FichaInspector._rebuild`'s
        `remove_children`) is exactly what threw the keyboard's focus to the
        rail every time this ran, docked or modal.

        Called UNCONDITIONALLY: `_declare_after_layout` already no-ops when
        the `ViewState` it would paint equals `_rendered_for` (`P1`), so a
        call that changes nothing costs one cheap dataclass compare.  A
        hand-rolled `(pan_x, pan_y)` guard here looked equivalent and is NOT:
        a terminal resize can change the CANVAS's geometry while leaving the
        pan NUMBER the same, and that guard then skipped the repaint the new
        geometry needed -- measured RED on
        `test_f2_the_modal_layout_does_not_pan_and_a_resize_re_derives_the_pan`
        (resized narrow then back to the reference width: the reveal came
        back `(0, 0)` instead of the original `(7, 0)`, because the pan
        value alone had not changed even though the frame it was read
        against had)."""
        self.pan_x, self.pan_y = pan_x, pan_y
        self._declare_after_layout()

    def _pan_revealing_selection(self, panel_x: int) -> int:
        """The painted pan, moved right until the selected card's box ends
        `REVEAL_MARGIN_CELLS` short of screen column `panel_x` (`G5`), or
        already does.  Only a renderer that consumes pan moves (`PAN-1`:
        outline and radial do not pan).  Read from the state the canvas was
        last painted from, through the same layout it draws
        (`layered._geometry`, read only), so the card is where the frame
        paints it.

        `A-109` (Inc-8 design pass 4, verdict `G2`): the target is clamped to
        the range legal on the VISIBLE canvas -- the columns left of the
        docked panel -- not the canvas's own full drawn width.  A card whose
        pre-dock pan already sat at the OLD range's maximum (the map's own
        right edge) used to stay partly covered: the old bound assumed the
        whole drawn width was visible, when the panel already covers the
        rightmost `panel_x`-to-`avail` slice of it regardless.  This is the
        one clamp `LLR-N06.1.2` now amends, and only for this call: `_clamp_pan`
        itself, and every other caller of it, is untouched.

        `H3` (closing verdict, round 5) fixes two things in the SAME call:

        `right`'s off-by-one.  A card's box is `geo.card_w` columns wide, but
        the title row's own fit (`views/layered.py`: `title_w = card_w - 3`,
        the glyph `▐ ` two columns ahead of it) never reaches the box's own
        last column when the row carries no change chip -- that column is
        declared width, not painted ink.  Treating it as painted put the
        margin's target one column too far right, so `REVEAL_MARGIN_CELLS`
        painted as 3 blank columns on an ordinary card, not 2.  `right` below
        is ONE COLUMN PAST the last column this call has reason to believe is
        painted -- never "the box's own last painted column" itself, which is
        `right - 1` (`INC8-FU-F4`: an earlier revision of this docstring said
        the second thing and meant the first).

        `INC8-FU-F1` (follow-up, non-blocking at Inc-8's close): a changed
        card paints ONE MORE column than an ordinary one.  `views/layered.py`
        paints the diff chip through the box's own last column
        (`chip_x + len(chip) - 1 == cx + geo.card_w - 1`), the exact column
        the ordinary case never reaches -- and the selection's own highlight
        pass never repaints that one column either way, diff or not, so it is
        the chip's paint that survives there.  Measured before this fix: a
        changed, selected card left only 1 blank column, not the declared 2,
        because `right` subtracted the ordinary case's `- 1` even where the
        chip made that column painted ink.  `chip_painted` below reads the
        SAME predicate `views/layered.py` gates the chip's own paint on
        (`changed.get(nid)` truthy, not merely `nid in changed`, which would
        wrongly count a diff entry whose list happens to be empty).

        The widened range.  At the map's own true right edge the OLD clamp
        left the margin exactly 0 -- read at the time as `LLR-N06.1.2`'s own
        "no blank space past the content" principle.  The operator's answer
        withdrew that reading for this one case (`A-109`'s dated addendum):
        the margin is painted everywhere, edge included, so the legal range
        this call clamps against widens by `REVEAL_MARGIN_CELLS` too -- room
        the docked panel already occupies on screen regardless of where the
        pan sits, exactly `A-109`'s own argument for widening to the visible
        span in the first place, one step further."""
        cursor = self.nav.cursor
        if cursor is None or not self._consumes_pan(self._current_renderer()):
            return self.pan_x
        _renderer, state = self._rendered_for
        pan_x = state.pan_x
        try:
            geo = layered_geometry(self.graph, state)
            (extent_x, _span_x), _y = pan_extent(self.graph, state)
        except Exception:
            # A frame that cannot be laid out cannot be panned (`_pan`).
            return pan_x
        if geo is None or cursor not in geo.pos:
            return pan_x
        canvas_x = self.query_one("#map-canvas", Static).region.x
        card_x, _card_y = geo.place(cursor)
        changed = state.diff.changed if state.diff else {}
        chip_painted = bool(changed.get(cursor))
        right = canvas_x + card_x + geo.card_w - (0 if chip_painted else 1)
        edge = panel_x - self.REVEAL_MARGIN_CELLS
        if card_x >= geo.avail or right <= edge:
            return pan_x
        visible_span = panel_x - canvas_x
        return self._clamp_pan(
            pan_x + right - edge, extent_x + self.REVEAL_MARGIN_CELLS, visible_span
        )

    def _current_crumb(self) -> list[str]:
        prefix = self.source_crumb or [self.map_id]
        if self.source_crumb:
            prefix = prefix + [f"linked: {self.map_id}"]
        return prefix

    def _branch_coverage_glyph(self, branch_root: str) -> tuple[str, str]:
        """Return (glyph, style) for a top-level branch's coverage minimap.

        THE `seen` SET IS NOT DEFENSIVE PADDING; without it this walk does not
        terminate.  It had no visited check at all, so on a graph with a cycle
        it re-expanded the same nodes forever -- an unbounded HANG reached from
        `refresh_canvas`, outside every guard, which is worse than the crash the
        sibling guards catch and is the one failure mode this tree's own rule
        singles out.  It also double-counted on a multi-parent DAG, where a node
        reachable by two paths landed in `nodes` twice and skewed the coverage
        percentage this glyph exists to report.
        """
        nodes = [branch_root]
        seen = {branch_root}
        stack = [branch_root]
        while stack:
            parent = stack.pop()
            for cid in self.graph.children_of(parent):
                if cid in seen:
                    continue
                seen.add(cid)
                nodes.append(cid)
                stack.append(cid)
        total = len(nodes)
        con_acta = sum(1 for nid in nodes if self.graph.nodes[nid].ficha.fields.get("D", "").strip())
        if total == 0:
            return ("╱", darkside.WORDMARK)
        pct = con_acta / total
        if pct >= 1.0:
            return ("█", darkside.INK)
        if pct >= 0.5:
            return ("▒", darkside.MUT)
        return ("░", darkside.WARN)

    # The coverage strip's budget: A COUNT CEILING AND A CELL BUDGET, and the
    # second exists because the first alone shipped broken.
    #
    # A count cap bounds ENTRIES; it does not bound CELLS, and titles are
    # file-derived.  The first revision capped 24 entries and appended the
    # declaration and the legend LAST, so at 80 columns those 24 entries wanted
    # about five rows and the clip ate entries 20-23, the declaration, and the
    # whole legend -- leaving the operator four coverage glyphs with no key, on
    # a strip still reporting its full three rows.  Measured: with short titles
    # the legend is lost from TWENTY branches up at 80 columns, and on a large
    # graph 118 was the ONLY width in {60, 70, 80, 100, 118} where the
    # declaration survived at all.
    #
    # `_HINT_BRANCH_CELLS` above records this same lesson in its own words -- a
    # fixed cell count fits at 118 and WRAPS at 80 -- and this is the second
    # surface to learn it.  So the entries take the ROW'S REMAINDER: the
    # caption, the legend and the declaration are reserved FIRST and the entries
    # fill what is left.  The affordances outrank the entries, exactly as they
    # do on the hint line.
    # THERE IS NO SEPARATE COUNT CEILING, and its absence is a finding rather
    # than a simplification.  A `MINIMAP_BRANCHES = 24` sat here beside the cell
    # budget, and a mutant setting it to `10**9` left the whole suite GREEN --
    # measured first by both independent reviews, then reproduced here after the
    # budget landed.  The reason is not a missing oracle: `min(24, budget //
    # per_entry)` is decided by the BUDGET at every width below roughly 162
    # columns, so the ceiling had no work left to do.  Two bounds where one does
    # the work is the duplication this batch keeps paying for; the redundant one
    # is gone, and the arm tests the bound that actually binds.
    #
    # Must equal the stylesheet's `max-height` for `#map-minimap`.  Two
    # spellings of one number is how they drift, so an arm asserts the two agree
    # rather than trusting this comment to be read.
    MINIMAP_ROWS = 3
    _MINIMAP_CAPTION_CELLS = 14
    _MINIMAP_LEGEND_CELLS = 37
    _MINIMAP_DECL_CELLS = 26
    _MINIMAP_NAME_CELLS = 12
    # a name, a space, the glyph, and the three-cell gap after it
    _MINIMAP_ENTRY_OVERHEAD = 5

    def _minimap_entry_limit(self, width: int, branches: int) -> int:
        """How many branches fit once the affordances have been paid for.

        THE DECLARATION'S CELLS ARE RESERVED ONLY IF THERE WILL BE A
        DECLARATION, and the conditional is the whole point of this method
        rather than a refinement of it.  Reserving unconditionally MANUFACTURES
        the omission it announces: measured on the shipped `legacy` map at
        35x14, an unconditional reserve drew ONE of three branches and declared
        `+2 ramas sin mostrar`, where the plain strip had drawn all three -- and
        the strip's height and the canvas's height were IDENTICAL either way, so
        the two dropped branches bought nothing at all.

        That is this increment's own `height: 3` mistake in a second costume:
        taxing the ordinary map to bound the pathological one.  The order below
        resolves the apparent circularity -- the limit decides whether there is
        a remainder, and the remainder decides the reserve -- by asking the
        cheaper question first: if everything fits WITHOUT a declaration, no
        declaration is needed and none is charged for.
        """
        per_entry = self._MINIMAP_NAME_CELLS + self._MINIMAP_ENTRY_OVERHEAD
        base = self.MINIMAP_ROWS * max(1, width) - self._MINIMAP_CAPTION_CELLS \
            - self._MINIMAP_LEGEND_CELLS
        if max(0, base) // per_entry >= branches:
            return branches
        return max(0, base - self._MINIMAP_DECL_CELLS) // per_entry

    def _minimap_text(self, width: int) -> Text:
        if self.graph.root_id is None:
            return Text("")
        parts: list[tuple[str, str]] = [("  coverage   ", darkside.MUT)]
        children = self.graph.children_of(self.graph.root_id)
        limit = self._minimap_entry_limit(width, len(children))
        for cid in children[:limit]:
            glyph, style = self._branch_coverage_glyph(cid)
            # Both halves are file-derived, and this widget's whole job is
            # telling the operator WHICH branch is at risk -- a `U+202E` here
            # displays one branch's coverage under a neighbour's name, so an
            # uncoerced title deceives the operator on exactly the judgement the
            # minimap exists to support.  `refresh_canvas` repaints it, which is
            # what puts it inside `LLR-N06.2.3`'s "every file-derived string
            # painted on a surface this batch touches".
            #
            # BOUNDED IN CELLS TOO, and `fit` rather than a slice: it coerces
            # (it calls `plain` itself) and it truncates VISIBLY.  A silent
            # row-drop is what the previous revision did, and an operator cannot
            # tell a truncated branch name from a short one.
            name = darkside.fit(self.graph.nodes[cid].ficha.title or cid,
                                self._MINIMAP_NAME_CELLS)
            parts.append((f"{name} ", darkside.MUT))
            parts.append((glyph, style))
            parts.append(("   ", ""))
        undrawn = len(children) - limit
        if undrawn > 0:
            # INK, not MUT, and `#D28` is why: this is a DECLARATION of how much
            # is not on screen -- the same load-bearing role the rule escalates,
            # and the role it names the minimap caption under.  `#map-minimap`
            # inherits `Screen`'s ground today, where `MUT` would clear the
            # floor; `INK` clears on either ground, so the token stays legible
            # if this strip is ever given a `PANEL` background.
            parts.append((f"+{undrawn} branches not shown   ", darkside.INK))
        parts.extend([
            ("█", darkside.INK), (" complete ", darkside.MUT),
            ("▒", darkside.MUT), (" medium ", darkside.MUT),
            ("░", darkside.WARN), (" low ", darkside.MUT),
            ("╱", darkside.WORDMARK), (" no data", darkside.MUT),
        ])
        return darkside.Text.assemble(*parts)

    def _search_index(self) -> SearchIndex:
        """The owner of "what matches", CONSTRUCTED IN ONE PLACE.

        Extracted when `Inc-4c` gave the count region a second question to ask.
        `test_the_count_and_the_paint_share_one_resolution` censuses this
        module for `SearchIndex(...)` call sites and pins the total at one,
        deliberately: a second construction is how the strip's number and the
        canvas's highlight come to be computed from two owners that agree today
        and drift tomorrow.  `_whole_graph_tally` was that second site, and the
        arm reddened on it.

        THE ARM WAS RIGHT AND THE FIX IS TO SHARE, NOT TO EXEMPT.  The tally is
        only ever read where `_search_order` returned `None`, so no frame paints
        both -- but "these two cannot disagree because of when they run" is a
        REASONED argument, and this batch has three recorded cases of a reasoned
        agreement argument surviving a mutation that broke the property.  One
        constructor is a structural one.
        """
        return SearchIndex(self.graph)

    def _whole_graph_tally(self) -> int:
        """How many nodes match, over the WHOLE graph, WITHOUT ordering them.

        `HLR-N07.2`'s figure, reached by the cheap half of the owner.
        `SearchIndex.query` states `len(query(q)) == len(hits(q))` for every
        graph and says in as many words that the count line may be taken from
        either; this takes it from `hits` because that is the half the renderer's
        bound was never about.  Measured at 12002 nodes: 0.0075 s here against
        0.0122 s for the ordered form.

        DELIBERATELY NOT MEMOISED AND DELIBERATELY NOT NAMED LIKE A RESOLUTION.
        It is reached only from `_count_line`, once per strip build, and it
        returns an `int` rather than a result set -- so it is not a second
        answer to "what matches" that could drift from `_search_order`'s, which
        is the defect `C-D6a` and the single-resolution rule exist to prevent.
        The walk does not call it, and must not: `_walk_hits` is pinned by AST to
        exactly one resolution source, and a count read from a second place
        inside that handler is the shape its own arm warns can slip past the
        vocabulary regex.
        """
        return len(self._search_index().hits(self.query_text))

    def _query_echo(self) -> str:
        """The operator's query, coerced and BOUNDED, for the count region.

        Through `fit` for two separate reasons that happen to share a call.  The
        query is operator text on a surface this batch touches, so it is a
        coercion sink (`HLR-COERCE`) -- measured elsewhere in this file, a
        right-to-left override left alive reverses the sentence it sits in.  And
        it is unbounded in length on a region that WRAPS, so without a cell
        budget it grows the strip and takes rows from `#map-body`.

        THE CAP IS IN CELLS; THE DIMENSION THAT MATTERS IS ROWS, AND THE TWO
        ARE NOT THE SAME -- which is why the query is line-flattened BEFORE it
        is fitted.  `plain` deliberately preserves U+0009 and U+000A
        (`darkside.PRESERVED_CODE_POINTS`, and layout elsewhere depends on
        that), so 32 cells can be 32 ROWS.  Measured on the shipped surface at
        118x34 with a line-break-bearing query, before this flattening: the
        count region went to 32 rows, `#map-canvas` was crushed to 1, and the
        `esc limpiar` affordance left the painted frame entirely.  That is the
        `Inc-4b` collapse shape reproduced one surface over -- unbounded text
        taking the rows from `#map-body` and pushing the recovery affordance
        off-frame -- so the cap has to bound the row count, not the cell count,
        and `translate` is where it does.  The flattening is LOCAL TO THIS SINK
        on purpose: `plain` must keep both code points for the surfaces whose
        layout reads them.

        THE TABLE IS DERIVED FROM `PRESERVED_CODE_POINTS`, NOT RE-LISTED HERE.
        It used to spell the two code points again, which made this sink a silent
        DUPLICATE of the frozenset that decides them: a code point added there
        would keep being preserved by `plain` and stop being flattened here, and
        the row bound would reopen with every arm still green.  Reading the same
        owner means growth there is covered here by construction.

        WHY THIS REPO OWNS THAT GUARD RATHER THAN INHERITING IT.  No operator
        path on Textual 8.2.8 delivers U+000A into the `Input`: `enter` submits,
        and `Input._on_paste` takes `event.text.splitlines()[0]`.  The pin in
        `pyproject.toml` is exact, so that holds today -- but it is a
        third-party implementation detail with no documented guarantee, and the
        `Input` at the call site declares neither `max_length` nor `restrict`.
        A defence nothing here asserts is a defence a version bump removes in
        silence, so the guard is stated locally and
        `test_the_query_echo_bounds_rows_and_not_only_cells` pins OUR behaviour
        rather than Textual's.

        A FIXED CAP, AND THE FILE'S OWN PRECEDENT SAYS FIXED CAPS ARE WRONG --
        so this one is measured rather than reasoned.  `_HINT_BRANCH_CELLS`
        records a fixed 40 that fitted at 118 and wrapped at 80, and the budget
        there had to become the row's remainder.  THE TWO CASES DIFFER IN WHAT
        OVERFLOW COSTS: on `HintLine` a wrap pushed the affordances out of the
        painted frame, so the cap had to guarantee no wrap at all.  Here the
        region is the strip itself, `#map-body` is `height: 1fr` and absorbs the
        row, and predicate 1 only asks that the declaration be READABLE -- a
        two-row region is as readable as a one-row one.  What must not happen is
        UNBOUNDED growth, and 32 flattened cells bounds it.

        THE SWEPT EVIDENCE, CORRECTED -- AND THE CORRECTION IS "THIS NUMBER IS
        NOT STABLE", NOT A SECOND NUMBER.  An earlier revision claimed the extra
        row appeared at 60 and nowhere else.  Review swept the same band and
        found five widths (60, 65, 85, 90, 95).  Re-swept here on the shipped
        tree, same band, same step, at height 34 over the `adjuntos` fixture
        above the bound: NINE widths with length 1 against length 2000 (60, 65,
        70, 110, 115, 120, 125, 130, 135) and EIGHT with the six-character
        fixture against the same fixture plus 2000 (60, 65, 70, 115, 120, 125,
        130, 135).  Three measurements, three different width sets, because WHICH
        widths pay depends on how much of the row the rest of the strip has
        already spent -- the page numeral, the notice and the chord all scale
        with the fixture.  So the count of widths is NOT the load-bearing figure
        and is recorded here only to stop the next reader trusting one.

        WHAT IS STABLE ACROSS ALL THREE SWEEPS, and what the cap actually rests
        on: the delta is 0 or +1 at every width measured, never more; and the
        declaration is never taken off-frame.  That one row is the whole price of
        the fixed cap, and it is stated here rather than rounded off.

        A WIDTH-RELATIVE BUDGET WAS WRITTEN FIRST AND REMOVED.  It read
        `self.size.width`, which RAISES `NoActiveAppError` on a screen that is
        not mounted -- the way three unit arms in `test_search.py` reach this
        code -- so it made a pure string helper depend on being inside a running
        app.  It bought one row at the narrow end of the band.
        """
        return darkside.fit(
            self.query_text.translate(dict.fromkeys(darkside.PRESERVED_CODE_POINTS, " ")),
            _QUERY_ECHO_CELLS,
        ).rstrip()

    def _suspended_count_line(self) -> Text:
        """`LLR-N07.3.4` predicate 1 — the region above the renderer's bound.

        Four facts on one row: the query, the whole-graph count, the chord that
        still works, and what is suspended.  The chord's glyph is read FROM THE
        SEAT (`UX-Q3-b`'s one-declaration-four-readers rule), so a later rebind
        of `back_or_home` reaches this string without a second edit.

        WHICH CHORD IS NAMED, AND WHY IT IS NOT `n`.  `#D43`'s example wording
        names the walk (`n recorre`).  It is not painted here, because above the
        bound the walk DECLINES -- `_walk_hits` returns on `hits is None` -- and
        a region promising a chord the handler refuses is the `AT-052`/`AT-053`
        lying-affordance class this batch exists to close, reproduced by the fix
        for it.  What is painted instead is the chord that DOES work at this
        size, `esc`, plus a notice naming the walk among the suspended things.
        The clause's numeric threshold asks for the query, the count and the
        notice; all three are here.  The Statement's third clause is not
        satisfiable without either a second resolution source inside `_walk_hits`
        (forbidden by `test_cd6a`'s AST arm) or unpicking `_search_order`'s
        `None` (which `M-N07.3.4-a` presumes stays), and it is reported rather
        than quietly reinterpreted.
        """
        head = f"{SEARCH_ACTIVE_LABEL}: «"
        tail = (
            f"» · {self._whole_graph_tally()} {SEARCH_COUNT_SUBJECT} · "
            f"{self._seat_glyph('back_or_home')} clear · "
            f"{SEARCH_SUSPENDED_NOTICE}  "
        )
        return darkside.Text(
            f"{head}{self._query_echo()}{tail}", style=darkside.INK
        )

    def _count_line(self) -> Text:
        """`n/N coincidencias en el mapa` — HLR-N07.2, on the `#D37` strip.

        `N` is the WHOLE-GRAPH match count and comes from the search owner, not
        from `painted_ids` and not from anything that has seen `folded` or the
        pan offsets.  `n` is where the SELECTION sits inside that list, which is
        the only honest reading available: the walk that moves the selection
        between matches lands in the next increment, so `n` is `0` whenever the
        cursor is not itself a match, and it says so rather than reserving a
        placeholder numeral that would be a lie until the walk arrives.

        A query with no non-whitespace character paints NO LINE AT ALL
        (`LLR-N07.3.3`), which is also the state of a screen nobody has searched
        on yet -- and the two are the same state, so they paint the same way.
        `0 coincidencias en el mapa` means something different and is reserved
        for it: a question that was asked and came back empty.

        ABOVE THE RENDERER'S BOUND THE REGION DECLARES THE SEARCH ANYWAY
        (`LLR-N07.3.4`, `#D43`) -- AND THIS REVERSES WHAT `Inc-4b` SHIPPED HERE.
        Until `#D43` this branch returned an empty `Text`, on the argument that
        above the bound the question was never ANSWERED and `0 coincidencias`
        over a graph holding 6001 real matches is the lying affordance US-N07
        exists to remove.  The second half of that argument still stands and is
        why `0` is not what gets painted.  The FIRST half was wrong: the question
        can be answered cheaply, and the silence left the operator with a query
        that still changed what `n` did while no surface advertised it -- live
        enough to change a keypress, invisible enough to have no affordance.

        SO THE COUNT IS TAKEN FROM `hits`, NOT FROM `_search_order`, and that is
        the whole reason it is affordable.  `SearchIndex.query` documents
        `len(query(q)) == len(hits(q))` for every graph, so the figure is the one
        `HLR-N07.2` owns either way; what differs is the cost, and only the
        ORDERING was ever expensive.  Measured on a real 12002-node graph:
        `hits` 0.0075 s, `tree_order` 0.0097 s, `query` 0.0122 s.  The
        "seconds each, four resolutions per repaint" figure `_search_order`'s
        bound was argued from predates `tree_order`'s child-index repair and no
        longer holds -- so the bound now buys ~12 ms, and the argument for it is
        the RENDERER's (nothing is drawn, so no hit set is meaningful to it)
        rather than the search's.

        WHAT `_search_order`'s `None` NOW MEANS, restated because this branch is
        what gave it its old meaning.  It no longer means "nobody asked": the
        count line asks at every size.  It means the ORDER was not resolved, so
        no highlight is painted and no walk is available -- which is exactly what
        `SEARCH_SUSPENDED_NOTICE` says on the same row.

        THE SUSPENSION NOTICE IS THE LOAD-BEARING HALF, not decoration.  A live
        count over an unlit canvas with no stated reason trades one hidden state
        for another, and `M-N07.3.4-b` is precisely the mutant that paints the
        count and drops the notice.

        Below the bound nothing here changed: `n/N`, the reserved `0`, and the
        offset `LLR-N07.3.2` asks for are all as `Inc-4a` shipped them.  Because
        everything painted before this point on the strip has a fixed width for
        a given graph, the count begins at the SAME offset whether it reads `0`
        or `3/5`.

        The tone is deliberately uniform.  `LLR-N07.3.2`'s empty-state TONE ships
        with the query chip, the hint line and the two toasts in the increment
        that owns them; painting a tone split here that nothing observes would
        be shipping an unobserved behaviour on a green suite, which is the exact
        failure this batch is spending its budget to stop.
        """
        if not self.query_text.strip():
            return darkside.Text("")
        hits = self._search_order()
        if hits is None:
            return self._suspended_count_line()
        if not hits:
            return darkside.Text(f"0 {SEARCH_COUNT_SUBJECT}  ", style=darkside.INK)
        at = hits.index(self.nav.cursor) + 1 if self.nav.cursor in hits else 0
        return darkside.Text(
            f"{at}/{len(hits)} {SEARCH_COUNT_SUBJECT}  ", style=darkside.INK
        )

    # The meter's step ceiling.  24 was measured during `Inc-4c`'s F-2 work as
    # the value that takes this region to two rows on a 12002-node graph; with
    # the minimap and this strip now both bounded in the stylesheet it is one
    # row at 118 columns and fits inside the strip's 3 at 80.
    METER_STEPS = 24

    def _pagination_text(self) -> Text:
        total = len(self.graph.nodes)
        page = 1
        per_page = max(1, total)
        # For now the tree is not paginated; this reserves the affordance.
        #
        # SUPERSEDED BY `Inc-STRIPS` -- THE METER IS BOUNDED NOW, and the block
        # below is kept because it records how the bound was arrived at.  Read
        # it as history: every sentence in it was true of the tree it was
        # written against and the first two are false of this one.  An earlier
        # revision of THIS increment claimed to have corrected it in place and
        # had not; the confirmation pass caught the packet asserting a byte
        # -identical block had changed, which is the same defect one register up.
        #
        # HISTORICAL, from the pre-bound tree:
        # THE METER IS STILL UNBOUNDED HERE, DELIBERATELY, AND BOUNDING IT IS
        # NECESSARY BUT NOT SUFFICIENT.  An earlier revision of this comment said
        # a cap "would not have helped"; that was wrong and is corrected here
        # rather than deleted, because a reader who trusts it bounds the minimap
        # alone and the count is still unreadable.  The meter prices one glyph
        # per node, so on a real 12002-node graph this region renders 104 rows
        # and is laid out at y=42 of a 34-row frame.  A 24-step cap was written
        # and measured: it takes the region to 2 rows but it is still laid out at
        # y=55, because `#map-minimap` is `height: auto` over the root's 4001
        # children and renders 668 rows on its own -- which also crushes
        # `#map-canvas` to a single row.  THE CONVERSE CONTROL WAS ALSO MEASURED,
        # minimap hidden and meter left unbounded: at 80x24 ALL 21 visible rows
        # are meter glyphs and the count is still off-screen, and at 118x34 the
        # same control yields 31 readable rows with the count on the last.  So
        # the minimap and the meter are INDEPENDENT causes and each alone is
        # enough to hide the count; the remedy bounds the minimap, the meter and
        # the overflow declaration TOGETHER.  That is a layout collapse across
        # three unbounded strips, not a defect of the count line, and it is
        # reported for its own increment rather than half-fixed from inside this
        # one.  See `increment-004c.md`, finding F-2 and its round-2 section.
        # THE METER IS BOUNDED HERE, and the numerals beside it carry the truth
        # the bar can no longer carry.  Priced one glyph per node it rendered
        # 12002 cells on a real large graph; capped at `METER_STEPS` it is one
        # row at every declared width.  Past the cap the bar stops being a
        # one-to-one scale and becomes a compressed one -- which is why
        # `page/per_page` is printed next to it and is NOT capped: the reader
        # who needs the exact figure reads the numerals, not the blocks.
        steps = min(per_page, self.METER_STEPS)
        filled = min(page, steps)
        text = darkside.Text.assemble(
            (" ", ""),
            darkside.step_meter(filled, steps),
            (f"   {page}/{per_page}  ", darkside.MUT),
        )
        text.append(self._count_line())
        # HLR-N06.3 on the strip beside the canvas, from the SAME `painted_ids`
        # pass the renderer used, so the two surfaces cannot declare different
        # totals.  `None` means a view that declares nothing, and the strip then
        # keeps only its reserved-affordance content.
        #
        # A BROKEN DECLARATION GETS ITS OWN WORDS, NOT SILENCE (`AT-058`).
        # `_painted_ids_for` RAISES for a renderer with no entry, and that raise
        # must not escape: this runs inside the message pump, and `TC-R08`
        # requires `refresh_canvas` to survive ANY renderer exception -- tests
        # and future code substitute renderers at runtime, and identity dispatch
        # cannot tell a substituted renderer from a forgotten one.  So the raise
        # is CAUGHT HERE and turned into a DIFFERENT OBSERVABLE.  Falling back to
        # silence instead would be the exact collision `AT-058` exists to break:
        # `LLR-N06.3.3` makes silence mean "nothing is hidden".
        try:
            hidden = self._unpainted_ids()
        except LookupError:
            text.append("hidden-node count unavailable ", style=darkside.INK)
            return text
        if hidden:
            # ONE SPELLING, consumed rather than repeated (`F7`).  This copy
            # already differed from the two renderers' -- same words, different
            # padding -- which is how a triplicated sentence starts drifting.
            text.append(f"{overflow_phrase(len(hidden))} ", style=darkside.INK)
        return text

    # The chrome around a toast's detail: the leading space, the label, and the
    # three-cell gap before the detail starts.
    _TOAST_CHROME_CELLS = 4

    def _event_toast(self, label: str, detail: str = "") -> None:
        """Bottom strip for events only — status words, not glyphs.

        THE DETAIL IS BOUNDED AT THIS SEAM, which is the only place all eleven
        call sites pass through.  Several of them hand it a file-derived node
        title, `#map-toast` carries no height rule, and the strip took its rows
        from `#map-body` -- so a 4000-character detail rendered 36 rows at 118x34
        and left the canvas ONE.  Same class as the crumb above it, with a
        smaller blast radius: it needs an operator action and it clears on the
        next toast, which is why it is degradation rather than a persistent
        collapse.

        `darkside.fit` COERCES AS WELL AS TRUNCATES -- it calls `plain` itself --
        so bounding here also closes a coercion gap the security review found at
        the export sink, which passed `str(path)` raw.  One seam, both defects,
        every call site.
        """
        toast = self.query_one("#map-toast", Static)
        if detail:
            room = max(
                self._TOAST_CHROME_CELLS,
                self.size.width - len(label) - self._TOAST_CHROME_CELLS,
            )
            detail = darkside.fit(detail, min(room, len(detail))).rstrip()
            text = darkside.Text.assemble(
                (f" {label}", f"bold {darkside.INK}"),
                (f"   {detail}", darkside.MUT),
            )
        else:
            text = darkside.Text.assemble((f" {label}", f"bold {darkside.INK}"))
        toast.styles.background = darkside.PANEL
        toast.update(text)

    # Widget id -> the `FOCUS_OWNERS` name that id stands for.  Bare ids, not
    # `#`-prefixed strings: nothing here is a CSS selector, and synthesising one
    # to compare against another string that merely looks like one silently
    # compares "#None" for every unnamed widget.
    _FOCUS_REGIONS = (
        ("map-rail", "rail"),
        ("map-inspector", "inspector"),
        ("map-canvas", "canvas"),
    )

    def _focus_owner(self) -> str:
        """Which region holds the keyboard, as one of `FOCUS_OWNERS`.

        Derived from the app's real focused widget rather than tracked
        separately: a second copy of "where the focus is" is a copy that goes
        stale, and the stale copy is the one the canvas would paint from.
        Returns `""` when nothing is focused, or when the focused widget belongs
        to no declared region -- the value that paints what the tree painted
        before this field existed.

        MEASURED: `#map-canvas` is `can_focus=False`, so `"canvas"` is not
        reachable through the real wiring today and the focused tone is arrived
        at via the `""` fallback.  The entry is kept because it is correct the
        moment the canvas becomes focusable, but a reader should not assume it
        is live (`B-53`).

        `""` IS ALSO THE HONEST ANSWER ON A NARROW TERMINAL, and that is not a
        defect: below `MIN_CANVAS_WIDTH`, `_apply_region_visibility` auto-hides
        the rail and the inspector, so nothing focusable remains and the focus
        chain is legitimately empty.  An earlier revision read that as "tab
        drops focus on this screen" and carried it as a defect -- measured only
        at the 80x24 default test size.  At 118x34 the chain is
        `[map-rail, insp-title, insp-state, insp-notes]` and tab traverses
        normally.  Retracted in `A-96`.
        """
        node = getattr(self.app, "focused", None)
        while node is not None:
            node_id = getattr(node, "id", None)
            for region_id, owner in self._FOCUS_REGIONS:
                if node_id == region_id:
                    return owner
            node = getattr(node, "parent", None)
        return ""

    def _search_order(self) -> tuple[str, ...] | None:
        """The live hits, over the WHOLE graph, in tree order.  `None` above the
        renderer's bound, where no order is resolved.

        WHAT `None` MEANS WAS NARROWED BY `LLR-N07.3.4` (`#D43`).  It used to
        mean "the question was not asked", and `_count_line` painted nothing on
        it.  The count region now asks at every graph size -- through
        `_whole_graph_tally`, which is the cheap half of the same owner -- so
        `None` means only that the ORDER was not resolved: no highlight is
        painted and no walk is available.  Every consumer below still reads it
        the same way; what changed is that a fourth surface stopped inferring
        "nobody asked" from it.

        THE SINGLE RESOLUTION ON THIS SCREEN.  The count line and the hit set
        the renderer paints from both come from here, and `_search_hits` is
        derived from it rather than resolved beside it -- deliberately, and the
        cost of the alternative was measured rather than imagined.  An earlier
        revision of this increment let the count line call the owner itself
        while `_view_state` called it separately; the two agreed, but nothing
        made them, and a mutation that scoped ONE of them to the visible set
        left the other correct and the acceptance green.  Two paths to "what
        matches" is the exact defect US-N07 exists to close, reproduced inside
        the screen that closes it.

        `MapScreen.folded` and `pan_x`/`pan_y` are not consulted and must never
        be: a count taken over what is on screen is risk A-6, and US-N06 ships
        fold in this same batch, so a viewport-scoped count would ACTIVELY
        CREATE the defect this story exists to close.

        THE BOUND IS THE RENDERER'S OWN, AND OBEYING IT IS THE POINT.  Above
        `MAX_RENDER_NODES` the renderer returns its overflow declaration without
        evaluating anything, so ordering a tree the app has already declared it
        will not draw buys nothing.  Search stops where drawing stops.

        THE COST FIGURE THIS BOUND WAS ARGUED FROM NO LONGER HOLDS, and saying so
        is the point of this paragraph.  `Inc-4a` justified the bound on "seconds
        each, three to four resolutions per repaint"; that measurement predates
        `tree_order`'s child-index repair, which took the walk from `O(N*E)` to
        `O(E)`.  RE-MEASURED at 12002 nodes for `Inc-4c`: `hits` 0.0075 s,
        `tree_order` 0.0097 s, `query` 0.0122 s.  So the bound is worth about
        12 ms per resolution, not seconds, and what still justifies it is the
        RENDERER's argument -- nothing is drawn, so no hit set is meaningful to
        it -- rather than the search's.  The figure is corrected here rather than
        left standing because a justification that names a mechanism which has
        since been repaired is how a later reader deletes the right guard.
        `S-15` observed that this bound limits the render COUNT and not the WORK;
        this closes the instance, not the underlying observation.

        AND "DECLARES NOTHING" IS RETURNED AS `None`, NEVER AS AN EMPTY ORDER.
        The first revision of this bound returned an empty order, which
        `_count_line` cannot tell from a question that came back empty -- so at
        12002 nodes it painted `0 coincidencias en el mapa` over a graph holding
        241 real matches.  An unanswered question and an answer of zero are
        different facts, they are gated by different arms, and the type is what
        keeps them apart.

        THE ORDER HANDED OUT IS IMMUTABLE.  It was the memo's own list, so a
        consumer that sorted or trimmed what it received corrupted every later
        read in the same pass.  No shipped consumer does; `Inc-4b`'s next-match
        walk is the plausible first, and `ViewState.hits` is a `frozenset` one
        layer up for exactly this reason, so the two decisions now agree.

        THE MEMO IS SCOPED TO ONE PAINT PASS AND CANNOT GO STALE.  Three to four
        consumers reach this helper per repaint (`_view_state` from the render
        and again from `_unpainted_ids`, plus `_count_line`), and each used to
        resolve from scratch.  `_open_paint_pass` drops the memo at the START of
        every repaint, so the only way to read a stale order is to have already
        painted a stale screen -- and the memo is keyed on the graph OBJECT and
        the query text, so switching maps mid-pass cannot alias either.
        """
        if len(self.graph.nodes) > MAX_RENDER_NODES:
            return None
        memo = self._search_memo
        if memo is not None and memo[0] is self.graph and memo[1] == self.query_text:
            return memo[2]
        order = tuple(self._search_index().query(self.query_text))
        self._search_memo = (self.graph, self.query_text, order)
        return order

    def _open_paint_pass(self) -> None:
        """Drop the frame-scoped search memo; called at the top of every repaint.

        Deliberately a named seam rather than an inline assignment: the memo's
        correctness argument is "it lives for exactly one paint pass", and that
        claim is only checkable if every pass opens the same way.
        """
        self._search_memo = None

    def _search_hits(self) -> frozenset[str]:
        """The same resolution, in the shape a renderer receives.

        The bound's `None` and an empty order collapse to the same empty set
        HERE and only here, which is correct for this consumer and is not a
        reintroduction of the conflation `_count_line` had to unpick: above the
        bound the renderer paints no tree at all, so a hit set that highlights
        nothing is the truthful parameter.  The distinction matters only where
        something is DECLARED about the answer, which is the count line.
        """
        return frozenset(self._search_order() or ())

    def _view_state(self, w: int, h: int) -> ViewState:
        """The renderer's whole parameter surface, built in ONE place.

        Built once and reused by every call site, which is what closes the
        measured defect that motivated the parameter object: the export site
        passed `query` without `diff`, so an SVG exported during a diff silently
        lost its tinting while the on-screen canvas kept it.  With one
        constructor there is no second argument list to forget.
        """
        return ViewState(
            selected_id=self.nav.cursor,
            w=w,
            h=h,
            focus_owner=self._focus_owner(),
            hits=self._search_hits(),
            diff=self.diff if self.diff_active else None,
            pan_x=self.pan_x,
            pan_y=self.pan_y,
            folded=self.folded,
        )

    def refresh_canvas(self) -> None:
        # US-001, LLR-003.2: the node-change guard, at the ONE re-pointing site
        # every cursor mover ends in, and FIRST -- before the canvas, the crumb,
        # the rail or the inspector repaint -- so `stay` needs no repaint and the
        # inspector is never re-pointed under a draft (A-9).
        self._drop_orphan_draft()
        inspector = self.query_one("#map-inspector", FichaInspector)
        if inspector.has_draft() and self.nav.cursor != inspector.draft_node_id:
            target = self.nav.cursor
            self.nav.cursor = inspector.draft_node_id
            inspector.focus_after_rebuild(None)
            self._guard_draft(lambda: self._repoint(target))
        self._open_paint_pass()
        canvas = self.query_one("#map-canvas", Static)
        renderer = self._current_renderer()
        w, h = self._canvas_size()
        # Any renderer failure is a drawing problem, not an application problem:
        # this method runs inside the message pump, so an escape here kills the
        # app.  Scoped to the sink, not to the exception types known today --
        # which is why `_reclamp_pan` is INSIDE it rather than beside it: it
        # reaches the same `_tree_layout` the render does, and Inc-3 had moved it
        # out where the guard could not see it.
        try:
            self._reclamp_pan(w, h)
            # CAPTURED, not recomputed afterwards: `_reclamp_pan` can move
            # `pan_x`/`pan_y`, so a second `_view_state` call is not necessarily
            # the state this content was produced from -- and recording a state
            # the render did not use is exactly the desync the guard exists to
            # prevent.
            state = self._view_state(w, h)
            text = renderer.render(self.graph, state)
        except Exception as exc:
            state = self._view_state(w, h)
            text = darkside.Text.assemble(
                (" could not draw the map\n\n", f"bold {darkside.INK}"),
                (f" {darkside.plain(str(exc))}", darkside.MUT),
            )
        canvas.update(text)
        # EVERYTHING this content was produced from, recorded so the settle pass
        # can tell "already reconciled" from "needs a re-render" (`P1`).  Set
        # even on the degraded path: the failure text is what the canvas now
        # HOLDS for this state, and re-rendering would only replace a stated
        # degradation with a copy of itself.
        self._rendered_for = (renderer, state)
        pulse_cursor(canvas)

        tab = self.query_one(TabStrip)
        node = self.graph.nodes.get(self.nav.cursor or "")
        node_title = node.ficha.title if node else ""
        # EVERY crumb segment, not just the title: `_current_crumb` also carries
        # `map_id` and the link chain, which are file-derived too.  Found by the
        # frame-level half of `LLR-N06.2.3`'s census rather than by the
        # region-by-region half -- `TabStrip` is queried BY TYPE here, so it has
        # no id for a region sweep to enumerate, and a hostile ficha title was
        # reaching the composited frame through the breadcrumb with the same
        # `U+202E` the minimap leaked.
        tab.set_crumb([
            darkside.plain(part) for part in self._current_crumb() + [node_title]
        ])

        self.query_one("#map-inspector", FichaInspector).show(node, self.graph)
        self.query_one("#map-rail", OutlineRail).show(
            self.graph, self.nav.cursor, self.folded
        )
        # GUARDED LIKE ITS SIBLING, and the asymmetry was the finding: this call
        # sits past the `try` above, `_branch_coverage_glyph` and `_minimap_text`
        # both index `self.graph.nodes[...]` unchecked, and a dangling edge
        # raises `KeyError` from inside the message pump -- which kills the app,
        # exactly the shape the cycle guard was added for.  `_unpainted_ids` has
        # its own try/except; the minimap had none.  A coverage strip that
        # cannot be drawn is a drawing problem, so it degrades to empty.
        #
        # THIS GUARD DOES NOT SAVE THE APP ON A DANGLING EDGE, and the comment
        # above says only that this method stops leaking one.  Measured, the
        # composited paint of the same graph still dies: `OutlineRail.render`
        # indexes `graph.nodes[...]` unchecked too and raises at compositor
        # paint time, one sink over and on a different path.  That sink is
        # CARRIED, not closed -- see the arm in `tests/test_pan.py` that states
        # in terms what it asserts (the exception does not escape this method)
        # and what it does not (that the frame survives).
        strip = self.query_one("#map-minimap", Static)
        # The strip's OWN width, not the screen's: it is docked full-width today
        # but reading the screen would make this budget wrong the moment it is
        # not.  `size.width` is 0 before the first layout, and the fallback is
        # the screen rather than a constant so the pre-layout frame budgets from
        # something real.
        strip_width = strip.size.width or self.size.width
        try:
            minimap = self._minimap_text(strip_width)
        except Exception:
            minimap = darkside.Text("")
        strip.update(minimap)
        # LAST, and the position is load-bearing rather than incidental: the
        # declaration is computed from `painted_ids` over the state that was
        # just rendered, and `_focus_owner` -- which `_view_state` reads -- is
        # only settled once the side regions have been shown.  Moved ahead of
        # them during development and 6 arms went red on focus and on the rail's
        # byte identity.
        self.query_one(f"#{COUNT_REGION_ID}", Static).update(self._pagination_text())
        # ...AND THE LINE ABOVE CAN MOVE THE CANVAS THAT WAS PAINTED ABOVE IT.
        # `P1`, and the mechanism was measured rather than reasoned.  The strip
        # is content-height (`#map-pagination` carries `max-height` and no
        # `height`) while `#map-body` is `1fr`, so the strip's own row count
        # decides how many rows the canvas gets.  In `outline` the declaration is
        # absent, so this line renders 17 cells instead of layered's 36, stops
        # wrapping at terminal widths <= 34, and hands the canvas back a row --
        # AFTER `canvas.update` ran.  Nothing re-rendered, because this method
        # never armed the settle loop.  Measured on `legacy`: the canvas held 3
        # lines where the settled geometry asks for 4 at (30,16) and (32,16), 5
        # where it asks 6 at (24,20), 1 where it asks 2 at (34,14).  The return
        # trip is worse -- layered content written at outline's larger `h` into a
        # region that then SHRINKS overflows by a physical row, CLIPPING content
        # rather than leaving a blank one.
        #
        # `_declare_after_layout` already does the right thing: it re-renders at
        # the CURRENT geometry and chases the region until it stops moving.  It
        # was simply never armed from here.  Clearing `_declared_for` stops its
        # first pass mistaking this frame for one it already reconciled, and it
        # terminates on its own -- it re-schedules only while the region CHANGED,
        # so a settled layout costs exactly one no-op pass.
        self._declared_for = None
        self.call_after_refresh(self._declare_after_layout)
        self._paint_draft_hint()

    # -- the card draft: save, guard, failure (US-001) ---------------------
    # The inspector holds the draft; this screen, which owns the graph and the
    # store, is the only thing that writes it.  `widgets -> store` is banned.

    def _paint_draft_hint(self) -> None:
        """R8 / PDR C6: with the card hidden, the hint line carries the draft."""
        inspector = self.query_one("#map-inspector", FichaInspector)
        prefix = ""
        if self.inspector_hidden and inspector.has_draft():
            count = len(inspector.draft_values())
            prefix = f"● unsaved ({count}) · {hint_pair(SCOPE_MAP, 'save_draft')} · "
        self.query_one(MapHintLine).set_draft_prefix(prefix)

    def _drop_orphan_draft(self) -> None:
        """A draft whose node no longer exists cannot be saved or guarded: drop it,
        and say which fields were lost (LLR-004.2).  No guard opens for it."""
        inspector = self.query_one("#map-inspector", FichaInspector)
        if not inspector.has_draft() or inspector.draft_node_id in self.base_graph.nodes:
            return
        fields = ", ".join(sorted(inspector.draft_values()))
        inspector.clear_draft()
        self.notify(
            f"unsaved draft dropped · its card no longer exists · {darkside.plain(fields)}",
            severity="warning",
            markup=False,
        )

    def has_pending_draft(self) -> bool:
        """Whether this map holds a draft the operator has not saved or dropped."""
        return self.query_one("#map-inspector", FichaInspector).has_draft()

    def _guard_draft(self, proceed, *, on_hold=None) -> None:
        """The ONE decision point for leaving a draft (R-014, LLR-003.2).

        No draft: *proceed* now.  A guard already up: nothing (no second modal).
        Otherwise ask `save · discard · stay`; *proceed* runs only after `save`
        reached disk or after `discard`, and *on_hold* runs on `stay` or on a
        failed save (the guard holds at `stay`, LLR-004.2).
        """
        inspector = self.query_one("#map-inspector", FichaInspector)
        if not inspector.has_draft():
            proceed()
            return
        if self._draft_guard_open:
            return
        self._draft_guard_open = True
        node = self.base_graph.nodes.get(inspector.draft_node_id or "")
        title = node.ficha.title if node else ""

        def answered(choice: str | None) -> None:
            self._draft_guard_open = False
            if choice == "save":
                if self._save_draft():
                    proceed()
                elif on_hold is not None:
                    on_hold()
            elif choice == "discard":
                inspector.clear_draft()
                proceed()
            elif on_hold is not None:
                on_hold()

        self.app.push_screen(DraftGuardScreen(title, self.map_id), answered)

    def _repoint(self, target: str | None) -> None:
        """Move the cursor to *target* once the guard answered (PDR C2)."""
        if target not in self.graph.nodes:
            target = self.graph.root_id
        self.nav.cursor = target
        self.refresh_canvas()

    @staticmethod
    def _apply_field(ficha: Ficha, field: str, value: str) -> None:
        """Write one drafted value onto *ficha*.

        `A-111`: coerced with `plain()`'s rule before it reaches a graph -- a
        broken paste must not carry a lone surrogate to `save()`.  `field` is a
        schema key or one of the pseudo-keys `title` / `notes` / `state`, which
        live on the `Ficha` itself rather than in `fields`.
        """
        value = darkside.plain(value)
        if field == "title":
            ficha.title = value
        elif field == "notes":
            ficha.notes = value
        elif field == "state":
            ficha.state = value
        else:
            ficha.fields[field] = value

    def action_save_draft(self) -> None:
        self._save_draft()

    def _save_draft(self) -> bool:
        """Write the draft: one snapshot, one whole-graph write (LLR-001.4, 004.1).

        Copy-apply-write: the draft is applied to a COPY of the whole map
        (`base_graph`, never a focused subgraph -- R-1, LLR-004.4), so the
        in-memory graph never holds a value that is not on disk (A-10).

        On a failure, disk is the truth: the undo stack is restored exactly, the
        map is reloaded through the screen's own load path, and the draft is
        re-diffed against it, so a value that reached disk turns clean and the
        rest stay drafted (LLR-004.2).  Nothing on that path writes the map.
        """
        self._drop_orphan_draft()
        inspector = self.query_one("#map-inspector", FichaInspector)
        draft = inspector.draft_values()
        node_id = inspector.draft_node_id
        if not draft:
            return True
        refocus = self._focused_field_id(inspector)
        saved_stack = list(self._snapshots)
        self._push_snapshot(self.base_graph)
        candidate = copy.deepcopy(self.base_graph)
        for field, value in draft.items():
            self._apply_field(candidate.nodes[node_id].ficha, field, value)
        if _save_or_toast(self, self.store, self.map_id, candidate, toast=False):
            # The focused view, if any, shares these `Node` objects.
            node = self.base_graph.nodes[node_id]
            for field, value in draft.items():
                self._apply_field(node.ficha, field, value)
            inspector.clear_draft()
            self.refresh_canvas()
            self._refocus_field(inspector, refocus)
            self._event_toast("saved", darkside.plain(node.ficha.title or node.id))
            return True

        # `_push_snapshot` may have evicted the oldest entry at `UNDO_DEPTH`, so
        # the stack is restored whole, never popped.
        self._snapshots[:] = saved_stack
        cursor = self.nav.cursor
        try:
            graph = self.store.load(self.map_id)
            error = darkside.plain(getattr(self, "_last_save_error", "") or "error")
            message = (
                f"could not save {darkside.plain(self.map_id)!r} ({error}) · draft kept · "
                f"{self._seat_glyph('save_draft')} to retry"
            )
        except Exception:  # noqa: BLE001 -- any reload failure keeps the pre-save map.
            # `base_graph` was never touched by this save (the draft went onto a
            # copy), so re-establishing it IS the pre-save graph.  No store call.
            graph = self.base_graph
            discard = next(b for b in bindings_for(SCOPE_DRAFT) if b.action == "discard")
            message = f"could not reload · draft kept · leaving needs {discard.glyph} ({discard.label})"
        self._establish_graph(graph, cursor=cursor)
        self.refresh_canvas()
        if self.nav.cursor == node_id:
            self._refocus_field(inspector, refocus)
        self.notify(darkside.plain(message), severity="error", markup=False)
        return False

    @staticmethod
    def _focused_field_id(inspector: FichaInspector) -> str | None:
        """The id of the inspector field holding focus, if one does."""
        focused = inspector.screen.focused
        if isinstance(focused, Input) and focused.parent is inspector:
            return focused.id
        return None

    @staticmethod
    def _refocus_field(inspector: FichaInspector, widget_id: str | None) -> None:
        """PDR C7: after `ctrl+s` from inside a field, typing continues there.

        Queued on the inspector AFTER the rebuild `refresh_canvas` queued, so it
        focuses the remounted field, not the removed one.
        """
        if widget_id is None:
            return

        def restore_focus() -> None:
            for field in inspector.query(f"#{widget_id}"):
                field.focus()

        inspector.call_next(restore_focus)

    def on_field_input_left(self, event) -> None:
        """`escape` inside a field returns focus to the map, keeping the value."""
        event.stop()
        self.set_focus(None)
        self.query_one(HintLine).set_hint(map_hint())
        self._paint_draft_hint()

    # -- attachments (US-N02) ----------------------------------------------
    def on_ficha_inspector_attachment_activated(
        self, event: FichaInspector.AttachmentActivated
    ) -> None:
        """Open an attachment through the one OS-handler boundary.

        The refusal is always shown: a dropped status word would make a refused
        launch indistinguishable from a successful one (LLR-N02.9).
        """
        event.stop()
        node = self.graph.nodes.get(event.node_id)
        if node is None or self.store is None:
            return
        if not 0 <= event.index < len(node.ficha.attachments):
            return
        att = node.ficha.attachments[event.index]
        refusal = _path_refusal(att.path, self.store.workspace) if att.kind == "file" else None
        if refusal is not None:
            # `U1` / `V1`: a target outside the allow-list (a sidecar can hold any text) or outside the
            # workspace is not looked at and not named; the same fixed sentences as the add prompt.
            self.notify(darkside.plain(refusal), severity="warning", markup=False)
            return
        status = open_external(
            att.kind, att.path, workspace=self.store.workspace,
            launcher=getattr(self.app, "attachment_launcher", None),
        )
        # Both branches carry file-derived text, so both are coerced.  `notify`
        # parses markup by default in textual 8.2.8 (Toast.render calls
        # Content.from_markup), so a hostile path could crash the toast or, worse,
        # REWRITE the refusal text the operator is reading — defeating the point
        # of showing the real target at the exact moment it matters.
        shown = darkside.plain(att.path)
        if status == OSOPEN_OK:
            self._event_toast("opened", darkside.plain(att.caption or att.path))
        elif status == ATTACHMENT_HARD_LINKED:
            # `INC9P-SEC-F3`: the status is the fixed sentence; it names nothing, so the path is not appended.
            self.notify(darkside.plain(status), severity="warning", markup=False)
        else:
            self.notify(darkside.plain(f"{status}: {shown}"), severity="warning", markup=False)

    def on_ficha_inspector_attachment_add_requested(
        self, event: FichaInspector.AttachmentAddRequested
    ) -> None:
        event.stop()
        node = self.graph.nodes.get(event.node_id)
        if node is None or self.store is None:
            return

        def on_target(target: str | None) -> None:
            if not target:
                return
            # `A-111`: coerced before it reaches the graph, same rule as
            # `plain()` — the prompt is a real `Input`, not a hostile file.
            target = darkside.plain(target)
            kind = "url" if "://" in target else "file"
            refusal = _path_refusal(target, self.store.workspace) if kind == "file" else None
            if refusal is not None:
                # `U2`: refused at ADD time, nothing stored, no undo snapshot taken.
                self.notify(darkside.plain(refusal), severity="warning", markup=False)
                return
            self._push_snapshot()
            node.ficha.attachments.append(Attachment(kind=kind, path=target))
            if not _save_or_toast(self, self.store, self.map_id, self.graph):
                return
            self.base_graph = self.graph
            self.refresh_canvas()
            self._event_toast("attachment added", darkside.plain(target))

        self.app.push_screen(
            _PromptScreen("attachment path or url", "docs/record.pdf"), callback=on_target
        )

    def on_ficha_inspector_attachment_remove_requested(
        self, event: FichaInspector.AttachmentRemoveRequested
    ) -> None:
        event.stop()
        node = self.graph.nodes.get(event.node_id)
        if node is None or self.store is None:
            return
        if not 0 <= event.index < len(node.ficha.attachments):
            return
        removed = node.ficha.attachments.pop(event.index)
        self._push_snapshot()
        if not _save_or_toast(self, self.store, self.map_id, self.graph):
            return
        self.base_graph = self.graph
        self.refresh_canvas()
        self._event_toast(
            "attachment removed", darkside.plain(removed.caption or removed.path)
        )

    def action_add_attachment(self) -> None:
        self.query_one("#map-inspector", FichaInspector).request_add_attachment()

    def action_remove_attachment(self) -> None:
        self.query_one("#map-inspector", FichaInspector).request_remove_attachment()

    UNDO_DEPTH = 20

    @property
    def _snapshots(self) -> list[bytes]:
        """This map's undo history, held by the App so it outlives the screen.

        Keyed by `map_id`: one global stack would let an undo taken in map B
        restore a snapshot of map A, which is data loss wearing a feature's
        clothes.
        """
        return self.app.undo_stacks.setdefault(self.map_id, [])

    def _push_snapshot(self, graph: Graph | None = None) -> None:
        """Push *graph* (default: the graph on show) onto this map's undo stack.

        The draft save passes `base_graph`: under focus the graph on show is a
        subtree, and undoing a save must restore the whole map (R-1).
        """
        if self.store is None:
            return
        graph = self.graph if graph is None else graph
        mmd = dump_mermaid(graph)
        sidecar = self.store._build_sidecar(graph)
        import yaml

        yml = yaml.safe_dump(sidecar, sort_keys=False, allow_unicode=True)
        stack = self._snapshots
        stack.append(json.dumps({"mmd": mmd, "yml": yml}).encode())
        del stack[: max(0, len(stack) - self.UNDO_DEPTH)]

    def _pop_snapshot(self) -> None:
        if not self._snapshots:
            self.notify("nothing to undo")
            return
        import yaml

        blob = self._snapshots.pop()
        data = json.loads(blob.decode())
        graph = self.store._graph_from_sidecar(data["mmd"], yaml.safe_load(data["yml"]) or {})
        self.graph = graph
        self.base_graph = graph
        if self.nav.cursor not in self.graph.nodes:
            self.nav.cursor = self.graph.root_id
        if not _save_or_toast(self, self.store, self.map_id, self.graph):
            return
        self.refresh_canvas()
        self._event_toast("undo", "state restored")

    def action_next_sibling(self) -> None:
        nxt = self.nav.next_sibling()
        if nxt:
            self.nav.cursor = nxt
            self.refresh_canvas()

    def action_prev_sibling(self) -> None:
        prv = self.nav.prev_sibling()
        if prv:
            self.nav.cursor = prv
            self.refresh_canvas()

    def action_child(self) -> None:
        ch = self.nav.first_child()
        if ch:
            self.nav.cursor = ch
            self.refresh_canvas()

    def action_parent(self) -> None:
        p = self.nav.parent()
        if p:
            self.nav.cursor = p
            self.refresh_canvas()

    def action_open_ficha(self) -> None:
        node = self.graph.nodes.get(self.nav.cursor or "")
        if node is None:
            return
        linked = node.linked_map_id()
        if linked:
            crumb_back = self._current_crumb() + [node.ficha.title or node.id]
            self._guard_draft(lambda: self.app.push_screen(MapScreen(linked, source_crumb=crumb_back)))
            return
        self.app.push_screen(_FichaScreen(node, self.graph))

    def action_search(self) -> None:
        inp = self.query_one("#search-input", Input)
        inp.disabled = False
        inp.display = True
        inp.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self.query_text = event.value
            event.input.display = False
            event.input.disabled = True
            self.focus()
            self.refresh_canvas()
            # AFTER the repaint, deliberately: the hint then describes the
            # frame the operator is now looking at, and the order it reads is
            # the one `refresh_canvas` just resolved rather than a second
            # resolution beside it.
            #
            # `None` IS NO LONGER EXCLUDED HERE (`LLR-N07.3.4`).  Above the
            # renderer's bound a query is live and `esc` clears it, so the hint
            # has an affordance to promise; `_search_hint` grew the third arm
            # that says what is suspended instead of `sin coincidencias`, which
            # would declare an empty answer over a graph that may hold thousands
            # of matches.  The guard below is the shared predicate, which now
            # asks about the QUERY -- so the blank query is still excluded and
            # the bound no longer is.
            order = self._search_order()
            if self._search_is_live():
                self.query_one(HintLine).set_hint(self._search_hint(order))
            else:
                self.query_one(HintLine).set_hint(map_hint())

    def on_input_blurred(self, event: Input.Blurred) -> None:
        if event.input.id == "search-input":
            event.input.display = False
            event.input.disabled = True
            self.focus()

    # -- US-N07 · the walk over the live matches (`#D5b`, `HLR-N07.3`) ------
    def _seat_row(self, action: str) -> KeyBinding | None:
        """The seat's row for *action* in this screen's scope, at CALL time.

        Never captured at import.  Everything the surfaces below paint about a
        chord -- the glyph in the hint line, the glyph and the label in the
        rebind declaration -- is read through here, so a later rebind reaches
        the painted string without a second edit.  This increment is itself the
        proof that the hazard is real: `n` meant `next_gap` one commit ago.
        """
        for binding in bindings_for(self.KEY_SCOPE):
            if binding.action == action:
                return binding
        return None

    def _seat_glyph(self, action: str) -> str:
        row = self._seat_row(action)
        return row.glyph if row else ""

    def _seat_label(self, action: str) -> str:
        row = self._seat_row(action)
        return row.label if row else ""

    def _field_hint(self) -> str:
        """The hint while an inspector field holds the keyboard (U2).

        Typing drafts the field and `j` types a letter, so the map-navigation
        hint would lie; this names the save key from the seat instead
        (LLR-005.2)."""
        save = self._seat_glyph("save_draft")
        return f"type to draft · {save} {self._seat_label('save_draft')} · esc leave field"

    def _search_hint(self, hits: tuple[str, ...] | None) -> str:
        """`UX-Q3-b`'s hint for a live search, glyphs READ FROM THE SEAT.

        Takes the resolved order as an ARGUMENT rather than resolving again, so
        the hint cannot describe a different answer from the one its caller
        acted on -- the same "one resolution per frame" rule `_search_order`'s
        memo exists to enforce, applied one surface up.
        """
        clear = f"{self._seat_glyph('back_or_home')} clear"
        if hits is None:
            # Above the renderer's bound.  `sin coincidencias` here would be the
            # lying affordance one surface over from the one `_count_line`
            # refuses to paint -- it declares an empty answer over a graph that
            # may hold thousands of matches.  The state comes first and the
            # affordance last, which is the shape the empty-state hint below
            # already uses, and `esc` is promised because `esc` now works here.
            return f"{SEARCH_SUSPENDED_NOTICE} · {clear}"
        if not hits:
            return f"no matches · {clear}"
        return (
            f"{self._seat_glyph('next_hit')} next · "
            f"{self._seat_glyph('prev_hit')} previous · {clear}"
        )

    def _search_is_live(self) -> bool:
        """What BOTH `esc` and the hint line mean by "a search is live".

        ONE PREDICATE, BOTH CALLERS -- unchanged from `Inc-4b`.  WHAT IT READS
        CHANGED (`LLR-N07.3.4`, `#D43`), and this reverses `Inc-4b`'s version.

        It used to be `query_text.strip() and _search_order() is not None`, so
        above the renderer's bound it answered `False` and `esc` popped the
        screen on the first press.  Both gates approved that ON THE PREMISE that
        nothing was painted to clear.  `#D43` rejects the premise: the count
        region now declares the query at every graph size, so there IS something
        to clear, and a chord whose meaning varies with the size of the map is a
        lying affordance with extra steps -- the operator learns a rule that
        silently stops holding on a large map, and learns it by losing their
        place.

        SO IT READS THE QUERY, WHICH IS THE STATE, AND NOT THE RESOLUTION, WHICH
        IS A RENDERING DETAIL.  `M-N07.3.4-a` is exactly this method left reading
        the resolution while the region is taught to declare the query, and the
        acceptance reddens it by asserting `esc` across BOTH regimes in one node.

        It no longer reaches the search resolution at all, which is why it and
        `action_back_or_home` were REMOVED from `test_search.py`'s
        `_PASS_FREE_READERS` rather than left there: that arm pins its set in
        both directions, and a stale exemption fails it.
        """
        return bool(self.query_text.strip())

    def _declare_rebind(self) -> None:
        """Say ONCE that `n` changed hands (`AT-051b`).

        Every string comes from the SEAT.  A typed copy would go on announcing a
        rebind that a later increment moved again, which is the failure the
        declaration exists to prevent, reproduced inside the declaration.
        Between this increment and Inc-8 the relocated `next_gap` is
        undiscoverable through `?` -- its `view` group sits below the legend's
        fold at the declared size -- so this toast is the only painted route to
        its new home.
        """
        self._event_toast(
            f"{self._seat_glyph('next_hit')} · {self._seat_label('next_hit')}",
            f"{self._seat_label('next_gap')} now on {self._seat_glyph('next_gap')}",
        )

    def _walk_toast(self, declaring: bool, label: str, detail: str) -> None:
        """One toast slot, and the one-time declaration outranks it on press 1.

        `E1b` and `E1c` are painted on every later press; on the very first they
        would hide the fact that the KEY changed meaning, which is the more
        urgent of the two things to say and the only one that is ever said.
        """
        if declaring:
            self._declare_rebind()
            return
        self._event_toast(label, detail)

    def _unfold_onto(self, nid: str) -> list[str]:
        """Open every folded branch that hides *nid*; return what was opened.

        `LLR-N06.2.4`.  Landing the selection inside a fold moves it somewhere
        the operator cannot see, which is the silent state change US-N06
        forbids.  The branch is NOT re-closed when the walk moves past it: that
        would undo, unasked, the only thing that made the previous step legible.
        The child index is built once for the same reason `search.tree_order`
        builds one -- `Graph.children_of` is a full scan of `graph.edges`.
        """
        if not self.folded:
            return []
        kids: dict[str, list[str]] = {}
        for edge in self.graph.edges:
            kids.setdefault(edge.parent_id, []).append(edge.child_id)
        opened: list[str] = []
        for start in sorted(self.folded):
            seen: set[str] = set()
            stack = list(kids.get(start, ()))
            while stack:
                cid = stack.pop()
                if cid in seen:
                    continue
                seen.add(cid)
                stack.extend(kids.get(cid, ()))
            if nid in seen:
                opened.append(start)
        self.folded = self.folded - set(opened)
        return opened

    def _branch_name(self, nid: str) -> str:
        """What the hint line calls a branch: its title, or its id if it has none.

        Lifted out of `_walk_hits` rather than written inline, and the reason is
        mechanical: the acceptance asserts BY AST that the walk handler contains
        no boolean expression, because `search_hits or lens_matches` is the shape
        `M-N07.3-a` takes.  A `title or nid` fallback is harmless and is the same
        shape, so it lives here instead of weakening the rule to allow it.

        Through `plain()`: the title is file-derived and the hint line is a
        surface this batch touches (`HLR-COERCE`).

        The `.get` is not defensive padding: a folded id that is an edge parent
        with no `Node` entry raises `KeyError` on the keypress, and while the
        shipped loader synthesises a node for every `.mmd` edge endpoint (so no
        FILE reaches it), the fold set is keyed on ids, not on nodes.  Falling
        through to the id arm costs one call and removes a crash from a path
        that has no other error handling.
        """
        node = self.graph.nodes.get(nid)
        title = node.ficha.title if node else ""
        if title:
            return darkside.plain(title)
        return darkside.plain(nid)

    def _hint_with_opened(self, hint: str, opened: list[str], width: int) -> str:
        """Append `abrió «…»` to *hint*, BOUNDED, and BEHIND the affordances.

        Branch titles are file-derived: unbounded in length, and one walk can
        open several nested folds at once.  `HintLine` WRAPS rather than clips,
        so an unbounded segment does not overflow the strip -- it grows the
        strip and takes the rows from the canvas.  Measured at the declared
        118x34 with a ~2000-character title and one real `n`: the strip went to
        18 rows, the map to ONE, and `n siguiente · N anterior · esc limpiar`
        left the painted frame -- including `esc limpiar`, the affordance `#D38`
        newly promises.  So the increment that introduced the recovery route
        also introduced the way to lose it.

        TWO INDEPENDENT GUARDS, because either alone is insufficient.  Order:
        the names go AFTER the affordances, so a wrap that still happened could
        only push the ANNOUNCEMENT off, never the keys.  Budget: the name gets
        the row's remainder, capped, so no wrap happens at all -- a FIXED cap
        was tried first and measured wrapping at 80 columns, where the whole
        strip then left the frame.  With no room to say anything the
        announcement is dropped: the operator can see the branch opened, and
        losing `esc` is the worse of the two failures.
        """
        if not opened:
            return hint
        names = ", ".join(self._branch_name(nid) for nid in opened[:_HINT_BRANCHES])
        if len(opened) > _HINT_BRANCHES:
            names += f" +{len(opened) - _HINT_BRANCHES}"
        room = min(_HINT_BRANCH_CELLS, width - len(hint) - _HINT_NAME_OVERHEAD)
        if room < _HINT_NAME_MIN_CELLS:
            return hint
        # `fit` truncates to display CELLS and re-coerces; its padding is
        # stripped because this sits inside quotes, not in a column.
        return f"{hint} · opened «{darkside.fit(names, room).rstrip()}»"

    def _walk_hits(self, step: int) -> None:
        """Move the selection to the next (or previous) match, wrapping both ways.

        ONE SOURCE OF "WHAT MATCHES", AND NO FALLBACK (`C-D6a`).  The order comes
        from `_search_order` and from nowhere else.  The named weaker variant
        `M-N07.3-a` is this walk written over two result sets joined by `or`
        with neither ever cleared: it passes `AT-022` whenever only one of them
        is populated -- which is every single-feature test -- and the two diverge
        silently the first time an operator uses both.  There is no second set in
        this batch (`#D23` defers the lens), so the invariant "submitting a
        search clears the lens matches" would be GREEN BEFORE ANY CODE WAS
        WRITTEN, which is the vacuous check this batch exists to stop.  It is
        closed STRUCTURALLY instead: this method reads exactly one resolution and
        contains no boolean fallback, and `test_search.py` asserts both BY AST.
        What that buys, stated exactly: the two NAMED shapes of `M-N07.3-a` are
        structurally unavailable here rather than merely undetected.  It is not
        a proof that no second result set can exist -- one named outside the
        arm's vocabulary and joined by concatenation would satisfy both
        assertions.

        THE ORDER IS THE ONE THE FRAME ON SCREEN WAS PAINTED FROM.  `_search_order`
        is memoised per paint pass and keyed on the graph object and the query
        text, and a walk changes neither, so the memo of the last frame is the
        same value a fresh resolution would return.  The repaint that follows
        opens its own pass; this method is registered in the acceptance's
        exemption table with that reason rather than opening one of its own.
        """
        hits = self._search_order()
        declaring = not self._rebind_declared
        self._rebind_declared = True
        if not self.query_text.strip():
            # `E1b` -- nothing was ever asked.  A blank or whitespace-only query
            # is the SAME state (`LLR-N07.3.3`) and the count line already paints
            # the two identically.  The body reports the STATE rather than
            # prescribing the `/` route: `#D6` made the route conditional, so a
            # body naming it is accidentally true today and misdirection the
            # increment a second producer lands.
            self._walk_toast(
                declaring,
                "no active search",
                "no matches to step through",
            )
            return
        if hits is None:
            # Above the renderer's bound.  `E1c`'s body here would declare "no
            # aparece en este mapa" over a graph that may hold thousands of
            # matches, which is why this branch exists at all.
            #
            # THE LABEL WAS `búsqueda sin evaluar` AND IS NOW FALSE
            # (`LLR-N07.3.4`, which is the clause that finally OWNS this string).
            # The count region evaluates the search at every graph size now and
            # paints the whole-graph figure, so a toast saying the search was not
            # evaluated contradicts the row above it.  What is actually suspended
            # is the thing the operator just asked for -- the walk -- and that is
            # what the toast now names, in the same words
            # `SEARCH_SUSPENDED_NOTICE` uses on the region.
            #
            # THE COUNT IS DELIBERATELY NOT REPEATED HERE.  The region carries it
            # persistently, which is the point of `#D43`; a toast that repeated
            # it would be a second surface making the same claim, and reading it
            # would mean calling a counter from inside the one handler `C-D6a`
            # pins by AST to a single resolution source.
            self._walk_toast(
                declaring,
                "walk suspended",
                f"the map exceeds the limit of {MAX_RENDER_NODES} nodes",
            )
            return
        if not hits:
            # `E1c` -- asked, and answered empty.  The body interpolates the
            # OPERATOR'S query, which makes this toast a coercion sink: measured,
            # `darkside.plain` strips a control byte and a right-to-left
            # override where `Text.assemble` leaves the override alive, and an
            # override reverses the toast's own sentence.
            self._walk_toast(
                declaring,
                "0 matches",
                f"«{darkside.plain(self.query_text)}» is not in this map",
            )
            return
        if self.nav.cursor in hits:
            index = (hits.index(self.nav.cursor) + step) % len(hits)
        else:
            index = 0 if step > 0 else len(hits) - 1
        target = hits[index]
        opened = self._unfold_onto(target)
        self.nav.cursor = target
        self.refresh_canvas()
        line = self.query_one(HintLine)
        line.set_hint(self._hint_with_opened(self._search_hint(hits), opened, line.size.width))
        if declaring:
            self._declare_rebind()

    def action_next_hit(self) -> None:
        self._walk_hits(1)

    def action_prev_hit(self) -> None:
        self._walk_hits(-1)

    def action_toggle_focus(self) -> None:
        if self.focus_active:
            self.graph = self.base_graph
            self.focus_active = False
            self.nav = NavigationModel(self.graph)
            if self.nav.cursor not in self.graph.nodes:
                self.nav.cursor = self.graph.root_id
            self.refresh_canvas()
            return

        if self.nav.cursor is None or self.nav.cursor not in self.graph.nodes:
            return
        self._push_snapshot()
        self.graph = self.base_graph.focus(self.nav.cursor)
        self.focus_active = True
        self.nav = NavigationModel(self.graph)
        self.refresh_canvas()

    def action_toggle_outline(self) -> None:
        self.outline_mode = not self.outline_mode
        self.radial_mode = False
        self._clear_pan_hint()
        self.refresh_canvas()

    def action_toggle_radial(self) -> None:
        self.radial_mode = not self.radial_mode
        self.outline_mode = False
        self._clear_pan_hint()
        self.refresh_canvas()

    def _clear_pan_hint(self) -> None:
        """Drop `PAN_INERT_HINT` when the view changes underneath it.

        THE HINT IS A STATEMENT ABOUT THE VIEW, so it stops being true the
        moment the view changes -- and `_pan`'s own clear is reachable only on a
        SUCCESSFUL pan, which a non-panning view never performs.  Without this
        the hint LATCHES: press a pan key in radial, press `r` back to layered,
        and the strip still reads "esta vista no se desplaza" while standing in
        the view that does scroll.  Not merely stale -- FALSE in the view
        displaying it.

        This is the defect `_pan` already records one branch down ("the hint is
        set on a no-op and nothing ever unset it ... it latched on the first
        sideways press and then sat there describing every LIVE `J`/`K` as an
        edge the operator had not reached"), reintroduced on a new surface by
        the branch added to fix `PAN-1`.  Cleared HERE, at the seam where the
        property stops holding, rather than on the next successful pan.

        Scoped to the pan hint alone: an unconditional clear would swallow
        whatever another handler had just declared.

        READS `HintLine.text`, THE STORED VALUE, rather than rendering the
        widget to inspect it.  A zero-arg `render()` here would be a WIDGET-
        protocol call in PRODUCTION code -- correctly outside the `A3`, but the
        census pins that population and a new production site changes it; the
        first version of this method did exactly that and the `A3` pins caught
        it.  The stored value is also the honest source: it is what `set_hint`
        wrote, with no styling or wrapping in between.
        """
        hint = self.query_one(HintLine)
        if hint.text in (PAN_INERT_HINT, PAN_EDGE_HINT):
            hint.set_hint(self._resting_hint())

    def _resting_hint(self) -> str:
        """What the hint line says when no handler has declared anything: the live search's hint while a
        query is live, else the map's.  `_pan` and `_clear_pan_hint` restore THIS, never a blank
        (`PR-QA-F3`: a blank hint after a pan is a map that stopped saying what the keys are)."""
        if self._search_is_live():
            return self._search_hint(self._search_order())
        return map_hint()

    def action_toggle_diff(self) -> None:
        if self.diff_active:
            self.diff_active = False
            self.refresh_canvas()
            self.notify("diff hidden")
            return
        if self.store is None:
            return
        diff = git_diff(self.map_id, self.store)
        if diff is None:
            self.notify("no diff available (is the map in git?)")
            return
        self.diff = diff
        self.diff_active = True
        self.refresh_canvas()
        added = len(diff.added)
        removed = len(diff.removed)
        changed = len(diff.changed)
        self.notify(darkside.plain(f"diff: +{added} -{removed} ~{changed}"), markup=False)

    def action_coverage(self) -> None:
        def on_select(node_id: str | None) -> None:
            if node_id is None or node_id not in self.graph.nodes:
                return
            self._goto_gap(node_id)

        self.app.push_screen(CoverageScreen(self.graph, self.map_id), callback=on_select)

    # -- coverage worklist (US-N04) ----------------------------------------
    def _incomplete_order(self) -> list[str]:
        """Nodes with a missing required field, in the coverage report's order.

        Walks the tree the same way `CoverageScreen` does, so "next" in the
        worklist means the same thing as "next row" in the report.  Consumes
        `Ficha.missing_required`, the model's single owner of what is missing.
        """
        out: list[str] = []
        if self.graph.root_id is None:
            return out
        visited: set[str] = set()
        stack = [self.graph.root_id]
        while stack:
            nid = stack.pop()
            if nid in visited or nid not in self.graph.nodes:
                continue
            visited.add(nid)
            if self.graph.nodes[nid].ficha.missing_required(self.graph.schema):
                out.append(nid)
            for cid in reversed(self.graph.children_of(nid)):
                if cid not in visited:
                    stack.append(cid)
        return out

    def _goto_gap(self, node_id: str) -> bool:
        """Move the cursor to *node_id* and focus its first missing field."""
        if node_id not in self.graph.nodes:
            return False
        self.nav.cursor = node_id
        if self.inspector_hidden:
            self.inspector_hidden = False
            self._apply_region_visibility()
        # Ask for the focus BEFORE refreshing: the inspector applies the request
        # at the end of the rebuild that creates the rows, so the two are ordered
        # causally instead of racing on frame timing.
        missing = self.graph.nodes[node_id].ficha.missing_required(self.graph.schema)
        inspector = self.query_one("#map-inspector", FichaInspector)
        inspector.focus_after_rebuild(missing[0].key if missing else None)
        self.refresh_canvas()
        if missing:
            # The save key is READ FROM THE SEAT (LLR-005.2): `↵` keeps the draft
            # and leaves the field (R7), so naming it here would advertise a save
            # that does not happen -- the defect US-N03 exists to remove.
            save = self._seat_glyph("save_draft")
            self.query_one(HintLine).set_hint(
                f"fill in «{missing[0].label}» · {save} {self._seat_label('save_draft')}"
                " · esc leave field",
                save,
            )
        return True

    def action_next_gap(self) -> None:
        """Advance to the next node that is missing a required field.

        Wraps once.  When nothing anywhere is missing it says so, rather than
        cycling silently on the same node forever.
        """
        order = self._incomplete_order()
        if not order:
            self._event_toast("coverage complete", "no required field is missing")
            return
        if self.nav.cursor in order:
            idx = (order.index(self.nav.cursor) + 1) % len(order)
        else:
            idx = 0
        self._goto_gap(order[idx])

    #: Above this many cells the export ANNOUNCES ITSELF before it freezes the
    #: pump.  A JUDGEMENT, named as one, and deliberately NOT derived from a
    #: time: this seam's whole lesson is that cost is not a function of cells,
    #: so any cells-to-seconds threshold would be that same false universal a
    #: third time.  The notice therefore states the EXTENT and promises no
    #: duration.  Roughly a quarter of the budget, which on the measured shapes
    #: is about where an export stops being instantaneous on any terminal.
    EXPORT_DECLARE_CELLS = 90_000

    #: How long the export yields so the notice can actually REACH THE SCREEN.
    #: MEASURED, and it is why this action is `async`.  A notice that arrives
    #: after the freeze it warns about is an apology, not a declaration -- and
    #: three cheaper shapes were measured and REJECTED: notifying then blocking
    #: in the same handler paints the toast 404 ms LATE, `call_after_refresh`
    #: 403 ms late, and an async action yielding with `sleep(0)` 403 ms late.
    #: Only a real yield lets the pump mount and paint the toast first (+50 ms,
    #: measured).  So declaring the wait DOES need async, and this constant is
    #: the whole of what that costs.
    EXPORT_DECLARE_PAUSE = 0.05

    async def action_export_svg(self) -> None:
        if self.store is None:
            return
        try:
            size = self.size or self.app.size
            renderer = self._current_renderer()
            # THE BUDGET IS CHECKED FIRST, so a refusal never announces a wait
            # it is not going to take.
            state = self._export_view_state(size)
            cells = max(0, state.w) * max(0, state.h)
            if cells >= self.EXPORT_DECLARE_CELLS:
                # A FREEZE NOBODY WAS TOLD ABOUT IS THIS BATCH'S OWN DEFECT
                # CLASS APPLIED TO TIME INSTEAD OF CONTENT -- hidden without
                # being declared.  The export is bounded and useful now, but
                # bounded is not instant: the worst shape the budget admits
                # still costs seconds on a short terminal, and a TUI that stops
                # answering with no indication reads as hung rather than busy.
                self.notify(
                    darkside.plain(f"exporting {cells} cells; this may take a moment."),
                    markup=False,
                )
                await asyncio.sleep(self.EXPORT_DECLARE_PAUSE)
            text = renderer.render(self.graph, state)
            path = self.store.workspace / f"{self.map_id}.svg"
            save_svg(text, path)
            self._event_toast("exported", path.name)
        except ExportTooLarge as too_large:
            # A REFUSAL, AND IT NAMES THE ROUTE FORWARD.  Nothing is written --
            # see `_export_view_state` for why a partial artifact is the one
            # outcome this path may not produce.  The message carries the
            # measured extent, the budget, and the chord that makes the map
            # small enough, because a refusal the operator cannot act on is a
            # capability regression rather than a safeguard.
            #
            # AND IT DECLARES THE STALE FILE, because refusing to write leaves
            # whatever the LAST export wrote sitting at the very path the
            # success toast names.  The operator is told the export refused;
            # without this they are not told that the file still there is OLD --
            # and a stale artifact at the expected path is this batch's own
            # defect family (`B-68`: a file that looks current and is not),
            # reintroduced one seam over by the increment that closed it.
            #
            # DECLARED RATHER THAN DELETED, and that is the correct answer
            # rather than the cautious one.  The standard is that nothing is
            # hidden without being DECLARED -- not that nothing stale exists --
            # so an old file the operator has been told about is declared.  And
            # deleting their file on their behalf, on a refusal, with no
            # confirmation is the destructive act `US-N05` already ruled
            # against: silently deleting would break a standing ruling in order
            # to soften a lesser one.
            #
            # THE SENTENCE IS CONDITIONAL BECAUSE IT MUST NEVER BE FALSE -- AND
            # ITS FIRST FORM WAS FALSE ANYWAY.  It read "... es de una
            # exportación anterior y ya no refleja este mapa", guarded by
            # `path.exists()`.  But EXISTENCE IS NOT STALENESS, and the guard and
            # the sentence were therefore two different claims.  Measured: export
            # a map, change NOTHING about the graph, then make the same map
            # exceed the budget -- the artifact on disk is still a faithful
            # export of that exact graph, and the refusal called it stale.
            #
            # So it now says only what `exists()` licenses: nothing was written,
            # a file is there, and an earlier export wrote it.  Whether that file
            # still matches the map is something this code does not know and must
            # not assert.  Telling the operator a CURRENT file is stale is the
            # same category of error as letting them believe a STALE file is
            # current -- both are the artifact misdescribing itself, which is the
            # family `B-68` names.
            # `CR17-F4`, and it is this fix's OWN principle turned on it. The
            # sentence was justified as saying "only what `exists()` licenses"
            # -- and then said an EXPORT wrote the file, which `exists()` does
            # not license: a directory, or a file the operator dropped there,
            # would have been called a previous export. `is_file()` licenses
            # "el archivo"; nothing licenses a claim about its author, so no
            # claim about its author is made. What the operator actually needs
            # is that NOTHING WAS WRITTEN and what is there is not this export,
            # and both of those are true whoever put it there.
            # `E2` (operator, 2026-10-02) then asked the sentence to say where the file comes from, so it now does:
            # that claim is the operator's ruling, not something `is_file()` licenses.
            path = self.store.workspace / f"{self.map_id}.svg"
            stale = ""
            if path.is_file():
                stale = (
                    f" Nothing was written; {path.name} on disk is from an earlier export."
                )
            self.notify(
                darkside.plain(f"map too large to export: {too_large.cells} cells, "
                f"limit {too_large.limit}. Focus a subtree with f and export that view."
                f"{stale}"),
                severity="warning",
                markup=False,
            )
        except Exception as e:
            self.notify(darkside.plain(f"export failed: {type(e).__name__}"), severity="error", markup=False)

    #: How many times `_export_view_state` may grow the canvas looking for the
    #: size at which the whole map fits.  MEASURED, not guessed, and measured by
    #: COUNTING THE CALLS THIS LOOP MAKES rather than by replaying it: across
    #: the pan fixture, 200- and 1000-long chains, 200/500/4001-wide fanouts, a
    #: 50x400-character title set and three wide-and-deep shapes, the extent
    #: settles after exactly ONE growth step -- `layered._geometry` stops
    #: shrinking `card_w` once the width is generous, so the second probe
    #: already fits.
    #:
    #: AN INDEPENDENT PASS MEASURED TWO on its own shape set, and that number is
    #: named here rather than reconciled away: six is headroom over both, and a
    #: docstring quoting only the author's own figure is the declaration family
    #: again.  Six is headroom for a shape nobody has measured, not a prediction
    #: that six will ever be needed -- and the exhaustion path below REFUSES, so
    #: being wrong about it costs a refusal rather than a cropped artifact.
    EXPORT_EXTENT_STEPS = 6

    #: The export's area budget, in CELLS, and the number is DERIVED.
    #:
    #: IN CELLS BECAUSE CELLS ARE WHAT COSTS.  `Canvas.rows()` walks a dense
    #: `w x h` grid, so export cost tracks the map's BOUNDING-BOX AREA and not
    #: its node count.  `MAX_RENDER_NODES` bounds the wrong quantity here: a
    #: 1,801-node map that is wide AND deep at once carries roughly 23x the
    #: CELLS of a 4,002-node map that is only wide, and costs several times as
    #: much wall clock despite holding fewer than half the nodes.  Bounding
    #: nodes in this seam would license the expensive shape and refuse the
    #: cheap one.
    #:
    #: (The figures that stood here -- "169 s" and "14 s" -- are STRUCK for the
    #: same reason as the derivation below: both came from the profiler-
    #: contaminated harness and overstate wall clock by 5.3-5.6x.  The ORDERING
    #: they were cited for is real and survives re-measurement, so the claim
    #: stands on the cell ratio, which no instrument error touches, rather than
    #: on two seconds-figures that were never true.)
    #:
    #: THE TARGET IS **2 SECONDS** of synchronous freeze.  `action_export_svg`
    #: runs on the Textual message pump with no progress bar and no cancel, and
    #: beyond roughly two seconds an unresponsive TUI reads as hung rather than
    #: busy.  Time is what binds, not memory -- that part stands.
    #:
    #: BUT THE HEAP FIGURE IS STRUCK, AND IT IS THE FOURTH CLAIM OF THIS
    #: DOCSTRING'S FAMILY, ONE AXIS OVER.  It read "peak heap fits 18.9
    #: bytes/cell, so the whole budget below costs about 7 MB".  Measured with
    #: no clock read at all: 42.8 B/cell at fan 940, and 147.9 B/cell at fan
    #: 3,645 -- AT THE SAME CELL COUNT, and an independent reader measuring
    #: render plus `save_svg` together got 292.3 B/cell and 102 MB against the
    #: claimed 7.  A per-cell MEMORY rate varies with node density for exactly
    #: the reason given below for why no per-cell TIME rate may appear, so the
    #: same prohibition applies and no replacement figure is offered.
    #:
    #: EVERY PER-CELL DERIVATION THIS CONSTANT ONCE CARRIED IS STRUCK.  Two
    #: were written here in turn -- "4.907 us/cell, so 2.0 s / 4.907 us =
    #: 407,616, round down to 400,000", then its replacement "a measured
    #: bracket, 315,252 cells -> 1.801 s and 490,052 -> 2.631 s, so 2.000 s
    #: falls at 357,156, round down to 350,000; cross-checked by a
    #: through-origin fit at 5.4264 us/cell".  BOTH ARE FALSE, AND THEY ARE
    #: FALSE FOR THE SAME REASON: the harness that produced them
    #: (`sec_b68_real_cost.py`, then `b68_budget_probe.py`) calls
    #: `tracemalloc.start()` on the line BEFORE it takes `t0`, so an allocation
    #: profiler ran inside the whole timed region and inflated every point by
    #: 5.3-5.6x.  Measured clean, that bracket's own shape costs **0.301 s**,
    #: not 1.801 -- reproduced independently at 0.321 s and 0.331 s.
    #:
    #: A CORRECTION THAT CHANGES THE NUMBER BUT KEEPS THE INSTRUMENT HAS NOT
    #: CORRECTED ANYTHING.  That is why this is a strike and not an annotation:
    #: the second derivation was not a faithful record taken under an
    #: undeclared condition, it was the first defect re-run.  When a figure is
    #: wrong the question is whether the INPUT or the INSTRUMENT was wrong, and
    #: re-deriving from the same instrument reproduces the defect while looking
    #: like diligence.
    #:
    #: AND THE PER-CELL MODEL ITSELF IS WRONG, which is why no rate appears
    #: above.  Cost per cell tracks NODE DENSITY, not area, so a single rate
    #: cannot derive a cell budget in either direction -- which is why two
    #: independent passes that each sampled one shape family reached answers 6x
    #: apart: wide-and-deep is cheap per cell, wide-only is dense and expensive.
    #:
    #: (The span first written here, "0.955 to 3.27 us/cell, a 3.4x spread", is
    #: STRUCK with the universal below and for the same reason: it was measured
    #: over the same restricted region, at tall start heights only.  An
    #: independent pass measured up to ~53 us/cell once the start height is free
    #: -- roughly a 55x spread.  The QUALITATIVE claim, that the rate varies
    #: with density and so cannot be a single number, is what survives, and it
    #: is stated without a figure because no figure is safe here.)
    #:
    #: WHAT JUSTIFIES 350,000 IS UTILITY, AND *NOT* A TIME GUARANTEE.  THE TIME
    #: CLAIM THAT STOOD HERE IS STRUCK, AND IT IS THE SECOND DERIVATION OF THIS
    #: CONSTANT TO BE STRUCK FOR A DIFFERENT REASON THAN THE ONE BEFORE IT.
    #: It read: "the worst ACCEPTED shape -- 1,000 wide, 312,026 cells -- costs
    #: 1.447 s against the 2-second target, a margin of about 28%.  Nothing the
    #: budget admits crosses the target."  THE UNIVERSAL IS FALSE.
    #:
    #: WHY IT IS FALSE: the hunt varied GRAPH SHAPE and held the START HEIGHT
    #: fixed, and the start height is not a free choice -- it is
    #: `max(5, size.height - 10)`, set by the operator's TERMINAL, and it governs
    #: how much node DENSITY a fixed cell budget admits.  A SHORTER terminal
    #: gives a smaller `h`, so `w * h <= EXPORT_MAX_CELLS` admits a far WIDER
    #: map, and width is what costs.  Measured clean, the worst ADMITTED shape
    #: per terminal:
    #:
    #:     118x40 ->   940 wide, 349,711 cells ->  1.91 s   (under)
    #:     118x35 -> 1,121 wide, 349,778 cells ->  2.41 s   (1.2x over)
    #:      80x24 -> 1,944 wide, 349,935 cells ->  5.94 s   (3.0x over)
    #:     118x20 -> 2,651 wide, 349,943 cells -> 10.38 s   (5.2x over)
    #:     118x11 -> 3,645 wide, 349,928 cells -> 17.73 s   (8.9x over)
    #:
    #: It is over target at 80x24, the classic default, and over target at the
    #: very terminal the struck sentence was measured on.
    #:
    #: THIS IS `C-31` AT THE SEARCH RATHER THAN THE INSTRUMENT, and it is the
    #: corollary minted one revision earlier, applied to its own author: the
    #: previous derivation was struck for a contaminated INSTRUMENT, the
    #: instrument was fixed, and the SEARCH was left holding a governing
    #: variable fixed.  Correcting how you measure does not correct what you
    #: measured over.
    #:
    #: NO SAFE-SIDE TIME CLAIM IS MADE HERE, AND THE THIRD ATTEMPT AT ONE IS
    #: STRUCK ALONGSIDE THE OTHER TWO.  It read: "at start heights of about 30
    #: rows and up, the worst admitted shape stays under 2 s.  Below that it
    #: rises monotonically as the terminal shortens."  NEITHER HALF SURVIVES,
    #: but FOR DIFFERENT REASONS, and the first reason is not the one first
    #: recorded.
    #:
    #: THE SAFE SIDE IS NOT A PROPERTY OF THIS CODE AT ALL.  It was first
    #: recorded here as FALSE, on 4-of-9 runs over 2 s at start height 30 and an
    #: independent 7-of-9.  A SECOND READER THEN FAILED TO REPRODUCE IT
    #: ENTIRELY: 27 runs of the identical shape, 0 over 2 s, 1.333 to 1.662 s,
    #: on artifact bytes identical to both other parties'.  Three measurements
    #: of the same work: 0/27, 4/9, 7/9.  SO THE SENTENCE DESCRIBES A
    #: MACHINE-SESSION, NOT `mapper` -- and that is a BETTER ground for striking
    #: it than "false", because "false" invites a fourth CORRECTED number while
    #: this rules the whole claim shape out.  The 2-second boundary sits inside
    #: between-machine variance, so an upper quantile taken here would have
    #: RATIFIED the struck sentence on one machine and refuted it on another.
    #:
    #: THE ROOT CAUSE IS STILL A STATISTIC, and the failed reproduction sharpens
    #: it rather than weakening it.  The 1.91 s behind the sentence was a
    #: MINIMUM.  Best-of-N is the right statistic for demonstrating a BREACH --
    #: if the minimum exceeds the bound then every run does -- and the WRONG one
    #: for demonstrating SAFETY, where nothing about the other runs follows from
    #: it.  Measured across the three parties, the MINIMUM was the most
    #: reproducible statistic (1.321 vs 1.333, 0.9% apart) and the tail the
    #: least (1.617 vs 2.146), so quoting a minimum is wrong TWICE: it cannot
    #: bound a maximum, AND it is the statistic most likely to look stable --
    #: which makes a safety claim built on it look robust exactly when it is not.
    #:
    #: EVERY SECONDS-FIGURE SURVIVING IN THIS BLOCK IS `IRREDUCIBLY A READING`,
    #: not a property: taken on one Windows machine, best-of-N unless stated,
    #: n as given.  They are kept because they show the SHAPE of the cost, and
    #: none of them may be used as a bound.
    #:
    #: "Monotonically" is false: the curve rises and then PLATEAUS.  ITS CAUSE
    #: AND ITS BOUNDARY WERE BOTH STATED WRONG HERE AND ARE CORRECTED -- a wrong
    #: CAUSE is worse than a wrong number, because it is what the next reader
    #: reasons from.  The text said "the start height FLOORS at 5: every
    #: terminal at or below 15 rows admits the identical shape".  Measured, the
    #: extent settles at `max(8, start + 1)` where 8 is THE MAP'S OWN CONTENT
    #: HEIGHT -- so the plateau runs to terminal 17, not 15, and it is the
    #: content-height floor that causes it, not the start-height floor of 5.
    #: Proof that the floor of 5 is not the cause: changing it to 1 leaves the
    #: extent at terminals 9 through 17 completely unchanged.
    #:
    #: Three runs of that identical plateau work measured 18.9 s, 21.0 s and
    #: 18.9 s -- a 2.1 s spread on one idle machine, which is its own argument
    #: against any wall-clock sentence living in this docstring.
    #:
    #: THE FAMILY, THREE DEEP: the first derivation was struck for a
    #: contaminated INSTRUMENT, the second for a SEARCH that held a governing
    #: variable fixed, and this one for the STATISTIC.  Each correction was
    #: sound and each left the next layer untouched.
    #:
    #: WHAT IS TRUE AND CLOCKLESS, and it is the MECHANISM rather than a number:
    #: THE SAME MAP IS ADMITTED OR REFUSED DEPENDING ON THE TERMINAL.  A
    #: 3,645-wide fanout fits this budget at start height 5 and is refused at
    #: 30, because the budget bounds `w * h` while the start height is chosen by
    #: the operator's terminal.  That is precisely why A CELLS-ONLY BUDGET
    #: CANNOT EXPRESS A TIME BOUND: cost depends on `w` and `h` separately and
    #: this constant constrains only their product, so no value of it makes any
    #: universal true.  Making the freeze genuinely bounded needs a different
    #: BOUND, which is a ruling rather than a constant -- and until there is
    #: one, the export DECLARES the wait instead of promising its length.
    #: `test_the_SAME_map_is_admitted_or_refused_by_the_TERMINAL` pins that
    #: mechanism without a clock, so it cannot flake and cannot drift.  It pins
    #: the BOUNDARY (17 admitted against 18 refused) rather than two far-apart
    #: points, because the far-apart version missed three mutations of the very
    #: expression it existed to pin.
    #:
    #: AND THE TERMINAL IS NOT THE ONLY GOVERNING VARIABLE -- THE VIEW IS A
    #: SECOND ONE, named here because leaving it inherited is how all three
    #: struck sentences went wrong.  `outline` and `radial` DECLINE the resize
    #: (they hold no viewport), so the export keeps a terminal-sized state and
    #: this budget can never refuse in those views at all: the same fan-3,645
    #: map that is refused in `layered` at a 40-row terminal is admitted in both
    #: of them.  Every figure in this block is a `layered` figure.
    #:
    #: DECLARED GAP, measured rather than assumed: the floor of `5` in
    #: `max(5, size.height - 10)` is pinned by NOTHING.  Changing it to 1 leaves
    #: every verdict unchanged, because the content-height floor of 8 dominates
    #: for any map large enough to approach the budget -- so the floor is
    #: observable only in the EXTENT of a small map, where the verdict never
    #: moves.  It is a mandate nothing reads, and closing it needs an extent
    #: arm rather than a budget one.
    #:
    #: SO THE CONSTANT RESTS ON UTILITY ALONE, which is untouched and never
    #: depended on the arithmetic: a 72001x24004 SVG is unreadable by anybody
    #: whatever it costs to produce.  A proposal to relax the budget to ~2.12M
    #: cells is still REFUSED -- it generalised from the cheap shape family and
    #: would admit wide-only maps costing many seconds more than these.
    #:
    #: THE UTILITY GROUND IS UNTOUCHED AND STANDS ALONE.  Even were the cost
    #: free, a 72001x24004 SVG is not an artifact any recipient can read, so
    #: `A-100` does not rest on the arithmetic at all -- which is precisely why
    #: striking the arithmetic costs the ruling nothing.
    #:
    #: WHAT THAT REFUSES -- AND EVERY ROW BELOW IS TERMINAL-SCOPED, which this
    #: list did not say and which makes some of its rows conditional rather than
    #: factual.  All of it was taken at `118x34`, identified after the fact by an
    #: independent reader reproducing the 500-wide row at exactly 150,025 cells.
    #: The CHAIN rows are content-bound and hold at any terminal; the FANOUT rows
    #: are not, and at least one INVERTS: the 500-wide fanout is admitted at
    #: `118x67` (348,058) and REFUSED at `118x68` (354,059).  Measured at
    #: `118x34`: the pan fixture (4,320 cells), a 500-wide fanout (150,025), a
    #: 200-long chain (96,480) and 50 nodes carrying 400-character titles
    #: (15,025) all export.  A 1,000-deep chain (480,480) and a 4,001-way fanout
    #: (1,200,325) are REFUSED.  The wide-and-deep boundary is MEASURED rather
    #: than interpolated: 161 nodes (315,252 cells) export, 201 nodes (490,052)
    #: do not -- that pair alone was NOT re-verified by the reader who found the
    #: scoping defect, because its fixture is ambiguous from the text, so it is
    #: flagged rather than confirmed.
    #: That is the intended consequence rather than a regrettable one: a
    #: 120x4004 artifact is four thousand rows tall and a 48013-column one is
    #: unreadable by anybody, so the refusal costs a file nobody wanted.  `f`
    #: focuses a subtree, which is the route the refusal message names.
    EXPORT_MAX_CELLS = 350_000

    def _export_view_state(self, size) -> ViewState:
        """The state an export renders from: the canvas state, minus the session.

        THE SAME STATE THE CANVAS DRAWS FROM, EXCEPT WHAT IS TRANSIENT.  Sharing
        the state is what closes the measured defect that decided the renderer
        contract: this site passed `query` and omitted `diff`, so an SVG
        exported during a diff silently lost its tinting.  One constructor
        leaves no second argument list to under-fill.

        AN EXPORT IS A STANDALONE ARTIFACT, so it must not encode where the
        session happened to be.  That was ruled once, for the focus owner:
        "which screen region owns the keyboard" is meaningless inside a file,
        and measured on a plain operator sequence -- `tab` (or `g`, which
        focuses the rail), then `e` -- passing the live owner through painted
        the selected node in the INACTIVE tone.  An export always renders as
        though the canvas were focused.

        `B-68` IS THAT SAME RULING, APPLIED TO THE OTHER HALF OF THE SAME
        EXPRESSION.  The pan offsets are transient view state sitting in the
        very `_view_state(...)` call the `focus_owner` `replace()` wrapped, and
        they rode through untouched: the export sized itself from the TERMINAL
        while `_geometry` shrinks `card_w` at that wider width until the tree
        fits, collapsing `max_pan_x` to 0 -- so an offset perfectly legal on the
        canvas was out of range for the export and shifted content off the
        artifact's left edge.  Measured on the pan fixture: 47,263 bytes at
        pan (0,0) against 16,718 at the reachable pan (49,10) -- roughly 65% of
        the map missing from a file the operator hands to someone else, and
        the file looks complete to both of them.  Reachable with no view
        change: pan to the edge, press `e`.

        SO THE FIX REMOVES THE STATE RATHER THAN BOUNDING IT.  Clamping the pan
        to the export's own geometry would stop the content loss and still
        encode a scroll position in a standalone artifact, which is the thing
        the ruling forbids.  The recipient wants the MAP, not where the
        operator happened to be looking.  An "export what I am looking at" mode,
        if it is ever wanted, is a separate deliberate feature whose crop is
        DECLARED IN THE ARTIFACT.

        THE TRANSIENT SET IS DERIVED, NOT LISTED HERE.  `focus_owner`, then the
        pan offsets, then `selected_id` and `hits` were each noticed one at a
        time -- which is a ruling about a CLASS being discharged as a handful of
        instances, leaving the next field for the next reviewer to find.  The
        classification now lives beside the dataclass as
        `views.state.EXPORT_FIELD_KINDS`, and `export_neutralised` resets every
        field marked `transient` to its own declared default.  A field added to
        `ViewState` without a row there fails an arm instead of inheriting
        whichever behaviour its neighbour happened to have.

        AND THE EXTENT IS BOUNDED, BECAUSE "ALWAYS FULL EXTENT" DID NOT SURVIVE
        MEASUREMENT.  Export cost follows the map's BOUNDING-BOX AREA -- the
        canvas walks a dense `w x h` grid -- so a wide AND deep map priced at
        ~125 minutes and ~16 GB inside the product's own node cap, paid on the
        message pump.  It also fails on utility before it fails on cost: a
        72001x24004 SVG is not an artifact any recipient can read.

        SO THIS REFUSES, AND A REFUSAL IS NOT A CROP.  The defect `B-68` names
        is a file that LOOKS COMPLETE AND IS NOT.  Producing nothing and saying
        why preserves that principle exactly; producing a truncated,
        best-effort or silently-shrunk artifact reinstates it.  There is no
        partial-artifact path out of this method, and the exhaustion case below
        refuses for the same reason rather than shipping whatever it had
        reached.

        A VIEW THAT DOES NOT CONSUME PAN DECLINES THE RESIZE, matching
        `_reclamp_pan` one seam over: outline and radial hold no viewport, so
        growing a canvas to "fit the extent" would be applying a layered
        helper renderer-independently -- the defect `PAN-1` closed.  Their
        offsets are still zeroed, because zero is what they already behave as.

        HONEST BOUNDARY: "full extent" here is GEOMETRIC.  It guarantees every
        node's CARD is inside the artifact, not that every node's TITLE is
        printed whole -- `layered._geometry` clamps `card_w` down as the tree
        widens, so at 300 leaves a 40-character title still renders in about
        nine columns. That clamping is identical to the canvas's and is not
        changed here; it is stated so "the recipient wants the MAP" is not read
        as "nothing is ever elided".
        """
        state = export_neutralised(
            self._view_state(max(20, size.width), max(5, size.height - 10))
        )
        if not self._consumes_pan(self._current_renderer()):
            return self._within_export_budget(state)
        for _ in range(self.EXPORT_EXTENT_STEPS):
            try:
                (extent_x, span_x), (extent_y, span_y) = pan_extent(self.graph, state)
            except Exception:
                # Same argument as `refresh_canvas`'s guard and `_pan`'s: a
                # graph that is not a tree raises out of `_tree_layout` by
                # design, and an export is not worth killing the app over.  The
                # render two lines up raises on the same graph into the same
                # handler, so this returns the terminal-sized request rather
                # than inventing a second failure mode for it.
                return self._within_export_budget(state)
            if extent_x <= span_x and extent_y <= span_y:
                return self._within_export_budget(state)
            state = replace(
                state,
                w=state.w + max(0, extent_x - span_x) + 2,
                h=state.h + max(0, extent_y - span_y) + 1,
            )
        # EXHAUSTED WITHOUT FITTING.  Measured, this does not happen -- the
        # extent settles in one step on every shape probed, and an independent
        # pass reproduced it at two.  But returning `state` here would toast
        # "exportado" over an artifact that is cropped for a reason nobody
        # recorded, which is `B-68` with no pan to blame.  Refuse instead.
        #
        # AND IT REFUSES WITH ITS OWN REASON, not with `ExportTooLarge`.  This
        # branch is reached by a state that did not CONVERGE, which is not the
        # same event as a state that was too big -- an exhausted extent can sit
        # under the budget, and `ExportTooLarge` would then hand the operator a
        # number that contradicts its own sentence and advice (`f`) that cannot
        # help.  A message must not name a culprit its condition cannot
        # identify, so this one names what actually happened.
        raise ExportError(
            f"the export extent did not settle in {self.EXPORT_EXTENT_STEPS} steps "
            f"(reached {state.w}x{state.h}); a cropped artifact is the defect this "
            "refuses, so nothing is written"
        )

    def _within_export_budget(self, state: ViewState) -> ViewState:
        """Return `state`, or refuse if rendering it would exceed the budget."""
        cells = max(0, state.w) * max(0, state.h)
        if cells > self.EXPORT_MAX_CELLS:
            raise ExportTooLarge(cells, self.EXPORT_MAX_CELLS)
        return state

    def _guard_focus_mutation(self) -> bool:
        """Return True if a structural mutation should proceed."""
        if self.focus_active:
            self.notify("cannot edit while focus is active (press f to leave)")
            return False
        return True

    def action_add_child(self) -> None:
        if self.nav.cursor is None or self.nav.cursor not in self.graph.nodes:
            self.notify("select a node first")
            return
        if not self._guard_focus_mutation():
            return

        def on_title(title: str | None) -> None:
            if not title or self.store is None:
                return
            self._push_snapshot()
            # `A-111`: coerced before it reaches the graph or `slugify`.
            title = darkside.plain(title)
            parent_id = self.nav.cursor
            base = slugify(title) or "n"
            nid = base
            counter = 1
            while nid in self.graph.nodes:
                nid = f"{base}-{counter}"
                counter += 1
            node = Node(id=nid, ficha=Ficha(title=title))
            self.graph.add_node(node)
            self.graph.add_edge(Edge(parent_id=parent_id, child_id=nid))
            if not _save_or_toast(self, self.store, self.map_id, self.graph):
                return
            self.base_graph = self.graph
            self.nav.cursor = nid
            self.refresh_canvas()

        self.app.push_screen(_PromptScreen("child name", "new child"), callback=on_title)

    def action_open_documents(self) -> None:
        node_id = self.nav.cursor
        if node_id is None or node_id not in self.graph.nodes:
            self.notify("select a node first")
            return
        doc_name = self.graph.document_names()[0] if self.graph.document_names() else ""
        self.app.push_screen(
            FactoryScreen(
                self.graph,
                process_name=self.map_id,
                node_id=node_id,
                document_name=doc_name,
                map_id=self.map_id,
            )
        )

    def action_archive(self) -> None:
        if self.nav.cursor is None or self.nav.cursor not in self.graph.nodes or self.store is None:
            return
        if not self._guard_focus_mutation():
            return
        node = self.graph.nodes[self.nav.cursor]

        def do_archive(confirmed: bool) -> None:
            if not confirmed:
                return
            self._push_snapshot()
            self._remove_subtree(self.nav.cursor)
            if not _save_or_toast(self, self.store, self.map_id, self.graph):
                return
            self.base_graph = self.graph
            self.nav.cursor = self.graph.root_id
            self.refresh_canvas()
            self._event_toast("archived", darkside.plain(node.ficha.title or node.id))

        # Every archive is confirmed, root or not.  A non-root subtree used to be
        # destroyed with no prompt at all, and `x` sits next to the navigation
        # keys.  The message names how much goes, because "archivar" alone does
        # not tell the operator that the children go too.
        count = self._subtree_size(self.nav.cursor)
        # `SEC-H2`, the SOURCE half, and it is a DIFFERENT hazard from the sink's.
        # `markup=False` stops the title acting on the dialog; it does not stop
        # the title REORDERING the sentence, because a bidi override is faithful
        # text and every renderer paints it faithfully.  Measured on the unfixed
        # tree: U+202E and U+200D reached the confirmation raw, so a title could
        # rearrange the words the operator is approving.  `darkside.plain` maps
        # the banned ranges to U+FFFD.  The archive toast eight lines above
        # already called it on this identical value; this line built it again,
        # raw -- which is why the fix is here and not only at the sink.
        name = darkside.plain(node.ficha.title or node.id)
        # Archiving everything is not archiving, it is erasing.  The confirmation
        # used to promise it would "replace the root of the map" and then wrote an
        # EMPTY map to disk — nodes {}, root_id None — with the only recovery an
        # in-memory undo stack that dies with the process.  Refuse instead.
        if count >= len(self.graph.nodes):
            self.notify(
                "cannot archive the whole map: it would be empty. "
                "archive a branch, or delete the map from home.",
                severity="warning",
                markup=False,
            )
            return
        descendants = f"{count - 1} descendant" if count == 2 else f"{count - 1} descendants"
        if self.nav.cursor == self.graph.root_id:
            message = (
                f"archive the root «{name}» and its {descendants}? "
                "this will replace the root of the map."
            )
        elif count > 1:
            message = f"archive «{name}» and its {descendants}?"
        else:
            message = f"archive «{name}»?"
        self.app.push_screen(_ConfirmScreen(message), callback=do_archive)

    def _subtree_size(self, root_id: str | None) -> int:
        """How many nodes would go if this subtree were archived."""
        if root_id is None:
            return 0
        seen: set[str] = set()
        stack = [root_id]
        while stack:
            nid = stack.pop()
            if nid in seen or nid not in self.graph.nodes:
                continue
            seen.add(nid)
            stack.extend(self.graph.children_of(nid))
        return len(seen)

    def _remove_subtree(self, root_id: str) -> None:
        remove: set[str] = set()
        stack = [root_id]
        while stack:
            nid = stack.pop()
            if nid in remove:
                continue
            remove.add(nid)
            stack.extend(self.graph.children_of(nid))
        self.graph.nodes = {k: v for k, v in self.graph.nodes.items() if k not in remove}
        self.graph.edges = [
            e for e in self.graph.edges if e.parent_id not in remove and e.child_id not in remove
        ]
        if self.graph.root_id in remove:
            self.graph.root_id = next(iter(self.graph.nodes), None)

    def action_undo(self) -> None:
        self._pop_snapshot()

    def action_home(self) -> None:
        self._guard_draft(self.app.pop_screen)

    def action_back_or_home(self) -> None:
        """`esc` clears a live search; with none live it leaves the map (`#D38`).

        The hint line promises `esc limpiar` the moment a search is submitted,
        and before this branch existed `escape` popped the screen
        UNCONDITIONALLY -- so an operator who followed the hint left the map.
        Painting a hint for behaviour nobody implemented is the defect `AT-052`
        exists for, one surface over.

        The seat's label stays `volver` and the branch lives here, which `#D10`
        requires: a chord whose LABEL changes with state breaks the whole-seat
        pin's static set equality, and the pin is what makes "help shows exactly
        the keys that work here" checkable at all.

        The two identical arms this replaced -- `if self.source_crumb: pop else:
        pop` -- are gone.  A branch whose sides are the same statement reads as a
        distinction the code does not make.

        The guard is `_search_is_live`, shared with the hint line.

        IT CLEARS IN EVERY REGIME (`LLR-N07.3.4`, `#D43`), which reverses what
        `Inc-4b` shipped.  There the shared predicate read the RESOLUTION, so
        above the renderer's bound this handler popped the screen on the first
        press while it cleared below it -- one chord, two meanings, selected by
        how big the map happened to be.  The count region declares the query at
        every size now, so there is something to clear at every size, and the
        chord means one thing.  A second `esc`, with no query live, still leaves.
        """
        if self._search_is_live():
            self.query_text = ""
            self.refresh_canvas()
            self.query_one(HintLine).set_hint(map_hint())
            return
        self._guard_draft(self.app.pop_screen)

    def action_palette(self) -> None:
        self.app.action_palette()

    def action_help(self) -> None:
        self.app.action_help()


class MapperApp(App):
    """Main application entry point."""

    # Textual's own attribute is ENABLE_COMMAND_PALETTE.  This app previously set
    # COMMAND_PALETTE_ENABLE, a name Textual never reads, so the built-in palette
    # silently owned ctrl+p and mapper's own palette was unreachable by keyboard.
    # Caught only once a test pressed the real key instead of calling the action.
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    Screen { background: #000000; color: #f5f5f5; }
    .group-box { background: #121212; }

    Input {
        border: none;
        background: #262626;
        color: #f5f5f5;
        padding: 0 1;
    }
    Input:focus { border: none; background: #262626; color: #f5f5f5; }

    DataTable {
        background: #121212;
        color: #f5f5f5;
        border: none;
    }
    DataTable > .datatable--header {
        background: #262626;
        color: #737373;
        text-style: bold;
    }
    DataTable > .datatable--cursor {
        background: #1783ff;
        color: #000000;
    }
    DataTable > .datatable--hover {
        background: #262626;
    }

    HomeScreen { layout: vertical; }
    #home-resume-box { height: auto; }
    #home-recents-box { height: 1fr; }
    #home-recents { width: 100%; height: 100%; border: none; }
    #home-empty { width: 100%; height: 100%; }
    #home-identity { width: 100%; text-align: center; padding: 1 0; }

    MapScreen, PlugRepoScreen { layout: vertical; }
    RepoScreen { layout: vertical; }
    #repo-dashboard { height: 1fr; }
    #repo-sidebar { width: 30; background: #121212; padding: 1 1; }
    #repo-name { text-style: bold; color: #f5f5f5; margin-bottom: 1; }
    #repo-stages { color: #737373; margin-bottom: 1; }
    #repo-progress { color: #737373; margin-bottom: 1; }
    #repo-sidebar-hints { color: #737373; }
    #repo-table { height: 1fr; background: #000000; padding: 0 1; }
    /* Variant A «taller»: canvas + inspector side by side.  Depth comes from the
       background step, never from a border — borders are reserved for modals. */
    #map-body { height: 1fr; }
    /* S-07 (LLR-R04.1): without this rule the rail defaults to the full width of
       #map-body, so the canvas collapses to 1 column and the inspector is laid
       out entirely off-screen (measured at 140x45: rail x=0 w=140, inspector
       x=141..177).  The 24 is a LITERAL and not an interpolation of
       rail.RAIL_WIDTH on purpose: TC-R22 asserts the two agree, and a value the
       stylesheet derived from the constant could never disagree with it. */
    #map-rail { width: 24; height: 100%; }
    #map-canvas { width: 1fr; height: 100%; }
    /* THE TWO STRIPS ARE BOUNDED IN THE STYLESHEET, and that is the half of the
       fix the Python cannot do.  Both defaulted to auto height and WRAPPED, so
       their content decided the layout: on a real 12002-node graph #map-minimap
       rendered 471 rows at 118x34 and 712 at 80x24, crushing #map-canvas to a
       single row and laying #map-pagination out at y=715 of a 24-row frame --
       the count region off-viewport entirely.  Capping the meter and the branch
       list is NECESSARY AND NOT SUFFICIENT: a strip whose height is its content
       is one long title away from doing it again.  A fixed height plus a clip
       makes the collapse unreachable by construction rather than by budget.
       3 each: the minimap holds 24 branch entries and its legend at 118
       columns, and the pagination strip holds the meter, the page numerals, the
       search count and the overflow token at 80.

       MAX-HEIGHT, NOT HEIGHT, and the difference is not stylistic -- a fixed
       height is a FLOOR as well as a ceiling.  Written as `height: 3` this rule
       fixed the collapse and then taxed every small map two rows it never
       needed: `legacy` has eight branches and its minimap wants ONE row, so at
       a 35x14 terminal the canvas went to a single row and the coverage
       declaration degraded -- three arms in `test_overflow.py` caught it.  A
       ceiling bounds the pathological case without charging the ordinary one. */
    #map-minimap { max-height: 3; overflow: hidden; }
    #map-pagination { max-height: 3; overflow: hidden; }
    /* `Inc-CRUMB` — the same bound on the two strips `Inc-STRIPS` did not reach,
       and THE ORDER MATTERS: the Python bound landed FIRST, in
       `darkside._crumb_line` and at the `_event_toast` seam. A CSS lid over
       content that is not cell-bounded is how `Inc-STRIPS`' own F1 was born --
       the strip reports its full height while silently eating what it was
       supposed to declare. These are defence in depth over content that is
       already bounded, not the bound itself.
       TABSTRIP IS 3, AND THE FIRST DRAFT SAID 2.  The tab row is not one row at
       every width: at 60 columns the tabs plus the wordmark exceed the terminal
       and that row wraps, so a 2-row lid clipped the CRUMB away entirely -- the
       strip reporting its full height while eating the very thing this
       increment added.  That is `Inc-STRIPS`' own F1 reproduced by its own
       remedy, caught here by this increment's crumb-declaration arm.
       3 = a tab row that may wrap once, plus the one crumb row.  The tab row's
       wrapping at narrow widths is PRE-EXISTING and is carried, not introduced:
       `tab_strip` sizes itself to `max(width, tabs + wordmark)`, so below about
       60 columns it overflows whatever this rule says. */
    TabStrip { max-height: 3; overflow: hidden; }
    #map-toast { max-height: 2; overflow: hidden; }
    #map-inspector {
        width: 36;
        height: 100%;
        background: #121212;
        padding: 0 1;
        overflow-y: auto;
    }
    #map-inspector .insp-label { color: #737373; }
    #map-inspector Input {
        border: none;
        background: #262626;
        color: #f5f5f5;
        height: 1;
        padding: 0 1;
    }
    #map-inspector Input:focus { background: #1783ff; color: #000000; }
    #search-input { dock: bottom; display: none; }

    PlugRepoScreen { align: center middle; }
    #repo-dialog { width: 50; height: auto; background: #121212; padding: 1 2; }
    #repo-title { text-style: bold; color: #f5f5f5; margin-bottom: 1; }

    ConstructScreen, _PromptScreen, _FichaScreen, _TemplateScreen, _ConfirmScreen {
        align: center middle;
        background: #000000 70%;
    }
    #construct-dialog, #prompt-dialog, #ficha-dialog, #template-dialog, #confirm-dialog {
        width: 50;
        height: auto;
        background: #121212;
        padding: 1 2;
    }
    #template-table { width: 100%; height: auto; max-height: 20; border: none; background: #121212; }
    #template-table > .datatable--header { background: #262626; color: #737373; text-style: bold; }
    #template-table > .datatable--cursor { background: #1783ff; color: #000000; }
    #ficha-dialog { width: 60; max-height: 28; }
    #construct-label, #prompt-label, #template-title, #confirm-label {
        text-align: center;
        text-style: bold;
        color: #f5f5f5;
        margin-bottom: 1;
    }
    #construct-hints, #prompt-hints, #confirm-hints {
        text-align: center;
        color: #737373;
        margin-top: 1;
    }

    _ImportPreviewScreen { layout: vertical; }
    #import-preview-canvas { width: 100%; height: 1fr; }
    """

    KEY_SCOPE = SCOPE_APP
    # The app's own bindings come from the seat too — this was the one list that
    # escaped it.  Its hand-written `q -> quit` was bound app-wide, so on the plug
    # and import-preview screens (neither of which declares `q`) pressing `q` quit
    # the application outright, discarding an unsaved import, while palette and
    # help advertised no such key.  `q` now quits only in home scope, where it is
    # advertised.
    BINDINGS = screen_bindings(SCOPE_APP)

    def __init__(self, workspace: Path | str):
        super().__init__()
        self.store = MapStore(workspace)
        # Undo history lives here, not on MapScreen: a screen is rebuilt every
        # time the operator re-enters a map, which used to discard the history
        # silently and make an archived subtree unrecoverable.
        self.undo_stacks: dict[str, list[bytes]] = {}
        self.attachment_launcher = None
        # US-001 (LLR-003.5): set while a quit-walk over draft-bearing map screens
        # is in flight, so a second `ctrl+q` never starts (and stacks) a second walk.
        self._quit_walk_open = False

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())

    def on_screen_resume(self, event) -> None:
        """Refresh the map list when returning to home."""
        if isinstance(self.screen, HomeScreen):
            self.screen.on_mount()

    def action_palette(self) -> None:
        target_screen = self.screen
        scope = getattr(target_screen, "KEY_SCOPE", SCOPE_APP)

        def on_command(action: str | None) -> None:
            if not action:
                return
            # `action` is an action_* method stem straight from the keymap seat,
            # never a translated label — that is what makes the entry dispatch.
            method_name = f"action_{action}"
            if hasattr(target_screen, method_name):
                getattr(target_screen, method_name)()
            elif hasattr(self, method_name):
                getattr(self, method_name)()

        self.push_screen(CommandPalette(scope), callback=on_command)

    def action_help(self) -> None:
        self.push_screen(HelpScreen(
            getattr(self.screen, "KEY_SCOPE", SCOPE_APP),
            view=getattr(self.screen, "legend_view", None),
            host=self.screen,
        ))

    def action_quit(self) -> None:
        # US-001 (LLR-003.5): quitting walks every map screen with a draft and
        # guards each one before the app exits.  A second `ctrl+q` while the walk
        # is up does nothing.  `pending` is the draft-bearing map screens, top of
        # the stack first; each guard's `proceed` advances to the next, the last
        # one exits, and `on_hold` (stay or a failed save) ends the walk.
        if self._quit_walk_open:
            return
        self._quit_walk_open = True
        pending = [
            s
            for s in reversed(self.screen_stack)
            if isinstance(s, MapScreen) and s.has_pending_draft()
        ]

        def end_walk() -> None:
            self._quit_walk_open = False

        def step(index: int) -> None:
            if index >= len(pending):
                self.exit()
                return
            screen = pending[index]
            # PDR C1: a guard already open on this screen (a cursor move asked
            # first) makes `_guard_draft` return without calling anything.  Ending
            # the walk here keeps the operator answering the open guard first.
            if screen._draft_guard_open:
                end_walk()
                return
            screen._guard_draft(
                proceed=lambda: step(index + 1),
                on_hold=end_walk,
            )

        step(0)


def main() -> None:
    import sys

    # Windows terminals default to cp1252 and crash on box-drawing glyphs.
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / "maps"
    app = MapperApp(workspace)
    app.run()


if __name__ == "__main__":
    main()
