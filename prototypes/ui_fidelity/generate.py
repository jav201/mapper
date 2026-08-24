"""UI fidelity prototypes — three chrome systems over the same four screens.

Run: python prototypes/ui_fidelity/generate.py
Outputs: out/*.svg + index.html (per-screen switcher)

The operator's feedback the previous rounds missed, and what this round adds:
  1. VISUAL CUES — selection is reverse + accent edge, position chips (3/12),
     step chips for multi-step flows, empty states that onboard, hover hints.
  2. GESTALT — chrome (header/footer) on the panel ground, content on the app
     ground; controls grouped by category with labels; aligned edges; nothing
     is a wall of equal-weight text.
  3. GUIDANCE — every screen answers Where am I? (breadcrumb) What can I do?
     (grouped key bar) What's next? (a literal hint line above the key bar).
  4. ONE APP — the four entry points share one frame, one key vocabulary,
     one palette, one command palette.

Three organizational systems, NOT recolours:
  V1 FRAME & RIBBON — chrome is boxed; grouping is containment.
  V2 AIR & RULES   — frameless; grouping is whitespace, rules, spines.
  V3 DECK & TABS   — the four doors become a persistent facet tab strip.
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

# --- tokens ------------------------------------------------------------------
ACCENT = "#00d4ff"
PANEL_BG = "#161b22"
GROUND = "#0d0d0d"
INK = "#e6edf3"
HD = "#ffffff"
MUT = "#8b98a5"
DIM = "#5b6675"
OK = "#4dff88"
WARN = "#ffcc00"
ALERT = "#ff5555"
KIND = {"concept": ACCENT, "legacy": WARN, "factory": "#e879f9",
        "repo": OK, "new": HD}


def make_console(w: int = 118, h: int = 30) -> Console:
    # rich 15 law: Console.size honours _width ONLY when _height is also set.
    return Console(record=True, width=w, height=h, force_terminal=True,
                   color_system="truecolor",
                   file=open(os.devnull, "w", encoding="utf-8"))


def save(console: Console, name: str, title: str) -> None:
    console.save_svg(str(OUT / name), title=title)
    print(f"wrote {name}")


# --- shared content ----------------------------------------------------------
RECENTS = [("sistema-legacy", "legacy", 24, 3),
           ("lanzamiento-q3", "concept", 12, 0),
           ("contratacion", "factory", 8, 8),
           ("mapper (repo)", "repo", 46, 0)]

TREE_ROWS = [
    ("▐ sistema-legacy", "root", False, "ink"),
    ("  ├─▐ core", "node", False, "ink"),
    ("  │  ├─▐ auth      ◫ D-2024-001", "node", True, "ink"),
    ("  │  ├─▐ db        ◫ D-2024-002", "node", False, "ink"),
    ("  │  └─▐ api       ◫ SIN ACTA", "node", False, "alert"),
    ("  └─▐ frontend", "node", False, "ink"),
    ("     ├─▐ ui        ◫ D-2024-003", "node", False, "ink"),
    ("     └─▐ state     ◫ SIN ACTA", "node", False, "alert"),
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

DOC_TEXT = [
    "Estimado/a candidato/a,",
    "",
    "Le extendemos la oferta para el puesto {{puesto}}.",
    "Departamento: {{depto}}",
    "Ubicación: {{ubicacion}}",
    "Salario: {{salario}}",
    "",
    "Aprobador: {{director}}",
]

TAGS = [("{{puesto}}", "Ingeniero de datos", "—"),
        ("{{ubicacion}}", "Remoto", "—"),
        ("{{depto}}", "—", "Plataforma"),
        ("{{director}}", "—", "—"),
        ("{{salario}}", "—", "—")]


def badge(kind: str) -> Text:
    return Text(f" {kind} ", style=f"bold {GROUND} on {KIND[kind]}")


def steps(items: list[str], current: int) -> Text:
    t = Text()
    for i, s in enumerate(items):
        t.append(f" {i + 1} ", style=(f"bold {GROUND} on {ACCENT}"
                                      if i == current else f"{DIM} on {PANEL_BG}"))
        t.append(f" {s}  ", style=ACCENT if i == current else DIM)
        if i < len(items) - 1:
            t.append("→ ", style=DIM)
    return t


def key_group(label: str, pairs: list[tuple[str, str]], *, boxed: bool) -> Text:
    t = Text()
    if not boxed:
        t.append(f"{label} ", style=DIM)
    for k, label_ in pairs:
        t.append(f"{k} ", style=f"bold {ACCENT}")
        t.append(f"{label_}  ", style=MUT)
    return t


def hint(text: str) -> Text:
    return Text("siguiente ▸ ", style=DIM) + Text(text, style=MUT)


# ---------------------------------------------------------------------------
# V1 · FRAME & RIBBON — chrome is boxed; grouping is containment
# ---------------------------------------------------------------------------
def v1_chrome_top(console, crumb: list[str], mode: str, mode_tone: str) -> None:
    left = Text()
    left.append("◆ MAPPER", style=f"bold {ACCENT}")
    for part in crumb:
        left.append("  /  ", style=DIM)
        left.append(part, style=INK if part != crumb[-1] else f"bold {HD}")
    # compose in ONE text so the badge keeps its own width, never stretched
    top = left.copy()
    top.append(" " * max(1, 110 - left.cell_len - len(mode) - 4))
    top.append(f" {mode} ", style=f"bold {GROUND} on {mode_tone}")
    console.print(Panel(top, border_style=ACCENT, padding=(0, 1)))


def v1_chrome_bottom(console, hint_text: str, groups: list[tuple[str, list]]) -> None:
    bar = Table.grid(expand=True)
    bar.add_column()
    bar.add_column(justify="right")
    bar.add_row(hint(hint_text), Text("ctrl+p palette", style=DIM))
    groups_row = Text()
    for i, (label, pairs) in enumerate(groups):
        if i:
            groups_row.append("   ", style=DIM)
        groups_row.append(f"[{label}] ", style=f"bold {DIM}")
        groups_row.append_text(key_group(label, pairs, boxed=True))
    bar.add_row(groups_row)
    console.print(Panel(bar, border_style=DIM, padding=(0, 1)))


def v1_home() -> None:
    console = make_console()
    v1_chrome_top(console, ["home"], "browse", ACCENT)
    doors = Table.grid(padding=(1, 2))
    doors.add_column(justify="center")
    doors.add_column(justify="center")
    for r, (a, b) in enumerate((("c consult maps", "p plug repo"),
                                ("n construct", "f document factory"))):
        row = []
        for item in (a, b):
            key, label = item.split(" ", 1)
            kind = {"c": "concept", "p": "repo", "n": "new",
                    "f": "factory"}[key]
            card = Table.grid(padding=(0, 1))
            card.add_row(Text(f"{label}", style=f"bold {INK}"),
                         badge(kind))
            card.add_row(Text(f"{key}", style=f"bold {ACCENT}"), "")
            row.append(Panel(card, border_style=ACCENT if key in "cn" else DIM,
                             padding=(1, 3)))
        doors.add_row(*row)
    console.print(Align.center(doors))

    recent = Table(box=None, padding=(0, 2), show_header=True, expand=True)
    recent.add_column("recent maps", style=f"bold {INK}")
    recent.add_column("kind", style=DIM)
    recent.add_column("nodes", justify="right", style=DIM)
    recent.add_column("doc", justify="right", style=DIM)
    for name, kind, nodes, docs in RECENTS:
        recent.add_row(f"▐ {name}", Text(kind, style=KIND[kind]),
                       str(nodes), str(docs) if docs else "—")
    console.print(Panel(recent, title="recents", title_align="left",
                        border_style=DIM, padding=(0, 1)))
    v1_chrome_bottom(
        console, "elige un mapa con j/k y presiona ↵ — o una puerta con su tecla",
        [("nav", [("j/k", "elegir"), ("↵", "abrir")]),
         ("doors", [("c", "consult"), ("p", "plug"), ("n", "construct"),
                    ("f", "factory")]),
         ("app", [("?", "help"), ("q", "quit")])])
    save(console, "v1-home.svg", "V1 frame & ribbon — home")


def v1_map() -> None:
    console = make_console()
    v1_chrome_top(console, ["home", "sistema-legacy", "auth"], "browse",
                  ACCENT)
    tree = Text()
    for row, _kind, sel, tone in TREE_ROWS:
        if sel:
            tree.append("  │  ├─▐ auth      ◫ D-2024-001", style=f"bold reverse")
        elif "SIN ACTA" in row:
            tree.append(row, style=ALERT)
        elif row.startswith("▐") or "├─▐" in row or "└─▐" in row:
            tree.append(row + "\n", style=INK if tone == "ink" else MUT)
        else:
            tree.append(row + "\n", style=MUT)
    console.print(Panel(tree, title="layered", title_align="left",
                        border_style=DIM, padding=(0, 2)))

    strip = Table.grid(padding=(0, 2))
    strip.add_column(style=f"bold {ACCENT}")
    strip.add_column(style=INK)
    strip.add_column(style=DIM)
    strip.add_row("▸", "auth", "componente crítico · 2 sub")
    strip.add_row("", "doc", Text("D-2024-001", style=OK))
    strip.add_row("", "owner", "@carlos · creado 2024")
    strip.add_row("", "cobertura", Text("4/5 requeridos", style=WARN))
    console.print(Panel(strip, title="ficha", title_align="left",
                        border_style=ACCENT, padding=(0, 1)))
    v1_chrome_bottom(
        console, "auth tiene 2 sub-nodos — l baja, h sube, ↵ abre la ficha",
        [("nav", [("j/k", "mover"), ("h/l", "nivel"), ("↵", "ficha")]),
         ("node", [("a", "add"), ("d", "doc"), ("x", "archivar")]),
         ("view", [("v", "cycle"), ("/", "buscar"), ("e", "export")]),
         ("app", [("?", "help"), ("q", "home")])])
    save(console, "v1-map.svg", "V1 frame & ribbon — map")


def v1_factory() -> None:
    console = make_console()
    v1_chrome_top(console, ["home", "contratacion", "oferta"], "factory",
                  KIND["factory"])
    console.print(steps(["proceso", "oferta", "aprobacion", "envio"], 1))
    joined = "\n".join(FACT_TREE)
    off = joined.index("├─▐ oferta")
    tree = Text(joined)
    tree.stylize(f"bold {WARN}", off, off + len("├─▐ oferta  ◫"))
    preview = Panel(
        "[b]Documento: oferta[/b]  [dim]preview (tags resolved)[/dim]\n"
        "[dim]──────────────────────[/dim]\n"
        "Estimado/a candidato/a,\n\n"
        "Le extendemos la oferta para el puesto [b #4dff88]Ingeniero de datos[/b #4dff88].\n"
        "Departamento: [#00d4ff]Plataforma[/#00d4ff]\n"
        "Ubicación: Remoto\n"
        "Salario: [#ff5555]—[/#ff5555]\n\n"
        "Aprobador: [dim]—[/dim]",
        border_style=ACCENT, padding=(1, 2), width=60)
    tags = Table(box=None, padding=(0, 1), title="tags",
                 border_style=DIM)
    tags.add_column("tag", style=f"bold {ACCENT}")
    tags.add_column("local", style=INK)
    tags.add_column("inherited", style=DIM)
    for tag, local, inh in TAGS:
        tags.add_row(tag, local, inh)
    console.print(Columns([tree, preview, tags], equal=False, padding=(2, 2)))
    v1_chrome_bottom(
        console, "oferta hereda {{depto}} de contratacion — d edita el documento",
        [("nav", [("j/k", "sibling"), ("h/l", "parent/child")]),
         ("doc", [("a", "add child"), ("d", "edit doc"), ("tab", "preview")]),
         ("app", [("s", "save"), ("?", "help"), ("q", "home")])])
    save(console, "v1-factory.svg", "V1 frame & ribbon — factory")


def v1_editor() -> None:
    console = make_console()
    v1_chrome_top(console, ["home", "contratacion", "oferta", "doc"], "edit",
                  WARN)
    body = "\n".join(DOC_TEXT)
    for i, line in enumerate(DOC_TEXT):
        pass
    editor = Text(body)
    for tag, _l, _i in TAGS:
        tag = tag[2:-2]
        start = body.find("{{" + tag + "}}")
        while start != -1:
            editor.stylize(f"bold {ACCENT} on {PANEL_BG}", start,
                           start + len(tag) + 4)
            start = body.find("{{" + tag + "}}", start + 1)
    console.print(Panel(editor, title="source — {{tags}} highlighted",
                        title_align="left", border_style=WARN,
                        padding=(1, 2), width=72))
    found = Text("detected: ", style=DIM) + Text("  ".join(
        t[0] for t in TAGS), style=ACCENT)
    console.print(Align.left(found))
    v1_chrome_bottom(
        console, "tab cambia a preview resuelto — ctrl+s guarda y vuelve al mapa",
        [("edit", [("tab", "preview"), ("ctrl+s", "save"), ("esc", "cancel")]),
         ("nav", [("j/k", "mover cursor")]),
         ("app", [("?", "help"), ("q", "home")])])
    save(console, "v1-editor.svg", "V1 frame & ribbon — editor")


# ---------------------------------------------------------------------------
# V2 · AIR & RULES — frameless; grouping is whitespace, rules, spines
# ---------------------------------------------------------------------------
def v2_top(console, crumb: list[str], mode: str, mode_tone: str) -> None:
    left = Text()
    left.append("◆ MAPPER", style=f"bold {ACCENT}")
    for part in crumb:
        left.append("  /  ", style=DIM)
        left.append(part, style=INK if part != crumb[-1] else f"bold {HD}")
    left.append(" " * 4)
    left.append(f"[{mode}]", style=mode_tone)
    console.print(left)
    console.print(Rule(style=DIM))


def v2_bottom(console, hint_text: str, groups: list[tuple[str, list]]) -> None:
    console.print(Rule(style=DIM))
    console.print(hint(hint_text))
    bar = Text()
    for i, (label, pairs) in enumerate(groups):
        if i:
            bar.append("   ", style=DIM)
        bar.append_text(key_group(label, pairs, boxed=False))
    console.print(bar)


def v2_home() -> None:
    console = make_console()
    v2_top(console, ["home"], "browse", ACCENT)
    console.print()
    for key, label, kind, desc in (
            ("c", "consult maps", "concept", "mapas locales del workspace"),
            ("p", "plug repo", "repo", "lectura de un repo de GitHub"),
            ("n", "construct", "factory", "mapa nuevo, semilla incluida"),
            ("f", "document factory", "factory", "proceso → documento formal")):
        line = Text()
        line.append(f"▐ {key} ", style=f"bold {ACCENT}")
        line.append(label.ljust(20), style=f"bold {INK}")
        line.append(desc.ljust(34), style=MUT)
        line.append_text(badge(kind))
        console.print(Align.center(line))
    console.print()
    console.print(Rule(style=DIM))
    for name, kind, nodes, docs in RECENTS:
        line = Text()
        line.append(f"▐ {name}".ljust(22), style=INK)
        line.append(kind.ljust(10), style=KIND[kind])
        line.append(f"{nodes} nodos".rjust(12), style=DIM)
        line.append(f"{docs} docs".rjust(10) if docs else " " * 10, style=DIM)
        console.print(Align.center(line))
    v2_bottom(
        console, "j/k elige un mapa, ↵ lo abre — o una puerta con su tecla",
        [("nav", [("j/k", "elegir"), ("↵", "abrir")]),
         ("doors", [("c", "consult"), ("p", "plug"), ("n", "construct"),
                    ("f", "factory")]),
         ("app", [("?", "help"), ("q", "quit")])])
    save(console, "v2-home.svg", "V2 air & rules — home")


def v2_map() -> None:
    console = make_console()
    v2_top(console, ["home", "sistema-legacy", "auth"], "browse", ACCENT)
    for row, _kind, sel, tone in TREE_ROWS:
        t = Text()
        if sel:
            t.append("  │  ├─▐ ", style=ACCENT)
            t.append("auth      ◫ D-2024-001", style="bold reverse")
        elif "SIN ACTA" in row:
            t.append(row, style=ALERT)
        else:
            t.append(row, style=INK if tone == "ink" else MUT)
        console.print(t)
    console.print(Rule(style=DIM))
    strip = Text()
    strip.append("▸ auth", style=f"bold {INK}")
    strip.append("   doc ", style=DIM)
    strip.append("D-2024-001", style=OK)
    strip.append("   owner ", style=DIM)
    strip.append("@carlos · 2024", style=MUT)
    strip.append("   cobertura ", style=DIM)
    strip.append("4/5", style=WARN)
    console.print(strip)
    v2_bottom(
        console, "auth tiene 2 sub-nodos — l baja, h sube, ↵ abre la ficha",
        [("nav", [("j/k", "mover"), ("h/l", "nivel"), ("↵", "ficha")]),
         ("node", [("a", "add"), ("d", "doc"), ("x", "archivar")]),
         ("view", [("v", "cycle"), ("/", "buscar"), ("e", "export")]),
         ("app", [("?", "help"), ("q", "home")])])
    save(console, "v2-map.svg", "V2 air & rules — map")


def v2_factory() -> None:
    console = make_console()
    v2_top(console, ["home", "contratacion", "oferta"], "factory",
           KIND["factory"])
    console.print(steps(["proceso", "oferta", "aprobacion", "envio"], 1))
    console.print()
    joined = "\n".join(FACT_TREE)
    off = joined.index("├─▐ oferta")
    tree = Text(joined)
    tree.stylize(f"bold {WARN}", off, off + len("├─▐ oferta  ◫"))
    console.print(tree)
    console.print(Rule(style=DIM))
    prev = Text()
    prev.append("documento: oferta   ", style=f"bold {INK}")
    prev.append("preview (tags resolved)\n", style=DIM)
    prev.append("Estimado/a candidato/a,\n\nLe extendemos la oferta para el puesto ")
    prev.append("Ingeniero de datos", style=f"bold {OK}")
    prev.append(".\nDepartamento: ")
    prev.append("Plataforma", style=ACCENT)
    prev.append("\nUbicación: Remoto\nSalario: ")
    prev.append("—", style=ALERT)
    prev.append("\n\nAprobador: ")
    prev.append("—", style=DIM)
    tags = Text()
    for tag, local, inh in TAGS:
        tags.append(f"{tag}".ljust(14), style=ACCENT)
        tags.append(f"{local}".ljust(20), style=INK if local != "—" else DIM)
        tags.append(f"{inh}\n", style=DIM)
    console.print(Columns([prev, tags], equal=False, padding=(0, 3)))
    v2_bottom(
        console, "oferta hereda {{depto}} de contratacion — d edita el documento",
        [("nav", [("j/k", "sibling"), ("h/l", "parent/child")]),
         ("doc", [("a", "add child"), ("d", "edit doc"), ("tab", "preview")]),
         ("app", [("s", "save"), ("?", "help"), ("q", "home")])])
    save(console, "v2-factory.svg", "V2 air & rules — factory")


def v2_editor() -> None:
    console = make_console()
    v2_top(console, ["home", "contratacion", "oferta", "doc"], "edit", WARN)
    body = "\n".join(DOC_TEXT)
    editor = Text(body)
    for tag, _l, _i in TAGS:
        tag = tag[2:-2]
        start = body.find("{{" + tag + "}}")
        while start != -1:
            editor.stylize(f"bold {ACCENT}", start, start + len(tag) + 4)
            start = body.find("{{" + tag + "}}", start + 1)
    console.print(editor)
    console.print(Rule(style=DIM))
    found = Text("detected: ", style=DIM) + Text("  ".join(
        t[0] for t in TAGS), style=ACCENT)
    console.print(found)
    v2_bottom(
        console, "tab cambia a preview resuelto — ctrl+s guarda y vuelve al mapa",
        [("edit", [("tab", "preview"), ("ctrl+s", "save"), ("esc", "cancel")]),
         ("nav", [("j/k", "mover cursor")]),
         ("app", [("?", "help"), ("q", "home")])])
    save(console, "v2-editor.svg", "V2 air & rules — editor")


# ---------------------------------------------------------------------------
# V3 · DECK & TABS — the four doors become a persistent facet strip
# ---------------------------------------------------------------------------
def v3_tabs(console, active: str, crumb: list[str]) -> None:
    strip = Table.grid(padding=(0, 1))
    strip.add_column()
    strip.add_column()
    strip.add_column()
    strip.add_column()
    strip.add_column(justify="right")
    cells = []
    for key, label, kind in (("c", "consult", "concept"), ("p", "repo", "repo"),
                             ("n", "construct", "factory"),
                             ("f", "factory", "factory")):
        on = label == active or (active == "home" and label == "consult")
        card = Text()
        card.append(f" {key} ", style=(f"bold {GROUND} on {KIND[kind]}"
                                       if on else f"bold {KIND[kind]}"))
        card.append(f" {label} ", style=(f"bold {INK} on {ACCENT}" if on
                                         else MUT))
        cells.append(card)
    right = Text("?" , style=f"bold {ACCENT}")
    right.append(" help   ctrl+p palette", style=DIM)
    strip.add_row(*cells, right)
    console.print(Panel(strip, border_style=DIM, padding=(0, 1),
                        style=f"on {PANEL_BG}"))
    if crumb:
        line = Text()
        for i, part in enumerate(crumb):
            if i:
                line.append("  /  ", style=DIM)
            line.append(part, style=INK if part != crumb[-1] else f"bold {HD}")
        console.print(Align.center(line))


def v3_home() -> None:
    console = make_console()
    v3_tabs(console, "home", [])
    console.print()
    recent = Table(box=None, padding=(0, 2), show_header=True, expand=True)
    recent.add_column("recent maps", style=f"bold {INK}")
    recent.add_column("kind", style=DIM)
    recent.add_column("nodes", justify="right", style=DIM)
    recent.add_column("doc", justify="right", style=DIM)
    for name, kind, nodes, docs in RECENTS:
        recent.add_row(f"▐ {name}", Text(kind, style=KIND[kind]),
                       str(nodes), str(docs) if docs else "—")
    console.print(Align.center(recent))
    console.print()
    next_ = Text()
    next_.append("siguiente ▸ ", style=DIM)
    next_.append("j/k elige · ↵ abre · las pestañas de arriba son las puertas",
                 style=MUT)
    console.print(Align.center(next_))
    save(console, "v3-home.svg", "V3 deck & tabs — home")


def v3_map() -> None:
    console = make_console()
    v3_tabs(console, "consult", ["sistema-legacy", "auth"])
    body = Table.grid(padding=(0, 2))
    body.add_column(ratio=3)
    body.add_column(ratio=2)
    tree = Text()
    for row, _kind, sel, tone in TREE_ROWS:
        if sel:
            tree.append("  │  ├─▐ ", style=ACCENT)
            tree.append("auth      ◫ D-2024-001", style="bold reverse")
            tree.append("\n")
        elif "SIN ACTA" in row:
            tree.append(row + "\n", style=ALERT)
        else:
            tree.append(row + "\n", style=INK if tone == "ink" else MUT)
    strip = Text()
    strip.append("▸ auth\n", style=f"bold {INK}")
    strip.append("doc ", style=DIM)
    strip.append("D-2024-001\n", style=OK)
    strip.append("owner ", style=DIM)
    strip.append("@carlos · 2024\n", style=MUT)
    strip.append("cobertura ", style=DIM)
    strip.append("4/5", style=WARN)
    body.add_row(tree, Panel(strip, title="ficha", title_align="left",
                             border_style=ACCENT, padding=(0, 1)))
    console.print(body)
    console.print(Rule(style=DIM))
    bar = Text()
    bar.append_text(key_group("nav", [("j/k", "mover"), ("h/l", "nivel"),
                                      ("↵", "ficha")], boxed=False))
    bar.append("   ", style=DIM)
    bar.append_text(key_group("node", [("a", "add"), ("d", "doc"),
                                       ("x", "archivar")], boxed=False))
    bar.append("   ", style=DIM)
    bar.append_text(key_group("view", [("v", "cycle"), ("/", "buscar"),
                                       ("e", "export")], boxed=False))
    console.print(Align.center(bar))
    save(console, "v3-map.svg", "V3 deck & tabs — map")


def v3_factory() -> None:
    console = make_console()
    v3_tabs(console, "factory", ["contratacion", "oferta"])
    console.print(Align.center(steps(["proceso", "oferta", "aprobacion",
                                      "envio"], 1)))
    console.print()
    body = Table.grid(padding=(0, 2))
    body.add_column(ratio=2)
    body.add_column(ratio=3)
    joined = "\n".join(FACT_TREE)
    off = joined.index("├─▐ oferta")
    tree = Text(joined)
    tree.stylize(f"bold {WARN}", off, off + len("├─▐ oferta  ◫"))
    right = Text()
    right.append("documento: oferta   ", style=f"bold {INK}")
    right.append("preview (tags resolved)\n", style=DIM)
    right.append("Estimado/a candidato/a,\n\nLe extendemos la oferta para el puesto ")
    right.append("Ingeniero de datos", style=f"bold {OK}")
    right.append(".\nDepartamento: ")
    right.append("Plataforma", style=ACCENT)
    right.append("\nUbicación: Remoto\nSalario: ")
    right.append("—", style=ALERT)
    right.append("\n\nAprobador: ")
    right.append("—", style=DIM)
    body.add_row(tree, Panel(right, border_style=ACCENT, padding=(1, 2)))
    console.print(body)
    tags = Text()
    tags.append("tags        local        inherited\n", style=DIM)
    for tag, local, inh in TAGS:
        tags.append(f"{tag}".ljust(12), style=ACCENT)
        tags.append(f"{local}".ljust(13), style=INK if local != "—" else DIM)
        tags.append(f"{inh}\n", style=DIM)
    console.print(Align.center(tags))
    console.print(Rule(style=DIM))
    bar = Text()
    bar.append_text(key_group("nav", [("j/k", "sibling"), ("h/l", "parent/child")],
                              boxed=False))
    bar.append("   ", style=DIM)
    bar.append_text(key_group("doc", [("a", "add child"), ("d", "edit doc"),
                                      ("tab", "preview")], boxed=False))
    bar.append("   ", style=DIM)
    bar.append_text(key_group("app", [("s", "save"), ("q", "home")],
                              boxed=False))
    console.print(Align.center(bar))
    save(console, "v3-factory.svg", "V3 deck & tabs — factory")


def v3_editor() -> None:
    console = make_console()
    v3_tabs(console, "factory", ["contratacion", "oferta", "doc"])
    body = "\n".join(DOC_TEXT)
    editor = Text(body)
    for tag, _l, _i in TAGS:
        tag = tag[2:-2]
        start = body.find("{{" + tag + "}}")
        while start != -1:
            editor.stylize(f"bold {ACCENT} on {PANEL_BG}", start,
                           start + len(tag) + 4)
            start = body.find("{{" + tag + "}}", start + 1)
    console.print(Align.center(Panel(
        editor, title="source — {{tags}} highlighted", title_align="left",
        border_style=WARN, padding=(1, 2), width=74)))
    bar = Text()
    bar.append_text(key_group("edit", [("tab", "preview"), ("ctrl+s", "save"),
                                       ("esc", "cancel")], boxed=False))
    console.print(Align.center(bar))
    save(console, "v3-editor.svg", "V3 deck & tabs — editor")


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------
def build_index() -> None:
    screens = [
        ("home", "Home — four doors, recents, guidance",
         ["v1-home.svg", "v2-home.svg", "v3-home.svg"]),
        ("map", "Map view — tree, selection, ficha",
         ["v1-map.svg", "v2-map.svg", "v3-map.svg"]),
        ("factory", "Document factory — process, preview, tags",
         ["v1-factory.svg", "v2-factory.svg", "v3-factory.svg"]),
        ("editor", "Document editor — source with tags",
         ["v1-editor.svg", "v2-editor.svg", "v3-editor.svg"]),
    ]
    sections = []
    for key, title, svgs in screens:
        figs = []
        for i, svg in enumerate(svgs, 1):
            text = (OUT / svg).read_text(encoding="utf-8")
            if text.startswith("<?xml"):
                text = text.split("?>", 1)[1]
            figs.append(
                f'<div class="term-fig frame" data-variant="v{i}"'
                f'{" hidden" if i > 1 else ""}>{text}</div>')
        sections.append(f'''<section class="screen" data-screen="{key}">
<h2>{title}</h2>
{"".join(figs)}
</section>''')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>mapper — UI fidelity: three chrome systems</title>
<style>
body{{margin:0;background:#0b0f14;color:#c9d1d9;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}
.wrap{{max-width:1240px;margin:0 auto;padding:30px 20px 120px}}
h1{{font-size:22px;color:#00d4ff}}
h2{{font-size:15px;color:#ffcc00;margin:1.6em 0 .5em}}
p.note{{color:#7d8790;max-width:92ch;margin:.3em 0 1.2em;line-height:1.5}}
.term-fig{{margin:12px 0;border:1px solid #1f2733;border-radius:8px;overflow:hidden;background:#000;box-shadow:0 10px 30px rgba(0,0,0,.45)}}
.term-fig svg{{display:block;width:100%;height:auto}}
.switcher{{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);background:#1f2733;border:1px solid #334154;border-radius:999px;padding:8px 18px;display:flex;gap:14px;align-items:center;box-shadow:0 8px 24px rgba(0,0,0,.55);z-index:100}}
.switcher button{{background:#0b0f14;border:1px solid #334154;color:#c9d1d9;border-radius:6px;padding:5px 12px;cursor:pointer;font:inherit}}
.switcher button:hover{{border-color:#00d4ff;color:#00d4ff}}
.switcher .label{{font-weight:bold;color:#00d4ff;min-width:150px;text-align:center}}
</style>
</head>
<body>
<div class="wrap">
<h1>mapper — UI fidelity: three chrome systems, same four screens</h1>
<p class="note">The redesign answers the operator's four points: visual cues
(selection reverse + accent edge, position and step chips, onboarding empty
states), Gestalt separation (chrome on the panel ground, content on the app
ground, controls grouped by category), task guidance (breadcrumb = where am I,
grouped key bar = what can I do, hint line = what's next), and one-app feel
(same frame, keys, palette everywhere). Each screen shows V1 frame &amp; ribbon /
V2 air &amp; rules / V3 deck &amp; tabs — switch with ←/→, move between screens
with ↑/↓.</p>
{"".join(sections)}
</div>

<div class="switcher">
  <button id="prev">←</button>
  <span class="label" id="label">V1 · frame &amp; ribbon</span>
  <button id="next">→</button>
</div>

<script>
const names = ['V1 · frame & ribbon', 'V2 · air & rules', 'V3 · deck & tabs'];
const screens = [...document.querySelectorAll('.screen')];
let v = 0, s = 0;
function apply() {{
  screens.forEach((sc, si) => {{
    sc.hidden = false;
    sc.querySelectorAll('.frame').forEach((el, vi) => el.hidden = vi !== v);
    sc.style.opacity = si === s ? 1 : 0.45;
  }});
  document.getElementById('label').textContent = names[v];
}}
function step(dv) {{ v = (v + dv + 3) % 3; apply(); }}
function jump(ds) {{ s = (s + ds + screens.length) % screens.length;
  screens[s].scrollIntoView({{behavior:'smooth'}}); apply(); }}
document.getElementById('prev').addEventListener('click', () => step(-1));
document.getElementById('next').addEventListener('click', () => step(1));
document.addEventListener('keydown', e => {{
  if (['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) return;
  if (e.key === 'ArrowLeft') step(-1);
  if (e.key === 'ArrowRight') step(1);
  if (e.key === 'ArrowUp') {{ e.preventDefault(); jump(-1); }}
  if (e.key === 'ArrowDown') {{ e.preventDefault(); jump(1); }}
}});
apply();
</script>
</body>
</html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    v1_home(); v1_map(); v1_factory(); v1_editor()
    v2_home(); v2_map(); v2_factory(); v2_editor()
    v3_home(); v3_map(); v3_factory(); v3_editor()
    build_index()
    print("done")
