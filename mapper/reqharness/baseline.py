"""Baselines: the frozen derivation and the five-class diff (HLR-RH.6).

A baseline freezes the CURRENT derivation — objects (id, class, normative
digest, state), the verified chain head, the review file set, the creation
time — under ``reqharness/baselines/<name>.yml``, bound to the repository's
current commit SHA (read-only ``git rev-parse HEAD``) and a ``dirty`` flag
from read-only ``git status --porcelain --no-optional-locks`` (LLR-RH.6.1).
The dirty flag is taken ONLY here, in the operator's own repo, at
``Baseline.create`` (R27a: ``--audit`` runs NO ``git status``); it is
recorded and refuses nothing.  The stated residual: baseline creation
trusts the repo's ``.git/config``.  Git tagging stays a manual act (O9).

The diff classifies every union id (LLR-RH.6.2, R13/R24 — five classes,
``reactivated`` and the review-state progression are DEFERRED, B-125):

    new        absent from the baseline, present now
    changed    the normative digest moved (both sides present)
    retired    active in the baseline, retired now
    unchanged  the digest and the state hold
    deleted    in the baseline, absent from the canon now — including a
               deleted review file, via the baseline's frozen review set

comparing either two baselines or a baseline against the current state.
"""
from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mapper.reqharness import identity
from mapper.reqharness.chain import ChainReport
from mapper.reqharness.config import (
    REQHARNESS_DIR,
    check_int,
    check_str,
    check_time,
    load_config,
    load_documents,
)
from mapper.reqharness.derive import (
    CANON_NAME,
    STATE_RETIRED,
    CanonObject,
    Derivation,
    derive_states,
    load_canon,
    object_digests,
)
from mapper.reqharness.records import Config, ValidationError
from mapper.reqharness.release import safe_verify
from mapper.reqharness.reviews import (
    REVIEW_DIR,
    ReviewScan,
    load_reviews,
    scan_event_dir,
)

BASELINES_DIR = "baselines"
BASELINE_WHERE = f"{REQHARNESS_DIR}/{BASELINES_DIR}"

CLASS_NEW = "new"
CLASS_CHANGED = "changed"
CLASS_UNCHANGED = "unchanged"
CLASS_RETIRED = "retired"
CLASS_DELETED = "deleted"


@dataclass(frozen=True)
class FrozenObject:
    """One object of a frozen (or current) derivation."""

    id: str
    class_id: str
    normative_digest: str
    state: str


@dataclass(frozen=True)
class Snapshot:
    """The full current derivation, ready to freeze or diff: the live
    config, the verified chain report, the canon, the derivation, the
    frozen-object rows (digest + state per canon id) and the review file
    set."""

    config: Config
    report: ChainReport
    canon: tuple[CanonObject, ...]
    derivation: Derivation
    objects: tuple[FrozenObject, ...]
    review_files: tuple[str, ...]


def freeze_objects(
    canon: tuple[CanonObject, ...],
    states: dict[str, str],
    config: Config,
) -> tuple[FrozenObject, ...]:
    """The frozen-object rows of one derivation: the normative digest and
    the derived state per canon id (ids without a declared class carry no
    state and are skipped — they are reported by the derivation)."""
    classes = {cls.id: cls for cls in config.classes}
    rows: list[FrozenObject] = []
    for obj in canon:
        cls = classes.get(obj.class_id)
        if cls is None:
            continue
        normative, _informative = object_digests(cls, obj.fields)
        rows.append(
            FrozenObject(
                id=obj.id,
                class_id=obj.class_id,
                normative_digest=normative,
                state=states.get(obj.id, "not reviewed"),
            )
        )
    return tuple(rows)


