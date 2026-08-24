"""mapper × darkside — regenerate the approved UI prototypes from the real
shared design-system modules (`mapper.darkside`, `mapper.keymap`).

Run: python prototypes/ui_darkside/generate.py
Outputs: out/*.svg + index.html
"""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

# Make the mapper package importable from this prototype directory.
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

# Re-use the canonical darkside tokens and helpers.
GROUND = darkside.GROUND
PANEL = darkside.PANEL
STEP = darkside.STEP
INK = darkside.INK
MUT = darkside.MUT
ACCENT = darkside.ACCENT
WARN = darkside.WARN
ALERT = darkside.ALERT
WORDMARK = darkside.WORDMARK


def make_console(w: int = 118, h: int = 30) -> Console:
    # rich 15 law: Console.size honours _width ONLY when _height is set too.
    return Console(record=True, width=w, height=h, force_terminal=True,
                   color_system="truecolor",
                   file=open(os.devnull, "w", encoding="utf-8"))


def save(console: Console, name: str, title: str) -> None:
    console.save_svg(str(OUT / name), title=title)
    print(f"wrote {name}")


# --- shared chrome -------------------------------------------------------------
def group_box(renderable, pad_x: int = 1) -> Panel:
    return darkside.group_box(renderable, pad_x=pad_x)


def footer(console, groups, hint: str, hint_key: str | None = None) -> None:
    console.print()
    console.print(darkside.hint_line(hint, hint_key))
    console.print(darkside.keybar(groups))


# --- shared content ------------------------------------------------------------
RECENTS = [("sistema-legacy", "legacy", 24, 3),
           ("lanzamiento-q3", "concept", 12, 0),
           ("contratacion", "factory", 8, 8),
           ("mapper", "repo", 46, 0)]

TREE_ROWS = [
    ("▐ sistema-legacy", "root"),
    ("  ├─▐ core", "node"),
    ("  │  ├─▐ auth      ◫ D-2024-001", "sel"),
    ("  │  ├─▐ db        ◫ D-2024-002", "node"),
    ("  │  └─▐ api       ◫ SIN ACTA", "alert"),
    ("  └─▐ frontend", "node"),
    ("     ├─▐ ui        ◫ D-2024-003", "node"),
    ("     └─▐ state     ◫ SIN ACTA", "alert"),
]

FACT_TREE = [
    "                    ┌─▐ requisición  ◫",
    "                    │",
    "▐ contratacion  ◫ ──┼─▐ aprobacion  ◫",
    "                    │",
    "                    ├─▐ oferta  ◫",
    "                    │",
    "                    └─▐ onboarding  ◫",
]

TAGS = [("{{puesto}}", "ingeniero de datos", "—"),
        ("{{ubicacion}}", "remoto", "—"),
        ("{{depto}}", "—", "plataforma"),
        ("{{director}}", "—", "—"),
        ("{{salario}}", "—", "—")]

DOC_TEXT = [
    "estimado/a candidato/a,",
    "",
    "le extendemos la oferta para el puesto {{puesto}}.",
    "departamento: {{depto}}",
    "ubicación: {{ubicacion}}",
    "salario: {{salario}}",
    "",
    "aprobador: {{director}}",
]


# ---------------------------------------------------------------------------
# screens
# ---------------------------------------------------------------------------
def ds_home() -> None:
    console = make_console()
    console.print(darkside.tab_strip("consult"))
    console.print()

    # continue where you left — the resume row, one level up from the rest
    resume = Text()
    resume.append(" ↩ retomar  ", style=f"bold #000000 on {ACCENT}")
    resume.append("  sistema-legacy  /  auth", style=INK)
    resume.append("   última sesión hace 2h", style=MUT)
    console.print(group_box(resume))
    console.print()

    recent = Table(box=None, padding=(0, 2), expand=True)
    recent.add_column(style=INK)
    recent.add_column(style=MUT)
    recent.add_column(justify="right", style=MUT)
    recent.add_column(justify="right", style=MUT)
    for name, kind, nodes, docs in RECENTS:
        recent.add_row(f"▐ {name}", darkside.kind_chip(kind),
                       f"{nodes} nodos", f"{docs} docs" if docs else "—")
    console.print(group_box(recent))
    console.print()

    footer(console,
           groups_for_keybar(["nav", "doors", "app"]),
           "j/k elige un mapa, ↵ lo abre — o una puerta con su tecla", "↵")
    save(console, "ds-home.svg", "darkside — home")


