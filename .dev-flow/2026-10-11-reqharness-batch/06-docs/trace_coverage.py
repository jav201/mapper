"""Coverage check for 06-docs/traceability-matrix.md (batch 2026-10-11-reqharness-batch).

Parses 01-requirements.md for every US/HLR/LLR/AT id, parses the matrix's §1
and §1b tables, verifies:

* every requirements-doc id appears in the matrix (US/HLR/LLR in §1, AT in §1b);
* every matrix row's US/HLR/LLR ids exist in the requirements doc;
* every `T/<file>::<node>` selector cites at least one real collected node
  (checked against `pytest --collect-only` over the union of cited files);
* coverage percentages (computed, not hand-counted) — printed at the end.

Run from the repo root:  python .dev-flow/2026-10-11-reqharness-batch/06-docs/trace_coverage.py
Exit 0 and "COVERAGE OK" iff every check holds.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / ".dev-flow" / "2026-10-11-reqharness-batch"
REQ = BATCH / "01-requirements.md"
MATRIX = BATCH / "06-docs" / "traceability-matrix.md"

US_RE = re.compile(r"\b(US-RH-\d{3})\b")
HLR_RE = re.compile(r"^### (HLR-RH\.\d+) — ")
LLR_RE = re.compile(r"^### (LLR-RH\.\d+\.\d+) — ")
# The bare umbrella AT-077 is never itself a declared acceptance id (P1 premise 2).
AT_RE = re.compile(r"\b(AT-077[a-c]|AT-07[89]|AT-08[0-3])\b")
SELECTOR_RE = re.compile(r"(?:T|tests)/([\w/]+\.py)::([A-Za-z0-9_]+)")


def req_ids() -> dict[str, set[str]]:
    ids = {"US": set(), "HLR": set(), "LLR": set(), "AT": set()}
    for line in REQ.read_text(encoding="utf-8").splitlines():
        for key, rx in (("US", US_RE), ("HLR", HLR_RE), ("LLR", LLR_RE), ("AT", AT_RE)):
            ids[key].update(rx.findall(line))
    return ids


def matrix_tables() -> tuple[list[list[str]], list[list[str]]]:
    """§1 rows and §1b rows as cell lists."""
    text = MATRIX.read_text(encoding="utf-8").splitlines()
    rows1, rows1b = [], []
    target = None
    for line in text:
        if line.startswith("## 1b"):
            target = rows1b
            continue
        if line.startswith("## 1 "):
            target = rows1
            continue
        if line.startswith("## 2 "):
            target = None
        if target is not None and line.startswith("| US |"):
            continue
        if target is not None and line.startswith("|---"):
            continue
        if target is not None and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            target.append(cells)
    return rows1, rows1b


def collected_nodes(files: set[str]) -> dict[str, set[str]]:
    out = subprocess.run(
        [sys.executable, "-B", "-m", "pytest", "--collect-only", "-q",
         "-p", "no:cacheprovider", *sorted(files)],
        cwd=ROOT, capture_output=True, text=True,
    )
    nodes: dict[str, set[str]] = {f: set() for f in files}
    for line in out.stdout.splitlines():
        if "::" not in line:
            continue
        f, _, rest = line.partition("::")
        f = f.strip().replace("\\", "/")
        if f in nodes:
            nodes[f].add(rest.strip())
    return nodes


def main() -> int:
    ids = req_ids()
    rows1, rows1b = matrix_tables()
    errors: list[str] = []

    m_us = {r[0] for r in rows1}
    m_hlr = {r[1] for r in rows1}
    m_llr = {r[2] for r in rows1}
    m_at = {r[1] for r in rows1b}

    for key, mset in (("US", m_us), ("HLR", m_hlr), ("LLR", m_llr), ("AT", m_at)):
        missing = ids[key] - mset
        extra = mset - ids[key]
        if missing:
            errors.append(f"{key} in requirements but not in matrix: {sorted(missing)}")
        if extra:
            errors.append(f"{key} in matrix but not in requirements: {sorted(extra)}")

    files: set[str] = set()
    selectors: list[tuple[str, str]] = []
    for r in rows1:
        for f, node in SELECTOR_RE.findall(r[3]):
            path = f"tests/{f}" if not f.startswith("tests/") else f
            files.add(path)
            selectors.append((path, node))
    nodes = collected_nodes(files)
    for f, node in selectors:
        hits = {n for n in nodes.get(f, set()) if n == node or n.startswith(node + "[")}
        if not hits:
            errors.append(f"selector collects 0: T/{f}::{node}")

    n_us = len(ids["US"])
    n_hlr = len(ids["HLR"])
    n_llr = len(ids["LLR"])
    n_at = len(ids["AT"])
    llr_covered = sum(1 for r in rows1 if r[2] in ids["LLR"] and r[3].strip())
    hlr_covered = len({r[1] for r in rows1 if r[3].strip()})
    us_covered = len({r[0] for r in rows1 if r[3].strip()})

    print(f"requirements: {n_us} US, {n_hlr} HLR, {n_llr} LLR, {n_at} AT")
    print(f"US coverage:     {us_covered}/{n_us} = {us_covered / n_us:.0%}")
    print(f"HLR coverage:    {hlr_covered}/{n_hlr} = {hlr_covered / n_hlr:.0%}")
    print(f"LLR coverage:    {llr_covered}/{n_llr} = {llr_covered / n_llr:.0%}")
    print(f"AT coverage:     {len(m_at & ids['AT'])}/{n_at} = {len(m_at & ids['AT']) / n_at:.0%}")
    print(f"selectors checked: {len(selectors)} across {len(files)} files")

    if errors:
        print("\n".join(errors))
        print("COVERAGE FAILED")
        return 1
    print("COVERAGE OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
