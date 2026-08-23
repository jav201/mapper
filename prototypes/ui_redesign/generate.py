"""Generate real terminal-rendered SVG prototypes for mapper UI redesign.

Run with: python prototypes/ui_redesign/generate.py
Outputs:  out/A_home.svg, B_map.svg, C_focus.svg, D_factory.svg, index.html
"""
from __future__ import annotations

from pathlib import Path

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

# Prism-ish tokens: achromatic ramp + one accent (cyan) + reserved semantic hues.
BG = "#121212"
INK = "#e0e0e0"
DIM = "#737373"
ACCENT = "#00d4ff"
WARN = "#ffcc00"
ALERT = "#ff4d4d"
OK = "#4dff88"


def make_console(w: int = 120, h: int = 40) -> Console:
    import os
    return Console(
        record=True,
        width=w,
        height=h,
        force_terminal=True,
        color_system="truecolor",
        file=open(os.devnull, "w", encoding="utf-8"),
    )


def variant_a_home() -> None:
    """Home screen: three clear doors, recent maps, contextual hints."""
    console = make_console()
    header = Text()
    header.append("◆ MAPPER", style=f"bold {ACCENT}")
    header.append("   mapas vivos para encontrar información relevante", style=f"dim {DIM}")

    doors = Table.grid(padding=(1, 2))
    doors.add_column(justify="center")
    doors.add_column(justify="center")
    doors.add_column(justify="center")
    doors.add_row(
        Panel.fit("[b]Consult maps[/b]\n[dim]c[/dim]", border_style=ACCENT, padding=(2, 4)),
        Panel.fit("[b]Plug repo[/b]\n[dim]p[/dim]", border_style=DIM, padding=(2, 4)),
        Panel.fit("[b]Construct[/b]\n[dim]n[/dim]", border_style=ACCENT, padding=(2, 4)),
    )

    recent = Table(box=None, padding=(0, 2), show_header=True)
    recent.add_column("Recent maps", style=f"bold {INK}")
    recent.add_column("Kind", style=DIM)
    recent.add_column("Nodes", justify="right", style=DIM)
    recent.add_row("sistema-legacy", "legacy schema", "24")
    recent.add_row("lanzamiento-q3", "concept", "12")
    recent.add_row("onboarding-procesos", "process", "8")
    recent.add_row("[dim](empty workspace — press n to build your first map)[/dim]", "", "")

    hints = Text()
    hints.append("? ", style=f"bold {ACCENT}")
    hints.append("help   ", style=DIM)
    hints.append("ctrl+p ", style=f"bold {ACCENT}")
    hints.append("palette   ", style=DIM)
    hints.append("q ", style=f"bold {ACCENT}")
    hints.append("quit", style=DIM)

    console.print(header)
    console.print()
    console.print(Align.center(doors))
    console.print()
    console.print(Rule(style=DIM))
    console.print(recent)
    console.print()
    console.print(Align.right(hints))
    console.save_svg(str(OUT / "A_home.svg"), title="Variant A — Home")


