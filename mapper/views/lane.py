"""Lane (repo-as-map) renderer — simplified horizontal branch view."""
from __future__ import annotations

from rich.text import Text

from mapper.model import Graph


class LaneRenderer:
    """Render a repo Graph as horizontal branch lanes."""

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
        header.append("◆ MAPPER", style="bold magenta")
        header.append(f" · {graph.root_id or 'repo'}", style="dim")
        lines.append(header)

        if graph.root_id is None:
            lines.append(Text("(no repo loaded)"))
            return Text("\n").join(lines)

        branches = graph.children_of(graph.root_id)
        for bid in branches[: h - 4]:
            node = graph.nodes[bid]
            line = Text()
            marker = "●"
            style = {
                "ok": "green",
                "risk": "yellow",
                "late": "red",
                "blocked": "red",
                "": "default",
            }.get(node.ficha.state, "default")
            if bid == selected_id:
                line.append("> ", style="bold magenta")
            else:
                line.append("  ")
            line.append(marker + " ", style=style)
            line.append(node.ficha.title, style="bold" if bid == selected_id else "default")
            line.append(f"   {node.ficha.meta}", style="dim")
            if node.ficha.notes:
                line.append(f"   {node.ficha.notes}", style="dim")
            lines.append(line)

        if len(branches) > h - 4:
            lines.append(Text(f"  +{len(branches) - (h - 4)} more", style="dim"))

        lines.append(Text("─" * max(0, w - 2), style="frame"))
        sel = graph.nodes.get(selected_id)
        if sel is not None:
            strip = Text()
            strip.append("▸ ", style="bold magenta")
            strip.append(sel.ficha.title, style="bold")
            strip.append(f"   {sel.ficha.meta}", style="dim")
            strip.append(f"   {sel.ficha.notes}", style="dim")
            lines.append(strip)

        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result
