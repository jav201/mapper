"""Inc-1a RED + mutation driver (project stack, run from the worktree root).

Usage: python <this> red            base-tree counterfactual (no stash, no checkout)
       python <this> ID[,ID...]     one mutant at a time

Every run: record sha256 of each touched file, apply, run the node files with
`pytest -v`, print one verdict line per FAILED/ERROR node plus the summary,
restore from the saved bytes in a `finally`, compare sha256.  The verdict is
read per resolved node id, never from the process exit code.
"""
import hashlib, os, re, subprocess, sys

DS, CS = "tests/test_draft_save.py", "tests/test_data_safety_census.py"
KM, KD = "tests/test_keymap.py", "tests/test_key_dispatch.py"
NODES = [DS, CS, KM, KD]
KEY, INIT, GUARD = "mapper/keymap.py", "mapper/screens/__init__.py", "mapper/screens/draft_guard.py"

M = {}
def add(i, f, old, new, note):
    M[i] = (f, old, new, note)

add("K-d-swap", KEY, 'KeyBinding("d", "d", "discard", "discard", "draft")',
    'KeyBinding("d", "d", "stay", "discard", "draft")', "seat: the d row's action swapped to stay")
add("K-modal-off", KEY, "MODAL_SCOPES = (SCOPE_PALETTE, SCOPE_HELP, SCOPE_DRAFT)",
    "MODAL_SCOPES = (SCOPE_PALETTE, SCOPE_HELP)", "seat: draft dropped from MODAL_SCOPES")
add("K-priority", KEY, 'KeyBinding("escape", "esc", "stay", "stay", "draft")',
    'KeyBinding("escape", "esc", "stay", "stay", "draft", priority=True)', "seat: the esc row made priority")
add("K-order", KEY, '    "help": SCOPE_HELP,\n    "draft": SCOPE_DRAFT,\n    "app": SCOPE_APP,\n}',
    '    "help": SCOPE_HELP,\n    "app": SCOPE_APP,\n    "draft": SCOPE_DRAFT,\n}', "seat: draft group declared after app")
add("K-header", KEY, '"draft": "unsaved"', '"draft": "draft"', "seat: GROUP_HEADER draft renamed")
add("K-glyph", KEY, 'KeyBinding("escape", "esc", "stay", "stay", "draft")',
    'KeyBinding("escape", "escape", "stay", "stay", "draft")', "seat: esc glyph spelled out")
add("G-markup", GUARD, 'id="draft-guard-title", markup=False)', 'id="draft-guard-title")',
    "sink: markup=False dropped from the title Static")
add("G-plain-title", GUARD, "darkside.plain(self.node_title)", "self.node_title",
    "sink: plain dropped from the node title")
add("G-plain-map", GUARD, "darkside.plain(self.map_id)", "self.map_id",
    "sink: plain dropped from the map id")
add("G-plain-both", GUARD, "f\"unsaved draft on «{darkside.plain(self.node_title)}»\"", "f\"unsaved draft on «{self.node_title}»\"",
    "sink: plain dropped from the title (single-site form of G-plain-title)")
add("G-no-map", GUARD, "    if self.map_id:", "    if False:", "title: map id never shown")
add("G-save-token", GUARD, 'self.dismiss("save")', 'self.dismiss("discard")', "action_save returns discard")
add("G-stay-token", GUARD, 'self.dismiss("stay")', 'self.dismiss("save")', "action_stay returns save")
add("G-hint-key", GUARD, "pieces.append((row.glyph, darkside.INK))", "pieces.append((row.key, darkside.INK))",
    "hint: key name instead of the seat glyph")
add("G-hint-literal", GUARD, "return Text.assemble(*pieces)",
    'return Text("s save   d discard   esc stay")', "hint: a literal with today's wording (provenance mutant)")
add("G-bindings-literal", GUARD, "for key, action, label, priority in textual_bindings(SCOPE_DRAFT)",
    "for key, action, label, priority in textual_bindings(SCOPE_DRAFT, include_app=True)",
    "BINDINGS: the app chords inherited into the guard")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pytest(nodes):
    r = subprocess.run([sys.executable, "-B", "-W", "error::SyntaxWarning", "-m", "pytest", "-v", "-rfE", "--continue-on-collection-errors", "-p",
                        "no:cacheprovider", *nodes], capture_output=True, text=True,
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"}, encoding="utf-8", errors="replace")
    lines = r.stdout.splitlines()
    for l in lines:
        if re.match(r"(FAILED|ERROR) ", l):
            print(l[:200])
    print("summary:", lines[-1] if lines else "(no output)")


def run(i):
    f, old, new, note = M[i]
    before = sha(f)
    orig = open(f, "rb").read()
    nl = b"\r\n" if b"\r\n" in orig else b"\n"
    o, n = old.replace("\n", nl.decode()).encode("utf-8"), new.replace("\n", nl.decode()).encode("utf-8")
    print(f"=== {i}: {note}\nfile {f}\nsha256 before {before}")
    if orig.count(o) != 1:
        print(f"BAD: anchor applies {orig.count(o)} times")
        return
    try:
        open(f, "wb").write(orig.replace(o, n))
        print(f"sha256 mutated {sha(f)}  (changed: {sha(f) != before})")
        pytest(NODES)
    finally:
        open(f, "wb").write(orig)
        after = sha(f)
        print(f"sha256 after restore {after}  restored: {after == before}\n")


def red():
    """Base-tree counterfactual: keymap.py and screens/__init__.py back to HEAD,
    draft_guard.py moved aside; the new and updated tests stay as committed."""
    files = [KEY, INIT, GUARD]
    saved = {f: open(f, "rb").read() for f in files}
    before = {f: sha(f) for f in files}
    for f in files:
        print(f"sha256 before {f} {before[f]}")
    aside = GUARD + ".aside"
    try:
        for f in (KEY, INIT):
            base = subprocess.run(["git", "show", f"HEAD:{f}"], capture_output=True, check=True).stdout
            open(f, "wb").write(base)
        os.rename(GUARD, aside)
        print("applied: keymap.py and screens/__init__.py = HEAD blobs; draft_guard.py moved aside")
        pytest(NODES)
    finally:
        if os.path.exists(aside):
            os.rename(aside, GUARD)
        for f in (KEY, INIT):
            open(f, "wb").write(saved[f])
        for f in files:
            print(f"sha256 after  {f} {sha(f)}  restored: {sha(f) == before[f]}")


if sys.argv[1] == "red":
    red()
else:
    for i in sys.argv[1].split(","):
        run(i)
