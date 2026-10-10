"""MapScreen's `edits` concern as the `EditingOps` mixin (editing.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

from mapper import darkside
from mapper.mermaid import slugify
from mapper.model import Attachment, Edge, Ficha, Node
from mapper.screens.common import _path_refusal, _save_or_toast
from mapper.screens.prompt import _ConfirmScreen, _PromptScreen
from mapper.widgets.inspector import FichaInspector


class EditingOps:
    """MapScreen's `edits` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

    def on_ficha_inspector_attachment_add_requested(
        self, event: FichaInspector.AttachmentAddRequested
    ) -> None:
        event.stop()
        node_id = event.node_id
        self._guard_draft(lambda: self._add_attachment(node_id))

    def _add_attachment(self, node_id: str) -> None:
        node = self.graph.nodes.get(node_id)
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
        node_id = event.node_id
        index = event.index
        self._guard_draft(lambda: self._remove_attachment(node_id, index))

    def _remove_attachment(self, node_id: str, index: int) -> None:
        node = self.graph.nodes.get(node_id)
        if node is None or self.store is None:
            return
        if not 0 <= index < len(node.ficha.attachments):
            return
        removed = node.ficha.attachments.pop(index)
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

    def _guard_focus_mutation(self) -> bool:
        """Return True if a structural mutation should proceed."""
        if self.focus_active:
            self.notify("cannot edit while focus is active (press f to leave)")
            return False
        return True

    def action_add_child(self) -> None:
        self._guard_draft(self._add_child)

    def _add_child(self) -> None:
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

    def action_archive(self) -> None:
        self._guard_draft(self._archive)

    def _archive(self) -> None:
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
