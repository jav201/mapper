"""mapper — the WELCOME round: every view gets its appeal, darkside-compliant.

Run: python prototypes/ui_welcome/generate.py
Outputs: out/*.svg + index.html

What the references taught (desk · s19_app · taskboard), applied to mapper
WITHOUT breaking the darkside laws:
  - desk: empty states are SENTENCES, never zeroes; one hero per surface.
  - s19_app: never mount blank — the status says "Ready." from construction;
    the help triad (?, ctrl+p, the keybar) is always discoverable.
  - taskboard: the aperture — a glance surface with a drawn identity element.
  - darkside laws stay: blue only on interactivity, grey steps, no borders,
    lowercase, computed moon, solid selection, 300 ms breath.

Views: W1 home-as-aperture · W2 first-run welcome · W3 map with rail +
inspector · W4 factory · W5 the help surface.
"""
from __future__ import annotations

import os
import sys
from datetime import date
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

group_box = darkside.group_box

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

GROUND = darkside.GROUND
PANEL = darkside.PANEL
STEP = darkside.STEP
INK = darkside.INK
MUT = darkside.MUT
ACCENT = darkside.ACCENT
WARN = darkside.WARN
ALERT = darkside.ALERT
WORDMARK = darkside.WORDMARK

TODAY = date(2026, 8, 18)
WEEKDAYS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado",
            "domingo")
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre")


def make_console(w: int = 118, h: int = 30) -> Console:
    return Console(record=True, width=w, height=h, force_terminal=True,
                   color_system="truecolor",
                   file=open(os.devnull, "w", encoding="utf-8"))


def save(console: Console, name: str, title: str) -> None:
    console.save_svg(str(OUT / name), title=title)
    print(f"wrote {name}")


# --- the identity block (the aperture's drawn type) --------------------------
_WORD5 = {
    "m": ("#  #", "####", "####", "#  #", "#  #"),
    "a": (" ## ", "#  #", "####", "#  #", "#  #"),
    "p": ("### ", "#  #", "### ", "#   ", "#   "),
    "e": ("####", "#   ", "####", "#   ", "####"),
    "r": ("### ", "#  #", "### ", "#  #", "#  #"),
}


def bigword(word: str, tone: str) -> Text:
    rows = [""] * 5
    for ch in word:
        g = _WORD5.get(ch)
        if g:
            for i in range(5):
                rows[i] += g[i].replace("#", "█") + " "
    t = Text()
    for r in rows:
        t.append(r.rstrip() + "\n", style=tone)
    return t


def date_line() -> Text:
    return Text(f"{WEEKDAYS[TODAY.weekday()]} {TODAY.day} de "
                f"{MESES[TODAY.month - 1]}", style=MUT)


RECENTS = [("sistema-legacy", "legacy", 24, 3, 4, 5),
           ("lanzamiento-q3", "concept", 12, 0, 0, 0),
           ("contratacion", "factory", 8, 8, 5, 5),
           ("mapper", "repo", 46, 0, 0, 0)]


