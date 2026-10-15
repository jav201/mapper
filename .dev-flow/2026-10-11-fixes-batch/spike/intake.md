# P0 intake spike — 2026-10-11-fixes-batch

Scope: BACKLOG rows B-115, B-116, B-117, B-127. Every item was reproduced NOW on `master`
(`5188a546086abad0df80daf01c3dfc85e622db85`) from the worktree root, before any product
change. All four are genuine bugs, none bigger than a bug — none is split out. Commands and
outputs are verbatim.

---

## B-115 — `slugify("")` → `"n"`; empty parent cell slugified on import

**Reproduction (command + output, run from the worktree root):**

```
$ python - <<'EOF'
from mapper.mermaid import slugify
print("slugify('') ->", repr(slugify("")))
print("slugify('!!!') ->", repr(slugify("!!!")))
EOF
slugify('') -> 'n'
slugify('!!!') -> 'n'
```

```
$ python - <<'EOF'
import tempfile
from pathlib import Path
from mapper.import_csv import preview_csv
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "empty_parent.csv"
    p.write_text("id,title,parent\nalpha,Alpha,\nbeta,Beta,\n!!!,Bang,\n", encoding="utf-8")
    g = preview_csv(p)
    print("B-115 nodes:", sorted((n.id, n.ficha.title) for n in g.nodes.values()))
    print("B-115 edges:", [(e.parent_id, e.child_id) for e in g.edges])
EOF
B-115 nodes: [('alpha', 'Alpha'), ('beta', 'Beta'), ('n', 'Bang')]
B-115 edges: [('n', 'alpha'), ('n', 'beta'), ('n', 'n')]
```

**Code:** `mapper/mermaid.py:46-51` (`slugify`, `value[:32] or "n"`); call sites
`mapper/import_csv.py:59` (row id) and `mapper/import_csv.py:70` (parent cell — slugifies the
empty string for every parentless row).

**Expected behaviour:** an empty parent cell means "top-level row" — the row is parentless
(root-level, no `? ` park, since nothing is missing); it never references a node `n`. An id
that slugifies to empty must not become `n` colliding with everything else.

**Risk:** silent data-shape corruption on every CSV import with parentless rows (all top-level
rows re-parented under a stray `n` node when one exists — see the `n→n` self-edge above,
which a valid root named `N` produces and save then refuses as a cycle); pre-existing.

**Proposed fix (3–5 lines):** in `preview_csv`, skip the slugify call when the parent cell is
empty (`parent_id = slugify(parent) if parent else ""`), so an empty parent takes the
parentless/depth path; and when a row's id slugifies to empty, fall back to the existing
`row-N` auto-id instead of `"n"`. Leave `slugify`'s own fallback for direct API callers, or
drop it — P1 decides; the import call sites no longer depend on it.

---

## B-116 — CSV listing a child before its root is refused as a cycle

**Reproduction (command + output, run from the worktree root):**

```
$ python - <<'EOF'
import tempfile
from pathlib import Path
from mapper.import_csv import preview_csv
with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "child_first.csv"
    p.write_text("id,title,parent\nchild,Child,root\nroot,Root,\n", encoding="utf-8")
    g = preview_csv(p)
    print("B-116 root_id:", g.root_id)
    print("B-116 edges:", [(e.parent_id, e.child_id) for e in g.edges])
    print("B-116 find_cycle:", g.find_cycle())
EOF
B-116 root_id: child
B-116 edges: [('root', 'child'), ('child', 'root')]
B-116 find_cycle: ['child', 'root', 'child']
```

