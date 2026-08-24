"""Unified mapper UI prototypes — one app, four entry points.

Run: python prototypes/ui_unified/generate.py
Outputs: out/*.svg + self-contained index.html
"""
from __future__ import annotations

import os
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

ACCENT = "#00d4ff"
DIM = "#737373"
INK = "#e0e0e0"
WARN = "#ffcc00"
OK = "#4dff88"


def make_console(w: int = 120, h: int = 40) -> Console:
    return Console(
        record=True,
        width=w,
        height=h,
        force_terminal=True,
        color_system="truecolor",
        file=open(os.devnull, "w", encoding="utf-8"),
    )


def variant_e_home() -> None:
    """Unified home: four doors that all lead to the same map viewer."""
    console = make_console()
    header = Text()
    header.append("◆ MAPPER", style=f"bold {ACCENT}")
    header.append("   un solo lienzo para mapas, nodos y documentos", style=DIM)

    doors = Table.grid(padding=(1, 2))
    doors.add_column(justify="center")
    doors.add_column(justify="center")
    doors.add_row(
        Panel.fit("[b]Consult maps[/b]\n[dim]c[/dim]", border_style=ACCENT, padding=(2, 4)),
        Panel.fit("[b]Plug repo[/b]\n[dim]p[/dim]", border_style=DIM, padding=(2, 4)),
    )
    doors.add_row(
        Panel.fit("[b]Construct[/b]\n[dim]n[/dim]", border_style=ACCENT, padding=(2, 4)),
        Panel.fit("[b]Document factory[/b]\n[dim]f[/dim]", border_style=WARN, padding=(2, 4)),
    )

    recent = Table(box=None, padding=(0, 2), show_header=True)
    recent.add_column("Recent maps", style=f"bold {INK}")
    recent.add_column("Kind", style=DIM)
    recent.add_column("Nodes", justify="right", style=DIM)
    recent.add_column("Doc nodes", justify="right", style=DIM)
    recent.add_row("sistema-legacy", "legacy", "24", "3")
    recent.add_row("lanzamiento-q3", "concept", "12", "0")
    recent.add_row("contratacion", "factory", "8", "8")

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
    console.save_svg(str(OUT / "E_home.svg"), title="E — Unified home")


def variant_f_factory() -> None:
    """Factory mode: process tree + rendered document + tag inheritance table."""
    console = make_console()
    top = Text()
    top.append("◆ MAPPER", style=f"bold {ACCENT}")
    top.append("  /  ", style=DIM)
    top.append("contratacion", style=INK)
    top.append("  /  ", style=DIM)
    top.append("oferta", style=f"bold {INK}")
    top.append("   [factory]", style=DIM)

    tree = Text()
    tree.append("                    ┌─▐ requisición  ◫\n", style=DIM)
    tree.append("                    │\n", style=DIM)
    tree.append("▐ contratacion  ◫ ──┼─▐ aprobacion  ◫\n", style=f"bold {ACCENT}")
    tree.append("                    │\n", style=DIM)
    tree.append("                    ├─▐ oferta  ◫      ← seleccionado\n", style=f"bold {WARN}")
    tree.append("                    │\n", style=DIM)
    tree.append("                    └─▐ onboarding  ◫\n", style=DIM)

    preview = Panel(
        "[b]Documento: Oferta[/b]\n"
        "[dim]──────────────────────[/dim]\n"
        "Estimado/a candidato/a,\n"
        "\n"
        "Le extendemos la oferta para el puesto [ok]Ingeniero de datos[/ok].\n"
        "Departamento: [accent]Plataforma[/accent]\n"
        "Ubicación: Remoto\n"
        "Salario: [warn]—[/warn]\n"
        "\n"
        "Aprobador: [dim]—[/dim]",
        border_style=ACCENT,
        title="preview (tags resolved)",
        title_align="left",
        padding=(1, 2),
        width=58,
    )

    tags = Table(box=None, padding=(0, 1))
    tags.add_column("Tag", style=f"bold {ACCENT}")
    tags.add_column("Local", style=INK)
    tags.add_column("Inherited", style=DIM)
    tags.add_row("{{puesto}}", "Ingeniero de datos", "—")
    tags.add_row("{{ubicacion}}", "Remoto", "—")
    tags.add_row("{{depto}}", "—", "Plataforma")
    tags.add_row("{{director}}", "—", "—")
    tags.add_row("{{salario}}", "—", "—")

    footer = Text()
    footer.append("j/k ", style=f"bold {ACCENT}")
    footer.append("sibling  ", style=DIM)
    footer.append("h/l ", style=f"bold {ACCENT}")
    footer.append("parent/child  ", style=DIM)
    footer.append("a ", style=f"bold {ACCENT}")
    footer.append("add child  ", style=DIM)
    footer.append("d ", style=f"bold {ACCENT}")
    footer.append("edit doc  ", style=DIM)
    footer.append("s ", style=f"bold {ACCENT}")
    footer.append("save  ", style=DIM)
    footer.append("? ", style=f"bold {ACCENT}")
    footer.append("help", style=DIM)

    console.print(top)
    console.print(Rule(style=DIM))
    console.print(tree)
    console.print()
    console.print(Columns([preview, tags], equal=False))
    console.print()
    console.print(Rule(style=DIM))
    console.print(footer)
    console.save_svg(str(OUT / "F_factory.svg"), title="F — Document factory")


