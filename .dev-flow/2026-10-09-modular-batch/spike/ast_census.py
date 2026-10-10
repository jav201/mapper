"""Throwaway AST census for MapScreen in mapper/app.py (MOD-CENSUS unit).

Outputs machine-readable JSON the census doc is built from:
- methods: per-method metadata (lines, attrs read/written, internal calls, module names used)
- state: every self.<attr> assigned in MapScreen with first-assignment site
- toplevel: classes/functions of app.py outside MapScreen with their dependencies
"""
import ast
import builtins
import json
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent / "mapper" / "app.py"
SRC = APP.read_text(encoding="utf-8")
TREE = ast.parse(SRC)


def lineno(node):
    return getattr(node, "lineno", None)


def endlineno(node):
    return getattr(node, "end_lineno", lineno(node))


def qual_name(node):
    """Dotted name for Attribute/Name, None otherwise."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


class MethodCensus(ast.NodeVisitor):
    """Collect, for one function body: self-attr reads/writes, self-method calls,
    module-level names used."""

    def __init__(self):
        self.reads = set()
        self.writes = set()
        self.calls = set()          # other MapScreen methods called via self.<m>(
        self.module_names = set()   # bare names that are not self/local/params
        self._local_scopes = []

    def visit_FunctionDef(self, node):
        if self._local_scopes:
            self._local_scopes[-1].add(node.name)
        self._local_scopes.append(set())
        for a in node.args.args + node.args.kwonlyargs:
            self._local_scopes[-1].add(a.arg)
        if node.args.vararg:
            self._local_scopes[-1].add(node.args.vararg.arg)
        if node.args.kwarg:
            self._local_scopes[-1].add(node.args.kwarg.arg)
        self.generic_visit(node)
        self._local_scopes.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        self._local_scopes.append(set())
        for a in node.args.args:
            self._local_scopes[-1].add(a.arg)
        self.generic_visit(node)
        self._local_scopes.pop()

    def visit_ExceptHandler(self, node):
        self._local_scopes.append(set())
        if node.name:
            self._local_scopes[-1].add(node.name)
        for stmt in node.body:
            self.visit(stmt)
        self._local_scopes.pop()

    def _is_local(self, name):
        return any(name in s for s in self._local_scopes)

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store,)):
            # assignment target at module-use level: track as local
            for scope in reversed(self._local_scopes):
                scope.add(node.id)
                break
        elif isinstance(node.ctx, ast.Load):
            if not self._is_local(node.id) and node.id != "self":
                self.module_names.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        qn = qual_name(node)
        if qn and qn.startswith("self."):
            attr = qn.split(".", 1)[1]
            # writes: only direct self.x = / self.x += etc, not self.x.y =
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                if "." not in attr:
                    self.writes.add(attr)
                else:
                    # self.x.y = z writes self.x's contents; count x as read
                    self.reads.add(attr.split(".")[0])
            elif isinstance(node.ctx, ast.Load):
                self.reads.add(attr.split(".")[0])
        self.generic_visit(node)

    def visit_Call(self, node):
        # self.method(...) call
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) \
                and node.func.value.id == "self":
            self.calls.add(node.func.attr)
        self.generic_visit(node)


def method_span(node):
    """Line span of a method including decorators."""
    start = lineno(node)
    for d in node.decorator_list:
        start = min(start, lineno(d))
    return start, endlineno(node)


# ---- locate MapScreen and top-level defs ---------------------------------
mapscreen = None
toplevel = []
for node in TREE.body:
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        toplevel.append(node)
        if node.name == "MapScreen":
            mapscreen = node

methods = []
state_first = {}
for item in mapscreen.body:
    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
        start, end = method_span(item)
        c = MethodCensus()
        c.visit(item)
        doc = ast.get_docstring(item)
        body_first = start + (1 if doc else 0)
        decorator_names = set()
        for d in item.decorator_list:
            qn = qual_name(d) or ""
            if qn:
                decorator_names.add(qn.split(".")[0])
            for sub in ast.walk(d):
                if isinstance(sub, ast.Name):
                    decorator_names.add(sub.id)
        module_names = {
            n for n in c.module_names
            if n not in dir(builtins) and n not in decorator_names
        }
        methods.append({
            "name": item.name,
            "first_line": start,
            "line_count": end - start + 1,
            "decorators": [qual_name(d) or ast.dump(d) for d in item.decorator_list],
            "doc_first_line": (doc or "").splitlines()[0][:110] if doc else "",
            "reads": sorted(c.reads),
            "writes": sorted(c.writes),
            "calls": sorted(c.calls),
            "module_names": sorted(module_names),
            "property": any((qual_name(d) or "") == "property" for d in item.decorator_list),
        })
    elif isinstance(item, ast.Assign):
        for t in item.targets:
            qn = qual_name(t)
            if qn and qn.startswith("self."):
                attr = qn.split(".", 1)[1].split(".")[0]
                if attr not in state_first:
                    state_first[attr] = {"where": "class-assign",
                                          "line": lineno(item)}

# first-assignment per attribute from methods (class-assigns already recorded)
for m in methods:
    for w in m["writes"]:
        if w not in state_first:
            state_first[w] = {"where": m["name"], "line": m["first_line"]}

# ---- top-level classes/functions and their app.py dependencies -----------
app_names = {n.name for n in toplevel}
app_funcs = [n for n in toplevel if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

deps = {}
for node in toplevel:
    used = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Load):
            used.add(sub.id)
        elif isinstance(sub, ast.Attribute):
            qn = qual_name(sub)
            if qn:
                used.add(qn.split(".")[0])
    deps[node.name] = {
        "first_line": lineno(node),
        "line_count": endlineno(node) - lineno(node) + 1,
        "kind": type(node).__name__,
        "app_deps": sorted(d for d in used if d in app_names and d != node.name),
    }

out = {
    "methods": methods,
    "state_first": state_first,
    "toplevel": deps,
}
Path(__file__).resolve().parent.joinpath("census.json").write_text(
    json.dumps(out, indent=1), encoding="utf-8")
print(f"methods={len(methods)} state_attrs={len(state_first)} toplevel={len(toplevel)}")
print(f"wrote {Path(__file__).resolve().parent / 'census.json'}")