# ---------------------------------------------------------------------------
# W1 · home as the aperture
# ---------------------------------------------------------------------------
def w1_home() -> None:
    console = make_console()
    console.print(darkside.tab_strip("c"))
    console.print()

    # the identity block: drawn type + computed moon + the date
    glyph, phase = darkside.moon(TODAY)
    brand = Text()
    brand.append_text(bigword("mapper", WORDMARK))
    brand.append(f"\n{glyph} {phase}", style=STEP)
    brand.append("  ·  mapas vivos", style=WORDMARK)
    right = Text()
    right.append("hoy\n", style=STEP)
    right.append_text(date_line())
    console.print(Columns([Align.left(brand), Align.right(right)],
                          equal=False, expand=True))
    console.print()

    # the workspace pulse: counts + the step-meter coverage (darkside's
    # quantity idiom), one row of facts, never zeroes
    pulse = Text()
    pulse.append("  workspace   ", style=STEP)
    pulse.append("4 mapas", style=INK)
    pulse.append(" · 90 nodos · 11 docs", style=MUT)
    pulse.append("    cobertura  ", style=STEP)
    pulse.append_text(darkside.step_meter(9, 13))
    pulse.append("  67%", style=MUT)
    console.print(group_box(pulse, 2))

    # resume row (the one blue affordance in the middle)
    resume = Text()
    resume.append(" ↩ retomar  ", style=f"bold #000000 on {ACCENT}")
    resume.append("  sistema-legacy  /  auth", style=INK)
    resume.append("   última sesión hace 2h", style=MUT)
    console.print(group_box(resume, 2))
    console.print()

    # the recents rail: per-map kind chip + mini coverage meter
    table = Table(box=None, padding=(0, 2), expand=True)
    table.add_column(style=INK)
    table.add_column(style=MUT)
    table.add_column(justify="right", style=MUT)
    table.add_column(justify="right", style=MUT)
    table.add_column(justify="right", style=MUT)
    for name, kind, nodes, docs, have, req in RECENTS:
        meter = Text()
        if req:
            meter.append_text(darkside.step_meter(have, req))
        else:
            meter.append("—", style=STEP)
        table.add_row(f"▐ {name}", Text(f" {kind} ", style=f"{INK} on {STEP}"),
                      f"{nodes} nodos", f"{docs} docs" if docs else "—",
                      meter)
    console.print(group_box(table, 2))
    console.print()

    footer = Text()
    footer.append("siguiente ▸ ", style=STEP)
    footer.append("j/k elige · ", style=MUT)
    footer.append("↵", style=ACCENT)
    footer.append(" abre · ", style=MUT)
    footer.append("r", style=ACCENT)
    footer.append(" retoma · las puertas son las pestañas de arriba", style=MUT)
    console.print(footer)
    console.print(darkside.keybar(groups_for_keybar(["nav", "doors", "app"])))
    save(console, "w1-home.svg", "W1 — home as aperture")


# ---------------------------------------------------------------------------
# W2 · the first-run welcome (desk: a sentence; s19: never blank)
# ---------------------------------------------------------------------------
def w2_welcome() -> None:
    console = make_console()
    console.print(darkside.tab_strip("c"))
    console.print()

    glyph, phase = darkside.moon(TODAY)
    brand = Text()
    brand.append_text(bigword("mapper", WORDMARK))
    brand.append(f"\n{glyph} {phase}  ·  mapas vivos", style=WORDMARK)
    console.print(Align.center(brand))
    console.print()

    hello = Text()
    hello.append("bienvenido. esto es un lienzo para mapas vivos:\n", style=INK)
    hello.append("cada nodo es una ficha — con notas, documentos y tags; ", style=MUT)
    hello.append("nunca un nodo mudo.\n", style=MUT)
    console.print(Align.center(hello))

    # a ghost mini-map as the taste (desk: the preview IS the onboarding)
    ghost = Text()
    ghost.append("         ▐ módulo\n", style=STEP)
    ghost.append("        ┌┴─┐\n", style=STEP)
    ghost.append("     ▐ api   ▐ ui\n", style=STEP)
    ghost.append("       └────┘", style=STEP)
    console.print(Align.center(ghost))
    console.print()

    doors = Text()
    for key, label in (("c", "consult maps"), ("p", "plug repo"),
                       ("n", "construct"), ("f", "document factory")):
        doors.append(f" {key} ", style=f"bold #000000 on {ACCENT}"
                     if key == "n" else f"bold {ACCENT} on {STEP}")
        doors.append(f" {label}   ", style=MUT if key != "n" else INK)
    console.print(Align.center(doors))
    console.print()

    nxt = Text()
    nxt.append("siguiente ▸ ", style=STEP)
    nxt.append("empieza con ", style=MUT)
    nxt.append("n", style=ACCENT)
    nxt.append(" — un mapa nuevo nace con una semilla de 3 nodos", style=MUT)
    console.print(Align.center(nxt))
    save(console, "w2-welcome.svg", "W2 — first-run welcome")


