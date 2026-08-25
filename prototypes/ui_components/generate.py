"""mapper × darkside — the component sheet round.

C1 is the settings-screen canary: every interaction-layer component of the
darkside language in its three states (default / focused / disabled) — the
place where a fake language hides. C2-C4 wire the new components into the
real views: home KPIs + sparkline, map accordion + pagination + toast,
repo-plug skeleton + spinner.

Run: python prototypes/ui_components/generate.py
Outputs: out/*.svg + index.html
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the mapper package importable from this prototype directory.
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rich.console import Console
from rich.table import Table
from rich.text import Text

from mapper import darkside
from mapper.keymap import groups_for_keybar

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

ON_ACCENT = f"bold {GROUND} on {ACCENT}"


def make_console(w: int = 118, h: int = 34) -> Console:
    # rich 15 law: Console.size honours _width ONLY when _height is set too.
    return Console(record=True, width=w, height=h, force_terminal=True,
                   color_system="truecolor",
                   file=open(os.devnull, "w", encoding="utf-8"))


def save(console: Console, name: str, title: str) -> None:
    console.save_svg(str(OUT / name), title=title)
    print(f"wrote {name}")


def footer(console, groups, hint: str, hint_key: str | None = None) -> None:
    console.print()
    console.print(darkside.hint_line(hint, hint_key))
    console.print(darkside.keybar(groups))


# --- component primitives (darkside mechanisms, not colour) -------------------
def sw(active: bool, state: str = "default") -> Text:
    """Switch: word flip. The active word wears the blue block."""
    if state == "disabled":
        return Text.assemble((" on ", STEP), (" "), (" off ", STEP))
    on_style = ON_ACCENT if active else f"{MUT} on {STEP}"
    off_style = ON_ACCENT if not active else f"{MUT} on {STEP}"
    edge = ("▐", ACCENT) if state == "focused" else (" ", "")
    return Text.assemble(edge, (" on ", on_style), (" "), (" off ", off_style))


def stepper(value: int, state: str = "default") -> Text:
    """Stepper: - value + — the ± carry the affordance."""
    if state == "disabled":
        return Text.assemble(("  - ", STEP), (f" {value} ", STEP), (" + ", STEP))
    minus = ON_ACCENT if state == "focused" else ACCENT
    plus = ON_ACCENT if state == "focused" else ACCENT
    return Text.assemble(("  - ", minus), (f" {value} ", INK), (" + ", plus))


def slider(ratio: float, state: str = "default", width: int = 18) -> Text:
    """Slider: track STEP, fill INK, handle a blue block."""
    pos = max(0, min(width - 1, round(ratio * (width - 1))))
    if state == "disabled":
        return Text("─" * width, style=STEP)
    parts: list[tuple[str, str]] = []
    for i in range(width):
        if i == pos:
            parts.append(("▮", ON_ACCENT if state == "focused" else ACCENT))
        elif i < pos:
            parts.append(("━", INK))
        else:
            parts.append(("─", STEP))
    return Text.assemble(*parts)


def segmented(options: list[str], active: int, state: str = "default") -> Text:
    """Segmented control: the tab strip's little sibling."""
    parts: list[tuple[str, str]] = []
    if state == "focused":
        parts.append(("▐", ACCENT))
    for i, opt in enumerate(options):
        if i > 0:
            parts.append((" ", ""))
        if state == "disabled":
            parts.append((f" {opt} ", f"{STEP} on {PANEL}"))
        elif i == active:
            parts.append((f" {opt} ", ON_ACCENT))
        else:
            parts.append((f" {opt} ", f"{MUT} on {STEP}"))
    return Text.assemble(*parts)


def spinner(frame: int = 0, label: str = "cargando…", state: str = "default") -> Text:
    """Braille spinner: the frame is motion, the colour is the affordance."""
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    glyph = frames[frame % len(frames)]
    if state == "disabled":
        return Text.assemble(("· ", STEP), (label, STEP))
    return Text.assemble((f"{glyph} ", ACCENT), (label, MUT))