def _is_link(info: os.stat_result) -> bool:
    """A symlink or any reparse point (junction, mount point), from an
    ``os.lstat`` result — the ``osopen.is_link`` rule restated here: the
    osopen-import census (``tests/test_arch_osopen_callers.py``) pins
    which reqharness modules may import osopen names, so the three-line
    predicate lives here rather than as an import."""
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def _resolve_inside(root: Path, rel: str) -> Path:
    """``<root>/<rel>`` resolved, refusing anything that escapes *root* —
    by name, before the caller reads or creates anything (M1).  A link
    resolving INSIDE the root is followed; a missing tail breaks the walk
    (nothing below a missing component can be a link); and the FINAL
    resolved path — not the lexical one — is asserted inside the resolved
    root, so a ``..`` traversal is refused even when no link is involved."""
    root_real = os.path.normcase(str(Path(root).resolve()))
    parts = Path(rel).parts
    probe = Path(root)
    for index, part in enumerate(parts):
        probe = probe / part
        try:
            info = os.lstat(probe)
        except (FileNotFoundError, NotADirectoryError):
            # the tail is missing: nothing below it can be a link, so the
            # walk is done — but the tail itself belongs to the result
            probe = probe.joinpath(*parts[index + 1 :])
            break
        except OSError:
            raise ValidationError(f"{rel}: refused (unreadable)") from None
        if _is_link(info):
            try:
                real = os.path.normcase(str(probe.resolve()))
            except (OSError, ValueError):
                raise ValidationError(f"{rel}: refused (unreadable)") from None
            if real != root_real and not real.startswith(root_real + os.sep):
                raise ValidationError(f"{rel}: refused (link)")
    try:
        resolved = probe.resolve()
    except (OSError, ValueError):
        raise ValidationError(f"{rel}: refused (unreadable)") from None
    resolved_real = os.path.normcase(str(resolved))
    if resolved_real != root_real and not resolved_real.startswith(
        root_real + os.sep
    ):
        raise ValidationError(f"{rel}: refused (outside)")
    return resolved


def _check_baseline_name(name: str) -> None:
    """`create`'s name rule, applied to the INCOMING ``name`` argument
    BEFORE any path is built: a ``/``, ``\\`` or ``..`` reaches the
    filesystem as a traversal component otherwise, so the refusal is by
    name alone — `load` and `_write` hold the same rule at their top."""
    check_str(name, where=BASELINE_WHERE, field="name")
    if name in (".", "..") or "/" in name or "\\" in name:
        raise ValidationError(f"{BASELINE_WHERE}/{name}.yml: refused (name)")


def confinement_sweep(root: Path) -> None:
    """The registry-read confinement (M1): every file the audit, baseline
    and release paths read under ``<root>/reqharness/`` and
    ``<root>/REQUIREMENTS.md`` must itself resolve inside *root*.  A file
    or link that resolves outside is refused BY NAME before its reader is
    reached — never followed; a missing or stat-failing entry is left to
    its reader's own named refusal.  Read-only: the sweep walks and stats,
    it writes nothing (R4)."""
    try:
        root_real_path = Path(root).resolve()
    except (OSError, ValueError):
        raise ValidationError(f"{REQHARNESS_DIR}: refused (unreadable)") from None
    root_real = os.path.normcase(str(root_real_path))
    registry = Path(root) / REQHARNESS_DIR
    candidates: list[tuple[str, Path]] = [(CANON_NAME, Path(root) / CANON_NAME)]
    if registry.is_dir():
        candidates.append((REQHARNESS_DIR, registry))
        for dirpath, dirnames, filenames in os.walk(registry, followlinks=False):
            for name in (*dirnames, *filenames):
                path = Path(dirpath) / name
                candidates.append((path.relative_to(root).as_posix(), path))
    elif registry.exists():
        candidates.append((REQHARNESS_DIR, registry))
    for rel, path in candidates:
        try:
            info = os.lstat(path)
        except OSError:
            continue  # missing/unreadable: the reader names it later
        if not _is_link(info):
            continue
        try:
            real = path.resolve()
        except (OSError, ValueError):
            real = None
        real_text = os.path.normcase(str(real)) if real is not None else ""
        if (
            real is None
            or (real_text != root_real and not real_text.startswith(root_real + os.sep))
        ):
            raise ValidationError(f"{rel}: refused (link)")


def snapshot(repo: str | Path, *, scan: ReviewScan | None = None) -> Snapshot:
    """The current derivation over *repo*: config, chain, canon, reviews
    and derived states folded into frozen-object rows.  A broken chain or
    an unverifiable derivation is a named refusal — a baseline is frozen
    only over a verifiable registry."""
    confinement_sweep(Path(repo))
    config = load_config(repo)
    report = safe_verify(repo)
    if not report.ok:
        raise ValidationError(
            f"{REQHARNESS_DIR}/roles.yml is not verifiable "
            f"({report.status}); refusing to freeze"
        )
    if scan is None:
        scan = load_reviews(repo)
    canon, canon_reported = load_canon(repo)
    derivation = derive_states(canon, scan, report, config)
    if not derivation.verifiable:
        raise ValidationError(
            f"registry is not verifiable ({derivation.reason}); "
            "refusing to freeze"
        )
    names, _reported = scan_event_dir(repo, REVIEW_DIR)
    if canon_reported:
        derivation = Derivation(  # carry the canon reader's named lines
            verifiable=derivation.verifiable,
            states=derivation.states,
            informative_marks=derivation.informative_marks,
            pre_reviewed=derivation.pre_reviewed,
            unentitled=derivation.unentitled,
            reported=tuple(derivation.reported) + tuple(canon_reported),
            warnings=derivation.warnings,
            reason=derivation.reason,
        )
    return Snapshot(
        config=config,
        report=report,
        canon=canon,
        derivation=derivation,
        objects=freeze_objects(canon, derivation.states, config),
        review_files=tuple(names),
    )


