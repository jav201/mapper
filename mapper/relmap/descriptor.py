"""Bounded repository reads and the relation descriptor (HLR-RML.1, LLR-RML.1.1-.1.6).

`read_repo_text` is the only way the relation-map package reads a repository file; every
refusal is one of the closed causes K1-K17 (`CAUSE`), a FIXED string: a cause is never
`str(exc)`, a path, an anchor name or a YAML snippet.  Read-only by contract (no write, no
process, no network).  The lines `refusal_line` returns are repository-derived and UNESCAPED:
the sink must escape (`run_cli` does); the base name is cut here.

`read_repo_text` is a file-type guard, not a confinement.  `us_canon` / `at_table` are
confined (`confine_reason`) and NEVER opened in R1; the batch that first opens one calls
`confine_reason` again at open time and then `read_repo_text`.
"""
from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

import yaml

from mapper.osopen import (
    MAX_MAP_BYTES,
    ContentReadError,
    confine_reason,
    is_link,
    read_capped,
)
from mapper.relmap.model import cut
from mapper.relmap.profile import REQHARNESS
from mapper.yamlscan import YamlLimitError, prescan

#: The closed cause set.  Read-only (`MappingProxyType`): no caller can rewrite it at run time.
#: K5 is stored without its number; `refusal_line` renders `exceeds the <N> byte limit`.
#: K16 and K17 are templates the loader fills with the field name and the confinement reason.
CAUSE = MappingProxyType({
    "K1": "is a link",
    "K2": "is not a regular file",
    "K3": "file not found",
    "K4": "could not read file",
    "K5": "exceeds the byte limit",
    "K6": "looks binary",
    "K7": "is not UTF-8 text",
    "K8": "contains YAML anchors or aliases",
    "K9": "nests deeper than the depth limit",
    "K10": "not valid YAML",
    "K11": "not a mapping",
    "K12": "unsupported kind",
    "K13": "unsupported profile",
    "K14": "unsupported canon source",
    "K15": "source is not a mapping",
    "K16": "source.{key} is not text",
    "K17": "unsafe path in {field} ({reason})",
})

CANON_NAME = "REQUIREMENTS.md"
DESCRIPTOR_SUFFIX = ".relmap.yml"
MAX_DESCRIPTORS = 8
_PATH_FIELDS = ("us_canon", "at_table")


class RepoReadError(Exception):
    """A repository read refused.  `cause` is the fixed text of K1-K7, `limit` the cap given."""

    def __init__(self, cause: str, limit: int) -> None:
        super().__init__(cause)
        self.cause = cause
        self.limit = limit


class DescriptorError(Exception):
    """A descriptor refused.  `cause` is the fixed text of K1-K17, `name` the file's BASE NAME.

    The message is the base name and the cause only.  `limit` is the cap behind a K5.
    """

    def __init__(self, cause: str, name: str, limit: int | None = None) -> None:
        super().__init__(f"{name}: {cause}")
        self.cause = cause
        self.name = name
        self.limit = limit


@dataclass(frozen=True)
class Descriptor:
    profile: str
    canon: str
    us_canon: str | None
    at_table: str | None
    ignored_keys: tuple[str, ...]


def default_descriptor() -> Descriptor:
    return Descriptor(REQHARNESS.name, CANON_NAME, None, None, ())


def read_repo_text(path: Path, cap: int) -> str:
    """`path` as text, or `RepoReadError` (K1-K7).  lstat, refuse links and non-regular files
    before any open, open once, compare the opened file's identity with the lstat result, then
    `read_capped`.  The window between the identity check and `read_capped`'s own open needs
    write access to the audited repository and the read stays read-only and capped."""
    try:
        before = os.lstat(path)
    except FileNotFoundError:
        raise RepoReadError(CAUSE["K3"], cap) from None
    except OSError:
        raise RepoReadError(CAUSE["K4"], cap) from None
    if is_link(before):
        raise RepoReadError(CAUSE["K1"], cap)
    if not stat.S_ISREG(before.st_mode):
        raise RepoReadError(CAUSE["K2"], cap)
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(path, flags)
    except FileNotFoundError:
        raise RepoReadError(CAUSE["K3"], cap) from None
    except OSError:
        raise RepoReadError(CAUSE["K4"], cap) from None
    try:
        after = os.fstat(fd)
    except OSError:
        raise RepoReadError(CAUSE["K4"], cap) from None
    finally:
        os.close(fd)
    # Some network and FAT mounts report st_ino = 0: the inode joins the comparison only when
    # both values are known.
    inode_differs = bool(before.st_ino and after.st_ino and before.st_ino != after.st_ino)
    if not stat.S_ISREG(after.st_mode) or after.st_dev != before.st_dev or inode_differs:
        raise RepoReadError(CAUSE["K2"], cap)
    try:
        return read_capped(path, cap)
    except ContentReadError as exc:
        text = str(exc)
        if text.startswith("file exceeds"):
            raise RepoReadError(CAUSE["K5"], cap) from None
        if text.startswith("file looks binary"):
            raise RepoReadError(CAUSE["K6"], cap) from None
        if text.startswith("file is not UTF-8"):
            raise RepoReadError(CAUSE["K7"], cap) from None
        raise RepoReadError(CAUSE["K4"], cap) from None
    except OSError:
        raise RepoReadError(CAUSE["K4"], cap) from None


