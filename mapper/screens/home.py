"""The home screen — A4 of batch `2026-10-09-modular-batch` (LLR-MOD.1.1).

Home of `HomeScreen`, the sala the app opens on: the hero, the resume
row, the recents table and the doors.  It pushes `MapScreen`
(`mapper.screens.map`), `PlugRepoScreen` (`mapper.screens.plug_repo`),
`_ImportPreviewScreen` (`mapper.screens.import_preview`) and
`ConstructScreen` (`mapper.screens.construct`) — never `mapper.app`
(§3); the modals come from `mapper.screens.prompt` and the shared
helpers from `mapper.screens.common`.  `preview_csv` is bound here at
module level, read by `action_import_csv` — the test patch targets this
module (LLR-MOD.3.2).  The name is re-exported from `mapper.app` so
historical `from mapper.app import HomeScreen` sites keep resolving
(LLR-MOD.3.1).
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Static

from mapper import darkside
from mapper.import_csv import preview_csv
from mapper.keymap import SCOPE_HOME, bindings_for, groups_for_keybar
from mapper.model import Document, Edge, Ficha, Graph, Node
from mapper.osopen import PATH_NOT_SUPPORTED, safe_local_path
from mapper.screens.common import (
    _home_door_key,
    _refusal_toast,
    home_hint,
    keybar_groups,
    screen_bindings,
)
from mapper.screens.construct import ConstructScreen
from mapper.screens.factory import FactoryScreen
from mapper.screens.import_preview import _ImportPreviewScreen
from mapper.screens.map.screen import MapScreen
from mapper.screens.plug_repo import PlugRepoScreen
from mapper.screens.prompt import _PromptScreen, _TemplateScreen
from mapper.screens.settings import SettingsScreen
from mapper.store import TEMPLATES
from mapper.widgets.chrome import GroupBox, HintLine, KeyBar, TabStrip

if TYPE_CHECKING:
    from mapper.store import MapStore


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
