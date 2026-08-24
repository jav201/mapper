"""Coverage report screen for incomplete required fields."""
from __future__ import annotations

from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Static

from mapper import darkside
from mapper.model import Graph, SchemaField


class CoverageScreen(ModalScreen[str | None]):
    """Modal report listing nodes with incomplete required-field coverage.

    Dismisses with the selected node id, or None if closed without selection.
    """

    BINDINGS = [
        ("enter", "select", "Seleccionar"),
        ("escape", "dismiss", "Cerrar"),
        ("q", "dismiss", "Cerrar"),
    ]

    CSS = """
    CoverageScreen {
        align: center middle;
        background: #000000 70%;
    }
    #coverage-dialog {
        width: 80;
        height: auto;
        max-height: 32;
        background: #121212;
        padding: 1 2;
    }
    #coverage-title {
        text-style: bold;
        color: #f5f5f5;
        margin-bottom: 1;
    }
    #coverage-table {
        width: 100%;
        height: auto;
        max-height: 24;
        border: none;
        background: #121212;
        color: #f5f5f5;
    }
    #coverage-table > .datatable--header {
        background: #262626;
        color: #737373;
        text-style: bold;
    }
    #coverage-table > .datatable--cursor {
        background: #1783ff;
        color: #000000;
    }
    """

    def __init__(self, graph: Graph, map_id: str) -> None:
        super().__init__()
        self.graph = graph
        self.map_id = map_id

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("cobertura incompleta", id="coverage-title"),
            DataTable(id="coverage-table", cursor_type="row"),
            id="coverage-dialog",
        )

    def on_mount(self) -> None:
        table = self.query_one("#coverage-table", DataTable)
        table.clear()
        table.add_columns("▐", "nodo", "faltantes", "cobertura")

        for node in self._incomplete_nodes():
            have, req = node.ficha.required_coverage(self.graph.schema)
            missing = self._missing_keys(node.ficha, self.graph.schema)
            table.add_row(
                Text.assemble(("▐", darkside.STEP)),
                escape(node.ficha.title or node.id),
                Text.assemble((escape(",".join(missing)), darkside.ALERT)),
                darkside.step_meter(have, req),
                key=node.id,
            )

        if table.row_count == 0:
            table.add_row(
                Text.assemble(("▐", darkside.STEP)),
                "(todos los campos requeridos están completos)",
                Text(""),
                Text(""),
            )

    def _incomplete_nodes(self) -> list:
        """Return nodes with incomplete required coverage, ordered by subtree."""
        out = []
        if self.graph.root_id is None:
            return out

        visited = set()
        stack = [self.graph.root_id]
        while stack:
            nid = stack.pop()
            if nid in visited or nid not in self.graph.nodes:
                continue
            visited.add(nid)
            node = self.graph.nodes[nid]
            have, req = node.ficha.required_coverage(self.graph.schema)
            if req and have < req:
                out.append(node)
            # children in original order so the report follows the tree.
            for cid in reversed(self.graph.children_of(nid)):
                if cid not in visited:
                    stack.append(cid)
        return out

    @staticmethod
    def _missing_keys(ficha, schema: list[SchemaField]) -> list[str]:
        return [f.key for f in schema if f.required and not ficha.fields.get(f.key)]

    def action_select(self) -> None:
        table = self.query_one("#coverage-table", DataTable)
        if table.cursor_row is None:
            self.dismiss(None)
            return
        key = table.coordinate_to_cell_key(table.cursor_coordinate)
        if key is not None and key.value in self.graph.nodes:
            self.dismiss(str(key.value))
        else:
            self.dismiss(None)

    def action_dismiss(self) -> None:
        self.dismiss(None)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        node_id = str(event.row_key.value)
        if node_id in self.graph.nodes:
            self.dismiss(node_id)
        else:
            self.dismiss(None)
