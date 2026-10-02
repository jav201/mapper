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
import re
import stat
import subprocess
import sys
from pathlib import Path, PureWindowsPath
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

# `U1` (Round 10): the one sentence for a typed or stored path outside the allow-list; it names nothing.
# `V1` (Round 11): the second sentence, for a path the allow-list accepts but the workspace does not
# contain.  Both live here so `app` and `screens` import them without a `screens` -> `app` edge.
PATH_NOT_SUPPORTED = "path not supported: use C:\\\u2026 or a relative path"
PATH_OUTSIDE_WORKSPACE = "attachment must be inside the workspace: use a relative path"
# `W2` (Round 12): the third sentence, for a path that goes through a link or reparse point inside the workspace.
PATH_THROUGH_LINK = "path goes through a link: use a real folder inside the workspace"


_DRIVE = re.compile(r"[A-Za-z]:")


def safe_local_path(text: str) -> Path | None:
    r"""`S1` applied to a typed LOCAL path: a closed allow-list, decided on strings before any
    filesystem call, so no SMB or NTLM lookup and no NT-namespace path is ever probed.

    Refused (None): an empty text, a NUL, a leading `-`; a `~` that cannot be expanded; a DOS device
    name (`con`, `nul`, `conin$`, `com1`, `aux`, `lpt1`...) in ANY component, with an extension, trailing
    dots or spaces, in any case; and everything that is not (a) drive-absolute (a letter drive and a
    root, as `C:\x`) or (b) relative (no drive and no root).  That covers UNC, `\\?\`, `\\.\`, `\??\`,
    `/??/`, root-relative `\x` and drive-relative `C:x`.  The caller may stat the returned path, and only
    then.
    """
    if not isinstance(text, str) or not text or "\x00" in text or text.startswith("-"):
        return None
    try:
        # `INC9O-CR-F5`: only a text that STARTS with `~` is expanded; `./~x` is a plain relative name (pathlib
        # drops the `./`, so asking `expanduser` about the parsed path would expand it).
        expanded = Path(text).expanduser() if text.startswith("~") else Path(text)
        parsed = PureWindowsPath(str(expanded))
    except (RuntimeError, OSError, ValueError):
        return None
    # `INC9M-SEC-F2`: opening a device name hangs (`Import-CSV CON` was measured to) or reads a console.
    # `PureWindowsPath.is_reserved()` (3.12) judges the LAST component only, so every component is asked;
    # Python 3.13 spells it `os.path.isreserved`.
    if any(PureWindowsPath(part).is_reserved() for part in parsed.parts):
        return None
    if _DRIVE.fullmatch(parsed.drive) and parsed.root == "\\":
        return expanded
    if not parsed.drive and not parsed.root:
        return expanded
    return None


def _lexically_inside(local: Path, workspace: Path) -> str | None:
    """The absolute, normalised target when it lies under *workspace* by TEXT alone, else None.  No
    filesystem call (`abspath` only joins and collapses `..`).  The comparison is by path parts, so
    `ws2` is not inside `ws`, and case-folded by `normcase` (a no-op off Windows)."""
    root = os.path.abspath(workspace)
    joined = os.path.abspath(Path(workspace) / local)
    if Path(os.path.normcase(joined)).is_relative_to(os.path.normcase(root)):
        return joined
    return None


def lexically_outside(text: str, workspace: Path) -> bool:
    """True when `confine_reason` refuses *text* as `outside` (`V2`, `INC9O-CR-F1`): the one step 2, not a
    second rule.  A refused text (allow-list, normalised) is not 'outside': it is unsupported."""
    return confine_reason(text, workspace)[1] == "outside"


