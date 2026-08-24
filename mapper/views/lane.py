"""Lane (repo-as-map) renderers — list, refined rail timeline, and hybrid."""
from __future__ import annotations

import re

from rich.markup import escape
from rich.text import Text

from mapper import darkside
from mapper.canvas import Canvas
from mapper.model import Graph


_STATE_STYLE = {
    "ok": darkside.INK,
    "risk": darkside.WARN,
    "late": darkside.WARN,
    "blocked": darkside.ALERT,
    "": darkside.INK,
}

_AHEAD_BEHIND_RE = re.compile(r"\+(\d+)/-(\d+)")


def _parse_ahead_behind(meta: str) -> tuple[int, int]:
    m = _AHEAD_BEHIND_RE.search(meta)
    if not m:
        return 0, 0
    return int(m.group(1)), int(m.group(2))


def _ahead_behind_chip(meta: str) -> Text:
    """Render +N/-M as a tiny step-meter chip, keeping the text readable."""
    ahead, behind = _parse_ahead_behind(meta)
    total = max(1, ahead + behind)
    parts = [(" ", "")]
    for i in range(total):
        if i < ahead:
            parts.append(("▰", darkside.INK))
        else:
            parts.append(("▱", darkside.ALERT if behind else darkside.STEP))
    return Text.assemble(*parts)


def _ahead_chip(ahead: int) -> Text:
    if ahead == 0:
        return Text.assemble(("+", darkside.MUT), ("0", darkside.MUT))
    blocks = darkside.step_meter(ahead, max(1, ahead))
    return Text.assemble(("+", darkside.INK), (str(ahead), darkside.INK), (" ", ""), blocks)


def _behind_chip(behind: int) -> Text:
    if behind == 0:
        return Text.assemble(("-", darkside.MUT), ("0", darkside.MUT))
    blocks = darkside.step_meter(behind, max(1, behind))
    return Text.assemble(("-", darkside.ALERT), (str(behind), darkside.ALERT), (" ", ""), blocks)


def _ci_chip(notes: str) -> Text:
    """CI state from a notes string such as 'CI: ok'."""
    state = ""
    if "CI:" in notes:
        state = notes.split("CI:", 1)[1].strip().lower()
    if state == "ok":
        return Text.assemble(("●", darkside.INK), (" ok", darkside.MUT))
    if state == "pending":
        return Text.assemble(("◐", darkside.WARN), (" run", darkside.WARN))
    if state in ("fail", "failure"):
        return Text.assemble(("●", darkside.ALERT), (" fail", darkside.ALERT))
    return Text.assemble(("●", darkside.STEP), (" —", darkside.MUT))


def _branch_kind(name: str) -> str:
    lowered = name.lower()
    if "hotfix" in lowered:
        return "hotfix"
    if "release" in lowered or lowered in ("main", "master"):
        return "release"
    return "branch"


def _kind_icon(kind: str) -> str:
    return {"release": "◆", "hotfix": "◈", "branch": "◫"}.get(kind, "◫")


def _mini_timeline(ahead: int, behind: int, width: int = 20) -> Text:
    total = max(1, ahead + behind)
    text = Text()
    for i in range(min(total, width)):
        if i < ahead:
            text.append("▰", style=darkside.INK)
        else:
            text.append("▱", style=darkside.ALERT)
    return text


def _header(graph: Graph) -> Text:
    header = Text()
    header.append("◆ ", style=darkside.INK)
    header.append("mapper", style=darkside.WORDMARK)
    header.append(f" · {graph.root_id or 'repo'}", style=darkside.MUT)
    return header


