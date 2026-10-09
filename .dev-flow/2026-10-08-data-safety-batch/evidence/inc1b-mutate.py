"""Inc-1b RED + mutation driver (project stack, run from the worktree root).

Usage: python -B <this> red             base-tree counterfactual (no stash, no checkout)
       python -B <this> census          design 5.3 census: final source, tests at BASE
       python -B <this> all             every mutant below, one at a time
       python -B <this> ID[,ID...]      the named mutants

Every run records the sha256 of each touched file, applies the edit, runs the node
files with `pytest -v`, prints one line per FAILED/ERROR node plus the summary,
restores the saved bytes in a `finally`, and compares sha256.  The verdict is read
per resolved node id, never from the exit code.  BASE is pinned to the commit the
increment branched from (Inc-1a review F2: never `HEAD`, which moves).
"""
import hashlib, os, re, subprocess, sys

BASE = "554314f"
INSP, APP, KEY, GUARD = (
    "mapper/widgets/inspector.py", "mapper/app.py", "mapper/keymap.py", "mapper/screens/draft_guard.py",
)
DS, IN, CS = "tests/test_draft_save.py", "tests/test_inspector.py", "tests/test_data_safety_census.py"
G6, WL = "tests/test_g6_store_surrogates.py", "tests/test_worklist_safety.py"
KM, KD, I4, DC = "tests/test_keymap.py", "tests/test_key_dispatch.py", "tests/test_inc4_census.py", "tests/test_darkside_census.py"
BEHAVIOUR = [DS, IN, G6, WL]
SEAT = [CS, KM, KD, I4, DS]
EDITED = [DS, IN, CS, G6, WL, KM, KD, I4, DC]

M = {}


def add(i, f, edits, note, nodes=BEHAVIOUR):
    M[i] = (f, edits, note, nodes)


# -- inspector.py --------------------------------------------------------------
add("I-blur-save", INSP, [(
    "    def on_input_submitted(self, event: Input.Submitted) -> None:",
    "    def on_input_blurred(self, event) -> None:\n        self.screen._save_draft()\n\n"
    "    def on_input_submitted(self, event: Input.Submitted) -> None:")],
    "AT-001: a blur->save path re-added")
add("I-changed-to-blur", INSP, [(
    "    def on_input_changed(self, event: Input.Changed) -> None:",
    "    def on_input_blurred(self, event: Input.Blurred) -> None:")],
    "AT-010 / TC-001.2a: the draft updates on blur only (no per-keystroke update)")
add("I-stale-keyed-to-node", INSP, [(
    'self._put_draft(getattr(event.input, "node_id", None), field, event.value)',
    'self._put_draft(self.node.id if self.node else None, field, event.value)')],
    "TC-001.2b: the entry is keyed to the re-pointed node, not the input's")
add("I-values-not-copy", INSP, [("        return dict(self._draft)", "        return self._draft")],
    "TC-001.1: draft_values returns the live dict")
add("I-clear-noop", INSP, [(
    "        self._draft = {}\n        self._draft_node_id = None\n        self._paint_dirty()",
    "        pass")], "TC-001.1: clear_draft does nothing")
add("I-count-binary", INSP, [("        return len(self._shown_draft())", "        return min(1, len(self._shown_draft()))")],
    "AT-003: N = 1 if draft else 0")
add("I-no-paint-on-change", INSP, [(
    "        self._draft_node_id = node_id if self._draft else None\n        self._paint_dirty()",
    "        self._draft_node_id = node_id if self._draft else None")],
    "AT-003: markers not repainted on a keystroke")
add("I-remount-per-key", INSP, [(
    "        self._draft_node_id = node_id if self._draft else None\n        self._paint_dirty()",
    "        self._draft_node_id = node_id if self._draft else None\n        self.call_next(self._rebuild)")],
    "TC-002.2: each keystroke remounts the form")
add("I-raw-title", INSP, [("            return darkside.plain(ficha.title)", "            return ficha.title")],
    "TC-002.1: dirty against the raw stored title")
add("I-raw-state", INSP, [(
    "            return ficha.state if ficha.state in STATE_VALUES else STATE_VALUES[0]",
    "            return ficha.state")], "TC-002.1: dirty against the raw stored state")
