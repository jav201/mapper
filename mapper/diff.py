"""Diff a map against its last committed version in git."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .github import _git_env
from .model import Graph, SchemaField
from .store import MapStore


@dataclass
class DiffResult:
    """Node-level diff between the working tree and HEAD."""

    added: set[str] = field(default_factory=set)
    removed: set[str] = field(default_factory=set)
    changed: dict[str, list[str]] = field(default_factory=dict)
    removed_titles: dict[str, str] = field(default_factory=dict)


def git_diff(map_id: str, store: MapStore) -> DiffResult | None:
    """Return a node-level diff of the current graph vs HEAD.

    Returns None if git is unavailable, the workspace is not a repository,
    or the files are not present in HEAD.
    """
    ws = Path(store.workspace)
    if not (ws / ".git").is_dir():
        return None

    def _show(path: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", "show", f"HEAD:{path}"],
                cwd=ws,
                capture_output=True,
                check=True,
                # `INC9G-SEC-F5`: the one environment every `git` call here runs in.
                env=_git_env(),
            )
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return None
        # Review inc004-F1 (MAJOR): the decode happens HERE, behind the pinned
        # `subprocess.run` seam (`tests/test_inc9h.py` pins argv+env, not
        # `text=`), never via `text=True` — decoding inside subprocess's reader
        # thread let an undecodable HEAD object (a legacy latin-1 committed
        # `.mmd`) escape the None-on-error contract: a raise on POSIX, a
        # swallowed thread exception (and stderr traceback spam) on Windows.
        # This is the pre-increment guard, restored on the new seam.
        try:
            return result.stdout.decode("utf-8")
        except UnicodeDecodeError:
            return None

    mmd_text = _show(f"{map_id}.mmd")
    yml_text = _show(f"{map_id}_nodos.yml")
    if mmd_text is None or yml_text is None:
        return None

    try:
        # The caps reach this side ONLY through the store edge (ruling R8 — no
        # `diff -> osopen` import).  S1 (PDR security finding, ruling R9) —
        # disposition REVISED at the L2b gate: the capture stays on the
        # `subprocess.run` seam because `tests/test_inc9h.py` pins that exact
        # invocation shape, and bounding it needs `Popen`; the store instead
        # refuses texts over the map cap before any parse (acceptance with
        # rationale, recorded in increment-004 section 5/6).  Any refusal here
        # still becomes None — the None-on-error contract is preserved.
        old_graph = store._capped_side_graph(map_id, mmd_text, yml_text)
    except Exception:
        return None

    return _compare_graphs(old_graph, store.load(map_id))


def _compare_graphs(old: Graph, current: Graph) -> DiffResult:
    """Compare two graphs and return added/removed/changed node ids."""
    old_ids = set(old.nodes)
    current_ids = set(current.nodes)

    result = DiffResult(
        added=current_ids - old_ids,
        removed=old_ids - current_ids,
        removed_titles={
            nid: old.nodes[nid].ficha.title or nid
            for nid in old_ids - current_ids
        },
    )

    schema_keys = {f.key for f in current.schema or old.schema}

    for nid in old_ids & current_ids:
        old_node = old.nodes[nid]
        cur_node = current.nodes[nid]
        changed: list[str] = []

        if old_node.ficha.title != cur_node.ficha.title:
            changed.append("title")

        for key in schema_keys:
            old_val = old_node.ficha.fields.get(key, "")
            cur_val = cur_node.ficha.fields.get(key, "")
            if old_val != cur_val:
                changed.append(key)

        if changed:
            result.changed[nid] = changed

    return result