def text_field(value: str, state: str = "default",
               placeholder: str = "nombre del mapa…") -> Text:
    """Text field: cursor ▌ blue, placeholder STEP."""
    if state == "disabled":
        return Text(f" {value or placeholder} ", style=STEP)
    if state == "focused":
        return Text.assemble(("▌", ACCENT), (value, INK))
    if value:
        return Text(f" {value} ", style=MUT)
    return Text(f" {placeholder} ", style=STEP)


def pagination(page: int, total: int, state: str = "default") -> Text:
    """Pagination: ‹ n/m › — number INK, arrows blue."""
    if state == "disabled":
        return Text.assemble((" ‹ ", STEP), (f"{page}/{total}", STEP), (" › ", STEP))
    arrow = ON_ACCENT if state == "focused" else ACCENT
    return Text.assemble((" ‹ ", arrow), (f"{page}/{total}", INK), (" › ", arrow))


def chip(name: str, state: str = "default") -> Text:
    """Tag chip: [name] over STEP; focused wears the blue block."""
    if state == "disabled":
        return Text(f" {name} ", style=f"{STEP} on {PANEL}")
    if state == "focused":
        return Text(f" {name} ", style=ON_ACCENT)
    return Text(f" {name} ", style=f"{INK} on {STEP}")


def skeleton_bar(width: int) -> Text:
    """Skeleton: dim blocks holding the shape of content that is coming."""
    return Text("█" * width, style=STEP)


# ---------------------------------------------------------------------------
# C1 — the settings-screen canary: every component x every state
# ---------------------------------------------------------------------------
def uc_settings() -> None:
    console = make_console()
    console.print(darkside.tab_strip("c", ["consultar", "preferencias"]))
    console.print()

    grid = Table.grid(expand=False)
    grid.add_column(width=15)
    grid.add_column(width=26)
    grid.add_column(width=26)
    grid.add_column(width=26)
    grid.add_row(
        Text("componente", style=STEP),
        Text("default", style=STEP),
        Text("focused", style=STEP),
        Text("disabled", style=STEP),
    )
    grid.add_row(Text(""), Text(""), Text(""), Text(""))

    rows: list[tuple[str, Text, Text, Text]] = [
        ("switch", sw(True), sw(True, "focused"), sw(True, "disabled")),
        ("stepper", stepper(3), stepper(3, "focused"), stepper(3, "disabled")),
        ("slider", slider(0.55), slider(0.55, "focused"), slider(0.55, "disabled")),
        ("segmented", segmented(["luna", "marea", "noche"], 0),
         segmented(["luna", "marea", "noche"], 0, "focused"),
         segmented(["luna", "marea", "noche"], 0, "disabled")),
        ("progress", darkside.step_meter(3, 5),
         darkside.step_meter(3, 5, accent_current=True),
         Text.assemble(*[("▱", STEP)] * 5)),
        ("spinner", spinner(0), spinner(3), spinner(0, "en espera", "disabled")),
        ("text field", text_field(""), text_field("sistema-leg", "focused"),
         text_field("core", "disabled")),
        ("pagination", pagination(2, 5), pagination(2, 5, "focused"),
         pagination(2, 5, "disabled")),
        ("tag chip", chip("legacy"), chip("legacy", "focused"),
         chip("legacy", "disabled")),
    ]
    for name, d, f, dis in rows:
        grid.add_row(Text(name, style=MUT), d, f, dis)
        grid.add_row(Text(""), Text(""), Text(""), Text(""))

    console.print(darkside.group_box(grid, pad_x=2))
    footer(console,
           groups_for_keybar(["nav", "app"]),
           "el foco es el bloque sólido — tab recorre, ↵ acciona",
           "tab")
    save(console, "uc-settings.svg", "darkside — component sheet canary")


