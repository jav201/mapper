"""Lane (repo-as-map) renderer — simplified horizontal branch view."""
from __future__ import annotations

import re

from rich.text import Text

from mapper import darkside
from mapper.model import Graph


STATE_STYLE = {
    "ok": darkside.INK,
    "risk": darkside.WARN,
    "late": darkside.WARN,
    "blocked": darkside.ALERT,
    "": darkside.INK,
}


def _ahead_behind_chip(meta: str) -> Text:
    """Render +N/-M as a tiny step-meter chip, keeping the text readable."""
    m = re.search(r"\+(\d+)/-(\d+)", meta)
    if not m:
        return Text("")
    ahead = int(m.group(1))
    behind = int(m.group(2))
    total = max(1, ahead + behind)
    parts = [(" ", "")]
    for i in range(total):
        if i < ahead:
            parts.append(("▰", darkside.INK))
        else:
            parts.append(("▱", darkside.ALERT if behind else darkside.STEP))
    return Text.assemble(*parts)


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
        header.append("◆ ", style=darkside.INK)
        header.append("mapper", style=darkside.WORDMARK)
        header.append(f" · {graph.root_id or 'repo'}", style=darkside.MUT)
        lines.append(header)

        if graph.root_id is None:
            lines.append(Text("(no repo loaded)"))
            return Text("\n").join(lines)

        branches = graph.children_of(graph.root_id)
        for bid in branches[: h - 4]:
            node = graph.nodes[bid]
            line = Text()
            marker = "●"
            style = STATE_STYLE.get(node.ficha.state, darkside.INK)
            line.append(marker + " ", style=style)
            if bid == selected_id:
                line.append(node.ficha.title,
                            style=f"bold {darkside.GROUND} on {darkside.ACCENT}")
            else:
                line.append(node.ficha.title, style="bold")
            line.append(f"   {node.ficha.meta}", style=darkside.MUT)
            line.append(_ahead_behind_chip(node.ficha.meta))
            if node.ficha.notes:
                line.append(f"   {node.ficha.notes}", style=darkside.MUT)
            lines.append(line)

        if len(branches) > h - 4:
            lines.append(Text(f"  +{len(branches) - (h - 4)} more", style=darkside.MUT))

        lines.append(Text("─" * max(0, w - 2), style=darkside.STEP))
        sel = graph.nodes.get(selected_id)
        if sel is not None:
            strip = Text()
            strip.append("▸ ", style=darkside.ACCENT)
            strip.append(sel.ficha.title, style="bold")
            strip.append(f"   {sel.ficha.meta}", style=darkside.MUT)
            strip.append(f"   {sel.ficha.notes}", style=darkside.MUT)
            lines.append(strip)

        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result