def load_descriptor(path: Path, repo: Path) -> Descriptor:
    """The descriptor at `path`, or `DescriptorError` (K1-K17) naming only its base name."""
    path = Path(path)
    name = path.name
    try:
        text = read_repo_text(path, MAX_MAP_BYTES)
    except RepoReadError as exc:
        raise DescriptorError(exc.cause, name, exc.limit) from None
    try:
        prescan(text)
        data = yaml.safe_load(text)
    except YamlLimitError as exc:
        key = "K8" if exc.kind == "anchor" else "K9"
        raise DescriptorError(CAUSE[key], name) from None
    except (yaml.YAMLError, ValueError, RecursionError):
        raise DescriptorError(CAUSE["K10"], name) from None
    return _from_mapping(data, name, repo)


_ABSENT = object()


def _from_mapping(data: object, name: str, repo: Path) -> Descriptor:
    if not isinstance(data, dict):
        raise DescriptorError(CAUSE["K11"], name)
    kind = data.get("kind", _ABSENT)
    if kind is not _ABSENT and not (isinstance(kind, str) and kind == "relation"):
        raise DescriptorError(CAUSE["K12"], name)
    profile = data.get("profile", _ABSENT)
    if profile is not _ABSENT and not (isinstance(profile, str) and profile == REQHARNESS.name):
        raise DescriptorError(CAUSE["K13"], name)
    source = data.get("source", _ABSENT)
    paths: dict[str, str | None] = {field: None for field in _PATH_FIELDS}
    if source is not _ABSENT:
        if not isinstance(source, dict):
            raise DescriptorError(CAUSE["K15"], name)
        canon = source.get("canon", _ABSENT)
        if canon is not _ABSENT and not (isinstance(canon, str) and canon == CANON_NAME):
            raise DescriptorError(CAUSE["K14"], name)
        for field in _PATH_FIELDS:
            value = source.get(field, _ABSENT)
            if value is _ABSENT:
                continue
            if not isinstance(value, str):
                raise DescriptorError(CAUSE["K16"].format(key=field), name)
            _resolved, reason = confine_reason(value, repo)
            if reason != "ok":
                raise DescriptorError(CAUSE["K17"].format(field=field, reason=reason), name)
            paths[field] = value
    ignored = tuple(cut(str(key)) for key in data if key not in ("kind", "profile", "source"))
    return Descriptor(
        REQHARNESS.name, CANON_NAME, paths["us_canon"], paths["at_table"], ignored)


def discover_descriptors(repo: Path) -> tuple[tuple[Path, ...], int]:
    """(at most 8 `*.relmap.yml` paths of the repository root, sorted by code point; how many
    more exist).  A link, a directory or any other entry is listed too: reading it refuses it."""
    try:
        names = os.listdir(repo)
    except OSError:
        return (), 0
    found = sorted(n for n in names if n.endswith(DESCRIPTOR_SUFFIX))
    return tuple(Path(repo) / n for n in found[:MAX_DESCRIPTORS]), max(0, len(found) - MAX_DESCRIPTORS)


def refusal_line(base_name: str, cause: str, limit: int | None = None) -> str:
    """`structure: refused (<base name>): <cause> - descriptor skipped`.  The base name is cut
    to 120 characters; K5 renders `exceeds the <limit> byte limit` when `limit` is given."""
    if cause == CAUSE["K5"] and limit is not None:
        cause = f"exceeds the {limit} byte limit"
    return f"structure: refused ({cut(base_name)}): {cause} - descriptor skipped"