add("I-prune-inverted", INSP, [("        if value == self._shown_value(field):", "        if value != self._shown_value(field):")],
    "TC-L0-1: the equal-to-shown prune inverted")
add("I-no-rediff", INSP, [(
    "            self._draft = {f: v for f, v in self._draft.items() if v != self._shown_value(f)}",
    "            pass")], "AT-009 / AT-002a both: show() does not re-diff the draft")
add("I-no-notes-key", INSP, [('        if widget_id == "insp-notes":\n            return "notes"\n', "")],
    "TC-006.2: the notes arm of _field_of dropped")
add("I-enter-saves", INSP, [(
    "        event.input.call_later(event.input.action_leave_field)",
    "        self.screen._save_draft()")], "AT-006: enter saves (and stays in the field)")
add("I-enter-stays", INSP, [("        event.input.call_later(event.input.action_leave_field)", "        pass")],
    "TC-005.1: enter does not leave the field")
add("I-enter-direct", INSP, [(
    "        event.input.call_later(event.input.action_leave_field)",
    "        event.input.action_leave_field()")],
    "TC-005.1: the design's literal call (sender = inspector, Left stopped at it)")
add("I-segment-saves", INSP, [(
    '        self._put_draft(self.node.id, "state", STATE_VALUES[event.index])',
    '        self._put_draft(self.node.id, "state", STATE_VALUES[event.index])\n        self.screen._save_draft()')],
    "AT-007 / TC-006.1: the segment saves at once")
# -- app.py --------------------------------------------------------------------
add("A-snapshot-after", APP, [
    ("        self._push_snapshot(self.base_graph)\n        candidate", "        candidate"),
    ("                self._apply_field(node.ficha, field, value)\n            inspector.clear_draft()",
     "                self._apply_field(node.ficha, field, value)\n            self._push_snapshot(self.base_graph)\n"
     "            inspector.clear_draft()")], "AT-002: snapshot pushed AFTER applying to base_graph")
add("A-save-twice", APP, [(
    "        if _save_or_toast(self, self.store, self.map_id, candidate):",
    "        if _save_or_toast(self, self.store, self.map_id, candidate) and "
    "_save_or_toast(self, self.store, self.map_id, candidate):")], "AT-002: _save_or_toast called twice")
add("A-save-per-field", APP, [(
    "        if _save_or_toast(self, self.store, self.map_id, candidate):",
    "        if all([_save_or_toast(self, self.store, self.map_id, candidate) for _ in draft]):")],
    "TC-001.4: one save per field")
add("A-snapshot-per-field", APP, [(
    "        self._push_snapshot(self.base_graph)\n        candidate",
    "        for _ in draft:\n            self._push_snapshot(self.base_graph)\n        candidate")],
    "TC-004.1: one snapshot per field")
add("A-clear-on-failure", APP, [(
    "        self._snapshots[:] = saved_stack",
    "        self._snapshots[:] = saved_stack\n        inspector.clear_draft()")], "AT-002a zero: clear the draft on any failure")
add("A-no-reload", APP, [("            graph = self.store.load(self.map_id)", "            graph = self.base_graph")],
    "AT-002a both: skip the reload, keep base_graph")
add("A-pop-not-restore", APP, [("        self._snapshots[:] = saved_stack", "        self._snapshots.pop()")],
    "TC-004.2a: pop instead of the slice restore")
add("A-mutate-then-save", APP, [("        candidate = copy.deepcopy(self.base_graph)", "        candidate = self.base_graph")],
    "TC-004.2b: apply onto base_graph before the save")
add("A-save-subgraph", APP, [("        candidate = copy.deepcopy(self.base_graph)", "        candidate = copy.deepcopy(self.graph)")],
    "TC-004.4 / R-1: the focused subgraph is written as the map")
add("A-assign-graph-only", APP, [(
    "        self._establish_graph(graph, cursor=cursor)\n        self.refresh_canvas()\n        if self.nav.cursor == node_id:",
    "        self.graph = self.base_graph = graph\n        self.refresh_canvas()\n        if self.nav.cursor == node_id:")],
    "TC-004.2d: reload assigns the graph without the load path")