# ---------------------------------------------------------------------------
# W3 · map with rail + inspector ficha + active path
# ---------------------------------------------------------------------------
_TREE = [
    ("sistema-legacy", 0, False, "root"),
    ("core", 1, False, "node"),
    ("auth", 2, True, "sel"),                      # the selected node
    ("db", 2, False, "node"),
    ("api", 2, False, "alert"),
    ("frontend", 1, False, "node"),
    ("ui", 2, False, "node"),
    ("state", 2, False, "alert"),
]


def w3_map() -> None:
    console = make_console()
    console.print(darkside.tab_strip("c", ["sistema-legacy", "auth"]))

    # left rail carries the tree guides (darkside layout); the active path to
    # root reads in blue, the rest in grey steps (the D-A lesson on layered)
    on_path = {"sistema-legacy", "core", "auth"}
    tree = Text()
    for name, depth, sel, kind in _TREE:
        active = name in on_path
        guide_tone = ACCENT if active else STEP
        spine = "▐ " if depth == 0 else "│ " * (depth - 1) + ("├─▐ " if True else "")
        t = Text()
        t.append("  ", style=GROUND)
        t.append("│ " * (depth - 1), style=STEP)
        if depth:
            t.append("├─▐ ", style=guide_tone)
        else:
            t.append("▐ ", style=guide_tone)
        if sel:
            t.append(f" {name}      ◫ D-2024-001 ",
                     style=f"bold #000000 on {ACCENT}")
        elif kind == "alert":
            t.append(name, style=MUT)
            t.append("      ◫ ", style=STEP)
            t.append("SIN ACTA", style=ALERT)
        else:
            doc = {"auth": "D-2024-001", "db": "D-2024-002",
                   "ui": "D-2024-003"}.get(name, "")
            t.append(name, style=INK if kind == "root" else MUT)
            if doc:
                t.append("      ◫ ", style=STEP)
                t.append(doc, style=MUT)
        tree.append_text(t)
        tree.append("\n")
    console.print(group_box(tree, 2))
    console.print()

    # the ficha as an inspector: chips + step meter, grouped
    insp = Table(box=None, padding=(0, 2))
    insp.add_column(style=STEP)
    insp.add_column(style=INK)
    insp.add_row("▸ auth", "componente crítico · 2 sub")
    insp.add_row("doc", Text("D-2024-001", style=INK))
    insp.add_row("owner", "@carlos · creado 2024")
    insp.add_row("cobertura", Text.assemble(
        darkside.step_meter(4, 5), ("  4/5", MUT)))
    insp.add_row("notas", "el login viejo sigue en producción")
    console.print(group_box(insp, 2))
    console.print()

    nxt = Text()
    nxt.append("siguiente ▸ ", style=STEP)
    nxt.append("auth tiene 2 sub-nodos — ", style=MUT)
    nxt.append("l", style=ACCENT)
    nxt.append(" baja, ", style=MUT)
    nxt.append("h", style=ACCENT)
    nxt.append(" sube, ", style=MUT)
    nxt.append("↵", style=ACCENT)
    nxt.append(" abre la ficha", style=MUT)
    console.print(nxt)
    console.print(darkside.keybar(groups_for_keybar(["nav", "node", "view",
                                                     "app"])))
    save(console, "w3-map.svg", "W3 — map with rail + inspector")


# ---------------------------------------------------------------------------
# W4 · factory with the same chrome
# ---------------------------------------------------------------------------
_FACT_TREE = [
    "                    ┌─▐ requisición  ◫",
    "                    │",
    "▐ contratacion  ◫ ──┼─▐ aprobacion  ◫",
    "                    │",
    "                    ├─▐ oferta  ◫",
    "                    │",
    "                    └─▐ onboarding  ◫",
]