# ---------------------------------------------------------------------------
# C2 — home enriched: KPI tiles + activity sparkline + resume + recents rail
# ---------------------------------------------------------------------------
def _kpi_row(tiles: list[tuple[str, str, str, str]]) -> Text:
    """One row of KPI tiles: value INK, label MUT, delta STEP — on STEP."""
    w = 22
    lines = [Text() for _ in range(3)]
    for i, (value, label, delta, delta_style) in enumerate(tiles):
        for line, content, style in zip(
            lines,
            (f" {value}", f" {label}", f" {delta}"),
            (f"bold {INK}", MUT, delta_style),
        ):
            if i > 0:
                line.append("  ", style="")
            line.append(content.ljust(w), style=f"{style} on {STEP}")
    return Text.assemble(*sum(([line, "\n"] for line in lines), [])[:-1])


def uc_home() -> None:
    console = make_console()
    console.print(darkside.tab_strip("c"))
    console.print()

    resume = Text.assemble(
        (" ↩ retomar ", ON_ACCENT),
        ("  sistema-legacy — auth · acta D-2024-001", MUT),
    )
    console.print(resume)
    console.print()

    console.print(_kpi_row([
        ("46", "nodos", "+6 esta semana", MUT),
        ("12", "sin acta", "3 vencen hoy", WARN),
        ("3", "mapas", "1 compartido", MUT),
        ("89 %", "cobertura", "meta 100 %", MUT),
    ]))
    console.print()

    spark = Text.assemble(
        ("actividad 14d  ", MUT),
        *[(ch, STEP if i < 4 else MUT if i < 9 else INK)
          for i, ch in enumerate("▁▂▂▃▂▃▅▃▆▅▆▇▇▅")],
    )
    console.print(darkside.group_box(spark, pad_x=2))
    console.print()

    recents = Table.grid(expand=False)
    recents.add_column(width=3)
    recents.add_column(width=22)
    recents.add_column(width=12)
    recents.add_column(width=24)
    recents.add_column()
    for name, kind, nodes, missing, when in [
            ("sistema-legacy", "legacy", 24, 3, "hace 2 h"),
            ("lanzamiento-q3", "concept", 12, 0, "ayer"),
            ("contratacion", "factory", 8, 8, "hace 3 d"),
            ("mapper", "repo", 46, 0, "hace 5 d")]:
        alert = f" · {missing} sin acta" if missing else ""
        recents.add_row(
            Text("▐", style=ACCENT),
            Text(name, style=INK),
            darkside.kind_chip(kind),
            Text(f"{nodes} nodos{alert}", style=WARN if missing else MUT),
            Text(when, style=MUT),
        )
    console.print(Text("  recientes", style=STEP))
    console.print(darkside.group_box(recents, pad_x=2))
    footer(console,
           groups_for_keybar(["doors", "app"]),
           "↵ abre el mapa reciente — n construye uno nuevo",
           "↵")
    save(console, "uc-home.svg", "darkside — home with KPI tiles and sparkline")


