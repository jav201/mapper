"""A-110 -- no tracked file names the operator's real Windows account.

Two arms, and they answer two different questions:

* `test_a110_no_undeclared_user_profile_path_in_any_tracked_file` is the
  HERMETIC arm. It reads only `ALLOWED_PATH_SEGMENTS`, a declared allow-list
  of placeholder and hostile-fixture names this repo's tracked `.dev-flow`
  records already carry inside a `.../Users/<name>/...` path -- never the
  environment's own username -- so its verdict does not depend on who runs
  it. Any OTHER name segment inside a user-profile path is refused.
* `test_a110_the_real_operator_username_appears_nowhere` is the BACKSTOP. It
  reads the real account name from `USERNAME` at run time (never hardcoded
  here -- that would BE the leak this test exists to prevent) and asserts it
  appears in no tracked file at all, inside a path or not. It does not
  consult `ALLOWED_PATH_SEGMENTS`, so widening that list can never blind it.
  It skips cleanly when `USERNAME` is unset (non-Windows CI).

Traceability: `A-110` (`.dev-flow/2026-08-26-ui-next-batch-02/01-requirements.md`),
which discharges the identity half of backlog carry `B-22`.
"""
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

#: A Windows user-profile path in any of the three spellings A-110 declares:
#: one or two backslashes, or a forward slash, before AND after `Users`.
USER_PROFILE_PATH = re.compile(
    r"[A-Za-z]:(?:\\{1,2}|/)Users(?:\\{1,2}|/)([^\\/\"'\s]+)"
)

#: Every name segment this repo's tracked files are declared to carry inside
#: a user-profile path, and why each one is not a real account. A-110 is the
#: authority for this list; widening it is a requirements change, not a test
#: edit made in passing.
ALLOWED_PATH_SEGMENTS: dict[str, str] = {
    "<operator>": "the redaction placeholder A-110 itself introduces",
    "<user>": "a generic placeholder used quoting an evidence-transcript path",
    "<USER>": "a generic placeholder used in a redacted probe-output quote",
    "<username>": "a generic placeholder named in a security-review note",
    "OP": "a reviewer-constructed path (`.../Users/OP/.ssh/id_rsa`) built for "
          "a security probe, not a real account",
    "secret]click[": "a hostile markup-injection fixture proving link/style "
                      "escaping (`file:///C:/Users/secret]click[/link]`), "
                      "not an account",
    "secret": "the SAME hostile fixture above, captured a second time where "
              "a `'` in its own surrounding quote truncates the match early",
    "%USERPROFILE%": "the declared non-identifying spelling of the profile "
                      "directory",
}


@dataclass(frozen=True)
class Hit:
    path: str
    line_no: int
    segment: str


def tracked_files(root: Path) -> list[Path]:
    """Every file `git` tracks under `root`, as absolute paths."""
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root, capture_output=True, check=True,
    ).stdout
    return [root / p for p in out.decode("utf-8").split("\0") if p]


def scan_user_profile_paths(root: Path) -> list[Hit]:
    """Every user-profile path segment in every tracked file under `root`.

    Takes `root` as a parameter, rather than closing over `REPO_ROOT`, so the
    mutation battery can drive the SAME function this suite uses over a
    synthetic tree outside the real repo -- a probe that reimplements the
    scan to test the scan cannot disagree with its author.
    """
    hits: list[Hit] = []
    for path in tracked_files(root):
        if not path.is_file():
            continue
        text = path.read_bytes().decode("utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for m in USER_PROFILE_PATH.finditer(line):
                hits.append(Hit(str(path.relative_to(root)), line_no, m.group(1)))
    return hits


def undeclared_hits(root: Path) -> list[Hit]:
    return [h for h in scan_user_profile_paths(root) if h.segment not in ALLOWED_PATH_SEGMENTS]


def test_a110_no_undeclared_user_profile_path_in_any_tracked_file():
    """A-110: every tracked user-profile path segment is a declared placeholder.

    Hermetic by construction -- it never reads `os.environ`, so the same
    tree gives the same verdict on any machine, under any account.
    """
    bad = undeclared_hits(REPO_ROOT)
    assert not bad, (
        f"{len(bad)} tracked line(s) carry a user-profile path segment that "
        "is not in ALLOWED_PATH_SEGMENTS (A-110): "
        + "; ".join(f"{h.path}:{h.line_no} -> {h.segment!r}" for h in bad[:25])
    )


def test_a110_the_real_operator_username_appears_nowhere():
    """A-110's backstop: literal search for the real account name.

    Deliberately ignores `ALLOWED_PATH_SEGMENTS` and ignores whether the
    match sits inside a path at all -- it is the arm that still catches a
    leak if the allow-list above is ever widened past what it should hold.
    """
    username = os.environ.get("USERNAME")
    if not username:
        pytest.skip("USERNAME is not set in this environment")

    offenders: list[str] = []
    for path in tracked_files(REPO_ROOT):
        if not path.is_file():
            continue
        if username.encode("utf-8") in path.read_bytes():
            offenders.append(str(path.relative_to(REPO_ROOT)))

    assert not offenders, (
        f"the real account name (read from $USERNAME, not printed here) "
        f"appears in {len(offenders)} tracked file(s): "
        + ", ".join(offenders[:25])
    )
