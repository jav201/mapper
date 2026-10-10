"""MapScreen's `open` concern as the `OpeningOps` mixin (opening.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

from mapper import darkside
from mapper.osopen import ATTACHMENT_HARD_LINKED, OK as OSOPEN_OK, open_external
from mapper.screens import FactoryScreen
from mapper.screens.common import _path_refusal
from mapper.widgets.inspector import FichaInspector


class OpeningOps:
    """MapScreen's `open` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

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
