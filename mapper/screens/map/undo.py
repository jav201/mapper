"""MapScreen's `undo` concern as the `UndoOps` mixin (undo.py).

Moved verbatim out of `screen.py` at `2026-10-09-modular-batch` Spine B; composed into
`MapScreen`. Never imports `mapper.app` (LLR-MOD.6.2).
"""

from __future__ import annotations

import json
from mapper.mermaid import dump as dump_mermaid
from mapper.model import Graph
from mapper.screens.common import _save_or_toast


class UndoOps:
    """MapScreen's `undo` concern (moved verbatim at 2026-10-09-modular-batch Spine B).

    A plain mixin composed into `MapScreen` (screen.py): it declares no BINDINGS, no
    DEFAULT_CSS and no `@on` handlers (Textual ignores them on a non-DOMNode base), and its
    method names are disjoint from every other concern's (LLR-MOD.2.1, LLR-MOD.2.2).
    """

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

    def action_undo(self) -> None:
        self._pop_snapshot()
