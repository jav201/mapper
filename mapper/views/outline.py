"""Outline (indented text) renderer."""
from __future__ import annotations

from rich.text import Text

from mapper import darkside
from mapper.model import Graph


def _indent(level: int) -> str:
    return "  " * level


class OutlineRenderer:
    """Render a Graph as an editable-looking indented outline."""

    def render(
        self,
        graph: Graph,
        selected_id: str | None = None,
        w: int = 80,
        h: int = 24,
        **kwargs,
    ) -> Text:
        lines: list[Text] = []
        header = Text()
        header.append("◆ ", style=darkside.INK)
        header.append("mapper", style=darkside.WORDMARK)
        header.append(" · outline", style=darkside.MUT)
        lines.append(header)

        if graph.root_id is None:
            lines.append(Text("(no map loaded)"))
            return Text("\n").join(lines)

        def walk(nid: str, depth: int) -> None:
            node = graph.nodes[nid]
            prefix = _indent(depth) + ("- " if depth else "")
            line = Text()
            if nid == selected_id:
                block = f"bold {darkside.GROUND} on {darkside.ACCENT}"
                line.append(prefix, style=block)
                line.append(node.ficha.title, style=block)
                if node.ficha.meta:
                    line.append(f"  {node.ficha.meta}", style=block)
            else:
                line.append(prefix, style=darkside.MUT)
                line.append(node.ficha.title, style="bold")
                if node.ficha.meta:
                    line.append(f"  {node.ficha.meta}", style=darkside.MUT)
            lines.append(line)
            for cid in graph.children_of(nid):
                walk(cid, depth + 1)

        walk(graph.root_id, 0)

        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result
