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

        def subtree_counts(nid: str) -> tuple[int, int]:
            total = 1
            sin_acta = 0 if graph.nodes[nid].ficha.fields.get("D", "").strip() else 1
            stack = list(graph.children_of(nid))
            while stack:
                cid = stack.pop()
                total += 1
                if not graph.nodes[cid].ficha.fields.get("D", "").strip():
                    sin_acta += 1
                stack.extend(graph.children_of(cid))
            return total, sin_acta

        def walk(nid: str, depth: int) -> None:
            node = graph.nodes[nid]
            prefix = _indent(depth) + ("- " if depth else "")
            line = Text()
            if nid == selected_id:
                block = f"bold {darkside.GROUND} on {darkside.ACCENT}"
                line.append(prefix, style=block)
                line.append(node.ficha.title, style=block)
            else:
                line.append(prefix, style=darkside.MUT)
                line.append(node.ficha.title, style="bold")
            # Collapsed branches still answer: declare counts inline.
            children = graph.children_of(nid)
            if children:
                total, missing = subtree_counts(nid)
                note = f"  {total} nodos"
                if missing:
                    note += f" · {missing} sin acta"
                style = darkside.WARN if missing else darkside.MUT
                if nid == selected_id:
                    style = f"bold {darkside.GROUND} on {darkside.ACCENT}"
                line.append(note, style=style)
            elif node.ficha.meta:
                line.append(f"  {node.ficha.meta}", style=darkside.MUT)
            lines.append(line)
            for cid in children:
                walk(cid, depth + 1)

        walk(graph.root_id, 0)

        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result
