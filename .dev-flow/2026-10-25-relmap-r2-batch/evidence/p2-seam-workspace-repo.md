# Seam probe (b) — workspace-as-repo canon derivation

Date: 2026-10-25. Worktree branch `feat/relmap-r2`. Probe runner: `python` with
`PYTHONPATH=<worktree>` (package is not installed; imports resolve from the worktree root).

## Code facts

**Derivation entry.** `derive_reqharness_map(repo, descriptor)` at
`mapper/relmap/adapter.py:121`. The canon text is read at `mapper/relmap/adapter.py:129`:

```python
text = read_repo_text(Path(repo) / descriptor.canon, LIMIT_ROLES_YML_BYTES)
```

A `RepoReadError` is re-raised as `CanonUnavailable(cause, limit)` at
`mapper/relmap/adapter.py:130-131` (`CanonUnavailable` defined at `mapper/relmap/adapter.py:43-49`).
`descriptor.canon` for the default descriptor is the constant `CANON_NAME = "REQUIREMENTS.md"`
(`mapper/relmap/descriptor.py:57`, `default_descriptor()` at `mapper/relmap/descriptor.py:94-95`).

**Canon resolution base.** Plain filesystem join against the directory object passed as `repo`.
No git, no discovery upward, no `.git` probe anywhere in `mapper/relmap/` (grep for
`git|rev-parse|\.git` over the package: zero hits). Descriptor discovery is
`discover_descriptors(repo)` at `mapper/relmap/descriptor.py:200-208` — a flat
`os.listdir(repo)` filtered by `DESCRIPTOR_SUFFIX = ".relmap.yml"` (`:58`), capped at 8.
The bounded reader `read_repo_text` (`mapper/relmap/descriptor.py:98-143`) lstats/opens the
joined path directly; a missing file is cause K3 `"file not found"` (`:105-106`), non-UTF-8 is
K7 `"is not UTF-8 text"` (`:139-140`), binary K6, over-cap K5. The closed cause set K1–K17 is
`CAUSE` at `mapper/relmap/descriptor.py:37-55`; `refusal_line` at `:211-216`.

**Git dependence.** None at the relmap layer. Git enters only one layer up, in the reqharness
audit wrapper: `audit()` calls `identity.repo_root(root)` (`mapper/reqharness/audit.py:223`),
which runs `git rev-parse --show-toplevel` (`mapper/reqharness/identity.py:208-212`). On
`NO_REPO` the report short-circuits (`mapper/reqharness/audit.py:224-225`) and the relmap hook
is never called: `_hook_lines` returns `structure: unavailable (no repository)` for
`NO_REPO` and `structure: unavailable (no registry)` for `NO_REGISTRY`
(`mapper/reqharness/audit.py:378-381`). Only a real git repo with a `reqharness/` directory
reaches `extra_lines(Path(report.repo))` (`mapper/reqharness/audit.py:383`), where
`report.repo` is the git **toplevel** (`root = Path(top)`, `mapper/reqharness/audit.py:226`),
not necessarily the directory the operator passed. The wired surface is the `--audit` CLI
(`mapper/app.py:349-353`); no TUI screen renders `structure_lines`.

**Missing/corrupt-descriptor behavior (the `unavailable` closed set).**
`structure_lines(repo)` at `mapper/relmap/audit.py:173-206` catches `CanonUnavailable` and
renders `structure: unavailable (canon: <cause text>)` (`:182-183`, via `_cause_text`), and
`RelMapLimitError` as `structure: unavailable (canon: over the node or edge limit)`
(`:184-185`, `LIMIT_LINE` at `:41`). It never propagates. A refused `*.relmap.yml` descriptor
renders `structure: refused (<base name>): <cause> - descriptor skipped` via `refusal_line`
(`mapper/relmap/audit.py:192-197`) **on top of** the canon map still derived under the default
descriptor — the descriptor only annotates, it never replaces the canon. Canon content
corruption is NOT an unavailable state: `parse_canon` (`mapper/reqharness/derive.py:134-192`)
returns `(objects, reports)`; a broken table row becomes a reported note
(`Derivation.reported`, "unparsed row <id>"), and prose with no table at all yields an empty
map with zero notes — a healthy-looking `nodes=0` structure.