def variant_g_editor() -> None:
    """Document editor modal inside the unified app."""
    console = make_console()
    bg = Text("\n" * 8, style="on #0d0d0d")
    console.print(bg)

    editor = Panel(
        "[b]Edit document: oferta[/b]\n"
        "[dim]────────────────────────────────────────────────[/dim]\n"
        "Estimado/a candidato/a,\n"
        "\n"
        "Le extendemos la oferta para el puesto {{puesto}}.\n"
        "Departamento: {{depto}}\n"
        "Ubicación: {{ubicacion}}\n"
        "Salario: {{salario}}\n"
        "\n"
        "Aprobador: {{director}}\n"
        "[dim]────────────────────────────────────────────────[/dim]\n"
        "Tags detectados:  puesto  depto  ubicacion  salario  director\n"
        "[dim]ctrl+s save   esc cancel   tab preview[/dim]",
        border_style=ACCENT,
        padding=(1, 2),
        width=70,
    )
    console.print(Align.center(editor))
    console.save_svg(str(OUT / "G_editor.svg"), title="G — Document editor")


def variant_h_map() -> None:
    """Legacy/concept map with document chip in the card."""
    console = make_console()
    top = Text()
    top.append("◆ MAPPER", style=f"bold {ACCENT}")
    top.append("  /  ", style=DIM)
    top.append("sistema-legacy", style=INK)
    top.append("   [layered]", style=DIM)

    tree = Text()
    tree.append("                                                ┌─▐ auth  ◫ D-2024-001\n", style=DIM)
    tree.append("                                                │\n", style=DIM)
    tree.append("                  ┌─▐ core ─────────────────────┼─▐ db  ◫ D-2024-002\n", style=DIM)
    tree.append("                  │                             │\n", style=DIM)
    tree.append("▐ sistema-legacy ──┤                             └─▐ api  ◫ SIN ACTA\n", style=f"bold {ACCENT}")
    tree.append("                  │\n", style=DIM)
    tree.append("                  └─▐ frontend ─────────────────┬─▐ ui  ◫ D-2024-003\n", style=DIM)
    tree.append("                                                │\n", style=DIM)
    tree.append("                                                └─▐ state  ◫ SIN ACTA", style=DIM)

    strip = Table.grid(padding=(0, 2))
    strip.add_column(style=f"bold {ACCENT}")
    strip.add_column(style=INK)
    strip.add_column(style=DIM)
    strip.add_row("▸", "auth", "componente crítico")
    strip.add_row("", "Documento:", "D-2024-001")
    strip.add_row("", "Owner:", "@carlos")
    strip.add_row("", "Coverage:", "4/5 requeridos")

    footer = Text()
    footer.append("enter ", style=f"bold {ACCENT}")
    footer.append("ficha  ", style=DIM)
    footer.append("d ", style=f"bold {ACCENT}")
    footer.append("document  ", style=DIM)
    footer.append("v ", style=f"bold {ACCENT}")
    footer.append("cycle view  ", style=DIM)
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
    console.save_svg(str(OUT / "H_map.svg"), title="H — Unified map view")


def build_index() -> None:
    svgs = ["E_home.svg", "F_factory.svg", "G_editor.svg", "H_map.svg"]
    labels = [
        "E — Unified home (four doors, one app)",
        "F — Document factory mode",
        "G — Document editor modal",
        "H — Legacy/concept map with document chip",
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
  <title>mapper unified UI prototypes</title>
  <style>
    body {{ background: #0d0d0d; color: #e0e0e0; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; margin: 0; padding: 2rem; }}
    h1 {{ color: #00d4ff; font-weight: 700; }}
    h2 {{ color: #9e9e9e; font-size: 1rem; margin-top: 2rem; }}
    .variant {{ margin-bottom: 3rem; }}
    .svg-wrap {{ max-width: 100%; overflow-x: auto; border: 1px solid #333; border-radius: 6px; }}
    .svg-wrap svg {{ display: block; max-width: 100%; }}
    p {{ max-width: 70ch; line-height: 1.5; }}
    code {{ background: #222; padding: 0.1rem 0.3rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>mapper — unified UI prototypes</h1>
  <p>Four screens of the same app: maps, nodes, documents and templates share one model.
     Regenerate with <code>python prototypes/ui_unified/generate.py</code>.</p>
  {''.join(rows)}
</body>
</html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    variant_e_home()
    variant_f_factory()
    variant_g_editor()
    variant_h_map()
    build_index()
    print(f"Unified prototypes written to {OUT}")