**Code:** `mapper/model.py:186-189` (`add_node` stamps `root_id` with the FIRST row);
`mapper/import_csv.py:86-104` (second pass builds `root→child` from row 1's parent column);
the orphan-attach pass `mapper/import_csv.py:106-112` then hangs the later-declared `root`
under the first row (`child→root`), closing a 2-cycle that save/load refuses (`MermaidError`).

**Expected behaviour:** row order must not change the outcome: this CSV is the same tree as
its rows reordered (`root` on top), and imports as root `root` with one edge `root→child`.
The csv-safety store then saves it without a cycle refusal.

**Risk:** legitimate spreadsheets (exported unsorted) are unimportable with a scary cycle
error; the user cannot tell the CSV is fine. Pre-existing.

**Proposed fix (3–5 lines):** after the second pass, choose the orphan-attach target as a node
that stays parentless (e.g. the last row with no parent reference and no parent edge, or the
first row that no edge points at), never the first row unconditionally; and skip (park with
`? `) any orphan attachment that would create a cycle, instead of adding the edge blind.
Equivalent alternative: build edges first, then set `graph.root_id` to the unique parentless
node before attaching remaining orphans to it.

---

## B-117 — a forest map's root changes on reload

**Reproduction (command + output, run from the worktree root):**

```
$ python - <<'EOF'
from mapper.mermaid import parse, dump
src = "graph TD\n    a\n    b --> c\n"
g1 = parse(src)
print("B-117 root before save:", g1.root_id)
d = dump(g1)
print(d, end="")
g2 = parse(d)
print("B-117 root after reload:", g2.root_id)
EOF
B-117 root before save: a
graph TD
    b --> c
    a
B-117 root after reload: b
```

**Code:** `mapper/mermaid.py:135-150` (`dump` emits all edges before any parentless node);
`mapper/mermaid.py:125-127` (`parse` picks the first parentless node in text order — after a
save, that is the first edge's parent, not the declared root). The legacy forest fixtures
(`fixtures/legacy.mmd` — a forest) load today with root `a` and drift to `b` after one
save+reload.

**Expected behaviour:** save+reload is root-stable: a forest map reloads with the same root it
had before saving (round-trip identity for the root, as for every other node).

**Risk:** every forest save silently re-roots the map; focus/canvas state keyed to the root
id breaks after reload. The csv-safety batch pinned the CURRENT behaviour (ruling R11: the
round-trip check must not compare the root; LLR-CSV.1.3's forest regression) — those pins
move with this fix, in the same increment, with the RED proof recorded.

**Proposed fix (3–5 lines):** in `dump`, emit the declared root's node line FIRST (before the
edge block), so `parse`'s existing first-parentless-in-text-order rule selects it; forests
whose declared root is an edge parent are unaffected (already first). No `parse` change — one
writer-side rule, matching how the fix was scoped in the backlog row.

---

## B-127 — roles screen runs git reads on the UI thread at mount

**Reproduction (command + output, run from the worktree root; a seeded registry per
`tests/test_roles_screen.py`, git calls delayed 0.5 s each):**

```
$ python - <<'EOF'
import os, subprocess, tempfile, threading, time
from pathlib import Path
from unittest import mock
from mapper.reqharness.config import create_registry
from mapper.screens import roles
from mapper.reqharness import identity

with tempfile.TemporaryDirectory() as d:
    ws = Path(d)
    env = {**os.environ, "GIT_CONFIG_GLOBAL": str(ws / "global.gitconfig")}
    subprocess.run(["git", "init", "-q", str(ws)], env=env, check=True)
    subprocess.run(["git", "-C", str(ws), "config", "user.name", "Probe"], env=env, check=True)
    subprocess.run(["git", "-C", str(ws), "config", "user.email", "probe@example.invalid"], env=env, check=True)
    create_registry(ws, person="subject", name="Subject", email="subject@example.invalid",
                    now="2026-10-11T09:00:00Z")
    calls = []
    real = identity._run_git
    def slow(repo, tail):
        calls.append((threading.current_thread().name, tuple(tail)))
        time.sleep(0.5)
        return real(repo, list(tail))
    t0 = time.perf_counter()
    with mock.patch.object(identity, "_run_git", slow):
        snap = roles._load(ws)
    dt = time.perf_counter() - t0
    print(f"B-127 _load wall time with 0.5s per git call: {dt:.2f}s")
    for thread_name, tail in calls:
        print(f"  git call on thread {thread_name!r}: {tail}")
    print(f"B-127 status={snap.status!r} viewer={snap.viewer_id!r}")
EOF
B-127 _load wall time with 0.5s per git call: 1.88s
  git call on thread 'MainThread': ('rev-parse', '--show-toplevel')
  git call on thread 'MainThread': ('config', '--get', 'user.name')
  git call on thread 'MainThread': ('config', '--get', 'user.email')
B-127 status='chain verified' viewer='Probe'
```

**Code:** `mapper/screens/roles.py:471-483` — `on_mount` → `_reload` → `self._snap =
_load(workspace)` synchronously (no worker); `_load` calls `identity.repo_root`
(`mapper/screens/roles.py:178`) and `identity.read` (`:222`), i.e. three sequential
`subprocess.run` calls, each with a 10 s timeout (`mapper/reqharness/identity.py:56`,
`:191-200`), all on the UI thread. Worst case ≈ 30 s freeze if git hangs; probe shows the
calls are sequential and blocking on the calling thread (1.88 s ≈ 3 × 0.5 s + overhead).

**Expected behaviour:** mounting the roles screen never blocks the UI thread on git; a slow or
hung git degrades to the already-named states (`no repo` / empty identity) and the screen
paints when the load completes.

**Risk:** UI freeze up to ~30 s on mount/resume (`on_screen_resume` re-runs the same load)
whenever git is slow (network fs, hung credential helper, heavy index). Residual risk
recorded at the ReqHarness DDR; the fix is a follow-up by ruling.

**Proposed fix (3–5 lines):** run `_load` in a Textual worker (`self.run_worker(...)`) at mount
and on resume, painting only when the snapshot arrives; keep every degradation named as
today. **UI-design note:** a *visible* loading indicator is a TUI design change — it needs a
prototype verdict before implementation (standing practice: every new visual state goes back
to the operator as a prototype round). **Proposed minimal non-visual alternative:** no new
chrome — the screen keeps its current pre-paint state (blank matrix/status band) and
populates when the worker finishes; optionally cache the three identity reads per repo in
`mapper/reqharness/identity.py` so repeat mounts are instant.

---

## Validator

`python <flow>/tools/devflow-validate.py --brief` run in the worktree after the rollover
(2026-10-11, `PYTHONDONTWRITEBYTECODE=1`): **exit 1 · `3 block · 532 notice · 46 not
applicable`**. All 3 blocks are environment, none names this batch:

- `V7` — `FLOW-VERSION.md`: local flow revision `d2af39dd1ee690c4` ≠ declared `0504b99f7b8deecf` (flow bundle changed outside this project).
- `V16` ×2 — `~/.claude` and `~/.claude/skills` carry uncommitted changes (same cause).

Batch-specific readback is clean: the new batch id appears in no finding (no `V18` ghost —
`.dev-flow/2026-10-11-fixes-batch/` exists and is seeded; no `V29` decisions-log mismatch —
the log was archived to the outgoing batch's record and reset). `V27`/`V40` are notices only
(empty log at open; `owner` OMITTED by the project guard A-110, by design — identical to the
outgoing batch's record). `V9` notices on the seeded `03-increments/increment-001.md`
("packet declares no SOURCE count") are the expected skeleton-seed state; the packet is
filled when the increment runs.