add("A-no-orphan-drop", APP, [(
    "        self._drop_orphan_draft()\n        inspector = self.query_one(\"#map-inspector\", FichaInspector)\n"
    "        if inspector.has_draft() and self.nav.cursor",
    "        inspector = self.query_one(\"#map-inspector\", FichaInspector)\n"
    "        if inspector.has_draft() and self.nav.cursor")], "TC-004.2c: refresh_canvas skips the orphan drop")
add("A-stay-repoints", APP, [(
    "            self._guard_draft(lambda: self._repoint(target))",
    "            self._guard_draft(lambda: self._repoint(target), on_hold=lambda: self._repoint(target))")],
    "AT-004: stay re-points anyway")
add("A-show-before-guard", APP, [(
    "    def refresh_canvas(self) -> None:\n        # US-001, LLR-003.2",
    "    def refresh_canvas(self) -> None:\n        self.query_one(\"#map-inspector\", FichaInspector).show("
    "self.graph.nodes.get(self.nav.cursor or \"\"), self.graph)\n        # US-001, LLR-003.2")],
    "TC-003.2: the inspector is re-pointed before the guard")
add("A-second-guard", APP, [("        if self._draft_guard_open:\n            return\n", "")],
    "LLR-004.2: no re-entrancy check (a second guard stacks)")
add("A-guard-same-node", APP, [(
    "        if inspector.has_draft() and self.nav.cursor != inspector.draft_node_id:",
    "        if inspector.has_draft():")], "LLR-003.2 boundary: a same-node repaint asks")
add("A-undo-clears", APP, [(
    "    def action_undo(self) -> None:\n        self._pop_snapshot()",
    "    def action_undo(self) -> None:\n        self.query_one(\"#map-inspector\", FichaInspector).clear_draft()\n"
    "        self._pop_snapshot()")], "TC-004.3: undo clears the draft")
add("A-no-plain-apply", APP, [("        value = darkside.plain(value)\n        if field == \"title\":", "        if field == \"title\":")],
    "TC-L0-2 / g6b: _apply_field drops plain")
add("A-swap-title-notes", APP, [(
    "        if field == \"title\":\n            ficha.title = value\n        elif field == \"notes\":\n            ficha.notes = value",
    "        if field == \"title\":\n            ficha.notes = value\n        elif field == \"notes\":\n            ficha.title = value")],
    "TC-L0-2: title and notes branches swapped")
add("A-hint-literal", APP, [(
    "                f\"fill in «{missing[0].label}» · {save} {self._seat_label('save_draft')}\"",
    "                f\"fill in «{missing[0].label}» · ↵ save\"")], "AT-006 / TC-005.2: the `↵ save` literal back")
add("A-hint-fixed-words", APP, [(
    "                f\"fill in «{missing[0].label}» · {save} {self._seat_label('save_draft')}\"",
    "                f\"fill in «{missing[0].label}» · ctrl+s save\"")], "TC-005.2: today's words as a literal (provenance)")
add("A-no-refocus", APP, [(
    "            self.refresh_canvas()\n            self._refocus_field(inspector, refocus)\n            self._event_toast",
    "            self.refresh_canvas()\n            self._event_toast")], "C7: focus not returned to the field")
add("A-reload-toast", APP, [(
    "            message = f\"could not reload · draft kept · leaving needs {discard.glyph} ({discard.label})\"",
    "            message = \"could not reload -- leave and reopen the map\"")], "C8: the design's earlier wording")
add("A-retry-toast-missing", APP, [(
    "        self.notify(darkside.plain(message), severity=\"error\", markup=False)\n        return False",
    "        return False")], "LLR-004.2: no 'draft kept' toast after a failure")
add("A-prefix-mut", APP, [(
    "visual = darkside.Text.assemble((self.draft_prefix, darkside.ALERT), visual)",
    "visual = darkside.Text.assemble((self.draft_prefix, darkside.MUT), visual)")], "C6: prefix not in ALERT")
add("A-prefix-lost-on-set-hint", APP, [(
    "        super().set_hint(text, key)\n        self._paint_prefix()",
    "        super().set_hint(text, key)")], "C6: a later set_hint drops the prefix")