def variant_b_map() -> None:
    """Map view: breadcrumb, layered tree, ficha strip, curated footer."""
    console = make_console()
    top = Text()
    top.append("◆ MAPPER", style=f"bold {ACCENT}")
    top.append("  /  ", style=DIM)
    top.append("lanzamiento-q3", style=INK)
    top.append("  /  ", style=DIM)
    top.append("diseño", style=f"bold {INK}")
    top.append("   [layered]", style=DIM)

    tree = Text()
    tree.append("                                            ┌─▐ descubrimiento\n", style=DIM)
    tree.append("                                            │\n", style=DIM)
    tree.append("                  ┌─▐ estrategia ──────────┼─▐ alcance\n", style=DIM)
    tree.append("                  │                         │\n", style=DIM)
    tree.append("▐ diseño ─────────┤                         └─▐ cronograma\n", style=f"bold {ACCENT}")
    tree.append("                  │\n", style=DIM)
    tree.append("                  └─▐ ejecución ────────────┬─▐ sprints\n", style=DIM)
    tree.append("                                            │\n", style=DIM)
    tree.append("                                            └─▐ entrega", style=DIM)

    strip = Table.grid(padding=(0, 2))
    strip.add_column(style=f"bold {ACCENT}")
    strip.add_column(style=INK)
    strip.add_column(style=DIM)
    strip.add_row("▸", "diseño", "fase inicial · prioridad alta")
    strip.add_row("", "Owner:", "@ana")
    strip.add_row("", "Notas:", "Definir arquitectura de información antes de wireframes.")

    footer = Text()
    footer.append("j/k ", style=f"bold {ACCENT}")
    footer.append("sibling  ", style=DIM)
    footer.append("h/l ", style=f"bold {ACCENT}")
    footer.append("parent/child  ", style=DIM)
    footer.append("f ", style=f"bold {ACCENT}")
    footer.append("focus  ", style=DIM)
    footer.append("o/r ", style=f"bold {ACCENT}")
    footer.append("outline/radial  ", style=DIM)
    footer.append("e ", style=f"bold {ACCENT}")
    footer.append("export  ", style=DIM)
    footer.append("? ", style=f"bold {ACCENT}")
    footer.append("help", style=DIM)

    console.print(top)
    console.print(Rule(style=DIM))
    console.print(tree)
    console.print()
    console.print(Rule(style=DIM))
    console.print(strip)
    console.print(Rule(style=DIM))
    console.print(footer)
    console.save_svg(str(OUT / "B_map.svg"), title="Variant B — Map view")


def variant_c_focus() -> None:
    """Focus/detail board: large tiles, emojis, color highlights."""
    console = make_console()
    header = Text()
    header.append("◆ FOCUS BOARD", style=f"bold {ACCENT}")
    header.append("   tareas marcadas para seguimiento", style=DIM)

    def tile(title: str, meta: str, note: str, marks: list[str], tone: str) -> Panel:
        body = Text()
        body.append(f"{title}\n", style=f"bold {tone}")
        body.append(f"{meta}\n", style=DIM)
        body.append(note, style=INK)
        if marks:
            body.append("\n")
            for m in marks:
                body.append(f"{m} ", style=WARN if m in "❓❗" else OK if m == "✅" else ACCENT)
        return Panel(body, border_style=tone, padding=(1, 2), width=38)

    tiles = Columns(
        [
            tile("Revisar API", "vence hoy", "⚠ endpoint /users sin paginación", ["❗", "⏰"], WARN),
            tile("Diseño tiles", "en curso", "✅ layout base listo; falta densidad", ["✅", "⭐"], OK),
            tile("Documentar factory", "bloqueado", "❓ ¿dónde viven los templates?", ["❓", "📎"], ALERT),
            tile("Kanban v2", "próximo", "nueva agrupación por prioridad", ["⭐", "⏰"], ACCENT),
        ],
        equal=True,
    )

    legend = Text()
    legend.append("texto normal · ", style=INK)
    legend.append("resuelto ", style=f"{OK} underline")
    legend.append("· ", style=DIM)
    legend.append("atención ", style=f"{WARN} underline")
    legend.append("· ", style=DIM)
    legend.append("bloqueo ", style=f"{ALERT} underline")
    legend.append("  — marcas en notas con :ok :warn :block", style=DIM)

    footer = Text()
    footer.append("space ", style=f"bold {ACCENT}")
    footer.append("toggle mark  ", style=DIM)
    footer.append("tab ", style=f"bold {ACCENT}")
    footer.append("next tile  ", style=DIM)
    footer.append("enter ", style=f"bold {ACCENT}")
    footer.append("open ficha  ", style=DIM)
    footer.append("esc ", style=f"bold {ACCENT}")
    footer.append("back", style=DIM)

    console.print(header)
    console.print(Rule(style=DIM))
    console.print(tiles)
    console.print()
    console.print(legend)
    console.print()
    console.print(Rule(style=DIM))
    console.print(footer)
    console.save_svg(str(OUT / "C_focus.svg"), title="Variant C — Focus board")


