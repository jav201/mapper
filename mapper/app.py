"""Textual TUI app for mapper — darkside UI."""
from __future__ import annotations

from pathlib import Path

from textual.app import App

from .export import save_svg
from .github import GitHubConnector
from .keymap import SCOPE_APP
from .screens import CommandPalette, HelpScreen
from .screens.common import (
    COUNT_REGION_ID,
    PAN_INERT_HINT,
    SEARCH_ACTIVE_LABEL,
    SEARCH_COUNT_SUBJECT,
    SEARCH_SUSPENDED_NOTICE,
    _QUERY_ECHO_CELLS,
    _path_refusal,
    keybar_groups,
    map_hint,
    screen_bindings,
)
from .screens.construct import ConstructScreen
from .screens.home import HomeScreen
from .screens.import_preview import _ImportPreviewScreen
from .screens.map.screen import MapScreen
from .screens.map.navigation import NavigationModel
from .screens.plug_repo import PlugRepoScreen
from .screens.prompt import (
    _ConfirmScreen,
    _FichaScreen,
    _PromptScreen,
    _TemplateScreen,
)
from .screens.repo import RepoScreen
from .search import SearchIndex
from .store import MapStore
from .views.layered import MAX_RENDER_NODES, pan_extent


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
            if screen.guard_open():
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
