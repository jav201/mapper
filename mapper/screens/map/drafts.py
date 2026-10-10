"""MapScreen's `draft` concern as the `DraftsOps` mixin (drafts.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

import copy
from mapper import darkside
from mapper.keymap import bindings_for, hint_pair, SCOPE_DRAFT, SCOPE_MAP
from mapper.model import Ficha
from mapper.screens import DraftGuardScreen
from mapper.screens.common import _save_or_toast, map_hint, MapHintLine
from mapper.widgets.chrome import HintLine
from mapper.widgets.inspector import FichaInspector
from textual.widgets import Input


class DraftsOps:
    """MapScreen's `draft` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

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

    def guard_open(self) -> bool:
        """Whether a draft guard this screen pushed is up.

        B-103: the quit walk reads this, not the private flag.
        """
        return self._draft_guard_open

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
            error = darkside.plain(self._last_save_error or "error")
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