# ---------------------------------------------------------------------------
# C3 — map: accordion disclosure with declared counts + pagination + toast
# ---------------------------------------------------------------------------
def uc_map() -> None:
    console = make_console()
    console.print(darkside.tab_strip("c", ["consultar", "sistema-legacy"]))
    console.print()

    tree = Table.grid(expand=False)
    tree.add_column(width=10)
    tree.add_column()

    def node(prefix: str, name: str, meta: str = "", style: str = INK,
             meta_style: str = MUT) -> None:
        tree.add_row(Text(prefix, style=STEP),
                     Text.assemble((name, style), (f"  {meta}", meta_style)))

    def disclosure(opened: bool, name: str, count: int) -> None:
        glyph = "▾" if opened else "▸"
        tree.add_row(
            Text.assemble(("▐ ", ACCENT), (f"{glyph} ", ACCENT)),
            Text.assemble((name, INK), (f"  {count}", MUT)),
        )

    tree.add_row(Text("▐", style=ACCENT), Text("sistema-legacy", style=INK))
    disclosure(True, "core", 3)
    node("  │  ├─▐", "auth", "◫ D-2024-001")
    tree.add_row(Text("  │  ├─▐", style=STEP),
                 Text.assemble(("db", ON_ACCENT), ("  ◫ D-2024-002", MUT)))
    node("  │  └─▐", "api", "◫ SIN ACTA", meta_style=WARN)
    disclosure(False, "frontend", 5)
    node("     └─▐", "…", "5 nodos plegados", style=MUT, meta_style=STEP)

    ficha = Text.assemble(
        (" db", INK), ("  ", ""), (" nodo ", f"{INK} on {STEP}"), ("\n\n"),
        ("creado", STEP), ("  2024-03-11", MUT), ("\n"),
        ("acta", STEP), ("    D-2024-002 · enlazada", MUT), ("\n"),
        ("tags", STEP), ("    ", ""),
        (" oracle ", f"{INK} on {STEP}"), (" "), (" sin-owner ", f"{INK} on {STEP}"),
        ("\n\n"),
        ("notas — el esquema vive en producción; no hay\nstaging desde 2019. hablar con ops antes de\ntocar secuencias.", MUT),
    )

    body = Table.grid(expand=False)
    body.add_column(width=58)
    body.add_column()
    body.add_row(tree, darkside.group_box(ficha, pad_x=2))
    console.print(body)

    console.print(Text.assemble((" ", ""), pagination(1, 2)))
    console.print()
    toast = Text.assemble(
        (" guardado", f"bold {INK}"), ("   db · notas actualizadas", MUT),
        style=f"on {PANEL}",
    )
    console.print(toast)
    footer(console,
           groups_for_keybar(["nav", "node", "view", "app"]),
           "l pliega/despliega la rama — ctrl+s guarda la ficha",
           "l")
    save(console, "uc-map.svg", "darkside — map accordion, pagination, toast")


# ---------------------------------------------------------------------------
# C4 — repo plug: the fetch state — skeleton + spinner
# ---------------------------------------------------------------------------
def uc_repo() -> None:
    console = make_console()
    console.print(darkside.tab_strip("p", ["repo", "conectar"]))
    console.print()

    console.print(Text.assemble(
        ("url o ruta local\n", MUT),
        ("▌", ACCENT), ("github.com/acme/legacy-core.git", INK), ("\n"),
        ("pega una URL https o una ruta local — plain git primero", STEP),
    ))
    console.print()
    console.print(Text.assemble((" ", ""), (" conectar ", ON_ACCENT),
                                ("  esc cancela", MUT)))
    console.print()

    refs = Table.grid(expand=False)
    refs.add_column(width=60)
    refs.add_row(Text("refs", style=STEP))
    for w in (38, 24, 31, 18, 27, 13):
        refs.add_row(skeleton_bar(w))
    console.print(darkside.group_box(refs, pad_x=2))
    console.print()
    console.print(Text.assemble((" ", ""), spinner(1, "leyendo refs del repo…")))
    footer(console,
           groups_for_keybar(["doors", "app"]),
           "↵ conecta — el skeleton sostiene la forma mientras llega el fetch",
           "↵")
    save(console, "uc-repo.svg", "darkside — repo plug fetch state")


# ---------------------------------------------------------------------------
# round 2 — components matched to the view's PURPOSE
# lessons applied:
#   desk      the hero renders, ambient fields read state, empty states tell
#             the truth, hints carry priorities
#   taskboard the loudest signal wins the hero; the sparkline must not
#             outrank the metric; one hue = one job; empty states name the key
#   s19       distributions are ONE inline microbar strip, not a tile row;
#             a 1-row minimap reads the whole before you open anything
#   gbl       a collapsed header still ANSWERS (counts, not just a name);
#             honesty badges on the source ([github]/[local]); a shared time
#             axis where what aligns vertically happened at the same time
# ---------------------------------------------------------------------------

# Drawn type: the hero number RENDERS, it does not label.
_DIGITS = {
    "0": ("███", "█ █", "█ █", "█ █", "███"),
    "1": (" █ ", "██ ", " █ ", " █ ", "███"),
    "2": ("███", "  █", "███", "█  ", "███"),
    "3": ("███", "  █", " ██", "  █", "███"),
    "4": ("█ █", "█ █", "███", "  █", "  █"),
    "5": ("███", "█  ", "███", "  █", "███"),
    "6": ("███", "█  ", "███", "█ █", "███"),
    "7": ("███", "  █", " █ ", " █ ", " █ "),
    "8": ("███", "█ █", "███", "█ █", "███"),
    "9": ("███", "█ █", "███", "  █", "███"),
}