**Pointer corrections.** (1) The descriptor convention is `<name>.relmap.yml` at the
workspace root, not `<basename>_nodos.yml`; `_nodos.yml` is the **mmd map sidecar**
(`mapper/store.py:763`, missing sidecar silently treated as `{}` at `mapper/store.py:783`) —
a different pipeline. (2) The Home screen (`mapper/screens/home.py:209` globs `*.mmd`) lists
mmd maps; its refused-map state is the `⊘ dañado` damaged card (`mapper/screens/home.py:331-361`)
driven by `MapStoreError`, not the relmap `unavailable` state and not `refusal_line`.

## Probe script

```python
"""Seam probe (b): workspace-as-repo canon derivation (W1..W4 + audit wrapper)."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from mapper.relmap.adapter import CanonUnavailable, derive_reqharness_map
from mapper.relmap.audit import structure_lines
from mapper.relmap.descriptor import default_descriptor, discover_descriptors

CANON_GOOD = """\
| Id | Statement | Status |
| HLR-n1 | first high level req | active |
| LLR-n1.1 | first low level req | active |
| HLR-n2 | second high level req | active |
| LLR-n2.1 | second low level req | deferred |
"""

CANON_GARBAGE = "just some prose, no table here\n# not a canon at all\n"

CANON_BROKEN_ROW = """\
| Id | Statement | Status |
| HLR-n1 | first high level req | active |
| LLR-n1.1 | broken row here | active | extra cell |
"""


def show(label: str, tmp: Path, ws: Path) -> None:
    print(f"=== {label} ===")
    print(f"  has .git entry: {(ws / '.git').exists()}")
    try:
        paths, overflow = discover_descriptors(ws)
        print(f"  discover_descriptors: {[p.name for p in paths]} overflow={overflow}")
    except Exception as exc:  # noqa: BLE001 - probe reports whatever happens
        print(f"  discover_descriptors RAISED: {type(exc).__name__}: {exc}")
    try:
        der = derive_reqharness_map(ws, default_descriptor())
        print(
            f"  derive_reqharness_map: OK nodes={len(der.map.nodes)} "
            f"edges={len(der.map.edges)} reported={der.reported} "
            f"unlinked={der.unlinked} unknown_status={der.unknown_status}"
        )
        kinds = sorted({n.kind for n in der.map.nodes})
        print(f"  node kinds: {kinds}")
    except CanonUnavailable as exc:
        print(f"  derive_reqharness_map: CanonUnavailable cause={exc.cause!r} limit={exc.limit}")
    except Exception as exc:  # noqa: BLE001
        print(f"  derive_reqharness_map RAISED: {type(exc).__name__}: {exc}")
    try:
        lines = structure_lines(ws)
        for line in lines:
            print(f"  | {line}")
    except Exception as exc:  # noqa: BLE001
        print(f"  structure_lines RAISED: {type(exc).__name__}: {exc}")
    print()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="p2-seam-"))
    print(f"scratch root (sanitized): <tmp>={tmp.name}")

    w1 = tmp / "W1"
    w1.mkdir()
    (w1 / "REQUIREMENTS.md").write_text(CANON_GOOD, encoding="utf-8")
    (w1 / "n1.mmd").write_text("graph TD\n    n1 --> n2\n", encoding="utf-8")
    (w1 / "n1_nodos.yml").write_text("schema: []\nnodes: {}\n", encoding="utf-8")
    show("W1 bare dir + valid canon (+ mmd/_nodos.yml present)", tmp, w1)

    (w1 / ".git").mkdir()
    show("W1g W1 + EMPTY .git dir", tmp, w1)

    w1r = tmp / "W1r"
    w1r.mkdir()
    (w1r / "REQUIREMENTS.md").write_text(CANON_GOOD, encoding="utf-8")
    init = subprocess.run(
        ["git", "init", "-q", str(w1r)], capture_output=True, text=True
    )
    print(f"git init on W1r: rc={init.returncode} (real repo root: {init.returncode == 0})")
    show("W1r real git repo root + valid canon", tmp, w1r)

    w2 = tmp / "W2"
    w2.mkdir()
    show("W2 bare dir, MISSING canon", tmp, w2)

    w3a = tmp / "W3a"
    w3a.mkdir()
    (w3a / "REQUIREMENTS.md").write_bytes(b"\xff\xfe\xfd binary junk")
    show("W3a bare dir, NON-UTF8 canon bytes", tmp, w3a)

    w3b = tmp / "W3b"
    w3b.mkdir()
    (w3b / "REQUIREMENTS.md").write_text(CANON_GARBAGE, encoding="utf-8")
    show("W3b bare dir, canon = UTF-8 garbage (no table)", tmp, w3b)

    w3c = tmp / "W3c"
    w3c.mkdir()
    (w3c / "REQUIREMENTS.md").write_text(CANON_BROKEN_ROW, encoding="utf-8")
    show("W3c bare dir, canon with one broken row", tmp, w3c)

    w4 = tmp / "W4"
    w4.mkdir()
    (w4 / "REQUIREMENTS.md").write_text(CANON_GOOD, encoding="utf-8")
    (w4 / "probe.relmap.yml").write_text("kind: relation\n  bad indent: [", encoding="utf-8")
    show("W4 bare dir, valid canon + corrupt descriptor", tmp, w4)

    # The audit-wrapper layer above the hook: is it git-dependent?
    print("=== audit wrapper layer (reqharness.audit) ===")
    from mapper.reqharness import audit as rh_audit

    for label, path in (("W1 (bare)", w1), ("W1r (real git)", w1r)):
        report = rh_audit.audit(path)
        print(
            f"  {label}: chain_status={report.chain_status!r} "
            f"verdict={report.verdict!r}"
        )
        lines = rh_audit._hook_lines(report, structure_lines)
        print(f"  hook lines -> {lines}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Follow-up probe (W5: real git repo + `reqharness/` dir reaches the hook):

```python
"""Follow-up: a real git repo WITH reqharness/ reaches the relmap hook."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from mapper.reqharness import audit as rh_audit
from mapper.relmap.audit import structure_lines

CANON_GOOD = """\
| Id | Statement | Status |
| HLR-n1 | first high level req | active |
| LLR-n1.1 | first low level req | active |
"""


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="p2-seam2-"))
    ws = tmp / "W5"
    ws.mkdir()
    (ws / "REQUIREMENTS.md").write_text(CANON_GOOD, encoding="utf-8")
    (ws / "reqharness").mkdir()
    init = subprocess.run(["git", "init", "-q", str(ws)], capture_output=True, text=True)
    print(f"git init rc={init.returncode}")
    report = rh_audit.audit(ws)
    print(f"chain_status={report.chain_status!r} verdict={report.verdict!r}")
    print(f"report.repo ends with W5: {report.repo.endswith('W5')}")
    for line in rh_audit._hook_lines(report, structure_lines):
        print(f"  | {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Run transcript (sanitized)

Command (both probes):
`PYTHONPATH=<worktree> PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 python <scratch>/p2_probe.py`
(run from the worktree directory; `<scratch>` = the batch's scratch folder under the system
temp dir, temp workspaces under `%TEMP%` as `p2-seam-*`). Probe 1, first run, exit 0 — no iteration needed.

```
scratch root (sanitized): <tmp>=p2-seam-mjwb8o5n
=== W1 bare dir + valid canon (+ mmd/_nodos.yml present) ===
  has .git entry: False
  discover_descriptors: [] overflow=0
  derive_reqharness_map: OK nodes=4 edges=2 reported=() unlinked=() unknown_status=0
  node kinds: ['HLR', 'LLR']
  | structure: informational - does not change the verdict or the exit code
  | structure: descriptor (built-in default)
  | structure: profile=reqharness nodes=4 (HLR=2, LLR=2) edges=2 (refines=2) cycles=0
  | structure: sources: canon=REQUIREMENTS.md us_canon=unset at_table=unset
  | structure: gaps: 0 (HIGH=0, MED=0, LOW=0)

=== W1g W1 + EMPTY .git dir ===
  has .git entry: True
  discover_descriptors: [] overflow=0
  derive_reqharness_map: OK nodes=4 edges=2 reported=() unlinked=() unknown_status=0
  node kinds: ['HLR', 'LLR']
  | structure: profile=reqharness nodes=4 (HLR=2, LLR=2) edges=2 (refines=2) cycles=0
  ... (identical to W1)

git init on W1r: rc=0 (real repo root: True)
=== W1r real git repo root + valid canon ===
  has .git entry: True
  derive_reqharness_map: OK nodes=4 edges=2 reported=() unlinked=() unknown_status=0
  | structure: profile=reqharness nodes=4 (HLR=2, LLR=2) edges=2 (refines=2) cycles=0
  ... (identical to W1 — byte-for-byte same structure lines)

=== W2 bare dir, MISSING canon ===
  has .git entry: False
  discover_descriptors: [] overflow=0
  derive_reqharness_map: CanonUnavailable cause='file not found' limit=4194304
  | structure: informational - does not change the verdict or the exit code
  | structure: unavailable (canon: file not found)

=== W3a bare dir, NON-UTF8 canon bytes ===
  derive_reqharness_map: CanonUnavailable cause='is not UTF-8 text' limit=4194304
  | structure: unavailable (canon: is not UTF-8 text)

=== W3b bare dir, canon = UTF-8 garbage (no table) ===
  derive_reqharness_map: OK nodes=0 edges=0 reported=() unlinked=() unknown_status=0
  node kinds: []
  | structure: descriptor (built-in default)
  | structure: profile=reqharness nodes=0 edges=0 cycles=0
  | structure: gaps: 0 (HIGH=0, MED=0, LOW=0)
  (NOT unavailable — a garbage canon reads as a healthy empty map)

=== W3c bare dir, canon with one broken row ===
  derive_reqharness_map: OK nodes=1 edges=0 reported=('unparsed row LLR-n1.1',) unlinked=() unknown_status=0
  node kinds: ['HLR']
  | structure: profile=reqharness nodes=1 (HLR=1) edges=0 cycles=0
  | structure: gaps: 1 (HIGH=0, MED=1, LOW=0)
  | structure gap: MED · HLR WITHOUT LLR · HLR-n1 · reach=0 · HLR-n1 has no LLR under it: ... (canon rows near this id could not be parsed or linked: 1)
  | structure note: unparsed row LLR-n1.1
  (map still derived; corruption surfaces as notes/gaps, not unavailable)

=== W4 bare dir, valid canon + corrupt descriptor ===
  discover_descriptors: ['probe.relmap.yml'] overflow=0
  derive_reqharness_map: OK nodes=4 edges=2 reported=() unlinked=() unknown_status=0
  | structure: refused (probe.relmap.yml): not valid YAML - descriptor skipped
  (canon block suppressed for that descriptor only; refusal_line, K10 cause)

=== audit wrapper layer (reqharness.audit) ===
  W1 (bare): chain_status='no repo' verdict='not ready · no repo'
  hook lines -> ['structure: unavailable (no repository)']
  W1r (real git): chain_status='no registry yet' verdict='not ready · no registry yet'
  hook lines -> ['structure: unavailable (no registry)']
```

Probe 2 (W5), exit 0:

```
git init rc=0
chain_status='chain broken' verdict='not ready · registry not verifiable'
report.repo ends with W5: True
  | structure: informational - does not change the verdict or the exit code
  | structure: descriptor (built-in default)
  | structure: profile=reqharness nodes=2 (HLR=1, LLR=1) edges=1 (refines=1) cycles=0
  | structure: sources: canon=REQUIREMENTS.md us_canon=unset at_table=unset
  | structure: gaps: 0 (HIGH=0, MED=0, LOW=0)
```

## Result

**What today's code does.**

- **Git dependence: NO at the relmap layer.** W1 (bare dir), W1g (empty `.git`), and W1r (real
  `git init` repo) produce byte-identical derivations and structure lines. The canon is resolved
  as `Path(workspace) / "REQUIREMENTS.md"` (`mapper/relmap/adapter.py:129`) and descriptors by
  flat `os.listdir(workspace)` (`mapper/relmap/descriptor.py:204`). Nothing in `mapper/relmap/`
  mentions git.
- **W1 (non-git workspace, valid canon):** full derivation, 4 nodes / 2 `refines` edges, normal
  `structure:` block. Git presence is irrelevant.
- **W2 (missing canon):** `derive_reqharness_map` raises `CanonUnavailable` with
  `cause='file not found'` (closed cause K3) and `limit=4194304`;
  `structure_lines` catches it and returns the closed-set line
  `structure: unavailable (canon: file not found)` (`mapper/relmap/audit.py:182-183`). No
  exception escapes; never a crash.
- **W3a (non-UTF-8 canon):** same shape, `cause='is not UTF-8 text'` (K7) →
  `structure: unavailable (canon: is not UTF-8 text)`.
- **W3b (garbage-but-valid-UTF-8 canon):** NOT unavailable — an empty map with zero notes and a
  healthy-looking `nodes=0` structure block. Only read-level refusal yields `unavailable`.
- **W3c (broken table row):** map still derived; corruption appears as `Derivation.reported`
  (`unparsed row LLR-n1.1`) rendered as `structure note:` lines plus a MED gap.
- **W4 (corrupt `*.relmap.yml`):** `structure: refused (probe.relmap.yml): not valid YAML -
  descriptor skipped` via `refusal_line`; the canon block under it is skipped for that
  descriptor only.
- **Wrapper seam (the real nuance):** the only wired caller of `structure_lines` is the
  `--audit` CLI hook (`mapper/app.py:349-353` → `mapper/reqharness/audit.py:383`). That wrapper
  IS git-dependent: for a non-git workspace it short-circuits at
  `identity.repo_root` (`git rev-parse --show-toplevel`, `mapper/reqharness/identity.py:211`)
  and prints `structure: unavailable (no repository)` **without ever attempting the canon**;
  for a git repo without `reqharness/` it prints `structure: unavailable (no registry)`. Only a
  real git repo with a registry reaches the hook, with `report.repo` = the git **toplevel**
  (probe 2, W5: `report.repo.endswith('W5')` and the structure block derived even with
  `chain broken`).

**Recommended rule statement.** The LLR/AT should pin two layers separately: (1) Derivation
layer — "given any directory, the canon resolves as `<dir>/REQUIREMENTS.md` and descriptors as
`<dir>/*.relmap.yml`, flat, with no git involvement; a read-level refusal (missing/binary/
non-UTF-8/over-limit) yields `CanonUnavailable` with a K1–K7 cause, rendered as
`structure: unavailable (canon: <cause>)`; never a crash." (2) Wiring layer — "the structure
block is shown only when the audit wrapper establishes a git toplevel with a `reqharness/`
registry; otherwise the closed-set `structure: unavailable (no repository)` /
`(no registry)` line is shown and the canon is not read."

**Contradictions with the naive contract wording** (for the author to resolve — word the LLR to
match reality or schedule a fix): (a) If the contract says a bare (non-git) workspace "resolves
the canon relative to the workspace root and shows unavailable on a missing canon", that is true
of `derive_reqharness_map`/`structure_lines` in isolation but **contradicted by the only wired
surface**: a bare directory never reaches the canon read at all — the operator sees
`unavailable (no repository)`, not `unavailable (canon: file not found)`. (b) When git IS
present, the resolution base is the git **toplevel**, which can differ from the directory the
operator passed (subdirectory argument) — not "the workspace root" as given. (c) "Corrupt canon
→ unavailable" holds only for read-level corruption; content-garbage canons and broken rows
produce empty/derived maps with notes, never the `unavailable` state. (d) A corrupt/missing
`*_nodos.yml` is the **mmd map** pipeline (silently `{}` when missing, `MapStoreError` when
unreadable) and has nothing to do with the relmap canon — the known-pointer's fixture-shape and
home.py claims conflate the two pipelines.

## Notes

- Pointers corrected against the code: descriptor suffix is `.relmap.yml` (not `_nodos.yml`);
  `refusal_line` is reached only from `structure_lines` (`mapper/relmap/audit.py:195`), not from
  the Home screen; Home's refused-map state is the `⊘ dañado` card for the mmd pipeline
  (`mapper/screens/home.py:331-361`). The Home screen does not render relation-map structure at
  all — the `unavailable` closed set is a CLI (`--audit`) surface today.
- `derive_reqharness_map` requires `PYTHONPATH=<worktree>` (package not installed).
- `default_descriptor()` pins `canon="REQUIREMENTS.md"`, so the `source.canon` field of a
  descriptor can only ever equal the default (K14 otherwise, `mapper/relmap/descriptor.py:183`).
- Probe hygiene: probe scripts lived in `<scratch>` and were deleted after the transcript was
  captured; all `p2-seam-*` temp workspaces under `%TEMP%` were deleted. This transcript is the
  only retained artifact; all paths and node names are neutralized.
