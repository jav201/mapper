"""Inc-M1 RED-proof driver — executes each named mutation, confirms the named
node FAILS, restores mapper/model.py byte-identically (sha256 compared), and
writes the transcript.  Self-deleting artifacts: the .bak is removed at the end;
this driver is deleted by the caller."""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

M = Path("mapper/model.py")
EVIDENCE = Path(".dev-flow/2026-10-10-perf-batch/evidence")
LOG = EVIDENCE / "m1-red.transcript"
BAK = EVIDENCE / "m1-red.model.py.bak"
F = "tests/test_perf_adjacency.py"

lines: list[str] = []


def emit(s: str = "") -> None:
    print(s)
    lines.append(s)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_node(node: str) -> tuple[int, str]:
    cmd = [sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", node]
    r = subprocess.run(cmd, capture_output=True, text=True)
    # stdout tail only: the assertion and the FAILED summary line live there;
    # stderr is the pytest-asyncio deprecation noise (and carries the
    # interpreter's absolute path, which must never reach the transcript).
    out = r.stdout.strip().splitlines()
    tail = "\n".join(out[-4:])
    return r.returncode, f"$ {' '.join(cmd)}\n{tail}"


def cycle(title: str, node: str, transform) -> bool:
    before = sha(M)
    text = M.read_text(encoding="utf-8")
    new = transform(text)
    assert new != text, f"mutation did not apply: {title}"
    M.write_text(new, encoding="utf-8")
    code, out = run_node(node)
    verdict = "RED" if code != 0 else "STAYED-GREEN"
    M.write_bytes(BAK.read_bytes())
    after = sha(M)
    emit(f"### {title}")
    emit(out)
    emit(f"exit={code} -> {verdict}")
    emit(f"sha256 before={before}")
    emit(f"sha256 after ={after}")
    emit(f"byte-identical restore: {before == after}")
    emit()
    return code != 0 and before == after


def sub(old: str, new: str):
    def t(text: str) -> str:
        assert text.count(old) == 1, f"want 1 occurrence of {old!r}, got {text.count(old)}"
        return text.replace(old, new)
    return t


def plant(snippet: str):
    def t(text: str) -> str:
        return text + "\n\n" + snippet + "\n"
    return t


CENSUS_SNIPPETS = {
    "setitem": "def _m(g):\n    g.edges[0] = None",
    "slice": "def _m(g):\n    g.edges[0:1] = []",
    "del": "def _m(g):\n    del g.edges[0]",
    "iadd": "def _m(g):\n    g.edges += []",
    "imul": "def _m(g):\n    g.edges *= 1",
    "sort": "def _m(g):\n    g.edges.sort()",
    "reverse": "def _m(g):\n    g.edges.reverse()",
    "clear": "def _m(g):\n    g.edges.clear()",
    "extend": "def _m(g):\n    g.edges.extend([])",
    "insert": "def _m(g):\n    g.edges.insert(0, None)",
    "remove": "def _m(g):\n    g.edges.remove(None)",
    "pop": "def _m(g):\n    g.edges.pop()",
    "alias": "def _m(g):\n    x = g.edges\n    x.append(None)",
}

emit("Inc-M1 RED proofs — batch 2026-10-10-perf-batch, Lane M")
emit("worktree-relative paths only; product: mapper/model.py; tests: tests/test_perf_adjacency.py")
emit()

shutil.copyfile(M, BAK)
baseline = sha(M)
emit(f"baseline sha256(model.py) = {baseline}")
emit()

ok = True
ok &= cycle(
    "M-M1a bypass the cache (hit check -> `if False:`, rebuild every lookup)",
    f"{F}::test_cache_counted_ops",
    sub("if self._adj_src is self.edges and len(self.edges) == self._adj_len:",
        "if False:"),
)
ok &= cycle(
    "M-M1b drop the `is` check (len-only key, `_adj_src is not None`)",
    f"{F}::test_cache_mutation_script_equality",
    sub("self._adj_src is self.edges", "self._adj_src is not None"),
)
ok &= cycle(
    "fresh-list mutant (children_of returns the cached list itself)",
    f"{F}::test_cache_mutation_script_equality",
    sub("return list(children.get(node_id, ()))",
        "return children.get(node_id, [])"),
)
for form, snippet in sorted(CENSUS_SNIPPETS.items()):
    ok &= cycle(
        f"census in-place form planted in mapper/model.py: {form} (M-M1c)",
        f"{F}::test_edges_writer_census",
        plant(snippet),
    )

code, out = run_node(F)
emit("### post-restore GREEN (whole new file)")
emit(out)
emit(f"exit={code}")
ok &= code == 0 and sha(M) == baseline

BAK.unlink()
LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nALL RED PROVES OK: {ok}  (transcript: {LOG})")
sys.exit(0 if ok else 1)