def draw_number(s: str, style: str = INK) -> Text:
    rows = [Text() for _ in range(5)]
    for ch in s:
        glyph = _DIGITS.get(ch)
        if glyph is None:
            continue
        for i, row in enumerate(glyph):
            rows[i].append(row + " ", style=style)
    return Text.assemble(*sum(([r, "\n"] for r in rows), [])[:-1])


def microbar(count: int, total: int, width: int = 10, fill: str = INK) -> Text:
    """Inline distribution bar (s19): floor=True — present never paints absent.
    Track is WORDMARK: STEP is invisible on the GROUND, it only works on PANEL."""
    if total <= 0 or count <= 0:
        filled = 0
    else:
        filled = max(1, round(count / total * width))
    return Text.assemble(("█" * filled, fill), ("░" * (width - filled), "#3a3a3a"))


# ---------------------------------------------------------------------------
# H2 — home, posture GLANCE: one hero (the loudest signal), everything else
# available rather than prominent
# ---------------------------------------------------------------------------
def uc2_home() -> None:
    console = make_console()
    console.print(darkside.tab_strip("c"))
    console.print()

    # The hero answers the only first question: how much documentation debt
    # does the tree I work on carry — and is any of it urgent TODAY.
    hero = Table.grid(expand=False)
    hero.add_column(width=14)
    hero.add_column(width=34)
    hero.add_column()
    hero.add_row(
        draw_number("12"),
        Text.assemble(
            ("\nnodos sin acta\n", MUT),
            ("sistema-legacy\n", INK),
            ("▲ 3 vencen hoy", WARN),
        ),
        Text.assemble(
            ("actividad 14d\n", STEP),
            # the chart stays in the dim tier — it supports, it never
            # outranks the metric it serves (taskboard hero law)
            *[(ch, MUT if i >= 9 else STEP)
              for i, ch in enumerate("▁▂▂▃▂▃▅▃▆▅▆▇▇▅")],
        ),
    )
    console.print(darkside.group_box(hero, pad_x=2))
    console.print()

    # The distribution is ONE line (s19 microbar strip), not a row of tiles.
    console.print(Text.assemble(
        ("  con acta 34 ", MUT), microbar(34, 46), ("    ", ""),
        ("sin acta 12 ", WARN), microbar(12, 46, fill=WARN), ("    ", ""),
        ("cobertura 74 %", INK),
    ))
    console.print()

    resume = Text.assemble(
        (" ↩ retomar ", ON_ACCENT),
        ("  sistema-legacy — auth · acta D-2024-001", MUT),
    )
    console.print(resume)
    console.print()

    recents = Table.grid(expand=False)
    recents.add_column(width=3)
    recents.add_column(width=22)
    recents.add_column(width=12)
    recents.add_column(width=24)
    recents.add_column()
    for name, kind, nodes, missing, when in [
            ("sistema-legacy", "legacy", 24, 3, "hace 2 h"),
            ("lanzamiento-q3", "concept", 12, 0, "ayer"),
            ("contratacion", "factory", 8, 8, "hace 3 d"),
            ("mapper", "repo", 46, 0, "hace 5 d")]:
        alert = f" · {missing} sin acta" if missing else ""
        recents.add_row(
            Text("▐", style=ACCENT),
            Text(name, style=INK),
            darkside.kind_chip(kind),
            Text(f"{nodes} nodos{alert}", style=WARN if missing else MUT),
            Text(when, style=MUT),
        )
    console.print(Text("  recientes", style=STEP))
    console.print(darkside.group_box(recents, pad_x=2))
    console.print(Text("  (1 mapa archivado — u restaura)", style=MUT))
    footer(console,
           groups_for_keybar(["doors", "app"]),
           "↵ abre el mapa reciente — n construye uno nuevo",
           "↵")
    save(console, "uc2-home.svg", "darkside — home, glance posture, one hero")