def variant_d_factory() -> None:
    """Process map + document factory: templates with {{tags}}, tree, preview."""
    console = make_console()
    header = Text()
    header.append("◆ DOCUMENT FACTORY", style=f"bold {ACCENT}")
    header.append("   proceso: contratación", style=DIM)

    tree = Text()
    tree.append("▐ contratación\n", style=f"bold {ACCENT}")
    tree.append("  ├─▐ requisición        {{depto}} {{monto}}\n", style=INK)
    tree.append("  ├─▐ aprobación         {{depto}} {{monto}} {{director}}\n", style=INK)
    tree.append("  ├─▐ oferta             {{puesto}} {{salario}} {{ubicacion}}\n", style=INK)
    tree.append("  └─▐ onboarding         {{nombre}} {{puesto}} {{ubicacion}}\n", style=INK)

    preview = Panel(
        "[b]Template: oferta[/b]\n"
        "[dim]─────────────────────[/dim]\n"
        "Estimado/a candidato/a,\n"
        "Le extendemos la oferta para el puesto [ok]{{puesto}}[/ok] "
        "en [accent]{{ubicacion}}[/accent] con un salario de {{salario}}.\n\n"
        "Departamento: {{depto}}\n"
        "Aprobador: {{director}}",
        border_style=ACCENT,
        title="preview",
        title_align="left",
        padding=(1, 2),
        width=60,
    )

    params = Table(box=None, padding=(0, 1))
    params.add_column("Tag", style=f"bold {ACCENT}")
    params.add_column("Value", style=INK)
    params.add_column("Source node", style=DIM)
    params.add_row("{{puesto}}", "Ingeniero de datos", "oferta")
    params.add_row("{{ubicacion}}", "Remoto", "oferta")
    params.add_row("{{salario}}", "—", "[dim]not set[/dim]")
    params.add_row("{{depto}}", "Plataforma", "requisición")

    footer = Text()
    footer.append("t ", style=f"bold {ACCENT}")
    footer.append("pick template  ", style=DIM)
    footer.append("e ", style=f"bold {ACCENT}")
    footer.append("edit tag  ", style=DIM)
    footer.append("n ", style=f"bold {ACCENT}")
    footer.append("new node  ", style=DIM)
    footer.append("s ", style=f"bold {ACCENT}")
    footer.append("save doc  ", style=DIM)
    footer.append("? ", style=f"bold {ACCENT}")
    footer.append("help", style=DIM)

    console.print(header)
    console.print(Rule(style=DIM))
    console.print(tree)
    console.print()
    console.print(Columns([preview, params], equal=False))
    console.print()
    console.print(Rule(style=DIM))
    console.print(footer)
    console.save_svg(str(OUT / "D_factory.svg"), title="Variant D — Document factory")


def build_index() -> None:
    """Create a self-contained HTML page comparing the four variants."""
    svgs = ["A_home.svg", "B_map.svg", "C_focus.svg", "D_factory.svg"]
    labels = [
        "A — Home screen",
        "B — Map view",
        "C — Focus board",
        "D — Document factory",
    ]
    rows = []
    for svg, label in zip(svgs, labels):
        svg_text = (OUT / svg).read_text(encoding="utf-8")
        rows.append(f"""<div class=\"variant\">
            <h2>{label}</h2>
            <div class=\"svg-wrap\">{svg_text}</div>
        </div>""")
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>mapper UI redesign — prototypes</title>
  <style>
    body {{ background: #0d0d0d; color: #e0e0e0; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin: 0; padding: 2rem; }}
    h1 {{ color: #00d4ff; font-weight: 700; }}
    h2 {{ color: #9e9e9e; font-size: 1rem; margin-top: 2rem; }}
    .variant {{ margin-bottom: 3rem; }}
    .svg-wrap {{ max-width: 100%; overflow-x: auto; border: 1px solid #333; border-radius: 6px; }}
    .svg-wrap svg {{ display: block; max-width: 100%; }}
    p {{ max-width: 70ch; line-height: 1.5; }}
  </style>
</head>
<body>
  <h1>mapper UI redesign — prototypes</h1>
  <p>Four structural directions rendered as real terminal SVGs (Rich console capture).
     Regenerate with <code>python prototypes/ui_redesign/generate.py</code>.</p>
  {''.join(rows)}
</body>
</html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    variant_a_home()
    variant_b_map()
    variant_c_focus()
    variant_d_factory()
    build_index()
    print(f"Prototypes written to {OUT}")
