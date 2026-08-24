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
# D-A · the radial map in darkside — the language's answer to branch colours
# ---------------------------------------------------------------------------
def ds_mental() -> None:
    """Branch hues are ANTI-darkside (colour on passive data). The language's
    answer: the whole map in grey steps, and ONLY the active path
    (root → selected node) in KMBlue. The selected node is the solid block."""
    import math as _math
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).resolve().parents[2]
                            .parent / "taskboard" / "prototypes" / "mapper"))
    import proto as mp                          # the mapper prototype's engine

    MENTAL = mp.N(
        "m", "mapper", "", "el producto",
        children=(
            mp.N("fuentes", "fuentes", children=(
                mp.N("c1", "conceptos"), mp.N("c2", "github"),
                mp.N("c3", "mermaid"))),
            mp.N("fichas", "fichas", children=(
                mp.N("c4", "notas"), mp.N("c5", "documentos"),
                mp.N("c6", "tags"), mp.N("c7", "estados"))),
            mp.N("vistas", "vistas", children=(
                mp.N("c8", "canvas"), mp.N("c9", "outline"),
                mp.N("c10", "export"))),
            mp.N("nav", "navegación", children=(
                mp.N("c11", "salto /"), mp.N("c12", "foco"))),
        ))
    SEL = "c5"                                   # documentos — the active path

    console = make_console()
    console.print(darkside.tab_strip("c", ["mapper", "fichas", "documentos"]))

    # the radial layout, reused from the mapper prototype
    inner, body_h = 116, 26
    all_nodes = []

    def gather(n):
        all_nodes.append(n)
        for ch_ in n.children:
            gather(ch_)
    gather(MENTAL)

    cv = mp.Canvas(inner, body_h)
    cv.dots = {}
    cv.bgs = {}

    def leaves(n):
        return 1 if not n.children else sum(leaves(c) for c in n.children)

    pos = {}
    cx0, cy0 = 12, body_h // 2
    level_r = (0, max(12, inner // 4), max(24, inner // 2 - 3))
    span = 1.75
    squash = min(0.55, max(0.3, (cy0 - 1) / (level_r[2] * _math.sin(span / 2))))

    def place(n, level, a0, a1):
        a = (a0 + a1) / 2
        r = level_r[min(level, 2)]
        pos[n.id] = (cx0 + r * _math.cos(a), cy0 + r * _math.sin(a) * squash)
        acc = a0
        for ch_ in n.children:
            frac = leaves(ch_) / max(1, sum(leaves(c) for c in n.children))
            place(ch_, level + 1, acc, acc + frac * (a1 - a0))
            acc += frac * (a1 - a0)

    place(MENTAL, 0, 0, 0)
    acc = -span / 2
    total = sum(leaves(c) for c in MENTAL.children) or 1
    for ch_ in MENTAL.children:
        frac = leaves(ch_) / total
        place(ch_, 1, acc, acc + frac * span)
        acc += frac * span

    # the active path: the selected node and its ancestors
    on_path = set()
    n_ = next(n for n in all_nodes if n.id == SEL)
    while n_ is not None:
        on_path.add(n_.id)
        n_ = n_.parent

    def curve(x0, y0, x1, y1, tone, w0, bow=0.14):
        X0, Y0, X1, Y1 = x0 * 2, y0 * 4, x1 * 2, y1 * 4
        mx, my = (X0 + X1) / 2, (Y0 + Y1) / 2
        dx, dy = X1 - X0, Y1 - Y0
        dist = max(1.0, _math.hypot(dx, dy))
        cxq, cyq = mx - dy * bow, my + dx * bow
        steps = int(dist * 1.6)
        for i in range(steps + 1):
            t = i / steps
            bx = (1 - t) ** 2 * X0 + 2 * (1 - t) * t * cxq + t ** 2 * X1
            by = (1 - t) ** 2 * Y0 + 2 * (1 - t) * t * cyq + t ** 2 * Y1
            r = w0 + (0.35 - w0) * t
            rr = int(round(r))
            for ox in range(-rr, rr + 1):
                for oy in range(-rr, rr + 1):
                    if ox * ox + oy * oy <= r * r:
                        cv.dots[(round(bx + ox), round(by + oy))] = tone

    for n in all_nodes:
        if n.parent is not None:
            x0, y0 = pos[n.parent.id]
            x1, y1 = pos[n.id]
            active = n.id in on_path and n.parent.id in on_path
            level = 0
            m = n
            while m.parent is not None:
                m = m.parent
                level += 1
            tone = (ACCENT if active else
                    ("#4a4a4a" if level == 1 else STEP))
            curve(x0, y0, x1, y1, tone, 1.6 if n.parent is MENTAL else 0.8)

    for n in all_nodes:
        x1, y1 = pos[n.id]
        sel = n.id == SEL
        path = n.id in on_path
        level = 0
        m = n
        while m.parent is not None:
            m = m.parent
            level += 1
        title = mp.clip(n.title, 22)
        cw = mp.vis(title) + 3
        x = max(0, min(inner - cw, int(x1) - (0 if level == 0 else cw // 2)))
        y = int(y1)
        for j in range(cw):
            cv.bgs[(x + j, y)] = PANEL
        for j, ch in enumerate(" " + mp.fit(title, cw - 2)):
            cv.put(x + j, y, ch, "ink" if not sel else "ink@")
        cv.put(x, y, "●" if level else "◆",
               "accent" if path else ("mut" if level <= 1 else "dim"))

    console.print()
    for r in cv.rows():
        console.print(r)
    console.print()
    strip = Text()
    strip.append("▸ documentos", style=INK)
    strip.append("   camino: mapper / fichas / documentos", style=MUT)
    console.print(group_box(strip))
    console.print()
    footer(console,
           [("nav", [("j/k", "mover"), ("h/l", "nivel"), ("↵", "ficha")]),
            ("view", [("v", "cycle"), ("/", "buscar")]),
            ("app", [("ctrl+p", "palette"), ("?", "help"), ("q", "home")])],
           "el camino activo es lo único azul — v cicla a otra vista", "v")
    save(console, "ds-mental.svg", "darkside — radial, active path")








# ---------------------------------------------------------------------------
# D-B · motion: 300 ms in_out_cubic — the selection BREATHES, never snaps
# ---------------------------------------------------------------------------
def _mix_hex(a: str, b: str, t: float) -> str:
    ar = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    br = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(ar[i] + (br[i] - ar[i]) * t)
                                   for i in range(3))


def _in_out_cubic(t: float) -> float:
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ds_motion() -> None:
    """Six frames of a 300 ms selection move (auth → db), the in_out_cubic
    curve applied to the solid block's fade — the tempo law made visible."""
    FRAMES = [_in_out_cubic(i / 5) for i in range(6)]

    def map_at(t: float) -> None:
        console = make_console()
        console.print(darkside.tab_strip("c", ["sistema-legacy", "auth → db"]))
        tree = Text()
        for row, kind in TREE_ROWS:
            if kind == "sel":                    # auth — leaving
                tree.append("  │  ├─▐ ", style=MUT)
                tree.append(" auth      ◫ D-2024-001 ",
                            style=f"bold {_mix_hex('#000000', INK, t)} on "
                                  f"{_mix_hex(ACCENT, PANEL, t)}")
            elif row.strip().startswith("├─▐ db"):   # db — arriving
                tree.append("  │  ├─▐ ", style=MUT)
                tree.append(" db        ◫ D-2024-002 ",
                            style=f"bold {_mix_hex(INK, '#000000', t)} on "
                                  f"{_mix_hex(PANEL, ACCENT, t)}")
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
        strip.add_row("▸ auth" if t < 0.5 else "▸ db",
                      "componente crítico · 2 sub")
        strip.add_row("doc", Text("D-2024-001", style=INK))
        strip.add_row("owner", "@carlos · creado 2024")
        strip.add_row("cobertura", darkside.step_meter(4, 5))
        console.print(group_box(strip))
        console.print()
        footer(console, groups_for_keybar(["nav", "node", "view", "app"]),
               f"300 ms in_out_cubic · frame t={t:.2f}", "j/k")
        save(console, f"ds-motion-f{FRAMES.index(t)}.svg",
             f"darkside — motion t={t:.2f}")

    for t in FRAMES:
        map_at(t)


# ---------------------------------------------------------------------------
# D-C · home with the identity moment — recessive wordmark, computed moon
# ---------------------------------------------------------------------------
_WORD5 = {                       # a tiny 4x5 block font for the wordmark
    "m": ("#  #", "####", "####", "#  #", "#  #"),
    "a": (" ## ", "#  #", "####", "#  #", "#  #"),
    "p": ("### ", "#  #", "### ", "#   ", "#   "),
    "e": ("####", "#   ", "####", "#   ", "####"),
    "r": ("### ", "#  #", "### ", "#  #", "#  #"),
}


def _bigword(word: str, tone: str) -> Text:
    rows = [""] * 5
    for ch in word:
        g = _WORD5.get(ch)
        if g:
            for i in range(5):
                rows[i] += g[i].replace("#", "█").replace(" ", " ") + " "
    t = Text()
    for r in rows:
        t.append(r + "\n", style=tone)
    return t


def ds_home_identity() -> None:
    """The home's identity moment: the big recessive wordmark beside the
    computed moon, the recents rail — darkside's wordmark law, carried."""
    console = make_console()
    console.print(darkside.tab_strip("c"))
    console.print()

    glyph, phase_name = darkside.moon(date.today())
    brand = Text()
    brand.append_text(_bigword("mapper", WORDMARK))
    brand.append(f"\n  {glyph} {phase_name}", style=STEP)
    brand.append("   — mapas vivos", style=WORDMARK)

    recent = Table(box=None, padding=(0, 2), expand=False)
    recent.add_column(style=INK)
    recent.add_column(style=MUT)
    recent.add_column(justify="right", style=MUT)
    for name, kind, nodes, docs in RECENTS:
        recent.add_row(f"▐ {name}", Text(f" {kind} ", style=f"{MUT} on {STEP}"),
                       f"{nodes} nodos")
    body = Columns([group_box(recent, 2), brand], equal=False, padding=(0, 3))
    console.print(body)
    console.print()

    footer(console,
           groups_for_keybar(["nav", "doors", "app"]),
           "j/k elige · ↵ abre · la marca es recesiva a propósito", "↵")
    save(console, "ds-home-identity.svg", "darkside — home, identity moment")




# ---------------------------------------------------------------------------
# repo plug — connect by local path or URL (plain git first, gh as enrichment)
# ---------------------------------------------------------------------------
def ds_repo_plug() -> None:
    """The plug screen: one input that accepts a local path OR a URL; the
    source detection is automatic; the preview says what the map will carry.
    Plain `git` gives branches/commits/tags with no auth — the gh layer (CI,
    PRs) is an optional enrichment on top."""
    console = make_console()
    console.print(darkside.tab_strip("p"))
    console.print()

    inp = Text()
    inp.append("  ruta o url ▸ ", style=MUT)
    inp.append("/home/jav201/repos/mapper", style=INK)
    inp.append("▌", style=ACCENT)
    console.print(group_box(inp, 2))

    det = Text()
    det.append("  detectado: ", style=STEP)
    det.append(" repo local de git ", style=f"{INK} on {STEP}")
    det.append("   leer con git plano — sin auth, sin API", style=MUT)
    console.print(det)
    console.print()

    stats = Table(box=None, padding=(0, 2))
    stats.add_column(style=MUT)
    stats.add_column(style=INK)
    stats.add_row("ramas", "12 (4 activas este mes)")
    stats.add_row("tags / releases", "4 · último v1.2.0")
    stats.add_row("commits", "312 · último hace 2h")
    stats.add_row("autor principal", "@jav201")
    console.print(group_box(stats, 2))
    console.print()

    alt = Text()
    alt.append("  también: ", style=STEP)
    alt.append("https://github.com/jav201/mapper", style=INK)
    alt.append("  → se clona al cache y se lee igual", style=MUT)
    alt.append("   (+ gh enriquece con CI y PRs si está autenticado)",
               style=STEP)
    console.print(alt)
    console.print()

    footer(console,
           groups_for_keybar(["nav", "doors", "app"]),
           "↵ conecta y mapea — una ruta local lee en el sitio, una url clona al cache",
           "↵")
    save(console, "ds-repo-plug.svg", "darkside — repo plug, path or url")




# ---------------------------------------------------------------------------
# factory with a REAL office template — the .docx/.pptx/.xlsx ingestion
# ---------------------------------------------------------------------------
def ds_factory_office() -> None:
    """The template is a real office file with {{tags}} inside; mapper ingests
    it directly (OOXML = a zip of XML — no external parser needed, probed this
    round). The factory shows the file source, the parsed tags, and the
    preview resolved against the selected node."""
    console = make_console()
    console.print(darkside.tab_strip("f", ["contratacion", "oferta"]))
    console.print()

    src = Text()
    src.append("  template ▸ ", style=MUT)
    src.append("oferta.docx", style=INK)
    src.append("  ·  ", style=STEP)
    src.append("archivo real ingerido", style=MUT)
    src.append("   (docx = zip+xml: los {{tags}} se leen directo)", style=STEP)
    console.print(group_box(src, 2))
    console.print()

    tree = Text("\n".join(FACT_TREE))
    joined = "\n".join(FACT_TREE)
    off = joined.index("├─▐ oferta")
    tree.stylize(f"bold #000000 on {ACCENT}", off, off + len("├─▐ oferta  ◫"))
    console.print(tree)
    console.print()

    prev = Text()
    prev.append("documento: oferta.docx   ", style=INK)
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
    tags.add_row("tag (del docx)", "local", "inherited")
    for tag, local, inh in TAGS:
        tags.add_row(tag, local, inh)
    console.print(Columns([group_box(prev, 2), group_box(tags, 1)],
                          equal=False, padding=(0, 1)))
    console.print()

    footer(console,
           groups_for_keybar(["nav", "doc", "app"]),
           "t ingesta un .docx/.pptx/.xlsx como template — d edita, tab preview",
           "t")
    save(console, "ds-factory-office.svg", "darkside — factory, real office template")


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------
def build_index() -> None:
    motion = "\n".join(
        f'<div class="term-fig frame" data-frame="{i}"{" hidden" if i else ""}>'
        + (lambda t: t.split("?>", 1)[1] if t.startswith("<?xml") else t)(
            (OUT / f"ds-motion-f{i}.svg").read_text(encoding="utf-8"))
        + "</div>" for i in range(6))
    svgs = [
        ("ds-home.svg", "home — resume row, recents, guidance"),
        ("ds-home-empty.svg", "home — empty state onboarding"),
        ("ds-map.svg", "map — tree, solid selection, ficha"),
        ("ds-factory.svg", "factory — steps, preview, tags"),
        ("ds-editor.svg", "editor — source with tags"),
        ("ds-palette.svg", "command palette — grouped, first match solid"),
        ("ds-mental.svg", "radial — grey steps, ONLY the active path blue"),
        ("ds-home-identity.svg", "home — the identity moment (wordmark + moon)"),
        ("ds-repo-plug.svg", "repo plug — a local path or a URL, plain git first"),
        ("ds-factory-office.svg", "factory — real .docx/.pptx/.xlsx template ingestion"),
    ]
    rows = []
    rows.append("<h2>motion — the 300 ms selection breath (flipbook)</h2>"
                + '<div class="flipbook" id="motion">' + motion + "</div>")
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
    ds_mental()
    ds_motion()
    ds_home_identity()
    ds_repo_plug()
    ds_factory_office()
    build_index()
    print("done")