class LaneRenderer:
    """Render a repo Graph as horizontal branch lanes (simple list)."""

    def render(
        self,
        graph: Graph,
        selected_id: str | None = None,
        w: int = 80,
        h: int = 24,
        **kwargs,
    ) -> Text:
        lines: list[Text] = []
        lines.append(_header(graph))

        if graph.root_id is None:
            lines.append(Text("(no repo loaded)"))
            return Text("\n").join(lines)

        branches = graph.children_of(graph.root_id)
        for bid in branches[: h - 4]:
            node = graph.nodes[bid]
            line = Text()
            marker = "●"
            style = _STATE_STYLE.get(node.ficha.state, darkside.INK)
            line.append(marker + " ", style=style)
            if bid == selected_id:
                line.append(
                    escape(node.ficha.title),
                    style=f"bold {darkside.GROUND} on {darkside.ACCENT}",
                )
            else:
                line.append(escape(node.ficha.title), style="bold")
            line.append(f"   {node.ficha.meta}", style=darkside.MUT)
            line.append(_ahead_behind_chip(node.ficha.meta))
            if node.ficha.notes:
                line.append(f"   {escape(node.ficha.notes)}", style=darkside.MUT)
            lines.append(line)

        if len(branches) > h - 4:
            lines.append(Text(f"  +{len(branches) - (h - 4)} more", style=darkside.MUT))

        lines.append(Text("─" * max(0, w - 2), style=darkside.STEP))
        sel = graph.nodes.get(selected_id)
        if sel is not None:
            strip = Text()
            strip.append("▸ ", style=darkside.ACCENT)
            strip.append(escape(sel.ficha.title), style="bold")
            strip.append(f"   {sel.ficha.meta}", style=darkside.MUT)
            strip.append(f"   {escape(sel.ficha.notes)}", style=darkside.MUT)
            lines.append(strip)

        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result