def ds_home_empty() -> None:
    console = make_console()
    console.print(darkside.tab_strip("consult"))
    console.print()
    console.print()
    ghost = Text()
    ghost.append("  aún no hay mapas en este workspace\n\n", style=MUT)
    ghost.append("  empieza con una puerta:\n", style=INK)
    for key, label, desc in (
            ("c", "consult", "abrir un .mmd del disco"),
            ("p", "plug repo", "leer un repo de github (read-only)"),
            ("n", "construct", "mapa nuevo con semilla de 3 nodos"),
            ("f", "factory", "proceso → documento formal")):
        ghost.append("   ", style=GROUND)
        ghost.append(f"{key}", style=ACCENT)
        ghost.append(f" {label}".ljust(14), style=INK)
        ghost.append(desc + "\n", style=MUT)
    console.print(group_box(ghost, 2))
    console.print()
    footer(console,
           groups_for_keybar(["doors", "app"]),
           "no hay nada que listar todavía — la primera puerta es n", "n")
    save(console, "ds-home-empty.svg", "darkside — home, empty state")


def ds_map() -> None:
    console = make_console()
    console.print(darkside.tab_strip("consult", ["sistema-legacy", "auth"]))

    tree = Text()
    for row, kind in TREE_ROWS:
        if kind == "sel":
            tree.append("  │  ├─▐ ", style=MUT)
            tree.append(" auth      ◫ D-2024-001 ",
                        style=f"bold #000000 on {ACCENT}")
        elif kind == "alert":
            i = row.index("SIN ACTA")
            tree.append(row[:i], style=MUT)
            tree.append("SIN ACTA", style=ALERT)
        else:
            tree.append(row, style=INK if kind == "root" else MUT)
        tree.append("\n")
    console.print(group_box(tree, 2))
    console.print()

    strip = Table(box=None, padding=(0, 2))
    strip.add_column(style=MUT)
    strip.add_column(style=INK)
    strip.add_row("▸ auth", "componente crítico · 2 sub")
    strip.add_row("doc", Text("D-2024-001", style=INK))
    strip.add_row("owner", "@carlos · creado 2024")
    strip.add_row("cobertura", darkside.step_meter(4, 5))
    console.print(group_box(strip))
    console.print()

    footer(console,
           groups_for_keybar(["nav", "node", "view", "app"]),
           "auth tiene 2 sub-nodos — l baja, h sube, ↵ abre la ficha", "↵")
    save(console, "ds-map.svg", "darkside — map")


def ds_factory() -> None:
    console = make_console()
    console.print(darkside.tab_strip("factory", ["contratacion", "oferta"]))

    steps = Text()
    for i, s in enumerate(("proceso", "oferta", "aprobacion", "envio")):
        if i == 1:
            steps.append(f" {i + 1} {s} ", style=f"bold #000000 on {ACCENT}")
        else:
            steps.append(f" {i + 1} {s} ", style=f"{MUT} on {STEP}")
        if i < 3:
            steps.append(" ", style=GROUND)
    console.print(steps)
    console.print()

    tree = Text("\n".join(FACT_TREE))
    joined = "\n".join(FACT_TREE)
    off = joined.index("├─▐ oferta")
    tree.stylize(f"bold #000000 on {ACCENT}", off, off + len("├─▐ oferta  ◫"))
    console.print(tree)
    console.print()

    prev = Text()
    prev.append("documento: oferta   ", style=INK)
    prev.append("preview (tags resolved)\n", style=MUT)
    prev.append("estimado/a candidato/a,\n\nle extendemos la oferta para el puesto ")
    prev.append("ingeniero de datos", style=INK)
    prev.append(".\ndepartamento: ")
    prev.append("plataforma", style=INK)
    prev.append("\nubicación: remoto\nsalario: ")
    prev.append("—", style=ALERT)
    prev.append("\n\naprobador: ")
    prev.append("—", style=MUT)

    tags = Table(box=None, padding=(0, 1))
    tags.add_column(style=ACCENT)
    tags.add_column(style=INK)
    tags.add_column(style=MUT)
    tags.add_row("tag", "local", "inherited")
    for tag, local, inh in TAGS:
        tags.add_row(tag, local, inh)
    console.print(Columns([group_box(prev, 2), group_box(tags, 1)],
                          equal=False, padding=(0, 1)))
    console.print()

    footer(console,
           groups_for_keybar(["nav", "doc", "app"]),
           "oferta hereda {{depto}} de contratacion — d edita el documento",
           "d")
    save(console, "ds-factory.svg", "darkside — factory")