# ---------------------------------------------------------------------------
# M2 — map, posture OPERATED+READ: the ficha is the payload, the tree carries
# state inline, and a collapsed branch still answers
# ---------------------------------------------------------------------------
def uc2_map() -> None:
    console = make_console()
    console.print(darkside.tab_strip("c", ["consultar", "sistema-legacy"]))
    console.print()

    # Coverage minimap (s19 memstrip): one row reads the whole tree's state
    # before a single node is opened. ╱ = sin datos, a separator not a count.
    console.print(Text.assemble(
        ("  cobertura   ", MUT),
        ("core ", MUT), ("█", INK), ("   ", ""),
        ("api ", MUT), ("░", WARN), ("   ", ""),
        ("frontend ", MUT), ("▒", MUT), ("   ", ""),
        ("db ", MUT), ("█", INK), ("   ", ""),
        ("docs ", MUT), ("╱", "#3a3a3a"), ("   ", ""),
        ("█", INK), (" completa ", MUT), ("▒", MUT), (" media ", MUT),
        ("░", WARN), (" baja ", MUT), ("╱", "#3a3a3a"), (" sin datos", MUT),
    ))
    console.print()

    tree = Table.grid(expand=False)
    tree.add_column(width=10)
    tree.add_column()

    def node(prefix: str, name: str, meta: str = "", style: str = INK,
             meta_style: str = MUT) -> None:
        tree.add_row(Text(prefix, style=STEP),
                     Text.assemble((name, style), (f"  {meta}", meta_style)))

    tree.add_row(Text("▐", style=ACCENT),
                 Text.assemble(("sistema-legacy", INK),
                               ("  46 nodos · 74 % docs", MUT)))
    tree.add_row(Text.assemble(("▐ ", ACCENT), ("▾ ", ACCENT)),
                 Text.assemble(("core", INK), ("  3 nodos · 1 sin acta", MUT)))
    node("  ├─▐", "auth", "◫ D-2024-001")
    tree.add_row(Text("  ├─▐", style=STEP),
                 Text.assemble(("db", ON_ACCENT), ("  ◫ D-2024-002", MUT)))
    node("  └─▐", "api", "◫ SIN ACTA", meta_style=WARN)
    # a collapsed branch still ANSWERS (gbl BandHeader): counts, not a name
    tree.add_row(Text.assemble(("▐ ", ACCENT), ("▸ ", ACCENT)),
                 Text.assemble(("frontend", INK),
                               ("  5 nodos · 2 sin acta", WARN)))

    ficha = Text.assemble(
        (" db", INK), ("  ", ""), (" nodo ", f"{INK} on {STEP}"), ("\n\n"),
        ("creado", STEP), ("  2024-03-11", MUT), ("\n"),
        ("acta", STEP), ("    D-2024-002 · enlazada", MUT), ("\n"),
        ("tags", STEP), ("    ", ""),
        (" oracle ", f"{INK} on {STEP}"), (" "), (" sin-owner ", f"{INK} on {STEP}"),
        ("\n\n"),
        ("notas — el esquema vive en producción; no hay\nstaging desde 2019. hablar con ops antes de\ntocar secuencias.", MUT),
    )

    body = Table.grid(expand=False)
    body.add_column(width=58)
    body.add_column()
    body.add_row(tree, darkside.group_box(ficha, pad_x=2))
    console.print(body)

    console.print(Text.assemble((" ", ""), pagination(1, 2)))
    console.print()
    toast = Text.assemble(
        (" guardado", f"bold {INK}"), ("   db · notas actualizadas", MUT),
        style=f"on {PANEL}",
    )
    console.print(toast)
    footer(console,
           groups_for_keybar(["nav", "node", "view", "app"]),
           "l pliega/despliega la rama — ctrl+s guarda la ficha",
           "l")
    save(console, "uc2-map.svg", "darkside — map, collapsed branches still answer")