@dataclass(frozen=True)
class Baseline:
    """One frozen baseline, as written under
    ``reqharness/baselines/<name>.yml``."""

    name: str
    created: str
    commit: str
    dirty: bool
    roles_seq: int
    roles_hash: str
    objects: tuple[FrozenObject, ...]
    review_files: tuple[str, ...]

    @classmethod
    def create(cls, repo: str | Path, name: str, *, now: str | None = None) -> "Baseline":
        """Freeze the current derivation under ``baselines/<name>.yml``
        (LLR-RH.6.1): the commit SHA from a read-only ``git rev-parse
        HEAD``, the dirty flag from ``git status --porcelain
        --no-optional-locks``, the chain head and the review file set.
        An existing baseline of the same name is never overwritten."""
        _check_baseline_name(name)
        when = (
            check_time(now, where=BASELINE_WHERE, field="now")
            if now is not None
            else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        root = Path(repo)
        commit = identity.head_commit(root)
        if commit == identity.NO_REPO:
            raise ValidationError(
                f"{BASELINE_WHERE}/{name}.yml: no repo "
                "(git rev-parse HEAD failed); refusing to freeze"
            )
        porcelain = identity.status_porcelain(root)
        if porcelain == identity.NO_REPO:
            raise ValidationError(
                f"{BASELINE_WHERE}/{name}.yml: no repo "
                "(git status failed); refusing to freeze"
            )
        data = snapshot(root)
        head_seq, head_hash = data.report.head
        baseline = cls(
            name=name,
            created=when,
            commit=commit,
            dirty=porcelain != "",
            roles_seq=head_seq,
            roles_hash=head_hash,
            objects=data.objects,
            review_files=data.review_files,
        )
        baseline._write(root)
        return baseline

    def _document(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "created": self.created,
            "commit": self.commit,
            "dirty": self.dirty,
            "roles_seq": self.roles_seq,
            "roles_hash": self.roles_hash,
            "objects": [
                {
                    "id": row.id,
                    "class": row.class_id,
                    "normative_digest": row.normative_digest,
                    "state": row.state,
                }
                for row in self.objects
            ],
            "review_files": list(self.review_files),
        }

    def _write(self, root: Path) -> None:
        _check_baseline_name(self.name)
        where = f"{BASELINE_WHERE}/{self.name}.yml"
        resolved = _resolve_inside(root, where)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        try:
            with resolved.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(
                    yaml.safe_dump(
                        self._document(), sort_keys=False, allow_unicode=True
                    )
                )
        except FileExistsError:
            raise ValidationError(
                f"{where}: baseline already exists (refusing to overwrite)"
            ) from None

    @classmethod
    def load(cls, repo: str | Path, name: str) -> "Baseline":
        """Read one frozen baseline through the typed schema (R18: every
        field isinstance-checked; ``dirty`` is the one bool; ``objects``
        is a list of mappings, never iterated before its type is known;
        and the name rule runs on the INCOMING ``name`` before any path
        is built (R18: a traversal is refused by name, never touched)."""
        _check_baseline_name(name)
        where = f"{BASELINE_WHERE}/{name}.yml"
        resolved = _resolve_inside(Path(repo), where)
        try:
            raw = resolved.read_bytes()
        except FileNotFoundError:
            raise ValidationError(f"{where}: file not found") from None
        except OSError as exc:
            raise ValidationError(f"{where}: cannot read ({exc})") from exc
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"{where}: not valid UTF-8 ({exc})") from exc
        documents = load_documents(text, where=where)
        if len(documents) != 1:
            raise ValidationError(
                f"{where}: expected exactly 1 document, found {len(documents)}"
            )
        document = documents[0]
        if not isinstance(document, dict):
            raise ValidationError(
                f"{where}: expected a mapping, got {type(document).__name__}"
            )
        keys = set(document)
        expected = {
            "name", "created", "commit", "dirty",
            "roles_seq", "roles_hash", "objects", "review_files",
        }
        unknown = sorted(str(k) for k in keys - expected)
        if unknown:
            raise ValidationError(f"{where}: unknown key(s): {', '.join(unknown)}")
        missing = sorted(expected - keys)
        if missing:
            raise ValidationError(f"{where}: missing key(s): {', '.join(missing)}")
        objects_raw = document["objects"]
        if not isinstance(objects_raw, list):
            raise ValidationError(
                f"{where}: field 'objects' must be a list, got "
                f"{type(objects_raw).__name__} ({objects_raw!r})"
            )
        objects = []
        for index, raw_row in enumerate(objects_raw):
            row_where = f"{where}: objects[{index}]"
            if not isinstance(raw_row, dict):
                raise ValidationError(
                    f"{row_where}: expected a mapping, got "
                    f"{type(raw_row).__name__}"
                )
            row_keys = set(raw_row)
            row_expected = {"id", "class", "normative_digest", "state"}
            if row_keys != row_expected:
                raise ValidationError(
                    f"{row_where}: expected keys {sorted(row_expected)}, "
                    f"got {sorted(str(k) for k in row_keys)}"
                )
            objects.append(
                FrozenObject(
                    id=check_str(raw_row["id"], where=row_where, field="id"),
                    class_id=check_str(
                        raw_row["class"], where=row_where, field="class"
                    ),
                    normative_digest=check_str(
                        raw_row["normative_digest"],
                        where=row_where,
                        field="normative_digest",
                    ),
                    state=check_str(raw_row["state"], where=row_where, field="state"),
                )
            )
        review_files = document["review_files"]
        if not isinstance(review_files, list):
            raise ValidationError(
                f"{where}: field 'review_files' must be a list, got "
                f"{type(review_files).__name__}"
            )
        dirty = document["dirty"]
        if type(dirty) is not bool:
            raise ValidationError(
                f"{where}: field 'dirty' must be a bool, got "
                f"{type(dirty).__name__} ({dirty!r})"
            )
        name = check_str(document["name"], where=where, field="name")
        if name in (".", "..") or "/" in name or "\\" in name:
            raise ValidationError(f"{where}: refused (name)")
        return cls(
            name=name,
            created=check_time(document["created"], where=where, field="created"),
            commit=check_str(document["commit"], where=where, field="commit"),
            dirty=dirty,
            roles_seq=check_int(
                document["roles_seq"], where=where, field="roles_seq"
            ),
            roles_hash=check_str(
                document["roles_hash"], where=where, field="roles_hash"
            ),
            objects=tuple(objects),
            review_files=tuple(
                check_str(item, where=where, field=f"review_files[{i}]")
                for i, item in enumerate(review_files)
            ),
        )