def ds_editor() -> None:
    console = make_console()
    console.print(darkside.tab_strip("factory", ["contratacion", "oferta", "doc"]))

    body = "\n".join(DOC_TEXT)
    editor = Text(body)
    for tag, _l, _i in TAGS:
        tag = tag[2:-2]
        start = body.find("{{" + tag + "}}")
        while start != -1:
            editor.stylize(f"{ACCENT} on {STEP}", start, start + len(tag) + 4)
            start = body.find("{{" + tag + "}}", start + 1)
    console.print(group_box(editor, 2))
    console.print()
    found = Text("  detected: ", style=STEP) + Text("  ".join(
        t[0] for t in TAGS), style=ACCENT)
    console.print(found)
    console.print()

    footer(console,
           groups_for_keybar(["edit", "nav", "app"]),
           "tab cambia a preview resuelto — ctrl+s guarda y vuelve al mapa",
           "tab")
    save(console, "ds-editor.svg", "darkside — editor")


def ds_palette() -> None:
    console = make_console()
    console.print(darkside.tab_strip("consult", ["sistema-legacy"]))
    console.print()

    overlay = Table(box=None, padding=(0, 1), show_header=False)
    overlay.add_column(style=ACCENT, width=8)
    overlay.add_column(style=INK, width=22)
    overlay.add_column(style=STEP)
    query = Text(" /fic", style=f"bold {ACCENT}")
    overlay.add_row(query, "", "")
    groups = [
        ("node", [("a", "add child"), ("d", "document"), ("x", "archivar")]),
        ("view", [("v", "cycle view"), ("/", "buscar"), ("e", "export")]),
        ("app", [("ctrl+p", "palette"), ("?", "help"), ("q", "home")]),
    ]
    first = True
    for gname, pairs in groups:
        overlay.add_row("", Text(gname, style=STEP), "")
        for k, label in pairs:
            if first:
                overlay.add_row(Text(f"{k}", style=ACCENT),
                                Text(f" {label} ",
                                     style=f"bold #000000 on {ACCENT}"),
                                Text("primer match", style=MUT))
                first = False
            else:
                overlay.add_row(Text(f"{k}", style=ACCENT),
                                Text(label, style=MUT), "")
    console.print(Align.center(group_box(overlay, 1)))
    console.print()

    footer(console,
           groups_for_keybar(["palette", "app"]),
           "esc cierra la paleta sin ejecutar", "esc")
    save(console, "ds-palette.svg", "darkside — command palette")


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------
def build_index() -> None:
    svgs = [
        ("ds-home.svg", "home — resume row, recents, guidance"),
        ("ds-home-empty.svg", "home — empty state onboarding"),
        ("ds-map.svg", "map — tree, solid selection, ficha"),
        ("ds-factory.svg", "factory — steps, preview, tags"),
        ("ds-editor.svg", "editor — source with tags"),
        ("ds-palette.svg", "command palette — grouped, first match solid"),
    ]
    rows = []
    for svg, label in svgs:
        text = (OUT / svg).read_text(encoding="utf-8")
        if text.startswith("<?xml"):
            text = text.split("?>", 1)[1]
        rows.append(f'<h2>{label}</h2><div class="term-fig">{text}</div>')
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>mapper × darkside</title>
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
<h1>mapper × darkside</h1>
<p class="note">The Moonshot language: achromatic greys, KMBlue only on
interactive affordances, depth by grey-steps never borders, lowercase register,
a date-driven moon doodle on the wordmark, semantic warn/alert only, solid-block
selection. Renders are generated from the real <code>mapper/darkside.py</code> and
<code>mapper/keymap.py</code> modules with <code>python prototypes/ui_darkside/generate.py</code>.</p>
{"".join(rows)}
</div>
</body>
</html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    ds_home()
    ds_home_empty()
    ds_map()
    ds_factory()
    ds_editor()
    ds_palette()
    build_index()
    print("done")
