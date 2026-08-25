"""Repo navigation & loading prototypes — real terminal renders (Rich SVG).

Run: python prototypes/repo_nav/generate.py
Outputs: out/*.svg + index.html
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from mapper import darkside
from mapper.keymap import groups_for_keybar

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

REPO = "jav201/taskboard"


@dataclass
class Branch:
    name: str
    ahead: int
    behind: int
    ci: str
    updated: str
    kind: str = "branch"


BRANCHES = [
    Branch("main", 0, 0, "success", "hace 2h", "release"),
    Branch("feature/auth", 4, 2, "pending", "hace 1d", "branch"),
    Branch("hotfix/db", 1, 5, "failure", "hace 3h", "hotfix"),
    Branch("refactor/ui", 12, 1, "pending", "hace 4d", "branch"),
    Branch("experimental/ml", 30, 8, "failure", "hace 1sem", "branch"),
    Branch("release/v1.9", 0, 0, "success", "hace 1sem", "release"),
]


def make_console(w: int = 118, h: int = 32) -> Console:
    return Console(
        record=True,
        width=w,
        height=h,
        force_terminal=True,
        color_system="truecolor",
        file=open(os.devnull, "w", encoding="utf-8"),
    )


def save(console: Console, name: str, title: str) -> None:
    console.save_svg(str(OUT / name), title=title)
    print(f"wrote {name}")


def ci_chip(ci: str) -> Text:
    if ci == "failure":
        return Text.assemble(("●", darkside.ALERT), (" fail", darkside.ALERT))
    if ci == "pending":
        return Text.assemble(("◐", darkside.WARN), (" run", darkside.WARN))
    if ci == "success":
        return Text.assemble(("●", darkside.INK), (" ok", darkside.MUT))
    return Text.assemble(("●", darkside.STEP), (" —", darkside.MUT))


def progress_bar(pct: int, width: int = 40) -> Text:
    filled = int(width * pct / 100)
    parts = [("▰" * filled, darkside.INK), ("▱" * (width - filled), darkside.STEP)]
    return Text.assemble(*parts, (f" {pct}%", darkside.MUT))


def stage_indicator(stages: list[str], current: int) -> Text:
    parts: list[tuple[str, str]] = []
    for i, stage in enumerate(stages):
        if i > 0:
            parts.append(("  ▸  ", darkside.STEP))
        if i < current:
            parts.append((stage, darkside.MUT))
        elif i == current:
            parts.append((stage, f"bold {darkside.INK}"))
        else:
            parts.append((stage, darkside.STEP))
    return Text.assemble(*parts)


def branch_table(selected: int = 1) -> Table:
    table = Table(box=None, padding=(0, 2), expand=True)
    table.add_column("rail", style=darkside.STEP, width=3)
    table.add_column("rama", style=darkside.INK)
    table.add_column("ahead", justify="right", style=darkside.INK)
    table.add_column("behind", justify="right", style=darkside.ALERT)
    table.add_column("ci", style=darkside.MUT)
    table.add_column("actualizado", style=darkside.MUT)
    table.add_column("estado", style=darkside.MUT)

    for i, branch in enumerate(BRANCHES):
        rail = "▶" if i == selected else "▐"
        name = branch.name
        kind_icon = {"release": "◆", "hotfix": "◈", "branch": "◫"}.get(branch.kind, "◫")
        state = "ok" if branch.ahead < 10 and branch.behind < 10 and branch.ci == "success" else "risk"
        if branch.ci == "failure":
            state = "blocked"
        state_style = {"ok": darkside.INK, "risk": darkside.WARN, "blocked": darkside.ALERT}.get(state, darkside.MUT)
        table.add_row(
            rail,
            f"{kind_icon} {name}",
            f"+{branch.ahead}",
            f"-{branch.behind}",
            ci_chip(branch.ci),
            branch.updated,
            Text.assemble(("● ", state_style), (state, state_style)),
        )
    return table


def footer(console: Console, hint: str, hint_key: str | None = None) -> None:
    console.print()
    console.print(darkside.hint_line(hint, hint_key))
    console.print(darkside.keybar(groups_for_keybar(["nav", "app"])))


# ---------------------------------------------------------------------------
# Variant A — focus-aware form + progress bar + table
# ---------------------------------------------------------------------------
def variant_a() -> None:
    console = make_console()
    console.print(darkside.tab_strip("p", ["conectar repo"]))
    console.print()

    # progress stage under tabs
    console.print(stage_indicator(["clonar", "fetch", "ramas", "listo"], current=2))
    console.print(progress_bar(60))
    console.print()

    # input form (not auto-focused; focus indicator hidden)
    form = Panel(
        Text.assemble(
            ("owner/repo  ", darkside.MUT),
            ("jav201/taskboard", darkside.INK),
            ("_", darkside.ACCENT),
            "\n",
            ("↵ conectar    esc cancelar    tab mueve foco", darkside.MUT),
        ),
        border_style=darkside.STEP,
        style=f"on {darkside.PANEL}",
        padding=(1, 2),
    )
    console.print(Align.center(form, vertical="middle"))
    console.print()

    console.print(darkside.group_box(branch_table(selected=1)))
    footer(console, "j/k elige rama cuando el input no tiene foco · ↵ detalle · q inicio", "j/k")
    save(console, "variant-a-form-table.svg", "A — formulario con foco consciente + tabla")


# ---------------------------------------------------------------------------
# Variant B — command bar + inline progress + dense dashboard
# ---------------------------------------------------------------------------
def variant_b() -> None:
    console = make_console()
    console.print(darkside.tab_strip("p", [REPO]))
    console.print()

    # inline progress in status line
    status = Text()
    status.append("cargando ramas ", darkside.MUT)
    status.append_text(progress_bar(45, width=24))
    status.append("   ◐ 3/6 ramas", darkside.WARN)
    console.print(status)
    console.print()

    # dense dashboard table
    table = Table(box=None, padding=(0, 1), expand=True)
    table.add_column("rama", style=darkside.INK)
    table.add_column("diff", justify="right", style=darkside.MUT)
    table.add_column("timeline", style=darkside.MUT)
    table.add_column("ci", style=darkside.MUT)

    for branch in BRANCHES:
        total = max(1, branch.ahead + branch.behind)
        width = min(total, 20)
        timeline = Text()
        for i in range(width):
            if i < branch.ahead:
                timeline.append("▰", darkside.INK)
            else:
                timeline.append("▱", darkside.ALERT)
        table.add_row(
            branch.name,
            f"+{branch.ahead}/-{branch.behind}",
            timeline,
            ci_chip(branch.ci),
        )
    console.print(darkside.group_box(table))
    console.print()

    # command bar at bottom (appears on 'c')
    bar = Panel(
        Text.assemble(("c ", darkside.INK), ("conectar repo  ", darkside.MUT), ("jav201/taskboard", darkside.INK), ("_", darkside.ACCENT)),
        border_style=darkside.STEP,
        style=f"on {darkside.PANEL}",
        padding=(0, 1),
    )
    console.print(bar)
    footer(console, "c abre la barra de comando · j/k navega · q inicio", "c")
    save(console, "variant-b-command-bar.svg", "B — barra de comando + progreso inline")


# ---------------------------------------------------------------------------
# Variant C — two-pane sidebar with stage progress + grouped table
# ---------------------------------------------------------------------------
def variant_c() -> None:
    console = make_console()
    console.print(darkside.tab_strip("p", ["conectar repo"]))
    console.print()

    # two columns drawn manually
    left_w = 30
    left = Text()
    left.append("owner/repo\n", darkside.MUT)
    left.append("jav201/taskboard", darkside.INK)
    left.append("_\n\n", darkside.ACCENT)
    left.append("etapas\n", darkside.MUT)
    for i, stage in enumerate(["clonar", "fetch", "ramas", "listo"]):
        marker = "●" if i < 2 else ("◐" if i == 2 else "○")
        style = darkside.INK if i < 2 else (darkside.WARN if i == 2 else darkside.STEP)
        left.append(f"{marker} {stage}\n", style)
    left.append("\n", "")
    left.append_text(progress_bar(60, width=26))

    left_panel = Panel(left, border_style=darkside.STEP, style=f"on {darkside.PANEL}", width=left_w, padding=(1, 1))

    right = Text()
    # grouped table
    for group, kind in [("releases", "release"), ("hotfixes", "hotfix"), ("branches", "branch")]:
        right.append(f"{group}\n", f"bold {darkside.MUT}")
        for branch in BRANCHES:
            if branch.kind != kind:
                continue
            state = "ok" if branch.ahead < 10 and branch.behind < 10 and branch.ci == "success" else "risk"
            if branch.ci == "failure":
                state = "blocked"
            state_style = {"ok": darkside.INK, "risk": darkside.WARN, "blocked": darkside.ALERT}[state]
            right.append(f"  {branch.name:22} +{branch.ahead:2}/-{branch.behind:2}  ", darkside.INK)
            right.append_text(ci_chip(branch.ci))
            right.append(f"  ", "")
            right.append("●", state_style)
            right.append("\n", "")
        right.append("\n", "")
    right_panel = Panel(right, border_style=darkside.STEP, style=f"on {darkside.PANEL}", padding=(1, 2))

    console.print(Columns([left_panel, right_panel], equal=False, expand=True))
    console.print()
    footer(console, "j/k navega tabla · i enfoca input · q inicio", "j/k")
    save(console, "variant-c-two-pane.svg", "C — panel lateral con etapas + tabla agrupada")


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------
def build_index() -> None:
    svgs = [
        ("variant-a-form-table.svg", "A — formulario consciente del foco + barra de progreso + tabla"),
        ("variant-b-command-bar.svg", "B — barra de comando deslizable + progreso inline + dashboard denso"),
        ("variant-c-two-pane.svg", "C — panel lateral con etapas + tabla agrupada por tipo"),
    ]
    rows = []
    for svg, label in svgs:
        text = (OUT / svg).read_text(encoding="utf-8")
        if text.startswith("<?xml"):
            text = text.split(">", 1)[1]
            text = "<svg" + text
        rows.append(f'<h2>{label}</h2><div class="term-fig">{text}</div>')

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>mapper repo — prototipos de navegación y carga</title>
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
<h1>mapper repo — navegación, foco y carga</h1>
<p class="note">Tres propuestas para resolver: (1) el input que secuestra las teclas globales,
(2) la falta de feedback de progreso al cargar un repo/mapa, y (3) la tabla de ramas con indicadores
más claros. Todos los renders son SVGs reales generados desde Rich con la paleta darkside.</p>
{"".join(rows)}
</div>
</body>
</html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    variant_a()
    variant_b()
    variant_c()
    build_index()
    print("done")