@dataclass(frozen=True)
class DiffResult:
    """The five-class diff of a baseline against a baseline or the current
    state: the class of every union id, the review files the baseline
    listed that are gone now, and the baseline's recorded dirty flag."""

    classes: dict[str, str]
    deleted_reviews: tuple[str, ...]
    baseline_dirty: bool

    def by_class(self, class_name: str) -> tuple[str, ...]:
        """The ids of one class, sorted — the report's per-class lists."""
        return tuple(
            sorted(object_id for object_id, c in self.classes.items() if c == class_name)
        )


def diff(
    base: Baseline,
    current: tuple[FrozenObject, ...],
    *,
    current_review_files: tuple[str, ...] = (),
) -> DiffResult:
    """Classify every union id over the FIVE classes (LLR-RH.6.2): the
    normative digest decides `changed` (M-BL2 classifies by id presence
    only and reddens); an id in the baseline but absent now is `deleted`,
    never collapsed into `retired` (M-BL3); retired→active (reactivated)
    and the review-state progression are DEFERRED (B-125)."""
    base_map = {row.id: row for row in base.objects}
    current_map = {row.id: row for row in current}
    classes: dict[str, str] = {}
    for object_id in sorted(set(base_map) | set(current_map)):
        before = base_map.get(object_id)
        after = current_map.get(object_id)
        if before is None:
            classes[object_id] = CLASS_NEW
        elif after is None:
            classes[object_id] = CLASS_DELETED
        elif after.state == STATE_RETIRED and before.state != STATE_RETIRED:
            classes[object_id] = CLASS_RETIRED
        elif after.normative_digest != before.normative_digest:
            classes[object_id] = CLASS_CHANGED
        else:
            classes[object_id] = CLASS_UNCHANGED
    return DiffResult(
        classes=classes,
        deleted_reviews=tuple(sorted(set(base.review_files) - set(current_review_files))),
        baseline_dirty=base.dirty,
    )


__all__ = [
    "BASELINES_DIR",
    "BASELINE_WHERE",
    "Baseline",
    "CLASS_CHANGED",
    "CLASS_DELETED",
    "CLASS_NEW",
    "CLASS_RETIRED",
    "CLASS_UNCHANGED",
    "DiffResult",
    "FrozenObject",
    "Snapshot",
    "confinement_sweep",
    "diff",
    "freeze_objects",
    "snapshot",
]