class RailTimelineRenderer:
    """Render a repo Graph as a refined rail timeline.

    Main lane runs horizontally through the centre; branches fork above or below
    and carry ahead/behind chips, CI state, and a time scale across the top.
    """

    def render(
        self,
        graph: Graph,
        selected_id: str | None = None,
        w: int = 118,
        h: int = 28,
        **kwargs,
    ) -> Text:
        if graph.root_id is None or not graph.nodes:
            body = Text()
            body.append(_header(graph))
            body.append("\n(no repo loaded)")
            return body

        inner = max(20, w - 2)
        body_h = max(7, h - 5)
        main_y = body_h // 2
        main_x0, main_x1 = 6, inner - 8

        # Time scale
        scale = Text()
        scale.append("today ", style=darkside.MUT)
        for label in ["-1d", "-2d", "-3d", "-1w", "-2w"]:
            scale.append("│", style=darkside.STEP)
            scale.append(f" {label} ", style=darkside.MUT)

        cv = Canvas(inner, body_h)

        # Main lane track
        for x in range(main_x0, main_x1 + 1):
            cv.put(x, main_y, "─", darkside.STEP)

        # Commit dots and head on main
        commit_spacing = max(8, (main_x1 - main_x0) // 6)
        for x in range(main_x0 + commit_spacing, main_x1, commit_spacing):
            cv.put(x, main_y, "●", darkside.MUT)
        cv.put(main_x1, main_y, "▶", darkside.INK)

        branches = graph.children_of(graph.root_id)
        if not branches:
            body = Text()
            body.append(_header(graph))
            body.append("\n")
            body.append(scale)
            body.append("\n")
            body.append(Text("\n").join(cv.rows()))
            return body

        # Pick a default/main branch; first branch is the trunk.
        main_branch = branches[0]
        main_node = graph.nodes[main_branch]
        main_selected = main_branch == selected_id
        main_label = f"◆ {escape(main_node.ficha.title)}"
        main_style = (
            f"bold {darkside.GROUND} on {darkside.ACCENT}"
            if main_selected
            else f"bold {darkside.INK}"
        )
        cv.text(main_x0, main_y - 1, main_label, main_style)

        next_fork_x = main_x0 + len(main_label) + 4

        # Pre-compute a lane row for each branch, alternating above/below main
        # with enough vertical breathing room for the rails.
        lane_rows: list[int] = []
        for i in range(len(branches) - 1):
            slot = i + 1
            side = -1 if slot % 2 == 1 else 1
            offset = 2 + 3 * (i // 2)
            y = main_y + side * offset
            if not (1 <= y < body_h - 1):
                y = main_y - side * offset
            lane_rows.append(y)

        for slot, bid in enumerate(branches[1:], start=1):
            node = graph.nodes[bid]
            ahead, behind = _parse_ahead_behind(node.ficha.meta)
            kind = _branch_kind(node.ficha.title)
            lane_y = lane_rows[slot - 1]

            fork_x = max(next_fork_x, main_x0 + 4)
            if fork_x >= main_x1 - 12:
                break

            span = min(max(8, ahead + behind), main_x1 - fork_x - 4)
            end_x = fork_x + span

            # Vertical rail from fork to lane_y
            if lane_y < main_y:
                for y in range(lane_y, main_y + 1):
                    cv.put(fork_x, y, "│", darkside.STEP)
                cv.put(fork_x, main_y, "┴", darkside.STEP)
                cv.put(fork_x, lane_y, "┌", darkside.STEP)
            else:
                for y in range(main_y, lane_y + 1):
                    cv.put(fork_x, y, "│", darkside.STEP)
                cv.put(fork_x, main_y, "┬", darkside.STEP)
                cv.put(fork_x, lane_y, "└", darkside.STEP)

            # Horizontal lane to end_x
            for x in range(fork_x + 1, end_x + 1):
                cv.put(x, lane_y, "─", darkside.STEP)

            marker = "◈" if kind == "hotfix" else "○"
            cv.put(end_x + 1, lane_y, marker, darkside.INK)

            selected = bid == selected_id
            ci_state = ""
            if "CI:" in node.ficha.notes:
                ci_state = node.ficha.notes.split("CI:", 1)[1].strip().lower()
            label = f" {escape(node.ficha.title)}  +{ahead}/-{behind}  {ci_state}"
            max_label = max(0, inner - (end_x + 3) - 1)
            if len(label) > max_label:
                label = label[: max(0, max_label - 1)] + "…"
            label_style = (
                f"bold {darkside.GROUND} on {darkside.ACCENT}"
                if selected
                else darkside.INK
            )
            cv.text(end_x + 3, lane_y, label, label_style)

            next_fork_x = end_x + 3 + len(label) + 4

        body = Text()
        body.append(_header(graph))
        body.append("\n")
        body.append(scale)
        body.append("\n")
        rows = cv.rows()
        for y, row in enumerate(rows):
            if y:
                body.append("\n")
            body.append(row)

        return body


class HybridLaneRenderer:
    """Hybrid repo view: list rows with a mini timeline per branch."""

    def render(
        self,
        graph: Graph,
        selected_id: str | None = None,
        w: int = 80,
        h: int = 24,
        **kwargs,
    ) -> Text:
        lines: list[Text] = []
        lines.append(_header(graph))

        if graph.root_id is None:
            lines.append(Text("(no repo loaded)"))
            return Text("\n").join(lines)

        branches = graph.children_of(graph.root_id)
        if not branches:
            lines.append(Text("(sin ramas)"))
            return Text("\n").join(lines)

        for bid in branches[: h - 4]:
            node = graph.nodes[bid]
            ahead, behind = _parse_ahead_behind(node.ficha.meta)
            kind = _branch_kind(node.ficha.title)
            selected = bid == selected_id

            rail = "▶" if selected else "▐"
            name = escape(node.ficha.title)
            if kind == "release":
                name = f"◆ {name}"
            elif kind == "hotfix":
                name = f"◈ {name}"
            else:
                name = f"◫ {name}"

            row = Text()
            row.append(f"{rail} ", style=darkside.STEP)
            if selected:
                row.append(name, style=f"bold {darkside.GROUND} on {darkside.ACCENT}")
            else:
                row.append(name, style=f"bold {darkside.INK}")
            row.append("   ", style="")
            row.append_text(_ahead_chip(ahead))
            row.append(" /", style=darkside.MUT)
            row.append_text(_behind_chip(behind))
            row.append("   ", style="")
            row.append_text(_mini_timeline(ahead, behind))
            row.append("   ", style="")
            row.append_text(_ci_chip(node.ficha.notes))
            lines.append(row)

        if len(branches) > h - 4:
            lines.append(Text(f"  +{len(branches) - (h - 4)} more", style=darkside.MUT))

        result = Text()
        for i, row in enumerate(lines[:h]):
            if i:
                result.append("\n")
            result.append(row)
        return result