# ---------------------------------------------------------------------------
# R2 — repo, posture OPERATED: one shared time axis for branches + releases,
# honesty badge on the source
# ---------------------------------------------------------------------------
def _time_row(name: str, age_days: int, glyph: str, style: str,
              note: str) -> Text:
    """One event on the shared 30-day axis; today rule ╎ in the same column
    on every row — what aligns vertically happened at the same time (gbl)."""
    w = 48
    cells = [" "] * (w + 1)
    cells[w] = "╎"
    col = max(0, w - 1 - round(age_days / 30 * (w - 2)))
    cells[col] = glyph
    parts: list[tuple[str, str]] = [(f"{name:<14}", MUT)]
    for c in cells:
        if c == "╎":
            parts.append((c, "#3a3a3a"))  # the today rule must survive GROUND
        elif c == glyph:
            parts.append((c, style))
        else:
            parts.append((c, ""))
    parts.append(("  ", ""))
    parts.append((note, MUT))
    return Text.assemble(*parts)


def uc2_repo() -> None:
    console = make_console()
    console.print(darkside.tab_strip("p", ["repo", "legacy-core"]))
    console.print()

    # honesty badge on the source (gbl [REAL]/[VIZ]): where this data lives
    console.print(Text.assemble(
        ("  github.com/acme/legacy-core", INK), ("  ", ""),
        (" github ", f"{INK} on {STEP}"), ("   ", ""),
        ("3 ramas · 2 releases", MUT),
    ))
    console.print()

    console.print(Text("  ramas", style=MUT))
    console.print(_time_row("main", 0, "●", INK, "hace 2 h"))
    console.print(_time_row("develop", 6, "●", INK, "hace 6 d · +4/-12"))
    console.print(_time_row("feature/auth", 21, "●", MUT, "hace 3 sem · sin pr"))
    console.print()
    console.print(Text("  releases", style=MUT))
    console.print(_time_row("v2.1.0", 13, "◆", INK, "hace 13 d"))
    console.print(_time_row("v2.0.0", 28, "◆", MUT, "hace 4 sem"))
    console.print()
    console.print(Text.assemble(
        ("  ●", INK), (" commit   ", MUT), ("◆", INK), (" release   ", MUT),
        ("╎", "#3a3a3a"), (" hoy   (30 días)", MUT),
    ))
    footer(console,
           groups_for_keybar(["doors", "app"]),
           "↵ abre la rama como mapa — u desconecta el repo",
           "↵")
    save(console, "uc2-repo.svg", "darkside — repo, shared time axis")


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------
def build_index() -> None:
    svgs = [
        ("uc-settings.svg", "C1 · settings canary — every component × every state"),
        ("uc-home.svg", "C2 · home — KPI tiles, activity sparkline, resume, recents"),
        ("uc-map.svg", "C3 · map — accordion with declared counts, pagination, toast"),
        ("uc-repo.svg", "C4 · repo plug — skeleton + braille spinner on fetch"),
        ("uc2-home.svg", "H2 · home, GLANCE — one hero (loudest signal), microbar strip, dim sparkline"),
        ("uc2-map.svg", "M2 · map, OPERATED+READ — coverage minimap, collapsed branches still answer"),
        ("uc2-repo.svg", "R2 · repo, OPERATED — shared time axis, honesty badge on the source"),
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
<title>mapper — darkside component sheet</title>
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
<h1>mapper — darkside component sheet</h1>
<p class="note">The interaction layer of the darkside language, rendered from
the real <code>mapper/darkside.py</code> tokens: switch (word flip), stepper,
slider, segmented, progress step-meter, braille spinner, text field, pagination,
tag chips — each in default / focused / disabled. The focused state is always
the solid blue block; the disabled state sinks to STEP. Generated with
<code>python prototypes/ui_components/generate.py</code>.</p>
{"".join(rows)}
</div>
</body>
</html>"""
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("wrote index.html")


if __name__ == "__main__":
    uc_settings()
    uc_home()
    uc_map()
    uc_repo()
    uc2_home()
    uc2_map()
    uc2_repo()
    build_index()
    print("done")