add("A-prefix-never", APP, [(
    "        if self.inspector_hidden and inspector.has_draft():",
    "        if False:")], "C6: no prefix at all")
add("A-prefix-always", APP, [(
    "        if self.inspector_hidden and inspector.has_draft():",
    "        if inspector.has_draft():")], "C6: prefix even with the card visible")
# -- keymap.py / draft_guard.py ------------------------------------------------
add("K-ctrl-s-priority", KEY, [(
    'KeyBinding("ctrl+s", "ctrl+s", "save_draft", "save", "node")',
    'KeyBinding("ctrl+s", "ctrl+s", "save_draft", "save", "node", priority=True)')],
    "seat: ctrl+s made priority", nodes=SEAT)
add("K-ctrl-s-gone", KEY, [(
    '    KeyBinding("ctrl+s", "ctrl+s", "save_draft", "save", "node"),\n', "")],
    "seat: the ctrl+s row removed", nodes=SEAT)
add("G-plain-title", GUARD, [("darkside.plain(self.node_title)", "self.node_title")],
    "AT-015: plain dropped at the guard's title sink", nodes=[DS])
add("G-empty-placeholder", GUARD, [(
    'text = f"unsaved draft on «{darkside.plain(self.node_title)}»"',
    'text = f"unsaved draft on «{darkside.plain(self.node_title) or \'(untitled)\'}»"')],
    "Inc-1a F1: a placeholder for an empty title", nodes=[DS])


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pytest(nodes):
    r = subprocess.run([sys.executable, "-B", "-W", "error::SyntaxWarning", "-m", "pytest", "-v", "-rfE",
                        "--continue-on-collection-errors", "-p", "no:cacheprovider", *nodes],
                       capture_output=True, text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                       encoding="utf-8", errors="replace")
    lines = r.stdout.splitlines()
    for l in lines:
        if re.match(r"(FAILED|ERROR) ", l):
            print(l[:200])
    print("summary:", lines[-1] if lines else "(no output)")


def run(i):
    f, edits, note, nodes = M[i]
    before = sha(f)
    orig = open(f, "rb").read()
    nl = b"\r\n" if b"\r\n" in orig else b"\n"
    mutated = orig
    print(f"=== {i}: {note}\nfile {f}\nsha256 before {before}")
    for old, new in edits:
        o = old.replace("\n", nl.decode()).encode("utf-8")
        n = new.replace("\n", nl.decode()).encode("utf-8")
        if mutated.count(o) != 1:
            print(f"BAD: anchor applies {mutated.count(o)} times: {old[:60]!r}\n")
            return
        mutated = mutated.replace(o, n)
    try:
        open(f, "wb").write(mutated)
        print(f"sha256 mutated {sha(f)}  (changed: {sha(f) != before})")
        pytest(nodes)
    finally:
        open(f, "wb").write(orig)
        after = sha(f)
        print(f"sha256 after restore {after}  restored: {after == before}\n")


def swap_to_base(files, nodes, label):
    saved = {f: open(f, "rb").read() for f in files}
    before = {f: sha(f) for f in files}
    for f in files:
        print(f"sha256 before {f} {before[f]}")
    try:
        for f in files:
            open(f, "wb").write(subprocess.run(["git", "show", f"{BASE}:{f}"], capture_output=True, check=True).stdout)
        print(f"applied: {label} = {BASE} blobs")
        pytest(nodes)
    finally:
        for f in files:
            open(f, "wb").write(saved[f])
        for f in files:
            print(f"sha256 after  {f} {sha(f)}  restored: {sha(f) == before[f]}")


if sys.argv[1] == "red":
    # the three source files at base; every new and edited test as committed
    swap_to_base([INSP, APP, KEY], EDITED, "inspector.py, app.py, keymap.py")
elif sys.argv[1] == "census":
    # final source; the existing tests this increment edits at base (design 5.3)
    swap_to_base([IN, G6, WL, KM, KD, I4, DC, CS], [IN, G6, WL, KM, KD, I4, DC, CS, "tests/test_inc9.py",
                 "tests/test_a3_census.py"], "the edited existing tests")
else:
    for i in (list(M) if sys.argv[1] == "all" else sys.argv[1].split(",")):
        run(i)