def _is_link(info: os.stat_result) -> bool:
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def confine_reason(text: str, workspace: Path) -> tuple[Path | None, str]:
    """The ONE containment rule, with its cause: `(resolved, "ok")` or `(None, reason)`.

    Reasons: `allow_list` (`safe_local_path` refused), `normalised` (a component Windows rewrites), `outside`
    (lexically, or after `resolve()`), `link` (a symlink or reparse point under the workspace), `unreadable`
    (a component could not be inspected, or `resolve()` failed).

    In order: (1) `safe_local_path` (the closed allow-list; it expands `~` for every caller, so add and open
    agree); (1b) `INC9O-SEC-F1`: refuse, on the text and before ANY filesystem call, a component other than
    `.` and `..` that ends in a dot or a space (`...`, `. .`, `d `, `d. .`): Windows normalises it, so the walk
    below would stop early and `resolve()` would follow a link behind it; (2) lexical containment, no stat;
    (3) a walk from the workspace down with `os.lstat`, refusing a symlink or any reparse point (junction,
    mount point) BEFORE anything below it is touched; (4) only then `resolve()` and a last `is_relative_to`.
    Policy: links inside the workspace are not followed.  The workspace root itself may be a link; only what
    lies under it is walked.
    """
    local = safe_local_path(text)
    if local is None:
        return None, "allow_list"
    if any(part not in (".", "..") and part != part.rstrip(" .") for part in local.parts):
        return None, "normalised"
    joined = _lexically_inside(local, workspace)
    if joined is None:
        return None, "outside"
    root = Path(os.path.abspath(workspace))
    current = root
    for part in Path(joined).parts[len(root.parts):]:
        current = current / part
        try:
            info = os.lstat(current)
        except (FileNotFoundError, NotADirectoryError):
            break
        except (OSError, ValueError):
            return None, "unreadable"
        if _is_link(info):
            return None, "link"
    try:
        resolved = (Path(workspace) / local).resolve()
        if not resolved.is_relative_to(Path(workspace).resolve()):
            return None, "outside"
    except (OSError, ValueError):
        return None, "unreadable"
    return resolved, "ok"


def confine(text: str, workspace: Path) -> Path | None:
    """The resolved target of *text* inside *workspace*, or None; see `confine_reason` for the rule."""
    return confine_reason(text, workspace)[0]


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
    # A NUL or other C0/C1 control reaches here from a plain-ASCII sidecar via
    # YAML's escape syntax (a YAML double-quoted escape for the NUL character, followed by a URL).  `urlparse` then
    # reads a perfectly good `https` scheme and the allowlist waves it through,
    # but `os.startfile` raises ValueError — not OSError — on the embedded NUL,
    # and the application dies.  Refuse the whole class here rather than relying
    # on every downstream launcher to survive it.
    if any(ord(ch) < 0x20 or 0x7F <= ord(ch) <= 0x9F for ch in target):
        return REFUSED_TYPE

    launch = launcher or _default_launcher

    if kind == "url":
        try:
            parsed = urlparse(target.strip())
            scheme = parsed.scheme.lower()
        except ValueError:
            return REFUSED_TYPE
        if scheme not in ALLOWED_SCHEMES:
            return REFUSED_SCHEME
        # `https://example.com@evil.example.com/` reads as example.com and goes to
        # evil.example.com.  Userinfo has no legitimate use in an attachment and
        # is exactly the shape of a link that lies about its destination.
        if "@" in parsed.netloc:
            return REFUSED_SCHEME
        try:
            launch(target.strip())
        except (OSError, ValueError):
            return REFUSED_ERROR
        return OK

    # `INC9L-SEC-F5`: the same closed allow-list as a typed path, BEFORE `resolve()`: resolving
    # a UNC or NT-namespace target is itself a network or device lookup.
    if kind == "file" and safe_local_path(target) is None:
        return REFUSED_TYPE

    # kind == "file": confinement is the control, and it is checked BEFORE the launcher is reached.
    # Existence is NOT an authorisation: the containment test runs whether or not the path is there.
    resolved = confine(target, Path(workspace))
    if resolved is None:
        return REFUSED_OUTSIDE
    if not resolved.is_file():
        return REFUSED_ERROR
    try:
        launch(str(resolved))
    except (OSError, ValueError):
        return REFUSED_ERROR
    return OK
