"""mapper repo-as-map prototypes — real terminal renders (Rich SVG).

Run: python prototypes/ui_repo/generate.py
Outputs: out/*.svg + index.html
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mapper import darkside
from mapper.canvas import Canvas
from mapper.keymap import groups_for_keybar

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------
@dataclass
class Branch:
    name: str
    ahead: int
    behind: int
    ci: str  # success | failure | pending | unknown
    updated: str
    milestone: str = ""
    kind: str = "branch"  # branch | release | hotfix


BRANCHES = [
    Branch("main", 0, 0, "success", "hace 2h", milestone="v2.0.0", kind="release"),
    Branch("feature/auth", 4, 2, "pending", "hace 1d", kind="branch"),
    Branch("hotfix/db", 1, 5, "failure", "hace 3h", kind="hotfix"),
    Branch("refactor/ui", 12, 1, "pending", "hace 4d", kind="branch"),
    Branch("experimental/ml", 30, 8, "failure", "hace 1sem", kind="branch"),
    Branch("release/v1.9", 0, 0, "success", "hace 1sem", milestone="v1.9.0", kind="release"),
]
DEFAULT = "main"
REPO = "jav201/taskboard"


def make_console(w: int = 118, h: int = 32) -> Console:
    return Console(record=True, width=w, height=h, force_terminal=True,
                   color_system="truecolor",
                   file=open(os.devnull, "w", encoding="utf-8"))


def footer(console, groups, hint: str, hint_key: str | None = None) -> None:
    console.print()
    console.print(darkside.hint_line(hint, hint_key))
    console.print(darkside.keybar(groups))


def save(console: Console, name: str, title: str) -> None:
    console.save_svg(str(OUT / name), title=title)
    print(f"wrote {name}")


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------
def ci_chip(ci: str) -> Text:
    """CI state as a semantic darkside chip."""
    if ci == "failure":
        return Text.assemble(("●", darkside.ALERT), (" fail", darkside.ALERT))
    if ci == "pending":
        return Text.assemble(("◐", darkside.WARN), (" run", darkside.WARN))
    if ci == "success":
        # Calm state = ink, never green.
        return Text.assemble(("●", darkside.INK), (" ok", darkside.MUT))
    return Text.assemble(("●", darkside.STEP), (" —", darkside.MUT))


def ahead_chip(ahead: int) -> Text:
    if ahead == 0:
        return Text.assemble(("+", darkside.MUT), ("0", darkside.MUT))
    blocks = darkside.step_meter(ahead, max(1, ahead))
    return Text.assemble(("+", darkside.INK), (str(ahead), darkside.INK), (" ", ""), blocks)


def behind_chip(behind: int) -> Text:
    if behind == 0:
        return Text.assemble(("-", darkside.MUT), ("0", darkside.MUT))
    blocks = darkside.step_meter(behind, max(1, behind))
    return Text.assemble(("-", darkside.ALERT), (str(behind), darkside.ALERT), (" ", ""), blocks)


def kind_icon(kind: str) -> str:
    return {"release": "◆", "hotfix": "◈", "branch": "◫"}.get(kind, "◫")


def branch_row(branch: Branch, selected: bool = False) -> Text:
    """One list row with rail, kind, name, milestone, ahead, behind, CI, age."""
    text = Text()
    # rail
    text.append("▐ ", style=darkside.STEP)
    # kind icon
    icon = kind_icon(branch.kind)
    text.append(f"{icon} ", style=darkside.INK if branch.kind == "release" else darkside.MUT)
    # name
    name_style = f"bold {darkside.GROUND} on {darkside.ACCENT}" if selected else f"bold {darkside.INK}"
    text.append(branch.name, style=name_style)
    text.append("  ", style="")
    # milestone
    if branch.milestone:
        text.append(branch.milestone, style=darkside.INK)
        text.append("  ", style="")
    # ahead/behind chips
    text.append_text(ahead_chip(branch.ahead))
    text.append("   ", style="")
    text.append_text(behind_chip(branch.behind))
    text.append("   ", style="")
    # CI
    text.append_text(ci_chip(branch.ci))
    text.append("   ", style="")
    # age
    text.append(branch.updated, style=darkside.MUT)
    return text


# ---------------------------------------------------------------------------
# A — improved list
# ---------------------------------------------------------------------------
def repo_list() -> None:
    console = make_console()
    console.print(darkside.tab_strip("repo", [REPO]))
    console.print()

    # legend
    legend = Text()
    legend.append("leyenda  ", style=darkside.MUT)
    legend.append_text(ahead_chip(3))
    legend.append(" = ahead  ", style=darkside.MUT)
    legend.append_text(behind_chip(3))
    legend.append(" = behind  ", style=darkside.MUT)
    legend.append("● ok ", style=darkside.MUT)
    legend.append("◐ run ", style=darkside.WARN)
    legend.append("● fail", style=darkside.ALERT)
    console.print(legend)
    console.print()

    rows = Text()
    for i, branch in enumerate(BRANCHES):
        rows.append_text(branch_row(branch, selected=(i == 1)))
        rows.append("\n")
    console.print(darkside.group_box(rows, 2))
    console.print()

    footer(console,
           groups_for_keybar(["nav", "app"]),
           "j/k elige una rama · ↵ abre detalle · q home", "j/k")
    save(console, "repo-list.svg", "repo-as-map — improved list")


# ---------------------------------------------------------------------------
# B — refined rail timeline
# ---------------------------------------------------------------------------
def repo_rail_timeline() -> None:
    console = make_console()
    console.print(darkside.tab_strip("repo", [REPO]))
    console.print()

    # time scale
    scale = Text()
    scale.append("today ", style=darkside.MUT)
    for label in ["-1d", "-2d", "-3d", "-1w", "-2w"]:
        scale.append("│", style=darkside.STEP)
        scale.append(f" {label} ", style=darkside.MUT)
    console.print(scale)
    console.print()

    W, H = 118, 22
    cv = Canvas(W, H)
    main_y = 12
    main_x0, main_x1 = 6, 104

    # main lane track
    for x in range(main_x0, main_x1 + 1):
        cv.wire(x, main_y, 0x0A, "")  # L|R horizontal, style via cell override below
    # redraw track as explicit characters so we can style it
    for x in range(main_x0, main_x1 + 1):
        cv.put(x, main_y, "─", darkside.STEP)

    # commits on main
    commits = [18, 34, 50, 66, 82]
    for x in commits:
        cv.put(x, main_y, "●", darkside.MUT)
    # head
    cv.put(main_x1, main_y, "▶", darkside.INK)
    # main label
    cv.text(main_x0, main_y - 1, "◆ main  v2.0.0", f"bold {darkside.INK}")

    # branches: (name, fork_x, lane_y, end_x, ahead, behind, ci, age, selected)
    branches = [
        ("feature/auth", 22, 4, 38, 4, 2, "pending", "1d", True),
        ("refactor/ui", 40, 7, 56, 12, 1, "pending", "4d", False),
        ("hotfix/db", 60, 17, 74, 1, 5, "failure", "3h", False),
        ("experimental/ml", 78, 19, 90, 30, 8, "failure", "1w", False),
    ]

    for name, fx, ly, ex, ahead, behind, ci_state, age, selected in branches:
        # vertical rail from fork up/down to lane_y
        if ly < main_y:
            for y in range(ly, main_y + 1):
                cv.put(fx, y, "│", darkside.STEP)
            cv.put(fx, main_y, "┴", darkside.STEP)
            cv.put(fx, ly, "┌", darkside.STEP)
        else:
            for y in range(main_y, ly + 1):
                cv.put(fx, y, "│", darkside.STEP)
            cv.put(fx, main_y, "┬", darkside.STEP)
            cv.put(fx, ly, "└", darkside.STEP)
        # horizontal lane to end_x
        for x in range(fx + 1, ex + 1):
            cv.put(x, ly, "─", darkside.STEP)
        # branch node marker
        marker = "◈" if "hotfix" in name else "○"
        cv.put(ex + 1, ly, marker, darkside.INK)
        # label block
        label = f" {name}  +{ahead}/-{behind}  {ci_state}  {age}"
        label_style = f"bold {darkside.GROUND} on {darkside.ACCENT}" if selected else darkside.INK
        cv.text(ex + 3, ly, label, label_style)

    # release tag on main
    cv.put(72, main_y, "◆", darkside.INK)
    cv.text(74, main_y - 1, "v1.9.0", darkside.INK)

    # assemble canvas rows into a single Text
    body = Text()
    for y, row in enumerate(cv.rows()):
        if y:
            body.append("\n")
        body.append(row)

    console.print(darkside.group_box(body, 1))
    console.print()

    footer(console,
           groups_for_keybar(["nav", "app"]),
           "j/k navega ramas · h/l avanza en el tiempo · ↵ detalle · q home", "j/k")
    save(console, "repo-rail.svg", "repo-as-map — refined rail timeline")


# ---------------------------------------------------------------------------
# C — compact lanes with date scale
# ---------------------------------------------------------------------------
def repo_compact() -> None:
    console = make_console()
    console.print(darkside.tab_strip("repo", [REPO]))
    console.print()

    # time scale
    scale = Text()
    scale.append("today ", style=darkside.MUT)
    for label in ["-1d", "-2d", "-3d", "-1w", "-2w"]:
        scale.append("│", style=darkside.STEP)
        scale.append(f" {label} ", style=darkside.MUT)
    console.print(scale)
    console.print()

    table = Table(box=None, padding=(0, 2), expand=True)
    table.add_column("lane", style=darkside.INK)
    table.add_column("status", style=darkside.MUT)
    table.add_column("ahead", style=darkside.INK)
    table.add_column("behind", style=darkside.ALERT)
    table.add_column("ci", style=darkside.MUT)
    for branch in BRANCHES:
        marker = "●" if branch.kind == "release" else "○"
        table.add_row(
            f"{marker} {branch.name}",
            branch.milestone or "—",
            ahead_chip(branch.ahead),
            behind_chip(branch.behind),
            ci_chip(branch.ci),
        )
    console.print(darkside.group_box(table))
    console.print()

    footer(console,
           groups_for_keybar(["nav", "app"]),
           "j/k elige lane · l avanza en fecha · q home", "j/k")
    save(console, "repo-compact.svg", "repo-as-map — compact lanes")


# ---------------------------------------------------------------------------
# D — hybrid: list + mini timeline
# ---------------------------------------------------------------------------
def repo_hybrid() -> None:
    console = make_console()
    console.print(darkside.tab_strip("repo", [REPO]))
    console.print()

    # mini timeline bar per branch
    def mini_timeline(ahead: int, behind: int, width: int = 20) -> Text:
        total = max(1, ahead + behind)
        text = Text()
        for i in range(min(total, width)):
            if i < ahead:
                text.append("▰", style=darkside.INK)
            else:
                text.append("▱", style=darkside.ALERT)
        return text

    table = Table(box=None, padding=(0, 2), expand=True)
    table.add_column("rail", style=darkside.STEP, width=3)
    table.add_column("branch", style=darkside.INK)
    table.add_column("diff", style=darkside.MUT)
    table.add_column("timeline", style=darkside.MUT)
    table.add_column("ci", style=darkside.MUT)
    for i, branch in enumerate(BRANCHES):
        rail = "▶" if branch.name == DEFAULT else "▐"
        name = branch.name
        if branch.milestone:
            name += f"  {branch.milestone}"
        diff = f"+{branch.ahead}/-{branch.behind}"
        table.add_row(
            rail,
            name,
            diff,
            mini_timeline(branch.ahead, branch.behind),
            ci_chip(branch.ci).plain,
        )
    console.print(darkside.group_box(table))
    console.print()

    footer(console,
           groups_for_keybar(["nav", "app"]),
           "j/k elige rama · ↵ detalle · q home", "j/k")
    save(console, "repo-hybrid.svg", "repo-as-map — hybrid list + timeline")


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------
def build_index() -> None:
    svgs = [
        ("repo-list.svg", "A — lista mejorada: rail, ahead/behind separados, CI semántico"),
        ("repo-rail.svg", "B — rail timeline: main central + branches con fork/merge"),
        ("repo-compact.svg", "C — compact lanes: escala de fechas + tabla densa"),
        ("repo-hybrid.svg", "D — híbrido: lista + mini timeline por rama"),
    ]
    rows = []
    for svg, label in svgs:
        text = (OUT / svg).read_text(encoding="utf-8")
        if text.startswith("<?xml"):
            text = text.split(">", 1)[1]
            text = "<svg" + text
        rows.append(f'<h2>{label}</h2><div class="term-fig">{text}</div>')
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>mapper repo-as-map prototypes</title>
<style>
body{{margin:0;background:#0b0f14;color:#c9d1d9;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.wrap{{max-width:1240px;margin:0 auto;padding:30px 20px 80px}}
h1{{font-size:22px;color:#1783ff}}
h2{{font-size:15px;color:#737373;margin:1.6em 0 .5em}}
p.note{{color:#7d8790;max-width:92ch;margin:.3em 0 1.2em;line-height:1.5}}
.term-fig{{margin:12px 0;border:1px solid #1f2733;border-radius:8px;overflow:hidden;background:#000;box-shadow:0 10px 30px rgba(0,0,0,.45)}}
.term-fig svg{{display:block;width:100%;height:auto}}
</style>
</head>
<body>
<div class="wrap">
<h1>mapper repo-as-map — prototipos</h1>
<p class="note">Cuatro direcciones para mejorar la vista de repositorio. Todos usan el
sistema darkside real: grises acromáticos, KMBlue (#1783ff) solo en interactividad,
rojo (#ff4f42) para alertas y amarillo (#ffd230) para warnings. Los renders son
SVGs reales generados desde Rich.</p>
{"".join(rows)}
</div>
</body>
</html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    repo_list()
    repo_rail_timeline()
    repo_compact()
    repo_hybrid()
    build_index()
    print("done")
