"""The OS-handler boundary — the highest-risk crossing in this system.

An attachment target is *file-derived text*: it comes out of `_nodos.yml`, which a
human edits by hand and which arrives with a cloned or shared map.  Handing that
to an OS handler is program execution driven by document content, so this module
exists as one greppable file with one job: decide whether a target may be opened,
and refuse everything else **before** any launcher runs.

Measured on this machine before the confinement rule existed: a `..` traversal
target launched a file outside the workspace, and both `calc.exe` and
`powershell.exe` launched.  `os.startfile`'s own documentation says it "acts like
double-clicking the file in Explorer".

Two bans from `docs/ARCHITECTURE.md` §3 shape the signature: this module imports
nothing from `mapper` (so it cannot discover its own targets, and the audit
surface stays one file), and only `app` may call it (so the call site is
countable).  It therefore takes plain strings plus the workspace root.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

# Only these two kinds are openable at all.  `image` is a display concern, not a
# launch one.
OPENABLE_KINDS = ("url", "file")

# For `kind == "url"`.  Deliberately NOT including `file:` — a file URL would give
# the URL branch an unconfined path, routing around the workspace check below.
# Local files travel as `kind == "file"` and are confined.
ALLOWED_SCHEMES = ("http", "https")

# Status words.  The caller shows these; this module never raises for anything
# reachable from a `yaml.safe_load` of a sidecar.
OK = "abierto"
REFUSED_KIND = "tipo no abrible"
REFUSED_TYPE = "destino inválido"
REFUSED_SCHEME = "esquema no permitido"
REFUSED_OUTSIDE = "fuera del espacio de trabajo"
REFUSED_ERROR = "no se pudo abrir"


def _default_launcher(target: str) -> None:
    """Hand *target* to the platform's default handler, never through a shell."""
    if sys.platform == "win32":
        os.startfile(target)  # noqa: S606 - single path argument, no command line
    elif sys.platform == "darwin":
        subprocess.run(["open", target], check=False)
    else:
        subprocess.run(["xdg-open", target], check=False)


def open_external(
    kind: str,
    target: str,
    *,
    workspace: Path,
    launcher: Callable[[str], None] | None = None,
) -> str:
    """Open an attachment target, or refuse it and say why.

    Returns a status word; never raises for input a sidecar could contain.  The
    caller is responsible for showing the refusal — a dropped return value would
    make a refusal indistinguishable from a success.
    """
    if kind not in OPENABLE_KINDS:
        return REFUSED_KIND
    # A sidecar can hold any YAML scalar: `path: 12345` parses to an int, and a
    # missing value to None.  Neither may reach a launcher, and neither may raise.
    if not isinstance(target, str) or not target.strip():
        return REFUSED_TYPE

    launch = launcher or _default_launcher

    if kind == "url":
        try:
            scheme = urlparse(target.strip()).scheme.lower()
        except ValueError:
            return REFUSED_TYPE
        if scheme not in ALLOWED_SCHEMES:
            return REFUSED_SCHEME
        try:
            launch(target.strip())
        except OSError:
            return REFUSED_ERROR
        return OK

    # kind == "file": confinement is the control, and it is checked BEFORE the
    # launcher is reached.  Existence is NOT an authorisation — it answers "will
    # this fail?", not "should this open?" — so the containment test runs whether
    # or not the path is there.
    try:
        resolved = (workspace / target).resolve() if not Path(target).is_absolute() \
            else Path(target).resolve()
        root = Path(workspace).resolve()
    except (OSError, ValueError):
        return REFUSED_TYPE
    if not resolved.is_relative_to(root):
        return REFUSED_OUTSIDE
    if not resolved.exists():
        return REFUSED_ERROR
    try:
        launch(str(resolved))
    except OSError:
        return REFUSED_ERROR
    return OK