def w4_factory() -> None:
    console = make_console()
    console.print(darkside.tab_strip("f", ["contratacion", "oferta"]))

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

    tree = Text("\n".join(_FACT_TREE))
    joined = "\n".join(_FACT_TREE)
    off = joined.index("├─▐ oferta")
    tree.stylize(f"bold #000000 on {ACCENT}", off, off + len("├─▐ oferta  ◫"))

    prev = Text()
    prev.append("documento: oferta.docx   ", style=INK)
    prev.append("preview (tags resolved)\n", style=MUT)
    prev.append("estimado/a candidato/a,\n\nle extendemos la oferta para el "
                "puesto ")
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
    for tag, local, inh in (("{{puesto}}", "ingeniero de datos", "—"),
                            ("{{ubicacion}}", "remoto", "—"),
                            ("{{depto}}", "—", "plataforma"),
                            ("{{director}}", "—", "—"), ("{{salario}}", "—",
                                                         "—")):
        tags.add_row(tag, local, inh)
    console.print(Columns([group_box(tree, 2), group_box(prev, 2),
                           group_box(tags, 1)], equal=False, padding=(0, 1)))
    console.print()

    nxt = Text()
    nxt.append("siguiente ▸ ", style=STEP)
    nxt.append("oferta hereda {{depto}} de contratacion — ", style=MUT)
    nxt.append("d", style=ACCENT)
    nxt.append(" edita el documento", style=MUT)
    console.print(nxt)
    console.print(darkside.keybar(groups_for_keybar(["nav", "doc", "app"])))
    save(console, "w4-factory.svg", "W4 — factory")


# ---------------------------------------------------------------------------
# W5 · the help surface (s19's triad: every live key, grouped)
# ---------------------------------------------------------------------------
def w5_help() -> None:
    console = make_console()
    console.print(darkside.tab_strip("c", ["help"]))
    console.print()

    intro = Text()
    intro.append("  cada tecla mostrada funciona; cada tecla que funciona se "
                 "muestra.\n", style=INK)
    intro.append("  las tres puertas de la ayuda: la barra abajo · ", style=MUT)
    intro.append("ctrl+p", style=ACCENT)
    intro.append(" paleta · ", style=MUT)
    intro.append("?", style=ACCENT)
    intro.append(" esta pantalla.", style=MUT)
    console.print(group_box(intro, 2))
    console.print()

    groups = [("nav", [("j/k", "mover"), ("h/l", "nivel"), ("↵", "abrir"),
                       ("tab", "vista")]),
              ("node", [("a", "añadir"), ("d", "documento"), ("x", "archivar"),
                        ("u", "deshacer")]),
              ("view", [("v", "ciclar"), ("/", "buscar"), ("f", "foco"),
                        ("e", "exportar")]),
              ("map", [("r", "reporte"), ("=", "diff vs HEAD"),
                       ("m", "mapas enlazados"), ("i", "importar csv")]),
              ("app", [("ctrl+p", "paleta"), ("?", "ayuda"), ("q", "salir")])]
    table = Table(box=None, padding=(0, 2), expand=True)
    table.add_column(style=STEP)
    table.add_column(style=MUT)
    for gname, pairs in groups:
        first = True
        for k, label in pairs:
            table.add_row(gname if first else "", Text(f"{k}", style=ACCENT)
                          + Text(f"  {label}", style=MUT))
            first = False
    console.print(group_box(table, 2))
    console.print()

    nxt = Text()
    nxt.append("siguiente ▸ ", style=STEP)
    nxt.append("esc vuelve a donde estabas", style=MUT)
    console.print(nxt)
    save(console, "w5-help.svg", "W5 — help surface")


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------
def build_index() -> None:
    svgs = [
        ("w1-home.svg", "W1 — home as aperture (identity + pulse + rail + resume)"),
        ("w2-welcome.svg", "W2 — first-run welcome (a sentence, never blank)"),
        ("w3-map.svg", "W3 — map with rail, inspector ficha, active path"),
        ("w4-factory.svg", "W4 — factory with step chips + preview + tags"),
        ("w5-help.svg", "W5 — help surface (every live key, grouped)"),
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
<title>mapper — the welcome round</title>
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
<h1>mapper — the welcome round</h1>
<p class="note">Visual appeal + a welcoming entry, darkside-compliant. Lessons:
desk (empty states are sentences), s19_app (never mount blank, the help triad),
taskboard (the aperture). Regenerate with
<code>python prototypes/ui_welcome/generate.py</code>.</p>
{"".join(rows)}
</div>
</body>
</html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    w1_home()
    w2_welcome()
    w3_map()
    w4_factory()
    w5_help()
    build_index()
    print("done")
